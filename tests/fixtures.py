from __future__ import annotations

from typing import Any

TABLE = "woningbouwplannen_openbaar"


def plan(id: int, **overrides: Any) -> dict[str, Any]:
    record: dict[str, Any] = {
        "_links": {
            "schema": "https://schemas.data.amsterdam.nl/datasets/nieuwbouwplannen/dataset#woningbouwplannenOpenbaar",
            "self": {
                "href": f"https://api.data.amsterdam.nl/v1/nieuwbouwplannen/{TABLE}/{id}/",
                "title": str(id),
                "id": id,
            },
        },
        "id": id,
        "projectnaamAfkorting": "NDSM Kavel B7",
        "buurtCode": "N73b",
        "buurtNaam": "NDSM terrein",
        "wijkCode": "N73",
        "wijkNaam": "NDSM/Hamerstraat",
        "gebiedCode": "GN08",
        "gebiedNaam": "Noord-West",
        "stadsdeelCode": "N",
        "stadsdeelNaam": "Noord",
        "zelfbouw": None,
        "socialeHuurCorporatie": "Ja",
        "plaberumPublicatie": "Uitvoering",
        "startBouwGepland": "2026-03-23",
        "startBouwGerealiseerd": "2026-03-23",
        "socialeHuurZelfstPerm": 80,
        "middeldureHuur": 60,
        "betaalbareKoop": 20,
        "vrijeSectorHuur": 27,
        "vrijeSectorKoop": 20,
        "vrijeSectorNb": 0,
        "onbekend": 0,
        "jongeren": "0",
        "studenten": None,
        "shOnzelfstEnOfTijdelijk": "0",
        "onzelfstandig": "0",
        "tijdelijk": "0",
        "totaal": 207,
        "totaalZelfstPerm": 207,
        "peildatum": "2026-07-01",
        "geometrie": {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [119500.0, 490900.0],
                        [119600.0, 490900.0],
                        [119600.0, 491000.0],
                        [119500.0, 490900.0],
                    ]
                ]
            ],
        },
    }
    record.update(overrides)
    return record


def page(
    records: list[dict[str, Any]],
    *,
    number: int = 1,
    size: int = 20,
    next_href: str | None = None,
    previous_href: str | None = None,
    total: int | None = None,
) -> dict[str, Any]:
    page_info: dict[str, Any] = {"number": number, "size": size}
    if total is not None:
        page_info["totalElements"] = total
        page_info["totalPages"] = -(-total // size)
    return {
        "_links": {
            "self": {"href": f"https://api.data.amsterdam.nl/v1/nieuwbouwplannen/{TABLE}/"},
            "next": {"href": next_href},
            "previous": {"href": previous_href},
        },
        "_embedded": {TABLE: records},
        "page": page_info,
    }
