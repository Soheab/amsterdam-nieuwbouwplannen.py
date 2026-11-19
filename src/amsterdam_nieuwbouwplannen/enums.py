from enum import StrEnum
from typing import Self

from .field_filter import FieldFilter

__all__ = ("KwartaalUitgebreidField", "PlanField", "SortOrder", "Stadsdeel")


class _FilterField(StrEnum):
    @property
    def filter(self) -> FieldFilter[Self]:
        """Start a filter expression for this field.

        Returns
        -------
        :class:`~amsterdam_nieuwbouwplannen.FieldFilter`
            Expression ready to receive comparison operators.
        """

        return FieldFilter(self)


class PlanField(_FilterField):
    """Select or sort fields shared by the public and quarterly tables."""

    ID = "id"
    PROJECTNAAM_AFKORTING = "projectnaam_afkorting"
    BUURT_CODE = "buurt_code"
    BUURT_NAAM = "buurt_naam"
    WIJK_CODE = "wijk_code"
    WIJK_NAAM = "wijk_naam"
    GEBIED_CODE = "gebied_code"
    GEBIED_NAAM = "gebied_naam"
    STADSDEEL_CODE = "stadsdeel_code"
    STADSDEEL_NAAM = "stadsdeel_naam"
    ZELFBOUW = "zelfbouw"
    SOCIALE_HUUR_CORPORATIE = "sociale_huur_corporatie"
    PLABERUM_PUBLICATIE = "plaberum_publicatie"
    START_BOUW_GEPLAND = "start_bouw_gepland"
    START_BOUW_GEREALISEERD = "start_bouw_gerealiseerd"
    PEILDATUM = "peildatum"
    SOCIALE_HUUR_ZELFST_PERM = "sociale_huur_zelfst_perm"
    MIDDELDURE_HUUR = "middeldure_huur"
    BETAALBARE_KOOP = "betaalbare_koop"
    VRIJE_SECTOR_HUUR = "vrije_sector_huur"
    VRIJE_SECTOR_KOOP = "vrije_sector_koop"
    VRIJE_SECTOR_NB = "vrije_sector_nb"
    ONBEKEND = "onbekend"
    JONGEREN = "jongeren"
    STUDENTEN = "studenten"
    SH_ONZELFST_EN_OF_TIJDELIJK = "sh_onzelfst_en_of_tijdelijk"
    ONZELFSTANDIG = "onzelfstandig"
    TIJDELIJK = "tijdelijk"
    TOTAAL = "totaal"
    TOTAAL_ZELFST_PERM = "totaal_zelfst_perm"
    GEOMETRIE = "geometrie"


class KwartaalUitgebreidField(_FilterField):
    """Select or sort fields in the extended quarterly table."""

    ID = "id"
    PROJECTNAAM_AFKORTING = "projectnaam_afkorting"
    BUURT_CODE = "buurt_code"
    BUURT_NAAM = "buurt_naam"
    WIJK_CODE = "wijk_code"
    WIJK_NAAM = "wijk_naam"
    GEBIED_CODE = "gebied_code"
    GEBIED_NAAM = "gebied_naam"
    STADSDEEL_CODE = "stadsdeel_code"
    STADSDEEL_NAAM = "stadsdeel_naam"
    ZELFBOUW = "zelfbouw"
    SOCIALE_HUUR_CORPORATIE = "sociale_huur_corporatie"
    PLABERUM_PUBLICATIE = "plaberum_publicatie"
    START_BOUW_GEPLAND = "start_bouw_gepland"
    START_BOUW_GEREALISEERD = "start_bouw_gerealiseerd"
    PEILDATUM = "peildatum"
    SOCIALE_HUUR_ZELFST_PERM = "sociale_huur_zelfst_perm"
    MIDDELDURE_HUUR = "middeldure_huur"
    BETAALBARE_KOOP = "betaalbare_koop"
    VRIJE_SECTOR_HUUR = "vrije_sector_huur"
    VRIJE_SECTOR_KOOP = "vrije_sector_koop"
    VRIJE_SECTOR_NB = "vrije_sector_nb"
    ONBEKEND = "onbekend"
    JONGEREN = "jongeren"
    STUDENTEN = "studenten"
    SH_ONZELFST_EN_OF_TIJDELIJK = "sh_onzelfst_en_of_tijdelijk"
    ONZELFSTANDIG = "onzelfstandig"
    TIJDELIJK = "tijdelijk"
    TOTAAL = "totaal"
    TOTAAL_ZELFST_PERM = "totaal_zelfst_perm"
    GEOMETRIE = "geometrie"
    ID_PRIMAVERA = "id_primavera"
    GREX = "grex"
    GEBIEDSINDELING_PRIMAVERA = "gebiedsindeling_primavera"
    OPLEVERING_GEPLAND = "oplevering_gepland"


class SortOrder(StrEnum):
    """Specify whether values sort in ascending or descending order."""

    ASC = "asc"
    DESC = "desc"


class Stadsdeel(StrEnum):
    """Identify an Amsterdam district by name and geographic code."""

    CENTRUM = "Centrum"
    WESTPOORT = "Westpoort"
    WEST = "West"
    NIEUW_WEST = "Nieuw-West"
    ZUID = "Zuid"
    OOST = "Oost"
    NOORD = "Noord"
    WEESP = "Weesp"
    ZUIDOOST = "Zuidoost"

    @property
    def code(self) -> str:
        """Return the geographic code for this stadsdeel.

        Returns
        -------
        :class:`str`
            Geographic district code used by the API.
        """

        return STADSDELEN_TO_CODE[self]


STADSDELEN_TO_CODE: dict[Stadsdeel, str] = {
    Stadsdeel.CENTRUM: "A",
    Stadsdeel.WESTPOORT: "B",
    Stadsdeel.WEST: "E",
    Stadsdeel.NIEUW_WEST: "F",
    Stadsdeel.ZUID: "K",
    Stadsdeel.OOST: "M",
    Stadsdeel.NOORD: "N",
    Stadsdeel.WEESP: "S",
    Stadsdeel.ZUIDOOST: "T",
}
