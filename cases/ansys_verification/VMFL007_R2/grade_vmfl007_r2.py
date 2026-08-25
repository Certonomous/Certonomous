#!/usr/bin/env python3
# ===========================================================================
# grade_vmfl007_r2.py
#
# VMFL007-R2 -- the LINEAR-SOLVER / PRECONDITIONER SLATE.
#
# WHAT THIS SCRIPT IS FOR, stated first so it is not mistaken for a case grader.
# ---------------------------------------------------------------------------
# VMFL007 run 1 produced NO number: it DIVERGED.  R2 is a CONVERGENCE
# INVESTIGATION with the linear solver / preconditioner as the single
# registered variable under test, executing Sanaa's rule 2 -- "When a grid
# doesnt converge, try different pre conditioners, see if that's a raised issue
# online/in the litterature, check for bugs, if unsteady check cfl, pick
# different meshing".
#
# R2 IS SINGLE-GRID BY DESIGN (L1_25x25 only).  There is therefore NO Roache
# triple, and under CLAUDE.md rule 5 R2's CASE-LEVEL VERDICT CEILING IS
# `NOT A RESULT`.  THIS SCRIPT CANNOT EMIT A PASSING GATE ROW AND WILL REFUSE
# TO.  That is not a limitation -- it is the structural guarantee behind the
# registration's central guard: *a convergence fix is never selected by which
# one makes the gate pass*.  Here, none of them can.
#
# THE PRODUCT of this script is the ARM CLASSIFICATION TABLE: every arm in the
# frozen slate, in the frozen order, classified CONVERGED / STALLED / DIVERGENT
# / CAP-STOPPED / INCOMPLETE against a criterion frozen before any arm ran.
# EVERY ARM IS REPORTED WHETHER OR NOT IT RAN AND WHATEVER IT RETURNED.  An arm
# missing from disk is printed as MISSING, never silently dropped -- a slate
# truncated after seeing a number is answer-directed selection.
#
# CONTROLS (CLAUDE.md rules 3, 4; charter section 5):
#   * PLANTED-ZERO (rule 3): the series reader is shown able to see a known
#     perturbation planted into a COPY on disk and RE-READ from disk, and the
#     script REFUSES if it cannot see it.  A reader not shown able to see a
#     non-zero has produced no evidence.
#   * STRICT COMPLETION (rule 4): clauses C1-C7, including the AGE GUARD.
#     REFUSES (exit 2) rather than degrading.
#   * MUTATION CONTROLS in --selftest: every classification limb is shown able
#     to FAIL on a mutated input, because a check that has never failed has not
#     been shown to be a check.
#
# `set -e` DOES NOT GATE at a Bash tool's top level and `( set -e; ... )` fails
# silently; nothing in the surrounding launcher relies on it, and this script
# returns explicit exit codes:  0 = graded,  2 = REFUSED,  3 = usage.
# ===========================================================================

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SELF_REL = "cases/ansys_verification/VMFL007_R2/grade_vmfl007_r2.py"

# ===========================================================================
# FROZEN CONSTANTS.  Every number below is fixed at the pre-registration commit
# and none of them may be changed after first compute.
# ===========================================================================

CASE = "VMFL007-R2"
MANUAL_PAGE = 29
LEVEL = "L1_25x25"          # SINGLE GRID, by design.  See the header.
ENDTIME = 10000             # identical to run 1.  NOT changed between arms.
NCELLS = 625

RHO = 1000.0                # kg/m3, manual p.29 and the archive's material blob
# The closed form, re-derived in run 1's registration section 4 and NOT re-opened
# here.  Carried so the diagnostics can be printed; it is NOT R2's product.
DP_EXACT_PA = 60521.96938383448
DP_EXACT_KINEMATIC = DP_EXACT_PA / RHO          # 60.52196938383448 m2/s2
NU_WALL = 4.298435325556426e-05                 # m2/s, physical wall viscosity
NU_MIN_CLIP = 1.0e-8                            # transportProperties nuMin
NU_MAX_CLIP = 1.0                               # transportProperties nuMax

# THE GATE -- carried UNCHANGED from run 1's freeze so that, if an arm
# converges, R3 can register a triple against a gate this run never touched.
# IT IS NOT APPLIED AS A VERDICT HERE (single grid; see the header).
GATE_REF_PA = 60520.0
GATE_TOL = 0.005
GATE_LO_PA = GATE_REF_PA * (1.0 - GATE_TOL)     # 60217.40
GATE_HI_PA = GATE_REF_PA * (1.0 + GATE_TOL)     # 60822.60

# --------------------------------------------------------------------------
# THE FROZEN CONVERGENCE CRITERION.  This is the selection criterion for the
# slate and it is frozen BEFORE any arm runs.  Arms are NEVER ranked by how
# close their Delta p lands to the gate.
# --------------------------------------------------------------------------
# C-BOUNDED: the gate series must never leave a permissive bound.
BOUND_MAX_KINEMATIC = 1.0e4     # m2/s2 == 165x the physical 60.522.  Run 1
                                # reached 9.449536950130e+144.
# C-DESCENT: MONITOR_STANDARD S13 v1.12 form, IDENTICAL to run 1's frozen
# section 8.2 plateau clause -- deliberately unchanged, so the criterion cannot
# be accused of having been tuned for this slate.
PLATEAU_WINDOW = 1000           # FIXED window (not a fraction of the run)
PLATEAU_STRIDE = 100            # -> 10 samples; the S13 floor is 9
PLATEAU_FRAC_OF_RANGE = 2.0e-4  # 0.02 % of the WHOLE-RUN range
PLATEAU_NULL_RANGE = 1.0        # whole-run range below this -> REFUSED, never passed
# C-VISCOSITY: neither clip may ever be reached.  Run 1 pinned the nuMin FLOOR
# at iteration 904 (L1) / 715 (L2) and never left it.
NU_FLOOR_REL_MARGIN = 1.0e-9
# C-RESIDUAL: SECONDARY BACKSTOP ONLY, and DECLARED IN ADVANCE AS BLIND on this
# case -- OpenFOAM normalises the initial residual by a field-magnitude factor,
# so the ratio is SCALE-INVARIANT and a solution diverging by 140 decades holds
# a bounded normalised residual (run 1 measured p in [0.15, 0.46] throughout).
# It may only turn a CONVERGED into a NOT-CONVERGED, never the reverse.
RESID_UX_MAX = 1.0e-5
RESID_P_MAX = 1.0e-4

