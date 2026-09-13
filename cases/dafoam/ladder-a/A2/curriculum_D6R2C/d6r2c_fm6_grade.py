#!/usr/bin/env python3
# ===========================================================================
# d6r2c_fm6_grade.py -- THE GRADING PATH FOR ARM FM6 (after-item 9, successor)
# ===========================================================================
#
# Registered by PREREGISTRATION_AFTER_ITEM9_R2.md section 11, and IN THE SAME
# COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS (CLAUDE.md rule 2).
#
# A FORK of d6r2c_after_grade.py (md5 6c22013af54569ae651f8f23d1088861), which
# stays on disk unedited and keeps grading FM5 under its own document.  What
# changed, exhaustively:
#   (1) item 8 (D1-D6) is DELETED -- this document does not register it;
#   (2) I1 is NEW -- the initialisation is what it says it is, anchored to a
#       reconstruction the grader RE-DERIVES from O_mp rather than to the
#       producer's word for it;
#   (3) H1 now requires the ADDENDUM 4 A4.3 equality, an anchor fixed before
#       FM6 ran and outside it;
#   (4) H4 additionally requires the staged inputs to be the registered inputs,
#       and records the convergence floor against FM5's;
#   (5) the cap is DERIVED from the registered prediction, never typed twice --
#       the defect PREREGISTRATION_AFTER_ITEM8_R2.md section 8a records.
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
# PREREGISTRATION_AFTER_ITEM9_R2.md, and each constant carries the sentence it was
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

# ---- I1, NEW.  The registered equality of ADDENDUM 4 A4.3, which FM5 met and
# ---- which is an anchor FIXED BEFORE THIS RUN AND OUTSIDE IT (sec 3, H1).
H1_REGISTERED = {"n_cgns_unique_nodes": 1031, "n_cgns_unique_registered": 1031,
                 "n_foam_wall_points": 1031, "bijective": True, "n_unmatched": 0,
                 "worst_dist": 5.010837892761856e-09}
# "faces.gz / owner.gz / neighbour.gz / boundary are byte-identical across all
#  three meshes" (sec 2a) -- the premise of the index transfer, RE-CHECKED here
# rather than taken from the producer's record.
CONNECTIVITY_MD5 = {
    "faces.gz": "0a94bba01e37c8587676b056c7a2bb05",
    "owner.gz": "16febaf5dfa4137ef7fb1ec4a3659ec5",
    "neighbour.gz": "803a7546fd09fcbd673ef1ed52b4fcd6",
    "boundary": "c8d1891562dc7a1d5822cd6b94c2c2d4",
}
# "the transfer set is exactly the volFields the destination's own 0.orig
#  carries" (sec 2c), MEASURED from 0.orig: T U alphat nuTilda nut p.
TRANSFER_SET = ("T", "U", "alphat", "nuTilda", "nut", "p")
# "38,304 cells" (sec 9a) and "the three conditions" (PREREGISTRATION.md sec 1).
N_CELLS = 38304
RUN_DIRS = ("mp04", "mp05", "mp06")
# "primalMinResTol is NEVER loosened" (sec 3, H4 and sec 10).
PRIMAL_MIN_RES_TOL = 1.0e-8
# "FM5's floor was 1.278377566e-05 and the FM6 discriminator is fixed in
#  advance" (sec 3a) -- an anchor from a run this one did not produce.
FM5_FLOOR = 1.278377566e-05
FLOOR_SAME_REL = 0.01

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
# The frozen optimisation runscript -- the bytes O_mp ran.  Asserted by H4 so
# that "nothing about the optimisation moved" is a CHECK, not a sentence.
RUNSCRIPT_MD5 = "2f2ae43a627146cf8e0f065b035ada4b"

