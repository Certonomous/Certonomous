#!/usr/bin/env python
"""Curriculum D15 -- NACA0012 SUBSONIC (DARhoSimpleFoam) baseline gradient instrument.

DERIVED FROM `curriculum_D5/d5_fd_endpoint.py` (md5 91b9f3526a39cb02eafbd5be504d7107)
with EXACTLY these registered deltas and no other (d15_xf_DELTAS_from_d5_fd_endpoint.diff):
  * PRODUCER is `d15_runScript.py` -- a BYTE COPY of the shipped tutorial
    `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/subsonic/runScript.py`
    (md5 6537fa7641c4ccb20056f60f96f63b11) -- and PRODUCER_MD5 is that md5.
    D4's instrument REFUSES any producer but its own, by md5; the refusal is
    kept, re-pointed.
  * TWO MODES, selected by `-mode X|F`.  X = the adjoint (compute_totals) of
    CD AND CL w.r.t. `shape` and `patchV` at the tutorial's BASELINE design
    (shape = 0, patchV = [U0, aoa0]), written to `d15_X.json`.  F = a CENTRAL
    finite-difference table over the REGISTERED STEP SET (three steps per DV
    kind, not the D4 clearance ladder) on the REGISTERED SUBSET of components,
    written to `d15_F.json` / `d15_F.jsonl`.  The design point is the BASELINE,
    not an optimiser endpoint: no endpoint file is read (D4's `d4_endpoint_dvs.json`
    clause is removed), so no optimiser runs in this item.
  * PLANTED-ZERO CONTROL COMPONENT `CTRL` (CLAUDE.md rule 3): a synthetic row
    with CD_plus == CD_minus == CD_baseline (derivative EXACTLY 0.0, no solve)
    and a PLANTED row with CD_plus = CD_baseline + PLANT (derivative EXACTLY
    PLANT/(2 s)); both are written to the JSONL, READ BACK FROM DISK, and the
    instrument EXITS 2 if the read-back does not see the plant.  A zero from a
    reader not shown able to see a non-zero is not evidence.
  * The two-primal eta measurement, the emit/fsync discipline and the MPI
    rank-0 file rule are D5/D4's bytes.
  * The toolchain identity is written INTO the artefact: `idwarp.__file__` and
    the md5 of `libidwarp.so`, read in-process, beside the launcher's own
    `D4S_IDWARP_SO_MD5:` print (G9 reads both; they must agree).

DAFOAM_CHARTER.md section 2: an adjoint gradient is not a result until an FD
table stands beside it -- here at the baseline, which is where the shipped
A1 row was measured to FAIL (11.43 %, idx6 sign-flipped) and the patched A1
row to PASS, so the same design point is where the two-row rule bites.
"""
import hashlib
import json
import os
import sys
import time

PRODUCER = "d15_runScript.py"
PRODUCER_MD5 = "6537fa7641c4ccb20056f60f96f63b11"
ANCHOR = "# OpenMDAO setup"
ITEM = "D15"

# ---- registered constants (PREREGISTRATION.md section 3) --------------------
ETA_FLOOR = 1.0e-14          # a measured eta below this is replaced by this and FLAGGED
STEPS = {
    "shape":  [1.0e-2, 1.0e-3, 1.0e-4],     # registered step set, FFD y-displacement units
    "patchV": [1.0e-1, 1.0e-2, 1.0e-3],     # registered step set, degrees of aoa
}
# The REGISTERED SUBSET, named in advance: 5 physical components + the control.
# shape[0] = first interior shape function (i=1, j=0); shape[3] = (i=2, j=1);
# shape[6] = the LE thickness function (i=0) -- the A1 idx6-class component the
# shipped A1 row sign-flipped at its baseline; shape[7] = the TE function;
# patchV[1] = angle of attack (degrees).
COMPONENTS = [
    ("shape", 0),
    ("shape", 3),
    ("shape", 6),
    ("shape", 7),
    ("patchV", 1),
]
CTRL_STEP = 1.0e-3
PLANT = 1.234e-03            # rule 3

OUT_X = "d15_X.json"
OUT_F = "d15_F.json"
JSONL_F = "d15_F.jsonl"


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
    if mode not in ("X", "F"):
        sys.stderr.write("D15_XF usage: d15_xf.py -mode X|F\n")
        sys.exit(64)
    return mode


