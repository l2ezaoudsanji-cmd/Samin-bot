import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8946756497:AAFxaT2tpx-66OwzDp4LJl1IHTCYqloSCl0")
CHANNEL_ID = "@saminpakhsh1"
ADMIN_ID = 1884167467
DATA_FILE = "products.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ORDER_NAME, ORDER_PHONE, ORDER_ADDRESS, ORDER_PRODUCT, ORDER_QUANTITY, ORDER_CONFIRM = range(6)
ADD_NAME, ADD_PRICE, ADD_PHOTO = range(6, 9)
EDIT_VALUE = 9

def load_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"name": "💧 آب معدنی ۳۵۰ سی‌سی بطری شفاف – بسته ۱۵ عددی", "price": "۲۷۶,۶۵۰ تومان", "available": True, "photo_id": None},
        {"name": "💧 آب معدنی ۲۰۰ سی‌سی گرد رنگی و دودی – بسته ۱۲ عددی", "price": "۱۴۸,۷۰۰ تومان", "available": True, "photo_id": None},
        {"name": "💧 آب معدنی ۲۰۰ سی‌سی مکعبی – بسته ۱۵ عددی", "price": "ناموجود", "available": False, "photo_id": None},
        {"name": "💧 آب معدنی ۵۰۰ سی‌سی رنگی و دودی – بسته ۱۲ عددی", "price": "۲۷۶,۶۵۰ تومان", "available": True, "photo_id": None},
        {"name": "💧 آب معدنی کتابی ۳۰۰ سی‌سی – باکس ۱۲ عددی", "price": "۲۲۶,۴۵۰ تومان", "available": True, "photo_id": None},
        {"name": "🍷 آب معدنی طرح شرابی رنگی – باکس ۱۲ عددی", "price": "۲۷۶,۶۰۰ تومان", "available": True, "photo_id": None},
        {"name": "🍷 آب معدنی طرح شرابی دودی و سفید – باکس ۱۲ عددی", "price": "۳۰۸,۶۰۰ تومان", "available": True, "photo_id": None},
        {"name": "🍫 شکلات طعم قهوه تلخ – کیلویی", "price": "۷۲۵,۸۰۰ تومان", "available": True, "photo_id": None},
        {"name": "🍫 شکلات تلخ – کیلویی", "price": "۸۲۵,۸۷۰ تومان", "available": True, "photo_id": None},
        {"name": "🍫 شکلات ۶۵ درصد – کیلویی", "price": "۷۰۵,۴۵۰ تومان", "available": True, "photo_id": None},
        {"name": "🍬 نبات زعفرانی کیفیت A+ – کیلویی", "price": "۱۹۵,۳۴۰ تومان", "available": True, "photo_id": None},
        {"name": "🍬 نبات زعفرانی کیفیت A – کیلویی", "price": "۱۹۲,۵۲۰ تومان", "available": True, "photo_id": None},
    ]

def save_products(products):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def get_dates():
    try:
        import jdatetime
        now = jdatetime.datetime.now()
        weekdays = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
        months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
        jalali = f"{weekdays[now.weekday()]} {now.day} {months[now.month-1]} {now.year}"
    except:
        jalali = datetime.now().strftime("%Y-%m-%d")
    miladi = datetime.now().strftime("%d %B %Y")
    return jalali, miladi

def build_product_text():
    products = load_products()
    lines = []
    for p in products:
        if p["available"]:
            lines.append(f"{p['name']}\n    💰 {p['price']}")
        else:
            lines.append(f"{p['name']}\n    🚫 ناموجود")
    return "\n\n".join(lines)

def build_channel_message():
    jalali, miladi = get_dates()
    return f"""🌅 صبح بخیر

📅 {jalali}
🗓 {miladi}

━━━━━━━━━━━━━━━━━━
🏢 ثمین پخش غرب
☕️ پخش کافه رستورانی
━━━━━━━━━━━━━━━━━━

📋 لیست محصولات امروز:

{build_product_text()}

━━━━━━━━━━━━━━━━━━
📲 سفارش: @Samin_pakhsh_bot

☎️ ۰۹۱۸۳۸۹۰۵۴۲
☎️ ۰۹۱۸۳۲۲۰۳۹۷
☎️ ۰۹۱۲۶۳۵۴۵۰۱"""

