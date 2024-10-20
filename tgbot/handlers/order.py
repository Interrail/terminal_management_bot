import json
import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from infrastructure.api.terminal import TerminalAPI
from tgbot.keyboards.inline import start_keyboard, container_type_keyboard, \
    container_loading_keyboard, transport_type_keyboard, confirmation_keyboard, back_keyboard
from tgbot.misc.states import TerminalImport

user_router = Router()
API_URL = "https://api.trains.uz"
PER_PAGE = 40


def create_paginated_keyboard(items: list, current_page: int, total_items: int,
                              callback_prefix: str) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()

    for item in items:
        keyboard.button(text=item['name'], callback_data=f"{callback_prefix}_{item['id']}_{item['name']}")

    total_pages = (total_items - 1) // PER_PAGE + 1
    if current_page > 1:
        keyboard.button(text="⬅️ Назад", callback_data=f"page_{current_page - 1}")
    if current_page < total_pages:
        keyboard.button(text="Вперед ➡️", callback_data=f"page_{current_page + 1}")

    keyboard.adjust(2)
    return keyboard


async def get_current_message(state: FSMContext) -> str:
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


async def update_message(message: Message | CallbackQuery, state: FSMContext, additional_text: str = "",
                         reply_markup=None):
    current_message = await get_current_message(state)
    full_message = f"{current_message}\n\n<b>{additional_text}</b>".strip()

    if isinstance(message, Message):
        await message.answer(full_message, parse_mode="HTML", reply_markup=reply_markup)
    elif isinstance(message, CallbackQuery):
        await message.message.edit_text(full_message, parse_mode="HTML", reply_markup=reply_markup)


@user_router.message(Command('create_order'))
async def user_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(TerminalImport.request_type)
    await message.answer("Вас приветствует МТТ бот для заявки!\n", reply_markup=start_keyboard)


@user_router.callback_query(TerminalImport.request_type, F.data != "back")
async def get_request_type(call: CallbackQuery, state: FSMContext):
    await state.update_data(request_type=call.data.upper())
    await state.set_state(TerminalImport.container_size)
    await update_message(call, state, "Выберите тип контейнера:", reply_markup=container_type_keyboard.as_markup())


@user_router.callback_query(TerminalImport.container_size, F.data != "back")
async def get_container_type(call: CallbackQuery, state: FSMContext):
    await state.update_data(container_size=call.data.upper())
    await state.set_state(TerminalImport.container_name)
    await update_message(call, state, "Введите номер контейнера (Например:TGHU1234567):",
                         reply_markup=back_keyboard.as_markup())


@user_router.message(TerminalImport.container_name)
async def get_container_name(message: Message, state: FSMContext):
    clean_text = re.sub(r'\s+', '', message.text)
    if not re.match(r'^[A-Za-z]{4}\d{7}$', clean_text):
        await message.answer("Номер контейнера должен быть 11 символов: первые 4 буквы, затем 7 цифр.")
        return
    terminal_api = TerminalAPI()
    containers,count = await terminal_api.get_container(container_name=clean_text)
    for i in range(count):
        if containers[i]['exit_time'] is None:
            await message.answer("Контейнер с таким номером уже существует.")
            return


    await state.update_data(container_name=clean_text.upper())

    await state.set_state(TerminalImport.container_state)
    await update_message(message, state, "Контейнер:", reply_markup=container_loading_keyboard.as_markup())


@user_router.callback_query(TerminalImport.container_state, F.data != "back")
async def get_loading_type(call: CallbackQuery, state: FSMContext):
    container_state = call.data
    await state.update_data(container_state=container_state)

    if container_state == 'empty':
        await state.set_state(TerminalImport.customer_name)
        await show_clients_list(call, state)
    else:
        await state.set_state(TerminalImport.product_name)
        await update_message(call, state, "Введите название продукта:", reply_markup=back_keyboard.as_markup())


@user_router.message(TerminalImport.product_name)
async def get_product_name(message: Message, state: FSMContext):
    await state.update_data(product_name=message.text.upper())
    await state.set_state(TerminalImport.customer_name)
    await show_clients_list(message, state)


async def show_clients_list(message: Message | CallbackQuery, state: FSMContext, page: int = 1):
    terminal_api = TerminalAPI()
    clients, total_clients = await terminal_api.get_clients((page - 1) * PER_PAGE, PER_PAGE)
    if not clients:
        await message.answer("Список клиентов пуст.")
        return

    keyboard = create_paginated_keyboard(clients, page, total_clients, "client")
    keyboard.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))
    await update_message(
        message,
        state,
        f"Выберите клиента (Страница {page} из {(total_clients - 1) // PER_PAGE + 1}):",
        reply_markup=keyboard.as_markup()
    )




