from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
import logging 

from bot.handlers import (
    list_expense_callback,
    delete_expense_callback,
    delete_expense_callback,
    delete_handle,
    start_handle,
    add_handle,
    list_handle,
    message_handle,
    delete_handle
)
from bot.utils.config import TELEGRAM_BOT_TOKEN

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
        ("delete", "Delete an expense"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    """Main function initializing the bot."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(set_commands).build()

    app.add_handler(CommandHandler("start", start_handle))

    app.add_handler(CommandHandler("add", add_handle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handle))

    app.add_handler(CommandHandler("list", list_handle))
    app.add_handler(CallbackQueryHandler(list_expense_callback, pattern=r"^list:"))

    app.add_handler(CommandHandler("delete", delete_handle))
    app.add_handler(CallbackQueryHandler(delete_expense_callback, pattern=r"^delete:"))

    app.run_polling()