async def send_to_channel(bot):
    products = load_products()
    message = build_channel_message()
    await bot.send_message(chat_id=CHANNEL_ID, text=message)
    for p in products:
        if p["available"] and p.get("photo_id"):
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=p["photo_id"],
                caption=f"{p['name']}\n💰 {p['price']}"
            )

async def ask_admin_morning(bot):
    keyboard = [
        [InlineKeyboardButton("✅ همون قیمت‌ها، بفرست!", callback_data="send_same")],
        [InlineKeyboardButton("✏️ میخوام قیمت عوض کنم", callback_data="edit_prices")],
    ]
    await bot.send_message(
        chat_id=ADMIN_ID,
        text="🌅 صبح بخیر!\n\nوقت ارسال لیست قیمت‌هاست.\nقیمت‌ها همون دیروزه یا عوض شده؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
        [InlineKeyboardButton("📚 کاتالوگ محصولات", callback_data="catalog")],
        [InlineKeyboardButton("📋 لیست قیمت امروز", callback_data="products")],
        [InlineKeyboardButton("📞 تماس با ما", callback_data="contact")],
    ]
    await update.message.reply_text(
        "🌿 به ربات ثمین پخش غرب خوش آمدید!\n\n☕️ پخش کافه رستورانی در کرمانشاه\n\nاز منو انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    keyboard = [
        [InlineKeyboardButton("📋 مدیریت محصولات", callback_data="manage_products")],
        [InlineKeyboardButton("➕ افزودن محصول جدید", callback_data="add_product")],
        [InlineKeyboardButton("📤 ارسال لیست به کانال", callback_data="send_same")],
    ]
    await update.message.reply_text("👨‍💼 پنل مدیریت ثمین پخش:", reply_markup=InlineKeyboardMarkup(keyboard))

async def btn_send_same(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await send_to_channel(context.bot)
    await query.edit_message_text("✅ لیست با موفقیت به کانال فرستاده شد!")

async def btn_edit_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    products = load_products()
    keyboard = []
    for i, p in enumerate(products):
        status = "✅" if p["available"] else "🚫"
        keyboard.append([InlineKeyboardButton(f"{status} {i+1}. {p['name'][:40]}", callback_data=f"ep_{i}")])
    keyboard.append([InlineKeyboardButton("📤 تموم شد، بفرست!", callback_data="send_same")])
    await query.edit_message_text("کدوم محصول رو ویرایش کنی؟", reply_markup=InlineKeyboardMarkup(keyboard))

async def btn_edit_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[1])
    products = load_products()
    p = products[idx]
    context.user_data["editing_idx"] = idx
    keyboard = [
        [InlineKeyboardButton("💰 تغییر قیمت", callback_data="ef_price")],
        [InlineKeyboardButton("🚫 ناموجود کن", callback_data="ef_unavailable")],
        [InlineKeyboardButton("✅ موجود کن", callback_data="ef_available")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="edit_prices")],
    ]
    await query.edit_message_text(
        f"محصول: {p['name']}\nقیمت: {p['price']}\nوضعیت: {'✅ موجود' if p['available'] else '🚫 ناموجود'}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def btn_edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    field = query.data.split("_")[1]
    idx = context.user_data.get("editing_idx")
    products = load_products()
    if field == "unavailable":
        products[idx]["available"] = False
        save_products(products)
        await query.edit_message_text(f"🚫 ناموجود شد!\n\n/admin برای ادامه")
        return ConversationHandler.END
    elif field == "available":
        products[idx]["available"] = True
        save_products(products)
        await query.edit_message_text(f"✅ موجود شد!\n\n/admin برای ادامه")
        return ConversationHandler.END
    elif field == "price":
        await query.edit_message_text("قیمت جدید رو بنویس:\n(مثال: ۲۵۰,۰۰۰ تومان)")
        return EDIT_VALUE

async def save_edit_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("editing_idx")
    products = load_products()
    products[idx]["price"] = update.message.text
    products[idx]["available"] = True
    save_products(products)
    await update.message.reply_text(f"✅ قیمت آپدیت شد!\n\n/admin برای ادامه")
    return ConversationHandler.END

async def btn_manage_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    products = load_products()
    keyboard = []
    for i, p in enumerate(products):
        status = "✅" if p["available"] else "🚫"
        keyboard.append([InlineKeyboardButton(f"{status} {i+1}. {p['name'][:40]}", callback_data=f"ep_{i}")])
    keyboard.append([InlineKeyboardButton("➕ محصول جدید", callback_data="add_product")])
    await query.edit_message_text("📋 محصولات:", reply_markup=InlineKeyboardMarkup(keyboard))

async def btn_show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await query.edit_message_text(f"📋 لیست قیمت امروز:\n\n{build_product_text()}", reply_markup=InlineKeyboardMarkup(keyboard))

async def btn_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📚 در حال بارگذاری کاتالوگ...")
    products = load_products()
    for p in products:
        caption = f"{p['name']}\n💰 {'ناموجود 🚫' if not p['available'] else p['price']}"
        if p.get("photo_id"):
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=p["photo_id"], caption=caption)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=caption)

