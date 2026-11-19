from __future__ import annotations

import datetime

import msgspec

from ..enums import Stadsdeel
from .geometry import MultiPolygon
from .links import ItemLinks

__all__ = (
    "WoningbouwplanKwartaalStandaard",
    "WoningbouwplanKwartaalUitgebreid",
    "WoningbouwplanOpenbaar",
)

# The schema publishes these counts as strings for the public table; the extended table
# may expose them as integers. Accept both so decoding never breaks on a schema bump.
type _Count = int | str | None


class _BasePlan(msgspec.Struct, frozen=True, kw_only=True, rename="camel"):
    id: int
    """Unique identifier of the new-build project."""

    links: ItemLinks | None = msgspec.field(default=None, name="_links")

    projectnaam_afkorting: str | None = None
    """Project name, usually based on the Primavera name."""

    # Location
    buurt_code: str | None = None
    buurt_naam: str | None = None
    wijk_code: str | None = None
    wijk_naam: str | None = None
    gebied_code: str | None = None
    gebied_naam: str | None = None
    stadsdeel_code: str | None = None
    stadsdeel_naam: str | None = None

    # Characteristics
    zelfbouw: str | None = None
    """Whether future residents develop the project themselves (MO, PO, CPO, SIHK, ...)."""
    sociale_huur_corporatie: str | None = None
    """Whether a housing corporation is involved in the social rent homes."""
    plaberum_publicatie: str | None = None
    """Current phase in the (five step) plaberum process."""

    # Dates
    start_bouw_gepland: datetime.date | None = None
    start_bouw_gerealiseerd: datetime.date | None = None
    peildatum: datetime.date | None = None
    """Reference date of the file; always the first day of a quarter."""

    # Homes per segment
    sociale_huur_zelfst_perm: int | None = None
    middeldure_huur: int | None = None
    betaalbare_koop: int | None = None
    sociale_koop: int | None = None
    """Older name of ``betaalbare_koop`` still present in some OpenAPI versions."""
    vrije_sector_huur: int | None = None
    vrije_sector_koop: int | None = None
    vrije_sector_nb: int | None = None
    """Free sector, rent or buy not decided yet."""
    onbekend: int | None = None
    jongeren: _Count = None
    studenten: _Count = None
    sh_onzelfst_en_of_tijdelijk: _Count = None
    onzelfstandig: _Count = None
    tijdelijk: _Count = None
    totaal: int | None = None
    """All homes, including non-independent and temporary ones."""
    totaal_zelfst_perm: int | None = None
    """All independent, permanent homes."""

    geometrie: MultiPolygon | None = None

    @property
    def stadsdeel(self) -> Stadsdeel | None:
        """The known district, resolved by code or name.

        Returns
        -------
        :class:`~amsterdam_nieuwbouwplannen.Stadsdeel` | :obj:`None`
            Known district, matched by code first and then by name. :obj:`None` if neither
            matches.
        """

        for district in Stadsdeel:
            if district.code == self.stadsdeel_code:
                return district
        return next((district for district in Stadsdeel if district == self.stadsdeel_naam), None)

    @property
    def started(self) -> bool:
        """Whether construction has actually started.

        Returns
        -------
        :class:`bool`
            :obj:`True` when an actual construction start date is present.
        """

        return self.start_bouw_gerealiseerd is not None


class WoningbouwplanOpenbaar(_BasePlan, frozen=True, kw_only=True):
    """A record of ``woningbouwplannen_openbaar`` (public, no authorisation)."""


class WoningbouwplanKwartaalStandaard(_BasePlan, frozen=True, kw_only=True):
    """A record of ``woningbouwplannen_kwartaal_standaard`` (scope ``BB/WB/GO/STAN``)."""


class WoningbouwplanKwartaalUitgebreid(_BasePlan, frozen=True, kw_only=True):
    """A record of ``woningbouwplannen_kwartaal_uitgebreid`` (scope ``BB/WB/GO/UITG``).

    Attributes
    ----------
    id_primavera: :class:`str` | :obj:`None`
        Project identifier in Primavera.
    grex: :class:`str` | :obj:`None`
        Land development identifier.
    gebiedsindeling_primavera: :class:`str` | :obj:`None`
        Area classification in Primavera.
    oplevering_gepland: :class:`datetime.date` | :obj:`None`
        Planned completion date.
    """

    id_primavera: str | None = None
    grex: str | None = None
    """Land development (grondexploitatie) number."""
    gebiedsindeling_primavera: str | None = None
    oplevering_gepland: datetime.date | None = None
    """Planned completion date."""