@user_router.callback_query(lambda c: c.data.startswith("page_"))
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[1])
    await show_clients_list(callback, state, page)
    await callback.answer()

@user_router.callback_query(lambda c: c.data.startswith("servicepage_"))
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[1])
    await show_services_list(callback, state, page)
    await callback.answer()


@user_router.callback_query(lambda c: c.data.startswith("client_"), TerminalImport.customer_name)
async def handle_client_selection(callback: CallbackQuery, state: FSMContext):
    customer_name = callback.data.split("_")[-1]
    customer_id = int(callback.data.split("_")[1])
    await state.update_data(customer_name=customer_name, customer_id=customer_id)
    await state.set_state(TerminalImport.container_owner)
    await update_message(callback, state, "Введите Собственника контейнера:", reply_markup=back_keyboard.as_markup())


@user_router.message(TerminalImport.container_owner)
async def handle_customer_owner(message: Message, state: FSMContext):
    await state.update_data(container_owner=message.text)
    await state.set_state(TerminalImport.date)
    keyboard = await SimpleCalendar().start_calendar()
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back")])
    await update_message(message, state, "Выберите дату:", reply_markup=keyboard)


@user_router.callback_query(SimpleCalendarCallback.filter(), TerminalImport.date)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback,
                                  state: FSMContext):
    calendar = SimpleCalendar(show_alerts=True)
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(date=date)
        await state.set_state(TerminalImport.transport_type)
        await update_message(callback_query, state, "Тип транспорта:", reply_markup=transport_type_keyboard.as_markup())


@user_router.callback_query(TerminalImport.transport_type, F.data != "back")
async def handle_transport_type(callback: CallbackQuery, state: FSMContext):
    await state.update_data(transport_type=callback.data)
    await state.set_state(TerminalImport.transport_number)
    transport = 'Вагон' if callback.data == "wagon" else 'Авто'
    await update_message(callback, state, f"Введите номер {transport}:", reply_markup=back_keyboard.as_markup())


