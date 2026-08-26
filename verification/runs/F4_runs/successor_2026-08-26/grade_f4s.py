#!/usr/bin/env python3
"""F4 SUCCESSOR -- the frozen grading path.

Registered by verification/campaign/F4S_SHOCK_LOCUS_PREREGISTRATION.md and
fixed at that document's commit (CLAUDE.md rule 2).  Nothing here may change
after the first solver of this campaign starts.

WHAT THIS FILE IS FOR, IN ONE PARAGRAPH.  Its predecessor located the bow shock
by argmax of |d(rho)/ds| over a 400-point sample line.  argmax over a fixed
point set is a DISCRETE-VALUED functional of the data: it can only move in whole
sample intervals, so it cannot vary continuously with the mesh, and a Roache
triple built on it grades the detector's jumps rather than the flow.  This file
registers a CONTINUOUS, SUB-CELL locus -- the linear-interpolated crossing of a
Rankine-Hugoniot mid-density threshold fixed from theory -- and grades the
predecessor's argmax locus BESIDE it as a full gate, so the detector hypothesis
is answered by a registered verdict rather than by an annotation.

RULE 5 IS REACHED THROUGH roache_triple.grade_ladder AND THROUGH NOTHING ELSE.
This file does not reimplement a triple.  It calls grade_ladder() and supplies
iterative_states and plateau_states, or it refuses.
"""
import sys

# ---------------------------------------------------------------------------
# HARD REFUSAL AT ENTRY, BEFORE ANYTHING ELSE RUNS.
# grade_ladder reaches its rule-1 and rule-5 gate through four `assert`
# statements in the SHARED instrument scripts/roache_triple.py (:195, :632,
# :634, :637).  That instrument is referred to verification and is not this
# lane's to edit.  `python3 -O` deletes those statements and the gate silently
# stops being a gate.  The exposure is made irrelevant at the boundary this
# document owns: under -O this file grades nothing at all.
# ---------------------------------------------------------------------------
if not __debug__:
    sys.stderr.write(
        "REFUSE (exit 2): grade_f4s.py will not run under `python -O`.\n"
        "rule 1 and rule 5 are enforced inside roache_triple.grade_ladder by\n"
        "assert statements that -O removes.  Refusing at entry.\n")
    sys.exit(2)

import argparse
import ast
import json
import math
import os
import re
import shutil
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "scripts"))

import roache_triple as RT                                  # noqa: E402
from roache_triple import (grade_ladder, external_plant_control,  # noqa: E402
                           Refusal, refuse)

EXIT_OK, EXIT_REFUSE = 0, 2

# ---------------------------------------------------------------------------
# REGISTERED CONSTANTS.  Every one of these is fixed by the pre-registration.
# ---------------------------------------------------------------------------
MACHS = (6.0, 7.0, 8.0)
LEVELS = ("coarse", "medium", "fine")
CELLS = {"coarse": 1000, "medium": 4000, "fine": 16000}
NRES = {"coarse": (50, 20), "medium": (100, 40), "fine": (200, 80)}

R_BODY = 1.0
R_TOP_OVER_R = 1.7
L_RAD = 0.7                     # (R_top - R) -- the sample line's whole span
RADIAL_GRADING = 8.0
NPOINTS = 400                   # sample points per line, UNCHANGED from F4
DS = L_RAD / (NPOINTS - 1)      # 0.0017543859649122805

GAMMA = 1.4
RHO_INF = 1.4                   # = gamma * p_inf / T_inf with p_inf = T_inf = 1
P_INF = 1.0
T_INF = 1.0

ENDTIME = 6.0
NWRITES = 16
WRITE_INTERVAL = ENDTIME / NWRITES              # 0.375
N_WINDOW = 8                    # the sustained window: the last 8 of 16 writes
MIN_WINDOW = 8                  # REFUSAL below this.  Class C element 4.
RUNAWAY_T = ENDTIME * 1.001
PER_CASE_WALL_GUARD_S = 1200.0

DIM = 2
FS = RT.FS
FORM = "equal"
SIM_H1_TOL = 0.05               # near-wall first-cell refinement, +/- 5 % of 2

GATE_STATION = "r0"             # theta = 0, the stagnation line
NEG_STATION = "r3"              # theta ~ 36 deg -- the negative control's target
XY_SUFFIX = "_T_p_rho.xy"

PLANT = RT.PLANT                # 1.234e-03
SHIFTS = (7, -11)               # localisation plants, in whole sample intervals


# ---------------------------------------------------------------------------
# THE FORBIDDEN-DELETE GUARD.  shutil.rmtree is forbidden outright on a case
# directory in cfd's territory.  The only tree this file may remove is one it
# created itself under the system temp directory.
# ---------------------------------------------------------------------------
def rmtree_tmp_only(path):
    real = os.path.realpath(path)
    tmproot = os.path.realpath(tempfile.gettempdir())
    if not real.startswith(tmproot + os.sep):
        refuse(f"refusing to delete {real!r}: this file removes nothing "
               "outside the system temp directory, and never a case directory")
    shutil.rmtree(real)


# ---------------------------------------------------------------------------
# THE ZERO-ASSERT SELF-CHECK, BY AST PARSE AND NOT BY grep.
# L-332: no `assert` in this file may carry a refusal, guard, control or gate.
# The check is that there is no ast.Assert node at all, anywhere.
# ---------------------------------------------------------------------------
def assert_node_count(path):
    with open(path) as fh:
        tree = ast.parse(fh.read(), filename=path)
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))


def no_assert_selfcheck(path=None):
    path = path or os.path.abspath(__file__)
    n = assert_node_count(path)
    if n != 0:
        refuse(f"{path}: {n} ast.Assert node(s) present; no refusal, guard, "
               "control or gate in this file may be carried by `assert` "
               "(L-332), and -O would delete every one of them")
    return n


# ---------------------------------------------------------------------------
# REFERENCE VALUES, from theory only.  No CFD value is an input to any of them.
# ---------------------------------------------------------------------------
def billig(M):
    """delta/R = 0.386 exp(4.67/M^2).  Anderson 2nd ed. eq. 5.36, after
    Billig, J. Spacecraft and Rockets 4(6) 1967 pp.822-823."""
    return 0.386 * math.exp(4.67 / (M * M))


def rho_ratio_normal_shock(M):
    """rho2/rho1 across a normal shock, gamma = 1.4."""
    return ((GAMMA + 1.0) * M * M) / ((GAMMA - 1.0) * M * M + 2.0)


def rho_threshold(M):
    """THE REGISTERED DETECTOR THRESHOLD.

    The mid-density of the Rankine-Hugoniot jump, in the solver's own
    non-dimensional units: rho* = rho_inf * (1 + rho2/rho1) / 2.

    Every input is theory: gamma, the free-stream Mach number, and the
    free-stream density implied by the registered initial conditions
    (0/p = uniform 1, 0/T = uniform 1, rho = gamma p / T = 1.4).  NO VALUE FROM
    ANY SOLVE ENTERS THIS NUMBER.
    """
    return RHO_INF * (1.0 + rho_ratio_normal_shock(M)) / 2.0


def cp_max(M):
    """Exact Rayleigh-Pitot stagnation Cp.  Reported only; no gate uses it."""
    p02p1 = (((GAMMA + 1.0) * M * M / 2.0) ** (GAMMA / (GAMMA - 1.0))
             * ((GAMMA + 1.0) / (2.0 * GAMMA * M * M - (GAMMA - 1.0)))
             ** (1.0 / (GAMMA - 1.0)))
    return (p02p1 - 1.0) / (0.5 * GAMMA * M * M)


