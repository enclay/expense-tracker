from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)
import logging 

from bot.utils.config import TELEGRAM_BOT_TOKEN
from bot.handlers import start_handle, add_handle, list_handle, handle_message

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

async def set_commands(application: Application):
    commands = [
        ("start", "Start the bot"),
        ("add", "Add an expense"),
        ("list", "List all expenses"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(set_commands).build()

    app.add_handler(CommandHandler("start", start_handle))
    app.add_handler(CommandHandler("add", add_handle))
    app.add_handler(CommandHandler("list", list_handle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
