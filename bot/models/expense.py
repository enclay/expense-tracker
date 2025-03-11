import logging
from datetime import datetime, date
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Expense:
    """Represents an expense without id."""
    description: str
    cost: float
    currency: str
    payment_date: date

    def from_json(data: dict):
        """Parse Expense object from JSON."""
        
        return Expense(
            description=data.get("description", "unknown expense"),
            cost=float(data.get("cost", 5.00)),
            currency=data.get("currency", "usd").lower(),
            payment_date=data.get("payment_date", datetime.now().strftime("%Y-%m-%d"))
        )

    def to_json(self) -> dict:
        """Convert Expense object to JSON-compatible dictionary."""
        return {
            "description": self.description,
            "cost": self.cost,
            "currency": self.currency,
            "payment_date": self.payment_date
        }
@dataclass
class ExpenseWithId(Expense):
    """Represents an expense with id."""
    id: int

    def from_json(data: dict):
        """Parses ExpenseWithId object from JSON."""

        return ExpenseWithId(
            id=int(data.get("id", 0)),
            description=data.get("description", "unknown expense"),
            cost=float(data.get("cost", 5.00)),
            currency=data.get("currency", "usd").lower(),
            payment_date=data.get("payment_date", datetime.now().strftime("%Y-%m-%d"))
        )

    def to_json(self) -> dict:
        """Convert ExpenseWithId object to JSON-compatible dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "cost": self.cost,
            "currency": self.currency,
            "payment_date": self.payment_date
        }
