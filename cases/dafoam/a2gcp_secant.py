#!/usr/bin/env python3
"""A2-GC-P primal-only secant trim: the pure core, its readers, its controls.

REGISTERED BY cases/dafoam/A2_GC_P_PRIMAL_TRIM_GRID_CONVERGENCE_PREREGISTRATION.md
(PERMISSION: NOT_FROZEN at the time this file was written; the freeze is the
dafoam supervisor's act). Every constant below is QUOTED from that document's
section 4.1 and nothing here may be treated as a threshold in its own right.

WHY THIS FILE EXISTS SEPARATELY FROM THE DRIVER BLOCK. It imports nothing from
DAFoam, OpenMDAO, MPI or OpenFOAM. That is deliberate and load-bearing: it lets
--selftest run to completion BEFORE any solver starts, which is what the
pre-registration requires and what a selftest that could only run inside the
container could never give.

WHAT REPLACES WHAT. optFuncs.findFeasibleDesign is a GRADIENT-BASED trim; the
adjoint it needs dominated the parent item's wall time and cap-stopped it
(A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md section R3). The graded quantity --
CD at fixed CL -- needs no adjoint. This is the primal-only replacement.

ORDER OF OPERATIONS, and it is not negotiable:

  1. preflight() -- the rule-3 birth register. Every reader is shown able to see
     a planted non-zero THROUGH THE REAL READER, on bytes written by the REAL
     PRODUCER, and REFUSES (exit 2) if it cannot. VERIFICATION_CHARTER section 2j:
     an instrument that has not answered that question does not grade.
  2. only then the trim.

Usage:  a2gcp_secant.py --selftest    controls + secant suites; NO solver
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

# ---------------------------------------------------------------------------
# Thresholds -- ALL quoted from the pre-registration section 4.1. None invented.
# ---------------------------------------------------------------------------
CL_TARGET = 0.500          # graded quantity is CD at THIS fixed CL
TRIM_TOL = 5.0e-4          # |CL - CL_TARGET|; a miss is BLOCKED, never estimated
ALPHA0_DEG = 4.0           # the pristine script's own aoa0
A_SEED_PER_DEG = 0.10      # SEED ONLY. Places evaluation 2. NEVER reported as a
                           # lift slope and never enters a graded number.
N_SECANT_MAX = 8           # primal evaluations per level, including evaluation 1
STEP_MAX_DEG = 2.0         # per-update step limiter
ALPHA_MIN_DEG = 0.0
ALPHA_MAX_DEG = 10.0
DEN_MIN = 1.0e-9           # secant denominator floor; below it we REFUSE to divide

# The real-producer artifact the birth register reads. Registered in the
# pre-registration section 10 as a REQUIRED RETAINED ARTIFACT: if it is deleted,
# LIMB 1 cannot run and the selftest REFUSES rather than skipping.
REAL_LOG = os.environ.get(
    "A2GCP_REAL_LOG",
    "/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence/L1/level.log")

# The parent's own published L1 values (its section R1). The birth register
# asserts the CLEAN reading of the real bytes reproduces these, so the readers
# are anchored to a number somebody else published, not to a fixture.
PARENT_L1_CD = 0.02961982052
PARENT_L1_CL = 0.4999996084
PARENT_L1_AOA = 4.326120747
PARENT_L1_NSAMPLES = 66

PLANT = 1.234e-03          # the lab's standing plant constant


class Refuse(Exception):
    """A reader that could not be shown able to see a non-zero. Exit 2."""


class Blocked(Exception):
    """The trim cannot produce a standing value. The level is BLOCKED, and the
    reason is recorded -- it is NEVER estimated and NEVER interpolated."""

    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail


# ---------------------------------------------------------------------------
# THE READERS.
#
# They read the SOLVER'S OWN PRINTED LINES, not a GC_RESULT line. That is a
# deliberate change from the parent instrument and the pre-registration section
# 9.2 records it: the parent's grader reads a GC_RESULT line that NO A2-GC run
# has ever emitted -- both completing runs were killed by their cap during the
# post-trim adjoint, before the emit (parent section R4). These four line forms
# DO exist in real producer output and are verified against it in birth_register().
#
# Every reader is a pure function of text so a plant can be pushed through the
# REAL reader rather than through a stand-in.
# ---------------------------------------------------------------------------
_RE_CD = re.compile(r"^CD:\s+([-\d.eE+]+)\s+final:", re.M)
_RE_CL = re.compile(r"^CL:\s+([-\d.eE+]+)\s+final:", re.M)
_RE_AOA = re.compile(r"AoA\s*=\s*([-\d.eE+]+)\s*degs")


def read_cd_series(text: str):
    """Every CD the solver printed, in order. This IS the GATE I history: the
    identical quantity the graded number is read from, so there is no rescale
    and no scaling guard to get wrong (pre-registration section 6.3)."""
    return [float(v) for v in _RE_CD.findall(text)]


def read_cl_series(text: str):
    return [float(v) for v in _RE_CL.findall(text)]


def read_aoa_series(text: str):
    """Incidence, from the solver's own 'Setting UMag = ... AoA = ... degs'."""
    return [float(v) for v in _RE_AOA.findall(text)]


