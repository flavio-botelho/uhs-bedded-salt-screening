"""Cavern placement optimizer.

Finds optimal halite-to-halite sub-intervals for a single (well, cycle):

1. Split intervals on thick (>20 m) non-halite barriers.
2. Enumerate (top_halite, bottom_halite) pairs as candidate sub-intervals.
3. Scan H/D ∈ [0.5, 2.0] and pick the configuration that maximises net volume
   subject to the insoluble-fraction cutoff.
4. Return the full Pareto frontier over (net volume, insolubles %).
"""

from typing import NamedTuple

import numpy as np
import pandas as pd

from .config import (
    HD_SCAN_MAX,
    HD_SCAN_MIN,
    HD_SCAN_STEP,
    MAX_INSOLUBLES_PERCENT,
    MAX_INTERLAYER_THICKNESS,
)
from .constraints import filter_depth_range
from .data_loading import find_contiguous_groups
from .geometry import (
    calculate_cavern_geometry,
    calculate_net_volume,
    calculate_sump_volume,
)


class OptimalResult(NamedTuple):
    sub_top: float
    sub_bottom: float
    sub_length: float
    hd_ratio: float
    diameter: float
    height: float
    gross_volume: float
    net_volume: float
    sump_volume: float
    insolubles_percent: float


class ParetoSolution(NamedTuple):
    hd_ratio: float
    sub_top: float
    sub_bottom: float
    net_volume: float
    insolubles_percent: float


def get_halite_layers(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["LITO"] == "Halite"].sort_values("FROM").reset_index(drop=True)


def has_thick_interlayer(
    df: pd.DataFrame,
    sub_top: float,
    sub_bottom: float,
    max_thickness: float = MAX_INTERLAYER_THICKNESS,
) -> bool:
    """True if any contiguous non-halite block inside ``[sub_top, sub_bottom]`` exceeds ``max_thickness``."""
    layers_in_range = df[(df["TO"] > sub_top) & (df["FROM"] < sub_bottom)].copy()
    if layers_in_range.empty:
        return False

    interlayers = layers_in_range[layers_in_range["LITO"] != "Halite"].copy()
    if interlayers.empty:
        return False

    interlayers["clipped_from"] = interlayers["FROM"].clip(lower=sub_top)
    interlayers["clipped_to"] = interlayers["TO"].clip(upper=sub_bottom)
    interlayers = interlayers.sort_values("clipped_from")

    interlayers["gap_before"] = interlayers["clipped_from"] - interlayers[
        "clipped_to"
    ].shift(1)
    interlayers["new_group"] = (interlayers["gap_before"] > 0.1).fillna(True)
    interlayers["group_id"] = interlayers["new_group"].cumsum()

    group_thicknesses = interlayers.groupby("group_id").apply(
        lambda g: g["clipped_to"].max() - g["clipped_from"].min()
    )
    return (group_thicknesses > max_thickness).any()


def find_candidate_zones(df: pd.DataFrame) -> list[pd.DataFrame]:
    """Split ``df`` into zones separated by any single non-halite interval > 20 m."""
    if df.empty:
        return []

    df = df.sort_values("FROM").reset_index(drop=True)

    zones = []
    current_zone_indices: list[int] = []

    for idx, row in df.iterrows():
        thickness = row["TO"] - row["FROM"]
        is_halite = row["LITO"] == "Halite"

        if not is_halite and thickness > MAX_INTERLAYER_THICKNESS:
            if current_zone_indices:
                zones.append(df.loc[current_zone_indices].copy())
                current_zone_indices = []
        else:
            current_zone_indices.append(idx)

    if current_zone_indices:
        zones.append(df.loc[current_zone_indices].copy())

    return zones


def calculate_insolubles_at_position(
    df: pd.DataFrame,
    cavern_top_depth: float,
    cavern_bottom_depth: float,
) -> float:
    """Insolubles % inside a specific cavern position (clipped to its boundaries)."""
    if df.empty or cavern_bottom_depth <= cavern_top_depth:
        return 100.0

    cavern_layers = df[
        (df["TO"] > cavern_top_depth) & (df["FROM"] < cavern_bottom_depth)
    ].copy()
    if cavern_layers.empty:
        return 100.0

    cavern_layers["clipped_from"] = cavern_layers["FROM"].clip(lower=cavern_top_depth)
    cavern_layers["clipped_to"] = cavern_layers["TO"].clip(upper=cavern_bottom_depth)
    cavern_layers["clipped_thickness"] = (
        cavern_layers["clipped_to"] - cavern_layers["clipped_from"]
    )

    total_cavern_length = cavern_bottom_depth - cavern_top_depth
    non_halite = cavern_layers[cavern_layers["LITO"] != "Halite"]
    non_halite_thickness = non_halite["clipped_thickness"].sum()

    return (non_halite_thickness / total_cavern_length) * 100.0


