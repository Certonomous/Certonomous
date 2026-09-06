#!/usr/bin/env python
"""Curriculum D6RF4 -- the CONVERGENCE PROBE `P_conv`, and (in `full` mode)
the endpoint finite-difference spot-check of the COMPOSITE J.

DERIVED FROM `curriculum_D6RF3/d6rf4_fd_endpoint.py`
(md5 `24586c9ab7f733cd2b642775aaf7fbe3`, verified on disk before this file was
written) with the REGISTERED DELTAS of `D6RF4 PREREGISTRATION.md` sections 4
and 5, enumerated in `d6rf4_fd_endpoint_DELTAS_from_d6rf3.diff` beside this
file.  FOUR mechanisms, all registered before compute:

  N1  `D6RF4-DEF-7`, REPAIR PART 1 (section 4).  THE GATED PRODUCT IS WRITTEN
      INCREMENTALLY.  The parent wrote `OUT` exactly once, at the very end,
      AFTER every FD leg -- so a run that died at its first primal left NO
      `.json` at all and `X-CDLOG` had no source to read.  Here `_write_out()`
      is called AFTER THE BASELINE PRIMAL, BEFORE ANY FD LEG, and again after
      every subsequent primal.  A run that dies at point k leaves the CD block
      for everything up to k on disk and readable.  The `.jsonl` stays what it
      always was -- a progress log -- and is never a gated source.

  N2  `D6RF4-DEF-8`, REPAIR PART 1 (section 5).  `baseline_repeat` runs
      IMMEDIATELY after `baseline` and BEFORE ANY FD LEG, so `eta_raw` -- the
      bar falsifier `F1` is read against -- exists at the cheapest possible
      point in the program.  The parent already had this ORDER; what it did
      not have is an EXECUTABLE assertion of it, so a successor could reorder
      the program and lose the bar silently.  `_LEGS_RUN` records every primal
      as it completes and `_require_bar_before_fd()` REFUSES (exit 2) if an FD
      leg is reached with `baseline_repeat` not in it.

  N3  `--mode`, section 8.2's three legs.  `P_conv` runs `baseline` then
      `baseline_repeat` AND STOPS -- no `compute_totals`, no FD legs, because
      `D6RF4` buys a convergence measurement and not a gradient.  `F5_loose`
      runs `baseline` ONLY, at `D6RF3`'s original `fvSolution`, and is
      falsifier `F5`.  `full` is the parent's whole program, unchanged in
      shape, and is NOT registered at this freeze.

  N4  LEG MARKERS.  Each leg prints `D6RF4_LEG_BEGIN <leg>` and
      `D6RF4_LEG_END <leg> ...` to stdout, which is how the grader SPLITS one
      container log into per-leg segments and reads each leg's own final-
      iteration residuals for `G-CONV`.  Without a marker the three legs are
      one undifferentiated log and no per-leg number can be cited.

  N5  `F5_loose` DOES NOT PROPAGATE THE PRIMAL FAILURE.  Its registered
      prediction IS that DAFoam refuses the primal post-`End` at
      `1.3162e-05 > 1.0e-05`; that refusal is the falsifier's DATUM, not the
      arm crashing.  The exception is caught, recorded in the product AND in
      the leg marker as `leg_primal_raised=True`, and the leg exits 0 so the
      arm completes and `G1` can grade it.  THE ACCEPT FLOOR IS NOT TOUCHED TO
      MAKE THIS HAPPEN -- `primalMinResTol` and `primalMinResTolDiff` are
      unchanged at `1e-08` and `1000` and `d6rf4_accept_floor_control.py`
      REFUSES the whole grading if either has moved.

INHERITED VERBATIM below this line.

DERIVED FROM `curriculum_D6RF2/d6rf2_fd_endpoint.py`
(md5 `0ce81a0b038abe12728b5b062e4420df`, verified on disk before this file was
written) with the REGISTERED DELTAS of `D6RF4 PREREGISTRATION.md` section 2a,
enumerated in `d6rf4_fd_endpoint_DELTAS_from_d6rf2.diff` beside this file:

  * PRODUCER is this item's own staged `d6rf4_opt_runScript.py`.  ITS md5 IS
    UNCHANGED at `137539e0a99be27f27fdb69e063b2a87` -- the staged copy is
    BYTE-IDENTICAL to `D6RF2`'s, deliberately, so that `G-ANCHOR`'s single-
    occurrence assertion on `# OpenMDAO setup` (`D6RF-BLOCKING-1`'s repair)
    carries over unaltered rather than being re-established.
  * PRODUCTS carry this item's names: `d6rf4_fd_endpoint.json` / `.jsonl`, and
    the endpoint DVs are read from `d6rf4_endpoint_dvs.json`.
  * THE ONE SUBSTANTIVE DELTA: the JSON product now carries a TOP-LEVEL
    `points` block, which is the path `PREREGISTRATION.md` section 2a
    registers as the source of `CD_i(mp)`.  The parent already MEASURED these
    numbers -- `d6rf2_fd_endpoint.py:114-118` calls
    `prob.get_val("<pt>.aero_post.CD")` for all three points at every primal
    including `baseline` -- but wrote them only under `points_baseline`, so
    the registered path did not exist in the product.  Zero marginal
    core-minutes: nothing new is computed.

INHERITED VERBATIM from the parent chain (D6 -> D6R -> D6RF -> D6RF2): the step
ladder, clearance rule, plateau tolerance, eta floor and the emit/plan/FD logic
are D4's bytes.  The A6 step-rule limitation is inherited VERBATIM:
  "One item, five components, one case, one eta.  The rule has not been tried
   where the proxy |J_adj| is itself wrong -- which is the case it would be
   worst at, since it sizes the step from the very quantity under test."

THE PLATEAU.  The `s_lo`/`s_hi` pair this program evaluates IS
`VERIFICATION_CHARTER.md` section 7 step 1's "two or three point mini-sweep",
which `DAFOAM_CHARTER.md` section 3 delegates the definition of and section 20
(addendum 2026-09-04) rules SATISFIES section 3.  **No caveat that a plateau
proof is not claimed belongs on this artefact; writing one would be a false
self-deprecation.**  What IS true and is reported by the grader per component:
the pair grades at `s_hi` with its only neighbour BELOW it, so the coarse side
is unmeasured -- a strength-of-evidence fact, not a compliance one.  This family
has a measured instance of that blind side firing (`D15_D16_FD_STEP_TABLE.md:234`,
D16 PATCHED CL `shape[6]`: 14.0978 % coarse against 1.1268 % fine).  Buying a
third, coarser point is a STRENGTHENING and is not bought here; not buying it is
not a breach (`DAFOAM_CHARTER.md` section 20.2).

DERIVED FROM curriculum_D5/d5_fd_endpoint.py (itself D4's d4_fd_endpoint.py,
md5 c6112b0ec3bfdb5287345e350500f64a, re-pointed) with the REGISTERED DELTAS of
D6 PREREGISTRATION.md section 3:
  * PRODUCER is d6r_opt_runScript.py (frozen md5 below); the header up to the
    literal anchor `# OpenMDAO setup` is exec'd so daOptions, Top, POINTS,
    WEIGHTS and the DVs are the producer's own bytes;
  * the graded function is the composite objective `obj.J`; each primal also
    records CD and CL at every point (the per-point numbers G-D6-1 reads);
  * the endpoint DVs come from d6r_endpoint_dvs.json (twist, shape,
    patchV_cl04/05/06);
  * the five COMPONENTS are shape[46], shape[18], shape[0], twist[0] and
    patchV_cl05[1] (the AoA of the CL 0.5 point), NAMED IN ADVANCE.
Step ladder, clearance rule, plateau tolerance, eta floor and the emit/plan/FD
logic are D4's bytes.  The A6 step-rule limitation is inherited VERBATIM:
  "One item, five components, one case, one eta.  The rule has not been tried
   where the proxy |J_adj| is itself wrong -- which is the case it would be
   worst at, since it sizes the step from the very quantity under test."
EVERY graded number is written to a FILE by rank 0 (MPI log splicing on this
case is MEASURED, A2 per_component_table 2.2, commit 79679a84).
"""
import argparse
import hashlib
import json
import os
import sys
import time

