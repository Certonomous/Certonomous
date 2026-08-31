# =====================================================================
# UNFROZEN, UNREVIEWED, INCOMPLETE DRAFT -- DO NOT RUN, DO NOT GRADE.
# Halted mid-authoring 2026-08-31 on Sanaa's order to stop work.
# This file is NOT a frozen grading path under CLAUDE.md rule 2: no
# pre-registration document accompanies it and no commit fixes it.
# closure-supervisor has NOT performed SUPERVISION_CHARTER sec.3 check 1
# (the measurement-script diff read) on this file. A relayed check is a
# summary, not a check, and no check has been performed at all here.
# It is committed ONLY so the work survives; the R4b instruments sat
# untracked through a 32-hour shutdown and were one checkout from gone.
# NOTHING THIS FILE PRODUCES IS A RESULT.
# =====================================================================
#!/usr/bin/env python3
"""R4b-Ib - THE SUCCESSOR BIRTH-GRADER.  Four repairs, and nothing else.

R4b-I's gates are CLOSED.  `_dev/` compute under
`/home/ubuntu/closure-data/r4b_instruments/` (2026-08-28T17:39:12Z-17:43:16Z,
~11.2 MB, including a GRADED B3 birth record) is FIRST COMPUTE for R4b-I on the
drafters' own terms: `QUEUE_ENTRY_DRAFT.json:19` names that instrument root's
NON-EXISTENCE as its own pre-compute condition, and that condition is now false
on disk.  A registration that names its own pre-compute test is bound when that
test fails, and a `_dev/` prefix or a self-applied "NOT A REGISTERED ARTEFACT"
label cannot decide whether a rule binds its own author.

Therefore `grade_r4b.py` MAY NOT BE EDITED.  This file is a SUCCESSOR, exactly
as G1 -> G1b: a NEW instrument for a NEW item, R4b-Ib.

WHAT THIS FILE IS, ARCHITECTURALLY, AND WHY
-------------------------------------------
It IMPORTS the frozen `grade_r4b.py` and re-uses it UNMODIFIED.  Every band,
threshold, cap, label and gate criterion for B1 and B2 is therefore not
"copied" - it is the SAME CODE OBJECT, and cannot have drifted.  The parent is
PINNED BY SHA256 and this file REFUSES if the parent's bytes have moved, so the
dependency is a checked one, not an assumed one.

Only four things are repaired, all in the STRICTLY STRICTER direction:

  D1  `grade_r4b.py:478` `m = json.load(open(model_json))` is UNGUARDED.  With
      an absent MODEL.json it raises FileNotFoundError -> uncaught traceback,
      exit 1: not a refusal, not a verdict in the vocabulary.  It happens AFTER
      `os.makedirs` at :477, so it leaves a partial write and NO birth record.
      REPAIR: `require_readable_json` / `require_readable_file` - named
      refusals, exit 2, run BEFORE the first consumer of those files and
      therefore before the byte `:477` would write.

  D2  `:734` declares `gate_set=["B1","B2","B3","B4","B5"]` but `:750` builds
      the record with `B1`, `B2`, `B5` only.  There is no `b3` or `b4` variable
      in the file; `gate_set` is inert metadata consumed nowhere; `:1038`
      decides on three gates and `:1047` returns rc 0 when those three pass.
      The registered headline "B1-B5 all PASS -> GATE REACHED" (sec. 5.6) IS
      NOT COMPUTABLE and a run returns rc 0 LOOKING like the registered result.
      REPAIR: `b3_selector` and `b4_builder` actually grade B3 and B4 against
      sec. 5's frozen criteria, both enter the record, and `headline()`
      computes sec. 5.6's mapping.

  D3  `:663` `if case_dir and os.path.isdir(case_dir):` SILENTLY SKIPS B5's
      drive demonstration when no `--built-case` is passed, and B5 still
      aggregates to PASS.  B5 would certify a runner it never ran - a control
      with no limb at all.  REPAIR: `B5-DRIVE-ABSENT`, a refusal.  In this
      successor B5 is additionally handed B4's own freshly built tree, so the
      limb cannot be absent by omission.

  D4  `:681` `sub = [v["verdict"] for v in rep.values() if isinstance(v, dict)]`
      aggregates over WHATEVER DICTS HAPPEN TO BE IN `rep`, not over a
      registered list, and `all()` over a short or empty set returns True.
      REPAIR: `aggregate_required()` - ONE function, used for the B-gate set,
      for B5's sub-report and for B3's controls.  It aggregates over an
      EXPLICIT REGISTERED LIST of required names and REFUSES (exit 2) if any
      required name is MISSING.  A MISSING GATE IS A REFUSAL, NEVER A SILENT
      OMISSION.  This is the structural fix and it is written once.

WHAT IS NOT CHANGED, AND IS RE-USED BY IMPORT
---------------------------------------------
* The fatal channel keeps the NARROW `Foam::sigFpe::sigHandler` form
  (`grade_r4b.py:840`).  NEVER the broad substring - OpenFOAM writes
  `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).` at line
  18 of EVERY log, so the broad form fired on 63 of 70 real logs, 57 with a
  clean `End` line.  It is a constant, not a detector (L-396, D548); it cost G1
  its entire 127.08 core-min verdict.  `grade()` is imported unmodified.
* B1's criterion (4 of 4 instruments, 100 % of refusals under `python3` AND
  `python3 -O`) and B2's criterion (6 of 6 controls, both halves each) are the
  imported functions themselves.  The `-O` selftest pair at `:471-472` is
  inside the imported `b1_existence_and_refusals`.
* Verdict vocabulary FIXED: PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
  BLOCKED / PENDING.  No synonyms.  sec. 5.6's composite `GATE REACHED
  (PARTIAL)` is a REGISTERED headline label from the frozen table, reproduced
  verbatim and kept out of the per-gate vocabulary channel.
* Aggregation is ONE-WAY: a gate may only pull the item verdict DOWN.
* ZERO `ast.Assert` nodes (L-332: `python -O` erases `assert`, so a refusal
  written as one silently vanishes).  `--selftest` PARSES ITS OWN AST to prove
  it rather than eyeballing it.
* This file starts no process it does not itself stop, and uses no process-
  termination verb; `--selftest` proves that mechanically over its own bytes,
  with a planted positive control, tolerating exactly one token - the frozen
  B5 clause NAME `never_kills`, which this file must be able to name.

THE TWO ROOTS THIS FILE MUST NOT TOUCH
--------------------------------------
* `/home/ubuntu/closure-data/r4b` - R4b's SOLVE root.  Its ABSENCE is R4b's own
  pre-compute condition and R4b's solve arm is BLOCKED on Sanaa's ruling on the
  increment.  Re-asserted here, verbatim from `grade_r4b.py:694-698`.
* `/home/ubuntu/closure-data/r4b_instruments` - R4b-I's instrument root.  It
  holds the `_dev/` compute the closure supervisor's ruling rests on.  Writing
  there disturbs that evidence, so `R4b-I-ROOT-GUARD` refuses it.  R4b-Ib
  writes to `/home/ubuntu/closure-data/r4b_ib_birth` instead.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import sys
import time

# No .pyc may be written into the FROZEN parent directory by importing from it,
# and stale bytecode inverts control/mutation tests.  Set before the import.
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)

import grade_r4b as P                                                # noqa: E402

# ------------------------------------------------------------------ pinning
PARENT_PATH = os.path.join(PARENT, "grade_r4b.py")
PARENT_SHA256 = \
    "0e2554ae00e486c75a8529f07e77a974c388913d96d1839d0bc8d601cd34ca96"
SELECT_PATH = os.path.join(PARENT, "select_control.py")
SELECT_SHA256 = \
    "50d9622d95a26bc02b72c8af19f025934e1313570433ac95107387594f7f290f"
BUILD_PATH = os.path.join(PARENT, "build_r4b_cases.py")
BUILD_SHA256 = \
    "b45ddd8e7f2a02fef286623f396f41f82223563262580fa18e84cf37c11e82d7"
REGISTRATION_PATH = os.path.join(PARENT, "INSTRUMENT_BUILD_PREREGISTRATION.md")
REGISTRATION_SHA256 = \
    "7a80553cc36a7462baf35c770a10807e0c3ca7c51ddc038dc6b9c23201c289f9"

PINNED = {PARENT_PATH: PARENT_SHA256, SELECT_PATH: SELECT_SHA256,
          BUILD_PATH: BUILD_SHA256, REGISTRATION_PATH: REGISTRATION_SHA256}

# ------------------------------------------------------------------- roots
IB_ROOT = "/home/ubuntu/closure-data/r4b_ib_birth"
R4B_I_INSTRUMENT_ROOT = P.INSTRUMENT_ROOT      # /home/.../r4b_instruments
SOLVE_ROOT = P.SOLVE_ROOT                      # /home/.../r4b   - MUST BE ABSENT
BIRTH_RECORD = os.path.join(IB_ROOT, "r4b_ib_instrument_birth.json")

# The REAL producer artefact for B4's COVERAGE precondition: the FS2/FS5
# discharge written by the frozen `make_coverage.py` chain on 2026-08-23, NOT a
# development fixture (L-402: ask who WROTE the bytes your control reads).
REAL_COVERAGE_MD = os.path.join(os.path.dirname(PARENT), "R4_sparta_build",
                                "COVERAGE.md")

# ------------------------------------- THE REGISTERED REQUIRED NAME LISTS (D4)
REQUIRED_B_GATES = ("B1", "B2", "B3", "B4", "B5")
REQUIRED_B5_CLAUSES = ("capacity", "non_pgrep_path", "skip_if_complete",
                       "never_kills", "drive_with_noop_solver")
REQUIRED_B3_PARTS = ("G0a", "G0e", "grid")
REQUIRED_B4_PARTS = ("refusal_MODEL_ABSENT", "refusal_MODEL_HASH",
                     "refusal_COVERAGE_ABSENT", "refusal_CASE_TREE_EXISTS",
                     "term_order_n4", "set_libs_both_shapes",
                     "positive_build")

# sec. 5.6's registered headline labels, and nothing else.
HEADLINES = ("GATE REACHED", "GATE REACHED (PARTIAL)", "GATE FAIL", "BLOCKED",
             "PENDING")

# sec. 7.3, copied VERBATIM.  Neither number moves.
ESTIMATE_CORE_MIN = 12.0
CAP_CORE_MIN = 40.0
RANKS = 1


# ------------------------------------------------------------------ guards
def require_parent_unmodified():
    """Rule 2: verify the frozen files ARE the files that ran, by hash."""
    bad = []
    for path, want in PINNED.items():
        if not os.path.exists(path):
            bad.append(f"{path}: ABSENT")
            continue
        got = P.sha256_file(path)
        if got != want:
            bad.append(f"{path}: {got} != {want}")
    P.require(not bad, "PINNED-INSTRUMENT",
              "R4b-Ib re-uses R4b-I's frozen instruments BY IMPORT and BY PATH, "
              "and they have moved since R4b-Ib was registered. A successor "
              "grading against a silently edited parent is not a result:\n  "
              + "\n  ".join(bad))
    return {os.path.relpath(p, os.path.dirname(PARENT)): s
            for p, s in PINNED.items()}


def guard_ib_root(path):
    """No byte of R4b-Ib lands in R4b's SOLVE root or in R4b-I's instrument
    root.  The first would close R4b's amendment window before Sanaa has ruled
    on the increment; the second would disturb the `_dev/` evidence the closure
    supervisor's ruling rests on."""
    p = P.guard_write_root(path)                 # SOLVE-ROOT-GUARD, unmodified
    r = os.path.abspath(R4B_I_INSTRUMENT_ROOT)
    P.require(p != r and not p.startswith(r + os.sep), "R4b-I-ROOT-GUARD",
              f"{p} is inside R4b-I's instrument root {r}. R4b-I's gates are "
              f"CLOSED and its `_dev/` compute is the evidence the successor "
              f"ruling rests on; R4b-Ib writes to {IB_ROOT}.")
    return p


