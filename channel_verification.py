# توابع کمکی برای بررسی عضویت واقعی در کانال

from telegram import ChatMember
from telegram.error import TelegramError

async def check_user_channel_membership(bot, user_id: int, channel_username: str) -> bool:
    """
    بررسی اینکه کاربر عضو کانال است یا نه
    
    Args:
        bot: شیء bot
        user_id: شناسه کاربر
        channel_username: نام کاربری کانال (بدون @)
    
    Returns:
        bool: True اگر عضو بود، False اگر نبود
    """
    try:
        # دریافت اطلاعات عضویت کاربر
        member = await bot.get_chat_member(chat_id=f"@{channel_username}", user_id=user_id)
        
        # بررسی وضعیت عضویت
        if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
            return True
        else:
            return False
            
    except TelegramError as e:
        print(f"خطا در بررسی عضویت: {e}")
        return False

# نمونه استفاده در ربات:
# 
# async def verify_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     await query.answer()
#     
#     user_id = query.from_user.id
#     
#     # بررسی واقعی عضویت
#     is_member = await check_user_channel_membership(
#         context.bot, 
#         user_id, 
#         CHANNEL_USERNAME
#     )
#     
#     if not is_member:
#         keyboard = [
#             [InlineKeyboardButton("✅ عضو کانال شدم", callback_data="verify_membership")]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         
#         await query.edit_message_text(
#             text=f"❌ متاسفانه هنوز عضو کانال نیستید!\n\n"
#             f"@{CHANNEL_USERNAME} را دنبال کنید و دوباره تلاش کنید.",
#             reply_markup=reply_markup
#         )
#         return CHANNEL_VERIFICATION
#     
#     # اگر عضو بود، ادامه دهید...
#     # (باقی کد)
