import json
import logging
from datetime import datetime 
from openai import OpenAI
from dataclasses import dataclass
from bot.utils.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

@dataclass
class IntentData:
    type: str
    period: str = None

    @staticmethod
    def from_json(json_str: str):
        """Parses JSON and returns an IntentData object."""
        try:
            data = json.loads(json_str)
            return IntentData(type=data["type"], period=data.get("period"))
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse intent JSON: {e}")
            return IntentData(type="unknown")

def parse_intent(user_input: str) -> IntentData:
    """Determines the user's intent (list, add, delete) and time span (all or month)."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
                Identify the user's intent from their message and return the result as a **pure JSON object**.
        
                **Expected JSON format:**
                {{
                    "type": "list" | "add" | "delete",
                    "period": "YYYY-MM" | "YYYY" | "all"  (defaults to current month if missing)
                }}
        
                **Rules:**
                - If a specific month is mentioned, return it as `"YYYY-MM"` (e.g., `"2025-03"`).
                - If a specific year is mentioned, return it as `"YYYY"` (e.g., `"2025"`).
                - If "all time" is mentioned, return `"all"`.
                - If no period is mentioned, default to the **current month** (`"{datetime.now().strftime('%Y-%m')}"`).
        
                **Examples:**
                - "Show my expenses for March 2025" → {{"type": "list", "period": "2025-03"}}
                - "Show all my expenses" → {{"type": "list", "period": "all"}}
                - "Delete all my expenses" → {{"type": "delete", "period": "all"}}
                - "Delete my expenses from 2024" → {{"type": "delete", "period": "2024"}}
                - "I want to add a new expense" → {{"type": "add", "period": "{datetime.now().strftime('%Y-%m')}"}}
        
                **User input:**
                "{user_input}"
        
                **Return only valid JSON. No explanations, no markdown, no ```json formatting.**
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
        return IntentData(type="unknown")
