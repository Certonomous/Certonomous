#!/usr/bin/env python3
# ===========================================================================
# d6r2c_fm12_grade.py -- THE FM12 GRADER: G1, G2, D1, D2, M0, M1, W1, Q1, H4
# ===========================================================================
#
# Registered by PREREGISTRATION_FM12_MATCHED_LIFT.md sections 3, 5, 6 and 7, and
# IN THE SAME COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS (rule 2).
#
# THIS FILE GRADES.  IT PRODUCES NO PHYSICS.  It recomputes the weighted drag
# from the per-condition CD and the frozen weights rather than trusting any J
# a producer wrote, and it re-measures the mesh gate and the wall gate FROM THE
# RUN DIRECTORY rather than believing the producer's own record of them.
#
# THE THREE CLAUSES OF DAFOAM_CHARTER.md sec 22.4, AND WHERE EACH IS ANSWERED:
#   (1) every instrument named in the frozen table EXISTS at its stated md5 --
#       answered by d6r2c_fm12_prefreeze.sh, which hashes the table's own rows.
#   (2) the pre-freeze check drives THE CLI THE LAUNCHER EMITS -- answered by
#       the same script, which asks d6r2c_fm12_run_arm.sh --emit-grade-cmd for
#       the EXACT string and runs it against a synthetic arm.  A --selftest
#       green against the graded FUNCTION proves the function; the FM9 grader's
#       frozen command line could only ever return NOT A RESULT and its selftest
#       never saw it (L-595, L-570).  main() below is therefore reachable from
#       the check, and --item accepts EVERY arm id this document registers so
#       that a re-run id cannot fall through argparse as FM10's did.
#   (3) every channel a gate reads has a writer that ran.  primal_residual.json
#       HAD FOUR READERS, ZERO WRITERS AND ZERO SUCH FILES ON DISK, and the
#       default conv[p] = True stood for every condition.  IT IS DELETED.  H4's
#       convergence limb reads the ARM LOG, whose writer is the solver itself
#       and whose lines are countable -- and the limb REFUSES on a log that
#       carries no primal block at all, so an absent writer cannot pass as a
#       silent zero (rule 3).
# ===========================================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys

# ---------------------------------------------------------------------------
# THE FROZEN INPUTS.  Paths and hashes, all inherited, none chosen here.
# ---------------------------------------------------------------------------
PARENT_BASE = ("/home/ubuntu/certonomous-runs/"
               "CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable")
FM10_RECORD_DEFAULT = ("/home/ubuntu/certonomous-runs/"
                       "CURRICULUM-D6R2C-FM9-a2-wing-freshmesh-arrives/FM10/"
                       "d6r2c_freshmesh.json")
EVALS_DEFAULT = os.path.join(PARENT_BASE, "O_mp", "d6r2c_evals.jsonl")
EVALS_MD5 = "2c0b8143caad198cd2e21d8047986aa3"
RUNSCRIPT_MD5 = "2f2ae43a627146cf8e0f065b035ada4b"
BASE_POINTS_MD5 = "0fb1935a9b8781b73ac4ccb136e3ec68"
GENWINGMESH_MD5 = "dab5e959187ab2e2bfb4e2c0ded0feb6"

POINTS = ["cl04", "cl05", "cl06"]
WEIGHTS = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}    # PREREGISTRATION.md sec 1
CL_TARGETS = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}    # PREREGISTRATION.md sec 1
RUN_DIRS = ("mp04", "mp05", "mp06")
N_PROCESSORS = 4
SUB_ARMS = ("Zb", "Zo")
STATE_OF = {"Zb": "Zb", "Zo": "Zo"}
RECORD = "d6r2c_fm12.jsonl"

# The F-record indices the two inherited weighted drags come from: n = 2 is the
# optimiser's first feasible design (J0) and n = 88 its final one (Jf).
N_J0, N_JF = 2, 88
FINAL_RECORD_N = 88

# ---- THE DECLARED CONSTANTS.  Each one says whether it is DECLARED or DERIVED,
# ---- and every DERIVED one is derived below, in this invocation, from a
# ---- quantity read at run time -- and THE DERIVED VALUE IS THE VALUE USED.
CL_FINDING_TRIGGER = 5.0e-3      # AFTER_ITEM9_R2 sec 3c, "five times the G3 tolerance"
G3_MULTIPLE = 5.0                # ... so TRIM_TOL = CL_FINDING_TRIGGER / G3_MULTIPLE
BAND_FRACTION_OF_J0 = 0.01       # FM_BAND_ABS is "0.01 x J0" -- AFTER_ITEMS sec 2d
SETTLE_MARGIN = 1000.0           # DECLARED: the settle criterion is this many times
                                 # tighter than the decision band's relative size
DOUBLE_SPLIT = 0.50              # DECLARED split of a measured interval, sec 3 D1
PLANT = 1.234e-03                # rule 3

# ---- THE COST, AND ITS ANCHORS.  Each term names the run it came from; not one
# ---- of them is a figure this arm produced.  Derived here, used here.
#   per objective evaluation (3 conditions, cold): DEC7 state O, 81.7 s at 4 ranks
#   per gradient evaluation:  O_mp, median of 26 G records, 177.944 s at 4 ranks
#   Zb trim:                  DEC7 state B (zero shape, zero twist, trimmed), 574.5 s
#   Zo trim:                  DEC7 state S (the deformed geometry, trimmed), 2400.3 s
#   mesh + deform + stage:    FM10 arm wall 160 s minus its solve 71.847 s
#   model load per process:   DEC7 FOOTER wall 5918.862 minus the sum of its states
RANKS = 4
OBJ_EVAL_WALL_S = 81.7           # DEC7 d6r2c_dec5.jsonl, STATE O (n_trim = 1)
GRAD_EVAL_WALL_S = 177.944       # O_mp d6r2c_evals.jsonl, median of 26 G records
ZB_TRIM_WALL_S = 61.113          # RE-ANCHORED ON MEASUREMENT.  FM12's Zb ran the
                                 # WHOLE sub-arm in 163.413 s (its own FOOTER) against
                                 # the 676.8 s FM12 registered for it -- 4.14x faster,
                                 # because the trim closed in 2 evaluations where DEC7
                                 # STATE B needed 6.  163.413 minus the same
                                 # MESH_OVERHEAD_WALL_S (88.2) and MODEL_LOAD_WALL_S
                                 # (14.1) the formula below already carries leaves
                                 # 61.113 s for the trim itself.  WAS 574.5 (DEC7
                                 # STATE B), which is now KNOWN TOO LARGE for this
                                 # state and is named here rather than quietly dropped.
ZO_TRIM_WALL_S = 2400.3          # DEC7 STATE S -- UNTESTED.  FM12 never reached a Zo
                                 # solve (BLOCKED at its deform phase), so this term is
                                 # neither confirmed nor falsified and is carried
                                 # forward UNCHANGED and LABELLED so.
MESH_OVERHEAD_WALL_S = 88.2      # FM10: 160 - 71.847, rounded up to 88.2
MODEL_LOAD_WALL_S = 14.1         # DEC7: 5918.862 - (574.5+1205.7+2400.3+1150.1+81.7+492.5)
N_SUB_ARMS = 2
CAP_FACTOR = 3.00
RATE_USD_PER_CORE_H = 0.0513     # owner-stated; the box cannot read its own billing

CORE_MIN_PER_OBJ_EVAL = OBJ_EVAL_WALL_S * RANKS / 60.0
CORE_MIN_PER_GRAD_EVAL = GRAD_EVAL_WALL_S * RANKS / 60.0
N_GRAD_EVALS_THIS_ARM = 0        # FM12 runs NO adjoint.  Registered so the zero
                                 # is BY DESIGN and visible, not by omission.
PREDICTED_WALL_S = (N_SUB_ARMS * MESH_OVERHEAD_WALL_S
                    + N_SUB_ARMS * MODEL_LOAD_WALL_S
                    + ZB_TRIM_WALL_S + ZO_TRIM_WALL_S
                    + 2 * OBJ_EVAL_WALL_S)          # Ez and Do, one evaluation each
PREDICTION_CORE_MIN = round(PREDICTED_WALL_S * RANKS / 60.0, 3)
CAP_CORE_MIN = round(PREDICTION_CORE_MIN * CAP_FACTOR, 3)
# THE ARM IDS THIS DOCUMENT REGISTERS.  A re-run id carries THE IDENTICAL
# REGISTERED FIGURE -- the same number under another key.  --item accepts every
# one of them, so a launcher that passes its own arm id cannot fall through
# argparse the way `--item FM9` did while arm FM10 was running (L-570).
ARM_IDS = ("FM13", "FM13R2", "FM13R3")
CAPS = {a: CAP_CORE_MIN for a in ARM_IDS}

LABEL_PASS = "PASS"
LABEL_GATE_FAIL = "GATE FAIL"
LABEL_NOT_A_RESULT = "NOT A RESULT"
LABEL_BLOCKED = "BLOCKED"


class Refusal(Exception):
    """Refuse (exit 2), never degrade."""


# ---------------------------------------------------------------------------
# THE LIBRARIES.  The readers are imported, never re-spelled (L-221/L-222), so
# that the grader and the producer cannot disagree about what a mesh file says.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d6r2c_fm9_stage as stg          # noqa: E402
import d6r2c_fm12_states as prod       # noqa: E402


def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _finite(x, what):
    v = float(x)
    if v != v or v in (float("inf"), float("-inf")):
        raise Refusal("REFUSE_NON_FINITE %s = %r" % (what, x))
    return v


def _scalar(x, what):
    """The number OpenMDAO wrote, whether it wrote it bare or wrapped.

    OpenMDAO serialises every output as an ARRAY, so `obj.J` in the optimiser's
    own evaluation log reads `[0.030641631438997615]`.  A ONE-element list is
    that scalar; anything longer is a VECTOR and is REFUSED rather than silently
    reduced to its first element -- an instrument that takes `[a, b][0]` is
    reading an adjacent quantity (L-595)."""
    if isinstance(x, (list, tuple)):
        if len(x) != 1:
            raise Refusal("REFUSE_J_NOT_SCALAR %s is a sequence of %d, not a "
                          "scalar.  This clause will not pick an element out of "
                          "a vector and call it the objective"
                          % (what, len(x)))
        x = x[0]
    return _finite(x, what)


