import logging
import json
from datetime import datetime
from typing import List
from openai import OpenAI
from bot.utils.config import OPENAI_API_KEY, OPENAI_MODEL
from bot.models.expense import Expense

logger = logging.getLogger(__name__)

EXTRACT_PROMPT = f"""
    - Each expense should have:
      - "description" (description of expense)
      - "cost" (as a float)
      - "currency" (ISO 4217: USD, EUR, RUB, GBP)
      - "payment_date" (the exact date of the expense in "YYYY-MM-DD" format):
          - !IMPORTANT Calculate the date RELATIVE to today's date ({datetime.now().strftime("%Y-%m-%d")}).

    - If a month is different and day is not explicitly specified: default to day 1 in date.
    - If no cost is found: default to 5.00.
    - If no currency is found: default to "USD".
    - Do NOT wrap the response in markdown (no ```json format).
    - Return ONLY a valid JSON object, nothing else.

    **Examples:**

    **Input:** "I spent 10 dollars on lunch yesterday and 5 euros on coffee today. (assuming today's date: 13.03.2077)"
    **Output:**
    [
        {{"description": "Lunch", "cost": 10.0, "currency": "usd", "payment_date": "2077-03-12"}},
        {{"description": "Coffee", "cost": 5.0, "currency": "eur", "payment_date": "2077-03-13"}}
    ]

    **Input:** "I will pay 100 GBP for rent in 2 months. (assuming today's date: 13.03.2077)"
    **Output:**
    [
        {{"description": "Rent", "cost": 100.0, "currency": "gbp", "payment_date": "2077-05-13"}}
    ]
"""

def parse_expenses(user_input: str) -> List[Expense]:
    """Extract multiple expenses from the user input."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
        Detect the language of the following message and extract one or more expenses while keeping the original language for descriptions
        and calculating correct date for it:
        {user_input}

        {EXTRACT_PROMPT}
        """

        messages = [
            {"role": "system", "content": "You are a finance assistant extracting expenses from user text."},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=5000,
        )

        gpt_output = response.choices[0].message.content.strip()
        logger.info(gpt_output)

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
