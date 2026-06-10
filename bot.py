import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
import httpx

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8946756497:AAFxaT2tpx-66OwzDp4LJl1IHTCYqloSCl0")
CHANNEL_ID = "@saminpakhsh1"
ADMIN_ID = 1884167467
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://urqalfixzrgauqdjcgqj.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_UHSeqHYXLQFEBQsU0HHWlA_aZdfRhCs")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ORDER_NAME, ORDER_PHONE, ORDER_ADDRESS, ORDER_PRODUCT, ORDER_QUANTITY, ORDER_CONFIRM = range(6)
ADD_NAME, ADD_PRICE, ADD_PHOTO = range(6, 9)
EDIT_PRICE_VALUE = 9
WAIT_PHOTO = 10

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

async def db_get_products():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/products?order=id", headers=HEADERS)
        return r.json()

async def db_update_product(pid, data):
    async with httpx.AsyncClient() as client:
        await client.patch(f"{SUPABASE_URL}/rest/v1/products?id=eq.{pid}", headers=HEADERS, json=data)

async def db_insert_product(data):
    async with httpx.AsyncClient() as client:
        await client.post(f"{SUPABASE_URL}/rest/v1/products", headers=HEADERS, json=data)

async def db_delete_product(pid):
    async with httpx.AsyncClient() as client:
        await client.delete(f"{SUPABASE_URL}/rest/v1/products?id=eq.{pid}", headers=HEADERS)

def get_jalali():
    try:
        import jdatetime
        now = jdatetime.datetime.now()
        weekdays = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
        months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
        return f"{weekdays[now.weekday()]} {now.day} {months[now.month-1]} {now.year}"
    except:
        return datetime.now().strftime("%Y-%m-%d")

async def send_morning(bot):
    jalali = get_jalali()
    text = f"""🌅 صبح بخیر

📅 {jalali}

🏢 ثمین پخش غرب
☕️ پخش کافه رستورانی

☎️ ۰۹۱۸۳۸۹۰۵۴۲
☎️ ۰۹۱۸۳۲۲۰۳۹۷
☎️ ۰۹۱۲۶۳۵۴۵۰۱

📲 Saminpakhsh1"""
    await bot.send_message(chat_id=CHANNEL_ID, text=text)

async def send_pricelist(bot):
    products = await db_get_products()
    for p in products:
        if not p["available"]:
            continue
        caption = f"{p['name']}\n💰 {p['price']}"
        try:
            if p.get("photo_id"):
                await bot.send_photo(chat_id=CHANNEL_ID, photo=p["photo_id"], caption=caption)
            else:
                await bot.send_message(chat_id=CHANNEL_ID, text=caption)
        except Exception as e:
            logger.error(f"خطا: {e}")
            await bot.send_message(chat_id=CHANNEL_ID, text=caption)

    await bot.send_message(chat_id=CHANNEL_ID, text="""جهت سفارش میتوانید با شماره های زیر تماس بگیرید:

☎️ ۰۹۱۸۳۸۹۰۵۴۲
☎️ ۰۹۱۸۳۲۲۰۳۹۷
☎️ ۰۹۱۲۶۳۵۴۵۰۱

یا از طریق دایرکت چنل اقدام نمایید

📲 Saminpakhsh1""")

async def job_morning(context: ContextTypes.DEFAULT_TYPE):
    await send_morning(context.bot)

