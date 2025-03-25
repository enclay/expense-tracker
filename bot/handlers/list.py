import logging 
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from bot.database.operations import sql_list_expenses, sql_get_user_by_id
from bot.utils.currency import get_currency_symbol
from bot.utils.exchange_rate import EXCHANGE_RATES

logger = logging.getLogger(__name__)

async def list_handle(update: Update, context: CallbackContext):
    """Display expenses for the current month with pagination."""

    period = context.user_data.get("list_last_month", datetime.now())

    await _refresh_list(update, context, period)


async def _refresh_list(update: Update, context: CallbackContext, period: datetime):
    """Refresh the expense list based on specified time period."""
    user_id = update.effective_user.id

    expenses = sql_list_expenses(user_id, period.year, period.month)

    message_text = f"*Expenses for {period.strftime("%B %Y")}:*"

    if not expenses:
        message_text += "\n\n\U0000274C *No expenses found.*"
    else:
        total = 0.0
        for exp in expenses:
            rate = EXCHANGE_RATES.get(exp.currency, None)
            if rate is None:
                logger.info(f"unrecognized currency {exp.currency}")
            else:
                total += exp.cost * rate

        user = sql_get_user_by_id(user_id)
        factor = EXCHANGE_RATES.get(user.currency)
        total = float(factor) * float(total)

        message_text += f"\n`{get_currency_symbol(user.currency)}{total:.2f}`\n\n"

        for exp in expenses:
            message_text += f"- [{exp.description}](https://t.me/fintest11_bot?start=expense_{exp.id}) - {exp.cost}{get_currency_symbol(exp.currency)} ({exp.payment_date.strftime("%d %b")}) "
            message_text += f"\n"

    callback_date = period.strftime("%Y-%m")

    keyboard = [
        [
            InlineKeyboardButton("← Previous", callback_data=f"list:prev:{callback_date}"),
            InlineKeyboardButton("Next →", callback_data=f"list:next:{callback_date}")
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

def _change_month(dt: datetime, months: int) -> datetime:
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
            new_month = _change_month(dt, -1)
        elif direction == "next":
            new_month = _change_month(dt, 1)

        context.user_data["list_last_month"] = new_month

    except Exception as e:
        logger.error(f"Error parsing callback data '{data}': {e}")
        new_month = datetime.now()

    await _refresh_list(update, context, new_month)
