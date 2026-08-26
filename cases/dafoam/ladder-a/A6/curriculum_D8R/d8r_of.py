#!/usr/bin/env python
"""Curriculum D8R -- A6 CRM wing-alone N=16, twist-only constrained drag minimisation
TO CONVERGENCE (DARhoSimpleCFoam, M 0.85), then the ENDPOINT gradient FD-verified:
the optimisation + endpoint-FD instrument, TWO MODES.

DERIVED FROM `curriculum_D16/d16_xf.py` (d8r_of_DELTAS_from_d16_xf.diff), itself from
`curriculum_D15/d15_xf.py` and `curriculum_D5/d5_fd_endpoint.py` (md5 91b9f3526a39cb02eafbd5be504d7107),
with these registered deltas:
  * PRODUCER is `d8r_runScript.py` -- a BYTE COPY of D8's frozen arm script
    `/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt/opt/runScript.py`
    (md5 28c7819487a025a5f6554d38062a2b66; = `d8_gen_arm.py` applied to the A6 tutorial
    script, D8 RESULTS.md section 7 proved the byte identity) -- and PRODUCER_MD5 is that md5.
    Only its HEADER (everything above `# OpenMDAO setup`: daOptions with D8's E1/E2 edits,
    meshOptions, the twist-only `Top` with E3/E4) is executed; D8's post-anchor task branches
    (max_iter 3, optd8, fdsub8) are NEVER reached -- the optimiser settings below are this
    item's registered ones.  D4's instrument REFUSES any producer but its own, by md5.
  * MODE O = the OPTIMISATION arm: cold primal (P-BASE), CL trim (D8's exact
    findFeasibleDesign call), `run_driver` under IPOPT with D8's option block and the
    REGISTERED major budget MAX_ITER, endpoint re-evaluation, `compute_totals` of CD and CL
    w.r.t. twist and patchV at the ENDPOINT, the IPOPT terminus read from opt_IPOPT.txt;
    written to `d8r_O.json`.
  * MODE F = the ENDPOINT FD arm: reads `d8r_O_endpoint.json` (the launcher's copy of the
    SAME ROW's `d8r_O.json`), sets the endpoint design, measures eta by two primals, then a
    CENTRAL finite-difference table over the REGISTERED STEP SET (three steps) on the
    REGISTERED SUBSET of twist components; written to `d8r_F.json` / `d8r_F.jsonl`.
  * PLANTED-ZERO CONTROL COMPONENT `CTRL` (CLAUDE.md rule 3), the emit/fsync discipline,
    the MPI rank-0 file rule and the in-process libidwarp.so md5: D16's bytes.

DAFOAM_CHARTER.md section 9: an optimisation is PASS only if the optimiser printed its own
convergence statement, and every optimisation reports an FD check of the gradient AT ITS
FINAL DESIGN POINT -- that is what mode F is for, on both rows.
"""
import hashlib
import json
import os
import re
import sys
import time

PRODUCER = "d8r_runScript.py"
PRODUCER_MD5 = "28c7819487a025a5f6554d38062a2b66"
ANCHOR = "# OpenMDAO setup"
ITEM = "D8R"
SCENARIO = "scenario1"

# ---- registered constants (PREREGISTRATION.md sections 2-3) ------------------
MAX_ITER = 30                # the registered major-iteration budget = 1.5 x the 20-major point
IPOPT_OPTS = {               # D8's option block (opt/runScript.py), max_iter re-registered
    "tol": 1.0e-5,
    "constr_viol_tol": 1.0e-5,
    "max_iter": MAX_ITER,
    "print_level": 5,
    "output_file": "opt_IPOPT.txt",
    "mu_strategy": "adaptive",
    "limited_memory_max_history": 10,
    "nlp_scaling_method": "none",
    "alpha_for_y": "full",
    "recalc_y": "yes",
}
TRIM = {"epsFD": [1.0e-1], "tol": 1.0e-3, "maxIter": 4}   # D8's findFeasibleDesign call, verbatim
ETA_FLOOR = 1.0e-14
STEPS = {
    "twist": [3.0e-2, 1.0e-1, 3.0e-1],   # degrees; D8's graded rungs (T1: s_lo 0.03-0.1, s_hi 0.1-0.2)
}
# The REGISTERED SUBSET (<= 5), named in advance: the three D8 components with the
# largest endpoint error (twist 5: 2.650 %, twist 4: 2.171 %, twist 1: 2.070 %) and two
# of the best (twist 0: 0.584 %, twist 3: 0.577 %) -- D8 RESULTS.md T2.  twist idx6 is
# NOT A RESULT by name (D8 section 6) and is not touched.
COMPONENTS = [
    ("twist", 0),
    ("twist", 1),
    ("twist", 3),
    ("twist", 4),
    ("twist", 5),
]
CTRL_STEP = 1.0e-1
PLANT = 1.234e-03            # rule 3

