import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def _convert_time_offset(offset: str) -> int:
    """Convert relative time offset (-1d, +2m, etc.) to Unix timestamp."""
    now = datetime.now()

    if not offset:
        return int(now.timestamp())

    try:
        if offset.endswith("d"):
            days = int(offset[:-1])
            target_date = now + timedelta(days=days)

        elif offset.endswith("m"):
            months = int(offset[:-1])
            new_month = now.month + months

            year_adjust = new_month // 12
            target_year = now.year + year_adjust
            target_month = new_month % 12 or 12

            day = min(now.day, (datetime(target_year, target_month, 1) - timedelta(days=1)).day)
            target_date = datetime(target_year, target_month, day, now.hour, now.minute, now.second)

        else:
            return int(now.timestamp())
        
        return int(target_date.timestamp())

    except Exception as e:
        logger.error(f"Time offset conversion failed: {e}")
        return int(now.timestamp())

@dataclass
class Expense:
    """Represents an expense without id."""
    description: str
    cost: float
    currency: str
    time: int

    @staticmethod
    def from_json(data: dict):
        """Parse Expense object from JSON."""
        
        return Expense(
            description=data.get("description", "unknown expense"),
            cost=float(data.get("cost", 5.00)),
            currency=data.get("currency", "usd").lower(),
            time=_convert_time_offset(data.get("time_offset", 0))
        )

@dataclass
class ExpenseWithId(Expense):
    """Represents an expense with id."""
    id: int

    @staticmethod
    def from_json(data: dict):
        """Parses ExpenseWithId object from JSON."""
        return ExpenseWithId(
            id=int(data.get("id", 0)),
            description=data.get("description", "unknown expense"),
            cost=float(data.get("cost", 5.00)),
            currency=data.get("currency", "usd").lower(),
            time=_convert_time_offset(data.get("time_offset", 0))
        )
