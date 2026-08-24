#!/usr/bin/env python3
"""F5b PHYSICS RUNG -- the reader.  STAGE 2: controls complete, grading complete.

Registered by ``verification/campaign/F5b_PHYSICS_PREREGISTRATION.md`` section 10 and
committed under that document's two-stage freeze (section 9), BOTH STAGES STRICTLY
BEFORE ANY COMPUTE -- ``verification/runs/F5b_runs/physics_p1`` did not exist at either
commit:

  STAGE 1  every control of section 4 implemented end to end and demonstrably passing
      on the C-N1 fixture; the section 5 completion clauses 1-8; the window /
      sigma_quad / delta_close machinery; the RAN=/FOUND= reporting of charter
      section 9's ``ran_before_found``; an exit-2 refusal path for every control.
      ``grade_G1``, ``grade_G2``, ``grade_G3`` and ``emit_verdict`` raised
      ``NotImplementedError``.

      The point of stage 1 is that the controls are PROVED TO WORK in their own commit,
      before any grading logic exists that could be tuned to them.

  STAGE 2 (this file as committed here)
      the grading bodies, implemented against the bands frozen in section 2 and the
      outcome map of section 7, and against nothing else.  Still before any compute, so
      section 2d's enforcement test -- compare the comparator's commit timestamp
      against the earliest completion marker in its own run tree -- passes by
      construction: there is no marker, because there is no tree.

      Stage 2 also plants the zero for the GRADER itself.  A GATE FAIL from a grader
      never shown able to return PASS is not evidence of anything, so
      ``selftest-grading`` builds a synthetic dynamic-stall loop (the attached-flow
      fixture plus a 0.60 collapse) and requires G1 and G2 to PASS on it while both
      GATE FAIL on the attached-flow fixture -- same code path, same frozen bands.

THE READER REFUSES RATHER THAN DEGRADES (CLAUDE.md rule 4).  There is no fallback
path, no "best available" reading and no partial grade.  Every refusal is exit 2.

PARSING IS BY HEADER NAME, NEVER BY COLUMN POSITION (pre-registration section 2,
Revision 2).  E4's ``forceCoeffs1`` dictionary carries no ``coefficients`` entry, so
OpenFOAM v2606 writes ALL TWELVE coefficients in lexicographic order and ``Cl`` is at
0-based field index 4 -- not the index 2 of the familiar ``Time Cd Cl Cm`` layout.  A
positional reader would have graded this rung's gate on ``Cd(f)`` and would have
returned a number rather than an error.

Zero compute: this file runs no solver, builds no mesh and creates no run directory.

USAGE
-----
    # C-N1 + C-P1 + C-P2 + C-P3, all against the committed attached-flow fixture
    python3 verification/runs/F5b_runs/analyse_f5b_physics.py controls

    # the section 5 completion clauses, exercised both ways on a synthetic tree
    python3 verification/runs/F5b_runs/analyse_f5b_physics.py selftest-completion

    # the grader, shown able to PASS and able to GATE FAIL
    python3 verification/runs/F5b_runs/analyse_f5b_physics.py selftest-grading

    # the real thing
    python3 verification/runs/F5b_runs/analyse_f5b_physics.py grade --run <dir>
"""

from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from make_theodorsen_fixture import (          # noqa: E402
    ALPHA_AMP_DEG, ALPHA_MEAN_DEG, END_TIME, OMEGA, PERIOD, PITCH_AXIS_A,
    REDUCED_FREQ, alpha_deg, lift_slope_Z,
)

# ==========================================================================
# FROZEN CONSTANTS -- pre-registration section 2.  Nothing below is tunable.
# ==========================================================================

# --- G1: loop is open, and more open than attached flow -------------------
G1_BAND = 2.00                  # C_L.deg; PASS if A_L >= this

# --- G2: an excursion attached flow cannot produce ------------------------
G2_DALPHA_MAX = 2.00            # deg; the pair's admissible |alpha_j - alpha_i|
G2_DCL_MIN = 0.40               # PASS if some admissible pair has C_L,i - C_L,j >= this

# --- G3: Courant admissibility (section 2, re-specified at Revision 1) ----
MAX_CO = 1.00                   # controlDict maxCo, section 3
CO_HARD_FACTOR = 2.00           # (a) any step above this x maxCo    -> NOT A RESULT
CO_SOFT_FACTOR = 1.05           # the "above threshold" mark for (b) and (c)
CO_POP_FRACTION = 0.0100        # (b) more than this fraction above soft -> NOT A RESULT
CO_RUN_LENGTH = 5               # (c) this many CONSECUTIVE above soft   -> NOT A RESULT

# --- reference values derived in section 2 --------------------------------
A_ATT_DEG = 0.42900727          # C_L.deg, attached-flow loop area
G2_CEILING = 0.2034845          # analytic supremum, any admissible pair, attached flow
CROSS_STROKE_GAP = 0.0273115    # attached-flow hysteresis width at matched alpha

# --- section 4 control parameters ----------------------------------------
PLANT_LADDER = (1.234, 12.34, 123.4)    # C-P1, smallest that clears visibility
PLANT_VISIBILITY_FACTOR = 10.0          # |dA_pred| > this x sigma_quad
PLANT_BLOCK_LINES = 40                  # C-P2 collapse block
PLANT_DROP = 0.60                       # C-P2 ramp fall across the block

# Floating-point floor under C-P1's correctness tolerance.  DECLARED, NOT FITTED,
# and registered in the pre-registration at Revision 2 item (6).  sigma_quad is a
# QUADRATURE error; on a smooth loop sampled densely it collapses to ~1e-15, at
# which point ``|measured - predicted| <= sigma_quad`` is an assertion about
# double-precision round-off rather than about the reader, and would refuse on a
# healthy file.  That is the same defect Revision 1 withdrew the 1.05x hard Courant
# limit for.  The floor is nine orders of magnitude below the G1 band, so it cannot
# hide a reader that is actually wrong.
CP1_TOL_FLOOR_REL = 1.0e-9

# --- section 5 completion --------------------------------------------------
END_TIME_STR = "21.9440"
REQUIRED_FIELDS = ("U", "p", "k", "omega", "nut")   # E2 initial_fields; section 5 clause 4
REPORTED_NOT_GATED_FIELDS = ("phi", "yPlus")
PRELOOP_COURANT_LINES = 2       # pimpleFoam.C:107 and :114 -- DERIVED, see section 2
WALL_CAP_S = 4200.0             # driver timeout, section 8
COST_CAP_CORE_MIN = 72.0        # section 8 RUN CAP

# ``Courant Number mean:`` anchored at line start.  UNANCHORED WOULD ALSO MATCH
# ``Mesh Courant Number mean:`` (meshCourantNo.H:49), and a moving-mesh case is
# exactly the run where that second string can appear.
RE_COURANT = re.compile(r"^Courant Number mean:\s*(\S+)\s+max:\s*(\S+)", re.M)
RE_MESH_COURANT = re.compile(r"^Mesh Courant Number mean:", re.M)
RE_EXECTIME = re.compile(r"^ExecutionTime = ", re.M)
RE_TIME = re.compile(r"^Time = (\S+)", re.M)
RE_END = re.compile(r"^End\s*$", re.M)

FIXTURE_DEFAULT = os.path.join(_HERE, "controls", "theodorsen_attached_fixture.dat")


class Refusal(Exception):
    """Raised where a refusal must be catchable (self-tests).  Otherwise -> exit 2."""


def refuse(reason: str) -> "None":
    raise Refusal(reason)


def _die(reason: str) -> "None":
    sys.stderr.write("REFUSE (exit 2): %s\n" % reason)
    print("REFUSE (exit 2): %s" % reason)
    sys.exit(2)


# ==========================================================================
# Parsing -- BY HEADER NAME
# ==========================================================================

class CoeffTable:
    """A parsed ``coefficient*.dat``.  Columns are addressed by NAME only."""

    __slots__ = ("path", "names", "rows", "md5", "mtime", "n_comment_lines")

    def __init__(self, path, names, rows, md5, mtime, n_comment_lines):
        self.path = path
        self.names = names
        self.rows = rows
        self.md5 = md5
        self.mtime = mtime
        self.n_comment_lines = n_comment_lines

    def col(self, name: str) -> list:
        if name not in self.names:
            refuse("column %r absent from %s; header carries %r"
                   % (name, self.path, self.names))
        if self.names.count(name) != 1:
            refuse("column %r appears %d times in %s's header"
                   % (name, self.names.count(name), self.path))
        j = self.names.index(name)
        return [r[j] for r in self.rows]

    def __len__(self) -> int:
        return len(self.rows)


