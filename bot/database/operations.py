import logging
import sqlite3
from typing import List, Tuple
from bot.utils.config import DB_PATH
from bot.llm.expense_parser import Expense

logger = logging.getLogger(__name__)

def sql_add_expense(user_id: int, expense: str, cost: float, currency: str, time: int = None):
    """Add an expense to the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if time:
                cursor.execute(
                    "INSERT INTO Expense (user_id, expense, cost, currency, time) VALUES (?, ?, ?, ?, ?)",
                    (user_id, expense, cost, currency, time)
                )
            else:
                cursor.execute(
                    "INSERT INTO Expense (user_id, expense, cost, currency, time) VALUES (?, ?, ?, ?, strftime('%s', 'now'))",
                    (user_id, expense, cost, currency)
                )
    except sqlite3.Error as e:
        logger.error(f"Error adding expense: {e}")

def sql_add_expenses(user_id: int, expenses: List[Expense]):
    """
    Add multiple expenses to the database in a single transaction.

    :param user_id: User ID.
    :param expenses: List of Expense objects.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Convert Expense objects into tuples for SQL insertion
            expense_data = [
                (user_id, exp.expense, exp.cost, exp.currency, exp.date)
                for exp in expenses  # Now expecting a pure list of Expense objects
            ]

            if expense_data:  # Only insert if there are expenses
                cursor.executemany(
                    "INSERT INTO Expense (user_id, expense, cost, currency, time) VALUES (?, ?, ?, ?, ?)",
                    expense_data
                )
                conn.commit()  # Commit all inserts at once
                logger.info(f"Inserted {len(expenses)} expenses for user {user_id}.")
            else:
                logger.warning(f"No expenses to insert for user {user_id}.")

    except sqlite3.Error as e:
        logger.error(f"Error adding batch expenses: {e}")

def sql_list_expenses(user_id: int, month: str = None) -> List[Tuple]:
    """Fetch all expenses for a user."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if month:
                cursor.execute(
                    """
                    SELECT id, expense, cost, currency, time 
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
                    SELECT id, expense, cost, currency, time 
                    FROM Expense 
                    WHERE user_id = ?
                    ORDER BY time DESC
                    """,
                    (user_id,)
                )
            return cursor.fetchall()
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
