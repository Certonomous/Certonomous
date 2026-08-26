#!/usr/bin/env python3
"""
F25 -- THE GRADING PATH for fully developed laminar flow in a SQUARE DUCT
(simpleFoam, steady, Re_Dh ~ 100, streamwise cyclic, fixed body force, a
GENUINE 3-D ladder refined by exactly 2 in all three directions, 4 ranks at
every level).  Lineage: cases/F23_HP_WEDGE/grade_f23.py.  It calls
`scripts/roache_triple.py::grade_ladder` and rule 5 is reached through that
call and through NOTHING ELSE (exactly one call node, AST-censused).

REFUSAL DISCIPLINE: `raise` / `sys.exit(2)` only; ZERO `assert` across this
file, exact_f25.py, foam_io_f25.py, build_f25.py (L-332); hard `-O` refusal.

THE FIELDS ARE READ FROM THE processor*/ DIRECTORIES (the run is decomposed
on 4 ranks and never reconstructed): every level's 0/C, 0/V and <t>/U are the
concatenation over the RANKS processor directories, each cell carrying its own
centre and volume, so no ordering is assumed.  The graded STATION is the one
x-slab of cells nearest x = L/2 + dx/2; its cell count must equal NR^2.

CONVERGENCE IS CLASS C (CFD_CONVERGENCE_GATE_RULING_2026-08-25.md section 2),
all four elements, on the GRADED QUANTITY ITSELF sampled at every written
checkpoint (100 iterations apart); element 4 exits.  Rule 5 limb (1) is a
CENSUS over every iteration in the Class C window of the solver's own initial
residual for Ux -- THE DRIVEN COMPONENT -- plus a FIELD-LEVEL check that the
transverse components Uy, Uz are zero to 1e-10 U_MAX at endTime.  The
NORMALISED initial residuals of Uy, Uz and p are PRINTED beside the verdict
and EXCLUDED from the gate, declared at freeze (NUMERICS_KNOWLEDGE N-AV8):
each is a vanishing channel (v = w = 0 exactly on the fully developed
solution; p is uniform on the cyclic domain) whose relative residual is
normalised by a vanishing scale and carries no information.

THE ITERATIVE FLOOR IS DERIVED, NOT INHERITED (L-346): the census tolerance
UX_RES_TOL over the CLASS_C window must put the integrated iterative movement
at least a decade below the model's PREDICTED FINE-LEVEL discretisation error
(both gates); `control_iterative_floor_derived_from_fine_error` refuses
otherwise and is driven both ways.

L-342: PHYSICS_CRITICAL and INFRASTRUCTURE field classes are declared below;
gates and refusals read the first only; the second can only refuse the cost
claim and print a BOOKKEEPING DEFECT line.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: grade_f25.py must not run under `python3 -O` (the shared "
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

import roache_triple as RT              # THE GATE. Rule 5 lives here and nowhere else.
import exact_f25 as EX                  # THE EXACT SOLUTION and the discretisation model.
import foam_io_f25 as FIO               # THE READERS.

DIM = EX.DIM                            # 3: refinement in ALL THREE directions, r = 2 exactly
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
LEVEL_NAMES = [n for n, _nr, _nx in EX.LEVELS]
CELLS = dict((n, nr * nr * nx) for n, nr, nx in EX.LEVELS)
SHAPE = dict((n, (nr, nx)) for n, nr, nx in EX.LEVELS)
END_TIME = EX.N_ITER
DT = 1.0
WRITE_EVERY = EX.WRITE_EVERY
RANKS = dict((n, EX.RANKS) for n in LEVEL_NAMES)

# THE ONE DECLARED PARAMETER BOTH BANDS ARE BUILT FROM.
BAND_FACTOR = 3.0

# Rule 5 limb (1): the driven component's initial residual, censused over
# every iteration inside the Class C window; and the transverse field floor.
UX_RES_TOL = 1.0e-8
TRANSVERSE_FIELD_TOL = 1.0e-10          # x U_MAX, on max|Uy|, max|Uz| at endTime
FLOOR_MARGIN = 0.1                      # L-346: window x UX_RES_TOL <= FLOOR_MARGIN x predicted fine error

CAP_CORE_MIN = 1400.0                   # ClockTime s * ranks / 60, summed over levels
U_RELAX, P_RELAX = 0.95, 1.0            # SIMPLEC factors the iterative floor was MEASURED with (prereg 5.1)

PHYSICS_CRITICAL = (
    "log.simpleFoam `End` line and `Time =` count (fixed-count identity)",
    "RC.txt (solver rc, written by the launcher in the shell that ran mpirun)",
    "processor*/<endTime>/U and p present in every one of the RANKS directories and NEWER than the serial 0/U (age guard)",
    "processor*/0/C cell centres and processor*/0/V cell volumes (the gate quantities are undefined without them)",
    "checkpoint U files (the gate quantity and the Class C series)",
    "initial residual of Ux in log.simpleFoam (rule 5 limb 1 census); max|Uy|, max|Uz| at endTime (transverse floor)",
)
INFRASTRUCTURE = (
    "ClockTime in log.simpleFoam (cost actual)",
    "box_before.txt / box_after.txt (load and memory probes)",
    "MESH_LINE.txt (recorded mesh-quality reading; the gate is enforced at build time)",
    "log.decomposePar, log.blockMesh, log.checkMesh, log.build (utility logs)",
    "STATUS.* / launcher.queue.out / LAUNCH_LOG rows written by a queue runner",
    "calibration figures derived from any of the above",
)

CLASS_C = dict(
    min_samples=20,      # element 4: 20 of the 40 checkpoints
    window=12,           # element 1: 12 checkpoints = 1200 iterations
    trend_tol=2.0e-4,
    stat_tol=1.0e-4,
    var_ratio=(0.2, 5.0),
    floor=1.0e-14,
)

WRITE_PATH_NOTE = (
    "OpenFOAM ascii volVectorField `U` written by the solver at every checkpoint into each "
    "processor<k>/<t>/ directory: `internalField nonuniform List<vector>` NEWLINE N NEWLINE `(` one "
    "`(ux uy uz)` per line `)`; volVectorField `C` and volScalarField `V` in processor<k>/0/ written by "
    "`postProcess -func writeCellCentres|writeCellVolumes` before decomposePar.  Layout pinned against "
    "REAL solver output on this box: verification/runs/ansys_verification/VMFL019/L1_30/5/U (icoFoam, "
    "v2606, 120 cells), parsed at selftest as a live control by BOTH reader paths (fast and regex).")
REAL_U_ON_BOX = os.path.join(REPO, "verification", "runs", "ansys_verification", "VMFL019", "L1_30", "5", "U")


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
    """(xc, yc, zc, V) concatenated over the processor directories."""
    xs, ys, zs, vs = [], [], [], []
    for p in pdirs:
        C = _read(os.path.join(p, "0", "C"), "vector", "cell-centre file")
        vp = os.path.join(p, "0", "V")
        if not os.path.isfile(vp):
            refuse("no cell-volume file at %s" % vp)
        try:
            V = FIO.scalar_field_values(vp, C.shape[0])     # cubic cells: the solver writes 0/V `uniform h^3`
        except FIO.FieldFormatError as e:
            refuse("%s: 0/C carries %d cells but 0/V does not: %s" % (p, C.shape[0], e))
        xs.append(C[:, 0]); ys.append(C[:, 1]); zs.append(C[:, 2]); vs.append(V)
    xc, yc, zc, V = np.concatenate(xs), np.concatenate(ys), np.concatenate(zs), np.concatenate(vs)
    if np.any(V <= 0):
        refuse("non-positive cell volumes in 0/V")
    return xc, yc, zc, V


def read_U(paths):
    out = []
    for p in paths:
        U = _read(p, "vector", "U field")
        out.append(U)
    U = np.vstack(out)
    if U.shape[0] < 16:
        refuse("only %d cells across %s; refusing to form a profile norm over that" % (U.shape[0], paths))
    return U


_STATION_CACHE = {}


def station_read(u_paths, V, mask):
    """Read U once per checkpoint (both gates and the diagnostics share it):
    the station slice plus the field-level diagnostics, keyed on the files'
    identity (path, size, mtime)."""
    key = tuple((p, os.path.getsize(p), os.path.getmtime(p)) for p in u_paths)
    if key not in _STATION_CACHE:
        U = read_U(u_paths)
        if U.shape[0] != len(V):
            refuse("U carries %d cells but 0/V carries %d" % (U.shape[0], len(V)))
        ub_all = float(np.sum(V * U[:, 0]) / np.sum(V))
        _STATION_CACHE[key] = dict(u=U[mask, 0].copy(), ubar_all_cells=ub_all,
                                   max_abs_Uy=float(np.max(np.abs(U[:, 1]))), max_abs_Uz=float(np.max(np.abs(U[:, 2]))))
        if len(_STATION_CACHE) > 200:
            _STATION_CACHE.pop(next(iter(_STATION_CACHE)))
    return _STATION_CACHE[key]


def station_mask(xc, nr, nx):
    dx = EX.L / nx
    xs = EX.L * EX.X_STATION_FRAC + 0.5 * dx
    m = np.abs(xc - xs) < 0.25 * dx
    if int(m.sum()) != nr * nr:
        refuse("the station x = %.9g selects %d cells, registered NR^2 = %d" % (xs, int(m.sum()), nr * nr))
    return m


def e2n_from_files(u_paths, yc, zc, V, mask):
    """G-F25-1: volume-weighted L2 error of the normalised station profile."""
    st = station_read(u_paths, V, mask)
    u, y, z, v = st["u"], yc[mask], zc[mask], V[mask]
    ubar = float(np.sum(v * u) / np.sum(v))
    if ubar <= 0.0:
        refuse("station bulk velocity %.6g is not positive; the normalised profile is undefined" % ubar)
    return EX.e2_normalised(u, ubar, y, z, v)


def fre_from_files(u_paths, V, mask):
    """G-F25-2: f.Re from the imposed G and the READ station bulk velocity."""
    st = station_read(u_paths, V, mask)
    u, v = st["u"], V[mask]
    ubar = float(np.sum(v * u) / np.sum(v))
    if ubar <= 0.0:
        refuse("station bulk velocity %.6g is not positive; f.Re is undefined" % ubar)
    return EX.f_re(ubar)


def diagnostics_from_files(u_paths, V, mask):
    """PRINTED, NOT GATED: x-uniformity (all-cell vs station bulk velocity)
    and the transverse field maxima."""
    st = station_read(u_paths, V, mask)
    ub_st = float(np.sum(V[mask] * st["u"]) / np.sum(V[mask]))
    return dict(ubar_all_cells=st["ubar_all_cells"], ubar_station=ub_st,
                x_nonuniformity=abs(st["ubar_all_cells"] - ub_st) / max(abs(ub_st), 1e-300),
                max_abs_Uy=st["max_abs_Uy"], max_abs_Uz=st["max_abs_Uz"])


# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (rule 3) -- into copies of the REAL processor files,
# read back with the REAL parser.
# ---------------------------------------------------------------------------
def _planted_copies(u_paths, d):
    tmp = tempfile.mkdtemp(prefix="f25_plant_")
    work = []
    for k, p in enumerate(u_paths):
        w = os.path.join(tmp, "U_%d" % k)
        if FIO.plant_into_vector_file(p, w, 0, d) == 0:
            shutil.rmtree(tmp, ignore_errors=True)
            refuse("nothing to plant into %s" % p)
        work.append(w)
    return tmp, work


def plant_control_e2n(u_paths, yc, zc, V, mask, level):
    d = RT.PLANT
    st = station_read(u_paths, V, mask)
    u, y, z, v = st["u"], yc[mask], zc[mask], V[mask]
    ub = float(np.sum(v * u) / np.sum(v))
    before = EX.e2_normalised(u, ub, y, z, v)
    predicted = EX.e2_normalised(u + d, ub + d, y, z, v)    # the plant shifts u AND the read Ubar_h
    tmp, work = _planted_copies(u_paths, d)
    try:
        after = e2n_from_files(work, yc, zc, V, mask)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if after == before or abs(after - predicted) > 1e-13:
        refuse("PLANTED-ZERO CONTROL FAILED for E2n on %s: a Ux offset of %.6e must move E2n to %.17g; "
               "the reader returned %.17g (before %.17g)" % (u_paths, d, predicted, after, before))
    return RT.external_plant_control("e2n_from_files", before, after, plant=(predicted - before),
                                     artifact=";".join(u_paths), level=level)


def plant_control_fre(u_paths, V, mask, level):
    d = RT.PLANT
    st = station_read(u_paths, V, mask)
    u, v = st["u"], V[mask]
    ub = float(np.sum(v * u) / np.sum(v))
    before = EX.f_re(ub)
    predicted = EX.f_re(ub + d)
    tmp, work = _planted_copies(u_paths, d)
    try:
        after = fre_from_files(work, V, mask)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if after == before or abs(after - predicted) > 1e-10:
        refuse("PLANTED-ZERO CONTROL FAILED for f.Re on %s: a Ux offset of %.6e must move f.Re to %.17g; "
               "the reader returned %.17g" % (u_paths, d, predicted, after))
    return RT.external_plant_control("fre_from_files", before, after, plant=(predicted - before),
                                     artifact=";".join(u_paths), level=level)


# ---------------------------------------------------------------------------
# CLASS C -- four elements; element 4 EXITS
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
             "import grade_f25 as g\nimport numpy as np\n"
             "try:\n    g.class_c(np.arange(5.0), np.ones(5), 'short')\n"
             "    print('CONTROL_FAILED_NO_REFUSAL')\n"
             "except SystemExit as e:\n    print('REFUSED' if e.code == 2 else 'WRONG_CODE')\n") % HERE
    p = subprocess.run([sys.executable, "-c", probe], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if "REFUSED" not in p.stdout.decode():
        refuse("CLASS C ELEMENT 4 CONTROL FAILED: a 5-sample series did not exit 2 (got %r)" % p.stdout.decode().strip())
    return dict(control="PZ-F25-CLASSC_four_limbs_each_shown_able_to_refuse",
                flat="PLATEAUED", ramp=grow, step=stat, short_series="exit 2", passed=True)


# ---------------------------------------------------------------------------
# ITERATIVE CONVERGENCE -- a CENSUS over every iteration in the Class C window
# ---------------------------------------------------------------------------
INIT_RES_RE = re.compile(r"Solving for (Ux|Uy|Uz|p), Initial residual = ([0-9eE+\-.]+)")
TIME_RE = re.compile(r"^Time = ([0-9eE+\-.]+)\s*$", re.M)


def iterative_state(log_path, diag):
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
        if m and cur is not None and m.group(1) not in cur:      # the FIRST p solve of the iteration
            cur[m.group(1)] = float(m.group(2))
    n_win = CLASS_C["window"] * WRITE_EVERY
    win = [d for d in per_iter if d["time"] > END_TIME - n_win]
    if len(win) < n_win:
        refuse("only %d iterations inside the %d-iteration census window of %s; an absent measurement is "
               "reported as absent" % (len(win), n_win, log_path))
    bad = 0
    worst = dict(Ux=0.0, Uy=0.0, Uz=0.0, p=0.0)
    for d in win:
        if "Ux" not in d:
            refuse("iteration %g of %s carries no initial residual for Ux" % (d["time"], log_path))
        for k in worst:
            if k in d:
                worst[k] = max(worst[k], d[k])
        if d["Ux"] > UX_RES_TOL:
            bad += 1
    floor = TRANSVERSE_FIELD_TOL * EX.u_max()
    transverse_bad = diag["max_abs_Uy"] > floor or diag["max_abs_Uz"] > floor
    detail = dict(basis="initial residual of Ux (the driven component) censused over every iteration in the "
                        "Class C window; Uy/Uz/p residuals PRINTED and EXCLUDED (N-AV8: vanishing channels); "
                        "transverse components checked in the FIELD at endTime instead; UX_RES_TOL derived from "
                        "the predicted fine-level error (L-346)",
                  window_iterations=n_win, ux_tol=UX_RES_TOL, n_ux_above_tol=bad, worst_initial_residuals=worst,
                  ungated_printed=dict(Uy=worst["Uy"], Uz=worst["Uz"], p=worst["p"]),
                  transverse_field_floor=floor, max_abs_Uy=diag["max_abs_Uy"], max_abs_Uz=diag["max_abs_Uz"])
    if bad:
        return "NOT_CONVERGED_%d_Ux_READINGS_ABOVE_TOL" % bad, detail
    if transverse_bad:
        return "NOT_CONVERGED_TRANSVERSE_FIELD_ABOVE_FLOOR", detail
    return "CONVERGED", detail


def iterative_floor_admissible(ux_tol, window_iters, e2n_fine_pred, fre_rel_err_fine_pred, margin=FLOOR_MARGIN):
    """L-346: the integrated iterative movement over the census window
    (window x normalised residual tolerance, relative to the velocity scale)
    must sit at least 1/margin below the SMALLER predicted fine-level error."""
    budget = margin * min(abs(e2n_fine_pred), abs(fre_rel_err_fine_pred))
    return window_iters * ux_tol <= budget, dict(window_x_tol=window_iters * ux_tol, budget=budget,
                                                 e2n_fine_pred=e2n_fine_pred, fre_rel_err_fine_pred=fre_rel_err_fine_pred,
                                                 margin=margin)


def control_iterative_floor_derived_from_fine_error():
    fine = dict((r["name"], r) for r in EX.predictions())["fine"]
    rel = fine["fRe_err_pred"] / EX.f_re_exact()
    n_win = CLASS_C["window"] * WRITE_EVERY
    ok, d = iterative_floor_admissible(UX_RES_TOL, n_win, fine["E2n_pred"], rel)
    if not ok:
        refuse("L-346 REGISTRATION DEFECT: the iterative floor UX_RES_TOL = %.1e over the %d-iteration window "
               "(%.3e) is NOT a decade below the predicted fine-level error (budget %.3e); the census could read "
               "CONVERGED while the graded quantity still moves" % (UX_RES_TOL, n_win, d["window_x_tol"], d["budget"]))
    loose, _ = iterative_floor_admissible(100.0 * UX_RES_TOL, n_win, fine["E2n_pred"], rel)
    if loose:
        refuse("PLANTED CONTROL FAILED: a 100x looser floor was still accepted as admissible")
    tight, _ = iterative_floor_admissible(UX_RES_TOL, n_win, 1e-2 * fine["E2n_pred"], 1e-2 * rel)
    if tight:
        refuse("PLANTED CONTROL FAILED: a fine level 100x more accurate than predicted was still accepted with this floor")
    return dict(control="PZ-F25-L346_iterative_floor_derived_from_predicted_fine_error_both_ways", ux_tol=UX_RES_TOL,
                window_iterations=n_win, window_x_tol=d["window_x_tol"], budget=d["budget"],
                e2n_fine_pred=fine["E2n_pred"], fre_rel_err_fine_pred=rel, margin=FLOOR_MARGIN,
                ratio_used=d["window_x_tol"] / d["budget"], passed=True)


# ---------------------------------------------------------------------------
# COMPLETION -- standing rule 4, PHYSICS_CRITICAL fields only
# ---------------------------------------------------------------------------
def completion(case_dir, log_path, ranks):
    out = dict(case=case_dir, log=log_path)
    rc_path = os.path.join(case_dir, "RC.txt")
    if not os.path.isfile(rc_path):
        return dict(out, done=False, why="no RC.txt yet: the solver rc is not recorded (run in progress or launcher "
                                         "died before recording it); PENDING, not a verdict")
    rc = open(rc_path).read().strip()
    out["rc"] = rc
    if rc != "0":
        return dict(out, done=False, crashed=True,
                    why="recorded solver rc is %r, not 0: a crash is a FINDING (NOT A RESULT), not a pending run" % rc)
    if not os.path.isfile(log_path):
        return dict(out, done=False, crashed=True, why="rc 0 but no solver log at %s: NOT A RESULT" % log_path)
    text = open(log_path, errors="replace").read()
    times = [float(m.group(1)) for m in TIME_RE.finditer(text)]
    out.update(n_times=len(times), latest=times[-1] if times else None, dt=DT)
    if not times:
        return dict(out, done=False, crashed=True, why="rc 0 but no `Time =` lines in the log: NOT A RESULT")
    if not re.search(r"^End\s*$", text, re.M):
        return dict(out, done=False, crashed=True,
                    why="rc 0 recorded but no `End` line: the solver log and the rc disagree; NOT A RESULT")
    if not (times[-1] + DT > END_TIME):
        return dict(out, done=False, why="latest %g + dt %g does not exceed endTime %g" % (times[-1], DT, END_TIME))
    if len(times) != END_TIME:
        return dict(out, done=False, why="fixed-deltaT identity fails: %d `Time` lines, endTime/dt = %d"
                                          % (len(times), END_TIME))
    zero_u = os.path.join(case_dir, "0", "U")
    if not os.path.isfile(zero_u):
        return dict(out, done=False, why="no serial 0/U to date the launch against")
    t0 = os.path.getmtime(zero_u)
    pdirs = sorted([d for d in os.listdir(case_dir) if re.fullmatch(r"processor[0-9]+", d)], key=lambda s: int(s[9:]))
    if len(pdirs) != ranks:
        return dict(out, done=False, why="%d processor directories, registered ranks %d" % (len(pdirs), ranks))
    missing, stale = [], []
    for pd in pdirs:
        end_dir = None
        for d in os.listdir(os.path.join(case_dir, pd)):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and abs(float(d) - END_TIME) < 1e-9:
                end_dir = os.path.join(case_dir, pd, d)
        if end_dir is None:
            return dict(out, done=False, why="%s has no time directory at endTime %g" % (pd, END_TIME))
        for f in ("U", "p"):
            fp = os.path.join(end_dir, f)
            if not os.path.isfile(fp):
                missing.append("%s/%s" % (pd, f))
            elif os.path.getmtime(fp) <= t0:
                stale.append("%s/%s" % (pd, f))
    if missing:
        return dict(out, done=False, why="fields missing at endTime: %s" % missing)
    if stale:
        return dict(out, done=False, why="AGE GUARD: fields %s at endTime are NOT newer than the serial 0/U" % stale)
    return dict(out, done=True, why="rc 0; End present; latest + dt > endTime; %d `Time` lines == endTime; U and p "
                                    "at endTime in all %d processor directories and newer than 0/U" % (len(times), ranks))


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
    return dict(control="PZ-F25-GRADE_LADDER_CALLSITE_ast_census_plus_grep_both_ways",
                ast_call_nodes=calls, grep_lines=grep_hits, passed=True)


def control_solver_dicts_match():
    """nu, G, ranks on disk == exact_f25; residualControl ABSENT; endTime and
    writeInterval == registered; the cyclic/wall patch declarations present."""
    tp = open(os.path.join(HERE, "case", "constant", "transportProperties")).read()
    m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
    if not m or abs(float(m.group(1)) - EX.NU) > 1e-15:
        refuse("transportProperties nu does not equal exact_f25.NU = %.17g" % EX.NU)
    fo = open(os.path.join(HERE, "case", "constant", "fvOptions")).read()
    m = re.search(r"U\s+\(\(\s*([0-9eE+\-.]+)\s+0\s+0\s*\)\s+0\s*\)\s*;", fo)
    if not m or abs(float(m.group(1)) - EX.G) > 1e-15:
        refuse("fvOptions momentum source does not equal exact_f25.G = %.17g" % EX.G)
    if not re.search(r"volumeMode\s+specific\s*;", fo) or not re.search(r"selectionMode\s+all\s*;", fo):
        refuse("fvOptions must apply G per unit volume (volumeMode specific) to all cells")
    fs = open(os.path.join(HERE, "case", "system", "fvSolution")).read()
    if re.search(r"^\s*residualControl", fs, re.M):
        refuse("fvSolution carries residualControl; the run must go to endTime")
    if not re.search(r"consistent\s+yes\s*;", fs):
        refuse("fvSolution is not SIMPLEC (consistent yes); the registered iterative floor was measured under SIMPLEC")
    mu = re.search(r"equations\s*\{\s*U\s+([0-9.]+)\s*;", fs)
    mp = re.search(r"fields\s*\{\s*p\s+([0-9.]+)\s*;", fs)
    if not mu or abs(float(mu.group(1)) - U_RELAX) > 1e-12 or not mp or abs(float(mp.group(1)) - P_RELAX) > 1e-12:
        refuse("fvSolution relaxation factors are not the registered U %g / p %g" % (U_RELAX, P_RELAX))
    sch = open(os.path.join(HERE, "case", "system", "fvSchemes")).read()
    if not re.search(r"div\(phi,U\)\s+Gauss linearUpwind grad\(U\)\s*;", sch):
        refuse("fvSchemes div(phi,U) is not the registered `Gauss linearUpwind grad(U)` (the dominant implicit part "
               "the iterative floor was measured with)")
    if not re.search(r"laplacianSchemes\s*\{\s*default Gauss linear corrected;", sch):
        refuse("fvSchemes Laplacian is not Gauss linear corrected (the stencil the model integrates)")
    cd = open(os.path.join(HERE, "case", "system", "controlDict")).read()
    me = re.search(r"^\s*endTime\s+([0-9]+)\s*;", cd, re.M)
    mw = re.search(r"^\s*writeInterval\s+([0-9]+)\s*;", cd, re.M)
    if not me or int(me.group(1)) != END_TIME:
        refuse("controlDict endTime is not the registered %d" % END_TIME)
    if not mw or int(mw.group(1)) != WRITE_EVERY:
        refuse("controlDict writeInterval is not the registered %d" % WRITE_EVERY)
    dp = open(os.path.join(HERE, "case", "system", "decomposeParDict")).read()
    m = re.search(r"numberOfSubdomains\s+([0-9]+)\s*;", dp)
    if not m or int(m.group(1)) != EX.RANKS:
        refuse("decomposeParDict numberOfSubdomains is not the registered %d" % EX.RANKS)
    if not re.search(r"n\s*\(\s*1\s+2\s+2\s*\)", dp):
        refuse("decomposeParDict does not keep the x direction whole (n (1 2 2)); the cyclic pair would be cut")
    bm = open(os.path.join(HERE, "case", "system", "blockMeshDict.template")).read()
    for pat, what in ((r"inlet\s*\{\s*type cyclic;\s*neighbourPatch outlet;", "inlet cyclic -> outlet"),
                      (r"outlet\s*\{\s*type cyclic;\s*neighbourPatch inlet;", "outlet cyclic -> inlet"),
                      (r"wall\s*\{\s*type wall;", "wall")):
        if not re.search(pat, bm):
            refuse("blockMeshDict.template does not declare %s" % what)
    if not re.search(r"hex \(0 1 2 3 4 5 6 7\) \(__NX__ __NR__ __NR__\)", bm):
        refuse("blockMeshDict.template block is not __NX__ x __NR__ x __NR__")
    ut = open(os.path.join(HERE, "case", "0", "U.template")).read()
    if not re.search(r"wall\s*\{\s*type noSlip;", ut):
        refuse("0/U.template wall is not noSlip")
    return dict(control="solver_dictionaries_agree_with_registration", nu=EX.NU, G=EX.G, ranks=EX.RANKS,
                endTime=END_TIME, writeInterval=WRITE_EVERY, residualControl="absent", decomposition="simple n (1 2 2)",
                simplec=True, relaxation=dict(U=U_RELAX, p=P_RELAX), div_phi_U="Gauss linearUpwind grad(U)", passed=True)


def control_reader_parses_real_solver_output():
    if not os.path.isfile(REAL_U_ON_BOX):
        refuse("the real solver output the format is pinned against is absent: %s" % REAL_U_ON_BOX)
    F = FIO.read_field(REAL_U_ON_BOX)
    if F["kind"] != "vector" or F["internal"] is None or F["internal"].shape != (120, 3):
        refuse("reader did not return 120 vectors from %s" % REAL_U_ON_BOX)
    if not np.all(np.isfinite(F["internal"])):
        refuse("reader returned non-finite values from %s" % REAL_U_ON_BOX)
    # the FAST path must equal the REGEX path bit for bit on the real file and on a synthetic one
    R = FIO.read_field(REAL_U_ON_BOX, fast=False)
    if not np.array_equal(F["internal"], R["internal"]):
        refuse("READER CONTROL FAILED: the fast list parser and the regex parser disagree on %s" % REAL_U_ON_BOX)
    for name in F["patches"]:
        a, b = F["patches"][name], R["patches"].get(name)
        if (a is None) != (b is None) or (a is not None and not np.array_equal(a, b)):
            refuse("READER CONTROL FAILED: patch %s differs between the fast and regex parsers" % name)
    tmp = tempfile.mkdtemp(prefix="f25_rd_")
    try:
        arr = np.random.RandomState(7).standard_normal((333, 3)) * 1e-3
        p = os.path.join(tmp, "U")
        open(p, "w").write("FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
                           "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
                           "boundaryField { wall { type noSlip; } }\n" % FIO.fmt_list(arr, "vector"))
        S1, S2 = FIO.read_field(p), FIO.read_field(p, fast=False)
        if not (np.array_equal(S1["internal"], arr) and np.array_equal(S2["internal"], arr)):
            refuse("READER CONTROL FAILED: a synthetic 333-vector list did not round-trip through both parsers")
        # PLANTED: a list whose declared N disagrees with its body must NOT be accepted by the fast path silently
        open(p, "w").write("FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
                           "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
                           "boundaryField { wall { type noSlip; } }\n" % FIO.fmt_list(arr, "vector").replace("333", "334", 1))
        try:
            FIO.read_field(p)
            refuse("READER CONTROL FAILED: a list declaring 334 entries but carrying 333 was accepted")
        except FIO.FieldFormatError:
            pass
        # a `uniform` 0/V (what OpenFOAM writes for a cubic mesh) must expand to n copies; a
        # nonuniform one with the wrong count must refuse
        vpath = os.path.join(tmp, "V")
        open(vpath, "w").write("FoamFile { version 2.0; format ascii; class volScalarField; object V; }\n"
                               "dimensions [0 3 0 0 0 0 0];\ninternalField uniform 2.44140625e-4;\n"
                               "boundaryField { wall { type calculated; value uniform 0; } }\n")
        vv = FIO.scalar_field_values(vpath, 77)
        if vv.shape != (77,) or not np.all(vv == 2.44140625e-4):
            refuse("READER CONTROL FAILED: a uniform 0/V was not expanded to 77 copies of its value")
        try:
            FIO.scalar_field_values(p, 5)          # p is a vector file: must refuse
            refuse("READER CONTROL FAILED: a vector file was accepted as a scalar volume field")
        except FIO.FieldFormatError:
            pass
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(control="reader_parses_real_solver_written_U_on_this_box_fast_path_equals_regex_path",
                artifact=REAL_U_ON_BOX, cells=120, synthetic_cells=333, mismatched_count_refused=True,
                uniform_volume_file_expanded=True, passed=True)


# ---------------------------------------------------------------------------
# BANDS -- both from ONE declared parameter applied to the model prediction
# ---------------------------------------------------------------------------
def bands():
    tab = dict((r["name"], r) for r in EX.predictions())
    fine = tab["fine"]
    e2p = fine["E2n_pred"]
    tol = BAND_FACTOR * abs(fine["fRe_err_pred"])
    fre = EX.f_re_exact()
    return {
        "G-F25-1_E2_normalised_profile": dict(
            band=(e2p / BAND_FACTOR, e2p * BAND_FACTOR), reference=0.0, dim=DIM,
            principle=("discretisation-model prediction E2n = %.9e at h_fine = %g (the 5-point cross-section stencil "
                       "simpleFoam reduces to on the cubic mesh, solved), times [1/%g, %g]"
                       % (e2p, fine["h"], BAND_FACTOR, BAND_FACTOR))),
        "G-F25-2_f_Re": dict(
            band=(fre - tol, fre + tol), reference=fre, dim=DIM,
            principle=("exact series f.Re = %.9f +/- %g x the model's predicted fine-level error (%.6e) = +/- %.6e"
                       % (fre, BAND_FACTOR, fine["fRe_err_pred"], tol))),
    }


# ---------------------------------------------------------------------------
# THE DEMONSTRATION -- both gates shown able to take a failing AND a passing
# value, through the real readers, on files in the pinned write format
# ---------------------------------------------------------------------------
def synth_level(tmp, nr, nx, u_station, tag):
    """A synthetic single-processor level: nx x-slabs each carrying the given
    cross-section profile, with 0/C and 0/V from the model's cubic geometry."""
    g = EX.cross_section_geometry(nr)
    dx = g["h"]
    xg = (np.arange(nx) + 0.5) * dx
    xc = np.repeat(xg, nr * nr)
    yc = np.tile(g["yc"], nx)
    zc = np.tile(g["zc"], nx)
    V = np.tile(g["vol"], nx)
    U = np.column_stack([np.tile(u_station, nx), np.zeros(xc.size), np.zeros(xc.size)])
    pd = os.path.join(tmp, tag, "processor0")
    os.makedirs(os.path.join(pd, "0"))
    open(os.path.join(pd, "0", "C"), "w").write(
        "FoamFile { version 2.0; format ascii; class volVectorField; object C; }\n"
        "dimensions [0 1 0 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
        "boundaryField { wall { type calculated; value uniform (0 0 0); } }\n"
        % FIO.fmt_list(np.column_stack([xc, yc, zc]), "vector"))
    open(os.path.join(pd, "0", "V"), "w").write(
        "FoamFile { version 2.0; format ascii; class volScalarField; object V; }\n"
        "dimensions [0 3 0 0 0 0 0];\ninternalField nonuniform List<scalar> \n%s;\n"
        "boundaryField { wall { type calculated; value uniform 0; } }\n" % FIO.fmt_list(V, "scalar"))
    up = os.path.join(pd, "U")
    open(up, "w").write(
        "FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
        "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
        "boundaryField { wall { type noSlip; } }\n" % FIO.fmt_list(U, "vector"))
    return [pd], [up]


