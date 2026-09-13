#!/usr/bin/env python3
# ===========================================================================
# d6r2c_dec4_decomp.py -- PRODUCER for the successor to after-item 8
# ===========================================================================
#
# Registered by PREREGISTRATION_AFTER_ITEM8_R2.md sections 1, 3 and 5, and IN
# THE SAME COMMIT, BEFORE ANY CONTAINER STARTS (CLAUDE.md rule 2).
#
# A FORK of d6r2c_decomp.py (md5 42ec0dd582584812a69129a474b2783e), which stays
# on disk unedited.  What changed, exhaustively:
#   (1) a SIXTH state, B2 -- the baseline re-trimmed from the O state's fields.
#       REPORTED, NEVER GATED; it measures N-D48's path-dependence directly;
#   (2) the INCIDENCE GOVERNOR -- the registered analysis bound is asserted on
#       every incidence set, and any jump larger than AOA_STEP_MAX_DEG is walked
#       in sub-steps, each one a converged primal.  ARM DEC3 DIED BECAUSE OF THE
#       ABSENCE OF THIS, NOT BECAUSE OF A BOUND: findFeasibleDesign calls
#       prob.set_val and prob.run_model directly, so add_design_var's bounds --
#       which live in IPOPT -- never constrained it.  It jumped 3.805494637 deg
#       in one step and the pressure equation stalled at 1.091200008e-05;
#   (3) the trim-evaluation count is MEASURED, by counting calls, not inferred
#       from a return value.  In DEC3 every count was recorded null and the
#       registered cap was therefore INERT;
#   (4) the geometric constraints thickcon and volcon are RECORDED, because they
#       are this family's only external, path-independent anchor (D2-GEO, L-588);
#   (5) every incidence VISITED is recorded, so the grader can check the bound
#       and the step cap rather than take this file's word for them.
#
# THE WIDENED INCIDENCE BOUND IS AN ANALYSIS BOUND AND IT NEVER TOUCHED THE
# OPTIMISATION.  d6r2c_opt_runScript.py is loaded from its own unedited bytes,
# md5-asserted below; its line 280 still reads
# `self.add_design_var("patchV_" + pt, lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)`.
# O_mp's GATE FAIL, its 24.732 % weighted drag reduction and its
# Jf/J0 = 0.752677 stand exactly as graded, and that md5 is how a reader checks it.
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
import math
import os
import sys
import time

RUNSCRIPT_MD5 = "2f2ae43a627146cf8e0f065b035ada4b"   # PREREGISTRATION.md ADDENDUM 1, A1.6
EVALS_MD5 = "2c0b8143caad198cd2e21d8047986aa3"       # AFTER_ITEMS section 0b
FINAL_RECORD_N = 88                                  # AFTER_ITEMS section 1
ANCHOR = '\nif args.task == "run_driver":\n'

# "the six states in one container, order B -> T -> S -> F -> O -> B2"
STATES = ["B", "T", "S", "F", "O"]
REPORTED_STATES = ["B2"]          # REPORTED, NEVER GATED (registration sec 1e)
ORDER = STATES + REPORTED_STATES
# "findFeasibleDesign gets at most TRIM_MAX_EVALS = 15 primal evaluations per state"
TRIM_MAX_EVALS = 15
# "AOA_LOWER_DEG = -4.9570114", "AOA_UPPER_DEG = 10.0"  (registration sec 1d)
AOA_LOWER_DEG = -4.9570114
AOA_UPPER_DEG = 10.0
# "AOA_STEP_MAX_DEG = 0.987284431"  (registration sec 1f) -- the largest single
# incidence jump whose primal is MEASURED to have converged on this case.
AOA_STEP_MAX_DEG = 0.987284431
# "CONT_MAX_STEPS = 12"  (registration sec 1f)
CONT_MAX_STEPS = 12
# The geometric constraints, this family's only external path-independent anchor.
GEO_KEYS = ["geometry_cl05.thickcon", "geometry_cl05.volcon"]
RECORD = "d6r2c_dec4.jsonl"


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
    if state not in ORDER:
        raise Refusal("REFUSE_UNKNOWN_STATE %r" % state)
    zeros_shape = [0.0] * len(dv_star["shape"])
    zeros_twist = [0.0] * len(dv_star["twist"])
    if state in ("B", "B2"):
        # B2 IS THE SAME DESIGN POINT AS B.  It differs ONLY in the fields it is
        # reached from -- B is cold, B2 follows O -- which is the whole content of
        # the path-dependence measurement (registration sec 1e).
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