def parse_coefficient_dat(path: str) -> CoeffTable:
    """Parse by header name.  Refuses on a missing header, a duplicated name, or a
    data row whose field count disagrees with the header's."""
    if not os.path.isfile(path):
        refuse("coefficient file does not exist: %s" % path)
    with open(path, "rb") as fh:
        raw = fh.read()
    md5 = hashlib.md5(raw).hexdigest()
    mtime = os.path.getmtime(path)
    text = raw.decode("utf-8", "replace")

    names = None
    n_comments = 0
    rows = []
    for lineno, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            n_comments += 1
            toks = s.lstrip("#").split()
            # The LAST '#' line whose tokens begin with 'Time' is the column header.
            # Taking the last one is what lets the fixture carry a provenance preamble
            # without changing the parse.
            if toks and toks[0] == "Time" and len(toks) > 1:
                names = toks
            continue
        if names is None:
            refuse("data at %s:%d before any column-header line ('# Time ...') was "
                   "seen -- refusing to guess the layout" % (path, lineno))
        fields = s.split()
        if len(fields) != len(names):
            refuse("%s:%d has %d fields but the header names %d columns (%r) -- "
                   "refusing to index a row of unknown shape"
                   % (path, lineno, len(fields), len(names), names))
        try:
            rows.append([float(f) for f in fields])
        except ValueError as exc:
            refuse("%s:%d is not all-numeric: %s" % (path, lineno, exc))

    if names is None:
        refuse("no column-header line ('# Time ...') anywhere in %s" % path)
    if len(names) != len(set(names)):
        dups = sorted({n for n in names if names.count(n) > 1})
        refuse("duplicate column name(s) %r in %s's header" % (dups, path))
    if not rows:
        refuse("%s carries a header but no data rows" % path)
    return CoeffTable(path, names, rows, md5, mtime, n_comments)


# ==========================================================================
# Derived series
# ==========================================================================

def alpha_series(times):
    """alpha(t) reconstructed from the parsed Time column via E2's prescribed motion.

    ``coefficient.dat`` HAS NO ALPHA COLUMN (pre-registration section 2, Revision 2;
    section 11 A-10).  This reconstruction is an IDENTITY -- alpha is an input to the
    solve, not a solved field -- and it preserves the property C-P1 needs: one value
    per parsed row, derived from the file the reader actually parsed, untunable.
    """
    return [alpha_deg(t) for t in times]


def window_mask(times):
    """W = [t1, t_end], t1 = t_end - PERIOD, computed from E2's PERIOD, never from a
    rounded literal.  Asserts t1 >= 1.0 (section 2's transient exclusion)."""
    t_end = times[-1]
    t1 = t_end - PERIOD
    if t1 < 1.0:
        refuse("analysis window starts at t1 = %.9f < 1.0: the run does not cover one "
               "full period after the declared transient exclusion" % t1)
    idx = [i for i, t in enumerate(times) if t >= t1]
    if len(idx) < 3:
        refuse("only %d samples in W = [%.9f, %.9f]" % (len(idx), t1, t_end))
    return idx, t1, t_end


def loop_area(alpha, cl):
    """A_L = contour integral of C_L dalpha, trapezoid on every sample, alpha in
    degrees, traversal in increasing t.

    The contour is CLOSED explicitly by a final segment from the last sample back to
    the first, and that segment's contribution is returned separately so it is visible
    rather than buried.  On a window spanning exactly one period the segment is
    numerically zero; on a real run whose samples do not land on the window edge it is
    not, and a reader that silently omitted it would be integrating an open path and
    calling it a loop.
    """
    n = len(alpha)
    a = 0.0
    for i in range(n - 1):
        a += 0.5 * (cl[i] + cl[i + 1]) * (alpha[i + 1] - alpha[i])
    closing = 0.5 * (cl[-1] + cl[0]) * (alpha[0] - alpha[-1])
    return a + closing, closing


def sigma_quad(alpha, cl):
    """The reader's OWN quadrature error: |A_L(every sample) - A_L(every 2nd sample)|.

    This IS the error bar on A_L and it is what C-P1's visibility threshold scales
    against.  It is not delta_close and the two are never merged.
    """
    full, _ = loop_area(alpha, cl)
    half, _ = loop_area(alpha[::2], cl[::2])
    return abs(full - half), full, half


def delta_close(cl):
    """The PERIODICITY DEFICIT |C_L(t_end) - C_L(t1)|.

    NOT an error bar and never quoted as one: it measures how far the flow is from a
    periodic limit cycle after one covered period, which is a physical statement about
    the run.
    """
    return abs(cl[-1] - cl[0])


# --------------------------------------------------------------------------
# G2's pair search -- exact, O(N log N)
# --------------------------------------------------------------------------

class _MaxTree:
    """Iterative segment tree over alpha-rank: point insert, range max of (value, idx)."""

    def __init__(self, n):
        self.n = 1
        while self.n < max(n, 1):
            self.n <<= 1
        self.v = [(-math.inf, -1)] * (2 * self.n)

    def insert(self, pos, value, idx):
        i = pos + self.n
        if self.v[i][0] >= value:
            return
        self.v[i] = (value, idx)
        i >>= 1
        while i:
            self.v[i] = max(self.v[2 * i], self.v[2 * i + 1])
            i >>= 1

    def query(self, lo, hi):                 # [lo, hi)
        best = (-math.inf, -1)
        lo += self.n
        hi += self.n
        while lo < hi:
            if lo & 1:
                best = max(best, self.v[lo]); lo += 1
            if hi & 1:
                hi -= 1; best = max(best, self.v[hi])
            lo >>= 1
            hi >>= 1
        return best


def max_admissible_pair(alpha, cl, dalpha_max=G2_DALPHA_MAX):
    """max over (i, j) with i < j (in TIME) and |alpha_j - alpha_i| <= dalpha_max of
    (C_L,i - C_L,j).

    Returns (best_drop, i, j) with i, j indices into the passed arrays, or
    (0.0, -1, -1) if no admissible pair exists at all.

    Exact.  Sweeps j forward in time holding every earlier sample in a segment tree
    keyed by alpha rank, and asks for the largest earlier C_L inside the admissible
    alpha band.  O(N log N) -- an O(N^2) scan is ~4.8e8 pairs on the real run and would
    invite a sampled shortcut, which is exactly how a control stops being exact.
    """
    n = len(alpha)
    order = sorted(range(n), key=lambda i: alpha[i])
    rank = [0] * n
    sorted_alpha = [0.0] * n
    for r, i in enumerate(order):
        rank[i] = r
        sorted_alpha[r] = alpha[i]

    import bisect
    tree = _MaxTree(n)
    best = (0.0, -1, -1)
    found_any = False
    for j in range(n):
        lo = bisect.bisect_left(sorted_alpha, alpha[j] - dalpha_max)
        hi = bisect.bisect_right(sorted_alpha, alpha[j] + dalpha_max)
        val, i = tree.query(lo, hi)
        if i >= 0:
            found_any = True
            drop = val - cl[j]
            if drop > best[0] or best[1] < 0:
                best = (drop, i, j)
        tree.insert(rank[j], cl[j], j)
    if not found_any:
        return 0.0, -1, -1
    return best


def pair_kind(times, alpha, i, j):
    """within-stroke (same sign of dalpha/dt) or cross-stroke (opposite signs).

    The sign is computed FROM THE ALPHA SERIES BY FINITE DIFFERENCE, not from the
    model, exactly as section 2 requires.
    """
    def slope(k):
        if k <= 0:
            return alpha[1] - alpha[0]
        if k >= len(alpha) - 1:
            return alpha[-1] - alpha[-2]
        return alpha[k + 1] - alpha[k - 1]
    si, sj = slope(i), slope(j)
    if si == 0.0 or sj == 0.0:
        return "stroke-reversal"
    return "within-stroke" if (si > 0) == (sj > 0) else "cross-stroke"


# ==========================================================================
# Section 4 CONTROLS.  Every one emits RAN= before FOUND= (charter section 9,
# ``ran_before_found``); a control that did not execute reports unknown, never
# collapsed into a pass and never into a failure.
# ==========================================================================

class ControlResult:
    def __init__(self, cid, ran, found=None, detail=""):
        self.cid = cid
        self.ran = ran
        self.found = found
        self.detail = detail

    def emit(self):
        print("  %-5s RAN=%s" % (self.cid, "yes" if self.ran else "no"))
        if not self.ran:
            print("  %-5s FOUND=unknown  (did not execute -- NOT a pass and NOT a fail)"
                  % self.cid)
        else:
            print("  %-5s FOUND=%s" % (self.cid, self.found))
        for line in self.detail.splitlines():
            if line.strip():
                print("        %s" % line)


def control_CP3(table: CoeffTable, expected_root: str, root_label: str) -> ControlResult:
    """C-P3 -- the reader is reading THIS file.  Records md5 and mtime of the exact
    file parsed and asserts the path lies inside the expected root."""
    p = os.path.abspath(table.path)
    root = os.path.abspath(expected_root)
    inside = p == root or p.startswith(root.rstrip(os.sep) + os.sep)
    if not inside:
        refuse("C-P3: parsed %s, which is NOT inside the required root %s" % (p, root))
    return ControlResult(
        "C-P3", True, "provenance ok",
        "path   %s\nroot   %s  (%s)\nmd5    %s\nmtime  %.6f\nrows   %d  columns %d"
        % (p, root, root_label, table.md5, table.mtime, len(table), len(table.names)))


