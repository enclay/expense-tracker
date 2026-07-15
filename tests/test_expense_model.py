from datetime import date, datetime

import pytest

from bot.models.expense import Expense


def test_parses_valid_expense():
    exp = Expense.from_json({
        "description": "Lunch",
        "cost": 10.5,
        "currency": "EUR",
        "payment_date": "2026-07-15",
    })
    assert exp.description == "Lunch"
    assert exp.cost == 10.5
    assert exp.currency == "eur"
    assert exp.payment_date == date(2026, 7, 15)


def test_defaults_when_fields_missing():
    exp = Expense.from_json({})
    assert exp.description == "unknown expense"
    assert exp.cost == 5.00
    assert exp.currency == "usd"
    assert exp.payment_date == datetime.now().date()


def test_unknown_currency_falls_back_to_usd():
    exp = Expense.from_json({"currency": "THB"})
    assert exp.currency == "usd"


def test_currency_is_normalized_to_lowercase():
    exp = Expense.from_json({"currency": "RUB"})
    assert exp.currency == "rub"


def test_description_is_truncated_to_100_chars():
    exp = Expense.from_json({"description": "x" * 500})
    assert len(exp.description) == 100


@pytest.mark.parametrize("bad_cost", [0, -1, 1_000_001, float("inf"), float("nan")])
def test_invalid_cost_raises(bad_cost):
    with pytest.raises(ValueError):
        Expense.from_json({"cost": bad_cost})


def test_cost_boundaries_are_accepted():
    assert Expense.from_json({"cost": 0.01}).cost == 0.01
    assert Expense.from_json({"cost": 1_000_000}).cost == 1_000_000


def test_non_numeric_cost_raises():
    with pytest.raises(ValueError):
        Expense.from_json({"cost": "free"})


def test_malformed_date_raises():
    with pytest.raises(ValueError):
        Expense.from_json({"payment_date": "15.07.2026"})