def find_optimal_subinterval(
    df: pd.DataFrame,
    interval_top: float,
    interval_length: float,
    max_insolubles: float = MAX_INSOLUBLES_PERCENT,
    hd_min: float = HD_SCAN_MIN,
    hd_max: float = HD_SCAN_MAX,
    hd_step: float = HD_SCAN_STEP,
) -> OptimalResult | None:
    """Halite-to-halite sub-interval maximising net volume."""
    interval_bottom = interval_top + interval_length

    halite_layers = get_halite_layers(df)
    halite_layers = halite_layers[
        (halite_layers["FROM"] >= interval_top)
        & (halite_layers["TO"] <= interval_bottom)
    ].reset_index(drop=True)

    if halite_layers.empty:
        return None

    hd_ratios = np.arange(hd_min, hd_max + hd_step / 2, hd_step)

    best_result: OptimalResult | None = None
    best_net_volume = 0.0

    for i, top_row in halite_layers.iterrows():
        sub_top = top_row["FROM"]

        for j, bottom_row in halite_layers.iterrows():
            if j < i:
                continue

            sub_bottom = bottom_row["TO"]
            if sub_bottom <= sub_top:
                continue

            sub_length = sub_bottom - sub_top
            if sub_length < 5.0:
                continue

            if has_thick_interlayer(df, sub_top, sub_bottom):
                continue

            for hd_ratio in hd_ratios:
                geom = calculate_cavern_geometry(sub_length, hd_ratio)
                if geom["diameter"] <= 0 or geom["height"] <= 0:
                    continue

                cavern_top_depth = sub_top + geom["hw"]
                cavern_bottom_depth = cavern_top_depth + geom["height"]

                insolubles = calculate_insolubles_at_position(
                    df, cavern_top_depth, cavern_bottom_depth
                )
                if insolubles > max_insolubles:
                    continue

                gross_volume = geom["volume"]
                sump_volume = calculate_sump_volume(gross_volume, insolubles)
                net_volume = calculate_net_volume(gross_volume, insolubles)

                if net_volume > best_net_volume:
                    best_net_volume = net_volume
                    best_result = OptimalResult(
                        sub_top=sub_top,
                        sub_bottom=sub_bottom,
                        sub_length=sub_length,
                        hd_ratio=hd_ratio,
                        diameter=geom["diameter"],
                        height=geom["height"],
                        gross_volume=gross_volume,
                        net_volume=net_volume,
                        sump_volume=sump_volume,
                        insolubles_percent=insolubles,
                    )

    return best_result


def generate_pareto_solutions(
    df: pd.DataFrame,
    interval_top: float,
    interval_length: float,
) -> list[ParetoSolution]:
    """All feasible (halite-to-halite × H/D-scan) solutions for Pareto analysis."""
    interval_bottom = interval_top + interval_length

    halite_layers = get_halite_layers(df)
    halite_layers = halite_layers[
        (halite_layers["FROM"] >= interval_top)
        & (halite_layers["TO"] <= interval_bottom)
    ].reset_index(drop=True)

    if halite_layers.empty:
        return []

    hd_ratios = np.arange(HD_SCAN_MIN, HD_SCAN_MAX + HD_SCAN_STEP / 2, HD_SCAN_STEP)
    solutions: list[ParetoSolution] = []

    for i, top_row in halite_layers.iterrows():
        sub_top = top_row["FROM"]

        for j, bottom_row in halite_layers.iterrows():
            if j < i:
                continue

            sub_bottom = bottom_row["TO"]
            if sub_bottom <= sub_top:
                continue

            sub_length = sub_bottom - sub_top
            if sub_length < 5.0:
                continue

            if has_thick_interlayer(df, sub_top, sub_bottom):
                continue

            for hd_ratio in hd_ratios:
                geom = calculate_cavern_geometry(sub_length, hd_ratio)
                if geom["diameter"] <= 0 or geom["height"] <= 0:
                    continue

                cavern_top_depth = sub_top + geom["hw"]
                cavern_bottom_depth = cavern_top_depth + geom["height"]

                insolubles = calculate_insolubles_at_position(
                    df, cavern_top_depth, cavern_bottom_depth
                )
                net_volume = calculate_net_volume(geom["volume"], insolubles)

                solutions.append(
                    ParetoSolution(
                        hd_ratio=hd_ratio,
                        sub_top=sub_top,
                        sub_bottom=sub_bottom,
                        net_volume=net_volume,
                        insolubles_percent=insolubles,
                    )
                )

    return solutions


def calculate_pareto_frontier(solutions: list[ParetoSolution]) -> list[ParetoSolution]:
    """Non-dominated solutions: maximise net volume, minimise insolubles %."""
    if not solutions:
        return []

    pareto_front: list[ParetoSolution] = []

    for candidate in solutions:
        is_dominated = False
        for other in solutions:
            if candidate == other:
                continue

            if (
                other.net_volume >= candidate.net_volume
                and other.insolubles_percent <= candidate.insolubles_percent
                and (
                    other.net_volume > candidate.net_volume
                    or other.insolubles_percent < candidate.insolubles_percent
                )
            ):
                is_dominated = True
                break

        if not is_dominated:
            pareto_front.append(candidate)

    pareto_front.sort(key=lambda s: s.net_volume, reverse=True)
    return pareto_front


