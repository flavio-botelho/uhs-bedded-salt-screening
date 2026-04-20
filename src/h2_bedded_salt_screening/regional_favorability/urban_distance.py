"""Distance from each grid cell to the nearest urban-area polygon."""

from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from . import config


def compute_urban_distance_grid(
    valid_mask: NDArray[np.bool_],
    profile: dict,
    shapefile_path: Path,
) -> NDArray[np.floating] | None:
    """Distance (m) from each valid cell to the unary-union of urban polygons."""
    if not shapefile_path.exists():
        print(f"  Urban shapefile not found: {shapefile_path}")
        print("  Skipping urban distance parameter.")
        return None

    print("  Computing distance to urban areas...")

    try:
        import geopandas as gpd
        from shapely.geometry import Point
        from shapely.ops import unary_union
    except ImportError as e:
        print(f"  Error importing geopandas/shapely: {e}")
        return None

    try:
        urban_gdf = gpd.read_file(shapefile_path)
    except Exception as e:
        print(f"  Error reading shapefile: {e}")
        return None

    if urban_gdf.empty:
        print("  Empty shapefile. Returning safe distance.")
        safe_grid = np.full(valid_mask.shape, config.URBAN_DIST_SAFE * 1.1)
        safe_grid[~valid_mask] = np.nan
        return safe_grid

    try:
        urban_union = unary_union(urban_gdf.geometry)
    except Exception as e:
        print(f"  Error creating union: {e}")
        return None

    transform = profile["transform"]
    cols, rows = profile["width"], profile["height"]
    x_centers = transform.c + transform.a / 2 + np.arange(cols) * transform.a
    y_centers = transform.f + transform.e / 2 + np.arange(rows) * transform.e

    result = np.full(valid_mask.shape, np.nan)
    valid_count = 0

    for r in range(rows):
        for c in range(cols):
            if valid_mask[r, c]:
                point = Point(x_centers[c], y_centers[r])
                dist = point.distance(urban_union)
                result[r, c] = dist
                valid_count += 1

    print(f"    Computed urban distance for {valid_count} cells.")
    return result
