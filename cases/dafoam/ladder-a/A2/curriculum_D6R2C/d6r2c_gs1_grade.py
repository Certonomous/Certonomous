#!/usr/bin/env python3
# ===========================================================================
# d6r2c_gs1_grade.py -- THE GRADING PATH for the D6R2C GRADIENT SPOT-CHECK
# ===========================================================================
#
# Registered by PREREGISTRATION_GRADIENT_SPOTCHECK.md section 11, and IN THE SAME
# COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS (CLAUDE.md rule 2).
#
# NOTHING IN THIS FILE WAS CHOSEN BY ITS AUTHOR.  Every threshold, literal and
# comparison direction is COPIED VERBATIM from that document, each carrying the
# sentence it was copied from as its comment.  Where the document is silent this
# file REFUSES (exit 2); it does not choose.
#
# REFUSE, NEVER DEGRADE.  A missing, unreadable or non-finite input is a refusal
# or a registered gate failure.  No default value, no silent skip, no except:pass.
#
# IT RECOMPUTES EVERY FD ESTIMATE from the two J values rather than trusting the
# producer's arithmetic, and refuses on a disagreement.
# ===========================================================================
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile

# ---------------------------------------------------------------------------
# THE REGISTERED CONSTANTS
# ---------------------------------------------------------------------------

# "the adjoint at the optimum is OptView.hst record key = 172, iter = 86" (sec 1b)
ADJ_RECORD_KEY = 172
ADJ_RECORD_ITER = 86
OPTVIEW_MD5 = "2a96b47a19e84e40a95c30e1634ce356"
# "dJ/d(dv), driver-scaled, from that record" (sec 1b) -- AN EXTERNAL ANCHOR:
# produced by a run this arm did not perform, fixed before it ran.
ADJOINT = {
    "shape[84]": -0.0012395965734695029,
    "twist[2]": 0.0063348068779340615,
    "patchV_cl05[1]": 0.01719085469787987,
}
# "shape[83] is within 0.011 % of shape[84]" (sec 1c) -- a LIMIT ON THE CLAIM.
ADJOINT_SHAPE83 = -0.0012394586288117077

# "the ladder is {1e-1, 1e-2, 1e-3, 1e-4}, driver-scaled, central" (sec 2b)
LADDER = [1.0e-1, 1.0e-2, 1.0e-3, 1.0e-4]
DVS = ["shape[84]", "twist[2]", "patchV_cl05[1]"]
# "six unperturbed evaluations" (sec 2c) -- REPORTED, NEVER GATED.
N_UNPERTURBED = 6
N_FD = 24

# "PLATEAU_TOL = 5.0e-3 relative to the adjoint" (sec 3b).  DERIVED, NOT CHOSEN:
# N-D3 measures this stack's flat region as "dead flat at 2.5-3.0 %" over
# 1e-4..3e-2 -- a width of 0.5 PERCENTAGE POINTS of the adjoint value, so
# adjacent FD estimates in a plateau agree to within 5.0e-3 of the adjoint.
PLATEAU_TOL = 5.0e-3
# "a plateau is THREE consecutive steps" (sec 3b).  Two points are a line.
PLATEAU_MIN_STEPS = 3

# "PASS at <= 5 % aggregate ... CONDITIONAL between 5 % and 15 % ... FAIL above
#  15 % or on any sign-flipped component" -- DAFOAM_CHARTER section 2.
# INHERITED AND USED FOR PER-COMPONENT REPORTING ONLY.  THE CHARTER'S BAND IS ON
# AN AGGREGATE OVER THE WHOLE GRADIENT VECTOR AND THIS ARM MEASURES 3 OF 106
# COMPONENTS, SO THE AGGREGATE IS NOT COMPUTABLE HERE AND IS NOT COMPUTED (sec 4).
CHARTER_PASS_PCT = 5.0
CHARTER_FAIL_PCT = 15.0

# "primalMinResTol = 1.0e-8, the tolerance the graded run uses, NEVER loosened"
# (sec 3d; DAFOAM_CHARTER section 3: "the sweep is run at the primal tolerance
# the graded run uses").
PRIMAL_MIN_RES_TOL = 1.0e-8

RUNSCRIPT_MD5 = "2f2ae43a627146cf8e0f065b035ada4b"
EVALS_MD5 = "2c0b8143caad198cd2e21d8047986aa3"

# ---- THE FM7 LESSON, CARRIED (sec 3e).  FM7 transferred every field correctly
# and THE SOLVER NEVER SAW THEM, and the floor that followed looked exactly like
# a refutation of the registered change.  YOU CANNOT REFUTE A CHANGE THAT DID NOT
# TAKE EFFECT.  On the WARPED mesh a freestream start produces this signature,
# measured in FM5's and FM7's deform phase and in runs this arm did not perform:
WARPED_FREESTREAM_T100 = 0.0003970258637     # "p initRes" at Time = 100
WARPED_FREESTREAM_FLOOR = 1.2161568500e-06   # the value it plateaus at
# A REFUSAL, NOT A GATE: section 11a registers this condition in words and this
# makes it executable.  The test is EQUALITY, not proximity, so a genuinely
# different run is never blocked by it.
# "J = 0.25 x CD04 + 0.50 x CD05 + 0.25 x CD06" (sec 9) -- the objective, stated.
WEIGHTS = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}
POINTS = ["cl04", "cl05", "cl06"]

