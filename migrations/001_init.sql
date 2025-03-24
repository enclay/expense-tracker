CREATE TABLE IF NOT EXISTS Expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    description TEXT NOT NULL,
	cost REAL NOT NULL,
    currency TEXT NOT NULL,
    payment_date DATE NOT NULL,

	FOREIGN KEY(user_id) REFERENCES User(id)
);

CREATE INDEX idx_expense_user ON Expense(user_id);
CREATE INDEX idx_expense_time ON Expense(payment_date);

CREATE TABLE IF NOT EXISTS User (
	id INTEGER NOT NULL,
	currency TEXT NOT NULL
);
