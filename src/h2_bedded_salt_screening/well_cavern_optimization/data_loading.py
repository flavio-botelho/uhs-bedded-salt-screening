"""Load per-well lithology intervals and split them into contiguous depth groups."""

from pathlib import Path

import pandas as pd


def load_well_data(filepath: Path) -> pd.DataFrame:
    """Load ``wells_data_corrected.csv`` (WELL, FROM, TO, LITO, Ciclos_Evaporiticos)."""
    df = pd.read_csv(filepath)
    df["Ciclos_Evaporiticos"] = df["Ciclos_Evaporiticos"].fillna("Unassigned")
    df["Ciclos_Evaporiticos"] = df["Ciclos_Evaporiticos"].replace("", "Unassigned")
    return df


def find_contiguous_groups(
    df: pd.DataFrame, tolerance: float = 0.5
) -> list[pd.DataFrame]:
    """Split intervals into contiguous depth groups (gap <= ``tolerance`` metres)."""
    if df.empty:
        return []

    df = df.sort_values("FROM").reset_index(drop=True)

    groups = []
    current_indices = [0]
    current_end = df.iloc[0]["TO"]

    for idx in range(1, len(df)):
        row = df.iloc[idx]
        gap = row["FROM"] - current_end

        if gap <= tolerance:
            current_indices.append(idx)
            current_end = max(current_end, row["TO"])
        else:
            groups.append(df.iloc[current_indices].copy())
            current_indices = [idx]
            current_end = row["TO"]

    if current_indices:
        groups.append(df.iloc[current_indices].copy())

    return groups
