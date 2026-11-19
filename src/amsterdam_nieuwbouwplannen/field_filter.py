from __future__ import annotations

import datetime
from dataclasses import dataclass, field as dataclass_field
from typing import TYPE_CHECKING, Literal, Self

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ._types.geo_filter import Point

__all__ = ("FieldFilter",)

type Operand = int | str | datetime.date
type Operator = Literal[
    "eq",
    "not",
    "in",
    "gt",
    "gte",
    "lt",
    "lte",
    "like",
    "isnull",
    "isempty",
    "contains",
    "intersects",
    "within",
]


@dataclass(frozen=True)
class FieldFilter[FieldT: str]:
    """Build a reusable filter expression for one table field.

    Parameters
    ----------
    field: :obj:`FieldT`
        Field enum member to filter.

    Notes
    -----
    Each operator returns a new expression. Repeating an operator replaces its
    operand. The API determines which operators are accepted for each field.
    """

    field: FieldT
    _operators: tuple[tuple[Operator, object], ...] = dataclass_field(
        default=(), init=False, repr=False
    )

    def _with_operator(self, operator: Operator, value: object) -> Self:
        operands = dict(self._operators)
        operands[operator] = value
        expression = type(self)(self.field)
        object.__setattr__(expression, "_operators", tuple(operands.items()))
        return expression

    def as_filters(self) -> dict[str, object]:
        """Expose this expression for serialization as a field filter.

        Returns
        -------
        :class:`dict`
            A field mapped to its operator operands.
        """

        return {self.field: dict(self._operators)} if self._operators else {}

    def equal_to(self, value: Operand) -> Self:
        """Match the exact value.

        Parameters
        ----------
        value: :obj:`Operand`
            Operand for this comparison.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("eq", value)

    def not_equal_to(self, value: Operand) -> Self:
        """Exclude the exact value.

        Parameters
        ----------
        value: :obj:`Operand`
            Operand for this comparison.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("not", value)

    def one_of(self, value: Sequence[Operand]) -> Self:
        """Match any of the supplied values.

        Parameters
        ----------
        value: :class:`~collections.abc.Sequence`
            Candidate values.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("in", tuple(value))

    def greater_than(self, value: Operand) -> Self:
        """Match values above the exclusive lower bound.

        Parameters
        ----------
        value: :obj:`Operand`
            Operand for this comparison.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("gt", value)

    def greater_than_or_equal_to(self, value: Operand) -> Self:
        """Match values at or above the inclusive lower bound.

        Parameters
        ----------
        value: :obj:`Operand`
            Operand for this comparison.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("gte", value)

    def less_than(self, value: Operand) -> Self:
        """Match values below the exclusive upper bound.

        Parameters
        ----------
        value: :obj:`Operand`
            Operand for this comparison.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("lt", value)

    def less_than_or_equal_to(self, value: Operand) -> Self:
        """Match values at or below the inclusive upper bound.

        Parameters
        ----------
        value: :obj:`Operand`
            Operand for this comparison.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("lte", value)

    def matches_pattern(self, value: str) -> Self:
        """Match text using a pattern with ``*`` and ``?`` wildcards.

        Parameters
        ----------
        value: :class:`str`
            Operand for this comparison.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("like", value)

    def is_null(self, value: bool = True) -> Self:
        """Check whether the field is null.

        Parameters
        ----------
        value: :class:`bool`
            Whether the field must be null or non-null.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("isnull", value)

    def is_empty(self, value: bool = True) -> Self:
        """Check whether the text is empty.

        Parameters
        ----------
        value: :class:`bool`
            Whether the field must be empty or non-empty.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("isempty", value)

    def contains(self, value: Point) -> Self:
        """Match geometries containing the given point.

        Parameters
        ----------
        value: :obj:`Point`
            Operand for this comparison.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("contains", value)

    def intersects(self, value: Point | str) -> Self:
        """Match geometries intersecting a point or WKT geometry.

        Parameters
        ----------
        value: :obj:`Point` | :class:`str`
            Operand for this comparison.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("intersects", value)

    def within(self, value: tuple[float, float, float]) -> Self:
        """Match geometries within a radius of the given point.

        Parameters
        ----------
        value: :class:`tuple`
            Coordinates and radius as (x, y, radius), with the radius in metres.

        Returns
        -------
        :obj:`typing.Self`
            Expression including this comparison.
        """

        return self._with_operator("within", value)

    def eq(self, value: Operand) -> Self:
        """Alias for :meth:`equal_to`."""

        return self.equal_to(value)

    def not_(self, value: Operand) -> Self:
        """Alias for :meth:`not_equal_to`."""

        return self.not_equal_to(value)

    def in_(self, value: Sequence[Operand]) -> Self:
        """Alias for :meth:`one_of`."""

        return self.one_of(value)

    def gt(self, value: Operand) -> Self:
        """Alias for :meth:`greater_than`."""

        return self.greater_than(value)

    def gte(self, value: Operand) -> Self:
        """Alias for :meth:`greater_than_or_equal_to`."""

        return self.greater_than_or_equal_to(value)

    def lt(self, value: Operand) -> Self:
        """Alias for :meth:`less_than`."""

        return self.less_than(value)

    def lte(self, value: Operand) -> Self:
        """Alias for :meth:`less_than_or_equal_to`."""

        return self.less_than_or_equal_to(value)

    def like(self, value: str) -> Self:
        """Alias for :meth:`matches_pattern`."""

        return self.matches_pattern(value)

    def isnull(self, value: bool = True) -> Self:
        """Alias for :meth:`is_null`."""

        return self.is_null(value)

    def isempty(self, value: bool = True) -> Self:
        """Alias for :meth:`is_empty`."""

        return self.is_empty(value)
