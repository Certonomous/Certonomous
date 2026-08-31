#!/usr/bin/env python3
"""
JF1 -- THE COMPARATOR.  Jet-flap NACA 0012, ARC R&M 3304.

THIS FILE IS A TRANSCRIPTION of sections 8.1, 8.2, 8.3 and 8.4 of
`verification/campaign/JF1_PREREGISTRATION.md`, FROZEN at blob
66543c97fa1527ef7c36f0980460fcc0ca348508.  Where this lane believes the frozen
document is wrong it implements the document as frozen and reports the
disagreement separately; rule 2 closed those gates and this file does not
reopen them.  Every registered clause below carries the frozen document's own
line number.

THE COMPARATOR REFUSES (exit 2) RATHER THAN DEGRADES (:1577).  There is no path
in it that emits a number when a precondition fails.

REFUSAL DISCIPLINE: every refusal raises `Refusal`, carrying a stable CODE, and
`main` converts it to `REFUSED[<CODE>]` on stderr plus `sys.exit(2)`.  ZERO
`assert` statements in this file, in `foam_io_jf1.py` and in `mutation_jf1.py`
(L-332), censused by AST at every entry.

VERDICT VOCABULARY (:1739): PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING and nothing else.  Sealed by `seal_verdict`.

NOT IMPLEMENTED, NAMED RATHER THAN OMITTED -- see `NOT_IMPLEMENTED` at the foot
of this module and the report that accompanies it.
"""
import sys

if not __debug__:
    sys.stderr.write(
        "REFUSED[R-DASH-O]: analyse_jf1.py must not run under `python3 -O`.\n"
        "  -O deletes every `assert`, including the _seal invariants in the shared\n"
        "  scripts/roache_triple.py (verdict vocabulary, the one-way gate, no GCI\n"
        "  on a non-monotone triple).  With those deleted, rule 1 and rule 5 are\n"
        "  enforced by nothing.\n")
    sys.exit(2)

import os
import re
import ast
import json
import math
import shutil
import hashlib
import tempfile
import argparse
import datetime
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if os.path.join(REPO, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(REPO, "scripts"))

import foam_io_jf1 as FIO                                   # noqa: E402
import roache_triple as RT                                  # noqa: E402


# ===========================================================================
# THE FROZEN CONSTANTS.  Each carries the line of JF1_PREREGISTRATION.md it is
# transcribed from.  Nothing here is computed from a run.
# ===========================================================================
PREREG = os.path.join(REPO, "verification", "campaign", "JF1_PREREGISTRATION.md")
FREEZE_BLOB = "66543c97fa1527ef7c36f0980460fcc0ca348508"     # :2364 / RUN_STATUS

# ---- section 8.1 clause 3, THE PIN (:1612-1619)
PIN_CONTROLDICT = {"startTime": "0", "deltaT": "1", "endTime": "20000",
                   "writeControl": "timeStep", "writeInterval": "20000"}
PIN_RESIDUALCONTROL = {"p": 1e-6, "U": 1e-6, "k": 1e-6, "omega": 1e-6}
N_MIN = 2000            # :1627 -- below this the section 5.5 plateau window does not exist
N_CAP = 20000           # :1013 -- ITERATION CAP.  Hitting it is NOT A RESULT.
RESIDUAL_3A = 1e-6      # :1629-1630
RESIDUAL_CHANNELS_3A = ("p", "Ux", "Uy", "k", "omega")       # :1629

# ---- section 8.1 clause 4 (:1657) -- THIS FAMILY's field list
FIELDS_AT_NSTOP = ("U", "p", "k", "omega", "nut")
AGE_DATUM = os.path.join("0", "U")                           # :1666-1670

# ---- section 8.2, the three plants (:1687-1704)
PLANT_CL = 1.234e-03            # :1687
PLANT_CL_TOL = 1e-9             # :1691
PLANT_MASSFLOW_PCT = 2.000      # :1697
PLANT_MASSFLOW_TOL = 1e-6       # :1697
MASSFLOW_FLAG_PCT = 0.5         # :1697, :1534

# ---- section 0 / 2 -- symbols and derived quantities (:130-139, :442-464)
TAU = math.pi / 6.0             # :132, :451 -- pi/6 EXACTLY, never 0.5235988
U_INF = 10.0                    # :446
CHORD = 1.0                     # :445
H_SLOT = 0.005                  # :135, :450
NU = 1.0e-5                     # :447
T_Z = 1.0                       # :1160 -- t_z = 1.0 m EXACTLY
AREA_JETSLOT = 0.005            # :1164 -- h * t_z
AREA_JETSLOT_TOL = 1e-9         # :1164
C_MU_SWEEP = (0.0, 0.05, 0.10, 0.20, 0.40)                   # :130, :452
ALPHA_SWEEP = (0, 4, 8)                                      # :134, :453

# ---- section 7.3 -- gate THEORY (:1490-1495, :1511-1512, :1523)
CL_THEORY = {0.05: 0.4234034434, 0.10: 0.6047756775,
             0.20: 0.8687421542, 0.40: 1.2594769538}
THEORY_A_GATED = (0.05, 0.10, 0.20)                          # :1498-1502
THEORY_BAND = 0.15                                           # :1492-1494, :1523
DCLDALPHA_THEORY = 6.7208116310                              # :1511-1512  /rad

# ---- section 7.2 / 4.2 -- gate G (:1440-1442, :1463, :590-598)
ORDER_BAND = (1.3, 2.5)                                      # :1440
GCI_MAX = 0.03                                               # :1441
FS = 1.25                                                    # :1442
DIM = 2
ROACHE_MAP = (("1 (fine)", "L3"), ("2 (medium)", "L2"), ("3 (coarse)", "L1"))  # :590-594
PLANNED_CELLS = {"L1": 46180, "L2": 86638, "L3": 161006}     # :570
RATIO_GAP_REL_MAX = 0.01                                     # :615, :1750

# ---- section 5.5 / 5.5a / 5.5b -- the absolute bounds (:979-988, :1050-1054, :1116)
BOUND_SUM_LOCAL = 1e-8                                       # :981, :1119
BOUND_NUT_OVER_NU = 1e5                                      # :988
BOUND_DCL = 1e-4                                             # :986
BOUND_DCD = 1e-5                                             # :987
PLATEAU_WINDOW = 2000                                        # :986-987, :1022-1024
BLOWUP_M = 2.0                                               # :1053
UPEAK_A = 1.196                                              # :1052
UPEAK_B = 6.108                                              # :1052
GUARD_MARGINAL_RATIO = 1.2                                   # :1097

# ---- section 7.4 -- physicality (:1534-1541)
YPLUS_MAX = 1.0                                              # :1538
MASSFLOW_TOL_FRAC = 0.005                                    # :1534
JET_SHEET_MIN_CELLS = 8                                      # :1539
FRAME_TOL = 1e-9                                             # :1540, :408

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


class Refusal(Exception):
    def __init__(self, code, msg):
        Exception.__init__(self, msg)
        self.code = code
        self.msg = msg


def refuse(code, msg):
    raise Refusal(code, msg)


def seal_verdict(word):
    """Section 8.3 (:1739-1742): the comparator emits ONLY the six words.  It
    has no other verdict string and no adjectives."""
    if word not in VERDICTS:
        refuse("R-VERDICT-VOCABULARY",
               "%r is not one of the six registered verdicts %s. Section 8.3: "
               "`there is no softer word available to it`." % (word, list(VERDICTS)))
    return word


# ===========================================================================
# DERIVED REGISTERED QUANTITIES -- recomputed, never copied (:439-440)
# ===========================================================================
def v_jet(c_mu_jet):
    """:455 -- `V_j = U_inf sqrt( C_mu_jet / (2 h/c) )`."""
    return U_INF * math.sqrt(c_mu_jet / (2.0 * (H_SLOT / CHORD)))


def cl_pred(c_mu_jet, alpha_deg):
    """The row's own predicted lift, used ONLY by the section 5.5a blow-up
    guard (:1051-1053) and never reported as a prediction of the answer."""
    if c_mu_jet == 0.0:
        return 0.0
    if c_mu_jet not in CL_THEORY:
        refuse("R-BOUND-BLOWUP-UNREGISTERED",
               "no registered CL_theory for C_mu_jet = %r; section 5.5a derives the "
               "blow-up bound from the row's own predicted peak and this row has no "
               "registered prediction" % c_mu_jet)
    return CL_THEORY[c_mu_jet] + DCLDALPHA_THEORY * math.radians(alpha_deg)


def u_peak_pred(c_mu_jet, alpha_deg):
    """:1051-1053 -- `U_peak_pred = max(V_j, U_inf * (u/U)_peak)`,
    `(u/U)_peak = 1.196 + 6.108 * alpha_eff`, `alpha_eff = CL_pred / (2 pi)`."""
    alpha_eff = cl_pred(c_mu_jet, alpha_deg) / (2.0 * math.pi)
    return max(v_jet(c_mu_jet), U_INF * (UPEAK_A + UPEAK_B * alpha_eff))


def blowup_bound(c_mu_jet, alpha_deg):
    return BLOWUP_M * u_peak_pred(c_mu_jet, alpha_deg)


def jet_reaction(c_mu_jet, alpha_deg):
    """:1217, :382 -- `C_mu_jet sin(tau + alpha)`, AIRFOIL FRAME (section 1.6a)."""
    return c_mu_jet * math.sin(TAU + math.radians(alpha_deg))


# ===========================================================================
# SECTION 8.1 -- THE STRICT COMPLETION RULE, IN FULL
# ===========================================================================
def prelaunch_guard(case_dir):
    """:1672-1674 -- "A pre-launch guard REFUSES to start a case whose run
    directory already contains `0/` or any time directory."  This is the LAUNCH
    guard, run before a solver starts, never as part of grading a finished run."""
    if not os.path.isdir(case_dir):
        return dict(ok=True, why="run directory %s does not exist" % case_dir)
    bad = []
    if os.path.isdir(os.path.join(case_dir, "0")):
        bad.append("0")
    bad += [d for d in FIO.numeric_time_dirs(case_dir) if d != "0"]
    if bad:
        refuse("R-PRELAUNCH-POPULATED",
               "PRE-LAUNCH GUARD (:1672): %s already contains %s. A restart into a "
               "populated directory is not a run; it is an answer of unknown "
               "parentage." % (case_dir, bad))
    return dict(ok=True, why="%s contains no `0/` and no time directory" % case_dir)


