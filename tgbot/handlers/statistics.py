from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from infrastructure.api.terminal import TerminalAPI

statistic_router = Router()


@statistic_router.message(Command("statistics"))
async def get_container(message: Message):
    terminal_api = TerminalAPI()
    statistics = await terminal_api.get_statistics()
    statistics_message = f"""
Общшее Количество контейнеров: <b>{statistics['total_containers']}</b>
Груженные контейнера: <b>{statistics['loaded_containers']}</b>
Порожние контейнера: <b>{statistics['empty_containers']}</b>
Контейнеры в терминале: <b>{statistics['total_active_containers']}</b>
Отправленные контейнеры: <b>{statistics['total_dispatched_containers']}</b>
Контейнеры на терминале: <b>{statistics['total_active_containers']}</b>
Новые контейнера: <b>{statistics['new_arrived_containers']}</b>
"""
    await message.answer(statistics_message)
