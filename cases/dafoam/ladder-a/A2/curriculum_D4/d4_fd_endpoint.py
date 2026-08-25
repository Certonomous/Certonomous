#!/usr/bin/env python
"""Curriculum D4 -- endpoint finite-difference spot-check producer.

DAFOAM_CHARTER.md §2 and §9: an adjoint gradient is not a result until an FD
table stands beside it, and for an OPTIMISATION that table is measured AT THE
FINAL DESIGN POINT, not at the baseline.

Design rules this file obeys, all registered in PREREGISTRATION.md before it ran:

  * The model definition is NOT copied.  This file reads the frozen producer
    `d4_opt_runScript.py`, asserts its md5, splits it at the literal anchor
    line `# OpenMDAO setup`, and execs the header.  The daOptions, the Top
    class, the DVs and the constraints are therefore the producer's own bytes.
    A copy could drift; this cannot.
  * EVERY graded number is written to a FILE by rank 0 and is never recovered
    from stdout.  MPI log splicing on this exact case is MEASURED
    (`cases/dafoam/ladder-a/A2/per_component_table/RESULTS.md` §2.2, commit
    79679a84): four ranks interleave on one stdout and sever arrays mid-number.
  * The step is chosen by the mechanical rule of
    `cases/dafoam/ladder-a/A6/rung_n16_remaining_components/RESULTS.md` §3.1
    from the stored |J_adj| and the MEASURED eta and from nothing else.
    That rule carries its own registered limitation VERBATIM:
      "One item, five components, one case, one eta.  The rule has not been
       tried where the proxy |J_adj| is itself wrong -- which is the case it
       would be worst at, since it sizes the step from the very quantity under
       test."
    On a rung whose adjoint is wrong, the |J_adj| proxy sizes steps from a
    wrong number.  That limitation is inherited here unchanged.
"""
import hashlib
import json
import os
import sys
import time

PRODUCER = "d4_opt_runScript.py"
PRODUCER_MD5 = "2906d52a5dbed2bacbaeaf85a37d3fe8"
ANCHOR = "# OpenMDAO setup"

# ---- registered constants (frozen in PREREGISTRATION.md §5 and §7) --------
CLEARANCE_FLOOR = 5.0        # C = |J|*s/eta must reach this for a step to be usable
RATIO_MIN = 2.0              # s_hi is the smallest rung with s_hi >= RATIO_MIN * s_lo
PLATEAU_TOL = 10.0           # percent; |d(s_hi)-d(s_lo)|/|d(s_hi)|
ETA_FLOOR = 1.0e-14          # a measured eta below this is replaced by this and FLAGGED
LADDER = {
    "shape":  [1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2],
    "twist":  [1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1],
    "patchV": [1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1],
}
# The FIVE named components.  NAMED IN ADVANCE, in the pre-registration, with
# their reasons and their verdict mapping.  idx46 of `shape` is the
# idx46-class near-zero component (A1 idx6 / A5 idx16 / A2 idx46 family).
COMPONENTS = [
    ("shape", 46),
    ("shape", 18),
    ("shape", 0),
    ("twist", 0),
    ("patchV", 1),
]

OUT = "d4_fd_endpoint.json"
JSONL = "d4_fd_endpoint.jsonl"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def main():
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("D4_FD REFUSE producer md5 %s != frozen %s\n"
                         % (got, PRODUCER_MD5))
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D4_FD REFUSE anchor %r appears %d times\n"
                         % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]

    # the producer header parses sys.argv; give it the registered task
    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d4_frozen_header", "__file__": PRODUCER}
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

    # ---- endpoint design variables, read from a FILE -----------------------
    with open("d4_endpoint_dvs.json") as fh:
        dvs = json.load(fh)
    for key in ("twist", "shape", "patchV"):
        if key not in dvs:
            sys.stderr.write("D4_FD REFUSE endpoint dv file missing %s\n" % key)
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

    # ---- analytic (adjoint) gradient at the endpoint ------------------------
    t0 = time.time()
    totals = prob.compute_totals(of=[CD], wrt=["twist", "shape", "patchV"])
    emit({"kind": "compute_totals", "wall_s": round(time.time() - t0, 3)})
    jadj = {}
    for dv in ("twist", "shape", "patchV"):
        arr = np.atleast_1d(np.array(totals[(CD, dv)]).ravel())
        jadj[dv] = [float(v) for v in arr]
        emit({"kind": "adjoint", "dv": dv, "n": int(arr.size),
              "values": [repr(float(v)) for v in arr]})

    # ---- mechanical step selection, from |J_adj| and eta and nothing else ---
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

    # ---- central finite differences at the planned steps -------------------
    base = {"twist": np.array(dvs["twist"], dtype=float),
            "shape": np.array(dvs["shape"], dtype=float),
            "patchV": np.array(dvs["patchV"], dtype=float)}

    def set_perturbed(dv, idx, delta):
        for k in ("twist", "shape", "patchV"):
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
                cdp, clp = primal("%s[%d]+%g" % (dv, idx, s))
                set_perturbed(dv, idx, -s)
                cdm, clm = primal("%s[%d]-%g" % (dv, idx, s))
                d = (cdp - cdm) / (2.0 * s)
                fd[label] = {"step": s, "d": repr(d), "CD_plus": repr(cdp),
                             "CD_minus": repr(cdm), "CL_plus": repr(clp),
                             "CL_minus": repr(clm), "ok": True}
            except Exception as exc:                      # noqa: BLE001
                fd[label] = {"step": s, "ok": False, "error": repr(exc)[:400]}
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "which": label,
                  "row": fd[label]})
        rows.append(dict(p, fd=fd))
    # restore
    for k in ("twist", "shape", "patchV"):
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
        }
        with open(OUT, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("D4_FD_ENDPOINT_WRITTEN %s n_rows=%d\n"
                         % (OUT, len(rows)))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
