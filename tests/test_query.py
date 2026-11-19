from __future__ import annotations

import datetime

from amsterdam_nieuwbouwplannen import (
    DateFilter,
    GeoFilter,
    IntFilter,
    KwartaalUitgebreidField,
    KwartaalUitgebreidFilters,
    PlanField,
    PlanFilters,
    Sort,
    SortOrder,
    Stadsdeel,
    StrFilter,
    WoningbouwplanKwartaalUitgebreid,
    WoningbouwplanOpenbaar,
)
from amsterdam_nieuwbouwplannen.query import build_filters, build_list_params, wire_names

NAMES = wire_names(WoningbouwplanOpenbaar)


def test_plain_and_operator_filters() -> None:
    filters = PlanFilters(
        id=IntFilter(eq=1041),
        buurt_code=StrFilter(in_=["N73b", "N73c"]),
        wijk_naam=StrFilter(like="IJburg*", not_="IJburg West"),
        stadsdeel_code=Stadsdeel.NOORD.code,
        stadsdeel_naam=Stadsdeel.NOORD,
        start_bouw_gepland=DateFilter(gte=datetime.date(2027, 1, 1)),
        start_bouw_gerealiseerd=DateFilter(isnull=False),
        totaal=IntFilter(gte=0, lt=500),
    )
    assert build_filters(filters, NAMES) == [
        ("id", "1041"),
        ("buurtCode[in]", "N73b,N73c"),
        ("wijkNaam[not]", "IJburg West"),
        ("wijkNaam[like]", "IJburg*"),
        ("stadsdeelCode", "N"),
        ("stadsdeelNaam", "Noord"),
        ("startBouwGepland[gte]", "2027-01-01"),
        ("startBouwGerealiseerd[isnull]", "false"),
        ("totaal[gte]", "0"),
        ("totaal[lt]", "500"),
    ]


def test_geo_filters() -> None:
    filters = PlanFilters(geometrie=GeoFilter(within=(121000.0, 487000.0, 500.0)))
    assert build_filters(filters, NAMES) == [("geometrie[within]", "121000.0,487000.0,500.0")]


def test_list_params() -> None:
    params = build_list_params(
        names=NAMES,
        page=2,
        page_size=50,
        sort=[Sort(PlanField.START_BOUW_GEPLAND, SortOrder.DESC), Sort(PlanField.ID)],
        fields=[PlanField.TOTAAL, PlanField.STADSDEEL_NAAM],
        count=True,
    )
    assert params == [
        ("page", "2"),
        ("_pageSize", "50"),
        ("_sort", "-startBouwGepland,id"),
        ("_fields", "id,totaal,stadsdeelNaam"),
        ("_count", "true"),
    ]


def test_sort_as_sequence() -> None:
    assert build_list_params(names=NAMES, sort=[PlanField.TOTAAL_ZELFST_PERM]) == [
        ("_sort", "totaalZelfstPerm")
    ]


def test_empty() -> None:
    assert build_list_params(names=NAMES, filters=PlanFilters(totaal=IntFilter())) == []


def test_extended_table_query() -> None:
    params = build_list_params(
        names=wire_names(WoningbouwplanKwartaalUitgebreid),
        filters=KwartaalUitgebreidFilters(
            id_primavera="123",
            oplevering_gepland=DateFilter(gte=datetime.date(2027, 1, 1)),
        ),
        sort=[Sort(KwartaalUitgebreidField.OPLEVERING_GEPLAND, SortOrder.DESC)],
        fields=[KwartaalUitgebreidField.ID_PRIMAVERA],
    )
    assert params == [
        ("idPrimavera", "123"),
        ("opleveringGepland[gte]", "2027-01-01"),
        ("_sort", "-opleveringGepland"),
        ("_fields", "id,idPrimavera"),
    ]