def _req(d, key, what):
    if key not in d:
        raise Refusal("REFUSE_MISSING_FIELD %r in %s" % (key, what))
    return d[key]


def weighted_J(cd):
    missing = [p for p in POINTS if p not in cd]
    if missing:
        raise Refusal("REFUSE_MISSING_CONDITION %r -- a weighted drag over a "
                      "subset of the conditions is not this arm's J" % missing)
    return sum(WEIGHTS[p] * _finite(cd[p], "CD[%s]" % p) for p in POINTS)


# ---------------------------------------------------------------------------
# THE THREE EXTERNAL ANCHORS.  Each is a quantity THIS ARM DOES NOT PRODUCE.
# ---------------------------------------------------------------------------

def load_inherited(evals_path, require_md5=True):
    """J0 and Jf from the optimiser's own evaluation log -- the record that
    fixes the 24.732 % headline.  READ, never re-typed."""
    if not os.path.isfile(evals_path):
        raise Refusal("REFUSE_MISSING_EVALS %s -- R_def has no anchor" % evals_path)
    got = _md5(evals_path)
    if require_md5 and got != EVALS_MD5:
        raise Refusal("REFUSE_EVALS_MD5 got %s want %s -- the optimisation this "
                      "arm is a comparison against is not the one on disk"
                      % (got, EVALS_MD5))
    f = {}
    for line in open(evals_path):
        r = json.loads(line)
        if r.get("kind") == "F" and r.get("n") is not None:
            f[int(r["n"])] = r
    for n in (N_J0, N_JF):
        if n not in f:
            raise Refusal("REFUSE_NO_F_RECORD n=%d in %s" % (n, evals_path))

    def _J(rec):
        fu = rec.get("funcs") or {}
        cd = {}
        for p in POINTS:
            for k in ("%s.aero_post.functionals.CD" % p, "%s.aero_post.CD" % p,
                      "%s_CD" % p, "CD_%s" % p):
                if k in fu:
                    cd[p] = _scalar(fu[k], k)
                    break
        if len(cd) == len(POINTS):
            return weighted_J(cd), "recomputed from the per-condition CD"
        # THE FALLBACK, REPAIRED.  FM11's chain tried ("obj", "J", "fun",
        # "weighted_CD") and the REAL record's key is `obj.J` -- with a dot --
        # whose value is a ONE-ELEMENT LIST, and its F records carry no
        # per-condition CD at all.  So the emitted command REFUSED
        # REFUSE_NO_J_IN_RECORD on the very anchor it was written to read, and
        # the selftest never saw it because it ran on `--evals SYNTHETIC`.
        # MEASURED on /home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-
        # multipoint-transonic-restartable/O_mp/d6r2c_evals.jsonl, md5
        # 2c0b8143caad198cd2e21d8047986aa3:
        #     n=2   funcs keys ['cl04.aero_post.functionals.CL', ..., 'obj.J']
        #           obj.J = [0.030641631438997615]
        #     n=88  obj.J = [0.023063259528677764]
        #     ratio = 0.752677270941 -- R_def to twelve places.
        # THE ANCHOR WAS NEVER IN DOUBT.  ONLY THE READER WAS.
        for k in ("obj.J", "obj", "J", "fun", "weighted_CD"):
            if k in fu:
                return _scalar(fu[k], k), "the record's own %s" % k
        raise Refusal("REFUSE_NO_J_IN_RECORD keys=%r" % sorted(fu)[:12])

    J0, how0 = _J(f[N_J0])
    Jf, howf = _J(f[N_JF])
    return {"J0": J0, "Jf": Jf, "J0_basis": how0, "Jf_basis": howf,
            "evals_md5": got, "n_J0": N_J0, "n_Jf": N_JF}


def load_fm10(path):
    """FM10's measured CL excess -- E_star, D1's external anchor.  FM10 is
    NOT A RESULT and stays NOT A RESULT; what is used here is its measured lift
    excess, which is the very thing that made it one."""
    if not os.path.isfile(path):
        raise Refusal("REFUSE_MISSING_FM10_RECORD %s -- D1 and D2 have no "
                      "external anchor and this arm will not invent one" % path)
    r = json.load(open(path))
    solve = _req(r, "solve", "the FM10 record")
    cl = _req(solve, "CL", "FM10 solve")
    cd = _req(solve, "CD", "FM10 solve")
    e_star = {p: _finite(cl[p], "FM10 CL[%s]" % p) - CL_TARGETS[p] for p in POINTS}
    return {"E_star": e_star, "CL": {p: cl[p] for p in POINTS},
            "J": weighted_J(cd), "record": path,
            "role": "FM10 is NOT A RESULT and is not re-graded.  Its MEASURED "
                    "lift excess is D1's anchor and its MEASURED J is D2's."}


def declared_max_nonorth(runscript_path):
    """DAFoam's OWN declared limit, parsed out of the md5-asserted runScript's
    checkMeshThreshold block.  DERIVED HERE, and the derived value is used --
    a literal 70.0 typed into a grader is a second thing that can drift."""
    if not os.path.isfile(runscript_path):
        raise Refusal("REFUSE_MISSING_RUNSCRIPT %s -- Q1 has no declared limit "
                      "to compare against" % runscript_path)
    src = open(runscript_path).read()
    got = hashlib.md5(src.encode()).hexdigest()
    if got != RUNSCRIPT_MD5:
        raise Refusal("REFUSE_RUNSCRIPT_MD5 got %s want %s" % (got, RUNSCRIPT_MD5))
    m = re.search(r'"checkMeshThreshold"\s*:\s*\{(.*?)\}', src, re.S)
    if not m:
        raise Refusal("REFUSE_NO_CHECKMESH_THRESHOLD in %s" % runscript_path)
    v = re.search(r'"maxNonOrth"\s*:\s*([0-9.eE+-]+)', m.group(1))
    if not v:
        raise Refusal("REFUSE_NO_MAXNONORTH in the checkMeshThreshold block")
    return _finite(v.group(1), "maxNonOrth")


# ---------------------------------------------------------------------------
# THE ARM LOG -- H4's CONVERGENCE LIMB, AND THE CHANNEL THAT REPLACED THE ONE
# WITH NO WRITER
# ---------------------------------------------------------------------------

_CD_RE = re.compile(r"^CD:\s*([0-9eE.+-]+)")
_TIME_RE = re.compile(r"^Time = ([0-9eE.+-]+)\s*$")


def parse_primal_blocks(text):
    """Every primal the solver ran, from the solver's OWN printed output.

    A block is the run of lines up to an `End`; it is a PRIMAL block if it
    printed at least two `CD:` lines, which is what separates a flow solve from
    the mesh-utility runs that also print `End`.  A PURE FUNCTION OVER TEXT,
    deliberately: that is what lets a check drive it to its failing side with a
    synthetic log rather than waiting for a run to go wrong."""
    blocks, cur_cd, cur_t = [], [], []
    for line in text.splitlines():
        s = line.strip()
        m = _CD_RE.match(s)
        if m:
            try:
                cur_cd.append(float(m.group(1)))
            except ValueError:
                pass
            continue
        m = _TIME_RE.match(s)
        if m:
            cur_t.append(m.group(1))
            continue
        if s == "End":
            if len(cur_cd) >= 2:
                blocks.append({"n_cd_prints": len(cur_cd),
                               "n_time_prints": len(cur_t),
                               "last_time": cur_t[-1] if cur_t else None,
                               "cd_last": cur_cd[-1], "cd_prev": cur_cd[-2]})
            cur_cd, cur_t = [], []
    return blocks


def grade_log(log_path, settle_rel):
    """REFUSES on a log with no primal block at all.  A convergence clause whose
    source is absent must not read as zero failures -- that is the shape of the
    defect charter 22.4 clause 3 names, and rule 3 forbids it."""
    if not log_path or not os.path.isfile(log_path):
        raise Refusal("REFUSE_NO_ARM_LOG %r -- H4's convergence limb has no "
                      "source, and an absent source is NOT zero failures"
                      % log_path)
    blocks = parse_primal_blocks(open(log_path, errors="replace").read())
    if not blocks:
        raise Refusal("REFUSE_NO_PRIMAL_BLOCKS in %s -- the log carries no flow "
                      "solve at all.  A writer that did not run cannot be read "
                      "as a pass (rule 3)" % log_path)
    worst, worst_i = 0.0, None
    rows = []
    for i, b in enumerate(blocks):
        denom = abs(b["cd_last"]) or 1.0
        rel = abs(b["cd_last"] - b["cd_prev"]) / denom
        rows.append({"block": i, "n_cd_prints": b["n_cd_prints"],
                     "last_time": b["last_time"], "cd_last": b["cd_last"],
                     "rel_change_last_step": rel, "settled": rel <= settle_rel})
        if rel > worst:
            worst, worst_i = rel, i
    return {"source": "the arm log -- the solver's own printed CD series",
            "n_primal_blocks": len(blocks),
            "worst_rel_change_last_step": worst,
            "worst_block": worst_i,
            "CD_SETTLE_REL": settle_rel,
            "all_settled": all(r["settled"] for r in rows),
            "blocks": rows,
            "why_not_primal_residual_json":
                "that channel had four readers, zero writers and zero such "
                "files on disk, and its default was True (charter 22.4.3).  It "
                "is DELETED from this item; this limb reads a channel whose "
                "writer is the solver and whose absence REFUSES."}


# ---------------------------------------------------------------------------
# THE RUN DIRECTORY -- re-measured, never believed
# ---------------------------------------------------------------------------

def read_states(sub_dir):
    path = os.path.join(sub_dir, RECORD)
    if not os.path.isfile(path):
        raise Refusal("REFUSE_MISSING_RECORD %s" % path)
    head, states, foot = None, {}, None
    for line in open(path):
        r = json.loads(line)
        k = r.get("kind")
        if k == "HEADER":
            head = r
        elif k == "STATE":
            states[r["state"]] = r
        elif k == "FOOTER":
            foot = r
    if head is None:
        raise Refusal("REFUSE_NO_HEADER in %s" % path)
    return {"header": head, "states": states, "footer": foot, "path": path}


