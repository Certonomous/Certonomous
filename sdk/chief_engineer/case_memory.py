"""Case memory: what Certonomous has actually run, and what it learned.

Every record here corresponds to solver runs executed on this machine and
recorded in ``docs/NUMERICS_KNOWLEDGE.md`` / ``docs/OPENFOAM.md``.  Nothing is
hypothetical — the point of this module is that when the chiefs reason about
an unfamiliar geometry, the cases they retrieve are real, nameable, and
auditable.

Similarity is deliberately crude and explainable (feature overlap, not a
learned metric): a demo that claims sophistication it cannot show is worse
than one that shows exactly what it does.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(frozen=True)
class CaseRecord:
    name: str
    geometry: str
    dimensionality: str          # 2d | 3d
    body_type: str               # bluff | streamlined | mixed
    flow: str                    # steady-laminar | steady-turbulent | unsteady
    reynolds: tuple[float, float]
    meshing: str                 # blockMesh-ogrid | snappyHexMesh
    cells: tuple[int, int]
    results: str
    validated_against: str
    source: str

    def as_dict(self) -> dict[str, Any]:
        return {key: getattr(self, key) for key in self.__dataclass_fields__}


CASE_MEMORY: tuple[CaseRecord, ...] = (
    CaseRecord(
        name="cylinder-2d-laminar",
        geometry="circular cylinder", dimensionality="2d", body_type="bluff",
        flow="steady-laminar", reynolds=(10.0, 40.0),
        meshing="blockMesh-ogrid", cells=(600, 21600),
        results="Cd 3.011 / 2.161 / 1.815 / 1.618 at Re 10 / 20 / 30 / 40; "
                "grid-converged to Cd ≈ 2.156 at Re 20",
        validated_against="Tritton experimental drag data",
        source="docs/NUMERICS_KNOWLEDGE.md #1, #2",
    ),
    CaseRecord(
        name="cylinder-2d-past-regime",
        geometry="circular cylinder", dimensionality="2d", body_type="bluff",
        flow="unsteady", reynolds=(100.0, 200.0),
        meshing="blockMesh-ogrid", cells=(2400, 2400),
        results="Re 100 converges onto the unstable symmetric branch "
                "(Cd 1.181, physical ≈ 1.3–1.4); Re 200 fails to converge "
                "(residual 1e-3, Cd oscillation 1e-2)",
        validated_against="known steady-wake instability above Re ≈ 47",
        source="docs/NUMERICS_KNOWLEDGE.md #3, #4",
    ),
    CaseRecord(
        name="motorbike-3d-turbulent",
        geometry="motorBike + rider", dimensionality="3d", body_type="bluff",
        flow="steady-turbulent", reynolds=(3.0e5, 3.0e5),
        meshing="snappyHexMesh", cells=(353578, 353578),
        results="Cd 0.4167 ± 0.0013, Cl 0.0641 ± 0.0011 (95% final-window "
                "envelopes); max non-orthogonality 65.0, max skewness 8.94",
        validated_against="OpenFOAM tutorial reference configuration",
        source="docs/NUMERICS_KNOWLEDGE.md #7",
    ),
)


@dataclass
class Match:
    case: CaseRecord
    score: float
    shared: tuple[str, ...]
    differing: tuple[str, ...]


def _features(**query) -> dict[str, Any]:
    return {key: value for key, value in query.items() if value is not None}


def retrieve(*, geometry_kind: str | None = None, dimensionality: str | None = None,
             body_type: str | None = None, flow: str | None = None,
             reynolds: float | None = None, meshing: str | None = None,
             limit: int = 3) -> list[Match]:
    """Rank real cases by explainable feature overlap with the query."""
    query = _features(dimensionality=dimensionality, body_type=body_type,
                      flow=flow, meshing=meshing)
    matches: list[Match] = []
    for case in CASE_MEMORY:
        shared, differing = [], []
        for key, value in query.items():
            (shared if getattr(case, key) == value else differing).append(
                f"{key}={value}" if getattr(case, key) == value
                else f"{key}: {getattr(case, key)} vs {value}")
        score = len(shared) / max(1, len(query))
        if reynolds is not None:
            low, high = case.reynolds
            if low <= reynolds <= high:
                shared.append(f"Re {reynolds:.0f} inside {low:.0f}–{high:.0f}")
                score += 0.5
            else:
                decades = abs(_log10(reynolds) - _log10((low + high) / 2))
                differing.append(f"Re {reynolds:.0f} is {decades:.1f} decades from "
                                 f"this case's {low:.0f}–{high:.0f}")
                score += max(0.0, 0.25 - 0.1 * decades)
        matches.append(Match(case, score, tuple(shared), tuple(differing)))
    matches.sort(key=lambda item: item.score, reverse=True)
    return matches[:limit]


def _log10(value: float) -> float:
    import math
    return math.log10(max(value, 1e-12))
