"""Scientific constants for the conceptual field-layout workflow (W3)."""

# Favorability cutoff: caverns are only placed where favorability > threshold
FAVORABILITY_THRESHOLD = 6.0

# Hexagonal-grid centre-to-centre spacing, expressed as a multiple of cavern diameter
SPACING_FACTOR = 4.0

# Fallback CRS if the input raster has no CRS (SIRGAS 2000 / UTM zone 25S)
DEFAULT_CRS = "EPSG:31985"

# Reference Pareto scenarios (well '1PE0002AL', Cycle 2b) from
# the paper's per-well Pareto analysis.
SCENARIOS: tuple[dict, ...] = (
    {"name": "HD_0.75", "hd_ratio": 0.75, "net_volume": 1_132_203.49},
    {"name": "HD_2.00", "hd_ratio": 2.00, "net_volume": 636_345.09},
)