# ---------------------------------------------------------------------------
# THE BAND, DERIVED FROM MESH GEOMETRY AND FROM NOTHING MEASURED.
# ---------------------------------------------------------------------------
def cell_at_distance(nR, d):
    """Height of the simpleGrading cell that CONTAINS radial distance d.

    Closed form from the WRITTEN blockMeshDict (MESH_STANDARD.md 9.2 -- the
    requested value is the thing that lied): span L_RAD, expansion RADIAL_GRADING
    over nR cells, ratio per cell k = E^(1/(nR-1)), first cell
    h1 = L(k-1)/(k^nR - 1), cell i height h1 k^i.
    """
    k = RADIAL_GRADING ** (1.0 / (nR - 1))
    h1 = L_RAD * (k - 1.0) / (k ** nR - 1.0)
    s = 0.0
    for i in range(nR):
        h = h1 * (k ** i)
        if s + h >= d:
            return h, i, h1
        s += h
    refuse(f"distance {d} lies outside the radial span {L_RAD}")


def band_abs(M, level):
    """delta_Billig +/- ONE local radial cell height at the shock, in delta/R.

    THE PRINCIPLE, AND IT IS NOT THE PREDECESSOR'S.  F4 banded an ARGMAX locus
    at +/- one cell because argmax is quantised: two shock positions inside one
    cell produce the same detected index.  This file's locus is CONTINUOUS and
    resolves inside a cell, so that argument does not carry over and is not
    reused.  The band here is the SMEARING scale: a shock-capturing scheme
    spreads a normal shock over O(1) cells, and when that captured profile is
    asymmetric the mid-density crossing is displaced from the true discontinuity
    by up to about the local cell height.  One local cell is therefore a
    conservative upper bound on the instrument's systematic displacement.

    Inputs: the Billig reference and the written mesh.  No CFD value.
    """
    dR, _, _ = cell_at_distance(NRES[level][1], billig(M))
    d = billig(M)
    return (d - dR, d + dR), dR


# ---------------------------------------------------------------------------
# THE READER.  One parser, used by the gates and by every control.
# ---------------------------------------------------------------------------
def read_xy(path):
    """Parse an OpenFOAM `setFormat raw` set file: distance, T, p, rho.

    Column order is REFUSED rather than assumed: OpenFOAM names the file after
    the fields in the order it wrote them, and this reader will not touch a file
    whose basename does not end `_T_p_rho.xy`.  That closes the positional-read
    trap (a column-sorted writer read by index).
    """
    base = os.path.basename(path)
    if not base.endswith(XY_SUFFIX):
        refuse(f"{path}: basename does not end {XY_SUFFIX!r}; this reader takes "
               "the column order from the filename the writer chose and will "
               "not read a file it cannot name")
    dist, T, p, rho = [], [], [], []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            f = line.split()
            if len(f) != 4:
                refuse(f"{path}: {len(f)} columns, expected 4")
            dist.append(float(f[0])); T.append(float(f[1]))
            p.append(float(f[2])); rho.append(float(f[3]))
    if len(dist) != NPOINTS:
        refuse(f"{path}: {len(dist)} sample points, registered {NPOINTS}")
    for i in range(1, len(dist)):
        if not dist[i] > dist[i - 1]:
            refuse(f"{path}: distance column is not strictly increasing at {i}")
    return dist, T, p, rho


def write_xy(path, dist, T, p, rho):
    """Re-emit a set file at FULL precision.  Controls plant into a copy written
    by this function, so the distance column is bit-identical to the parsed one
    and a planted displacement is exact rather than tolerance-bounded."""
    with open(path, "w") as fh:
        for i in range(len(dist)):
            fh.write(f"{dist[i]!r} \t{T[i]!r} \t{p[i]!r} \t{rho[i]!r}\n")


def locate_crossing(path, M):
    """THE PRIMARY DETECTOR.  Sub-cell, continuous, single-valued.

    Returns (i, w, s, n_crossings) where i is the lower bracketing index, w the
    linear interpolation weight in [0,1), s = dist[i] + w (dist[i+1] - dist[i]).

    The ENDPOINT GUARD IS APPLIED BY THE CALLER, not here, so a control may plant
    at an endpoint and observe that the reader really does return it.
    """
    dist, _T, _p, rho = read_xy(path)
    thr = rho_threshold(M)
    idx = [i for i in range(NPOINTS - 1)
           if (rho[i] - thr) > 0.0 >= (rho[i + 1] - thr)]
    if not idx:
        refuse(f"{path}: no crossing of rho* = {thr!r}; the profile spans "
               f"[{rho[-1]!r}, {rho[0]!r}] and does not bracket the threshold. "
               "A bow shock outside the sampled span is a REFUSAL, not a value")
    i = idx[0]
    w = (rho[i] - thr) / (rho[i] - rho[i + 1])
    s = dist[i] + w * (dist[i + 1] - dist[i])
    return i, w, s, len(idx)


def locate_argmax(path):
    """THE PREDECESSOR'S DETECTOR, kept verbatim in semantics so that G-F4S-1B
    grades the same instrument F4 graded.  Peak |d(rho)/ds| by central
    differences, argmax over the 400 sample points.  DISCRETE-VALUED.

    The endpoint guard is applied by the caller, for the same reason as above.
    """
    dist, _T, _p, rho = read_xy(path)
    n = len(dist)
    grad = [0.0] * n
    grad[0] = (rho[1] - rho[0]) / (dist[1] - dist[0])
    grad[n - 1] = (rho[n - 1] - rho[n - 2]) / (dist[n - 1] - dist[n - 2])
    for i in range(1, n - 1):
        grad[i] = (rho[i + 1] - rho[i - 1]) / (dist[i + 1] - dist[i - 1])
    i = max(range(n), key=lambda j: abs(grad[j]))
    return i, dist[i]


def endpoint_censored(i, n_edge=1):
    """np.argmax and a bracket search both return an index in [0, NPOINTS-1].
    A locus at either end of that range is the INSTRUMENT'S RANGE LIMIT and is
    not a measurement.  F4's own census found station r5 pinned at index 399 in
    27 of 27 reads.  Refused, at both detectors."""
    return i <= (n_edge - 1) or i >= (NPOINTS - 1 - n_edge)


def preshock_undisturbed(path):
    """The far end of the sample line must still be free stream, or the domain
    is too small and the standoff is measured against a disturbed reference."""
    _dist, _T, _p, rho = read_xy(path)
    return abs(rho[-1] - RHO_INF) / RHO_INF


