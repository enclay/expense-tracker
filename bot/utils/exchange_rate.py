import logging
import requests

logger = logging.getLogger(__name__)

# approximate rates used if the API is unreachable (USD base)
FALLBACK_RATES = {"usd": 1.0, "eur": 0.92, "rub": 90.0, "gbp": 0.79}

def fetch_exchange_rates():
    """Fetch current exchange rates for fiat currencies (USD as base)."""
    fiat_api_url = "https://open.er-api.com/v6/latest/USD"

    try:
        response = requests.get(fiat_api_url, timeout=5)
        data = response.json()

        if data.get("result") != "success":
            raise ValueError("Error fetching exchange rates")

        return {k.lower(): v for k, v in data["rates"].items()}

    except Exception as e:
        logger.warning(f"Using fallback exchange rates: {e}")
        return FALLBACK_RATES

EXCHANGE_RATES = fetch_exchange_rates()