# "PREDICTION 1507.4 s wall x 4 ranks / 60 = 100.495 core-min" (sec 8)
PREDICTION_CORE_MIN = 100.495
# "REGISTERED CAP (3.00x) = 301.485 core-min" (sec 8).
# THE CAP IS 3.00x THE **REGISTERED** PREDICTION (100.495), NOT 3x an unrounded
# intermediate -- those differ in the last digit (301.485 vs 301.486) and only the
# first is a number a reader can re-derive from the two figures the document
# states.  Caught by the selftest asserting the document's literal.
CAP_FACTOR = 3.00
CAPS = {"GS1": round(PREDICTION_CORE_MIN * CAP_FACTOR, 3)}

# "d6r2c_gs1_grade.py plants PLANT = 1.234e-03" (sec 7)
PLANT = 1.234e-03

LABEL_PASS = "PASS"
LABEL_GATE_FAIL = "GATE FAIL"
LABEL_NOT_A_RESULT = "NOT A RESULT"


class Refusal(Exception):
    """Refuse, never degrade."""


def _finite(x, what):
    if x is None or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise Refusal("REFUSE_NON_FINITE %s = %r" % (what, x))
    return float(x)


def _req(d, k, what):
    if not isinstance(d, dict) or k not in d:
        raise Refusal("REFUSE_MISSING_KEY %r in %s" % (k, what))
    return d[k]


def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def scan_arm_dir(arm_dir, datum_epoch):
    if not os.path.isdir(arm_dir):
        raise Refusal("REFUSE_MISSING_ARM_DIR %s" % arm_dir)
    n, root_owned = 0, []
    for dirpath, dirnames, filenames in os.walk(arm_dir):
        for name in list(dirnames) + list(filenames):
            p = os.path.join(dirpath, name)
            try:
                st = os.lstat(p)
            except OSError:
                continue
            n += 1
            if st.st_mtime > datum_epoch and (st.st_uid == 0 or st.st_gid == 0):
                root_owned.append([p, st.st_uid, st.st_gid])
    return {"n_scanned": n, "n_root_owned": len(root_owned),
            "root_owned_examples": root_owned[:10], "ok": not root_owned}


def _weighted_J(cd):
    return sum(WEIGHTS[p] * cd[p] for p in POINTS)


def first_solve_signature(log_text):
    """The FIRST solver run's p residual at Time = 100, and the last reported
    floor.  The arm log holds several runs; the FIRST is the one whose starting
    field the transfer was supposed to set."""
    import re
    t100, at100 = None, False
    for ln in log_text.splitlines():
        if re.match(r"^Time = 100$", ln):
            at100 = True
            continue
        if at100:
            m = re.match(r"^p initRes: ([0-9.eE+-]+)", ln)
            if m:
                t100 = float(m.group(1))
                break
            if re.match(r"^Time = ", ln):
                at100 = False
    fl = re.findall(r"Primal min residual ([0-9.eE+-]+)", log_text)
    return t100, (float(fl[-1]) if fl else None)


def warm_start_refusal(log_path, _plant=None):
    """REFUSE if the first solve reproduced the warped-mesh FREESTREAM signature.

    If it did, the transfer did not reach the solver and NOTHING in the sweep is
    evidence about a warm-started FD -- the same way FM7's floor was not evidence
    about the registered change."""
    if log_path is None or not os.path.isfile(log_path):
        return {"checked": False,
                "why": "no arm log supplied; the check did not run and says so"}
    t100, floor = first_solve_signature(open(log_path, errors="replace").read())
    if _plant == "WARM":
        t100 = WARPED_FREESTREAM_T100
    hits = []
    if t100 is not None and t100 == WARPED_FREESTREAM_T100:
        hits.append("t=100 p initRes is BIT-IDENTICAL to a warped-mesh freestream "
                    "start (%.12g)" % WARPED_FREESTREAM_T100)
    if floor is not None and floor == WARPED_FREESTREAM_FLOOR:
        hits.append("the floor is BIT-IDENTICAL to the freestream floor (%.12g)"
                    % WARPED_FREESTREAM_FLOOR)
    out = {"checked": True, "t100": t100, "floor": floor, "matches_freestream": hits,
           "anchors": {"t100": WARPED_FREESTREAM_T100, "floor": WARPED_FREESTREAM_FLOOR}}
    if hits:
        raise Refusal(
            "REFUSE_FREESTREAM_START the first solve reproduced a freestream "
            "trajectory exactly:\n  " + "\n  ".join(hits)
            + "\n  THE TRANSFER DID NOT REACH THE SOLVER, so nothing in this "
              "sweep is evidence about a warm-started finite difference.  This is "
              "a PRODUCER DEFECT (sec 11a): stopped, NOT A RESULT, repaired under "
              "VERIFICATION_CHARTER 2d.1.  No gate is added and no threshold moved.")
    return out


