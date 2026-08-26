#!/usr/bin/env python
"""Curriculum AV2 -- NACA0012 INCOMPRESSIBLE (DASimpleFoam) baseline gradient: FORWARD-mode AD
(ADF) against REVERSE-mode AD (ADR) at np = 1 -- the dot-product / duality identity at the
total level, per registered design-variable component (ADJOINT_VERIFICATION_STANDARD.md
section 2, v1.0a):  <1, (dJ/dx) e_k> [ADF]  =  <(dJ/dx)^T 1, e_k> [ADR].

DERIVED FROM `curriculum_AV1/av1_x.py` (0b3ebaa4, md5 74011a9c5e6c760b8aec1c78e928b4d2)
with EXACTLY these registered deltas and no other (av2_xf_DELTAS_from_av1_x.diff):
  * TWO MODES.  `-mode X` = AV1's X mode unchanged (reverse totals of CD and CL w.r.t.
    `shape` and `patchV` at the baseline, artefact-level planted control, av2_X.json).
    `-mode FAD` = for each REGISTERED component k (shape[0], shape[3], shape[6], shape[7],
    patchV[1] -- D15's subset), a FRESH problem built with
        daOptions["useAD"] = {"mode": "forward", "dvName": <dv>, "seedIndex": k}
    (pyDAFoam.py:426 default overridden; :811 `self.solverAD.solvePrimal()`; seeds one-hot
    at :1363-1370, FFD seeds through pyGeo + IDWarp forward mode at :1376 calcFFD2XvSeeds,
    which needs `add_dvgeo` on the solver component, mphys_dafoam.py:295/:321), then
    `prob.run_model()`, and the TANGENTS read as `prob.get_val(CD)[0]` / `prob.get_val(CL)[0]`
    -- DAFoam's OWN regression pattern, tests/testFuncs.py:33-50 (md5 fb11e906...).
  * THE FORWARD-CHANNEL CONTROLS (standard v1.0a): the FAD arm first runs ONE ordinary
    (reverse-configured) primal to get CD0/CL0; then for every component the forward value
    MUST NOT be exactly 0.0 (silent no-op), MUST NOT be exactly 1.0 (seed echo), and MUST
    differ from CD0 by more than 1e-6 relative (function echo) -- any of these writes the
    row as NOT_A_RESULT_CONTROL and the instrument EXITS 2.  A value from a channel not shown
    to carry a tangent is not evidence.
  * THE BLOCKED BRANCH, registered: if the ADF module does not import, no subsystem exposes
    `add_dvgeo`, or forward mode raises on this case, the row is written `blocked` with the
    exception text, the artefact is still written and the instrument exits 0 -- the grader
    maps a blocked row to BLOCKED (never to PASS, never to NOT A RESULT).
  * The artefact-level planted control (PLANT added to every forward value, re-read) and
    the emit/fsync discipline are AV1's bytes.
"""
import hashlib
import json
import os
import sys
import time

PRODUCER = "av2_runScript.py"
PRODUCER_MD5 = "0557da51f6f179f6de865144343c499f"
ANCHOR = "# OpenMDAO setup"
ITEM = "AV2"
PLANT = 1.234e-03            # rule 3
COMPONENTS = [("shape", 0), ("shape", 3), ("shape", 6), ("shape", 7), ("patchV", 1)]
ECHO_TOL = 1.0e-6            # forward value must differ from the function value by more than this, relative
OUT_X, OUT_X_PLANTED, JSONL_X = "av2_X.json", "av2_X_planted.json", "av2_X.jsonl"
OUT_F, OUT_F_PLANTED, JSONL_F = "av2_FAD.json", "av2_FAD_planted.json", "av2_FAD.jsonl"
CD = "scenario1.aero_post.CD"
CL = "scenario1.aero_post.CL"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def idwarp_identity():
    try:
        import idwarp
        p = idwarp.__file__
        so = os.path.join(os.path.dirname(p), "libidwarp.so")
        return {"idwarp_file": p, "libidwarp_so_md5": md5_of(so)}
    except Exception as exc:                                  # noqa: BLE001
        return {"idwarp_file": None, "libidwarp_so_md5": None, "error": repr(exc)[:200]}


def parse_mode(argv):
    mode = None
    for i, a in enumerate(argv):
        if a == "-mode" and i + 1 < len(argv):
            mode = argv[i + 1]
    if mode not in ("X", "FAD"):
        sys.stderr.write("AV2_XF usage: av2_xf.py -mode X|FAD\n")
        sys.exit(64)
    return mode


def read_X(path):
    j = json.load(open(path))
    vals = []
    for of in ("CD", "CL"):
        for dv in ("shape", "patchV"):
            vals.extend(float(v) for v in j["adjoint"][of][dv])
    return vals


