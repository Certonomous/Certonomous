#!/usr/bin/env python3
# ===========================================================================
# d6r2c_gs1_fd.py -- PRODUCER for the D6R2C GRADIENT SPOT-CHECK (arm GS1)
# ===========================================================================
#
# Registered by PREREGISTRATION_GRADIENT_SPOTCHECK.md sections 2, 3 and 11, and
# IN THE SAME COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS (rule 2).
#
# WHAT IT DOES.  A central-difference sweep over THREE design variables at FOUR
# steps each, at the O_mp optimum, against the adjoint gradient read from the
# driver's own history -- plus SIX unperturbed evaluations spread through the arm
# that measure the procedure's own scatter.
#
# THE CONTAMINATION THIS DESIGN DOES NOT REMOVE, NAMED FIRST BECAUSE A LATER
# READER WILL OTHERWISE ASSUME NOBODY NOTICED IT.  The two members of each
# central-difference pair DO NOT start from the same field.  DAFoam reads
# processorN/0/ ONCE, at prob.setup(); every run_model() after that begins where
# the previous one finished (PREREGISTRATION_AFTER_ITEMS.md section 4a, measured).
# THAT WAS KNOWN BEFORE THIS ARM WAS REGISTERED AND WAS DELIBERATELY NOT REMOVED.
# The alternative -- restarting the container per evaluation and re-transferring
# the fields -- was costed at ~216 core-min against ~100 and REJECTED ON EVIDENCE
# ORDER, not on price: its whole benefit rests on an inference about where the
# noise floor sits, and this arm MEASURES that floor instead of assuming it.
# The six unperturbed evaluations are that measurement, taken under exactly the
# sequential warm-starting every FD pair experiences.
#
# THE ARM IS WARM-STARTED ONCE, by d6r2c_fm6_init.py's cell-for-cell index
# transfer -- REUSED UNCHANGED and pinned.  That is the one thing measured on
# 2026-09-13 to make this configuration converge at the optimum (arm FM8), and
# ~60 % of O_mp's primal evaluations failed at large |shape| without it.
#
# THIS FILE PRODUCES NUMBERS.  IT GRADES NOTHING.  Every threshold lives in
# d6r2c_gs1_grade.py, which recomputes each FD estimate from the two J values
# rather than trusting the one recorded here.
#
# HONEST GAP (section 11a): this file has never been executed against the solver.
# What is driven at the freeze is --selftest, on the pure logic: the DV plan, the
# perturbation arithmetic, the record writer and every refusal path.
# ===========================================================================
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time

RUNSCRIPT_MD5 = "2f2ae43a627146cf8e0f065b035ada4b"   # the bytes O_mp ran
EVALS_MD5 = "2c0b8143caad198cd2e21d8047986aa3"       # the inherited O_mp record
OPTVIEW_MD5 = "2a96b47a19e84e40a95c30e1634ce356"     # the driver history
FINAL_RECORD_N = 88
ANCHOR = '\nif args.task == "run_driver":\n'

# ---- THE ADJOINT AT THE OPTIMUM (registration section 1b).
# THE RECORD IS NAMED, AND SO IS THE METHOD THAT FOUND IT.  OptView.hst holds 52
# funcsSens records.  The one at the optimum was found by comparing each record's
# `xuser` shape vector against n = 88's from the md5-pinned evals file and taking
# the exact match: key = 172, iter = 86, isMajor = True, max|d shape| = 0.000e+00.
# THE LAST funcsSens RECORD IS key = 173 AND IS **NOT** THE ONE AT THE FINAL
# DESIGN POINT.  Taking the last record would have been the obvious move and it
# would have been wrong -- the same shape as reading an index as a count.
ADJ_RECORD_KEY = 172
ADJ_RECORD_ITER = 86
# driver-scaled, dJ/d(dv), from that record
ADJOINT = {
    "shape[84]": -0.0012395965734695029,
    "twist[2]": 0.0063348068779340615,
    "patchV_cl05[1]": 0.01719085469787987,
}
# "shape[83] = -0.0012394586288117077 is within 0.011 % of shape[84]" (sec 1c).
# THE TWO ARE A NEAR-DEGENERATE PAIR AND 84 IS 'THE MAXIMUM' BY A MARGIN THIS
# EXPERIMENT CANNOT RESOLVE.  The FD checks the adjoint's VALUE at 84, which is
# unaffected; the CHOICE is not a demonstrated ranking and is not reported as one.
ADJOINT_SHAPE83 = -0.0012394586288117077

