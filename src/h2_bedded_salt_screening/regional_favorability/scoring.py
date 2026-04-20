"""Scoring functions for favorability parameters.

All functions accept numpy arrays and return scores in the range [0, 10].
NaN values in input arrays are preserved as NaN in outputs.
"""

import numpy as np
from numpy.typing import NDArray

from . import config


def score_depth_topo(depth: NDArray[np.floating]) -> NDArray[np.floating]:
    """Score depth to top with a Gaussian (μ=1250 m, σ=350 m; hard 0 outside [500, 2000] m)."""
    depth = np.asarray(depth, dtype=float)
    score = 10.0 * np.exp(-0.5 * ((depth - config.DEPTH_MU) / config.DEPTH_SIGMA) ** 2)
    score = np.where(np.isnan(depth), np.nan, score)
    score = np.where(depth < config.DEPTH_MIN_CUTOFF, 0.0, score)
    score = np.where(depth > config.DEPTH_MAX_CUTOFF, 0.0, score)
    return score


def score_thickness(thickness: NDArray[np.floating]) -> NDArray[np.floating]:
    """Score cycle thickness linearly from 100 m (0) to 600 m (10); <=100 m excluded."""
    thickness = np.asarray(thickness, dtype=float)
    min_val = config.THICKNESS_MIN_SCORE0
    max_val = config.THICKNESS_MAX_SCORE10

    score = np.zeros_like(thickness)
    if max_val > min_val:
        score = 10.0 * (thickness - min_val) / (max_val - min_val)

    score = np.where(np.isnan(thickness), np.nan, score)
    score = np.where(thickness <= config.THICKNESS_MIN_CUTOFF, 0.0, score)
    return np.clip(score, 0.0, 10.0)


def score_insolubles_percent(insolubles: NDArray[np.floating]) -> NDArray[np.floating]:
    """Score insolubles inverse-linearly (<=26% -> 10; >=70% -> 0)."""
    insolubles = np.asarray(insolubles, dtype=float)
    min_val = config.INSOLUBLES_MIN_SCORE10
    max_val = config.INSOLUBLES_MAX_SCORE0

    score = np.zeros_like(insolubles)
    if max_val > min_val:
        score = 10.0 * (1.0 - (insolubles - min_val) / (max_val - min_val))

    score = np.where(np.isnan(insolubles), np.nan, score)
    return np.clip(score, 0.0, 10.0)


def score_fault_distance(distance: NDArray[np.floating]) -> NDArray[np.floating]:
    """Score distance to nearest fault linearly (<=200 m -> 0; >=1000 m -> 10)."""
    distance = np.asarray(distance, dtype=float)
    min_val = config.FAULT_DIST_CRITICAL
    max_val = config.FAULT_DIST_SAFE

    score = np.zeros_like(distance)
    if max_val > min_val:
        score = 10.0 * (distance - min_val) / (max_val - min_val)

    score = np.where(np.isnan(distance), np.nan, score)
    return np.clip(score, 0.0, 10.0)


def score_edge_distance(distance: NDArray[np.floating]) -> NDArray[np.floating]:
    """Score distance to cycle edge linearly (<=500 m -> 0; >=2000 m -> 10)."""
    distance = np.asarray(distance, dtype=float)
    min_val = config.EDGE_DIST_CRITICAL
    max_val = config.EDGE_DIST_SAFE

    score = np.zeros_like(distance)
    if max_val > min_val:
        score = 10.0 * (distance - min_val) / (max_val - min_val)

    score = np.where(np.isnan(distance), np.nan, score)
    return np.clip(score, 0.0, 10.0)


def score_urban_distance(distance: NDArray[np.floating]) -> NDArray[np.floating]:
    """Score distance to nearest urban area linearly (<=1000 m -> 0; >=3000 m -> 10)."""
    distance = np.asarray(distance, dtype=float)
    min_val = config.URBAN_DIST_CRITICAL
    max_val = config.URBAN_DIST_SAFE

    score = np.zeros_like(distance)
    if max_val > min_val:
        score = 10.0 * (distance - min_val) / (max_val - min_val)

    score = np.where(np.isnan(distance), np.nan, score)
    return np.clip(score, 0.0, 10.0)
