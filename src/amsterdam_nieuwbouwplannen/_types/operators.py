from __future__ import annotations

import datetime
from collections.abc import Sequence

import msgspec

from .geo_filter import GeoFilter, Point

__all__ = (
    "DateFilter",
    "DateValue",
    "GeoFilter",
    "IntFilter",
    "IntValue",
    "Point",
    "StrFilter",
    "StrValue",
)


class IntFilter(msgspec.Struct, kw_only=True):
    """Apply comparison and null checks to an integer field.

    Parameters
    ----------
    eq: :class:`int` | :obj:`None`
        Value to match exactly.
    not_: :class:`int` | :obj:`None`
        Value to exclude.
    in_: :class:`collections.abc.Sequence`[:class:`int`] | :obj:`None`
        Values to match against.
    gt: :class:`int` | :obj:`None`
        Exclusive lower bound.
    gte: :class:`int` | :obj:`None`
        Inclusive lower bound.
    lt: :class:`int` | :obj:`None`
        Exclusive upper bound.
    lte: :class:`int` | :obj:`None`
        Inclusive upper bound.
    isnull: :class:`bool` | :obj:`None`
        Whether the value must be null or non-null.
    """

    eq: int | None = None
    not_: int | None = msgspec.field(default=None, name="not")
    in_: Sequence[int] | None = msgspec.field(default=None, name="in")
    gt: int | None = None
    gte: int | None = None
    lt: int | None = None
    lte: int | None = None
    isnull: bool | None = None


class StrFilter(msgspec.Struct, kw_only=True):
    """Apply exact, wildcard, membership, and missing-value checks to text.

    Parameters
    ----------
    eq: :class:`str` | :obj:`None`
        Value to match exactly.
    not_: :class:`str` | :obj:`None`
        Value to exclude.
    in_: :class:`collections.abc.Sequence`[:class:`str`] | :obj:`None`
        Values to match against.
    like: :class:`str` | :obj:`None`
        Pattern with * and ? wildcards.
    isnull: :class:`bool` | :obj:`None`
        Whether the value must be null or non-null.
    isempty: :class:`bool` | :obj:`None`
        Whether the string must be empty or non-empty.
    """

    eq: str | None = None
    not_: str | None = msgspec.field(default=None, name="not")
    in_: Sequence[str] | None = msgspec.field(default=None, name="in")
    like: str | None = None
    isnull: bool | None = None
    isempty: bool | None = None


class DateFilter(msgspec.Struct, kw_only=True):
    """Apply comparison and null checks to a date field.

    Parameters
    ----------
    eq: :class:`datetime.date` | :obj:`None`
        Value to match exactly.
    not_: :class:`datetime.date` | :obj:`None`
        Value to exclude.
    in_: :class:`collections.abc.Sequence`[:class:`datetime.date`] | :obj:`None`
        Values to match against.
    gt: :class:`datetime.date` | :obj:`None`
        Exclusive lower bound.
    gte: :class:`datetime.date` | :obj:`None`
        Inclusive lower bound.
    lt: :class:`datetime.date` | :obj:`None`
        Exclusive upper bound.
    lte: :class:`datetime.date` | :obj:`None`
        Inclusive upper bound.
    isnull: :class:`bool` | :obj:`None`
        Whether the value must be null or non-null.
    """

    eq: datetime.date | None = None
    not_: datetime.date | None = msgspec.field(default=None, name="not")
    in_: Sequence[datetime.date] | None = msgspec.field(default=None, name="in")
    gt: datetime.date | None = None
    gte: datetime.date | None = None
    lt: datetime.date | None = None
    lte: datetime.date | None = None
    isnull: bool | None = None


type IntValue = int | IntFilter
type StrValue = str | StrFilter
type DateValue = datetime.date | DateFilter
