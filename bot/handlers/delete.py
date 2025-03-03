from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.database.operations import sql_list_expenses, sql_delete_expense

from datetime import datetime
import logging 

logger = logging.getLogger(__name__)

async def delete_handle(update: Update, context: CallbackContext):
    """Display all expenses for the current month as separate inline buttons for deletion."""
    user_id = update.effective_user.id
    current_month = datetime.now().strftime("%Y-%m")
    expenses = sql_list_expenses(user_id, current_month)
    
    if not expenses:
        await update.message.reply_text("No expenses found for the current month.")
        return

    keyboard = []
    for exp in expenses:
        button_text = f"{exp.description} - ${exp.cost}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"delete:{exp.id}")])

    keyboard.append([InlineKeyboardButton("Cancel", callback_data="delete_cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select an expense to delete:", reply_markup=reply_markup)

async def delete_cancel_callback(update: Update, context: CallbackContext):
    """ Delete the message and inform the user that the deletion is cancelled."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Deletion is cancelled by user.")

async def delete_expense_callback(update: Update, context: CallbackContext):
    """Handle the deletion when a user clicks an inline button."""
    query = update.callback_query
    await query.answer()
    
    try:
        _, expense_id_str = query.data.split(":")
        expense_id = int(expense_id_str)
        sql_delete_expense(expense_id)
        await query.edit_message_text("Expense deleted successfully.")
    except Exception as e:
        logger.error(f"Error deleting expense: {e}")
        await query.edit_message_text("Failed to delete expense. Please try again.")