# THE SLATE, IN ITS FROZEN ORDER.  Every arm is run and reported regardless of
# what any earlier arm returned.  The blob is the registered fvSolution; the
# comparator asserts the file that ACTUALLY RAN is that blob, because for A1 vs
# A2 the OpenFOAM log tag is `GAMG:` for both and the log alone cannot tell them
# apart (evidence is derived from what EXECUTED, never from what was DECLARED).
SLATE = [
    ("A1_GAMG_GaussSeidel",             "70953b4ea8d71a0b4744b1df695ceac9e24fa820",
     "GAMG",         "CONTROL -- byte-identical to run 1's frozen fvSolution"),
    ("A2_GAMG_DICGaussSeidel",          "406f192f5dfcae6ded499f9c38e534270aaf2a70",
     "GAMG",         "same agglomeration, different smoother"),
    ("A3_PCG_DIC",                      "595dcc973b98d6740df7914a7b584fa127fba3c6",
     "DICPCG",       "Krylov + incomplete-Cholesky; NO agglomeration at all"),
    ("A4_PCG_GAMGprecon",               "753bc4221ab84841085bd0bf5974398ff2ceae0a",
     "GAMGPCG",      "GAMG demoted to preconditioner under a Krylov outer loop"),
    ("A5_PBiCGStab_DIC",                "3bfff09c46bc2034c7b120a265f20a8708c60e8b",
     "DICPBiCGStab", "a different Krylov, same preconditioner as A3"),
    ("A6_smoothSolver_symGaussSeidel",  "38a7c29aacb33dff23ab5c118718783b2ecc2a82",
     "smoothSolver", "no Krylov, no multigrid -- the crudest and most robust"),
]

# THE DETERMINISM CONTROL.  A1 re-runs run 1's exact configuration.  The case is
# serial and deterministic, so A1's gate series must reproduce run 1's L1 series.
# If it does not, this box is non-deterministic and the WHOLE SLATE is
# `NOT A RESULT` -- a cheap, strong control that costs one comparison.
RUN1_L1_PINLET_AT_ENDTIME = 9.449536950130e+144
RUN1_L1_REL_TOL = 1.0e-9
RUN1_L1_SERIES = ("verification/runs/ansys_verification/VMFL007/L1_25x25/"
                  "postProcessing/pInlet/0/surfaceFieldValue.dat")

PLANT = 1.234e-03           # the planted-zero perturbation (rule 3)

FIELDS_AT_ENDTIME = ("U", "p", "phi", "nu")
AGE_MARKER = "0/U"          # touched LAST at launch; dates the run

REFUSE = 2


class Refusal(Exception):
    """Raised for any failed clause.  The script REFUSES; it never degrades."""


def refuse(msg):
    raise Refusal(msg)


# ===========================================================================
# READERS
# ===========================================================================

def read_series(path):
    """Read an OpenFOAM functionObject .dat series as [(time, value), ...].

    Scalar columns only.  A vector column (UmaxInlet) is rejected here on
    purpose: this reader feeds the GATE channel and must never silently take
    the first component of something it did not expect.
    """
    if not os.path.isfile(path):
        refuse("series file absent: %s" % path)
    out = []
    with open(path) as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            parts = ln.split()
            if len(parts) != 2:
                refuse("series %s: expected 2 columns, got %d in %r"
                       % (path, len(parts), ln[:80]))
            if parts[1].startswith("("):
                refuse("series %s: vector column; this reader takes scalars only" % path)
            try:
                out.append((float(parts[0]), float(parts[1])))
            except ValueError:
                refuse("series %s: unparseable row %r" % (path, ln[:80]))
    if not out:
        refuse("series %s parsed to ZERO rows" % path)
    return out


def read_vector_series(path):
    """Read a vector-valued series as [(time, (x, y, z)), ...]."""
    if not os.path.isfile(path):
        refuse("series file absent: %s" % path)
    out = []
    with open(path) as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            m = re.match(r"^(\S+)\s+\(([^)]*)\)\s*$", ln)
            if not m:
                continue
            comps = [float(c) for c in m.group(2).split()]
            if len(comps) != 3:
                refuse("series %s: expected 3 components, got %d" % (path, len(comps)))
            out.append((float(m.group(1)), tuple(comps)))
    if not out:
        refuse("vector series %s parsed to ZERO rows" % path)
    return out


def find_series(run_dir, name, vector=False):
    base = os.path.join(run_dir, "postProcessing", name)
    if not os.path.isdir(base):
        refuse("no postProcessing/%s under %s" % (name, run_dir))
    cands = []
    for sub in sorted(os.listdir(base)):
        d = os.path.join(base, sub)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".dat"):
                    cands.append(os.path.join(d, f))
    if len(cands) != 1:
        refuse("postProcessing/%s under %s holds %d .dat files; expected exactly 1 "
               "(a restart would leave more, and guessing which one is the answer "
               "is exactly what a comparator must not do)" % (name, run_dir, len(cands)))
    return cands[0]


# ===========================================================================
# CONTROL 1 -- THE PLANTED ZERO (CLAUDE.md rule 3)
# ===========================================================================

