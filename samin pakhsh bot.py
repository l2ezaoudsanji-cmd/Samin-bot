import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ==================== تنظیمات ====================
BOT_TOKEN = "8946756497:AAFxaT2tpx-66OwzDp4LJl1IHTCYqloSCl0"
CHANNEL_ID = "@saminpakhsh1"
ADMIN_ID = 1884167467

# ==================== مراحل سفارش ====================
NAME, PHONE, ADDRESS, PRODUCT, QUANTITY, CONFIRM = range(6)

# ==================== محصولات نمونه ====================
# اینا رو هر روز ویرایش کن
PRODUCTS = [
    {"name": "روغن آفتابگردان ۱۸ کیلویی", "price": "۱,۲۵۰,۰۰۰ تومان"},
    {"name": "برنج ایرانی درجه یک", "price": "۸۵۰,۰۰۰ تومان"},
    {"name": "شکر کیلویی", "price": "۱۲۰,۰۰۰ تومان"},
    {"name": "ماکارونی ۵۰۰ گرمی", "price": "۴۵,۰۰۰ تومان"},
    {"name": "رب گوجه فرنگی ۸۰۰ گرمی", "price": "۶۵,۰۰۰ تومان"},
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== تبدیل تاریخ شمسی ====================
def get_jalali_date():
    try:
        import jdatetime
        now = jdatetime.datetime.now()
        weekdays = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
        months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور',
                  'مهر','آبان','آذر','دی','بهمن','اسفند']
        day_name = weekdays[now.weekday()]
        return f"{day_name} {now.day} {months[now.month-1]} {now.year}"
    except:
        return datetime.now().strftime("%Y-%m-%d")

# ==================== ارسال پیام صبحگاهی به کانال ====================
async def send_morning_message(context: ContextTypes.DEFAULT_TYPE):
    date_str = get_jalali_date()
    
    product_list = "\n".join([
        f"🔹 {p['name']} — {p['price']}" for p in PRODUCTS
    ])
    
    message = f"""🌅 صبح بخیر

📅 {date_str}

━━━━━━━━━━━━━━━━━━
🏪 ثمین پخش | پخش مواد غذایی
━━━━━━━━━━━━━━━━━━

📦 لیست محصولات امروز:

{product_list}

━━━━━━━━━━━━━━━━━━
📲 برای سفارش به ربات مراجعه کنید:
👉 @Samin_pakhsh_bot

☎️ تحویل درب منزل | کرمانشاه"""

    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=message
        )
        logger.info("پیام صبحگاهی ارسال شد")
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {e}")

# ==================== دستور /start ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
        [InlineKeyboardButton("📦 مشاهده محصولات", callback_data="products")],
        [InlineKeyboardButton("📞 تماس با ما", callback_data="contact")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌿 به ربات ثمین پخش خوش آمدید!\n\n"
        "پخش عمده مواد غذایی در کرمانشاه\n\n"
        "از منوی زیر انتخاب کنید:",
        reply_markup=reply_markup
    )

