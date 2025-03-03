def get_currency_symbol(input: str):
    """Get currency symbol for a given currency code."""
    
    currency_symbols = {
        "USD": "$",  # US Dollar
        "EUR": "€",  # Euro
        "GBP": "£",  # British Pound
        "RUB": "₽",  # Russian Ruble
        "JPY": "¥",  # Japanese Yen
        "CNY": "¥",  # Chinese Yuan
        "CHF": "CHF",  # Swiss Franc
    
        "BRL": "R$",  # Brazilian Real
        "ARS": "$",  # Argentine Peso
        "CLP": "$",  # Chilean Peso
        "COP": "$",  # Colombian Peso
        "MXN": "Mex$",  # Mexican Peso
        "PEN": "S/.",  # Peruvian Sol
        "VES": "Bs",  # Venezuelan Bolívar
        "CAD": "C$",  # Canadian Dollar
    
        "SEK": "kr",  # Swedish Krona
        "NOK": "kr",  # Norwegian Krone
        "DKK": "kr",  # Danish Krone
        "PLN": "zł",  # Polish Zloty
        "CZK": "Kč",  # Czech Koruna
        "HUF": "Ft",  # Hungarian Forint
        "RON": "lei",  # Romanian Leu
        "BGN": "лв",  # Bulgarian Lev
        "UAH": "₴",  # Ukrainian Hryvnia
        "GEL": "₾",  # Georgian Lari
    
        "INR": "₹",  # Indian Rupee
        "IDR": "Rp",  # Indonesian Rupiah
        "MYR": "RM",  # Malaysian Ringgit
        "SGD": "S$",  # Singapore Dollar
        "PHP": "₱",  # Philippine Peso
        "THB": "฿",  # Thai Baht
        "KRW": "₩",  # South Korean Won
        "VND": "₫",  # Vietnamese Dong
        "HKD": "HK$",  # Hong Kong Dollar
        "TWD": "NT$",  # New Taiwan Dollar
        "TRY": "₺",  # Turkish Lira
        "ILS": "₪",  # Israeli Shekel
        "SAR": "﷼",  # Saudi Riyal
        "AED": "د.إ",  # UAE Dirham
        "QAR": "﷼",  # Qatari Riyal
        "KWD": "د.ك",  # Kuwaiti Dinar
        "PKR": "₨",  # Pakistani Rupee
        "BDT": "৳",  # Bangladeshi Taka
    
        "ZAR": "R",  # South African Rand
        "EGP": "£",  # Egyptian Pound
        "NGN": "₦",  # Nigerian Naira
        "KES": "KSh",  # Kenyan Shilling
        "TZS": "TSh",  # Tanzanian Shilling
    
        "BTC": "₿",  # Bitcoin
        "ETH": "Ξ",  # Ethereum
        "LTC": "Ł",  # Litecoin
        "BNB": "BNB",  # Binance Coin
        "XRP": "XRP",  # Ripple
        "ADA": "₳",  # Cardano
        "DOT": "DOT",  # Polkadot
        "DOGE": "Ð",  # Dogecoin
        "SOL": "◎",  # Solana
        "AVAX": "AVAX",  # Avalanche
        "XMR": "ɱ",  # Monero
        "BCH": "₿",  # Bitcoin Cash
        "USDT": "₮",  # Tether
        "USDC": "₮",  # USD Coin
        "DAI": "DAI",  # DAI Stablecoin
        "SHIB": "SHIB",  # Shiba Inu Coin
        "MATIC": "MATIC",  # Polygon
        "TRX": "TRX",  # TRON
    }
    return currency_symbols.get(input.upper(), input)