def analyze_zone(zone_df: pd.DataFrame) -> dict | None:
    """Best single configuration for a candidate zone (no Pareto here)."""
    if zone_df.empty:
        return None

    zone_df = filter_depth_range(zone_df)
    if zone_df.empty:
        return None

    zone_df = zone_df.sort_values("FROM").reset_index(drop=True)

    interval_top = zone_df["FROM"].min()
    interval_bottom = zone_df["TO"].max()
    interval_length = interval_bottom - interval_top

    optimal = find_optimal_subinterval(zone_df, interval_top, interval_length)
    if optimal is None:
        return None

    halite_thickness = (
        zone_df[zone_df["LITO"] == "Halite"]["TO"].values
        - zone_df[zone_df["LITO"] == "Halite"]["FROM"].values
    )
    total_halite = halite_thickness.sum() if len(halite_thickness) > 0 else 0.0

    non_halite_df = zone_df[zone_df["LITO"] != "Halite"]
    non_halite_thickness = (non_halite_df["TO"] - non_halite_df["FROM"]).sum()
    interval_insolubles = (
        (non_halite_thickness / interval_length) * 100.0 if interval_length > 0 else 0.0
    )

    return {
        "zone_df": zone_df,
        "Interval_Top_m": interval_top,
        "Interval_Bottom_m": interval_bottom,
        "Total_Length_m": interval_length,
        "Halite_Thickness_m": total_halite,
        "Insolubles_Interval_Percent": interval_insolubles,
        "Optimal_HD_Ratio": optimal.hd_ratio,
        "Optimal_Diameter_m": optimal.diameter,
        "Optimal_Height_m": optimal.height,
        "Optimal_Gross_Volume_m3": optimal.gross_volume,
        "Optimal_Net_Volume_m3": optimal.net_volume,
        "Optimal_Sump_Volume_m3": optimal.sump_volume,
        "Optimal_Sub_Top_m": optimal.sub_top,
        "Optimal_Sub_Bottom_m": optimal.sub_bottom,
        "Optimal_Sub_Length_m": optimal.sub_length,
        "Optimal_Insolubles_Percent": optimal.insolubles_percent,
    }


def analyze_well_cycle_group(df: pd.DataFrame) -> dict | None:
    """Best configuration across contiguous sub-groups and candidate zones."""
    if df.empty:
        return None

    contiguous_groups = find_contiguous_groups(df)
    all_results: list[dict] = []

    for contiguous_df in contiguous_groups:
        zones = find_candidate_zones(contiguous_df)
        for zone_df in zones:
            result = analyze_zone(zone_df)
            if result is not None:
                all_results.append(result)

    if not all_results:
        return None

    return max(all_results, key=lambda z: z["Optimal_Net_Volume_m3"])


def _process_group(args: tuple) -> tuple[dict | None, list[dict]]:
    well, cycle, group_df = args

    interval_data = analyze_well_cycle_group(group_df)
    if interval_data is None:
        return None, []

    zone_df = interval_data.pop("zone_df")
    interval_top = interval_data["Interval_Top_m"]
    interval_length = interval_data["Total_Length_m"]

    pareto_solutions = generate_pareto_solutions(zone_df, interval_top, interval_length)

    result = {"WELL": well, "Ciclos_Evaporiticos": cycle, **interval_data}
    pareto_list = [
        {
            "WELL": well,
            "Cycle": cycle,
            "HD_Ratio": sol.hd_ratio,
            "Sub_Top_m": sol.sub_top,
            "Sub_Bottom_m": sol.sub_bottom,
            "Net_Volume_m3": sol.net_volume,
            "Insolubles_Percent": sol.insolubles_percent,
        }
        for sol in pareto_solutions
    ]
    return result, pareto_list


def analyze_all_wells(
    df: pd.DataFrame, n_workers: int = 6
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run the optimization for every (well, cycle) pair with a multiprocessing Pool."""
    from multiprocessing import Pool

    df = df[df["Ciclos_Evaporiticos"] != "Unassigned"].copy()
    if df.empty:
        print("  No assigned cycles found.")
        return pd.DataFrame(), pd.DataFrame()

    grouped = df.groupby(["WELL", "Ciclos_Evaporiticos"], sort=False)
    groups = [(well, cycle, group_df) for (well, cycle), group_df in grouped]
    total_groups = len(groups)

    print(f"  Processing {total_groups} well/cycle groups with {n_workers} workers...")

    with Pool(processes=n_workers) as pool:
        results_list = pool.map(_process_group, groups)

    results: list[dict] = []
    all_pareto: list[dict] = []
    for result, pareto_list in results_list:
        if result is not None:
            results.append(result)
            all_pareto.extend(pareto_list)

    print(f"  Found {len(results)} valid intervals.")
    if not results:
        return pd.DataFrame(), pd.DataFrame()

    results_df = pd.DataFrame(results).sort_values(
        by=["Optimal_Net_Volume_m3"], ascending=[False]
    )
    pareto_df = pd.DataFrame(all_pareto) if all_pareto else pd.DataFrame()

    return results_df, pareto_df
