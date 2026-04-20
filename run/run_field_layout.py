"""Thin entrypoint: run the conceptual field-layout workflow (W3).

Usage:
    PYTHONPATH=src:. pixi run python run/run_field_layout.py
"""

from __future__ import annotations

import sys

from h2_bedded_salt_screening.conceptual_field_layout import run

from configs.field_layout_config import PATHS


def main() -> int:
    print("=" * 60)
    print("Conceptual Field Layout — UHS in bedded salt")
    print("=" * 60)
    counts = run(PATHS)
    total = sum(counts.values())
    print("\n" + "=" * 60)
    for name, n in counts.items():
        print(f"  {name}: {n} caverns")
    print(f"  total: {total}")
    print("=" * 60)
    return 0 if total > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
