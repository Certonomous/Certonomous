#!/usr/bin/env python3
# ===========================================================================
# d6r2c_dec5_grade.py -- THE GRADING PATH FOR THE SUCCESSOR TO AFTER-ITEM 8
# ===========================================================================
#
# Registered by PREREGISTRATION_AFTER_ITEM8_R2.md section 11, and IN THE SAME
# COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS (CLAUDE.md rule 2).
#
# THIS FILE IS A FORK of d6r2c_after_grade.py (md5 6c22013af54569ae651f8f23d1088861),
# which stays on disk, unedited, and keeps grading arm FM5 under
# PREREGISTRATION_AFTER_ITEMS.md.  The fork exists because the successor
# registers NEW thresholds, and rule 2 closes a registration's gates after its
# first compute: a new threshold is a new document and a new instrument, never
# an edit to a frozen one (rule 6).  What changed, exhaustively:
#   (1) item 9 (H1-H4) is DELETED -- this document does not register it;
#   (2) REPRO_TOL, CLOSE_TOL and TRIM_MAX_EVALS are RE-DERIVED (sec 3);
#   (3) D2-GEO is NEW -- an external, md5-pinned, path-independent anchor (L-588);
#   (4) D1 now REFUSES a null trim-evaluation count (the cap was inert, sec 3);
#   (5) D1 now checks every incidence against the registered AoA bound (sec 1d);
#   (6) state B2 is NEW, REPORTED and NEVER GATED (sec 1e).
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
# PREREGISTRATION_AFTER_ITEM8_R2.md, and each constant carries the sentence it was
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

# "|J_B - J0| / J0 <= REPRO_TOL = 1.7162447e-04"  and the same for J_opt vs Jf
# (sec 3, D2-J).  RE-DERIVED, NOT INHERITED.  N-D48 measured the PATH-dependence of
# this solver class at 8.764756e-07 absolute in J at primalMinResTol = 1.0e-8; that
# calibrates dJ/d(residual) at C = 87.648.  BOTH ends of the comparison carry such a
# tail, so the mechanism bound is 2 x C x 1.0e-8 = 1.7529513e-06 absolute
# = 5.7208157e-05 relative to J0, and a stated safety factor of 3 covers N-D48's own
# caveat that its number is ONE measurement at ONE design point.
REPRO_TOL = 1.7162447e-04

# "|(d_shape + d_twist + d_trim) - (J_opt - J_B)| <= CLOSE_TOL = 8.423462e-15" (sec 3, D3)
# RE-DERIVED, NOT INHERITED, and STRICTLY TIGHTER than the 1.0e-12 it replaces -- a
# re-derivation that can only make a gate harder cannot be fitting.  Floor: 12
# floating-point operations x eps (2.220446049250313e-16) x the largest J on record
# for this case (0.0316132495761607) = 8.4234618e-17; the registered band is 100x it.
CLOSE_TOL = 8.423462e-15

# "D4 PASSES iff |I| <= INTERACT_TOL x |J_F - J_B| with INTERACT_TOL = 0.10"  (sec 3, D4)
INTERACT_TOL = 0.10

# "findFeasibleDesign gets at most TRIM_MAX_EVALS = 15 primal evaluations per state"
# (sec 3a).  RE-DERIVED, NOT INHERITED: arm DEC3 visited 5 distinct incidences per
# condition in a CONVERGING trim (state T, its own log), so 15 is 3x the measured
# need.  The 40 it replaces was never derived and, worse, was INERT -- see D1.
TRIM_MAX_EVALS = 15

# ---- THE WIDENED INCIDENCE BOUND (sec 1d).  DERIVED, NOT CHOSEN.
# "AOA_LOWER_DEG = -4.9570114 degrees" -- the midpoint of the largest incidence
# demand on the record (-4.5839298 deg, the worst root-finder iterate implied by the
# -3.64 deg figure carried in the supervisor's brief, using the MEASURED overshoot
# fraction 0.14366435) and the physical sanity limit (-5.3300930 deg, the shape-only
# wing's zero-lift incidence by the secant through two measured (AoA, CL) points).
# IT IS AN ANALYSIS BOUND AND IT NEVER TOUCHED THE OPTIMISATION: the frozen
# d6r2c_opt_runScript.py still carries lower=[U0, 0.0] at its line 280, its md5 is
# unchanged, and that md5 is asserted below.
AOA_LOWER_DEG = -4.9570114
# "AOA_UPPER_DEG = 10.0" -- INHERITED unchanged from the runscript's own upper bound.
AOA_UPPER_DEG = 10.0
# "AOA_STEP_MAX_DEG = 0.987284431" (sec 1f) -- the largest single incidence jump whose
# primal is MEASURED to have converged on this case (DEC3, cl06, 5.941267044 ->
# 6.928551475).  The jump that FAILED was 3.805494637 deg, 3.85x larger.
AOA_STEP_MAX_DEG = 0.987284431
# "CONT_MAX_STEPS = 12" (sec 1f) -- ceil( (5.941267044 - (-4.9570114)) / 0.987284431 ).
CONT_MAX_STEPS = 12

# ---- D2-GEO (sec 3).  NEW.  The geometric constraints are pyGeo outputs: they do
# not touch the flow solver, so they carry NONE of the convergence-tail
# path-dependence that forces REPRO_TOL wide.  Values are O(1) and ~10 operations
# deep, so the floating-point floor is ~2e-15; the registered band is 500x it.
GEO_TOL = 1.0e-12

# ===========================================================================
# D6R2C-AFTER8-R3 (DEC5) -- THE MESH RUNG.  NEW CONSTANTS, EACH CARRYING THE
# SENTENCE OF THE REGISTRATION IT WAS COPIED FROM.
# ===========================================================================
# "GROWTH_TARGET = 1.20 IS DECLARED, NOT MEASURED" (sec 1a step 2).  The upper
# edge of the 1.1-1.2 boundary-layer practice the finding note cites, hence the
# SMALLEST change that brings the mesh inside it.
GROWTH_TARGET = 1.20
# "N = 62 layers, 61 cells per chain" (sec 1a step 3), and 1008 wall faces
# (parent sec 9a), so 1008 x 61 cells.
MESH_N_LAYERS = 62
MESH_CELLS_PER_CHAIN = MESH_N_LAYERS - 1
MESH_WALL_FACES = 1008
MESH_CELLS_TOTAL = MESH_WALL_FACES * MESH_CELLS_PER_CHAIN
# "SANITY_BAND = 0.5 x 0.247323 = 0.123661365" (sec 3b.2), derived from two
# MEASURED anchors: the physics scale |J_T-J_B|/J_B = 0.031680 that it must
# clear, and the design scale |Jf-J0|/J0 = 0.247323 that is a LOWER BOUND on a
# scaler-class defect.  3.904x above the first, 2.000x below the second.  The
# factor 0.5 is DECLARED, NOT MEASURED.
SANITY_BAND = 0.123661365
# THE REGISTERED PLANT CANNOT TEST THE WIDENED LIMBS, AND THAT IS A FINDING, NOT
# A NUISANCE.  PLANT = 1.234e-03 into one condition's CD moves J by PLANT x its
# weight 0.50 = 6.170e-04 = 2.0136 % of J0.  SANITY_BAND is 12.3661 %.  So the
# registered plant is INVISIBLE to M3 -- a plant smaller than the band is not a
# test of the band, and rule 3 would have this grader refuse forever.
# The smallest CD perturbation that CAN flip M3 is SANITY_BAND x J0 / 0.50 =
# 7.578372e-03.  PLANT_SANITY = 10 x PLANT = 1.234e-02 is the smallest DECADE
# multiple above it and reaches 20.1360 % of J0.  The decade is DECLARED.
PLANT_SANITY = 1.234e-02
# the family script this item's mesh script must differ from in EXACTLY ONE line
FAMILY_GENWINGMESH_MD5 = "dab5e959187ab2e2bfb4e2c0ded0feb6"
# The frozen runscript that O_mp ran, asserted so that "the widened bound never
# touched O_mp" is a CHECK and not a sentence.
RUNSCRIPT_MD5 = "2f2ae43a627146cf8e0f065b035ada4b"

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
# "the final design vector is staged from O_mp/d6r2c_x0.json" (sec 4), pinned in
# the registration's section 0e.  IT IS NOW CHECKED.  In the first draft this
# constant was DECLARED AND NEVER READ -- a pin that pins nothing, found by the
# constant sweep of section 8a.  D6 now asserts the producer's recorded x0_md5
# against it, which is what a reader seeing this line would reasonably assume.
X0_MD5 = "b225fe7fdbd12eaa8a9b8a70835849c8"

