import asyncio
import os
from datetime import timedelta

from aiogram import Bot
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
        send_reminder(task)


@app.task
def send_reminder(task):
    print("Сообщение отправляю")
    asyncio.run(send_telegram_message(task))


async def send_telegram_message(task):
    bot = Bot(token=BOT_TOKEN)
    msg = (f"Напоминаю о:\n"
           f"<b>{task.title}</b>\n"
           f"{task.description}")
    await bot.send_message(chat_id=task.chat_id, text=msg, parse_mode="HTML")
    await bot.session.close()
