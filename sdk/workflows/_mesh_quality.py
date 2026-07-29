"""Shared mesh-quality gate for the parametric acts (wedge, cone, diamond,
hypersonic cylinder, cylinder vortex shedding) -- the same published gates
``workflows.geometry_study`` judges its snappyHexMesh bodies by, applied here
to a locally-run ``checkMesh`` log instead of a remote one.
"""

from __future__ import annotations

import re

from workflows.geometry_study import MAX_NON_ORTHOGONALITY, MAX_SKEWNESS, mesh_gates_pass  # noqa: F401


def parse_check_mesh(text: str) -> dict:
    """Pull cell count, max non-orthogonality and max skewness out of a
    ``checkMesh`` log's text, the same patterns the snappyHexMesh path uses."""
    stats: dict = {"mesh_ok": "Mesh OK" in text}
    for pattern, key in (
        (r"cells:\s+(\d+)", "cells"),
        (r"non-orthogonality Max:\s*([0-9.]+)", "max_non_orthogonality"),
        (r"Max non-orthogonality =\s*([0-9.]+)", "max_non_orthogonality"),
        (r"Max skewness =\s*([0-9.]+)", "max_skewness"),
    ):
        match = re.search(pattern, text)
        if match:
            stats[key] = float(match.group(1))
    return stats
