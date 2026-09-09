#!/usr/bin/env python3
"""A3FL2 COMPARATOR -- the nd-only free-conditioning-lever arm for the ONERA-M6
rung-3 `-3` adjoint stagnation.  Successor to the CONFOUNDED A3FL1 (curriculum_A3FL1,
frozen 865e7c71, NOT A RESULT | config-install crash on the invalid `KSPCalcSingularVal`
daOption).  A3FL2 DROPS that invalid diagnostic ENTIRELY: the ONLY lever is
`jacMatReOrdering: natural -> nd` inside `adjEqnOption` (a placement confirmed valid --
A3FL1's crash was solely the TOP-LEVEL KSPCalcSingularVal option, never nd).

DRAFT -- FROZEN by md5 in A3FL2_PREREGISTRATION.md section 9 by the dafoam-supervisor at
check-1, and ONLY after a GREEN pre-flight exercise (a3fl2_exercise.sh -- the A3FL1 lesson).
Computes nothing about physics; renders verdicts from the FIXED vocabulary ONLY (PASS /
GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING).

THREE LEGS, ALL under the ONE pinned image dafoam-subpclu:v1 (sha256:ba2d16ab...):
  CONTROL      = rung-2 (converging baseline) + nd (jacMatReOrdering natural->nd).  Does
                `nd` BREAK a converging solve?  Must still CONVERGE.
  BASELINE_R3  = rung-3, NATURAL ordering UNCHANGED (NO nd) -- a PURE COPY of the baseline
                runScript.  REPRODUCES the `-3` stagnation under the arm's OWN pinned image
                -- the fresh natural reference that makes the arm section-11-clean BY
                MEASUREMENT (the historical rung-3 image was not preserved; a measured
                in-arm natural baseline replaces the un-pinnable historical one).
                Expected: STAGNATION.
  TEST_R3      = rung-3 + nd (jacMatReOrdering natural->nd).  Does `nd` clear the stagnation?

WHAT CHANGED FROM A3FL1 (the confounded predecessor):
  * The `KSPCalcSingularVal` injection is GONE from both delta functions and from the
    required proofs.  A3FL1's grader REQUIRED `KSPCalcSingularVal 1;` in every leg's dump;
    A3FL2's grader does NOT -- a log reading `KSPCalcSingularVal 0` (the baseline value) is
    ACCEPTED.  The ONLY lever proof is the leg's jacMatReOrdering (nd / natural).
  * G-DIAG no longer reads an in-arm singular-value token (there is no diagnostic to emit
    one).  sMax/sMin is reported NOT_MEASURED_THIS_ARM, citing the historical MEASURED
    natural-ordering value 9.57e+10 (rung 3, PRIOR_WORK 119-120) as the reference.
    Conditioning is adjudicated by CONVERGENCE (G-CONV), never by a singular-value token.

WHAT IT GRADES (A3FL2_PREREGISTRATION.md sections 4/5/7):
  PROOFS  per leg log, before any number counts (L-40): the DAOption dump + KSP echo must
          read the leg's EXACT ordering -- `nd` for CONTROL and TEST_R3 (dump
          `jacMatReOrdering nd;` AND echo `Mat ReOrdering: nd`; a leg still reading
          `natural` did NOT apply the lever -> REFUSE), and `natural` for BASELINE_R3 (the
          baseline config UNCHANGED; a BASELINE_R3 log reading `nd` is not the natural
          baseline -> REFUSE).  ALL legs: `transonicPCOption 1;`, `adjStateOrdering cell;`,
          `ILU PC Fill Level: 0`, `GMRES Restart: 200`, no sub-LU banner.  Any missing ->
          REFUSE.  (NO KSPCalcSingularVal proof -- dropped in A3FL2.)
  G-CONV  the convergence gate.  From the terminal `**Completed**! Total iterations: T.
          PetscConvergedReason: R. <wall> s` and the residual trace `Main iteration N KSP
          Residual norm r_N`:
            CONVERGED     = R == 2 AND T < cap, on the graded objective(s).
            STAGNATION    = R < 0 at exactly the cap AND flat tail: relative residual change
                            over the last N_TAIL iters < THETA_STAG.
            BUDGET_LIMITED= R < 0 at the cap but the tail is still descending (>= THETA_STAG,
                            monotone) -- NOT a stagnation verdict.
            NOT_EVALUABLE = no terminal reason (crash/OOM before a reason).
  G-CTRL  the control leg CONVERGED on BOTH CD and CL (reason 2, below cap) -> VALID, else
          `nd` is harmful and the arm is inconclusive.
  G-BASE  BASELINE_R3 REPRODUCES the `-3` stagnation (leg STAGNATION) under the pinned
          image -> the premise/toolchain is validated; anything else (converges, budget-
          limited, crash) -> the premise is NOT validated and nd's effect cannot be
          attributed -> NOT A RESULT.
  G-DIAG  sMax/sMin reported NOT_MEASURED_THIS_ARM (A3FL2 drops the KSPCalcSingularVal
          diagnostic), citing the historical MEASURED 9.57e+10 as the reference.  Never a
          gate.  No in-arm singular-value token is required.
  G-FD    the bright line (DAFOAM_CHARTER section 2), CONDITIONAL on TEST_R3 convergence: an
          endpoint FD table, per-component band D (<= 5 %, same sign; a sign flip is GATE FAIL),
          aggregate band E (<= 5 %), plateau (middle step vs a neighbour <= 10 %), >= MIN_GRADED
          evaluable.  Reuses d8r_grade.py's band machinery and planted controls.

ITEM verdict (section 7 map, read in order): CONTROL not-evaluable -> BLOCKED; CONTROL not
  converged -> NOT A RESULT (nd harmful); BASELINE_R3 does NOT reproduce the stagnation
  (converges / budget-limited / crash / not-evaluable) -> NOT A RESULT (toolchain/premise not
  validated); [CONTROL converged AND BASELINE_R3 stagnates:] TEST_R3 not-evaluable -> BLOCKED;
  TEST_R3 budget-limited -> NOT A RESULT; TEST_R3 stagnation -> GATE FAIL (with the historical
  sMax/sMin conditioning reference + "free conditioning exhausted: nd does not clear the
  rung-3 wall, MEASURED under a section-11-clean self-contained baseline"); TEST_R3 converged +
  no FD yet -> PENDING; TEST_R3 converged + FD fail/flip -> GATE FAIL; TEST_R3 converged + FD
  pass -> PASS.  A G-CAP crossing folds to GATE FAIL unless a higher row already fired.

PLANTED CONTROLS (rule 3): (i) a fixture converging trace and a fixture stagnant trace are read
back and the grade REFUSES if G-CONV cannot tell them apart; (ii) each FD table is re-read with
a known PLANT added to every physical derivative and the grade REFUSES unless every value moved
by exactly PLANT.  L-332: NO `assert` anywhere -- the module counts ast.Assert nodes in its own
source and refuses on any.  Rule 4 / L-342: a missing physics field -> REFUSE, never degrade.
"""
import argparse
import ast
import hashlib
import json
import math
import os
import re
import sys
import time

