from aiogram.types import *
import icons

# Inline-клавиатура, при первом использовании бота
setup_menu = InlineKeyboardMarkup(True)
create_family = InlineKeyboardButton(text=icons.add + " Создать семью", callback_data="createFamily")
join_family = InlineKeyboardButton(text=icons.join + " Присоединиться к семье", callback_data="joinFamily")
setup_menu.row(create_family)
setup_menu.row(join_family)