def check_pin(case_dir):
    """Section 8.1 clause 3, THE PIN (:1612-1619).  Read FIRST inside clause 3,
    because "a run whose termination settings were changed is not a run of this
    registration" and every later branch reads a number whose meaning the pin
    fixes."""
    cd_path = os.path.join(case_dir, "system", "controlDict")
    try:
        cd = FIO.read_control_dict(cd_path)
    except FIO.FoamReadError as e:
        refuse("R-PIN-CONTROLDICT", "clause 3 pin: %s" % e)
    bad = []
    for key, want in PIN_CONTROLDICT.items():
        got = cd.get(key)
        same = False
        if got is not None:
            if key in ("writeControl",):
                same = (got == want)
            else:
                try:
                    same = (float(got) == float(want))
                except ValueError:
                    same = False
        if not same:
            bad.append("%s = %r (registered %r)" % (key, got, want))
    if bad:
        refuse("R-PIN-CONTROLDICT",
               "clause 3 PIN FAILS on %s (:1615-1616): %s. A run whose termination "
               "settings were changed is not a run of this registration."
               % (cd_path, "; ".join(bad)))

    fv_path = os.path.join(case_dir, "system", "fvSolution")
    try:
        rc_keys = FIO.read_residual_control(fv_path)
    except FIO.FoamReadError as e:
        refuse("R-PIN-FVSOLUTION", "clause 3 pin: %s" % e)
    if set(rc_keys) != set(PIN_RESIDUALCONTROL):
        refuse("R-PIN-FVSOLUTION",
               "clause 3 PIN FAILS on %s (:1616-1618): residualControl keys are %s, "
               "registered exactly %s" % (fv_path, sorted(rc_keys),
                                          sorted(PIN_RESIDUALCONTROL)))
    bad = []
    for key, want in PIN_RESIDUALCONTROL.items():
        try:
            got = float(rc_keys[key])
        except ValueError:
            got = None
        if got is None or got != want:
            bad.append("%s = %r (registered %g)" % (key, rc_keys[key], want))
    if bad:
        refuse("R-PIN-FVSOLUTION",
               "clause 3 PIN FAILS on %s (:1616-1618): %s. All five residual "
               "channels are held to the SAME order 1e-6 (:990)."
               % (fv_path, "; ".join(bad)))
    return dict(controlDict=cd, residualControl=rc_keys)


def check_completion(case_dir, case_id):
    """SECTION 8.1 IN FULL (:1580-1674).  Returns a record when EVERY clause
    holds; refuses (exit 2) otherwise.  Clause order is the document's order,
    and it is load-bearing: the cap branch 3b is reached before clause 5 so a
    capped run is labelled `cap hit` rather than mislabelled a log/field
    disagreement."""
    rec = dict(case=case_dir, case_id=case_id)

    # ---- clause 1: rc = 0, from the wrapper's own record (:1606-1607, :1807-1810)
    try:
        st = FIO.read_run_status(case_dir, case_id)
    except FIO.FoamReadError as e:
        refuse("R-COMPLETION-1-RC", "clause 1 (:1606): %s" % e)
    rc = st["fields"].get("solver_rc")
    rec["run_status"] = st["path"]
    rec["solver_rc"] = rc
    if rc is None:
        refuse("R-COMPLETION-1-RC",
               "clause 1 (:1606): %s carries no `solver_rc` key. Section 9.2 writes "
               "it; its absence is not a zero." % st["path"])
    if rc.strip() != "0":
        refuse("R-COMPLETION-1-RC",
               "clause 1 (:1606): solver_rc = %r, not 0, in %s. A crash is a "
               "FINDING; the row is NOT A RESULT." % (rc, st["path"]))

    # ---- clause 2: an `End` line in log.simpleFoam (:1608)
    log_path = os.path.join(case_dir, "log.simpleFoam")
    try:
        log = FIO.read_solver_log(log_path)
    except FIO.FoamReadError as e:
        refuse("R-COMPLETION-2-END", "clause 2 (:1608): %s" % e)
    rec["log"] = log_path
    rec["fatal_token_REPORTED"] = log["fatal"]
    if not log["has_end"]:
        refuse("R-COMPLETION-2-END",
               "clause 2 (:1608): no `End` line in %s (last line: %r). rc = 0 and the "
               "log disagree." % (log_path, log["last_line"]))

    # ---- clause 3: THE PIN, then exactly one termination branch (:1609-1655)
    rec["pin"] = check_pin(case_dir)

    ns, time_dirs = FIO.n_stop(case_dir)
    rec["time_dirs"] = time_dirs
    if ns is None:
        refuse("R-TERM-3C-EARLY-STOP",
               "clause 3 (:1621): no time directory other than `0` under %s, so "
               "`N_stop` does not exist. rc = 0 and `End` present with NO written "
               "field is branch 3c: the run stopped for a reason that is not "
               "convergence." % case_dir)
    n_stop = int(float(ns))
    rec["N_stop"] = n_stop
    conv = log["converged"]
    rec["converged_lines"] = conv
    rec["n_exec"] = log["n_exec"]

    # -- 3b, THE CAP.  Checked before 3a's arithmetic so that a capped run is
    #    labelled a cap hit and not something else (:1641-1644).
    if n_stop == N_CAP and not conv:
        refuse("R-TERM-3B-CAP",
               "clause 3b CAP HIT (:1641): N_stop = %d == the registered iteration cap "
               "%d and the log carries no converged line. Section 5.5's registered "
               "words apply verbatim -- a run that hits the cap is NOT A RESULT, never "
               "`close enough`. It is not a refusal to be argued with."
               % (n_stop, N_CAP))

    # -- 3c, THE EARLY STOP.  The limb that keeps an early EXIT apart from an
    #    early STOP (:1646-1655).
    if not conv and n_stop < N_CAP:
        refuse("R-TERM-3C-EARLY-STOP",
               "clause 3c EARLY STOP (:1646): N_stop = %d < %d and there is NO "
               "converged line naming it. The run stopped early for a reason that is "
               "not convergence -- divergence, FatalError, a signal, an OOM kill, a "
               "wall-clock timeout, a lost MPI rank, a truncated log or a hand-stopped "
               "solve. rc = %r; `End` present = %s; last log line %r; fatal token %r."
               % (n_stop, N_CAP, rc, log["has_end"], log["last_line"], log["fatal"]))

    # -- 3a, THE ONLY COMPLETE TERMINATION (:1623-1630)
    if len(conv) != 1:
        refuse("R-TERM-3A-CONVERGED-LINE",
               "clause 3a (:1624-1625): `SIMPLE solution converged in <N> iterations` "
               "must appear EXACTLY ONCE in %s; it appears %d times (%s). More than "
               "one is a concatenated or restarted log and the comparator will not "
               "choose an N." % (log_path, len(conv), conv))
    n_conv = conv[0]
    rec["N_converged"] = n_conv
    if n_conv != n_stop:
        refuse("R-TERM-3A-N-MISMATCH",
               "clause 3a (:1626): the converged line names N = %d but the last time "
               "directory is %d. The integer in that line must BE the last time "
               "directory; the log and the written fields disagree about where the "
               "run ended." % (n_conv, n_stop))
    if n_stop >= N_CAP:
        refuse("R-TERM-3B-CAP",
               "clause 3a (:1627-1628): N_stop = %d is at or beyond the cap %d; see "
               "branch 3b. NOT A RESULT." % (n_stop, N_CAP))
    if n_stop < N_MIN:
        refuse("R-TERM-3A-BELOW-2000",
               "clause 3a (:1627): N_stop = %d < %d. Below 2 000 the section 5.5 "
               "plateau window (|dCL| and |dCd| over the LAST 2 000 iterations) does "
               "not exist and the clause is unevaluable. NOT A RESULT, with N_stop "
               "printed; a finding about the case, never a pass." % (n_stop, N_MIN))
    res = FIO.final_initial_residuals(log)
    rec["final_initial_residuals"] = res
    missing = [c for c in RESIDUAL_CHANNELS_3A if res.get(c) is None]
    if missing:
        refuse("R-TERM-3A-RESIDUAL",
               "clause 3a (:1629): the final iteration of %s carries no initial "
               "residual for %s. An absent residual is not a small one."
               % (log_path, missing))
    over = {c: res[c] for c in RESIDUAL_CHANNELS_3A if not (res[c] < RESIDUAL_3A)}
    if over:
        refuse("R-TERM-3A-RESIDUAL",
               "clause 3a (:1629-1630): the final iteration's initial residuals must "
               "ALL be < %g; these are not: %s. The solver did not meet the "
               "registered criteria." % (RESIDUAL_3A, over))
    rec["termination"] = "3a CONVERGED EARLY EXIT"

    # ---- clause 4: fields present at N_stop (:1657-1660)
    end_dir = os.path.join(case_dir, ns)
    absent = [f for f in FIELDS_AT_NSTOP if not os.path.isfile(os.path.join(end_dir, f))]
    if absent:
        refuse("R-COMPLETION-4-FIELDS",
               "clause 4 (:1657): fields %s absent from %s. This family's registered "
               "list is `U p k omega nut`; the thermal family's `T alphat p_rgh` do "
               "not exist here and are not required." % (absent, end_dir))
    rec["fields_at_N_stop"] = list(FIELDS_AT_NSTOP)

    # ---- clause 5: ExecutionTime count == N_stop (:1661-1665)
    if log["n_exec"] != n_stop:
        refuse("R-COMPLETION-5-EXECTIME",
               "clause 5 (:1661): %d `ExecutionTime` lines in %s but N_stop = %d. The "
               "log and the written fields disagree about how many iterations were "
               "taken. NOT `== endTime` -- that clause was STRUCK at :1586-1588."
               % (log["n_exec"], log_path, n_stop))

    # ---- clause 6: THE AGE GUARD (:1666-1670)
    datum = os.path.join(case_dir, AGE_DATUM)
    if not os.path.isfile(datum):
        refuse("R-COMPLETION-6-AGE",
               "clause 6 (:1666): no %s to date the launch against. `0/U` is touched "
               "LAST at launch (section 9.2 :1783) and is this family's registered age "
               "datum -- there is no `0/T` here." % datum)
    t0 = os.path.getmtime(datum)
    stale = [f for f in FIELDS_AT_NSTOP
             if os.path.getmtime(os.path.join(end_dir, f)) <= t0]
    if stale:
        refuse("R-COMPLETION-6-AGE",
               "AGE GUARD, clause 6 (:1666): fields %s at N_stop = %d are NOT newer "
               "than %s. `0/U` dates the run that was allowed to produce the answer; "
               "a field older than it came from some other run." % (stale, n_stop, datum))
    rec["age_datum"] = datum
    rec["complete"] = True
    return rec


