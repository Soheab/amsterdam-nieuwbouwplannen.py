from __future__ import annotations

import os
from functools import cached_property
from typing import TYPE_CHECKING, Self

import msgspec

from .http import DEFAULT_BASE_URL, HTTPClient
from .models.page import Page
from .models.plans import (
    WoningbouwplanKwartaalStandaard,
    WoningbouwplanKwartaalUitgebreid,
    WoningbouwplanOpenbaar,
)
from .table import Table

if TYPE_CHECKING:
    from types import TracebackType

    import aiohttp

    from ._types.filters import KwartaalUitgebreidFilters, PlanFilters
    from .enums import KwartaalUitgebreidField, PlanField

__all__ = (
    "API_KEY_ENV",
    "Client",
)

API_KEY_ENV = "DATA_AMSTERDAM_API_KEY"
"""Environment variable read for the API key when none is passed."""


class Client:
    """Access Amsterdam's Nieuwbouwplannen tables asynchronously.

    Parameters
    ----------
    api_key: :class:`str` | :obj:`None`
        Key sent in the X-Api-Key header.
    access_token: :class:`str` | :obj:`None`
        OAuth bearer token for the protected quarterly tables.
    session: :class:`aiohttp.ClientSession` | :obj:`None`
        Existing aiohttp session to reuse. The client closes sessions it creates.
    crs: :class:`str` | :obj:`None`
        Output coordinate reference system, for example EPSG:4326. By default, the
        table or API supplies it.
    base_url: :class:`str`
        Base URL of the Nieuwbouwplannen dataset.
    timeout: :class:`float`
        Total request timeout in seconds for a new session.

    Attributes
    ----------
    openbaar: :class:`~amsterdam_nieuwbouwplannen.Table`
        Public plans table.
    kwartaal_standaard: :class:`~amsterdam_nieuwbouwplannen.Table`
        Standard quarterly table requiring scope BB/WB/GO/STAN.
    kwartaal_uitgebreid: :class:`~amsterdam_nieuwbouwplannen.Table`
        Extended quarterly table requiring scope BB/WB/GO/UITG.

    Notes
    -----
    If api_key is omitted, the client reads DATA_AMSTERDAM_API_KEY.
    Each table is created on first access and cached for this client.

    Examples
    --------
    >>> from amsterdam_nieuwbouwplannen import Client
    >>> client = Client()

    Use the client in an asynchronous context::

        async with Client() as client:
            page = await client.openbaar.list(page_size=5)
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        access_token: str | None = None,
        session: aiohttp.ClientSession | None = None,
        crs: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        """Configure credentials and the shared HTTP transport.

        Parameters
        ----------
        api_key: :class:`str` | :obj:`None`
            Key sent in the X-Api-Key header.
        access_token: :class:`str` | :obj:`None`
            OAuth bearer token for the protected quarterly tables.
        session: :class:`aiohttp.ClientSession` | :obj:`None`
            Existing aiohttp session to reuse. The client closes sessions it creates.
        crs: :class:`str` | :obj:`None`
            Output coordinate reference system, for example EPSG:4326. By default, the
            table or API supplies it.
        base_url: :class:`str`
            Base URL of the Nieuwbouwplannen dataset.
        timeout: :class:`float`
            Total request timeout in seconds for a new session.
        """

        self.http: HTTPClient = HTTPClient(
            base_url=base_url,
            api_key=api_key if api_key is not None else os.environ.get(API_KEY_ENV),
            access_token=access_token,
            session=session,
            timeout=timeout,
        )

        self._default_crs = crs

    @cached_property
    def openbaar(self) -> Table[WoningbouwplanOpenbaar, PlanFilters, PlanField]:
        """Get the public plans table, which is available without authorization."""

        return Table(
            self.http,
            name="woningbouwplannen_openbaar",
            model=WoningbouwplanOpenbaar,
            page_decoder=msgspec.json.Decoder(Page[WoningbouwplanOpenbaar]),
            item_decoder=msgspec.json.Decoder(WoningbouwplanOpenbaar),
            default_crs=self._default_crs,
        )

    @cached_property
    def kwartaal_standaard(self) -> Table[WoningbouwplanKwartaalStandaard, PlanFilters, PlanField]:
        """Get the standard quarterly table, which requires scope ``BB/WB/GO/STAN``."""

        return Table(
            self.http,
            name="woningbouwplannen_kwartaal_standaard",
            model=WoningbouwplanKwartaalStandaard,
            page_decoder=msgspec.json.Decoder(Page[WoningbouwplanKwartaalStandaard]),
            item_decoder=msgspec.json.Decoder(WoningbouwplanKwartaalStandaard),
            default_crs=self._default_crs,
        )

    @cached_property
    def kwartaal_uitgebreid(
        self,
    ) -> Table[
        WoningbouwplanKwartaalUitgebreid,
        KwartaalUitgebreidFilters,
        PlanField | KwartaalUitgebreidField,
    ]:
        """Get the extended quarterly table, which requires scope ``BB/WB/GO/UITG``."""

        return Table(
            self.http,
            name="woningbouwplannen_kwartaal_uitgebreid",
            model=WoningbouwplanKwartaalUitgebreid,
            page_decoder=msgspec.json.Decoder(Page[WoningbouwplanKwartaalUitgebreid]),
            item_decoder=msgspec.json.Decoder(WoningbouwplanKwartaalUitgebreid),
            default_crs=self._default_crs,
        )

    @property
    def api_key(self) -> str | None:
        """Get the API key used for requests.

        Returns
        -------
        :class:`str` | :obj:`None`
            API key, or :obj:`None` when no key is configured.
        """

        return self.http.api_key

    @api_key.setter
    def api_key(self, value: str | None) -> None:
        """Update the API key used for requests.

        Parameters
        ----------
        value: :class:`str` | :obj:`None`
            Key sent in the X-Api-Key header. Pass :obj:`None` to clear it.
        """

        self.http.api_key = value

    @property
    def access_token(self) -> str | None:
        """Get the OAuth bearer token used for protected requests.

        Returns
        -------
        :class:`str` | :obj:`None`
            Bearer token, or :obj:`None` when no token is configured.
        """

        return self.http.access_token

    @access_token.setter
    def access_token(self, value: str | None) -> None:
        """Update the OAuth bearer token used for requests.

        Parameters
        ----------
        value: :class:`str` | :obj:`None`
            OAuth bearer token for the protected quarterly tables. Pass :obj:`None` to clear it.
        """

        self.http.access_token = value

    async def close(self) -> None:
        """Close the HTTP session owned by this instance, if open."""

        await self.http.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()
