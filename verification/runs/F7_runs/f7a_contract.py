#!/usr/bin/env python3
"""F7a gate — the measurement definition as an EXECUTABLE contract.

WHY THIS FILE EXISTS.  `F7a_REGATE_SPEC.md` §2 (frozen 2026-08-11, landed at
`1393b8b4`) declares itself normative: *"Everything in §2 is normative.  Two
independent agents given only §2 and the same case directory must compute the
same number."*  It was prose.  The extractor that produced the §3 verdict,
`front_metrics.py`, was written BEFORE that prose (it landed at `4aad8298`) and
implements neither the pinned rounding, nor any of the FAIL LOUD structural
assertions, nor the monotonicity guard, nor the threshold-spread trigger, nor
the wall clause, nor the station set, nor the tolerance, nor the verdict.  A
normative definition whose only home is a markdown file is a definition that
can drift from the code silently, and it had already drifted in at least four
measurable ways before anyone executed it.

This module is that definition's single executable home.  Every constant below
carries the §-clause it comes from, and `sdk/tests/test_f7a_contract.py`
asserts each one against the frozen prose in `F7a_REGATE_SPEC.md` itself, so
the two cannot diverge without a test going red.

WHAT THIS MODULE IS NOT.  It is not a re-litigation of the gate.  §2.6 forbids
revising a verdict by changing a threshold, station set, axis, mesh or reading
after the numbers are known, and nothing here does.  The contract is
transcribed at v1.0 exactly as frozen, INCLUDING one constant that this module
proves defective (see COLUMN_ROUND_DP).  Repairing it is a v1.1 with a dated
reason that re-grades every case; that is recorded, not performed here.

VERDICT VOCABULARY.  Three-valued, per §2.4 and docket B2: the extractor
answers *did the check run?* before *what did it find?*

  PASS         max|d_k| <= 5% over the six graded stations, all checks ran
  FAIL         max|d_k| >  5%, all checks ran
  UNGRADEABLE  a check could not be run, or ran and disqualified the case

and separately, `ContractViolation` is raised — never returned as a verdict —
where §2 says FAIL LOUD.  A FAIL LOUD condition means the input is not the
thing the contract describes, so no verdict of any kind is available.  The
contract never falls back to a default.

Usage:  f7a_contract.py <case_dir> [out.json]
"""
import gzip
import json
import math
import os
import re
import sys

# --------------------------------------------------------------------------
# THE CONTRACT.  Every constant is quoted to its clause in F7a_REGATE_SPEC.md.
# test_f7a_contract.py::test_constants_match_frozen_spec_text re-reads that
# file and asserts these values against the prose.  Do not edit one without
# the other; the test exists to make that impossible to do quietly.
# --------------------------------------------------------------------------

SPEC = "F7a_REGATE_SPEC.md v1.0 (frozen 2026-08-11, landed 1393b8b4)"

# §2.1 Coordinate frame and length scale.
#   "Length scale a = 0.05715 m exactly (2 1/4 in x 0.0254 m/in).
#    Reduced coordinate Z = x / a."
A = 0.05715

# §2.3 "T = t . sqrt(g/a), with g = 9.81 m/s^2 exactly and a = 0.05715 m
#       exactly.  t is the OpenFOAM time value, in seconds, unshifted."
G = 9.81

# §2.1 "Cells are grouped into columns by cell-centre x rounded to 8 decimal
#       places. ... This is why the digit count is pinned rather than left to
#       the implementer."
#
# MEASURED DEFECT IN v1.0, recorded rather than silently repaired.  8 dp is
# sufficient for the a/16 family the clause was written for (20 rows x 240
# cols = 4800 = ncells, where 9 dp gives 37 x 263 = 9731 and is what
# front_metrics.py actually executed).  It is NOT sufficient for `res8_base`,
# where 8 dp yields 211 apparent columns against 120 physical ones and 10 x
# 211 = 2110 != 1200 cells.  7 dp satisfies the assertion on every tracked
# case.  Under this contract `res8_base` therefore raises ContractViolation
# rather than returning a number — which is the correct behaviour of a
# fail-loud instrument, and is how the defect was found.  §2.5 already forbids
# any verdict at that mesh, so no verdict changes.  Re-pinning to 7 dp is a
# v1.1 change under §2.6 and is filed, not taken here.
COLUMN_ROUND_DP = 8

