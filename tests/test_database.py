import sqlite3
from datetime import date
from pathlib import Path

import pytest

from bot.database import operations as ops
from bot.models.expense import Expense
from bot.models.user import User

SCHEMA = Path(__file__).resolve().parent.parent / "migrations" / "001_init.sql"


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Point the operations module at a fresh temp database with the real schema."""
    db_path = tmp_path / "test.db"
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA.read_text())
    monkeypatch.setattr(ops, "DB_PATH", str(db_path))
    return db_path


def _expense(desc="Lunch", cost=10.0, currency="usd", day=date(2026, 7, 15)):
    return Expense(description=desc, cost=cost, currency=currency, payment_date=day)


def test_add_and_list_roundtrip(db):
    ops.sql_add_expenses(1, [_expense(), _expense("Coffee", 3.5, "eur")])

    result = ops.sql_list_expenses(1)
    assert len(result) == 2
    assert {e.description for e in result} == {"Lunch", "Coffee"}
    assert all(e.payment_date == date(2026, 7, 15) for e in result)


def test_list_filters_by_year_and_month(db):
    ops.sql_add_expenses(1, [
        _expense("July", day=date(2026, 7, 1)),
        _expense("June", day=date(2026, 6, 1)),
        _expense("LastYear", day=date(2025, 7, 1)),
    ])

    july_2026 = ops.sql_list_expenses(1, year=2026, month=7)
    assert [e.description for e in july_2026] == ["July"]


def test_expenses_are_isolated_per_user(db):
    ops.sql_add_expenses(1, [_expense("Mine")])
    ops.sql_add_expenses(2, [_expense("Theirs")])

    assert [e.description for e in ops.sql_list_expenses(1)] == ["Mine"]
    assert ops.sql_get_expense_by_id(1, user_id=2) is None


def test_delete_expenses(db):
    ops.sql_add_expenses(1, [_expense("A"), _expense("B")])
    ids = [e.id for e in ops.sql_list_expenses(1)]

    ops.sql_delete_expenses(1, ids[:1])
    assert len(ops.sql_list_expenses(1)) == 1


def test_update_description(db):
    ops.sql_add_expenses(1, [_expense("Old")])
    exp_id = ops.sql_list_expenses(1)[0].id

    ops.sql_update_description(1, exp_id, "New")
    assert ops.sql_get_expense_by_id(exp_id, user_id=1).description == "New"


def test_user_created_and_updated(db):
    ops.sql_create_user_if_needed(42, currency="eur")
    assert ops.sql_get_user_by_id(42).currency == "eur"

    ops.sql_update_user(User(42, "gbp"))
    assert ops.sql_get_user_by_id(42).currency == "gbp"


def test_unknown_user_gets_default(db):
    user = ops.sql_get_user_by_id(999)
    assert user.currency == "usd"
