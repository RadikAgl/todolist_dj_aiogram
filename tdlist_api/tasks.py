import os
from datetime import timedelta

import requests
from django.utils import timezone
from dotenv import load_dotenv

from tdlist_api.models import Task
from todolist_dj_aiogram.celery import app

load_dotenv(os.path.join(".", ".env"))
BOT_TOKEN = os.getenv("BOT_TOKEN")


@app.task
def get_hot_tasks():

    now = timezone.now()
    now_after = now + timedelta(seconds=20)
    now_before = now - timedelta(seconds=20)

    tasks = Task.objects.filter(is_done=False).filter(deadline__range=(now_before, now_after))
    
    for task in tasks:
        send_telegram_message(task)


@app.task
def print_all_tasks(tasks):
    for task in tasks:
        print(task.deadline)
    print(f"All tasks: {tasks}")


@app.task
def send_telegram_message(task):
    chat_id = task.chat_id
    print(f"CHAT_ID {chat_id}")
    msg = (f"Напоминаю о:\n"
           f"<b>{task.title}</b>"
           f"{task.description}")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        print(f"Сообщение отправлено: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка: {e}")
