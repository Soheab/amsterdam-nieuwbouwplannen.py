from __future__ import annotations

from typing import TYPE_CHECKING, Self

import aiohttp
import msgspec

from . import __version__
from .errors import (
    BadRequest,
    Forbidden,
    HTTPException,
    NotFound,
    RateLimited,
    ServerError,
    Unauthorized,
)
from .models.problem import ProblemDetails

if TYPE_CHECKING:
    from types import TracebackType

    from .query import QueryParams

__all__ = ("DEFAULT_BASE_URL", "HTTPClient")

DEFAULT_BASE_URL = "https://api.data.amsterdam.nl/v1/nieuwbouwplannen"
USER_AGENT = f"amsterdam-nieuwbouwplannen.py/{__version__}"

_problem_decoder = msgspec.json.Decoder(ProblemDetails)

_ERRORS: dict[int, type[HTTPException]] = {
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound,
    429: RateLimited,
}


class HTTPClient:
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        access_token: str | None = None,
        session: aiohttp.ClientSession | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url: str = base_url.rstrip("/")
        self.api_key: str | None = api_key
        self.access_token: str | None = access_token
        self._session: aiohttp.ClientSession | None = session
        self._owns_session: bool = session is None
        self._timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=timeout)

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
            self._owns_session = True
        return self._session

    def url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _headers(self, accept: str, crs: str | None, content_crs: str | None) -> dict[str, str]:
        headers = {"Accept": accept, "User-Agent": USER_AGENT}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        if crs:
            headers["Accept-Crs"] = crs
        if content_crs:
            headers["Content-Crs"] = content_crs
        return headers

    async def request(
        self,
        path: str,
        *,
        params: QueryParams | None = None,
        accept: str = "application/hal+json",
        crs: str | None = None,
        content_crs: str | None = None,
    ) -> bytes:
        async with self.session.get(
            self.url(path),
            params=params or None,
            headers=self._headers(accept, crs, content_crs),
        ) as response:
            body = await response.read()
            if response.status < 400:
                return body
            raise self._error(response.status, body)

    @staticmethod
    def _error(status: int, body: bytes) -> HTTPException:
        try:
            problem: ProblemDetails | None = _problem_decoder.decode(body)
        except msgspec.DecodeError:
            problem = None
        cls = _ERRORS.get(status, ServerError if status >= 500 else HTTPException)
        return cls(status, problem, body)

    async def close(self) -> None:
        if self._owns_session and self._session is not None and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()
