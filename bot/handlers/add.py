from datetime import datetime
from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.database.operations import sql_add_expenses
from bot.database.models import Expense 
from bot.llm.expense_parser import parse_expenses


async def add_handle(update: Update, context: CallbackContext):
    """Handle new expenses."""
    message_text = update.message.text

    expenses = parse_expenses(message_text)

    await present_expenses_for_confirmation(update, context, expenses)

async def present_expenses_for_confirmation(update: Update, context: CallbackContext, expenses: List[Expense]):
    if not expenses:
        await update.message.reply_text("No valid expenses found.")
        return

    message_id  = context.user_data.pop("insertion_message_id", None)
    if message_id:
        await context.bot.edit_message_text(
            text="Adding expenses is cancelled.",
            message_id=message_id,
            chat_id=update.message.chat_id
        )
    context.user_data["pending_insertion"] = expenses

    confirmation_text = "Please confirm your expenses:\n\n"
    for i, expense in enumerate(expenses, 1):
        formatted_time = datetime.fromtimestamp(int(expense.time)).strftime("%d/%m/%Y, %H:%M")
        confirmation_text += f"*{i}.* {expense.description} - {expense.cost:.2f} {expense.currency.upper()} ({formatted_time})\n"

    keyboard = [
        [InlineKeyboardButton("\u2705 Confirm", callback_data="confirm_expense")],
        [InlineKeyboardButton("\u274C Cancel", callback_data="cancel_expense")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await update.message.reply_text(
        confirmation_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    context.user_data["insertion_message_id"] = message.message_id

async def add_confirm_callback(update: Update, context: CallbackContext):
    """Callback saving pending expenses after user confirmation."""
    query = update.callback_query

    await query.answer()
    context.user_data.pop("insertion_message_id", None)

    pending_expenses = context.user_data.get("pending_insertion")
    if not pending_expenses:
        await query.edit_message_text("No pending expenses found.")
        return
    
    user_id = update.effective_user.id
    sql_add_expenses(user_id, pending_expenses)
    
    context.user_data.pop("pending_insertion", None)
    await query.edit_message_text(f"{len(pending_expenses)} expense(s) added successfully!")

async def add_cancel_callback(update: Update, context: CallbackContext):
    """Callback cancelling new transactions"""
    query = update.callback_query

    await query.answer()
    context.user_data.pop("insertion_message_id", None)

    context.user_data.pop("pending_insertion", None)
    await query.edit_message_text("Expense entry cancelled.")