# Section 8, the registered caps (3.00x), in core-minutes.
# ---- THE REGISTERED CAP, IN CORE-MINUTES, DERIVED IN CODE AND NOT TYPED TWICE.
#
# DEFECT FIND AT THE SUPERVISOR'S READ (registration sec 8a).  The first draft of
# this file carried `CAPS = {"DEC5": 407.303}` as a bare literal, taken from a
# SUPERSEDED cost model in which a continuation sub-step was costed per condition
# (16.027 s) rather than per evaluation (48.081 s -- run_model solves all three
# conditions at once).  The document moved to 138.973 / 416.919 and THIS LITERAL
# DID NOT.  Nothing compared the two, and this file's own cap controls read
# CAPS["DEC5"] to build their own boundary -- self-referential, and therefore
# blind to exactly this (L-588, applied to the instrument rather than the run).
#
# THE CAP IS NOW DERIVED FROM THE PREDICTION, SO THERE IS ONE NUMBER AND NOT TWO.
# D6R2C-AFTER8-R3 sec 6: "5410 s x 4 / 60 = 360.7 core-min", from DEC4's OWN
# measured 64.39 s per run_model call (state T, 965.8 s / 15 calls), rounded UP
# to 65 and scaled by the 1.6053x cell ratio to 104.3 s/call.
PREDICTION_CORE_MIN = 360.7
# "REGISTERED CAP, CAP_FACTOR = 3.00: 1082.1 core-min"  (sec 6)
CAP_FACTOR = 3.00
CAPS = {"DEC5": round(PREDICTION_CORE_MIN * CAP_FACTOR, 3)}

# The five registered decomposition states, IN THE REGISTERED ORDER.
# "the five decomposition states in one container, order B -> T -> S -> F -> O"  (sec 5)
STATES = ["B", "T", "S", "F", "O"]
# "J_opt is exempt by construction -- it is the un-trimmed control"  (sec 3, D1)
TRIMMED_STATES = ["B", "T", "S", "F"]
# "state B2 -- the baseline re-trimmed a SECOND time, from the O state's fields.
#  REPORTED, NEVER GATED" (sec 1e).  It must be PRESENT (D6 completion); its value
#  is a measurement of N-D48's path-dependence and gates nothing.
REPORTED_STATES = ["B2"]

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
    # D2-GEO's external anchor.  Read from the SAME md5-pinned artefact, NEVER
    # transcribed into this file: a 100-number transcription is a second copy that
    # can drift (L-221/L-222).  thickcon and volcon are pyGeo outputs -- pure
    # geometry, no flow solver, therefore NO convergence-tail path-dependence.
    for tag, rec in (("baseline", first), ("final", last)):
        for k in ("geometry_cl05.thickcon", "geometry_cl05.volcon"):
            if k not in rec.get("funcs", {}):
                raise Refusal("REFUSE_NO_GEO_ANCHOR %s missing from the inherited %s "
                              "record -- D2-GEO is this family's only floating-point "
                              "tight EXTERNAL anchor and it is not optional (L-588)"
                              % (k, tag))
            for v in rec["funcs"][k]:
                _finite(v, "inherited %s %s" % (tag, k))
    out["thickcon_baseline"] = [float(v) for v in first["funcs"]["geometry_cl05.thickcon"]]
    out["thickcon_final"] = [float(v) for v in last["funcs"]["geometry_cl05.thickcon"]]
    out["volcon_baseline"] = [float(v) for v in first["funcs"]["geometry_cl05.volcon"]]
    out["volcon_final"] = [float(v) for v in last["funcs"]["geometry_cl05.volcon"]]
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
    missing = [s for s in STATES + REPORTED_STATES if s not in states]
    if missing:
        raise Refusal("REFUSE_MISSING_STATES %r -- the registered order is %r"
                      % (missing, STATES + REPORTED_STATES))
    extra = [s for s in states if s not in STATES + REPORTED_STATES]
    if extra:
        raise Refusal("REFUSE_UNREGISTERED_STATE %r -- this document registers %r and "
                      "nothing else; which record is the measurement is not this "
                      "file's to choose" % (extra, STATES + REPORTED_STATES))
    return header, states, footer


def measure_growth_ratio(plot3d_path, _plant=None):
    """The wall-normal growth ratio of the generated mesh, from pyHyp's OWN
    structured output.

    WHY plot3d AND NOT polyMesh.  `volumeMesh.xyz` is pyHyp's structured
    multiblock output written BEFORE any OpenFOAM conversion, so the marching
    direction is an explicit index (the third) and no chain reconstruction is
    needed.  Reconstructing chains from an unstructured polyMesh is a second
    implementation of the same measurement and a second thing that can be wrong.

    CROSS-VALIDATED against the INDEPENDENT polyMesh-based measurement in
    FINDING_NOTE_D6R2C_LAYER_GROWTH.md, on FM5's mesh:
        this method (plot3d)   median 1.328558  mean 1.320146  max 1.619258
        the note  (polyMesh)   median 1.330314  mean 1.322246  max 1.618285
    -- 0.13 % apart on the median.  The pair COUNTS differ (44,955 here against
    the note's 37,296) because the 9 blocks share edges, so interface chains are
    sampled twice by the structured reader and once by the cell-based one.  That
    is a property of the two populations and is disclosed rather than reconciled.
    """
    import statistics
    tok = open(plot3d_path).read().split()
    p = 0
    nb = int(tok[p]); p += 1
    dims = []
    for _ in range(nb):
        dims.append(tuple(int(tok[p + i]) for i in range(3))); p += 3
    ratios, firsts, nk_seen = [], [], set()
    for (ni, nj, nk) in dims:
        nk_seen.add(nk)
        n = ni * nj * nk
        v = [float(x) for x in tok[p:p + 3 * n]]; p += 3 * n
        X, Y, Z = v[0:n], v[n:2 * n], v[2 * n:3 * n]
        def at(k, j, i):
            idx = k * nj * ni + j * ni + i
            return X[idx], Y[idx], Z[idx]
        for j in range(nj):
            for i in range(ni):
                th = []
                for k in range(nk - 1):
                    x0, y0, z0 = at(k, j, i); x1, y1, z1 = at(k + 1, j, i)
                    th.append(((x1-x0)**2 + (y1-y0)**2 + (z1-z0)**2) ** 0.5)
                firsts.append(th[0])
                ratios += [th[m + 1] / th[m] for m in range(len(th) - 1) if th[m] > 0.0]
    if _plant == "RATIO":
        ratios = [r + PLANT for r in ratios]
    med = statistics.median(ratios)
    return {"blocks": nb, "dims": [list(x) for x in dims],
            "marching_index_values": sorted(nk_seen),
            "pairs": len(ratios),
            "median": med, "mean": sum(ratios) / len(ratios),
            "max": max(ratios), "min": min(ratios),
            "first_cell_median": statistics.median(firsts),
            "frac_above_1p30": sum(1 for x in ratios if x > 1.30) / len(ratios),
            "frac_above_1p20": sum(1 for x in ratios if x > 1.20) / len(ratios),
            "GROWTH_TARGET": GROWTH_TARGET,
            "ok": med <= GROWTH_TARGET}


