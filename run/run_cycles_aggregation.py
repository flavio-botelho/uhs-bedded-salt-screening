"""Thin entrypoint: regenerate ``cycles_data.csv`` from ``wells_data_corrected.csv``.

This produces the intermediate table consumed by the regional favorability
workflow (IDW of insoluble percent across wells).

Usage:
    PYTHONPATH=src:. pixi run python run/run_cycles_aggregation.py
"""

from __future__ import annotations

from pathlib import Path

from h2_bedded_salt_screening.regional_favorability.cycles_aggregation import aggregate

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "derived"

INPUT_CSV = DATA_DIR / "wells" / "wells_data_corrected.csv"
OUTPUT_CSV = DATA_DIR / "intermediates" / "cycles_data.csv"


if __name__ == "__main__":
    aggregate(INPUT_CSV, OUTPUT_CSV)
