"""Hexagonal-packing cavern-field geometry."""

import numpy as np
from shapely.geometry import Point


def calculate_diameter(volume: float, hd_ratio: float) -> float:
    """Diameter of an ellipsoidal cavern given net volume and H/D ratio.

    V = (π/6) · D² · H and H = hd_ratio · D  ⇒  D = ((6·V)/(π·hd_ratio))^(1/3).
    """
    return float(np.cbrt((6.0 * volume) / (np.pi * hd_ratio)))


def generate_hexagonal_grid(
    bounds: tuple[float, float, float, float],
    spacing: float,
) -> list[Point]:
    """Hexagonal lattice of points covering ``bounds = (xmin, ymin, xmax, ymax)``.

    Horizontal step = ``spacing``; vertical step = ``spacing · √3/2``; odd rows
    are offset by ``spacing/2``.
    """
    xmin, ymin, xmax, ymax = bounds
    dx = spacing
    dy = spacing * (np.sqrt(3) / 2.0)

    points: list[Point] = []
    y = ymin
    row_idx = 0
    while y <= ymax + dy:
        x_offset = (dx / 2.0) if (row_idx % 2 == 1) else 0.0
        x = xmin + x_offset
        while x <= xmax + dx:
            points.append(Point(x, y))
            x += dx
        y += dy
        row_idx += 1
    return points


def sample_grid_value(raster_src, x: float, y: float):
    """Raster value at ``(x, y)``; returns ``None`` if the point is outside the grid."""
    try:
        row, col = raster_src.index(x, y)
        if 0 <= row < raster_src.height and 0 <= col < raster_src.width:
            return raster_src.read(1)[row, col]
    except Exception:
        pass
    return None
