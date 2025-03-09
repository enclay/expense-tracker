import logging
import base64
from io import BytesIO
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ChatAction
from bot.llm.photo_parser import parse_expenses_from_photo

logger = logging.getLogger(__name__)

async def _encode_image(image_bytes: BytesIO) -> str:
    """Encodes image from BytesIO to Base64."""
    return base64.b64encode(image_bytes.getvalue()).decode("utf-8")

async def import_image_handle(update: Update, context: CallbackContext) -> None:
    """Import expenses via image"""
    message = update.message

    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document and message.document.mime_type.startswith("image/"):
        file_id = message.document.file_id
    else:
        await message.reply_text("Please send a valid image.")
        return

    await message.chat.send_action(ChatAction.TYPING)

    file = await context.bot.get_file(file_id)
    data = await file.download_as_bytearray()
    image_bytes = BytesIO(data)

    await file.download_to_memory(image_bytes)
    image_bytes.seek(0)

    base64_image = await _encode_image(image_bytes)
    expenses = parse_expenses_from_photo(base64_image)

    if not expenses:
        await update.message.reply_text("No valid expenses found.")
        return

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

    await message.reply_text(
        confirmation_text, reply_markup=reply_markup, parse_mode="Markdown"
    )
