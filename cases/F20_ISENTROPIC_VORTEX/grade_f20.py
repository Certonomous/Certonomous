#!/usr/bin/env python3
"""
F20 -- THE GRADING PATH for the 2-D isentropic vortex (rhoCentralFoam, one
period, t = 10).  Lineage: cases/F19_SOD/grade_f19.py.  It calls
`scripts/roache_triple.py::grade_ladder` and rule 5 is reached through that
call and through NOTHING ELSE (exactly one call node, AST-censused).

REFUSAL DISCIPLINE: `raise` / `sys.exit(2)` only; ZERO `assert` across this
file, exact_f20.py, foam_io_f20.py, build_f20.py (L-332); hard `-O` refusal.

THERE IS NO PLATEAU GATE, AND THAT IS SAID RATHER THAN HIDDEN: the graded
quantities are values at the fixed instant t = 10 of a transient; there is
no steady state, so `plateau_states` is passed as None and recorded ABSENT
(VERIFICATION_CHARTER section 9).  Rule 5 limb (1): the case is INVISCID and
rhoCentralFoam performs no linear solve, so NO iterative residual exists
(F15's grader says the same); limb (1) is evaluated as a STABILITY CENSUS over
every time step's `max Courant Number` line against the registered ceiling,
with the line count required to equal the step count, and is named as such.

L-342: PHYSICS_CRITICAL and INFRASTRUCTURE field classes are declared below;
gates and refusals read the first only; the second can only refuse the cost
claim and print a BOOKKEEPING DEFECT line.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: grade_f20.py must not run under `python3 -O` (the shared "
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

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)

import roache_triple as RT              # THE GATE.
import exact_f20 as EX                  # THE EXACT SOLUTION and the discretisation model.
import foam_io_f20 as FIO               # THE READERS.

DIM = 2
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
LEVEL_NAMES = [nm for nm, _n, _s in EX.LEVELS]
CELLS = dict((nm, n * n) for nm, n, _s in EX.LEVELS)
STEPS = dict((nm, s) for nm, _n, s in EX.LEVELS)
DT = dict((nm, EX.dt_of(s)) for nm, _n, s in EX.LEVELS)
END_TIME = EX.T_END

BAND_FACTOR = 3.0                       # the one declared parameter; see exact_f20 docstring
CO_CEILING = EX.CO_CEILING              # on the solver-reported Courant number
CAP_CORE_MIN = 240.0
RANKS = dict(coarse=1, medium=1, fine=1)
END_FIELDS = ("rho", "U", "p", "T")

PHYSICS_CRITICAL = (
    "log.rhoCentralFoam `End` line and `Time =` count (fixed-deltaT identity)",
    "RC.txt (solver rc, written by the launcher in the shell that ran the solver)",
    "<endTime>/rho, U, p, T present and NEWER than 0/U (age guard)",
    "0/C cell centres",
    "every time step's `max Courant Number` in log.rhoCentralFoam (rule 5 limb 1 stability census)",
)
INFRASTRUCTURE = (
    "ClockTime in log.rhoCentralFoam (cost actual)",
    "box_before.txt / box_after.txt",
    "MESH_LINE.txt",
    "STATUS.* / launcher.queue.out / LAUNCH_LOG rows written by a queue runner",
    "calibration figures derived from any of the above",
)

WRITE_PATH_NOTE = (
    "OpenFOAM ascii volScalarField `rho` (`internalField nonuniform List<scalar>` NEWLINE N NEWLINE `(` "
    "one value per line `)`) and volVectorField `U` (one `(ux uy uz)` per line) at endTime; pinned against "
    "REAL rhoCentralFoam output on this box, verification/runs/F15_runs/coarse/4/{rho,U}, parsed at selftest.")
REAL_RHO_ON_BOX = os.path.join(REPO, "verification", "runs", "F15_runs", "coarse", "4", "rho")
REAL_U_ON_BOX = os.path.join(REPO, "verification", "runs", "F15_runs", "coarse", "4", "U")
REAL_RHO_CELLS = 10000


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


def read_rho(path):
    if not os.path.isfile(path):
        refuse("no rho field at %s" % path)
    try:
        F = FIO.read_field(path)
    except FIO.FieldFormatError as e:
        refuse("%s: %s" % (path, e))
    if F["kind"] != "scalar" or F["internal"] is None:
        refuse("%s is not a nonuniform volScalarField. %s" % (path, WRITE_PATH_NOTE))
    if F["internal"].shape[0] < 64:
        refuse("%s has only %d cells" % (path, F["internal"].shape[0]))
    return F["internal"]


def read_U(path):
    if not os.path.isfile(path):
        refuse("no U field at %s" % path)
    try:
        F = FIO.read_field(path)
    except FIO.FieldFormatError as e:
        refuse("%s: %s" % (path, e))
    if F["kind"] != "vector" or F["internal"] is None:
        refuse("%s is not a nonuniform volVectorField. %s" % (path, WRITE_PATH_NOTE))
    return F["internal"]


def e2_from_files(rho_path, xc, yc):
    """G-F20-1: E2(T) = sqrt(mean over cells (rho_h - rho_exact(x_c, T))^2)."""
    rho = read_rho(rho_path)
    if rho.shape[0] != len(xc):
        refuse("%s carries %d cells but 0/C carries %d" % (rho_path, rho.shape[0], len(xc)))
    return float(math.sqrt(np.mean((rho - EX.rho_exact(xc, yc, END_TIME)) ** 2)))


def ke_from_files(rho_path, u_path):
    """G-F20-2: mean over cells of rho |U|^2 / 2 (uniform cells: the box-mean KE)."""
    rho = read_rho(rho_path)
    U = read_U(u_path)
    if U.shape[0] != rho.shape[0]:
        refuse("%s carries %d cells but %s carries %d" % (u_path, U.shape[0], rho_path, rho.shape[0]))
    return float(np.mean(0.5 * rho * (U[:, 0] ** 2 + U[:, 1] ** 2)))


# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (rule 3)
# ---------------------------------------------------------------------------
def _plant(rho_path, level, name, predicted_fn, read_fn):
    d = RT.PLANT
    rho = read_rho(rho_path)
    before = read_fn(rho_path)
    predicted = predicted_fn(rho + d)
    tmp = tempfile.mkdtemp(prefix="f20_plant_")
    try:
        work = os.path.join(tmp, "rho")
        if FIO.plant_into_scalar_file(rho_path, work, d) == 0:
            refuse("nothing to plant into %s" % rho_path)
        after = read_fn(work)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if after == before:
        refuse("PLANTED-ZERO CONTROL FAILED for %s on %s: the plant did not move the reading" % (name, rho_path))
    if abs(after - predicted) > 1e-13:
        refuse("PLANTED-ZERO CONTROL FAILED for %s on %s: predicted %.17g, reader returned %.17g"
               % (name, rho_path, predicted, after))
    return RT.external_plant_control(name, before, after, plant=(predicted - before),
                                     artifact=rho_path, level=level)


def plant_control_e2(rho_path, xc, yc, level):
    ex = EX.rho_exact(xc, yc, END_TIME)
    return _plant(rho_path, level, "e2_from_files",
                  lambda r: float(math.sqrt(np.mean((r - ex) ** 2))),
                  lambda p: e2_from_files(p, xc, yc))


def plant_control_ke(rho_path, u_path, level):
    U = read_U(u_path)
    return _plant(rho_path, level, "ke_from_files",
                  lambda r: float(np.mean(0.5 * r * (U[:, 0] ** 2 + U[:, 1] ** 2))),
                  lambda p: ke_from_files(p, u_path))


# ---------------------------------------------------------------------------
# RULE 5 LIMB (1) -- explicit solver: a STABILITY CENSUS, named as such
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
                  n_above_ceiling=len(bad), n_non_finite=n_nan, worst=max(v for v in vals if math.isfinite(v)) if n_nan < len(vals) else None,
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
    for f in END_FIELDS:
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
                why="rc 0; End; latest + dt > endTime; %d `Time` lines == endTime/dt; %s at endTime newer than 0/U"
                    % (len(times), ", ".join(END_FIELDS)))


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
        for probe in ("box_before.txt", "box_after.txt", "MESH_LINE.txt"):
            if not os.path.isfile(os.path.join(cd, probe)):
                defects.append("BOOKKEEPING DEFECT: level %s lacks %s; NOT MEASURED" % (name, probe))
    return dict(fields="INFRASTRUCTURE", core_min_claim=None if defects else spent, partial_sum_core_min=spent,
                cap_core_min=CAP_CORE_MIN, defects=defects,
                note="ClockTime x ranks / 60; dollars at $0.0513/core-h DERIVED, NOT MEASURED")


def control_field_classes_separate():
    tmp = tempfile.mkdtemp(prefix="f20_l342_")
    try:
        cd = os.path.join(tmp, "coarse")
        os.makedirs(os.path.join(cd, "0")); os.makedirs(os.path.join(cd, "10"))
        open(os.path.join(cd, "0", "U"), "w").write("x")
        import time as _t
        _t.sleep(0.02)
        n = STEPS["coarse"]; dt = DT["coarse"]
        body = "".join("Mean and max Courant Numbers = 0.05 0.09\nTime = %.10g\n" % ((i + 1) * dt) for i in range(n)) \
            + "ClockTime = 3 s\nEnd\n"
        open(os.path.join(cd, "log.rhoCentralFoam"), "w").write(body)
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        for f in END_FIELDS:
            open(os.path.join(cd, "10", f), "w").write("y")
        log = os.path.join(cd, "log.rhoCentralFoam")
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
        open(log, "w").write(body.replace("0.05 0.09\n", "0.05 0.31\n", 1))
        st, _ = iterative_state(log, "coarse")
        if st == "CONVERGED":
            refuse("L-342 CONTROL: one step above the Courant ceiling was still read as CONVERGED")
        open(log, "w").write(body.replace("0.05 0.09\n", "nan nan\n", 1))
        st, _ = iterative_state(log, "coarse")
        if st == "CONVERGED":
            refuse("L-342 CONTROL: a nan Courant line was still read as CONVERGED")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(control="PZ-F20-L342_infrastructure_vs_physics_fields_driven_both_ways",
                infrastructure_deleted="verdict channel unchanged, cost claim refused, defect lines printed",
                physics_corrupted="NOT A RESULT; Courant ceiling and nan both flip limb 1", passed=True)


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
    return dict(control="PZ-F20-GRADE_LADDER_CALLSITE_ast_census_plus_grep_both_ways", ast_call_nodes=calls, passed=True)


def control_solver_dicts_match():
    tp = open(os.path.join(HERE, "case", "constant", "thermophysicalProperties")).read()
    m = re.search(r"molWeight\s+([0-9eE+\-.]+)\s*;", tp)
    if not m or abs(float(m.group(1)) - EX.MOL_WEIGHT) > 1e-9:
        refuse("thermophysicalProperties molWeight does not equal exact_f20.MOL_WEIGHT (R = 1)")
    m = re.search(r"\bCp\s+([0-9eE+\-.]+)\s*;", tp)
    if not m or abs(float(m.group(1)) - EX.CP) > 1e-15:
        refuse("thermophysicalProperties Cp does not equal exact_f20.CP (gamma = 1.4)")
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
            refuse("fvSchemes does not register %s (the model integrates exactly that)" % what)
    cd = open(os.path.join(HERE, "case", "system", "controlDict.template")).read()
    me = re.search(r"^\s*endTime\s+([0-9.]+)\s*;", cd, re.M)
    if not me or abs(float(me.group(1)) - END_TIME) > 1e-12:
        refuse("controlDict.template endTime is not the registered %g" % END_TIME)
    if not re.search(r"adjustTimeStep\s+no\s*;", cd):
        refuse("controlDict.template must fix dt (adjustTimeStep no)")
    return dict(control="solver_dictionaries_agree_with_registration", molWeight=EX.MOL_WEIGHT, Cp=EX.CP,
                endTime=END_TIME, flux="Kurganov", limiters="vanLeer/vanLeerV/vanLeer", ddt="Euler", passed=True)


def control_reader_parses_real_solver_output():
    if not os.path.isfile(REAL_RHO_ON_BOX):
        refuse("the real solver output the format is pinned against is absent: %s" % REAL_RHO_ON_BOX)
    F = FIO.read_field(REAL_RHO_ON_BOX)
    if F["kind"] != "scalar" or F["internal"] is None or F["internal"].shape != (REAL_RHO_CELLS,):
        refuse("reader did not return %d scalars from %s" % (REAL_RHO_CELLS, REAL_RHO_ON_BOX))
    if not np.all(np.isfinite(F["internal"])) or np.min(F["internal"]) <= 0:
        refuse("real rho artifact holds non-finite or non-positive values")
    if not os.path.isfile(REAL_U_ON_BOX):
        refuse("the real solver U output the format is pinned against is absent: %s" % REAL_U_ON_BOX)
    G = FIO.read_field(REAL_U_ON_BOX)
    if G["kind"] != "vector" or G["internal"] is None or G["internal"].shape != (REAL_RHO_CELLS, 3):
        refuse("reader did not return %d vectors from %s" % (REAL_RHO_CELLS, REAL_U_ON_BOX))
    return dict(control="reader_parses_real_solver_written_rho_and_U_on_this_box",
                artifacts=[REAL_RHO_ON_BOX, REAL_U_ON_BOX], cells=REAL_RHO_CELLS, passed=True)


# ---------------------------------------------------------------------------
# BANDS
# ---------------------------------------------------------------------------
def bands():
    tab = dict((r["name"], r) for r in EX.predictions())
    fine = tab["fine"]
    e2p = fine["E2_pred"]
    ke = EX.ke_exact()
    tol = BAND_FACTOR * fine["ke_tol_basis"]
    d = EX.decomposition()
    return {
        "G-F20-1_E2_density_L2_at_T": dict(
            band=(e2p / BAND_FACTOR, e2p * BAND_FACTOR), reference=0.0, dim=DIM,
            principle=("discretisation-model prediction E2(T) = %.9e at h_fine = %g, dt = %g (numpy re-implementation "
                       "of rhoCentralFoam's Kurganov/vanLeer/Euler scheme integrated at 128^2, extrapolated with the "
                       "model's own order %.4f), times [1/%g, %g]" % (e2p, fine["h"], fine["dt"], d["p_e2"], BAND_FACTOR, BAND_FACTOR))),
        "G-F20-2_mean_kinetic_energy_at_T": dict(
            band=(ke - tol, ke + tol), reference=ke, dim=DIM,
            principle=("exact box-mean kinetic energy %.12f +/- %g x (|S(h_fine)| + |B dt_fine|) = +/- %.6e, where the model "
                       "decomposes the KE error into a dissipative spatial part S (order %.4f, %.4e at fine) and an "
                       "anti-dissipative Euler part B dt (B = %.4f, %.4e at fine); their signed sum %+.4e is the value "
                       "prediction and the band is the SUM OF MAGNITUDES so it does not rely on the cancellation"
                       % (ke, BAND_FACTOR, tol, d["p_S"], fine["ke_spatial_pred"], d["B"], fine["ke_euler_pred"], fine["ke_err_pred"]))),
    }


# ---------------------------------------------------------------------------
# DEMONSTRATION -- both gates able to take a failing AND a passing value
# ---------------------------------------------------------------------------
def synth_pair(tmp, rho, U, tag):
    rp = os.path.join(tmp, "rho_%s" % tag)
    up = os.path.join(tmp, "U_%s" % tag)
    open(rp, "w").write("FoamFile { version 2.0; format ascii; class volScalarField; object rho; }\n"
                        "dimensions [1 -3 0 0 0 0 0];\ninternalField nonuniform List<scalar> \n%s;\n"
                        "boundaryField { left { type cyclic; } }\n" % FIO.fmt_list(rho, "scalar"))
    open(up, "w").write("FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
                        "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
                        "boundaryField { left { type cyclic; } }\n" % FIO.fmt_list(U, "vector"))
    return rp, up


def demonstrate(bnd):
    """ZERO COMPUTE.  The model's 128^2 error fields, scaled by the model's
    128->512 E2 ratio, stand in for the fine field (inside both bands); the same
    scaled 40x is outside G-F20-1; a 0.1 % velocity inflation is outside G-F20-2."""
    m = EX.model(128, 4000)
    n = m["n"]
    xc, yc = m["xc"], m["yc"]
    rho_ex, u_ex, v_ex, _p, _T = EX.fields_exact(xc, yc, END_TIME)
    ratio = dict((r["name"], r) for r in EX.predictions())["fine"]["E2_pred"] / m["E2_pred"]
    d_rho = (m["rho"].ravel() - rho_ex) * ratio
    d_u = (m["u"].ravel() - u_ex) * ratio
    d_v = (m["v"].ravel() - v_ex) * ratio
    rows = []
    tmp = tempfile.mkdtemp(prefix="f20_demo_")
    try:
        cases = ((1.0, 1.0, "inside", "inside"), (40.0, 1.0, "outside", None), (1.0, 1.001, None, "outside"))
        for k, (scale, uinf, want1, want2) in enumerate(cases):
            rho = rho_ex + scale * d_rho
            U = np.column_stack([(u_ex + scale * d_u) * uinf, (v_ex + scale * d_v) * uinf, np.zeros(n * n)])
            rp, up = synth_pair(tmp, rho, U, "c%d" % k)
            cons = "exact(T) + %g x scaled model error field, U x %g" % (scale, uinf)
            if want1:
                v1 = e2_from_files(rp, xc, yc)
                lo, hi = bnd["G-F20-1_E2_density_L2_at_T"]["band"]
                rows.append(dict(gate="G-F20-1_E2_density_L2_at_T", construction=cons, value=v1, band=[lo, hi],
                                 inside=bool(lo <= v1 <= hi), intended=want1))
            if want2:
                v2 = ke_from_files(rp, up)
                lo, hi = bnd["G-F20-2_mean_kinetic_energy_at_T"]["band"]
                rows.append(dict(gate="G-F20-2_mean_kinetic_energy_at_T", construction=cons, value=v2, band=[lo, hi],
                                 inside=bool(lo <= v2 <= hi), intended=want2))
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
GATES = ("G-F20-1_E2_density_L2_at_T", "G-F20-2_mean_kinetic_energy_at_T")


def grade_one(root, gate, bnd):
    levels, detail = [], []
    for name in LEVEL_NAMES:
        case_dir = os.path.join(root, name)
        if not os.path.isdir(case_dir):
            return dict(gate=gate, verdict="PENDING", note="level %r absent from %s" % (name, root))
        log = os.path.join(case_dir, "log.rhoCentralFoam")
        comp = completion(case_dir, log, name)
        if not comp["done"]:
            verdict = "NOT A RESULT" if comp.get("crashed") else "PENDING"
            return dict(gate=gate, verdict=verdict, note="level %r: %s" % (name, comp["why"]), completion=comp)
        xc, yc = read_centres(case_dir)
        if len(xc) != CELLS[name]:
            refuse("level %s carries %d cells, registered %d" % (name, len(xc), CELLS[name]))
        rp = os.path.join(comp["end_dir"], "rho")
        up = os.path.join(comp["end_dir"], "U")
        val = e2_from_files(rp, xc, yc) if gate == GATES[0] else ke_from_files(rp, up)
        it_state, it_detail = iterative_state(log, name)
        levels.append(dict(name=name, cells=CELLS[name], value=val))
        detail.append(dict(name=name, cells=CELLS[name], value=val, artifact=rp, artifact_U=up,
                           h=EX.h_of(int(round(math.sqrt(CELLS[name])))),
                           dt=DT[name], completion=comp, iterative=it_state, iterative_detail=it_detail,
                           plateau="ABSENT: value at a fixed instant of a transient; no plateau exists to test",
                           xc=xc, yc=yc))
    fd = detail[-1]
    pc = plant_control_e2(fd["artifact"], fd["xc"], fd["yc"], fd["name"]) if gate == GATES[0] \
        else plant_control_ke(fd["artifact"], fd["artifact_U"], fd["name"])
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
    row["iterative_note"] = ("explicit inviscid solver: no iterative residual exists; limb (1) is a per-step "
                             "solver-reported Courant census against ceiling %g, named as such" % CO_CEILING)
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
        return False, "expected 4 demonstration rows (2 gates x inside/outside), got %d" % len(demo)
    if not __debug__:
        return False, "running under -O"
    return True, ("%d controls green; both gate quantities shown able to take a passing AND a failing value "
                  "through the real reader on the pinned write format; 0 assert nodes across 4 files; exactly "
                  "one grade_ladder call node; __debug__ True" % len(controls))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs", "F20_ISENTROPIC_VORTEX_runs"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--prereg-commit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    census = ast_no_asserts([os.path.abspath(__file__), os.path.join(HERE, "exact_f20.py"),
                             os.path.join(HERE, "foam_io_f20.py"), os.path.join(HERE, "build_f20.py")])
    controls = [EX.control_symbolic_substitution(), EX.control_substitution_is_able_to_fail(),
                EX.control_field_returns_after_one_period(), EX.control_ladder_is_geometrically_similar(),
                EX.control_model_is_forced_and_ordered(),
                control_grade_ladder_is_called(), control_solver_dicts_match(),
                control_reader_parses_real_solver_output(), control_field_classes_separate()]
    bnd = bands()
    demo = demonstrate(bnd)

    if a.selftest:
        ok, why = selftest_predicate(controls, demo, census)
        print(json.dumps(dict(assert_census=census, controls=controls,
                              bands=dict((k, dict(band=v["band"], reference=v["reference"], principle=v["principle"]))
                                         for k, v in bnd.items()),
                              model_levels=EX.predictions(), model_orders=EX.model_orders(), decomposition=EX.decomposition(),
                              gate_demonstration=demo, write_path=WRITE_PATH_NOTE,
                              predicate=dict(ok=ok, why=why)), indent=2, default=str))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0

    if not a.prereg_commit:
        refuse("--prereg-commit is required for a real grade (rule 2)")
    rows = [grade_one(a.root, g, bnd) for g in GATES]
    cost = cost_claim(a.root)
    out = a.out or os.path.join(a.root, "F20_GRADED.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(dict(rung="F20-ISENTROPIC_VORTEX", prereg_commit=a.prereg_commit,
                       prereg="verification/campaign/F20_ISENTROPIC_VORTEX_PREREGISTRATION.md",
                       assert_census=census, controls=controls, gate_demonstration=demo, write_path=WRITE_PATH_NOTE,
                       cap_core_min=CAP_CORE_MIN,
                       field_classes=dict(PHYSICS_CRITICAL=PHYSICS_CRITICAL, INFRASTRUCTURE=INFRASTRUCTURE),
                       cost_claim=cost, rows=rows), f, indent=2, default=str)
    print("F20 -- 2-D ISENTROPIC VORTEX -- TALLY")
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
