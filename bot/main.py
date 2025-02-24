from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)
import logging 

from bot.utils.config import TELEGRAM_BOT_TOKEN
from bot.handlers import change_month_callback, start_handle, add_handle, list_handle, message_handle 
from bot.handlers import change_month_callback
from telegram.ext import CallbackQueryHandler

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

async def set_commands(application: Application):
    """Set the bot commands."""
    commands = [
        ("start", "Start the bot"),
        ("add", "Add an expense"),
        ("list", "List all expenses"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    """Main function initializing the bot."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(set_commands).build()

    app.add_handler(CommandHandler("start", start_handle))

    app.add_handler(CommandHandler("add", add_handle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handle))

    app.add_handler(CommandHandler("list", list_handle))
    app.add_handler(CallbackQueryHandler(change_month_callback, pattern=r"^expenses:"))

    app.run_polling()
