#!/usr/bin/env python3
"""Curriculum D6RF10 -- THE GRADING PATH for the A2-wing convergence probe
`P_conv`, the OUTER-LOOP-CONVERGENCE successor to D6RF7 (NOT A RESULT /
G-CONV GATE FAIL).

PERMISSION = NOT_FROZEN.  This is a lane's prediction-first DRAFT instrument.
Nothing here is a registration until the dafoam-supervisor freezes
`PREREGISTRATION.md` by sha (CLAUDE.md rule 2), after the supervisor's
non-delegable check-1 (the DELTAS diff beside this file). The freeze, the
per-rung pin fixpoints and the enqueue belong to the supervisor and are NOT
taken here. `python d6rf10_grade.py --drive` runs the planted-zero control and
the selftest at ZERO compute and is the only thing this file does before freeze.

DERIVED FROM `curriculum_D6RF7/d6rf7_grade.py`
(md5 `d6547afe3a5420fa2e7de6e1ee38605d`, re-hashed on disk before this file was
written).  The DELTAS are enumerated in `d6rf10_grade.py_DELTAS_from_d6rf7.diff`
beside this file and are the supervisor's check-1 subject.

WHAT IS INHERITED VERBATIM (T25 -- no gate/threshold/floor moved):

  * THE ACCEPT FLOOR.  `d6rf10_accept_floor_control.py` is a BYTE-IDENTICAL copy
    of `d6rf7_accept_floor_control.py` (md5 `c6e63098e7afd542ea379a03eccfaf12`,
    asserted equal in `freeze_check`).  `ACCEPT_FLOOR = primalMinResTol 1e-08 x
    primalMinResTolDiff 1000 = 1.0e-05` (N-D43: the floor is the PRODUCT, never
    the tolerance alone).  It is IMPORTED, not re-declared, and it REFUSES the
    grading (exit 2) if either term has moved in EITHER direction in the arm's
    own container log.  A TIGHTENED floor refuses too: the registered value is a
    value, not an inequality.  Whether a successor may EVER register a different
    acceptance rule is ESCALATED TO SANAA AND UNRULED (N-D43, and N-D43
    CORRECTION 2026-09-06); this file does not touch that boundary.

  * G-CONV's SCORING.  Per field in `CONV_FIELDS`, per graded leg: the
    final-iteration `initRes` against `CONV_BAR = ACCEPT_FLOOR`; `PASS` iff
    `v < CONV_BAR`, else `GATE FAIL`; the p-solve is SPLIT into
    `p_first_uncorrected` (the FIRST/uncorrected solve, the BINDING field, T25)
    and `p_corrected` (the last corrected solve).  Carried from
    `d6rf7_grade.py:1928-2050` and `:367-368` unchanged in its arithmetic.

  * THE PER-LEG CONTAINER-LOG READER.  `read_legs` is carried from
    `d6rf7_grade.py:1761-1925`; its residual-line and time-block parsing, its
    rank-duplicate LEG_BEGIN collapse, and its p-first/p-corrected split are
    unchanged.

WHAT CHANGED, AND WHY (the registered DELTAS -- check-1 subject):

  D1  THE LEG DISCRIMINATOR IS `fvSolution`/`solverName`, NOT `fvSchemes`.
      D6RF7 changed the DISCRETISATION (limited 0.333) and discriminated legs
      by fvSchemes md5.  D6RF10 holds the D6RF7 LIMITED scheme FIXED and changes
      only OUTER-LOOP numerics (endTime, nNonOrthogonalCorrectors, relaxation,
      solverName SIMPLE->SIMPLEC).  So `G-SCHEME` is REPLACED by `G-CONFIG`
      (D2) and the leg's identity is the rung's fvSolution/solverName read back
      out of the run, never a staged file.

  D2  `G-CONFIG` REPLACES `G-SCHEME`.  The anti-cheat gate: the graded leg must
      show the RUNG'S registered outer-loop config -- `solverName`,
      `nNonOrthogonalCorrectors` (read from the RUN by counting the per-corrector
      p-solves in the final outer iteration = count - 1), the p/equations
      relaxation factors, and `endTime` -- read back out of the arm's own
      container log.  A leg that ran a different config is `NOT A RESULT`, never
      `GATE FAIL` (CLAUDE.md rule 5, strictly restrictive).  The accept floor is
      verified UNMOVED (afc); CD/CL are REPORTED (SIMPLE and SIMPLEC converge to
      the SAME discrete fixed point, so no CD/CL shift is expected and none is
      gated -- unlike D6RF7, where the limited scheme deliberately shifted them).

  D3  `CONV_MEASURED_D6RF7` REPLACES `CONV_MEASURED_D6RF4` as the printed
      baseline (D6RF7's OWN measured final-iteration initRes: p_first_uncorrected
      `1.625570732e-05`, nuTilda `1.408231801e-05`).  Every graded row prints its
      improvement vs this baseline so the record states whether a rung MOVED the
      binding residual.

  D4  THE F5-EQUIVALENT CONTROL LEG is D6RF7's FROZEN config (LIMITED scheme,
      nNonOrthogonalCorrectors 3, DARhoSimpleFoam, endTime 1000), which is
      MEASURED to give `p_first_uncorrected 1.625570732e-05` = 1.626x the bar ->
      GATE FAIL.  Running it beside each rung proves any rung PASS is due to the
      rung's outer-loop change and not a gate defect: a PASS on the D6RF7 control
      would WITHDRAW the rung's verdict (section 6 withdrawal clause).

  D5  THE FD / CD / off-design / price gates of D6RF7 are DROPPED, not silenced:
      this is a single-arm convergence probe (as D6RF3->D6RF7). It buys no
      F_mp/REF_off arm; those gates would read want-of-input, so carrying their
      machinery adds no information. The SHIPPED multipoint row stays NAMED and
      priced (PREREGISTRATION.md section 6), not bought here.

VOCABULARY: `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` and no
other word (CLAUDE.md rule 1). `GATE REACHED` is DELIBERATELY ABSENT -- this item
runs no optimiser.

THE PLANTED-ZERO CONTROL (CLAUDE.md rule 3) is not decoration: `run_residual_
plant_control` plants a known initRes into a COPY of a log, reads it back FROM
DISK through the SAME `read_legs` the gate calls, and REFUSES if the reader
cannot see it -- and asserts the original is byte-unchanged. A zero from a reader
not shown able to see a non-zero is not evidence.

NO `assert` STATEMENT APPEARS IN THIS FILE (`python -O` deletes them).
REFUSES RATHER THAN DEGRADES (exit 2), as this family's comparators do.
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile

# ============================ REGISTERED CONSTANTS ==========================
# Every value in this block is frozen by PREREGISTRATION.md before compute.
ITEM = "D6RF10"
RANKS = 4

# ---- the ordered outer-loop-convergence ladder (PREREGISTRATION.md section 3)
# Each rung changes OUTER-LOOP NUMERICS ONLY: never the mesh, the geometry, the
# objective/constraint, the fvSchemes discretisation, or the accept floor. The
# chain runs rungs IN ORDER and STOPS at the first rung whose graded leg drives
# p_first_uncorrected < CONV_BAR (STOPPED_AT_FIRST_PASS). If all rungs are
# MEASURED and none passes, the item records a CAPABILITY FINDING -- MEASURED,
# never inferred -- and the escalated N-D43 acceptance-rule question is re-opened
# for Sanaa (not decided here).
RUNGS = ("R1", "R2", "R3", "R4")
RUNG_CONFIG = {
    # solverName, nNonOrthogonalCorrectors, p relaxation, eqn relaxation, endTime
    "R1": {"solverName": "DARhoSimpleFoam", "nNonOrth": 3,
           "relax_p": 0.30, "relax_eqn": 0.70, "endTime": 2500,
           "role": "extended outer horizon at the D6RF7 config -- the cheapest "
                   "rung, and the MEASURED control on the run-longer lever"},
    "R2": {"solverName": "DARhoSimpleFoam", "nNonOrth": 12,
           "relax_p": 0.30, "relax_eqn": 0.70, "endTime": 300,
           "role": "deep non-orthogonal corrector loop -- iterate the LAGGED "
                   "deferred-correction term (the named binding mechanism) to "
                   "within-iteration convergence; un-tried above 3 correctors"},
    "R3": {"solverName": "DARhoSimpleCFoam", "nNonOrth": 12,
           "relax_p": 0.70, "relax_eqn": 0.70, "endTime": 2000,
           "role": "SIMPLEC (consistent) pressure-velocity coupling; converges "
                   "to the SAME fixed point so CD/CL shift is predicted ~0 and "
                   "REPORTED not gated"},
    "R4": {"solverName": "DARhoSimpleCFoam", "nNonOrth": 12,
           "relax_p": 0.15, "relax_eqn": 0.50, "endTime": 4000,
           "role": "heavy under-relaxation fallback -- damp the outer loop onto "
                   "a lower plateau if the floor is a weak limit cycle"},
}
# The D6RF7 FROZEN config, run beside each rung as the known-fail control (D4).
CONTROL_CONFIG = {"solverName": "DARhoSimpleFoam", "nNonOrth": 3,
                  "relax_p": 0.30, "relax_eqn": 0.70, "endTime": 1000}
CONTROL_MEASURED_P_FIRST = 1.625570732e-05   # D6RF7 L1, GATE FAIL at 1.626x

# ---- G-CONV: the fields and the bar (INHERITED VERBATIM, T25) --------------
# Carried BYTE-FOR-VALUE from d6rf7_grade.py:367-368. The p-solve is SPLIT: the
# FIRST (uncorrected) solve is the BINDING field; the corrected final solve is
# under floor and is not the convergence measure.
CONV_FIELDS = ("U0", "U1", "U2", "he", "p_first_uncorrected",
               "p_corrected", "nuTilda")
# D6RF7's OWN measured final-iteration initRes (D3). The binding field and the
# genuine second over-floor field, from d6rf7 RESULTS.md section 2 / the frozen
# verdict json.
CONV_MEASURED_D6RF7 = {
    "U0": 2.050400149e-07, "U1": 7.782685238e-07, "U2": 5.580946633e-08,
    "he": 9.791852881e-09,
    "p_first_uncorrected": 1.625570732e-05,   # BINDING, 1.626x the floor
    "p_corrected": 6.4090e-08,                # corrected final p-solve, << floor
    "nuTilda": 1.408231801e-05,               # second over-floor field, 1.408x
}
BINDING_FIELD = "p_first_uncorrected"
PRIMAL_FAILURE_BANNER = "Primal solution failed!"

# leg markers (INHERITED VERBATIM from d6rf7_grade.py:414-416)
LEG_BEGIN = "D6RF10_LEG_BEGIN"
LEG_END = "D6RF10_LEG_END"
# D6RF10's install marker echoes the OUTER-LOOP config, not an fvSchemes md5 (D1).
CONFIG_INSTALL_MARKER = "D6RF10_CONFIG_INSTALLED"

PLANT_INITRES = 1.234e-03            # the planted-zero perturbation, registered
PLANT_REL_TOL = 1.0e-9
# G-CONFIG numeric-identity tolerance (A6 fix): the config-install marker's
# numeric fields are compared to the registered values within this ABS tol, so a
# formatting variant (`0.30` vs `0.3`) is identity and a genuine difference
# (`0.15` vs `0.30`, ~0.15 apart) is not. Tight enough that no two registered
# rung values (min gap 0.15 in relax, 500 in endTime) collide.
CONFIG_NUM_ABSTOL = 1.0e-9

# ---- A2 PLATEAU GATE (AMENDMENT A2, 2026-09-09 / S-144 / commit c2a6e318) --
# FROZEN pre-compute in PREREGISTRATION.md AMENDMENT A2 (lines 405-414). A
# strictly-more-restrictive layer on a would-be-PASS (below-floor) rung: a
# convergence PASS is a claim about the PLATEAU, not one sub-floor sample taken
# while the binding residual is still descending (CLAUDE.md rule 5). Over the
# LATE_WINDOW of outer-iterations (inclusive), read >= MIN_PLATEAU_SAMPLES
# FIRST-UNCORRECTED `p initRes:` samples from the solver log; the relative
# spread (max - min) / mean must be <= PLATEAU_SPREAD_MAX. The 0.31% ceiling
# bounds R1's MEASURED 0.307% plateau signature (the campaign's own bar). This
# layer can ONLY turn a would-be PASS into NOT A RESULT -- it never manufactures
# a PASS and never softens a GATE FAIL (rule-5 direction, preserved by the
# MORE-restrictive fold in gate_conv). It touches NO gate / floor / cap / field.
LATE_WINDOW = (1500, 2000)      # outer-iterations, inclusive (AMENDMENT A2)
MIN_PLATEAU_SAMPLES = 5         # < 5 in-window samples -> NOT A RESULT
PLATEAU_SPREAD_MAX = 0.0031     # 0.31% relative-spread ceiling (R1's 0.307%)

# freeze pins (PLACEHOLDER until the supervisor freezes -- rule 2). The grader
# verifies its own bytes == the committed blob at HEAD at execution AFTER freeze.
D6RF7_GRADE_MD5 = "d6547afe3a5420fa2e7de6e1ee38605d"
D6RF7_ACCEPT_FLOOR_MD5 = "c6e63098e7afd542ea379a03eccfaf12"

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# THE ONE ACCEPT-FLOOR READER OF THIS ITEM (imported, not re-implemented, so
# this file and the instrument that refuses on drift cannot disagree). Its
# md5 is asserted equal to D6RF7's in freeze_check (T25).
import d6rf10_accept_floor_control as afc                           # noqa: E402
ACCEPT_FLOOR = afc.ACCEPT_FLOOR                                    # 1.0e-05
CONV_BAR = ACCEPT_FLOOR


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail},
                             sort_keys=True, default=str)[:4000])


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def _f(x):
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x)
        except ValueError:
            refuse("float_parse", {"value": x[:120]})
    refuse("float_parse", {"type": type(x).__name__})


class NonFinite(Exception):
    def __init__(self, artefact, key, token):
        self.detail = {"reason": "NON_FINITE_INPUT", "artefact": artefact,
                       "key": key, "token_as_read": token}
        Exception.__init__(self, json.dumps(self.detail, sort_keys=True,
                                            default=str))


def _ff(x, artefact, key):
    """Section 3f reader (INHERITED). Strictly restrictive: a non-finite value
    can only turn a PASS or GATE FAIL INTO a NOT A RESULT, never the reverse."""
    v = _f(x)
    if not math.isfinite(v):
        raise NonFinite(artefact, key, repr(x) if isinstance(x, str) else v)
    return v


# ============ THE PER-LEG CONTAINER-LOG READER (INHERITED, D1 delta) ========
_RES_LINE = re.compile(
    r'^(?P<f>\S+) initRes: (?P<i>\S+) finalRes: (?P<r>\S+) nIters: (?P<n>\d+)\s*$')
_TIME_LINE = re.compile(r'^Time = (?P<t>\d+)\s*$')


def read_legs(log_path):
    """Split ONE container log into the rung's legs and read each leg's OWN
    final-iteration per-field `initRes`. Carried from d6rf7_grade.py:1761 with
    ONE delta (D1): the install marker echoes the OUTER-LOOP config, not an
    fvSchemes md5, and legs are bound by the `leg=` tag the producer prints.

    FAILS CLOSED: a leg with no LEG_BEGIN is BAR_NOT_PRODUCED; a leg with a
    begin and no residual block is SEGMENT_WITHOUT_RESIDUALS. Neither is a pass.
    """
    out = {"log": log_path, "segments": {}, "order": [], "markers_seen": 0}
    if not log_path or not os.path.isfile(log_path):
        out["state"] = "BAR_NOT_PRODUCED"
        out["why"] = ("the arm's container log is not on disk; UNMEASURED, "
                      "never a pass.")
        return out
    cur, segs, installs = None, [], []
    with open(log_path, errors="replace") as fh:
        for ln, line in enumerate(fh, 1):
            s = line.rstrip("\n")
            if s.startswith(CONFIG_INSTALL_MARKER):
                kv = dict(x.split("=", 1) for x in s.split()[1:] if "=" in x)
                kv["line"] = ln
                installs.append(kv)
                continue
            if s.startswith(LEG_BEGIN):
                parts = s.split()
                tag = parts[1] if len(parts) > 1 else None
                mode = next((x.split("=", 1)[1] for x in parts
                             if x.startswith("mode=")), None)
                # collapse rank-duplicate LEG_BEGIN markers (INHERITED)
                if (cur is not None and cur.get("tag") == tag
                        and cur.get("mode") == mode
                        and not cur["times"] and not cur["fields"]):
                    cur.setdefault("rank_duplicate_begins", 1)
                    cur["rank_duplicate_begins"] += 1
                    out["markers_seen"] += 1
                    continue
                cur = {"tag": tag, "mode": mode, "begin_line": ln,
                       "end_line": None, "times": [], "fields": {},
                       "n_p_solves": 0, "CD": None, "CL": None,
                       "primal_failed": None}
                segs.append(cur)
                out["markers_seen"] += 1
                continue
            if s.startswith(LEG_END):
                out["markers_seen"] += 1
                if cur is not None:
                    cur["end_line"] = ln
                    cur = None
                continue
            if cur is None:
                continue
            m = _TIME_LINE.match(s)
            if m:
                cur["times"].append(int(m.group("t")))
                cur["fields"] = {}          # the LAST time block is graded
                cur["n_p_solves"] = 0
                continue
            m = _RES_LINE.match(s)
            if m:
                f = m.group("f")
                rec = {"initRes": m.group("i"), "finalRes": m.group("r"),
                       "nIters": int(m.group("n")), "line": ln}
                if f == "p":
                    # p is solved (1 + nNonOrthogonalCorrectors) times per outer
                    # iteration; the FIRST is p_first_uncorrected, the LAST
                    # overwrites p_corrected, and the count gives nNonOrth back.
                    if "p_first_uncorrected" not in cur["fields"]:
                        cur["fields"]["p_first_uncorrected"] = rec
                    cur["fields"]["p_corrected"] = rec
                    cur["n_p_solves"] = cur.get("n_p_solves", 0) + 1
                else:
                    cur["fields"][f] = rec
                continue
            if PRIMAL_FAILURE_BANNER in s:
                cur["primal_failed"] = True
    # bind segments to legs by the tag the producer printed, in order
    for seg in segs:
        leg = seg.get("tag")
        seg["leg"] = leg
        seg["final_time"] = seg["times"][-1] if seg["times"] else None
        # nNonOrthogonalCorrectors read back FROM THE RUN = p-solves - 1
        seg["nNonOrth_read_from_run"] = (seg["n_p_solves"] - 1
                                         if seg["n_p_solves"] else None)
        seg["state"] = "READ" if seg["fields"] else "SEGMENT_WITHOUT_RESIDUALS"
        if leg is not None:
            out["segments"][leg] = seg
            out["order"].append(leg)
    out["config_installs"] = installs
    out["n_segments"] = len(segs)
    out["state"] = "BAR_PRODUCED" if out["segments"] else "BAR_NOT_PRODUCED"
    return out


# ===== A2 PLATEAU: the late-window first-uncorrected series reader ==========
def read_late_window_p_first(log_path, leg, window=LATE_WINDOW):
    """Read the FIRST-UNCORRECTED `p initRes:` of each outer iteration whose
    `Time` falls in the INCLUSIVE `window`, within the graded `leg`. Uses the
    SAME first-p rule read_legs uses (the FIRST p-solve of an outer iteration is
    p_first_uncorrected; later p-solves are correctors and are ignored here).
    Returns the ordered in-window samples + their times.

    Leg scoping mirrors read_legs: samples are collected only between this leg's
    LEG_BEGIN and its LEG_END. Rank-duplicate LEG_BEGIN markers are harmless (a
    repeated begin for the same leg just re-affirms in_leg). If the log carries
    NO LEG_BEGIN marker AT ALL (e.g. a bare smoke log), the whole file is treated
    as the leg so the reader still extracts samples rather than silently seeing
    nothing. FAILS CLOSED: a missing log yields no samples -> the gate reads
    NOT A RESULT (insufficient plateau evidence), never a pass."""
    lo, hi = window
    out = {"log": log_path, "leg": leg, "window": [lo, hi],
           "samples": [], "times": []}
    if not log_path or not os.path.isfile(log_path):
        out["state"] = "BAR_NOT_PRODUCED"
        return out
    with open(log_path, errors="replace") as fh:
        lines = fh.read().splitlines()
    has_markers = any(x.startswith(LEG_BEGIN) for x in lines)
    default_in = not has_markers          # no markers -> whole file is the leg
    in_leg = default_in
    cur_time = None
    got_first_p = False
    for s in lines:
        if s.startswith(LEG_BEGIN):
            parts = s.split()
            tag = parts[1] if len(parts) > 1 else None
            in_leg = (tag == leg)
            cur_time = None
            got_first_p = False
            continue
        if s.startswith(LEG_END):
            in_leg = default_in
            cur_time = None
            got_first_p = False
            continue
        if not in_leg:
            continue
        m = _TIME_LINE.match(s)
        if m:
            cur_time = int(m.group("t"))
            got_first_p = False
            continue
        m = _RES_LINE.match(s)
        if m and m.group("f") == "p" and cur_time is not None:
            if not got_first_p:                     # the FIRST p-solve only
                got_first_p = True
                if lo <= cur_time <= hi:
                    out["samples"].append(_f(m.group("i")))
                    out["times"].append(cur_time)
    out["state"] = "READ"
    return out


# ============ G-CONFIG: the anti-cheat on the OUTER-LOOP config (D2) =========
def gate_config(seg, rung):
    """The graded leg must show the RUNG'S registered outer-loop config, read
    back out of the run. NOT A RESULT (never GATE FAIL) if it does not: a leg
    that ran a different config did not measure this rung."""
    want = RUNG_CONFIG[rung] if rung in RUNG_CONFIG else CONTROL_CONFIG
    inst = None
    for kv in seg.get("_config_installs", []):
        if kv.get("leg") == seg.get("leg"):
            inst = kv
    read = {"nNonOrth_from_p_solve_count": seg.get("nNonOrth_read_from_run"),
            "final_time": seg.get("final_time"),
            "config_install_marker": inst}
    ok = True
    reasons = []
    if seg.get("nNonOrth_read_from_run") != want["nNonOrth"]:
        ok = False
        reasons.append("nNonOrthogonalCorrectors read %r != registered %d"
                       % (seg.get("nNonOrth_read_from_run"), want["nNonOrth"]))
    if inst is None:
        ok = False
        reasons.append("CONFIG_INSTALL_MARKER not produced for this leg")
    else:
        # A6 FIX (2026-09-08). solverName stays an EXACT string compare; the
        # numeric config fields (relax_p, relax_eqn, endTime) are compared
        # NUMERICALLY within CONFIG_NUM_ABSTOL, so a producer echoing `relax_p=
        # 0.30` no longer fails against `str(0.30)="0.3"` and turns a GENUINE
        # leg NOT A RESULT (the defect). A genuinely-DIFFERENT config (e.g. 0.15
        # vs 0.30) STILL fails; an unparseable numeric token STILL fails. This
        # gate only turns PASS/GATE FAIL -> NOT A RESULT, never the reverse, so
        # a formatting-robust identity check can never yield a false PASS. The
        # accept floor, CONV_BAR, BINDING_FIELD and G-CONV scoring are untouched.
        for key in ("solverName", "relax_p", "relax_eqn", "endTime"):
            got = inst.get(key)
            if got is None:                      # partial marker: not a mismatch
                continue
            if key == "solverName":
                exp = str(want[key])
                if got != exp:
                    ok = False
                    reasons.append("solverName installed %r != registered %s"
                                   % (got, exp))
                continue
            try:
                gotf = float(got)
                wantf = float(want[key])
            except (TypeError, ValueError):
                ok = False
                reasons.append("%s installed %r is not numeric-parseable "
                               "against registered %r" % (key, got, want[key]))
                continue
            if abs(gotf - wantf) > CONFIG_NUM_ABSTOL:
                ok = False
                reasons.append("%s installed %r (%.12g) != registered %r (%.12g)"
                               % (key, got, gotf, want[key], wantf))
    return {"config_as_registered": ok, "read": read,
            "registered": want, "reasons": reasons}


# ================= A2 PLATEAU GATE (AMENDMENT A2) ==========================
# Severity ordering for the strictly-restrictive fold. NOT A RESULT is the most
# restrictive; a fold that takes the MORE restrictive of two verdicts can only
# move a verdict UP this scale, never down -- so the plateau layer can never
# manufacture a PASS nor soften a GATE FAIL (CLAUDE.md rule 5 direction).
_SEV = {"PASS": 0, "GATE FAIL": 1, "NOT A RESULT": 2}


def _more_restrictive(a, b):
    """Return whichever of a, b is the more restrictive verdict (higher _SEV).
    An unknown/None verdict is treated as maximally restrictive."""
    return a if _SEV.get(a, 2) >= _SEV.get(b, 2) else b


def gate_plateau(v_binding, samples):
    """The A2 plateau layer (AMENDMENT A2 / commit c2a6e318). `v_binding` is the
    binding field (p_first_uncorrected) final-iteration initRes; `samples` is the
    late-window FIRST-UNCORRECTED series read over LATE_WINDOW. Three-way, EXACT
    per AMENDMENT A2 (prereg lines 405-414):
      * below floor (v_binding < CONV_BAR) AND spread <= PLATEAU_SPREAD_MAX -> PASS
      * below floor but spread > PLATEAU_SPREAD_MAX (still moving)  -> NOT A RESULT
      * below floor but < MIN_PLATEAU_SAMPLES in-window samples     -> NOT A RESULT
      * v_binding >= floor (or absent/non-finite)                   -> GATE FAIL
    STRICTLY RESTRICTIVE: only ever turns a would-be PASS into NOT A RESULT; it
    never manufactures a PASS and never softens a GATE FAIL (rule 5)."""
    n = len(samples)
    out = {"gate": "A2-PLATEAU", "late_window": list(LATE_WINDOW),
           "spread_ceiling": PLATEAU_SPREAD_MAX,
           "min_samples": MIN_PLATEAU_SAMPLES, "n_samples": n,
           "v_binding": v_binding, "conv_bar": CONV_BAR,
           "provenance": ("AMENDMENT A2 (PREREGISTRATION.md lines 405-414), "
                          "commit c2a6e318; the 0.31% ceiling bounds R1's "
                          "measured 0.307% plateau signature.")}
    below_floor = (v_binding is not None and isinstance(v_binding, (int, float))
                   and math.isfinite(v_binding) and v_binding < CONV_BAR)
    out["below_floor"] = below_floor
    if not below_floor:
        # >= floor (or absent / non-finite): already GATE FAIL by the floor. The
        # plateau layer does not touch it and cannot manufacture a PASS.
        out.update({"verdict": "GATE FAIL",
                    "reason": ("binding field >= accept floor (or absent); the "
                               "plateau layer does not manufacture a PASS "
                               "(rule 5).")})
        return out
    if n < MIN_PLATEAU_SAMPLES:
        out.update({"verdict": "NOT A RESULT",
                    "reason": ("INSUFFICIENT_PLATEAU_EVIDENCE: %d first-"
                               "uncorrected samples in late window %s < "
                               "MIN_PLATEAU_SAMPLES %d; the plateau is unmeasured "
                               "so a PASS is not admissible (rule 5)."
                               % (n, list(LATE_WINDOW), MIN_PLATEAU_SAMPLES))})
        return out
    mn, mx = min(samples), max(samples)
    mean = sum(samples) / n
    if not (math.isfinite(mean) and mean > 0.0):
        out.update({"verdict": "NOT A RESULT", "mean": mean,
                    "reason": ("PLATEAU_MEAN_NONPOSITIVE: cannot form a relative "
                               "spread from the late-window samples.")})
        return out
    spread = (mx - mn) / mean
    out.update({"min": mn, "max": mx, "mean": mean, "relative_spread": spread,
                "plateaued": spread <= PLATEAU_SPREAD_MAX})
    if spread <= PLATEAU_SPREAD_MAX:
        out.update({"verdict": "PASS",
                    "reason": ("below floor AND plateaued: late-window relative "
                               "spread %.4g%% <= %.4g%%."
                               % (spread * 100.0, PLATEAU_SPREAD_MAX * 100.0))})
    else:
        out.update({"verdict": "NOT A RESULT",
                    "reason": ("NOT_PLATEAUED: below floor but late-window "
                               "relative spread %.4g%% > %.4g%% (still moving / "
                               "oscillating; not converged, rule 5)."
                               % (spread * 100.0, PLATEAU_SPREAD_MAX * 100.0))})
    return out


# ------------------------------------------------------------ G-CONV --------
def gate_conv(seg, rung):
    """G-CONV, per-field final-iteration initRes against CONV_BAR. Scoring
    INHERITED VERBATIM from d6rf7_grade.py:1997-2042 (PASS iff v < CONV_BAR).
    The subject is the rung's graded leg. STRICTLY RESTRICTIVE via _ff."""
    row = {"gate": "G-CONV_per_field_final_initRes", "bar": CONV_BAR,
           "rung": rung, "leg": seg.get("leg"),
           "final_time": seg.get("final_time"),
           "primal_failure_banner": bool(seg.get("primal_failed")),
           "bar_provenance": (
               "1.0e-05 = primalMinResTol 1e-08 x primalMinResTolDiff 1000, "
               "carried from D6RF7 UNCHANGED (N-D43: the floor is the PRODUCT). "
               "d6rf10_accept_floor_control.py refuses if it has moved."),
           "per_field": {}, "fields_absent": []}
    gc = gate_config(seg, rung)
    row["config_check"] = gc
    if not gc["config_as_registered"]:
        row.update({"verdict": "NOT A RESULT",
                    "reason": "CONFIG_NOT_AS_REGISTERED",
                    "note": "this leg's log does not show the rung's registered "
                            "outer-loop config; its residual cannot grade the "
                            "rung. NOT A RESULT, never GATE FAIL (rule 5)."})
        return row
    if seg.get("state") != "READ":
        row.update({"verdict": "NOT A RESULT", "reason": seg.get("state"),
                    "note": "the leg produced no final-iteration residual "
                            "block; nothing to grade. NOT A RESULT."})
        return row
    worst, worst_f = None, None
    for f in CONV_FIELDS:
        got = seg["fields"].get(f)
        if got is None:
            row["fields_absent"].append(f)
            row["per_field"][f] = {"initRes": None, "verdict": "NOT A RESULT",
                                   "reason": "FIELD_ABSENT_FROM_SEGMENT"}
            continue
        try:
            v = _ff(got["initRes"], os.path.basename(str(seg.get("_log"))),
                    "%s.%s.initRes" % (seg.get("leg"), f))
        except NonFinite as e:
            row["per_field"][f] = {"initRes": got["initRes"],
                                   "verdict": "NOT A RESULT",
                                   "reason": "NON_FINITE_INPUT",
                                   "non_finite": e.detail}
            continue
        row["per_field"][f] = {
            "initRes": v, "finalRes": got["finalRes"], "nIters": got["nIters"],
            "log_line": got["line"], "ratio_to_bar": v / CONV_BAR,
            "d6rf7_measured": CONV_MEASURED_D6RF7.get(f),
            "improvement_vs_d6rf7": (CONV_MEASURED_D6RF7[f] / v
                                     if f in CONV_MEASURED_D6RF7 and v > 0
                                     else None),
            "verdict": "PASS" if v < CONV_BAR else "GATE FAIL"}
        if worst is None or v > worst:
            worst, worst_f = v, f
    row["worst_field"] = worst_f
    row["worst_initRes"] = worst
    row["worst_ratio_to_bar"] = (worst / CONV_BAR) if worst is not None else None
    row["binding_field"] = BINDING_FIELD
    floor_binding_verdict = row["per_field"].get(BINDING_FIELD, {}).get("verdict")

    # ---- A2 PLATEAU LAYER (AMENDMENT A2 / commit c2a6e318) -----------------
    # Refine the BINDING field's would-be PASS with the late-window plateau test,
    # then re-aggregate. The fold takes the MORE restrictive of the floor and
    # plateau verdicts, so it can only turn a would-be PASS into NOT A RESULT --
    # never manufacture a PASS, never soften a GATE FAIL (rule-5 direction).
    bf_rec = row["per_field"].get(BINDING_FIELD, {})
    bf_iv = bf_rec.get("initRes")
    v_binding = (bf_iv if isinstance(bf_iv, (int, float)) and math.isfinite(bf_iv)
                 else None)
    lw = read_late_window_p_first(seg.get("_log"), seg.get("leg"))
    pv = gate_plateau(v_binding, lw["samples"])
    pv["late_window_read"] = {"n_samples": len(lw["samples"]),
                              "times": lw["times"], "state": lw.get("state"),
                              "log": lw.get("log")}
    row["plateau_check"] = pv
    binding_effective = _more_restrictive(floor_binding_verdict, pv["verdict"])
    if BINDING_FIELD in row["per_field"]:
        row["per_field"][BINDING_FIELD]["floor_verdict"] = floor_binding_verdict
        row["per_field"][BINDING_FIELD]["plateau_verdict"] = pv["verdict"]
        row["per_field"][BINDING_FIELD]["verdict"] = binding_effective
    row["binding_verdict"] = binding_effective

    vs = [c.get("verdict") for c in row["per_field"].values()]
    row["verdict"] = ("NOT A RESULT" if "NOT A RESULT" in vs else
                      ("PASS" if all(v == "PASS" for v in vs) else "GATE FAIL"))
    return row


