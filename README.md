# h2-bedded-salt-screening

Screening workflows for **underground hydrogen storage (UHS) in heterogeneous bedded salt**, applied to the Aptian Paripueira evaporites of the Maceió Formation, Fazenda Guindaste Low, onshore Alagoas Sub-basin (NE Brazil).

This repository accompanies the manuscript:

> **Testing safety criteria for planning underground hydrogen storage in bedded salt deposits: the Fazenda Guindaste onshore salt basin, Northeast Brazil.** *Submitted, 2026.*

## Workflows

The package exposes four sequential workflows. Each lives in its own subpackage under `src/h2_bedded_salt_screening/` and is driven by a thin runner in `run/` plus a path config in `configs/`.

| # | Workflow | Package | Runner |
|---|---|---|---|
| W1 | Regional favorability (MCDA) | `regional_favorability` | `run/run_regional_favorability.py` |
| W2 | Well-scale cavern interval optimization | `well_cavern_optimization` | `run/run_well_cavern_optimization.py` |
| W3 | Conceptual cavern field layout (hex packing) | `conceptual_field_layout` | `run/run_field_layout.py` |
| W4 | H₂ effective energy | `h2_effective_energy` | `run/run_h2_energy.py` |

An auxiliary preprocessing runner, `run/run_cycles_aggregation.py`, regenerates
`data/derived/intermediates/cycles_data.csv` from
`data/derived/wells/wells_data_corrected.csv` for use in W1.

Data flow: **cycle aggregation → W1 favorability grids; W2 → per-well Pareto frontier; W3 consumes the W1 Cycle 2b favorability grid plus reference W2 scenarios encoded in `conceptual_field_layout/config.py`; W4 consumes W2 + W3 → energy summary.**
See [`docs/methodology_mapping.md`](docs/methodology_mapping.md) for how each
code module maps to the paper's methodology, and
[`docs/data_dictionary.md`](docs/data_dictionary.md) for the expected inputs
and outputs.

## Installation

The project is developed with [Pixi](https://pixi.sh/) on Linux, which
reproduces the authored environment. A standard pip-based installation is also
supported for users who prefer a conventional Python workflow.

```bash
# Option A — Pixi (recommended, matches the authored environment)
pixi install

# Option B — pip, in a fresh Python ≥3.11 environment
pip install -e .
```

## Running the workflows

All runners read their paths from the matching module in `configs/`. Edit those files to point at your local `data/` and `outputs/` layout, then run them either through Pixi or through a regular Python environment:

```bash
# Optional preprocessing step for W1 inputs
PYTHONPATH=src:. pixi run python run/run_cycles_aggregation.py

# With Pixi
PYTHONPATH=src:. pixi run python run/run_regional_favorability.py
PYTHONPATH=src:. pixi run python run/run_well_cavern_optimization.py
PYTHONPATH=src:. pixi run python run/run_field_layout.py
PYTHONPATH=src:. pixi run python run/run_h2_energy.py

# With a regular Python environment
PYTHONPATH=src:. python run/run_cycles_aggregation.py
PYTHONPATH=src:. python run/run_regional_favorability.py
PYTHONPATH=src:. python run/run_well_cavern_optimization.py
PYTHONPATH=src:. python run/run_field_layout.py
PYTHONPATH=src:. python run/run_h2_energy.py
```

See [`examples/reproduce_main_results.md`](examples/reproduce_main_results.md) for a full reproduction recipe.

## Data

- `data/raw/` — **not versioned**. Raw well and structural data come from Brazil's public repositories (ANP / SGB REATE). See `docs/data_dictionary.md` for fetch instructions.
- `data/derived/` — author-generated, reproducible products required by the workflows (cycle tables, favorability input grids, fault meshes, urban polygons, well coordinates).
- `data/sample/` — optional lightweight samples for smoke tests.
- `outputs/` — generally gitignored; created by the runners.

Raw ANP/SGB data is **never committed** to this repository.

## Repository layout

```
h2-bedded-salt-screening/
├── src/h2_bedded_salt_screening/   # Python package (4 subpackages, one per workflow)
├── configs/                        # local path configs (Python modules)
├── run/                            # thin runner scripts
├── data/                           # raw (gitignored), derived, sample
├── outputs/                        # generated artefacts (mostly gitignored)
├── docs/                           # methodology mapping, data dictionary, supporting documentation
├── examples/                       # reproduction recipes
└── tests/                          # lightweight sanity tests
```

## Citation

If you use this code, please cite the software (`CITATION.cff`) and the paper above.

## License

MIT — see [`LICENSE`](LICENSE).
