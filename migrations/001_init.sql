CREATE TABLE IF NOT EXISTS Expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    description TEXT NOT NULL,
	cost REAL NOT NULL,
    currency TEXT NOT NULL,
    time INTEGER NOT NULL
);

CREATE INDEX idx_expense_user ON Expense(user_id);
CREATE INDEX idx_expense_time ON Expense(time);