# ---- REGISTERED CONSTANTS (A3FL2_PREREGISTRATION.md; the document governs) ----------
ITEM = "A3FL2"
LEGS = ("CONTROL", "BASELINE_R3", "TEST_R3")
# legs that apply the nd lever (their dump/echo MUST read nd); BASELINE_R3 stays natural.
ND_LEGS = ("CONTROL", "TEST_R3")
CAP_ITERS = {"CONTROL": 2000, "BASELINE_R3": 4000, "TEST_R3": 4000}   # gmresMaxIters per leg (section 4)
CAP_CORE_MIN = {"CONTROL": 45.0, "BASELINE_R3": 130.0, "TEST_R3": 130.0, "FD": 90.0}   # section 5/6
ITEM_CEILING_CORE_MIN = 395.0        # sum of per-leg caps (hard stop); predicted spend ~220 (+FD ~60-70)
# HISTORICAL natural-ordering condition-number reference (rung 3: 9.57e10, PRIOR_WORK 119-120),
# MEASURED off-line under the natural baseline.  A3FL2 DROPS the in-arm KSPCalcSingularVal
# diagnostic, so this is a REPORTED historical reference beside the (unmeasured-this-arm) reading,
# NEVER a gate.
HISTORICAL_SMAX_OVER_SMIN = {"TEST_R3": 9.57e10, "BASELINE_R3": 9.57e10, "CONTROL": None}
N_TAIL = 1000                    # section 5: relative residual change over the last N_TAIL iters
THETA_STAG = 1.0e-3              # section 5: below this over N_TAIL = flat = STAGNATION
CONVERGED_REASON = 2            # KSP_CONVERGED_RTOL (gmresRelTol reached)
# FD leg (section 5, reuses d8r bands)
STEPS_REGISTERED = [5.0e-4, 1.0e-3, 2.0e-3]     # middle 1e-3 is the reference
PLATEAU_TOL_PCT = 10.0
FD_BAND_PCT = 5.0
AGG_BAND_PCT = 5.0
MIN_GRADED = 2                   # A3 family rule (fewer -> NOT A RESULT)
NEAR_ZERO_ABS = 1.0e-14
COMPONENTS_REGISTERED = [["patchV", 1], ["twist", 1], ["shape", 115]]
PLANT = 1.234e-03
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}

