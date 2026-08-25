#!/usr/bin/env python
"""Curriculum D7 -- endpoint finite-difference table producer.

DAFOAM_CHARTER.md sec.1 (THE LINE): a DAFoam gradient is not a result until an
FD table stands beside it at a step PROVED to lie in the plateau.  For an
OPTIMISATION that table is measured AT THE FINAL DESIGN POINT, not at the
baseline.  D7 buys this table on BOTH toolchain rows (arms F-S and F-P) --
DAFOAM_CHARTER.md sec.6, PREREGISTRATION.md sec.9b.

Rules this file obeys, all frozen in PREREGISTRATION.md before it ran:

  * THE MODEL DEFINITION IS NOT COPIED.  This file reads the frozen producer
    `d7_opt_runScript.py`, ASSERTS its md5, splits it at the literal anchor
    `# OpenMDAO setup`, and execs the header.  daOptions, Top, the DVs and the
    constraints are therefore the PRODUCER'S OWN BYTES.  A copy could drift
    from the thing under test; this cannot.
  * EVERY graded number is written to a FILE by rank 0 and fsynced.  Nothing
    graded is recovered from stdout (A2/per_component_table sec.2.2, 79679a84).
  * THE STEP IS CHOSEN MECHANICALLY, from the stored |J_adj| and the MEASURED
    eta and from nothing else -- PREREGISTRATION.md sec.7:
        s_lo = smallest ladder rung with C = |J_adj|*s/eta >= 5
        s_hi = smallest rung with s_hi >= 2*s_lo
        eta  = |CD(baseline) - CD(baseline repeated)|, measured in THIS
               invocation.  N-D15: bands are sized from MEASURED repeat-noise,
               never assumed.
  * THE LADDER IS ANCHORED ON A3 RUNG 2's OWN measured usable step h = 1e-2 on
    THIS mesh -- NOT on A2's 1e-3, which belongs to a different case
    (PREREGISTRATION.md sec.5).
  * A STEP THAT FAILS TO PRODUCE A CONVERGED PRIMAL IS RECORDED AS A
    FAILED-STEP ROW, NEVER DROPPED (DAFOAM_CHARTER.md sec.3).  Shock-induced
    primal fragility at deformed transonic shapes is a NAMED failure mode for
    this case, so failed steps are EXPECTED and their rows are evidence.

REGISTERED LIMITATION, CARRIED VERBATIM from the step-selection rule's own
record (A6/rung_n16_remaining_components/RESULTS.md sec.3.1):

    "One item, five components, one case, one eta.  The rule has not been tried
     where the proxy |J_adj| is itself wrong -- which is the case it would be
     worst at, since it sizes the step from the very quantity under test."

On a rung whose adjoint is wrong, the |J_adj| proxy sizes steps from a wrong
number.  That is the standing limitation and D7 DOES NOT REPAIR IT.
"""
import hashlib
import json
import os
import sys
import time

PRODUCER = "d7_opt_runScript.py"
PRODUCER_MD5 = "e43902ed2cfc99022c6e21e075f88695"
ANCHOR = "# OpenMDAO setup"

# ---- registered constants (PREREGISTRATION.md sec.4 band E, sec.5, sec.7) ---
CLEARANCE_FLOOR = 5.0     # sec.6a: C = |J|*s/eta must reach this
RATIO_MIN = 2.0           # sec.7: s_hi is the smallest rung >= 2*s_lo
PLATEAU_TOL = 10.0        # sec.4 band E, percent
ETA_FLOOR = 1.0e-14       # a measured eta below this is replaced and FLAGGED
# sec.5 -- anchored on rung 2's own measured usable step 1e-2 / 2h = 2e-2
LADDER = {
    "shape":  [3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1],
    "twist":  [3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1],
    "patchV": [3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1],
}
# ---- THE FIVE COMPONENTS, NAMED IN ADVANCE (PREREGISTRATION.md sec.6) ------
# 1 shape[115] : graded on BOTH rows at rung 2; the one the rotation patch
#                DEGRADED 9.208x (0.0172 % -> 0.1586 %).  Crosses the warp.
# 2 twist[1]   : graded on both rows; DEGRADED 3.39x (0.2740 % -> 0.9279 %);
#                a rot_z on the reference axis -- crosses the rotation path
#                DIRECTLY.
# 3 patchV[1]  : AoA -- the DV the CL equality is carried by, and the control
#                that does NOT cross the warp chain; bit-identical at rung 2.
# 4 shape[0]   : unflagged control, chosen BY INDEX POSITION (first of 120).
# 5 shape[119] : second unflagged control, last of 120 -- same mechanical rule.
COMPONENTS = [
    ("shape", 115),
    ("twist", 1),
    ("patchV", 1),
    ("shape", 0),
    ("shape", 119),
]
DVKEYS = ("twist", "shape", "patchV")
SIZES = {"twist": 5, "shape": 120, "patchV": 2}