# ---------------------------------------------------------------------------
# CLASS C -- TEMPORAL CONVERGENCE OF THE LOCUS.  Four elements, all four
# registered, and element 4 (the sample-count refusal) is the one that always
# makes a run gradeable when it is quietly dropped, so it refuses hardest.
# ---------------------------------------------------------------------------
def class_c(times, values, dr):
    """times ascending, values the located locus at each; dr the local radial
    cell height at the shock for THIS mesh -- the floor is mesh-derived and no
    measured deviation enters it.

    element 1  sustained window : peak-to-peak spread over the whole window
                                  <= dr.  Evaluated over N_WINDOW consecutive
                                  snapshots, never at one instant.
    element 2  trend fit        : |OLS slope| * window duration <= dr, AND the
                                  absolute increments must not be strictly
                                  growing (a growing series is rejected even
                                  when its net slope is small).
    element 3  stationarity     : |mean(second half) - mean(first half)|
                                  <= dr/2, and it CAN report NOT STATIONARY.
    element 4  sample count     : fewer than MIN_WINDOW snapshots is a REFUSAL.
    """
    if len(values) < MIN_WINDOW:
        refuse(f"Class C: {len(values)} snapshots in the window, registered "
               f"minimum {MIN_WINDOW}.  One reading is not evidence of "
               "convergence and a short window is refused, never graded")
    n = len(values)
    p2p = max(values) - min(values)
    tbar = sum(times) / n
    vbar = sum(values) / n
    sxx = sum((t - tbar) ** 2 for t in times)
    if sxx <= 0.0:
        refuse("Class C: the window carries no time variation; a trend cannot "
               "be fitted and an unfitted trend is not a passed one")
    slope = sum((times[i] - tbar) * (values[i] - vbar) for i in range(n)) / sxx
    drift = abs(slope) * (times[-1] - times[0])
    inc = [abs(values[i + 1] - values[i]) for i in range(n - 1)]
    growing = all(inc[i + 1] > inc[i] for i in range(len(inc) - 1))
    h = n // 2
    half_gap = abs(sum(values[h:]) / (n - h) - sum(values[:h]) / h)

    sustained_ok = p2p <= dr
    trend_ok = (drift <= dr) and not growing
    stationary = half_gap <= (dr / 2.0)

    return dict(n=n, p2p=p2p, dr=dr, slope=slope, drift=drift,
                increments_growing=growing, half_gap=half_gap,
                sustained_ok=sustained_ok, trend_ok=trend_ok,
                iterative="CONVERGED" if (sustained_ok and trend_ok)
                else "NOT CONVERGED",
                plateau="PLATEAUED" if stationary else "NOT PLATEAUED",
                mean=sum(values) / n)


# ---------------------------------------------------------------------------
# GATE 0 -- ADMISSIBILITY.  Every clause REFUSES; a refusal is not a GATE FAIL.
# ---------------------------------------------------------------------------
_TIME_RE = re.compile(r"^Time = ([0-9.eE+-]+)\s*$")
_EXEC_RE = re.compile(r"^ExecutionTime = ([0-9.eE+-]+) s\s+ClockTime = ([0-9]+) s")


def parse_log(log_path):
    times, execs, clocks, end = [], [], [], False
    with open(log_path, errors="replace") as fh:
        for line in fh:
            m = _TIME_RE.match(line)
            if m:
                times.append(float(m.group(1)))
                continue
            m = _EXEC_RE.match(line)
            if m:
                execs.append(float(m.group(1)))
                clocks.append(float(m.group(2)))
                continue
            if line.strip() == "End":
                end = True
    return dict(times=times, execs=execs, clocks=clocks, end=end)


def latest_time_dir(case_dir):
    best, bestname = None, None
    for name in os.listdir(case_dir):
        try:
            v = float(name)
        except ValueError:
            continue
        if v <= 0.0:
            continue
        if best is None or v > best:
            best, bestname = v, name
    return best, bestname


def check_no_preexisting(case_dir):
    """THE LAUNCH-SIDE GUARD (rule 4's last clause).  Refuses a case directory in
    which 0/ or any numeric time directory already exists.  The answer to a
    dirty case directory is a REFUSAL, never a delete: shutil.rmtree on a case
    directory is forbidden outright in cfd's territory."""
    if not os.path.isdir(case_dir):
        return True
    if os.path.isdir(os.path.join(case_dir, "0")):
        refuse(f"{case_dir}: 0/ already exists; refusing to build over it")
    v, name = latest_time_dir(case_dir)
    if v is not None:
        refuse(f"{case_dir}: time directory {name!r} already exists; refusing "
               "to build over it, and this file deletes nothing")
    return True


def check_completion(case_dir):
    """CLAUDE.md rule 4, with the ONE declared adaptation (the reach test).

    THE REACH TEST, AND WHY IT IS NOT |t_last - endTime| <= eps.
    adjustTimeStep yes sizes the final step from maxCo and nothing clips it onto
    endTime, so the last written time straddles endTime by O(1e-4) on either
    side.  The registered clause is

        t_last + dt_final > ENDTIME

    -- the solver could not have taken another step without passing endTime.
    dt_final is read from THE RUN'S OWN LOG (the difference of its last two
    Time = lines); it never looks at whether the run passed, which is what makes
    it a derivation and not a threshold fitted to the answer.  A two-sided
    tolerance is REFUSED as the expression of this clause and is named here so
    it cannot be reintroduced: choosing eps after seeing which runs it admits is
    the fit rule 2 exists to prevent.
    """
    out = dict(case=case_dir)
    rc_path = os.path.join(case_dir, "RC.txt")
    if not os.path.isfile(rc_path):
        refuse(f"{case_dir}: no RC.txt.  rule 4's first clause is rc = 0 and an "
               "INFERRED rc is not an rc: `set -e` does not gate at tool top "
               "level nor inside ( set -e; ... ).  The launcher writes it, "
               "syncs, and this grader reads it back")
    with open(rc_path) as fh:
        rc = int(fh.read().strip())
    out["rc"] = rc
    if rc != 0:
        refuse(f"{case_dir}: rc = {rc}")

    log = os.path.join(case_dir, "log.rhoCentralFoam")
    if not os.path.isfile(log):
        refuse(f"{case_dir}: no log.rhoCentralFoam")
    L = parse_log(log)
    if not L["end"]:
        refuse(f"{case_dir}: no End line")
    if len(L["times"]) < 2:
        refuse(f"{case_dir}: {len(L['times'])} Time = lines; dt_final cannot be "
               "derived from the run's own log")
    if len(L["times"]) != len(L["execs"]):
        refuse(f"{case_dir}: {len(L['times'])} Time = lines vs "
               f"{len(L['execs'])} ExecutionTime lines; a truncated or "
               "interleaved log is refused")
    t_last = L["times"][-1]
    dt_final = L["times"][-1] - L["times"][-2]
    out.update(t_last=t_last, dt_final=dt_final,
               execution_time_s=L["execs"][-1], clock_time_s=L["clocks"][-1])

    if not (t_last + dt_final > ENDTIME):
        refuse(f"{case_dir}: reach test FAILED -- t_last {t_last!r} + dt_final "
               f"{dt_final!r} = {t_last + dt_final!r} <= endTime {ENDTIME}; the "
               "solver could have taken another step without passing endTime")
    if t_last > RUNAWAY_T:
        refuse(f"{case_dir}: runaway guard -- t_last {t_last!r} > {RUNAWAY_T!r}")

    v, name = latest_time_dir(case_dir)
    if v is None:
        refuse(f"{case_dir}: no written time directory")
    if abs(v - t_last) > 1e-6:
        refuse(f"{case_dir}: last logged time {t_last!r} != latest written time "
               f"directory {name!r}")
    out["latest_dir"] = name

    zero_T = os.path.join(case_dir, "0", "T")
    if not os.path.isfile(zero_T):
        refuse(f"{case_dir}: no 0/T; the age guard has no reference")
    t0 = os.path.getmtime(zero_T)
    for fld in ("T", "U", "p", "rho"):
        fp = os.path.join(case_dir, name, fld)
        if not os.path.isfile(fp):
            refuse(f"{case_dir}: field {fld} missing at {name}")
        if not os.path.getmtime(fp) > t0:
            refuse(f"{case_dir}: AGE GUARD -- {name}/{fld} is not newer than "
                   "0/T; 0/T is touched last at launch and so dates the run "
                   "allowed to produce this answer")
    out["age_guard"] = "PASS"

    if L["clocks"][-1] > PER_CASE_WALL_GUARD_S:
        refuse(f"{case_dir}: per-case wall guard -- ClockTime "
               f"{L['clocks'][-1]!r} s > {PER_CASE_WALL_GUARD_S} s")
    return out


