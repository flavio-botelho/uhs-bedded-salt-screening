"""Cavern geometry: ellipsoidal volume, sump correction, HW/FW buffers."""

import numpy as np

from .config import FW_FACTOR, HW_FACTOR, SWELLING_FACTOR


def calculate_spheroid_volume(diameter: float, height: float) -> float:
    """V = (π / 6) · D² · H (ellipsoid of revolution)."""
    return (np.pi / 6.0) * (diameter**2) * height


def calculate_sump_volume(
    gross_volume: float,
    insolubles_percent: float,
    swelling_factor: float = SWELLING_FACTOR,
) -> float:
    """Sump volume = gross volume × insoluble fraction × bulking factor."""
    return gross_volume * (insolubles_percent / 100.0) * swelling_factor


def calculate_net_volume(
    gross_volume: float,
    insolubles_percent: float,
    swelling_factor: float = SWELLING_FACTOR,
) -> float:
    """Net usable volume = gross − sump (lower-bounded at 0)."""
    sump = calculate_sump_volume(gross_volume, insolubles_percent, swelling_factor)
    return max(0.0, gross_volume - sump)


def calculate_cavern_geometry(available_height: float, hd_ratio: float) -> dict:
    """Solve the largest cavern fitting in ``available_height`` for a given H/D.

    Layout (top-down): ``[HW_buffer] [cavern height H] [FW_buffer]``. With
    ``H = hd_ratio · D``, ``HW = HW_FACTOR · D`` and ``FW = FW_FACTOR · D``,
    the available height satisfies ``L = (hd_ratio + HW_FACTOR + FW_FACTOR) · D``.
    """
    if available_height <= 0:
        return _empty_geometry()

    diameter = available_height / (hd_ratio + HW_FACTOR + FW_FACTOR)
    if diameter <= 0:
        return _empty_geometry()

    height = hd_ratio * diameter
    hw = HW_FACTOR * diameter
    fw = FW_FACTOR * diameter
    volume = calculate_spheroid_volume(diameter, height)

    cavern_top_offset = hw
    cavern_bottom_offset = hw + height

    return {
        "diameter": diameter,
        "height": height,
        "volume": volume,
        "hw": hw,
        "fw": fw,
        "cavern_top_offset": cavern_top_offset,
        "cavern_bottom_offset": cavern_bottom_offset,
    }


def _empty_geometry() -> dict:
    return {
        "diameter": 0.0,
        "height": 0.0,
        "volume": 0.0,
        "hw": 0.0,
        "fw": 0.0,
        "cavern_top_offset": 0.0,
        "cavern_bottom_offset": 0.0,
    }
