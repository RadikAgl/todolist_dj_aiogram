import logging
import operator
import re
from datetime import datetime, date
from typing import Any

from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from aiogram_dialog import DialogManager, StartMode, Dialog, Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Start, Row, Back, Next, Cancel, ScrollingGroup, Multiselect, Calendar, \
    CalendarConfig, Select
from aiogram_dialog.widgets.text import Const, Format, Case

from tgbot.data_exchanger import (list_tasks, auth_user, get_categories, add_task, delete_task, get_task, update_task,
                                  delete_category, update_category, create_category, get_category)
from tgbot.utils import FAILURE_MESSAGE
from tgbot.states import MainDialogSG, CreateTaskSG, CategoriesSG, CreateCategorySG, TasksSG

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("ad_start"))
async def start(message: types.Message, dialog_manager: DialogManager):
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(MainDialogSG.main, mode=StartMode.RESET_STACK)


async def start_categories_dialog(callback: CallbackQuery, button: Button,
                                  manager: DialogManager):
    await manager.start(CategoriesSG.main, data={"key": "value"})


async def start_create_task_dialog(callback: CallbackQuery, button: Button,
                                   manager: DialogManager):
    await manager.start(CreateTaskSG.title, data={"is_editing": False, "task_id": None})


async def start_tasks_dialog(callback: CallbackQuery, button: Button,
                             manager: DialogManager):
    await manager.start(TasksSG.list, data={"category_id": None})


async def start_create_category_dialog(callback: CallbackQuery, button: Button,
                                       manager: DialogManager):
    await manager.start(CreateCategorySG.name, data={"category_id": None})


main_dialog = Dialog(
    Window(
        Const("Меню"),
        Button(Const("Список задач"), id="list_tasks", on_click=start_tasks_dialog),
        Button(Const("Создать задачу"), id="create_task", on_click=start_create_task_dialog),
        Start(Const("Категории"), id="list_categories", state=CategoriesSG.main),
        state=MainDialogSG.main,
    ),
)


async def get_task_title(
        message: Message,
        message_input: MessageInput,
        manager: DialogManager,
):
    manager.dialog_data["title"] = message.document
    await message.answer(f"{message.document}")
    await manager.done()


async def get_categories_data(dialog_manager: DialogManager, **kwargs):
    buttons = []

    headers = dialog_manager.middleware_data.get('headers')
    user_id = dialog_manager.event.from_user.id

    response = await get_categories(headers, user_id)
    if response and response.get('status') == 200:
        categories = response.get('json')
        res = True if categories else False
        for category in categories:
            buttons.append((category["name"], category["id"]))
        dialog_manager.dialog_data["categories"] = buttons
    else:
        res = False
    return {"categories": buttons, "count": len(buttons), "is_success": res}


scrolling_grp_multiselect_categories = ScrollingGroup(
    Multiselect(
        Format("✓ {item[0]}"),
        Format("{item[0]}"),
        id="categories",
        item_id_getter=operator.itemgetter(1),
        items="categories",
    ),
    id="chose_category",
    width=2,
    height=2,
)


def get_category_names(cats, manager):
    categories = manager.dialog_data.get("categories")
    categories = filter(lambda x: x[1] in cats, categories)
    categories = list(map(lambda x: x[0], categories))
    return ", ".join(categories)


async def get_dialog_data(dialog_manager: DialogManager, **kwargs):
    categories = dialog_manager.find("categories").get_checked()
    return {
        "title": dialog_manager.find("title").get_value(),
        "description": dialog_manager.find("description").get_value(),
        "categories": categories,
        "categories_name": get_category_names(categories, dialog_manager),
        "date": dialog_manager.dialog_data.get("date"),
        "time": dialog_manager.find("time").get_value(),
        "category_qnt": True if len(dialog_manager.find("categories").get_checked()) else False
    }


async def on_date_selected(callback: CallbackQuery, widget,
                           manager: DialogManager, selected_date: date):
    manager.dialog_data["date"] = str(selected_date)  # YYYY-mm-dd
    await manager.next()


def is_actual_time(task_date, time_str):
    full_time_str = task_date + " " + time_str
    full_time = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M")
    if full_time > datetime.now():
        return True