# ================= THE PLANTED-ZERO CONTROL (CLAUDE.md rule 3) ==============
def _synthetic_leg_log(path, leg="R1", init_p="1.62e-05", n_p_solves=4,
                       solver="DARhoSimpleFoam", nnonorth=3, relax_p="0.3",
                       relax_eqn="0.7", endtime="2500"):
    """A minimal container log of the shape the arm writes -- built here so the
    control is drivable AT FREEZE, when no arm log exists."""
    body = ["%s leg=%s endTime=%s solverName=%s relax_p=%s relax_eqn=%s"
            % (CONFIG_INSTALL_MARKER, leg, endtime, solver, relax_p, relax_eqn),
            "%s %s mode=P_conv" % (LEG_BEGIN, leg), "", "Time = %s" % endtime, ""]
    # p solved (1 + nNonOrth) times: first = uncorrected (the planted subject)
    body.append("p initRes: %s finalRes: 6.4e-08 nIters: 40" % init_p)
    for _ in range(max(0, n_p_solves - 1)):
        body.append("p initRes: 3.0e-07 finalRes: 6.4e-08 nIters: 30")
    body += ["U0 initRes: 2.0e-07 finalRes: 1e-09 nIters: 3",
             "U1 initRes: 7.8e-07 finalRes: 1e-09 nIters: 3",
             "U2 initRes: 5.6e-08 finalRes: 1e-09 nIters: 3",
             "he initRes: 9.7e-09 finalRes: 1e-11 nIters: 2",
             "nuTilda initRes: 1.4e-05 finalRes: 1.8e-09 nIters: 6",
             "ExecutionTime = 60 s  ClockTime = 61 s", "", "End",
             "%s %s primal_raised=True" % (LEG_END, leg),
             "Finalising parallel run"]
    with open(path, "w") as fh:
        fh.write("\n".join(body) + "\n")
    return path