def grade_mesh(arm_dir, _plant=None):
    """M1 and M2 -- sec 3.  M1: the mesh is the mesh this document derived.
    M2: the one-change proof, taken as a diff and not as a sentence."""
    m1 = {"reasons": []}
    p3d = os.path.join(arm_dir, "volumeMesh.xyz")
    if not os.path.isfile(p3d):
        m1.update({"ok": False}); m1["reasons"].append("no volumeMesh.xyz")
    else:
        g = measure_growth_ratio(p3d, _plant="RATIO" if _plant == "M1RATIO" else None)
        m1["growth"] = g
        nk = g["marching_index_values"]
        layers_ok = (nk == [MESH_N_LAYERS])
        if not layers_ok:
            m1["reasons"].append("marching index %r, registered %d" % (nk, MESH_N_LAYERS))
        ratio_ok = g["ok"]
        if not ratio_ok:
            m1["reasons"].append("median ratio %.6f > GROWTH_TARGET %.4f" % (g["median"], GROWTH_TARGET))
        m1["layers_ok"] = layers_ok
        m1["ratio_ok"] = ratio_ok
        m1["ok"] = bool(layers_ok and ratio_ok)
    # ---- M2: the diff against the family script, and the mesh step's rc
    m2 = {"reasons": []}
    rcp = os.path.join(arm_dir, "mesh_rc.txt")
    try:
        m2["mesh_rc"] = int(open(rcp).read().strip())
    except Exception:
        m2["mesh_rc"] = None; m2["reasons"].append("no mesh_rc.txt")
    dp = os.path.join(arm_dir, "genwingmesh_diff.txt")
    try:
        dl = [l for l in open(dp).read().splitlines() if l[:1] in ("<", ">")]
    except Exception:
        dl = None; m2["reasons"].append("no genwingmesh_diff.txt")
    m2["changed_lines"] = None if dl is None else len(dl)
    m2["diff"] = dl
    one_line = (dl is not None and len(dl) == 2
                and all('"N":' in l for l in dl))
    if dl is not None and not one_line:
        m2["reasons"].append("diff is not exactly one changed N line: %r" % dl)
    if _plant == "M2DIFF":
        one_line = False; m2["reasons"].append("PLANTED two-line diff")
    m2["one_changed_N_line"] = one_line
    m2["ok"] = bool(one_line and m2["mesh_rc"] == 0)
    return m1, m2


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
            # PLANT_SANITY, not PLANT: the CD plant is the one that has to be
            # seen by M3, whose band is SANITY_BAND.  See the PLANT_SANITY
            # derivation at the head of this file.  The CL and GEO plants keep
            # PLANT, because TRIM_TOL = 1.0e-6 and GEO_TOL = 1.0e-12 see it by
            # three and nine decades respectively.
            row["CD"][_plant[2]] = row["CD"][_plant[2]] + PLANT_SANITY
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
        # A NULL COUNT IS NOW A FAILURE, NOT A PASS.  Measured in arm DEC3: every
        # state recorded n_trim_evals = null, so `isinstance(n, int)` was False and
        # TRIM_MAX_EVALS never fired.  A cap that cannot be read is not a cap.
        if not isinstance(n, int):
            d1_detail[s]["ok"] = False
            d1_detail[s]["why"] = ("n_trim_evals = %r is not an integer -- the cap "
                                   "TRIM_MAX_EVALS = %d is unreadable and therefore "
                                   "inert; the state is NOT A RESULT (sec 3a)"
                                   % (n, TRIM_MAX_EVALS))
        elif n > TRIM_MAX_EVALS:
            d1_detail[s]["ok"] = False
            d1_detail[s]["why"] = ("TRIM_MAX_EVALS = %d exceeded (%d) -- section 3a: "
                                   "the state is NOT A RESULT and TRIM_TOL is never "
                                   "widened" % (TRIM_MAX_EVALS, n))
    # ---- the registered incidence bound, checked on EVERY state including the
    # ---- reported-only one, and on every incidence the producer says it VISITED.
    aoa_detail = {}
    for s in STATES + REPORTED_STATES:
        r = states[s]
        vis = r.get("aoa_visited_deg") or {}
        rows = {}
        for p in POINTS:
            seq = [float(v) for v in vis.get(p, [])] if isinstance(vis, dict) else []
            final = table[s]["AoA_deg"][p] if s in table else float(
                _req(r, "AoA_deg", "state %s" % s)[p])
            allv = seq + [final]
            steps = [abs(allv[i + 1] - allv[i]) for i in range(len(allv) - 1)]
            rows[p] = {
                "n_visited": len(seq),
                "final_deg": final,
                "min_deg": min(allv), "max_deg": max(allv),
                "inside_bound": all(AOA_LOWER_DEG <= v <= AOA_UPPER_DEG for v in allv),
                "max_step_deg": (max(steps) if steps else 0.0),
                "step_ok": all(st <= AOA_STEP_MAX_DEG * (1.0 + 1.0e-9) for st in steps),
                "n_steps_ok": len(steps) <= CONT_MAX_STEPS + TRIM_MAX_EVALS,
            }
        aoa_detail[s] = rows
    aoa_ok = all(v["inside_bound"] and v["step_ok"] and v["n_steps_ok"]
                 for rows in aoa_detail.values() for v in rows.values())
    aoa_recorded = all(rows[p]["n_visited"] > 0
                       for s2, rows in aoa_detail.items() for p in POINTS
                       if s2 in TRIMMED_STATES + REPORTED_STATES)
    D1 = all(v["ok"] for v in d1_detail.values()) and aoa_ok and aoa_recorded

    # ---- D2 -- the instrument reproduces the run it is decomposing, BOTH ENDS
    J0, Jf = inherited["J0"], inherited["Jf"]
    rel_B = abs(JB - J0) / abs(J0)
    rel_O = abs(JO - Jf) / abs(Jf)
    cl_O = {p: abs(table["O"]["CL"][p] - inherited["CL_final"][p]) for p in POINTS}
    # ---- D2-GEO: thickcon and volcon at the two ANCHORED states, against the
    # ---- md5-pinned O_mp record.  These are pyGeo outputs -- they never touch the
    # ---- flow solver, so they carry none of the convergence-tail path-dependence
    # ---- that forces REPRO_TOL wide, and they see the INPUT fault class that D2-J
    # ---- at 1.7e-04 cannot (L-588, and PREREGISTRATION_AFTER_ITEMS ADDENDUM 2).
    geo_detail = {}
    for s, tag in (("B", "baseline"), ("F", "final"), ("O", "final")):
        r = states[s]
        got_t = r.get("thickcon")
        got_v = r.get("volcon")
        if not isinstance(got_t, list) or not isinstance(got_v, list):
            raise Refusal("REFUSE_NO_GEO_IN_STATE state %s carries thickcon=%r volcon=%r "
                          "-- D2-GEO is the only floating-point tight external anchor "
                          "in this family and the producer must record it (sec 3, D2-GEO)"
                          % (s, type(got_t).__name__, type(got_v).__name__))
        want_t = inherited["thickcon_" + tag]
        want_v = inherited["volcon_" + tag]
        if len(got_t) != len(want_t) or len(got_v) != len(want_v):
            raise Refusal("REFUSE_GEO_LENGTH state %s: thickcon %d vs %d, volcon %d vs %d"
                          % (s, len(got_t), len(want_t), len(got_v), len(want_v)))
        gt = [float(x) for x in got_t]
        gv = [float(x) for x in got_v]
        if _plant and _plant[0] == "GEO" and _plant[1] == s:
            gt = list(gt)
            gt[0] = gt[0] + PLANT
        dt = [abs(a - b) for a, b in zip(gt, want_t)]
        dv = [abs(a - b) for a, b in zip(gv, want_v)]
        worst = max(dt + dv)
        geo_detail[s] = {"anchor_record": tag, "worst_abs_diff": worst,
                         "worst_thickcon_diff": max(dt), "worst_volcon_diff": max(dv),
                         "GEO_TOL": GEO_TOL, "ok": worst <= GEO_TOL}
    D2GEO = all(v["ok"] for v in geo_detail.values())

    d2_detail = {
        "J_B": JB, "J0": J0, "rel_B": rel_B, "rel_B_ok": rel_B <= SANITY_BAND,
        "J_opt": JO, "Jf": Jf, "rel_O": rel_O, "rel_O_ok": rel_O <= SANITY_BAND,
        "B_max_CL_miss": table["B"]["max_CL_miss"],
        "B_CL_ok": table["B"]["max_CL_miss"] <= TRIM_TOL,
        "O_CL_vs_inherited": cl_O,
        "O_CL_ok": max(cl_O.values()) <= TRIM_TOL,
        "SANITY_BAND": SANITY_BAND, "TRIM_TOL": TRIM_TOL,
        "REPRO_TOL_STRUCK": REPRO_TOL,
        "D2GEO": D2GEO, "D2GEO_detail": geo_detail,
        "fault_classes_seen": {
            "D2-J": "GROSS state faults only.  REPRO_TOL = %.6e relative is %.3e "
                    "absolute in J = %.4f drag counts; anything smaller is INVISIBLE "
                    "to this clause and that is a property of the solver's stopping "
                    "rule, not of the gate (N-D48)." % (
                        REPRO_TOL, REPRO_TOL * abs(J0), REPRO_TOL * abs(J0) * 1.0e4),
            "D2-GEO": "INPUT faults -- a wrong design vector, a wrong space, a wrong "
                      "scaler, a wrong source record, a wrong FFD.  Anchored to an "
                      "md5-pinned artefact this run did not produce, at 1.0e-12 on "
                      "quantities the flow solver never touches.  BLIND to every "
                      "flow-solver fault.",
            "D2-CL": "trim faults at state O, against the inherited CL vector.",
            "NOT ANCHORED": "states T and S carry NO external geometric anchor -- no "
                            "record of a twist-only or shape-only geometry exists. "
                            "The unseen fault class is a DV-installation fault that "
                            "corrupts ONLY the twist-only or shape-only vector while "
                            "leaving the full vector correct.  Disclosed, not repaired.",
        },
    }
    # ---- sec 3a.1: D2 does NOT survive whole, and it is NOT struck whole.
    # D2GEO reads thickcon/volcon, which are pyGeo outputs (see the comment at
    # the head of load_inherited): the CFD volume mesh is NOT an input to them,
    # so changing N from 39 to 62 CANNOT move them.  It is carried forward at
    # FULL tightness, GEO_TOL = 1.0e-12, and it is the sharpest scaler-class
    # detector here: thickcon/volcon are normalised to ~1.0, so a `shape`
    # installed 10x too large moves them by order 100 % -- TWELVE DECADES
    # outside GEO_TOL.
    #
    # The four CFD-output limbs (two J, two CL) are mesh-dependent BY
    # CONSTRUCTION on this arm and cannot be gated at REPRO_TOL.  The two J
    # limbs are re-banded to SANITY_BAND as M3 (sec 3b); the two CL limbs are
    # REPORTED, NEVER GATED, because the inherited CLs are CFD outputs of the
    # N=39 mesh and this arm changes the mesh.
    M3 = (d2_detail["rel_B_ok"] and d2_detail["rel_O_ok"])
    d2_detail["M3"] = M3
    d2_detail["CL_limbs_reported_not_gated"] = {
        "B_max_CL_miss": d2_detail["B_max_CL_miss"],
        "O_CL_vs_inherited": d2_detail["O_CL_vs_inherited"],
        "why": "the inherited CLs are CFD outputs of the N=39 mesh; this arm "
               "changes the mesh, so they are reported and not gated."}
    D2 = D2GEO

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
    for s in STATES + REPORTED_STATES:
        pc = _req(states[s], "primal_converged", "state %s" % s)
        conv[s] = {p: bool(pc.get(p)) for p in POINTS}
    all_conv = all(all(v.values()) for v in conv.values())
    art = {name: newer_than_datum(os.path.join(arm_dir, name), datum_epoch)
           for name in ["d6r2c_dec5.jsonl"]}
    # "the widened bound never touched O_mp" is a CHECK, not a sentence: the
    # runscript the producer loaded must still be the bytes O_mp ran.
    rs_md5 = header.get("runscript_md5")
    rs_ok = (rs_md5 == RUNSCRIPT_MD5)
    # the two staged INPUTS, pinned.  Both are recorded by the producer in its
    # HEADER and neither was checked by anything in the first draft.
    x0_md5 = header.get("x0_md5")
    ev_md5 = header.get("evals_md5")
    inputs_ok = (x0_md5 == X0_MD5) and (ev_md5 == EVALS_MD5)
    cap = CAPS["DEC5"]
    cap_crossed = (core_min is not None) and (core_min > cap)   # strict >, as the parent's ledger uses
    d6_detail = {"rc": rc, "rc_is_zero": rc == 0,
                 "ownership": own, "artefacts": art,
                 "primal_converged": conv, "all_primals_converged": all_conv,
                 "footer_present": footer is not None,
                 "core_min": core_min, "cap_core_min": cap, "cap_crossed": cap_crossed,
                 "runscript_md5_recorded": rs_md5, "runscript_md5_registered": RUNSCRIPT_MD5,
                 "runscript_unchanged": rs_ok,
                 "x0_md5_recorded": x0_md5, "x0_md5_registered": X0_MD5,
                 "evals_md5_recorded": ev_md5, "evals_md5_registered": EVALS_MD5,
                 "staged_inputs_are_the_registered_inputs": inputs_ok,
                 "runscript_note":
                     "The registered incidence bound is an ANALYSIS bound.  The frozen "
                     "optimisation runscript is unedited and still carries "
                     "lower=[U0, 0.0] at its line 280; O_mp's GATE FAIL, its 24.732 % "
                     "and its Jf/J0 = 0.752677 stand exactly as graded, and a reader "
                     "is entitled to check that by this md5."}
    D6 = (rc == 0 and own["ok"] and all_conv and rs_ok and inputs_ok
          and all(a["newer_than_datum"] for a in art.values()))

    # ---- M1 and M2: the mesh rung's own gates (sec 3)
    M1_detail, M2_detail = grade_mesh(arm_dir,
                                      _plant=(_plant[0] if _plant and _plant[0] in ("M1RATIO", "M2DIFF") else None))
    M1 = bool(M1_detail.get("ok"))
    M2 = bool(M2_detail.get("ok"))

    # ---- the label
    if not (M1 and M2 and D1 and D2 and M3 and D3 and D6) or cap_crossed:
        label = LABEL_NOT_A_RESULT
    elif not D4:
        label = LABEL_GATE_FAIL
    else:
        label = LABEL_PASS

    # ---- state B2: REPORTED, NEVER GATED (sec 1e).  The baseline re-trimmed a
    # ---- SECOND time, from the O state's fields.  |J_B2 - J_B| is a DIRECT
    # ---- measurement of the path-dependence N-D48 says is uncharacterised, and it
    # ---- is the reason this arm carries a sixth state at all.
    rB2 = states["B2"]
    cdB2 = {p: _finite(_req(rB2, "CD", "state B2").get(p), "B2 CD %s" % p) for p in POINTS}
    clB2 = {p: _finite(_req(rB2, "CL", "state B2").get(p), "B2 CL %s" % p) for p in POINTS}
    JB2 = _weighted_J(cdB2)
    b2_reported = {
        "J_B2": JB2, "J_B": JB, "J0_inherited": J0,
        "abs_J_B2_minus_J_B": abs(JB2 - JB),
        "rel_J_B2_minus_J_B": abs(JB2 - JB) / abs(JB),
        "abs_J_B2_minus_J0": abs(JB2 - J0),
        "rel_J_B2_minus_J0": abs(JB2 - J0) / abs(J0),
        "CD": cdB2, "CL": clB2,
        "max_CL_miss": max(abs(clB2[p] - CL_TARGETS[p]) for p in POINTS),
        "AoA_deg": _req(rB2, "AoA_deg", "state B2"),
        "note": "REPORTED, NEVER GATED (sec 1e).  N-D48 records ONE path-dependence "
                "measurement at ONE design point and says so; this is a second, and "
                "registering a gate on a quantity with one prior measurement is what "
                "N-D48 forbids.  No label depends on any number in this block.",
    }

    rec = {
        "item": "8R2", "arm": "DEC5", "label": label,
        "M1": M1, "M2": M2, "M3": M3,
        "M1_detail": M1_detail, "M2_detail": M2_detail,
        "D1": D1, "D2": D2, "D3": D3, "D4": D4, "D6": D6,
        "D2GEO": D2GEO,
        "D1_detail": d1_detail, "D1_aoa_detail": aoa_detail,
        "D1_aoa_bound": {"AOA_LOWER_DEG": AOA_LOWER_DEG, "AOA_UPPER_DEG": AOA_UPPER_DEG,
                         "AOA_STEP_MAX_DEG": AOA_STEP_MAX_DEG,
                         "CONT_MAX_STEPS": CONT_MAX_STEPS,
                         "all_inside_bound": aoa_ok,
                         "every_trimmed_state_recorded_its_path": aoa_recorded},
        "B2_reported_never_gated": b2_reported,
        "D2_detail": d2_detail,
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
# THE LIVE PLANTED CONTROL (rule 3) -- runs on EVERY real grading
# ---------------------------------------------------------------------------

def live_plant_check(item, grade_fn_kwargs, verdict_label):
    """Re-grade deep copies of the same inputs with PLANT injected.  REFUSE if any
    plant leaves the verdict at PASS.

    Section 7: "A comparator that cannot see a disagreement of that size in these
    artefacts cannot certify an agreement, and its zero is not evidence." """
    plants = [("CD", "B", "cl05"), ("CD", "T", "cl05"), ("CD", "F", "cl05"),
              ("CD", "O", "cl05"), ("CL", "F", "cl05"),
              ("GEO", "B"), ("GEO", "F"), ("GEO", "O")]
    fn = grade_item8
    if item != "8R2":
        raise Refusal("REFUSE_UNREGISTERED_ITEM %r -- this file grades 8R2 and nothing "
                      "else" % (item,))
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
                "is %.1fx the LOOSEST band this grader applies (REPRO_TOL = %.6e relative "
                "= %.6e absolute in J) and many decades above the others (GEO_TOL = %.1e, "
                "CLOSE_TOL = %.6e); a reader that cannot see it cannot certify an "
                "agreement (rule 3)."
                % (pl, PLANT, PLANT / (REPRO_TOL * J0_INHERITED), REPRO_TOL,
                   REPRO_TOL * J0_INHERITED, GEO_TOL, CLOSE_TOL))
    return {"PLANT": PLANT, "verdict_without_plant": verdict_label, "controls": results,
            "all_plants_visible": True}


