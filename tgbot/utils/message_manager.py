from typing import Union, Optional
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

class MessageManager:
    async def get_current_message(self, state: FSMContext) -> str:
        """Get formatted current message from state data."""
        data = await state.get_data()
        translations = {
            'request_type': 'Тип заявки',
            'container_size': 'Размер контейнера',
            'container_name': 'Номер контейнера',
            'container_state': 'Состояние контейнера',
            'product_name': 'Название продукта',
            'customer_name': 'Имя клиента',
            'container_owner': 'Собственник контейнера',
            'transport_type': 'Тип транспорта',
            'transport_number': 'Номер транспорта',
            'date': 'Дата',
            'selected_service_names': 'Выбранные услуги'
        }

        message_parts = [
            f"{translations.get(key, key).capitalize()}: <b>{value}</b>"
            for key, value in data.items()
            if key in translations
        ]
        return "\n".join(message_parts)

    async def update_message(
        self,
        message: Union[Message, CallbackQuery],
        state: FSMContext,
        additional_text: str = "",
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ):
        """Update message with current state and additional text."""
        current_message = await self.get_current_message(state)
        full_message = f"{current_message}\n\n<b>{additional_text}</b>".strip()

        if isinstance(message, Message):
            await message.answer(full_message, parse_mode="HTML", reply_markup=reply_markup)
        elif isinstance(message, CallbackQuery):
            await message.message.edit_text(full_message, parse_mode="HTML", reply_markup=reply_markup)
