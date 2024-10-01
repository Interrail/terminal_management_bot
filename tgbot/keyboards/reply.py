from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📝 Заполнить заявку"), KeyboardButton(text="Поиск контейнера")]],
    resize_keyboard=True,
    selective=True,
)
