from openai import OpenAI
from bot.utils.config import OPENAI_API_KEY
import logging
import json
from dataclasses import dataclass
from typing import List
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Expense:
    """Represents an expense without an ID (for inserting new expenses)."""
    expense: str
    cost: float
    currency: str
    date: int  # Unix timestamp (always set to now)

    @staticmethod
    def from_json(data: dict):
        """Parses JSON and returns an Expense object, always setting the current timestamp."""
        return Expense(
            expense=data.get("expense", "Unknown Expense"),
            cost=float(data.get("cost", 5.00)),  # Default cost is 5.00
            currency=data.get("currency", "usd").lower(),  # Default currency is USD
            date=int(datetime.now().timestamp())  # Always use the current timestamp
        )

@dataclass
class ExpenseWithId(Expense):
    """Represents an expense with an ID (retrieved from the database)."""
    id: int

    @staticmethod
    def from_json(data: dict):
        """Parses JSON and returns an ExpenseWithId object."""
        return ExpenseWithId(
            id=int(data.get("id", 0)),  # Default to 0 if not provided
            expense=data.get("expense", "Unknown Expense"),
            cost=float(data.get("cost", 5.00)),
            currency=data.get("currency", "usd").lower(),
            date=int(datetime.now().timestamp())  # Always use the current timestamp
        )

def parse_expenses(user_input: str) -> List[Expense]:
    """Parse the user input to extract multiple expenses with cost, currency, and always set the current timestamp."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
        Extract one or more expenses from the following message:
        "{user_input}"

        - Each expense should have:
          - "expense" (description)
          - "cost" (as a float)
          - "currency" (ISO 4217: USD, EUR, RUB, GBP).

        - If no cost is found, default to 5.00.
        - If no currency is found, default to "USD".
        - Do NOT wrap the response in markdown (no ```json format).
        - Return ONLY a valid JSON object, nothing else.

        **Examples:**

        **Input:** "I spent 10 dollars on lunch and 5 euros on coffee."
        **Output:**
        [
            {{"expense": "Lunch", "cost": 10.0, "currency": "usd"}},
            {{"expense": "Coffee", "cost": 5.0, "currency": "eur"}}
        ]

        **Input:** "Bought groceries for 30 EUR."
        **Output:**
        [
            {{"expense": "Groceries", "cost": 30.0, "currency": "eur"}}
        ]
        """

        messages = [
            {"role": "system", "content": "You are a finance assistant extracting expenses from user text."},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=100,
        )

        gpt_output = response.choices[0].message.content.strip()

        # Parse JSON directly into a list of Expense objects
        try:
            data = json.loads(gpt_output)
            if isinstance(data, list):
                return [Expense.from_json(exp) for exp in data]
            else:
                return [Expense.from_json(data)]  # Handle single expense case
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {gpt_output}")
            return []

    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        return []  # Return empty list on failure
