import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from dotenv import load_dotenv
from redis import Redis

from tgbot.middleware import AuthMiddleware
from tgbot.handlers import router

load_dotenv(os.path.join("", ".env"))


# Объект бота
token = os.getenv("BOT_TOKEN")
bot = Bot(
    token=token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
        )
    )

redis_url = os.getenv("REDIS_URL")
storage = RedisStorage.from_url(redis_url)

# REDIS_PORT = int(os.getenv("REDIS_PORT"))
# REDIS_HOST = os.getenv("REDIS_HOST")
# USE_REDIS = os.getenv("USE_REDIS")
#
# redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=5)
# storage = RedisStorage(redis_client) if USE_REDIS else MemoryStorage()

# Диспетчер
dp = Dispatcher(storage=storage)

dp.include_routers(router)
dp.message.middleware(AuthMiddleware())
dp.callback_query.outer_middleware(AuthMiddleware())


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(filename='tgbot/logs/bot.log', level=logging.INFO)
    asyncio.run(main())

