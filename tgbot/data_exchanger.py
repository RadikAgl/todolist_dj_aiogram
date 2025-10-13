import functools
import os
import json
import logging
from datetime import datetime
from typing import Any

import aiohttp
from aiohttp import connector

from dotenv import load_dotenv

load_dotenv(os.path.join("..", ".env"))

TASKS_URL = os.getenv("TASKS_URL")
CATEGORIES_URL = os.getenv("CATEGORIES_URL")
API_TOKENS_URL = os.getenv("API_TOKENS_URL")
ACCESS_TOKEN_REFRESH_URL = os.getenv("ACCESS_TOKEN_REFRESH_URL")
ACCESS_TOKEN_VERIFY_URL = os.getenv("ACCESS_TOKEN_VERIFY_URL")

logger = logging.getLogger(__name__)


# Логирующий асинхронный декоратор
def log_async(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"[{datetime.now()}] Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"[{datetime.now()}] {func.__name__} returned {result}")
            return result
        except Exception as e:
            logger.error(f"[{datetime.now()}] Exception in {func.__name__}: {e}", exc_info=True)
            raise

    return wrapper


# Обёртка для универсального запроса
async def request(
        method: str,
        url: str,
        headers: dict = None,
        params: dict = None,
        json_data: dict = None,
        data: Any = None,
) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    data=data,
            ) as response:
                result = {'status': response.status}
                try:
                    resp_json = await response.json()
                    result['json'] = resp_json
                except aiohttp.ContentTypeError:
                    pass
                return result
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")
        return {'status': 'connection_error', 'error': str(e)}


# ************** БИЗНЕС-ФУНКЦИИ *********************

@log_async
async def list_tasks(headers: dict, user_id: int | None = None, category: str | None = None):
    params = {}
    if user_id is not None:
        params['tg_id'] = user_id
    if category is not None:
        params['category'] = category
    return await request('GET', TASKS_URL, headers=headers, params=params)


@log_async
async def get_task(headers: dict, task_id: str):
    return await request('GET', f"{TASKS_URL}{task_id}/", headers=headers)


@log_async
async def delete_task(headers: dict, task_id: str):
    return await request('DELETE', f"{TASKS_URL}{task_id}/", headers=headers)


@log_async
async def add_task(headers: dict, data: dict[str, Any]):
    return await request('POST', TASKS_URL, headers=headers, json_data={'data': data})


@log_async
async def update_task(headers: dict, data: dict):
    task_id = data.get('task_id') or data.get("id")
    return await request('PATCH', f"{TASKS_URL}{task_id}/", headers=headers, json_data=data)


@log_async
async def get_categories(headers: dict, user_id: int):
    return await request('GET', CATEGORIES_URL, headers=headers, params={'tg_id': user_id})


@log_async
async def get_category(headers: dict, category_id: str):
    return await request('GET', f"{CATEGORIES_URL}{category_id}/", headers=headers)


@log_async
async def add_category(headers: dict, data: dict[str, Any]):
    return await request('POST', CATEGORIES_URL, headers=headers, json_data={'data': data})


@log_async
async def update_category(headers: dict, category_id: str, updated_data: dict):
    return await request('PATCH', f"{CATEGORIES_URL}{category_id}/", headers=headers, json_data=updated_data)


@log_async
async def delete_category(headers: dict, category_id: str):
    return await request('DELETE', f"{CATEGORIES_URL}{category_id}/", headers=headers)


@log_async
async def auth_user(username: str, password: str):
    data = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}
    return await request('POST', API_TOKENS_URL, headers=headers, data=json.dumps(data))


@log_async
async def verify_access_token(access_token: str):
    return await request('POST', ACCESS_TOKEN_VERIFY_URL, json_data={"token": access_token})


@log_async
async def request_new_access_token(refresh_token: str):
    return await request('POST', ACCESS_TOKEN_REFRESH_URL, json_data={"refresh": refresh_token})
