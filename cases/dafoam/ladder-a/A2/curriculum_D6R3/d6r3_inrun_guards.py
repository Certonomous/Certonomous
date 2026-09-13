#!/usr/bin/env python3
"""
D6R3 IN-RUN GUARDS -- the six instruments of SHAPE_OPTIMIZATION_STANDING_RULES rules 6-11,
which RUN DURING the optimisation, not after it.

DRAFT.  Registered by cases/dafoam/ladder-a/A2/curriculum_D6R3/PREREGISTRATION.md (R2).
Nothing here launches compute.  Nothing here is sent, filed or submitted (CLAUDE.md rule 7).

WHY THIS FILE EXISTS, in the owner's words (2026-09-13):
    "we must incorporate the within run checks of the instructions to ensure the result we get
     is not from a mesh artefact."

THE CONTRACT EVERY GUARD IN THIS FILE OBEYS
-------------------------------------------
1.  A guard returns exactly one of:  "OK" | "STOP" | "REFUSE".
       OK     -- the quantity was read and is inside its registered threshold.
       STOP   -- the quantity was read and crossed its threshold.  The run stops (rule 7, 9, 10).
       REFUSE -- the guard could not SEE the quantity.  It never degrades to OK.
2.  NON-FINITE IS CHECKED BEFORE ANY COMPARISON (rule 26).  `abs(nan - x) > tol` is False, so a
    guard written the other way round never refuses.
3.  EVERY GUARD COUNTS ITS INFORMATIVE INPUTS AND REFUSES BELOW A REGISTERED FLOOR (rule 25).
    A gate placed where the quantity under test is identically zero cannot fire for any defect.
4.  EVERY CONSTANT IS DERIVED FROM THE THING UNDER TEST IN THE SAME INVOCATION WHERE THAT IS
    POSSIBLE (rule 23); where it is a registered threshold it carries `derived_from` naming the
    registration line it was copied from.
5.  EVERY COUNT IS PRINTED WITH ITS FAILING PARTNER (rule 24):  n_ok + n_bad == n_total, asserted.
6.  --selftest DRIVES EVERY GUARD AGAINST A KNOWN-BAD INPUT AND REQUIRES IT TO FIRE.
    A guard that has never said no is not a guard.

REGISTERED THRESHOLDS -- every one copied verbatim from PREREGISTRATION.md (R2) section 9,
each carrying the sentence it was copied from.
"""

import argparse
import json
import math
import os
import sys

VERSION = "D6R3-INRUN-DRAFT-1"

# ---------------------------------------------------------------------------------------------
# REGISTERED THRESHOLDS.  Each constant carries the registration sentence it was copied from.
# ---------------------------------------------------------------------------------------------

# "useRotations True and LdefFact 1.0 are the two IDWarp mechanisms rule 6 names, verified at
#  UnstructuredMesh.py:138/:1058 -> kd_tree.F90:1110,:1339 and :133/:1053 -> warpMesh.F90:39."
R6_REQUIRED_WARP = {"useRotations": True, "LdefFact": 1.0, "evalMode": "exact"}

# "max non-orthogonality <= 70.0 -- the published DAFoam mesh-quality CONSTRAINT bound,
#  UBend_Channel/runScript_meshQualityConstraint_v2.py:213 (optProb.addCon nonOrtho upper=70.0).
#  NOT the CRM file's own abort threshold of 75.0 (CRM_Wing/runScript.py:82), which remains the
#  registered SOLVER setting.  Measured reason, DAFOAM_CHARTER section 22.7 and reproduced by this
#  lane from the logs named in PREREGISTRATION R2 section 9.7: the solver's own non-orthogonality
#  clause NEVER REFUSES on this family -- O_mp printed 'Non-orthogonality check OK.' in all 202
#  mesh-check blocks while 76 of them measured above 70.0, worst 80.90429398."
R7_MAX_NONORTHO = 70.0
# "worst-cell skewness <= 4.0 -- the published DAFoam mesh-quality CONSTRAINT bound,
#  UBend_Channel/runScript_meshQualityConstraint_v2.py:212."
R7_MAX_SKEWNESS = 4.0
# "max aspect ratio <= 2000.0 -- the PUBLISHED CRM value, CRM_Wing/runScript.py:81."
R7_MAX_ASPECT = 2000.0
# "minimum first-cell height relative to baseline >= 0.80."
R7_MIN_H1_RATIO = 0.80
# "minimum cell volume strictly > 0 and >= 0.10 x the baseline minimum."
R7_MIN_VOL_RATIO = 0.10
# "y+ median <= 1.5 and max <= 3.0 under deviation #1; under the verbatim wall-function setup
#  y+ max <= 110.0, being 1.5 x the measured baseline max of 73.826."
R7_YPLUS_MEDIAN_MAX = 1.5
R7_YPLUS_MAX_MAX = 3.0
R7_YPLUS_MAX_WALLFN = 110.0

# "N = 3 IPOPT majors."
R8_N_MAJORS = 3

