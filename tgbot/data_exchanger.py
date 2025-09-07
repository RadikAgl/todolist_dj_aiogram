import logging
from datetime import datetime
from typing import Any

import aiohttp
from aiohttp import connector

# await tgbot.send_message(text=text,
#                        chat_id=admin)
TASKS_URL = 'http://web:8000/api/tasks/'
CATEGORIES_URL = 'http://web:8000/api/categories/'
USER_AUTH_URL = 'http://web:8000/api/telegram/auth/'
ACCESS_TOKEN_REFRESH_URL = 'http://web:8000/api/token/refresh/'
ACCESS_TOKEN_VERIFY_URL = 'http://web:8000/api/token/verify/'

logger = logging.getLogger(__name__)


async def list_tasks(headers: dict, user_id: int | None = None, category=None):
    try:
        params = {"user_id": user_id, "category": category} if category else {"user_id": user_id}
        async with (aiohttp.ClientSession() as session):
            async with session.get(
                    TASKS_URL,
                    params=params,
                    headers=headers
            ) as response:
                return {
                    'status': response.status,
                    'json': await response.json()
                }
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")


async def get_task(headers: dict, task_id: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{TASKS_URL}{task_id}/",
                    headers=headers
            ) as response:
                return {
                    'status': response.status,
                    'json': await response.json()
                }
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")


async def delete_task(headers: dict, task_id: str):
    try:
        print(f"{TASKS_URL}{task_id}/")
        async with (aiohttp.ClientSession() as session):
            async with session.delete(
                    f"{TASKS_URL}{task_id}/",
                    headers=headers
            ) as response:
                return {
                    'status': response.status
                }
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")


async def task_is_done(headers: dict, task_id: str):
    try:
        updated_data = {"is_done": True}
        async with (aiohttp.ClientSession() as session):
            async with session.patch(
                    f"{TASKS_URL}{task_id}/",
                    headers=headers,
                    json=updated_data
            ) as response:
                return {
                    'status': response.status
                }
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")


async def update_task(headers: dict, data: dict):
    try:
        task_id = data['task_id']
        print("Updating to view", data)
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                    f"{TASKS_URL}{task_id}/",
                    headers=headers,
                    json=data) as response:
                return {
                    'status': response.status
                }
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")


async def auth_user(user_id: int):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(USER_AUTH_URL, json={'tg_id': user_id}) as response:
                return {
                    'status': response.status,
                    'json': await response.json()
                }
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")


async def get_categories(headers: dict, user_id: int):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    CATEGORIES_URL,
                    headers=headers,
                    json={'tg_id': user_id}
            ) as response:
                return {
                    'status': response.status,
                    'json': await response.json()
                }
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")


async def add_task(headers: dict, data: dict[str, Any]) -> dict[str, int]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    TASKS_URL,
                    headers=headers,
                    json={
                        'data': data
                    }
            ) as response:
                return {
                    'status': response.status
                }
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")


async def verify_access_token(access_token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ACCESS_TOKEN_VERIFY_URL, json={
                "token": access_token
            }) as response:
                return {
                    'status': response.status
                }
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")


async def request_new_access_token(refresh_token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ACCESS_TOKEN_REFRESH_URL, json={
                'refresh': refresh_token
            }) as response:
                return {
                    'status': response.status,
                    'json': await response.json()
                }
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")
