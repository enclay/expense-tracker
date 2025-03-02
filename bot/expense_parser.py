from openai import OpenAI
from bot.utils.config import OPENAI_API_KEY
import logging
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ExpenseData:
    """Class to store parsed expense data."""
    expense: str
    cost: float
    currency: str

    @staticmethod
    def from_json(json_str: str):
        """Parses JSON string and returns an ExpenseData object."""
        try:
            data = json.loads(json_str)
            return ExpenseData(
                expense=data.get("expense", "Unknown Expense"),
                cost=float(data.get("cost", 5.00)),  # Default cost is 5.00
                currency=data.get("currency", "usd").lower()  # Default currency is USD
            )
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {json_str}")
            return ExpenseData("Unknown Expense", 5.00, "usd")  # Return default values on failure

def parse_expenses(user_input: str) -> ExpenseData:
    """Parse the user input to extract the expense, cost, and optionally currency."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
        Extract the expense description, cost, and optionally the currency from the following message:
        "{user_input}"
        
        - If a cost is found, return it as a float.
        - If no cost is found, return 5.00 as the default.
        - If a currency name is provided (dollars, euros, roubles, pounds), convert it to the correct ISO 4217 code (USD, EUR, RUB, GBP).
        - If no currency is found, default to "USD".
        - Do NOT wrap the response in markdown (no ```json format).
        - Return ONLY a valid JSON object, nothing else.
        - Example output:

        {{"expense": "Lunch at Subway", "cost": 12.50, "currency": "usd"}}
        """

        messages = [
            {"role": "system", "content": "You are a finance assistant extracting expenses from user text."},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=50,
        )

        gpt_output = response.choices[0].message.content

        return ExpenseData.from_json(gpt_output)

    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")

    return ExpenseData("Unknown Expense", 5.00, "usd")  # Default return
