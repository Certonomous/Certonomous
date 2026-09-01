#!/usr/bin/env python3
r"""Curriculum D19T -- THE GRADER.

===========================================================================
PART I -- THE VERDICT CEILING, AND WHY IT IS NOT A HEDGE
===========================================================================
`VERDICT_CEILING = "GATE REACHED"`.  It is applied as the LAST step of every
composition and can only make a verdict WORSE, never better.

The reason is named rather than felt.  Sanaa's 2026-09-01 doctrine section 0
says *"Every gated case runs its grid convergence study automatically; a case
without one is not a result."*  **D19T does not carry one.**  Its graded
quantity is an INSTRUMENT PROPERTY -- whether a finite-difference plateau
closes -- measured on one 4,032-cell mesh, and a plateau is not a physical
prediction that a grid triple would band.  Whether section 0 reaches an
instrument-verification item is a **GATE-DESIGN question, and gate design is
reserved to Sanaa** (`CLAUDE.md` rule 9; D19R section 5 in terms).

So this item does not decide that question in its own favour by ignoring it,
and does not decide it against itself by declaring `NOT A RESULT` on a rule
that may not reach it.  It caps at `GATE REACHED` and says why on the row.

===========================================================================
PART II -- THE ITEM CEILING IS COMPOSED FROM THE UNCAPPED ROW VERDICT
===========================================================================
**D19T-COMPOSE-DEF-1, inherited as a DEFECT and repaired here, not copied.**
`curriculum_D19M/d19m_grade.py:1526` composes the item from
`rows[r]["verdict"]` -- the value `compose_row` has ALREADY passed through
`_apply_ceiling`.  The item's own `_apply_ceiling` therefore receives a token
that is by construction no better than the ceiling, so **the item-level
ceiling can never fire** and `capped_by_ceiling` at item level is always
`False` however the item was actually bounded.

`compose_item` here reads `verdict_before_ceiling` and applies the ceiling
once, at the end, where it can actually bind.  `RED-CEIL` in the selftest
drives it: an item whose uncapped verdict is `PASS` must emit
`capped_by_ceiling: true`, and under D19M's composition it emits `false`.

===========================================================================
PART III -- THE BIRTH REGISTER (CLAUDE.md rule 3)
===========================================================================
Every reader whose ZERO could pass a gate is BORN at grade time: a known
perturbation is planted into a SEPARATE COPY of the artefact, read back
THROUGH THE REAL READER FUNCTION, and the grader REFUSES (exit 2) if the
reader cannot see it.  `n_not_born != 0` is a refusal, not a footnote.

The register is emitted into the graded JSON so a later reader can see which
readers were shown able to see a non-zero ON THIS RUN, rather than trusting
that they once were.
"""
import argparse
import ast
import copy
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d19t_age_guard as AGE                                       # noqa: E402

ITEM = "D19T"
VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
VERDICT_CEILING = "GATE REACHED"
CEILING_REASON = (
    "D19T grades an INSTRUMENT PROPERTY (whether an FD plateau closes) on ONE "
    "4,032-cell mesh and carries NO grid-convergence study.  Sanaa's 2026-09-01 "
    "doctrine section 0 requires one of every gated case; whether it reaches an "
    "instrument-verification item is a GATE-DESIGN question reserved to Sanaa. "
    "The item caps rather than deciding that question in its own favour.")

# =============================================================================
# REGISTERED CONSTANTS -- frozen at the pre-registration commit
# =============================================================================
ARMS_DECLARED = ["MESH", "T08", "T10", "T12", "XT10"]
ARM_TOL = {"T08": 1.0e-8, "T10": 1.0e-10, "T12": 1.0e-12, "XT10": 1.0e-10}
ARM_KIND = {"MESH": "SCRIPT", "T08": "T", "T10": "T", "T12": "T", "XT10": "X"}
ARM_RANKS = {"MESH": 1, "T08": 2, "T10": 2, "T12": 2, "XT10": 2}
ARTEFACT = {"T": "d19t_T.json", "X": "d19t_X.json"}
TERMINAL = {"T": "D19T_T_WRITTEN", "X": "D19T_X_WRITTEN", "SCRIPT": "D19T_MESH_IDENTITY_OK"}

# per-arm core-minute caps and the ITEM CEILING (PREREGISTRATION section 6)
ARM_CAP_CORE_MIN = {"MESH": 1.0, "T08": 4.0, "T10": 4.0, "T12": 4.0, "XT10": 5.0}
ITEM_CEILING_CORE_MIN = 18.0

# the treatment arm whose plateau is the headline, and the reproduction arm
ARM_REPRO = "T08"
ARM_TREAT = "T10"
ARM_TREAT2 = "T12"
ARM_ADJ = "XT10"
# T08's PLATEAU IS REGISTERED TO FAIL, and that failure is its SUCCESS.
# It re-measures D19R's condition with this harness; a T08 that CLOSED the
# plateau would mean this instrument is not the one that failed, so its
# plateau verdict is an INPUT TO G-REPRO and is NOT a row failure.  Registered
# here, before the run, so the exemption cannot be granted afterwards to a
# reproduction arm that happened to disappoint.
ARM_PLATEAU_GRADED = {"T08": False, "T10": True, "T12": True}

# steps and the plateau reading
TRIVIAL_STEP = 3.0e-2
STEPS_SANAA = [1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5]
STEPS = [TRIVIAL_STEP] + STEPS_SANAA
PLATEAU_CENTRE = 1.0e-3
PLATEAU_TOL_PCT = 10.0            # D19R's G19R-1b band, UNCHANGED
DECADE_STRIDE = 1
GRADED_COMPONENT = ("shape", 7)
CONTRAST_COMPONENT = ("shape", 6)
FUNCTIONS = ["CD", "CL"]
NEAR_ZERO_ABS = 1.0e-14

# G-ADJ: adjoint vs FD at the plateau centre, on the GRADED component
ADJ_BAND_PCT = 10.0
# G-TRIVIAL (DAFOAM_CHARTER section 4): the deliberately wrong step MUST FAIL
TRIVIAL_MUST_EXCEED_PCT = 10.0

