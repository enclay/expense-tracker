import logging
import sqlite3
from typing import List
from bot.utils.config import DB_PATH
from bot.database.models import ExpenseWithId, Expense

logger = logging.getLogger(__name__)

def sql_add_expenses(user_id: int, expenses: List[Expense]):
    """Add multiple expenses to the database in a single transaction."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            expense_data = [
                (user_id, exp.description, exp.cost, exp.currency, exp.time)
                for exp in expenses
            ]

            if expense_data:
                cursor.executemany(
                    "INSERT INTO Expense (user_id, description, cost, currency, time) VALUES (?, ?, ?, ?, ?)",
                    expense_data
                )
                conn.commit()
                logger.info(f"Inserted {len(expenses)} expenses for user {user_id}.")
            else:
                logger.warning(f"No expenses to insert for user {user_id}.")

    except sqlite3.Error as e:
        logger.error(f"Error adding batch expenses: {e}")

def sql_list_expenses(user_id: int, month: str = None) -> List[ExpenseWithId]:
    """Fetch all expenses for a user."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if month:
                cursor.execute(
                    """
                    SELECT id, description, cost, currency, time 
                    FROM Expense 
                    WHERE user_id = ? 
                      AND strftime('%Y-%m', datetime(time, 'unixepoch')) = ?
                    ORDER BY time DESC
                    """,
                    (user_id, month)
                )
            else:
                cursor.execute(
                    """
                    SELECT id, description, cost, currency, time
                    FROM Expense
                    WHERE user_id = ?
                    ORDER BY time DESC
                    """,
                    (user_id,)
                )
            return [
                ExpenseWithId(
                    id=row[0],
                    description=row[1],
                    cost=row[2],
                    currency=row[3],
                    time=row[4]
                ) for row in cursor.fetchall()
            ]
    except sqlite3.Error as e:
        logger.error(f"Error listing expenses: {e}")
        return []


def sql_delete_expense(expense_id: int):
    """Delete an expense by its ID."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Expense WHERE id = ?", (expense_id,))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error deleting expense: {e}")