# ---------------------------------------------------------------------------
# LADDER SIMILARITY, MEASURED FROM THE WRITTEN DICTS.
# ---------------------------------------------------------------------------
_HEX_RE = re.compile(r"hex\s*\([^)]*\)\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)\s*"
                     r"simpleGrading\s*\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+"
                     r"([0-9.eE+-]+)\s*\)")


def measure_similarity(case_dirs):
    """MESH_STANDARD.md 9.2 -- reads nothing from RES, parses the hex line out of
    the blockMeshDict the mesher was ACTUALLY HANDED, in each case."""
    got = {}
    for level, cd in case_dirs.items():
        dict_path = os.path.join(cd, "system", "blockMeshDict")
        if not os.path.isfile(dict_path):
            refuse(f"{dict_path}: absent; similarity is measured from the "
                   "written dict or not at all")
        with open(dict_path) as fh:
            m = _HEX_RE.search(fh.read())
        if not m:
            refuse(f"{dict_path}: no parsable hex block line")
        ntheta, nr = int(m.group(1)), int(m.group(2))
        grading = float(m.group(5))
        cells = ntheta * nr * int(m.group(3))
        if (ntheta, nr) != NRES[level]:
            refuse(f"{dict_path}: written ({ntheta} {nr}), registered "
                   f"{NRES[level]}")
        if cells != CELLS[level]:
            refuse(f"{dict_path}: written mesh has {cells} cells, registered "
                   f"{CELLS[level]}")
        if abs(grading - RADIAL_GRADING) > 1e-12:
            refuse(f"{dict_path}: written radial grading {grading!r}, "
                   f"registered {RADIAL_GRADING}")
        _h, _i, h1 = cell_at_distance(nr, billig(6.0))
        got[level] = dict(ntheta=ntheta, nr=nr, cells=cells, h1=h1)
    r21 = (CELLS["medium"] / CELLS["coarse"]) ** (1.0 / DIM)
    r32 = (CELLS["fine"] / CELLS["medium"]) ** (1.0 / DIM)
    if abs(r21 - r32) > RT.EQUAL_RATIO_TOL:
        refuse(f"ladder is not equal-ratio: r21 = {r21!r}, r32 = {r32!r}")
    a = got["coarse"]["h1"] / got["medium"]["h1"]
    b = got["medium"]["h1"] / got["fine"]["h1"]
    for nm, v in (("coarse/medium", a), ("medium/fine", b)):
        if abs(v - 2.0) / 2.0 > SIM_H1_TOL:
            refuse(f"near-wall first-cell ratio {nm} = {v!r} is more than "
                   f"{SIM_H1_TOL * 100} % from 2")
    return dict(levels=got, r21=r21, r32=r32, h1_ratios=(a, b))


# ---------------------------------------------------------------------------
# CONTROLS.  All run BEFORE any gate is graded, and each REFUSES rather than
# degrading.  A zero -- or any number -- from a reader not shown able to see a
# non-zero is not evidence (rule 3).
# ---------------------------------------------------------------------------
def control_P0(xy_path, M):
    """P0 -- THE PLANT grade_ladder ITSELF CONSUMES.

    PLANT is added to rho at the crossing's own lower bracketing index in a COPY
    written by write_xy, and read back through read_xy -- the same parser the
    gate uses.  The delta must land to PLANT_READBACK_TOL or grade_ladder
    refuses on the control.
    """
    dist, T, p, rho = read_xy(xy_path)
    i, _w, _s, _n = locate_crossing(xy_path, M)
    tmp = tempfile.mkdtemp(prefix="f4s_P0_")
    try:
        work = os.path.join(tmp, os.path.basename(xy_path))
        before = rho[i]
        rho2 = list(rho)
        rho2[i] = before + PLANT
        write_xy(work, dist, T, p, rho2)
        _d2, _T2, _p2, rho_back = read_xy(work)
        after = rho_back[i]
    finally:
        rmtree_tmp_only(tmp)
    return external_plant_control("read_xy(rho column)", before, after,
                                  plant=PLANT, artifact=xy_path,
                                  level=f"index {i}")


def control_P1(xy_path, M):
    """P1 -- LOCALISATION, and it is EXACT rather than tolerance-bounded.

    The rho column is shifted by m whole sample intervals in a copy whose
    distance column is bit-identical to the parsed one.  The located crossing
    must then move by EXACTLY m indices with a BIT-IDENTICAL interpolation
    weight.  Two shifts, one inward and one outward, so a reader that happens to
    be right for one cannot pass by luck.

    A reader that ignores the file, or that returns a constant, fails this.
    """
    dist, T, p, rho = read_xy(xy_path)
    i0, w0, s0, _n = locate_crossing(xy_path, M)
    rows = []
    tmp = tempfile.mkdtemp(prefix="f4s_P1_")
    try:
        for m in SHIFTS:
            sh = list(rho)
            if m > 0:
                sh = [rho[0]] * m + rho[:NPOINTS - m]
            else:
                k = -m
                sh = rho[k:] + [rho[NPOINTS - 1]] * k
            work = os.path.join(tmp, os.path.basename(xy_path))
            write_xy(work, dist, T, p, sh)
            i1, w1, s1, _n1 = locate_crossing(work, M)
            ok = (i1 - i0 == m) and abs(w1 - w0) <= 1e-12
            rows.append(dict(shift=m, i_base=i0, i_planted=i1,
                             index_delta=i1 - i0, w_base=w0, w_planted=w1,
                             s_base=s0, s_planted=s1, passed=ok))
    finally:
        rmtree_tmp_only(tmp)
    for r in rows:
        if not r["passed"]:
            refuse("P1 FAILED: shifting rho by "
                   f"{r['shift']} samples moved the located crossing by "
                   f"{r['index_delta']} (weight {r['w_base']!r} -> "
                   f"{r['w_planted']!r}).  The detector does not localise on "
                   "this file and its loci mean nothing")
    return rows


def control_P1b(xy_path):
    """P1b -- the ARGMAX detector's endpoint state is REACHABLE.

    A dominating gradient is planted at the LAST sample index and the frozen
    argmax reader must return index NPOINTS-1, so the endpoint guard that
    refuses that index is shown to guard a reachable state rather than an
    imaginary one.  F4's census found r5 pinned there in 27 of 27 reads.
    """
    dist, T, p, rho = read_xy(xy_path)
    tmp = tempfile.mkdtemp(prefix="f4s_P1b_")
    try:
        sh = list(rho)
        sh[NPOINTS - 1] = sh[NPOINTS - 1] + 1.0e6
        work = os.path.join(tmp, os.path.basename(xy_path))
        write_xy(work, dist, T, p, sh)
        i, s = locate_argmax(work)
    finally:
        rmtree_tmp_only(tmp)
    if i != NPOINTS - 1:
        refuse(f"P1b FAILED: a dominating plant at index {NPOINTS - 1} was "
               f"located at {i}; the endpoint guard cannot be shown to guard a "
               "reachable state")
    return dict(planted_index=NPOINTS - 1, located_index=i, distance=s,
                passed=True)