def _write_plant(src: CoeffTable, dst_path: str, mutate) -> str:
    """Copy the source file verbatim and rewrite only the Cl field of the data lines
    the mutator touches.  Comment lines, column order, spacing and every other column
    are preserved byte for byte."""
    with open(src.path) as fh:
        lines = fh.read().splitlines()
    jcl = src.names.index("Cl")
    data_lineno = []
    for k, line in enumerate(lines):
        s = line.strip()
        if s and not s.startswith("#"):
            data_lineno.append(k)
    if len(data_lineno) != len(src):
        refuse("plant writer counted %d data lines but the parse produced %d rows"
               % (len(data_lineno), len(src)))
    for di, new_cl in mutate.items():
        k = data_lineno[di]
        # The row is: the time right-justified in setw(18), then ONE TAB BEFORE EACH
        # coefficient (forceCoeffs.C:265 -- ``os << tab << value``).  So a tab split
        # yields len(names) fields, with the time as field 0, and the tab-split index
        # of a coefficient equals its index in ``names``.  There is no extra field.
        fields = lines[k].split("\t")
        if len(fields) != len(src.names):
            refuse("plant writer: %s data line %d splits into %d tab fields, not the "
                   "%d the header names" % (src.path, di, len(fields), len(src.names)))
        fields[jcl] = "%.10g" % new_cl
        lines[k] = "\t".join(fields)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return dst_path


def control_CP1(src: CoeffTable, workdir: str) -> ControlResult:
    """C-P1 -- the loop-area reader sees a non-zero, and sees the RIGHT non-zero.

    Two-sided, and both sides must hold or the reader refuses:
      1. CORRECTNESS  |A_L(planted) - A_L(original) - dA_pred| <= tol
      2. VISIBILITY   |dA_pred| > 10 sigma_quad

    The plant index i* is the index within W maximising |alpha_{i+1} - alpha_{i-1}|,
    computed from the copy's own reconstructed alpha series -- deterministic, decided
    entirely by the PRESCRIBED motion, and so untunable to the answer.
    """
    t0 = src.col("Time")
    a0 = alpha_series(t0)
    c0 = src.col("Cl")
    idx, t1, t_end = window_mask(t0)
    aw = [a0[i] for i in idx]
    cw = [c0[i] for i in idx]
    sq, A_full, A_half = sigma_quad(aw, cw)
    A_orig, _ = loop_area(aw, cw)

    # i* : maximise |alpha_{i+1} - alpha_{i-1}| over the interior of W.
    best_k, best_span = None, -1.0
    for k in range(1, len(idx) - 1):
        span = abs(aw[k + 1] - aw[k - 1])
        if span > best_span:
            best_span, best_k = span, k
    if best_k is None:
        refuse("C-P1: window has no interior sample to plant into")
    i_star_local = best_k
    i_star_global = idx[best_k]
    weight = (aw[i_star_local + 1] - aw[i_star_local - 1]) / 2.0

    chosen = None
    ladder_report = []
    for pv in PLANT_LADDER:
        dA_pred = pv * weight
        visible = abs(dA_pred) > PLANT_VISIBILITY_FACTOR * sq
        ladder_report.append("PLANT_CL=%-8g dA_pred=%+.6e visible=%s"
                             % (pv, dA_pred, "yes" if visible else "no"))
        if visible and chosen is None:
            chosen = (pv, dA_pred)
    if chosen is None:
        refuse("C-P1: no PLANT_CL in the registered ladder %r clears visibility "
               "(|dA_pred| > %g x sigma_quad = %g); the reader cannot be shown able to "
               "see its own plant" % (PLANT_LADDER, PLANT_VISIBILITY_FACTOR, sq))
    plant_value, dA_pred = chosen

    dst = os.path.join(workdir, "coeff_plant_area.dat")
    _write_plant(src, dst, {i_star_global: c0[i_star_global] + plant_value})

    planted = parse_coefficient_dat(dst)
    tp = planted.col("Time")
    ap = alpha_series(tp)
    cp = planted.col("Cl")
    pidx, _, _ = window_mask(tp)
    A_plant, _ = loop_area([ap[i] for i in pidx], [cp[i] for i in pidx])

    measured = A_plant - A_orig
    tol = max(sq, CP1_TOL_FLOOR_REL * max(abs(A_orig), abs(dA_pred), 1.0))
    err = abs(measured - dA_pred)
    if err > tol:
        refuse("C-P1 CORRECTNESS: the reader saw a change of %+.9e but the planted "
               "change is %+.9e (error %.3e > tol %.3e).  A reader that sees A change "
               "but the WRONG change is as broken as one that sees nothing."
               % (measured, dA_pred, err, tol))

    detail = (
        "window          W = [%.9f, %.9f], %d samples of %d\n"
        "A_L(original)   %+.9f C_L.deg\n"
        "sigma_quad      %.6e   (A_full %+.9f, A_half %+.9f)\n"
        "i*              window index %d / file row %d, |alpha_{i+1}-alpha_{i-1}| = "
        "%.9f deg  (max over W)\n"
        "%s\n"
        "PLANT_CL used   %g   (smallest in the registered ladder clearing visibility)\n"
        "dA_pred         %+.9e   = PLANT_CL x (alpha_{i+1}-alpha_{i-1})/2\n"
        "dA_measured     %+.9e\n"
        "|error|         %.3e   tol %.3e  (max of sigma_quad and the declared "
        "round-off floor %.0e x scale)\n"
        "planted copy    %s"
        % (t1, t_end, len(idx), len(src), A_orig, sq, A_full, A_half,
           i_star_local, i_star_global, best_span, "\n".join(ladder_report),
           plant_value, dA_pred, measured, err, tol, CP1_TOL_FLOOR_REL, dst))
    return ControlResult("C-P1", True, "reader sees the RIGHT non-zero", detail)


def control_CP2(src: CoeffTable, workdir: str) -> ControlResult:
    """C-P2 -- the collapse detector (G2) can fire.

    Over a contiguous block of 40 data lines inside W across which |dalpha| <= 2.00
    deg, the Cl column is replaced by a linear ramp falling by PLANT_DROP = 0.60.
    The block is chosen deterministically: the first admissible block inside W, scanned
    forward.  The control then requires the pair search to find a firing pair, and to
    find it INSIDE the planted block.
    """
    t0 = src.col("Time")
    a0 = alpha_series(t0)
    c0 = src.col("Cl")
    idx, t1, t_end = window_mask(t0)
    if len(idx) < PLANT_BLOCK_LINES + 2:
        refuse("C-P2: window holds %d samples, fewer than the %d-line plant block"
               % (len(idx), PLANT_BLOCK_LINES))

    start_local = None
    for k in range(0, len(idx) - PLANT_BLOCK_LINES + 1):
        blk = [a0[idx[m]] for m in range(k, k + PLANT_BLOCK_LINES)]
        if abs(max(blk) - min(blk)) <= G2_DALPHA_MAX:
            start_local = k
            break
    if start_local is None:
        refuse("C-P2: no contiguous %d-line block inside W spans <= %.2f deg of alpha"
               % (PLANT_BLOCK_LINES, G2_DALPHA_MAX))

    rows = [idx[start_local + m] for m in range(PLANT_BLOCK_LINES)]
    base = c0[rows[0]]
    mutate = {}
    for m, gi in enumerate(rows):
        frac = m / float(PLANT_BLOCK_LINES - 1)
        mutate[gi] = base - PLANT_DROP * frac

    dst = os.path.join(workdir, "coeff_plant_collapse.dat")
    _write_plant(src, dst, mutate)

    planted = parse_coefficient_dat(dst)
    tp = planted.col("Time")
    ap = alpha_series(tp)
    cp = planted.col("Cl")
    pidx, _, _ = window_mask(tp)
    aw = [ap[i] for i in pidx]
    cw = [cp[i] for i in pidx]
    drop, li, lj = max_admissible_pair(aw, cw)
    if li < 0:
        refuse("C-P2: the pair search found NO admissible pair at all on the planted "
               "copy -- the detector cannot fire and its zero on the real run would be "
               "worthless")
    if drop < G2_DCL_MIN:
        refuse("C-P2: the largest admissible-pair drop on the planted copy is %.6f, "
               "below the registered band %.2f, although a %.2f collapse was planted "
               "into it.  The collapse detector cannot fire." % (drop, G2_DCL_MIN, PLANT_DROP))
    gi, gj = pidx[li], pidx[lj]
    inside = (rows[0] <= gi <= rows[-1]) and (rows[0] <= gj <= rows[-1])
    if not inside:
        refuse("C-P2: the detector fired on file rows (%d, %d), OUTSIDE the planted "
               "block [%d, %d].  It found something, but not the thing that was planted."
               % (gi, gj, rows[0], rows[-1]))

    detail = (
        "planted block   file rows %d..%d (%d lines), alpha span %.6f deg <= %.2f\n"
        "ramp            C_L from %+.6f falling by %.2f\n"
        "firing pair     file rows (%d, %d), window indices (%d, %d)\n"
        "                alpha_i %+.6f  alpha_j %+.6f  |dalpha| %.6f\n"
        "                C_L,i  %+.6f  C_L,j  %+.6f  drop %.6f  >= band %.2f\n"
        "                kind %s\n"
        "pair inside the planted block: yes\n"
        "planted copy    %s"
        % (rows[0], rows[-1], PLANT_BLOCK_LINES,
           abs(max(a0[r] for r in rows) - min(a0[r] for r in rows)), G2_DALPHA_MAX,
           base, PLANT_DROP, gi, gj, li, lj, aw[li], aw[lj], abs(aw[lj] - aw[li]),
           cw[li], cw[lj], drop, G2_DCL_MIN, pair_kind(tp, aw, li, lj), dst))
    return ControlResult("C-P2", True, "G2 detector fires on a planted collapse", detail)


