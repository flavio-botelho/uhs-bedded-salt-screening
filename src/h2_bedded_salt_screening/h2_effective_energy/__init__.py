"""H2 effective-energy workflow (W4).

Per-cavern working mass and aggregated energy capacity using the Lemmon et al.
(2008) H2 equation of state and site-specific geomechanical pressure limits.
"""

from .pipeline import PathsConfig, run
from .thermodynamics import calculate_h2_density

__all__ = ["PathsConfig", "run", "calculate_h2_density"]