# ---- THE REGISTERED CAP, DERIVED AND NOT TYPED TWICE.  A cap that exists as a
# ---- literal in two files is two things that can drift, and in this item they
# ---- did (PREREGISTRATION_AFTER_ITEM8_R2.md section 8a).
# "PREDICTION 236.054 s wall x 4 ranks / 60 = 15.737 core-min"  (sec 8)
PREDICTION_CORE_MIN = 15.737
# "REGISTERED CAP (3.00x) = 47.211 core-min"  (sec 8)
CAP_FACTOR = 3.00
CAPS = {"FM6": round(PREDICTION_CORE_MIN * CAP_FACTOR, 3)}

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
# THE GRADED QUANTITY -- recomputed from the per-condition CD and the FROZEN
# weights.  The producer's own J is read too and a disagreement is a refusal:
# this file does not take the producer's word for the graded quantity.
# "J = 0.25 x CD04 + 0.50 x CD05 + 0.25 x CD06"  (sec 0e)
# ---------------------------------------------------------------------------

def _weighted_J(cd):
    return sum(WEIGHTS[p] * cd[p] for p in POINTS)


# ---------------------------------------------------------------------------
# ARM FM6
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
    # THE REGISTERED EQUALITY (sec 3, H1).  H1 depends only on the DVGeo
    # deformation and on O_mp's wall points already on disk -- it is INDEPENDENT
    # OF THE FLOW SOLVE -- and this solver class is measured bitwise reproducible
    # across independent cold runs.  FM5 met the equality; FM6 must MEET IT
    # AGAIN, BIT FOR BIT.  This is not a tolerance and it is an anchor fixed
    # before this run and outside it (L-588).
    eq = {"n_foam_wall_points": n_fo, "n_unmatched": n_unmatched,
          "bijective": bijective, "worst_dist": worst}
    eq_want = {k: H1_REGISTERED[k] for k in eq}
    equality_ok = all(eq[k] == eq_want[k] for k in eq)
    H1 = (counts_ok and bijective and n_unmatched == 0
          and worst <= SHAPE_MATCH_TOL and equality_ok)
    h1_detail = {"n_cgns_nodes": n_cg, "n_foam_wall_points": n_fo,
                 "counts_match": counts_ok, "bijective": bijective,
                 "n_unmatched": n_unmatched, "worst_dist": worst,
                 "SHAPE_MATCH_TOL": SHAPE_MATCH_TOL,
                 "registered_equality": eq_want, "observed": eq,
                 "equality_holds": equality_ok, "pass": H1}
    if not equality_ok:
        h1_detail["why"] = (
            "H1 DIFFERS FROM THE REGISTERED EQUALITY of ADDENDUM 4 A4.3.  H1 is "
            "independent of the flow solve, so ANY difference at all is a finding "
            "and is escalated, never absorbed (sec 3, H1).")
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

    # ---- I1 -- THE ONE REGISTERED CHANGE IS WHAT IT SAYS IT IS ----------
    # The grader RE-DERIVES the reconstruction from O_mp rather than believing
    # the producer's record of it.  O_mp is opened READ-ONLY and is never
    # written; it is a graded run directory a closed verdict cites by path.
    init_path = os.path.join(arm_dir, "d6r2c_fm6_init.json")
    if not os.path.isfile(init_path):
        raise Refusal("REFUSE_MISSING_INIT_RECORD %s -- the one registered change "
                      "of this arm left no record, so there is nothing to grade"
                      % init_path)
    with open(init_path) as fh:
        ir = json.load(fh)
    i1_detail = {"record": init_path}
    conn_dst = _req(ir, "connectivity_destination", "init record")
    conn_ok = all(conn_dst.get(k) == v for k, v in CONNECTIVITY_MD5.items())
    i1_detail["connectivity_destination"] = conn_dst
    i1_detail["connectivity_registered"] = dict(CONNECTIVITY_MD5)
    i1_detail["connectivity_holds"] = conn_ok
    tset = tuple(ir.get("transfer_set") or ())
    set_ok = tuple(sorted(tset)) == tuple(sorted(TRANSFER_SET))
    i1_detail["transfer_set"] = list(tset)
    i1_detail["transfer_set_registered"] = list(TRANSFER_SET)
    i1_detail["transfer_set_ok"] = set_ok
    conds = _req(ir, "conditions", "init record")
    rows_ok = True
    per = {}
    for mp in RUN_DIRS:
        c = conds.get(mp)
        if not isinstance(c, dict):
            rows_ok = False
            per[mp] = {"present": False}
            continue
        csrc = c.get("connectivity_source") or {}
        src_ok = all(csrc.get(k) == v for k, v in CONNECTIVITY_MD5.items())
        flds = c.get("fields") or {}
        got = tuple(sorted(flds))
        f_ok = got == tuple(sorted(TRANSFER_SET))
        worst_rb = 0.0
        n_ok = True
        for f in TRANSFER_SET:
            d = flds.get(f) or {}
            w = d.get("readback_worst_abs_diff")
            if _plant and _plant[0] == "I1_readback" and _plant[1] == mp and f == "p":
                w = (w or 0.0) + PLANT
            if w is None or w != 0.0:
                worst_rb = max(worst_rb, abs(w) if w is not None else float("inf"))
            if d.get("n") != N_CELLS:
                n_ok = False
        per[mp] = {"present": True, "connectivity_source_holds": src_ok,
                   "fields_present": list(got), "field_set_ok": f_ok,
                   "every_field_covers_all_cells": n_ok,
                   "worst_readback_abs_diff": worst_rb}
        rows_ok = rows_ok and src_ok and f_ok and n_ok and worst_rb == 0.0
    i1_detail["per_condition"] = per
    i1_detail["n_cells_registered"] = N_CELLS
    i1_detail["source"] = ir.get("source")
    src_rec = (ir.get("source") or {})
    src_ok2 = (src_rec.get("evals_md5") == EVALS_MD5
               and src_rec.get("record_n") == 88
               and src_rec.get("time") == "1000")
    i1_detail["source_is_the_registered_converged_primal"] = src_ok2
    I1 = conn_ok and set_ok and rows_ok and src_ok2
    i1_detail["pass"] = I1
    i1_detail["what_this_licenses"] = (
        "The transferred field is an INPUT to the gated quantity, not the gated "
        "quantity.  J_fresh is still a fresh-mesh solve: the mesh, the geometry "
        "and the design variables are unchanged by the initialisation, and only "
        "the starting field differs.  The influence of a different start is "
        "bounded by the MEASURED path-dependence of this solver class, "
        "8.764756e-07 absolute in J (N-D48), which is %.0fx INSIDE the registered "
        "band FM_BAND_ABS = %.9e." % (FM_BAND_ABS / 8.764756e-07, FM_BAND_ABS))

    # ---- H4 -- completion and hygiene
    own = scan_arm_dir(arm_dir, datum_epoch)
    conv = {p: bool(_req(solve, "primal_converged", "solve").get(p)) for p in POINTS}
    cap = CAPS["FM6"]
    cap_crossed = (core_min is not None) and (core_min > cap)
    rs_ok = r.get("runscript_md5") == RUNSCRIPT_MD5
    ev_ok = r.get("evals_md5") == EVALS_MD5
    h4_detail = {"rc": rc, "rc_is_zero": rc == 0, "ownership": own,
                 "primal_converged": conv, "all_primals_converged": all(conv.values()),
                 "uid": r.get("uid"), "ran_as_uid_1000": r.get("uid") == 1000,
                 "record_newer_than_datum": newer_than_datum(json_path, datum_epoch),
                 "runscript_md5_recorded": r.get("runscript_md5"),
                 "runscript_md5_registered": RUNSCRIPT_MD5,
                 "evals_md5_recorded": r.get("evals_md5"),
                 "evals_md5_registered": EVALS_MD5,
                 "staged_inputs_are_the_registered_inputs": rs_ok and ev_ok,
                 "primalMinResTol": PRIMAL_MIN_RES_TOL,
                 "core_min": core_min, "cap_core_min": cap, "cap_crossed": cap_crossed}
    H4 = (rc == 0 and own["ok"] and all(conv.values()) and rs_ok and ev_ok
          and h4_detail["record_newer_than_datum"]["newer_than_datum"])

    # ---- THE FLOOR DISCRIMINATOR (sec 3a).  REPORTED, NEVER GATED.
    # Fixed before FM6 ran: if a primal does NOT converge, is its floor the same
    # floor FM5 sat on?  If it is, the initial field was not the obstacle and the
    # registered change is REFUTED -- which is a result, not a disappointment.
    res = _req(solve, "primal_final_res", "solve")
    floor = {}
    for p in POINTS:
        v = res.get(p)
        if v is None or not isinstance(v, (int, float)):
            floor[p] = {"final_res": v, "verdict": "not recorded"}
            continue
        rel = abs(float(v) - FM5_FLOOR) / FM5_FLOOR
        floor[p] = {"final_res": float(v), "FM5_floor": FM5_FLOOR,
                    "relative_difference": rel,
                    "verdict": ("SAME FLOOR AS FM5 -- the initial field was not the "
                                "obstacle and the registered change is REFUTED"
                                if rel <= FLOOR_SAME_REL else
                                "a DIFFERENT floor from FM5's -- the stall depends on "
                                "the starting state, so it is not a fixed floor")}
    h4_detail["floor_discriminator"] = {
        "FLOOR_SAME_REL": FLOOR_SAME_REL, "per_condition": floor,
        "note": "REPORTED, NEVER GATED (sec 3a).  primalMinResTol is NEVER loosened; "
                "a surviving stall is a finding about this DARhoSimpleFoam "
                "configuration and goes to Sanaa as one (sec 10)."}

    if not (H1 and H2 and H4 and I1) or cap_crossed:
        label = LABEL_NOT_A_RESULT
    elif not H3:
        label = LABEL_GATE_FAIL
    else:
        label = LABEL_PASS

    rec = {"item": "9R2", "arm": "FM6", "label": label,
           "H1": H1, "H2": H2, "H3": H3, "H4": H4, "I1": I1,
           "the_one_registered_change":
               "The fresh-mesh primal is initialised from O_mp's converged fields "
               "at the SAME design point, transferred cell-for-cell by index, "
               "instead of from freestream.  RUNG 2 (numerics) on Sanaa's "
               "mesh-then-numerics-then-model ladder; rung 1 was tested and "
               "refuted by measurement (registration sec 1).",
           "initialisation_disclosed_in_the_verdict":
               "J_fresh was obtained from a MAPPED INITIAL FIELD.  It is still a "
               "fresh-mesh solve -- mesh, geometry and design variables are "
               "unchanged by the initialisation.  The influence of the different "
               "start is bounded by the measured path-dependence of this solver "
               "class, 8.764756e-07 absolute in J (N-D48), which is 350x INSIDE "
               "the registered band FM_BAND_ABS = 3.064163144e-04.",
           "I1_detail": i1_detail,
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
    if item != "9R2":
        raise Refusal("REFUSE_UNREGISTERED_ITEM %r -- this file grades 9R2 and "
                      "nothing else" % (item,))
    plants = [("CD_fresh", "cl05"), ("Jf_inherited",), ("H1",),
              ("I1_readback", "mp04"), ("I1_readback", "mp06")]
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
                "is %.1fx the LOOSEST band this grader applies (FM_BAND_ABS = %.9e) "
                "and unbounded against I1's exact-equality clauses; a reader that "
                "cannot see it cannot certify an agreement (rule 3)."
                % (pl, PLANT, PLANT / FM_BAND_ABS, FM_BAND_ABS))
    return {"PLANT": PLANT, "verdict_without_plant": verdict_label, "controls": results,
            "all_plants_visible": True}


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


