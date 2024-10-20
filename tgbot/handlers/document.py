import os

from aiogram import Router
from aiogram.client.session import aiohttp
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ContentType, FSInputFile
from magic_filter import F

from infrastructure.api.terminal import TerminalAPI
from tgbot.handlers.order import API_URL
from tgbot.misc.states import TerminalDocument

document_router = Router()


@document_router.message(Command("search"))
async def get_container(message: Message, state: FSMContext):
    await message.answer("Отправьте номер контейнера")
    await state.set_state(TerminalDocument.container_number)


@document_router.message(TerminalDocument.container_number)
async def get_document(message: Message, state: FSMContext):
    terminal_api = TerminalAPI()
    response = await terminal_api.get_container(message.text)
    containers_info_list = response[0]

    if not containers_info_list:
        await message.answer("Контейнер не найден")

    for container in containers_info_list:
        response_parts = [
            f"Контейнер: <b>{container['container']['name']} ({container['container']['size']})</b>",
            f"Статус: <b>{container['container_state']}</b>",
            f"Клиент: <b>{container['company']['name']}</b>",
            f"Дата прибытия: <b>{container['entry_time']}</b>"
        ]

        for service in container['services']:
            response_parts.append(f"Услуга: <b>{service['service_type']['name']}</b>")

        response_message = "\n".join(response_parts)

        inline_keyboard = [
            [
                InlineKeyboardButton(text="Добавить фото",
                                     callback_data=f"photo_{container['id']}_{container['container']['name']}"),
                InlineKeyboardButton(text="Добавить документ",
                                     callback_data=f"document_{container['id']}_{container['container']['name']}")
            ]
        ]
        media_keyboard = []
        if container["images"]:
            media_keyboard.append(InlineKeyboardButton(text="Скачать Фото",
                                                       callback_data=f"downloadPhoto_{container['id']}_{container['container']['name']}"))

        if container["documents"]:
            media_keyboard.append(InlineKeyboardButton(text="Скачать Документ",
                                                       callback_data=f"downloadDocument_{container['id']}_{container['container']['name']}"))
        inline_keyboard.append(media_keyboard)
        container_reply = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        await message.answer(response_message, reply_markup=container_reply)


@document_router.callback_query(lambda c: c.data.startswith("photo_"))
async def add_photo(callback_query: CallbackQuery, state: FSMContext):
    container_id = callback_query.data.split("_")[1]
    await state.update_data({"container_id": container_id})
    container_name = callback_query.data.split("_")[2]
    await callback_query.message.answer(f"Добавьте фото контейнера {container_name}")
    await state.set_state(TerminalDocument.photo)


@document_router.callback_query(lambda c: c.data.startswith("document_"))
async def add_document(callback_query: CallbackQuery, state: FSMContext):
    container_id = callback_query.data.split("_")[1]
    await state.update_data({"container_id": container_id})
    container_name = callback_query.data.split("_")[2]
    await callback_query.message.answer(f"Добавьте документ контейнера {container_name}")
    await state.set_state(TerminalDocument.document)


@document_router.message(TerminalDocument.photo, F.content_type == ContentType.PHOTO)
async def save_photo(message: Message, state: FSMContext):
    terminal_api = TerminalAPI()
    container_id = (await state.get_data())["container_id"]

    # Get the file ID from the photo
    file_id = message.photo[-1].file_id
    file = await message.bot.get_file(file_id)

    # Download the photo
    file_path = file.file_path
    photo_url = f'https://api.telegram.org/file/bot{message.bot.token}/{file_path}'

    # Download the photo from the Telegram servers
    async with aiohttp.ClientSession() as session:
        async with session.get(photo_url) as response:
            photo_bytes = await response.read()

    # Prepare the form data with the photo
    data = aiohttp.FormData()
    data.add_field('file', photo_bytes, filename="photo.jpg", content_type='image/jpeg')

    try:
        await terminal_api.add_photo(container_id, data)
        await message.answer("Фото сохранено")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


@document_router.message(TerminalDocument.document, F.content_type == ContentType.DOCUMENT)
async def save_document(message: Message, state: FSMContext):
    terminal_api = TerminalAPI()
    container_id = (await state.get_data())["container_id"]

    # Get the file ID from the document
    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)

    # Download the document
    file_path = file.file_path
    document_url = f'https://api.telegram.org/file/bot{message.bot.token}/{file_path}'

    # Download the document from the Telegram servers
    async with aiohttp.ClientSession() as session:
        async with session.get(document_url) as response:
            document_bytes = await response.read()

    # Prepare the form data with the document
    data = aiohttp.FormData()
    data.add_field('file', document_bytes, filename=message.document.file_name)

    try:
        await terminal_api.add_document(container_id, data)
        await message.answer("Документ сохранен")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


@document_router.callback_query(lambda c: c.data.startswith("downloadPhoto_"))
async def download_photo(callback_query: CallbackQuery):
    container_id = callback_query.data.split("_")[1]
    container_name = callback_query.data.split("_")[2]
    terminal_api = TerminalAPI()
    images = await terminal_api.get_photos(container_id)

    for image in images:
        image_url = f"{API_URL}{image['image']}"  # Construct full URL

        # Download the image
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()

                    # Save the image to a temporary file
                    temp_filename = f"temp_{container_id}_{image['id']}.jpg"
                    with open(temp_filename, "wb") as f:
                        f.write(image_data)

                    # Use FSInputFile to send the photo
                    photo = FSInputFile(temp_filename)
                    await callback_query.message.answer_photo(photo=photo)

                    # Remove the temporary file after sending
                    os.remove(temp_filename)

    await callback_query.message.answer(f"Фото контейнера {container_name}")


@document_router.callback_query(lambda c: c.data.startswith("downloadDocument_"))
async def download_document(callback_query: CallbackQuery):
    container_id = callback_query.data.split("_")[1]
    container_name = callback_query.data.split("_")[2]
    terminal_api = TerminalAPI()
    documents = await terminal_api.get_documents(container_id)

    for document in documents:
        document_url = f"{API_URL}{document['document']}"
        async with aiohttp.ClientSession() as session:
            async with session.get(document_url) as resp:
                if resp.status == 200:
                    document_data = await resp.read()
                    # Extract the original file extension
                    file_extension = os.path.splitext(document['document'])[1]
                    temp_filename = f"temp_{container_id}_{document['id']}{file_extension}"
                    with open(temp_filename, "wb") as f:
                        f.write(document_data)
                    document = FSInputFile(temp_filename)
                    await callback_query.message.answer_document(document=document)
                    os.remove(temp_filename)
    await callback_query.message.answer(f"Документ контейнера {container_name}")
