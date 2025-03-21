import requests

def fetch_exchange_rates():
    """Fetch current exchange rates for fiat currencies (USD as base)."""
    
    fiat_api_url = "https://open.er-api.com/v6/latest/USD"
    
    try:
        response = requests.get(fiat_api_url)
        data = response.json()
        
        if data.get("result") != "success":
            raise ValueError("Error fetching exchange rates")

        fiat_rates = {k.lower(): v for k, v in data["rates"].items()}

        return fiat_rates

    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        return {}

EXCHANGE_RATES = fetch_exchange_rates()
