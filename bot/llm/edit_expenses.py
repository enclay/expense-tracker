import json
import logging
from dataclasses import asdict
from typing import List
from openai import OpenAI
from bot.models.expense import ExpenseWithId
from bot.utils.config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)

def edit_expenses(user_input: str, expenses: List[ExpenseWithId]) -> List[ExpenseWithId]:
    """Use ChatGPT to apply modifications from user input to a list of expenses."""

    client = OpenAI(api_key=OPENAI_API_KEY)

    if not expenses:
        return []

    expenses_json: str = [asdict(exp) for exp in expenses]

    prompt = (
        "You are an assistant that modifies a list of expenses based on user instructions. "
        "The expenses are provided as a JSON list. Each expense has 'id', 'description', 'cost', "
        "'currency', and 'time' fields. Based on the user's input, return a modified JSON list "
        "with the same structure, applying the changes. If an instruction doesn't match any expense, "
        "keep that expense unchanged. Do not add new expenses or remove existing ones unless explicitly told to.\n\n"
        f"Current expenses: {json.dumps(expenses_json, indent=2)}\n"
        f"User instruction: {user_input}\n\n"
        "Return the modified list in JSON format."
        "Do NOT wrap the response in markdown (no ```json format)."
        "Return ONLY a valid JSON object, nothing else."
    )

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Modify the expenses as instructed."}
            ],
            max_tokens=1000
        )

        modified_json = response.choices[0].message.content.strip()
        
        print(f"out: {modified_json}")
        modified_expenses_data = json.loads(modified_json)

        modified_expenses = [
            ExpenseWithId.from_json(expense_data, time_offset=False)
            for expense_data in modified_expenses_data
        ]

        return modified_expenses

    except Exception as e:
        print(f"Error editing expenses with ChatGPT: {e}")
        return expenses
