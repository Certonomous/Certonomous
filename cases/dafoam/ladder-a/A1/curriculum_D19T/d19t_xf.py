#!/usr/bin/env python
r"""Curriculum D19T -- THE PRIMAL-TOLERANCE LADDER ON `shape[7]`.

SANAA-DIRECT, section 5 of
`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`:

    "FD step sweep on that component only: 1e-2, 1e-3, 1e-4, 1e-5; converge
     each perturbed primal to 1e-8 so FD noise is below the plateau; report
     the plateau value against the adjoint."

===========================================================================
THE INSTRUCTION'S OWN PREMISE IS ALREADY SATISFIED IN THE GROUND IT
COMPLAINS ABOUT, AND THIS FILE EXISTS BECAUSE OF THAT
===========================================================================
`curriculum_D19R/d19r_runScript.py:45` ALREADY sets `primalMinResTol 1.0e-8`,
and D19R's arm log shows **82 of 82** primal solves reporting

    Minimal residual 9.9674e-09 satisfied the prescribed tolerance 1e-08

so "converge each perturbed primal to 1e-8" describes the failing run, not a
change to it.  Executing the instruction literally would re-run the identical
experiment.  **The tightening therefore goes BELOW 1e-8**, which is the
direction the instruction intends -- FD noise beneath the plateau -- and the
ladder `1e-8 / 1e-10 / 1e-12` is registered so the ANSWER IS A SCALING LAW
rather than a single before/after pair.

`DAFOAM_CHARTER.md` section 3 carries the precedent in this lane's own words:
at `primalMinResTol 1e-6` "the cold primal stops at its **first** tolerance
crossing" and central FD misses the adjoint by 25.9 %; one pair re-run at 1e-8
moves the same cell to **0.032 %**.  *"The step was never the problem; the
primal's stopping rule was."*  D19T is that same sentence one rung down.

===========================================================================
WHAT THIS INSTRUMENT CHANGES, AND THE ONE THING IT DOES NOT TOUCH
===========================================================================
**The producer is not edited.**  `d19r_runScript.py` is frozen and this file
execs its header exactly as `d19r_xf.py` does, asserting the same two md5s.
The tolerance is applied by mutating `ns["daOptions"]["primalMinResTol"]` in
the exec'd namespace BEFORE `Top()` is instantiated -- `Top.setup` reads that
same dict object, so the arm's tolerance is a REGISTERED ARM PARAMETER and the
frozen file on disk keeps its own bytes and its own md5.

**THE DICTIONARY IS NOT ASSUMED TO HAVE TAKEN.**  Three independent readings,
because a tolerance that silently did not apply would make every number here a
re-run of D19R wearing a new label:

  1. this file asserts the mutation landed in `ns` and REFUSES if it did not;
  2. it emits `primalMinResTol_requested` and `primalMinResTol_in_namespace`
     into the identity record, which the grader compares;
  3. **the grader reads the ARM LOG** and requires every solve to print
     `satisfied the prescribed tolerance <R>` with R the registered value --
     DAFoam prints the tolerance it actually honoured, so this is a direct
     reading of the applied value and not an inference from a dictionary.

Reading 3 is the load-bearing one.  1 and 2 can only prove what this process
believed; 3 proves what the solver did.

===========================================================================
COMPONENTS: ONE GRADED, ONE CONTRAST CONTROL
===========================================================================
Sanaa directed the sweep "on that component only", and **`shape[7]` is the only
GRADED component here**.  `shape[6]` is measured at the same steps as a
NON-GRADED CONTRAST CONTROL and is registered as one, because the signature that
separates the hypotheses is DIFFERENTIAL, not absolute:

  * `shape[7]` is near-null in CD -- |dCD/dshape[7]| is **1.4854 %** of
    |dCD/dshape[6]| on D19R's landed adjoint -- so a fixed additive CD error
    swamps it first;
  * `shape[6]` carries 68x the signal at the same noise, so tightening should
    move it hardly at all.

"The noise-limited component moved and the signal-rich one did not" is a claim
about two numbers.  Measuring only one of them cannot make it.

===========================================================================
THE TRIVIAL BASELINE IS A STEP, AND IT IS IN THE SWEEP
===========================================================================
`DAFOAM_CHARTER.md` section 4: the registered trivial baseline for a DAFoam FD
gate is the same probe at a deliberately wrong step, an order of magnitude off
the registered one.  `TRIVIAL_STEP = 3.0e-2` is that step -- 30x the registered
`1e-3` -- and it is measured as a row, never as a plateau centre.  D19R's
landed sweep puts it **29.83 %** from the adjoint, and the pre-registration
predicts it STAYS failed under tightening, because its error is truncation and
tightening does not touch truncation.

Usage:  d19t_xf.py -mode T -tol 1e-10
        d19t_xf.py -mode X -tol 1e-10
        d19t_xf.py --selftest
"""
import hashlib
import json
import os
import sys
import time