@user_router.message(TerminalImport.transport_number)
async def handle_transport_number(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(transport_number=message.text, selected_services=[])
    await state.set_state(TerminalImport.selected_services)
    await show_services_list(message, state)


async def show_services_list(message: Message | CallbackQuery, state: FSMContext, page: int = 1):
    data = await state.get_data()
    terminal_api = TerminalAPI()
    services, total_services = await terminal_api.get_services((page - 1) * PER_PAGE, PER_PAGE,
                                                               customer_id=data['customer_id'],

                                                               container_size=data.get('container_size'),
                                                               container_state=data.get('container_state'))
    if not services:
        await message.answer("Не удалось получить список сервисов. Попробуйте позже.")
        return

    keyboard = create_services_keyboard(services, page, total_services, data.get('selected_services', []))
    await update_message(message, state, "Выберите дополнительные услуги!", reply_markup=keyboard.as_markup())


def create_services_keyboard(services: list, current_page: int, total_services: int,
                             selected_services: list) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()

    for service in services:
        service_id = service['id']
        is_selected = service_id in selected_services
        service_name = f"{service['service_type']['name']}"

        button_text = f"✅ {service_name}" if is_selected else service_name
        keyboard.button(text=button_text, callback_data=f"ss_{service_name}___{service_id}")

    total_pages = (total_services - 1) // PER_PAGE + 1
    if current_page > 1:
        keyboard.button(text="⬅️ Назад", callback_data=f"servicepage_{current_page - 1}")
    if current_page < total_pages:
        keyboard.button(text="Вперед ➡️", callback_data=f"servicepage_{current_page + 1}")

    keyboard.button(text="Подтвердить ✅", callback_data="confirm_services")
    keyboard.button(text="◀️ Назад", callback_data="back")
    keyboard.adjust(2)
    return keyboard


@user_router.callback_query(lambda c: c.data.startswith("ss_"), F.data != "back")
async def handle_service_selection(callback_query: CallbackQuery, state: FSMContext):
    service_id = int(callback_query.data.split("___")[1])
    service_name = callback_query.data.split("___")[0].split("_")[-1]
    data = await state.get_data()
    selected_services = data.get('selected_services', [])
    selected_service_names = data.get('selected_service_names', [])
    if service_id in selected_services:
        selected_services.remove(service_id)
        selected_service_names.remove(service_name)

    else:
        selected_services.append(service_id)
        selected_service_names.append(service_name)

    await state.update_data(selected_services=selected_services)
    await state.update_data(selected_service_names=selected_service_names)
    await show_services_list(callback_query, state)


@user_router.callback_query(lambda c: c.data == "confirm_services", F.data != "back")
async def handle_confirm_services(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_services = data.get('selected_services', [])
    if not selected_services:
        await callback_query.answer("Пожалуйста, выберите хотя бы одну услугу.")
        return

    await update_message(callback_query, state, "Подтвердить ✅ ?", reply_markup=confirmation_keyboard.as_markup())
    await state.set_state(TerminalImport.confirmation)


@user_router.callback_query(lambda c: c.data == "confirm", TerminalImport.confirmation, F.data != "back")
async def handle_confirm(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    terminal_api = TerminalAPI()
    selected_services = [{"id": service_id} for service_id in data['selected_services']]
    container_data = {
        "container_size": data['container_size'],
        "container_name": data['container_name'],
        "container_state": data['container_state'].lower(),
        "product_name": data.get('product_name', ''),
        "company_id": data['customer_id'],
        "container_owner": data['container_owner'],
        "transport_type": data['transport_type'],
        "transport_number": data['transport_number'],
        "entry_time": data['date'].strftime('%Y-%m-%d'),
        "services": selected_services,
    }

    response = await terminal_api.register_container(container_data)

    from bot import bot
    await bot.send_message(chat_id=5331201165, text=json.dumps(response[0], ensure_ascii=False, indent=4))
    if response[-1] == 201:
        await callback_query.message.answer("Заявка успешно создана!!", reply_markup=ReplyKeyboardRemove())
        await state.clear()

    else:
        await callback_query.answer("Произошла ошибка при создании заявки. Попробуйте еще раз.")


@user_router.callback_query(F.data == "back")
async def handle_back(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()

    state_order = [
        TerminalImport.request_type,
        TerminalImport.container_size,
        TerminalImport.container_name,
        TerminalImport.container_state,
        TerminalImport.product_name,
        TerminalImport.customer_name,
        TerminalImport.container_owner,
        TerminalImport.date,
        TerminalImport.transport_type,
        TerminalImport.transport_number,
        TerminalImport.selected_services,
        TerminalImport.confirmation
    ]

    current_index = state_order.index(current_state)

    if current_index > 0:
        previous_state = state_order[current_index - 1]
        await state.set_state(previous_state)

        # Handle different previous states
        if previous_state == TerminalImport.request_type:
            await update_message(callback, state, "Выберите тип заявки", reply_markup=start_keyboard)
        elif previous_state == TerminalImport.container_size:
            await update_message(callback, state, "Выберите тип контейнера:",
                                 reply_markup=container_type_keyboard.as_markup())
        elif previous_state == TerminalImport.container_name:
            await update_message(callback, state, "Введите номер контейнера:", reply_markup=back_keyboard.as_markup())
        elif previous_state == TerminalImport.container_state:
            await update_message(callback, state, "Контейнер:", reply_markup=container_loading_keyboard.as_markup())
        elif previous_state == TerminalImport.product_name:
            if data.get('container_state') != 'EMPTY':
                await update_message(callback, state, "Введите название продукта:",
                                     reply_markup=back_keyboard.as_markup())
            else:
                await show_clients_list(callback, state)
        elif previous_state == TerminalImport.customer_name:
            await show_clients_list(callback, state)
        elif previous_state == TerminalImport.container_owner:

            await update_message(callback, state, "Введите Собственника контейнера:",
                                 reply_markup=back_keyboard.as_markup())
        elif previous_state == TerminalImport.date:
            keyboard = await SimpleCalendar().start_calendar()
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back")])
            await update_message(callback, state, "Выберите дату:",
                                 reply_markup=keyboard)
        elif previous_state == TerminalImport.transport_type:
            await update_message(callback, state, "Тип транспорта:", reply_markup=transport_type_keyboard.as_markup())
        elif previous_state == TerminalImport.transport_number:
            transport = 'Вагон' if data.get('transport_type') == "wagon" else 'Авто'
            await update_message(callback, state, f"Введите номер {transport}:", reply_markup=back_keyboard.as_markup())
        elif previous_state == TerminalImport.selected_services:
            await show_services_list(callback, state)

        # Remove the data for the current state
        if current_state in data:
            del data[current_state]
        await state.set_data(data)
    else:
        await callback.answer("Вы уже на начальном этапе.")

    await callback.answer()
