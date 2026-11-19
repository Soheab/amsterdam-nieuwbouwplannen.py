# amsterdam-nieuwbouwplannen.py

Fully typed, async Python client for the Gemeente Amsterdam
[Nieuwbouwplannen API](https://api.data.amsterdam.nl/v1/docs/datasets/nieuwbouwplannen.html)
(DSO-API, `https://api.data.amsterdam.nl/v1/nieuwbouwplannen`).

See it in use on **[amsterdam-nieuwbouwplannen.soheab.com](https://amsterdam-nieuwbouwplannen.soheab.com)**.

- `aiohttp` + `msgspec`, pyright strict
- All three tables: `woningbouwplannen_openbaar` (public), `woningbouwplannen_kwartaal_standaard` and `woningbouwplannen_kwartaal_uitgebreid` (need authorisation)
- Typed filters with every DSO operator (`gt`, `gte`, `lt`, `lte`, `not`, `in`, `like`, `isnull`, `isempty`), plus geometry filters
- Automatic pagination, `count()`, single-record lookup, CSV and GeoJSON exports
- Pythonic snake_case names that map to the API's camelCase ones
- Errors are mapped to exceptions that carry the RFC 7807 problem body

## Install

Requires Python 3.12 or later. The distribution is named
`amsterdam-nieuwbouwplannen.py` and is imported as `amsterdam_nieuwbouwplannen`.

```bash
pip install -e .            # from a checkout
uv sync                     # dev: also installs pytest, pyright, ruff
```

## Usage

```python
import asyncio
import datetime

from amsterdam_nieuwbouwplannen import (
    Client,
    DateFilter,
    IntFilter,
    PlanField,
    PlanFilters,
    Sort,
    SortOrder,
    Stadsdeel,
    StrFilter,
)


async def main() -> None:
    async with Client(crs="EPSG:4326") as client:
        # One page
        page = await client.openbaar.list(
            filters=PlanFilters(
                stadsdeel=Stadsdeel.NOORD,
                totaal=IntFilter(gte=100),
                start_bouw_gepland=DateFilter(lt=datetime.date(2030, 1, 1)),
            ),
            sort=[Sort(PlanField.START_BOUW_GEPLAND, SortOrder.DESC)],
            page_size=50,
            count=True,
        )
        print(page.page.total_elements if page.page else None)

        # Every record, pages are followed automatically
        async for plan in client.openbaar.iter(
            filters=PlanFilters(wijk_naam=StrFilter(like="IJburg*"))
        ):
            print(plan.id, plan.projectnaam_afkorting, plan.totaal, plan.start_bouw_gepland)

        # A single record
        plan = await client.openbaar.get(1041)
        print(plan.started, plan.geometrie)

        # Counts and exports
        started = PlanFilters(start_bouw_gerealiseerd=DateFilter(isnull=False))
        print(await client.openbaar.count(filters=started))
        csv_bytes = await client.openbaar.export_csv(
            fields=[PlanField.ID, PlanField.PROJECTNAAM_AFKORTING, PlanField.TOTAAL]
        )
        geojson_bytes = await client.openbaar.export_geojson()


asyncio.run(main())
```

### Filters

Use `where()` to build a reusable filtered table. Each call returns a new
table. Start a field expression with `.filter` and chain operators such as
`.equal_to()`, `.greater_than_or_equal_to()`, and `.less_than()`. The short
methods are aliases. If you supply the same field to another
`where()` call, the latest filter for that field takes precedence.

```python
noord = client.openbaar.where(PlanFilters(stadsdeel=Stadsdeel.NOORD))
large_plans = noord.where(PlanField.TOTAAL.filter.greater_than_or_equal_to(100).less_than(500))
total = await large_plans.count()
plans = await large_plans.all(limit=10)
csv_bytes = await large_plans.export_csv()
```


Use `PlanFilters` for the public and standard quarterly tables and
`KwartaalUitgebreidFilters` for the extended quarterly table. Pass a plain
value for equality or an operator model for comparisons. Use `not_` and
`in_` for the API operators `not` and `in`. Pass `stadsdeel=Stadsdeel.NOORD`
to filter by district code. On a returned record, `plan.stadsdeel` gives you
the enum with its name in `.value` and its code in `.code` when the district
is recognized. The individual fields remain available.

Pass field enums to `fields` or `sort`. A bare field sorts ascending.
Use `Sort(field, SortOrder.DESC)` for descending order. The extended quarterly
table also accepts `KwartaalUitgebreidField`.

| Filter model | Operators |
| --- | --- |
| `IntFilter` | `eq`, `not_`, `in_`, `gt`, `gte`, `lt`, `lte`, `isnull` |
| `StrFilter` | `eq`, `not_`, `in_`, `like` (`*` / `?` wildcards), `isnull`, `isempty` |
| `DateFilter` | `eq`, `not_`, `in_`, `gt`, `gte`, `lt`, `lte`, `isnull` |
| `GeoFilter` | `contains` (point), `intersects` (point or WKT), `within` (`(x, y, radius)`), `isnull` |

Geometry filter coordinates are RD (EPSG:28992) by default. Pass `content_crs="EPSG:4326"` to use lat/lon.

| Fluent operator | Short alias |
| --- | --- |
| `equal_to()` | `eq()` |
| `not_equal_to()` | `not_()` |
| `one_of()` | `in_()` |
| `greater_than()` | `gt()` |
| `greater_than_or_equal_to()` | `gte()` |
| `less_than()` | `lt()` |
| `less_than_or_equal_to()` | `lte()` |
| `matches_pattern()` | `like()` |
| `is_null()` | `isnull()` |
| `is_empty()` | `isempty()` |

### API key

The Dataplatform is making an API key mandatory for all DSO-APIs. Request one and either pass
`api_key=` or set `DATA_AMSTERDAM_API_KEY`. It's sent as `X-Api-Key`. It only registers usage, it doesn't authorise anything.

### The kwartaal tables

`kwartaal_standaard` (scope `BB/WB/GO/STAN`) and `kwartaal_uitgebreid` (scope `BB/WB/GO/UITG`)
need an OAuth bearer token from the Gemeente Amsterdam. Request access from the data owner
(datateamsob@amsterdam.nl), then:

```python
from amsterdam_nieuwbouwplannen import KwartaalUitgebreidFilters

client = Client(access_token="eyJ...")
plans = await client.kwartaal_uitgebreid.all(
    filters=KwartaalUitgebreidFilters(oplevering_gepland=DateFilter(gte=datetime.date(2027, 1, 1)))
)
```

Without a valid token these raise `Unauthorized` or `Forbidden`.

### Errors

```python
from amsterdam_nieuwbouwplannen import BadRequest, NotFound

try:
    await client.openbaar.get(999999)
except NotFound as exc:
    print(exc.status, exc.problem)
```

`BadRequest.problem.invalid_params` explains which filter or field was rejected.

## Explorer

[amsterdam-nieuwbouwplannen.soheab.com](https://amsterdam-nieuwbouwplannen.soheab.com) is a
map-based explorer built on this client. Search and filter the plans, colour them by building
status or number of homes, narrow the list by panning the map, and open a project for its housing
mix, planning phase, boundary on an aerial photo and nearby official notices.

## Development

```bash
uv sync
uv run ruff format && uv run ruff check
uv run pyright
uv run pytest            # offline tests against a local mock server
uv run pytest -m live    # smoke test against the real API
```

## License

MIT. The data is © Gemeente Amsterdam, licensed CC BY (Naamsvermelding).