def control_P2(sampdir, M):
    """P2 -- THE NEGATIVE CONTROL.  The selector must be UNABLE to see a plant
    at a station it does not declare.

    A plant is written into r3 (theta ~ 36 deg).  The r0 gate value must be
    BIT-IDENTICAL before, after and on restore.  A gate that moves when a file
    it did not declare is perturbed is reading something it did not declare.
    """
    gate_path = os.path.join(sampdir, GATE_STATION + XY_SUFFIX)
    neg_path = os.path.join(sampdir, NEG_STATION + XY_SUFFIX)
    if not os.path.isfile(neg_path):
        refuse(f"{neg_path}: absent; the negative control has no target and an "
               "unrun control is not a passed one")
    _i, _w, before, _n = locate_crossing(gate_path, M)
    tmp = tempfile.mkdtemp(prefix="f4s_P2_")
    try:
        backup = os.path.join(tmp, os.path.basename(neg_path))
        shutil.copy(neg_path, backup)
        with open(neg_path) as fh:
            original = fh.read()
        d, T, p, rho = read_xy(neg_path)
        write_xy(neg_path, d, T, p, [v + 3.0 for v in rho])
        _i2, _w2, during, _n2 = locate_crossing(gate_path, M)
        shutil.copy(backup, neg_path)
        with open(neg_path) as fh:
            restored = fh.read()
        _i3, _w3, after, _n3 = locate_crossing(gate_path, M)
    finally:
        rmtree_tmp_only(tmp)
    ok = (before == during == after) and (restored == original)
    if not ok:
        refuse(f"P2 FAILED: the {GATE_STATION} gate value moved "
               f"{before!r} -> {during!r} -> {after!r} when {NEG_STATION} was "
               "perturbed, or the perturbed file did not restore byte for byte")
    return dict(before=before, during=during, after=after, restored=True,
                passed=True)


def control_P3(case_dirs):
    """P3 -- the similarity check must STOP calling the ladder similar when the
    written dict is perturbed.  A similarity check that always says yes is
    indistinguishable from no check at all."""
    cd = case_dirs["medium"]
    dict_path = os.path.join(cd, "system", "blockMeshDict")
    with open(dict_path) as fh:
        original = fh.read()
    tmp = tempfile.mkdtemp(prefix="f4s_P3_")
    caught = None
    try:
        shutil.copy(dict_path, os.path.join(tmp, "blockMeshDict"))
        with open(dict_path, "w") as fh:
            fh.write(original.replace("(100 40 1)", "(100 41 1)"))
        try:
            measure_similarity(case_dirs)
        except Refusal as exc:
            caught = str(exc)
        shutil.copy(os.path.join(tmp, "blockMeshDict"), dict_path)
        with open(dict_path) as fh:
            restored = fh.read()
    finally:
        rmtree_tmp_only(tmp)
    if caught is None or restored != original:
        refuse("P3 FAILED: perturbing the written medium dict to (100 41 1) did "
               "not stop the similarity check, or the dict did not restore")
    return dict(refusal=caught, restored=True, passed=True)


def control_P4():
    """P4 -- Class C's stationarity and trend tests CAN report a failure.

    A flat series must return CONVERGED/PLATEAUED; a ramp must return NOT
    CONVERGED and NOT PLATEAUED; a series with GROWING increments and a small
    net slope must return NOT CONVERGED even though its drift is inside dr.
    """
    t = [3.375 + 0.375 * i for i in range(8)]
    dr = 1.0e-2
    flat = class_c(t, [0.44 + 1e-6 * (i % 2) for i in range(8)], dr)
    ramp = class_c(t, [0.44 + 0.02 * i for i in range(8)], dr)
    grow = class_c(t, [0.44, 0.4401, 0.43987, 0.44035, 0.43945,
                       0.44085, 0.43875, 0.44165], dr)
    if flat["iterative"] != "CONVERGED" or flat["plateau"] != "PLATEAUED":
        refuse(f"P4 FAILED: a flat series was graded {flat['iterative']}/"
               f"{flat['plateau']}")
    if ramp["iterative"] == "CONVERGED" or ramp["plateau"] == "PLATEAUED":
        refuse("P4 FAILED: a monotone ramp was graded CONVERGED or PLATEAUED; "
               "the stationarity test cannot report NOT stationary and is "
               "therefore not a test")
    if grow["increments_growing"] is not True or grow["trend_ok"] is not False:
        refuse("P4 FAILED: a series with strictly growing increments and a "
               "small net slope was not rejected by the trend fit")
    return dict(flat=flat, ramp=ramp, growing=grow, passed=True)


def control_P5():
    """P5 -- Class C element 4.  A window shorter than MIN_WINDOW must REFUSE.

    This is the element most likely to be quietly dropped, BECAUSE DROPPING IT
    ALWAYS MAKES A RUN GRADEABLE.  It is controlled, and the control is
    mutation-tested in --selftest.
    """
    t = [3.375 + 0.375 * i for i in range(MIN_WINDOW - 1)]
    v = [0.44] * (MIN_WINDOW - 1)
    try:
        class_c(t, v, 1.0e-2)
    except Refusal as exc:
        return dict(refusal=str(exc), n=MIN_WINDOW - 1, passed=True)
    refuse(f"P5 FAILED: a {MIN_WINDOW - 1}-snapshot window was GRADED; the "
           "minimum-sample-count refusal is absent and every short run is "
           "silently gradeable")


def control_C1(tmpdir_root=None):
    """C1 -- the completion checker must DISCRIMINATE a real adjustTimeStep
    landing from an early stop.  Two synthetic cases are BUILT ON DISK: one
    landing under endTime by 0.4 dt, one by 3 dt.  The first must be accepted,
    the second refused.

    P0-P3 are all about the READERS.  Nothing there exercises the completion
    path against a real landing time, and that is exactly how the reach-test
    defect survived a 21-check selftest in the predecessor.
    """
    dt = 4.0e-4
    out = {}
    tmp = tempfile.mkdtemp(prefix="f4s_C1_", dir=tmpdir_root)
    try:
        for tag, gap, want_ok in (("near", 0.4 * dt, True),
                                  ("early", 3.0 * dt, False)):
            t_last = ENDTIME - gap
            cd = os.path.join(tmp, tag)
            os.makedirs(os.path.join(cd, "0"))
            os.makedirs(os.path.join(cd, repr(t_last)))
            with open(os.path.join(cd, "0", "T"), "w") as fh:
                fh.write("0/T\n")
            os.utime(os.path.join(cd, "0", "T"), (1.0, 1.0))
            for fld in ("T", "U", "p", "rho"):
                fp = os.path.join(cd, repr(t_last), fld)
                with open(fp, "w") as fh:
                    fh.write(fld + "\n")
                os.utime(fp, (1000.0, 1000.0))
            with open(os.path.join(cd, "RC.txt"), "w") as fh:
                fh.write("0\n")
            with open(os.path.join(cd, "log.rhoCentralFoam"), "w") as fh:
                fh.write(f"Time = {t_last - dt!r}\n")
                fh.write("ExecutionTime = 1 s  ClockTime = 1 s\n\n")
                fh.write(f"Time = {t_last!r}\n")
                fh.write("ExecutionTime = 2 s  ClockTime = 2 s\n\nEnd\n")
            got_ok, why = True, None
            try:
                check_completion(cd)
            except Refusal as exc:
                got_ok, why = False, str(exc)
            out[tag] = dict(t_last=t_last, gap_in_dt=gap / dt,
                            accepted=got_ok, why=why)
            if got_ok != want_ok:
                refuse(f"C1 FAILED: the {tag} landing at {t_last!r} was "
                       f"{'accepted' if got_ok else 'refused'}; the completion "
                       "checker does not discriminate a real adjustTimeStep "
                       "landing from an early stop")
    finally:
        rmtree_tmp_only(tmp)
    out["passed"] = True
    return out


