"""Scientific constants for the well-scale cavern optimization workflow.

Frozen research assumptions from the thesis/paper.
"""

# Depth window for admissible intervals (m, TVDSS)
MIN_DEPTH = 500.0
MAX_DEPTH = 2000.0

# Geological constraints
MAX_INTERLAYER_THICKNESS = 20.0  # continuous non-halite above this segments the interval
MAX_INSOLUBLES_PERCENT = 35.0  # cavern zone mean insolubles cutoff

# Cavern geometry safety buffers (fractions of diameter D)
HW_FACTOR = 0.75  # hangwall / roof buffer  (H_roof = 0.75 * D)
FW_FACTOR = 0.20  # footwall / floor buffer (H_floor = 0.20 * D)

# Sump correction: insoluble material settles and bulks up by this factor
SWELLING_FACTOR = 1.3

# H/D ratio scan
HD_SCAN_MIN = 0.5
HD_SCAN_MAX = 2.0
HD_SCAN_STEP = 0.05