# G-REPRO: T08 must reproduce D19R's landed failure.  Both legs are registered.
D19R_FINE_DEV_PCT = 21.060684242435336        # D19R d19r_selected_step.json
D19R_SHAPE7_CD = {1.0e-2: -0.00020890917339921877,
                  1.0e-3: -0.00020648832854686106,
                  1.0e-4: -0.00016300047367412418,
                  1.0e-5: 0.000251917448013117,
                  3.0e-2: -0.00014732049854471185}
D19R_ADJ_SHAPE7_CD = -2.099480e-04
REPRO_BAND_PCT = 5.0     # T08's FD must match D19R's landed FD to this, per step

# G-EPS: the registered scaling law.  eps = (FD(h) - adjoint) * h is a FIXED
# ADDITIVE CD ERROR; H1 predicts it falls with the primal tolerance.
EPS_STEPS = [1.0e-4, 1.0e-5]      # the bias-dominated end
EPS_RATIO_MIN = 10.0              # 1e-8 -> 1e-10 must cut |eps| by at least this

# G-MANIFEST: the pre-normalisation must hold with ZERO mismatches
MANIFEST_MISMATCHES_ALLOWED = 0

FATAL_TOKENS = ("Floating point exception", "SIGSEGV", "Segmentation fault",
                "Traceback (most recent call last)", "MPI_ABORT", "Killed",
                "primal solution failed", "DIVERGED", "std::bad_alloc")
BENIGN = {"simple_no_criteria": "SIMPLE: no convergence criteria found",
          "continuity_errors": "time step continuity errors",
          "trapfpe_notice": "trapFpe:"}

_LEDGER = re.compile(
    r"^ARM=(?P<arm>\S+)\s+ROW=(?P<row>\S+)\s+IMG=(?P<img>\S+)\s+DIGEST=(?P<digest>\S+)\s+"
    r"rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall>\d+)\s+ranks=(?P<ranks>\d+)\s+"
    r"core_min=(?P<core_min>[0-9.]+)\s+cap_core_min=(?P<cap>[0-9.]+).*?"
    r"cpuset=(?P<cpuset>\S+)", re.M)
# DAFoam prints the tolerance it ACTUALLY honoured.  This is the direct reading.
_TOLLINE = re.compile(
    r"Minimal residual\s+(?P<res>[0-9.eE+-]+)\s+satisfied the prescribed tolerance\s+"
    r"(?P<tol>[0-9.eE+-]+)")

# -----------------------------------------------------------------------------
# THE BIRTH REGISTER -- every reader whose ZERO could pass a gate
# -----------------------------------------------------------------------------
READERS = {
    "R1_read_ledger": {
        "produces": "core_min, rc, ranks, cpuset, digest -> G-CAPS/G9/G-PLACE/G-NP",
        "zero_passes_a_gate": True,
        "hazard": "no ledger -> no rows -> no cap violations -> every cap gate green"},
    "R2_read_fatal_tokens": {
        "produces": "fatal-token list -> G-COMPLETE",
        "zero_passes_a_gate": True,
        "hazard": "an unreadable log yields zero fatal tokens and reads as clean"},
    "R3_read_tolerance_lines": {
        "produces": "per-solve honoured tolerance -> G-TOL  (THE LOAD-BEARING ONE)",
        "zero_passes_a_gate": True,
        "hazard": "zero lines would mean 'nothing contradicted the tolerance'; the "
                  "gate must FAIL CLOSED on a count of zero, and the reader must be "
                  "shown able to see a real line"},
    "R4_read_fd": {
        "produces": "FD derivative table -> G-PLAT7/G-ADJ/G-TRIVIAL/G-EPS/G-REPRO",
        "zero_passes_a_gate": True,
        "hazard": "a missing row read as absent rather than as a failure"},
    "R5_read_adjoint": {
        "produces": "adjoint totals -> G-ADJ/G-EPS",
        "zero_passes_a_gate": True,
        "hazard": "a zero adjoint would make every relative agreement undefined or "
                  "trivially small"},
    "R6_read_manifest_mismatches": {
        "produces": "manifest mismatch list -> G-MANIFEST",
        "zero_passes_a_gate": True,
        "hazard": "ZERO IS THE PASS CONDITION here, which is precisely rule 3's case"},
}


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail},
                             sort_keys=True, default=str))


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def count_asserts(path):
    """L-332: `python3 -O` strips `assert`, so an assert is not a guard.  Counted
    here, and the count is itself proved against a PLANTED assert in the selftest."""
    return sum(1 for n in ast.walk(ast.parse(open(path).read()))
               if isinstance(n, ast.Assert))


