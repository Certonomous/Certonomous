#!/usr/bin/env python
"""Curriculum D19R PHASE 1 -- the RE-BRACKETED FD PLATEAU instrument on D15's ground.

DERIVED FROM `curriculum_D19/d19_xf.py` (md5 asserted below) with EXACTLY these
registered deltas and no others.  D19's file is FROZEN and is not edited.

  * THE SWEEP IS EIGHT HALF-DECADE LEVELS, NOT FIVE DECADES
    (PREREGISTRATION.md section 4.1):
        shape  : 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5
        patchV : 3e-1, 1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4
    THE BRACKET IS UNCHANGED FROM D19.  What changed is the SPACING.  D19's own
    five-level sweep measured `shape[7]` on `CD` CHANGING SIGN between 1e-4 and
    1e-5 (-1.618542e-04 -> +2.660843e-04) and degrading away from 1e-3 toward
    BOTH ends, and `A_stepsize_study.md` records the primal FAILS at 5e-2 and
    1e-1.  Widening is measured-worse in both directions; only the spacing was
    left unmeasured, because a flat narrower than a decade is invisible to a
    decade grid.

  * FIVE MODES, `-mode X|S8|N2|S1|R1`:
      X   -- the adjoint (compute_totals) at the BASELINE design.  Arm `X2`.
      S8  -- the EIGHT-level sweep, 5 components, both functions.  Arm `S8`, np=2.
      N2  -- PERTURBED-MESH REPEATABILITY.  Arm `N2`, np=2.  Re-runs the primal
             THREE TIMES at each perturbed design point.  This is the noise floor
             `D15_D16_FD_STEP_TABLE.md` section 1.2 says has NEVER been measured:
             `eta` measures rerun determinism ON THE SAME MESH, not "the
             convergence-tolerance scatter of a primal restarted on a PERTURBED
             mesh, which is the noise that actually matters and which these
             artefacts do not measure at all."  A MEASUREMENT arm; grades nothing.
      S1  -- the SELECTED step only, serial, for G19R-1d.  Arm `S1`, np=1.
      R1  -- SENSITIVITY-EQUALISED STEP DIAGNOSTIC, `shape[7]` only.  Arm `R1`,
             np=1.  NON-GRADED (PREREGISTRATION.md section 4.3).

  * `kappa` FOR MODE R1 IS COMPUTED FROM FD AND FROM NOTHING ELSE -- never from
    the adjoint -- so `DAFOAM_CHARTER.md` section 3's prohibition on "Selecting
    the step after seeing which one agrees" is enforced by the DATA FLOW and not
    by the author's intention.  Mode R1 reads `d19r_S.json`'s `rows[].fd`; it
    never opens `d19r_X.json`.

  * THE PLANTED-ZERO CONTROL IS SIZED RELATIVE (CLAUDE.md rule 3; G19R-1c):
        plant = K * (band/100) * |d_ref|,   K = 5.0 REGISTERED AT FREEZE
    D15's and D19's control was the bare ABSOLUTE 1.234e-03.  `SO-2M` was lost to
    exactly that: an absolute plant that turned out to be 2.48 % of its own
    reference and COULD NOT CROSS ITS OWN 5 % BAND.  A plant that cannot cross
    the band it is judged by proves nothing.  The refusal is unchanged in
    mechanism: the control row is written, READ BACK FROM DISK, and the
    instrument EXITS 2 if the read-back cannot see the plant.
    AND THE SUFFICIENCY LEG IS DRIVEN RED at K_shrunk = 0.5, which must NOT cross
    -- a control that reports "crossed" at every plant size measures nothing.

  * THIS INSTRUMENT WRITES NO ADJOINT INTO ANY SWEEP ARTEFACT.  Modes S8/N2/S1/R1
    carry `rows[].fd` and nothing derived from `compute_totals`; mode X writes a
    SEPARATE file the selector never opens.  The selector asserts this at entry.

SINGLE-POINT, SINGLE DIRECTORY, AND WHY THAT IS STILL SAFE.  D19's reasoning is
inherited unchanged: SO-3aR died because three multipoint scenarios shared one
case directory and each renamed its solution to `0.0001`
(`pyDAFoam.renameSolution`).  D19R is SINGLE-POINT -- one scenario, one `prob`,
perturbed primals strictly sequential inside one arm directory.  The collision
class needs two writers; this has one.  Every ARM gets its own staged tree and
the launcher refuses to stage over a live one.

AND WHAT D19 MEASURED ABOUT THAT DIRECTORY, WHICH THIS INSTRUMENT DOES NOT PRETEND
AWAY.  DAFoam DOES rewrite `0/U` mid-run: the `patchV` DV is applied by rewriting
the inlet boundary condition, and OpenFOAM writes the whole object -- converged
internalField included -- under `writeCompression`.  D19's `S1/0/U.gz` ended the
run holding `nonuniform List<vector> 4032` against a staged `uniform (100 0 0)`,
and `S2/processor0/0/U.gz` did the same.  The CONSEQUENCE for the FD answer was
bounded by varying the warm-start history rather than by assuming a bound: S1
(12-primal chain, mutated case `0/`) vs S2 (52-primal, processor `0/`) agreed to
worst 0.041027 %, and S2 vs D15's independently-run `F-P` to worst 0.003385 %.
Three histories, one number.  `G19R-1d` re-tests it live at 2.0 % on this item's
own data rather than resting on D19's.
"""
import hashlib
import json
import os
import sys
import time

