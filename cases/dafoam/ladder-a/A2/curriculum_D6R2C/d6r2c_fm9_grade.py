#!/usr/bin/env python3
# ===========================================================================
# d6r2c_fm9_grade.py -- THE GRADING PATH FOR ARM FM9 (the mesh actually arrives)
# ===========================================================================
#
# Registered by PREREGISTRATION_FRESHMESH_ARRIVES.md section 11, and IN THE SAME
# COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS (CLAUDE.md rule 2).
#
# A FORK of d6r2c_fm6_grade.py (md5 1a5ca51f8dab59e3c72b9a71ce8f77e6), unedited
# on disk.  WHAT CHANGED, EXHAUSTIVELY:
#   (1) H2 IS REPLACED BY M1.  H2 checked that the fresh mesh EXISTED, came from
#       the pinned genWingMesh.py, and DIFFERED from the base.  ALL THREE WERE
#       TRUE IN FM5, FM7 AND FM8 WHILE THE SOLVER READ A DECOMPOSITION OF THE
#       BASE MESH BUILT ONE PHASE EARLIER.  M1 reads THE MESH THE SOLVER LOADED.
#   (2) I1 IS DELETED.  There is no field transfer in this arm: the cell-for-cell
#       index copy is NOT VALID once the fresh mesh genuinely arrives (measured
#       warped-to-fresh displacement: median 17.8 first-cell heights, max 4391).
#       This arm starts from freestream and changes ONE thing.
#   (3) H4 takes convergence FROM THE LOG.  primal_converged defaults to True and
#       its source file has four readers and no writer anywhere in this repo.
#   (4) H3's band is unchanged but WHAT IT COMPARES HAS CHANGED MEANING: for the
#       first time J_fresh really is a fresh-mesh value (sec 4).
#
# A FORK of d6r2c_after_grade.py (md5 6c22013af54569ae651f8f23d1088861), which
# stays on disk unedited and keeps grading FM5 under its own document.  What
# changed, exhaustively:
#   (1) item 8 (D1-D6) is DELETED -- this document does not register it;
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
import re
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

# ---- M1's REGISTERED HASHES (sec 3).
# "the base mesh, which the loaded mesh must NOT be" (sec 3, M1)
BASE_POINTS_MD5_M1 = "0fb1935a9b8781b73ac4ccb136e3ec68"
# "the decomposed base mesh FM5/FM7/FM8 actually solved on" (sec 1a)
STALE_PROC_POINTS_MD5 = "c7f5feda2f4dc6774cf320d4cb2ffcb3"
# "38,304 cells, 40,209 points" (sec 9) -- corroboration limb, from the LOG
N_CELLS_M1 = 38304
N_POINTS_M1 = 40209
# "the three conditions x four ranks = twelve processor meshes" (sec 3, M1)
N_PROCESSORS = 4

# ---- H1's registered equality of ADDENDUM 4 A4.3, which FM5 met and
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
# "PREDICTION 171.0 s wall x 4 ranks / 60 = 11.400 core-min"  (sec 8)
PREDICTION_CORE_MIN = 11.400
# "REGISTERED CAP (3.00x) = 34.200 core-min"  (sec 8)
CAP_FACTOR = 3.00
CAPS = {"FM9": round(PREDICTION_CORE_MIN * CAP_FACTOR, 3)}

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