# ---------------------------------------------------------------------------
# THE INCIDENCE GOVERNOR -- the registered analysis bound, and the continuation
# ---------------------------------------------------------------------------
#
# WHAT KILLED ARM DEC3, STATED SO THIS FILE CANNOT BE MISREAD AS A BOUND FIX.
# findFeasibleDesign is a root find.  It calls prob.set_val on patchV_<pt> and
# then prob.run_model().  add_design_var's `lower`/`upper` are OPTIMISER bounds:
# they reach IPOPT and nothing else, so they never constrained the trim.  In DEC3
# the trim's first Newton step for the shape-only state asked for
# AoA = -0.8751112647 deg, a jump of 3.805494637 deg from a field converged at
# 2.9303833722 deg, and the primal stalled at a min residual of 1.091200008e-05
# against primalMinResTol = 1.0e-8 with U, he and nuTilda converged and the
# PRESSURE EQUATION ALONE lagging.  WIDENING A BOUND WOULD NOT HAVE SAVED IT.
# What was missing was a bounded approach, and that is what this class is.


def plan_substeps(prev_deg, target_deg, step_max=AOA_STEP_MAX_DEG):
    """The incidences to visit walking from `prev_deg` to `target_deg`.

    PURE FUNCTION, no solver, driven by --selftest.  Returns the INTERMEDIATE
    incidences only; the caller visits `target_deg` itself last.  An empty list
    means the jump was already inside the measured-converging step."""
    if prev_deg is None:
        return []
    gap = target_deg - prev_deg
    if abs(gap) <= step_max:
        return []
    n = int(math.ceil(abs(gap) / step_max))
    if n > CONT_MAX_STEPS:
        raise Refusal(
            "REFUSE_CONTINUATION_TOO_LONG %.9f -> %.9f deg needs %d sub-steps at "
            "AOA_STEP_MAX_DEG = %.9f, above the registered CONT_MAX_STEPS = %d"
            % (prev_deg, target_deg, n, step_max, CONT_MAX_STEPS))
    return [prev_deg + gap * (k / float(n)) for k in range(1, n)]


class IncidenceGovernor(object):
    """Wraps prob.run_model.  Asserts the registered bound on every incidence the
    caller sets, walks any oversized jump in sub-steps, counts every primal
    evaluation, and records every incidence visited.

    IT CHANGES NO VALUE ANY CALLER OBSERVES.  The caller's requested incidence is
    always the last one solved, so findFeasibleDesign reads the CL at exactly the
    incidence it asked for.  The only difference is the field it started from."""

    def __init__(self, prob, points, scalers, dv_divisor_for):
        self._prob = prob
        self._points = list(points)
        self._scalers = scalers
        self._div = dv_divisor_for
        self._real = prob.run_model
        self.last = {p: None for p in self._points}   # last incidence SOLVED
        self.visited = {p: [] for p in self._points}
        self.n_evals = 0
        self.n_continuation = 0
        prob.run_model = self._run_model

    def _aoa(self, p):
        s = self._div(self._scalers, "patchV_" + p)
        return float(self._prob.get_val("patchV_" + p)[1]) * s

    def _set_aoa(self, p, deg):
        s = self._div(self._scalers, "patchV_" + p)
        cur = self._prob.get_val("patchV_" + p)
        self._prob.set_val("patchV_" + p, [float(cur[0]), deg / s])

    def _solve(self):
        self.n_evals += 1
        for p in self._points:
            a = self._aoa(p)
            self.visited[p].append(a)
            self.last[p] = a
        self._real()

    def _run_model(self):
        want = {}
        for p in self._points:
            a = self._aoa(p)
            if not (AOA_LOWER_DEG <= a <= AOA_UPPER_DEG):
                raise Refusal(
                    "REFUSE_AOA_OUT_OF_BOUND %s asked for %.10f deg, outside the "
                    "registered ANALYSIS bound [%.7f, %.7f].  The bound is never "
                    "widened at run time: below it the case stops being a "
                    "lift-constrained cruise wing (registration sec 1d)."
                    % (p, a, AOA_LOWER_DEG, AOA_UPPER_DEG))
            want[p] = a
        plans = {p: plan_substeps(self.last[p], want[p]) for p in self._points}
        n_sub = max([len(v) for v in plans.values()] + [0])
        for k in range(n_sub):
            for p in self._points:
                seq = plans[p]
                self._set_aoa(p, seq[k] if k < len(seq) else want[p])
            self._solve()
            self.n_continuation += 1
        for p in self._points:
            self._set_aoa(p, want[p])
        self._solve()

    def release(self):
        self._prob.run_model = self._real


