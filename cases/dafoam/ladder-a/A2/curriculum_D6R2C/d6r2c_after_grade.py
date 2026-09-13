#!/usr/bin/env python3
# ===========================================================================
# d6r2c_after_grade.py -- THE GRADING PATH FOR SANAA'S AFTER-ITEMS 8 AND 9
# ===========================================================================
#
# Registered by PREREGISTRATION_AFTER_ITEMS.md section 11, and IN THE SAME
# COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS (CLAUDE.md rule 2).
#
# WHY THAT SENTENCE IS THE FIRST ONE.  The parent item D6R2C registered its
# production gates against `d6r2c_grade.py` and that file DID NOT EXIST -- not
# in the working tree, not in any tree in this repository's history.  The
# instrument had to be written after its run had produced data, which is
# precisely the hazard rule 2 exists to prevent (PREREGISTRATION.md ADDENDUM 3,
# and lesson L-579).  This file exists before its first datum so that defect is
# not repeated in a new costume.
#
# NOTHING IN THIS FILE WAS CHOSEN BY ITS AUTHOR.  Every threshold, literal,
# comparison direction and label below is COPIED VERBATIM from
# PREREGISTRATION_AFTER_ITEMS.md, and each constant carries the sentence it was
# copied from as its comment.  Where that document is silent this file REFUSES
# (exit 2); it does not choose.
#
# REFUSE, NEVER DEGRADE.  A missing, unreadable or non-finite input is a refusal
# (exit 2) or a registered gate failure.  There is no default value anywhere in
# this file, no silent skip, and no `except: pass`.
#
# RULE 3, THE PLANTED CONTROL, IN TWO FORMS.
#   (a) LIVE, on every real grading: after the verdict is computed, the grader
#       re-grades deep copies of the SAME inputs with PLANT = 1.234e-03 injected
#       into the values it read back from disk, and REFUSES (exit 2) if any
#       plant leaves the verdict at PASS.  A reader that cannot see a
#       disagreement of that size cannot certify an agreement, and its zero is
#       not evidence.
#   (b) --selftest, on synthetic trees in a temporary directory, touching no run
#       directory: controls in BOTH directions, including a negative control
#       that must NOT flip.
#
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
# THE REGISTERED CONSTANTS.  Each carries the sentence it was copied from.
# ---------------------------------------------------------------------------

# "max_i |CL_i - target_i| <= TRIM_TOL = 1.0e-6 over cl04 / cl05 / cl06"  (sec 3, D1)
TRIM_TOL = 1.0e-6

# "|J_B - J0| / J0 <= REPRO_TOL = 1.0e-5"  and the same for J_opt vs Jf  (sec 3, D2)
REPRO_TOL = 1.0e-5

# "|(d_shape + d_twist + d_trim) - (J_opt - J_B)| <= CLOSE_TOL = 1.0e-12"  (sec 3, D3)
CLOSE_TOL = 1.0e-12

# "D4 PASSES iff |I| <= INTERACT_TOL x |J_F - J_B| with INTERACT_TOL = 0.10"  (sec 3, D4)
INTERACT_TOL = 0.10

# "a bijection ... within SHAPE_MATCH_TOL = 1.0e-8 (absolute, metres)"  (sec 2c / 4, H1)
SHAPE_MATCH_TOL = 1.0e-8

# "|J_fresh(s*, t*, a*) - Jf| <= FM_BAND_ABS = 3.064163144e-04"  (sec 2d / 4, H3)
# derived exactly as 0.01 x J0 = 0.01 x 0.0306416314389976151
FM_BAND_ABS = 3.064163144e-04

# "If J_fresh >= 0.90 x J0 = 2.757747e-02 ... the G2 conclusion is contradicted"  (sec 2f)
G2_BAR_ON_J0 = 0.90

# "|CL_fresh,i - CL_deformed,i| > 5.0e-3 for any i is named in the record as a
#  finding (5.0e-3 is five times the G3 tolerance ...)"  (sec 2e)
CL_FINDING_TRIGGER = 5.0e-3

# "findFeasibleDesign gets at most TRIM_MAX_EVALS = 40 primal evaluations per state"  (sec 3a)
TRIM_MAX_EVALS = 40

# "d6r2c_after_grade.py plants PLANT = 1.234e-03 into values it read back from disk"  (sec 7)
PLANT = 1.234e-03

# "J = 0.25 x CD04 + 0.50 x CD05 + 0.25 x CD06"  (PREREGISTRATION.md section 1, WEIGHTS)
WEIGHTS = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}
# "cl04 -> CL = 0.4, cl05 -> CL = 0.5, cl06 -> CL = 0.6"  (PREREGISTRATION.md section 1)
CL_TARGETS = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
POINTS = ["cl04", "cl05", "cl06"]

# Section 0b, the inherited state, each pinned to an artefact.
J0_INHERITED = 0.0306416314389976151   # d6r2c_evals.jsonl, F record n = 2
JF_INHERITED = 0.0230632595286777639   # d6r2c_evals.jsonl, F record n = 88
EVALS_MD5 = "2c0b8143caad198cd2e21d8047986aa3"
X0_MD5 = "b225fe7fdbd12eaa8a9b8a70835849c8"
BASE_POINTS_MD5 = "0fb1935a9b8781b73ac4ccb136e3ec68"   # base/constant/polyMesh/points.gz
GENWINGMESH_MD5 = "dab5e959187ab2e2bfb4e2c0ded0feb6"   # the family script's mesh step

# Section 8, the registered caps (3.00x), in core-minutes.
CAPS = {"DEC": 968.1, "FM": 618.0, "FM_L2": 180.0}

# The five registered decomposition states, IN THE REGISTERED ORDER.
# "the five decomposition states in one container, order B -> T -> S -> F -> O"  (sec 5)
STATES = ["B", "T", "S", "F", "O"]
# "J_opt is exempt by construction -- it is the un-trimmed control"  (sec 3, D1)
TRIMMED_STATES = ["B", "T", "S", "F"]

LABEL_PASS = "PASS"
LABEL_GATE_FAIL = "GATE FAIL"
LABEL_NOT_A_RESULT = "NOT A RESULT"


class Refusal(Exception):
    """Refuse, never degrade.  Raised for any condition the registration did not
    resolve, any missing input, and any failed planted control."""


def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _finite(x, what):
    if x is None or not isinstance(x, (int, float)) or not math.isfinite(float(x)):
        raise Refusal("REFUSE_NON_FINITE %s = %r -- a non-measurement is not a "
                      "number and is never graded as one" % (what, x))
    return float(x)


def _req(d, key, what):
    if not isinstance(d, dict) or key not in d:
        raise Refusal("REFUSE_MISSING_FIELD %s: %r" % (what, key))
    return d[key]


# ---------------------------------------------------------------------------
# THE INHERITED RECORD
# ---------------------------------------------------------------------------

