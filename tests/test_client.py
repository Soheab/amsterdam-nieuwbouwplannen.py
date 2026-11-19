from __future__ import annotations

from typing import TYPE_CHECKING, Any

import msgspec
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from amsterdam_nieuwbouwplannen import (
    BadRequest,
    Client,
    Forbidden,
    IntFilter,
    NotFound,
    PlanField,
    PlanFilters,
    Sort,
    SortOrder,
    Stadsdeel,
)

from .fixtures import TABLE, page, plan

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

PREFIX = "/v1/nieuwbouwplannen"


class Recorder:
    def __init__(self) -> None:
        self.requests: list[web.Request] = []


def _json(body: Any, status: int = 200, content_type: str = "application/hal+json") -> web.Response:
    return web.Response(body=msgspec.json.encode(body), status=status, content_type=content_type)


def _problem(status: int, title: str, **extra: Any) -> web.Response:
    return _json(
        {"type": "urn:apiexception:x", "title": title, "status": status, **extra},
        status=status,
        content_type="application/problem+json",
    )


@pytest.fixture
async def server() -> AsyncIterator[tuple[TestServer, Recorder]]:
    recorder = Recorder()
    srv: TestServer

    async def list_view(request: web.Request) -> web.Response:
        recorder.requests.append(request)
        fmt = request.query.get("_format")
        if fmt == "csv":
            return web.Response(text="id,totaal\r\n1,10\r\n", content_type="text/csv")
        if fmt == "geojson":
            return _json(
                {"type": "FeatureCollection", "features": []}, content_type="application/geo+json"
            )
        if "bogus" in request.query:
            return _problem(
                400,
                "Invalid filter",
                **{"invalid-params": [{"name": "bogus", "reason": "Unknown"}]},
            )
        number = int(request.query.get("page", "1"))
        size = int(request.query.get("_pageSize", "20"))
        all_ids = list(range(1, 6))  # 5 records in the "dataset"
        chunk = all_ids[(number - 1) * size : number * size]
        has_next = number * size < len(all_ids)
        next_href = (
            str(srv.make_url(f"{PREFIX}/{TABLE}/?page={number + 1}&_pageSize={size}"))
            if has_next
            else None
        )
        total = len(all_ids) if request.query.get("_count") == "true" else None
        return _json(
            page(
                [plan(i) for i in chunk], number=number, size=size, next_href=next_href, total=total
            )
        )

    async def detail_view(request: web.Request) -> web.Response:
        recorder.requests.append(request)
        id = int(request.match_info["id"])
        if id == 404:
            return _problem(404, "Not found")
        return _json(plan(id))

    async def kwartaal_view(request: web.Request) -> web.Response:
        recorder.requests.append(request)
        if request.headers.get("Authorization") != "Bearer good":
            return _problem(403, "Forbidden", detail="Scope BB/WB/GO/UITG required")
        return _json(page([plan(9, idPrimavera="P-9")]))

    app = web.Application()
    app.router.add_get(f"{PREFIX}/{TABLE}", list_view)
    app.router.add_get(f"{PREFIX}/{TABLE}/", list_view)
    app.router.add_get(f"{PREFIX}/{TABLE}/{{id}}", detail_view)
    app.router.add_get(f"{PREFIX}/woningbouwplannen_kwartaal_uitgebreid", kwartaal_view)
    srv = TestServer(app)
    await srv.start_server()
    try:
        yield srv, recorder
    finally:
        await srv.close()


@pytest.fixture
async def client(server: tuple[TestServer, Recorder]) -> AsyncIterator[Client]:
    srv, _ = server
    async with Client(
        base_url=str(srv.make_url(PREFIX)), api_key="key123", crs="EPSG:4326"
    ) as client:
        yield client


