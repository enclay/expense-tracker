import json
import logging
from openai import OpenAI
from dataclasses import dataclass
from bot.utils.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

@dataclass
class IntentData:
    type: str
    span: str = None

    @staticmethod
    def from_json(json_str: str):
        """Parses JSON and returns an IntentData object."""
        try:
            data = json.loads(json_str)
            return IntentData(type=data["type"], span=data.get("span"))
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse intent JSON: {e}")
            return IntentData(type="unknown")

def parse_intent(user_input: str) -> IntentData:
    """Determines the user's intent (list, add, delete) and time span (all or month)."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
        You are an expense tracking bot. Identify the user's intent from their message.

        Expected JSON output:
        - "type": One of "list", "add", or "delete".
        - "span": Only for "list" or "delete", either "month" (default) or "all" if explicitly mentioned.

        Examples:
        - "Show my expenses" → {{"type": "list", "span": "month"}}
        - "Delete all my expenses" → {{"type": "delete", "span": "all"}}
        - "I want to add a new expense" → {{"type": "add"}}

        User input:
        "{user_input}"
        
        Return only valid JSON. No additional text or explanations.
        """

        messages = [
            {"role": "system", "content": "You are an expense tracking assistant extracting user intent."},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=50,
        )

        gpt_output = response.choices[0].message.content.strip()

        return IntentData.from_json(gpt_output)

    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        return IntentData(type="unknown")  # Default fallback