# "the DVs are perturbed in the DRIVER-SCALED space, because that is the space the
#  adjoint is reported in" (sec 2a).  The parent burned two arms on
#  scaled-versus-physical (PREREGISTRATION.md ADDENDUM 1, ADDENDUM 2).
DVS = [("shape", 84), ("twist", 2), ("patchV_cl05", 1)]
# "the ladder extends UP, because for shape that is where the signal is" (sec 2b)
LADDER = [1.0e-1, 1.0e-2, 1.0e-3, 1.0e-4]
# "six unperturbed evaluations: two before the ladder, one after each DV block,
#  one at the end" (sec 2c).  REPORTED, NEVER GATED.
N_UNPERTURBED = 6
RECORD = "d6r2c_gs1.jsonl"
# "d6r2c_gs1_grade.py plants PLANT = 1.234e-03" (sec 7)
PLANT = 1.234e-03


class Refusal(Exception):
    """Refuse, never degrade."""


def _md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# THE PLAN -- a pure function, so the whole ordering is testable without a solver
# ---------------------------------------------------------------------------

def sweep_plan(dvs=None, ladder=None):
    """The evaluation sequence, in order.

    Each entry is a dict: kind 'U' (unperturbed) or 'FD', with its dv, step and
    sign.  THE ORDER IS PART OF THE REGISTRATION, not an implementation detail:
    the two unperturbed evaluations come FIRST so a reader has the scatter in
    hand before the ladder's numbers, and one more follows each DV block so a
    CONSTANT scatter can be told from one that GROWS through the arm.  Those have
    completely different implications for whether the later DVs can be believed."""
    dvs = DVS if dvs is None else dvs
    ladder = LADDER if ladder is None else ladder
    plan = [{"kind": "U", "tag": "U0"}, {"kind": "U", "tag": "U1"}]
    for i, (name, idx) in enumerate(dvs):
        for h in ladder:
            for sign in (+1, -1):
                plan.append({"kind": "FD", "dv": name, "index": idx,
                             "step": h, "sign": sign,
                             "tag": "%s[%d]%+g" % (name, idx, sign * h)})
        plan.append({"kind": "U", "tag": "U_after_%s[%d]" % (name, idx)})
    plan.append({"kind": "U", "tag": "U_final"})
    return plan


def perturb(base_vector, index, step, sign):
    """The perturbed design vector.  ONE component moves; everything else is the
    optimum, byte for byte.  Returns a NEW list -- the caller's vector is never
    mutated, because a sweep that mutates its own base accumulates its steps."""
    if not (0 <= index < len(base_vector)):
        raise Refusal("REFUSE_DV_INDEX %d outside [0, %d)" % (index, len(base_vector)))
    out = list(base_vector)
    out[index] = out[index] + sign * step
    return out


def fd_estimate(j_plus, j_minus, step):
    """Central difference.  (J(+h) - J(-h)) / (2h), in the driver-scaled space
    the perturbation was applied in and the adjoint is reported in."""
    if step <= 0:
        raise Refusal("REFUSE_STEP %r is not positive" % (step,))
    for v, nm in ((j_plus, "J(+h)"), (j_minus, "J(-h)")):
        if v is None or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise Refusal("REFUSE_NON_FINITE %s = %r -- A STALLED OR MISSING "
                          "EVALUATION IS A MISSING MEASUREMENT, NOT A GRADIENT "
                          "DISAGREEMENT.  It is never averaged in and never "
                          "interpolated over (sec 3a)." % (nm, v))
    return (j_plus - j_minus) / (2.0 * step)


