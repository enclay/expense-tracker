from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
from bot.database.operations import sql_add_expenses
from bot.llm.expense_parser import parse_expenses
from bot.utils.ratelimit import allow

async def add_handle(update: Update, context: CallbackContext):
    """Handle for insertion of new expenses."""
    message_text = update.message.text

    if len(message_text) > 500:
        await update.message.reply_text("Message too long (max 500 chars).")
        return

    if not allow(update.effective_user.id):
        await update.message.reply_text("Too many requests, wait a minute.")
        return

    expenses = parse_expenses(message_text)
    if not expenses:
        await update.message.reply_text("No valid expenses found.")
        return

    context.user_data["pending_insertion"] = expenses

    message_id  = context.user_data.pop("insertion_message_id", None)
    if message_id:
        await context.bot.edit_message_text(
            text="Adding expenses is cancelled.",
            message_id=message_id,
            chat_id=update.message.chat_id
        )

    confirmation_text = "Please confirm your expenses:\n\n"
    for i, exp in enumerate(expenses, start=1):
        confirmation_text += f"*{i}.* {escape_markdown(exp.description)} - {exp.cost:.2f} "
        confirmation_text += f"{exp.currency.upper()} ({exp.payment_date})\n"

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
    user_id = update.effective_user.id
    query = update.callback_query

    await query.answer()
    context.user_data.pop("insertion_message_id", None)

    pending_expenses = context.user_data.get("pending_insertion")
    if not pending_expenses:
        await query.edit_message_text("No pending expenses found.")
        return
    
    sql_add_expenses(user_id, pending_expenses)
    
    context.user_data.pop("pending_insertion", None)
    await query.edit_message_text(f"{len(pending_expenses)} expense(s) added successfully!")

async def add_cancel_callback(update: Update, context: CallbackContext):
    """Callback cancelling new transactions."""
    query = update.callback_query

    await query.answer()
    context.user_data.pop("insertion_message_id", None)

    context.user_data.pop("pending_insertion", None)
    await query.edit_message_text("Expense entry cancelled.")
