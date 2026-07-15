import json
from datetime import date
from unittest.mock import MagicMock

from bot.llm import expense_parser
from bot.utils import exchange_rate


def _mock_openai(monkeypatch, content: str):
    """Patch the OpenAI client so no real API call happens."""
    client = MagicMock()
    choice = MagicMock()
    choice.message.content = content
    client.chat.completions.create.return_value = MagicMock(choices=[choice])
    monkeypatch.setattr(expense_parser, "OpenAI", lambda api_key: client)
    return client


class TestParseExpenses:
    def test_parses_list_of_expenses(self, monkeypatch):
        payload = json.dumps([
            {"description": "Lunch", "cost": 10.0, "currency": "usd", "payment_date": "2026-07-14"},
            {"description": "Coffee", "cost": 5.0, "currency": "eur", "payment_date": "2026-07-15"},
        ])
        _mock_openai(monkeypatch, payload)

        expenses = expense_parser.parse_expenses("lunch 10$ yesterday, coffee 5 eur today")

        assert len(expenses) == 2
        assert expenses[0].description == "Lunch"
        assert expenses[1].currency == "eur"
        assert expenses[1].payment_date == date(2026, 7, 15)

    def test_wraps_single_object_into_list(self, monkeypatch):
        payload = json.dumps(
            {"description": "Rent", "cost": 100.0, "currency": "gbp", "payment_date": "2026-08-01"}
        )
        _mock_openai(monkeypatch, payload)

        expenses = expense_parser.parse_expenses("rent 100 gbp next month")

        assert len(expenses) == 1
        assert expenses[0].description == "Rent"

    def test_invalid_json_returns_empty_list(self, monkeypatch):
        _mock_openai(monkeypatch, "sorry, I can't do that")
        assert expense_parser.parse_expenses("nonsense") == []

    def test_api_error_returns_empty_list(self, monkeypatch):
        def boom(api_key):
            raise RuntimeError("API down")

        monkeypatch.setattr(expense_parser, "OpenAI", boom)
        assert expense_parser.parse_expenses("lunch 10$") == []


class TestExchangeRates:
    def test_successful_fetch_lowercases_keys(self, monkeypatch):
        response = MagicMock()
        response.json.return_value = {
            "result": "success",
            "rates": {"USD": 1.0, "EUR": 0.92},
        }
        monkeypatch.setattr(exchange_rate.requests, "get", lambda url, timeout: response)

        rates = exchange_rate.fetch_exchange_rates()
        assert rates == {"usd": 1.0, "eur": 0.92}

    def test_api_failure_returns_fallback(self, monkeypatch):
        def boom(url, timeout):
            raise ConnectionError("no network")

        monkeypatch.setattr(exchange_rate.requests, "get", boom)
        assert exchange_rate.fetch_exchange_rates() == exchange_rate.FALLBACK_RATES

    def test_api_error_result_returns_fallback(self, monkeypatch):
        response = MagicMock()
        response.json.return_value = {"result": "error"}
        monkeypatch.setattr(exchange_rate.requests, "get", lambda url, timeout: response)

        assert exchange_rate.fetch_exchange_rates() == exchange_rate.FALLBACK_RATES
