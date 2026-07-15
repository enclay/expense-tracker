from bot.utils import ratelimit
from bot.utils.currency import get_currency_symbol


class TestRateLimit:
    def setup_method(self):
        ratelimit._hits.clear()

    def test_allows_up_to_limit(self):
        assert all(ratelimit.allow(1, limit=5, window=60) for _ in range(5))

    def test_blocks_over_limit(self):
        for _ in range(5):
            ratelimit.allow(1, limit=5, window=60)
        assert ratelimit.allow(1, limit=5, window=60) is False

    def test_users_are_independent(self):
        for _ in range(5):
            ratelimit.allow(1, limit=5, window=60)
        assert ratelimit.allow(2, limit=5, window=60) is True

    def test_window_expiry_frees_slots(self, monkeypatch):
        now = 1000.0
        monkeypatch.setattr(ratelimit.time, "time", lambda: now)
        for _ in range(5):
            ratelimit.allow(1, limit=5, window=60)
        assert ratelimit.allow(1, limit=5, window=60) is False

        monkeypatch.setattr(ratelimit.time, "time", lambda: now + 61)
        assert ratelimit.allow(1, limit=5, window=60) is True


class TestCurrencySymbol:
    def test_known_currency(self):
        assert get_currency_symbol("EUR") == "€"

    def test_case_insensitive(self):
        assert get_currency_symbol("eur") == "€"

    def test_unknown_currency_returned_as_is(self):
        assert get_currency_symbol("XYZ") == "XYZ"