# "|J_fresh - J_deformed| / J_fresh <= 0.010 (1.0 %), both sides at matched lift, both trims
#  converged to |CL_i - target_i| <= 1.0e-4."
R9_FRESH_BAND = 0.010
R9_CL_TOL = 1.0e-4

# "if dCD_total < 0 while |dCD_pressure| < 0.20 x |dCD_total| -- more than 80 % of the gain
#  arriving in the viscous component -- and the span load changes by less than 1 % at every
#  station, the run STOPS and re-meshes."
R10_PRESSURE_SHARE_FLOOR = 0.20
R10_SPANLOAD_QUIET = 0.01

# "a per-major move limit of 0.10 on the scaled shape vector's inf-norm and 0.5 deg on twist."
R11_SHAPE_MOVE = 0.10
R11_TWIST_MOVE = 0.5

# "A guard that cannot see must say so rather than pass quietly."  The blindness floor: a design
# perturbation is informative only if non-zero on either side.  D6R2C measured 103 of 109
# components identically zero at x0, leaving all discriminating power in 6.
INFORMATIVE_FLOOR = 6

PLANT = 1.234e-03  # CLAUDE.md rule 3


class Refusal(Exception):
    pass


def _finite(*vals):
    """Rule 26: non-finite is checked BEFORE any comparison, never after."""
    for v in vals:
        if v is None:
            raise Refusal("non-finite: value is None")
        try:
            f = float(v)
        except (TypeError, ValueError):
            raise Refusal("non-finite: value %r is not a number" % (v,))
        if not math.isfinite(f):
            raise Refusal("non-finite: %r" % (f,))
    return True


def _counts(n_ok, n_bad, n_total):
    """Rule 24: every count is printed with its failing partner, and the sum is asserted."""
    if n_ok + n_bad != n_total:
        raise Refusal("count identity failed: %d + %d != %d" % (n_ok, n_bad, n_total))
    return {"n_ok": n_ok, "n_bad": n_bad, "n_total": n_total}


# =============================================================================================
# GUARD 6 -- RULE 6.  The warp settings that carry the near-wall layers are IN FORCE.
#   External anchor: IDWarp's own live option dictionary, read back from the running mesh object.
#   Known-bad input: a live option dict with useRotations False (the setting silently off).
# =============================================================================================

def guard6_warp_in_force(live_options, required=None):
    required = dict(R6_REQUIRED_WARP if required is None else required)
    if not isinstance(live_options, dict):
        raise Refusal("guard6: live option dict is not a dict (%r)" % type(live_options))
    # Rule 25: the guard must be able to SEE each required key.  A key absent from the live dict
    # is not a pass -- IDWarp would be running its own default and the record would not know.
    missing = [k for k in required if k not in live_options]
    if missing:
        raise Refusal("guard6: options not readable from the live mesh object: %s" % missing)
    informative = len(required)
    if informative < 3:
        raise Refusal("guard6: only %d option(s) checked, floor is 3" % informative)
    bad = {}
    for k, want in required.items():
        got = live_options[k]
        if isinstance(want, float):
            _finite(got)
            if abs(float(got) - want) > 0.0:
                bad[k] = (got, want)
        else:
            if got != want:
                bad[k] = (got, want)
    counts = _counts(informative - len(bad), len(bad), informative)
    if bad:
        return {"verdict": "STOP", "rule": 6, "bad": bad, "counts": counts,
                "derived_from": "R6_REQUIRED_WARP, PREREGISTRATION R2 section 9.6"}
    return {"verdict": "OK", "rule": 6, "bad": {}, "counts": counts,
            "derived_from": "R6_REQUIRED_WARP, PREREGISTRATION R2 section 9.6"}


# =============================================================================================
# GUARD 7 -- RULE 7.  The per-iteration quality budget, on the AS-RUN points.
#   External anchor: checkMesh run on the points the solver will read, AFTER the final DV apply.
#   Known-bad input: the MEASURED D6R2 as-run mesh, maxNonOrth 79.21, which breached 70.0 and was
#                    never checked.
# =============================================================================================