def _synthetic_series_log(path, leg="R1", first_p_series=None, times=None,
                          solver="DARhoSimpleFoam", nnonorth=3, relax_p="0.3",
                          relax_eqn="0.7", endtime="2500", nutilda="8.0e-06"):
    """A container log with MULTIPLE outer-iteration Time blocks so the A2
    plateau reader has a late-window series to read. `first_p_series[i]` is the
    FIRST-UNCORRECTED p initRes at `times[i]`; each block then writes `nnonorth`
    corrector p-solves (so nNonOrth read back = nnonorth). The LAST block is the
    one G-CONV grades. Built here so the A2 plateau branches are drivable AT
    FREEZE, when no arm log exists."""
    if times is None:
        times = [1500, 1600, 1700, 1800, 1900, 2000]
    if first_p_series is None:
        first_p_series = ["8.0e-06"] * len(times)
    body = ["%s leg=%s endTime=%s solverName=%s relax_p=%s relax_eqn=%s"
            % (CONFIG_INSTALL_MARKER, leg, endtime, solver, relax_p, relax_eqn),
            "%s %s mode=P_conv" % (LEG_BEGIN, leg)]
    for tt, fp in zip(times, first_p_series):
        body += ["", "Time = %s" % tt, "",
                 "p initRes: %s finalRes: 6.4e-08 nIters: 40" % fp]
        for _ in range(max(0, nnonorth)):        # nnonorth corrector p-solves
            body.append("p initRes: 3.0e-07 finalRes: 6.4e-08 nIters: 30")
        body += ["U0 initRes: 2.0e-07 finalRes: 1e-09 nIters: 3",
                 "U1 initRes: 7.8e-07 finalRes: 1e-09 nIters: 3",
                 "U2 initRes: 5.6e-08 finalRes: 1e-09 nIters: 3",
                 "he initRes: 9.7e-09 finalRes: 1e-11 nIters: 2",
                 "nuTilda initRes: %s finalRes: 1.8e-09 nIters: 6" % nutilda,
                 "ExecutionTime = %d s  ClockTime = %d s" % (tt, tt)]
    body += ["", "End", "%s %s primal_raised=True" % (LEG_END, leg),
             "Finalising parallel run"]
    with open(path, "w") as fh:
        fh.write("\n".join(body) + "\n")
    return path


