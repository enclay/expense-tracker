from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.database.operations import sql_list_expenses, sql_delete_expenses
from bot.llm.deletion_parser import parse_deletion

from datetime import datetime
import logging 

logger = logging.getLogger(__name__)

async def delete_handle(update: Update, context: CallbackContext):
    """Handle deleting expenses."""
    user_id = update.effective_user.id
    message_text = update.message.text

    expenses = sql_list_expenses(user_id)

    expenses_to_delete = parse_deletion(expenses, message_text)
    context.user_data["pending_deletion"] = expenses_to_delete

    if not expenses_to_delete:
        await update.message.reply_text("No matching expenses found for deletion.")
        return

    confirmation_text = "**Please confirm the deletion of these expenses:**\n\n"
    for i, expense in enumerate(expenses_to_delete, 1):
        formatted_time = datetime.fromtimestamp(int(expense.time)).strftime("%d/%m/%Y, %H:%M")
        confirmation_text += f"*{i}.* {expense.description} - {expense.cost:.2f} {expense.currency.upper()} ({formatted_time})\n"

    keyboard = [
        [InlineKeyboardButton("\u2705 Confirm", callback_data="confirm_deletion")],
        [InlineKeyboardButton("\u274C Cancel", callback_data="cancel_deletion")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        confirmation_text, reply_markup=reply_markup, parse_mode="Markdown"
    )

async def delete_confirm_callback(update: Update, context: CallbackContext):
    """Callback: Delete the pending expenses after user confirms."""
    query = update.callback_query
    await query.answer()

    pending_deletion = context.user_data.get("pending_deletion")
    if not pending_deletion:
        await query.edit_message_text("No pending expenses found for deletion.")
        return

    user_id = update.effective_user.id

    expense_ids = [expense.id for expense in pending_deletion]

    sql_delete_expenses(user_id, expense_ids)

    context.user_data.pop("pending_deletion", None)

    await query.edit_message_text(f"{len(expense_ids)} expense(s) successfully deleted!")


async def delete_cancel_callback(update: Update, context: CallbackContext):
    """Callback: Cancel deleting the pending expenses."""
    query = update.callback_query
    await query.answer()

    context.user_data.pop("pending_deletion", None)
    await query.edit_message_text("Expense deletion cancelled.")
