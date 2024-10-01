import asyncio
import os
import sys

import pytest

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from infrastructure.api.terminal import TerminalAPI


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def api():
    return TerminalAPI()


@pytest.mark.asyncio
async def test_get_clients(api):
    clients, count = await api.get_clients(offset=0, limit=5)
    assert isinstance(clients, list), "get_clients should return a list"
    assert isinstance(count, int), "get_clients count should be an integer"
    assert len(clients) <= 5, "get_clients should respect the limit parameter"
    if clients:
        assert isinstance(clients[0], dict), "Each client should be a dictionary"


@pytest.mark.asyncio
async def test_get_services(api):
    # You may need to replace this with a valid customer_id from your database
    customer_id = 1
    services, count = await api.get_services(
        offset=0,
        limit=5,
        customer_id=customer_id,
        container_size="20",
        container_state="empty"
    )
    assert isinstance(services, list), "get_services should return a list"
    assert isinstance(count, int), "get_services count should be an integer"
    assert len(services) <= 5, "get_services should respect the limit parameter"
    if services:
        assert isinstance(services[0], dict), "Each service should be a dictionary"


@pytest.mark.asyncio
async def test_fetch_data(api):
    # Test with a known endpoint
    data, count = await api.fetch_data(f"{api.API_URL}customers/list/", params={'offset': 0, 'limit': 1})
    assert isinstance(data, list), "fetch_data should return a list as the first item of the tuple"
    assert isinstance(count, int), "fetch_data should return an integer as the second item of the tuple"


@pytest.mark.asyncio
async def test_get_containers(api, container_name="TGHU1234567"):
    containers, count = await api.get_container(container_name)
    assert isinstance(containers, list), "get_containers should return a list"
    assert isinstance(count, int), "get_containers count should be an integer"
    if containers:
        assert isinstance(containers[0], dict), "Each container should be a dictionary"

