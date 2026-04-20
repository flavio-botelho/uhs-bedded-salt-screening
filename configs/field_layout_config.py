"""Path configuration for the conceptual field-layout workflow (W3).

Scientific constants (favorability threshold, spacing factor, Pareto scenarios)
live in ``src/h2_bedded_salt_screening/conceptual_field_layout/config.py``.
"""

from pathlib import Path

from h2_bedded_salt_screening.conceptual_field_layout import PathsConfig

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# W3 consumes the Cycle-2b favorability grid produced by W1.
FAVORABILITY_GRID = PROJECT_ROOT / "outputs" / "favorability" / "favorability_Cycle_2b.asc"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "field_layout"

PATHS = PathsConfig(
    favorability_grid=FAVORABILITY_GRID,
    output_dir=OUTPUT_DIR,
)