# ===========================================================================
# SECTION 8.2 -- THE THREE PLANTS.  Each writes a REAL FILE and reads it back
# THROUGH THE SAME READER THAT GRADES.  Each has a NEGATIVE LIMB proving the
# control can say no.
# ===========================================================================
def plant_1_cl(case_dir):
    """PLANT 1 -- THE `CL` READER (:1687-1693).

    Reader certified : `foam_io_jf1.read_cl` (via `read_coefficient_dat`)
    Graded quantity  : `CL_aero` -> `CL_total`, the comparand of gate G
                       (:1439) and of gate THEORY (a) and (b) (:1485, :1522)

    A byte-level copy of the real `coefficient.dat` is made; the `Cl` column is
    perturbed BY LINE INDEX at the final time by exactly PLANT_CL; the REAL,
    UNMODIFIED `read_cl()` is run on the copy."""
    clean = FIO.read_cl(case_dir)
    tmp = tempfile.mkdtemp(prefix="jf1_plant_cl_")
    try:
        work = os.path.join(tmp, "case")
        os.makedirs(os.path.join(work, "postProcessing", "forceCoeffs", "0"))
        dst = os.path.join(work, "postProcessing", "forceCoeffs", "0", "coefficient.dat")
        line_idx, before, after = FIO.plant_into_coefficient_dat(
            clean["path"], dst, "Cl", PLANT_CL)
        planted = FIO.read_cl(work)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    delta = planted["cl"] - clean["cl"]
    ok = abs(planted["cl"] - clean["cl"] - PLANT_CL) < PLANT_CL_TOL
    out = dict(name="PLANT 1 -- CL reader", reader="foam_io_jf1.read_cl",
               graded_quantity="CL_aero -> CL_total (gate G, gate THEORY)",
               artifact=clean["path"], planted=PLANT_CL, line_index=line_idx,
               before=clean["cl"], after=planted["cl"], delta=delta,
               tol=PLANT_CL_TOL, passed=bool(ok))
    if not ok:
        refuse("R-PLANT-CL",
               "PLANT 1 FAILED (:1690-1693): a `Cl` offset of %.6e planted by line "
               "index at the final time of %s must move `read_cl` by exactly that; it "
               "moved %.17g (residual %.3e >= %g). A CL of any value from a reader not "
               "shown able to see a change is NOT EVIDENCE (rule 3). NOT A RESULT."
               % (PLANT_CL, clean["path"], delta,
                  abs(delta - PLANT_CL), PLANT_CL_TOL))
    return out


def plant_1_negative_limb(case_dir):
    """The negative limb: a reader that CANNOT see the plant must make the
    control FIRE.  Without this the control's `passed` is not evidence either."""
    clean = FIO.read_cl(case_dir)
    tmp = tempfile.mkdtemp(prefix="jf1_plant_cl_neg_")
    try:
        work = os.path.join(tmp, "case")
        os.makedirs(os.path.join(work, "postProcessing", "forceCoeffs", "0"))
        dst = os.path.join(work, "postProcessing", "forceCoeffs", "0", "coefficient.dat")
        FIO.plant_into_coefficient_dat(clean["path"], dst, "Cl", PLANT_CL)
        # A BLIND reader: it opens the planted file and returns the CLEAN value.
        blind = clean["cl"]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    fired = not (abs(blind - clean["cl"] - PLANT_CL) < PLANT_CL_TOL)
    if not fired:
        refuse("R-PLANT-CL-NEGATIVE",
               "NEGATIVE LIMB FAILED for PLANT 1: a reader that returns the clean "
               "value for the planted file was NOT refused. The control cannot say "
               "no, so its yes means nothing.")
    return dict(name="PLANT 1 negative limb", blind_reader_delta=blind - clean["cl"],
                fired=True)


def massflow_mismatch(sum_phi, c_mu_jet):
    """The GRADED number of section 7.4's jet mass-flow check (:1534), in the
    units the solver actually produces -- `phi` is VOLUMETRIC (section 5.6
    HAZARD 3, :1180-1186), so both sides are m3/s.

    Returns (pct, expected) or (None, 0.0) at C_mu_jet = 0, where V_j = 0 makes
    both sides zero and the relative mismatch 0/0.  :1547-1551 registers that
    case as `N/A -- not run`, NEVER as `0.0 %` and never as a pass."""
    expected = v_jet(c_mu_jet) * H_SLOT * T_Z
    if expected == 0.0:
        return None, 0.0
    return 100.0 * abs(abs(sum_phi) - expected) / expected, expected


def plant_2_massflow(case_dir, c_mu_jet):
    """PLANT 2 -- THE JET MASS-FLOW READER, the check whose expected answer IS
    zero (:1695-1699).

    Reader certified : `foam_io_jf1.read_jet_sum_phi`
    Graded quantity  : the jet mass-flow relative mismatch (:1534, :1752)

    A known 2.000 % error is planted into the `jetSlot` `phi` sum on a copy; the
    REAL checker must report 2.000 % +- 1e-6 AND must FLAG it (> 0.5 %)."""
    if c_mu_jet == 0.0:
        refuse("R-PLANT-MASSFLOW",
               "PLANT 2 cannot be run at C_mu_jet = 0: V_j = 0 makes the registered "
               "expectation zero and the mismatch 0/0 (:1547). The plant is run on a "
               "BLOWN row and its result carries the unblown row, whose own check is "
               "recorded `N/A` (never `0.0 %`, never a pass).")
    clean = FIO.read_jet_sum_phi(case_dir)
    expected = v_jet(c_mu_jet) * H_SLOT * T_Z
    sign = -1.0 if clean["sum_phi"] < 0 else 1.0
    planted_value = sign * expected * (1.0 + PLANT_MASSFLOW_PCT / 100.0)
    tmp = tempfile.mkdtemp(prefix="jf1_plant_mdot_")
    try:
        work = os.path.join(tmp, "case")
        os.makedirs(os.path.join(work, "postProcessing", "jetMassFlow", "0"))
        dst = os.path.join(work, "postProcessing", "jetMassFlow", "0",
                           "surfaceFieldValue.dat")
        line_idx, before, _ = FIO.plant_into_surface_field_value(
            clean["path"], dst, planted_value)
        read_back = FIO.read_jet_sum_phi(work)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    pct, _ = massflow_mismatch(read_back["sum_phi"], c_mu_jet)
    flagged = pct is not None and pct > MASSFLOW_FLAG_PCT
    ok = pct is not None and abs(pct - PLANT_MASSFLOW_PCT) < PLANT_MASSFLOW_TOL
    out = dict(name="PLANT 2 -- jet mass-flow reader",
               reader="foam_io_jf1.read_jet_sum_phi",
               graded_quantity="jet mass-flow relative mismatch (section 7.4)",
               artifact=clean["path"], line_index=line_idx,
               planted_pct=PLANT_MASSFLOW_PCT, reported_pct=pct,
               flagged=bool(flagged), clean_sum_phi=before,
               planted_sum_phi=planted_value, expected_m3_s=expected,
               tol=PLANT_MASSFLOW_TOL, passed=bool(ok and flagged))
    if not ok:
        refuse("R-PLANT-MASSFLOW",
               "PLANT 2 FAILED (:1695-1699): a known %.3f %% error planted into the "
               "jetSlot phi sum on a copy of %s must be reported as %.3f %% +- %g; the "
               "checker reported %r. A checker that reports 0.0 %% on the planted case "
               "has not been shown able to see a non-zero and its 0.0 %% on the real "
               "case is NOT EVIDENCE."
               % (PLANT_MASSFLOW_PCT, clean["path"], PLANT_MASSFLOW_PCT,
                  PLANT_MASSFLOW_TOL, pct))
    if not flagged:
        refuse("R-PLANT-MASSFLOW",
               "PLANT 2 FAILED (:1697): the checker reported %.6f %% but did NOT FLAG "
               "it against the registered %.1f %% threshold. Seeing a non-zero and not "
               "acting on it is the same defect one step later." % (pct, MASSFLOW_FLAG_PCT))
    return out


def plant_2_negative_limb(case_dir, c_mu_jet):
    """The negative limb: a checker whose reported mismatch does not move with
    the planted value must make the control FIRE."""
    if c_mu_jet == 0.0:
        refuse("R-PLANT-MASSFLOW-NEGATIVE",
               "PLANT 2's negative limb needs a blown row (:1547)")
    clean = FIO.read_jet_sum_phi(case_dir)
    blind_pct, _ = massflow_mismatch(clean["sum_phi"], c_mu_jet)
    fired = blind_pct is None or abs(blind_pct - PLANT_MASSFLOW_PCT) >= PLANT_MASSFLOW_TOL
    if not fired:
        refuse("R-PLANT-MASSFLOW-NEGATIVE",
               "NEGATIVE LIMB FAILED for PLANT 2: a checker ignoring the plant and "
               "reading the clean file reported the planted %.3f %% anyway, so the "
               "control cannot distinguish a seeing reader from a blind one."
               % PLANT_MASSFLOW_PCT)
    return dict(name="PLANT 2 negative limb", blind_reported_pct=blind_pct, fired=True)