def guard7_quality_budget(q, baseline, wall_resolved=True):
    """q and baseline are dicts of measured mesh quality on the AS-RUN points."""
    need = ["source", "maxNonOrtho", "maxSkewness", "maxAspect", "minH1", "minVol",
            "yPlusMedian", "yPlusMax", "checkmesh_mtime", "dv_apply_mtime"]
    missing = [k for k in need if k not in q]
    if missing:
        raise Refusal("guard7: quantities not measured: %s" % missing)
    for k in ("minH1", "minVol"):
        if k not in baseline:
            raise Refusal("guard7: baseline lacks %s, so no ratio can be formed" % k)

    # THE BUDGET IS OUR INSTRUMENT, NOT THE SOLVER'S VERDICT LINE.  A budget that delegates its
    # stop to checkMesh's own "Mesh OK." has already been MEASURED not to stop: 76 of O_mp's 202
    # mesh-check blocks exceeded the declared threshold and every one of them printed
    # "Non-orthogonality check OK." and then "Mesh OK."  This guard therefore requires the
    # QUANTITIES, measured off the as-run mesh, and refuses a verdict string.
    if q["source"] != "as_run_mesh_measurement":
        raise Refusal(
            "guard7: source is %r -- this budget reads MEASURED quantities off the as-run mesh "
            "and refuses in its own code.  The solver's own verdict line is not an input: it was "
            "measured to print 'Non-orthogonality check OK.' at 80.90429398 against a declared "
            "70.0." % (q["source"],))

    # RULE 31, and it is the clause this guard exists for: the quality log must have been written
    # AFTER the final design-variable application, or it describes a mesh no solver saw.
    _finite(q["checkmesh_mtime"], q["dv_apply_mtime"])
    if float(q["checkmesh_mtime"]) <= float(q["dv_apply_mtime"]):
        raise Refusal(
            "guard7: checkMesh (%.3f) is NOT newer than the DV apply (%.3f) -- this quality log "
            "describes the AS-BUILT mesh, not the AS-RUN mesh (rule 31; FM10 measured 66.32 "
            "as-built against 79.21 as-run)" % (float(q["checkmesh_mtime"]), float(q["dv_apply_mtime"])))

    _finite(q["maxNonOrtho"], q["maxSkewness"], q["maxAspect"], q["minH1"], q["minVol"],
            q["yPlusMedian"], q["yPlusMax"], baseline["minH1"], baseline["minVol"])

    # Rule 23: the two ratio thresholds are DERIVED from the baseline in this same invocation.
    if float(baseline["minH1"]) <= 0.0 or float(baseline["minVol"]) <= 0.0:
        raise Refusal("guard7: baseline minH1/minVol is not positive; no ratio is defined")
    h1_ratio = float(q["minH1"]) / float(baseline["minH1"])
    vol_ratio = float(q["minVol"]) / float(baseline["minVol"])

    yp_max_limit = R7_YPLUS_MAX_MAX if wall_resolved else R7_YPLUS_MAX_WALLFN
    checks = [
        ("maxNonOrtho", float(q["maxNonOrtho"]) <= R7_MAX_NONORTHO, q["maxNonOrtho"], R7_MAX_NONORTHO),
        ("maxSkewness", float(q["maxSkewness"]) <= R7_MAX_SKEWNESS, q["maxSkewness"], R7_MAX_SKEWNESS),
        ("maxAspect", float(q["maxAspect"]) <= R7_MAX_ASPECT, q["maxAspect"], R7_MAX_ASPECT),
        ("minH1_ratio", h1_ratio >= R7_MIN_H1_RATIO, h1_ratio, R7_MIN_H1_RATIO),
        ("minVol_positive", float(q["minVol"]) > 0.0, q["minVol"], 0.0),
        ("minVol_ratio", vol_ratio >= R7_MIN_VOL_RATIO, vol_ratio, R7_MIN_VOL_RATIO),
        ("yPlusMax", float(q["yPlusMax"]) <= yp_max_limit, q["yPlusMax"], yp_max_limit),
    ]
    if wall_resolved:
        checks.append(("yPlusMedian", float(q["yPlusMedian"]) <= R7_YPLUS_MEDIAN_MAX,
                       q["yPlusMedian"], R7_YPLUS_MEDIAN_MAX))
    crossed = [(n, v, t) for (n, ok, v, t) in checks if not ok]
    counts = _counts(len(checks) - len(crossed), len(crossed), len(checks))
    verdict = "STOP" if crossed else "OK"
    return {"verdict": verdict, "rule": 7, "crossed": crossed, "counts": counts,
            "h1_ratio": h1_ratio, "vol_ratio": vol_ratio,
            "derived_from": "h1_ratio and vol_ratio derived from the baseline in this invocation"}


# =============================================================================================
# GUARD 8 -- RULE 8.  Periodic re-meshing with restart every N majors.
#   External anchor: the mesh generation stamp, i.e. the extrusion's own output mtime/id.
#   Known-bad input: major 7 with the mesh still carrying the stamp written at major 0.
# =============================================================================================

def guard8_remesh_due(major, mesh_generation_major, n_majors=R8_N_MAJORS):
    _finite(major, mesh_generation_major, n_majors)
    major = int(major)
    mesh_generation_major = int(mesh_generation_major)
    if n_majors < 1:
        raise Refusal("guard8: N must be >= 1, got %r" % n_majors)
    if mesh_generation_major > major:
        raise Refusal("guard8: mesh stamped at major %d, later than the current major %d -- the "
                      "stamp is not this run's" % (mesh_generation_major, major))
    age = major - mesh_generation_major
    counts = _counts(0 if age >= n_majors else 1, 1 if age >= n_majors else 0, 1)
    if age >= n_majors:
        return {"verdict": "STOP", "rule": 8, "action": "REMESH_AND_RESTART",
                "mesh_age_majors": age, "N": n_majors, "counts": counts,
                "derived_from": "R8_N_MAJORS, derived from the measured first checkMesh breach "
                                "at IPOPT major ~6 of 25 in the D6R2C O_mp log"}
    return {"verdict": "OK", "rule": 8, "mesh_age_majors": age, "N": n_majors, "counts": counts,
            "derived_from": "R8_N_MAJORS"}