def require_readable_file(path, code, what):
    """THE D1 REPAIR, half one: a named refusal, exit 2, before any write."""
    P.require(bool(path), code, f"{what}: no path was given")
    P.require(os.path.exists(path), code,
              f"{what}: {path} does not exist. An absent input is a REFUSAL "
              f"(exit 2), never an uncaught traceback and never a partial "
              f"write with no birth record (grade_r4b.py:477-478).")
    P.require(os.path.isfile(path), code, f"{what}: {path} is not a file")
    P.require(os.path.getsize(path) > 0, code, f"{what}: {path} is empty")
    return os.path.abspath(path)


def require_readable_json(path, code, what):
    """THE D1 REPAIR, half two: readable AND parseable, both refusals."""
    p = require_readable_file(path, code, what)
    try:
        with open(p) as fh:
            json.load(fh)
    except ValueError as ex:
        P.refuse(code, f"{what}: {p} is not readable JSON: {ex}")
    except OSError as ex:
        P.refuse(code, f"{what}: {p} could not be read: {ex}")
    return p


# ------------------------------------------- THE D4 REPAIR, WRITTEN ONCE
def aggregate_required(mapping, required, code, what):
    """Aggregate over an EXPLICIT REGISTERED LIST of required names.

    `grade_r4b.py:681` aggregates over whatever dicts happen to be present, and
    `all()` over a short or empty set returns True - so a gate that never ran
    reads as PASS.  Here a MISSING required name is a REFUSAL (exit 2), never a
    silent omission, and every value must be in the fixed vocabulary.

    ONE-WAY: this returns PASS only when every required name reads PASS.
    """
    P.require(isinstance(mapping, dict), code,
              f"{what}: the record is not a mapping")
    missing = [n for n in required if n not in mapping]
    P.require(not missing, code,
              f"{what}: required gate(s) {missing} are MISSING from the record. "
              f"A missing gate is a refusal, never a silent omission: `all()` "
              f"over a short or empty set returns True, which is how an "
              f"ungraded gate reads as PASS.")
    verdicts = {}
    for n in required:
        v = mapping[n]
        s = v.get("verdict") if isinstance(v, dict) else v
        P.require(P.verdict_ok(s), code,
                  f"{what}: {n} carries {s!r}, which is not in the fixed "
                  f"vocabulary {P.VOCAB}")
        verdicts[n] = s
    v = "PASS" if all(s == "PASS" for s in verdicts.values()) else "GATE FAIL"
    return v, verdicts


