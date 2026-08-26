#!/usr/bin/env python3
"""
F15-R2 -- COMPARATOR RE-REGISTRATION UNDER L-342 (2026-08-26). ZERO COMPUTE.
==========================================================================
PARENT: cases/F15_oblique_shock_reflection/grade_f15.py, blob e4076c03ca68d67e8247f73a4038d179cd7a20f2
        (identical on disk, at HEAD and at the freeze commit 2aea29d9).
DEFECTS (both measured on the preserved artefacts of the 2aea29d9 run):
  (i)  TIME_RE, DELTAT_RE and CLOCK_RE are ^-anchored and applied with
       .finditer() to the whole log WITHOUT re.MULTILINE: 0 of the 9233
       `Time =` lines in verification/runs/F15_runs/coarse/log.rhoCentralFoam
       are read -> completion() says "no `Time =` lines" on a complete level.
  (ii) read_xy_p pins FOUR columns (x y z p), measured on F6b's `axis xyz`
       sets; this case's sets are `type midPoint; axis x`, and OpenFOAM's raw
       writer emits ONE coordinate column for a single axis: the real
       lineWall_p.xy / lineY05_p.xy carry TWO columns (x p).
RULE:   L-342 -- a bookkeeping failure invalidates the bookkeeping, never the
        physics artefacts. The parent is NOT edited (rule 2). This file is a NEW
        registration grading the PRESERVED artefacts; scope widened over the
        F16-R2 form on cfd-supervisor's ruling of 2026-08-26.
DIFF SCOPE against the parent, and NOTHING ELSE:
  (1) this header block;
  (2) the L-342 field-class declaration (PHYSICS_CRITICAL / INFRASTRUCTURE)
      below VERDICTS, and the infrastructure census that prints `BOOKKEEPING
      DEFECT` lines beside the tally instead of refusing;
  (3) read_xy_p: shape pin 4 -> 2, x = column 0, p = column 1; the p-column
      plant index in plant_control_e1 (3 -> 1) and synth_xy writing the same
      two-column shape, so the plant and the demonstration still go through
      the REAL write format;
  (4) TIME_RE, DELTAT_RE, CLOCK_RE compiled with re.MULTILINE;
  (5) two driven controls appended to the selftest: the completion reader on a
      VERBATIM excerpt of the real coarse log (5 `Time =`, 5 `deltaT =`,
      5 ClockTime, 1 `End` planted; positive and negative) and the sample
      reader on a VERBATIM excerpt of the real lineWall_p.xy (39 rows);
      the class-C probe importing THIS module by its own basename;
  (6) the JSON `rung` label F15-OSR29-R2, the parent blob and the R2 prereg
      path; default output F15_R2_GRADED.json; the tally title.
GATES, BANDS, THRESHOLDS, CAP AND LABELS ARE BYTE-IDENTICAL to the parent:
N_CAPTURE_CELLS, END_TIME, SAMPLE_INTERVAL, CAP_CORE_MIN, CLASS_C, bands(),
smeared_profile(), demonstrate(), grade_one() and the single grade_ladder call
are untouched lines.
Refusals reclassified from refusal to BOOKKEEPING DEFECT: NONE -- the parent
keys no refusal on an infrastructure field (CAP_CORE_MIN is written to the
record only; clock_time_s is recorded as detail and never gates).

F15 -- THE GRADING PATH for the oblique shock reflection at M_inf = 2.9.
It calls `scripts/roache_triple.py::grade_ladder` and rule 5 is reached through
that call and through NOTHING ELSE.  There is no second triple in this file:
`grep -n grade_ladder` finds exactly one call site, and `--selftest` proves the
grep can see a call by planting one (see `control_grade_ladder_is_called`).

WHY THAT SENTENCE IS AT THE TOP.  cfd-supervisor's ruling at `887ddfaf`: a
grader that reimplements the Roache triple bypasses the one place standing rule 5
is enforced.  F4's did, and rule 5 clause (a) was unreachable for all nine of its
rows.  A registration tonight claimed compliance while its path called
`grade_ladder` nowhere.

REFUSAL DISCIPLINE
------------------
`raise` / `sys.exit(2)` only.  ZERO `assert` statements, checked by AST parse at
every entry (L-332).  And because `grade_ladder` reaches its own gate through
four asserts in the SHARED instrument -- `roache_triple.py:195, 632, 634, 637`,
carrying rule 1's verdict vocabulary and rule 5's one-way asymmetry -- which
`python3 -O` deletes, THIS FILE REFUSES TO RUN UNDER `-O` AT ALL, at entry,
before anything else executes.  That shared file is referred to verification and
is not this team's to edit; the refusal is placed at the boundary F15 owns.

THE CONVERGENCE GATE IS CLASS C (CFD_CONVERGENCE_GATE_RULING_2026-08-25.md §2),
all four elements, and element 4 -- refusal below a minimum sample count --
exits 2 rather than returning a state, because the ruling says so and because
dropping it always makes a run gradeable.
"""
import sys

if not __debug__:
    sys.stderr.write(
        "REFUSED: grade_f15.py must not run under `python3 -O`.\n"
        "  -O deletes every `assert`, including roache_triple.py:195,632,634,637,\n"
        "  which carry require_dim and the _seal invariants: the verdict must be\n"
        "  in the fixed vocabulary, the gate must be one-way against the band\n"
        "  verdict, and NO GCI may be quoted on a non-monotone triple. With those\n"
        "  deleted, rule 1 and rule 5 are not enforced by anything.\n")
    sys.exit(2)

import os
import re
import ast
import json
import math
import shutil
import tempfile
import argparse
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)

import roache_triple as RT              # THE GATE. Rule 5 lives here and nowhere else.
import exact_osr as EX                  # THE EXACT SOLUTION, self-verifying.

DIM = 2                                 # 2-D refinement; printed beside every order
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

# ---------------------------------------------------------------------------
# L-342 FIELD CLASSES.  Gates read PHYSICS_CRITICAL fields only.  An absent or
# unreadable INFRASTRUCTURE field is reported as NOT MEASURED beside the verdict
# as a `BOOKKEEPING DEFECT` line; it never refuses and never voids a run.
# ---------------------------------------------------------------------------
PHYSICS_CRITICAL = (
    "log.rhoCentralFoam `Time =` and `deltaT =` lines (final-step limb)",
    "log.rhoCentralFoam `End` line",
    "fields T, U, p at endTime and newer than 0/T (age guard)",
    "postProcessing/lineY05 and lineWall <t>/<set>_p.xy series",
    "postProcessing/pAvg volFieldValue.dat monitor",
)
INFRASTRUCTURE = (
    "ClockTime / cost in core-minutes (CAP_CORE_MIN)",
    "STATUS.F15 rc/end line written by the launcher",
    "launcher.out running tally",
    "RC.txt per level (the launcher's copy of the solver rc)",
)


