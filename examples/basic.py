from __future__ import annotations

import asyncio

from amsterdam_nieuwbouwplannen import (
    Client,
    DateFilter,
    PlanField,
    PlanFilters,
    Sort,
    SortOrder,
    Stadsdeel,
)


async def main() -> None:
    async with Client() as client:
        total = await client.openbaar.count()
        print(f"{total} projects in the dataset\n")

        plans = await client.openbaar.all(
            filters=PlanFilters(
                stadsdeel=Stadsdeel.NOORD,
                start_bouw_gerealiseerd=DateFilter(isnull=True),
            ),
            sort=[Sort(PlanField.TOTAAL, SortOrder.DESC)],
            limit=10,
        )
        for plan in plans:
            print(
                f"{plan.id:>6}  {plan.projectnaam_afkorting or '?':<40} "
                f"{plan.totaal or 0:>5} homes  start {plan.start_bouw_gepland}"
            )


if __name__ == "__main__":
    asyncio.run(main())
