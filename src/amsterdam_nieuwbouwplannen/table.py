from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING, Self

import msgspec

from .field_filter import FieldFilter
from .query import build_list_params, merge_filters, wire_names

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping, Sequence

    from ._types.sort import Sort
    from .enums import SortOrder
    from .http import HTTPClient
    from .models.page import Page

__all__ = ("Table",)


class Table[ModelT: msgspec.Struct, FiltersT: msgspec.Struct, FieldT: str]:
    """Query and export records from one Nieuwbouwplannen table.

    Parameters
    ----------
    http: :class:`~amsterdam_nieuwbouwplannen.http.HTTPClient`
        HTTP transport shared by the client's tables.
    name: :class:`str`
        Dataset table name used in request paths.
    model: :class:`type`[:obj:`ModelT`]
        Record struct whose Python and API field names are mapped.
    page_decoder: :class:`msgspec.json.Decoder`
        Decodes :class:`~amsterdam_nieuwbouwplannen.Page` objects for this table's record type.
    item_decoder: :class:`msgspec.json.Decoder`[:obj:`ModelT`]
        JSON decoder configured for a single record.
    default_crs: :class:`str` | :obj:`None`
        Output coordinate reference system used when the request omits one.
    """

    def __init__(
        self,
        http: HTTPClient,
        *,
        name: str,
        model: type[ModelT],
        page_decoder: msgspec.json.Decoder[Page[ModelT]],
        item_decoder: msgspec.json.Decoder[ModelT],
        default_crs: str | None = None,
    ) -> None:
        """Configure the table transport and its response decoders.

        Parameters
        ----------
        http: :class:`~amsterdam_nieuwbouwplannen.http.HTTPClient`
            HTTP transport shared by the client's tables.
        name: :class:`str`
            Dataset table name used in request paths.
        model: :class:`type`[:obj:`ModelT`]
            Record struct whose Python and API field names are mapped.
        page_decoder: :class:`msgspec.json.Decoder`
            Decodes :class:`~amsterdam_nieuwbouwplannen.Page` objects for this table's record type.
        item_decoder: :class:`msgspec.json.Decoder`[:obj:`ModelT`]
            JSON decoder configured for a single record.
        default_crs: :class:`str` | :obj:`None`
            Output coordinate reference system used when the request omits one.
        """

        self._http: HTTPClient = http
        self.name: str = name
        self.model: type[ModelT] = model
        self._page_decoder: msgspec.json.Decoder[Page[ModelT]] = page_decoder
        self._item_decoder: msgspec.json.Decoder[ModelT] = item_decoder
        self._names: dict[str, str] = wire_names(model)
        self.default_crs: str | None = default_crs
        self._filters: Mapping[str, object] = {}

    def __repr__(self) -> str:
        """Represent the table by its dataset name and record model.

        Returns
        -------
        :class:`str`
            String showing the table name and model class.
        """

        return f"<Table name={self.name!r} model={self.model.__name__}>"

    def where(self, filters: FiltersT | FieldFilter[FieldT]) -> Self:
        """Return a table with filters attached to its collection requests.

        Parameters
        ----------
        filters: :obj:`FiltersT` | :class:`~amsterdam_nieuwbouwplannen.FieldFilter`
            A filter model or a chain of comparisons for one field. A supplied field
            replaces any previous filter for that field.

        Returns
        -------
        :obj:`typing.Self`
            A new table sharing the original transport and decoders.

        Notes
        -----
        Filters apply to collection requests, including counts and exports.
        :meth:`get` looks up a record directly by ID.
        """

        table = copy(self)
        new_filters = filters.as_filters() if isinstance(filters, FieldFilter) else filters
        table._filters = merge_filters(self._filters, new_filters)
        return table

    def _crs(self, crs: str | None) -> str | None:
        return crs if crs is not None else self.default_crs

    async def list(
        self,
        *,
        filters: FiltersT | None = None,
        page: int = 1,
        page_size: int | None = None,
        sort: Mapping[FieldT, SortOrder] | Sequence[FieldT | Sort[FieldT]] | None = None,
        fields: Sequence[FieldT] | None = None,
        count: bool = False,
        crs: str | None = None,
        content_crs: str | None = None,
    ) -> Page[ModelT]:
        """Fetch a single page.

        Parameters
        ----------
        filters: :obj:`FiltersT` | :obj:`None`
            Field filters to apply to the request.
        page: :class:`int`
            One-based page number.
        page_size: :class:`int` | :obj:`None`
            Maximum number of records per page. :obj:`None` uses the API default.
        sort: :class:`~collections.abc.Mapping` | :class:`~collections.abc.Sequence` | :obj:`None`
            Field names or :class:`~amsterdam_nieuwbouwplannen.Sort` models in priority order.
            A bare field sorts ascending. A mapping pairs fields with sort directions.
        fields: :class:`collections.abc.Sequence`[:obj:`FieldT`] | :obj:`None`
            Fields to return. The record ID is always included.
        count: :class:`bool`
            Whether to request the total record and page counts.
        crs: :class:`str` | :obj:`None`
            Output coordinate reference system, for example EPSG:4326. By default, the
            table or API supplies it.
        content_crs: :class:`str` | :obj:`None`
            Coordinate reference system of the geometry filter operands.

        Returns
        -------
        :class:`~amsterdam_nieuwbouwplannen.Page`[:obj:`ModelT`]
            Decoded page containing records, links, and available pagination metadata.
        """

        params = build_list_params(
            names=self._names,
            filters=merge_filters(self._filters, filters),
            page=page,
            page_size=page_size,
            sort=sort,
            fields=fields,
            count=count,
        )
        body = await self._http.request(
            self.name, params=params, crs=self._crs(crs), content_crs=content_crs
        )
        return self._page_decoder.decode(body)

    async def iter_pages(
        self,
        *,
        filters: FiltersT | None = None,
        page_size: int | None = 100,
        sort: Mapping[FieldT, SortOrder] | Sequence[FieldT | Sort[FieldT]] | None = None,
        fields: Sequence[FieldT] | None = None,
        crs: str | None = None,
        content_crs: str | None = None,
    ) -> AsyncIterator[Page[ModelT]]:
        """Yield pages by following the API's next links.

        The initial request uses :meth:`list`.

        Parameters
        ----------
        filters: :obj:`FiltersT` | :obj:`None`
            Field filters to apply to the request.
        page_size: :class:`int` | :obj:`None`
            Maximum number of records per page. :obj:`None` uses the API default.
        sort: :class:`~collections.abc.Mapping` | :class:`~collections.abc.Sequence` | :obj:`None`
            Field names or :class:`~amsterdam_nieuwbouwplannen.Sort` models in priority order.
            A bare field sorts ascending. A mapping pairs fields with sort directions.
        fields: :class:`collections.abc.Sequence`[:obj:`FieldT`] | :obj:`None`
            Fields to return. The record ID is always included.
        crs: :class:`str` | :obj:`None`
            Output coordinate reference system, for example EPSG:4326. By default, the
            table or API supplies it.
        content_crs: :class:`str` | :obj:`None`
            Coordinate reference system of the geometry filter operands.

        Yields
        ------
        :class:`~amsterdam_nieuwbouwplannen.Page`[:obj:`ModelT`]
            Decoded page of matching records.
        """

        current = await self.list(
            filters=filters,
            page_size=page_size,
            sort=sort,
            fields=fields,
            crs=crs,
            content_crs=content_crs,
        )
        yield current
        while (next_url := current.next_url) is not None:
            body = await self._http.request(next_url, crs=self._crs(crs), content_crs=content_crs)
            current = self._page_decoder.decode(body)
            yield current

    async def iter(
        self,
        *,
        filters: FiltersT | None = None,
        page_size: int | None = 100,
        sort: Mapping[FieldT, SortOrder] | Sequence[FieldT | Sort[FieldT]] | None = None,
        fields: Sequence[FieldT] | None = None,
        limit: int | None = None,
        crs: str | None = None,
        content_crs: str | None = None,
    ) -> AsyncIterator[ModelT]:
        """Yield matching records across pages up to the optional limit.

        Parameters
        ----------
        filters: :obj:`FiltersT` | :obj:`None`
            Field filters to apply to the request.
        page_size: :class:`int` | :obj:`None`
            Maximum number of records per page. :obj:`None` uses the API default.
        sort: :class:`~collections.abc.Mapping` | :class:`~collections.abc.Sequence` | :obj:`None`
            Field names or :class:`~amsterdam_nieuwbouwplannen.Sort` models in priority order.
            A bare field sorts ascending. A mapping pairs fields with sort directions.
        fields: :class:`collections.abc.Sequence`[:obj:`FieldT`] | :obj:`None`
            Fields to return. The record ID is always included.
        limit: :class:`int` | :obj:`None`
            Maximum number of records to collect or yield. :obj:`None` has no limit.
        crs: :class:`str` | :obj:`None`
            Output coordinate reference system, for example EPSG:4326. By default, the
            table or API supplies it.
        content_crs: :class:`str` | :obj:`None`
            Coordinate reference system of the geometry filter operands.

        Yields
        ------
        :obj:`ModelT`
            Matching housing plan record.
        """

        if limit is not None and limit <= 0:
            return
        if limit is not None and page_size is not None:
            page_size = min(page_size, limit)
        yielded = 0
        async for page in self.iter_pages(
            filters=filters,
            page_size=page_size,
            sort=sort,
            fields=fields,
            crs=crs,
            content_crs=content_crs,
        ):
            for item in page.items:
                yield item
                yielded += 1
                if limit is not None and yielded >= limit:
                    return

    async def all(
        self,
        *,
        filters: FiltersT | None = None,
        sort: Mapping[FieldT, SortOrder] | Sequence[FieldT | Sort[FieldT]] | None = None,
        fields: Sequence[FieldT] | None = None,
        limit: int | None = None,
        crs: str | None = None,
    ) -> list[ModelT]:
        """Collect matching records across pages into a list.

        This method collects records from :meth:`iter`.

        Parameters
        ----------
        filters: :obj:`FiltersT` | :obj:`None`
            Field filters to apply to the request.
        sort: :class:`~collections.abc.Mapping` | :class:`~collections.abc.Sequence` | :obj:`None`
            Field names or :class:`~amsterdam_nieuwbouwplannen.Sort` models in priority order.
            A bare field sorts ascending. A mapping pairs fields with sort directions.
        fields: :class:`collections.abc.Sequence`[:obj:`FieldT`] | :obj:`None`
            Fields to return. The record ID is always included.
        limit: :class:`int` | :obj:`None`
            Maximum number of records to collect or yield. :obj:`None` has no limit.
        crs: :class:`str` | :obj:`None`
            Output coordinate reference system, for example EPSG:4326. By default, the
            table or API supplies it.

        Returns
        -------
        :class:`list`[:obj:`ModelT`]
            Matching housing plans in API order.
        """

        return [
            item
            async for item in self.iter(
                filters=filters, sort=sort, fields=fields, limit=limit, crs=crs
            )
        ]

    async def get(
        self,
        id: int,
        *,
        fields: Sequence[FieldT] | None = None,
        crs: str | None = None,
    ) -> ModelT:
        """Fetch a single housing plan by its record ID.

        Parameters
        ----------
        id: :class:`int`
            Unique identifier of the housing plan.
        fields: :class:`collections.abc.Sequence`[:obj:`FieldT`] | :obj:`None`
            Fields to return. The record ID is always included.
        crs: :class:`str` | :obj:`None`
            Output coordinate reference system, for example EPSG:4326. By default, the
            table or API supplies it.

        Returns
        -------
        :obj:`ModelT`
            Decoded housing plan record.

        Raises
        ------
        :class:`~amsterdam_nieuwbouwplannen.NotFound`
            No record has the requested identifier.
        """

        params = build_list_params(names=self._names, fields=fields)
        body = await self._http.request(f"{self.name}/{id}", params=params, crs=self._crs(crs))
        return self._item_decoder.decode(body)

    async def count(self, *, filters: FiltersT | None = None) -> int:
        """Count records matching the supplied filters.

        Parameters
        ----------
        filters: :obj:`FiltersT` | :obj:`None`
            Field filters to apply to the request.

        Returns
        -------
        :class:`int`
            Total count supplied by the API, or the number of records in the response when
            no total is available.
        """

        params = build_list_params(
            names=self._names,
            filters=merge_filters(self._filters, filters),
            page_size=1,
            fields=["id"],
            count=True,
        )
        page = self._page_decoder.decode(await self._http.request(self.name, params=params))
        if page.page is None or page.page.total_elements is None:
            return len(page)
        return page.page.total_elements

    async def export_csv(
        self,
        *,
        filters: FiltersT | None = None,
        sort: Mapping[FieldT, SortOrder] | Sequence[FieldT | Sort[FieldT]] | None = None,
        fields: Sequence[FieldT] | None = None,
        content_crs: str | None = None,
    ) -> bytes:
        """Fetch the unpaginated CSV export.

        Parameters
        ----------
        filters: :obj:`FiltersT` | :obj:`None`
            Field filters to apply to the request.
        sort: :class:`~collections.abc.Mapping` | :class:`~collections.abc.Sequence` | :obj:`None`
            Field names or :class:`~amsterdam_nieuwbouwplannen.Sort` models in priority order.
            A bare field sorts ascending. A mapping pairs fields with sort directions.
        fields: :class:`collections.abc.Sequence`[:obj:`FieldT`] | :obj:`None`
            Fields to return. The record ID is always included.

        content_crs: :class:`str` | :obj:`None`
            Coordinate reference system of the geometry filter operands.

        Returns
        -------
        :class:`bytes`
            CSV response body.
        """

        params = build_list_params(
            names=self._names,
            filters=merge_filters(self._filters, filters),
            sort=sort,
            fields=fields,
            format="csv",
        )
        return await self._http.request(
            self.name, params=params, accept="text/csv", content_crs=content_crs
        )

    async def export_geojson(
        self,
        *,
        filters: FiltersT | None = None,
        sort: Mapping[FieldT, SortOrder] | Sequence[FieldT | Sort[FieldT]] | None = None,
        fields: Sequence[FieldT] | None = None,
        crs: str | None = None,
        content_crs: str | None = None,
    ) -> bytes:
        """Fetch the unpaginated GeoJSON FeatureCollection.

        Parameters
        ----------
        filters: :obj:`FiltersT` | :obj:`None`
            Field filters to apply to the request.
        sort: :class:`~collections.abc.Mapping` | :class:`~collections.abc.Sequence` | :obj:`None`
            Field names or :class:`~amsterdam_nieuwbouwplannen.Sort` models in priority order.
            A bare field sorts ascending. A mapping pairs fields with sort directions.
        fields: :class:`collections.abc.Sequence`[:obj:`FieldT`] | :obj:`None`
            Fields to return. The record ID is always included.
        crs: :class:`str` | :obj:`None`
            Output coordinate reference system, for example EPSG:4326. By default, the
            table or API supplies it.

        content_crs: :class:`str` | :obj:`None`
            Coordinate reference system of the geometry filter operands.

        Returns
        -------
        :class:`bytes`
            GeoJSON response body.
        """

        params = build_list_params(
            names=self._names,
            filters=merge_filters(self._filters, filters),
            sort=sort,
            fields=fields,
            format="geojson",
        )
        return await self._http.request(
            self.name,
            params=params,
            accept="application/geo+json",
            crs=self._crs(crs),
            content_crs=content_crs,
        )