def demonstrate(bnd):
    """ZERO COMPUTE.  The model's SOLVED fine-level station profile (exact +
    model error) stands in for the fine field, on a 4-slab synthetic level at
    the fine cross-section: inside both bands; the error field x40 is outside
    G-F25-1; the profile x1.01 is outside G-F25-2.  The synthetic station is
    at x = L_synth/2 + dx/2 of the SYNTHETIC length (nx = 4 slabs)."""
    m = EX.model("fine")
    nr, _nx_full = SHAPE["fine"]
    nx = 4
    err = m["u"] - EX.u_exact(m["yc"], m["zc"])
    rows = []
    tmp = tempfile.mkdtemp(prefix="f25_demo_")
    saved_L = EX.L
    try:
        EX.L = nx * EX.h_of(nr)                    # the synthetic level's own length (restored below)
        cases = ((1.0, 1.0, "inside", "inside"), (40.0, 1.0, "outside", None), (1.0, 1.01, None, "outside"))
        for k, (scale, mult, want1, want2) in enumerate(cases):
            u = (EX.u_exact(m["yc"], m["zc"]) + scale * err) * mult
            pdirs, ups = synth_level(tmp, nr, nx, u, "c%d" % k)
            xc, yc, zc, V = read_geometry(pdirs)
            mask = station_mask(xc, nr, nx)
            cons = "exact + %g x model error field, u x %g" % (scale, mult)
            if want1:
                v1 = e2n_from_files(ups, yc, zc, V, mask)
                lo, hi = bnd["G-F25-1_E2_normalised_profile"]["band"]
                rows.append(dict(gate="G-F25-1_E2_normalised_profile", construction=cons, value=v1, band=[lo, hi],
                                 inside=bool(lo <= v1 <= hi), intended=want1))
            if want2:
                v2 = fre_from_files(ups, V, mask)
                lo, hi = bnd["G-F25-2_f_Re"]["band"]
                rows.append(dict(gate="G-F25-2_f_Re", construction=cons, value=v2, band=[lo, hi],
                                 inside=bool(lo <= v2 <= hi), intended=want2))
    finally:
        EX.L = saved_L
        shutil.rmtree(tmp, ignore_errors=True)
    for r in rows:
        if (r["intended"] == "inside") != r["inside"]:
            refuse("GATE DEMONSTRATION FAILED for %s: construction intended %s returned %.9g against %s"
                   % (r["gate"], r["intended"], r["value"], r["band"]))
    seen = set((r["gate"], r["inside"]) for r in rows)
    for g in bnd:
        if (g, True) not in seen or (g, False) not in seen:
            refuse("gate %s was not shown able to take BOTH values" % g)
    return rows