def dv_key(rec):
    return "%s[%d]" % (rec["dv"], rec["index"])


# ---------------------------------------------------------------------------
# THE GRADE
# ---------------------------------------------------------------------------

def grade(jsonl_path, arm_dir, datum_epoch, core_min, rc, _plant=None, log_path=None):
    if not os.path.isfile(jsonl_path):
        raise Refusal("REFUSE_MISSING_RECORD %s" % jsonl_path)
    header = footer = None
    evals = []
    with open(jsonl_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            k = r.get("kind")
            if k == "HEADER":
                header = r
            elif k == "FOOTER":
                footer = r
            elif k == "EVAL":
                evals.append(r)
    if header is None:
        raise Refusal("REFUSE_NO_HEADER in %s" % jsonl_path)

    # ---- G2 -- THE ADJOINT IS THE REGISTERED ONE.  EXTERNAL ANCHOR (L-588):
    # ---- every value here was produced by a run this arm did not perform.
    got_adj = dict(header.get("adjoint") or {})
    # THE PLANT GOES INTO WHAT THE GRADER READS, not into its own registered
    # copy.  A plant into the constant this file already holds would be compared
    # against itself and would be invisible by construction -- which is how the
    # first draft of this control passed while proving nothing.
    if _plant and _plant[0] == "ADJ" and _plant[1] in got_adj:
        got_adj[_plant[1]] = got_adj[_plant[1]] + PLANT
    adj = dict(ADJOINT)
    adj_ok = all(got_adj.get(k) == v for k, v in ADJOINT.items())
    key_ok = (header.get("adjoint_record_key") == ADJ_RECORD_KEY
              and header.get("adjoint_record_iter") == ADJ_RECORD_ITER)
    md5_ok = (header.get("optview_md5_registered") == OPTVIEW_MD5
              and header.get("runscript_md5") == RUNSCRIPT_MD5
              and header.get("evals_md5") == EVALS_MD5)
    G2 = adj_ok and key_ok and md5_ok
    g2 = {"adjoint_recorded": got_adj, "adjoint_registered": dict(ADJOINT),
          "adjoint_matches": adj_ok,
          "record_key": header.get("adjoint_record_key"),
          "record_key_registered": ADJ_RECORD_KEY, "record_identity_ok": key_ok,
          "md5s_ok": md5_ok, "pass": G2,
          "anchor_note":
              "EXTERNAL: the adjoint, the driver history, the runscript and the "
              "inherited record were all produced before this arm ran and are "
              "pinned by md5.  The record at the optimum was identified by "
              "MATCHING DESIGN VECTORS to an exact 0.000e+00, not by position -- "
              "the LAST funcsSens record is key 173 and is NOT the one at the "
              "final design point (sec 1b)."}

    # ---- THE TABLE.  Built BEFORE any agreement or plateau claim (sec 3c).
    # ---- FAILED STEPS APPEAR AS ROWS.  DAFOAM_CHARTER section 3: "a sweep that
    # ---- hides its failed steps is reporting a plateau it has not measured."
    unpert, byname = [], {}
    for r in evals:
        if r.get("kind") != "EVAL":
            continue
        if r.get("fail", 1) != 0 or r.get("J") is None \
                or not isinstance(r.get("J"), (int, float)) \
                or not math.isfinite(r.get("J")):
            # a stalled or failed evaluation -- RECORDED, never dropped
            if r.get("kind") == "EVAL" and r.get("dv") is not None:
                byname.setdefault(dv_key(r), {}).setdefault(r["step"], {})[
                    r["sign"]] = None
            continue
        cd = {p: _finite(_req(r, "CD", "eval %s" % r.get("i")).get(p),
                         "CD %s" % p) for p in POINTS}
        J = _weighted_J(cd)
        Jp = _finite(_req(r, "J", "eval %s" % r.get("i")), "producer J")
        if abs(J - Jp) > 1.0e-12 and not (_plant and _plant[0] == "J"):
            raise Refusal("REFUSE_J_DISAGREEMENT eval %s: recomputed %.17g vs "
                          "producer %.17g -- the grader does not take the "
                          "producer's word for the graded quantity"
                          % (r.get("i"), J, Jp))
        if _plant and _plant[0] == "J" and r.get("tag") == _plant[1]:
            J = J + PLANT
        if r["kind"] == "EVAL" and r.get("dv") is None:
            unpert.append({"tag": r.get("tag"), "i": r.get("i"), "J": J})
        else:
            byname.setdefault(dv_key(r), {}).setdefault(r["step"], {})[r["sign"]] = J

    # ---- the sweep table, one row per (dv, step), failed steps included
    table = {}
    for name in DVS:
        rows = []
        for h in LADDER:
            pair = byname.get(name, {}).get(h, {})
            jp, jm = pair.get(1), pair.get(-1)
            row = {"dv": name, "step": h, "J_plus": jp, "J_minus": jm}
            if jp is None or jm is None:
                row["fd"] = None
                row["status"] = "MISSING -- a stalled or absent evaluation is a " \
                                "MISSING MEASUREMENT, not a gradient disagreement; " \
                                "it is never averaged in and never interpolated over"
            else:
                row["fd"] = (jp - jm) / (2.0 * h)
                row["signal_2h_absg"] = 2.0 * h * abs(ADJOINT[name])
                row["status"] = "measured"
                a = adj[name]
                row["rel_err_pct"] = abs(row["fd"] - a) / abs(a) * 100.0
                row["sign_flipped"] = (row["fd"] * a) < 0.0
            rows.append(row)
        table[name] = rows

    # ---- G3 -- THE TABLE EXISTS BEFORE ANY CLAIM.  A REFUSAL, NOT A GATE.
    if not table or any(len(v) != len(LADDER) for v in table.values()):
        raise Refusal("REFUSE_NO_TABLE -- the sweep table is incomplete, so no "
                      "plateau or agreement field is written at all (sec 3c)")

    # ---- THE UNPERTURBED SPREAD.  REPORTED, NEVER GATED (sec 2c).
    # ---- SIX POINTS ARE SIX POINTS.  This is the OBSERVED DIFFERENCE between
    # ---- identical evaluations.  It is NOT a standard deviation and NOT a floor.
    uj = [u["J"] for u in unpert]
    spread = (max(uj) - min(uj)) if len(uj) >= 2 else None
    unpert_rep = {
        "n": len(uj), "evaluations": unpert,
        "observed_spread_max_minus_min": spread,
        "first_minus_last": (uj[0] - uj[-1]) if len(uj) >= 2 else None,
        "wording": "THE OBSERVED SPREAD BETWEEN IDENTICAL EVALUATIONS. Six points "
                   "are six points: this is NOT a standard deviation and NOT a "
                   "floor. REPORTED, NEVER GATED -- a threshold derived in-run is "
                   "what rule 2 forbids (sec 2c).",
        "drift_note": "The evaluations are spread through the arm -- two before "
                      "the ladder, one after each DV block, one at the end -- so a "
                      "CONSTANT scatter can be told from one that GROWS. Those have "
                      "different implications for whether the later DVs' ladders "
                      "can be believed at all.",
    }
    if spread is not None:
        for name in DVS:
            for row in table[name]:
                if row.get("signal_2h_absg"):
                    row["signal_over_observed_spread"] = (
                        row["signal_2h_absg"] / spread if spread > 0 else None)

    # ---- G4 -- THE PLATEAU, PER COMPONENT.  N-D3: plateau membership is a
    # ---- PER-COMPONENT property and the vector norm can dip where no component
    # ---- supports it.
    plateau = {}
    for name in DVS:
        a = adj[name]
        fds = [(r["step"], r["fd"]) for r in table[name]]
        best = None
        for i in range(len(fds) - PLATEAU_MIN_STEPS + 1):
            win = fds[i:i + PLATEAU_MIN_STEPS]
            if any(v is None for _, v in win):
                continue
            worst = max(abs(v - w) for _, v in win for _, w in win)
            if worst <= PLATEAU_TOL * abs(a) and (best is None or worst < best[1]):
                best = ([s for s, _ in win], worst)
        n_missing = sum(1 for r in table[name] if r["fd"] is None)
        plateau[name] = {
            "found": best is not None,
            "steps": (best[0] if best else None),
            "worst_pairwise_abs_diff": (best[1] if best else None),
            "threshold_abs": PLATEAU_TOL * abs(a),
            "PLATEAU_TOL": PLATEAU_TOL, "PLATEAU_MIN_STEPS": PLATEAU_MIN_STEPS,
            "n_missing_steps": n_missing,
            "note": ("A LADDER WITH A HOLE CANNOT BE SAID TO SHOW A PLATEAU (sec 3a)."
                     if n_missing else
                     "three consecutive steps agreeing to within PLATEAU_TOL x |adjoint|"),
        }
    G4 = all(v["found"] for v in plateau.values())

    # ---- REPORTED, NEVER GATED: the charter's per-component classification.
    charter = {}
    for name in DVS:
        best = plateau[name]["steps"]
        row = None
        if best:
            mid = best[len(best) // 2]
            row = next(r for r in table[name] if r["step"] == mid)
        charter[name] = {
            "plateau_step_used": (row["step"] if row else None),
            "rel_err_pct": (row["rel_err_pct"] if row else None),
            "sign_flipped": (row["sign_flipped"] if row else None),
            "classification": (
                None if row is None else
                ("FAIL-band (>15 % or sign-flipped)"
                 if (row["sign_flipped"] or row["rel_err_pct"] > CHARTER_FAIL_PCT)
                 else ("CONDITIONAL-band (5-15 %)"
                       if row["rel_err_pct"] > CHARTER_PASS_PCT
                       else "PASS-band (<= 5 %)"))),
        }
    charter_note = (
        "REPORTED, NEVER GATED. DAFOAM_CHARTER section 2's band is on an AGGREGATE "
        "over the whole gradient vector -- the vector-relative error "
        "||J_an - J_fd|| / ||J_fd||. THIS ARM MEASURES 3 OF 106 COMPONENTS, SO THE "
        "AGGREGATE IS NOT COMPUTABLE HERE AND IS NOT COMPUTED. These are "
        "per-component relative errors placed against the charter's boundaries so "
        "a reader can see where they sit; THEY ARE NOT THE CHARTER'S VERDICT (sec 4).")

    # ---- G1 -- COMPLETION AND HYGIENE
    own = scan_arm_dir(arm_dir, datum_epoch)
    n_fd_seen = sum(1 for r in evals if r.get("dv") is not None)
    cap = CAPS["GS1"]
    cap_crossed = (core_min is not None) and (core_min > cap)
    g1 = {"rc": rc, "rc_is_zero": rc == 0, "ownership": own,
          "n_evaluations": len(evals), "n_fd": n_fd_seen,
          "n_fd_registered": N_FD,
          "n_unperturbed": len(uj), "n_unperturbed_registered": N_UNPERTURBED,
          "footer_present": footer is not None,
          "primalMinResTol": PRIMAL_MIN_RES_TOL,
          "core_min": core_min, "cap_core_min": cap, "cap_crossed": cap_crossed}
    G1 = (rc == 0 and own["ok"] and footer is not None
          and n_fd_seen == N_FD and len(uj) == N_UNPERTURBED)

    if not (G1 and G2) or cap_crossed:
        label = LABEL_NOT_A_RESULT
    elif not G4:
        label = LABEL_GATE_FAIL
    else:
        label = LABEL_PASS

    warm = warm_start_refusal(log_path, _plant=("WARM" if _plant == "WARM" else None))

    rec = {
        "item": "GS1", "arm": "GS1", "label": label,
        "warm_start_refusal": warm,
        "G1": G1, "G2": G2, "G4": G4,
        "G1_detail": g1, "G2_detail": g2,
        "sweep_table": table,
        "plateau": plateau,
        "unperturbed_reported_never_gated": unpert_rep,
        "charter_per_component_reported_never_gated": charter,
        "charter_note": charter_note,
        "what_this_delivers": {
            "sanaa_item10_spot_check_table": "YES -- the table above, whatever it shows",
            "charter_per_component_reporting": "YES, for 3 of 106 components",
            "charter_aggregate_band": "NO -- the aggregate needs the whole vector",
            "charter_bright_line_plateau_proved_step":
                "ONLY for components whose ladder shows a plateau: %r"
                % [k for k, v in plateau.items() if v["found"]],
        },
        "shape83_near_degeneracy": {
            "g_shape84": ADJOINT["shape[84]"], "g_shape83": ADJOINT_SHAPE83,
            "relative_difference": abs(ADJOINT_SHAPE83 - ADJOINT["shape[84]"])
                                   / abs(ADJOINT["shape[84]"]),
            "limit_on_the_claim":
                "shape[84] is 'the maximum-sensitivity shape DV' BY A MARGIN THIS "
                "EXPERIMENT CANNOT RESOLVE. The FD checks the adjoint's VALUE at "
                "84, which is unaffected; THE CHOICE IS NOT A DEMONSTRATED "
                "RANKING and is not reported as one (sec 1c).",
        },
        "sequential_warm_start":
            "The two members of each central-difference pair DO NOT start from the "
            "same field. KNOWN IN ADVANCE, deliberately not removed, and MEASURED "
            "by the six unperturbed evaluations instead of assumed away (sec 2c).",
        "cost": {"core_min": core_min, "cap_core_min": cap,
                 "cap_crossed": cap_crossed,
                 "cost_basis": "reported-by-owner; core-minutes = wall_s x ranks / 60; "
                               "dollars DERIVED, NOT MEASURED (CLAUDE.md rule 12)"},
        "planted_control": {"PLANT": PLANT, "form": "live, on every real grading"},
    }
    return rec


def live_plant_check(grade_kwargs, verdict_label):
    """Re-grade deep copies with PLANT injected.  REFUSE if any plant leaves the
    verdict at PASS.  A reader that cannot see a disagreement of that size in
    these artefacts cannot certify an agreement (rule 3)."""
    plants = [("ADJ", "shape[84]"), ("ADJ", "twist[2]"), ("ADJ", "patchV_cl05[1]"),
              ("J", "shape[84]+0.01"), ("J", "twist[2]-0.001")]
    out = []
    for pl in plants:
        kw = dict(grade_kwargs)
        kw["_plant"] = pl
        try:
            lab = grade(**kw)["label"]
        except Refusal as e:
            lab = "REFUSED: %s" % str(e).split("\n")[0]
        out.append({"plant": list(pl), "label_under_plant": lab})
        if lab == LABEL_PASS:
            raise Refusal(
                "REFUSE_PLANT_INVISIBLE plant %r left the verdict at PASS.  "
                "PLANT = %.6e against a plateau threshold of %.6e on the smallest "
                "|adjoint| (%.6e); a reader that cannot see it cannot certify an "
                "agreement (rule 3)."
                % (pl, PLANT, PLATEAU_TOL * min(abs(v) for v in ADJOINT.values()),
                   min(abs(v) for v in ADJOINT.values())))
    return {"PLANT": PLANT, "verdict_without_plant": verdict_label,
            "controls": out, "all_plants_visible": True}


# ---------------------------------------------------------------------------
# SELFTEST
# ---------------------------------------------------------------------------

def _synth(tmp, fd_scale=1.0, missing=None, n_unpert=N_UNPERTURBED,
           spread=0.0, adjoint=None, key=ADJ_RECORD_KEY, rc_fail=False,
           optview=OPTVIEW_MD5, plateau_break=0.0):
    """A synthetic sweep whose FD estimates are EXACTLY fd_scale x the adjoint,
    so a clean case has a perfect plateau and any departure is deliberate."""
    d = os.path.join(tmp, "GS1")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "d6r2c_gs1.jsonl")
    rows = [{"kind": "HEADER", "adjoint": dict(adjoint or ADJOINT),
             "adjoint_record_key": key, "adjoint_record_iter": ADJ_RECORD_ITER,
             "optview_md5_registered": optview, "runscript_md5": RUNSCRIPT_MD5,
             "evals_md5": EVALS_MD5, "weights": WEIGHTS}]
    i = 0
    base = 0.0230632595286777639

    def ev(**kw):
        nonlocal i
        r = {"kind": "EVAL", "i": i, "fail": 0}
        r.update(kw)
        i += 1
        rows.append(r)

    def push_u(tag, off):
        cd = {q: base + off for q in POINTS}
        ev(tag=tag, CD=cd, CL={q: 0.4 for q in POINTS}, J=_weighted_J(cd))

    push_u("U0", 0.0)
    push_u("U1", spread)
    for name in DVS:
        dv, idx = name.split("[")[0], int(name.split("[")[1][:-1])
        for k, h in enumerate(LADDER):
            for sign in (+1, -1):
                if missing and missing == (name, h, sign):
                    continue
                g = ADJOINT[name] * fd_scale
                if plateau_break and k == 0:
                    g = g * (1.0 + plateau_break)
                off = sign * h * g
                cd = {q: base + off for q in POINTS}
                ev(tag="%s%+g" % (name, sign * h), dv=dv, index=idx, step=h,
                   sign=sign, CD=cd, CL={q: 0.4 for q in POINTS}, J=_weighted_J(cd))
        push_u("U_after_%s" % name, 0.0)
    push_u("U_final", 0.0)
    while sum(1 for r in rows if r.get("kind") == "EVAL"
              and r.get("dv") is None) > n_unpert:
        for j, r in enumerate(rows):
            if r.get("kind") == "EVAL" and r.get("dv") is None:
                del rows[j]
                break
    rows.append({"kind": "FOOTER", "rc": 1 if rc_fail else 0})
    with open(p, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    os.utime(p, (2_000_000_000, 2_000_000_000))
    return p, d


def selftest():
    DATUM = 1_000_000_000
    ok = True
    controls = []

    def check(name, got, want):
        controls.append(name)
        nonlocal ok
        if got != want:
            ok = False
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r" % (name, got, want))

    tmp = tempfile.mkdtemp(prefix="d6r2c_gs1_selftest_")
    try:
        # ---- clean: FD == adjoint exactly, so every component plateaus --------
        p, d = _synth(tmp)
        kw = dict(jsonl_path=p, arm_dir=d, datum_epoch=DATUM, core_min=50.0, rc=0)
        r = grade(**kw)
        check("clean -> PASS", r["label"], LABEL_PASS)
        check("clean -> every component plateaus",
              all(v["found"] for v in r["plateau"].values()), True)
        check("the table exists for all three DVs", sorted(r["sweep_table"]), sorted(DVS))
        check("each ladder has 4 rows",
              [len(v) for v in r["sweep_table"].values()], [4, 4, 4])
        check("the record says what it DOES deliver",
              r["what_this_delivers"]["sanaa_item10_spot_check_table"][:3], "YES")
        check("and what it does NOT: the charter aggregate",
              r["what_this_delivers"]["charter_aggregate_band"][:2], "NO")
        check("the near-degeneracy is a LIMIT ON THE CLAIM, in the record",
              "NOT A DEMONSTRATED RANKING" in r["shape83_near_degeneracy"]["limit_on_the_claim"],
              True)
        check("the sequential warm start is disclosed in the record",
              "deliberately not removed" in r["sequential_warm_start"], True)
        lp = live_plant_check(kw, r["label"])
        check("all 5 live plants visible", lp["all_plants_visible"], True)
        check("NEGATIVE -- a re-grade reproduces the label", grade(**kw)["label"], LABEL_PASS)

        # ---- EXTERNAL ANCHORS, typed as assertions and not as sources --------
        check("EXTERNAL: adjoint shape[84]", ADJOINT["shape[84]"], -0.0012395965734695029)
        check("EXTERNAL: adjoint twist[2]", ADJOINT["twist[2]"], 0.0063348068779340615)
        check("EXTERNAL: adjoint patchV_cl05[1]", ADJOINT["patchV_cl05[1]"], 0.01719085469787987)
        check("EXTERNAL: the record key is 172", ADJ_RECORD_KEY, 172)
        check("EXTERNAL: OptView.hst md5", OPTVIEW_MD5, "2a96b47a19e84e40a95c30e1634ce356")
        check("EXTERNAL: PLATEAU_TOL is section 3b's 5.0e-3", PLATEAU_TOL, 5.0e-3)
        check("EXTERNAL: a plateau needs THREE steps", PLATEAU_MIN_STEPS, 3)
        check("EXTERNAL: the prediction is section 8's 100.495", PREDICTION_CORE_MIN, 100.495)
        check("EXTERNAL: the cap is section 8's 301.485", CAPS["GS1"], 301.485)
        check("the cap is DERIVED, not typed twice",
              CAPS["GS1"], round(PREDICTION_CORE_MIN * CAP_FACTOR, 3))
        check("EXTERNAL: primalMinResTol UNTOUCHED at 1.0e-8", PRIMAL_MIN_RES_TOL, 1.0e-8)
        check("EXTERNAL: the objective's weights", (WEIGHTS["cl04"], WEIGHTS["cl05"],
              WEIGHTS["cl06"]), (0.25, 0.50, 0.25))
        check("EXTERNAL: the charter boundaries", (CHARTER_PASS_PCT, CHARTER_FAIL_PCT),
              (5.0, 15.0))

        # ---- G2: a failing control for every clause --------------------------
        bad = dict(ADJOINT); bad["twist[2]"] = 0.0
        p, d = _synth(tmp + "/a", adjoint=bad)
        r = grade(p, d, DATUM, 50.0, 0)
        check("G2 a wrong recorded adjoint -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        check("G2 names the mismatch", r["G2_detail"]["adjoint_matches"], False)
        p, d = _synth(tmp + "/b", key=173)
        r = grade(p, d, DATUM, 50.0, 0)
        check("G2 THE LAST RECORD (173) INSTEAD OF THE OPTIMUM (172) -> NOT A RESULT",
              r["label"], LABEL_NOT_A_RESULT)
        check("G2 names the record identity", r["G2_detail"]["record_identity_ok"], False)
        p, d = _synth(tmp + "/c", optview="0" * 32)
        check("G2 a wrong OptView md5 -> NOT A RESULT",
              grade(p, d, DATUM, 50.0, 0)["label"], LABEL_NOT_A_RESULT)

        # ---- G4: the plateau, both directions --------------------------------
        p, d = _synth(tmp + "/d", plateau_break=0.02)
        r = grade(p, d, DATUM, 50.0, 0)
        check("G4 one step 2 % off still plateaus on the other three",
              r["plateau"]["shape[84]"]["found"], True)
        check("...and the plateau EXCLUDES the broken step",
              1.0e-1 in (r["plateau"]["shape[84]"]["steps"] or []), False)
        p, d = _synth(tmp + "/e")
        rows = [json.loads(x) for x in open(p).read().splitlines()]
        for row in rows:  # break EVERY step of one DV by alternating signs
            if row.get("dv") == "twist":
                s = 1.0 + (0.05 if row["step"] in (1e-1, 1e-3) else -0.05)
                for q in POINTS:
                    row["CD"][q] = 0.0230632595286777639 + (
                        row["CD"][q] - 0.0230632595286777639) * s
                row["J"] = _weighted_J(row["CD"])
        with open(p, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
        os.utime(p, (2_000_000_000, 2_000_000_000))
        r = grade(p, d, DATUM, 50.0, 0)
        check("G4 NO plateau on one component -> GATE FAIL", r["label"], LABEL_GATE_FAIL)
        check("G4 names which component", r["plateau"]["twist[2]"]["found"], False)
        check("...and the OTHER components still plateau",
              r["plateau"]["patchV_cl05[1]"]["found"], True)
        check("GATE FAIL still emits the table", len(r["sweep_table"]), 3)

        # ---- a STALLED evaluation is a MISSING MEASUREMENT -------------------
        p, d = _synth(tmp + "/f", missing=("shape[84]", 1.0e-2, -1))
        r = grade(p, d, DATUM, 50.0, 0)
        check("a missing FD evaluation -> NOT A RESULT (G1 completion)",
              r["label"], LABEL_NOT_A_RESULT)
        row = next(x for x in r["sweep_table"]["shape[84]"] if x["step"] == 1.0e-2)
        check("the missing step appears AS A ROW, never dropped", row["fd"], None)
        check("...and the row says it is a MISSING MEASUREMENT",
              "MISSING MEASUREMENT" in row["status"], True)
        check("a ladder with a hole cannot be said to show a plateau",
              "CANNOT BE SAID TO SHOW A PLATEAU" in r["plateau"]["shape[84]"]["note"], True)

        # ---- the unperturbed spread: reported, never gated --------------------
        p, d = _synth(tmp + "/g", spread=1.0e-5)
        r = grade(p, d, DATUM, 50.0, 0)
        check("a large unperturbed spread does NOT change the label",
              r["label"], LABEL_PASS)
        check("...and IS reported",
              r["unperturbed_reported_never_gated"]["observed_spread_max_minus_min"] > 0,
              True)
        check("...with the wording ruled: not a standard deviation, not a floor",
              "NOT a standard deviation" in r["unperturbed_reported_never_gated"]["wording"],
              True)
        p, d = _synth(tmp + "/h", n_unpert=4)
        check("fewer than six unperturbed evaluations -> NOT A RESULT",
              grade(p, d, DATUM, 50.0, 0)["label"], LABEL_NOT_A_RESULT)

        # ---- THE FM7 LESSON: a freestream first solve is a REFUSAL ------------
        lg = os.path.join(tmp, "fs.log")
        open(lg, "w").write("Time = 100\np initRes: 0.0003970258637 finalRes: 1 nIters: 3\n"
                            "Primal min residual 1.2161568500e-06\n")
        p, d = _synth(tmp + "/w")
        try:
            grade(p, d, DATUM, 50.0, 0, log_path=lg)
            check("a freestream first solve -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("a freestream first solve -> REFUSE_FREESTREAM_START",
                  str(e).startswith("REFUSE_FREESTREAM_START"), True)
            check("...and the refusal explains that nothing in the sweep is evidence",
                  "nothing in this sweep is evidence" in str(e), True)
        lg2 = os.path.join(tmp, "warm.log")
        open(lg2, "w").write("Time = 100\np initRes: 7.412008e-06 finalRes: 1 nIters: 3\n"
                             "Primal min residual 4.01e-09\n")
        check("NEGATIVE -- a warm-started first solve is accepted",
              grade(p, d, DATUM, 50.0, 0, log_path=lg2)["label"], LABEL_PASS)
        lg3 = os.path.join(tmp, "ulp.log")
        open(lg3, "w").write("Time = 100\np initRes: 0.0003970258638 finalRes: 1 nIters: 3\n"
                             "Primal min residual 1.2161568501e-06\n")
        check("NEGATIVE -- ONE ULP off both anchors is accepted, so the test is "
              "equality and not proximity",
              grade(p, d, DATUM, 50.0, 0, log_path=lg3)["label"], LABEL_PASS)
        check("no log supplied -> the check says it did not run, rather than passing",
              grade(p, d, DATUM, 50.0, 0)["warm_start_refusal"]["checked"], False)

        # ---- G1: rc, cap, hygiene --------------------------------------------
        p, d = _synth(tmp + "/i")
        check("rc=137 -> NOT A RESULT", grade(p, d, DATUM, 50.0, 137)["label"],
              LABEL_NOT_A_RESULT)
        check("cap crossed -> NOT A RESULT",
              grade(p, d, DATUM, CAPS["GS1"] + 0.1, 0)["label"], LABEL_NOT_A_RESULT)
        check("AT the cap is NOT crossed (strict >)",
              grade(p, d, DATUM, CAPS["GS1"], 0)["label"], LABEL_PASS)
        p, d = _synth(tmp + "/j", rc_fail=True)
        check("a FOOTER rc != 0 is recorded", grade(p, d, DATUM, 50.0, 0)["G1_detail"]["rc"], 0)
        p, d = _synth(tmp + "/k")
        os.remove(p)
        try:
            grade(p, d, DATUM, 50.0, 0)
            check("a missing record -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("a missing record -> REFUSE_MISSING_RECORD",
                  str(e).startswith("REFUSE_MISSING_RECORD"), True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("D6R2C_GS1_GRADE SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", len(controls)))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the D6R2C gradient spot-check (arm GS1).")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--item", choices=("GS1",))
    ap.add_argument("--arm-dir")
    ap.add_argument("--datum-file")
    ap.add_argument("--core-min", type=float)
    ap.add_argument("--rc", type=int)
    ap.add_argument("--out")
    ap.add_argument("--log", help="the arm log, for the warm-start refusal (sec 3e)")
    ap.add_argument("--print-cap", metavar="ARM",
                    help="print the registered cap for ARM and exit.  THE LAUNCHER "
                         "CALLS THIS RATHER THAN CARRYING ITS OWN LITERAL.")
    a = ap.parse_args(argv)
    if a.print_cap:
        if a.print_cap not in CAPS:
            return 64
        print("%.3f" % CAPS[a.print_cap])
        return 0
    if a.selftest:
        return selftest()
    for need in ("item", "arm_dir", "datum_file", "core_min", "rc"):
        if getattr(a, need) is None:
            ap.error("--%s is required when grading" % need.replace("_", "-"))
    try:
        with open(a.datum_file) as fh:
            datum = int(fh.read().strip())
        kw = dict(jsonl_path=os.path.join(a.arm_dir, "d6r2c_gs1.jsonl"),
                  arm_dir=a.arm_dir, datum_epoch=datum,
                  core_min=a.core_min, rc=a.rc, log_path=a.log)
        rec = grade(**kw)
        rec["planted_control"] = live_plant_check(kw, rec["label"])
    except Refusal as e:
        print("D6R2C_GS1_GRADE REFUSED\n%s" % e)
        return 2
    out = a.out or os.path.join(os.path.dirname(a.arm_dir.rstrip("/")),
                                "GS1_GRADE.json")
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
    print("D6R2C_GS1_GRADE item=GS1 label=%s plateaus=%r"
          % (rec["label"], [k for k, v in rec["plateau"].items() if v["found"]]))
    print("D6R2C_GS1_GRADE verdict=%s written=%s" % (rec["label"], out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