def read_F(path):
    j = json.load(open(path))
    vals = []
    for row in j["rows"]:
        if row.get("status") == "MEASURED":
            vals.append(float(row["fwd_CD"]))
            vals.append(float(row["fwd_CL"]))
    return vals


def plant_and_readback(out, planted_path, orig_path, reader, mutate):
    planted = json.loads(json.dumps(out))
    mutate(planted)
    planted["planted"] = True
    with open(planted_path, "w") as fh:
        json.dump(planted, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    a, b = reader(orig_path), reader(planted_path)
    if len(a) == 0 or len(a) != len(b):
        sys.stderr.write("AV2_XF REFUSE planted control: %d vs %d values read back\n" % (len(a), len(b)))
        sys.exit(2)
    worst = max(abs((y - x) - PLANT) for x, y in zip(a, b))
    if worst > 1e-12:
        sys.stderr.write("AV2_XF REFUSE planted control not seen on read-back: worst residual %r\n" % worst)
        sys.exit(2)
    sys.stdout.write("AV2_PLANTED_CONTROL_SEEN n=%d worst_residual=%r plant=%r\n" % (len(a), worst, PLANT))


def main():
    mode = parse_mode(sys.argv)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("AV2_XF REFUSE producer md5 %s != frozen %s\n" % (got, PRODUCER_MD5))
        sys.exit(2)
    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("AV2_XF REFUSE anchor %r appears %d times\n" % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "av2_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    Top = ns["Top"]
    daOptions = ns["daOptions"]
    jsonl = JSONL_X if mode == "X" else JSONL_F

    def emit(rec):
        if rank != 0:
            return
        with open(jsonl, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    ident = idwarp_identity()
    emit({"kind": "identity", "item": ITEM, "mode": mode, "nprocs": nprocs,
          "producer_md5": got, "solverName": daOptions.get("solverName"),
          "gmresRelTol": (daOptions.get("adjEqnOption") or {}).get("gmresRelTol"),
          "primalMinResTol": daOptions.get("primalMinResTol"), "useAD_default": daOptions.get("useAD"), **ident})

    def build(useAD=None):
        if useAD is None:
            daOptions.pop("useAD", None)
        else:
            daOptions["useAD"] = dict(useAD)
        prob = om.Problem()
        prob.model = Top()
        prob.setup(mode="rev")
        return prob

    def attach_dvgeo(prob):
        dvgeo = getattr(prob.model.geometry, "DVGeo", None)
        if dvgeo is None:
            return 0
        n = 0
        for sub in prob.model.system_iter(recurse=True):
            if hasattr(sub, "add_dvgeo"):
                sub.add_dvgeo(dvgeo)
                n += 1
        return n

    # ---- the ordinary (reverse-configured) baseline primal, both modes --------------
    prob = build(None)
    base = {"shape": np.array(prob.get_val("shape"), dtype=float).copy(),
            "patchV": np.array(prob.get_val("patchV"), dtype=float).copy()}
    emit({"kind": "baseline_dvs", "n_shape": int(base["shape"].size), "n_patchV": int(base["patchV"].size),
          "shape": [repr(float(v)) for v in base["shape"]], "patchV": [repr(float(v)) for v in base["patchV"]]})
    t0 = time.time()
    prob.run_model()
    cd0 = float(prob.get_val(CD)[0])
    cl0 = float(prob.get_val(CL)[0])
    emit({"kind": "primal", "tag": "baseline", "CD": repr(cd0), "CL": repr(cl0), "wall_s": round(time.time() - t0, 3)})

    if mode == "X":
        t0 = time.time()
        totals = prob.compute_totals(of=[CD, CL], wrt=["shape", "patchV"])
        emit({"kind": "compute_totals", "wall_s": round(time.time() - t0, 3)})
        jadj = {}
        for of_name, of_key in ((CD, "CD"), (CL, "CL")):
            jadj[of_key] = {}
            for dv in ("shape", "patchV"):
                arr = np.atleast_1d(np.array(totals[(of_name, dv)]).ravel())
                jadj[of_key][dv] = [repr(float(v)) for v in arr]
                emit({"kind": "adjoint", "of": of_key, "dv": dv, "n": int(arr.size), "values": jadj[of_key][dv]})
        if rank == 0:
            out = {"item": ITEM, "mode": "X", "producer_md5": got, "nprocs": nprocs, "identity": ident,
                   "CD_baseline": repr(cd0), "CL_baseline": repr(cl0),
                   "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]], "patchV": [repr(float(v)) for v in base["patchV"]]},
                   "adjoint": jadj, "plant": PLANT}
            with open(OUT_X, "w") as fh:
                json.dump(out, fh, indent=1, sort_keys=True); fh.flush(); os.fsync(fh.fileno())

            def mut(p):
                for of_key in ("CD", "CL"):
                    for dv in ("shape", "patchV"):
                        p["adjoint"][of_key][dv] = [repr(float(v) + PLANT) for v in p["adjoint"][of_key][dv]]
            plant_and_readback(out, OUT_X_PLANTED, OUT_X, read_X, mut)
            sys.stdout.write("AV2_X_WRITTEN %s nprocs=%d\n" % (OUT_X, nprocs))
        MPI.COMM_WORLD.Barrier()
        return

    # ---- mode FAD: one fresh forward-mode problem per registered component --------------
    rows = []
    blocked_any = False
    control_fail = False
    for dv, idx in COMPONENTS:
        if idx >= base[dv].size:
            rows.append({"dv": dv, "idx": idx, "status": "ABSENT", "n_available": int(base[dv].size)})
            continue
        useAD = {"mode": "forward", "dvName": dv, "seedIndex": int(idx)}
        row = {"dv": dv, "idx": idx, "useAD": useAD}
        t0 = time.time()
        try:
            p = build(useAD)
            n_dvgeo = attach_dvgeo(p)
            row["n_add_dvgeo"] = n_dvgeo
            if dv == "shape" and n_dvgeo == 0:
                raise RuntimeError("no subsystem exposes add_dvgeo; forward mode on an FFD DV needs calcFFD2XvSeeds(DVGeo)")
            for k in ("shape", "patchV"):
                p.set_val(k, base[k].copy())
            p.run_model()
            fcd = float(p.get_val(CD)[0])
            fcl = float(p.get_val(CL)[0])
            row.update({"status": "MEASURED", "fwd_CD": repr(fcd), "fwd_CL": repr(fcl),
                        "wall_s": round(time.time() - t0, 3)})
            # ---- the forward-channel controls (standard v1.0a)
            ctl = {"nonzero": fcd != 0.0 and fcl != 0.0,
                   "not_seed_echo": fcd != 1.0 and fcl != 1.0,
                   "not_function_echo": (abs(fcd - cd0) > ECHO_TOL * abs(cd0)) and (abs(fcl - cl0) > ECHO_TOL * abs(cl0))}
            row["controls"] = ctl
            if not all(ctl.values()):
                row["status"] = "NOT_A_RESULT_CONTROL"
                control_fail = True
        except Exception as exc:                                  # noqa: BLE001
            row.update({"status": "BLOCKED", "blocked": True, "error": repr(exc)[:600],
                        "wall_s": round(time.time() - t0, 3)})
            blocked_any = True
        emit({"kind": "forward", "row": row})
        rows.append(row)

    if rank == 0:
        out = {"item": ITEM, "mode": "FAD", "producer_md5": got, "nprocs": nprocs, "identity": ident,
               "components_requested": [[d, i] for (d, i) in COMPONENTS], "n_components_requested": len(COMPONENTS),
               "CD_baseline": repr(cd0), "CL_baseline": repr(cl0), "echo_tol": ECHO_TOL,
               "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]], "patchV": [repr(float(v)) for v in base["patchV"]]},
               "rows": rows, "n_rows": len(rows), "blocked_any": blocked_any, "control_fail": control_fail, "plant": PLANT}
        with open(OUT_F, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True); fh.flush(); os.fsync(fh.fileno())
        if control_fail:
            sys.stderr.write("AV2_XF REFUSE forward-channel control: a forward value is 0.0, 1.0 or equal to the function value (silent no-op / seed echo / function echo)\n")
            sys.stdout.write("AV2_FAD_CONTROL_REFUSED %s\n" % OUT_F)
            sys.exit(2)
        if [r for r in rows if r.get("status") == "MEASURED"]:
            def mutf(p):
                for r in p["rows"]:
                    if r.get("status") == "MEASURED":
                        r["fwd_CD"] = repr(float(r["fwd_CD"]) + PLANT)
                        r["fwd_CL"] = repr(float(r["fwd_CL"]) + PLANT)
            plant_and_readback(out, OUT_F_PLANTED, OUT_F, read_F, mutf)
        else:
            sys.stdout.write("AV2_PLANTED_CONTROL_SEEN n=0 note=every row blocked, nothing to plant\n")
        if blocked_any:
            sys.stdout.write("AV2_FAD_BLOCKED rows_blocked=%d\n" % sum(1 for r in rows if r.get("blocked")))
        sys.stdout.write("AV2_FAD_WRITTEN %s n_rows=%d blocked_any=%s\n" % (OUT_F, len(rows), blocked_any))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
