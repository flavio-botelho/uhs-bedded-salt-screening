"""Regional favorability analysis (Workflow 1).

Multi-criteria decision analysis (MCDA) over evaporite cycles for UHS site
screening. Produces a favorability grid in [0, 10] per cycle, with cells
violating hard safety cutoffs forced to 0.
"""

from .pipeline import PathsConfig, compute_favorability, run
from .scoring import (
    score_depth_topo,
    score_edge_distance,
    score_fault_distance,
    score_insolubles_percent,
    score_thickness,
    score_urban_distance,
)
from .grids import read_asc, write_asc

__all__ = [
    "PathsConfig",
    "compute_favorability",
    "run",
    "score_depth_topo",
    "score_thickness",
    "score_insolubles_percent",
    "score_fault_distance",
    "score_edge_distance",
    "score_urban_distance",
    "read_asc",
    "write_asc",
]