# ---- log tokens confirmed on disk (A3-rung3-n52/rung3_stage1.log) --------------------
RE_TERMINAL = re.compile(r"\*\*Completed\*\*!\s+Total iterations:\s+(\d+)\.\s+PetscConvergedReason:\s+(-?\d+)\.\s+([\d.]+)\s*s")
RE_MAINITER = re.compile(r"Main iteration\s+(\d+)\s+KSP Residual norm\s+(\S+)")
RE_DUMP_JACORD = re.compile(r"jacMatReOrdering\s+(\w+);")
RE_DUMP_STATEORD = re.compile(r"adjStateOrdering\s+(\w+);")
RE_DUMP_TPC = re.compile(r"transonicPCOption\s+(\d+);")
RE_ECHO_MATORD = re.compile(r"Mat ReOrdering:\s+(\w+)")
RE_ECHO_FILL = re.compile(r"ILU PC Fill Level:\s+(\d+)")
RE_ECHO_RESTART = re.compile(r"GMRES Restart:\s+(\d+)")
RE_ECHO_MAXIT = re.compile(r"GMRES Max Iterations:\s+(\d+)")
RE_SUBLU = re.compile(r"DAFOAM_SUBPC_TYPE|SubMatrix.*lu|sub.*LU banner", re.I)


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def md5_of(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


# ================= log parsing ========================================================
def parse_log(text):
    """Return dump/echo proof tokens, terminal solves, and per-solve residual segments.
    A residual segment is a run of `Main iteration` lines whose iter counter increases; a
    reset to a smaller iter starts a new segment (CD then CL).  A3FL2 reads NO singular-value
    token (the KSPCalcSingularVal diagnostic is dropped)."""
    dump = {
        "jacMatReOrdering": (RE_DUMP_JACORD.search(text).group(1) if RE_DUMP_JACORD.search(text) else None),
        "adjStateOrdering": (RE_DUMP_STATEORD.search(text).group(1) if RE_DUMP_STATEORD.search(text) else None),
        "transonicPCOption": (RE_DUMP_TPC.search(text).group(1) if RE_DUMP_TPC.search(text) else None),
        "Mat ReOrdering": (RE_ECHO_MATORD.search(text).group(1) if RE_ECHO_MATORD.search(text) else None),
        "ILU PC Fill Level": (RE_ECHO_FILL.search(text).group(1) if RE_ECHO_FILL.search(text) else None),
        "GMRES Restart": (RE_ECHO_RESTART.search(text).group(1) if RE_ECHO_RESTART.search(text) else None),
        "GMRES Max Iterations": (RE_ECHO_MAXIT.search(text).group(1) if RE_ECHO_MAXIT.search(text) else None),
    }
    terminals = [(int(m.group(1)), int(m.group(2)), float(m.group(3))) for m in RE_TERMINAL.finditer(text)]
    segments, cur, last_it = [], [], -1
    for m in RE_MAINITER.finditer(text):
        it = int(m.group(1))
        try:
            r = float(m.group(2))
        except ValueError:
            continue
        if it <= last_it and cur:
            segments.append(cur)
            cur = []
        cur.append((it, r))
        last_it = it
    if cur:
        segments.append(cur)
    return {"dump": dump, "terminals": terminals, "segments": segments}


def check_proofs(leg, parsed):
    d = parsed["dump"]
    if d["transonicPCOption"] != "1":
        refuse("PROOF", {"leg": leg, "transonicPCOption": d["transonicPCOption"], "want": "1"})
    # ORDERING is leg-specific: nd for CONTROL/TEST_R3, natural for BASELINE_R3 (baseline unchanged).
    want_ord = "nd" if leg in ND_LEGS else "natural"
    if d["jacMatReOrdering"] != want_ord or d["Mat ReOrdering"] != want_ord:
        note = ("the nd lever's own echo is absent; the leg did not apply the lever" if leg in ND_LEGS
                else "BASELINE_R3 must stay NATURAL (baseline config unchanged); this log reads a different ordering")
        refuse("PROOF", {"leg": leg, "jacMatReOrdering": d["jacMatReOrdering"], "Mat ReOrdering": d["Mat ReOrdering"],
                         "want": want_ord, "note": note})
    # NB: A3FL2 does NOT require KSPCalcSingularVal (A3FL1's invalid daOption, dropped entirely).
    if d["adjStateOrdering"] != "cell":
        refuse("PROOF", {"leg": leg, "adjStateOrdering": d["adjStateOrdering"], "want": "cell (held at baseline)"})
    if d["ILU PC Fill Level"] != "0":
        refuse("PROOF", {"leg": leg, "ILU PC Fill Level": d["ILU PC Fill Level"], "want": "0"})
    if d["GMRES Restart"] != "200":
        refuse("PROOF", {"leg": leg, "GMRES Restart": d["GMRES Restart"], "want": "200"})
    if RE_SUBLU.search("".join("%s %s" % kv for kv in d.items()) or ""):
        refuse("PROOF", {"leg": leg, "note": "sub-LU banner present; env must be unset"})
    return {"proofs_seen": True, "ordering_expected": want_ord, "dump": d}


# ================= G-CONV: the convergence gate =======================================
def g_conv_one(leg, T, reason, segment):
    """Classify a single solve.  segment is its residual trace [(iter, r), ...]."""
    cap = CAP_ITERS[leg]
    out = {"leg": leg, "total_iters": T, "reason": reason, "cap": cap}
    if reason == CONVERGED_REASON and T < cap:
        out["state"] = "CONVERGED"
        return out
    if reason < 0 and T >= cap:
        # look at the tail: relative residual change over the last N_TAIL iters
        if len(segment) < 2:
            out.update({"state": "NOT_EVALUABLE", "reason_text": "negative reason at cap but no residual trace"})
            return out
        it_last, r_last = segment[-1]
        # nearest entry at or below (it_last - N_TAIL)
        prior = [(it, r) for it, r in segment if it <= it_last - N_TAIL]
        if not prior:
            out.update({"state": "NOT_EVALUABLE", "reason_text": "trace shorter than N_TAIL"})
            return out
        it_prev, r_prev = prior[-1]
        rel = abs(r_prev - r_last) / abs(r_last) if r_last != 0.0 else float("inf")
        monotone = all(segment[i][1] >= segment[i + 1][1] for i in range(len(segment) - 1))
        out.update({"tail_from_iter": it_prev, "tail_to_iter": it_last, "r_prev": r_prev, "r_last": r_last,
                    "tail_rel_change": rel, "theta_stag": THETA_STAG, "monotone": monotone})
        out["state"] = "STAGNATION" if rel < THETA_STAG else "BUDGET_LIMITED"
        return out
    if reason < 0:
        out["state"] = "DIVERGED_NOT_CAP"       # negative but not at cap -> treated as not-evaluable conditioning
        return out
    out["state"] = "NOT_EVALUABLE"
    return out


def g_conv_leg(leg, parsed):
    """CONTROL requires BOTH solves CONVERGED; BASELINE_R3 and TEST_R3 key on the first
    (CD) solve."""
    terms, segs = parsed["terminals"], parsed["segments"]
    if not terms:
        return {"leg": leg, "leg_state": "NOT_EVALUABLE", "solves": [], "note": "no terminal reason (crash/OOM before a reason)"}
    solves = []
    for i, (T, reason, wall) in enumerate(terms):
        seg = segs[i] if i < len(segs) else []
        solves.append(g_conv_one(leg, T, reason, seg))
    if leg == "CONTROL":
        need = 2  # both CD and CL
        if len(solves) < need:
            leg_state = "NOT_EVALUABLE"
        elif all(s["state"] == "CONVERGED" for s in solves[:need]):
            leg_state = "CONVERGED"
        elif any(s["state"] == "NOT_EVALUABLE" for s in solves):
            leg_state = "NOT_EVALUABLE"
        else:
            leg_state = "NOT_CONVERGED"
    else:  # BASELINE_R3 and TEST_R3 key on CD (first solve)
        leg_state = solves[0]["state"]
    return {"leg": leg, "leg_state": leg_state, "solves": solves}


def g_diag(leg, parsed):
    """A3FL2 DROPS the in-arm KSPCalcSingularVal diagnostic (it was A3FL1's invalid daOption).
    sMax/sMin is NOT measured in this arm; report NOT_MEASURED_THIS_ARM and cite the historical
    MEASURED natural-ordering reference (rung 3: 9.57e+10, PRIOR_WORK 119-120).  Never a gate --
    conditioning is adjudicated by convergence (G-CONV)."""
    ref = HISTORICAL_SMAX_OVER_SMIN.get(leg)
    return {"leg": leg, "singular": "NOT_MEASURED_THIS_ARM", "historical_reference_ratio": ref,
            "note": ("A3FL2 drops the KSPCalcSingularVal in-arm diagnostic (A3FL1's invalid daOption); "
                     "sMax/sMin is not measured this arm. Historical MEASURED natural-ordering reference "
                     "9.57e+10 (rung 3, PRIOR_WORK 119-120) cited. Conditioning is read from convergence, "
                     "never from an in-arm singular-value token.")}


# ================= G-FD: the bright line (conditional) reuses d8r bands ===============
def read_F(path):
    j = json.load(open(path))
    if j.get("components_requested") != COMPONENTS_REGISTERED:
        refuse("G-FD", {"components_requested_not_registered": j.get("components_requested"),
                        "registered": COMPONENTS_REGISTERED})
    table, ctrl = {}, None
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            ctrl = row
            continue
        key = (row["dv"], int(row["idx"]))
        fd = {}
        for k, v in (row.get("fd") or {}).items():
            fd[float(v["step"])] = {"ok": bool(v.get("ok")), "dCD": (float(v["dCD"]) if v.get("ok") else None)}
        table[key] = {"J_adj": (float(row["J_adj"]) if row.get("J_adj") is not None else None), "fd": fd}
    return {"table": table, "ctrl": ctrl, "raw": j}


def ctrl_control(F):
    c = F["ctrl"]
    if c is None:
        refuse("CONTROL", {"ctrl_row_absent": True})
    zero = float(c["fd"][repr(1.0e-1)]["dCD"]) if repr(1.0e-1) in c["fd"] else None
    plant = float(c["planted"]["dCD"]) if c.get("planted") else None
    want = PLANT / (2.0 * 1.0e-1)
    if zero != 0.0 or plant is None or abs(plant - want) > 1e-12 * abs(want):
        refuse("CONTROL", {"instrument_ctrl_not_seen": {"zero": zero, "planted": plant, "want": want}})
    return {"instrument_ctrl_zero": zero, "instrument_ctrl_planted": plant, "want": want}


def grader_plant_control(base, fpath):
    j = json.load(open(fpath))
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            continue
        for v in (row.get("fd") or {}).values():
            if v.get("ok"):
                v["dCD"] = repr(float(v["dCD"]) + PLANT)
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "F_planted.json")
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    orig, back = read_F(fpath)["table"], read_F(cp)["table"]
    worst, n = 0.0, 0
    for key, row in orig.items():
        for s, v in row["fd"].items():
            if v["ok"]:
                worst = max(worst, abs((back[key]["fd"][s]["dCD"] - v["dCD"]) - PLANT))
                n += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"grader_plant_not_seen": {"n_values": n, "worst_residual": worst, "plant": PLANT}})
    return {"grader_plant_seen": True, "n_values": n, "worst_residual": worst}