def _bind(legs, leg):
    seg = legs["segments"][leg]
    seg["_config_installs"] = legs.get("config_installs", [])
    seg["_log"] = legs["log"]
    return seg


def run_residual_plant_control(ctrl_dir):
    """Plant a KNOWN initRes into a COPY of a log, read it back through the SAME
    read_legs the gate calls, and REFUSE if the reader cannot see it. Assert the
    original is byte-unchanged. Three states: EXERCISED-PASS/-FAIL/NOT EXERCISED.
    A zero from a reader not shown able to see a non-zero is not evidence."""
    os.makedirs(ctrl_dir, exist_ok=True)
    # a clean log that GATE-FAILS honestly (p_first over floor)
    clean = _synthetic_leg_log(os.path.join(ctrl_dir, "clean.log"),
                               init_p="1.62e-05")
    m0 = md5_of(clean)
    seg0 = _bind(read_legs(clean), "R1")
    baseline_first = seg0["fields"][BINDING_FIELD]["initRes"]
    # plant a DIFFERENT, PASSING value into a COPY
    planted = os.path.join(ctrl_dir, "planted.log")
    txt = open(clean, errors="replace").read()
    tok = "%.6e" % (PLANT_INITRES,)
    planted_txt = txt.replace("p initRes: 1.62e-05", "p initRes: %s" % tok, 1)
    with open(planted, "w") as fh:
        fh.write(planted_txt)
        fh.flush(); os.fsync(fh.fileno())
    seg1 = _bind(read_legs(planted), "R1")
    read_back = seg1["fields"][BINDING_FIELD]["initRes"]
    saw = abs(_f(read_back) - PLANT_INITRES) <= PLANT_REL_TOL * PLANT_INITRES
    original_unchanged = (md5_of(clean) == m0)
    res = {"planted_token": tok, "baseline_first_initRes": baseline_first,
           "read_back_first_initRes": read_back, "reader_saw_the_plant": saw,
           "original_unchanged": original_unchanged,
           "state": "EXERCISED-PASS" if (saw and original_unchanged)
                    else "EXERCISED-FAIL"}
    if not saw:
        refuse("PLANT_RESIDUAL",
               dict(res, note="the reader the gate calls could not see a "
                              "planted first-uncorrected initRes; a log that "
                              "reads a residual from a blind reader is not "
                              "evidence."))
    if not original_unchanged:
        refuse("PLANT_RESIDUAL",
               dict(res, the_control_modified_the_artefact_it_grades=True))
    return res