# ---------------------------------------------------------------------------
# THE MARKDOWN TABLE -- the absolute numbers, before any percentage
# ---------------------------------------------------------------------------

NAMES = {"B": "baseline (trimmed)", "T": "twist-only (re-trimmed)",
         "S": "shape-only (re-trimmed)", "F": "full optimum (re-trimmed)",
         "O": "optimiser final state (NOT matched lift)",
         "B2": "baseline re-trimmed a SECOND time (REPORTED, NEVER GATED)"}


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
    b2 = rec["B2_reported_never_gated"]
    L += ["", "## State `B2` -- REPORTED, NEVER GATED", "",
          "The baseline re-trimmed a second time, from the `O` state's fields.  It measures",
          "the PATH-dependence N-D48 records as uncharacterised, and it gates nothing.", "",
          "| quantity | value |", "|---|---|",
          "| `J_B2` | %.17g |" % b2["J_B2"],
          "| `J_B` | %.17g |" % b2["J_B"],
          "| `|J_B2 - J_B|` | %.6e absolute, %.6e relative |" % (
              b2["abs_J_B2_minus_J_B"], b2["rel_J_B2_minus_J_B"]),
          "| `|J_B2 - J0|` | %.6e absolute, %.6e relative |" % (
              b2["abs_J_B2_minus_J0"], b2["rel_J_B2_minus_J0"]),
          ""]
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
            "CL_miss_final": {"cl04": 5.539e-4, "cl05": 1.2099e-3, "cl06": 2.787e-3},
            # D2-GEO's external anchor, in the synthetic shape the real one has:
            # 100 thickness constraints and 1 volume constraint per record.
            "thickcon_baseline": [1.0] * 100, "volcon_baseline": [1.0],
            "thickcon_final": [0.5 + 0.008 * i for i in range(100)], "volcon_final": [1.0019113618945679]}


