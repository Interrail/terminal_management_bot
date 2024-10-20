import pytest
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, MagicMock

from infrastructure.api.terminal import TerminalAPI
from tgbot.handlers.order import create_paginated_keyboard, get_current_message, update_message, show_clients_list, \
    show_services_list, handle_pagination, handle_service_selection, handle_confirm_services, handle_confirm, \
    handle_transport_type, get_container_name


# Fixtures for creating mock objects for message, callback query, state, and terminal API
@pytest.fixture
def mock_message():
    return MagicMock(spec=Message)


@pytest.fixture
def mock_callback_query():
    return MagicMock(spec=CallbackQuery)


@pytest.fixture
def mock_state():
    return AsyncMock(spec=FSMContext)


@pytest.fixture
def mock_terminal_api():
    return AsyncMock(spec=TerminalAPI)


@pytest.mark.asyncio
async def test_create_paginated_keyboard():
    items = [{'name': 'Client 1', 'id': 1}, {'name': 'Client 2', 'id': 2}]
    current_page = 1
    total_items = 80
    callback_prefix = "client"
    keyboard = create_paginated_keyboard(items, current_page, total_items, callback_prefix)

    # Assuming the correct way to access buttons is through a method or property
    buttons = keyboard.as_markup().inline_keyboard

    # Check the number of buttons
    assert len(buttons) == 2

    # Check the item buttons
    assert buttons[0][0].text == 'Client 1'
    assert buttons[0][0].callback_data == 'client_1_Client 1'
    assert buttons[0][1].text == 'Client 2'
    assert buttons[0][1].callback_data == 'client_2_Client 2'

    # Check the pagination button
    assert buttons[1][0].text == 'Вперед ➡️'
    assert buttons[1][0].callback_data == 'page_2'
    # 2 buttons for items, 1 for next, 1 for back


@pytest.mark.asyncio
async def test_get_current_message(mock_state):
    mock_state.get_data.return_value = {
        'request_type': 'import',
        'container_size': 'large',
        'customer_name': 'Client X'
    }
    message = await get_current_message(mock_state)
    print(message)
    expected = "Тип заявки: <b>import</b>\nРазмер контейнера: <b>large</b>\nИмя клиента: <b>Client X</b>"
    assert message == expected


@pytest.mark.asyncio
async def test_update_message(mock_state):
    # Create mock_message using AsyncMock for asynchronous behavior
    mock_message = AsyncMock(spec=Message)

    # Mock the return value for get_data as it is awaited
    mock_state.get_data = AsyncMock(return_value={
        'request_type': 'import',
        'container_size': 'large',
        'customer_name': 'Client X'
    })

    additional_text = "Дополнительная информация"

    # Call the async function under test
    await update_message(mock_message, mock_state, additional_text)

    # Verify that mock_message.answer was called once
    mock_message.answer.assert_called_once()

    # Retrieve the arguments with which it was called
    args, kwargs = mock_message.answer.call_args

    # Assert that the expected text is in the 'text' argument
    assert "Тип заявки: <b>IMPORT</b>" in kwargs['text']
    assert "Дополнительная информация" in kwargs['text']

#
# @pytest.mark.asyncio
# async def test_show_clients_list(mock_message, mock_state, mock_terminal_api):
#     mock_terminal_api.get_clients.return_value = ([{'name': 'Client 1', 'id': 1}, {'name': 'Client 2', 'id': 2}], 80)
#     await show_clients_list(mock_message, mock_state, 1)
#     mock_message.answer.assert_called_once()
#     args, kwargs = mock_message.answer.call_args
#     assert "Выберите клиента" in kwargs['text']
#
#
# @pytest.mark.asyncio
# async def test_show_services_list(mock_message, mock_state, mock_terminal_api):
#     mock_state.get_data.return_value = {'customer_id': 1, 'container_size': 'large', 'container_state': 'loaded'}
#     mock_terminal_api.get_services.return_value = ([{'id': 1, 'service_type': {'name': 'Service 1'}}, {'id': 2, 'service_type': {'name': 'Service 2'}}], 40)
#     await show_services_list(mock_message, mock_state, 1)
#     mock_message.answer.assert_called_once()
#     args, kwargs = mock_message.answer.call_args
#     assert "Выберите дополнительные услуги" in kwargs['text']
#
#
# @pytest.mark.asyncio
# async def test_handle_pagination(mock_callback_query, mock_state):
#     mock_callback_query.data = "page_2"
#     await handle_pagination(mock_callback_query, mock_state)
#     mock_callback_query.answer.assert_called_once()
#
#
# @pytest.mark.asyncio
# async def test_handle_service_selection(mock_callback_query, mock_state):
#     mock_callback_query.data = "ss_Service1___1"
#     mock_state.get_data.return_value = {'selected_services': [], 'selected_service_names': []}
#     await handle_service_selection(mock_callback_query, mock_state)
#     mock_state.update_data.assert_called()
#     updated_data = mock_state.update_data.call_args_list[-1][1]
#     assert 1 in updated_data['selected_services']
#     assert "Service1" in updated_data['selected_service_names']
#
#
# @pytest.mark.asyncio
# async def test_handle_confirm_services(mock_callback_query, mock_state):
#     mock_state.get_data.return_value = {'selected_services': [1]}
#     await handle_confirm_services(mock_callback_query, mock_state)
#     mock_callback_query.answer.assert_not_called()
#     mock_callback_query.message.edit_text.assert_called_once()
#     args, kwargs = mock_callback_query.message.edit_text.call_args
#     assert "Подтвердить ✅ ?" in kwargs['text']
#
#
# @pytest.mark.asyncio
# async def test_handle_confirm(mock_callback_query, mock_state, mock_terminal_api):
#     mock_state.get_data.return_value = {
#         'container_size': 'large',
#         'container_name': 'TGHU1234567',
#         'container_state': 'loaded',
#         'customer_id': 1,
#         'container_owner': 'Owner X',
#         'transport_type': 'wagon',
#         'transport_number': '12345',
#         'date': '2024-10-20',
#         'selected_services': [1]
#     }
#     mock_terminal_api.register_container.return_value = [{'status': 'success'}, 201]
#     await handle_confirm(mock_callback_query, mock_state)
#     mock_callback_query.message.answer.assert_called_once_with("Заявка успешно создана!!", reply_markup=None)
#     mock_state.clear.assert_called_once()
#
#
# @pytest.mark.asyncio
# async def test_handle_transport_type(mock_callback_query, mock_state):
#     mock_callback_query.data = "wagon"
#     await handle_transport_type(mock_callback_query, mock_state)
#     mock_state.update_data.assert_called_with(transport_type="wagon")
#     mock_state.set_state.assert_called()
#     mock_callback_query.message.edit_text.assert_called_once()
#     args, kwargs = mock_callback_query.message.edit_text.call_args
#     assert "Введите номер Вагон:" in kwargs['text']
#
#
# @pytest.mark.asyncio
# async def test_get_container_name(mock_message, mock_state, mock_terminal_api):
#     mock_message.text = "TGHU1234567"
#     mock_terminal_api.get_container.return_value = ([{'exit_time': None}], 1)
#     await get_container_name(mock_message, mock_state)
#     mock_message.answer.assert_called_once_with("Контейнер с таким номером уже существует.")
#     mock_state.update_data.assert_not_called()
