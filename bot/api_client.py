import aiohttp
from typing import Any, Dict, Optional, Tuple
from bot.config import API_BASE_URL

class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        session = await self.get_session()
        async with session.get(f"{self.base_url}/api/v1/user/{telegram_id}") as response:
            if response.status == 200:
                return await response.json()
            return None

    async def register_user(self, telegram_id: int, student_id: str) -> bool:
        session = await self.get_session()
        payload = {
            "telegram_id": str(telegram_id),
            "student_id": student_id
        }
        async with session.post(f"{self.base_url}/api/v1/user/", json=payload) as response:
            return response.status == 200 or response.status == 201

    async def get_timetable(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        session = await self.get_session()
        async with session.get(f"{self.base_url}/api/v1/timetable/{telegram_id}") as response:
            if response.status == 200:
                return await response.json()
            return None

    async def get_assignments(self, telegram_id: int) -> Tuple[int, Any]:
        session = await self.get_session()
        async with session.get(f"{self.base_url}/api/v1/assignment/available/{telegram_id}") as response:
            try:
                data = await response.json()
            except:
                data = await response.text()
            return response.status, data

    async def check_payment(self, telegram_id: int, file_bytes: bytes, filename: str) -> Tuple[bool, Any]:
        session = await self.get_session()
        data = aiohttp.FormData()
        data.add_field("telegram_id", str(telegram_id))
        data.add_field("file", file_bytes, filename=filename, content_type="image/jpeg")

        async with session.post(f"{self.base_url}/api/v1/transaction/check", data=data) as response:
            try:
                resp_data = await response.json()
            except:
                resp_data = await response.text()
            return response.status == 200, resp_data
