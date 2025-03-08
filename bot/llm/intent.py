import json
import logging
from openai import OpenAI
from bot.utils.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

def parse_intent(user_input: str) -> str:
    """Determine the user's intent (list, add, delete)"""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
                Identify the user's intent from their message and return the result as a **pure JSON object**.

                **Expected JSON format:**
                {{
                    "type": "list" | "add" | "delete"
                }}

                **Examples:**
                - "Show my expenses for March 2025" → {{"type": "list"}}
                - "Show all my expenses" → {{"type": "list"}}
                - "Delete all my expenses" → {{"type": "delete"}}
                - "Delete my expenses from 2024" → {{"type": "delete"}}
                - "I want to add a new expense" → {{"type": "add"}}
        
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
        return json.loads(gpt_output)["type"]

    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        return "unknown"
