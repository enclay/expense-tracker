from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
)
from telegram import (
    Update
) 
import logging 
from bot.utils.config import TELEGRAM_BOT_TOKEN


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def start_handle(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to Finance Tracker Bot! 📊\n")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handle))
    app.run_polling()


if __name__ == "__main__":
    main()
