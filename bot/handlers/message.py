from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from bot.handlers.add import process_expense
from bot.constants import ChatState

async def message_input_handle(update: Update, context: CallbackContext):
    """Handle processing general messages such as new expense entry."""
    chat_state = context.user_data.get("chat_state", None)
    
    if chat_state == ChatState.EXPENSE_INPUT:
        await process_expense(update, context)
    else:
        await update.message.reply_text("Unknown command. Please use */start* to see available commands.", parse_mode=ParseMode.MARKDOWN)