def _f(x, default=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


# =============================================================================
# READERS -- each one named, each one born
# =============================================================================
def read_ledger(text):
    rows, order = {}, []
    for m in _LEDGER.finditer(text):
        arm = m.group("arm")
        rows[arm] = {"arm": arm, "row": m.group("row"), "image": m.group("img"),
                     "digest": m.group("digest"), "rc": int(m.group("rc")),
                     "wall_s": int(m.group("wall")), "ranks": int(m.group("ranks")),
                     "core_min": float(m.group("core_min")),
                     "cap_core_min": float(m.group("cap")),
                     "cpuset": m.group("cpuset")}
        order.append(arm)
    return rows, order


def read_fatal_tokens(text):
    return [t for t in FATAL_TOKENS if t in text]


def read_benign_counts(text):
    return {k: text.count(v) for k, v in BENIGN.items()}


def read_tolerance_lines(text):
    """THE LOAD-BEARING READER.  DAFoam prints the tolerance it actually honoured,
    so this reads the APPLIED value rather than inferring it from a dictionary.

    Returns one record per solve: the achieved residual and the honoured tolerance.
    """
    out = []
    for m in _TOLLINE.finditer(text):
        res, tol = _f(m.group("res")), _f(m.group("tol"))
        if res is None or tol is None:
            continue
        out.append({"residual": res, "tolerance": tol})
    return out


def read_fd(doc, dv, idx):
    """rows[].fd for one component -> {step: {...}}.  Reads NOTHING else."""
    for row in doc.get("rows", []):
        if row.get("dv") == dv and row.get("idx") == idx:
            if row.get("status") != "MEASURED":
                return None
            out = {}
            for _k, v in row.get("fd", {}).items():
                s = _f(v.get("step"))
                if s is not None:
                    out[s] = v
            return out
    return None


def read_adjoint(doc, of, dv, idx):
    arr = doc.get("adjoint", {}).get(of, {}).get(dv)
    if not isinstance(arr, list) or idx >= len(arr):
        return None
    return _f(arr[idx])


def read_manifest_mismatches(arm_dir, manifest):
    """ZERO IS THE PASS CONDITION, which is exactly rule 3's case.

    Delegates to the FROZEN guard's own checker rather than re-implementing the
    comparison -- but that checker signals by RAISING and returns a bare `True`
    on success, so the empty list this reader returns has to be constructed
    here.  The birth register's zero leg proves this reader returns EMPTY on a
    manifest that holds, and its plant leg proves it returns NON-EMPTY on one
    that does not.
    """
    try:
        AGE.check_manifest(arm_dir, manifest)
        return []
    except AGE.Refusal as exc:
        return [json.loads(str(exc))]


# =============================================================================
# THE BIRTH REGISTER -- plant, read back through the REAL reader, refuse
# =============================================================================
def born(root):
    """Every reader in READERS is planted into a SEPARATE COPY and read back.

    Nothing here mutates a run artefact: each leg builds its own object or its
    own temporary text.  A reader that cannot see its plant is a REFUSAL.
    """
    seen = {}

    # R1 -- a ledger row planted into a copy of the ledger text
    base_led = ("ARM=ZZPLANT ROW=PATCHED IMG=i DIGEST=d rc=0 wall_s=7 ranks=3 "
                "core_min=1.5 cap_core_min=9.0 memory=4g cpuset=1,15\n")
    rows, _o = read_ledger(base_led)
    seen["R1_read_ledger"] = {
        "planted": "ARM=ZZPLANT core_min=1.5 ranks=3",
        "recovered": bool(rows.get("ZZPLANT", {}).get("core_min") == 1.5
                          and rows.get("ZZPLANT", {}).get("ranks") == 3),
        "read_back": rows.get("ZZPLANT"),
        "zero_leg": read_ledger("no ledger rows here at all\n")[0] == {}}

    # R2 -- a fatal token planted into a copy of a clean log
    clean = "Time = 100\nEnd\n"
    seen["R2_read_fatal_tokens"] = {
        "planted": "MPI_ABORT",
        "recovered": read_fatal_tokens(clean + "MPI_ABORT was called\n") == ["MPI_ABORT"],
        "zero_leg": read_fatal_tokens(clean) == []}

    # R3 -- a real DAFoam tolerance line planted into a copy of a clean log
    line = "Minimal residual 9.9674e-09 satisfied the prescribed tolerance 1e-08\n"
    got3 = read_tolerance_lines(clean + line + line)
    seen["R3_read_tolerance_lines"] = {
        "planted": "2 x %r" % line.strip(),
        "recovered": bool(len(got3) == 2
                          and abs(got3[0]["tolerance"] - 1.0e-8) < 1e-20
                          and abs(got3[0]["residual"] - 9.9674e-09) < 1e-20),
        "read_back": got3,
        "zero_leg": read_tolerance_lines(clean) == []}

    # R4 -- an FD row planted into a synthetic document
    docp = {"rows": [{"dv": "shape", "idx": 7, "status": "MEASURED",
                      "fd": {"0.001": {"step": 1.0e-3, "dCD": "-1.234e-04",
                                       "dCL": "0.5", "ok": True}}}]}
    got4 = read_fd(docp, "shape", 7)
    seen["R4_read_fd"] = {
        "planted": "shape[7] fd[1e-3].dCD = -1.234e-04",
        "recovered": bool(got4 and _f(got4.get(1.0e-3, {}).get("dCD")) == -1.234e-04),
        "read_back": got4,
        "zero_leg": read_fd({"rows": []}, "shape", 7) is None}

    # R5 -- an adjoint value planted into a synthetic document
    doca = {"adjoint": {"CD": {"shape": ["0.0"] * 7 + ["-2.099480e-04"]}}}
    got5 = read_adjoint(doca, "CD", "shape", 7)
    seen["R5_read_adjoint"] = {
        "planted": "adjoint.CD.shape[7] = -2.099480e-04",
        "recovered": bool(got5 is not None and abs(got5 + 2.099480e-04) < 1e-16),
        "read_back": got5,
        "zero_leg": read_adjoint({"adjoint": {}}, "CD", "shape", 7) is None}

    # R6 -- a mismatch planted into a manifest whose file is real on disk
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "system")
        os.makedirs(p)
        f = os.path.join(p, "planted")
        with open(f, "w") as fh:
            fh.write("the real bytes")
        good = {"entries": [{"path": "system/planted", "md5": md5_of(f)}]}
        bad = {"entries": [{"path": "system/planted", "md5": "0" * 32}]}
        zero_leg = read_manifest_mismatches(td, good)
        got6 = read_manifest_mismatches(td, bad)
    seen["R6_read_manifest_mismatches"] = {
        "planted": "recorded md5 flipped to 0*32 on a file that EXISTS on disk",
        "recovered": bool(got6),
        "read_back": got6[:2] if isinstance(got6, list) else got6,
        "zero_leg": zero_leg == []}

    readers, not_born, zero_unproved = {}, [], []
    for k, v in READERS.items():
        c = seen.get(k, {})
        readers[k] = {**v, "born": bool(c.get("recovered")),
                      "zero_leg_proved": bool(c.get("zero_leg")),
                      "planted": c.get("planted"), "read_back": c.get("read_back")}
        if not readers[k]["born"]:
            not_born.append(k)
        if not readers[k]["zero_leg_proved"]:
            zero_unproved.append(k)
    return {"readers": readers, "n_readers": len(readers),
            "n_born": sum(1 for v in readers.values() if v["born"]),
            "n_not_born": len(not_born), "not_born": not_born,
            "n_zero_leg_unproved": len(zero_unproved), "zero_leg_unproved": zero_unproved,
            "rule": "CLAUDE.md rule 3 -- a zero from a reader not shown able to see a "
                    "non-zero is not evidence.  Both legs are required: the reader "
                    "SEES a planted non-zero, and it returns EMPTY on clean input."}


# =============================================================================
# GATES
# =============================================================================
def g_stages(ran):
    short = [a for a in ARMS_DECLARED if a not in ran]
    return {"declared": len(ARMS_DECLARED), "executed": len(ran),
            "arms_declared": ARMS_DECLARED, "arms_ran": sorted(ran),
            "arms_missing": short,
            "verdict": "PASS" if not short else "NOT A RESULT",
            "why": "declared vs executed is a GATE INPUT, not a footnote"}


