import logging
import json
import os
from datetime import datetime, time
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
EDIT_CHOOSE, EDIT_FIELD, EDIT_VALUE = range(9, 12)

# ==================== مدیریت محصولات ====================
def load_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # محصولات پیش‌فرض
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

# ==================== تاریخ ====================
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

# ==================== ارسال صبحگاهی ====================
async def ask_admin_morning(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ همون قیمت‌ها، بفرست!", callback_data="send_same")],
        [InlineKeyboardButton("✏️ میخوام قیمت عوض کنم", callback_data="edit_prices")],
    ]
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text="🌅 صبح بخیر!\n\nوقت ارسال لیست قیمت‌هاست.\nقیمت‌ها همون دیروزه یا عوض شده؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def send_to_channel(context: ContextTypes.DEFAULT_TYPE):
    products = load_products()
    message = build_channel_message()
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message)
    # ارسال عکس‌های محصولات موجود
    for p in products:
        if p["available"] and p.get("photo_id"):
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=p["photo_id"],
                caption=f"{p['name']}\n💰 {p['price']}"
            )

async def handle_send_same(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await send_to_channel(context)
    await query.edit_message_text("✅ لیست با موفقیت به کانال فرستاده شد!")

# ==================== ویرایش قیمت‌ها ====================
async def handle_edit_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    products = load_products()
    keyboard = []
    for i, p in enumerate(products):
        status = "✅" if p["available"] else "🚫"
        keyboard.append([InlineKeyboardButton(f"{status} {i+1}. {p['name'][:30]}...", callback_data=f"ep_{i}")])
    keyboard.append([InlineKeyboardButton("✅ تموم شد، بفرست!", callback_data="send_same")])
    await query.edit_message_text(
        "کدوم محصول رو میخوای ویرایش کنی؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_edit_product_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[1])
    products = load_products()
    p = products[idx]
    context.user_data["editing_idx"] = idx
    
    keyboard = [
        [InlineKeyboardButton("💰 تغییر قیمت", callback_data=f"ef_price")],
        [InlineKeyboardButton("🚫 ناموجود کن", callback_data=f"ef_unavailable")],
        [InlineKeyboardButton("✅ موجود کن", callback_data=f"ef_available")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="edit_prices")],
    ]
    await query.edit_message_text(
        f"محصول:\n{p['name']}\n\nقیمت: {p['price']}\nوضعیت: {'✅ موجود' if p['available'] else '🚫 ناموجود'}\n\nچی میخوای تغییر بدی؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    field = query.data.split("_")[1]
    idx = context.user_data.get("editing_idx")
    products = load_products()
    
    if field == "unavailable":
        products[idx]["available"] = False
        products[idx]["price"] = "ناموجود"
        save_products(products)
        await query.edit_message_text(f"🚫 محصول ناموجود شد:\n{products[idx]['name']}\n\nبرای ادامه /admin بزن")
        return ConversationHandler.END
    elif field == "available":
        products[idx]["available"] = True
        save_products(products)
        await query.edit_message_text(f"✅ محصول موجود شد:\n{products[idx]['name']}\n\nبرای ادامه /admin بزن")
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
    await update.message.reply_text(
        f"✅ قیمت آپدیت شد!\n{products[idx]['name']}\nقیمت جدید: {update.message.text}\n\nبرای ادامه /admin بزن"
    )
    return ConversationHandler.END

# ==================== پنل ادمین ====================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    keyboard = [
        [InlineKeyboardButton("📋 مدیریت محصولات", callback_data="manage_products")],
        [InlineKeyboardButton("➕ افزودن محصول جدید", callback_data="add_product")],
        [InlineKeyboardButton("📸 آپدیت عکس محصولات", callback_data="update_photos")],
        [InlineKeyboardButton("📤 ارسال لیست به کانال", callback_data="send_same")],
    ]
    await update.message.reply_text(
        "👨‍💼 پنل مدیریت ثمین پخش\n\nچه کاری میخوای انجام بدی؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def manage_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    products = load_products()
    keyboard = []
    for i, p in enumerate(products):
        status = "✅" if p["available"] else "🚫"
        keyboard.append([InlineKeyboardButton(f"{status} {i+1}. {p['name'][:35]}", callback_data=f"ep_{i}")])
    keyboard.append([InlineKeyboardButton("➕ محصول جدید", callback_data="add_product")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")])
    await query.edit_message_text(
        "📋 لیست محصولات:\n✅ موجود | 🚫 ناموجود\n\nروی هر محصول بزن برای ویرایش:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== افزودن محصول ====================
async def start_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("➕ افزودن محصول جدید\n\nاسم محصول رو بنویس:\n(مثال: 🧃 آبمیوه سیب – بسته ۶ عددی)")
    return ADD_NAME

async def get_add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_name"] = update.message.text
    await update.message.reply_text("💰 قیمت محصول رو بنویس:\n(مثال: ۱۵۰,۰۰۰ تومان)")
    return ADD_PRICE

async def get_add_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_price"] = update.message.text
    await update.message.reply_text("📸 عکس محصول رو بفرست:\n(اگه عکس نداری، بنویس 'رد کن')")
    return ADD_PHOTO

async def get_add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = load_products()
    photo_id = None
    
    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
    
    new_product = {
        "name": context.user_data["new_name"],
        "price": context.user_data["new_price"],
        "available": True,
        "photo_id": photo_id
    }
    products.append(new_product)
    save_products(products)
    
    await update.message.reply_text(
        f"✅ محصول اضافه شد!\n\n{new_product['name']}\n💰 {new_product['price']}\n\nبرای مدیریت بیشتر /admin بزن"
    )
    return ConversationHandler.END

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.strip() in ["رد کن", "رد", "skip"]:
        products = load_products()
        new_product = {
            "name": context.user_data["new_name"],
            "price": context.user_data["new_price"],
            "available": True,
            "photo_id": None
        }
        products.append(new_product)
        save_products(products)
        await update.message.reply_text(
            f"✅ محصول بدون عکس اضافه شد!\n\n{new_product['name']}\n💰 {new_product['price']}\n\nبرای مدیریت /admin بزن"
        )
        return ConversationHandler.END
    await update.message.reply_text("عکس بفرست یا بنویس 'رد کن':")
    return ADD_PHOTO

# ==================== آپدیت عکس ====================
async def update_photos_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    products = load_products()
    keyboard = []
    for i, p in enumerate(products):
        has_photo = "📸" if p.get("photo_id") else "❌"
        keyboard.append([InlineKeyboardButton(f"{has_photo} {i+1}. {p['name'][:35]}", callback_data=f"uphoto_{i}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")])
    await query.edit_message_text(
        "📸 آپدیت عکس محصولات:\n📸 دارد عکس | ❌ ندارد عکس\n\nروی محصول بزن تا عکس بفرستی:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def choose_photo_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[1])
    context.user_data["photo_product_idx"] = idx
    products = load_products()
    await query.edit_message_text(
        f"📸 عکس این محصول رو بفرست:\n{products[idx]['name']}"
    )

async def receive_product_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not update.message.photo:
        return
    idx = context.user_data.get("photo_product_idx")
    if idx is None:
        return
    products = load_products()
    products[idx]["photo_id"] = update.message.photo[-1].file_id
    save_products(products)
    await update.message.reply_text(
        f"✅ عکس ذخیره شد!\n{products[idx]['name']}\n\nبرای ادامه /admin بزن"
    )
    context.user_data["photo_product_idx"] = None

# ==================== کاتالوگ ====================
async def send_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = load_products()
    await update.message.reply_text("📚 کاتالوگ محصولات ثمین پخش غرب:")
    for p in products:
        caption = f"{p['name']}\n💰 {'ناموجود 🚫' if not p['available'] else p['price']}"
        if p.get("photo_id"):
            await update.message.reply_photo(photo=p["photo_id"], caption=caption)
        else:
            await update.message.reply_text(caption)

# ==================== start ====================
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

async def show_products_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    await query.edit_message_text(
        f"📋 لیست قیمت امروز:\n\n{build_product_text()}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_catalog_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📚 کاتالوگ محصولات در حال بارگذاری...")
    products = load_products()
    for p in products:
        caption = f"{p['name']}\n💰 {'ناموجود 🚫' if not p['available'] else p['price']}"
        if p.get("photo_id"):
            await query.message.reply_photo(photo=p["photo_id"], caption=caption)
        else:
            await query.message.reply_text(caption)

async def contact_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📞 تماس با ثمین پخش غرب\n\n"
        "☎️ ۰۹۱۸۳۸۹۰۵۴۲\n"
        "☎️ ۰۹۱۸۳۲۲۰۳۹۷\n"
        "☎️ ۰۹۱۲۶۳۵۴۵۰۱\n\n"
        "📍 کرمانشاه\n"
        "⏰ ۸ صبح تا ۶ عصر\n\n"
        "برای بازگشت /start بزنید"
    )

async def back_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
        [InlineKeyboardButton("📚 کاتالوگ محصولات", callback_data="catalog")],
        [InlineKeyboardButton("📋 لیست قیمت امروز", callback_data="products")],
        [InlineKeyboardButton("📞 تماس با ما", callback_data="contact")],
    ]
    await query.edit_message_text(
        "🌿 ثمین پخش غرب\n\nاز منو انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_back_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📋 مدیریت محصولات", callback_data="manage_products")],
        [InlineKeyboardButton("➕ افزودن محصول جدید", callback_data="add_product")],
        [InlineKeyboardButton("📸 آپدیت عکس محصولات", callback_data="update_photos")],
        [InlineKeyboardButton("📤 ارسال لیست به کانال", callback_data="send_same")],
    ]
    await query.edit_message_text(
        "👨‍💼 پنل مدیریت ثمین پخش",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== سفارش ====================
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🛒 ثبت سفارش\n\nنام و نام خانوادگی خود را وارد کنید:")
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
    await update.message.reply_text(f"📦 شماره محصول را وارد کنید:\n\n{lines}")
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
        else:
            await update.message.reply_text("❌ عدد نامعتبر:")
            return ORDER_PRODUCT
    except:
        await update.message.reply_text("❌ فقط عدد وارد کنید:")
        return ORDER_PRODUCT

async def get_order_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['quantity'] = update.message.text
    d = context.user_data
    keyboard = [
        [InlineKeyboardButton("✅ تایید سفارش", callback_data="confirm")],
        [InlineKeyboardButton("❌ انصراف", callback_data="cancel")]
    ]
    await update.message.reply_text(
        f"✅ خلاصه سفارش:\n\n"
        f"👤 {d['name']}\n📞 {d['phone']}\n📍 {d['address']}\n"
        f"📦 {d['product']}\n💰 {d['price']}\n🔢 {d['quantity']}\n\nتایید می‌کنید؟",
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
        text=f"🔔 سفارش جدید!\n\n👤 {d['name']}\n📞 {d['phone']}\n📍 {d['address']}\n"
             f"📦 {d['product']}\n💰 {d['price']}\n🔢 {d['quantity']}\n"
             f"🆔 @{user.username or 'ندارد'}\n⏰ {datetime.now().strftime('%H:%M - %Y/%m/%d')}"
    )
    await query.edit_message_text("✅ سفارش ثبت شد!\nبه زودی تماس می‌گیریم 🙏\n\n/start")
    return ConversationHandler.END

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ سفارش لغو شد.\n\n/start")
    return ConversationHandler.END

async def send_now_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await send_to_channel(context)
    await update.message.reply_text("✅ لیست به کانال ارسال شد!")

# ==================== main ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # مکالمه ویرایش قیمت
    edit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_edit_product_choose, pattern="^ep_")],
        states={
            EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edit_value)],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("admin", admin_panel)],
    )

    # مکالمه افزودن محصول
    add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_product, pattern="^add_product$")],
        states={
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_add_name)],
            ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_add_price)],
            ADD_PHOTO: [
                MessageHandler(filters.PHOTO, get_add_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, skip_photo),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # مکالمه سفارش
    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order, pattern="^order$")],
        states={
            ORDER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_name)],
            ORDER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_phone)],
            ORDER_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_address)],
            ORDER_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_product)],
            ORDER_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_quantity)],
            ORDER_CONFIRM: [
                CallbackQueryHandler(confirm_order, pattern="^confirm$"),
                CallbackQueryHandler(cancel_order, pattern="^cancel$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("catalog", send_catalog))
    app.add_handler(CommandHandler("send", send_now_cmd))
    app.add_handler(edit_conv)
    app.add_handler(add_conv)
    app.add_handler(order_conv)
    app.add_handler(CallbackQueryHandler(handle_send_same, pattern="^send_same$"))
    app.add_handler(CallbackQueryHandler(handle_edit_prices, pattern="^edit_prices$"))
    app.add_handler(CallbackQueryHandler(handle_edit_field, pattern="^ef_"))
    app.add_handler(CallbackQueryHandler(manage_products, pattern="^manage_products$"))
    app.add_handler(CallbackQueryHandler(update_photos_menu, pattern="^update_photos$"))
    app.add_handler(CallbackQueryHandler(choose_photo_product, pattern="^uphoto_"))
    app.add_handler(CallbackQueryHandler(show_products_btn, pattern="^products$"))
    app.add_handler(CallbackQueryHandler(show_catalog_btn, pattern="^catalog$"))
    app.add_handler(CallbackQueryHandler(contact_btn, pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(back_btn, pattern="^back$"))
    app.add_handler(CallbackQueryHandler(admin_back_btn, pattern="^admin_back$"))
    app.add_handler(MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), receive_product_photo))

    # هر روز ۷:۳۰ صبح
    app.job_queue.run_daily(
        ask_admin_morning,
        time=time(hour=7, minute=30, second=0),
        days=(0, 1, 2, 3, 4, 5, 6)
    )

    print("✅ ربات ثمین پخش فعال شد!")
    app.run_polling()

if __name__ == "__main__":
    main()