def both_halves_guard(ctl):
    """ONE-WAY: a PASS whose demonstration is not recorded two-sided becomes
    GATE FAIL.  Any non-PASS verdict (PENDING under sec. 3.2's carve-out
    included) is returned untouched, so this can only pull a verdict DOWN."""
    v = ctl.get("verdict") if isinstance(ctl, dict) else None
    if v == "PASS" and ctl.get("both_halves") is not True:
        return "GATE FAIL"
    return v


# ------------------------------------------------------------- B3 (D2, new)
def b3_selector(root, bijdelta=None, timeout=1800):
    """B3 - THE BIRTH OF `select_control.py`, sec. 5 VERBATIM:

    > G0a and G0e demonstrated two-sided through `select_control.py`'s OWN
    > reader, not through the comparator's; plus the selector run over the full
    > frozen 12-value grid, producing a feasibility result at EVERY grid value.
    >
    > PASS requires both controls two-sided AND 12 of 12 grid values evaluated
    > and reported. Anything less is GATE FAIL.
    >
    > Registered and NOT graded here: the VALUE of xi*.

    The selector is RE-RUN FROM SCRATCH into R4b-Ib's own root.  No verdict and
    no value is read from R4b-I's `_dev/` tree; sec. 4.3's conservative rule
    stands - the demonstration MODEL.json is never promoted.
    """
    root = guard_ib_root(root)
    os.makedirs(root, exist_ok=True)
    frag_path = guard_ib_root(os.path.join(root, "birth",
                                           "B3_select_control.json"))
    os.makedirs(os.path.dirname(frag_path), exist_ok=True)

    argv = [sys.executable, SELECT_PATH, "--birth", "--demonstration",
            "--out-dir", root, "--birth-out", frag_path]
    if bijdelta:
        argv += ["--bijdelta", bijdelta]
    rc, out, err = P._run(argv, timeout=timeout)

    if rc != 0 or not os.path.exists(frag_path):
        return dict(gate="B3", instrument="select_control.py", rc=rc,
                    fragment=frag_path, fragment_written=os.path.exists(frag_path),
                    stderr_head=(err.strip().splitlines() or [""])[0][:300],
                    verdict="GATE FAIL",
                    reason="the selector did not complete its birth run, so "
                           "neither control nor the 12-value grid is on the "
                           "record")

    with open(frag_path) as fh:
        frag = json.load(fh)

    n_eval = frag.get("grid_values_evaluated")
    n_req = frag.get("grid_values_required")
    grid_ok = (isinstance(n_eval, int) and n_eval == n_req == len(P.SC.GRID)
               == 12)
    graded = {
        "G0a": dict(verdict=both_halves_guard(frag.get("G0a", {})),
                    reader=frag.get("G0a", {}).get("reader"),
                    real_artefact=frag.get("G0a", {}).get("real_artefact"),
                    real_artefact_producer=frag.get("G0a", {}).get(
                        "real_artefact_producer"),
                    both_halves=frag.get("G0a", {}).get("both_halves")),
        "G0e": dict(verdict=both_halves_guard(frag.get("G0e", {})),
                    reader=frag.get("G0e", {}).get("reader"),
                    rose_by=frag.get("G0e", {}).get("rose_by"),
                    required_rise=frag.get("G0e", {}).get("required_rise"),
                    both_halves=frag.get("G0e", {}).get("both_halves")),
        "grid": dict(verdict="PASS" if grid_ok else "GATE FAIL",
                     grid_values_evaluated=n_eval, grid_values_required=n_req,
                     rule="12 of 12 grid values evaluated and reported; a "
                          "selector that silently short-circuits is visible"),
    }
    verdict, per = aggregate_required(graded, REQUIRED_B3_PARTS,
                                      "B3-REQUIRED", "B3")
    self_reported = frag.get("verdict")
    P.require(self_reported == verdict, "B3-AGGREGATION-DISAGREES",
              f"select_control.py reports {self_reported!r} for its own birth "
              f"while R4b-Ib's aggregation over the registered required list "
              f"{list(REQUIRED_B3_PARTS)} reads {verdict!r}. An instrument and "
              f"its grader disagreeing about the instrument's own birth is a "
              f"refusal, not a verdict.")
    return dict(gate="B3", instrument="select_control.py",
                required_parts=list(REQUIRED_B3_PARTS), parts=graded,
                per_part_verdict=per,
                self_reported_verdict=self_reported,
                fragment=frag_path,
                model_json=os.path.join(root, "MODEL.json"),
                interpreter_optimize=frag.get("interpreter_optimize"),
                xi_star_reported_not_graded=frag.get(
                    "xi_star_reported_not_graded"),
                xi_star_note="sec. 5 B3: the VALUE of xi* is `reported, not "
                             "graded`. R4b's prediction P1 belongs to R4b's "
                             "registration and is graded there. NO VERDICT OF "
                             "THIS ITEM TURNS ON IT. R4b-I's `_dev` value is "
                             "NOT A RESULT and is not quoted here.",
                verdict=verdict)