def g_tol(arm, text, n_solves_expected):
    """G-TOL -- THE LOAD-BEARING GATE.  The tolerance was APPLIED, read from the
    solver's own statement of what it honoured, on EVERY solve.

    Fails closed on a count of zero: no lines is not 'nothing contradicted it'.
    """
    want = ARM_TOL[arm]
    lines = read_tolerance_lines(text)
    wrong = [r for r in lines if abs(r["tolerance"] - want) > 1e-3 * want]
    worst = max((r["residual"] for r in lines), default=None)
    out = {"arm": arm, "tolerance_registered": want, "n_lines": len(lines),
           "n_expected": n_solves_expected,
           "n_wrong_tolerance": len(wrong),
           "wrong_examples": wrong[:3],
           "worst_achieved_residual": worst,
           "all_below_tolerance": bool(worst is not None and worst <= want)}
    if not lines:
        out["verdict"] = "NOT A RESULT"
        out["why"] = ("ZERO tolerance statements read.  A gate that treats an empty "
                      "reading as agreement is the planted-zero failure; this one "
                      "fails closed.")
    elif wrong:
        out["verdict"] = "GATE FAIL"
        out["why"] = ("the solver honoured a tolerance other than the registered one "
                      "on %d solves -- the dictionary did not take" % len(wrong))
    elif len(lines) != n_solves_expected:
        out["verdict"] = "GATE FAIL"
        out["why"] = ("%d solves reached the tolerance but %d were registered: a solve "
                      "that ran out of iterations does not appear here and its CD is "
                      "NOT converged" % (len(lines), n_solves_expected))
    else:
        out["verdict"] = "PASS"
        out["why"] = ("every registered solve printed the registered tolerance, read "
                      "from the solver's own statement")
    return out


def g_completion(root, arm, led, doc, text, log_name):
    """CLAUDE.md rule 4 -- all of it or none of it."""
    out = {"arm": arm, "clauses": {}, "log": log_name}
    kind = ARM_KIND[arm]
    out["clauses"]["rc_zero"] = bool(led and led.get("rc") == 0)
    out["clauses"]["terminal_statement"] = bool(TERMINAL[kind] in text)
    if kind != "SCRIPT":
        out["clauses"]["artefact_present"] = doc is not None
    hits = read_fatal_tokens(text)
    out["clauses"]["no_fatal_token"] = not hits
    out["fatal_tokens_seen"] = hits
    out["benign_counts"] = read_benign_counts(text)
    out["_benign_note"] = ("COUNTED AND NAMED, never suppressed.  `SIMPLE: no "
                           "convergence criteria found` is OpenFOAM's banner and is "
                           "NOT evidence: DAFoam applies its own primalMinResTol, "
                           "which G-TOL reads directly.")
    ag = {"ran": False}
    mpath = os.path.join(root, arm, ".d19t_manifest.json")
    spath = AGE.sentinel_path(root, arm)
    if os.path.isfile(mpath) and os.path.isfile(spath):
        arts = [ARTEFACT[kind]] if kind != "SCRIPT" else ["checkMesh.log"]
        try:
            ev = AGE.check_arm(os.path.join(root, arm), arts, spath,
                               json.load(open(mpath)), [root])
            ag = {"ran": True, "ok": True, "evidence": ev}
        except AGE.Refusal as exc:
            ag = {"ran": True, "ok": False, "refusal": json.loads(str(exc))}
    out["age_guard"] = ag
    out["clauses"]["age_guard"] = bool(ag.get("ok"))
    out["verdict"] = "PASS" if all(out["clauses"].values()) else "GATE FAIL"
    return out


def g_manifest(root, arms_ran):
    """G-MANIFEST -- the decomposeParDict PRE-NORMALISATION held.

    D19R2 measured `system/decomposeParDict` mutating in exactly the three np=2
    arms, five `kahipCoeffs` lines appended by decomposePar itself.  D19T does
    NOT exclude the path and does NOT widen `SOLVER_WRITE_TARGETS` -- that would
    be the gate-design decision D19M's guard explicitly declined.  Staging runs
    decomposePar to a FIXED POINT first, so the file the manifest pins is the
    file decomposePar will write, and the gate stays byte-for-byte as strict.
    """
    per, total = {}, 0
    for arm in arms_ran:
        mpath = os.path.join(root, arm, ".d19t_manifest.json")
        if not os.path.isfile(mpath):
            per[arm] = {"manifest": False, "mismatches": None}
            continue
        mm = read_manifest_mismatches(os.path.join(root, arm), json.load(open(mpath)))
        per[arm] = {"manifest": True, "n_entries": len(json.load(open(mpath)).get("entries", [])),
                    "n_mismatches": len(mm), "mismatches": mm[:5]}
        total += len(mm)
    missing = [a for a, v in per.items() if not v["manifest"]]
    return {"per_arm": per, "n_mismatches_total": total,
            "allowed": MANIFEST_MISMATCHES_ALLOWED, "arms_without_manifest": missing,
            "verdict": ("NOT A RESULT" if missing else
                        "PASS" if total <= MANIFEST_MISMATCHES_ALLOWED else "GATE FAIL"),
            "why": "no path is excluded and no write-target list is widened; the "
                   "dictionary is pre-normalised to a fixed point at staging so it "
                   "does not move"}


# ---- the plateau reading -----------------------------------------------------
def deviations(fd, centre, of):
    """Both DECADE-separated neighbour deviations at `centre`, on one function."""
    ladder = STEPS_SANAA
    if centre not in ladder:
        refuse("PLATEAU_CENTRE_NOT_ON_LADDER", {"centre": centre, "ladder": ladder})
    i = ladder.index(centre)
    lo, hi = i - DECADE_STRIDE, i + DECADE_STRIDE
    if lo < 0 or hi >= len(ladder):
        refuse("CANDIDATE_LACKS_DECADE_NEIGHBOUR",
               {"centre": centre, "stride": DECADE_STRIDE, "ladder": ladder})
    key = "dCD" if of == "CD" else "dCL"
    vals = {}
    for s in (ladder[lo], centre, ladder[hi]):
        row = fd.get(s)
        if not row or not row.get("ok"):
            return None
        vals[s] = _f(row.get(key))
        if vals[s] is None:
            return None
    ref = vals[centre]
    if abs(ref) < NEAR_ZERO_ABS:
        return None
    return {"centre": centre, "coarse_step": ladder[lo], "fine_step": ladder[hi],
            "ref": ref, "coarse_value": vals[ladder[lo]], "fine_value": vals[ladder[hi]],
            "coarse_pct": abs(vals[ladder[lo]] - ref) / abs(ref) * 100.0,
            "fine_pct": abs(vals[ladder[hi]] - ref) / abs(ref) * 100.0}


