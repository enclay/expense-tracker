import logging
import json
from typing import List
from openai import OpenAI
from bot.utils.config import OPENAI_API_KEY, OPENAI_MODEL
from bot.models.expense import Expense

logger = logging.getLogger(__name__)

def parse_expenses(user_input: str) -> List[Expense]:
    """Extract multiple expenses from the user input."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
        Detect the language of the following message and extract one or more expenses while keeping the original language for descriptions:
        "{user_input}"

        - Each expense should have:
          - "description" (description of expense)
          - "cost" (as a float)
          - "currency" (ISO 4217: USD, EUR, RUB, GBP)
          - "time_offset" (relative time offset as **-Xd / +Xm format**, where X is a number):
            - "-1d" for "yesterday"
            - "-7d" for "one week ago"
            - "+2m" for "in 2 months"
            - Default to "0d" (today) if no time is specified.

        - If no cost is found, default to 5.00.
        - If no currency is found, default to "USD".
        - Do NOT wrap the response in markdown (no ```json format).
        - Return ONLY a valid JSON object, nothing else.

        **Examples:**

        **Input:** "I spent 10 dollars on lunch yesterday and 5 euros on coffee today."
        **Output:**
        [
            {{"description": "Lunch", "cost": 10.0, "currency": "usd", "time_offset": "-1d"}},
            {{"description": "Coffee", "cost": 5.0, "currency": "eur", "time_offset": "0d"}}
        ]

        **Input:** "I will pay 100 GBP for rent in 2 months."
        **Output:**
        [
            {{"description": "Rent", "cost": 100.0, "currency": "gbp", "time_offset": "+2m"}}
        ]
        """

        messages = [
            {"role": "system", "content": "You are a finance assistant extracting expenses from user text."},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=500,
        )

        gpt_output = response.choices[0].message.content.strip()
        logger.info(gpt_output)

        try:
            data = json.loads(gpt_output)
            if isinstance(data, list):
                return [Expense.from_json(exp, time_offset=True) for exp in data]
            else:
                return [Expense.from_json(data, time_offset=True)]
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {gpt_output}")
            return []

    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        return []
