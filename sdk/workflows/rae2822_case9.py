"""RAE 2822 transonic aerofoil, AGARD AR-138 Case 9 -- compressible RANS
against digitised experiment.

WHAT THIS IS AND WHY IT EXISTS
------------------------------
``workflows.transonic_airfoil`` records, in its own docstring, that the lab
chose a NACA 0012 for its transonic family because no citable digitised
RAE 2822 Cp dataset could be sourced inside one task's budget, and that no
RAE 2822 comparison is therefore claimed anywhere. That dataset has since been
sourced and validated; see
``demo-output/website/campaign/F12_runs/reference/decode_tape.py`` for its
provenance and the four checks it passes before being admitted.

This module is the case built on it. Unlike F2 (a NACA 0012 graded on shock
POSITION alone, against a literature-recalled inviscid number, in a band), this
is a point comparison of the whole surface pressure distribution, the shock
location and the integrated coefficients against experiment.

THE WALL-INTERFERENCE CORRECTION, WHICH IS THE CLASSIC TRAP ON THIS CASE
------------------------------------------------------------------------
Case 9 was run in a slotted-wall tunnel and its published conditions circulate
in more than one corrected form. Two are used here, both stated, both solved:

  ``TAPE``      M = 0.730, alpha = 2.79 deg.  This is what the reference data
                itself carries. The AFOSR-HTTM tape stores XMREF (free-stream
                Mach) = 0.730, ALPHAG (geometric incidence) = 3.19 deg and
                ALPHAC (corrected incidence) = 2.79 deg for case 9. The
                correction is applied to INCIDENCE ONLY; there is one Mach
                number on the tape and it is the measured one. The Cp values
                are non-dimensionalised on that same measured free stream.

  ``WORKSHOP``  M = 0.734, alpha = 2.79 deg.  The 1st-5th International
                Workshops on High-Order CFD Methods specify case C2.2 (also
                ADIGMA MTC5) at "corrected flow conditions, namely Mach number
                M = 0.734, angle of attack = 2.79 deg, with the same Reynolds
                number", i.e. the same incidence correction plus a Mach
                correction of +0.004.
                https://cfd.ku.edu/hiocfd/case_c2.2.html

The incidence correction is identical in both; only the Mach differs, by 0.004.
The workshop condition is the primary solve here because it is the one the
external community grades against, and the tape condition is solved as well so
the sensitivity to the disagreement is measured rather than assumed. Getting
this wrong is how a confident wrong answer is produced on this case, so both
numbers travel with every result.

A third convention, M = 0.734 with alpha = 2.54 deg, also appears in the
literature. It is NOT used here: 2.54 deg is the tape's corrected incidence for
case 6, not case 9, and pairing it with case 9's Mach number is a conflation.

MODELLING CHOICES THAT ARE CHOICES, NOT MEASUREMENTS
-----------------------------------------------------
* Fully turbulent. The experiment tripped transition at 3% chord (tape file 3,
  ``trip_x_over_c`` = 0.03) and the workshop specifies transition fixed at 3%
  chord on both surfaces. This solve does not model transition; at Re = 6.5e6
  with a trip that far forward the laminar run is a small fraction of the
  chord. Documented, not hidden.
* Free-stream turbulence is not published for this experiment. The values used
  are the NASA Turbulence Modeling Resource's standard far-field state for
  k-omega SST -- eddy-viscosity ratio 0.009, k = 9e-9 a_inf^2,
  omega = 1e-6 rho_inf a_inf^2 / mu_inf -- which is a cited convention rather
  than a guess. See ``freestream_state``.
* Free air. The tunnel walls are not modelled; that is what the corrected
  conditions above exist to stand in for.
"""

from __future__ import annotations

import argparse
import math
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

# GEOMETRY AND PROCESS HELPERS ONLY.  Nothing grid-convergence is imported
# from this module and nothing here quotes one of its values: F12's observed
# order, GCI and Richardson extrapolate come from scripts/roache_triple.py
# (blob 8dee0d31e94d3f59d28658f88a4cd6df80ae8e39, commit 9c69a79a), which the
# lab is standardising on under N-T8.
from workflows.tmr_verification import (
    ratio_for_first_cell, geometric_first_cell, _foam, _foam_header,
    final_coefficient, parse_force_split,
)
from chief_engineer.head_engineer import parse_coefficient_history

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

# --------------------------------------------------------------------------
# Reference data
# --------------------------------------------------------------------------

# WHERE THE REFERENCE DATA IS, AND WHY THIS IS A FUNCTION AND NOT A CONSTANT.
# This was ``lab_paths.WEB / "campaign" / "F12_runs" / "reference"``, which
# binds to ``web/campaign/F12_runs/reference``.  THAT DIRECTORY DOES NOT
# EXIST: the reference moved with the MOVE_MAP to
# ``verification/runs/F12_runs/reference``, so every read below raised
# FileNotFoundError and ``rae_section()`` -- hence ``build_case`` -- could not
# run at all.  Found 2026-08-25 with zero compute, by calling
# ``blockmesh_dict``.  This is the D419 class and it is expressly outside the
# comparator-freeze clause (VERIFICATION_CHARTER 2d, boundary clause 1: a path
# either resolves or refuses; repairing one cannot move a number).
#
# ``lab_paths.resolve`` returns whichever of {literal, MOVE_MAP successor,
# MOVE_MAP predecessor} exists, and None when none does.  The None case
# REFUSES rather than binding a directory that is not there (CLAUDE.md rule 4:
# refuse, never degrade to a default).
REFERENCE_CITATION = "demo-output/website/campaign/F12_runs/reference"


def reference_dir() -> Path:
    """The directory holding the decoded Case 9 reference data.

    Raises rather than returning a path that does not exist, so a missing
    reference is a refusal at the first read instead of an empty tap list or
    a silently defaulted aerofoil.
    """
    resolved = lab_paths.resolve(REFERENCE_CITATION)
    if resolved is None:
        raise FileNotFoundError(
            "rae2822: the Case 9 reference directory does not resolve. The "
            f"citation {REFERENCE_CITATION!r} was tried at its literal "
            "location, at its MOVE_MAP successor and at its predecessor, and "
            "none of the three exists on disk. Refusing rather than "
            "defaulting to a path that is not there.")
    return resolved

# Straight from the tape, and re-derivable at any time by running
# reference/decode_tape.py. Quoted here so the workflow can state them without
# reparsing 237 kB of tape image on every call.
EXPERIMENT = {
    "case": 9,
    "mach_uncorrected": 0.730,
    "alpha_geometric_deg": 3.19,
    "alpha_corrected_deg": 2.79,
    "reynolds": 6.5e6,
    "trip_x_over_c": 0.03,
    "CN": 0.8030,
    "CM": -0.0990,
    "CD": 0.0168,
    "cp_tap_uncertainty": 0.0026,
    "source": ("Cook, McDonald & Firmin, AGARD AR-138 (1979); digitised as "
               "AFOSR-HTTM/Stanford flow 8621, hosted by the NASA Turbulence "
               "Modeling Resource"),
}

CONDITIONS = {
    # name -> (Mach, alpha_deg, what it is)
    "workshop": (0.734, 2.79, "International Workshop on High-Order CFD "
                              "Methods case C2.2 corrected conditions"),
    "tape": (0.730, 2.79, "AFOSR-HTTM tape: measured Mach, corrected incidence"),
}

GAMMA = 1.4
R_AIR = 287.05
P_INF = 101_325.0
T_INF = 300.0
CHORD = 1.0


def load_experiment_cp() -> dict[str, list[tuple[float, float]]]:
    """The digitised Case 9 taps, (x/c, Cp) per surface, sorted by x/c."""
    out = {}
    for surface in ("upper", "lower"):
        path = reference_dir() / f"rae2822_case9_cp_{surface}.dat"
        pts = []
        for line in path.read_text().splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            x, cp = line.split()
            pts.append((float(x), float(cp)))
        out[surface] = sorted(pts)
    return out


def load_coordinates() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """(upper, lower) design ordinates, (x/c, y/c), leading edge first."""
    upper, lower = [], []
    path = reference_dir() / "rae2822_coordinates.dat"
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        x, yu, yl = (float(v) for v in line.split())
        upper.append((x, yu))
        lower.append((x, yl))
    return upper, lower


# --------------------------------------------------------------------------
# Surface geometry
# --------------------------------------------------------------------------