def remeasure_mesh_gate(sub_dir, _plant=None):
    """M1: THE MESH THE RUNNING SOLVER LOADED, rebuilt from its own
    pointProcAddressing and compared FOR EXACT EQUALITY against the mesh this
    arm generated.  H2-style checks -- the mesh exists, it came from the pinned
    script, it differs from the base -- were ALL THREE TRUE IN FM5, FM7 AND FM8
    WHILE THE SOLVER READ SOMETHING ELSE."""
    pm = os.path.join(sub_dir, "constant", "polyMesh")
    gpath = stg._open_either(os.path.join(pm, "points"))
    generated = stg.read_points(gpath)
    out = {"generated_points_md5": stg._md5(gpath),
           "n_generated_points": len(generated), "conditions": {}}
    ok = True
    for mp in RUN_DIRS:
        mp_dir = os.path.join(sub_dir, mp)
        row = {"n_processors": len(stg.processor_dirs(mp_dir))}
        try:
            loaded = stg.reconstruct_loaded_points(mp_dir, len(generated))
            worst = stg.max_point_difference(loaded, generated)
            if _plant and _plant[0] == "M1" and _plant[1] == mp:
                worst += PLANT
            row["max_point_difference_from_generated"] = worst
            row["exact"] = (worst == 0.0)
        except Refusal as e:
            row["refusal"] = str(e)
            row["exact"] = False
        row["n_processors_ok"] = row["n_processors"] == N_PROCESSORS
        ok = ok and row["exact"] and row["n_processors_ok"]
        out["conditions"][mp] = row
    out["pass"] = ok
    out["rule"] = ("EXACT equality.  A tolerance here would let a mesh that is "
                   "nearly the generated one pass as the generated one, and the "
                   "question M1 answers admits no nearly.")
    return out


def remeasure_wall_gate(sub_dir, states, _plant=None):
    """W1: G-WALL, RE-MEASURED FROM DISK.  The producer records its own result;
    this recomputes it from the processor directories, so a producer that
    mis-measured its own guard cannot carry the arm."""
    pm = os.path.join(sub_dir, "constant", "polyMesh")
    generated = stg.read_points(stg._open_either(os.path.join(pm, "points")))
    wall_ids, _nf = prod.fm.wall_point_ids(pm, patch=prod.WALL_PATCH)
    out = {"n_wall_points": len(wall_ids), "tol_m": prod.WALL_MOVE_TOL,
           "states": {}}
    gated_ok = True
    for st in sorted(states):
        row = {"gated": st in prod.WALL_GATE_STATES, "conditions": {}}
        for mp in RUN_DIRS:
            try:
                pts, used = prod.reconstruct_asrun_points(
                    os.path.join(sub_dir, mp), len(generated))
                w = prod.wall_displacement(pts, generated, wall_ids)
                if _plant and _plant[0] == "W1" and _plant[1] == mp:
                    w["max_displacement_m"] += PLANT
                    w["pass"] = w["max_displacement_m"] <= prod.WALL_MOVE_TOL
                w["time_dirs_read"] = used
            except Refusal as e:
                w = {"refusal": str(e), "pass": False, "max_displacement_m": None}
            row["conditions"][mp] = w
        row["max_displacement_m"] = max(
            [c["max_displacement_m"] for c in row["conditions"].values()
             if c.get("max_displacement_m") is not None] or [None])
        row["pass"] = all(c.get("pass") for c in row["conditions"].values())
        if row["gated"]:
            gated_ok = gated_ok and row["pass"]
        out["states"][st] = row
    out["pass"] = gated_ok
    out["note"] = ("RE-MEASURED FROM DISK.  The last state written is the one "
                   "whose warped points sit in the time directories, so only "
                   "that state's row is a live measurement; the earlier states' "
                   "rows are the producer's, carried in the state records and "
                   "reported beside these.")
    return out


def scan_ownership(root, datum_epoch):
    n, bad = 0, []
    for dirpath, _d, files in os.walk(root):
        for f in files:
            p = os.path.join(dirpath, f)
            try:
                st = os.lstat(p)
            except OSError:
                continue
            if st.st_mtime < datum_epoch:
                continue
            n += 1
            if st.st_uid == 0 or st.st_gid == 0:
                bad.append(p)
    return {"n_scanned": n, "n_root_owned": len(bad),
            "root_owned_examples": bad[:5], "ok": not bad}


# ---------------------------------------------------------------------------
# THE GRADE
# ---------------------------------------------------------------------------