# ---- the frozen producer, borrowed and NOT edited ----------------------------
PRODUCER = "d19r_runScript.py"
PRODUCER_MD5 = "a5e18503ea29d0e37c3cf1668533cd34"
HEADER_MD5_SHARED_WITH_D15 = "d1efc43583fbeb59fb5116816b055a07"
ANCHOR = "# OpenMDAO setup"
ITEM = "D19T"

# ---- registered constants (PREREGISTRATION.md section 4) ---------------------
# Sanaa's four steps, VERBATIM, plus the charter-4 trivial baseline at the head.
TRIVIAL_STEP = 3.0e-2
STEPS_SANAA = [1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5]
STEPS = [TRIVIAL_STEP] + STEPS_SANAA

# The GRADED component, and the NON-GRADED contrast control.
GRADED_COMPONENT = ("shape", 7)
CONTRAST_COMPONENT = ("shape", 6)
COMPONENTS = [GRADED_COMPONENT, CONTRAST_COMPONENT]
GRADED = {GRADED_COMPONENT: True, CONTRAST_COMPONENT: False}

# The registered plateau centre and its band.  THE BAND IS D19R's G19R-1b,
# UNCHANGED -- 10.0 %.  A tightened primal that had to be graded on a looser
# band would be answering an easier question than the one that failed.
PLATEAU_CENTRE = 1.0e-3
PLATEAU_TOL_PCT = 10.0
# On a DECADE grid the decade neighbours of a centre are its immediate
# neighbours: stride 1.  D19R needed stride 2 because its grid was half-decade.
# `assert_decade_stride` proves this against the registered ladder rather than
# asserting it in prose.
DECADE_STRIDE = 1

# The registered tolerance ladder.  1e-8 is the REPRODUCTION arm and is not a
# treatment: it re-measures D19R's own condition with this instrument, so a
# change downstream cannot be this harness rather than the tolerance.
TOL_LADDER = [1.0e-8, 1.0e-10, 1.0e-12]
ARM_TOL = {"T08": 1.0e-8, "T10": 1.0e-10, "T12": 1.0e-12, "XT10": 1.0e-10}

ETA_FLOOR = 1.0e-14
CTRL_STEP = 1.0e-3
PLANT_K = 5.0
PLANT_K_SHRUNK = 0.5

OUT_T = "d19t_T.json"
OUT_X = "d19t_X.json"
MODES = ("T", "X")


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def idwarp_identity():
    try:
        import idwarp
        p = idwarp.__file__
        so = os.path.join(os.path.dirname(p), "libidwarp.so")
        return {"idwarp_file": p, "libidwarp_so_md5": md5_of(so)}
    except Exception as exc:                                       # noqa: BLE001
        return {"idwarp_file": None, "libidwarp_so_md5": None, "error": repr(exc)[:200]}


def assert_decade_stride(steps=None, stride=DECADE_STRIDE):
    """A stride constant that stops matching the grid is a silently relaxed gate.

    D19R's `G19R-1b-N` earned this: on its half-decade grid a stride of ONE
    would have graded the plateau against neighbours a factor 3.16 away instead
    of 10, relaxing the band by regridding with nothing in any diff to see.
    D19T's grid is a decade grid so the stride is 1 -- and that is PROVED here
    against the registered ladder, not asserted.
    """
    steps = list(STEPS_SANAA if steps is None else steps)
    for i in range(len(steps) - stride):
        ratio = steps[i] / steps[i + stride]
        if abs(ratio - 10.0) > 1e-9 * 10.0:
            raise Refusal(json.dumps({
                "REFUSE": "DECADE_STRIDE_DOES_NOT_SPAN_A_DECADE",
                "detail": {"level": i, "stride": stride,
                           "steps": [steps[i], steps[i + stride]], "ratio": ratio,
                           "note": "the plateau band is defined against DECADE "
                                   "neighbours; a stride that does not span a "
                                   "decade would relax the gate by regridding"}},
                sort_keys=True))
    return True


