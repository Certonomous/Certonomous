#!/usr/bin/env python
"""Curriculum D6RF6 -- the CONVERGENCE PROBE `P_conv`, and (in `full` mode)
the endpoint finite-difference spot-check of the composite J, on the
NON-ORTHOGONAL-CORRECTION repair (successor to D6RF5, BLOCKED).

Supersedes: D6RF5 (BLOCKED -- harness defect, not physics).

DERIVED FROM `curriculum_D6RF5/d6rf5_fd_endpoint.py`
(md5 `1c045eb598267252f1900f72c0601b1b`, verified on disk before this file was
written) with ONE REGISTERED DELTA over D6RF5 -- the P_conv baseline-primal
GUARD (`D6RF6 PREREGISTRATION.md` section 2), enumerated in
`d6rf6_fd_endpoint_DELTAS_from_d6rf5.diff` beside this file.  D6RF5's P_conv arm
graded BLOCKED because THIS baseline primal was UNGUARDED while the F5_scheme
path above already caught DAFoam's post-`End` `Primal solution failed!`
AnalysisError: the physically-EXPECTED over-floor plateau (p first-solve
initRes 1.62e-05 > the 1.0e-05 accept floor) raised through the unguarded call
and aborted the run before the product json was written, so the grader refused
at G1 (product absent).  THE ACCEPT FLOOR IS NOT MOVED (N-D43); the numerics,
the gate, and the LIMITED fvSchemes + nNonOrthogonalCorrectors 3 scheme are
CARRIED BYTE-IDENTICAL -- this successor changes only the harness's SURVIVAL of
the expected refusal so the grader can grade the expected G-CONV GATE FAIL.
The FD MACHINERY IS CARRIED VERBATIM.  The D6RF5-over-D6RF4 deltas, still in
force, are:

  R1  REPRESENTATIVE DV = `shape[46]`, SINGLE (section 10.3).  `COMPONENTS` is
      reduced from the lineage's five named components to the one interior FFD
      shape control point section 10.3 fixes -- high index, away from the LE/TE
      corner where `getRotationMatrix3d`'s degenerate branch fires.  NO
      SUBSTITUTION: if `shape[46]`'s adjoint fails the clearance floor (plan
      status `NEAR_ZERO`/`NO_S_HI`), G-FD reads NOT A RESULT and a SUCCESSOR
      re-registers a different component; the step/DV is NEVER re-chosen after
      seeing which one agrees (DAFOAM_CHARTER.md section 3).

  R2  THE 2-POINT CLEARANCE/RATIO MINI-SWEEP IS CARRIED VERBATIM (section 10.3
      [H-SET]).  `CLEARANCE_FLOOR = 5.0`, `RATIO_MIN = 2.0`, `PLATEAU_TOL = 10.0`,
      `ETA_FLOOR = 1e-14`, `LADDER["shape"] = {1e-3, 3e-3, 1e-2, 3e-2}` are the
      lineage bytes.  This is NOT a 5-step full-ladder rule: clearance selects
      `s_lo`, ratio selects `s_hi`, the pair is graded.  Section 10.2 REJECTS
      the draft `{1e-2..1e-6}`/`1%` as mis-sized below the shape-DV harness floor
      and registers this proven machinery instead.

  R3  `F5_scheme` REPLACES `F5_loose`.  D6RF6's falsifier F5 re-runs the baseline
      primal at D6RF4's SCHEME (laplacianSchemes `Gauss linear corrected`,
      snGradSchemes `corrected`, nNonOrthogonalCorrectors 1 -- installed by the
      LAUNCHER via d6rf6_fvSchemes_D6RF4_ORIGINAL, not by this script), everything
      else held.  Its REGISTERED PREDICTED DATUM is the p FIRST-solve initRes
      1.658293702e-05 (MEASURED, D6RF4 P_conv log :2107), 1.658x the 1.0e-05
      floor: `1.658e-05 > 1.0e-05` FAILS G-CONV by 1.658x at zero extra compute
      (section 5).  A refusal here is the prediction landing, not the arm
      crashing; the accept floor is NOT moved to make it happen.

  N4  LEG MARKERS, CARRIED.  Each leg prints `D6RF6_LEG_BEGIN <leg>` /
      `D6RF6_LEG_END <leg> ...`, which is how the GRADER splits one container log
      into per-leg segments.

  N5  THE PER-FIELD G-CONV FIRST-P-SOLVE EXTRACTION LIVES IN THE GRADER, NOT
      HERE (a deliberate design choice, disclosed).  DAFoam prints the p solve
      once per corrector as `p initRes: <X> finalRes: <Y> nIters: <n>` (D6RF4
      log :2107 first/uncorrected = binding, :2108..last corrected); with
      nNonOrthogonalCorrectors 3 there are FOUR such lines per outer iteration.
      `d6rf6_grade.py:read_legs` records the FIRST p line of the final Time block
      as `p_first_uncorrected` and the LAST as `p_corrected`, and `gate_conv`
      grades both against the floor.  Those lines only exist in the container log
      the grader parses; this script's contribution to G-CONV is the leg markers
      (N4) that make the per-corrector p lines segmentable -- putting a second
      log parser here would violate the single-reader discipline the controls
      rest on (CLAUDE.md rule 3).  This is stated so the omission is deliberate,
      not an oversight of section 3.1.

INHERITED VERBATIM below this line (the DEF-7/DEF-8 incremental-write and
bar-before-FD repairs, the emit/plan/FD logic, and the A6 step-rule limitation)
are D6RF4's bytes, unchanged in shape.  EVERY graded number is written to a FILE
by rank 0.
"""
import argparse
import hashlib
import json
import os
import sys
import time

