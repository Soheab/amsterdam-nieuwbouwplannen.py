from __future__ import annotations

import msgspec

from ..enums import Stadsdeel
from .geo_filter import GeoFilter
from .operators import DateValue, IntValue, StrValue

__all__ = ("KwartaalUitgebreidFilters", "PlanFilters")


class PlanFilters(msgspec.Struct, kw_only=True):
    """Filter housing plan records using fields shared by all tables.

    Parameters
    ----------
    id: :obj:`IntValue` | :obj:`None`
        Unique identifier of the housing plan.
    projectnaam_afkorting: :obj:`StrValue` | :obj:`None`
        Short project name.
    buurt_code: :obj:`StrValue` | :obj:`None`
        Geographic neighbourhood code.
    buurt_naam: :obj:`StrValue` | :obj:`None`
        Name of the neighbourhood.
    wijk_code: :obj:`StrValue` | :obj:`None`
        Geographic ward code.
    wijk_naam: :obj:`StrValue` | :obj:`None`
        Name of the ward.
    gebied_code: :obj:`StrValue` | :obj:`None`
        Geographic area code.
    gebied_naam: :obj:`StrValue` | :obj:`None`
        Name of the area.
    stadsdeel: :class:`~amsterdam_nieuwbouwplannen.Stadsdeel` | :obj:`None`
        District whose geographic code matches the record.
    stadsdeel_code: :obj:`StrValue` | :obj:`None`
        Geographic district code.
    stadsdeel_naam: :obj:`StrValue` | :obj:`None`
        District name.
    zelfbouw: :obj:`StrValue` | :obj:`None`
        Resident-led development category.
    sociale_huur_corporatie: :obj:`StrValue` | :obj:`None`
        Housing corporation involvement in social rent homes.
    plaberum_publicatie: :obj:`StrValue` | :obj:`None`
        Published Plaberum planning phase.
    start_bouw_gepland: :obj:`DateValue` | :obj:`None`
        Planned construction start date.
    start_bouw_gerealiseerd: :obj:`DateValue` | :obj:`None`
        Actual construction start date.
    peildatum: :obj:`DateValue` | :obj:`None`
        Reference date for the snapshot.
    sociale_huur_zelfst_perm: :obj:`IntValue` | :obj:`None`
        Filter by the number of independent, permanent social rental homes.
    middeldure_huur: :obj:`IntValue` | :obj:`None`
        Filter by the number of mid-priced rental homes.
    betaalbare_koop: :obj:`IntValue` | :obj:`None`
        Filter by the number of affordable owner-occupied homes.
    vrije_sector_huur: :obj:`IntValue` | :obj:`None`
        Filter by the number of market-rate rental homes.
    vrije_sector_koop: :obj:`IntValue` | :obj:`None`
        Filter by the number of market-rate owner-occupied homes.
    vrije_sector_nb: :obj:`IntValue` | :obj:`None`
        Filter by the number of market-rate homes.
    onbekend: :obj:`IntValue` | :obj:`None`
        Filter by the number of unclassified homes.
    jongeren: :obj:`StrValue` | :obj:`None`
        Filter by the number of youth homes.
    studenten: :obj:`StrValue` | :obj:`None`
        Filter by the number of student homes.
    sh_onzelfst_en_of_tijdelijk: :obj:`StrValue` | :obj:`None`
        Filter by the number of shared or temporary social rental homes.
    onzelfstandig: :obj:`StrValue` | :obj:`None`
        Filter by the number of non-independent homes.
    tijdelijk: :obj:`StrValue` | :obj:`None`
        Filter by the number of temporary homes.
    totaal: :obj:`IntValue` | :obj:`None`
        Total number of homes.
    totaal_zelfst_perm: :obj:`IntValue` | :obj:`None`
        Total number of independent, permanent homes.
    geometrie: :class:`~amsterdam_nieuwbouwplannen.GeoFilter` | :obj:`None`
        Plan geometry.

    Notes
    -----
    Plain values match exactly. Operator models apply comparisons or missing-value checks.

    Examples
    --------
    >>> from amsterdam_nieuwbouwplannen import PlanFilters, Stadsdeel
    >>> filters = PlanFilters(stadsdeel=Stadsdeel.NOORD)
    """

    id: IntValue | None = None
    projectnaam_afkorting: StrValue | None = None
    buurt_code: StrValue | None = None
    buurt_naam: StrValue | None = None
    wijk_code: StrValue | None = None
    wijk_naam: StrValue | None = None
    gebied_code: StrValue | None = None
    gebied_naam: StrValue | None = None
    stadsdeel: Stadsdeel | None = None
    stadsdeel_code: StrValue | None = None
    stadsdeel_naam: StrValue | None = None
    zelfbouw: StrValue | None = None
    sociale_huur_corporatie: StrValue | None = None
    plaberum_publicatie: StrValue | None = None
    start_bouw_gepland: DateValue | None = None
    start_bouw_gerealiseerd: DateValue | None = None
    peildatum: DateValue | None = None
    sociale_huur_zelfst_perm: IntValue | None = None
    middeldure_huur: IntValue | None = None
    betaalbare_koop: IntValue | None = None
    vrije_sector_huur: IntValue | None = None
    vrije_sector_koop: IntValue | None = None
    vrije_sector_nb: IntValue | None = None
    onbekend: IntValue | None = None
    jongeren: StrValue | None = None
    studenten: StrValue | None = None
    sh_onzelfst_en_of_tijdelijk: StrValue | None = None
    onzelfstandig: StrValue | None = None
    tijdelijk: StrValue | None = None
    totaal: IntValue | None = None
    totaal_zelfst_perm: IntValue | None = None
    geometrie: GeoFilter | None = None


class KwartaalUitgebreidFilters(PlanFilters, kw_only=True):
    """Filter records using shared and extended quarterly fields.

    Parameters
    ----------
    id_primavera: :obj:`StrValue` | :obj:`None`
        Project identifier in Primavera.
    grex: :obj:`StrValue` | :obj:`None`
        Land development identifier.
    gebiedsindeling_primavera: :obj:`StrValue` | :obj:`None`
        Area classification in Primavera.
    oplevering_gepland: :obj:`DateValue` | :obj:`None`
        Planned completion date.

    Notes
    -----
    All parameters from :class:`~amsterdam_nieuwbouwplannen.PlanFilters` are also available.
    """

    id_primavera: StrValue | None = None
    grex: StrValue | None = None
    gebiedsindeling_primavera: StrValue | None = None
    oplevering_gepland: DateValue | None = None
