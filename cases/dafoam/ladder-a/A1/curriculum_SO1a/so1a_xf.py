#!/usr/bin/env python
"""Curriculum SO-1a -- NACA0012 INCOMPRESSIBLE drag-min-at-fixed-lift, the
FD-VERIFIED GRADIENT RUNG of Sanaa's shape-optimisation ladder SO-1.

DERIVED FROM `curriculum_D15/d15_xf.py` (md5 8a664a976de77c5fe7c3fed5746be4de)
with EXACTLY these registered deltas and no other (so1a_xf_DELTAS_from_d15_xf.diff):
  * PRODUCER is `so1a_runScript.py` -- a BYTE COPY of the shipped tutorial
    `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/runScript.py`
    (md5 0557da51f6f179f6de865144343c499f), the DRAG-MIN-AT-FIXED-LIFT problem
    itself: objective `CD`, EQUALITY constraint `CL == CL_target = 0.5`, DVs
    `shape` (8 FFD shape functions) and `patchV` (|U| fixed, aoa free).
    D15's md5 refusal is kept, re-pointed.
  * THE CONSTRAINT GRADIENT IS A FIRST-CLASS OUTPUT, not a by-product.  SO-1's
    optimisation rung SO-1b is a CONSTRAINED problem, so `dCL/dx` is graded on
    the same registered components and the same bands as `dCD/dx`.  Both come
    from the SAME primals -- the FD table records CD_plus/CD_minus AND
    CL_plus/CL_minus at every step -- so the constraint gradient costs nothing
    beyond the objective's.
  * THE CHARTER-4 TRIVIAL BASELINE IS BOUGHT, not merely named.  `TB_STEPS`
    adds one DELIBERATELY WRONG step per DV kind, five orders below the
    registered middle step, in the subtractive-cancellation regime where the FD
    difference is at or below the measured primal repeatability eta.  It is
    written into the artefact under the key `tb` beside `fd`, so the grader can
    score the registered gate G-TB: if the WRONG step also passes band D the FD
    gate is not measuring the step and the G5 verdict is WITHDRAWN
    (`DAFOAM_CHARTER.md` section 4, registered before its own run).
  * `writeCompression` IS READ FROM THE CASE'S OWN `system/controlDict` and
    written into the artefact.  AV-1 and AV-2 both died this session because a
    frozen grader pinned the age-guard datum to the NAME `0/U` while
    `writeCompression on` turns it into `0/U.gz` on a serial arm.  The setting
    is now a recorded datum of the run, not an assumption of the reader.
  * np = 1 ON EVERY SOLVER ARM by registration (`DAFOAM_CHARTER.md` section 5,
    serial before parallel; and A4's 16,600x decomposition effect is removed
    from the chain entirely).  `nprocs` is still read from MPI and recorded.
  * Printed tokens D15_* -> SO1A_*; artefact names d15_* -> so1a_*.
  * The two-primal eta measurement, the CTRL planted-zero component with its
    disk read-back refusal, the emit/fsync discipline and the MPI rank-0 file
    rule are D15/D5/D4's bytes.

DAFOAM_CHARTER.md section 2: an adjoint gradient is not a result until an FD
table stands beside it.  Section 3: the step is proved to lie in the plateau.
Section 4: the gate names its trivial baseline BEFORE its own run.  Section 5:
serial before parallel.  All four are instrumented here.
"""

import hashlib
import json
import os
import sys
import time

PRODUCER = "so1a_runScript.py"
PRODUCER_MD5 = "0557da51f6f179f6de865144343c499f"
ANCHOR = "# OpenMDAO setup"
ITEM = "SO1a"

