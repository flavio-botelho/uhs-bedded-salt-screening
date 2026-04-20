"""Conceptual field-layout pipeline: place hexagonally-packed caverns on a favorability grid."""

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio

from . import config
from .layout import calculate_diameter, generate_hexagonal_grid, sample_grid_value


@dataclass(frozen=True)
class PathsConfig:
    favorability_grid: Path
    output_dir: Path


def _allocate_scenario(
    src,
    scenario: dict,
    threshold: float,
    spacing_factor: float,
    default_crs: str,
    output_dir: Path,
) -> int:
    name = scenario["name"]
    hd = scenario["hd_ratio"]
    vol = scenario["net_volume"]

    diameter = calculate_diameter(vol, hd)
    height = diameter * hd
    spacing = diameter * spacing_factor

    print(f"\n--- Scenario: {name} ---")
    print(f"  Volume: {vol:,.0f} m³ | HD: {hd}")
    print(f"  Diameter: {diameter:.2f} m | Height: {height:.2f} m | Spacing: {spacing:.2f} m")

    candidates = generate_hexagonal_grid(src.bounds, spacing)
    print(f"  Candidates generated: {len(candidates)}")

    nodata = src.nodata
    valid: list[dict] = []
    for pt in candidates:
        val = sample_grid_value(src, pt.x, pt.y)
        if val is None or val == nodata or np.isnan(val):
            continue
        if val > threshold:
            valid.append({"geometry": pt, "fav_score": float(val)})

    print(f"  Valid caverns (fav > {threshold}): {len(valid)}")
    if not valid:
        return 0

    gdf = gpd.GeoDataFrame(valid)
    gdf["Scenario"] = name
    gdf["HD_Ratio"] = hd
    gdf["Net_Vol"] = vol
    gdf["Diameter"] = diameter
    gdf["Height"] = height
    gdf["geometry"] = gdf.geometry.buffer(diameter / 2.0)

    if src.crs:
        gdf.set_crs(src.crs, inplace=True)
    else:
        print(f"  Raster has no CRS; assigning default {default_crs}")
        gdf.set_crs(default_crs, inplace=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"caverns_pareto_{name}.shp"
    gdf.to_file(out_path)
    print(f"  Saved: {out_path}")
    return len(valid)


def run(paths: PathsConfig, scenarios: tuple[dict, ...] | None = None) -> dict[str, int]:
    """Place caverns for every Pareto scenario on the favorability grid."""
    if scenarios is None:
        scenarios = config.SCENARIOS

    if not paths.favorability_grid.exists():
        raise FileNotFoundError(f"Favorability grid not found: {paths.favorability_grid}")

    counts: dict[str, int] = {}
    with rasterio.open(paths.favorability_grid) as src:
        print(f"Grid loaded: bounds={src.bounds} nodata={src.nodata}")
        for scenario in scenarios:
            counts[scenario["name"]] = _allocate_scenario(
                src,
                scenario,
                config.FAVORABILITY_THRESHOLD,
                config.SPACING_FACTOR,
                config.DEFAULT_CRS,
                paths.output_dir,
            )
    return counts