def infrastructure_census(root):
    """L-342: read every INFRASTRUCTURE field, mark absence NOT MEASURED, never
    refuse. Returns the census and the list of BOOKKEEPING DEFECT lines."""
    census, defects = {}, []
    total = 0.0
    for name, _nx, _ny in LEVELS:
        lp = os.path.join(root, name, "log.rhoCentralFoam")
        clocks = [int(m.group(1)) for m in CLOCK_RE.finditer(
            open(lp, errors="replace").read())] if os.path.isfile(lp) else []
        rcp = os.path.join(root, name, "RC.txt")
        rc = open(rcp).read().strip() if os.path.isfile(rcp) else None
        row = dict(clock_time_s=clocks[-1] if clocks else None,
                   core_min=(clocks[-1] * RANKS[name] / 60.0) if clocks else None,
                   rc_txt=rc)
        census[name] = row
        if row["core_min"] is None:
            defects.append("BOOKKEEPING DEFECT: level %s ClockTime NOT MEASURED "
                           "(infrastructure field; grade proceeds)" % name)
        else:
            total += row["core_min"]
        if rc is None:
            defects.append("BOOKKEEPING DEFECT: level %s RC.txt absent "
                           "(infrastructure field; grade proceeds)" % name)
    st = os.path.join(root, "STATUS.F15")
    census["status_file"] = open(st).read().strip() if os.path.isfile(st) else None
    if census["status_file"] is None:
        defects.append("BOOKKEEPING DEFECT: STATUS.F15 absent (infrastructure "
                       "field; grade proceeds)")
    census["total_core_min"] = total
    census["cap_core_min"] = CAP_CORE_MIN
    if total > CAP_CORE_MIN:
        defects.append("BOOKKEEPING DEFECT: measured %.4f core-min exceeds the "
                       "registered cap %.1f -- reported, not a refusal; the "
                       "launcher's incremental cap check is the stopping "
                       "instrument" % (total, CAP_CORE_MIN))
    return census, defects

# ---------------------------------------------------------------------------
# THE LADDER, FROZEN.  Coarse first, as grade_ladder requires.
# The coarse level is the paper's own 200 x 50 grid.
# ---------------------------------------------------------------------------
LEVELS = (("coarse", 200, 50), ("medium", 400, 100), ("fine", 800, 200))
CELLS = dict((n, nx * ny) for n, nx, ny in LEVELS)
DX = dict((n, (EX.X_MAX - EX.X_MIN) / float(nx)) for n, nx, _ny in LEVELS)

# THE ONE DECLARED PARAMETER BOTH BANDS ARE BUILT FROM.  Declared BEFORE any
# run: the number of cells a limited second-order shock-capturing scheme is
# ALLOWED to smear one steady oblique shock over.  It is not measured, not
# fitted, and not revisable after first compute.
N_CAPTURE_CELLS = 8

END_TIME = 10.0                         # 7.25 flow-throughs at u1 = 2.9 over L = 4;
#                                       the endTime OpenFOAM's own obliqueShock
#                                       tutorial uses for this same case
SAMPLE_INTERVAL = 0.05                  # functionObject write interval
CAP_CORE_MIN = 200.0                    # wall_s(ClockTime) * ranks / 60, summed
#                                       over levels. 1.6x the estimate built from
#                                       the lab-MEASURED 1.03 us/cell/step.
RANKS = dict(coarse=1, medium=1, fine=1)   # AMENDMENT 1, 2026-08-26:
#   serial at every level; decomposePar is not invoked. A ladder must differ
#   ONLY in mesh, and a changing rank count changes the summation order.

# CLASS C, all four elements, registered here and nowhere else.
CLASS_C = dict(
    min_samples=100,     # element 4: 5.0 of 10.0 time units at 0.05 -> refuse below
    window=60,           # element 1: the criterion holds over 3.0 time units,
                         #   which is 2.2 flow-throughs -- longer than any single
                         #   traverse of the domain, so a wave crossing the
                         #   sampled line cannot sit inside the window
    trend_tol=2.0e-3,    # element 2: |fitted drift| over the window, relative
    stat_tol=1.0e-3,     # element 3: two-half mean split, relative
    var_ratio=(0.2, 5.0),# element 3: two-half variance ratio must be O(1)
    floor=1.0e-12,
)

WRITE_PATH_NOTE = (
    "OpenFOAM `sets` functionObject, `setFormat raw`, writing "
    "<case>/postProcessing/<setName>/<time>/<setName>_p.xy with THREE "
    "coordinate columns (x y z) followed by the field. Format pinned against "
    "REAL solver output already on this box -- 2690 such files exist under "
    "verification/runs and /home/ubuntu/certonomous-runs; "
    "verification/runs/F6b_runs/coarse/postProcessing/singleGraph_x0/3418/"
    "line_k_nut_omega_p_U.xy carries 10 columns = 3 coordinates + k + nut + "
    "omega + p + 3 U components, which is where the three-coordinate layout "
    "was measured rather than assumed.")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# READERS -- the real read path, one per graded quantity
# ---------------------------------------------------------------------------
def read_xy_p(path):
    """Read a `sets`/raw .xy carrying ONE scalar. Refuses on any other shape."""
    if not os.path.isfile(path):
        refuse("no sampled file at %s" % path)
    arr = np.loadtxt(path, comments="#", ndmin=2)
    if arr.ndim != 2 or arr.shape[1] != 2:
        refuse("%s has %d columns; a `sets`/raw sample of one scalar on a "
               "single-axis (`axis x`) set has exactly 2 (x p) -- R2: measured "
               "on the real lineWall_p.xy, not on F6b's axis-xyz layout. %s"
               % (path, arr.shape[1] if arr.ndim == 2 else -1, WRITE_PATH_NOTE))
    if arr.shape[0] < 8:
        refuse("%s has only %d sampled points; refusing to integrate a line "
               "error over that" % (path, arr.shape[0]))
    order = np.argsort(arr[:, 0])
    return arr[order, 0], arr[order, 1]        # R2: p is column 1 (x p)


def e1_from_xy(path, sol=None):
    """G-F15-1: the domain-normalised L1 pressure error along y = 0.5.

        E1 = (1 / (L * p1)) * Int |p_num(x) - p_exact(x)| dx
    """
    sol = EX.solve() if sol is None else sol
    x, p = read_xy_p(path)
    pe = np.array([EX.p_exact_along_sample_line(float(xi), sol) for xi in x])
    integral = np.trapezoid(np.abs(p - pe), x) if hasattr(np, "trapezoid") \
        else np.trapz(np.abs(p - pe), x)
    return float(integral / (sol["domain_length"] * sol["region1"]["p"]))


