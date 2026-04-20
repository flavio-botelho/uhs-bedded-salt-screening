"""Geological constraint checks for cavern intervals."""

import pandas as pd

from .config import (
    MAX_DEPTH,
    MAX_INSOLUBLES_PERCENT,
    MAX_INTERLAYER_THICKNESS,
    MIN_DEPTH,
)


def filter_depth_range(
    df: pd.DataFrame, min_depth: float = MIN_DEPTH, max_depth: float = MAX_DEPTH
) -> pd.DataFrame:
    """Keep intervals fully contained in ``[min_depth, max_depth]``."""
    return df[(df["FROM"] >= min_depth) & (df["TO"] <= max_depth)].copy()


def calculate_halite_thickness(df: pd.DataFrame) -> float:
    halite_intervals = df[df["LITO"] == "Halite"]
    return (halite_intervals["TO"] - halite_intervals["FROM"]).sum()


def get_interlayers(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["LITO"] != "Halite"].copy()


def calculate_max_interlayer_thickness(df: pd.DataFrame) -> float:
    interlayers = get_interlayers(df)
    if interlayers.empty:
        return 0.0
    return (interlayers["TO"] - interlayers["FROM"]).max()


def check_interlayer_constraint(
    df: pd.DataFrame, max_thickness: float = MAX_INTERLAYER_THICKNESS
) -> bool:
    return calculate_max_interlayer_thickness(df) <= max_thickness


def calculate_insolubles_percentage(df: pd.DataFrame) -> float:
    if df.empty:
        return 100.0

    total_length = df["TO"].max() - df["FROM"].min()
    if total_length <= 0:
        return 100.0

    interlayers = get_interlayers(df)
    non_halite_thickness = (interlayers["TO"] - interlayers["FROM"]).sum()
    return (non_halite_thickness / total_length) * 100.0


def check_insolubles_constraint(
    df: pd.DataFrame, max_percent: float = MAX_INSOLUBLES_PERCENT
) -> bool:
    return calculate_insolubles_percentage(df) <= max_percent