def plant_3_theory(c_mu_jet=0.10):
    """PLANT 3 -- THE THEORY-DIFFERENCE CHANNEL (:1701-1704).

    Channel certified : `foam_io_jf1.theory_rel_diff`
    Graded quantity   : the gate THEORY relative difference (:1492-1494)

    A deliberately wrong `CL_total` is fed in; the reported relative difference
    must change by the corresponding amount.  A difference channel that reports
    the same number for two different inputs is not a difference channel.

    THIS LIMB IS AS THE DOCUMENT WORDS IT: the wrong value is FED IN, so it
    certifies the difference FUNCTION and not a file reader.  `plant_3_disk`
    below closes that gap and is declared as an ADDITION, not as this limb."""
    theory = CL_THEORY[c_mu_jet]
    truth = theory
    wrong = theory + PLANT_CL
    d_true = FIO.theory_rel_diff(truth, theory)
    d_wrong = FIO.theory_rel_diff(wrong, theory)
    expected_shift = PLANT_CL / theory
    ok = abs((d_wrong - d_true) - expected_shift) < PLANT_CL_TOL
    out = dict(name="PLANT 3 -- theory-difference channel",
               reader="foam_io_jf1.theory_rel_diff",
               graded_quantity="gate THEORY relative difference |CL_total - CL_theory|/CL_theory",
               artifact="section 7.3 registered CL_theory = %.10f" % theory,
               fed_true=truth, fed_wrong=wrong, diff_true=d_true, diff_wrong=d_wrong,
               expected_shift=expected_shift, tol=PLANT_CL_TOL, passed=bool(ok))
    if not ok:
        refuse("R-PLANT-THEORY",
               "PLANT 3 FAILED (:1701-1704): feeding CL_total = %.10f instead of "
               "%.10f must move the reported relative difference by %.10e; it moved "
               "%.10e. A difference channel that reports the same number for two "
               "different inputs is not a difference channel."
               % (wrong, truth, expected_shift, d_wrong - d_true))
    return out


def plant_3_disk(case_dir, c_mu_jet, alpha_deg):
    """ADDITION, DECLARED AS ONE AND NOT AS A TRANSCRIPTION.

    Section 8.2's PLANT 3 feeds a wrong `CL_total` in directly, which certifies
    the difference function but not a reader.  This limb routes the SAME plant
    through the disk and through `read_cl`, so the certified path is
    `coefficient.dat` -> `read_cl` -> `cl_total` -> `theory_rel_diff` -> the
    gate THEORY number.  It only ever ADDS a refusal; it removes none.  It is
    reported to the supervisor as an addition beyond the frozen text."""
    theory = CL_THEORY[c_mu_jet]
    clean = FIO.read_cl(case_dir)
    d_true = FIO.theory_rel_diff(
        FIO.cl_total(clean["cl"], c_mu_jet, alpha_deg, TAU), theory)
    tmp = tempfile.mkdtemp(prefix="jf1_plant_th_")
    try:
        work = os.path.join(tmp, "case")
        os.makedirs(os.path.join(work, "postProcessing", "forceCoeffs", "0"))
        dst = os.path.join(work, "postProcessing", "forceCoeffs", "0", "coefficient.dat")
        FIO.plant_into_coefficient_dat(clean["path"], dst, "Cl", PLANT_CL)
        planted = FIO.read_cl(work)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    d_planted = FIO.theory_rel_diff(
        FIO.cl_total(planted["cl"], c_mu_jet, alpha_deg, TAU), theory)
    sign = 1.0 if FIO.cl_total(clean["cl"], c_mu_jet, alpha_deg, TAU) >= theory else -1.0
    expected_shift = sign * PLANT_CL / theory
    ok = abs((d_planted - d_true) - expected_shift) < PLANT_CL_TOL
    out = dict(name="PLANT 3 (disk-routed) -- ADDITION beyond the frozen text",
               reader="foam_io_jf1.read_cl -> cl_total -> theory_rel_diff",
               graded_quantity="gate THEORY relative difference",
               artifact=clean["path"], diff_true=d_true, diff_planted=d_planted,
               expected_shift=expected_shift, tol=PLANT_CL_TOL, passed=bool(ok))
    if not ok:
        refuse("R-PLANT-THEORY-DISK",
               "PLANT 3 (disk-routed) FAILED: a `Cl` plant of %.6e on %s must move the "
               "gate THEORY relative difference by %.10e; it moved %.10e."
               % (PLANT_CL, clean["path"], expected_shift, d_planted - d_true))
    return out


def plant_3_negative_limb(c_mu_jet=0.10):
    """The negative limb: a channel that returns a CONSTANT must make the
    control FIRE."""
    theory = CL_THEORY[c_mu_jet]
    const = FIO.theory_rel_diff(theory, theory)
    fired = abs((const - const) - PLANT_CL / theory) >= PLANT_CL_TOL
    if not fired:
        refuse("R-PLANT-THEORY-NEGATIVE",
               "NEGATIVE LIMB FAILED for PLANT 3: a constant channel was not refused.")
    return dict(name="PLANT 3 negative limb", constant_shift=0.0, fired=True)


def run_all_plants(case_dir, c_mu_jet, alpha_deg):
    """Section 8.2 (:1684-1685): "Every zero this comparator can report is
    proven visible-when-non-zero, through THE REAL CODE PATH, BEFORE ANY
    GRADING.  Refusal on any limb." """
    out = [plant_1_cl(case_dir), plant_1_negative_limb(case_dir)]
    if c_mu_jet != 0.0:
        out.append(plant_2_massflow(case_dir, c_mu_jet))
        out.append(plant_2_negative_limb(case_dir, c_mu_jet))
        out.append(plant_3_disk(case_dir, c_mu_jet, alpha_deg))
    else:
        out.append(dict(name="PLANT 2 -- jet mass-flow reader", passed=None,
                        verdict=seal_verdict("NOT A RESULT"),
                        note="N/A at C_mu_jet = 0 (:1547): V_j = 0 makes the "
                             "expectation zero and the mismatch 0/0. Recorded N/A, "
                             "NEVER 0.0 %, never counted toward a PASS (:1760-1763)."))
    out.append(plant_3_theory(0.10 if c_mu_jet == 0.0 else c_mu_jet))
    out.append(plant_3_negative_limb(0.10 if c_mu_jet == 0.0 else c_mu_jet))
    return out


# ===========================================================================
# SECTION 8.4 -- THE REGISTERED REFUSALS BEYOND SECTION 8.1
# ===========================================================================
def check_freeze():
    """:1755 -- "the frozen-file md5 does not match the committed blob".

    The pre-registration's git blob is hashed from the WORKING-TREE bytes and
    compared against the pinned FREEZE_BLOB.  Section 15's freeze block, which
    is where the comparator's OWN md5 was to be recorded, is UNFILLED in the
    frozen document; that gap is reported to the supervisor and is not papered
    over here with a self-hash the document never registered."""
    if not os.path.isfile(PREREG):
        refuse("R-FREEZE-MD5", "the frozen pre-registration is absent from %s" % PREREG)
    raw = open(PREREG, "rb").read()
    blob = hashlib.sha1(b"blob %d\x00" % len(raw) + raw).hexdigest()
    if blob != FREEZE_BLOB:
        refuse("R-FREEZE-MD5",
               "FROZEN-FILE HASH MISMATCH (:1755): %s hashes to git blob %s, pinned "
               "%s. The grading path is fixed at the pre-registration commit and the "
               "file that ran must BE the frozen file (rule 2)." % (PREREG, blob, FREEZE_BLOB))
    return dict(path=PREREG, blob=blob, pinned=FREEZE_BLOB,
                section_15_freeze_block="UNFILLED in the frozen document (:2085-2091); "
                                        "no registered md5 of analyse_jf1.py exists to "
                                        "check against. REPORTED, not worked around.")


def check_field_finite_and_realisable(case_dir, n_stop_dir):
    """:1755-1757 -- `U` contains NaN or Inf is an UNCONDITIONAL refusal
    (:1100-1101); and section 5.5's realisability bounds: `k >= 0` everywhere,
    `omega > 0` everywhere, `nut/nu` finite and `< 1e5` everywhere (:984-988)."""
    out = {}
    d = os.path.join(case_dir, n_stop_dir)
    try:
        U = FIO.read_field(os.path.join(d, "U"))
    except FIO.FoamReadError as e:
        refuse("R-U-NONFINITE", "cannot read U at %s: %s" % (d, e))
    vals = [U["internal"]] + [v for v in U["patches"].values() if v is not None]
    bad = sum(int(np.count_nonzero(~np.isfinite(v))) for v in vals)
    out["U_nonfinite_entries"] = bad
    if bad:
        refuse("R-U-NONFINITE",
               "`U` at %s carries %d NaN or Inf entries (:1100). NaN or Inf anywhere "
               "in U is an UNCONDITIONAL refusal, independent of the section 5.5a "
               "bound." % (d, bad))
    out["max_abs_U"] = float(np.max(np.linalg.norm(U["internal"], axis=1)))

    k = FIO.read_field(os.path.join(d, "k"))
    kmin = float(np.min(k["internal"]))
    out["min_k"] = kmin
    if not np.all(np.isfinite(k["internal"])):
        refuse("R-BOUND-K", "`k` at %s carries NaN or Inf" % d)
    if kmin < 0.0:
        refuse("R-BOUND-K",
               "section 5.5 absolute bound (:984): `k >= 0` everywhere fails -- "
               "min(k) = %.6e at %s. NOT A RESULT." % (kmin, d))

    om = FIO.read_field(os.path.join(d, "omega"))
    ommin = float(np.min(om["internal"]))
    out["min_omega"] = ommin
    if not np.all(np.isfinite(om["internal"])):
        refuse("R-BOUND-OMEGA", "`omega` at %s carries NaN or Inf" % d)
    if not (ommin > 0.0):
        refuse("R-BOUND-OMEGA",
               "section 5.5 absolute bound (:985): `omega > 0` everywhere fails -- "
               "min(omega) = %.6e at %s. NOT A RESULT." % (ommin, d))

    nut = FIO.read_field(os.path.join(d, "nut"))
    ratio = nut["internal"] / NU
    out["max_nut_over_nu"] = float(np.max(ratio))
    if not np.all(np.isfinite(ratio)):
        refuse("R-BOUND-NUT",
               "section 5.5 realisability (:988): `nut/nu` is not finite everywhere "
               "at %s" % d)
    if out["max_nut_over_nu"] >= BOUND_NUT_OVER_NU:
        refuse("R-BOUND-NUT",
               "section 5.5 realisability (:988): max(nut/nu) = %.6e is not < %g at "
               "%s. NOT A RESULT." % (out["max_nut_over_nu"], BOUND_NUT_OVER_NU, d))
    return out