async def on_success_handler(message: Message, widget, dialog_manager: DialogManager, *args, **kwargs):
    time_str = message.text
    task_date = dialog_manager.dialog_data.get('date')
    if is_actual_time(task_date, time_str):
        await dialog_manager.next()
    else:
        await message.answer("Время не должно быть прошедшим")


def time_type_factory(time_str):
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    if bool(re.match(pattern, time_str)):
        return time_str
    raise ValueError("Неверный формат времени")


async def time_selecting_error(
        message: Message,
        dialog_: Any,
        manager: DialogManager,
        error_: ValueError
):
    await message.answer("Время должно быть в формате HH:MM, например, 06:30.")


async def on_task_confirmed(callback: CallbackQuery, button: Button,
                            manager: DialogManager):
    data = await get_dialog_data(manager)
    is_editing = manager.start_data.get("is_editing")
    headers = manager.middleware_data.get('headers')
    data["tg_id"] = manager.event.from_user.id
    data["chat_id"] = manager.event.message.chat.id
    data["date"] += f" {data['time']}"
    if is_editing:
        data['task_id'] = manager.start_data.get('task_id')
        response = await update_task(headers, data)
    else:
        response = await add_task(headers, data)
    try:
        if response["status"] == 200:
            msg = "Задача обновлена!"
        elif response["status"] == 201:
            msg = "Задача создана!"
        else:
            msg = FAILURE_MESSAGE
    except Exception as e:
        logger.error(f"datetime.now() - функция: {on_task_confirmed.__name__} - {e}")
        msg = FAILURE_MESSAGE
    await callback.answer(msg, show_alert=True)
    await manager.done()


create_task_dialog = Dialog(
    Window(
        Const("Введите название задачи"),
        TextInput(id="title", on_success=Next()),
        Row(
            Cancel(Const("Отмена")),
        ),
        state=CreateTaskSG.title,
    ),
    Window(
        Const("Введите описание задачи"),
        TextInput(id="description", on_success=Next()),
        Row(
            Back(Const("Назад")),
            Cancel(Const("Отмена")),
        ),
        state=CreateTaskSG.description,
    ),
    Window(

        Case(
            {
                True: Const("Выберите категории задачи\n"),
                False: Const("Категорий пока нет, добавьте новую")
            },
            selector="is_success",
        ),
        scrolling_grp_multiselect_categories,

        Next(Const("Готово")),
        Button(Const("Без категории"), id="without_category_btn", on_click=Next()),
        Start(Const("Новая категория"), id="start_create_category_dialog", state=CreateCategorySG.name),
        Row(
            Back(Const("Назад")),
            Cancel(Const("Отмена")),
        ),
        state=CreateTaskSG.category,
        getter=get_categories_data
    ),
    Window(
        Const("Когда нужно напомнить?"),
        Calendar(
            id='calendar',
            config=CalendarConfig(min_date=datetime.today().date()),
            on_click=on_date_selected
        ),
        Row(
            Back(Const("Назад")),
            Cancel(Const("Отмена")),
        ),
        state=CreateTaskSG.date
    ),
    Window(
        Const("Введите точное время в формате HH:MM"),
        TextInput(
            id="time",
            on_error=time_selecting_error,
            on_success=on_success_handler,
            type_factory=time_type_factory,
        ),
        Row(
            Back(Const("Назад")),
            Cancel(Const("Отмена")),
        ),
        state=CreateTaskSG.time
    ),
    Window(
        Const("Подтвердите атрибуты задачи"),
        Format("Название: {title}"),
        Format("Описание: {description}"),
        Case(
            {
                True: Format("Категории: {categories_name}"),
                False: Const("Категории: Без категории")
            },
            selector="category_qnt"
        ),
        Format("Напомнить: {date} {time}"),
        Button(Const("Подтверждаю"), id="task_confirmed", on_click=on_task_confirmed),
        Row(
            Back(Const("Назад")),
            Cancel(Const("Отмена")),
        ),
        state=CreateTaskSG.confirmation,
        getter=get_dialog_data
    ),
)


