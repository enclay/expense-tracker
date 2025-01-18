from typing import Generic, TypeVar
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler

from utils.config import API_TOKEN

from handlers.start import set_commands, start
from handlers.expenses import create_add_handler, total_expenses, list_expenses
from handlers.handle_text import handle_text

def main():

    app = ApplicationBuilder().token(API_TOKEN).post_init(set_commands).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(create_add_handler())
    app.add_handler(CommandHandler("total", total_expenses))
    app.add_handler(CommandHandler("list", list_expenses))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()


if __name__ == "__main__":
    main()
