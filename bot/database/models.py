import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Expense:
    """Represents an expense without id (for inserting new expenses)."""
    description: str
    cost: float
    currency: str
    date: int

    @staticmethod
    def from_json(data: dict):
        """Parses Expense object from JSON."""
        return Expense(
            description=data.get("description", "unknown expense"),
            cost=float(data.get("cost", 5.00)),
            currency=data.get("currency", "usd").lower(),
            date=int(datetime.now().timestamp())
        )

@dataclass
class ExpenseWithId(Expense):
    """Represents an expense with id (retrieved from the database)."""
    id: int

    @staticmethod
    def from_json(data: dict):
        """Parses ExpenseWithId object from JSON."""
        return ExpenseWithId(
            id=int(data.get("id", 0)),
            description=data.get("description", "unknown expense"),
            cost=float(data.get("cost", 5.00)),
            currency=data.get("currency", "usd").lower(),
            date=int(datetime.now().timestamp())
        )