PRODUCER = "d19r_runScript.py"
PRODUCER_MD5 = "a5e18503ea29d0e37c3cf1668533cd34"
# The header ABOVE the anchor is what this instrument execs.  Byte-identical to
# D15's and D19's producer header; G19R-1a rests on that, so it is ASSERTED.
HEADER_MD5_SHARED_WITH_D15 = "d1efc43583fbeb59fb5116816b055a07"
ANCHOR = "# OpenMDAO setup"
ITEM = "D19R"

# ---- registered constants (PREREGISTRATION.md section 4.1) -------------------
ETA_FLOOR = 1.0e-14
STEPS_SWEEP = {
    "shape":  [3.0e-2, 1.0e-2, 3.0e-3, 1.0e-3, 3.0e-4, 1.0e-4, 3.0e-5, 1.0e-5],
    "patchV": [3.0e-1, 1.0e-1, 3.0e-2, 1.0e-2, 3.0e-3, 1.0e-3, 3.0e-4, 1.0e-4],
}
# The five levels shared with D19, named so the reproduction subset (G19R-1a) is
# explicit and is not re-derived by intersecting two lists at grading time.
STEPS_D19 = {"shape":  [3.0e-2, 1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5],
             "patchV": [3.0e-1, 1.0e-1, 1.0e-2, 1.0e-3, 1.0e-4]}
COMPONENTS = [("shape", 0), ("shape", 3), ("shape", 6), ("shape", 7), ("patchV", 1)]

# ---- G19R-1c: the RELATIVE plant --------------------------------------------
CTRL_STEP = 1.0e-3
PLANT_K = 5.0                 # sufficiency: must cross the band with a 5x margin
PLANT_K_SHRUNK = 0.5          # sufficiency RED leg: must NOT cross
PLATEAU_TOL_PCT = 10.0        # the band the plant is sized against (G19R-1b)

# ---- arm N2 (PREREGISTRATION.md section 4.2) --------------------------------
N2_COMPONENTS = [("shape", 7), ("shape", 6)]   # the suspect, and the flat contrast
N2_STEPS = [1.0e-3, 1.0e-4]
N2_REPEATS = 3

# ---- arm R1 (PREREGISTRATION.md section 4.3) --------------------------------
R1_COMPONENT = ("shape", 7)
R1_KAPPA_REF = ("shape", 6)   # kappa = |FD(CD, shape[6])| / |FD(CD, shape[7])| at 1e-3
R1_KAPPA_STEP = 1.0e-3
R1_BASE_LADDER = [1.0e-3, 3.0e-4, 1.0e-4, 3.0e-5]
R1_STEP_CEILING = 3.0e-2      # A_stepsize_study.md: the primal FAILS at 5e-2 and 1e-1

SELECTED = "d19r_selected_step.json"
SWEEP_ARTEFACT = "d19r_S.json"
OUT = {"X": "d19r_X.json", "S8": "d19r_S.json", "N2": "d19r_N.json",
       "S1": "d19r_S1.json", "R1": "d19r_R1.json"}