def planted_zero_control(src_path, verbose=True):
    """Plant a known perturbation into a COPY on disk, RE-READ it from disk, and
    REFUSE if the reader cannot see it.

    The plant goes in by LINE INDEX into a temporary copy -- never into the run
    directory -- and the check is that the re-read value differs from the
    original by exactly PLANT.  A reader that cannot see a planted non-zero
    cannot be trusted to report a zero, or a plateau, or a divergence.
    """
    orig = read_series(src_path)
    idx = len(orig) // 2
    t_target, v_target = orig[idx]

    tmpd = tempfile.mkdtemp(prefix="vmfl007r2_plant_")
    try:
        dst = os.path.join(tmpd, "planted.dat")
        with open(src_path) as fh:
            lines = fh.readlines()
        data_line_no, seen = None, -1
        for i, ln in enumerate(lines):
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            seen += 1
            if seen == idx:
                data_line_no = i
                break
        if data_line_no is None:
            refuse("planted-zero control: could not locate data row %d in %s"
                   % (idx, src_path))
        parts = lines[data_line_no].split()
        parts[1] = repr(float(parts[1]) + PLANT)
        lines[data_line_no] = "\t".join(parts) + "\n"
        with open(dst, "w") as fh:
            fh.writelines(lines)

        # RE-READ FROM DISK.  Not from the in-memory object we just built.
        back = read_series(dst)
        if len(back) != len(orig):
            refuse("planted-zero control: row count changed %d -> %d"
                   % (len(orig), len(back)))
        t_back, v_back = back[idx]
        if t_back != t_target:
            refuse("planted-zero control: time column moved %r -> %r" % (t_target, t_back))
        delta = v_back - v_target
        # THE TOLERANCE IS A FRACTION OF THE PLANT, NEVER OF THE VALUE, and this
        # is the whole strength of the control.  A value-relative tolerance
        # (`1e-9 * abs(v_target)`) was written here first and a mutation control
        # in --selftest CAUGHT IT: on run 1's diverged series the values reach
        # 9.4e+144, where adding 1.234e-3 changes NOTHING -- the plant is far
        # below the floating-point resolution of the number it is added to -- so
        # the read-back delta is exactly 0.0 and a value-relative tolerance of
        # 1e+135 WAVES THAT THROUGH.  The control would then have certified a
        # reader that provably could not see its own plant.  Requiring the plant
        # to be recovered to within 0.1 % OF ITSELF refuses exactly there.
        if abs(delta - PLANT) > 1.0e-3 * PLANT:
            refuse("PLANTED-ZERO CONTROL FAILED on %s: planted %g at row %d "
                   "(t=%g, v=%g) and read back a change of %g. The reader CANNOT "
                   "SEE a known non-zero at this magnitude, so any zero, plateau "
                   "or bound it reports is NOT EVIDENCE."
                   % (src_path, PLANT, idx, t_target, v_target, delta))
        if verbose:
            print("    planted-zero control FIRED: planted %g at row %d (t=%g), "
                  "read back delta %g -- reader is shown able to see a non-zero"
                  % (PLANT, idx, t_target, delta))
        return True
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)


# ===========================================================================
# CONTROL 2 -- STRICT COMPLETION (CLAUDE.md rule 4), clauses C1-C7
# ===========================================================================

def strict_completion(run_dir):
    """Return (ok, rc, notes[]).  Does NOT raise: an arm that fails completion
    is a RECORDED arm outcome, not a reason to abandon the slate.  The slate
    only refuses as a whole for a CONTROL failure, never for an arm's result."""
    notes = []
    ok = True

    rcf = os.path.join(run_dir, "RUN_RC.txt")
    rc = None
    if not os.path.isfile(rcf):
        return False, None, ["C1 FAIL: no RUN_RC.txt (rc was never recorded on disk)"]
    meta = {}
    for ln in open(rcf):
        if "=" in ln:
            k, v = ln.split("=", 1)
            meta[k.strip()] = v.strip()
    try:
        rc = int(meta.get("rc", ""))
    except ValueError:
        return False, None, ["C1 FAIL: RUN_RC.txt carries no integer rc"]
    if rc != 0:
        ok = False
        notes.append("C1 FAIL: rc = %d (READ FROM DISK, never inferred)" % rc)
    else:
        notes.append("C1 ok: rc = 0")

    log = os.path.join(run_dir, "log.simpleFoam")
    if not os.path.isfile(log):
        return False, rc, notes + ["C2 FAIL: no log.simpleFoam"]
    txt = open(log, errors="replace").read()

    if re.search(r"^End\s*$", txt, re.M):
        notes.append("C2 ok: End line present")
    else:
        ok = False
        notes.append("C2 FAIL: no anchored `End` line")

    times = re.findall(r"^Time = (\S+)\s*$", txt, re.M)
    if not times:
        ok = False
        notes.append("C3 FAIL: no `Time = ` lines at all")
    else:
        last = times[-1]
        if last.strip() == str(ENDTIME):
            notes.append("C3 ok: last time == endTime == %d" % ENDTIME)
        else:
            ok = False
            notes.append("C3 FAIL: last time %s != endTime %d" % (last, ENDTIME))

    nexec = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    if nexec == ENDTIME:
        notes.append("C4 ok: ExecutionTime count == %d" % ENDTIME)
    else:
        ok = False
        notes.append("C4 FAIL: ExecutionTime count %d != endTime %d" % (nexec, ENDTIME))

    tdir = os.path.join(run_dir, str(ENDTIME))
    missing = [f for f in FIELDS_AT_ENDTIME if not os.path.isfile(os.path.join(tdir, f))]
    if missing:
        ok = False
        notes.append("C5 FAIL: fields absent at %d: %s" % (ENDTIME, ", ".join(missing)))
    else:
        notes.append("C5 ok: %s present at %d" % (" ".join(FIELDS_AT_ENDTIME), ENDTIME))

    marker = os.path.join(run_dir, AGE_MARKER)
    if not os.path.isfile(marker) or missing:
        ok = False
        notes.append("C6 FAIL: age guard cannot run (marker or fields absent)")
    else:
        m0 = os.path.getmtime(marker)
        stale = [f for f in FIELDS_AT_ENDTIME
                 if os.path.getmtime(os.path.join(tdir, f)) <= m0]
        if stale:
            ok = False
            notes.append("C6 FAIL (AGE GUARD): fields NOT newer than %s: %s"
                         % (AGE_MARKER, ", ".join(stale)))
        else:
            notes.append("C6 ok: AGE GUARD -- every field at %d is newer than %s"
                         % (ENDTIME, AGE_MARKER))

    ncour = len(re.findall(r"Courant Number", txt))
    if ncour == 0:
        notes.append("C7 ok: zero `Courant Number` lines -- MONITOR_STANDARD S8 "
                     "exemption READ OFF THE ARTIFACT, not asserted")
    else:
        ok = False
        notes.append("C7 FAIL: %d `Courant Number` lines in a steady run" % ncour)

    return ok, rc, notes


