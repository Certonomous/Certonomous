#!/usr/bin/env python3
"""M6I comparator — ONERA M6 by IMPORT.  Grades Gate A (mesh admission) and Gate G
(grid convergence) against verification/campaign/M6I_PREREGISTRATION.md.

    analyse_m6i.py selftest              # prove every reader can see a non-zero
    analyse_m6i.py gateA  --runs <dir>   # mesh admission, R0
    analyse_m6i.py gateG  --runs <dir>   # grid convergence on C_D, R1-R3

REFUSES (exit 2) RATHER THAN DEGRADING.  Every grading path runs `selftest()` first
and grades nothing if it fails: a comparator whose readers have not been shown able to
see a non-zero does not get to report a zero (CLAUDE.md rule 3).

THE SELFTEST IS SELF-CONTAINED.  It synthesises every fixture it needs in a temporary
directory, so it runs green BEFORE any solver has ever been launched.  It does not
depend on a control run existing on disk.

--------------------------------------------------------------------------------
THREE DEFECTS THIS FILE IS BUILT NOT TO HAVE, each already paid for by this lab:

1.  N-T8, the Richardson SIGN.  Four independent implementations here wrote
        f_ext = f_fine + e21/(r^p - 1)          # WRONG, reflects the limit through
                                                # f_fine onto the coarse side
    where the correct form is
        f_ext = f_fine - e21/(r^p - 1),  e21 = f_mid - f_fine.
    The wrong value has the right magnitude, the right units and a plausible position
    between the levels, and both `p` and `GCI` are sign-independent, so every
    neighbouring number stays right and a KEY-PRESENCE selftest cannot catch it.  The
    standing rule of 2026-08-24 requires a VALUE control: a synthetic power-law triple
    whose limit is known by construction, asserted to 1e-12 relative.  N-T8's free
    identity `frozen + corrected == 2*f_fine` is asserted on the REAL data too.

2.  MESH_STANDARD.md section 14 — checkMesh's verdict lines CANNOT DISCRIMINATE this
    lab's 70-degree gate.  Section 14.1: an admissible mesh at 51.2554 deg and an
    inadmissible one at 81.5834 deg both print `Non-orthogonality check OK.`
    Section 14.3: the closing lines run ANTI-CORRELATED with the gate.  And measured by
    this lane on the M6I demo L3: max 88.9306 deg, 484 severe faces, closing line
    `Mesh OK.`, with no failed check of any kind.  THE GATE IS READ OFF THE REPORTED
    MAXIMUM.  `selftest()` proves this reader ignores the verdict lines by feeding it a
    log that says `Mesh OK.` at 88.9306 deg and requiring REJECTION.

3.  L-430 — a family whose levels are not similar produces three clean meshes and a
    meaningless observed order.  The cheap 3-D check is that the total cell-count ratio
    must equal r**3.  It is a GATE here, not an advisory.
--------------------------------------------------------------------------------
"""

import argparse
import math
import os
import re
import shutil
import sys
import tempfile

# ---- registered constants.  Changing any of these changes a GATE and is not this
# ---- script's to do: they are transcribed from M6I_PREREGISTRATION.md.
R_LADDER      = 2.0        # section 3, exact by construction (one generator call + coarsener)
DIM           = 3
CELL_RATIO    = 8.0        # r**3, L-430's cheap check
CELL_RATIO_TOL= 1.0e-4     # section 4 Gate A: 8.0000 +/- 0.0001
NONORTHO_MAX  = 70.0       # MESH_STANDARD section 3.1 hard gate
SKEW_MAX      = 4.0        # MESH_STANDARD section 3.2
NEST_TOL      = 1.0e-12    # root chords, section 4 Gate A
RESID_MAX     = 1.0e-8     # section 4 Gate G2
P_BAND        = (1.5, 2.5) # section 4 Gate G3 -- section 0 step 3
FS            = 1.25       # GCI factor of safety, rule 5
ITER_RATIO    = 10.0       # section 0 step 2: the 10x rule
STATION_ITERS = 2000       # section 4 Gate G2
FIELDS        = ("U", "p", "T", "rho", "nut", "k", "omega")   # section 6, rule 4
AGE_GUARD_REF = "0/U"      # section 6: touched last at launch

PLANT_NONORTHO = 12.3456   # deg, planted into a checkMesh log
PLANT_CD       = 1.234e-03 # planted into a force-coefficient file
PLANT_NEST     = 1.0e-9    # root chords, planted into a points file
PLANT_YPLUS    = 3.0       # multiplicative, planted into a yPlus field


def die(msg):
    print("REFUSED: %s" % msg)
    sys.exit(2)


# ===========================================================================
# READERS.  Each one is proved able to see a non-zero in selftest() before use.
# ===========================================================================

def read_checkmesh(path):
    """Return a dict from a checkMesh log, or {'state': 'ABSENT'}.

    AN ABSENT LOG READS 'ABSENT'.  IT NEVER READS CLEAN.  (M6I_PREREGISTRATION
    section 4, Gate A.)  This function returns ABSENT rather than raising, and the
    caller REFUSES to grade the level -- it does not skip it and does not pass it.

    THE VERDICT LINES ARE DELIBERATELY NOT PARSED.  MESH_STANDARD section 14: they
    cannot discriminate this gate.  Only the reported maxima are read.
    """
    if not os.path.exists(path):
        return {"state": "ABSENT", "path": path}
    txt = open(path, errors="replace").read()
    out = {"state": "READ", "path": path}

    m = re.search(r"non-orthogonality Max:\s*([0-9.eE+-]+)", txt)
    out["nonortho_max"] = float(m.group(1)) if m else None
    m = re.search(r"Max skewness\s*=\s*([0-9.eE+-]+)", txt)
    out["skew_max"] = float(m.group(1)) if m else None
    m = re.search(r"severely non-orthogonal \(>\s*70 degrees\) faces:\s*(\d+)", txt)
    out["severe"] = int(m.group(1)) if m else 0
    m = re.search(r"^\s*cells:\s*(\d+)", txt, re.M)
    out["cells"] = int(m.group(1)) if m else None
    m = re.search(r"^\s*internal faces:\s*(\d+)", txt, re.M)
    out["internal_faces"] = int(m.group(1)) if m else None

    # Missing maxima are a REFUSAL, never a pass: a log we cannot read the gate
    # quantity out of is not a log that clears the gate.
    if out["nonortho_max"] is None or out["skew_max"] is None or out["cells"] is None:
        out["state"] = "UNREADABLE"
    return out


