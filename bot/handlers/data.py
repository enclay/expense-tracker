import json
from datetime import datetime
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import CallbackContext
from bot.database.operations import sql_add_expense, sql_add_expense_with_time, sql_list_expenses

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

        count = 0
        for entry in data:
            if all(key in entry for key in ["expense", "cost", "currency", "time"]):
                sql_add_expense_with_time(
                    user_id,
                    entry["expense"],
                    float(entry["cost"]),
                    int(entry["time"]),
                    entry["currency"]
                )
                count += 1
            else:
                await update.message.reply_text("Invalid JSON format. Some entries are missing required fields.")
                return

        await update.message.reply_text(f"Successfully imported {count} expenses!")

    except json.JSONDecodeError:
        await update.message.reply_text("Invalid JSON format. Please ensure the file contains valid JSON.")


async def export_handle(update: Update, context: CallbackContext):
    """Export user's spendings."""
    
    user_id = update.effective_user.id
    current_month = datetime.now().strftime("%Y-%m")
    expenses = sql_list_expenses(user_id, current_month)
    
    if not expenses:
        await update.message.reply_text("No expenses found for the current month.")
        return

    expense_data = []
    for exp in expenses:
        expense_id, expense, cost, currency, timestamp = exp
        expense_data.append({
            "expense": expense,
            "cost": cost,
            "currency": currency,
            "time": timestamp
        })

    # Convert JSON to BytesIO object (in memory)
    json_data = json.dumps(expense_data, indent=4)
    json_file = BytesIO(json_data.encode("utf-8"))
    json_file.name = "expenses.json"

    await update.message.reply_document(document=InputFile(json_file, filename="expenses.json"))
