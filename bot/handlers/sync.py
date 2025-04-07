import json
from datetime import datetime, date
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import CallbackContext
from bot.database.operations import sql_list_expenses, sql_add_expenses
from bot.models.expense import Expense


async def export_handle(update: Update, context: CallbackContext):
    """Export user's spendings."""
    user_id = update.effective_user.id

    expenses = sql_list_expenses(user_id)
    if not expenses:
        await update.message.reply_text("No expenses found.")
        return

    expense_data = []
    for exp in expenses:
        expense_data.append({
            "description": exp.description,
            "cost": exp.cost,
            "currency": exp.currency,
            "payment_date": exp.payment_date.strftime("%Y-%m-%d")
        })

    json_data = json.dumps(expense_data, indent=4)
    json_file = BytesIO(json_data.encode("utf-8"))

    await update.message.reply_document(
        document=InputFile(json_file, filename="expenses.json")
    )

async def import_handle(update: Update, context: CallbackContext):
    """Import user's spendings from a JSON file."""
    user_id = update.effective_user.id

    if not update.message.document:
        await update.message.reply_text("No valid file found.")
        return

    file = await update.message.document.get_file()
    file_content = await file.download_as_bytearray()
    json_data = file_content.decode("utf-8")

    try:
        data = json.loads(json_data)
        if not isinstance(data, list):
            raise ValueError("The root element must be a list.")

        expenses = []
        required_keys = ["description", "cost", "currency", "payment_date"]

        for entry in data:
            if not all(key in entry for key in required_keys):
                raise ValueError("Some entries are missing required fields.")

            expenses.append(Expense(
                description=entry["description"],
                cost=float(entry["cost"]),
                currency=entry["currency"],
                payment_date=date.fromisoformat(entry["payment_date"])
            ))

        if expenses:
            sql_add_expenses(user_id, expenses)
            await update.message.reply_text(f"Successfully imported {len(expenses)} expenses!")
        else:
            await update.message.reply_text("No valid expenses found in the JSON file.")

    except json.JSONDecodeError:
        await update.message.reply_text("Invalid JSON format. Please ensure the file contains valid JSON.")
