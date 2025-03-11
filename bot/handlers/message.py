from telegram import Update
from telegram.ext import CallbackContext
from bot.handlers.add import add_handle 
from bot.handlers.delete import delete_handle
from bot.handlers.edit import edit_insertion_handle, edit_deletion_handle 
from bot.llm.intent import parse_intent

async def message_input_handle(update: Update, context: CallbackContext):
    """Handle processing general messages such as new expense entry."""

    message_text = update.message.text
        
    if "insertion_message_id" in context.user_data:
        await edit_insertion_handle(update, context)

    elif "deletion_message_id" in context.user_data:
        await edit_deletion_handle(update, context)
    else:
        intent = parse_intent(message_text)
        if intent == "add":
            await add_handle(update, context)
        elif intent == "delete":
            await delete_handle(update, context)
        else:
            await unknown_handle(update, context)

async def unknown_handle(update: Update, callback: CallbackContext):
    """Handle processing unknown commands."""
    message = (
            "*Oops!* I didn’t quite catch that. Could you please clarify what you’d like to do? \U0001F60A\n\n"
            "*Here’s what I can help you with:*\n"
            "• *Add an expense* (e.g., `add 5$ coffee`)\n"
            "• *Delete an expense* (e.g., `delete last`)\n"
            "• *List all expenses* (use `/list`)\n"
            "• *Export your data* (use `/export`)\n\n"
            "Just let me know what you need!"
        )
    await update.message.reply_text(message, parse_mode='Markdown')