def g_plateau(arm, doc):
    """G-PLAT7 -- the gate Sanaa's section 5 is about.  TWO-SIDED, band UNCHANGED
    at D19R's 10.0 %, read on the GRADED component for BOTH functions."""
    dv, idx = GRADED_COMPONENT
    fd = read_fd(doc, dv, idx) if doc else None
    if not fd:
        return {"arm": arm, "verdict": "NOT A RESULT",
                "why": "no MEASURED row for %s[%d]" % (dv, idx)}
    per, worst, binding = {}, -1.0, None
    for of in FUNCTIONS:
        d = deviations(fd, PLATEAU_CENTRE, of)
        if d is None:
            return {"arm": arm, "verdict": "NOT A RESULT",
                    "why": "the plateau at %r could not be read on %s (a neighbour step "
                           "failed, or the reference is at the near-zero floor)"
                           % (PLATEAU_CENTRE, of)}
        d["two_sided"] = bool(max(d["coarse_pct"], d["fine_pct"]) <= PLATEAU_TOL_PCT)
        per["%s[%d]/%s" % (dv, idx, of)] = d
        for side in ("coarse_pct", "fine_pct"):
            if d[side] > worst:
                worst, binding = d[side], ["%s[%d]" % (dv, idx), of, side.split("_")[0]]
    closed = all(v["two_sided"] for v in per.values())
    return {"arm": arm, "component": "%s[%d]" % (dv, idx),
            "centre": PLATEAU_CENTRE, "band_pct": PLATEAU_TOL_PCT,
            "decade_stride": DECADE_STRIDE, "per_function": per,
            "score_pct": worst, "binding": binding, "all_two_sided": closed,
            "reading": "max over BOTH functions and BOTH sides (not min)",
            "verdict": "PASS" if closed else "GATE FAIL",
            "why": ("the plateau closes two-sided on both functions inside the "
                    "UNCHANGED 10.0 %% band" if closed else
                    "the plateau does not close: worst %.4f %% on %s" % (worst, binding))}


def g_repro(doc, t08_plateau):
    """G-REPRO -- THE EXPERIMENT'S OWN PLANTED ZERO.

    T08 re-measures D19R's condition with THIS harness.  It must (a) reproduce
    D19R's landed FD values per step, and (b) FAIL the plateau.  If T08 PASSES
    the plateau then this harness is not D19R's instrument, and every downstream
    claim that tightening changed something is withdrawn.

    Leg (b) is the reason this item can say "tightening closed it" at all.  A
    before/after with no demonstrated "before" is one measurement wearing two
    labels.
    """
    dv, idx = GRADED_COMPONENT
    fd = read_fd(doc, dv, idx) if doc else None
    if not fd:
        return {"verdict": "NOT A RESULT", "why": "T08 produced no MEASURED row"}
    per, bad = {}, []
    for s, want in sorted(D19R_SHAPE7_CD.items()):
        row = fd.get(s)
        got = _f(row.get("dCD")) if row and row.get("ok") else None
        if got is None:
            per[repr(s)] = {"d19r": want, "d19t": None, "rel_pct": None}
            bad.append(s)
            continue
        rel = abs(got - want) / abs(want) * 100.0
        per[repr(s)] = {"d19r": want, "d19t": got, "rel_pct": rel}
        if rel > REPRO_BAND_PCT:
            bad.append(s)
    # LEG (b): the reproduction arm must FAIL the plateau, as D19R did.
    p_verdict = (t08_plateau or {}).get("verdict")
    failed_as_registered = p_verdict == "GATE FAIL"
    out = {"arm": ARM_REPRO, "band_pct": REPRO_BAND_PCT, "per_step": per,
           "steps_outside_band": [repr(s) for s in bad],
           "values_reproduced": not bad,
           "t08_plateau_verdict": p_verdict,
           "t08_plateau_failed_as_registered": failed_as_registered,
           "t08_plateau_score_pct": (t08_plateau or {}).get("score_pct"),
           "d19r_score_pct": D19R_FINE_DEV_PCT}
    if bad:
        out["verdict"] = "GATE FAIL"
        out["why"] = ("T08 does not reproduce D19R at %d steps; a difference "
                      "downstream cannot be attributed to the tolerance" % len(bad))
    elif p_verdict is None:
        out["verdict"] = "NOT A RESULT"
        out["why"] = "T08's plateau could not be read, so the 'before' is unproved"
    elif not failed_as_registered:
        out["verdict"] = "GATE FAIL"
        out["why"] = ("T08 CLOSED the plateau that D19R could not.  This harness is "
                      "therefore not measuring D19R's condition, and any downstream "
                      "improvement attributed to the tolerance is withdrawn.")
    else:
        out["verdict"] = "PASS"
        out["why"] = ("T08 reproduces D19R's landed shape[7]/CD at every step AND "
                      "fails the plateau as D19R did: this harness IS D19R's "
                      "instrument, and the 'before' is demonstrated rather than "
                      "quoted")
    return out


