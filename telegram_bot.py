import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes
from telegram.constants import ChatAction
import sqlite3
from datetime import datetime

# تنظیم logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# مراحل مختلف مکالمه
PHONE_NUMBER, MENU_SELECTION, CHANNEL_VERIFICATION = range(3)

# اطلاعات ربات (توجه: توکن خود را جایگزین کنید)
BOT_TOKEN = "8350647127:AAG0dWujgM0pD9XlsYKFwqOVPvhrNkHn3kk"
CHANNEL_USERNAME = quantex_robo  # این را بعداً مقدار دهید

# ایجاد دیتابیس
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  phone_number TEXT,
                  is_channel_member BOOLEAN DEFAULT 0,
                  joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_action TEXT)''')
    conn.commit()
    conn.close()

# ذخیره کاربر در دیتابیس
def save_user(user_id, phone_number=None):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    if phone_number:
        c.execute('UPDATE users SET phone_number = ? WHERE user_id = ?', 
                 (phone_number, user_id))
    conn.commit()
    conn.close()

# دستور شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    save_user(user.id)
    
    keyboard = [
        [ReplyKeyboardMarkup.BUTTON_CONTACT]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"👋 سلام {user.first_name}!\n\n"
        "برای استفاده از خدمات ما، لطفاً شماره تلفن خود را برای ما اشتراک کنید.",
        reply_markup=reply_markup
    )
    
    return PHONE_NUMBER

# دریافت شماره تلفن
async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    
    if update.message.contact:
        phone_number = update.message.contact.phone_number
        save_user(user.id, phone_number)
        
        # منو اصلی
        keyboard = [
            ["دریافت دوره رایگان"],
            ["ارتباط با پشتیبانی"],
            ["دوره ها"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"✅ شماره تلفن شما ({phone_number}) ثبت شد.\n\n"
            "حالا می‌تونید از خدمات ما استفاده کنید:",
            reply_markup=reply_markup
        )
        
        return MENU_SELECTION
    else:
        await update.message.reply_text(
            "❌ لطفاً از دکمه 'اشتراک تماس' استفاده کنید."
        )
        return PHONE_NUMBER

# منو اصلی
async def menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    user_choice = update.message.text
    
    # ذخیره انتخاب کاربر
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE users SET last_action = ? WHERE user_id = ?', 
             (user_choice, user.id))
    conn.commit()
    conn.close()
    
    # بررسی عضویت در کانال
    keyboard = [
        [InlineKeyboardButton("✅ عضو کانال شدم", callback_data="verify_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚠️ برای دسترسی به «{user_choice}»، ابتدا باید عضو کانال تلگرام ما بشوید.\n\n"
        f"@{CHANNEL_USERNAME} (کانال ما را دنبال کنید)\n\n"
        "بعد از عضویت، روی دکمه زیر کلیک کنید:",
        reply_markup=reply_markup
    )
    
    return CHANNEL_VERIFICATION

# بررسی عضویت در کانال
async def verify_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # اینجا می‌تونید بررسی کنید که کاربر واقعاً عضو کانال شده یا نه
    # برای الآن فرض می‌کنیم که عضو شده است
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE users SET is_channel_member = 1 WHERE user_id = ?', (user_id,))
    c.execute('SELECT last_action FROM users WHERE user_id = ?', (user_id,))
    last_action = c.fetchone()[0]
    conn.commit()
    conn.close()
    
    # بر اساس انتخاب قبلی، پاسخ مختلف
    if last_action == "دریافت دوره رایگان":
        await query.edit_message_text(
            text="✅ عضویت شما تایید شد!\n\n"
            "🎓 **دوره رایگان**\n"
            "دوره رایگان ما شامل:\n"
            "• 5 ویدیو آموزشی\n"
            "• دسترسی به فایل‌های منابع\n"
            "• گروه پشتیبانی\n\n"
            "دسترسی شما فعال شد! 🎉"
        )
    
    elif last_action == "ارتباط با پشتیبانی":
        await query.edit_message_text(
            text="✅ عضویت شما تایید شد!\n\n"
            "📞 **تیم پشتیبانی**\n"
            "برای ارتباط با ما:\n"
            "📧 Email: support@example.com\n"
            "💬 Telegram: @support_username\n"
            "🕐 ساعت پاسخگویی: 9 صبح تا 6 شب\n\n"
            "منتظر پیام شما هستیم! 💙"
        )
    
    elif last_action == "دوره ها":
        keyboard = [
            [InlineKeyboardButton("دوره مبتدی", callback_data="course_beginner")],
            [InlineKeyboardButton("دوره پیشرفته", callback_data="course_advanced")],
            [InlineKeyboardButton("دوره حرفه‌ای", callback_data="course_professional")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="✅ عضویت شما تایید شد!\n\n"
            "🎓 **دوره های موجود**\n"
            "لطفاً یکی از دوره‌ها را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return MENU_SELECTION
    
    # بازگشت به منو اصلی
    keyboard = [
        ["دریافت دوره رایگان"],
        ["ارتباط با پشتیبانی"],
        ["دوره ها"],
        ["منو اصلی"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await query.message.reply_text(
        "برای انتخاب دیگری می‌تونید از منو استفاده کنید:",
        reply_markup=reply_markup
    )
    
    return MENU_SELECTION

# دوره های مختلف
async def course_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    course_data = {
        "course_beginner": {
            "name": "دوره مبتدی",
            "duration": "4 هفته",
            "lessons": 20,
            "price": "رایگان برای اعضا"
        },
        "course_advanced": {
            "name": "دوره پیشرفته",
            "duration": "8 هفته",
            "lessons": 40,
            "price": "50,000 تومان"
        },
        "course_professional": {
            "name": "دوره حرفه‌ای",
            "duration": "12 هفته",
            "lessons": 60,
            "price": "100,000 تومان"
        }
    }
    
    course = course_data.get(query.data)
    
    await query.edit_message_text(
        text=f"📚 {course['name']}\n\n"
        f"⏱️ مدت دوره: {course['duration']}\n"
        f"📹 تعداد درس: {course['lessons']}\n"
        f"💰 قیمت: {course['price']}\n\n"
        "برای ثبت‌نام با پشتیبانی تماس بگیرید! 📞"
    )
    
    return MENU_SELECTION

# منو اصلی دوباره
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        ["دریافت دوره رایگان"],
        ["ارتباط با پشتیبانی"],
        ["دوره ها"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🏠 منو اصلی:\n"
        "یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )
    
    return MENU_SELECTION

# کنسل کردن
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ عملیات لغو شد.\n"
        "برای شروع دوباره /start را بزنید."
    )
    return ConversationHandler.END

# تابع اصلی
def main():
    # مقدار دهی دیتابیس
    init_db()
    
    # ساخت Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE_NUMBER: [MessageHandler(filters.CONTACT | filters.TEXT, receive_phone)],
            MENU_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, menu_selection),
                CommandHandler("menu", main_menu),
                CallbackQueryHandler(course_selection, pattern="^course_")
            ],
            CHANNEL_VERIFICATION: [
                CallbackQueryHandler(verify_membership, pattern="^verify_membership$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # شروع ربات
    print("🤖 ربات شروع شد...")
    print("برای توقف CTRL+C را بزنید")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