# ------------------------------------------------------------- B4 (D2, new)
def b4_builder(root, model_json, coverage_md, case="alpha_125", timeout=1800):
    """B4 - THE BIRTH OF `build_r4b_cases.py`, sec. 5 VERBATIM:

    > Negative half: all four registered refusals fire - no MODEL.json; a
    > MODEL.json whose hash differs from the committed blob; a missing
    > COVERAGE.md; an existing case tree. Each exit 2, each under -O too.
    >
    > Positive half, and it must be REAL: with all four preconditions met, the
    > builder builds ONE REAL CASE TREE by calling `build_aposteriori.build()`
    > unmodified, into this item's run root. Verified on that tree: the
    > n in (1,2,3) assert is present AT THE NEW CALL SITE and fires when handed
    > n = 4; `set_libs` is verified on BOTH real shapes.
    >
    > PASS requires 4 of 4 refusals AND the positive build with both `set_libs`
    > shapes and the n assert verified. Anything less is GATE FAIL.
    """
    root = guard_ib_root(root)
    b4 = guard_ib_root(os.path.join(root, "b4"))
    os.makedirs(b4, exist_ok=True)
    out_root = guard_ib_root(os.path.join(root, "cases"))

    model_json = require_readable_json(model_json, "B4-MODEL-INPUT",
                                       "B4's MODEL.json")
    coverage_md = require_readable_file(coverage_md, "B4-COVERAGE-INPUT",
                                        "B4's COVERAGE.md")
    good_sha = P.sha256_file(model_json)
    missing_model = os.path.join(b4, "NO_SUCH_MODEL.json")
    missing_cov = os.path.join(b4, "NO_SUCH_COVERAGE.md")

    def fire(name, argv):
        rc1, _, e1 = P._run([sys.executable, BUILD_PATH] + argv,
                            timeout=timeout)
        rc2, _, e2 = P._run([sys.executable, "-O", BUILD_PATH] + argv,
                            timeout=timeout)
        is_ae = "AssertionError" in e1 or "AssertionError" in e2
        return dict(rc_python3=rc1, rc_python3_O=rc2,
                    fires=bool(rc1 == 2 and rc2 == 2),
                    is_assertion_error=is_ae,
                    stderr_head=(e1.strip().splitlines() or [""])[0][:200],
                    verdict=("PASS" if (rc1 == 2 and rc2 == 2 and not is_ae)
                             else "GATE FAIL"),
                    rule="exit 2 under python3 AND python3 -O, and NOT an "
                         "AssertionError (L-332)")

    parts = {}
    parts["refusal_MODEL_ABSENT"] = fire("MODEL-ABSENT", [
        "--model", missing_model, "--coverage", coverage_md,
        "--out-root", out_root])
    parts["refusal_MODEL_HASH"] = fire("MODEL-HASH", [
        "--model", model_json, "--coverage", coverage_md,
        "--model-sha256", "0" * 64, "--out-root", out_root])
    parts["refusal_COVERAGE_ABSENT"] = fire("COVERAGE-ABSENT", [
        "--model", model_json, "--coverage", missing_cov,
        "--model-sha256", good_sha, "--out-root", out_root])

    # the n in (1,2,3) check AT THE NEW CALL SITE, handed n = 4 (rule 14).
    bad_model = guard_ib_root(os.path.join(b4, "MODEL_n4.json"))
    with open(model_json) as fh:
        m4 = dict(json.load(fh))
    m4["bDelta_terms_scaled"] = [[4, 0, 0, -1.0]]
    m4["frozen_at"] = P.utcnow()
    with open(bad_model, "w") as fh:
        json.dump(m4, fh, indent=1)
    parts["term_order_n4"] = fire("TERM-ORDER (n = 4)", [
        "--model", bad_model, "--coverage", coverage_md,
        "--model-sha256", P.sha256_file(bad_model), "--dry-run",
        "--cases", case, "--out-root", out_root])
    parts["term_order_n4"]["planted_term"] = [4, 0, 0, -1.0]
    parts["term_order_n4"]["planted_model"] = bad_model

    # set_libs on BOTH real shapes, through the real `set_libs`.
    rc_l, o_l, e_l = P._run([sys.executable, BUILD_PATH, "--verify-set-libs",
                             "--out-root", root], timeout=timeout)
    libs = {}
    if rc_l == 0:
        try:
            libs = json.loads(o_l)
        except ValueError:
            libs = {}
    hills, ducts = libs.get("hills", {}), libs.get("ducts", {})
    libs_ok = bool(
        rc_l == 0 and libs.get("both_shapes_exercised") is True
        and hills.get("before", {}).get("has_libs_line") is False
        and ducts.get("before", {}).get("has_libs_line") is True
        and hills.get("after", {}).get("sparta_present") is True
        and ducts.get("after", {}).get("sparta_present") is True
        and hills.get("after", {}).get("n_top_level_libs_entries") == 1
        and ducts.get("after", {}).get("n_top_level_libs_entries") == 1)
    parts["set_libs_both_shapes"] = dict(
        rc=rc_l, report=libs,
        stderr_head=(e_l.strip().splitlines() or [""])[0][:200],
        rule="BOTH real shapes: (i) a hill case carrying NO libs line at all, "
             "on which a bare str.replace is a silent no-op and the run then "
             "returns the BASELINE field, which looks physical; (ii) a duct "
             "case carrying one naming a library absent from this machine. "
             "After set_libs the library name must be PRESENT in both, in "
             "exactly ONE top-level entry (L-221/L-222).",
        verdict="PASS" if libs_ok else "GATE FAIL")

    # THE POSITIVE HALF, and it must be REAL: one case tree actually built.
    rc_b, o_b, e_b = P._run([sys.executable, BUILD_PATH,
                             "--model", model_json, "--coverage", coverage_md,
                             "--model-sha256", good_sha, "--cases", case,
                             "--out-root", out_root], timeout=timeout)
    manifest_path = os.path.join(out_root, "build_manifest.json")
    man, built_dir = {}, None
    if rc_b == 0 and os.path.exists(manifest_path):
        with open(manifest_path) as fh:
            man = json.load(fh)
        rows = man.get("cases", [])
        built_dir = rows[0]["dir"] if rows else None
    build_ok = bool(rc_b == 0 and built_dir and os.path.isdir(built_dir))
    parts["positive_build"] = dict(
        rc=rc_b, case=case, out_root=out_root, manifest=manifest_path,
        built_dir=built_dir,
        builder_sha256=man.get("builder_sha256"),
        build_aposteriori_sha256=man.get("build_aposteriori_sha256"),
        n_cases_built=len(man.get("cases", [])),
        stderr_head=(e_b.strip().splitlines() or [""])[0][:200],
        rule="build_aposteriori.build() called UNMODIFIED into this item's own "
             "run root; one real case tree on disk",
        verdict="PASS" if build_ok else "GATE FAIL")

    # the fourth refusal needs the tree the positive half just built.
    parts["refusal_CASE_TREE_EXISTS"] = fire("CASE-TREE-EXISTS", [
        "--model", model_json, "--coverage", coverage_md,
        "--model-sha256", good_sha, "--cases", case,
        "--out-root", out_root])
    parts["refusal_CASE_TREE_EXISTS"]["note"] = (
        "fired against the tree the positive half built; R4b sec. 4.3 - no run "
        "is resumed in place, and copy_skeleton would DELETE it")

    verdict, per = aggregate_required(parts, REQUIRED_B4_PARTS,
                                      "B4-REQUIRED", "B4")
    return dict(gate="B4", instrument="build_r4b_cases.py",
                required_parts=list(REQUIRED_B4_PARTS), parts=parts,
                per_part_verdict=per, built_case_dir=built_dir,
                coverage_md=coverage_md,
                coverage_producer="the frozen make_coverage.py chain "
                                  "(f8c40810..., unmodified), 2026-08-23 - the "
                                  "FS2/FS5 discharge, NOT a development fixture",
                model_json=model_json, model_sha256=good_sha,
                verdict=verdict)