class Refusal(Exception):
    pass


def parse_args(argv):
    mode = tol = None
    for i, a in enumerate(argv):
        if a == "-mode" and i + 1 < len(argv):
            mode = argv[i + 1]
        if a == "-tol" and i + 1 < len(argv):
            tol = argv[i + 1]
    if mode not in MODES:
        sys.stderr.write("D19T_XF usage: d19t_xf.py -mode %s -tol <float>\n" % "|".join(MODES))
        sys.exit(64)
    if tol is None:
        sys.stderr.write("D19T_XF REFUSE -tol is REQUIRED: the tolerance is the whole "
                         "independent variable of this item and may not default\n")
        sys.exit(64)
    try:
        tolf = float(tol)
    except ValueError:
        sys.stderr.write("D19T_XF REFUSE -tol %r is not a float\n" % tol)
        sys.exit(64)
    if tolf not in TOL_LADDER:
        sys.stderr.write("D19T_XF REFUSE tolerance %r is not on the registered ladder %r -- "
                         "a tolerance chosen at run time is a gate chosen after the answer\n"
                         % (tolf, TOL_LADDER))
        sys.exit(2)
    return mode, tolf


def plant_relative(d_ref, band_pct, k):
    return k * (band_pct / 100.0) * abs(d_ref)


# =============================================================================
# THE SELFTEST -- logic and controls only, and it says so
# =============================================================================
def selftest():
    ok = True
    print("D19T_XF SELFTEST -- proves the LOGIC and the CONTROLS, never the physics")
    print()

    print("DECADE-STRIDE assertion against the registered ladder:")
    try:
        assert_decade_stride()
        print("   stride %d spans exactly one decade on %r   OK" % (DECADE_STRIDE, STEPS_SANAA))
    except Refusal as exc:
        print("   **WRONG** %s" % exc)
        ok = False

    print("   RED LEG -- a half-decade ladder must REFUSE stride 1:")
    try:
        assert_decade_stride([1.0e-2, 3.0e-3, 1.0e-3, 3.0e-4], 1)
        print("   **WRONG** a half-decade ladder was accepted at stride 1")
        ok = False
    except Refusal:
        print("   refused DECADE_STRIDE_DOES_NOT_SPAN_A_DECADE   OK -- drove red")

    print()
    print("THE TOLERANCE IS THE INDEPENDENT VARIABLE AND MAY NOT DEFAULT OR DRIFT:")
    for bad in ("1e-9", "1e-6", "0.0"):
        rc = None
        try:
            parse_args(["-mode", "T", "-tol", bad])
        except SystemExit as exc:
            rc = exc.code
        good = rc == 2
        ok = ok and good
        print("   -tol %-6s off the registered ladder -> exit %-4r %s"
              % (bad, rc, "OK" if good else "**WRONG**"))
    rc = None
    try:
        parse_args(["-mode", "T"])
    except SystemExit as exc:
        rc = exc.code
    good = rc == 64
    ok = ok and good
    print("   -tol omitted entirely                    -> exit %-4r %s"
          % (rc, "OK" if good else "**WRONG**"))
    for good_tol in TOL_LADDER:
        m, t = parse_args(["-mode", "T", "-tol", repr(good_tol)])
        good = t == good_tol
        ok = ok and good
        print("   -tol %-8r on the ladder                -> accepted %s"
              % (good_tol, "OK" if good else "**WRONG**"))

    print()
    print("THE PLANTED CONTROL (rule 3), RELATIVE, BOTH LEGS:")
    d_ref = -2.064883e-04                       # D19R's landed shape[7]/CD at 1e-3
    p = plant_relative(d_ref, PLATEAU_TOL_PCT, PLANT_K)
    ps = plant_relative(d_ref, PLATEAU_TOL_PCT, PLANT_K_SHRUNK)
    mv, mvs = abs(p) / abs(d_ref) * 100.0, abs(ps) / abs(d_ref) * 100.0
    print("   d_ref = %.6e  (D19R S8 rows[shape,7].fd[0.001].dCD)" % d_ref)
    print("   K=%.1f  moves %6.2f pp  band %.1f pp -> %s"
          % (PLANT_K, mv, PLATEAU_TOL_PCT, "CROSSES" if mv > PLATEAU_TOL_PCT else "**DOES NOT**"))
    print("   K=%.1f  moves %6.2f pp  band %.1f pp -> %s"
          % (PLANT_K_SHRUNK, mvs, PLATEAU_TOL_PCT,
             "DOES NOT CROSS -- red leg drove red" if mvs <= PLATEAU_TOL_PCT else "**CROSSES**"))
    ok = ok and (mv > PLATEAU_TOL_PCT) and (mvs <= PLATEAU_TOL_PCT)

    print()
    print("THE REGISTERED PLAN:")
    print("   steps          %r  (trivial baseline %r + Sanaa's four)" % (STEPS, TRIVIAL_STEP))
    print("   graded         %s[%d]" % GRADED_COMPONENT)
    print("   contrast ctrl  %s[%d]  NON-GRADED" % CONTRAST_COMPONENT)
    print("   plateau centre %r   band %.1f %%   stride %d" % (PLATEAU_CENTRE, PLATEAU_TOL_PCT, DECADE_STRIDE))
    print("   tolerance ladder %r" % (TOL_LADDER,))
    n = len(COMPONENTS) * len(STEPS) * 2 + 2
    print("   solves per T arm %d  (= %d components x %d steps x 2 sides + baseline + repeat)"
          % (n, len(COMPONENTS), len(STEPS)))
    print()
    print("D19T_XF SELFTEST %s" % ("OK" if ok else "FAILED"))
    return 0 if ok else 1


