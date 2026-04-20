"""Sanity checks for W1 scoring functions."""

import numpy as np

from h2_bedded_salt_screening.regional_favorability import config, scoring


def test_depth_score_peak_near_optimum():
    scores = scoring.score_depth_topo(np.array([config.DEPTH_MU]))
    assert scores[0] == np.max(scoring.score_depth_topo(np.linspace(500, 2000, 31)))


def test_depth_cutoff_scores_zero():
    scores = scoring.score_depth_topo(
        np.array([config.DEPTH_MIN_CUTOFF - 1, config.DEPTH_MAX_CUTOFF + 1])
    )
    assert np.all(scores == 0.0)


def test_thickness_cutoff_is_inclusive():
    scores = scoring.score_thickness(np.array([config.THICKNESS_MIN_CUTOFF]))
    assert scores[0] == 0.0


def test_thickness_saturates_at_ten():
    scores = scoring.score_thickness(np.array([config.THICKNESS_MAX_SCORE10 + 50]))
    assert scores[0] == 10.0


def test_insolubles_bounds():
    scores = scoring.score_insolubles_percent(
        np.array([config.INSOLUBLES_MIN_SCORE10 - 5, config.INSOLUBLES_MAX_SCORE0 + 5])
    )
    assert scores[0] == 10.0
    assert scores[1] == 0.0


def test_fault_distance_cutoff():
    scores = scoring.score_fault_distance(
        np.array([config.FAULT_DIST_CRITICAL, config.FAULT_DIST_SAFE * 2])
    )
    assert scores[0] == 0.0
    assert scores[1] == 10.0