class _SurfaceSpline:
    """y(x) for one aerofoil surface, splined against sqrt(x).

    A rounded leading edge has y ~ sqrt(x), whose derivative is unbounded at
    x = 0, so a spline built directly on x oscillates over the first few
    stations. Splining against t = sqrt(x) makes the leading edge locally
    LINEAR in the spline variable and removes that failure mode.

    The interpolant is a not-a-knot cubic, which is C2. A shape-preserving
    PCHIP was tried first, on the usual reasoning that it cannot invent a
    wiggle between two tabulated points. Measured on this table, that reasoning
    inverts: PCHIP is only C1, so surface curvature jumps at all 65 knots, and
    over 0.2 < x/c < 0.6 -- which is exactly where this case's shock stands --
    it returns a curvature range of -1.415 to +0.271 with steps up to 1.379,
    i.e. it flattens segments between knots and reverses the sign of the
    curvature on a section that is convex there. The cubic returns -0.672 to
    -0.322 over the same interval with steps of 0.004. Curvature kinks on an
    aerofoil surface print as pressure kinks, so the smoother interpolant is
    the honest one here and the shape-preserving argument does not survive
    contact with the data.
    """

    def __init__(self, points: list[tuple[float, float]]):
        from scipy.interpolate import CubicSpline

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        self._x_max = xs[-1]
        self._spline = CubicSpline([math.sqrt(x) for x in xs], ys)

    def __call__(self, x: float) -> float:
        return float(self._spline(math.sqrt(max(0.0, min(x, self._x_max)))))


@dataclass(frozen=True)
class Section:
    upper: _SurfaceSpline
    lower: _SurfaceSpline

    def y(self, x: float, sign: float) -> float:
        return self.upper(x) if sign > 0 else self.lower(x)


def rae_section() -> Section:
    upper, lower = load_coordinates()
    return Section(_SurfaceSpline(upper), _SurfaceSpline(lower))


def surface_points(section: Section, x_lo: float, x_hi: float, sign: float,
                   n: int = 240) -> list[tuple[float, float]]:
    """Interior points of one surface segment, cosine-clustered toward both
    segment ends so the polyLine is densest where curvature lives."""
    pts = []
    for i in range(1, n):
        t = 0.5 * (1.0 - math.cos(math.pi * i / n))
        x = x_lo + (x_hi - x_lo) * t
        pts.append((x, section.y(x, sign)))
    return pts


# --------------------------------------------------------------------------
# Mesh ladder
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class GridLevel:
    name: str
    n_surf_quarter: int   # cells per quarter of the surface (4 quarters)
    n_wake: int           # streamwise cells in each wake block
    ny: int               # wall-normal cells

    @property
    def cells(self) -> int:
        return (4 * self.n_surf_quarter + 2 * self.n_wake) * self.ny


# A clean factor-2 ladder in every direction, so an observed order of
# convergence is meaningful on it.
LEVELS = (
    GridLevel("coarse", 48, 48, 80),     # 23,040 cells
    GridLevel("medium", 96, 96, 160),    # 92,160 cells
    GridLevel("fine", 192, 192, 320),    # 368,640 cells
)

FARFIELD_R = 50.0     # chords, circular outer boundary centred on the TE
WAKE_LEN = 50.0       # chords of rectangular extension downstream
E_LE = 50.0           # mid-chord to leading-edge surface spacing ratio
E_TE = 4.0            # mid-chord to trailing-edge surface spacing ratio

# ---------------------------------------------------------------------------
# MESH-SIMILARITY ANCHORS
# ---------------------------------------------------------------------------
# A grid triple is admissible as a Roache ladder only if the three meshes are a
# geometrically SIMILAR family: every spacing scales with the refinement and
# the recipe is otherwise held fixed.  An order fitted across a ladder that
# changes recipe between rungs is a slope through a change of experiment, not a
# discretization order (VERIFICATION_CHARTER.md section 3.2, second failure
# mode), and scripts/roache_triple.py cannot see it -- its own docstring says
# the caller establishes similarity and the file cannot.  The lab has the
# defect on record in the Ahmed ladder (L-303 / N-C1 / D514).
#
# THIS LADDER CARRIED IT TWICE, in the wall-normal direction, and both are
# repaired here.  Written up in verification/campaign/F12_PREREGISTRATION.md,
# MESH-SIMILARITY AMENDMENT of 2026-08-25, sections 3-5 and 7.
#
#   1. The wall-normal first cell was the module constant FIRST_CELL = 2.0e-6,
#      exposed as a KEYWORD DEFAULT ONLY and never passed by build_case, so it
#      was FIXED at 2e-6 chord on all three levels while ny went 80/160/320
#      over the same 50-chord radius.  The similarity invariant -- the total
#      expansion ratio last/first -- fell 4.4011e6 -> 2.1935e6 -> 1.0643e6, a
#      factor 4.135, and near-wall growth fell from 21.4%/cell to 4.4%/cell.
#   2. The wake blocks' far-side (outlet) first cell was a level-independent
#      0.3 chord.  At ny = 320 that EXCEEDS the uniform spacing 50/320, so
#      ratio_for_first_cell's guard returned 1.0 and the fine level's wake
#      blocks were UNIFORM where the coarse level's were graded 3.747:1.  A
#      branch flip, not a drift.
#
# THE REPAIR IS ONE ANCHOR PER SPACING.  Each anchored spacing is registered
# ONCE, as the ANCHOR LEVEL's value, and every other level's is DERIVED from it
# by that level's own refinement factor.  The halving is therefore visible in
# one place and cannot drift between three; and a level that is not a uniform
# refinement of the anchor is REFUSED rather than given a spacing.
ANCHOR_LEVEL = LEVELS[0]        # coarse

# The frozen "wall-normal first cell 2e-6 chord, targeting y+ below 1", read
# per the 2026-08-25 amendment section 7 as the COARSE level's value.  The
# ladder it derives is 2.0e-6 / 1.0e-6 / 5.0e-7 chord.  ESTIMATED y+ on the
# full first-cell height at Re 6.5e6, from a flat-plate correlation and NOT
# measured: 0.47 / 0.23 / 0.12.  Anchoring instead at the FINE level would put
# the coarse rung at y+ 1.86, bridged rather than resolved, contradicting the
# second half of the same frozen sentence.
FIRST_CELL_ANCHOR = 2.0e-6      # anchor-level wall-normal first cell, chords

# The wake blocks' FAR-SIDE wall-normal first cell, at the outlet
# x = farfield_r + wake_len.  Its counterpart at the wake blocks' NEAR side is
# the O-grid's own r_y, so the boundary layer leaving the trailing edge is
# carried at wall resolution while the outlet end is graded on a wake scale
# instead.  Anchoring it and halving with the ladder makes the guard's branch
# condition LEVEL-INVARIANT by construction -- requested / uniform = 0.48 at
# every level -- and holds the far-side total expansion to 3.7472 / 3.7527 /
# 3.7555.  The farfield taper below reproduces the previous expression
# min(0.3, 0.3 * farfield_r / 25.0) exactly at the anchor level.
FAR_FIRST_CELL_ANCHOR = 0.3     # anchor-level wake-outlet first cell, chords
FAR_FIRST_CELL_REF_R = 25.0     # farfield radius that anchor is quoted at


class MeshSimilarityError(RuntimeError):
    """A level that cannot be placed on the anchored similar family, or a
    requested spacing that would be silently discarded rather than built."""


def refinement_factor(level: GridLevel,
                      anchor: GridLevel | None = None) -> float:
    """Linear refinement factor of ``level`` against ``anchor``.

    REFUSES unless the surface, wake and wall-normal counts all refine by ONE
    common factor.  A ladder that refines one direction and not another is not
    a similar family, whatever its cell counts say, and this is the guard that
    the Ahmed ladder (L-303) did not have.
    """
    anchor = ANCHOR_LEVEL if anchor is None else anchor
    pairs = (("n_surf_quarter", level.n_surf_quarter, anchor.n_surf_quarter),
             ("n_wake", level.n_wake, anchor.n_wake),
             ("ny", level.ny, anchor.ny))
    for name, num, den in pairs:
        if num <= 0 or den <= 0:
            raise MeshSimilarityError(
                f"rae2822: {name} must be positive on both level "
                f"{level.name!r} ({num}) and anchor {anchor.name!r} ({den})")
    factors = [num / den for _, num, den in pairs]
    if max(factors) - min(factors) > 1e-12 * max(factors):
        raise MeshSimilarityError(
            f"rae2822: level {level.name!r} is not a UNIFORM refinement of "
            f"anchor {anchor.name!r}; per-direction factors are "
            + ", ".join(f"{name}={f:.10g}"
                        for (name, _, _), f in zip(pairs, factors))
            + ". Refusing to derive an anchored spacing for a ladder that is "
              "not a geometrically similar family.")
    return factors[0]


def first_cell_for_level(level: GridLevel,
                         anchor: GridLevel | None = None) -> float:
    """Wall-normal first cell at the aerofoil surface, derived from the one
    registered anchor.  2.0e-6 / 1.0e-6 / 5.0e-7 chord on this ladder."""
    return FIRST_CELL_ANCHOR / refinement_factor(level, anchor)


