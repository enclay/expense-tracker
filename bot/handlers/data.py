import json
from datetime import datetime
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import CallbackContext
from bot.database.operations import sql_list_expenses, sql_add_expenses
from bot.database.models import Expense

async def import_handle(update: Update, context: CallbackContext):
    """Import user's spendings from a JSON file."""

    user_id = update.effective_user.id

    if not update.message.document:
        await update.message.reply_text("Please send a valid JSON file.")
        return

    file = await update.message.document.get_file()
    
    file_content = await file.download_as_bytearray()
    json_data = file_content.decode("utf-8")

    try:
        data = json.loads(json_data)

        if not isinstance(data, list):
            raise ValueError("Invalid JSON format. The root element must be a list.")

        expenses = []
        for entry in data:
            if all(key in entry for key in ["description", "cost", "currency", "time"]):
                expenses.append(Expense(
                    description=entry["description"],
                    cost=float(entry["cost"]),
                    currency=entry["currency"],
                    time=int(entry["time"])
                ))
            else:
                await update.message.reply_text("Invalid JSON format. Some entries are missing required fields.")
                return

        if expenses:
            sql_add_expenses(user_id, expenses)
            await update.message.reply_text(f"Successfully imported {len(expenses)} expenses!")
        else:
            await update.message.reply_text("No valid expenses found in the JSON file.")

    except json.JSONDecodeError:
        await update.message.reply_text("Invalid JSON format. Please ensure the file contains valid JSON.")


async def export_handle(update: Update, context: CallbackContext):
    """Export user's spendings."""
    
    user_id = update.effective_user.id

    expenses = sql_list_expenses(user_id)
    
    if not expenses:
        await update.message.reply_text("No expenses found for the current month.")
        return

    expense_data = []
    for exp in expenses:
        expense_data.append({
            "description": exp.description,
            "cost": exp.cost,
            "currency": exp.currency,
            "time": exp.time
        })

    json_data = json.dumps(expense_data, indent=4)
    json_file = BytesIO(json_data.encode("utf-8"))
    json_file.name = "expenses.json"

    await update.message.reply_document(document=InputFile(json_file, filename="expenses.json"))