def grade_fm12(arm_dir, datum_epoch, inherited, fm10, core_min, rc,
               runscript_path, log_path=None, _plant=None):
    # ---- the DERIVED constants, derived here and USED here -----------------
    J0, Jf = inherited["J0"], inherited["Jf"]
    FM_BAND_ABS = BAND_FRACTION_OF_J0 * J0
    R_def = Jf / J0
    rel_on_opt = FM_BAND_ABS / Jf
    rel_on_base = FM_BAND_ABS / J0
    RATIO_BAND = R_def * (rel_on_opt ** 2 + rel_on_base ** 2) ** 0.5
    TRIM_TOL = CL_FINDING_TRIGGER / G3_MULTIPLE
    CD_SETTLE_REL = (FM_BAND_ABS / J0) / SETTLE_MARGIN
    MAX_NONORTH = declared_max_nonorth(runscript_path)

    derived = {
        "J0": J0, "Jf": Jf, "R_def": R_def,
        "gain_def_pct": 100.0 * (1.0 - R_def),
        "FM_BAND_ABS": FM_BAND_ABS,
        "FM_BAND_ABS_basis": "%.3g x J0, DERIVED from the inherited J0 in this "
                             "invocation" % BAND_FRACTION_OF_J0,
        "RATIO_BAND": RATIO_BAND,
        "RATIO_BAND_basis": "FM_BAND_ABS propagated through the ratio in "
                            "quadrature: sqrt((%.8f)^2 + (%.8f)^2) x R_def.  A "
                            "DECLARED decision-relevance band inherited from "
                            "FM_BAND_ABS -- NOT a measured discretisation "
                            "uncertainty and NOT a GCI."
                            % (rel_on_opt, rel_on_base),
        "PASS_window": [R_def - RATIO_BAND, R_def + RATIO_BAND],
        "TRIM_TOL": TRIM_TOL,
        "TRIM_TOL_basis": "CL_FINDING_TRIGGER / %.1f -- the trigger is registered "
                          "as five times the G3 tolerance the optimiser itself "
                          "worked against" % G3_MULTIPLE,
        "CD_SETTLE_REL": CD_SETTLE_REL,
        "CD_SETTLE_REL_basis": "the decision band's relative size divided by a "
                               "DECLARED margin of %.0f.  The margin is declared, "
                               "not measured." % SETTLE_MARGIN,
        "MAX_NONORTH_DECLARED": MAX_NONORTH,
        "MAX_NONORTH_basis": "parsed from the md5-asserted runScript's own "
                             "checkMeshThreshold block, not typed here",
        "DOUBLE_SPLIT": DOUBLE_SPLIT,
    }

    # ---- the two sub-arms --------------------------------------------------
    sub = {}
    for s in SUB_ARMS:
        d = os.path.join(arm_dir, s)
        if not os.path.isdir(d):
            raise Refusal("REFUSE_MISSING_SUB_ARM %s -- G1 is a ratio and needs "
                          "both sides" % d)
        sub[s] = read_states(d)

    cd = {}
    for s in SUB_ARMS:
        st = sub[s]["states"].get(STATE_OF[s])
        if st is None:
            raise Refusal("REFUSE_MISSING_STATE %s in sub-arm %s"
                          % (STATE_OF[s], s))
        row = dict(_req(st, "CD", "state %s" % STATE_OF[s]))
        if _plant and _plant[0] == "CD" and _plant[1] == s:
            row[_plant[2]] = row[_plant[2]] + PLANT
        cd[s] = row
    J_base = weighted_J(cd["Zb"])
    J_opt = weighted_J(cd["Zo"])

    # ---- G1 -- THE RATIO AT MATCHED LIFT -----------------------------------
    R_fresh = J_opt / J_base if J_base else float("inf")
    lo, hi = R_def - RATIO_BAND, R_def + RATIO_BAND
    inside = lo <= R_fresh <= hi
    g1 = {"J_base_fresh": J_base, "J_opt_fresh": J_opt, "R_fresh": R_fresh,
          "gain_fresh_pct": 100.0 * (1.0 - R_fresh),
          "R_def": R_def, "window": [lo, hi], "inside": inside,
          "pass": inside,
          "branch": ("the gain survives independent mesh generation at matched "
                     "lift; the %.4f %% stands as quoted"
                     % derived["gain_def_pct"]) if inside else
                    ("the optimised shape is NOT better on independently "
                     "generated meshes; the %.4f %% is WITHDRAWN"
                     % derived["gain_def_pct"]) if R_fresh >= 1.0 else
                    ("a PARTIAL gain: both numbers are reported and the headline "
                     "may be quoted only with the fresh-mesh figure beside it"),
          "J_recomputed_from": "the per-condition CD and the frozen weights, "
                               "never a producer's own J"}

    # ---- G2 -- THE TRIM REACHED THE REGISTERED CONDITIONS ------------------
    g2 = {"TRIM_TOL": TRIM_TOL, "states": {}}
    g2_ok = True
    for s in SUB_ARMS:
        st = sub[s]["states"][STATE_OF[s]]
        cl = _req(st, "CL", "state %s" % STATE_OF[s])
        miss = {p: abs(_finite(cl[p], "CL") - CL_TARGETS[p]) for p in POINTS}
        row = {"CL": {p: cl[p] for p in POINTS}, "miss": miss,
               "max_miss": max(miss.values()),
               "trimmed": st.get("trimmed"),
               "n_trim_evals": st.get("n_trim_evals"),
               "pass": max(miss.values()) <= TRIM_TOL and bool(st.get("trimmed"))}
        g2_ok = g2_ok and row["pass"]
        g2["states"][STATE_OF[s]] = row
    g2["pass"] = g2_ok
    g2["role"] = ("a ratio of drags is only a comparison if both sides sit at "
                  "the same lift.  A trim that did not close is a MISSING "
                  "MEASUREMENT, never a solve at whatever lift it reached.")

    # ---- D1 -- THE DOUBLE-DEFORMATION DIAGNOSTIC ---------------------------
    ez = sub["Zo"]["states"].get("Ez")
    if ez is None:
        raise Refusal("REFUSE_MISSING_STATE Ez in sub-arm Zo -- D1 is a gate "
                      "and it has no measurement")
    e_zero = {p: _finite(ez["CL"][p], "Ez CL") - CL_TARGETS[p] for p in POINTS}
    if _plant and _plant[0] == "D1":
        e_zero = {p: v + PLANT for p, v in e_zero.items()}
    mean_zero = sum(abs(v) for v in e_zero.values()) / len(POINTS)
    mean_star = sum(abs(v) for v in fm10["E_star"].values()) / len(POINTS)
    ratio = mean_zero / mean_star if mean_star else float("inf")
    d1 = {"E_zero": e_zero, "E_star": fm10["E_star"],
          "mean_abs_E_zero": mean_zero, "mean_abs_E_star": mean_star,
          "ratio": ratio, "DOUBLE_SPLIT": DOUBLE_SPLIT,
          "pass": ratio < DOUBLE_SPLIT,
          "branch": ("the excess follows the shape DVs and not the mesh: the "
                     "double application is CONFIRMED and FM10's J_fresh is "
                     "withdrawn as a measurement of anything")
                    if ratio < DOUBLE_SPLIT else
                    ("the excess is a property of the fresh mesh: section 1b's "
                     "hypothesis is WRONG, and that is a larger finding about "
                     "the mesh than about the producer"),
          "split_basis": "a DECLARED split of a measured interval running from "
                         "zero to E_star.  One half is the midpoint and it is "
                         "not dressed up as derived.  The raw ratio is printed "
                         "whatever it is."}

    # ---- D2 -- Do REPRODUCES FM10 ------------------------------------------
    do = sub["Zo"]["states"].get("Do")
    if do is None:
        raise Refusal("REFUSE_MISSING_STATE Do in sub-arm Zo -- D2 is the "
                      "planted control in the large and it is not optional")
    J_do = weighted_J(do["CD"])
    if _plant and _plant[0] == "D2":
        J_do += PLANT
    cl_do = {p: _finite(do["CL"][p], "Do CL") for p in POINTS}
    cl_gap = {p: abs(cl_do[p] - fm10["CL"][p]) for p in POINTS}
    d2 = {"J_Do": J_do, "J_FM10": fm10["J"], "abs_diff": abs(J_do - fm10["J"]),
          "FM_BAND_ABS": FM_BAND_ABS, "CL_Do": cl_do, "CL_FM10": fm10["CL"],
          "CL_gap": cl_gap, "max_CL_gap": max(cl_gap.values()),
          "pass": (abs(J_do - fm10["J"]) <= FM_BAND_ABS
                   and max(cl_gap.values()) <= TRIM_TOL),
          "role": "THE PLANTED CONTROL IN THE LARGE.  If the same inputs on the "
                  "same mesh do not return the same numbers, nothing else in "
                  "this arm is evidence.  Failure here is NOT A RESULT for the "
                  "WHOLE arm, not for Do alone."}

    # ---- M0b / M0o -- THE TWO EXTRUSION-EVIDENCE GATES ----------------------
    # Read from each sub-arm's own header, where the stager wrote them BEFORE
    # anything was copied.  They are SEPARATE gates with separate pass fields:
    # a grader that reduced them to one boolean would be the relaxed gate this
    # arm exists to avoid.
    m0 = {s: sub[s]["header"].get("M0") for s in SUB_ARMS}
    if m0.get("Zb") is None or m0.get("Zo") is None:
        raise Refusal("REFUSE_MISSING_M0 the header of %r carries no M0 record "
                      "-- the extrusion-evidence gate did not run"
                      % [s for s in SUB_ARMS if m0.get(s) is None])
    if m0["Zb"].get("gate") != "M0b":
        raise Refusal("REFUSE_WRONG_M0_GATE sub-arm Zb was gated by %r, not M0b "
                      "-- Zb must be gated on PROVENANCE, because the mesh it "
                      "generates is EXPECTED to equal the base mesh"
                      % m0["Zb"].get("gate"))
    if m0["Zo"].get("gate") != "M0o":
        raise Refusal("REFUSE_WRONG_M0_GATE sub-arm Zo was gated by %r, not M0o "
                      "-- Zo must be gated on DIFFERENCE FROM BASE, and that "
                      "gate is not weakened for any sub-arm"
                      % m0["Zo"].get("gate"))
    m0b = dict(m0["Zb"])
    m0o = dict(m0["Zo"])
    # M0b.5 -- the polyMesh the SOLVER READ.  Taken from the Zb state record,
    # and RE-MEASURED below as M1; this limb is cited so M0b's claim is
    # evidenced, and it is the SAME measurement, not a second one.
    zb_state = sub["Zb"]["states"].get(STATE_OF["Zb"]) or {}
    rb = zb_state.get("M0b_readback") or {}
    if _plant and _plant[0] == "M0b":
        rb = dict(rb)
        rb["pass"] = False
    m0b["readback"] = rb
    m0b["pass"] = bool(m0b.get("pass")) and bool(rb.get("pass"))
    m0o["pass"] = bool(m0o.get("pass")) and bool(m0o.get("differs_from_base"))
    m0b_ok, m0o_ok = m0b["pass"], m0o["pass"]

    # ---- R1 -- MESHER DETERMINISM ACROSS TIME.  ITS OWN GATE, ITS OWN VERDICT,
    # ---- AND IT NEVER FLIPS THIS ARM'S LABEL --------------------------------
    r1_raw = dict(m0b.get("R1") or {})
    if not r1_raw:
        raise Refusal("REFUSE_MISSING_R1 the Zb header carries no R1 "
                      "measurement -- a registered gate with no measurement is "
                      "PENDING, and this grader will not print one as a pass")
    diff = r1_raw.get("max_point_difference_from_base_m")
    if _plant and _plant[0] == "R1":
        diff = (diff or 0.0) + PLANT
        r1_raw["max_point_difference_from_base_m"] = diff
    n_pts = r1_raw.get("n_points")
    n_id = r1_raw.get("n_points_identical")
    r1_pass = (diff == 0.0 and n_pts is not None and n_id == n_pts)
    r1 = dict(r1_raw)
    r1.update({
        "threshold": "max point difference == 0.0 m EXACTLY, and every point "
                     "identical.  A tolerance here would make the claim "
                     "'deterministic' unfalsifiable.",
        "verdict": LABEL_PASS if r1_pass else LABEL_GATE_FAIL,
        "pass": r1_pass,
        "claim": "genWingMesh.py plus the family sequence, run again on the "
                 "same base surface at the same parameters, reproduces the "
                 "base volume mesh BIT FOR BIT after %s days."
                 % (("%.3f" % r1_raw["elapsed_days"])
                    if r1_raw.get("elapsed_days") is not None else "an unrecorded number of"),
        "why_it_matters": "rules 8 and 9 of this family -- periodic re-meshing "
                          "and fresh-mesh checkpoints -- rest on the mesher "
                          "being reproducible.  Until now that was assumed.",
        "md5_claim_admissible": bool(r1_raw.get("gzip_mtime_field_is_zero")),
        "md5_claim_basis": "OpenFOAM writes .gz with the gzip header MTIME "
                           "field set to 0, READ BACK from both files by the "
                           "producer.  When that field is not zero on either "
                           "file the md5 half of this claim is WITHDRAWN and "
                           "only the point measurement stands.",
        "role": "REPORTED WITH ITS OWN VERDICT AND NEVER FLIPPING THIS ARM'S "
                "LABEL.  This arm's question is the drag ratio at matched lift; "
                "no mesher-determinism threshold was pre-registered as its "
                "gate.  R1 is graded, printed, and carried into `findings`.",
    })
    if not r1["md5_claim_admissible"]:
        r1["verdict_note"] = ("the md5 half is withdrawn; the verdict above "
                              "rests on the POINT measurement alone")

    # ---- M1 / W1 / Q1 -------------------------------------------------------
    m1 = {s: remeasure_mesh_gate(os.path.join(arm_dir, s), _plant=_plant)
          for s in SUB_ARMS}
    m1_ok = all(m1[s]["pass"] for s in SUB_ARMS)
    w1 = {s: remeasure_wall_gate(os.path.join(arm_dir, s),
                                 sorted(sub[s]["states"]), _plant=_plant)
          for s in SUB_ARMS}
    w1_producer = {s: {st: sub[s]["states"][st].get("G_WALL_pass")
                       for st in sorted(sub[s]["states"])} for s in SUB_ARMS}
    w1_ok = all(w1[s]["pass"] for s in SUB_ARMS) and all(
        v is not False for s in SUB_ARMS for v in w1_producer[s].values())

    q1 = {"declared_max_nonorth": MAX_NONORTH, "states": {}, "breaches": []}
    for s in SUB_ARMS:
        for st, rec in sorted(sub[s]["states"].items()):
            cm = rec.get("checkMesh_asrun") or {}
            row = {"sub_arm": s, "max_nonorth": cm.get("max_nonorth"),
                   "ran": cm.get("ran"), "rc": cm.get("rc"),
                   "condition": cm.get("condition"), "log": cm.get("log")}
            row["breaches"] = (row["max_nonorth"] is not None
                               and row["max_nonorth"] > MAX_NONORTH)
            if row["breaches"]:
                q1["breaches"].append("%s/%s max_nonorth=%.4f > %.1f"
                                      % (s, st, row["max_nonorth"], MAX_NONORTH))
            q1["states"]["%s/%s" % (s, st)] = row
    q1["any_breach"] = bool(q1["breaches"])
    q1["role"] = ("REPORTED, NEVER GATED, AND NEVER SILENT.  The comparison "
                  "value is DAFoam's own declared maxNonOrth, parsed from the "
                  "frozen runScript.  A breach does not flip this arm's label -- "
                  "its question is the drag ratio and no mesh-quality threshold "
                  "was pre-registered as its gate -- but it is written here, "
                  "into the printed verdict line and into `findings`, and the "
                  "headline may not be quoted without it.  MEASURED ELSEWHERE, "
                  "and this is why the clause exists: the optimisation mesh "
                  "as-run 71.24 and FM10 as-run 79.21 BOTH BREACH the declared "
                  "70.0, and neither was ever checked.")

    # ---- H4 -- COMPLETION AND HYGIENE --------------------------------------
    log = grade_log(log_path, CD_SETTLE_REL)
    own = scan_ownership(arm_dir, datum_epoch)
    rec_newer = {}
    for s in SUB_ARMS:
        p = sub[s]["path"]
        rec_newer[s] = os.path.getmtime(p) >= datum_epoch
    cap_crossed = core_min is not None and core_min > CAP_CORE_MIN
    footers_ok = all(sub[s]["footer"] is not None for s in SUB_ARMS)
    uid_ok = all(sub[s]["header"].get("uid") == 1000 for s in SUB_ARMS)
    h4 = {"rc": rc, "rc_is_zero": rc == 0,
          "core_min": core_min, "cap_core_min": CAP_CORE_MIN,
          "cap_crossed": cap_crossed,
          "cap_rule": "Sanaa's directive #17 is in force: NOTHING IS STOPPED BY "
                      "THE CAP.  A crossing is REPORTED and the row is graded "
                      "NOT A RESULT, and the cap is never raised.",
          "footers_present": footers_ok,
          "ran_as_uid_1000": uid_ok,
          "record_newer_than_datum": rec_newer,
          "ownership": own,
          "convergence_from_the_log": log,
          "pass": (rc == 0 and footers_ok and uid_ok and own["ok"]
                   and all(rec_newer.values()) and log["all_settled"])}

    # ---- THE LABEL ---------------------------------------------------------
    # M0b and M0o ARE HARD GATES AND ARE LISTED SEPARATELY.  R1 IS NOT HERE:
    # it carries its own verdict and never flips this arm's label.
    hard = {"G2": g2["pass"], "D2": d2["pass"], "M0b": m0b_ok, "M0o": m0o_ok,
            "M1": m1_ok, "W1": w1_ok, "H4": h4["pass"]}
    if cap_crossed or not all(hard.values()):
        label = LABEL_NOT_A_RESULT
    else:
        label = LABEL_PASS if g1["pass"] else LABEL_GATE_FAIL

    findings = []
    if q1["any_breach"]:
        findings.append("MESH QUALITY: the mesh that RAN breaches DAFoam's own "
                        "declared maxNonOrth = %.1f -- %s"
                        % (MAX_NONORTH, "; ".join(q1["breaches"])))
    if r1["pass"]:
        findings.append(
            "R1 %s -- MESHER DETERMINISM ACROSS TIME: genWingMesh.py plus the "
            "family sequence reproduces the base volume mesh BIT FOR BIT after "
            "%.3f days -- max point difference %.17g m, %d/%d points identical%s."
            "  Rules 8 and 9 (periodic re-meshing, fresh-mesh checkpoints) "
            "assumed this; it is now measured."
            % (LABEL_PASS, r1.get("elapsed_days") or 0.0,
               r1["max_point_difference_from_base_m"], n_id, n_pts,
               ", md5 identical on files whose gzip MTIME field reads 0 on both"
               if r1["md5_claim_admissible"] and r1.get("md5_identical") else
               " (the md5 half is withdrawn: a gzip MTIME field is not zero)"))
    else:
        findings.append(
            "R1 %s -- MESHER DETERMINISM ACROSS TIME: the regenerated base mesh "
            "does NOT reproduce the base mesh; max point difference %.6e m, "
            "%s/%s points identical, after %.3f days.  This does NOT flip the "
            "arm's label -- its question is the drag ratio -- but the headline "
            "may not be quoted without it."
            % (LABEL_GATE_FAIL, r1["max_point_difference_from_base_m"] or 0.0,
               n_id, n_pts, r1.get("elapsed_days") or 0.0))
    if label == LABEL_GATE_FAIL and g1["R_fresh"] >= 1.0:
        findings.append("THE 24.732 %% IS WITHDRAWN: R_fresh = %.6f >= 1.0 at "
                        "matched lift on independently generated meshes"
                        % g1["R_fresh"])
    if d1["pass"]:
        findings.append("PRODUCER: D1 confirms the double application; FM10's "
                        "J_fresh is withdrawn as a measurement of anything.  A "
                        "defect note against d6r2c_freshmesh.py is a DRAFT and "
                        "is NOT FILED -- submissions parked (rule 7).")

    return {"item": "FM12", "label": label,
            "G1": g1["pass"], "G2": g2["pass"], "D1": d1["pass"],
            "D2": d2["pass"], "M0b": m0b_ok, "M0o": m0o_ok,
            "M1": m1_ok, "W1": w1_ok, "H4": h4["pass"],
            "R1": r1["pass"], "R1_verdict": r1["verdict"],
            "Q1_reported_not_gated": not q1["any_breach"],
            "G1_detail": g1, "G2_detail": g2, "D1_detail": d1,
            "D2_detail": d2, "M0_detail": m0, "M0b_detail": m0b,
            "M0o_detail": m0o, "R1_detail": r1, "M1_detail": m1,
            "W1_detail": {"remeasured": w1, "producer_recorded": w1_producer},
            "Q1_detail": q1, "H4_detail": h4,
            "derived_constants": derived,
            "inherited": inherited, "fm10_anchor": fm10,
            "findings": findings,
            "does_not_claim": [
                "no GCI is computed and none may be quoted; RATIO_BAND is a "
                "DECLARED decision band and a Roache triple would need three "
                "grid levels this arm does not run (CLAUDE.md rule 5)",
                "the cross-mesh ratio J_fresh/Jf mixes a fresh-mesh numerator "
                "with a deformed-mesh denominator and must not be quoted",
                "FM10's NOT A RESULT stands and is not re-graded into anything",
                "R1 is a statement about THIS mesher on THIS surface at THESE "
                "parameters over THIS interval.  It is not a claim that "
                "genWingMesh.py is deterministic in general, and it says "
                "nothing about a different surface, a different machine or a "
                "different image",
                "M0b.5 is the SAME measurement as M1 restricted to Zb.  It is "
                "cited under M0b so that gate's claim is evidenced; it is not a "
                "second independent confirmation and two green limbs here are "
                "one reading, not two",
                "FM11 is BLOCKED and stays BLOCKED.  Nothing in this arm "
                "re-grades it, and its frozen instruments are untouched",
            ]}