# ================================ FREEZE CHECK ==============================
def freeze_check():
    """T25 and CLAUDE.md rule 2. Asserts (a) the accept-floor control is
    BYTE-IDENTICAL to D6RF7's (the floor is provably inherited), and (b) the
    grader's own bytes equal the committed blob at HEAD -- the latter is a
    PLACEHOLDER until the supervisor freezes and is not enforced pre-freeze."""
    out = {"permission": "NOT_FROZEN"}
    afc_path = os.path.join(HERE, "d6rf10_accept_floor_control.py")
    out["accept_floor_control_md5"] = md5_of(afc_path)
    out["accept_floor_inherited_verbatim"] = (
        out["accept_floor_control_md5"] == D6RF7_ACCEPT_FLOOR_MD5)
    out["accept_floor_value"] = ACCEPT_FLOOR
    out["conv_bar"] = CONV_BAR
    out["t25_floor_unmoved"] = (ACCEPT_FLOOR == 1.0e-05
                                and afc.PRIMAL_MIN_RES_TOL == 1.0e-08
                                and afc.PRIMAL_MIN_RES_TOL_DIFF == 1000.0)
    if not out["accept_floor_inherited_verbatim"]:
        refuse("FREEZE_CHECK",
               dict(out, note="the accept-floor control is NOT byte-identical "
                              "to D6RF7's; the floor is not provably inherited."))
    if not out["t25_floor_unmoved"]:
        refuse("FREEZE_CHECK",
               dict(out, note="T25 VIOLATED: the accept floor or a term moved."))
    return out