PRODUCER = "d6rf6_opt_runScript.py"
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
    # PREREGISTRATION.md section 10.3: the SINGLE registered representative DV.
    # NO SUBSTITUTION -- if shape[46]'s adjoint is NEAR_ZERO/NO_S_HI the plan
    # marks it so and G-FD reads NOT A RESULT (a successor re-registers a
    # different component; the DV is never re-chosen after seeing agreement).
    ("shape", 46),
]
DV_KEYS = ("twist", "shape", "patchV_cl04", "patchV_cl05", "patchV_cl06")
OUT = "d6rf6_fd_endpoint.json"
JSONL = "d6rf6_fd_endpoint.jsonl"

# ---------------------------------------------------------------- section 8.2
# THE REGISTERED LEGS.  `P_conv` is the ONLY arm registered at this freeze and
# it runs L1 then L3; L2 is inside L1's mode.  `full` is priced but NOT bought
# (PREREGISTRATION.md section 8.2), and is kept here so the successor that buys
# it inherits one file rather than a re-derivation.
MODES = ("P_conv", "F5_scheme", "full")
MODE_OUT = {"P_conv": OUT, "F5_scheme": "d6rf6_f5_endpoint.json", "full": OUT}
MODE_JSONL = {"P_conv": JSONL, "F5_scheme": "d6rf6_f5_endpoint.jsonl",
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
            "D6RF6_FD REFUSE mode=%s reached an FD leg with legs_run=%r -- "
            "`%s` has not run, so `eta_raw` does not exist and F1's bar would "
            "be UNRESOLVED with FD rows already bought. Order refused.\n"
            % (mode, _LEGS_RUN, BAR_LEG))
        sys.exit(2)


