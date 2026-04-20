"""Well-scale cavern optimization workflow (W2).

Finds the best halite-to-halite sub-interval per (well, evaporitic cycle) and
returns both the single optimum and the Pareto frontier over (net volume,
insolubles %).
"""

from .pipeline import PathsConfig, run

__all__ = ["PathsConfig", "run"]
