import logging
import sqlite3
from typing import List
from datetime import datetime
from bot.utils.config import DB_PATH
from bot.models.expense import ExpenseWithId, Expense

logger = logging.getLogger(__name__)

def sql_add_expenses(user_id: int, expenses: List[Expense]):
    """Add multiple expenses to the database with a single transaction."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            expense_data = [
                (user_id, exp.description, exp.cost, exp.currency, exp.payment_date)
                for exp in expenses
            ]

            if expense_data:
                cursor.executemany(
                    "INSERT INTO Expense (user_id, description, cost, currency, payment_date) VALUES (?, ?, ?, ?, ?)",
                    expense_data
                )
                conn.commit()
                logger.info(f"Inserted {len(expenses)} expenses for user {user_id}.")
            else:
                logger.warning(f"No expenses to insert for user {user_id}.")

    except sqlite3.Error as e:
        logger.error(f"Error adding batch expenses: {e}")


def sql_list_expenses(user_id: int, period: str = None) -> List[ExpenseWithId]:
    """
    Fetch all expenses for a user.

    - If `period` is `YYYY-MM`, filters by month.
    - If `period` is `YYYY`, filters by year.
    - If `period` is None, fetches all expenses.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            if period:
                if len(period) == 7:  # Format YYYY-MM (month-based filter)
                    cursor.execute(
                        """
                        SELECT id, description, cost, currency, payment_date 
                        FROM Expense 
                        WHERE user_id = ? 
                          AND strftime('%Y-%m', payment_date) = ?
                        ORDER BY payment_date DESC
                        """,
                        (user_id, period)
                    )
                elif len(period) == 4:  # Format YYYY (year-based filter)
                    cursor.execute(
                        """
                        SELECT id, description, cost, currency, payment_date 
                        FROM Expense 
                        WHERE user_id = ? 
                          AND strftime('%Y', payment_date) = ?
                        ORDER BY payment_date DESC
                        """,
                        (user_id, period)
                    )
                else:
                    logger.warning(f"Invalid period format: {period}")
                    return []
            else:
                cursor.execute(
                    """
                    SELECT id, description, cost, currency, payment_date
                    FROM Expense
                    WHERE user_id = ?
                    ORDER BY payment_date DESC
                    """,
                    (user_id,)
                )

            return [
                ExpenseWithId(
                    id=row[0],
                    description=row[1],
                    cost=float(row[2]),
                    currency=row[3],
                    payment_date=datetime.strptime(row[4], "%Y-%m-%d").date()
                )
                for row in cursor.fetchall()
            ]

    except sqlite3.Error as e:
        logger.error(f"Error listing expenses: {e}")
        return []


def sql_delete_expenses(user_id: int, expense_ids: List[int]):
    """Delete multiple expenses by their IDs for a specific user."""
    if not expense_ids:
        logger.warning(f"No expenses provided for deletion for user {user_id}.")
        return

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            placeholders = ", ".join("?" for _ in expense_ids)
            query = f"DELETE FROM Expense WHERE user_id = ? AND id IN ({placeholders})"

            cursor.execute(query, (user_id, *expense_ids))
            conn.commit()

            logger.info(f"Deleted {cursor.rowcount} expenses for user {user_id}.")

    except sqlite3.Error as e:
        logger.error(f"Error deleting expenses for user {user_id}: {e}")