# ---------------------------------------------------------------------------
# THE COST CLAIM -- INFRASTRUCTURE fields only (L-342)
# ---------------------------------------------------------------------------
def cost_claim(root):
    defects, spent = [], 0.0
    for name in LEVEL_NAMES:
        cd = os.path.join(root, name)
        if not os.path.isdir(cd):
            continue
        log = os.path.join(cd, "log.simpleFoam")
        hits = re.findall(r"ClockTime = ([0-9]+) s", open(log, errors="replace").read()) if os.path.isfile(log) else []
        if not hits:
            defects.append("BOOKKEEPING DEFECT: level %s has no ClockTime reading in log.simpleFoam; cost actual NOT MEASURED" % name)
        else:
            spent += float(hits[-1]) * RANKS[name] / 60.0
        for probe in ("box_before.txt", "box_after.txt", "MESH_LINE.txt", "log.decomposePar"):
            if not os.path.isfile(os.path.join(cd, probe)):
                defects.append("BOOKKEEPING DEFECT: level %s lacks %s; NOT MEASURED" % (name, probe))
    return dict(fields="INFRASTRUCTURE", core_min_claim=None if defects else spent, partial_sum_core_min=spent,
                cap_core_min=CAP_CORE_MIN, defects=defects,
                note="ClockTime x ranks / 60 (4 ranks); dollars at $0.0513/core-h DERIVED, NOT MEASURED")


