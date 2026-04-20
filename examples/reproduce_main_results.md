# Reproducing the main results

Step-by-step recipe for reproducing the figures and tables in the paper from a clean clone.

## 0 — Environment

```bash
git clone <repo-url> h2-bedded-salt-screening
cd h2-bedded-salt-screening
pixi install
```

## 1 — Place derived data

Copy the derived products into `data/derived/` following the layout in [`docs/data_dictionary.md`](../docs/data_dictionary.md). Raw ANP/SGB files are not needed for reproduction; only the derived CSVs, ASCII grids and shapefiles are.

Minimum required files:

- `data/derived/wells/wells_data_corrected.csv`
- `data/derived/wells/well_xy.csv`
- `data/derived/grids/*.asc`  (one set per evaporitic cycle)
- `data/derived/faults/*.shp`
- `data/derived/urban/urban_areas.shp`

## 2 — Regenerate cycle aggregation (optional; included as a derived file)

```bash
PYTHONPATH=src:. pixi run python run/run_cycles_aggregation.py
```

Produces `data/derived/intermediates/cycles_data.csv`.

## 3 — W1 · Regional favorability

```bash
PYTHONPATH=src:. pixi run python run/run_regional_favorability.py
```

Writes `outputs/favorability/favorability_Cycle_*.asc` for all six cycles.

## 4 — W2 · Well-scale cavern optimization

```bash
PYTHONPATH=src:. pixi run python run/run_well_cavern_optimization.py
```

Writes `outputs/cavern_optimization/optimal_cavern_intervals_analysis.csv` and `pareto_frontier.csv`.

## 5 — W3 · Conceptual field layout

Depends on W1 (`favorability_Cycle_2b.asc`) and implicitly on the reference-well Pareto solution hard-coded in `conceptual_field_layout/config.py`.

```bash
PYTHONPATH=src:. pixi run python run/run_field_layout.py
```

Writes `outputs/field_layout/caverns_pareto_HD_0.75.shp` and `caverns_pareto_HD_2.00.shp`.

## 6 — W4 · H₂ effective energy

Depends on W2 (Pareto CSV) and W3 (cavern shapefiles).

```bash
PYTHONPATH=src:. pixi run python run/run_h2_energy.py
```

Writes `outputs/h2_energy/h2_capacity_pareto.csv`.

## 7 — Expected headline numbers

For the Cycle 2b / well 1PE0002AL reference scenarios used in the paper:

| Scenario | Caverns | Total energy (TWh) | Effective energy (TWh) |
|---|---|---|---|
| HD_0.75 | 27 | ≈ 11.04 | ≈ 5.52 |
| HD_2.00 | 76 | ≈ 17.09 | ≈ 8.54 |

Small floating-point deltas (~1e-15) are expected across platforms; structural numbers should match.
