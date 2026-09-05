#!/usr/bin/env python
"""Curriculum D6RF3 -- endpoint finite-difference spot-check of the COMPOSITE J,
AND the registered producer of `CD_i(mp)`.

DERIVED FROM `curriculum_D6RF2/d6rf2_fd_endpoint.py`
(md5 `0ce81a0b038abe12728b5b062e4420df`, verified on disk before this file was
written) with the REGISTERED DELTAS of `D6RF3 PREREGISTRATION.md` section 2a,
enumerated in `d6rf3_fd_endpoint_DELTAS_from_d6rf2.diff` beside this file:

  * PRODUCER is this item's own staged `d6rf3_opt_runScript.py`.  ITS md5 IS
    UNCHANGED at `137539e0a99be27f27fdb69e063b2a87` -- the staged copy is
    BYTE-IDENTICAL to `D6RF2`'s, deliberately, so that `G-ANCHOR`'s single-
    occurrence assertion on `# OpenMDAO setup` (`D6RF-BLOCKING-1`'s repair)
    carries over unaltered rather than being re-established.
  * PRODUCTS carry this item's names: `d6rf3_fd_endpoint.json` / `.jsonl`, and
    the endpoint DVs are read from `d6rf3_endpoint_dvs.json`.
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
import hashlib
import json
import os
import sys
import time

PRODUCER = "d6rf3_opt_runScript.py"
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
OUT = "d6rf3_fd_endpoint.json"
JSONL = "d6rf3_fd_endpoint.jsonl"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def main():
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("D6RF3_FD REFUSE producer md5 %s != frozen %s\n" % (got, PRODUCER_MD5))
        sys.exit(2)
    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D6RF3_FD REFUSE anchor %r appears %d times\n" % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]
    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d6rf3_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    Top = ns["Top"]
    POINTS = ns["POINTS"]

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

    with open("d6rf3_endpoint_dvs.json") as fh:
        dvs = json.load(fh)
    for key in DV_KEYS:
        if key not in dvs:
            sys.stderr.write("D6RF3_FD REFUSE endpoint dv file missing %s\n" % key)
            sys.exit(2)
        prob.set_val(key, np.array(dvs[key], dtype=float))
    emit({"kind": "endpoint_dvs", "source": dvs.get("_source"),
          "n_twist": len(dvs["twist"]), "n_shape": len(dvs["shape"]),
          "n_patchV": {pt: len(dvs["patchV_" + pt]) for pt in POINTS}})

    J = "obj.J"

    def primal(tag):
        t0 = time.time()
        prob.run_model()
        j = float(prob.get_val(J)[0])
        per = {}
        for pt in POINTS:
            per[pt] = {"CD": repr(float(prob.get_val("%s.aero_post.CD" % pt)[0])),
                       "CL": repr(float(prob.get_val("%s.aero_post.CL" % pt)[0]))}
        emit({"kind": "primal", "tag": tag, "J": repr(j), "points": per,
              "wall_s": round(time.time() - t0, 3)})
        return j, per

    j0, per0 = primal("baseline")
    j0r, per0r = primal("baseline_repeat")
    eta_raw = abs(j0 - j0r)
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flagged, "J_baseline": repr(j0), "J_repeat": repr(j0r)})

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
    for k in DV_KEYS:
        prob.set_val(k, base[k].copy())

    if rank == 0:
        out = {
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
        }
        with open(OUT, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("D6RF3_FD_ENDPOINT_WRITTEN %s n_rows=%d\n" % (OUT, len(rows)))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
