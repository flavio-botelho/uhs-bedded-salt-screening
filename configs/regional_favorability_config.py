"""Path configuration for the regional favorability workflow.

Edit this file to point the pipeline at your local ``data/derived/`` layout.
Scientific constants live in
``src/h2_bedded_salt_screening/regional_favorability/config.py`` and should
not be changed here.
"""

from pathlib import Path

from h2_bedded_salt_screening.regional_favorability import PathsConfig

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "derived"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "favorability"

PATHS = PathsConfig(
    grids_dir=DATA_DIR / "grids",
    faults_dir=DATA_DIR / "faults",
    urban_shapefile=DATA_DIR / "urban" / "urban_areas.shp",
    well_xy_csv=DATA_DIR / "wells" / "well_xy.csv",
    cycles_data_csv=DATA_DIR / "intermediates" / "cycles_data.csv",
    output_dir=OUTPUT_DIR,
)

# Cycles to process (default: all six from config.CYCLES)
CYCLES: list[str] | None = None
