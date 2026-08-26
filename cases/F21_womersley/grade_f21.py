#!/usr/bin/env python3
"""
F21 -- THE GRADING PATH for pulsatile Womersley channel flow (pimpleFoam in
PISO mode, alpha = 5, locked phase t = 12.25 T).  It calls
`scripts/roache_triple.py::grade_ladder` and rule 5 is reached through that
call and through NOTHING ELSE (exactly one call node, AST-censused).

REFUSAL DISCIPLINE: `raise` / `sys.exit(2)` only; ZERO `assert` across this
file, exact_f21.py, foam_io_f21.py, build_f21.py (L-332); hard `-O` refusal.

TWO GATES, both at the locked phase, both from ONE declared parameter
(BAND_FACTOR) applied to the discretisation model's prediction:
  G-F21-1  E2 = sqrt(mean |U_h - U_exact|^2) / U_ref over every cell at t = 12.25
  G-F21-2  u/U_ref at the centreline probe (LX/2, 0), bilinear between the four
           surrounding cell centres.  ITS REFERENCE IS THE EXACT FIELD SAMPLED
           AT THE FINE LEVEL'S CELL CENTRES THROUGH THE SAME bilinear() -- the
           F17b AMENDMENT 1 lesson applied at registration, so the stencil's own
           interpolation error cancels and a zero-error solver reads zero.

THE PLATEAU ANALOGUE IS PERIODICITY, and it is measured, not assumed: at every
level the field at t = T_END - PERIOD is read and ||U(T_END) - U(T_END-T)||_2 /
U_ref must be <= PERIOD_TOL, else the level is NOT_PERIODIC and rule 5 limb (1)
turns the row into NOT A RESULT through grade_ladder.  Rule 5 limb (1)'s
iterative part is a CENSUS over EVERY time step's final p and Ux residuals
against the solver's own tolerances.

L-342: PHYSICS_CRITICAL and INFRASTRUCTURE field classes are declared below;
gates and refusals read the first only.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: grade_f21.py must not run under `python3 -O` (the shared "
                     "roache_triple.py seals rule 1 and rule 5 with asserts that -O deletes).\n")
    sys.exit(2)

import os
import re
import ast
import json
import math
import shutil
import tempfile
import argparse

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)

import roache_triple as RT              # THE GATE.
import exact_f21 as EX                  # THE EXACT SOLUTION and the discretisation model.
import foam_io_f21 as FIO               # THE READERS.

DIM = 2
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
LEVEL_NAMES = [nm for nm, _n, _s in EX.LEVELS]
NSIDE = dict((nm, n) for nm, n, _s in EX.LEVELS)
CELLS = dict((nm, n * n) for nm, n, _s in EX.LEVELS)
STEPS = dict((nm, s) for nm, _n, s in EX.LEVELS)
DT = dict((nm, EX.dt_of(s)) for nm, _n, s in EX.LEVELS)
END_TIME = EX.T_END
PREV_PERIOD_TIME = EX.T_END - EX.PERIOD

BAND_FACTOR = 3.0                       # the one declared parameter; see exact_f21 docstring
P_SOLVER_TOL = 1.0e-9                   # matches system/fvSolution, checked below
U_SOLVER_TOL = 1.0e-12                  # matches system/fvSolution, checked below
PERIOD_TOL = 1.0e-5                     # periodicity: ||U(T_END) - U(T_END - T)||_2 / U_ref; a control
                                        # requires it >= 10 x the model's predicted change at every level
CAP_CORE_MIN = 1500.0                   # see the pre-registration section 8
RANKS = dict(coarse=1, medium=1, fine=1)

PHYSICS_CRITICAL = (
    "log.pimpleFoam `End` line and `Time =` count (fixed-deltaT identity)",
    "RC.txt (solver rc, written by the launcher in the shell that ran the solver)",
    "<endTime>/U and <endTime>/p present and NEWER than 0/U (age guard)",
    "<endTime - PERIOD>/U present (the periodicity check)",
    "0/C cell centres",
    "every time step's final p and Ux residual in log.pimpleFoam (rule 5 limb 1 census)",
)
INFRASTRUCTURE = (
    "ClockTime in log.pimpleFoam (cost actual)",
    "box_before.txt / box_after.txt",
    "MESH_LINE.txt",
    "STATUS.* / launcher.queue.out / LAUNCH_LOG rows written by a queue runner",
    "calibration figures derived from any of the above",
)

WRITE_PATH_NOTE = (
    "OpenFOAM ascii volVectorField `U` at a write time: `internalField nonuniform List<vector>` "
    "NEWLINE N NEWLINE `(` one `(ux uy uz)` per line `)`; pinned against REAL solver output "
    "on this box, verification/runs/ansys_verification/VMFL019/L1_30/5/U, parsed at selftest.")
REAL_U_ON_BOX = os.path.join(REPO, "verification", "runs", "ansys_verification", "VMFL019", "L1_30", "5", "U")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# READERS
# ---------------------------------------------------------------------------
def read_centres(case_dir):
    path = os.path.join(case_dir, "0", "C")
    if not os.path.isfile(path):
        refuse("no cell-centre file at %s; the gate quantity is ABSENT without it" % path)
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
        refuse("%s has only %d cells" % (path, F["internal"].shape[0]))
    return F["internal"]


def structured(xc, yc, n):
    """Map unstructured cell centres onto (n, n) index arrays; refuse on any
    collision or gap so a wrong ordering cannot be silently graded."""
    h = EX.h_of(n)
    ii = np.rint(xc / h - 0.5).astype(int)
    jj = np.rint((yc + EX.H) / h - 0.5).astype(int)
    if np.max(np.abs(xc / h - 0.5 - ii)) > 1e-6 or np.max(np.abs((yc + EX.H) / h - 0.5 - jj)) > 1e-6:
        refuse("cell centres do not sit on the registered uniform %dx%d grid" % (n, n))
    if ii.min() < 0 or ii.max() >= n or jj.min() < 0 or jj.max() >= n:
        refuse("cell-centre indices outside the %dx%d grid" % (n, n))
    flat = jj * n + ii
    if len(np.unique(flat)) != n * n or len(flat) != n * n:
        refuse("cell centres do not cover the %dx%d grid exactly once" % (n, n))
    return ii, jj


def e2_from_files(u_path, xc, yc, t=END_TIME):
    """G-F21-1: E2 = sqrt(mean |U_h - U_exact(x_c, y_c, t)|^2) / U_ref."""
    U = read_U(u_path)
    if U.shape[0] != len(xc):
        refuse("%s carries %d cells but 0/C carries %d" % (u_path, U.shape[0], len(xc)))
    du = U[:, 0] - EX.u_exact(xc, yc, t)
    dv = U[:, 1] - EX.v_exact(xc, yc, t)
    return float(math.sqrt(np.mean(du ** 2 + dv ** 2)) / EX.U_REF)


def u_probe_from_files(u_path, xc, yc, n):
    """G-F21-2: u/U_ref at the centreline probe, bilinear between the four
    surrounding cell centres."""
    U = read_U(u_path)
    if U.shape[0] != len(xc):
        refuse("%s carries %d cells but 0/C carries %d" % (u_path, U.shape[0], len(xc)))
    ii, jj = structured(xc, yc, n)
    F = np.empty((n, n))
    F[jj, ii] = U[:, 0]
    _h, xg, yg = EX.centres(n)
    return float(EX.bilinear(xg, yg, F, EX.PROBE[0], EX.PROBE[1]) / EX.U_REF)


def u_probe_reference(n):
    """The G-F21-2 REFERENCE: the exact field at the level's own cell centres
    through the SAME bilinear() the solved field goes through (F17b AMENDMENT 1
    applied at registration)."""
    _h, xg, yg = EX.centres(n)
    X, Y = np.meshgrid(xg, yg)
    return float(EX.bilinear(xg, yg, EX.u_exact(X, Y, END_TIME), EX.PROBE[0], EX.PROBE[1]) / EX.U_REF)


def period_change_from_files(u_end, u_prev, xc, yc):
    """||U(T_END) - U(T_END - T)||_2 / U_ref over every cell."""
    A = read_U(u_end); B = read_U(u_prev)
    if A.shape != B.shape or A.shape[0] != len(xc):
        refuse("%s and %s do not carry the same %d cells" % (u_end, u_prev, len(xc)))
    d = A[:, :2] - B[:, :2]
    return float(math.sqrt(np.mean(d[:, 0] ** 2 + d[:, 1] ** 2)) / EX.U_REF)


# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (rule 3) -- into the REAL artifact format, read back
# with the REAL parser, refusing with exit 2.
# ---------------------------------------------------------------------------
def plant_control_e2(u_path, xc, yc, level):
    d = RT.PLANT
    U = read_U(u_path)
    du = U[:, 0] - EX.u_exact(xc, yc, END_TIME)
    dv = U[:, 1] - EX.v_exact(xc, yc, END_TIME)
    before = float(math.sqrt(np.mean(du ** 2 + dv ** 2)) / EX.U_REF)
    predicted = float(math.sqrt(np.mean((du + d) ** 2 + dv ** 2)) / EX.U_REF)
    tmp = tempfile.mkdtemp(prefix="f21_plant_e2_")
    try:
        work = os.path.join(tmp, "U")
        if FIO.plant_into_vector_file(u_path, work, 0, d) == 0:
            refuse("nothing to plant into %s" % u_path)
        after = e2_from_files(work, xc, yc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs(after - predicted) > 1e-13:
        refuse("PLANTED-ZERO CONTROL FAILED for E2 on %s: predicted %.17g, reader returned %.17g"
               % (u_path, predicted, after))
    return RT.external_plant_control("e2_from_files", before, after, plant=(predicted - before),
                                     artifact=u_path, level=level)


def plant_control_u_probe(u_path, xc, yc, n, level):
    d = RT.PLANT
    before = u_probe_from_files(u_path, xc, yc, n)
    tmp = tempfile.mkdtemp(prefix="f21_plant_up_")
    try:
        work = os.path.join(tmp, "U")
        if FIO.plant_into_vector_file(u_path, work, 0, d) == 0:
            refuse("nothing to plant into %s" % u_path)
        after = u_probe_from_files(work, xc, yc, n)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs((after - before) - d / EX.U_REF) > 1e-11:
        refuse("PLANTED-ZERO CONTROL FAILED for u(probe) on %s: a Ux offset of %.6e must move the "
               "interpolated value by exactly %.6e; the reader moved it %.6e" % (u_path, d, d / EX.U_REF, after - before))
    return RT.external_plant_control("u_probe_from_files", before, after, plant=d / EX.U_REF,
                                     artifact=u_path, level=level)


# ---------------------------------------------------------------------------
# ITERATIVE CONVERGENCE -- census over EVERY time step's final residuals
# ---------------------------------------------------------------------------
TIME_RE = re.compile(r"^Time = ([0-9eE+\-.]+)\s*$", re.M)
FINAL_RE = re.compile(r"Solving for (p|Ux), Initial residual = [0-9eE+\-.]+, Final residual = ([0-9eE+\-.]+)")


def iterative_state(log_path):
    if not os.path.isfile(log_path):
        refuse("no solver log at %s; rule 5 limb (1) cannot be evaluated" % log_path)
    vals = dict(p=[], Ux=[])
    for line in open(log_path, errors="replace"):
        m = FINAL_RE.search(line)
        if m:
            vals[m.group(1)].append(float(m.group(2)))
    for k in ("p", "Ux"):
        if not vals[k]:
            refuse("no `Solving for %s ... Final residual` lines in %s; the iterative state is ABSENT" % (k, log_path))
    bad = dict(p=sum(1 for v in vals["p"] if v > P_SOLVER_TOL), Ux=sum(1 for v in vals["Ux"] if v > U_SOLVER_TOL))
    detail = dict(basis="per-time-step final p and Ux residuals, census over ALL steps and correctors",
                  n_readings=dict(p=len(vals["p"]), Ux=len(vals["Ux"])),
                  tolerances=dict(p=P_SOLVER_TOL, Ux=U_SOLVER_TOL), n_above_tolerance=bad,
                  worst=dict(p=max(vals["p"]), Ux=max(vals["Ux"])))
    nb = bad["p"] + bad["Ux"]
    if nb:
        return "NOT_CONVERGED_%d_READINGS_ABOVE_TOL" % nb, detail
    return "CONVERGED", detail


def period_state(case_dir, comp, xc, yc):
    """The plateau analogue: PLATEAUED iff the field at T_END equals the field
    one period earlier to PERIOD_TOL (relative to U_ref, L2 over cells)."""
    u_end = os.path.join(comp["end_dir"], "U")
    u_prev = os.path.join(comp["prev_dir"], "U")
    change = period_change_from_files(u_end, u_prev, xc, yc)
    detail = dict(basis="||U(T_END) - U(T_END - PERIOD)||_2 / U_ref over every cell", change=change,
                  tolerance=PERIOD_TOL, artifacts=[u_end, u_prev])
    if change > PERIOD_TOL:
        return "NOT_PERIODIC_change_%.3e_above_%.1e" % (change, PERIOD_TOL), detail
    return "PLATEAUED", detail


def control_period_check_can_say_no():
    """Driven: two synthetic files differing by a uniform Ux offset PLANT read
    back as exactly PLANT/U_ref; the state flips at the registered tolerance;
    and PERIOD_TOL is at least 10x the model's predicted change at every level."""
    n = 16
    tmp = tempfile.mkdtemp(prefix="f21_period_")
    try:
        z = np.zeros((n, n))
        up, xc, yc = synth_case(tmp, n, z, z, name="U_a")
        d = RT.PLANT
        work = os.path.join(tmp, "U_b")
        FIO.plant_into_vector_file(up, work, 0, d)
        change = period_change_from_files(work, up, xc, yc)
        same = period_change_from_files(up, up, xc, yc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs(change - d / EX.U_REF) > 1e-12 or same != 0.0:
        refuse("PERIODICITY CONTROL FAILED: planted %.6e read back as %.6e (identical files: %.3e)"
               % (d / EX.U_REF, change, same))
    if not (change > PERIOD_TOL):
        refuse("PERIODICITY CONTROL FAILED: the planted change %.3e is not above PERIOD_TOL %.1e" % (change, PERIOD_TOL))
    worst = max(r["period_change_pred"] for r in EX.predictions())
    if PERIOD_TOL < 10.0 * worst:
        refuse("PERIOD_TOL %.1e is below 10x the model's predicted period-to-period change %.3e" % (PERIOD_TOL, worst))
    return dict(control="PZ-F21-PERIODICITY_planted_change_read_back_and_tolerance_above_10x_model",
                planted=d / EX.U_REF, read_back=change, identical_files=same, tolerance=PERIOD_TOL,
                model_worst_predicted_change=worst, passed=True)


def control_probe_reference_same_stencil():
    """Driven: the exact field written in the real format at the FINE size and
    read through the real probe reader returns ZERO error against the
    reference (to round-off); a planted Ux perturbation is read back exactly."""
    n = NSIDE["fine"]
    ref = u_probe_reference(n)
    d = RT.PLANT
    tmp = tempfile.mkdtemp(prefix="f21_ref_")
    try:
        z = np.zeros((n, n))
        up, xc, yc = synth_case(tmp, n, z, z)
        v0 = u_probe_from_files(up, xc, yc, n)
        work = os.path.join(tmp, "U_planted")
        if FIO.plant_into_vector_file(up, work, 0, d) == 0:
            refuse("nothing to plant into %s" % up)
        v1 = u_probe_from_files(work, xc, yc, n)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs(v0 - ref) > 1e-12:
        refuse("SAME-STENCIL REFERENCE CONTROL FAILED: exact field read back as %.17g against reference %.17g" % (v0, ref))
    if abs((v1 - ref) - d / EX.U_REF) > 1e-11:
        refuse("SAME-STENCIL REFERENCE CONTROL FAILED: planted %.6e read back as %.6e" % (d / EX.U_REF, v1 - ref))
    return dict(control="PZ-F21-PROBE_reference_same_stencil_zero_error_and_plant_read_back", reference=ref,
                pointwise_exact=EX.u_probe_exact(), stencil_error=ref - EX.u_probe_exact(),
                zero_error_readback=v0 - ref, planted_readback=v1 - ref, passed=True)


# ---------------------------------------------------------------------------
# COMPLETION -- rule 4, PHYSICS_CRITICAL fields only
# ---------------------------------------------------------------------------
def _time_dir(case_dir, t):
    for d in os.listdir(case_dir):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and abs(float(d) - t) < 1e-9:
            return os.path.join(case_dir, d)
    return None


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
    if "End" not in text:
        return dict(out, done=False, crashed=True, why="rc 0 recorded but no `End` line: NOT A RESULT")
    if not (times[-1] + dt > END_TIME):
        return dict(out, done=False, why="latest %.9g + dt %.9g does not exceed endTime %.9g" % (times[-1], dt, END_TIME))
    expected = int(round(END_TIME / dt))
    if len(times) != expected:
        return dict(out, done=False, why="fixed-deltaT identity fails: %d `Time` lines, endTime/dt = %d"
                                          % (len(times), expected))
    zero_u = os.path.join(case_dir, "0", "U")
    if not os.path.isfile(zero_u):
        return dict(out, done=False, why="no 0/U to date the launch against")
    t0 = os.path.getmtime(zero_u)
    end_dir = _time_dir(case_dir, END_TIME)
    if end_dir is None:
        return dict(out, done=False, why="no time directory at endTime %g" % END_TIME)
    prev_dir = _time_dir(case_dir, PREV_PERIOD_TIME)
    if prev_dir is None or not os.path.isfile(os.path.join(prev_dir, "U")):
        return dict(out, done=False, why="no U at t = endTime - PERIOD = %g: the periodicity check is ABSENT" % PREV_PERIOD_TIME)
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
    return dict(out, done=True, end_dir=end_dir, prev_dir=prev_dir,
                why="rc 0; End; latest + dt > endTime; %d `Time` lines == endTime/dt; U, p at endTime newer than 0/U; "
                    "U at endTime - PERIOD present" % len(times))


# ---------------------------------------------------------------------------
# COST CLAIM -- INFRASTRUCTURE only (L-342)
# ---------------------------------------------------------------------------
def cost_claim(root):
    defects, spent = [], 0.0
    for name in LEVEL_NAMES:
        cd = os.path.join(root, name)
        if not os.path.isdir(cd):
            continue
        log = os.path.join(cd, "log.pimpleFoam")
        hits = re.findall(r"ClockTime = ([0-9]+) s", open(log, errors="replace").read()) if os.path.isfile(log) else []
        if not hits:
            defects.append("BOOKKEEPING DEFECT: level %s has no ClockTime reading; cost actual NOT MEASURED" % name)
        else:
            spent += float(hits[-1]) * RANKS[name] / 60.0
        for probe in ("box_before.txt", "box_after.txt", "MESH_LINE.txt"):
            if not os.path.isfile(os.path.join(cd, probe)):
                defects.append("BOOKKEEPING DEFECT: level %s lacks %s; NOT MEASURED" % (name, probe))
    return dict(fields="INFRASTRUCTURE", core_min_claim=None if defects else spent, partial_sum_core_min=spent,
                cap_core_min=CAP_CORE_MIN, defects=defects,
                note="ClockTime x ranks / 60; dollars at $0.0513/core-h DERIVED, NOT MEASURED")


def control_field_classes_separate():
    tmp = tempfile.mkdtemp(prefix="f21_l342_")
    try:
        cd = os.path.join(tmp, "coarse")
        os.makedirs(os.path.join(cd, "0")); os.makedirs(os.path.join(cd, "12.25")); os.makedirs(os.path.join(cd, "11.25"))
        open(os.path.join(cd, "0", "U"), "w").write("x")
        import time as _t
        _t.sleep(0.02)
        n = STEPS["coarse"]; dt = DT["coarse"]
        body = "".join("Time = %.10g\n" % ((i + 1) * dt) for i in range(n)) + "ClockTime = 3 s\nEnd\n"
        open(os.path.join(cd, "log.pimpleFoam"), "w").write(body)
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        for f in ("U", "p"):
            open(os.path.join(cd, "12.25", f), "w").write("y")
        open(os.path.join(cd, "11.25", "U"), "w").write("y")
        good = completion(cd, os.path.join(cd, "log.pimpleFoam"), "coarse")
        if not good["done"]:
            refuse("L-342 CONTROL: a complete synthetic level was not accepted: %s" % good["why"])
        cc = cost_claim(tmp)
        if cc["core_min_claim"] is not None or not cc["defects"] or not completion(cd, os.path.join(cd, "log.pimpleFoam"), "coarse")["done"]:
            refuse("L-342 CONTROL: missing infrastructure did not refuse the cost claim with defect lines "
                   "while leaving completion untouched")
        os.remove(os.path.join(cd, "11.25", "U"))
        if completion(cd, os.path.join(cd, "log.pimpleFoam"), "coarse")["done"]:
            refuse("L-342 CONTROL: a missing U at endTime - PERIOD was accepted as complete")
        open(os.path.join(cd, "11.25", "U"), "w").write("y")
        open(os.path.join(cd, "RC.txt"), "w").write("134\n")
        if not completion(cd, os.path.join(cd, "log.pimpleFoam"), "coarse").get("crashed"):
            refuse("L-342 CONTROL: a non-zero rc did not flip the level to NOT A RESULT")
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        open(os.path.join(cd, "log.pimpleFoam"), "w").write(body.replace("End\n", ""))
        if not completion(cd, os.path.join(cd, "log.pimpleFoam"), "coarse").get("crashed"):
            refuse("L-342 CONTROL: a missing End line with rc 0 did not flip the level to NOT A RESULT")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(control="PZ-F21-L342_infrastructure_vs_physics_fields_driven_both_ways",
                infrastructure_deleted="verdict channel unchanged, cost claim refused, defect lines printed",
                physics_corrupted="NOT A RESULT", missing_prev_period_U="not complete", passed=True)


def control_iterative_census_can_say_no():
    tmp = tempfile.mkdtemp(prefix="f21_iter_")
    try:
        lg = os.path.join(tmp, "log")
        good = ("Time = 0.01\nPBiCGStab:  Solving for Ux, Initial residual = 1, Final residual = 5e-13, No Iterations 3\n"
                "DICPCG:  Solving for p, Initial residual = 0.5, Final residual = 9e-10, No Iterations 40\n"
                "DICPCG:  Solving for p, Initial residual = 0.1, Final residual = 8e-10, No Iterations 30\n")
        open(lg, "w").write(good * 3)
        s1, _ = iterative_state(lg)
        open(lg, "w").write(good * 2 + good.replace("Final residual = 8e-10", "Final residual = 2e-09"))
        s2, d2 = iterative_state(lg)
        open(lg, "w").write(good * 2 + good.replace("Final residual = 5e-13", "Final residual = 3e-12"))
        s3, _ = iterative_state(lg)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if s1 != "CONVERGED" or not s2.startswith("NOT_CONVERGED_1") or not s3.startswith("NOT_CONVERGED_1"):
        refuse("ITERATIVE CENSUS CONTROL FAILED: %s / %s / %s" % (s1, s2, s3))
    return dict(control="PZ-F21-ITERATIVE_census_flags_one_bad_p_and_one_bad_Ux_reading", clean=s1, bad_p=s2, bad_Ux=s3,
                passed=True)


# ---------------------------------------------------------------------------
# CENSUSES / CONTROLS ON THE INSTRUMENT ITSELF
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
    return dict(control="PZ-F21-GRADE_LADDER_CALLSITE_ast_census_plus_grep_both_ways", ast_call_nodes=calls, passed=True)


def control_solver_dicts_match():
    tp = open(os.path.join(HERE, "case", "constant", "transportProperties")).read()
    m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
    if not m or abs(float(m.group(1)) - EX.NU) > 1e-15:
        refuse("transportProperties nu does not equal exact_f21.NU = %.17g" % EX.NU)
    if not re.search(r"simulationType\s+laminar\s*;", open(os.path.join(HERE, "case", "constant", "turbulenceProperties")).read()):
        refuse("turbulenceProperties is not laminar")
    fs = open(os.path.join(HERE, "case", "system", "fvSolution")).read()
    m = re.search(r"\bp\b[^}]*?tolerance\s+([0-9eE+\-.]+)\s*;", fs, re.S)
    if not m or float(m.group(1)) != P_SOLVER_TOL:
        refuse("P_SOLVER_TOL = %g but fvSolution sets %s" % (P_SOLVER_TOL, m.group(1) if m else None))
    m = re.search(r"\(U\|UFinal\)\"[^}]*?tolerance\s+([0-9eE+\-.]+)\s*;", fs, re.S)
    if not m or float(m.group(1)) != U_SOLVER_TOL:
        refuse("U_SOLVER_TOL = %g but fvSolution sets %s" % (U_SOLVER_TOL, m.group(1) if m else None))
    if not re.search(r"nOuterCorrectors\s+1\s*;", fs):
        refuse("PIMPLE nOuterCorrectors is not 1 (PISO mode is registered)")
    cd = open(os.path.join(HERE, "case", "system", "controlDict.template")).read()
    me = re.search(r"^\s*endTime\s+([0-9.]+)\s*;", cd, re.M)
    if not me or abs(float(me.group(1)) - END_TIME) > 1e-12:
        refuse("controlDict.template endTime is not the registered %g" % END_TIME)
    mw = re.search(r"^\s*writeInterval\s+([0-9.]+)\s*;", cd, re.M)
    if not mw or abs(EX.PERIOD / float(mw.group(1)) - round(EX.PERIOD / float(mw.group(1)))) > 1e-12 \
            or abs(END_TIME / float(mw.group(1)) - round(END_TIME / float(mw.group(1)))) > 1e-12:
        refuse("writeInterval does not divide both PERIOD and endTime; t = endTime - PERIOD would not be written")
    if not re.search(r"application\s+pimpleFoam\s*;", cd):
        refuse("controlDict.template application is not pimpleFoam")
    if not re.search(r"ddtSchemes\s*\{\s*default\s+backward\s*;", open(os.path.join(HERE, "case", "system", "fvSchemes")).read()):
        refuse("fvSchemes ddt is not `backward`; the model integrates BDF2")
    fo = open(os.path.join(HERE, "case", "system", "fvOptions")).read()
    mf = re.search(r"type\s+cosine\s*;\s*frequency\s+([0-9.eE+\-]+)\s*;\s*amplitude\s+([0-9.eE+\-]+)\s*;\s*scale\s+\(\s*1\s+0\s+0\s*\)", fo)
    if not mf or abs(float(mf.group(1)) - EX.OMEGA / (2 * math.pi)) > 1e-15 or abs(float(mf.group(2)) - EX.A_DRIVE) > 1e-15:
        refuse("fvOptions does not carry the registered cosine drive (frequency omega/2pi = %.17g, amplitude %g, x-hat)"
               % (EX.OMEGA / (2 * math.pi), EX.A_DRIVE))
    if not re.search(r"volumeMode\s+specific\s*;", fo) or not re.search(r"selectionMode\s+all\s*;", fo):
        refuse("fvOptions drive is not a specific (per-volume) source over all cells")
    return dict(control="solver_dictionaries_agree_with_registration", nu=EX.NU, p_tol=P_SOLVER_TOL, U_tol=U_SOLVER_TOL,
                endTime=END_TIME, ddt="backward", drive="cosine f=1 A=1 x-hat, specific, all", passed=True)


def control_reader_parses_real_solver_output():
    if not os.path.isfile(REAL_U_ON_BOX):
        refuse("the real solver output the format is pinned against is absent: %s" % REAL_U_ON_BOX)
    F = FIO.read_field(REAL_U_ON_BOX)
    if F["kind"] != "vector" or F["internal"] is None or F["internal"].shape != (120, 3):
        refuse("reader did not return 120 vectors from %s" % REAL_U_ON_BOX)
    return dict(control="reader_parses_real_solver_written_U_on_this_box", artifact=REAL_U_ON_BOX, cells=120, passed=True)


# ---------------------------------------------------------------------------
# BANDS -- both from ONE declared parameter applied to the model prediction
# ---------------------------------------------------------------------------
def bands():
    tab = dict((r["name"], r) for r in EX.predictions())
    fine = tab["fine"]
    e2p = fine["E2_pred"]
    up = u_probe_reference(NSIDE["fine"])
    tol = BAND_FACTOR * abs(fine["probe_err_pred"])
    return {
        "G-F21-1_E2_velocity_locked_phase": dict(
            band=(e2p / BAND_FACTOR, e2p * BAND_FACTOR), reference=0.0, dim=DIM,
            principle=("discretisation-model prediction E2 = %.9e at h_fine = %g, dt = %g, t = %g (the solver's own "
                       "1-D FV/BDF2 discretisation solved on the coarse and medium grids, fine extrapolated with the "
                       "model order), times [1/%g, %g]" % (e2p, fine["h"], fine["dt"], END_TIME, BAND_FACTOR, BAND_FACTOR))),
        "G-F21-2_u_centreline_locked_phase": dict(
            band=(up - tol, up + tol), reference=up, dim=DIM,
            principle=("exact field sampled at the fine level's cell centres and interpolated by the grader's own "
                       "bilinear() at (%g, %g), t = %g: u/U_ref = %.15f (pointwise exact %.15f) +/- %g x the model's "
                       "predicted pointwise error there (%.9e) = +/- %.9e"
                       % (EX.PROBE[0], EX.PROBE[1], END_TIME, up, EX.u_probe_exact(), BAND_FACTOR, fine["probe_err_pred"], tol))),
    }


# ---------------------------------------------------------------------------
# DEMONSTRATION -- both gates able to take a failing AND a passing value
# ---------------------------------------------------------------------------
def synth_case(tmp, n, eu, ev, name="U"):
    """Write 0/C and a U file (exact(T_END) + error field) in the real format."""
    _h, xg, yg = EX.centres(n)
    X, Y = np.meshgrid(xg, yg)
    xc, yc = X.ravel(), Y.ravel()
    U = np.column_stack([EX.u_exact(xc, yc, END_TIME) + eu.ravel(), EX.v_exact(xc, yc, END_TIME) + ev.ravel(),
                         np.zeros(xc.size)])
    up = os.path.join(tmp, name)
    open(up, "w").write("FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
                        "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
                        "boundaryField { left { type cyclic; } }\n" % FIO.fmt_list(U, "vector"))
    return up, xc, yc


def demonstrate(bnd):
    """ZERO COMPUTE.  The finest SOLVED grid's 1-D error profile, prolongated
    piecewise-constant onto the FINE grid (constant in x) and scaled by the
    model's solved->fine E2 ratio, stands in for the fine field -- built AT the
    fine size so the probe's own bilinear interpolation is the fine level's."""
    m = EX.solved(*EX.MODEL_GRIDS[-1])
    n = NSIDE["fine"]
    k = n // m["n"]
    if k * m["n"] != n:
        refuse("fine grid %d is not an integer refinement of the solved %d" % (n, m["n"]))
    fine = dict((r["name"], r) for r in EX.predictions())["fine"]
    ratio = fine["E2_pred"] / m["E2_pred"]
    eu = np.repeat(m["eu"], k)[:, None] * np.ones((1, n))          # (n, n): rows = y
    ev = np.zeros((n, n))
    rows = []
    tmp = tempfile.mkdtemp(prefix="f21_demo_")
    try:
        for scale, want in ((1.0, "inside"), (40.0, "outside")):
            up, xc, yc = synth_case(tmp, n, scale * ratio * eu, scale * ratio * ev)
            v1 = e2_from_files(up, xc, yc)
            lo, hi = bnd["G-F21-1_E2_velocity_locked_phase"]["band"]
            rows.append(dict(gate="G-F21-1_E2_velocity_locked_phase", construction="exact(T) + %g x scaled model error field" % scale,
                             value=v1, band=[lo, hi], inside=bool(lo <= v1 <= hi), intended=want))
            v2 = u_probe_from_files(up, xc, yc, n)
            lo, hi = bnd["G-F21-2_u_centreline_locked_phase"]["band"]
            rows.append(dict(gate="G-F21-2_u_centreline_locked_phase", construction="exact(T) + %g x scaled model error field" % scale,
                             value=v2, band=[lo, hi], inside=bool(lo <= v2 <= hi), intended=want))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for r in rows:
        if (r["intended"] == "inside") != r["inside"]:
            refuse("GATE DEMONSTRATION FAILED for %s: intended %s, got %.6g against %s"
                   % (r["gate"], r["intended"], r["value"], r["band"]))
    seen = set((r["gate"], r["inside"]) for r in rows)
    for g in bnd:
        if (g, True) not in seen or (g, False) not in seen:
            refuse("gate %s was not shown able to take BOTH values" % g)
    return rows


# ---------------------------------------------------------------------------
# THE GRADE
# ---------------------------------------------------------------------------
GATES = ("G-F21-1_E2_velocity_locked_phase", "G-F21-2_u_centreline_locked_phase")


def grade_one(root, gate, bnd):
    levels, detail = [], []
    for name in LEVEL_NAMES:
        case_dir = os.path.join(root, name)
        if not os.path.isdir(case_dir):
            return dict(gate=gate, verdict="PENDING", note="level %r absent from %s" % (name, root))
        log = os.path.join(case_dir, "log.pimpleFoam")
        comp = completion(case_dir, log, name)
        if not comp["done"]:
            verdict = "NOT A RESULT" if comp.get("crashed") else "PENDING"
            return dict(gate=gate, verdict=verdict, note="level %r: %s" % (name, comp["why"]), completion=comp)
        xc, yc = read_centres(case_dir)
        n = NSIDE[name]
        up = os.path.join(comp["end_dir"], "U")
        val = e2_from_files(up, xc, yc) if gate == GATES[0] else u_probe_from_files(up, xc, yc, n)
        it_state, it_detail = iterative_state(log)
        pd_state, pd_detail = period_state(case_dir, comp, xc, yc)
        levels.append(dict(name=name, cells=CELLS[name], value=val))
        detail.append(dict(name=name, cells=CELLS[name], value=val, artifact=up, h=EX.h_of(n), dt=DT[name],
                           completion=comp, iterative=it_state, iterative_detail=it_detail,
                           plateau=pd_state, plateau_detail=pd_detail, n=n, xc=xc, yc=yc))
    fd = detail[-1]
    pc = plant_control_e2(fd["artifact"], fd["xc"], fd["yc"], fd["name"]) if gate == GATES[0] \
        else plant_control_u_probe(fd["artifact"], fd["xc"], fd["yc"], fd["n"], fd["name"])
    for d in detail:
        d.pop("xc"); d.pop("yc")
    spec = bnd[gate]
    # ---- THE ONE AND ONLY GATE CALL.  plateau = periodicity, measured at every level.
    row = RT.grade_ladder(
        quantity=gate, levels=levels, dim=spec["dim"], band=spec["band"], plant_control=pc,
        iterative_states=dict((d["name"], d["iterative"]) for d in detail),
        plateau_states=dict((d["name"], d["plateau"]) for d in detail),
        reference=spec["reference"])
    row["gate"] = gate
    row["band_principle"] = spec["principle"]
    row["levels_detail"] = detail
    row["plateau_note"] = "periodicity: ||U(T_END) - U(T_END - PERIOD)||_2 / U_ref <= %g at every level" % PERIOD_TOL
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
                  "through the real reader on the pinned write format; 0 assert nodes across 4 files; exactly "
                  "one grade_ladder call node; __debug__ True" % len(controls))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs", "F21_runs"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--prereg-commit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    census = ast_no_asserts([os.path.abspath(__file__), os.path.join(HERE, "exact_f21.py"),
                             os.path.join(HERE, "foam_io_f21.py"), os.path.join(HERE, "build_f21.py")])
    controls = [EX.control_symbolic_substitution(), EX.control_substitution_is_able_to_fail(),
                EX.control_ladder_is_geometrically_similar(), EX.control_model_is_second_order_and_sensitive(),
                control_grade_ladder_is_called(), control_solver_dicts_match(),
                control_reader_parses_real_solver_output(), control_field_classes_separate(),
                control_iterative_census_can_say_no(), control_period_check_can_say_no(),
                control_probe_reference_same_stencil()]
    bnd = bands()
    demo = demonstrate(bnd)

    if a.selftest:
        ok, why = selftest_predicate(controls, demo, census)
        print(json.dumps(dict(assert_census=census, controls=controls,
                              bands=dict((k, dict(band=v["band"], reference=v["reference"], principle=v["principle"]))
                                         for k, v in bnd.items()),
                              model_levels=EX.predictions(), gate_demonstration=demo, write_path=WRITE_PATH_NOTE,
                              predicate=dict(ok=ok, why=why)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0

    if not a.prereg_commit:
        refuse("--prereg-commit is required for a real grade (rule 2)")
    rows = [grade_one(a.root, g, bnd) for g in GATES]
    cost = cost_claim(a.root)
    out = a.out or os.path.join(a.root, "F21_GRADED.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(dict(rung="F21-WOMERSLEY", prereg_commit=a.prereg_commit,
                       prereg="verification/campaign/F21_WOMERSLEY_PREREGISTRATION.md",
                       assert_census=census, controls=controls, gate_demonstration=demo, write_path=WRITE_PATH_NOTE,
                       cap_core_min=CAP_CORE_MIN,
                       field_classes=dict(PHYSICS_CRITICAL=PHYSICS_CRITICAL, INFRASTRUCTURE=INFRASTRUCTURE),
                       cost_claim=cost, rows=rows), f, indent=2, default=str)
    print("F21 -- WOMERSLEY PULSATILE CHANNEL FLOW -- TALLY")
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