# §2.1 "Assertion, FAIL LOUD: the mesh is uniform in y; graded on a graded
#       mesh, the extractor refuses."
#
# The clause names no tolerance, so both the test and its tolerance are pinned
# here and justified rather than left to the implementer.
#
# The test is a LINEAR-FIT RESIDUAL, not a successive-difference spread, and
# the difference is load-bearing.  The `C` field is written in ASCII at finite
# precision: the R1 ladder carries 8 significant figures, but the older
# `damBreak_MM_a2p25in_*` cases carry 6, which near the top of a 0.113 m
# domain is 1e-6 m absolute — a third of a percent of a a/20 cell.  Testing
# successive differences measures that write noise and refuses a perfectly
# uniform mesh.  Testing each row against the fit y_j = y_0 + j.dy does not:
# write noise is bounded per point and does not accumulate, whereas a graded
# mesh's rows depart from the fit progressively and without bound.
#
# Measured on the tracked corpus: uniform meshes sit at <= 4e-4 of a cell from
# the fit; a blockMesh `simpleGrading` of 1.1 over 6 rows — the mildest grading
# anyone would call graded — sits at more than a whole cell.  0.05 of a cell
# leaves two orders of margin on both sides.
UNIFORM_Y_FIT_TOL = 0.05

# §2.2 "The front is the largest x at which h(x) crosses downward through
#       h* = 0.02 a ... h* = 0.02 a = 1.143 mm, fixed."
H_STAR = 0.02

# §2.2 "The identical extraction is repeated at h* in {0.01a, 0.02a, 0.03a,
#       0.04a}."
THRESHOLD_SWEEP = (0.01, 0.02, 0.03, 0.04)

# §2.2 "If that spread exceeds 1.0% of Z at any graded station, the verdict is
#       UNGRADEABLE, not FAIL."
SPREAD_UNGRADEABLE_FRAC = 0.010

# §2.2 "If the front reaches Z >= 14.5 at or before a graded station, that
#       station is UNGRADEABLE (wall proximity confounds it)."
Z_WALL_UNGRADEABLE = 14.5

# §2.2 "The extractor walks the written times in order and stops at the first
#       time at which Z decreases by more than 0.05."
MONOTONIC_DROP_TOL = 0.05

# §2.3 "writeInterval must satisfy dT <= 0.35 (dt_w <= 0.025 s at a = 0.05715)."
DT_STAR_MAX = 0.35

# §2.3 "the extractor reads <t>/uniform/time and asserts its value equals the
#       directory name to 1e-9.  Mismatch => FAIL LOUD."
TIME_VALUE_TOL = 1e-9

# §2.3 "controlDict must carry startFrom latestTime (or startTime with
#       startTime 0 on a cold run).  Any other value => UNGRADEABLE."
ALLOWED_START_FROM = ("latestTime", "startTime")

# §2.4 "The frozen reference table (T, Z), all eight points."
REFERENCE = ((3.90, 6.00), (4.49, 7.00), (5.17, 8.00), (5.91, 9.00),
             (6.70, 10.00), (7.72, 11.00), (8.58, 12.00), (9.53, 13.00))

# §2.4 "Graded stations: the first six, T = 3.90 ... 7.72, Z = 6 ... 11.
#       Frozen here, before the run."  The last two are "extracted and
#       reported anyway, labelled reported, not graded".
N_GRADED = 6

# §2.4 "Tolerance: 5%, applied to max|d_k| over the six graded stations.
#       The gate PASSES iff max_k |d_k| <= 0.05."
TOLERANCE = 0.05

# §2.5 "A gate verdict may be taken only on a mesh with dy <= a/128."
DY_VERDICT_FLOOR_DIV = 128

# §2.5 "A diagnostic or ladder rung may be run coarser, but no verdict is
#       taken on it below dy <= a/32."
DY_DIAGNOSTIC_FLOOR_DIV = 32

