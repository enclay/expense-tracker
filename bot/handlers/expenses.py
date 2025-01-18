from datetime import datetime

from telegram import Update
from services.gpt import call_gpt
from utils.db import load_data, save_data
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler

ASK_INPUT = 1

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "What would you like to add?",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_INPUT

def add_item(item, price, category):
    now = datetime.now()
    month_key = now.strftime('%Y-%m')

    data = load_data()
    if month_key not in data:
        data[month_key] = []

    data[month_key].append({
        "item": item,
        "price": price,
        "category": category,
        "date": now.strftime('%Y-%m-%d %H:%M:%S'),
    })
    save_data(data)


async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_input = update.message.text

    prompt = (
        f"Extract structured data from the following input. "
        f"Each item should be in the format: item, price, category. "
        f"The category should be inferred based on common sense or left as 'other' if it's unclear. "
        f"Do not reject the input unless it is completely invalid. Assume items and prices if possible.\n\n"
        f"Input: {user_input}\n\n"
        f"Output should be a semicolon-separated list like this: "
        f"coffee,2,food;cookies,6,food;present,5,other.\n\n"
        f"Guidelines for inference:\n"
        f"- If the price is mentioned, extract it.\n"
        f"- If no specific category is clear, default to 'other'.\n"
        f"- Use common sense to guess the category (e.g., food, drink, electronics, clothing).\n"
        f"- Avoid rejecting inputs unless absolutely necessary.\n\n"
        f"If extraction is completely impossible (e.g., input contains no relevant information), respond with 'error' and explain why."
    )

    response = call_gpt(prompt)

    if response == "error":
        await update.message.reply_text("I'm sorry, I couldn't extract the data.")
        return ConversationHandler.END

    for entry in response.split(";"):
        parts = entry.split(",")
        if len(parts) != 3:
            raise ValueError("Invalid response format from GPT.")
        
        item = parts[0].strip()
        price = parts[1].strip()
        category = parts[2].strip()
        
        add_item(item, price, category)
        await update.message.reply_text(f"✅ Added: {price},{item},{category}")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation canceled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def create_add_handler():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add_command)],
        states={
            ASK_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    return conv_handler


async def total_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()
    now = datetime.now()
    month_key = now.strftime('%Y-%m')

    if month_key in data:
        total = sum(item['price'] for item in data[month_key])
        await update.message.reply_text(f"📊 Total expenses this month: €{total:.2f}")
    else:
        await update.message.reply_text("No expenses recorded this month.")


async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = load_data()
    now = datetime.now()
    month_key = now.strftime('%Y-%m')

    if month_key in data:
        response = "Expenses:\n"
        for item in data[month_key]:
            response += f"• €{item['price']} - {item['item']} ({item['date']})\n"
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("No expenses recorded for this month.")