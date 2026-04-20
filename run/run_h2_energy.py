"""Thin entrypoint: run the H2 effective-energy workflow (W4).

Usage:
    PYTHONPATH=src:. pixi run python run/run_h2_energy.py
"""

from __future__ import annotations

import sys

from h2_bedded_salt_screening.h2_effective_energy import run

from configs.h2_energy_config import PATHS


def main() -> int:
    df = run(PATHS)
    return 0 if not df.empty else 1


if __name__ == "__main__":
    sys.exit(main())
