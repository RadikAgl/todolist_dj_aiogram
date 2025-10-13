import logging

from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from aiogram_dialog import DialogManager, StartMode, Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.text import Const

from tgbot.states import MainDialogSG, CreateTaskSG, CategoriesSG, TasksSG

logger = logging.getLogger(__name__)

router = Router()


async def start_create_task_dialog(callback: CallbackQuery, button: Button,
                                   manager: DialogManager):
    await manager.start(CreateTaskSG.title, data={"is_editing": False, "task_id": None})


async def start_tasks_dialog(callback: CallbackQuery, button: Button,
                             manager: DialogManager):
    await manager.start(TasksSG.list, data={"category_id": None})


main_dialog = Dialog(
    Window(
        Const("🏠 Меню"),
        Button(Const("📝 Список задач"), id="list_tasks", on_click=start_tasks_dialog),
        Button(Const("➕ Добавить задачу"), id="create_task", on_click=start_create_task_dialog),
        Start(Const("📂 Категории"), id="list_categories", state=CategoriesSG.main),
        state=MainDialogSG.main,
    ),
)


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="❌ Действие отменено"
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, dialog_manager: DialogManager):
    await state.clear()
    await state.set_state()
    await message.answer(
        "Привет! 👋 \n\n "
        "Я помогу тебе больше ничего не забывать. Создавай задачи, сортируй их по категориям"
        " и отмечай выполненное всего в несколько кликов.\n\n"
        "Чтобы начать воспользуйся меню ниже!"
    )
    await dialog_manager.start(MainDialogSG.main, mode=StartMode.RESET_STACK)
