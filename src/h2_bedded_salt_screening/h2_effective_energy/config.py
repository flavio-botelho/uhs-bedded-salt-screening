"""Scientific constants for the H2 effective-energy workflow (W4)."""

# --- Thermodynamics: Lemmon et al. (2008) H2 equation of state ---
A_COEFFS = (
    0.05888460,
    -0.06136111,
    -0.002650473,
    0.002731125,
    0.001802374,
    -0.001150707,
    0.9588528e-4,
    -0.1109040e-6,
    0.1264403e-9,
)
B_COEFFS = (1.325, 1.87, 2.5, 2.8, 2.938, 3.14, 3.37, 3.75, 4.0)
C_COEFFS = (1.0, 1.0, 2.0, 2.0, 2.42, 2.63, 3.0, 4.0, 5.0)

R_GAS_CONSTANT = 8.314472  # J/(mol·K)
H2_MOLAR_MASS_KG_MOL = 2.01588 / 1000.0

# --- Geomechanics ---
OVERBURDEN_DENSITY_FACTOR = 2.2 * 9.8  # ≈21.56 MPa/km (ρ=2.2 g/cm³, g=9.8 m/s²)
SURFACE_TEMP_C = 25.0
GEOTHERMAL_GRADIENT_C_PER_KM = 25.0
PMAX_FACTOR = 0.80  # Pmax = 0.80 × lithostatic
PMIN_FACTOR = 0.30  # Pmin = 0.30 × lithostatic

# --- Cavern-geometry buffers (must match well_cavern_optimization.config) ---
HW_FACTOR = 0.75
FW_FACTOR = 0.20

# LCCS offset: reference depth = roof − 20 m
LCCS_OFFSET_M = 20.0

# Surface elevation of reference well (1PE0002AL)
SURFACE_ELEVATION_M = 37.6

# --- Energy ---
LHV_H2_MJ_PER_KG = 120.0
GJ_TO_GWH = 3600.0
ENERGY_EFFICIENCY = 0.50  # Effective (recoverable) energy fraction

# --- Reference Pareto scenario (matches conceptual_field_layout) ---
REFERENCE_WELL = "1PE0002AL"
REFERENCE_CYCLE = "Cycle 2b"