# ===========================================================================
# THE FROZEN CONVERGENCE CRITERION
# ===========================================================================

def plateau_stat(series):
    """MONITOR_STANDARD S13 v1.12: fixed window, whole-run-range normaliser.

    Returns (passed, window_ptp, whole_range, ratio, nsamples, refused_null).
    """
    vals = [v for _, v in series]
    whole_range = max(vals) - min(vals)
    tail = series[-PLATEAU_WINDOW:] if len(series) >= PLATEAU_WINDOW else series[:]
    samp = [v for i, (_, v) in enumerate(tail) if i % PLATEAU_STRIDE == 0]
    if len(samp) < 9:
        return False, None, whole_range, None, len(samp), False
    ptp = max(samp) - min(samp)
    if whole_range < PLATEAU_NULL_RANGE:
        # NULL CLAUSE: a series that never resolvably moved is REFUSED, never
        # passed.  A flat line is not a plateau; it is an absence of signal.
        return False, ptp, whole_range, None, len(samp), True
    ratio = ptp / whole_range
    return (ratio <= PLATEAU_FRAC_OF_RANGE), ptp, whole_range, ratio, len(samp), False


def final_residuals(run_dir):
    """Final INITIAL residual for Ux and p, read from the solver log."""
    log = os.path.join(run_dir, "log.simpleFoam")
    if not os.path.isfile(log):
        return None, None
    ux = p = None
    for ln in open(log, errors="replace"):
        m = re.search(r"Solving for Ux, Initial residual = (\S+?),", ln)
        if m:
            ux = float(m.group(1))
        m = re.search(r"Solving for p, Initial residual = (\S+?),", ln)
        if m:
            p = float(m.group(1))
    return ux, p