def g_adjoint(t_doc, x_doc):
    """G-ADJ -- the adjoint against the plateau value, on the GRADED component.

    NOTE FOR THE READER, registered before the run: on D19R's LANDED artefacts
    this gate ALREADY PASSES.  adjoint = -2.099480e-04 against FD at 3e-3 =
    -2.095615e-04 is 0.1841 %.  Sanaa's section 5 conditional -- "if the adjoint
    is off on that component alone" -- has a FALSE antecedent on the evidence
    that exists.  The gate is registered anyway, because a measurement that is
    expected to pass is still a measurement.
    """
    dv, idx = GRADED_COMPONENT
    fd = read_fd(t_doc, dv, idx) if t_doc else None
    adj = read_adjoint(x_doc, "CD", dv, idx) if x_doc else None
    if fd is None or adj is None:
        return {"verdict": "NOT A RESULT",
                "why": "the FD row or the adjoint value is absent"}
    if abs(adj) < NEAR_ZERO_ABS:
        return {"verdict": "NOT A RESULT", "why": "the adjoint is at the near-zero floor"}
    row = fd.get(PLATEAU_CENTRE)
    got = _f(row.get("dCD")) if row and row.get("ok") else None
    if got is None:
        return {"verdict": "NOT A RESULT", "why": "no ok FD value at the plateau centre"}
    rel = abs(got - adj) / abs(adj) * 100.0
    per = {}
    for s in STEPS:
        r = fd.get(s)
        v = _f(r.get("dCD")) if r and r.get("ok") else None
        per[repr(s)] = {"fd": v,
                        "rel_pct": (abs(v - adj) / abs(adj) * 100.0) if v is not None else None}
    return {"component": "%s[%d]" % (dv, idx), "function": "CD",
            "adjoint": adj, "fd_at_centre": got, "centre": PLATEAU_CENTRE,
            "rel_pct": rel, "band_pct": ADJ_BAND_PCT, "per_step": per,
            "verdict": "PASS" if rel <= ADJ_BAND_PCT else "GATE FAIL",
            "why": "adjoint vs FD at the registered plateau centre"}


def g_trivial(t_doc, x_doc):
    """G-TRIVIAL -- DAFOAM_CHARTER section 4.  The SAME probe at a deliberately
    wrong step MUST FAIL the agreement band.  If the wrong step also passes, the
    gate is not measuring what it claims and G-ADJ's verdict is WITHDRAWN."""
    dv, idx = GRADED_COMPONENT
    fd = read_fd(t_doc, dv, idx) if t_doc else None
    adj = read_adjoint(x_doc, "CD", dv, idx) if x_doc else None
    if fd is None or adj is None or abs(adj) < NEAR_ZERO_ABS:
        return {"verdict": "NOT A RESULT", "why": "the FD row or the adjoint is absent"}
    row = fd.get(TRIVIAL_STEP)
    got = _f(row.get("dCD")) if row and row.get("ok") else None
    if got is None:
        return {"verdict": "NOT A RESULT",
                "why": "the trivial-baseline step produced no ok value"}
    rel = abs(got - adj) / abs(adj) * 100.0
    failed = rel > TRIVIAL_MUST_EXCEED_PCT
    return {"step": TRIVIAL_STEP, "fd": got, "adjoint": adj, "rel_pct": rel,
            "must_exceed_pct": TRIVIAL_MUST_EXCEED_PCT,
            "trivial_baseline_failed_as_required": failed,
            "withdraws_adjoint_verdict": not failed,
            "verdict": "PASS" if failed else "GATE FAIL",
            "why": ("the deliberately wrong step (30x the registered centre) misses the "
                    "adjoint by %.4f %%, so the agreement gate is discriminating" % rel
                    if failed else
                    "the WRONG step also agrees within the band -- the gate is not "
                    "measuring what it claims and G-ADJ is withdrawn")}


def eps_of(fd, adj, steps):
    """eps = (FD(h) - adjoint) * h.  A FIXED ADDITIVE CD ERROR shows up as a
    CONSTANT here across h; that constancy is what identifies the mechanism."""
    out = {}
    for s in steps:
        row = fd.get(s) if fd else None
        v = _f(row.get("dCD")) if row and row.get("ok") else None
        out[repr(s)] = None if (v is None or adj is None) else (v - adj) * s
    vals = [abs(v) for v in out.values() if v is not None]
    return {"per_step": out, "mean_abs": (sum(vals) / len(vals)) if vals else None,
            "n": len(vals)}


def g_eps(docs, x_doc):
    """G-EPS -- the registered SCALING LAW, and the three-way discriminator.

    H1 (near-null direction + convergence bias): |eps| falls with the primal
        tolerance, by at least EPS_RATIO_MIN from 1e-8 to 1e-10.
    H2 (frozen wall distance in the adjoint path): a discrepancy on shape[7]
        SURVIVES tightening -- eps does not fall, or the adjoint gap does not.
    H3 (parallel reduction bias): eps is INDEPENDENT of the tolerance.

    H2 and H3 share the falsifier "eps does not fall"; they are separated by
    WHERE the residue sits -- H2 in the adjoint-vs-FD gap on this component
    alone, H3 in eps for EVERY component including the contrast control.
    """
    dv, idx = GRADED_COMPONENT
    cdv, cidx = CONTRAST_COMPONENT
    adj = read_adjoint(x_doc, "CD", dv, idx) if x_doc else None
    adjc = read_adjoint(x_doc, "CD", cdv, cidx) if x_doc else None
    if adj is None:
        return {"verdict": "NOT A RESULT", "why": "no adjoint to measure eps against"}
    per = {}
    for arm in (ARM_REPRO, ARM_TREAT, ARM_TREAT2):
        d = docs.get(arm)
        per[arm] = {"tolerance": ARM_TOL[arm],
                    "graded": eps_of(read_fd(d, dv, idx) if d else None, adj, EPS_STEPS),
                    "contrast": eps_of(read_fd(d, cdv, cidx) if d else None, adjc, EPS_STEPS)}
    e8 = per[ARM_REPRO]["graded"]["mean_abs"]
    e10 = per[ARM_TREAT]["graded"]["mean_abs"]
    ratio = (e8 / e10) if (e8 and e10) else None
    fell = bool(ratio is not None and ratio >= EPS_RATIO_MIN)
    return {"per_arm": per, "steps": EPS_STEPS,
            "eps_1e8": e8, "eps_1e10": e10, "ratio_1e8_over_1e10": ratio,
            "ratio_required": EPS_RATIO_MIN, "eps_fell": fell,
            "hypothesis_supported": ("H1" if fell else "NOT H1 -- see H2/H3 separation"),
            "verdict": "PASS" if fell else "GATE FAIL",
            "why": ("|eps| fell by %.2fx from tol 1e-8 to 1e-10, at or above the "
                    "registered %.1fx: the FD floor is a CONVERGENCE BIAS and it is "
                    "removable" % (ratio, EPS_RATIO_MIN) if fell else
                    "|eps| did not fall as registered; H1 is NOT supported and the "
                    "H2/H3 separation in this gate's per-arm contrast decides which")}