OUT_O = "d8r_O.json"
OUT_F = "d8r_F.json"
JSONL_F = "d8r_F.jsonl"
ENDPOINT_IN = "d8r_O_endpoint.json"


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
    if mode not in ("O", "F"):
        sys.stderr.write("D8R_OF usage: d8r_of.py -mode O|F\n")
        sys.exit(64)
    return mode


def read_ipopt_terminus(path):
    """The optimiser's OWN statement, read from its own file; absent -> None fields."""
    out = {"exit_line": None, "n_iter": None, "nlp_error": None, "constr_viol": None, "file": path}
    if not os.path.isfile(path):
        return out
    text = open(path, errors="replace").read()
    m = re.search(r"^(EXIT: .*)$", text, re.M)
    if m:
        out["exit_line"] = m.group(1).strip()
    m = re.search(r"^Number of Iterations\.*:\s*(\d+)", text, re.M)
    if m:
        out["n_iter"] = int(m.group(1))
    m = re.search(r"^Overall NLP error\.*:\s*([0-9.eE+-]+)", text, re.M)
    if m:
        out["nlp_error"] = m.group(1)
    m = re.search(r"^Constraint violation\.*:\s*([0-9.eE+-]+)", text, re.M)
    if m:
        out["constr_viol"] = m.group(1)
    return out


