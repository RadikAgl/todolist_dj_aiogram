FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Зависимости проекта
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Исходники
COPY . .
COPY wait_for_migrations.sh /app/wait_for_migrations.sh
RUN sed -i 's/\r$//' /app/wait_for_migrations.sh && chmod 755 /app/wait_for_migrations.sh

## Нерутовый пользователь
#RUN useradd -m appuser && chown -R appuser:appuser /app
#USER appuser