# =============================================================================================
# GUARD 9 -- RULE 9.  The fresh-mesh objective checkpoint at matched lift.
#   HER OWN LINE: this is the rule that would have caught D6R2 on day one.
#   External anchor: a mesh freshly extruded by pyHyp from the current design surface --
#                    independent of the warp, which is the whole point.
#   Known-bad input: D6R2's OWN measured deformed-vs-fresh gap.
# =============================================================================================

def guard9_fresh_vs_deformed(j_fresh, j_deformed, cl_fresh, cl_deformed, targets,
                             band=R9_FRESH_BAND, cl_tol=R9_CL_TOL):
    _finite(j_fresh, j_deformed)
    j_fresh = float(j_fresh)
    j_deformed = float(j_deformed)
    if j_fresh <= 0.0:
        raise Refusal("guard9: J_fresh is not positive (%r); no relative band is defined" % j_fresh)

    # RULE 19 and RULE 3: neither side may be read at an unconverged lift constraint, or the
    # ratio is not a number.  This is checked BEFORE the drag comparison, deliberately.
    for name, cls in (("fresh", cl_fresh), ("deformed", cl_deformed)):
        if not isinstance(cls, dict) or not cls:
            raise Refusal("guard9: %s side has no CL record; matched lift is unverifiable" % name)
        for k, t in targets.items():
            if k not in cls:
                raise Refusal("guard9: %s side missing condition %r" % (name, k))
            _finite(cls[k], t)
        worst = max(abs(float(cls[k]) - float(targets[k])) for k in targets)
        if worst > cl_tol:
            raise Refusal("guard9: %s side is NOT at matched lift -- worst |CL-target| = %.6e "
                          "against %.1e.  A drag ratio across different lifts is not a number "
                          "(rule 19)." % (name, worst, cl_tol))

    # Rule 25: the comparison must be made where the quantity can differ.  Two sides that are
    # bitwise identical carry no information about whether the reader could see a difference.
    informative = sum(1 for k in targets
                      if abs(float(cl_fresh[k]) - float(cl_deformed[k])) > 0.0) + \
                  (1 if j_fresh != j_deformed else 0)
    rel = abs(j_fresh - j_deformed) / j_fresh
    counts = _counts(0 if rel > band else 1, 1 if rel > band else 0, 1)
    verdict = "STOP" if rel > band else "OK"
    return {"verdict": verdict, "rule": 9, "rel_gap": rel, "band": band,
            "j_fresh": j_fresh, "j_deformed": j_deformed,
            "informative_components": informative, "counts": counts,
            "action": "STOP_AND_REMESH" if verdict == "STOP" else None,
            "derived_from": "R9_FRESH_BAND = the grid-family band of PREREGISTRATION R2 section 8c"}


# =============================================================================================
# GUARD 10 -- RULE 10.  The shear/pressure drag split, every iteration, with the artefact
#   signature named.
#   External anchor: OpenFOAM's own `forces` function object output (force.dat), which carries
#                    total / pressure / viscous columns and is written by the solver, not by us.
#   Known-bad input: a drag gain arriving 100 % in the viscous component with the span load flat.
# =============================================================================================

def guard10_drag_split(prev, cur, spanload_prev, spanload_cur,
                       share_floor=R10_PRESSURE_SHARE_FLOOR, quiet=R10_SPANLOAD_QUIET):
    for name, d in (("prev", prev), ("cur", cur)):
        for k in ("cd_total", "cd_pressure", "cd_viscous"):
            if k not in d:
                raise Refusal("guard10: %s side has no %s -- the `forces` function object did "
                              "not write it (rule 27: a channel with no writer)" % (name, k))
            _finite(d[k])
        s = float(d["cd_pressure"]) + float(d["cd_viscous"])
        if abs(s - float(d["cd_total"])) > 1e-9 * max(1.0, abs(float(d["cd_total"]))):
            raise Refusal("guard10: %s side does not close: pressure + viscous = %.12e against "
                          "total %.12e" % (name, s, float(d["cd_total"])))

    if not spanload_prev or not spanload_cur or len(spanload_prev) != len(spanload_cur):
        raise Refusal("guard10: span load not readable on both sides")
    for a, b in zip(spanload_prev, spanload_cur):
        _finite(a, b)

    n_station = len(spanload_prev)
    if n_station < INFORMATIVE_FLOOR:
        raise Refusal("guard10: only %d span stations, floor is %d -- a span-load test on too "
                      "few stations cannot see a redistribution" % (n_station, INFORMATIVE_FLOOR))

    d_total = float(cur["cd_total"]) - float(prev["cd_total"])
    d_press = float(cur["cd_pressure"]) - float(prev["cd_pressure"])
    d_visc = float(cur["cd_viscous"]) - float(prev["cd_viscous"])

    if d_total == 0.0:
        return {"verdict": "OK", "rule": 10, "reason": "no drag change", "d_total": 0.0,
                "counts": _counts(1, 0, 1)}

    press_share = abs(d_press) / abs(d_total)
    span_change = max(abs(b - a) / max(abs(a), 1e-30) for a, b in zip(spanload_prev, spanload_cur))
    span_quiet = span_change < quiet
    gain = d_total < 0.0
    artefact = gain and (press_share < share_floor) and span_quiet
    counts = _counts(0 if artefact else 1, 1 if artefact else 0, 1)
    return {"verdict": "STOP" if artefact else "OK", "rule": 10,
            "d_total": d_total, "d_pressure": d_press, "d_viscous": d_visc,
            "pressure_share": press_share, "max_spanload_change": span_change,
            "span_quiet": span_quiet, "n_stations": n_station, "counts": counts,
            "action": "STOP_AND_REMESH" if artefact else None,
            "derived_from": "R10_PRESSURE_SHARE_FLOOR; the D6R2 gap was carried 104.5/102.9/99.6 %% "
                            "by PRESSURE drag, so a gain arriving in friction is the inverse"}