def far_first_cell_for_level(level: GridLevel, *,
                             farfield_r: float = FARFIELD_R,
                             anchor: GridLevel | None = None) -> float:
    """Wall-normal first cell at the wake outlet, derived from the one
    registered anchor.  0.3 / 0.15 / 0.075 chord on this ladder.

    REFUSES if the request at the ANCHOR level is not strictly finer than that
    level's uniform spacing, because ``ratio_for_first_cell`` would then return
    1.0 and the requested grading would be discarded rather than built
    (CLAUDE.md rule 4: refuse, do not degrade).  That is precisely the branch
    the fine level used to fall into.
    """
    anchor = ANCHOR_LEVEL if anchor is None else anchor
    at_anchor = min(FAR_FIRST_CELL_ANCHOR,
                    FAR_FIRST_CELL_ANCHOR * farfield_r / FAR_FIRST_CELL_REF_R)
    uniform_at_anchor = farfield_r / anchor.ny
    if not at_anchor < uniform_at_anchor:
        raise MeshSimilarityError(
            "rae2822: the wake-outlet first cell requested at anchor level "
            f"{anchor.name!r} is {at_anchor:.6g} chord, which is not finer "
            f"than that level's uniform spacing {uniform_at_anchor:.6g} "
            f"(farfield_r={farfield_r:.6g}, ny={anchor.ny}). "
            "ratio_for_first_cell would return 1.0 and the grading would be "
            "discarded. Refusing rather than building an ungraded wake outlet.")
    return at_anchor / refinement_factor(level, anchor)


def _wake_ratio(level: GridLevel, wake_len: float) -> float:
    """Total wake expansion so the first wake cell matches the surface
    trailing-edge streamwise spacing."""
    seg = 0.502
    r = (1.0 / E_TE) ** (1.0 / (level.n_surf_quarter - 1))
    first = seg * (r - 1.0) / (r ** level.n_surf_quarter - 1.0)
    te_spacing = first * r ** (level.n_surf_quarter - 1)
    return ratio_for_first_cell(wake_len, level.n_wake, te_spacing)


def blockmesh_dict(section: Section, level: GridLevel, *,
                   farfield_r: float = FARFIELD_R, wake_len: float = WAKE_LEN,
                   first_cell: float | None = None,
                   far_first_cell: float | None = None) -> str:
    """O-grid around the section plus a rectangular wake extension.

    Topology is the one already exercised by ``workflows.transonic_airfoil``
    (four quarter blocks around the surface, split at the leading edge, both
    mid-chord points and the trailing edge, plus upper and lower wake blocks),
    generalised from that module's analytic symmetric thickness law to an
    arbitrary cambered section read from a coordinate table. The two mid-chord
    block corners therefore sit at (0.5, y_upper(0.5)) and (0.5, y_lower(0.5))
    rather than at +/- the same thickness.

    ``first_cell`` and ``far_first_cell`` are the wall-normal spacings at the
    aerofoil surface and at the wake outlet.  ``None`` means DERIVE THEM FROM
    ``level`` against the registered anchors -- it does not mean "use a fixed
    default".  Both WERE fixed constants, 2e-6 chord and 0.3 chord, on every
    level until 2026-08-25; that made the ladder non-similar in two independent
    ways (see the MESH-SIMILARITY ANCHORS block above).  Pass an explicit value
    only for a deliberate single-level sensitivity study, never to build a
    triple.
    """
    R, W = farfield_r, farfield_r + wake_len
    if first_cell is None:
        first_cell = first_cell_for_level(level)
    if far_first_cell is None:
        far_first_cell = far_first_cell_for_level(level, farfield_r=farfield_r)
    # REFUSE, never degrade.  ratio_for_first_cell returns 1.0 -- an ungraded,
    # uniform column -- for any request that is not strictly finer than the
    # uniform spacing, and it does so silently.  That silent branch is how the
    # fine level's wake blocks came to differ in KIND from the coarse level's.
    for what, value in (("aerofoil-surface", first_cell),
                        ("wake-outlet", far_first_cell)):
        if not value > 0.0:
            raise MeshSimilarityError(
                f"rae2822: {what} first cell on level {level.name!r} must be "
                f"positive, got {value!r}")
        if value >= R / level.ny:
            raise MeshSimilarityError(
                f"rae2822: {what} first cell {value:.6g} chord on level "
                f"{level.name!r} is not finer than that level's uniform "
                f"wall-normal spacing {R / level.ny:.6g} "
                f"(farfield_r={R:.6g}, ny={level.ny}). ratio_for_first_cell "
                "would return 1.0 and build an UNGRADED column, changing the "
                "kind of mesh this level is. Refusing.")
    r_y = ratio_for_first_cell(R, level.ny, first_cell)
    r_y_far = ratio_for_first_cell(R, level.ny, far_first_cell)
    r_wake = _wake_ratio(level, wake_len)
    y_up_mid = section.y(0.5, +1.0)
    y_lo_mid = section.y(0.5, -1.0)
    c45 = R / math.sqrt(2.0)

    def arc_point(deg: float) -> str:
        rad = math.radians(deg)
        return f"({1.0 + R * math.cos(rad):.10g} {R * math.sin(rad):.10g}"

    def poly(points: list[tuple[float, float]], z: float) -> str:
        inner = "\n".join(f"        ({x:.10g} {y:.10g} {z})" for x, y in points)
        return f"(\n{inner}\n    )"

    up_front = surface_points(section, 0.0, 0.5, +1.0)
    up_rear = surface_points(section, 0.5, 1.0, +1.0)
    lo_front = surface_points(section, 0.0, 0.5, -1.0)
    lo_rear = surface_points(section, 0.5, 1.0, -1.0)
    ns, nw, ny = level.n_surf_quarter, level.n_wake, level.ny

    lines = [_foam_header("dictionary", "blockMeshDict", "system"), """
scale   1;

vertices
("""]
    base = [
        (1.0, 0.0), (0.0, 0.0), (0.5, y_up_mid), (0.5, y_lo_mid),
        (1.0 - R, 0.0), (1.0 - c45, c45), (1.0, R), (1.0 - c45, -c45), (1.0, -R),
        (W, 0.0), (W, R), (W, -R),
    ]
    for z in (0, 1):
        for i, (x, y) in enumerate(base):
            lines.append(f"    ({x:.10g} {y:.10g} {z})   // {i + 12 * z}")
    lines.append(f""");

blocks
(
    hex (1 2 5 4 13 14 17 16) ({ns} {ny} 1)
        simpleGrading ({E_LE:.8g} {r_y:.8g} 1)
    hex (2 0 6 5 14 12 18 17) ({ns} {ny} 1)
        simpleGrading ({1.0 / E_TE:.8g} {r_y:.8g} 1)
    hex (0 3 7 8 12 15 19 20) ({ns} {ny} 1)
        simpleGrading ({E_TE:.8g} {r_y:.8g} 1)
    hex (3 1 4 7 15 13 16 19) ({ns} {ny} 1)
        simpleGrading ({1.0 / E_LE:.8g} {r_y:.8g} 1)
    hex (0 9 10 6 12 21 22 18) ({nw} {ny} 1)
        edgeGrading ({r_wake:.8g} {r_wake:.8g} {r_wake:.8g} {r_wake:.8g}
                     {r_y:.8g} {r_y_far:.8g} {r_y_far:.8g} {r_y:.8g}
                     1 1 1 1)
    hex (9 0 8 11 21 12 20 23) ({nw} {ny} 1)
        edgeGrading ({1.0 / r_wake:.8g} {1.0 / r_wake:.8g} {1.0 / r_wake:.8g} {1.0 / r_wake:.8g}
                     {r_y_far:.8g} {r_y:.8g} {r_y:.8g} {r_y_far:.8g}
                     1 1 1 1)
);

edges
(""")
    for z, off in ((0.0, 0), (1.0, 12)):
        lines.append(f"    polyLine {1 + off} {2 + off} {poly(up_front, z)}")
        lines.append(f"    polyLine {2 + off} {0 + off} {poly(up_rear, z)}")
        lines.append(f"    polyLine {0 + off} {3 + off} {poly(lo_rear[::-1], z)}")
        lines.append(f"    polyLine {3 + off} {1 + off} {poly(lo_front[::-1], z)}")
        for a, b, deg in ((4, 5, 157.5), (5, 6, 112.5), (8, 7, 247.5), (7, 4, 202.5)):
            lines.append(f"    arc {a + off} {b + off} {arc_point(deg)} {z:g})")
    lines.append("""
);

boundary
(
    aerofoil
    {
        type wall;
        faces ((1 2 14 13) (2 0 12 14) (0 3 15 12) (3 1 13 15));
    }
    inflow
    {
        type patch;
        faces
        (
            (4 5 17 16) (5 6 18 17) (8 7 19 20) (7 4 16 19)
            (11 8 20 23)
        );
    }
    outflow
    {
        type patch;
        faces ((6 10 22 18) (9 10 22 21) (9 11 23 21));
    }
    frontAndBack
    {
        type empty;
        faces
        (
            (1 2 5 4) (2 0 6 5) (0 3 7 8) (3 1 4 7)
            (0 9 10 6) (9 0 8 11)
            (13 14 17 16) (14 12 18 17) (12 15 19 20) (15 13 16 19)
            (12 21 22 18) (21 12 20 23)
        );
    }
);
""")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Free-stream state
# --------------------------------------------------------------------------

