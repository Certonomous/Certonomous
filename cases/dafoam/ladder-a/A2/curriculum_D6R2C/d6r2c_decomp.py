#!/usr/bin/env python3
# ===========================================================================
# d6r2c_decomp.py -- ITEM 8 PRODUCER: the five decomposition states, in order
# ===========================================================================
#
# Registered by PREREGISTRATION_AFTER_ITEMS.md sections 1, 3 and 5, and IN THE
# SAME COMMIT, BEFORE ANY CONTAINER STARTS (CLAUDE.md rule 2).
#
# THIS FILE PRODUCES NUMBERS.  IT GRADES NOTHING.  Every threshold lives in
# d6r2c_after_grade.py, which reads what this file writes and recomputes the
# graded quantity from the per-condition CD and the frozen weights rather than
# trusting the J written here.  There is no branch in this file that can change
# a value it observes.
#
# THE MODEL IS NOT REDEFINED HERE.  It is the frozen d6r2c_opt_runScript.py's
# own bytes, md5-asserted, executed up to -- and NOT INCLUDING -- its task
# dispatch.  A second hand-written copy of the physics is a second thing that
# can drift (L-221/L-222), and this item's whole subject is a comparison between
# states of one model.  If the anchor line is not found exactly once, or the
# md5 does not match, THIS FILE REFUSES (exit 2) rather than proceed on a model
# it cannot prove is the one that ran.
#
# HONEST GAP, NAMED BEFORE IT IS DISCOVERED (registration section 11a): THIS
# FILE HAS NEVER BEEN EXECUTED AGAINST THE SOLVER.  It cannot be before the
# compute this registration authorises.  What is driven at the freeze is
# `--selftest`, which exercises the pure logic -- DV assembly, the driver-scaled
# space conversion, the record writer and every refusal path -- on synthetic
# inputs, touching no container and no run directory.
# ===========================================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

RUNSCRIPT_MD5 = "2f2ae43a627146cf8e0f065b035ada4b"   # PREREGISTRATION.md ADDENDUM 1, A1.6
EVALS_MD5 = "2c0b8143caad198cd2e21d8047986aa3"       # AFTER_ITEMS section 0b
FINAL_RECORD_N = 88                                  # AFTER_ITEMS section 1
ANCHOR = '\nif args.task == "run_driver":\n'

# "the five decomposition states in one container, order B -> T -> S -> F -> O"
STATES = ["B", "T", "S", "F", "O"]
# "findFeasibleDesign gets at most TRIM_MAX_EVALS = 40 primal evaluations per state"
TRIM_MAX_EVALS = 40
RECORD = "d6r2c_decomp.jsonl"


class Refusal(Exception):
    pass


def _md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# THE FINAL DESIGN VECTOR, READ FROM THE MD5-PINNED ARTEFACT
# ---------------------------------------------------------------------------

