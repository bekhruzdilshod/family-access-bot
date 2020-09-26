from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage


import ops
import configparser
import str_templates as str_tmp
import nav
import states


config = configparser.ConfigParser()
config.read("config.ini")

storage = MemoryStorage()
bot = Bot(config["BOT"]["TOKEN"])
print(config["BOT"]["TOKEN"])
dp = Dispatcher(bot=bot, storage=storage)


# Обработка стартового сообщения
@dp.message_handler(commands=["start"])
async def start_message(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    member = ops.get_member_by_id(chat_id)
    if not member:
        await bot.send_message(chat_id, str_tmp.start["not_auth"], reply_markup=nav.setup_menu,
                               parse_mode=ParseMode.MARKDOWN)
    else:
        await bot.send_message(chat_id, "Вы уже зарегистрированы в системе! Введите /main для перехода в главное меню!")


# ГЛАВНОЕ МЕНЮ НАВИГАЦИИ
@dp.message_handler(commands=["main"])
async def main_menu(message: types.Message, state: FSMContext):
    await message.answer("Хеллоу!")


# ----------------------------------------------- ОБРАБОТКИ STATES И FSM-CONTEXT ---------------------------------------
# Обработка запроса присоединения к семье, в случае, если введен несуществующий ID для семьи
@dp.message_handler(lambda message: message.text not in ops.get_families_id() or len(message.text) > 6,
                    state=states.JoinFamily.family_id)
async def family_not_exists(message: types.Message, state: FSMContext):
    await message.answer(str_tmp.join_family["not_exists"], parse_mode=ParseMode.MARKDOWN)
    await states.JoinFamily.family_id.set()


# Обработка успешного запроса присоединения к семье по ID
@dp.message_handler(state=states.JoinFamily.family_id)
async def handle_join_family_id(message: types.Message, state: FSMContext):
    family_id = message.text
    await state.update_data(family_id=family_id)
    await states.JoinFamily.user_name.set()
    await message.answer(str_tmp.join_family["input_user_name"], parse_mode=ParseMode.MARKDOWN)


# Последний шаг к добавлению в семью, выбор будущего имени участника семьи
@dp.message_handler(state=states.JoinFamily.user_name)
async def handle_join_family_user_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    user_name = message.text
    async with state.proxy() as data:
        family_id = data["family_id"]
    if ops.create_member(chat_id, int(family_id), user_name):
        await message.answer(str_tmp.join_family["success"].format(family_id=family_id), parse_mode=ParseMode.MARKDOWN)
        family_joined_to = ops.get_family_by_id(family_id)
        family_members_list = family_joined_to.get_members()
        for x in family_members_list:               # Отправка сообщения о новом участнике всем членам семьи
            if not x.id == chat_id:                 # Предотвращение отправки сообщения новому участнику
                await bot.send_message(x.id,
                                       str_tmp.join_family["new_member_in_your_family"].format(name=x.name,
                                                                                               new_member_name=user_name),
                                       parse_mode=ParseMode.MARKDOWN)
        await state.finish()


# Обработка запроса на создание семьи (введение имени семьи)
@dp.message_handler(state=states.CreateFamily.family_name)
async def handle_create_family_name(message: types.Message, state: FSMContext):
    family_name = message.text
    await state.update_data(family_name=family_name)
    await states.CreateFamily.user_name.set()
    await message.answer(str_tmp.create_family["input_user_name"], parse_mode=ParseMode.MARKDOWN)


# Последний шаг к созданию семьи. Введение имени нового пользователя, регистрация
@dp.message_handler(state=states.CreateFamily.user_name)
async def handle_create_family_user_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    async with state.proxy() as data:
        family_name = data["family_name"]
    created_family = ops.create_family(name=family_name)
    if created_family:
        ops.create_member(chat_id, created_family.id, message.text, admin_status=1)
        await message.answer(str_tmp.create_family["success"].format(family_name=created_family.name,
                                                                     family_id=created_family.id),
                             parse_mode=ParseMode.MARKDOWN)
        await state.finish()


# ------------------------------------------- CALLBACK ОБРАБОТКИ ------------------------------------------------------
# Обработчик Callback-запроса при нажатии кнопки присоединения к семье (кнопка в стартовом меню)
@dp.callback_query_handler(text="joinFamily")
async def callback_join_family(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    chat_id = call.message.chat.id
    await states.JoinFamily.family_id.set()
    await bot.send_message(chat_id, str_tmp.join_family["input_id"], parse_mode=ParseMode.MARKDOWN)


# Обработчик callback-запроса при нажатии кнопки создания семьи (кнопка в стартовом меню)
@dp.callback_query_handler(text="createFamily")
async def callback_create_family(call: types.CallbackQuery):
    await call.message.delete()
    chat_id = call.message.chat.id
    await states.CreateFamily.family_name.set()
    await bot.send_message(chat_id, str_tmp.create_family["input_family_name"], parse_mode=ParseMode.MARKDOWN)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
