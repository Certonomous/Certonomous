#!/usr/bin/env python3
"""
F24 -- THE GRADING PATH for the Prandtl-Meyer corner expansion (rhoCentralFoam,
time-marched to a steady state, M1 = 2, deflection 15 deg, 4 ranks at every
level).  Lineage: cases/F20_ISENTROPIC_VORTEX/grade_f20.py (explicit-solver
limb 1, field readers) and cases/F23_HP_WEDGE/grade_f23.py (processor-directory
readers, Class C plateau).  It calls `scripts/roache_triple.py::grade_ladder`
and rule 5 is reached through that call and through NOTHING ELSE (exactly one
call node, AST-censused).

REFUSAL DISCIPLINE: `raise` / `sys.exit(2)` only; ZERO `assert` across this
file, exact_f24.py, foam_io_f24.py, build_f24.py (L-332); hard `-O` refusal.

THREE QUANTITIES, in the modes exact_f24.GATE_MODE registers (each mode is
ADMITTED by the quantity's sub-ladder triple through roache_triple; a control
in exact_f24 refuses otherwise):
  G-F24-1  p2/p1: volume-weighted box mean of p / p1 in region 2, the PLATEAU-
           WINDOW MEAN over the last CLASS_C["window"] checkpoints.
           GATED-ABSOLUTE: reference +/- 3 x the finest sub-ladder error; NO
           order claim; rule 5 free to return NOT A RESULT on the ladder triple.
  G-F24-2  fan-line L2 error of p: sqrt(sum V (p - p_exact)^2 / sum V) / p1 over
           the column of cells at x = X_LINE + h/2, evaluated on the WINDOW-MEAN
           p FIELD (the captured fan edges oscillate checkpoint to checkpoint
           at the 1e-4 level of p1; the per-checkpoint series is printed with
           its std, ungated).  GATED-EXTRAPOLATED with an order claim.
  R-F24-M  box-mean Mach number in region 2, window mean.  REPORTED-NOT-GATED:
           values, ladder triple and order printed beside the exact M2; NO
           verdict.  Its reader still carries a planted-zero control (rule 3).

THE PLATEAU RULE is a property of the LEVEL (rule 5 limb 1, "any level not
plateaued -> NOT A RESULT"), carried by the physical state quantity p2/p1:
  (i)   Class C on the box-mean p/p1 series (trend, stationarity, variance
        ratio, sample count) with the tolerances below;
  (ii)  a RESIDUAL: the maximum over box cells of |p_k - p_{k-1}| / p1 between
        the last two checkpoints must not exceed RESIDUAL_TOL;
  (iii) a STABILITY CENSUS over every time step's solver-reported max Courant
        number against CO_CEILING, line count == step count, nan/FATAL refusing
        (explicit inviscid rhoCentralFoam has no iterative residual: F15/F19/F20).
(i) and (ii) enter grade_ladder as plateau_states; (iii) as iterative_states;
the same states apply to every quantity read from that level.

L-342: PHYSICS_CRITICAL and INFRASTRUCTURE field classes are declared below;
gates and refusals read the first only; the second can only refuse the cost
claim and print a BOOKKEEPING DEFECT line.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: grade_f24.py must not run under `python3 -O` (the shared "
                     "roache_triple.py seals rule 1 and rule 5 with checks -O would blind).\n")
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

import roache_triple as RT              # THE GATE.
import exact_f24 as EX                  # THE EXACT SOLUTION and the band derivation.
import foam_io_f24 as FIO               # THE READERS.

DIM = 2
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
LEVEL_NAMES = [nm for nm, _n, _s in EX.LEVELS]
NSIDE = dict((nm, n) for nm, n, _s in EX.LEVELS)
CELLS = dict((nm, 2 * n * n) for nm, n, _s in EX.LEVELS)
STEPS = dict((nm, s) for nm, _n, s in EX.LEVELS)
DT = dict((nm, EX.dt_of(s)) for nm, _n, s in EX.LEVELS)
END_TIME = EX.T_END
WRITE_DT = EX.WRITE_DT
N_CHECKPOINTS = int(round(END_TIME / WRITE_DT))
RANKS = dict((nm, EX.RANKS) for nm in LEVEL_NAMES)

BAND_FACTOR = EX.BAND_FACTOR            # the one declared parameter (3)
CO_CEILING = EX.CO_CEILING
RESIDUAL_TOL = 5.0e-3                   # limb (ii): max over box cells |p_k - p_{k-1}| / p1, last two checkpoints
CAP_CORE_MIN = 1450.0
END_FIELDS = ("rho", "U", "p", "T")

CLASS_C = dict(
    min_samples=20,      # of the 40 checkpoints
    window=12,           # t = 2.9 ... 4.0: 1.1 time units = 1.3 flow-through times after 2.9 have elapsed
    trend_tol=3.0e-4,    # relative drift of the fitted line over the window (p/p1 series; 1/64 sub-ladder read 2.5e-5)
    stat_tol=1.5e-4,     # relative half-window mean split (1/64 sub-ladder read 9.3e-6)
    var_ratio=(0.1, 10.0),
    floor=1.0e-14,
)

GATES = ("G-F24-1_p2_over_p1_box_mean", "G-F24-2_p_line_L2_across_fan")
REPORTED = ("R-F24-M2_box_mean",)
QUANTITY_OF = {GATES[0]: "p_box", GATES[1]: "p_line", REPORTED[0]: "M_box"}

PHYSICS_CRITICAL = (
    "log.rhoCentralFoam `End` line and `Time =` count (fixed-deltaT identity)",
    "RC.txt (solver rc, written by the launcher in the shell that ran mpirun)",
    "processor*/<endTime>/rho, U, p, T present in every one of the RANKS directories and NEWER than the serial 0/U (age guard)",
    "processor*/0/C cell centres and processor*/0/V cell volumes",
    "checkpoint p, T, U files (the gate quantities, the plateau series and the residual)",
    "every time step's `max Courant Number` in log.rhoCentralFoam (limb iii stability census)",
)
INFRASTRUCTURE = (
    "ClockTime in log.rhoCentralFoam (cost actual)",
    "box_before.txt / box_after.txt",
    "MESH_LINE.txt",
    "log.decomposePar, log.blockMesh, log.checkMesh, log.build (utility logs)",
    "STATUS.* / launcher.queue.out / LAUNCH_LOG rows written by a queue runner",
    "calibration figures derived from any of the above",
)

WRITE_PATH_NOTE = (
    "OpenFOAM ascii volScalarField `p`, `T` and volVectorField `U` written by the solver at every checkpoint "
    "into each processor<k>/<t>/ directory; `C` (vector) and `V` (scalar) in processor<k>/0/ from postProcess "
    "before decomposePar.  Pinned against REAL rhoCentralFoam output on this box, "
    "verification/runs/F15_runs/coarse/4/{rho,U}, parsed at selftest.")
REAL_RHO_ON_BOX = os.path.join(REPO, "verification", "runs", "F15_runs", "coarse", "4", "rho")
REAL_U_ON_BOX = os.path.join(REPO, "verification", "runs", "F15_runs", "coarse", "4", "U")
REAL_CELLS = 10000


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# READERS -- concatenation over processor directories
# ---------------------------------------------------------------------------
def processor_dirs(case_dir, ranks):
    dirs = sorted([d for d in os.listdir(case_dir) if re.fullmatch(r"processor[0-9]+", d)],
                  key=lambda s: int(s[9:])) if os.path.isdir(case_dir) else []
    if len(dirs) != ranks:
        refuse("%s holds %d processor directories, registered ranks %d" % (case_dir, len(dirs), ranks))
    return [os.path.join(case_dir, d) for d in dirs]


def _read(path, kind, what):
    if not os.path.isfile(path):
        refuse("no %s at %s" % (what, path))
    try:
        F = FIO.read_field(path)
    except FIO.FieldFormatError as e:
        refuse("%s: %s" % (path, e))
    if F["kind"] != kind or F["internal"] is None:
        refuse("%s is not a nonuniform %s field. %s" % (path, kind, WRITE_PATH_NOTE))
    return F["internal"]


def read_geometry(pdirs):
    xs, ys, vs = [], [], []
    for p in pdirs:
        C = _read(os.path.join(p, "0", "C"), "vector", "cell-centre file")
        V = _read(os.path.join(p, "0", "V"), "scalar", "cell-volume file")
        if C.shape[0] != V.shape[0]:
            refuse("%s: 0/C carries %d cells but 0/V carries %d" % (p, C.shape[0], V.shape[0]))
        xs.append(C[:, 0]); ys.append(C[:, 1]); vs.append(V)
    xc, yc, V = np.concatenate(xs), np.concatenate(ys), np.concatenate(vs)
    if np.any(V <= 0):
        refuse("non-positive cell volumes in 0/V")
    return xc, yc, V


def read_scalar(paths):
    return np.concatenate([_read(p, "scalar", "scalar field") for p in paths])


def read_vector(paths):
    return np.vstack([_read(p, "vector", "vector field") for p in paths])


def box(xc, yc):
    m = EX.box_mask(xc, yc)
    if int(m.sum()) < 16:
        refuse("the sampling box selects only %d cells" % int(m.sum()))
    return m


def p_ratio_from_files(p_paths, V, mask):
    """G-F24-1 (per checkpoint): volume-weighted box-mean p / p1."""
    p = read_scalar(p_paths)
    if p.shape[0] != len(V):
        refuse("p carries %d cells but 0/V carries %d" % (p.shape[0], len(V)))
    return float(np.sum(V[mask] * p[mask]) / np.sum(V[mask]) / EX.P1)


def mach_from_files(u_paths, t_paths, V, mask):
    """R-F24-M (per checkpoint): volume-weighted box-mean Mach number |U| / sqrt(gamma R T)."""
    U = read_vector(u_paths)
    T = read_scalar(t_paths)
    if U.shape[0] != len(V) or T.shape[0] != len(V):
        refuse("U/T cell counts (%d/%d) differ from 0/V (%d)" % (U.shape[0], T.shape[0], len(V)))
    if np.any(T[mask] <= 0):
        refuse("non-positive temperature inside the sampling box; the Mach number is undefined")
    M = EX.mach(U[mask], T[mask])
    return float(np.sum(V[mask] * M) / np.sum(V[mask]))


def p_line_from_files(p_path_sets, xc, yc, V, n):
    """G-F24-2: the fan-line L2 error of p on the MEAN of the given checkpoint
    fields (one path set per checkpoint), through exact_f24.line_l2 (refuses a
    column count != n)."""
    if not p_path_sets:
        refuse("no checkpoint p fields to average for the fan line")
    acc = None
    for paths in p_path_sets:
        p = read_scalar(paths)
        if p.shape[0] != len(V):
            refuse("p carries %d cells but 0/V carries %d" % (p.shape[0], len(V)))
        acc = p if acc is None else acc + p
    return EX.line_l2(acc / float(len(p_path_sets)), xc, yc, V, n)


# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (rule 3)
# ---------------------------------------------------------------------------
def _planted_scalar_copies(paths, d):
    tmp = tempfile.mkdtemp(prefix="f24_plant_")
    work = []
    for k, p in enumerate(paths):
        w = os.path.join(tmp, "f_%d" % k)
        if FIO.plant_into_scalar_file(p, w, d) == 0:
            shutil.rmtree(tmp, ignore_errors=True)
            refuse("nothing to plant into %s" % p)
        work.append(w)
    return tmp, work


def _planted_vector_copies(paths, d):
    tmp = tempfile.mkdtemp(prefix="f24_plant_")
    work = []
    for k, p in enumerate(paths):
        w = os.path.join(tmp, "U_%d" % k)
        if FIO.plant_into_vector_file(p, w, 0, d) == 0:
            shutil.rmtree(tmp, ignore_errors=True)
            refuse("nothing to plant into %s" % p)
        work.append(w)
    return tmp, work


def plant_control_p(p_paths, V, mask, level):
    d = RT.PLANT
    before = p_ratio_from_files(p_paths, V, mask)
    predicted = before + d / EX.P1            # a uniform shift moves a volume-weighted mean by exactly d
    tmp, work = _planted_scalar_copies(p_paths, d)
    try:
        after = p_ratio_from_files(work, V, mask)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if after == before or abs(after - predicted) > 1e-13:
        refuse("PLANTED-ZERO CONTROL FAILED for <p>/p1 on %s: a shift of %.6e must move it to %.17g; the reader "
               "returned %.17g" % (p_paths, d, predicted, after))
    return RT.external_plant_control("p_ratio_from_files", before, after, plant=(predicted - before),
                                     artifact=";".join(p_paths), level=level)


def plant_control_mach(u_paths, t_paths, V, mask, level):
    d = RT.PLANT
    U = read_vector(u_paths)
    T = read_scalar(t_paths)
    before = mach_from_files(u_paths, t_paths, V, mask)
    Up = U.copy(); Up[:, 0] += d
    predicted = float(np.sum(V[mask] * EX.mach(Up[mask], T[mask])) / np.sum(V[mask]))
    tmp, work = _planted_vector_copies(u_paths, d)
    try:
        after = mach_from_files(work, t_paths, V, mask)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if after == before or abs(after - predicted) > 1e-13:
        refuse("PLANTED-ZERO CONTROL FAILED for <M> on %s: a Ux offset of %.6e must move it to %.17g; the reader "
               "returned %.17g" % (u_paths, d, predicted, after))
    return RT.external_plant_control("mach_from_files", before, after, plant=(predicted - before),
                                     artifact=";".join(u_paths), level=level)


def plant_control_line(p_path_sets, xc, yc, V, n, level):
    """A uniform shift d on p in EVERY averaged checkpoint moves the mean field
    by exactly d; the L2 error it must produce is computed in memory."""
    d = RT.PLANT
    mean = None
    for paths in p_path_sets:
        p = read_scalar(paths)
        mean = p if mean is None else mean + p
    mean = mean / float(len(p_path_sets))
    before = EX.line_l2(mean, xc, yc, V, n)
    predicted = EX.line_l2(mean + d, xc, yc, V, n)
    tmps, works = [], []
    try:
        for paths in p_path_sets:
            tmp, work = _planted_scalar_copies(paths, d)
            tmps.append(tmp); works.append(work)
        after = p_line_from_files(works, xc, yc, V, n)
    finally:
        for tmp in tmps:
            shutil.rmtree(tmp, ignore_errors=True)
    if after == before or abs(after - predicted) > 1e-13:
        refuse("PLANTED-ZERO CONTROL FAILED for the fan-line L2 on level %s: a shift of %.6e must move it to %.17g; "
               "the reader returned %.17g" % (level, d, predicted, after))
    return RT.external_plant_control("p_line_from_files", before, after, plant=(predicted - before),
                                     artifact=";".join(p_path_sets[-1]), level=level)


# ---------------------------------------------------------------------------
# PLATEAU RULE -- limbs (i) Class C and (ii) residual; limb (iii) census below
# ---------------------------------------------------------------------------
def class_c(t, v, label, cfg=None):
    cfg = CLASS_C if cfg is None else cfg
    t = np.asarray(t, dtype=float)
    v = np.asarray(v, dtype=float)
    if v.size < cfg["min_samples"]:
        refuse("CLASS C ELEMENT 4: %s has %d samples; the registered minimum is %d. NOT A RESULT."
               % (label, v.size, cfg["min_samples"]))
    w = int(cfg["window"])
    if v.size < w:
        refuse("CLASS C ELEMENT 1: %s has %d samples, fewer than the window %d" % (label, v.size, w))
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


def residual_state(p_last, p_prev, V, mask):
    """Limb (ii): max over box cells of |p_k - p_{k-1}| / p1 between the last two checkpoints."""
    a = read_scalar(p_last)
    b = read_scalar(p_prev)
    if a.shape[0] != len(V) or b.shape[0] != len(V):
        refuse("checkpoint p files do not carry the mesh's cell count")
    r = float(np.max(np.abs(a[mask] - b[mask])) / EX.P1)
    detail = dict(basis="max over sampling-box cells |p_k - p_{k-1}| / p1 between the last two checkpoints",
                  residual=r, tol=RESIDUAL_TOL)
    return ("PLATEAUED" if r <= RESIDUAL_TOL else "NOT_PLATEAUED_RESIDUAL_%.2e" % r), detail


def control_plateau_limbs_can_say_no():
    n = CLASS_C["min_samples"] + 20
    t = np.arange(1, n + 1, dtype=float) * WRITE_DT
    flat = np.full(n, 0.393) + 1e-6 * np.sin(np.arange(n))
    ok, _ = class_c(t, flat, "control_flat")
    if ok != "PLATEAUED":
        refuse("CLASS C CONTROL FAILED: a flat series was reported %r" % ok)
    ramp = flat + 4e-3 * t / t[-1]                         # drift over the window 1.1e-3 relative > trend_tol
    grow, _ = class_c(t, ramp, "control_ramp")
    if grow != "NOT_PLATEAUED_TREND":
        refuse("CLASS C ELEMENT 2 CONTROL FAILED: a drifting series was reported %r" % grow)
    step = flat.copy()
    step[-(CLASS_C["window"] // 2):] += 2e-4
    stat, _ = class_c(t, step, "control_step")
    if stat not in ("NOT_STATIONARY_MEAN", "NOT_PLATEAUED_TREND"):
        refuse("CLASS C ELEMENT 3 CONTROL FAILED: a mean shift was reported %r" % stat)
    probe = ("import sys; sys.path.insert(0, %r)\n"
             "import grade_f24 as g\nimport numpy as np\n"
             "try:\n    g.class_c(np.arange(5.0), np.ones(5), 'short')\n"
             "    print('CONTROL_FAILED_NO_REFUSAL')\n"
             "except SystemExit as e:\n    print('REFUSED' if e.code == 2 else 'WRONG_CODE')\n") % HERE
    p = subprocess.run([sys.executable, "-c", probe], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if "REFUSED" not in p.stdout.decode():
        refuse("CLASS C ELEMENT 4 CONTROL FAILED: a 5-sample series did not exit 2 (got %r)" % p.stdout.decode().strip())
    # limb (ii) driven both ways through the real reader
    tmp = tempfile.mkdtemp(prefix="f24_resid_")
    try:
        V = np.ones(32)
        mask = np.ones(32, dtype=bool)
        pa = np.full(32, 0.39); pb = pa + 1e-4
        fa, fb, fc = [os.path.join(tmp, n) for n in ("a", "b", "c")]
        for f, arr in ((fa, pa), (fb, pb), (fc, pa + 2 * RESIDUAL_TOL)):
            open(f, "w").write("FoamFile { version 2.0; format ascii; class volScalarField; object p; }\n"
                               "dimensions [1 -1 -2 0 0 0 0];\ninternalField nonuniform List<scalar> \n%s;\n"
                               "boundaryField { inlet { type fixedValue; value uniform 1; } }\n" % FIO.fmt_list(arr, "scalar"))
        s_ok, _ = residual_state([fb], [fa], V, mask)
        s_bad, _ = residual_state([fc], [fa], V, mask)
        if s_ok != "PLATEAUED" or s_bad == "PLATEAUED":
            refuse("RESIDUAL LIMB CONTROL FAILED: small change %r, large change %r" % (s_ok, s_bad))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(control="PZ-F24-PLATEAU_limbs_each_shown_able_to_refuse", flat="PLATEAUED", ramp=grow, step=stat,
                short_series="exit 2", residual_small="PLATEAUED", residual_large=s_bad, passed=True)


# ---------------------------------------------------------------------------
# LIMB (iii) -- explicit solver: a STABILITY CENSUS, named as such
# ---------------------------------------------------------------------------
TIME_RE = re.compile(r"^Time = ([0-9eE+\-.]+)\s*$", re.M)
CO_RE = re.compile(r"Mean and max Courant Numbers = ([0-9eE+\-.na]+) ([0-9eE+\-.na]+)")


def iterative_state(log_path, level):
    if not os.path.isfile(log_path):
        refuse("no solver log at %s; rule 5 limb (1) cannot be evaluated" % log_path)
    text = open(log_path, errors="replace").read()
    vals = []
    for m in CO_RE.finditer(text):
        try:
            vals.append(float(m.group(2)))
        except ValueError:
            vals.append(float("nan"))
    if not vals:
        refuse("no `Mean and max Courant Numbers` lines in %s; the stability state is ABSENT" % log_path)
    n_nan = sum(1 for v in vals if not math.isfinite(v))
    bad = [v for v in vals if math.isfinite(v) and v > CO_CEILING]
    detail = dict(basis="explicit inviscid rhoCentralFoam: NO iterative residual exists; per-time-step "
                        "solver-reported max Courant census over ALL steps against the registered ceiling",
                  n_readings=len(vals), expected=STEPS[level], ceiling=CO_CEILING,
                  n_above_ceiling=len(bad), n_non_finite=n_nan,
                  worst=max(v for v in vals if math.isfinite(v)) if n_nan < len(vals) else None,
                  fatal="FOAM FATAL" in text)
    if n_nan or detail["fatal"]:
        return "NOT_STABLE_NON_FINITE_OR_FATAL", detail
    if len(vals) != STEPS[level]:
        return "NOT_STABLE_%d_COURANT_LINES_FOR_%d_STEPS" % (len(vals), STEPS[level]), detail
    if bad:
        return "NOT_STABLE_%d_STEPS_ABOVE_CEILING" % len(bad), detail
    return "CONVERGED", detail


# ---------------------------------------------------------------------------
# COMPLETION -- rule 4, PHYSICS_CRITICAL fields only
# ---------------------------------------------------------------------------
def completion(case_dir, log_path, level):
    out = dict(case=case_dir, log=log_path)
    dt = DT[level]
    rc_path = os.path.join(case_dir, "RC.txt")
    if not os.path.isfile(rc_path):
        return dict(out, done=False, why="no RC.txt yet: rc not recorded; PENDING, not a verdict")
    rc = open(rc_path).read().strip()
    out["rc"] = rc
    if rc != "0":
        return dict(out, done=False, crashed=True, why="recorded solver rc is %r: a crash is a FINDING (NOT A RESULT)" % rc)
    if not os.path.isfile(log_path):
        return dict(out, done=False, crashed=True, why="rc 0 but no solver log: NOT A RESULT")
    text = open(log_path, errors="replace").read()
    times = [float(m.group(1)) for m in TIME_RE.finditer(text)]
    out.update(n_times=len(times), latest=times[-1] if times else None, dt=dt)
    if not times:
        return dict(out, done=False, crashed=True, why="rc 0 but no `Time =` lines: NOT A RESULT")
    if not re.search(r"^End\s*$", text, re.M):
        return dict(out, done=False, crashed=True, why="rc 0 recorded but no `End` line: NOT A RESULT")
    if not (times[-1] + dt > END_TIME):
        return dict(out, done=False, why="latest %.9g + dt %.9g does not exceed endTime %.9g" % (times[-1], dt, END_TIME))
    if len(times) != STEPS[level]:
        return dict(out, done=False, why="fixed-deltaT identity fails: %d `Time` lines, registered steps %d"
                                          % (len(times), STEPS[level]))
    zero_u = os.path.join(case_dir, "0", "U")
    if not os.path.isfile(zero_u):
        return dict(out, done=False, why="no serial 0/U to date the launch against")
    t0 = os.path.getmtime(zero_u)
    pdirs = sorted([d for d in os.listdir(case_dir) if re.fullmatch(r"processor[0-9]+", d)], key=lambda s: int(s[9:]))
    if len(pdirs) != RANKS[level]:
        return dict(out, done=False, why="%d processor directories, registered ranks %d" % (len(pdirs), RANKS[level]))
    missing, stale, end_dirs = [], [], []
    for pd in pdirs:
        end_dir = None
        for d in os.listdir(os.path.join(case_dir, pd)):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and abs(float(d) - END_TIME) < 1e-9:
                end_dir = os.path.join(case_dir, pd, d)
        if end_dir is None:
            return dict(out, done=False, why="%s has no time directory at endTime %g" % (pd, END_TIME))
        end_dirs.append(end_dir)
        for f in END_FIELDS:
            fp = os.path.join(end_dir, f)
            if not os.path.isfile(fp):
                missing.append("%s/%s" % (pd, f))
            elif os.path.getmtime(fp) <= t0:
                stale.append("%s/%s" % (pd, f))
    if missing:
        return dict(out, done=False, why="fields missing at endTime: %s" % missing)
    if stale:
        return dict(out, done=False, why="AGE GUARD: fields %s at endTime are NOT newer than the serial 0/U" % stale)
    return dict(out, done=True, end_dirs=end_dirs,
                why="rc 0; End; latest + dt > endTime; %d `Time` lines == registered steps; %s at endTime in all %d "
                    "processor directories and newer than 0/U" % (len(times), ", ".join(END_FIELDS), len(pdirs)))


# ---------------------------------------------------------------------------
# COST CLAIM -- INFRASTRUCTURE only (L-342)
# ---------------------------------------------------------------------------
def cost_claim(root):
    defects, spent = [], 0.0
    for name in LEVEL_NAMES:
        cd = os.path.join(root, name)
        if not os.path.isdir(cd):
            continue
        log = os.path.join(cd, "log.rhoCentralFoam")
        hits = re.findall(r"ClockTime = ([0-9]+) s", open(log, errors="replace").read()) if os.path.isfile(log) else []
        if not hits:
            defects.append("BOOKKEEPING DEFECT: level %s has no ClockTime reading; cost actual NOT MEASURED" % name)
        else:
            spent += float(hits[-1]) * RANKS[name] / 60.0
        for probe in ("box_before.txt", "box_after.txt", "MESH_LINE.txt", "log.decomposePar"):
            if not os.path.isfile(os.path.join(cd, probe)):
                defects.append("BOOKKEEPING DEFECT: level %s lacks %s; NOT MEASURED" % (name, probe))
    return dict(fields="INFRASTRUCTURE", core_min_claim=None if defects else spent, partial_sum_core_min=spent,
                cap_core_min=CAP_CORE_MIN, defects=defects,
                note="ClockTime x ranks / 60 (4 ranks); dollars at $0.0513/core-h DERIVED, NOT MEASURED")


def control_field_classes_separate():
    tmp = tempfile.mkdtemp(prefix="f24_l342_")
    try:
        cd = os.path.join(tmp, "coarse")
        os.makedirs(os.path.join(cd, "0"))
        open(os.path.join(cd, "0", "U"), "w").write("x")
        import time as _t
        _t.sleep(0.02)
        for k in range(EX.RANKS):
            os.makedirs(os.path.join(cd, "processor%d" % k, "4"))
            for f in END_FIELDS:
                open(os.path.join(cd, "processor%d" % k, "4", f), "w").write("y")
        n = STEPS["coarse"]; dt = DT["coarse"]
        body = "".join("Mean and max Courant Numbers = 0.12 0.2\nTime = %.10g\n" % ((i + 1) * dt) for i in range(n)) \
            + "ClockTime = 3 s\nEnd\n"
        log = os.path.join(cd, "log.rhoCentralFoam")
        open(log, "w").write(body)
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        good = completion(cd, log, "coarse")
        if not good["done"]:
            refuse("L-342 CONTROL: a complete synthetic level was not accepted: %s" % good["why"])
        st, _ = iterative_state(log, "coarse")
        if st != "CONVERGED":
            refuse("L-342 CONTROL: a stable synthetic log was not read as CONVERGED: %s" % st)
        cc = cost_claim(tmp)
        if cc["core_min_claim"] is not None or not cc["defects"] or not completion(cd, log, "coarse")["done"]:
            refuse("L-342 CONTROL: missing infrastructure did not refuse the cost claim with defect lines "
                   "while leaving completion untouched")
        open(os.path.join(cd, "RC.txt"), "w").write("134\n")
        if not completion(cd, log, "coarse").get("crashed"):
            refuse("L-342 CONTROL: a non-zero rc did not flip the level to NOT A RESULT")
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        open(log, "w").write(body.replace("End\n", ""))
        if not completion(cd, log, "coarse").get("crashed"):
            refuse("L-342 CONTROL: a missing End line with rc 0 did not flip the level to NOT A RESULT")
        open(log, "w").write(body.replace("0.12 0.2\n", "0.12 0.41\n", 1))
        st, _ = iterative_state(log, "coarse")
        if st == "CONVERGED":
            refuse("L-342 CONTROL: one step above the Courant ceiling was still read as CONVERGED")
        open(log, "w").write(body.replace("0.12 0.2\n", "nan nan\n", 1))
        st, _ = iterative_state(log, "coarse")
        if st == "CONVERGED":
            refuse("L-342 CONTROL: a nan Courant line was still read as CONVERGED")
        open(log, "w").write(body)
        shutil.rmtree(os.path.join(cd, "processor%d" % (EX.RANKS - 1)))
        if completion(cd, log, "coarse")["done"]:
            refuse("L-342 CONTROL: a missing processor directory was accepted as complete")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(control="PZ-F24-L342_infrastructure_vs_physics_fields_driven_both_ways",
                infrastructure_deleted="verdict channel unchanged, cost claim refused, defect lines printed",
                physics_corrupted="NOT A RESULT; Courant ceiling, nan and a missing rank all flip", passed=True)


# ---------------------------------------------------------------------------
# CENSUSES / CONTROLS
# ---------------------------------------------------------------------------
def ast_no_asserts(paths):
    bad = {}
    for p in paths:
        lines = [n.lineno for n in ast.walk(ast.parse(open(p).read())) if isinstance(n, ast.Assert)]
        if lines:
            bad[p] = lines
    if bad:
        refuse("`assert` carries a check in this rung's own path (L-332): %s" % json.dumps(bad))
    if sum(1 for n in ast.walk(ast.parse("def f(x):\n    assert x\n")) if isinstance(n, ast.Assert)) != 1:
        refuse("the assert counter cannot see a planted assert")
    return dict(files_checked=len(paths), assert_nodes=0, planted_assert_seen=True)


def control_grade_ladder_is_called():
    src = open(os.path.abspath(__file__)).read()
    calls = [n.lineno for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "grade_ladder"]
    if len(calls) != 1:
        refuse("expected EXACTLY ONE grade_ladder CALL NODE; found %d at %s" % (len(calls), calls))
    pat = re.compile(r"RT\.grade_ladder\s*\(")
    if [ln for ln in "def f():\n    return 1\n".splitlines() if pat.search(ln)]:
        refuse("GREP CONTROL FAILED: matcher hit a file with no call")
    if not [ln for ln in "import x as RT\nz = RT.grade_ladder(q)\n".splitlines() if pat.search(ln)]:
        refuse("GREP CONTROL FAILED: matcher MISSED a planted call")
    return dict(control="PZ-F24-GRADE_LADDER_CALLSITE_ast_census_plus_grep_both_ways", ast_call_nodes=calls, passed=True)


def control_solver_dicts_match():
    tp = open(os.path.join(HERE, "case", "constant", "thermophysicalProperties")).read()
    m = re.search(r"molWeight\s+([0-9eE+\-.]+)\s*;", tp)
    if not m or abs(float(m.group(1)) - EX.MOL_WEIGHT) > 1e-9:
        refuse("thermophysicalProperties molWeight does not equal exact_f24.MOL_WEIGHT (R = 1)")
    m = re.search(r"\bCp\s+([0-9eE+\-.]+)\s*;", tp)
    if not m or abs(float(m.group(1)) - EX.CP) > 1e-15:
        refuse("thermophysicalProperties Cp does not equal exact_f24.CP (gamma = 1.4)")
    for key, val in (("Tref", 0.0), ("Hsref", 0.0), ("Hf", 0.0), ("mu", 0.0)):
        mm = re.search(r"\b%s\s+([0-9eE+\-.]+)\s*;" % key, tp)
        if not mm or float(mm.group(1)) != val:
            refuse("thermophysicalProperties %s is not %g" % (key, val))
    fs = open(os.path.join(HERE, "case", "system", "fvSchemes")).read()
    for pat, what in ((r"fluxScheme\s+Kurganov\s*;", "fluxScheme Kurganov"),
                      (r"ddtSchemes\s*\{\s*default\s+Euler\s*;", "ddt Euler"),
                      (r"reconstruct\(rho\)\s+vanLeer\s*;", "reconstruct(rho) vanLeer"),
                      (r"reconstruct\(U\)\s+vanLeerV\s*;", "reconstruct(U) vanLeerV"),
                      (r"reconstruct\(T\)\s+vanLeer\s*;", "reconstruct(T) vanLeer")):
        if not re.search(pat, fs):
            refuse("fvSchemes does not register %s" % what)
    cd = open(os.path.join(HERE, "case", "system", "controlDict.template")).read()
    me = re.search(r"^\s*endTime\s+([0-9.]+)\s*;", cd, re.M)
    mw = re.search(r"^\s*writeInterval\s+([0-9.]+)\s*;", cd, re.M)
    if not me or abs(float(me.group(1)) - END_TIME) > 1e-12:
        refuse("controlDict.template endTime is not the registered %g" % END_TIME)
    if not mw or abs(float(mw.group(1)) - WRITE_DT) > 1e-12:
        refuse("controlDict.template writeInterval is not the registered %g" % WRITE_DT)
    if not re.search(r"adjustTimeStep\s+no\s*;", cd):
        refuse("controlDict.template must fix dt (adjustTimeStep no)")
    if not re.search(r"application\s+rhoCentralFoam\s*;", cd):
        refuse("controlDict.template application is not rhoCentralFoam")
    dp = open(os.path.join(HERE, "case", "system", "decomposeParDict")).read()
    m = re.search(r"numberOfSubdomains\s+([0-9]+)\s*;", dp)
    if not m or int(m.group(1)) != EX.RANKS:
        refuse("decomposeParDict numberOfSubdomains is not the registered %d" % EX.RANKS)
    ut = open(os.path.join(HERE, "case", "0", "U.template")).read()
    for pat, what in ((r"wallUp\s*\{\s*type slip;", "wallUp slip"), (r"wallDown\s*\{\s*type slip;", "wallDown slip"),
                      (r"outlet\s*\{\s*type zeroGradient;", "outlet zeroGradient"),
                      (r"topB\s*\{\s*type zeroGradient;", "topB zeroGradient (outflow)"),
                      (r"inlet\s*\{\s*type fixedValue;", "inlet fixedValue"),
                      (r"topA\s*\{\s*type fixedValue;", "topA fixedValue")):
        if not re.search(pat, ut):
            refuse("0/U.template does not declare %s" % what)
    # F16 finding (F16b RESULTS): an `empty` patch removes its normal direction from the solved set.
    # Exactly ONE empty declaration per file, and it must be the +/-z pair `frontAndBack`.
    for rel in ("case/system/blockMeshDict.template", "case/0/U.template", "case/0/p.template", "case/0/T.template"):
        txt = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, rel)).read())
        hits = re.findall(r"(\w+)\s*\{[^{}]*?type\s+empty\b", txt)
        if hits != ["frontAndBack"]:
            refuse("%s declares `empty` on %s; only the +/-z pair frontAndBack may be empty (F16 finding)" % (rel, hits))
    return dict(control="solver_dictionaries_agree_with_registration_and_empty_is_z_only", molWeight=EX.MOL_WEIGHT, Cp=EX.CP,
                endTime=END_TIME, writeInterval=WRITE_DT, flux="Kurganov", limiters="vanLeer/vanLeerV/vanLeer",
                ddt="Euler", ranks=EX.RANKS, empty_patches=["frontAndBack"], passed=True)


def control_reader_parses_real_solver_output():
    if not os.path.isfile(REAL_RHO_ON_BOX) or not os.path.isfile(REAL_U_ON_BOX):
        refuse("the real solver output the format is pinned against is absent: %s / %s" % (REAL_RHO_ON_BOX, REAL_U_ON_BOX))
    F = FIO.read_field(REAL_RHO_ON_BOX)
    if F["kind"] != "scalar" or F["internal"] is None or F["internal"].shape != (REAL_CELLS,):
        refuse("reader did not return %d scalars from %s" % (REAL_CELLS, REAL_RHO_ON_BOX))
    G = FIO.read_field(REAL_U_ON_BOX)
    if G["kind"] != "vector" or G["internal"] is None or G["internal"].shape != (REAL_CELLS, 3):
        refuse("reader did not return %d vectors from %s" % (REAL_CELLS, REAL_U_ON_BOX))
    return dict(control="reader_parses_real_solver_written_rho_and_U_on_this_box",
                artifacts=[REAL_RHO_ON_BOX, REAL_U_ON_BOX], cells=REAL_CELLS, passed=True)


# ---------------------------------------------------------------------------
# BANDS -- from exact_f24.gate_specs (modes admitted by the sub-ladder triples)
# ---------------------------------------------------------------------------
def bands():
    gs = EX.gate_specs()
    out = {}
    for name in GATES + REPORTED:
        spec = gs[QUANTITY_OF[name]]
        if name in GATES and spec["band"] is None:
            refuse("%s is registered as a gate but its quantity %s carries no band (mode %s)" % (name, QUANTITY_OF[name], spec["mode"]))
        if name in REPORTED and spec["mode"] != "REPORTED-NOT-GATED":
            refuse("%s is a reported quantity but exact_f24 registers mode %s for it" % (name, spec["mode"]))
        out[name] = dict(quantity=QUANTITY_OF[name], mode=spec["mode"], band=spec["band"], reference=spec["reference"],
                         dim=DIM, order_claim=spec["order_claim"], fine_pred=spec["fine_pred"], principle=spec["principle"],
                         subladder_triple=spec["triple"])
    return out


# ---------------------------------------------------------------------------
# DEMONSTRATION -- every gate able to take a failing AND a passing value; the
# reported quantity's reader shown to see a non-zero
# ---------------------------------------------------------------------------
def synth_level(tmp, tag, p, T, U, xc, yc, V):
    pd = os.path.join(tmp, tag, "processor0")
    os.makedirs(os.path.join(pd, "0"))
    hdr = "FoamFile { version 2.0; format ascii; class %s; object %s; }\ndimensions %s;\ninternalField nonuniform List<%s> \n%s;\nboundaryField { inlet { type zeroGradient; } }\n"
    open(os.path.join(pd, "0", "C"), "w").write(hdr % ("volVectorField", "C", "[0 1 0 0 0 0 0]", "vector",
                                                        FIO.fmt_list(np.column_stack([xc, yc, np.zeros(xc.size)]), "vector")))
    open(os.path.join(pd, "0", "V"), "w").write(hdr % ("volScalarField", "V", "[0 3 0 0 0 0 0]", "scalar", FIO.fmt_list(V, "scalar")))
    paths = {}
    for name, arr, cls, dims, kind in (("p", p, "volScalarField", "[1 -1 -2 0 0 0 0]", "scalar"),
                                       ("T", T, "volScalarField", "[0 0 0 1 0 0 0]", "scalar"),
                                       ("U", U, "volVectorField", "[0 1 -1 0 0 0 0]", "vector")):
        fp = os.path.join(pd, name)
        open(fp, "w").write(hdr % (cls, name, dims, kind, FIO.fmt_list(arr, kind)))
        paths[name] = [fp]
    return [pd], paths


def _synthetic_geometry():
    """A box-sized grid in region 2 PLUS the fine level's fan-line column."""
    s2 = EX.state2()
    nb = 40
    xg = np.linspace(EX.X_BOX0 + 0.01, EX.X_BOX1 - 0.01, nb)
    ng = np.linspace(0.005, EX.N_BOX - 0.005, nb)
    X, Nn = np.meshgrid(xg, ng)
    d = math.radians(EX.DELTA_DEG)
    xb = X.ravel(); yb = EX.wall_y(xb) + Nn.ravel() / math.cos(d)
    n = NSIDE["fine"]; h = EX.h_of(n)
    xl = np.full(n, EX.X_LINE + 0.5 * h)
    yl = EX.wall_y(xl) + (np.arange(n) + 0.5) * h
    xc = np.concatenate([xb, xl]); yc = np.concatenate([yb, yl])
    V = np.concatenate([np.full(xb.size, 0.1 * 0.25 / nb / nb), np.full(n, h * h * math.cos(d))])
    return s2, xc, yc, V, n


