import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler
)
from bot.handlers.message import message_input_handle
from bot.handlers.add import add_confirm_callback, add_cancel_callback
from bot.handlers.list import list_handle, list_expense_callback
from bot.handlers.delete import delete_confirm_callback, delete_cancel_callback
from bot.handlers.sync import export_handle, import_handle
from bot.handlers.import_image import import_image_handle
from bot.utils.config import TELEGRAM_BOT_TOKEN
from bot.filters import MessageFilters 

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

async def set_commands(app: Application):
    """Set the bot commands."""
    commands = [
        ("list", "List expenses"),
        ("export", "Export data"),
    ]
    await app.bot.set_my_commands(commands)

def main():
    """Main function initializing the bot."""

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(set_commands).build()

    app.add_handler(MessageHandler(MessageFilters.RAW_TEXT, message_input_handle))
    app.add_handler(MessageHandler(MessageFilters.PHOTO, import_image_handle))
    app.add_handler(MessageHandler(MessageFilters.JSON, import_handle))

    app.add_handler(CallbackQueryHandler(add_confirm_callback, pattern=r"^confirm_expense"))
    app.add_handler(CallbackQueryHandler(add_cancel_callback, pattern=r"^cancel_expense"))
    app.add_handler(CallbackQueryHandler(delete_confirm_callback, pattern=r"^confirm_deletion"))
    app.add_handler(CallbackQueryHandler(delete_cancel_callback, pattern=r"^cancel_deletion"))
    app.add_handler(CallbackQueryHandler(list_expense_callback, pattern=r"^list:"))

    app.add_handler(CommandHandler("list", list_handle))
    app.add_handler(CommandHandler("export", export_handle))

    app.run_polling()