def read_cd(text: str) -> float:
    s = read_cd_series(text)
    return s[-1] if s else 0.0


def read_cl(text: str) -> float:
    s = read_cl_series(text)
    return s[-1] if s else 0.0


def read_aoa(text: str) -> float:
    s = read_aoa_series(text)
    return s[-1] if s else 0.0


def read_iter_delta(series) -> float:
    """delta_iter: the swing in CD over the last 20 % of the samples.

    THE HIGHEST-VALUE PLANT IN THIS ITEM. A delta_iter stuck at zero makes
    Delta_mesh/delta_iter infinite, passes GATE I trivially, and hands back an
    observed order that is pure iterative noise dressed as discretisation --
    exactly the failure Sanaa's SS0 clause 2 was written against.
    """
    s = list(series)
    if not s:
        return 0.0
    n = max(2, int(round(0.2 * len(s))))
    w = s[-n:]
    return max(w) - min(w)


def read_trim_record(text: str):
    """The trim's own record, as the driver writes it.

    HONEST LIMIT, and the pre-registration section 10 states it rather than
    glossing it: NO real producer bytes for this reader exist anywhere on this
    box, because no A2-GC-P run has written a trim_record.json. Its control below
    is on PRODUCER-SHAPED bytes written by this harness, which is precisely the
    condition VERIFICATION_CHARTER section 2j names as INSUFFICIENT. The full
    2j demonstration is OWED and is registered as a precondition: L2 and L3 may
    not be graded until the register has been re-run against L1's own emitted
    trim_record.json.
    """
    try:
        rec = json.loads(text)
    except Exception:
        return {"n_evaluations": 0, "converged": False, "alpha_star": 0.0}
    if not isinstance(rec, dict):
        return {"n_evaluations": 0, "converged": False, "alpha_star": 0.0}
    return {
        "n_evaluations": int(rec.get("n_evaluations", 0) or 0),
        "converged": bool(rec.get("converged", False)),
        "alpha_star": float(rec.get("alpha_star") or 0.0),
    }


# ---------------------------------------------------------------------------
# THE PLANT. Applied INTO the real producer's own bytes, by line, so the reader
# under test reads reality with a known perturbation in it -- not a fixture.
# ---------------------------------------------------------------------------
def plant_into_log(text: str, plant: float = PLANT) -> str:
    """Add `plant` to the LAST CD line, the LAST CL line and the LAST AoA line,
    and append one extra CD/CL sample so the series length also moves."""
    lines = text.splitlines(keepends=True)

    def _last_index(pred):
        for i in range(len(lines) - 1, -1, -1):
            if pred(lines[i]):
                return i
        return None

    i_cd = _last_index(lambda l: _RE_CD.match(l))
    i_cl = _last_index(lambda l: _RE_CL.match(l))
    i_ao = _last_index(lambda l: _RE_AOA.search(l))
    if i_cd is None or i_cl is None or i_ao is None:
        raise Refuse(
            "REFUSED: the real producer artifact does not carry the line forms "
            f"the readers parse (CD/CL/AoA) -- {REAL_LOG!r}. A plant that cannot "
            "be applied to real bytes is not a rule-3 control.")

    v_cd = float(_RE_CD.match(lines[i_cd]).group(1)) + plant
    v_cl = float(_RE_CL.match(lines[i_cl]).group(1)) + plant
    v_ao = float(_RE_AOA.search(lines[i_ao]).group(1)) + plant
    lines[i_cd] = f"CD: {v_cd:.11f} final: {v_cd:.11f}\n"
    lines[i_cl] = f"CL: {v_cl:.11f} final: {v_cl:.11f}\n"
    lines[i_ao] = _RE_AOA.sub(f"AoA = {v_ao:.9f} degs", lines[i_ao], count=1)
    lines.append(f"CD: {v_cd:.11f} final: {v_cd:.11f}\n")
    lines.append(f"CL: {v_cl:.11f} final: {v_cl:.11f}\n")
    return "".join(lines)