# ---------------------------------------------------------------------------
# THE SYNTHETIC PROFILE.  Written in the solver's own on-disk format and read
# back through the SAME parser the gates use, so the controls below are
# exercised end to end BEFORE any compute.  Only the numbers are synthetic: the
# format, the parser, the detectors and the plants are the production ones.
#
# rho(s) = rho_inf + (rho2 - rho_inf)/2 * (1 - tanh((s - s0)/w))
#                  + (rho_wall - rho2) * clamp((s0 - s)/s0, 0, 1)
#
# At s = s0 the tanh term is exactly the registered threshold rho* and the ramp
# is exactly zero, SO THE TRUE CROSSING IS AT s0 BY CONSTRUCTION and the
# detector's accuracy -- not merely its self-consistency -- is measurable.
# ---------------------------------------------------------------------------
def synthetic_profile(M, s0, w, rho_wall=None):
    rho2 = RHO_INF * rho_ratio_normal_shock(M)
    rho_wall = rho_wall if rho_wall is not None else rho2 * 1.08
    dist = [i * DS for i in range(NPOINTS)]
    T = [1.0] * NPOINTS
    p = [1.0] * NPOINTS
    rho = []
    for s in dist:
        base = RHO_INF + 0.5 * (rho2 - RHO_INF) * (1.0 - math.tanh((s - s0) / w))
        ramp = (rho_wall - rho2) * min(1.0, max(0.0, (s0 - s) / s0))
        rho.append(base + ramp)
    return dist, T, p, rho


def write_synthetic_station(dirpath, station, M, s0, w):
    os.makedirs(dirpath, exist_ok=True)
    path = os.path.join(dirpath, station + XY_SUFFIX)
    write_xy(path, *synthetic_profile(M, s0, w))
    return path


def detector_resolution_demo(M=7.0):
    """THE PRE-COMPUTE PROOF OF THIS DOCUMENT'S PREMISE, and it is falsifiable.

    The true shock is swept across ONE sample interval in 20 sub-steps.  The
    registered locus must track every sub-step; the predecessor's argmax locus
    can only report a member of the 400-point set and must therefore collapse
    the 20 sub-positions onto a handful of values.

    If the argmax locus were to track the sweep too, this document's whole
    premise would be wrong and the demonstration would say so.
    """
    _b, dr = band_abs(M, "fine")
    w = 1.5 * dr
    s_base = billig(M)
    tmp = tempfile.mkdtemp(prefix="f4s_demo_")
    xs, ax, err = [], [], []
    try:
        for k in range(20):
            s0 = s_base + k * DS / 20.0
            path = os.path.join(tmp, GATE_STATION + XY_SUFFIX)
            write_xy(path, *synthetic_profile(M, s0, w))
            _i, _wt, s_cross, _n = locate_crossing(path, M)
            _ia, s_arg = locate_argmax(path)
            xs.append(s_cross); ax.append(s_arg); err.append(abs(s_cross - s0))
    finally:
        rmtree_tmp_only(tmp)
    return dict(M=M, n_sweep=20, ds=DS, smearing_w=w,
                distinct_crossing=len(set(xs)), distinct_argmax=len(set(ax)),
                max_abs_error_crossing=max(err),
                crossing_error_in_ds=max(err) / DS,
                argmax_span=max(ax) - min(ax))


def controls_on_synthetic(M=7.0):
    """P0, P1, P1b and P2 exercised END TO END on a file written in the
    production format and read by the production parser, before any compute."""
    _b, dr = band_abs(M, "fine")
    s0 = billig(M) + 0.31 * DS
    tmp = tempfile.mkdtemp(prefix="f4s_syn_")
    try:
        sampdir = os.path.join(tmp, "6")
        gate = write_synthetic_station(sampdir, GATE_STATION, M, s0, 1.5 * dr)
        write_synthetic_station(sampdir, NEG_STATION, M, s0 * 1.11, 1.5 * dr)
        _i, _wt, s_det, _n = locate_crossing(gate, M)
        out = dict(true_s0=s0, detected=s_det, abs_error=abs(s_det - s0),
                   error_in_ds=abs(s_det - s0) / DS,
                   P0=control_P0(gate, M), P1=control_P1(gate, M),
                   P1b=control_P1b(gate), P2=control_P2(sampdir, M))
    finally:
        rmtree_tmp_only(tmp)
    return out


# ---------------------------------------------------------------------------
# THE GRADE.  rule 5 is reached through grade_ladder and through nothing else.
# ---------------------------------------------------------------------------
def snapshot_times(case_dir):
    root = os.path.join(case_dir, "postProcessing", "sampleDict")
    if not os.path.isdir(root):
        refuse(f"{case_dir}: no postProcessing/sampleDict")
    times = []
    for name in os.listdir(root):
        try:
            times.append((float(name), name))
        except ValueError:
            continue
    times.sort()
    if len(times) < N_WINDOW:
        refuse(f"{case_dir}: {len(times)} sampled times, the registered "
               f"sustained window is {N_WINDOW}")
    return times[-N_WINDOW:]


def measure_case(case_dir, M):
    """Every measurement for one case.  Refuses; never degrades."""
    comp = check_completion(case_dir)
    win = snapshot_times(case_dir)
    dr, _i, _h1 = cell_at_distance(
        NRES[os.path.basename(case_dir)][1], billig(M)) \
        if os.path.basename(case_dir) in NRES else (None, None, None)
    if dr is None:
        refuse(f"{case_dir}: basename is not one of {LEVELS}")

    ts, xs, ax = [], [], []
    for tv, tname in win:
        sampdir = os.path.join(case_dir, "postProcessing", "sampleDict", tname)
        gate_path = os.path.join(sampdir, GATE_STATION + XY_SUFFIX)
        if not os.path.isfile(gate_path):
            refuse(f"{gate_path}: absent")
        dev = preshock_undisturbed(gate_path)
        if dev > 0.01:
            refuse(f"{gate_path}: the far end of the sample line is at rho "
                   f"{dev * 100:.4f} % from free stream; the domain is "
                   "disturbed at its outer edge and the standoff would be "
                   "measured against a moving reference")
        i, w, s, ncr = locate_crossing(gate_path, M)
        if ncr != 1:
            refuse(f"{gate_path}: {ncr} crossings of rho*; the locus is not "
                   "single-valued and a multi-valued locus is refused")
        if endpoint_censored(i):
            refuse(f"{gate_path}: crossing at index {i}, an endpoint of the "
                   "detector's own range [0, 399]; a range limit is not a "
                   "measurement")
        ia, sa = locate_argmax(gate_path)
        if endpoint_censored(ia):
            refuse(f"{gate_path}: argmax at index {ia}, an endpoint of the "
                   "detector's own range; a range limit is not a measurement")
        ts.append(tv); xs.append(s); ax.append(sa)

    cc_x = class_c(ts, xs, dr)
    cc_a = class_c(ts, ax, dr)
    last_dir = os.path.join(case_dir, "postProcessing", "sampleDict",
                            win[-1][1])
    return dict(case=case_dir, M=M, completion=comp, dr=dr, times=ts,
                crossing=xs, argmax=ax, class_c_crossing=cc_x,
                class_c_argmax=cc_a, value_crossing=cc_x["mean"],
                value_argmax=cc_a["mean"], last_sampdir=last_dir)