async def job_pricelist(context: ContextTypes.DEFAULT_TYPE):
    await send_pricelist(context.bot)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
        [InlineKeyboardButton("📋 لیست قیمت", callback_data="products")],
        [InlineKeyboardButton("📞 تماس با ما", callback_data="contact")],
    ]
    await update.message.reply_text(
        "🌿 به ربات ثمین پخش غرب خوش آمدید!\n\n☕️ پخش کافه رستورانی در کرمانشاه\n\nاز منو انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def btn_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⏳ در حال بارگذاری...")
    products = await db_get_products()
    chat_id = update.effective_chat.id
    for p in products:
        caption = f"{p['name']}\n💰 {'ناموجود 🚫' if not p['available'] else p['price']}"
        try:
            if p.get("photo_id"):
                await context.bot.send_photo(chat_id=chat_id, photo=p["photo_id"], caption=caption)
            else:
                await context.bot.send_message(chat_id=chat_id, text=caption)
        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=caption)
    keyboard = [[InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")]]
    await context.bot.send_message(chat_id=chat_id, text="برای ثبت سفارش:", reply_markup=InlineKeyboardMarkup(keyboard))

async def btn_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📞 تماس با ثمین پخش غرب\n\n☎️ ۰۹۱۸۳۸۹۰۵۴۲\n☎️ ۰۹۱۸۳۲۲۰۳۹۷\n☎️ ۰۹۱۲۶۳۵۴۵۰۱\n\n📍 کرمانشاه\n\n/start")

async def btn_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
        [InlineKeyboardButton("📋 لیست قیمت", callback_data="products")],
        [InlineKeyboardButton("📞 تماس با ما", callback_data="contact")],
    ]
    await query.edit_message_text("🌿 ثمین پخش غرب\n\nاز منو انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ دسترسی ندارید!")
        return
    keyboard = [
        [InlineKeyboardButton("📋 مدیریت محصولات", callback_data="adm_list")],
        [InlineKeyboardButton("➕ افزودن محصول", callback_data="adm_add")],
        [InlineKeyboardButton("📤 ارسال فوری به کانال", callback_data="adm_send")],
    ]
    await update.message.reply_text("👨‍💼 پنل مدیریت ثمین پخش:", reply_markup=InlineKeyboardMarkup(keyboard))

async def adm_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    products = await db_get_products()
    keyboard = []
    for p in products:
        status = "✅" if p["available"] else "🚫"
        photo = "📸" if p.get("photo_id") else "📷"
        keyboard.append([InlineKeyboardButton(f"{status}{photo} {p['name'][:32]}", callback_data=f"adm_p_{p['id']}")])
    keyboard.append([InlineKeyboardButton("➕ محصول جدید", callback_data="adm_add")])
    keyboard.append([InlineKeyboardButton("📤 ارسال به کانال", callback_data="adm_send")])
    await query.edit_message_text("📋 محصولات:\n✅=موجود 🚫=ناموجود 📸=دارد عکس 📷=بدون عکس", reply_markup=InlineKeyboardMarkup(keyboard))

async def adm_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    pid = int(query.data.split("_")[2])
    context.user_data["edit_pid"] = pid
    products = await db_get_products()
    p = next((x for x in products if x["id"] == pid), None)
    if not p:
        await query.edit_message_text("❌ محصول پیدا نشد!\n\n/admin")
        return
    keyboard = [
        [InlineKeyboardButton("💰 تغییر قیمت", callback_data=f"adm_price_{pid}")],
        [InlineKeyboardButton("📸 تغییر عکس", callback_data=f"adm_photo_{pid}")],
        [InlineKeyboardButton("🚫 ناموجود کن", callback_data=f"adm_unavail_{pid}")],
        [InlineKeyboardButton("✅ موجود کن", callback_data=f"adm_avail_{pid}")],
        [InlineKeyboardButton("🗑 حذف", callback_data=f"adm_del_{pid}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_list")],
    ]
    photo_status = "✅ دارد عکس" if p.get("photo_id") else "❌ ندارد عکس"
    await query.edit_message_text(
        f"📦 {p['name']}\n💰 {p['price']}\nوضعیت: {'✅ موجود' if p['available'] else '🚫 ناموجود'}\nعکس: {photo_status}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def adm_set_unavail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    pid = int(query.data.split("_")[2])
    await db_update_product(pid, {"available": False})
    await query.edit_message_text(f"🚫 ناموجود شد!\n\n/admin")

async def adm_set_avail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    pid = int(query.data.split("_")[2])
    await db_update_product(pid, {"available": True})
    await query.edit_message_text(f"✅ موجود شد!\n\n/admin")

async def adm_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    pid = int(query.data.split("_")[2])
    await db_delete_product(pid)
    await query.edit_message_text(f"🗑 حذف شد!\n\n/admin")

async def adm_send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    await query.edit_message_text("⏳ در حال ارسال به کانال...")
    try:
        await send_morning(context.bot)
        await send_pricelist(context.bot)
        await context.bot.send_message(chat_id=ADMIN_ID, text="✅ لیست کامل به کانال ارسال شد!")
    except Exception as e:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ خطا: {e}")

async def send_now_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("⏳ در حال ارسال...")
    try:
        await send_morning(context.bot)
        await send_pricelist(context.bot)
        await update.message.reply_text("✅ ارسال شد!")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def adm_start_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    pid = int(query.data.split("_")[2])
    context.user_data["edit_pid"] = pid
    await query.edit_message_text("💰 قیمت جدید را بنویسید:\n(مثال: ۲۵۰,۰۰۰ تومان)")
    return EDIT_PRICE_VALUE

async def adm_save_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    pid = context.user_data.get("edit_pid")
    if not pid:
        return ConversationHandler.END
    await db_update_product(pid, {"price": update.message.text, "available": True})
    await update.message.reply_text(f"✅ قیمت ذخیره شد!\n💰 {update.message.text}\n\n/admin")
    return ConversationHandler.END

async def adm_start_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    pid = int(query.data.split("_")[2])
    context.user_data["photo_pid"] = pid
    await query.edit_message_text("📸 عکس جدید را بفرستید:")
    return WAIT_PHOTO

async def adm_save_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    if not update.message.photo:
        await update.message.reply_text("❌ لطفاً عکس بفرستید!")
        return WAIT_PHOTO
    pid = context.user_data.get("photo_pid")
    if not pid:
        return ConversationHandler.END
    photo_id = update.message.photo[-1].file_id
    await db_update_product(pid, {"photo_id": photo_id})
    await update.message.reply_text(f"✅ عکس ذخیره شد!\n\n/admin")
    return ConversationHandler.END

async def adm_start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    await query.edit_message_text("➕ اسم محصول جدید را بنویسید:")
    return ADD_NAME

async def adm_add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_name"] = update.message.text
    await update.message.reply_text("💰 قیمت را بنویسید:")
    return ADD_PRICE

async def adm_add_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_price"] = update.message.text
    await update.message.reply_text("📸 عکس محصول را بفرستید:\n(یا بنویسید 'رد کن')")
    return ADD_PHOTO

async def adm_add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = None
    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
    elif update.message.text and update.message.text.strip() in ["رد کن", "رد", "skip"]:
        photo_id = None
    else:
        await update.message.reply_text("عکس بفرستید یا 'رد کن' بنویسید:")
        return ADD_PHOTO
    await db_insert_product({"name": context.user_data["new_name"], "price": context.user_data["new_price"], "available": True, "photo_id": photo_id})
    await update.message.reply_text(f"✅ محصول اضافه شد!\n{context.user_data['new_name']}\n💰 {context.user_data['new_price']}\n\n/admin")
    return ConversationHandler.END

async def btn_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🛒 نام و نام خانوادگی:")
    return ORDER_NAME

async def order_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['o_name'] = update.message.text
    await update.message.reply_text("📞 شماره تلفن:")
    return ORDER_PHONE

async def order_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['o_phone'] = update.message.text
    await update.message.reply_text("📍 آدرس تحویل:")
    return ORDER_ADDRESS

async def order_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['o_address'] = update.message.text
    products = await db_get_products()
    available = [p for p in products if p["available"]]
    context.user_data['o_available'] = available
    lines = "\n".join([f"{i+1}. {p['name']} — {p['price']}" for i, p in enumerate(available)])
    await update.message.reply_text(f"📦 شماره محصول:\n\n{lines}")
    return ORDER_PRODUCT

async def order_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        available = context.user_data['o_available']
        idx = int(update.message.text.strip()) - 1
        if 0 <= idx < len(available):
            context.user_data['o_product'] = available[idx]['name']
            context.user_data['o_price'] = available[idx]['price']
            await update.message.reply_text("🔢 تعداد:")
            return ORDER_QUANTITY
    except:
        pass
    await update.message.reply_text("❌ عدد نامعتبر:")
    return ORDER_PRODUCT

async def order_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['o_qty'] = update.message.text
    d = context.user_data
    keyboard = [
        [InlineKeyboardButton("✅ تایید", callback_data="o_confirm")],
        [InlineKeyboardButton("❌ انصراف", callback_data="o_cancel")]
    ]
    await update.message.reply_text(
        f"✅ خلاصه سفارش:\n\n👤 {d['o_name']}\n📞 {d['o_phone']}\n📍 {d['o_address']}\n📦 {d['o_product']}\n💰 {d['o_price']}\n🔢 {d['o_qty']}\n\nتایید؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ORDER_CONFIRM

async def order_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    d = context.user_data
    user = update.effective_user
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 سفارش جدید!\n\n👤 {d['o_name']}\n📞 {d['o_phone']}\n📍 {d['o_address']}\n📦 {d['o_product']}\n💰 {d['o_price']}\n🔢 {d['o_qty']}\n🆔 @{user.username or 'ندارد'}\n⏰ {datetime.now().strftime('%H:%M')}"
    )
    await query.edit_message_text("✅ سفارش ثبت شد!\nبه زودی تماس می‌گیریم 🙏\n\n/start")
    return ConversationHandler.END

async def order_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ لغو شد.\n\n/start")
    return ConversationHandler.END

async def cancel_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لغو شد.\n\n/start")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    price_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(adm_start_price, pattern=r"^adm_price_\d+$")],
        states={EDIT_PRICE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID), adm_save_price)]},
        fallbacks=[CommandHandler("cancel", cancel_conv)],
        per_message=False,
    )

    photo_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(adm_start_photo, pattern=r"^adm_photo_\d+$")],
        states={WAIT_PHOTO: [MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), adm_save_photo)]},
        fallbacks=[CommandHandler("cancel", cancel_conv)],
        per_message=False,
    )

    add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(adm_start_add, pattern="^adm_add$")],
        states={
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID), adm_add_name)],
            ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID), adm_add_price)],
            ADD_PHOTO: [
                MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), adm_add_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID), adm_add_photo),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_conv)],
        per_message=False,
    )

    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(btn_order, pattern="^order$")],
        states={
            ORDER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_name)],
            ORDER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_phone)],
            ORDER_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_address)],
            ORDER_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_product)],
            ORDER_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_quantity)],
            ORDER_CONFIRM: [
                CallbackQueryHandler(order_confirm, pattern="^o_confirm$"),
                CallbackQueryHandler(order_cancel, pattern="^o_cancel$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_conv), CommandHandler("start", start)],
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("send", send_now_cmd))
    app.add_handler(price_conv)
    app.add_handler(photo_conv)
    app.add_handler(add_conv)
    app.add_handler(order_conv)
    app.add_handler(CallbackQueryHandler(adm_list, pattern="^adm_list$"))
    app.add_handler(CallbackQueryHandler(adm_product, pattern=r"^adm_p_\d+$"))
    app.add_handler(CallbackQueryHandler(adm_set_unavail, pattern=r"^adm_unavail_\d+$"))
    app.add_handler(CallbackQueryHandler(adm_set_avail, pattern=r"^adm_avail_\d+$"))
    app.add_handler(CallbackQueryHandler(adm_del, pattern=r"^adm_del_\d+$"))
    app.add_handler(CallbackQueryHandler(adm_send_now, pattern="^adm_send$"))
    app.add_handler(CallbackQueryHandler(btn_products, pattern="^products$"))
    app.add_handler(CallbackQueryHandler(btn_contact, pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(btn_back, pattern="^back$"))

    app.job_queue.run_daily(job_morning, time=datetime.strptime("08:00", "%H:%M").time())
    app.job_queue.run_daily(job_pricelist, time=datetime.strptime("10:00", "%H:%M").time())

    print("✅ ربات ثمین پخش فعال شد!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
