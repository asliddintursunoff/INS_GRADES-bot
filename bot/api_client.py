from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Dict, Tuple

import httpx


@dataclass(frozen=True)
class ApiError(Exception):
    status_code: int
    detail: str

    def __str__(self) -> str:
        return f"ApiError(status={self.status_code}, detail={self.detail})"


class BackendClient:
    """
    Safe HTTP client for your backend.

    Key fix:
    - prevents bot crashes on intermittent backend/network issues
      (httpx.ReadError, timeouts, disconnects, etc.)
    - register_user() returns (status_code, body) even on network failure:
        -> (503, {"detail": "BACKEND_UNAVAILABLE"})
    """

    def __init__(self, base_url: str, timeout_seconds: float = 25.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "BackendClient":
        # Split timeouts to reduce ReadError crashes on slow responses
        timeout = httpx.Timeout(
            connect=min(5.0, self.timeout_seconds),
            read=self.timeout_seconds,
            write=min(10.0, self.timeout_seconds),
            pool=min(5.0, self.timeout_seconds),
        )
        limits = httpx.Limits(max_connections=50, max_keepalive_connections=20)

        self._client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            follow_redirects=False,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("BackendClient not initialized. Use 'async with BackendClient(...)'.")
        return self._client

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _try_json(self, resp: httpx.Response) -> Dict[str, Any]:
        try:
            data = resp.json()
            return data if isinstance(data, dict) else {"detail": str(data)}
        except Exception:
            return {"detail": (resp.text or f"HTTP {resp.status_code}")}

    async def _parse_detail(self, resp: httpx.Response) -> str:
        try:
            data = resp.json()
            if isinstance(data, dict) and "detail" in data:
                return str(data["detail"])
        except Exception:
            pass
        return resp.text or f"HTTP {resp.status_code}"

    async def _safe_get(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
        """
        GET wrapper that never raises httpx network exceptions.
        Returns (status_code, json_body).
        """
        try:
            resp = await self.client.get(self._url(path), params=params)
            return resp.status_code, self._try_json(resp)
        except (httpx.ReadError, httpx.ReadTimeout, httpx.ConnectError, httpx.ConnectTimeout, httpx.RemoteProtocolError):
            return 503, {"detail": "BACKEND_UNAVAILABLE"}

    async def _safe_post(self, path: str, *, json: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
        """
        POST wrapper that never raises httpx network exceptions.
        Returns (status_code, json_body).
        NOTE: no retries here (POST may not be safe to retry).
        """
        try:
            resp = await self.client.post(self._url(path), json=json)
            return resp.status_code, self._try_json(resp)
        except (httpx.ReadError, httpx.ReadTimeout, httpx.ConnectError, httpx.ConnectTimeout, httpx.RemoteProtocolError):
            return 503, {"detail": "BACKEND_UNAVAILABLE"}

    # -------------------- Public API --------------------

    async def get_user_info(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        status, body = await self._safe_get("/user/get-user-info", params={"telegram_id": telegram_id})
        if status == 503:
            raise ApiError(503, body.get("detail", "BACKEND_UNAVAILABLE"))
        if status == 404:
            return None
        if status != 200:
            raise ApiError(status, body.get("detail", f"HTTP {status}"))
        return body

    async def get_user_type(self, telegram_id: str) -> str:
        status, body = await self._safe_get("/user/user_type", params={"telegram_id": telegram_id})
        if status == 503:
            raise ApiError(503, body.get("detail", "BACKEND_UNAVAILABLE"))
        if status != 200:
            raise ApiError(status, body.get("detail", f"HTTP {status}"))
        return str(body.get("user_type") or "new_user")

    async def register_user(self, telegram_id: str, student_id: str) -> Tuple[int, Dict[str, Any]]:
        """
        Returns (status_code, json_body).
        Special backend flow:
          - 200: registered half user
          - 300: "user must register with password"
        Fix:
          - if backend/network breaks, returns 503 instead of crashing the bot
        """
        status, body = await self._safe_post(
            "/user/register-user",
            json={"telegram_id": telegram_id, "student_id": student_id},
        )

        # allow your existing flows
        if status in (200, 300, 503):
            return status, body

        raise ApiError(status, str(body.get("detail") or f"HTTP {status}"))

    async def register_eclass(self, telegram_id: str, student_id: str, password: str) -> Dict[str, Any]:
        status, body = await self._safe_get(
            "/user/register-user-eclass-and-load-data",
            params={"student_id": student_id, "password": password, "telegram_id": telegram_id},
        )
        if status == 503:
            raise ApiError(503, body.get("detail", "BACKEND_UNAVAILABLE"))
        if status != 200:
            raise ApiError(status, body.get("detail", f"HTTP {status}"))
        return body

    async def get_timetable(self, telegram_id: str) -> Dict[str, Any]:
        status, body = await self._safe_get("/my-timetable", params={"telegram_id": telegram_id})
        if status == 503:
            raise ApiError(503, body.get("detail", "BACKEND_UNAVAILABLE"))
        if status != 200:
            raise ApiError(status, body.get("detail", f"HTTP {status}"))
        return body

    async def get_eclass_info(self, telegram_id: str) -> Dict[str, Any]:
        status, body = await self._safe_get("/e-class/get-my-attendance", params={"telegram_id": telegram_id})
        if status == 503:
            raise ApiError(503, body.get("detail", "BACKEND_UNAVAILABLE"))
        if status != 200:
            raise ApiError(status, body.get("detail", f"HTTP {status}"))
        return body