def x_wall_from_xy(path, sol=None):
    """G-F15-2: the incident shock's wall impingement abscissa, from the
    half-rise crossing of the wall pressure, linearly interpolated between the
    two bracketing samples so the estimate is SUB-CELL and continuous.  A
    cell-centre estimate would be quantised and would make the triple STAGNANT
    for reasons that have nothing to do with the solution."""
    sol = EX.solve() if sol is None else sol
    x, p = read_xy_p(path)
    p_half = 0.5 * (sol["region1"]["p"] + sol["region3"]["p"])
    idx = np.where((p[:-1] < p_half) & (p[1:] >= p_half))[0]
    if idx.size == 0:
        refuse("%s: the wall pressure never crosses the half-rise value %.6f; "
               "min %.6f max %.6f. The gate quantity is ABSENT, which is "
               "reported as absent and never graded as a pass."
               % (path, p_half, float(p.min()), float(p.max())))
    i = int(idx[0])
    f = (p_half - p[i]) / (p[i + 1] - p[i])
    return float(x[i] + f * (x[i + 1] - x[i]))


# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (standing rule 3) -- into the REAL artifact, read back
# with the REAL parser, refusing on failure
# ---------------------------------------------------------------------------
def _plant_column(src, dst, col, delta):
    rows = 0
    with open(dst, "w") as out:
        for line in open(src):
            if line.startswith("#") or not line.strip():
                out.write(line)
                continue
            parts = line.split()
            parts[col] = repr(float(parts[col]) + delta)
            out.write(" ".join(parts) + "\n")
            rows += 1
    return rows


def plant_control_e1(path, level, sol):
    """Add a known offset to the p column.  Every pointwise error moves by
    exactly that offset, so the post-plant E1 is PREDICTABLE from the pre-plant
    error array -- and the reader must reproduce the prediction to 1e-12.  A
    reader that ignored the file would return the same value twice and fail."""
    d = RT.PLANT
    x, p = read_xy_p(path)
    pe = np.array([EX.p_exact_along_sample_line(float(xi), sol) for xi in x])
    e = p - pe
    trap = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    scale = sol["domain_length"] * sol["region1"]["p"]
    before = float(trap(np.abs(e), x) / scale)
    predicted_after = float(trap(np.abs(e + d), x) / scale)
    tmp = tempfile.mkdtemp(prefix="f15_plant_e1_")
    try:
        work = os.path.join(tmp, os.path.basename(path))
        if _plant_column(path, work, 1, d) == 0:    # R2: p is column 1
            refuse("nothing to plant into %s: no data rows" % path)
        after = e1_from_xy(work, sol)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs(after - predicted_after) > 1e-12:
        refuse("PLANTED-ZERO CONTROL FAILED for E1 on %s: a p-column offset of "
               "%.6e must move E1 to %.15g by definition; the reader returned "
               "%.15g. The reader has not been shown able to see a plant, so its "
               "values are NOT EVIDENCE." % (path, d, predicted_after, after))
    return RT.external_plant_control("e1_from_xy", before, after,
                                     plant=(predicted_after - before),
                                     artifact=path, level=level)


def plant_control_x_wall(path, level, sol):
    """Shift the x column by a known amount.  The half-rise crossing must move
    by EXACTLY that amount -- an exact, non-asymptotic prediction."""
    d = RT.PLANT
    before = x_wall_from_xy(path, sol)
    tmp = tempfile.mkdtemp(prefix="f15_plant_xw_")
    try:
        work = os.path.join(tmp, os.path.basename(path))
        if _plant_column(path, work, 0, d) == 0:
            refuse("nothing to plant into %s: no data rows" % path)
        after = x_wall_from_xy(work, sol)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs((after - before) - d) > 1e-10:
        refuse("PLANTED-ZERO CONTROL FAILED for x_wall on %s: an x-column shift "
               "of %.6e must move the crossing by exactly that; the reader moved "
               "it %.6e. Its values are NOT EVIDENCE." % (path, d, after - before))
    return RT.external_plant_control("x_wall_from_xy", before, after,
                                     artifact=path, level=level)


# ---------------------------------------------------------------------------
# CLASS C -- all four elements. Element 4 EXITS, it does not return a state.
# ---------------------------------------------------------------------------
def class_c(t, v, label, cfg=None):
    cfg = CLASS_C if cfg is None else cfg
    t = np.asarray(t, dtype=float)
    v = np.asarray(v, dtype=float)

    # ELEMENT 4 -- refusal below a minimum sample count, FIRST, and it exits.
    if v.size < cfg["min_samples"]:
        refuse("CLASS C ELEMENT 4: %s has %d samples; the registered minimum is "
               "%d. NOT A RESULT. A verdict computed from what happened to be on "
               "disk is exactly the defect this limb exists to stop "
               "(CFD_CONVERGENCE_GATE_RULING_2026-08-25.md section 2)."
               % (label, v.size, cfg["min_samples"]))
    w = int(cfg["window"])
    if v.size < w:
        refuse("CLASS C ELEMENT 1: %s has %d samples, fewer than the registered "
               "sustained window of %d" % (label, v.size, w))

    tw, vw = t[-w:], v[-w:]
    scale = max(abs(float(np.mean(vw))), cfg["floor"])
    detail = dict(samples=int(v.size), window=w, window_span=float(tw[-1] - tw[0]),
                  window_mean=float(np.mean(vw)), scale=scale)

    # ELEMENT 2 -- trend fit; a growing or drifting series is rejected.
    slope = float(np.polyfit(tw, vw, 1)[0])
    drift = abs(slope) * (tw[-1] - tw[0]) / scale
    detail.update(fitted_slope=slope, relative_drift_over_window=drift,
                  trend_tol=cfg["trend_tol"])
    if drift > cfg["trend_tol"]:
        return "NOT_PLATEAUED_TREND", detail

    # ELEMENT 3 -- explicit stationarity, able to report NOT stationary.
    h = w // 2
    m1, m2 = float(np.mean(vw[:h])), float(np.mean(vw[h:]))
    s1 = float(np.var(vw[:h])) + cfg["floor"]
    s2 = float(np.var(vw[h:])) + cfg["floor"]
    ratio = s2 / s1
    detail.update(half_mean_first=m1, half_mean_second=m2,
                  half_mean_split=abs(m1 - m2) / scale, stat_tol=cfg["stat_tol"],
                  variance_ratio=ratio, var_ratio_band=cfg["var_ratio"])
    if abs(m1 - m2) / scale > cfg["stat_tol"]:
        return "NOT_STATIONARY_MEAN", detail
    if not (cfg["var_ratio"][0] <= ratio <= cfg["var_ratio"][1]):
        return "NOT_STATIONARY_VARIANCE", detail

    # ELEMENT 1 -- the criterion held across the whole registered window, not at
    # the last sample. That is what the three tests above were applied to.
    return "PLATEAUED", detail


