from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    filters,
    MessageHandler
)
from telegram import (
    Update,
    ReplyKeyboardMarkup
) 
import logging 
from typing import Dict
from enum import Enum

from bot.utils.config import TELEGRAM_BOT_TOKEN


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

class UserState(Enum):
    AWAITING_EXPENSE = 0

user_states: Dict[int, UserState] = {}


async def add_handle(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_states[user_id] = UserState.AWAITING_EXPENSE

    cancel_markup = ReplyKeyboardMarkup(
            [["Cancel"]],
            one_time_keyboard=True,
            resize_keyboard=True
    )
    await update.message.reply_text("Please enter your item.", reply_markup=cancel_markup)


async def handle_expense(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_states.pop(user_id)

    await update.message.reply_text("Expense added successfully!")


async def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_states.get(user_id) == UserState.AWAITING_EXPENSE:
        await handle_expense(update, context)
    else:
        await update.message.reply_text("Please use the /add command to add an expense.")

async def start_handle(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to Finance Tracker Bot!")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handle))
    app.add_handler(CommandHandler("add", add_handle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
