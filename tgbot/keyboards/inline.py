from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Приём 📥", callback_data="import"),
        ],
        [
            InlineKeyboardButton(text="Отправка 📤", callback_data="export"),
        ],
    ]
)

# This is a simple keyboard, that contains 2 buttons
transport_type_keyboard = InlineKeyboardBuilder()
transport_type_keyboard.add(InlineKeyboardButton(text="🚚 Авто", callback_data="auto"))
transport_type_keyboard.add(InlineKeyboardButton(text="🚆 ЖД", callback_data="wagon"))
transport_type_keyboard.adjust(2)
transport_type_keyboard.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))

# Container type keyboard
container_type_keyboard = InlineKeyboardBuilder()
container_type_keyboard.add(InlineKeyboardButton(text="📦 20", callback_data="20"))
container_type_keyboard.add(InlineKeyboardButton(text="📦 20HC", callback_data="20HC"))
container_type_keyboard.add(InlineKeyboardButton(text="📦 40", callback_data="40"))
container_type_keyboard.add(InlineKeyboardButton(text="📦 40HC", callback_data="40HC"))
container_type_keyboard.add(InlineKeyboardButton(text="📦 45", callback_data="45"))
container_type_keyboard.adjust(2, 2, 1)
container_type_keyboard.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))



container_loading_keyboard = InlineKeyboardBuilder()
container_loading_keyboard.add(InlineKeyboardButton(text="Гружённый 🚛", callback_data="loaded"))
container_loading_keyboard.add(InlineKeyboardButton(text="Порожний 🚚", callback_data="empty"))
container_loading_keyboard.adjust(2)
container_loading_keyboard.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))

confirmation_keyboard = InlineKeyboardBuilder()
confirmation_keyboard.button(text="Подтвердить ✅", callback_data="confirm")
confirmation_keyboard.button(text="Назад", callback_data="back")

back_keyboard = InlineKeyboardBuilder()
back_keyboard.button(text="◀️ Назад", callback_data="back")


yes_no_keyboard = InlineKeyboardBuilder()
yes_no_keyboard.button(text="Да", callback_data="yes")
yes_no_keyboard.button(text="Нет", callback_data="no")