import logging
import json
from typing import List
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI
from bot.utils.config import OPENAI_API_KEY
from bot.database.models import Expense

logger = logging.getLogger(__name__)

def parse_expenses(user_input: str) -> List[Expense]:
    """Parse the user input to extract multiple expenses with cost, currency, and always set the current timestamp."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
        Extract one or more expenses from the following message:
        "{user_input}"

        - Each expense should have:
          - "description" (description of expense)
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
            {{"description": "Lunch", "cost": 10.0, "currency": "usd"}},
            {{"description": "Coffee", "cost": 5.0, "currency": "eur"}}
        ]

        **Input:** "Bought groceries for 30 EUR."
        **Output:**
        [
            {{"description": "Groceries", "cost": 30.0, "currency": "eur"}}
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

        try:
            data = json.loads(gpt_output)
            if isinstance(data, list):
                return [Expense.from_json(exp) for exp in data]
            else:
                return [Expense.from_json(data)]
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {gpt_output}")
            return []

    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        return []