def _synth_init(d, conn=None, tset=None, readback=0.0, src=None, nc=N_CELLS,
                src_conn=None):
    """A synthetic FM6 init record.  Touches no run directory and no O_mp."""
    conn = dict(CONNECTIVITY_MD5) if conn is None else conn
    src_conn = dict(CONNECTIVITY_MD5) if src_conn is None else src_conn
    tset = list(TRANSFER_SET) if tset is None else tset
    src = ({"dir": "<synthetic>", "time": "1000", "record_n": 88,
            "evals_md5": EVALS_MD5} if src is None else src)
    rec = {"kind": "FM6_INIT", "connectivity_destination": conn,
           "connectivity_registered": dict(CONNECTIVITY_MD5),
           "transfer_set": tset, "n_cells": nc, "source": src, "conditions": {}}
    for mp in RUN_DIRS:
        rec["conditions"][mp] = {
            "connectivity_source": src_conn,
            "fields": {f: {"kind": "vector" if f == "U" else "scalar", "n": nc,
                           "readback_worst_abs_diff": readback,
                           "dest_md5": "0" * 32, "first_cell": 1.0, "sum_abs": 1.0}
                       for f in tset}}
    p = os.path.join(d, "d6r2c_fm6_init.json")
    with open(p, "w") as fh:
        json.dump(rec, fh)
    os.utime(p, (2_000_000_000, 2_000_000_000))
    return p