def load_inherited(evals_path, require_md5=True):
    """Read J0, Jf and the two CL vectors from the md5-pinned O_mp record.

    The md5 assertion is the whole point: a number whose artefact has changed is
    not the number this registration froze."""
    if not os.path.isfile(evals_path):
        raise Refusal("REFUSE_MISSING_INHERITED %s" % evals_path)
    got = _md5(evals_path)
    if require_md5 and got != EVALS_MD5:
        raise Refusal("REFUSE_INHERITED_MD5 %s\n  got  %s\n  want %s\n"
                      "  the artefact this registration pinned is not the artefact on disk"
                      % (evals_path, got, EVALS_MD5))
    recs = []
    with open(evals_path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    F = [r for r in recs if r.get("kind") == "F"]
    if not F:
        raise Refusal("REFUSE_NO_F_RECORDS in %s" % evals_path)
    first, last = F[0], F[-1]
    for tag, rec in (("baseline n=%s" % first.get("n"), first),
                     ("final n=%s" % last.get("n"), last)):
        # A-2a style non-measurement guard, BEFORE any arithmetic on the record.
        # ADDENDUM 3 A3.4: NaN comparisons are all False, so a NaN record falls
        # straight through every band check and manufactures a verdict.
        if rec.get("fail", 1) != 0:
            raise Refusal("REFUSE_FAILED_RECORD inherited %s carries fail=%r" % (tag, rec.get("fail")))
        _finite(_req(rec, "funcs", tag)["obj.J"][0], "inherited %s obj.J" % tag)
        for p in POINTS:
            _finite(rec["funcs"]["%s.aero_post.functionals.CL" % p][0], "inherited %s %s CL" % (tag, p))
    out = {
        "evals_path": evals_path,
        "evals_md5": got,
        "baseline_n": first.get("n"),
        "final_n": last.get("n"),
        "J0": float(first["funcs"]["obj.J"][0]),
        "Jf": float(last["funcs"]["obj.J"][0]),
        "CL_baseline": {p: float(first["funcs"]["%s.aero_post.functionals.CL" % p][0]) for p in POINTS},
        "CL_final": {p: float(last["funcs"]["%s.aero_post.functionals.CL" % p][0]) for p in POINTS},
    }
    out["CL_miss_final"] = {p: abs(out["CL_final"][p] - CL_TARGETS[p]) for p in POINTS}
    out["CL_miss_baseline"] = {p: abs(out["CL_baseline"][p] - CL_TARGETS[p]) for p in POINTS}
    return out


# ---------------------------------------------------------------------------
# AGE DATUM AND OWNERSHIP -- the D6/H4 hygiene half
# ---------------------------------------------------------------------------

def scan_arm_dir(arm_dir, datum_epoch):
    """Every entry under arm_dir: is it newer than the datum, and who owns it?

    "zero files under the arm directory newer than the datum owned by uid 0 or
    gid 0"  (sec 3 D6 / sec 4 H4)"""
    if not os.path.isdir(arm_dir):
        raise Refusal("REFUSE_MISSING_ARM_DIR %s" % arm_dir)
    n_scanned = 0
    root_owned = []
    for dirpath, dirnames, filenames in os.walk(arm_dir):
        for name in list(dirnames) + list(filenames):
            p = os.path.join(dirpath, name)
            try:
                st = os.lstat(p)
            except OSError:
                continue
            n_scanned += 1
            if st.st_mtime > datum_epoch and (st.st_uid == 0 or st.st_gid == 0):
                root_owned.append([p, st.st_uid, st.st_gid])
    return {"n_scanned": n_scanned, "n_root_owned": len(root_owned),
            "root_owned_examples": root_owned[:10], "ok": len(root_owned) == 0}


def newer_than_datum(path, datum_epoch):
    if not os.path.exists(path):
        return {"present": False, "newer_than_datum": False, "path": path}
    st = os.lstat(path)
    return {"present": True, "mtime": st.st_mtime,
            "newer_than_datum": st.st_mtime > datum_epoch, "path": path}


# ---------------------------------------------------------------------------
# ITEM 8
# ---------------------------------------------------------------------------

def _weighted_J(cd):
    """Recomputed here from the per-condition CD and the FROZEN weights.  The
    producer's own J is read too and a disagreement is a refusal -- the grader
    does not take the producer's word for the graded quantity."""
    return sum(WEIGHTS[p] * cd[p] for p in POINTS)


def _read_states(jsonl_path):
    if not os.path.isfile(jsonl_path):
        raise Refusal("REFUSE_MISSING_DECOMP_RECORD %s" % jsonl_path)
    header, footer, states = None, None, {}
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
            elif k == "STATE":
                s = _req(r, "state", "STATE record")
                if s in states:
                    raise Refusal("REFUSE_DUPLICATE_STATE %r appears twice -- which "
                                  "one is the measurement is not this file's to choose" % s)
                states[s] = r
    if header is None:
        raise Refusal("REFUSE_NO_HEADER in %s" % jsonl_path)
    missing = [s for s in STATES if s not in states]
    if missing:
        raise Refusal("REFUSE_MISSING_STATES %r -- the registered order is %r"
                      % (missing, STATES))
    return header, states, footer


def grade_item8(jsonl_path, arm_dir, datum_epoch, inherited, core_min,
                rc, _plant=None):
    """Grade D1-D6 and build the absolute table.  Returns the record dict.

    `_plant` is used ONLY by the live planted control and by --selftest; it is
    never set on a real grading path."""
    header, states, footer = _read_states(jsonl_path)

    # ---- Build the absolute table FIRST.  Section 1c: no percentage field is
    # ---- written at all unless every cell is present and finite.
    table = {}
    for s in STATES:
        r = states[s]
        # A-2a non-measurement guard BEFORE any arithmetic (ADDENDUM 3 A3.4).
        if r.get("fail", 1) != 0:
            raise Refusal("REFUSE_FAILED_STATE %s carries fail=%r -- a failed "
                          "evaluation is not a measurement" % (s, r.get("fail")))
        cd = _req(r, "CD", "state %s" % s)
        cl = _req(r, "CL", "state %s" % s)
        aoa = _req(r, "AoA_deg", "state %s" % s)
        row = {"state": s,
               "CD": {p: _finite(cd.get(p), "state %s CD %s" % (s, p)) for p in POINTS},
               "CL": {p: _finite(cl.get(p), "state %s CL %s" % (s, p)) for p in POINTS},
               "AoA_deg": {p: _finite(aoa.get(p), "state %s AoA %s" % (s, p)) for p in POINTS},
               "n_trim_evals": r.get("n_trim_evals"),
               "primal_converged": _req(r, "primal_converged", "state %s" % s)}
        if _plant and _plant[0] == "CD" and _plant[1] == s:
            row["CD"][_plant[2]] = row["CD"][_plant[2]] + PLANT
        if _plant and _plant[0] == "CL" and _plant[1] == s:
            row["CL"][_plant[2]] = row["CL"][_plant[2]] + PLANT
        row["CD_counts"] = {p: row["CD"][p] * 1.0e4 for p in POINTS}
        row["CL_miss"] = {p: abs(row["CL"][p] - CL_TARGETS[p]) for p in POINTS}
        row["max_CL_miss"] = max(row["CL_miss"].values())
        row["J"] = _weighted_J(row["CD"])
        # The producer's own J, read and cross-checked, never trusted.
        row["J_producer"] = _finite(_req(r, "J", "state %s" % s), "state %s J" % s)
        row["J_recomputed_minus_producer"] = row["J"] - row["J_producer"]
        # The producer's own claimed miss, read and cross-checked, never trusted.
        claimed = r.get("claimed_cl_miss")
        row["claimed_cl_miss"] = claimed
        table[s] = row

    # A recomputed J that disagrees with the producer's means the weights, the
    # CDs or the record disagree about one quantity.  Not this file's to choose.
    for s in STATES:
        d = abs(table[s]["J_recomputed_minus_producer"])
        if d > 1.0e-12 and not (_plant and _plant[1] == s):
            raise Refusal("REFUSE_J_DISAGREEMENT state %s: recomputed %.17g vs "
                          "producer %.17g (|d| = %.3e > 1e-12)"
                          % (s, table[s]["J"], table[s]["J_producer"], d))
    for s in STATES:
        c = table[s]["claimed_cl_miss"]
        if isinstance(c, dict):
            for p in POINTS:
                if p in c and abs(float(c[p]) - table[s]["CL_miss"][p]) > 1.0e-12 \
                        and not (_plant and _plant[0] == "CL" and _plant[1] == s):
                    raise Refusal("REFUSE_CLMISS_DISAGREEMENT state %s %s: producer "
                                  "claimed %.17g, recomputed %.17g"
                                  % (s, p, float(c[p]), table[s]["CL_miss"][p]))

    JB, JT, JS, JF, JO = (table[s]["J"] for s in STATES)

    # ---- D1 -- every matched-lift arm is at matched lift
    d1_detail = {s: {"max_CL_miss": table[s]["max_CL_miss"],
                     "ok": table[s]["max_CL_miss"] <= TRIM_TOL,
                     "n_trim_evals": table[s]["n_trim_evals"]}
                 for s in TRIMMED_STATES}
    for s in TRIMMED_STATES:
        n = d1_detail[s]["n_trim_evals"]
        if isinstance(n, int) and n > TRIM_MAX_EVALS:
            d1_detail[s]["ok"] = False
            d1_detail[s]["why"] = ("TRIM_MAX_EVALS = %d exceeded (%d) -- section 3a: "
                                   "the state is NOT A RESULT and TRIM_TOL is never "
                                   "widened" % (TRIM_MAX_EVALS, n))
    D1 = all(v["ok"] for v in d1_detail.values())

    # ---- D2 -- the instrument reproduces the run it is decomposing, BOTH ENDS
    J0, Jf = inherited["J0"], inherited["Jf"]
    rel_B = abs(JB - J0) / abs(J0)
    rel_O = abs(JO - Jf) / abs(Jf)
    cl_O = {p: abs(table["O"]["CL"][p] - inherited["CL_final"][p]) for p in POINTS}
    d2_detail = {
        "J_B": JB, "J0": J0, "rel_B": rel_B, "rel_B_ok": rel_B <= REPRO_TOL,
        "J_opt": JO, "Jf": Jf, "rel_O": rel_O, "rel_O_ok": rel_O <= REPRO_TOL,
        "B_max_CL_miss": table["B"]["max_CL_miss"],
        "B_CL_ok": table["B"]["max_CL_miss"] <= TRIM_TOL,
        "O_CL_vs_inherited": cl_O,
        "O_CL_ok": max(cl_O.values()) <= TRIM_TOL,
        "REPRO_TOL": REPRO_TOL, "TRIM_TOL": TRIM_TOL,
    }
    D2 = (d2_detail["rel_B_ok"] and d2_detail["rel_O_ok"]
          and d2_detail["B_CL_ok"] and d2_detail["O_CL_ok"])

    # ---- the contributions
    d_twist_1 = JT - JB
    d_shape_1 = JF - JT
    d_shape_2 = JS - JB
    d_twist_2 = JF - JS
    I = d_shape_1 - d_shape_2
    d_shape = 0.5 * (d_shape_1 + d_shape_2)
    d_twist = 0.5 * (d_twist_1 + d_twist_2)
    d_trim = JO - JF
    geometric = JF - JB
    total = JO - JB

    # ---- D3 -- the accounting closes (an ARITHMETIC identity; floating-point band)
    closure = abs((d_shape + d_twist + d_trim) - total)
    D3 = closure <= CLOSE_TOL

    # ---- D4 -- order independence
    d4_rhs = INTERACT_TOL * abs(geometric)
    D4 = abs(I) <= d4_rhs

    # ---- D6 -- completion and hygiene
    own = scan_arm_dir(arm_dir, datum_epoch)
    conv = {}
    for s in STATES:
        pc = table[s]["primal_converged"]
        conv[s] = {p: bool(pc.get(p)) for p in POINTS}
    all_conv = all(all(v.values()) for v in conv.values())
    art = {name: newer_than_datum(os.path.join(arm_dir, name), datum_epoch)
           for name in ["d6r2c_decomp.jsonl"]}
    cap = CAPS["DEC"]
    cap_crossed = (core_min is not None) and (core_min > cap)   # strict >, as the parent's ledger uses
    d6_detail = {"rc": rc, "rc_is_zero": rc == 0,
                 "ownership": own, "artefacts": art,
                 "primal_converged": conv, "all_primals_converged": all_conv,
                 "footer_present": footer is not None,
                 "core_min": core_min, "cap_core_min": cap, "cap_crossed": cap_crossed}
    D6 = (rc == 0 and own["ok"] and all_conv
          and all(a["newer_than_datum"] for a in art.values()))

    # ---- the label
    if not (D1 and D2 and D3 and D6) or cap_crossed:
        label = LABEL_NOT_A_RESULT
    elif not D4:
        label = LABEL_GATE_FAIL
    else:
        label = LABEL_PASS

    rec = {
        "item": 8, "arm": "DEC", "label": label,
        "D1": D1, "D2": D2, "D3": D3, "D4": D4, "D6": D6,
        "D1_detail": d1_detail, "D2_detail": d2_detail,
        "D3_detail": {"closure_residual": closure, "CLOSE_TOL": CLOSE_TOL,
                      "note": "an ARITHMETIC identity; its band is a floating-point "
                              "band and it is NOT a physics test (registration sec 3, D3)"},
        "D4_detail": {"I": I, "INTERACT_TOL": INTERACT_TOL,
                      "threshold": d4_rhs, "geometric_gain": geometric,
                      "INTERACT_TOL_basis": "DECLARED, NOT MEASURED (registration sec 3, D4)"},
        "D6_detail": d6_detail,
        "table": table,
        "contributions_absolute": {
            "delta_twist_order1_twist_first": d_twist_1,
            "delta_shape_order1_twist_first": d_shape_1,
            "delta_shape_order2_shape_first": d_shape_2,
            "delta_twist_order2_shape_first": d_twist_2,
            "interaction_I": I,
            "delta_shape_symmetric": d_shape,
            "delta_twist_symmetric": d_twist,
            "delta_trim": d_trim,
            "geometric_gain_matched_lift_JF_minus_JB": geometric,
            "total_J_opt_minus_J_B": total,
        },
        "cost": {"core_min": core_min, "cap_core_min": cap, "cap_crossed": cap_crossed,
                 "cost_basis": "reported-by-owner; core-minutes = wall_s x ranks / 60; "
                               "dollars DERIVED, NOT MEASURED (CLAUDE.md rule 12)"},
        "inherited": {k: inherited[k] for k in
                      ("evals_path", "evals_md5", "baseline_n", "final_n", "J0", "Jf")},
        "planted_control": {"PLANT": PLANT, "form": "live, on every real grading"},
    }

    # ---- D5 -- "before any percentage is quoted".  MECHANICAL, NOT PROSE.
    table_complete = all(
        all(math.isfinite(table[s][k][p]) for p in POINTS)
        for s in STATES for k in ("CD", "CL", "AoA_deg"))
    if not table_complete:
        raise Refusal("REFUSE_NO_TABLE -- section 1c: no percentage field is written "
                      "at all unless every cell of the absolute table is present and "
                      "finite.  Sanaa: 'table shows shape vs twist vs trim "
                      "contributions before any percentage is quoted'.")
    if label == LABEL_NOT_A_RESULT:
        rec["percentages_absent_because"] = (
            "label is NOT A RESULT; section 1c forbids emitting a share whose table "
            "is not a measurement.  The absolute table above is reported as-measured.")
    else:
        # Every share names its denominator IN THE SAME RECORD (section 1b).
        rec["percentages"] = {
            "headline_reduction_unmatched_lift_pct": 100.0 * (J0 - Jf) / J0,
            "headline_reduction_denominator": "J0 (baseline, deformed mesh, from the O_mp record)",
            "headline_reduction_caveat":
                "THE OPTIMISER'S FINAL STATE IS NOT AT MATCHED LIFT.  This is NOT the "
                "number the shape/twist split applies to (registration sec 1b).",
            "matched_lift_reduction_pct": 100.0 * (JB - JF) / JB,
            "matched_lift_reduction_denominator": "J_B (baseline re-solved at matched lift, this arm)",
            "shape_share_of_matched_lift_gain_pct": 100.0 * d_shape / geometric if geometric != 0 else None,
            "twist_share_of_matched_lift_gain_pct": 100.0 * d_twist / geometric if geometric != 0 else None,
            "share_denominator": "J_F - J_B (the geometric gain at matched lift)",
            "trim_slack_share_of_headline_pct": 100.0 * d_trim / total if total != 0 else None,
            "trim_slack_denominator": "J_opt - J_B (the full unmatched-lift change)",
            "split_is_order_dependent": not D4,
            "split_quotable_as_a_split": bool(D4),
        }
        if not D4:
            rec["percentages"]["order_dependent_pairs"] = {
                "twist_first": {"twist_pct": 100.0 * d_twist_1 / geometric,
                                "shape_pct": 100.0 * d_shape_1 / geometric},
                "shape_first": {"shape_pct": 100.0 * d_shape_2 / geometric,
                                "twist_pct": 100.0 * d_twist_2 / geometric},
            }
    return rec


# ---------------------------------------------------------------------------
# ITEM 9
# ---------------------------------------------------------------------------

def grade_item9(json_path, arm_dir, datum_epoch, inherited, core_min, rc, _plant=None):
    if not os.path.isfile(json_path):
        raise Refusal("REFUSE_MISSING_FRESHMESH_RECORD %s" % json_path)
    with open(json_path) as fh:
        r = json.load(fh)

    # ---- H1 -- the fresh mesh is the final shape
    h1 = _req(r, "h1", "freshmesh record")
    n_cg = _req(h1, "n_cgns_nodes", "h1")
    n_fo = _req(h1, "n_foam_wall_points", "h1")
    worst = _finite(_req(h1, "worst_dist", "h1"), "h1 worst_dist")
    if _plant and _plant[0] == "H1":
        worst = worst + PLANT
    n_unmatched = _req(h1, "n_unmatched", "h1")
    bijective = bool(_req(h1, "bijective", "h1"))
    counts_ok = (n_cg == n_fo)
    H1 = counts_ok and bijective and n_unmatched == 0 and worst <= SHAPE_MATCH_TOL
    h1_detail = {"n_cgns_nodes": n_cg, "n_foam_wall_points": n_fo,
                 "counts_match": counts_ok, "bijective": bijective,
                 "n_unmatched": n_unmatched, "worst_dist": worst,
                 "SHAPE_MATCH_TOL": SHAPE_MATCH_TOL, "pass": H1}
    if not counts_ok:
        h1_detail["why"] = ("count mismatch -- registration sec 2c: NOT A RESULT with both "
                            "counts printed, NEVER a silent fallback to a Hausdorff distance")

    # ---- H2 -- the mesh is fresh, and from the family script
    mesh = _req(r, "mesh", "freshmesh record")
    gm = r.get("genwingmesh_md5")
    pts_md5 = _req(mesh, "points_md5", "mesh")
    h2_detail = {
        "genwingmesh_md5": gm, "genwingmesh_md5_expected": GENWINGMESH_MD5,
        "genwingmesh_md5_ok": gm == GENWINGMESH_MD5,
        "staged_surface_md5": r.get("staged_surface_md5"),
        "mesh_rc": r.get("mesh_rc"),
        "mesh_rc_is_zero": r.get("mesh_rc") == 0,
        "nCells": mesh.get("nCells"), "nPoints": mesh.get("nPoints"),
        "points_md5": pts_md5, "base_points_md5": BASE_POINTS_MD5,
        "differs_from_base_mesh": pts_md5 != BASE_POINTS_MD5,
        "polyMesh_newer_than_datum": newer_than_datum(
            os.path.join(arm_dir, "constant", "polyMesh", "points.gz"), datum_epoch),
        "checkmesh_report_path": r.get("checkmesh_report_path"),
        "checkmesh_note": "RECORDED, NOT GATED -- this registration fixes no mesh-quality "
                          "threshold and will not invent one after the fact (sec 4, H2)",
    }
    H2 = (h2_detail["genwingmesh_md5_ok"] and h2_detail["mesh_rc_is_zero"]
          and h2_detail["differs_from_base_mesh"]
          and h2_detail["polyMesh_newer_than_datum"]["newer_than_datum"])

    # ---- H3 -- the band.  Comparison (i): same DVs including a*, NO re-trim.
    solve = _req(r, "solve", "freshmesh record")
    cd = _req(solve, "CD", "solve")
    cl = _req(solve, "CL", "solve")
    CD = {p: _finite(cd.get(p), "fresh CD %s" % p) for p in POINTS}
    CL = {p: _finite(cl.get(p), "fresh CL %s" % p) for p in POINTS}
    if _plant and _plant[0] == "CD_fresh":
        CD[_plant[1]] = CD[_plant[1]] + PLANT
    J_fresh = _weighted_J(CD)
    J_prod = _finite(_req(solve, "J", "solve"), "fresh J")
    if abs(J_fresh - J_prod) > 1.0e-12 and not (_plant and _plant[0] == "CD_fresh"):
        raise Refusal("REFUSE_J_DISAGREEMENT fresh mesh: recomputed %.17g vs producer %.17g"
                      % (J_fresh, J_prod))
    Jf = inherited["Jf"]
    if _plant and _plant[0] == "Jf_inherited":
        Jf = Jf + PLANT
    diff = abs(J_fresh - Jf)
    H3 = diff <= FM_BAND_ABS
    g2_bar = G2_BAR_ON_J0 * inherited["J0"]
    g2_contradicted = J_fresh >= g2_bar
    h3_detail = {
        "J_fresh": J_fresh, "Jf_deformed_mesh": Jf, "abs_diff": diff,
        "FM_BAND_ABS": FM_BAND_ABS, "rel_diff": diff / abs(Jf),
        "FM_BAND_REL_reported_not_gated": FM_BAND_ABS / abs(Jf),
        "band_basis": "DECLARED decision-relevance band = 0.01 x J0, i.e. ONE PERCENTAGE "
                      "POINT of the headline reduction.  NOT a measured discretisation "
                      "uncertainty, NOT a GCI (registration sec 2d).",
        "comparison": "(i) same DVs including a*, NO re-trim -- the only thing that differs "
                      "is the mesh (registration sec 2e)",
        "pass": H3,
        "g2_bar_0p90_x_J0": g2_bar, "g2_contradicted_on_fresh_mesh": g2_contradicted,
    }
    # Reported, never gated.
    cl_delta = {p: abs(CL[p] - inherited["CL_final"][p]) for p in POINTS}
    reported = {
        "per_condition": {p: {"CD_fresh": CD[p], "CD_counts_fresh": CD[p] * 1.0e4,
                              "CL_fresh": CL[p],
                              "CL_deformed": inherited["CL_final"][p],
                              "CL_miss_fresh": abs(CL[p] - CL_TARGETS[p]),
                              "CL_miss_deformed": inherited["CL_miss_final"][p],
                              "abs_CL_delta": cl_delta[p]} for p in POINTS},
        "CL_finding_triggered": any(v > CL_FINDING_TRIGGER for v in cl_delta.values()),
        "CL_FINDING_TRIGGER": CL_FINDING_TRIGGER,
        "retrimmed": r.get("retrimmed"),
        "note": "REPORTED, NOT GATED (registration sec 2e / sec 4, H3)",
    }

    # ---- H4 -- completion and hygiene
    own = scan_arm_dir(arm_dir, datum_epoch)
    conv = {p: bool(_req(solve, "primal_converged", "solve").get(p)) for p in POINTS}
    cap = CAPS["FM"]
    cap_crossed = (core_min is not None) and (core_min > cap)
    h4_detail = {"rc": rc, "rc_is_zero": rc == 0, "ownership": own,
                 "primal_converged": conv, "all_primals_converged": all(conv.values()),
                 "uid": r.get("uid"), "ran_as_uid_1000": r.get("uid") == 1000,
                 "record_newer_than_datum": newer_than_datum(json_path, datum_epoch),
                 "core_min": core_min, "cap_core_min": cap, "cap_crossed": cap_crossed}
    H4 = (rc == 0 and own["ok"] and all(conv.values())
          and h4_detail["record_newer_than_datum"]["newer_than_datum"])

    if not (H1 and H2 and H4) or cap_crossed:
        label = LABEL_NOT_A_RESULT
    elif not H3:
        label = LABEL_GATE_FAIL
    else:
        label = LABEL_PASS

    rec = {"item": 9, "arm": "FM", "label": label,
           "H1": H1, "H2": H2, "H3": H3, "H4": H4,
           "H1_detail": h1_detail, "H2_detail": h2_detail,
           "H3_detail": h3_detail, "H4_detail": h4_detail,
           "reported_not_gated": reported,
           "cost": {"core_min": core_min, "cap_core_min": cap, "cap_crossed": cap_crossed,
                    "cost_basis": "reported-by-owner; core-minutes = wall_s x ranks / 60; "
                                  "dollars DERIVED, NOT MEASURED (CLAUDE.md rule 12)"},
           "inherited": {k: inherited[k] for k in
                         ("evals_path", "evals_md5", "final_n", "J0", "Jf")},
           "planted_control": {"PLANT": PLANT, "form": "live, on every real grading"},
           "g2_contradicted_on_fresh_mesh": g2_contradicted}

    if not H3:
        # Section 2f, decided in advance.
        rec["headline_quotation_constraint"] = "MUST_CITE_FRESH_MESH_DISCREPANCY"
        rec["headline_note"] = (
            "A fresh-mesh weighted drag outside the band is a GATE FAIL on item 9 and does "
            "NOT invalidate the 24.732 %.  It quantifies a disclosed discretisation channel. "
            "The 24.732 % may not be quoted anywhere without this discrepancy beside it "
            "(registration sec 2f).")
    if g2_contradicted:
        rec["escalation"] = (
            "G2 CONTRADICTED ON A FRESH MESH: J_fresh >= 0.90 x J0.  Escalated to "
            "dafoam-supervisor as a defect against the O_mp record.  Retiring or moving a "
            "gate threshold is reserved to Sanaa (CLAUDE.md, Reserved to Sanaa).")
    return rec


# ---------------------------------------------------------------------------
# THE LIVE PLANTED CONTROL (rule 3) -- runs on EVERY real grading
# ---------------------------------------------------------------------------

def live_plant_check(item, grade_fn_kwargs, verdict_label):
    """Re-grade deep copies of the same inputs with PLANT injected.  REFUSE if any
    plant leaves the verdict at PASS.

    Section 7: "A comparator that cannot see a disagreement of that size in these
    artefacts cannot certify an agreement, and its zero is not evidence." """
    if item == 8:
        plants = [("CD", "B", "cl05"), ("CD", "T", "cl05"), ("CD", "F", "cl05"),
                  ("CD", "O", "cl05"), ("CL", "F", "cl05")]
        fn = grade_item8
    else:
        plants = [("CD_fresh", "cl05"), ("Jf_inherited",), ("H1",)]
        fn = grade_item9
    results = []
    for pl in plants:
        kw = dict(grade_fn_kwargs)
        kw["inherited"] = copy.deepcopy(kw["inherited"])
        kw["_plant"] = pl
        try:
            out = fn(**kw)
            lab = out["label"]
        except Refusal as e:
            lab = "REFUSED: %s" % str(e).split("\n")[0]
        results.append({"plant": list(pl), "label_under_plant": lab})
        if lab == LABEL_PASS:
            raise Refusal(
                "REFUSE_PLANT_INVISIBLE plant %r left the verdict at PASS.  PLANT = %.6e "
                "is %.0fx the tightest band this grader applies; a reader that cannot see "
                "it cannot certify an agreement (rule 3)." % (pl, PLANT, PLANT / REPRO_TOL))
    return {"PLANT": PLANT, "verdict_without_plant": verdict_label, "controls": results,
            "all_plants_visible": True}


# ---------------------------------------------------------------------------
# THE MARKDOWN TABLE -- the absolute numbers, before any percentage
# ---------------------------------------------------------------------------

NAMES = {"B": "baseline (trimmed)", "T": "twist-only (re-trimmed)",
         "S": "shape-only (re-trimmed)", "F": "full optimum (re-trimmed)",
         "O": "optimiser final state (NOT matched lift)"}


def table_markdown(rec):
    t = rec["table"]
    L = ["# D6R2C after-item 8 -- THE ABSOLUTE TABLE",
         "",
         "Drag counts: 1 count = 1.0e-4 in CD.  **This table exists before any percentage is",
         "quoted** (Sanaa's item 8, enforced mechanically -- registration section 1c).",
         "",
         "| state | what it is | CD04 (cts) | CD05 (cts) | CD06 (cts) | J | max CL miss | AoA cl04/05/06 (deg) |",
         "|---|---|---|---|---|---|---|---|"]
    for s in STATES:
        r = t[s]
        L.append("| `%s` | %s | %.4f | %.4f | %.4f | %.10f | %.3e | %.6f / %.6f / %.6f |" % (
            s, NAMES[s], r["CD_counts"]["cl04"], r["CD_counts"]["cl05"], r["CD_counts"]["cl06"],
            r["J"], r["max_CL_miss"],
            r["AoA_deg"]["cl04"], r["AoA_deg"]["cl05"], r["AoA_deg"]["cl06"]))
    c = rec["contributions_absolute"]
    L += ["", "## Contributions, ABSOLUTE, in J", "",
          "| term | value | in drag counts |", "|---|---|---|"]
    for k in ("delta_twist_symmetric", "delta_shape_symmetric", "delta_trim",
              "geometric_gain_matched_lift_JF_minus_JB", "total_J_opt_minus_J_B",
              "interaction_I"):
        L.append("| `%s` | %.10e | %.4f |" % (k, c[k], c[k] * 1.0e4))
    L += ["", "**Label: `%s`**" % rec["label"], ""]
    if "percentages" not in rec:
        L.append("**No percentage is quoted: %s**" % rec.get("percentages_absent_because", ""))
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# SELFTEST
# ---------------------------------------------------------------------------

def _synth_inherited():
    return {"evals_path": "<synthetic>", "evals_md5": EVALS_MD5,
            "baseline_n": 2, "final_n": 88,
            "J0": J0_INHERITED, "Jf": JF_INHERITED,
            "CL_baseline": {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6},
            "CL_final": {"cl04": 0.399446101576034, "cl05": 0.498790141539629,
                         "cl06": 0.5972130043172164},
            "CL_miss_baseline": {p: 0.0 for p in POINTS},
            "CL_miss_final": {"cl04": 5.539e-4, "cl05": 1.2099e-3, "cl06": 2.787e-3}}


def _cd_for(J):
    """A CD triple whose FROZEN weighted mean is exactly J (flat triple)."""
    return {p: J for p in POINTS}


def _synth_decomp(tmp, JB, JT, JS, JF, JO, cl_miss=0.0, fail=0,
                  n_trim=6, converged=True, o_cl=None):
    d = os.path.join(tmp, "DEC")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "d6r2c_decomp.jsonl")
    inh = _synth_inherited()
    rows = [{"kind": "HEADER", "ranks": 4, "points": POINTS,
             "cl_targets": CL_TARGETS, "weights": WEIGHTS, "evals_md5": EVALS_MD5}]
    for s, J in zip(STATES, (JB, JT, JS, JF, JO)):
        cd = _cd_for(J)
        if s == "O":
            cl = dict(o_cl) if o_cl else dict(inh["CL_final"])
        else:
            cl = {p: CL_TARGETS[p] + cl_miss for p in POINTS}
        rows.append({"kind": "STATE", "state": s, "fail": fail,
                     "trimmed": s != "O", "n_trim_evals": (None if s == "O" else n_trim),
                     "CD": cd, "CL": cl,
                     "AoA_deg": {"cl04": 1.0, "cl05": 2.0, "cl06": 3.0},
                     "J": _weighted_J(cd),
                     "claimed_cl_miss": {p: abs(cl[p] - CL_TARGETS[p]) for p in POINTS},
                     "primal_converged": {p: converged for p in POINTS},
                     "primal_final_res": {p: 1e-9 for p in POINTS}})
    rows.append({"kind": "FOOTER", "rc": 0})
    with open(path, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    os.utime(path, (2_000_000_000, 2_000_000_000))
    return path, d


def _synth_fresh(tmp, J_fresh, worst=1e-12, n_cg=1031, n_fo=1031, bij=True,
                 unmatched=0, mesh_rc=0, gm=GENWINGMESH_MD5,
                 pts_md5="deadbeef", converged=True, uid=1000, cl=None):
    d = os.path.join(tmp, "FM")
    os.makedirs(os.path.join(d, "constant", "polyMesh"), exist_ok=True)
    pg = os.path.join(d, "constant", "polyMesh", "points.gz")
    with open(pg, "wb") as fh:
        fh.write(b"x")
    os.utime(pg, (2_000_000_000, 2_000_000_000))
    inh = _synth_inherited()
    cd = _cd_for(J_fresh)
    rec = {"kind": "FRESHMESH", "uid": uid, "mesh_rc": mesh_rc,
           "genwingmesh_md5": gm, "staged_surface_md5": "cafe",
           "mesh": {"nCells": 38304, "nPoints": 40209, "points_md5": pts_md5},
           "h1": {"n_cgns_nodes": n_cg, "n_foam_wall_points": n_fo,
                  "bijective": bij, "worst_dist": worst, "n_unmatched": unmatched},
           "solve": {"CD": cd, "CL": (cl or dict(inh["CL_final"])),
                     "AoA_deg": {"cl04": 0.577, "cl05": 1.772, "cl06": 3.038},
                     "J": _weighted_J(cd),
                     "primal_converged": {p: converged for p in POINTS},
                     "primal_final_res": {p: 1e-9 for p in POINTS}},
           "checkmesh_report_path": "checkMesh.log"}
    path = os.path.join(d, "d6r2c_freshmesh.json")
    with open(path, "w") as fh:
        json.dump(rec, fh)
    os.utime(path, (2_000_000_000, 2_000_000_000))
    return path, d


def selftest():
    DATUM = 1_000_000_000
    inh = _synth_inherited()
    J0, Jf = inh["J0"], inh["Jf"]
    controls = []

    def check(name, got, want):
        controls.append((name, got, want))
        if got != want:
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r" % (name, got, want))
            return False
        return True

    ok = True
    tmp = tempfile.mkdtemp(prefix="d6r2c_after_selftest_")
    try:
        # --- a clean, internally consistent decomposition ---------------------
        # JB == J0 exactly, JO == Jf exactly, additive (I == 0).
        JB, JO = J0, Jf
        JT = JB - 0.002
        JS = JB - 0.004
        JF = JB - 0.006          # additive: JF - JT = JS - JB = -0.004 -> I = 0
        p, d = _synth_decomp(tmp, JB, JT, JS, JF, JO)
        kw = dict(jsonl_path=p, arm_dir=d, datum_epoch=DATUM, inherited=inh,
                  core_min=300.0, rc=0)
        r = grade_item8(**kw)
        ok &= check("8: clean additive case -> PASS", r["label"], LABEL_PASS)
        ok &= check("8: clean case D3 closure <= CLOSE_TOL", r["D3"], True)
        ok &= check("8: clean case I == 0", abs(r["contributions_absolute"]["interaction_I"]) < 1e-15, True)
        ok &= check("8: percentages present on PASS", "percentages" in r, True)
        ok &= check("8: share denominator named", "share_denominator" in r["percentages"], True)
        # the LIVE planted control must itself pass on the clean case
        lp = live_plant_check(8, kw, r["label"])
        ok &= check("8: all 5 live plants visible", lp["all_plants_visible"], True)

        # --- NEGATIVE CONTROL: an untouched re-grade reproduces the label ------
        r2 = grade_item8(**kw)
        ok &= check("8: NEGATIVE control, re-grade reproduces label", r2["label"], r["label"])

        # --- D1: an arm off matched lift --------------------------------------
        p, d = _synth_decomp(tmp + "/a", JB, JT, JS, JF, JO, cl_miss=1.0e-5)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("8: D1 miss 1e-5 > TRIM_TOL -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        ok &= check("8: D1 false", r["D1"], False)
        ok &= check("8: no percentages when NOT A RESULT", "percentages" in r, False)
        # BOUNDARY, BOTH SIDES, ONE ULP APART.
        #
        # THE TRIM_TOL EDGE IS NOT REPRESENTABLE, and this control had to be
        # written around that rather than the gate written around this.  For the
        # registered targets there is no IEEE double `v` with
        # |v - target| == 1.0e-6 exactly: the attainable misses step by ~1.1e-16
        # and straddle the literal without landing on it, DIFFERENTLY PER TARGET
        # (target + 1e-6 gives a miss of 9.999999999732e-07 at target 0.4 -- INSIDE
        # the band -- but 1.000000000029e-06 at 0.5 and 0.6 -- OUTSIDE it).  The
        # boundary is therefore driven from the ATTAINABLE values on both sides,
        # one ulp apart.  NO TOLERANCE WAS ADDED TO D1 TO MAKE THE EDGE REACHABLE.
        # (The same property was recorded for G3's 1.0e-3 edge in
        # PREREGISTRATION.md ADDENDUM 3 A3.2 item 1.)
        def _straddle(target, tol):
            v = target + tol
            while abs(v - target) > tol:
                v = math.nextafter(v, target)
            below = v                     # largest attainable miss <= tol
            above = math.nextafter(v, 1.0)   # one ulp up: first miss > tol
            assert abs(below - target) <= tol < abs(above - target)
            return abs(below - target), abs(above - target)
        # drive it on the TIGHTEST target (0.6 -- coarsest ulp), the worst case
        lo, hi = _straddle(CL_TARGETS["cl06"], TRIM_TOL)
        p, d = _synth_decomp(tmp + "/b", JB, JT, JS, JF, JO, cl_miss=lo)
        ok &= check("8: D1 boundary, largest ATTAINABLE miss <= TRIM_TOL -> D1 holds",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["D1"], True)
        p, d = _synth_decomp(tmp + "/c", JB, JT, JS, JF, JO, cl_miss=hi)
        ok &= check("8: D1 boundary, ONE ULP ABOVE that -> D1 fails",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["D1"], False)

        # --- D2: the reproduction control at each end -------------------------
        p, d = _synth_decomp(tmp + "/d", JB * (1 + 2e-5), JT, JS, JF, JO)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("8: D2 far end J_B off by 2e-5 -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        ok &= check("8: D2 false (J_B)", r["D2"], False)
        p, d = _synth_decomp(tmp + "/e", JB, JT, JS, JF, JO * (1 + 2e-5))
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("8: D2 far end J_opt off by 2e-5 -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_decomp(tmp + "/f", JB, JT, JS, JF, JO,
                             o_cl={p2: inh["CL_final"][p2] + 1e-5 for p2 in POINTS})
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("8: D2 J_opt CL drift 1e-5 -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)

        # --- D3: one part in 1e14 inside the identity band --------------------
        # perturb JF only in the PRODUCER's J, which breaks the cross-check first
        # The cross-check threshold is 1.0e-12 ABSOLUTE on J.  A RELATIVE
        # perturbation of 1e-14 on J ~ 0.025 is ~2.5e-16 absolute and is BELOW
        # that threshold -- the first draft of this control used one and the
        # control correctly did not fire.  Recorded rather than quietly fixed:
        # a control that fires for the wrong reason is worse than none.  Both
        # sides of the absolute threshold are driven.
        def _perturb_producer_J(tag, delta):
            pp, dd = _synth_decomp(tmp + tag, JB, JT, JS, JF, JO)
            rws = [json.loads(x) for x in open(pp).read().splitlines()]
            for row in rws:
                if row.get("state") == "F":
                    row["J"] = row["J"] + delta
            with open(pp, "w") as fh:
                for row in rws:
                    fh.write(json.dumps(row) + "\n")
            os.utime(pp, (2_000_000_000, 2_000_000_000))
            return pp, dd
        p, d = _perturb_producer_J("/g", 1.0e-11)
        try:
            grade_item8(p, d, DATUM, inh, 300.0, 0)
            ok &= check("8: producer J off by 1e-11 (> 1e-12) -> refusal",
                        "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("8: producer J off by 1e-11 -> REFUSE_J_DISAGREEMENT",
                        str(e).startswith("REFUSE_J_DISAGREEMENT"), True)
        p, d = _perturb_producer_J("/g2", 1.0e-13)
        try:
            lab = grade_item8(p, d, DATUM, inh, 300.0, 0)["label"]
            ok &= check("8: NEGATIVE -- producer J off by 1e-13 (< 1e-12) does NOT refuse",
                        lab, LABEL_PASS)
        except Refusal as e:
            ok &= check("8: producer J off by 1e-13 must NOT refuse", str(e), "no refusal")

        # --- D4: interaction above and below the threshold --------------------
        # geometric gain = JF - JB = -0.006; threshold = 0.10 * 0.006 = 6.0e-4
        JT2 = JB - 0.002
        JS2 = JB - 0.004 + 5.0e-4     # I = (JF-JT2) - (JS2-JB) = -0.004 - (-0.0035) = -5.0e-4
        p, d = _synth_decomp(tmp + "/h", JB, JT2, JS2, JF, JO)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("8: |I| = 5.0e-4 < 6.0e-4 -> D4 holds, PASS", r["label"], LABEL_PASS)
        JS3 = JB - 0.004 + 8.0e-4     # I = -8.0e-4, above 6.0e-4
        p, d = _synth_decomp(tmp + "/i", JB, JT2, JS3, JF, JO)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("8: |I| = 8.0e-4 > 6.0e-4 -> GATE FAIL", r["label"], LABEL_GATE_FAIL)
        ok &= check("8: GATE FAIL still emits percentages, qualified",
                    r["percentages"]["split_is_order_dependent"], True)
        ok &= check("8: GATE FAIL emits BOTH orderings",
                    "order_dependent_pairs" in r["percentages"], True)

        # --- D6: rc, convergence, cap ----------------------------------------
        p, d = _synth_decomp(tmp + "/j", JB, JT, JS, JF, JO)
        ok &= check("8: rc=137 -> NOT A RESULT",
                    grade_item8(p, d, DATUM, inh, 300.0, 137)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_decomp(tmp + "/k", JB, JT, JS, JF, JO, converged=False)
        ok &= check("8: a primal not converged -> NOT A RESULT",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_decomp(tmp + "/l", JB, JT, JS, JF, JO)
        ok &= check("8: cap crossed (968.2 > 968.1) -> NOT A RESULT",
                    grade_item8(p, d, DATUM, inh, 968.2, 0)["label"], LABEL_NOT_A_RESULT)
        ok &= check("8: cap AT the cap (968.1) is NOT crossed (strict >)",
                    grade_item8(p, d, DATUM, inh, 968.1, 0)["label"], LABEL_PASS)
        p, d = _synth_decomp(tmp + "/m", JB, JT, JS, JF, JO, n_trim=TRIM_MAX_EVALS + 1)
        ok &= check("8: TRIM_MAX_EVALS exceeded -> NOT A RESULT",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_NOT_A_RESULT)

        # --- the non-measurement guard (ADDENDUM 3 A3.4) ----------------------
        p, d = _synth_decomp(tmp + "/n", JB, JT, JS, JF, JO, fail=1)
        try:
            grade_item8(p, d, DATUM, inh, 300.0, 0)
            ok &= check("8: fail=1 -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("8: fail=1 -> REFUSE_FAILED_STATE",
                        str(e).startswith("REFUSE_FAILED_STATE"), True)
        # fail=0 but NaN -- isolates the NaN path from the fail flag
        p, d = _synth_decomp(tmp + "/o", JB, JT, JS, JF, JO)
        rows = [json.loads(x) for x in open(p).read().splitlines()]
        for row in rows:
            if row.get("state") == "F":
                row["CD"]["cl05"] = float("nan")
        with open(p, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
        os.utime(p, (2_000_000_000, 2_000_000_000))
        try:
            grade_item8(p, d, DATUM, inh, 300.0, 0)
            ok &= check("8: fail=0 with NaN CD -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("8: fail=0 with NaN CD -> REFUSE_NON_FINITE",
                        str(e).startswith("REFUSE_NON_FINITE"), True)
        # a missing state
        p, d = _synth_decomp(tmp + "/p", JB, JT, JS, JF, JO)
        rows = [json.loads(x) for x in open(p).read().splitlines()]
        rows = [r2 for r2 in rows if r2.get("state") != "S"]
        with open(p, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
        try:
            grade_item8(p, d, DATUM, inh, 300.0, 0)
            ok &= check("8: missing state S -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("8: missing state S -> REFUSE_MISSING_STATES",
                        str(e).startswith("REFUSE_MISSING_STATES"), True)

        # ================= ITEM 9 =============================================
        # clean: inside the band
        p, d = _synth_fresh(tmp, Jf + 0.5 * FM_BAND_ABS)
        kw9 = dict(json_path=p, arm_dir=d, datum_epoch=DATUM, inherited=inh,
                   core_min=200.0, rc=0)
        r = grade_item9(**kw9)
        ok &= check("9: inside band -> PASS", r["label"], LABEL_PASS)
        lp = live_plant_check(9, kw9, r["label"])
        ok &= check("9: all 3 live plants visible", lp["all_plants_visible"], True)
        ok &= check("9: NEGATIVE control, re-grade reproduces",
                    grade_item9(**kw9)["label"], LABEL_PASS)
        # band boundary, both sides one ulp apart
        p, d = _synth_fresh(tmp + "/b1", Jf + FM_BAND_ABS)
        ok &= check("9: AT the band -> H3 holds",
                    grade_item9(p, d, DATUM, inh, 200.0, 0)["H3"], True)
        p, d = _synth_fresh(tmp + "/b2", math.nextafter(Jf + FM_BAND_ABS, 1.0))
        ok &= check("9: ONE ULP outside the band -> GATE FAIL",
                    grade_item9(p, d, DATUM, inh, 200.0, 0)["label"], LABEL_GATE_FAIL)
        # H1 failures
        p, d = _synth_fresh(tmp + "/c1", Jf, worst=1e-7)
        ok &= check("9: H1 worst_dist 1e-7 > 1e-8 -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 200.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/c2", Jf, n_fo=1030)
        r = grade_item9(p, d, DATUM, inh, 200.0, 0)
        ok &= check("9: H1 count mismatch -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        ok &= check("9: H1 count mismatch prints both counts",
                    (r["H1_detail"]["n_cgns_nodes"], r["H1_detail"]["n_foam_wall_points"]),
                    (1031, 1030))
        p, d = _synth_fresh(tmp + "/c3", Jf, bij=False)
        ok &= check("9: H1 non-bijective -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 200.0, 0)["label"], LABEL_NOT_A_RESULT)
        # H2 failures
        p, d = _synth_fresh(tmp + "/d1", Jf, pts_md5=BASE_POINTS_MD5)
        r = grade_item9(p, d, DATUM, inh, 200.0, 0)
        ok &= check("9: H2 fresh mesh IDENTICAL to base -> NOT A RESULT",
                    r["label"], LABEL_NOT_A_RESULT)
        ok &= check("9: H2 differs_from_base_mesh False",
                    r["H2_detail"]["differs_from_base_mesh"], False)
        p, d = _synth_fresh(tmp + "/d2", Jf, gm="0" * 32)
        ok &= check("9: H2 genWingMesh md5 wrong -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 200.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/d3", Jf, mesh_rc=1)
        ok &= check("9: H2 mesh rc != 0 -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 200.0, 0)["label"], LABEL_NOT_A_RESULT)
        # H4
        p, d = _synth_fresh(tmp + "/e1", Jf, converged=False)
        ok &= check("9: H4 primal not converged -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 200.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/e2", Jf)
        ok &= check("9: H4 cap crossed -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 618.1, 0)["label"], LABEL_NOT_A_RESULT)
        # the G2-contradiction escalation, and that it is NOT confused with the band
        p, d = _synth_fresh(tmp + "/f1", G2_BAR_ON_J0 * J0 + 1e-6)
        r = grade_item9(p, d, DATUM, inh, 200.0, 0)
        ok &= check("9: J_fresh >= 0.90 x J0 -> g2_contradicted true",
                    r["g2_contradicted_on_fresh_mesh"], True)
        ok &= check("9: g2 contradiction carries the escalation", "escalation" in r, True)
        ok &= check("9: g2 contradiction is a GATE FAIL, not NOT A RESULT",
                    r["label"], LABEL_GATE_FAIL)
        ok &= check("9: GATE FAIL binds the headline quotation",
                    r.get("headline_quotation_constraint"), "MUST_CITE_FRESH_MESH_DISCREPANCY")
        # the reported-not-gated CL finding trigger
        p, d = _synth_fresh(tmp + "/g1", Jf,
                            cl={p2: inh["CL_final"][p2] + 6.0e-3 for p2 in POINTS})
        r = grade_item9(p, d, DATUM, inh, 200.0, 0)
        ok &= check("9: CL delta 6e-3 > 5e-3 triggers the FINDING",
                    r["reported_not_gated"]["CL_finding_triggered"], True)
        ok &= check("9: the CL finding does NOT change the label", r["label"], LABEL_PASS)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("D6R2C_AFTER_GRADE SELFTEST %s n=%d"
          % ("PASS" if ok else "FAIL", len(controls)))
    return 0 if ok else 1


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Grade D6R2C after-items 8 (decomposition) and 9 (fresh mesh).")
    ap.add_argument("--selftest", action="store_true",
                    help="drive the planted controls on synthetic trees; touches no run dir")
    ap.add_argument("--item", type=int, choices=(8, 9))
    ap.add_argument("--arm-dir")
    ap.add_argument("--evals", default="/home/ubuntu/certonomous-runs/"
                    "CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp/d6r2c_evals.jsonl")
    ap.add_argument("--datum-file", help="the arm's .d6r2c_age_datum")
    ap.add_argument("--core-min", type=float)
    ap.add_argument("--rc", type=int)
    ap.add_argument("--out", help="where to write the verdict JSON")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()
    for need in ("item", "arm_dir", "datum_file", "core_min", "rc"):
        if getattr(a, need) is None:
            ap.error("--%s is required when grading" % need.replace("_", "-"))
    try:
        with open(a.datum_file) as fh:
            datum = int(fh.read().strip())
        inherited = load_inherited(a.evals)
        if a.item == 8:
            kw = dict(jsonl_path=os.path.join(a.arm_dir, "d6r2c_decomp.jsonl"),
                      arm_dir=a.arm_dir, datum_epoch=datum, inherited=inherited,
                      core_min=a.core_min, rc=a.rc)
            rec = grade_item8(**kw)
        else:
            kw = dict(json_path=os.path.join(a.arm_dir, "d6r2c_freshmesh.json"),
                      arm_dir=a.arm_dir, datum_epoch=datum, inherited=inherited,
                      core_min=a.core_min, rc=a.rc)
            rec = grade_item9(**kw)
        rec["planted_control"] = live_plant_check(a.item, kw, rec["label"])
    except Refusal as e:
        print("D6R2C_AFTER_GRADE REFUSED\n%s" % e)
        return 2
    out = a.out or os.path.join(os.path.dirname(a.arm_dir.rstrip("/")),
                                "AFTER_ITEM%d_GRADE.json" % a.item)
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
    if a.item == 8:
        md = os.path.join(os.path.dirname(out), "DECOMP_TABLE.md")
        with open(md, "w") as fh:
            fh.write(table_markdown(rec))
        print("D6R2C_AFTER_GRADE item=8 label=%s table=%s" % (rec["label"], md))
    else:
        print("D6R2C_AFTER_GRADE item=9 label=%s J_fresh=%.12g Jf=%.12g |d|=%.6e band=%.6e"
              % (rec["label"], rec["H3_detail"]["J_fresh"], rec["H3_detail"]["Jf_deformed_mesh"],
                 rec["H3_detail"]["abs_diff"], FM_BAND_ABS))
    print("D6R2C_AFTER_GRADE verdict=%s written=%s" % (rec["label"], out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
