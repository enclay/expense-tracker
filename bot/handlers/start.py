# Start command
from telegram import BotCommand, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to Finance Tracker Bot! 📊\n"
        "Use /add <amount> <description> to track an expense.\n"
        "Example: /add 15.50 Lunch\n"
        "/total - Show this month's expenses\n"
        "/list - List all expenses"
    )

async def set_commands(application):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("add", "Add an expense"),
        BotCommand("total", "Show total spending"),
        BotCommand("list", "List all expenses this month")
    ]
    await application.bot.set_my_commands(commands)