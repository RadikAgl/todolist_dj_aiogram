from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def show_or_create_task_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Текущие задачи")
    kb.button(text="Категории задач")
    kb.button(text="Создать задачу")
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True)


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def get_keyboard_with_categories(categories: list[dict]) -> types.InlineKeyboardMarkup:
    buttons = []
    for category in categories:
        buttons.append(types.InlineKeyboardButton(text=category['name'], callback_data=f"cat_{category['id']}"))
    buttons.append(types.InlineKeyboardButton(text='Без категории', callback_data='num_nocat'))
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons, ])
    return keyboard


def get_keyboard_tasks_menu(task_id: str) -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text='Редактировать', callback_data=f'task_edit_{task_id}'),
         types.InlineKeyboardButton(text='Задача выполнена', callback_data=f'task_done_{task_id}'),
         types.InlineKeyboardButton(text='Удалить', callback_data=f'task_delete_{task_id}')],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_button_without_category() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text='Без категории', callback_data=f'without_category')],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_categories_kb(cats: list) -> types.InlineKeyboardMarkup:
    buttons = []
    for cat in cats:
        buttons.append([types.InlineKeyboardButton(text=f"{cat['name']}", callback_data=f'cats_{cat["id"]}')])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_task_editing_kb():
    buttons = [
        [types.InlineKeyboardButton(text='Название', callback_data=f'task_edit_name'),
         types.InlineKeyboardButton(text='Описание', callback_data=f'task_edit_description'),
         types.InlineKeyboardButton(text='Время напоминания', callback_data=f'task_edit_deadline'),
         types.InlineKeyboardButton(text='Категории', callback_data=f'task_edit_categories'),
         types.InlineKeyboardButton(text='Готово', callback_data=f'task_edit_finish')],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
