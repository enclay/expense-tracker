from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

async def start_handle(update: Update, context: CallbackContext):
    """Handle the /start command."""
    welcome_message = (
        "*Expense Tracker Bot*\n\n"
        "*Easily track your expenses and stay on top of your budget!*\n\n"
        "*/add* - Add new expense\n"
        "*/list* - List all expenses\n"
        "*/delete* - Delete an expense\n\n"
        "*/start* - Learn how to use the bot\n\n"
        "Start tracking now by using */add*!"
    )
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
