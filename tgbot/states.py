from aiogram.fsm.state import StatesGroup, State


class MainDialogSG(StatesGroup):
    main = State()


class TasksSG(StatesGroup):
    list = State()
    detail = State()

class CreateTaskSG(StatesGroup):
    title = State()
    description = State()
    category = State()
    date = State()
    time = State()
    confirmation = State()


class CategoriesSG(StatesGroup):
    main = State()
    list = State()
    detail = State()
    new = State()


class CreateCategorySG(StatesGroup):
    name = State()


class AuthStates(StatesGroup):
    waiting_for_auth = State()