def freestream_state(mach: float, reynolds: float, *, p_inf: float = P_INF,
                     t_inf: float = T_INF) -> dict[str, float]:
    """Dimensional free-stream state realising (Mach, Re) at chord = 1.

    Turbulence far field follows the NASA Turbulence Modeling Resource's
    standard k-omega SST condition rather than an assumed tunnel turbulence
    level: mu_t/mu = 0.009, k = 9e-9 a_inf^2, omega = 1e-6 rho_inf a_inf^2 /
    mu_inf. Those three are mutually consistent by construction, since
    nu_t = k/omega = 0.009 mu/rho.
    """
    a_inf = math.sqrt(GAMMA * R_AIR * t_inf)
    u_inf = mach * a_inf
    rho_inf = p_inf / (R_AIR * t_inf)
    mu = rho_inf * u_inf * CHORD / reynolds
    nu = mu / rho_inf
    k_inf = 9.0e-9 * a_inf ** 2
    omega_inf = 1.0e-6 * rho_inf * a_inf ** 2 / mu
    return {
        "a_inf": a_inf, "u_inf": u_inf, "rho_inf": rho_inf, "mu": mu, "nu": nu,
        "k_inf": k_inf, "omega_inf": omega_inf, "nut_inf": k_inf / omega_inf,
        "q_inf": 0.5 * rho_inf * u_inf ** 2,
    }


# --------------------------------------------------------------------------
# constant/* and system/*
# --------------------------------------------------------------------------

def thermophysical_properties(mu: float) -> str:
    return _foam_header("dictionary", "thermophysicalProperties") + f"""
thermoType
{{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleInternalEnergy;
}}

mixture
{{
    specie
    {{
        molWeight   28.96;
    }}
    thermodynamics
    {{
        Cp          1004.5;
        Hf          0;
    }}
    transport
    {{
        mu          {mu:.8g};
        Pr          0.71;
    }}
}}
"""


_TURBULENCE_PROPERTIES = _foam_header("dictionary", "turbulenceProperties") + """
simulationType          RAS;

RAS
{
    RASModel            kOmegaSST;
    turbulence          on;
    printCoeffs         on;
}
"""


def fv_schemes() -> str:
    return _foam_header("dictionary", "fvSchemes") + """
ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
    limited         cellLimited Gauss linear 1;
    grad(U)         $limited;
    grad(k)         $limited;
    grad(omega)     $limited;
}

divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind limited;
    energy          bounded Gauss linearUpwind limited;
    div(phi,e)      $energy;
    div(phi,K)      $energy;
    div(phi,Ekp)    $energy;
    turbulence      bounded Gauss upwind;
    div(phi,k)      $turbulence;
    div(phi,omega)  $turbulence;
    div(phid,p)     Gauss upwind;
    div((phi|interpolate(rho)),p)  bounded Gauss upwind;
    div(((rho*nuEff)*dev2(T(grad(U)))))    Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

wallDist
{
    method          meshWave;
}
"""


def fv_solution(residual: float = 1.0e-6) -> str:
    return _foam_header("dictionary", "fvSolution") + f"""
solvers
{{
    p
    {{
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-8;
        relTol          0.01;
    }}
    "(U|k|omega|e)"
    {{
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-9;
        relTol          0.1;
    }}
}}

SIMPLE
{{
    residualControl
    {{
        p               {residual:g};
        U               {residual:g};
        "(k|omega|e)"   {residual:g};
    }}
    nNonOrthogonalCorrectors 1;
    pMinFactor      0.1;
    pMaxFactor      2;
}}

relaxationFactors
{{
    fields
    {{
        p               0.3;
        rho             0.05;
    }}
    equations
    {{
        U               0.3;
        e               0.5;
        "(k|omega)"     0.5;
    }}
}}
"""


def control_dict(iterations: int, *, rho_inf: float, u_inf: float,
                 alpha_deg: float, write_interval: int | None = None) -> str:
    """Aref is chord x span. The mesh is one cell thick between z = 0 and
    z = 1, so span = 1 chord and Aref = 1. (transonic_airfoil records the
    measured consequence of getting this wrong: Aref = 0.1 there put every
    coefficient out by exactly 10x.)"""
    rad = math.radians(alpha_deg)
    drag_dir = f"({math.cos(rad):.10f} {math.sin(rad):.10f} 0)"
    lift_dir = f"({-math.sin(rad):.10f} {math.cos(rad):.10f} 0)"
    return _foam_header("dictionary", "controlDict") + f"""
application     rhoSimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {iterations};
deltaT          1;
writeControl    timeStep;
writeInterval   {write_interval or iterations};
purgeWrite      1;
writeFormat     ascii;
writePrecision  10;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;

functions
{{
    forceCoeffs1
    {{
        type            forceCoeffs;
        libs            (forces);
        writeControl    timeStep;
        writeInterval   1;
        patches         (aerofoil);
        rho             rho;
        rhoInf          {rho_inf:.10g};
        magUInf         {u_inf:.10g};
        lRef            {CHORD};
        Aref            {CHORD * 1.0};
        CofR            (0.25 0 0);
        dragDir         {drag_dir};
        liftDir         {lift_dir};
        pitchAxis       (0 0 1);
    }}
    surfaceP
    {{
        type            surfaces;
        libs            (sampling);
        executeControl  onEnd;
        writeControl    onEnd;
        surfaceFormat   raw;
        fields          (p);
        interpolate     false;
        surfaces
        (
            aerofoil {{ type patch; patches (aerofoil); }}
        );
    }}
    yPlus
    {{
        type            yPlus;
        libs            (fieldFunctionObjects);
        executeControl  onEnd;
        writeControl    onEnd;
    }}
    machNo
    {{
        type            MachNo;
        libs            (fieldFunctionObjects);
        executeControl  onEnd;
        writeControl    onEnd;
    }}
}}
"""


def _field(cls: str, obj: str, dimensions: str, internal: str,
           boundaries: dict[str, str]) -> str:
    body = "".join(f"    {name}\n    {{\n{entry}    }}\n"
                   for name, entry in boundaries.items())
    return (_foam_header(cls, obj, "0") + f"dimensions      {dimensions};\n\n"
            + f"internalField   {internal};\n\n"
            + "boundaryField\n{\n" + body + "}\n")


def initial_fields(alpha_deg: float, state: dict[str, float]) -> dict[str, str]:
    rad = math.radians(alpha_deg)
    u_inf = state["u_inf"]
    u_vec = f"({u_inf * math.cos(rad):.8f} {u_inf * math.sin(rad):.8f} 0)"
    empty = "        type            empty;\n"

    def bc(*lines: str) -> str:
        return "".join(f"        {line}\n" for line in lines)

    def far(kind: str, value: str) -> dict[str, str]:
        return {p: bc(f"type            {kind};", f"inletValue      uniform {value};",
                      f"value           uniform {value};")
                for p in ("inflow", "outflow")}

    k_inf, omega_inf, nut_inf = state["k_inf"], state["omega_inf"], state["nut_inf"]

    fields = {}
    fields["U"] = _field("volVectorField", "U", "[0 1 -1 0 0 0 0]",
                         f"uniform {u_vec}", {
        "inflow": bc("type            freestreamVelocity;",
                     f"freestreamValue uniform {u_vec};",
                     f"value           uniform {u_vec};"),
        "outflow": bc("type            freestreamVelocity;",
                      f"freestreamValue uniform {u_vec};",
                      f"value           uniform {u_vec};"),
        "aerofoil": bc("type            noSlip;"),
        "frontAndBack": empty})
    fields["p"] = _field("volScalarField", "p", "[1 -1 -2 0 0 0 0]",
                         f"uniform {P_INF:.10g}", {
        "inflow": bc("type            freestreamPressure;",
                     f"freestreamValue uniform {P_INF:.10g};"),
        "outflow": bc("type            freestreamPressure;",
                      f"freestreamValue uniform {P_INF:.10g};"),
        "aerofoil": bc("type            zeroGradient;"),
        "frontAndBack": empty})
    fields["T"] = _field("volScalarField", "T", "[0 0 0 1 0 0 0]",
                         f"uniform {T_INF:.10g}",
                         {**far("inletOutlet", f"{T_INF:.10g}"),
                          "aerofoil": bc("type            zeroGradient;"),
                          "frontAndBack": empty})
    # Wall-resolved treatment: the first cell sits at y+ ~ 0.5, so k is driven
    # to zero at the wall and nut is not modelled by a log-law bridge.
    fields["k"] = _field("volScalarField", "k", "[0 2 -2 0 0 0 0]",
                         f"uniform {k_inf:.8g}",
                         {**far("inletOutlet", f"{k_inf:.8g}"),
                          "aerofoil": bc("type            kLowReWallFunction;",
                                         f"value           uniform {k_inf:.8g};"),
                          "frontAndBack": empty})
    fields["omega"] = _field("volScalarField", "omega", "[0 0 -1 0 0 0 0]",
                             f"uniform {omega_inf:.8g}",
                             {**far("inletOutlet", f"{omega_inf:.8g}"),
                              "aerofoil": bc("type            omegaWallFunction;",
                                             f"value           uniform {omega_inf:.8g};"),
                              "frontAndBack": empty})
    fields["nut"] = _field("volScalarField", "nut", "[0 2 -1 0 0 0 0]",
                           f"uniform {nut_inf:.8g}", {
        "inflow": bc("type            calculated;", "value           uniform 0;"),
        "outflow": bc("type            calculated;", "value           uniform 0;"),
        "aerofoil": bc("type            nutLowReWallFunction;",
                       "value           uniform 0;"),
        "frontAndBack": empty})
    fields["alphat"] = _field("volScalarField", "alphat", "[1 -1 -1 0 0 0 0]",
                              "uniform 0", {
        "inflow": bc("type            calculated;", "value           uniform 0;"),
        "outflow": bc("type            calculated;", "value           uniform 0;"),
        "aerofoil": bc("type            compressible::alphatWallFunction;",
                       "value           uniform 0;"),
        "frontAndBack": empty})
    return fields


