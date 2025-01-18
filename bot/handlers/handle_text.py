import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ContextTypes
from telegram import Update

from services.gpt import call_gpt

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_message = update.message.text
        response = call_gpt(user_message)
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")