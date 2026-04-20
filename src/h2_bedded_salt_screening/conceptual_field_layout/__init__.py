"""Conceptual field-layout workflow (W3).

Places ellipsoidal caverns on a favorability grid using a hexagonal packing
whose spacing is 4× the cavern diameter; filters candidates by a favorability
threshold and exports Shapefiles per Pareto scenario.
"""

from .pipeline import PathsConfig, run

__all__ = ["PathsConfig", "run"]