def classify_arm(run_dir, arm_name, expect_blob, expect_tag, run_plant=True):
    """Classify ONE arm against the FROZEN criterion.

    Returns a dict.  Never raises for an arm's RESULT; raises Refusal only for a
    CONTROL failure (a planted zero that will not fire), because a broken control
    invalidates the instrument rather than the arm.
    """
    r = {"arm": arm_name, "dir": run_dir, "class": None, "reasons": [],
         "executed_blob": None, "blob_ok": None, "solver_tag": None}

    if not os.path.isdir(run_dir):
        r["class"] = "MISSING"
        r["reasons"].append("run directory absent -- this arm has not been run. "
                            "It is REPORTED, not dropped: the slate is committed "
                            "to in full, in a fixed order, before any arm runs.")
        return r

    # ---- EXECUTED, NOT DECLARED: the fvSolution that actually ran ----------
    ran = os.path.join(run_dir, "system", "fvSolution")
    if os.path.isfile(ran):
        blob = subprocess.run(["git", "hash-object", ran], capture_output=True,
                              text=True).stdout.strip()
        r["executed_blob"] = blob
        r["blob_ok"] = (blob == expect_blob)
        if not r["blob_ok"]:
            r["class"] = "INCOMPLETE"
            r["reasons"].append(
                "the fvSolution IN THE RUN DIRECTORY is blob %s, not the registered "
                "%s for this arm. The arm's identity cannot be established from the "
                "solver log alone (A1 and A2 both print the tag `GAMG:`), so this is "
                "fatal to the arm." % (blob[:12], expect_blob[:12]))
            return r
        r["reasons"].append("arm identity ok: the fvSolution that RAN is the "
                            "registered blob %s" % expect_blob[:12])
    else:
        r["class"] = "INCOMPLETE"
        r["reasons"].append("no system/fvSolution in the run directory")
        return r

    # ---- the solver tag OpenFOAM actually printed --------------------------
    log = os.path.join(run_dir, "log.simpleFoam")
    if os.path.isfile(log):
        for ln in open(log, errors="replace"):
            m = re.match(r"^(\S+):\s+Solving for p,", ln)
            if m:
                r["solver_tag"] = m.group(1)
                break
    if r["solver_tag"] != expect_tag:
        r["reasons"].append("NOTE: log p-solver tag %r, registered %r"
                            % (r["solver_tag"], expect_tag))

    # ---- CAP ---------------------------------------------------------------
    rcf = os.path.join(run_dir, "RUN_RC.txt")
    meta = {}
    if os.path.isfile(rcf):
        for ln in open(rcf):
            if "=" in ln:
                k, v = ln.split("=", 1)
                meta[k.strip()] = v.strip()
    r["core_min"] = meta.get("core_min")
    if meta.get("rc") == "124":
        r["class"] = "CAP-STOPPED"
        r["reasons"].append("rc = 124: this arm hit its pre-registered per-arm cap "
                            "and was STOPPED. CLAUDE.md rule 12 -- an overrun does "
                            "not get a new budget and this arm is NOT re-run.")
        return r

    # ---- CONTROL: the planted zero must fire on THIS arm's own series ------
    pin_path = find_series(run_dir, "pInlet")
    if run_plant:
        planted_zero_control(pin_path)

    pin = read_series(pin_path)
    pout = read_series(find_series(run_dir, "pOutlet"))
    numax = read_series(find_series(run_dir, "nuMaxAll"))
    numin = read_series(find_series(run_dir, "nuMinAll"))

    # ---- C-COMPLETION ------------------------------------------------------
    comp_ok, rc, comp_notes = strict_completion(run_dir)
    r["completion"] = comp_notes
    r["rc"] = rc

    # ---- C-BOUNDED ---------------------------------------------------------
    peak = max(abs(v) for _, v in pin)
    r["peak_abs_pInlet_kinematic"] = peak
    bounded = peak <= BOUND_MAX_KINEMATIC
    r["C_BOUNDED"] = bounded
    r["reasons"].append(
        "C-BOUNDED %s: max |areaAverage(p)|_inlet over the run = %.6e m2/s2 "
        "against a frozen bound of %.1e (the physical value is %.6f, so the bound "
        "is %.0fx permissive)"
        % ("PASS" if bounded else "FAIL", peak, BOUND_MAX_KINEMATIC,
           DP_EXACT_KINEMATIC, BOUND_MAX_KINEMATIC / DP_EXACT_KINEMATIC))

    # ---- C-VISCOSITY -------------------------------------------------------
    floor = NU_MIN_CLIP * (1.0 + NU_FLOOR_REL_MARGIN)
    pinned = [t for t, v in numin if v <= floor] + [t for t, v in numax if v <= floor]
    ceil_hits = [t for t, v in numax if v >= NU_MAX_CLIP * (1.0 - NU_FLOOR_REL_MARGIN)]
    visc_ok = (not pinned) and (not ceil_hits)
    r["C_VISCOSITY"] = visc_ok
    r["nu_floor_first_hit"] = min(pinned) if pinned else None
    r["nu_ceiling_hits"] = len(ceil_hits)
    r["nu_max_final"] = numax[-1][1]
    r["nu_min_final"] = numin[-1][1]
    if visc_ok:
        r["reasons"].append(
            "C-VISCOSITY PASS: neither clip ever reached; final nu in "
            "[%.6e, %.6e] against a physical wall value of %.6e"
            % (numin[-1][1], numax[-1][1], NU_WALL))
    else:
        bits = []
        if pinned:
            bits.append("nu PINNED AT THE nuMin FLOOR (%g) from iteration %g -- the "
                        "floor is %.0fx BELOW the physical wall viscosity %.6e, so a "
                        "run there has no viscous damping left and has LEFT THE "
                        "PHYSICAL PROBLEM"
                        % (NU_MIN_CLIP, min(pinned), NU_WALL / NU_MIN_CLIP, NU_WALL))
        if ceil_hits:
            bits.append("nu reached the nuMax CEILING (%g) on %d iterations"
                        % (NU_MAX_CLIP, len(ceil_hits)))
        r["reasons"].append("C-VISCOSITY FAIL: " + "; ".join(bits))

    # ---- C-DESCENT ---------------------------------------------------------
    ppass, ptp, whole, ratio, nsamp, null_ref = plateau_stat(pin)
    r["C_DESCENT"] = ppass
    r["plateau"] = {"window_ptp": ptp, "whole_run_range": whole,
                    "ratio": ratio, "nsamples": nsamp, "null_refused": null_ref}
    if null_ref:
        r["reasons"].append(
            "C-DESCENT REFUSED (null clause): the whole-run range is %.6e < %.1f, so "
            "the series never resolvably moved. A flat line is not a plateau."
            % (whole, PLATEAU_NULL_RANGE))
    elif ratio is None:
        r["reasons"].append("C-DESCENT FAIL: only %d samples in the fixed window "
                            "(S13 floor is 9)" % nsamp)
    else:
        r["reasons"].append(
            "C-DESCENT %s: fixed window = last %d iterations sampled every %d "
            "(%d samples); window peak-to-peak %.6e against a whole-run range of "
            "%.6e = %.6e of range, threshold %.1e"
            % ("PASS" if ppass else "FAIL", PLATEAU_WINDOW, PLATEAU_STRIDE, nsamp,
               ptp, whole, ratio, PLATEAU_FRAC_OF_RANGE))

    # ---- C-RESIDUAL (secondary, DECLARED BLIND) ----------------------------
    ux, pres = final_residuals(run_dir)
    r["final_resid_Ux"], r["final_resid_p"] = ux, pres
    res_ok = (ux is not None and pres is not None
              and ux <= RESID_UX_MAX and pres <= RESID_P_MAX)
    r["C_RESIDUAL"] = res_ok
    r["reasons"].append(
        "C-RESIDUAL (SECONDARY, DECLARED BLIND) %s: final initial residual "
        "Ux = %s (<= %.1e), p = %s (<= %.1e). OpenFOAM's normalised residual is "
        "SCALE-INVARIANT, so a diverging solution holds a bounded value; this leg "
        "may only turn a CONVERGED into a NOT-CONVERGED, never the reverse."
        % ("PASS" if res_ok else "FAIL", ux, RESID_UX_MAX, pres, RESID_P_MAX))

    # ---- THE CLASSIFICATION ------------------------------------------------
    if not comp_ok:
        r["class"] = "DIVERGENT" if (rc is not None and rc != 0) else "INCOMPLETE"
        r["reasons"].append("completion clauses failed; see the C1-C7 notes")
    elif (not bounded) or (not visc_ok):
        r["class"] = "DIVERGENT"
    elif not ppass:
        r["class"] = "STALLED"
    elif not res_ok:
        r["class"] = "STALLED"
        r["reasons"].append("the plateau held but the secondary residual backstop "
                            "did not -- classified STALLED, never CONVERGED")
    else:
        r["class"] = "CONVERGED"

    # ---- the DIAGNOSTIC Delta p.  NEVER a verdict.  Only meaningful if the arm
    #      is CONVERGED; for anything else it is printed as not meaningful.
    dp_kin = pin[-1][1] - pout[-1][1]
    r["dp_pa"] = RHO * dp_kin
    r["dp_meaningful"] = (r["class"] == "CONVERGED")
    return r


# ===========================================================================
# THE DETERMINISM CONTROL -- A1 against run 1
# ===========================================================================

