from __future__ import annotations

import datetime

import msgspec

from amsterdam_nieuwbouwplannen import (
    Page,
    Stadsdeel,
    WoningbouwplanKwartaalUitgebreid,
    WoningbouwplanOpenbaar,
)

from .fixtures import page, plan


def test_decode_record() -> None:
    record = msgspec.json.decode(msgspec.json.encode(plan(1041)), type=WoningbouwplanOpenbaar)
    assert record.id == 1041
    assert record.stadsdeel is Stadsdeel.NOORD
    assert record.stadsdeel_naam == "Noord"
    assert record.start_bouw_gepland == datetime.date(2026, 3, 23)
    assert record.started
    assert record.totaal == 207
    assert record.jongeren == "0"
    assert record.geometrie is not None
    assert record.geometrie.type == "MultiPolygon"
    assert record.links is not None
    assert record.links.self_ is not None
    assert record.links.self_.id == 1041


def test_decode_sparse_record() -> None:
    record = msgspec.json.decode(b'{"id": 5}', type=WoningbouwplanOpenbaar)
    assert record.id == 5
    assert record.totaal is None
    assert not record.started


def test_counts_accept_int_and_str() -> None:
    record = msgspec.json.decode(
        msgspec.json.encode(plan(1, jongeren=12, studenten="3")), type=WoningbouwplanOpenbaar
    )
    assert record.jongeren == 12
    assert record.studenten == "3"


def test_unknown_fields_are_ignored() -> None:
    record = msgspec.json.decode(
        msgspec.json.encode(plan(1, nieuwVeld="x")), type=WoningbouwplanOpenbaar
    )
    assert record.id == 1


def test_uitgebreid_extra_fields() -> None:
    body = plan(7, idPrimavera="P-123", grex="GX1", opleveringGepland="2029-12-31")
    record = msgspec.json.decode(msgspec.json.encode(body), type=WoningbouwplanKwartaalUitgebreid)
    assert record.id_primavera == "P-123"
    assert record.oplevering_gepland == datetime.date(2029, 12, 31)


def test_decode_page() -> None:
    body = page([plan(1), plan(2)], next_href="https://x/?page=2", total=45)
    result = msgspec.json.decode(msgspec.json.encode(body), type=Page[WoningbouwplanOpenbaar])
    assert [p.id for p in result.items] == [1, 2]
    assert len(result) == 2
    assert result.has_next
    assert result.next_url == "https://x/?page=2"
    assert result.previous_url is None
    assert result.page is not None
    assert result.page.total_elements == 45
    assert result.page.total_pages == 3


def test_decode_last_page_without_next() -> None:
    body = page([plan(1)])
    del body["_links"]["next"]
    result = msgspec.json.decode(msgspec.json.encode(body), type=Page[WoningbouwplanOpenbaar])
    assert not result.has_next