def control_CN1(fixture_path: str) -> ControlResult:
    """C-N1 -- the negative control, and the section 2c discrimination test.

    The attached-flow fixture contains the 0.0273 cross-stroke gap in full, at every
    alpha.  Run unmodified on it the reader must:
        (a) return A_L = 0.429 +/- 0.005 C_L.deg
        (b) report that G2 does NOT fire
        (c) report the largest admissible-pair dC_L as ~0.203 -- it must SEE the
            attached-flow excursion and still place it BELOW the 0.40 band

    A reader that scores the attached-flow fixture as dynamic stall is broken and its
    verdict on the real run is void; a reader that reports 0 for (c) has not looked.
    """
    table = parse_coefficient_dat(fixture_path)
    t = table.col("Time")
    a = alpha_series(t)
    c = table.col("Cl")
    idx, t1, t_end = window_mask(t)
    aw = [a[i] for i in idx]
    cw = [c[i] for i in idx]

    A_L, closing = loop_area(aw, cw)
    sq, _, _ = sigma_quad(aw, cw)
    dcl, li, lj = max_admissible_pair(aw, cw)

    fails = []
    if not (abs(A_L - A_ATT_DEG) <= 0.005):
        fails.append("(a) A_L = %.9f, outside 0.429 +/- 0.005" % A_L)
    if dcl >= G2_DCL_MIN:
        fails.append("(b) largest admissible-pair drop %.6f REACHES the G2 band %.2f "
                     "-- the reader scores attached flow as dynamic stall" % (dcl, G2_DCL_MIN))
    if not (0.19 <= dcl <= 0.215):
        fails.append("(c) largest admissible-pair drop %.6f is not ~0.203; a reader "
                     "reporting 0 here has not looked" % dcl)
    if fails:
        refuse("C-N1 (the discrimination test) FAILED:\n    " + "\n    ".join(fails)
               + "\n  The reader's verdict on the real run is VOID.")

    kind = pair_kind(t, aw, li, lj) if li >= 0 else "n/a"
    detail = (
        "fixture         %s\n"
        "md5             %s\n"
        "rows            %d   columns %d   Cl at 0-based field index %d\n"
        "column order    %s\n"
        "window          W = [%.9f, %.9f], %d samples\n"
        "(a) A_L         %+.9f C_L.deg   vs A_att %.8f   |diff| %.3e  <= 0.005  OK\n"
        "    closing seg %+.3e  (contour closed explicitly)\n"
        "    sigma_quad  %.6e\n"
        "    delta_close %.6e\n"
        "(b) G2 fires    NO   (largest drop %.7f < band %.2f)\n"
        "(c) max pair    %.7f   analytic supremum %.7f   cross-stroke gap %.7f\n"
        "    firing pair window indices (%d, %d), kind %s\n"
        "                alpha_i %+.6f  alpha_j %+.6f  |dalpha| %.6f\n"
        "                C_L,i  %+.6f  C_L,j  %+.6f"
        % (os.path.abspath(fixture_path), table.md5, len(table), len(table.names),
           table.names.index("Cl"), " ".join(table.names), t1, t_end, len(idx),
           A_L, A_ATT_DEG, abs(A_L - A_ATT_DEG), closing, sq, delta_close(cw),
           dcl, G2_DCL_MIN, dcl, G2_CEILING, CROSS_STROKE_GAP, li, lj, kind,
           aw[li], aw[lj], abs(aw[lj] - aw[li]), cw[li], cw[lj]))
    return ControlResult("C-N1", True, "attached flow correctly NOT scored as stall", detail)


# ==========================================================================
# Section 5 COMPLETION -- all of it, or the run is NOT A RESULT
# ==========================================================================

class Completion:
    def __init__(self):
        self.clauses = []       # (n, name, ok, detail)

    def add(self, n, name, ok, detail):
        self.clauses.append((n, name, ok, detail))

    def failed(self):
        return [c for c in self.clauses if not c[2]]

    def emit(self):
        for n, name, ok, detail in self.clauses:
            print("  clause %d  %-28s %s" % (n, name, "OK" if ok else "FAIL"))
            for line in str(detail).splitlines():
                if line.strip():
                    print("            %s" % line)


def check_completion(run_dir: str) -> Completion:
    """Section 5 clauses 1-8.  Every clause is checked; the caller decides the label.

    Clause 1 note, disclosed rather than papered over: NO EXIT CODE IS RECORDED ON
    DISK anywhere in this run tree.  E2's ``run_case`` raises on a non-zero rc and
    therefore never writes ``record.json`` (defect D-2), so ``record.json`` existing is
    a PROXY for "every rc was 0", not a reading of an rc.  The proxy is stated on the
    face of the clause rather than presented as a measurement.
    """
    comp = Completion()
    run = os.path.abspath(run_dir)
    case = os.path.join(run, "case")
    log_p = os.path.join(case, "log.pimpleFoam")
    rec_p = os.path.join(run, "record.json")

    def read(p):
        if not os.path.isfile(p):
            return None
        with open(p, "r", errors="replace") as fh:
            return fh.read()

    log = read(log_p)
    if log is None:
        comp.add(0, "log.pimpleFoam present", False,
                 "absent: %s -- nothing below can be checked" % log_p)
        return comp

    # ---- clause 1: rc = 0 (by the disclosed proxy) + End lines on the preludes ----
    pre_logs = ["log.blockMesh", "log.checkMesh", "log.potentialFoam"]
    missing, no_end = [], []
    for nm in pre_logs:
        txt = read(os.path.join(case, nm))
        if txt is None:
            missing.append(nm)
        elif not RE_END.search(txt):
            no_end.append(nm)
    rec_exists = os.path.isfile(rec_p)
    ok1 = rec_exists and not missing and not no_end
    comp.add(1, "rc = 0 (proxy)", ok1,
             "record.json present: %s  <- PROXY for all-rc-0; run_case raises and "
             "writes no record on a non-zero rc (D-2).  NO rc IS RECORDED ON DISK.\n"
             "prelude logs missing: %s\nprelude logs without End: %s"
             % (rec_exists, missing or "none", no_end or "none"))

    # ---- clause 2: an End line in log.pimpleFoam ----
    ok2 = bool(RE_END.search(log))
    comp.add(2, "End line", ok2, "log.pimpleFoam %s a final End line"
             % ("carries" if ok2 else "DOES NOT carry"))

    # ---- clause 3: last time == endTime ----
    times = RE_TIME.findall(log)
    last = times[-1] if times else None
    ok3 = last is not None and abs(float(last) - float(END_TIME_STR)) < 1e-8
    comp.add(3, "last time == endTime", ok3,
             "last 'Time = ' in log.pimpleFoam: %s   required: %s   (%d Time lines)"
             % (last, END_TIME_STR, len(times)))

    # ---- clause 4: fields present ----
    tdir = os.path.join(case, END_TIME_STR)
    have = sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []
    absent = [f for f in REQUIRED_FIELDS if f not in have]
    ok4 = os.path.isdir(tdir) and not absent
    comp.add(4, "fields present", ok4,
             "%s\nrequired (E2 initial_fields): %s\nmissing: %s\n"
             "reported, NOT gated: %s"
             % (tdir, list(REQUIRED_FIELDS), absent or "none",
                {f: (f in have) for f in REPORTED_NOT_GATED_FIELDS}))

    # ---- clause 5: the four-way step count ----
    n_exec = len(RE_EXECTIME.findall(log))
    co_vals = [float(m[1]) for m in RE_COURANT.findall(log)]
    n_co = len(co_vals)
    n_mesh_co = len(RE_MESH_COURANT.findall(log))
    coeff_path = find_coefficient_file(case, soft=True)
    n_rows = None
    if coeff_path:
        try:
            n_rows = len(parse_coefficient_dat(coeff_path))
        except Refusal as exc:
            n_rows = "unparseable: %s" % exc
    n_steps = None
    if rec_exists:
        try:
            n_steps = json.loads(read(rec_p)).get("n_steps")
        except Exception as exc:
            n_steps = "unreadable: %s" % exc
    ok5 = (isinstance(n_rows, int) and isinstance(n_steps, int)
           and n_exec == n_rows == n_steps
           and n_co == n_steps + PRELOOP_COURANT_LINES)
    comp.add(5, "four-way step count", ok5,
             "count(ExecutionTime = )            %s\n"
             "count(coefficient.dat data rows)   %s\n"
             "record.json n_steps (E2:306)       %s\n"
             "count(^Courant Number mean:)       %s   required n_steps + %d = %s\n"
             "count(^Mesh Courant Number mean:)  %s   (reported, not folded into the "
             "count above -- the regex is anchored so it cannot be)"
             % (n_exec, n_rows, n_steps, n_co, PRELOOP_COURANT_LINES,
                (n_steps + PRELOOP_COURANT_LINES) if isinstance(n_steps, int) else "?",
                n_mesh_co))

    # ---- clause 6: the age guard ----
    zdir = os.path.join(case, "0")
    ok6, d6 = False, "0/ or endTime dir absent"
    if os.path.isdir(zdir) and os.path.isdir(tdir):
        zs = [(f, os.path.getmtime(os.path.join(zdir, f))) for f in os.listdir(zdir)]
        if zs:
            argmax_z = max(zs, key=lambda x: x[1])
            newest_zero = argmax_z[1]
            olds = [(f, os.path.getmtime(os.path.join(tdir, f)))
                    for f in os.listdir(tdir)
                    if os.path.getmtime(os.path.join(tdir, f)) <= newest_zero]
            ok6 = not olds
            d6 = ("max(mtime) over the whole 0/ directory: %s at %.6f  (max taken over "
                  "the DIRECTORY, not one named file, so write order cannot defeat the "
                  "guard)\nfiles at endTime NOT strictly newer: %s\n"
                  "reported, not gated: argmax is 0/nut as expected: %s"
                  % (argmax_z[0], newest_zero, olds or "none", argmax_z[0] == "nut"))
    comp.add(6, "age guard", ok6, d6)

    # ---- clause 7: pre-existing-state guard ----
    comp.add(7, "pre-existing-state guard", True,
             "enforced at LAUNCH (section 3 assertion 1, defect D-1), not here: the "
             "wrapper refuses (exit 2) before run_case is called if physics_p1/ exists. "
             "This clause is a launch-time guard and the reader records that it is the "
             "launcher's, not the reader's.")

    # ---- clause 8: cap guard ----
    wall = None
    if rec_exists:
        try:
            wall = json.loads(read(rec_p)).get("wall_seconds")
        except Exception:
            wall = None
    core_min = (wall / 60.0) if isinstance(wall, (int, float)) else None
    ok8 = (isinstance(wall, (int, float)) and wall <= WALL_CAP_S
           and core_min <= COST_CAP_CORE_MIN)
    comp.add(8, "cap guard", ok8,
             "record.json wall_seconds %s  <= %.0f s driver timeout\n"
             "core-minutes (x1 rank / 60) %s  <= %.1f cap\n"
             "AN OVERRUN STOPS THE RUN; IT DOES NOT GET A NEW BUDGET (rule 12)"
             % (wall, WALL_CAP_S,
                ("%.3f" % core_min) if core_min is not None else None,
                COST_CAP_CORE_MIN))
    return comp