# --------------------------------------------------------------------------
# Mesh quality gate (docs/standards/MESH_STANDARD.md)
# --------------------------------------------------------------------------

MAX_NON_ORTHOGONALITY = 70.0   # checkMesh's own nonOrthThreshold_
MAX_SKEWNESS = 4.0             # checkMesh's own skewThreshold_, boundary faces included


def parse_check_mesh(text: str) -> dict[str, Any]:
    """The quality numbers the lab's mesh standard gates on, plus the counts
    checkMesh prints, straight out of a log."""
    out: dict[str, Any] = {"failed_checks": []}
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("Max cell openness") and "aspect ratio" in s:
            out["max_aspect_ratio"] = float(s.split("=")[-1].split()[0].rstrip("."))
        elif "Mesh non-orthogonality Max:" in s:
            parts = s.split()
            out["max_non_orthogonality"] = float(parts[parts.index("Max:") + 1])
        elif s.startswith("Max skewness ="):
            out["max_skewness"] = float(s.split("=")[1].split()[0].rstrip("."))
        elif s.startswith("cells:"):
            out.setdefault("cells", int(s.split()[-1]))
        elif "***" in s:
            out["failed_checks"].append(s.lstrip("* ").strip())
        elif s.startswith("Mesh OK"):
            out["mesh_ok"] = True
    return out


def mesh_gate(quality: dict[str, Any]) -> dict[str, Any]:
    breaches = []
    nonortho = quality.get("max_non_orthogonality")
    skew = quality.get("max_skewness")
    if nonortho is None or nonortho > MAX_NON_ORTHOGONALITY:
        breaches.append(f"max non-orthogonality {nonortho} > {MAX_NON_ORTHOGONALITY}")
    if skew is None or skew > MAX_SKEWNESS:
        breaches.append(f"max skewness {skew} > {MAX_SKEWNESS}")
    return {"passed": not breaches, "breaches": breaches,
            "max_non_orthogonality": nonortho, "max_skewness": skew,
            "max_aspect_ratio": quality.get("max_aspect_ratio"),
            # Aspect ratio is advisory per the mesh standard: reference-grade
            # wall-resolved grids run to 7e4 and a hard gate at 1000 would
            # reject all of them. It is recorded, with its alignment
            # justification (anisotropy is wall-normal, on orthogonal cells).
            "aspect_ratio_gated": False}


# --------------------------------------------------------------------------
# Surface pressure extraction and shock detection
# --------------------------------------------------------------------------

def split_surfaces(raw_text: str, section: Section, p_inf: float, q_inf: float
                   ) -> dict[str, list[tuple[float, float]]]:
    """(x/c, Cp) per surface from a raw patch sample of p.

    Assignment is by proximity to each surface spline, NOT by the sign of y.
    The RAE 2822 has aft camber: its lower surface crosses above the chord line
    near x/c = 0.93 and stays there to the trailing edge, so a sign-of-y split
    silently moves the last few percent of the lower surface onto the upper
    one, exactly where the trailing-edge pressures are being compared.
    """
    upper, lower = [], []
    for line in raw_text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 4:
            continue
        try:
            x, y, p = float(parts[0]), float(parts[1]), float(parts[3])
        except ValueError:
            continue
        cp = (p - p_inf) / q_inf
        du = abs(y - section.y(x, +1.0))
        dl = abs(y - section.y(x, -1.0))
        (upper if du <= dl else lower).append((x, cp))
    return {"upper": sorted(upper), "lower": sorted(lower)}


def sonic_cp(mach: float) -> float:
    """Critical pressure coefficient: the Cp at which the local flow is sonic."""
    t = (1.0 + 0.5 * (GAMMA - 1.0) * mach * mach) / (1.0 + 0.5 * (GAMMA - 1.0))
    return (t ** (GAMMA / (GAMMA - 1.0)) - 1.0) / (0.5 * GAMMA * mach * mach)


def shock_location(profile: list[tuple[float, float]], mach: float, *,
                   x_lo: float = 0.10, x_hi: float = 0.95) -> dict[str, Any] | None:
    """Where the upper-surface shock stands, by two definitions.

    ``steepest``  midpoint of the adjacent sample pair with the largest
                  positive dCp/dx. This is the detector F2 uses, and F2's
                  record documents its failure mode: it can only return values
                  on the sample lattice, so its resolution is the local sample
                  spacing and a deviation smaller than one spacing is not
                  resolved. That spacing is returned alongside as
                  ``steepest_resolution`` and must be quoted with the value.

    ``sonic``     x/c at which Cp crosses the critical value from below on the
                  recompression, found by linear interpolation between the two
                  bracketing samples. This is continuous in x rather than
                  quantised, is defined identically on the experimental taps
                  and on the CFD samples, and is the value graded on.
    """
    window = [(x, cp) for x, cp in profile if x_lo <= x <= x_hi]
    if len(window) < 3:
        return None
    best = None
    for (x0, c0), (x1, c1) in zip(window, window[1:]):
        if x1 <= x0:
            continue
        slope = (c1 - c0) / (x1 - x0)
        if best is None or slope > best[1]:
            best = (0.5 * (x0 + x1), slope, x1 - x0)
    if best is None:
        return None

    cp_star = sonic_cp(mach)
    sonic_x = None
    # walk forward from the strongest recompression and take the first upward
    # crossing of Cp* at or after it
    for (x0, c0), (x1, c1) in zip(window, window[1:]):
        if x1 < best[0]:
            continue
        if c0 < cp_star <= c1:
            sonic_x = x0 + (x1 - x0) * (cp_star - c0) / (c1 - c0)
            break
    return {"steepest_x_over_c": best[0], "steepest_dcp_dx": best[1],
            "steepest_resolution": best[2], "sonic_x_over_c": sonic_x,
            "cp_star": cp_star}


def cp_deviation(cfd: list[tuple[float, float]],
                 experiment: list[tuple[float, float]]) -> dict[str, Any]:
    """RMS and peak deviation of the CFD surface pressure from the measured
    taps, evaluated AT THE TAP LOCATIONS by interpolating the CFD onto them.

    The CFD is the interpolated side on purpose. Interpolating the 50-odd
    experimental taps onto hundreds of CFD faces would invent experimental
    values between taps and then grade against them; interpolating the dense
    CFD onto the sparse taps only ever reads the CFD where it is smooth.
    """
    import numpy as np

    xs = np.array([p[0] for p in cfd])
    cps = np.array([p[1] for p in cfd])
    order = np.argsort(xs)
    xs, cps = xs[order], cps[order]
    ex = np.array([p[0] for p in experiment])
    ey = np.array([p[1] for p in experiment])
    inside = (ex >= xs.min()) & (ex <= xs.max())
    ex, ey = ex[inside], ey[inside]
    interp = np.interp(ex, xs, cps)
    diff = interp - ey
    worst = int(np.argmax(np.abs(diff)))
    return {"n_taps": int(len(ex)),
            "rms": float(np.sqrt(np.mean(diff ** 2))),
            "mean_signed": float(np.mean(diff)),
            "max_abs": float(np.abs(diff).max()),
            "max_abs_at_x": float(ex[worst]),
            "per_tap": [(float(a), float(b), float(c))
                        for a, b, c in zip(ex, ey, interp)]}