PASS, FAIL, UNGRADEABLE = "PASS", "FAIL", "UNGRADEABLE"

# THE EXIT CODE IS A FUNCTION OF THE VERDICT (V15 round 7 F6, docket D95).
#
# Until 2026-08-15 `main()` printed `VERDICT: FAIL` and returned None, so this
# module exited 0 on every case including the three that fail the re-gate:
#
#     $ f7a_contract.py F7a_R1/res32y128_base
#     ... max|d| 11.03% against a 5% tolerance
#     VERDICT: FAIL
#     $ echo $?
#     0
#
# Docket D78's criterion is that a gate is a program whose exit code is a
# function of its finding; a program that prints FAIL and exits 0 is a printer,
# and any caller that composes it -- a shell `&&`, a CI step, `lab_check.py`'s
# admission predicate -- reads it as clean. The codes match this lab's runner
# contract (`scripts/lab_check.py`: 0 PASS, 1 FAIL, 3 UNKNOWN) so that the two
# compose without a translation table. A `ContractViolation` is deliberately
# NOT in this table: it is a FAIL LOUD condition, it propagates as an uncaught
# exception, and the non-zero exit that produces is the right answer.
EXIT_BY_VERDICT = {PASS: 0, FAIL: 1, UNGRADEABLE: 3}


class ContractViolation(Exception):
    """A §2 FAIL LOUD condition.  The input is not what the contract describes,
    so no verdict of any kind — not even UNGRADEABLE — is available."""


# --------------------------------------------------------------------------
# Field reading.  Deliberately written independently of front_metrics.py so
# that agreement between the two is evidence rather than shared code.
# --------------------------------------------------------------------------

def _open(path):
    if os.path.exists(path):
        return open(path)
    if os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt")
    raise FileNotFoundError(path)


def _internal_field(path, kind):
    txt = _open(path).read()
    m = re.search(
        r"internalField\s+nonuniform\s+List<%s>\s*\n(\d+)\n\(\n(.*?)\n\)\s*;" % kind,
        txt, re.S)
    if m is None:
        m2 = re.search(r"internalField\s+uniform\s+([-\d.eE+]+)\s*;", txt)
        if m2 is not None:
            return None, float(m2.group(1))
        raise ContractViolation("cannot parse internalField in %s" % path)
    n = int(m.group(1))
    body = m.group(2).split("\n")
    if len(body) != n:
        raise ContractViolation(
            "%s declares %d entries and carries %d" % (path, n, len(body)))
    return body, None


def read_scalar(path, ncells):
    body, uniform = _internal_field(path, "scalar")
    if body is None:
        return [uniform] * ncells
    return [float(v) for v in body]


def read_vector(path):
    body, _ = _internal_field(path, "vector")
    return [tuple(float(v) for v in ln.strip().strip("()").split()) for ln in body]


def find_centres(case_dir):
    """§2.1: cell-centre field C written once by `postProcess -func
    writeCellCentres`.  Decomposed processor*/ data is never read."""
    for d in sorted(os.listdir(case_dir)):
        if d.startswith("processor"):
            continue
        p = os.path.join(case_dir, d, "C")
        if os.path.exists(p) or os.path.exists(p + ".gz"):
            return p
    raise ContractViolation("no cell-centre field C in %s" % case_dir)


# --------------------------------------------------------------------------
# §2.1 — mesh structure.  FAIL LOUD.
# --------------------------------------------------------------------------

class Mesh(object):
    def __init__(self, xs, ys, dx, dy, col_of, ncells):
        self.xs, self.ys = xs, ys
        self.dx, self.dy = dx, dy
        self.col_of = col_of      # cell index -> column index
        self.nx, self.ny = len(xs), len(ys)
        self.ncells = ncells


