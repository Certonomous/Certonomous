#!/usr/bin/env python3
"""A3FL1 COMPARATOR -- the free-conditioning-levers arm (jacMatReOrdering:nd +
KSPCalcSingularVal:1) for the ONERA-M6 rung-3 `-3` adjoint stagnation.  DRAFT -- FROZEN by
md5 in A3FL1_PREREGISTRATION.md section 9 by the dafoam-supervisor at check-1.  Computes
nothing about physics; renders verdicts from the FIXED vocabulary ONLY
(PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING).

WHAT IT GRADES (A3FL1_PREREGISTRATION.md sections 4/5/7):
  PROOFS  per leg log, before any number counts (L-40): the DAOption dump must read
          `jacMatReOrdering nd;` AND the KSP echo `Mat ReOrdering: nd` (the lever's own echo;
          a leg still reading `natural` did NOT apply the lever -> REFUSE), `KSPCalcSingularVal 1;`
          (baseline 0 -> REFUSE if 0), `transonicPCOption 1;`, `adjStateOrdering cell;`,
          `ILU PC Fill Level: 0`, `GMRES Restart: 200`, no sub-LU banner.  Any missing -> REFUSE.
  G-CONV  the convergence gate.  From the terminal `**Completed**! Total iterations: T.
          PetscConvergedReason: R. <wall> s` and the residual trace `Main iteration N KSP
          Residual norm r_N`:
            CONVERGED     = R == 2 AND T < cap, on the graded objective(s).
            STAGNATION    = R < 0 at exactly the cap AND flat tail: relative residual change
                            over the last N_TAIL iters < THETA_STAG.
            BUDGET_LIMITED= R < 0 at the cap but the tail is still descending (>= THETA_STAG,
                            monotone) -- NOT a stagnation verdict.
            NOT_EVALUABLE = no terminal reason (crash/OOM before a reason).
  G-CTRL  the control leg CONVERGED on BOTH CD and CL (reason 2, below cap) -> VALID, else the
          arm is inconclusive ("levers harmful").
  G-DIAG  sMax/sMin from KSPCalcSingularVal (reported measurement, never a gate); NOT_MEASURED
          and named if the solver emits no singular-value token (the print format has never
          been observed on disk).
  G-FD    the bright line (DAFOAM_CHARTER section 2), CONDITIONAL on TEST convergence: an
          endpoint FD table, per-component band D (<= 5 %, same sign; a sign flip is GATE FAIL),
          aggregate band E (<= 5 %), plateau (middle step vs a neighbour <= 10 %), >= MIN_GRADED
          evaluable.  Reuses d8r_grade.py's band machinery and planted controls.

ITEM verdict (section 7 map, read in order): CONTROL not-evaluable -> BLOCKED; CONTROL not
  converged -> NOT A RESULT; TEST not-evaluable -> BLOCKED; TEST budget-limited -> NOT A RESULT;
  TEST stagnation -> GATE FAIL (with the sMax/sMin conditioning finding beside it); TEST
  converged + no FD yet -> PENDING; TEST converged + FD fail/flip -> GATE FAIL; TEST converged +
  FD pass -> PASS.  A G-CAP crossing folds to GATE FAIL unless a higher row already fired.

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

# ---- REGISTERED CONSTANTS (A3FL1_PREREGISTRATION.md; the document governs) ----------
ITEM = "A3FL1"
LEGS = ("CONTROL", "TEST")
CAP_ITERS = {"CONTROL": 2000, "TEST": 4000}          # gmresMaxIters per leg (section 4)
CAP_CORE_MIN = {"CONTROL": 45.0, "TEST": 130.0, "FD": 90.0}   # section 5/6
ITEM_CEILING_CORE_MIN = 265.0
BASELINE_SMAX_OVER_SMIN = {"TEST": 9.57e10, "CONTROL": None}  # natural-ordering baseline (PRIOR_WORK 119-120)
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
RE_DUMP_SINGVAL = re.compile(r"KSPCalcSingularVal\s+(\d+);")
RE_DUMP_STATEORD = re.compile(r"adjStateOrdering\s+(\w+);")
RE_DUMP_TPC = re.compile(r"transonicPCOption\s+(\d+);")
RE_ECHO_MATORD = re.compile(r"Mat ReOrdering:\s+(\w+)")
RE_ECHO_FILL = re.compile(r"ILU PC Fill Level:\s+(\d+)")
RE_ECHO_RESTART = re.compile(r"GMRES Restart:\s+(\d+)")
RE_ECHO_MAXIT = re.compile(r"GMRES Max Iterations:\s+(\d+)")
RE_SUBLU = re.compile(r"DAFOAM_SUBPC_TYPE|SubMatrix.*lu|sub.*LU banner", re.I)
# singular-value print format is UNOBSERVED on disk: try candidates, else NOT_MEASURED.
RE_SINGVAL_CANDS = [
    re.compile(r"[Ee]xtreme singular values.*?max[^0-9eE+-]*([0-9.eE+-]+).*?min[^0-9eE+-]*([0-9.eE+-]+)"),
    re.compile(r"sMax\s*[=:]\s*([0-9.eE+-]+).*?sMin\s*[=:]\s*([0-9.eE+-]+)"),
    re.compile(r"[Ss]igma_?max\s*[=:]\s*([0-9.eE+-]+).*?[Ss]igma_?min\s*[=:]\s*([0-9.eE+-]+)"),
    re.compile(r"Emax\s*[=:]?\s*([0-9.eE+-]+).*?Emin\s*[=:]?\s*([0-9.eE+-]+)"),
]


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
    """Return dump/echo proof tokens, terminal solves, per-solve residual segments, and any
    singular-value reading.  A residual segment is a run of `Main iteration` lines whose iter
    counter increases; a reset to a smaller iter starts a new segment (CD then CL)."""
    dump = {
        "jacMatReOrdering": (RE_DUMP_JACORD.search(text).group(1) if RE_DUMP_JACORD.search(text) else None),
        "KSPCalcSingularVal": (RE_DUMP_SINGVAL.search(text).group(1) if RE_DUMP_SINGVAL.search(text) else None),
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
    sv = None
    for rc in RE_SINGVAL_CANDS:
        m = rc.search(text)
        if m:
            try:
                smax, smin = float(m.group(1)), float(m.group(2))
                if smin != 0.0:
                    sv = {"sMax": smax, "sMin": smin, "ratio": smax / smin}
                    break
            except ValueError:
                continue
    return {"dump": dump, "terminals": terminals, "segments": segments, "singular": sv}


def check_proofs(leg, parsed):
    d = parsed["dump"]
    if d["transonicPCOption"] != "1":
        refuse("PROOF", {"leg": leg, "transonicPCOption": d["transonicPCOption"], "want": "1"})
    if d["jacMatReOrdering"] != "nd" or d["Mat ReOrdering"] != "nd":
        refuse("PROOF", {"leg": leg, "jacMatReOrdering": d["jacMatReOrdering"], "Mat ReOrdering": d["Mat ReOrdering"],
                         "note": "the nd lever's own echo is absent; the leg did not apply the lever"})
    if d["KSPCalcSingularVal"] != "1":
        refuse("PROOF", {"leg": leg, "KSPCalcSingularVal": d["KSPCalcSingularVal"], "want": "1"})
    if d["adjStateOrdering"] != "cell":
        refuse("PROOF", {"leg": leg, "adjStateOrdering": d["adjStateOrdering"], "want": "cell (held at baseline)"})
    if d["ILU PC Fill Level"] != "0":
        refuse("PROOF", {"leg": leg, "ILU PC Fill Level": d["ILU PC Fill Level"], "want": "0"})
    if d["GMRES Restart"] != "200":
        refuse("PROOF", {"leg": leg, "GMRES Restart": d["GMRES Restart"], "want": "200"})
    if RE_SUBLU.search("".join("%s %s" % kv for kv in d.items()) or ""):
        refuse("PROOF", {"leg": leg, "note": "sub-LU banner present; env must be unset"})
    return {"proofs_seen": True, "dump": d}


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
    """CONTROL requires all solves CONVERGED; TEST keys on the first (CD) solve."""
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
    else:  # TEST keys on CD (first solve)
        leg_state = solves[0]["state"]
    return {"leg": leg, "leg_state": leg_state, "solves": solves}


def g_diag(leg, parsed):
    sv = parsed["singular"]
    base = BASELINE_SMAX_OVER_SMIN.get(leg)
    if sv is None:
        return {"leg": leg, "singular": "NOT_MEASURED", "baseline_ratio": base,
                "note": "no singular-value token in the log; KSPCalcSingularVal print format unobserved on disk"}
    out = {"leg": leg, "sMax": sv["sMax"], "sMin": sv["sMin"], "ratio": sv["ratio"], "baseline_ratio": base}
    if base:
        out["ratio_over_baseline"] = sv["ratio"] / base
    return out


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
def compose_item(control, test, fd):
    """control/test are g_conv_leg outputs; fd is grade_fd output or None."""
    cs, ts = control["leg_state"], test["leg_state"]
    if cs == "NOT_EVALUABLE":
        return "BLOCKED", "CONTROL not evaluable (crash/OOM/memory before a reason)"
    if cs != "CONVERGED":
        return "NOT A RESULT", "CONTROL did not converge -> levers harmful; arm inconclusive"
    if ts == "NOT_EVALUABLE":
        return "BLOCKED", "TEST not evaluable (crash/OOM/memory before a reason)"
    if ts == "BUDGET_LIMITED":
        return "NOT A RESULT", "TEST -3 at cap but still descending: budget-limited, cap too small to decide"
    if ts == "DIVERGED_NOT_CAP":
        return "NOT A RESULT", "TEST negative reason but not at the cap: not a clean conditioning read"
    if ts == "STAGNATION":
        return "GATE FAIL", "TEST stagnation (flat -3 at cap, memory comfortable): levers did NOT clear it; conditioning finding reported"
    if ts == "CONVERGED":
        if fd is None:
            return "PENDING", "TEST converged; FD-verification leg owed (bright line, DAFOAM_CHARTER section 2)"
        if fd["verdict"] == "PASS":
            return "PASS", "TEST converged AND FD table passes the band: a new verified A3 rung"
        if fd["verdict"] == "GATE FAIL":
            return "GATE FAIL", "TEST converged but FD table fails band/sign (bright line)"
        return "NOT A RESULT", "TEST converged but FD leg not evaluable (fewer than MIN_GRADED)"
    return "NOT A RESULT", "unmapped test state %s" % ts


# ================= single-log grade + compose =========================================
def grade_leg(logpath, leg, fd_json=None, run_base=None):
    if leg not in LEGS:
        refuse("ARG", {"leg": leg, "want": list(LEGS)})
    text = open(logpath, errors="replace").read()
    proofs = check_proofs(leg, parse_log(text))
    parsed = parse_log(text)
    conv = g_conv_leg(leg, parsed)
    diag = g_diag(leg, parsed)
    out = {"item": "CURRICULUM-%s" % ITEM, "leg": leg, "log": logpath, "proofs": proofs,
           "G_CONV": conv, "G_DIAG": diag}
    if leg == "TEST" and fd_json and os.path.isfile(fd_json):
        F = read_F(fd_json)
        controls = {"instrument_ctrl": ctrl_control(F),
                    "grader_plant": grader_plant_control(run_base or os.path.dirname(fd_json), fd_json)}
        out["G_FD"] = grade_fd(F)
        out["controls"] = controls
    return out


# ================= selftest: planted fixtures =========================================
EXPECTED_UNITS = 26


def _dump_block(jac="nd", sv="1", state_ord="cell", tpc="1", mat="nd", fill="0", restart="200", maxit="4000"):
    return ("adjEqnSolMethod Krylov;\n    jacMatReOrdering %s;\n    KSPCalcEigen 0;\n"
            "    KSPCalcSingularVal %s;\n    adjStateOrdering %s;\n    transonicPCOption %s;\n"
            "GMRES Restart: %s\nMat ReOrdering: %s\nILU PC Fill Level: %s\nGMRES Max Iterations: %s\n"
            % (jac, sv, state_ord, tpc, restart, mat, fill, maxit))


def _trace(start_r, n, per100_factor, cap, reason, singular=None):
    """Build a residual trace + terminal line. per100_factor multiplies r every 100 iters."""
    lines, r = [], start_r
    it = 0
    while it <= n:
        lines.append("Main iteration %d KSP Residual norm %.12e %.2f s. " % (it, r, it * 0.35))
        r = r * per100_factor
        it += 100
    T = n
    term = "**Completed**! Total iterations: %d. PetscConvergedReason: %d. 1416 s\n" % (T, reason)
    sv_line = ""
    if singular:
        sv_line = "Extreme singular values: max = %.6e ; min = %.6e\n" % singular
    return "\n".join(lines) + "\n" + sv_line + term


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

    os.makedirs(tmp, exist_ok=True)
    # ---- CONTROL converged (two solves reason 2, below cap) ----
    ctrl_log = _dump_block(maxit="2000") + _trace(1.0, 900, 0.5, 2000, 2) + "\n" + _trace(1.0, 1100, 0.5, 2000, 2)
    p = os.path.join(tmp, "control.log"); open(p, "w").write(ctrl_log)
    r = grade_leg(p, "CONTROL")
    unit("U1 CONTROL two solves reason 2 below cap -> leg CONVERGED", r["G_CONV"]["leg_state"] == "CONVERGED")
    unit("U2 CONTROL solves classified CONVERGED each", all(s["state"] == "CONVERGED" for s in r["G_CONV"]["solves"][:2]))
    # ---- CONTROL collapse (reason -5) ----
    coll = _dump_block(maxit="2000") + _trace(1.0, 200, 1.0, 2000, -5)
    p = os.path.join(tmp, "control_collapse.log"); open(p, "w").write(coll)
    r = grade_leg(p, "CONTROL")
    unit("U3 CONTROL single -5 (not 2 solves) -> NOT_CONVERGED or NOT_EVALUABLE",
         r["G_CONV"]["leg_state"] in ("NOT_CONVERGED", "NOT_EVALUABLE"))
    # ---- TEST stagnation: -3 at cap 4000, flat tail ----
    flat = _dump_block() + _trace(2.121e-2, 4000, 1.0000001, 4000, -3, singular=(9.6e10, 1.0))
    # force a genuinely flat tail: overwrite with near-constant residuals
    lines = []
    it = 0
    while it <= 4000:
        rr = 1.615246e-2 + (2.121343e-2 - 1.615246e-2) * math.exp(-it / 150.0)  # decays early, flat by 1500
        lines.append("Main iteration %d KSP Residual norm %.12e %.2f s. " % (it, rr, it * 0.35))
        it += 100
    flat = _dump_block() + "\n".join(lines) + "\nExtreme singular values: max = 9.600000e+10 ; min = 1.000000e+00\n" \
        + "**Completed**! Total iterations: 4000. PetscConvergedReason: -3. 1416 s\n"
    p = os.path.join(tmp, "test_stag.log"); open(p, "w").write(flat)
    r = grade_leg(p, "TEST")
    unit("U4 TEST -3 at cap with flat tail -> STAGNATION", r["G_CONV"]["leg_state"] == "STAGNATION")
    unit("U5 TEST stagnation tail_rel_change < THETA_STAG", r["G_CONV"]["solves"][0]["tail_rel_change"] < THETA_STAG)
    unit("U6 TEST singular value parsed (sMax/sMin)", r["G_DIAG"].get("ratio") is not None and abs(r["G_DIAG"]["ratio"] - 9.6e10) < 1e6)
    # ---- TEST budget-limited: -3 at cap, still descending ----
    lines, it = [], 0
    while it <= 4000:
        rr = 1.0 * (0.999 ** (it / 100.0))  # steadily descending ~0.1%/100 iters -> > THETA_STAG over 1000
        lines.append("Main iteration %d KSP Residual norm %.12e %.2f s. " % (it, rr, it * 0.35))
        it += 100
    budg = _dump_block() + "\n".join(lines) + "\n**Completed**! Total iterations: 4000. PetscConvergedReason: -3. 1416 s\n"
    p = os.path.join(tmp, "test_budget.log"); open(p, "w").write(budg)
    r = grade_leg(p, "TEST")
    unit("U7 TEST -3 at cap still descending -> BUDGET_LIMITED", r["G_CONV"]["leg_state"] == "BUDGET_LIMITED")
    # ---- TEST converged ----
    convlog = _dump_block() + _trace(1.0, 1500, 0.5, 4000, 2)
    p = os.path.join(tmp, "test_conv.log"); open(p, "w").write(convlog)
    r = grade_leg(p, "TEST")
    unit("U8 TEST reason 2 below cap -> CONVERGED", r["G_CONV"]["leg_state"] == "CONVERGED")
    # ---- PROOF refusals ----

    def refused(fn):
        try:
            fn(); return False
        except Refusal:
            return True
    bad = _dump_block(jac="natural", mat="natural") + _trace(1.0, 1500, 0.5, 4000, 2)
    p = os.path.join(tmp, "bad_natural.log"); open(p, "w").write(bad)
    unit("U9 dump/echo still reading natural -> REFUSE (lever not applied)", refused(lambda: grade_leg(p, "TEST")))
    bad = _dump_block(sv="0") + _trace(1.0, 1500, 0.5, 4000, 2)
    p = os.path.join(tmp, "bad_sv0.log"); open(p, "w").write(bad)
    unit("U10 KSPCalcSingularVal 0 in dump -> REFUSE (diagnostic not on)", refused(lambda: grade_leg(p, "TEST")))
    bad = _dump_block(tpc="2") + _trace(1.0, 1500, 0.5, 4000, 2)
    p = os.path.join(tmp, "bad_tpc.log"); open(p, "w").write(bad)
    unit("U11 transonicPCOption 2 -> REFUSE", refused(lambda: grade_leg(p, "TEST")))
    bad = _dump_block(state_ord="state") + _trace(1.0, 1500, 0.5, 4000, 2)
    p = os.path.join(tmp, "bad_state.log"); open(p, "w").write(bad)
    unit("U12 adjStateOrdering drifted to state -> REFUSE", refused(lambda: grade_leg(p, "TEST")))
    # ---- NOT_EVALUABLE: no terminal ----
    noterm = _dump_block() + "Main iteration 0 KSP Residual norm 1.0 0.0 s. \n(crash)\n"
    p = os.path.join(tmp, "noterm.log"); open(p, "w").write(noterm)
    r = grade_leg(p, "TEST")
    unit("U13 no terminal reason -> leg NOT_EVALUABLE", r["G_CONV"]["leg_state"] == "NOT_EVALUABLE")
    # ---- G-DIAG NOT_MEASURED when no singular token ----
    unit("U14 no singular token -> G_DIAG NOT_MEASURED and named", r["G_DIAG"]["singular"] == "NOT_MEASURED")
    # ---- FD: clean -> PASS ----
    F = _fd_json(os.path.join(tmp, "fd_clean.json"))
    fd = grade_fd(read_F(F))
    unit("U15 FD clean (all ~0.5%) -> band D/E PASS, verdict PASS", fd["verdict"] == "PASS" and fd["n_graded"] == 3)
    # ---- FD: planted 7% on one component -> GATE FAIL ----
    F = _fd_json(os.path.join(tmp, "fd_err.json"), errs={("twist", 1): 7.0})
    fd = grade_fd(read_F(F))
    unit("U16 FD planted 7% error -> component + verdict GATE FAIL", fd["verdict"] == "GATE FAIL" and fd["n_gate_fail"] == 1)
    # ---- FD: sign flip -> GATE FAIL ----
    F = _fd_json(os.path.join(tmp, "fd_flip.json"), flip={("patchV", 1)})
    fd = grade_fd(read_F(F))
    unit("U17 FD sign flip -> GATE FAIL, flip counted", fd["verdict"] == "GATE FAIL" and fd["sign_flips"] == 1)
    # ---- FD: no plateau on one -> that component NOT A RESULT, still 2 graded -> PASS ----
    F = _fd_json(os.path.join(tmp, "fd_noplat.json"), noplateau={("shape", 115)})
    fd = grade_fd(read_F(F))
    unit("U18 FD one no-plateau -> that comp NOT A RESULT, 2 graded -> PASS", fd["verdict"] == "PASS" and fd["n_graded"] == 2)
    # ---- FD: two no-plateau -> 1 graded < MIN_GRADED -> NOT A RESULT ----
    F = _fd_json(os.path.join(tmp, "fd_noplat2.json"), noplateau={("shape", 115), ("twist", 1)})
    fd = grade_fd(read_F(F))
    unit("U19 FD two no-plateau -> 1 graded < MIN_GRADED -> NOT A RESULT", fd["verdict"] == "NOT A RESULT")
    # ---- planted controls ----
    F = _fd_json(os.path.join(tmp, "fd_ctrl.json"))
    unit("U20 instrument CTRL planted row SEEN", ctrl_control(read_F(F))["instrument_ctrl_zero"] == 0.0)
    unit("U21 grader-level plant SEEN on FD table", grader_plant_control(tmp, F)["grader_plant_seen"])
    F = _fd_json(os.path.join(tmp, "fd_ctrl_broken.json"), ctrl_ok=False)
    unit("U22 CTRL planted row broken -> REFUSE", refused(lambda: ctrl_control(read_F(F))))
    # ---- item composition (section 7 map) ----
    conv_ctrl = {"leg_state": "CONVERGED"}
    unit("U23 control valid + test stagnation -> GATE FAIL", compose_item(conv_ctrl, {"leg_state": "STAGNATION"}, None)[0] == "GATE FAIL")
    unit("U24 control valid + test converged + no FD -> PENDING", compose_item(conv_ctrl, {"leg_state": "CONVERGED"}, None)[0] == "PENDING")
    unit("U25 control not converged -> NOT A RESULT", compose_item({"leg_state": "NOT_CONVERGED"}, {"leg_state": "CONVERGED"}, None)[0] == "NOT A RESULT")
    unit("U26 control valid + test converged + FD PASS -> PASS", compose_item(conv_ctrl, {"leg_state": "CONVERGED"}, {"verdict": "PASS"})[0] == "PASS")
    # extra guards fold into vocabulary + assert-free (not counted toward EXPECTED_UNITS beyond)
    for v in ("BLOCKED", "GATE FAIL", "PENDING", "PASS", "NOT A RESULT"):
        if v not in VOCAB:
            fails.append("vocab %s" % v)
    print("A3FL1 GRADER SELFTEST units=%d expected=%d failures=%d" % (n, EXPECTED_UNITS, len(fails)))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("A3FL1 GRADER SELFTEST PASS %d/%d" % (n, EXPECTED_UNITS))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=None, help="a leg log to grade")
    ap.add_argument("--leg", default=None, choices=list(LEGS))
    ap.add_argument("--fd-json", default=None, help="TEST FD table JSON (only if TEST converged)")
    ap.add_argument("--run-base", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    a = ap.parse_args()
    if count_asserts(os.path.abspath(__file__)) != 0:
        print("REFUSAL: this comparator carries an assert statement (L-332)")
        return 2
    if a.selftest:
        d = os.path.join(a.tmpdir, "a3fl1_selftest_%d" % os.getpid())
        return selftest(d)
    if not a.log or not a.leg:
        print("usage: a3fl1_grade.py --log <leg log> --leg CONTROL|TEST [--fd-json F] [--out FILE] | --selftest")
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
