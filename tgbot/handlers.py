from datetime import datetime, timedelta

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from tgbot.data_exchanger import list_tasks, auth_user, get_categories, add_task, delete_task, task_is_done, \
    get_task, update_task
from tgbot.keyboards import show_or_create_task_kb, get_keyboard_button_without_category, get_categories_kb
from tgbot.utils import TaskStates, user_tokens, is_valid_time, make_task_msgs

router = Router()


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=show_or_create_task_kb()
    )


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state()
    user_id = message.from_user.id
    response = await auth_user(user_id)
    if response["status"] == 200:
        data = response["json"]

        user_tokens.set_tokens(user_id, data["access"], data["refresh"])

        await message.answer(
            "Вы успешно авторизованы!",
            reply_markup=show_or_create_task_kb()
        )
    else:
        await message.answer("Не удалось авторизоваться. Попробуйте позже.")


# Хэндлер на кнопку показать задачи
@router.message(Command(commands=["list"]))
@router.message(F.text.lower() == "текущие задачи")
async def show_tasks_list(message: types.Message, headers):
    data = await list_tasks(headers, message.from_user.id)
    tasks = data["json"]
    if tasks:
        msgs = make_task_msgs(tasks)
        for msg in msgs:
            await message.answer(
                text=msg[0],
                reply_markup=msg[1]
            )
    else:
        await message.answer("Задач пока нет, создайте новую задачу")


@router.message(Command(commands=["categories"]))
@router.message(F.text.lower() == "категории задач")
async def show_categories(message: types.Message, headers):
    data = await get_categories(headers, message.from_user.id)
    categories = data["json"]
    if categories:
        kb = get_categories_kb(categories)

        await message.answer(text="Категории:", reply_markup=kb)

    else:
        await message.answer("Категорий нет")


@router.callback_query(F.data.startswith("cats_"))
async def callbacks_tasks(callback: types.CallbackQuery, state: FSMContext, headers):
    cat_id = callback.data.split("_")[1]
    data = await list_tasks(headers, callback.from_user.id, cat_id)
    tasks = data["json"]
    if tasks:
        msgs = make_task_msgs(tasks)
        for msg in msgs:
            await callback.message.answer(
                text=msg[0],
                reply_markup=msg[1]
            )
    else:
        await callback.message.answer("Задач пока нет, создайте новую задачу")


@router.callback_query(F.data.startswith("task_"))
async def callbacks_tasks(callback: types.CallbackQuery, state: FSMContext, headers):
    await state.clear()
    callback_data = callback.data.split("_")
    task_id = callback_data[2]
    action = callback_data[1]

    if action == "edit":
        await state.set_state(TaskStates.entering_task_name)
        await state.update_data(is_editing=True)
        await state.update_data(task_id=task_id)
        task = await get_task(headers, task_id)
        task = task['json']
        await state.update_data(title=task['title'])
        await state.update_data(description=task['description'])
        await state.update_data(deadline=task['deadline'])
        await state.update_data(categories=task['categories'])

        await callback.message.answer(
            text=f"Текущее название: {task['title']}\n"
                 f"Введите новое название задачи"
        )

    elif action == "done":
        res = await task_is_done(headers, task_id)
        if res['status'] == 200:
            msg = "задача помечена как выполненная"
        else:
            msg = "Проблемы на сервере, уже решаем проблему. Попробуйте еще раз позднее"
        await callback.message.answer(msg)
    elif action == "delete":
        res = await delete_task(headers, task_id)
        if res['status'] == 204:
            msg = "Задача удалена"
        else:
            msg = "Проблемы на сервере, уже решаем проблему. Попробуйте еще раз позднее"
        await callback.message.answer(msg)


# Хэндлер на кнопку создать задачу
@router.message(Command(commands=["create"]))
@router.message(StateFilter(None), F.text.lower() == "создать задачу")
async def create_task(message: types.Message, state: FSMContext):
    await state.update_data(is_editing=False)
    await message.answer(
        text="Введите название задачи"
    )
    # Устанавливаем пользователю состояние "вводит название задачи"
    await state.set_state(TaskStates.entering_task_name)


@router.message(TaskStates.entering_task_name)
async def task_title_entered(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(
        text="Введите краткое описание задачи"
    )

    await state.set_state(TaskStates.entering_task_description)


@router.message(TaskStates.entering_task_description)
async def task_description_entered(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)

    await message.answer(
        text="Введите категории через запятую",
        reply_markup=get_keyboard_button_without_category()
    )

    await state.set_state(TaskStates.choosing_task_category)


@router.callback_query(F.data.startswith("without_category"), TaskStates.choosing_task_category)
async def task_without_category(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    calendar = SimpleCalendar()
    calendar.set_dates_range(datetime.today(), datetime.today() + timedelta(days=365))
    await callback_query.message.answer(
        text="Укажите дату напоминания",
        reply_markup=await calendar.start_calendar()
    )

    await state.set_state(TaskStates.setting_deadline_date)


@router.message(TaskStates.choosing_task_category)
async def categories_entered(message: types.Message, state: FSMContext):
    await state.update_data(categories=message.text)

    calendar = SimpleCalendar()
    calendar.set_dates_range(datetime.today(), datetime.today() + timedelta(days=365))
    await message.answer(
        text="Укажите дату напоминания",
        reply_markup=await calendar.start_calendar()
    )

    await state.set_state(TaskStates.setting_deadline_date)


@router.callback_query(SimpleCalendarCallback.filter(), TaskStates.setting_deadline_date)
async def process_dialog_calendar(
        callback_query: types.CallbackQuery,
        callback_data: SimpleCalendarCallback,
        state: FSMContext
):
    selected, date = await (SimpleCalendar().
                            process_selection(callback_query, callback_data))
    if selected:
        if date.date() < datetime.today().date():
            calendar = SimpleCalendar()
            calendar.set_dates_range(datetime.today(), datetime.today() + timedelta(days=365))

            await callback_query.message.answer(
                text="Дата должна быть не ранее сегодняшней",
                reply_markup=await calendar.start_calendar()
            )
            return

        await state.update_data(date=date.strftime("%Y-%m-%d"))

        await callback_query.message.answer(
            text="Укажите время напоминания в формате HH:MM"
        )

        await state.set_state(TaskStates.setting_deadline_time)


@router.message(TaskStates.setting_deadline_time)
async def time_entered(message: types.Message, state: FSMContext, headers):
    if not is_valid_time(message.text):
        await message.answer(
            text="Неверный формат! Укажите время напоминания в формате HH:MM, например, 06:30"
        )
        return
    data = await state.get_data()

    time_chosen = datetime.strptime(
        f"{data['date']} {message.text}",
        "%Y-%m-%d %H:%M"
    )
    if time_chosen < datetime.now():
        await message.answer(
            text="Время должно быть не в прошлом"
        )
        return

    user_data = await state.get_data()
    user_data["date"] += f" {message.text}"
    user_data["chat_id"] = message.chat.id
    user_data["tg_id"] = message.from_user.id

    is_editing = user_data.get('is_editing')
    if is_editing:
        print("Updating", user_data)
        res = await update_task(headers, user_data)
    else:
        res = await add_task(headers, user_data)

    if res['status'] == 201:
        msg = "Задача создана"
    elif res['status'] == 200:
        msg = "Задача обновлена"
    else:
        msg = "Проблемы на сервере, уже решаем проблему. Попробуйте еще раз позднее"
    await message.answer(
        text=msg,
        reply_markup=show_or_create_task_kb()
    )

    await state.clear()
    await state.set_state()