def grade_all(root, out_json=None):
    if "successor_" not in os.path.abspath(root):
        refuse(f"{root}: this grader mutates files during P2 and P3 and will "
               "only ever point at a successor_* run root.  An instrument that "
               "could silently corrupt the artifact it measures is a hazard, "
               "not an instrument")
    no_assert_selfcheck()

    report = dict(root=os.path.abspath(root), dim=DIM, fs=FS, form=FORM,
                  rho_inf=RHO_INF, npoints=NPOINTS, ds=DS,
                  window=N_WINDOW, min_window=MIN_WINDOW,
                  assert_nodes_in_grader=0, controls={}, rows=[])

    report["controls"]["P4"] = control_P4()
    report["controls"]["P5"] = control_P5()
    report["controls"]["C1"] = control_C1()

    for M in MACHS:
        case_dirs = {lv: os.path.join(root, "cyl", f"M{M}", lv)
                     for lv in LEVELS}
        sim = measure_similarity(case_dirs)
        report["controls"].setdefault("P3", {})[f"M{M}"] = control_P3(case_dirs)
        cases = {lv: measure_case(case_dirs[lv], M) for lv in LEVELS}

        fine_sampdir = cases["fine"]["last_sampdir"]
        gate_path = os.path.join(fine_sampdir, GATE_STATION + XY_SUFFIX)
        p0 = control_P0(gate_path, M)
        report["controls"].setdefault("P0", {})[f"M{M}"] = p0
        report["controls"].setdefault("P1", {})[f"M{M}"] = control_P1(gate_path, M)
        report["controls"].setdefault("P1b", {})[f"M{M}"] = control_P1b(gate_path)
        report["controls"].setdefault("P2", {})[f"M{M}"] = control_P2(
            fine_sampdir, M)

        band, dr_fine = band_abs(M, "fine")
        common = dict(dim=DIM, band=band, plant_control=p0, fs=FS, form=FORM,
                      reference=billig(M))

        for gate, key, cckey in (("G-F4S-1", "value_crossing", "class_c_crossing"),
                                 ("G-F4S-1B", "value_argmax", "class_c_argmax")):
            levels = [dict(name=lv, cells=CELLS[lv], value=cases[lv][key])
                      for lv in LEVELS]
            it = {lv: cases[lv][cckey]["iterative"] for lv in LEVELS}
            pl = {lv: cases[lv][cckey]["plateau"] for lv in LEVELS}
            row = grade_ladder(f"{gate}-M{M}", levels, iterative_states=it,
                               plateau_states=pl, **common)
            row["gate"] = gate
            row["mach"] = M
            row["band_pct_of_reference"] = 100.0 * dr_fine / billig(M)
            row["deviation_pct"] = 100.0 * (row["value"] - billig(M)) / billig(M)
            row["similarity"] = sim
            report["rows"].append(row)

    if out_json:
        with open(out_json, "w") as fh:
            json.dump(report, fh, indent=2, default=str)
        print(f"wrote {out_json}")
    return report


def print_report(report):
    print(f"root  {report['root']}")
    print(f"dim {report['dim']}  Fs {report['fs']}  form {report['form']}  "
          f"window {report['window']} (min {report['min_window']})")
    print(f"ast.Assert nodes in this grader: "
          f"{report['assert_nodes_in_grader']}")
    print("")
    for row in report["rows"]:
        vals = " -> ".join(f"{lv['value']:.6f}" for lv in row["levels"])
        print(f"{row['quantity']:<22} {vals}")
        print(f"   states {row['states']}  orders {row['orders']}")
        print(f"   band {row['band']}  (+/- {row['band_pct_of_reference']:.4f} "
              f"% of Billig)  deviation {row['deviation_pct']:+.4f} %")
        print(f"   band_verdict (G-F4S-2 channel): {row['band_verdict']}")
        print(f"   VERDICT: {row['verdict']}")
        if "GCI_pct" in row:
            print(f"   observed order {row['order']:.4f}  "
                  f"GCI {row['GCI_pct']:.4f} % at Fs = {row['fs']}")
        print(f"   why: {row['why']}")
        print("")