def read_points_bounds(path):
    """Read an OpenFOAM ASCII points file -> list of (x,y,z).  Used for node nesting."""
    txt = open(path, errors="replace").read()
    return [tuple(float(v) for v in m.group(1).split())
            for m in re.finditer(r"\(([-0-9.eE+ ]+)\)", txt)]


def read_coefficient(path, column):
    """Read an OpenFOAM coefficient.dat -> {iteration: value} for the named column."""
    hdr, out = None, {}
    for line in open(path, errors="replace"):
        s = line.strip()
        if s.startswith("#"):
            if "Cd" in s or "Cl" in s:
                hdr = s.lstrip("#").split()
            continue
        if not s:
            continue
        parts = s.split()
        if hdr is None or column not in hdr:
            continue
        j = hdr.index(column)
        if j < len(parts):
            out[int(float(parts[0]))] = float(parts[j])
    return out


def read_first_residual(path, field):
    """Initial residual of the FIRST solve of <field> in the LAST time step.

    THE FIRST SOLVE, NOT THE LAST, AND THE DIFFERENCE IS NOT COSMETIC.

    With `nNonOrthogonalCorrectors >= 1` a field -- in practice `p` -- is solved MORE
    THAN ONCE PER OUTER ITERATION.  OpenFOAM's own convergence control tests the FIRST
    of those solves.  Verified in the installed source, not from memory:

      solutionControl.C:231-232   residuals.first() = cmptMax(sp.first().initialResidual());
                                  residuals.last()  = cmptMax(sp.last().initialResidual());
      simpleControl.C:71          const bool absCheck =
                                      (residuals.first() < residualControl_[fieldi].absTol);

    `sp` is the solver-performance pair for that field in that time step, so `.first()`
    is the first solve.  A reader that keeps the LAST match returns the final corrector
    pass -- the SMALLEST residual of the set -- which understates the residual and
    admits levels that should fail G2.  IT ERRS IN THE FLATTERING DIRECTION.

    This is L-419's shape (a partial sample reported as the whole), and this team has
    already published a wrong p-residual column through `grep ... | tail -1` on a case
    with `nNonOrthogonalCorrectors 1`.  That setting is live in this repository right
    now, in `cases/JF1_JET_FLAP/case/system/fvSolution` and in 15+ mega-batch cases.
    It matters most here of all: non-orthogonal correctors are exactly what one reaches
    for on a highly non-orthogonal mesh, and this campaign's meshes measure 86-89 deg.

    Returns (residual, solves_per_iteration) so the caller can SAY whether correctors
    were active rather than silently assuming they were not.
    """
    pat = re.compile(r"Solving for %s,\s*Initial residual = ([0-9.eE+-]+)" % re.escape(field))
    val, seen_this_step, n_this_step, n_last = None, False, 0, 0
    for line in open(path, errors="replace"):
        if line.startswith("Time = "):
            if n_this_step:
                n_last = n_this_step
            seen_this_step, n_this_step = False, 0
            continue
        m = pat.search(line)
        if m:
            n_this_step += 1
            if not seen_this_step:
                val = float(m.group(1))       # FIRST solve of this time step
                seen_this_step = True
    if n_this_step:
        n_last = n_this_step
    return val, n_last


def read_last_residual_DEFECTIVE(path, field):
    """The defective reader -- keeps the LAST match, i.e. the final corrector pass.

    RETAINED ONLY so the planted control can assert that the two readers differ on a
    multi-corrector log.  A control that cannot separate the right implementation from
    the wrong one is not a control.  NOTHING GRADES THROUGH THIS FUNCTION.
    """
    val = None
    pat = re.compile(r"Solving for %s,\s*Initial residual = ([0-9.eE+-]+)" % re.escape(field))
    for line in open(path, errors="replace"):
        m = pat.search(line)
        if m:
            val = float(m.group(1))
    return val


def read_yplus_max(path):
    """Max y+ from a yPlus function-object log."""
    val = None
    for line in open(path, errors="replace"):
        m = re.search(r"max(?:imum)?\s*[:=]?\s*([0-9.eE+-]+)", line)
        if m and "y+" in line.lower():
            val = float(m.group(1))
    return val