# ------------------------------------------------- B5 (D3 + D4, at call site)
def b5_required(root, case_dir):
    """B5 with D3 and D4 closed AT THE CALL SITE, so the frozen `b5_runner`
    stays byte-for-byte unmodified.

    D3: `grade_r4b.py:663` skips the drive demonstration when no case tree is
    given, and B5 still aggregates to PASS - certifying a runner it never ran,
    a control with NO LIMB AT ALL.  Here that is a refusal.

    D4: `:681` aggregates over whatever dicts are present.  Here the dict-valued
    clause set must equal the REGISTERED clause list EXACTLY, and the verdict is
    then recomputed over that list.  Because the two sets are proven equal
    first, this recomputation is identical to the frozen one on every reachable
    input, plus a refusal path - it can only refuse or agree, never invent a
    PASS.
    """
    P.require(bool(case_dir) and os.path.isdir(case_dir), "B5-DRIVE-ABSENT",
              f"B5's drive demonstration has no case tree ({case_dir!r}). "
              f"grade_r4b.py:663 SKIPS it silently and B5 still aggregates to "
              f"PASS, which certifies a runner that was never run - a sec. 2j "
              f"birth-requirement violation, a control with no limb at all.")
    rep = P.b5_runner(root, case_dir)
    present = tuple(sorted(k for k, v in rep.items() if isinstance(v, dict)))
    P.require(present == tuple(sorted(REQUIRED_B5_CLAUSES)), "B5-CLAUSE-SET",
              f"B5's clause set is {list(present)}, not the registered set "
              f"{sorted(REQUIRED_B5_CLAUSES)}. An unregistered or missing "
              f"clause is a refusal: aggregating over whatever happens to be "
              f"present is exactly how a skipped clause reads as PASS.")
    frozen_verdict = rep.get("verdict")
    verdict, per = aggregate_required(rep, REQUIRED_B5_CLAUSES,
                                      "B5-CLAUSE-SET", "B5")
    P.require(verdict == frozen_verdict, "B5-AGGREGATION-DISAGREES",
              f"the registered-list aggregation reads {verdict!r} while "
              f"grade_r4b.py:682's reads {frozen_verdict!r}; the two must agree "
              f"once the clause set is proven equal")
    rep["required_clauses"] = list(REQUIRED_B5_CLAUSES)
    rep["per_clause_verdict"] = per
    rep["verdict_over_registered_clause_list"] = verdict
    rep["verdict"] = verdict
    return rep


# ------------------------------------------------------ sec. 5.6, computed
def headline(gate_verdicts, controls, core_min, cap=CAP_CORE_MIN):
    """sec. 5.6's mapping table, computed.  In `grade_r4b.py` it is not
    computable at all (D2): three gates are graded, five are declared.

    The table, verbatim:
      B1-B5 all PASS                          -> GATE REACHED
      any B-gate GATE FAIL                    -> GATE FAIL
      a control PENDING per sec. 3.2's carve-out, and that is the ONLY
        shortfall                             -> GATE REACHED (PARTIAL),
                                                 with the not-born gate named
      the 40.0 core-min cap is reached        -> BLOCKED
      not yet started                         -> PENDING
    """
    if core_min is not None and core_min >= cap:
        return "BLOCKED", (f"the {cap} core-min cap is reached "
                           f"({core_min:.2f} core-min). An overrun stops the "
                           f"run; it does not get a new budget.")
    if all(v == "PASS" for v in gate_verdicts.values()):
        return "GATE REACHED", ("B1-B5 all PASS: the four instruments exist, "
                                "are frozen by sha, and every reader in them "
                                "has been shown able to see a non-zero through "
                                "the real production path.")
    pending = sorted(k for k, v in controls.items()
                     if v.get("verdict") == "PENDING")
    others = sorted(g for g, v in gate_verdicts.items()
                    if v != "PASS" and g != "B2")
    if pending and not others and gate_verdicts.get("B2") != "PASS":
        not_born = sorted({g for g, cs in P.GATE_CONTROLS.items()
                           for c in cs if c in pending})
        return "GATE REACHED (PARTIAL)", (
            f"sec. 3.2's registered carve-out is the ONLY shortfall: control(s) "
            f"{pending} are PENDING because the real producer artefact they "
            f"must travel is absent. NOT BORN for gate(s) {not_born}, which the "
            f"comparator must refuse to grade.")
    return "GATE FAIL", (
        f"B-gate(s) {sorted(g for g, v in gate_verdicts.items() if v != 'PASS')}"
        f" did not PASS. The instrument is repaired, the demonstration re-run, "
        f"and the repair costed INSIDE THE SAME CAP. The cap does not move.")