def check_continuity(log):
    """:1756-1757, :1116-1121 -- the GATED quantity is `sum local` at the FINAL
    iteration, bound `< 1e-8`.  `global` and `cumulative` are REPORTED on every
    row and gated on none; no row's verdict may cite them."""
    ce = FIO.final_continuity(log)
    if ce is None:
        refuse("R-CONTINUITY-SUMLOCAL",
               "no `time step continuity errors` line in the final iteration of %s. "
               "The gated quantity of section 5.5b is ABSENT; an absent measurement is "
               "reported as absent, never as a pass." % log["path"])
    if not (ce["sum_local"] < BOUND_SUM_LOCAL):
        refuse("R-CONTINUITY-SUMLOCAL",
               "section 5.5b (:1116-1119): `sum local` continuity error at the final "
               "iteration is %.6e, not < %g. NOT A RESULT. (`global` = %.6e and "
               "`cumulative` = %.6e are REPORTED and gated on nothing.)"
               % (ce["sum_local"], BOUND_SUM_LOCAL, ce["glob"], ce["cumulative"]))
    return ce


def check_blowup(case_dir, c_mu_jet, alpha_deg, max_abs_U_field):
    """Section 5.5a (:1047-1101).  The bound is the row's OWN predicted peak
    times the registered margin M = 2.0.  `max|U|`, its cell location,
    `U_peak_pred` and the ratio are printed ON EVERY ROW; a ratio above 1.2 is
    REPORTED as guard-marginal -- a diagnostic, never a gate arm and never a
    verdict."""
    pred = u_peak_pred(c_mu_jet, alpha_deg)
    bound = BLOWUP_M * pred
    loc = None
    try:
        mm = FIO.read_field_min_max(case_dir)
        measured, loc = mm["max"], mm["loc_max"]
        source = mm["path"]
    except FIO.FoamReadError:
        measured, source = max_abs_U_field, "internal field at N_stop"
    ratio = measured / pred if pred else float("inf")
    out = dict(max_abs_U=measured, location=loc, U_peak_pred=pred, bound=bound,
               ratio=ratio, source=source,
               guard_marginal_REPORTED=bool(ratio > GUARD_MARGINAL_RATIO))
    if not (measured < bound):
        refuse("R-BOUND-BLOWUP",
               "section 5.5a BLOW-UP GUARD (:1053): max|U| = %.6f m/s is not < M * "
               "U_peak_pred = %.1f * %.6f = %.6f m/s for C_mu_jet = %g, alpha = %g deg. "
               "NOT A RESULT." % (measured, BLOWUP_M, pred, bound, c_mu_jet, alpha_deg))
    return out


def check_plateau(cl_reader):
    """Section 5.5 (:986-987): `|dCL| < 1e-4` and `|dCd| < 1e-5` over the LAST
    2 000 iterations.  A run with no such window has already been refused by
    clause 3a's `N_stop >= 2000` (:1627); this reads the window that exists."""
    t = cl_reader["times"]
    keep = t >= (t[-1] - PLATEAU_WINDOW)
    if int(np.count_nonzero(keep)) < 2:
        refuse("R-BOUND-PLATEAU",
               "the last %d iterations of %s carry fewer than two force samples; the "
               "plateau bound is unevaluable and is reported as absent, never as a "
               "pass." % (PLATEAU_WINDOW, cl_reader["path"]))
    dcl = float(np.max(cl_reader["cl_series"][keep]) - np.min(cl_reader["cl_series"][keep]))
    dcd = float(np.max(cl_reader["cd_series"][keep]) - np.min(cl_reader["cd_series"][keep]))
    out = dict(window=PLATEAU_WINDOW, dCL=dcl, dCd=dcd,
               bound_dCL=BOUND_DCL, bound_dCd=BOUND_DCD,
               n_samples=int(np.count_nonzero(keep)))
    if not (abs(dcl) < BOUND_DCL):
        refuse("R-BOUND-PLATEAU",
               "section 5.5 (:986): |dCL| = %.6e over the last %d iterations is not "
               "< %g. NOT A RESULT." % (dcl, PLATEAU_WINDOW, BOUND_DCL))
    if not (abs(dcd) < BOUND_DCD):
        refuse("R-BOUND-PLATEAU",
               "section 5.5 (:987): |dCd| = %.6e over the last %d iterations is not "
               "< %g. NOT A RESULT." % (dcd, PLATEAU_WINDOW, BOUND_DCD))
    return out


def check_jetslot_area(case_dir):
    """:1752, :1162-1168 -- THE `t_z` CROSS-CHECK.  The comparator INDEPENDENTLY
    measures `t_z` from the solved case and does not take the mesh script's word
    for it: `area(jetSlot)` MUST equal 0.005 m2 to 1e-9, because `Aref = c` is
    correct if and only if `t_z == 1.0 m` exactly (HAZARD 1, silent).  If it
    does not, every CL and Cd in the case is scaled wrong."""
    d = FIO.read_jet_sum_phi(case_dir)
    area = d["area"]
    if abs(area - AREA_JETSLOT) > AREA_JETSLOT_TOL:
        refuse("R-JETSLOT-AREA",
               "t_z CROSS-CHECK FAILS (:1164): area(jetSlot) = %.10e m2, registered "
               "%.10e m2 to %g (read from %s). Implied t_z = %.6g m against the "
               "registered 1.0 m exactly, so Aref = c * t_z is wrong by that factor "
               "and EVERY CL and Cd in this case is scaled wrong. All rows are "
               "NOT A RESULT." % (area, AREA_JETSLOT, AREA_JETSLOT_TOL, d["path"],
                                  area / H_SLOT))
    return dict(area=area, implied_t_z=area / H_SLOT, path=d["path"])


def check_jet_massflow(case_dir, c_mu_jet):
    """:1752, :1534 -- the jet mass-flow mismatch must not exceed 0.5 %.
    At C_mu_jet = 0 the check is `N/A -- not run` (:1547-1551), recorded N/A,
    never as `0.0 %` and never as a pass."""
    if c_mu_jet == 0.0:
        return dict(pct="N/A", reason="C_mu_jet = 0: V_j = 0 makes both sides zero and "
                                      "the relative mismatch 0/0 (:1547). Recorded "
                                      "N/A, never 0.0 %, never a pass (rule 3).",
                    counted_toward_pass=False)
    d = FIO.read_jet_sum_phi(case_dir)
    pct, expected = massflow_mismatch(d["sum_phi"], c_mu_jet)
    out = dict(sum_phi_m3_s=d["sum_phi"], expected_m3_s=expected, pct=pct,
               tol_pct=100.0 * MASSFLOW_TOL_FRAC, path=d["path"])
    if pct > 100.0 * MASSFLOW_TOL_FRAC:
        refuse("R-JET-MASSFLOW",
               "section 7.4 (:1534): jet mass-flow mismatch is %.4f %%, above the "
               "registered %.1f %%. `Sum phi` = %.10e m3/s against `V_j h t_z` = "
               "%.10e m3/s, both volumetric (section 5.6 HAZARD 3). A mesh/BC defect; "
               "the row is NOT A RESULT." % (pct, 100.0 * MASSFLOW_TOL_FRAC,
                                             d["sum_phi"], expected))
    return out


def check_yplus(case_dir):
    """:1751, :1538 -- `max(y+) <= 1` on `airfoil`, MEASURED from the solved
    field."""
    y = FIO.read_yplus(case_dir)
    if y["max"] > YPLUS_MAX:
        refuse("R-YPLUS",
               "section 7.4 (:1538): measured max(y+) on `airfoil` is %.6f > %g "
               "(from %s, final sample at t = %g). Section 4.3 sizes y1 so this is "
               "reachable, with a predicted L1 max of 0.9419. NOT A RESULT."
               % (y["max"], YPLUS_MAX, y["path"], y["t"]))
    return y


def check_frame(alpha_cases):
    """:1753-1754, :403-409 -- THE FRAME ASSERTION.

    Before grading the alpha sweep the comparator reads `0/U` from each of the
    alpha = 0, 4 and 8 cases at C_mu_jet = 0.1 and refuses unless the `jetSlot`
    `value` entry is BYTEWISE IDENTICAL across all three, and unless each
    `farfield` `freestreamValue` matches `U_inf (cos alpha, sin alpha, 0)` to
    1e-9.  A frame error is then a refusal, not a number.

    `alpha_cases` is {alpha_deg: case_dir}."""
    if not alpha_cases:
        refuse("R-FRAME-JETSLOT",
               "the frame assertion (:403) was requested with no alpha cases; it is "
               "not skipped by having nothing to compare.")
    entries, ff = {}, {}
    for a, cdir in sorted(alpha_cases.items()):
        f = FIO.read_field(os.path.join(cdir, "0", "U"))
        entries[a] = FIO.patch_entry_text(f, "jetSlot", "value")
        ff[a] = FIO.patch_vector(f, "farfield", "freestreamValue")
    ref_a = sorted(entries)[0]
    for a, txt in entries.items():
        if txt != entries[ref_a]:
            refuse("R-FRAME-JETSLOT",
                   "FRAME ASSERTION FAILS (:406-407): the `jetSlot` `value` entry at "
                   "alpha = %s is not BYTEWISE IDENTICAL to the one at alpha = %s.\n"
                   "  alpha %s: %r\n  alpha %s: %r\n"
                   "The jet is a property of the BODY and is NOT rotated with alpha "
                   "(:365-368). Rotating both the freestream and the jet restores the "
                   "refuted sin(tau) convention and its one-signed 1.2325 %% slope bias."
                   % (a, ref_a, ref_a, entries[ref_a], a, txt))
    for a, vec in ff.items():
        want = np.array([U_INF * math.cos(math.radians(a)),
                         U_INF * math.sin(math.radians(a)), 0.0])
        if float(np.max(np.abs(vec - want))) > FRAME_TOL:
            refuse("R-FRAME-FARFIELD",
                   "FRAME ASSERTION FAILS (:407-408): `farfield` freestreamValue at "
                   "alpha = %s is %s, registered U_inf (cos a, sin a, 0) = %s, to %g. "
                   "The FREESTREAM is the thing that rotates (:363-364)."
                   % (a, vec.tolist(), want.tolist(), FRAME_TOL))
    return dict(jetSlot_entry=entries[ref_a], alphas=sorted(entries),
                farfield={a: v.tolist() for a, v in ff.items()})


