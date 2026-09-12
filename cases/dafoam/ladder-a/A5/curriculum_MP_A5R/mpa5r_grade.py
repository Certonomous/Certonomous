#!/usr/bin/env python3
"""
CURRICULUM MP_A5 -- THE COMPARATOR.  A5 U-bend, 3D incompressible MULTIPOINT
pressure-loss minimisation over three inlet velocities.

THIS FILE IS THE GRADING PATH AND IS FROZEN WITH THE PRE-REGISTRATION, IN THE
SAME COMMIT.  Nothing below chooses a gate, a threshold, a band or a label; all
of those are read out of the registered constants in section 0, which are the
same literals the pre-registration carries.

READER DISCIPLINE, carried from cases/dafoam/ladder-a/A5/curriculum_A5P2/a5p2_grade.py:
  (1) `initRes` ONLY, NEVER `finalRes` (N-D44).  DAFoam's accepted quantity is the
      INITIAL residual of the outer iteration; `finalRes` is the inner linear
      solve's residual and is small even when the outer loop has not converged.
  (2) every number a gate reads comes from a JSON record the instrument wrote, or
      from a log line matched by one of the four regexes in section 1.  Nothing is
      graded from a human-readable summary.
  (3) EVERY reader is proved able to see a NON-ZERO before any zero it returns is
      believed (CLAUDE.md rule 3).  Section 5 plants a known perturbation into a
      scratch copy BY LINE INDEX, reads it back through the SAME reader, and this
      comparator REFUSES (exit 2) if the reader cannot see it.  A second, opposite
      plant proves the gate itself can FAIL -- a reader that always passes is as
      blind as one that always returns zero.

EXIT STATUS IS NOT THE VERDICT.  exit 0 = the comparator ran and produced a
verdict (which may be GATE FAIL or NOT A RESULT).  exit 2 = the comparator
REFUSED: a control failed, or a required artefact is missing.  A refusal is never
degraded into a verdict.

SUBMISSIONS PARKED.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

# =============================================================================
# 0.  THE REGISTERED CONSTANTS.  Every literal here appears in PREREGISTRATION.md.
# =============================================================================
SCENARIOS = ["point0", "point1", "point2"]
U0S = [6.30, 8.40, 10.50]
WEIGHTS = [0.25, 0.50, 0.25]

ARMS = ["B", "O", "E"]
ARMS_GATED_ON_CONVERGENCE = ["B", "E"]     # G-CONV.  O is REPORTED, never gated.

# G-CONV: the registered accept floor for the primal, on `p` initRes.
#
# MP_A5R-1  THE WHOLE REASON THIS SUCCESSOR EXISTS.  MP_A5 registered 1.0e-06,
# calibrated from A5P2's measured 1.448577e-08 -- WITHOUT NOTICING THAT A5P2's
# TREE RUNS `endTime 5000` WHILE THE TREE MP_A5 STAGED FROM RUNS `endTime 1000`.
# A floor calibrated on a 5x-longer raw-solver run was applied to the 1000-
# iteration optimisation tree, and MP_A5's arm B duly read 1.556e-06 / 9.596e-07
# / 1.026e-06 -- two of three above the floor -- and graded GATE FAIL.  That
# GATE FAIL stands and is not relaxed; this item is the FIX, not the excuse.
#
# THIS ITEM STAGES AT `endTime 5000`, THE SAME LENGTH THE FLOOR WAS MEASURED AT,
# and the launcher applies AND READS BACK that value, so the floor and the tree
# it grades cannot drift apart again.  The floor stays at 1.0e-06 -- deliberately
# NOT tightened to A5P2's 1.448577e-08 -- because 1e-06 is now TWO DECADES of
# headroom above a value measured on a matching tree, and re-using the identical
# literal keeps this item's gate comparable to its predecessor's row for row.
P_INITRES_FLOOR = 1.0e-06
# MP_A5R-1  the staged primal length, asserted by the launcher against the tree.
REGISTERED_END_TIME = 5000
# G-J0: the structural identity |J(baseline) - 1| must hold to this.
J0_TOL = 1.0e-06
# G-MP1: the registered PASS band for the composite objective at the endpoint.
J_END_BAND = (0.94, 0.98)
# G-MESH: the case's own checkMeshThreshold { maxNonOrth 70; }.
MAXNONORTH_LIMIT = 70.0
# G-NONORTHO-IDENTITY: three scenarios share one deformed mesh.
NONORTHO_IDENTITY_TOL = 1.0e-09
# G-TRIV: the single-point endpoint this multipoint endpoint is compared against.
SINGLEPOINT_DV = "/home/ubuntu/certonomous-runs/CURRICULUM-D9SUCCESSOR-a5-ubend-opt/opt_dv.json"
SINGLEPOINT_L2_RECORDED = 0.1622           # D9successor/RESULTS.md section 4
TRIV_REL_THRESHOLD = 0.02 / 0.1622         # registered as an ABSOLUTE l2 of 0.02
TRIV_ABS_THRESHOLD = 0.02

PLANT = 1.234e-03                          # the planted perturbation
PLANT_FAIL = 1.0e-02                       # a value that MUST fail G-CONV

FATAL_TOKENS = [
    "Foam::error",
    "Segmentation fault",
    "MPI_ABORT",
    "Primal solution failed",
    "AnalysisError",
]

# =============================================================================
# 1.  READERS.  Four regexes; nothing else parses a log.
# =============================================================================
RE_INITRES = re.compile(r"^\s*(\S+) initRes:\s*([-+0-9.eEdD]+)")
RE_SEGMENT = re.compile(r"^Printing Primal Residual Statistics")
RE_NONORTH = re.compile(r"Mesh non-orthogonality Max:\s*([-+0-9.eE]+)")
RE_END = re.compile(r"^End\s*$")


def read_lines(path):
    with open(path, errors="replace") as f:
        return f.read().splitlines()


def p_initres_per_segment(lines):
    """[(segment_index, last p initRes in that segment)] for every primal segment.

    A segment ENDS at the `Printing Primal Residual Statistics` banner DAFoam
    prints when a primal finishes, so a multipoint run_model over three
    scenarios yields three segments, in scenario declaration order.
    """
    out = []
    seg = 0
    last = None
    for ln in lines:
        m = RE_INITRES.match(ln)
        if m and m.group(1) == "p":
            try:
                last = float(m.group(2).replace("D", "E").replace("d", "e"))
            except ValueError:
                pass
        if RE_SEGMENT.match(ln):
            out.append((seg, last))
            seg += 1
            last = None
    return out


def last_maxnonorth(lines):
    v = None
    for ln in lines:
        m = RE_NONORTH.search(ln)
        if m:
            try:
                v = float(m.group(1))
            except ValueError:
                pass
    return v


def has_end(lines):
    return any(RE_END.match(ln) for ln in lines)


def fatal_tokens_present(lines):
    hits = []
    for tok in FATAL_TOKENS:
        for ln in lines:
            if tok in ln:
                hits.append(tok)
                break
    return hits


def read_record(path):
    with open(path) as f:
        return json.load(f)


# =============================================================================
# 2.  RULE-4 COMPLETION, PER ARM.
# =============================================================================
def rule4(root, arm, stamp):
    armdir = os.path.join(root, arm)
    log = os.path.join(root, "%s_%s.log" % (arm, stamp))
    rec = os.path.join(armdir, "mpa5r_out.json")
    datum = os.path.join(armdir, "0", "U")
    cl = {}

    cl["C1_rc_value"] = clause(
        ledger_rc(root, arm) == 0,
        "ledger rc for arm %s" % arm,
        ledger_rc(root, arm),
    )
    lines = read_lines(log) if os.path.exists(log) else []
    cl["C2_terminal_marker"] = clause(has_end(lines), "an `End` line in %s" % os.path.basename(log), has_end(lines))
    cl["C3_artefact_present"] = clause(os.path.exists(rec), "the record %s" % rec, os.path.exists(rec))

    # THE AGE GUARD.  0/U is touched last at staging and so dates the run allowed
    # to produce this arm's answer.  The answer must be NEWER than it.
    if os.path.exists(rec) and os.path.exists(datum):
        ok = os.path.getmtime(rec) > os.path.getmtime(datum)
        val = "rec=%.0f datum=%.0f" % (os.path.getmtime(rec), os.path.getmtime(datum))
    else:
        ok, val = False, "rec or datum absent"
    cl["C4_age_guard"] = clause(ok, "the record newer than the arm's own 0/U", val)

    hits = fatal_tokens_present(lines)
    cl["C5_no_fatal_token"] = clause(not hits, "no fatal token in the arm log", hits)

    cl["verdict"] = "PASS" if all(c["verdict"] == "PASS" for k, c in cl.items() if k != "verdict") else "NOT A RESULT"
    return cl


def clause(ok, what, value):
    return {"verdict": "PASS" if ok else "GATE FAIL", "what": what, "value": value}


def ledger_rc(root, arm):
    """rc as the LAUNCHER recorded it, from the ledger, never re-inferred."""
    led = os.path.join(root, "ledger.txt")
    if not os.path.exists(led):
        return None
    rc = None
    for ln in read_lines(led):
        if ln.startswith("STAGE=%s " % arm):
            m = re.search(r"\brc=(-?\d+)", ln)
            if m:
                rc = int(m.group(1))
    return rc


# =============================================================================
# 3.  THE GATES.
# =============================================================================
def gate_conv(root, arm, stamp):
    """G-CONV: every scenario's `p` initRes at the end of its primal segment is
    below the registered floor.  Reported per segment."""
    log = os.path.join(root, "%s_%s.log" % (arm, stamp))
    if not os.path.exists(log):
        return {"verdict": "NOT A RESULT", "reason": "arm log absent: %s" % log}
    segs = p_initres_per_segment(read_lines(log))
    if len(segs) != len(SCENARIOS):
        return {
            "verdict": "NOT A RESULT",
            "reason": "expected %d primal segments, the log carries %d" % (len(SCENARIOS), len(segs)),
            "segments": segs,
        }
    per = {}
    allok = True
    for i, (_, v) in enumerate(segs):
        if v is None:
            per[SCENARIOS[i]] = {"verdict": "NOT A RESULT", "p_initRes": None}
            allok = False
            continue
        ok = v < P_INITRES_FLOOR
        per[SCENARIOS[i]] = {"verdict": "PASS" if ok else "GATE FAIL", "p_initRes": v, "floor": P_INITRES_FLOOR}
        allok = allok and ok
    return {"verdict": "PASS" if allok else "GATE FAIL", "floor": P_INITRES_FLOOR, "per_scenario": per}


def gate_endtime(root, arm, stamp):
    """G-ENDTIME -- MP_A5R-1.  THE GATE THAT MAKES THE PREDECESSOR'S ERROR
    UNREPEATABLE.  MP_A5's floor and MP_A5's tree disagreed about how long the
    primal runs, and nothing in the grading path could see it: the floor was
    measured at `endTime 5000` and the tree ran `endTime 1000`.  This gate reads
    the LAST `Time = ` each primal segment actually reached and requires it to
    equal the registered length the floor was calibrated at.  A tree that stages
    short now fails a gate instead of silently failing the floor."""
    log = os.path.join(root, "%s_%s.log" % (arm, stamp))
    if not os.path.exists(log):
        return {"verdict": "NOT A RESULT", "reason": "arm log absent: %s" % log}
    lines = read_lines(log)
    seg, last_t, reached = 0, None, []
    for ln in lines:
        m = re.match(r"^Time = (\S+)\s*$", ln)
        if m:
            try:
                last_t = float(m.group(1))
            except ValueError:
                pass
        if RE_SEGMENT.match(ln):
            reached.append(last_t)
            seg += 1
            last_t = None
    if not reached:
        return {"verdict": "NOT A RESULT", "reason": "no primal segment finished in %s" % os.path.basename(log)}
    ok = all(t is not None and abs(t - REGISTERED_END_TIME) < 1e-9 for t in reached)
    return {
        "verdict": "PASS" if ok else "GATE FAIL",
        "registered_endTime": REGISTERED_END_TIME,
        "reached_per_segment": reached,
        "why_this_gate_exists": "MP_A5 calibrated its floor at endTime 5000 and staged endTime 1000; "
                                "nothing in its grading path could see the mismatch",
    }


def gate_expr(rec):
    """G-EXPR: the objective expression the instrument actually assembled is the
    registered formula, rebuilt here from the registered weights and the record's
    own normalisers, compared CHARACTER FOR CHARACTER."""
    norms = rec.get("norms")
    if not norms or len(norms) != 3:
        return {"verdict": "NOT A RESULT", "reason": "record carries no three normalisers"}
    want = "val = " + " + ".join(
        "%.17g*(TP1_%d - TP2_%d)/%.17g" % (WEIGHTS[i], i, i, float(norms[i])) for i in range(3)
    )
    got = rec.get("obj_expr", "")
    return {
        "verdict": "PASS" if got == want else "GATE FAIL",
        "expected": want,
        "recorded": got,
    }


def gate_j0(rec_b, norms):
    """G-J0: with the normalisers taken from the baseline and sum(w)=1, the
    composite at the baseline design is EXACTLY 1.0 by construction.  This gate
    recomputes it from arm B's own per-scenario dP, so a mis-assembled objective
    cannot pass silently."""
    dp = rec_b.get("dP")
    if not dp or len(dp) != 3:
        return {"verdict": "NOT A RESULT", "reason": "arm B carries no three-scenario dP"}
    j0 = sum(WEIGHTS[i] * float(dp[i]) / float(norms[i]) for i in range(3))
    return {
        "verdict": "PASS" if abs(j0 - 1.0) <= J0_TOL else "GATE FAIL",
        "J0_recomputed": j0,
        "tol": J0_TOL,
    }


def gate_mp1(rec_b, rec_e, norms):
    """G-MP1, THE HEADLINE: the composite weighted fractional pressure loss at the
    endpoint, recomputed by THIS comparator from arm E's per-scenario dP and arm
    B's normalisers.  The instrument's own OBJ_val is reported beside it and is
    NOT what is graded -- an instrument that computes its own headline can round it."""
    dpe = rec_e.get("dP")
    if not dpe or len(dpe) != 3:
        return {"verdict": "NOT A RESULT", "reason": "arm E carries no three-scenario dP"}
    j = sum(WEIGHTS[i] * float(dpe[i]) / float(norms[i]) for i in range(3))
    lo, hi = J_END_BAND
    inband = lo <= j <= hi
    return {
        "verdict": "PASS" if inband else "GATE FAIL",
        "J_end_recomputed": j,
        "band": [lo, hi],
        "composite_reduction_pct": 100.0 * (1.0 - j),
        "instrument_OBJ_val_REPORTED_NOT_GRADED": rec_e.get("OBJ_val"),
    }


def gate_scen_all(rec_b, rec_e):
    """G-SCEN-ALL: multipoint's whole claim is that EVERY operating point improves.
    One scenario going backwards is a GATE FAIL even if the weighted sum falls."""
    dpb, dpe = rec_b.get("dP"), rec_e.get("dP")
    if not dpb or not dpe or len(dpb) != 3 or len(dpe) != 3:
        return {"verdict": "NOT A RESULT", "reason": "a dP triple is missing"}
    per = {}
    allok = True
    for i, sc in enumerate(SCENARIOS):
        d = float(dpe[i]) - float(dpb[i])
        ok = d < 0.0
        per[sc] = {
            "verdict": "PASS" if ok else "GATE FAIL",
            "U0": U0S[i],
            "dP_baseline": float(dpb[i]),
            "dP_endpoint": float(dpe[i]),
            "reduction_pct": 100.0 * (1.0 - float(dpe[i]) / float(dpb[i])),
        }
        allok = allok and ok
    return {"verdict": "PASS" if allok else "GATE FAIL", "per_scenario": per}


def gate_mesh(root, stamp):
    """G-MESH: the RAW checkMesh maxNonOrth at the endpoint, from the E arm's
    primal-startup checkMesh block -- D9successor's proven mechanism (it measured
    69.2937 there against this same 70.0 limit)."""
    log = os.path.join(root, "E_%s.log" % stamp)
    if not os.path.exists(log):
        return {"verdict": "NOT A RESULT", "reason": "arm E log absent"}
    v = last_maxnonorth(read_lines(log))
    if v is None:
        return {"verdict": "NOT A RESULT", "reason": "no `Mesh non-orthogonality Max` line in the arm E log"}
    return {
        "verdict": "PASS" if v <= MAXNONORTH_LIMIT else "GATE FAIL",
        "raw_maxNonOrth": v,
        "limit": MAXNONORTH_LIMIT,
        "d9successor_precedent": 69.2937,
    }


def gate_nonortho_identity(rec_e):
    """G-NONORTHO-IDENTITY: the three scenarios share ONE deformed mesh, so their
    three KS values must be the same number.  This is what makes it legitimate to
    register the constraint on point1 alone."""
    ks = rec_e.get("nonOrtho_KS")
    if not ks or len(ks) != 3:
        return {"verdict": "NOT A RESULT", "reason": "arm E carries no three KS values"}
    spread = max(ks) - min(ks)
    return {
        "verdict": "PASS" if spread <= NONORTHO_IDENTITY_TOL else "GATE FAIL",
        "KS_values": ks,
        "spread": spread,
        "tol": NONORTHO_IDENTITY_TOL,
    }


def gate_triv(rec_o):
    """G-TRIV, THE DISCRIMINATING NEGATIVE.  Distance from D9successor's
    SINGLE-point endpoint.  REGISTERED PREDICTION: TRIVIAL -- the three Reynolds
    numbers span only 1.67x and the flow regime does not change, so the multipoint
    optimum is expected to sit within l2 0.02 of the single-point optimum.
    BOTH OUTCOMES ARE RESULTS.  Neither is a failure; this gate never makes a
    PASS into a GATE FAIL."""
    dv = rec_o.get("shapexUpper")
    if not dv:
        return {"verdict": "NOT A RESULT", "reason": "arm O carries no endpoint shapexUpper"}
    if not os.path.exists(SINGLEPOINT_DV):
        return {"verdict": "NOT A RESULT", "reason": "the single-point endpoint is not on disk: %s" % SINGLEPOINT_DV}
    sp = json.load(open(SINGLEPOINT_DV))["shapexUpper"]
    if len(sp) != len(dv):
        return {"verdict": "NOT A RESULT", "reason": "DV lengths differ: %d vs %d" % (len(dv), len(sp))}
    l2 = sum((float(a) - float(b)) ** 2 for a, b in zip(dv, sp)) ** 0.5
    l2_mp = sum(float(a) ** 2 for a in dv) ** 0.5
    return {
        "status": "TRIVIAL_MULTIPOINT" if l2 <= TRIV_ABS_THRESHOLD else "NON_TRIVIAL_MULTIPOINT",
        "registered_prediction": "TRIVIAL_MULTIPOINT",
        "l2_distance_to_singlepoint": l2,
        "threshold": TRIV_ABS_THRESHOLD,
        "l2_multipoint_endpoint": l2_mp,
        "l2_singlepoint_endpoint_recorded": SINGLEPOINT_L2_RECORDED,
        "note": "REPORTED, never gated -- both outcomes are results",
    }


# =============================================================================
# 4.  THE PLANTED CONTROLS.  A zero from a reader not shown able to see a
#     non-zero is not evidence (CLAUDE.md rule 3).
# =============================================================================
def plant_into_log(src, dst, value):
    """Rewrite the LAST `p initRes:` line's value BY LINE INDEX -- never a
    regex-replace-all, which would rewrite lines the reader never reaches."""
    lines = read_lines(src)
    idx = None
    for i, ln in enumerate(lines):
        m = RE_INITRES.match(ln)
        if m and m.group(1) == "p":
            idx = i
    if idx is None:
        return False
    lines[idx] = "p initRes: %.7e finalRes: 1.0e-12 nIters: 1" % value
    with open(dst, "w") as f:
        f.write("\n".join(lines) + "\n")
    return True


def control_log_reader(root, arm, stamp):
    """CONTROL A -- the log reader must SEE a planted non-zero, and CONTROL B --
    the gate must FAIL on a planted failing value.  A reader that always returns
    the same thing is blind in one direction or the other."""
    log = os.path.join(root, "%s_%s.log" % (arm, stamp))
    if not os.path.exists(log):
        return (False, "arm %s log absent; the control cannot be run" % arm)
    unplanted = p_initres_per_segment(read_lines(log))
    if not unplanted:
        return (False, "the UNPLANTED read found NO `p initRes:` segments at all in arm %s" % arm)

    tmp = tempfile.mkdtemp(prefix="mpa5_control_")
    try:
        a = os.path.join(tmp, "A.log")
        if not plant_into_log(log, a, PLANT):
            return (False, "no `p initRes:` line to plant into")
        seen = p_initres_per_segment(read_lines(a))
        if not seen or seen[-1][1] is None or abs(seen[-1][1] - PLANT) > 1e-12:
            return (False, "CONTROL A FAILED: planted %.6e, the reader read %r" % (PLANT, seen[-1][1] if seen else None))

        b = os.path.join(tmp, "B.log")
        plant_into_log(log, b, PLANT_FAIL)
        seenb = p_initres_per_segment(read_lines(b))
        if not seenb or seenb[-1][1] is None or not (seenb[-1][1] >= P_INITRES_FLOOR):
            return (False, "CONTROL B FAILED: a value of %.6e above the %.1e floor did not read back above it" % (PLANT_FAIL, P_INITRES_FLOOR))
        return (True, "CONTROL A: planted %.6e, read back %.6e.  CONTROL B: planted %.6e, read back %.6e and it IS above the %.1e floor." % (PLANT, seen[-1][1], PLANT_FAIL, seenb[-1][1], P_INITRES_FLOOR))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_record_reader(root, arm):
    """CONTROL C -- the JSON reader must SEE a planted non-zero in `dP[0]`."""
    rec = os.path.join(root, arm, "mpa5r_out.json")
    if not os.path.exists(rec):
        return (False, "arm %s record absent; the control cannot be run" % arm)
    d = read_record(rec)
    if not d.get("dP"):
        return (False, "the UNPLANTED read found no `dP` in arm %s" % arm)
    tmp = tempfile.mkdtemp(prefix="mpa5_controlc_")
    try:
        p = os.path.join(tmp, "planted.json")
        d2 = json.loads(json.dumps(d))
        d2["dP"][0] = PLANT
        with open(p, "w") as f:
            json.dump(d2, f)
        back = read_record(p)
        if abs(float(back["dP"][0]) - PLANT) > 1e-15:
            return (False, "CONTROL C FAILED: planted %.6e into dP[0], the reader read %r" % (PLANT, back["dP"][0]))
        return (True, "CONTROL C: planted %.6e into dP[0], read back %.6e." % (PLANT, back["dP"][0]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# =============================================================================
# 5.  MAIN.
# =============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--stamp", required=True)
    ap.add_argument("--cpuset", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    root, stamp = a.root, a.stamp

    out = {
        "item": "MP_A5R",
        "what": "A5 U-bend, 3D INCOMPRESSIBLE MULTIPOINT pressure-loss minimisation over three inlet velocities",
        "root": root,
        "stamp": stamp,
        "cpuset": a.cpuset,
        "registered": {
            "scenarios": SCENARIOS,
            "U0s": U0S,
            "weights": WEIGHTS,
            "p_initRes_floor": P_INITRES_FLOOR,
            "endTime": REGISTERED_END_TIME,
            "J_end_band": list(J_END_BAND),
            "maxNonOrth_limit": MAXNONORTH_LIMIT,
        },
        "controls": {},
        "rule4_clauses_per_arm": {},
        "gates": {},
    }

    # ---- THE CONTROLS FIRST.  A refusal is exit 2 and is never a verdict.
    okA, msgA = control_log_reader(root, "B", stamp)
    out["controls"]["A_B_log_reader_sees_a_planted_nonzero_and_a_planted_failure"] = {"passed": okA, "detail": msgA}
    okC, msgC = control_record_reader(root, "B")
    out["controls"]["C_record_reader_sees_a_planted_nonzero"] = {"passed": okC, "detail": msgC}
    if not (okA and okC):
        out["verdict"] = "REFUSED"
        emit(out, a.out)
        print("MPA5R COMPARATOR REFUSED: a planted control did not fire.  This is NOT a verdict.", file=sys.stderr)
        sys.exit(2)

    # ---- RULE 4, per arm.
    for arm in ARMS:
        out["rule4_clauses_per_arm"][arm] = rule4(root, arm, stamp)
    rule4_ok = all(out["rule4_clauses_per_arm"][x]["verdict"] == "PASS" for x in ARMS)

    # ---- the records.
    recs = {}
    for arm in ARMS:
        p = os.path.join(root, arm, "mpa5r_out.json")
        recs[arm] = read_record(p) if os.path.exists(p) else None

    # ---- G-CONV on B and E; O is REPORTED, never gated.
    for arm in ARMS_GATED_ON_CONVERGENCE:
        out["gates"]["G-CONV_%s" % arm] = gate_conv(root, arm, stamp)
        out["gates"]["G-ENDTIME_%s" % arm] = gate_endtime(root, arm, stamp)
    olog = os.path.join(root, "O_%s.log" % stamp)
    out["primal_convergence_arm_O"] = {
        "status": "REPORTED, NEVER GATED -- the endpoint is re-evaluated in arm E, which IS gated",
        "segments": len(p_initres_per_segment(read_lines(olog))) if os.path.exists(olog) else None,
    }

    norms = None
    if recs["B"] and recs["B"].get("dP"):
        norms = [float(v) for v in recs["B"]["dP"]]

    if recs["O"]:
        out["gates"]["G-EXPR"] = gate_expr(recs["O"])
    if recs["B"] and norms:
        out["gates"]["G-J0"] = gate_j0(recs["B"], norms)
    if recs["B"] and recs["E"] and norms:
        out["gates"]["G-MP1"] = gate_mp1(recs["B"], recs["E"], norms)
        out["gates"]["G-SCEN-ALL"] = gate_scen_all(recs["B"], recs["E"])
    out["gates"]["G-MESH"] = gate_mesh(root, stamp)
    if recs["E"]:
        out["gates"]["G-NONORTHO-IDENTITY"] = gate_nonortho_identity(recs["E"])
    if recs["O"]:
        out["G-TRIV"] = gate_triv(recs["O"])
        out["driver"] = {
            "driver_failed": recs["O"].get("driver_failed"),
            "driver_iter_count": recs["O"].get("driver_iter_count"),
            "obj_history_len": len(recs["O"].get("obj_history", []) or []),
            "status": "REPORTED -- a pyOptSparse SLSQP `driver_failed` on a constrained "
                      "single-DV-group run is D9's and D9successor's recorded behaviour and "
                      "is not by itself a physics verdict",
        }

    # ---- THE VERDICT.  Order is registered: rule 4 first, then the gates.
    if not rule4_ok:
        out["verdict"] = "NOT A RESULT"
        out["verdict_reason"] = "an arm failed the strict completion rule"
    else:
        gv = [g.get("verdict") for g in out["gates"].values() if isinstance(g, dict) and "verdict" in g]
        if "NOT A RESULT" in gv:
            out["verdict"] = "NOT A RESULT"
            out["verdict_reason"] = "a gate could not be evaluated on the artefacts present"
        elif "GATE FAIL" in gv:
            out["verdict"] = "GATE FAIL"
            out["verdict_reason"] = "every arm completed; at least one registered gate is outside its band"
        else:
            out["verdict"] = "PASS"
            out["verdict_reason"] = "every arm completed and every registered gate is inside its band"

    emit(out, a.out)
    print("MPA5R VERDICT: %s" % out["verdict"])
    sys.exit(0)


def emit(out, path):
    txt = json.dumps(out, indent=2, sort_keys=True)
    if path:
        with open(path, "w") as f:
            f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
