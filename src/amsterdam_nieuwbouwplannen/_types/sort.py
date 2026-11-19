from __future__ import annotations

import msgspec

from ..enums import SortOrder

__all__ = ("Sort",)


class Sort[FieldT: str](msgspec.Struct, frozen=True):
    """A field and its sort direction.

    Parameters
    ----------
    field: :obj:`FieldT`
        Field to sort by.
    order: :class:`~amsterdam_nieuwbouwplannen.SortOrder`
        Sort direction. Ascending is the default.
    """

    field: FieldT
    order: SortOrder = SortOrder.ASC