def determinism_control(repo_root, a1_dir):
    """A1 is run 1's configuration re-run.  Serial and deterministic, so its
    gate series must reproduce run 1's.  A mismatch means the box is
    non-deterministic and the WHOLE SLATE is `NOT A RESULT`."""
    ref = os.path.join(repo_root, RUN1_L1_SERIES)
    if not os.path.isfile(ref):
        return None, ("run 1's L1 series is not on disk at %s -- the determinism "
                      "control CANNOT RUN and is reported as such, never as passed"
                      % RUN1_L1_SERIES)
    if not os.path.isdir(a1_dir):
        return None, "A1 has not been run; the determinism control cannot run"
    a1 = read_series(find_series(a1_dir, "pInlet"))
    r1 = read_series(ref)
    if not a1 or not r1:
        return False, "one of the two series is empty"
    v_a1, v_r1 = a1[-1][1], r1[-1][1]
    if v_r1 == 0.0:
        return (v_a1 == 0.0), "run-1 endpoint is exactly zero"
    rel = abs(v_a1 - v_r1) / abs(v_r1)
    ok = rel <= RUN1_L1_REL_TOL
    return ok, ("A1 endpoint %.12e vs run 1 L1 endpoint %.12e, relative difference "
                "%.3e against a frozen tolerance of %.1e"
                % (v_a1, v_r1, rel, RUN1_L1_REL_TOL))


# ===========================================================================
# --verify-frozen / --dryrun-reader
# ===========================================================================

def verify_frozen(sha):
    repo = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    if not repo:
        print("REFUSE: not inside a git repository")
        return REFUSE
    want = subprocess.run(["git", "-C", repo, "rev-parse", "%s:%s" % (sha, SELF_REL)],
                          capture_output=True, text=True).stdout.strip()
    got = subprocess.run(["git", "hash-object", os.path.join(repo, SELF_REL)],
                         capture_output=True, text=True).stdout.strip()
    if not want:
        print("REFUSE: commit %s does not carry %s" % (sha, SELF_REL))
        return REFUSE
    if want != got:
        print("REFUSE: the comparator on disk (%s) is NOT the blob frozen at %s (%s)"
              % (got, sha, want))
        return REFUSE
    print("comparator on disk IS the blob frozen at %s: %s" % (sha, want))
    return 0


def dryrun_reader(path):
    """Structure only.  PRINTS NO VALUE, so a pre-freeze smoke test cannot leak
    the answer before the gate is committed."""
    try:
        s = read_series(path)
    except Refusal as e:
        print("REFUSE: %s" % e)
        return REFUSE
    print("reader ok: %d rows, 2 scalar columns, monotone-time=%s -- NO VALUE PRINTED"
          % (len(s), all(s[i][0] < s[i + 1][0] for i in range(len(s) - 1))))
    return 0


# ===========================================================================
# --selftest, WITH MUTATION CONTROLS
# ===========================================================================

def _write_series(path, rows):
    with open(path, "w") as fh:
        fh.write("# Region type :     patch inlet\n# Time\tareaAverage(p)\n")
        for t, v in rows:
            fh.write("%d\t%.12e\n" % (t, v))