def completion(run_root, end_time):
    """CLAUDE.md rule 4, STRICT and ALL-OR-NOTHING.  Every clause or nothing."""
    r = {"ok": False, "clauses": {}}
    log = os.path.join(run_root, "log.solver")
    rcf = os.path.join(run_root, "rc")
    r["clauses"]["log_present"] = os.path.exists(log)
    if not r["clauses"]["log_present"]:
        return r
    txt = open(log, errors="replace").read()
    r["clauses"]["rc0"] = os.path.exists(rcf) and open(rcf).read().strip() == "0"
    r["clauses"]["end_line"] = bool(re.search(r"^End\b", txt, re.M))
    times = [float(m.group(1)) for m in re.finditer(r"^Time = ([0-9.eE+-]+)", txt, re.M)]
    r["clauses"]["last_time_is_endTime"] = bool(times) and abs(times[-1] - end_time) < 1e-9
    r["clauses"]["exec_count_is_endTime"] = len(re.findall(r"^ExecutionTime", txt, re.M)) == int(end_time)
    tdir = os.path.join(run_root, ("%g" % end_time))
    r["clauses"]["time_dir"] = os.path.isdir(tdir)
    present = [f for f in FIELDS if os.path.exists(os.path.join(tdir, f))]
    r["clauses"]["fields_present"] = (len(present) == len(FIELDS))
    r["missing_fields"] = [f for f in FIELDS if f not in present]
    # THE AGE GUARD.  0/U is touched last at launch, so it dates the run that was
    # allowed to produce this answer.  Every field at endTime must be NEWER.
    ref = os.path.join(run_root, AGE_GUARD_REF)
    if os.path.exists(ref) and r["clauses"]["fields_present"]:
        t0 = os.path.getmtime(ref)
        r["clauses"]["age_guard"] = all(
            os.path.getmtime(os.path.join(tdir, f)) > t0 for f in FIELDS)
    else:
        r["clauses"]["age_guard"] = False
    r["ok"] = all(r["clauses"].values())
    return r


# ===========================================================================
# ROACHE / RICHARDSON
# ===========================================================================

def richardson(f_fine, f_mid, r, p):
    """CORRECT form (N-T8):  f_ext = f_fine - e21/(r**p - 1),  e21 = f_mid - f_fine."""
    den = r ** p - 1.0
    if den == 0.0:
        return None
    return f_fine - (f_mid - f_fine) / den


def richardson_frozen_defect(f_fine, f_mid, r, p):
    """The N-T8 sign defect.  Kept ONLY so the identity control can assert it."""
    den = r ** p - 1.0
    if den == 0.0:
        return None
    return f_fine + (f_mid - f_fine) / den


def triple(f_coarse, f_mid, f_fine, r=R_LADDER):
    """Classify a triple and, only when CONVERGING, compute p, GCI and f_ext."""
    e32 = f_mid - f_coarse
    e21 = f_fine - f_mid
    out = {"f_coarse": f_coarse, "f_mid": f_mid, "f_fine": f_fine,
           "e32": e32, "e21": e21, "p": None, "gci_fine": None,
           "f_ext": None, "kind": None}
    if e21 == 0.0 and e32 == 0.0:
        out["kind"] = "EXACT"
        return out
    if e21 == 0.0 or e32 == 0.0:
        out["kind"] = "STAGNANT"
        return out
    ratio = e32 / e21
    out["ratio"] = ratio
    if ratio < 0:
        out["kind"] = "OSCILLATORY"
        return out
    if ratio <= 1.0:
        out["kind"] = "DIVERGENT"
        return out
    out["p"] = math.log(ratio) / math.log(r)
    out["kind"] = "CONVERGING"
    # GCI on the FINE level, Fs = 1.25 (rule 5)
    if f_fine != 0.0:
        out["gci_fine"] = FS * abs(e21 / f_fine) / (r ** out["p"] - 1.0)
    out["f_ext"] = richardson(f_fine, f_mid, r, out["p"])
    return out


# ===========================================================================
# SELFTEST -- every reader shown able to see a non-zero, on fixtures it builds
# ===========================================================================

CHECKMESH_TEMPLATE = """Mesh stats
    points:           %(points)d
    faces:            %(faces)d
    internal faces:   %(ifaces)d
    cells:            %(cells)d

Checking geometry...
    Max cell openness = 2.8e-14 OK.
    Max aspect ratio = 637.086 OK.
    Mesh non-orthogonality Max: %(nonortho)s average: 33.98
   *Number of severely non-orthogonal (> 70 degrees) faces: %(severe)d.
    Max skewness = %(skew)s OK.

%(verdict)s
"""


def _write_checkmesh(path, nonortho, skew, cells, severe=0, verdict="Mesh OK."):
    with open(path, "w") as f:
        f.write(CHECKMESH_TEMPLATE % {
            "points": cells + 4000, "faces": cells * 3, "ifaces": cells * 3 - 7000,
            "cells": cells, "nonortho": nonortho, "severe": severe,
            "skew": skew, "verdict": verdict})