PRODUCER = "d6rf4_opt_runScript.py"
PRODUCER_MD5 = "137539e0a99be27f27fdb69e063b2a87"
ANCHOR = "# OpenMDAO setup"

CLEARANCE_FLOOR = 5.0
RATIO_MIN = 2.0
PLATEAU_TOL = 10.0
ETA_FLOOR = 1.0e-14
LADDER = {
    "shape":  [1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2],
    "twist":  [1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1],
    "patchV_cl05": [1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1],
}
COMPONENTS = [
    ("shape", 46),
    ("shape", 18),
    ("shape", 0),
    ("twist", 0),
    ("patchV_cl05", 1),
]
DV_KEYS = ("twist", "shape", "patchV_cl04", "patchV_cl05", "patchV_cl06")
OUT = "d6rf4_fd_endpoint.json"
JSONL = "d6rf4_fd_endpoint.jsonl"

# ---------------------------------------------------------------- section 8.2
# THE REGISTERED LEGS.  `P_conv` is the ONLY arm registered at this freeze and
# it runs L1 then L3; L2 is inside L1's mode.  `full` is priced but NOT bought
# (PREREGISTRATION.md section 8.2), and is kept here so the successor that buys
# it inherits one file rather than a re-derivation.
MODES = ("P_conv", "F5_loose", "full")
MODE_OUT = {"P_conv": OUT, "F5_loose": "d6rf4_f5_endpoint.json", "full": OUT}
MODE_JSONL = {"P_conv": JSONL, "F5_loose": "d6rf4_f5_endpoint.jsonl",
              "full": JSONL}

