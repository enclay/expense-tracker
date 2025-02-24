from datetime import datetime

def add_months(dt: datetime, months: int) -> datetime:
    """Helper to add or subtract months from a date."""
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    # day=1 so that filtering is consistent
    return dt.replace(year=year, month=month, day=1)
