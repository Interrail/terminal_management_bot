from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

menu_router = Router()


@menu_router.message(CommandStart())
async def menu_start(message: Message):
    await message.answer("Привет! Это бот для учёта контейнеров", reply_markup=ReplyKeyboardRemove())
