"""Thin entrypoint: run the regional favorability workflow (W1).

Usage:
    PYTHONPATH=src:. pixi run python run/run_regional_favorability.py
"""

from __future__ import annotations

import sys

from h2_bedded_salt_screening.regional_favorability import run

from configs.regional_favorability_config import CYCLES, PATHS


def main() -> int:
    print("=" * 60)
    print("Regional Favorability Analysis — UHS in bedded salt")
    print("=" * 60)
    print(f"Output: {PATHS.output_dir}")

    results = run(PATHS, cycles=CYCLES)
    errors = sum(1 for v in results.values() if v is None)
    successes = len(results) - errors

    print("\n" + "=" * 60)
    print(f"Success: {successes}   Errors: {errors}")
    print("=" * 60)
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