# ---- registered constants (PREREGISTRATION.md section 3) --------------------
ETA_FLOOR = 1.0e-14          # a measured eta below this is replaced by this and FLAGGED
STEPS = {
    "shape":  [1.0e-2, 1.0e-3, 1.0e-4],     # registered step set, FFD y-displacement units
    "patchV": [1.0e-1, 1.0e-2, 1.0e-3],     # registered step set, degrees of aoa
}
# THE CHARTER-4 TRIVIAL BASELINE: the SAME probe at a DELIBERATELY WRONG step,
# five orders below the registered middle step.  At h = 1e-8 on a derivative of
# order 1e-2 the numerator is ~1e-10, at or below the measured primal
# repeatability eta (D15 measured eta 1.30e-10 on this mesh), so the estimate is
# noise and MUST fail band D.  If it PASSES, the gate is not measuring the step
# and the G5 verdict is WITHDRAWN -- registered here, before its own run.
TB_STEPS = {
    "shape":  [1.0e-8],
    "patchV": [1.0e-6],
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

OUT_X = "so1a_X.json"
OUT_F = "so1a_F.json"
JSONL_F = "so1a_F.jsonl"


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


def case_write_compression():
    """Read `writeCompression` from THE CASE'S OWN system/controlDict.

    AV-1 and AV-2 both returned NOT A RESULT this session because a frozen
    comparator pinned the age-guard datum to the NAME `0/U`, and
    `writeCompression on` rewrites that file as `0/U.gz` on a serial arm.  The
    setting is a fact about the run and is recorded as one; the grader resolves
    the datum by EXISTENCE over both names and cross-checks it against this
    value.  An unreadable dictionary is reported, never guessed.
    """
    p = os.path.join("system", "controlDict")
    try:
        for line in open(p, errors="replace"):
            s = line.strip()
            if s.startswith("writeCompression"):
                return {"write_compression": s.rstrip(";").split()[-1],
                        "write_compression_source": os.path.abspath(p)}
    except OSError as exc:                                    # noqa: BLE001
        return {"write_compression": None, "write_compression_source": None,
                "write_compression_error": repr(exc)[:200]}
    return {"write_compression": None, "write_compression_source": os.path.abspath(p),
            "write_compression_error": "key absent from controlDict"}


def parse_mode(argv):
    mode = None
    for i, a in enumerate(argv):
        if a == "-mode" and i + 1 < len(argv):
            mode = argv[i + 1]
    if mode not in ("X", "F"):
        sys.stderr.write("SO1A_XF usage: so1a_xf.py -mode X|F\n")
        sys.exit(64)
    return mode


def main():
    mode = parse_mode(sys.argv)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("SO1A_XF REFUSE producer md5 %s != frozen %s\n"
                         % (got, PRODUCER_MD5))
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("SO1A_XF REFUSE anchor %r appears %d times\n"
                         % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]

    # the producer header parses sys.argv; give it the registered task
    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "so1a_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    Top = ns["Top"]
    jsonl = JSONL_F if mode == "F" else "so1a_X.jsonl"

    def emit(rec):
        if rank != 0:
            return
        with open(jsonl, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    ident = idwarp_identity()
    ident.update(case_write_compression())
    emit({"kind": "identity", "item": ITEM, "mode": mode, "nprocs": nprocs,
          "producer_md5": got, "solverName": ns["daOptions"].get("solverName"),
          "U0": ns.get("U0"), "aoa0": ns.get("aoa0"), "CL_target": ns.get("CL_target"),
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
            sys.stdout.write("SO1A_X_WRITTEN %s\n" % OUT_X)
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
        # ---- the CHARTER-4 TRIVIAL BASELINE at the DELIBERATELY WRONG step ----
        tb = {}
        for s in TB_STEPS[dv]:
            key = repr(s)
            try:
                set_perturbed(dv, idx, +s)
                cdp, clp = primal("TB %s[%d]+%g" % (dv, idx, s))
                set_perturbed(dv, idx, -s)
                cdm, clm = primal("TB %s[%d]-%g" % (dv, idx, s))
                tb[key] = {"step": s, "dCD": repr((cdp - cdm) / (2.0 * s)),
                           "dCL": repr((clp - clm) / (2.0 * s)),
                           "CD_plus": repr(cdp), "CD_minus": repr(cdm),
                           "CL_plus": repr(clp), "CL_minus": repr(clm), "ok": True}
            except Exception as exc:                      # noqa: BLE001
                tb[key] = {"step": s, "ok": False, "error": repr(exc)[:400]}
            emit({"kind": "tb_step", "dv": dv, "idx": idx, "step": s, "row": tb[key]})
        rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd, "tb": tb})
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
            sys.stderr.write("SO1A_XF REFUSE planted-zero control not seen on read-back: zero=%r plant=%r want=%r\n"
                             % (seen_zero, seen_plant, want))
            sys.exit(2)
        sys.stdout.write("SO1A_PLANTED_ZERO_CONTROL_SEEN zero=%r plant=%r\n" % (seen_zero, seen_plant))
        out = {
            "item": ITEM, "mode": "F", "producer_md5": got, "nprocs": nprocs,
            "identity": ident,
            "components_requested": [[d, i] for (d, i) in COMPONENTS],
            "n_components_requested": len(COMPONENTS),
            "steps": STEPS, "tb_steps": TB_STEPS, "ctrl_step": CTRL_STEP, "plant": PLANT,
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
        sys.stdout.write("SO1A_F_WRITTEN %s n_rows=%d\n" % (OUT_F, len(rows)))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
