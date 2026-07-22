"""The curriculum registry: surface name -> its published reference.

A geometry study asks one question of this module — "does the lab hold an
experimental reference for this body, and if so, what is it?" — and the answer
is what lets a converged force be graded against reality rather than only
against its own convergence history.

The reference lives beside each STL as ``<name>/reference.yaml``; this module
is the typed accessor for it, plus the ordered Tier-0 suite the overnight
queue walks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CURRICULUM_ROOT = Path(__file__).resolve().parent

# The Tier-0 suite, ordered cheapest-to-costliest so the overnight queue banks
# the quick, decisive cases before the long automotive and wing solves.
TIER0 = [
    "cube",
    "sphere",
    "flat_plate",
    "cylinder",
    "naca0012_wing",
    "naca4412_wing",
    "ahmed_35",
    "ahmed_25",
]

REQUIRED_FIELDS = ("name", "cd", "area_basis", "reynolds", "tolerance", "source")


# Screening geometries carry no experimental reference and never reach a
# VALIDATED tier; they exercise a workflow rather than grade against reality.
# The idealized aortic valve is registered here so the lab knows it exists
# without expecting it in the Tier-0 external-aerodynamics suite.
SCREENING = ["aortic_valve"]


def is_screening(name: str) -> bool:
    return Path(name).stem in SCREENING


def stl_path(name: str) -> Path:
    return CURRICULUM_ROOT / name / f"{name}.stl"


def reference_path(name: str) -> Path:
    return CURRICULUM_ROOT / name / "reference.yaml"


def reference_for(name: str) -> dict[str, Any] | None:
    """Return the reference dict for a body, or None if the lab holds none.

    ``name`` may be a bare stem (``cube``) or a file name (``cube.stl``); the
    stem is what indexes the curriculum.
    """
    stem = Path(name).stem
    path = reference_path(stem)
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data.setdefault("name", stem)
    return data


def solve_hints(name: str) -> dict[str, Any]:
    """The orientation and speed a body needs to match its reference regime."""
    reference = reference_for(name)
    if not reference:
        return {}
    return dict(reference.get("solve") or {})


def has_reference(name: str) -> bool:
    return reference_path(Path(name).stem).exists()


def all_references() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for name in TIER0:
        reference = reference_for(name)
        if reference:
            out[name] = reference
    return out
