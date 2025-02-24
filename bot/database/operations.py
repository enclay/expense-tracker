import sqlite3
from typing import List, Tuple
from bot.utils.config import DB_PATH

def sql_add_expense(user_id: int, expense: str, cost: float):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO Expense (user_id, expense, cost, currency, time) VALUES (?, ?, ?, ?, strftime('%s', 'now'))",
        (user_id, expense, cost, 0)
    )

    conn.commit()
    conn.close()


#def sql_list_expenses(user_id: int) -> List[Tuple]:
#    conn = sqlite3.connect(DB_PATH)
#    cursor = conn.cursor()
#
#    cursor.execute(
#        "SELECT id, expense, cost, currency, time FROM Expense WHERE user_id = ? ORDER BY time DESC",
#        (user_id,)
#    )
#
#    expenses = cursor.fetchall()
#    conn.close()
#    return expenses

def sql_list_expenses(user_id: int, month: str = None) -> List[Tuple]:
    conn = sqlite3.connect(DB_PATH)
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
    expenses = cursor.fetchall()
    conn.close()
    return expenses