def selftest():
    ok = True
    print("=== M6I comparator selftest ===")

    # -- 1. RICHARDSON VALUE CONTROL (N-T8 standing rule, 2026-08-24) -----------
    # A synthetic power law whose limit is known BY CONSTRUCTION.
    f_ex, A, p_true, r = 0.0175, 4.0e-4, 2.0, R_LADDER
    f1 = f_ex + A * (r ** p_true) ** 0      # fine
    f2 = f_ex + A * (r ** p_true) ** 1      # mid
    f3 = f_ex + A * (r ** p_true) ** 2      # coarse
    t = triple(f3, f2, f1)
    if t["kind"] != "CONVERGING":
        print("  FAIL richardson control: synthetic triple classified %s" % t["kind"])
        ok = False
    else:
        dp = abs(t["p"] - p_true)
        rel = abs(t["f_ext"] - f_ex) / abs(f_ex)
        print("  richardson VALUE control: p %.12f (true %.1f, |d| %.2e), f_ext %.15f "
              "(true %.15f, rel %.2e)" % (t["p"], p_true, dp, t["f_ext"], f_ex, rel))
        if dp > 1e-10 or rel > 1e-12:
            print("  FAIL: value control outside 1e-12 relative")
            ok = False
        # N-T8's FREE identity: frozen + corrected == 2*f_fine, exactly.
        lhs = richardson_frozen_defect(f1, f2, r, t["p"]) + t["f_ext"]
        if abs(lhs - 2.0 * f1) > 1e-12 * abs(f1):
            print("  FAIL identity: frozen+corrected %.15f != 2*f_fine %.15f" % (lhs, 2 * f1))
            ok = False
        else:
            print("  N-T8 identity control: frozen + corrected == 2*f_fine  HOLDS")
        # And the defective form must be measurably WRONG on this case, or the
        # control is not discriminating anything.
        if abs(richardson_frozen_defect(f1, f2, r, t["p"]) - f_ex) / abs(f_ex) < 1e-6:
            print("  FAIL: the N-T8 defect is indistinguishable here -- control is blind")
            ok = False
        else:
            print("  N-T8 defect control: the frozen form is measurably wrong  CONFIRMED")

    # -- 2. TRIPLE CLASSIFIER, all five kinds ---------------------------------
    cases = [((4.0, 2.0, 1.0), "CONVERGING"), ((1.0, 2.0, 4.0), "DIVERGENT"),
             ((1.0, 2.0, 1.0), "OSCILLATORY"), ((1.0, 1.0, 1.0), "EXACT"),
             ((1.0, 2.0, 2.0), "STAGNANT")]
    bad = [(v, k, triple(*v)["kind"]) for v, k in cases if triple(*v)["kind"] != k]
    if bad:
        print("  FAIL triple classifier: %s" % bad)
        ok = False
    else:
        print("  triple classifier: CONVERGING/DIVERGENT/OSCILLATORY/EXACT/STAGNANT all correct")

    d = tempfile.mkdtemp(prefix="m6i_selftest_")
    try:
        # -- 3. checkMesh READER, PLANTED ---------------------------------------
        p1 = os.path.join(d, "log.checkMesh")
        _write_checkmesh(p1, "51.2554", "1.443", 122880)
        base = read_checkmesh(p1)
        _write_checkmesh(p1, "%.4f" % (51.2554 + PLANT_NONORTHO), "1.443", 122880)
        pl = read_checkmesh(p1)
        delta = pl["nonortho_max"] - base["nonortho_max"]
        print("  checkMesh reader planted control: read-back delta %.6f (plant %.6f)"
              % (delta, PLANT_NONORTHO))
        if abs(delta - PLANT_NONORTHO) > 1e-6:
            print("  FAIL: the checkMesh reader cannot see the plant")
            ok = False

        # -- 4. THE SECTION 14 DISCRIMINATION CONTROL ---------------------------
        # A log whose VERDICT says the mesh is fine and whose MAXIMUM says it is
        # 18.93 deg over the gate.  This is the real M6I demo L3.  A reader keyed
        # on the verdict line PASSES it; this gate must REJECT it.
        p2 = os.path.join(d, "log.checkMesh.trap")
        _write_checkmesh(p2, "88.9306", "2.94156", 1920, severe=484, verdict="Mesh OK.")
        trap = read_checkmesh(p2)
        admitted = (trap["nonortho_max"] <= NONORTHO_MAX and trap["skew_max"] <= SKEW_MAX)
        print("  MESH_STANDARD section 14 discrimination control: log says 'Mesh OK.' at "
              "%.4f deg -> gate admits? %s" % (trap["nonortho_max"], admitted))
        if admitted:
            print("  FAIL: this gate is reading the verdict line, not the maximum")
            ok = False
        else:
            print("  section 14 control PASSED: rejected on the reported maximum, "
                  "verdict line ignored")

        # -- 5. ABSENT NEVER READS CLEAN ---------------------------------------
        miss = read_checkmesh(os.path.join(d, "does_not_exist"))
        print("  ABSENT control: missing log reads state=%s" % miss["state"])
        if miss["state"] != "ABSENT":
            print("  FAIL: a missing checkMesh log did not read ABSENT")
            ok = False
        # ...and an UNREADABLE log is a refusal too, not a pass.
        p3 = os.path.join(d, "log.checkMesh.trunc")
        open(p3, "w").write("Mesh stats\n    cells:  1920\n\nMesh OK.\n")
        if read_checkmesh(p3)["state"] != "UNREADABLE":
            print("  FAIL: a log with no reported maximum did not read UNREADABLE")
            ok = False
        else:
            print("  UNREADABLE control: a log missing the maximum refuses, does not pass")

        # -- 6. CELL-COUNT-RATIO GATE (L-430) -----------------------------------
        good = ratio_check([15360, 122880, 983040])
        bad_ = ratio_check([15360, 122880, 983041])       # ONE cell added
        gross = ratio_check([15360, 122880, 188006])      # L-430's own 1.531-vs-2.25 shape
        print("  L-430 cell-ratio control: exact family %s ; ONE cell added -> %s "
              "(exact clause %s, band clause %s) ; gross non-similarity -> %s"
              % (good["verdict"], bad_["verdict"], bad_["exact"], bad_["band"],
                 gross["verdict"]))
        if good["verdict"] != "PASS" or bad_["verdict"] == "PASS" or gross["verdict"] == "PASS":
            print("  FAIL: the cell-count-ratio gate cannot see a one-cell perturbation")
            ok = False
        else:
            print("     the ONE-cell case is caught by the EXACT clause ONLY -- the "
                  "registered\n     float band reads 8.0000081, which is 12.3x INSIDE its "
                  "own 1e-4 tolerance.\n     That is why AMENDMENT 1 added the exact clause "
                  "before any compute.")

        # -- 7. NODE-NESTING READER, PLANTED ------------------------------------
        fine = os.path.join(d, "points_fine")
        coarse = os.path.join(d, "points_coarse")
        pts = [(i * 0.5, i * 0.25, 0.0) for i in range(16)]
        _write_points(fine, pts)
        _write_points(coarse, pts[::2])
        n0 = nesting_max_dev(coarse, fine, 2)
        moved = list(pts)
        moved[4] = (moved[4][0] + PLANT_NEST, moved[4][1], moved[4][2])
        _write_points(fine, moved)
        n1 = nesting_max_dev(coarse, fine, 2)
        print("  node-nesting planted control: as-read %.3e -> planted %.12e (plant %.1e)"
              % (n0, n1, PLANT_NEST))
        if not (n0 == 0.0 and abs(n1 - PLANT_NEST) < 1e-15):
            print("  FAIL: the nesting reader cannot see a %.0e displacement" % PLANT_NEST)
            ok = False

        # -- 8. COEFFICIENT READER, PLANTED -------------------------------------
        cd = os.path.join(d, "coefficient.dat")
        _write_coeffs(cd, [(i, 0.0175 + 1e-6 * (3000 - i)) for i in range(1, 3001)])
        b = read_coefficient(cd, "Cd")
        _write_coeffs(cd, [(i, 0.0175 + 1e-6 * (3000 - i) + PLANT_CD) for i in range(1, 3001)])
        q = read_coefficient(cd, "Cd")
        dl = q[3000] - b[3000]
        print("  C_D reader planted control: read-back delta %.12e (plant %.12e)" % (dl, PLANT_CD))
        if abs(dl - PLANT_CD) > 1e-12:
            print("  FAIL: the C_D reader cannot see the plant")
            ok = False

        # -- 9. THE 10x RULE (section 0 step 2) ---------------------------------
        # inter-level difference 1.0e-3; iterative drift 1.0e-5 passes, 5.0e-4 fails.
        okp = ten_x_rule(1.0e-5, 1.0e-3)
        okf = ten_x_rule(5.0e-4, 1.0e-3)
        print("  10x-rule control: drift 1e-5 vs level gap 1e-3 -> %s ; drift 5e-4 -> %s"
              % (okp, okf))
        if not okp or okf:
            print("  FAIL: the 10x rule does not discriminate")
            ok = False

        # -- 10. RULE 4 COMPLETION, including the AGE GUARD ---------------------
        rr = os.path.join(d, "run")
        _make_run(rr, end_time=3, complete=True)
        c_ok = completion(rr, 3.0)
        _make_run(rr + "_stale", end_time=3, complete=True, stale=True)
        c_stale = completion(rr + "_stale", 3.0)
        _make_run(rr + "_nofield", end_time=3, complete=True, drop="omega")
        c_drop = completion(rr + "_nofield", 3.0)
        print("  rule-4 completion control: complete=%s ; stale-field(age guard)=%s ; "
              "missing omega=%s" % (c_ok["ok"], c_stale["ok"], c_drop["ok"]))
        if not c_ok["ok"] or c_stale["ok"] or c_drop["ok"]:
            print("  FAIL: the completion check is not all-or-nothing")
            ok = False
        if c_stale["clauses"]["age_guard"]:
            print("  FAIL: the AGE GUARD did not fire on a field older than 0/U")
            ok = False
        else:
            print("  AGE GUARD control: a field older than 0/U refuses  CONFIRMED")

        # -- 11. RESIDUAL READER: FIRST SOLVE, NOT LAST.  PLANTED. --------------
        # A two-corrector log: p is solved TWICE per iteration and the two initial
        # residuals differ by a known factor of 1000.  The reader must return the
        # FIRST.  OpenFOAM's own residualControl tests the first solve
        # (simpleControl.C:71 via solutionControl.C:231).
        rl = os.path.join(d, "log.twocorrector")
        FIRST_R, LAST_R = 4.0e-7, 4.0e-10
        with open(rl, "w") as f:
            for t in range(1, 6):
                f.write("Time = %d\n" % t)
                f.write("smoothSolver:  Solving for Ux, Initial residual = 1.1e-09, "
                        "Final residual = 1e-12, No Iterations 3\n")
                f.write("GAMG:  Solving for p, Initial residual = %.6e, "
                        "Final residual = 1e-9, No Iterations 5\n" % FIRST_R)
                f.write("GAMG:  Solving for p, Initial residual = %.6e, "
                        "Final residual = 1e-11, No Iterations 2\n" % LAST_R)
                f.write("ExecutionTime = %.2f s\n" % (t * 2.0))
        got, nsolves = read_first_residual(rl, "p")
        bad_got = read_last_residual_DEFECTIVE(rl, "p")
        print("  residual reader planted control: two-corrector log, p solved %d x per "
              "iteration" % nsolves)
        print("     first-solve residual  = %.6e   <- what residualControl tests" % got)
        print("     last-solve  residual  = %.6e   <- what a tail-1 reader returns "
              "(%.0fx smaller)" % (bad_got, FIRST_R / LAST_R))
        if abs(got - FIRST_R) > 1e-18 or nsolves != 2:
            print("  FAIL: the residual reader did not return the FIRST solve")
            ok = False
        elif abs(bad_got - LAST_R) > 1e-18:
            print("  FAIL: the defective reader is not reproducing the defect -- the "
                  "control is blind")
            ok = False
        elif got <= bad_got:
            print("  FAIL: the two readers do not differ -- the control discriminates nothing")
            ok = False
        else:
            print("     the two readers DIFFER by 1000x on this log, and the gate uses the "
                  "FIRST.\n     A tail-1 reader would have admitted a level at 4.0e-10 whose "
                  "tested\n     residual is 4.0e-07 -- it errs in the FLATTERING direction.")
        # And on a single-solve log the two must AGREE, or the fix has broken the
        # ordinary case.
        rl1 = os.path.join(d, "log.onecorrector")
        with open(rl1, "w") as f:
            for t in range(1, 4):
                f.write("Time = %d\n" % t)
                f.write("GAMG:  Solving for p, Initial residual = %.6e, "
                        "Final residual = 1e-12, No Iterations 4\n" % (1.0e-9 * t))
        g1, n1 = read_first_residual(rl1, "p")
        if n1 != 1 or abs(g1 - read_last_residual_DEFECTIVE(rl1, "p")) > 1e-20:
            print("  FAIL: on a single-solve log the corrected reader disagrees with the "
                  "obvious answer")
            ok = False
        else:
            print("     single-solve log: both readers agree (%.3e) -- the fix does not "
                  "change the ordinary case" % g1)

        # -- 12. y+ READER, PLANTED ---------------------------------------------
        yp = os.path.join(d, "log.yPlus")
        open(yp, "w").write("patch WING y+ : min = 0.11 max = 0.98 average = 0.44\n")
        y0 = read_yplus_max(yp)
        open(yp, "w").write("patch WING y+ : min = 0.11 max = %.6f average = 0.44\n"
                            % (0.98 * PLANT_YPLUS))
        y1 = read_yplus_max(yp)
        print("  y+ reader planted control: as-read %.4f -> planted %.4f (x%.1f)"
              % (y0, y1, PLANT_YPLUS))
        if abs(y1 / y0 - PLANT_YPLUS) > 1e-9:
            print("  FAIL: the y+ reader cannot see a scaled field")
            ok = False
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("=== selftest %s ===" % ("PASSED" if ok else "FAILED"))
    return ok


