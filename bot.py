import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ==================== تنظیمات ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8946756497:AAFxaT2tpx-66OwzDp4LJl1IHTCYqloSCl0")
CHANNEL_ID = "@saminpakhsh1"
ADMIN_ID = 1884167467
DATA_FILE = "products.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== مراحل ====================
(ORDER_NAME, ORDER_PHONE, ORDER_ADDRESS, ORDER_PRODUCT, ORDER_QUANTITY, ORDER_CONFIRM) = range(6)
(ADD_NAME, ADD_PRICE, ADD_PHOTO) = range(6, 9)
EDIT_PRICE_VALUE = 9
WAIT_PHOTO = 10

# ==================== محصولات ====================
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

# ==================== تاریخ شمسی ====================
def get_jalali():
    try:
        import jdatetime
        now = jdatetime.datetime.now()
        weekdays = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
        months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
        return f"{weekdays[now.weekday()]} {now.day} {months[now.month-1]} {now.year}"
    except:
        return datetime.now().strftime("%Y-%m-%d")

# ==================== ارسال صبحگاهی ====================
async def job_morning_greeting(context: ContextTypes.DEFAULT_TYPE):
    """ساعت ۸ صبح - پیام خوش‌آمد"""
    jalali = get_jalali()
    text = f"""🌅 صبح بخیر

📅 {jalali}

🏢 ثمین پخش غرب
☕️ پخش کافه رستورانی

☎️ ۰۹۱۸۳۸۹۰۵۴۲
☎️ ۰۹۱۸۳۲۲۰۳۹۷
☎️ ۰۹۱۲۶۳۵۴۵۰۱

📲 Saminpakhsh1"""
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)

async def job_send_pricelist(context: ContextTypes.DEFAULT_TYPE):
    """ساعت ۱۰ صبح - لیست قیمت"""
    products = load_products()
    for p in products:
        if not p["available"]:
            continue
        caption = f"{p['name']}\n💰 {p['price']}"
        if p.get("photo_id"):
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=p["photo_id"],
                caption=caption
            )
        else:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=caption)

    footer = """جهت سفارش میتوانید با شماره های زیر تماس بگیرید:

☎️ ۰۹۱۸۳۸۹۰۵۴۲
☎️ ۰۹۱۸۳۲۲۰۳۹۷
☎️ ۰۹۱۲۶۳۵۴۵۰۱

یا از طریق دایرکت چنل اقدام نمایید

📲 Saminpakhsh1"""
    await context.bot.send_message(chat_id=CHANNEL_ID, text=footer)