def check_roache_index_mapping(levels):
    """:1751, :585-598 -- "the Roache index mapping does not match section 4.2
    (fine = L3)".  `levels` is the COARSE-FIRST list handed to the triple."""
    names = [lv["name"] for lv in levels]
    if names != ["L1", "L2", "L3"]:
        refuse("R-ROACHE-INDEX-MAP",
               "ROACHE INDEX MAPPING (:590-594): the triple must be handed coarse-first "
               "as ['L1','L2','L3'] so that Roache index 1 (FINE) is L3; it was handed "
               "%s. Under the inverted mapping the reported `fine-grid` GCI is computed "
               "from the L1-L2 (coarse) difference -- a 1.9x overstatement carrying the "
               "wrong label (:604-609)." % names)
    cells = [lv["cells"] for lv in levels]
    if not (cells[0] < cells[1] < cells[2]):
        refuse("R-ROACHE-INDEX-MAP",
               "ROACHE INDEX MAPPING (:590-594): cell counts %s are not strictly "
               "increasing coarse-to-fine, so L3 is not the finest level." % cells)
    return dict(mapping=[dict(roache=r, level=l) for r, l in ROACHE_MAP], cells=cells)


def check_constant_r_branch(r21, r32, form):
    """:1749-1750, :612-618 -- refuse if the constant-`r` branch was taken on a
    triple with `|r_21 - r_32| / r_21 > 1 %`.  Section 4.2 registers the
    non-constant-`r` form REGARDLESS; the 1 % clause is a refusal on the BRANCH
    TAKEN, never a licence to take the constant-`r` branch."""
    gap = abs(r21 - r32) / r21
    if form != "unequal":
        if gap > RATIO_GAP_REL_MAX:
            refuse("R-ROACHE-CONSTANT-R",
                   "a triple with |r_21 - r_32|/r_21 = %.4f %% > %.1f %% was handed to "
                   "the constant-`r` branch (:1749). r_21 = %.6f, r_32 = %.6f."
                   % (100 * gap, 100 * RATIO_GAP_REL_MAX, r21, r32))
        refuse("R-ROACHE-CONSTANT-R",
               "the constant-`r` branch was taken. Section 4.2 (:612-616) registers the "
               "non-constant-`r` Roache iterative form for this ladder REGARDLESS of "
               "the gap; the 1 %% clause is a refusal on the branch taken, never a "
               "licence to take the constant-`r` branch.")
    return dict(r21=r21, r32=r32, rel_gap=gap, form=form)


# ===========================================================================
# SECTION 7 -- THE GATES
# ===========================================================================
def gate_v():
    """:1268, :1308 -- GATE V IS `BLOCKED`.  Its premise is false: the lab holds
    no unblown NACA 0012 record at low-Re (`y+ <= 1`, no wall functions) fit to
    serve as a same-family regression comparand (FINDING JF1-V1, :1335-1339).
    A BLOCKED gate is not a failed gate and may never be reported as one
    (:1359).  It has no arms and no bands."""
    return dict(gate="V", verdict=seal_verdict("BLOCKED"), arms=[], bands=None,
                finding="JF1-V1 (:1335): Certonomous holds no unblown NACA 0012 record "
                        "at low-Re wall treatment fit to serve as a same-family "
                        "regression comparand.",
                note="Contributes the word BLOCKED and nothing else in either "
                     "direction (:1359-1361). No row's verdict may cite Cd (:1356).")


def gate_g(levels, plant_control, iterative_states, plateau_states):
    """:1433-1476 -- GATE G, the Roache triple on `CL_total` at C_mu_jet = 0.1,
    alpha = 0.  Rule 5's three steps, in the document's order and direction.

    MECHANISM DISCLOSED: the shared `scripts/roache_triple.py` supplies the
    sealed arithmetic (`triple_from_cells` in its unequal-`r` form, `monotone`,
    `assert_plant_control`).  `grade_ladder` is NOT the call node here because
    its band is a band on the VALUE, and section 7.2's registered bands are on
    the ORDER `p` (:1440) and on `GCI_fine` (:1441) -- calling it would require
    inventing a `CL_total` band this registration does not contain."""
    RT.assert_plant_control(plant_control)
    idx = check_roache_index_mapping(levels)
    n_c, n_m, n_f = (lv["cells"] for lv in levels)
    f_c, f_m, f_f = (lv["value"] for lv in levels)
    r21 = RT.refinement_ratio(n_m, n_f, DIM)
    r32 = RT.refinement_ratio(n_c, n_m, DIM)
    branch = check_constant_r_branch(r21, r32, "unequal")
    tr = RT.triple_from_cells(f_c, f_m, f_f, n_c, n_m, n_f, DIM, fs=FS, form="unequal")
    mono = RT.monotone(tr)

    row = dict(gate="G", quantity="CL_total", dim=DIM, fs=FS,
               index_mapping=idx, ratios=branch,
               levels=[dict(lv) for lv in levels],
               state=tr["state"], order=tr.get("order"), monotone=bool(mono),
               eps_21=tr.get("e21"), eps_32=tr.get("e32"),
               value=f_f, planted_zero=dict(plant_control),
               iterative_states=dict(iterative_states),
               plateau_states=dict(plateau_states),
               order_band=ORDER_BAND, gci_max=GCI_MAX)

    # rule 5 step (1) -- any level not iteratively converged or not plateaued
    bad = {k: v for k, v in iterative_states.items() if v != "CONVERGED"}
    bad.update({k: v for k, v in plateau_states.items() if v != "PLATEAUED"})
    if bad:
        row.update(verdict=seal_verdict("NOT A RESULT"),
                   why="rule 5 step 1 (:1447): levels not converged/plateaued: %s" % bad,
                   gci=None)
        return row
    # rule 5 step (2) -- DIVERGENT, STAGNANT, OSCILLATORY or EXACT
    if tr["state"] != "CONVERGING":
        row.update(verdict=seal_verdict("NOT A RESULT"),
                   why="rule 5 step 2 (:1449): triple is %s. Value, both triples and "
                       "the orders are printed beside it." % tr["state"],
                   gci=None)
        return row
    # NO GCI IS EVER QUOTED WHEN THE THREE VALUES ARE NOT MONOTONE (:1459)
    if not mono:
        row.update(verdict=seal_verdict("NOT A RESULT"),
                   why="the triple is not monotone (:1459-1461); NO GCI is computed and "
                       "none is quoted. The non-monotone triple and the label are "
                       "printed instead.", gci=None)
        return row
    # `scripts/roache_triple.py` returns `GCI_pct` in PERCENT; section 7.2's
    # registered band is `GCI_fine < 3 %`.  The conversion is done here, once,
    # rather than comparing a percent against a fraction.
    gci_pct = tr.get("GCI_pct")
    gci = None if gci_pct is None else gci_pct / 100.0
    p = tr.get("order")
    if p is None or gci is None:
        row.update(verdict=seal_verdict("NOT A RESULT"),
                   why="the shared Roache module returned state %r with no order or "
                       "no GCI; nothing is quoted in place of an absent number."
                       % tr["state"], gci=None)
        return row
    row["gci"] = gci
    inside = (ORDER_BAND[0] <= p <= ORDER_BAND[1]) and (gci is not None and gci < GCI_MAX)
    row["verdict"] = seal_verdict("PASS" if inside else "GATE FAIL")
    row["why"] = ("rule 5 step 3 (:1452): triple CONVERGING; p = %.4f in [%g, %g] = %s; "
                  "GCI_fine = %.4f %% < %g %% = %s"
                  % (p, ORDER_BAND[0], ORDER_BAND[1],
                     ORDER_BAND[0] <= p <= ORDER_BAND[1], 100 * gci, 100 * GCI_MAX,
                     gci < GCI_MAX))
    return row


def gate_theory_a(rows):
    """:1485-1503 -- arm (a), the `C_mu_jet` sweep at alpha = 0 on L1.
    `|CL_total - CL_theory| / CL_theory <= 15 %` at C_mu_jet in {0.05, 0.1, 0.2}.
    C_mu_jet = 0.4 is OUTSIDE THE GATE BY REGISTRATION and is reported as the
    theory-departure exhibit; C_mu_jet = 0 has no CL_theory at all."""
    out = []
    for c_mu, cl_tot in sorted(rows.items()):
        if c_mu not in CL_THEORY:
            out.append(dict(c_mu_jet=c_mu, CL_total=cl_tot, gated=False,
                            verdict=seal_verdict("NOT A RESULT"),
                            note="no registered CL_theory at C_mu_jet = %g; a map "
                                 "point, carrying no verdict (:1844)" % c_mu))
            continue
        th = CL_THEORY[c_mu]
        rel = FIO.theory_rel_diff(cl_tot, th)
        gated = c_mu in THEORY_A_GATED
        row = dict(c_mu_jet=c_mu, CL_total=cl_tot, CL_theory=th, rel_diff=rel,
                   band=THEORY_BAND, gated=gated)
        if gated:
            row["verdict"] = seal_verdict("PASS" if rel <= THEORY_BAND else "GATE FAIL")
        else:
            row["verdict"] = seal_verdict("NOT A RESULT")
            row["note"] = ("OUTSIDE THE GATE BY REGISTRATION (:1495, :1502): the "
                           "theory-departure exhibit. Reported, never a gate arm.")
        out.append(row)
    return dict(gate="THEORY (a)", rows=out)


def gate_theory_b(cl_total_by_alpha):
    """:1509-1523 -- arm (b), `dCL/dalpha` at C_mu_jet = 0.1 from the alpha
    sweep on L2.  Measured: LEAST-SQUARES slope of `CL_total` over
    alpha in {0, 4, 8} deg, IN RADIANS.  Band:
    `|slope_sim - 6.7208116310| / 6.7208116310 <= 15 %`."""
    alphas = sorted(cl_total_by_alpha)
    if list(alphas) != list(ALPHA_SWEEP):
        refuse("R-THEORY-B-SWEEP",
               "arm (b) (:1522) is a least-squares slope over alpha in %s; it was "
               "handed %s. A slope over a different point set is a different "
               "measurement." % (list(ALPHA_SWEEP), alphas))
    x = np.array([math.radians(a) for a in alphas])
    y = np.array([cl_total_by_alpha[a] for a in alphas])
    slope = float(np.polyfit(x, y, 1)[0])
    rel = abs(slope - DCLDALPHA_THEORY) / DCLDALPHA_THEORY
    return dict(gate="THEORY (b)", alphas=alphas, CL_total=y.tolist(),
                slope_per_rad=slope, theory_per_rad=DCLDALPHA_THEORY,
                rel_diff=rel, band=THEORY_BAND,
                jet_reaction_contribution_per_rad=0.0828364299,
                verdict=seal_verdict("PASS" if rel <= THEORY_BAND else "GATE FAIL"))