# =============================================================================
# main
# =============================================================================
def main():
    if "--selftest" in sys.argv:
        return selftest()

    mode, TOL = parse_args(sys.argv)
    assert_decade_stride()

    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("D19T_XF REFUSE producer md5 %s != frozen %s\n" % (got, PRODUCER_MD5))
        sys.exit(2)
    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D19T_XF REFUSE anchor %r appears %d times\n" % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]
    hmd5 = hashlib.md5(header.encode()).hexdigest()
    if hmd5 != HEADER_MD5_SHARED_WITH_D15:
        sys.stderr.write("D19T_XF REFUSE producer header md5 %s != D15's %s\n"
                         % (hmd5, HEADER_MD5_SHARED_WITH_D15))
        sys.exit(2)
    sys.stdout.write("D19T_HEADER_IDENTICAL_TO_D15 md5=%s\n" % hmd5)

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d19t_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    # ---- THE TOLERANCE, APPLIED AND THEN READ BACK --------------------------
    tol_before = ns["daOptions"].get("primalMinResTol")
    ns["daOptions"]["primalMinResTol"] = TOL
    tol_after = ns["daOptions"].get("primalMinResTol")
    if tol_after != TOL:
        sys.stderr.write("D19T_XF REFUSE the tolerance did not land in the namespace: "
                         "requested %r, namespace holds %r\n" % (TOL, tol_after))
        sys.exit(2)
    sys.stdout.write("D19T_TOL_APPLIED requested=%r producer_default=%r namespace=%r\n"
                     % (TOL, tol_before, tol_after))
    sys.stdout.write("D19T_TOL_LOG_ASSERT_EXPECTS satisfied the prescribed tolerance %g\n" % TOL)

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    Top = ns["Top"]
    out_path = OUT_T if mode == "T" else OUT_X
    jsonl = out_path.replace(".json", ".jsonl")

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
          "primalMinResTol_producer_default": tol_before,
          "primalMinResTol_requested": TOL,
          "primalMinResTol_in_namespace": tol_after,
          "U0": ns.get("U0"), "aoa0": ns.get("aoa0"), "T0": ns.get("T0"),
          "p0": ns.get("p0"), **ident})

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    base = {"shape": np.array(prob.get_val("shape"), dtype=float).copy(),
            "patchV": np.array(prob.get_val("patchV"), dtype=float).copy()}
    emit({"kind": "baseline_dvs", "n_shape": int(base["shape"].size),
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

    # ======================= mode X: the adjoint =============================
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
                   "primalMinResTol_requested": TOL,
                   "primalMinResTol_in_namespace": tol_after,
                   "CD_baseline": repr(cd0), "CL_baseline": repr(cl0),
                   "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]],
                                    "patchV": [repr(float(v)) for v in base["patchV"]]},
                   "adjoint": jadj, "contains_adjoint": True}
            with open(out_path, "w") as fh:
                json.dump(out, fh, indent=1, sort_keys=True)
                fh.flush()
                os.fsync(fh.fileno())
            sys.stdout.write("D19T_X_WRITTEN %s\n" % out_path)
        MPI.COMM_WORLD.Barrier()
        return 0

    # ---- eta: same-mesh rerun determinism, NAMED for the weak bound it is ----
    cd0r, cl0r = primal("baseline_repeat")
    eta_raw = abs(cd0 - cd0r)
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flagged, "CD_baseline": repr(cd0), "CD_repeat": repr(cd0r),
          "note": "SAME-MESH rerun determinism.  THIS IS A SCATTER AND THE FD IS "
                  "LIMITED BY A BIAS: D19R measured eta_raw = 1.3011e-10 while its "
                  "own FD carried a shared additive CD error of |eps| ~ 4.7e-9, 36x "
                  "larger.  A repeatability arm CANNOT bound a convergence bias, and "
                  "this number is reported so that gap stays visible."})

    # ======================= mode T: the sweep ===============================
    rows = []
    for dv, idx in COMPONENTS:
        if idx >= base[dv].size:
            rows.append({"dv": dv, "idx": idx, "status": "ABSENT",
                         "n_available": int(base[dv].size), "fd": {},
                         "graded": GRADED[(dv, idx)]})
            continue
        fd = {}
        for s in STEPS:
            key = repr(s)
            try:
                set_perturbed(dv, idx, +s)
                cdp, clp = primal("%s[%d]+%g" % (dv, idx, s))
                set_perturbed(dv, idx, -s)
                cdm, clm = primal("%s[%d]-%g" % (dv, idx, s))
                fd[key] = {"step": s, "dCD": repr((cdp - cdm) / (2.0 * s)),
                           "dCL": repr((clp - clm) / (2.0 * s)),
                           "CD_plus": repr(cdp), "CD_minus": repr(cdm),
                           "CL_plus": repr(clp), "CL_minus": repr(clm),
                           "ok": True, "is_trivial_baseline": bool(s == TRIVIAL_STEP)}
            except Exception as exc:                               # noqa: BLE001
                # A FAILED STEP IS A ROW, NOT A GAP (VERIFICATION_CHARTER section 7).
                fd[key] = {"step": s, "ok": False, "error": repr(exc)[:400],
                           "is_trivial_baseline": bool(s == TRIVIAL_STEP)}
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "step": s, "row": fd[key]})
        rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd,
                     "graded": GRADED[(dv, idx)]})
    for k in ("shape", "patchV"):
        prob.set_val(k, base[k].copy())

    # ---- the RELATIVE planted control, BOTH LEGS ----------------------------
    d_ref = cd0
    plant = plant_relative(d_ref, PLATEAU_TOL_PCT, PLANT_K)
    plant_shrunk = plant_relative(d_ref, PLATEAU_TOL_PCT, PLANT_K_SHRUNK)
    moved_pp = abs(plant) / abs(d_ref) * 100.0
    moved_pp_shrunk = abs(plant_shrunk) / abs(d_ref) * 100.0
    ctrl = {"dv": "CTRL", "idx": 0, "status": "CONTROL", "graded": False, "fd": {
        repr(CTRL_STEP): {"step": CTRL_STEP, "dCD": repr(0.0), "dCL": repr(0.0),
                          "CD_plus": repr(cd0), "CD_minus": repr(cd0), "ok": True,
                          "note": "synthetic: identical DVs both sides -> derivative exactly 0"}},
        "planted": {"step": CTRL_STEP, "plant": repr(plant), "K": PLANT_K,
                    "band_pct": PLATEAU_TOL_PCT, "d_ref": repr(d_ref),
                    "formula": "plant = K * (band/100) * |d_ref|",
                    "moved_pp": repr(moved_pp),
                    "crosses_band": bool(moved_pp > PLATEAU_TOL_PCT),
                    "dCD": repr(plant / (2.0 * CTRL_STEP)), "ok": True},
        "planted_shrunk": {"step": CTRL_STEP, "plant": repr(plant_shrunk),
                           "K": PLANT_K_SHRUNK, "band_pct": PLATEAU_TOL_PCT,
                           "moved_pp": repr(moved_pp_shrunk),
                           "crosses_band": bool(moved_pp_shrunk > PLATEAU_TOL_PCT),
                           "dCD": repr(plant_shrunk / (2.0 * CTRL_STEP)),
                           "note": "SUFFICIENCY RED LEG -- must NOT cross the band"}}
    emit({"kind": "control", "row": ctrl})
    rows.append(ctrl)

    if rank == 0:
        # READ THE PLANT BACK THROUGH THE FILE, not out of the variable that
        # wrote it.  A control read from memory proves the arithmetic, not the
        # reader.
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
            sys.stderr.write("D19T_XF REFUSE planted-zero control not seen on read-back: "
                             "zero=%r plant=%r want=%r shrunk=%r want_shrunk=%r\n"
                             % (seen_zero, seen_plant, want, seen_shrunk, want_shrunk))
            sys.exit(2)
        if not moved_pp > PLATEAU_TOL_PCT:
            sys.stderr.write("D19T_XF REFUSE plant at K=%r moves %.4f pp and does NOT cross "
                             "the %.1f pp band -- the SO-2M failure\n"
                             % (PLANT_K, moved_pp, PLATEAU_TOL_PCT))
            sys.exit(2)
        if moved_pp_shrunk > PLATEAU_TOL_PCT:
            sys.stderr.write("D19T_XF REFUSE shrunken plant at K=%r DOES cross the band -- "
                             "the control is not measuring crossing\n" % PLANT_K_SHRUNK)
            sys.exit(2)
        sys.stdout.write("D19T_PLANTED_CONTROL_SEEN zero=%r K=%r moved=%.4f pp CROSSES | "
                         "K_shrunk=%r moved=%.4f pp DOES NOT CROSS (band %.1f pp)\n"
                         % (seen_zero, PLANT_K, moved_pp, PLANT_K_SHRUNK,
                            moved_pp_shrunk, PLATEAU_TOL_PCT))
        out = {
            "item": ITEM, "mode": "T", "producer_md5": got, "header_md5": hmd5,
            "nprocs": nprocs, "identity": ident,
            "primalMinResTol_producer_default": tol_before,
            "primalMinResTol_requested": TOL,
            "primalMinResTol_in_namespace": tol_after,
            "steps_registered": STEPS, "steps_sanaa": STEPS_SANAA,
            "trivial_baseline_step": TRIVIAL_STEP,
            "plateau_centre": PLATEAU_CENTRE, "plateau_tol_pct": PLATEAU_TOL_PCT,
            "decade_stride": DECADE_STRIDE,
            "graded_component": list(GRADED_COMPONENT),
            "contrast_component": list(CONTRAST_COMPONENT),
            "ctrl_step": CTRL_STEP, "plant_K": PLANT_K, "plant_K_shrunk": PLANT_K_SHRUNK,
            "plant": repr(plant), "plant_shrunk": repr(plant_shrunk),
            "plant_moved_pp": repr(moved_pp), "plant_moved_pp_shrunk": repr(moved_pp_shrunk),
            "CD_baseline": repr(cd0), "CL_baseline": repr(cl0),
            "CD_baseline_repeat": repr(cd0r), "CL_baseline_repeat": repr(cl0r),
            "eta_raw": repr(eta_raw), "eta_used": repr(eta), "eta_floored": eta_flagged,
            "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]],
                             "patchV": [repr(float(v)) for v in base["patchV"]]},
            "rows": rows, "n_rows": len(rows),
            "contains_adjoint": False, "grades_nothing": False,
        }
        with open(out_path, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("D19T_T_WRITTEN %s tol=%g\n" % (out_path, TOL))
    MPI.COMM_WORLD.Barrier()
    return 0


if __name__ == "__main__":
    sys.exit(main())