def drive():
    """Runs the planted-zero control, the freeze check and a selftest of the
    gate scoring at ZERO compute. Returns 0 only if all behave as registered."""
    tmp = tempfile.mkdtemp(prefix="d6rf10_grade_drive_")
    rc = 0
    print("D6RF10 GRADE -- DRIVEN (no compute, PERMISSION=NOT_FROZEN)")
    try:
        fz = freeze_check()
        print("  OK    freeze_check   accept_floor_inherited_verbatim=%s  "
              "floor=%g  t25_floor_unmoved=%s"
              % (fz["accept_floor_inherited_verbatim"], fz["conv_bar"],
                 fz["t25_floor_unmoved"]))
    except Refusal as e:
        rc = 1; print("  FAIL  freeze_check  REFUSED -- %s" % str(e)[:200])
    try:
        pc = run_residual_plant_control(os.path.join(tmp, "plant"))
        ok = pc["reader_saw_the_plant"] and pc["original_unchanged"]
        print("  %-5s plant_control  state=%s  read_back=%s  saw=%s  "
              "original_unchanged=%s"
              % ("OK" if ok else "FAIL", pc["state"], pc["read_back_first_initRes"],
                 pc["reader_saw_the_plant"], pc["original_unchanged"]))
        if not ok:
            rc = 1
    except Refusal as e:
        rc = 1; print("  FAIL  plant_control REFUSED -- %s" % str(e)[:200])
    # selftest the gate scoring: a GATE-FAIL leg (single block, binding OVER
    # floor) stays GATE FAIL under the plateau layer (>= floor is untouched).
    fail_log = _synthetic_leg_log(os.path.join(tmp, "fail.log"),
                                  init_p="1.62e-05")
    seg_f = _bind(read_legs(fail_log), "R1")
    gf = gate_conv(seg_f, "R1")
    ok_gate = (gf["binding_verdict"] == "GATE FAIL"
               and gf["verdict"] == "GATE FAIL")
    print("  %-5s gate_conv      p_first 1.62e-05 -> %s (binding %s)"
          % ("OK" if ok_gate else "FAIL", gf["verdict"], gf["binding_verdict"]))
    if not ok_gate:
        rc = 1

    # A2 PLATEAU selftest (AMENDMENT A2): all THREE branches + insufficient
    # samples, first as a DIRECT gate_plateau unit test on synthetic series.
    flat = [8.00e-06, 8.01e-06, 8.00e-06, 8.02e-06, 8.00e-06, 8.01e-06]     # ~0.25%
    moving = [6.306e-06, 6.884e-06, 6.50e-06, 6.70e-06, 6.40e-06, 6.60e-06]  # ~8.8%
    p_pass = gate_plateau(8.0e-06, flat)          # below floor + flat  -> PASS
    p_nar = gate_plateau(6.6e-06, moving)         # below floor + moving -> NOT A RESULT
    p_gf = gate_plateau(1.62e-05, flat)           # plateaued but >= floor -> GATE FAIL
    p_few = gate_plateau(8.0e-06, flat[:4])       # < 5 samples -> NOT A RESULT
    ok_plat = (p_pass["verdict"] == "PASS"
               and p_nar["verdict"] == "NOT A RESULT"
               and p_gf["verdict"] == "GATE FAIL"
               and p_few["verdict"] == "NOT A RESULT")
    print("  %-5s A2_plateau     below+flat(%.3g%%)->%s ; below+moving(%.3g%%)->%s"
          " ; flat+overfloor->%s ; <5samples->%s"
          % ("OK" if ok_plat else "FAIL",
             p_pass["relative_spread"] * 100.0, p_pass["verdict"],
             p_nar["relative_spread"] * 100.0, p_nar["verdict"],
             p_gf["verdict"], p_few["verdict"]))
    if not ok_plat:
        rc = 1

    # END-TO-END through gate_conv on multi-time-block container logs: a flat
    # below-floor series is a REAL PASS; a moving below-floor series (a would-be
    # PASS) is refused to NOT A RESULT.
    flat_log = _synthetic_series_log(
        os.path.join(tmp, "flat.log"), leg="R1",
        first_p_series=["%.3e" % v for v in flat])
    gp_flat = gate_conv(_bind(read_legs(flat_log), "R1"), "R1")
    move_log = _synthetic_series_log(
        os.path.join(tmp, "move.log"), leg="R1",
        first_p_series=["%.3e" % v for v in moving])
    gp_move = gate_conv(_bind(read_legs(move_log), "R1"), "R1")
    ok_e2e = (gp_flat["binding_verdict"] == "PASS"
              and gp_flat["verdict"] == "PASS"
              and gp_move["binding_verdict"] == "NOT A RESULT"
              and gp_move["verdict"] == "NOT A RESULT")
    print("  %-5s gate_conv+A2   flat series -> %s (binding %s, spread %.3g%%) ; "
          "moving series -> %s (binding %s, spread %.3g%%)"
          % ("OK" if ok_e2e else "FAIL",
             gp_flat["verdict"], gp_flat["binding_verdict"],
             gp_flat["plateau_check"]["relative_spread"] * 100.0,
             gp_move["verdict"], gp_move["binding_verdict"],
             gp_move["plateau_check"]["relative_spread"] * 100.0))
    if not ok_e2e:
        rc = 1
    # G-CONFIG selftest: a leg at the WRONG corrector count is NOT A RESULT
    wrong_log = _synthetic_leg_log(os.path.join(tmp, "wrong.log"),
                                   init_p="8.0e-06", n_p_solves=2)  # nNonOrth=1
    seg_w = _bind(read_legs(wrong_log), "R1")
    gw = gate_conv(seg_w, "R1")   # R1 wants nNonOrth 3
    ok_cfg = (gw["verdict"] == "NOT A RESULT"
              and gw["reason"] == "CONFIG_NOT_AS_REGISTERED")
    print("  %-5s g_config       R1(wants nNonOrth 3) on a 1-corrector leg -> "
          "%s (%s)"
          % ("OK" if ok_cfg else "FAIL", gw["verdict"], gw.get("reason")))
    if not ok_cfg:
        rc = 1
    print("  RESULT %s" % ("ALL AS REGISTERED" if rc == 0 else "NOT AS REGISTERED"))
    return rc