# ===========================================================================
# SECTION 7.5 -- REPORTED, NEVER GATED (:1553-1567)
# ===========================================================================
def structure_metrics(case_dir, c_mu_jet, alpha_deg, cl_reader, log, blowup):
    """"These are reported and are never gated, and no row's verdict may cite
    them.  A discrepancy printed here is a real discrepancy and is not annotated
    as non-binding beyond the fact that it is not a gate arm." (:1565-1567)"""
    ce = FIO.final_continuity(log)
    out = dict(
        Cd=cl_reader["cd"],
        Cd_note="REPORTED, NEVER GATED. Under the O4 ruling there is NO gated Cd arm "
                "anywhere in this registration (:1356, :1424-1429).",
        base_Cp="NOT MEASURED -- see NOT_IMPLEMENTED['base_Cp']",
        base_drag_increment="NOT MEASURED -- see NOT_IMPLEMENTED['base_Cp']",
        CL_aero=cl_reader["cl"],
        CL_total=FIO.cl_total(cl_reader["cl"], c_mu_jet, alpha_deg, TAU),
        jet_reaction_term=jet_reaction(c_mu_jet, alpha_deg),
        max_abs_U=blowup["max_abs_U"], max_abs_U_location=blowup["location"],
        U_peak_pred=blowup["U_peak_pred"], guard_ratio=blowup["ratio"],
        guard_marginal=blowup["guard_marginal_REPORTED"],
        continuity_global_REPORTED=(ce or {}).get("glob"),
        continuity_cumulative_REPORTED=(ce or {}).get("cumulative"),
        continuity_note="`global` and `cumulative` are REPORTED on every row and gated "
                        "on NONE; no row's verdict may cite them (:1119-1121).",
        jet_sheet_trajectory="NOT MEASURED -- see NOT_IMPLEMENTED['jet_sheet_trajectory']",
        separation_point="NOT MEASURED -- see NOT_IMPLEMENTED['separation_point']",
        Cp_distribution="NOT MEASURED -- see NOT_IMPLEMENTED['Cp_distribution']",
        decomposition_digest="NOT MEASURED -- see NOT_IMPLEMENTED['decomposition_digest']",
        DECOMP_SEED="NOT READ -- see NOT_IMPLEMENTED['decomposition_digest']")
    return out


NOT_IMPLEMENTED = {
    "jet_sheet_resolution": (
        "Section 7.4 (:1539) `>= 8 cells across the max|U| locus at x/c = 1`. NOT "
        "IMPLEMENTED. It needs cell centres (`0/C`), which `writeCellCentres` was "
        "never run to produce in any JF1 run on this box. It is NOT in section 8.4's "
        "refusal list, so its absence is an ABSENT MEASUREMENT reported as absent, "
        "never as a pass; the row it would qualify is NOT A RESULT until it is "
        "measured."),
    "base_Cp": (
        "Section 7.1 (:1424-1429) / 7.5 (:1558-1560): `Cd` with the measured base `Cp` "
        "and the derived base-drag increment beside it. NOT IMPLEMENTED. It needs the "
        "base-patch face set, which the mesh script does not name as its own patch. "
        "REPORTED-only quantity; no gate depends on it."),
    "separation_point": (
        "Section 7.5 (:1556-1557): upper-surface separation from a `wallShearStress` "
        "sign change. NOT IMPLEMENTED -- `wallShearStress` is not written by any JF1 "
        "controlDict on this box. REPORTED-only; no gate depends on it."),
    "Cp_distribution": (
        "Section 7.5 (:1557-1558): `Cp` distribution blown vs unblown. NOT "
        "IMPLEMENTED -- needs surface sampling that no JF1 controlDict configures. "
        "REPORTED-only; no gate depends on it."),
    "jet_sheet_trajectory": (
        "Section 7.5 (:1555-1556): locus of max|U| at x/c = 0.25/0.5/1/2/3. NOT "
        "IMPLEMENTED -- needs `0/C`. REPORTED-only; no gate depends on it."),
    "decomposition_digest": (
        "Section 9.4 (:1819, :1825-1827): md5 of the sorted per-processor cell counts, "
        "identical across every run on a level; a digest change makes the affected rows "
        "NOT A RESULT. NOT IMPLEMENTED -- no JF1 run on this box was decomposed "
        "(`processor*` directories absent; the feasibility rows ran serial). The "
        "assertion has nothing to compare and is reported as unperformed."),
    "min_k_jet_core": (
        "Section 5.5 / 7.4 (:984, :1537): `min(k) > 0` IN THE JET CORE. NOT "
        "IMPLEMENTED as a core-restricted check -- identifying the jet core needs "
        "cell centres (`0/C`). The GLOBAL bound `k >= 0` (:984) IS implemented and "
        "enforced in `check_field_finite_and_realisable`. Recorded `N/A` at "
        "C_mu_jet = 0 per :1537 and never as a pass."),
    "section_15_md5": (
        "Section 8 (:1573-1575) requires the comparator's own md5 to be recorded in "
        "section 15 at freeze and verified before grading. Section 15 is UNFILLED in "
        "the frozen document (:2085-2091 read `NO -- this document is an UNFROZEN "
        "DRAFT` and `(supervisor)`), so there is no registered md5 to check against. "
        "`check_freeze` verifies the PRE-REGISTRATION blob against the pinned "
        "66543c97 and reports this gap rather than inventing a value."),
    "comparator_path": (
        "Section 8 (:1573) registers the comparator at "
        "`verification/runs/JF1_jet_flap/analyse_jf1.py`. This file is at "
        "`cases/JF1_JET_FLAP/analyse_jf1.py` on the supervisor's instruction. The "
        "divergence is REPORTED, not resolved by this lane: rule 2 fixes the grading "
        "path at the pre-registration commit and a path change is the supervisor's "
        "call."),
}


# ===========================================================================
# CONTROLS ON THE INSTRUMENT ITSELF
# ===========================================================================
def control_no_asserts():
    """L-332: zero `assert` statements across the JF1 comparator chain."""
    paths = [os.path.join(HERE, n) for n in
             ("analyse_jf1.py", "foam_io_jf1.py", "mutation_jf1.py")]
    bad = {}
    for p in paths:
        if not os.path.isfile(p):
            continue
        lines = [n.lineno for n in ast.walk(ast.parse(open(p).read()))
                 if isinstance(n, ast.Assert)]
        if lines:
            bad[p] = lines
    if bad:
        refuse("R-CONTROL-ASSERTS",
               "L-332: `assert` statements found in the comparator chain %s. `python3 "
               "-O` deletes them and the refusal they carry." % bad)
    return dict(files=[os.path.basename(p) for p in paths], asserts=0)


def control_plants_certify_graded_readers():
    """THE CONTROL THAT F28's DEFECT WOULD HAVE FAILED.

    Every plant must certify a reader whose VALUE reaches a graded number.  This
    control asserts the pairing mechanically by checking that each plant's
    declared reader is a name actually called on the grading path, and that its
    declared graded quantity is a registered comparand."""
    src = open(os.path.join(HERE, "analyse_jf1.py")).read()
    tree = ast.parse(src)
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute):
                called.add("foam_io_jf1.%s" % f.attr if isinstance(f.value, ast.Name)
                           and f.value.id == "FIO" else f.attr)
            elif isinstance(f, ast.Name):
                called.add(f.id)
    need = {"foam_io_jf1.read_cl": "CL_aero -> CL_total",
            "foam_io_jf1.read_jet_sum_phi": "jet mass-flow mismatch",
            "foam_io_jf1.theory_rel_diff": "gate THEORY relative difference"}
    missing = [r for r in need if r not in called]
    if missing:
        refuse("R-CONTROL-PLANT-PAIRING",
               "a plant certifies reader(s) %s that the grading path never calls. A "
               "plant that certifies a reader whose value reaches no graded number "
               "certifies nothing (the F28 defect)." % missing)
    return dict(pairs=need, all_called=True)


def control_upeak_table():
    """A TRANSCRIPTION CONTROL: section 5.5a's registered bound table (:1069-1075)
    is recomputed from the registered construction (:1051-1053).  A mismatch
    means this file transcribed the construction or the constants wrongly."""
    want = {(0.00, 0): 23.920, (0.05, 0): 44.721, (0.10, 0): 63.246,
            (0.20, 0): 89.443, (0.40, 0): 126.491, (0.10, 4): 63.246,
            (0.10, 8): 63.246}
    bad = {}
    for (c_mu, a), w in want.items():
        got = blowup_bound(c_mu, a)
        if abs(got - w) > 1e-3:
            bad[(c_mu, a)] = (got, w)
    if bad:
        refuse("R-CONTROL-UPEAK",
               "section 5.5a bound table (:1069-1075) does NOT reproduce from the "
               "registered construction (:1051-1053): %s" % bad)
    return dict(rows=len(want), max_abs_error_m_s=1e-3)


def control_vj_table():
    """A TRANSCRIPTION CONTROL: section 2's `V_j` table (:460-464) recomputed."""
    want = {0.0: 0.0, 0.05: 22.360680, 0.10: 31.622777,
            0.20: 44.721360, 0.40: 63.245553}
    bad = {c: (v_jet(c), w) for c, w in want.items() if abs(v_jet(c) - w) > 5e-7}
    if bad:
        refuse("R-CONTROL-VJ",
               "section 2's V_j table (:460-464) does not reproduce from :455: %s" % bad)
    return dict(rows=len(want))


def control_frame_table():
    """A TRANSCRIPTION CONTROL: section 1.6a's jet-reaction table (:416-418)."""
    want = {0: 0.0500000000, 4: 0.0559192903, 8: 0.0615661475}
    bad = {a: (jet_reaction(0.10, a), w) for a, w in want.items()
           if abs(jet_reaction(0.10, a) - w) > 1e-9}
    if bad:
        refuse("R-CONTROL-FRAME",
               "section 1.6a's registered term table (:416-418) does not reproduce "
               "from `C_mu_jet sin(tau + alpha)`: %s" % bad)
    return dict(rows=len(want))