# ==================== منوی اصلی ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
        [InlineKeyboardButton("📋 لیست قیمت", callback_data="products")],
        [InlineKeyboardButton("📞 تماس با ما", callback_data="contact")],
    ]
    await update.message.reply_text(
        "🌿 به ربات ثمین پخش غرب خوش آمدید!\n\n☕️ پخش کافه رستورانی در کرمانشاه",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def btn_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⏳ در حال بارگذاری لیست قیمت...")
    products = load_products()
    chat_id = update.effective_chat.id
    for p in products:
        caption = f"{p['name']}\n💰 {'ناموجود 🚫' if not p['available'] else p['price']}"
        if p.get("photo_id"):
            await context.bot.send_photo(chat_id=chat_id, photo=p["photo_id"], caption=caption)
        else:
            await context.bot.send_message(chat_id=chat_id, text=caption)
    keyboard = [[InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")]]
    await context.bot.send_message(chat_id=chat_id, text="برای ثبت سفارش:", reply_markup=InlineKeyboardMarkup(keyboard))

async def btn_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📞 تماس با ثمین پخش غرب\n\n☎️ ۰۹۱۸۳۸۹۰۵۴۲\n☎️ ۰۹۱۸۳۲۲۰۳۹۷\n☎️ ۰۹۱۲۶۳۵۴۵۰۱\n\n📍 کرمانشاه\n\nبرای بازگشت /start بزنید"
    )

async def btn_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
        [InlineKeyboardButton("📋 لیست قیمت", callback_data="products")],
        [InlineKeyboardButton("📞 تماس با ما", callback_data="contact")],
    ]
    await query.edit_message_text(
        "🌿 ثمین پخش غرب\n\nاز منو انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== پنل ادمین ====================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ شما دسترسی ندارید!")
        return
    keyboard = [
        [InlineKeyboardButton("📋 مدیریت محصولات", callback_data="adm_list")],
        [InlineKeyboardButton("➕ افزودن محصول", callback_data="adm_add")],
        [InlineKeyboardButton("📤 ارسال فوری به کانال", callback_data="adm_send")],
    ]
    await update.message.reply_text(
        "👨‍💼 پنل مدیریت ثمین پخش\n\nفقط شما دسترسی دارید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def adm_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ دسترسی ندارید!")
        return
    await query.answer()
    products = load_products()
    keyboard = []
    for i, p in enumerate(products):
        status = "✅" if p["available"] else "🚫"
        photo = "📸" if p.get("photo_id") else "📷"
        keyboard.append([InlineKeyboardButton(
            f"{status}{photo} {i+1}. {p['name'][:35]}",
            callback_data=f"adm_p_{i}"
        )])
    keyboard.append([InlineKeyboardButton("➕ محصول جدید", callback_data="adm_add")])
    keyboard.append([InlineKeyboardButton("📤 ارسال به کانال", callback_data="adm_send")])
    await query.edit_message_text(
        "📋 لیست محصولات:\n✅=موجود 🚫=ناموجود 📸=دارد عکس 📷=بدون عکس",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def adm_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ دسترسی ندارید!")
        return
    await query.answer()
    idx = int(query.data.split("_")[2])
    products = load_products()
    p = products[idx]
    context.user_data["edit_idx"] = idx
    keyboard = [
        [InlineKeyboardButton("💰 تغییر قیمت", callback_data=f"adm_price_{idx}")],
        [InlineKeyboardButton("📸 تغییر عکس", callback_data=f"adm_photo_{idx}")],
        [InlineKeyboardButton("🚫 ناموجود کن", callback_data=f"adm_unavail_{idx}")],
        [InlineKeyboardButton("✅ موجود کن", callback_data=f"adm_avail_{idx}")],
        [InlineKeyboardButton("🗑 حذف محصول", callback_data=f"adm_del_{idx}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_list")],
    ]
    photo_status = "✅ دارد عکس" if p.get("photo_id") else "❌ ندارد عکس"
    await query.edit_message_text(
        f"محصول: {p['name']}\nقیمت: {p['price']}\nوضعیت: {'✅ موجود' if p['available'] else '🚫 ناموجود'}\nعکس: {photo_status}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def adm_set_unavail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    idx = int(query.data.split("_")[2])
    products = load_products()
    products[idx]["available"] = False
    save_products(products)
    await query.edit_message_text(f"🚫 ناموجود شد:\n{products[idx]['name']}\n\n/admin برای ادامه")

async def adm_set_avail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    idx = int(query.data.split("_")[2])
    products = load_products()
    products[idx]["available"] = True
    save_products(products)
    await query.edit_message_text(f"✅ موجود شد:\n{products[idx]['name']}\n\n/admin برای ادامه")

async def adm_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    idx = int(query.data.split("_")[2])
    products = load_products()
    name = products[idx]["name"]
    products.pop(idx)
    save_products(products)
    await query.edit_message_text(f"🗑 حذف شد:\n{name}\n\n/admin برای ادامه")

async def adm_send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    await query.edit_message_text("⏳ در حال ارسال...")
    await job_morning_greeting(context)
    await job_send_pricelist(context)
    await context.bot.send_message(chat_id=ADMIN_ID, text="✅ لیست کامل به کانال ارسال شد!")

async def send_now_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("⏳ در حال ارسال...")
    await job_morning_greeting(context)
    await job_send_pricelist(context)
    await update.message.reply_text("✅ ارسال شد!")

# ==================== تغییر قیمت ====================
async def adm_start_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    idx = int(query.data.split("_")[2])
    context.user_data["edit_idx"] = idx
    products = load_products()
    await query.edit_message_text(
        f"محصول: {products[idx]['name']}\nقیمت فعلی: {products[idx]['price']}\n\nقیمت جدید را بنویسید:\n(مثال: ۲۵۰,۰۰۰ تومان)"
    )
    return EDIT_PRICE_VALUE

async def adm_save_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    idx = context.user_data.get("edit_idx")
    if idx is None:
        return ConversationHandler.END
    products = load_products()
    old_price = products[idx]["price"]
    products[idx]["price"] = update.message.text
    products[idx]["available"] = True
    save_products(products)
    await update.message.reply_text(
        f"✅ قیمت آپدیت شد!\n\n{products[idx]['name']}\nقبلی: {old_price}\nجدید: {update.message.text}\n\n/admin برای ادامه"
    )
    return ConversationHandler.END

# ==================== تغییر عکس ====================
async def adm_start_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    idx = int(query.data.split("_")[2])
    context.user_data["photo_idx"] = idx
    products = load_products()
    await query.edit_message_text(
        f"📸 عکس جدید برای:\n{products[idx]['name']}\n\nعکس را بفرستید:"
    )
    return WAIT_PHOTO

async def adm_save_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    if not update.message.photo:
        await update.message.reply_text("❌ لطفاً عکس بفرستید!")
        return WAIT_PHOTO
    idx = context.user_data.get("photo_idx")
    if idx is None:
        return ConversationHandler.END
    products = load_products()
    products[idx]["photo_id"] = update.message.photo[-1].file_id
    save_products(products)
    await update.message.reply_text(
        f"✅ عکس ذخیره شد!\n{products[idx]['name']}\n\n/admin برای ادامه"
    )
    return ConversationHandler.END

# ==================== افزودن محصول ====================
async def adm_start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    await query.edit_message_text("➕ اسم محصول جدید را بنویسید:\n(مثال: 🧃 آبمیوه سیب – بسته ۶ عددی)")
    return ADD_NAME

async def adm_add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_name"] = update.message.text
    await update.message.reply_text("💰 قیمت را بنویسید:\n(مثال: ۱۵۰,۰۰۰ تومان)")
    return ADD_PRICE

async def adm_add_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_price"] = update.message.text
    await update.message.reply_text("📸 عکس محصول را بفرستید:\n(یا بنویسید 'رد کن' برای بدون عکس)")
    return ADD_PHOTO

async def adm_add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = None
    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
    elif update.message.text and update.message.text.strip() in ["رد کن", "رد", "skip"]:
        photo_id = None
    else:
        await update.message.reply_text("عکس بفرستید یا بنویسید 'رد کن':")
        return ADD_PHOTO
    
    products = load_products()
    products.append({
        "name": context.user_data["new_name"],
        "price": context.user_data["new_price"],
        "available": True,
        "photo_id": photo_id
    })
    save_products(products)
    await update.message.reply_text(
        f"✅ محصول اضافه شد!\n\n{context.user_data['new_name']}\n💰 {context.user_data['new_price']}\n\n/admin برای ادامه"
    )
    return ConversationHandler.END

# ==================== سفارش ====================
async def btn_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🛒 ثبت سفارش\n\nنام و نام خانوادگی خود را وارد کنید:")
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
    products = load_products()
    available = [p for p in products if p["available"]]
    context.user_data['o_available'] = available
    lines = "\n".join([f"{i+1}. {p['name']} — {p['price']}" for i, p in enumerate(available)])
    await update.message.reply_text(f"📦 شماره محصول را وارد کنید:\n\n{lines}")
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
    await update.message.reply_text("❌ عدد نامعتبر. دوباره امتحان کنید:")
    return ORDER_PRODUCT

async def order_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['o_qty'] = update.message.text
    d = context.user_data
    keyboard = [
        [InlineKeyboardButton("✅ تایید سفارش", callback_data="o_confirm")],
        [InlineKeyboardButton("❌ انصراف", callback_data="o_cancel")]
    ]
    await update.message.reply_text(
        f"✅ خلاصه سفارش:\n\n"
        f"👤 نام: {d['o_name']}\n"
        f"📞 تلفن: {d['o_phone']}\n"
        f"📍 آدرس: {d['o_address']}\n"
        f"📦 محصول: {d['o_product']}\n"
        f"💰 قیمت: {d['o_price']}\n"
        f"🔢 تعداد: {d['o_qty']}\n\n"
        "تایید می‌کنید؟",
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
        text=f"🔔 سفارش جدید!\n\n"
             f"👤 نام: {d['o_name']}\n"
             f"📞 تلفن: {d['o_phone']}\n"
             f"📍 آدرس: {d['o_address']}\n"
             f"📦 محصول: {d['o_product']}\n"
             f"💰 قیمت: {d['o_price']}\n"
             f"🔢 تعداد: {d['o_qty']}\n"
             f"🆔 یوزر: @{user.username or 'ندارد'}\n"
             f"⏰ زمان: {datetime.now().strftime('%H:%M - %Y/%m/%d')}"
    )
    await query.edit_message_text(
        "✅ سفارش شما ثبت شد!\n\nبه زودی با شما تماس می‌گیریم 🙏\n\nبرای سفارش مجدد /start بزنید"
    )
    return ConversationHandler.END

async def order_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ سفارش لغو شد.\n\n/start")
    return ConversationHandler.END

async def cancel_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لغو شد. /start")
    return ConversationHandler.END

# ==================== main ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # مکالمه تغییر قیمت
    price_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(adm_start_price, pattern=r"^adm_price_\d+$")],
        states={EDIT_PRICE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID), adm_save_price)]},
        fallbacks=[CommandHandler("cancel", cancel_conv)],
        per_message=False,
    )

    # مکالمه تغییر عکس
    photo_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(adm_start_photo, pattern=r"^adm_photo_\d+$")],
        states={WAIT_PHOTO: [MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), adm_save_photo)]},
        fallbacks=[CommandHandler("cancel", cancel_conv)],
        per_message=False,
    )

    # مکالمه افزودن محصول
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

    # مکالمه سفارش
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

    # زمان‌بندی خودکار
    app.job_queue.run_daily(job_morning_greeting, time=datetime.strptime("08:00", "%H:%M").time())
    app.job_queue.run_daily(job_send_pricelist, time=datetime.strptime("10:00", "%H:%M").time())

    print("✅ ربات ثمین پخش فعال شد!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