def grade_item9(json_path, arm_dir, datum_epoch, inherited, core_min, rc, _plant=None, log_path=None):
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
    # H2 IS NO LONGER A GATE.  Its three clauses are all TRUE of FM5, FM7 and
    # FM8, which never solved on the mesh it describes.  PROVENANCE IS STILL
    # WORTH RECORDING -- it says the mesh came from the pinned family script --
    # BUT IT IS NOT EVIDENCE THAT THE SOLVER READ IT.  M1 is.
    h2_detail["role"] = ("REPORTED, NEVER GATED (sec 3).  Provenance of the file, "
                         "not evidence that the solver loaded it.  All three of "
                         "these clauses passed in FM5, FM7 and FM8.")
    H2_reported = (h2_detail["genwingmesh_md5_ok"] and h2_detail["mesh_rc_is_zero"]
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

    # ---- M1 -- THE MESH THE SOLVER LOADED IS THE FRESH MESH ---------------
    # H2 checked that the mesh EXISTED, came from the pinned script, and DIFFERED
    # from the base.  ALL THREE WERE TRUE IN FM5, FM7 AND FM8 WHILE THE SOLVER
    # READ SOMETHING ELSE.  M1 READS WHAT THE SOLVER LOADED, by rebuilding the
    # undecomposed mesh from the solver's own processor directories.
    #
    # A NOTE ON WHAT IS ACHIEVABLE, because the brief asked for something that is
    # not: A PROCESSOR'S OWN points.gz md5 CAN NEVER EQUAL THE WHOLE MESH'S -- it
    # holds a SUBSET.  "Twelve hashes equal to the fresh mesh's" would have to be
    # weakened to pass.  Rebuilding the arrays and requiring EXACT equality is
    # achievable, is stronger than a hash, and is the technique that exposed the
    # defect in the first place.
    import d6r2c_fm9_stage as st
    fresh_pm = os.path.join(arm_dir, "constant", "polyMesh")
    fresh_pts_file = os.path.join(fresh_pm, "points.gz")
    if not os.path.isfile(fresh_pts_file):
        raise Refusal("REFUSE_NO_FRESH_MESH %s -- there is nothing to have "
                      "arrived" % fresh_pts_file)
    fresh_md5 = _md5(fresh_pts_file)
    fresh_pts = st.read_points(fresh_pts_file)
    fresh_mtime = os.lstat(fresh_pts_file).st_mtime
    base_pts_file = os.path.join(arm_dir, "base_points_reference.gz")
    m1 = {"fresh_points_md5": fresh_md5,
          "fresh_differs_from_base": fresh_md5 != BASE_POINTS_MD5_M1,
          "n_points_fresh": len(fresh_pts),
          "per_condition": {}, "limbs": {}}
    loaded_ok, timeline_ok, nproc_ok = True, True, True
    for mp in RUN_DIRS:
        mp_dir = os.path.join(arm_dir, mp)
        row = {}
        try:
            procs = st.processor_dirs(mp_dir)
            row["n_processor_dirs"] = len(procs)
            if len(procs) != N_PROCESSORS:
                nproc_ok = False
            loaded = st.reconstruct_loaded_points(mp_dir, len(fresh_pts))
            worst = st.max_point_difference(loaded, fresh_pts)
            if _plant and _plant[0] == "M1" and _plant[1] == mp:
                worst = worst + PLANT
            row["max_point_difference_from_fresh"] = worst
            row["loaded_IS_the_fresh_mesh"] = (worst == 0.0)
            if worst != 0.0:
                loaded_ok = False
            # the TIMELINE limb -- the check that would have caught FM8 in one line
            times = []
            for pd in procs:
                p = os.path.join(mp_dir, pd, "constant", "polyMesh", "points.gz")
                if not os.path.isfile(p):
                    p = p[:-3]
                times.append(os.lstat(p).st_mtime if os.path.exists(p) else None)
            row["processor_mesh_mtimes"] = times
            row["all_at_or_after_fresh_mesh"] = all(
                t is not None and t >= fresh_mtime for t in times)
            if not row["all_at_or_after_fresh_mesh"]:
                timeline_ok = False
        except (Refusal, st.Refusal) as e:
            # TWO Refusal CLASSES.  d6r2c_fm9_stage defines its own, and a bare
            # `except Refusal` in this file DOES NOT CATCH IT -- the reconstruction
            # would escape as an uncaught exception instead of becoming a recorded
            # NOT A RESULT.  Found by driving the missing-processor control.
            row["refusal"] = str(e).split("\n")[0]
            row["loaded_IS_the_fresh_mesh"] = False
            row["all_at_or_after_fresh_mesh"] = False
            loaded_ok = timeline_ok = False
        m1["per_condition"][mp] = row
    # CORROBORATION FROM A DIFFERENT OBJECT: the solver's own reported statistics.
    # A hash check and a log check read different things; if they disagree that is
    # a finding and the arm refuses rather than believing either.
    log_cells = log_points = None
    if log_path and os.path.isfile(log_path):
        txt = open(log_path, errors="replace").read()
        mc = re.findall(r"cells:\s*(\d+)", txt)
        mp_ = re.findall(r"points:\s*(\d+)", txt)
        log_cells = int(mc[-1]) if mc else None
        log_points = int(mp_[-1]) if mp_ else None
    corrob_ok = (log_cells == N_CELLS_M1 and log_points == N_POINTS_M1)
    m1["limbs"] = {
        "loaded_is_fresh_all_conditions": loaded_ok,
        "timeline_all_processor_meshes_at_or_after_fresh": timeline_ok,
        "processor_count_is_registered": nproc_ok,
        "log_corroboration": {"cells": log_cells, "points": log_points,
                              "registered": [N_CELLS_M1, N_POINTS_M1],
                              "ok": corrob_ok},
        "fresh_differs_from_base": fresh_md5 != BASE_POINTS_MD5_M1,
    }
    M1 = (loaded_ok and timeline_ok and nproc_ok and corrob_ok
          and fresh_md5 != BASE_POINTS_MD5_M1)
    m1["pass"] = M1
    m1["what_this_exercises"] = (
        "THE MESH THE SOLVER LOADED, rebuilt from its own processor directories "
        "via pointProcAddressing and compared to the generated mesh by EXACT "
        "point equality -- not the existence, provenance or difference-from-base "
        "of a file it may never have read.  A CHECK MUST EXERCISE THE THING, NOT "
        "DESCRIBE IT (L-595).")
    if not loaded_ok:
        m1["why"] = ("THE FRESH MESH DID NOT ARRIVE for: %r.  That is the FM5 / "
                     "FM7 / FM8 defect recurring, and it is NOT A RESULT."
                     % [k for k, v in m1["per_condition"].items()
                        if not v.get("loaded_IS_the_fresh_mesh")])

    # ---- H4 -- completion and hygiene
    own = scan_arm_dir(arm_dir, datum_epoch)
    # CONVERGENCE FROM THE LOG, NOT FROM primal_converged.  That field DEFAULTS
    # TO True and its source primal_residual.json HAS FOUR READERS AND NO WRITER
    # ANYWHERE IN THIS REPOSITORY, so the clause it feeds is vacuous.
    conv = {p: bool(_req(solve, "primal_converged", "solve").get(p)) for p in POINTS}
    logconv = {"source": "the arm log", "checked": False,
               "why_not_the_field": "primal_converged defaults to True and its "
                                    "source file has four readers and no writer"}
    if log_path and os.path.isfile(log_path):
        _t = open(log_path, errors="replace").read()
        _n = _t.count("Primal solution failed")
        logconv = {"source": "the arm log", "checked": True,
                   "n_primal_solution_failed": _n, "ok": _n == 0,
                   "min_residuals": re.findall(r"Primal min residual ([0-9.eE+-]+)", _t)[:5],
                   "why_not_the_field": logconv["why_not_the_field"]}
    logconv_ok = bool(logconv.get("checked")) and bool(logconv.get("ok"))
    cap = CAPS["FM9"]
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
    h4_detail["convergence_from_the_log"] = logconv
    h4_detail["primal_converged_field_is_NOT_used"] = (
        "primal_converged is recorded above for the reader but NO CLAUSE RESTS ON "
        "IT: it defaults to True and its source file has four readers and no "
        "writer anywhere in this repository (sec 3d).")
    H4 = (rc == 0 and own["ok"] and logconv_ok and rs_ok and ev_ok
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

    if not (H1 and M1 and H4) or cap_crossed:
        label = LABEL_NOT_A_RESULT
    elif not H3:
        label = LABEL_GATE_FAIL
    else:
        label = LABEL_PASS

    rec = {"item": "FM9", "arm": "FM9", "label": label,
           "H1": H1, "M1": M1, "H3": H3, "H4": H4,
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
           "M1_detail": m1,
           "H1_detail": h1_detail, "H2_reported_not_gated": h2_detail,
           "H2_reported_value": H2_reported,
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
    if item != "FM9":
        raise Refusal("REFUSE_UNREGISTERED_ITEM %r -- this file grades FM9 and "
                      "nothing else" % (item,))
    plants = [("CD_fresh", "cl05"), ("Jf_inherited",), ("H1",),
              ("M1", "mp04"), ("M1", "mp06")]
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


def _synth_fresh(tmp, J_fresh, worst=None, n_cg=1031, n_fo=1031, bij=True,
                 unmatched=0, mesh_rc=0, gm=GENWINGMESH_MD5, pts_md5="deadbeef",
                 converged=True, uid=1000, cl=None, rs_md5=RUNSCRIPT_MD5,
                 ev_md5=EVALS_MD5):
    """The freshmesh record H1/H3/H4 read.  NO init record: this arm has no
    field transfer (sec 2)."""
    if worst is None:
        worst = H1_REGISTERED["worst_dist"]
    d = os.path.join(tmp, "FM9rec")
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
                     "primal_final_res": {p: 1e-9 for p in POINTS}},
           "checkmesh_report_path": "checkMesh.log"}
    path = os.path.join(d, "d6r2c_freshmesh.json")
    with open(path, "w") as fh:
        json.dump(rec, fh)
    os.utime(path, (2_000_000_000, 2_000_000_000))
    return path, d


def _mesh_tree(root, pts, mtime, n_proc=4, conds=("mp04","mp05","mp06"),
               unstaged=None, fresh_pts=None):
    """A synthetic arm: a fresh mesh, and per-condition decompositions that
    either DO or DO NOT carry it.  `unstaged` names conditions whose processors
    still hold the OLD points -- the FM5/FM7/FM8 state."""
    import gzip
    HDR = ("FoamFile\n{\n    version 2.0;\n    class %s;\n    object %s;\n}\n"
           "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n")
    def wpts(path, P, gz=True):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        body = (HDR % ("vectorField", "points")
                + "%d\n(\n%s\n)\n" % (len(P), "\n".join("(%g %g %g)" % p for p in P)))
        if gz:
            with gzip.open(path, "wt") as fh:
                fh.write(body)
        else:
            open(path, "w").write(body)
    def wlab(path, v):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with gzip.open(path, "wt") as fh:
            fh.write(HDR % ("labelList", "pointProcAddressing")
                     + "%d\n(\n%s\n)\n" % (len(v), "\n".join(str(x) for x in v)))
    fresh_pts = fresh_pts or pts
    fp = os.path.join(root, "constant", "polyMesh", "points.gz")
    wpts(fp, fresh_pts)
    os.utime(fp, (mtime, mtime))
    n = len(fresh_pts)
    for c in conds:
        src = (pts if (unstaged and c in unstaged) else fresh_pts)
        for k in range(n_proc):
            idx = list(range(k, n, n_proc))
            pm = os.path.join(root, c, "processor%d" % k, "constant", "polyMesh")
            wlab(os.path.join(pm, "pointProcAddressing.gz"), idx)
            pp = os.path.join(pm, "points.gz")
            wpts(pp, [src[i] for i in idx])
            t = mtime + 10 if not (unstaged and c in unstaged) else mtime - 60
            os.utime(pp, (t, t))
    return root


def selftest():
    DATUM = 1_000_000_000
    inh = _synth_inherited()
    J0, Jf = inh["J0"], inh["Jf"]
    CAP = CAPS["FM9"]
    controls = []

    def check(name, got, want):
        controls.append(name)
        nonlocal ok
        if got != want:
            ok = False
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r" % (name, got, want))

    ok = True
    tmp = tempfile.mkdtemp(prefix="d6r2c_fm9_selftest_")
    try:
        FRESH = [(float(i), 1.0, 2.0) for i in range(24)]
        OLD = [(float(i) + 0.5, 1.0, 2.0) for i in range(24)]
        MT = 2_000_000_000

        def arm(tag, **kw):
            d = os.path.join(tmp, tag, "FM9")
            _mesh_tree(d, OLD, MT, fresh_pts=FRESH, **kw)
            p, _ = _synth_fresh(os.path.join(tmp, tag), Jf + 0.5 * FM_BAND_ABS)
            # _synth_fresh writes into <tmp>/<tag>/FM6; move its record next to us
            import shutil as _sh
            _sh.copyfile(p, os.path.join(d, "d6r2c_freshmesh.json"))
            os.utime(os.path.join(d, "d6r2c_freshmesh.json"),
                     (2_000_000_000, 2_000_000_000))
            lg = os.path.join(d, "arm.log")
            open(lg, "w").write("cells: %d\npoints: %d\n"
                                "Time = 100\np initRes: 7.4e-06\n"
                                % (N_CELLS_M1, N_POINTS_M1))
            return os.path.join(d, "d6r2c_freshmesh.json"), d, lg

        # ---- clean: the fresh mesh ARRIVED in every condition -----------------
        p, d, lg = arm("a")
        kw = dict(json_path=p, arm_dir=d, datum_epoch=DATUM, inherited=inh,
                  core_min=5.0, rc=0, log_path=lg)
        r = grade_item9(**kw)
        check("clean -> M1 holds", r["M1"], True)
        check("clean -> PASS", r["label"], LABEL_PASS)
        check("M1 says it EXERCISES the mesh, not describes it",
              "EXERCISE THE THING" in r["M1_detail"]["what_this_exercises"], True)
        check("every condition's loaded mesh IS the fresh mesh",
              [v["loaded_IS_the_fresh_mesh"] for v in r["M1_detail"]["per_condition"].values()],
              [True, True, True])
        check("the timeline limb holds",
              r["M1_detail"]["limbs"]["timeline_all_processor_meshes_at_or_after_fresh"], True)
        check("the log corroboration limb holds",
              r["M1_detail"]["limbs"]["log_corroboration"]["ok"], True)
        check("H2 is REPORTED, not gated", "H2_reported_not_gated" in r, True)
        check("...and says so in the record",
              "NEVER GATED" in r["H2_reported_not_gated"]["role"], True)
        lp = live_plant_check("FM9", kw, r["label"])
        check("all live plants visible", lp["all_plants_visible"], True)

        # ---- THE FAILING CONTROL: one condition un-staged ---------------------
        p, d, lg = arm("b", unstaged=("mp05",))
        r = grade_item9(p, d, DATUM, inh, 5.0, 0, log_path=lg)
        check("ONE condition un-staged -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        check("...M1 fails", r["M1"], False)
        check("...and NAMES which condition did not arrive",
              "'mp05'" in r["M1_detail"]["why"] or "mp05" in r["M1_detail"]["why"], True)
        check("...while the OTHER conditions are still reported as arrived",
              r["M1_detail"]["per_condition"]["mp04"]["loaded_IS_the_fresh_mesh"], True)
        check("...and the FM5/FM7/FM8 defect is named in the refusal text",
              "FM8 defect" in r["M1_detail"]["why"], True)
        # ALL conditions un-staged: the exact FM8 state
        p, d, lg = arm("c", unstaged=("mp04", "mp05", "mp06"))
        r = grade_item9(p, d, DATUM, inh, 5.0, 0, log_path=lg)
        check("THE EXACT FM8 STATE -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        check("...all three named",
              sorted(k for k, v in r["M1_detail"]["per_condition"].items()
                     if not v["loaded_IS_the_fresh_mesh"]), ["mp04", "mp05", "mp06"])

        # ---- the timeline limb alone, which would have caught FM8 in one line --
        p, d, lg = arm("e")
        for c in ("mp04", "mp05", "mp06"):
            for k in range(4):
                f = os.path.join(d, c, "processor%d" % k, "constant", "polyMesh",
                                 "points.gz")
                os.utime(f, (MT - 60, MT - 60))
        r = grade_item9(p, d, DATUM, inh, 5.0, 0, log_path=lg)
        check("processor meshes older than the fresh mesh -> NOT A RESULT",
              r["label"], LABEL_NOT_A_RESULT)
        check("...the timeline limb is what fails",
              r["M1_detail"]["limbs"]["timeline_all_processor_meshes_at_or_after_fresh"],
              False)
        check("...and the CONTENT limb still passes, so the two limbs are independent",
              r["M1_detail"]["limbs"]["loaded_is_fresh_all_conditions"], True)

        # ---- the corroboration limb, from a DIFFERENT object ------------------
        p, d, lg = arm("f")
        open(lg, "w").write("cells: 12345\npoints: 40209\nTime = 100\np initRes: 7.4e-06\n")
        r = grade_item9(p, d, DATUM, inh, 5.0, 0, log_path=lg)
        check("the log reporting a DIFFERENT cell count -> NOT A RESULT",
              r["label"], LABEL_NOT_A_RESULT)
        check("...the corroboration limb is what fails",
              r["M1_detail"]["limbs"]["log_corroboration"]["ok"], False)
        p, d, lg = arm("g")
        check("NO LOG -> NOT A RESULT, never a silent pass",
              grade_item9(p, d, DATUM, inh, 5.0, 0)["label"], LABEL_NOT_A_RESULT)

        # ---- a missing decomposition is a refusal, not a pass -----------------
        p, d, lg = arm("h")
        import shutil as _sh2
        _sh2.rmtree(os.path.join(d, "mp06", "processor0"))
        r = grade_item9(p, d, DATUM, inh, 5.0, 0, log_path=lg)
        check("a missing processor directory -> NOT A RESULT",
              r["label"], LABEL_NOT_A_RESULT)
        check("...and it is recorded as a refusal on that condition",
              "refusal" in r["M1_detail"]["per_condition"]["mp06"], True)

        # ---- EXTERNAL ANCHORS, typed as assertions and not as sources ---------
        check("EXTERNAL: the base mesh hash", BASE_POINTS_MD5_M1,
              "0fb1935a9b8781b73ac4ccb136e3ec68")
        check("EXTERNAL: the mesh FM5/FM7/FM8 actually solved on",
              STALE_PROC_POINTS_MD5, "c7f5feda2f4dc6774cf320d4cb2ffcb3")
        check("EXTERNAL: the registered cell count", N_CELLS_M1, 38304)
        check("EXTERNAL: the registered point count", N_POINTS_M1, 40209)
        check("EXTERNAL: FM_BAND_ABS is section 2d's", FM_BAND_ABS, 3.064163144e-04)
        check("EXTERNAL: SHAPE_MATCH_TOL", SHAPE_MATCH_TOL, 1.0e-8)
        check("EXTERNAL: H1's registered worst_dist",
              H1_REGISTERED["worst_dist"], 5.010837892761856e-09)
        check("EXTERNAL: the prediction is section 8's 11.400", PREDICTION_CORE_MIN, 11.400)
        check("EXTERNAL: the cap is section 8's 34.200", CAPS["FM9"], 34.200)
        check("the cap is DERIVED, not typed twice",
              CAPS["FM9"], round(PREDICTION_CORE_MIN * CAP_FACTOR, 3))
        check("EXTERNAL: the objective's weights",
              (WEIGHTS["cl04"], WEIGHTS["cl05"], WEIGHTS["cl06"]), (0.25, 0.50, 0.25))
        check("EXTERNAL: primalMinResTol UNTOUCHED", PRIMAL_MIN_RES_TOL, 1.0e-8)

        # ---- H1, H3, H4 carried ----------------------------------------------
        p, d, lg = arm("i")
        rows = json.load(open(p))
        rows["h1"]["worst_dist"] = math.nextafter(H1_REGISTERED["worst_dist"], 1.0)
        json.dump(rows, open(p, "w"))
        os.utime(p, (2_000_000_000, 2_000_000_000))
        check("H1 one ulp off the registered equality -> NOT A RESULT",
              grade_item9(p, d, DATUM, inh, 5.0, 0, log_path=lg)["label"],
              LABEL_NOT_A_RESULT)
        p, d, lg = arm("j")
        rows = json.load(open(p))
        cd = {q: Jf + FM_BAND_ABS * 2 for q in POINTS}
        rows["solve"]["CD"] = cd
        rows["solve"]["J"] = _weighted_J(cd)
        json.dump(rows, open(p, "w"))
        os.utime(p, (2_000_000_000, 2_000_000_000))
        check("H3 outside the band -> GATE FAIL",
              grade_item9(p, d, DATUM, inh, 5.0, 0, log_path=lg)["label"],
              LABEL_GATE_FAIL)
        p, d, lg = arm("k")
        check("rc=137 -> NOT A RESULT",
              grade_item9(p, d, DATUM, inh, 5.0, 137, log_path=lg)["label"],
              LABEL_NOT_A_RESULT)
        check("cap crossed -> NOT A RESULT",
              grade_item9(p, d, DATUM, inh, CAP + 0.1, 0, log_path=lg)["label"],
              LABEL_NOT_A_RESULT)
        check("AT the cap is NOT crossed (strict >)",
              grade_item9(p, d, DATUM, inh, CAP, 0, log_path=lg)["label"], LABEL_PASS)

        # ---- ADDENDUM 1: THE CONTROL THAT DRIVES main(), NOT THE FUNCTION -----
        # THE DEFECT THIS EXISTS FOR: --log was absent from the parser and main()
        # never passed log_path, so on the CLI path the corroboration limb and
        # the convergence limb were both skipped and THIS GRADER COULD ONLY EVER
        # RETURN NOT A RESULT.  Every control above calls grade_item9 DIRECTLY and
        # none of them could see it.  I TESTED THE FUNCTION AND SHIPPED THE CLI.
        p, d, lg = arm("cli")
        df = os.path.join(d, ".d6r2c_age_datum")
        open(df, "w").write(str(DATUM))
        outp = os.path.join(d, "CLI_GRADE.json")
        rcmain = main(["--item", "FM9", "--arm-dir", d, "--datum-file", df,
                       "--core-min", "5.0", "--rc", "0", "--log", lg,
                       "--out", outp])
        check("main() accepts --log and exits 0", rcmain, 0)
        check("main() wrote the verdict", os.path.isfile(outp), True)
        got = json.load(open(outp))
        check("THROUGH THE CLI the verdict is PASS, not the unconditional "
              "NOT A RESULT the unrepaired entry point produced",
              got["label"], LABEL_PASS)
        check("...and the log-fed corroboration limb actually RAN",
              got["M1_detail"]["limbs"]["log_corroboration"]["ok"], True)
        check("...and the log-fed convergence limb actually RAN",
              got["H4_detail"]["convergence_from_the_log"]["checked"], True)
        # AND THE NEGATIVE: no --log through the CLI must still be NOT A RESULT
        outp2 = os.path.join(d, "CLI_GRADE_NOLOG.json")
        main(["--item", "FM9", "--arm-dir", d, "--datum-file", df,
              "--core-min", "5.0", "--rc", "0", "--out", outp2])
        check("NEGATIVE -- main() with NO --log is NOT A RESULT, never a silent pass",
              json.load(open(outp2))["label"], LABEL_NOT_A_RESULT)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("D6R2C_FM9_GRADE SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", len(controls)))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade arm FM6 (after-item 9, successor).")
    ap.add_argument("--selftest", action="store_true",
                    help="drive the planted controls on synthetic trees; touches no run dir")
    ap.add_argument("--item", choices=("FM9",))
    ap.add_argument("--arm-dir")
    ap.add_argument("--evals", default="/home/ubuntu/certonomous-runs/"
                    "CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp/d6r2c_evals.jsonl")
    ap.add_argument("--datum-file", help="the arm's .d6r2c_age_datum")
    ap.add_argument("--core-min", type=float)
    ap.add_argument("--rc", type=int)
    ap.add_argument("--out", help="where to write the verdict JSON")
    # ADDENDUM 1: --log WAS ABSENT AND main() NEVER PASSED log_path.  Both the
    # mesh-corroboration limb and the convergence limb sit behind
    # `if log_path and os.path.isfile(...)`, so ON THE CLI PATH THEY WERE SKIPPED
    # AND THIS GRADER COULD ONLY EVER RETURN NOT A RESULT.  The launcher emitted
    # `--log` and argparse rejected it.  The selftest did not see it because IT
    # CALLS THE GRADING FUNCTION DIRECTLY AND NEVER GOES THROUGH main() -- the
    # function was tested and the entry point was shipped.
    ap.add_argument("--log", help="the arm log: the ONLY source of convergence "
                                  "evidence and of the mesh corroboration limb")
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
                  core_min=a.core_min, rc=a.rc, log_path=a.log)
        rec = grade_item9(**kw)
        rec["planted_control"] = live_plant_check(a.item, kw, rec["label"])
    except Refusal as e:
        print("D6R2C_FM9_GRADE REFUSED\n%s" % e)
        return 2
    out = a.out or os.path.join(os.path.dirname(a.arm_dir.rstrip("/")),
                                "FM9_GRADE.json")
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
    print("D6R2C_FM9_GRADE item=FM9 label=%s J_fresh=%.12g Jf=%.12g |d|=%.6e band=%.6e"
          % (rec["label"], rec["H3_detail"]["J_fresh"], rec["H3_detail"]["Jf_deformed_mesh"],
             rec["H3_detail"]["abs_diff"], FM_BAND_ABS))
    print("D6R2C_FM9_GRADE verdict=%s written=%s" % (rec["label"], out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
