import json
import logging
from datetime import datetime
from typing import Any

import aiohttp
from aiohttp import connector


TASKS_URL = 'http://web:8000/api/tasks/'
CATEGORIES_URL = 'http://web:8000/api/categories/'
API_TOKENS_URL = 'http://web:8000/api/token/'
ACCESS_TOKEN_REFRESH_URL = 'http://web:8000/api/token/refresh/'
ACCESS_TOKEN_VERIFY_URL = 'http://web:8000/api/token/verify/'


logger = logging.getLogger(__name__)


async def list_tasks(headers: dict, user_id: int | None = None, category=None):
    try:
        params = {"tg_id": user_id, "category": category} if category else {"tg_id": user_id}
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


async def get_category(headers: dict, category_id: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{CATEGORIES_URL}{category_id}/",
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


async def delete_category(headers: dict, category_id: str):
    try:
        async with (aiohttp.ClientSession() as session):
            async with session.delete(
                    f"{CATEGORIES_URL}{category_id}/",
                    headers=headers
            ) as response:
                return {
                    'status': response.status
                }
    except connector.ClientConnectorError as e:
        logger.error(f"{datetime.now()} {e}")


async def update_category(headers: dict, category_id: str, updated_data):
    try:
        async with (aiohttp.ClientSession() as session):
            async with session.patch(
                    f"{CATEGORIES_URL}{category_id}/",
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


async def auth_user(username: str, password: str):
    try:
        data = {
            "username": username,
            "password": password
        }
        headers = {
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(API_TOKENS_URL,
                                    data=json.dumps(data),
                                    headers=headers) as response:
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
                    params={'tg_id': user_id}
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


async def create_category(headers: dict, data: dict[str, Any]) -> dict[str, int]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    CATEGORIES_URL,
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