# ---------------------------------------------------------------------------
# THE PLANTED CONTROL (rule 3) -- A ZERO FROM A READER NOT SHOWN ABLE TO SEE A
# NON-ZERO IS NOT EVIDENCE
# ---------------------------------------------------------------------------

def live_plant_check(kwargs, verdict_label):
    """Plant PLANT into the per-condition CD THE GRADER READS BACK FROM DISK,
    re-grade, and REFUSE unless the planted value moves the graded ratio.  The
    plant goes into the read-back, never into a registered copy -- a reader
    compared against itself sees nothing and proves nothing."""
    out = {"PLANT": PLANT, "plants": []}
    base = grade_fm12(**kwargs)
    for plant in [("CD", "Zo", "cl05"), ("CD", "Zb", "cl05"),
                  ("M1", "mp04"), ("W1", "mp04"), ("D1",), ("D2",),
                  ("M0b",), ("R1",)]:
        kw = dict(kwargs)
        kw["_plant"] = plant
        try:
            got = grade_fm12(**kw)
        except Refusal as e:
            out["plants"].append({"plant": plant, "refused": str(e), "seen": True})
            continue
        # THE FINGERPRINT IS THE GRADED QUANTITIES, NOT ONLY THE VERDICT.  A
        # plant that moves a measured value without crossing a threshold is
        # STILL SEEN, and a check that only watched the booleans would call the
        # grader blind when it was merely inside its band -- which is the
        # opposite error to the one rule 3 is about, and just as wrong.
        def _fp(r):
            return (r["G1_detail"]["R_fresh"], r["label"],
                    r["M1"], r["W1"], r["D1"], r["D2"],
                    r["M0b"], r["M0o"], r["R1"],
                    r["R1_detail"]["max_point_difference_from_base_m"],
                    r["D1_detail"]["ratio"], r["D2_detail"]["abs_diff"],
                    r["W1_detail"]["remeasured"]["Zb"]["states"]["Zb"]
                     ["max_displacement_m"])
        moved = _fp(got) != _fp(base)
        out["plants"].append({"plant": plant, "seen": moved,
                              "label_before": base["label"],
                              "label_after": got["label"],
                              "R_before": base["G1_detail"]["R_fresh"],
                              "R_after": got["G1_detail"]["R_fresh"]})
    out["all_seen"] = all(p["seen"] for p in out["plants"])
    if not out["all_seen"]:
        blind = [p["plant"] for p in out["plants"] if not p["seen"]]
        raise Refusal("REFUSE_PLANT_UNSEEN the grader could not see the planted "
                      "%.3e in %r.  A zero from a reader not shown able to see "
                      "a non-zero is not evidence (rule 3)." % (PLANT, blind))
    out["verdict_graded"] = verdict_label
    return out


# ---------------------------------------------------------------------------
# SELFTEST -- synthetic trees only.  Touches no run directory.
# ---------------------------------------------------------------------------