def control_field_classes_separate():
    tmp = tempfile.mkdtemp(prefix="f25_l342_")
    try:
        cd = os.path.join(tmp, "coarse")
        os.makedirs(os.path.join(cd, "0"))
        open(os.path.join(cd, "0", "U"), "w").write("x")
        import time as _t
        _t.sleep(0.02)
        for k in range(EX.RANKS):
            os.makedirs(os.path.join(cd, "processor%d" % k, str(END_TIME)))
            for f in ("U", "p"):
                open(os.path.join(cd, "processor%d" % k, str(END_TIME), f), "w").write("y")
        body = "".join("Time = %d\nGAMG:  Solving for Ux, Initial residual = 1e-12, Final residual = 1e-13, No Iterations 0\n" % i
                       for i in range(1, END_TIME + 1)) + "ClockTime = 7 s\nEnd\n"
        log = os.path.join(cd, "log.simpleFoam")
        open(log, "w").write(body)
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        good = completion(cd, log, EX.RANKS)
        if not good["done"]:
            refuse("L-342 CONTROL: a complete synthetic level was not accepted: %s" % good["why"])
        diag = dict(max_abs_Uy=0.0, max_abs_Uz=0.0)
        st, _ = iterative_state(log, diag)
        if st != "CONVERGED":
            refuse("L-342 CONTROL: a converged synthetic log was not read as CONVERGED: %s" % st)
        cc = cost_claim(tmp)
        if cc["core_min_claim"] is not None or not cc["defects"] or not completion(cd, log, EX.RANKS)["done"]:
            refuse("L-342 CONTROL: missing infrastructure fields did not produce a refused cost claim with defect "
                   "lines while leaving completion untouched")
        open(os.path.join(cd, "RC.txt"), "w").write("134\n")
        if not completion(cd, log, EX.RANKS).get("crashed"):
            refuse("L-342 CONTROL: a non-zero rc did not flip the level to NOT A RESULT")
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        open(log, "w").write(body.replace("End\n", ""))
        if not completion(cd, log, EX.RANKS).get("crashed"):
            refuse("L-342 CONTROL: a missing End line with rc 0 did not flip the level to NOT A RESULT")
        open(log, "w").write(body.replace("Initial residual = 1e-12", "Initial residual = 1e-7", 1))
        # the single substituted line sits at iteration 1, OUTSIDE the census window: must still be CONVERGED
        st, _ = iterative_state(log, diag)
        if st != "CONVERGED":
            refuse("L-342 CONTROL: a residual outside the census window changed the state")
        open(log, "w").write(body[:body.rfind("Initial residual = 1e-12")] + body[body.rfind("Initial residual = 1e-12"):].replace(
            "Initial residual = 1e-12", "Initial residual = 1e-7", 1))
        st, _ = iterative_state(log, diag)
        if st == "CONVERGED":
            refuse("L-342 CONTROL: one Ux residual above tolerance inside the window was still read as CONVERGED")
        open(log, "w").write(body)
        st, _ = iterative_state(log, dict(max_abs_Uy=1e-6, max_abs_Uz=0.0))
        if st == "CONVERGED":
            refuse("L-342 CONTROL: a transverse field above the floor was still read as CONVERGED")
        shutil.rmtree(os.path.join(cd, "processor%d" % (EX.RANKS - 1)))
        if completion(cd, log, EX.RANKS)["done"]:
            refuse("L-342 CONTROL: a missing processor directory was accepted as complete")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(control="PZ-F25-L342_infrastructure_vs_physics_fields_driven_both_ways",
                infrastructure_deleted="verdict channel unchanged, cost claim refused, defect lines printed",
                physics_corrupted="NOT A RESULT; Ux residual in window, transverse field floor, missing rank all flip",
                passed=True)


