#!/usr/bin/env python
"""Curriculum D19 PHASE 1 -- the FD PLATEAU SWEEP instrument on D15's ground.

DERIVED FROM `curriculum_D15/d15_xf.py` (md5 8a664a976de77c5fe7c3fed5746be4de)
with EXACTLY these registered deltas and no others:

  * PRODUCER is `d19_runScript.py`, which is `d15_runScript.py` with the SINGLE
    change registered in PREREGISTRATION.md section 4 -- IPOPT `max_iter`
    100 -> 40 -- a line that sits BELOW the `# OpenMDAO setup` anchor.  The
    HEADER this instrument execs is therefore BYTE-IDENTICAL to D15's, and that
    is ASSERTED here against a frozen md5 rather than asserted in prose.  This
    is the mechanical support for gate G19-1a (reproduction): the same header,
    the same mesh, the same tolerance, the same ranks.

  * THREE MODES, `-mode X|S|S1`:
      X  -- the adjoint (compute_totals) of CD and CL wrt shape and patchV at
            the BASELINE design.  Arm `X2`.  Writes `d19_X.json`.
      S  -- the FIVE-STEP central-difference sweep on the five registered
            components, both functions.  Arm `S2`, np = 2.  Writes `d19_S.json`.
      S1 -- the SELECTED step only, read from `d19_selected_step.json` which the
            phase-1 SELECTOR wrote.  Arm `S1`, np = 1.  Writes `d19_S1.json`.
            This arm exists because DAFOAM_CHARTER.md section 5 FORBIDS carrying
            an FD reference across np; G19-1d gates np=1 against np=2 at s*.

  * THE SWEEP IS FIVE STEPS, FROZEN (PREREGISTRATION.md section 3):
        shape  : 3e-2, 1e-2, 1e-3, 1e-4, 1e-5
        patchV : 3e-1, 1e-1, 1e-2, 1e-3, 1e-4
    Three of the five are D15's own registered steps and are the REPRODUCTION
    control; the coarser and finer additions are what BRACKET the flat.  D15
    measured a ONE-SIDED plateau on `CD` `shape[7]` -- [1.1559 %, 21.6299 %] --
    and a one-sided plateau is not the FD table DAFOAM_CHARTER.md section 2
    requires beside a gradient entering an optimisation.

  * THIS INSTRUMENT WRITES NO ADJOINT INTO THE SWEEP ARTEFACT.  `d19_S.json` and
    `d19_S1.json` carry `rows[].fd` and nothing derived from `compute_totals`.
    That is not tidiness: the SELECTOR (`d19_select_step.py`) asserts at entry
    that no adjoint is present in its input and REFUSES if one is, and this
    instrument is the file that has to make that assertion satisfiable.  Mode X
    writes a SEPARATE file which the selector never opens.

  * PLANTED-ZERO CONTROL COMPONENT `CTRL`, inherited from D15 unchanged in
    mechanism, RE-SIZED RELATIVE (CLAUDE.md rule 3; PREREGISTRATION.md G19-1c).
    D15's plant was the bare absolute 1.234e-03.  Here the SAME absolute value
    is kept -- it is the registered `PLANT` of G19-1c and this instrument may
    not re-register it -- but it is ALSO reported as a FRACTION of the quantity
    it perturbs (`plant_rel_to_CD_baseline`), so a reader can see what band it
    is being asked to cross.  The refusal is unchanged: the control row is
    written, READ BACK FROM DISK, and the instrument EXITS 2 if the read-back
    cannot see the plant.

  * The two-primal eta measurement, the emit/fsync discipline and the MPI rank-0
    file rule are D15's bytes.

SINGLE-POINT, SINGLE DIRECTORY, AND WHY THAT IS SAFE HERE.  SO-3aR died because
three multipoint scenarios shared one case directory and each renamed its
solution to `0.0001` (`pyDAFoam.renameSolution`, pyDAFoam.py:1543).  D19 is
SINGLE-POINT: one scenario, one `prob`, perturbed primals run STRICTLY
SEQUENTIALLY inside one arm directory, which is the pattern D15's graded `F-P`
row already ran 32 primals through.  The collision class needs two writers; this
has one.  What DOES get its own directory is every ARM -- MESH, X2, S2, S1 are
four separate staged trees under the run root, and the launcher refuses to stage
over a live one.
"""
import hashlib
import json
import os
import sys
import time

