"""Terminal printing and CSV export for cavern optimization results."""

from pathlib import Path

import pandas as pd


RESULT_COLUMNS = [
    "WELL",
    "Ciclos_Evaporiticos",
    "Interval_Top_m",
    "Interval_Bottom_m",
    "Total_Length_m",
    "Halite_Thickness_m",
    "Insolubles_Interval_Percent",
    "Optimal_HD_Ratio",
    "Optimal_Diameter_m",
    "Optimal_Height_m",
    "Optimal_Gross_Volume_m3",
    "Optimal_Net_Volume_m3",
    "Optimal_Sump_Volume_m3",
    "Optimal_Sub_Top_m",
    "Optimal_Sub_Bottom_m",
    "Optimal_Sub_Length_m",
    "Optimal_Insolubles_Percent",
]


def print_results(df: pd.DataFrame) -> None:
    print("=" * 80)
    print("OPTIMAL CAVERN PLACEMENT ANALYSIS RESULTS")
    print("=" * 80)
    print()

    if df.empty:
        print("No valid intervals found meeting all constraints.")
        print()
        return

    print(f"Found {len(df)} valid interval(s) meeting all constraints:")
    print()

    for _, row in df.iterrows():
        print("-" * 70)
        print(f"Well: {row['WELL']}")
        print(f"Evaporitic Cycle: {row['Ciclos_Evaporiticos']}")
        print()
        print(
            f"  Full Interval: {row['Interval_Top_m']:.1f} - {row['Interval_Bottom_m']:.1f} m "
            f"({row['Total_Length_m']:.1f} m)"
        )
        print(f"  Halite Thickness: {row['Halite_Thickness_m']:.1f} m")
        print(f"  Full Interval Insolubles: {row['Insolubles_Interval_Percent']:.1f}%")
        print()
        print("  Optimal Cavern Configuration:")
        print(
            f"    Sub-interval: {row['Optimal_Sub_Top_m']:.1f} - {row['Optimal_Sub_Bottom_m']:.1f} m "
            f"({row['Optimal_Sub_Length_m']:.1f} m)"
        )
        print(f"    H/D Ratio: {row['Optimal_HD_Ratio']:.2f}")
        print(f"    Diameter: {row['Optimal_Diameter_m']:.1f} m")
        print(f"    Height: {row['Optimal_Height_m']:.1f} m")
        print(f"    Gross Volume: {row['Optimal_Gross_Volume_m3']:,.0f} m³")
        print(f"    Net Volume: {row['Optimal_Net_Volume_m3']:,.0f} m³")
        print(f"    Sump Volume: {row['Optimal_Sump_Volume_m3']:,.0f} m³")
        print(f"    Cavern Insolubles: {row['Optimal_Insolubles_Percent']:.1f}%")
        print()

    print("-" * 70)
    print()


def save_results_csv(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_ordered = df[[c for c in RESULT_COLUMNS if c in df.columns]]
    df_ordered.to_csv(output_path, index=False)
    print(f"Results saved to: {output_path}")
