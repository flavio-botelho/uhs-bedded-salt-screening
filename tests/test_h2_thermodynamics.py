"""Sanity checks for W3 layout and W4 H2 density."""

import math

from h2_bedded_salt_screening.conceptual_field_layout import config as w3_config
from h2_bedded_salt_screening.conceptual_field_layout.layout import (
    calculate_diameter,
    generate_hexagonal_grid,
)
from h2_bedded_salt_screening.h2_effective_energy import calculate_h2_density


def test_diameter_inverts_ellipsoidal_volume():
    D, hd = 100.0, 1.5
    V = math.pi / 6.0 * D**2 * (hd * D)
    assert math.isclose(calculate_diameter(V, hd), D, rel_tol=1e-10)


def test_hexagonal_grid_spacing_matches_config():
    pts = generate_hexagonal_grid((0.0, 0.0, 100.0, 100.0), spacing=20.0)
    assert len(pts) > 0
    assert w3_config.SPACING_FACTOR == 4.0


def test_h2_density_rises_with_pressure():
    T = 320.0
    rho_low = calculate_h2_density(5.0, T)
    rho_high = calculate_h2_density(20.0, T)
    assert rho_high > rho_low > 0


def test_h2_density_plausible_magnitude_at_cavern_conditions():
    rho = calculate_h2_density(pressure_mpa=15.0, temp_k=320.0)
    assert 5.0 < rho < 20.0


def test_h2_density_zero_guard():
    assert calculate_h2_density(0.0, 300.0) == 0.0
    assert calculate_h2_density(10.0, 0.0) == 0.0