def grade_fd(F):
    comps, graded_fd, graded_adj = [], [], []
    steps = sorted(STEPS_REGISTERED, reverse=True)
    for dv, idx in COMPONENTS_REGISTERED:
        row = F["table"].get((dv, idx))
        c = {"dv": dv, "idx": idx}
        if row is None or row["J_adj"] is None:
            c.update({"verdict": "NOT A RESULT", "reason": "ABSENT"})
            comps.append(c)
            continue
        j = row["J_adj"]
        c["J_adj"] = j
        vals = [row["fd"].get(s) for s in steps]
        if any(v is None or not v["ok"] for v in vals):
            c.update({"verdict": "NOT A RESULT", "reason": "FD_STEP_FAILED_OR_ABSENT", "steps_present": sorted(row["fd"])})
            comps.append(c)
            continue
        d = [v["dCD"] for v in vals]
        ref = d[1]
        c.update({"steps": steps, "d_fd": d, "d_ref": ref})
        if abs(ref) < NEAR_ZERO_ABS:
            c.update({"verdict": "NOT A RESULT", "reason": "NEAR_ZERO"})
            comps.append(c)
            continue
        nb = [abs(d[0] - ref) / abs(ref) * 100.0, abs(d[2] - ref) / abs(ref) * 100.0]
        c["plateau_neighbour_pct"] = nb
        if min(nb) > PLATEAU_TOL_PCT:
            c.update({"verdict": "NOT A RESULT", "reason": "NO_PLATEAU"})
            comps.append(c)
            continue
        rel = abs(ref - j) / abs(ref) * 100.0
        flip = bool(ref * j < 0.0)
        c.update({"rel_err_pct": rel, "sign_flip": flip})
        c["verdict"] = "GATE FAIL" if (flip or rel > FD_BAND_PCT) else "PASS"
        graded_fd.append(ref)
        graded_adj.append(j)
        comps.append(c)
    n_graded = len(graded_fd)
    out = {"components": comps, "n_graded": n_graded,
           "n_gate_fail": sum(1 for c in comps if c.get("verdict") == "GATE FAIL"),
           "sign_flips": sum(1 for c in comps if c.get("sign_flip"))}
    if n_graded < MIN_GRADED:
        out.update({"verdict": "NOT A RESULT", "aggregate_rel_err_pct": None,
                    "reason": "fewer than %d graded components" % MIN_GRADED})
        return out
    num = math.sqrt(sum((a - b) ** 2 for a, b in zip(graded_fd, graded_adj)))
    den = math.sqrt(sum(a ** 2 for a in graded_fd))
    agg = num / den * 100.0
    out["aggregate_rel_err_pct"] = agg
    band_d_ok = out["n_gate_fail"] == 0
    band_e_ok = agg <= AGG_BAND_PCT
    out["band_D"] = "PASS" if band_d_ok else "GATE FAIL"
    out["band_E"] = "PASS" if band_e_ok else "GATE FAIL"
    out["verdict"] = "PASS" if (band_d_ok and band_e_ok) else "GATE FAIL"
    return out