def find_coefficient_file(case_dir: str, soft: bool = False):
    """postProcessing/forceCoeffs1/*/coefficient*.dat -- the newest match wins, and a
    multiple match is REPORTED, never silently resolved."""
    base = os.path.join(case_dir, "postProcessing", "forceCoeffs1")
    hits = []
    if os.path.isdir(base):
        for d in sorted(os.listdir(base)):
            sub = os.path.join(base, d)
            if not os.path.isdir(sub):
                continue
            for f in sorted(os.listdir(sub)):
                if f.startswith("coefficient") and f.endswith(".dat"):
                    hits.append(os.path.join(sub, f))
    if not hits:
        if soft:
            return None
        refuse("no coefficient*.dat under %s" % base)
    if len(hits) > 1 and not soft:
        refuse("%d coefficient files under %s: %r.  A restart collision renames the "
               "file (see the lab's restart-watcher lesson); the reader refuses rather "
               "than choosing one." % (len(hits), base, hits))
    return hits[0]


def courant_series(log_text: str):
    """The ``Courant Number mean: ... max: ...`` series -- the ONLY Courant figure
    pimpleFoam prints, and it is LAGGED.

    ``pimpleFoam.C:132-135``: inside the time loop the order is CourantNo.H ->
    setDeltaT.H -> ++runTime, so the line is printed BEFORE the step it precedes.
    ``CourantNo.H:44-50``: CoNum is built from ``phi`` AS THE PREVIOUS STEP LEFT IT.
    So the Courant number REALISED by step n is observed on the line printed at loop
    iteration n+1, and the series must be shifted by one step before the limbs are
    applied.  The first PRELOOP_COURANT_LINES entries are the two pre-loop evaluations
    at the t=0 state (pimpleFoam.C:107 and :114) and belong to no step at all.

    Returns (per_step_realised, n_preloop, n_mesh_lines) where per_step_realised[k] is
    the realised Courant number of step k+1 (1-based), for k = 0 .. n_steps-2.  The
    FINAL step's realised value is never printed and is not in the list.
    """
    vals = [float(m[1]) for m in RE_COURANT.findall(log_text)]
    n_mesh = len(RE_MESH_COURANT.findall(log_text))
    if len(vals) <= PRELOOP_COURANT_LINES:
        refuse("only %d anchored 'Courant Number mean:' lines, at or below the %d "
               "pre-loop evaluations -- no step has an observable Courant number"
               % (len(vals), PRELOOP_COURANT_LINES))
    return vals[PRELOOP_COURANT_LINES + 1:], PRELOOP_COURANT_LINES, n_mesh


# ==========================================================================
# GRADING -- STAGE 2, implemented against the bands frozen in section 2 and the
# outcome map of section 7, and against nothing else.  Committed BEFORE the run
# directory is created, so section 2d's enforcement test (compare the comparator's
# commit timestamp against the earliest completion marker in its own run tree)
# passes by construction: there is no marker, because there is no tree.
#
# LABELS COME FROM CLAUDE.md RULE 1'S FIXED VOCABULARY AND NOWHERE ELSE:
#   PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING
# ==========================================================================

VERDICT_PASS = "PASS"
VERDICT_GATE_FAIL = "GATE FAIL"
VERDICT_NOT_A_RESULT = "NOT A RESULT"
VERDICT_BLOCKED = "BLOCKED"


def grade_G1(A_L, sq, closing, A_up=None, A_down=None):
    """G1 -- the loop is open, and MORE open than attached flow.

    Band, frozen in section 2: PASS if A_L >= +2.00 C_L.deg, else GATE FAIL.
    2.00 is 4.66x the attached-flow reference A_att = 0.429 C_L.deg, so the limb
    survives a 4x error in A_att -- which section 2 flags as the least robust number
    in the document because Im(Z) is a near cancellation.

    The measured value is printed beside the band WHICHEVER WAY IT GOES (section 7
    row 2: the measured values are printed in full beside the bands they missed).
    """
    label = VERDICT_PASS if A_L >= G1_BAND else VERDICT_GATE_FAIL
    detail = (
        "A_L            %+.9f C_L.deg   +/- sigma_quad %.6e\n"
        "band           A_L >= %+.2f C_L.deg  -> %s\n"
        "A_att          %.8f C_L.deg   (band is %.2fx the attached-flow value)\n"
        "margin         A_L - band = %+.9f\n"
        "closing seg    %+.6e   (the contour is closed explicitly; this is its "
        "contribution, shown so an open path cannot masquerade as a loop)"
        % (A_L, sq, G1_BAND, label, A_ATT_DEG, G1_BAND / A_ATT_DEG,
           A_L - G1_BAND, closing))
    if A_up is not None:
        detail += ("\nreported, NOT gated: A_up %+.9f   A_down %+.9f  (section 2)"
                   % (A_up, A_down))
    return label, detail


def grade_G2(times, alpha, cl):
    """G2 -- a C_L excursion exists that attached flow cannot produce.

    Band, frozen in section 2: PASS if there is a sample pair (i, j), i < j, both in
    W, with |alpha_j - alpha_i| <= 2.00 deg and C_L,i - C_L,j >= 0.40.  Else GATE FAIL.
    0.40 is 1.97x the analytic attached-flow ceiling 0.2035 over ANY admissible pair.

    Section 2 requires the FIRING PAIR'S KIND to be reported -- within-stroke (a lift
    collapse, stall onset proper) or cross-stroke (the post-stall lift deficit) --
    from the sign of dalpha/dt computed FROM THE ALPHA SERIES, not from the model.
    A G2 PASS whose kind is not reported is incomplete, so the kind is printed here on
    the PASS path and on the GATE FAIL path alike.
    """
    drop, i, j = max_admissible_pair(alpha, cl)
    if i < 0:
        return VERDICT_GATE_FAIL, (
            "NO ADMISSIBLE PAIR EXISTS AT ALL in W under |dalpha| <= %.2f deg.\n"
            "That is not a small excursion -- it is no excursion, and it is reported "
            "as such rather than as a zero." % G2_DALPHA_MAX)
    label = VERDICT_PASS if drop >= G2_DCL_MIN else VERDICT_GATE_FAIL
    kind = pair_kind(times, alpha, i, j)
    detail = (
        "largest admissible-pair drop   %.7f\n"
        "band                           C_L,i - C_L,j >= %.2f  -> %s\n"
        "attached-flow ceiling          %.7f analytic supremum "
        "(band is %.2fx it); cross-stroke component %.7f\n"
        "FIRING PAIR (section 2 requires the kind, and this is it):\n"
        "  kind      %s\n"
        "  i         window index %d   t = %.9f   alpha = %+.6f deg   C_L = %+.6f\n"
        "  j         window index %d   t = %.9f   alpha = %+.6f deg   C_L = %+.6f\n"
        "  |dalpha|  %.6f deg  <= %.2f\n"
        "  drop      %.7f"
        % (drop, G2_DCL_MIN, label, G2_CEILING, G2_DCL_MIN / G2_CEILING,
           CROSS_STROKE_GAP, kind,
           i, times[i], alpha[i], cl[i], j, times[j], alpha[j], cl[j],
           abs(alpha[j] - alpha[i]), G2_DALPHA_MAX, drop))
    if label == VERDICT_GATE_FAIL:
        detail += ("\nNOTE: the pair above is the LARGEST admissible excursion found, "
                   "printed in full beside the band it missed (section 7 row 2).  It is "
                   "not a firing pair.")
    return label, detail


