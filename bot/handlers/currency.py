import logging 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.database.operations import sql_get_user_by_id
from bot.utils.currency import get_currency_symbol
from bot.database.operations import sql_get_user_by_id, sql_update_user
from bot.models.user import User 

logger = logging.getLogger(__name__)

async def currency_handle(update: Update, context: CallbackContext):
    """View and change default currency."""
    
    user = sql_get_user_by_id(update.effective_user.id)

    keyboard = [
         [InlineKeyboardButton("Change to USD", callback_data="currency:usd")],
         [InlineKeyboardButton("Change to EUR", callback_data="currency:eur")],
         [InlineKeyboardButton("Change to RUB", callback_data="currency:rub")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Your current default currency is: {user.currency}",
        reply_markup=markup
    )

async def change_currency_callback(update: Update, context: CallbackContext):
    """Callback which changes currency setting."""
    user_id = update.effective_user.id
    query = update.callback_query
    data = query.data

    await query.answer()
    
    user = User(user_id, currency=data.split(":")[1])
    sql_update_user(user)

    await context.bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )

    await context.bot.send_message(
        query.message.chat.id,
        f"Currency changed to {get_currency_symbol(user.currency) * 3}"
    )