# ================= item composition (section 7 map) ===================================
def compose_item(control, baseline, test, fd):
    """control/baseline/test are g_conv_leg outputs; fd is grade_fd output or None.
    Read in order; the first matching row is the item verdict (prereg section 7)."""
    cs = control["leg_state"]
    bs = baseline["leg_state"]
    ts = test["leg_state"]
    # ---- CONTROL: does nd break a converging solve? --------------------------------
    if cs == "NOT_EVALUABLE":
        return "BLOCKED", "CONTROL not evaluable (crash/OOM/memory before a reason)"
    if cs != "CONVERGED":
        return "NOT A RESULT", "CONTROL did not converge -> nd is harmful (breaks a converging solve); arm inconclusive"
    # ---- BASELINE_R3: is the -3 stagnation reproduced under THIS pinned image? ------
    if bs != "STAGNATION":
        return "NOT A RESULT", ("BASELINE_R3 did NOT reproduce the rung-3 -3 stagnation under the pinned "
                                "image (leg_state=%s) -> premise/toolchain NOT validated; nd's effect cannot "
                                "be attributed without a confirmed natural baseline under this image" % bs)
    # ---- CONTROL converged AND BASELINE_R3 stagnates: attribute nd's effect --------
    if ts == "NOT_EVALUABLE":
        return "BLOCKED", "TEST_R3 not evaluable (crash/OOM/memory before a reason)"
    if ts == "BUDGET_LIMITED":
        return "NOT A RESULT", "TEST_R3 -3 at cap but still descending: budget-limited, cap too small to decide"
    if ts == "DIVERGED_NOT_CAP":
        return "NOT A RESULT", "TEST_R3 negative reason but not at the cap: not a clean conditioning read"
    if ts == "STAGNATION":
        return "GATE FAIL", ("TEST_R3 stagnation (flat -3 at cap, memory comfortable): free conditioning "
                             "exhausted -- nd does NOT clear the rung-3 wall, MEASURED under a section-11-clean "
                             "self-contained baseline; historical conditioning reference (sMax/sMin 9.57e+10) "
                             "reported beside it")
    if ts == "CONVERGED":
        if fd is None:
            return "PENDING", "TEST_R3 converged; FD-verification leg owed (bright line, DAFOAM_CHARTER section 2)"
        if fd["verdict"] == "PASS":
            return "PASS", "TEST_R3 converged AND FD table passes the band: a new verified A3 rung"
        if fd["verdict"] == "GATE FAIL":
            return "GATE FAIL", "TEST_R3 converged but FD table fails band/sign (bright line)"
        return "NOT A RESULT", "TEST_R3 converged but FD leg not evaluable (fewer than MIN_GRADED)"
    return "NOT A RESULT", "unmapped test state %s" % ts


# ================= single-log grade + compose =========================================
def grade_leg(logpath, leg, fd_json=None, run_base=None):
    if leg not in LEGS:
        refuse("ARG", {"leg": leg, "want": list(LEGS)})
    text = open(logpath, errors="replace").read()
    parsed = parse_log(text)
    proofs = check_proofs(leg, parsed)
    conv = g_conv_leg(leg, parsed)
    diag = g_diag(leg, parsed)
    out = {"item": "CURRICULUM-%s" % ITEM, "leg": leg, "log": logpath, "proofs": proofs,
           "G_CONV": conv, "G_DIAG": diag}
    if leg == "TEST_R3" and fd_json and os.path.isfile(fd_json):
        F = read_F(fd_json)
        controls = {"instrument_ctrl": ctrl_control(F),
                    "grader_plant": grader_plant_control(run_base or os.path.dirname(fd_json), fd_json)}
        out["G_FD"] = grade_fd(F)
        out["controls"] = controls
    return out


# ================= selftest: planted fixtures =========================================
EXPECTED_UNITS = 36


def _dump_block(jac="nd", state_ord="cell", tpc="1", mat="nd", fill="0", restart="200", maxit="4000", sv="0"):
    """Fixture dump.  A3FL2 does NOT check KSPCalcSingularVal, so `sv` is emitted purely to
    prove the grader is INDIFFERENT to it (default 0, the untouched baseline value)."""
    return ("adjEqnSolMethod Krylov;\n    jacMatReOrdering %s;\n    KSPCalcEigen 0;\n"
            "    KSPCalcSingularVal %s;\n    adjStateOrdering %s;\n    transonicPCOption %s;\n"
            "GMRES Restart: %s\nMat ReOrdering: %s\nILU PC Fill Level: %s\nGMRES Max Iterations: %s\n"
            % (jac, sv, state_ord, tpc, restart, mat, fill, maxit))