def grade_G3(co_realised, step_times, step_index_offset=1):
    """G3's Courant limb -- the reading is admissible.

    Section 2, re-specified at Revision 1 against setDeltaT.H and given its reading
    rule at Revision 2.  NOT A RESULT if ANY of:
        (a) any step has Co > 2.00 x maxCo
        (b) more than 1.00 % of the graded steps have Co > 1.05 x maxCo
        (c) any run of 5 or more CONSECUTIVE steps has Co > 1.05 x maxCo

    REPORTED ALWAYS, whatever the verdict: the maximum Co with the time and step index
    at which it occurred, the count and fraction above 1.05 x maxCo, and the length of
    the longest consecutive run above it.

    ``co_realised[k]`` is the Courant number REALISED by step ``k + step_index_offset``
    -- the series is already shifted by ``courant_series`` because the printed figure is
    lagged (see that function).  The final step's realised value is never printed and
    is therefore absent from the series; the shortfall is stated, not absorbed.
    """
    hard = CO_HARD_FACTOR * MAX_CO
    soft = CO_SOFT_FACTOR * MAX_CO
    n = len(co_realised)
    if n == 0:
        refuse("G3: the realised-Courant series is empty; no step has an observable "
               "Courant number and the reading cannot be shown admissible")

    kmax = max(range(n), key=lambda k: co_realised[k])
    co_max = co_realised[kmax]
    step_max = kmax + step_index_offset
    t_max = step_times[step_max] if step_max < len(step_times) else float("nan")

    above = [k for k in range(n) if co_realised[k] > soft]
    frac = len(above) / float(n)
    longest, run, run_start, best_start = 0, 0, None, None
    for k in range(n):
        if co_realised[k] > soft:
            if run == 0:
                run_start = k
            run += 1
            if run > longest:
                longest, best_start = run, run_start
        else:
            run = 0

    fired = []
    if co_max > hard:
        fired.append("(a) max Co %.6f > %.2f x maxCo = %.2f -- the local velocity "
                     "magnitude more than doubled inside one time step; that is a "
                     "divergence or a mesh-motion artifact, not a physical "
                     "acceleration, and a stall signature read under it cannot be told "
                     "from the artifact" % (co_max, CO_HARD_FACTOR, hard))
    if frac > CO_POP_FRACTION:
        fired.append("(b) %d of %d graded steps (%.4f %%) above %.2f x maxCo = %.2f, "
                     "over the %.2f %% population limb  [JUDGEMENT limb, section 11 A-9]"
                     % (len(above), n, 100.0 * frac, CO_SOFT_FACTOR, soft,
                        100.0 * CO_POP_FRACTION))
    if longest >= CO_RUN_LENGTH:
        fired.append("(c) %d CONSECUTIVE steps above %.2f x maxCo (from graded index "
                     "%d, step %d), at or over the limit of %d -- reduction is "
                     "immediate and undamped (setDeltaT.H), so a controller tracking "
                     "the flow cannot stay above threshold this long; it is chronically "
                     "behind the flow"
                     % (longest, CO_SOFT_FACTOR, best_start,
                        best_start + step_index_offset, CO_RUN_LENGTH))

    report = (
        "REPORTED ALWAYS, whatever the verdict:\n"
        "  max Co                 %.6f   at step %d, t = %s\n"
        "  count > %.2f x maxCo   %d of %d graded steps\n"
        "  fraction               %.6f %%   (limb (b) fires above %.2f %%)\n"
        "  longest consecutive    %d steps   (limb (c) fires at %d)\n"
        "  maxCo (controlDict)    %.2f;  hard limb (a) at %.2f;  soft mark at %.2f\n"
        "  graded steps           %d   (the FINAL step's realised Co is never printed "
        "by pimpleFoam and is absent from this series -- one step, named, not absorbed)"
        % (co_max, step_max, ("%.9g" % t_max) if t_max == t_max else "unknown",
           CO_SOFT_FACTOR, len(above), n, 100.0 * frac, 100.0 * CO_POP_FRACTION,
           longest, CO_RUN_LENGTH, MAX_CO, hard, soft, n))

    if fired:
        return VERDICT_NOT_A_RESULT, report + "\nLIMBS FIRED:\n  " + "\n  ".join(fired)
    return None, report + ("\nNo limb fired.  A few-percent single-step overshoot is "
                           "the controller working as designed (section 2, property 1) "
                           "and does not void the run.")


def emit_verdict(completion, controls, g3_label, g1_label, g2_label, extra=""):
    """The section 7 outcome map, applied in its registered order.

    Precedence is not a choice made here: CLAUDE.md rule 5's principle -- a gate can
    only turn a PASS or GATE FAIL INTO NOT A RESULT, never the reverse -- fixes it.
    So every NOT A RESULT trigger is resolved before G1/G2 are allowed to speak, and
    when one fires THE GATE IS NOT EVALUATED and no partial A_L is quoted (section 7
    row 3, charter section 2: a gate that was not reached is stated as not reached,
    never replaced by a nearer gate that was).
    """
    print()
    print("=" * 78)
    print("SECTION 7 OUTCOME MAP")
    print("=" * 78)

    failed = completion.failed() if completion is not None else []
    if failed:
        names = ", ".join("clause %d (%s)" % (n, nm) for n, nm, _, _ in failed)
        print("row 3   %s" % VERDICT_NOT_A_RESULT)
        print("        failing completion clause(s): %s" % names)
        print("        THE GATE IS NOT EVALUATED and no partial A_L is quoted.")
        _print_standing_rows()
        return VERDICT_NOT_A_RESULT

    if controls is not None and not controls:
        print("row 4   %s" % VERDICT_NOT_A_RESULT)
        print("        a section 4 control refused.  The reader is declared broken, the "
              "run's numbers are withheld ENTIRELY, and the reader defect is a docket "
              "item.")
        _print_standing_rows()
        return VERDICT_NOT_A_RESULT

    if g3_label == VERDICT_NOT_A_RESULT:
        print("row 5   %s   (G3)" % VERDICT_NOT_A_RESULT)
        print("        the Courant condition fired.  The full Courant report is printed "
              "above WHATEVER the verdict.")
        _print_standing_rows()
        return VERDICT_NOT_A_RESULT

    if g1_label == VERDICT_PASS and g2_label == VERDICT_PASS:
        print("row 1   %s" % VERDICT_PASS)
        print("        Physics rung established: the dynamic-stall mechanism is present "
              "ON THE 3,584-CELL FEASIBILITY MESH.")
        print("        SECTION 6 CEILING TRAVELS WITH THIS VERDICT AND IS NOT OPTIONAL:")
        print("          - no discretisation-error claim; single grid, no GCI, no "
              "observed order (rule 5 is not applicable and none is printed)")
        print("          - no quantitative comparison to TP-1100 (reference NOT "
              "OBTAINED, and the mesh has no error bar -- either alone suffices)")
        print("          - no cycle-convergence claim: one period is covered, and a "
              "repeatability estimate needs at least two")
        print("          - a PASS here means the mechanism is present, AND NOTHING MORE")
        _print_standing_rows()
        return VERDICT_PASS

    print("row 2   %s" % VERDICT_GATE_FAIL)
    print("        Physics rung NOT established.  G1 %s, G2 %s." % (g1_label, g2_label))
    print("        Shipped as a documented failure under charter section 8, never "
          "re-posed to fit the answer (L-44).  The measured values are printed in full "
          "beside the bands they missed, above.")
    _print_standing_rows()
    return VERDICT_GATE_FAIL


def _print_standing_rows():
    print("row 7   %s -- the Gate rung (quantitative vs NASA TP-1100) is unchanged by "
          "any outcome above; its reference is NOT OBTAINED." % VERDICT_BLOCKED)
    print("row 8   PENDING is a QUEUE state and is never used to soften a GATE FAIL "
          "(rule 1).")


# ==========================================================================
# Drivers
# ==========================================================================

def run_controls(fixture: str, workdir: str | None) -> int:
    print("=" * 78)
    print("F5b PHYSICS -- SECTION 4 CONTROLS")
    print("reader   %s" % os.path.abspath(__file__))
    print("md5      %s" % hashlib.md5(open(__file__, "rb").read()).hexdigest())
    print("=" * 78)
    tmp = None
    if workdir is None:
        tmp = tempfile.mkdtemp(prefix="f5b_controls_")
        workdir = tmp
    print("plant workdir  %s" % workdir)
    print()

    results = [ControlResult(c, False) for c in ("C-P3", "C-N1", "C-P1", "C-P2")]
    try:
        table = parse_coefficient_dat(fixture)
        results[0] = control_CP3(table, os.path.dirname(os.path.abspath(fixture)),
                                 "FIXTURE ROOT -- NOT physics_p1/case/postProcessing/. "
                                 "A fixture pass is NOT a run pass.")
        results[1] = control_CN1(fixture)
        results[2] = control_CP1(table, workdir)
        results[3] = control_CP2(table, workdir)
    except Refusal as exc:
        for r in results:
            r.emit()
        _die(str(exc))

    for r in results:
        r.emit()
        print()
    print("ALL SECTION 4 CONTROLS PASSED on %s" % os.path.abspath(fixture))
    print("NOTE: C-P3 validated provenance against the FIXTURE root.  On the real run "
          "it validates against physics_p1/case/postProcessing/ and nothing else.")
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