def _close(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


def birth_register(real_log: str = None):
    """Rule 3 / VERIFICATION_CHARTER section 2j. REFUSES (exit 2) on any reader
    that cannot be shown able to see its plant.

    LIMB 1 reads REAL PRODUCER BYTES and asserts the clean reading reproduces the
    parent's published values, then plants into those same bytes.
    LIMB 2 (in --selftest) blinds each reader in turn and requires the register
    to refuse -- a register never shown able to REFUSE is not evidence either.
    """
    path = real_log or REAL_LOG
    if not os.path.exists(path):
        raise Refuse(
            f"REFUSED: the required retained producer artifact is absent: {path!r}. "
            "LIMB 1 of the birth register reads REAL producer bytes; without them "
            "this instrument has NOT answered rule 3's question and does not grade. "
            "It is not skipped and it is not downgraded to a fixture.")
    with open(path, errors="replace") as fh:
        clean_text = fh.read()

    # Anchor: the clean reading of real bytes must reproduce the parent's own
    # published section R1 values. A reader that drifts off them is not reading
    # what the parent read, whatever its plant says.
    anchors = [
        ("read_cd", read_cd(clean_text), PARENT_L1_CD),
        ("read_cl", read_cl(clean_text), PARENT_L1_CL),
        ("read_aoa", read_aoa(clean_text), PARENT_L1_AOA),
        ("read_cd_series", len(read_cd_series(clean_text)), PARENT_L1_NSAMPLES),
    ]
    for name, got, want in anchors:
        if not _close(got, want, 1e-9):
            raise Refuse(
                f"REFUSED: anchor mismatch on {name!r} against the parent's "
                f"published L1 value: read {got!r}, parent published {want!r}. "
                "The reader is not reading what the parent read.")

    planted_text = plant_into_log(clean_text)

    born, register = [], []

    def witness(name, zero_passes_a_gate, clean_in, planted_in, reader, expect,
                producer, predicate=None):
        """`expect` is the exact planted reading where one exists. Where the
        planted reading is a FUNCTION of the real bytes and not a constant --
        read_iter_delta's swing is the plant PLUS whatever swing the real series
        already carries -- `predicate` states the falsifiable condition instead.
        The control never recomputes what the reader computes; it only says what
        must be true of the reader's own answer."""
        clean = reader(clean_in)
        seen = reader(planted_in)
        if predicate is None:
            ok = _close(seen, expect) and not _close(seen, clean)
        else:
            ok = bool(predicate(clean, seen))
        register.append({
            "reader": name,
            "a_zero_here_could_pass_a_gate": zero_passes_a_gate,
            "bytes_written_by": producer,
            "clean_reading": clean,
            "planted_value": expect,
            "reading_after_plant": seen,
            "reader_is_evidence": ok,
        })
        if not ok:
            raise Refuse(
                f"REFUSED: reader {name!r} was not shown able to see a planted "
                f"non-zero (clean={clean!r}, planted={seen!r}, expected={expect!r}). "
                "A zero from this reader is not evidence -- CLAUDE.md rule 3.")
        born.append(name)

    real = "REAL PRODUCER (DAFoam/OpenFOAM, A2-GC L1 level.log)"
    harness = "THIS HARNESS -- NOT the real producer; section 2j demonstration OWED"

    witness("read_cd", True, clean_text, planted_text, read_cd,
            PARENT_L1_CD + PLANT, real)
    witness("read_cl", True, clean_text, planted_text, read_cl,
            PARENT_L1_CL + PLANT, real)
    witness("read_aoa", True, clean_text, planted_text, read_aoa,
            PARENT_L1_AOA + PLANT, real)
    witness("read_cd_series", True, clean_text, planted_text,
            lambda t: float(len(read_cd_series(t))),
            float(PARENT_L1_NSAMPLES + 1), real)
    witness("read_cl_series", True, clean_text, planted_text,
            lambda t: float(len(read_cl_series(t))),
            float(PARENT_L1_NSAMPLES + 1), real)
    # read_iter_delta is CHAINED on the real reader: the series it consumes is
    # produced by read_cd_series from the real bytes, planted and clean.
    # The planted swing is the plant PLUS the swing the real series already
    # carries (3.8385e-07 over the last 13 of 66 samples, per the parent's
    # section R4), so it is not a constant. The condition is stated instead:
    # the reader must see AT LEAST the plant, and must move by at least 0.9x it.
    witness("read_iter_delta", True, clean_text, planted_text,
            lambda t: read_iter_delta(read_cd_series(t)),
            f">= {PLANT:.6e} and moved by >= {0.9 * PLANT:.6e}", real,
            predicate=lambda clean, seen: (seen >= PLANT
                                           and (seen - clean) >= 0.9 * PLANT))
    witness("read_trim_record", True,
            json.dumps({"n_evaluations": 0, "converged": False, "alpha_star": 0.0}),
            json.dumps({"n_evaluations": 4, "converged": True,
                        "alpha_star": PARENT_L1_AOA}),
            lambda t: read_trim_record(t)["alpha_star"], PARENT_L1_AOA, harness)

    return {
        "plant": PLANT,
        "real_producer_artifact": path,
        "real_producer_artifact_bytes": len(clean_text),
        "readers_declared": 7,
        "readers_born": len(born),
        "zero_passing_readers": sum(
            1 for r in register if r["a_zero_here_could_pass_a_gate"]),
        "readers_on_real_producer_bytes": sum(
            1 for r in register if r["bytes_written_by"] == real),
        "section_2j_demonstration_owed": [
            r["reader"] for r in register if r["bytes_written_by"] == harness],
        "witnesses": register,
        "all_born": len(born) == 7,
    }


def preflight(real_log: str = None):
    """Called by the driver block BEFORE the first trim evaluation. Rule 3 is a
    PRECONDITION of grading, not a property acquired later."""
    return birth_register(real_log)


# ---------------------------------------------------------------------------
# THE SECANT. Pure: it takes an `evaluate(alpha_deg) -> CL` callable, so the
# whole loop including every guard is exercised without a solver.
# ---------------------------------------------------------------------------
def secant_next(a_prev, cl_prev, a_cur, cl_cur, target=CL_TARGET):
    """One secant update. REFUSES to divide by a degenerate denominator rather
    than producing a number that means nothing (guard G-DEN)."""
    den = cl_cur - cl_prev
    if not math.isfinite(den) or abs(den) < DEN_MIN:
        raise Blocked("secant_denominator_degenerate",
                      f"|CL_k - CL_k-1| = {abs(den):.3e} < {DEN_MIN:.1e}")
    return a_cur + (target - cl_cur) * (a_cur - a_prev) / den


def _limit(a_from, a_to):
    """Apply G-STEP then G-BOUND. Returns (alpha, step_clipped, bound_clipped)."""
    step_clipped = bound_clipped = None
    d = a_to - a_from
    if abs(d) > STEP_MAX_DEG:
        a_to = a_from + math.copysign(STEP_MAX_DEG, d)
        step_clipped = STEP_MAX_DEG
    if a_to < ALPHA_MIN_DEG:
        a_to, bound_clipped = ALPHA_MIN_DEG, "min"
    elif a_to > ALPHA_MAX_DEG:
        a_to, bound_clipped = ALPHA_MAX_DEG, "max"
    return a_to, step_clipped, bound_clipped


def run_trim(evaluate, target=CL_TARGET, tol=TRIM_TOL, n_max=N_SECANT_MAX,
             alpha0=ALPHA0_DEG, a_seed=A_SEED_PER_DEG):
    """Primal-only secant trim on incidence.

    `evaluate(alpha_deg) -> CL` is one primal. Returns the trim record. Every
    non-convergent exit is a LABEL with a reason -- never an estimate and never
    an interpolation (pre-registration section 4.1).
    """
    rec = {
        "_what": "A2-GC-P primal-only secant trim on incidence at fixed CL.",
        "target_CL": target, "trim_tol": tol, "n_max": n_max,
        "alpha0_deg": alpha0, "a_seed_per_deg": a_seed,
        "_a_seed_note": "SEED ONLY: places evaluation 2. Never a reported lift "
                        "slope; never enters a graded number.",
        "evaluations": [], "clips": [],
        "converged": False, "alpha_star": None, "cl_star": None,
        "n_evaluations": 0, "blocked": None,
    }
    prev_bound_clip = None
    a_prev = cl_prev = None
    a = float(alpha0)

    for k in range(1, n_max + 1):
        cl = float(evaluate(a))
        rec["n_evaluations"] = k
        rec["evaluations"].append({"k": k, "alpha_deg": a, "CL": cl})
        if not (math.isfinite(a) and math.isfinite(cl)):
            rec["blocked"] = {"reason": "non_finite",
                              "detail": f"alpha={a!r}, CL={cl!r}"}
            return rec
        if abs(cl - target) <= tol:
            rec.update(converged=True, alpha_star=a, cl_star=cl)
            return rec
        if k == n_max:
            break

        try:
            if k == 1:
                if abs(a_seed) < DEN_MIN:
                    raise Blocked("secant_denominator_degenerate",
                                  "A_SEED is zero")
                a_next = a + (target - cl) / a_seed
            else:
                a_next = secant_next(a_prev, cl_prev, a, cl, target)
        except Blocked as b:
            rec["blocked"] = {"reason": b.reason, "detail": b.detail}
            return rec

        a_lim, step_clip, bound_clip = _limit(a, a_next)
        if step_clip is not None or bound_clip is not None:
            rec["clips"].append({"k": k, "alpha_unclipped_deg": a_next,
                                 "alpha_deg": a_lim,
                                 "step_clipped_to_deg": step_clip,
                                 "bound_clipped": bound_clip})
        # G-BOUND fires on EITHER limb. The second limb was added because the
        # first alone does not reach the case that motivates the guard: once
        # incidence is pinned AT a bound, the next update is clipped back to the
        # same value, the following evaluation returns the SAME CL, and G-DEN
        # then fires on a zero denominator -- a truthful label, but the WRONG
        # one, because the trim did not stall on a degenerate secant, it ran out
        # of incidence. Measured on the G-BOUND suite before this line existed.
        if bound_clip is not None and (a_lim == a or bound_clip == prev_bound_clip):
            rec["blocked"] = {
                "reason": "alpha_bound",
                "detail": (f"clipped to the {bound_clip} bound with no movement "
                           f"left" if a_lim == a else
                           f"two consecutive clips at the {bound_clip} bound")
                          + f" ({ALPHA_MIN_DEG} to {ALPHA_MAX_DEG} deg)"}
            return rec
        prev_bound_clip = bound_clip

        a_prev, cl_prev = a, cl
        a = a_lim

    rec["blocked"] = {
        "reason": "trim_cap",
        "detail": f"{n_max} primal evaluations reached without "
                  f"|CL - {target}| <= {tol:.1e}. The level is BLOCKED. The trim "
                  f"is NEVER estimated and NEVER interpolated."}
    return rec


# ---------------------------------------------------------------------------
# SELFTEST. Runs BEFORE any solver, by construction: nothing above imports a
# solver package.
# ---------------------------------------------------------------------------
def _counted(fn):
    box = {"n": 0}

    def wrapped(a):
        box["n"] += 1
        return fn(a)
    wrapped.calls = box
    return wrapped


def _selftest_secant():
    failures = []

    def check(name, cond, detail=""):
        if not cond:
            failures.append(f"{name}: {detail}")

    # 1. exact linear model -- the root is reachable in two evaluations.
    lin = _counted(lambda a: 0.10 * (a - 0.5))
    r = run_trim(lin)
    check("linear/converged", r["converged"], json.dumps(r["blocked"]))
    check("linear/root", r["converged"] and abs(r["alpha_star"] - 5.5) < 1e-9,
          f"alpha*={r['alpha_star']!r}")

    # 2. ANCHORED to the parent's own measured L1 point: a model whose root IS
    #    4.326120747 deg. The trim must recover it.
    anch = _counted(lambda a: 0.5 + 0.10 * (a - PARENT_L1_AOA))
    r = run_trim(anch)
    check("anchor/converged", r["converged"], json.dumps(r["blocked"]))
    check("anchor/alpha", r["converged"]
          and abs(r["alpha_star"] - PARENT_L1_AOA) < 1e-9,
          f"alpha*={r['alpha_star']!r} vs {PARENT_L1_AOA}")
    check("anchor/tol", r["converged"] and abs(r["cl_star"] - CL_TARGET) <= TRIM_TOL,
          f"CL*={r['cl_star']!r}")

    # 3. nonlinear -- must still land inside TRIM_TOL within N_SECANT_MAX.
    nl = _counted(lambda a: 0.5 + 0.10 * (a - PARENT_L1_AOA)
                  - 0.004 * (a - PARENT_L1_AOA) ** 2)
    r = run_trim(nl)
    check("nonlinear/converged", r["converged"], json.dumps(r["blocked"]))
    check("nonlinear/tol",
          r["converged"] and abs(r["cl_star"] - CL_TARGET) <= TRIM_TOL,
          f"CL*={r['cl_star']!r}")
    check("nonlinear/budget", nl.calls["n"] <= N_SECANT_MAX,
          f"{nl.calls['n']} evaluations")

    # 4. G-DEN -- a CL that does not respond. We must REFUSE to divide.
    r = run_trim(lambda a: 0.2)
    check("G-DEN/blocked", r["blocked"] is not None
          and r["blocked"]["reason"] == "secant_denominator_degenerate",
          json.dumps(r["blocked"]))
    check("G-DEN/no_value", r["alpha_star"] is None, f"alpha*={r['alpha_star']!r}")

    # 5. G-BOUND -- a target unreachable inside [0, 10] deg.
    r = run_trim(lambda a: 0.02 * a)
    check("G-BOUND/blocked", r["blocked"] is not None
          and r["blocked"]["reason"] == "alpha_bound", json.dumps(r["blocked"]))
    check("G-BOUND/no_value", r["alpha_star"] is None, f"alpha*={r['alpha_star']!r}")

    # 6. G-STEP -- the limiter fires and is RECORDED, and it is not a failure.
    shallow = _counted(lambda a: 0.5 + 0.02 * (a - 9.5))
    r = run_trim(shallow)
    check("G-STEP/recorded", len(r["clips"]) > 0, "no clip recorded")
    check("G-STEP/still_converges", r["converged"], json.dumps(r["blocked"]))

    # 7. G-CAP -- the evaluation budget runs out. BLOCKED, never estimated.
    r = run_trim(shallow, n_max=3)
    check("G-CAP/blocked", r["blocked"] is not None
          and r["blocked"]["reason"] == "trim_cap", json.dumps(r["blocked"]))
    check("G-CAP/no_value", r["alpha_star"] is None, f"alpha*={r['alpha_star']!r}")
    check("G-CAP/budget_respected", r["n_evaluations"] == 3,
          f"{r['n_evaluations']} evaluations")

    # 8. G-NAN.
    r = run_trim(lambda a: float("nan"))
    check("G-NAN/blocked", r["blocked"] is not None
          and r["blocked"]["reason"] == "non_finite", json.dumps(r["blocked"]))

    # 9. THE TRIVIAL BASELINE (VERIFICATION_CHARTER section 2c / DAFOAM_CHARTER
    #    section 4): a trim that never moves incidence. It must NOT converge on
    #    the anchored model -- if it did, the trim would not be measuring the
    #    trim.
    r = run_trim(anch, n_max=1)
    check("trivial_baseline/does_not_converge", not r["converged"],
          "a one-evaluation no-move trim converged on the anchored model, so "
          "convergence is not evidence that the secant did anything")

    return failures


def _selftest_readers():
    """LIMB 1 then LIMB 2. Returns (register, failures)."""
    failures = []
    reg = birth_register()

    # LIMB 2 -- THE CONTROL ON THE CONTROL. Blind each reader in turn to a
    # zero-returning stub; the register MUST refuse on that reader, every time,
    # through the real code path.
    g = globals()
    names = ["read_cd", "read_cl", "read_aoa", "read_cd_series",
             "read_cl_series", "read_iter_delta", "read_trim_record"]
    # Blinding a SERIES reader also blinds every reader derived from it, and the
    # register then refuses naming the DERIVED reader -- which is a correct
    # refusal, not a miss. The dependency is declared here rather than papered
    # over by accepting any refusal at all, which would weaken LIMB 2 to
    # "something went wrong somewhere".
    consumers = {
        "read_cd_series": {"read_cd_series", "read_cd", "read_iter_delta"},
        "read_cl_series": {"read_cl_series", "read_cl"},
    }
    caught = []
    for name in names:
        realfn = g[name]
        if name.endswith("_series"):
            g[name] = lambda *_a, **_k: []
        elif name == "read_trim_record":
            g[name] = lambda *_a, **_k: {"n_evaluations": 0, "converged": False,
                                         "alpha_star": 0.0}
        else:
            g[name] = lambda *_a, **_k: 0.0
        try:
            birth_register()
        except Refuse as exc:
            if any(n in str(exc) for n in consumers.get(name, {name})):
                caught.append(name)
        except Exception:
            pass
        finally:
            g[name] = realfn
    missed = sorted(set(names) - set(caught))
    if missed:
        failures.append(f"blinding {missed} did NOT make the register refuse")

    # The absent-artifact path must REFUSE, not skip.
    try:
        birth_register(real_log="/nonexistent/a2gcp/limb1/level.log")
        failures.append("an absent producer artifact did NOT make the register "
                        "refuse; a skipped LIMB 1 is not a control")
    except Refuse:
        pass

    return reg, failures, len(caught), len(names)


def main(argv):
    if "--selftest" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        reg, rfail, caught, total = _selftest_readers()
    except Refuse as e:
        print(str(e), file=sys.stderr)
        return 2
    sfail = _selftest_secant()
    failures = rfail + sfail
    print(json.dumps(reg, indent=1))
    if failures:
        for f in failures:
            print(f"SELFTEST FAILURE: {f}", file=sys.stderr)
        return 2
    print(f"BIRTH REGISTER: {reg['readers_born']}/{reg['readers_declared']} born, "
          f"{reg['zero_passing_readers']} zero-passing, "
          f"{reg['readers_on_real_producer_bytes']} on REAL producer bytes "
          f"({reg['real_producer_artifact_bytes']} bytes, "
          f"{reg['real_producer_artifact']}).")
    print(f"REFUSAL PATH DEMONSTRATED: blinding each of the {total} readers in "
          f"turn made the register refuse, {caught}/{total}; and an absent "
          f"producer artifact refuses rather than skipping.")
    print(f"SECTION 2j DEMONSTRATION OWED for: "
          f"{reg['section_2j_demonstration_owed']} -- these have no real "
          f"producer bytes on this box yet. L2 and L3 may not be graded until "
          f"the register is re-run against L1's own emitted trim_record.json.")
    print("SECANT SUITES: 9 suites passed, including the four BLOCKED guard "
          "paths (G-DEN, G-BOUND, G-CAP, G-NAN), the G-STEP limiter, the "
          "anchored recovery of the parent's measured 4.326120747 deg, and the "
          "registered trivial baseline.")
    print("NO SOLVER RAN.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
