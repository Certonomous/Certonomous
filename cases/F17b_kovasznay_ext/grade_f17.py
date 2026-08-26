#!/usr/bin/env python3
"""
F17 -- THE GRADING PATH for Kovasznay flow (simpleFoam, steady, Re = 40).
It calls `scripts/roache_triple.py::grade_ladder` and rule 5 is reached through
that call and through NOTHING ELSE.  Exactly one call node, censused by AST at
every entry.

REFUSAL DISCIPLINE: `raise` / `sys.exit(2)` only.  ZERO `assert` statements,
checked by AST parse across this file, exact_f17.py, foam_io_f17.py and
build_f17.py (L-332).  `grade_ladder` reaches its own gate through asserts in
the SHARED roache_triple.py which `python3 -O` deletes; that file is not this
team's to edit, so THIS FILE REFUSES TO RUN UNDER `-O` at entry.

CONVERGENCE IS CLASS C (CFD_CONVERGENCE_GATE_RULING_2026-08-25.md section 2),
all four elements, on the GRADED QUANTITY ITSELF sampled at every written
checkpoint (100 iterations apart); element 4 exits rather than returning a
state.  Rule 5 limb (1) is a CENSUS over every iteration in the Class C
window of the solver's own initial residuals for Ux, Uy and p.
"""
import sys

if not __debug__:
    sys.stderr.write(
        "REFUSED: grade_f17.py must not run under `python3 -O`.\n"
        "  -O deletes every `assert`, including the _seal invariants in the shared\n"
        "  roache_triple.py (verdict vocabulary, one-way gate, no GCI on a\n"
        "  non-monotone triple).  With those deleted, rule 1 and rule 5 are not\n"
        "  enforced by anything.\n")
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
import exact_f17 as EX                  # THE EXACT SOLUTION and the discretisation model.
import foam_io_f17 as FIO               # THE READERS.

DIM = 2                                 # refinement in BOTH directions, r = 2 exactly
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
LEVEL_NAMES = [n for n, _nx, _ny in EX.LEVELS]
CELLS = dict((n, nx * ny) for n, nx, ny in EX.LEVELS)
SHAPE = dict((n, (nx, ny)) for n, nx, ny in EX.LEVELS)
END_TIME = EX.N_ITER
DT = 1.0
WRITE_EVERY = EX.WRITE_EVERY

# THE ONE DECLARED PARAMETER BOTH BANDS ARE BUILT FROM: the multiplicative
# window around the discretisation-derived prediction in exact_f17.  Declared
# before any run; not fitted, not measured, not revisable after first compute.
BAND_FACTOR = 3.0

# Rule 5 limb (1): thresholds for the solver's own INITIAL residuals, censused
# over every iteration inside the Class C window.  Registered here.
P_RES_TOL = 1.0e-5
U_RES_TOL = 1.0e-6

CAP_CORE_MIN = 150.0                    # ClockTime s * ranks / 60, summed over levels (F17b)

# ---------------------------------------------------------------------------
# L-342 (Sanaa, verbatim): "a bookkeeping failure invalidates the bookkeeping,
# never the physics artifacts -- and graders must separate physics-critical
# fields from infrastructure fields so a dead poller can never void a run
# again."  TWO EXPLICIT FIELD CLASSES.  Gates and refusals (exit 2) read
# PHYSICS_CRITICAL only.  A missing or inconsistent INFRASTRUCTURE field prints
# a `BOOKKEEPING DEFECT` line beside the verdict and refuses the COST CLAIM
# only; it can never produce NOT A RESULT.
# ---------------------------------------------------------------------------
PHYSICS_CRITICAL = (
    "log.simpleFoam `End` line and `Time =` count",   # solver finished, fixed-count identity
    "RC.txt (solver rc, written by the launcher in the same shell the solver ran in)",
    "<endTime>/U and <endTime>/p present and NEWER than 0/U (age guard)",
    "0/C cell centres (the gate quantity is undefined without them)",
    "checkpoint U files (the gate quantity and the Class C series)",
    "initial residuals Ux/Uy/p in log.simpleFoam (rule 5 limb 1 census)",
)
INFRASTRUCTURE = (
    "ClockTime in log.simpleFoam (cost actual)",
    "box_before.txt / box_after.txt (load and memory probes)",
    "MESH_LINE.txt (recorded mesh-quality reading; the gate is enforced at build time)",
    "STATUS.* / launcher.queue.out / LAUNCH_LOG rows written by a queue runner",
    "calibration figures derived from any of the above",
)
RANKS = dict(coarse=1, medium=1, fine=1)

CLASS_C = dict(
    min_samples=20,      # element 4: 20 of the 40 checkpoints
    window=12,           # element 1: 12 checkpoints = 1200 iterations. Justified,
                         #   not inherited: SIMPLE at alpha_U = 0.7 / alpha_p = 0.3
                         #   contracts a slowly-decaying mode by roughly 1-alpha_p
                         #   per sweep at worst, so 1200 sweeps is > 400 e-foldings
                         #   of the slowest relaxation mode; a surviving transient
                         #   cannot hide inside the window.
    trend_tol=2.0e-4,
    stat_tol=1.0e-4,
    var_ratio=(0.2, 5.0),
    floor=1.0e-14,
)

