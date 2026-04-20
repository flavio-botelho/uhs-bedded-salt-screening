"""Grid I/O and interpolation utilities.

ESRI ASCII grid read/write, coordinate meshgrid, IDW, and edge-distance EDT.
"""

from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from numpy.typing import NDArray
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree

from . import config


def read_asc(filepath: Path) -> tuple[NDArray[np.floating], dict[str, Any]]:
    """Read an ESRI ASCII grid. Returns (data with NODATA as NaN, rasterio profile)."""
    with rasterio.open(filepath) as src:
        data = src.read(1).astype(float)
        profile = src.profile.copy()
        nodata_val = src.nodatavals[0]
        if nodata_val is not None:
            data[data == nodata_val] = np.nan
    return data, profile


def write_asc(
    filepath: Path,
    data: NDArray[np.floating],
    profile: dict[str, Any],
    nodata_value: float = config.NODATA_VALUE,
) -> None:
    """Write a 2D array as ESRI ASCII grid (NaN replaced by ``nodata_value``)."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    profile_out = profile.copy()
    profile_out.update(dtype=rasterio.float32, count=1, nodata=nodata_value)

    data_to_write = np.where(np.isnan(data), nodata_value, data)

    with rasterio.open(filepath, "w", **profile_out) as dst:
        dst.write(data_to_write.astype(np.float32), 1)

    print(f"  Saved: {filepath.name}")


def create_grid_coordinates(
    profile: dict[str, Any],
) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
    """Create (grid_xx, grid_yy) cell-center meshgrids from a rasterio profile."""
    transform = profile["transform"]
    cols, rows = profile["width"], profile["height"]

    x_centers = transform.c + transform.a / 2 + np.arange(cols) * transform.a
    y_centers = transform.f + transform.e / 2 + np.arange(rows) * transform.e

    return np.meshgrid(x_centers, y_centers)


def idw_interpolation(
    x_coords: NDArray[np.floating],
    y_coords: NDArray[np.floating],
    values: NDArray[np.floating],
    grid_xx: NDArray[np.floating],
    grid_yy: NDArray[np.floating],
    power: int = config.IDW_POWER,
    k: int = config.IDW_K_NEIGHBORS,
) -> NDArray[np.floating]:
    """Inverse Distance Weighted interpolation using k nearest neighbours."""
    values = np.asarray(values, dtype=float)

    if len(x_coords) == 0:
        return np.full(grid_xx.shape, np.nan)

    tree = cKDTree(np.vstack((x_coords, y_coords)).T)
    k_actual = min(k, len(x_coords))

    if k_actual == 0:
        return np.full(grid_xx.shape, np.nan)

    grid_points = np.vstack((grid_xx.ravel(), grid_yy.ravel())).T
    distances, indices = tree.query(grid_points, k=k_actual, workers=-1)

    if distances.ndim == 1:
        distances = distances[:, np.newaxis]
        indices = indices[:, np.newaxis]

    distances = np.maximum(distances, 1e-12)
    weights = 1.0 / (distances**power)

    result = np.full(grid_points.shape[0], np.nan)

    for i in range(grid_points.shape[0]):
        valid_mask = (indices[i, :] < len(values)) & (indices[i, :] >= 0)
        valid_indices = indices[i, valid_mask]
        valid_weights = weights[i, valid_mask]

        point_values = values[valid_indices]
        nan_mask = ~np.isnan(point_values)

        if np.any(nan_mask):
            final_weights = valid_weights[nan_mask]
            final_values = point_values[nan_mask]
            weight_sum = np.sum(final_weights)
            if weight_sum > 1e-9:
                result[i] = np.sum(final_weights * final_values) / weight_sum

    return result.reshape(grid_xx.shape)


def create_edge_distance_grid(
    valid_mask: NDArray[np.bool_], cellsize: float
) -> NDArray[np.floating]:
    """Distance from each valid cell to the boundary of the valid area (EDT, metres)."""
    dist_cells = distance_transform_edt(valid_mask)
    dist_metres = dist_cells * cellsize

    return np.where(valid_mask, dist_metres, np.nan)