def control_class_c_can_say_no():
    """PLANTED CONTROL on the Class C gate itself.  Three plants, three
    different refusals.  A gate that says PLATEAUED to everything is not a
    gate."""
    n = CLASS_C["min_samples"] + 20
    t = np.arange(n, dtype=float) * SAMPLE_INTERVAL
    flat = np.full(n, 2.5) + 1e-9 * np.sin(np.arange(n))
    ok, _ = class_c(t, flat, "control_flat")
    if ok != "PLATEAUED":
        refuse("CLASS C CONTROL FAILED: a flat series was reported %r, not "
               "PLATEAUED. The gate refuses everything and grades nothing." % ok)
    ramp = flat + 0.02 * t / t[-1]
    grow, _gd = class_c(t, ramp, "control_ramp")
    if grow != "NOT_PLATEAUED_TREND":
        refuse("CLASS C ELEMENT 2 CONTROL FAILED: a series growing by 0.8%% "
               "across the window was reported %r. A trend fit that cannot "
               "reject a growing series is not element 2." % grow)
    step = flat.copy()
    step[-(CLASS_C["window"] // 2):] += 0.01
    stat, _sd = class_c(t, step, "control_step")
    if stat not in ("NOT_STATIONARY_MEAN", "NOT_PLATEAUED_TREND"):
        refuse("CLASS C ELEMENT 3 CONTROL FAILED: a mean shift of 0.4%% across "
               "the window halves was reported %r. The stationarity test cannot "
               "report NOT stationary." % stat)
    probe = ("import sys; sys.path.insert(0, %r)\n"
             "import " + os.path.splitext(os.path.basename(__file__))[0] + " as g\n"
             "import numpy as np\n"
             "t = np.arange(5.0); v = np.ones(5)\n"
             "try:\n"
             "    g.class_c(t, v, 'short')\n"
             "    print('CONTROL_FAILED_NO_REFUSAL')\n"
             "except SystemExit as e:\n"
             "    print('REFUSED' if e.code == 2 else 'WRONG_CODE')\n") % HERE
    p = subprocess.run([sys.executable, "-c", probe], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    if "REFUSED" not in p.stdout.decode():
        refuse("CLASS C ELEMENT 4 CONTROL FAILED: a 5-sample series did not "
               "make class_c exit 2 (got %r). Element 4 is the limb most likely "
               "to be quietly dropped, because dropping it always makes a run "
               "gradeable." % p.stdout.decode().strip())
    return dict(control="PZ-F15-CLASSC_four_limbs_each_shown_able_to_refuse",
                flat="PLATEAUED", ramp=grow, step=stat,
                short_series="exit 2", passed=True)


# ---------------------------------------------------------------------------
# COMPLETION -- standing rule 4, with the registered final-step limb
# ---------------------------------------------------------------------------
TIME_RE = re.compile(r"^Time = ([0-9eE+\-.]+)\s*$", re.MULTILINE)      # R2
DELTAT_RE = re.compile(r"^deltaT = ([0-9eE+\-.]+)", re.MULTILINE)       # R2
CLOCK_RE = re.compile(r"ClockTime = ([0-9]+) s", re.MULTILINE)           # R2: the real
#   line is `ExecutionTime = X s  ClockTime = N s`; the parent's `^ClockTime`
#   could match nothing on a real log even with MULTILINE


def completion(case_dir, log_path):
    """rc, End, the final-step limb, the fields, and the age guard.

    THE LIMB IS `latest + dt_final > endTime`, NOT `latest >= endTime`: the
    latter refused 4 of 9 genuinely complete F4 runs. It is NOT a two-sided
    tolerance either -- choosing an epsilon after seeing which runs it admits is
    the fitted-threshold move this lab has a rule against.

    The `ExecutionTime count == endTime` clause of standing rule 4 is a
    FIXED-deltaT identity. This case runs `adjustTimeStep yes`, so that clause
    cannot hold and is NOT applied; it is replaced by the final-step limb above
    and the substitution is recorded here rather than left silent.
    """
    out = dict(case=case_dir, log=log_path)
    if not os.path.isfile(log_path):
        return dict(out, done=False, why="no solver log at %s" % log_path)
    text = open(log_path, errors="replace").read()
    times = [float(m.group(1)) for m in TIME_RE.finditer(text)]
    dts = [float(m.group(1)) for m in DELTAT_RE.finditer(text)]
    clocks = [int(m.group(1)) for m in CLOCK_RE.finditer(text)]
    out.update(n_times=len(times), latest=times[-1] if times else None,
               dt_final=dts[-1] if dts else None,
               clock_time_s=clocks[-1] if clocks else None,
               end_line="End" in text.splitlines()[-6:] if text else False)
    if not times:
        return dict(out, done=False, why="no `Time =` lines in the log")
    if "End" not in text:
        return dict(out, done=False, why="no `End` line: the solver did not finish")
    if not dts:
        return dict(out, done=False, why="no `deltaT =` lines; the final-step "
                                         "limb cannot be evaluated")
    if not (times[-1] + dts[-1] > END_TIME):
        return dict(out, done=False,
                    why="latest %.9g + dt_final %.9g does not exceed endTime %.9g"
                        % (times[-1], dts[-1], END_TIME))
    zero_t = os.path.join(case_dir, "0", "T")
    if not os.path.isfile(zero_t):
        return dict(out, done=False, why="no 0/T to date the launch against; the "
                                         "age guard cannot be evaluated")
    t0 = os.path.getmtime(zero_t)
    end_dir = None
    for d in os.listdir(case_dir):
        if re.match(r"^[0-9]+(\.[0-9]+)?$", d) and abs(float(d) - END_TIME) < 1e-9:
            end_dir = os.path.join(case_dir, d)
    if end_dir is None:
        return dict(out, done=False, why="no time directory at endTime %g" % END_TIME)
    missing, stale = [], []
    for f in ("T", "U", "p"):
        fp = os.path.join(end_dir, f)
        if not os.path.isfile(fp):
            missing.append(f)
        elif os.path.getmtime(fp) <= t0:
            stale.append(f)
    if missing:
        return dict(out, done=False, why="fields missing at endTime: %s" % missing)
    if stale:
        return dict(out, done=False,
                    why="AGE GUARD: fields %s at endTime are NOT newer than the "
                        "case's own 0/T; they predate the run allowed to produce "
                        "the answer" % stale)
    return dict(out, done=True, why="rc handled by the launcher; End present; "
                                    "latest + dt_final > endTime; T U p present "
                                    "at endTime and all newer than 0/T")


# ---------------------------------------------------------------------------
# R2 DRIVEN CONTROLS -- the two readers on VERBATIM excerpts of the real coarse
# artefacts of run 2aea29d9.  These are the controls the parent never ran.
# ---------------------------------------------------------------------------
REAL_LOG_EXCERPT = 'Starting time loop\n\nSampled set:\n    lineY05 -> raw\n\nSampled set:\n    lineWall -> raw\n\ndeltaT = 0.00299850074963\nMean and max Courant Numbers = 0.510215827174 0.533289371075\nTime = 0.00299850075\n\ndiagonal:  Solving for rho, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoUx, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoUy, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoE, Initial residual = 0, Final residual = 0, No Iterations 0\nExecutionTime = 0.15 s  ClockTime = 1 s\n\ndeltaT = 0.00112443778111\nMean and max Courant Numbers = 0.191315857627 0.199627356965\nTime = 0.004122938531\n\ndiagonal:  Solving for rho, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoUx, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoUy, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoE, Initial residual = 0, Final residual = 0, No Iterations 0\nExecutionTime = 0.16 s  ClockTime = 1 s\n\ndeltaT = 0.00112634145681\nMean and max Courant Numbers = 0.191648881031 0.199912511779\nTime = 0.005249279988\n\ndiagonal:  Solving for rho, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoUx, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoUy, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoE, Initial residual = 0, Final residual = 0, No Iterations 0\nExecutionTime = 0.17 s  ClockTime = 1 s\n\ndeltaT = 0.00112697780792\nMean and max Courant Numbers = 0.191772847403 0.199889702883\nTime = 0.006376257795\n\n\ndiagonal:  Solving for rho, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoUx, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoUy, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoE, Initial residual = 0, Final residual = 0, No Iterations 0\nExecutionTime = 67.56 s  ClockTime = 68 s\n\ndeltaT = 0.00113636363636\nMean and max Courant Numbers = 0.188630571939 0.201103314184\nTime = 10\n\ndiagonal:  Solving for rho, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoUx, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoUy, Initial residual = 0, Final residual = 0, No Iterations 0\ndiagonal:  Solving for rhoE, Initial residual = 0, Final residual = 0, No Iterations 0\nExecutionTime = 67.58 s  ClockTime = 68 s\n\nEnd\n\n\n'
REAL_LOG_EXCERPT_COUNTS = dict(time=5, deltaT=5, clock=5, end=1)
REAL_XY_EXCERPT = '-1.99 \t0.714285714286\n-1.97 \t0.714285714286\n-1.95 \t0.714285714286\n-1.93 \t0.714285714286\n-1.91 \t0.714285714285\n-1.89 \t0.714285714286\n-1.87 \t0.714285714286\n-1.85 \t0.714285714286\n-1.83 \t0.714285714286\n-1.81 \t0.714285714286\n-1.79 \t0.714285714286\n-1.77 \t0.714285714286\n-0.09 \t3.16647879369\n-0.07 \t3.15759525978\n-0.05 \t3.09873114023\n-0.03 \t3.04442475141\n-0.01 \t3.00347537823\n0.01 \t2.96171203327\n0.03 \t2.941308457\n0.05 \t2.92174540974\n0.07 \t2.90270423731\n0.09 \t2.8969513708\n0.11 \t2.89479438512\n0.13 \t2.89435032798\n0.15 \t2.89915658766\n0.17 \t2.91540577006\n0.19 \t2.92941540155\n1.77 \t2.92840420923\n1.79 \t2.92652693323\n1.81 \t2.92622644129\n1.83 \t2.92668184457\n1.85 \t2.9274838609\n1.87 \t2.92943982268\n1.89 \t2.93360244922\n1.91 \t2.93697886263\n1.93 \t2.93756287616\n1.95 \t2.93758900254\n1.97 \t2.93684305224\n1.99 \t2.93288955692\n'
REAL_XY_EXCERPT_ROWS = 39


def control_completion_reads_a_real_log():
    tmp = tempfile.mkdtemp(prefix="f15_r2_reallog_")
    try:
        case = os.path.join(tmp, "coarse")
        os.makedirs(os.path.join(case, "0"))
        os.makedirs(os.path.join(case, "%g" % END_TIME))
        open(os.path.join(case, "0", "T"), "w").write("planted\n")
        for f in ("T", "U", "p"):
            open(os.path.join(case, "%g" % END_TIME, f), "w").write("planted\n")
        log = os.path.join(case, "log.rhoCentralFoam")
        open(log, "w").write(REAL_LOG_EXCERPT)
        counts = dict(time=len(TIME_RE.findall(REAL_LOG_EXCERPT)),
                      deltaT=len(DELTAT_RE.findall(REAL_LOG_EXCERPT)),
                      clock=len(CLOCK_RE.findall(REAL_LOG_EXCERPT)),
                      end=REAL_LOG_EXCERPT.split("\n").count("End"))
        parent_form = len(re.findall(r"^Time = ([0-9eE+\-.]+)\s*$", REAL_LOG_EXCERPT))
        pos = completion(case, log)
        neg_text = "\n".join(l for l in REAL_LOG_EXCERPT.split("\n")
                             if not l.startswith("Time = ")) + "\n"
        open(log, "w").write(neg_text)
        neg = completion(case, log)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if parent_form != 0:
        refuse("REAL-LOG CONTROL: the parent's anchored, non-MULTILINE form saw "
               "%d lines on this excerpt; the defect this file exists to repair "
               "is not reproduced, so the excerpt is not the real log shape"
               % parent_form)
    if counts != REAL_LOG_EXCERPT_COUNTS:
        refuse("REAL-LOG CONTROL FAILED: readers counted %s on a verbatim excerpt "
               "that carries %s. The readers have not been shown able to see the "
               "lines they grade on." % (counts, REAL_LOG_EXCERPT_COUNTS))
    if (not pos["done"] or pos["n_times"] != REAL_LOG_EXCERPT_COUNTS["time"]
            or pos["latest"] != END_TIME
            or pos["clock_time_s"] is None or pos["dt_final"] is None):
        refuse("REAL-LOG CONTROL FAILED: completion() on the excerpt returned %r"
               % pos)
    if neg["done"] or neg["n_times"] != 0 or "no `Time =` lines" not in neg["why"]:
        refuse("REAL-LOG NEGATIVE CONTROL FAILED: with the `Time =` lines removed "
               "the reader said %r" % neg["why"])
    return dict(control="PZ-F15-R2-REAL_LOG_EXCERPT_completion_reader_driven_both_ways",
                excerpt_source="verification/runs/F15_runs/coarse/log.rhoCentralFoam",
                planted=REAL_LOG_EXCERPT_COUNTS, counted=counts,
                parent_form_without_MULTILINE_count=parent_form,
                completion_positive=dict(done=pos["done"], n_times=pos["n_times"],
                                         latest=pos["latest"],
                                         dt_final=pos["dt_final"],
                                         clock_time_s=pos["clock_time_s"]),
                negative_why=neg["why"], passed=True)


def control_sample_reader_on_real_xy():
    """read_xy_p on a verbatim excerpt of the real 2-column lineWall_p.xy, and
    a negative: the same rows re-written in the parent's 4-column pin must be
    REFUSED, so the pin is shown to discriminate rather than accept anything."""
    tmp = tempfile.mkdtemp(prefix="f15_r2_realxy_")
    try:
        f = os.path.join(tmp, "lineWall_p.xy")
        open(f, "w").write(REAL_XY_EXCERPT)
        x, p = read_xy_p(f)
        four = os.path.join(tmp, "four_col.xy")
        with open(four, "w") as out:
            for xi, pi in zip(x, p):
                out.write("%.12g %.12g %.12g %.12g\n" % (xi, EX.SAMPLE_Y, 0.0, pi))
        probe = ("import sys; sys.path.insert(0, %r)\n"
                 "import " + os.path.splitext(os.path.basename(__file__))[0] + " as g\n"
                 "try:\n"
                 "    g.read_xy_p(%r)\n"
                 "    print('CONTROL_FAILED_NO_REFUSAL')\n"
                 "except SystemExit as e:\n"
                 "    print('REFUSED' if e.code == 2 else 'WRONG_CODE')\n") % (HERE, four)
        pr = subprocess.run([sys.executable, "-c", probe], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if x.size != REAL_XY_EXCERPT_ROWS:
        refuse("REAL-XY CONTROL FAILED: read_xy_p returned %d rows from a verbatim "
               "excerpt of %d" % (x.size, REAL_XY_EXCERPT_ROWS))
    if not (float(p.max()) > 2.0 * float(p.min())):
        refuse("REAL-XY CONTROL FAILED: the excerpt spans the wall shock jump "
               "(min %g max %g on disk) but the reader returned p in [%g, %g]"
               % (0.714285714285, 3.16647879369, p.min(), p.max()))
    if "REFUSED" not in pr.stdout.decode():
        refuse("REAL-XY NEGATIVE CONTROL FAILED: a 4-column file was not refused "
               "(got %r)" % pr.stdout.decode().strip())
    return dict(control="PZ-F15-R2-REAL_XY_EXCERPT_read_xy_p_driven_both_ways",
                excerpt_source="verification/runs/F15_runs/coarse/postProcessing/"
                               "lineWall/9.95/lineWall_p.xy",
                rows=int(x.size), p_min=float(p.min()), p_max=float(p.max()),
                x_first=float(x[0]), x_last=float(x[-1]),
                negative="4-column layout refused (exit 2)", passed=True)


# ---------------------------------------------------------------------------
# THE AST CENSUS AND THE grade_ladder CALL-SITE CONTROL
# ---------------------------------------------------------------------------
def ast_no_asserts(paths):
    bad = {}
    for p in paths:
        lines = [n.lineno for n in ast.walk(ast.parse(open(p).read()))
                 if isinstance(n, ast.Assert)]
        if lines:
            bad[p] = lines
    if bad:
        refuse("`assert` carries a check in this rung's own path and `python3 -O` "
               "deletes every one (L-332): %s" % json.dumps(bad))
    return dict(files_checked=len(paths), assert_nodes=0)


def control_grade_ladder_is_called():
    """PLANTED CONTROL on the claim `this path calls grade_ladder`.

    The census is done by AST, not by grep: a regex counts prose. Line 433 of an
    earlier draft of this file was a COMMENT saying "the one and only gate call"
    and a naive matcher counted it as a third gate. The AST counts CALL NODES.

    The grep is then driven separately, BOTH WAYS, on two synthetic files -- one
    with no call and one with a planted call -- so that the textual evidence a
    reader can reproduce from a terminal is itself shown able to miss and to hit.
    """
    src = open(os.path.abspath(__file__)).read()
    calls = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "grade_ladder":
            calls.append(node.lineno)
    if len(calls) != 1:
        refuse("expected EXACTLY ONE grade_ladder CALL NODE in this file; found "
               "%d at lines %s. More than one is a second gate; zero is the "
               "887ddfaf defect." % (len(calls), calls))

    pat = re.compile(r"RT\.grade_ladder\s*\(")
    grep_hits = [i + 1 for i, ln in enumerate(src.splitlines()) if pat.search(ln)]
    tmp = tempfile.mkdtemp(prefix="f15_gl_control_")
    try:
        neg = os.path.join(tmp, "no_call.py")
        open(neg, "w").write("def f():\n    return 1\n")
        if [i for i, ln in enumerate(open(neg).read().splitlines())
                if pat.search(ln)]:
            refuse("GREP CONTROL FAILED: the matcher found a grade_ladder call "
                   "in a file that has none. Its hits mean nothing.")
        pos = os.path.join(tmp, "yes_call.py")
        open(pos, "w").write("import x as RT\ndef f():\n"
                             "    return RT.grade_ladder(q, l, d, b, p)\n")
        if not [i for i, ln in enumerate(open(pos).read().splitlines())
                if pat.search(ln)]:
            refuse("GREP CONTROL FAILED: the matcher MISSED a planted "
                   "grade_ladder call. Its misses mean nothing.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(control="PZ-F15-GRADE_LADDER_CALLSITE_ast_census_plus_grep_both_ways",
                ast_call_nodes=calls, grep_lines=grep_hits,
                grep_lines_note=("grep also matches prose in this file; the AST "
                                 "census is the binding count"),
                negative_control="miss on a file with no call",
                positive_control="hit on a planted call", passed=True)


# ---------------------------------------------------------------------------
# BANDS -- derived from a stated principle, never from a measured deviation
# ---------------------------------------------------------------------------
def bands(sol):
    """Both bands descend from ONE declared parameter, N_CAPTURE_CELLS = 8.

    G-F15-1 (E1).  A conservative scheme smears a discontinuity over at least
    one cell.  A step of height dp reproduced as a monotone linear ramp of width
    n*dx contributes exactly  n * dp * dx / 4  to Int|p_num - p_exact|.  Two
    discontinuities cross y = 0.5, so the normalised L1 error of a scheme that
    is otherwise EXACT is

        E1(n) = n * dx * (dp_incident + dp_reflected) / (4 * L * p1)
              = n * dx * c,          c = L1_floor_per_dx, computed in exact_osr

    The band is [E1(1), E1(N_CAPTURE_CELLS)] at the FINEST spacing: below one
    cell is impossible for a conservative scheme, above eight cells is more
    smearing than the declared allowance.

    G-F15-2 (x_wall).  The same allowance in the same units: a shock whose
    captured profile is n cells wide places its half-rise crossing no better
    than +/- (n/2) * dx.  The band is the exact impingement +/- that.
    """
    dx_f = DX["fine"]
    c = sol["L1_floor_per_dx"]
    e1 = (1.0 * dx_f * c, N_CAPTURE_CELLS * dx_f * c)
    half = 0.5 * N_CAPTURE_CELLS * dx_f
    xw = sol["x_wall_impingement"]
    return {
        "G-F15-1_E1_pressure_L1_y0.5": dict(
            band=e1, reference=0.0, dim=DIM,
            principle=("one-cell conservative smearing floor x [1, %d] declared "
                       "capture cells; c = (dp_i + dp_r)/(4 L p1) = %.12f, "
                       "dx_fine = %g" % (N_CAPTURE_CELLS, c, dx_f))),
        "G-F15-2_x_wall_impingement": dict(
            band=(xw - half, xw + half), reference=xw, dim=DIM,
            principle=("exact impingement %.12f +/- (N_CAPTURE_CELLS/2)*dx_fine "
                       "= +/- %.12f" % (xw, half))),
    }


# ---------------------------------------------------------------------------
# THE DEMONSTRATION -- each gate quantity shown able to take a FAILING and a
# PASSING value, through the real reader, on a file in the real write format
# ---------------------------------------------------------------------------
def synth_xy(path, x, p):
    with open(path, "w") as f:
        for xi, pi in zip(x, p):
            f.write("%.12g \t%.12g\n" % (xi, pi))   # R2: the real 2-column shape


def smeared_profile(x, sol, n_cells, dx, on_wall=False):
    """The exact solution with each discontinuity replaced by a monotone linear
    ramp of width n_cells * dx -- the ideal captured solution."""
    if on_wall:
        edges = [(sol["x_wall_impingement"], sol["region1"]["p"],
                  sol["region3"]["p"])]
    else:
        edges = [(sol["x_incident_at_sample_y"], sol["region1"]["p"],
                  sol["region2"]["p"]),
                 (sol["x_reflected_at_sample_y"], sol["region2"]["p"],
                  sol["region3"]["p"])]
    out = np.empty_like(x)
    for i, xi in enumerate(x):
        val = edges[0][1]
        for x0, lo, hi in edges:
            wdt = max(n_cells * dx, 1e-15)
            if xi <= x0 - wdt / 2.0:
                pass
            elif xi >= x0 + wdt / 2.0:
                val = hi
            else:
                val = lo + (hi - lo) * ((xi - (x0 - wdt / 2.0)) / wdt)
        out[i] = val
    return out


def demonstrate(sol, bnd):
    """ZERO COMPUTE. Builds files in the pinned `sets`/raw layout and drives the
    real readers over them, once inside the band and once outside, so that
    neither gate is bound to a quantity that can only ever take one value.
    That class has bitten VMFL059, F12's P4, F11's C4 and F5c's M4."""
    tmp = tempfile.mkdtemp(prefix="f15_demo_")
    rows = []
    try:
        dx = DX["fine"]
        x = np.arange(EX.X_MIN + dx / 2.0, EX.X_MAX, dx)

        for n_cells, want in ((1, "inside"), (60, "outside")):
            p = smeared_profile(x, sol, n_cells, dx)
            f = os.path.join(tmp, "lineY05_p.xy")
            synth_xy(f, x, p)
            val = e1_from_xy(f, sol)
            lo, hi = bnd["G-F15-1_E1_pressure_L1_y0.5"]["band"]
            rows.append(dict(gate="G-F15-1_E1_pressure_L1_y0.5",
                             construction="ideal capture over %d cells" % n_cells,
                             value=val, band=[lo, hi],
                             inside=bool(lo <= val <= hi), intended=want))

        for shift, want in ((0.0, "inside"), (0.35, "outside")):
            xw = sol["x_wall_impingement"]
            sol2 = dict(sol)
            sol2["x_wall_impingement"] = xw + shift
            p = smeared_profile(x, sol2, 3, dx, on_wall=True)
            f = os.path.join(tmp, "lineWall_p.xy")
            synth_xy(f, x, p)
            val = x_wall_from_xy(f, sol)
            lo, hi = bnd["G-F15-2_x_wall_impingement"]["band"]
            rows.append(dict(gate="G-F15-2_x_wall_impingement",
                             construction="impingement displaced by %g" % shift,
                             value=val, band=[lo, hi],
                             inside=bool(lo <= val <= hi), intended=want))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for r in rows:
        if (r["intended"] == "inside") != r["inside"]:
            refuse("GATE DEMONSTRATION FAILED for %s: a construction intended to "
                   "land %s the band returned %.6g against band %s. A gate that "
                   "cannot take both values is not a gate."
                   % (r["gate"], r["intended"], r["value"], r["band"]))
    seen = set((r["gate"], r["inside"]) for r in rows)
    for g in bnd:
        if (g, True) not in seen or (g, False) not in seen:
            refuse("gate %s was not shown able to take BOTH a passing and a "
                   "failing value" % g)
    return rows


# ---------------------------------------------------------------------------
# THE GRADE
# ---------------------------------------------------------------------------
SETS = {"G-F15-1_E1_pressure_L1_y0.5": ("lineY05", e1_from_xy, plant_control_e1),
        "G-F15-2_x_wall_impingement": ("lineWall", x_wall_from_xy,
                                       plant_control_x_wall)}


def numeric_time_dirs(root):
    """Numeric-sorted, never lexicographic -- '9' before '10' has bitten this
    lab before (instrument.py::numeric_time_dirs)."""
    if not os.path.isdir(root):
        return []
    out = []
    for d in os.listdir(root):
        if re.match(r"^[0-9]+(\.[0-9]+)?$", d):
            out.append((float(d), os.path.join(root, d)))
    out.sort(key=lambda t: t[0])
    return out


def series_for(case_dir, set_name, reader, sol):
    """The plateau series: the GRADED QUANTITY itself, recomputed at every
    sampled time from that time's own artifact. Not a proxy."""
    root = os.path.join(case_dir, "postProcessing", set_name)
    ts, vs, last = [], [], None
    for t, d in numeric_time_dirs(root):
        f = os.path.join(d, "%s_p.xy" % set_name)
        if not os.path.isfile(f):
            continue
        ts.append(t)
        vs.append(reader(f, sol))
        last = f
    if last is None:
        refuse("no sampled %s files under %s. The gate quantity is ABSENT."
               % (set_name, root))
    return ts, vs, last


def iterative_series(case_dir):
    """The whole-field monitor, DISTINCT from the graded functional: the
    volume-averaged pressure, written by a `volFieldValue` functionObject.

    rhoCentralFoam on an INVISCID case performs no linear solves, so there is no
    solver residual to read and rule 5 limb (1) cannot be answered from one.
    Saying so and measuring a whole-field steady-state monitor instead is the
    honest answer; reporting an absent residual as CONVERGED would not be.
    """
    root = os.path.join(case_dir, "postProcessing", "pAvg")
    ts, vs = [], []
    for _t, d in numeric_time_dirs(root):
        f = os.path.join(d, "volFieldValue.dat")
        if not os.path.isfile(f):
            continue
        for line in open(f):
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            ts.append(float(parts[0]))
            vs.append(float(parts[-1]))
    if not ts:
        refuse("no volume-averaged pressure monitor under %s; rule 5 limb (1) "
               "cannot be evaluated and an UNEVALUATED step is not a passed one."
               % root)
    order = np.argsort(np.asarray(ts))
    return list(np.asarray(ts)[order]), list(np.asarray(vs)[order])


def grade_one(root, gate, sol, bnd):
    set_name, reader, planter = SETS[gate]
    levels, detail = [], []
    for name, _nx, _ny in LEVELS:
        case_dir = os.path.join(root, name)
        if not os.path.isdir(case_dir):
            return dict(gate=gate, verdict="PENDING",
                        note="level %r absent from %s" % (name, root))
        comp = completion(case_dir, os.path.join(case_dir, "log.rhoCentralFoam"))
        if not comp["done"]:
            return dict(gate=gate, verdict="PENDING",
                        note="level %r is not complete: %s" % (name, comp["why"]),
                        completion=comp)
        ts, vs, last = series_for(case_dir, set_name, reader, sol)
        it_t, it_v = iterative_series(case_dir)
        it_state, it_detail = class_c(it_t, it_v, "%s/%s volAvg(p)" % (name, gate))
        pl_state, pl_detail = class_c(ts, vs, "%s/%s" % (name, gate))
        levels.append(dict(name=name, cells=CELLS[name], value=vs[-1]))
        detail.append(dict(name=name, cells=CELLS[name], value=vs[-1],
                           artifact=last, dx=DX[name], completion=comp,
                           iterative=it_state, iterative_detail=it_detail,
                           plateau=pl_state, plateau_detail=pl_detail))

    pc = planter(detail[-1]["artifact"], detail[-1]["name"], sol)
    spec = bnd[gate]

    # ---- THE ONE AND ONLY GATE CALL. Rule 5 is reached here and nowhere else.
    row = RT.grade_ladder(
        quantity=gate,
        levels=levels,
        dim=spec["dim"],
        band=spec["band"],
        plant_control=pc,
        iterative_states=dict((d["name"], "CONVERGED" if d["iterative"] == "PLATEAUED"
                               else d["iterative"]) for d in detail),
        plateau_states=dict((d["name"], d["plateau"]) for d in detail),
        reference=spec["reference"])

    row["gate"] = gate
    row["band_principle"] = spec["principle"]
    row["levels_detail"] = detail
    row["gated_by"] = ("scripts/roache_triple.py::grade_ladder -- rule 5 is "
                       "reached through this call and through nothing else")
    if row["verdict"] not in VERDICTS:
        refuse("%s produced a verdict outside the fixed vocabulary: %r"
               % (gate, row["verdict"]))
    return row


def selftest_predicate(controls, demo, census):
    if census["assert_nodes"] != 0:
        return False, "assert nodes present in this rung's path"
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if len(demo) != 4:
        return False, "expected 4 demonstration rows, got %d" % len(demo)
    if not __debug__:
        return False, "running under -O"
    return True, ("%d controls green; both gate quantities shown able to take a "
                  "passing AND a failing value through the real reader on the "
                  "real write format; 0 assert nodes; exactly one grade_ladder "
                  "call site, with the matcher driven both ways; __debug__ True"
                  % len(controls))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs",
                                                   "F15_runs"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--prereg-commit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    census = ast_no_asserts([os.path.abspath(__file__),
                             os.path.join(HERE, "exact_osr.py")])
    sol = EX.solve()
    controls = [EX.control_paper_agreement(sol),
                EX.control_rankine_hugoniot(sol),
                EX.control_geometry_in_domain(sol),
                control_class_c_can_say_no(),
                control_grade_ladder_is_called(),
                control_completion_reads_a_real_log(),
                control_sample_reader_on_real_xy()]
    bnd = bands(sol)
    demo = demonstrate(sol, bnd)

    if a.selftest:
        ok, why = selftest_predicate(controls, demo, census)
        print(json.dumps(dict(assert_census=census, controls=controls,
                              bands=dict((k, dict(band=v["band"],
                                                  reference=v["reference"],
                                                  principle=v["principle"]))
                                         for k, v in bnd.items()),
                              gate_demonstration=demo,
                              write_path=WRITE_PATH_NOTE,
                              predicate=dict(ok=ok, why=why)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        # THE CLAIM IS INSIDE THE PASSING BRANCH.
        print("\nSELFTEST GREEN -- %s" % why)
        return 0

    if not a.prereg_commit:
        refuse("--prereg-commit is required for a real grade (rule 2: the "
               "grading path is fixed at the pre-registration commit)")
    rows = [grade_one(a.root, g, sol, bnd) for g in sorted(SETS)]
    infra, defects = infrastructure_census(a.root)
    out = a.out or os.path.join(a.root, "F15_R2_GRADED.json")
    report = dict(rung="F15-OSR29-R2", parent_grader_blob='e4076c03ca68d67e8247f73a4038d179cd7a20f2',
                  prereg_commit=a.prereg_commit,
                  prereg=("verification/campaign/"
                          "F15_OSR29_R2_PREREGISTRATION.md"),
                  field_classes=dict(physics_critical=PHYSICS_CRITICAL,
                                     infrastructure=INFRASTRUCTURE),
                  infrastructure_census=infra, bookkeeping_defects=defects,
                  assert_census=census, controls=controls,
                  gate_demonstration=demo, write_path=WRITE_PATH_NOTE,
                  cap_core_min=CAP_CORE_MIN, rows=rows)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print("F15-R2 -- OBLIQUE SHOCK REFLECTION M=2.9 -- TALLY (L-342 re-registration)")
    print("=" * 78)
    for r in rows:
        print("%-40s %s" % (r["gate"], r["verdict"]))
        if "why" in r:
            print("    %s" % r["why"])
        if "note" in r:
            print("    %s" % r["note"])
    for d in defects:
        print("    %s" % d)
    print("=" * 78)
    print("gated by: scripts/roache_triple.py::grade_ladder")
    print("written: %s" % out)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RT.Refusal as e:
        sys.stderr.write("REFUSED (roache_triple): %s\n" % e)
        sys.exit(2)