# `D6RF4-DEF-8`.  THE ORDER IS ASSERTED, NOT MERELY INTENDED.  Every primal
# that completes appends its tag here, and an FD leg refuses if the bar its
# falsifier is read against is not already in the list.
_LEGS_RUN = []
BAR_LEG = "baseline_repeat"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def leg_say(*words):
    """The per-leg stdout marker the grader splits the container log on.

    Flushed and fsync'd through stdout deliberately: a marker that is still in
    a buffer when the container is killed segments nothing, and an unsegmented
    log is a log no per-leg number can be cited from."""
    sys.stdout.write(" ".join(str(w) for w in words) + "\n")
    sys.stdout.flush()
    try:
        os.fsync(sys.stdout.fileno())
    except (OSError, ValueError):                 # not a real fd under a pipe
        pass


def _require_bar_before_fd(mode):
    """`D6RF4-DEF-8` repair part 1, MADE EXECUTABLE.

    `F1`'s yardstick `eta_raw` is DERIVED FROM THE RUN -- which is the property
    `DAFOAM_CHARTER.md` section 21.6 singles out as the design this family
    should prefer, because a bar derived from the run cannot be mis-sized
    against what it bounds.  The other half, which 2026-09-05 taught: a bar
    derived from the run DOES NOT EXIST when the run stops early.  So the
    program is ordered to buy the bar first, and that order is ASSERTED here
    rather than left to whoever edits `main()` next."""
    if BAR_LEG not in _LEGS_RUN:
        sys.stderr.write(
            "D6RF4_FD REFUSE mode=%s reached an FD leg with legs_run=%r -- "
            "`%s` has not run, so `eta_raw` does not exist and F1's bar would "
            "be UNRESOLVED with FD rows already bought. Order refused.\n"
            % (mode, _LEGS_RUN, BAR_LEG))
        sys.exit(2)


