"""Path configuration for the well-scale cavern optimization workflow.

Edit this file to point the pipeline at your local ``data/derived/`` layout.
Scientific constants live in
``src/h2_bedded_salt_screening/well_cavern_optimization/config.py`` and should
not be changed here.
"""

from pathlib import Path

from h2_bedded_salt_screening.well_cavern_optimization import PathsConfig

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "derived"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "cavern_optimization"

PATHS = PathsConfig(
    wells_data_csv=DATA_DIR / "wells" / "wells_data_corrected.csv",
    optimal_intervals_csv=OUTPUT_DIR / "optimal_cavern_intervals_analysis.csv",
    pareto_csv=OUTPUT_DIR / "pareto_frontier.csv",
)

N_WORKERS = 6