def main():
    mode = parse_mode(sys.argv)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("D15_XF REFUSE producer md5 %s != frozen %s\n"
                         % (got, PRODUCER_MD5))
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D15_XF REFUSE anchor %r appears %d times\n"
                         % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]

    # the producer header parses sys.argv; give it the registered task
    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d15_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    Top = ns["Top"]
    jsonl = JSONL_F if mode == "F" else "d15_X.jsonl"

    def emit(rec):
        if rank != 0:
            return
        with open(jsonl, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    ident = idwarp_identity()
    emit({"kind": "identity", "item": ITEM, "mode": mode, "nprocs": nprocs,
          "producer_md5": got, "solverName": ns["daOptions"].get("solverName"),
          "U0": ns.get("U0"), "aoa0": ns.get("aoa0"), "T0": ns.get("T0"),
          "p0": ns.get("p0"), **ident})

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    # ---- the BASELINE design: the producer's own defaults, read back ----------
    base = {"shape": np.array(prob.get_val("shape"), dtype=float).copy(),
            "patchV": np.array(prob.get_val("patchV"), dtype=float).copy()}
    emit({"kind": "baseline_dvs", "n_shape": int(base["shape"].size),
          "n_patchV": int(base["patchV"].size),
          "shape": [repr(float(v)) for v in base["shape"]],
          "patchV": [repr(float(v)) for v in base["patchV"]]})

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
                emit({"kind": "adjoint", "of": of_key, "dv": dv, "n": int(arr.size),
                      "values": jadj[of_key][dv]})
        if rank == 0:
            out = {"item": ITEM, "mode": "X", "producer_md5": got, "nprocs": nprocs,
                   "identity": ident, "CD_baseline": repr(cd0), "CL_baseline": repr(cl0),
                   "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]],
                                    "patchV": [repr(float(v)) for v in base["patchV"]]},
                   "adjoint": jadj}
            with open(OUT_X, "w") as fh:
                json.dump(out, fh, indent=1, sort_keys=True)
                fh.flush()
                os.fsync(fh.fileno())
            sys.stdout.write("D15_X_WRITTEN %s\n" % OUT_X)
        MPI.COMM_WORLD.Barrier()
        return

    # ---- mode F: eta, then central differences at the REGISTERED steps ---------
    cd0r, cl0r = primal("baseline_repeat")
    eta_raw = abs(cd0 - cd0r)
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flagged, "CD_baseline": repr(cd0),
          "CD_repeat": repr(cd0r), "CL_baseline": repr(cl0),
          "CL_repeat": repr(cl0r)})

    def set_perturbed(dv, idx, delta):
        for k in ("shape", "patchV"):
            prob.set_val(k, base[k].copy())
        v = base[dv].copy()
        v[idx] += delta
        prob.set_val(dv, v)

    rows = []
    for dv, idx in COMPONENTS:
        if idx >= base[dv].size:
            rows.append({"dv": dv, "idx": idx, "status": "ABSENT",
                         "n_available": int(base[dv].size), "fd": {}})
            continue
        fd = {}
        for s in STEPS[dv]:
            key = repr(s)
            try:
                set_perturbed(dv, idx, +s)
                cdp, clp = primal("%s[%d]+%g" % (dv, idx, s))
                set_perturbed(dv, idx, -s)
                cdm, clm = primal("%s[%d]-%g" % (dv, idx, s))
                fd[key] = {"step": s, "dCD": repr((cdp - cdm) / (2.0 * s)),
                           "dCL": repr((clp - clm) / (2.0 * s)),
                           "CD_plus": repr(cdp), "CD_minus": repr(cdm),
                           "CL_plus": repr(clp), "CL_minus": repr(clm), "ok": True}
            except Exception as exc:                      # noqa: BLE001
                fd[key] = {"step": s, "ok": False, "error": repr(exc)[:400]}
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "step": s, "row": fd[key]})
        rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
    # restore
    for k in ("shape", "patchV"):
        prob.set_val(k, base[k].copy())

    # ---- the PLANTED-ZERO CONTROL COMPONENT (rule 3): no solve, written, read back
    ctrl = {"dv": "CTRL", "idx": 0, "status": "CONTROL", "fd": {
        repr(CTRL_STEP): {"step": CTRL_STEP, "dCD": repr(0.0), "dCL": repr(0.0),
                          "CD_plus": repr(cd0), "CD_minus": repr(cd0),
                          "CL_plus": repr(cl0), "CL_minus": repr(cl0), "ok": True,
                          "note": "synthetic: identical DVs on both sides -> derivative exactly 0"}},
        "planted": {"step": CTRL_STEP, "plant": PLANT,
                    "dCD": repr(PLANT / (2.0 * CTRL_STEP)),
                    "CD_plus": repr(cd0 + PLANT), "CD_minus": repr(cd0), "ok": True,
                    "note": "synthetic: CD_plus = CD_baseline + PLANT -> derivative exactly PLANT/(2 s)"}}
    emit({"kind": "control", "row": ctrl})
    rows.append(ctrl)

    if rank == 0:
        # READ BACK FROM DISK what was just emitted; refuse if the plant is invisible
        seen_zero, seen_plant = None, None
        with open(jsonl) as fh:
            for line in fh:
                rec = json.loads(line)
                if rec.get("kind") == "control":
                    r = rec["row"]
                    seen_zero = float(r["fd"][repr(CTRL_STEP)]["dCD"])
                    seen_plant = float(r["planted"]["dCD"])
        want = PLANT / (2.0 * CTRL_STEP)
        if seen_zero != 0.0 or seen_plant is None or abs(seen_plant - want) > 1e-12 * abs(want):
            sys.stderr.write("D15_XF REFUSE planted-zero control not seen on read-back: zero=%r plant=%r want=%r\n"
                             % (seen_zero, seen_plant, want))
            sys.exit(2)
        sys.stdout.write("D15_PLANTED_ZERO_CONTROL_SEEN zero=%r plant=%r\n" % (seen_zero, seen_plant))
        out = {
            "item": ITEM, "mode": "F", "producer_md5": got, "nprocs": nprocs,
            "identity": ident,
            "components_requested": [[d, i] for (d, i) in COMPONENTS],
            "n_components_requested": len(COMPONENTS),
            "steps": STEPS, "ctrl_step": CTRL_STEP, "plant": PLANT,
            "CD_baseline": repr(cd0), "CL_baseline": repr(cl0),
            "CD_baseline_repeat": repr(cd0r), "CL_baseline_repeat": repr(cl0r),
            "eta_raw": repr(eta_raw), "eta_used": repr(eta), "eta_floored": eta_flagged,
            "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]],
                             "patchV": [repr(float(v)) for v in base["patchV"]]},
            "rows": rows, "n_rows": len(rows),
        }
        with open(OUT_F, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("D15_F_WRITTEN %s n_rows=%d\n" % (OUT_F, len(rows)))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