def main(mode):
    if mode not in MODES:
        sys.stderr.write("D6RF4_FD REFUSE unknown mode %r; registered: %r\n"
                         % (mode, MODES))
        sys.exit(2)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("D6RF4_FD REFUSE producer md5 %s != frozen %s\n" % (got, PRODUCER_MD5))
        sys.exit(2)
    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D6RF4_FD REFUSE anchor %r appears %d times\n" % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]
    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d6rf4_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    Top = ns["Top"]
    POINTS = ns["POINTS"]

    out_path, jsonl_path = MODE_OUT[mode], MODE_JSONL[mode]

    def emit(rec):
        if rank != 0:
            return
        with open(jsonl_path, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    with open("d6rf4_endpoint_dvs.json") as fh:
        dvs = json.load(fh)
    for key in DV_KEYS:
        if key not in dvs:
            sys.stderr.write("D6RF4_FD REFUSE endpoint dv file missing %s\n" % key)
            sys.exit(2)
        prob.set_val(key, np.array(dvs[key], dtype=float))
    emit({"kind": "endpoint_dvs", "source": dvs.get("_source"),
          "n_twist": len(dvs["twist"]), "n_shape": len(dvs["shape"]),
          "n_patchV": {pt: len(dvs["patchV_" + pt]) for pt in POINTS}})

    J = "obj.J"

    # ---------------------------------------------------------- section 4/5
    # `_state` IS THE PRODUCT, built as the run goes rather than at the end.
    # `D6RF4-DEF-7`: the parent assembled this dict in one place, AFTER every
    # FD leg, so a run that died at its first primal wrote no `.json` at all
    # and `X-CDLOG` read `ARM_DID_NOT_RUN` about an arm that had run for 2.067
    # core-min.  Here every key exists as soon as it is measured.
    _state = {
        "mode": mode,
        "producer_md5": got,
        "components_requested": [[d, i] for (d, i) in COMPONENTS],
        "n_components_requested": len(COMPONENTS),
        "clearance_floor": CLEARANCE_FLOOR, "ratio_min": RATIO_MIN,
        "plateau_tol_pct": PLATEAU_TOL, "ladder": LADDER,
        "legs_run": _LEGS_RUN,
        "n_primals_completed": 0,
        "points_source": "FD_BASELINE_PRIMAL",
        "points_source_statement": (
            "CD_i(mp) is prob.get_val('<pt>.aero_post.CD') in the `baseline` "
            "primal of this program, at the endpoint design vector "
            "reconstructed to PHYSICAL units. It is NOT the last accepted "
            "major of D6R's optimisation (D6RF section 0a's quantity), and no "
            "result carrying it may be compared to a D6R- or D6RF-era "
            "CD_i(mp) without this label travelling with the number "
            "(DAFOAM_CHARTER.md section 18.6 refinement 2)."),
        "optimality_claim": (
            "NONE. The producing optimisation exited `Invalid number in NLP "
            "function or derivative detected.` and 687 of its 863 recorded "
            "funcs rows are non-finite (D6RF3-DEF-5). This is a design point, "
            "not an optimum."),
        "fvSolution_statement": (
            "THE ONLY THING D6RF4 CHANGES ABOUT THE PRIMAL IS THE LINEAR-"
            "SOLVER STOPPING RULE IN system/fvSolution, and it TIGHTENS it. "
            "primalMinResTol (1e-08) and primalMinResTolDiff (1000) are "
            "carried forward byte-identical, so the accept floor is 1.0e-05 "
            "in every leg of this item. d6rf4_accept_floor_control.py reads "
            "both values back out of the container log and REFUSES the "
            "grading if either has moved."),
    }

    def _write_out():
        """THE DEF-7 REPAIR.  Called after EVERY primal, and the first call is
        BEFORE ANY FD LEG.  Written to a temp path and renamed, so a kill
        during the write leaves the previous complete product rather than a
        truncated one."""
        if rank != 0:
            return
        _state["legs_run"] = list(_LEGS_RUN)
        _state["n_primals_completed"] = len(_LEGS_RUN)
        tmp = out_path + ".partial"
        with open(tmp, "w") as fh:
            json.dump(_state, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, out_path)
        leg_say("D6RF4_FD_ENDPOINT_WRITTEN", out_path,
                "legs_run=%s" % ",".join(_LEGS_RUN),
                "n_rows=%d" % len(_state.get("rows", [])))

    def primal(tag):
        t0 = time.time()
        leg_say("D6RF4_LEG_BEGIN", tag, "mode=%s" % mode)
        prob.run_model()
        j = float(prob.get_val(J)[0])
        per = {}
        for pt in POINTS:
            per[pt] = {"CD": repr(float(prob.get_val("%s.aero_post.CD" % pt)[0])),
                       "CL": repr(float(prob.get_val("%s.aero_post.CL" % pt)[0]))}
        emit({"kind": "primal", "tag": tag, "J": repr(j), "points": per,
              "wall_s": round(time.time() - t0, 3)})
        _LEGS_RUN.append(tag)
        leg_say("D6RF4_LEG_END", tag, "mode=%s" % mode, "J=%r" % j,
                "wall_s=%.3f" % (time.time() - t0), "primal_raised=False")
        return j, per

    # ================= LEG 1 / LEG 3: THE BASELINE PRIMAL ===================
    # In `F5_loose` this is falsifier F5 at D6RF3's ORIGINAL fvSolution and its
    # registered prediction is that DAFoam refuses it post-`End`.  That refusal
    # is F5's DATUM (section 6), not the arm crashing, so it is caught, recorded
    # and reported -- and the accept floor it fails against is NOT moved to let
    # it through.
    if mode == "F5_loose":
        try:
            j0, per0 = primal("baseline")
            _state.update({"J_baseline": repr(j0), "points_baseline": per0,
                           "points": per0, "primal_raised": False})
        except Exception as exc:                              # noqa: BLE001
            _LEGS_RUN.append("baseline_RAISED")
            _state.update({"J_baseline": None, "points": {},
                           "primal_raised": True,
                           "primal_error": repr(exc)[:800],
                           "primal_raised_statement": (
                               "F5 is the DELIBERATELY WRONG SETTING and its "
                               "registered predicted value, 1.3162e-05, FAILS "
                               "G-CONV's own bar of 1.0e-05 by 1.3162x. A "
                               "refusal here is the prediction landing, not "
                               "the arm failing. The per-field residuals the "
                               "gate actually reads are in this leg's own log "
                               "segment, between its LEG_BEGIN and LEG_END "
                               "markers.")})
            emit({"kind": "primal_raised", "tag": "baseline", "mode": mode,
                  "error": repr(exc)[:800]})
            leg_say("D6RF4_LEG_END", "baseline", "mode=%s" % mode,
                    "primal_raised=True")
        _write_out()
        leg_say("D6RF4_MODE_COMPLETE", mode,
                "legs_run=%s" % ",".join(_LEGS_RUN))
        MPI.COMM_WORLD.Barrier()
        return

    j0, per0 = primal("baseline")
    # ---- THE DEF-7 WRITE POINT.  `points.<pt>.CD` IS ON DISK HERE, BEFORE
    # ---- ANY FD LEG AND BEFORE compute_totals.  `points` and
    # ---- `points_baseline` are THE SAME OBJECT, not a second measurement.
    _state.update({"J_baseline": repr(j0), "points_baseline": per0,
                   "points": per0})
    _write_out()

    # ================= LEG 2: THE BAR F1 IS READ AGAINST ====================
    j0r, per0r = primal("baseline_repeat")
    eta_raw = abs(j0 - j0r)
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flagged, "J_baseline": repr(j0), "J_repeat": repr(j0r)})
    _state.update({"J_baseline_repeat": repr(j0r),
                   "points_baseline_repeat": per0r,
                   "eta_raw": repr(eta_raw), "eta_used": repr(eta),
                   "eta_floored": eta_flagged,
                   "bar_state": "BAR_PRODUCED",
                   "bar_producing_leg": BAR_LEG})
    _write_out()

    if mode == "P_conv":
        # THE REGISTERED ARM STOPS HERE.  D6RF4 buys a CONVERGENCE measurement,
        # not a gradient: section 8.2 prices the full FD arm at 934 core-min at
        # the tightened settings and refuses to buy a 934 core-min arm to learn
        # a 17.9 core-min fact.  G-FD, band D, G-OFF and G-PRICE therefore have
        # NO INPUTS in this arm and read NOT A RESULT for want of one -- which
        # is section 5's null-reading table, not a silence.
        leg_say("D6RF4_MODE_COMPLETE", mode,
                "legs_run=%s" % ",".join(_LEGS_RUN))
        MPI.COMM_WORLD.Barrier()
        return

    _require_bar_before_fd(mode)          # D6RF4-DEF-8, executable
    t0 = time.time()
    totals = prob.compute_totals(of=[J], wrt=list(DV_KEYS))
    emit({"kind": "compute_totals", "wall_s": round(time.time() - t0, 3)})
    jadj = {}
    for dv in DV_KEYS:
        arr = np.atleast_1d(np.array(totals[(J, dv)]).ravel())
        jadj[dv] = [float(v) for v in arr]
        emit({"kind": "adjoint", "dv": dv, "n": int(arr.size),
              "values": [repr(float(v)) for v in arr]})

    plan = []
    for dv, idx in COMPONENTS:
        if idx >= len(jadj[dv]):
            plan.append({"dv": dv, "idx": idx, "status": "ABSENT", "n_available": len(jadj[dv])})
            continue
        j = abs(jadj[dv][idx])
        rungs = LADDER[dv]
        cl_pred = [(s, j * s / eta) for s in rungs]
        usable = [s for (s, c) in cl_pred if c >= CLEARANCE_FLOOR]
        if not usable:
            plan.append({"dv": dv, "idx": idx, "status": "NEAR_ZERO", "J_adj": repr(jadj[dv][idx]),
                         "clearance_by_rung": [[s, c] for (s, c) in cl_pred],
                         "max_clearance": max(c for (_, c) in cl_pred)})
            continue
        s_lo = min(usable)
        hi = [s for s in rungs if s >= RATIO_MIN * s_lo]
        if not hi:
            plan.append({"dv": dv, "idx": idx, "status": "NO_S_HI", "s_lo": s_lo, "J_adj": repr(jadj[dv][idx])})
            continue
        s_hi = min(hi)
        plan.append({"dv": dv, "idx": idx, "status": "PLANNED", "s_lo": s_lo, "s_hi": s_hi,
                     "J_adj": repr(jadj[dv][idx]), "C_lo": j * s_lo / eta, "C_hi": j * s_hi / eta})
    emit({"kind": "plan", "plan": plan, "clearance_floor": CLEARANCE_FLOOR,
          "ratio_min": RATIO_MIN, "ladder": LADDER})
    _state["adjoint"] = {k: [repr(v) for v in vs] for k, vs in jadj.items()}
    _state["plan"] = plan
    _write_out()

    base = {k: np.array(dvs[k], dtype=float) for k in DV_KEYS}

    def set_perturbed(dv, idx, delta):
        for k in DV_KEYS:
            prob.set_val(k, base[k].copy())
        v = base[dv].copy()
        v[idx] += delta
        prob.set_val(dv, v)

    rows = []
    for p in plan:
        if p["status"] != "PLANNED":
            rows.append(dict(p, fd={}))
            continue
        dv, idx = p["dv"], p["idx"]
        fd = {}
        for label in ("s_lo", "s_hi"):
            s = p[label]
            try:
                set_perturbed(dv, idx, +s)
                jp, pp = primal("%s[%d]+%g" % (dv, idx, s))
                set_perturbed(dv, idx, -s)
                jm, pm = primal("%s[%d]-%g" % (dv, idx, s))
                d = (jp - jm) / (2.0 * s)
                fd[label] = {"step": s, "d": repr(d), "J_plus": repr(jp), "J_minus": repr(jm),
                             "points_plus": pp, "points_minus": pm, "ok": True}
            except Exception as exc:                      # noqa: BLE001
                fd[label] = {"step": s, "ok": False, "error": repr(exc)[:400]}
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "which": label, "row": fd[label]})
        rows.append(dict(p, fd=fd))
        _state["rows"] = rows
        _state["n_rows"] = len(rows)
        _write_out()                     # DEF-7: partial rows are on disk
    for k in DV_KEYS:
        prob.set_val(k, base[k].copy())

    _state["rows"] = rows
    _state["n_rows"] = len(rows)
    _write_out()
    if rank == 0:
        # RETAINED FOR THE READER, and it is now a RE-STATEMENT of what has
        # already been on disk since the baseline primal rather than the first
        # and only write.  `_write_out()` above has already produced this file.
        out = dict(_state)
        out.update({
            "producer_md5": got,
            "components_requested": [[d, i] for (d, i) in COMPONENTS],
            "n_components_requested": len(COMPONENTS),
            "J_baseline": repr(j0), "J_baseline_repeat": repr(j0r),
            "points_baseline": per0, "points_baseline_repeat": per0r,
            # ---- PREREGISTRATION.md section 2a's REGISTERED SOURCE ---------
            # `points.<pt>.CD` is the path section 2a names.  The parent
            # (d6rf2_fd_endpoint.py:204) wrote this block ONLY under
            # `points_baseline`, so the registered path did not exist in the
            # product.  It exists here, and it is the SAME OBJECT as
            # `points_baseline` -- not a second measurement, not a copy taken
            # at a different time.  `points_baseline` is retained UNCHANGED
            # because falsifier F1 reads it against `points_baseline_repeat`.
            "points": per0,
            "points_source": "FD_BASELINE_PRIMAL",
            "points_source_statement": (
                "CD_i(mp) is prob.get_val('<pt>.aero_post.CD') in the "
                "`baseline` primal of this program, at the endpoint design "
                "vector reconstructed to PHYSICAL units. It is NOT the last "
                "accepted major of D6R's optimisation (D6RF section 0a's "
                "quantity), and no result carrying it may be compared to a "
                "D6R- or D6RF-era CD_i(mp) without this label travelling with "
                "the number (DAFOAM_CHARTER.md section 18.6 refinement 2)."),
            "optimality_claim": (
                "NONE. The producing optimisation exited `Invalid number in "
                "NLP function or derivative detected.` and 687 of its 863 "
                "recorded funcs rows are non-finite (D6RF3-DEF-5). This is a "
                "design point, not an optimum."),
            "eta_raw": repr(eta_raw), "eta_used": repr(eta), "eta_floored": eta_flagged,
            "clearance_floor": CLEARANCE_FLOOR, "ratio_min": RATIO_MIN,
            "plateau_tol_pct": PLATEAU_TOL, "ladder": LADDER,
            "adjoint": {k: [repr(v) for v in vs] for k, vs in jadj.items()},
            "rows": rows, "n_rows": len(rows),
        })
        tmp = out_path + ".partial"
        with open(tmp, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, out_path)
        leg_say("D6RF4_FD_ENDPOINT_WRITTEN", out_path, "n_rows=%d" % len(rows))
    leg_say("D6RF4_MODE_COMPLETE", mode, "legs_run=%s" % ",".join(_LEGS_RUN))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=list(MODES),
                    help="P_conv = baseline + baseline_repeat and STOP; "
                         "F5_loose = baseline only at D6RF3's original "
                         "fvSolution (falsifier F5); full = the parent "
                         "program, PRICED BUT NOT BOUGHT at this freeze")
    main(ap.parse_args().mode)