def main():
    mode = parse_mode(sys.argv)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("D8R_OF REFUSE producer md5 %s != frozen %s\n" % (got, PRODUCER_MD5))
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D8R_OF REFUSE anchor %r appears %d times\n" % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_driver", "-optimizer", "IPOPT"]
    ns = {"__name__": "d8r_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    Top = ns["Top"]
    OptFuncs = ns["OptFuncs"]
    daOptions = ns["daOptions"]
    CL_target = float(ns["CL_target"])
    jsonl = JSONL_F if mode == "F" else "d8r_O.jsonl"

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
          "transonicPCOption": daOptions.get("transonicPCOption"),
          "primalMinResTolDiff": daOptions.get("primalMinResTolDiff"),
          "U0": ns.get("U0"), "aoa0": ns.get("aoa0"), "T0": ns.get("T0"), "p0": ns.get("p0"),
          "CL_target": CL_target, "max_iter_registered": MAX_ITER, "scenario": SCENARIO, **ident})

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    CD = "%s.aero_post.CD" % SCENARIO
    CL = "%s.aero_post.CL" % SCENARIO
    DVS = ("twist", "patchV")

    def dvs_now():
        return {k: [float(v) for v in np.atleast_1d(np.array(prob.get_val(k), dtype=float))] for k in DVS}

    def primal(tag):
        t0 = time.time()
        prob.run_model()
        cd = float(prob.get_val(CD)[0])
        cl = float(prob.get_val(CL)[0])
        emit({"kind": "primal", "tag": tag, "CD": repr(cd), "CL": repr(cl),
              "wall_s": round(time.time() - t0, 3)})
        return cd, cl

    if mode == "O":
        optFuncs = OptFuncs(daOptions, prob)
        prob.driver = om.pyOptSparseDriver()
        prob.driver.options["optimizer"] = "IPOPT"
        prob.driver.opt_settings = dict(IPOPT_OPTS)
        prob.driver.options["debug_print"] = ["nl_cons", "objs", "desvars"]
        prob.driver.options["print_opt_prob"] = True
        prob.driver.hist_file = "OptView.hst"
        emit({"kind": "driver", "optimizer": "IPOPT", "opt_settings": IPOPT_OPTS, "trim": TRIM})

        cd_cold, cl_cold = primal("cold")
        emit({"kind": "cold", "CD": repr(cd_cold), "CL": repr(cl_cold), "dvs": dvs_now()})
        t0 = time.time()
        optFuncs.findFeasibleDesign([CL], ["patchV"], targets=[CL_target], designVarsComp=[1],
                                    epsFD=TRIM["epsFD"], tol=TRIM["tol"], maxIter=TRIM["maxIter"])
        emit({"kind": "trim_done", "wall_s": round(time.time() - t0, 3)})
        cd_s, cl_s = primal("start")
        dv_s = dvs_now()
        emit({"kind": "start", "CD": repr(cd_s), "CL": repr(cl_s), "dvs": dv_s})

        t0 = time.time()
        prob.run_driver()
        wall_drv = round(time.time() - t0, 3)
        cd_f = float(prob.get_val(CD)[0])
        cl_f = float(prob.get_val(CL)[0])
        dv_f = dvs_now()
        ip = read_ipopt_terminus(IPOPT_OPTS["output_file"]) if rank == 0 else None
        ip = MPI.COMM_WORLD.bcast(ip, root=0)
        emit({"kind": "run_driver_done", "wall_s": wall_drv, "CD": repr(cd_f), "CL": repr(cl_f),
              "dvs": dv_f, "ipopt": ip})

        # endpoint re-evaluation at the FINAL design (D8's form), then the endpoint adjoint
        for k in DVS:
            prob.set_val(k, np.array(dv_f[k]))
        cd_e, cl_e = primal("endpoint")
        t0 = time.time()
        totals = prob.compute_totals(of=[CD, CL], wrt=list(DVS))
        emit({"kind": "compute_totals", "wall_s": round(time.time() - t0, 3)})
        jadj = {}
        for of_name, of_key in ((CD, "CD"), (CL, "CL")):
            jadj[of_key] = {}
            for dv in DVS:
                arr = np.atleast_1d(np.array(totals[(of_name, dv)]).ravel())
                jadj[of_key][dv] = [repr(float(v)) for v in arr]
                emit({"kind": "adjoint", "of": of_key, "dv": dv, "n": int(arr.size), "values": jadj[of_key][dv]})
        if rank == 0:
            out = {"item": ITEM, "mode": "O", "producer_md5": got, "nprocs": nprocs, "identity": ident,
                   "max_iter_registered": MAX_ITER, "opt_settings": IPOPT_OPTS, "trim": TRIM,
                   "CD_cold": repr(cd_cold), "CL_cold": repr(cl_cold),
                   "CD_start": repr(cd_s), "CL_start": repr(cl_s), "dvs_start": dv_s,
                   "CD_final": repr(cd_f), "CL_final": repr(cl_f), "dvs_final": dv_f,
                   "CD_endpoint": repr(cd_e), "CL_endpoint": repr(cl_e),
                   "ipopt": ip, "wall_run_driver_s": wall_drv, "adjoint": jadj}
            with open(OUT_O, "w") as fh:
                json.dump(out, fh, indent=1, sort_keys=True)
                fh.flush()
                os.fsync(fh.fileno())
            sys.stdout.write("D8R_IPOPT_TERMINUS %r n_iter=%r\n" % (ip.get("exit_line"), ip.get("n_iter")))
            sys.stdout.write("D8R_O_WRITTEN %s\n" % OUT_O)
        MPI.COMM_WORLD.Barrier()
        return

    # ---- mode F: the SAME ROW's endpoint, eta, then central differences ---------
    if not os.path.isfile(ENDPOINT_IN):
        sys.stderr.write("D8R_OF REFUSE endpoint file %s absent (the launcher copies the O arm's d8r_O.json)\n" % ENDPOINT_IN)
        sys.exit(2)
    ep = json.load(open(ENDPOINT_IN))
    if ep.get("item") != ITEM or ep.get("mode") != "O" or "dvs_final" not in ep:
        sys.stderr.write("D8R_OF REFUSE endpoint file is not a D8R mode-O artefact\n")
        sys.exit(2)
    ep_md5 = md5_of(ENDPOINT_IN)
    base = {k: np.array(ep["dvs_final"][k], dtype=float).copy() for k in DVS}
    for k in DVS:
        prob.set_val(k, base[k].copy())
    emit({"kind": "endpoint_loaded", "endpoint_md5": ep_md5, "CD_final_O": ep.get("CD_final"),
          "dvs": {k: [repr(float(v)) for v in base[k]] for k in DVS}})

    cd0, cl0 = primal("baseline")
    cd0r, cl0r = primal("baseline_repeat")
    eta_raw = abs(cd0 - cd0r)
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta), "eta_floored": eta_flagged,
          "CD_baseline": repr(cd0), "CD_repeat": repr(cd0r), "CL_baseline": repr(cl0), "CL_repeat": repr(cl0r)})

    def set_perturbed(dv, idx, delta):
        for k in DVS:
            prob.set_val(k, base[k].copy())
        v = base[dv].copy()
        v[idx] += delta
        prob.set_val(dv, v)

    rows = []
    for dv, idx in COMPONENTS:
        if idx >= base[dv].size:
            rows.append({"dv": dv, "idx": idx, "status": "ABSENT", "n_available": int(base[dv].size), "fd": {}})
            continue
        fd = {}
        for s in STEPS[dv]:
            key = repr(s)
            try:
                set_perturbed(dv, idx, +s)
                cdp, clp = primal("%s[%d]+%g" % (dv, idx, s))
                set_perturbed(dv, idx, -s)
                cdm, clm = primal("%s[%d]-%g" % (dv, idx, s))
                fd[key] = {"step": s, "dCD": repr((cdp - cdm) / (2.0 * s)), "dCL": repr((clp - clm) / (2.0 * s)),
                           "CD_plus": repr(cdp), "CD_minus": repr(cdm), "CL_plus": repr(clp), "CL_minus": repr(clm), "ok": True}
            except Exception as exc:                      # noqa: BLE001
                fd[key] = {"step": s, "ok": False, "error": repr(exc)[:400]}
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "step": s, "row": fd[key]})
        rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
    for k in DVS:
        prob.set_val(k, base[k].copy())

    ctrl = {"dv": "CTRL", "idx": 0, "status": "CONTROL", "fd": {
        repr(CTRL_STEP): {"step": CTRL_STEP, "dCD": repr(0.0), "dCL": repr(0.0),
                          "CD_plus": repr(cd0), "CD_minus": repr(cd0), "CL_plus": repr(cl0), "CL_minus": repr(cl0), "ok": True,
                          "note": "synthetic: identical DVs on both sides -> derivative exactly 0"}},
        "planted": {"step": CTRL_STEP, "plant": PLANT, "dCD": repr(PLANT / (2.0 * CTRL_STEP)),
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
            sys.stderr.write("D8R_OF REFUSE planted-zero control not seen on read-back: zero=%r plant=%r want=%r\n"
                             % (seen_zero, seen_plant, want))
            sys.exit(2)
        sys.stdout.write("D8R_PLANTED_ZERO_CONTROL_SEEN zero=%r plant=%r\n" % (seen_zero, seen_plant))
        out = {"item": ITEM, "mode": "F", "producer_md5": got, "nprocs": nprocs, "identity": ident,
               "endpoint_source": {"file": ENDPOINT_IN, "md5": ep_md5, "CD_final_O": ep.get("CD_final"),
                                   "ipopt_exit_line_O": (ep.get("ipopt") or {}).get("exit_line")},
               "components_requested": [[d, i] for (d, i) in COMPONENTS], "n_components_requested": len(COMPONENTS),
               "steps": STEPS, "ctrl_step": CTRL_STEP, "plant": PLANT,
               "CD_baseline": repr(cd0), "CL_baseline": repr(cl0), "CD_baseline_repeat": repr(cd0r), "CL_baseline_repeat": repr(cl0r),
               "eta_raw": repr(eta_raw), "eta_used": repr(eta), "eta_floored": eta_flagged,
               "baseline_dvs": {k: [repr(float(v)) for v in base[k]] for k in DVS},
               "rows": rows, "n_rows": len(rows)}
        with open(OUT_F, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("D8R_F_WRITTEN %s n_rows=%d\n" % (OUT_F, len(rows)))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
