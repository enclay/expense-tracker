import json
import logging
from openai import OpenAI
from datetime import datetime
from bot.utils.config import OPENAI_API_KEY, OPENAI_MODEL 
from bot.models.expense import ExpenseWithId

logger = logging.getLogger(__name__)

def _convert_timestamp_to_str(ts: int):
    """Converts Unix timestamp to human-readable string."""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def filter_expenses_for_delete(expenses: list[ExpenseWithId], user_input: str) -> list[ExpenseWithId]:
    """
    Determines which expenses should be deleted based on user input.
    Returns a list of ExpenseWithId objects.
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        expenses_json = [
            {
                "id": exp.id,
                "description": exp.description,
                "cost": exp.cost,
                "currency": exp.currency,
                "time": _convert_timestamp_to_str(exp.time)
            }
            for exp in expenses
        ]

        prompt = f"""
        You are an expense tracking assistant. The user wants to delete certain expenses.
        
        Given this user request/requireement to be matched:
        "{user_input}"

        And the following expenses:
        {json.dumps(expenses_json, indent=2)}

        Identify which expenses match the user's request and should be deleted.
        
        Expected JSON output:
        - Return a **list of expense IDs** to be deleted. Example:
          [1, 3, 7]
        
        - If no expenses match the request, return an empty list: []
        
        Do NOT wrap the response in markdown (no ```json format). Return ONLY valid JSON.
        """

        messages = [
            {"role": "system", "content": "You are an intelligent assistant that helps users delete specific expenses."},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=1000,
        )

        gpt_output = response.choices[0].message.content.strip()

        try:
            data = json.loads(gpt_output)
            if isinstance(data, list) and all(isinstance(i, int) for i in data):
                return [exp for exp in expenses if exp.id in data]
            else:
                logger.error(f"Unexpected response format: {gpt_output}")
                return []
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {gpt_output}")
            return []

    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        return []
