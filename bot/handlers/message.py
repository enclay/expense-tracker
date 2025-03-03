from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from bot.handlers.add import add_handle 
from bot.handlers.delete import delete_handle
from bot.llm.intent import parse_intent
from bot.llm.expense_parser import parse_expenses
from bot.database.operations import sql_add_expenses

async def message_input_handle(update: Update, context: CallbackContext):
    """Handle processing general messages such as new expense entry."""

    message_text = update.message.text
    
    intent = parse_intent(message_text)
    if intent.type == "add":
        await add_handle(update, context)
    elif intent.type == "delete":
        await delete_handle(update, context, intent.span)
