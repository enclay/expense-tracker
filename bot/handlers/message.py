from telegram import Update
from telegram.ext import CallbackContext
from bot.handlers.add import add_handle 
from bot.handlers.deeplink import change_description_handle

async def message_input_handle(update: Update, context: CallbackContext):
    """Handle processing general messages such as new expense entry."""

    if "pending_description_change" in context.user_data:
        await change_description_handle(update, context)
    else:
        await add_handle(update, context)
