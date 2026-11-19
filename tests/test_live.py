from __future__ import annotations

import pytest

from amsterdam_nieuwbouwplannen import Client, IntFilter, NotFound, PlanFilters

pytestmark = pytest.mark.live


async def test_live_roundtrip() -> None:
    async with Client() as client:
        page = await client.openbaar.list(page_size=5, count=True)
        assert page.items, "no records returned"
        assert page.page is not None
        assert page.page.total_elements is not None

        first = page.items[0]
        again = await client.openbaar.get(first.id)
        assert again.id == first.id

        noord = await client.openbaar.all(filters=PlanFilters(stadsdeel_naam="Noord"), limit=3)
        assert all(p.stadsdeel_naam == "Noord" for p in noord)

        assert await client.openbaar.count(filters=PlanFilters(totaal=IntFilter(gte=0))) > 0

        with pytest.raises(NotFound):
            await client.openbaar.get(999_999_999)
