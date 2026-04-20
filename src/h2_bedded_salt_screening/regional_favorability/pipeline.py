"""Regional favorability pipeline.

Builds a multi-criteria favorability grid per evaporite cycle by combining
six parameter grids with hard cutoffs and a weighted linear overlay.

Paths are supplied via a :class:`PathsConfig` dataclass; scientific constants
live in :mod:`.config`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from . import config, scoring
from .fault_distance import compute_fault_distance_grid
from .grids import (
    create_edge_distance_grid,
    create_grid_coordinates,
    idw_interpolation,
    read_asc,
    write_asc,
)
from .urban_distance import compute_urban_distance_grid


@dataclass(frozen=True)
class PathsConfig:
    """Filesystem paths consumed by the regional favorability workflow."""

    grids_dir: Path
    faults_dir: Path
    urban_shapefile: Path
    well_xy_csv: Path
    cycles_data_csv: Path
    output_dir: Path


def compute_favorability(cycle: str, paths: PathsConfig) -> Path | None:
    """Compute the favorability grid for a single evaporitic cycle."""
    print(f"\n{'=' * 60}")
    print(f"Processing {cycle}")
    print("=" * 60)

    asc_prefix = config.CYCLE_TO_ASC_PREFIX.get(cycle)
    if asc_prefix is None:
        print(f"Unknown cycle: {cycle}")
        return None

    elev_file = paths.grids_dir / f"{asc_prefix}_elevation.asc"
    thick_file = paths.grids_dir / f"{asc_prefix}_thickness.asc"

    try:
        elev_grid, profile = read_asc(elev_file)
        thick_grid, _ = read_asc(thick_file)
    except FileNotFoundError as e:
        print(f"Input files not found: {e}")
        return None
    except Exception as e:
        print(f"Error reading ASC files: {e}")
        return None

    valid_mask = ~np.isnan(elev_grid) & ~np.isnan(thick_grid)
    cellsize = abs(profile["transform"][0])

    print(f"  Grid size: {profile['width']} x {profile['height']}")
    print(f"  Valid cells: {np.sum(valid_mask)}")

    param_grids: dict[str, NDArray[np.floating] | None] = {}
    param_grids["depth_topo"] = np.abs(elev_grid)
    param_grids["thickness"] = thick_grid
    param_grids["edge_distance"] = create_edge_distance_grid(valid_mask, cellsize)
    param_grids["fault_distance"] = compute_fault_distance_grid(
        elev_grid, profile, paths.faults_dir
    )
    param_grids["urban_distance"] = compute_urban_distance_grid(
        valid_mask, profile, paths.urban_shapefile
    )
    param_grids.update(
        _interpolate_well_parameters(cycle, profile, valid_mask, paths)
    )

    available_params = {k: v for k, v in param_grids.items() if v is not None}
    print(f"\n  Available parameters: {list(available_params.keys())}")

    effective_weights = _compute_effective_weights(available_params.keys())
    print(f"  Effective weights: {effective_weights}")

    scored_grids, favorability = _compute_weighted_favorability(
        available_params, effective_weights, valid_mask
    )
    favorability = _apply_hard_cutoffs(favorability, param_grids, valid_mask)

    paths.output_dir.mkdir(parents=True, exist_ok=True)
    cycle_suffix = cycle.replace(" ", "_")

    for param_name, scored_grid in scored_grids.items():
        output_file = paths.output_dir / f"scored_{param_name}_{cycle_suffix}.asc"
        write_asc(output_file, scored_grid, profile)

    fav_file = paths.output_dir / f"favorability_{cycle_suffix}.asc"
    write_asc(fav_file, favorability, profile)

    valid_fav = favorability[~np.isnan(favorability)]
    if len(valid_fav) > 0:
        print(f"\n  Favorability stats for {cycle}:")
        print(f"    Min: {valid_fav.min():.2f}")
        print(f"    Max: {valid_fav.max():.2f}")
        print(f"    Mean: {valid_fav.mean():.2f}")
        print(f"    Cells with favorability = 0: {np.sum(valid_fav == 0)}")

    return fav_file


def run(paths: PathsConfig, cycles: list[str] | None = None) -> dict[str, Path | None]:
    """Run the favorability workflow over a list of cycles (default: all)."""
    cycles = cycles if cycles is not None else config.CYCLES
    results: dict[str, Path | None] = {}
    for cycle in cycles:
        try:
            results[cycle] = compute_favorability(cycle, paths)
        except Exception as e:
            print(f"Error processing {cycle}: {e}")
            results[cycle] = None
    return results


def _interpolate_well_parameters(
    cycle: str,
    profile: dict,
    valid_mask: NDArray[np.bool_],
    paths: PathsConfig,
) -> dict[str, NDArray[np.floating] | None]:
    """IDW-interpolate well-based parameters (currently only insolubles %)."""
    print("  Interpolating well-based parameters...")

    result: dict[str, NDArray[np.floating] | None] = {}

    try:
        df_wells_xy = pd.read_csv(paths.well_xy_csv)
        df_cycles = pd.read_csv(paths.cycles_data_csv)
    except FileNotFoundError as e:
        print(f"    Error loading well data: {e}")
        return result

    df_merged = df_cycles.merge(df_wells_xy, on="WELL", how="left")
    df_merged = df_merged[~df_merged["WELL"].isin(config.EXCLUDED_WELLS)]

    cycle_excluded = config.EXCLUDED_WELLS_PER_CYCLE.get(cycle, [])
    if cycle_excluded:
        df_merged = df_merged[~df_merged["WELL"].isin(cycle_excluded)]

    col_suffix = config.CYCLE_TO_COLUMN_SUFFIX.get(cycle)
    if col_suffix is None:
        return result

    grid_xx, grid_yy = create_grid_coordinates(profile)

    param_columns = {
        "insolubles_percent": f"Insolubles_Percent_{col_suffix}",
    }

    for param_name, col_name in param_columns.items():
        if col_name not in df_merged.columns:
            print(f"    Column {col_name} not found")
            result[param_name] = None
            continue

        df_valid = df_merged.dropna(subset=["X", "Y", col_name])
        if df_valid.empty:
            print(f"    No data for {param_name}")
            result[param_name] = None
            continue

        print(f"    Interpolating {param_name} from {len(df_valid)} wells")
        interpolated = idw_interpolation(
            df_valid["X"].values,
            df_valid["Y"].values,
            df_valid[col_name].values,
            grid_xx,
            grid_yy,
        )

        interpolated = np.where(valid_mask, interpolated, np.nan)
        result[param_name] = interpolated

    return result


def _apply_hard_cutoffs(
    favorability: NDArray[np.floating],
    param_grids: dict[str, NDArray[np.floating] | None],
    valid_mask: NDArray[np.bool_],
) -> NDArray[np.floating]:
    """Force favorability to zero where any critical safety constraint fails."""
    result = favorability.copy()
    zero_mask = np.zeros_like(favorability, dtype=bool)

    if param_grids.get("depth_topo") is not None:
        depth = param_grids["depth_topo"]
        depth_fail = (depth < config.DEPTH_MIN_CUTOFF) | (
            depth > config.DEPTH_MAX_CUTOFF
        )
        zero_mask |= np.nan_to_num(depth_fail, nan=False).astype(bool)

    if param_grids.get("fault_distance") is not None:
        fault_fail = param_grids["fault_distance"] <= config.FAULT_DIST_CRITICAL
        zero_mask |= np.nan_to_num(fault_fail, nan=False).astype(bool)

    if param_grids.get("edge_distance") is not None:
        edge_fail = param_grids["edge_distance"] < config.EDGE_DIST_CRITICAL
        zero_mask |= np.nan_to_num(edge_fail, nan=False).astype(bool)

    if param_grids.get("urban_distance") is not None:
        urban_fail = param_grids["urban_distance"] <= config.URBAN_DIST_CRITICAL
        zero_mask |= np.nan_to_num(urban_fail, nan=False).astype(bool)

    if param_grids.get("thickness") is not None:
        # Paper convention: thickness <= THICKNESS_MIN_CUTOFF is excluded
        thickness_fail = param_grids["thickness"] <= config.THICKNESS_MIN_CUTOFF
        zero_mask |= np.nan_to_num(thickness_fail, nan=False).astype(bool)

    result[zero_mask & valid_mask] = 0.0

    cutoff_count = np.sum(zero_mask & valid_mask)
    print(f"\n  Hard cutoffs applied: {cutoff_count} cells forced to favorability = 0")

    return result


def _compute_effective_weights(
    available_params: list[str] | set[str],
) -> dict[str, float]:
    """Renormalise configured weights over whichever parameters are available."""
    weights = {}
    total = 0.0

    for param in available_params:
        if param in config.PARAM_WEIGHTS:
            weights[param] = config.PARAM_WEIGHTS[param]
            total += weights[param]

    if total > 0:
        weights = {k: v / total for k, v in weights.items()}

    return weights


def _compute_weighted_favorability(
    param_grids: dict[str, NDArray[np.floating]],
    weights: dict[str, float],
    valid_mask: NDArray[np.bool_],
) -> tuple[dict[str, NDArray[np.floating]], NDArray[np.floating]]:
    """Apply per-parameter scoring and combine with the weighted linear overlay."""
    score_funcs = {
        "depth_topo": scoring.score_depth_topo,
        "thickness": scoring.score_thickness,
        "insolubles_percent": scoring.score_insolubles_percent,
        "fault_distance": scoring.score_fault_distance,
        "edge_distance": scoring.score_edge_distance,
        "urban_distance": scoring.score_urban_distance,
    }

    scored_grids = {}
    template = next(iter(param_grids.values()))
    favorability = np.zeros_like(template, dtype=float)

    for param_name, grid in param_grids.items():
        if param_name not in weights or param_name not in score_funcs:
            continue

        scored = score_funcs[param_name](grid)
        scored_grids[param_name] = scored

        weight = weights[param_name]
        favorability += np.nan_to_num(scored, nan=0.0) * weight

    favorability = np.where(valid_mask, favorability, np.nan)
    favorability = np.clip(favorability, 0.0, 10.0)

    return scored_grids, favorability