def grade_log(log_path, rung, skip_freeze=False):
    """The REAL-GRADE path. SELF-RUNS every control and REFUSES (raises Refusal
    -> exit 2) BEFORE emitting any gate verdict. A grade path that runs without
    its own controls is FAIL-OPEN; this mirrors the frozen `d6rf7_grade.py:grade`
    (freeze_check at :2922, run_planted_controls at :2948, afc.run_floor_control
    at :2962-2966). The controls ALWAYS run on a real grade; `--skip-freeze`
    skips ONLY the frozen-path `freeze_check` (exactly d6rf7_grade.py:2922-2930,
    "NEVER on a real grading run"), NEVER the planted-residual or accept-floor
    control -- those run on every real grade. No control is weakened."""
    # (1) freeze_check: accept-floor byte-inheritance + T25 floor-unmoved.
    #     Skippable ONLY the way d6rf7_grade.py:2922 skips its freeze_check.
    if not skip_freeze:
        freeze_check()                                   # Refusal -> exit 2
    ctrl = tempfile.mkdtemp(prefix="d6rf10_grade_ctrl_")
    # (2) THE PLANTED-ZERO RESIDUAL CONTROL (CLAUDE.md rule 3) -- ALWAYS runs.
    plant = run_residual_plant_control(os.path.join(ctrl, "plant"))  # -> exit 2
    # (3) ACCEPT_FLOOR_UNMOVED, read back out of the ARM'S OWN LOG, in BOTH
    #     directions (PREREGISTRATION.md section 4; d6rf7_grade.py:2962-2966).
    #     ALWAYS runs; refuses (exit 2) if a floor term moved in the run's bytes.
    #     A log with no floor dump refuses fail-CLOSED (a blind reader is not
    #     evidence); a log absent is NOT EXERCISED and the leg is NOT A RESULT.
    try:
        floor = afc.run_floor_control(os.path.join(ctrl, "accept_floor"),
                                      log_path)
    except afc.AcceptFloorRefusal as e:
        refuse("ACCEPT_FLOOR_UNMOVED", {"instrument_refused": str(e)[:2500]})
    # controls PASSED -> now, and only now, read and grade the arm log.
    legs = read_legs(log_path)
    controls = {"planted_residual": plant, "accept_floor_unmoved": floor}
    if rung not in legs["segments"]:
        return {"item": ITEM, "verdict": "NOT A RESULT",
                "reason": "LEG_NOT_IN_LOG", "rung": rung,
                "legs_seen": legs["order"], "controls": controls}
    seg = _bind(legs, rung)
    row = gate_conv(seg, rung)
    row["item"] = ITEM
    row["controls"] = controls
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drive", action="store_true",
                    help="drive the controls + selftest (no compute)")
    ap.add_argument("--log", help="grade a real arm container log")
    ap.add_argument("--rung", default="R1", help="which rung the log is")
    ap.add_argument("--skip-freeze", action="store_true",
                    help="skip ONLY the frozen-path freeze_check (dev/selftest; "
                         "NEVER on a real grading run). Does NOT skip the "
                         "planted-residual or the accept-floor control -- those "
                         "ALWAYS run on a real grade (d6rf7_grade.py pattern).")
    a = ap.parse_args()
    if a.drive:
        return drive()
    if a.log:
        try:
            row = grade_log(a.log, a.rung, a.skip_freeze)
        except Refusal as e:
            sys.stderr.write("D6RF10_GRADE REFUSED %s\n" % e)
            return 2
        print(json.dumps(row, indent=1, default=str))
        return 0
    ap.print_help()
    return 64


if __name__ == "__main__":
    sys.exit(main())