MODES = tuple(OUT)


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
    if mode not in MODES:
        sys.stderr.write("D19R_XF usage: d19r_xf.py -mode %s\n" % "|".join(MODES))
        sys.exit(64)
    return mode


def plant_relative(d_ref, band_pct, k):
    """G19R-1c's registered formula.  Identical to d19r_age_guard.plant_relative."""
    return k * (band_pct / 100.0) * abs(d_ref)


def read_fd_value(path, dv, idx, of, step):
    """Read ONE FD number out of a sweep artefact.  Used only by mode R1 for
    `kappa`, and it REFUSES if the document declares itself adjoint-bearing --
    so no adjoint quantity can reach a step choice in this item."""
    doc = json.load(open(path))
    if doc.get("contains_adjoint") is not False:
        sys.stderr.write("D19R_XF REFUSE %s does not declare contains_adjoint=false\n" % path)
        sys.exit(2)
    for row in doc.get("rows", []):
        if row.get("dv") == dv and row.get("idx") == idx:
            for _k, v in row.get("fd", {}).items():
                if abs(float(v["step"]) - step) < 1e-15 and v.get("ok"):
                    return float(v["dCD" if of == "CD" else "dCL"])
    sys.stderr.write("D19R_XF REFUSE no ok FD value for %s[%d]/%s at step %r in %s\n"
                     % (dv, idx, of, step, path))
    sys.exit(2)