def g_caps(led_rows):
    over, total = [], 0.0
    for arm, r in led_rows.items():
        cap = ARM_CAP_CORE_MIN.get(arm)
        total += r["core_min"]
        if cap is None:
            over.append({"arm": arm, "reason": "arm is not on the registered cap list"})
        elif r["core_min"] > cap:
            over.append({"arm": arm, "core_min": r["core_min"], "cap": cap})
    return {"per_arm": {a: {"core_min": r["core_min"],
                            "cap": ARM_CAP_CORE_MIN.get(a)} for a, r in led_rows.items()},
            "total_core_min": total, "item_ceiling": ITEM_CEILING_CORE_MIN,
            "over_cap": over, "over_ceiling": bool(total > ITEM_CEILING_CORE_MIN),
            "verdict": "PASS" if not over and total <= ITEM_CEILING_CORE_MIN else "GATE FAIL",
            "why": "CLAUDE.md rule 12: an overrun stops the run, it does not get a "
                   "new budget"}


def g_np(led_rows):
    bad = {a: r["ranks"] for a, r in led_rows.items() if r["ranks"] != ARM_RANKS.get(a)}
    return {"registered": ARM_RANKS, "violations": bad,
            "verdict": "PASS" if not bad else "GATE FAIL",
            "why": "np is held at D19R's OWN value on every solver arm, because the "
                   "reproduction control compares against D19R's landed numbers and "
                   "a changed decomposition would confound the tolerance"}


def g_place(led_rows, cpuset_registered):
    bad = {a: r["cpuset"] for a, r in led_rows.items() if r["cpuset"] != cpuset_registered}
    return {"registered_cpuset": cpuset_registered, "violations": bad,
            "verdict": "PASS" if not bad else "GATE FAIL"}


def g_toolchain(led_rows, digest_registered, so_md5_registered, docs):
    bad = []
    for a, r in led_rows.items():
        if digest_registered and r["digest"] != digest_registered:
            bad.append({"arm": a, "field": "digest", "got": r["digest"]})
    for a, d in docs.items():
        if d is None:
            continue
        got = (d.get("identity") or {}).get("libidwarp_so_md5")
        if so_md5_registered and got != so_md5_registered:
            bad.append({"arm": a, "field": "libidwarp_so_md5", "got": got})
    return {"registered_digest": digest_registered, "registered_so_md5": so_md5_registered,
            "mismatches": bad, "verdict": "PASS" if not bad else "GATE FAIL",
            "why": "DAFOAM_CHARTER section 6: toolchain identity is an image digest "
                   "and a library hash, NEVER a version string"}


# =============================================================================
# COMPOSITION
# =============================================================================
def _apply_ceiling(verdict):
    order = {"PASS": 6, "GATE REACHED": 5, "PENDING": 4, "BLOCKED": 3,
             "GATE FAIL": 2, "NOT A RESULT": 1}
    if order.get(verdict, 0) > order.get(VERDICT_CEILING, 0):
        return VERDICT_CEILING, True
    return verdict, False


def _worst(tokens):
    """NOT A RESULT dominates GATE FAIL dominates everything else."""
    if "NOT A RESULT" in tokens:
        return "NOT A RESULT"
    if "GATE FAIL" in tokens:
        return "GATE FAIL"
    if "BLOCKED" in tokens:
        return "BLOCKED"
    if "PENDING" in tokens:
        return "PENDING"
    if "GATE REACHED" in tokens:
        return "GATE REACHED"
    return "PASS"


def compose_row(arm, gates):
    """One row per solver arm.  Returns BOTH the capped and the UNCAPPED token;
    the item composes from the UNCAPPED one (see the module docstring, part II)."""
    parts = {"completion": gates["G-COMPLETE"][arm]["verdict"],
             "tolerance": gates["G-TOL"][arm]["verdict"]}
    # T08's plateau is REGISTERED TO FAIL and feeds G-REPRO instead; see
    # ARM_PLATEAU_GRADED.  A NOT A RESULT there still binds, because an
    # unreadable plateau is not a demonstrated "before".
    if arm in gates["G-PLAT7"]:
        pv = gates["G-PLAT7"][arm]["verdict"]
        if ARM_PLATEAU_GRADED.get(arm, True):
            parts["plateau"] = pv
        elif pv == "NOT A RESULT":
            parts["plateau_unreadable"] = pv
    raw = _worst(list(parts.values()))
    why = "; ".join("%s=%s" % (k, v) for k, v in sorted(parts.items()))
    final, capped = _apply_ceiling(raw)
    return {"row": arm, "verdict": final, "verdict_before_ceiling": raw,
            "capped_by_ceiling": capped, "parts": parts, "why": why}


def compose_item(gates, rows):
    """THE REPAIR.  Composed from `verdict_before_ceiling`, so the item-level
    ceiling can actually bind.  D19M composed from the already-capped token and
    its item ceiling was unreachable -- see the module docstring, part II."""
    row_raw = [rows[r]["verdict_before_ceiling"] for r in rows]
    hard = [gates[g]["verdict"] for g in
            ("G-STAGES", "G-MANIFEST", "G-CAPS", "G-NP", "G-PLACE", "G9-TOOLCHAIN",
             "G-REPRO", "G-ADJ", "G-TRIVIAL", "G-EPS")]
    # G-TRIVIAL WITHDRAWS G-ADJ rather than merely sitting beside it.
    if gates["G-TRIVIAL"].get("withdraws_adjoint_verdict"):
        hard.append("NOT A RESULT")
    raw = _worst(row_raw + hard)
    verdict, capped = _apply_ceiling(raw)
    capped_anywhere = bool(capped or any(rows[r]["capped_by_ceiling"] for r in rows))
    return {"verdict": verdict, "verdict_before_ceiling": raw,
            "capped_by_ceiling": capped,
            "capped_by_ceiling_anywhere": capped_anywhere,
            "rows_capped_by_ceiling": [r for r in rows if rows[r]["capped_by_ceiling"]],
            "verdict_ceiling": VERDICT_CEILING, "verdict_ceiling_reason": CEILING_REASON,
            "row_verdicts_uncapped": {r: rows[r]["verdict_before_ceiling"] for r in rows},
            "hard_gate_verdicts": dict(zip(
                ("G-STAGES", "G-MANIFEST", "G-CAPS", "G-NP", "G-PLACE", "G9-TOOLCHAIN",
                 "G-REPRO", "G-ADJ", "G-TRIVIAL", "G-EPS"), hard))}