# ---- selftest fixture helpers ----------------------------------------------

def _write_points(path, pts):
    with open(path, "w") as f:
        f.write("FoamFile{version 2.0;format ascii;class vectorField;object points;}\n")
        f.write("%d\n(\n" % len(pts))
        for p in pts:
            f.write("(%.17g %.17g %.17g)\n" % p)
        f.write(")\n")


def _write_coeffs(path, rows):
    with open(path, "w") as f:
        f.write("# Force coefficients\n# Time Cd Cl\n")
        for i, v in rows:
            f.write("%d\t%.12e\t%.12e\n" % (i, v, 0.28))


def _make_run(root, end_time, complete=True, stale=False, drop=None):
    import time
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(os.path.join(root, "0"), exist_ok=True)
    tdir = os.path.join(root, "%g" % end_time)
    os.makedirs(tdir, exist_ok=True)
    lines = []
    for t in range(1, end_time + 1):
        lines.append("Time = %d\n" % t)
        lines.append("ExecutionTime = %.2f s  ClockTime = %d s\n" % (t * 3.1, t * 3))
    if complete:
        lines.append("End\n")
    open(os.path.join(root, "log.solver"), "w").writelines(lines)
    open(os.path.join(root, "rc"), "w").write("0\n")
    if stale:
        # fields written BEFORE 0/U -> the age guard must refuse
        for fl in FIELDS:
            open(os.path.join(tdir, fl), "w").write("x\n")
        time.sleep(0.02)
        open(os.path.join(root, AGE_GUARD_REF), "w").write("x\n")
    else:
        open(os.path.join(root, AGE_GUARD_REF), "w").write("x\n")
        time.sleep(0.02)
        for fl in FIELDS:
            if drop and fl == drop:
                continue
            open(os.path.join(tdir, fl), "w").write("x\n")


