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
