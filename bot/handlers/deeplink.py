import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.database.operations import sql_delete_expenses, sql_get_expense_by_id, sql_update_description
from bot.utils.currency import get_currency_symbol

async def deeplink_handle(update: Update, context: CallbackContext):
    args = context.args
    await update.message.delete()
    if args and args[0].startswith("expense_"):
        expense_id = args[0].split("_")[1]
        await view_expense(update, context, expense_id)

    else:
        await update.message.reply_text("Welcome to the bot!")

async def view_expense(update: Update, context: CallbackContext, expense_id: int):
    user_id = update.effective_user.id

    exp = sql_get_expense_by_id(expense_id, user_id)

    keyboard = [
        [InlineKeyboardButton("\u270f Change description", callback_data=f"expense_change_description:{expense_id}")],
        [InlineKeyboardButton("\u274c Delete expense", callback_data=f"expense_delete:{expense_id}")],
        [InlineKeyboardButton("Cancel", callback_data=f"expense_view_cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    reply_message = f"[{exp.description}](https://t.me/fintest11_bot?start=expense_{exp.id})\n"
    reply_message += f"cost: {exp.cost}{get_currency_symbol(exp.currency)}\n"
    reply_message += f"date: {exp.payment_date.strftime("%d %b")}"

    await update.message.reply_text(
        reply_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def change_description_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    expense_id = query.data.split(":")[1]
    context.user_data["pending_description_change"] = expense_id

    await context.bot.send_message(
        query.message.chat.id,
        "Please enter new description:"
    )

async def change_description(update: Update, context: CallbackContext):
    message = update.message
    expense_id = context.user_data.pop("pending_description_change")

    sql_update_description(update.effective_user.id, expense_id, message.text)
    await update.message.reply_text(f"Description successfully changed to \"{message.text}\"!")

async def delete_expense_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    expense_id = query.data.split(":")[1]
    sql_delete_expenses(query.message.chat.id, [expense_id])
    await context.bot.send_message(query.message.chat.id, "Description successully deleted!")

async def view_cancel_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await context.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