def _synth_arm(root, J_base, J_opt, cl_base=None, cl_opt=None, cl_ez=None,
               J_do=None, cl_do=None, nonorth=66.32, warp_zo=False,
               loaded_wrong=False, uid=1000,
               r1_diff=0.0, r1_n=40209, r1_ident=40209, r1_gzip=True,
               m0o_differs=True, readback_ok=True, m0_gate_wrong=None):
    """A complete synthetic FM12 arm: two sub-arms, four states, meshes the
    reconstruction can actually rebuild."""
    n_pts = 24
    gen = [(float(i), 0.0, 0.0) for i in range(n_pts)]
    wall_ids = [2, 5, 9]
    for s in SUB_ARMS:
        d = os.path.join(root, s)
        pm = os.path.join(d, "constant", "polyMesh")
        os.makedirs(pm)
        _write_points(os.path.join(pm, "points"), gen)
        _write_wall_boundary(pm, wall_ids)
        for mp in RUN_DIRS:
            pts = list(gen)
            if loaded_wrong and s == "Zo" and mp == "mp05":
                pts[1] = (pts[1][0] + 1e-3, 0.0, 0.0)
            prod._synth_mp(os.path.join(d, mp), pts, n_proc=N_PROCESSORS,
                           time_name="1000")
            if warp_zo and s == "Zo":
                moved = list(gen)
                moved[wall_ids[0]] = (moved[wall_ids[0]][0] + 0.02, 0.0, 0.0)
                prod._synth_mp(os.path.join(root, "_w"), moved,
                               n_proc=N_PROCESSORS, time_name="1000")
                for i in range(N_PROCESSORS):
                    shutil.copyfile(
                        os.path.join(root, "_w", "processor%d" % i, "1000",
                                     "polyMesh", "points"),
                        os.path.join(d, mp, "processor%d" % i, "1000",
                                     "polyMesh", "points"))
        rows = []
        if s == "Zb":
            m0 = {"gate": "M0b", "sub_arm": "Zb", "pass": True,
                  "R1": {"clause": "R1 -- MESHER DETERMINISM ACROSS TIME",
                         "max_point_difference_from_base_m": r1_diff,
                         "n_points": r1_n, "n_points_identical": r1_ident,
                         "all_points_identical": r1_ident == r1_n,
                         "md5_identical": r1_diff == 0.0,
                         "gzip_mtime_field_is_zero": r1_gzip,
                         "elapsed_days": 47.719,
                         "base_points_md5": BASE_POINTS_MD5}}
        else:
            m0 = {"gate": "M0o", "sub_arm": "Zo", "pass": True,
                  "max_point_difference_from_base_m": 1.5,
                  "differs_from_base": m0o_differs}
        if m0_gate_wrong and m0_gate_wrong[0] == s:
            m0["gate"] = m0_gate_wrong[1]
        hdr = {"kind": "HEADER", "sub_arm": s, "uid": uid, "ranks": 4, "M0": m0}
        rows.append(hdr)
        states = [(STATE_OF[s], J_base if s == "Zb" else J_opt,
                   cl_base if s == "Zb" else cl_opt, True)]
        if s == "Zo":
            states.append(("Ez", J_opt, cl_ez, False))
            states.append(("Do", J_do, cl_do, False))
        for st, J, cl, trimmed in states:
            rows.append({"kind": "STATE", "state": st, "sub_arm": s,
                         "trimmed": trimmed, "n_trim_evals": 6 if trimmed else 1,
                         "CD": {p: J for p in POINTS},
                         "CL": dict(cl), "AoA_deg": {p: 1.0 for p in POINTS},
                         "J": J, "G_WALL_pass": True if st != "Do" else None,
                         "M0b_readback": ({"limb": "M0b.5",
                                           "pass": readback_ok,
                                           "conditions": {}}
                                          if s == "Zb" else None),
                         "checkMesh_asrun": {"max_nonorth": nonorth, "ran": True,
                                             "rc": 0, "condition": "mp05",
                                             "log": "checkMesh_asrun_%s.log" % st}})
        rows.append({"kind": "FOOTER", "sub_arm": s, "rc": 0})
        with open(os.path.join(d, RECORD), "w") as fh:
            for r in rows:
                fh.write(json.dumps(r, sort_keys=True) + "\n")
    shutil.rmtree(os.path.join(root, "_w"), ignore_errors=True)
    return root


def _write_points(path, pts):
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n}\n// * * *\n\n%d\n(\n" % len(pts))
        for p in pts:
            fh.write("(%.17g %.17g %.17g)\n" % p)
        fh.write(")\n")


def _write_wall_boundary(pm, wall_ids):
    """One `wing` face carrying exactly wall_ids, so wall_point_ids() returns
    them.  The faces file holds a filler face first so startFace = 1."""
    with open(os.path.join(pm, "faces"), "w") as fh:
        fh.write("FoamFile\n{\n}\n// * * *\n\n2\n(\n3(0 1 3)\n%d(%s)\n)\n"
                 % (len(wall_ids), " ".join(str(i) for i in wall_ids)))
    with open(os.path.join(pm, "boundary"), "w") as fh:
        fh.write("FoamFile\n{\n}\n// * * *\n\n1\n(\n    wing\n    {\n"
                 "        type            wall;\n        nFaces          1;\n"
                 "        startFace       1;\n    }\n)\n")


