"""Shared mesh-quality gate for the parametric acts (wedge, cone, diamond,
hypersonic cylinder, cylinder vortex shedding) -- the same published gates
``workflows.geometry_study`` judges its snappyHexMesh bodies by, applied here
to a locally-run ``checkMesh`` log instead of a remote one.
"""

from __future__ import annotations

import re

from workflows.geometry_study import (  # noqa: F401
    MAX_NON_ORTHOGONALITY, MAX_SKEWNESS, mesh_gates_pass, mesh_quality_reading)


def parse_check_mesh(text: str) -> dict:
    """Pull cell count, max non-orthogonality and max skewness out of a
    ``checkMesh`` log's text, the same patterns the snappyHexMesh path uses.

    Also pulls the two readings the recipe does NOT pin -- the face count and
    the number of faces checkMesh itself called severely non-orthogonal -- so
    ``mesh_quality_reading`` has something to fall back on when the reported
    maximum turns out to be a ``meshQualityDict`` ceiling. checkMesh prints the
    severe-face line only when the count is non-zero, so its absence means zero
    and is recorded as zero rather than as missing.
    """
    stats: dict = {"mesh_ok": "Mesh OK" in text}
    for pattern, key in (
        (r"cells:\s+(\d+)", "cells"),
        (r"faces:\s+(\d+)", "faces"),
        (r"non-orthogonality Max:\s*([0-9.]+)", "max_non_orthogonality"),
        (r"Max non-orthogonality =\s*([0-9.]+)", "max_non_orthogonality"),
        (r"non-orthogonality Max:\s*[0-9.]+\s+average:\s*([0-9.]+)",
         "average_non_orthogonality"),
        (r"Max skewness =\s*([0-9.]+)", "max_skewness"),
        (r"severely non-orthogonal \(> [0-9.]+ degrees\) faces:\s*(\d+)",
         "severe_non_ortho_faces"),
    ):
        match = re.search(pattern, text)
        if match:
            stats[key] = float(match.group(1))
    if "severe_non_ortho_faces" not in stats and "max_non_orthogonality" in stats:
        stats["severe_non_ortho_faces"] = 0.0
    return stats