def main():
    mode = parse_mode(sys.argv)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("D19R_XF REFUSE producer md5 %s != frozen %s\n" % (got, PRODUCER_MD5))
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D19R_XF REFUSE anchor %r appears %d times\n" % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]
    hmd5 = hashlib.md5(header.encode()).hexdigest()
    if hmd5 != HEADER_MD5_SHARED_WITH_D15:
        sys.stderr.write("D19R_XF REFUSE producer header md5 %s != D15's %s -- G19R-1a "
                         "reproduction cannot be claimed against a different header\n"
                         % (hmd5, HEADER_MD5_SHARED_WITH_D15))
        sys.exit(2)
    sys.stdout.write("D19R_HEADER_IDENTICAL_TO_D15 md5=%s\n" % hmd5)

    # ---- mode S1 reads the SELECTOR's frozen choice; it invents no step -------
    sel = None
    if mode == "S1":
        if not os.path.isfile(SELECTED):
            sys.stderr.write("D19R_XF REFUSE mode S1 needs %s (written by d19r_select_step.py)\n"
                             % SELECTED)
            sys.exit(2)
        selj = json.load(open(SELECTED))
        sel = {"shape": float(selj["s_star"]["shape"]), "patchV": float(selj["s_star"]["patchV"])}
        for dv in ("shape", "patchV"):
            if sel[dv] not in STEPS_SWEEP[dv]:
                sys.stderr.write("D19R_XF REFUSE selected %s step %r is not in the frozen sweep %r\n"
                                 % (dv, sel[dv], STEPS_SWEEP[dv]))
                sys.exit(2)
        if selj.get("selector_saw_adjoint") is not False:
            sys.stderr.write("D19R_XF REFUSE selection artefact does not assert the selector was "
                             "adjoint-blind\n")
            sys.exit(2)
        sys.stdout.write("D19R_S1_USING_SELECTED_STEP shape=%r patchV=%r\n"
                         % (sel["shape"], sel["patchV"]))

    # ---- mode R1 computes kappa FROM FD, never from the adjoint ---------------
    kappa, r1_ladder = None, None
    if mode == "R1":
        if not os.path.isfile(SWEEP_ARTEFACT):
            sys.stderr.write("D19R_XF REFUSE mode R1 needs %s from arm S8\n" % SWEEP_ARTEFACT)
            sys.exit(2)
        num = abs(read_fd_value(SWEEP_ARTEFACT, R1_KAPPA_REF[0], R1_KAPPA_REF[1],
                                "CD", R1_KAPPA_STEP))
        den = abs(read_fd_value(SWEEP_ARTEFACT, R1_COMPONENT[0], R1_COMPONENT[1],
                                "CD", R1_KAPPA_STEP))
        if den <= 0.0:
            sys.stderr.write("D19R_XF REFUSE mode R1 kappa denominator is zero\n")
            sys.exit(2)
        kappa = num / den
        r1_ladder = [s for s in (kappa * b for b in R1_BASE_LADDER) if s <= R1_STEP_CEILING]
        if not r1_ladder:
            sys.stderr.write("D19R_XF REFUSE mode R1 ladder is empty after the %r ceiling "
                             "(kappa=%r)\n" % (R1_STEP_CEILING, kappa))
            sys.exit(2)
        sys.stdout.write("D19R_R1_KAPPA_FROM_FD kappa=%.6f ladder=%r n_truncated=%d ceiling=%r\n"
                         % (kappa, r1_ladder, len(R1_BASE_LADDER) - len(r1_ladder), R1_STEP_CEILING))

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d19r_frozen_header", "__file__": PRODUCER}
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
          "p0": ns.get("p0"), "kappa": kappa, **ident})

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

    def set_perturbed(dv, idx, delta):
        for k in ("shape", "patchV"):
            prob.set_val(k, base[k].copy())
        v = base[dv].copy()
        v[idx] += delta
        prob.set_val(dv, v)

    cd0, cl0 = primal("baseline")

    # ======================= mode X: the adjoint ==============================
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
            sys.stdout.write("D19R_X_WRITTEN %s\n" % OUT["X"])
        MPI.COMM_WORLD.Barrier()
        return

    # ---- eta: same-mesh rerun determinism.  NAMED for what it is -------------
    cd0r, cl0r = primal("baseline_repeat")
    eta_raw = abs(cd0 - cd0r)
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flagged, "CD_baseline": repr(cd0),
          "CD_repeat": repr(cd0r), "CL_baseline": repr(cl0), "CL_repeat": repr(cl0r),
          "note": "SAME-MESH rerun determinism.  D15_D16_FD_STEP_TABLE.md section 1.2 "
                  "records this as the WEAKEST bound available and NOT the noise that "
                  "matters for a perturbed-mesh FD.  Arm N2 measures that one."})

    # ======================= mode N2: perturbed-mesh repeatability ============
    if mode == "N2":
        rows = []
        for dv, idx in N2_COMPONENTS:
            if idx >= base[dv].size:
                rows.append({"dv": dv, "idx": idx, "status": "ABSENT", "reps": {}})
                continue
            reps = {}
            for s in N2_STEPS:
                for sign, sname in ((+1.0, "plus"), (-1.0, "minus")):
                    key = "%r/%s" % (s, sname)
                    vals_cd, vals_cl = [], []
                    for r in range(N2_REPEATS):
                        try:
                            set_perturbed(dv, idx, sign * s)
                            cdp, clp = primal("N2 %s[%d]%s%g rep%d"
                                              % (dv, idx, sname, s, r))
                            vals_cd.append(cdp)
                            vals_cl.append(clp)
                        except Exception as exc:              # noqa: BLE001
                            emit({"kind": "n2_error", "dv": dv, "idx": idx, "step": s,
                                  "sign": sname, "rep": r, "error": repr(exc)[:400]})
                    if len(vals_cd) < 2:
                        reps[key] = {"step": s, "sign": sname, "ok": False,
                                     "n": len(vals_cd)}
                        continue
                    scat_cd = max(vals_cd) - min(vals_cd)
                    scat_cl = max(vals_cl) - min(vals_cl)
                    reps[key] = {"step": s, "sign": sname, "ok": True,
                                 "n": len(vals_cd),
                                 "CD": [repr(v) for v in vals_cd],
                                 "CL": [repr(v) for v in vals_cl],
                                 "scatter_CD_abs": repr(scat_cd),
                                 "scatter_CL_abs": repr(scat_cl),
                                 "scatter_CD_over_eta": repr(scat_cd / eta)}
                    emit({"kind": "n2_point", "dv": dv, "idx": idx, "row": reps[key]})
            rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "reps": reps})
        for k in ("shape", "patchV"):
            prob.set_val(k, base[k].copy())
        if rank == 0:
            out = {"item": ITEM, "mode": "N2", "producer_md5": got, "header_md5": hmd5,
                   "nprocs": nprocs, "identity": ident,
                   "components": [[d, i] for (d, i) in N2_COMPONENTS],
                   "steps": N2_STEPS, "repeats": N2_REPEATS,
                   "CD_baseline": repr(cd0), "CL_baseline": repr(cl0),
                   "CD_baseline_repeat": repr(cd0r), "CL_baseline_repeat": repr(cl0r),
                   "eta_raw": repr(eta_raw), "eta_used": repr(eta),
                   "eta_floored": eta_flagged, "rows": rows, "n_rows": len(rows),
                   "contains_adjoint": False,
                   "grades_nothing": True,
                   "purpose": "the PERTURBED-MESH noise floor, which "
                              "D15_D16_FD_STEP_TABLE.md section 1.2 states these "
                              "artefacts do not measure at all"}
            with open(OUT["N2"], "w") as fh:
                json.dump(out, fh, indent=1, sort_keys=True)
                fh.flush()
                os.fsync(fh.fileno())
            sys.stdout.write("D19R_N2_WRITTEN %s n_rows=%d\n" % (OUT["N2"], len(rows)))
        MPI.COMM_WORLD.Barrier()
        return

    # ======================= modes S8 / S1 / R1: central differences ==========
    if mode == "S8":
        plan = [(dv, idx, list(STEPS_SWEEP[dv])) for dv, idx in COMPONENTS]
    elif mode == "S1":
        plan = [(dv, idx, [sel[dv]]) for dv, idx in COMPONENTS]
    else:                                                     # R1
        plan = [(R1_COMPONENT[0], R1_COMPONENT[1], list(r1_ladder))]

    rows = []
    for dv, idx, steps in plan:
        if idx >= base[dv].size:
            rows.append({"dv": dv, "idx": idx, "status": "ABSENT",
                         "n_available": int(base[dv].size), "fd": {}})
            continue
        fd = {}
        for s in steps:
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
            except Exception as exc:                          # noqa: BLE001
                # A FAILED STEP IS A ROW, NOT A GAP.  VERIFICATION_CHARTER.md
                # section 7: "A sweep that hides its failed steps is reporting a
                # plateau it did not measure."
                fd[key] = {"step": s, "ok": False, "error": repr(exc)[:400]}
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "step": s, "row": fd[key]})
        rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
    for k in ("shape", "patchV"):
        prob.set_val(k, base[k].copy())

    # ---- G19R-1c: the RELATIVE planted control, BOTH LEGS --------------------
    d_ref = cd0                       # the quantity the control perturbs
    plant = plant_relative(d_ref, PLATEAU_TOL_PCT, PLANT_K)
    plant_shrunk = plant_relative(d_ref, PLATEAU_TOL_PCT, PLANT_K_SHRUNK)
    moved_pp = abs(plant) / abs(d_ref) * 100.0
    moved_pp_shrunk = abs(plant_shrunk) / abs(d_ref) * 100.0
    ctrl = {"dv": "CTRL", "idx": 0, "status": "CONTROL", "fd": {
        repr(CTRL_STEP): {"step": CTRL_STEP, "dCD": repr(0.0), "dCL": repr(0.0),
                          "CD_plus": repr(cd0), "CD_minus": repr(cd0),
                          "CL_plus": repr(cl0), "CL_minus": repr(cl0), "ok": True,
                          "note": "synthetic: identical DVs on both sides -> derivative exactly 0"}},
        "planted": {"step": CTRL_STEP, "plant": repr(plant), "K": PLANT_K,
                    "band_pct": PLATEAU_TOL_PCT, "d_ref": repr(d_ref),
                    "formula": "plant = K * (band/100) * |d_ref|",
                    "moved_pp": repr(moved_pp),
                    "crosses_band": bool(moved_pp > PLATEAU_TOL_PCT),
                    "dCD": repr(plant / (2.0 * CTRL_STEP)),
                    "CD_plus": repr(cd0 + plant), "CD_minus": repr(cd0), "ok": True},
        "planted_shrunk": {"step": CTRL_STEP, "plant": repr(plant_shrunk),
                           "K": PLANT_K_SHRUNK, "band_pct": PLATEAU_TOL_PCT,
                           "moved_pp": repr(moved_pp_shrunk),
                           "crosses_band": bool(moved_pp_shrunk > PLATEAU_TOL_PCT),
                           "dCD": repr(plant_shrunk / (2.0 * CTRL_STEP)),
                           "note": "SUFFICIENCY RED LEG -- must NOT cross the band"}}
    emit({"kind": "control", "row": ctrl})
    rows.append(ctrl)

    if rank == 0:
        seen_zero = seen_plant = seen_shrunk = None
        with open(jsonl) as fh:
            for line in fh:
                rec = json.loads(line)
                if rec.get("kind") == "control":
                    r = rec["row"]
                    seen_zero = float(r["fd"][repr(CTRL_STEP)]["dCD"])
                    seen_plant = float(r["planted"]["dCD"])
                    seen_shrunk = float(r["planted_shrunk"]["dCD"])
        want = plant / (2.0 * CTRL_STEP)
        want_shrunk = plant_shrunk / (2.0 * CTRL_STEP)
        if (seen_zero != 0.0 or seen_plant is None
                or abs(seen_plant - want) > 1e-12 * abs(want)
                or seen_shrunk is None
                or abs(seen_shrunk - want_shrunk) > 1e-12 * abs(want_shrunk)):
            sys.stderr.write("D19R_XF REFUSE planted-zero control not seen on read-back: "
                             "zero=%r plant=%r want=%r shrunk=%r want_shrunk=%r\n"
                             % (seen_zero, seen_plant, want, seen_shrunk, want_shrunk))
            sys.exit(2)
        # SUFFICIENCY, both directions.  A control that crosses at every plant
        # size is not measuring crossing.
        if not moved_pp > PLATEAU_TOL_PCT:
            sys.stderr.write("D19R_XF REFUSE plant at K=%r moves %.4f pp and does NOT cross "
                             "the %.1f pp band -- this is the SO-2M failure\n"
                             % (PLANT_K, moved_pp, PLATEAU_TOL_PCT))
            sys.exit(2)
        if moved_pp_shrunk > PLATEAU_TOL_PCT:
            sys.stderr.write("D19R_XF REFUSE shrunken plant at K=%r moves %.4f pp and DOES cross "
                             "the %.1f pp band -- the control is not measuring crossing\n"
                             % (PLANT_K_SHRUNK, moved_pp_shrunk, PLATEAU_TOL_PCT))
            sys.exit(2)
        sys.stdout.write("D19R_PLANTED_CONTROL_SEEN zero=%r K=%r moved=%.4f pp CROSSES "
                         "| K_shrunk=%r moved=%.4f pp DOES NOT CROSS (band %.1f pp)\n"
                         % (seen_zero, PLANT_K, moved_pp, PLANT_K_SHRUNK,
                            moved_pp_shrunk, PLATEAU_TOL_PCT))
        out = {
            "item": ITEM, "mode": mode, "producer_md5": got, "header_md5": hmd5,
            "nprocs": nprocs, "identity": ident,
            "components_requested": [[d, i] for (d, i, _s) in plan],
            "n_components_requested": len(plan),
            "steps": {dv: steps for (dv, _i, steps) in plan},
            "steps_sweep_registered": STEPS_SWEEP,
            "steps_shared_with_d19": STEPS_D19,
            "selected_step": sel,
            "kappa": kappa, "r1_ladder": r1_ladder,
            "ctrl_step": CTRL_STEP,
            "plant": repr(plant), "plant_K": PLANT_K,
            "plant_shrunk": repr(plant_shrunk), "plant_K_shrunk": PLANT_K_SHRUNK,
            "plant_band_pct": PLATEAU_TOL_PCT,
            "plant_moved_pp": repr(moved_pp), "plant_moved_pp_shrunk": repr(moved_pp_shrunk),
            "CD_baseline": repr(cd0), "CL_baseline": repr(cl0),
            "CD_baseline_repeat": repr(cd0r), "CL_baseline_repeat": repr(cl0r),
            "eta_raw": repr(eta_raw), "eta_used": repr(eta), "eta_floored": eta_flagged,
            "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]],
                             "patchV": [repr(float(v)) for v in base["patchV"]]},
            "rows": rows, "n_rows": len(rows),
            "contains_adjoint": False,
            "grades_nothing": bool(mode == "R1"),
        }
        if mode == "R1":
            out["diagnostic_only"] = (
                "PREREGISTRATION.md section 4.3: R1 CANNOT produce a PASS, cannot change "
                "any gate, and cannot be cited as a plateau.  kappa is computed from FD "
                "and from nothing else.  This artefact never reaches the selector.")
        with open(OUT[mode], "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("D19R_%s_WRITTEN %s n_rows=%d\n" % (mode, OUT[mode], len(rows)))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