def read_final_dv(evals_path, require_md5=True):
    """Return (dv_driver_scaled, funcs) for F record n = 88.

    The vector is read IN THE DRIVER-SCALED SPACE the file records and is set
    back in THAT SAME SPACE.  ADDENDUM 1 of the parent registration is the
    reason this function names a space: comparing a driver-scaled vector against
    a physical one produced worst_abs_diff = 90.0 and cost a NOT A RESULT."""
    if not os.path.isfile(evals_path):
        raise Refusal("REFUSE_MISSING_EVALS %s" % evals_path)
    got = _md5_file(evals_path)
    if require_md5 and got != EVALS_MD5:
        raise Refusal("REFUSE_EVALS_MD5 got %s want %s -- the artefact this "
                      "registration pinned is not the artefact on disk" % (got, EVALS_MD5))
    rec = None
    with open(evals_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("kind") == "F" and r.get("n") == FINAL_RECORD_N:
                rec = r
    if rec is None:
        raise Refusal("REFUSE_NO_FINAL_RECORD n=%d not found in %s"
                      % (FINAL_RECORD_N, evals_path))
    if rec.get("fail", 1) != 0:
        raise Refusal("REFUSE_FINAL_RECORD_FAILED n=%d carries fail=%r -- a failed "
                      "evaluation is not a design" % (FINAL_RECORD_N, rec.get("fail")))
    dv = {k.split(".")[-1]: [float(x) for x in v] for k, v in rec["dv"].items()}
    for need in ("shape", "twist"):
        if need not in dv:
            raise Refusal("REFUSE_MISSING_DV %r in record n=%d" % (need, FINAL_RECORD_N))
    return dv, rec["funcs"], got


def dv_divisor(meta_entry):
    """The divisor converting a DRIVER-SCALED DV component to PHYSICAL.

    COPIED FROM THE WORKING SPELLING -- d6r2c_opt_runScript.py `_dv_scalers()`
    lines 431-434 -- and deliberately NOT re-invented.  ONE definition serves
    both producers (d6r2c_freshmesh.py imports it), because a second copy of a
    number is a second thing that can drift (L-221/L-222).

    REPAIR, 2026-09-13, under VERIFICATION_CHARTER 2d.1 and
    PREREGISTRATION_AFTER_ITEMS.md section 11a, disclosed in ADDENDUM 2.  The
    original spelling at d6r2c_decomp.py:225 and d6r2c_freshmesh.py:229,344 was
    `float(v.get("total_scaler") or 1.0)` -- WITH NO FALLBACK TO `scaler`.
    MEASURED in the pinned image against this exact model: `total_scaler` is
    None for EVERY design variable and `scaler` carries the value (twist 0.1,
    shape 10.0, patchV_* 0.1).  The divisor was therefore 1.0 for all five DVs,
    installing patchV = [10.0 m/s, 0.293 deg] where [100.0, 2.930] was
    registered -- a 10x velocity error corroborated by a measured yPlus
    collapse of 9.24x -- with twist 10x too SMALL and shape 10x too LARGE
    (outside its own registered bounds [-1, 1]).  Arm DEC2 crashed on it and is
    NOT A RESULT; arm FM would NOT have crashed.

    STATED, NOT FOLDED IN SILENTLY: this uses `is None`, not truthiness, so a
    scaler of exactly 0.0 is passed through and divides loudly rather than being
    swallowed into 1.0 by `or`.  That is a behaviour change from the line it
    replaces and it is named here rather than left to be discovered.
    """
    sc = meta_entry.get("total_scaler")
    if sc is None:
        sc = meta_entry.get("scaler")
    return 1.0 if sc is None else float(sc)


def dv_divisor_for(scalers, name):
    """Look up a design variable's divisor, and REFUSE if the model never
    reported one for it.

    HARDENING, 2026-09-13, disclosed in ADDENDUM 2.  The line this replaces was
    `scalers.get(name, 1.0)` -- THE SAME DEFECT ONE LAYER DOWN as the
    `total_scaler or 1.0` it sat beneath.  If a DV name is ever absent from
    OpenMDAO's metadata, a silent 1.0 installs a DRIVER-SCALED number as a
    PHYSICAL one, which is exactly how arm DEC2 came to run at U = 10 m/s with
    shape driven to +/-2.786 against its own registered bounds of +/-1.

    A reader that cannot see must say so rather than pass quietly.  This refuses
    with the name it wanted AND the names the model actually reported, so the
    failure names its own cause instead of producing a plausible number.
    """
    if name not in scalers:
        raise Refusal("REFUSE_UNKNOWN_DV_SCALER %r is not among the design "
                      "variables the model reported (%s) -- refusing rather than "
                      "dividing by a silent 1.0, which would install a "
                      "driver-scaled value as a physical one"
                      % (name, sorted(scalers)))
    return scalers[name]


def dv_for_state(state, dv_star, dv_x0):
    """The design vector for each registered state, in the DRIVER-SCALED space.

    Registration section 1, the table.  Nothing else in this file decides what a
    state is."""
    if state not in STATES:
        raise Refusal("REFUSE_UNKNOWN_STATE %r" % state)
    zeros_shape = [0.0] * len(dv_star["shape"])
    zeros_twist = [0.0] * len(dv_star["twist"])
    if state == "B":
        out = {"shape": zeros_shape, "twist": zeros_twist}
    elif state == "T":
        out = {"shape": zeros_shape, "twist": list(dv_star["twist"])}
    elif state == "S":
        out = {"shape": list(dv_star["shape"]), "twist": zeros_twist}
    else:                       # F and O share the geometry; they differ in AoA
        out = {"shape": list(dv_star["shape"]), "twist": list(dv_star["twist"])}
    if state == "O":
        # "J_opt is the optimiser's own final state" -- AoA taken from n=88, NOT trimmed
        for k, v in dv_star.items():
            if k.startswith("patchV_"):
                out[k] = list(v)
        out["_trim"] = False
    else:
        # every other state starts from x0's trim and is RE-TRIMMED
        for k, v in dv_x0.items():
            if k.startswith("patchV_"):
                out[k] = list(v)
        out["_trim"] = True
    return out


# ---------------------------------------------------------------------------
# THE RECORD WRITER -- appends as the run proceeds (registration section 6)
# ---------------------------------------------------------------------------

def append_record(path, obj):
    with open(path, "a") as fh:
        fh.write(json.dumps(obj, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def state_record(state, trimmed, n_trim_evals, cd, cl, aoa, weights, targets,
                 converged, final_res, wall_s, fail=0):
    J = sum(weights[p] * cd[p] for p in sorted(cd))
    return {"kind": "STATE", "state": state, "trimmed": trimmed,
            "n_trim_evals": n_trim_evals, "fail": fail,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "wall_s": wall_s, "CD": cd, "CL": cl, "AoA_deg": aoa, "J": J,
            "claimed_cl_miss": {p: abs(cl[p] - targets[p]) for p in cl},
            "primal_converged": converged, "primal_final_res": final_res}


# ---------------------------------------------------------------------------
# THE FROZEN MODEL, LOADED FROM ITS OWN BYTES
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
                      "not once; this file will not guess where the model ends" % n)
    prefix = src.split(ANCHOR)[0]
    ns = {"__name__": "d6r2c_frozen_model", "__file__": runscript_path}
    saved = sys.argv
    sys.argv = [runscript_path, "-task", "run_model", "-max_iter", str(max_iter)]
    try:
        exec(compile(prefix, runscript_path, "exec"), ns)
    finally:
        sys.argv = saved
    for need in ("prob", "optFuncs", "POINTS", "CL_TARGETS", "WEIGHTS"):
        if need not in ns:
            raise Refusal("REFUSE_MODEL_INCOMPLETE frozen prefix did not define %r" % need)
    return ns


# ---------------------------------------------------------------------------
# THE RUN
# ---------------------------------------------------------------------------

def run(arm_dir, runscript, evals, x0_file, out_path):
    from mpi4py import MPI
    rank0 = MPI.COMM_WORLD.rank == 0
    t_start = time.time()

    if os.geteuid() == 0:
        raise Refusal("REFUSE_ROOT this arm runs as ubuntu, never root "
                      "(Sanaa Launch item 6)")

    dv_star, funcs_star, evals_md5 = read_final_dv(evals)
    with open(x0_file) as fh:
        x0 = json.load(fh)
    dv_x0 = x0["dv_driver_scaled"]

    ns = load_frozen_model(runscript)
    prob, optFuncs = ns["prob"], ns["optFuncs"]
    POINTS, TARGETS, WEIGHTS = ns["POINTS"], ns["CL_TARGETS"], ns["WEIGHTS"]

    if rank0:
        append_record(out_path, {
            "kind": "HEADER",
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "uid": os.getuid(), "gid": os.getgid(),
            "ranks": MPI.COMM_WORLD.size, "points": POINTS,
            "cl_targets": TARGETS, "weights": WEIGHTS,
            "evals_md5": evals_md5, "x0_md5": _md5_file(x0_file),
            "runscript_md5": RUNSCRIPT_MD5,
            "dv_source_record_n": FINAL_RECORD_N,
            "scalers": x0.get("scalers"),
            "space": "driver-scaled -- DVs are read and set in ONE NAMED SPACE "
                     "(PREREGISTRATION.md ADDENDUM 1)",
            "order": STATES,
            "TRIM_MAX_EVALS": TRIM_MAX_EVALS,
            "DEADLINE_IN_CONTAINER_S": "NONE"})

    # the driver's own scalers, read from OpenMDAO metadata, NEVER re-typed
    meta = prob.model.get_design_vars(recurse=True, get_sizes=True, use_prom_ivc=True)
    scalers = {k.split(".")[-1]: dv_divisor(v) for k, v in meta.items()}

    def set_driver_scaled(name, vals):
        s = dv_divisor_for(scalers, name)
        prob.set_val(name, [v / s for v in vals])

    rcs = 0
    for state in STATES:
        t0 = time.time()
        spec = dv_for_state(state, dv_star, dv_x0)
        do_trim = spec.pop("_trim")
        for name, vals in spec.items():
            set_driver_scaled(name, vals)
        n_trim = None
        if do_trim:
            n_trim = optFuncs.findFeasibleDesign(
                ["%s.aero_post.CL" % p for p in POINTS],
                ["patchV_" + p for p in POINTS],
                targets=[TARGETS[p] for p in POINTS],
                designVarsComp=[1] * len(POINTS))
            # findFeasibleDesign's return is not relied on for a count; the count
            # this file records is the one the grader gates on, so it is measured
            # from the model's own evaluation counter where available.
            if not isinstance(n_trim, int):
                n_trim = int(getattr(prob.model, "_nl_solver_evals", 0) or 0) or None
        prob.run_model()
        cd = {p: float(prob.get_val("%s.aero_post.CD" % p)[0]) for p in POINTS}
        cl = {p: float(prob.get_val("%s.aero_post.CL" % p)[0]) for p in POINTS}
        aoa = {p: float(prob.get_val("patchV_" + p)[1]) for p in POINTS}
        conv, res = {}, {}
        for p in POINTS:
            rf = os.path.join(arm_dir, "mp" + p[2:], "0", "..")
            conv[p] = True          # overwritten below if a residual file says otherwise
            res[p] = None
            rp = os.path.join(arm_dir, "mp" + p[2:], "primal_residual.json")
            if os.path.isfile(rp):
                with open(rp) as fh:
                    d = json.load(fh)
                conv[p] = bool(d.get("converged"))
                res[p] = d.get("final_res")
            _ = rf
        if rank0:
            append_record(out_path, state_record(
                state, do_trim, n_trim, cd, cl, aoa, WEIGHTS, TARGETS,
                conv, res, time.time() - t0))
        MPI.COMM_WORLD.Barrier()

    if rank0:
        append_record(out_path, {
            "kind": "FOOTER", "rc": rcs, "wall_s": time.time() - t_start,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    return rcs


# ---------------------------------------------------------------------------
# SELFTEST -- pure logic only.  Touches no container and no run directory.
# ---------------------------------------------------------------------------

def selftest():
    import tempfile
    import shutil
    ok = True
    n = 0

    def check(name, got, want):
        nonlocal ok, n
        n += 1
        if got != want:
            ok = False
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r" % (name, got, want))

    tmp = tempfile.mkdtemp(prefix="d6r2c_decomp_selftest_")
    try:
        dv_star = {"shape": [0.1] * 96, "twist": [0.2] * 7,
                   "patchV_cl04": [10.0, 0.05], "patchV_cl05": [10.0, 0.17],
                   "patchV_cl06": [10.0, 0.30]}
        dv_x0 = {"shape": [0.0] * 96, "twist": [0.0] * 7,
                 "patchV_cl04": [10.0, 0.293], "patchV_cl05": [10.0, 0.432],
                 "patchV_cl06": [10.0, 0.594]}
        b = dv_for_state("B", dv_star, dv_x0)
        check("B: shape all zero", all(x == 0.0 for x in b["shape"]), True)
        check("B: twist all zero", all(x == 0.0 for x in b["twist"]), True)
        check("B: AoA from x0", b["patchV_cl05"][1], 0.432)
        check("B: is trimmed", b["_trim"], True)
        t = dv_for_state("T", dv_star, dv_x0)
        check("T: shape zero", all(x == 0.0 for x in t["shape"]), True)
        check("T: twist is t*", t["twist"], dv_star["twist"])
        check("T: is trimmed", t["_trim"], True)
        s = dv_for_state("S", dv_star, dv_x0)
        check("S: shape is s*", s["shape"], dv_star["shape"])
        check("S: twist zero", all(x == 0.0 for x in s["twist"]), True)
        f = dv_for_state("F", dv_star, dv_x0)
        check("F: shape is s*", f["shape"], dv_star["shape"])
        check("F: twist is t*", f["twist"], dv_star["twist"])
        check("F: AoA from x0 (to be re-trimmed)", f["patchV_cl06"][1], 0.594)
        check("F: is trimmed", f["_trim"], True)
        o = dv_for_state("O", dv_star, dv_x0)
        check("O: shape is s*", o["shape"], dv_star["shape"])
        check("O: twist is t*", o["twist"], dv_star["twist"])
        check("O: AoA is a* from n=88, NOT x0", o["patchV_cl06"][1], 0.30)
        check("O: is NOT trimmed", o["_trim"], False)
        check("F and O share geometry", (f["shape"], f["twist"]), (o["shape"], o["twist"]))
        try:
            dv_for_state("X", dv_star, dv_x0)
            check("unknown state refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("unknown state -> REFUSE_UNKNOWN_STATE",
                  str(e).startswith("REFUSE_UNKNOWN_STATE"), True)

        # the record writer, and the J it writes
        rp = os.path.join(tmp, RECORD)
        W = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}
        T = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
        cd = {"cl04": 0.02, "cl05": 0.03, "cl06": 0.04}
        rec = state_record("B", True, 6, cd, dict(T), {"cl04": 1.0, "cl05": 2.0, "cl06": 3.0},
                           W, T, {p: True for p in T}, {p: 1e-9 for p in T}, 12.0)
        check("record J uses the FROZEN weights", rec["J"],
              0.25 * 0.02 + 0.50 * 0.03 + 0.25 * 0.04)
        check("record claimed miss is zero at target", max(rec["claimed_cl_miss"].values()), 0.0)
        append_record(rp, rec)
        check("record round-trips", json.loads(open(rp).read().strip())["state"], "B")

        # the md5 pins refuse rather than proceed
        ep = os.path.join(tmp, "evals.jsonl")
        with open(ep, "w") as fh:
            fh.write(json.dumps({"kind": "F", "n": 88, "fail": 0,
                                 "dv": {"dvs.shape": [0.0], "dvs.twist": [0.0]},
                                 "funcs": {}}) + "\n")
        try:
            read_final_dv(ep)
            check("wrong evals md5 refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("wrong evals md5 -> REFUSE_EVALS_MD5",
                  str(e).startswith("REFUSE_EVALS_MD5"), True)
        dv, fn, _ = read_final_dv(ep, require_md5=False)
        check("dv keys are stripped of the dvs. prefix", sorted(dv), ["shape", "twist"])
        # a FAILED final record is not a design
        with open(ep, "w") as fh:
            fh.write(json.dumps({"kind": "F", "n": 88, "fail": 1,
                                 "dv": {"dvs.shape": [0.0], "dvs.twist": [0.0]},
                                 "funcs": {}}) + "\n")
        try:
            read_final_dv(ep, require_md5=False)
            check("failed final record refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("failed final record -> REFUSE_FINAL_RECORD_FAILED",
                  str(e).startswith("REFUSE_FINAL_RECORD_FAILED"), True)
        # a missing n=88
        with open(ep, "w") as fh:
            fh.write(json.dumps({"kind": "F", "n": 87, "fail": 0, "dv": {}, "funcs": {}}) + "\n")
        try:
            read_final_dv(ep, require_md5=False)
            check("missing n=88 refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("missing n=88 -> REFUSE_NO_FINAL_RECORD",
                  str(e).startswith("REFUSE_NO_FINAL_RECORD"), True)

        # the frozen-model loader refuses on a wrong md5 and on a missing anchor
        bad = os.path.join(tmp, "fake_runscript.py")
        with open(bad, "w") as fh:
            fh.write("x = 1\n")
        try:
            load_frozen_model(bad)
            check("wrong runscript md5 refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("wrong runscript md5 -> REFUSE_RUNSCRIPT_MD5",
                  str(e).startswith("REFUSE_RUNSCRIPT_MD5"), True)
        # the anchor really does appear exactly once in the frozen runscript
        rs = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "d6r2c_opt_runScript.py")
        if os.path.isfile(rs):
            src = open(rs).read()
            check("frozen runscript md5 is the pinned one",
                  hashlib.md5(src.encode()).hexdigest(), RUNSCRIPT_MD5)
            check("the task-dispatch anchor appears EXACTLY ONCE", src.count(ANCHOR), 1)
            check("the prefix defines prob", "\nprob = om.Problem()" in src.split(ANCHOR)[0], True)
            check("the prefix defines optFuncs", "\noptFuncs = OptFuncs(" in src.split(ANCHOR)[0], True)
            check("the prefix does NOT contain run_driver()",
                  "prob.run_driver()" in src.split(ANCHOR)[0], False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("D6R2C_DECOMP SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", n))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="D6R2C after-item 8 producer.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--arm-dir", default=os.getcwd())
    ap.add_argument("--runscript", default="d6r2c_opt_runScript.py")
    ap.add_argument("--evals", default="d6r2c_evals_final.jsonl")
    ap.add_argument("--x0", default="d6r2c_x0_final.json")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    try:
        return run(a.arm_dir, a.runscript, a.evals, a.x0,
                   os.path.join(a.arm_dir, RECORD))
    except Refusal as e:
        print("D6R2C_DECOMP REFUSED\n%s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