# --------------------------------------------------------------------------
# Case assembly and run
# --------------------------------------------------------------------------

def build_case(case_dir: Path, *, mach: float, alpha_deg: float,
               reynolds: float = 6.5e6, level: GridLevel = LEVELS[0],
               iterations: int = 6000, farfield_r: float = FARFIELD_R,
               wake_len: float = WAKE_LEN,
               first_cell: float | None = None,
               far_first_cell: float | None = None) -> dict[str, Any]:
    case = Path(case_dir)
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)
    section = rae_section()
    state = freestream_state(mach, reynolds)

    # Derived HERE as well as inside the dictionary writer, so the values that
    # were ACTUALLY built travel out in the returned record and a grader can
    # audit this ladder's similarity from the run output rather than
    # re-deriving it from the source (VERIFICATION_CHARTER 3.2, rule 3: a
    # recipe audit precedes an order, read from each rung's own dictionary).
    if first_cell is None:
        first_cell = first_cell_for_level(level)
    if far_first_cell is None:
        far_first_cell = far_first_cell_for_level(level, farfield_r=farfield_r)

    (case / "system" / "blockMeshDict").write_text(
        blockmesh_dict(section, level, farfield_r=farfield_r, wake_len=wake_len,
                       first_cell=first_cell, far_first_cell=far_first_cell))
    (case / "system" / "fvSchemes").write_text(fv_schemes())
    (case / "system" / "fvSolution").write_text(fv_solution())
    (case / "system" / "controlDict").write_text(
        control_dict(iterations, rho_inf=state["rho_inf"],
                     u_inf=state["u_inf"], alpha_deg=alpha_deg))
    (case / "constant" / "thermophysicalProperties").write_text(
        thermophysical_properties(state["mu"]))
    (case / "constant" / "turbulenceProperties").write_text(_TURBULENCE_PROPERTIES)
    for name, text in initial_fields(alpha_deg, state).items():
        (case / "0" / name).write_text(text)
    return {"mach": mach, "alpha_deg": alpha_deg, "reynolds": reynolds,
            "level": level.name, "cells_nominal": level.cells,
            "iterations": iterations, "farfield_r": farfield_r,
            "first_cell": first_cell, "far_first_cell": far_first_cell,
            "wall_normal_total_ratio": ratio_for_first_cell(
                farfield_r, level.ny, first_cell),
            "far_total_ratio": ratio_for_first_cell(
                farfield_r, level.ny, far_first_cell),
            "refinement_factor": refinement_factor(level),
            **state}


def solver_converged(log_text: str) -> bool:
    """The solver's own convergence statement, not a residual that looks
    small (LESSONS L-14/L-15)."""
    return "SIMPLE solution converged" in log_text


def run_case(*, mach: float, alpha_deg: float, work_dir: Path,
             reynolds: float = 6.5e6, level: GridLevel = LEVELS[0],
             iterations: int = 6000, farfield_r: float = FARFIELD_R,
             first_cell: float | None = None,
             far_first_cell: float | None = None,
             ranks: int = 1, timeout: float = 7200.0,
             log: Callable[[str], None] = print) -> dict[str, Any]:
    case = Path(work_dir)
    if case.exists():
        shutil.rmtree(case, ignore_errors=True)
    case.mkdir(parents=True, exist_ok=True)
    params = build_case(case, mach=mach, alpha_deg=alpha_deg, reynolds=reynolds,
                        level=level, iterations=iterations, farfield_r=farfield_r,
                        first_cell=first_cell, far_first_cell=far_first_cell)
    section = rae_section()
    timings: dict[str, float] = {}

    def step(name: str, args: list[str], limit: float) -> Any:
        start = time.monotonic()
        result = _foam(args, case, f"log.{name}", timeout=limit)
        timings[name] = round(time.monotonic() - start, 1)
        return result

    if step("blockMesh", ["blockMesh"], 1800).returncode != 0:
        raise RuntimeError("rae2822: blockMesh failed:\n" + "\n".join(
            (case / "log.blockMesh").read_text(errors="replace").splitlines()[-25:]))
    step("checkMesh", ["checkMesh"], 1800)
    quality = parse_check_mesh((case / "log.checkMesh").read_text(errors="replace"))
    gate = mesh_gate(quality)

    if ranks > 1:
        (case / "system" / "decomposeParDict").write_text(
            _foam_header("dictionary", "decomposeParDict")
            + f"numberOfSubdomains {ranks};\nmethod scotch;\n")
        step("decomposePar", ["decomposePar"], 1800)
        solve = step("rhoSimpleFoam",
                     ["mpirun", "-np", str(ranks), "rhoSimpleFoam", "-parallel"],
                     timeout)
        step("reconstructPar", ["reconstructPar", "-latestTime"], 1800)
    else:
        solve = step("rhoSimpleFoam", ["rhoSimpleFoam"], timeout)

    log_text = (case / "log.rhoSimpleFoam").read_text(errors="replace")
    if solve.returncode != 0:
        raise RuntimeError("rae2822: rhoSimpleFoam failed:\n"
                           + "\n".join(log_text.splitlines()[-30:]))

    coeff = sorted((case / "postProcessing" / "forceCoeffs1").rglob("coefficient*.dat"))
    if not coeff:
        raise RuntimeError("rae2822: no forceCoeffs output")
    dat = coeff[-1].read_text(errors="replace")
    cd, cl, cm = (final_coefficient(dat, c) for c in ("Cd", "Cl", "CmPitch"))
    if cd is None or cl is None:
        raise RuntimeError("rae2822: Cd/Cl not found in forceCoeffs output")
    history = parse_coefficient_history(dat)

    # Normal force, the quantity the experiment publishes (CN is referred to
    # the CHORD, lift and drag to the free stream).
    rad = math.radians(alpha_deg)
    cn = cl["value"] * math.cos(rad) + cd["value"] * math.sin(rad)

    surfaces = {}
    shock = None
    raw = sorted((case / "postProcessing" / "surfaceP").rglob("*.raw"))
    if raw:
        state = freestream_state(mach, reynolds)
        surfaces = split_surfaces(raw[-1].read_text(errors="replace"), section,
                                  P_INF, state["q_inf"])
        shock = shock_location(surfaces["upper"], mach)

    record = {
        **{k: params[k] for k in ("mach", "alpha_deg", "reynolds", "level",
                                  "iterations", "farfield_r",
                                  "first_cell", "far_first_cell",
                                  "wall_normal_total_ratio", "far_total_ratio",
                                  "refinement_factor")},
        "cells": quality.get("cells", params["cells_nominal"]),
        "mesh_quality": quality, "mesh_gate": gate,
        "converged": solver_converged(log_text),
        "iterations_run": len(history.get("Cd", [])),
        "cd": cd["value"], "cd_spread": cd["spread"],
        "cl": cl["value"], "cl_spread": cl["spread"],
        "cm": cm["value"] if cm else None,
        "cn": cn,
        "cd_split": parse_force_split(log_text, "Cd"),
        "shock": shock,
        "surfaces": surfaces,
        "ranks": ranks,
        "timings": timings,
        "wall_seconds": sum(timings.values()),
        "core_seconds": sum(v for k, v in timings.items()
                            if k != "rhoSimpleFoam") + timings.get(
                                "rhoSimpleFoam", 0.0) * ranks,
    }
    log("[rae2822 %s M%.3f a%.2f] cells %d  converged %s  Cl %.5f  Cd %.6f  "
        "CN %.5f  shock %s" % (level.name, mach, alpha_deg, record["cells"],
                               record["converged"], record["cl"], record["cd"],
                               cn, shock["sonic_x_over_c"] if shock else None))
    return record


# --------------------------------------------------------------------------
# --selftest: VALUE checks and MUTATION controls on the mesh ladder
# --------------------------------------------------------------------------
#
# STANDING RULE N-T8 (registered at 792acd8f): a comparator's --selftest must
# carry a VALUE-checking control, not a key-presence check.  The reason is on
# the record: an inverted Richardson sign survived every run in five
# implementations because the selftests asked whether a key existed rather than
# what number it held.  A test that passes on both the right answer and the
# wrong one tests nothing.
#
# So every numeric check below comes in a pair: the VALUE the repaired ladder
# must produce, and a MUTATION that re-introduces the pre-2026-08-25 behaviour
# and MUST make that same check fail (or be refused outright).  A mutation that
# does not get caught is itself recorded as a failure.
#
# WHAT THIS SELFTEST DOES NOT DO.  It computes no observed order, no GCI and no
# Richardson extrapolate, and it takes none from workflows.tmr_verification --
# from which this module imports geometry and process helpers only.  F12's
# grading goes through scripts/roache_triple.py.  This selftest builds no mesh,
# writes no case directory and launches no solver: it emits blockMeshDict TEXT
# in memory and reads the numbers back out of it.