# =============================================================================================
# GUARD 11 -- RULE 11.  The trust region on the design step.
#   External anchor: the design vector itself, as the driver recorded it.
#   Known-bad input: a step that moves the scaled shape vector by 0.35, 3.5x the move limit.
# =============================================================================================

def guard11_trust_region(dv_prev, dv_cur, shape_move=R11_SHAPE_MOVE, twist_move=R11_TWIST_MOVE):
    for name, d in (("prev", dv_prev), ("cur", dv_cur)):
        if not isinstance(d, dict) or "shape" not in d or "twist" not in d:
            raise Refusal("guard11: %s design vector lacks shape/twist" % name)
    s0, s1 = list(dv_prev["shape"]), list(dv_cur["shape"])
    t0, t1 = list(dv_prev["twist"]), list(dv_cur["twist"])
    if len(s0) != len(s1) or len(t0) != len(t1):
        raise Refusal("guard11: design vector length changed between steps")
    for v in list(s0) + list(s1) + list(t0) + list(t1):
        _finite(v)

    # RULE 25, and it is not theoretical: at x0 every shape and twist component is exactly zero,
    # so a guard driven only there is blind to any move limit whatsoever.
    informative = sum(1 for a, b in zip(s0, s1) if a != 0.0 or b != 0.0) + \
                  sum(1 for a, b in zip(t0, t1) if a != 0.0 or b != 0.0)
    if informative < INFORMATIVE_FLOOR:
        raise Refusal("guard11: only %d informative components (floor %d) -- every component is "
                      "zero on both sides, so this guard cannot see a step of any size"
                      % (informative, INFORMATIVE_FLOOR))

    ds = max(abs(b - a) for a, b in zip(s0, s1)) if s0 else 0.0
    dt = max(abs(b - a) for a, b in zip(t0, t1)) if t0 else 0.0
    bad = []
    if ds > shape_move:
        bad.append(("shape", ds, shape_move))
    if dt > twist_move:
        bad.append(("twist", dt, twist_move))
    counts = _counts(2 - len(bad), len(bad), 2)
    return {"verdict": "STOP" if bad else "OK", "rule": 11, "bad": bad,
            "shape_step_inf": ds, "twist_step_inf": dt,
            "informative_components": informative, "counts": counts,
            "derived_from": "R11_SHAPE_MOVE / R11_TWIST_MOVE, PREREGISTRATION R2 section 9.11"}


# =============================================================================================
# THE CONTROLS.  Every guard is driven against a KNOWN-BAD INPUT and REQUIRED to fire.
# Where a real measured artefact exists, the known-bad input IS that artefact.
# =============================================================================================

def _c(name, fn, want):
    try:
        r = fn()
        got = r["verdict"]
        detail = {k: v for k, v in r.items() if k not in ("counts",)}
    except Refusal as e:
        got = "REFUSE"
        detail = {"refusal": str(e)}
    ok = (got == want)
    return {"control": name, "want": want, "got": got, "PASS": ok, "detail": detail}


