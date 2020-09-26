from aiogram.dispatcher.filters.state import StatesGroup, State


class CreateFamily(StatesGroup):
    family_name = State()
    user_name = State()


class JoinFamily(StatesGroup):
    family_id = State()
    user_name = State()