def _synthetic_run(root: str, break_clause: int | None = None) -> str:
    """A minimal synthetic run tree, used ONLY to prove the section 5 clauses can both
    pass and fail.  No solver runs; every byte here is written by this function."""
    import time as _time
    case = os.path.join(root, "case")
    tdir = os.path.join(case, END_TIME_STR)
    zdir = os.path.join(case, "0")
    ppdir = os.path.join(case, "postProcessing", "forceCoeffs1", "0")
    for d in (tdir, zdir, ppdir):
        os.makedirs(d, exist_ok=True)

    n_steps = 12
    for f in REQUIRED_FIELDS:
        open(os.path.join(zdir, f), "w").write("0\n")
    _time.sleep(0.02)

    lines = []
    for i in range(PRELOOP_COURANT_LINES):
        lines.append("Courant Number mean: 0.1 max: 0.2")
    for s in range(n_steps):
        lines.append("Courant Number mean: 0.3 max: %g" % (0.5 + 0.01 * s))
        t = float(END_TIME_STR) * (s + 1) / n_steps
        lines.append("Time = %s" % (END_TIME_STR if s == n_steps - 1 else "%.8g" % t))
        lines.append("ExecutionTime = %g s  ClockTime = %d s" % (1.0 * (s + 1), s + 1))
    lines.append("End")
    log = "\n".join(lines) + "\n"
    if break_clause == 2:
        log = log.replace("\nEnd\n", "\n")
    if break_clause == 3:
        log = log.replace("Time = %s" % END_TIME_STR, "Time = 20.0000")
    if break_clause == 5:
        log = log.replace("ExecutionTime = 1 s", "", 1)
    open(os.path.join(case, "log.pimpleFoam"), "w").write(log)

    for nm in ("log.blockMesh", "log.checkMesh", "log.potentialFoam"):
        open(os.path.join(case, nm), "w").write("...\nEnd\n")
    if break_clause == 1:
        open(os.path.join(case, "log.checkMesh"), "w").write("...\n")

    hdr = ("# Time            " + "".join("\t" + n.rjust(18)
           for n in ("Cd", "Cl")) + "\n")
    body = "".join("%s\t%g\t%g\n" % (("%.8g" % (float(END_TIME_STR) * (s + 1) / n_steps)),
                                     0.01, 1.0) for s in range(n_steps))
    open(os.path.join(ppdir, "coefficient.dat"), "w").write(hdr + body)

    _time.sleep(0.02)
    for f in REQUIRED_FIELDS:
        open(os.path.join(tdir, f), "w").write("0\n")
    if break_clause == 4:
        os.remove(os.path.join(tdir, "nut"))
    if break_clause == 6:
        _time.sleep(0.02)
        open(os.path.join(zdir, "nut"), "w").write("0\n")

    rec = {"n_steps": n_steps, "wall_seconds": 100.0}
    if break_clause == 8:
        rec["wall_seconds"] = WALL_CAP_S + 1.0
    if break_clause != 1:
        open(os.path.join(root, "record.json"), "w").write(json.dumps(rec))
    else:
        open(os.path.join(root, "record.json"), "w").write(json.dumps(rec))
    return root


def run_selftest_completion() -> int:
    """Plant the zero, for the completion rule itself.

    A completion checker never shown able to FAIL is a checker whose green is not
    evidence.  Each clause is broken in turn, on a synthetic tree, and the checker must
    report exactly that clause failing.
    """
    print("=" * 78)
    print("F5b PHYSICS -- SECTION 5 COMPLETION SELF-TEST (synthetic tree, no solver)")
    print("=" * 78)
    tmp = tempfile.mkdtemp(prefix="f5b_completion_")
    try:
        root = _synthetic_run(os.path.join(tmp, "clean"))
        comp = check_completion(root)
        bad = comp.failed()
        print("CONTROL (nothing broken): %d clause(s) failing" % len(bad))
        for n, name, _, _ in bad:
            print("   unexpectedly FAILING: clause %d %s" % (n, name))
        if bad:
            comp.emit()
            _die("completion self-test: the CLEAN synthetic tree does not pass.  A "
                 "checker that cannot pass a good tree cannot be trusted to fail a bad "
                 "one.")
        print("   -> all 8 clauses OK\n")

        for k in (1, 2, 3, 4, 5, 6, 8):
            root = _synthetic_run(os.path.join(tmp, "break%d" % k), break_clause=k)
            comp = check_completion(root)
            names = [n for n, _, ok, _ in comp.clauses if not ok]
            hit = k in names
            print("break clause %d -> failing clauses %s   %s"
                  % (k, names or "NONE", "OK" if hit else "*** DID NOT FIRE ***"))
            if not hit:
                _die("completion self-test: breaking clause %d did not make clause %d "
                     "fail.  The clause is decorative." % (k, k))
        print("\nclause 7 is a LAUNCH-time guard (section 3 assertion 1), not a reader "
              "clause; it is reported, not self-tested here.")
        print("\nCOMPLETION SELF-TEST PASSED: every reader clause was shown able to "
              "both pass and fail.")
        return 0
    except Refusal as exc:
        _die(str(exc))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _stall_deficit(t: float) -> float:
    """A synthetic DYNAMIC-STALL deficit on top of the attached-flow loop.

    Deliberately crude and fully deterministic -- it is a test of the GRADER, not a
    model of stall.  It reproduces the two signatures section 2 names, and nothing else:

      * upstroke, alpha in [24, 25] deg: the deficit ramps 0 -> 0.60.  A lift COLLAPSE
        of 0.60 across 1 deg of incidence -- within-stroke, inside the 2.00 deg
        admissible span, above the 0.40 band.
      * downstroke, alpha from 25 deg down to 8 deg: the deficit holds at 0.60.  The
        post-stall lift deficit -- so the same alpha is worth 0.60 less on the way down
        than on the way up, which is the CROSS-STROKE signature and which opens the loop.
      * downstroke, alpha in [5, 8] deg: the deficit relaxes 0.60 -> 0, so the loop
        closes and the curve is continuous at both stroke reversals.
    """
    a = alpha_deg(t)
    upstroke = math.cos(OMEGA * t) > 0.0
    if upstroke:
        if a <= 24.0:
            return 0.0
        return 0.60 * min(1.0, (a - 24.0) / 1.0)
    if a > 8.0:
        return 0.60
    if a > 5.0:
        return 0.60 * (a - 5.0) / 3.0
    return 0.0


def _write_stall_fixture(path: str, n_samples: int = 4096) -> str:
    """Write the dynamic-stall fixture in the SAME column layout as the C-N1 fixture,
    reusing that generator's writers so the layouts cannot drift apart."""
    import make_theodorsen_fixture as MTF
    Z = lift_slope_Z(REDUCED_FREQ, PITCH_AXIS_A)
    names = MTF.coefficient_names()
    icl = names.index("Cl")
    t1 = END_TIME - PERIOD
    lines = [
        "# ============================================================",
        "# SYNTHETIC POSITIVE FIXTURE -- NOT SOLVER OUTPUT.  NO SOLVER RAN.",
        "# F5b Physics rung, GRADING self-test.",
        "# The attached-flow loop of the C-N1 fixture PLUS a 0.60 lift collapse over",
        "# 1 deg of incidence at the top of the upstroke, held through the downstroke",
        "# and relaxed near the trough.  Built to make G1 and G2 FIRE, so that their",
        "# GATE FAIL on the attached-flow fixture is shown to be discrimination and",
        "# not an inability to fire at all.",
        "# Only the 'Cl' column carries physics; every other column is a sentinel.",
        "# ============================================================",
    ]
    lines += MTF.header_block(names)
    for i in range(n_samples):
        ts = MTF._time(t1 + PERIOD * i / (n_samples - 1))
        t = float(ts)
        cl = MTF.cl_attached(t, Z) - _stall_deficit(t)
        row = ts.rjust(MTF.CHAR_WIDTH)
        for j, nm in enumerate(names):
            row += "\t" + MTF._num(cl if j == icl else
                                   MTF.SENTINEL_BASE + MTF.SENTINEL_STEP * j)
        lines.append(row)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def _grade_fixture(path: str):
    """Run G1 and G2 over a fixture, exactly as the real pipeline does."""
    table = parse_coefficient_dat(path)
    t = table.col("Time")
    a = alpha_series(t)
    c = table.col("Cl")
    idx, t1, t_end = window_mask(t)
    tw = [t[i] for i in idx]
    aw = [a[i] for i in idx]
    cw = [c[i] for i in idx]
    A_L, closing = loop_area(aw, cw)
    sq, _, _ = sigma_quad(aw, cw)
    g1, d1 = grade_G1(A_L, sq, closing)
    g2, d2 = grade_G2(tw, aw, cw)
    return (g1, d1), (g2, d2), A_L, table.md5