# ---------------------------------------------------------------------------
# SELFTEST
# ---------------------------------------------------------------------------
def selftest():
    checks = []

    def ok(name, cond, detail=""):
        checks.append((name, bool(cond), detail))

    ok("no ast.Assert node in this grader", assert_node_count(
        os.path.abspath(__file__)) == 0)
    ok("grade_ladder is the graded path (imported symbol is roache_triple's)",
       grade_ladder is RT.grade_ladder)
    ok("Fs matches the shared instrument", FS == RT.FS, f"{FS}")
    ok("form is 'equal', never 'auto'", FORM == "equal")

    for M, want in ((6.0, 0.43946566521114816), (7.0, 0.4245982772504153),
                    (8.0, 0.41521901145222184)):
        ok(f"Billig M={M}", abs(billig(M) - want) <= 1e-15, repr(billig(M)))
    for M, want in ((6.0, 1.8180637188927689), (7.0, 1.823691727535517),
                    (8.0, 1.8273541997099865)):
        ok(f"Cp_max M={M}", abs(cp_max(M) - want) <= 1e-15, repr(cp_max(M)))
    for M, want in ((6.0, 4.3878048780487795), (7.0, 4.511111111111111),
                    (8.0, 4.595652173913043)):
        ok(f"rho* M={M}", abs(rho_threshold(M) - want) <= 1e-15,
           repr(rho_threshold(M)))
        ok(f"rho* M={M} lies strictly inside (rho_inf, rho2)",
           RHO_INF < rho_threshold(M) < RHO_INF * rho_ratio_normal_shock(M))

    for M, wants in ((6.0, (13.3916, 6.4598, 3.1747)),
                     (7.0, (13.8605, 6.6860, 3.2005)),
                     (8.0, (12.7042, 6.4820, 3.2728))):
        for lv, want in zip(LEVELS, wants):
            _b, dr = band_abs(M, lv)
            pct = 100.0 * dr / billig(M)
            ok(f"band M={M} {lv} = +/-{want} %", abs(pct - want) <= 5e-5,
               f"{pct:.4f}")
    for M in MACHS:
        _b, c = band_abs(M, "coarse")
        _b, m = band_abs(M, "medium")
        _b, f = band_abs(M, "fine")
        ok(f"band tightens ~2x per level M={M} -- the signature of an "
           "instrument-resolution band",
           1.8 <= c / m <= 2.3 and 1.8 <= m / f <= 2.3,
           f"{c / m:.4f} {m / f:.4f}")
    ok("sample spacing", abs(DS - 0.0017543859649122805) <= 1e-18, repr(DS))
    for M in MACHS:
        _b, dr = band_abs(M, "fine")
        ok(f"fine cell is >7 sample quanta wide at M={M} -- refining the "
           "sample line cannot help", dr / DS > 7.0, f"{dr / DS:.3f}")

    demo = detector_resolution_demo(7.0)
    ok("DETECTOR: the registered crossing locus resolves SUB-SAMPLE -- 20 "
       "sub-positions inside one sample interval give 20 distinct loci",
       demo["distinct_crossing"] == 20, f"{demo['distinct_crossing']}")
    ok("DETECTOR: the crossing locus tracks the true shock to < DS/10",
       demo["crossing_error_in_ds"] < 0.1,
       f"max err {demo['max_abs_error_crossing']:.3e} = "
       f"{demo['crossing_error_in_ds']:.4f} DS")
    ok("DETECTOR: the predecessor's argmax locus is QUANTISED -- the same 20 "
       "sub-positions collapse onto at most 3 values",
       demo["distinct_argmax"] <= 3, f"{demo['distinct_argmax']}")

    syn = controls_on_synthetic(7.0)
    ok("SYNTHETIC: the detector recovers a KNOWN sub-sample shock location",
       syn["error_in_ds"] < 0.1, f"{syn['error_in_ds']:.5f} DS")
    ok("P0 (the plant grade_ladder consumes) on an on-disk file",
       syn["P0"]["passed"], f"delta {syn['P0']['read_back_delta']!r}")
    ok("P1 (localisation, two shifts, exact index and weight)",
       all(r["passed"] for r in syn["P1"]),
       str([(r["shift"], r["index_delta"]) for r in syn["P1"]]))
    ok("P1b (the argmax endpoint state is REACHABLE, so its guard guards "
       "something)", syn["P1b"]["passed"])
    ok("P2 (the selector CANNOT see a plant at a station it did not declare)",
       syn["P2"]["passed"], f"gate value {syn['P2']['before']!r} unmoved")

    ok("P4 (Class C can report NOT stationary)", control_P4()["passed"])
    ok("P5 (short window REFUSES)", control_P5()["passed"])
    ok("C1 (completion discriminates)", control_C1()["passed"])

    # MUTATIONS -- each must FAIL, or the control it guards is decorative.
    saved = globals()["class_c"]
    try:
        def stub_never_refuses(times, values, dr):
            return dict(n=len(values), p2p=0.0, dr=dr, slope=0.0, drift=0.0,
                        increments_growing=False, half_gap=0.0,
                        sustained_ok=True, trend_ok=True,
                        iterative="CONVERGED", plateau="PLATEAUED",
                        mean=sum(values) / len(values))
        globals()["class_c"] = stub_never_refuses
        mutated_caught = False
        try:
            control_P5()
        except Refusal:
            mutated_caught = True
        ok("MUTATION: dropping the sample-count refusal makes P5 fail",
           mutated_caught)
        mutated_caught = False
        try:
            control_P4()
        except Refusal:
            mutated_caught = True
        ok("MUTATION: a stationarity test that always passes makes P4 fail",
           mutated_caught)
    finally:
        globals()["class_c"] = saved

    saved = globals()["check_completion"]
    try:
        globals()["check_completion"] = lambda cd: dict(case=cd)
        mutated_caught = False
        try:
            control_C1()
        except Refusal:
            mutated_caught = True
        ok("MUTATION: a completion checker that never refuses makes C1 fail",
           mutated_caught)
    finally:
        globals()["check_completion"] = saved

    # grade_ladder's own two branches, on synthetic triples.
    pc = external_plant_control("selftest", 0.0, PLANT, plant=PLANT)
    lv_conv = [dict(name="coarse", cells=1000, value=1.10),
               dict(name="medium", cells=4000, value=1.04),
               dict(name="fine", cells=16000, value=1.01)]
    lv_osc = [dict(name="coarse", cells=1000, value=1.00),
              dict(name="medium", cells=4000, value=1.10),
              dict(name="fine", cells=16000, value=1.02)]
    st = {lv: "CONVERGED" for lv in LEVELS}
    pl = {lv: "PLATEAUED" for lv in LEVELS}
    r = grade_ladder("selftest-converging", lv_conv, dim=DIM, band=(0.9, 1.1),
                     plant_control=pc, iterative_states=st, plateau_states=pl,
                     fs=FS, form=FORM)
    ok("grade_ladder CAN return a PASS on a converging triple",
       r["verdict"] == "PASS", f"{r['verdict']} p={r.get('order')}")
    r = grade_ladder("selftest-oscillatory", lv_osc, dim=DIM, band=(0.9, 1.1),
                     plant_control=pc, iterative_states=st, plateau_states=pl,
                     fs=FS, form=FORM)
    ok("grade_ladder CAN return NOT A RESULT on a non-monotone triple",
       r["verdict"] == "NOT A RESULT" and r.get("GCI_pct") is None,
       f"{r['verdict']}")
    r = grade_ladder("selftest-not-converged", lv_conv, dim=DIM,
                     band=(0.9, 1.1), plant_control=pc,
                     iterative_states={"coarse": "NOT CONVERGED",
                                       "medium": "CONVERGED",
                                       "fine": "CONVERGED"},
                     plateau_states=pl, fs=FS, form=FORM)
    ok("rule 5 step (a) is REACHED: a not-converged level -> NOT A RESULT",
       r["verdict"] == "NOT A RESULT", f"{r['verdict']}")
    caught = False
    try:
        grade_ladder("selftest-no-states", lv_conv, dim=DIM, band=(0.9, 1.1),
                     plant_control=pc, iterative_states=None,
                     plateau_states=pl, fs=FS, form=FORM)
    except Refusal:
        caught = True
    ok("grade_ladder REFUSES when iterative_states is omitted", caught)
    caught = False
    try:
        grade_ladder("selftest-no-plant", lv_conv, dim=DIM, band=(0.9, 1.1),
                     plant_control=None, iterative_states=st,
                     plateau_states=pl, fs=FS, form=FORM)
    except Refusal:
        caught = True
    ok("grade_ladder REFUSES with no planted-zero control", caught)

    # the -O refusal, driven for real.
    import subprocess
    p = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                        "--selftest"], capture_output=True, text=True)
    ok("python3 -O exits 2 at entry", p.returncode == 2,
       f"rc={p.returncode}")

    bad = [(n, d) for n, c, d in checks if not c]
    for n, c, d in checks:
        print(f"  [{'ok ' if c else 'FAIL'}] {n}" + (f"   {d}" if d else ""))
    if bad:
        print(f"SELFTEST FAILED: {len(bad)} of {len(checks)}")
        return 1
    # printed INSIDE the passing branch: removing the check removes the claim.
    print(f"SELFTEST PASSED: {len(checks)} checks, "
          f"{sum(1 for n, _c, _d in checks if n.startswith('MUTATION'))} "
          "mutations that had to fail")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--json")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--astcheck", help="AST-parse another file and refuse if it "
                                       "carries any assert")
    a = ap.parse_args()
    try:
        if a.selftest:
            return selftest()
        if a.astcheck:
            n = no_assert_selfcheck(a.astcheck)
            print(f"{a.astcheck}: {n} ast.Assert nodes")
            return 0
        if not a.root:
            print("--root or --selftest required", file=sys.stderr)
            return 2
        print_report(grade_all(a.root, out_json=a.json))
        return 0
    except Refusal as exc:
        print(f"REFUSE: {exc}", file=sys.stderr)
        return EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(main())
