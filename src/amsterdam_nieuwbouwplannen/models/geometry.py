from __future__ import annotations

from typing import Literal

import msgspec

__all__ = ("MultiPolygon", "MultiPolygonCoordinates")

# [polygon][ring][point][x, y(, z)]
type MultiPolygonCoordinates = list[list[list[list[float]]]]


class MultiPolygon(msgspec.Struct, frozen=True, kw_only=True):
    """GeoJSON MultiPolygon. Coordinates are RD (EPSG:28992) unless another CRS was requested.

    Attributes
    ----------
    type: :obj:`typing.Literal`[``"MultiPolygon"``]
        GeoJSON geometry type.
    coordinates: :obj:`MultiPolygonCoordinates`
        Coordinates grouped by polygon, ring, and position.

    Notes
    -----
    Coordinates use RD (EPSG:28992) unless the request selected another CRS.
    """

    type: Literal["MultiPolygon"] = "MultiPolygon"
    coordinates: MultiPolygonCoordinates
