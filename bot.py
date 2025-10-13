import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from dotenv import load_dotenv

from tgbot.middleware import AuthMiddleware
from tgbot.handlers import router, main_dialog, create_task_dialog, create_category_dialog, categories_dialog, \
    tasks_dialog

load_dotenv(os.path.join("", ".env"))


# Объект бота
token = os.getenv("BOT_TOKEN")
bot = Bot(
    token=token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
        )
    )

REDIS_URL = os.getenv("REDIS_URL")


storage = RedisStorage.from_url(REDIS_URL, key_builder=DefaultKeyBuilder(with_destiny=True))


# Диспетчер
dp = Dispatcher(storage=storage)

dp.include_routers(router)
dp.include_router(main_dialog)
dp.include_router(create_task_dialog)
dp.include_router(create_category_dialog)
dp.include_router(categories_dialog)
dp.include_router(tasks_dialog)
dp.message.middleware(AuthMiddleware())
dp.callback_query.outer_middleware(AuthMiddleware())
setup_dialogs(dp)


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    handler = RotatingFileHandler("tgbot/logs/bot.log", maxBytes=1024 * 1024, backupCount=3, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    asyncio.run(main())