# ===========================================================================
# GATE HELPERS
# ===========================================================================

def ratio_check(cells_coarse_first):
    """L-430: for a 3-D family the total cell-count ratio must be r**3.

    TWO CLAUSES, BOTH CHECKED.  See M6I_PREREGISTRATION AMENDMENT 1 (pre-compute).

      (i)  EXACT INTEGER:  cells_fine == 8 * cells_mid, as integers.
      (ii) the registered float band 8.0000 +/- 0.0001, retained and still applied.

    Clause (i) exists because the registered float band CANNOT SEE A ONE-CELL
    PERTURBATION at this ladder's size: 983041/122880 = 8.0000081, which is 12.3x
    INSIDE the registered 1e-4 tolerance.  The selftest planted exactly that and the
    gate admitted it.  The coarsener removes every other node, so the ratio is exactly
    8 by construction and any departure -- of even one cell -- means a level was
    regenerated rather than coarsened.  Clause (i) STRICTLY NARROWS the gate; it can
    only turn a PASS into a GATE FAIL, never the reverse.
    """
    out = {"cells": list(cells_coarse_first), "ratios": [], "verdict": "PASS",
           "exact": True, "band": True}
    for a, b in zip(cells_coarse_first, cells_coarse_first[1:]):
        rr = float(b) / float(a)
        out["ratios"].append(rr)
        if int(b) != int(CELL_RATIO) * int(a):          # clause (i)
            out["exact"] = False
            out["verdict"] = "GATE FAIL"
        if abs(rr - CELL_RATIO) > CELL_RATIO_TOL:       # clause (ii)
            out["band"] = False
            out["verdict"] = "GATE FAIL"
    return out


def nesting_max_dev(coarse_points, fine_points, stride):
    """Max |coarse[i] - fine[stride*i]| in root chords.  Zero iff exactly nested."""
    c = read_points_bounds(coarse_points)
    f = read_points_bounds(fine_points)
    worst = 0.0
    for i, cp in enumerate(c):
        j = stride * i
        if j >= len(f):
            return float("inf")
        worst = max(worst, max(abs(cp[k] - f[j][k]) for k in range(3)))
    return worst


