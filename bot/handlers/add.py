from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.database.operations import sql_add_expenses
from bot.llm.expense_parser import parse_expenses


async def add_handle(update: Update, context: CallbackContext):
    """Handle new expenses."""
    message_text = update.message.text

    expenses = parse_expenses(message_text)

    if not expenses:
        await update.message.reply_text("No valid expenses found.")
        return

    context.user_data["pending_expenses"] = expenses

    confirmation_text = "Please confirm your expenses:\n\n"
    for i, expense in enumerate(expenses, 1):
        formatted_time = datetime.fromtimestamp(int(expense.time)).strftime("%d/%m/%Y, %H:%M")
        confirmation_text += f"*{i}.* {expense.description} - {expense.cost:.2f} {expense.currency.upper()} ({formatted_time})\n"

    keyboard = [
        [InlineKeyboardButton("\u2705 Confirm", callback_data="confirm_expense")],
        [InlineKeyboardButton("\u274C Cancel", callback_data="cancel_expense")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        confirmation_text, reply_markup=reply_markup, parse_mode="Markdown"
    )

async def add_confirm_callback(update: Update, context: CallbackContext):
    """Callback saving pending expenses after user confirmation."""
    query = update.callback_query
    await query.answer()

    pending_expenses = context.user_data.get("pending_expenses")
    if not pending_expenses:
        await query.edit_message_text("No pending expenses found.")
        return
    
    user_id = update.effective_user.id
    sql_add_expenses(user_id, pending_expenses)
    
    context.user_data.pop("pending_expenses", None)
    await query.edit_message_text(f"{len(pending_expenses)} expense(s) added successfully!")

async def add_cancel_callback(update: Update, context: CallbackContext):
    """Callback cancelling new transactions"""
    query = update.callback_query
    await query.answer()

    context.user_data.pop("pending_expenses", None)
    await query.edit_message_text("Expense entry cancelled.")
