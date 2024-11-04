from aiogram.fsm.state import StatesGroup, State


class TerminalImport(StatesGroup):
    container_size = State()
    container_name = State()
    container_state = State()
    product_name = State("")
    request_type = State()
    customer_name = State()
    customer_id = State()
    contract_id = State()
    container_owner = State()
    date = State()
    transport_type = State()
    transport_number = State()
    selected_services = State()
    selected_service_names = State()
    confirmation = State()
    add_photo = State()


class TerminalDocument(StatesGroup):
    container_number = State()
    container_id = State()
    photo = State()
    document = State()
