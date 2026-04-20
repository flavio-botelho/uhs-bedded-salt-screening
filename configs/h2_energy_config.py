"""Path configuration for the H2 effective-energy workflow (W4)."""

from pathlib import Path

from h2_bedded_salt_screening.h2_effective_energy import PathsConfig

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ALLOCATION_DIR = PROJECT_ROOT / "outputs" / "field_layout"
PARETO_CSV = PROJECT_ROOT / "outputs" / "cavern_optimization" / "pareto_frontier.csv"
OUTPUT_CSV = PROJECT_ROOT / "outputs" / "h2_energy" / "h2_capacity_pareto.csv"

PATHS = PathsConfig(
    allocation_dir=ALLOCATION_DIR,
    pareto_csv=PARETO_CSV,
    output_csv=OUTPUT_CSV,
)