def _trace(start_r, n, per100_factor, cap, reason):
    """Build a residual trace + terminal line. per100_factor multiplies r every 100 iters.
    A3FL2 emits NO singular-value line (the diagnostic is dropped)."""
    lines, r = [], start_r
    it = 0
    while it <= n:
        lines.append("Main iteration %d KSP Residual norm %.12e %.2f s. " % (it, r, it * 0.35))
        r = r * per100_factor
        it += 100
    T = n
    term = "**Completed**! Total iterations: %d. PetscConvergedReason: %d. 1416 s\n" % (T, reason)
    return "\n".join(lines) + "\n" + term


def _flat_stag_trace(cap, reason):
    """A genuinely flat -3-at-cap tail (STAGNATION): residual decays early, flat by ~1500.
    A3FL2 emits NO singular-value line."""
    lines, it = [], 0
    while it <= cap:
        rr = 1.615246e-2 + (2.121343e-2 - 1.615246e-2) * math.exp(-it / 150.0)
        lines.append("Main iteration %d KSP Residual norm %.12e %.2f s. " % (it, rr, it * 0.35))
        it += 100
    return "\n".join(lines) + "\n" \
        + "**Completed**! Total iterations: %d. PetscConvergedReason: %d. 1416 s\n" % (cap, reason)


def _fd_json(path, errs=None, flip=None, noplateau=None, ctrl_ok=True):
    errs = errs or {}
    flip = flip or set()
    noplateau = noplateau or set()
    J = {("patchV", 1): 7.6e-3, ("twist", 1): -2.0e-3, ("shape", 115): -1.24e-1}
    rows = []
    for dv, idx in COMPONENTS_REGISTERED:
        j = J[(dv, idx)]
        e = errs.get((dv, idx), 0.5)
        dref = j * (1.0 + e / 100.0)
        if (dv, idx) in flip:
            dref = -dref
        fd = {}
        for s in STEPS_REGISTERED:
            scale = 1.0 if s == sorted(STEPS_REGISTERED)[1] else 1.01
            if (dv, idx) in noplateau:
                scale = 1.0 if s == sorted(STEPS_REGISTERED)[1] else 1.5
            fd[repr(s)] = {"step": s, "ok": True, "dCD": repr(dref * scale)}
        rows.append({"dv": dv, "idx": idx, "J_adj": repr(j), "fd": fd})
    planted = PLANT / (2.0 * 1.0e-1) if ctrl_ok else 0.0
    rows.append({"dv": "CTRL", "idx": 0, "fd": {repr(1.0e-1): {"step": 1.0e-1, "ok": True, "dCD": repr(0.0)}},
                 "planted": {"step": 1.0e-1, "plant": PLANT, "dCD": repr(planted), "ok": True}})
    json.dump({"item": ITEM, "components_requested": COMPONENTS_REGISTERED, "rows": rows}, open(path, "w"))
    return path