def append_record(path, obj):
    with open(path, "a") as fh:
        fh.write(json.dumps(obj, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def state_record(state, trimmed, n_trim_evals, cd, cl, aoa, weights, targets,
                 converged, final_res, wall_s, fail=0, aoa_visited=None,
                 thickcon=None, volcon=None, n_continuation_steps=None):
    J = sum(weights[p] * cd[p] for p in sorted(cd))
    return {"kind": "STATE", "state": state, "trimmed": trimmed,
            "n_trim_evals": n_trim_evals, "fail": fail,
            "aoa_visited_deg": aoa_visited,
            "n_continuation_steps": n_continuation_steps,
            "thickcon": thickcon, "volcon": volcon,
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
            "order": ORDER,
            "reported_never_gated": REPORTED_STATES,
            "TRIM_MAX_EVALS": TRIM_MAX_EVALS,
            "AOA_LOWER_DEG": AOA_LOWER_DEG, "AOA_UPPER_DEG": AOA_UPPER_DEG,
            "AOA_STEP_MAX_DEG": AOA_STEP_MAX_DEG, "CONT_MAX_STEPS": CONT_MAX_STEPS,
            "aoa_bound_note":
                "The incidence bound recorded here is an ANALYSIS bound and it never "
                "touched the optimisation.  d6r2c_opt_runScript.py is loaded from its "
                "own unedited bytes at the md5 above and still carries "
                "lower=[U0, 0.0] at its line 280.",
            "DEADLINE_IN_CONTAINER_S": "NONE"})

    # the driver's own scalers, read from OpenMDAO metadata, NEVER re-typed
    meta = prob.model.get_design_vars(recurse=True, get_sizes=True, use_prom_ivc=True)
    scalers = {k.split(".")[-1]: dv_divisor(v) for k, v in meta.items()}

    def set_driver_scaled(name, vals):
        s = dv_divisor_for(scalers, name)
        prob.set_val(name, [v / s for v in vals])

    # THE GOVERNOR IS INSTALLED ONCE, BEFORE THE FIRST STATE, AND IS NEVER
    # REMOVED.  It wraps prob.run_model, so it also governs the calls
    # findFeasibleDesign makes internally -- which is the only place the failing
    # jump of arm DEC3 could have been caught.
    gov = IncidenceGovernor(prob, POINTS, scalers, dv_divisor_for)

    rcs = 0
    for state in ORDER:
        t0 = time.time()
        spec = dv_for_state(state, dv_star, dv_x0)
        do_trim = spec.pop("_trim")
        for name, vals in spec.items():
            set_driver_scaled(name, vals)
        n0, c0 = gov.n_evals, gov.n_continuation
        for p in POINTS:
            gov.visited[p] = []
        if do_trim:
            optFuncs.findFeasibleDesign(
                ["%s.aero_post.CL" % p for p in POINTS],
                ["patchV_" + p for p in POINTS],
                targets=[TARGETS[p] for p in POINTS],
                designVarsComp=[1] * len(POINTS))
        prob.run_model()
        # THE COUNT IS MEASURED, NOT INFERRED.  findFeasibleDesign's return value
        # was recorded as null in every state of arm DEC3, which left the
        # registered cap TRIM_MAX_EVALS unreadable and therefore inert.  This
        # count is the governor's own call counter, minus the continuation
        # sub-steps, which are this file's doing and not the trim's.
        n_cont = gov.n_continuation - c0
        n_trim = (gov.n_evals - n0) - n_cont
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
        # The external, path-independent anchor (D2-GEO).  Read back from the
        # model, never recomputed here.  Absent for a state whose geometry has no
        # inherited record -- the grader knows which states are anchored.
        geo = {}
        for k in GEO_KEYS:
            try:
                geo[k] = [float(v) for v in prob.get_val(k)]
            except Exception as exc:      # noqa: BLE001 -- named, never swallowed
                raise Refusal("REFUSE_NO_GEO state %s could not read %r: %s -- D2-GEO "
                              "is this family's only floating-point tight external "
                              "anchor and it is not optional (L-588)" % (state, k, exc))
        if rank0:
            append_record(out_path, state_record(
                state, do_trim, n_trim, cd, cl, aoa, WEIGHTS, TARGETS,
                conv, res, time.time() - t0,
                aoa_visited={p: list(gov.visited[p]) for p in POINTS},
                thickcon=geo["geometry_cl05.thickcon"],
                volcon=geo["geometry_cl05.volcon"],
                n_continuation_steps=n_cont))
        MPI.COMM_WORLD.Barrier()

    if rank0:
        append_record(out_path, {
            "kind": "FOOTER", "rc": rcs, "wall_s": time.time() - t_start,
            "n_primal_evals_total": gov.n_evals,
            "n_continuation_steps_total": gov.n_continuation,
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
        # ================= THE INCIDENCE GOVERNOR ==========================
        # plan_substeps is a PURE function and is driven on both sides of the
        # measured-converging step, at the registered limit, and past it.
        check("substep: a jump inside the measured step needs none",
              plan_substeps(2.0, 2.0 + AOA_STEP_MAX_DEG * 0.999), [])
        check("substep: AT the measured step needs none",
              plan_substeps(2.0, 2.0 + AOA_STEP_MAX_DEG), [])
        check("substep: ONE ULP past it needs one",
              len(plan_substeps(2.0, math.nextafter(2.0 + AOA_STEP_MAX_DEG, 99.0))), 1)
        # the jump that killed arm DEC3: 2.9303833722 -> -0.8751112647
        _p0, _p1 = 2.9303833722365633, -0.8751112647
        dec3 = plan_substeps(_p0, _p1)
        check("substep: the DEC3 jump is walked in 4 legs", len(dec3), 3)
        check("substep: every DEC3 leg is inside the measured maximum",
              all(abs(b - a) <= AOA_STEP_MAX_DEG * (1 + 1e-12) for a, b in
                  zip([_p0] + dec3, dec3 + [_p1])), True)
        check("substep: the walk is monotone",
              all(dec3[i] > dec3[i + 1] for i in range(len(dec3) - 1)), True)
        check("substep: no previous incidence means no continuation",
              plan_substeps(None, -4.0), [])
        try:
            plan_substeps(0.0, AOA_STEP_MAX_DEG * (CONT_MAX_STEPS + 1.5))
            check("substep: past CONT_MAX_STEPS refuses", "no refusal", "Refusal")
        except Refusal as e:
            check("substep: past CONT_MAX_STEPS -> REFUSE_CONTINUATION_TOO_LONG",
                  str(e).startswith("REFUSE_CONTINUATION_TOO_LONG"), True)
        try:
            check("substep: NEGATIVE -- exactly CONT_MAX_STEPS does not refuse",
                  len(plan_substeps(0.0, -AOA_STEP_MAX_DEG * CONT_MAX_STEPS)),
                  CONT_MAX_STEPS - 1)
        except Refusal as e:
            check("substep: exactly CONT_MAX_STEPS must not refuse", str(e), "no refusal")

        # The governor, driven against a FAKE prob -- no solver, no container.
        # L-589: this control CANNOT bear on anything about the real model's
        # framework behaviour, and it does not claim to.  What it drives is this
        # file's own arithmetic: the bound assertion, the sub-step walk, the call
        # count and the recorded path.  The real-model behaviour it cannot see is
        # named in the registration's section 11a.
        class _FakeProb(object):
            def __init__(self, aoa):
                self.v = {"patchV_" + p: [100.0, aoa[p] / 0.1] for p in aoa}
                self.calls = []
                self.run_model = self._rm

            def get_val(self, k):
                return list(self.v[k])

            def set_val(self, k, val):
                self.v[k] = list(val)

            def _rm(self):
                self.calls.append({k: self.v[k][1] * 0.1 for k in self.v})
        pts = ["cl04", "cl05", "cl06"]
        sc = {"patchV_cl04": 0.1, "patchV_cl05": 0.1, "patchV_cl06": 0.1}
        fp = _FakeProb({p: _p0 for p in pts})
        g = IncidenceGovernor(fp, pts, sc, dv_divisor_for)
        fp.run_model()
        check("governor: the first call is one evaluation", g.n_evals, 1)
        check("governor: the first call is not a continuation", g.n_continuation, 0)
        for p in pts:
            fp.set_val("patchV_" + p, [100.0, _p1 / 0.1])
        fp.run_model()
        check("governor: the DEC3 jump costs 3 continuation legs + 1",
              (g.n_continuation, g.n_evals), (3, 5))
        check("governor: the LAST incidence solved is the one that was ASKED FOR",
              abs(fp.calls[-1]["patchV_cl04"] - _p1) < 1e-9, True)
        check("governor: every incidence solved is recorded",
              len(g.visited["cl04"]), g.n_evals)
        check("governor: no recorded incidence is outside the bound",
              all(AOA_LOWER_DEG <= a <= AOA_UPPER_DEG for a in g.visited["cl04"]), True)
        for bad, why in ((math.nextafter(AOA_LOWER_DEG, -99.0), "below"),
                         (math.nextafter(AOA_UPPER_DEG, 99.0), "above")):
            fp2 = _FakeProb({p: 2.0 for p in pts})
            IncidenceGovernor(fp2, pts, sc, dv_divisor_for)
            fp2.set_val("patchV_cl04", [100.0, bad / 0.1])
            try:
                fp2.run_model()
                check("governor: one ulp %s the bound refuses" % why,
                      "no refusal", "Refusal")
            except Refusal as e:
                check("governor: one ulp %s the bound -> REFUSE_AOA_OUT_OF_BOUND" % why,
                      str(e).startswith("REFUSE_AOA_OUT_OF_BOUND"), True)
        fp3 = _FakeProb({p: 2.0 for p in pts})
        g3 = IncidenceGovernor(fp3, pts, sc, dv_divisor_for)
        fp3.set_val("patchV_cl04", [100.0, AOA_LOWER_DEG / 0.1])
        try:
            fp3.run_model()
            check("governor: NEGATIVE -- AT the bound is legal", g3.n_evals > 0, True)
        except Refusal as e:
            check("governor: AT the bound must be legal", str(e), "no refusal")

        # ================= STATE B2 =======================================
        check("B2 is the SAME design point as B",
              dv_for_state("B2", dv_star, dv_x0), dv_for_state("B", dv_star, dv_x0))
        check("B2 is trimmed", dv_for_state("B2", dv_star, dv_x0)["_trim"], True)
        check("the registered order ends with B2", ORDER[-1], "B2")
        check("B2 is REPORTED, never gated", REPORTED_STATES, ["B2"])
        check("the re-derived trim cap is 15", TRIM_MAX_EVALS, 15)
        check("the record file is the successor's own", RECORD, "d6r2c_dec4.jsonl")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("D6R2C_DEC4_DECOMP SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", n))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="D6R2C after-item 8 SUCCESSOR producer (arm DEC4).")
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
        print("D6R2C_DEC4_DECOMP REFUSED\n%s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
