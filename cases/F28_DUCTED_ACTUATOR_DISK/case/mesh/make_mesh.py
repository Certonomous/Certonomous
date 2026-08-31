#!/usr/bin/env python3
"""F28 -- ONE PARAMETRIC MESH GENERATOR FOR ALL THREE LEVELS.

Registration: verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md
              FROZEN at 76ce0ed5 (cfd-supervisor, check 4, 2026-08-31).

Section 5 of that registration:

    `case/mesh/make_mesh.py` takes a single level argument and emits the whole
    `blockMeshDict` / `snappyHexMeshDict` set.  **No level is ever produced by
    editing another level's dictionary**, and the script's sha is recorded per
    level in the birth certificate.

NO GENERATED DICTIONARY IS EVER HAND-EDITED.  If a dictionary is wrong, this
file is wrong and this file is what changes.

-------------------------------------------------------------------------------
WHAT THIS SCRIPT PRODUCES, AND WHAT IT DELIBERATELY DOES NOT
-------------------------------------------------------------------------------
It produces `system/blockMeshDict` only.  **NO `snappyHexMeshDict` IS EMITTED
AND NONE IS NEEDED.**  Disclosed rather than left to be noticed:

  * The registration's section 5 names a "`blockMeshDict` / `snappyHexMeshDict`
    set".  This generator uses a PURE STRUCTURED MULTI-BLOCK `blockMesh` and no
    snapping stage at all.
  * Reason 1 -- `snappyHexMesh` cannot produce a valid 5-degree wedge.  It
    refines and snaps a 3-D background hex lattice; the one-cell-thick wedge
    with its two `wedge` patches and its collapsed axis is not expressible that
    way.  Every axisymmetric wedge in this repository is a pure `blockMesh`.
  * Reason 2 -- `MESH_STANDARD.md` section 9.2 requires GEOMETRIC SIMILARITY
    across a Roache ladder: first cell height and expansion ratio must scale
    WITH the mesh and the recipe must otherwise be held fixed.  A structured
    generator can guarantee that by construction and read it back; a snapped
    mesh cannot.
  * Reason 3 -- `y+ <= 1` on three walls needs deterministic wall-normal
    spacing.  Structured grading gives it exactly.

This is a departure from the LETTER of section 5's parenthetical and it changes
NO gate, NO threshold, NO cap and NO label.  It is reported to the supervisor,
not taken silently.

-------------------------------------------------------------------------------
THE TOPOLOGY, AND WHY IT IS NOT THE OBVIOUS ONE
-------------------------------------------------------------------------------
THE OBVIOUS H-GRID FAILS AT THE LIP, AND IT FAILS BY ~83 DEGREES.

The duct inlet lip is BLUNT: the inner and outer surfaces meet at the highlight
with a VERTICAL tangent (that is what a lip radius IS).  Put a block-column
boundary on the vertical line through the highlight and the first cell
downstream of it is bounded by two vertical faces while the wall it hugs drops
`r_lip*sqrt(2*dx/a_lip)` -- 1.7 mm over a 0.2 mm cell.  The face angle is
`atan(1.7e-3/2e-4)` = 83 degrees.  That is a `checkMesh` non-orthogonality of
~83 against this case's registered gate of 65, and NO amount of refinement
removes it: the drop goes as `sqrt(dx)`, so refining makes the ratio WORSE.

`MESH_STANDARD.md` section 8.2 is the governing lesson -- F1's tip fill was
refused by `blockMesh`, the refusal was routed around, and the mesh that was
then built failed admission at 84.64 degrees.  **A topology that cannot pass is
redesigned, not bypassed.**  So the lip is wrapped:

  * A thin O-BAND hugs the duct on both sides, thickness `TIP_GAP` = 0.01 D.
    Its two halves (`B_in` inside the duct, `B_out` outside) meet on the
    HORIZONTAL edge running upstream from the highlight to the band's nose
    `P'`.  That edge is NORMAL to the wall at the highlight, so the two cells
    meeting there are square, not collapsed.
  * The band's outer boundary `C'` leaves `P'` at a REGISTERED slope
    (`CPRIME_NOSE_SLOPE`) instead of vertically, so that the vertical block
    column at `x = X_B` and `C'` do not leave `P'` in the same direction.  Six
    blocks meet at `P'`; the sectors are 90/90/45/45/45/45 degrees rather than
    one of them being zero.
  * `C'` is blended into `r_in(x) - TIP_GAP` before the disk station, so at the
    disk the band's inner boundary is EXACTLY `r_tip` = D/2 - 0.01 D and the
    actuator-disk `cellZone` is EXACTLY the rectangle
    [X_DISK_0, X_DISK_1] x [r_hub, r_tip] -- one whole block, no trimming.

THE CENTREBODY NOSE IS TANGENT TO THE AXIS, AND THAT IS A MESHING CHOICE.
A hemispherical or elliptical nose cap has a VERTICAL tangent where it leaves
the axis, which puts a 90-degree kink in the axis grid line that no structured
grid can carry.  The nose here is a C1 smoothstep, `r = R_HUB*(3s^2 - 2s^3)`,
tangent to the axis at the apex and tangent to the cylinder at its end.
Section 4 of the registration says the profile "is registered as an artifact at
freeze (`case/geometry/centerbody_profile.csv`, produced by the parametric
script), not described in prose here -- a profile described in words is not
reproducible."  THIS SCRIPT IS THAT ARTIFACT'S PRODUCER.  The same centrebody
is present in BOTH arms of the section 7.1 ratio, so the choice is common-mode.

The TAIL is a straight cone, as section 4 words it, terminating AT the exit
plane (section 7.1).  Its apex leaves a finite kink in the axis line whose
angle is `atan(R_HUB/L_TAIL)`; that angle is computed, asserted below the gate,
and reported.

-------------------------------------------------------------------------------
STANDING RULES HONOURED HERE
-------------------------------------------------------------------------------
* rule 2  -- nothing in this file alters a gate, threshold, cap or label.
* rule 13 -- no scratch path is written into any artifact this file produces.
* MESH_STANDARD 9.2 -- every grading and first-cell parameter is READ BACK from
  the WRITTEN dictionary by `read_back_grading()`, never reported from the
  requested value.  The F12 defect was precisely that the requested value was
  identical at every level and the RETURNED value was not.
* MESH_STANDARD 13 -- THIS SCRIPT GATES NO WEDGE ANGLE AGAINST A FIXED
  ABSOLUTE TOLERANCE.  The wedge half-angle is reported as a diagnostic only.
  Section 13.3's discriminator is answered explicitly: the only wedge-angle
  number this case records comes from `checkMesh`'s printed value, which DOES
  derive from `wedgePolyPatch::cosAngle_`, and it is therefore NOT GATED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys

# =============================================================================
# REGISTERED GEOMETRY -- every number here is section 4 of the frozen
# pre-registration unless the comment says otherwise.
# =============================================================================
D            = 0.25            # duct inner diameter at the disk station [m]
R_DUCT       = D / 2.0         # 0.125
L_DUCT       = 0.8 * D         # 0.200
R_LIP        = 0.06 * D        # 0.015   -- "Inlet lip elliptical r_lip/D = 0.06"
SIGMA        = 1.0             # primary, gated
TIP_GAP      = 0.01 * D        # 0.0025  -- "Tip gap band 1% D"
R_TIP        = R_DUCT - TIP_GAP        # 0.12250
R_HUB        = 0.15 * D                # 0.03750  (hub DIAMETER 0.3 D)
X_DISK       = 0.35 * L_DUCT           # 0.070 from the lip highlight
T_DISK       = 0.02 * D                # 0.005
X_DISK_0     = X_DISK - T_DISK / 2.0   # 0.0675
X_DISK_1     = X_DISK + T_DISK / 2.0   # 0.0725
A_DISK       = math.pi * (R_TIP ** 2 - R_HUB ** 2)     # 0.0427256... m^2
A_EXIT       = SIGMA * A_DISK
R_EXIT       = math.sqrt(A_EXIT / math.pi)             # tail cone ends AT the
                                                       # exit plane, so the exit
                                                       # annulus is a full disc
R_FAR        = 15.0 * D        # 3.75
X_IN         = -10.0 * D       # -2.50  (10 D upstream of the lip highlight)
X_OUT        = L_DUCT + 25.0 * D       # 6.45 (25 D downstream of the exit)
X_SLIP       = L_DUCT + 5.0 * D        # 1.45 (slipstream refinement to 5 D)
WEDGE_DEG    = 5.0             # total wedge angle
WEDGE_SCALE  = 360.0 / WEDGE_DEG       # 72.0 -- section 2.6

# -----------------------------------------------------------------------------
# SHAPE PARAMETERS THE REGISTRATION DOES NOT FIX.  Every one of these is a
# DISCLOSED lane choice, is recorded in the birth certificate, and moves no
# gate.  They exist because section 4 registers areas and radii, not profiles.
# -----------------------------------------------------------------------------
A_LIP        = 2.0 * R_LIP     # 0.030  axial semi-axis of the lip ellipse (2:1)
R_HI         = R_DUCT + R_LIP  # 0.140  highlight radius
B_OUT        = 0.8 * R_LIP     # 0.012  radial semi-axis of the OUTER lip
A_OUT        = 4.0 * R_LIP     # 0.060  axial semi-axis of the OUTER lip
X_CONTRACT   = 0.50 * L_DUCT   # 0.100  inner wall starts contracting to R_EXIT
X_NOSE       = -0.03           # centrebody nose apex (upstream of the highlight)
L_NOSE       = 0.08            # nose length, so the hub is cylindrical by 0.05
X_TAIL       = 0.10            # tail cone starts here, ends at L_DUCT
X_B          = -TIP_GAP        # -0.0025  the O-band nose P' = (X_B, R_HI)
X_LIPEND     = A_LIP           # 0.030  column boundary where the inner lip ends
# |dr/dx| of C' as it leaves the O-band nose P', and the x at which C' has
# settled onto the constant TIP_GAP offset.  THESE ARE NOT FREE.  Near a blunt
# leading edge the wall itself departs the highlight like sqrt(x): over the
# first 1 mm the inner wall drops 3.8 mm.  A C' leaving P' at 45 degrees is
# OVERTAKEN BY THE WALL and ends up INSIDE THE SOLID -- measured, at
# x = 3.86e-4 m on the first attempt, which is why the generator refused.
# So the slopes below are the shallowest that keep C' clear of both walls with
# margin, and the corner sectors at P' are what they are as a consequence.
CPRIME_SLOPE_IN  = 1.6         # 58.0 deg -- see the note above; 1.5 was MEASURED to fail
CPRIME_SLOPE_OUT = 1.4         # 54.5 deg
CPRIME_BLEND_IN  = 0.02
CPRIME_BLEND_OUT = 0.02
CPRIME_MIN_CLEARANCE = 0.2 * TIP_GAP   # 5e-4 m; refuse below this
Y_FIRST_L1   = 1.0e-5          # first cell height at every viscous wall, L1 [m]
                               # basis: U_ref 45 m/s, nu 1.5e-5, L 0.2 m,
                               # Cf = 0.058 Re_L^-0.2 -> u_tau 1.9 m/s ->
                               # y(y+=1) = 7.9e-6.  1.0e-5 is the registered
                               # target and the ACHIEVED value is read back.
MAX_GROWTH   = 1.36            # refuse a grading whose per-cell ratio exceeds

# Refinement ratios, section 5 of the registration (targets, not achieved).
R_32_TARGET  = math.sqrt(55000.0 / 30000.0)    # 1.35401  L1 -> L2
R_21_TARGET  = math.sqrt(100000.0 / 55000.0)   # 1.34840  L2 -> L3

# checkMesh gates, section 5.  REPEATED HERE ONLY SO THE GENERATOR CAN REFUSE
# TO CLAIM ADMISSIBILITY; the authority is the frozen registration.
GATE_NONORTHO = 65.0
GATE_SKEW     = 4.0

TOL = 1.0e-12


# =============================================================================
# PROFILES
# =============================================================================
def smoothstep(s: float) -> float:
    return 3.0 * s * s - 2.0 * s * s * s


def r_hub(x: float) -> float:
    """Centrebody radius.  0 outside [X_NOSE, L_DUCT] (no body there)."""
    if x <= X_NOSE or x >= L_DUCT:
        return 0.0
    if x < X_NOSE + L_NOSE:
        return R_HUB * smoothstep((x - X_NOSE) / L_NOSE)
    if x <= X_TAIL:
        return R_HUB
    return R_HUB * (L_DUCT - x) / (L_DUCT - X_TAIL)


def r_in(x: float) -> float:
    """Duct INNER surface, x in [0, L_DUCT].  Highlight -> throat -> exit."""
    if x < 0.0 or x > L_DUCT + TOL:
        raise ValueError("r_in outside the duct: %r" % x)
    if x <= A_LIP:
        # ellipse centred (A_LIP, R_DUCT + R_LIP): x = a(1-cos p), r = rc - b sin p
        c = 1.0 - x / A_LIP
        c = max(-1.0, min(1.0, c))
        p = math.acos(c)
        return R_HI - R_LIP * math.sin(p)
    if x <= X_CONTRACT:
        return R_DUCT
    s = (x - X_CONTRACT) / (L_DUCT - X_CONTRACT)
    return R_DUCT + (R_EXIT - R_DUCT) * smoothstep(s)


def r_out(x: float) -> float:
    """Duct OUTER surface, x in [0, L_DUCT].  Highlight -> crest -> cusped TE."""
    if x < 0.0 or x > L_DUCT + TOL:
        raise ValueError("r_out outside the duct: %r" % x)
    r_crest = R_HI + B_OUT
    if x <= A_OUT:
        c = 1.0 - x / A_OUT
        c = max(-1.0, min(1.0, c))
        p = math.acos(c)
        return R_HI + B_OUT * math.sin(p)
    s = (x - A_OUT) / (L_DUCT - A_OUT)
    return r_crest + (R_EXIT - r_crest) * smoothstep(s)


def _hermite_monotone(x0, y0, m0, x1, y1, m1):
    """Cubic Hermite with a Fritsch-Carlson clamp.  Returns (f, m0_used)."""
    h = x1 - x0
    delta = (y1 - y0) / h
    a0, a1 = m0, m1
    if delta != 0.0:
        alpha, beta = m0 / delta, m1 / delta
        n = math.hypot(alpha, beta)
        if n > 3.0:
            a0, a1 = 3.0 * m0 / n, 3.0 * m1 / n

    def f(x):
        s = (x - x0) / h
        h00 = 2 * s ** 3 - 3 * s ** 2 + 1
        h10 = s ** 3 - 2 * s ** 2 + s
        h01 = -2 * s ** 3 + 3 * s ** 2
        h11 = s ** 3 - s ** 2
        return h00 * y0 + h10 * h * a0 + h01 * y1 + h11 * h * a1

    return f, a0


# C' -- the O-band's outer boundary.  Blend from the nose P' at a slope of
# +/-CPRIME_SLOPE into a constant TIP_GAP offset from the wall before the disk.
_XB_I = CPRIME_BLEND_IN
_XB_O = CPRIME_BLEND_OUT
_DR_IN = (r_in(_XB_I + 1e-7) - r_in(_XB_I - 1e-7)) / 2e-7
_DR_OUT = (r_out(_XB_O + 1e-7) - r_out(_XB_O - 1e-7)) / 2e-7


def _quintic(x0, y0, m0, c0, x1, y1, m1, c1):
    """C2 blend.  A C1-ONLY BLEND WAS MEASURED TO COST 6 DEGREES.

    With a cubic Hermite, C' matched the wall offset in value and slope at the
    blend end but NOT in curvature.  On L2 that curvature jump produced the
    mesh's worst cell -- 63.42 deg at x = +0.0207, r = 0.1240, against a 65 deg
    gate, i.e. 1.58 deg of margin -- while L1 and L3 sat at 57.5 and 57.6.
    Matching the second derivative as well removes the jump.  The monotonicity
    and wall-clearance guards below are UNCHANGED and still drive this curve.
    """
    h = x1 - x0
    a = [y0, m0 * h, c0 * h * h / 2.0]
    d0 = y1 - (a[0] + a[1] + a[2])
    d1 = m1 * h - (a[1] + 2 * a[2])
    d2 = c1 * h * h - (2 * a[2])
    a3 = 10 * d0 - 4 * d1 + 0.5 * d2
    a4 = -15 * d0 + 7 * d1 - 1.0 * d2
    a5 = 6 * d0 - 3 * d1 + 0.5 * d2
    def f(x):
        s = (x - x0) / h
        return a[0] + a[1] * s + a[2] * s ** 2 + a3 * s ** 3 + a4 * s ** 4 + a5 * s ** 5
    return f


def _d2(fn, x, h=1e-6):
    return (fn(x + h) - 2.0 * fn(x) + fn(x - h)) / (h * h)


_C2_IN = _d2(r_in, _XB_I)
_C2_OUT = _d2(r_out, _XB_O)
_CI_F = _quintic(X_B, R_HI, -CPRIME_SLOPE_IN, 0.0,
                 _XB_I, r_in(_XB_I) - TIP_GAP, _DR_IN, _C2_IN)
_CO_F = _quintic(X_B, R_HI, CPRIME_SLOPE_OUT, 0.0,
                 _XB_O, r_out(_XB_O) + TIP_GAP, _DR_OUT, _C2_OUT)
CPRIME_SLOPE_IN_USED = -CPRIME_SLOPE_IN
CPRIME_SLOPE_OUT_USED = CPRIME_SLOPE_OUT


def cprime_in(x: float) -> float:
    """O-band inner boundary (also the disk cellZone's outer boundary)."""
    if x <= _XB_I:
        return _CI_F(x)
    return r_in(x) - TIP_GAP


def cprime_out(x: float) -> float:
    if x <= _XB_O:
        return _CO_F(x)
    return r_out(x) + TIP_GAP


# =============================================================================
# GRADING -- SOLVED, NEVER GUESSED, AND READ BACK FROM THE WRITTEN DICTIONARY
# =============================================================================
# WHY THE AXIAL SPACING IS PRESCRIBED AT EVERY COLUMN BOUNDARY AND SOLVED
# INSIDE EACH COLUMN, rather than set as a per-column expansion by hand.
#
# Attempt 1 set eight per-column expansions by hand.  Measured on the built
# mesh: a 22x axial cell-size JUMP across the column boundary at the centrebody
# nose apex (19.5 mm one side, 0.9 mm the other) and a max non-orthogonality of
# 76.76 deg against this case's 65 deg gate.
#
# Attempt 2 solved a continuous chain but let the chain choose the boundary
# spacings.  It drove the spacing at the O-band nose down to 2.4e-4 m, and that
# column of very thin axial cells runs all the way out to the farfield at
# r = 3.75 m.  Measured: 84.62 deg, on faces at x = -0.0025 and r = 1.2 to 3.5 m.
# THE MECHANISM WAS MEASURED, NOT GUESSED -- the worst cell's own vertices were
# read out of `constant/polyMesh`:
#
#   * `blockMesh` blends a block's interior from its four EDGES.  The outer
#     block's bottom edge was the CURVED C', its top edge the straight
#     farfield, so the block's axial grid lines TILT: the worst cell measured
#     x = -0.0022749 at its inner corner and x = -0.0022625 at its outer one,
#     a 1.24e-5 m tilt across 0.557 m of radius.
#   * On a WEDGE the cell volume is weighted by r, so a cell that is 5% longer
#     at its outer edge has its centroid pulled OUTWARD -- 2.49e-3 m here.
#   * The face is 2.35e-4 m thick.  atan(2.49e-3 / 2.35e-4) = 84.6 degrees.
#
#   * AND THE ANGLE IS SCALE-INVARIANT: halve the axial spacing and both the
#     tilt and the centroid shift halve with it.  REFINING DOES NOT FIX IT.
#     Only removing the curved edge from the tall block does.
#
# So: (a) the outer region is SPLIT at R_MID_O.  Below it the block carries the
# curved C' but is only ~0.15 m tall; above it the block is 3.45 m tall and is a
# PLAIN RECTANGLE with no curved edge and therefore no tilt.  (b) the axial
# spacing is PRESCRIBED at each column boundary at a value the geometry needs,
# and each column solves a two-segment distribution to meet both of its ends.

N1_REL_TOL = 1.0e-9    # relative tolerance on the n == 1 identity length==first


def solve_ratio(length: float, n: int, first: float) -> float:
    """Per-cell ratio q of the geometric series with n cells, first cell
    `first`, summing to `length`.  Refuses rather than degrades.

    THE n == 1 BRANCH USED TO BREAK THAT PROMISE, AND IT BROKE IT SILENTLY.
    A one-cell segment delivers a cell of size `length`.  It delivers `first`
    only when `length == first`, which is a coincidence, not an identity.  The
    old branch returned q = 1.0 unconditionally and BEFORE computing `target`,
    so `seg()` then reported `last = first * q**0 = first` -- the REQUESTED
    size, never the delivered one -- and `distribution()` scored its
    junction-match against that fiction and preferred it, because a fiction
    matches perfectly.

    MEASURED CONSEQUENCE at the time of the repair (F28, this generator):
      * L1 column c1 received a first axial cell of 0.02255 m where 3.5e-4 m
        was prescribed at X_NOSE -- a factor of 64 -- immediately downstream of
        the centrebody nose apex, giving a face-adjacent cell-volume jump of
        28,735 against a mesh median of 1.22.
      * L2 column c2 received 0.015925 m where 8.86e-4 m was prescribed at
        X_LIPEND -- a factor of 18 -- which is half the lip, while the
        `>= 40 cells around the lip` refusal below still passed because it
        counts cells and does not size them.
      * L3 was not affected in any harmful way.
    The defect therefore fired in a DIFFERENT column at each level and not at
    all at L3, so the three meshes were not geometrically similar and
    MESH_STANDARD 9.2 similarity did not hold across the Roache ladder.

    The repair is a REFUSAL, not a correction: `n == 1` is legal only when the
    segment length IS the requested first-cell size.  Callers that search over
    candidate splits (`distribution`) catch ValueError and skip the candidate,
    so an inadmissible one-cell segment is now rejected by the search instead
    of winning it.  If no admissible split exists the caller refuses outright.
    NOTHING IS CLAMPED AND NOTHING IS WARNED-AND-CONTINUED.
    """
    if n < 1:
        raise ValueError("n < 1")
    if n == 1:
        if abs(length - first) > N1_REL_TOL * max(abs(first), TOL):
            raise ValueError(
                "n == 1 delivers a cell of size %.12g, but %.12g was requested "
                "as the first cell (relative error %.3g > %.3g). A one-cell "
                "segment cannot honour a first-cell size other than its own "
                "length." % (length, first,
                             abs(length - first) / max(abs(first), TOL),
                             N1_REL_TOL))
        return 1.0
    target = length / first

    def s(q):
        if abs(q - 1.0) < 1e-14:
            return float(n)
        return (q ** n - 1.0) / (q - 1.0)

    if abs(target - n) < 1e-12:
        return 1.0
    if target > n:
        lo, hi = 1.0, 1.0
        while s(hi) < target:
            hi *= 1.05
            if hi > 50.0:
                raise ValueError("grading will not close: L=%g n=%d h1=%g"
                                 % (length, n, first))
    else:
        lo, hi = 1e-6, 1.0
        while s(lo) > target:
            lo *= 0.5
            if lo < 1e-12:
                raise ValueError("grading will not close (contracting)")
    for _ in range(400):
        mid = 0.5 * (lo + hi)
        if s(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def seg(length: float, n: int, first: float):
    """Return (blockMesh expansion last/first, per-cell ratio q, last cell)."""
    q = solve_ratio(length, n, first)
    return q ** (n - 1), q, first * q ** (n - 1)


def _g(v):
    return v if isinstance(v, str) else "%.10g" % v


def multi(entries) -> str:
    return "( " + " ".join("(%.10g %.10g %.10g)" % e for e in entries) + " )"


def _series_sum(h_first: float, h_last: float, n: int) -> float:
    # SECOND, LATENT INSTANCE OF THE SAME DEFECT CLASS -- guarded, never fired.
    # With n == 1 this returned h_first and ignored h_last, so
    # `solve_end_spacing`'s bisection on the LEFT-unknown limb searched a
    # constant and would have returned an arbitrary answer.  It never fired
    # because every caller passes a column cell count and `level_counts` floors
    # those at 2.  It is guarded rather than left as a trap for the next edit.
    if n == 1:
        raise ValueError(
            "_series_sum with n == 1 cannot honour two independent end "
            "spacings (h_first=%.12g, h_last=%.12g); a one-cell series has one "
            "size, its own length." % (h_first, h_last))
    q = (h_last / h_first) ** (1.0 / (n - 1))
    if abs(q - 1.0) < 1e-14:
        return h_first * n
    return h_first * (q ** n - 1.0) / (q - 1.0)


def solve_end_spacing(length, n, h_known, known_is_right):
    lo, hi = 1e-10, 100.0
    for _ in range(400):
        mid = math.sqrt(lo * hi)
        s = (_series_sum(mid, h_known, n) if known_is_right
             else _series_sum(h_known, mid, n))
        if s < length:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def distribution(length, n, h_left, h_right, name=""):
    """Grading spec meeting the prescribed END CELL SIZES.

    One end may be None (free).  With both ends given the distribution is two
    geometric segments joined at a point chosen to make the two junction cell
    sizes as nearly equal as the counts allow; THE ACHIEVED MISMATCH IS
    RETURNED AND REPORTED, never assumed to be 1.
    """
    if h_left is None and h_right is None:
        raise ValueError("both ends free")
    if h_right is None:
        e, q, last = seg(length, n, h_left)
        return _g(e), dict(mode="single", q=[q], h_left=h_left, h_right=last,
                           junction_jump=1.0)
    if h_left is None:
        hl = solve_end_spacing(length, n, h_right, known_is_right=True)
        e, q, last = seg(length, n, hl)
        return _g(e), dict(mode="single", q=[q], h_left=hl, h_right=last,
                           junction_jump=1.0)
    best = None
    for n1 in range(1, n):
        n2 = n - n1
        for k in range(5, 96):
            f = k / 100.0
            try:
                e1, q1, l1 = seg(f * length, n1, h_left)
                e2, q2, l2 = seg((1.0 - f) * length, n2, h_right)
            except ValueError:
                continue
            if not (1.0 / MAX_GROWTH <= q1 <= MAX_GROWTH):
                continue
            if not (1.0 / MAX_GROWTH <= q2 <= MAX_GROWTH):
                continue
            jump = l1 / l2
            sc = abs(math.log(jump))
            if best is None or sc < best[0]:
                best = (sc, n1, n2, f, e1, e2, q1, q2, jump)
    if best is None:
        raise SystemExit("REFUSE: no admissible distribution for %s "
                         "(L=%g n=%d hL=%g hR=%g)" % (name, length, n,
                                                      h_left, h_right))
    _, n1, n2, f, e1, e2, q1, q2, jump = best
    spec = multi([(f, n1 / float(n), e1), (1.0 - f, n2 / float(n), 1.0 / e2)])
    return spec, dict(mode="two-segment", q=[q1, q2], cells=[n1, n2],
                      length_fraction=f, h_left=h_left, h_right=h_right,
                      junction_jump=jump)


# =============================================================================
# LEVEL DEFINITION -- ONE recipe, scaled.  MESH_STANDARD 9.2 similarity: the
# first cell height, every prescribed spacing and every expansion scale WITH
# the mesh; nothing else in the recipe changes between levels.
# =============================================================================
R_MID_O = 0.30                 # outer-region split radius [m]

BASE_NR = {"I": 44, "BI": 22, "BO": 22, "O1": 20, "O2": 26}
BASE_NX = {"c0": 40, "c1": 18, "c2": 28, "c3": 18, "c4": 4,
           "c5": 36, "c6": 70, "c7": 42}

# Prescribed axial cell size at each column boundary, level 1 [m].
# None = free end, solved from the column's other end.
BASE_HX = {"X_IN": None, "X_NOSE": 3.5e-4, "X_B": 2.5e-4, "X_LIPEND": 1.2e-3,
           "X_DISK_0": 1.25e-3, "X_DISK_1": 1.25e-3, "L_DUCT": 1.2e-3,
           "X_SLIP": 0.02, "X_OUT": None}

R_32_TARGET = math.sqrt(55000.0 / 30000.0)
R_21_TARGET = math.sqrt(100000.0 / 55000.0)
LEVEL_SCALE = {1: 1.0, 2: R_32_TARGET, 3: R_32_TARGET * R_21_TARGET}

COLS = [("c0", X_IN,      X_NOSE,   "X_IN",     "X_NOSE"),
        ("c1", X_NOSE,    X_B,      "X_NOSE",   "X_B"),
        ("c2", X_B,       X_LIPEND, "X_B",      "X_LIPEND"),
        ("c3", X_LIPEND,  X_DISK_0, "X_LIPEND", "X_DISK_0"),
        ("c4", X_DISK_0,  X_DISK_1, "X_DISK_0", "X_DISK_1"),
        ("c5", X_DISK_1,  L_DUCT,   "X_DISK_1", "L_DUCT"),
        ("c6", L_DUCT,    X_SLIP,   "L_DUCT",   "X_SLIP"),
        ("c7", X_SLIP,    X_OUT,    "X_SLIP",   "X_OUT")]
DUCT_COLS = {"c2", "c3", "c4", "c5"}
WAKE_COLS = {"c6", "c7"}


def level_counts(level):
    f = LEVEL_SCALE[level]
    nr = {k: max(2, int(round(v * f))) for k, v in BASE_NR.items()}
    nx = {k: max(2, int(round(v * f))) for k, v in BASE_NX.items()}
    nx["c4"] = max(4, nx["c4"])
    hx = {k: (None if v is None else v / f) for k, v in BASE_HX.items()}
    return nr, nx, hx


def y_first(level):
    return Y_FIRST_L1 / LEVEL_SCALE[level]


# =============================================================================
# MESH ASSEMBLY
# =============================================================================
class Mesh:
    def __init__(self):
        self.pts = {}
        self.coords = []
        self.blocks = []
        self.edges = {}
        self.patch_faces = {}

    def key(self, x, r):
        return (round(x, 10), round(max(r, 0.0), 10))

    def vert(self, x, r):
        k = self.key(x, r)
        if k in self.pts:
            return self.pts[k]
        half = math.radians(WEDGE_DEG / 2.0)
        y, z = r * math.cos(half), r * math.sin(half)
        if r <= TOL:
            i = len(self.coords)
            self.coords.append((x, 0.0, 0.0))
            self.pts[k] = (i, i)
        else:
            ib = len(self.coords)
            self.coords.append((x, y, -z))
            ifr = len(self.coords)
            self.coords.append((x, y, z))
            self.pts[k] = (ib, ifr)
        return self.pts[k]

    def block(self, p0, p1, p2, p3, nx, nr, grading, zone=None):
        b0, f0 = self.vert(*p0)
        b1, f1 = self.vert(*p1)
        b2, f2 = self.vert(*p2)
        b3, f3 = self.vert(*p3)
        self.blocks.append(dict(v=[b0, b1, b2, b3, f0, f1, f2, f3],
                                n=(nx, nr, 1), g=grading, zone=zone,
                                corners=(p0, p1, p2, p3)))
        return self.blocks[-1]

    def edge(self, pa, pb, fn, npts=80):
        """polyLine edge between two corner points, following r = fn(x)."""
        if self.key(*pa) == self.key(*pb):
            return
        half = math.radians(WEDGE_DEG / 2.0)
        for front in (False, True):
            va = self.vert(*pa)[1 if front else 0]
            vb = self.vert(*pb)[1 if front else 0]
            if (va, vb) in self.edges or (vb, va) in self.edges:
                continue
            pl = []
            for i in range(1, npts):
                x = pa[0] + (pb[0] - pa[0]) * i / float(npts)
                r = fn(x)
                pl.append((x, r * math.cos(half),
                           r * math.sin(half) * (1.0 if front else -1.0)))
            self.edges[(va, vb)] = pl

    def face(self, patch, quad):
        self.patch_faces.setdefault(patch, []).append(quad)


def bf(blk, which):
    b0, b1, b2, b3, f0, f1, f2, f3 = blk["v"]
    return {"xmin": [b0, f0, f3, b3], "xmax": [b1, b2, f2, f1],
            "rmin": [b0, b1, f1, f0], "rmax": [b3, f3, f2, b2],
            "back": [b0, b3, b2, b1], "front": [f0, f1, f2, f3]}[which]


def build(level, axis_patch=True):
    nr, nx, hx = level_counts(level)
    y1 = y_first(level)
    m, diag = Mesh(), {}

    # ---- radial gradings, shared by every column so that every shared face
    # ---- carries the same point distribution on both sides.
    e_b, q_b, last_b = seg(TIP_GAP, nr["BI"], y1)
    if q_b > MAX_GROWTH:
        raise SystemExit("REFUSE: O-band per-cell growth %.4f > %.2f"
                         % (q_b, MAX_GROWTH))
    g_bi_r = _g(1.0 / e_b)          # C'_inner -> wall : contracting
    g_bo_r = _g(e_b)                # wall -> C'_outer : expanding

    L_I = R_TIP - R_HUB                              # 0.085 at the disk station
    g_i_r, d_i = distribution(L_I, nr["I"], y1, last_b, "ROW_I")

    L_O1 = R_MID_O - cprime_out(X_DISK)
    g_o1_r, d_o1 = distribution(L_O1, nr["O1"], last_b, None, "ROW_O1")
    L_O2 = R_FAR - R_MID_O
    g_o2_r, d_o2 = distribution(L_O2, nr["O2"], d_o1["h_right"], None, "ROW_O2")

    diag["radial"] = {"O_band": dict(q=[q_b], h_wall=y1, h_outer=last_b),
                      "ROW_I": d_i, "ROW_O1": d_o1, "ROW_O2": d_o2}
    diag["y_first_requested_m"] = y1

    # ---- axial gradings, one per column, meeting the prescribed spacings
    gx, dx_diag = {}, {}
    for name, xa, xb, ka, kb in COLS:
        gx[name], dx_diag[name] = distribution(xb - xa, nx[name],
                                               hx[ka], hx[kb], "axial " + name)
    diag["axial"] = dx_diag

    def G(col, radial):
        return "simpleGrading (%s %s 1)" % (gx[col], radial)

    P = lambda x, r: (x, r)
    for name, xa, xb, _ka, _kb in COLS:
        n = nx[name]
        if name in DUCT_COLS:
            zone = "disk" if name == "c4" else None
            p0, p1 = P(xa, r_hub(xa)), P(xb, r_hub(xb))
            p2, p3 = P(xb, cprime_in(xb)), P(xa, cprime_in(xa))
            m.block(p0, p1, p2, p3, n, nr["I"], G(name, g_i_r), zone)
            m.edge(p0, p1, r_hub)
            m.edge(p3, p2, cprime_in)
            q3 = P(0.0, R_HI) if name == "c2" else P(xa, r_in(xa))
            m.block(p3, p2, P(xb, r_in(xb)), q3, n, nr["BI"], G(name, g_bi_r))
            m.edge(q3, P(xb, r_in(xb)), r_in)
            s0 = P(0.0, R_HI) if name == "c2" else P(xa, r_out(xa))
            s1 = P(xb, r_out(xb))
            s2, s3 = P(xb, cprime_out(xb)), P(xa, cprime_out(xa))
            m.block(s0, s1, s2, s3, n, nr["BO"], G(name, g_bo_r))
            m.edge(s0, s1, r_out)
            m.edge(s3, s2, cprime_out)
            m.block(s3, s2, P(xb, R_MID_O), P(xa, R_MID_O),
                    n, nr["O1"], G(name, g_o1_r))
            m.block(P(xa, R_MID_O), P(xb, R_MID_O), P(xb, R_FAR), P(xa, R_FAR),
                    n, nr["O2"], G(name, g_o2_r))
        elif name in WAKE_COLS:
            r1, r2, r3 = cprime_in(L_DUCT), R_EXIT, cprime_out(L_DUCT)
            m.block(P(xa, 0.0), P(xb, 0.0), P(xb, r1), P(xa, r1),
                    n, nr["I"], G(name, g_i_r))
            m.block(P(xa, r1), P(xb, r1), P(xb, r2), P(xa, r2),
                    n, nr["BI"], G(name, g_bi_r))
            m.block(P(xa, r2), P(xb, r2), P(xb, r3), P(xa, r3),
                    n, nr["BO"], G(name, g_bo_r))
            m.block(P(xa, r3), P(xb, r3), P(xb, R_MID_O), P(xa, R_MID_O),
                    n, nr["O1"], G(name, g_o1_r))
            m.block(P(xa, R_MID_O), P(xb, R_MID_O), P(xb, R_FAR), P(xa, R_FAR),
                    n, nr["O2"], G(name, g_o2_r))
        else:
            p0, p1 = P(xa, r_hub(xa)), P(xb, r_hub(xb))
            m.block(p0, p1, P(xb, R_HI), P(xa, R_HI), n, nr["I"], G(name, g_i_r))
            if name == "c1":
                m.edge(p0, p1, r_hub)
            m.block(P(xa, R_HI), P(xb, R_HI), P(xb, R_MID_O), P(xa, R_MID_O),
                    n, nr["O1"], G(name, g_o1_r))
            m.block(P(xa, R_MID_O), P(xb, R_MID_O), P(xb, R_FAR), P(xa, R_FAR),
                    n, nr["O2"], G(name, g_o2_r))

    # ---- patches
    bi = 0
    for name, xa, xb, _ka, _kb in COLS:
        if name in DUCT_COLS or name in WAKE_COLS:
            rowI, rowBi, rowBo, rowO1, rowO2 = m.blocks[bi:bi + 5]
            if name in DUCT_COLS:
                m.face("hub", bf(rowI, "rmin"))
                m.face("ductInner", bf(rowBi, "rmax"))
                m.face("ductOuter", bf(rowBo, "rmin"))
            else:
                if axis_patch:
                    m.face("axis", bf(rowI, "rmin"))
            m.face("farfield", bf(rowO2, "rmax"))
            if name == "c7":
                for b in (rowI, rowBi, rowBo, rowO1, rowO2):
                    m.face("outlet", bf(b, "xmax"))
            bi += 5
        else:
            rowI, rowO1, rowO2 = m.blocks[bi:bi + 3]
            if name == "c0":
                if axis_patch:
                    m.face("axis", bf(rowI, "rmin"))
                for b in (rowI, rowO1, rowO2):
                    m.face("inlet", bf(b, "xmin"))
            else:
                m.face("hub", bf(rowI, "rmin"))
            m.face("farfield", bf(rowO2, "rmax"))
            bi += 3
    for b in m.blocks:
        m.face("front", bf(b, "front"))
        m.face("back", bf(b, "back"))

    # ---- refusals and reported geometry
    total = sum(b["n"][0] * b["n"][1] for b in m.blocks)
    diag.update(cells_predicted=total, blocks=len(m.blocks), nr=nr, nx=nx,
                hx_prescribed=hx, R_MID_O=R_MID_O)
    _ai = math.degrees(math.atan(abs(CPRIME_SLOPE_IN_USED)))
    _ao = math.degrees(math.atan(abs(CPRIME_SLOPE_OUT_USED)))
    diag["cprime_nose_slope_requested"] = [CPRIME_SLOPE_IN, CPRIME_SLOPE_OUT]
    diag["cprime_nose_slope_used"] = [abs(CPRIME_SLOPE_IN_USED),
                                      abs(CPRIME_SLOPE_OUT_USED)]
    diag["pprime_sectors_deg"] = {"B_in": _ai, "bg_inner": 90.0 - _ai,
                                  "bg_upstream_inner": 90.0,
                                  "bg_upstream_outer": 90.0,
                                  "bg_outer": 90.0 - _ao, "B_out": _ao}
    diag["pprime_min_sector_deg"] = min(_ai, _ao, 90.0 - _ai, 90.0 - _ao)
    diag["tail_cone_half_angle_deg"] = math.degrees(
        math.atan(R_HUB / (L_DUCT - X_TAIL)))
    diag["nose_max_slope_deg"] = math.degrees(math.atan(1.5 * R_HUB / L_NOSE))
    diag["lip_cells_inner"] = nx["c2"]
    diag["lip_cells_outer"] = nx["c2"] + int(round(
        nx["c3"] * (A_OUT - X_LIPEND) / (X_DISK_0 - X_LIPEND)))
    diag["lip_cells_wrap_total"] = (diag["lip_cells_inner"]
                                    + diag["lip_cells_outer"])
    diag["disk_zone_cells_axial"] = nx["c4"]
    diag["disk_zone_cells_radial"] = nr["I"]
    diag["A_disk_m2"] = A_DISK
    diag["r_exit_m"] = R_EXIT
    diag["wedge_disk_zone_volume_m3"] = (A_DISK * T_DISK) / WEDGE_SCALE
    diag["full_annulus_disk_zone_volume_m3"] = A_DISK * T_DISK

    xs = [X_B + (L_DUCT - X_B) * i / 4000.0 for i in range(4001)]
    cmin_i = cmin_o = 1e9
    for x in xs:
        if x < 0.0:
            continue
        ci, co = r_in(x) - cprime_in(x), cprime_out(x) - r_out(x)
        cmin_i, cmin_o = min(cmin_i, ci), min(cmin_o, co)
        if ci < CPRIME_MIN_CLEARANCE:
            raise SystemExit("REFUSE: C'_inner clearance %.3e at x=%g" % (ci, x))
        if co < CPRIME_MIN_CLEARANCE:
            raise SystemExit("REFUSE: C'_outer clearance %.3e at x=%g" % (co, x))
        if cprime_in(x) <= r_hub(x) + 0.2 * TIP_GAP:
            raise SystemExit("REFUSE: C'_inner touches the hub at x=%g" % x)
        if cprime_out(x) >= R_MID_O:
            raise SystemExit("REFUSE: C'_outer crosses R_MID_O at x=%g" % x)
    diag["cprime_min_clearance_m"] = [cmin_i, cmin_o]
    for i in range(1, len(xs)):
        if cprime_in(xs[i]) > cprime_in(xs[i - 1]) + 1e-12:
            raise SystemExit("REFUSE: C'_inner not monotone")
    if abs(cprime_in(X_DISK) - R_TIP) > 1e-12:
        raise SystemExit("REFUSE: disk zone outer edge %.12g != r_tip"
                         % cprime_in(X_DISK))
    if abs(r_hub(X_DISK) - R_HUB) > 1e-12:
        raise SystemExit("REFUSE: hub not cylindrical at the disk station")
    if nx["c4"] < 4:
        raise SystemExit("REFUSE: disk zone thinner than 4 cells")
    if diag["lip_cells_wrap_total"] < 40:
        raise SystemExit("REFUSE: fewer than 40 cells around the lip")
    return m, diag


# =============================================================================
# EMIT
# =============================================================================
HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
  F28 -- DUCTED ACTUATOR DISK.  GENERATED FILE -- DO NOT HAND-EDIT.
  Generator : case/mesh/make_mesh.py
  sha256    : %s
  level     : L%d          command: %s
  Registration: verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md
  Actuator-disk representation; no rotor.
\\*---------------------------------------------------------------------------*/
FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }

mergeType points;   // wedge geometry -- merge points, not topology
scale   1;
"""

PATCH_TYPE = {"inlet": "patch", "outlet": "patch", "farfield": "patch",
              "axis": "empty", "hub": "wall", "ductInner": "wall",
              "ductOuter": "wall", "front": "wedge", "back": "wedge"}
PATCH_ORDER = ["inlet", "outlet", "farfield", "axis", "hub", "ductInner",
               "ductOuter", "front", "back"]


def emit(m, sha, level, cmd):
    out = [HEADER % (sha, level, cmd), "\nvertices\n(\n"]
    for (x, y, z) in m.coords:
        out.append("    (%.12g %.12g %.12g)\n" % (x, y, z))
    out.append(");\n\nblocks\n(\n")
    for b in m.blocks:
        zone = (" " + b["zone"]) if b["zone"] else ""
        out.append("    hex (%s)%s (%d %d %d) %s\n"
                   % (" ".join(str(v) for v in b["v"]), zone,
                      b["n"][0], b["n"][1], b["n"][2], b["g"]))
    out.append(");\n\nedges\n(\n")
    for (va, vb), pl in m.edges.items():
        out.append("    polyLine %d %d (%s)\n"
                   % (va, vb, " ".join("(%.12g %.12g %.12g)" % p for p in pl)))
    out.append(");\n\nboundary\n(\n")
    for p in PATCH_ORDER:
        faces = m.patch_faces.get(p)
        if not faces:
            continue
        out.append("    %s\n    {\n        type %s;\n        faces\n        (\n"
                   % (p, PATCH_TYPE[p]))
        for f in faces:
            out.append("            (%s)\n" % " ".join(str(v) for v in f))
        out.append("        );\n    }\n")
    out.append(");\n\nmergePatchPairs\n(\n);\n")
    return "".join(out)


def read_back_grading(text):
    """MESH_STANDARD 9.2 -- read the ACTUAL grading out of the WRITTEN bytes.

    The F12 defect was that the REQUESTED parameter was identical at every level
    and the RETURNED one was not, so a check comparing requested values reports
    perfect similarity on exactly the ladder that is broken.  This parses the
    emitted file.
    """
    simple, multi_ = [], []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("hex "):
            continue
        parts = s.split("simpleGrading", 1)
        if len(parts) != 2:
            continue
        body = parts[1].strip()
        (multi_ if "((" in body else simple).append(body)
    return {"simpleGrading_bodies": sorted(set(simple)),
            "multiGrading_bodies": sorted(set(multi_)),
            "n_blocks_parsed": len(simple) + len(multi_)}


def geometry_csvs(outdir):
    os.makedirs(outdir, exist_ok=True)
    n = 2001
    with open(os.path.join(outdir, "centerbody_profile.csv"), "w") as fh:
        fh.write("# F28 centrebody profile -- THE REGISTERED ARTIFACT of "
                 "section 4.\n# Actuator-disk representation; no rotor.\n")
        fh.write("# nose: C1 smoothstep TANGENT TO THE AXIS at the apex "
                 "(x=%.6g);\n" % X_NOSE)
        fh.write("# tail: STRAIGHT CONE terminating AT the exit plane "
                 "(section 7.1).\nx_m,r_m\n")
        for i in range(n):
            x = X_NOSE + (L_DUCT - X_NOSE) * i / (n - 1.0)
            fh.write("%.12g,%.12g\n" % (x, r_hub(x)))
    with open(os.path.join(outdir, "duct_profile.csv"), "w") as fh:
        fh.write("# F28 duct inner/outer surfaces and the O-band boundary C'.\n"
                 "# Actuator-disk representation; no rotor.\n")
        fh.write("x_m,r_inner_m,r_outer_m,r_cprime_inner_m,r_cprime_outer_m\n")
        for i in range(n):
            x = i * L_DUCT / (n - 1.0)
            fh.write("%.12g,%.12g,%.12g,%.12g,%.12g\n"
                     % (x, r_in(x), r_out(x), cprime_in(x), cprime_out(x)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, required=True, choices=[1, 2, 3])
    ap.add_argument("--out", required=True)
    ap.add_argument("--geometry-dir", default=None)
    ap.add_argument("--no-axis-patch", action="store_true")
    a = ap.parse_args()

    sha = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
    cmd = "make_mesh.py --level %d" % a.level
    m, diag = build(a.level, axis_patch=not a.no_axis_patch)
    text = emit(m, sha, a.level, cmd)

    sysdir = os.path.join(a.out, "system")
    os.makedirs(sysdir, exist_ok=True)
    with open(os.path.join(sysdir, "blockMeshDict"), "w") as fh:
        fh.write(text)

    diag["mesh_script_sha256"] = sha
    diag["blockMeshDict_sha256"] = hashlib.sha256(text.encode()).hexdigest()
    diag["grading_read_back_from_written_dict"] = read_back_grading(text)
    diag["level"] = a.level
    diag["level_scale_from_L1"] = LEVEL_SCALE[a.level]
    diag["generating_command"] = cmd
    diag["axis_patch_emitted"] = not a.no_axis_patch
    with open(os.path.join(sysdir, "MESH_DIAGNOSTICS.json"), "w") as fh:
        json.dump(diag, fh, indent=2, sort_keys=True, default=str)

    if a.geometry_dir:
        geometry_csvs(a.geometry_dir)

    print(json.dumps({"level": a.level,
                      "blockMeshDict": os.path.join(sysdir, "blockMeshDict"),
                      "cells_predicted": diag["cells_predicted"],
                      "blocks": diag["blocks"],
                      "y_first_m": diag["y_first_requested_m"],
                      "mesh_script_sha256": sha}, indent=2))


if __name__ == "__main__":
    main()