def build_mesh(C, dp=COLUMN_ROUND_DP):
    """§2.1 structural contract, FAIL LOUD on every clause.

      * every column contains exactly n_y cells and every row exactly n_x,
        with n_x . n_y == the internal field length;
      * the mesh is uniform in y (the quadrature below is a plain sum . dy,
        which is only the depth integral on a uniform mesh).
    """
    # Group on the pinned rounding, but take each column's/row's representative
    # coordinate as the MEAN OF THE RAW cell-centre values in it.  Rounding is
    # the grouping key only; using the rounded value as the coordinate would
    # quantise the spacing at 1e-dp and make the uniformity test below measure
    # the rounding rather than the mesh.
    gx, gy = {}, {}
    for c in C:
        gx.setdefault(round(c[0], dp), []).append(c[0])
        gy.setdefault(round(c[1], dp), []).append(c[1])
    xkeys, ykeys = sorted(gx), sorted(gy)
    xs = [sum(gx[k]) / len(gx[k]) for k in xkeys]
    ys = [sum(gy[k]) / len(gy[k]) for k in ykeys]
    nx, ny = len(xs), len(ys)
    if nx * ny != len(C):
        raise ContractViolation(
            "§2.1 structure: n_x=%d x n_y=%d = %d != %d cells at %d dp. The "
            "cell-centre coordinates do not collapse onto a structured grid at "
            "the pinned rounding, so there are no columns to integrate over."
            % (nx, ny, nx * ny, len(C), dp))
    if ny < 2:
        raise ContractViolation("§2.1: need >= 2 rows to define dy; got %d" % ny)

    xi = {k: i for i, k in enumerate(xkeys)}
    yi = {k: i for i, k in enumerate(ykeys)}
    per_col = [0] * nx
    per_row = [0] * ny
    col_of = []
    for c in C:
        i = xi[round(c[0], dp)]
        j = yi[round(c[1], dp)]
        per_col[i] += 1
        per_row[j] += 1
        col_of.append(i)
    bad = [i for i, n in enumerate(per_col) if n != ny]
    if bad:
        raise ContractViolation(
            "§2.1 structure: %d column(s) do not hold exactly n_y=%d cells "
            "(first at x=%g, holding %d)" % (len(bad), ny, xs[bad[0]], per_col[bad[0]]))
    bad = [j for j, n in enumerate(per_row) if n != nx]
    if bad:
        raise ContractViolation(
            "§2.1 structure: %d row(s) do not hold exactly n_x=%d cells" % (len(bad), nx))

    dy = (ys[-1] - ys[0]) / (ny - 1)
    resid = max(abs(ys[j] - (ys[0] + j * dy)) for j in range(ny))
    if resid > UNIFORM_Y_FIT_TOL * dy:
        raise ContractViolation(
            "§2.1 quadrature: the mesh is graded in y — rows depart from the "
            "uniform fit y_j = y_0 + j.dy by up to %.3g, which is %.3f of a "
            "cell (dy = %.6g). The depth integral is a plain sum . dy and the "
            "extractor refuses." % (resid, resid / dy, dy))
    dxs = [xs[i + 1] - xs[i] for i in range(nx - 1)]
    dx = sum(dxs) / len(dxs)
    return Mesh(xs, ys, dx, dy, col_of, len(C))


# --------------------------------------------------------------------------
# §2.1 quadrature and §2.2 front criterion.
# --------------------------------------------------------------------------

def depth_profile(alpha, mesh):
    """§2.1: h(x_i) = sum_j alpha_ij . dy over ALL n_y cells of column i, from
    y = 0 to the top of the domain, with no truncation and no free surface
    sought.  h has dimensions of length; it is NOT an interface height."""
    if len(alpha) != mesh.ncells:
        raise ContractViolation(
            "alpha has %d entries, mesh has %d cells" % (len(alpha), mesh.ncells))
    h = [0.0] * mesh.nx
    for k, a in enumerate(alpha):
        h[mesh.col_of[k]] += a * mesh.dy
    return h


def front(mesh, h, h_star_abs):
    """§2.2: the largest x at which h(x) crosses downward through h*, located
    by linear interpolation between the two adjacent column-centre x values
    that bracket the crossing.  The search scans from the far wall toward
    x = 0 and returns the first crossing it meets.  Returns Z = x/a, or None
    when no crossing exists."""
    xs = mesh.xs
    for i in range(len(xs) - 1, 0, -1):
        if h[i] < h_star_abs <= h[i - 1]:
            den = h[i] - h[i - 1]
            frac = (h_star_abs - h[i - 1]) / den if den else 0.0
            return (xs[i - 1] + frac * (xs[i] - xs[i - 1])) / A
    return None