async def test_list_sends_params_and_headers(
    client: Client, server: tuple[TestServer, Recorder]
) -> None:
    _, recorder = server
    result = await client.openbaar.list(
        filters=PlanFilters(stadsdeel=Stadsdeel.NOORD, totaal=IntFilter(gte=100)),
        sort=[Sort(PlanField.START_BOUW_GEPLAND, SortOrder.DESC)],
        page_size=2,
        count=True,
    )
    assert [p.id for p in result.items] == [1, 2]
    assert result.page is not None
    assert result.page.total_elements == 5
    request = recorder.requests[-1]
    assert request.query["stadsdeelCode"] == "N"
    assert request.query["totaal[gte]"] == "100"
    assert request.query["_sort"] == "-startBouwGepland"
    assert request.headers["X-Api-Key"] == "key123"
    assert request.headers["Accept-Crs"] == "EPSG:4326"
    assert "Authorization" not in request.headers


async def test_where_reuses_filters_without_changing_source_table(
    client: Client, server: tuple[TestServer, Recorder]
) -> None:
    _, recorder = server
    noord = client.openbaar.where(PlanFilters(stadsdeel=Stadsdeel.NOORD))
    minimum = PlanField.TOTAAL.filter.greater_than_or_equal_to(100)
    assert minimum == PlanField.TOTAAL.filter.gte(100)
    large = noord.where(minimum.less_than(500)).where(PlanField.WIJK_NAAM.filter.equal_to("IJburg"))

    await large.all(limit=2)
    assert recorder.requests[-1].query["stadsdeelCode"] == "N"
    assert recorder.requests[-1].query["totaal[gte]"] == "100"

    assert recorder.requests[-1].query["totaal[lt]"] == "500"
    assert recorder.requests[-1].query["wijkNaam"] == "IJburg"

    await noord.where(minimum).count()
    assert "totaal[lt]" not in recorder.requests[-1].query

    await large.export_csv(filters=PlanFilters(totaal=IntFilter(gte=200)))
    assert recorder.requests[-1].query["stadsdeelCode"] == "N"
    assert recorder.requests[-1].query["totaal[gte]"] == "200"

    await noord.count()
    assert recorder.requests[-1].query["stadsdeelCode"] == "N"
    assert "totaal[gte]" not in recorder.requests[-1].query

    await client.openbaar.count()
    assert "stadsdeelCode" not in recorder.requests[-1].query


async def test_iter_follows_next_links(client: Client) -> None:
    ids = [p.id async for p in client.openbaar.iter(page_size=2)]
    assert ids == [1, 2, 3, 4, 5]


async def test_iter_limit(client: Client) -> None:
    assert [p.id for p in await client.openbaar.all(limit=3)] == [1, 2, 3]


async def test_iter_pages(client: Client) -> None:
    sizes = [len(p) async for p in client.openbaar.iter_pages(page_size=2)]
    assert sizes == [2, 2, 1]


async def test_get(client: Client) -> None:
    record = await client.openbaar.get(1041)
    assert record.id == 1041
    assert record.projectnaam_afkorting == "NDSM Kavel B7"


async def test_get_not_found(client: Client) -> None:
    with pytest.raises(NotFound) as info:
        await client.openbaar.get(404)
    assert info.value.status == 404
    assert info.value.problem is not None
    assert info.value.problem.title == "Not found"


async def test_count(client: Client) -> None:
    assert await client.openbaar.count() == 5


async def test_bad_request_has_invalid_params(client: Client) -> None:
    with pytest.raises(BadRequest) as info:
        await client.http.request(TABLE, params=[("bogus", "1")])
    assert info.value.problem is not None
    assert info.value.problem.invalid_params is not None
    assert info.value.problem.invalid_params[0].name == "bogus"


async def test_exports(client: Client) -> None:
    assert (await client.openbaar.export_csv()).startswith(b"id,totaal")
    assert b"FeatureCollection" in await client.openbaar.export_geojson()


async def test_kwartaal_needs_token(client: Client) -> None:
    with pytest.raises(Forbidden):
        await client.kwartaal_uitgebreid.list()
    client.access_token = "good"
    result = await client.kwartaal_uitgebreid.list()
    assert result.items[0].id_primavera == "P-9"