OUT = "d7_fd_endpoint.json"
JSONL = "d7_fd_endpoint.jsonl"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def main():
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("D7_FD REFUSE producer md5 %s != frozen %s\n"
                         % (got, PRODUCER_MD5))
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D7_FD REFUSE anchor %r appears %d times\n"
                         % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d7_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    Top = ns["Top"]

    def emit(rec):
        if rank != 0:
            return
        with open(JSONL, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    with open("d7_endpoint_dvs.json") as fh:
        dvs = json.load(fh)
    for key in DVKEYS:
        if key not in dvs:
            sys.stderr.write("D7_FD REFUSE endpoint dv file missing %s\n" % key)
            sys.exit(2)
        if len(dvs[key]) != SIZES[key]:
            sys.stderr.write("D7_FD REFUSE endpoint %s has %d components, "
                             "registered %d\n" % (key, len(dvs[key]), SIZES[key]))
            sys.exit(2)
        prob.set_val(key, np.array(dvs[key], dtype=float))
    emit({"kind": "endpoint_dvs", "source": dvs.get("_source"),
          "n_twist": len(dvs["twist"]), "n_shape": len(dvs["shape"]),
          "n_patchV": len(dvs["patchV"])})

    CD = "scenario1.aero_post.CD"
    CL = "scenario1.aero_post.CL"

    def primal(tag):
        t0 = time.time()
        prob.run_model()
        cd = float(prob.get_val(CD)[0])
        cl = float(prob.get_val(CL)[0])
        emit({"kind": "primal", "tag": tag, "CD": repr(cd), "CL": repr(cl),
              "wall_s": round(time.time() - t0, 3)})
        return cd, cl

    cd0, cl0 = primal("baseline")
    cd0r, cl0r = primal("baseline_repeat")

    eta_raw = abs(cd0 - cd0r)
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flagged, "CD_baseline": repr(cd0),
          "CD_repeat": repr(cd0r), "CL_baseline": repr(cl0),
          "CL_repeat": repr(cl0r)})

    t0 = time.time()
    totals = prob.compute_totals(of=[CD], wrt=list(DVKEYS))
    emit({"kind": "compute_totals", "wall_s": round(time.time() - t0, 3)})
    jadj = {}
    for dv in DVKEYS:
        arr = np.atleast_1d(np.array(totals[(CD, dv)]).ravel())
        jadj[dv] = [float(v) for v in arr]
        emit({"kind": "adjoint", "dv": dv, "n": int(arr.size),
              "values": [repr(float(v)) for v in arr]})

    # ---- mechanical step selection ----------------------------------------
    plan = []
    for dv, idx in COMPONENTS:
        if idx >= len(jadj[dv]):
            plan.append({"dv": dv, "idx": idx, "status": "ABSENT",
                         "n_available": len(jadj[dv])})
            continue
        j = abs(jadj[dv][idx])
        rungs = LADDER[dv]
        cl_pred = [(s, j * s / eta) for s in rungs]
        usable = [s for (s, c) in cl_pred if c >= CLEARANCE_FLOOR]
        if not usable:
            # PREREGISTRATION.md sec.6a: clearance below 5 at EVERY rung ->
            # NOT A RESULT for that component; excluded from the aggregate and
            # from the coverage count, and coverage is reported as `k of 5`,
            # never as a percentage over a shrunken denominator.
            plan.append({"dv": dv, "idx": idx, "status": "NEAR_ZERO",
                         "J_adj": repr(jadj[dv][idx]),
                         "clearance_by_rung": [[s, c] for (s, c) in cl_pred],
                         "max_clearance": max(c for (_, c) in cl_pred)})
            continue
        s_lo = min(usable)
        hi = [s for s in rungs if s >= RATIO_MIN * s_lo]
        if not hi:
            plan.append({"dv": dv, "idx": idx, "status": "NO_S_HI",
                         "s_lo": s_lo, "J_adj": repr(jadj[dv][idx])})
            continue
        s_hi = min(hi)
        plan.append({"dv": dv, "idx": idx, "status": "PLANNED",
                     "s_lo": s_lo, "s_hi": s_hi,
                     "J_adj": repr(jadj[dv][idx]),
                     "C_lo": j * s_lo / eta, "C_hi": j * s_hi / eta})
    emit({"kind": "plan", "plan": plan, "clearance_floor": CLEARANCE_FLOOR,
          "ratio_min": RATIO_MIN, "ladder": LADDER})

    base = {k: np.array(dvs[k], dtype=float) for k in DVKEYS}

    def set_perturbed(dv, idx, delta):
        for k in DVKEYS:
            prob.set_val(k, base[k].copy())
        v = base[dv].copy()
        v[idx] += delta
        prob.set_val(dv, v)

    rows = []
    n_fd_steps_attempted = 0
    for p in plan:
        if p["status"] != "PLANNED":
            rows.append(dict(p, fd={}))
            continue
        dv, idx = p["dv"], p["idx"]
        fd = {}
        for label in ("s_lo", "s_hi"):
            s = p[label]
            n_fd_steps_attempted += 1
            try:
                set_perturbed(dv, idx, +s)
                cdp, clp = primal("%s[%d]+%g" % (dv, idx, s))
                set_perturbed(dv, idx, -s)
                cdm, clm = primal("%s[%d]-%g" % (dv, idx, s))
                d = (cdp - cdm) / (2.0 * s)
                fd[label] = {"step": s, "d": repr(d), "CD_plus": repr(cdp),
                             "CD_minus": repr(cdm), "CL_plus": repr(clp),
                             "CL_minus": repr(clm), "ok": True}
            except Exception as exc:                      # noqa: BLE001
                # FAILED-STEP ROW, recorded not dropped (CHARTER sec.3)
                fd[label] = {"step": s, "ok": False, "error": repr(exc)[:400]}
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "which": label,
                  "row": fd[label]})
        rows.append(dict(p, fd=fd))
    for k in DVKEYS:
        prob.set_val(k, base[k].copy())

    if rank == 0:
        out = {
            "producer_md5": got,
            "components_requested": [[d, i] for (d, i) in COMPONENTS],
            "n_components_requested": len(COMPONENTS),
            "CD_baseline": repr(cd0), "CL_baseline": repr(cl0),
            "CD_baseline_repeat": repr(cd0r), "CL_baseline_repeat": repr(cl0r),
            "eta_raw": repr(eta_raw), "eta_used": repr(eta),
            "eta_floored": eta_flagged,
            "clearance_floor": CLEARANCE_FLOOR, "ratio_min": RATIO_MIN,
            "plateau_tol_pct": PLATEAU_TOL, "ladder": LADDER,
            "adjoint": {k: [repr(v) for v in vs] for k, vs in jadj.items()},
            "rows": rows,
            "n_rows": len(rows),
            "n_fd_steps_attempted": n_fd_steps_attempted,
        }
        with open(OUT, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("D7_FD_ENDPOINT_WRITTEN %s n_rows=%d fd_steps=%d\n"
                         % (OUT, len(rows), n_fd_steps_attempted))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
