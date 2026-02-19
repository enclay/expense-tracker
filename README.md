# AI-Powered Expense Tracker Bot

A sophisticated Telegram bot that simplifies personal finance tracking using Natural Language Processing. Instead of filling out tedious forms, just tell the bot what you spent, and let the AI handle the structured data.

## Table of Contents
* [Features](#features)
* [Tech Stack](#tech-stack)
* [Getting Started](#getting-started)
* [Usage](#usage)
* [Project Structure](#project-structure)

---

## Features

* **Natural Language Ingestion:** Log expenses by typing naturally (e.g., *"Spent 15€ on a Pizza today and 5$ for a bus yesterday"*).
* **LLM Parsing Engine:** Uses OpenAI to automatically extract:
    * Description (normalized to nominative form)
    * Cost
    * Currency (ISO 4217 detection)
    * Relative Dates (handles "yesterday", "last Friday", etc.)
* **Interactive Expense Management:**
    * **Monthly Summaries:** Visual lists with total spending calculated in your preferred currency.
    * **Deep Linking:** Every expense in the list is a link that opens a management menu.
    * **CRUD Operations:** Edit descriptions or delete entries directly via Telegram callback buttons.
* **Data Portability:** Full JSON Export/Import functionality to keep your data under your control.
* **Multi-Currency:** Support for USD, EUR, RUB, and GBP with internal exchange rate normalization.

---

## Tech Stack

* **Language:** Python 3.11+
* **Framework:** `python-telegram-bot`
* **Intelligence:** OpenAI API (`gpt-4o` / `gpt-3.5-turbo`)
* **Database:** SQLite (Relational storage)
* **Dependency Management:** Poetry
* **DevOps:** Docker & Docker Compose

---

## Getting Started

### Prerequisites

* A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
* An OpenAI API Key
* Docker (Optional, for containerized deployment)

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/enclay/enclay-expense-tracker.git
   cd enclay-expense-tracker
   ```
2. **Install Dependencies:**
   ```bash
   poetry install
   ```
3. **Run Migrations:**
   ```bash
   poetry run migrate
   ```
4. **Start the Bot:**
   ```bash
   poetry run start
   ```

### Running with Docker

The easiest way to deploy:
```bash
docker-compose up --build
```

## Usage
Commands
* `/start` - Initialize the bot and handle deep links.
* `/list` - View monthly spending with navigation buttons.
* `/currency` - Set your default display currency (USD, EUR, RUB).
* `/export` - Download your spending history as a JSON file.

### How to add expenses

Simply send a text message. The bot will parse it and ask for confirmation:

**User:** "8 Euro for a Döner and 2.50 for water"

**Bot:** ✅ Please confirm your expenses:
  1. **Döner** - 8.00 EUR (2026-02-19)
  2. **Water** - 2.50 EUR (2026-02-19)

## Project Structure
```Plaintext
├── bot/
│   ├── database/    # SQLite logic and CRUD operations
│   ├── handlers/    # Telegram command and callback handlers
│   ├── llm/         # OpenAI integration and prompt engineering
│   ├── models/      # Dataclasses for Expense and User objects
│   └── utils/       # Currency symbols, exchange rates, and config
├── migrations/      # SQL schema initialization
├── scripts/         # Automation scripts
└── docker-compose.yml
```