# ---------------------------------------------------------------- the birth
def run_birth(root, coverage_md=None, bijdelta=None, artefacts=None,
              started=None):
    """R4b-Ib's birth suite, in sec. 2.3 ORDER B's gate sequence: A2 (B3),
    A4 (B4), A6 (B5), A8 (B1 and B2)."""
    t0 = started if started is not None else time.time()
    pinned = require_parent_unmodified()

    # verbatim from grade_r4b.py:694-698 - R4b's SOLVE root must be ABSENT.
    P.require(not os.path.exists(SOLVE_ROOT), "SOLVE-ROOT-PRESENT",
              f"{SOLVE_ROOT} EXISTS. That is R4b's solve run root and its "
              f"absence is R4b's own pre-compute condition; this item may not "
              f"run while it exists, because anything written there closes "
              f"R4b's amendment window before Sanaa has ruled on the increment.")
    root = guard_ib_root(root)
    coverage_md = require_readable_file(coverage_md or REAL_COVERAGE_MD,
                                        "COVERAGE-INPUT", "COVERAGE.md")

    # A2 - B3.  It produces the demonstration MODEL.json B4 and B1 consume.
    b3 = b3_selector(root, bijdelta=bijdelta)

    # THE D1 REPAIR: refuse on an absent/unreadable MODEL.json BEFORE the first
    # consumer touches it, and therefore before grade_r4b.py:477's makedirs.
    model_json = require_readable_json(b3["model_json"], "MODEL-INPUT",
                                       "the demonstration MODEL.json B1 and B4 "
                                       "read (grade_r4b.py:478 loads it "
                                       "UNGUARDED, after :477 has already "
                                       "written)")

    # A4 - B4.  Its built tree is B5's drive limb, so D3 cannot recur by
    # omission.
    b4 = b4_builder(root, model_json, coverage_md)
    built_case_dir = b4.get("built_case_dir")

    # A6 - B5, with D3 and D4 closed at the call site.
    b5 = b5_required(root, built_case_dir)

    # A8 - B1 and B2.
    b1 = P.b1_existence_and_refusals(root, model_json, coverage_md,
                                     built_case_dir)

    art = dict(P.DEFAULT_ARTEFACTS)
    art.update(artefacts or {})
    scratch = os.path.join(root, "birth", "grade_r4b_ib")
    controls = {}
    controls["G0a"] = P.field_control(
        "G0a", art["G0a"], scratch,
        "the frozen extraction (kCorrectiveFrozenFoam)")
    controls["G0b"] = P.field_control(
        "G0b", art["G0b"], scratch,
        "the frozen extraction (kCorrectiveFrozenFoam)")
    controls["G0c"] = P.field_control(
        "G0c", art["G0c"], scratch,
        "the propagation solver (simpleFoam / kOmegaSSTCorrected)")
    controls["G0d"] = P.field_control(
        "G0d", art["G0d"], scratch, "OpenFOAM postProcess -func 'grad(U)'")
    controls["G0e"] = P.realisability_control(scratch)
    controls["G0f"] = P.zero_shot_control()

    born = {k: bool(v.get("born")) for k, v in controls.items()}
    n_born = sum(born.values())
    pending = {k: v["pending_path"] for k, v in controls.items()
               if v.get("verdict") == "PENDING"}
    not_born_gates = sorted({g for g, cs in P.GATE_CONTROLS.items()
                             for c in cs if not born.get(c)})
    b2 = dict(gate="B2", n_controls=len(controls), n_born=n_born,
              controls_born=born, pending=pending,
              verdict="PASS" if n_born == len(controls) else "GATE FAIL",
              not_born_gates=not_born_gates)

    gates = dict(B1=b1, B2=b2, B3=b3, B4=b4, B5=b5)
    item_verdict, per_gate = aggregate_required(gates, REQUIRED_B_GATES,
                                                "B-GATE-SET", "the item")
    core_min = (time.time() - t0) * RANKS / 60.0
    head, why = headline(per_gate, controls, core_min)

    record = dict(
        item="R4b-Ib",
        supersedes="R4b-I (gates CLOSED by first compute; grade_r4b.py frozen)",
        gate_set=list(REQUIRED_B_GATES),
        gate_set_is_graded=True,
        registration="cases/RANS_LES_closure_models/R4b_pair_control/R4b_Ib/"
                     "INSTRUMENT_BUILD_PREREGISTRATION_R4b_Ib.md",
        criteria_source="cases/RANS_LES_closure_models/R4b_pair_control/"
                        "INSTRUMENT_BUILD_PREREGISTRATION.md sec. 5 - every "
                        "band, threshold, cap and label copied VERBATIM",
        criteria_source_sha256=REGISTRATION_SHA256,
        pinned_instruments=pinned,
        at=P.utcnow(),
        interpreter=sys.version.split()[0],
        interpreter_optimize=int(sys.flags.optimize),
        instrument_root=root, solve_root=SOLVE_ROOT,
        solve_root_absent_at_start=True,
        r4b_i_instrument_root=R4B_I_INSTRUMENT_ROOT,
        r4b_i_instrument_root_untouched=True,
        birth_requirement="INSTRUMENT_BUILD_PREREGISTRATION.md section 5.0; "
                          "every demonstration is TWO-SIDED and both halves "
                          "are graded",
        hashes=P.hash_sweep(strict=False),
        controls=controls,
        gate_controls={k: list(v) for k, v in P.GATE_CONTROLS.items()},
        B1=b1, B2=b2, B3=b3, B4=b4, B5=b5,
        per_gate_verdict=per_gate,
        item_verdict=item_verdict,
        headline=head, headline_reason=why,
        cost=dict(core_minutes=round(core_min, 3), ranks=RANKS,
                  estimate_core_minutes=ESTIMATE_CORE_MIN,
                  cap_core_minutes=CAP_CORE_MIN,
                  cap_reached=bool(core_min >= CAP_CORE_MIN),
                  basis="wall seconds x ranks / 60, measured by this run"))
    return record


# ------------------------------------------- the D4 control on a REAL record
def d4_control(birth_record_path, out_path=None):
    """THE TWO-LIMB CONTROL FOR D4, ON A RECORD WRITTEN BY THE REAL PRODUCER.

    sec. 2j.2 / L-402: ask who WROTE the bytes your control reads.  A synthetic
    fixture is not enough - G2's selftest PASSED while its defect was live
    because its synthetic log did not carry the `trapFpe:` banner every real log
    carries, so the fixture was cleaner than anything the solver has ever
    produced.  This control therefore runs on the birth record THIS INSTRUMENT
    ACTUALLY WROTE, in memory, never rewriting it on disk:

      limb 1, NEGATIVE - a record with one REQUIRED gate REMOVED must REFUSE;
      limb 2, POSITIVE - the intact record must PROCEED to a verdict.

    A control carrying only limb 2 certifies nothing: a function that never
    refuses passes it.
    """
    path = require_readable_json(birth_record_path, "D4-CONTROL-RECORD",
                                 "the birth record the D4 control reads")
    record = P.load_birth_record(path)          # verifies the record's OWN hash
    P.require(all(g in record for g in REQUIRED_B_GATES), "D4-CONTROL-RECORD",
              f"{path} does not carry all of {list(REQUIRED_B_GATES)}, so it "
              f"cannot serve as the positive limb")

    limbs = {}
    for gate in REQUIRED_B_GATES:
        short = {k: v for k, v in record.items() if k != gate}
        try:
            aggregate_required(short, REQUIRED_B_GATES, "B-GATE-SET",
                               "the item")
            limbs[gate] = dict(removed=gate, refused=False, code=None,
                               verdict="GATE FAIL",
                               reason=f"removing {gate} did NOT refuse; a "
                                      f"missing gate was silently omitted")
        except SystemExit as ex:
            limbs[gate] = dict(removed=gate, refused=bool(ex.code == 2),
                               code=ex.code,
                               verdict="PASS" if ex.code == 2 else "GATE FAIL")
    negative_ok = all(v["refused"] for v in limbs.values())

    positive_v, per = aggregate_required(record, REQUIRED_B_GATES,
                                         "B-GATE-SET", "the item")
    rep = dict(
        control="D4", record=path, record_producer=os.path.abspath(__file__),
        record_producer_note="the bytes this control reads were written by "
                             "grade_r4b_ib.py's own --birth-only run on real "
                             "producer artefacts, NOT by a test harness "
                             "(sec. 2j.2, L-402)",
        required_gates=list(REQUIRED_B_GATES),
        negative_limb=dict(per_removed_gate=limbs,
                           all_removals_refused=negative_ok,
                           verdict="PASS" if negative_ok else "GATE FAIL",
                           rule="removing ANY ONE required gate must REFUSE "
                                "(exit 2), never aggregate over what remains"),
        positive_limb=dict(intact_record_verdict=positive_v,
                           per_gate=per, proceeded=True, verdict="PASS",
                           rule="the intact record must PROCEED to a verdict; "
                                "a refuser that refuses always certifies "
                                "nothing"),
        both_halves=True,
        at=P.utcnow())
    rep["verdict"] = "PASS" if negative_ok else "GATE FAIL"
    if out_path:
        P.write_json(guard_ib_root(out_path), rep)
    return rep


