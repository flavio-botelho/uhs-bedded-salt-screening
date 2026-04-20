"""Thin entrypoint: run the well-scale cavern optimization workflow (W2).

Usage:
    PYTHONPATH=src:. pixi run python run/run_well_cavern_optimization.py
"""

from __future__ import annotations

import sys

from h2_bedded_salt_screening.well_cavern_optimization import run

from configs.well_optimization_config import N_WORKERS, PATHS


def main() -> int:
    results_df, _ = run(PATHS, n_workers=N_WORKERS)
    return 0 if not results_df.empty else 1


if __name__ == "__main__":
    sys.exit(main())
