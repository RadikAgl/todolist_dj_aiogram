import re

from aiogram.fsm.state import StatesGroup, State

from tgbot.data_exchanger import request_new_access_token
from tgbot.keyboards import get_keyboard_tasks_menu

API_URL = 'http://localhost:8000/api'


class TaskStates(StatesGroup):
    entering_task_name = State()
    entering_task_description = State()
    setting_deadline_date = State()
    setting_deadline_time = State()
    choosing_task_category = State()
    creating_category = State()
    editing_task = State()


class AuthStates(StatesGroup):
    waiting_for_auth = State()


# Класс для хранения токенов пользователя
class UserTokens:

    def __init__(self):
        self.tokens = {}  # {user_id: {"access": "...", "refresh": "..."}}

    def set_tokens(self, user_id, access_token, refresh_token):
        self.tokens[user_id] = {
            "access": access_token,
            "refresh": refresh_token
        }

    def get_access_token(self, user_id):
        if user_id in self.tokens:
            return self.tokens[user_id]["access"]
        return None

    def get_refresh_token(self, user_id):
        if user_id in self.tokens:
            return self.tokens[user_id]["refresh"]
        return None

    async def refresh_access_token(self, user_id):
        refresh_token = self.get_refresh_token(user_id)
        if not refresh_token:
            return False

        response = await request_new_access_token(refresh_token)
        if response["status"] == 200:
            data = response["json"]
            self.tokens[user_id]["access"] = data["access"]
            if "refresh" in data:
                self.tokens[user_id]["refresh"] = data["refresh"]
            return True
        return False

    async def refresh_tokens(self, user_id):
        refresh_token = self.get_refresh_token(user_id)
        if not refresh_token:
            return False

        response = await request_new_access_token(refresh_token)
        if response["status"] == 200:
            data = response["json"]
            self.tokens[user_id]["access"] = data["access"]
            if "refresh" in data:
                self.tokens[user_id]["refresh"] = data["refresh"]
            return True
        return False


user_tokens = UserTokens()


def is_valid_time(time_str):
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))


def extract_category_names(cat_dict):
    if cat_dict:
        cats = [elem["name"] for elem in cat_dict]
        return ', '.join(cats)
    return "Нет категорий"


def make_task_msgs(tasks):
    return [(task_describe_text(task), get_keyboard_tasks_menu(task['id'])) for task in list(tasks)]


def task_describe_text(task):
    return (f"<b>{task['title']}</b>\n"
            f"{task['description']}\n"
            f"Напомнить: {task['deadline']}\n"
            f"Категории: {extract_category_names(task['categories'])}")
