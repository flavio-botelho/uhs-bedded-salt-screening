# Methodology mapping

How each module in `src/h2_bedded_salt_screening/` implements the steps described in the paper.

## W1 — Regional favorability (`regional_favorability/`)

Multi-Criteria Decision Analysis (MCDA) producing a 0–10 favorability raster per evaporitic cycle.

| Paper concept | Code location |
|---|---|
| Depth cutoff (500–2000 m) | `config.DEPTH_MIN_CUTOFF`, `config.DEPTH_MAX_CUTOFF` |
| Gaussian depth score (μ≈1250, σ≈350) | `scoring.score_depth_gaussian` |
| Gross thickness cutoff (≤100 m) and 0–10 ramp | `config.THICKNESS_*`; `scoring.score_thickness` |
| Insolubles scoring (~26% favorable, ~70% poor) | `config.INSOLUBLES_*`; `scoring.score_insolubles` |
| Distance-to-fault cutoff (≤200 m) | `config.FAULT_DIST_*`; `scoring.score_distance` |
| Distance-to-cycle-boundary (<500 m) | `config.EDGE_DIST_*` |
| Distance-to-urban (≤1000 m) | `config.URBAN_DIST_*` |
| Criterion weights (fault 2.0, thickness 2.0, depth 2.0, insol 1.5, urban 1.5, edge 1.0) | `config.PARAM_WEIGHTS` |
| IDW interpolation of well-scale criteria | `interpolation.idw_interpolate` |
| Combined favorability raster per cycle | `pipeline.compute_favorability` |

## W2 — Well-scale cavern optimization (`well_cavern_optimization/`)

For every (well, cycle), find the halite-to-halite sub-interval that maximises net cavern volume subject to safety constraints.

| Paper concept | Code location |
|---|---|
| Depth window 800–2200 m | `config.MIN_DEPTH`, `config.MAX_DEPTH`; `constraints.filter_depth_range` |
| 20 m non-halite interlayer as stratigraphic barrier | `config.MAX_INTERLAYER_THICKNESS`; `optimizer.has_thick_interlayer`, `optimizer.find_candidate_zones` |
| Halite-to-halite boundary condition | `optimizer.get_halite_layers`, `find_optimal_subinterval` |
| Ellipsoidal cavern V = (π/6)·D²·H | `geometry.calculate_spheroid_volume` |
| H/D scan [0.5, 2.0] in 0.05 steps | `config.HD_SCAN_*`; `optimizer.find_optimal_subinterval` |
| Safety buffers H_roof=0.75·D, H_floor=0.20·D | `config.HW_FACTOR`, `config.FW_FACTOR`; `geometry.calculate_cavern_geometry` |
| Insoluble exclusion (cavern-zone mean ≤40%) | `config.MAX_INSOLUBLES_PERCENT`; `optimizer.calculate_insolubles_at_position` |
| Sump correction (bulking factor 1.3) | `config.SWELLING_FACTOR`; `geometry.calculate_sump_volume` |
| Per-well Pareto frontier (net volume ↑, insolubles ↓) | `optimizer.generate_pareto_solutions`, `calculate_pareto_frontier` |

## W3 — Conceptual field layout (`conceptual_field_layout/`)

Hexagonal cavern packing over the favorability raster.

| Paper concept | Code location |
|---|---|
| Favorability threshold (>6.0) | `config.FAVORABILITY_THRESHOLD`; `pipeline._allocate_scenario` |
| Hex packing, centre-to-centre = 4·D | `config.SPACING_FACTOR`; `layout.generate_hexagonal_grid` |
| Diameter from ellipsoidal V and H/D | `layout.calculate_diameter` |
| Scenarios HD=0.75 vs HD=2.00 from reference well Pareto | `config.SCENARIOS` |
| Output: circular cavern footprints as shapefiles | `pipeline._allocate_scenario` |

## W4 — H₂ effective energy (`h2_effective_energy/`)

Per-cavern working-gas mass and aggregated energy.

| Paper concept | Code location |
|---|---|
| Reference depth D_ref = D_roof − 20 m (LCCS) | `config.LCCS_OFFSET_M`; `pipeline.process_scenario` |
| Surface T=25 °C, gradient 25 °C/km | `config.SURFACE_TEMP_C`, `config.GEOTHERMAL_GRADIENT_C_PER_KM` |
| Overburden ρ=2200 kg/m³, g=9.8 m/s² | `config.OVERBURDEN_DENSITY_FACTOR` |
| P_max=0.80·P_sv, P_min=0.30·P_sv | `config.PMAX_FACTOR`, `config.PMIN_FACTOR` |
| Lemmon et al. (2008) H₂ EOS | `thermodynamics.calculate_h2_density`; `config.A_COEFFS`, `B_COEFFS`, `C_COEFFS` |
| LHV_H₂ = 120 MJ/kg; η_cycle = 0.5 | `config.LHV_H2_MJ_PER_KG`, `config.ENERGY_EFFICIENCY` |
| Working mass = V · (ρ_max − ρ_min); energy totals | `pipeline.process_scenario`, `pipeline.run` |
