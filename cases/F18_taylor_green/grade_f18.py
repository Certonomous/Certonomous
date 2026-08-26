#!/usr/bin/env python3
"""
F18 -- THE GRADING PATH for the 2-D Taylor-Green vortex (icoFoam, T = 2 s).
It calls `scripts/roache_triple.py::grade_ladder` and rule 5 is reached through
that call and through NOTHING ELSE (exactly one call node, AST-censused).

REFUSAL DISCIPLINE: `raise` / `sys.exit(2)` only; ZERO `assert` across this
file, exact_f18.py, foam_io_f18.py, build_f18.py (L-332); hard `-O` refusal.

THERE IS NO PLATEAU GATE, AND THAT IS SAID RATHER THAN HIDDEN: the graded
quantities are values at the fixed instant t = T of a decaying transient; there
is no steady state and no period to lock to, so `plateau_states` is passed as
None and recorded as ABSENT (VERIFICATION_CHARTER section 9: an absent
measurement is reported as absent, never as a pass).  Rule 5 limb (1) is a
CENSUS over EVERY time step's final pressure residual against the solver's own
tolerance -- not a two-point sample.

L-342: PHYSICS_CRITICAL and INFRASTRUCTURE field classes are declared below;
gates and refusals read the first only; the second can only refuse the cost
claim and print a BOOKKEEPING DEFECT line.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: grade_f18.py must not run under `python3 -O` (the shared "
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
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)

import roache_triple as RT              # THE GATE.
import exact_f18 as EX                  # THE EXACT SOLUTION and the discretisation model.
import foam_io_f18 as FIO               # THE READERS.

DIM = 2
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
LEVEL_NAMES = [nm for nm, _n, _s in EX.LEVELS]
CELLS = dict((nm, n * n) for nm, n, _s in EX.LEVELS)
STEPS = dict((nm, s) for nm, _n, s in EX.LEVELS)
DT = dict((nm, EX.dt_of(s)) for nm, _n, s in EX.LEVELS)
END_TIME = EX.T_END

BAND_FACTOR = 3.0                       # the one declared parameter; see exact_f18 docstring
P_SOLVER_TOL = 1.0e-9                   # matches system/fvSolution, checked below
CAP_CORE_MIN = 30.0
RANKS = dict(coarse=1, medium=1, fine=1)

PHYSICS_CRITICAL = (
    "log.icoFoam `End` line and `Time =` count (fixed-deltaT identity)",
    "RC.txt (solver rc, written by the launcher in the shell that ran the solver)",
    "<endTime>/U and <endTime>/p present and NEWER than 0/U (age guard)",
    "0/C cell centres",
    "every time step's final p residual in log.icoFoam (rule 5 limb 1 census)",
)
INFRASTRUCTURE = (
    "ClockTime in log.icoFoam (cost actual)",
    "box_before.txt / box_after.txt",
    "MESH_LINE.txt",
    "STATUS.* / launcher.queue.out / LAUNCH_LOG rows written by a queue runner",
    "calibration figures derived from any of the above",
)

WRITE_PATH_NOTE = (
    "OpenFOAM ascii volVectorField `U` at endTime: `internalField nonuniform List<vector>` "
    "NEWLINE N NEWLINE `(` one `(ux uy uz)` per line `)`; pinned against REAL icoFoam output "
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


def e2_from_files(u_path, xc, yc, t=END_TIME):
    """G-F18-1: E2(T) = sqrt(mean |U_h - U_exact(x_c, T)|^2) / U0."""
    U = read_U(u_path)
    if U.shape[0] != len(xc):
        refuse("%s carries %d cells but 0/C carries %d" % (u_path, U.shape[0], len(xc)))
    du = U[:, 0] - EX.u_exact(xc, yc, t)
    dv = U[:, 1] - EX.v_exact(xc, yc, t)
    return float(math.sqrt(np.mean(du ** 2 + dv ** 2)) / EX.U0)


def ke_from_files(u_path):
    """G-F18-2: mean over cells of |U_h|^2 / 2 (uniform cells, so the mean is
    the box-averaged kinetic energy)."""
    U = read_U(u_path)
    return float(np.mean(0.5 * (U[:, 0] ** 2 + U[:, 1] ** 2)))


# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (rule 3)
# ---------------------------------------------------------------------------
def plant_control_e2(u_path, xc, yc, level):
    d = RT.PLANT
    U = read_U(u_path)
    du = U[:, 0] - EX.u_exact(xc, yc, END_TIME)
    dv = U[:, 1] - EX.v_exact(xc, yc, END_TIME)
    before = float(math.sqrt(np.mean(du ** 2 + dv ** 2)) / EX.U0)
    predicted = float(math.sqrt(np.mean((du + d) ** 2 + dv ** 2)) / EX.U0)
    tmp = tempfile.mkdtemp(prefix="f18_plant_e2_")
    try:
        work = os.path.join(tmp, "U")
        if FIO.plant_into_vector_file(u_path, work, 0, d) == 0:
            refuse("nothing to plant into %s" % u_path)
        after = e2_from_files(work, xc, yc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs(after - predicted) > 1e-14:
        refuse("PLANTED-ZERO CONTROL FAILED for E2 on %s: predicted %.17g, reader returned %.17g"
               % (u_path, predicted, after))
    return RT.external_plant_control("e2_from_files", before, after, plant=(predicted - before),
                                     artifact=u_path, level=level)


def plant_control_ke(u_path, level):
    d = RT.PLANT
    U = read_U(u_path)
    before = ke_from_files(u_path)
    predicted = float(np.mean(0.5 * ((U[:, 0] + d) ** 2 + U[:, 1] ** 2)))
    tmp = tempfile.mkdtemp(prefix="f18_plant_ke_")
    try:
        work = os.path.join(tmp, "U")
        if FIO.plant_into_vector_file(u_path, work, 0, d) == 0:
            refuse("nothing to plant into %s" % u_path)
        after = ke_from_files(work)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs(after - predicted) > 1e-14:
        refuse("PLANTED-ZERO CONTROL FAILED for KE on %s: predicted %.17g, reader returned %.17g"
               % (u_path, predicted, after))
    return RT.external_plant_control("ke_from_files", before, after, plant=(predicted - before),
                                     artifact=u_path, level=level)


# ---------------------------------------------------------------------------
# ITERATIVE CONVERGENCE -- census over EVERY time step's final p residual
# ---------------------------------------------------------------------------
TIME_RE = re.compile(r"^Time = ([0-9eE+\-.]+)\s*$", re.M)


def iterative_state(log_path):
    if not os.path.isfile(log_path):
        refuse("no solver log at %s; rule 5 limb (1) cannot be evaluated" % log_path)
    vals = []
    for line in open(log_path, errors="replace"):
        if "Solving for p" in line and "Final residual" in line:
            m = re.search(r"Final residual = ([0-9eE+\-.]+)", line)
            if m:
                vals.append(float(m.group(1)))
    if not vals:
        refuse("no `Solving for p ... Final residual` lines in %s; the iterative state is ABSENT" % log_path)
    bad = [v for v in vals if v > P_SOLVER_TOL]
    detail = dict(basis="per-time-step final p residual, census over ALL steps and correctors",
                  n_readings=len(vals), tolerance=P_SOLVER_TOL, n_above_tolerance=len(bad), worst=max(vals))
    if bad:
        return "NOT_CONVERGED_%d_STEPS_ABOVE_TOL" % len(bad), detail
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
    return dict(out, done=True, end_dir=end_dir,
                why="rc 0; End; latest + dt > endTime; %d `Time` lines == endTime/dt; U, p at endTime newer than 0/U" % len(times))


# ---------------------------------------------------------------------------
# COST CLAIM -- INFRASTRUCTURE only (L-342)
# ---------------------------------------------------------------------------
def cost_claim(root):
    defects, spent = [], 0.0
    for name in LEVEL_NAMES:
        cd = os.path.join(root, name)
        if not os.path.isdir(cd):
            continue
        log = os.path.join(cd, "log.icoFoam")
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
    tmp = tempfile.mkdtemp(prefix="f18_l342_")
    try:
        cd = os.path.join(tmp, "coarse")
        os.makedirs(os.path.join(cd, "0")); os.makedirs(os.path.join(cd, "2"))
        open(os.path.join(cd, "0", "U"), "w").write("x")
        import time as _t
        _t.sleep(0.02)
        n = STEPS["coarse"]; dt = DT["coarse"]
        body = "".join("Time = %.10g\n" % ((i + 1) * dt) for i in range(n)) + "ClockTime = 3 s\nEnd\n"
        open(os.path.join(cd, "log.icoFoam"), "w").write(body)
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        for f in ("U", "p"):
            open(os.path.join(cd, "2", f), "w").write("y")
        good = completion(cd, os.path.join(cd, "log.icoFoam"), "coarse")
        if not good["done"]:
            refuse("L-342 CONTROL: a complete synthetic level was not accepted: %s" % good["why"])
        cc = cost_claim(tmp)
        if cc["core_min_claim"] is not None or not cc["defects"] or not completion(cd, os.path.join(cd, "log.icoFoam"), "coarse")["done"]:
            refuse("L-342 CONTROL: missing infrastructure did not refuse the cost claim with defect lines "
                   "while leaving completion untouched")
        open(os.path.join(cd, "RC.txt"), "w").write("134\n")
        if not completion(cd, os.path.join(cd, "log.icoFoam"), "coarse").get("crashed"):
            refuse("L-342 CONTROL: a non-zero rc did not flip the level to NOT A RESULT")
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        open(os.path.join(cd, "log.icoFoam"), "w").write(body.replace("End\n", ""))
        if not completion(cd, os.path.join(cd, "log.icoFoam"), "coarse").get("crashed"):
            refuse("L-342 CONTROL: a missing End line with rc 0 did not flip the level to NOT A RESULT")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(control="PZ-F18-L342_infrastructure_vs_physics_fields_driven_both_ways",
                infrastructure_deleted="verdict channel unchanged, cost claim refused, defect lines printed",
                physics_corrupted="NOT A RESULT", passed=True)


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
    return dict(control="PZ-F18-GRADE_LADDER_CALLSITE_ast_census_plus_grep_both_ways", ast_call_nodes=calls, passed=True)


def control_solver_dicts_match():
    tp = open(os.path.join(HERE, "case", "constant", "transportProperties")).read()
    m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
    if not m or abs(float(m.group(1)) - EX.NU) > 1e-15:
        refuse("transportProperties nu does not equal exact_f18.NU")
    fs = open(os.path.join(HERE, "case", "system", "fvSolution")).read()
    m = re.search(r"\bp\b[^}]*?tolerance\s+([0-9eE+\-.]+)\s*;", fs, re.S)
    if not m or float(m.group(1)) != P_SOLVER_TOL:
        refuse("P_SOLVER_TOL = %g but fvSolution sets %s" % (P_SOLVER_TOL, m.group(1) if m else None))
    cd = open(os.path.join(HERE, "case", "system", "controlDict.template")).read()
    me = re.search(r"^\s*endTime\s+([0-9.]+)\s*;", cd, re.M)
    if not me or abs(float(me.group(1)) - END_TIME) > 1e-12:
        refuse("controlDict.template endTime is not the registered %g" % END_TIME)
    if not re.search(r"ddtSchemes\s*\{\s*default\s+backward\s*;", open(os.path.join(HERE, "case", "system", "fvSchemes")).read()):
        refuse("fvSchemes ddt is not `backward`; the model integrates BDF2")
    return dict(control="solver_dictionaries_agree_with_registration", nu=EX.NU, p_tol=P_SOLVER_TOL,
                endTime=END_TIME, ddt="backward", passed=True)


def control_reader_parses_real_solver_output():
    if not os.path.isfile(REAL_U_ON_BOX):
        refuse("the real solver output the format is pinned against is absent: %s" % REAL_U_ON_BOX)
    F = FIO.read_field(REAL_U_ON_BOX)
    if F["kind"] != "vector" or F["internal"] is None or F["internal"].shape != (120, 3):
        refuse("reader did not return 120 vectors from %s" % REAL_U_ON_BOX)
    return dict(control="reader_parses_real_solver_written_U_on_this_box", artifact=REAL_U_ON_BOX, cells=120, passed=True)


# ---------------------------------------------------------------------------
# BANDS
# ---------------------------------------------------------------------------
def bands():
    tab = dict((r["name"], r) for r in EX.predictions())
    fine = tab["fine"]
    e2p = fine["E2_pred"]
    ke = EX.ke_norm_exact(END_TIME)
    tol = BAND_FACTOR * abs(fine["ke_err_pred"])
    return {
        "G-F18-1_E2_velocity_L2_at_T": dict(
            band=(e2p / BAND_FACTOR, e2p * BAND_FACTOR), reference=0.0, dim=DIM,
            principle=("discretisation-model prediction E2(T) = %.9e at h_fine = %g, dt = %g (linearised "
                       "discrete equations forced by the exact field's truncation residual, integrated "
                       "with BDF2 at coarse and medium, fine extrapolated with the model order), times [1/%g, %g]"
                       % (e2p, fine["h"], fine["dt"], BAND_FACTOR, BAND_FACTOR))),
        "G-F18-2_mean_kinetic_energy_at_T": dict(
            band=(ke - tol, ke + tol), reference=ke, dim=DIM,
            principle=("exact box-mean kinetic energy at T = U0^2/4 e^{-4 nu T} = %.15f +/- %g x the model's "
                       "predicted KE error (%.9e) = +/- %.9e" % (ke, BAND_FACTOR, fine["ke_err_pred"], tol))),
    }


# ---------------------------------------------------------------------------
# DEMONSTRATION -- both gates able to take a failing AND a passing value
# ---------------------------------------------------------------------------
def synth_case(tmp, n, eu, ev):
    h = EX.h_of(n)
    c = (np.arange(n) + 0.5) * h
    X, Y = np.meshgrid(c, c)
    xc, yc = X.ravel(), Y.ravel()
    U = np.column_stack([EX.u_exact(xc, yc, END_TIME) + eu.ravel(), EX.v_exact(xc, yc, END_TIME) + ev.ravel(),
                         np.zeros(xc.size)])
    up = os.path.join(tmp, "U")
    open(up, "w").write("FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
                        "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
                        "boundaryField { left { type cyclic; } }\n" % FIO.fmt_list(U, "vector"))
    return up, xc, yc


def demonstrate(bnd):
    """ZERO COMPUTE.  The model's MEDIUM error field is integrated; scaled by the
    model's own medium->fine ratio it stands in for the fine field, so the rows
    are format-faithful synthetic files at the medium size."""
    m = EX.model("medium")
    n = m["n"]
    fine = dict((r["name"], r) for r in EX.predictions())["fine"]
    ratio = fine["E2_pred"] / m["E2_pred"]
    rows = []
    tmp = tempfile.mkdtemp(prefix="f18_demo_")
    try:
        for scale, want in ((1.0, "inside"), (40.0, "outside")):
            up, xc, yc = synth_case(tmp, n, scale * ratio * m["eu"], scale * ratio * m["ev"])
            v1 = e2_from_files(up, xc, yc)
            lo, hi = bnd["G-F18-1_E2_velocity_L2_at_T"]["band"]
            rows.append(dict(gate="G-F18-1_E2_velocity_L2_at_T", construction="exact(T) + %g x scaled model error field" % scale,
                             value=v1, band=[lo, hi], inside=bool(lo <= v1 <= hi), intended=want))
            v2 = ke_from_files(up)
            lo, hi = bnd["G-F18-2_mean_kinetic_energy_at_T"]["band"]
            rows.append(dict(gate="G-F18-2_mean_kinetic_energy_at_T", construction="exact(T) + %g x scaled model error field" % scale,
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
GATES = ("G-F18-1_E2_velocity_L2_at_T", "G-F18-2_mean_kinetic_energy_at_T")


def grade_one(root, gate, bnd):
    levels, detail = [], []
    for name in LEVEL_NAMES:
        case_dir = os.path.join(root, name)
        if not os.path.isdir(case_dir):
            return dict(gate=gate, verdict="PENDING", note="level %r absent from %s" % (name, root))
        log = os.path.join(case_dir, "log.icoFoam")
        comp = completion(case_dir, log, name)
        if not comp["done"]:
            verdict = "NOT A RESULT" if comp.get("crashed") else "PENDING"
            return dict(gate=gate, verdict=verdict, note="level %r: %s" % (name, comp["why"]), completion=comp)
        xc, yc = read_centres(case_dir)
        up = os.path.join(comp["end_dir"], "U")
        val = e2_from_files(up, xc, yc) if gate == GATES[0] else ke_from_files(up)
        it_state, it_detail = iterative_state(log)
        levels.append(dict(name=name, cells=CELLS[name], value=val))
        detail.append(dict(name=name, cells=CELLS[name], value=val, artifact=up, h=EX.h_of(int(math.sqrt(CELLS[name]))),
                           dt=DT[name], completion=comp, iterative=it_state, iterative_detail=it_detail,
                           plateau="ABSENT: value at a fixed instant of a transient; no plateau exists to test",
                           xc=xc, yc=yc))
    fd = detail[-1]
    pc = plant_control_e2(fd["artifact"], fd["xc"], fd["yc"], fd["name"]) if gate == GATES[0] \
        else plant_control_ke(fd["artifact"], fd["name"])
    for d in detail:
        d.pop("xc"); d.pop("yc")
    spec = bnd[gate]
    # ---- THE ONE AND ONLY GATE CALL.  plateau_states=None: ABSENT, said so.
    row = RT.grade_ladder(
        quantity=gate, levels=levels, dim=spec["dim"], band=spec["band"], plant_control=pc,
        iterative_states=dict((d["name"], d["iterative"]) for d in detail),
        plateau_states=None, reference=spec["reference"])
    row["gate"] = gate
    row["band_principle"] = spec["principle"]
    row["levels_detail"] = detail
    row["plateau_note"] = "ABSENT by construction (transient value at t = T); reported as absent, not as a pass"
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
    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs", "F18_runs"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--prereg-commit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    census = ast_no_asserts([os.path.abspath(__file__), os.path.join(HERE, "exact_f18.py"),
                             os.path.join(HERE, "foam_io_f18.py"), os.path.join(HERE, "build_f18.py")])
    controls = [EX.control_symbolic_substitution(), EX.control_substitution_is_able_to_fail(),
                EX.control_ladder_is_geometrically_similar(), EX.control_model_is_second_order_and_forced(),
                control_grade_ladder_is_called(), control_solver_dicts_match(),
                control_reader_parses_real_solver_output(), control_field_classes_separate()]
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
    out = a.out or os.path.join(a.root, "F18_GRADED.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(dict(rung="F18-TG2D", prereg_commit=a.prereg_commit,
                       prereg="verification/campaign/F18_TG2D_PREREGISTRATION.md",
                       assert_census=census, controls=controls, gate_demonstration=demo, write_path=WRITE_PATH_NOTE,
                       cap_core_min=CAP_CORE_MIN,
                       field_classes=dict(PHYSICS_CRITICAL=PHYSICS_CRITICAL, INFRASTRUCTURE=INFRASTRUCTURE),
                       cost_claim=cost, rows=rows), f, indent=2, default=str)
    print("F18 -- 2-D TAYLOR-GREEN VORTEX -- TALLY")
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
