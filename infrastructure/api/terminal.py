from aiogram.client.session import aiohttp


class TerminalAPI:
    API_URL = "https://terminal.danke.uz/"
    PER_PAGE = 8

    async def fetch_data(self, url: str, params: dict = None) -> tuple[list, int]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('results', []), data.get('count', 0)
        return [], 0

    async def get_clients(self, offset: int, limit: int) -> tuple[list, int]:
        return await self.fetch_data(f"{self.API_URL}customers/list/", params={'offset': offset, 'limit': limit})

    async def get_services(self, offset: int, limit: int,
                           customer_id: int,
                           container_size: str,
                           container_state: str) -> tuple[list, int]:
        params = {'offset': offset, 'limit': limit}
        if container_size:
            params['container_size'] = container_size
        if container_state:
            params['container_state'] = container_state

        return await self.fetch_data(
            f"{self.API_URL}customers/contracts/services/by_company/active/{customer_id}/",
            params=params
        )

    async def get_container(self, container_name: str) -> tuple[list, int]:
        return await self.fetch_data(
            f"{self.API_URL}containers/containers_visit_list/",
            params={'container_name': container_name}
        )

    async def register_container(self, data: dict) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Content-Type': 'application/json'}
                async with session.post(f"{self.API_URL}containers/container_visit_register/", json=data,
                                        headers=headers) as resp:
                    resp_json = await resp.json()
                    return resp.status == 201
        except aiohttp.ClientError as e:
            print(f"Client error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return False

    async def add_photo(self, container_id: int, data: aiohttp.FormData) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.API_URL}containers/files/container_visit/{container_id}/image/create/",
                                        data=data) as resp:
                    resp_json = await resp.json()
                    return resp.status == 201
        except aiohttp.ClientError as e:
            print(f"Client error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return False

    async def add_document(self, container_id: int, data: aiohttp.FormData) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.API_URL}containers/files/container_visit/{container_id}/document/create/",
                        data=data) as resp:
                    resp_json = await resp.json()
                    return resp.status == 201
        except aiohttp.ClientError as e:
            print(f"Client error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return False

    async def get_photos(self, container_id: str) -> list:
        async with aiohttp.ClientSession() as session:
            url = f"{self.API_URL}containers/files/container_visit/{container_id}/images/download/"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    return []

    async def get_documents(self, container_id: str) -> list:
        async with aiohttp.ClientSession() as session:
            url = f"{self.API_URL}containers/files/container_visit/{container_id}/documents/download/"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    return []

    async def get_statistics(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.API_URL}containers/container_visit_statistics/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    return {}
