"""Aggregate per-well lithology intervals into per-cycle statistics.

Consumes ``wells_data_corrected.csv`` (one row per lithology interval) and
produces ``cycles_data.csv`` (one row per well with one column group per cycle:
FROM, TO, Thickness, Halite_Sum, Insolubles_Percent, Number_Interlayers,
Mean_Interlayers_Thickness, Max_Interlayer_Thickness).

``cycles_data.csv`` is a derived product consumed by the favorability pipeline
(insoluble-percent IDW interpolation).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from . import config


def calculate_interlayer_metrics(
    cycle_df: pd.DataFrame,
) -> tuple[int, float, float]:
    """Count, mean, and max thickness of contiguous non-halite interlayer blocks."""
    if cycle_df.empty:
        return 0, 0.0, 0.0

    cycle_df = cycle_df.copy()
    cycle_df["is_halite"] = cycle_df["LITO"] == "Halite"
    cycle_df["group"] = (
        cycle_df["is_halite"] != cycle_df["is_halite"].shift()
    ).cumsum()

    non_halite_df = cycle_df[~cycle_df["is_halite"]]
    if non_halite_df.empty:
        return 0, 0.0, 0.0

    interlayer_thicknesses = non_halite_df.groupby("group").apply(
        lambda g: g["TO"].max() - g["FROM"].min(), include_groups=False
    )

    number_interlayers = len(interlayer_thicknesses)
    mean_thickness = interlayer_thicknesses.mean() if number_interlayers > 0 else 0.0
    max_thickness = interlayer_thicknesses.max() if number_interlayers > 0 else 0.0

    return number_interlayers, mean_thickness, max_thickness


def calculate_cycle_data(well_df: pd.DataFrame, cycle_name: str) -> dict[str, Any]:
    """Compute cycle-level metrics for a single (well, cycle) pair."""
    cycle_df = well_df[well_df["Ciclos_Evaporiticos"] == cycle_name].copy()
    if cycle_df.empty:
        return {}

    cycle_df = cycle_df.sort_values("FROM").reset_index(drop=True)

    cycle_from = cycle_df["FROM"].min()
    cycle_to = cycle_df["TO"].max()
    thickness = cycle_to - cycle_from

    halite_df = cycle_df[cycle_df["LITO"] == "Halite"]
    halite_sum = (halite_df["TO"] - halite_df["FROM"]).sum()

    insolubles_percent = (
        (1.0 - (halite_sum / thickness)) * 100 if thickness > 0 else 0.0
    )

    num_interlayers, mean_interlayer, max_interlayer = calculate_interlayer_metrics(
        cycle_df
    )

    suffix = cycle_name.replace(" ", "_")

    return {
        f"FROM_{suffix}": cycle_from,
        f"TO_{suffix}": cycle_to,
        f"Thickness_{suffix}": thickness,
        f"Halite_Sum_{suffix}": halite_sum,
        f"Insolubles_Percent_{suffix}": insolubles_percent,
        f"Number_Interlayers_{suffix}": num_interlayers,
        f"Mean_Interlayers_Thickness_{suffix}": mean_interlayer,
        f"Max_Interlayer_Thickness_{suffix}": max_interlayer,
    }


def process_well(well_df: pd.DataFrame) -> dict[str, Any]:
    """Aggregate every cycle in ``config.CYCLES`` for a single well."""
    well_name = well_df["WELL"].iloc[0]
    result: dict[str, Any] = {"WELL": well_name}

    for cycle in config.CYCLES:
        result.update(calculate_cycle_data(well_df, cycle))

    return result


def aggregate(input_csv: Path, output_csv: Path) -> pd.DataFrame:
    """Compute per-well cycle statistics and write them to ``output_csv``."""
    print(f"Reading lithology intervals from: {input_csv}")
    df = pd.read_csv(input_csv)

    wells = df["WELL"].unique()
    print(f"Processing {len(wells)} wells")

    results = []
    for well in wells:
        well_df = df[df["WELL"] == well]
        well_result = process_well(well_df)

        cycles_present = [
            c for c in config.CYCLES if f"FROM_{c.replace(' ', '_')}" in well_result
        ]
        if cycles_present:
            results.append(well_result)
            print(f"  {well}: {len(cycles_present)} cycles - {cycles_present}")
        else:
            print(f"  {well}: no cycles, skipping")

    output_df = pd.DataFrame(results)

    cols = ["WELL"]
    for cycle in config.CYCLES:
        suffix = cycle.replace(" ", "_")
        cycle_cols = [
            f"FROM_{suffix}",
            f"TO_{suffix}",
            f"Thickness_{suffix}",
            f"Halite_Sum_{suffix}",
            f"Insolubles_Percent_{suffix}",
            f"Number_Interlayers_{suffix}",
            f"Mean_Interlayers_Thickness_{suffix}",
            f"Max_Interlayer_Thickness_{suffix}",
        ]
        cols.extend([c for c in cycle_cols if c in output_df.columns])

    output_df = output_df[cols]

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_csv, index=False)
    print(f"\nWrote: {output_csv}")

    return output_df