PRODUCER = "d19_runScript.py"
PRODUCER_MD5 = "a5e18503ea29d0e37c3cf1668533cd34"
# The header ABOVE the anchor is what this instrument execs.  It is byte-identical
# to D15's producer header; G19-1a rests on that and so it is asserted, not stated.
HEADER_MD5_SHARED_WITH_D15 = "d1efc43583fbeb59fb5116816b055a07"
ANCHOR = "# OpenMDAO setup"
ITEM = "D19"

# ---- registered constants (PREREGISTRATION.md section 3) --------------------
ETA_FLOOR = 1.0e-14
STEPS_SWEEP = {
    "shape":  [3.0e-2, 1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5],
    "patchV": [3.0e-1, 1.0e-1, 1.0e-2, 1.0e-3, 1.0e-4],
}
# D15's registered three, named so the reproduction subset is explicit and is not
# re-derived by intersecting two lists at grading time.
STEPS_D15 = {"shape": [1.0e-2, 1.0e-3, 1.0e-4], "patchV": [1.0e-1, 1.0e-2, 1.0e-3]}
COMPONENTS = [("shape", 0), ("shape", 3), ("shape", 6), ("shape", 7), ("patchV", 1)]
CTRL_STEP = 1.0e-3
PLANT = 1.234e-03            # G19-1c, D15's own registered value

SELECTED = "d19_selected_step.json"
OUT = {"X": "d19_X.json", "S": "d19_S.json", "S1": "d19_S1.json"}


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
    if mode not in ("X", "S", "S1"):
        sys.stderr.write("D19_XF usage: d19_xf.py -mode X|S|S1\n")
        sys.exit(64)
    return mode


def steps_for(mode, dv, sel):
    if mode == "S":
        return list(STEPS_SWEEP[dv])
    return [sel[dv]]