# ESTIMATED, from a flat-plate correlation at Re_c = 6.5e6, and NOT MEASURED.
# cf = 0.0592 Re^-0.2 = 0.002569, so y+ = (y/c) * Re * sqrt(cf/2) gives 2.330e5
# per chord of wall distance.  Quoted on the FULL first-cell height, which is
# the convention the generator's own "y+ ~ 0.5" note uses.  Reported below, and
# gated only against the frozen sentence's own "y+ below 1" clause.
YPLUS_PER_CHORD_ESTIMATE = 2.330e5

_CHECKS: list[tuple[str, bool]] = []


def _check(name: str, ok: bool, detail: str = "") -> bool:
    ok = bool(ok)
    _CHECKS.append((name, ok))
    print(f"  [{'ok' if ok else 'FAIL'}] {name}")
    if detail:
        print(f"         {detail}")
    return ok


def _refuses(name: str, fn, detail: str = "") -> bool:
    """A mutation control on a REFUSAL: ``fn`` must raise MeshSimilarityError."""
    try:
        fn()
    except MeshSimilarityError as exc:
        first = " ".join(str(exc).split())
        return _check(name, True, (detail + "  " if detail else "")
                      + "refused: " + (first[:150] + "..."
                                       if len(first) > 150 else first))
    except Exception as exc:                       # pragma: no cover - clarity
        return _check(name, False,
                      f"raised {type(exc).__name__} instead of "
                      f"MeshSimilarityError: {exc}")
    return _check(name, False,
                  "DID NOT REFUSE -- the guard this control exists to prove is "
                  "not there")


_HEX_RE = re.compile(
    r"hex \((?P<verts>[0-9 ]+)\)\s*\([0-9 ]+\)\s*"
    r"edgeGrading \((?P<grad>[^)]*)\)", re.S)


def wake_block_gradings(dict_text: str) -> list[tuple[str, list[float]]]:
    """The two wake blocks' WALL-NORMAL edge gradings, read back out of an
    emitted blockMeshDict.

    Establishes what the far-side grading is geometrically FOR, from the block
    topology rather than from the format string.  The upper wake block is
    ``hex (0 9 10 6 ...)``; in blockMesh's edge order the four y-direction
    entries are edges 0->3, 1->2, 5->6 and 4->7.  Vertex 0 is the trailing edge
    (1, 0) and vertex 3 is the top of the far-field circle (1, R), so edge 0->3
    is the column standing on the TRAILING EDGE and carries the O-grid's own
    wall grading.  Vertex 1 is (W, 0) and vertex 2 is (W, R), so edge 1->2 is
    the column at the OUTLET, W = farfield_r + wake_len downstream, and that is
    the edge the far-side grading exists for: there is no wall there, the wake
    has spread, and the column is graded on a wake scale instead of a
    boundary-layer one.  The lower block ``hex (9 0 8 11 ...)`` is the same two
    columns with the roles swapped, which is why its quadruple is reversed.

    Returns (vertex string, [4 wall-normal gradings]) per wake block.
    """
    out = []
    for m in _HEX_RE.finditer(dict_text):
        grad = [float(v) for v in m.group("grad").split()]
        if len(grad) != 12:
            raise MeshSimilarityError(
                "rae2822: an edgeGrading entry did not carry 12 numbers; "
                f"got {len(grad)} in block ({m.group('verts')})")
        out.append((m.group("verts").strip(), grad[4:8]))
    if len(out) != 2:
        raise MeshSimilarityError(
            "rae2822: expected exactly 2 edgeGrading (wake) blocks in the "
            f"emitted blockMeshDict, found {len(out)}. The reader cannot be "
            "trusted to see the gradings and this selftest refuses.")
    return out


def surface_block_wall_gradings(dict_text: str) -> list[float]:
    """The wall-normal entry of each of the four O-grid blocks' simpleGrading,
    read back out of an emitted blockMeshDict."""
    got = [float(m.group(1)) for m in re.finditer(
        r"simpleGrading \([^ ]+ ([^ ]+) 1\)", dict_text)]
    if len(got) != 4:
        raise MeshSimilarityError(
            "rae2822: expected exactly 4 simpleGrading (O-grid) blocks in the "
            f"emitted blockMeshDict, found {len(got)}. Refusing.")
    return got