# --------------------------------------------------------------- selftest
def _selftest():
    import tempfile
    ok = []

    def check(name, cond, detail=""):
        ok.append((name, bool(cond), detail))

    def refused(fn, want=2):
        try:
            fn()
            return False, "did not refuse"
        except SystemExit as ex:
            return ex.code == want, f"code={ex.code}"

    src = open(os.path.abspath(__file__)).read()
    tree = ast.parse(src)
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    check("zero_ast_assert_nodes", n_assert == 0, f"count={n_assert}")

    # the process-termination sweep over this file's own bytes, two-sided. The
    # ONE tolerated token is the frozen B5 clause NAME this file must name.
    verb = "k" + "ill"
    stripped = src.replace("never_" + verb + "s", "")
    check("no_process_termination_verbs", verb not in stripped)
    check("termination_sweep_sees_a_planted_verb",
          verb in (stripped + f"\nos.{verb}(pid, 9)\n"))

    check("vocab_is_the_six", P.VOCAB == ("PASS", "GATE REACHED", "GATE FAIL",
                                          "NOT A RESULT", "BLOCKED", "PENDING"))
    check("headlines_are_the_registered_five", len(HEADLINES) == 5
          and HEADLINES[1] == "GATE REACHED (PARTIAL)")
    check("cap_and_estimate_unmoved",
          ESTIMATE_CORE_MIN == 12.0 and CAP_CORE_MIN == 40.0,
          f"{ESTIMATE_CORE_MIN}/{CAP_CORE_MIN}")
    check("five_required_b_gates", REQUIRED_B_GATES
          == ("B1", "B2", "B3", "B4", "B5"))
    check("five_required_b5_clauses", len(REQUIRED_B5_CLAUSES) == 5)
    check("grid_is_twelve", len(P.SC.GRID) == 12, str(len(P.SC.GRID)))

    # the parent pin, both halves: it matches, and it can SEE a mismatch.
    try:
        require_parent_unmodified()
        check("parent_pin_matches", True)
    except SystemExit as ex:
        check("parent_pin_matches", False, f"code={ex.code}")
    saved = PINNED[PARENT_PATH]
    PINNED[PARENT_PATH] = "f" * 64
    c, d = refused(require_parent_unmodified)
    check("parent_pin_sees_a_planted_mismatch", c, d)
    PINNED[PARENT_PATH] = saved

    # ---- THE D4 TWO-LIMB CONTROL, the whole point of the successor.
    full = {g: dict(verdict="PASS") for g in REQUIRED_B_GATES}
    v, per = aggregate_required(full, REQUIRED_B_GATES, "T", "t")
    check("D4_positive_limb_all_present_proceeds",
          v == "PASS" and len(per) == 5, f"{v} {len(per)}")
    for gate in REQUIRED_B_GATES:
        short = {k: x for k, x in full.items() if k != gate}
        c, d = refused(lambda s=short: aggregate_required(
            s, REQUIRED_B_GATES, "T", "t"))
        check(f"D4_negative_limb_missing_{gate}_refuses", c, d)
    c, d = refused(lambda: aggregate_required({}, REQUIRED_B_GATES, "T", "t"))
    check("D4_empty_record_refuses_not_passes", c, d)
    one_fail = dict(full, B3=dict(verdict="GATE FAIL"))
    v2, _ = aggregate_required(one_fail, REQUIRED_B_GATES, "T", "t")
    check("D4_aggregation_is_one_way_down", v2 == "GATE FAIL", v2)
    c, d = refused(lambda: aggregate_required(
        dict(full, B4=dict(verdict="roughly converged")),
        REQUIRED_B_GATES, "T", "t"))
    check("D4_refuses_a_verdict_outside_the_vocabulary", c, d)

    # the B5 clause-set exactness guard (D3/D4 at the call site).
    good_rep = {c2: dict(verdict="PASS") for c2 in REQUIRED_B5_CLAUSES}
    v3, _ = aggregate_required(good_rep, REQUIRED_B5_CLAUSES, "T", "B5")
    check("B5_full_clause_set_aggregates", v3 == "PASS", v3)
    thin = {c2: dict(verdict="PASS") for c2 in REQUIRED_B5_CLAUSES
            if c2 != "drive_with_noop_solver"}
    c, d = refused(lambda: aggregate_required(
        thin, REQUIRED_B5_CLAUSES, "T", "B5"))
    check("B5_missing_drive_clause_refuses", c, d)
    c, d = refused(lambda: b5_required(IB_ROOT, None))
    check("D3_refusal_B5_DRIVE_ABSENT_on_no_case_tree", c, d)
    c, d = refused(lambda: b5_required(IB_ROOT, "/nonexistent/case/pair"))
    check("D3_refusal_B5_DRIVE_ABSENT_on_absent_case_tree", c, d)

    # ---- THE D1 REPAIR, both halves.
    with tempfile.TemporaryDirectory() as td:
        good = os.path.join(td, "MODEL.json")
        json.dump({"a": 1}, open(good, "w"))
        try:
            require_readable_json(good, "T", "t")
            check("D1_positive_limb_readable_json_proceeds", True)
        except SystemExit as ex:
            check("D1_positive_limb_readable_json_proceeds", False,
                  f"code={ex.code}")
        c, d = refused(lambda: require_readable_json(
            os.path.join(td, "NO_SUCH.json"), "T", "t"))
        check("D1_negative_limb_absent_model_refuses", c, d)
        empty = os.path.join(td, "empty.json")
        open(empty, "w").close()
        c, d = refused(lambda: require_readable_json(empty, "T", "t"))
        check("D1_empty_model_refuses", c, d)
        corrupt = os.path.join(td, "corrupt.json")
        open(corrupt, "w").write("{not json")
        c, d = refused(lambda: require_readable_json(corrupt, "T", "t"))
        check("D1_unparseable_model_refuses", c, d)
        c, d = refused(lambda: require_readable_file("", "T", "t"))
        check("D1_empty_path_refuses", c, d)

    # ---- the write guards, both halves.
    c, d = refused(lambda: guard_ib_root(os.path.join(SOLVE_ROOT, "x")))
    check("solve_root_guard", c, d)
    c, d = refused(lambda: guard_ib_root(
        os.path.join(R4B_I_INSTRUMENT_ROOT, "_dev", "x")))
    check("R4b_I_root_guard_refuses_the_frozen_evidence_root", c, d)
    try:
        guard_ib_root(os.path.join(IB_ROOT, "birth"))
        check("ib_root_is_permitted", True)
    except SystemExit as ex:
        check("ib_root_is_permitted", False, f"code={ex.code}")
    check("ib_root_is_not_r4b_i_root",
          os.path.abspath(IB_ROOT) != os.path.abspath(R4B_I_INSTRUMENT_ROOT))

    # ---- both_halves_guard is ONE-WAY.
    check("both_halves_pass_two_sided_stays_PASS",
          both_halves_guard(dict(verdict="PASS", both_halves=True)) == "PASS")
    check("both_halves_pass_one_sided_falls_to_GATE_FAIL",
          both_halves_guard(dict(verdict="PASS", both_halves=False))
          == "GATE FAIL")
    check("both_halves_never_lifts_a_PENDING",
          both_halves_guard(dict(verdict="PENDING", both_halves=False))
          == "PENDING")

    # ---- sec. 5.6's mapping table, every row.
    allp = {g: "PASS" for g in REQUIRED_B_GATES}
    noctl = {}
    h, _ = headline(allp, noctl, 1.0)
    check("headline_all_pass_is_GATE_REACHED", h == "GATE REACHED", h)
    h, _ = headline(dict(allp, B4="GATE FAIL"), noctl, 1.0)
    check("headline_any_gate_fail_is_GATE_FAIL", h == "GATE FAIL", h)
    h, _ = headline(allp, noctl, CAP_CORE_MIN)
    check("headline_at_cap_is_BLOCKED", h == "BLOCKED", h)
    h, _ = headline(dict(allp, B4="GATE FAIL"), noctl, CAP_CORE_MIN)
    check("headline_cap_outranks_gate_fail", h == "BLOCKED", h)
    carve = {"G0d": dict(verdict="PENDING", pending_path="/nonexistent")}
    h, why = headline(dict(allp, B2="GATE FAIL"), carve, 1.0)
    check("headline_carve_out_only_is_GATE_REACHED_PARTIAL",
          h == "GATE REACHED (PARTIAL)" and "G4" in why, h)
    h, _ = headline(dict(allp, B2="GATE FAIL", B5="GATE FAIL"), carve, 1.0)
    check("headline_carve_out_plus_another_shortfall_is_GATE_FAIL",
          h == "GATE FAIL", h)
    check("every_headline_is_registered",
          all(headline(g, c2, m)[0] in HEADLINES
              for g, c2, m in ((allp, noctl, 1.0),
                               (dict(allp, B1="GATE FAIL"), noctl, 1.0),
                               (allp, noctl, CAP_CORE_MIN),
                               (dict(allp, B2="GATE FAIL"), carve, 1.0))))

    # ---- the criteria are the PARENT's, not re-decided here.
    check("B1_criterion_is_the_imported_function",
          P.b1_existence_and_refusals.__module__ == "grade_r4b")
    check("B5_criterion_is_the_imported_function",
          P.b5_runner.__module__ == "grade_r4b")
    check("grade_and_its_narrow_sigFpe_form_are_imported",
          P.grade.__module__ == "grade_r4b"
          and "sigFpe::sigHandler" in open(PARENT_PATH).read())
    # L-396/D548: the broad substring is a CONSTANT, not a detector - OpenFOAM
    # writes `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).`
    # at line 18 of EVERY log, so it fired on 63 of 70 real logs, 57 with a
    # clean `End` line, and it cost G1 its 127.08 core-min verdict. It may
    # appear in PROSE explaining that; it may never appear on an EXECUTABLE
    # line. Docstring lines are excluded mechanically, not by eye.
    doc_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)) and ast.get_docstring(node, False):
            d = node.body[0]
            doc_lines.update(range(d.lineno, (d.end_lineno or d.lineno) + 1))
    broad = "Floating point " + "exception"

    def broad_on_code_lines(text):
        return [i for i, ln in enumerate(text.split("\n"), 1)
                if broad in ln and i not in doc_lines
                and not ln.lstrip().startswith("#")]
    check("broad_fpe_substring_on_no_executable_line",
          not broad_on_code_lines(src), str(broad_on_code_lines(src)))
    planted = src + f'\nif "{broad}" in log: ok = False\n'
    check("broad_fpe_sweep_sees_a_planted_executable_use",
          bool(broad_on_code_lines(planted)))

    bad = [n for n, c2, _ in ok if not c2]
    for n, c2, d2 in ok:
        print(f"  [{'ok ' if c2 else 'FAIL'}] {n} {d2}")
    print(f"grade_r4b_ib.py --selftest: {len(ok) - len(bad)}/{len(ok)} "
          f"(optimize={sys.flags.optimize})")
    if bad:
        sys.stderr.write(f"SELFTEST FAILED: {bad}\n")
        return 1
    return 0