def _strip_r1(root):
    """Remove the R1 measurement from a synthetic arm's Zb header, so the
    'a registered gate with no measurement is PENDING' path can be driven."""
    p = os.path.join(root, "Zb", RECORD)
    rows = [json.loads(l) for l in open(p)]
    for r in rows:
        if r.get("kind") == "HEADER":
            r["M0"].pop("R1", None)
    with open(p, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")


def _synth_log(tmp, n_blocks=8, settled=True, name="arm.log"):
    # THE NAME IS A PARAMETER, and it is one because the first draft of this
    # function hardcoded "arm.log": building an unsettled log then SILENTLY
    # OVERWROTE the settled one every later control was still pointing at, and
    # four controls failed for a reason that had nothing to do with what they
    # were testing.  A fixture that cannot make two different fixtures is a
    # fixture that makes one.
    p = os.path.join(tmp, name)
    with open(p, "w") as fh:
        fh.write("Create time\n\nTime = 0\nEnd\n")     # a mesh utility, no CD
        for i in range(n_blocks):
            fh.write("\nSetting UMag = 100 AoA = 4 degs at 1(inout)\n")
            for t in (1, 500, 999, 1000):
                fh.write("\nTime = %d\n\n" % t)
                fh.write("CD: 0.0400000000 final: 0.0400000000\n"
                         if (settled or t != 1000) else
                         "CD: 0.0500000000 final: 0.0500000000\n")
                fh.write("CL: 0.5 final: 0.5\n")
            fh.write("\nEnd\n\nPrinting Primal Residual Statistics.\n")
    return p


def selftest():
    import tempfile
    ok = True
    n = 0

    def check(name, got, want):
        nonlocal ok, n
        n += 1
        if got != want:
            ok = False
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r" % (name, got, want))

    # ---- the cost, DERIVED, and the derived value is the one served --------
    check("the cap is 3.00x the derived prediction, to three decimals",
          CAP_CORE_MIN, round(PREDICTION_CORE_MIN * CAP_FACTOR, 3))
    check("every registered arm id carries the IDENTICAL cap",
          sorted({CAPS[a] for a in ARM_IDS}), [CAP_CORE_MIN])
    check("the per-objective-evaluation figure is the DEC7 anchor, converted",
          round(CORE_MIN_PER_OBJ_EVAL, 3), round(81.7 * 4 / 60.0, 3))
    check("the per-gradient-evaluation figure is the O_mp anchor, converted",
          round(CORE_MIN_PER_GRAD_EVAL, 3), round(177.944 * 4 / 60.0, 3))
    check("this arm runs ZERO gradient evaluations, registered as zero",
          N_GRAD_EVALS_THIS_ARM, 0)

    # ---- the log limb, DRIVEN IN BOTH DIRECTIONS --------------------------
    tmp = tempfile.mkdtemp(prefix="d6r2c_fm12_grade_selftest_")
    try:
        lg = _synth_log(tmp, n_blocks=8, settled=True)
        r = grade_log(lg, 1.0e-5)
        check("the log limb counts every primal block and NOT the mesh utility",
              r["n_primal_blocks"], 8)
        check("a settled log passes", r["all_settled"], True)
        lg2 = _synth_log(tmp, n_blocks=3, settled=False, name="unsettled.log")
        r2 = grade_log(lg2, 1.0e-5)
        check("an UNSETTLED log FAILS the limb", r2["all_settled"], False)
        check("... and it names the worst block", r2["worst_block"] is not None, True)
        empty = os.path.join(tmp, "empty.log")
        open(empty, "w").write("Create time\nTime = 0\nEnd\n")
        try:
            grade_log(empty, 1.0e-5)
            check("a log with no primal block REFUSES", "no refusal", "Refusal")
        except Refusal as e:
            check("no primal block -> REFUSE_NO_PRIMAL_BLOCKS",
                  str(e).startswith("REFUSE_NO_PRIMAL_BLOCKS"), True)
        try:
            grade_log(os.path.join(tmp, "nope.log"), 1.0e-5)
            check("an ABSENT log REFUSES rather than reading as zero failures",
                  "no refusal", "Refusal")
        except Refusal as e:
            check("an absent log -> REFUSE_NO_ARM_LOG",
                  str(e).startswith("REFUSE_NO_ARM_LOG"), True)

        # ---- the declared limit is PARSED from the frozen runScript --------
        rs = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "d6r2c_opt_runScript.py")
        if os.path.isfile(rs):
            check("maxNonOrth is parsed out of the frozen runScript, not typed",
                  declared_max_nonorth(rs), 70.0)
            bad = os.path.join(tmp, "bad_runscript.py")
            open(bad, "w").write("x = 1\n")
            try:
                declared_max_nonorth(bad)
                check("a runScript at the wrong md5 refuses", "no refusal", "Refusal")
            except Refusal as e:
                check("wrong runScript -> REFUSE_RUNSCRIPT_MD5",
                      str(e).startswith("REFUSE_RUNSCRIPT_MD5"), True)

        # ---- the whole grade, on a synthetic arm, IN BOTH DIRECTIONS -------
        inh = {"J0": 0.0306416314389976151, "Jf": 0.0230632595286777639,
               "J0_basis": "synthetic", "Jf_basis": "synthetic",
               "evals_md5": "synthetic", "n_J0": N_J0, "n_Jf": N_JF}
        E_star = {"cl04": 0.149286, "cl05": 0.151566, "cl06": 0.152398}
        fm10 = {"E_star": E_star,
                "CL": {p: CL_TARGETS[p] + E_star[p] for p in POINTS},
                "J": 0.036964341844, "record": "synthetic", "role": "synthetic"}
        on_target = {p: CL_TARGETS[p] for p in POINTS}
        small = {p: CL_TARGETS[p] + 0.004 for p in POINTS}       # D1 ratio ~0.026
        cl_do = dict(fm10["CL"])

        def build(tag, J_base, J_opt, **kw):
            root = os.path.join(tmp, tag)
            os.makedirs(root)
            return _synth_arm(root, J_base, J_opt, cl_base=on_target,
                              cl_opt=on_target, cl_ez=small,
                              J_do=0.036964341844, cl_do=cl_do, **kw)

        def graded(root, **kw):
            base = dict(arm_dir=root, datum_epoch=0, inherited=inh, fm10=fm10,
                        core_min=10.0, rc=0, runscript_path=rs, log_path=lg)
            base.update(kw)
            return grade_fm12(**base)

        # (a) the gain SURVIVES -- R_fresh sits on R_def exactly
        Jb = 0.0306416314389976151
        Jo = Jb * (inh["Jf"] / inh["J0"])
        g = graded(build("survive", Jb, Jo))
        check("G1 PASSES when R_fresh sits on R_def", g["G1"], True)
        check("... and the arm's label is PASS", g["label"], LABEL_PASS)
        check("... and no GCI is claimed anywhere",
              any("GCI" in s for s in g["does_not_claim"]), True)
        # (b) the gain is GONE -- R_fresh = 1.0
        g = graded(build("gone", Jb, Jb))
        check("G1 FAILS when R_fresh = 1.0", g["G1"], False)
        check("... and the arm's label is GATE FAIL", g["label"], LABEL_GATE_FAIL)
        check("... and the withdrawal is stated as a FINDING",
              any("WITHDRAWN" in s for s in g["findings"]), True)
        # (c) an UNTRIMMED side -- G2 fails and the arm is NOT A RESULT
        root = os.path.join(tmp, "untrimmed")
        os.makedirs(root)
        _synth_arm(root, Jb, Jo, cl_base={p: CL_TARGETS[p] + 0.15 for p in POINTS},
                   cl_opt=on_target, cl_ez=small, J_do=0.036964341844, cl_do=cl_do)
        g = graded(root)
        check("G2 FAILS on a side that flew 0.15 CL off target", g["G2"], False)
        check("... and an untrimmed side makes the ARM NOT A RESULT",
              g["label"], LABEL_NOT_A_RESULT)
        # (d) D2 fails -- Do does not reproduce FM10
        root = os.path.join(tmp, "d2fail")
        os.makedirs(root)
        _synth_arm(root, Jb, Jo, cl_base=on_target, cl_opt=on_target,
                   cl_ez=small, J_do=0.05, cl_do=cl_do)
        g = graded(root)
        check("D2 FAILS when Do does not reproduce FM10's J", g["D2"], False)
        check("... and that is NOT A RESULT for the WHOLE arm",
              g["label"], LABEL_NOT_A_RESULT)
        # (e) D1's two branches
        root = os.path.join(tmp, "d1big")
        os.makedirs(root)
        _synth_arm(root, Jb, Jo, cl_base=on_target, cl_opt=on_target,
                   cl_ez=dict(fm10["CL"]), J_do=0.036964341844, cl_do=cl_do)
        g = graded(root)
        check("D1 FAILS when the zero-shape excess EQUALS FM10's",
              g["D1"], False)
        check("... and its ratio is 1.0 to twelve places",
              round(g["D1_detail"]["ratio"], 12), 1.0)
        g = graded(build("d1small", Jb, Jo))
        check("D1 PASSES when the zero-shape excess is a small fraction",
              g["D1"], True)
        # (f) the mesh gate, driven by a mesh the solver did NOT load
        root = os.path.join(tmp, "wrongmesh")
        os.makedirs(root)
        _synth_arm(root, Jb, Jo, cl_base=on_target, cl_opt=on_target,
                   cl_ez=small, J_do=0.036964341844, cl_do=cl_do,
                   loaded_wrong=True)
        g = graded(root)
        check("M1 FAILS when the loaded mesh is not the generated mesh",
              g["M1"], False)
        check("... and that is NOT A RESULT", g["label"], LABEL_NOT_A_RESULT)
        # (g) the wall gate, driven by a wall the DV set moved
        root = os.path.join(tmp, "warped")
        os.makedirs(root)
        _synth_arm(root, Jb, Jo, cl_base=on_target, cl_opt=on_target,
                   cl_ez=small, J_do=0.036964341844, cl_do=cl_do, warp_zo=True)
        g = graded(root)
        check("W1 FAILS when the solve-phase DV set moved the wall",
              g["W1"], False)
        check("... and that is NOT A RESULT", g["label"], LABEL_NOT_A_RESULT)
        # (h) Q1 -- REPORTED, NAMED, and it does NOT flip the label
        root = os.path.join(tmp, "nonorth")
        os.makedirs(root)
        _synth_arm(root, Jb, Jo, cl_base=on_target, cl_opt=on_target,
                   cl_ez=small, J_do=0.036964341844, cl_do=cl_do, nonorth=79.21)
        g = graded(root)
        check("Q1 SEES a breach of DAFoam's own declared 70.0",
              g["Q1_reported_not_gated"], False)
        check("... and NAMES it in findings",
              any("MESH QUALITY" in s for s in g["findings"]), True)
        check("... and does NOT flip the label, exactly as registered",
              g["label"], LABEL_PASS)
        # (i) the cap -- REPORTED, never enforced by stopping (directive #17)
        g = graded(build("capped", Jb, Jo), core_min=CAP_CORE_MIN * 2)
        check("a cap crossing is NOT A RESULT", g["label"], LABEL_NOT_A_RESULT)
        check("... and the cap is reported, not raised",
              g["H4_detail"]["cap_core_min"], CAP_CORE_MIN)
        # (j) a non-zero rc
        g = graded(build("rcfail", Jb, Jo), rc=137)
        check("rc != 0 is NOT A RESULT", g["label"], LABEL_NOT_A_RESULT)

        # ==== THE READER REPAIR, AGAINST THE REAL ANCHOR ====================
        # FM11's _J tried ("obj","J","fun","weighted_CD") and the real record's
        # key is `obj.J`, a one-element list -- so the emitted command REFUSED
        # on the very file it was written to read, and the selftest never saw
        # it because it ran on --evals SYNTHETIC.  THIS CONTROL READS THE REAL
        # FILE.  If the anchor is not on disk, the control FAILS; it does not
        # quietly skip, because a skipped control is how that defect survived.
        check("the real evals anchor is on disk", os.path.isfile(EVALS_DEFAULT), True)
        if os.path.isfile(EVALS_DEFAULT):
            real = load_inherited(EVALS_DEFAULT)
            check("load_inherited READS THE REAL RECORD -- not a synthetic stand-in",
                  real["evals_md5"], EVALS_MD5)
            check("...out of the key the record actually uses, `obj.J`",
                  (real["J0_basis"], real["Jf_basis"]),
                  ("the record's own obj.J", "the record's own obj.J"))
            check("...and it reproduces R_def to twelve places",
                  "%.12f" % (real["Jf"] / real["J0"]), "0.752677270941")
            check("...and the gain to six", "%.6f" % (100 * (1 - real["Jf"] / real["J0"])),
                  "24.732273")
        # the one-element unwrap, driven in BOTH directions
        check("a one-element list IS the scalar", _scalar([1.5], "x"), 1.5)
        check("a bare number is unchanged", _scalar(1.5, "x"), 1.5)
        for bad, why in (([1.0, 2.0], "a two-element vector"),
                         ([], "an empty list")):
            try:
                _scalar(bad, "x")
                check("%s refuses" % why, "no refusal", "Refusal")
            except Refusal as e:
                check("%s -> REFUSE_J_NOT_SCALAR, never element [0]" % why,
                      str(e).startswith("REFUSE_J_NOT_SCALAR"), True)
        # and the FM11 chain is shown to FAIL on the real key shape, so the
        # repair is demonstrated against the defect and not merely asserted
        fu_real = {"obj.J": [0.030641631438997615],
                   "cl04.aero_post.functionals.CL": [0.4]}
        check("FM11's fallback chain finds NOTHING in the real funcs dict -- "
              "which is the REFUSE_NO_J_IN_RECORD that blocked its grader",
              [k for k in ("obj", "J", "fun", "weighted_CD") if k in fu_real], [])
        check("...and FM12's chain finds `obj.J`",
              [k for k in ("obj.J", "obj", "J", "fun", "weighted_CD")
               if k in fu_real], ["obj.J"])

        # ==== M0b / M0o / R1, EACH DRIVEN TO ITS FAILING SIDE ===============
        g = graded(build("m0ok", Jb, Jo))
        check("M0b and M0o both PASS on a well-formed arm",
              (g["M0b"], g["M0o"]), (True, True))
        check("...and R1 PASSES at exactly zero on 40209/40209 points",
              (g["R1"], g["R1_verdict"]), (True, LABEL_PASS))
        check("...and R1 is STATED as a finding, not left as a footnote",
              any(s.startswith("R1 PASS") for s in g["findings"]), True)
        check("...and the arm's label is PASS", g["label"], LABEL_PASS)
        # M0b fails via the read-back limb
        root = os.path.join(tmp, "m0bfail")
        os.makedirs(root)
        _synth_arm(root, Jb, Jo, cl_base=on_target, cl_opt=on_target, cl_ez=small,
                   J_do=0.036964341844, cl_do=cl_do, readback_ok=False)
        g = graded(root)
        check("M0b FAILS when the mesh the SOLVER READ is not the generated mesh",
              g["M0b"], False)
        check("... and that is NOT A RESULT", g["label"], LABEL_NOT_A_RESULT)
        # M0o fails -- the Zo mesh did not differ from base
        root = os.path.join(tmp, "m0ofail")
        os.makedirs(root)
        _synth_arm(root, Jb, Jo, cl_base=on_target, cl_opt=on_target, cl_ez=small,
                   J_do=0.036964341844, cl_do=cl_do, m0o_differs=False)
        g = graded(root)
        check("M0o FAILS when the Zo mesh does not differ from base -- the gate "
              "FM11 had, at the strength FM11 had it",
              g["M0o"], False)
        check("... and that is NOT A RESULT", g["label"], LABEL_NOT_A_RESULT)
        # THE GATES ARE NOT INTERCHANGEABLE: Zb gated by M0o, or Zo by M0b,
        # REFUSES.  This is what stops a future edit from writing one relaxed
        # gate and pointing both sub-arms at it.
        for sa, wrong in (("Zb", "M0o"), ("Zo", "M0b")):
            root = os.path.join(tmp, "swap%s" % sa)
            os.makedirs(root)
            _synth_arm(root, Jb, Jo, cl_base=on_target, cl_opt=on_target,
                       cl_ez=small, J_do=0.036964341844, cl_do=cl_do,
                       m0_gate_wrong=(sa, wrong))
            try:
                graded(root)
                check("%s gated by %s refuses" % (sa, wrong), "no refusal", "Refusal")
            except Refusal as e:
                check("%s gated by %s -> REFUSE_WRONG_M0_GATE -- one relaxed "
                      "gate cannot be pointed at both sub-arms" % (sa, wrong),
                      str(e).startswith("REFUSE_WRONG_M0_GATE"), True)
        # R1 fails -- and does NOT flip the label
        root = os.path.join(tmp, "r1fail")
        os.makedirs(root)
        _synth_arm(root, Jb, Jo, cl_base=on_target, cl_opt=on_target, cl_ez=small,
                   J_do=0.036964341844, cl_do=cl_do, r1_diff=3.0e-7,
                   r1_ident=40100)
        g = graded(root)
        check("R1 FAILS on a 3e-7 m drift", (g["R1"], g["R1_verdict"]),
              (False, LABEL_GATE_FAIL))
        check("...and NAMES it in findings",
              any("R1 GATE FAIL" in s for s in g["findings"]), True)
        check("...and does NOT flip the arm's label, exactly as registered",
              g["label"], LABEL_PASS)
        # R1's md5 half is WITHDRAWN when a gzip MTIME field is not zero
        root = os.path.join(tmp, "r1gzip")
        os.makedirs(root)
        _synth_arm(root, Jb, Jo, cl_base=on_target, cl_opt=on_target, cl_ez=small,
                   J_do=0.036964341844, cl_do=cl_do, r1_gzip=False)
        g = graded(root)
        check("R1 WITHDRAWS its md5 claim when a gzip MTIME field is not zero",
              g["R1_detail"]["md5_claim_admissible"], False)
        check("...and still passes on the POINT measurement alone", g["R1"], True)
        check("...and says so", "withdrawn" in g["R1_detail"]["verdict_note"], True)
        # an ABSENT R1 is PENDING, never a pass
        root = os.path.join(tmp, "nor1")
        os.makedirs(root)
        _synth_arm(root, Jb, Jo, cl_base=on_target, cl_opt=on_target, cl_ez=small,
                   J_do=0.036964341844, cl_do=cl_do)
        _strip_r1(root)
        try:
            graded(root)
            check("a missing R1 refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("a registered gate with no measurement -> REFUSE_MISSING_R1",
                  str(e).startswith("REFUSE_MISSING_R1"), True)

        # ---- THE PLANTED CONTROL, driven live ------------------------------
        root = build("plant", Jb, Jo)
        kw = dict(arm_dir=root, datum_epoch=0, inherited=inh, fm10=fm10,
                  core_min=10.0, rc=0, runscript_path=rs, log_path=lg)
        pc = live_plant_check(kw, LABEL_PASS)
        check("every planted perturbation is SEEN by the grader",
              pc["all_seen"], True)
        check("the CD plant moves the graded ratio",
              pc["plants"][0]["R_after"] != pc["plants"][0]["R_before"], True)
        # ... and the control itself is driven to its FAILING side: a grader
        # that ignores the plant must be REFUSED, not merely reported.
        saved = globals()["grade_fm12"]

        def _blind(**kwargs):
            kwargs.pop("_plant", None)
            return saved(**kwargs)      # the REAL grader, captured before the
                                        # patch; calling the global here would
                                        # call the patch and recurse
        try:
            globals()["grade_fm12"] = _blind
            try:
                live_plant_check(kw, LABEL_PASS)
                check("a BLIND grader is refused", "no refusal", "Refusal")
            except Refusal as e:
                check("a blind grader -> REFUSE_PLANT_UNSEEN",
                      str(e).startswith("REFUSE_PLANT_UNSEEN"), True)
        finally:
            globals()["grade_fm12"] = saved

        # ---- main() ON ITS OWN CLI, which is the clause 22.4.2 repair ------
        outp = os.path.join(tmp, "verdict.json")
        argv = ["--item", "FM13", "--arm-dir", root,
                "--datum-file", os.path.join(tmp, "datum"),
                "--core-min", "10.0", "--rc", "0", "--log", lg,
                "--evals", "SYNTHETIC", "--fm10-record", "SYNTHETIC",
                "--runscript", rs, "--out", outp]
        open(os.path.join(tmp, "datum"), "w").write("0\n")
        check("main() on the launcher's own argument shape returns 0",
              main(argv), 0)
        check("... and it WROTE the verdict file", os.path.isfile(outp), True)
        check("... and the verdict is the one the function gave",
              json.load(open(outp))["label"], LABEL_PASS)
        check("--item accepts EVERY registered arm id, so a re-run id cannot "
              "fall through argparse (L-570)",
              all(a in ARM_IDS for a in ("FM13", "FM13R2", "FM13R3")), True)
        # ARM-ID COLLISION, NAMED RATHER THAN INHERITED SILENTLY.
        # PREREGISTRATION_FM11_MATCHED_LIFT.md:349 registers FM13 as one of
        # FM11's re-run ids, and d6r2c_fm11_run_arm.sh:99 and :671 will launch
        # it under FM11's cap.  FM11 is graded BLOCKED.  This document ALSO
        # registers FM13.  The two cannot be separated by arm id, so they are
        # separated by ROOT and by the ledger's ITEM= line, and the collision is
        # asserted here so it can never be discovered instead of read.
        check("this document registers FM13, and so does FM11 -- the collision "
              "is REGISTERED, and the two are separated by run root and by the "
              "ledger ITEM= line, never by arm id alone",
              "FM13" in ARM_IDS, True)
        check("...and FM12's OWN ids are NOT registered here, so a launcher that "
              "passed FM12 is refused rather than graded under a registration "
              "that is not this one",
              any(a in ARM_IDS for a in ("FM12", "FM12R2", "FM12R3")), False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("D6R2C_FM12_GRADE SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", n))
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# MAIN -- and this entry point is REACHABLE FROM THE PRE-FREEZE CHECK
# ---------------------------------------------------------------------------