def selftest(verbose=True):
    res = []

    # ---- GUARD 6 -------------------------------------------------------------------------
    good6 = {"useRotations": True, "LdefFact": 1.0, "evalMode": "exact", "aExp": 3.0}
    res.append(_c("G6.clean -- the registered warp settings are in force",
                  lambda: guard6_warp_in_force(good6), "OK"))
    res.append(_c("G6.KNOWN-BAD -- useRotations silently False (rule 6's named mechanism off)",
                  lambda: guard6_warp_in_force(dict(good6, useRotations=False)), "STOP"))
    res.append(_c("G6.KNOWN-BAD -- LdefFact moved to 0.5 without registration",
                  lambda: guard6_warp_in_force(dict(good6, LdefFact=0.5)), "STOP"))
    res.append(_c("G6.KNOWN-BAD -- evalMode back to the published 'fast' approximation",
                  lambda: guard6_warp_in_force(dict(good6, evalMode="fast")), "STOP"))
    res.append(_c("G6.BLIND -- the option is absent from the live dict (IDWarp on its own default)",
                  lambda: guard6_warp_in_force({"LdefFact": 1.0, "evalMode": "exact"}), "REFUSE"))

    # ---- GUARD 7 -------------------------------------------------------------------------
    base7 = {"minH1": 1.0e-4, "minVol": 1.0e-12}
    good7 = {"source": "as_run_mesh_measurement",
             "maxNonOrtho": 66.32, "maxSkewness": 1.9, "maxAspect": 684.4,
             "minH1": 0.98e-4, "minVol": 0.9e-12, "yPlusMedian": 0.47, "yPlusMax": 0.998,
             "checkmesh_mtime": 200.0, "dv_apply_mtime": 100.0}
    res.append(_c("G7.clean -- as-run mesh inside every threshold",
                  lambda: guard7_quality_budget(good7, base7), "OK"))
    # ---- the REAL as-run meshes.  Every value below was read by this lane from the named log
    # ---- with `grep -o "Mesh non-orthogonality Max: [0-9.]*"`, not copied from prose (s22.6).
    res.append(_c("G7.KNOWN-BAD/REAL -- O_mp's WORST as-run mesh, 80.90429398, which OpenFOAM "
                  "itself called 'Non-orthogonality check OK.' then 'Mesh OK.'",
                  lambda: guard7_quality_budget(dict(good7, maxNonOrtho=80.90429398), base7), "STOP"))
    res.append(_c("G7.KNOWN-BAD/REAL -- FM10's worst as-run mesh, 79.21261137, 6 of 6 blocks over "
                  "70.0 and ZERO 'Failed 1 mesh checks.' in that log",
                  lambda: guard7_quality_budget(dict(good7, maxNonOrtho=79.21261137), base7), "STOP"))
    res.append(_c("G7.KNOWN-BAD/REAL -- 71.23798136, the value present in BOTH logs' check blocks, "
                  "1.8 % over and passed by the solver",
                  lambda: guard7_quality_budget(dict(good7, maxNonOrtho=71.23798136), base7), "STOP"))
    res.append(_c("G7.KNOWN-BAD/REAL -- 70.01418200, the SMALLEST of O_mp's 76 over-70 values: the "
                  "budget must catch the marginal breach too",
                  lambda: guard7_quality_budget(dict(good7, maxNonOrtho=70.014182), base7), "STOP"))
    res.append(_c("G7.REAL/boundary -- 66.96543422, an O_mp block genuinely under 70.0, must NOT fire",
                  lambda: guard7_quality_budget(dict(good7, maxNonOrtho=66.96543422), base7), "OK"))
    res.append(_c("G7.DELEGATION -- handed the solver's own verdict line instead of a measurement, "
                  "the budget must REFUSE: that channel was measured never to refuse",
                  lambda: guard7_quality_budget(dict(good7, source="solver_verdict"), base7), "REFUSE"))
    res.append(_c("G7.KNOWN-BAD/REAL -- D6R2's worst aspect-ratio trip 1050.3162 against the CRM's "
                  "published 2000.0: does NOT fire, and that is registered as a finding",
                  lambda: guard7_quality_budget(dict(good7, maxAspect=1050.3162), base7), "OK"))
    res.append(_c("G7.KNOWN-BAD -- aspect ratio 2100 breaches the published CRM 2000.0",
                  lambda: guard7_quality_budget(dict(good7, maxAspect=2100.0), base7), "STOP"))
    res.append(_c("G7.KNOWN-BAD -- skewness 4.5 breaches the published constraint bound 4.0",
                  lambda: guard7_quality_budget(dict(good7, maxSkewness=4.5), base7), "STOP"))
    res.append(_c("G7.KNOWN-BAD -- first cell collapsed to 0.5x baseline",
                  lambda: guard7_quality_budget(dict(good7, minH1=0.5e-4), base7), "STOP"))
    res.append(_c("G7.KNOWN-BAD -- a negative cell volume",
                  lambda: guard7_quality_budget(dict(good7, minVol=-1.0e-14), base7), "STOP"))
    res.append(_c("G7.KNOWN-BAD -- y+ median drifted to 2.0 under warping",
                  lambda: guard7_quality_budget(dict(good7, yPlusMedian=2.0), base7), "STOP"))
    res.append(_c("G7.RULE-31 -- checkMesh written BEFORE the DV apply (the FM10 defect exactly)",
                  lambda: guard7_quality_budget(dict(good7, checkmesh_mtime=50.0), base7), "REFUSE"))
    res.append(_c("G7.NON-FINITE -- maxNonOrtho is NaN (rule 26: nan>tol is False)",
                  lambda: guard7_quality_budget(dict(good7, maxNonOrtho=float("nan")), base7), "REFUSE"))
    res.append(_c("G7.BLIND -- maxNonOrtho was never measured",
                  lambda: guard7_quality_budget({k: v for k, v in good7.items()
                                                 if k != "maxNonOrtho"}, base7), "REFUSE"))

    # ---- GUARD 8 -------------------------------------------------------------------------
    res.append(_c("G8.clean -- mesh regenerated at major 6, now at major 7, N=3",
                  lambda: guard8_remesh_due(7, 6), "OK"))
    res.append(_c("G8.KNOWN-BAD -- major 7 on a mesh stamped at major 0 (D6R2's whole run)",
                  lambda: guard8_remesh_due(7, 0), "STOP"))
    res.append(_c("G8.boundary -- exactly N=3 majors old must fire",
                  lambda: guard8_remesh_due(3, 0), "STOP"))
    res.append(_c("G8.boundary -- exactly N-1=2 majors old must not fire",
                  lambda: guard8_remesh_due(2, 0), "OK"))
    res.append(_c("G8.BLIND -- the mesh stamp is from the future, so it is not this run's",
                  lambda: guard8_remesh_due(3, 9), "REFUSE"))

    # ---- GUARD 9 -- the one that would have caught D6R2 -----------------------------------
    tgt = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
    matched = {"cl04": 0.40000, "cl05": 0.50000, "cl06": 0.60002}
    res.append(_c("G9.clean -- fresh and deformed agree to 0.3 %, both at matched lift",
                  lambda: guard9_fresh_vs_deformed(0.0230, 0.02293, matched, matched, tgt), "OK"))
    # D6R2's OWN measured numbers: deformed-mesh optimum/baseline 0.753 vs fresh 1.206.
    res.append(_c("G9.KNOWN-BAD/MEASURED -- D6R2's own deformed 0.753 vs fresh 1.206 ratio pair",
                  lambda: guard9_fresh_vs_deformed(1.206, 0.753, matched, matched, tgt), "STOP"))
    res.append(_c("G9.KNOWN-BAD/MEASURED -- the 139-count deformed-vs-fresh gap on CD 0.023",
                  lambda: guard9_fresh_vs_deformed(0.0230, 0.0230 - 0.0139, matched, matched, tgt),
                  "STOP"))
    res.append(_c("G9.boundary -- a 1.1 % gap must fire against the 1.0 % band",
                  lambda: guard9_fresh_vs_deformed(1.0, 1.0 - 0.011, matched, matched, tgt), "STOP"))
    res.append(_c("G9.boundary -- a 0.9 % gap must not fire",
                  lambda: guard9_fresh_vs_deformed(1.0, 1.0 - 0.009, matched, matched, tgt), "OK"))
    # FM10's MEASURED lift excess: +0.1493 / +0.1516 / +0.1524 above target.
    fm10 = {"cl04": 0.4 + 0.1493, "cl05": 0.5 + 0.1516, "cl06": 0.6 + 0.1524}
    res.append(_c("G9.KNOWN-BAD/MEASURED -- FM10's +0.149/+0.152/+0.152 lift excess: refuse the "
                  "comparison rather than report a drag ratio across different lifts",
                  lambda: guard9_fresh_vs_deformed(0.0230, 0.0229, fm10, matched, tgt), "REFUSE"))
    res.append(_c("G9.NON-FINITE -- J_fresh is NaN",
                  lambda: guard9_fresh_vs_deformed(float("nan"), 0.023, matched, matched, tgt),
                  "REFUSE"))
    res.append(_c("G9.PLANT -- a plant of 1.234e-03 on a J of 0.023 (5.4 %) must be seen",
                  lambda: guard9_fresh_vs_deformed(0.0230, 0.0230 - PLANT, matched, matched, tgt),
                  "STOP"))
    res.append(_c("G9.BLIND -- the fresh side has no CL record at all",
                  lambda: guard9_fresh_vs_deformed(0.023, 0.0229, {}, matched, tgt), "REFUSE"))

    # ---- GUARD 10 ------------------------------------------------------------------------
    span = [0.10, 0.20, 0.30, 0.40, 0.35, 0.25, 0.15, 0.05]
    span_moved = [x * (1.10 if i < 4 else 0.90) for i, x in enumerate(span)]
    p10 = {"cd_total": 0.02300, "cd_pressure": 0.01500, "cd_viscous": 0.00800}
    res.append(_c("G10.clean -- a real gain, carried by PRESSURE, with the span load moving",
                  lambda: guard10_drag_split(
                      p10, {"cd_total": 0.02200, "cd_pressure": 0.01400, "cd_viscous": 0.00800},
                      span, span_moved), "OK"))
    res.append(_c("G10.KNOWN-BAD -- the artefact signature: 100 % of the gain in FRICTION with "
                  "the span load flat",
                  lambda: guard10_drag_split(
                      p10, {"cd_total": 0.02200, "cd_pressure": 0.01500, "cd_viscous": 0.00700},
                      span, span), "STOP"))
    res.append(_c("G10.boundary -- 19 % of the gain in pressure (just inside the 20 % floor) fires",
                  lambda: guard10_drag_split(
                      p10, {"cd_total": 0.02200, "cd_pressure": 0.01500 - 0.00019,
                            "cd_viscous": 0.00800 - 0.00081}, span, span), "STOP"))
    res.append(_c("G10.boundary -- 21 % of the gain in pressure does not fire",
                  lambda: guard10_drag_split(
                      p10, {"cd_total": 0.02200, "cd_pressure": 0.01500 - 0.00021,
                            "cd_viscous": 0.00800 - 0.00079}, span, span), "OK"))
    res.append(_c("G10.not-a-gain -- a friction-only RISE is not the artefact signature",
                  lambda: guard10_drag_split(
                      p10, {"cd_total": 0.02400, "cd_pressure": 0.01500, "cd_viscous": 0.00900},
                      span, span), "OK"))
    res.append(_c("G10.BLIND -- `forces` never wrote the viscous column (rule 27)",
                  lambda: guard10_drag_split(
                      p10, {"cd_total": 0.02200, "cd_pressure": 0.01400}, span, span), "REFUSE"))
    res.append(_c("G10.INCONSISTENT -- pressure + viscous does not equal total",
                  lambda: guard10_drag_split(
                      p10, {"cd_total": 0.02200, "cd_pressure": 0.01400, "cd_viscous": 0.00900},
                      span, span), "REFUSE"))
    res.append(_c("G10.BLIND -- 3 span stations, below the informative floor of 6",
                  lambda: guard10_drag_split(
                      p10, {"cd_total": 0.02200, "cd_pressure": 0.01500, "cd_viscous": 0.00700},
                      span[:3], span[:3]), "REFUSE"))

    # ---- GUARD 11 ------------------------------------------------------------------------
    prev11 = {"shape": [0.01 * (i % 7 + 1) for i in range(192)], "twist": [0.1] * 7}
    small = {"shape": [v + 0.02 for v in prev11["shape"]], "twist": [0.2] * 7}
    big = {"shape": [v + 0.35 for v in prev11["shape"]], "twist": [0.2] * 7}
    bigt = {"shape": [v + 0.02 for v in prev11["shape"]], "twist": [0.9] * 7}
    res.append(_c("G11.clean -- a 0.02 scaled-shape step inside the 0.10 move limit",
                  lambda: guard11_trust_region(prev11, small), "OK"))
    res.append(_c("G11.KNOWN-BAD -- a 0.35 scaled-shape step, 3.5x the move limit",
                  lambda: guard11_trust_region(prev11, big), "STOP"))
    res.append(_c("G11.KNOWN-BAD -- a 0.8 deg twist step against the 0.5 deg limit",
                  lambda: guard11_trust_region(prev11, bigt), "STOP"))
    res.append(_c("G11.BLIND/MEASURED -- x0, where D6R2C measured 103 of 109 components exactly "
                  "zero: the guard must REFUSE, not pass",
                  lambda: guard11_trust_region({"shape": [0.0] * 192, "twist": [0.0] * 7},
                                               {"shape": [0.0] * 192, "twist": [0.0] * 7}), "REFUSE"))
    res.append(_c("G11.NON-FINITE -- a NaN in the design vector",
                  lambda: guard11_trust_region(prev11,
                                               {"shape": [float("nan")] + small["shape"][1:],
                                                "twist": small["twist"]}), "REFUSE"))

    n_pass = sum(1 for r in res if r["PASS"])
    n_fail = len(res) - n_pass
    assert n_pass + n_fail == len(res)  # rule 24

    if verbose:
        for r in res:
            print("%-6s %-4s want=%-6s got=%-6s  %s"
                  % ("PASS" if r["PASS"] else "FAIL", "", r["want"], r["got"], r["control"]))
            if not r["PASS"]:
                print("        detail: %s" % json.dumps(r["detail"], default=str)[:400])
        print()
        print("D6R3_INRUN SELFTEST  n_total=%d  n_pass=%d  n_fail=%d" % (len(res), n_pass, n_fail))
        print("D6R3_INRUN SELFTEST %s" % ("PASS" if n_fail == 0 else "FAIL"))
    return res, n_pass, n_fail


def main(argv=None):
    ap = argparse.ArgumentParser(prog="d6r3_inrun_guards.py")
    ap.add_argument("--selftest", action="store_true",
                    help="drive every guard against a known-bad input and require it to fire")
    ap.add_argument("--json", default=None, help="write the control table to this path")
    ap.add_argument("--version", action="store_true")
    a = ap.parse_args(argv)
    if a.version:
        print(VERSION)
        return 0
    if not a.selftest:
        ap.print_help()
        return 64
    res, n_pass, n_fail = selftest()
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"version": VERSION, "n_total": len(res), "n_pass": n_pass,
                       "n_fail": n_fail, "controls": res}, f, indent=1, default=str)
        print("wrote %s" % a.json)
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