def main(mode):
    if mode not in MODES:
        sys.stderr.write("D6RF6_FD REFUSE unknown mode %r; registered: %r\n"
                         % (mode, MODES))
        sys.exit(2)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("D6RF6_FD REFUSE producer md5 %s != frozen %s\n" % (got, PRODUCER_MD5))
        sys.exit(2)
    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D6RF6_FD REFUSE anchor %r appears %d times\n" % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]
    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d6rf6_frozen_header", "__file__": PRODUCER}
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

    with open("d6rf6_endpoint_dvs.json") as fh:
        dvs = json.load(fh)
    for key in DV_KEYS:
        if key not in dvs:
            sys.stderr.write("D6RF6_FD REFUSE endpoint dv file missing %s\n" % key)
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
            "THE ONLY THING D6RF6 CHANGES ABOUT THE PRIMAL IS THE LINEAR-"
            "SOLVER STOPPING RULE IN system/fvSolution, and it TIGHTENS it. "
            "primalMinResTol (1e-08) and primalMinResTolDiff (1000) are "
            "carried forward byte-identical, so the accept floor is 1.0e-05 "
            "in every leg of this item. d6rf6_accept_floor_control.py reads "
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
        leg_say("D6RF6_FD_ENDPOINT_WRITTEN", out_path,
                "legs_run=%s" % ",".join(_LEGS_RUN),
                "n_rows=%d" % len(_state.get("rows", [])))

    def primal(tag):
        t0 = time.time()
        leg_say("D6RF6_LEG_BEGIN", tag, "mode=%s" % mode)
        prob.run_model()
        j = float(prob.get_val(J)[0])
        per = {}
        for pt in POINTS:
            per[pt] = {"CD": repr(float(prob.get_val("%s.aero_post.CD" % pt)[0])),
                       "CL": repr(float(prob.get_val("%s.aero_post.CL" % pt)[0]))}
        emit({"kind": "primal", "tag": tag, "J": repr(j), "points": per,
              "wall_s": round(time.time() - t0, 3)})
        _LEGS_RUN.append(tag)
        leg_say("D6RF6_LEG_END", tag, "mode=%s" % mode, "J=%r" % j,
                "wall_s=%.3f" % (time.time() - t0), "primal_raised=False")
        return j, per

    # ================= LEG 1 / LEG 3: THE BASELINE PRIMAL ===================
    # In `F5_scheme` this is falsifier F5 at D6RF4's ORIGINAL SCHEME (the
    # launcher stages d6rf6_fvSchemes_D6RF4_ORIGINAL + 1 corrector before it)
    # and its registered prediction is that DAFoam refuses it post-`End` at the
    # p first-solve 1.658293702e-05.  That refusal is F5's DATUM (section 5),
    # not the arm crashing, so it is caught, recorded and reported -- and the
    # accept floor it fails against is NOT moved to let it through.
    if mode == "F5_scheme":
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
                               "F5 is the DELIBERATELY WRONG SCHEME and its "
                               "registered predicted value, 1.658293702e-05, "
                               "FAILS G-CONV's own bar of 1.0e-05 by 1.658x. A "
                               "refusal here is the prediction landing, not "
                               "the arm failing. The per-field residuals the "
                               "gate actually reads are in this leg's own log "
                               "segment, between its LEG_BEGIN and LEG_END "
                               "markers.")})
            emit({"kind": "primal_raised", "tag": "baseline", "mode": mode,
                  "error": repr(exc)[:800]})
            leg_say("D6RF6_LEG_END", "baseline", "mode=%s" % mode,
                    "primal_raised=True")
        _write_out()
        leg_say("D6RF6_MODE_COMPLETE", mode,
                "legs_run=%s" % ",".join(_LEGS_RUN))
        MPI.COMM_WORLD.Barrier()
        return

    # ===== D6RF6 DELTA vs D6RF5 (Supersedes D6RF5, BLOCKED) ==============
    # THE ONE SUBSTANTIVE CHANGE OF THIS SUCCESSOR.  In D6RF5 this baseline
    # primal was UNGUARDED while the F5_scheme path above already caught
    # DAFoam's post-`End` `Primal solution failed!` AnalysisError.  D6RF5's
    # P_conv arm therefore CRASHED to BLOCKED: the physically-EXPECTED
    # over-floor plateau (p first-solve initRes 1.62e-05 > the 1.0e-05 accept
    # floor) raised through this unguarded call and aborted the run before
    # d6rf6_fd_endpoint.json was written, so the grader refused at G1 (product
    # absent).  The refusal is the PREDICTION LANDING, not the arm crashing;
    # the binding p lines the gate reads live in this leg's log segment.  This
    # DELTA wraps the baseline the SAME way the F5_scheme path is wrapped: it
    # records primal_raised + the error, STILL writes the product, and
    # completes the mode so the grader can GRADE the expected G-CONV GATE
    # FAIL.  The accept floor is NOT moved (N-D43); the numerics and the gate
    # are UNCHANGED.
    try:
        j0, per0 = primal("baseline")
        # ---- THE DEF-7 WRITE POINT.  `points.<pt>.CD` IS ON DISK HERE,
        # ---- BEFORE ANY FD LEG AND BEFORE compute_totals.  `points` and
        # ---- `points_baseline` are THE SAME OBJECT, not a second measurement.
        _state.update({"J_baseline": repr(j0), "points_baseline": per0,
                       "points": per0, "primal_raised": False})
        _write_out()
    except Exception as exc:                                   # noqa: BLE001
        _LEGS_RUN.append("baseline_RAISED")
        _state.update({"J_baseline": None, "points": {},
                       "primal_raised": True,
                       "primal_error": repr(exc)[:800],
                       "primal_raised_statement": (
                           "The P_conv baseline is the CONVERGENCE PROBE. Its "
                           "registered predicted binding datum -- p first-solve "
                           "initRes 1.625570732e-05 (D6RF5 P_conv log) -- FAILS "
                           "G-CONV's bar of 1.0e-05 by ~1.63x, so DAFoam raises "
                           "`Primal solution failed!` after `End`. A refusal "
                           "here is the prediction landing, not the arm failing. "
                           "The per-field residuals the gate actually reads are "
                           "in this leg's own log segment, between its LEG_BEGIN "
                           "and LEG_END markers.")})
        emit({"kind": "primal_raised", "tag": "baseline", "mode": mode,
              "error": repr(exc)[:800]})
        leg_say("D6RF6_LEG_END", "baseline", "mode=%s" % mode,
                "primal_raised=True")
        _write_out()
        leg_say("D6RF6_MODE_COMPLETE", mode,
                "legs_run=%s" % ",".join(_LEGS_RUN))
        MPI.COMM_WORLD.Barrier()
        return

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
        # THE REGISTERED ARM STOPS HERE.  D6RF6 buys a CONVERGENCE measurement,
        # not a gradient: section 8.2 prices the full FD arm at 934 core-min at
        # the tightened settings and refuses to buy a 934 core-min arm to learn
        # a 17.9 core-min fact.  G-FD, band D, G-OFF and G-PRICE therefore have
        # NO INPUTS in this arm and read NOT A RESULT for want of one -- which
        # is section 5's null-reading table, not a silence.
        leg_say("D6RF6_MODE_COMPLETE", mode,
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
        leg_say("D6RF6_FD_ENDPOINT_WRITTEN", out_path, "n_rows=%d" % len(rows))
    leg_say("D6RF6_MODE_COMPLETE", mode, "legs_run=%s" % ",".join(_LEGS_RUN))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=list(MODES),
                    help="P_conv = baseline + baseline_repeat and STOP; "
                         "F5_scheme = baseline only at D6RF4's original "
                         "SCHEME (falsifier F5); full = the parent "
                         "program, PRICED BUT NOT BOUGHT at this freeze")
    main(ap.parse_args().mode)