async def btn_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📞 تماس با ثمین پخش غرب\n\n☎️ ۰۹۱۸۳۸۹۰۵۴۲\n☎️ ۰۹۱۸۳۲۲۰۳۹۷\n☎️ ۰۹۱۲۶۳۵۴۵۰۱\n\n📍 کرمانشاه\n\n/start"
    )

async def btn_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
        [InlineKeyboardButton("📚 کاتالوگ محصولات", callback_data="catalog")],
        [InlineKeyboardButton("📋 لیست قیمت امروز", callback_data="products")],
        [InlineKeyboardButton("📞 تماس با ما", callback_data="contact")],
    ]
    await query.edit_message_text("🌿 ثمین پخش غرب\n\nاز منو انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("➕ اسم محصول جدید رو بنویس:")
    return ADD_NAME

async def get_add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_name"] = update.message.text
    await update.message.reply_text("💰 قیمت محصول:")
    return ADD_PRICE

async def get_add_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_price"] = update.message.text
    await update.message.reply_text("📸 عکس محصول رو بفرست یا بنویس 'رد کن':")
    return ADD_PHOTO

async def get_add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = load_products()
    photo_id = update.message.photo[-1].file_id if update.message.photo else None
    products.append({"name": context.user_data["new_name"], "price": context.user_data["new_price"], "available": True, "photo_id": photo_id})
    save_products(products)
    await update.message.reply_text(f"✅ محصول اضافه شد!\n\n/admin")
    return ConversationHandler.END

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = load_products()
    products.append({"name": context.user_data["new_name"], "price": context.user_data["new_price"], "available": True, "photo_id": None})
    save_products(products)
    await update.message.reply_text(f"✅ محصول اضافه شد!\n\n/admin")
    return ConversationHandler.END

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🛒 نام و نام خانوادگی:")
    return ORDER_NAME

async def get_order_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📞 شماره تلفن:")
    return ORDER_PHONE

async def get_order_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("📍 آدرس تحویل:")
    return ORDER_ADDRESS

async def get_order_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    products = load_products()
    available = [p for p in products if p["available"]]
    context.user_data['available'] = available
    lines = "\n".join([f"{i+1}. {p['name']} — {p['price']}" for i, p in enumerate(available)])
    await update.message.reply_text(f"📦 شماره محصول:\n\n{lines}")
    return ORDER_PRODUCT

async def get_order_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        available = context.user_data['available']
        idx = int(update.message.text) - 1
        if 0 <= idx < len(available):
            context.user_data['product'] = available[idx]['name']
            context.user_data['price'] = available[idx]['price']
            await update.message.reply_text("🔢 تعداد:")
            return ORDER_QUANTITY
    except:
        pass
    await update.message.reply_text("❌ عدد نامعتبر:")
    return ORDER_PRODUCT

async def get_order_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['quantity'] = update.message.text
    d = context.user_data
    keyboard = [[InlineKeyboardButton("✅ تایید", callback_data="confirm")], [InlineKeyboardButton("❌ انصراف", callback_data="cancel")]]
    await update.message.reply_text(
        f"✅ خلاصه سفارش:\n\n👤 {d['name']}\n📞 {d['phone']}\n📍 {d['address']}\n📦 {d['product']}\n💰 {d['price']}\n🔢 {d['quantity']}\n\nتایید؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ORDER_CONFIRM

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    d = context.user_data
    user = update.effective_user
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 سفارش جدید!\n\n👤 {d['name']}\n📞 {d['phone']}\n📍 {d['address']}\n📦 {d['product']}\n💰 {d['price']}\n🔢 {d['quantity']}\n🆔 @{user.username or 'ندارد'}\n⏰ {datetime.now().strftime('%H:%M')}"
    )
    await query.edit_message_text("✅ سفارش ثبت شد! به زودی تماس می‌گیریم 🙏\n\n/start")
    return ConversationHandler.END

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ لغو شد.\n\n/start")
    return ConversationHandler.END

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    idx = context.user_data.get("photo_product_idx")
    if idx is None:
        return
    products = load_products()
    products[idx]["photo_id"] = update.message.photo[-1].file_id
    save_products(products)
    await update.message.reply_text(f"✅ عکس ذخیره شد!\n\n/admin")
    context.user_data["photo_product_idx"] = None

async def send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await send_to_channel(context.bot)
    await update.message.reply_text("✅ ارسال شد!")

async def morning_job(context: ContextTypes.DEFAULT_TYPE):
    await ask_admin_morning(context.bot)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    edit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(btn_edit_product, pattern="^ep_")],
        states={EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edit_value)]},
        fallbacks=[CommandHandler("start", start)],
    )

    add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add, pattern="^add_product$")],
        states={
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_add_name)],
            ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_add_price)],
            ADD_PHOTO: [MessageHandler(filters.PHOTO, get_add_photo), MessageHandler(filters.TEXT & ~filters.COMMAND, skip_photo)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order, pattern="^order$")],
        states={
            ORDER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_name)],
            ORDER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_phone)],
            ORDER_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_address)],
            ORDER_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_product)],
            ORDER_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_quantity)],
            ORDER_CONFIRM: [CallbackQueryHandler(confirm_order, pattern="^confirm$"), CallbackQueryHandler(cancel_order, pattern="^cancel$")],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("send", send_now))
    app.add_handler(edit_conv)
    app.add_handler(add_conv)
    app.add_handler(order_conv)
    app.add_handler(CallbackQueryHandler(btn_send_same, pattern="^send_same$"))
    app.add_handler(CallbackQueryHandler(btn_edit_prices, pattern="^edit_prices$"))
    app.add_handler(CallbackQueryHandler(btn_edit_field, pattern="^ef_"))
    app.add_handler(CallbackQueryHandler(btn_manage_products, pattern="^manage_products$"))
    app.add_handler(CallbackQueryHandler(btn_show_products, pattern="^products$"))
    app.add_handler(CallbackQueryHandler(btn_catalog, pattern="^catalog$"))
    app.add_handler(CallbackQueryHandler(btn_contact, pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(btn_back, pattern="^back$"))
    app.add_handler(MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), receive_photo))

    # هر روز ساعت ۷:۳۰ صبح
    app.job_queue.run_daily(morning_job, time=datetime.strptime("07:30", "%H:%M").time())

    print("✅ ربات فعال شد!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
