from __future__ import annotations

import msgspec

__all__ = ("GeoFilter", "Point")

type Point = tuple[float, float]
"""``(x, y)`` in RD, or ``(lat, lon)`` in WGS84 when ``content_crs="EPSG:4326"``."""


class GeoFilter(msgspec.Struct, kw_only=True):
    """Apply spatial and null checks to a plan's geometry.

    Parameters
    ----------
    eq: :class:`str` | :obj:`None`
        WKT geometry to match exactly.
    not_: :class:`str` | :obj:`None`
        WKT geometry to exclude.
    contains: :obj:`Point` | :obj:`None`
        Point that the geometry must contain.
    intersects: :obj:`Point` | :class:`str` | :obj:`None`
        Point or WKT geometry that the geometry must intersect.
    within: :class:`tuple`[:class:`float`, :class:`float`, :class:`float`] | :obj:`None`
        Search centre and distance as (x, y, radius), with radius in metres.
    isnull: :class:`bool` | :obj:`None`
        Whether the value must be null or non-null.

    Notes
    -----
    Coordinates use RD (EPSG:28992) unless content_crs specifies another CRS.
    """

    eq: str | None = None
    not_: str | None = msgspec.field(default=None, name="not")
    contains: Point | None = None
    """Geometry contains this point."""
    intersects: Point | str | None = None
    """Geometry intersects this point or WKT geometry."""
    within: tuple[float, float, float] | None = None
    """Geometry lies within ``radius`` metres of ``(x, y)``: ``(x, y, radius)``."""
    isnull: bool | None = None
