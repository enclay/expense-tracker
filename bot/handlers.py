from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from bot.database.operations import sql_add_expense, sql_list_expenses
from bot.expense_parser import parse_expenses
from bot.constants import ChatState

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
