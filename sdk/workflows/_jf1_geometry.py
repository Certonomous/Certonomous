"""Is the uploaded surface the section the jet-flap calculations ran on?

THIS FILE HOLDS NO ARITHMETIC ON PURPOSE, for the same reason ``_jf1_numbers``
holds none: the measurement it exposes lives beside the thing it measures, at

    cases/demo-surfaces/generate_demo_stls.py

which is the script that WRITES the surface. That script already had to know
what the solved section is, because it now refuses to write anything else. A
second copy of "chord 1.0, h/c 0.005" here would be a constant that agrees with
the generator today and disagrees with it the first time either moves, which is
exactly how one number becomes two numbers that disagree.

WHY A RUNTIME CHECK EXISTS AT ALL. Sanaa's demo-mode binding requires the
geometry stage to render the uploaded surface AS the solved geometry. The
generator's refusal makes that true for the file the lab ships. It says nothing
about a file somebody else uploads, and the act may not assume the upload is
the demo body just because it usually is. So the act measures what actually
arrived and speaks accordingly: bound, or honestly not bound.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

#: The single implementation. A moved tree fails loudly here, once.
_SOURCE = Path("/home/ubuntu/Certonomous/cases/demo-surfaces"
               "/generate_demo_stls.py")

#: Where the control room resolves a body by name and where an upload lands.
#: This is the server's own line (``HERE.parent / "geometry"`` in
#: ``chief_engineer/server.py``), and it is NOT the directory the generator
#: writes to. The two are different directories holding copies of the same
#: file, and the act has to read the one the interface actually serves.
STAGING = Path("/home/ubuntu/Certonomous/sdk/geometry")


def _load():
    if not _SOURCE.is_file():
        raise ImportError(
            f"the surface generator is not at {_SOURCE}; the act cannot say "
            f"whether an uploaded body is the solved section")
    name = "generate_demo_stls"
    existing = sys.modules.get(name)
    if existing is not None and getattr(existing, "__file__", None) == str(_SOURCE):
        return existing
    spec = importlib.util.spec_from_file_location(name, _SOURCE)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load the surface generator from {_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_impl = _load()

measure_blown_slot = _impl.measure_blown_slot
SOLVED_CHORD_M = _impl.SOLVED_CHORD_M
SOLVED_H_OVER_C = _impl.SOLVED_H_OVER_C
SOLVED_GEOMETRY_TOL = _impl.SOLVED_GEOMETRY_TOL


def is_solved_section(surface: str) -> bool:
    """True only if the named uploaded surface IS the solved jet-flap section.

    Returns False rather than raising for anything it cannot measure: a body
    in another format, a name that resolves nowhere, a file that is not a
    binary STL. Every one of those means the act does not know the upload is
    the solved section, and "does not know" and "is not" lead to the same
    sentence on screen. Only a positive measurement unlocks the claim.
    """
    name = Path(str(surface)).name
    if not name:
        return False
    target = (STAGING / name).resolve()
    if STAGING.resolve() not in target.parents or not target.is_file():
        return False
    try:
        chord, h_over_c = measure_blown_slot(target)
    except Exception:                                    # noqa: BLE001
        return False
    return (abs(chord - SOLVED_CHORD_M) <= SOLVED_GEOMETRY_TOL
            and abs(h_over_c - SOLVED_H_OVER_C) <= SOLVED_GEOMETRY_TOL)


__all__ = ["STAGING", "SOLVED_CHORD_M", "SOLVED_H_OVER_C",
           "SOLVED_GEOMETRY_TOL", "measure_blown_slot", "is_solved_section"]
