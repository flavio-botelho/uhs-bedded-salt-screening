"""Default parameters for the regional favorability workflow.

These values define the baseline configuration used to reproduce the results
reported in the study. They can be modified for testing, sensitivity analyses,
or adaptation to other datasets. Project-specific paths and run settings live
in ``configs/regional_favorability_config.py``.
"""

# -----------------------------------------------------------------------------
# Cycles
# -----------------------------------------------------------------------------
CYCLES = ["Cycle 1", "Cycle 2", "Cycle 2b", "Cycle 3", "Cycle 3b", "Cycle 4"]

CYCLE_TO_ASC_PREFIX = {
    "Cycle 1": "ciclo1",
    "Cycle 2": "ciclo2",
    "Cycle 2b": "ciclo2b",
    "Cycle 3": "ciclo3",
    "Cycle 3b": "ciclo3b",
    "Cycle 4": "ciclo4",
}

CYCLE_TO_COLUMN_SUFFIX = {
    "Cycle 1": "Cycle_1",
    "Cycle 2": "Cycle_2",
    "Cycle 2b": "Cycle_2b",
    "Cycle 3": "Cycle_3",
    "Cycle 3b": "Cycle_3b",
    "Cycle 4": "Cycle_4",
}

# Pinch-out border wells with unrepresentative single-layer halite and 0% insolubles
EXCLUDED_WELLS = ["1RD0002AL", "1CPA0001AL"]

# 1MPE0003AL excluded from Cycle 1 because the well didn't intercept the full cycle
EXCLUDED_WELLS_PER_CYCLE = {
    "Cycle 1": ["1MPE0003AL"],
}

# -----------------------------------------------------------------------------
# Scoring thresholds
# -----------------------------------------------------------------------------

# Depth to top (m, TVDSS positive downward)
DEPTH_MU = 1250.0
DEPTH_SIGMA = 350.0
DEPTH_MIN_CUTOFF = 500.0
DEPTH_MAX_CUTOFF = 2000.0

# Cycle thickness (m)
THICKNESS_MIN_SCORE0 = 100.0
THICKNESS_MAX_SCORE10 = 600.0
THICKNESS_MIN_CUTOFF = 100.0  # cells with thickness <= this are excluded

# Insolubles (%)
INSOLUBLES_MIN_SCORE10 = 26.0
INSOLUBLES_MAX_SCORE0 = 70.0

# Distance to faults (m, 3D)
FAULT_DIST_CRITICAL = 200.0
FAULT_DIST_SAFE = 1000.0

# Distance to cycle lateral boundary (m)
EDGE_DIST_CRITICAL = 500.0
EDGE_DIST_SAFE = 2000.0

# Distance to urban areas / infrastructure (m)
URBAN_DIST_CRITICAL = 1000.0
URBAN_DIST_SAFE = 3000.0

# -----------------------------------------------------------------------------
# Parameter weights (normalised to sum 1.0; final favorability in [0, 10])
# -----------------------------------------------------------------------------
PARAM_WEIGHTS = {
    "fault_distance": 0.20,
    "thickness": 0.20,
    "depth_topo": 0.20,
    "insolubles_percent": 0.15,
    "urban_distance": 0.15,
    "edge_distance": 0.10,
}

assert abs(sum(PARAM_WEIGHTS.values()) - 1.0) < 1e-6, "Weights must sum to 1.0"

# -----------------------------------------------------------------------------
# Grid processing
# -----------------------------------------------------------------------------
NODATA_VALUE = -99999.0
IDW_POWER = 2
IDW_K_NEIGHBORS = 8