def ten_x_rule(iterative_drift, level_gap):
    """Section 0 step 2: the iterative change must be at least 10x smaller than the
    difference between consecutive mesh levels, else the observed order is NOISE."""
    if level_gap == 0.0:
        return False
    return abs(iterative_drift) * ITER_RATIO <= abs(level_gap)


# ===========================================================================
# GATE A -- mesh admission (R0)
# ===========================================================================

def gate_a(runs):
    print("\n=== GATE A -- mesh admission (M6I_PREREGISTRATION section 4) ===")
    levels = ["L3", "L2", "L1"]     # coarse first
    logs = {L: read_checkmesh(os.path.join(runs, L, "log.checkMesh")) for L in levels}

    refused = [L for L in levels if logs[L]["state"] != "READ"]
    for L in levels:
        s = logs[L]
        if s["state"] != "READ":
            print("  %-3s %s  <- %s" % (L, s["state"], s["path"]))
        else:
            print("  %-3s cells %-9d max non-ortho %8.4f deg   max skew %6.3f   "
                  "severe(>70) %d" % (L, s["cells"], s["nonortho_max"],
                                      s["skew_max"], s["severe"]))
    if refused:
        # An ABSENT or UNREADABLE log NEVER reads clean.  We refuse; we do not skip.
        die("checkMesh log %s for level(s) %s -- Gate A is not graded"
            % (logs[refused[0]]["state"], ", ".join(refused)))

    verdict, reasons = "PASS", []
    for L in levels:
        s = logs[L]
        if s["nonortho_max"] > NONORTHO_MAX:
            verdict = "GATE FAIL"
            reasons.append("%s max non-orthogonality %.4f deg > %.1f deg gate (over by %.4f)"
                           % (L, s["nonortho_max"], NONORTHO_MAX,
                              s["nonortho_max"] - NONORTHO_MAX))
        if s["skew_max"] > SKEW_MAX:
            verdict = "GATE FAIL"
            reasons.append("%s max skewness %.4f > %.1f" % (L, s["skew_max"], SKEW_MAX))

    rc = ratio_check([logs[L]["cells"] for L in levels])
    print("  cell counts (coarse first): %s" % ", ".join(str(c) for c in rc["cells"]))
    print("  cell-count ratios (L-430): %s"
          % ", ".join("%.8f" % x for x in rc["ratios"]))
    print("    clause (i)  EXACT integer r**3 = %d : %s" % (int(CELL_RATIO), rc["exact"]))
    print("    clause (ii) float band %.4f +/- %.4f : %s"
          % (CELL_RATIO, CELL_RATIO_TOL, rc["band"]))
    print("    -> %s   (AMENDMENT 1, pre-compute: clause (i) added because the float "
          "band alone\n       cannot see a one-cell perturbation at this ladder's size)"
          % rc["verdict"])
    if rc["verdict"] != "PASS":
        verdict = "GATE FAIL"
        reasons.append("cell-count ratio off r**3: ratios %s (exact=%s, band=%s)"
                       % (rc["ratios"], rc["exact"], rc["band"]))

    print("\n  NOTE, MESH_STANDARD section 14: this gate read the reported MAXIMUM on "
          "every level.\n  No checkMesh verdict line was parsed. Section 14.1/14.3 and the "
          "M6I demo L3\n  (88.9306 deg printing 'Mesh OK.') show those lines cannot "
          "discriminate this gate.")
    print("\n  GATE A: %s" % verdict)
    for r in reasons:
        print("    - %s" % r)
    if verdict != "PASS":
        print("\n  R0 = GATE FAIL.  The case is BLOCKED on mesh admission and NO SOLVER RUNS.")
    return verdict


# ===========================================================================
# GATE G -- grid convergence (R1-R3)
# ===========================================================================

