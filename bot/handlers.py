from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from bot.database.operations import sql_add_expense, sql_list_expenses
from bot.expense_parser import parse_expenses
from bot.constants import ChatState
from bot.utils.datetime import add_months

from datetime import datetime
import logging 

logger = logging.getLogger(__name__)

async def process_expense(update: Update, context: CallbackContext):
    """ Process the expense and save to persistent storage"""
    user_id = update.effective_user.id
    expense_text = update.message.text

    if expense_text.lower() == "cancel":
        context.user_data.pop("chat_state", None)
        return

    expense, cost = parse_expenses(expense_text)
    sql_add_expense(user_id, expense, cost)
    context.user_data.pop("chat_state", None)

    await update.message.reply_text("Expense added successfully!")


async def message_handle(update: Update, context: CallbackContext):
    """Handle processing general messages such as new expense entry."""
    chat_state = context.user_data.get("chat_state", None)
    
    if chat_state == ChatState.EXPENSE_INPUT:
        await process_expense(update, context)
    else:
        await update.message.reply_text("Unknown command. Please use */start* to see available commands.", parse_mode=ParseMode.MARKDOWN)


async def add_handle(update: Update, context: CallbackContext):
    """Handle adding a new expense."""
    context.user_data["chat_state"] = ChatState.EXPENSE_INPUT

    cancel_markup = ReplyKeyboardMarkup(
            [["Cancel"]],
            one_time_keyboard=True,
            resize_keyboard=True
    )
    await update.message.reply_text("Please enter your item.", reply_markup=cancel_markup)


async def list_handle(update: Update, context: CallbackContext):
    """Handle displaying expenses for the current month with pagination."""
    current_month = datetime.now().strftime("%Y-%m")
    await refresh_list(update, context, current_month)

async def refresh_list(update: Update, context: CallbackContext, month: str):
    """Helper function which updates this list according to month"""
    user_id = update.effective_user.id

    expenses = sql_list_expenses(user_id, month)
    try:
        dt = datetime.strptime(month, "%Y-%m")
        month_title = dt.strftime("%B %Y")
    except Exception:
        month_title = month

    if not expenses:
        message_text = f"No expenses found for {month_title}."
    else:
        message_text = f"*Expenses for {month_title}:*\n"
        for exp in expenses:
            expense_id, description, cost, currency, timestamp = exp
            message_text += f"- {description} - ${cost}\n"

    keyboard = [
        [
            InlineKeyboardButton("← Previous", callback_data=f"expenses:prev:{month}"),
            InlineKeyboardButton("Next →", callback_data=f"expenses:next:{month}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

async def change_month_callback(update: Update, context: CallbackContext):
    """Callback function handling month navigation"""
    query = update.callback_query
    await query.answer()
    data = query.data  # Expected format: "expenses:prev:YYYY-MM" or "expenses:next:YYYY-MM"
    try:
        _, direction, current_month = data.split(":")
        dt = datetime.strptime(current_month, "%Y-%m")
        if direction == "prev":
            new_dt = add_months(dt, -1)
        elif direction == "next":
            new_dt = add_months(dt, 1)
        else:
            new_dt = dt
        new_month = new_dt.strftime("%Y-%m")
    except Exception as e:
        logger.error(f"Error parsing callback data '{data}': {e}")
        new_month = datetime.now().strftime("%Y-%m")

    await refresh_list(update, context, new_month)

async def start_handle(update: Update, context: CallbackContext):
    """Handle the /start command."""
    welcome_message = (
        "*Expense Tracker Bot*\n\n"
        "*Easily track your expenses and stay on top of your budget!*\n\n"
        "*/add* - Add new expense\n"
        "*/list* - List all expenses\n"
        "*/start* - Learn how to use the bot\n\n"
        "Start tracking now by using */add*!"
    )
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
