from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters
)
from telegram import (
    Update,
    ReplyKeyboardMarkup
)
from telegram.constants import (
    ParseMode
)
from openai import (
    OpenAI
)
import logging 
import sqlite3
import re

from typing import List, Tuple
from enum import Enum

from bot.utils.config import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, DB_PATH


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

class ChatState(Enum):
    EXPENSE_INPUT = 0


def parse_expenses(user_input: str):
    try:
        client = OpenAI(api_key = OPENAI_API_KEY)

        prompt = f"""
        Extract the expense description and cost from the following message:
        "{user_input}"
        
        - If a cost is found, return it as a float.
        - If no cost is found, return 5.00 as default.
        - If the cost includes currency symbols ($, €, etc.), remove them.
        - Return a JSON response like this:
        
        {{"expense": "Lunch at Subway", "cost": 12.50}}
        """

        messages = [
            {"role": "system", "content": "You are a finance assistant extracting expenses from user text."},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=50,
        )

        gpt_output = response.choices[0].message.content

        match = re.search(r'{"expense": "(.*?)", "cost": (\d+\.\d+)}', gpt_output)
        if match:
            expense = match.group(1)
            cost = float(match.group(2))
            return expense, cost

    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")

    return user_input, 0


def sql_add_expense(user_id: int, expense: str, cost: float):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO Expense (user_id, expense, cost, currency, time) VALUES (?, ?, ?, ?, strftime('%s', 'now'))",
        (user_id, expense, cost, 0)
    )

    conn.commit()
    conn.close()


def sql_list_expenses(user_id: int) -> List[Tuple]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, expense, cost, currency, time FROM Expense WHERE user_id = ? ORDER BY time DESC",
        (user_id,)
    )

    expenses = cursor.fetchall()
    conn.close()
    return expenses


async def handle_expense(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    expense_text = update.message.text

    if expense_text.lower() == "cancel":
        context.user_data.pop("chat_state", None)
        return

    expense, cost = parse_expenses(expense_text)
    sql_add_expense(user_id, expense, cost)
    context.user_data.pop("chat_state", None)

    await update.message.reply_text("Expense added successfully!")


async def handle_message(update: Update, context: CallbackContext):
    chat_state = context.user_data.get("chat_state", None)
    
    if chat_state == ChatState.EXPENSE_INPUT:
        await handle_expense(update, context)
    else:
        await update.message.reply_text("Please use the /add command to add an expense.")


async def add_handle(update: Update, context: CallbackContext):
    context.user_data["chat_state"] = ChatState.EXPENSE_INPUT

    cancel_markup = ReplyKeyboardMarkup(
            [["Cancel"]],
            one_time_keyboard=True,
            resize_keyboard=True
    )
    await update.message.reply_text("Please enter your item.", reply_markup=cancel_markup)


async def list_handle(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    expenses = sql_list_expenses(user_id)

    if not expenses:
        await update.message.reply_text("No expenses found.")
        return

    message = "Your Expenses:\n"
    for exp in expenses:
        expense_id, description, cost, currency, timestamp = exp
        message += f"{description} - ${cost} (Time: {timestamp})\n"

    await update.message.reply_text(message)


async def start_handle(update: Update, context: CallbackContext):
    welcome_message = (
        "*Expense Tracker Bot*\n\n"
        "*Easily track your expenses and stay on top of your budget!*\n\n"
        "*/add* - Add new expense\n"
        "*/list* - List all expenses\n"
        "*/start* - Learn how to use the bot\n\n"
        "Start tracking now by using */add*!"
    )
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)

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


if __name__ == "__main__":
    main()
