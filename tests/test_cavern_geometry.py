"""Sanity checks for W2 cavern geometry and constraints."""

import math

import pandas as pd

from h2_bedded_salt_screening.well_cavern_optimization import config, constraints, geometry


def test_spheroid_volume_formula():
    v = geometry.calculate_spheroid_volume(diameter=10.0, height=20.0)
    assert math.isclose(v, math.pi / 6.0 * 100.0 * 20.0, rel_tol=1e-12)


def test_sump_and_net_volume():
    gross = 1000.0
    sump = geometry.calculate_sump_volume(gross, insolubles_percent=20.0)
    expected_sump = 1000.0 * 0.20 * config.SWELLING_FACTOR
    assert math.isclose(sump, expected_sump, rel_tol=1e-12)

    net = geometry.calculate_net_volume(gross, insolubles_percent=20.0)
    assert math.isclose(net, gross - expected_sump, rel_tol=1e-12)


def test_net_volume_lower_bounded_at_zero():
    assert geometry.calculate_net_volume(100.0, insolubles_percent=200.0) == 0.0


def test_cavern_geometry_fits_available_height():
    hd = 1.0
    L = 100.0
    geom = geometry.calculate_cavern_geometry(available_height=L, hd_ratio=hd)
    fit = geom["hw"] + geom["height"] + geom["fw"]
    assert math.isclose(fit, L, rel_tol=1e-12)
    assert math.isclose(geom["hw"], config.HW_FACTOR * geom["diameter"], rel_tol=1e-12)
    assert math.isclose(geom["fw"], config.FW_FACTOR * geom["diameter"], rel_tol=1e-12)


def test_depth_filter_keeps_only_contained_intervals():
    df = pd.DataFrame(
        {
            "FROM": [700.0, 1000.0, 2100.0],
            "TO": [900.0, 1200.0, 2300.0],
            "LITO": ["Halite", "Halite", "Halite"],
        }
    )
    filtered = constraints.filter_depth_range(df)
    assert len(filtered) == 1
    assert filtered.iloc[0]["FROM"] == 1000.0