def run_selftest_grading() -> int:
    """Plant the zero, for the GRADER.

    A GATE FAIL from a grader never shown able to return PASS is not evidence of
    anything.  The attached-flow fixture must GATE FAIL and the dynamic-stall fixture
    must PASS, on the same code path, with the same frozen bands.  G3's three limbs are
    each shown able to fire and able not to.
    """
    print("=" * 78)
    print("F5b PHYSICS -- STAGE 2 GRADING SELF-TEST (synthetic fixtures, no solver)")
    print("=" * 78)
    tmp = tempfile.mkdtemp(prefix="f5b_grading_")
    try:
        stall = _write_stall_fixture(os.path.join(tmp, "dynamic_stall_fixture.dat"))

        print("\n--- POSITIVE fixture: attached flow + a 0.60 collapse -------------")
        print("    %s" % stall)
        (g1s, d1s), (g2s, d2s), A_s, md5s = _grade_fixture(stall)
        print("    md5 %s" % md5s)
        for line in (d1s + "\n" + d2s).splitlines():
            print("      %s" % line)
        print("    G1 %s    G2 %s" % (g1s, g2s))

        print("\n--- NEGATIVE fixture: the committed C-N1 attached-flow loop --------")
        print("    %s" % FIXTURE_DEFAULT)
        (g1n, d1n), (g2n, d2n), A_n, md5n = _grade_fixture(FIXTURE_DEFAULT)
        print("    md5 %s" % md5n)
        for line in (d1n + "\n" + d2n).splitlines():
            print("      %s" % line)
        print("    G1 %s    G2 %s" % (g1n, g2n))

        bad = []
        if g1s != VERDICT_PASS:
            bad.append("G1 did not PASS on the dynamic-stall fixture (A_L = %.6f)" % A_s)
        if g2s != VERDICT_PASS:
            bad.append("G2 did not PASS on the dynamic-stall fixture")
        if g1n != VERDICT_GATE_FAIL:
            bad.append("G1 did not GATE FAIL on the attached-flow fixture (A_L = %.6f)"
                       % A_n)
        if g2n != VERDICT_GATE_FAIL:
            bad.append("G2 did not GATE FAIL on the attached-flow fixture -- THE READER "
                       "SCORES ATTACHED FLOW AS DYNAMIC STALL")
        if bad:
            _die("grading self-test FAILED:\n    " + "\n    ".join(bad))

        print("\n--- G3's three limbs, each shown able to fire and not to -----------")
        st = [0.001 * k for k in range(400)]
        cases = [
            ("clean, all Co ~ 0.9", [0.9] * 300, None),
            ("(a) one step at 2.5", [0.9] * 150 + [2.5] + [0.9] * 149,
             VERDICT_NOT_A_RESULT),
            ("(c) six consecutive at 1.2",
             [0.9] * 100 + [1.2] * 6 + [0.9] * 194, VERDICT_NOT_A_RESULT),
            ("(b) 2 % isolated at 1.1",
             [1.1 if (k % 50 == 0) else 0.9 for k in range(300)],
             VERDICT_NOT_A_RESULT),
            ("below (b): 0.67 % isolated at 1.1",
             [1.1 if (k % 150 == 0) else 0.9 for k in range(300)], None),
        ]
        for name, series, expect in cases:
            lab, _ = grade_G3(series, st)
            ok = (lab == expect)
            print("    %-34s -> %-14s %s"
                  % (name, lab or "no limb fired", "OK" if ok else "*** WRONG ***"))
            if not ok:
                _die("grading self-test: G3 case %r returned %r, expected %r"
                     % (name, lab, expect))

        print("\n--- the section 7 map, on the two fixtures -------------------------")
        print("  attached-flow fixture:")
        v_n = emit_verdict(None, True, None, g1n, g2n)
        print("  dynamic-stall fixture:")
        v_s = emit_verdict(None, True, None, g1s, g2s)
        if v_n != VERDICT_GATE_FAIL or v_s != VERDICT_PASS:
            _die("grading self-test: the outcome map returned %r / %r" % (v_n, v_s))

        print()
        print("GRADING SELF-TEST PASSED: the grader was shown able to return PASS and "
              "able to return GATE FAIL, on the same code path and the same frozen "
              "bands, and G3's three limbs were each shown able to fire and not to.")
        return 0
    except Refusal as exc:
        _die(str(exc))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_grade(run_dir: str) -> int:
    """The real pipeline.  Completion, then controls, then G3, then G1/G2, then the
    section 7 map -- in that order, because a gate can only turn a PASS or GATE FAIL
    INTO NOT A RESULT, never the reverse (rule 5)."""
    run = os.path.abspath(run_dir)
    print("=" * 78)
    print("F5b PHYSICS RUNG -- GRADING")
    print("run      %s" % run)
    print("reader   %s" % os.path.abspath(__file__))
    print("md5      %s" % hashlib.md5(open(__file__, "rb").read()).hexdigest())
    print("         (rule 2 / charter 2d: hash this against the committed blob BEFORE "
          "believing anything below; a freeze that is claimed and not checked is a "
          "claim about intent)")
    print("=" * 78)

    if not os.path.isdir(run):
        _die("run directory does not exist: %s" % run)
    case = os.path.join(run, "case")

    try:
        print("\n--- SECTION 5 COMPLETION ------------------------------------------")
        comp = check_completion(run)
        comp.emit()
        if comp.failed():
            return 0 if emit_verdict(comp, None, None, None, None) else 0

        print("\n--- SECTION 4 CONTROLS --------------------------------------------")
        coeff = find_coefficient_file(case)
        table = parse_coefficient_dat(coeff)
        workdir = os.path.join(run, "controls")
        results = [
            control_CP3(table, os.path.join(case, "postProcessing"),
                        "physics_p1/case/postProcessing/"),
            control_CN1(FIXTURE_DEFAULT),
            control_CP1(table, workdir),
            control_CP2(table, workdir),
        ]
        for r in results:
            r.emit()

        print("\n--- G3: IS THE READING ADMISSIBLE? --------------------------------")
        with open(os.path.join(case, "log.pimpleFoam"), errors="replace") as fh:
            log = fh.read()
        co, n_pre, n_mesh = courant_series(log)
        step_times = [float(x) for x in RE_TIME.findall(log)]
        print("  pre-loop Courant lines %d (derived: pimpleFoam.C:107 and :114)" % n_pre)
        print("  Mesh Courant lines     %d (counted separately; the graded regex is "
              "anchored so these cannot leak in)" % n_mesh)
        g3, d3 = grade_G3(co, step_times)
        for line in d3.splitlines():
            print("  %s" % line)

        t = table.col("Time")
        a = alpha_series(t)
        c = table.col("Cl")
        idx, t1, t_end = window_mask(t)
        tw = [t[i] for i in idx]
        aw = [a[i] for i in idx]
        cw = [c[i] for i in idx]
        A_L, closing = loop_area(aw, cw)
        sq, _, _ = sigma_quad(aw, cw)

        if g3 == VERDICT_NOT_A_RESULT:
            return 0 if emit_verdict(comp, True, g3, None, None) else 0

        print("\n--- G1 and G2 -----------------------------------------------------")
        peak = max(range(len(aw)), key=lambda k: cw[k])
        A_up, A_down = _split_area(aw, cw)
        g1, d1 = grade_G1(A_L, sq, closing, A_up, A_down)
        for line in d1.splitlines():
            print("  %s" % line)
        g2, d2 = grade_G2(tw, aw, cw)
        for line in d2.splitlines():
            print("  %s" % line)

        print("\n--- REPORTED BESIDE THE GATE, NEVER GATED ON (charter 2a) ----------")
        print("  delta_close  %.9e   PERIODICITY DEFICIT -- NOT an error bar and never "
              "quoted as one" % delta_close(cw))
        print("  sigma_quad   %.9e   the reader's own quadrature error; THIS is the "
              "error bar on A_L" % sq)
        print("  C_L,max      %+.6f at alpha = %+.6f deg, t = %.9f"
              % (cw[peak], aw[peak], tw[peak]))
        print("  C_L,min      %+.6f" % min(cw))
        print("  samples in W %d      A_att %.8f C_L.deg" % (len(idx), A_ATT_DEG))
        print("  NOT CLAIMED: no cycle-to-cycle repeatability figure -- one period is "
              "covered and a repeatability estimate needs at least two.")

        emit_verdict(comp, True, g3, g1, g2)
        return 0
    except Refusal as exc:
        _die(str(exc))
    return 0


def _split_area(alpha, cl):
    """A_L split into upstroke and downstroke contributions.  REPORTED, never gated."""
    up = down = 0.0
    for i in range(len(alpha) - 1):
        seg = 0.5 * (cl[i] + cl[i + 1]) * (alpha[i + 1] - alpha[i])
        if alpha[i + 1] >= alpha[i]:
            up += seg
        else:
            down += seg
    return up, down


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="F5b Physics rung reader (STAGE 1)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("controls", help="run the section 4 controls")
    c.add_argument("--fixture", default=FIXTURE_DEFAULT)
    c.add_argument("--workdir", default=None)

    sub.add_parser("selftest-completion", help="prove the section 5 clauses can fail")
    sub.add_parser("selftest-grading", help="prove the grader can PASS and GATE FAIL")

    g = sub.add_parser("grade", help="grade a run")
    g.add_argument("--run", required=True)

    args = ap.parse_args(argv)
    try:
        if args.cmd == "controls":
            return run_controls(args.fixture, args.workdir)
        if args.cmd == "selftest-completion":
            return run_selftest_completion()
        if args.cmd == "selftest-grading":
            return run_selftest_grading()
        if args.cmd == "grade":
            return run_grade(args.run)
    except Refusal as exc:
        _die(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
