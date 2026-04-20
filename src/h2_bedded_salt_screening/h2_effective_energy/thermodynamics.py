"""H2 density from Lemmon et al. (2008) equation of state."""

from .config import (
    A_COEFFS,
    B_COEFFS,
    C_COEFFS,
    H2_MOLAR_MASS_KG_MOL,
    R_GAS_CONSTANT,
)


def calculate_h2_density(pressure_mpa: float, temp_k: float) -> float:
    """H2 density (kg/m³) from the Lemmon et al. (2008) EOS.

    Z = 1 + Σ aᵢ (100/T)^bᵢ · P^cᵢ ;  ρ = P / (Z·R·T) · M.
    """
    if pressure_mpa <= 0 or temp_k <= 0:
        return 0.0

    z_sum = sum(
        A * ((100.0 / temp_k) ** B) * (pressure_mpa**C)
        for A, B, C in zip(A_COEFFS, B_COEFFS, C_COEFFS)
    )
    z = 1.0 + z_sum

    pressure_pa = pressure_mpa * 1_000_000.0
    molar_density = pressure_pa / (z * R_GAS_CONSTANT * temp_k)
    return molar_density * H2_MOLAR_MASS_KG_MOL