async def add_new_category(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: str,
):
    category_id = manager.start_data.get('category_id')
    headers = manager.middleware_data.get('headers')
    data = {
        "name": text,
        "tg_id": manager.event.from_user.id
    }

    if category_id:
        response = await update_category(headers, category_id, data)
    else:
        response = await create_category(headers, data)
    try:
        if response["status"] == 200:
            msg = "Категория обновлена!"
        elif response["status"] == 201:
            msg = "Категория создана!"
        else:
            msg = FAILURE_MESSAGE
    except Exception as e:
        logger.error(f"datetime.now() - функция: {on_task_confirmed.__name__} - {e}")
        msg = FAILURE_MESSAGE
    await message.answer(msg, show_alert=True)
    await manager.done()


create_category_dialog = Dialog(
    Window(
        Const("Введите название категории"),
        TextInput(id="title", on_success=add_new_category),
        Row(
            Cancel(Const("Отмена")),
        ),
        state=CreateCategorySG.name,
    ),
)


async def on_selecting_category(callback: CallbackQuery, button: Button,
                                manager: DialogManager, item_id: str):
    manager.dialog_data["category_id"] = item_id
    await manager.next()


async def get_category_data(dialog_manager: DialogManager, **kwargs):
    category_id = dialog_manager.dialog_data.get('category_id')
    headers = dialog_manager.middleware_data.get('headers')
    response = await get_category(headers, category_id)
    if response.get('status') == 200:
        category = response.get('json')
        res = True if category else False
        return {
            "name": category["name"],
            "is_success": res
        }

    else:
        await dialog_manager.event.answer(FAILURE_MESSAGE, show_alert=True)
        await dialog_manager.done()


async def on_deleting_category(callback: CallbackQuery, button: Button,
                               manager: DialogManager):
    category_id = manager.dialog_data.get('category_id')
    headers = manager.middleware_data.get('headers')
    response = await delete_category(headers, category_id)
    if response.get('status') == 204:
        await callback.answer("Категория удалена", show_alert=True)
    else:
        await callback.answer(
            FAILURE_MESSAGE,
            show_alert=True
        )
    await manager.done()


async def on_changing_category(callback: CallbackQuery, button: Button,
                               manager: DialogManager):
    await manager.start(CreateCategorySG.name, data={"category_id": manager.dialog_data.get('category_id')})


async def on_category_tasks_list(callback: CallbackQuery, button: Button,
                                 manager: DialogManager):
    await manager.start(TasksSG.list, data={"category_id": manager.dialog_data.get('category_id')})


select_widget_category = Select(
    Format("{item[0]}"),
    id="s_categories",
    item_id_getter=operator.itemgetter(1),
    items="categories",
    on_click=on_selecting_category,
)
#
scrolling_select_category = ScrollingGroup(
    select_widget_category,
    id="scrolling_select_group_category",
    width=1,
    height=3,
)

categories_dialog = Dialog(
    Window(
        Case(
            {
                True: Const("Текущие категории"),
                False: Const("Категорий пока нет")
            },
            selector="is_success"),
        scrolling_select_category,
        Button(Const("Добавить новую категорию"), id="category_lists_add", on_click=start_create_category_dialog),
        Cancel(Const("Назад")),

        getter=get_categories_data,
        state=CategoriesSG.main,
    ),
    Window(
        Format("<b>{name}</b>"),
        Button(Const("Удалить"), id="delete_category", on_click=on_deleting_category),
        Button(Const("Изменить название"), id="change_category", on_click=on_changing_category),
        Button(Const("Задачи категории"), id="category_tasks", on_click=on_category_tasks_list),
        Row(
            Cancel(Const("Вернуться в главное меню")),
            Back(Const("Назад")),
        ),
        parse_mode=ParseMode.HTML,
        getter=get_category_data,
        state=CategoriesSG.detail

    ),
)


async def on_selecting_task(callback: CallbackQuery, button: Button,
                            manager: DialogManager, item_id: str):
    manager.dialog_data["task_id"] = item_id
    await manager.next()


async def get_tasks_data(dialog_manager: DialogManager, **kwargs):
    buttons = []
    category_id = dialog_manager.start_data.get('category_id')
    headers = dialog_manager.middleware_data.get('headers')
    user_id = dialog_manager.event.from_user.id

    response = await list_tasks(headers, user_id, category_id)
    if response.get('status') == 200:
        tasks = response.get('json')
        res = True if tasks else False
        for task in tasks:
            buttons.append((task["title"], task["id"]))
        return {"tasks": buttons, "count": len(buttons), "is_success": res}
    else:
        await dialog_manager.event.answer(FAILURE_MESSAGE, show_alert=True)
        await dialog_manager.done()