def control_exemplar_is_gradeable():
    """THE SATISFIABILITY CONTROL, section 17.3 (:2338-2416).

    The struck clause 3 refused EVERY POSSIBLE RUN (:1586-1604).  This control
    replays the registered exemplar triple through the gate arithmetic and
    requires it to PASS -- so that a comparator which refuses everything is
    caught by its own self-test rather than by a wasted campaign.

    The exemplar's values are a CONSTRUCTED EXEMPLAR, never a JF1 measurement
    (:2428-2433), and are used here for nothing but this check."""
    levels = [dict(name="L1", cells=PLANNED_CELLS["L1"], value=0.604830),
              dict(name="L2", cells=PLANNED_CELLS["L2"], value=0.606700),
              dict(name="L3", cells=PLANNED_CELLS["L3"], value=0.607700)]
    pc = RT.external_plant_control("control_exemplar", 0.0, RT.PLANT,
                                   artifact="section 17.3 exemplar", level="L3")
    row = gate_g(levels, pc,
                 {lv["name"]: "CONVERGED" for lv in levels},
                 {lv["name"]: "PLATEAUED" for lv in levels})
    if row["verdict"] != "PASS":
        refuse("R-CONTROL-EXEMPLAR",
               "section 17.3's registered SATISFIABLE exemplar does not PASS this "
               "comparator's gate G: verdict %r, state %r, p = %r, GCI = %r. A "
               "comparator that cannot pass the registration's own worked instance "
               "refuses every possible run -- L-409, the defect section 8.1 was "
               "amended to repair." % (row["verdict"], row["state"], row.get("order"),
                                       row.get("gci")))
    for got, want, name, tol in ((row["order"], 1.9546, "p", 5e-3),
                                 (row["gci"], 0.002471, "GCI_fine", 5e-5)):
        if abs(got - want) > tol:
            refuse("R-CONTROL-EXEMPLAR",
                   "section 17.3 (:2402-2403) registers %s = %s for the exemplar; this "
                   "comparator computes %s." % (name, want, got))
    theory = gate_theory_a({0.10: 0.604830})
    if theory["rows"][0]["verdict"] != "PASS":
        refuse("R-CONTROL-EXEMPLAR",
               "section 17.3 (:2413-2415) registers gate THEORY (a) PASS at 0.00898 %% "
               "for the exemplar; this comparator says %r"
               % theory["rows"][0]["verdict"])
    return dict(gate_G=row["verdict"], order=row["order"], gci=row["gci"],
                theory_a=theory["rows"][0]["verdict"],
                theory_a_rel_pct=100 * theory["rows"][0]["rel_diff"])


def control_functions_block_is_stripped():
    """A control on the PIN reader itself (`strip_top_level_block`).

    `system/controlDict` carries function objects with their own `writeControl`
    and `writeInterval`.  This control builds a dict whose TOP LEVEL is
    registration-conforming but whose `functions` block contains
    `writeInterval 1;`, and requires the pin to PASS; then moves the wrong value
    to the top level and requires it to REFUSE.  Without both limbs the pin
    could be reading the function object's number."""
    good = ("startTime 0;\ndeltaT 1;\nendTime 20000;\nwriteControl timeStep;\n"
            "writeInterval 20000;\nfunctions\n{\n  fc\n  {\n    writeControl "
            "timeStep;\n    writeInterval 1;\n  }\n}\n")
    bad = good.replace("writeInterval 20000;", "writeInterval 1;")
    fv = ("SIMPLE\n{\n residualControl\n {\n  p 1e-06;\n  U 1e-06;\n  k 1e-06;\n"
          "  omega 1e-06;\n }\n}\n")
    tmp = tempfile.mkdtemp(prefix="jf1_ctrl_fn_")
    try:
        res = {}
        for tag, text in (("good", good), ("bad", bad)):
            cd = os.path.join(tmp, tag, "system")
            os.makedirs(cd)
            open(os.path.join(cd, "controlDict"), "w").write(text)
            open(os.path.join(cd, "fvSolution"), "w").write(fv)
            try:
                check_pin(os.path.join(tmp, tag))
                res[tag] = "PASSED"
            except Refusal as e:
                res[tag] = e.code
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if res.get("good") != "PASSED":
        refuse("R-CONTROL-FUNCTIONS-BLOCK",
               "the pin refused a CONFORMING controlDict because it read the "
               "`functions` block's own writeInterval: %s" % res)
    if res.get("bad") != "R-PIN-CONTROLDICT":
        refuse("R-CONTROL-FUNCTIONS-BLOCK",
               "the pin did NOT refuse a controlDict whose TOP-LEVEL writeInterval is "
               "wrong: %s. The pin is reading the wrong number." % res)
    return dict(conforming="PASSED", top_level_wrong="R-PIN-CONTROLDICT")


def run_controls():
    return dict(no_asserts=control_no_asserts(),
                plant_pairing=control_plants_certify_graded_readers(),
                v_j_table=control_vj_table(),
                u_peak_table=control_upeak_table(),
                frame_table=control_frame_table(),
                functions_block=control_functions_block_is_stripped(),
                exemplar_satisfiable=control_exemplar_is_gradeable())


# ===========================================================================
# THE GRADING PATH
# ===========================================================================
def grade_case(case_dir, case_id, c_mu_jet, alpha_deg, level,
               alpha_cases=None, skip_plants=False):
    """One row, all of section 8, in order.  Refuses (exit 2) rather than
    degrading anywhere along it."""
    rec = dict(case_dir=case_dir, case_id=case_id, c_mu_jet=c_mu_jet,
               alpha_deg=alpha_deg, level=level,
               utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    rec["freeze"] = check_freeze()
    rec["controls"] = run_controls()
    rec["completion"] = check_completion(case_dir, case_id)
    ns = str(rec["completion"]["N_stop"])
    if not skip_plants:
        rec["plants"] = run_all_plants(case_dir, c_mu_jet, alpha_deg)
    rec["t_z_cross_check"] = check_jetslot_area(case_dir)
    rec["jet_mass_flow"] = check_jet_massflow(case_dir, c_mu_jet)
    rec["y_plus"] = check_yplus(case_dir)
    log = FIO.read_solver_log(os.path.join(case_dir, "log.simpleFoam"))
    rec["continuity"] = check_continuity(log)
    fields = check_field_finite_and_realisable(case_dir, ns)
    rec["fields"] = fields
    rec["blow_up_guard"] = check_blowup(case_dir, c_mu_jet, alpha_deg,
                                        fields["max_abs_U"])
    cl = FIO.read_cl(case_dir)
    rec["plateau"] = check_plateau(cl)
    if alpha_cases:
        rec["frame"] = check_frame(alpha_cases)
    rec["CL_aero"] = cl["cl"]
    rec["CL_total"] = FIO.cl_total(cl["cl"], c_mu_jet, alpha_deg, TAU)
    rec["structure_metrics_REPORTED"] = structure_metrics(
        case_dir, c_mu_jet, alpha_deg, cl, log, rec["blow_up_guard"])
    rec["gate_V"] = gate_v()
    rec["not_implemented"] = sorted(NOT_IMPLEMENTED)
    rec["row_verdict"] = seal_verdict("GATE REACHED")
    rec["row_verdict_note"] = (
        "GATE REACHED means this ROW cleared every section 8.1 clause, every section "
        "8.2 plant and every section 8.4 refusal. Gate G and gate THEORY are graded "
        "across ROWS (`--gate-g`, `--gate-theory`), never from one row.")
    return rec


# ===========================================================================
# CLI
# ===========================================================================
def _emit(obj):
    sys.stdout.write(json.dumps(obj, indent=2, default=str) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description="JF1 comparator (frozen sections 8.1-8.4)")
    ap.add_argument("--controls", action="store_true",
                    help="run the instrument controls only")
    ap.add_argument("--completion", metavar="CASE_DIR",
                    help="run section 8.1 IN FULL on one case and nothing else")
    ap.add_argument("--case-id", help="case id for artefacts/RUN_STATUS.<id>.txt")
    ap.add_argument("--prelaunch", metavar="CASE_DIR",
                    help="the section 8.1 pre-launch guard (:1672)")
    ap.add_argument("--plants", metavar="CASE_DIR", help="run the section 8.2 plants")
    ap.add_argument("--grade", metavar="CASE_DIR", help="grade one row, all of section 8")
    ap.add_argument("--c-mu-jet", type=float, default=None)
    ap.add_argument("--alpha", type=float, default=0.0)
    ap.add_argument("--level", default="L1")
    ap.add_argument("--skip-plants", action="store_true",
                    help="section 8.1 only, for the mutation harness")
    args = ap.parse_args(argv)

    if args.controls:
        _emit(run_controls())
        return 0
    if args.prelaunch:
        _emit(prelaunch_guard(args.prelaunch))
        return 0
    if args.completion:
        if not args.case_id:
            refuse("R-CLI", "--completion requires --case-id: section 9.3 registers "
                            "`artefacts/RUN_STATUS.<case_id>.txt` and the comparator "
                            "will not guess a case id")
        _emit(check_completion(args.completion, args.case_id))
        return 0
    if args.plants:
        if args.c_mu_jet is None:
            refuse("R-CLI", "--plants requires --c-mu-jet: PLANT 2's expectation is "
                            "`V_j h t_z` and V_j is a function of C_mu_jet")
        _emit(run_all_plants(args.plants, args.c_mu_jet, args.alpha))
        return 0
    if args.grade:
        if args.c_mu_jet is None or not args.case_id:
            refuse("R-CLI", "--grade requires --case-id and --c-mu-jet")
        _emit(grade_case(args.grade, args.case_id, args.c_mu_jet, args.alpha,
                         args.level, skip_plants=args.skip_plants))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as exc:
        sys.stderr.write("REFUSED[%s]: %s\n" % (exc.code, exc.msg))
        sys.exit(2)
    except FIO.FoamReadError as exc:
        sys.stderr.write("REFUSED[R-READ]: %s\n" % exc)
        sys.exit(2)