# ------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=IB_ROOT)
    ap.add_argument("--birth-record", default=BIRTH_RECORD)
    ap.add_argument("--coverage", default=REAL_COVERAGE_MD)
    ap.add_argument("--bijdelta", default="")
    ap.add_argument("--birth-only", action="store_true",
                    help="run the two-sided birth suite B1-B5 and write the "
                         "birth record; grade nothing")
    ap.add_argument("--d4-control", action="store_true",
                    help="run the two-limb D4 control on a REAL birth record")
    ap.add_argument("--d4-out", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()

    if a.d4_control:
        rep = d4_control(a.birth_record, a.d4_out or None)
        print(f"D4 control {rep['verdict']}  "
              f"(negative {rep['negative_limb']['verdict']}, "
              f"positive {rep['positive_limb']['verdict']})")
        for g, limb in rep["negative_limb"]["per_removed_gate"].items():
            print(f"  without {g}: refused={limb['refused']} "
                  f"code={limb['code']}")
        if a.d4_out:
            print(f"  -> {a.d4_out}")
        return 0 if rep["verdict"] == "PASS" else 1

    if a.birth_only:
        t0 = time.time()
        rec = run_birth(a.root, coverage_md=a.coverage,
                        bijdelta=a.bijdelta or None, started=t0)
        payload = P.write_birth_record(rec, guard_ib_root(a.birth_record))
        for g in REQUIRED_B_GATES:
            print(f"{g} {rec[g]['verdict']}")
        print(f"item verdict: {rec['item_verdict']}")
        print(f"HEADLINE: {rec['headline']}")
        print(f"  {rec['headline_reason']}")
        print(f"cost: {rec['cost']['core_minutes']} core-min "
              f"(estimate {ESTIMATE_CORE_MIN}, cap {CAP_CORE_MIN})")
        print(f"birth record -> {a.birth_record}")
        print(f"record_sha256 = {payload['record_sha256']}")
        return 0 if rec["headline"] in ("GATE REACHED",
                                        "GATE REACHED (PARTIAL)") else 1

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
