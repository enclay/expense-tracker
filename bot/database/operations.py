import logging
import sqlite3
from typing import List, Tuple
from bot.utils.config import DB_PATH

logger = logging.getLogger(__name__)

def sql_add_expense(user_id: int, expense: str, cost: float, curr: str = "usd"):
    """Add an expense to the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Expense (user_id, expense, cost, currency, time) VALUES (?, ?, ?, ?, strftime('%s', 'now'))",
                (user_id, expense, cost, curr)
            )
            conn.commit()

    except sqlite3.Error as e:
        logger.error(f"Error adding expense: {e}")

def sql_add_expense_with_time(user_id: int, expense: str, cost: float, time: int, curr: str = "usd"):
    """Add an expense to the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Expense (user_id, expense, cost, currency, time) VALUES (?, ?, ?, ?, ?)",
                (user_id, expense, cost, time, curr)
            )
            conn.commit()

    except sqlite3.Error as e:
        logger.error(f"Error adding expense: {e}")

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