# --------------------------------------------------------------------------
# §2.3 — time origin, write cadence, restart interaction.
# --------------------------------------------------------------------------

def written_times(case_dir):
    """Time directories carrying an alpha.water field, t > 0, sorted."""
    out = []
    for d in os.listdir(case_dir):
        try:
            t = float(d)
        except ValueError:
            continue          # `0.orig`, `constant`, `system`, logs
        ap = os.path.join(case_dir, d, "alpha.water")
        if t > 0 and (os.path.exists(ap) or os.path.exists(ap + ".gz")):
            out.append((t, d))
    out.sort()
    return out


def T_of(t):
    """§2.3: T = t . sqrt(g/a), t unshifted.  NOT re-zeroed at the first solver
    write, NOT re-zeroed at Z = 1."""
    return t * math.sqrt(G / A)


def check_time_contract(case_dir, times):
    """§2.3 clauses 1-4.  Returns a list of UNGRADEABLE reasons; raises
    ContractViolation for clause 2, which the spec marks FAIL LOUD."""
    reasons = []

    cd = os.path.join(case_dir, "system", "controlDict")
    if not os.path.exists(cd):
        reasons.append("§2.3.1: no system/controlDict")
    else:
        txt = open(cd).read()
        m = re.search(r"^\s*startFrom\s+(\w+)\s*;", txt, re.M)
        sf = m.group(1) if m else None
        if sf not in ALLOWED_START_FROM:
            reasons.append("§2.3.1: startFrom is %r" % sf)
        elif sf == "startTime":
            m0 = re.search(r"^\s*startTime\s+([-\d.eE+]+)\s*;", txt, re.M)
            if m0 is None or float(m0.group(1)) != 0.0:
                reasons.append("§2.3.1: startFrom startTime with startTime != 0")

    # clause 2 — FAIL LOUD
    for t, d in times:
        up = os.path.join(case_dir, d, "uniform", "time")
        if not os.path.exists(up):
            continue
        m = re.search(r"^\s*value\s+([-\d.eE+]+)\s*;", open(up).read(), re.M)
        if m is None:
            raise ContractViolation("§2.3.2: %s/uniform/time has no value entry" % d)
        if abs(float(m.group(1)) - t) > TIME_VALUE_TOL:
            raise ContractViolation(
                "§2.3.2: %s/uniform/time value=%s does not equal its directory "
                "name to %g" % (d, m.group(1), TIME_VALUE_TOL))

    # clause 3 — a single write interval across the whole run
    ts = [t for t, _ in times]
    if len(ts) < 2:
        reasons.append("§2.3.3: fewer than two written times")
        return reasons, None
    steps = [ts[i + 1] - ts[i] for i in range(len(ts) - 1)]
    dtw = sum(steps) / len(steps)
    if max(abs(s - dtw) for s in steps) > 1e-6 * dtw:
        reasons.append(
            "§2.3.3: written times are not a single arithmetic sequence "
            "(dt_w spans %.6g..%.6g)" % (min(steps), max(steps)))
    if abs(ts[0] - dtw) > 1e-6 * dtw:
        reasons.append("§2.3.3: first written time %g != dt_w %g" % (ts[0], dtw))

    # clause 4 — dT <= 0.35
    if T_of(dtw) > DT_STAR_MAX + 1e-9:
        reasons.append("§2.3.4: dT = %.4f exceeds %.2f" % (T_of(dtw), DT_STAR_MAX))
    return reasons, dtw


# --------------------------------------------------------------------------
# §2.2 monotonicity guard.
# --------------------------------------------------------------------------

