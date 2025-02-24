from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from bot.expense_parser import parse_expenses
from bot.database.operations import sql_add_expense
from bot.constants import ChatState

async def add_handle(update: Update, context: CallbackContext):
    """Handle adding a new expense."""
    context.user_data["chat_state"] = ChatState.EXPENSE_INPUT
    await update.message.reply_text("Please enter your expense.")

async def process_expense(update: Update, context: CallbackContext):
    """Process the expense and save to persistent storage"""
    user_id = update.effective_user.id
    expense_text = update.message.text

    expense, cost = parse_expenses(expense_text)
    context.user_data["pending_expense"] = (expense, cost)

    keyboard = [
        [
            InlineKeyboardButton("\u2705 Confirm", callback_data="add_confirm"),
            InlineKeyboardButton("\u274C Cancel", callback_data="add_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
            f"Parsed expense:\n\n*{expense}* - ${cost:.2f}\nDo you want to confirm?",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def add_confirm_callback(update: Update, context: CallbackContext):
    """Callback: Save the pending expense after user confirms."""
    query = update.callback_query

    await query.answer()
    pending = context.user_data.get("pending_expense")
    if not pending:
        await query.edit_message_text("No pending expense found.")
        return
    expense, cost = pending
    user_id = update.effective_user.id
    sql_add_expense(user_id, expense, cost)

    context.user_data.pop("pending_expense", None)
    context.user_data.pop("chat_state", None)
    await query.edit_message_text("Expense added successfully.")


async def add_cancel_callback(update: Update, context: CallbackContext):
    """Callback: Cancel the pending expense addition."""
    query = update.callback_query

    await query.answer()
    context.user_data.pop("pending_expense", None)
    context.user_data.pop("chat_state", None)
    await query.edit_message_text("Expense entry cancelled.")