def main():
    mode = parse_mode(sys.argv)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("D19_XF REFUSE producer md5 %s != frozen %s\n" % (got, PRODUCER_MD5))
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D19_XF REFUSE anchor %r appears %d times\n" % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]
    hmd5 = hashlib.md5(header.encode()).hexdigest()
    if hmd5 != HEADER_MD5_SHARED_WITH_D15:
        sys.stderr.write("D19_XF REFUSE producer header md5 %s != D15's %s -- G19-1a "
                         "reproduction cannot be claimed against a different header\n"
                         % (hmd5, HEADER_MD5_SHARED_WITH_D15))
        sys.exit(2)
    sys.stdout.write("D19_HEADER_IDENTICAL_TO_D15 md5=%s\n" % hmd5)

    # ---- mode S1 reads the SELECTOR's frozen choice; it invents no step -------
    sel = None
    if mode == "S1":
        if not os.path.isfile(SELECTED):
            sys.stderr.write("D19_XF REFUSE mode S1 needs %s (written by d19_select_step.py)\n" % SELECTED)
            sys.exit(2)
        selj = json.load(open(SELECTED))
        sel = {"shape": float(selj["s_star"]["shape"]), "patchV": float(selj["s_star"]["patchV"])}
        for dv in ("shape", "patchV"):
            if sel[dv] not in STEPS_SWEEP[dv]:
                sys.stderr.write("D19_XF REFUSE selected %s step %r is not in the frozen sweep %r\n"
                                 % (dv, sel[dv], STEPS_SWEEP[dv]))
                sys.exit(2)
        if selj.get("selector_saw_adjoint") is not False:
            sys.stderr.write("D19_XF REFUSE selection artefact does not assert the selector was adjoint-blind\n")
            sys.exit(2)
        sys.stdout.write("D19_S1_USING_SELECTED_STEP shape=%r patchV=%r\n" % (sel["shape"], sel["patchV"]))

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d19_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    Top = ns["Top"]
    jsonl = OUT[mode].replace(".json", ".jsonl")

    def emit(rec):
        if rank != 0:
            return
        with open(jsonl, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    ident = idwarp_identity()
    emit({"kind": "identity", "item": ITEM, "mode": mode, "nprocs": nprocs,
          "producer_md5": got, "header_md5": hmd5,
          "solverName": ns["daOptions"].get("solverName"),
          "primalMinResTol": ns["daOptions"].get("primalMinResTol"),
          "U0": ns.get("U0"), "aoa0": ns.get("aoa0"), "T0": ns.get("T0"),
          "p0": ns.get("p0"), **ident})

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

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
            out = {"item": ITEM, "mode": "X", "producer_md5": got, "header_md5": hmd5,
                   "nprocs": nprocs, "identity": ident,
                   "CD_baseline": repr(cd0), "CL_baseline": repr(cl0),
                   "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]],
                                    "patchV": [repr(float(v)) for v in base["patchV"]]},
                   "adjoint": jadj}
            with open(OUT["X"], "w") as fh:
                json.dump(out, fh, indent=1, sort_keys=True)
                fh.flush()
                os.fsync(fh.fileno())
            sys.stdout.write("D19_X_WRITTEN %s\n" % OUT["X"])
        MPI.COMM_WORLD.Barrier()
        return

    # ---- modes S / S1: eta, then central differences ---------------------------
    cd0r, cl0r = primal("baseline_repeat")
    eta_raw = abs(cd0 - cd0r)
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flagged, "CD_baseline": repr(cd0),
          "CD_repeat": repr(cd0r), "CL_baseline": repr(cl0), "CL_repeat": repr(cl0r)})

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
        for s in steps_for(mode, dv, sel):
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
    for k in ("shape", "patchV"):
        prob.set_val(k, base[k].copy())

    # ---- the PLANTED-ZERO CONTROL COMPONENT (rule 3 / G19-1c) ------------------
    # The plant is the registered absolute PLANT, and is ALSO reported relative to
    # the quantity it perturbs, so a reader can size it against a band.
    ctrl = {"dv": "CTRL", "idx": 0, "status": "CONTROL", "fd": {
        repr(CTRL_STEP): {"step": CTRL_STEP, "dCD": repr(0.0), "dCL": repr(0.0),
                          "CD_plus": repr(cd0), "CD_minus": repr(cd0),
                          "CL_plus": repr(cl0), "CL_minus": repr(cl0), "ok": True,
                          "note": "synthetic: identical DVs on both sides -> derivative exactly 0"}},
        "planted": {"step": CTRL_STEP, "plant": PLANT,
                    "plant_rel_to_CD_baseline": repr(PLANT / abs(cd0)),
                    "dCD": repr(PLANT / (2.0 * CTRL_STEP)),
                    "CD_plus": repr(cd0 + PLANT), "CD_minus": repr(cd0), "ok": True,
                    "note": "synthetic: CD_plus = CD_baseline + PLANT -> derivative exactly PLANT/(2 s)"}}
    emit({"kind": "control", "row": ctrl})
    rows.append(ctrl)

    if rank == 0:
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
            sys.stderr.write("D19_XF REFUSE planted-zero control not seen on read-back: "
                             "zero=%r plant=%r want=%r\n" % (seen_zero, seen_plant, want))
            sys.exit(2)
        sys.stdout.write("D19_PLANTED_ZERO_CONTROL_SEEN zero=%r plant=%r rel_to_CD=%.6f\n"
                         % (seen_zero, seen_plant, PLANT / abs(cd0)))
        out = {
            "item": ITEM, "mode": mode, "producer_md5": got, "header_md5": hmd5,
            "nprocs": nprocs, "identity": ident,
            "components_requested": [[d, i] for (d, i) in COMPONENTS],
            "n_components_requested": len(COMPONENTS),
            "steps": {dv: steps_for(mode, dv, sel) for dv in ("shape", "patchV")},
            "steps_sweep_registered": STEPS_SWEEP,
            "steps_shared_with_d15": STEPS_D15,
            "selected_step": sel,
            "ctrl_step": CTRL_STEP, "plant": PLANT,
            "plant_rel_to_CD_baseline": repr(PLANT / abs(cd0)),
            "CD_baseline": repr(cd0), "CL_baseline": repr(cl0),
            "CD_baseline_repeat": repr(cd0r), "CL_baseline_repeat": repr(cl0r),
            "eta_raw": repr(eta_raw), "eta_used": repr(eta), "eta_floored": eta_flagged,
            "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]],
                             "patchV": [repr(float(v)) for v in base["patchV"]]},
            "rows": rows, "n_rows": len(rows),
            "contains_adjoint": False,
        }
        with open(OUT[mode], "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("D19_%s_WRITTEN %s n_rows=%d\n" % (mode, OUT[mode], len(rows)))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
