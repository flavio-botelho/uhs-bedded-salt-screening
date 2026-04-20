"""Cavern optimization pipeline: load wells → optimize → save results and Pareto frontier."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import config
from .data_loading import load_well_data
from .optimizer import ParetoSolution, analyze_all_wells, calculate_pareto_frontier
from .output import print_results, save_results_csv


@dataclass(frozen=True)
class PathsConfig:
    wells_data_csv: Path
    optimal_intervals_csv: Path
    pareto_csv: Path


def _compute_per_group_pareto(pareto_df: pd.DataFrame) -> pd.DataFrame:
    frontier_rows: list[dict] = []

    for (well, cycle), group in pareto_df.groupby(["WELL", "Cycle"]):
        solutions = [
            ParetoSolution(
                hd_ratio=row["HD_Ratio"],
                sub_top=row["Sub_Top_m"],
                sub_bottom=row["Sub_Bottom_m"],
                net_volume=row["Net_Volume_m3"],
                insolubles_percent=row["Insolubles_Percent"],
            )
            for _, row in group.iterrows()
        ]
        frontier = calculate_pareto_frontier(solutions)

        for s in frontier:
            frontier_rows.append(
                {
                    "WELL": well,
                    "Cycle": cycle,
                    "HD_Ratio": s.hd_ratio,
                    "Sub_Top_m": s.sub_top,
                    "Sub_Bottom_m": s.sub_bottom,
                    "Net_Volume_m3": s.net_volume,
                    "Insolubles_Percent": s.insolubles_percent,
                }
            )

    return pd.DataFrame(frontier_rows)


def run(paths: PathsConfig, n_workers: int = 6) -> tuple[pd.DataFrame, pd.DataFrame]:
    print()
    print("=" * 70)
    print("OPTIMAL CAVERN PLACEMENT ANALYSIS")
    print("Underground Hydrogen Storage in Bedded Salt Formations")
    print("=" * 70)
    print()

    print("Loading well data...")
    df = load_well_data(paths.wells_data_csv)
    print(f"Loaded {len(df)} lithology intervals from {df['WELL'].nunique()} wells.")
    print()

    print("Analysis Configuration:")
    print(f"  Depth range: {config.MIN_DEPTH}-{config.MAX_DEPTH} m")
    print(f"  Max interlayer thickness: {config.MAX_INTERLAYER_THICKNESS} m")
    print(f"  Max insolubles: {config.MAX_INSOLUBLES_PERCENT}%")
    print(f"  Swelling factor: {config.SWELLING_FACTOR}")
    print()

    print("Running optimization...")
    results_df, pareto_df = analyze_all_wells(df, n_workers=n_workers)

    if not pareto_df.empty:
        frontier_df = _compute_per_group_pareto(pareto_df)
        paths.pareto_csv.parent.mkdir(parents=True, exist_ok=True)
        frontier_df.to_csv(paths.pareto_csv, index=False)
        print(
            f"Pareto frontier ({len(frontier_df)} solutions) saved to: {paths.pareto_csv}"
        )

    print()
    print_results(results_df)

    if not results_df.empty:
        save_results_csv(results_df, paths.optimal_intervals_csv)

    print("Analysis complete.")
    print()

    return results_df, pareto_df