WRITE_PATH_NOTE = (
    "OpenFOAM ascii volVectorField `U` written by the solver at every "
    "checkpoint: `internalField nonuniform List<vector>` NEWLINE N NEWLINE `(` "
    "one `(ux uy uz)` per line `)`. Layout pinned against REAL solver output "
    "already on this box: verification/runs/ansys_verification/VMFL019/L1_30/5/U "
    "(icoFoam, v2606, 120 cells), which the reader below parses at selftest "
    "as a live control. Cell centres come from the run's own 0/C written by "
    "`postProcess -func writeCellCentres` at build time, never from an assumed "
    "ordering.")
REAL_U_ON_BOX = os.path.join(REPO, "verification", "runs", "ansys_verification",
                             "VMFL019", "L1_30", "5", "U")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# READERS
# ---------------------------------------------------------------------------
def read_centres(case_dir):
    path = os.path.join(case_dir, "0", "C")
    if not os.path.isfile(path):
        refuse("no cell-centre file at %s; the graded quantity needs the mesh's own "
               "centres and is ABSENT without them" % path)
    try:
        C = FIO.read_field(path)
    except FIO.FieldFormatError as e:
        refuse("%s: %s" % (path, e))
    if C["kind"] != "vector" or C["internal"] is None:
        refuse("%s is not a nonuniform vector field" % path)
    return C["internal"][:, 0], C["internal"][:, 1]


def read_U(path):
    if not os.path.isfile(path):
        refuse("no U field at %s" % path)
    try:
        F = FIO.read_field(path)
    except FIO.FieldFormatError as e:
        refuse("%s: %s" % (path, e))
    if F["kind"] != "vector" or F["internal"] is None:
        refuse("%s is not a nonuniform volVectorField. %s" % (path, WRITE_PATH_NOTE))
    if F["internal"].shape[0] < 64:
        refuse("%s has only %d cells; refusing to form an L2 norm over that"
               % (path, F["internal"].shape[0]))
    return F["internal"]


def structured(xc, yc, nx, ny):
    """Map unstructured cell centres onto (ny, nx) index arrays; refuse on any
    collision or gap so a wrong ordering cannot be silently graded."""
    h = EX.h_of(nx)
    ii = np.rint((xc - EX.X0) / h - 0.5).astype(int)
    jj = np.rint((yc - EX.Y0) / h - 0.5).astype(int)
    if np.max(np.abs((xc - EX.X0) / h - 0.5 - ii)) > 1e-6 or np.max(np.abs((yc - EX.Y0) / h - 0.5 - jj)) > 1e-6:
        refuse("cell centres do not sit on the registered uniform %dx%d grid" % (nx, ny))
    if ii.min() < 0 or ii.max() >= nx or jj.min() < 0 or jj.max() >= ny:
        refuse("cell-centre indices outside the %dx%d grid" % (nx, ny))
    flat = jj * nx + ii
    if len(np.unique(flat)) != nx * ny or len(flat) != nx * ny:
        refuse("cell centres do not cover the %dx%d grid exactly once" % (nx, ny))
    return ii, jj


def e2_from_files(u_path, xc, yc):
    """G-F17-1: domain-normalised L2 error of the velocity vector.

        E2 = sqrt( mean over cells |U_h - U_exact|^2 ) / U0
    """
    U = read_U(u_path)
    if U.shape[0] != len(xc):
        refuse("%s carries %d cells but 0/C carries %d" % (u_path, U.shape[0], len(xc)))
    du = U[:, 0] - EX.u_exact(xc, yc)
    dv = U[:, 1] - EX.v_exact(xc, yc)
    return float(math.sqrt(np.mean(du ** 2 + dv ** 2)) / EX.U0)


def u_probe_from_files(u_path, xc, yc, nx, ny):
    """G-F17-2: u/U0 at the registered probe, bilinearly interpolated between
    the four surrounding cell centres."""
    U = read_U(u_path)
    if U.shape[0] != len(xc):
        refuse("%s carries %d cells but 0/C carries %d" % (u_path, U.shape[0], len(xc)))
    ii, jj = structured(xc, yc, nx, ny)
    F = np.empty((ny, nx))
    F[jj, ii] = U[:, 0]
    h = EX.h_of(nx)
    xg = EX.X0 + (np.arange(nx) + 0.5) * h
    yg = EX.Y0 + (np.arange(ny) + 0.5) * h
    return float(EX.bilinear(xg, yg, F, EX.PROBE[0], EX.PROBE[1]) / EX.U0)


# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (standing rule 3) -- into the REAL artifact format,
# read back with the REAL parser, refusing with exit 2.
# ---------------------------------------------------------------------------
def plant_control_e2(u_path, xc, yc, level):
    d = RT.PLANT
    U = read_U(u_path)
    du = U[:, 0] - EX.u_exact(xc, yc)
    dv = U[:, 1] - EX.v_exact(xc, yc)
    before = float(math.sqrt(np.mean(du ** 2 + dv ** 2)) / EX.U0)
    predicted = float(math.sqrt(np.mean((du + d) ** 2 + dv ** 2)) / EX.U0)
    tmp = tempfile.mkdtemp(prefix="f17_plant_e2_")
    try:
        work = os.path.join(tmp, "U")
        if FIO.plant_into_vector_file(u_path, work, 0, d) == 0:
            refuse("nothing to plant into %s" % u_path)
        after = e2_from_files(work, xc, yc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs(after - predicted) > 1e-14:
        refuse("PLANTED-ZERO CONTROL FAILED for E2 on %s: a Ux offset of %.6e must "
               "move E2 to %.17g by definition; the reader returned %.17g. Its values "
               "are NOT EVIDENCE." % (u_path, d, predicted, after))
    return RT.external_plant_control("e2_from_files", before, after,
                                     plant=(predicted - before), artifact=u_path, level=level)


def plant_control_u_probe(u_path, xc, yc, nx, ny, level):
    d = RT.PLANT
    before = u_probe_from_files(u_path, xc, yc, nx, ny)
    tmp = tempfile.mkdtemp(prefix="f17_plant_up_")
    try:
        work = os.path.join(tmp, "U")
        if FIO.plant_into_vector_file(u_path, work, 0, d) == 0:
            refuse("nothing to plant into %s" % u_path)
        after = u_probe_from_files(work, xc, yc, nx, ny)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs((after - before) - d / EX.U0) > 1e-12:
        refuse("PLANTED-ZERO CONTROL FAILED for u(probe) on %s: a Ux offset of %.6e "
               "must move the interpolated value by exactly %.6e; the reader moved it "
               "%.6e." % (u_path, d, d / EX.U0, after - before))
    return RT.external_plant_control("u_probe_from_files", before, after,
                                     plant=d / EX.U0, artifact=u_path, level=level)


# ---------------------------------------------------------------------------
# CLASS C -- four elements; element 4 EXITS
# ---------------------------------------------------------------------------
def class_c(t, v, label, cfg=None):
    cfg = CLASS_C if cfg is None else cfg
    t = np.asarray(t, dtype=float)
    v = np.asarray(v, dtype=float)
    if v.size < cfg["min_samples"]:
        refuse("CLASS C ELEMENT 4: %s has %d samples; the registered minimum is %d. "
               "NOT A RESULT." % (label, v.size, cfg["min_samples"]))
    w = int(cfg["window"])
    if v.size < w:
        refuse("CLASS C ELEMENT 1: %s has %d samples, fewer than the window %d"
               % (label, v.size, w))
    tw, vw = t[-w:], v[-w:]
    scale = max(abs(float(np.mean(vw))), cfg["floor"])
    detail = dict(samples=int(v.size), window=w, window_span=float(tw[-1] - tw[0]),
                  window_mean=float(np.mean(vw)), scale=scale)
    slope = float(np.polyfit(tw, vw, 1)[0])
    drift = abs(slope) * (tw[-1] - tw[0]) / scale
    detail.update(fitted_slope=slope, relative_drift_over_window=drift, trend_tol=cfg["trend_tol"])
    if drift > cfg["trend_tol"]:
        return "NOT_PLATEAUED_TREND", detail
    hh = w // 2
    m1, m2 = float(np.mean(vw[:hh])), float(np.mean(vw[hh:]))
    s1 = float(np.var(vw[:hh])) + cfg["floor"]
    s2 = float(np.var(vw[hh:])) + cfg["floor"]
    ratio = s2 / s1
    detail.update(half_mean_first=m1, half_mean_second=m2, half_mean_split=abs(m1 - m2) / scale,
                  stat_tol=cfg["stat_tol"], variance_ratio=ratio, var_ratio_band=cfg["var_ratio"])
    if abs(m1 - m2) / scale > cfg["stat_tol"]:
        return "NOT_STATIONARY_MEAN", detail
    if not (cfg["var_ratio"][0] <= ratio <= cfg["var_ratio"][1]):
        return "NOT_STATIONARY_VARIANCE", detail
    return "PLATEAUED", detail


def control_class_c_can_say_no():
    n = CLASS_C["min_samples"] + 20
    t = np.arange(1, n + 1, dtype=float) * WRITE_EVERY
    flat = np.full(n, 1.1e-4) + 1e-12 * np.sin(np.arange(n))
    ok, _ = class_c(t, flat, "control_flat")
    if ok != "PLATEAUED":
        refuse("CLASS C CONTROL FAILED: a flat series was reported %r" % ok)
    ramp = flat + 2e-6 * t / t[-1]
    grow, _ = class_c(t, ramp, "control_ramp")
    if grow != "NOT_PLATEAUED_TREND":
        refuse("CLASS C ELEMENT 2 CONTROL FAILED: a drifting series was reported %r" % grow)
    step = flat.copy()
    step[-(CLASS_C["window"] // 2):] += 5e-7
    stat, _ = class_c(t, step, "control_step")
    if stat not in ("NOT_STATIONARY_MEAN", "NOT_PLATEAUED_TREND"):
        refuse("CLASS C ELEMENT 3 CONTROL FAILED: a mean shift was reported %r" % stat)
    probe = ("import sys; sys.path.insert(0, %r)\n"
             "import grade_f17 as g\nimport numpy as np\n"
             "try:\n    g.class_c(np.arange(5.0), np.ones(5), 'short')\n"
             "    print('CONTROL_FAILED_NO_REFUSAL')\n"
             "except SystemExit as e:\n    print('REFUSED' if e.code == 2 else 'WRONG_CODE')\n") % HERE
    p = subprocess.run([sys.executable, "-c", probe], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if "REFUSED" not in p.stdout.decode():
        refuse("CLASS C ELEMENT 4 CONTROL FAILED: a 5-sample series did not exit 2 (got %r)"
               % p.stdout.decode().strip())
    return dict(control="PZ-F17-CLASSC_four_limbs_each_shown_able_to_refuse",
                flat="PLATEAUED", ramp=grow, step=stat, short_series="exit 2", passed=True)


# ---------------------------------------------------------------------------
# ITERATIVE CONVERGENCE -- a CENSUS over every iteration in the Class C window
# ---------------------------------------------------------------------------
INIT_RES_RE = re.compile(r"Solving for (Ux|Uy|p), Initial residual = ([0-9eE+\-.]+)")
TIME_RE = re.compile(r"^Time = ([0-9eE+\-.]+)\s*$", re.M)


def iterative_state(log_path):
    if not os.path.isfile(log_path):
        refuse("no solver log at %s; rule 5 limb (1) cannot be evaluated" % log_path)
    per_iter = []
    cur = None
    for line in open(log_path, errors="replace"):
        m = TIME_RE.match(line)
        if m:
            cur = dict(time=float(m.group(1)))
            per_iter.append(cur)
            continue
        m = INIT_RES_RE.search(line)
        if m and cur is not None:
            cur[m.group(1)] = float(m.group(2))
    n_win = CLASS_C["window"] * WRITE_EVERY
    win = [d for d in per_iter if d["time"] > END_TIME - n_win]
    if len(win) < n_win:
        refuse("only %d iterations inside the %d-iteration census window of %s; an "
               "absent measurement is reported as absent" % (len(win), n_win, log_path))
    bad = dict(Ux=0, Uy=0, p=0)
    worst = dict(Ux=0.0, Uy=0.0, p=0.0)
    for d in win:
        for k, tol in (("Ux", U_RES_TOL), ("Uy", U_RES_TOL), ("p", P_RES_TOL)):
            if k not in d:
                refuse("iteration %g of %s carries no initial residual for %s" % (d["time"], log_path, k))
            worst[k] = max(worst[k], d[k])
            if d[k] > tol:
                bad[k] += 1
    detail = dict(basis="initial residuals of Ux, Uy, p censused over every iteration in "
                        "the Class C window", window_iterations=n_win,
                  tolerances=dict(U=U_RES_TOL, p=P_RES_TOL), n_above_tolerance=bad, worst=worst)
    nb = sum(bad.values())
    if nb:
        return "NOT_CONVERGED_%d_READINGS_ABOVE_TOL" % nb, detail
    return "CONVERGED", detail


# ---------------------------------------------------------------------------
# COMPLETION -- standing rule 4
# ---------------------------------------------------------------------------
def completion(case_dir, log_path):
    out = dict(case=case_dir, log=log_path)
    if not os.path.isfile(log_path):
        return dict(out, done=False, why="no solver log at %s" % log_path)
    text = open(log_path, errors="replace").read()
    times = [float(m.group(1)) for m in TIME_RE.finditer(text)]
    out.update(n_times=len(times), latest=times[-1] if times else None, dt=DT)
    rc_path = os.path.join(case_dir, "RC.txt")
    if not os.path.isfile(rc_path):
        return dict(out, done=False, why="no RC.txt yet: the solver rc is not recorded (run in progress "
                                         "or launcher died before recording it); PENDING, not a verdict")
    rc = open(rc_path).read().strip()
    out["rc"] = rc
    if rc != "0":
        return dict(out, done=False, crashed=True,
                    why="recorded solver rc is %r, not 0: a crash is a FINDING (NOT A RESULT), not a pending run" % rc)
    if not times:
        return dict(out, done=False, crashed=True, why="rc 0 but no `Time =` lines in the log: NOT A RESULT")
    if "End" not in text:
        return dict(out, done=False, crashed=True,
                    why="rc 0 recorded but no `End` line: the solver log and the rc disagree; NOT A RESULT")
    if not (times[-1] + DT > END_TIME):
        return dict(out, done=False, why="latest %g + dt %g does not exceed endTime %g"
                                          % (times[-1], DT, END_TIME))
    if len(times) != END_TIME:
        return dict(out, done=False, why="fixed-deltaT identity fails: %d `Time` lines, endTime/dt = %d"
                                          % (len(times), END_TIME))
    zero_u = os.path.join(case_dir, "0", "U")
    if not os.path.isfile(zero_u):
        return dict(out, done=False, why="no 0/U to date the launch against")
    t0 = os.path.getmtime(zero_u)
    end_dir = None
    for d in os.listdir(case_dir):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and abs(float(d) - END_TIME) < 1e-9:
            end_dir = os.path.join(case_dir, d)
    if end_dir is None:
        return dict(out, done=False, why="no time directory at endTime %g" % END_TIME)
    missing, stale = [], []
    for f in ("U", "p"):
        fp = os.path.join(end_dir, f)
        if not os.path.isfile(fp):
            missing.append(f)
        elif os.path.getmtime(fp) <= t0:
            stale.append(f)
    if missing:
        return dict(out, done=False, why="fields missing at endTime: %s" % missing)
    if stale:
        return dict(out, done=False, why="AGE GUARD: fields %s at endTime are NOT newer than 0/U" % stale)
    return dict(out, done=True, why="rc 0; End present; latest + dt > endTime; %d `Time` lines == endTime; "
                                    "U and p present at endTime and newer than 0/U" % len(times))


# ---------------------------------------------------------------------------
# CENSUSES AND CONTROLS ON THE INSTRUMENT ITSELF
# ---------------------------------------------------------------------------
def ast_no_asserts(paths):
    bad = {}
    for p in paths:
        lines = [n.lineno for n in ast.walk(ast.parse(open(p).read())) if isinstance(n, ast.Assert)]
        if lines:
            bad[p] = lines
    if bad:
        refuse("`assert` carries a check in this rung's own path (L-332): %s" % json.dumps(bad))
    planted = "def f(x):\n    assert x > 0\n    return x\n"
    if sum(1 for n in ast.walk(ast.parse(planted)) if isinstance(n, ast.Assert)) != 1:
        refuse("the assert counter cannot see a planted assert; its zero is not evidence")
    return dict(files_checked=len(paths), assert_nodes=0, planted_assert_seen=True)


def control_grade_ladder_is_called():
    src = open(os.path.abspath(__file__)).read()
    calls = [n.lineno for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "grade_ladder"]
    if len(calls) != 1:
        refuse("expected EXACTLY ONE grade_ladder CALL NODE; found %d at %s" % (len(calls), calls))
    pat = re.compile(r"RT\.grade_ladder\s*\(")
    grep_hits = [i + 1 for i, ln in enumerate(src.splitlines()) if pat.search(ln)]
    if [ln for ln in "def f():\n    return 1\n".splitlines() if pat.search(ln)]:
        refuse("GREP CONTROL FAILED: matcher hit a file with no call")
    if not [ln for ln in "import x as RT\nz = RT.grade_ladder(q)\n".splitlines() if pat.search(ln)]:
        refuse("GREP CONTROL FAILED: matcher MISSED a planted call")
    return dict(control="PZ-F17-GRADE_LADDER_CALLSITE_ast_census_plus_grep_both_ways",
                ast_call_nodes=calls, grep_lines=grep_hits, passed=True)


def control_solver_dicts_match():
    """nu on disk == exact_f17.NU; residualControl ABSENT; endTime and
    writeInterval on disk == the registered values."""
    tp = open(os.path.join(HERE, "case", "constant", "transportProperties")).read()
    m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
    if not m or abs(float(m.group(1)) - EX.NU) > 1e-15:
        refuse("transportProperties nu does not equal exact_f17.NU = %.17g" % EX.NU)
    fs = open(os.path.join(HERE, "case", "system", "fvSolution")).read()
    if re.search(r"^\s*residualControl", fs, re.M):
        refuse("fvSolution carries residualControl; the run must go to endTime so the "
               "Class C series is sampled uniformly")
    cd = open(os.path.join(HERE, "case", "system", "controlDict")).read()
    me = re.search(r"^\s*endTime\s+([0-9]+)\s*;", cd, re.M)
    mw = re.search(r"^\s*writeInterval\s+([0-9]+)\s*;", cd, re.M)
    if not me or int(me.group(1)) != END_TIME:
        refuse("controlDict endTime is not the registered %d" % END_TIME)
    if not mw or int(mw.group(1)) != WRITE_EVERY:
        refuse("controlDict writeInterval is not the registered %d" % WRITE_EVERY)
    return dict(control="solver_dictionaries_agree_with_registration", nu=EX.NU,
                endTime=END_TIME, writeInterval=WRITE_EVERY, residualControl="absent", passed=True)


def control_reader_parses_real_solver_output():
    """The reader is driven on a REAL solver-written U already on this box."""
    if not os.path.isfile(REAL_U_ON_BOX):
        refuse("the real solver output the format is pinned against is absent: %s" % REAL_U_ON_BOX)
    F = FIO.read_field(REAL_U_ON_BOX)
    if F["kind"] != "vector" or F["internal"] is None or F["internal"].shape != (120, 3):
        refuse("reader did not return 120 vectors from %s" % REAL_U_ON_BOX)
    if not np.all(np.isfinite(F["internal"])):
        refuse("reader returned non-finite values from %s" % REAL_U_ON_BOX)
    return dict(control="reader_parses_real_solver_written_U_on_this_box", artifact=REAL_U_ON_BOX,
                cells=120, passed=True)


# ---------------------------------------------------------------------------
# BANDS -- both from ONE declared parameter applied to the model prediction
# ---------------------------------------------------------------------------
def bands():
    tab = dict((r["name"], r) for r in EX.predictions())
    fine = tab["fine"]
    e2p = fine["E2_pred"]
    up = EX.u_probe_exact()
    tol = BAND_FACTOR * abs(fine["probe_err_pred"])
    return {
        "G-F17-1_E2_velocity_L2": dict(
            band=(e2p / BAND_FACTOR, e2p * BAND_FACTOR), reference=0.0, dim=DIM,
            principle=("discretisation-model prediction E2 = %.9e at h_fine = %g (linearised "
                       "discrete equations forced by the exact field's truncation residual), "
                       "times [1/%g, %g]" % (e2p, fine["h"], BAND_FACTOR, BAND_FACTOR))),
        "G-F17-2_u_at_probe": dict(
            band=(up - tol, up + tol), reference=up, dim=DIM,
            principle=("exact u(%g, %g)/U0 = %.15f +/- %g x the model's predicted pointwise "
                       "error there (%.9e) = +/- %.9e" % (EX.PROBE[0], EX.PROBE[1], up, BAND_FACTOR,
                                                           fine["probe_err_pred"], tol))),
    }


# ---------------------------------------------------------------------------
# THE DEMONSTRATION -- both gates shown able to take a failing AND a passing
# value, through the real readers, on files in the pinned write format
# ---------------------------------------------------------------------------
def synth_case(tmp, nx, ny, eu, ev):
    """Write 0/C and a U file (exact + error field) in the real format."""
    h = EX.h_of(nx)
    xg = EX.X0 + (np.arange(nx) + 0.5) * h
    yg = EX.Y0 + (np.arange(ny) + 0.5) * h
    X, Y = np.meshgrid(xg, yg)
    xc, yc = X.ravel(), Y.ravel()
    os.makedirs(os.path.join(tmp, "0"), exist_ok=True)
    C = np.column_stack([xc, yc, np.full(xc.size, 0.5)])
    open(os.path.join(tmp, "0", "C"), "w").write(
        "FoamFile { version 2.0; format ascii; class volVectorField; object C; }\n"
        "dimensions [0 1 0 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
        "boundaryField { inlet { type calculated; value uniform (0 0 0); } }\n" % FIO.fmt_list(C, "vector"))
    U = np.column_stack([EX.u_exact(xc, yc) + eu.ravel(), EX.v_exact(xc, yc) + ev.ravel(), np.zeros(xc.size)])
    up = os.path.join(tmp, "U")
    open(up, "w").write(
        "FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
        "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
        "boundaryField { inlet { type fixedValue; value uniform (0 0 0); } }\n" % FIO.fmt_list(U, "vector"))
    return up, xc, yc


def demonstrate(bnd):
    """ZERO COMPUTE.  F17b: the finest SOLVED grid's error field, prolongated
    (piecewise constant) onto the FINE grid and scaled by the model's solved->fine
    E2 ratio, stands in for the extrapolated fine field -- built AT the fine size
    so the probe's own bilinear interpolation error is the fine level's, not the
    solved grid's (which is 16x larger and would fail the band by itself)."""
    m = EX.solved(*EX.MODEL_GRIDS[-1])
    nx, ny = SHAPE["fine"]
    k = nx // m["nx"]
    if k * m["nx"] != nx or k * m["ny"] != ny:
        refuse("fine grid %dx%d is not an integer refinement of the solved %dx%d" % (nx, ny, m["nx"], m["ny"]))
    ratio = dict((r["name"], r) for r in EX.predictions())["fine"]["E2_pred"] / m["E2_pred"]
    eu, ev = np.kron(m["eu"], np.ones((k, k))), np.kron(m["ev"], np.ones((k, k)))
    rows = []
    tmp = tempfile.mkdtemp(prefix="f17_demo_")
    try:
        for scale, want in ((1.0, "inside"), (40.0, "outside")):
            up, xc, yc = synth_case(tmp, nx, ny, scale * ratio * eu, scale * ratio * ev)
            v1 = e2_from_files(up, xc, yc)
            lo, hi = bnd["G-F17-1_E2_velocity_L2"]["band"]
            rows.append(dict(gate="G-F17-1_E2_velocity_L2", construction="exact + %g x model error field" % scale,
                             value=v1, band=[lo, hi], inside=bool(lo <= v1 <= hi), intended=want))
            v2 = u_probe_from_files(up, xc, yc, nx, ny)
            lo, hi = bnd["G-F17-2_u_at_probe"]["band"]
            rows.append(dict(gate="G-F17-2_u_at_probe", construction="exact + %g x model error field" % scale,
                             value=v2, band=[lo, hi], inside=bool(lo <= v2 <= hi), intended=want))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for r in rows:
        if (r["intended"] == "inside") != r["inside"]:
            refuse("GATE DEMONSTRATION FAILED for %s: construction intended %s returned %.6g against %s"
                   % (r["gate"], r["intended"], r["value"], r["band"]))
    seen = set((r["gate"], r["inside"]) for r in rows)
    for g in bnd:
        if (g, True) not in seen or (g, False) not in seen:
            refuse("gate %s was not shown able to take BOTH values" % g)
    return rows


# ---------------------------------------------------------------------------
# THE GRADE
# ---------------------------------------------------------------------------
def numeric_time_dirs(root):
    out = [(float(d), os.path.join(root, d)) for d in os.listdir(root)
           if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d)]
    out.sort(key=lambda t: t[0])
    return out


def grade_one(root, gate, bnd):
    levels, detail = [], []
    for name in LEVEL_NAMES:
        case_dir = os.path.join(root, name)
        if not os.path.isdir(case_dir):
            return dict(gate=gate, verdict="PENDING", note="level %r absent from %s" % (name, root))
        log = os.path.join(case_dir, "log.simpleFoam")
        comp = completion(case_dir, log)
        if not comp["done"]:
            verdict = "NOT A RESULT" if comp.get("crashed") else "PENDING"
            return dict(gate=gate, verdict=verdict, note="level %r: %s" % (name, comp["why"]), completion=comp)
        xc, yc = read_centres(case_dir)
        nx, ny = SHAPE[name]
        ts, vs, last = [], [], None
        for t, d in numeric_time_dirs(case_dir):
            if t <= 0:
                continue
            up = os.path.join(d, "U")
            if not os.path.isfile(up):
                continue
            ts.append(t)
            if gate == "G-F17-1_E2_velocity_L2":
                vs.append(e2_from_files(up, xc, yc))
            else:
                vs.append(u_probe_from_files(up, xc, yc, nx, ny))
            last = up
        if last is None:
            refuse("no checkpoint U files under %s; the gate quantity is ABSENT" % case_dir)
        it_state, it_detail = iterative_state(log)
        pl_state, pl_detail = class_c(ts, vs, "%s/%s" % (name, gate))
        levels.append(dict(name=name, cells=CELLS[name], value=vs[-1]))
        detail.append(dict(name=name, cells=CELLS[name], value=vs[-1], artifact=last, h=EX.h_of(nx),
                           completion=comp, iterative=it_state, iterative_detail=it_detail,
                           plateau=pl_state, plateau_detail=pl_detail, xc=xc, yc=yc, nx=nx, ny=ny))
    fd = detail[-1]
    if gate == "G-F17-1_E2_velocity_L2":
        pc = plant_control_e2(fd["artifact"], fd["xc"], fd["yc"], fd["name"])
    else:
        pc = plant_control_u_probe(fd["artifact"], fd["xc"], fd["yc"], fd["nx"], fd["ny"], fd["name"])
    for d in detail:
        d.pop("xc"); d.pop("yc")
    spec = bnd[gate]
    # ---- THE ONE AND ONLY GATE CALL.
    row = RT.grade_ladder(
        quantity=gate, levels=levels, dim=spec["dim"], band=spec["band"], plant_control=pc,
        iterative_states=dict((d["name"], d["iterative"]) for d in detail),
        plateau_states=dict((d["name"], d["plateau"]) for d in detail),
        reference=spec["reference"])
    row["gate"] = gate
    row["band_principle"] = spec["principle"]
    row["levels_detail"] = detail
    row["gated_by"] = "scripts/roache_triple.py::grade_ladder -- rule 5 is reached through this call and through nothing else"
    if row["verdict"] not in VERDICTS:
        refuse("%s produced a verdict outside the fixed vocabulary: %r" % (gate, row["verdict"]))
    return row


GATES = ("G-F17-1_E2_velocity_L2", "G-F17-2_u_at_probe")


# ---------------------------------------------------------------------------
# THE COST CLAIM -- INFRASTRUCTURE fields only (L-342).  Never touches a verdict.
# ---------------------------------------------------------------------------
def cost_claim(root):
    """Sum ClockTime x ranks / 60 over the levels present.  Any missing or
    unparseable infrastructure field is a BOOKKEEPING DEFECT: reported, and the
    cost claim is REFUSED (claim=None) -- the physics verdicts are untouched."""
    defects, spent = [], 0.0
    for name in LEVEL_NAMES:
        cd = os.path.join(root, name)
        if not os.path.isdir(cd):
            continue
        log = os.path.join(cd, "log.simpleFoam")
        m = None
        if os.path.isfile(log):
            hits = re.findall(r"ClockTime = ([0-9]+) s", open(log, errors="replace").read())
            m = hits[-1] if hits else None
        if m is None:
            defects.append("BOOKKEEPING DEFECT: level %s has no ClockTime reading in log.simpleFoam; "
                           "cost actual NOT MEASURED" % name)
        else:
            spent += float(m) * RANKS[name] / 60.0
        for probe in ("box_before.txt", "box_after.txt"):
            if not os.path.isfile(os.path.join(cd, probe)):
                defects.append("BOOKKEEPING DEFECT: level %s lacks %s (box probe); NOT MEASURED" % (name, probe))
        if not os.path.isfile(os.path.join(cd, "MESH_LINE.txt")):
            defects.append("BOOKKEEPING DEFECT: level %s lacks MESH_LINE.txt (recorded mesh reading)" % name)
    claim = None if defects else spent
    return dict(fields="INFRASTRUCTURE", core_min_claim=claim, partial_sum_core_min=spent,
                cap_core_min=CAP_CORE_MIN, defects=defects,
                note="derived from ClockTime x ranks / 60; dollars at $0.0513/core-h are DERIVED, NOT MEASURED")


def control_field_classes_separate():
    """L-342 driven both ways in scratch: deleting an INFRASTRUCTURE field
    leaves completion() untouched and produces a defect line; corrupting a
    PHYSICS_CRITICAL field (rc / End) flips the level to NOT A RESULT."""
    tmp = tempfile.mkdtemp(prefix="f17_l342_")
    try:
        cd = os.path.join(tmp, "coarse")
        os.makedirs(os.path.join(cd, "0")); os.makedirs(os.path.join(cd, str(END_TIME)))
        open(os.path.join(cd, "0", "U"), "w").write("x")
        import time as _t
        _t.sleep(0.02)
        body = "".join("Time = %d\n" % i for i in range(1, END_TIME + 1)) + "ClockTime = 7 s\nEnd\n"
        open(os.path.join(cd, "log.simpleFoam"), "w").write(body)
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        for f in ("U", "p"):
            open(os.path.join(cd, str(END_TIME), f), "w").write("y")
        good = completion(cd, os.path.join(cd, "log.simpleFoam"))
        if not good["done"]:
            refuse("L-342 CONTROL: a complete synthetic level was not accepted: %s" % good["why"])
        # infrastructure absent (no box probes, no MESH_LINE): verdict channel unchanged, defect lines present
        cc = cost_claim(tmp)
        again = completion(cd, os.path.join(cd, "log.simpleFoam"))
        if not again["done"] or cc["core_min_claim"] is not None or not cc["defects"]:
            refuse("L-342 CONTROL: missing infrastructure fields did not produce a refused cost claim "
                   "with defect lines while leaving completion untouched")
        # physics-critical corrupted: rc
        open(os.path.join(cd, "RC.txt"), "w").write("134\n")
        bad = completion(cd, os.path.join(cd, "log.simpleFoam"))
        if bad["done"] or not bad.get("crashed"):
            refuse("L-342 CONTROL: a non-zero rc did not flip the level to NOT A RESULT")
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        open(os.path.join(cd, "log.simpleFoam"), "w").write(body.replace("End\n", ""))
        bad2 = completion(cd, os.path.join(cd, "log.simpleFoam"))
        if bad2["done"] or not bad2.get("crashed"):
            refuse("L-342 CONTROL: a missing End line with rc 0 did not flip the level to NOT A RESULT")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(control="PZ-F17-L342_infrastructure_vs_physics_fields_driven_both_ways",
                infrastructure_deleted="verdict channel unchanged, cost claim refused, defect lines printed",
                physics_corrupted="NOT A RESULT", passed=True)


def selftest_predicate(controls, demo, census):
    if census["assert_nodes"] != 0:
        return False, "assert nodes present"
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if len(demo) != 4:
        return False, "expected 4 demonstration rows, got %d" % len(demo)
    if not __debug__:
        return False, "running under -O"
    return True, ("%d controls green; both gate quantities shown able to take a passing AND a "
                  "failing value through the real reader on the pinned write format; 0 assert "
                  "nodes across 4 files; exactly one grade_ladder call node; __debug__ True" % len(controls))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs", "F17b_runs"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--prereg-commit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    census = ast_no_asserts([os.path.abspath(__file__), os.path.join(HERE, "exact_f17.py"),
                             os.path.join(HERE, "foam_io_f17.py"), os.path.join(HERE, "build_f17.py")])
    controls = [EX.control_symbolic_substitution(), EX.control_substitution_is_able_to_fail(),
                EX.control_ladder_is_geometrically_similar(), EX.control_boundary_fluxes_balance(),
                EX.control_model_is_second_order_and_solved(),
                control_class_c_can_say_no(), control_grade_ladder_is_called(),
                control_solver_dicts_match(), control_reader_parses_real_solver_output(),
                control_field_classes_separate()]
    bnd = bands()
    demo = demonstrate(bnd)

    if a.selftest:
        ok, why = selftest_predicate(controls, demo, census)
        print(json.dumps(dict(assert_census=census, controls=controls,
                              bands=dict((k, dict(band=v["band"], reference=v["reference"], principle=v["principle"]))
                                         for k, v in bnd.items()),
                              model_levels=EX.predictions(), gate_demonstration=demo,
                              write_path=WRITE_PATH_NOTE, predicate=dict(ok=ok, why=why)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)      # THE CLAIM IS INSIDE THE PASSING BRANCH.
        return 0

    if not a.prereg_commit:
        refuse("--prereg-commit is required for a real grade (rule 2)")
    rows = [grade_one(a.root, g, bnd) for g in GATES]
    cost = cost_claim(a.root)
    out = a.out or os.path.join(a.root, "F17b_GRADED.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(dict(rung="F17b-KV40-EXT", prereg_commit=a.prereg_commit,
                       prereg="verification/campaign/F17b_KV40_EXT_PREREGISTRATION.md",
                       assert_census=census, controls=controls, gate_demonstration=demo,
                       write_path=WRITE_PATH_NOTE, cap_core_min=CAP_CORE_MIN,
                       field_classes=dict(PHYSICS_CRITICAL=PHYSICS_CRITICAL, INFRASTRUCTURE=INFRASTRUCTURE),
                       cost_claim=cost, rows=rows), f, indent=2, default=str)
    print("F17b -- KOVASZNAY FLOW, LADDER EXTENSION -- TALLY")
    print("=" * 78)
    for r in rows:
        print("%-40s %s" % (r["gate"], r["verdict"]))
        for k in ("why", "note"):
            if k in r:
                print("    %s" % r[k])
    print("=" * 78)
    for dline in cost["defects"]:
        print(dline)
    if cost["core_min_claim"] is None:
        print("COST CLAIM REFUSED (infrastructure fields missing); physics verdicts above are unaffected (L-342)")
    else:
        print("cost actual: %.3f core-min of cap %.1f (ClockTime x ranks / 60; dollars derived, not measured)"
              % (cost["core_min_claim"], CAP_CORE_MIN))
    print("gated by: scripts/roache_triple.py::grade_ladder")
    print("written: %s" % out)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RT.Refusal as e:
        sys.stderr.write("REFUSED (roache_triple): %s\n" % e)
        sys.exit(2)
