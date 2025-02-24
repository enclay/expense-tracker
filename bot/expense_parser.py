from openai import OpenAI
from bot.utils.config import OPENAI_API_KEY
import logging
import re

logger = logging.getLogger(__name__)

def parse_expenses(user_input: str):
    """Parse the user input to extract the expense and cost."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
        Extract the expense description and cost from the following message:
        "{user_input}"
        
        - If a cost is found, return it as a float.
        - If no cost is found, return 5.00 as default.
        - If the cost includes currency symbols ($, €, etc.), remove them.
        - Return a JSON response like this:
        
        {{"expense": "Lunch at Subway", "cost": 12.50}}
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

        match = re.search(r'{"expense": "(.*?)", "cost": (\d+\.\d+)}', gpt_output)
        if match:
            expense = match.group(1)
            cost = float(match.group(2))
            return expense, cost

    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")

    return user_input, 0
