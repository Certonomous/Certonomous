#!/usr/bin/env python
"""Curriculum AV1 -- NACA0012 INCOMPRESSIBLE (DASimpleFoam) baseline gradient at np = 1 / 2 / 4.

DERIVED FROM `curriculum_D15/d15_xf.py` (8fc2bdeb, md5 8a664a976de77c5fe7c3fed5746be4de)
with EXACTLY these registered deltas and no other (av1_x_DELTAS_from_d15_xf.diff):
  * PRODUCER is `av1_runScript.py` -- a BYTE COPY of the shipped INCOMPRESSIBLE tutorial
    `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/runScript.py`
    (md5 0557da51f6f179f6de865144343c499f, checkout d3b7e38b) -- and PRODUCER_MD5 is that
    md5.  The producer-md5 refusal is kept, re-pointed.
  * ONE MODE, `-mode X`: the reverse-AD totals (compute_totals) of CD AND CL w.r.t.
    `shape` and `patchV` at the tutorial's BASELINE design, at whatever np mpirun gave us,
    written to `av1_X.json`.  The F mode (central FD) is REMOVED: this rung grades the
    adjoint against ITSELF across rank counts (ADJOINT_VERIFICATION_STANDARD.md section 3),
    never against an FD table -- the FD rows on this mesh are D13's and D15's.
  * THE PARTITION RECORD: after the run, rank 0 reads `processor*/constant/polyMesh/owner`
    (written by DAFoam's own decomposePar at np > 1) and records the per-processor cell
    counts and their sum beside the totals, so the grader can state WHICH decomposition
    produced the number (DAFOAM_CHARTER.md section 5: a parallel gradient names its
    decomposition in the same table as the number).  At np = 1 the record is `[]`, stated.
  * PLANTED CONTROL (CLAUDE.md rule 3), at the ARTEFACT level because this rung has no
    FD table to carry a CTRL component: the instrument writes `av1_X.json`, then writes
    `av1_X_planted.json` = the same artefact with PLANT = 1.234e-03 ADDED to every total,
    re-reads BOTH from disk through the same reader, and EXITS 2 unless every value moved
    by exactly PLANT.  A zero spread from a reader not shown able to see a non-zero is not
    evidence.
  * The emit/fsync discipline, the MPI rank-0 file rule and the in-artefact toolchain
    identity (idwarp.__file__, libidwarp.so md5) are D15's bytes.
"""
import glob
import hashlib
import json
import os
import re
import sys
import time

PRODUCER = "av1_runScript.py"
PRODUCER_MD5 = "0557da51f6f179f6de865144343c499f"
ANCHOR = "# OpenMDAO setup"
ITEM = "AV1"
PLANT = 1.234e-03            # rule 3
OUT_X = "av1_X.json"
OUT_X_PLANTED = "av1_X_planted.json"
JSONL = "av1_X.jsonl"
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
    if mode != "X":
        sys.stderr.write("AV1_X usage: av1_x.py -mode X\n")
        sys.exit(64)
    return mode


def partition_record():
    """Per-processor cell counts from processor*/constant/polyMesh/owner headers."""
    rec = []
    for d in sorted(glob.glob("processor*")):
        p = os.path.join(d, "constant", "polyMesh", "owner")
        n = None
        if os.path.isfile(p):
            with open(p, errors="replace") as fh:
                head = fh.read(4096)
            m = re.search(r"nCells:\s*(\d+)", head)
            n = int(m.group(1)) if m else None
        rec.append({"dir": d, "nCells": n})
    return rec


def read_X(path):
    j = json.load(open(path))
    vals = []
    for of in ("CD", "CL"):
        for dv in ("shape", "patchV"):
            vals.extend(float(v) for v in j["adjoint"][of][dv])
    return vals


def main():
    parse_mode(sys.argv)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("AV1_X REFUSE producer md5 %s != frozen %s\n" % (got, PRODUCER_MD5))
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("AV1_X REFUSE anchor %r appears %d times\n" % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "av1_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    Top = ns["Top"]

    def emit(rec):
        if rank != 0:
            return
        with open(JSONL, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    ident = idwarp_identity()
    emit({"kind": "identity", "item": ITEM, "mode": "X", "nprocs": nprocs,
          "producer_md5": got, "solverName": ns["daOptions"].get("solverName"),
          "U0": ns.get("U0"), "aoa0": ns.get("aoa0"),
          "gmresRelTol": (ns["daOptions"].get("adjEqnOption") or {}).get("gmresRelTol"),
          "primalMinResTol": ns["daOptions"].get("primalMinResTol"), **ident})

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    base = {"shape": np.array(prob.get_val("shape"), dtype=float).copy(),
            "patchV": np.array(prob.get_val("patchV"), dtype=float).copy()}
    emit({"kind": "baseline_dvs", "n_shape": int(base["shape"].size),
          "n_patchV": int(base["patchV"].size),
          "shape": [repr(float(v)) for v in base["shape"]],
          "patchV": [repr(float(v)) for v in base["patchV"]]})

    t0 = time.time()
    prob.run_model()
    cd0 = float(prob.get_val(CD)[0])
    cl0 = float(prob.get_val(CL)[0])
    emit({"kind": "primal", "tag": "baseline", "CD": repr(cd0), "CL": repr(cl0),
          "wall_s": round(time.time() - t0, 3)})

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
        part = partition_record()
        emit({"kind": "partition", "nprocs": nprocs, "record": part,
              "sum_cells": (sum(p["nCells"] for p in part if p["nCells"] is not None) if part else None)})
        out = {"item": ITEM, "mode": "X", "producer_md5": got, "nprocs": nprocs,
               "identity": ident, "CD_baseline": repr(cd0), "CL_baseline": repr(cl0),
               "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]],
                                "patchV": [repr(float(v)) for v in base["patchV"]]},
               "adjoint": jadj, "partition": part, "plant": PLANT}
        with open(OUT_X, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        # ---- the PLANTED CONTROL: a copy with PLANT added to every total, both re-read
        planted = json.loads(json.dumps(out))
        for of_key in ("CD", "CL"):
            for dv in ("shape", "patchV"):
                planted["adjoint"][of_key][dv] = [repr(float(v) + PLANT) for v in planted["adjoint"][of_key][dv]]
        planted["planted"] = True
        with open(OUT_X_PLANTED, "w") as fh:
            json.dump(planted, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        a, b = read_X(OUT_X), read_X(OUT_X_PLANTED)
        if len(a) == 0 or len(a) != len(b):
            sys.stderr.write("AV1_X REFUSE planted control: %d vs %d values read back\n" % (len(a), len(b)))
            sys.exit(2)
        worst = max(abs((y - x) - PLANT) for x, y in zip(a, b))
        if worst > 1e-12:
            sys.stderr.write("AV1_X REFUSE planted control not seen on read-back: worst residual %r\n" % worst)
            sys.exit(2)
        sys.stdout.write("AV1_PLANTED_CONTROL_SEEN n=%d worst_residual=%r plant=%r\n" % (len(a), worst, PLANT))
        sys.stdout.write("AV1_X_WRITTEN %s nprocs=%d\n" % (OUT_X, nprocs))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