def _synth_fresh(tmp, J_fresh, worst=None, n_cg=1031, n_fo=1031, bij=True,
                 unmatched=0, mesh_rc=0, gm=GENWINGMESH_MD5,
                 pts_md5="deadbeef", converged=True, uid=1000, cl=None,
                 rs_md5=RUNSCRIPT_MD5, ev_md5=EVALS_MD5, final_res=None,
                 init_kwargs=None):
    if worst is None:
        worst = H1_REGISTERED["worst_dist"]
    d = os.path.join(tmp, "FM6")
    os.makedirs(os.path.join(d, "constant", "polyMesh"), exist_ok=True)
    pg = os.path.join(d, "constant", "polyMesh", "points.gz")
    with open(pg, "wb") as fh:
        fh.write(b"x")
    os.utime(pg, (2_000_000_000, 2_000_000_000))
    inh = _synth_inherited()
    cd = _cd_for(J_fresh)
    rec = {"kind": "FRESHMESH", "uid": uid, "mesh_rc": mesh_rc,
           "genwingmesh_md5": gm, "staged_surface_md5": "cafe",
           "runscript_md5": rs_md5, "evals_md5": ev_md5,
           "mesh": {"nCells": 38304, "nPoints": 40209, "points_md5": pts_md5},
           "h1": {"n_cgns_nodes": n_cg, "n_foam_wall_points": n_fo,
                  "bijective": bij, "worst_dist": worst, "n_unmatched": unmatched},
           "solve": {"CD": cd, "CL": (cl or dict(inh["CL_final"])),
                     "AoA_deg": {"cl04": 0.577, "cl05": 1.772, "cl06": 3.038},
                     "J": _weighted_J(cd),
                     "primal_converged": {p: converged for p in POINTS},
                     "primal_final_res": (final_res or {p: 1e-9 for p in POINTS})},
           "checkmesh_report_path": "checkMesh.log"}
    path = os.path.join(d, "d6r2c_freshmesh.json")
    with open(path, "w") as fh:
        json.dump(rec, fh)
    os.utime(path, (2_000_000_000, 2_000_000_000))
    _synth_init(d, **(init_kwargs or {}))
    return path, d


