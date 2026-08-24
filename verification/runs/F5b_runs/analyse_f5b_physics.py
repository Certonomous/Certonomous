#!/usr/bin/env python3
"""F5b PHYSICS RUNG -- the reader.  STAGE 1 SKELETON: controls complete, grading absent.

Registered by ``verification/campaign/F5b_PHYSICS_PREREGISTRATION.md`` section 10 and
committed under that document's two-stage freeze (section 9), BOTH STAGES STRICTLY
BEFORE ANY COMPUTE:

  STAGE 1 (this file as committed here)
      every control of section 4 implemented end to end and demonstrably passing on
      the C-N1 fixture; the section 5 completion clauses 1-8; the window / sigma_quad
      / delta_close machinery; the RAN=/FOUND= reporting of charter section 9's
      ``ran_before_found``; an exit-2 refusal path for every control.
      ``grade_G1``, ``grade_G2``, ``grade_G3`` and ``emit_verdict`` raise
      ``NotImplementedError``.

      The point of stage 1 is that the controls can be PROVED TO WORK before the
      grading logic exists to be tuned to them.

  STAGE 2  the grading bodies, against the bands frozen in section 2 and nothing else.

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

    # the real thing (stage 2 only; refuses at stage 1)
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
# GRADING -- STAGE 2.  These raise at stage 1 BY DESIGN.
# ==========================================================================

_STAGE1_MSG = (
    "STAGE 1 SKELETON: %s is deliberately unimplemented.  The pre-registration "
    "(section 9) freezes the CONTROLS first, in their own commit, so that they are "
    "proved to work before any grading logic exists that could be tuned to them.  "
    "Stage 2 implements this against the bands frozen in section 2 and against "
    "nothing else.")


def grade_G1(*args, **kwargs):
    raise NotImplementedError(_STAGE1_MSG % "grade_G1")


def grade_G2(*args, **kwargs):
    raise NotImplementedError(_STAGE1_MSG % "grade_G2")


def grade_G3(*args, **kwargs):
    raise NotImplementedError(_STAGE1_MSG % "grade_G3")


def emit_verdict(*args, **kwargs):
    raise NotImplementedError(_STAGE1_MSG % "emit_verdict")


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


def run_grade(run_dir: str) -> int:
    _die("STAGE 1 SKELETON: grading is not implemented and this reader must not be "
         "used to grade %s.  grade_G1/grade_G2/grade_G3/emit_verdict raise "
         "NotImplementedError by design (pre-registration section 9, stage 1).  "
         "Nothing is graded, nothing is degraded, and no partial value is printed."
         % os.path.abspath(run_dir))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="F5b Physics rung reader (STAGE 1)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("controls", help="run the section 4 controls")
    c.add_argument("--fixture", default=FIXTURE_DEFAULT)
    c.add_argument("--workdir", default=None)

    sub.add_parser("selftest-completion", help="prove the section 5 clauses can fail")

    g = sub.add_parser("grade", help="grade a run (stage 2 only)")
    g.add_argument("--run", required=True)

    args = ap.parse_args(argv)
    try:
        if args.cmd == "controls":
            return run_controls(args.fixture, args.workdir)
        if args.cmd == "selftest-completion":
            return run_selftest_completion()
        if args.cmd == "grade":
            return run_grade(args.run)
    except Refusal as exc:
        _die(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