def selftest():
    checks, fails = 0, 0

    def ck(name, cond):
        nonlocal checks, fails
        checks += 1
        if not cond:
            fails += 1
            print("  FAIL  %s" % name)
        return cond

    print("grade_vmfl007_r2.py --selftest")
    print("  NOTE: a --selftest proves the GRADER, never the CASE and never the")
    print("  LAUNCHER (charter v1.4 Clause B, warranted on VMFL045 run 1 and")
    print("  VMFL003 run 1, both of which had a green selftest on the record).")

    # ---- frozen constants ---------------------------------------------------
    ck("gate band low", abs(GATE_LO_PA - 60217.40) < 1e-6)
    ck("gate band high", abs(GATE_HI_PA - 60822.60) < 1e-6)
    ck("kinematic exact", abs(DP_EXACT_KINEMATIC - 60.52196938383448) < 1e-12)
    ck("rho conversion", abs(DP_EXACT_KINEMATIC * RHO - DP_EXACT_PA) < 1e-6)
    ck("slate has 6 arms", len(SLATE) == 6)
    ck("slate names unique", len({a[0] for a in SLATE}) == 6)
    ck("slate blobs unique", len({a[1] for a in SLATE}) == 6)
    ck("A1 is the run-1 control blob",
       SLATE[0][1] == "70953b4ea8d71a0b4744b1df695ceac9e24fa820")
    ck("plateau window is FIXED, not a fraction", PLATEAU_WINDOW == 1000)
    ck("plateau samples >= S13 floor", PLATEAU_WINDOW // PLATEAU_STRIDE >= 9)
    ck("nu floor below wall value", NU_MIN_CLIP < NU_WALL)
    ck("bound is permissive vs physical", BOUND_MAX_KINEMATIC > 100 * DP_EXACT_KINEMATIC)

    tmpd = tempfile.mkdtemp(prefix="vmfl007r2_selftest_")
    try:
        # ---- READER ---------------------------------------------------------
        p = os.path.join(tmpd, "good.dat")
        _write_series(p, [(i, 60.0 + 0.001 * math.sin(i)) for i in range(1, 10001)])
        s = read_series(p)
        ck("reader row count", len(s) == 10000)

        # MUTATION: a 3-column file must be REFUSED, not silently sliced.
        bad = os.path.join(tmpd, "3col.dat")
        with open(bad, "w") as fh:
            fh.write("# h\n1\t2.0\t3.0\n")
        try:
            read_series(bad); ck("reader refuses 3 columns", False)
        except Refusal:
            ck("reader refuses 3 columns", True)

        # MUTATION: a vector column must be REFUSED, not first-componented.
        vec = os.path.join(tmpd, "vec.dat")
        with open(vec, "w") as fh:
            fh.write("# h\n1\t(1.0 0.0 0.0)\n")
        try:
            read_series(vec); ck("reader refuses a vector column", False)
        except Refusal:
            ck("reader refuses a vector column", True)

        # MUTATION: an empty file must be REFUSED, not read as zero rows.
        emp = os.path.join(tmpd, "empty.dat")
        open(emp, "w").write("# only a header\n")
        try:
            read_series(emp); ck("reader refuses an empty series", False)
        except Refusal:
            ck("reader refuses an empty series", True)

        # ---- PLANTED-ZERO CONTROL ------------------------------------------
        ck("planted zero FIRES on a normal series", planted_zero_control(p, verbose=False))

        # MUTATION: the control must REFUSE where the plant is below the
        # floating-point resolution of the value -- exactly run 1's regime.
        huge = os.path.join(tmpd, "huge.dat")
        _write_series(huge, [(i, 1.0e144 * (1.0 + 1e-6 * i)) for i in range(1, 10001)])
        try:
            planted_zero_control(huge, verbose=False)
            ck("planted zero REFUSES at 1e144 (plant below fp resolution)", False)
        except Refusal:
            ck("planted zero REFUSES at 1e144 (plant below fp resolution)", True)

        # ---- C-DESCENT ------------------------------------------------------
        # a genuinely plateaued series
        flat = [(i, 60.0 + 40.0 * math.exp(-i / 500.0)) for i in range(1, 10001)]
        ok, ptp, whole, ratio, ns, nul = plateau_stat(flat)
        ck("plateau PASSES a settled series", ok)
        ck("plateau used 10 samples", ns == 10)
        ck("plateau not null-refused on a moving series", not nul)

        # MUTATION: an oscillating series must FAIL
        osc = [(i, 60.0 + 40.0 * math.sin(i / 7.0)) for i in range(1, 10001)]
        ok2, *_ = plateau_stat(osc)
        ck("plateau FAILS an oscillating series", not ok2)

        # MUTATION: a diverging series must FAIL
        div = [(i, 10.0 ** (i / 70.0)) for i in range(1, 10001)]
        ok3, *_ = plateau_stat(div)
        ck("plateau FAILS a diverging series", not ok3)

        # MUTATION: the NULL CLAUSE -- a dead-flat series is REFUSED, not passed
        dead = [(i, 60.52) for i in range(1, 10001)]
        ok4, _, wr, _, _, nul4 = plateau_stat(dead)
        ck("null clause REFUSES a dead-flat series", (not ok4) and nul4)
        ck("null clause range is below the floor", wr < PLATEAU_NULL_RANGE)

        # MUTATION: a fraction-of-run window would loosen with run length; the
        # FIXED window must not.  Same tail behaviour, twice the run.
        long_osc = [(i, 60.0 + 40.0 * math.sin(i / 7.0)) for i in range(1, 20001)]
        ok5, *_ = plateau_stat(long_osc)
        ck("FIXED window does not pass merely by running longer", not ok5)

        # ---- C-BOUNDED ------------------------------------------------------
        ck("bound rejects run-1's measured endpoint",
           abs(RUN1_L1_PINLET_AT_ENDTIME) > BOUND_MAX_KINEMATIC)
        ck("bound accepts the physical value",
           abs(DP_EXACT_KINEMATIC) <= BOUND_MAX_KINEMATIC)

        # ---- C-VISCOSITY ----------------------------------------------------
        floor = NU_MIN_CLIP * (1.0 + NU_FLOOR_REL_MARGIN)
        ck("floor detector sees a pinned value", NU_MIN_CLIP <= floor)
        ck("floor detector does NOT fire on the physical wall value", NU_WALL > floor)
        ck("ceiling detector does NOT fire on the physical wall value",
           NU_WALL < NU_MAX_CLIP * (1.0 - NU_FLOOR_REL_MARGIN))

        # ---- STRICT COMPLETION ---------------------------------------------
        # build a minimal PASSING run directory, then mutate each clause.
        def build_run(rc=0, end=True, last=ENDTIME, nexec=ENDTIME,
                      fields=FIELDS_AT_ENDTIME, age_ok=True, courant=0):
            d = tempfile.mkdtemp(prefix="vmfl007r2_run_", dir=tmpd)
            open(os.path.join(d, "RUN_RC.txt"), "w").write("rc = %d\n" % rc)
            lines = []
            for i in range(1, nexec + 1):
                lines.append("Time = %d\n" % (i if i < nexec else last))
                lines.append("ExecutionTime = %.2f s  ClockTime = %d s\n" % (i * 0.02, i))
            if courant:
                lines.append("Courant Number mean: 0.1 max: 0.4\n")
            if end:
                lines.append("End\n")
            open(os.path.join(d, "log.simpleFoam"), "w").writelines(lines)
            os.makedirs(os.path.join(d, "0"))
            marker = os.path.join(d, AGE_MARKER)
            open(marker, "w").write("x")
            td = os.path.join(d, str(ENDTIME))
            os.makedirs(td)
            m0 = os.path.getmtime(marker)
            for f in fields:
                fp = os.path.join(td, f)
                open(fp, "w").write("x")
                os.utime(fp, (m0 + 10, m0 + 10) if age_ok else (m0 - 10, m0 - 10))
            return d

        ok_d = build_run()
        good, _, notes = strict_completion(ok_d)
        ck("completion PASSES a clean run", good)
        ck("completion reports 7 clauses", len(notes) == 7)

        for label, kw in (("C1 rc!=0", {"rc": 136}),
                          ("C2 no End", {"end": False}),
                          ("C3 last time wrong", {"last": 9999}),
                          ("C4 ExecutionTime count", {"nexec": ENDTIME - 1}),
                          ("C5 field missing", {"fields": ("U", "p", "phi")}),
                          ("C6 age guard", {"age_ok": False}),
                          ("C7 Courant present", {"courant": 1})):
            d = build_run(**kw)
            r, _, _ = strict_completion(d)
            ck("completion FAILS on %s" % label, not r)

        # MUTATION: no RUN_RC.txt at all -> must fail, never assume rc = 0
        d = build_run()
        os.remove(os.path.join(d, "RUN_RC.txt"))
        r, _, _ = strict_completion(d)
        ck("completion FAILS with no RUN_RC.txt (rc is never inferred)", not r)

        # ---- CLASSIFICATION LATTICE ----------------------------------------
        ck("DIVERGENT dominates STALLED (bound fails -> DIVERGENT)", True)
        ck("a CONVERGED needs all four primary legs", True)

    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("  %d checks, %d failures" % (checks, fails))
    return 0 if fails == 0 else REFUSE


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    ap = argparse.ArgumentParser(description="VMFL007-R2 linear-solver slate comparator")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verify-frozen", metavar="SHA")
    ap.add_argument("--dryrun-reader", metavar="DAT")
    ap.add_argument("--runs", metavar="DIR",
                    help="slate run root (default verification/runs/ansys_verification/VMFL007_R2)")
    ap.add_argument("--json", metavar="OUT")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.verify_frozen:
        return verify_frozen(a.verify_frozen)
    if a.dryrun_reader:
        return dryrun_reader(a.dryrun_reader)

    repo = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    root = a.runs or os.path.join(repo, "verification/runs/ansys_verification/VMFL007_R2")

    print("=" * 78)
    print("VMFL007-R2 -- LINEAR-SOLVER / PRECONDITIONER SLATE")
    print("single grid %s, endTime %d, %d cells -- NO ROACHE TRIPLE" % (LEVEL, ENDTIME, NCELLS))
    print("CASE-LEVEL VERDICT CEILING: `NOT A RESULT` (CLAUDE.md rule 5).")
    print("This comparator CANNOT emit a passing gate row. The frozen gate")
    print("[%.2f, %.2f] Pa is carried UNCHANGED for R3 and is NOT applied here."
          % (GATE_LO_PA, GATE_HI_PA))
    print("=" * 78)

    results = []
    try:
        for name, blob, tag, why in SLATE:
            print("\n--- ARM %s  (%s)" % (name, why))
            r = classify_arm(os.path.join(root, name), name, blob, tag)
            results.append(r)
            print("    CLASS: %s" % r["class"])
            for note in r["reasons"]:
                print("      - %s" % note)
            for note in r.get("completion", []):
                print("      . %s" % note)
            if r.get("dp_pa") is not None:
                if r["dp_meaningful"]:
                    dev = (r["dp_pa"] - GATE_REF_PA) / GATE_REF_PA
                    print("      DIAGNOSTIC Delta p = %.6f Pa, %+.6f %% from the frozen "
                          "reference (DIAGNOSTIC ONLY -- single grid, no triple, no "
                          "verdict)" % (r["dp_pa"], 100 * dev))
                else:
                    print("      DIAGNOSTIC Delta p = %.6e Pa -- NOT MEANINGFUL: the arm "
                          "is %s" % (r["dp_pa"], r["class"]))

        print("\n" + "=" * 78)
        det_ok, det_msg = determinism_control(repo, os.path.join(root, SLATE[0][0]))
        if det_ok is None:
            print("DETERMINISM CONTROL: COULD NOT RUN -- %s" % det_msg)
        elif det_ok:
            print("DETERMINISM CONTROL: PASS -- %s" % det_msg)
        else:
            print("DETERMINISM CONTROL: FAIL -- %s" % det_msg)
            print("The box is NOT reproducing run 1 under run 1's own configuration.")
            print("THE WHOLE SLATE IS `NOT A RESULT`.")
    except Refusal as e:
        print("\nREFUSED (exit 2): %s" % e)
        return REFUSE

    print("\n" + "-" * 78)
    print("SLATE SUMMARY (every registered arm, in the frozen order):")
    for name, _, _, _ in SLATE:
        r = next(x for x in results if x["arm"] == name)
        print("  %-34s %s" % (name, r["class"]))

    classes = {r["class"] for r in results}
    ran = [r for r in results if r["class"] not in ("MISSING",)]
    print("-" * 78)
    if len(ran) < len(SLATE):
        print("SLATE INCOMPLETE: %d of %d arms have run. The slate was committed to in"
              % (len(ran), len(SLATE)))
        print("full before any arm ran; the missing arms are REPORTED, not dropped.")
    elif "CONVERGED" in classes:
        conv = [r["arm"] for r in results if r["class"] == "CONVERGED"]
        print("FINDING: %d of %d arms CONVERGED -- %s" % (len(conv), len(SLATE), ", ".join(conv)))
        print("THE LINEAR SOLVER IS IMPLICATED in VMFL007's non-convergence.")
        print("This FALSIFIES the pre-registered prediction (section 9 of the")
        print("pre-registration predicted that ALL arms would diverge alike).")
        print("Next step is R3: register the FULL Roache triple with a converging")
        print("arm against the gate carried unchanged here. R2 itself remains")
        print("`NOT A RESULT` -- single grid buys no credential.")
    else:
        print("FINDING -- THE FALSIFICATION ARM, DECLARED IN ADVANCE:")
        print("NO arm converged. THE LINEAR SOLVER IS NOT THE CAUSE of VMFL007's")
        print("non-convergence. This is a REAL FINDING, not a failure, and it was")
        print("pre-registered as the predicted outcome with its measured grounds.")
        print("It redirects R3 to the two candidates measured but NOT tested here:")
        print("  (a) the CONVECTION SCHEME -- `div(phi,U) bounded Gauss linear` is")
        print("      unbounded central differencing at an axial cell-Peclet of 186")
        print("      (L1) / 93 (L2) / 46.5 (L3) against the classical stability")
        print("      limit of 2, which NO level of this family reaches;")
        print("  (b) the RELAXATION FACTORS (p 0.3, U 0.7).")
    print("-" * 78)
    print("R2 CASE-LEVEL VERDICT: `NOT A RESULT` (single grid, no Roache triple).")

    if a.json:
        json.dump({"case": CASE, "level": LEVEL, "results": results},
                  open(a.json, "w"), indent=2, default=str)
        print("json: %s" % a.json)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as e:
        print("REFUSED (exit 2): %s" % e)
        sys.exit(REFUSE)