def monotonicity_cutoff(series):
    """§2.2, FAIL LOUD in intent and not hypothetical.  A surge front does not
    retreat.  Walk the written times in order and stop at the first time at
    which Z decreases by more than MONOTONIC_DROP_TOL; that time and every
    later one are UNGRADEABLE.  Returns (kept, cut_T) where cut_T is None when
    the series never retreats.

    Without this, once the surge reaches the far wall h(x) no longer crosses
    h* downward at the toe and the furthest-crossing search silently returns a
    spurious crossing far upstream, which then gets averaged into the mean."""
    kept = []
    prev = None
    for T, Z in series:
        if Z is None:
            return kept, T
        if prev is not None and Z < prev - MONOTONIC_DROP_TOL:
            return kept, T
        kept.append((T, Z))
        prev = Z
    return kept, None


def interp_at(series, T_query):
    """§2.4: sim Z(T) linearly interpolated between the two written times
    bracketing each reference T.  A station not bracketed on both sides is
    UNGRADEABLE (returns None)."""
    for i in range(1, len(series)):
        T0, Z0 = series[i - 1]
        T1, Z1 = series[i]
        if T0 <= T_query <= T1:
            if T1 == T0:
                return Z0
            return Z0 + (T_query - T0) / (T1 - T0) * (Z1 - Z0)
    return None


# --------------------------------------------------------------------------
# The gate.
# --------------------------------------------------------------------------

def extract(case_dir, dp=COLUMN_ROUND_DP):
    """Run the §2.1-2.3 measurement.  Returns a dict of raw series."""
    C = read_vector(find_centres(case_dir))
    mesh = build_mesh(C, dp=dp)
    times = written_times(case_dir)
    if not times:
        raise ContractViolation("no written alpha.water fields in %s" % case_dir)
    time_reasons, dtw = check_time_contract(case_dir, times)

    series = {th: [] for th in THRESHOLD_SWEEP}
    for t, d in times:
        alpha = read_scalar(os.path.join(case_dir, d, "alpha.water"), mesh.ncells)
        h = depth_profile(alpha, mesh)
        for th in THRESHOLD_SWEEP:
            series[th].append((T_of(t), front(mesh, h, th * A)))
    return {"case": case_dir, "mesh": mesh, "dtw": dtw,
            "time_reasons": time_reasons, "series": series}