# ==================== نمایش محصولات ====================
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    product_list = "\n".join([
        f"🔹 {p['name']}\n    💰 {p['price']}" for p in PRODUCTS
    ])
    
    keyboard = [[InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(
        f"📦 محصولات امروز:\n\n{product_list}\n\n"
        "برای سفارش دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== شروع سفارش ====================
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🛒 ثبت سفارش\n\n"
        "لطفاً نام و نام خانوادگی خود را وارد کنید:"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📞 شماره تلفن خود را وارد کنید:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("📍 آدرس تحویل را وارد کنید:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    
    product_list = "\n".join([
        f"{i+1}. {p['name']} — {p['price']}" for i, p in enumerate(PRODUCTS)
    ])
    
    await update.message.reply_text(
        f"📦 محصول مورد نظر را انتخاب کنید (شماره بزنید):\n\n{product_list}"
    )
    return PRODUCT

async def get_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        idx = int(update.message.text) - 1
        if 0 <= idx < len(PRODUCTS):
            context.user_data['product'] = PRODUCTS[idx]['name']
            context.user_data['price'] = PRODUCTS[idx]['price']
            await update.message.reply_text("🔢 تعداد مورد نظر را وارد کنید:")
            return QUANTITY
        else:
            await update.message.reply_text("❌ عدد نامعتبر. دوباره امتحان کنید:")
            return PRODUCT
    except:
        await update.message.reply_text("❌ لطفاً فقط عدد وارد کنید:")
        return PRODUCT

async def get_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['quantity'] = update.message.text
    
    d = context.user_data
    summary = (
        f"✅ خلاصه سفارش:\n\n"
        f"👤 نام: {d['name']}\n"
        f"📞 تلفن: {d['phone']}\n"
        f"📍 آدرس: {d['address']}\n"
        f"📦 محصول: {d['product']}\n"
        f"💰 قیمت: {d['price']}\n"
        f"🔢 تعداد: {d['quantity']}\n\n"
        "آیا سفارش تایید می‌شود؟"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ تایید سفارش", callback_data="confirm")],
        [InlineKeyboardButton("❌ انصراف", callback_data="cancel")]
    ]
    
    await update.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    d = context.user_data
    user = update.effective_user
    
    # ارسال به ادمین
    admin_message = (
        f"🔔 سفارش جدید!\n\n"
        f"👤 نام: {d['name']}\n"
        f"📞 تلفن: {d['phone']}\n"
        f"📍 آدرس: {d['address']}\n"
        f"📦 محصول: {d['product']}\n"
        f"💰 قیمت: {d['price']}\n"
        f"🔢 تعداد: {d['quantity']}\n"
        f"🆔 یوزر تلگرام: @{user.username or 'ندارد'}\n"
        f"⏰ زمان: {datetime.now().strftime('%H:%M - %Y/%m/%d')}"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
    except Exception as e:
        logger.error(f"خطا در ارسال به ادمین: {e}")
    
    await query.edit_message_text(
        "✅ سفارش شما با موفقیت ثبت شد!\n\n"
        "به زودی با شما تماس می‌گیریم.\n"
        "ممنون از اعتماد شما 🙏\n\n"
        "برای سفارش مجدد /start را بزنید"
    )
    return ConversationHandler.END

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ سفارش لغو شد.\n\nبرای شروع مجدد /start را بزنید")
    return ConversationHandler.END

# ==================== تماس با ما ====================
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📞 تماس با ثمین پخش\n\n"
        "📱 تلفن: ۰۹۱۰۰۰۰۰۰۰۰\n"
        "📍 کرمانشاه\n"
        "⏰ ساعت کاری: ۸ صبح تا ۶ عصر\n\n"
        "برای بازگشت /start را بزنید"
    )

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")],
        [InlineKeyboardButton("📦 مشاهده محصولات", callback_data="products")],
        [InlineKeyboardButton("📞 تماس با ما", callback_data="contact")],
    ]
    await query.edit_message_text(
        "🌿 به ربات ثمین پخش خوش آمدید!\n\n"
        "از منوی زیر انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== دستور ادمین برای ارسال دستی ====================
async def send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await send_morning_message(context)
    await update.message.reply_text("✅ پیام صبحگاهی به کانال ارسال شد!")

# ==================== اجرای ربات ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # مکالمه سفارش
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order, pattern="^order$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product)],
            QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity)],
            CONFIRM: [
                CallbackQueryHandler(confirm_order, pattern="^confirm$"),
                CallbackQueryHandler(cancel_order, pattern="^cancel$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_now))  # برای ارسال دستی
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(show_products, pattern="^products$"))
    app.add_handler(CallbackQueryHandler(contact, pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back$"))
    
    # ارسال خودکار هر روز ساعت ۸ صبح
    app.job_queue.run_daily(
        send_morning_message,
        time=datetime.strptime("08:00", "%H:%M").time(),
        days=(0, 1, 2, 3, 4, 5, 6)
    )
    
    print("✅ ربات ثمین پخش فعال شد!")
    app.run_polling()

if __name__ == "__main__":
    main()