def selftest(tmp):
    n, fails = 0, []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    def refused(fn):
        try:
            fn(); return False
        except Refusal:
            return True

    os.makedirs(tmp, exist_ok=True)

    # ============ CONTROL (rung-2, nd) ============================================
    ctrl_log = _dump_block(maxit="2000") + _trace(1.0, 900, 0.5, 2000, 2) + "\n" + _trace(1.0, 1100, 0.5, 2000, 2)
    p = os.path.join(tmp, "control.log"); open(p, "w").write(ctrl_log)
    r = grade_leg(p, "CONTROL")
    unit("U1 CONTROL (nd) two solves reason 2 below cap -> leg CONVERGED", r["G_CONV"]["leg_state"] == "CONVERGED")
    unit("U2 CONTROL solves classified CONVERGED each", all(s["state"] == "CONVERGED" for s in r["G_CONV"]["solves"][:2]))
    coll = _dump_block(maxit="2000") + _trace(1.0, 200, 1.0, 2000, -5)
    p = os.path.join(tmp, "control_collapse.log"); open(p, "w").write(coll)
    r = grade_leg(p, "CONTROL")
    unit("U3 CONTROL single -5 (not 2 solves) -> NOT_CONVERGED or NOT_EVALUABLE",
         r["G_CONV"]["leg_state"] in ("NOT_CONVERGED", "NOT_EVALUABLE"))

    # ============ BASELINE_R3 (rung-3, NATURAL, no nd) ============================
    base_stag = _dump_block(jac="natural", mat="natural") + _flat_stag_trace(4000, -3)
    p = os.path.join(tmp, "baseline_stag.log"); open(p, "w").write(base_stag)
    r = grade_leg(p, "BASELINE_R3")
    unit("U4 BASELINE_R3 natural -3 at cap flat tail -> STAGNATION (premise reproduced)",
         r["G_CONV"]["leg_state"] == "STAGNATION")
    unit("U5 BASELINE_R3 proofs accept NATURAL ordering", r["proofs"]["ordering_expected"] == "natural")
    unit("U6 BASELINE_R3 G-DIAG NOT_MEASURED_THIS_ARM, historical 9.57e10 cited",
         r["G_DIAG"]["singular"] == "NOT_MEASURED_THIS_ARM"
         and abs(r["G_DIAG"]["historical_reference_ratio"] - 9.57e10) < 1e6)
    base_conv = _dump_block(jac="natural", mat="natural") + _trace(1.0, 1500, 0.5, 4000, 2)
    p = os.path.join(tmp, "baseline_conv.log"); open(p, "w").write(base_conv)
    r = grade_leg(p, "BASELINE_R3")
    unit("U7 BASELINE_R3 natural converged (premise NOT reproduced) -> CONVERGED",
         r["G_CONV"]["leg_state"] == "CONVERGED")
    # BASELINE_R3 reading nd MUST be refused (baseline must stay natural)
    base_nd = _dump_block(jac="nd", mat="nd") + _flat_stag_trace(4000, -3)
    p = os.path.join(tmp, "baseline_nd.log"); open(p, "w").write(base_nd)
    unit("U8 BASELINE_R3 log reading nd -> REFUSE (baseline must stay NATURAL)",
         refused(lambda: grade_leg(p, "BASELINE_R3")))

    # ============ TEST_R3 (rung-3, nd) ===========================================
    flat = _dump_block() + _flat_stag_trace(4000, -3)
    p = os.path.join(tmp, "test_stag.log"); open(p, "w").write(flat)
    r = grade_leg(p, "TEST_R3")
    unit("U9 TEST_R3 (nd) -3 at cap with flat tail -> STAGNATION", r["G_CONV"]["leg_state"] == "STAGNATION")
    unit("U10 TEST_R3 stagnation tail_rel_change < THETA_STAG", r["G_CONV"]["solves"][0]["tail_rel_change"] < THETA_STAG)
    unit("U11 TEST_R3 G-DIAG NOT_MEASURED_THIS_ARM (no in-arm singular token required)",
         r["G_DIAG"]["singular"] == "NOT_MEASURED_THIS_ARM")
    lines, it = [], 0
    while it <= 4000:
        rr = 1.0 * (0.999 ** (it / 100.0))  # steadily descending -> > THETA_STAG over 1000
        lines.append("Main iteration %d KSP Residual norm %.12e %.2f s. " % (it, rr, it * 0.35))
        it += 100
    budg = _dump_block() + "\n".join(lines) + "\n**Completed**! Total iterations: 4000. PetscConvergedReason: -3. 1416 s\n"
    p = os.path.join(tmp, "test_budget.log"); open(p, "w").write(budg)
    r = grade_leg(p, "TEST_R3")
    unit("U12 TEST_R3 -3 at cap still descending -> BUDGET_LIMITED", r["G_CONV"]["leg_state"] == "BUDGET_LIMITED")
    convlog = _dump_block() + _trace(1.0, 1500, 0.5, 4000, 2)
    p = os.path.join(tmp, "test_conv.log"); open(p, "w").write(convlog)
    r = grade_leg(p, "TEST_R3")
    unit("U13 TEST_R3 reason 2 below cap -> CONVERGED", r["G_CONV"]["leg_state"] == "CONVERGED")

    # ============ PROOF refusals (shared across the nd legs) =====================
    bad = _dump_block(jac="natural", mat="natural") + _trace(1.0, 1500, 0.5, 4000, 2)
    p = os.path.join(tmp, "bad_natural.log"); open(p, "w").write(bad)
    unit("U14 TEST_R3 dump/echo still reading natural -> REFUSE (lever not applied)",
         refused(lambda: grade_leg(p, "TEST_R3")))
    # A3FL2 DROPS the KSPCalcSingularVal requirement: a log reading `KSPCalcSingularVal 0`
    # (the untouched baseline value) MUST now be ACCEPTED, not refused (the A3FL1 lesson).
    ok = _dump_block(sv="0") + _trace(1.0, 1500, 0.5, 4000, 2)
    p = os.path.join(tmp, "sv0_accepted.log"); open(p, "w").write(ok)
    r = grade_leg(p, "TEST_R3")
    unit("U15 KSPCalcSingularVal 0 in dump -> ACCEPTED (A3FL2 drops the diagnostic requirement)",
         r["G_CONV"]["leg_state"] == "CONVERGED")
    bad = _dump_block(tpc="2") + _trace(1.0, 1500, 0.5, 4000, 2)
    p = os.path.join(tmp, "bad_tpc.log"); open(p, "w").write(bad)
    unit("U16 transonicPCOption 2 -> REFUSE", refused(lambda: grade_leg(p, "TEST_R3")))
    bad = _dump_block(state_ord="state") + _trace(1.0, 1500, 0.5, 4000, 2)
    p = os.path.join(tmp, "bad_state.log"); open(p, "w").write(bad)
    unit("U17 adjStateOrdering drifted to state -> REFUSE", refused(lambda: grade_leg(p, "TEST_R3")))
    noterm = _dump_block() + "Main iteration 0 KSP Residual norm 1.0 0.0 s. \n(crash)\n"
    p = os.path.join(tmp, "noterm.log"); open(p, "w").write(noterm)
    r = grade_leg(p, "TEST_R3")
    unit("U18 no terminal reason -> leg NOT_EVALUABLE", r["G_CONV"]["leg_state"] == "NOT_EVALUABLE")
    unit("U19 G_DIAG NOT_MEASURED_THIS_ARM and historical reference named (all legs, no diagnostic)",
         r["G_DIAG"]["singular"] == "NOT_MEASURED_THIS_ARM" and r["G_DIAG"]["historical_reference_ratio"] is not None)

    # ============ FD grading (bright line, reused d8r bands) =====================
    F = _fd_json(os.path.join(tmp, "fd_clean.json"))
    fd = grade_fd(read_F(F))
    unit("U20 FD clean (all ~0.5%) -> band D/E PASS, verdict PASS", fd["verdict"] == "PASS" and fd["n_graded"] == 3)
    F = _fd_json(os.path.join(tmp, "fd_err.json"), errs={("twist", 1): 7.0})
    fd = grade_fd(read_F(F))
    unit("U21 FD planted 7% error -> component + verdict GATE FAIL", fd["verdict"] == "GATE FAIL" and fd["n_gate_fail"] == 1)
    F = _fd_json(os.path.join(tmp, "fd_flip.json"), flip={("patchV", 1)})
    fd = grade_fd(read_F(F))
    unit("U22 FD sign flip -> GATE FAIL, flip counted", fd["verdict"] == "GATE FAIL" and fd["sign_flips"] == 1)
    F = _fd_json(os.path.join(tmp, "fd_noplat.json"), noplateau={("shape", 115)})
    fd = grade_fd(read_F(F))
    unit("U23 FD one no-plateau -> that comp NOT A RESULT, 2 graded -> PASS", fd["verdict"] == "PASS" and fd["n_graded"] == 2)
    F = _fd_json(os.path.join(tmp, "fd_noplat2.json"), noplateau={("shape", 115), ("twist", 1)})
    fd = grade_fd(read_F(F))
    unit("U24 FD two no-plateau -> 1 graded < MIN_GRADED -> NOT A RESULT", fd["verdict"] == "NOT A RESULT")

    # ============ planted controls (rule 3) ======================================
    F = _fd_json(os.path.join(tmp, "fd_ctrl.json"))
    unit("U25 instrument CTRL planted row SEEN", ctrl_control(read_F(F))["instrument_ctrl_zero"] == 0.0)
    unit("U26 grader-level plant SEEN on FD table", grader_plant_control(tmp, F)["grader_plant_seen"])
    F = _fd_json(os.path.join(tmp, "fd_ctrl_broken.json"), ctrl_ok=False)
    unit("U27 CTRL planted row broken -> REFUSE", refused(lambda: ctrl_control(read_F(F))))

    # ============ item composition (section 7 map, 3 legs) =======================
    CONV = {"leg_state": "CONVERGED"}
    STAG = {"leg_state": "STAGNATION"}
    unit("U28 CONTROL conv + BASELINE stag + TEST stagnation -> GATE FAIL",
         compose_item(CONV, STAG, STAG, None)[0] == "GATE FAIL")
    unit("U29 CONTROL conv + BASELINE stag + TEST converged + no FD -> PENDING",
         compose_item(CONV, STAG, CONV, None)[0] == "PENDING")
    unit("U30 CONTROL not converged -> NOT A RESULT (nd harmful)",
         compose_item({"leg_state": "NOT_CONVERGED"}, STAG, CONV, None)[0] == "NOT A RESULT")
    unit("U31 CONTROL not-evaluable -> BLOCKED",
         compose_item({"leg_state": "NOT_EVALUABLE"}, STAG, CONV, None)[0] == "BLOCKED")
    unit("U32 BASELINE converged (premise NOT reproduced) -> NOT A RESULT",
         compose_item(CONV, CONV, STAG, None)[0] == "NOT A RESULT")
    unit("U33 BASELINE budget-limited (premise NOT reproduced) -> NOT A RESULT",
         compose_item(CONV, {"leg_state": "BUDGET_LIMITED"}, STAG, None)[0] == "NOT A RESULT")
    unit("U34 BASELINE not-evaluable (premise NOT reproduced) -> NOT A RESULT",
         compose_item(CONV, {"leg_state": "NOT_EVALUABLE"}, STAG, None)[0] == "NOT A RESULT")
    unit("U35 CONTROL conv + BASELINE stag + TEST not-evaluable -> BLOCKED",
         compose_item(CONV, STAG, {"leg_state": "NOT_EVALUABLE"}, None)[0] == "BLOCKED")
    unit("U36 CONTROL conv + BASELINE stag + TEST converged + FD PASS -> PASS",
         compose_item(CONV, STAG, CONV, {"verdict": "PASS"})[0] == "PASS")

    # vocabulary guard (not a counted unit)
    for v in ("BLOCKED", "GATE FAIL", "PENDING", "PASS", "NOT A RESULT"):
        if v not in VOCAB:
            fails.append("vocab %s" % v)
    print("A3FL2 GRADER SELFTEST units=%d expected=%d failures=%d" % (n, EXPECTED_UNITS, len(fails)))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("A3FL2 GRADER SELFTEST PASS %d/%d" % (n, EXPECTED_UNITS))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=None, help="a leg log to grade")
    ap.add_argument("--leg", default=None, choices=list(LEGS))
    ap.add_argument("--fd-json", default=None, help="TEST_R3 FD table JSON (only if TEST_R3 converged)")
    ap.add_argument("--run-base", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--drive", action="store_true", help="alias for --selftest")
    ap.add_argument("--tmpdir", default="/tmp")
    a = ap.parse_args()
    if count_asserts(os.path.abspath(__file__)) != 0:
        print("REFUSAL: this comparator carries an assert statement (L-332)")
        return 2
    if a.selftest or a.drive:
        d = os.path.join(a.tmpdir, "a3fl2_selftest_%d" % os.getpid())
        return selftest(d)
    if not a.log or not a.leg:
        print("usage: a3fl2_grade.py --log <leg log> --leg CONTROL|BASELINE_R3|TEST_R3 "
              "[--fd-json F] [--out FILE] | --selftest")
        return 64
    try:
        r = grade_leg(a.log, a.leg, fd_json=a.fd_json, run_base=a.run_base)
    except Refusal as e:
        print("REFUSAL: %s -> NOT A RESULT" % e)
        if a.out:
            json.dump({"item": "CURRICULUM-%s" % ITEM, "leg": a.leg, "verdict": "NOT A RESULT", "refusal": str(e)}, open(a.out, "w"), indent=1)
        return 2
    print(json.dumps(r, indent=1, default=str))
    if a.out:
        json.dump(r, open(a.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
