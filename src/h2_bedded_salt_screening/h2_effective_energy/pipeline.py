"""H2 effective-energy pipeline (W4).

For each Pareto scenario shapefile (produced by W3), compute per-cavern working
mass from the Lemmon EOS and aggregate to total working mass, total energy and
effective energy.
"""

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from . import config
from .thermodynamics import calculate_h2_density


@dataclass(frozen=True)
class PathsConfig:
    allocation_dir: Path
    pareto_csv: Path
    output_csv: Path


def process_scenario(shp_path: Path, pareto_df: pd.DataFrame) -> tuple[dict | None, pd.DataFrame]:
    scenario_name = shp_path.name.replace("caverns_pareto_", "").replace(".shp", "")
    print(f"\nProcessing Scenario: {scenario_name}")

    gdf = gpd.read_file(shp_path)
    print(f"  Loaded {len(gdf)} caverns.")

    results: list[dict] = []
    for idx, row in gdf.iterrows():
        volume = row["Net_Vol"]
        hd_ratio = row["HD_Ratio"]

        matches = pareto_df[
            np.isclose(pareto_df["HD_Ratio"], hd_ratio, atol=1e-3)
            & (pareto_df["Cycle"] == config.REFERENCE_CYCLE)
            & (pareto_df["WELL"] == config.REFERENCE_WELL)
        ]
        if matches.empty:
            print(f"  Warning: no Pareto row for HD_Ratio {hd_ratio}")
            continue

        sub_top = matches.iloc[0]["Sub_Top_m"]
        sub_bottom = matches.iloc[0]["Sub_Bottom_m"]

        interval_height = sub_bottom - sub_top
        diameter = interval_height / (hd_ratio + config.HW_FACTOR + config.FW_FACTOR)

        depth_salt_top = sub_top + config.SURFACE_ELEVATION_M
        depth_roof = depth_salt_top + config.HW_FACTOR * diameter
        depth_ref = depth_roof - config.LCCS_OFFSET_M
        if depth_ref <= 0:
            print(f"  Warning: non-positive reference depth at ID {idx}; skipping.")
            continue

        p_sv_mpa = (config.OVERBURDEN_DENSITY_FACTOR * depth_ref) / 1000.0
        p_max = config.PMAX_FACTOR * p_sv_mpa
        p_min = config.PMIN_FACTOR * p_sv_mpa

        temp_k = (
            config.SURFACE_TEMP_C
            + (depth_ref / 1000.0) * config.GEOTHERMAL_GRADIENT_C_PER_KM
        ) + 273.15

        rho_max = calculate_h2_density(p_max, temp_k)
        rho_min = calculate_h2_density(p_min, temp_k)

        mass_working = volume * (rho_max - rho_min)

        results.append(
            {
                "Scenario": scenario_name,
                "Cavern_ID": idx,
                "Depth_Ref_m": depth_ref,
                "Pressure_Max_MPa": p_max,
                "Temp_C": temp_k - 273.15,
                "Mass_Working_kg": mass_working,
                "Volume_m3": volume,
            }
        )

    df_res = pd.DataFrame(results)
    if df_res.empty:
        return None, df_res

    total_mass_kg = df_res["Mass_Working_kg"].sum()
    total_vol = df_res["Volume_m3"].sum()
    total_energy_gwh = (total_mass_kg * config.LHV_H2_MJ_PER_KG / 1000.0) / config.GJ_TO_GWH
    total_energy_twh = total_energy_gwh / 1000.0
    effective_energy_twh = total_energy_twh * config.ENERGY_EFFICIENCY

    summary = {
        "Scenario": scenario_name,
        "Caverns_Count": len(df_res),
        "Total_Volume_m3": total_vol,
        "Total_Working_Mass_kg": total_mass_kg,
        "Total_Energy_TWh": total_energy_twh,
        "Effective_Energy_TWh": effective_energy_twh,
    }

    print(f"  Total Working Mass: {total_mass_kg:,.0f} kg")
    print(f"  Total Energy:       {total_energy_twh:.4f} TWh")
    return summary, df_res


def run(paths: PathsConfig) -> pd.DataFrame:
    if not paths.pareto_csv.exists():
        raise FileNotFoundError(f"Pareto CSV not found: {paths.pareto_csv}")

    shp_files = sorted(paths.allocation_dir.glob("caverns_pareto_*.shp"))
    if not shp_files:
        raise FileNotFoundError(f"No cavern shapefiles in {paths.allocation_dir}")

    pareto_df = pd.read_csv(paths.pareto_csv)
    print(f"Loaded Pareto CSV: {paths.pareto_csv}")

    summaries: list[dict] = []
    for shp in shp_files:
        summary, _ = process_scenario(shp, pareto_df)
        if summary:
            summaries.append(summary)

    df_summary = pd.DataFrame(summaries)
    if not df_summary.empty:
        paths.output_csv.parent.mkdir(parents=True, exist_ok=True)
        df_summary.to_csv(paths.output_csv, index=False)
        print(f"\nReport saved to: {paths.output_csv}")
        print(df_summary.to_string())
    return df_summary
