import logging 
from telegram import Update
from telegram.ext import CallbackContext
from bot.llm.edit_expenses import edit_expenses
from bot.handlers.add import present_expenses_for_confirmation

logger = logging.getLogger(__name__)

async def edit_insertion_handle(update: Update, context: CallbackContext):
    """Edit parsed expenses"""

    expenses = context.user_data.get("pending_insertion")
    new_expenses = edit_expenses(update.message.text, expenses)

    await present_expenses_for_confirmation(update, context, new_expenses)


async def edit_deletion_handle(update: Update, context: CallbackContext):
    pass