select_widget = Select(
    Format("{item[0]}"),  # How to display the button text
    id="s_tasks",
    item_id_getter=operator.itemgetter(1),  # How to get the unique ID for each item
    items="tasks",  # Key in your dialog data where the list of items is stored
    on_click=on_selecting_task,  # Optional: a handler for when a button is clicked
)
#
scrolling_select = ScrollingGroup(
    select_widget,
    id="scrolling_select_group",
    width=1,  # Number of buttons per row
    height=3,  # Number of rows per page
)


async def on_deleting_task(callback: CallbackQuery, button: Button,
                           manager: DialogManager):
    task_id = manager.dialog_data.get('task_id')
    headers = manager.middleware_data.get('headers')
    response = await delete_task(headers, task_id)
    if response.get('status') == 204:
        await callback.answer("Задача удалена", show_alert=True)
    else:
        await callback.answer(
            "Что-то пошло не так, уже решаем проблему. Попробуйте еще раз чуть позже.",
            show_alert=True
        )
    await manager.done()


async def on_changing_task(callback: CallbackQuery, button: Button,
                           manager: DialogManager):
    task_id = manager.dialog_data.get('task_id')
    await manager.start(CreateTaskSG.title, data={"is_editing": True, "task_id": task_id})


async def on_task_done(callback: CallbackQuery, button: Button,
                       manager: DialogManager):
    task_id = manager.dialog_data.get('task_id')
    data = {"task_id": task_id, "is_done": True}
    headers = manager.middleware_data.get('headers')
    response = await update_task(headers, data)

    if response.get('status') == 200:
        await callback.answer("Задача помечена выполненной", show_alert=True)
    else:
        await callback.answer(
            "Что-то пошло не так, уже решаем проблему. Попробуйте еще раз чуть позже.",
            show_alert=True
        )
    await manager.done()


async def get_task_data(dialog_manager: DialogManager, **kwargs):
    task_id = dialog_manager.dialog_data.get('task_id')
    headers = dialog_manager.middleware_data.get('headers')
    response = await get_task(headers, task_id)
    if response.get('status') == 200:
        task = response.get('json')
        res = True if task else False
        return {
            "title": task["title"],
            "description": task["description"],
            "categories": ", ".join([item["name"] for item in task["categories"]]) if task["categories"] else "Без "
                                                                                                              "категории",
            "deadline": task["deadline"],
            "created_at": task["created_at"],
            "is_success": res
        }

    else:
        await dialog_manager.event.answer(FAILURE_MESSAGE, show_alert=True)
        await dialog_manager.done()


tasks_dialog = Dialog(
    Window(

        Case(
            {
                True: Const("Актуальные задачи"),
                False: Const("Актуальных задач пока нет")
            },
            selector="is_success"),
        scrolling_select,
        Button(Const("Добавить задачу"), id="list_create_task", on_click=start_create_task_dialog),
        Cancel(Const("Назад")),

        getter=get_tasks_data,
        state=TasksSG.list,
    ),
    Window(
        Case(
            {
                True: Format(
                    "Название: {title}\n"
                    "Описание: {description}\n"
                    "Категории: {categories}\n"
                    "Создано: {created_at}\n"
                    "Напомнить: {deadline}\n"
                ),
                False: Const("Проблемы на сервере, уже решаем проблему. Попробуйте еще раз чуть позже.")
            },
            selector="is_success"
        ),
        Button(Const("Удалить"), id="delete_task", on_click=on_deleting_task),
        Button(Const("Редактировать"), id="change_task", on_click=on_changing_task),
        Button(Const("Задача выполнена"), id="task_done", on_click=on_task_done),
        Row(
            Cancel(Const("Вернуться в главное меню")),
            Back(Const("Назад")),
        ),
        state=TasksSG.detail,
        getter=get_task_data

    ),
)


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено"
    )


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, dialog_manager: DialogManager):
    await state.clear()
    await state.set_state()
    await message.answer(
            "Приветствую"
        )
    await dialog_manager.start(MainDialogSG.main, mode=StartMode.RESET_STACK)
