import logging
import operator

from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Row, Cancel, Button, Select, ScrollingGroup, Back
from aiogram_dialog.widgets.text import Const, Format, Case

from tgbot.data_exchanger import update_category, add_category, get_category, delete_category, get_categories
from tgbot.states import CreateCategorySG, TasksSG, CategoriesSG
from tgbot.utils import FAILURE_MESSAGE

logger = logging.getLogger(__name__)


async def start_categories_dialog(callback: CallbackQuery, button: Button,
                                  manager: DialogManager):
    await manager.start(CategoriesSG.main)


async def add_new_category(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: str,
):
    category_id = None
    try:
        category_id = manager.start_data.get('category_id')
    except AttributeError:
        pass
    headers = manager.middleware_data.get('headers')
    data = {
        "name": text,
        "tg_id": manager.event.from_user.id
    }

    if category_id:
        response = await update_category(headers, category_id, data)
    else:
        response = await add_category(headers, data)
    try:
        if response["status"] == 200:
            msg = "🎉 Категория обновлена!"
        elif response["status"] == 201:
            msg = "🎉 Категория создана!"
        else:
            msg = FAILURE_MESSAGE
    except Exception as e:
        logger.error(f"datetime.now() - функция: {add_new_category.__name__} - {e}")
        msg = FAILURE_MESSAGE
    await message.answer(msg, show_alert=True)
    await manager.done()


create_category_dialog = Dialog(
    Window(
        Const("Введите название категории"),
        TextInput(id="title", on_success=add_new_category),
        Row(
            Cancel(Const("❌ Отмена")),
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
        await callback.answer("🗑️ Категория удалена", show_alert=True)
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
scrolling_select_category = ScrollingGroup(
    select_widget_category,
    id="scrolling_select_group_category",
    width=1,
    height=3,
)


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


async def start_create_category_dialog(callback: CallbackQuery, button: Button,
                                       manager: DialogManager):
    await manager.start(CreateCategorySG.name, data={"category_id": None})


categories_dialog = Dialog(
    Window(
        Case(
            {
                True: Const("📂 Текущие категории"),
                False: Const("Категорий пока нет")
            },
            selector="is_success"),
        scrolling_select_category,
        Button(Const("➕ Добавить новую категорию"), id="category_lists_add", on_click=start_create_category_dialog),
        Cancel(Const("⬅️ Назад")),

        getter=get_categories_data,
        state=CategoriesSG.main,
    ),
    Window(
        Format("<b>{name}</b>"),
        Button(Const("🗑️ Удалить"), id="delete_category", on_click=on_deleting_category),
        Button(Const("✏️ Изменить название"), id="change_category", on_click=on_changing_category),
        Button(Const("📝 Задачи категории"), id="category_tasks", on_click=on_category_tasks_list),
        Row(
            Cancel(Const("🏠 Вернуться в главное меню")),
            Back(Const("⬅️ Назад")),
        ),
        parse_mode=ParseMode.HTML,
        getter=get_category_data,
        state=CategoriesSG.detail

    ),
)


# Назад ⬅️
# - Отмена ❌
# - Готово ✅
# - Успешно 🎉

# - Задачи 📝
# - Категории 📂
# - Добавить ➕
# - Удалить 🗑️
# - Задача выполнена ✔️