def build_parser():
    ap = argparse.ArgumentParser(description="Grade arm FM12 -- the comparison "
                                             "at matched lift.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--item", choices=ARM_IDS)
    ap.add_argument("--arm-dir")
    ap.add_argument("--evals", default=EVALS_DEFAULT)
    ap.add_argument("--fm10-record", default=FM10_RECORD_DEFAULT)
    ap.add_argument("--runscript", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "d6r2c_opt_runScript.py"))
    ap.add_argument("--datum-file")
    ap.add_argument("--core-min", type=float)
    ap.add_argument("--rc", type=int)
    ap.add_argument("--log", help="the arm log: H4's ONLY source of convergence "
                                  "evidence, and an absent one REFUSES")
    ap.add_argument("--out")
    ap.add_argument("--print-cap", metavar="ARM",
                    help="print the registered cap in core-minutes for ARM and "
                         "exit.  THE LAUNCHER CALLS THIS rather than carrying "
                         "its own literal.")
    ap.add_argument("--print-cost", action="store_true",
                    help="print the registered cost breakdown and exit")
    return ap


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)

    if a.print_cap:
        if a.print_cap not in CAPS:
            return 64
        print("%.3f" % CAPS[a.print_cap])
        return 0
    if a.print_cost:
        print("D6R2C_FM13_COST core_min_per_objective_evaluation=%.3f "
              "core_min_per_gradient_evaluation=%.3f n_gradient_evaluations=%d "
              "prediction_core_min=%.3f cap_core_min=%.3f "
              "usd_prediction_DERIVED=%.4f usd_cap_DERIVED=%.4f"
              % (CORE_MIN_PER_OBJ_EVAL, CORE_MIN_PER_GRAD_EVAL,
                 N_GRAD_EVALS_THIS_ARM, PREDICTION_CORE_MIN, CAP_CORE_MIN,
                 PREDICTION_CORE_MIN / 60.0 * RATE_USD_PER_CORE_H,
                 CAP_CORE_MIN / 60.0 * RATE_USD_PER_CORE_H))
        return 0
    if a.selftest:
        return selftest()
    for need in ("item", "arm_dir", "datum_file", "core_min", "rc", "log"):
        if getattr(a, need) is None:
            ap.error("--%s is required when grading" % need.replace("_", "-"))
    try:
        with open(a.datum_file) as fh:
            datum = int(float(fh.read().strip()))
        if a.evals == "SYNTHETIC":
            inherited = {"J0": 0.0306416314389976151,
                         "Jf": 0.0230632595286777639,
                         "J0_basis": "SYNTHETIC -- selftest only",
                         "Jf_basis": "SYNTHETIC -- selftest only",
                         "evals_md5": "SYNTHETIC", "n_J0": N_J0, "n_Jf": N_JF}
        else:
            inherited = load_inherited(a.evals)
        if a.fm10_record == "SYNTHETIC":
            E = {"cl04": 0.149286, "cl05": 0.151566, "cl06": 0.152398}
            fm10 = {"E_star": E,
                    "CL": {p: CL_TARGETS[p] + E[p] for p in POINTS},
                    "J": 0.036964341844, "record": "SYNTHETIC",
                    "role": "SYNTHETIC -- selftest only"}
        else:
            fm10 = load_fm10(a.fm10_record)
        kw = dict(arm_dir=a.arm_dir, datum_epoch=datum, inherited=inherited,
                  fm10=fm10, core_min=a.core_min, rc=a.rc,
                  runscript_path=a.runscript, log_path=a.log)
        rec = grade_fm12(**kw)
        rec["planted_control"] = live_plant_check(kw, rec["label"])
        rec["arm_id"] = a.item
    except Refusal as e:
        print("D6R2C_FM12_GRADE REFUSED\n%s" % e)
        return 2
    out = a.out or os.path.join(os.path.dirname(a.arm_dir.rstrip("/")),
                                "%s_GRADE.json" % a.item)
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
    g1 = rec["G1_detail"]
    print("D6R2C_FM12_GRADE item=%s label=%s R_fresh=%.9g R_def=%.9g "
          "window=[%.6f, %.6f] J_base=%.9g J_opt=%.9g"
          % (a.item, rec["label"], g1["R_fresh"], g1["R_def"],
             g1["window"][0], g1["window"][1], g1["J_base_fresh"],
             g1["J_opt_fresh"]))
    print("D6R2C_FM12_GRADE G1=%s G2=%s D1=%s D2=%s M0b=%s M0o=%s M1=%s W1=%s "
          "H4=%s Q1_no_breach=%s"
          % (rec["G1"], rec["G2"], rec["D1"], rec["D2"], rec["M0b"],
             rec["M0o"], rec["M1"], rec["W1"], rec["H4"],
             rec["Q1_reported_not_gated"]))
    r1 = rec["R1_detail"]
    print("D6R2C_FM12_R1 verdict=%s max_point_difference_m=%.17g "
          "points_identical=%s/%s elapsed_days=%.3f md5_identical=%s "
          "md5_claim_admissible=%s  (R1 NEVER flips this arm's label)"
          % (r1["verdict"], r1["max_point_difference_from_base_m"],
             r1.get("n_points_identical"), r1.get("n_points"),
             r1.get("elapsed_days") or 0.0, r1.get("md5_identical"),
             r1["md5_claim_admissible"]))
    for f in rec["findings"]:
        print("D6R2C_FM12_FINDING %s" % f)
    print("D6R2C_FM12_GRADE verdict=%s written=%s" % (rec["label"], out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
