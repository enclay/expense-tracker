FROM python:3.11-slim

WORKDIR /app

ENV POETRY_HOME="/opt/poetry" \
	PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt update && apt install -y curl sqlite3\
	&& curl -sSL https://install.python-poetry.org | python3 - \
	&& rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/

RUN poetry install

COPY . /app/

CMD poetry run migrate && poetry run start
