import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("TG_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_KEY")

DATA_FILE = 'expenses.json'