# =============================================================================
# DRIVER
# =============================================================================
def read_arm_log(root, arm):
    best, bestm = None, -1.0
    for fn in os.listdir(root):
        if fn.startswith(arm + "_") and fn.endswith(".log"):
            p = os.path.join(root, fn)
            m = os.path.getmtime(p)
            if m > bestm:
                best, bestm = p, m
    if not best:
        return None, ""
    return best, open(best, errors="replace").read()


def grade(root, cpuset, digest, so_md5):
    birth = born(root)
    if birth["n_not_born"] != 0:
        refuse("CONTROL_READER_NOT_BORN",
               {"not_born": birth["not_born"],
                "note": "CLAUDE.md rule 3 -- a zero from a reader not shown able to "
                        "see a non-zero is not evidence.  The grader refuses rather "
                        "than grading with a blind reader."})
    if birth["n_zero_leg_unproved"] != 0:
        refuse("CONTROL_ZERO_LEG_UNPROVED",
               {"zero_leg_unproved": birth["zero_leg_unproved"],
                "note": "a reader that reports a plant on CLEAN input is not "
                        "measuring the plant"})

    lpath = os.path.join(root, "ledger.txt")
    if not os.path.isfile(lpath):
        refuse("NO_LEDGER", {"path": lpath})
    led_rows, _order = read_ledger(open(lpath, errors="replace").read())
    ran = [a for a in ARMS_DECLARED if a in led_rows]

    docs, texts, lognames = {}, {}, {}
    for arm in ran:
        kind = ARM_KIND[arm]
        lp, txt = read_arm_log(root, arm)
        texts[arm], lognames[arm] = txt, (os.path.basename(lp) if lp else None)
        if kind == "SCRIPT":
            docs[arm] = None
            continue
        ap = os.path.join(root, arm, ARTEFACT[kind])
        docs[arm] = json.load(open(ap)) if os.path.isfile(ap) else None

    n_solves = len([GRADED_COMPONENT, CONTRAST_COMPONENT]) * len(STEPS) * 2 + 2
    gates = {}
    gates["G-STAGES"] = g_stages(ran)
    gates["G-COMPLETE"] = {a: g_completion(root, a, led_rows.get(a), docs.get(a),
                                           texts.get(a, ""), lognames.get(a))
                           for a in ran}
    gates["G-TOL"] = {a: g_tol(a, texts.get(a, ""),
                               n_solves if ARM_KIND[a] == "T" else 1)
                      for a in ran if ARM_KIND[a] in ("T", "X")}
    gates["G-PLAT7"] = {a: g_plateau(a, docs.get(a))
                        for a in ran if ARM_KIND[a] == "T"}
    gates["G-MANIFEST"] = g_manifest(root, ran)
    gates["G-REPRO"] = g_repro(docs.get(ARM_REPRO), gates["G-PLAT7"].get(ARM_REPRO))
    gates["G-ADJ"] = g_adjoint(docs.get(ARM_TREAT), docs.get(ARM_ADJ))
    gates["G-TRIVIAL"] = g_trivial(docs.get(ARM_TREAT), docs.get(ARM_ADJ))
    gates["G-EPS"] = g_eps(docs, docs.get(ARM_ADJ))
    gates["G-CAPS"] = g_caps(led_rows)
    gates["G-NP"] = g_np(led_rows)
    gates["G-PLACE"] = g_place(led_rows, cpuset)
    gates["G9-TOOLCHAIN"] = g_toolchain(led_rows, digest, so_md5, docs)

    rows = {a: compose_row(a, gates) for a in ran if ARM_KIND[a] == "T"}
    item = compose_item(gates, rows)

    for tok in [item["verdict"]] + [r["verdict"] for r in rows.values()]:
        if tok not in VOCAB:
            refuse("VERDICT_OUTSIDE_VOCABULARY", {"token": tok, "vocab": list(VOCAB)})

    return {"item": ITEM, "root": os.path.abspath(root),
            "grader_md5": md5_of(os.path.abspath(__file__)),
            "grader_asserts": count_asserts(os.path.abspath(__file__)),
            "registered": {
                "arms": ARMS_DECLARED, "arm_tolerances": ARM_TOL,
                "arm_ranks": ARM_RANKS, "arm_caps_core_min": ARM_CAP_CORE_MIN,
                "item_ceiling_core_min": ITEM_CEILING_CORE_MIN,
                "steps": STEPS, "steps_sanaa": STEPS_SANAA,
                "trivial_baseline_step": TRIVIAL_STEP,
                "plateau_centre": PLATEAU_CENTRE, "plateau_tol_pct": PLATEAU_TOL_PCT,
                "decade_stride": DECADE_STRIDE,
                "arm_plateau_graded": ARM_PLATEAU_GRADED,
                "graded_component": list(GRADED_COMPONENT),
                "contrast_component": list(CONTRAST_COMPONENT),
                "adj_band_pct": ADJ_BAND_PCT,
                "eps_ratio_min": EPS_RATIO_MIN, "repro_band_pct": REPRO_BAND_PCT,
                "n_solves_per_T_arm": n_solves},
            "birth_register": birth, "gates": gates, "rows": rows, **item}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--cpuset", required=True)
    ap.add_argument("--digest", required=True)
    ap.add_argument("--so-md5", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    try:
        out = grade(a.root, a.cpuset, a.digest, a.so_md5)
    except Refusal as exc:
        sys.stderr.write("D19T_GRADE REFUSED: %s\n" % exc)
        return 2
    dest = a.out or os.path.join(a.root, "d19t_grade.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
        fh.flush()
        os.fsync(fh.fileno())
    print("D19T_GRADE_WRITTEN %s" % dest)
    print("D19T_VERDICT %s  (uncapped %s, capped_by_ceiling=%s)"
          % (out["verdict"], out["verdict_before_ceiling"], out["capped_by_ceiling"]))
    for r in sorted(out["rows"]):
        print("   row %-5s %-14s (uncapped %s)"
              % (r, out["rows"][r]["verdict"], out["rows"][r]["verdict_before_ceiling"]))
    print("D19T_BIRTH %d/%d readers born, %d zero-legs proved"
          % (out["birth_register"]["n_born"], out["birth_register"]["n_readers"],
             out["birth_register"]["n_readers"] - out["birth_register"]["n_zero_leg_unproved"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