def _cd_for(J):
    """A CD triple whose FROZEN weighted mean is exactly J (flat triple)."""
    return {p: J for p in POINTS}


def _aoa_path(final):
    """A legal incidence path: inside the bound, every step <= AOA_STEP_MAX_DEG."""
    return {p: [final[p]] for p in POINTS}


def _synth_decomp(tmp, JB, JT, JS, JF, JO, cl_miss=0.0, fail=0,
                  n_trim=6, converged=True, o_cl=None, JB2=None,
                  aoa=None, geo_state=None, geo_delta=0.0, drop_geo=False,
                  runscript_md5=RUNSCRIPT_MD5, x0_md5=X0_MD5,
                  mesh_ratio=1.15, mesh_layers=MESH_N_LAYERS,
                  mesh_rc=0, diff_changed_lines=1, mesh=True):
    d = os.path.join(tmp, "DEC5")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "d6r2c_dec5.jsonl")
    inh = _synth_inherited()
    rows = [{"kind": "HEADER", "ranks": 4, "points": POINTS,
             "cl_targets": CL_TARGETS, "weights": WEIGHTS, "evals_md5": EVALS_MD5,
             "runscript_md5": runscript_md5, "x0_md5": x0_md5,
             "AOA_LOWER_DEG": AOA_LOWER_DEG, "AOA_UPPER_DEG": AOA_UPPER_DEG,
             "AOA_STEP_MAX_DEG": AOA_STEP_MAX_DEG, "CONT_MAX_STEPS": CONT_MAX_STEPS,
             "TRIM_MAX_EVALS": TRIM_MAX_EVALS}]
    Js = {"B": JB, "T": JT, "S": JS, "F": JF, "O": JO,
          "B2": (JB if JB2 is None else JB2)}
    ANCHOR = {"B": "baseline", "F": "final", "O": "final", "B2": "baseline"}
    default_aoa = {"cl04": 1.0, "cl05": 2.0, "cl06": 3.0}
    for st in STATES + REPORTED_STATES:
        J = Js[st]
        cd = _cd_for(J)
        if st == "O":
            cl = dict(o_cl) if o_cl else dict(inh["CL_final"])
        else:
            cl = {p: CL_TARGETS[p] + cl_miss for p in POINTS}
        a = dict(aoa) if aoa else dict(default_aoa)
        row = {"kind": "STATE", "state": st, "fail": fail,
               "trimmed": st != "O", "n_trim_evals": (None if st == "O" else n_trim),
               "CD": cd, "CL": cl,
               "AoA_deg": a, "aoa_visited_deg": _aoa_path(a),
               "J": _weighted_J(cd),
               "claimed_cl_miss": {p: abs(cl[p] - CL_TARGETS[p]) for p in POINTS},
               "primal_converged": {p: converged for p in POINTS},
               "primal_final_res": {p: 1e-9 for p in POINTS}}
        if st in ANCHOR and not drop_geo:
            tag = ANCHOR[st]
            tc = list(inh["thickcon_" + tag])
            vc = list(inh["volcon_" + tag])
            if geo_state == st:
                tc[0] = tc[0] + geo_delta
            row["thickcon"] = tc
            row["volcon"] = vc
        rows.append(row)
    rows.append({"kind": "FOOTER", "rc": 0})
    with open(path, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    os.utime(path, (2_000_000_000, 2_000_000_000))
    if mesh:
        # a synthetic pyHyp plot3d: ONE block, marching index `mesh_layers`,
        # geometric spacing at `mesh_ratio`.  The VALUES ARE WRITTEN BY THE TEST,
        # not read from the instrument's constants -- sec 8c.
        ni = nj = 2
        s0 = 1.0e-3
        zs = [0.0]
        t = s0
        for _ in range(mesh_layers - 1):
            zs.append(zs[-1] + t); t *= mesh_ratio
        X, Y, Z = [], [], []
        for k in range(mesh_layers):
            for j in range(nj):
                for i in range(ni):
                    X.append(float(i)); Y.append(float(j)); Z.append(zs[k])
        with open(os.path.join(d, "volumeMesh.xyz"), "w") as fh:
            fh.write("1\n%d %d %d\n" % (ni, nj, mesh_layers))
            for arr in (X, Y, Z):
                fh.write(" ".join("%.17g" % v for v in arr) + "\n")
        with open(os.path.join(d, "mesh_rc.txt"), "w") as fh:
            fh.write("%d\n" % mesh_rc)
        with open(os.path.join(d, "genwingmesh_diff.txt"), "w") as fh:
            fh.write("24c24\n")
            fh.write('<     "N": 39,  # number of layers to march\n')
            fh.write("---\n")
            fh.write('>     "N": %d,  # number of layers to march\n' % mesh_layers)
            if diff_changed_lines > 1:
                fh.write('<     "s0": 1.0e-3,\n---\n>     "s0": 2.0e-3,\n')
    return path, d


def selftest():
    DATUM = 1_000_000_000
    inh = _synth_inherited()
    J0, Jf = inh["J0"], inh["Jf"]
    CAP = CAPS["DEC5"]
    controls = []

    def check(name, got, want):
        controls.append((name, got, want))
        if got != want:
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r" % (name, got, want))
            return False
        return True

    ok = True
    tmp = tempfile.mkdtemp(prefix="d6r2c_dec4_selftest_")
    try:
        # --- a clean, internally consistent decomposition ---------------------
        JB, JO = J0, Jf
        JT = JB - 0.002
        JS = JB - 0.004
        JF = JB - 0.006          # additive: JF - JT = JS - JB = -0.004 -> I = 0
        p, d = _synth_decomp(tmp, JB, JT, JS, JF, JO)
        kw = dict(jsonl_path=p, arm_dir=d, datum_epoch=DATUM, inherited=inh,
                  core_min=300.0, rc=0)
        r = grade_item8(**kw)
        ok &= check("clean additive case -> PASS", r["label"], LABEL_PASS)
        ok &= check("clean case D3 closure <= CLOSE_TOL", r["D3"], True)
        ok &= check("clean case D2GEO holds", r["D2GEO"], True)
        ok &= check("clean case I == 0",
                    abs(r["contributions_absolute"]["interaction_I"]) < 1e-15, True)
        ok &= check("percentages present on PASS", "percentages" in r, True)
        ok &= check("share denominator named", "share_denominator" in r["percentages"], True)
        ok &= check("B2 is reported", "B2_reported_never_gated" in r, True)
        lp = live_plant_check("8R2", kw, r["label"])
        ok &= check("all 8 live plants visible", lp["all_plants_visible"], True)
        ok &= check("live plant list length", len(lp["controls"]), 8)

        # --- NEGATIVE CONTROL: an untouched re-grade reproduces the label ------
        ok &= check("NEGATIVE control, re-grade reproduces label",
                    grade_item8(**kw)["label"], r["label"])

        # --- B2 IS REPORTED AND NEVER GATED: move it hard, the label must not move
        p, d = _synth_decomp(tmp + "/b2", JB, JT, JS, JF, JO, JB2=JB * (1 + 1.0e-2))
        r2 = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("B2 off by 1e-2 relative does NOT change the label",
                    r2["label"], LABEL_PASS)
        ok &= check("B2 off by 1e-2 IS reported",
                    abs(r2["B2_reported_never_gated"]["rel_J_B2_minus_J_B"] - 1.0e-2) < 1e-9,
                    True)
        # ... and its ABSENCE is a refusal (it is part of the registered sequence)
        rows = [json.loads(x) for x in open(p).read().splitlines()]
        rows = [x for x in rows if x.get("state") != "B2"]
        with open(p, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
        try:
            grade_item8(p, d, DATUM, inh, 300.0, 0)
            ok &= check("missing B2 -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("missing B2 -> REFUSE_MISSING_STATES",
                        str(e).startswith("REFUSE_MISSING_STATES"), True)

        # --- D1: an arm off matched lift --------------------------------------
        p, d = _synth_decomp(tmp + "/a", JB, JT, JS, JF, JO, cl_miss=1.0e-5)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("D1 miss 1e-5 > TRIM_TOL -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        ok &= check("D1 false", r["D1"], False)
        ok &= check("no percentages when NOT A RESULT", "percentages" in r, False)

        # BOUNDARY, BOTH SIDES, ONE ULP APART.  The TRIM_TOL edge is not
        # representable (PREREGISTRATION_AFTER_ITEMS sec 3c): no IEEE double v has
        # |v - target| == 1.0e-6 exactly, and the straddle differs PER TARGET.  The
        # boundary is driven from the ATTAINABLE values.  NO TOLERANCE WAS ADDED TO
        # D1 TO MAKE THE EDGE REACHABLE.
        def _straddle(target, tol):
            v = target + tol
            while abs(v - target) > tol:
                v = math.nextafter(v, target)
            below = v
            above = math.nextafter(v, 1.0)
            assert abs(below - target) <= tol < abs(above - target)
            return abs(below - target), abs(above - target)
        lo, hi = _straddle(CL_TARGETS["cl06"], TRIM_TOL)
        p, d = _synth_decomp(tmp + "/b", JB, JT, JS, JF, JO, cl_miss=lo)
        ok &= check("D1 boundary, largest ATTAINABLE miss <= TRIM_TOL -> D1 holds",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["D1"], True)
        p, d = _synth_decomp(tmp + "/c", JB, JT, JS, JF, JO, cl_miss=hi)
        ok &= check("D1 boundary, ONE ULP ABOVE that -> D1 fails",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["D1"], False)

        # --- D1, NEW: a null trim-eval count is a FAILURE, not a pass ----------
        # Measured in arm DEC3: every state recorded n_trim_evals = null and the
        # registered cap was therefore INERT.  A cap that cannot be read is not a cap.
        p, d = _synth_decomp(tmp + "/n1", JB, JT, JS, JF, JO, n_trim=None)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("null n_trim_evals -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        ok &= check("null n_trim_evals names the inert cap",
                    "inert" in r["D1_detail"]["B"]["why"], True)
        p, d = _synth_decomp(tmp + "/n2", JB, JT, JS, JF, JO, n_trim=TRIM_MAX_EVALS)
        ok &= check("n_trim AT the cap is NOT over it",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_PASS)
        p, d = _synth_decomp(tmp + "/n3", JB, JT, JS, JF, JO, n_trim=TRIM_MAX_EVALS + 1)
        ok &= check("n_trim ONE over the cap -> NOT A RESULT",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_NOT_A_RESULT)

        # --- D1, NEW: the registered incidence bound --------------------------
        p, d = _synth_decomp(tmp + "/aoa1", JB, JT, JS, JF, JO,
                             aoa={"cl04": AOA_LOWER_DEG, "cl05": 2.0, "cl06": 3.0})
        ok &= check("an incidence AT the lower bound is INSIDE it",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_PASS)
        p, d = _synth_decomp(tmp + "/aoa2", JB, JT, JS, JF, JO,
                             aoa={"cl04": math.nextafter(AOA_LOWER_DEG, -10.0),
                                  "cl05": 2.0, "cl06": 3.0})
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("ONE ULP below the lower bound -> NOT A RESULT",
                    r["label"], LABEL_NOT_A_RESULT)
        ok &= check("the bound failure is named in the AoA block",
                    r["D1_aoa_bound"]["all_inside_bound"], False)
        p, d = _synth_decomp(tmp + "/aoa3", JB, JT, JS, JF, JO,
                             aoa={"cl04": AOA_UPPER_DEG + 1.0e-9, "cl05": 2.0, "cl06": 3.0})
        ok &= check("above the UPPER bound -> NOT A RESULT",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_NOT_A_RESULT)
        # a continuation step LARGER than the measured-converging maximum
        p, d = _synth_decomp(tmp + "/aoa4", JB, JT, JS, JF, JO)
        rows = [json.loads(x) for x in open(p).read().splitlines()]
        for row in rows:
            if row.get("state") == "S":
                row["aoa_visited_deg"]["cl04"] = [3.0, 3.0 - AOA_STEP_MAX_DEG * 1.001, 1.0]
        with open(p, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
        os.utime(p, (2_000_000_000, 2_000_000_000))
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("a continuation step ABOVE the measured maximum -> NOT A RESULT",
                    r["label"], LABEL_NOT_A_RESULT)
        ok &= check("the oversized step is named",
                    r["D1_aoa_detail"]["S"]["cl04"]["step_ok"], False)
        # NEGATIVE: a legal multi-step path must NOT fail
        p, d = _synth_decomp(tmp + "/aoa5", JB, JT, JS, JF, JO)
        rows = [json.loads(x) for x in open(p).read().splitlines()]
        for row in rows:
            if row.get("state") == "S":
                row["aoa_visited_deg"]["cl04"] = [3.0, 3.0 - AOA_STEP_MAX_DEG * 0.999,
                                                 3.0 - AOA_STEP_MAX_DEG * 1.5, 1.0]
        with open(p, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
        os.utime(p, (2_000_000_000, 2_000_000_000))
        ok &= check("NEGATIVE -- a legal multi-step continuation does NOT fail",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_PASS)
        # a state that recorded no path at all
        p, d = _synth_decomp(tmp + "/aoa6", JB, JT, JS, JF, JO)
        rows = [json.loads(x) for x in open(p).read().splitlines()]
        for row in rows:
            if row.get("state") == "S":
                row["aoa_visited_deg"] = {}
        with open(p, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
        os.utime(p, (2_000_000_000, 2_000_000_000))
        ok &= check("a trimmed state that recorded NO incidence path -> NOT A RESULT",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_NOT_A_RESULT)

        # --- D2-J: the reproduction control at each end, at the RE-DERIVED band
        # REPRO_TOL = 1.7162447e-04.  N-D48's measured path-dependence is
        # 2.860408e-05 relative -- 6.0x INSIDE the band, which is the whole reason
        # the band was re-derived.  Both sides are driven.
        p, d = _synth_decomp(tmp + "/d0", JB * (1 + 2.860408e-05), JT, JS, JF, JO)
        ok &= check("NEGATIVE -- the MEASURED path-dependence 2.86e-05 is INSIDE the "
                    "re-derived band", grade_item8(p, d, DATUM, inh, 300.0, 0)["D2"], True)
        p, d = _synth_decomp(tmp + "/d", JB * (1 + 2.0e-4), JT, JS, JF, JO)
        # ---- M3: BOTH SIDES OF SANITY_BAND ARE DRIVEN, not just the failing one.
        # The old controls perturbed by 2.0e-4, calibrated to the STRUCK
        # REPRO_TOL; against SANITY_BAND = 0.123661365 that is deep inside the
        # band and tests nothing.  The literals below are typed by the TEST.
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("M3: J_B off by 2e-4 is INSIDE the sanity band -> still PASS",
                    r["label"], LABEL_PASS)
        ok &= check("M3: and D2GEO is untouched by a J drift", r["D2"], True)
        # OUTSIDE the band: 0.13 > 0.123661365
        p, d = _synth_decomp(tmp + "/d2", JB * (1 + 0.13), JT, JS, JF, JO)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("M3: J_B off by 0.13 -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        ok &= check("M3 false (J_B end)", r["M3"], False)
        ok &= check("and D2GEO still holds -- the limbs are independent", r["D2"], True)
        # INSIDE the band, one step under: 0.11 < 0.123661365
        p, d = _synth_decomp(tmp + "/d3", JB * (1 + 0.11), JT, JS, JF, JO)
        ok &= check("M3: J_B off by 0.11 is inside -> not NOT A RESULT on M3",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["M3"], True)
        # the J_opt end -- the end a scaler-class defect cannot hide from
        p, d = _synth_decomp(tmp + "/e", JB, JT, JS, JF, JO * (1 + 0.13))
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("M3: J_opt off by 0.13 -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        ok &= check("M3 false (J_opt end)", r["M3"], False)
        p, d = _synth_decomp(tmp + "/f", JB, JT, JS, JF, JO,
                             o_cl={p2: inh["CL_final"][p2] + 1e-5 for p2 in POINTS})
        # sec 3a.1: the inherited CLs are CFD outputs of the N=39 mesh and this
        # arm changes the mesh, so the CL limbs are REPORTED, NEVER GATED.  The
        # control therefore asserts the OPPOSITE of DEC4's: the label must NOT
        # move, and the drift must still appear in the record.
        _rcl = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("CL limbs are REPORTED, not gated: label does not move",
                    _rcl["label"], LABEL_PASS)
        ok &= check("CL limbs are REPORTED: the drift is in the record",
                    "CL_limbs_reported_not_gated" in _rcl["D2_detail"], True)

        # --- D2-GEO: THE EXTERNAL, PATH-INDEPENDENT ANCHOR (L-588) -------------
        # This is the clause that compares against a quantity this run did not
        # produce, at a band the flow solver's convergence tail cannot reach.
        for st in ("B", "F", "O"):
            p, d = _synth_decomp(tmp + "/geo" + st, JB, JT, JS, JF, JO,
                                 geo_state=st, geo_delta=1.0e-9)
            r = grade_item8(p, d, DATUM, inh, 300.0, 0)
            ok &= check("D2-GEO state %s off by 1e-9 -> NOT A RESULT" % st,
                        r["label"], LABEL_NOT_A_RESULT)
            ok &= check("D2-GEO state %s flagged" % st,
                        r["D2_detail"]["D2GEO_detail"][st]["ok"], False)
        p, d = _synth_decomp(tmp + "/geoneg", JB, JT, JS, JF, JO,
                             geo_state="F", geo_delta=1.0e-14)
        ok &= check("NEGATIVE -- a 1e-14 geometric difference (< GEO_TOL) does NOT fire",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_PASS)
        p, d = _synth_decomp(tmp + "/geodrop", JB, JT, JS, JF, JO, drop_geo=True)
        try:
            grade_item8(p, d, DATUM, inh, 300.0, 0)
            ok &= check("absent geometric anchor -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("absent geometric anchor -> REFUSE_NO_GEO_IN_STATE",
                        str(e).startswith("REFUSE_NO_GEO_IN_STATE"), True)

        # --- D6, NEW: the frozen optimisation runscript must be UNCHANGED -----
        # "the widened bound never touched O_mp" is a CHECK, not a sentence.
        p, d = _synth_decomp(tmp + "/rs", JB, JT, JS, JF, JO, runscript_md5="0" * 32)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("a changed optimisation runscript -> NOT A RESULT",
                    r["label"], LABEL_NOT_A_RESULT)
        ok &= check("the runscript check is reported",
                    r["D6_detail"]["runscript_unchanged"], False)
        # --- D6, NEW: the staged INPUTS must be the registered inputs ---------
        # X0_MD5 was declared and never read in the first draft: a pin that pins
        # nothing.  Found by the constant sweep of registration section 8a.
        p, d = _synth_decomp(tmp + "/x0", JB, JT, JS, JF, JO, x0_md5="0" * 32)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("a wrong staged x0 -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        ok &= check("the staged-input check is reported",
                    r["D6_detail"]["staged_inputs_are_the_registered_inputs"], False)
        ok &= check("X0_MD5 is READ, not merely declared",
                    r["D6_detail"]["x0_md5_registered"], X0_MD5)

        # --- D3: both sides of the 1.0e-12 absolute cross-check ---------------
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
            ok &= check("producer J off by 1e-11 -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("producer J off by 1e-11 -> REFUSE_J_DISAGREEMENT",
                        str(e).startswith("REFUSE_J_DISAGREEMENT"), True)
        p, d = _perturb_producer_J("/g2", 1.0e-13)
        try:
            ok &= check("NEGATIVE -- producer J off by 1e-13 does NOT refuse",
                        grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_PASS)
        except Refusal as e:
            ok &= check("producer J off by 1e-13 must NOT refuse", str(e), "no refusal")
        # the RE-DERIVED, STRICTLY TIGHTER identity band
        ok &= check("CLOSE_TOL is strictly tighter than the 1.0e-12 it replaces",
                    CLOSE_TOL < 1.0e-12, True)

        # --- D4: interaction above and below the threshold --------------------
        JT2 = JB - 0.002
        JS2 = JB - 0.004 + 5.0e-4
        p, d = _synth_decomp(tmp + "/h", JB, JT2, JS2, JF, JO)
        ok &= check("|I| = 5.0e-4 < 6.0e-4 -> D4 holds, PASS",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_PASS)
        JS3 = JB - 0.004 + 8.0e-4
        p, d = _synth_decomp(tmp + "/i", JB, JT2, JS3, JF, JO)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("|I| = 8.0e-4 > 6.0e-4 -> GATE FAIL", r["label"], LABEL_GATE_FAIL)
        ok &= check("GATE FAIL still emits percentages, qualified",
                    r["percentages"]["split_is_order_dependent"], True)
        ok &= check("GATE FAIL emits BOTH orderings",
                    "order_dependent_pairs" in r["percentages"], True)

        # --- D6: rc, convergence, cap ----------------------------------------
        p, d = _synth_decomp(tmp + "/j", JB, JT, JS, JF, JO)
        ok &= check("rc=137 -> NOT A RESULT",
                    grade_item8(p, d, DATUM, inh, 300.0, 137)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_decomp(tmp + "/k", JB, JT, JS, JF, JO, converged=False)
        ok &= check("a primal not converged -> NOT A RESULT",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_decomp(tmp + "/l", JB, JT, JS, JF, JO)
        ok &= check("cap crossed -> NOT A RESULT",
                    grade_item8(p, d, DATUM, inh, CAP + 0.1, 0)["label"], LABEL_NOT_A_RESULT)
        ok &= check("AT the cap is NOT crossed (strict >)",
                    grade_item8(p, d, DATUM, inh, CAP, 0)["label"], LABEL_PASS)
        # THE CAP CONTROLS ABOVE ARE SELF-REFERENTIAL: they build their boundary
        # from CAPS["DEC5"] and would pass for ANY value it held.  That is how a
        # stale 407.303 survived every selftest in the first draft.  The two
        # checks below are the EXTERNAL anchor -- the literal figures the
        # registration's section 8 carries, typed here as an assertion, not as a
        # source.  If the document and this file ever disagree again, THESE fail.
        # ---- M1 and M2: FAILING CONTROLS, every value typed by the TEST -------
        # sec 8.  A selftest built from the instrument's own constants is a check
        # on arithmetic and not on registration (sec 8c).
        p, d = _synth_decomp(tmp + "/m1a", JB, JT, JS, JF, JO, mesh_ratio=1.25)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("M1: median ratio 1.25 > target -> NOT A RESULT",
                    r["label"], LABEL_NOT_A_RESULT)
        ok &= check("M1 false on ratio", r["M1"], False)
        ok &= check("M1 names the achieved ratio",
                    abs(r["M1_detail"]["growth"]["median"] - 1.25) < 5e-3, True)
        p, d = _synth_decomp(tmp + "/m1b", JB, JT, JS, JF, JO, mesh_layers=61)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("M1: 61 layers instead of 62 -> NOT A RESULT",
                    r["label"], LABEL_NOT_A_RESULT)
        ok &= check("M1 false on layer count", r["M1"], False)
        p, d = _synth_decomp(tmp + "/m1c", JB, JT, JS, JF, JO, mesh=False)
        ok &= check("M1: no volumeMesh.xyz at all -> NOT A RESULT",
                    grade_item8(p, d, DATUM, inh, 300.0, 0)["label"], LABEL_NOT_A_RESULT)
        p, d = _synth_decomp(tmp + "/m2a", JB, JT, JS, JF, JO, diff_changed_lines=2)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("M2: a two-line diff -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        ok &= check("M2 false on diff", r["M2"], False)
        ok &= check("M2 prints the diff it refused",
                    len(r["M2_detail"]["diff"]) > 2, True)
        p, d = _synth_decomp(tmp + "/m2b", JB, JT, JS, JF, JO, mesh_rc=1)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("M2: mesh step rc=1 -> NOT A RESULT", r["label"], LABEL_NOT_A_RESULT)
        ok &= check("M2 false on rc", r["M2"], False)
        # a GENTLE mesh at the registered layer count must NOT trip M1
        p, d = _synth_decomp(tmp + "/m1ok", JB, JT, JS, JF, JO, mesh_ratio=1.18)
        r = grade_item8(p, d, DATUM, inh, 300.0, 0)
        ok &= check("M1: ratio 1.18 at 62 layers -> M1 holds", r["M1"], True)
        ok &= check("M1: and the clean mesh case is still PASS", r["label"], LABEL_PASS)

        # EXTERNAL ANCHORS -- the literals are this document's section 6, typed
        # here by the TEST and not read from the instrument.  These two controls
        # are what caught the DEC4 cap defect (sec 8c find 3) and they caught the
        # DEC5 change too when the figures moved.
        ok &= check("EXTERNAL: the prediction is section 6's 360.7",
                    PREDICTION_CORE_MIN, 360.7)
        ok &= check("EXTERNAL: the registered cap is section 6's 1082.1",
                    CAPS["DEC5"], 1082.1)
        ok &= check("EXTERNAL: the growth target is section 1a's 1.20",
                    GROWTH_TARGET, 1.20)
        ok &= check("EXTERNAL: the sanity band is section 3b.2's 0.123661365",
                    SANITY_BAND, 0.123661365)
        ok &= check("EXTERNAL: the mesh is section 1a's 62 layers / 61 cells",
                    (MESH_N_LAYERS, MESH_CELLS_PER_CHAIN), (62, 61))
        ok &= check("the cap is DERIVED from the prediction, not typed twice",
                    CAPS["DEC5"], round(PREDICTION_CORE_MIN * CAP_FACTOR, 3))

        # --- the non-measurement guard (ADDENDUM 3 A3.4) ----------------------
        p, d = _synth_decomp(tmp + "/n", JB, JT, JS, JF, JO, fail=1)
        try:
            grade_item8(p, d, DATUM, inh, 300.0, 0)
            ok &= check("fail=1 -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("fail=1 -> REFUSE_FAILED_STATE",
                        str(e).startswith("REFUSE_FAILED_STATE"), True)
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
            ok &= check("fail=0 with NaN CD -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("fail=0 with NaN CD -> REFUSE_NON_FINITE",
                        str(e).startswith("REFUSE_NON_FINITE"), True)
        p, d = _synth_decomp(tmp + "/p", JB, JT, JS, JF, JO)
        rows = [json.loads(x) for x in open(p).read().splitlines()]
        rows = [r2 for r2 in rows if r2.get("state") != "S"]
        with open(p, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
        try:
            grade_item8(p, d, DATUM, inh, 300.0, 0)
            ok &= check("missing state S -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("missing state S -> REFUSE_MISSING_STATES",
                        str(e).startswith("REFUSE_MISSING_STATES"), True)
        # an UNREGISTERED state name
        p, d = _synth_decomp(tmp + "/q", JB, JT, JS, JF, JO)
        rows = [json.loads(x) for x in open(p).read().splitlines()]
        extra = dict([x for x in rows if x.get("state") == "S"][0])
        extra["state"] = "X"
        rows.append(extra)
        with open(p, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
        try:
            grade_item8(p, d, DATUM, inh, 300.0, 0)
            ok &= check("an unregistered state -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("an unregistered state -> REFUSE_UNREGISTERED_STATE",
                        str(e).startswith("REFUSE_UNREGISTERED_STATE"), True)
        # this file grades 8R2 and nothing else
        try:
            live_plant_check(9, kw, LABEL_PASS)
            ok &= check("item 9 -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            ok &= check("item 9 -> REFUSE_UNREGISTERED_ITEM",
                        str(e).startswith("REFUSE_UNREGISTERED_ITEM"), True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("D6R2C_DEC5_GRADE SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", len(controls)))
    return 0 if ok else 1


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Grade the successor to D6R2C after-item 8 (arm DEC4).")
    ap.add_argument("--selftest", action="store_true",
                    help="drive the planted controls on synthetic trees; touches no run dir")
    ap.add_argument("--item", choices=("8R2",),
                    help="the only registered item for this instrument")
    ap.add_argument("--arm-dir")
    ap.add_argument("--evals", default="/home/ubuntu/certonomous-runs/"
                    "CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp/d6r2c_evals.jsonl")
    ap.add_argument("--datum-file", help="the arm's .d6r2c_age_datum")
    ap.add_argument("--core-min", type=float)
    ap.add_argument("--rc", type=int)
    ap.add_argument("--out", help="where to write the verdict JSON")
    ap.add_argument("--print-cap", metavar="ARM",
                    help="print the registered cap in core-minutes for ARM and exit. "
                         "THE LAUNCHER CALLS THIS RATHER THAN CARRYING ITS OWN LITERAL: "
                         "a cap that exists in two files is two things that can drift, "
                         "and in the first draft of this item they did.")
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
        kw = dict(jsonl_path=os.path.join(a.arm_dir, "d6r2c_dec5.jsonl"),
                  arm_dir=a.arm_dir, datum_epoch=datum, inherited=inherited,
                  core_min=a.core_min, rc=a.rc)
        rec = grade_item8(**kw)
        rec["planted_control"] = live_plant_check(a.item, kw, rec["label"])
    except Refusal as e:
        print("D6R2C_DEC5_GRADE REFUSED\n%s" % e)
        return 2
    out = a.out or os.path.join(os.path.dirname(a.arm_dir.rstrip("/")),
                                "AFTER_ITEM8R2_GRADE.json")
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
    md = os.path.join(os.path.dirname(out), "DECOMP_TABLE.md")
    with open(md, "w") as fh:
        fh.write(table_markdown(rec))
    print("D6R2C_DEC5_GRADE item=8R2 label=%s table=%s" % (rec["label"], md))
    print("D6R2C_DEC5_GRADE verdict=%s written=%s" % (rec["label"], out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
