#!/usr/bin/env python
"""D4S-F3S -- endpoint finite-difference producer with the STATIONARITY
ACCEPTANCE RULE (`d4s_f3s_accept.py`) applied to EVERY primal, in-container,
on both rows under ONE rule.

Derived from curriculum_D4's frozen `d4_fd_endpoint.py` (md5 c6112b0e...) --
the model definition, the five registered components, the step ladder, the
clearance rule, the plateau tolerance, the central differences and every
output field are UNCHANGED (the DELTAS diff beside this file is the whole
difference).  What is added, and only this:

  (1) THE PRODUCER'S THRESHOLD CLAUSE IS DISARMED, NOT LOOSENED.  The exec'd
      frozen header's `daOptions["primalMinResTolDiff"]` is set to
      DISARM_TOL_DIFF = 1.0e12 (accept floor 1e-8 x 1e12 = 1e4 -- a value no
      run that reached endTime can exceed), and the EFFECTIVE value is READ
      BACK from the DASolver after setup (planted read: a print of the intended
      value proves nothing) -- REFUSE (rc 2) if it did not take.  The rule
      that then decides every primal is (2), and it is blind to which side of
      1e-5 the residual floor sits (D4S-PREREG-DEF-1).
  (2) EVERY primal's solver output (rank 0's fd 1, at the OS level, so the C++
      `Foam::Info` stream is captured) is written to
      `d4s_f3s_primal_NNN_<tag>.log` in the work directory, re-emitted to
      stdout so the arm log still carries it, parsed, and evaluated by
      `d4s_f3s_accept.evaluate` -- R1 End + window, R2 stationarity of every
      equation's initial residual to STATIONARITY_TOL over the last
      WINDOW_ITERS, R3 continuity bounded, R4 everything finite.  One record
      per primal goes to `d4s_f3s_accept.jsonl` (rank 0, fsync).  A primal
      that is NOT accepted REFUSES the arm (rc 2) with the record written --
      the FD sweep never continues on a primal the rule rejected.  A capture
      that yields zero samples is a READER FAILURE and REFUSES (rule 3).
  (3) Output names carry the item: `d4s_f3s_fd_endpoint.json` / `.jsonl`.

The mechanism of (2) was probed in the shipped image before this file was
frozen (PREREGISTRATION.md section 3.4): C-stdio, Python and raw-fd writes all
land in the capture and stdout is restored afterwards.
NO `assert` anywhere (L-332).
"""
import ctypes
import hashlib
import json
import math
import os
import sys
import time

PRODUCER = "d4_opt_runScript.py"
PRODUCER_MD5 = "2906d52a5dbed2bacbaeaf85a37d3fe8"
ANCHOR = "# OpenMDAO setup"

# ---- registered constants (frozen in curriculum_D4 PREREGISTRATION.md section 5 and 7; UNCHANGED)
CLEARANCE_FLOOR = 5.0
RATIO_MIN = 2.0
PLATEAU_TOL = 10.0
ETA_FLOOR = 1.0e-14
LADDER = {
    "shape":  [1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2],
    "twist":  [1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1],
    "patchV": [1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1],
}
COMPONENTS = [
    ("shape", 46),
    ("shape", 18),
    ("shape", 0),
    ("twist", 0),
    ("patchV", 1),
]

# ---- D4S-F3S additions (PREREGISTRATION.md section 3)
DISARM_KEY = "primalMinResTolDiff"
DISARM_TOL_DIFF = 1.0e12
ACCEPT_MODULE = "d4s_f3s_accept.py"
OUT = "d4s_f3s_fd_endpoint.json"
JSONL = "d4s_f3s_fd_endpoint.jsonl"
ACCEPT_JSONL = "d4s_f3s_accept.jsonl"
CAPTURE_FMT = "d4s_f3s_primal_%03d_%s.log"
TAG = "D4S_F3S"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def refuse(msg, rank=0):
    if rank == 0:
        sys.stderr.write("%s REFUSE %s\n" % (TAG, msg))
        sys.stderr.flush()
    sys.exit(2)


def safe_tag(tag):
    return "".join(c if (c.isalnum() or c in "._-+") else "_" for c in tag)[:60]


