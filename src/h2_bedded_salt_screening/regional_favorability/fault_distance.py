"""3D fault-distance computation.

Distance from each grid cell centre (x, y, z=elevation) to the nearest vertex
of any fault mesh under ``faults_dir``.
"""

from pathlib import Path

import numpy as np
import trimesh
from numpy.typing import NDArray
from scipy.spatial import cKDTree

from . import config


def compute_fault_distance_grid(
    elevation_grid: NDArray[np.floating],
    profile: dict,
    faults_dir: Path,
) -> NDArray[np.floating]:
    """Distance (m) from each valid cell to the nearest fault-mesh vertex."""
    print("  Computing 3D fault distance...")

    all_vertices = _load_fault_vertices(faults_dir)

    if all_vertices is None or len(all_vertices) == 0:
        print("    No fault files found. Returning safe distance grid.")
        safe_grid = np.full_like(elevation_grid, config.FAULT_DIST_SAFE * 1.1)
        safe_grid[np.isnan(elevation_grid)] = np.nan
        return safe_grid

    print(f"    Loaded {len(all_vertices)} fault vertices.")

    try:
        fault_tree = cKDTree(all_vertices)
    except Exception as e:
        print(f"    Error building KD-Tree: {e}. Returning safe distance grid.")
        safe_grid = np.full_like(elevation_grid, config.FAULT_DIST_SAFE * 1.1)
        safe_grid[np.isnan(elevation_grid)] = np.nan
        return safe_grid

    transform = profile["transform"]
    cols, rows = profile["width"], profile["height"]
    x_centers = transform.c + transform.a / 2 + np.arange(cols) * transform.a
    y_centers = transform.f + transform.e / 2 + np.arange(rows) * transform.e

    query_points = []
    indices = []

    for r in range(rows):
        for c in range(cols):
            z_val = elevation_grid[r, c]
            if not np.isnan(z_val):
                query_points.append([x_centers[c], y_centers[r], z_val])
                indices.append((r, c))

    if not query_points:
        return np.full_like(elevation_grid, np.nan)

    query_array = np.array(query_points)
    print(f"    Querying distances for {len(query_array)} valid cells...")

    try:
        distances, _ = fault_tree.query(query_array, k=1, workers=-1)
    except Exception as e:
        print(f"    Error in KD-Tree query: {e}")
        distances = np.full(len(query_array), config.FAULT_DIST_SAFE * 1.5)

    result = np.full_like(elevation_grid, np.nan)
    for idx, (r, c) in enumerate(indices):
        dist = distances[idx]
        if np.isinf(dist) or np.isnan(dist):
            result[r, c] = config.FAULT_DIST_SAFE * 1.5
        else:
            result[r, c] = dist

    print("    Fault distance computation complete.")
    return result


def _load_fault_vertices(faults_dir: Path) -> NDArray[np.floating] | None:
    if not faults_dir.exists():
        print(f"    Faults directory not found: {faults_dir}")
        return None

    obj_files = list(faults_dir.glob("*.obj")) + list(faults_dir.glob("*.OBJ"))

    if not obj_files:
        print(f"    No OBJ files in {faults_dir}")
        return None

    vertex_list = []

    for obj_file in obj_files:
        try:
            mesh = trimesh.load_mesh(obj_file, process=False)
            if (
                not mesh.is_empty
                and hasattr(mesh, "vertices")
                and len(mesh.vertices) > 0
            ):
                vertex_list.append(mesh.vertices)
        except Exception as e:
            print(f"    Warning: Could not load {obj_file.name}: {e}")

    if not vertex_list:
        return None

    return np.vstack(vertex_list)