def grade(case_dir, dp=COLUMN_ROUND_DP):
    """Apply §2.2, §2.4 and §2.5 and return the three-valued verdict.

    Never returns a bare percentage (§2.6 / prereg §6): the verdict, the
    per-station deviations and the metric's own threshold-spread uncertainty
    travel together."""
    raw = extract(case_dir, dp=dp)
    mesh = raw["mesh"]
    reasons = list(raw["time_reasons"])

    # §2.5 resolution floor
    dy_div = A / mesh.dy
    if dy_div < DY_VERDICT_FLOOR_DIV - 1e-6:
        reasons.append(
            "§2.5: dy = a/%.1f is coarser than the a/%d verdict floor"
            % (dy_div, DY_VERDICT_FLOOR_DIV))

    # §2.2 monotonicity guard, applied per threshold
    guarded, cutoffs = {}, {}
    for th in THRESHOLD_SWEEP:
        guarded[th], cutoffs[th] = monotonicity_cutoff(raw["series"][th])

    stations = []
    for k, (T_ref, Z_ref) in enumerate(REFERENCE):
        graded = k < N_GRADED
        Zs, st_reasons = {}, []
        for th in THRESHOLD_SWEEP:
            Z = interp_at(guarded[th], T_ref)
            Zs[th] = Z
            if Z is None:
                st_reasons.append(
                    "§2.2/§2.4: no bracketed crossing at h*=%g a" % th)
        ok = [z for z in Zs.values() if z is not None]
        spread = (max(ok) - min(ok)) if len(ok) == len(THRESHOLD_SWEEP) else None
        Z_pin = Zs[H_STAR]
        # §2.2 wall clause
        if Z_pin is not None and Z_pin >= Z_WALL_UNGRADEABLE:
            st_reasons.append(
                "§2.2: front at Z=%.3f >= %.1f, wall proximity confounds it"
                % (Z_pin, Z_WALL_UNGRADEABLE))
        # §2.2 metric uncertainty
        spread_frac = (spread / Z_pin) if (spread is not None and Z_pin) else None
        if spread_frac is not None and spread_frac > SPREAD_UNGRADEABLE_FRAC:
            st_reasons.append(
                "§2.2: threshold spread %.2f%% of Z exceeds %.1f%%"
                % (spread_frac * 100, SPREAD_UNGRADEABLE_FRAC * 100))
        d = ((Z_pin - Z_ref) / Z_ref) if Z_pin is not None else None
        stations.append({
            "T_ref": T_ref, "Z_ref": Z_ref, "graded": graded,
            "Z": {("%g" % th): Zs[th] for th in THRESHOLD_SWEEP},
            "Z_pinned": Z_pin, "dev": d,
            "dev_abs_Z": (Z_pin - Z_ref) if Z_pin is not None else None,
            "spread_Z": spread, "spread_frac": spread_frac,
            "reasons": st_reasons})
        if graded:
            reasons.extend("T=%.2f: %s" % (T_ref, r) for r in st_reasons)

    graded_devs = [s["dev"] for s in stations if s["graded"] and s["dev"] is not None]
    if len(graded_devs) < N_GRADED:
        reasons.append("§2.4: only %d of %d graded stations produced a deviation"
                       % (len(graded_devs), N_GRADED))

    if reasons:
        verdict = UNGRADEABLE
    elif max(abs(d) for d in graded_devs) <= TOLERANCE:
        verdict = PASS
    else:
        verdict = FAIL

    return {
        "spec": SPEC, "case": case_dir, "verdict": verdict, "reasons": reasons,
        "column_round_dp": dp,
        "mesh": {"ncells": mesh.ncells, "nx": mesh.nx, "ny": mesh.ny,
                 "dx": mesh.dx, "dy": mesh.dy,
                 "dx_div": A / mesh.dx, "dy_div": A / mesh.dy},
        "dt_write": raw["dtw"], "dT_write": T_of(raw["dtw"]) if raw["dtw"] else None,
        "h_star": H_STAR, "tolerance": TOLERANCE,
        "monotonicity_cutoff_T": {("%g" % th): cutoffs[th] for th in THRESHOLD_SWEEP},
        "stations": stations,
        "max_abs_dev": max((abs(d) for d in graded_devs), default=None),
        "mean_dev": (sum(graded_devs) / len(graded_devs)) if graded_devs else None,
        "n_graded": len(graded_devs),
    }


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    r = grade(sys.argv[1])
    print("%s\ncase %s" % (r["spec"], r["case"]))
    m = r["mesh"]
    print("mesh %d cells  %dx%d  dx=a/%.1f dy=a/%.1f  dt_w=%.4g (dT=%.3f)"
          % (m["ncells"], m["nx"], m["ny"], m["dx_div"], m["dy_div"],
             r["dt_write"] or float("nan"), r["dT_write"] or float("nan")))
    print("\n  %-6s %6s %9s %9s %9s %9s %9s %8s %8s"
          % ("T", "Z_ref", "0.01a", "0.02a", "0.03a", "0.04a", "spread", "dev", "graded"))
    for s in r["stations"]:
        cells = ["%9.4f" % s["Z"]["%g" % th] if s["Z"]["%g" % th] is not None
                 else "%9s" % "-" for th in THRESHOLD_SWEEP]
        print("  %-6.2f %6.2f %s %9s %8s %8s%s"
              % (s["T_ref"], s["Z_ref"], " ".join(cells),
                 "%.4f" % s["spread_Z"] if s["spread_Z"] is not None else "-",
                 "%+.2f%%" % (s["dev"] * 100) if s["dev"] is not None else "-",
                 "yes" if s["graded"] else "no",
                 ("  <- " + "; ".join(s["reasons"])) if s["reasons"] else ""))
    if r["n_graded"]:
        print("\n  %d graded stations: mean %+.2f%%, max|d| %.2f%% against a %.0f%% tolerance"
              % (r["n_graded"], r["mean_dev"] * 100, r["max_abs_dev"] * 100,
                 r["tolerance"] * 100))
    print("\nVERDICT: %s" % r["verdict"])
    for reason in r["reasons"]:
        print("   - %s" % reason)
    if len(sys.argv) > 2:
        json.dump(r, open(sys.argv[2], "w"), indent=1, default=str)
    return EXIT_BY_VERDICT[r["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