def demonstrate(bnd):
    """ZERO COMPUTE, at the FINE size.  Gate 1: exact state 2 plus 1x the finest
    sub-ladder error (inside) and 40x (outside).  Gate 2: the exact fan field on
    the column plus a uniform offset equal to the extrapolated fine error
    (inside, the reader returns exactly that error) and 40x (outside).  Reported
    quantity: exact state 2 reads M2 exactly; a Ux offset is seen."""
    s2, xc, yc, V, n = _synthetic_geometry()
    d = math.radians(EX.DELTA_DEG)
    gs = EX.gate_specs()
    e_p = gs["p_box"]["subladder_errors"][-1]
    e_l = gs["p_line"]["fine_pred"]
    exact = EX.fan_field(xc, yc)
    rows = []
    tmp = tempfile.mkdtemp(prefix="f24_demo_")
    try:
        for k, (scale, want) in enumerate(((1.0, "inside"), (40.0, "outside"))):
            p = exact["p"] + scale * (e_p * EX.P1)          # box cells are in region 2: exact p2 + scaled error
            p_line_field = exact["p"] + scale * e_l * EX.P1
            T = exact["T"]
            speed = exact["M"] * np.sqrt(EX.GAMMA * EX.R_GAS * T)
            U = np.column_stack([speed * np.cos(exact["theta"]), speed * np.sin(exact["theta"]), np.zeros(xc.size)])
            pdirs, paths = synth_level(tmp, "c%d" % k, p, T, U, xc, yc, V)
            xr, yr, Vr = read_geometry(pdirs)
            mask = box(xr, yr)
            v1 = p_ratio_from_files(paths["p"], Vr, mask)
            lo, hi = bnd[GATES[0]]["band"]
            rows.append(dict(gate=GATES[0], construction="exact state 2 + %g x finest sub-ladder error" % scale, value=v1,
                             band=[lo, hi], inside=bool(lo <= v1 <= hi), intended=want))
            _pd, paths2 = synth_level(tmp, "l%d" % k, p_line_field, T, U, xc, yc, V)
            v2 = p_line_from_files([paths2["p"]], xr, yr, Vr, n)
            lo, hi = bnd[GATES[1]]["band"]
            rows.append(dict(gate=GATES[1], construction="exact fan field + %g x extrapolated fine error (uniform)" % scale,
                             value=v2, band=[lo, hi], inside=bool(lo <= v2 <= hi), intended=want))
        # the reported quantity's reader: exact -> M2 to round-off; planted -> moves
        p = exact["p"]; T = exact["T"]
        speed = exact["M"] * np.sqrt(EX.GAMMA * EX.R_GAS * T)
        U = np.column_stack([speed * np.cos(exact["theta"]), speed * np.sin(exact["theta"]), np.zeros(xc.size)])
        pdirs, paths = synth_level(tmp, "m", p, T, U, xc, yc, V)
        xr, yr, Vr = read_geometry(pdirs)
        mask = box(xr, yr)
        m0 = mach_from_files(paths["U"], paths["T"], Vr, mask)
        if abs(m0 - s2["M2"]) > 1e-12:
            refuse("REPORTED-QUANTITY READER: exact state 2 read back as M = %.15g, exact %.15g" % (m0, s2["M2"]))
        pc = plant_control_mach(paths["U"], paths["T"], Vr, mask, "synthetic")
        if not pc.get("passed"):
            refuse("REPORTED-QUANTITY READER: the planted Ux offset was not seen")
        rows.append(dict(gate=REPORTED[0], construction="exact state 2 (reader returns M2 exactly) and planted Ux offset",
                         value=m0, band=None, inside=None, intended="reported", planted_seen=pc["passed"]))
        # the fan-line reader on the exact field returns ZERO error (same-field control, F17b lesson)
        _pd, paths3 = synth_level(tmp, "z", exact["p"], T, U, xc, yc, V)
        z = p_line_from_files([paths3["p"]], xr, yr, Vr, n)
        if z != 0.0:
            refuse("FAN-LINE READER: the exact fan field read back with error %.3e, expected exactly 0" % z)
        rows.append(dict(gate=GATES[1], construction="exact fan field, no error", value=z, band=None, inside=None,
                         intended="zero"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for r in rows:
        if r["intended"] in ("inside", "outside") and (r["intended"] == "inside") != r["inside"]:
            refuse("GATE DEMONSTRATION FAILED for %s: intended %s, got %.9g against %s"
                   % (r["gate"], r["intended"], r["value"], r["band"]))
    seen = set((r["gate"], r["inside"]) for r in rows)
    for g in GATES:
        if (g, True) not in seen or (g, False) not in seen:
            refuse("gate %s was not shown able to take BOTH values" % g)
    return rows


# ---------------------------------------------------------------------------
# THE GRADE
# ---------------------------------------------------------------------------
def checkpoint_paths(pdirs):
    """[(t, {field: [processor<k>/<t>/<field> ...]})] for every t > 0 present in ALL ranks."""
    per = []
    for p in pdirs:
        ts = {}
        for d in os.listdir(p):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and float(d) > 0 and all(
                    os.path.isfile(os.path.join(p, d, f)) for f in ("p", "T", "U")):
                ts[float(d)] = os.path.join(p, d)
        per.append(ts)
    common = sorted(set.intersection(*[set(t.keys()) for t in per]))
    return [(t, dict((f, [os.path.join(ts[t], f) for ts in per]) for f in ("p", "T", "U"))) for t in common]


_LEVEL_CACHE = {}


def read_level(root, name):
    """Everything the level yields, read ONCE: completion, geometry, the three
    quantity series, the level's plateau and stability states."""
    if name in _LEVEL_CACHE:
        return _LEVEL_CACHE[name]
    case_dir = os.path.join(root, name)
    out = dict(name=name, case_dir=case_dir)
    if not os.path.isdir(case_dir):
        out.update(present=False)
        _LEVEL_CACHE[name] = out
        return out
    log = os.path.join(case_dir, "log.rhoCentralFoam")
    comp = completion(case_dir, log, name)
    out.update(present=True, completion=comp)
    if not comp["done"]:
        _LEVEL_CACHE[name] = out
        return out
    pdirs = processor_dirs(case_dir, RANKS[name])
    xc, yc, V = read_geometry(pdirs)
    if len(xc) != CELLS[name]:
        refuse("level %s carries %d cells, registered %d" % (name, len(xc), CELLS[name]))
    mask = box(xc, yc)
    cps = checkpoint_paths(pdirs)
    if len(cps) != N_CHECKPOINTS:
        refuse("level %s holds %d checkpoints with p, T, U in every rank; registered %d" % (name, len(cps), N_CHECKPOINTS))
    ts, p_series, m_series, l_series = [], [], [], []
    for t, paths in cps:
        ts.append(t)
        p_series.append(p_ratio_from_files(paths["p"], V, mask))
        m_series.append(mach_from_files(paths["U"], paths["T"], V, mask))
        l_series.append(p_line_from_files([paths["p"]], xc, yc, V, NSIDE[name]))
    w = CLASS_C["window"]
    window_sets = [paths["p"] for _t, paths in cps[-w:]]
    it_state, it_detail = iterative_state(log, name)
    cc_state, cc_detail = class_c(ts, p_series, "%s/p_box" % name)
    rs_state, rs_detail = residual_state(cps[-1][1]["p"], cps[-2][1]["p"], V, mask)
    pl_state = cc_state if cc_state != "PLATEAUED" else rs_state
    values = dict(p_box=float(np.mean(p_series[-w:])), M_box=float(np.mean(m_series[-w:])),
                  p_line=p_line_from_files(window_sets, xc, yc, V, NSIDE[name]))
    out.update(xc=xc, yc=yc, V=V, mask=mask, cps=cps, window_sets=window_sets, values=values,
               series=dict(t=ts, p_box=p_series, M_box=m_series, p_line=l_series),
               series_window_std=dict(p_box=float(np.std(p_series[-w:])), M_box=float(np.std(m_series[-w:])),
                                      p_line=float(np.std(l_series[-w:]))),
               last=dict(p_box=p_series[-1], M_box=m_series[-1], p_line_last_checkpoint=l_series[-1],
                         p_line_mean_of_series=float(np.mean(l_series[-w:]))),
               iterative=it_state, iterative_detail=it_detail, plateau=pl_state,
               plateau_detail=dict(class_c=cc_detail, residual=rs_detail, class_c_state=cc_state, residual_state=rs_state),
               box_cells=int(mask.sum()), line_cells=int(EX.line_mask(xc, NSIDE[name]).sum()))
    _LEVEL_CACHE[name] = out
    return out


def _levels_for(root, name):
    """Level rows for quantity `name`, or an early (PENDING / NOT A RESULT) row."""
    q = QUANTITY_OF[name]
    levels, detail = [], []
    for lv in LEVEL_NAMES:
        L = read_level(root, lv)
        if not L["present"]:
            return None, dict(gate=name, verdict="PENDING", note="level %r absent from %s" % (lv, root))
        comp = L["completion"]
        if not comp["done"]:
            verdict = "NOT A RESULT" if comp.get("crashed") else "PENDING"
            return None, dict(gate=name, verdict=verdict, note="level %r: %s" % (lv, comp["why"]), completion=comp)
        levels.append(dict(name=lv, cells=CELLS[lv], value=L["values"][q]))
        detail.append(dict(name=lv, cells=CELLS[lv], value=L["values"][q], window_std=L["series_window_std"][q],
                           last=L["last"], artifact=L["cps"][-1][1], h=EX.h_of(NSIDE[lv]), dt=DT[lv],
                           completion=comp, iterative=L["iterative"], iterative_detail=L["iterative_detail"],
                           plateau=L["plateau"], plateau_detail=L["plateau_detail"],
                           box_cells=L["box_cells"], line_cells=L["line_cells"]))
    return (levels, detail), None


def grade_one(root, gate, bnd):
    got, early = _levels_for(root, gate)
    if early is not None:
        return early
    levels, detail = got
    F = read_level(root, LEVEL_NAMES[-1])
    q = QUANTITY_OF[gate]
    if q == "p_box":
        pc = plant_control_p(F["cps"][-1][1]["p"], F["V"], F["mask"], F["name"])
    else:
        pc = plant_control_line(F["window_sets"], F["xc"], F["yc"], F["V"], NSIDE[F["name"]], F["name"])
    spec = bnd[gate]
    # ---- THE ONE AND ONLY GATE CALL.
    row = RT.grade_ladder(
        quantity=gate, levels=levels, dim=spec["dim"], band=spec["band"], plant_control=pc,
        iterative_states=dict((d["name"], d["iterative"]) for d in detail),
        plateau_states=dict((d["name"], d["plateau"]) for d in detail),
        reference=spec["reference"])
    row["gate"] = gate
    row["mode"] = spec["mode"]
    row["order_claim"] = spec["order_claim"]
    row["band_principle"] = spec["principle"]
    row["levels_detail"] = detail
    row["value_note"] = ("graded value = plateau-window mean over the last %d checkpoints" % CLASS_C["window"]) if q == "p_box" \
        else ("graded value = fan-line L2 error of the WINDOW-MEAN p field (last %d checkpoints); the per-checkpoint "
              "series mean and std are printed beside it, ungated" % CLASS_C["window"])
    row["iterative_note"] = ("explicit inviscid solver: no iterative residual exists; limb (iii) is a per-step "
                             "solver-reported Courant census against ceiling %g, named as such" % CO_CEILING)
    row["plateau_note"] = "the plateau is the LEVEL's (Class C + residual on the box-mean p/p1 series)"
    row["gated_by"] = "scripts/roache_triple.py::grade_ladder -- rule 5 is reached through this call and through nothing else"
    if row["verdict"] not in VERDICTS:
        refuse("%s produced a verdict outside the fixed vocabulary: %r" % (gate, row["verdict"]))
    return row


def report_one(root, name, bnd):
    """REPORTED-NOT-GATED: values, the ladder triple and its order beside the
    exact reference, the planted control on the reader; NO verdict, and nothing
    here reaches rule 5."""
    got, early = _levels_for(root, name)
    if early is not None:
        early["mode"] = "REPORTED-NOT-GATED"
        early["verdict"] = None
        early["note"] = "no verdict by registration; " + early.get("note", "")
        return early
    levels, detail = got
    F = read_level(root, LEVEL_NAMES[-1])
    last = F["cps"][-1][1]
    pc = plant_control_mach(last["U"], last["T"], F["V"], F["mask"], F["name"])
    tr = RT.all_triples(levels, DIM)[-1]
    spec = bnd[name]
    return dict(gate=name, mode="REPORTED-NOT-GATED", verdict=None, quantity=QUANTITY_OF[name],
                reference=spec["reference"], levels=levels, levels_detail=detail,
                triple=dict(state=tr["state"], order=tr.get("order"), levels=tr.get("levels")),
                fine_error=levels[-1]["value"] - spec["reference"], planted_zero=dict(pc),
                note="REPORTED-NOT-GATED by registration (%s); NO verdict is issued and nothing here reaches rule 5"
                     % spec["principle"])


def selftest_predicate(controls, demo, census):
    if census["assert_nodes"] != 0:
        return False, "assert nodes present"
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if len(demo) != 6:
        return False, "expected 6 demonstration rows (2 gates x inside/outside, reported reader, zero-error line), got %d" % len(demo)
    if not __debug__:
        return False, "running under -O"
    return True, ("%d controls green; both gates shown able to take a passing AND a failing value through the real "
                  "reader on the pinned write format; the fan-line reader returns exactly 0 on the exact field; the "
                  "reported quantity's reader returns M2 exactly and sees a plant; 0 assert nodes across 4 files; "
                  "exactly one grade_ladder call node; __debug__ True" % len(controls))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs", "F24_PRANDTL_MEYER_runs"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--prereg-commit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    census = ast_no_asserts([os.path.abspath(__file__), os.path.join(HERE, "exact_f24.py"),
                             os.path.join(HERE, "foam_io_f24.py"), os.path.join(HERE, "build_f24.py")])
    controls = [EX.control_nu_closed_form_matches_quadrature(), EX.control_substitution_is_able_to_fail(),
                EX.control_fan_field(), EX.control_box_lies_in_region_2(), EX.control_ladder_is_geometrically_similar(),
                EX.control_subladder_registration(),
                control_plateau_limbs_can_say_no(), control_grade_ladder_is_called(),
                control_solver_dicts_match(), control_reader_parses_real_solver_output(),
                control_field_classes_separate()]
    bnd = bands()
    demo = demonstrate(bnd)

    if a.selftest:
        ok, why = selftest_predicate(controls, demo, census)
        print(json.dumps(dict(assert_census=census, controls=controls, bands=bnd,
                              model_levels=EX.predictions(), subladder=EX.SUBLADDER, gate_mode=EX.GATE_MODE,
                              plateau_rule=dict(class_c=CLASS_C, residual_tol=RESIDUAL_TOL, co_ceiling=CO_CEILING),
                              gate_demonstration=demo, write_path=WRITE_PATH_NOTE,
                              predicate=dict(ok=ok, why=why)), indent=2, default=str))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0

    if not a.prereg_commit:
        refuse("--prereg-commit is required for a real grade (rule 2)")
    rows = [grade_one(a.root, g, bnd) for g in GATES] + [report_one(a.root, r, bnd) for r in REPORTED]
    cost = cost_claim(a.root)
    out = a.out or os.path.join(a.root, "F24_GRADED.json")
    out_dir = os.path.dirname(os.path.abspath(out))
    if not os.path.isdir(out_dir):
        # THE GRADER CREATES NO RUN ROOT: a grade before the launcher must leave the rule-2 absence condition intact.
        print("NOT WRITTEN: %s does not exist; the grader creates no directory (rule-2 absence condition kept)" % out_dir)
    if os.path.isdir(out_dir):
      with open(out, "w") as f:
        json.dump(dict(rung="F24-PRANDTL_MEYER", prereg_commit=a.prereg_commit,
                       prereg="verification/campaign/F24_PRANDTL_MEYER_PREREGISTRATION.md",
                       assert_census=census, controls=controls, gate_demonstration=demo, write_path=WRITE_PATH_NOTE,
                       cap_core_min=CAP_CORE_MIN, bands=bnd,
                       field_classes=dict(PHYSICS_CRITICAL=PHYSICS_CRITICAL, INFRASTRUCTURE=INFRASTRUCTURE),
                       cost_claim=cost, rows=rows), f, indent=2, default=str)
    print("F24 -- PRANDTL-MEYER CORNER -- TALLY")
    print("=" * 78)
    for r in rows:
        if r.get("mode") == "REPORTED-NOT-GATED":
            print("%-40s REPORTED-NOT-GATED (no verdict by registration)" % r["gate"])
            if "triple" in r:
                print("    ladder triple %s, order %s; fine value %.9g vs exact %.9g (error %+.3e)"
                      % (r["triple"]["state"], r["triple"]["order"], r["levels"][-1]["value"], r["reference"], r["fine_error"]))
        else:
            print("%-40s %s  [mode %s]" % (r["gate"], r["verdict"], r.get("mode")))
        for k in ("why", "note"):
            if r.get(k):
                print("    %s" % r[k])
        for d in r.get("levels_detail", []):
            print("    %-7s value %.9g (window std %.2e)  level plateau %s  residual %.2e  Courant worst %s"
                  % (d["name"], d["value"], d["window_std"], d["plateau"],
                     d["plateau_detail"]["residual"]["residual"], d["iterative_detail"].get("worst")))
    print("=" * 78)
    for dline in cost["defects"]:
        print(dline)
    if cost["core_min_claim"] is None:
        print("COST CLAIM REFUSED (infrastructure fields missing); physics verdicts above are unaffected (L-342)")
    else:
        print("cost actual: %.3f core-min of cap %.1f (ClockTime x ranks / 60; dollars derived, not measured)"
              % (cost["core_min_claim"], CAP_CORE_MIN))
    print("gated by: scripts/roache_triple.py::grade_ladder")
    if os.path.isdir(out_dir):
        print("written: %s" % out)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RT.Refusal as e:
        sys.stderr.write("REFUSED (roache_triple): %s\n" % e)
        sys.exit(2)