def append_record(path, obj):
    with open(path, "a") as fh:
        fh.write(json.dumps(obj, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


# ---------------------------------------------------------------------------
# THE FROZEN MODEL, LOADED FROM ITS OWN BYTES  (the parent's load_frozen_model)
# ---------------------------------------------------------------------------

def load_frozen_model(runscript_path, max_iter="25"):
    src = open(runscript_path).read()
    got = hashlib.md5(src.encode()).hexdigest()
    if got != RUNSCRIPT_MD5:
        raise Refusal("REFUSE_RUNSCRIPT_MD5 got %s want %s -- the model this file "
                      "would build is not the model that ran" % (got, RUNSCRIPT_MD5))
    n = src.count(ANCHOR)
    if n != 1:
        raise Refusal("REFUSE_ANCHOR the task-dispatch anchor appears %d times, "
                      "not once" % n)
    ns = {"__name__": "d6r2c_frozen_model", "__file__": runscript_path}
    saved = sys.argv
    sys.argv = [runscript_path, "-task", "run_model", "-max_iter", str(max_iter)]
    try:
        exec(compile(src.split(ANCHOR)[0], runscript_path, "exec"), ns)
    finally:
        sys.argv = saved
    for need in ("prob", "POINTS", "CL_TARGETS", "WEIGHTS"):
        if need not in ns:
            raise Refusal("REFUSE_MODEL_INCOMPLETE frozen prefix did not define %r" % need)
    return ns


def read_final_dv(evals_path):
    got = _md5_file(evals_path)
    if got != EVALS_MD5:
        raise Refusal("REFUSE_EVALS_MD5 got %s want %s" % (got, EVALS_MD5))
    recs = [json.loads(l) for l in open(evals_path) if l.strip()]
    F = [r for r in recs if r.get("kind") == "F" and r.get("n") == FINAL_RECORD_N]
    if len(F) != 1:
        raise Refusal("REFUSE_FINAL_RECORD %d records with n = %d, expected 1"
                      % (len(F), FINAL_RECORD_N))
    r = F[0]
    if r.get("fail", 1) != 0:
        raise Refusal("REFUSE_FAILED_RECORD n = %d carries fail = %r -- a failed "
                      "evaluation is not a design point" % (FINAL_RECORD_N, r.get("fail")))
    dv = {k.split(".")[-1]: list(v) for k, v in r["dv"].items()}
    return dv, got


def dv_divisor(meta_entry):
    """The driver's own divisor, from OpenMDAO metadata, NEVER re-typed.
    ADDENDUM 2 of PREREGISTRATION_AFTER_ITEMS.md: total_scaler is None in this
    model and a fallback to scaler is required, and a guard that cannot MEASURE
    the divisor REFUSES rather than assuming 1.0."""
    for key in ("total_scaler", "scaler"):
        v = meta_entry.get(key)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                import numpy as np
                a = np.asarray(v).ravel()
                if a.size and len(set(a.tolist())) == 1:
                    return float(a[0])
                raise Refusal("REFUSE_DIVISOR_NONUNIFORM %r" % (v,))
    raise Refusal("REFUSE_DIVISOR_ABSENT neither total_scaler nor scaler is set; "
                  "this file does not assume 1.0")


# ---------------------------------------------------------------------------
# THE PHASES
# ---------------------------------------------------------------------------

def phase_stage(arm_dir, runscript):
    """Build the model so DAFoam creates mp0X and its decomposition, then STOP.

    NO PRIMAL IS SOLVED HERE.  The decomposition must exist before
    d6r2c_fm6_init.py can write processorN/0/, and the transfer must land before
    the sweep's prob.setup() reads it -- FM7 died because the write happened
    after the decomposition the solver actually read (ADDENDUM 3)."""
    if os.geteuid() == 0:
        raise Refusal("REFUSE_ROOT this arm runs as ubuntu, never root")
    load_frozen_model(runscript)
    made = [d for d in ("mp04", "mp05", "mp06")
            if os.path.isdir(os.path.join(arm_dir, d, "processor0"))]
    print("D6R2C_GS1_STAGE processor dirs present for: %r" % (made,))
    if len(made) != 3:
        raise Refusal(
            "REFUSE_NO_DECOMPOSITION prob.setup() did not leave a decomposition "
            "for all three conditions (got %r).  The transfer has nowhere to "
            "land; this is a PRODUCER DEFECT under section 11a -- stopped, "
            "NOT A RESULT, repaired under VERIFICATION_CHARTER 2d.1." % (made,))
    return 0


def phase_sweep(arm_dir, runscript, evals, out_path):
    from mpi4py import MPI
    rank0 = MPI.COMM_WORLD.rank == 0
    if os.geteuid() == 0:
        raise Refusal("REFUSE_ROOT this arm runs as ubuntu, never root")
    t_start = time.time()
    dv_star, evals_md5 = read_final_dv(evals)
    ns = load_frozen_model(runscript)
    prob, POINTS, W = ns["prob"], ns["POINTS"], ns["WEIGHTS"]
    meta = prob.model.get_design_vars(recurse=True, get_sizes=True, use_prom_ivc=True)
    scalers = {k.split(".")[-1]: dv_divisor(v) for k, v in meta.items()}

    def set_scaled(name, scaled_vals):
        s = scalers[name]
        prob.set_val(name, [v / s for v in scaled_vals])

    if rank0:
        append_record(out_path, {
            "kind": "HEADER",
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "uid": os.getuid(), "gid": os.getgid(),
            "ranks": MPI.COMM_WORLD.size, "points": POINTS, "weights": W,
            "evals_md5": evals_md5, "runscript_md5": RUNSCRIPT_MD5,
            "optview_md5_registered": OPTVIEW_MD5,
            "adjoint": dict(ADJOINT), "adjoint_record_key": ADJ_RECORD_KEY,
            "adjoint_record_iter": ADJ_RECORD_ITER,
            "adjoint_shape83_near_degenerate": ADJOINT_SHAPE83,
            "dvs": [[n, i] for n, i in DVS], "ladder": list(LADDER),
            "n_unperturbed": N_UNPERTURBED,
            "space": "driver-scaled -- the space the adjoint is reported in",
            "scalers": scalers,
            "sequential_warm_start_disclosed":
                "The two members of each central-difference pair do NOT start "
                "from the same field; DAFoam reads processorN/0/ once at setup. "
                "KNOWN IN ADVANCE, deliberately not removed, and MEASURED by the "
                "six unperturbed evaluations instead (sec 2c).",
            "DEADLINE_IN_CONTAINER_S": "NONE"})

    plan = sweep_plan()
    n_u = sum(1 for p in plan if p["kind"] == "U")
    if n_u != N_UNPERTURBED:
        raise Refusal("REFUSE_PLAN the plan carries %d unperturbed evaluations, "
                      "the registration fixes %d" % (n_u, N_UNPERTURBED))
    rc = 0
    for step_i, item in enumerate(plan):
        t0 = time.time()
        # EVERY evaluation is set from the OPTIMUM, never from the previous
        # vector -- a sweep that mutates its own base accumulates its steps.
        for name, vals in dv_star.items():
            set_scaled(name, vals)
        if item["kind"] == "FD":
            base = dv_star[item["dv"]]
            set_scaled(item["dv"],
                       perturb(base, item["index"], item["step"], item["sign"]))
        prob.run_model()
        cd = {p: float(prob.get_val("%s.aero_post.CD" % p)[0]) for p in POINTS}
        cl = {p: float(prob.get_val("%s.aero_post.CL" % p)[0]) for p in POINTS}
        J = sum(W[p] * cd[p] for p in POINTS)
        if rank0:
            rec = {"kind": "EVAL", "i": step_i, "utc": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "wall_s": time.time() - t0, "fail": 0,
                "CD": cd, "CL": cl, "J": J}
            rec.update(item)
            append_record(out_path, rec)
        MPI.COMM_WORLD.Barrier()

    if rank0:
        append_record(out_path, {
            "kind": "FOOTER", "rc": rc, "wall_s": time.time() - t_start,
            "n_evaluations": len(plan),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    return rc


# ---------------------------------------------------------------------------
# SELFTEST -- pure logic only.  No container, no run directory.
# ---------------------------------------------------------------------------

def selftest():
    ok = True
    n = 0

    def check(name, got, want):
        nonlocal ok, n
        n += 1
        if got != want:
            ok = False
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r" % (name, got, want))

    # ---- the plan: order is part of the registration -----------------------
    plan = sweep_plan()
    check("plan length = 3 DVs x 4 steps x 2 + 6 unperturbed", len(plan), 30)
    check("plan carries exactly N_UNPERTURBED unperturbed",
          sum(1 for p in plan if p["kind"] == "U"), N_UNPERTURBED)
    check("plan carries 24 FD evaluations",
          sum(1 for p in plan if p["kind"] == "FD"), 24)
    check("THE FIRST TWO EVALUATIONS ARE UNPERTURBED, so a reader has the scatter "
          "before the ladder", [plan[0]["kind"], plan[1]["kind"]], ["U", "U"])
    check("the LAST evaluation is unperturbed", plan[-1]["kind"], "U")
    # one unperturbed after each DV block -- the drift track
    idx = [i for i, p in enumerate(plan) if p["kind"] == "U"]
    check("the unperturbed evaluations are spread, not clustered",
          idx, [0, 1, 10, 19, 28, 29])
    for name, i in DVS:
        blk = [p for p in plan if p["kind"] == "FD" and p["dv"] == name]
        check("%s[%d] has 8 FD evaluations" % (name, i), len(blk), 8)
        check("%s[%d] covers every registered step" % (name, i),
              sorted(set(p["step"] for p in blk)), sorted(LADDER))
        check("%s[%d] is central: every step has + and -" % (name, i),
              sorted(p["sign"] for p in blk), [-1] * 4 + [1] * 4)

    # ---- perturbation arithmetic -------------------------------------------
    base = [1.0, 2.0, 3.0]
    check("perturb moves ONE component", perturb(base, 1, 0.5, +1), [1.0, 2.5, 3.0])
    check("perturb applies the sign", perturb(base, 1, 0.5, -1), [1.0, 1.5, 3.0])
    check("perturb does NOT mutate the caller's vector", base, [1.0, 2.0, 3.0])
    try:
        perturb(base, 3, 0.1, +1)
        check("perturb: index out of range -> refusal", "no refusal", "Refusal")
    except Refusal as e:
        check("perturb: index out of range -> REFUSE_DV_INDEX",
              str(e).startswith("REFUSE_DV_INDEX"), True)

    # ---- the central difference, and the stalled-evaluation refusal --------
    check("fd_estimate is the central difference",
          fd_estimate(1.5, 0.5, 0.25), 2.0)
    # A LINEAR FUNCTION, RECOVERED -- and its residue is the point.  The exact
    # slope is 3.0; on a base of 10.0 with h = 1e-3 the recovered value is
    # 3.0000000000001137, an error of 3.8e-14 that is PURE SUBTRACTIVE
    # CANCELLATION -- the two J values agree in their first 13 digits and the
    # difference keeps only what is left.  THAT IS THE EXACT EFFECT THE SMALL END
    # OF THE LADDER RUNS INTO, on a J of 0.023 where the real signal at h = 1e-4
    # is 2.5e-07.  The control asserts the property, not a float literal.
    lin = fd_estimate(10.0 + 3.0 * 1e-3, 10.0 - 3.0 * 1e-3, 1e-3)
    check("fd_estimate recovers a linear slope to better than 1e-12 relative",
          abs(lin - 3.0) / 3.0 < 1.0e-12, True)
    check("...and the residue is NONZERO, which is subtractive cancellation and "
          "is why the ladder has a small end at all", lin != 3.0, True)
    for bad in (None, float("nan"), float("inf")):
        try:
            fd_estimate(1.0, bad, 1e-3)
            check("fd_estimate: %r -> refusal" % bad, "no refusal", "Refusal")
        except Refusal as e:
            check("fd_estimate: a stalled evaluation (%r) -> REFUSE_NON_FINITE" % bad,
                  str(e).startswith("REFUSE_NON_FINITE"), True)
            check("...and the refusal says it is a MISSING MEASUREMENT",
                  "MISSING MEASUREMENT" in str(e), True)
    try:
        fd_estimate(1.0, 0.0, 0.0)
        check("fd_estimate: zero step -> refusal", "no refusal", "Refusal")
    except Refusal as e:
        check("fd_estimate: zero step -> REFUSE_STEP",
              str(e).startswith("REFUSE_STEP"), True)

    # ---- the divisor guard (ADDENDUM 2's defect, carried) -------------------
    check("divisor: total_scaler wins when set", dv_divisor({"total_scaler": 0.25}), 0.25)
    check("divisor: falls back to scaler when total_scaler is None",
          dv_divisor({"total_scaler": None, "scaler": 10.0}), 10.0)
    try:
        dv_divisor({"total_scaler": None})
        check("divisor: neither set -> refusal", "no refusal", "Refusal")
    except Refusal as e:
        check("divisor: neither set -> REFUSE_DIVISOR_ABSENT, never assume 1.0",
              str(e).startswith("REFUSE_DIVISOR_ABSENT"), True)

    # ---- EXTERNAL ANCHORS, typed as assertions and not as sources ----------
    check("EXTERNAL: the adjoint record is key 172", ADJ_RECORD_KEY, 172)
    check("EXTERNAL: at iter 86", ADJ_RECORD_ITER, 86)
    check("EXTERNAL: g_shape[84]", ADJOINT["shape[84]"], -0.0012395965734695029)
    check("EXTERNAL: g_twist[2]", ADJOINT["twist[2]"], 0.0063348068779340615)
    check("EXTERNAL: g_patchV_cl05[1]", ADJOINT["patchV_cl05[1]"], 0.01719085469787987)
    check("EXTERNAL: the near-degenerate shape[83]", ADJOINT_SHAPE83,
          -0.0012394586288117077)
    check("shape[83] and shape[84] differ by less than 0.02 %",
          abs(ADJOINT_SHAPE83 - ADJOINT["shape[84]"]) / abs(ADJOINT["shape[84]"])
          < 2.0e-4, True)
    check("EXTERNAL: the ladder extends UP to 1e-1", max(LADDER), 1.0e-1)
    check("EXTERNAL: and down to 1e-4", min(LADDER), 1.0e-4)

    print("D6R2C_GS1_FD SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", n))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="D6R2C gradient spot-check producer (arm GS1).")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--phase", choices=("stage", "sweep"), default="sweep")
    ap.add_argument("--arm-dir", default=os.getcwd())
    ap.add_argument("--runscript", default="d6r2c_opt_runScript.py")
    ap.add_argument("--evals", default="d6r2c_evals_final.jsonl")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    try:
        if a.phase == "stage":
            return phase_stage(a.arm_dir, a.runscript)
        return phase_sweep(a.arm_dir, a.runscript, a.evals,
                           os.path.join(a.arm_dir, RECORD))
    except Refusal as e:
        print("D6R2C_GS1_FD REFUSED\n%s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