def gate_g(runs, quantity="Cd", end_times=None):
    print("\n=== GATE G -- grid convergence on %s (section 0 steps 2-5) ===" % quantity)
    levels = ["L3", "L2", "L1"]
    end_times = end_times or {"L3": 2000, "L2": 3000, "L1": 4000}

    vals, drifts = {}, {}
    for L in levels:
        root = os.path.join(runs, L)
        comp = completion(root, float(end_times[L]))
        if not comp["ok"]:
            failed = [k for k, v in comp["clauses"].items() if not v]
            die("rule 4: %s incomplete -- failed clause(s) %s%s" %
                (L, ", ".join(failed),
                 (" ; missing fields %s" % comp["missing_fields"]) if comp.get("missing_fields") else ""))
        series = read_coefficient(os.path.join(root, "postProcessing", "forceCoeffs",
                                               "0", "coefficient.dat"), quantity)
        if not series:
            die("no %s series for %s -- a zero here would not be evidence" % (quantity, L))
        its = sorted(series)
        vals[L] = series[its[-1]]
        win = [series[i] for i in its if i > its[-1] - STATION_ITERS]
        drifts[L] = (max(win) - min(win)) if win else float("inf")
        # G2 reads the FIRST solve of each field in the last time step -- the value
        # OpenFOAM's own residualControl tests (simpleControl.C:71).  With
        # nNonOrthogonalCorrectors >= 1 the last solve is the final corrector pass and
        # is smaller; grading on it would err in the flattering direction.
        res = {}
        for f in ("Ux", "p", "k", "omega"):
            v, n = read_first_residual(os.path.join(root, "log.solver"), f)
            res[f] = (v or 0.0, n)
        rmax = max(v for v, _ in res.values())
        corr = {f: n for f, (_, n) in res.items() if n > 1}
        print("  %-3s %s = %.8f   drift over last %d its = %.3e   max first-solve "
              "residual = %.2e" % (L, quantity, vals[L], STATION_ITERS, drifts[L], rmax))
        print("      per-field first-solve residuals: %s"
              % ", ".join("%s %.2e" % (f, res[f][0]) for f in ("Ux", "p", "k", "omega")))
        if corr:
            print("      NON-ORTHOGONAL CORRECTORS ACTIVE: %s -- the gate uses the FIRST "
                  "solve of each iteration"
                  % ", ".join("%s solved %dx/iter" % (f, n) for f, n in corr.items()))
        if rmax > RESID_MAX:
            die("G2: %s first-solve residual %.2e exceeds the registered %.0e"
                % (L, rmax, RESID_MAX))

    gap = abs(vals["L1"] - vals["L2"])
    print("\n  G1, the 10x rule (section 0 step 2): |L1 - L2| = %.6e" % gap)
    noisy = [L for L in levels if not ten_x_rule(drifts[L], gap)]
    for L in levels:
        print("     %-3s drift %.3e  x10 = %.3e  vs level gap %.3e  -> %s"
              % (L, drifts[L], drifts[L] * ITER_RATIO, gap,
                 "OK" if L not in noisy else "NOT CONVERGED ENOUGH"))
    if noisy:
        # Rule 5 clause (1): a level not iteratively converged -> NOT A RESULT.
        print("\n  VERDICT: NOT A RESULT")
        print("    rule 5 clause (1): level(s) %s are not iteratively converged relative "
              "to the\n    inter-level difference.  The observed order would be NOISE, not "
              "discretisation." % ", ".join(noisy))
        return "NOT A RESULT"

    t = triple(vals["L3"], vals["L2"], vals["L1"])
    print("\n  triple: coarse %.8f  mid %.8f  fine %.8f   e32 %.6e  e21 %.6e"
          % (t["f_coarse"], t["f_mid"], t["f_fine"], t["e32"], t["e21"]))
    print("  classification: %s" % t["kind"])

    if t["kind"] != "CONVERGING":
        # Rule 5 clause (2): print the value and the triple beside the label.
        print("\n  VERDICT: NOT A RESULT   (rule 5 clause 2 -- triple is %s)" % t["kind"])
        print("    fine value %.8f is printed beside the label and is NOT a result."
              % t["f_fine"])
        print("    NO GCI IS QUOTED: the three values are not monotone." )
        return "NOT A RESULT"

    # SAY WHICH IS WHICH.  p is GATED, as a BAND CONDITION (G3): outside 1.5-2.5 is a
    # GATE FAIL.  C_D is the GRADED VALUE, and it is the FINE value that is graded,
    # never the Richardson extrapolate.  Both are true and they are different roles;
    # a reader told only that p is "reported" will not expect the GATE FAIL below.
    print("  observed order p = %.6f   (GATED as a band condition, G3: band %.1f-%.1f)"
          % (t["p"], P_BAND[0], P_BAND[1]))
    print("      role: p gates; %s is the graded VALUE; f_ext is reported and never graded"
          % quantity)
    print("  GCI_fine (Fs = %.2f) = %.6e  = %.4f %%" % (FS, t["gci_fine"], 100 * t["gci_fine"]))
    print("  Richardson extrapolate f_ext = %.10f   (CORRECT sign, N-T8)" % t["f_ext"])

    # N-T8's free identity, asserted on the REAL data.
    lhs = richardson_frozen_defect(t["f_fine"], t["f_mid"], R_LADDER, t["p"]) + t["f_ext"]
    if abs(lhs - 2.0 * t["f_fine"]) > 1e-10 * max(1.0, abs(t["f_fine"])):
        die("N-T8 identity failed on real data: %.15f != 2*f_fine %.15f"
            % (lhs, 2 * t["f_fine"]))
    print("  N-T8 identity on real data: frozen + corrected == 2*f_fine  HOLDS")

    if not (P_BAND[0] <= t["p"] <= P_BAND[1]):
        print("\n  VERDICT: GATE FAIL   (G3: p = %.4f outside %.1f-%.1f)"
              % (t["p"], P_BAND[0], P_BAND[1]))
        print("    SECTION 0 STEP 4 IS NOW OWED, AND IT IS AN OBLIGATION, NOT AN OPTION:")
        print("      (a) re-check G1/G2 on L1;")
        print("      (b) re-verify similarity -- cell ratios, coarsener nesting assertions, y+;")
        print("      (c) add L0 at 7,864,320 cells at the same r = 2 and recompute p on the")
        print("          finest three.  L0's cost and its separate cap are already registered.")
        return "GATE FAIL"

    print("\n  VERDICT: PASS   (p in band; the FINE value is graded, never the extrapolate)")
    print("  %s = %.8f  +/- %.4f %% (GCI_fine, Fs = %.2f)"
          % (quantity, t["f_fine"], 100 * t["gci_fine"], FS))
    return "PASS"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["selftest", "gateA", "gateG"])
    ap.add_argument("--runs", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--quantity", default="Cd")
    a = ap.parse_args()

    if a.mode == "selftest":
        sys.exit(0 if selftest() else 2)

    # EVERY grading path runs the selftest first and grades NOTHING if it fails.
    if not selftest():
        die("selftest failed -- no grading is performed")

    if a.mode == "gateA":
        v = gate_a(a.runs)
    else:
        v = gate_g(a.runs, a.quantity)
    sys.exit(0 if v == "PASS" else 1)


if __name__ == "__main__":
    main()