def selftest() -> int:
    print("rae2822_case9.py --selftest -- mesh-similarity repair, ZERO COMPUTE")
    print("no mesh is built, no case directory is written, no solver is run\n")
    R = FARFIELD_R
    expected_first = {"coarse": 2.0e-6, "medium": 1.0e-6, "fine": 5.0e-7}
    expected_far = {"coarse": 0.3, "medium": 0.15, "fine": 0.075}

    # ---- (i) the anchored wall-normal ladder, by VALUE --------------------
    print("(i) the anchored wall-normal ladder -- VALUE checks")
    wall = {}
    for lv in LEVELS:
        fc = first_cell_for_level(lv)
        total = ratio_for_first_cell(R, lv.ny, fc)
        delivered = geometric_first_cell(R, lv.ny, total)
        wall[lv.name] = (fc, total, total ** (1.0 / (lv.ny - 1)))
        _check(f"{lv.name}: derived first cell is exactly "
               f"{expected_first[lv.name]:.1e} chord",
               abs(fc - expected_first[lv.name]) <= 1e-21,
               f"got {fc:.12e}")
        _check(f"{lv.name}: the grading DELIVERS that first cell to 1e-12 "
               "relative",
               abs(delivered - fc) <= 1e-12 * fc,
               f"blockMesh would place {delivered:.12e}, requested "
               f"{fc:.12e}, relative {abs(delivered - fc) / fc:.2e}")
    totals = [wall[lv.name][1] for lv in LEVELS]
    spread = max(totals) / min(totals) - 1.0
    _check("SIMILARITY INVARIANT: the wall-normal TOTAL expansion ratio "
           "(last/first) is held across the ladder to 7%",
           spread <= 0.07,
           "totals " + " / ".join(f"{t:.6e}" for t in totals)
           + f"; spread {100 * spread:.2f}%")
    for a, b in zip(LEVELS, LEVELS[1:]):
        want = wall[a.name][2] ** 0.5
        got = wall[b.name][2]
        _check(f"cell-to-cell ratio: {b.name} == sqrt({a.name}) to 1e-3 "
               "relative, as a factor-two refinement of a geometric column "
               "requires",
               abs(got - want) <= 1e-3 * want,
               f"sqrt({wall[a.name][2]:.6f}) = {want:.6f} vs built "
               f"{got:.6f}; relative {abs(got - want) / want:.2e}")
    yplus = {lv.name: wall[lv.name][0] * YPLUS_PER_CHORD_ESTIMATE
             for lv in LEVELS}
    _check("every level's first cell is below y+ 1, the frozen mesh-study "
           "sentence's own second clause (ESTIMATED from a flat-plate "
           "correlation, NOT measured)",
           max(yplus.values()) < 1.0,
           "y+ " + " / ".join(f"{lv.name} {yplus[lv.name]:.3f}"
                              for lv in LEVELS))

    # ---- (ii) the anchored wake-outlet grading, by VALUE ------------------
    print("\n(ii) the anchored wake-outlet grading -- VALUE checks")
    far, fracs = {}, []
    for lv in LEVELS:
        fc = far_first_cell_for_level(lv, farfield_r=R)
        uniform = R / lv.ny
        total = ratio_for_first_cell(R, lv.ny, fc)
        far[lv.name] = (fc, uniform, total)
        fracs.append(fc / uniform)
        _check(f"{lv.name}: derived wake-outlet first cell is exactly "
               f"{expected_far[lv.name]:g} chord",
               abs(fc - expected_far[lv.name]) <= 1e-15,
               f"got {fc:.12g}")
        _check(f"{lv.name}: the request is strictly finer than uniform, so "
               "ratio_for_first_cell's 1.0 branch is NOT taken",
               fc < uniform and total > 1.0,
               f"requested {fc:.6g}, uniform {uniform:.6g}, total ratio "
               f"{total:.6f}")
    _check("THE BRANCH CONDITION IS LEVEL-INVARIANT: requested / uniform is "
           "identical on all three levels, so the flip that produced defect 2 "
           "is structurally unreachable",
           max(fracs) - min(fracs) <= 1e-12 * max(fracs),
           "requested/uniform = " + " / ".join(f"{f:.12f}" for f in fracs))
    ftotals = [far[lv.name][2] for lv in LEVELS]
    fspread = max(ftotals) / min(ftotals) - 1.0
    _check("SIMILARITY INVARIANT: the wake-outlet TOTAL expansion ratio is "
           "held across the ladder to 0.5%",
           fspread <= 0.005,
           "totals " + " / ".join(f"{t:.6f}" for t in ftotals)
           + f"; spread {100 * fspread:.3f}%")

    # ---- (iii) the rest of the recipe is held fixed -----------------------
    print("\n(iii) the REST of the recipe is held fixed across the ladder")
    _check("the refinement factor is 1 / 2 / 4 and all three directions agree",
           [refinement_factor(lv) for lv in LEVELS] == [1.0, 2.0, 4.0],
           "factors " + " / ".join(f"{refinement_factor(lv):g}"
                                   for lv in LEVELS))
    wk = [_wake_ratio(lv, WAKE_LEN) for lv in LEVELS]
    _check("the streamwise wake TOTAL expansion is held across the ladder "
           "to 5%",
           max(wk) / min(wk) - 1.0 <= 0.05,
           "totals " + " / ".join(f"{v:.4f}" for v in wk)
           + f"; spread {100 * (max(wk) / min(wk) - 1.0):.2f}%")
    _check("the surface streamwise clustering ratios E_LE and E_TE are "
           "level-independent constants, as similarity requires",
           isinstance(E_LE, float) and isinstance(E_TE, float),
           f"E_LE = {E_LE:g}, E_TE = {E_TE:g} on every level")

    # ---- (iv) the numbers that actually reach the dictionary --------------
    print("\n(iv) READ BACK FROM THE EMITTED blockMeshDict, not from the "
          "helper that produced it")
    section = rae_section()      # refuses if the reference data does not resolve
    emitted = {}
    for lv in LEVELS:
        text = blockmesh_dict(section, lv)
        emitted[lv.name] = text
        want_y = float(f"{wall[lv.name][1]:.8g}")
        want_far = float(f"{far[lv.name][2]:.8g}")
        blocks = wake_block_gradings(text)
        upper, lower = blocks[0][1], blocks[1][1]
        _check(f"{lv.name}: the upper wake block carries "
               "(TE, outlet, outlet, TE) = (r_y, r_y_far, r_y_far, r_y)",
               upper == [want_y, want_far, want_far, want_y],
               f"block ({blocks[0][0]}) -> {upper}")
        _check(f"{lv.name}: the lower wake block carries the same two columns "
               "with the roles swapped",
               lower == [want_far, want_y, want_y, want_far],
               f"block ({blocks[1][0]}) -> {lower}")
        _check(f"{lv.name}: all four O-grid blocks carry the ANCHORED "
               f"wall-normal grading {want_y:.6e}",
               surface_block_wall_gradings(text) == [want_y] * 4,
               f"first cell {wall[lv.name][0]:.3e} chord -> total expansion "
               f"{want_y:.6e}")
    _check("the three emitted dictionaries are all different, so the reader "
           "above is not reading one cached text three times",
           len({emitted[lv.name] for lv in LEVELS}) == 3)

    # ---- (v) MUTATION CONTROLS -------------------------------------------
    print("\n(v) MUTATION CONTROLS -- each re-introduces a defect and MUST be "
          "caught")

    # M1: defect 1, the first cell fixed at the anchor value on every level.
    m1 = [ratio_for_first_cell(R, lv.ny, FIRST_CELL_ANCHOR) for lv in LEVELS]
    m1_spread = max(m1) / min(m1) - 1.0
    _check("M1  first cell FIXED at 2e-6 on every level (the pre-repair "
           "behaviour) -> the 7% similarity check in (i) FAILS",
           m1_spread > 0.07,
           "totals " + " / ".join(f"{t:.6e}" for t in m1)
           + f"; spread {100 * m1_spread:.1f}% against the repaired ladder's "
             f"{100 * spread:.2f}%")
    _check("M1b and the per-level VALUE check in (i) separates them: the "
           "fixed ladder puts 2e-6 on medium and fine where the anchored one "
           "puts 1e-6 and 5e-7",
           all(abs(first_cell_for_level(lv) - FIRST_CELL_ANCHOR)
               > 1e-12 * FIRST_CELL_ANCHOR for lv in LEVELS[1:]),
           "anchored " + " / ".join(f"{first_cell_for_level(lv):.1e}"
                                    for lv in LEVELS)
           + f"; mutant {FIRST_CELL_ANCHOR:.1e} on all three")
    # M1c: the PLANT.  The dictionary reader of (iv) must be able to SEE a
    # wrong first cell, or its agreement there is not evidence (rule 3).
    planted = blockmesh_dict(section, LEVELS[2], first_cell=FIRST_CELL_ANCHOR)
    planted_y = surface_block_wall_gradings(planted)
    clean_y = surface_block_wall_gradings(emitted["fine"])
    _check("M1c PLANTED CONTROL: the dictionary reader SEES the pre-repair "
           "first cell when it is planted into the fine level -- a reader "
           "that cannot see the wrong number is not evidence for the right "
           "one",
           planted_y != clean_y and len(set(planted_y)) == 1,
           f"planted (2e-6 at ny=320) -> {planted_y[0]:.6e}; "
           f"anchored (5e-7 at ny=320) -> {clean_y[0]:.6e}")

    # M2: defect 2, the wake-outlet cell fixed at 0.3 chord on every level.
    m2 = [ratio_for_first_cell(R, lv.ny, FAR_FIRST_CELL_ANCHOR)
          for lv in LEVELS]
    _check("M2  wake-outlet cell FIXED at 0.3 chord (the pre-repair "
           "behaviour) -> a BRANCH FLIP: graded 3.747:1 at coarse, UNIFORM at "
           "fine",
           m2[0] > 3.7 and m2[2] == 1.0,
           "totals " + " / ".join(f"{t:.6f}" for t in m2)
           + "; the fine level's 1.000000 is ratio_for_first_cell's "
             "first_cell >= length/n guard, not a grading")
    _refuses("M2b and blockmesh_dict now REFUSES that request at the fine "
             "level instead of silently building an ungraded column",
             lambda: blockmesh_dict(section, LEVELS[2],
                                    far_first_cell=FAR_FIRST_CELL_ANCHOR))
    _refuses("M2c the same guard catches a too-coarse request on the wall "
             "side as well",
             lambda: blockmesh_dict(section, LEVELS[0], first_cell=1.0))

    # M3: the anti-tautology control.  Similarity alone does NOT pin the
    # anchoring, so the explicit VALUE check in (i) is load-bearing.
    m3 = [ratio_for_first_cell(R, lv.ny, 8.0e-6 / refinement_factor(lv))
          for lv in LEVELS]
    m3_spread = max(m3) / min(m3) - 1.0
    m3_yplus_coarse = 8.0e-6 * YPLUS_PER_CHORD_ESTIMATE
    _check("M3  ANTI-TAUTOLOGY: a FINE-anchored ladder (coarse 8e-6) is ALSO "
           "similar, so the similarity check cannot be what pins the "
           "anchoring -- the explicit 2e-6/1e-6/5e-7 value check in (i) is, "
           "and the y+ check is what rejects this alternative",
           m3_spread <= 0.07 and m3_yplus_coarse > 1.0,
           f"fine-anchored spread {100 * m3_spread:.2f}% (passes similarity) "
           f"but its coarse rung sits at y+ {m3_yplus_coarse:.2f} (ESTIMATED), "
           "bridged rather than resolved")

    # M4: a ladder that refines one direction and not another (the L-303 class).
    _refuses("M4  a level refining the surface but NOT the wall normal is "
             "REFUSED -- the Ahmed-ladder defect class (L-303 / N-C1)",
             lambda: refinement_factor(GridLevel("mutant", 96, 96, 80)))
    _refuses("M4b a level refining the wall normal but NOT the wake is "
             "REFUSED too",
             lambda: refinement_factor(GridLevel("mutant", 96, 48, 160)))

    # M5: an anchor whose own request would be discarded rather than built.
    _refuses("M5  anchoring the 0.3-chord wake-outlet request at the FINE "
             "level instead of the coarse one is REFUSED: at ny = 320 it is "
             "not a grading at all",
             lambda: far_first_cell_for_level(LEVELS[2], farfield_r=R,
                                              anchor=LEVELS[2]))

    n_ok = sum(1 for _, ok in _CHECKS if ok)
    n_mut = sum(1 for name, _ in _CHECKS if name.startswith("M"))
    print(f"\n{n_ok}/{len(_CHECKS)} checks passed, {n_mut} of them MUTATION "
          "controls")
    if n_ok != len(_CHECKS):
        print("FAILED: " + "; ".join(name for name, ok in _CHECKS if not ok))
        return 1
    print("This code is UNEXERCISED against a real solve: no mesh has been "
          "built from it and no solver has been run.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true",
                    help="value checks and mutation controls on the mesh "
                         "ladder; builds nothing and launches nothing")
    args = ap.parse_args(argv)
    if not args.selftest:
        ap.error("--selftest is the only action this module offers from the "
                 "command line; it never launches a solver")
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main())
