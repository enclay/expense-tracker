import logging 
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from bot.database.operations import sql_list_expenses
from bot.utils.currency import get_currency_symbol

logger = logging.getLogger(__name__)

async def list_handle(update: Update, context: CallbackContext):
    """Display expenses for the current month with pagination."""
    current_month = datetime.now().strftime("%Y-%m")
    await _refresh_list(update, context, current_month)

async def _refresh_list(update: Update, context: CallbackContext, period: str):
    """Refresh the expense list based on specified time period."""
    user_id = update.effective_user.id

    expenses = sql_list_expenses(user_id, period)

    try:
        dt = datetime.strptime(period, "%Y-%m")
        month_title = dt.strftime("%B %Y")
    except Exception:
        month_title = period

    message_text = f"*Expenses for {month_title}:*\n"

    if not expenses:
        message_text += "\n\U0000274C *No expenses found.*"
    else:
        for exp in expenses:
            message_text += f"- {exp.description} - {exp.cost}{get_currency_symbol(exp.currency)}\n"

    keyboard = [
        [
            InlineKeyboardButton("← Previous", callback_data=f"list:prev:{period}"),
            InlineKeyboardButton("Next →", callback_data=f"list:next:{period}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

def _add_months(dt: datetime, months: int) -> datetime:
    """Add or subtract months from a date."""
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    
    return dt.replace(year=year, month=month, day=1)

async def list_expense_callback(update: Update, context: CallbackContext):
    """Callback function handling month navigation."""
    query = update.callback_query
    data = query.data

    await query.answer()

    try:
        _, direction, current_month = data.split(":")
        dt = datetime.strptime(current_month, "%Y-%m")
        if direction == "prev":
            new_dt = _add_months(dt, -1)
        elif direction == "next":
            new_dt = _add_months(dt, 1)
        else:
            new_dt = dt
        new_month = new_dt.strftime("%Y-%m")

    except Exception as e:
        logger.error(f"Error parsing callback data '{data}': {e}")
        new_month = datetime.now().strftime("%Y-%m")

    await _refresh_list(update, context, new_month)