# ---------------------------------------------------------------------------
# THE GRADE
# ---------------------------------------------------------------------------
GATES = ("G-F25-1_E2_normalised_profile", "G-F25-2_f_Re")


def checkpoint_paths(pdirs):
    """{t: [processor<k>/<t>/U ...]} for every t > 0 present in ALL ranks."""
    per = []
    for p in pdirs:
        ts = {}
        for d in os.listdir(p):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and float(d) > 0 and os.path.isfile(os.path.join(p, d, "U")):
                ts[float(d)] = os.path.join(p, d, "U")
        per.append(ts)
    common = sorted(set.intersection(*[set(t.keys()) for t in per]))
    return [(t, [ts[t] for ts in per]) for t in common]


def grade_one(root, gate, bnd):
    levels, detail = [], []
    for name in LEVEL_NAMES:
        case_dir = os.path.join(root, name)
        if not os.path.isdir(case_dir):
            return dict(gate=gate, verdict="PENDING", note="level %r absent from %s" % (name, root))
        log = os.path.join(case_dir, "log.simpleFoam")
        comp = completion(case_dir, log, RANKS[name])
        if not comp["done"]:
            verdict = "NOT A RESULT" if comp.get("crashed") else "PENDING"
            return dict(gate=gate, verdict=verdict, note="level %r: %s" % (name, comp["why"]), completion=comp)
        pdirs = processor_dirs(case_dir, RANKS[name])
        xc, yc, zc, V = read_geometry(pdirs)
        nr, nx = SHAPE[name]
        if len(xc) != CELLS[name]:
            refuse("level %s carries %d cells, registered %d" % (name, len(xc), CELLS[name]))
        mask = station_mask(xc, nr, nx)
        ts, vs, last = [], [], None
        for t, ups in checkpoint_paths(pdirs):
            ts.append(t)
            vs.append(e2n_from_files(ups, yc, zc, V, mask) if gate == GATES[0] else fre_from_files(ups, V, mask))
            last = ups
        if last is None:
            refuse("no checkpoint U files under %s; the gate quantity is ABSENT" % case_dir)
        diag = diagnostics_from_files(last, V, mask)
        it_state, it_detail = iterative_state(log, diag)
        pl_state, pl_detail = class_c(ts, vs, "%s/%s" % (name, gate))
        levels.append(dict(name=name, cells=CELLS[name], value=vs[-1]))
        detail.append(dict(name=name, cells=CELLS[name], value=vs[-1], artifact=last, h=EX.h_of(nr),
                           completion=comp, iterative=it_state, iterative_detail=it_detail,
                           plateau=pl_state, plateau_detail=pl_detail, diagnostics_printed_not_gated=diag,
                           yc=yc, zc=zc, V=V, mask=mask))
    fd = detail[-1]
    if gate == GATES[0]:
        pc = plant_control_e2n(fd["artifact"], fd["yc"], fd["zc"], fd["V"], fd["mask"], fd["name"])
    else:
        pc = plant_control_fre(fd["artifact"], fd["V"], fd["mask"], fd["name"])
    for d in detail:
        d.pop("yc"); d.pop("zc"); d.pop("V"); d.pop("mask")
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
    row["ungated_channels_note"] = ("Uy/Uz/p initial residuals and the x-uniformity diagnostic are PRINTED in "
                                    "levels_detail and EXCLUDED from the gate by the freeze (N-AV8)")
    row["gated_by"] = "scripts/roache_triple.py::grade_ladder -- rule 5 is reached through this call and through nothing else"
    if row["verdict"] not in VERDICTS:
        refuse("%s produced a verdict outside the fixed vocabulary: %r" % (gate, row["verdict"]))
    return row


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
    return True, ("%d controls green; both gate quantities shown able to take a passing AND a failing value "
                  "through the real reader on the pinned write format; 0 assert nodes across 4 files; exactly one "
                  "grade_ladder call node; model triples CONVERGING through roache_triple at dim = 3 (L-345); "
                  "iterative floor derived from the predicted fine-level error (L-346); __debug__ True" % len(controls))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs", "F25_DUCT3D_runs"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--prereg-commit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    census = ast_no_asserts([os.path.abspath(__file__), os.path.join(HERE, "exact_f25.py"),
                             os.path.join(HERE, "foam_io_f25.py"), os.path.join(HERE, "build_f25.py")])
    controls = EX.all_controls() + [
        control_class_c_can_say_no(), control_grade_ladder_is_called(),
        control_solver_dicts_match(), control_reader_parses_real_solver_output(),
        control_field_classes_separate(), control_iterative_floor_derived_from_fine_error()]
    bnd = bands()
    demo = demonstrate(bnd)

    if a.selftest:
        ok, why = selftest_predicate(controls, demo, census)
        print(json.dumps(dict(assert_census=census, controls=controls,
                              bands=dict((k, dict(band=v["band"], reference=v["reference"], principle=v["principle"]))
                                         for k, v in bnd.items()),
                              model_levels=EX.predictions(), model_orders=dict(E2n=EX.model_orders()[0], fRe=EX.model_orders()[1]),
                              gate_demonstration=demo, write_path=WRITE_PATH_NOTE,
                              predicate=dict(ok=ok, why=why)), indent=2, default=str))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)      # THE CLAIM IS INSIDE THE PASSING BRANCH.
        return 0

    if not a.prereg_commit:
        refuse("--prereg-commit is required for a real grade (rule 2)")
    rows = [grade_one(a.root, g, bnd) for g in GATES]
    cost = cost_claim(a.root)
    out = a.out or os.path.join(a.root, "F25_GRADED.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(dict(rung="F25-DUCT3D", prereg_commit=a.prereg_commit,
                       prereg="verification/campaign/F25_DUCT3D_PREREGISTRATION.md",
                       assert_census=census, controls=controls, gate_demonstration=demo, write_path=WRITE_PATH_NOTE,
                       cap_core_min=CAP_CORE_MIN,
                       field_classes=dict(PHYSICS_CRITICAL=PHYSICS_CRITICAL, INFRASTRUCTURE=INFRASTRUCTURE),
                       cost_claim=cost, rows=rows), f, indent=2, default=str)
    print("F25 -- SQUARE DUCT, 3-D LADDER -- TALLY")
    print("=" * 78)
    for r in rows:
        print("%-40s %s" % (r["gate"], r["verdict"]))
        for k in ("why", "note"):
            if k in r:
                print("    %s" % r[k])
        for d in r.get("levels_detail", []):
            it = d["iterative_detail"]
            print("    %-7s value %.9g  Ux worst %.3e  UNGATED(printed): Uy %.3e Uz %.3e p %.3e  max|Uy| %.2e max|Uz| %.2e  x-nonuniformity %.2e"
                  % (d["name"], d["value"], it["worst_initial_residuals"]["Ux"], it["ungated_printed"]["Uy"],
                     it["ungated_printed"]["Uz"], it["ungated_printed"]["p"], it["max_abs_Uy"], it["max_abs_Uz"],
                     d["diagnostics_printed_not_gated"]["x_nonuniformity"]))
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
