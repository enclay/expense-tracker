import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ContextTypes
from telegram import Update

def call_gpt(message):
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": message}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=50
    )

    return response.choices[0].message.content