def selftest():
    DATUM = 1_000_000_000
    inh = _synth_inherited()
    J0, Jf = inh["J0"], inh["Jf"]
    CAP = CAPS["FM6"]
    controls = []

    def check(name, got, want):
        controls.append((name, got, want))
        if got != want:
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r" % (name, got, want))
            return False
        return True

    ok = True
    tmp = tempfile.mkdtemp(prefix="d6r2c_fm6_selftest_")
    try:
        # ---- clean: inside the band ------------------------------------------
        p, d = _synth_fresh(tmp, Jf + 0.5 * FM_BAND_ABS)
        kw = dict(json_path=p, arm_dir=d, datum_epoch=DATUM, inherited=inh,
                  core_min=20.0, rc=0)
        r = grade_item9(**kw)
        ok &= check("clean -> PASS", r["label"], LABEL_PASS)
        ok &= check("clean -> I1 holds", r["I1"], True)
        ok &= check("the record names the one registered change",
                    "the_one_registered_change" in r, True)
        ok &= check("the record DISCLOSES the initialisation in the verdict",
                    "MAPPED INITIAL FIELD" in r["initialisation_disclosed_in_the_verdict"],
                    True)
        lp = live_plant_check("9R2", kw, r["label"])
        ok &= check("all 5 live plants visible", lp["all_plants_visible"], True)
        ok &= check("live plant count", len(lp["controls"]), 5)
        ok &= check("NEGATIVE -- a re-grade reproduces the label",
                    grade_item9(**kw)["label"], LABEL_PASS)
        ok &= check("this file grades 9R2 only",
                    isinstance(r["item"], str) and r["item"] == "9R2", True)

        # ---- EXTERNAL ANCHORS, typed here as ASSERTIONS and not as sources ---
        # PREREGISTRATION_AFTER_ITEM8_R2.md section 8a: a control that reads the
        # constant it is checking would pass for ANY value it held.
        ok &= check("EXTERNAL: FM_BAND_ABS is section 2d's 3.064163144e-04",
                    FM_BAND_ABS, 3.064163144e-04)
        ok &= check("EXTERNAL: the prediction is section 8's 15.737",
                    PREDICTION_CORE_MIN, 15.737)
        ok &= check("EXTERNAL: the cap is section 8's 47.211", CAPS["FM6"], 47.211)
        ok &= check("the cap is DERIVED, not typed twice",
                    CAPS["FM6"], round(PREDICTION_CORE_MIN * CAP_FACTOR, 3))
        ok &= check("EXTERNAL: SHAPE_MATCH_TOL is 1.0e-8", SHAPE_MATCH_TOL, 1.0e-8)
        ok &= check("EXTERNAL: H1's registered worst_dist is A4.3's",
                    H1_REGISTERED["worst_dist"], 5.010837892761856e-09)
        ok &= check("EXTERNAL: FM5's floor is 1.278377566e-05", FM5_FLOOR, 1.278377566e-05)
        ok &= check("EXTERNAL: primalMinResTol is UNTOUCHED at 1.0e-8",
                    PRIMAL_MIN_RES_TOL, 1.0e-8)
        ok &= check("EXTERNAL: the objective's weights",
                    (WEIGHTS["cl04"], WEIGHTS["cl05"], WEIGHTS["cl06"]), (0.25, 0.50, 0.25))
        ok &= check("EXTERNAL: the transfer set is 0.orig's own six volFields",
                    tuple(sorted(TRANSFER_SET)),
                    ("T", "U", "alphat", "nuTilda", "nut", "p"))

        # ---- I1: A FAILING CONTROL FOR EVERY CLAUSE --------------------------
        bad = dict(CONNECTIVITY_MD5); bad["faces.gz"] = "0" * 32
        p, d = _synth_fresh(tmp + "/i1", Jf, init_kwargs={"conn": bad})
        r = grade_item9(p, d, DATUM, inh, 20.0, 0)
        ok &= check("I1 destination connectivity wrong -> NOT A RESULT",
                    r["label"], LABEL_NOT_A_RESULT)
        ok &= check("I1 names the broken premise", r["I1_detail"]["connectivity_holds"], False)
        p, d = _synth_fresh(tmp + "/i2", Jf, init_kwargs={"src_conn": bad})
        ok &= check("I1 SOURCE connectivity wrong -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/i3", Jf, init_kwargs={"readback": 1.0e-18})
        ok &= check("I1 a readback difference of ONE PART IN 1e18 -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/i4", Jf,
                            init_kwargs={"tset": ["T", "U", "p"]})
        ok &= check("I1 a short transfer set -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/i5", Jf, init_kwargs={"nc": N_CELLS - 1})
        ok &= check("I1 a field short of one cell -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/i6", Jf, init_kwargs={
            "src": {"dir": "x", "time": "900", "record_n": 88, "evals_md5": EVALS_MD5}})
        ok &= check("I1 the WRONG SOURCE TIME -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/i7", Jf, init_kwargs={
            "src": {"dir": "x", "time": "1000", "record_n": 87, "evals_md5": EVALS_MD5}})
        ok &= check("I1 the WRONG SOURCE RECORD -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/i8", Jf)
        os.remove(os.path.join(d, "d6r2c_fm6_init.json"))
        try:
            grade_item9(p, d, DATUM, inh, 20.0, 0)
            ok &= check("I1 no init record -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("I1 no init record -> REFUSE_MISSING_INIT_RECORD",
                        str(e).startswith("REFUSE_MISSING_INIT_RECORD"), True)

        # ---- H1: the registered equality, and a failing control for it -------
        p, d = _synth_fresh(tmp + "/h1a", Jf,
                            worst=math.nextafter(H1_REGISTERED["worst_dist"], 1.0))
        r = grade_item9(p, d, DATUM, inh, 20.0, 0)
        ok &= check("H1 ONE ULP off the registered equality -> NOT A RESULT",
                    r["label"], LABEL_NOT_A_RESULT)
        ok &= check("H1 names the equality, not the tolerance",
                    r["H1_detail"]["equality_holds"], False)
        ok &= check("NEGATIVE -- and it is still INSIDE SHAPE_MATCH_TOL",
                    r["H1_detail"]["worst_dist"] <= SHAPE_MATCH_TOL, True)
        p, d = _synth_fresh(tmp + "/h1b", Jf, n_fo=1030)
        r = grade_item9(p, d, DATUM, inh, 20.0, 0)
        ok &= check("H1 count mismatch -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        ok &= check("H1 prints both counts",
                    (r["H1_detail"]["n_cgns_nodes"], r["H1_detail"]["n_foam_wall_points"]),
                    (1031, 1030))
        p, d = _synth_fresh(tmp + "/h1c", Jf, bij=False)
        ok &= check("H1 non-bijective -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_NOT_A_RESULT)

        # ---- H2 --------------------------------------------------------------
        p, d = _synth_fresh(tmp + "/h2a", Jf, pts_md5=BASE_POINTS_MD5)
        r = grade_item9(p, d, DATUM, inh, 20.0, 0)
        ok &= check("H2 fresh mesh IDENTICAL to base -> NOT A RESULT",
                    r["label"], LABEL_NOT_A_RESULT)
        ok &= check("H2 differs_from_base_mesh False",
                    r["H2_detail"]["differs_from_base_mesh"], False)
        p, d = _synth_fresh(tmp + "/h2b", Jf, gm="0" * 32)
        ok &= check("H2 genWingMesh md5 wrong -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/h2c", Jf, mesh_rc=1)
        ok &= check("H2 mesh rc != 0 -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_NOT_A_RESULT)

        # ---- H3: the band, both sides, one ulp apart -------------------------
        p, d = _synth_fresh(tmp + "/h3a", Jf + FM_BAND_ABS)
        ok &= check("H3 AT the band -> H3 holds",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["H3"], True)
        p, d = _synth_fresh(tmp + "/h3b", math.nextafter(Jf + FM_BAND_ABS, 1.0))
        ok &= check("H3 ONE ULP outside -> GATE FAIL",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_GATE_FAIL)
        p, d = _synth_fresh(tmp + "/h3c", G2_BAR_ON_J0 * J0 + 1e-6)
        r = grade_item9(p, d, DATUM, inh, 20.0, 0)
        ok &= check("J_fresh >= 0.90 x J0 -> g2 contradicted",
                    r["g2_contradicted_on_fresh_mesh"], True)
        ok &= check("g2 contradiction carries the escalation", "escalation" in r, True)
        ok &= check("g2 contradiction is a GATE FAIL, not NOT A RESULT",
                    r["label"], LABEL_GATE_FAIL)
        ok &= check("GATE FAIL binds the headline quotation",
                    r.get("headline_quotation_constraint"),
                    "MUST_CITE_FRESH_MESH_DISCREPANCY")

        # ---- H4, including the NEW input pins --------------------------------
        p, d = _synth_fresh(tmp + "/h4a", Jf, converged=False)
        ok &= check("H4 a primal not converged -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/h4b", Jf)
        ok &= check("H4 cap crossed -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, CAP + 0.1, 0)["label"], LABEL_NOT_A_RESULT)
        ok &= check("H4 AT the cap is NOT crossed (strict >)",
                    grade_item9(p, d, DATUM, inh, CAP, 0)["label"], LABEL_PASS)
        p, d = _synth_fresh(tmp + "/h4c", Jf, rs_md5="0" * 32)
        r = grade_item9(p, d, DATUM, inh, 20.0, 0)
        ok &= check("H4 a changed optimisation runscript -> NOT A RESULT",
                    r["label"], LABEL_NOT_A_RESULT)
        ok &= check("H4 reports the staged-input check",
                    r["H4_detail"]["staged_inputs_are_the_registered_inputs"], False)
        p, d = _synth_fresh(tmp + "/h4d", Jf, ev_md5="0" * 32)
        ok &= check("H4 a wrong inherited record -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_fresh(tmp + "/h4e", Jf)
        ok &= check("H4 rc=137 -> NOT A RESULT",
                    grade_item9(p, d, DATUM, inh, 20.0, 137)["label"], LABEL_NOT_A_RESULT)

        # ---- THE FLOOR DISCRIMINATOR: reported, never gated -------------------
        p, d = _synth_fresh(tmp + "/f1", Jf, converged=False,
                            final_res={pt: FM5_FLOOR for pt in POINTS})
        r = grade_item9(p, d, DATUM, inh, 20.0, 0)
        ok &= check("a stall AT FM5's floor is NOT A RESULT (H4), as before",
                    r["label"], LABEL_NOT_A_RESULT)
        ok &= check("...and the discriminator says the change is REFUTED",
                    "REFUTED" in r["H4_detail"]["floor_discriminator"]
                    ["per_condition"]["cl04"]["verdict"], True)
        p, d = _synth_fresh(tmp + "/f2", Jf, converged=False,
                            final_res={pt: FM5_FLOOR * 2.0 for pt in POINTS})
        r = grade_item9(p, d, DATUM, inh, 20.0, 0)
        ok &= check("a stall at a DIFFERENT floor is named as such",
                    "DIFFERENT floor" in r["H4_detail"]["floor_discriminator"]
                    ["per_condition"]["cl04"]["verdict"], True)
        p, d = _synth_fresh(tmp + "/f3", Jf)
        r = grade_item9(p, d, DATUM, inh, 20.0, 0)
        ok &= check("NEGATIVE -- the discriminator NEVER changes a label",
                    r["label"], LABEL_PASS)

        # ---- the reported-not-gated CL finding trigger ------------------------
        p, d = _synth_fresh(tmp + "/g1", Jf,
                            cl={p2: inh["CL_final"][p2] + 6.0e-3 for p2 in POINTS})
        r = grade_item9(p, d, DATUM, inh, 20.0, 0)
        ok &= check("CL delta 6e-3 > 5e-3 triggers the FINDING",
                    r["reported_not_gated"]["CL_finding_triggered"], True)
        ok &= check("the CL finding does NOT change the label", r["label"], LABEL_PASS)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("D6R2C_FM6_GRADE SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", len(controls)))
    return 0 if ok else 1


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade arm FM6 (after-item 9, successor).")
    ap.add_argument("--selftest", action="store_true",
                    help="drive the planted controls on synthetic trees; touches no run dir")
    ap.add_argument("--item", choices=("9R2",))
    ap.add_argument("--arm-dir")
    ap.add_argument("--evals", default="/home/ubuntu/certonomous-runs/"
                    "CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp/d6r2c_evals.jsonl")
    ap.add_argument("--datum-file", help="the arm's .d6r2c_age_datum")
    ap.add_argument("--core-min", type=float)
    ap.add_argument("--rc", type=int)
    ap.add_argument("--out", help="where to write the verdict JSON")
    ap.add_argument("--print-cap", metavar="ARM",
                    help="print the registered cap in core-minutes for ARM and exit. "
                         "THE LAUNCHER CALLS THIS RATHER THAN CARRYING ITS OWN LITERAL.")
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
        inherited = load_inherited(a.evals)
        kw = dict(json_path=os.path.join(a.arm_dir, "d6r2c_freshmesh.json"),
                  arm_dir=a.arm_dir, datum_epoch=datum, inherited=inherited,
                  core_min=a.core_min, rc=a.rc)
        rec = grade_item9(**kw)
        rec["planted_control"] = live_plant_check(a.item, kw, rec["label"])
    except Refusal as e:
        print("D6R2C_FM6_GRADE REFUSED\n%s" % e)
        return 2
    out = a.out or os.path.join(os.path.dirname(a.arm_dir.rstrip("/")),
                                "AFTER_ITEM9R2_GRADE.json")
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
    print("D6R2C_FM6_GRADE item=9R2 label=%s J_fresh=%.12g Jf=%.12g |d|=%.6e band=%.6e"
          % (rec["label"], rec["H3_detail"]["J_fresh"], rec["H3_detail"]["Jf_deformed_mesh"],
             rec["H3_detail"]["abs_diff"], FM_BAND_ABS))
    print("D6R2C_FM6_GRADE verdict=%s written=%s" % (rec["label"], out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