def main():
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        refuse("producer md5 %s != frozen %s" % (got, PRODUCER_MD5))
    if not os.path.isfile(ACCEPT_MODULE):
        refuse("acceptance module %s absent from the work directory" % ACCEPT_MODULE)
    sys.path.insert(0, os.getcwd())
    import d4s_f3s_accept as acc

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        refuse("anchor %r appears %d times" % (ANCHOR, src.count(ANCHOR)))
    header = src.split(ANCHOR)[0]

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d4_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    # ---- (1) DISARM the producer's threshold clause in the exec'd namespace
    if not isinstance(ns.get("daOptions"), dict):
        refuse("the frozen header carries no daOptions dict")
    registered_before = ns["daOptions"].get(DISARM_KEY)
    ns["daOptions"][DISARM_KEY] = DISARM_TOL_DIFF

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    Top = ns["Top"]
    libc = ctypes.CDLL(None)

    def emit(rec, path=JSONL):
        if rank != 0:
            return
        with open(path, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    # ---- (1) READ BACK the effective option from the solver object
    dasolver = None
    try:
        dasolver = prob.model._get_subsystem("scenario1.coupling.solver").DASolver
    except Exception:                                    # noqa: BLE001
        for s in prob.model.system_iter(recurse=True):
            if hasattr(s, "DASolver"):
                dasolver = s.DASolver
                break
    if dasolver is None:
        refuse("no DASolver found under prob.model -- the disarm cannot be read back", rank)
    try:
        eff = float(dasolver.getOption(DISARM_KEY))
        tol = float(dasolver.getOption("primalMinResTol"))
    except Exception as exc:                             # noqa: BLE001
        refuse("getOption failed: %r" % (exc,), rank)
    if eff != DISARM_TOL_DIFF:
        refuse("effective %s=%r != %r -- the disarm did not take" % (DISARM_KEY, eff, DISARM_TOL_DIFF), rank)
    emit({"kind": "disarm", "key": DISARM_KEY, "registered_before": registered_before,
          "effective": eff, "primalMinResTol": tol, "producer_accept_floor_now": tol * eff,
          "note": "the producer's threshold clause cannot fire; the stationarity rule decides every primal"})
    if rank == 0:
        print("%s_DISARM %s registered_before=%r effective=%r primalMinResTol=%r" % (TAG, DISARM_KEY, registered_before, eff, tol), flush=True)

    with open("d4_endpoint_dvs.json") as fh:
        dvs = json.load(fh)
    for key in ("twist", "shape", "patchV"):
        if key not in dvs:
            refuse("endpoint dv file missing %s" % key, rank)
        prob.set_val(key, np.array(dvs[key], dtype=float))
    emit({"kind": "endpoint_dvs", "source": dvs.get("_source"), "units": dvs.get("_units"),
          "n_twist": len(dvs["twist"]), "n_shape": len(dvs["shape"]),
          "n_patchV": len(dvs["patchV"])})

    CD = "scenario1.aero_post.CD"
    CL = "scenario1.aero_post.CL"
    state = {"n": 0}

    # ---- (2) the captured, evaluated primal
    def primal(tag):
        state["n"] += 1
        n = state["n"]
        cap = CAPTURE_FMT % (n, safe_tag(tag))
        t0 = time.time()
        sys.stdout.flush(); sys.stderr.flush(); libc.fflush(None)
        fd = os.open(cap + (".rank%d" % rank if rank != 0 else ""), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
        saved = os.dup(1)
        os.dup2(fd, 1)
        err = None
        try:
            prob.run_model()
        except Exception as exc:                         # noqa: BLE001
            err = repr(exc)[:400]
        finally:
            sys.stdout.flush(); libc.fflush(None)
            os.dup2(saved, 1)
            os.close(saved)
            os.close(fd)
        wall = round(time.time() - t0, 3)
        text = open(cap if rank == 0 else cap + ".rank%d" % rank, errors="replace").read()
        if rank == 0:
            sys.stdout.write(text)
            if text and not text.endswith("\n"):
                sys.stdout.write("\n")
            sys.stdout.flush()
        if rank != 0:
            try:
                os.remove(cap + ".rank%d" % rank)
            except OSError:
                pass
        if err is not None:
            emit({"kind": "accept", "n": n, "tag": tag, "capture": cap, "accepted": False,
                  "run_model_error": err, "wall_s": wall}, ACCEPT_JSONL)
            refuse("primal %d (%s) raised during run_model: %s" % (n, tag, err), rank)
        # evaluate on rank 0's capture; broadcast the decision so every rank exits alike
        decision = None
        if rank == 0:
            try:
                ev = acc.evaluate(acc.parse_primal_text(text))
                decision = {"refused": False, "ev": ev}
            except acc.Refusal as exc:
                decision = {"refused": True, "reason": str(exc)}
        decision = MPI.COMM_WORLD.bcast(decision, root=0)
        cd = float(prob.get_val(CD)[0])
        cl = float(prob.get_val(CL)[0])
        if decision["refused"]:
            emit({"kind": "accept", "n": n, "tag": tag, "capture": cap, "accepted": False,
                  "REFUSED": decision["reason"], "wall_s": wall}, ACCEPT_JSONL)
            refuse("primal %d (%s): %s" % (n, tag, decision["reason"]), rank)
        ev = decision["ev"]
        rec = {"kind": "accept", "n": n, "tag": tag, "capture": cap,
               "accepted": bool(ev["accepted"]), "failures": ev["failures"],
               "end_time": ev["end_time"], "n_window": ev["n_window"],
               "window_times": ev["window_times"],
               "max_rel_drift": {k: v["max_rel_drift"] for k, v in ev["per_equation"].items()},
               "r_end": {k: v["r_end"] for k, v in ev["per_equation"].items()},
               "cont_local_end": ev["cont_local_end"], "CD_end": ev["CD_end"], "CL_end": ev["CL_end"],
               "CD": repr(cd), "CL": repr(cl), "wall_s": wall}
        emit(rec, ACCEPT_JSONL)
        if rank == 0:
            print("%s_ACCEPT n=%d tag=%s accepted=%s failures=%s nuTilda_r_end=%r max_drift=%r"
                  % (TAG, n, tag, rec["accepted"], rec["failures"],
                     rec["r_end"].get("nuTilda"), rec["max_rel_drift"].get("nuTilda")), flush=True)
        if not rec["accepted"]:
            refuse("primal %d (%s) NOT ACCEPTED by the stationarity rule: %s" % (n, tag, ev["failures"]), rank)
        if not (math.isfinite(cd) and math.isfinite(cl)):
            refuse("primal %d (%s) returned non-finite CD/CL %r %r" % (n, tag, cd, cl), rank)
        emit({"kind": "primal", "n": n, "tag": tag, "CD": repr(cd), "CL": repr(cl), "wall_s": wall})
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
    totals = prob.compute_totals(of=[CD], wrt=["twist", "shape", "patchV"])
    emit({"kind": "compute_totals", "wall_s": round(time.time() - t0, 3)})
    jadj = {}
    for dv in ("twist", "shape", "patchV"):
        arr = np.atleast_1d(np.array(totals[(CD, dv)]).ravel())
        jadj[dv] = [float(v) for v in arr]
        emit({"kind": "adjoint", "dv": dv, "n": int(arr.size),
              "values": [repr(float(v)) for v in arr]})

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
            # NOTE (delta from the ancestor): the ancestor wrapped each FD pair in
            # try/except and recorded `ok: False`; here a rejected or failed
            # primal REFUSES the arm inside primal(), so no silent FD_STEP_FAILED
            # row can exist -- an FD row present is an FD row whose four primals
            # were all accepted by the rule.
            set_perturbed(dv, idx, +s)
            cdp, clp = primal("%s[%d]+%g" % (dv, idx, s))
            set_perturbed(dv, idx, -s)
            cdm, clm = primal("%s[%d]-%g" % (dv, idx, s))
            d = (cdp - cdm) / (2.0 * s)
            fd[label] = {"step": s, "d": repr(d), "CD_plus": repr(cdp),
                         "CD_minus": repr(cdm), "CL_plus": repr(clp),
                         "CL_minus": repr(clm), "ok": True}
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "which": label,
                  "row": fd[label]})
        rows.append(dict(p, fd=fd))
    for k in ("twist", "shape", "patchV"):
        prob.set_val(k, base[k].copy())

    if rank == 0:
        out = {
            "producer_md5": got,
            "accept_module_md5": md5_of(ACCEPT_MODULE),
            "disarm": {"key": DISARM_KEY, "value": DISARM_TOL_DIFF, "registered_before": registered_before,
                       "effective_readback": eff},
            "n_primals": state["n"],
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
        sys.stdout.write("%s_FD_ENDPOINT_WRITTEN %s n_rows=%d n_primals=%d\n"
                         % (TAG, OUT, len(rows), state["n"]))
        sys.stdout.flush()
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
