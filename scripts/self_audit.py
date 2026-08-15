#!/usr/bin/env python3
"""Rolling re-verification of published claims against primary evidence.

The audit that caught wall.json and the memory-exponent error, made into a
scheduled process instead of luck. Every check below re-derives a published
number from the raw artifact that number came from, and fails loudly when the
two disagree. Nothing here writes to any published surface: this script
reports, it never repairs. Correcting a surface is a human decision.

Run weekly:

    python3 scripts/self_audit.py            # human-readable report
    python3 scripts/self_audit.py --json     # machine-readable, for a hook
    python3 scripts/self_audit.py --quiet    # only FAIL and WARN lines

Exit status is three-valued (2026-08-15, D118): 0 when every check that ran
passed, 1 when any check FAILs, and 3 when no check FAILs but at least one
returned UNKNOWN -- a check that could not run against its evidence. UNKNOWN is
not a softer FAIL and it is not a pass: it is a statement about the instrument
rather than about the lab, and it must not exit 0 beside the passes. A cron
entry or a CI step can gate on any of the three. The weekly schedule is one
line and it is
not installed by this file, because installing a timer is a change to the box
and belongs to whoever owns the box:

    0 6 * * 1 cd /home/ubuntu/Certonomous && python3 scripts/self_audit.py \
        > demo-output/website/audit/self_audit_$(date +\\%Y\\%m\\%d).txt 2>&1

WHAT THIS IS AND IS NOT. It is a review aid. It names what it found and the
reason the check exists, and a human decides. It never edits a surface, and it
never will: a script that quietly corrects the record is a script that can
quietly corrupt it, and the whole point of the exercise is that a published
number changed only where somebody chose to change it.

TUNING. False positives are cheap and false negatives are not, and every
check here is tuned on that asymmetry. A false positive costs one reading. A
false negative costs a published number that nobody rechecks, which is how
every defect this file looks for got onto a surface in the first place. So a
check that is unsure reports, and says why it is unsure.

Adding a check: write a function that returns a Result, and list it in CHECKS.
A check must read primary evidence (a ledger row, a solver log, a raw
coefficient file) and compare it against a published surface. A check that
compares two published surfaces to each other is a consistency check, not a
verification, and must say so in its name.

The checks below fall into two rounds. The first ten came from the audit that
caught `wall.json` and the memory exponent. The second ten, added 2026-07-31,
each encode a defect that was caught once by hand, by somebody looking at
something else: a gate table row whose cited transcript no longer supports it,
a credential wall that would change on rebuild, a generator holding published
numbers as hard-coded constants, an FD grade against a retired band, a
statistical caption on a value no statistical procedure produced, a caller
trusting a band its own flag calls non-conclusive, a worker fleet declared on
a path that dispatches nothing, and a governed threshold restated as a literal.

One check here does NOT compare a published number to its evidence, and says
so rather than pretending otherwise: `check_bundle_drift` compares the shipped
laptop bundle to the tree it was built from. It is a consistency check between
two copies of the same code, in the sense the paragraph above defines, and it
earns its place because the bundle is the only copy of this code that leaves
the box and it went 32 commits behind with nothing noticing. Since 2026-08-15
it reads `dist/certonomous-demo.zip`, which is TRACKED, and not the gitignored
directory beside it: a verification whose reference is gitignored expires the
moment it is made, because nobody can ever re-derive what it saw (D118).

WHAT EACH CHECK IS ACTUALLY TESTING, and why the distinction is not pedantry.
`check_wall_credentials_vs_results` re-derives every credential through
`lab.displayed_credential`, which is the same function `sdk/scripts/
build_wall.py` calls to write the card in the first place. A defect inside
that function is therefore identical on both sides of the comparison and reads
as agreement. That is not hypothetical: on 2026-08-01 the Ahmed 25 degree row
published its value on frontal area and its envelope on planform, understating
the band by the whole 3.586 area ratio, and this check reported PASS before the
fix and PASS after it. The check is worth having -- it measures drift between a
surface and the code that writes it, and the wall is rebuilt by hand -- but
drift is not correctness, and a check nobody can fail should be visible as one.

So every check now declares, in `BASIS` below, what it tests, what it catches
and what it is blind to, and `check_every_check_states_its_basis` enforces the
declaration: a GENERATOR check must name the function it shares with the
producer, and that function must actually appear in both files. The basis rides
on every report line and in the JSON, so a PASS says which kind of PASS it is.
"""

from __future__ import annotations

import _io
import argparse
import ast
import builtins
import functools
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field, asdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WEB = REPO / "demo-output" / "website"
LEDGER = WEB / "mega-batch" / "ledger.jsonl"
WALL = WEB / "wall" / "wall.json"

# A ledger row longer than this is an infrastructure stall, not solver cost.
# Justification is measured, not assumed: the six rows above this threshold
# land in two tight wall-clock clusters and are shared across independent
# solver families, which no per-solver cost mechanism can produce. See
# check_ledger_stalls.
STALL_SECONDS = 3600.0

#: UNKNOWN added 2026-08-15 (D118). A check that could not run is not a check
#: that passed, and WARN was the wrong home for it: `scripts/lab_check.py`
#: records at its own line 229 that self_audit "exits non-zero only on FAIL --
#: so an OFF detector reddens nothing here" (docket D78). UNKNOWN exits 3,
#: which lab_check's EXIT_CONTRACT already maps to UNKNOWN, and it is tallied
#: beside the others so a run cannot lose it silently.
PASS, WARN, FAIL, INFO, UNKNOWN = "PASS", "WARN", "FAIL", "INFO", "UNKNOWN"


@dataclass
class Result:
    name: str
    status: str
    summary: str
    detail: list[str] = field(default_factory=list)


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - a missing surface is a finding
        return {"__error__": f"{type(exc).__name__}: {exc}"}


def _rel(path: Path) -> str:
    """A path as the repository names it, for a report line."""
    try:
        return str(Path(path).resolve().relative_to(REPO))
    except (ValueError, OSError):
        return str(path)


# --------------------------------------------------------------------------
# THE EMPTY SET IS NOT AGREEMENT (defect class B1)
# --------------------------------------------------------------------------
#
# THE DEFECT, measured 2026-08-15 on this file. `check_ledger_stalls` iterated
# `_iter_ledger()`, which returns immediately when the gitignored ledger is
# absent, fell through to its `if not stalls` branch and returned
#
#     [PASS] ledger stall contamination  no row exceeds the stall threshold
#
# having read ZERO ROWS. With the ledger on disk the same function returns WARN
# on six stall rows carrying 11.3% of published core-hours. So the verdict that
# reads cleanest was the one produced by reading nothing, which is the exact
# inversion this lab calls defect class B1: a silence that reads as success
# where it costs most.
#
# THE RULE, applied uniformly below. **A check's verdict is a statement about
# what it examined. A check that examined nothing returns UNKNOWN and names
# what it could not read.** It does not return PASS, because PASS asserts that
# evidence was read and was clean, and it does not return FAIL, because FAIL
# asserts a defect in the record and a check with no evidence cannot tell a
# deleted artifact from one that was never written on this box.
#
# TWO DELIBERATE EXCEPTIONS, enumerated here so they are exceptions and not
# oversights. `check_gate_table_vs_transcripts` and `check_register_group_counts`
# FAIL when their file is missing, because that file is the PUBLISHED SURFACE
# the check exists to police rather than the evidence it polices it with, and
# no other check owns its existence: a nine-act gate table gone from the tree
# is a finding, not an instrument problem. The distinction is SUBJECT versus
# EVIDENCE. `check_wall_counters_vs_ledger` sits on both sides of it and is
# written that way: wall.json absent is FAIL (subject), ledger absent is
# UNKNOWN (evidence).
#
# The precedent is `check_bundle_drift`, repaired at e01dfdf6 (D118), which
# returns UNKNOWN and not PASS on a missing archive with the same reasoning.

def _no_evidence(name: str, summary: str, sources,
                 detail: list[str] | None = None) -> Result:
    """The UNKNOWN a check returns when its evidence was not there to read.

    Every caller reaches this from the branch that used to return PASS on an
    empty sweep. The closing lines are uniform on purpose: a reader who meets
    one of these should not have to work out, check by check, whether the
    silence means clean or means blind.
    """
    named = [s if isinstance(s, str) else _rel(s) for s in sources]
    return Result(
        name, UNKNOWN, summary,
        (detail or [])
        + [f"not read: {s}" for s in named]
        + ["UNKNOWN and not PASS: this check examined nothing, and an empty "
           "sweep is not agreement (defect class B1). It exits 3, which "
           "scripts/lab_check.py's EXIT_CONTRACT reads as UNKNOWN and treats "
           "as blocking."])


# THE SECOND RESIDUAL (D175), measured 2026-08-15 by execution. The sweep
# above caught SOURCE ABSENCE. It did not catch EMPTY SELECTION, which is the
# same silence one step later: the source is on disk, it is readable, it is not
# empty, and the check's own selector picks nothing out of it. Eighteen checks
# returned PASS that way when driven with a real non-empty source -- not nine,
# which is what D174 filed; the eleven it did not name are the ones sharing
# `_py_corpus` and `_stored_studies`, whose guards cover an EMPTY corpus and
# not a corpus that fails to select. The worst was
#
#     [PASS] closure entry of record  the wall quotes the current entry of record
#
# with `wall.json` repointed at a path that does not exist.
#
# THE TWO CASES ARE DIFFERENT FAILURES AND THEY HAVE DIFFERENT REMEDIES, so
# they say different things. "I could not read the source" is fixed by putting
# the source back -- build the bundle, run the batch, restore the mount. "I
# read the source and my selector matched nothing in it" is fixed by looking at
# the SELECTOR, because a corpus that is present and yields nothing is either a
# corpus that genuinely holds no instance or a pattern that has stopped
# matching, and only reading the pattern tells you which. Collapsing them into
# one sentence -- which one shared `_no_evidence` would have done -- hands the
# reader the wrong repair half the time.

def _no_selection(name: str, summary: str, sources, selector: str,
                  detail: list[str] | None = None) -> Result:
    """The UNKNOWN a check returns when it READ its source and selected nothing.

    `sources` are named as READ, not as missing -- that is the whole difference
    from `_no_evidence`, and the closing lines say which of the two situations
    the reader is in so the remedy is not guessed.
    """
    named = [s if isinstance(s, str) else _rel(s) for s in sources]
    return Result(
        name, UNKNOWN, summary,
        (detail or [])
        + [f"read, and not empty: {s}" for s in named]
        + [f"selector that matched nothing: {selector}",
           "UNKNOWN and not PASS: the source was FINE and this check's own "
           "selector picked nothing out of it, which is not the same failure "
           "as an unreadable source (see _no_evidence) and does not have the "
           "same remedy -- read the SELECTOR, because a present corpus that "
           "yields no instance is either a corpus with no instance in it or a "
           "pattern that has stopped matching, and the verdict cannot tell "
           "those apart. It exits 3, which scripts/lab_check.py's "
           "EXIT_CONTRACT reads as UNKNOWN and treats as blocking."])


def _iter_ledger():
    """Yield (line_number, row_or_None). A torn row yields None so integrity
    checks can count it rather than crash on it."""
    if not LEDGER.exists():
        return
    with LEDGER.open(encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield number, json.loads(line)
            except Exception:  # noqa: BLE001
                yield number, None


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

# THE SETTLED VERDICT ON AN ABSENT LEDGER, and why it is UNKNOWN in BOTH of
# the two checks below rather than whichever one was edited first.
#
# Until 2026-08-15 these siblings read the same nothing in opposite directions:
# `check_ledger_integrity` returned FAIL on an absent ledger and
# `check_ledger_stalls` returned PASS. Both were wrong, in the two available
# directions.
#
# The ledger is gitignored (`.gitignore:25`) and is written by the mega-batch
# runner. It is absent by design on a fresh clone, in the laptop bundle, and on
# any box that has not run the batch. Its absence is therefore a fact about
# THIS BOX and not about the record, and neither a defect (FAIL) nor a clean
# reading (PASS) can be inferred from it.
#
# WHAT THE FAIL WAS STANDING IN FOR, and why dropping it loses no coverage.
# The case worth catching is a published counter with no ledger under it. That
# case belongs to `check_wall_counters_vs_ledger` and it was measured on
# 2026-08-15 with the ledger hidden and wall.json left in place:
#
#     [FAIL] wall counters vs ledger  3 counter(s) disagree with the ledger
#            - missions_run: published 208102, ledger says 0
#
# So the loud finding survives, in the check that owns the published number,
# while the check that owns the ledger's health says the true thing: it could
# not read it. That check now guards the same absence and returns UNKNOWN for
# it, so a missing ledger cannot be reported as three disagreeing counters.

def check_ledger_integrity() -> Result:
    """Every ledger line parses. A torn line is silent data loss."""
    torn, total = [], 0
    for number, row in _iter_ledger():
        total += 1
        if row is None:
            torn.append(number)
    if not total:
        return _no_evidence(
            "ledger integrity",
            "the ledger is absent or holds no rows; no line was read",
            [LEDGER],
            ["the ledger is gitignored (.gitignore:25) and written by the "
             "mega-batch runner, so its absence is a fact about this box and "
             "not about the record; a published counter with no ledger under "
             "it is check_wall_counters_vs_ledger's finding and it FAILs "
             "there"])
    if torn:
        return Result(
            "ledger integrity", WARN,
            f"{len(torn)} of {total} ledger lines do not parse",
            [f"line {n} is truncated or malformed" for n in torn[:10]]
            + ["a torn line is an interrupted write; the row it held is lost"])
    return Result("ledger integrity", PASS, f"{total} ledger lines all parse")


def check_wall_counters_vs_ledger() -> Result:
    """wall.json's headline counters must re-derive from the ledger itself."""
    wall = _load_json(WALL)
    if "__error__" in wall:
        return Result("wall counters vs ledger", FAIL,
                      f"wall.json unreadable: {wall['__error__']}")
    counters = wall.get("counters", {})
    detail_block = counters.get("detail", {})
    per_solver_published = detail_block.get("per_solver", {})

    ok_rows = failed_rows = 0
    ok_seconds = 0.0
    rows = 0
    per_solver: dict[str, list] = {}
    for _, row in _iter_ledger():
        rows += 1
        if row is None:
            continue
        seconds = float(row.get("wall_seconds") or 0.0)
        solver = row.get("solver") or "unknown"
        if row.get("ok"):
            # The published per_solver block counts SUCCEEDED rows only —
            # lab_stats.ledger_summary builds it from ok_rows — so the check
            # must too. Until 2026-08-01 this accumulator ran over every row
            # and the check failed on all 91 not-ok rows every time, on three
            # solvers, while each published figure was in fact exact.
            entry = per_solver.setdefault(solver, [0, 0.0])
            entry[0] += 1
            entry[1] += seconds
            ok_rows += 1
            ok_seconds += seconds
        else:
            failed_rows += 1

    # SUBJECT versus EVIDENCE, both of them in this one check. wall.json is the
    # subject and its absence is the FAIL above. The ledger is the evidence,
    # and with no ledger every counter below "disagrees" with a zero this
    # function invented -- three FAIL lines diagnosing the wall for a file that
    # is not there. That is a misdiagnosis, not a finding.
    if not rows:
        return _no_evidence(
            "wall counters vs ledger",
            "the ledger is absent or holds no rows; no counter could be "
            "re-derived",
            [LEDGER],
            [f"wall.json is readable and publishes "
             f"missions_run={counters.get('missions_run')}; nothing here "
             f"contradicts it, because nothing was measured against it"])

    problems, notes = [], []

    def compare(label, published, measured, tolerance=0.0):
        if published is None:
            problems.append(f"{label}: absent from wall.json")
            return
        if abs(float(published) - float(measured)) > tolerance:
            problems.append(
                f"{label}: published {published}, ledger says {measured}")
        else:
            notes.append(f"{label}: {measured} confirmed")

    compare("missions_run", counters.get("missions_run"), ok_rows)
    compare("ledger_failed", detail_block.get("ledger_failed"), failed_rows)
    compare("solver_core_hours", counters.get("solver_core_hours"),
            round(ok_seconds / 3600.0, 3), tolerance=0.002)

    for solver, (count, seconds) in sorted(per_solver.items()):
        published = per_solver_published.get(solver)
        if published is None:
            problems.append(f"per_solver[{solver}]: absent from wall.json")
            continue
        if int(published.get("count", -1)) != count:
            problems.append(
                f"per_solver[{solver}].count: published "
                f"{published.get('count')}, ledger says {count}")
        if abs(float(published.get("wall_seconds", -1)) - seconds) > 0.2:
            problems.append(
                f"per_solver[{solver}].wall_seconds: published "
                f"{published.get('wall_seconds')}, ledger says {seconds:.1f}")

    if problems:
        return Result("wall counters vs ledger", FAIL,
                      f"{len(problems)} counter(s) disagree with the ledger",
                      problems)
    return Result("wall counters vs ledger", PASS,
                  "every published counter re-derives from the ledger", notes)


def check_ledger_stalls() -> Result:
    """Infrastructure stalls must not be counted as solver cost.

    A stall is identified, not assumed: rows above STALL_SECONDS are reported
    with their timestamps so the clustering that proves they are shared
    infrastructure events (not per-solver cost) is visible in the output.
    """
    stalls = []
    ok_seconds = 0.0
    rows = 0
    for _, row in _iter_ledger():
        rows += 1
        if row is None:
            continue
        seconds = float(row.get("wall_seconds") or 0.0)
        if row.get("ok"):
            ok_seconds += seconds
        if seconds > STALL_SECONDS:
            stalls.append((row.get("solver"), seconds, row.get("timestamp")))
    # The rows counter, and not `stalls`, is what separates "I read the ledger
    # and nothing in it stalled" from "there was no ledger to read". Before
    # 2026-08-15 the two shared one branch and both printed the clean sentence.
    if not rows:
        return _no_evidence(
            "ledger stall contamination",
            "the ledger is absent or holds no rows; no wall time was read",
            [LEDGER],
            ["the threshold was applied to zero rows, so this says nothing "
             "about published solver_core_hours; see the settled verdict "
             "above check_ledger_integrity"])
    if not stalls:
        return Result("ledger stall contamination", PASS,
                      f"no row of {rows} exceeds the stall threshold "
                      f"({STALL_SECONDS:.0f} s)")
    stall_seconds = sum(s for _, s, _ in stalls)
    share = 100.0 * stall_seconds / ok_seconds if ok_seconds else 0.0
    families = {solver for solver, _, _ in stalls}
    detail = [f"{solver}: {seconds:.0f} s at {stamp}"
              for solver, seconds, stamp in sorted(stalls, key=lambda r: r[2])]
    detail.append(
        f"{len(stalls)} rows across {len(families)} independent solver "
        f"families share these wall times, which no per-solver cost mechanism "
        f"explains; they are host stalls recorded as normal runs")
    detail.append(
        f"published solver_core_hours carries {stall_seconds/3600:.2f} "
        f"core-hours of stall ({share:.1f}% of the headline); the cleaned "
        f"figure is {(ok_seconds-stall_seconds)/3600:.2f} core-hours")
    return Result("ledger stall contamination", WARN,
                  f"{len(stalls)} stall rows are counted as solver cost "
                  f"({share:.1f}% of published core-hours)", detail)


# --------------------------------------------------------------------------
# The closure figures, DERIVED rather than typed
# --------------------------------------------------------------------------
#
# WHAT WENT WRONG, AND WHY IT WENT WRONG SILENTLY. Two facts about the closure
# entry used to sit in this file as literals: the best-on-board count ("four of
# eight") and the interval on P(rank 1) ("2-100% at 95%"). Both were true when
# they were typed. Both were false by 2026-08-11, when the public board went
# from four entries to six, and NEITHER went red -- because a guard that holds
# a copy of the fact it guards cannot report that the fact moved. It can only
# report that a SURFACE moved away from its copy, which is the same sentence
# with the blame reversed. So on 2026-08-11 this file was simultaneously
# demanding that surfaces say "four of eight" and certifying a credentials wall
# that said it, when the count against the live board was two -- and the
# rank-claim guard was insisting on an interval that no current surface states.
#
# L-79: a hard-coded fact inside an instrument goes stale silently; a fact
# recomputed from a committed source cannot. So neither number is typed here
# any more. Every closure quantity this file needs is computed on each run out
# of files that are committed and are somebody else's output:
#
#   the live board   `sdk/scripts/probability_of_rank.py` LIVE_BOARD, read by
#                    AST literal rather than by import. An instrument should
#                    not need numpy installed to run, and should not execute
#                    the file it is auditing.
#   our per-case     `closure_challenge_round5_qcr.json`, the scoring call's
#                    own machine record.
#   which cases the  the same record, structurally: a declined case is one
#   gate declined    whose round-5 score EQUALS its RANS-identity floor,
#                    because the gate passed the organisers' own unmodified
#                    field through untouched. No prose is consulted for it.
#   the interval     `probability_of_rank_record.json`, the `--json` output of
#                    that same script.
#
# The interval is the one number that cannot be recomputed here: a 2,000 x
# 4,000 double bootstrap is minutes, and this file is meant to be cheap enough
# to run weekly from cron. So it is READ from a stored result -- and because a
# stored result is exactly the failure mode described above, it is read with a
# PROVENANCE CHECK. The board and the entry that record was computed against
# are compared against the board and the entry on disk now, and a mismatch is
# reported LOUDLY, as an instrument that has gone stale, instead of being
# enforced quietly. That is the difference between this arrangement and the
# literal it replaces: the literal could not know it was old.
_HERE = Path(__file__).resolve().parents[1]
_PROB_SCRIPT = _HERE / "sdk" / "scripts" / "probability_of_rank.py"
_PROB_RECORD = _HERE / "sdk" / "scripts" / "probability_of_rank_record.json"
_ENTRY_OF_RECORD = (_HERE / "demo-output" / "website"
                    / "closure_challenge_round5_qcr.json")


def _module_literal(path: Path, name: str):
    """The value of a module-level literal assignment, without importing.

    `ast.literal_eval` and not `exec`: reading a number out of a script is not
    a reason to run the script, and this keeps the audit independent of
    whatever the audited file imports.
    """
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise KeyError(f"{name} is not a module-level literal in {path.name}")


def _derive_closure_facts(board: dict, cases: list[str], entry: dict,
                          record: dict | None) -> dict:
    """The closure facts implied by these inputs. Pure, so it can be driven.

    Kept free of file access on purpose. The count this returns is the thing
    that used to be a literal, and a derivation that can only ever be run
    against the one true board on disk is not testable against anything: the
    suite drives this with synthetic boards to show the count follows the
    board and is not a constant wearing a function's clothes.

    `best`      cases where our number beats every entrant on the board.
    `declined`  cases the decline gate passed through as the organisers' own
                unmodified RANS field, identified by our round-5 score being
                equal to the RANS-identity floor for that case.
    `earned`    `best` minus `declined` -- the count belonging to our MODEL,
                which is the number the disclosure rule is actually about.
    """
    facts: dict = {"stale": [], "entries": len(board.get("entrants") or {}),
                   "cases": list(cases), "best": [], "declined": [],
                   "earned": [], "interval": None, "p_rank1": None,
                   "our_overall": None, "leader": None}
    result = entry.get("official_test_harness_result") or {}
    full = result.get("round5_per_case_full") or {}
    rounded = result.get("round5_per_case") or {}
    floor = result.get("rans_identity_floor_per_case") or {}
    entrants = board.get("entrants") or {}
    if not full or not entrants:
        facts["stale"].append(
            "the entry of record carries no round-5 per-case block, or the "
            "board carries no entrants; no closure fact could be derived")
        return facts

    missing = [c for c in cases if c not in full]
    if missing:
        facts["stale"].append(
            f"the entry of record is missing {len(missing)} of the "
            f"{len(cases)} scored cases: {', '.join(missing)}")
        return facts

    facts["our_overall"] = sum(full[c] for c in cases) / len(cases)
    facts["leader"] = min(
        entrants, key=lambda n: sum(entrants[n]) / len(entrants[n]))
    for index, case in enumerate(cases):
        ours = full[case]
        rivals = [values[index] for values in entrants.values()]
        if rivals and ours < min(rivals):
            facts["best"].append(case)
        # The floor is recorded to four places, so the identity is judged
        # there. MARGIN, stated rather than discovered later: two genuinely
        # different fields that agree to 1e-4 would read here as a decline.
        if case in floor and case in rounded and floor[case] == rounded[case]:
            facts["declined"].append(case)
    facts["earned"] = [c for c in facts["best"] if c not in facts["declined"]]

    if record is None or "__error__" in record:
        facts["stale"].append(
            f"{_PROB_RECORD.name} is missing or unreadable, so the interval on "
            f"P(rank 1) cannot be stated; regenerate it with "
            f"`python3 sdk/scripts/probability_of_rank.py --json {_PROB_RECORD}`")
        return facts

    frame = record.get("frame") or {}
    if frame.get("entries") != facts["entries"]:
        facts["stale"].append(
            f"{_PROB_RECORD.name} was computed against a "
            f"{frame.get('entries')}-entry board; the board in "
            f"{_PROB_SCRIPT.name} now carries {facts['entries']} entries")
    if frame.get("fetched") != board.get("fetched"):
        facts["stale"].append(
            f"{_PROB_RECORD.name} was computed against the board fetched "
            f"{frame.get('fetched')}; {_PROB_SCRIPT.name} now carries the "
            f"board fetched {board.get('fetched')}")
    if not isinstance(frame.get("our_overall"), (int, float)) \
            or abs(frame["our_overall"] - facts["our_overall"]) > 1e-12:
        facts["stale"].append(
            f"{_PROB_RECORD.name} was computed against an entry scoring "
            f"{frame.get('our_overall')}; the entry of record now scores "
            f"{facts['our_overall']}")
    if facts["stale"]:
        facts["stale"].append(
            "the interval below is therefore NOT current and no surface "
            "should be judged against it until the record is regenerated")
        return facts

    band = record.get("double95")
    if isinstance(band, list) and len(band) == 2:
        facts["interval"] = (round(100 * band[0]), round(100 * band[1]))
    if isinstance(record.get("p_rank1"), (int, float)):
        facts["p_rank1"] = round(100 * record["p_rank1"])
    return facts


@functools.lru_cache(maxsize=1)
def _closure_facts() -> dict:
    """`_derive_closure_facts` against the committed files. Never raises."""
    try:
        board = _module_literal(_PROB_SCRIPT, "LIVE_BOARD")
        cases = _module_literal(_PROB_SCRIPT, "CASES")
    except (OSError, SyntaxError, ValueError, KeyError) as exc:
        return {"stale": [f"the live board could not be read from "
                          f"{_PROB_SCRIPT.name}: {exc}"],
                "best": [], "declined": [], "earned": [], "cases": [],
                "entries": 0, "interval": None, "p_rank1": None,
                "our_overall": None, "leader": None}
    entry = _load_json(_ENTRY_OF_RECORD)
    if "__error__" in entry:
        entry = {}
    return _derive_closure_facts(board, cases, entry,
                                 _load_json(_PROB_RECORD))


def _rank_interval_phrase() -> str:
    """`0-97% at 95%`, or a phrase that says the instrument cannot say."""
    band = _closure_facts()["interval"]
    if band is None:
        return "its 95% interval (UNAVAILABLE: see the stale-record warning)"
    return f"{band[0]}-{band[1]}% at 95%"


# THE MARKUP DIALECTS AN INTERVAL IS WRITTEN IN HERE, and why there is a table.
#
# THE DEFECT (2026-08-12). `closure_challenge_report.tex` carries the current
# interval nine times, spelled the only way LaTeX spells it -- `0--97\%`, an
# en-dash written as two hyphens and a percent sign that must be escaped or it
# starts a comment. The pattern below read a SINGLE dash followed by a BARE
# `%`, so it found no interval at all in that file -- not the wrong one, none --
# and the guard failed the report for being CORRECT. `closure_challenge_round5_
# qcr.json` was failed the same way for writing `0-97 percent at 95 percent`,
# because JSON prose here spells the unit as a word.
#
# A FALSE FAULT IS WORSE THAN A MISS, which is why this is a table and not a
# widened pattern. A guard that fails compliant surfaces teaches its readers
# that red means nothing, and the cheapest way to silence it is to "fix" the
# surface that was right. But broadening until the red file goes green is the
# same mistake pointed the other way, so the dialects are ENUMERATED, each
# named, each separately exercised by the suite.
#
# The list is not invented. It is a census of every tracked surface and every
# archive member: the separators actually used to join the two ends of a range
# are the ASCII hyphen, the LaTeX `--`, and the Unicode dashes; the units
# actually used are `%`, LaTeX `\%`, and the word "percent"; and some surfaces
# put a percent sign on BOTH ends (`20%-94%`). The HTML entity spellings occur
# nowhere in this corpus today -- `&ndash;`, `&#8211;`, `&#37;` return zero hits
# -- and are handled anyway because the pages that would use them are generated,
# so the day one appears is not a day anybody edits this file. They are marked
# as unexercised-by-the-corpus so that is on the record rather than implied.
#
# DELIBERATELY NOT A DIALECT: the word "to". `0 to 97%` is a plausible way to
# write a range and this corpus never uses it, while `docket.json` does contain
# "830,000 to 970,000 cells" -- a string whose digits read as `0 to 97`.
# Accepting "to" would buy nothing and would put a coincidence one unit-word
# away from certifying a surface that states no interval at all.
_INTERVAL_DIALECTS = (
    # (name, pattern, canonical form, present in this corpus today)
    ("LaTeX escaped percent `\\%`",   r"\\%",                       "%", True),
    ("HTML percent entity",           r"&(?:#0*37|percnt);",        "%", False),
    ("the unit spelled as a word",    r"\s*\bper\s?cent(?:age)?\b", "%", True),
    ("HTML dash entity",              r"&(?:ndash|mdash|#0*8211|#0*8212|#0*45);",
                                                                    "-", False),
    ("LaTeX `--` en-dash / `---` em-dash", r"-{2,3}",               "-", True),
    ("Unicode dash or minus sign",    r"[‐-―−]",     "-", True),
)
_INTERVAL_NORMALISERS = tuple(
    (re.compile(pattern, re.I), canonical)
    for _name, pattern, canonical, _seen in _INTERVAL_DIALECTS)

# A pair of percentages joined by a dash, read AFTER the dialects above have
# been folded to one spelling. Parsed rather than matched against a literal, so
# a surface writing `0.2-96.9%` and a surface writing `0-97%` are read as the
# same interval and neither has to guess how this file rounds. The first
# percent sign is optional because `20%-94%` is a spelling this corpus uses.
_INTERVAL_PAIR = re.compile(
    r"(\d+(?:\.\d+)?)\s*%?\s*-\s*(\d+(?:\.\d+)?)\s*%")


def _canonical_interval_markup(text: str) -> str:
    """Fold the enumerated markup dialects onto one spelling of a range."""
    for pattern, canonical in _INTERVAL_NORMALISERS:
        text = pattern.sub(canonical, text)
    return text


def _states_the_interval(text: str) -> bool:
    """Does this text carry the CURRENT interval on P(rank 1)?

    Returns True when the instrument cannot say what the current interval is.
    That is deliberate and it is the safe direction: the alternative is to
    fault every compliant surface in the tree because a record went stale,
    which is the fastest way to get a guard switched off. The staleness is not
    swallowed -- `check_rank_claim_surfaces` reports it loudly in its own
    verdict, where it is a statement about the instrument and not about the
    surfaces.

    What it still cannot do, stated rather than discovered later: it reads the
    WHOLE text, so an interval inside a strikethrough counts. That is the
    tombstone hole this ladder found on `closure.html`, and it is closed at the
    surface -- by the pages carrying the live figure -- not here, because the
    strike markup differs per format and a wrong stripper would fail compliant
    files. The suite pins each repaired surface with its struck text removed.
    """
    band = _closure_facts()["interval"]
    if band is None:
        return True
    low, high = band
    return any(round(float(a)) == low and round(float(b)) == high
               for a, b in _INTERVAL_PAIR.findall(
                   _canonical_interval_markup(text)))


_COUNT_WORDS = {"zero": 0, "no": 0, "one": 1, "two": 2, "three": 3, "four": 4,
                "five": 5, "six": 6, "seven": 7, "eight": 8}
_BEST_COUNT = re.compile(
    r"\bbest\b[^.\n]{0,80}?\b(zero|no|one|two|three|four|five|six|seven|eight|\d+)"
    r"\s+of\s+(?:the\s+)?(?:eight|8)\b", re.I)
# The disclosure the count may not travel without, in any of the spellings the
# lab's own records use for it.
_BASELINE_CREDIT = re.compile(
    r"belongs to the baseline|belonging to our own model|"
    r"organisers'? own unmodified RANS|the credit there belongs", re.I)


def _best_on_board_faults(text: str) -> list[str]:
    """Where this text's best-on-board claim disagrees with the board.

    The count is not held here. It is derived, so this returns nothing at all
    on the day the board moves and the surfaces move with it, and returns the
    NEW number in its complaint on the day only the board moves.
    """
    facts = _closure_facts()
    if facts["stale"] or not facts["cases"]:
        return []
    best, earned = len(facts["best"]), len(facts["earned"])
    faults = []
    stated = [m for m in _BEST_COUNT.finditer(text)]
    for match in stated:
        raw = match.group(1).lower()
        value = _COUNT_WORDS.get(raw, int(raw) if raw.isdigit() else None)
        if value is not None and value != best:
            faults.append(
                f"our_entry states best-on-board {raw} of eight; against the "
                f"{facts['entries']}-entry board in {_PROB_SCRIPT.name} the "
                f"count is {best} of eight ({', '.join(facts['best']) or 'none'})")
    if stated and not _BASELINE_CREDIT.search(text):
        faults.append(
            f"our_entry states a best-on-board count without the disclosure "
            f"that {len(facts['declined'])} of those rows are the organisers' "
            f"own unmodified RANS field passed through by the decline gate "
            f"(SUBMISSION_DRAFT sec 4.7, the highest-priority disclosure)")
    if stated and earned == 0 and not re.search(
            r"\b(zero|none|no)\b[^.\n]{0,60}\bof\s+(?:the\s+)?(?:eight|8)\b",
            text, re.I):
        faults.append(
            f"our_entry states a best-on-board count of {best} without saying "
            f"that the count belonging to OUR MODEL is zero of eight: every "
            f"one of the {best} row(s) we lead on "
            f"({', '.join(facts['best'])}) is a row the decline gate passed "
            f"through as the organisers' own field")
    return faults


def check_closure_entry_of_record() -> Result:
    """The credentials wall must quote the closure entry of record, not a
    superseded round."""
    # THE WALL IS THIS CHECK'S SUBJECT, NOT ITS EVIDENCE, and until 2026-08-15
    # nothing here said so. `_load_json` returns `{"__error__": ...}`, every
    # `.get` chain below took its `or {}` branch, `published_score` came out
    # None and `published_text` came out the empty string, no guard fired on an
    # empty string, and the check returned
    #
    #     [PASS] closure entry of record  the wall quotes the current entry of
    #                                     record
    #
    # with `wall.json` REPOINTED AT A PATH THAT DOES NOT EXIST. That is the
    # cleanest sentence this check can print and it was produced by opening
    # nothing -- on the one check that owns the credentials wall's closure
    # claims. FAIL and not UNKNOWN, by the SUBJECT-versus-EVIDENCE rule stated
    # above `check_ledger_integrity`: the wall is the published surface this
    # check exists to police, its sibling `check_wall_counters_vs_ledger` FAILs
    # on the same absence, and the two must not read one missing file in
    # opposite directions again.
    wall = _load_json(WALL)
    if "__error__" in wall:
        return Result("closure entry of record", FAIL,
                      f"wall.json unreadable: {wall['__error__']}; the surface "
                      f"whose closure claims this check owns is not there",
                      [f"not read: {_rel(WALL)}",
                       "FAIL and not UNKNOWN: wall.json is this check's "
                       "SUBJECT and not its evidence (see the SUBJECT versus "
                       "EVIDENCE rule above check_ledger_integrity); "
                       "check_wall_counters_vs_ledger FAILs on the same "
                       "absence and these two siblings must not read one "
                       "missing file in opposite directions"])
    closure = ((wall.get("counters") or {}).get("research") or {}).get("closure") or {}
    # The entry of record is ROUND 5 since 2026-08-07 (commit 07a7fe9e). This
    # check was pinned to the round-3 file and so failed the wall for being
    # CORRECT: it reported "wall says 0.0566, the entry of record scores 0.0676".
    # Re-pinned by Ladder V Pass 2 (V6/V10, 2026-08-10). When a later round
    # lands, repoint this file -- a guard that cries wolf is worse than no
    # guard, because the cheapest way to silence it is to "fix" the surface
    # that was right.
    #
    # "and the counts below in the same commit" used to stand here, and that
    # instruction was the defect. The counts are DERIVED now (2026-08-12);
    # nothing below has to be remembered when the board moves, because nothing
    # below is written down. The one thing still hard-coded is the NAME of the
    # file opened on the next line, and BASIS says so.
    entry_path = WEB / "closure_challenge_round5_qcr.json"
    entry = _load_json(entry_path)
    if "__error__" in entry:
        # EVIDENCE, not subject: the entry of record is what the wall is graded
        # AGAINST. WARN was the wrong home for it -- lab_check does not block on
        # WARN, so a check that could not open its evidence read as a mild note
        # beside real findings (D118).
        return _no_evidence(
            "closure entry of record",
            f"the entry of record did not open ({entry['__error__']}), so the "
            f"wall was graded against nothing", [entry_path])

    published_score = closure.get("our_score")
    published_text = str(closure.get("our_entry") or "")
    # EMPTY SELECTION, distinct from the absence above. The wall opened and
    # parsed, and its closure block carries neither a score to compare nor an
    # entry sentence to read. Every guard below is a no-op on that, and the
    # PASS underneath them is a statement about a claim nobody made.
    if published_score is None and not published_text:
        return _no_selection(
            "closure entry of record",
            "the wall opened and its closure block states neither a score nor "
            "an entry sentence, so there was no claim to grade",
            [WALL, entry_path],
            "counters.research.closure.our_score and .our_entry",
            ["the wall itself is readable; what is missing is the CLAIM, and a "
             "wall making no closure claim is not a wall quoting the entry of "
             "record"])

    # The entry of record's own overall score, from its own file.
    current = None
    for key in ("round5_overall", "overall", "round3_gated_overall", "gated_overall"):
        if isinstance(entry.get(key), (int, float)):
            current = float(entry[key])
            break
    if current is None:
        stack = [entry]
        while stack and current is None:
            node = stack.pop()
            if isinstance(node, dict):
                for key, value in node.items():
                    if key.endswith("overall") and isinstance(value, (int, float)) \
                            and "round2" not in key and "round4" not in key \
                            and "floor" not in key:
                        current = float(value)
                        break
                    if isinstance(value, (dict, list)):
                        stack.append(value)
            elif isinstance(node, list):
                stack.extend(node)

    problems = []
    if current is not None and published_score is not None:
        # The wall publishes the score at its own precision (4 dp since round 5,
        # where the record carries full float precision). Compare at the wall's
        # precision: quoting 0.0566 for 0.056647191704213645 is quoting it, and
        # an exact-equality test here would fail the wall for rounding.
        dp = len(str(published_score).split(".")[-1]) if "." in str(published_score) else 0
        if abs(round(current, dp) - float(published_score)) > 10 ** -(dp + 3):
            problems.append(
                f"our_score: wall says {published_score}, the entry of record "
                f"scores {current} (compared at the wall's {dp} dp)")
    if re.search(r"\ba single\b.{0,40}scoring call", published_text, re.I):
        problems.append(
            "our_entry claims a single scoring call; the record documents six "
            "official calls (floor, rounds 1-5) -- the unit being counted is "
            "DISTINCT PREDICTION SETS SCORED, and the benchmark imposes no "
            "scoring-call limit of any kind")
    # The best-on-board count used to be asserted here as a literal -- "round 5
    # records four of eight" -- which made this guard the thing that had to be
    # remembered when the board moved, and it was not. It is derived now; see
    # `_best_on_board_faults` and the block above it.
    problems.extend(_best_on_board_faults(published_text))
    # A rank claim on the wall must carry its companion: the probability that
    # the placement survives case resampling, AND the interval, AND the pairs
    # that are not decided. Ladder V rung V8 as amended 2026-08-10 -- "a bare
    # 68% is a worse claim than none, because 68% sounds settled and eight
    # cases do not support settled". This guard exists because rung V15 found
    # the four external surfaces (this text among them) edited by the very
    # commit that adopted the rule and left non-compliant with it: a rule that
    # binds surfaces needs a check that reads a surface.
    if re.search(r"\brank 1\b", published_text, re.I):
        missing = []
        if "P(rank 1)" not in published_text:
            missing.append("P(rank 1)")
        if not _states_the_interval(published_text):
            missing.append(f"its {_rank_interval_phrase()} interval")
        if "not statistically decided" not in published_text:
            missing.append("the sweep token 'not statistically decided'")
        if missing:
            problems.append(
                "our_entry makes a rank claim without " + ", ".join(missing)
                + " (Ladder V rung V8 as amended 2026-08-10; the figure and "
                "its interval come from sdk/scripts/probability_of_rank.py, "
                "not from this file)")
    if problems:
        return Result("closure entry of record", FAIL,
                      f"{len(problems)} stale claim(s) on the credentials wall",
                      problems)
    return Result("closure entry of record", PASS,
                  "the wall quotes the current entry of record")


# --------------------------------------------------------------------------
# Rank claims, on every surface that makes one
# --------------------------------------------------------------------------
#
# THE DEFECT THIS EXISTS FOR. The rank-claim guard immediately above reads ONE
# string: `our_entry` on the credentials wall. The rule it enforces (Ladder V
# rung V8 as amended 2026-08-10) binds EVERY surface, internal or external.
# Four external surfaces were brought into compliance and were guarded by that
# one string; `closure.html` -- the most prominent page in the shipping bundle
# -- went on making three rank claims with no probability and no interval,
# because it was not on anybody's list.
#
# THE LIST WAS THE DEFECT. So the surface set below is not written down. It is
# SEARCHED FOR, over every tracked file and every member of every shipping
# archive, and whatever the search finds is the set. A surface added tomorrow
# is covered the day it makes a claim, and nobody has to remember to add it.
#
# Three patterns decide what a rank claim is, and they are stated here rather
# than tuned quietly:
#
#   _RANK_CLAIM     the assertive FORM of a placement -- "rank 1 of 5", "is
#                   rank 1", "P(rank 1)", "best overall number on the board".
#                   A bare mention of the string "rank 1" is not a claim: the
#                   deficit-to-rank-1 language in the proposals, and the
#                   priority-ordering rank 1 in RESULT_PRIORITY_CHARTER, are
#                   about a rank without asserting we hold one.
#   _RANK_BOARD     the claim must sit within _RANK_WINDOW characters of the
#                   closure benchmark. Without this, "rank 1" in a scheduler
#                   or a chart is a claim.
#   _RANK_HOMONYM   MPI rank 1, process rank 1, and the `w3-qcr-rank1` run
#                   directory. This one is an exclusion list and is named as
#                   such: it excludes HOMONYMS OF THE WORD, not surfaces. The
#                   run logs say "MPI_ABORT was invoked on rank 1"; that is a
#                   different sense of the same five characters.
#
# The companion test is deliberately per-file rather than per-claim, and the
# BASIS entry says so: one compliant paragraph clears every claim in its file.
# Judging distance from a claim to its companion needs a notion of "passage"
# that a regex does not have, and a wrong one would fail compliant surfaces,
# which is the fastest way to get a guard switched off.
_RANK_CLAIM = re.compile(
    r"P\(rank\s*1\)"
    r"|\brank[ \-]1 of \w+"
    r"|\brank[ \-]1\b(?=[^.\n]{0,80}?"
    r"(?:scored locally|on the board|on the published board|on the leaderboard))"
    r"|\b(?:is|are|was|were|be|sits at|stands at|holds|puts us at|leaves us "
    r"at|ranks)\s+(?:still\s+|now\s+|only\s+)?(?:at\s+)?rank[ \-]1\b"
    r"|(?:best|lowest) overall (?:number|score)?[^.\n]{0,40}?(?:board|leaderboard)",
    re.I)
_RANK_BOARD = re.compile(
    r"board|leaderboard|benchmark|closure challenge|entry of record|"
    r"scored locally|reissmann|deb9155|0\.0566|overall score", re.I)
_RANK_HOMONYM = re.compile(
    r"MPI|process(?:or)?\s+rank|\bPID\b|node ip-|[/\w]rank1|rank-1-", re.I)
_RANK_WINDOW = 300
_RANK_HOMONYM_WINDOW = 120
# Companions, per the V8 amendment: the figure, its interval, and the pairs.
# The interval is NOT a constant here. It was one -- `2-100%` -- and it went
# stale on 2026-08-11 without going red, which is the whole finding; it is now
# derived by `_states_the_interval` from the committed probability record. See
# the block above `check_closure_entry_of_record` for why.
_RANK_TOKEN = "not statistically decided"
_RANK_FIGURE = "P(rank 1)"
# Anything larger is a data file, not a surface that makes a claim in prose.
_RANK_MAX_BYTES = 4_000_000


def _rank_claim_lines(text: str) -> list[int]:
    """Line numbers of every passage that ASSERTS a rank-1 placement."""
    lines = []
    for match in _RANK_CLAIM.finditer(text):
        near = text[max(0, match.start() - _RANK_HOMONYM_WINDOW):
                    match.end() + _RANK_HOMONYM_WINDOW]
        if _RANK_HOMONYM.search(near):
            continue
        window = text[max(0, match.start() - _RANK_WINDOW):
                      match.end() + _RANK_WINDOW]
        if not _RANK_BOARD.search(window):
            continue
        lines.append(text.count("\n", 0, match.start()) + 1)
    return lines


def _rank_companions_missing(text: str) -> list[str]:
    """What the V8 amendment requires and this text does not carry.

    The token test is the one with history. `not statistically decided` is the
    literal string the cross-surface sweep greps for, and it has been broken
    across a line by reflowing prose three times in this ladder -- present to a
    reader, invisible to a line-bounded grep. So it is tested for on ONE LINE,
    and a token that is present in the text but split across a newline is
    reported as its own fault rather than as a plain absence: those two call
    for different edits.
    """
    missing = []
    if _RANK_FIGURE not in text:
        missing.append("P(rank 1)")
    if not _states_the_interval(text):
        missing.append(f"its {_rank_interval_phrase()} interval")
    lines = text.splitlines()
    on_a_line = any(_RANK_TOKEN in line for line in lines)
    if not on_a_line:
        if _RANK_TOKEN.replace(" ", "") in re.sub(r"\s+", "", text):
            missing.append(
                f"the sweep token {_RANK_TOKEN!r} UNBROKEN on one line (it is "
                f"present but wrapped across a line break, which is invisible "
                f"to the sweep that greps for it)")
        else:
            missing.append(f"the sweep token {_RANK_TOKEN!r}")
    return missing


def _tracked_files() -> list[Path] | None:
    """Every path git tracks, or None if git cannot be asked."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"], cwd=REPO, capture_output=True,
            text=True, timeout=120, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return [REPO / rel for rel in out.split("\0") if rel]


def _shipping_archives() -> list[Path]:
    """The archives that leave this box, found by extension, not by name."""
    return sorted(p for p in (REPO / "dist").glob("*.zip") if p.is_file())


def _travelling_names() -> set[str]:
    """File names that TRAVEL, derived from what is actually packed.

    Two derivations, no list: the member names of every shipping archive, and
    everything inside a submission package directory. A surface that travels
    is read by somebody outside this lab, so a bad claim on one is a FAIL; the
    same claim on a lab record is a WARN. Both are reported.

    THE SEVERITY DOWNGRADE THIS USED TO HIDE, 2026-08-15. The `except` below
    used to `continue` in silence. An archive that will not open therefore
    contributed NO travelling names, every shipped surface was reclassified as
    a lab record, and every FAIL in both rank checks became a WARN -- a
    corrupted zip made the report quieter. The unopened archives are returned
    now and both callers put them on the verdict.
    """
    names: set[str] = set()
    unopened: list[str] = []
    for archive in _shipping_archives():
        try:
            with zipfile.ZipFile(archive) as zf:
                names.update(Path(n).name for n in zf.namelist())
        except (OSError, zipfile.BadZipFile) as exc:
            unopened.append(f"{_rel(archive)}: the set of names that TRAVEL "
                            f"could not be derived from it ({exc}), so a fault "
                            f"on a surface it packs would have been reported "
                            f"as a lab record")
    for package in sorted(WEB.glob("closure_challenge_submission*")):
        if package.is_dir():
            names.update(p.name for p in package.rglob("*") if p.is_file())
    _travelling_names.unopened = unopened          # type: ignore[attr-defined]
    return names


def _surface_text(raw: bytes) -> str | None:
    if b"rank" not in raw.lower() and b"overall" not in raw.lower():
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def check_rank_claim_surfaces() -> Result:
    """Every surface that claims rank 1 carries the figure, the interval and
    the pairs -- and the surface set is searched for, never listed.

    THE RULE. Ladder V rung V8, as amended 2026-08-10: any rank claim,
    internal or external, must carry P(rank 1), its interval on the eight
    scored cases, and the comparisons that are not statistically decided. No
    surface may state the figure without the interval -- a bare probability is
    a worse claim than none, because a bare probability sounds settled and
    eight cases do not support settled.

    THE INTERVAL IS NOT WRITTEN HERE. It was, and on 2026-08-11 the board went
    from four entries to six, the interval moved, and this guard went on
    demanding the old one without going red -- while `closure.html` satisfied
    it only through the STRUCK text of the superseded figure, kept on the page
    under L-76, which still contained the literal the guard wanted. A guard
    that a tombstone can satisfy is not measuring the live claim. The interval
    is derived now, and if the record it comes from no longer matches the board
    on disk this check says so in its own verdict instead of judging surfaces
    against a number it cannot vouch for.

    THE DEFECT. The guard for that rule read `our_entry` on the wall and
    nothing else. `closure.html` made three rank claims with no probability
    and no interval and was not caught, because it was not on the list. This
    check has no list. It searches every tracked file and every member of
    every archive under dist/, and reports what it finds.

    WHAT IT CANNOT SEE, stated rather than discovered later: a rank claim
    phrased in words it has no pattern for ("we top the board"); anything that
    does not decode as UTF-8, which includes every compiled PDF in the tree,
    so a claim that exists only in a built PDF is invisible here while its
    .tex source is not; untracked files; files over 4 MB; text a generator or
    a browser produces at render time; and WHERE a companion sits -- the
    companion test is per file, so one compliant paragraph clears every claim
    in that file.
    """
    tracked = _tracked_files()
    if tracked is None:
        # B1, 2026-08-15: this was a WARN, which lab_check does not block on
        # and which reads on the report beside real findings. A guard that
        # could not enumerate its own corpus examined nothing.
        return _no_evidence("rank claims carry their probability",
                            "git could not be asked which files exist, so no "
                            "surface was opened and no claim was graded",
                            ["git ls-files"])

    travelling = _travelling_names()
    surfaces: list[tuple[str, str, bool]] = []   # (label, text, travels)
    opened = skipped = 0
    unreadable: list[str] = list(
        getattr(_travelling_names, "unopened", []))
    for path in tracked:
        try:
            if not path.is_file():
                skipped += 1
                continue
            if path.stat().st_size > _RANK_MAX_BYTES:
                skipped += 1
                continue
            raw = path.read_bytes()
        except OSError:
            skipped += 1
            continue
        opened += 1
        text = _surface_text(raw)
        if text is None:
            continue
        surfaces.append((str(path.relative_to(REPO)), text,
                         path.name in travelling))
    for archive in _shipping_archives():
        try:
            with zipfile.ZipFile(archive) as zf:
                for info in zf.infolist():
                    if info.is_dir():
                        skipped += 1
                        continue
                    if info.file_size > _RANK_MAX_BYTES:
                        skipped += 1
                        continue
                    opened += 1
                    text = _surface_text(zf.read(info))
                    if text is None:
                        continue
                    surfaces.append(
                        (f"{archive.relative_to(REPO)}!{info.filename}",
                         text, True))
        except (OSError, zipfile.BadZipFile) as exc:
            # B1, 2026-08-15. This used to append a surface whose text was the
            # EMPTY STRING. An empty string makes no rank claim, so it raised
            # no fault, so an archive that would not open read on the report
            # as a clean one. An archive that cannot be opened is a statement
            # about the instrument and it now travels to the verdict.
            unreadable.append(f"{_rel(archive)}: could not be opened ({exc}), "
                              f"so every member inside it was graded by "
                              f"nothing")

    claiming, shipped_faults, internal_faults = 0, [], []
    for label, text, travels in surfaces:
        lines = _rank_claim_lines(text)
        if not lines:
            continue
        claiming += 1
        missing = _rank_companions_missing(text)
        if not missing:
            continue
        where = ", ".join(f"L{n}" for n in lines[:6])
        fault = (f"{label}: {len(lines)} rank claim(s) ({where}) without "
                 f"{'; '.join(missing)}")
        (shipped_faults if travels else internal_faults).append(fault)

    frame = (f"frame: {len(tracked)} tracked path(s) plus the members of "
             f"{len(_shipping_archives())} shipping archive(s); {opened} "
             f"opened, {skipped} skipped as absent, a directory, or over "
             f"{_RANK_MAX_BYTES // 1_000_000} MB; {len(surfaces)} decoded as "
             f"UTF-8 AND contain 'rank' or 'overall'; {claiming} of those "
             f"assert a rank-1 placement. Blind to: anything that is not "
             f"UTF-8 text (every compiled PDF here), untracked files, "
             f"render-time text, phrasing outside _RANK_CLAIM, and the "
             f"distance from a claim to its companion (judged per file)")

    # The instrument's own staleness, reported before any verdict about a
    # surface. This is the line that the literal it replaces could never have
    # printed: a hard-coded interval cannot notice that the board moved under
    # it, and the only symptom is surfaces being failed for being right.
    stale = _closure_facts()["stale"]
    if stale:
        return Result(
            "rank claims carry their probability", WARN,
            f"THIS DETECTOR IS PARTLY OFF: the interval on P(rank 1) could not "
            f"be confirmed current, so {claiming} rank-claiming surface(s) were "
            f"NOT judged against it",
            [f"STALE INSTRUMENT: {s}" for s in stale]
            + shipped_faults + internal_faults + [frame])
    interval = _rank_interval_phrase()
    frame += (f". The interval required is {interval}, derived from "
              f"{_PROB_RECORD.name} and checked against the board in "
              f"{_PROB_SCRIPT.name}; it is not written in this file")
    # THE VERDICT IS ABOUT FORM AND SAYS SO, 2026-08-15. Until D145 this
    # summary read "every travelling surface complies", which is a sentence
    # about the surfaces. It was true of their FORM and false of their VALUE
    # on the same run, over the same bytes: the shipped bundle's
    # `site/closure.html:502` was read, recognised and cleared while saying
    # `rank 1 of 5` against a board where it is 1 of 7. The word FORM is in
    # every verdict below so that no reader can quote this line as a statement
    # that a page is right. `check_rank_claim_values` grades the other half.
    blind = [f"NOT GRADED AT ALL: {u}" for u in unreadable]
    if shipped_faults:
        return Result("rank claims carry their probability", FAIL,
                      f"{len(shipped_faults)} surface(s) that TRAVEL claim "
                      f"rank 1 without the FORM V8 requires "
                      f"({len(internal_faults)} more on lab records)",
                      shipped_faults + internal_faults + blind + [frame])
    if not claiming:
        return _no_evidence(
            "rank claims carry their probability",
            "no rank claim was found on any surface, so no form was graded",
            ["every tracked file and every shipping archive member"],
            blind + [frame])
    if unreadable:
        return _no_evidence(
            "rank claims carry their probability",
            f"no travelling surface fails on FORM, but {len(unreadable)} "
            f"shipping archive(s) could not be opened at all",
            [u.split(":")[0] for u in unreadable],
            internal_faults + [frame])
    if internal_faults:
        return Result("rank claims carry their probability", WARN,
                      f"every travelling surface complies ON FORM (this "
                      f"verdict says nothing about whether its values are "
                      f"right -- see `rank claims carry the right values`); "
                      f"{len(internal_faults)} lab record(s) claim rank 1 "
                      f"without what V8 requires", internal_faults + [frame])
    return Result("rank claims carry their probability", UNKNOWN,
                  f"all {claiming} surface(s) that claim rank 1 carry the "
                  f"figure, its interval and the not-decided pairs -- a "
                  f"statement about FORM only", [frame])


# ---------------------------------------------------------------------------
# THE VALUE GRADER (D145, 2026-08-15): FORM AND VALUE ARE SEPARATE VERDICTS
# ---------------------------------------------------------------------------
#
# THE DEFECT, reproduced at HEAD 82fb3d46 before anything was changed.
# `check_rank_claim_surfaces` DOES open `dist/certonomous-demo.zip`, DOES read
# member `certonomous-demo/site/closure.html`, DOES recognise its line 502 as a
# rank claim -- `_rank_claim_lines` returns that member's claims as
# `[95, 96, 108, 112, 139, 141, 366, 370, 375, 391, 391, 502]` -- and reported:
#
#     [WARN] rank claims carry their probability
#            every travelling surface complies; 27 lab record(s) claim rank 1
#            without what V8 requires
#
# The sentence it cleared reads "rank 1 of 5 is our local scoring at a pinned
# benchmark commit, with a seed-uncertainty bound comparable to its margin."
# Against the live six-entry board that is rank 1 of SEVEN, and the bound is
# 177% of the margin -- it EXCEEDS the margin it is called comparable to. Two
# withdrawn claims in one sentence, perfectly formed, on a surface that ships.
#
# WHY IT SAID SO. That guard grades claim FORM: does the sentence carry
# `P(rank 1)`, does it carry the current interval, does it carry the literal
# `not statistically decided`. All three are present on that page. It has no
# opinion about the DENOMINATOR, about the MARGIN, or about whether
# `comparable` is still a true word. A FORM CHECK ON A STALE ARTIFACT IS NOT A
# BLIND SPOT. IT IS A FALSE CLEAN, and it is worse than no check at all,
# because a blind spot reports nothing and this one reports agreement -- and
# the report gets quoted as reassurance.
#
# TWO VERDICTS AND NOT ONE, deliberately. Form and value fail differently: a
# sentence can be TRUE and undated, or WELL-FORMED and false. Merging them is
# how a green on one hides a red on the other. So this is a second check with
# its own name, its own BASIS row and its own priced remedy, and both verdicts
# appear on every report.
#
# NOTHING ARITHMETIC IS REIMPLEMENTED HERE. `scripts/check_derived_figures.py`
# already reads the five source records, already holds the half-ulp predicate
# (`agrees`, `written_digits`, `Basis`, `Quantity.verdict`), already derives
# the live margin and the coverage ratio over every admissible basis, and
# already holds the masker for struck and quoted text -- 252 strike spans in
# this corpus, 69 of them multi-line and 8 crossing blockquote continuations,
# and two authors' line-by-line first cuts were both wrong. It is IMPORTED BY
# PATH and used. A second copy of that arithmetic is exactly the defect this
# lab keeps filing: a copy that survives its own correction.
#
# THE ONE THING ADDED HERE is the DATED-CONTEXT DISCRIMINATOR, and it is added
# because `check_derived_figures.py` names its absence as the reason P(rank 1)
# is measured and NOT SHIPPED there -- "13 hits on the corpus, mostly correct
# dated records; needs a dated-context discriminator (docket)" -- and D85 and
# D89 both name building it as the prerequisite. `mask_exempt` masks a struck
# SPAN, a kept-record BLOCK, a heading that declares ITSELF struck and a
# whole-document banner. What it does not have is D145's measured unit of
# classification: THE LINE PLUS THE NEAREST BANNER ABOVE IT. The two false
# positives D145 recorded, `CLOSURE_CHALLENGE_STATUS.md:406` and `:667`, are
# both correct round-3/round-4 history sitting under a section banner:
#
#     ## 0e. Round 4 (2026-07-31) -- ... *(superseded as entry of record by
#     round 5, sec 0f, 2026-08-07)*
#     > **Superseded 2026-08-07, see sec 0f.** ... The table below stands
#     > unchanged as the round-3/round-4 record.
#
# `_STRUCK_HEAD` misses the first because its alternation carries `SUPERSEDED`
# and `Superseded` but not the lower-case spelling, and misses the second
# because a blockquote banner is not a heading.
#
# THE DATE IS REQUIRED, and that is the whole discriminator. An UNDATED
# withdrawal word masks nothing here: this corpus is full of live sections
# that mention supersession in passing, and a historical record that does not
# say WHEN it was true is not a dated record, it is a stale one. So
# "superseded" alone is not an exemption; "superseded 2026-08-07" is.

_DERIVED_FIGURES = _HERE / "scripts" / "check_derived_figures.py"


@functools.lru_cache(maxsize=1)
def _derived_figures():
    """`scripts/check_derived_figures.py` imported by path, or why it is not.

    By path and not by name: `scripts/` is not a package, and this file is run
    both as `python3 scripts/self_audit.py` and imported from `sdk/tests/` by
    the same `spec_from_file_location` route. A plain `import` works in one and
    not the other, and a check that silently loses its arithmetic in the test
    harness is the failure mode this whole block exists to remove.

    Never raises. The caller turns a failure into UNKNOWN, because a value
    grader that could not load its own arithmetic has graded nothing and an
    empty sweep is not agreement (defect class B1).
    """
    try:
        spec = importlib.util.spec_from_file_location(
            "self_audit_derived_figures", _DERIVED_FIGURES)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    except Exception as exc:                        # noqa: BLE001
        return None, (f"{_rel(_DERIVED_FIGURES)} could not be imported, so no "
                      f"value could be derived and nothing was graded "
                      f"({type(exc).__name__}: {exc})")
    for symbol in ("mask_exempt", "read_sources", "build_registry", "agrees",
                   "written_digits", "_is_rejection", "_is_discrepancy_report",
                   "_kept_block_end", "_HEADING"):
        if not hasattr(module, symbol):
            return None, (f"{_rel(_DERIVED_FIGURES)} no longer exports "
                          f"`{symbol}`; this check reuses that module's "
                          f"arithmetic and masker rather than holding a second "
                          f"copy, and it will not grade against a copy it "
                          f"cannot find")
    return module, ""


#: A withdrawal verb ANYWHERE on the line, in any case, together with an ISO
#: date on the same line. Both halves are required: the verb without a date is
#: a live section discussing supersession, and a date without a verb is every
#: dated heading in the corpus.
_HISTORY_VERB = re.compile(
    r"\b(?:superseded|struck|withdrawn|retracted|falsified|obsolete|"
    r"no longer (?:the )?(?:current|live|in force)|as it (?:then )?stood|"
    r"stands unchanged as the|kept as the record|kept for the record)\b", re.I)
_ISO_DATE = re.compile(r"\b20\d{2}-[01]\d-[0-3]\d\b")
#: How far below a heading a banner may sit and still govern the section. The
#: two measured cases put it on the heading itself and two lines below it; the
#: window is the paragraph, not the section, so a withdrawal verb in the
#: section's BODY does not retroactively date the whole section.
_BANNER_LINES = 8

# THE THREE MARKUP DIALECTS `mask_exempt` DOES NOT SPEAK, each measured on this
# corpus before it was written down, and each ADDITIVE -- every one of them can
# only mask more, never less, so none of them can hide a fault the imported
# masker would have exposed. They are enumerated rather than folded into a
# widened pattern for the reason the interval table above this file already
# gives: a guard that fails compliant surfaces gets switched off, and the
# cheapest way to silence it is to "fix" the surface that was right.
#
#   Y1  HTML ENTITY QUOTATION. `check_derived_figures.py` reads only `*.md`
#       and `*.html`, and its `_QUOTED` knows the ASCII and Unicode quote
#       characters. The repaired pages spell their quotes as ENTITIES --
#       `&ldquo;comparable&rdquo; was fair` at `benchmarks.html:158` and
#       `closure.html:406,468` -- and all three are repair notes explaining why
#       the word was withdrawn. Without Y1 this check faults the three surfaces
#       that were repaired FIRST, which is the exact false-fault shape D115
#       records.
#
#   Y2  LATEX STRIKE. `latex/closure_challenge_report.tex:83` reads
#       `\sout{\textbf{rank 1 of 5, scored locally}, ...}`. That IS struck, in
#       the only dialect LaTeX has for it, and `mask_exempt` has no LaTeX
#       dialect because it never opens a `.tex`. This check does. Brace-
#       balanced, so a nested `\textbf{...}` inside the strike is covered.
#
#   Y3  LINE-SCOPED QUOTATION. `_QUOTED` may cross a newline, so an unbalanced
#       quote earlier in a file shifts every pairing after it. Measured at
#       `campaign/OWNERSHIP_BOUNDARY_SWEEP_2026-08-15.md:165`, where the
#       quotation `*"rank 1 of 5, scored locally; P 68% ..."*` came out of the
#       imported masker with its OPENING quote blanked and its body live -- a
#       document enumerating stale figures faulted for enumerating them, which
#       is D71's trap one level down. Y3 re-pairs quotes WITHIN a single line
#       and masks what it finds.
_Y1_ENTITY_QUOTE = re.compile(
    r"&ldquo;.*?&rdquo;|&#8220;.*?&#8221;|&quot;.*?&quot;|&#34;.*?&#34;")
_Y2_LATEX_STRIKE = re.compile(r"\\(?:sout|st|cancel|xcancel|xout)\s*\{")
_Y3_LINE_QUOTE = re.compile(r"\"[^\"\n]{1,400}\"|\u201c[^\u201d\n]{1,400}\u201d")

#   Y4  `record` IS A NOUN HERE. `check_derived_figures._REPORTED` lists
#       `record|records|recorded` among the verbs that mean "this document is
#       narrating what some other surface says". In this lab the commonest use
#       of the word is the NOUN in "the entry of record", and the suppressor
#       fired on it: `CLOSURE_CHALLENGE_STATUS.md:9` reads "the entry of
#       record, **rank 1 of 5 scored locally**" -- a live, present-tense,
#       wrong claim in the document's own header -- and was silently dropped
#       as a report about somebody else's words. Y4 blanks the NOUN so the
#       verb list cannot see it. It masks no digit and no claim: only the six
#       characters of the word itself, inside two fixed phrases.
_Y4_RECORD_NOUN = re.compile(r"(?<=\bof )record\b|(?<=\bthe )record\b", re.I)


def _y2_spans(text: str) -> list[tuple[int, int]]:
    """Brace-balanced spans of every LaTeX strike macro."""
    spans = []
    for m in _Y2_LATEX_STRIKE.finditer(text):
        depth, i = 1, m.end()
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        spans.append((m.start(), i))
    return spans


def _dated_history_spans(text: str, cdf) -> list[tuple[int, int, str]]:
    """(start, end, why) for every section a DATED banner declares historical.

    The banner may be the heading itself or a paragraph within the first
    `_BANNER_LINES` lines under it. The span runs to the next heading of the
    same or a shallower level, which is `check_derived_figures._kept_block_end`
    -- reused, not rewritten, so a change to how this corpus delimits a section
    changes both checks together.

    THE BANNER IS NOT INSIDE ITS OWN SPAN, and the first cut of this function
    had it the other way round. A supersession banner is written in the PRESENT
    TENSE about the CURRENT record -- `CLOSURE_CHALLENGE_STATUS.md:689-694`
    reads "Superseded again 2026-08-07, see sec 0f. The entry of record is now
    round 5: overall 0.0566, rank 1 of 5 scored locally ... The notes below
    stand as the superseded round-3/round-4 record." The notes BELOW are
    history. The banner itself is a live claim, and it is wrong: that is the
    `rank 1 of 5` D150 records at line 691, and masking from the heading
    swallowed it. The span therefore begins at the END of the banner
    paragraph. D145's unit is the line plus the nearest banner ABOVE it, and a
    banner is not above itself.
    """
    lines = text.split("\n")
    starts, pos = [], 0
    for line in lines:
        starts.append(pos)
        pos += len(line) + 1
    heads = [i for i, line in enumerate(lines) if cdf._HEADING.match(line)]
    spans = []
    for index, head in enumerate(heads):
        limit = min(head + _BANNER_LINES + 1,
                    heads[index + 1] if index + 1 < len(heads) else len(lines))
        banner = None
        for j in range(head, limit):
            if _HISTORY_VERB.search(lines[j]) and _ISO_DATE.search(lines[j]):
                banner = j
                break
        if banner is None:
            continue
        # The banner's own paragraph stays live. It runs to the first blank
        # line after it, which is how this corpus ends a banner block.
        body = banner + 1
        while body < len(lines) and lines[body].strip():
            body += 1
        end_line = cdf._kept_block_end(text, lines, head)
        if body >= end_line:
            continue
        start = starts[body]
        end = starts[end_line] if end_line < len(starts) else len(text)
        spans.append((start, end,
                      f"L{body + 1}-{end_line}: dated historical section, "
                      f"banner at L{banner + 1} (the banner itself is LIVE "
                      f"text and is graded): {lines[banner].strip()[:80]!r}"))
    return spans


def _live_claim_text(text: str, cdf) -> tuple[str, list[str]]:
    """`text` with every exempt region blanked, offsets preserved.

    Two layers, in order, and the order is the point: `mask_exempt` blanks what
    the AUTHOR marked (strike markup, kept-record blocks, code, quotations,
    correction arrows), and `_dated_history_spans` blanks what the SECTION
    declares. A claim that survives both is a claim this document is making
    now, in its own voice, undated.
    """
    live, _ = cdf.mask_exempt(text)
    out = list(live)
    notes = []

    def blank(start, end):
        for i in range(start, min(end, len(out))):
            if out[i] != "\n":
                out[i] = " "

    for rx in (_Y1_ENTITY_QUOTE, _Y3_LINE_QUOTE, _Y4_RECORD_NOUN):
        for m in rx.finditer(text):
            blank(m.start(), m.end())
    for start, end in _y2_spans(text):
        blank(start, end)
    for start, end, why in _dated_history_spans(text, cdf):
        blank(start, end)
        notes.append(why)
    return "".join(out), notes


# THE VALUE RULES. Each names the authority it grades against, and not one of
# them holds a number. `rank 1 of N` is graded against the length of
# `LIVE_BOARD` read by AST out of `sdk/scripts/probability_of_rank.py`; the
# best-on-board count against `round5_per_case_full` compared cell by cell
# against that same board; and `comparable` against the ratio
# `check_derived_figures.py` derives from
# `closure_challenge_seed_sensitivity.json` over every admissible margin basis.
# The day the board moves, all three move, and the surfaces that did not move
# go red -- which is the direction that matters.

# THE DENOMINATOR PREDICATE (D151, 2026-08-15), and why it is `rank N of M`
# and not `rank 1 of M`. `self_audit.py`'s own word-form guard defers this
# class: `_PLACE_OFN` skips `^\s*of\s+\d` after an ordinal with the comment
# "OUR claim, owned by the sibling guard". The sibling it names is
# `check_rank_claim_surfaces`, which grades FORM and has no arithmetic, so the
# deferral had no receiving end and NO INSTRUMENT IN THIS LAB HELD A
# DENOMINATOR PREDICATE. That is why `rank 1 of 5` has now been found live on
# six separate surfaces over four days, each repair finding another copy.
# Rule A of the word-form guard binds an ordinal to a NAMED PUBLISHED
# ENTRANT, so it is structurally incapable of reaching a claim about
# ourselves; this rule reaches both, because the arithmetic is the same
# arithmetic and building it twice is how the copies got here.
#
# BOTH DIGITS ARE GRADED. N is a rank on the live board counting us -- ours
# derived by sorting our overall against the entrants' means, an entrant's by
# their own position in that same sort. M is the number of positions the claim
# implicitly asserts exist.
#
# TWO ADMISSIBLE DENOMINATORS, and the reason is D55's two referents. A
# sentence may count the board WITH us in it (`entries + 1`, the standing
# question) or the published board WITHOUT us (`entries`, who is on the
# leaderboard). Both are true statements about different sets, so both pass
# and the message names both. What is not admissible is `5` against a board of
# six.
#
# THE BARE ORDINAL (chief ruling `9b9951a1` on V14's denominator gap,
# 2026-08-15, measured at `86dd1866`). This pattern used to require the literal
# token `rank`, so `2nd of 5` and `3rd of 5` fell outside its REGEX and not
# outside its arithmetic -- which grades them correctly. Four of the five
# four-entry claims a repo-wide denominator measurement found in the shipping
# archive carry no `rank` token, and the ruling is that the fix is this one
# pattern and NOT a second checker: a second instrument would duplicate a
# working arithmetic core to reach a string form. The `rank` branch below is
# character-for-character what it was; the `(?P<o>...)` branch is the whole
# widening.
#
# ONLY THE DENOMINATOR IS GRADED ON THE BARE BRANCH, and this is the part that
# keeps the widening from reversing the ruling on its own terms. `rank N of M`
# names the quantity: it is an OVERALL placement, so both digits are graded
# against the overall sort. A bare `<n>th of <m>` does not say WHICH placement
# it is -- `4th of 7` is the correct live per-case ordinal for `AR_3_Ret_360`
# and the wrong overall one -- so grading its numerator against our overall
# rank would FAULT A CORRECT TRAVELLING CLAIM, which is the one outcome the
# ruling names as reversing it. The denominator is the same question either
# way: how many positions the board has. So M is graded, N is returned
# ungraded with its reason, and the check says which of the two it decided.
#
# WORD BOUNDARIES ON BOTH ENDS OF THE ORDINAL, and they are not decoration.
# The measurement that produced this widening found `duct` matching inside
# `product` in its own instrument -- the same substring class as a prior
# sweep's `68%` matching inside `1.68%`. `\b(?P<o>\d{1,3})(?:st|nd|rd|th)\b`
# takes `21st` whole out of `21st of 50` and cannot take `1st` out of it, and
# cannot fire inside `v3rd` or `3rdx`. `sdk/tests/test_rank_claim_values.py`
# asserts both directions rather than trusting the reading.
#
# AND IT CANNOT SWALLOW RULE V2's SPANS. The same measurement found its own
# ordinal family eating its count family, so that the CORRECT `2 of 8`
# best-on-board count was reported as a wrong denominator. The ordinal suffix
# is what makes the two disjoint here: `4 of 8` carries none, so V1 cannot
# match it and V2 keeps it. Asserted in the suite, not argued.
#
# A DENOMINATOR IS AN INTEGER, and `\b` DOES NOT SAY SO. V16 round 11
# (`94419cc8`, D189-D194) found this pattern matching `rank 2 of 0` out of
# `latex/closure_challenge_report.tex:1890` -- *"a gap to rank 2 of 0.0030"* --
# because the word boundary after `\d{1,3}` falls BETWEEN the `0` and the
# decimal point. The pattern read a MARGIN as a BOARD SIZE: a sentence about a
# gap parsed as a claim about how many entrants exist. Reproduced here before
# fixing, on the real file: it matched, and the only thing holding it was
# `_in_board_context` returning False -- ONE GATE DEEP, and not the strike
# masker, which leaves that passage byte-identical. Put the word "board"
# anywhere in that window, which is entirely natural in a document about a
# leaderboard, and a correct sentence faults on a TRAVELLING surface.
#
# THE BARE-ORDINAL BRANCH ABOVE MAKES THAT SURFACE BIGGER, which is why the two
# changes ship together rather than in sequence: `2nd of 0.0030` and `3rd of
# 0.0592` were both matched by the widened pattern before this lookahead, and
# bare ordinals are commoner than `rank N of M` in exactly the prose where
# margins are discussed. `(?![.,]\d)` is the whole fix -- a denominator may end
# a sentence (`of 7.`) or a clause (`of 7,`), but it may not be the integer part
# of a decimal. Controlled on that exact `.tex` sentence, in both branches.
_VALUE_BOARD_SIZE = re.compile(
    r"(?:\brank[ \-]?(?P<n>\d{1,3}|one|two|three|four|five|six|seven|eight|"
    r"nine|ten)"
    r"|\b(?P<o>\d{1,3})(?:st|nd|rd|th)\b\*{0,2})"
    r"\s+of\s+\*{0,2}(?P<v>\d{1,3}|zero|one|two|three|four|five|"
    r"six|seven|eight|nine|ten)\b(?![.,]\d)", re.I)

#: A third-party placement on the FROZEN SCORING PIN is a claim about a
#: different board -- `deb91557` carries four entrants and Reissmann leads it,
#: which is why `SUBMISSION_DRAFT.md:729` says "on the frozen scoring pin
#: `deb91557` Reissmann is rank 1 of four" and is CORRECT. This check reads
#: only the live board, so it declines that class by name instead of faulting
#: it. It is NOT an exemption for our own claims: `rank 1 of 5 is our local
#: scoring at a pinned benchmark commit` is the shipped defect, and the pin
#: scores but does not rank (D55).
_VALUE_FROZEN_PIN = re.compile(
    r"deb9155|frozen (?:scoring )?pin|pinned (?:scoring )?board|"
    r"four-entry board|4-entry board", re.I)

#: `comparable` is a value claim wearing a word. It is only graded where it
#: binds the SEED BOUND to the MARGIN: this corpus carries 149 occurrences of
#: the word and the overwhelming majority are comparable meshes, comparable
#: Mach numbers and comparable steps. Both operands must be named inside the
#: window or nothing is graded, and the un-graded case is counted and printed.
_VALUE_COMPARABLE = re.compile(
    r"\b(?:comparable|of comparable size|the same size as|no larger than|"
    r"roughly the same size)\b", re.I)
_VALUE_MARGIN_WORD = re.compile(r"\bmargin\b", re.I)
_VALUE_BOUND_WORD = re.compile(
    r"seed[- ](?:uncertainty|stability|sensitivity)|seed bound|"
    r"(?:uncertainty|truth-free|one-seed|single-seed)[- ]bound|"
    r"bound of comparable|bound\b", re.I)
_VALUE_WINDOW = 160

# A LABELLED TEST CORPUS IS NOT A CLAIM SURFACE, and this is a definition
# rather than a tuning. `sdk/tests/fixtures/absolute_claims_labelled*.json`
# and `sdk/tests/test_rank_claim_surfaces.py` EXIST to carry the withdrawn
# sentences verbatim -- `CLOSURE_HTML_BEFORE`, `SUPERSEDED`, and 252 labelled
# units quoting surfaces as they read before repair. Faulting them is faulting
# the control, and D140 records the same fixture as "quoted historical text
# inside a labelled test fixture and is correct as history". The imported
# arithmetic module never reads these files at all: its own `PROSE_GLOBS` is
# `("*.md", "*.html")`. So this narrows TOWARD the module whose predicate is
# being reused, not away from it. The count is printed in the frame; nothing is
# dropped silently.
_VALUE_NOT_A_SURFACE = ("sdk/tests/",)

#: A CHEAP GATE BEFORE AN EXPENSIVE MASK. Masking a surface costs a dozen
#: multi-line regexes; grading 1,400 of them cost 85 seconds of the audit's
#: runtime, and almost none of them carries a value claim at all. This runs on
#: the RAW text first. It is SAFE because masking only ever blanks characters:
#: a trigger present after masking was present before it, so a surface this
#: skips could not have produced a fault. The count of what it skipped is
#: printed in the frame rather than being silent.
#: THE TRIGGER MUST STAY A SUPERSET OF EVERY RULE PATTERN, or the widening
#: above is inert on exactly the surfaces it was widened for. This gate runs
#: FIRST and a surface it skips is never masked and never graded, so admitting
#: `2nd of 5` to `_VALUE_BOARD_SIZE` without admitting it here would leave any
#: file whose only claim is a bare ordinal -- no `rank ... of`, no
#: `of eight`, no `comparable` -- silently ungraded. Measured rather than
#: assumed: the widened rule fires on `dist/certonomous-demo.zip!.../
#: closure.html`, which reaches this gate on its `rank 1 of 5` at line 502
#: anyway, so the archive would not have shown the omission.
_VALUE_TRIGGER = re.compile(
    r"rank[ \-]?(?:\d{1,3}|one|two|three|four|five|six|seven|eight|nine|ten)"
    r"\s+of\s"
    r"|\b\d{1,3}(?:st|nd|rd|th)\b\*{0,2}\s+of\s"
    r"|\bof\s+(?:the\s+)?(?:8|eight)\b"
    r"|comparable|the same size as|no larger than|roughly the same size", re.I)

#: SOMEBODY ELSE'S PLACEMENT IS NOT OUR CLAIM. `CLOSURE_CHALLENGE_SUBMISSION_
#: DRAFT.md:729` reads "on the frozen scoring pin `deb91557` Reissmann is rank
#: 1 of four", which is TRUE -- the pin's board has four entrants and Reissmann
#: leads it. A denominator rule that assumes every `rank 1 of N` is ours faults
#: a correct sentence about a competitor on a frozen board. The binding is
#: deliberately narrow: the entrant must be the SUBJECT of the copula
#: immediately before the ordinal, which is the same discipline
#: `check_board_placement_words` RULE A uses and for the same reason. Anything
#: looser exempts "below Reissmann's published 0.059525, rank 1 of 5", which is
#: OUR claim with a competitor's name 30 characters upstream.
_VALUE_OTHERS_SUBJECT = re.compile(
    r"\b(?P<who>[A-Z][A-Za-z'’\-]+)\**\s+"
    r"(?:is|was|were|are|remains|stays|sits\s+at|stands\s+at|holds|ranks)"
    # An adverb may sit between the copula and the ordinal. Measured:
    # `docs/P33_CROSS_SURFACE_SWEEP.md:48` reads "Montoya is now **rank 6 of
    # 6** on the live board, not 4" -- a CORRECT third-party statement that a
    # binding without this group read as a claim about US.
    r"(?:\s+(?:now|still|currently|already|only|nominally))?"
    r"\s+\**\s*$")

#: THE CORRECTION IDIOM `mask_exempt` HAS ONLY IN ARROW FORM. `_ARROW_OLD`
#: blanks the left of `4 of 8 -> 2 of 8`. This corpus writes the same
#: correction in prose -- "the best-on-board count falls from 4 of 8 to 2 of 8"
#: at `campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md:11` -- and the left
#: operand is the superseded value in both. Without this the document that
#: ANNOUNCED the correction is faulted for announcing it.
_VALUE_FROM_TO = re.compile(
    r"\bfrom\s+\**\s*$")
#: THE RIGHT OPERAND MAY BE AN ORDINAL, and it had to be admitted the day the
#: rule above learned to read bare ordinals. Without the optional suffix,
#: `\d{1,3}\b` cannot end inside `3rd`, so "the duct falls from 2nd of 5 to
#: 3rd of 7" was not recognised as a correction at all and the RETIRED value
#: was faulted -- i.e. the sentence announcing a repair got faulted for
#: announcing it, which is the exact defect this constant exists to prevent
#: and which this corpus's own repair notes are written in ("was 3rd",
#: "3rd of 5 -> 4th of 7"). Found by the widening's own control run, not by
#: review.
_VALUE_TO_NEW = re.compile(
    r"^[^.;\n]{0,30}?\bto\s+\**\s*"
    r"(?:\d{1,3}(?:st|nd|rd|th)?|zero|one|two|three|four|five|six|seven|"
    r"eight|nine|ten)\b")


@functools.lru_cache(maxsize=1)
def _live_ranks() -> dict:
    """{first-author surname -> rank on the live board counting us}, plus us.

    Our own position is keyed by the empty string. Derived, not listed: the
    board's own `entrants` block is read by AST, each entrant's overall is the
    mean of their eight published per-case values, our overall comes from the
    entry of record through `_closure_facts`, and the ranks are the order of
    that sort. An entrant added to the board is ranked here the day the board
    file changes, and no name and no ordinal is written in this file.
    """
    facts = _closure_facts()
    try:
        board = _module_literal(_PROB_SCRIPT, "LIVE_BOARD")
    except (OSError, SyntaxError, ValueError, KeyError):
        return {}
    entrants = board.get("entrants") or {}
    ours = facts.get("our_overall")
    if not entrants or ours is None:
        return {}
    scored = [("", float(ours))]
    for key, values in entrants.items():
        head = re.split(r"[,&]", key)[0].strip()
        if head and values:
            scored.append((head.split()[0], sum(values) / len(values)))
    scored.sort(key=lambda pair: pair[1])
    return {name: index + 1 for index, (name, _) in enumerate(scored)}


def _superseded_by_correction(live: str, start: int, end: int) -> bool:
    """`from <old> ... to <new>`: the left operand is the value being retired."""
    return bool(_VALUE_FROM_TO.search(live[max(0, start - 40):start])
                and _VALUE_TO_NEW.match(live[end:end + 40]))


def _in_board_context(text: str, start: int, end: int) -> bool:
    """The same two gates the FORM guard applies, applied to a value claim.

    Reused rather than re-derived so a homonym the form guard learns to ignore
    is ignored here on the same day. Without them `rank 1 of 35` in a mission
    transcript and the `rank 1 of 5` inside this file's own regex comment are
    both faults.
    """
    near = text[max(0, start - _RANK_HOMONYM_WINDOW):end + _RANK_HOMONYM_WINDOW]
    if _RANK_HOMONYM.search(near):
        return False
    window = text[max(0, start - _RANK_WINDOW):end + _RANK_WINDOW]
    return bool(_RANK_BOARD.search(window))


def _rank_value_faults(text: str, cdf, facts: dict, ratio_lo, ratio_hi):
    """(faults, ungraded) for one surface. Faults are (line, rule, message).

    `ungraded` is not a residue to be swallowed: every passage a rule matched
    and could not decide is returned with its reason, and the caller prints
    the count. A value grader that quietly drops what it cannot decide is the
    same instrument as the one this block replaces.
    """
    live, history = _live_claim_text(text, cdf)
    faults, ungraded = [], list(history)
    board_n = facts["entries"] + 1
    admissible_m = {board_n, facts["entries"]}
    ranks = _live_ranks()
    best, earned = len(facts["best"]), len(facts["earned"])

    def line_of(off):
        return live.count("\n", 0, off) + 1

    # RULE V1 -- the denominator of a rank-1 placement is the board's own
    # length plus us. `rank 1 of 5` was true of a four-entry board and is the
    # single most-copied withdrawn claim in this corpus.
    for m in _VALUE_BOARD_SIZE.finditer(live):
        if not _in_board_context(live, m.start(), m.end()):
            continue
        if cdf._is_rejection(live, m.start("v")):
            ungraded.append(f"L{line_of(m.start())}: `rank 1 of "
                            f"{m.group('v')}` is stated in order to be "
                            f"rejected or is reported as another surface's "
                            f"words; not graded")
            continue
        quoted = m.group(0)
        if _superseded_by_correction(live, m.start(), m.end()):
            ungraded.append(f"L{line_of(m.start())}: `{quoted}` is the LEFT "
                            f"operand of a `from ... to ...` correction, so it "
                            f"is the value being retired; not graded")
            continue
        bare = m.group("n") is None
        raw_n = (m.group("o") if bare else m.group("n")).lower()
        raw_m = m.group("v").lower()
        got_n = _COUNT_WORDS.get(raw_n, int(raw_n) if raw_n.isdigit() else None)
        got_m = _COUNT_WORDS.get(raw_m, int(raw_m) if raw_m.isdigit() else None)
        if got_n is None or got_m is None:
            ungraded.append(f"L{line_of(m.start())}: `{quoted}` -- one of the "
                            f"two digits is not a number this check reads")
            continue
        if bare:
            # A BARE ORDINAL NAMES A POSITION WITHOUT NAMING THE QUANTITY. See
            # the block above `_VALUE_BOARD_SIZE`: M is the board's length and
            # is decidable; N may be an overall placement or a per-case one and
            # this check cannot tell which, so it is returned ungraded instead
            # of being graded against the overall sort. A frozen-pin sentence
            # is a claim about the four-entry board and is declined by name,
            # exactly as the third-party arm below declines it.
            if not facts["entries"]:
                # THE BLINDFOLD DECLINE, and it was put here by a blindfold
                # rather than by review. With the board unreadable
                # `facts["entries"]` is 0, `admissible_m` is {0, 1}, and every
                # denominator in the corpus is "wrong" against a board of no
                # entrants -- so this arm manufactured faults out of the
                # ABSENCE of the evidence it claims to grade against. The
                # `rank` arm never had the hole because it grades its numerator
                # through `_live_ranks()`, which returns {} and declines; this
                # arm reads only the board's length and needed its own. The
                # caller already refuses to run at all on a stale board, so
                # this is the rule being honest when driven directly, which is
                # how every test in the suite drives it.
                ungraded.append(
                    f"L{line_of(m.start())}: `{quoted}` -- the live board "
                    f"could not be read, so the number of positions it has is "
                    f"unknown and no denominator was graded")
                continue
            window = live[max(0, m.start() - _VALUE_WINDOW):
                          m.end() + _VALUE_WINDOW]
            if _VALUE_FROZEN_PIN.search(window):
                ungraded.append(
                    f"L{line_of(m.start())}: `{quoted}` is a bare ordinal "
                    f"bound to the FROZEN SCORING PIN, a different board from "
                    f"the live one this check reads; declined rather than "
                    f"faulted")
                continue
            if got_m in admissible_m:
                ungraded.append(
                    f"L{line_of(m.start())}: `{quoted}` states an admissible "
                    f"denominator; its NUMERATOR is not graded, because a bare "
                    f"ordinal does not say whether it places us overall or on "
                    f"one case and this check cannot decide which")
                continue
            faults.append((
                line_of(m.start()), "board size",
                f"claims `{quoted}`; the live board in {_PROB_SCRIPT.name} "
                f"carries {facts['entries']} entrants, so there are "
                f"{board_n} positions counting us (or {facts['entries']} on "
                f"the published board without us) and no placement on it can "
                f"be out of {got_m}. Only the DENOMINATOR is graded here: a "
                f"bare ordinal does not say which placement it means"))
            continue
        subject = _VALUE_OTHERS_SUBJECT.search(
            live[max(0, m.start() - 60):m.start()])
        who = subject.group("who") if subject else None
        if who is not None and who not in ranks:
            who = None
        if who is not None:
            # SOMEBODY ELSE's placement. Reached deliberately: the word-form
            # guard binds these to a name and then has no arithmetic, so
            # without this arm the denominator class is ungraded for third
            # parties too, and D151 asks that the predicate be built once for
            # both.
            window = live[max(0, m.start() - _VALUE_WINDOW):
                          m.end() + _VALUE_WINDOW]
            if _VALUE_FROZEN_PIN.search(window):
                ungraded.append(
                    f"L{line_of(m.start())}: `{quoted}` is bound to {who} on "
                    f"the FROZEN SCORING PIN, a different board from the live "
                    f"one this check reads; declined rather than faulted")
                continue
            # The two readings must be CONSISTENT, not independently
            # admissible: an entrant's rank counting us goes with a
            # denominator counting us, and their rank on the published board
            # goes with the published board's own length. Measured on
            # `docs/P33_CROSS_SURFACE_SWEEP.md:48` -- "Montoya is now rank 6
            # of 6 on the live board" is correct as (published rank,
            # published length) and would be wrong as (6, 7).
            live_n = ranks[who]
            ours_n = ranks.get("")
            pub_n = live_n - 1 if ours_n is not None and live_n > ours_n \
                else live_n
            readings = {(live_n, board_n), (pub_n, facts["entries"])}
            if (got_n, got_m) not in readings:
                faults.append((
                    line_of(m.start()), "third-party placement",
                    f"claims `{quoted}` about {who}; on the live board in "
                    f"{_PROB_SCRIPT.name} {who} is rank {live_n} of "
                    f"{board_n} counting us, or rank {pub_n} of "
                    f"{facts['entries']} on the published board without us"))
            continue
        want_n = ranks.get("")
        if want_n is None:
            ungraded.append(f"L{line_of(m.start())}: `{quoted}` -- our own "
                            f"position on the live board could not be derived")
            continue
        if got_n != want_n or got_m not in admissible_m:
            faults.append((
                line_of(m.start()), "our placement",
                f"claims `{quoted}`; the live board in {_PROB_SCRIPT.name} "
                f"carries {facts['entries']} entrants and our entry of record "
                f"sorts to rank {want_n}, so the claim is rank {want_n} of "
                f"{board_n} counting us (or of {facts['entries']} if the "
                f"sentence means the published board without us)"))

    # RULE V2 -- the best-on-board count, against the same board and the
    # entry of record's own per-case block. Two values are admissible and both
    # are named in the message: the arithmetic count and the count belonging to
    # our MODEL after the decline gate's passthroughs are removed.
    for m in _BEST_COUNT.finditer(live):
        if not _in_board_context(live, m.start(), m.end()):
            continue
        if cdf._is_rejection(live, m.start(1)):
            ungraded.append(f"L{line_of(m.start())}: a best-on-board count "
                            f"stated in order to be rejected, or reported as "
                            f"another surface's words; not graded")
            continue
        if _superseded_by_correction(live, m.start(1), m.end()):
            ungraded.append(f"L{line_of(m.start())}: best-on-board "
                            f"`{m.group(1)} of eight` is the LEFT operand of a "
                            f"`from ... to ...` correction, so it is the "
                            f"value being retired; not graded")
            continue
        raw = m.group(1).lower()
        value = _COUNT_WORDS.get(raw, int(raw) if raw.isdigit() else None)
        if value is None:
            continue
        if value not in (best, earned):
            faults.append((
                line_of(m.start()), "best-on-board count",
                f"claims best-on-board `{raw} of eight`; against the "
                f"{facts['entries']}-entry board the arithmetic count is "
                f"{best} of eight ({', '.join(facts['best']) or 'none'}) and "
                f"the count belonging to OUR MODEL is {earned} of eight -- "
                f"every one of the {best} is a row the decline gate passed "
                f"through as the organisers' own unmodified RANS field"))

    # RULE V3 -- `comparable` is a claim about a RATIO. It is false in the one
    # direction that flatters us whenever the bound EXCEEDS the margin, and the
    # threshold is 100% and not a tuned band: at 177% the bound is not
    # comparable to the margin, it is larger than it.
    if ratio_lo is not None:
        for m in _VALUE_COMPARABLE.finditer(live):
            lo = max(0, m.start() - _VALUE_WINDOW)
            hi = min(len(live), m.end() + _VALUE_WINDOW)
            window = live[lo:hi]
            if not (_VALUE_MARGIN_WORD.search(window)
                    and _VALUE_BOUND_WORD.search(window)):
                continue
            if not _in_board_context(live, m.start(), m.end()):
                continue
            if cdf._is_rejection(live, m.start()):
                ungraded.append(
                    f"L{line_of(m.start())}: `comparable` beside a margin and "
                    f"a bound, stated in order to be rejected or reported as "
                    f"another surface's words; not graded")
                continue
            if ratio_lo <= 100 <= ratio_hi:
                ungraded.append(
                    f"L{line_of(m.start())}: `comparable` beside the margin "
                    f"and the bound, and the admissible ratio "
                    f"[{ratio_lo:.2f}%, {ratio_hi:.2f}%] straddles 100%, so "
                    f"this check CANNOT say the word is false")
                continue
            if ratio_lo > 100:
                faults.append((
                    line_of(m.start()), "bound vs margin",
                    f"calls the seed bound comparable to the margin; over "
                    f"every admissible basis the bound is "
                    f"[{ratio_lo:.2f}%, {ratio_hi:.2f}%] of the margin, so it "
                    f"EXCEEDS the margin it is called comparable to"))
    return faults, ungraded


def check_rank_claim_values() -> Result:
    """Every rank claim's VALUE, graded against the board it is a claim about.

    THE SIBLING, and why they are two checks. `check_rank_claim_surfaces`
    grades FORM -- P(rank 1), the current interval, the sweep token. This
    grades VALUE -- the denominator, the best-on-board count, and whether
    `comparable` is still a true word about the seed bound. On 2026-08-15 the
    form guard read line 502 of `site/closure.html` inside the shipped bundle,
    recognised it as a rank claim, and reported "every travelling surface
    complies" over "rank 1 of 5 ... a seed-uncertainty bound comparable to its
    margin". Both of those are false against the live board and neither is a
    form defect. They are reported separately because they fail separately.

    THREE-VALUED, and it will not PASS from an empty set. If the arithmetic
    module cannot be imported, if a source record is unreadable, if the board
    record is stale, if an archive will not open, or if the sweep finds no rank
    claim at all, this returns UNKNOWN and names what it could not read. That
    is defect class B1 and it is exactly how the sibling arrived at a false
    clean: a check whose cleanest verdict is the one it produces by reading
    nothing.

    WHAT IT CANNOT SEE, stated rather than discovered later. Anything the FORM
    guard cannot see, because the board-context and homonym gates are the same
    two: a claim phrased outside `_RANK_CLAIM`'s vocabulary, anything that is
    not UTF-8 (every compiled PDF here, and `latex/closure_challenge_report.pdf`
    is the corpus's largest single concentration of withdrawn claims),
    untracked files, files over 4 MB, and render-time text. Beyond those: a
    value claim carrying no number at all ("we lead comfortably"); P(rank 1)
    itself, which is MEASURED AND NOT SHIPPED here for the reason
    `check_derived_figures.py` records against the same quantity and this
    check's own measurement confirms; and any wrong figure inside a section
    whose banner carries a withdrawal verb and a date, because a dated
    historical section is exempt by construction.
    """
    name = "rank claims carry the right values"
    cdf, why = _derived_figures()
    if cdf is None:
        return _no_evidence(name, "the value grader could not load its "
                                  "arithmetic and graded nothing",
                            [_DERIVED_FIGURES], [why])

    facts = _closure_facts()
    if facts["stale"]:
        return _no_evidence(
            name, "the board record is not current, so no value could be "
                  "derived to grade any surface against",
            [_PROB_SCRIPT, _PROB_RECORD, _ENTRY_OF_RECORD],
            [f"STALE INSTRUMENT: {s}" for s in facts["stale"]])

    src = cdf.read_sources(REPO)
    quantities, problems, derived = cdf.build_registry(src)
    if problems:
        return _no_evidence(
            name, f"{len(problems)} source record(s) could not be read, so "
                  f"the derived values are incomplete and nothing was graded",
            sorted({r.path for r in src.values() if r.error}) or [_PROB_SCRIPT],
            [f"SOURCE: {p}" for p in problems])

    ratio_lo = ratio_hi = None
    ratio_why = ("the coverage ratio could not be derived from "
                 f"{cdf.SOURCES['seed'][0]} and the board, so `comparable` "
                 f"was not graded on any surface")
    for q in quantities:
        if q.qid == "coverage_pct" and q.bases:
            values = [float(b.value) for b in q.bases]
            ratio_lo, ratio_hi = min(values), max(values)
            ratio_why = (f"`comparable` graded against the seed bound as a "
                         f"percentage of the margin over {derived['leader']}: "
                         f"[{ratio_lo:.2f}%, {ratio_hi:.2f}%] over "
                         f"{len(values)} admissible margin bases")

    tracked = _tracked_files()
    if tracked is None:
        return _no_evidence(name, "git could not be asked which files exist, "
                                  "so no surface was opened",
                            ["git ls-files"])

    travelling = _travelling_names()
    surfaces: list[tuple[str, str, bool]] = []
    opened = skipped = members = 0
    blind: list[str] = list(getattr(_travelling_names, "unopened", []))
    for path in tracked:
        try:
            if not path.is_file():
                skipped += 1
                continue
            if path.stat().st_size > _RANK_MAX_BYTES:
                skipped += 1
                continue
            raw = path.read_bytes()
        except OSError as exc:
            blind.append(f"{_rel(path)}: unreadable ({exc})")
            skipped += 1
            continue
        opened += 1
        text = _surface_text(raw)
        if text is None:
            continue
        surfaces.append((str(path.relative_to(REPO)), text,
                         path.name in travelling))
    archives = _shipping_archives()
    for archive in archives:
        try:
            with zipfile.ZipFile(archive) as zf:
                for info in zf.infolist():
                    if info.is_dir():
                        skipped += 1
                        continue
                    if info.file_size > _RANK_MAX_BYTES:
                        skipped += 1
                        blind.append(f"{_rel(archive)}!{info.filename}: over "
                                     f"{_RANK_MAX_BYTES // 1_000_000} MB, not "
                                     f"opened")
                        continue
                    members += 1
                    opened += 1
                    text = _surface_text(zf.read(info))
                    if text is None:
                        continue
                    surfaces.append(
                        (f"{archive.relative_to(REPO)}!{info.filename}",
                         text, True))
        except (OSError, zipfile.BadZipFile) as exc:
            # NOT a surface with empty text. That is how the sibling swallowed
            # an unreadable archive: an empty string makes no claim, makes no
            # fault, and reads on the report as a clean member.
            blind.append(f"{_rel(archive)}: could not be opened ({exc}), so "
                         f"every member inside it was graded by nothing")

    claims = form_graded = value_graded = fixtures = untriggered = 0
    shipped, internal, ungraded = [], [], []
    for label, text, travels in surfaces:
        if label.startswith(_VALUE_NOT_A_SURFACE):
            fixtures += 1
            continue
        found = _rank_claim_lines(text)
        if not _VALUE_TRIGGER.search(text):
            claims += len(found)
            form_graded += len(found)
            untriggered += 1
            continue
        if found:
            claims += len(found)
            form_graded += len(found)
        faults, notes = _rank_value_faults(text, cdf, facts, ratio_lo, ratio_hi)
        value_graded += len(faults)
        for line, rule, message in faults:
            entry = f"{label}:{line} [{rule}] {message}"
            (shipped if travels else internal).append(entry)
        ungraded += [f"{label} {n}" for n in notes]

    frame = (
        f"frame: {len(tracked)} tracked path(s) and {len(archives)} shipping "
        f"archive(s) considered; {opened} opened ({members} of them archive "
        f"MEMBERS), {skipped} skipped as absent, a directory or over "
        f"{_RANK_MAX_BYTES // 1_000_000} MB; {len(surfaces)} decoded as UTF-8 "
        f"and mention 'rank' or 'overall'; {claims} rank claim(s) found and "
        f"{form_graded} graded for FORM by the sibling check; "
        f"{value_graded} value fault(s) found by {3} value rule(s) "
        f"(board size, best-on-board count, bound-vs-margin); "
        f"{len(ungraded)} passage(s) matched a rule and were NOT graded, "
        f"each named below with its reason; {fixtures} surface(s) under "
        f"{'/'.join(_VALUE_NOT_A_SURFACE)} were not graded at all, because a "
        f"labelled test corpus exists to carry the withdrawn text and "
        f"faulting it is faulting the control; {untriggered} surface(s) "
        f"carried no value-rule trigger at all on the RAW text and were not "
        f"masked (masking only blanks characters, so a trigger absent before "
        f"masking is absent after it). {ratio_why}. The board is "
        f"{facts['entries']} entrants from {_PROB_SCRIPT.name} read by AST, "
        f"so a rank-1 placement is rank 1 of {facts['entries'] + 1}; "
        f"best-on-board is {len(facts['best'])} of {len(facts['cases'])} and "
        f"the count belonging to our model is {len(facts['earned'])}. "
        f"Arithmetic, source records and the strike masker are imported from "
        f"{_rel(_DERIVED_FIGURES)}; no figure is written in this file")

    detail = shipped + internal
    if blind:
        detail += [f"NOT GRADED AT ALL: {b}" for b in blind]
    detail += [f"ungraded: {u}" for u in ungraded[:80]]
    if len(ungraded) > 80:
        detail.append(f"ungraded: ... and {len(ungraded) - 80} more")
    detail.append(frame)

    if not surfaces or not claims:
        return _no_evidence(
            name, "no rank claim was found on any surface, so no value was "
                  "graded",
            ["every tracked file and every shipping archive member"], detail)
    if shipped:
        return Result(name, FAIL,
                      f"{len(shipped)} claim(s) on surfaces that TRAVEL state "
                      f"a value the board contradicts "
                      f"({len(internal)} more on lab records)", detail)
    if blind:
        return _no_evidence(
            name, f"no travelling surface states a contradicted value, but "
                  f"{len(blind)} surface(s) could not be read at all",
            [b.split(":")[0] for b in blind], detail)
    if internal:
        return Result(name, WARN,
                      f"every travelling surface states values the board "
                      f"supports; {len(internal)} lab record(s) do not",
                      detail)
    return Result(name, PASS,
                  f"all {claims} rank claim(s) state a denominator, a "
                  f"best-on-board count and a bound-to-margin comparison the "
                  f"live board supports", detail)


# ---------------------------------------------------------------------------
# THE WORD-FORM PLACEMENT GUARD (Ladder V, V8 fix round, 2026-08-11)
#
# WHY THIS EXISTS AND WHY IT IS NOT check_rank_claim_surfaces. That guard is
# DIGIT-ANCHORED: `rank 1 of 5`, `P(rank 1)`, `best overall number on the
# board`. On 2026-08-11 three defects were found and fixed that it could never
# have fired on, because none of them is a digit claim about US:
#
#   * `DESCRIPTION_DOCUMENT.md:54`  "The rank-3 entry, Wu & Zhang's SST-QCRC"
#   * `CLOSURE_CHALLENGE_STATUS.md:559`  the same sentence, its parent
#   * `DESCRIPTION_DOCUMENT.md:202`  "our margin over the <position>", where the
#     position word stood in for the entrant's name
#
# All three are about Wu & Zhang, whom the board puts at rank 2, except the
# third, which is about Reissmann, whom the board puts at rank 1.
#
# Each states someone ELSE's placement, and each is wrong in the direction that
# flatters us: "rank 3" for a rank-2 entrant, and "runner-up" for the rank-1
# entrant, are true only in a five-way list with our unsubmitted entry on top.
# A wrong ordinal about a competitor is a rank claim about ourselves, made
# without the figure, the interval or the undecided pairs -- which is exactly
# what V8 forbids, arriving in a form V8's guard has no pattern for.
#
# WHAT MAKES THIS CHECKABLE. The published board is a primary artifact on this
# box. Parse its own README table and you have {first author -> rank}; any
# ordinal bound to an entrant either agrees with it or does not. That is
# arithmetic against a source, not a property of our prose, so this is EVIDENCE
# and not PROPERTY.
#
# TWO RULES, and the second is deliberately narrow:
#
#   RULE A  an ordinal BOUND to an entrant must equal that entrant's board
#           rank. Binding is proximity with nothing between: <= 40 characters,
#           no second entrant, no sentence boundary.
#   RULE B  our own comparison whose object is a PLACEMENT WORD instead of a
#           name. This one is narrow on purpose. The broad version ("any
#           absolute designator naming nobody") was measured against this
#           corpus and returned 11 hits of which 11 were noise: the idiom "in
#           the first place", a study that "wrote to a third place", "the gap
#           to first place". A guard that cries wolf gets switched off, and
#           then it guards nothing.
#
# USE AND MENTION, the limit that is not engineered away. Rule A clears a wrong
# ordinal that a correct one within 400 characters adjudicates, so an audit
# record that names a defect and states the truth beside it passes. Rule B has
# no such clause and cannot get one: there is no correct form of "the position
# word" to sit next to. So a record that QUOTES a rule-B defect is flagged by
# it. That is why rule B is a WARN on a lab record and a FAIL only on a surface
# that travels -- on a travelling surface there is no reason to quote a defect,
# and on a lab record there is every reason.
#
# WHOLE TEXT, NOT LINES -- and the first justification for this was WRONG.
#
# It used to say the parent instance on the lab record is defeated by its own
# reflow. It is not. That sentence breaks after "the rank-3 entry (Wu &", which
# is INSIDE the entrant's name and AFTER the first-author surname this check
# keys on -- Wu & Zhang being rank 2 -- so a line-bounded reader catches it too.
# I found that against my own claim and it is retracted here rather than left
# standing in the code a rule-author reads.
#
# The real justification is a live sentence in
# `latex/closure_challenge_report.tex`, which reads "The published entry
# ranked" and then breaks, with "second before round 5 --- Wu & Zhang's
# SST-QCRC" on the next line. There the break falls BETWEEN the ordinal and its
# rank word. Whole-text sees one placement there; line-bounded sees none. That
# sentence is correct, by luck rather than by any instrument, and it was
# invisible to this check until the `ranked <ordinal>` family was added on
# 2026-08-11.
#
# Whitespace is collapsed before matching, and the positive control in
# `sdk/tests/test_rank_claim_surfaces.py` proves the two modes disagree on a
# text where only the wrap differs.
_BOARD_DIR_ENV = "CLOSURE_BENCHMARK_DIR"
_BOARD_PIN = REPO / ("demo-output/website/closure_challenge_submission_round5"
                     "/README.md")
_BOARD_ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*\[([^\],]+)", re.M)

# THE ORDINAL VOCABULARY IS DERIVED FROM THE BOARD, not typed in.
#
# The first grade caught a literal surviving inside the thing built to remove
# literals: `_PLACE` covered 1-5 because today's board has four rows, so on a
# longer board every placement past fifth went unmatched -- silently, which is
# the failure mode this whole check exists to refuse. The board grew from three
# rows to four during this campaign; a fifth entrant is not hypothetical.
#
# The vocabulary now spans 1 .. len(board) + _PLACE_OVER, and the margin is the
# point: an ordinal NAMING A POSITION THE BOARD DOES NOT HAVE is itself a fault
# worth catching ("the rank-9 entry" on a four-row board), so the range has to
# reach past the board rather than stop at it.
_PLACE_OVER = 5
_PLACE_CARDINAL = ("one two three four five six seven eight nine ten eleven "
                   "twelve thirteen fourteen fifteen sixteen seventeen "
                   "eighteen nineteen twenty").split()
_PLACE_ORDINAL = ("first second third fourth fifth sixth seventh eighth ninth "
                  "tenth eleventh twelfth thirteenth fourteenth fifteenth "
                  "sixteenth seventeenth eighteenth nineteenth "
                  "twentieth").split()


@functools.lru_cache(maxsize=8)
def _place_tokens(upto: int) -> dict[str, int]:
    """{token: position} for 1..upto, in every form this corpus writes.

    Digits reach any position; the word forms reach as far as the tables above,
    and the frame line says so rather than leaving a reader to find out.
    """
    tokens: dict[str, int] = {}
    for n in range(1, max(1, upto) + 1):
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(
            n if n % 100 not in (11, 12, 13) else 0, "th")
        tokens[str(n)] = n
        tokens[f"{n}{suffix}"] = n
        if n <= len(_PLACE_CARDINAL):
            tokens[_PLACE_CARDINAL[n - 1]] = n
            tokens[_PLACE_ORDINAL[n - 1]] = n
    return tokens


# The families this pattern reaches, and why these and not the rest.
#
# The first two alternatives are what the corpus already writes -- `rank two
# entry` and `2nd of 5` are in the docket and the report. The rest were added
# 2026-08-11 after an independent grade measured the reach of those two alone
# at 11% on held-out sentences, and after my own held-out set of 46 put it at
# 20%. Each addition was measured for false positives on the whole repository
# before it was kept; each is a family this lab actually writes.
#
# `ranked <ordinal>` is first among them because a LIVE instance of it sits in
# `latex/closure_challenge_report.tex`, wrapped across a line break, in the
# same sentence family as the defect that opened this rung. It is correct, by
# luck. It was invisible.
#
# NOT ADDED, and named so the omission is a decision rather than an oversight:
# medals and podiums, roman numerals, non-English ordinals -- registers this
# lab does not write; markdown or CSV rows, because a numbered table row is not
# distinguishable from any numbered list, and the board's own README is one;
# and `No. N`, which WAS added, measured, and REMOVED -- it fired on a journal
# issue number in a third-party bibliography sitting near a `Wu` citation, and
# an unbounded false-positive source is not worth the one held-out sentence it
# bought. Cheap and safe has to mean safe.
_PLACE_VERB = r"placed|finished|came|came\s+in|took|sits?\s+at|stands?\s+at"

# THE REACH MEASUREMENTS, IN ONE PLACE, WITH THEIR PROVENANCE.
#
# Two failures of reporting are being prevented here at once.
#
# The first: these figures were typed into the docstring, the frame line and
# BASIS separately, alongside a hardcoded count of the patterns -- which is the
# literal problem one level above the ordinal vocabulary the same commit
# removed. Add a family and three surfaces state a wrong count with no test
# reddening. Everything below is now derived: the count from the compiled
# pattern's own named groups, the sentences from this table.
#
# The second, and it is the one a reader is misled by: the first published pair
# was "89% -> 30%", which is an OUTSIDE measurement of the old patterns beside
# an INSIDE measurement of the new ones. Different samples. Held-out sets of
# forty-odd sentences are small, and two honest ones disagree by twenty points
# on the same guard. So the headline is the fixed-set pair -- one sample,
# measured before and after -- and every row names who built it and whether
# they had seen the patterns.
#
# A THIRD failure of reporting, found by a third grade and worth its own note,
# because the fix for the first two did not reach it. The figures were made
# GENERATED so they could not drift between surfaces -- and then went stale
# anyway, in the commit that installed them: rule B was widened in the same
# commit, four of the grader's rule-B sentences moved from missed to caught,
# and nothing re-measured. The table even contradicted its own rule-B row about
# those same five sentences. Generation stopped one level short of the
# measurement.
#
# Every published figure's sentences are now IN THE REPOSITORY --
# `campaign/V16_GRADE_HELDOUT_SETS.py` and `campaign/V16_AUTHOR_HELDOUT_SET.py`,
# each assembled at import so neither is a corpus of faults -- and
# `sdk/tests/test_rank_claim_surfaces.py` recomputes every `now` figure below
# AND `_PLACE_REACH_B` from them, reddening on any disagreement. Storing a
# measurement whose inputs are not in the repository is what made all three of
# these stale.
#
# An earlier version of this comment said "It cannot happen again", which was
# true of three of the four published figures and false of the fourth: rule B's
# `5 of 5` had no committed sentences and no recompute, sitting in the same
# generated paragraph as three rows that had both, with nothing distinguishing
# it -- and it was the very figure whose contradiction made the previous table
# stale. A fourth grade found it. The sentences are committed now; the sentence
# claiming they all were is not repeated.
#
# The `was` column is a measurement against a version of the patterns that no
# longer exists, so it CANNOT be recomputed and is not: it is history, marked
# as such, and the test does not check it.
#
# (sample, who built it, blind to the current patterns?, n, missed by the two
#  ORIGINAL patterns [history, not recomputable], missed by the CURRENT set
#  [recomputed by test])
_PLACE_REACH = (
    ("the grader's first set", "an independent grader", True, 45, 40, 20),
    ("the author's set", "this check's author", True, 46, 37, 14),
    ("the grader's adversarial set", "an independent grader", False, 45,
     None, 42),
)
# Rule B's own reach, kept separate because it is a different rule and because
# the sample is five sentences. (caught, n, who invented them)
_PLACE_REACH_B = (5, 5, "an independent grader, invented blind")

# THE OTHER HALF, AND THE REASON SIX GRADE ROUNDS WERE NEEDED.
#
# Everything above measures a MISS. `_PLACE_REACH` has three rows and
# `_PLACE_REACH_B` has one, and all four answer "how much does this guard fail
# to catch". NOTHING measured how often it binds an ordinal to an entrant in a
# sentence that pins no placement on anybody -- which is the FALSE FAULT, the
# direction this check's own comments call the expensive one, since a rule-A
# fault on a travelling surface is FAIL severity.
#
# That asymmetry is not a gap in the paperwork. It is the mechanism. Six rounds
# of false FAULTs arrived as SURPRISES, each on a sentence nobody had tried,
# because the instrument had no way to report its own worst failure mode: the
# only thing that could report it was a grader, one sentence at a time, and a
# grader who finds one sentence produces one repair, which is how this rung came
# to spend four discriminators on one homonym. Reporting only the easier half is
# what made six rounds necessary. A guard that publishes "caught N of M, and
# falsely faults K of L, in these enumerated shapes" is less impressive and more
# useful, and a reader can act on it.
#
# ONE ROW FROM THE AUTHOR IS NOT A COST, IT IS A SELF-REPORT. This was a single
# row -- the author's own set, built with the pattern list in hand -- until
# grade round 7 built a second one blind and got a worse figure. The
# lab had already solved this for the recall half one screen up, where
# `_PLACE_REACH` publishes three rows each naming its builder and whether they
# were blind, under a note that two honest sets disagree by twenty points; the
# convention did not propagate down here by itself (L-82). It has now.
#
# AND THE SIZE OF THAT DISAGREEMENT WAS AN ARTEFACT OF HOW THE TWO ROWS WERE
# ADMITTED, which is the fifth absolute this rung produced and is filed as D49.
# This comment read, until 2026-08-11: "grade round 7 built a second one blind
# and got a figure 27 POINTS WORSE." That 27 points was measured with a LOOSE
# admission rule on the author's row and a STRICT one on the grader's. The
# author's row admitted a sentence on a raw rule-A pattern match; the grader's
# admitted it on `len(_placements(...)) > 0`, which applies the homonym list,
# the probability form, the of-N form and the linear-algebra subject-head
# discriminator AFTER the match, and is strictly narrower. Of the four
# combinations of {loose, strict} x {author, grader}, the published pairing was
# the only one that was not internally consistent, was the one that maximised
# the gap, and was the one whose Fisher p a chief ruling quoted. Both rows now
# use `_placements`; see `_PLACE_ADMISSION` below for why, and for the range
# the choice moves the spread across.
#
# THE ABSOLUTE THIS ROUND WITHDREW, KEPT AS HISTORY AND NOT AS A CLAIM (L-76,
# and it is the fourth absolute this one rung has produced). The generated
# paragraph below once read, of the author's 20 of 41: "THE SET IS ADVERSARIAL
# AND NOT REPRESENTATIVE -- it is weighted toward the shapes that have already
# broken, so 20 of 41 is a WORST CASE on hard sentences and not a corpus rate."
# The hedge was written to stop a reader overstating the number in the
# PESSIMISTIC direction, and it was falsified in the OPTIMISTIC one: an
# independently built set lands at 19 of 25. "Worst case" was never a property
# of the guard. It was a
# property of how much the sample's builder already knew about the guard. The
# sentence that stood here is quoted above, not repeated: nothing below asserts
# it, and no row here claims to bound the next sample.
#
# THE STRIKE ABOVE SURVIVED D49 AND ITS REASON NARROWED. The clause "the
# independent set APPLIES THIS SET'S OWN ADMISSION RULE, UNCHANGED, and lands
# at 19 of 25" stood in this comment until 2026-08-11 and was false: the two
# sets were admitted by two different predicates. It is quoted here rather than
# deleted, and it is not asserted anywhere. The strike itself does not depend on
# it -- 76% exceeds the author's rate under EVERY common admission rule, which
# is a claim `test_the_precision_spread_is_measured_under_both_rules` executes
# rather than a claim this comment makes.
#
# (sample, who built it, blind to the current patterns?, sentences the set
#  holds, n admitted, falsely faulted)
# The `n admitted` columns are the sentences the guard ACTUALLY EXAMINES --
# `len(_placements(...)) > 0` -- and BOTH rows use that one predicate; see
# `_PLACE_ADMISSION`. The `sentences the set holds` column is published beside
# it because the two are different numbers and a reader is entitled to see how
# many sentences each sample contains as well as how many were scored: the
# grader's 43 were reported for three rounds only as a 25. Both `falsely
# faulted` columns are recomputed from committed sentences by
# `sdk/tests/test_rank_claim_surfaces.py` (L-79), and so are both `n admitted`.
_PLACE_PRECISION = (
    ("the author's non-placement set", "this check's author", False, 41, 28,
     20),
    ("the grader's non-placement set", "an independent grader", True, 43, 25,
     19),
)
# THE ADMISSION RULE IS A CHOICE, IT MOVES THE HEADLINE, AND IT IS STATED
# RATHER THAN INHERITED (D49). A precision denominator has to say which
# sentences counted, and there are two defensible answers:
#
#   * `_placements` -- the sentences in which the guard actually FINDS a
#     placement expression, which is what it then runs its bind loop over.
#   * a raw rule-A pattern match -- every sentence in which the pattern fires
#     at all, before the homonym list, the probability form, the of-N form and
#     the linear-algebra subject-head discriminator get to mute it.
#
# `_placements` IS THE ONE TAKEN, FOR A REASON THAT IS NOT A PREFERENCE:
# `board_placement_faults` -- the function whose output IS the numerator -- is
# itself built on `_placements` and can only fault a sentence that survives it.
# Under the raw rule the numerator and the denominator are computed by two
# different functions, so a sentence the discriminator correctly clears sits in
# the denominator while being structurally incapable of entering the numerator.
# That is not a hard case the guard passed; it is a case the guard was never
# offered, and counting it as a success is counting the discriminator's correct
# silences twice.
#
# THIS IS THE LESS FLATTERING CHOICE AND THAT IS SAID OUT LOUD. It removes 13
# sentences from the author's own denominator -- 8 `linalg-head-listed`, 1
# `coordination`, 4 `homonym`, ALL of them true negatives, so the numerator
# stays 20 -- and the author's published rate therefore moves from 49% to 71%.
# The row that gets worse is this check's author's own.
#
# (rule, author admitted, author falsely faulted, grader admitted, grader
#  falsely faulted) -- recomputed from the same committed sentences as the
# table above, so the sensitivity in the generated paragraph cannot go stale
# the way the reach figures once did.
_PLACE_ADMISSION = (
    ("`_placements`, the sentences this guard actually examines -- IN USE "
     "above for both rows", 28, 20, 25, 19),
    ("a raw rule-A pattern match, looser, and what the author's row alone used "
     "until 2026-08-11", 41, 20, 26, 19),
)
# THE SHAPES, because a rate without them is not actionable, and because the
# ruling that permits a shape to be KNOWINGLY ACCEPTED rather than fixed
# requires it to be counted in the figure AND named here. The counts are
# recomputed from the same committed sentences as the figures by
# `test_every_false_fault_class_is_counted_and_named`, which asserts this table
# equals the measured per-class breakdown for BOTH samples -- so a shape in one
# and missing from the other reddens the suite. It does NOT check that the
# descriptions are right, only that the classes and counts are.
#
# AND IT IS CHECKED AGAINST A SET THIS FILE'S AUTHOR DID NOT BUILD, which is
# the whole point and was the defect grade round 7 filed as D28. When the only
# input was the author's own set, a test named "every false-FAULT class is
# counted and named" could only ever see classes the author had already thought
# of -- L-74's circularity, moved off the figure and onto the test guarding the
# figure. The last two classes below exist because an outsider's sentences
# faulted in shapes nobody here had enumerated; the `grader` column is what
# makes that possible to notice again.
# (class, what it is, how many in the author's set, how many in the grader's)
_PLACE_FALSE_FAULT = (
    ("reduced-relative",
     "an object relative clause with the relativizer deleted, which English "
     "does freely -- with no marker in the clause no cut is made and the "
     "later-noun tie-break resolves to the entrant, who follows the head", 4,
     4),
    ("linalg-head-unlisted",
     "a linear-algebra subject whose head noun is not in `_PLACE_LINALG_NEAR` "
     "-- a kernel, a Gramian, a Laplacian, an array. The clause cuts "
     "correctly and then finds no object, so the discriminator declines to "
     "mute. The list is a word list and no word list is closed", 4, 2),
    ("quotation",
     "a wrong placement QUOTED in order to name or correct it. Rule A has an "
     "adjudication clause and rule B has none, and neither reads intent", 3,
     3),
    ("dated-history",
     "a placement explicitly dated to an earlier board -- `in round 3 ...`, "
     "`... before round 5`. Declared blind spot 9 in the verdict line, and "
     "this is the measurement of it", 3, 4),
    ("abbreviation",
     "a period that ends an abbreviation AND a sentence, now that "
     "`_place_sentence_break` stops treating the first as the second; and an "
     "ordinal sitting inside a citation", 2, 2),
    ("coordination",
     "a coordinated subject whose second conjunct carries the entrant as a "
     "genitive determiner -- it resolves to whichever sits later", 1, 0),
    ("cross-sentence",
     "a semicolon, which `_place_subject_np` treats as a boundary and the "
     "ordinary `_PLACE_BIND` does not, because `_PLACE_SENTENCE` reads only "
     "`[.!?]`", 1, 0),
    ("idiom",
     "`in the first place`, with an entrant inside the 40-character bind. The "
     "broad form of rule B was cut to almost nothing over this idiom; rule A "
     "still meets it", 1, 0),
    ("bibliography",
     "`the Nth entry` of a journal issue rather than of the board", 1, 0),
    # THE TWO THE AUTHOR'S SET HAD NO INSTANCE OF, found by the outside set and
    # named here rather than left to be discovered a seventh time.
    ("other-named-board",
     "a real placement on a DIFFERENT and explicitly named ranking -- another "
     "benchmark, a citation ranking, an internal timing table. This check "
     "reads WHETHER an ordinal is claimed, never WHICH board it is claimed "
     "on, and naming the other ranking in the same sentence does not clear "
     "it. A submission document is a likely place to meet one", 0, 2),
    ("negated-or-questioned",
     "a placement that is DENIED, QUESTIONED or supposed rather than "
     "asserted. Rule A tests neither polarity nor mood, so a sentence saying "
     "the opposite of a placement reads as the placement", 0, 2),
)
# WHICH OF THE OUTSIDE SET'S FALSE FAULTS BELONGS TO WHICH CLASS ABOVE, by that
# set's own sentence labels (`campaign/V16_GRADE_ROUND7_PRECISION_SET.py`). The
# grader's taxonomy and this enumeration are different cuts of the same
# sentences -- the grader classes by what the sentence IS, this table by what
# the guard DOES with it -- so the correspondence is stated per sentence rather
# than per class, and is not a claim that the two vocabularies match. Two of the
# grader's `LINALG` sentences fault, and they fault for different reasons: one
# has its relativizer deleted (restoring the word silences it), the other has a
# head noun off `_PLACE_LINALG_NEAR` (it faults either way). Both were checked
# by execution, not read off the label.
#
# `test_every_false_fault_class_is_counted_and_named` requires this map to
# cover EVERY false fault that set produces. A sentence built by someone else,
# faulting in a shape not enumerated above, is exactly what it must redden on.
_PLACE_FF_OUTSIDE = {
    "NP-01": "reduced-relative",       "NP-04": "linalg-head-unlisted",
    "NP-06": "reduced-relative",       "NP-07": "reduced-relative",
    "NP-08": "linalg-head-unlisted",   "NP-09": "reduced-relative",
    "NP-10": "dated-history",          "NP-11": "dated-history",
    "NP-12": "dated-history",          "NP-13": "dated-history",
    "NP-14": "quotation",              "NP-15": "quotation",
    "NP-16": "quotation",
    "NP-33": "abbreviation",           "NP-34": "abbreviation",
    "NP-37": "other-named-board",      "NP-38": "other-named-board",
    "NP-40": "negated-or-questioned",  "NP-41": "negated-or-questioned",
}


def _place_reach_sentence() -> str:
    """The reach paragraph, generated from `_PLACE_REACH` so it cannot drift."""
    def pct(missed, n):
        return f"{missed} of {n} ({round(100 * missed / n)}%)"
    parts = []
    for name, who, blind, n, was, now in _PLACE_REACH:
        seen = ("invented BLIND, before these patterns existed" if blind
                else "invented WITH the pattern list in hand, adversarially")
        before = f"{pct(was, n)} against the two original patterns, " if was \
            else ""
        parts.append(f"{name} ({who}, {seen}): {before}{pct(now, n)} against "
                     f"the current set")
    fixed = _PLACE_REACH[0]
    return (f"Every `now` figure is RECOMPUTED FROM COMMITTED SENTENCES by "
            f"sdk/tests/test_rank_claim_surfaces.py "
            f"(campaign/V16_GRADE_HELDOUT_SETS.py, "
            f"campaign/V16_AUTHOR_HELDOUT_SET.py); the `before` figures are "
            f"history, measured against patterns that no longer exist, and "
            f"cannot be. "
            f"HEADLINE, on ONE FIXED SET measured before and after so the two "
            f"ends are comparable -- {fixed[0]}, built by {fixed[1]} before "
            f"these patterns existed: {pct(fixed[4], fixed[3])} missed became "
            f"{pct(fixed[5], fixed[3])}. Every sample, because forty-odd "
            f"sentences is a small one and two honest sets disagree by twenty "
            f"points: " + "; ".join(parts) + ". A set built against the "
            f"pattern list measures how much placement language lies outside "
            f"any finite set of regexes, which is unbounded by construction; "
            f"it is reported because it answers how far an adversary must "
            f"walk, and the answer is one sentence. RULE B separately, because "
            f"it is a different rule and the three sets above are rule-A "
            f"sentences: {_PLACE_REACH_B[0]} of {_PLACE_REACH_B[1]} shapes "
            f"caught ({_PLACE_REACH_B[2]}) -- and five sentences is not a "
            f"reach measurement, it is a smoke test, which is the honest name "
            f"for it")


def _place_precision_sentence() -> str:
    """The precision paragraph, generated from `_PLACE_PRECISION` and
    `_PLACE_FALSE_FAULT` so no row can drift from another or from the sentences
    all of them are measured on.

    EVERY COMPARISON HERE IS COMPUTED, not written down. The spread between the
    rows, which row is the higher one, AND HOW MUCH THE ADMISSION RULE MOVES
    THAT SPREAD are derived from the tables: a claim about the samples that a
    future measurement could falsify is the one thing this paragraph is not
    allowed to contain (L-76).

    THE SENSITIVITY SENTENCE EXISTS BECAUSE THIS PARAGRAPH ONCE CONTAINED SUCH
    A CLAIM AND EXECUTION FALSIFIED IT (D49, the fifth L-76 absolute on this
    rung and the first to sit in the reader-facing verdict rather than in a
    comment). The falsified text read: the two samples "differ in that variable
    and in nothing else", and "the same admission rule applies to both". They
    did not; two different predicates implemented that one rule, and the
    difference was worth up to 22 points on the author's own row. Both clauses
    are quoted here rather than deleted and neither is asserted anywhere. The
    replacement does not claim the builder is the only variable -- it REPORTS
    the range the other variable is worth, recomputed from `_PLACE_ADMISSION`
    rather than typed.
    """
    def pct(bad, n):
        return round(100 * bad / n)

    def row(name, who, blind, total, n, bad):
        seen = ("built BLIND -- neither these patterns nor the other sample "
                "was read until after its sentences existed" if blind else
                "built WITH the pattern list and six rounds of grade findings "
                "in hand, adversarially")
        return (f"{name} ({who}, {seen}): falsely faults {bad} of {n} "
                f"({pct(bad, n)}%), those {n} being the sentences the guard "
                f"examines out of the {total} the set holds")
    rows = "; ".join(row(*r) for r in _PLACE_PRECISION)
    rates = [pct(bad, n) for *_h, n, bad in _PLACE_PRECISION]
    high = max(_PLACE_PRECISION, key=lambda r: r[5] / r[4])
    shapes = "; ".join(
        f"{cls} ({a} author / {g} grader -- {what})"
        for cls, what, a, g in _PLACE_FALSE_FAULT)
    spreads = sorted(abs(pct(gb, gn) - pct(ab, an))
                     for _rule, an, ab, gn, gb in _PLACE_ADMISSION)
    alt = "; ".join(
        f"under {rule}: {pct(ab, an)}% ({ab} of {an}) against {pct(gb, gn)}% "
        f"({gb} of {gn}), a {abs(pct(gb, gn) - pct(ab, an))}-point spread"
        for rule, an, ab, gn, gb in _PLACE_ADMISSION)
    return (f"PRECISION, WHICH IS THE HALF THAT WENT UNMEASURED FOR SIX GRADE "
            f"ROUNDS and is the reason there were six: every figure above "
            f"counts a MISS. This one counts a FALSE FAULT, which is the "
            f"expensive direction, a rule-A fault on a travelling surface "
            f"being FAIL severity. {len(_PLACE_PRECISION)} SAMPLES, EACH "
            f"NAMING ITS BUILDER AND WHETHER THEY WERE BLIND, for the same "
            f"reason the reach rows do: {rows}. THEY DISAGREE BY "
            f"{max(rates) - min(rates)} POINTS, and the higher figure is "
            f"{high[0]} ({high[1]}). NEITHER IS A BOUND ON THE NEXT SAMPLE -- "
            f"a set's builder is a variable in the result and a third builder "
            f"would give a third number. THE BUILDER IS NOT THE ONLY VARIABLE, "
            f"AND THIS PARAGRAPH USED TO SAY IT WAS: the ADMISSION RULE -- "
            f"which sentences count toward a denominator at all -- moves the "
            f"spread between these two rows across a {spreads[0]}-to-"
            f"{spreads[-1]} point range, so the builder effect reported above "
            f"is CONFOUNDED with it and no part of the gap can be attributed "
            f"to provenance alone. Measured, on the same committed sentences: "
            f"{alt}. Every sentence scored in either row is one in which this "
            f"guard actually FINDS a placement expression -- "
            f"`len(_placements(...)) > 0`, the same predicate "
            f"`board_placement_faults` is built on, so a row's numerator and "
            f"its denominator come from one function and not two -- and in "
            f"which NO live placement is pinned on a named entrant. ONE RULE, "
            f"BOTH SAMPLES, AND IT IS THE LESS FLATTERING ONE HERE: it drops "
            f"13 sentences the discriminator correctly clears out of the "
            f"author's own denominator, all of them true negatives, moving "
            f"this check's author's row from 49% to 71% while leaving its "
            f"numerator at 20. Neither denominator can be padded with "
            f"sentences the guard never looks at, because those are excluded "
            f"rather than counted clean. Recomputed from "
            f"campaign/V16_PRECISION_SET.py and "
            f"campaign/V16_GRADE_ROUND7_PRECISION_SET.py by "
            f"sdk/tests/test_rank_claim_surfaces.py, which also asserts that "
            f"wrong placements still FAULT and that CORRECT ones stay SILENT, "
            f"so no figure here can be improved by switching the detector off "
            f"or by wedging it open. IN THESE SHAPES, every one of which is "
            f"KNOWINGLY ACCEPTED rather than fixed, with the count each sample "
            f"contributes: {shapes}. The enumeration is checked against BOTH "
            f"samples, so a shape only an outsider thought of cannot go "
            f"missing from it -- the last two classes are there because one "
            f"did. BOTH SETS ARE ADVERSARIAL AND NOT REPRESENTATIVE, each "
            f"weighted toward shapes that have already broken this guard, so "
            f"neither is a corpus rate; the corpus rate is the live sweep this "
            f"same verdict reports")


@functools.lru_cache(maxsize=8)
def _place_pattern(upto: int) -> re.Pattern:
    """The placement forms this corpus writes, over a board-derived range.

    Cached: this compiles a large alternation and `_placements` is called once
    per tracked surface, so rebuilding it per file made the check minutes
    slower than it needed to be.
    """
    alts = "|".join(re.escape(t) for t in
                    sorted(_place_tokens(upto), key=len, reverse=True))
    return re.compile(
        rf"rank(?:ed|s|ing)?[ \-](?P<r>{alts})\b"
        rf"|(?P<o>{alts})[ \-](?:place|ranked)\b"
        rf"|(?:{_PLACE_VERB})\s+(?P<v>{alts})\b"
        rf"|(?P<b>{alts})[ \-](?:overall|best)\b"
        rf"|\bthe\s+(?P<e>{alts})\s+(?:entry|submission|entrant)\b"
        rf"|(?P<s>{alts})[ \-]slot\b"
        rf"|\bposition\s+(?P<p>{alts})\b"
        r"|(?P<u>runner[ \-]?up)"
        r"|(?P<f>front[ \-]?runner)"
        r"|(?P<t>tops?|topping)\s+the\s+(?:published\s+)?(?:board|leaderboard)"
        r"|(?P<T>top)\s+of\s+the\s+(?:published\s+)?(?:board|leaderboard)",
        re.I)
# Homonyms of the WORD. This is an exclusion list and is named as one: it
# excludes SENSES of `rank`, never surfaces. Each was met in this corpus.
_PLACE_PROB = re.compile(r"P\(\s*$", re.I)            # P(rank 1): a probability
# THE DEFERRAL BELOW WAS FALSE UNTIL 2026-08-15 (D151), and it is corrected
# here rather than left standing. It read "OUR claim, owned by the sibling
# guard". The sibling it meant is `check_rank_claim_surfaces`, which grades
# claim FORM and holds no arithmetic over a denominator -- so the deferral
# pointed at a function that did not do the thing it was deferred for, and the
# consequence was measured: no instrument in this lab held a denominator
# predicate, and `rank 1 of 5` was found live on six separate surfaces over
# four days, each repair finding another copy. Rule A binds an ordinal to a
# NAMED PUBLISHED ENTRANT and is structurally incapable of faulting a claim
# about OUR OWN placement, so this was not a gap rule A could ever have closed.
# The receiver now exists and is named: `check_rank_claim_values`, whose
# `_VALUE_BOARD_SIZE` rule grades BOTH digits of `rank N of M`, for our own
# claims and for third-party ones, against the live board.
_PLACE_OFN = re.compile(r"^\s*of\s+\d", re.I)         # rank 1 of 5: OUR claim,
                                                      # graded by
                                                      # check_rank_claim_values
_PLACE_LINALG_R = re.compile(                         # rank-one pure-shear tensor;
    r"^\s*(pure|tensor|shear|out of|approximation|deficient)", re.I)
_PLACE_LINALG_L = re.compile(                         # ...is rank three out of five
    r"(is|are|has|have|of|a|an|exactly|pointwise)\s+$", re.I)
# WHAT DISCRIMINATES THE TWO SENSES, and the first answer here was a false
# statement about the corpus.
#
# It said: "every linear-algebra `rank` in this corpus is a word", and on that
# basis the left-context exclusion was restricted to word numerals -- so that
# "Wu & Zhang ARE RANK 2", a correct placement the adjudication clause depends
# on, would not be swallowed. The restriction was right; the reason was false.
# Linear-algebra rank IS written as a digit here. Swept over `git ls-files`
# piped to /usr/bin/grep -- NOT the `grep` on this shell's PATH, which is a
# function running `ugrep --ignore-files` and would have answered the question
# about a smaller corpus than the one asked about (L-75). Live instances, by
# path rather than by a count that can drift:
# `sdk/scripts/pope_1975_basis_check.py` ("tensor basis has pointwise rank 3"),
# `demo-output/website/dafoam/f6d_random_matrix_uq/rmt_sampler.py` ("Reynolds
# stress is a rank-2 tensor in 3 dimensions"),
# `demo-output/website/campaign/W2_POPE_1975_INTEGRITY_BASIS.md` ("rank 3 out
# of 5 at every cell") and `demo-output/website/agenda/docket.json` ("pointwise
# rank 3 on a unidirectional baseline"). The grade that found this said "four
# times"; that count is not repeated here, because it was not derived and the
# same sweep run mechanically returns a different number depending on whether
# the guard's own source and tests are in the filter.
#
# The real discriminator is not the NUMERAL FORM, it is WHAT IS BEING SAID TO
# BE RANK N. A board placement says an ENTRANT is rank N; a linear-algebra
# sentence says a TENSOR, a basis, a stress is.
#
# AND NEIGHBOURHOOD ALONE IS NOT ENOUGH -- the first repair of this defect used
# a plain 80-character window on BOTH sides, and that window swallowed real
# board placements: an entrant correctly named, given a WRONG ordinal, and
# muted because a turbulence noun sat elsewhere in the same clause. FIVE such
# sentences were executed against that build and all five returned zero faults.
#
# They are NOT written out here. An earlier draft of this comment did write
# three of them out, and they passed the guard only because a correct placement
# happened to sit 276 characters away, inside the _PLACE_ADJUDICATED window of
# 400 -- a margin of 124 characters, which is to say one reflow of this comment.
# Relying on that is the same bet the convention in
# sdk/tests/test_rank_claim_surfaces.py exists to stop the lab making. The five
# live there instead, assembled at run time, as the fixtures of
# `test_a_turbulence_noun_in_the_clause_does_not_mute_a_placement`.
#
# This lab's four entrants are turbulence authors, so a turbulence noun beside
# an entrant's name is the ordinary case here, not the exotic one. A fix that
# trades a latent false positive for a live false NEGATIVE is the worse trade:
# the false positive is loud and the false negative is silent.
#
# SO THE RULE IS THE HEAD OF THE GRAMMATICAL SUBJECT, and getting here took
# three wrong proxies for it. Each was a different way of asking the text
# "which of these two words is more important", when the question the sense
# turns on is "which of them is the sentence ABOUT":
#
#   1. NUMERAL FORM -- right restriction, false reason (above).
#   2. A WINDOW ON BOTH SIDES -- muted real placements whenever a turbulence
#      noun trailed the clause. Five sentences, now fixtures.
#   3. NEAREST WINS, LEFT ONLY -- token distance. It inverts on the ordinary
#      English postmodifier: put an entrant's genitive, agent phrase or
#      relative clause BETWEEN the linear-algebra noun and the ordinal and the
#      surname is nearer, so the guard read a sentence whose subject was a
#      tensor as a claim about a person. Grade round 5 executed six of these:
#      four faulted a correct sentence, two muted a wrong placement.
#
# Distance was never the thing. In `<SUBJECT> ... is rank N` the sense is fixed
# by the HEAD of the subject noun phrase, and English puts postmodifiers AFTER
# that head: everything from the first preposition or relativizer onward
# modifies the subject, it is not the subject. So cut there and read the head
# off what remains. The four false positives of round 5 all have a
# linear-algebra head with the entrant inside a postmodifier; the two false
# negatives all have an entrant head with the linear-algebra noun inside one.
#
# WHAT THIS COSTS, MEASURED. The sentence that stood here said the heuristic
# "has three known blind spots, none of which is a false FAULT", and grade
# round 6 executed it: TWO OF THE THREE ARE FALSE FAULTS, and there was a
# FOURTH not on the list at all. The claim was wrong in the one direction the
# claim existed to reassure about, which is the worst way for a stated cost to
# be wrong, and it survived because nothing measured the false-FAULT direction.
# Now something does: `_PLACE_PRECISION` and `_PLACE_FALSE_FAULT` above carry
# the rates and the shapes, recomputed from `campaign/V16_PRECISION_SET.py` and
# from `campaign/V16_GRADE_ROUND7_PRECISION_SET.py`, which this file's author
# did not build; the verdict line publishes both rows beside the four recall
# figures. The corrected enumeration, executed rather than reasoned:
#
#   1. A subject whose head noun is NOT in `_PLACE_LINALG_NEAR` -- a kernel, a
#      Gramian, a Laplacian -- falls through with no object found, so the
#      discriminator declines to mute and the entrant in the postmodifier
#      binds. THIS IS A FALSE FAULT. It was declared as not one.
#   2. A fronted modifier is skipped only because nothing stands in front of
#      it. This one behaves as declared: not a false FAULT.
#   3. Coordination (`the tensor and Wu's closure are ...`) resolves to
#      whichever sits later. THIS IS A FALSE FAULT. It was declared as not one.
#   4. THE REDUCED RELATIVE, which was not on the list at all: English drops
#      the relativizer in an object relative, and round 6's breaking sentence
#      was round 5's own probe MINUS ONE WORD. With no marker in the clause no
#      cut is made and the later-noun tie-break picks the entrant. A FALSE
#      FAULT.
#
# THE FIFTH DISCRIMINATOR IS NOT BEING BUILT, and that is a ruling and not
# fatigue (`campaign/LADDER_V_TRIPLE_VERIFICATION.md`, "V16's E2 closes by
# measurement"). MEASURED, not asserted: four discriminators were built over
# six grade rounds -- numeral form, a both-sides window, token distance, and
# this subject-head rule -- and a later round broke each of the four on a
# sentence its author had not tried, the fourth on its own predecessor's probe
# with ONE WORD DELETED. Four for four is the record; that a word list standing
# in for a parse must ALWAYS have a fifth sentence is a belief about English
# and is not claimed here. The shapes above are therefore
# KNOWINGLY ACCEPTED: counted in BOTH published precision figures, named in the
# blind-spot enumeration, and pinned by the probes of
# `campaign/V16_GRADE_ROUND6_PROBES.py`, which this suite runs. What closes
# them is a real parse, not a longer list.
#
# Right-hand context keeps its own narrower test (`_PLACE_LINALG_R`, head nouns
# directly after the ordinal).
_PLACE_LINALG_NEAR = re.compile(
    r"tensor|basis|matri(x|ces)|stress|gradient|invariant|operator|eigen"
    r"|representation|jacobian|hessian|subspace|singular value|pointwise"
    r"|deficient|full[- ]rank", re.I)
_PLACE_LINALG_WINDOW = 120
# What introduces a postmodifier: a preposition or a relativizer. Everything
# from here rightward describes the head; it is not the head.
_PLACE_POSTMOD = re.compile(
    r"\b(that|which|who|whose|whom|where|when|in|on|at|of|from|with|by|for"
    r"|to|into|across|within|under|over|between|among|through|via|against"
    r"|about|around|per|versus|than)\b", re.I)
# A clause the copula cannot reach back across. Deliberately NOT the comma:
# the comma is what delimits the appositive in the false-negative shapes, and
# cutting there would throw away the very subject that must be found.
#
# IT CARRIES THE MARKDOWN STRUCTURAL BOUNDARY TOO, and until grade round 6 it
# did not. This constant was `[.!?;:]` and the fallback below carried a comment
# saying it therefore "cannot reach across a sentence". That was an inference
# from punctuation to structure, and in a markdown corpus the inference is
# false: a heading, a list item and a table row all END WITHOUT PUNCTUATION.
# Round 6 executed three shapes that bound an ordinal to an entrant named in
# the PREVIOUS structural unit, at gaps of 65, 69 and 54 characters against a
# `_PLACE_BIND` of 40 -- so the ordinary bind was not what reached across, the
# fallback was. `|` is here because a table cell boundary survives the
# whitespace collapse as itself; `\n` is here because `_place_flatten` now
# PRESERVES the boundaries that do not, as exactly one newline. Executed by
# `TheStructuralBoundaryIsNotAPunctuationMarkTests`.
_PLACE_CLAUSE = re.compile(r"[.!?;:|\n]")
# What ENDS a markdown structural unit on the line before a break, and what
# BEGINS one on the line after it. Anything else -- an ordinary line wrapped
# mid-paragraph -- is a reflow, and joining reflows is the property
# `WholeTextNotLinesTests` pins and this must not cost.
_PLACE_UNIT_END = re.compile(r"^\s{0,3}#{1,6}\s|\|\s*$")
_PLACE_UNIT_START = re.compile(r"\s{0,3}(?:#{1,6}\s|[-*+]\s|\d+[.)]\s|\||>|```)")
_PLACE_SENTENCE = re.compile(r"[.!?][)\"'*`\s]*\s[A-Z(\"'*`]")
# Stands for "a new token starts here" in the boundary probe below. It is a
# constant on purpose: the CASE of the real first character says how the source
# was capitalised and not what the sentence is doing, and reading it was the
# whole of the round-5 boundary defect. It was carrying ONE other signal by
# accident, which making it constant destroyed -- see the next block, which is
# where that signal is now read on purpose.
_PLACE_TOKEN_START = "A"
# THE ONE THING THE REAL CHARACTER *WAS* DOING, which the comment introducing
# the constant above denied in an absolute ("the character's identity was never
# doing any work") that round 6 executed and falsified. A period that ends an
# abbreviation is not a sentence boundary, and making the probe's next
# character unconditionally uppercase turned every one of them into one: two
# real wrong placements sitting directly after `et al.` faulted before this
# rung and went silent after it. So the boundary test asks whether the period
# it found ends an abbreviation before believing it.
#
# WHAT THIS LIST DOES NOT CONTAIN, so the omission is a decision: a single
# capital initial (`Wu, J. rank 2 ...`). Adding `\b[A-Z]\.` would catch the
# citation form, and would also read a genuine sentence end after any
# one-letter word as an abbreviation -- a FALSE FAULT, which is the expensive
# direction, to buy a missed fault, which is the cheap one. It is left out and
# counted: an abbreviation ending in a bare initial is still read as a sentence
# boundary and the placement after it is still missed. Pinned by
# `test_a_bare_initial_is_still_read_as_a_sentence_end`.
#
# AND THE MATCH IS CASE-INSENSITIVE, WHICH HAS ITS OWN PRICE, in the same cheap
# direction: a sentence genuinely ending in one of these words lowercased --
# `... the answer is no.` -- stops being a boundary, so a wrong placement
# opening the next sentence is missed. Case-sensitive matching would cost the
# lowercased citation forms this corpus does write (`liu et al.` is a live
# round-5 probe), and a missed fault is the direction to err in.
_PLACE_ABBREV = re.compile(
    r"\b(?:et\s+al|e\.\s?g|i\.\s?e|cf|vs|viz|ibid|Fig|Figs|Eq|Eqs|Sec|Secs"
    r"|Ref|Refs|No|Nos|pp|ch|Dr|Mr|Mrs|Ms|Prof|St|Jr|Sr|Inc|Ltd|approx"
    r"|resp|etc)\.$", re.I)
# A copula, for the subject-NP bind below. Narrower than `_PLACE_LINALG_L` on
# purpose: that pattern also admits `of`, `a`, `an`, which introduce a
# measurement rather than predicate one of a subject.
_PLACE_COPULA = re.compile(r"\b(is|are|was|were|remains?|stays?)\s+$", re.I)
_PLACE_BIND = 40
_PLACE_ADJUDICATED = 400


def _place_flatten(text: str) -> str:
    """Whitespace collapsed to one space -- except a markdown structural
    boundary, which collapses to one NEWLINE instead.

    WHY NOT JUST COLLAPSE. Collapsing everything to a space is what makes a
    placement split by a reflow still one placement, and that property is
    load-bearing (a live correct instance in `latex/closure_challenge_report.tex`
    is only visible because of it). But it also erases every boundary this
    corpus writes without punctuation, and this corpus is markdown. Round 6
    bound an ordinal to an entrant across a heading, a list item and a table
    row on exactly that erasure.

    EXACTLY ONE CHARACTER EITHER WAY, so every offset in the result is the
    offset the plain collapse gave: the adjudication window, the 130-character
    context slices and the excerpt in the fault message are all unmoved. The
    only consumer that can tell the difference is `_PLACE_CLAUSE`, which is
    where the difference is wanted.

    A run is structural if it spans a blank line, or if the line it leaves ends
    a unit (`_PLACE_UNIT_END`), or the line it enters begins one
    (`_PLACE_UNIT_START`). Anything else is a reflow and still collapses to a
    space.
    """
    # THE SLICES ARE BOUNDED, and the first draft's were not. Writing `before`
    # as `text[:run.start()].rsplit("\n", 1)[-1]` copies the entire prefix once
    # per whitespace run, which is O(n^2) in the size of the surface -- and
    # this runs over every tracked file in the repository on every audit. It
    # was measured, not reasoned about: the corpus sweep went from minutes to
    # tens of minutes. `rfind`/`find` scan to the nearest newline and stop.
    def one(run: re.Match) -> str:
        span = run.group(0)
        if "\n" not in span:
            return " "
        if span.count("\n") > 1:
            return "\n"
        line = text.rfind("\n", 0, run.start()) + 1
        stop = text.find("\n", run.end())
        after = text[run.end():stop if stop != -1 else len(text)]
        if (_PLACE_UNIT_END.search(text[line:run.start()])
                or _PLACE_UNIT_START.match(after)):
            return "\n"
        return " "
    return re.sub(r"\s+", one, text)


def _place_sentence_break(probe: str) -> bool:
    """Is there a sentence boundary in `probe` that a bind must not cross?

    `_PLACE_SENTENCE` alone answers "is there a `.` followed by a token start",
    and with `_PLACE_TOKEN_START` supplying that token start unconditionally
    the answer became yes for every abbreviation-final period as well. This
    asks the second question the round-5 repair dropped: does the period it
    found END AN ABBREVIATION? Executed by
    `TheAbbreviationPeriodIsNotASentenceEndTests`, which carries the two real
    wrong placements that went silent, and the round-5 boundary shapes as
    controls that this has not simply reopened them.
    """
    for found in _PLACE_SENTENCE.finditer(probe):
        if not _PLACE_ABBREV.search(probe[:found.start() + 1]):
            return True
    return False


def _place_subject_np(left: str, names: re.Pattern) -> str:
    """The subject noun phrase of the clause the ordinal sits in.

    The clause containing the copula, cut at the FIRST postmodifier that has a
    candidate noun standing in front of it. The "in front of it" qualifier is
    what lets a fronted modifier be skipped: a sentence-initial prepositional
    phrase has nothing before it, so it cannot be the cut.
    """
    window = left[-_PLACE_LINALG_WINDOW:]
    start = max((m.end() for m in _PLACE_CLAUSE.finditer(window)), default=0)
    clause = window[start:]
    for mark in _PLACE_POSTMOD.finditer(clause):
        head = clause[:mark.start()]
        if _PLACE_LINALG_NEAR.search(head) or names.search(head):
            return head
    return clause


def _place_linalg_subject(left: str, names: re.Pattern) -> bool:
    """Is the thing said to be rank N a linear-algebra object, not an entrant?

    Decided on the SUBJECT NOUN PHRASE, not on token distance -- an entrant
    named inside a postmodifier is not what the sentence says is rank N. Within
    that phrase the later noun is the head, which is where English puts it.
    Covered by `LinearAlgebraRankIsNotAPlacementTests`: the five adversarial
    sentences the presence-only version went silent on, the four digit-form
    corpus shapes it must still mute, and the six round-5 postmodifier shapes.
    """
    head = _place_subject_np(left, names)
    obj = max((m.end() for m in _PLACE_LINALG_NEAR.finditer(head)),
              default=None)
    if obj is None:
        return False
    who = max((m.end() for m in names.finditer(head)), default=None)
    return who is None or obj > who


def _place_family_count() -> int:
    """How many alternatives the rule-A pattern actually has, counted from the
    compiled pattern rather than typed into three docstrings."""
    return len(_place_pattern(_PLACE_OVER + 1).groupindex)


@functools.lru_cache(maxsize=8)
def _place_unnamed(upto: int) -> re.Pattern:
    """RULE B: our comparison, someone else's position, no name INSIDE THE
    PHRASE -- and the phrase is the whole of what it looks at.

    That first line said "nobody's name" until 2026-08-14, and the fault
    message said "without naming who holds it". Both claimed the surroundings,
    and this rule has none: no proximity window, no adjudication clause,
    nothing outside `m.group(0)`. D54.

    Widened 2026-08-11, second grade: nine families had been added to rule A
    and NONE to rule B, so "the miss rate fell" was a statement about one of
    two rules presented as a statement about the check. Four of five fresh
    rule-B shapes passed clean.

    It stays narrower than rule A on purpose and the reason is structural, not
    laziness: rule B has no adjudication clause -- there is no correct form of
    a position word to sit beside a wrong one -- so every widening of it costs
    precision directly, with no way to clear a quotation. The broad version
    ("any absolute designator naming nobody") was measured at 11 hits, 11 of
    them the idiom "in the first place". What is added here is bounded on both
    sides: a comparison OF OURS, whose object is a position, in a small set of
    verbs and designators.

    ITS PRICE, WHICH WENT UNSTATED AND SHOULD NOT HAVE. "Each measured across
    the repository before keeping" was written of these, and it does not hold
    for the frame the repository actually had: the widening faulted SIX new
    places on lab records -- including the grade document that had commissioned
    it, committed twenty-one minutes earlier and present in the tree at the
    time. Every one is a mention under the declared use/mention limit, none is
    on a travelling surface, and the severity scoping did exactly its job. But
    a precision cost of six WARNs is a cost, and a measurement that names no
    moment is a measurement of a repository that no longer exists. After this,
    a measurement here states when it was taken.
    """
    alts = "|".join(re.escape(t) for t in
                    sorted(_place_tokens(upto), key=len, reverse=True))
    who = (rf"runner[ \-]?up|front[ \-]?runner|(?:{alts})[ \-]place"
           rf"|(?:{alts})[ \-]place\s+(?:entry|submission|entrant)"
           rf"|(?:board\s+)?leader\b|top\s+entry\b")
    return re.compile(
        rf"\b(?:our|the)\s+(?:margin|lead|gap|advantage|edge)\b[^.]{{0,25}}?"
        rf"\b(?:over|against|between\s+us\s+and)\s+the\s+({who})"
        rf"|\b(?:beat|beats|beating|clear\s+of|ahead\s+of)\s+the\s+({who})",
        re.I)


# A name has two ends and the heuristic can fall off either. Taking the LAST
# token fixed `van Dijk` (which used to key the board on `van` and bind to every
# occurrence of that word in prose) and created the mirror bug the re-grade
# found: `Reissmann Jr., Fang` keyed on `jr`. Both ends are handled now, and
# both are tests.
_NAME_SUFFIX = re.compile(r"^(jr|sr|ii|iii|iv|phd|md|esq)\.?$", re.I)


def _first_author_surname(cell: str) -> str:
    """The surname this check keys an entrant on, from a board author cell.

    `[Reissmann, Fang, and Sandberg](url)` -> Reissmann. The first author ends
    at the first comma or ` and `; generational and honorific suffixes are
    dropped from the end of that segment; the surname is what is then last, so
    `van Dijk, Smith` gives Dijk and `Reissmann Jr., Fang` gives Reissmann.
    """
    inner = re.match(r"\s*\[([^\]]*)\]", cell)
    who = (inner.group(1) if inner else cell).strip()
    first = re.split(r",| and ", who, maxsplit=1)[0].strip()
    parts = [p for p in re.split(r"\s+", first.strip(" .*_`")) if p]
    while len(parts) > 1 and _NAME_SUFFIX.match(parts[-1].strip(".,")):
        parts.pop()
    return parts[-1].strip(".,") if parts else ""


_BOARD_RANK_COL = re.compile(r"\b(rank|position|place)\b", re.I)
# ANCHORED, after the third grade found this matching unanchored: `Filename`,
# `Hostname` and `Casename` all satisfied "a column naming who the entrants
# are", so `| Rank | Filename |` over two rows parsed as a board of two CSVs.
# Inside the stated concession, but it made qualifying cheaper than the prose
# suggested, and a cheaper decoy is a likelier one.
_BOARD_WHO_COL = re.compile(
    r"\b(authors?|teams?|entrants?|submitters?|groups?|"
    r"(?<![a-z])names?)\b", re.I)
_BOARD_RULE = re.compile(r"^:?-{2,}:?$")
_BOARD_MIN_ROWS = 2


def _table_blocks(lines: list[str]) -> list[list[str]]:
    """Every CONTIGUOUS run of table rows in the file.

    Contiguous matters: a blank line inside a table splits it into two blocks,
    and the re-grade found that a blank line dropped an entrant SILENTLY under
    the old parse. Split here, each half is validated, each half fails, and the
    detector goes OFF instead of grading against three quarters of a board.
    """
    blocks, block = [], []
    for line in [*lines, ""]:
        if line.strip().startswith("|"):
            block.append(line)
            continue
        if block:
            blocks.append(block)
        block = []
    return blocks


def _read_board_table(block: list[str]) -> tuple[list[tuple[int, str]], str]:
    """(rows, "") if this block IS a leaderboard, else ([], why it is not)."""
    rows, header = [], None
    for line in block:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        if all(_BOARD_RULE.match(c) for c in cells if c):
            continue                                   # the |---|---| rule
        if cells[0].isdigit():
            rows.append((int(cells[0]), cells[1]))
        elif header is None:
            header = cells
    if header is None:
        return [], "no header row"
    if not _BOARD_RANK_COL.search(header[0]):
        return [], f"its first column is headed {header[0]!r}, not a rank"
    if not any(_BOARD_WHO_COL.search(c) for c in header):
        return [], f"no column names who the entrants are (header {header})"
    if len(rows) < _BOARD_MIN_ROWS:
        return [], (f"it has {len(rows)} numbered row(s); fewer than "
                    f"{_BOARD_MIN_ROWS} is not distinguishable from a decoy")
    ranks = [n for n, _ in rows]
    if sorted(ranks) != list(range(1, len(ranks) + 1)):
        return [], f"its rank column is not 1..N once each (read {ranks})"
    return rows, ""


def _published_board() -> tuple[dict[str, int] | None, str]:
    """(ranks, head) on success; (None, reason) on ANY failure.

    THIS FUNCTION CANNOT RAISE AN `Exception`, AND IT IS STRUCTURAL RATHER THAN
    A PROMISE. Every line that reads or parses the third-party file lives in
    `_parse_published_board`, which is free to raise whatever it likes; this
    wrapper turns anything it raises into an OFF that names the exception. A
    `KeyboardInterrupt` or a `SystemExit` still propagates, as it must.
    Nothing narrower is honest, and nothing narrower is safe:

    An earlier version said "NEVER raises" and did, twice. First a surname
    carrying a regex metacharacter raised `re.error`; that was fixed by
    escaping, which is a fix for ONE exception type. Then a single non-UTF-8
    byte in the benchmark README raised `UnicodeDecodeError` -- a `ValueError`,
    so `except OSError` did not see it -- out of this function, out of
    `check_board_placement_words`, and out of the whole `self_audit` run,
    taking every sibling check with it. The same crash class, twice, in the
    same function, through different exception types. Catching the second type
    would have invited a third. The blast radius is the one this docstring has
    always described, and the README it reads is a third-party file listing
    international author names -- the likeliest place in this corpus for a
    stray byte to arrive.

    THE SCOPE IS DELIBERATE. Only the read-and-parse of the file we do not
    control is wrapped. The rest of `check_board_placement_words` operates on
    this lab's own data, and a bug there should be LOUD, not swallowed into an
    OFF -- a check that catches everything everywhere hides its own defects,
    which is the failure one layer up from the one being fixed here.

    WHAT IT RETURNS, and what it can still be fooled by. A board only when
    EXACTLY ONE table in the file satisfies every property a leaderboard must
    have -- a rank-headed first column, a column naming who the entrants are,
    at least `_BOARD_MIN_ROWS` numbered rows, ranks reading exactly 1..N once
    each, and first-author surnames that are unique and usable. A decoy table
    that satisfies all of those IS a leaderboard as far as this function can
    tell; four such decoys were built by an independent grader and all four were
    accepted when they stood alone. What it no longer does is trust a HEADING:
    the first repair anchored to any heading containing the word `leaderboard`
    and took the first table after it, and never asked whether what it read was
    a leaderboard. That is now the only question it asks.

    Failure modes measured on synthetic READMEs, each an OFF with a stated
    reason, each a test -- and each CONDITIONAL on no other table qualifying,
    which the list used to read as though it were not:
      * more than one qualifying table, anywhere, in any order;
      * a blank line inside the board table (both halves then fail);
      * a heading elsewhere that also says `leaderboard`;
      * ranks that are not exactly 1..N once each;
      * two entrants sharing a first-author surname, which used to collapse
        into one dict key, dropping an entrant and then FAULTING CORRECT PROSE
        about the survivor -- a false positive manufactured by a parse failure,
        the worst kind, because it discredits the instrument;
      * a surname carrying a regex metacharacter, which used to raise.
    **When something else DOES qualify, the failure above is not an OFF: the
    other table becomes the board, silently.** That is the concession above
    doing exactly what it says, and it is written here too because the itemised
    list is what a reader reaches for.
    """
    try:
        return _parse_published_board()
    except Exception as exc:                                   # noqa: BLE001
        return None, (f"reading the published board raised "
                      f"{type(exc).__name__}: {exc} -- this detector is OFF "
                      f"rather than reporting nothing to find, and rather "
                      f"than ending the audit")


def _parse_published_board() -> tuple[dict[str, int] | None, str]:
    """The read and the parse. MAY RAISE; `_published_board` is the boundary."""
    root = Path(os.environ.get(_BOARD_DIR_ENV,
                               Path.home() / "closure-challenge-benchmark"))
    try:
        text = (root / "README.md").read_text(encoding="utf-8")
    except OSError:
        return None, (f"the benchmark clone is not readable at {root} "
                      f"(${_BOARD_DIR_ENV} or ~/closure-challenge-benchmark)")
    valid, rejected = [], []
    for block in _table_blocks(text.splitlines()):
        rows, why = _read_board_table(block)
        (valid if rows else rejected).append(rows or why)
    if len(valid) > 1:
        return None, (f"{len(valid)} tables in the benchmark README each "
                      f"satisfy every property of a leaderboard; this check "
                      f"will not choose between them")
    if not valid:
        near = "; ".join(rejected[:3]) or "no table rows at all"
        return None, (f"no table in the benchmark README is a leaderboard "
                      f"this check can read -- nearest candidates: {near}")
    rows = valid[0]
    board: dict[str, int] = {}
    for n, cell in rows:
        surname = _first_author_surname(cell)
        if len(surname) < 2:
            return None, (f"row {n}'s author cell yields no usable first-author "
                          f"surname ({cell.strip()!r})")
        key = surname.lower()
        if key in board:
            return None, (f"two entrants share the first-author surname "
                          f"{surname!r} (rows {board[key]} and {n}); this "
                          f"check keys on that surname and cannot tell them "
                          f"apart, so it grades nothing rather than grade one "
                          f"of them wrongly")
        board[key] = n
    try:
        re.compile("|".join(re.escape(k) for k in board))
    except re.error as exc:                                # belt and braces
        return None, f"a board surname will not compile as a pattern: {exc}"
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                              capture_output=True, text=True, timeout=30,
                              check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        head = "unknown"
    return board, head


def _board_pin_date() -> str:
    """The commit date of the frozen benchmark clone, or "" if unavailable.

    READ FROM THE CLONE, NEVER TYPED. BLIND TO item 12 names how old this
    check's board is, and a typed date is exactly the kind of figure L-79
    watched go stale in this same file. The one thing item 12 must never do is
    misreport the age of the thing it exists to disclose, so an unreadable
    clone yields "" and the item says the age is unknown rather than guessing.

    Not folded into `_parse_published_board`: that function's return contract
    is asserted by a dozen tests, and widening it to carry a cosmetic date
    would be a change to the detector in order to improve a comment.
    """
    root = Path(os.environ.get(_BOARD_DIR_ENV,
                               Path.home() / "closure-challenge-benchmark"))
    try:
        return subprocess.run(["git", "show", "-s", "--format=%cs", "HEAD"],
                              cwd=root, capture_output=True, text=True,
                              timeout=30, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


#: The RANKING referent. A committed, dated record of the live board, read for
#: the questions that are about STANDING; the frozen clone above stays the
#: SCORING referent and is read for the questions that are about SCORE.
_RANKING_RECORD = "demo-output/website/campaign/BOARD_MOVED_2026-08-11.md"
_RANKING_RECORD_ENV = "CERTONOMOUS_RANKING_RECORD"


def _ranking_board() -> tuple[dict[str, int] | None, str]:
    """(ranks, provenance) on success; (None, reason) on ANY failure. D55.

    WHY A SECOND REFERENT AND NOT A MOVED PIN. The frozen clone at
    `_BOARD_DIR_ENV` is pinned at `deb9155` because rung V1 needs the eight
    case scores to recompute identically; `BOARD_MOVED_2026-08-11.md` section 4
    says in as many words that the pin must not be moved. But the same file was
    also answering a different question -- how many entrants are there, and who
    stands where TODAY -- and for that question a frozen answer is simply
    wrong. One artifact was serving two purposes and only one of them wanted a
    frozen answer. This function is the other purpose, given its own object.

    WHY NOT FETCH THE LIVE BOARD. A self-audit that needs the network is OFF
    whenever the network is, and its verdict stops being reproducible from the
    tree. The referent is therefore a COMMITTED record, parsed by exactly the
    machinery that parses the pin -- `_table_blocks`, `_read_board_table`,
    `_first_author_surname` -- so a decoy table, a duplicate qualifying table
    or a shared first-author surname fails here the same way it fails there,
    and no second parser can drift from the first.

    THE STALENESS PROBLEM MOVES UP ONE LEVEL RATHER THAN AWAY, and that is not
    a defect hidden in this docstring: this record is dated 2026-08-11 and the
    live board will move again. `_ranking_board_date` reads its date from git
    rather than from a typed string, and the verdict prints it, so the referent
    can be seen to be old instead of quietly believed.

    THE FALLBACK IS NOT SILENT. On failure the caller keeps using the scoring
    pin for everything and the verdict says which referent answered -- a check
    that reads a different board without saying so is the defect this row was
    filed against, and it would be no better for being the new board.
    """
    try:
        return _parse_ranking_board()
    except Exception as exc:                                   # noqa: BLE001
        return None, (f"reading the ranking record raised "
                      f"{type(exc).__name__}: {exc} -- the ranking referent is "
                      f"OFF and the scoring pin is answering for it")


def _parse_ranking_board() -> tuple[dict[str, int] | None, str]:
    """The read and the parse. MAY RAISE; `_ranking_board` is the boundary.

    Deliberately the same shape as `_parse_published_board`, including the
    refusal to choose between two qualifying tables. A ranking referent that
    guesses is worse than one that is OFF, because the whole point of it is to
    be the object someone can check.
    """
    override = os.environ.get(_RANKING_RECORD_ENV)
    path = Path(override) if override else REPO / _RANKING_RECORD
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None, (f"the ranking record is not readable at {path} "
                      f"(${_RANKING_RECORD_ENV} or {_RANKING_RECORD})")
    valid = []
    for block in _table_blocks(text.splitlines()):
        rows, _ = _read_board_table(block)
        if rows:
            valid.append(rows)
    if len(valid) != 1:
        return None, (f"{len(valid)} table(s) in the ranking record satisfy "
                      f"every property of a leaderboard; this referent will "
                      f"not choose between them")
    board: dict[str, int] = {}
    for n, cell in valid[0]:
        surname = _first_author_surname(cell)
        if len(surname) < 2:
            return None, (f"row {n}'s author cell yields no usable first-author "
                          f"surname ({cell.strip()!r})")
        key = surname.lower()
        if key in board:
            return None, (f"two entrants share the first-author surname "
                          f"{surname!r} in the ranking record")
        board[key] = n
    dated = _ranking_board_date()
    return board, (f"{_RANKING_RECORD}"
                   f"{f', dated {dated}' if dated else ' (date unreadable)'}")


def _ranking_board_date() -> str:
    """The commit date of the ranking record, or "" if unavailable.

    READ FROM GIT, NEVER TYPED -- the same discipline `_board_pin_date` follows
    for the pin, and for the same reason: the one thing a referent that exists
    to be current must not do is misreport its own age.
    """
    try:
        return subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", _RANKING_RECORD],
            cwd=REPO, capture_output=True, text=True, timeout=30,
            check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _board_margin() -> tuple[int, int]:
    """(table blocks in the README, blocks that qualify as a leaderboard).

    A live operating margin, printed in the verdict because a third grade
    measured it and it is one edit wide: the real README has two table blocks
    and one qualifies. ONE more rank-headed two-row table anywhere in that
    file -- a historical board, a worked example -- and this detector goes OFF.
    That is the right direction for the failure to run, and it means the guard
    now sits one benchmark-README edit from DISABLED where it used to sit one
    edit from WRONG. Both are worth knowing; only one of them was ever stated.
    """
    root = Path(os.environ.get(_BOARD_DIR_ENV,
                               Path.home() / "closure-challenge-benchmark"))
    try:
        blocks = _table_blocks(
            (root / "README.md").read_text(encoding="utf-8").splitlines())
    except Exception:                                          # noqa: BLE001
        return 0, 0
    return len(blocks), sum(1 for b in blocks if _read_board_table(b)[0])


def _board_names(board: dict[str, int]) -> re.Pattern:
    """Surnames as a pattern, ESCAPED. `Fox[a` used to raise re.error here and
    take the whole audit down with it."""
    return re.compile(r"\b(" + "|".join(re.escape(k) for k in sorted(board))
                      + r")\b", re.I)


def _pinned_board_commit() -> str:
    """The board commit this lab's own claims are dated to, read off the
    travelling package rather than typed in here."""
    try:
        text = _BOARD_PIN.read_text(encoding="utf-8")
    except OSError:
        return ""
    found = re.search(r"closure-challenge-benchmark checkout ([0-9a-f]{40})",
                      text)
    return found.group(1) if found else ""


def _placements(text: str, names: re.Pattern, board: dict[str, int]):
    """(ordinal, entrant or None, that entrant's board rank, offset, token).

    Whole text with whitespace collapsed: a placement that a reflow split
    across two lines is the same placement. A markdown STRUCTURAL boundary is
    the one thing the collapse keeps -- see `_place_flatten`.
    """
    upto = len(board) + _PLACE_OVER
    tokens = _place_tokens(upto)
    found = []
    # Rule A can only fire where an entrant is named, and the placement scan is
    # the expensive part, so a surface that names nobody is skipped rather than
    # swept. The frame line reports this as the denominator it is: placements
    # counted IN SURFACES THAT NAME AN ENTRANT, which is a reproducible rule.
    #
    # THE TEST IS MADE ON THE RAW TEXT, BEFORE FLATTENING, and that is a
    # correctness claim and not only a speed one. `_board_names` compiles
    # `\b(<surname>|...)\b` and every key is a SINGLE TOKEN by construction --
    # `_first_author_surname` returns `parts[-1]`. Collapsing whitespace can
    # neither create nor destroy a match of a single word-boundaried token, so
    # the two tests agree. It is done here because `_place_flatten` runs a
    # Python callback per whitespace run and the first version of this rung
    # paid that on every tracked file in the repository, naming an entrant or
    # not: measured at 2.5x the old sweep before this line moved.
    if not names.search(text):
        return found
    flat = _place_flatten(text)
    for m in _place_pattern(upto).finditer(flat):
        token = m.group(0)
        left = flat[max(0, m.start() - 130):m.start()]
        right = flat[m.end():m.end() + 130]
        if _RANK_HOMONYM.search(left[-60:] + token + right[:60]):
            continue
        if m.group("u"):
            n = 2
        elif m.group("f") or m.group("t") or m.group("T"):
            n = 1
        else:
            value = next(g for g in ("r", "o", "v", "b", "e", "s", "p")
                         if m.group(g))
            n = tokens[m.group(value).lower()]
        if m.group("r"):
            if _PLACE_PROB.search(left) or _PLACE_OFN.match(right):
                continue
            if _PLACE_LINALG_R.match(right):
                continue
            if (_PLACE_LINALG_L.search(left)
                    and _place_linalg_subject(left, names)):
                continue
        who = rank = None
        for seg, side in ((left[-_PLACE_BIND:], "L"), (right[:_PLACE_BIND], "R")):
            hit = None
            for candidate in names.finditer(seg):
                hit = candidate if side == "L" else (hit or candidate)
            if hit is None:
                continue
            between = seg[hit.end():] if side == "L" else seg[:hit.start()]
            # The boundary test needs ONE character of what follows: a
            # sentence ends at ". " + a capital, and the slice between the
            # ordinal and the name stops just short of that capital. Found by
            # executing the comment that claims a sentence boundary blocks the
            # bind -- "They are at rank 4. Wu and Zhang run SST-QCRC." bound
            # across the full stop, because `between` was ". " and the W lived
            # outside it.
            #
            # IT IS SYMMETRIC, and the first repair patched one side only. On
            # the LEFT the capital that closes the boundary is the ORDINAL's
            # own first letter, so "Wu and Zhang did the duct case. Rank 4 is
            # Montoya's." bound across the stop for the identical reason --
            # executed against the patched-right/unpatched-left build, that
            # sentence and two more returned one rule-A fault each.
            #
            # AND SYMMETRY WAS NOT THE INVARIANT EITHER. Appending the REAL
            # next character made both sides carry one -- true, and it left the
            # defect standing, because `_PLACE_SENTENCE` closes a boundary only
            # on an UPPERCASE character and neither appended character reliably
            # is one. On the left it is the ordinal token's first character: a
            # DIGIT in every `Nth place` form, lowercase for a sentence-initial
            # rank token or a lowercased word-form ordinal. On the right it is
            # the matched surname's first character, and surnames match
            # case-insensitively, so a lowercase citation form defeated it.
            # Grade round 5 executed six shapes that bound across a full stop.
            #
            # The character's CASE carries no information about the sentence.
            # Both `token` and `hit.group(0)` are matches of word-boundaried
            # patterns, so what the appended character MEANS is "a new token
            # starts here" -- and whether the source happened to capitalise
            # that token is an accident of formatting. So append a character
            # that stands for the token start, and the test stops depending on
            # a case it cannot control. The positive controls that the guard
            # has not simply stopped binding after every full stop are in
            # `test_a_boundary_binds_nothing_even_when_the_name_starts_the_sentence`.
            #
            # THE SENTENCE ABOVE ONCE READ "the character's identity was never
            # doing any work", AND ROUND 6 EXECUTED IT. It was doing exactly
            # one job: an abbreviation supplies a lowercase next character and
            # a sentence supplies an uppercase one, so reading the real
            # character told abbreviation-final periods from sentence-final
            # ones by accident. Replacing it with a constant `A` made every
            # `et al. ` a sentence boundary and two real wrong placements went
            # silent. The bounded claim, which is what should have been written
            # the first time: the character's CASE is not evidence, and the
            # QUESTION its case happened to answer is now asked directly by
            # `_place_sentence_break`. Executed both ways by
            # `TheAbbreviationPeriodIsNotASentenceEndTests`.
            probe = between + _PLACE_TOKEN_START
            if names.search(between) or _place_sentence_break(probe):
                continue
            who, rank = hit.group(0), board[hit.group(0).lower()]
            break
        # THE SAME PROXY FAILURE, ONE LEVEL UP -- and the round-5 grade did not
        # see it. `_PLACE_BIND` is a distance standing in for "this ordinal is
        # predicated of that entrant", so a postmodifier between the subject and
        # the copula pushes the subject out of reach: in the two shapes that
        # grade filed as E2 false negatives the entrant sits 69 and 73
        # characters from the ordinal, and BOTH stay silent with the
        # linear-algebra discriminator answering correctly. Distance was not
        # what muted them.
        #
        # So when nothing bound and the ordinal is predicated by a copula, ask
        # the subject noun phrase who the subject is -- the same question E2
        # answers, and `_place_subject_np` already computes it.
        #
        # HOW FAR IT CAN REACH, at the width it has rather than the width first
        # claimed for it. This comment read "This cannot reach across a
        # sentence: the phrase is cut at `_PLACE_CLAUSE` first", and round 6
        # executed it: `_PLACE_CLAUSE` was `[.!?;:]`, so what it could not cross
        # was a PUNCTUATION MARK, and a markdown heading, list item and table
        # row end without one. Three shapes crossed a structural boundary at
        # gaps of 65, 69 and 54. The true statement now, at the width it has
        # and no wider: the phrase is cut at `_PLACE_CLAUSE`, which is
        # `[.!?;:|\n]`, and `_place_flatten` writes exactly these as that
        # newline -- a blank line, the end of an ATX heading or a table row,
        # and the start of a heading, list item, ordered-list item, table row,
        # block quote or fence. THAT LIST IS WHAT IT CANNOT CROSS. What it CAN
        # still cross, named so the omissions are decisions: a comma,
        # deliberately, because the comma is what delimits the appositive the
        # fallback exists for; a line wrapped mid-paragraph, deliberately,
        # because joining reflows is the property that makes the live instance
        # in `latex/closure_challenge_report.tex` visible at all; a setext
        # heading and its underline, which join; and a list item lazily
        # continued onto an unindented next line with no blank line between,
        # which markdown itself treats as one item. Executed both ways by
        # `TheStructuralBoundaryIsNotAPunctuationMarkTests`: three shapes that
        # must now be silent, four controls -- the punctuated twins, and the
        # two round-5 false negatives this fallback exists for, which must
        # still fault -- and two more asserting the reflow still joins and no
        # offset moved.
        #
        # The entrant must be the HEAD of that phrase -- last, with no
        # linear-algebra noun after it -- or the sentence is about the object,
        # not the person.
        if who is None and _PLACE_COPULA.search(left):
            phrase = _place_subject_np(left, names)
            subject = None
            for candidate in names.finditer(phrase):
                subject = candidate
            if subject is not None and not _PLACE_LINALG_NEAR.search(
                    phrase[subject.end():]):
                who = subject.group(0)
                rank = board[who.lower()]
        found.append((n, who, rank, m.start(), token, flat))
    return found


def board_placement_faults(text: str, board: dict[str, int],
                           ranking: dict[str, int] | None = None
                           ) -> tuple[list[str], list[str]]:
    """(rule A faults, rule B faults) for one surface.

    TWO REFERENTS, AND THE SPLIT IS DELIBERATE (D55, 2026-08-14). `board` is
    the SCORING referent -- the frozen benchmark clone -- and it keeps every
    question about WHO IS WHO: which surnames are entrants, and what rank the
    scored board binds each of them to. `ranking`, when supplied, is the
    RANKING referent (`_ranking_board`), and it answers the one question in
    here that is about STANDING rather than score: HOW MANY POSITIONS EXIST.

    That question was being answered by the scoring pin, which is D55's
    sentence exactly -- a check that RANKS reading a referent that SCORES. The
    pin lists four entrants; the live board has six. So a sentence placing an
    entrant at rank 5 was told, by this function, that rank 5 "is a position
    this board does not have", which is false of the world and was produced
    purely by asking a frozen scoring artifact a live standing question.

    WHAT WAS DELIBERATELY *NOT* RE-POINTED, and the measurement that decided
    it. Swapping the whole `board` argument to the live six-entry record was
    executed across the tracked corpus on 2026-08-14 and RE-EXECUTED at
    `48d3f05a` over the same 1455 opened surfaces: rule-A faults go from
    **2 to 68**. THE TWO SETS ARE DISJOINT, and the first writing of this
    docstring got that wrong by calling the difference "the 66 additions". It
    is not 66 additions: the move CLEARS both existing faults -- they sit in
    `docs/DOCKET.md` and `docs/INSTRUMENT_INTEGRITY_LEDGER.md` and are faults
    only because those sentences are correct of the LIVE board -- and raises
    **68 wholly new ones**, neither original file among them. Nor are the 68
    all one kind, and "overwhelmingly dated history" is not supported at that
    width either. Counted: **50 are dated records** -- evaluation protocols, methods comparisons and campaign
    write-ups describing the board as it stood when they were written, which
    this check has no discriminator for (its own BLIND TO item 9 says so) --
    and **18 are this check's OWN measuring apparatus**, 14 in
    `sdk/tests/test_rank_claim_surfaces.py`, 3 here in `self_audit.py`, and 1
    in `campaign/V16_AUTHOR_HELDOUT_SET.py`. That second group is not a
    footnote: it is D55's stated reason for the gate, executed. The held-out
    sets are written against whatever `_published_board` returns, so moving the
    binding moves the ruler and the sample together, and the resulting figure
    would be transcription fidelity worn as reach (L-74). Re-pointing the
    binding wholesale would therefore fault 50 correct dated records AND
    regrade the instrument against itself, at a price of clearing two live
    faults -- which is not a repair. D55's gate forbids it
    until a rule-A held-out set of LIVE-BOARD sentences exists. None does. So
    the identity binding stays on the pin, the existence question moves, and
    the fault message names which referent answered.
    """
    names = _board_names(board)
    found = _placements(text, names, board)
    disagree, unnamed = [], []
    for n, who, rank, at, token, flat in found:
        if who is None or n == rank:
            continue
        # A passage that ALSO states the entrant's real rank is adjudicating a
        # wrong ordinal, not asserting one -- which is what the audit records
        # that found these defects do, and they must not be faulted for it.
        if any(other == rank and named and named.lower() == who.lower()
               and abs(where - at) <= _PLACE_ADJUDICATED
               for other, named, _, where, _, _ in found):
            continue
        # THE EXISTENCE QUESTION IS THE RANKING REFERENT'S, NOT THE PIN'S.
        # `positions` falls back to the pin when no ranking referent could be
        # read, and the message says which one answered either way -- a fault
        # that does not name the board it was measured against is the thing
        # D55 was filed about, and it would be no better for naming the new
        # board silently than it was for naming the old one silently.
        positions = len(ranking) if ranking else len(board)
        which = ("the live-board record" if ranking
                 else "the frozen scoring pin")
        beyond = ("" if n <= positions else
                  f" -- and rank {n} is a position this board does not have "
                  f"({which}, {positions} entrants)")
        # THE STRUCTURAL MARKER DOES NOT REACH THE READER. `flat` now carries
        # a newline where a markdown structural boundary was, and this excerpt
        # is sliced straight out of it -- so without this the one live fault in
        # the corpus grew a line break in the middle of a one-line message.
        # Caught by the old-vs-new sweep, which reported one surface changed
        # and it was this, cosmetic: same binding, same count, different text.
        # Rendering the marker back to the space it stands for makes every
        # fault message BYTE-IDENTICAL to the build before this rung, which is
        # a stronger claim than "no verdict moved" and is the one that should
        # be made about a change to a shared representation.
        excerpt = flat[max(0, at - 60):at + 60].replace("\n", " ").strip()
        disagree.append(f"{token!r} is bound to {who}, whom the published "
                        f"board puts at rank {rank}{beyond}: "
                        f"...{excerpt}...")
    # RULE B GETS THE PLAIN COLLAPSE, deliberately. It has no clause rule, no
    # boundary rule and no bind -- it is a single pattern match over the flat
    # text -- so the structural newline `_place_flatten` preserves buys it
    # nothing, and giving it one could only take something away, by breaking a
    # `\s+` inside its own alternation across a heading. Rule B's behaviour is
    # therefore byte-identical to the build before this rung, which is what the
    # old-vs-new corpus sweep shows.
    flat = re.sub(r"\s+", " ", text)
    for m in _place_unnamed(len(board) + _PLACE_OVER).finditer(flat):
        # THE MESSAGE SAYS WHAT THE RULE TESTED, AND NOTHING MORE (D54,
        # 2026-08-14). It used to end "without naming who holds it", which is
        # a claim about the SURROUNDINGS -- and rule B has no surroundings: no
        # proximity window, no adjudication clause, nothing outside
        # `m.group(0)`. Executed at `5c9c63fb`: `"Yang: our margin over the
        # leader is 0.0027."` faults with the holder's name one character
        # away, identically to a surface that names nobody anywhere. The rule
        # was NOT widened to earn the old sentence -- retuning a detector so
        # the author's own prose passes is how a guard gets tuned to a number,
        # and rule B has no sample in this lab against which a widening could
        # be shown not to lose the anonymous cases it exists to catch. Whether
        # it SHOULD gain a proximity clause is its own row (D77), not a change
        # smuggled into a message. THAT NUMBER IS NOT THE ONE THIS COMMENT WAS
        # WRITTEN WITH: it said D63, an ID this work RESERVED BY CITATION while
        # it sat uncommitted, and which the fleet allocated to an unrelated
        # auto-stop defect before the work was ever recovered. A pointer into
        # an append-only register is only sound once the row exists.
        unnamed.append(f"{m.group(0)!r} makes a comparison of ours against a "
                       f"board POSITION where the phrase itself could name the "
                       f"entrant. Rule B tested this phrase and nothing else: "
                       f"it has no proximity window, so whether the holder is "
                       f"named in the next word or nowhere in the corpus is "
                       f"not what faulted here")
    return disagree, unnamed


def check_board_placement_words() -> Result:
    """Every ordinal this lab pins on an entrant agrees with the published
    board, and no comparison of ours takes a placement word for an opponent.

    THE RULE it serves is V8's, amended 2026-08-10: a rank claim carries
    P(rank 1), its interval and the undecided pairs. A wrong ordinal about a
    competitor is a rank claim about US wearing someone else's name, and it
    arrives carrying none of the three.

    WHAT IT CANNOT SEE, stated rather than discovered later, LARGEST FIRST:
    ANY placement phrased outside the rule-A patterns below. The three
    held-out sets are RULE-A sentences; rule B is a different rule with its own
    much smaller measurement, and until 2026-08-11 it had not been widened at
    all while nine families were added to rule A -- so "the miss rate fell" was
    a statement about one of two rules worn as a statement about the check.
    The figures themselves are NOT written here: they live in
    `_PLACE_REACH` with their provenance and are generated into the verdict and
    into BASIS by `_place_reach_sentence`, and the pattern count is counted from
    the compiled pattern by `_place_family_count`. A second grade found the
    count and three miss rates typed into three surfaces each with no test that
    they still described the patterns -- the literal problem one level above
    the ordinal vocabulary this same function had just been freed from.

    What is still unreachable:
    an ordinal used as a bare noun ("the board's fourth"), "are in fourth",
    "#N", a bare parenthetical ordinal, medals and podiums, roman numerals,
    non-English ordinals, and markdown or CSV rows -- the last omitted on
    purpose, because a numbered table row is not distinguishable from any
    numbered list and the benchmark's own board is one.

    AND WHAT IT INVENTS, which for six grade rounds nothing measured. Every
    figure named above counts a MISS. `_PLACE_PRECISION` and
    `_PLACE_FALSE_FAULT` count the other direction -- how often this check
    faults a sentence that pins no placement on anybody -- on TWO held-out sets
    of non-placements, one built by this check's author and one built blind by
    an independent grader, committed at `campaign/V16_PRECISION_SET.py` and
    `campaign/V16_GRADE_ROUND7_PRECISION_SET.py` and both recomputed by the
    suite, with the shapes enumerated rather than summarised and each shape
    carrying the count from each sample. The two rows disagree, which is the
    point of having two: a cost measured only by the party being measured is a
    self-report, and the independent row is the higher one (L-82). That
    asymmetry, not any one regex, is why this rung took six rounds: the
    instrument could only report the half that was easier to report. The rate
    and the shapes are generated into the verdict and into BASIS beside the
    recall figures.

    GREEN HERE IS NOT COVERAGE. It means no placement matching these patterns
    disagrees with the board, which is a narrower statement than it looks: the
    `ranked <ordinal>` family was added on 2026-08-11 only because a live and
    correct instance of it had been sitting in
    `latex/closure_challenge_report.tex`, wrapped across a line break, in the
    same sentence family as the defect that opened this rung, invisible.

    Then: word forms of positions past the number-word tables, and any
    position past the board's own length plus `_PLACE_OVER`; RELATIONAL
    comparatives -- "ahead of", "behind", "trails",
    "leads", "next-best" -- which need both operands resolved and cannot be
    checked against a single board rank; any entrant referred to by a co-author
    rather than the first author on their board row; a wrong ordinal that a
    nearby correct one
    adjudicates away, since adjudication is judged by proximity and not by
    grammar; the difference between USING a rule-B phrase and QUOTING one,
    which is why rule B is a WARN on a lab record and a FAIL only where the
    surface travels; non-UTF-8 surfaces, untracked files and archive members,
    none of which it opens; and whether a placement is DATED -- a round-3
    section saying "we lead on 5 of 8" is a historical record and this check
    would call it a claim if the pattern reached it, which is the other reason
    RULE B is narrow.
    """
    title = "placement words agree with the published board"
    board, head = _published_board()
    if board is None:
        return Result(title, WARN,
                      f"this detector is OFF, not reporting nothing to find: "
                      f"{head}")
    # THE SECOND REFERENT (D55). Read here rather than inside the loop so the
    # verdict can name it once, and so a record that cannot be read degrades to
    # "the pin answered the standing question too, and here is why" instead of
    # taking the whole check OFF -- an unreadable ranking record is a worse
    # verdict, not no verdict.
    ranking, ranking_note = _ranking_board()
    pinned = _pinned_board_commit()
    tracked = _tracked_files()
    if tracked is None:
        return Result(title, WARN,
                      "could not enumerate tracked files (git unavailable): "
                      "this detector is OFF, not reporting nothing to find")

    travelling = _travelling_names()
    names = _board_names(board)
    surveyed = opened = naming = 0
    shipped, internal, skipped = [], [], []
    for path in tracked:
        try:
            if not path.is_file() or path.stat().st_size > _RANK_MAX_BYTES:
                continue
            raw = path.read_bytes()
        except OSError:
            continue
        if not any(w in raw.lower() for w in (b"rank", b"runner", b"place",
                                              b"top ")):
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        opened += 1
        if names.search(text):
            naming += 1
        # WHAT THIS CATCH ACTUALLY GUARANTEES, stated at the width it has
        # rather than as an absolute (L-76): any `Exception` raised while
        # sweeping ONE surface is confined to that surface, so a single bad
        # document cannot take every OTHER check in this file down with it.
        # It does NOT cover a `BaseException` -- KeyboardInterrupt and
        # SystemExit still propagate, deliberately -- and it does not cover
        # anything raised BEFORE this loop (`_published_board`,
        # `_tracked_files`, `_board_names`), which are guarded separately
        # above. Executed by `ASkipIsNotAnAgreementTests
        # ::test_a_raise_on_only_the_faulty_surface_is_not_a_pass`, which
        # injects a raise on one document and shows the other surfaces still
        # reach a verdict. But A SURFACE THAT
        # COULD NOT BE READ IS NOT A SURFACE THAT AGREES, and for one round
        # this catch reported the skip in the frame while leaving the STATUS
        # green: inject a defect that raises on exactly the document carrying a
        # fault and the verdict read "all 0 placement expression(s) agree with
        # the published board". That is the green that means "I looked at
        # nothing", which this check refuses in its own words two paragraphs
        # up. The skip is counted, NAMED, and it reaches the verdict below.
        try:
            surveyed += len(_placements(text, names, board))
            disagree, unnamed = board_placement_faults(text, board, ranking)
        except Exception as exc:                   # noqa: BLE001 -- see above
            skipped.append(f"{path.relative_to(REPO)}: could not be swept "
                           f"({type(exc).__name__}: {exc}) -- NOT counted as "
                           f"agreeing with the board")
            continue
        if not disagree and not unnamed:
            continue
        label = str(path.relative_to(REPO))
        bucket = shipped if path.name in travelling else internal
        bucket.extend(f"{label}: {fault}" for fault in disagree + unnamed)

    order = ", ".join(f"{who} {rank}" for who, rank
                      in sorted(board.items(), key=lambda kv: kv[1]))
    pin_note = ("at the commit this lab's claims are dated to"
                if head == pinned else
                f"WHICH IS NOT the pinned {pinned[:8] or 'unknown'} this lab's "
                f"claims are dated to")
    pinned_on = _board_pin_date()
    pin_age = f", dated {pinned_on}" if pinned_on else " (date unreadable)"
    blocks, qualifying = _board_margin()
    # TWO REFERENTS, NAMED (D55). The verdict says which board answered which
    # question, because until 2026-08-14 one artifact answered both and nothing
    # said so.
    # The line must still BEGIN with `frame:` -- six tests select it out of the
    # detail list with `startswith("frame:")`, and prepending to it turned the
    # verdict's frame into a line nothing could find.
    two_referents = (
        f"TWO REFERENTS: the SCORING pin binds names to ranks; the "
        f"RANKING referent answers how many positions exist, and is "
        + (f"{ranking_note}, reading {len(ranking)} entrants"
           if ranking else f"OFF -- {ranking_note}") + ". "
        f"The pin is NOT stale and must not be moved (rung V1 needs the case "
        f"scores to recompute identically); it is simply not a rank oracle. "
        f"NOT re-pointed: the name-to-rank binding, deliberately -- swapping "
        f"it to the live board was measured across this corpus on 2026-08-14 "
        f"and re-measured at 48d3f05a, and takes rule-A faults from 2 to 68 "
        f"over DISJOINT sets: both current faults clear and 68 new ones "
        f"appear, 50 of them dated records this check cannot tell from a live "
        f"claim (item 9) and 18 of them inside its own held-out sets and "
        f"source, where moving the binding moves the ruler with the sample. ")
    frame = (f"frame: " + two_referents
             + f"board read from the benchmark's own README table at "
             f"{head[:8]} ({pin_note}) -- {order}. MARGIN: that README has "
             f"{blocks} table block(s) and {qualifying} qualif"
             f"{'ies' if qualifying == 1 else 'y'}; one more rank-headed "
             f"two-row table in it and this detector goes OFF, so the guard "
             f"sits one third-party edit from DISABLED where it used to sit "
             f"one edit from WRONG. {opened} tracked UTF-8 "
             f"surface(s) carrying rank/runner/place/top opened, of which "
             f"{naming} name a board entrant and were swept for placements "
             f"(rule A cannot fire where nobody is named; rule B's narrower "
             f"pattern runs on all {opened}); {surveyed} placement "
             f"expression(s) found in those {naming} -- that pair is the "
             f"denominator and its selection rule, stated so it reproduces. "
             f"Whole-text with whitespace "
             f"collapsed so a reflowed one still binds; ordinals derived from "
             f"the board's own length, 1..{len(board) + _PLACE_OVER} here, in "
             f"digit and word form (word forms exist to "
             f"{len(_PLACE_CARDINAL)}); {len(skipped)} surface(s) skipped after "
             f"raising -- a skip is NOT an agreement and is carried into the "
             f"verdict, not only into this line. "
             f"BLIND TO, LARGEST FIRST: (1) ANY placement phrased outside this "
             f"check's {_place_family_count()} RULE-A patterns. The three "
             f"held-out sets below are RULE-A sentences, each pinning a WRONG "
             f"placement on a NAMED entrant; rule B is measured separately and "
             f"on a far smaller sample. {_place_reach_sentence()}. "
             f"{_place_precision_sentence()}. "
             f"STILL UNREACHABLE: an ordinal as "
             f"a bare noun (the board's fourth), 'are in fourth', #N, a bare "
             f"parenthetical ordinal, medals and podiums, roman numerals, "
             f"non-English ordinals, and markdown or CSV rows -- the last "
             f"omitted deliberately, a numbered table row being "
             f"indistinguishable from any numbered list and the benchmark's "
             f"own board being one. The 'ranked Nth' family was added only "
             f"because a live correct instance of it had been sitting unseen "
             f"in latex/closure_challenge_report.tex. (2) word forms of "
             f"positions past "
             f"{len(_PLACE_CARDINAL)}, and any position past "
             f"{len(board) + _PLACE_OVER} in any form -- the vocabulary is "
             f"derived from this board's length plus a margin, not fixed at "
             f"five as it was until 2026-08-11. (3) relational comparatives -- "
             f"ahead of, behind, trails, leads, next-best -- which need both "
             f"operands and cannot be checked against one board rank. (4) an "
             f"entrant named by a co-author rather than the first author. "
             f"(5) rule B cannot tell USING a phrase from QUOTING one. "
             f"(6) adjudication is 400-character proximity and not grammar, so "
             f"a correct rank near a wrong one clears it -- RULE A ONLY: rule "
             f"B has no window at any distance, and faults a phrase whose "
             f"holder is named one character away exactly as it faults one "
             f"naming nobody anywhere; and a board surname "
             f"that is also an ordinary English word would over-bind, since "
             f"surnames match case-insensitively -- making them case-sensitive "
             f"was measured to cost one real binding in this corpus and was "
             f"not taken. (7) the travelling/lab-record split is matched by "
             f"BASENAME against the {len(travelling)} names drawn from "
             f"shipping archives and submission packages, so a file merely "
             f"SHARING a name with a packaged one inherits the FAIL severity "
             f"-- the error runs conservative, upgrading WARN to FAIL rather "
             f"than the reverse, but it is a name collision doing a "
             f"provenance check's job. (8) files over "
             f"{_RANK_MAX_BYTES // 1_000_000} MB, non-UTF-8 surfaces, "
             f"untracked files and archive members, none of which it opens. "
             f"(9) whether a placement is dated history rather than a live "
             f"claim. (10) WHICH BOARD a placement is about: an ordinal on a "
             f"different and explicitly named ranking -- another benchmark, a "
             f"citation ranking, an internal timing table -- reads exactly "
             f"like an ordinal on this one, and naming the other ranking in "
             f"the same sentence does not clear it. Counted above as "
             f"`other-named-board`. (11) POLARITY AND MOOD: a placement that "
             f"is denied, questioned or supposed reads as one asserted, "
             f"because rule A tests neither. Counted above as "
             f"`negated-or-questioned`. Items 10 and 11 are here because a "
             f"held-out set built OUTSIDE this check faulted on them and the "
             f"nine above did not describe either -- which is what an outside "
             f"sample is for. (12) WHETHER ITS OWN BOARD IS STILL CURRENT. "
             f"Item 9 is this hazard one level down, for the SENTENCE -- "
             f"whether a placement is dated history; this is the same hazard "
             f"for the REFERENT. The {len(board)} entrants above were read "
             f"from a clone frozen at {head[:8]}{pin_age}, and nothing in this "
             f"check can tell whether that board has moved since: it compares "
             f"sentences to the pin and never asks the pin's age. If the board "
             f"HAS moved the error runs BOTH ways -- a sentence true of the "
             f"live board FAULTS at the severity of the surface carrying it, "
             f"and a sentence true only of the pin stays SILENT. The pin is "
             f"deliberate and is NOT a defect to repair here: rung V1 needs a "
             f"frozen scoring reference so the case scores recompute "
             f"identically, and a clone that SCORES is not a clone that RANKS "
             f"-- the same file was serving both purposes and only one of them "
             f"wants a freeze. This item is the disclosure; the repair, if a "
             f"rank claim ever needs the live board, is to fetch the live "
             f"board and say so. Every part of it is generated from the pin "
             f"rather than typed, so it cannot outlive the pin it describes. "
             f"GREEN HERE IS NOT COVERAGE: it means no "
             f"placement in the patterns disagrees with the board")
    # A SKIP IS NOT AN AGREEMENT, and an empty sweep is not a clean one. Both
    # of these used to be capable of returning PASS: a defect that raised on
    # every surface produced "all 0 placement expression(s) agree with the
    # published board", and one that raised on exactly the document carrying a
    # fault produced the same green with the count buried in the frame. The
    # surfaces a guard cannot read are the unusual ones, which is to say the
    # interesting ones, so their absence has to move the status and not only a
    # number a reader may not reach.
    #
    # AND THE NOTES ARE APPENDED TO EVERY BRANCH, not only to the branch that
    # runs when nothing else was found -- which was itself a defect of exactly
    # this class, caught by executing it. The first repair gave "empty sweep"
    # its own terminal branch, and a single unrelated rule-B WARN elsewhere in
    # the corpus reached its branch first: a totally blind rule-A sweep was
    # reported as "every travelling surface agrees with the board". A condition
    # that only speaks when nothing else does is a condition that does not
    # speak. Pinned by `test_an_empty_sweep_is_not_agreement_either`, which
    # runs against the real corpus and so has a live rule-B WARN in it.
    notes = []
    if skipped:
        notes.append(f"{len(skipped)} surface(s) RAISED and were not swept -- "
                     f"a surface this check could not read is not a surface "
                     f"that agrees")
    if not surveyed:
        notes.append(f"and NO rule-A placement expression was found at all "
                     f"across {naming} surface(s) naming an entrant: an empty "
                     f"sweep is not agreement")
    tail = "".join(f"; {n}" for n in notes)
    extra = skipped + ([f"empty sweep: 0 rule-A placement expressions across "
                        f"{naming} surface(s) naming an entrant -- NOT counted "
                        f"as agreement"] if not surveyed else [])
    if shipped:
        return Result(title, FAIL,
                      f"{len(shipped)} placement(s) on surfaces that TRAVEL "
                      f"disagree with the published board or name no one "
                      f"({len(internal)} more on lab records){tail}",
                      shipped + internal + extra + [frame])
    if internal:
        return Result(title, WARN,
                      f"every travelling surface agrees with the board; "
                      f"{len(internal)} lab record placement(s) do not{tail}",
                      internal + extra + [frame])
    if notes:
        return Result(title, WARN,
                      f"no placement in the patterns disagrees with the board, "
                      f"but this is NOT a PASS{tail}",
                      extra + [frame])
    return Result(title, PASS,
                  f"all {surveyed} placement expression(s) agree with the "
                  f"published board, and no comparison takes a placement word "
                  f"for an opponent", [frame])


def check_memory_scaling_law() -> Result:
    """Refit the published adjoint memory law from its own three measurements."""
    doc = WEB / "dafoam" / "ADJOINT_MEMORY_ENVELOPE.md"
    if not doc.exists():
        return Result("adjoint memory law", WARN, "memory envelope record absent")
    text = doc.read_text(encoding="utf-8", errors="replace")
    claim = re.search(
        r"memory \(MiB\) = ([0-9.]+) x cells\^([0-9.]+)\*\*, R.? = ([0-9.]+)", text)
    rows = re.findall(r"^\| ([0-9,]{4,}) \| ([0-9,]+\.[0-9]+) \|$", text, re.M)
    points = []
    for cells, mib in rows:
        try:
            points.append((float(cells.replace(",", "")),
                           float(mib.replace(",", ""))))
        except ValueError:
            continue
    points = sorted(set(points))
    if not claim or len(points) < 3:
        return Result("adjoint memory law", WARN,
                      "could not locate the published law or its measurements")
    coef_pub, expo_pub, r2_pub = (float(claim.group(1)), float(claim.group(2)),
                                  float(claim.group(3)))
    xs = [math.log(c) for c, _ in points]
    ys = [math.log(m) for _, m in points]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / \
        sum((x - mx) ** 2 for x in xs)
    coef = math.exp(my - slope * mx)
    ss_res = sum((y - (math.log(coef) + slope * x)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")

    problems = []
    if abs(slope - expo_pub) > 5e-4:
        problems.append(f"exponent: published {expo_pub}, refit {slope:.4f}")
    if abs(coef - coef_pub) / coef_pub > 5e-3:
        problems.append(f"coefficient: published {coef_pub}, refit {coef:.4f}")
    if abs(r2 - r2_pub) > 5e-4:
        problems.append(f"R2: published {r2_pub}, refit {r2:.4f}")
    detail = [f"refit from {n} measurements: "
              f"memory (MiB) = {coef:.4f} x cells^{slope:.4f}, R2 = {r2:.4f}"]
    if problems:
        return Result("adjoint memory law", FAIL,
                      "published memory law does not refit", problems + detail)
    return Result("adjoint memory law", PASS,
                  "published memory law reproduces from its own data", detail)


def check_withdrawn_numbers() -> Result:
    """A withdrawn number must not survive on a promotional surface.

    Each sentinel names a value the record explicitly withdrew, and the
    surfaces it must not appear on. Sentinels are added when a withdrawal is
    recorded, so the next audit enforces it automatically.
    """
    sentinels = [
        # (value as written, why withdrawn, surfaces it must not appear on)
        ("0.2510", "A4's DAFoam Ahmed primal, withdrawn",
         [WALL, WEB / "benchmarks.json"]),
        ("10.04%", "A4's adjoint-vs-FD gradient grade, not a drag number",
         [WALL, WEB / "benchmarks.json"]),
    ]
    problems, checked, unread = [], [], []
    for value, reason, surfaces in sentinels:
        for surface in surfaces:
            if not surface.exists():
                # A sentinel skipped is a sentinel NOT enforced, and until
                # 2026-08-15 the skip was silent and the check still PASSed.
                unread.append(f"{value} on {_rel(surface)}")
                continue
            text = surface.read_text(encoding="utf-8", errors="replace")
            checked.append(f"{value} not on {surface.name}")
            if value in text:
                problems.append(
                    f"{value} ({reason}) appears on {surface.name}")
    if unread and not problems:
        return _no_evidence(
            "withdrawn numbers",
            f"{len(unread)} of {len(unread) + len(checked)} sentinel(s) could "
            f"not be enforced; their surface is not on disk", unread,
            [f"{len(checked)} sentinel(s) that COULD be read are clear"])
    if problems:
        return Result("withdrawn numbers", FAIL,
                      f"{len(problems)} withdrawn value(s) still published",
                      problems)
    return Result("withdrawn numbers", PASS,
                  f"{len(checked)} withdrawn-value sentinel(s) clear")


def check_evidence_paths_exist() -> Result:
    """Repo-rooted evidence paths cited by the records must exist on disk.

    Only paths anchored at a known repository root are checked. A bare
    filename in a record usually names a file inside a case directory and
    cannot be resolved from the citation alone, so checking it would produce
    noise rather than findings.
    """
    roots = ("demo-output/", "sdk/", "scripts/", "models/", "mission-output/",
             "docs/", "dist/")
    pattern = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.[A-Za-z0-9]{1,6})`")
    # A record that documents a past citation defect necessarily quotes the
    # broken path. Quoting a withdrawn path is the opposite of citing it, so
    # lines that narrate a correction are not findings.
    retracted = re.compile(
        r"previously pointed at|never existed|did not exist|neither path|"
        r"path corrected|citation correction|withdrawn|do not cite", re.I)
    missing, total, scanned = [], 0, 0
    for doc in sorted(WEB.rglob("*.md")):
        if any(part in {"work", "processor0"} for part in doc.parts):
            continue
        scanned += 1
        lines = doc.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines):
            context = " ".join(lines[max(0, number - 2):number + 3])
            for cited in sorted(set(pattern.findall(line))):
                if not cited.startswith(roots):
                    continue
                total += 1
                if (REPO / cited).exists():
                    continue
                if retracted.search(context):
                    continue
                missing.append(
                    f"{doc.relative_to(REPO)}:{number + 1} cites {cited}")
    if not scanned:
        return _no_evidence(
            "cited evidence paths",
            "no record was found to read citations out of",
            [f"{_rel(WEB)}/**/*.md"])
    if missing:
        return Result("cited evidence paths", FAIL,
                      f"{len(missing)} of {total} repo-rooted citations do "
                      f"not resolve", missing[:25])
    if not total:
        return _no_selection(
            "cited evidence paths",
            f"{scanned} record(s) were read and not one repo-rooted citation "
            f"was found in any of them",
            [f"{_rel(WEB)}/**/*.md"],
            f"a backticked path anchored at one of {', '.join(roots)}",
            ["'all 0 citations resolve' is a sentence about citations produced "
             "without finding one; the records are there, so the question is "
             "whether the anchoring roots still describe how this tree names "
             "its paths"])
    return Result("cited evidence paths", PASS,
                  f"all {total} repo-rooted citations across {scanned} "
                  f"records resolve")


def check_f2_reproduction() -> Result:
    """F2's published coefficients must match its own raw force file."""
    record = WEB / "campaign" / "F2_runs" / "F2_reproduction_2026-07-30.json"
    raw = (WEB / "campaign" / "F2_runs" / "primary_M0.8_a1.25_Re6e6" /
           "postProcessing" / "forceCoeffs1" / "0" / "coefficient.dat")
    if not record.exists() or not raw.exists():
        return Result("F2 reproduction", WARN,
                      "F2 reproduction record or its raw force file is absent")
    published = _load_json(record).get("primary_M0.8_a1.25_Re6e6", {})
    iteration = int(published.get("iterations", 2000))
    wanted = None
    for line in raw.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#"):
            continue
        parts = line.split()
        if parts and parts[0] == str(iteration):
            wanted = parts
            break
    if not wanted:
        return Result("F2 reproduction", FAIL,
                      f"iteration {iteration} not present in the raw force file")
    cd_raw, cl_raw = float(wanted[1]), float(wanted[4])
    problems = []
    for label, published_value, raw_value in (
            ("cd", published.get("cd"), cd_raw),
            ("cl", published.get("cl"), cl_raw)):
        if published_value is None or abs(float(published_value) - raw_value) > 1e-9:
            problems.append(
                f"{label}: record says {published_value}, raw file says {raw_value}")
    if problems:
        return Result("F2 reproduction", FAIL,
                      "published F2 coefficients do not match raw data", problems)
    return Result("F2 reproduction", PASS,
                  f"F2 Cd and Cl match the raw force file at iteration {iteration}",
                  [f"Cd {cd_raw}, Cl {cl_raw}"])


def check_cost_predictions() -> Result:
    """Measured-versus-predicted cost pairs, and the auto-approve bar.

    A solver family's forecasts become auto-approvable once three consecutive
    predictions land within 20%. This check reports where each family stands.
    Pairs are recorded here as they are found in the records; each carries the
    citation for both halves so the table is auditable.

    TWO THINGS THE BAR DOES NOT TEST, measured 2026-08-01 against the ledger
    (`demo-output/website/mega-batch/COST_SCALING.md`) and now stated on the
    report itself, so nobody reads a streak as more than it is.

    1. **A streak measures the spread of the family, not the skill of the
       forecast.** On a family whose cost barely varies, predicting its own
       median clears the bar. `vspaero-wing` clears it 6,457 times in a row
       with a fitted law of R2 0.0002 that is 45 times worse than that median.
       A streak is necessary and it is not sufficient.
    2. **A family that mixes rank counts is not one cost population.** The
       third pair below is an 8-rank run sitting beside two serial ones, and a
       streak counted across the mixture counts two different quantities.
    """
    lines = []
    # THE DOCKET'S OWN PAIRS, read from disk. Until 2026-08-02 this check read
    # nothing at all: its whole evidence was the three tuples below, typed into
    # this file, so it could not fail on a wrong pair and it could not see that
    # completed items were recording their own measured cost in prose nothing
    # parsed. `scripts/cost_calibration.py` reads `measured_core_min` off every
    # completed proposal, each carrying a `measured_basis` that quotes the
    # sentence in that item's outcome the figure came from.
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        import cost_calibration  # noqa: PLC0415
        state = cost_calibration.analyse()
    except Exception as exc:  # noqa: BLE001 - a broken reader is a finding
        state = {"n": 0, "error": f"{type(exc).__name__}: {exc}"}
    if state.get("error"):
        lines.append(f"could not read the docket pairs: {state['error']}")
    elif state["n"]:
        whole = state["all"]
        lines.append(
            f"DOCKET PAIRS: {state['n']} completed item(s) record both an "
            f"estimate and a measured cost; {state['est_total']:g} core-min "
            f"estimated against {state['measured_total']:g} measured, "
            f"aggregate ratio {state['aggregate_ratio']}")
        lines.append(
            f"the 3x planning multiplier brackets {whole['inside_the_3x_band']}"
            f" of {whole['n']}; {whole['within_20_percent']} land within 20 "
            f"percent; {whole['needed_no_solver_at_all']} spent EXACTLY ZERO "
            f"because the work needed no solver, which no multiplier fixes")
        for label, key in (("basis begins 'measured'",
                            "basis_names_a_measurement"),
                           ("basis is a forecast", "basis_is_a_forecast")):
            cut = state.get(key)
            if cut:
                lines.append(
                    f"{label}: {cut['n']} pair(s), worst over-run "
                    f"{cut['worst_overrun']}x, median {cut['median_ratio']}, "
                    f"{cut['inside_the_3x_band']} inside the 3x band")
        lines.append(
            "over-runs on record: " + ", ".join(
                f"{r['ratio']}x {r['id']} ({r['basis_kind']})"
                for r in state["overruns"]) or "none")
        lines.append(
            f"{len(state['gaps'])} completed item(s) with an estimate record "
            f"no readable measured cost, each naming why "
            f"(scripts/cost_calibration.py)")

    # (family, rung, predicted seconds, measured seconds, evidence)
    # STILL TRANSCRIBED, and labelled. These three are per-solver-family
    # forecasts in seconds rather than per-item core-minutes, so they are not
    # on the docket in the shape above; they stay here until the F5a ladder
    # records them where something can read them.
    pairs = [
        ("pimpleFoam unsteady cylinder", "Re 2000", 3715.0, 3965.11,
         "F5a ladder, cost model D13"),
        ("pimpleFoam unsteady cylinder", "Re 3900", 6390.0, 10899.4,
         "F5a ladder, cost model outcome"),
        ("pimpleFoam unsteady cylinder", "Re 1000 3D pilot, 8 ranks",
         64800.0, 44102.0, "F5a ladder, 8-rank optimistic row 18 h"),
    ]
    families: dict[str, list] = {}
    lines.append("TRANSCRIBED, per-solver-family, still typed into this file:")
    for family, rung, predicted, measured, source in pairs:
        error = 100.0 * (measured - predicted) / predicted
        within = abs(error) <= 20.0
        families.setdefault(family, []).append(within)
        lines.append(
            f"{family} | {rung} | predicted {predicted:.0f} s | measured "
            f"{measured:.0f} s | {error:+.1f}% | "
            f"{'within 20%' if within else 'MISS'} | {source}")
    qualified = []
    for family, outcomes in families.items():
        streak = 0
        for hit in outcomes:
            streak = streak + 1 if hit else 0
        lines.append(f"{family}: longest run of consecutive hits = {streak} of 3 needed")
        if streak >= 3:
            qualified.append(family)
    if qualified:
        lines.append(f"AUTO-APPROVABLE: {', '.join(qualified)}")
    else:
        lines.append("AUTO-APPROVABLE: none; no family has three consecutive "
                     "predictions within 20%")
    lines.append(
        "the bar is necessary and not sufficient: on the ledger, vspaero-wing "
        "clears three-in-a-row 6457 times with a law of R2 0.0002 that is 45x "
        "worse than predicting its own median, and the 8-rank pair above sits "
        "in a family with two serial ones (demo-output/website/mega-batch/"
        "COST_SCALING.md)")
    docket_pairs = state.get("n", 0)
    return Result("cost predictions vs measured", INFO,
                  f"{docket_pairs} measured-versus-estimated pair(s) read off "
                  f"the docket, plus {len(pairs)} transcribed into this file "
                  f"across {len(families)} solver family", lines)


def check_ungated_completed_runs() -> Result:
    """A completed run whose gate was never resolved is an unfinished gate."""
    findings = []
    ladder = WEB / "campaign" / "F5a_cylinder_reynolds_ladder.md"
    if not ladder.exists():
        # The `if ladder.exists()` this replaces skipped in silence and fell
        # through to "no completed run is missing its gate verdict", which is
        # a sentence about runs and was produced by reading no runs.
        return _no_evidence(
            "completed but ungated runs",
            "the only ladder record this check reads is not on disk",
            [ladder])
    text = ladder.read_text(encoding="utf-8", errors="replace")
    # THIS CHECK HAD NO DENOMINATOR. It looked for one literal and, finding it
    # absent, said "no completed run is missing its gate verdict" -- a sentence
    # about runs, from a function that never identified a run. Executed
    # 2026-08-15 against a real ladder record naming no run at all, it returned
    # that sentence as a PASS. The population is now counted: a row of the
    # measured table whose status cell says the rung completed. The check still
    # reports on the marker, but it can no longer report on a population it did
    # not find.
    completed = [line for line in text.splitlines()
                 if line.startswith("|") and re.search(r"\bcomplete\b", line)]
    if "PRELIMINARY, not yet graded" in text:
        findings.append(
            "F5a Re 1000 3D pilot: run completed to its full end time "
            "(44,102 s wall on 8 ranks, about 98 core-hours, the most "
            "expensive single solve in the lab) but its statistics are "
            "recorded as preliminary and not yet graded against the "
            "pre-stated expectation")
    if findings:
        return Result("completed but ungated runs", WARN,
                      f"{len(findings)} completed run(s) carry no gate verdict",
                      findings)
    if not completed:
        return _no_selection(
            "completed but ungated runs",
            "the ladder record was read and names no completed run, so no "
            "run's gate verdict was looked for",
            [ladder],
            "a table row whose status cell says the rung is complete",
            ["the record is on disk; with no completed run identified the PASS "
             "sentence was about a population this check had not found, which "
             "is the shape it exists to catch one level up"])
    return Result("completed but ungated runs", PASS,
                  f"none of {len(completed)} completed run(s) on this record "
                  f"is missing its gate verdict")


# --------------------------------------------------------------------------
# Round 2 checks, added 2026-07-31 under well W7.
#
# Each one is here because the defect it looks for was found once, by hand, by
# somebody who was looking at something else. The tuning rule for all of them
# is the asymmetry the certificate fix was tuned on: a false positive costs a
# reading, a false negative costs a published number nobody rechecks. So they
# are noisy on purpose, they name what they found and why, and none of them
# edits anything.
# --------------------------------------------------------------------------

MISSION = REPO / "mission-output"
CAMPAIGN = WEB / "campaign"
GATE_TABLE = CAMPAIGN / "NINE_ACT_GATE_TABLE.md"
ACTIVE = WEB / "ACTIVE_RESEARCH.md"
REGISTER = CAMPAIGN / "NOT_PASSING_REGISTER.md"
RESULTS = REPO / "models" / "curriculum" / "results"


def _md_rows(path: Path) -> list[list[str]]:
    """Cells of every pipe-delimited markdown row in a file, separators out."""
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= {"-", ":"} and c for c in cells):
            continue
        rows.append(cells)
    return rows


def check_gate_table_vs_transcripts() -> Result:
    """The published gate table must re-derive from the act transcripts.

    `gate_table.py` is the generator and the act transcript is its source of
    truth. If the published table and a fresh generation disagree, one of three
    things is true and all three are findings: the table was hand-edited, an
    act changed its output and the row is now unsupported, or the generator
    can no longer read an act it cites. This check does not say which. It says
    they disagree, and where.
    """
    if not GATE_TABLE.exists():
        return Result("gate table vs transcripts", FAIL,
                      "the published nine-act gate table is missing")
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        import gate_table  # noqa: PLC0415 - imported here so a broken
        generated = gate_table.rows()  # generator is a finding, not a crash
    except Exception as exc:  # noqa: BLE001
        return Result("gate table vs transcripts", FAIL,
                      f"the generator could not run: {type(exc).__name__}: {exc}")

    published = {}
    for cells in _md_rows(GATE_TABLE):
        if len(cells) >= 7 and cells[0] not in ("act",):
            published[cells[0]] = cells

    problems, pending = [], []
    for row in generated:
        case = row["case"]
        if case not in published:
            problems.append(f"{case}: generated but not published")
            continue
        pub = published[case]
        fields = (("reference", pub[2]), ("measured", pub[3]),
                  ("deviation", pub[4]), ("verdict", pub[5]))
        for key, published_value in fields:
            fresh = str(row[key])
            if fresh == PENDING_TOKEN and published_value != PENDING_TOKEN:
                pending.append(
                    f"{case}: published {key} is {published_value!r} but the "
                    f"generator now reads PENDING from "
                    f"{row['source']}; the cited artifact no longer supports "
                    f"the row as written")
                break
            if fresh != PENDING_TOKEN and fresh != published_value:
                problems.append(
                    f"{case}: {key} published {published_value!r}, "
                    f"re-derived {fresh!r} from {row['source']}")
    for case in published:
        if case not in {r["case"] for r in generated}:
            problems.append(f"{case}: published but the generator emits no such row")

    text = GATE_TABLE.read_text(encoding="utf-8", errors="replace")
    graded = sum(1 for r in generated
                 if str(r["verdict"]) != PENDING_TOKEN)
    claim = re.search(r"(\d+) of (\d+) acts have run; (\d+) carry a graded number",
                      text)
    if claim and int(claim.group(3)) != graded:
        problems.append(
            f"footer claims {claim.group(3)} graded rows; the generator "
            f"produces {graded}")

    if problems or pending:
        return Result("gate table vs transcripts", FAIL,
                      f"{len(problems) + len(pending)} row(s) do not re-derive "
                      f"from the artifact they cite", pending + problems)
    if not generated:
        return _no_selection(
            "gate table vs transcripts",
            f"the generator ran and emitted NO rows, so none of the "
            f"{len(published)} published row(s) was re-derived from anything",
            ["scripts/gate_table.py", _rel(GATE_TABLE)],
            "gate_table.rows()",
            ["the published table is on disk and the generator imported and "
             "ran; 'all 0 rows re-derive from their cited transcript' is a "
             "sentence about rows produced without generating one, and a "
             "generator that has stopped finding its acts looks exactly like "
             "a lab with no acts"])
    return Result("gate table vs transcripts", PASS,
                  f"all {len(generated)} rows re-derive from their cited "
                  f"transcript")


PENDING_TOKEN = "PENDING"


def check_wall_credentials_vs_results() -> Result:
    """Every credential on the wall must re-derive from its own result file.

    The join is positional and undocumented on the wall itself: a credential
    named `ahmed_25` is backed by `models/curriculum/results/ahmed_25.json`.
    That file is the primary evidence; `wall.json` is a build product of it.
    The wall is rebuilt by hand, so it can drift, and nothing else notices.
    """
    wall = _load_json(WALL)
    creds = wall.get("credentials") if isinstance(wall, dict) else None
    if not creds:
        return Result("wall credentials vs results", FAIL,
                      "wall.json carries no credentials array")
    sys.path.insert(0, str(REPO / "sdk"))
    try:
        from chief_engineer import lab  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        return Result("wall credentials vs results", WARN,
                      f"cannot import the re-derivation used by the wall "
                      f"builder: {type(exc).__name__}: {exc}")
    # The stored result file is the as-run archive. The wall displays what
    # `displayed_credential` makes of it today: the finest anchored rung, the
    # current grading rules. Comparing the wall against the raw tier would
    # flag every re-grade as a defect, so the comparison is against the same
    # re-derivation the builder performs. What this catches is drift: a wall
    # that would change if it were rebuilt right now.
    problems, checked = [], 0
    for cred in creds:
        name = cred.get("name")
        source = RESULTS / f"{name}.json"
        if not source.exists():
            problems.append(f"{name}: no result file at "
                            f"models/curriculum/results/{name}.json")
            continue
        raw = _load_json(source)
        checked += 1
        try:
            shown = lab.displayed_credential(raw)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{name}: re-derivation raised "
                            f"{type(exc).__name__}: {exc}")
            continue
        for wall_key, shown_key in (("tier", "tier"),
                                    ("measured", "on_reference_basis"),
                                    ("envelope", "envelope"),
                                    ("reason", "reason")):
            if wall_key not in cred or shown_key not in shown:
                continue
            if str(cred[wall_key]) != str(shown[shown_key]):
                problems.append(
                    f"{name}: wall {wall_key} is {cred[wall_key]!r}; a rebuild "
                    f"from models/curriculum/results/{name}.json would write "
                    f"{shown[shown_key]!r}")
        try:
            compared = float(raw.get("cd_compared"))
            reference = float(raw.get("reference_cd"))
            recomputed = abs(compared - reference) / abs(reference)
            stated = float(raw.get("relative_error"))
            if abs(recomputed - stated) > 5e-3:
                problems.append(
                    f"{name}: result file states relative_error {stated}, "
                    f"recomputed {recomputed:.4f} from its own cd_compared "
                    f"and reference_cd")
        except (TypeError, ValueError):
            problems.append(f"{name}: a compared value is not a number")
    if problems:
        return Result("wall credentials vs results", FAIL,
                      f"{len(problems)} credential field(s) do not re-derive",
                      problems)
    return Result("wall credentials vs results", PASS,
                  f"all {checked} credentials re-derive from their result file")


def check_benchmarks_vs_closure_record() -> Result:
    """`benchmarks.json` and its generator's hard-coded block must agree.

    This is the defect that would have overwritten a corrected card in
    silence. `sdk/scripts/build_benchmarks.py` holds the closure numbers as a
    module-level dict rather than reading them from the scored artifacts, so a
    hand-correction to `benchmarks.json` survives exactly until the next
    regeneration. The generator's own docstring says KEEP THIS IN SYNC. That
    instruction is a check waiting to be written, so here it is.
    """
    published = _load_json(WEB / "benchmarks.json")
    block = published.get("closure_challenge", {}) if isinstance(published, dict) else {}
    generator = REPO / "sdk" / "scripts" / "build_benchmarks.py"
    if not block:
        return Result("benchmarks vs closure record", FAIL,
                      "benchmarks.json carries no closure_challenge block")
    if not generator.exists():
        return Result("benchmarks vs closure record", WARN,
                      "the benchmarks generator is not on disk")
    problems = []
    try:
        tree = ast.parse(generator.read_text(encoding="utf-8"))
        constants = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                    isinstance(node.targets[0], ast.Name):
                try:
                    constants[node.targets[0].id] = ast.literal_eval(node.value)
                except Exception:  # noqa: BLE001
                    continue
        hard_coded = constants.get("_CLOSURE")
        if hard_coded is None:
            problems.append("_CLOSURE not found in the generator; the sync "
                            "rule this check enforces may have moved")
        else:
            for key in sorted(set(block) | set(hard_coded)):
                if block.get(key) != hard_coded.get(key):
                    problems.append(
                        f"{key}: published {block.get(key)!r}, the generator "
                        f"would write {hard_coded.get(key)!r}")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"could not read the generator: {type(exc).__name__}: {exc}")

    # And the published block against the scored artifacts themselves.
    entry = _load_json(WEB / "closure_challenge_trained_entry_round3_gated.json")
    harness = entry.get("official_test_harness_result", {}) if isinstance(entry, dict) else {}
    scored = harness.get("overall") or harness.get("overall_score")
    if scored is not None and block.get("our_score") is not None:
        if abs(float(scored) - float(block["our_score"])) > 1e-9:
            problems.append(
                f"our_score: benchmarks.json says {block['our_score']}, the "
                f"round-3 gated entry's own harness result is {scored}")
    if problems:
        return Result("benchmarks vs closure record", FAIL,
                      f"{len(problems)} closure field(s) disagree with the "
                      f"artifact or would regress on the next build", problems)
    return Result("benchmarks vs closure record", PASS,
                  "the published closure block matches the generator and the "
                  "scored entry of record")


_GRADE_WORDS = ("PASS", "CONDITIONAL", "FAIL")


def _fd_grade(percent: float, sign_flip: bool) -> str:
    """The current standard, verification charter section 7. One place."""
    if sign_flip or percent > 15.0:
        return "FAIL"
    if percent > 5.0:
        return "CONDITIONAL"
    return "PASS"


def check_fd_grades_current_standard() -> Result:
    """Every published FD grade is recomputed against the current standard.

    The retired band was "1 to 12 percent is normal". A row still graded
    against it reads as a pass and is not one. Charter clause: grades are
    recomputed every time a table is regenerated, and a row carrying a retired
    grade is a defect.
    """
    surfaces = [ACTIVE] if ACTIVE.exists() else []
    surfaces += sorted(WEB.rglob("*.md"))
    seen, problems, ungraded = set(), [], []
    graded = 0
    percent = re.compile(r"\*\*([\d.]+)%\*\*")
    for doc in surfaces:
        if doc in seen or any(p in {"work", "processor0"} for p in doc.parts):
            continue
        seen.add(doc)
        lines = doc.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines, 1):
            if not line.startswith("|") or "%" not in line:
                continue
            if "wrt" not in line and "derivative" not in line and "FD" not in line:
                continue
            found = percent.search(line)
            if not found:
                continue
            value = float(found.group(1))
            sign_flip = "sign flip" in line.lower()
            stated = [w for w in _GRADE_WORDS
                      if re.search(rf"\*\*{w}\*\*", line)]
            expected = _fd_grade(value, sign_flip)
            where = f"{doc.relative_to(REPO)}:{number}"
            if not stated:
                ungraded.append(f"{where}: {value}% carries no grade")
                continue
            graded += 1
            if stated[0] != expected:
                problems.append(
                    f"{where}: graded {stated[0]} at {value}%"
                    f"{' with a sign flip' if sign_flip else ''}; the current "
                    f"standard grades it {expected}. Row reads: {line.strip()}")
    if problems:
        return Result("FD grades vs current standard", FAIL,
                      f"{len(problems)} FD row(s) carry a grade the current "
                      f"standard does not give", problems + ungraded[:5])
    # Two ways to reach a clean verdict here and only one of them is a PASS:
    # every graded row agreed, or no graded row was found. Until 2026-08-15
    # the second printed the first's sentence, and an absent ACTIVE raised
    # instead of reporting.
    if not graded:
        return _no_evidence(
            "FD grades vs current standard",
            f"no graded FD row was found across {len(seen)} surface(s); no "
            f"grade was recomputed", [_rel(ACTIVE), f"{_rel(WEB)}/**/*.md"],
            [f"{len(ungraded)} row(s) carry a percentage and no grade word"]
            + ungraded[:5])
    return Result("FD grades vs current standard", PASS,
                  f"none of {graded} published FD grade(s) disagrees with the "
                  f"current standard", ungraded[:10])


def _looks_like_interval(text: str) -> bool:
    """Deliberately conservative, and the same shape the certificate uses.

    One signed number with an optional unit, anchored end to end. Anything
    with prose in it is not an interval. A false positive here would let a
    fabricated confidence interval past; a false negative only costs a real
    interval a flag.
    """
    return bool(re.fullmatch(
        r"\s*[+-]?\s*(?:±|\+/-|\+-)?\s*\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"
        r"\s*[A-Za-z%/°]{0,12}\s*", text or ""))


def check_statistical_labels() -> Result:
    """A statistical caption may only sit on a value a procedure produced.

    Two surfaces. The code that prints the caption, wherever a copy of it
    lives, must gate it on an interval test; an ungated copy in a bundle or a
    snapshot will seal fabricated intervals exactly as the tracked copy used
    to. And any transcript line carrying the caption must carry an interval
    next to it.
    """
    problems, checked = [], 0
    sites = transcripts = 0
    caption = "95% confidence interval"
    for source in sorted(REPO.rglob("certificate.py")):
        if "__pycache__" in source.parts:
            continue
        text = source.read_text(encoding="utf-8", errors="replace")
        if caption not in text:
            continue
        checked += 1
        sites += 1
        if "_looks_like_interval" not in text:
            problems.append(
                f"{source.relative_to(REPO)} prints {caption!r} with no "
                f"interval test in the file; every envelope it is handed "
                f"becomes a statistical claim")
    for transcript in sorted(MISSION.glob("*/transcript.*")):
        checked += 1
        transcripts += 1
        for number, line in enumerate(
                transcript.read_text(encoding="utf-8",
                                     errors="replace").splitlines(), 1):
            low = line.lower()
            if "confidence interval" not in low:
                continue
            if any(word in low for word in
                   ("no 95", "not a confidence", "no confidence",
                    "point estimate", "declin", "is not an interval")):
                continue
            if "±" in line or "+-" in line or "+/-" in line:
                continue
            problems.append(
                f"{transcript.relative_to(REPO)}:{number} says confidence "
                f"interval with no interval on the line: {line.strip()[:120]}")
    if problems:
        return Result("statistical labels", FAIL,
                      f"{len(problems)} statistical label(s) sit on something "
                      f"that is not an interval", problems)
    # This check has two halves and either can be empty independently. The
    # transcript half reads `mission-output/`, which is GITIGNORED
    # (.gitignore:13) and absent on a fresh clone -- so on a clone this
    # returned PASS on a sentence naming transcripts, having opened none.
    if not sites or not transcripts:
        off = ([f"{_rel(REPO)}/**/certificate.py carrying {caption!r}"]
               if not sites else [])
        off += [f"{_rel(MISSION)}/*/transcript.*"] if not transcripts else []
        return _no_evidence(
            "statistical labels",
            f"{'both halves' if not sites and not transcripts else 'one half'}"
            f" of this check read nothing: {sites} caption site(s) and "
            f"{transcripts} transcript(s)", off,
            ["mission-output/ is gitignored (.gitignore:13) and is absent on "
             "a fresh clone and in the laptop bundle"])
    return Result("statistical labels", PASS,
                  f"{checked} caption site(s) and transcripts carry no "
                  f"unearned confidence interval ({sites} caption site(s), "
                  f"{transcripts} transcript(s))")


# Where the source-shape checks look. THE DEFECT THIS LIST GREW FOR: it held
# only the two package directories, so every runner under `sdk/scripts/` and
# every tool under `scripts/` -- including this file -- was outside the reach
# of checks written to find defects that live in exactly that kind of code.
# Measured when the list was widened, 2026-08-02:
# `sdk/scripts/run_uq_studies.py:b52_fourth_rung()` fits a refinement ladder,
# reads `band_abs` off it and never reads `conclusive`, on the one ladder in
# this corpus whose band IS the non-monotone fallback. That is the precise
# defect `check_nonconclusive_band_readers` exists for, in the file that
# WRITES the studies, and the check had never opened it.
_PY_ROOTS = ("sdk/workflows", "sdk/chief_engineer", "sdk/scripts", "scripts")


def _py_sources() -> list[Path]:
    out: list[Path] = []
    for root in _PY_ROOTS:
        base = REPO / root
        if base.exists():
            out += [p for p in sorted(base.rglob("*.py"))
                    if "__pycache__" not in p.parts]
    return out


def _py_corpus(name: str) -> tuple[list[Path], Result | None]:
    """The source corpus, and the UNKNOWN to return if it came back empty.

    `_py_sources` skips a root that is not on disk, so a renamed or unmounted
    root shrinks the corpus silently and every source-shape check below then
    reports agreement over nothing. Five checks share this corpus and all five
    used to say "all 0 ... " and PASS.
    """
    sources = _py_sources()
    if sources:
        return sources, None
    return sources, _no_evidence(
        name, "no Python source was found to scan",
        [f"{root}/**/*.py" for root in _PY_ROOTS],
        ["every root this check reads is missing or empty, so the sweep "
         "examined no code at all"])


def _stored_studies(name: str) -> tuple[list[Path], Result | None]:
    """The stored UQ studies, and the UNKNOWN to return if there are none.

    Six checks read this one directory. An empty glob used to read as "all 0
    stored study(s) in scope" and PASS in every one of them.
    """
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
    if studies:
        return studies, None
    return studies, _no_evidence(
        name, "no stored study was found to read",
        ["models/curriculum/uq-studies/*.json"])


def _no_study_in_scope(name: str, studies, selector: str, note: str) -> Result:
    """EMPTY SELECTION over the study corpus, which is not an empty corpus.

    `_stored_studies` above guards the directory being empty. It cannot guard
    the case that matters more often: the directory holds studies and this
    check's own scope rule puts every one of them out of scope. All six sharers
    then said "all 0 ... " and PASSed, and the six sentences were about studies
    while the number in each of them was produced by grading none.
    """
    return _no_selection(
        name,
        f"{len(studies)} stored study(s) were read and NONE is in scope for "
        f"this check, so no study was graded",
        ["models/curriculum/uq-studies/*.json"], selector,
        [note,
         "the study corpus is present and non-empty -- this is not the "
         "empty-directory case _stored_studies already guards; what matched "
         "nothing is this check's own SCOPE RULE, so a writer that renamed the "
         "field it selects on empties the check without emptying the directory"])


def check_nonconclusive_band_readers() -> Result:
    """A caller reading `band_abs` must also read `conclusive`.

    `eca_hoekstra_band` returns a conservative fallback band even when it sets
    `conclusive` False. Five independent authors read the number and printed
    it. That is a fact about the return shape, so the check is on the shape:
    a function that calls the ladder fit, reads `band_abs` off it, and never
    mentions `conclusive` or `reportable_band` is the same defect again.

    Scoped to callers of the fit rather than to every reader of a key named
    `band_abs`, because other producers use the same key for bands that carry
    no conclusiveness flag at all, and flagging those would be noise with no
    defect behind it. `uq.py` itself is exempt: it owns the return shape.
    """
    problems, checked = [], 0
    sources, blind = _py_corpus("non-conclusive band readers")
    if blind:
        return blind
    for source in sources:
        if source.name == "uq.py":
            continue
        text = source.read_text(encoding="utf-8", errors="replace")
        if "band_abs" not in text or "eca_hoekstra_band" not in text:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            problems.append(f"{source.relative_to(REPO)} does not parse: {exc}")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            body = ast.get_source_segment(text, node) or ""
            if "band_abs" not in body or "eca_hoekstra_band(" not in body:
                continue
            checked += 1
            if "conclusive" in body or "reportable_band" in body:
                continue
            problems.append(
                f"{source.relative_to(REPO)}:{node.lineno} {node.name}() fits "
                f"a refinement ladder, reads band_abs off it and never reads "
                f"conclusive; on a failed ladder that number is a fallback, "
                f"not a measured uncertainty")
    if problems:
        return Result("non-conclusive band readers", FAIL,
                      f"{len(problems)} reader(s) trust a band without its flag",
                      problems)
    if not checked:
        return _no_selection(
            "non-conclusive band readers",
            f"{len(sources)} Python source(s) were read and not one function "
            f"in them fits a ladder and reads band_abs off it",
            [f"{root}/**/*.py" for root in _PY_ROOTS],
            "a function whose body holds both 'band_abs' and "
            "'eca_hoekstra_band('",
            ["the corpus is present; 'all 0 band_abs readers also read the "
             "flag' is a sentence about readers produced without finding one, "
             "and the call spelling this selects on is the thing to check "
             "before believing there are none"])
    return Result("non-conclusive band readers", PASS,
                  f"all {checked} band_abs readers also read the flag")


# The channel a `combine_expanded` keyword contributes, and the keyword the
# display record uses for the same channel. Two names for one thing is exactly
# how a term ends up in a total that the table beside it does not show.
_COMBINE_TO_CHANNEL = {"input_2sigma": "input", "numerical_abs": "numerical",
                       "model_abs": "model"}
_DISPLAY_KEYWORD = {"input": "input_2sigma", "numerical": "numerical",
                    "model": "model"}
# The shared channel builder, and the module that owns it. An act calling it
# displays whatever that builder declares, so the declaration is read from
# there rather than treated as unknown.
_SHARED_BUILDER = ("certificate_channels", "sdk/workflows/geometry_study.py")


def _declared_channels(text: str) -> dict[str, bool] | None:
    """Which channels an `uncertainty_channels` call in this source shows as
    quantified. None when the source makes no such call."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    shown: dict[str, bool] = {}
    seen = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if getattr(node.func, "id", getattr(node.func, "attr", "")) != \
                "uncertainty_channels":
            continue
        seen = True
        for keyword in node.keywords:
            for channel, display in _DISPLAY_KEYWORD.items():
                if keyword.arg != display:
                    continue
                quantified = not (isinstance(keyword.value, ast.Constant)
                                  and keyword.value.value is None)
                # Any call that quantifies the channel counts: an act with
                # two call sites shows the channel if either one carries a
                # figure.
                shown[channel] = shown.get(channel, False) or quantified
    return shown if seen else None


def check_channel_totals_use_one_rule() -> Result:
    """A reported total is the one combination rule, over the channels shown.

    Two halves, and the doctrine states both.

    (a) An act that quantifies two or more V&V-20 channels reports a total,
        and computes it through `combine_expanded` rather than inventing its
        own arithmetic. Eleven acts route through that call today; the check
        is here so the twelfth does too.

    (b) A term may not be in the total that the channel table reports
        unquantified. That is `combine_expanded`'s own contract, in its own
        docstring: the combined band is never presented without the channel
        table one level down. A total wider than the channels displayed is a
        difference the viewer has no way to account for, and unquantified
        means nobody measured it, not zero.

    This is a consistency check between two surfaces of the same act, not a
    re-derivation from primary evidence, and it is named that way.
    """
    problems, checked = [], 0
    shared_text = (REPO / _SHARED_BUILDER[1]).read_text(
        encoding="utf-8", errors="replace") \
        if (REPO / _SHARED_BUILDER[1]).exists() else ""
    shared_declared = _declared_channels(shared_text) or {}
    sources, blind = _py_corpus("channel totals vs the one rule")
    if blind:
        return blind
    for source in sources:
        if source.name == "uq.py" or "workflows" not in source.parts:
            continue
        text = source.read_text(encoding="utf-8", errors="replace")
        if "uncertainty_channels(" not in text and \
                f"{_SHARED_BUILDER[0]}(" not in text:
            continue
        declared = _declared_channels(text)
        if declared is None:
            # The act uses the shared builder, so it displays what the
            # builder declares.
            if f"{_SHARED_BUILDER[0]}(" not in text:
                continue
            declared = dict(shared_declared)
        checked += 1
        rel = source.relative_to(REPO)
        quantified = sorted(k for k, v in declared.items() if v)
        combines = "combine_expanded" in text
        if len(quantified) >= 2 and not combines:
            problems.append(
                f"{rel} quantifies {len(quantified)} channels "
                f"({', '.join(quantified)}) and reports no combined band "
                f"through the one rule")
        if not combines:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if getattr(node.func, "id",
                       getattr(node.func, "attr", "")) != "combine_expanded":
                continue
            for keyword in node.keywords:
                channel = _COMBINE_TO_CHANNEL.get(keyword.arg or "")
                if channel is None:
                    continue
                contributes = not (isinstance(keyword.value, ast.Constant)
                                   and keyword.value.value is None)
                if contributes and not declared.get(channel, False):
                    problems.append(
                        f"{rel}:{node.lineno} puts the {channel} channel in "
                        f"the total while the act's own channel table reports "
                        f"it unquantified; the total is wider than the "
                        f"breakdown it is shown beside")
    if problems:
        return Result("channel totals vs the one rule", FAIL,
                      f"{len(problems)} total(s) do not match the channels "
                      f"they are shown with", problems)
    if not checked:
        return _no_selection(
            "channel totals vs the one rule",
            f"{len(sources)} Python source(s) were read and not one act under "
            f"sdk/workflows declares a channel table",
            [f"{root}/**/*.py" for root in _PY_ROOTS],
            f"a file under sdk/workflows calling uncertainty_channels( or "
            f"{_SHARED_BUILDER[0]}( AND declaring channels",
            ["the corpus is present; what selected nothing is the pair of call "
             "spellings plus the 'workflows' path segment, so an act that "
             "renamed either leaves this check reporting one rule over no acts"])
    return Result("channel totals vs the one rule", PASS,
                  f"all {checked} channel-reporting act(s) combine through "
                  f"the one rule over the channels they display")


def check_declared_fleet_vs_work() -> Result:
    """A fleet declared on a restored path is a fleet the run never used.

    The hump act called `set_workers(ranks)` inside its warm-solve branch,
    where the mesh and the solve are both restored from cache and nothing is
    dispatched. The declaration reaches the worker numeral and the spend line,
    so it is a claim about the run. This finds the shape: a non-zero worker
    declaration inside a branch whose condition is a cache restore.
    """
    problems, branches = [], 0
    sources, blind = _py_corpus("declared fleet vs work")
    if blind:
        return blind
    for source in sources:
        text = source.read_text(encoding="utf-8", errors="replace")
        if "set_workers" not in text:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            test = (ast.get_source_segment(text, node.test) or "").lower()
            if not any(word in test for word in ("warm", "cached", "restore")):
                continue
            branches += 1
            # Body only. The `else` of a warm-path branch is the cold path,
            # where the fleet is real and the declaration is correct.
            inner_nodes = [n for stmt in node.body for n in ast.walk(stmt)]
            for inner in inner_nodes:
                if not isinstance(inner, ast.Call):
                    continue
                func = inner.func
                if not (isinstance(func, ast.Attribute)
                        and func.attr == "set_workers"):
                    continue
                if not inner.args:
                    continue
                first = inner.args[0]
                if isinstance(first, ast.Constant) and first.value == 0:
                    continue
                problems.append(
                    f"{source.relative_to(REPO)}:{inner.lineno} declares "
                    f"workers inside a restored-path branch "
                    f"({test.strip()[:60]}); the run dispatches nothing there")
    if problems:
        return Result("declared fleet vs work", FAIL,
                      f"{len(problems)} worker declaration(s) on a path that "
                      f"runs no parallel work", problems)
    if not branches:
        return _no_selection(
            "declared fleet vs work",
            f"{len(sources)} Python source(s) were read and not one holds a "
            f"branch whose condition is a cache restore",
            [f"{root}/**/*.py" for root in _PY_ROOTS],
            "an `if` whose test text contains 'warm', 'cached' or 'restore', "
            "in a file mentioning set_workers",
            ["'no worker declaration on any of 0 restored-path branches' names "
             "its own zero and still reads as a clean verdict; the corpus is "
             "there, so the three condition words are what to re-read"])
    return Result("declared fleet vs work", PASS,
                  f"no worker declaration on any of {branches} restored-path "
                  f"branches")


# Governed thresholds and the parameter names that must not restate them as
# literals. The monitor held its own 20.0 for five days after the approved
# constant moved to 10.0, and every caller taking the default judged on a
# threshold nobody approved.
GOVERNED_THRESHOLDS = {
    "flag_multiple": ("sdk/chief_engineer/log_signatures.py", "FLAG_MULTIPLE"),
    "fatal_multiple": ("sdk/chief_engineer/log_signatures.py", "FATAL_MULTIPLE"),
}


def check_restated_thresholds() -> Result:
    """A governed threshold restated as a literal is a defect at review.

    Whether or not it currently agrees with its source. On the day it stops
    agreeing, nothing announces it.
    """
    problems, pinned, seen = [], 0, 0
    sources, blind = _py_corpus("restated thresholds")
    if blind:
        return blind
    for source in sources:
        text = source.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            args = node.args
            names = [a.arg for a in args.args + args.kwonlyargs]
            defaults = ([None] * (len(args.args) - len(args.defaults))
                        + list(args.defaults) + list(args.kw_defaults))
            for name, default in zip(names, defaults):
                if name not in GOVERNED_THRESHOLDS or default is None:
                    continue
                # The DENOMINATOR, and it is not `pinned`. `pinned` counts only
                # the compliant half, so a sweep that found no governed
                # parameter at all printed "0 threshold default(s) read the
                # governed constant" -- a zero that reads as compliance.
                seen += 1
                governed_file, governed_name = GOVERNED_THRESHOLDS[name]
                if isinstance(default, ast.Name):
                    pinned += 1
                    continue
                if isinstance(default, ast.Constant) and isinstance(
                        default.value, (int, float)):
                    problems.append(
                        f"{source.relative_to(REPO)}:{node.lineno} "
                        f"{node.name}() restates {name} as the literal "
                        f"{default.value}; the governed value is "
                        f"{governed_name} in {governed_file}")
    if problems:
        return Result("restated thresholds", FAIL,
                      f"{len(problems)} governed threshold(s) restated as a "
                      f"literal", problems)
    if not seen:
        return _no_selection(
            "restated thresholds",
            f"{len(sources)} Python source(s) were read and no function "
            f"parameter in any of them carries a governed name with a default",
            [f"{root}/**/*.py" for root in _PY_ROOTS],
            f"a parameter named one of {', '.join(sorted(GOVERNED_THRESHOLDS))}"
            f" carrying a default",
            ["the corpus is present; the GOVERNED_THRESHOLDS name list is what "
             "matched nothing, and a threshold renamed at its call sites "
             "leaves this check green over a corpus it no longer reaches"])
    return Result("restated thresholds", PASS,
                  f"{pinned} of {seen} governed threshold default(s) read the "
                  f"governed constant")


def check_register_group_counts() -> Result:
    """The failure register's declared counts must match its own entries.

    A miscount is not cosmetic here. The register is the lab's inventory of
    what did not work, and a group that says five and holds four has lost an
    entry without anybody noticing.
    """
    if not REGISTER.exists():
        return Result("register group counts", FAIL,
                      "NOT_PASSING_REGISTER.md is missing")
    lines = REGISTER.read_text(encoding="utf-8", errors="replace").splitlines()
    groups, current, entries = [], None, 0
    declared = None
    for line in lines:
        if line.startswith("## GROUP"):
            if current is not None:
                groups.append((current, declared, entries))
            current, declared, entries = line[3:].strip(), None, 0
        elif line.startswith("## ") and current is not None:
            groups.append((current, declared, entries))
            current, declared, entries = None, None, 0
        elif current is not None:
            found = re.match(r"\*\*Count:\s*(\d+)\s*cases?\*\*", line.strip())
            if found:
                declared = int(found.group(1))
            elif line.startswith("### "):
                entries += 1
    if current is not None:
        groups.append((current, declared, entries))
    problems = []
    for name, count, actual in groups:
        if count is None:
            problems.append(f"{name}: declares no count")
        elif count != actual:
            problems.append(f"{name}: declares {count}, holds {actual} entries")
    total_declared = None
    for cells in _md_rows(REGISTER):
        if cells and cells[0].strip().upper().startswith("**TOTAL"):
            digits = re.search(r"(\d+)", cells[1] if len(cells) > 1 else "")
            if digits:
                total_declared = int(digits.group(1))
    total_actual = sum(a for _, _, a in groups)
    if total_declared is not None and total_declared != total_actual:
        problems.append(f"summary total declares {total_declared}, the groups "
                        f"hold {total_actual}")
    if problems:
        return Result("register group counts", WARN,
                      f"{len(problems)} count(s) in the failure register do "
                      f"not match its own entries",
                      problems + ["counted by heading; one entry can cover "
                                  "several cases, so a mismatch is a reading, "
                                  "not automatically an error"])
    if not groups:
        return _no_selection(
            "register group counts",
            f"the failure register was read ({len(lines)} lines) and no group "
            f"was found in it, so no declared count was compared to anything",
            [REGISTER],
            "a line beginning '## GROUP'",
            ["'0 groups, 0 entries, every count agrees' is the register's "
             "inventory reported clean by counting nothing; the file is there, "
             "so either the register was emptied or its heading convention "
             "moved"])
    return Result("register group counts", PASS,
                  f"{len(groups)} groups, {total_actual} entries, every count "
                  f"agrees")


def _uq_module():
    sys.path.insert(0, str(REPO / "sdk"))
    from chief_engineer import uq  # noqa: PLC0415
    return uq


# Two fixtures, chosen so the union of their keys covers every branch of the
# fit a stored study can land in: one ladder that certifies and one that is
# declined. Both are synthetic and neither is published anywhere; they exist
# only to ask the fit what it currently emits.
#
# THE UNION IS A CEILING, NOT THE REQUIREMENT. Both fixtures are monotone, so
# both reach the branch that fits an order and the union carries
# `asymptotic` and `richardson_extrapolated`. A non-monotone ladder never
# fits an order, and its fit deliberately does NOT record those two -- a guard
# that never ran is absent, not False. Measuring every study against the union
# therefore demands fields the study's own fit refuses to invent. So the union
# is only the fallback, used when a record cannot be refitted; a record that
# stores its rungs is measured against what ITS OWN fit emits (`_own_fit`).
_FIT_FIXTURES = (
    # phi = 0.42 + 0.05 h^2 on an 8x-per-rung 3D ladder: certifies at p = 2.
    ([10000, 80000, 640000], [1.22, 0.62, 0.47], 3),
    # The cylinder vortex-shedding rungs: declined, and by two guards at once.
    ([2496, 5032, 8640], [0.1245, 0.1490, 0.1578], 3),
)

# What it costs to fix each of the two faults below, stated where the fault is
# reported. THE DEFECT THIS REPLACES: both checks reported a missing field and
# said repairing it was "a decision about compute", which readers priced as a
# re-run of the study. It is not. A stored study carries its own rungs under
# `levels`, with cell counts and functionals; the fit is arithmetic on those,
# so it can be recomputed from the record in place for nothing. Of the eight
# fitted studies in this corpus, seven store their rungs and one does not, and
# only that one needs a solve. A remedy quoted an order of magnitude too high
# is a reason not to do the work, so the price now travels with the fault.
REMEDY_REFIT = ("remedy: refit in place from the {n} rungs this study already "
                "stores under levels[], through uq.study_numerical; NO COMPUTE")
REMEDY_NO_RUNGS = ("remedy: this record stores no rungs, so nothing here can "
                   "be recomputed from it; NEEDS COMPUTE (re-run the ladder) "
                   "or the record must be marked unverifiable or withdrawn")


def _own_fit(uq, study):
    """Re-run the fit that produced this study, from the study's own rungs.

    Returns the fit dict, or None when the record cannot be refitted -- either
    it stores no usable rungs, or no current fit reproduces the method string
    it has on file, which means the stored numbers came from something other
    than the code running today. Spends no compute: `levels` already holds
    every cell count and functional the fit reads.
    """
    numerical = study.get("numerical") or {}
    levels = study.get("levels")
    if not isinstance(levels, list) or len(levels) < 3:
        return None
    try:
        cells = [float(level["cells"]) for level in levels]
        values = [float(level["cd"]) for level in levels]
    except (KeyError, TypeError, ValueError):
        return None
    # Monotonicity picks the branch, and monotonicity does not depend on dim,
    # so a study that has not yet recorded its dim can be read at 3 without
    # changing which fields its fit emits.
    dim = numerical.get("dim") or 3
    for fit_fn in (uq.eca_hoekstra_band, uq.ladder_band):
        try:
            fit = fit_fn(cells, values, dim=int(dim))
        except Exception:  # noqa: BLE001 - a fit that raises is not the one
            continue
        if fit.get("method") == numerical.get("method"):
            return fit
    return None


def _study_rungs(study) -> int:
    levels = study.get("levels")
    return len(levels) if isinstance(levels, list) else 0


# Why a study is out of scope for the two study checks below, in the study's
# own terms. THE DEFECT THIS REPLACES: both checks narrowed to refinement fits
# with a bare `continue`, so a record they could not read simply was not in the
# report -- not as a pass, not as a fault, not at all. Two of the ten stored
# studies were invisible that way, and one of them was aortic-valve, whose
# `conclusive: True` was a hardcoded literal and whose band was the only one in
# the corpus reaching a live certificate. The record that cannot be checked
# against its own evidence was the record the checks could not see, and an
# unauditable record is indistinguishable from a clean one. So every stored
# study is now either checked or named here with the reason, and the count of
# each rides on every verdict line.
def _out_of_scope(study) -> str | None:
    """The reason this study is not a refinement fit, or None if it is one."""
    numerical = study.get("numerical") or {}
    if not numerical:
        return "no numerical block at all; nothing here states a fitted band"
    if "conclusive" not in numerical:
        return ("its numerical block records no `conclusive` verdict, so no "
                "fit ever adjudicated it")
    if "observed_order" not in numerical:
        kind = numerical.get("channel_kind")
        method = str(numerical.get("method") or "").split(";")[0].strip()
        what = f"{kind}" if kind else "not produced by a refinement fit"
        return (f"its numerical block records no `observed_order`, so it did "
                f"not come out of a refinement fit: {what}"
                + (f" ({method})" if method else ""))
    return None


def check_studies_carry_what_the_fit_records() -> Result:
    """A stored study must carry every field its own fit produces.

    THE DEFECT. Both study writers built the `numerical` block from a
    hand-typed list of keys. A hand-typed list keeps working when the fit
    learns to record something new, and drops the new field on every study it
    writes, in silence. When `eca_hoekstra_band` began recording the
    dimensionality its band was fitted with, not one stored study picked it up
    -- not because they predate the field, but because nothing was copying it.
    A record that omits what it was not told to keep looks complete, which is
    worse than one that never had the field: nothing on the file says a field
    is missing rather than absent.

    THE CHECK. Ask the fit what it emits today, subtract the exclusions the
    writers name out loud (`uq.STUDY_NUMERICAL_DROPS`), and read every stored
    study's `numerical` block for the remainder. A study written by an older
    writer is reported, not repaired -- this file never writes.

    WHAT "the fit emits today" MEANS PER STUDY. Preferably, the study's own
    fit re-run from the study's own stored rungs (`_own_fit`): a non-monotone
    ladder's fit never evaluates the post-order guards, so demanding
    `richardson_extrapolated` of it would be demanding an invented number.
    Only a record that cannot be refitted falls back to the union over the
    fixtures, which is a ceiling rather than the requirement.

    AND WHAT IT COSTS. Each fault now names its own remedy and whether that
    remedy needs compute. This check used to say only that repair "is a
    decision about compute", which read as a re-run of the study; for every
    record that stores its rungs the repair is arithmetic on data already on
    disk, and pricing it as a solve is how a cheap fix goes undone.

    This compares a published record against a re-derivation from the code
    that produces it, which is a verification of the record, not a
    surface-to-surface consistency check.
    """
    try:
        uq = _uq_module()
    except Exception as exc:  # noqa: BLE001
        return Result("studies carry what the fit records", WARN,
                      f"cannot import the fit: {type(exc).__name__}: {exc}")
    expected: set[str] = set()
    for cells, values, dim in _FIT_FIXTURES:
        for fit in (uq.eca_hoekstra_band, uq.ladder_band):
            try:
                expected |= set(fit(cells, values, dim=dim))
            except Exception as exc:  # noqa: BLE001
                return Result("studies carry what the fit records", FAIL,
                              f"{fit.__name__} raised on a fixture: "
                              f"{type(exc).__name__}: {exc}")
    expected -= set(uq.STUDY_NUMERICAL_DROPS)
    expected -= {"band_abs_middle"}   # a runner-chosen alternative to band_abs
    studies, blind = _stored_studies("studies carry what the fit records")
    if blind:
        return blind
    problems, notes, skipped, checked = [], [], [], 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            problems.append(f"{path.name}: does not parse")
            continue
        numerical = study.get("numerical") or {}
        # Only blocks that came out of a refinement fit are in scope. Every
        # branch of both fits sets `observed_order`, even when it sets it to
        # None, and no other producer does; the valve's quadrature convergence
        # of a reduced-order model is a different shape and is not measured
        # against this one. Scoping on the method text instead would silently
        # exempt exactly the declined ladders this check most needs to read,
        # because a guard-failure method string does not mention a mesh.
        #
        # OUT OF SCOPE IS NOT INVISIBLE. Anything this check cannot read is
        # named, with the reason, on the same report.
        reason = _out_of_scope(study)
        if reason:
            skipped.append(f"{path.stem}: SKIPPED, not in scope for this "
                           f"check -- {reason}")
            continue
        checked += 1
        rungs = _study_rungs(study)
        own = _own_fit(uq, study)
        if own is not None:
            want = (set(own) - set(uq.STUDY_NUMERICAL_DROPS)
                    - {"band_abs_middle"})
            remedy = REMEDY_REFIT.format(n=rungs)
        else:
            want = expected
            if rungs >= 3:
                # It stores rungs, and still cannot be refitted. That is a
                # sharper finding than a missing field: the stored method
                # string is one no fit running today produces.
                notes.append(
                    f"{path.stem}: stores {rungs} rungs but no current fit "
                    f"reproduces its stored method string, so its numbers "
                    f"were not produced by the fit running today; measured "
                    f"against the fixture ceiling instead")
                remedy = ("remedy: establish which producer wrote this block "
                          "before refitting it; NO COMPUTE to find out")
            else:
                remedy = REMEDY_NO_RUNGS
        missing = sorted(want - set(numerical))
        if missing:
            problems.append(
                f"{path.stem}: numerical block is missing "
                f"{', '.join(missing)}; its own fit records "
                f"{len(want)} field(s) and this study carries "
                f"{len(want) - len(missing)}. {remedy}")
    scope = (f"{checked} of {checked + len(skipped)} stored study(s) in "
             f"scope, {len(skipped)} named as skipped")
    if problems:
        needs_compute = sum(1 for p in problems if "NEEDS COMPUTE" in p)
        return Result("studies carry what the fit records", FAIL,
                      f"{len(problems)} stored study(s) omit a field their "
                      f"own fit produces; {len(problems) - needs_compute} are "
                      f"refittable in place at no compute, {needs_compute} "
                      f"need a solve; {scope}", problems + notes + skipped)
    if notes:
        return Result("studies carry what the fit records", INFO,
                      f"all {checked} fitted study(s) carry every field their "
                      f"own fit records; {len(notes)} could not be refitted; "
                      f"{scope}", notes + skipped)
    if not checked:
        return _no_study_in_scope(
            "studies carry what the fit records", studies,
            "a study whose numerical block came out of a refinement fit "
            "(_out_of_scope declines everything else)",
            f"all {len(skipped)} study(s) read were declined by _out_of_scope, "
            f"so no field set was compared to any fit")
    return Result("studies carry what the fit records", PASS,
                  f"all {checked} fitted study(s) carry every field their own "
                  f"fit records; {scope}", skipped)


def check_stored_fits_reproduce_their_values() -> Result:
    """A stored study's numbers must equal what its own rungs still produce.

    THE GAP THIS CLOSES. `check_studies_carry_what_the_fit_records` compares
    KEY SETS: it asks whether a study carries every field the fit emits, and
    never asks whether the values under those keys are the values the fit
    emits. A writer that stored a stale band, a hand-typed verdict, or a number
    from a rung it later replaced passes that check with a full field set. The
    aortic-valve study is the standing example: its `conclusive: True` was a
    typed literal, not anything a guard produced, and no field-presence check
    can see the difference between a literal and a computed value.

    THE CHECK. Refit each study from the rungs it stores under `levels[]`,
    through the same fit whose method string it records, and compare value by
    value. Zero compute: `levels` already holds every cell count and functional
    the fit reads.

    WHAT IT CATCHES AND WHAT IT DOES NOT. It catches the record writer -- a
    stored number that the fit would not produce from the study's own rungs
    today. It shares `chief_engineer.uq` with the code that wrote those
    numbers, so it is blind to a defect inside the fit itself: a wrong band
    computed one way and stored, then recomputed the same wrong way, agrees.
    That limit is declared in BASIS and is the whole point of declaring it.
    """
    try:
        uq = _uq_module()
    except Exception as exc:  # noqa: BLE001
        return Result("stored fits reproduce their values", WARN,
                      f"cannot import the fit: {type(exc).__name__}: {exc}")
    studies, blind = _stored_studies("stored fits reproduce their values")
    if blind:
        return blind
    problems, notes, checked, compared = [], [], 0, 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            problems.append(f"{path.name}: does not parse")
            continue
        numerical = study.get("numerical") or {}
        if not numerical:
            continue
        rungs = _study_rungs(study)
        own = _own_fit(uq, study)
        if own is None:
            # Named, not skipped in silence: a record whose stored numbers no
            # current fit reproduces is the record this check most wants to
            # read, and it is exactly the one it cannot.
            notes.append(
                f"{path.stem}: stores {rungs} rung(s) and NO CURRENT FIT "
                f"reproduces its stored method string "
                f"{str(numerical.get('method') or '')[:60]!r}, so none of its "
                f"values can be checked against its own evidence; remedy: "
                f"establish which producer wrote this block, and whether that "
                f"producer still exists, before any number here is believed "
                f"or rewritten; NO COMPUTE to find out"
                + ("" if rungs >= 3 else ", and it stores no usable rungs"))
            continue
        checked += 1
        drops = set(uq.STUDY_NUMERICAL_DROPS)
        for key in sorted(set(own) & set(numerical)):
            if key in drops:
                continue
            stored, fresh = numerical[key], own[key]
            compared += 1
            if isinstance(stored, (int, float)) and isinstance(
                    fresh, (int, float)) and not isinstance(stored, bool) \
                    and not isinstance(fresh, bool):
                scale = max(1.0, abs(float(fresh)))
                if abs(float(stored) - float(fresh)) <= 1e-9 * scale:
                    continue
            elif stored == fresh:
                continue
            problems.append(
                f"{path.stem}: numerical[{key}] is stored as {stored!r}; "
                f"refitting this study's own {rungs} rungs through "
                f"{own.get('method', '')[:40]!r} produces {fresh!r}. "
                + REMEDY_REFIT.format(n=rungs))
    if problems:
        return Result("stored fits reproduce their values", FAIL,
                      f"{len(problems)} stored value(s) are not what this "
                      f"study's own rungs produce", problems + notes)
    if notes:
        return Result("stored fits reproduce their values", WARN,
                      f"all {compared} value(s) across {checked} refittable "
                      f"study(s) reproduce; {len(notes)} study(s) cannot be "
                      f"refitted at all and are unchecked", notes)
    if not checked or not compared:
        return _no_study_in_scope(
            "stored fits reproduce their values", studies,
            "a study carrying a numerical block that _own_fit can reproduce "
            "from the rungs stored under levels[]",
            f"{checked} study(s) were refittable and {compared} stored value(s) "
            f"were compared, so 'all 0 stored value(s) reproduce' would be a "
            f"statement about values none of which was read")
    return Result("stored fits reproduce their values", PASS,
                  f"all {compared} stored value(s) across {checked} study(s) "
                  f"reproduce from the study's own rungs")


def check_declined_ladders_name_their_guard() -> Result:
    """A declined ladder must record WHICH guard held it, not only a sentence.

    THE DEFECT. The cylinder vortex-shedding ladder was declined for an
    observed order of 3.646, outside the credible window. Fitted on its own
    two-dimensional mesh that order is 2.430, inside it. The act stayed
    declined, because its extrapolated Strouhal number overshoots the range it
    measured and that guard does not depend on dimensionality at all. So the
    verdict never moved and the stated reason was wrong for a day, and nothing
    on the record could show it: `uq.not_conclusive_reason` DERIVES the
    sentence, so it silently reassigned itself when the arithmetic changed.

    THE CHECK. Every declined ladder in a stored study must carry
    `not_conclusive_guard` and a `guards` map, and the guard it names must be
    one the map actually records as failing. A verdict resting on more than
    one guard is reported as INFO, not a fault: it is the case where fixing
    the stated reason would not move the verdict, and somebody should know.

    AND WHAT IT COSTS. A ladder that stores its rungs can have its guard map
    recomputed from them in place, for nothing; only a record with no rungs
    behind it needs a solve. The remedy and its price are stated on each
    fault, because this check's first report was read as calling for eight
    re-runs when seven of the eight needed no compute at all.
    """
    try:
        uq = _uq_module()
    except Exception as exc:  # noqa: BLE001
        return Result("declined ladders name their guard", WARN,
                      f"cannot import the fit: {type(exc).__name__}: {exc}")
    studies, blind = _stored_studies("declined ladders name their guard")
    if blind:
        return blind
    problems, notes, skipped, checked = [], [], [], 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            problems.append(f"{path.name}: does not parse")
            continue
        numerical = study.get("numerical") or {}
        # SCOPE. A record that declines itself must name the guard that
        # declined it. That requirement does not depend on the record having
        # come out of a mesh fit, so the `observed_order` gate that used to sit
        # here is gone: it excluded the aortic-valve study, which is exactly
        # the record that most needed reading, since its verdict was a typed
        # literal rather than anything a guard produced. Everything out of
        # scope is named below with its reason instead of vanishing.
        if not numerical:
            skipped.append(f"{path.stem}: SKIPPED, not in scope for this "
                           f"check -- no numerical block at all, so there is "
                           f"no verdict here to decline")
            continue
        if "conclusive" not in numerical:
            skipped.append(f"{path.stem}: SKIPPED, not in scope for this "
                           f"check -- its numerical block records no "
                           f"`conclusive` verdict, so nothing adjudicated it "
                           f"either way")
            continue
        if numerical.get("conclusive") is not False:
            skipped.append(f"{path.stem}: SKIPPED, not in scope for this "
                           f"check -- conclusive is "
                           f"{numerical.get('conclusive')!r}, not a decline, "
                           f"so no guard is holding it")
            continue
        checked += 1
        rungs = _study_rungs(study)
        remedy = (REMEDY_REFIT.format(n=rungs) if rungs >= 3
                  else REMEDY_NO_RUNGS)
        guard = numerical.get("not_conclusive_guard")
        guards = numerical.get("guards")
        if not guard or not isinstance(guards, dict):
            problems.append(
                f"{path.stem}: declined, and the record does not say which "
                f"guard held it; the reason on any surface showing this "
                f"study is derived from the numbers as they stand today, not "
                f"the guard that fired when the fit ran. {remedy}")
            continue
        if guards.get(guard) is not False:
            problems.append(
                f"{path.stem}: states guard {guard!r} but its own guard map "
                f"records that guard as {guards.get(guard)!r}. {remedy}")
            continue
        held = [k for k, v in guards.items() if v is False]
        if len(held) > 1:
            notes.append(
                f"{path.stem}: declined on {guard!r} and would stay declined "
                f"on {', '.join(sorted(set(held) - {guard}))}")
    scope = (f"{checked} of {checked + len(skipped)} stored study(s) in "
             f"scope, {len(skipped)} named as skipped")
    if problems:
        needs_compute = sum(1 for p in problems if "NEEDS COMPUTE" in p)
        return Result("declined ladders name their guard", FAIL,
                      f"{len(problems)} declined ladder(s) do not record the "
                      f"guard that held them; "
                      f"{len(problems) - needs_compute} are refittable in "
                      f"place at no compute, {needs_compute} need a solve; "
                      f"{scope}", problems + notes + skipped)
    if notes:
        return Result("declined ladders name their guard", INFO,
                      f"all {checked} declined ladder(s) name their guard; "
                      f"{len(notes)} rest on more than one; {scope}",
                      notes + skipped)
    if not checked:
        return _no_study_in_scope(
            "declined ladders name their guard", studies,
            "a study whose numerical block records `conclusive` as False",
            f"all {len(skipped)} study(s) read carry no decline, so no guard "
            f"claim was checked against any guard map")
    return Result("declined ladders name their guard", PASS,
                  f"all {checked} declined ladder(s) name the guard that held "
                  f"them; {scope}", skipped)


# The two remedies this lab has already accepted for a whitelisting writer,
# both in-tree, so the check can name a precedent rather than a preference.
#   copy wholesale:  uq.study_numerical  -- {k: v for k, v in band.items()
#                    if k not in STUDY_NUMERICAL_DROPS}, plus dropped_from_fit
#   name the drops:  lab.credential_card -- CREDENTIAL_NOT_ON_CARD, each key
#                    with the reason it is not on the card
_DROP_DECLARATIONS = ("DROPS", "NOT_ON", "dropped_from", "dropped_keys",
                      "excluded_keys")


def _whitelist_source(node) -> str | None:
    """`src.get("k")` or `src["k"]` -> "src". Anything else -> None."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "get" \
            and isinstance(node.func.value, ast.Name) and node.args \
            and isinstance(node.args[0], ast.Constant) \
            and isinstance(node.args[0].value, str):
        return node.func.value.id
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
            and isinstance(node.slice, ast.Constant) \
            and isinstance(node.slice.value, str):
        return node.value.id
    return None


def check_record_writers_name_their_drops() -> Result:
    """A writer that whitelists keys drops what it was not told to keep.

    THE DEFECT. `eca_hoekstra_band` began recording the dimensionality its
    band was fitted with, and not one stored study picked the field up -- not
    because the studies predate it, but because both study writers built the
    `numerical` block from a hand-typed list of keys. A hand-typed list keeps
    working when the producer learns to record something new, and drops the
    new field on every record it writes, in silence. A record that omits what
    it was not told to keep looks complete, which is worse than one that never
    had the field: nothing on the file says a field is missing rather than
    absent. Both study writers are fixed; the shape is not confined to them.

    THE CHECK, and what it is honestly measuring. It finds the SHAPE: a dict
    literal four or more of whose values are `src.get("k")` or `src["k"]` from
    one source. That shape is the precondition for the defect, not the defect
    -- a writer whose source has exactly the keys it copies is fine, and this
    cannot tell the difference statically. So it separates the one case where
    the author demonstrably cannot know the key set, which is a source that
    arrives as a PARAMETER, from the case where the source was built a few
    lines up, and it reports rather than failing.

    THE BAR, from the charter clause this encodes: a record writer either
    copies what it is given or names the keys it drops. Both remedies have a
    precedent in this tree, and either clears the finding: iterate the
    source's `.items()`, or declare the exclusions in a named constant. A
    writer doing neither is one upstream field away from the study defect.
    """
    findings, local, cleared = [], [], []
    sources, blind = _py_corpus("record writers name their drops")
    if blind:
        return blind
    for source in sources:
        text = source.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for function in ast.walk(tree):
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            body = ast.get_source_segment(text, function) or ""
            parameters = {a.arg for a in function.args.posonlyargs
                          + function.args.args + function.args.kwonlyargs}
            for node in ast.walk(function):
                if not isinstance(node, ast.Dict):
                    continue
                counts: dict[str, int] = {}
                for value in node.values:
                    name = _whitelist_source(value)
                    if name:
                        counts[name] = counts.get(name, 0) + 1
                if not counts:
                    continue
                var, copied = max(counts.items(), key=lambda kv: kv[1])
                if copied < 4:
                    continue
                where = (f"{source.relative_to(REPO)}:{node.lineno} "
                         f"{function.name}() builds a record from {var!r} "
                         f"with {copied} hand-typed keys")
                if f"{var}.items()" in body:
                    cleared.append(f"{where}; also copies {var}.items()")
                elif any(word in body for word in _DROP_DECLARATIONS):
                    cleared.append(f"{where}; names its drops")
                elif var in parameters:
                    findings.append(
                        where + f", and {var!r} is a PARAMETER, so this "
                        f"function cannot see what its caller put in it. "
                        f"Remedy, either one: copy {var}.items() minus a named "
                        f"drop set, as uq.study_numerical does, or declare the "
                        f"exclusions in a constant, as lab.CREDENTIAL_NOT_ON_"
                        f"CARD does; NO COMPUTE")
                else:
                    local.append(where + f", and {var!r} is built in the same "
                                 f"function, so the author can see its keys")
    detail = findings + [
        f"{len(local)} more site(s) have the same shape on a locally built "
        f"source, which is the weaker case and is listed for the census:"] + \
        local[:10] + [
        f"{len(cleared)} site(s) already copy wholesale or name their drops"]
    if findings:
        return Result("record writers name their drops", WARN,
                      f"{len(findings)} writer(s) whitelist keys off a source "
                      f"they receive as a parameter and declare no drops",
                      detail)
    if not (findings or local or cleared):
        return _no_selection(
            "record writers name their drops",
            f"{len(sources)} Python source(s) were read and not one holds a "
            f"record-writing dict of the shape this check grades",
            [f"{root}/**/*.py" for root in _PY_ROOTS],
            "a dict literal four or more of whose values are src.get(\"k\") or "
            "src[\"k\"] from one name",
            ["the corpus is present, and with no site of any kind found the "
             "PASS sentence -- 'no writer whitelists keys off a parameter "
             "without saying what it leaves out' -- is true of an empty set "
             "and says nothing about this tree; the four-key bar and the two "
             "subscript spellings are what to re-read"])
    return Result("record writers name their drops", PASS,
                  f"no writer whitelists keys off a parameter without saying "
                  f"what it leaves out; {len(cleared)} declare their handling",
                  detail)


# A rung's stored precision matters only through one number: how much the
# extrapolation multiplies the finest increment. Below this the rounding is
# irrelevant however coarse; above it, the digits the record kept decide the
# answer. Not a tuned constant -- it is the point at which a half-unit in the
# last stored decimal starts to reach the band, and the check computes that
# reach per study rather than assuming it.
_ROUNDING_SHARE_OF_BAND = 0.10


def check_stored_rungs_carry_solved_precision() -> Result:
    """A refit reads what was solved, not what a table printed.

    THE DEFECT, measured. The supersonic wedge ladder was extrapolated twice
    from the same three rungs. Fitted on the values as the act's ladder table
    PRINTS them, at three decimals -- 47.588 / 46.123 / 44.693 -- the
    extrapolated shock angle is -13.733 degrees. Fitted on what the act
    solved -- 47.58767882153372 / 46.12330850878531 / 44.692792746510406 --
    it is -15.753. Two point zero two degrees apart, and the whole difference
    is rounding. Both readings are on the record and neither is withdrawn
    (demo-output/website/campaign/W3_2D_LADDER_REFIT.md section 4a).

    THE MECHANISM, which is why this is a rule and not a caution. At an
    observed order near zero the Richardson extrapolation amplifies the finest
    increment by a large factor -- 42.25 on that ladder. Whatever error the
    stored rungs carry is multiplied by the same factor. So the worse a ladder
    behaves, the more its refit depends on precision nobody thinks about, and
    a document is the one source that has already thrown that precision away.
    The cone, diamond and vortex-shedding orders moved in the third decimal
    the same way and changed no verdict; the wedge moved two degrees.

    THE CHECK, zero compute, from each study's own stored rungs. Compute the
    amplification the study's own extrapolation applies, and the reach of half
    a unit in the last decimal its rungs are stored to. Report where that
    reach exceeds a tenth of the study's own band, because that is the point
    at which the record's precision, rather than its measurements, is deciding
    the number. A study whose rungs are stored at full solved precision passes
    at any amplification, which is the behaviour to keep.
    """
    studies, blind = _stored_studies("stored rungs carry solved precision")
    if blind:
        return blind
    problems, notes, checked = [], [], 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            continue
        numerical = study.get("numerical") or {}
        phi0 = numerical.get("richardson_extrapolated")
        band = numerical.get("band_abs")
        levels = study.get("levels")
        if phi0 is None or not band or not isinstance(levels, list) \
                or len(levels) < 3:
            continue
        try:
            rows = sorted((l for l in levels if "cells" in l and "cd" in l),
                          key=lambda l: float(l["cells"]))[-3:]
            values = [float(r["cd"]) for r in rows]
        except (TypeError, ValueError):
            continue
        if len(values) < 3:
            continue
        checked += 1
        increment = abs(values[-1] - values[-2])
        if not increment:
            notes.append(f"{path.stem}: the finest two rungs are equal, so no "
                         f"amplification is defined")
            continue
        amplification = abs(float(phi0) - values[-1]) / increment
        # Decimals the record actually kept, per rung, from the stored text.
        decimals = min(len(repr(v).split(".")[-1]) for v in values)
        reach = amplification * 0.5 * (10.0 ** -decimals)
        share = reach / abs(float(band))
        line = (f"{path.stem}: extrapolation amplifies the finest increment "
                f"by {amplification:.2f}x; rungs stored to {decimals} "
                f"decimals, so half a unit in the last one reaches "
                f"{reach:.3g}, which is {share * 100:.4f} percent of the "
                f"study's own band of {float(band):.4g}")
        if share > _ROUNDING_SHARE_OF_BAND:
            problems.append(
                line + ". The precision this record kept, not its "
                "measurements, is deciding the extrapolated value; remedy: "
                "restore the rungs from the solve that produced them -- the "
                "forces file, not any table -- and refit; NO COMPUTE")
        else:
            notes.append(line)
    if problems:
        return Result("stored rungs carry solved precision", FAIL,
                      f"{len(problems)} of {checked} extrapolating ladder(s) "
                      f"are decided by their stored precision", problems + notes)
    if not checked:
        return _no_study_in_scope(
            "stored rungs carry solved precision", studies,
            "a study carrying richardson_extrapolated, a band_abs and at least "
            "three levels[] rungs with cells and cd",
            "no stored ladder extrapolates, so no amplification was computed "
            "and the precision rule was applied to nothing")
    return Result("stored rungs carry solved precision", PASS,
                  f"all {checked} extrapolating ladder(s) store rungs precise "
                  f"enough that rounding reaches under "
                  f"{_ROUNDING_SHARE_OF_BAND * 100:g} percent of their own "
                  f"band", notes)


def check_ladder_rungs_share_one_recipe() -> Result:
    """VERIFICATION_CHARTER section 3.2 rule 3, which had no checker.

    THE RULE. "A recipe audit precedes an order... read the refinement level
    from each rung's own dictionary and refuse a triple that does not share
    one." An order fitted across a change of mesh recipe is fitted across a
    change of EXPERIMENT and is not a discretization order at all. The second
    NACA 4412 ladder reported p = 10.467 that way. Section 3.1's rule about
    dimensionality has a checker and section 3.2's does not, so an order
    fitted across two recipes reaches a report with nothing objecting.

    WHY THE ORDER WINDOW DOES NOT COVER IT. The 4412's 10.467 is refused by
    `order_window`, so the verdict is right. The reason is wrong, and a right
    verdict resting on the wrong reason moves the moment the arithmetic does:
    an order of 2.3 fitted across the same recipe change would pass the window
    and be just as meaningless.

    THE CHECK, zero compute, from the rungs and the audit block already stored.
    A study's `recipe_audit.valid_family_cells` names the rungs that DO share
    one recipe. `eca_hoekstra_band` fits the finest three distinct cell counts
    it is handed. So the fit triple must be a subset of the valid family, and
    a study that carries no recipe audit at all cannot be known either way.

    TWO SEVERITIES, and the difference is whether the lab knows. A study whose
    own `recipe_audit` records the finding is a known, recorded matter that is
    reported and not escalated -- several defer explicitly to the open ruling
    on what a record should say when a body has no usable ladder. A study that
    fits across recipes with nothing on its record saying so, or that publishes
    an order with no recipe audit at all, is the case this check exists for.
    """
    studies, blind = _stored_studies("ladder rungs share one recipe")
    if blind:
        return blind
    problems, known, skipped, checked = [], [], [], 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            continue
        numerical = study.get("numerical") or {}
        if "observed_order" not in numerical:
            skipped.append(
                f"{path.stem}: SKIPPED, not in scope -- its numerical block "
                f"records no `observed_order`, so no refinement fit produced "
                f"it and there is no order here to be fitted across anything")
            continue
        checked += 1
        audit = study.get("recipe_audit")
        cells = []
        for level in study.get("levels") or []:
            try:
                value = int(level["cells"])
            except (KeyError, TypeError, ValueError):
                continue
            if value not in cells:
                cells.append(value)
        triple = sorted(cells)[-3:]
        if not isinstance(audit, dict) or not audit.get("finding"):
            order = numerical.get("observed_order")
            what = (f"publishes an observed order of {order!r}" if order
                    is not None else
                    "compares its rungs through a refinement fit that "
                    "declined to fit an order, and its fallback band is "
                    "still a comparison of those rungs")
            problems.append(
                f"{path.stem}: {what} and carries NO recipe "
                f"audit, so nothing on this record says whether its rungs "
                f"share one refinement recipe; remedy: read the refinement "
                f"level off each rung's own system/snappyHexMeshDict, as "
                f"b52.json and four others already do; NO COMPUTE")
            continue
        family = audit.get("valid_family_cells")
        if not isinstance(family, list) or not family:
            problems.append(
                f"{path.stem}: has a recipe audit with no "
                f"`valid_family_cells`, so the finding cannot be checked "
                f"against the rungs the fit used; NO COMPUTE to add it")
            continue
        outside = [c for c in triple if c not in set(int(f) for f in family)]
        if not outside:
            continue
        line = (f"{path.stem}: the fit triple {triple} includes "
                f"{outside}, which this study's OWN recipe audit excludes "
                f"from the family that shares one recipe ({sorted(family)}); "
                f"its observed order of {numerical.get('observed_order')!r} is "
                f"fitted across a change of experiment")
        # A record that states the finding itself is a known matter, not a
        # silent one, and several defer explicitly to an open ruling.
        acknowledged = any(
            str(audit.get(key) or "").strip()
            for key in ("numerical_block_untouched", "what_this_body_needs"))
        (known if acknowledged else problems).append(
            line + (". The record states this and names what the body needs, "
                    "so it is reported, not escalated"
                    if acknowledged else
                    ". Nothing on the record says so; NO COMPUTE to say it"))
    scope = (f"{checked} of {checked + len(skipped)} stored study(s) in "
             f"scope, {len(skipped)} named as skipped")
    if problems:
        return Result("ladder rungs share one recipe", FAIL,
                      f"{len(problems)} fitted ladder(s) publish an order "
                      f"with no recipe audit, or across recipes their record "
                      f"does not mention; {len(known)} more do so and say so; "
                      f"{scope}", problems + known + skipped)
    if known:
        return Result("ladder rungs share one recipe", WARN,
                      f"{len(known)} fitted ladder(s) fit across a recipe "
                      f"change that their own record names; {scope}",
                      known + skipped)
    if not checked:
        return _no_study_in_scope(
            "ladder rungs share one recipe", studies,
            "a study whose numerical block records an `observed_order`",
            f"all {len(skipped)} study(s) read record no observed order, so no "
            f"fit triple was compared against any recipe family")
    return Result("ladder rungs share one recipe", PASS,
                  f"all {checked} fitted ladder(s) fit inside a family their "
                  f"own recipe audit calls comparable; {scope}", skipped)


def check_order_window_declines_state_their_dimensionality() -> Result:
    """VERIFICATION_CHARTER section 3.1 rule 3, which had no checker.

    THE RULE. A ladder declined for an observed order outside the credible
    window must have its dimensionality checked before the decline is
    believed, because that is the one verdict the dimensionality assumption
    can fabricate. Changing `dim` divides every observed order by exactly 1.5
    and leaves a conclusive band and the extrapolated value untouched, so the
    assumption cannot corrupt a number; it can only wrongly admit or wrongly
    reject a ladder. Rules 1 and 2 of that section already have checkers
    (`uq.ladder_band` raises on an unstated `dim`, and the field-set check
    above reads `dim` off every stored study). Rule 3 had none.

    THE CHECK, two parts, both zero compute.

    1. A study declined with `order_window` among its failing guards must
       carry a `dimensionality` block whose `dim` agrees with the one its fit
       used, established from the case files rather than from the body's name,
       with at least one piece of evidence named.
    2. The same ladder is refit from its own stored rungs at the OTHER
       dimensionality, and the report says whether `order_window` would flip
       and whether the verdict would move with it. A flip that changes no
       verdict is the ordinary case and is INFO; a flip that would make the
       ladder conclusive is the case the charter exists to catch, and is a
       fault, because a published decline would then rest on an assumption
       rather than on the measurements.
    """
    try:
        uq = _uq_module()
    except Exception as exc:  # noqa: BLE001
        return Result("order-window declines state their dimensionality", WARN,
                      f"cannot import the fit: {type(exc).__name__}: {exc}")
    studies, blind = _stored_studies("order-window declines state their dimensionality")
    if blind:
        return blind
    problems, notes, checked = [], [], 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            continue
        numerical = study.get("numerical") or {}
        guards = numerical.get("guards")
        if numerical.get("conclusive") is not False or not isinstance(
                guards, dict) or guards.get("order_window") is not False:
            continue
        checked += 1
        block = study.get("dimensionality")
        if not isinstance(block, dict) or not block.get("evidence"):
            problems.append(
                f"{path.stem}: declined on order_window and states no "
                f"dimensionality evidence, so the one verdict this "
                f"assumption can fabricate rests on an unrecorded assumption; "
                f"remedy: read the out-of-plane boundary types off this "
                f"body's own archived case and record them; NO COMPUTE")
            continue
        if block.get("dim") != numerical.get("dim"):
            problems.append(
                f"{path.stem}: its dimensionality block says "
                f"{block.get('dim')!r} and its fit used "
                f"{numerical.get('dim')!r}")
            continue
        rungs = _study_rungs(study)
        if rungs < 3:
            notes.append(f"{path.stem}: stores {rungs} rungs, so the other "
                         f"dimensionality cannot be read from this record")
            continue
        levels = study["levels"]
        try:
            cells = [float(level["cells"]) for level in levels]
            values = [float(level["cd"]) for level in levels]
        except (KeyError, TypeError, ValueError):
            notes.append(f"{path.stem}: rungs are not readable as cells and "
                         f"values")
            continue
        dim = int(numerical.get("dim") or 3)
        other = 2 if dim == 3 else 3
        try:
            alt = uq.eca_hoekstra_band(cells, values, dim=other)
        except Exception as exc:  # noqa: BLE001
            notes.append(f"{path.stem}: refit at dim={other} raised "
                         f"{type(exc).__name__}")
            continue
        flips = (alt.get("guards") or {}).get("order_window") is True
        conclusive = bool(alt.get("conclusive"))
        line = (f"{path.stem}: p = {numerical.get('observed_order')} at "
                f"dim={dim}, {alt.get('observed_order')} at dim={other}; "
                f"order_window {'would pass' if flips else 'still fails'} "
                f"there, verdict "
                f"{'would become conclusive' if conclusive else 'does not move'}")
        if flips and conclusive:
            problems.append(line + "; the decline rests on the "
                            "dimensionality alone and the mesh has to settle "
                            "it; NO COMPUTE")
        else:
            notes.append(line)
    if problems:
        return Result("order-window declines state their dimensionality", FAIL,
                      f"{len(problems)} of {checked} order-window decline(s) "
                      f"cannot be believed as they stand", problems + notes)
    if not checked:
        return _no_study_in_scope(
            "order-window declines state their dimensionality", studies,
            "a study declined (conclusive False) with order_window False in "
            "its own guards map",
            "'no stored ladder is declined on order_window' is the one "
            "sentence this check can print without opening a ladder, and it "
            "was a PASS")
    return Result("order-window declines state their dimensionality", INFO,
                  f"all {checked} order-window decline(s) name the "
                  f"dimensionality their fit used and hold at the other one",
                  notes)


def check_campaign_json_citations() -> Result:
    """Machine-readable citations in the campaign records must resolve.

    The markdown citation check covers backticked paths in prose. The JSON
    companions carry theirs as fields, and nothing looked at those.
    """
    interesting = {"report", "report_json", "artifact", "log", "evidence",
                   "ledger", "source_file", "primary_evidence"}
    missing, total = [], 0

    def walk(node, path, where):
        nonlocal total
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else key, where)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]", where)
        elif isinstance(node, str):
            leaf = path.rsplit(".", 1)[-1].split("[")[0]
            if leaf not in interesting or "/" not in node:
                return
            # An `evidence` field is sometimes a sentence that happens to
            # contain a slash. A citation is path-shaped: no whitespace, and
            # it ends in a file extension or a directory.
            if re.search(r"\s", node) or not re.search(
                    r"(\.[A-Za-z0-9]{1,6}|/)$", node):
                return
            candidate = node.lstrip("/")
            if node.startswith("/"):
                candidate = node
                resolved = Path(candidate)
            else:
                resolved = REPO / candidate
            total += 1
            if not resolved.exists():
                missing.append(f"{where}: {path} cites {node}")

    companions = sorted(CAMPAIGN.glob("*.json"))
    if not companions:
        return _no_evidence(
            "campaign json citations",
            "no campaign JSON companion was found to read citations out of",
            [f"{_rel(CAMPAIGN)}/*.json"])
    for source in companions:
        walk(_load_json(source), "", source.relative_to(REPO))
    if missing:
        return Result("campaign json citations", FAIL,
                      f"{len(missing)} of {total} machine-readable citations "
                      f"do not resolve", missing[:25])
    if not total:
        return _no_selection(
            "campaign json citations",
            f"{len(companions)} campaign companion(s) were read and none "
            f"carries a machine-readable citation",
            [f"{_rel(CAMPAIGN)}/*.json"],
            f"a path-shaped string under a field named one of "
            f"{', '.join(sorted(interesting))}",
            ["the companions are on disk; what matched nothing is the FIELD "
             "NAME set, so a writer that renamed its citation field empties "
             "this check without emptying its corpus"])
    return Result("campaign json citations", PASS,
                  f"all {total} machine-readable campaign citations resolve")


# ---------------------------------------------------------------------------
# The shipped laptop bundle.
#
# THE ARTIFACT IS THE ZIP, AND THE REFERENCE MUST BE REPRODUCIBLE.
# `dist/certonomous-demo.zip` is TRACKED, so any clone at any commit can
# extract the exact bytes that left this box. `dist/certonomous-demo/` is
# GITIGNORED -- `.gitignore:72`, in its own words "the .zip is committed; the
# extracted tree is not".
#
# Until 2026-08-15 this check compared the tree against THE DIRECTORY. Three
# consequences, all measured (docket D118):
#
#   1. The only file that ships is the one nothing read. The directory and the
#      zip agreed only because one build wrote both; nothing enforced it.
#      Regenerate the directory without rebuilding the zip and the check went
#      green over a stale shipped artifact -- the silent-zero shape (class B1)
#      in the one place it costs most.
#   2. Every verdict it ever recorded is unfalsifiable. Because the reference
#      was untracked, no later agent can reconstruct what the check saw on
#      2026-08-11, so the `56/56` recorded that day was a CLAIM, not a
#      measurement, until it was re-derived against the tracked zip.
#      A VERIFICATION WHOSE REFERENCE IS GITIGNORED EXPIRES THE MOMENT IT IS
#      MADE.
#   3. The zip holds 90 members and the check graded 56. The 34 ungraded
#      members -- including `snapshot/lab_stats.json`, which carried defect 4
#      of the 2026-08-10 rebuild -- could not appear in any numerator it
#      printed, and nothing said so.
#
# The repair reads members from the zip, and states the whole 90 every run:
# what it compared, what it declined to compare and why, and what it could not
# classify at all.
_BUNDLE_ZIP = Path("dist") / "certonomous-demo.zip"
# The unpacked build directory. Kept, per BUNDLE_REBUILD_2026-08-10 section 4,
# because it is what a human opens -- but it is a CONVENIENCE COPY and this
# check never grades against it. Its agreement with the zip is reported as an
# observation, because a disagreement means somebody rebuilt one and not the
# other, which is precisely the failure mode above.
_BUNDLE_DIR = Path("dist") / "certonomous-demo"

# The two sets of files the laptop bundle copies VERBATIM out of TRACKED
# sources, each as (label, source directory, member directory, glob). These are
# the only members whose reference is reproducible from a clone, so they are
# the only members that carry the verdict.
_BUNDLE_VERBATIM = (
    ("control room", Path("sdk/chief_engineer"), Path("sdk/chief_engineer"),
     "**/*"),
    ("launcher", Path("scripts/laptop_bundle"), Path("."), "*"),
)
# The static pages, which move from demo-output/website into site/ and are the
# one set whose member path is not its repo path.
_BUNDLE_PAGES = (
    ("closure.html", Path("demo-output/website/closure.html"),
     Path("site/closure.html")),
    ("benchmarks.html", Path("demo-output/website/benchmarks.html"),
     Path("site/benchmarks.html")),
    ("wall.html", Path("demo-output/website/wall/wall.html"),
     Path("site/wall/wall.html")),
)
_BUNDLE_SKIP = ("__pycache__", ".pyc")

# Classes a shipped member can fall into. The classification is applied to the
# ZIP'S OWN MEMBER LIST -- it is never read off a list maintained here. D112's
# transferable shape is that A CLEARANCE VERIFIED AGAINST AN ENUMERATION CANNOT
# SEE THE ITEM BESIDE THE ONES IT LISTS, and that is exactly what produced the
# fourth stale claim in a bundle rebuilt to clear the third. So a member that
# matches no rule below is UNCLASSIFIED: it is named in the report and it turns
# this check UNKNOWN. It is never dropped, because dropping is how the 56
# became invisible as a subset of 90 in the first place.
_GRADED = "graded"
_DERIVED = "derived-at-build"
_UNTRACKED_SRC = "untracked-source"
_UNCLASSIFIED = "unclassified"

#: (member prefix, class, source root or None, why). Prefix rules, not member
#: names: a new file under a known prefix classifies itself, and a new prefix
#: does not.
_BUNDLE_MEMBER_RULES = (
    ("snapshot/", _DERIVED, None,
     "computed at build time by build_laptop_bundle._capture_panels() with the "
     "whole repo present (builder step 4). NO SOURCE FILE EXISTS to compare "
     "against: the credentials wall re-grades each body against the refinement "
     "ladders on disk and lab-stats counts 208k ledger rows, and copying the "
     "small inputs gets both wrong in the direction that CLAIMS MORE"),
    ("mission-state/", _UNTRACKED_SRC,
     Path("sdk") / "chief-engineer-runs" / "mission-state",
     "copied verbatim (builder step 2) from sdk/chief-engineer-runs/, which is "
     "GITIGNORED at .gitignore:15. Grading it would put this check's verdict "
     "back onto a reference no clone can reproduce, which is the D118 defect "
     "itself one level down; the divergence below is an observation, not a "
     "verdict, and it expires"),
    ("mission-output/", _UNTRACKED_SRC, Path("mission-output"),
     "copied verbatim (builder step 3) from mission-output/, which is "
     "GITIGNORED at .gitignore:13. Same reason: reported, observed, not graded"),
)


def _bundle_pairs() -> list[tuple[str, Path, str]]:
    """(label, tracked source, ZIP MEMBER NAME) for the copied-verbatim set.

    The third element changed on 2026-08-15 (D118) from a path inside the
    gitignored build directory to the member name inside the tracked shipped
    archive. Anything reading this function for a filesystem path is reading a
    reference that no longer exists.
    """
    pairs: list[tuple[str, Path, str]] = []
    for label, src_dir, dst_dir, pattern in _BUNDLE_VERBATIM:
        root = REPO / src_dir
        if not root.is_dir():
            continue
        for src in sorted(root.glob(pattern)):
            if not src.is_file():
                continue
            rel = src.relative_to(root)
            if any(part in str(rel) for part in _BUNDLE_SKIP):
                continue
            pairs.append((label, src, (dst_dir / rel).as_posix()))
    for label, src, dst in _BUNDLE_PAGES:
        if (REPO / src).is_file():
            pairs.append((f"page {label}", REPO / src, dst.as_posix()))
    return pairs


def _bundle_members(archive: zipfile.ZipFile) -> tuple[dict[str, bytes], str]:
    """Every file member of the shipped archive, keyed by bundle-relative name.

    The archive root is DERIVED from the members rather than assumed, because
    `build_laptop_bundle.py --out` can name it anything; the derived root is
    printed in the frame so a reader can see which prefix was stripped.
    """
    names = [i.filename for i in archive.infolist() if not i.is_dir()]
    tops = {n.split("/", 1)[0] for n in names if "/" in n}
    root = f"{tops.pop()}/" if len(tops) == 1 and all(
        "/" in n for n in names) else ""
    members: dict[str, bytes] = {}
    for name in names:
        rel = name[len(root):] if root and name.startswith(root) else name
        if any(part in rel for part in _BUNDLE_SKIP):
            continue
        members[rel] = archive.read(name)
    return members, root


def _classify_bundle_member(rel: str, graded: set[str]
                            ) -> tuple[str, str, Path | None, str]:
    """(class, rule key, source path or None, reason) for one shipped member.

    The rule key is reported separately from the class on purpose. Two rules
    share the `untracked-source` class for two different gitignore lines, and
    a frame that printed one reason per CLASS would print one of them and drop
    the other -- which is the omission this whole check exists to stop doing.
    """
    if rel in graded:
        return (_GRADED, "tracked copy list", None,
                "copied verbatim from a tracked source")
    for prefix, cls, source_root, why in _BUNDLE_MEMBER_RULES:
        if rel.startswith(prefix):
            source = (REPO / source_root / rel[len(prefix):]
                      if source_root is not None else None)
            return cls, prefix, source, why
    return (_UNCLASSIFIED, "(no rule)", None,
            "matches no rule in _BUNDLE_MEMBER_RULES and no tracked source in "
            "_bundle_pairs(): this check cannot say whether it is correct, "
            "stale, or shipped by mistake")


def check_bundle_drift() -> Result:
    """The shipped bundle must not fall behind the tree it was built from.

    WHY THIS EXISTS. The laptop bundle is the artifact people actually run: it
    is the backup console for the shoot, and it is the only copy of this code
    that leaves the box. It went 32 commits behind without anything noticing.
    Twenty-one modules and the control room had drifted, one module was absent
    from the bundle entirely, and it shipped a certificate that captioned any
    envelope a 95 percent confidence interval long after that was fixed here.
    None of it was detected. The one bug that did surface was found by hand, by
    somebody on a different errand.

    This compares bytes, not dates. A module whose mtime moved but whose
    content did not is not drift, and a module edited in place on the same
    second is.

    IT READS THE ZIP, NOT THE DIRECTORY BESIDE IT (2026-08-15, D118).
    `dist/certonomous-demo.zip` is tracked and `dist/certonomous-demo/` is
    gitignored, so only the zip gives a verdict a later agent can re-derive.
    See the comment block above `_BUNDLE_ZIP` for what the old reference cost.

    IT STATES ITS WHOLE FRAME, EVERY RUN. The archive holds more members than
    this check can grade. Each ungraded member is named with its class and the
    reason it is not graded, so the denominator says what it declines to grade
    instead of silently omitting it. Three classes decline for three different
    reasons and they must not be confused: `derived-at-build` has no source
    file at all, `untracked-source` has one that no clone can reproduce, and
    `unclassified` is this check admitting it does not know.

    THREE-VALUED, AND IT CANNOT PASS FROM AN EMPTY SET (class B1). A missing or
    unreadable archive is UNKNOWN with the reason, never PASS and never a
    quiet WARN: an absent artifact does not mean "nothing to report", it means
    THIS DETECTOR IS OFF for the one artifact that leaves this box. So is an
    archive with no members, an empty copy list, or any member this check
    cannot classify.

    A file missing from the archive FAILs on its own: an absent module is
    worse than a stale one, because a stale module still answers and an absent
    one takes a page down with an import error.
    """
    name = "bundle drift vs shipped zip"
    zip_path = REPO / _BUNDLE_ZIP
    if not zip_path.is_file():
        return Result(name, UNKNOWN,
                      f"NO SHIPPED ARCHIVE at {_BUNDLE_ZIP.as_posix()}: the "
                      f"drift detector for the artifact that leaves this box "
                      f"is OFF, not merely uninformative",
                      ["UNKNOWN, not PASS and not WARN: nothing is being "
                       "compared, and a silence here reads as success exactly "
                       "where it costs most (defect class B1, L-45)",
                       "build it with scripts/build_laptop_bundle.py --zip, or "
                       "record that the lab no longer ships one"])
    try:
        with zipfile.ZipFile(zip_path) as archive:
            members, root = _bundle_members(archive)
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        # Named, not swallowed. An unreadable archive is the detector being
        # off, and the exception text is the only evidence of why.
        return Result(name, UNKNOWN,
                      f"{_BUNDLE_ZIP.as_posix()} is UNREADABLE "
                      f"({type(exc).__name__}: {exc}): the drift detector is "
                      f"OFF",
                      ["UNKNOWN, not PASS: an archive that will not open has "
                       "not been checked and must not be reported as clean"])
    pairs = _bundle_pairs()
    frame = [f"FRAME: {len(members)} member(s) in "
             f"{_BUNDLE_ZIP.as_posix()} (root {root or '(none)'!r}), "
             f"{len(pairs)} tracked source(s) in the copy list",
             f"reference: {_BUNDLE_ZIP.as_posix()} is TRACKED, so this verdict "
             f"re-derives from any clone at this commit -- unlike "
             f"{_BUNDLE_DIR.as_posix()}, gitignored at .gitignore:72, which "
             f"this check no longer grades against (D118)"]
    if not members:
        return Result(name, UNKNOWN,
                      f"{_BUNDLE_ZIP.as_posix()} opened but holds NO file "
                      f"members: nothing was compared", frame + [
                          "UNKNOWN, not PASS: a check must not pass from an "
                          "empty set"])
    if not pairs:
        return Result(name, UNKNOWN,
                      "found no files the builder copies verbatim out of "
                      "tracked sources; the builder's copy list and this "
                      "check have diverged", frame + [
                          "UNKNOWN, not PASS: with an empty copy list every "
                          "shipped member is ungraded"])

    graded_names = {member for _, _, member in pairs}
    missing, differs = [], []
    for label, src, member in pairs:
        rel = src.relative_to(REPO)
        if member not in members:
            missing.append(f"{label}: {rel} is ABSENT from the shipped zip "
                           f"(expected member {member})")
            continue
        if src.read_bytes() != members[member]:
            differs.append(f"{label}: {rel} differs from the shipped "
                           f"{member}")

    counts: dict[tuple[str, str], int] = {}
    reasons: dict[tuple[str, str], str] = {}
    unclassified, observations = [], []
    for rel in sorted(members):
        cls, rule, source, why = _classify_bundle_member(rel, graded_names)
        counts[(cls, rule)] = counts.get((cls, rule), 0) + 1
        reasons.setdefault((cls, rule), why)
        if cls == _UNCLASSIFIED:
            unclassified.append(f"UNCLASSIFIED shipped member {rel}: {why}")
        elif cls == _UNTRACKED_SRC and source is not None:
            # An observation, deliberately not a verdict. Its reference is
            # gitignored, so a green from it would expire on sight -- which is
            # the whole finding. It is reported because a member that has
            # moved is worth seeing even when it cannot be graded.
            if not source.is_file():
                observations.append(
                    f"OBSERVATION (not graded): {rel} has no source at "
                    f"{source.relative_to(REPO)} today")
            elif source.read_bytes() != members[rel]:
                observations.append(
                    f"OBSERVATION (not graded): {rel} differs from the "
                    f"untracked {source.relative_to(REPO)}")

    frame.append(f"compared: {len(pairs)} member(s) against tracked sources")
    # One line per RULE, in rule order, so every rule that fired states its own
    # reason and no rule's reason can be shadowed by another in its class.
    for cls in (_DERIVED, _UNTRACKED_SRC, _UNCLASSIFIED):
        for (member_cls, rule), count in counts.items():
            if member_cls == cls:
                frame.append(f"NOT compared: {count} member(s) under "
                             f"{rule!r}, class {cls} -- "
                             f"{reasons[(member_cls, rule)]}")
    graded_count = sum(n for (cls, _), n in counts.items() if cls == _GRADED)
    ungraded = len(members) - graded_count
    frame.append(f"so the denominator is {graded_count} of "
                 f"{len(members)} shipped member(s); the other {ungraded} are "
                 f"named above by class and are NOT in any numerator here")
    # The convenience copy, reported and never graded. A disagreement means
    # one of the two was rebuilt without the other, which is the exact route
    # by which this check used to go green over a stale shipped artifact.
    bundle_dir = REPO / _BUNDLE_DIR
    if not bundle_dir.is_dir():
        frame.append(f"OBSERVATION: {_BUNDLE_DIR.as_posix()} (the gitignored "
                     f"convenience copy) is absent; this does not affect the "
                     f"verdict, which is taken from the zip")
    else:
        drifted = sum(1 for rel, blob in members.items()
                      if not (bundle_dir / rel).is_file()
                      or (bundle_dir / rel).read_bytes() != blob)
        frame.append(f"OBSERVATION: {_BUNDLE_DIR.as_posix()} (gitignored "
                     f"convenience copy) differs from the zip in {drifted} of "
                     f"{len(members)} member(s)"
                     + ("" if drifted else " -- one build wrote both"))
    observations = observations[:10]

    if missing or differs:
        return Result(name, FAIL,
                      f"{len(missing)} file(s) missing from the shipped zip "
                      f"and {len(differs)} behind the tree, of {len(pairs)} "
                      f"copied verbatim from tracked sources "
                      f"({len(members) - ungraded - len(missing) - len(differs)}"
                      f" of {len(members)} shipped members verified)",
                      missing + differs + unclassified + observations + frame)
    if unclassified:
        return Result(name, UNKNOWN,
                      f"all {len(pairs)} copied file(s) match, and "
                      f"{len(unclassified)} shipped member(s) CANNOT BE "
                      f"CLASSIFIED: this check cannot say the artifact is "
                      f"clean", unclassified + observations + frame)
    return Result(name, PASS,
                  f"all {len(pairs)} file(s) the builder copies verbatim out "
                  f"of tracked sources match the shipped zip byte for byte "
                  f"({ungraded} of {len(members)} shipped members are ungraded "
                  f"by declared class, not by omission)",
                  observations + frame)


_RUNG_SHAPED = re.compile(
    r"\brung\b|\bladder\b|refinement|grid[\s-]convergence|finest grid", re.I)
_ITERATION_TERM = re.compile(
    r"\biterat|\bsteps?\b|\bsweeps?\b|endTime|time step", re.I)


def check_rung_estimates_state_their_iterations() -> Result:
    """A refinement rung priced by its cells alone is priced by half.

    THE DEFECT. The flat plate's finest rung came in at 1.48x its estimate and
    the entire overrun was settling: it was asked for 15,000 iterations, read
    1.05 percent above its settled value with the coefficient still falling,
    and took 36,000. Its cells were estimated correctly. Nothing in the
    estimate asked how long that grid takes to settle.

    WHY THE OMISSION IS THE EXPENSIVE HALF, measured rather than asserted. On
    this lab's own ledger (`demo-output/website/mega-batch/COST_SCALING.md`),
    wall time carries an exponent of essentially one on iterations in both
    families that record them, 1.156 on time steps and 1.026 on SIMPLE
    iterations, while the within-family cell exponents are small because cells
    barely vary inside a family. The term that overruns is the term nobody
    writes down.

    THE CHECK. Every compute proposal on the docket whose objective or
    rationale is rung-shaped must have a `cost_basis` that names an iteration,
    step or sweep count. This never blocks a proposal: it counts them, so the
    gap is a number on a report rather than a surprise on a run.
    """
    docket_path = REPO / "demo-output" / "website" / "agenda" / "docket.json"
    docket = _load_json(docket_path)
    # An unreadable docket used to arrive here as `{"__error__": ...}`, take
    # `.get("proposals")` -> None -> `or []`, and land on the "no rung-shaped
    # compute proposal is on the docket" PASS below -- a sentence about the
    # docket produced without reading one. The SOURCE being unreadable and the
    # docket holding no rung-shaped proposal are different facts and only the
    # second is a PASS.
    if isinstance(docket, dict) and "__error__" in docket:
        return _no_evidence(
            "rung estimates state their iterations",
            f"the docket did not open: {docket['__error__']}", [docket_path])
    proposals = (docket.get("proposals") if isinstance(docket, dict)
                 else docket) or []
    if not isinstance(proposals, list):
        return Result("rung estimates state their iterations", WARN,
                      "the docket did not parse as a list of proposals")
    rung, silent = [], []
    for proposal in proposals:
        if not isinstance(proposal, dict) or not proposal.get("est_core_min"):
            continue
        text = f"{proposal.get('objective', '')} {proposal.get('rationale', '')}"
        if not _RUNG_SHAPED.search(text):
            continue
        rung.append(proposal)
        if not _ITERATION_TERM.search(str(proposal.get("cost_basis") or "")):
            silent.append(proposal)
    if not rung:
        # EMPTY SELECTION, and it is not the unreadable docket guarded above.
        # The docket opened, it holds proposals, and `_RUNG_SHAPED` matched
        # none of them. Executed 2026-08-15 against a real docket carrying one
        # non-rung proposal: this returned "no rung-shaped compute proposal is
        # on the docket" as a PASS.
        return _no_selection(
            "rung estimates state their iterations",
            f"the docket opened and holds {len(proposals)} proposal(s); none "
            f"is rung-shaped, so no cost basis was read",
            [docket_path],
            "a proposal with an est_core_min whose objective or rationale "
            "matches _RUNG_SHAPED",
            ["the docket is present and non-empty; what matched nothing is "
             "_RUNG_SHAPED, and this check's own live finding is that a "
             "regex over prose can read a disclaimer as a disclosure -- so a "
             "zero from it is a reason to read the pattern, not a clean bill"])
    live = [p for p in silent if p.get("status") in ("proposed", "approved")]
    detail = [f"{p.get('id')}: {p.get('status')}, {p.get('est_core_min')} "
              f"core-min, basis prices the grid only"
              for p in sorted(live, key=lambda p: -float(
                  p.get("est_core_min") or 0))[:12]]
    detail.append(
        f"{len(silent)} of {len(rung)} rung-shaped compute proposal(s) name no "
        f"iteration count; {len(live)} of those are still proposed or approved")
    if live:
        return Result("rung estimates state their iterations", WARN,
                      f"{len(live)} unstarted rung estimate(s) price the grid "
                      f"and not the settling", detail)
    return Result("rung estimates state their iterations", PASS,
                  f"every unstarted rung estimate names an iteration count; "
                  f"{len(rung)} rung-shaped proposal(s) read", detail)


# --------------------------------------------------------------------------
# What each check is actually testing
# --------------------------------------------------------------------------
#
# THE DEFECT THIS EXISTS FOR. A check that re-derives a published number
# through the same function that published it cannot fail on a defect inside
# that function: the error is identical on both sides and reads as agreement.
# `check_wall_credentials_vs_results` is built that way, and it reported PASS
# on both sides of a real defect (the Ahmed 25 degree row's value on frontal
# area and its envelope on planform, a factor of 3.586 apart, 2026-08-01).
# Such a check is still worth running -- it measures whether a hand-rebuilt
# surface has fallen behind its generator -- but it answers a different
# question from the one its PASS line appears to answer, and the reader has no
# way to tell which without reading the source.
#
# So every check declares which of the five it is, what it catches, and what
# it is blind to. The declaration is not a comment: for a GENERATOR check it
# names the symbol shared with the producer and the producer's file, and
# `check_every_check_states_its_basis` verifies that the symbol really does
# appear in both. A coupling that is removed, or one that is added and not
# declared, is then a finding rather than a comment nobody reread.

EVIDENCE = "EVIDENCE"
GENERATOR = "GENERATOR"
PROPERTY = "PROPERTY"
SURFACE = "SURFACE"
TRANSCRIBED = "TRANSCRIBED"
META = "META"

BASIS_MEANING = {
    EVIDENCE: ("re-derives a published number from a primary artifact, by "
               "arithmetic this file performs itself; a defect in the "
               "producing code shows up as a disagreement"),
    GENERATOR: ("compares a published surface against the code that wrote it; "
                "catches drift between the two and is BLIND to any defect "
                "inside the shared code, which both sides carry equally"),
    PROPERTY: ("asserts a property of a record, a surface or a source file; "
               "nothing is re-derived, so there is no shared derivation to "
               "hide in, and equally no number is confirmed"),
    SURFACE: ("compares two published surfaces, or two copies of one file, to "
              "each other; neither is primary evidence for the other"),
    TRANSCRIBED: ("the evidence is typed into this file as a constant; the "
                  "check cannot fail on a wrong value, only on arithmetic "
                  "over its own constants"),
    META: "a check on this file rather than on the lab's records",
}

# name -> (basis, catches, blind_to, shared)
# `shared` is (symbol, file that also uses it) for a GENERATOR check, else None.
BASIS: dict[str, tuple[str, str, str, tuple[str, str] | None]] = {
    "check_ledger_integrity": (
        PROPERTY, "an interrupted write that left a line unparseable",
        "a row that parses and is wrong; nothing here reads the values", None),
    "check_wall_counters_vs_ledger": (
        EVIDENCE,
        "a published counter that no longer sums out of the ledger; the sums "
        "are accumulated in this function, row by row, not obtained from "
        "lab_stats.ledger_summary which built the published block",
        "the DEFINITION of what counts, which was copied here from the "
        "generator by hand (succeeded rows only). If that convention is the "
        "wrong one, both sides are wrong together and this agrees", None),
    "check_ledger_stalls": (
        EVIDENCE,
        "rows whose wall time no per-solver cost mechanism explains, read "
        "straight off the ledger and reported with their timestamps",
        "whether STALL_SECONDS is the right cut; the threshold is declared "
        "here and is not derived from anything", None),
    "check_closure_entry_of_record": (
        EVIDENCE,
        "a wall score that disagrees with the entry file of record, which "
        "this check opens and searches itself",
        "A WRONG NUMBER THAT BOTH FILES AGREE ON. It compares the wall's "
        "score against the entry file and nothing re-derives either from the "
        "predictions, so a scoring error committed to the entry of record "
        "reads here as perfect agreement. It is blind to whether the file it "
        "opens IS the entry of record -- that name is hard-coded here, and "
        "this check once failed the wall for quoting round 5 while it was "
        "itself still pinned to round 3. Its prose guards are keyword "
        "detectors over one JSON string field: a claim reworded past "
        "`_BEST_COUNT`, `_BASELINE_CREDIT` or the single-scoring-call pattern "
        "is not a claim it declines to fault, it is a claim it never saw",
        None),
    "check_rank_claim_surfaces": (
        PROPERTY,
        "a surface that asserts a rank-1 placement for this lab's entry "
        "without P(rank 1), without the CURRENT 95% interval on it -- derived "
        "from sdk/scripts/probability_of_rank_record.json and checked against "
        "the board that record was computed from, never written here -- or "
        "without the literal 'not statistically decided' UNBROKEN on one line "
        "-- "
        "across every tracked file and every member of every archive under "
        "dist/, found by search, so a surface nobody listed is still covered",
        "a rank claim phrased outside its patterns (\"we top the board\"); "
        "anything that does not decode as UTF-8, which is every compiled PDF "
        "in the tree, so a claim living only in a built PDF is invisible "
        "here while its .tex source is not; untracked files; files over 4 MB; "
        "text produced at render time by a generator or a browser; and WHERE "
        "the companion sits -- the companion test is per file, so one "
        "compliant paragraph clears every claim in that file. IT GRADES FORM "
        "AND NOT VALUE, and that limit is now a separate check rather than a "
        "footnote: on 2026-08-15 it opened dist/certonomous-demo.zip, read "
        "line 502 of site/closure.html inside it, recognised the rank claim "
        "and cleared 'rank 1 of 5 ... a seed-uncertainty bound comparable to "
        "its margin' against a board where the placement is 1 of 7 and the "
        "bound is 177% of the margin. See check_rank_claim_values", None),
    "check_rank_claim_values": (
        EVIDENCE,
        "a rank claim whose VALUE the live board contradicts, on any tracked "
        "file or any member of any archive under dist/: a `rank 1 of N` whose "
        "denominator is not the board's own length plus us, a best-on-board "
        "count that is neither the arithmetic count nor the count belonging "
        "to our model after the decline gate, and the word `comparable` "
        "binding the seed bound to the margin when the bound EXCEEDS it. "
        "Every value is derived -- LIVE_BOARD read by AST from "
        "sdk/scripts/probability_of_rank.py, the per-case block from the "
        "entry of record, and the coverage ratio over every admissible margin "
        "basis from scripts/check_derived_figures.py, whose arithmetic and "
        "strike masker are IMPORTED rather than copied. Nothing numeric is "
        "written in this file, so the day the board moves the surfaces that "
        "did not move go red",
        "everything the form guard is blind to, because the board-context and "
        "homonym gates are the same two: phrasing outside _RANK_CLAIM's "
        "vocabulary, anything that is not UTF-8 (every compiled PDF, and "
        "latex/closure_challenge_report.pdf is this corpus's largest single "
        "concentration of withdrawn claims), untracked files, files over 4 MB "
        "and render-time text. Beyond those: a value claim carrying no number "
        "('we lead comfortably'); P(rank 1) itself, MEASURED AND NOT SHIPPED "
        "here for the reason check_derived_figures.py records against the "
        "same quantity -- its hits on this corpus are overwhelmingly correct "
        "dated records; and any wrong figure inside a section whose banner "
        "carries a withdrawal verb AND an ISO date, which is exempt by "
        "construction and is the discriminator that makes the check usable at "
        "all", None),
    "check_board_placement_words": (
        EVIDENCE,
        "an ordinal this lab pins on a leaderboard entrant that disagrees with "
        "the entrant's rank on the published board, the board being parsed "
        "from the benchmark's own README table rather than transcribed here; "
        "and a comparison of ours whose opponent is a placement word instead "
        "of a name (\"our margin over the <position>\"). Matched over whole "
        "text with whitespace collapsed, so a placement a reflow split across "
        "two lines still binds. TWO REFERENTS, and which one answers depends "
        "on the question (D55): the frozen scoring pin binds names to ranks, "
        "and a separate committed, dated record of the live board answers only "
        "HOW MANY POSITIONS EXIST -- a pin that is right for reproducibility "
        "is wrong for standing. The ranking referent is three-valued: if it "
        "cannot be read, the pin answers the standing question too and the "
        "verdict says so, rather than an empty board passing every check "
        "vacuously",
        f"MOST OF ALL, any placement phrased outside this check's "
        f"{_place_family_count()} RULE-A patterns. The three held-out sets "
        f"below are RULE-A sentences, each pinning a wrong placement on a "
        f"named entrant; rule B is measured separately and on a far smaller "
        f"sample. {_place_reach_sentence()}. "
        f"{_place_precision_sentence()}. "
        "Still unreachable: an ordinal as a bare noun, "
        "'are in fourth', #N, a bare parenthetical ordinal, medals, roman "
        "numerals, non-English ordinals, and markdown or CSV rows -- the last "
        "omitted deliberately. This is the "
        "same admission the digit-anchored sibling guard makes about itself "
        "and it belongs here too: a wider anchor is still an anchor. Also: "
        "word forms of board positions past the number-word tables, and any "
        "position past the board's own length plus its margin -- the ordinal "
        "vocabulary is derived from the parsed board rather than fixed at "
        "five, which it was until the first grade caught the literal; "
        "RELATIONAL comparatives -- ahead of, behind, trails, leads, "
        "next-best -- which need both operands resolved and cannot be checked "
        "against one board rank; an entrant referred to by a co-author rather "
        "than the first author on their board row; a wrong ordinal that a "
        "correct one within 400 characters adjudicates away, judged by "
        "proximity and not by grammar; a board surname that is also an "
        "ordinary English word, since surnames match case-insensitively -- "
        "case-sensitive matching was measured to cost one real binding here "
        "and was not taken; the difference between USING a rule-B "
        "phrase and QUOTING one, which rule B cannot make and which is why it "
        "is a WARN on a lab record and a FAIL only where a surface travels; "
        "the travelling set itself, which is matched by BASENAME against the "
        "names packed into shipping archives and submission packages, so a "
        "file merely sharing a name with a packaged one inherits the FAIL "
        "severity -- conservative in direction, still a name collision doing "
        "a provenance check's job; "
        "files over 4 MB, non-UTF-8 surfaces, untracked files and archive "
        "members; whether a placement is dated history rather than a live "
        "claim, which is the other reason rule B is narrow; and -- the same "
        "hazard one level up, for the REFERENT rather than the sentence -- "
        "whether the board it compares against is still the live one. It "
        "reads a deliberately frozen scoring clone and never asks that clone's "
        "age, so if the board has moved it will FAULT a sentence true of the "
        "live board and stay SILENT on one true only of the pin. The frame "
        "line states which commit and which date, generated from the pin "
        "rather than typed here, because a typed pin in a disclosure about "
        "staleness is the defect performing itself", None),
    "check_memory_scaling_law": (
        EVIDENCE,
        "a published power law that does not refit from its own tabulated "
        "measurements; the ordinary least squares is done in this function",
        "the measurements themselves, which are read from the SAME document "
        "that states the law. A mistyped MiB figure refits to the mistyped "
        "law and passes. Nothing here reaches the solver logs those three "
        "numbers came from", None),
    "check_withdrawn_numbers": (
        PROPERTY, "a withdrawn value still present verbatim on a promotional "
                  "surface",
        "the same value written any other way: 0.251 for 0.2510, or a "
        "recomputed near-neighbour", None),
    "check_evidence_paths_exist": (
        PROPERTY, "a repo-rooted citation with no file behind it",
        "a path that exists and holds something other than the evidence "
        "claimed for it", None),
    "check_f2_reproduction": (
        EVIDENCE,
        "a published coefficient that does not match the raw force file, "
        "which this check parses itself; this is the shape the others are "
        "measured against",
        "whether that raw file is the run the record names", None),
    "check_cost_predictions": (
        EVIDENCE,
        "the measured-versus-estimated pairs recorded on the docket, read "
        "from `measured_core_min` on every completed item, each carrying a "
        "`measured_basis` that quotes the sentence in that item's own outcome "
        "the figure came from. Until 2026-08-02 this check read nothing at "
        "all: its whole evidence was three tuples typed into this file",
        "the three per-solver-family pairs that are STILL transcribed here, "
        "and the correctness of a `measured_core_min` field itself, which is "
        "read from an outcome by hand and quoted rather than re-derived from "
        "a solver log", None),
    "check_ungated_completed_runs": (
        PROPERTY,
        "a completed run whose record still carries the not-yet-graded marker",
        "an ungated run whose record does not carry that marker; the check "
        "knows one string on one file", None),
    "check_gate_table_vs_transcripts": (
        GENERATOR,
        "a published row the generator would no longer write: hand-edited, "
        "or resting on a transcript that has stopped supporting it",
        "a misparse inside gate_table.py. The published table is that "
        "generator's own output pasted into markdown, so a transcript read "
        "wrongly is read wrongly on both sides and agrees",
        ("gate_table", "scripts/gate_table.py")),
    "check_wall_credentials_vs_results": (
        GENERATOR,
        "wall.json having fallen behind the builder: a card that would change "
        "if the wall were rebuilt right now. One arm IS independent -- "
        "relative_error is recomputed here from the result file's own "
        "cd_compared and reference_cd",
        "any defect inside displayed_credential, which is the function that "
        "wrote the card. This is the check the finding was filed on: it "
        "reported PASS on both sides of the Ahmed 25 degree area-basis "
        "defect, before the fix and after it",
        ("displayed_credential", "sdk/scripts/build_wall.py")),
    "check_benchmarks_vs_closure_record": (
        EVIDENCE,
        "two things: the published block regressing on the next build (that "
        "half is GENERATOR, against the generator's own _CLOSURE constant), "
        "and our_score disagreeing with the round-3 entry's own harness "
        "result, which this check reads from the scored artifact",
        "a closure field that is not our_score and is wrong in the artifact "
        "and in the constant alike", None),
    "check_fd_grades_current_standard": (
        PROPERTY,
        "a published FD row whose grade word is not the one the current "
        "standard gives for the percentage printed beside it",
        "the percentage itself, which is read off the published row and never "
        "recomputed from FD data. A wrong percentage carrying its own correct "
        "grade passes. And `_fd_grade` restates verification charter section "
        "7 as literals in this file, which is the very shape "
        "check_restated_thresholds calls a defect elsewhere", None),
    "check_statistical_labels": (
        PROPERTY,
        "a caption-printing site with no interval test in it, and a "
        "transcript line claiming an interval with no interval on it",
        "an interval that is present, well-formed and fabricated", None),
    "check_nonconclusive_band_readers": (
        PROPERTY,
        "a function that fits a ladder, reads band_abs and never reads the "
        "conclusiveness flag, by parsing the source",
        "a caller that mentions the flag and ignores it; the test is textual "
        "presence, not use", None),
    "check_channel_totals_use_one_rule": (
        SURFACE,
        "a combined band containing a channel the same act's own table "
        "reports unquantified",
        "whether either the total or the table is right; it only makes them "
        "agree with each other. Already self-declared in its docstring", None),
    "check_declared_fleet_vs_work": (
        PROPERTY,
        "a non-zero worker declaration inside a branch whose condition is a "
        "cache restore",
        "a fleet overstated on a cold path, where the declaration is inside "
        "no branch this check recognises", None),
    "check_restated_thresholds": (
        PROPERTY,
        "a governed threshold restated as a literal default, whether or not "
        "it currently agrees with its source",
        "a threshold this file does not know is governed. _PY_ROOTS now "
        "covers scripts/ and sdk/scripts/ as well, so this file IS scanned, "
        "but GOVERNED_THRESHOLDS names only two constants by parameter name. "
        "_fd_grade restates verification charter section 7 as the literals "
        "15.0 and 5.0 in positional code rather than as a defaulted parameter, "
        "and STALL_SECONDS is declared here with no governed source at all; "
        "neither is reachable by a check keyed on parameter defaults", None),
    "check_register_group_counts": (
        SURFACE,
        "a register group whose declared count disagrees with the headings "
        "under it, in the same file",
        "an entry that is missing from the register altogether; both numbers "
        "come from the register", None),
    "check_campaign_json_citations": (
        PROPERTY, "a machine-readable citation with no file behind it",
        "a citation pointing at a file that exists and is not the evidence",
        None),
    # PROPERTY, corrected 2026-08-15, and the correction is the finding rather
    # than a tidy-up. This entry declared EVIDENCE -- which BASIS_MEANING
    # defines as "re-derives a published number from a primary artifact, by
    # arithmetic this file performs itself" -- two lines above a `blind_to`
    # reading "every VALUE. It compares key sets only". A declaration
    # contradicting itself inside ONE dict entry, shipped on every report, and
    # `check_every_check_states_its_basis` passed it every single run, because
    # that check tests a BASIS string is NON-EMPTY and never that it is TRUE.
    # D174 names it as the standing proof that a declaration nothing verifies
    # is worth nothing.
    #
    # PROPERTY is the honest label and its own meaning says why: "nothing is
    # re-derived, so there is no shared derivation to hide in, and equally NO
    # NUMBER IS CONFIRMED". THE CORRECTION MAKES THE REPORT WORSE, NOT BETTER:
    # the EVIDENCE tally on the verdict line drops from 14 to 13, which is one
    # fewer check in this lab that re-derives a published number than the
    # report has been claiming. That is the point of the column.
    "check_studies_carry_what_the_fit_records": (
        PROPERTY,
        "a record writer that whitelists keys and has dropped a field the fit "
        "learned to emit; the writer and the fit are different code paths, so "
        "the comparison is real -- but it is a comparison of WHICH FIELDS "
        "EXIST, not of what is under them",
        "every VALUE. It compares key sets only. A stale or hand-typed number "
        "under a present key passes -- which is what "
        "check_stored_fits_reproduce_their_values now reads",
        None),
    "check_stored_fits_reproduce_their_values": (
        EVIDENCE,
        "a stored value the study's own rungs no longer produce: a stale "
        "band, a hand-typed verdict, a number from a rung later replaced. The "
        "record writer and the fit are different code paths",
        "a defect inside the fit itself. The same uq module computed the "
        "stored numbers and recomputes them here, so a band computed wrongly "
        "and recomputed the same way agrees. It is also blind to any study "
        "whose method string no current fit reproduces, and those are named "
        "on the report rather than skipped",
        ("eca_hoekstra_band", "sdk/chief_engineer/uq.py")),
    "check_declined_ladders_name_their_guard": (
        SURFACE,
        "a record whose named guard disagrees with its own guard map, and a "
        "decline that records no guard at all",
        "whether the guard map is right. Both fields were written by the same "
        "writer from the same fit, so this asks only that the record agrees "
        "with itself; it never refits to confirm the map", None),
    "check_record_writers_name_their_drops": (
        PROPERTY,
        "the code shape that makes the defect possible: a dict built from one "
        "source by four or more hand-typed keys, where the source arrives as "
        "a parameter so the author cannot see its key set",
        "whether any such writer is actually dropping a field today. The "
        "shape is the precondition, not the defect: a whitelist whose source "
        "has exactly the keys it copies is correct, and nothing static "
        "distinguishes the two. It is also blind to a writer that reads its "
        "source through anything other than .get(literal) or [literal]",
        None),
    "check_stored_rungs_carry_solved_precision": (
        EVIDENCE,
        "a stored ladder whose extrapolated value is decided by the number of "
        "decimals the record kept rather than by what was solved, computed "
        "from the study's own rungs, its own extrapolation and its own band",
        "a rung stored at full precision that is nonetheless the WRONG value, "
        "and any refit that happens outside a stored study -- the wedge case "
        "this encodes lives in a campaign document, not in this corpus, so "
        "the check would not have caught the defect that motivated it. It "
        "guards the corpus going forward and says so", None),
    "check_ladder_rungs_share_one_recipe": (
        EVIDENCE,
        "an observed order fitted across a change of mesh recipe, by reading "
        "the fit triple off the study's own rungs and the comparable family "
        "off its own recipe audit. These are two independent records: the "
        "rungs come from the solves, the family from each rung's meshing "
        "dictionary, and neither is derived from the other",
        "a study with no recipe audit, which it reports as a fault rather "
        "than passing; and the correctness of a recipe audit itself, which is "
        "read off snappyHexMeshDict by hand and not re-derived here", None),
    "check_order_window_declines_state_their_dimensionality": (
        EVIDENCE,
        "a decline that rests on the dimensionality assumption alone, by "
        "refitting the ladder from its own stored rungs at the other dim",
        "a defect inside eca_hoekstra_band, shared with the code that wrote "
        "the stored order. It also prints the STORED order beside a REFIT "
        "one, so the two columns do not come from the same place",
        ("eca_hoekstra_band", "sdk/chief_engineer/uq.py")),
    "check_bundle_drift": (
        SURFACE,
        "a shipped file that is absent from dist/certonomous-demo.zip or "
        "behind the tree, by byte comparison against the TRACKED archive; and "
        "a shipped member it cannot classify, which it reports as UNKNOWN "
        "rather than dropping",
        "whether the tree is right; a defect copied faithfully into the "
        "bundle is a match. Already self-declared in the module docstring. "
        "And 34 of the 90 shipped members, which it names every run rather "
        "than omitting: 2 are derived at build time with no source to compare, "
        "and 32 are copied from gitignored sources, so their comparison would "
        "rest on a reference no clone can reproduce -- it observes those and "
        "does not grade them (D118)",
        None),
    "check_rung_estimates_state_their_iterations": (
        PROPERTY,
        "a rung-shaped compute proposal whose cost_basis names no iteration, "
        "step or sweep count",
        "whether a stated iteration count is the right one, and whether the "
        "estimate built on it is any good", None),
    "check_every_finding_prices_its_remedy": (
        META, "a check that ships without a stated remedy and price",
        "whether a stated price is correct", None),
    "check_every_check_states_its_basis": (
        META,
        "a check that ships without declaring what it tests, and a GENERATOR "
        "declaration naming a coupling that is no longer there",
        "a check that declares EVIDENCE and is in fact coupled through a "
        "symbol it does not name; the declaration is enforced where it is "
        "made, not discovered from scratch. AND, THE LARGER ONE, MEASURED: "
        "whether a BASIS string is TRUE. It tests only that `catches` and "
        "`blind_to` are non-empty, so a declaration contradicting itself "
        "inside one dict entry passes -- which one did, for as long as this "
        "check has existed. check_every_value_claim_names_its_source grades "
        "that half", None),
    "check_every_value_claim_names_its_source": (
        META,
        "a check that CLAIMS to grade value and does not: one that names no "
        "source record, one whose own blind_to disclaims every value, one "
        "declaring basis EVIDENCE while grading form, and -- the rule that "
        "cannot be satisfied by wording -- one whose verdict is IDENTICAL "
        "when the record it names is made unreadable and the check is run "
        "again. It also holds the form column to a symmetric obligation: a "
        "FORM-OVER-VALUE declaration must name the well-formed falsehood that "
        "passes it",
        "WHETHER READING THE NAMED RECORD ANSWERS THE CLAIM. The probe proves "
        "the record is read and that the verdict depends on it; it cannot "
        "prove the check asks the record the right question, so a check "
        "genuinely constrained by a source it grades the wrong property of "
        "passes here. Also blind to a record that is present and WRONG -- "
        "blinding a corrupt source moves the verdict exactly as blinding a "
        "good one does -- and to any check whose named record is absent on "
        "this box, which is reported as UNPROVEN and is the honest verdict "
        "rather than a green. And it cannot see the four kinds themselves: "
        "the CENSUS it prints is a classification by a human of what each "
        "predicate establishes, and a check filed in the wrong column is "
        "caught only where the columns' own rules contradict each other",
        None),
}


# --------------------------------------------------------------------------
# Blind spots that MEASURE THEMSELVES
# --------------------------------------------------------------------------
#
# THE DEFECT THIS EXISTS FOR, and it is this file's own (2026-08-15). Every
# entry in `BASIS` above already carried a blind spot. Thirty of the thirty-four
# never reached the report: the terminal printer emitted `BLIND TO:` only for a
# `GENERATOR`/`TRANSCRIBED` verdict or one naming a shared symbol, so 4 checks
# printed theirs and 30 did not. Measured two ways on 2026-08-15 and both give
# 30 -- by the printer gate (4 print), and by scanning what each `Result`
# itself says (3 print under D34's own ruling, which threw out
# `check_record_writers_name_their_drops` as a false positive because there the
# subject of "cannot see" is the AUDITED function, not the instrument). D34
# published "3 of 34, 31 silent" for the second frame and this reproduces it.
# **A blind spot nobody reads is not a disclosure**, and a declaration that
# exists only to satisfy a guard that reads the dict is a comment with extra
# steps.
#
# THE SECOND DEFECT, which is why this is a table of CALLABLES and not more
# prose. L-79 watched typed figures in this very file go stale within the week,
# and `_board_pin_date` was written precisely so that BLIND TO item 12 could not
# misreport the age of the thing it exists to disclose. A blind spot stating a
# reach -- how many files, which extensions, what threshold -- is a figure, and
# a typed figure rots exactly like a published one. So where the extent of a
# blind spot can be MEASURED, it is measured here at report time, from the same
# state the check itself reads.
#
# name -> callable returning the derived half of that check's blind spot. The
# static half in `BASIS` says WHAT CLASS OF DEFECT is invisible; the callable
# says HOW MUCH is currently invisible. A deriver that raises must not take the
# report down with it -- an instrument that cannot state its own reach says so
# rather than exiting -- so `_derived_blind_spot` catches and reports.


@functools.lru_cache(maxsize=1)
def _corpus_reach() -> dict[str, int]:
    """What the tracked-markdown/UTF-8 frame does and does not contain.

    MEASURED, NEVER TYPED. Every number here is counted off the working tree
    at report time: the moment somebody commits the first PDF, or an act
    transcript is promoted out of `.gitignore`, these move without anybody
    remembering to edit a sentence. The whole point of the table below is that
    the audit's own reach is a figure like any other, and this lab has been
    burned by figures that were true when they were typed.
    """
    reach = {"tracked": 0, "pdf": 0, "over_cap": 0, "not_utf8": 0,
             "untracked": 0, "act_transcripts": 0}
    try:
        listed = subprocess.run(
            ["git", "ls-files", "-z"], cwd=REPO, capture_output=True,
            text=True, check=True).stdout.split("\0")
        ignored = subprocess.run(
            ["git", "ls-files", "-o", "-i", "--exclude-standard", "-z"],
            cwd=REPO, capture_output=True, text=True,
            check=True).stdout.split("\0")
        loose = subprocess.run(
            ["git", "ls-files", "-o", "--exclude-standard", "-z"], cwd=REPO,
            capture_output=True, text=True, check=True).stdout.split("\0")
    except (OSError, subprocess.SubprocessError):
        return reach
    unread = [p for p in ignored + loose if p]
    reach["untracked"] = len(unread)
    reach["act_transcripts"] = sum(
        1 for p in unread
        if p.startswith("mission-output/") and Path(p).stem == "transcript")
    for name in listed:
        if not name:
            continue
        path = REPO / name
        try:
            size = path.stat().st_size
        except OSError:
            continue
        reach["tracked"] += 1
        if path.suffix.lower() == ".pdf":
            reach["pdf"] += 1
        # The cap is READ FROM THE CONSTANT the sweeps actually enforce. Typing
        # "4 MB" here would be a second copy of a threshold, and a second copy
        # is the defect `check_restated_thresholds` exists to catch.
        if size > _RANK_MAX_BYTES:
            reach["over_cap"] += 1
            continue
        try:
            path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            reach["not_utf8"] += 1
        except OSError:
            continue
    return reach


def _blind_corpus() -> str:
    """The reach every corpus-sweeping check shares, counted now."""
    reach = _corpus_reach()
    if not reach["tracked"]:
        return ("the corpus frame could not be enumerated, so this check "
                "cannot state how much of the tree it did not read")
    return (
        f"the frame is TRACKED, UTF-8-DECODABLE files at or under "
        f"{_RANK_MAX_BYTES:,} bytes. Counted now against the working tree: of "
        f"{reach['tracked']:,} tracked files this check's frame excludes "
        f"{reach['pdf']} PDF(s) -- nothing in this file opens a PDF, so a "
        f"claim that exists only in a compiled report is invisible while its "
        f".tex source is not -- {reach['over_cap']} file(s) over the cap and "
        f"{reach['not_utf8']:,} that do not decode as UTF-8. It reads NO "
        f"untracked file: {reach['untracked']:,} of those exist, including "
        f"{reach['act_transcripts']} act transcript(s) under mission-output/, "
        f"which published tables cite as their evidence")


def _blind_stall_threshold() -> str:
    """How far the stall verdict sits from the cut that produced it."""
    # THE SAME SOURCE THE CHECK ITSELF READS. Deriving this sensitivity from
    # any other reader would make the disclosure a claim about a different
    # ledger from the one the verdict was computed on.
    walls = sorted(float(row.get("wall_seconds") or 0.0)
                   for _, row in _iter_ledger() if row is not None)
    below = [w for w in walls if w <= STALL_SECONDS]
    nearest = max(below) if below else None
    near = (f"the nearest row UNDER the cut sits at {nearest:,.0f}s, "
            f"{STALL_SECONDS - nearest:,.0f}s below it"
            if nearest is not None else "no row sits under the cut")
    return (f"whether {STALL_SECONDS:,.0f}s is the right cut. The threshold is "
            f"declared in this file and derived from nothing, and this line "
            f"states the sensitivity rather than asserting there is none: "
            f"{near}, so every row between it and the cut is one the verdict "
            f"calls solver cost purely because of where the constant was put")


def _blind_placement_binding() -> str:
    """Which live entrants the identity binding cannot name.

    DERIVED FROM BOTH BOARDS, never listed. The scoring pin supplies the
    surnames `board_placement_faults` will bind an ordinal to; the ranking
    referent supplies who is actually on the board. Anybody outside the first
    set is unfaultable no matter what a sentence says about them, and on
    2026-08-15 that set includes the board's own leader.
    """
    try:
        board, _ = _published_board()
        ranking = _ranking_board()
    except Exception:                              # noqa: BLE001
        return ("which entrants the identity binding covers could not be "
                "read, so this check cannot state whom it is unable to fault")
    live = dict(ranking[0]) if isinstance(ranking, tuple) else dict(ranking or {})
    # THE EMPTY SET IS NOT AGREEMENT (defect class B1). An unreadable or empty
    # ranking referent makes `unreachable` empty, and the sentence "every live
    # entrant is in the identity binding" is then TRUE AND VACUOUS -- it would
    # read, to anybody, as this check having full coverage at the exact moment
    # it has none. A blind-spot line that under-reports the blind spot when its
    # own evidence goes missing is worse than no line.
    if not live:
        verdict = ("the ranking referent is EMPTY or unreadable, so this check "
                   "cannot say whom it is unable to fault -- and that is NOT "
                   "the same as being able to fault everybody")
    else:
        unreachable = sorted(n for n in live if n not in board)
        leader = sorted((n for n, r in live.items() if r == 1))
        lead = leader[0] if leader else None
        verdict = (
            f"NO sentence about {', '.join(unreachable)} can be faulted by "
            f"rule A: the identity binding is built from the {len(board)}-entry "
            f"scoring pin and those {len(unreachable)} entrant(s) are not in it"
            if unreachable else
            f"all {len(live)} live entrant(s) are in the identity binding")
        if lead and lead in unreachable:
            verdict += (f" -- and {lead} is the board's CURRENT LEADER, so in "
                        f"the shipping configuration this check cannot fault "
                        f"any sentence about the entrant in first place")
    return (f"any placement claim it has no predicate for. It compares an "
            f"ORDINAL against a rank and nothing else: it has NO ARITHMETIC "
            f"predicate, so a false claim about a margin, a percentage or a "
            f"score gap passes it untouched however wrong the number is. And "
            f"{verdict}")


def _blind_best_on_board() -> str:
    """Why the best-on-board pattern cannot cross a line, measured."""
    gap = "[^.\\n]" in _BEST_COUNT.pattern
    try:
        wall = _load_json(WALL)
        entry = str((((wall.get("counters") or {}).get("research") or {})
                     .get("closure") or {}).get("our_entry") or "")
    except Exception:                              # noqa: BLE001
        entry = ""
    shape = (f"its only caller feeds it `our_entry` from the wall, which is "
             f"{len(entry):,} character(s) on {entry.count(chr(10)) + 1} "
             f"line(s)" if entry else
             "its only caller's input could not be read")
    return (f"a best-on-board claim it cannot match. The gap in `_BEST_COUNT` "
            f"is newline-bounded"
            f"{' (`[^.\\n]`)' if gap else ''}, so the pattern CANNOT CROSS A "
            f"LINE BREAK -- and {shape}, which is why that limit has never "
            f"been exercised and would go unnoticed the day the wall's entry "
            f"text is written multi-line. Also blind to whether the file it "
            f"opens is the entry of record; that name is hard-coded here")


BLIND_DERIVED: dict[str, object] = {
    "check_ledger_stalls": _blind_stall_threshold,
    "check_rank_claim_surfaces": _blind_corpus,
    "check_board_placement_words": _blind_placement_binding,
    "check_closure_entry_of_record": _blind_best_on_board,
    "check_evidence_paths_exist": _blind_corpus,
    "check_statistical_labels": _blind_corpus,
    "check_restated_thresholds": _blind_corpus,
    "check_campaign_json_citations": _blind_corpus,
    "check_record_writers_name_their_drops": _blind_corpus,
    "check_declared_fleet_vs_work": _blind_corpus,
}


def _derived_blind_spot(name: str) -> str | None:
    """The measured half of a check's blind spot, or None if it has none.

    A deriver that raises reports the failure IN PLACE OF the measurement. It
    must never take the report down: this whole block exists so the audit can
    state its own reach, and an instrument that cannot state its reach should
    say exactly that rather than exit.
    """
    deriver = BLIND_DERIVED.get(name)
    if deriver is None:
        return None
    try:
        return str(deriver())
    except Exception as exc:                       # noqa: BLE001
        return (f"the extent of this blind spot could not be measured "
                f"({type(exc).__name__}: {exc}); it is not thereby smaller")


def check_every_check_states_its_basis() -> Result:
    """Every check declares what it tests, and a declared coupling is real.

    THE DEFECT. `check_wall_credentials_vs_results` re-derives each credential
    through `lab.displayed_credential`, the same function `build_wall.py` calls
    to write the card. Its PASS means the wall has not drifted from its
    builder. It does not mean the card is right, and it read PASS on both
    sides of the Ahmed 25 degree area-basis defect. Nothing on the report said
    which kind of PASS it was.

    THE CHECK, three parts. Every check in CHECKS carries a BASIS entry and
    every BASIS entry names a live check. Every GENERATOR entry names the
    symbol it shares with the producer, and that symbol must actually appear
    both in this file and in the producer's file -- so a coupling that is
    removed, or a declaration that was never true, is a finding rather than a
    stale comment. And the tally of how many checks are blind to a defect in
    the code they check rides on the verdict line, because that number is the
    honest summary of what this audit can and cannot see.
    """
    names = {check.__name__ for check in CHECKS}
    missing = sorted(n for n in names if n not in BASIS)
    stale = sorted(n for n in BASIS if n not in names)
    problems = [f"{n}: does not declare what it tests" for n in missing]
    problems += [f"{n}: declares a basis and is not a check any more"
                 for n in stale]

    own_text = Path(__file__).read_text(encoding="utf-8", errors="replace")
    for name in sorted(set(BASIS) & names):
        basis, catches, blind, shared = BASIS[name]
        if basis not in BASIS_MEANING:
            problems.append(f"{name}: declares unknown basis {basis!r}")
        if not catches or not blind:
            problems.append(f"{name}: names no catch or no blind spot; a "
                            f"check with no stated blind spot has not been "
                            f"read for one")
        if basis == GENERATOR and not shared:
            problems.append(
                f"{name}: declares GENERATOR and names no shared symbol; the "
                f"whole content of that declaration is which function both "
                f"sides go through")
        if not shared:
            continue
        symbol, producer = shared
        if symbol not in own_text:
            problems.append(
                f"{name}: declares it shares {symbol!r} with {producer}, and "
                f"{symbol!r} does not appear in this file")
        path = REPO / producer
        if not path.exists():
            problems.append(f"{name}: names producer {producer}, which is not "
                            f"on disk")
        elif symbol not in path.read_text(encoding="utf-8", errors="replace"):
            problems.append(
                f"{name}: declares it shares {symbol!r} with {producer}, and "
                f"{producer} no longer mentions it; either the coupling is "
                f"gone and this check is now independent, or it moved")

    counted: dict[str, list[str]] = {}
    for name in sorted(set(BASIS) & names):
        counted.setdefault(BASIS[name][0], []).append(name)
    detail = [f"{basis}: {len(rows)} check(s) -- {BASIS_MEANING[basis]}"
              for basis, rows in sorted(counted.items())
              if basis in BASIS_MEANING]
    coupled = sorted(counted.get(GENERATOR, []) + counted.get(TRANSCRIBED, []))
    detail.append(
        f"{len(coupled)} of {len(names)} check(s) cannot fail on a defect "
        f"inside the code or the constants they check: "
        f"{', '.join(coupled) or 'none'}")
    detail.append(
        f"{len(counted.get(EVIDENCE, []))} check(s) re-derive a published "
        f"number from a primary artifact by arithmetic performed here")
    if problems:
        return Result("every check states its basis", FAIL,
                      f"{len(problems)} declaration(s) are missing or no "
                      f"longer true", problems + detail)
    return Result("every check states its basis", PASS,
                  f"all {len(names)} check(s) declare what they test and "
                  f"every declared coupling is still real", detail)


# --------------------------------------------------------------------------
# FORM OR VALUE, DECLARED -- and the probe that makes the declaration cost
# something (D174, D176)
# --------------------------------------------------------------------------
#
# THE MEASURED FAMILY. A census over CHECKS, read by import, classified every
# check by its PREDICATE -- by what its FAIL establishes, not by what its name
# suggests. At 82fb3d46 that was 17 grading VALUE, 15 grading FORM where the
# claim's failure mode is VALUE, and 2 where form is genuinely the whole
# requirement. `check_rank_claim_values` (847b4492) makes it 18/15/2 here. The
# 15 are not one bug repeated: `check_rung_estimates_state_their_iterations`
# matches `\biterat` and so reads "the iteration count is NOT priced here" as
# the disclosure; `check_record_writers_name_their_drops` is satisfied by the
# bare token `EXCLUDED_KEYS`, so `EXCLUDED_KEYS = ()` -- an empty and therefore
# false declaration -- clears it; and `check_every_check_states_its_basis`
# tests that a BASIS string is NON-EMPTY and never that it is TRUE.
#
# WHY A DECLARATION, AND NOT FIFTEEN REPAIRS. Most of the 15 have no derivable
# value: no source record says whether a `cost_basis` sentence is honest, which
# is why they are form checks in the first place. Deleting them is worse -- a
# form check that SAYS it is a form check is useful, and the defect is a form
# verdict READ AS a value verdict. So the fix is one declared column that makes
# the gap visible and countable on the report, plus the thing that column
# needs to not become the defect itself.
#
# WHICH IS: A DECLARATION THAT NOTHING VERIFIES IS THE VERY DEFECT BEING FIXED.
# `check_every_check_states_its_basis` already proves a non-empty string is
# worth nothing -- `check_studies_carry_what_the_fit_records` declared
# EVIDENCE, which BASIS_MEANING defines as "re-derives a published number from
# a primary artifact", while its own `blind_to` two lines below said "every
# VALUE. It compares key sets only", and that self-contradicting entry passed
# every run. So a VALUE declaration here must PROVE ITSELF, by four rules of
# which the last is executed rather than read:
#
#   NAMED       a VALUE claim names the machine record it grades against.
#   CONSISTENT  it does not declare VALUE while its own blind_to disclaims
#               value, and it does not declare EVIDENCE while grading form.
#   PRESENT     the named record resolves on disk. If it does not, that is a
#               fact about this box and the declaration is UNPROVEN, not false.
#   CONSTRAINS  THE PROBE. The check is run again with the named record made
#               unreadable in process, and its verdict must MOVE. A check whose
#               verdict is the same with its evidence taken away was not using
#               it, and its VALUE declaration is false however well it reads.
#               This is the rule that a forged declaration cannot survive: it
#               costs nothing to type VALUE, and the probe is what it costs.
#
# AND D176'S CLASS, WHICH IS WORSE THAN B AND IS COUNTED SEPARATELY. A check
# can grade value honestly and still emit an ACTIVELY WRONG verdict, when the
# record it grades against is a deliberate PIN rather than the referent the
# claims are about. `check_board_placement_words` binds names to ranks from a
# scoring pin that rung V1 requires frozen. When a repair wrote live-board
# ordinals -- which a chief ruling requires -- rule A went from 0 faults to 14,
# every one of them a CORRECT statement, and three of the fourteen named the
# WRONG ENTRANT, because with two live entrants absent from the pin the subject
# walk falls back to the nearest pinned name. That is not a missed defect, it
# is a manufactured one, in both directions: a claim true of the live board
# faults, and a claim true only of the pin stays silent. Folding it in with the
# form-graders would hide the severity, so it declares VALUE-ON-A-PIN and is
# tallied on its own line.

FORM = "FORM"
FORM_OVER_VALUE = "FORM-OVER-VALUE"
VALUE = "VALUE"
VALUE_ON_A_PIN = "VALUE-ON-A-PIN"

GRADES_MEANING = {
    FORM: ("grades SHAPE, and shape is the whole requirement: there is no "
           "value behind this that could be false while the shape is right"),
    FORM_OVER_VALUE: ("grades SHAPE over a claim whose failure mode is VALUE. "
                      "A well-formed falsehood passes, and this entry names "
                      "one. Its green is a statement about wording"),
    VALUE: ("grades whether a claim is TRUE, against a named machine record "
            "that is the live referent of the claim; proved by the probe"),
    VALUE_ON_A_PIN: ("grades whether a claim is true against a record that is "
                     "deliberately FROZEN and is NOT the referent the claims "
                     "are about, so the error runs both ways and a correct "
                     "claim can be faulted (D176)"),
}

# name -> (kind, evidence).  For VALUE and VALUE-ON-A-PIN the evidence is the
# tuple of repo-relative records the verdict is derived from, and the probe
# below blinds each one in turn. For FORM-OVER-VALUE it is the well-formed
# falsehood that passes -- the obligation is symmetric on purpose, so a check
# cannot dodge into the form column without saying what gets through it.
GRADES: dict[str, tuple[str, object]] = {
    # ---- FORM: shape is genuinely the whole requirement (class C) ----------
    "check_ledger_integrity": (
        FORM, ()),
    "check_restated_thresholds": (
        FORM, ()),

    # ---- VALUE: graded against a live machine record (class A) -------------
    "check_wall_counters_vs_ledger": (
        VALUE, ("demo-output/website/mega-batch/ledger.jsonl",)),
    "check_ledger_stalls": (
        VALUE, ("demo-output/website/mega-batch/ledger.jsonl",)),
    "check_closure_entry_of_record": (
        VALUE, ("demo-output/website/closure_challenge_round5_qcr.json",)),
    "check_rank_claim_values": (
        VALUE, ("sdk/scripts/probability_of_rank.py",
                "scripts/check_derived_figures.py")),
    "check_memory_scaling_law": (
        VALUE, ("demo-output/website/dafoam/ADJOINT_MEMORY_ENVELOPE.md",)),
    "check_f2_reproduction": (
        VALUE, ("demo-output/website/campaign/F2_runs/"
                "primary_M0.8_a1.25_Re6e6/postProcessing/forceCoeffs1/0/"
                "coefficient.dat",)),
    "check_cost_predictions": (
        VALUE, ("demo-output/website/agenda/docket.json",)),
    "check_gate_table_vs_transcripts": (
        VALUE, ("scripts/gate_table.py",)),
    "check_wall_credentials_vs_results": (
        VALUE, ("models/curriculum/results",)),
    "check_benchmarks_vs_closure_record": (
        VALUE, ("sdk/scripts/build_benchmarks.py",)),
    "check_register_group_counts": (
        VALUE, ("demo-output/website/campaign/NOT_PASSING_REGISTER.md",)),
    "check_stored_fits_reproduce_their_values": (
        VALUE, ("models/curriculum/uq-studies", "sdk/chief_engineer/uq.py")),
    "check_stored_rungs_carry_solved_precision": (
        VALUE, ("models/curriculum/uq-studies",)),
    "check_ladder_rungs_share_one_recipe": (
        VALUE, ("models/curriculum/uq-studies",)),
    "check_declined_ladders_name_their_guard": (
        VALUE, ("models/curriculum/uq-studies",)),
    "check_order_window_declines_state_their_dimensionality": (
        VALUE, ("models/curriculum/uq-studies", "sdk/chief_engineer/uq.py")),
    "check_bundle_drift": (
        VALUE, ("dist/certonomous-demo.zip",)),

    # ---- VALUE-ON-A-PIN: right predicate, frozen referent (D176) -----------
    # NOT the in-repo submission README, which is what this entry named first
    # and which the probe rejected within one run: `_parse_published_board`
    # reads the BENCHMARK CLONE, `$CLOSURE_BENCHMARK_DIR` or
    # `~/closure-challenge-benchmark`, and blinding a file the check never
    # opens moved no verdict. That is the probe doing its job on this table's
    # own first draft, which is the argument for having it.
    "check_board_placement_words": (
        VALUE_ON_A_PIN, ("~/closure-challenge-benchmark/README.md",)),

    # ---- FORM-OVER-VALUE: the 15, each naming what gets through it ---------
    "check_rank_claim_surfaces": (
        FORM_OVER_VALUE,
        "a surface carrying P(rank 1), the current interval and the sweep "
        "token, beside `rank 1 of 5` where the live board makes it 1 of 7 and "
        "a seed bound that is 177% of the margin called `comparable` to it. "
        "Read, recognised and cleared on 2026-08-15 at "
        "dist/certonomous-demo.zip!site/closure.html:502 (D145)"),
    "check_rung_estimates_state_their_iterations": (
        FORM_OVER_VALUE,
        "a cost_basis reading `the iteration count is NOT priced here`. "
        "_ITERATION_TERM matches `\\biterat`, so the regex reads the "
        "DISCLAIMER as the DISCLOSURE, and two live docket items clear it "
        "that way"),
    "check_fd_grades_current_standard": (
        FORM_OVER_VALUE,
        "a row whose PRINTED percentage is wrong. The grade WORD is recomputed "
        "from the printed figure; the figure is never recomputed from anything, "
        "so a wrong number correctly graded passes"),
    "check_statistical_labels": (
        FORM_OVER_VALUE,
        "a hand-typed `+/- 0.004` on the line. The interval test is that the "
        "identifier `_looks_like_interval` is TEXTUALLY PRESENT in the printing "
        "file and that a glyph is on the transcript line; neither reads a "
        "procedure's output"),
    "check_nonconclusive_band_readers": (
        FORM_OVER_VALUE,
        "a function whose body contains the substring `conclusive` only inside "
        "a comment saying the flag is ignored"),
    "check_channel_totals_use_one_rule": (
        FORM_OVER_VALUE,
        "an act that mentions `combine_expanded` in a docstring and computes "
        "its total another way; the test is `\"combine_expanded\" in text`"),
    "check_record_writers_name_their_drops": (
        FORM_OVER_VALUE,
        "`EXCLUDED_KEYS = ()` -- an empty, and therefore false, declaration. "
        "The test is membership of a bare token from _DROP_DECLARATIONS, so a "
        "declaration that names nothing satisfies the rule to name what is "
        "dropped"),
    "check_evidence_paths_exist": (
        FORM_OVER_VALUE,
        "a citation pointing at a real file that does not hold the claimed "
        "evidence; `.exists()` is the whole test"),
    "check_campaign_json_citations": (
        FORM_OVER_VALUE,
        "the same: a machine-readable citation resolving to a real file whose "
        "contents have nothing to do with the claim it is cited for"),
    "check_studies_carry_what_the_fit_records": (
        FORM_OVER_VALUE,
        "a stale or hand-typed number under a present key. It compares KEY "
        "SETS only and its own blind_to says so -- the aortic valve's "
        "`conclusive: True` was a typed literal under a correct field name. "
        "check_stored_fits_reproduce_their_values grades the values"),
    "check_declared_fleet_vs_work": (
        FORM_OVER_VALUE,
        "a warm-path branch whose condition word is none of warm, cached or "
        "restore; and a `set_workers(n)` outside an `if` altogether"),
    "check_withdrawn_numbers": (
        FORM_OVER_VALUE,
        "the same withdrawn quantity written to a different number of decimal "
        "places, or any withdrawn value nobody added to the sentinel list; the "
        "test is literal substring membership over a transcribed list"),
    "check_ungated_completed_runs": (
        FORM_OVER_VALUE,
        "a completed run whose record does not carry the literal `PRELIMINARY, "
        "not yet graded`; the marker is the whole detector and the record "
        "writes it by hand"),
    "check_every_check_states_its_basis": (
        FORM_OVER_VALUE,
        "a BASIS string that is non-empty and FALSE. Measured live: "
        "check_studies_carry_what_the_fit_records declared EVIDENCE -- "
        "\"re-derives a published number ... by arithmetic this file performs "
        "itself\" -- while its own blind_to two lines below said \"every VALUE. "
        "It compares key sets only\", a declaration contradicting itself inside "
        "one dict entry, and it PASSED. That is what "
        "check_every_value_claim_names_its_source now catches"),
    "check_every_finding_prices_its_remedy": (
        FORM_OVER_VALUE,
        "a remedy priced wrong, or a remedy that would not clear the finding. "
        "The test is name-membership in REMEDIES and never the price"),
    "check_every_value_claim_names_its_source": (
        FORM_OVER_VALUE,
        "a check that declares VALUE, names a real record, is genuinely "
        "constrained by it -- the probe moves its verdict -- and grades the "
        "WRONG PROPERTY of it. The probe proves the record is READ and that "
        "the verdict depends on it; it cannot prove that reading it answers "
        "the claim. This instrument does not exempt itself from the family it "
        "measures"),
}


# A blind_to that DISCLAIMS VALUE. Matched against the declared blind spot of
# anything claiming to grade value, because those two sentences cannot both be
# true. These are the real spellings in this file's own BASIS table, not
# invented ones -- the first is check_studies_carry_what_the_fit_records', the
# second check_ledger_integrity's, the third PROPERTY's own BASIS_MEANING.
_VALUE_DISCLAIMER = re.compile(
    r"every VALUE|compares KEY SETS only|compares key sets only|"
    r"nothing here reads the values|no number is confirmed|"
    r"cannot fail on a wrong value|nothing is re-derived|"
    r"IT GRADES FORM AND NOT VALUE", re.I)

def _grade_source_path(source: str) -> Path:
    """A declared source as a path on THIS box.

    Repo-relative by default. A `~`-anchored source is a record outside this
    repository, which today is the benchmark clone -- and its root is whatever
    `$CLOSURE_BENCHMARK_DIR` says when that is set, so the declaration has to
    follow the same override the check follows or the probe would blind a file
    the check never opens and report a true declaration false.
    """
    clone = "~/closure-challenge-benchmark/"
    if source.startswith(clone):
        root = Path(os.environ.get(
            _BOARD_DIR_ENV, Path.home() / "closure-challenge-benchmark"))
        return root / source[len(clone):]
    if source.startswith(("~", "/")):
        return Path(source).expanduser()
    return REPO / source


#: Filled by `main()` so the probe below does not pay for a second unblinded
#: run of every check it grades. It is a cache of THIS process's own results,
#: never a substitute for running: an entry that is not here is computed.
_RESULTS_THIS_RUN: dict[str, Result] = {}


class _Blindfold:
    """Make one repo path -- and everything under it -- unreadable, in process.

    Not a mock of the check and not an edit of the tree: five agents share this
    working tree and a probe that writes to it is a probe that corrupts
    somebody else's run. Every read route this file uses is covered: the
    `pathlib.Path` methods, `builtins.open`, and `zipfile.ZipFile`.

    IT ALSO EVICTS THE CACHES, which is the half that is easy to forget and
    without which the probe lies. `_derived_figures` is `lru_cache`d and
    `_uq_module` returns whatever `sys.modules` already holds, so blinding a
    module's FILE changes nothing at all while the module object is still
    loaded -- and the check would then look unconstrained by a record it in
    fact depends on completely. Modules under the blinded path are evicted and
    restored, and every `lru_cache` in this module is cleared on the way in and
    on the way out.
    """

    _METHODS = ("exists", "is_file", "is_dir", "read_text", "read_bytes",
                "open", "stat", "glob", "rglob", "iterdir")

    def __init__(self, target: Path):
        # `os.path` and NOT `Path.resolve()`, here and in `_hidden`. Resolving
        # through pathlib calls `Path.stat`, which is one of the methods this
        # class replaces, and the replacement asks `_hidden` -- so the first
        # version of this recursed until the interpreter gave up. The test at
        # the bottom of the blindfold's suite drives exactly that path.
        self.target = os.path.realpath(str(target))
        self._prefix = self.target + os.sep
        # THE COMPILED COPY, which is the trap this lab has already been bitten
        # by (LESSONS: stale __pycache__ has INVERTED mutation results here).
        # `SourceFileLoader` compares the source's mtime and size through
        # `os.stat` -- which no hook below touches -- and then reads
        # `__pycache__/<stem>.<tag>.pyc`, which does NOT live under the source
        # path. So blinding `uq.py` alone leaves the module loading happily
        # from bytecode, and the probe would report a check unconstrained by a
        # record it depends on entirely.
        head, tail = os.path.split(self.target)
        stem = os.path.splitext(tail)[0]
        self._cache_dir = os.path.join(head, "__pycache__")
        self._cache_stem = stem + "." if tail.endswith(".py") else None

    def _hidden(self, probe) -> bool:
        try:
            resolved = os.path.realpath(os.fspath(probe))
        except (OSError, TypeError, ValueError):
            return False
        if resolved == self.target or resolved.startswith(self._prefix):
            return True
        if self._cache_stem is None:
            return False
        head, tail = os.path.split(resolved)
        return head == self._cache_dir and tail.startswith(self._cache_stem)

    def __enter__(self):
        blind = self._hidden
        target = self.target
        self._saved = {name: getattr(Path, name) for name in self._METHODS}

        def wrap(name, original):
            def method(this, *args, **kwargs):
                if blind(this):
                    if name in ("exists", "is_file", "is_dir"):
                        return False
                    if name in ("glob", "rglob", "iterdir"):
                        return iter(())
                    raise FileNotFoundError(
                        f"[self_audit probe] {this} is blinded")
                out = original(this, *args, **kwargs)
                if name in ("glob", "rglob", "iterdir"):
                    return (p for p in out if not blind(p))
                return out
            return method

        for name, original in self._saved.items():
            setattr(Path, name, wrap(name, original))

        self._open = builtins.open

        def blind_open(file, *args, **kwargs):
            if isinstance(file, (str, os.PathLike)) and blind(file):
                raise FileNotFoundError(f"[self_audit probe] {file} is blinded")
            return self._open(file, *args, **kwargs)

        builtins.open = blind_open
        self._zip = zipfile.ZipFile

        def blind_zip(file, *args, **kwargs):
            if isinstance(file, (str, os.PathLike)) and blind(file):
                raise FileNotFoundError(f"[self_audit probe] {file} is blinded")
            return self._zip(file, *args, **kwargs)

        zipfile.ZipFile = blind_zip

        # THE IMPORT MACHINERY, which none of the hooks above reaches and which
        # five of this file's own VALUE declarations depend on. `import
        # gate_table`, `from chief_engineer import uq` and
        # `spec_from_file_location(... check_derived_figures.py)` all read
        # through `_io.open_code` inside importlib's bootstrap -- not through
        # `builtins.open`, not through `Path.read_text`. The first version of
        # this probe reported all five as unconstrained by records they in fact
        # cannot run without, which is a false accusation and exactly as bad as
        # the false clean it exists to find.
        self._open_code = _io.open_code

        def blind_open_code(path, *args, **kwargs):
            if blind(path):
                raise FileNotFoundError(
                    f"[self_audit probe] {path} is blinded")
            return self._open_code(path, *args, **kwargs)

        _io.open_code = blind_open_code

        self._evicted = {}
        self._detached = []
        for name, module in list(sys.modules.items()):
            origin = getattr(module, "__file__", None)
            if origin and blind(origin):
                self._evicted[name] = sys.modules.pop(name)
                # AND THE ATTRIBUTE ON THE PARENT PACKAGE. Dropping
                # `sys.modules["chief_engineer.uq"]` is not enough: importing a
                # submodule also BINDS it on its package, and `from
                # chief_engineer import uq` takes the attribute without
                # importing anything at all when it is there. Both `uq.py`
                # declarations read as unconstrained until this line existed --
                # the module was never re-read, so blinding its file could not
                # possibly change a verdict.
                package, _, attribute = name.rpartition(".")
                parent = sys.modules.get(package) if package else None
                if parent is not None and hasattr(parent, attribute):
                    self._detached.append(
                        (parent, attribute, getattr(parent, attribute)))
                    delattr(parent, attribute)
        _clear_caches()
        return self

    def __exit__(self, *exc):
        for name, original in self._saved.items():
            setattr(Path, name, original)
        builtins.open = self._open
        zipfile.ZipFile = self._zip
        _io.open_code = self._open_code
        sys.modules.update(self._evicted)
        for parent, attribute, module in self._detached:
            setattr(parent, attribute, module)
        _clear_caches()
        return False


def _clear_caches() -> None:
    """Every lru_cache in this module, emptied. A cached answer computed before
    a source was blinded is an answer about a file the probe is pretending is
    not there."""
    for value in list(globals().values()):
        clear = getattr(value, "cache_clear", None)
        if callable(clear):
            try:
                clear()
            except Exception:                          # noqa: BLE001
                pass


def _verdict_of(check) -> tuple[str, str]:
    """A check's verdict as the pair the probe compares: status and summary.

    The detail list is deliberately NOT compared. Detail carries frames, counts
    and timestamps that move for reasons that have nothing to do with the
    record under test, and a probe that treats any of those as "the verdict
    moved" would clear a declaration it should fail.
    """
    try:
        result = check()
    except Exception as exc:                           # noqa: BLE001
        return ("RAISED", f"{type(exc).__name__}: {exc}")
    return (result.status, result.summary)


def check_every_value_claim_names_its_source() -> Result:
    """A check that claims to grade VALUE proves it against a named record.

    THE DEFECT THIS EXISTS FOR, in one live entry.
    `check_studies_carry_what_the_fit_records` declared basis EVIDENCE, which
    BASIS_MEANING defines as re-deriving a published number by arithmetic this
    file performs itself, while its own `blind_to` two lines below read "every
    VALUE. It compares key sets only". Both halves shipped on every report, the
    contradiction was inside ONE dict entry, and
    `check_every_check_states_its_basis` passed it every time -- because that
    check tests a BASIS string is NON-EMPTY and never that it is TRUE.

    So this one does not test that a declaration exists. It tests that a VALUE
    declaration is true, by four rules, and the last of them is executed:

    1. NAMED. VALUE names the record it grades against; FORM-OVER-VALUE names
       the well-formed falsehood that passes it. Both obligations are real, so
       neither column is the cheap one to sit in.
    2. CONSISTENT. A VALUE claim whose own blind_to disclaims value is a
       contradiction and fails here. So is a check declaring basis EVIDENCE --
       a re-derivation of a number -- while grading form.
    3. PRESENT. The named record resolves on disk, or the declaration is
       UNPROVEN rather than false: an absent artifact is a fact about this box.
    4. CONSTRAINS. THE PROBE, and the reason typing VALUE is not free: each
       named record is made unreadable in process and the check is RUN AGAIN.
       Its verdict must move. A verdict that is identical with the evidence
       taken away was not derived from it.

    AND IT COUNTS RATHER THAN CONGRATULATES. Reclassifying the fifteen
    form-graders would make this green and change nothing on the record, so the
    verdict line carries the census -- how many checks grade value, how many
    grade form over a claim whose failure mode is value, and how many claim
    value without proving it -- on a PASS as loudly as on a FAIL.
    """
    title = "every value claim names its source"
    names = [check.__name__ for check in CHECKS]
    by_name = {check.__name__: check for check in CHECKS}
    known = set(names)

    problems: list[str] = []
    problems += [f"{n}: grades neither form nor value, because it declares "
                 f"nothing" for n in sorted(known - set(GRADES))]
    problems += [f"{n}: declares a grade and is not a check any more"
                 for n in sorted(set(GRADES) - known)]

    census: dict[str, list[str]] = {}
    unproven: list[str] = []
    probed = moved = 0

    for name in sorted(set(GRADES) & known):
        kind, evidence = GRADES[name]
        if kind not in GRADES_MEANING:
            problems.append(f"{name}: declares unknown grade {kind!r}")
            continue
        census.setdefault(kind, []).append(name)
        declared = BASIS.get(name)
        basis, blind = (declared[0], declared[2]) if declared else (None, "")

        if kind == FORM_OVER_VALUE:
            # RULE 1, the form side. A form check that cannot name what gets
            # through it has not been read for one, and its green is worth
            # exactly what its author has not yet checked.
            if not isinstance(evidence, str) or len(evidence.strip()) < 40:
                problems.append(
                    f"{name}: declares FORM-OVER-VALUE and names no "
                    f"well-formed falsehood that passes it; that sentence is "
                    f"the whole content of the declaration")
            continue
        if kind == FORM:
            if evidence:
                problems.append(
                    f"{name}: declares FORM -- shape IS the requirement -- and "
                    f"still names evidence {evidence!r}; if there is a record "
                    f"behind it, the honest grade is VALUE")
            if basis == EVIDENCE:
                problems.append(
                    f"{name}: declares basis EVIDENCE and grade FORM. EVIDENCE "
                    f"means {BASIS_MEANING[EVIDENCE][:60]}..., which is a claim "
                    f"about a number; one of the two declarations is false")
            continue

        # --- VALUE and VALUE-ON-A-PIN from here ----------------------------
        # RULE 2, CONSISTENT.
        if _VALUE_DISCLAIMER.search(blind or ""):
            problems.append(
                f"{name}: declares {kind} and its own blind_to disclaims value "
                f"-- {_VALUE_DISCLAIMER.search(blind).group(0)!r}. A check "
                f"cannot both grade value and be blind to every value; one of "
                f"the two sentences is false and they are two lines apart")
        # RULE 1, NAMED.
        sources = tuple(evidence or ())
        if not sources:
            problems.append(
                f"{name}: claims to grade {kind} and names NO source record. "
                f"An unbacked value claim is the defect this table exists to "
                f"make countable, in the table itself")
            continue

        for source in sources:
            path = _grade_source_path(source)
            # RULE 3, PRESENT.
            if not path.exists():
                unproven.append(
                    f"{name}: names {source}, which is not on this box, so its "
                    f"{kind} declaration could not be probed -- UNPROVEN, not "
                    f"disproved: an absent artifact is a fact about the box")
                continue
            # RULE 4, CONSTRAINS. Executed.
            probed += 1
            before = _RESULTS_THIS_RUN.get(name)
            before = ((before.status, before.summary) if before
                      else _verdict_of(by_name[name]))
            with _Blindfold(path):
                after = _verdict_of(by_name[name])
            if before == after:
                problems.append(
                    f"{name}: declares {kind} against {source}, and its verdict "
                    f"is IDENTICAL with {source} unreadable -- "
                    f"{before[0]} {before[1][:70]!r} both times. The record "
                    f"does not constrain this verdict, so the declaration is "
                    f"false however well it reads")
            else:
                moved += 1

    for name in sorted(set(GRADES) & known):
        kind, _ = GRADES[name]
        declared = BASIS.get(name)
        if declared and declared[0] == EVIDENCE and kind in (FORM,
                                                             FORM_OVER_VALUE):
            problems.append(
                f"{name}: declares basis EVIDENCE and grades {kind}. EVIDENCE "
                f"is itself a claim that a published NUMBER is re-derived here; "
                f"a form-grader declaring it is the false declaration this "
                f"check was written for")

    value_kinds = [n for k in (VALUE, VALUE_ON_A_PIN) for n in census.get(k, [])]
    detail = [f"{kind}: {len(rows)} check(s) -- {GRADES_MEANING[kind]}"
              for kind, rows in sorted(census.items())]
    detail.append(
        f"CENSUS: {len(value_kinds)} of {len(names)} check(s) grade whether a "
        f"claim is TRUE ({len(census.get(VALUE_ON_A_PIN, []))} of them against "
        f"a FROZEN referent, D176); "
        f"{len(census.get(FORM_OVER_VALUE, []))} grade SHAPE over a claim whose "
        f"failure mode is VALUE and each names a well-formed falsehood that "
        f"passes it; {len(census.get(FORM, []))} grade shape where shape is the "
        f"whole requirement")
    detail.append(
        f"PROVED BY EXECUTION: {moved} of {probed} (check, record) pair(s) "
        f"moved their verdict when the named record was made unreadable; "
        f"{len(unproven)} could not be probed on this box")
    detail.append(
        "counted and not congratulated: relabelling the "
        f"{len(census.get(FORM_OVER_VALUE, []))} form-graders as anything else "
        "would make this line shorter and change nothing about what they see, "
        "which is why the line prints on a PASS as well as on a FAIL")
    detail += unproven
    detail += [f"{kind}: {', '.join(sorted(rows))}"
               for kind, rows in sorted(census.items())]

    if problems:
        return Result(title, FAIL,
                      f"{len(problems)} grade declaration(s) are missing, "
                      f"self-contradicting or not backed by the record they "
                      f"name", problems + detail)
    if unproven:
        return Result(title, UNKNOWN,
                      f"{len(unproven)} value declaration(s) name a record "
                      f"that is not on this box and could not be probed; "
                      f"{moved} of {probed} probed pair(s) moved", detail)
    return Result(title, PASS,
                  f"all {len(names)} check(s) declare form or value, every "
                  f"value claim names a record, and all {probed} named "
                  f"record(s) MOVE the verdict when taken away", detail)


# --------------------------------------------------------------------------
# What clearing each finding costs
# --------------------------------------------------------------------------
#
# THE DEFECT THIS EXISTS FOR. This audit reported that eight stored studies
# could only be cleared by re-running them. Seven could be refitted in place
# from rungs already on disk, for nothing. The work sat undone for two days
# because the report priced it as eight solves. **A remedy priced an order of
# magnitude too high is a reason not to do the work**, and a finding that does
# not say what clearing it costs is asking the reader to guess.
#
# Two checks already carried their price per fault (`REMEDY_REFIT` and
# `REMEDY_NO_RUNGS` above, which vary per record). Everything else carried
# none. This table is the rest: one entry per check, `(remedy, needs_compute,
# basis)`, printed under any WARN or FAIL and carried in the JSON output.
#
# `needs_compute` is the honest question, not the comfortable one. It is True
# only when clearing the finding requires a solver to run. Re-deriving a
# published number from an artifact already on disk is arithmetic, however
# many rows it reads.
REMEDIES: dict[str, tuple[str, bool, str]] = {
    "check_ledger_integrity": (
        "the torn row's bytes are gone and nothing re-derives them; record "
        "the loss and keep the count on the report rather than closing it",
        False, "an interrupted write; there is nothing to recompute"),
    "check_wall_counters_vs_ledger": (
        "republish the wall counters from the ledger through the builder that "
        "reads it, sdk/scripts/build_wall.py",
        False, "arithmetic over rows already on disk"),
    "check_ledger_stalls": (
        "publish the cleaned figure beside the gross one and mark the stall "
        "rows in the ledger as host stalls",
        False, "the rows are identified; the fix is a label and a subtraction"),
    "check_closure_entry_of_record": (
        "repoint the wall at the entry file of record",
        False, "both numbers are on disk"),
    "check_rank_claim_surfaces": (
        "add P(rank 1), the current 95% interval on it as reported by "
        "`python3 sdk/scripts/probability_of_rank.py`, and the not-decided "
        "pairs to each named surface, keeping the literal 'not statistically "
        "decided' unbroken on one line; a fault on an archive member clears "
        "by rebuilding the bundle after the tree copy is fixed",
        False, "text on surfaces already on disk"),
    "check_rank_claim_values": (
        "correct the figure on the named surface to the value the live board "
        "supports, strike-and-keep: `rank 1 of N` takes the board's own "
        "length plus us, a best-on-board count takes the derived count with "
        "the decline-gate passthroughs disclosed, and a bound the margin no "
        "longer covers is not `comparable` to it and must say by how much it "
        "exceeds it. A fault on an archive member is NOT cleared by editing "
        "the member: the tree copy it was built from is already correct, and "
        "the remedy is one run of scripts/build_laptop_bundle.py by whoever "
        "owns dist/. Correct dated history is exempt and must NOT be edited",
        False, "every value is already derived on this box; the edit is prose"),
    "check_board_placement_words": (
        "correct the ordinal to the entrant's rank on the published board, or "
        "name the entrant instead of designating them by a position; a "
        "placement word cannot state a wrong placement if it is not there",
        False, "the board is on disk and the edit is to prose"),
    "check_memory_scaling_law": (
        "refit the law from its own stored measurements",
        False, "three measurements, already recorded"),
    "check_withdrawn_numbers": (
        "restore the sentinel, or withdraw the number again and say why",
        False, "an edit to a record"),
    "check_evidence_paths_exist": (
        "restore the cited file, or correct the citation to the file that "
        "carries the evidence",
        False, "deciding which of the two is right needs no run"),
    "check_f2_reproduction": (
        "re-derive the coefficients from the raw force file the record cites",
        False, "the force file is retained; that was L-27's whole point"),
    "check_cost_predictions": (
        "price an unstarted item from the fitted laws in "
        "demo-output/website/mega-batch/COST_SCALING.md, then check it against "
        "the run",
        True, "recording a pair from an outcome already written is a record "
              "edit and needs no solver; extending the record with a NEW pair "
              "needs the run, and the fit it is checked against is done"),
    "check_ungated_completed_runs": (
        "grade the completed run against its pre-stated expectation from the "
        "statistics it already wrote",
        False, "the run finished; the grading reads its output"),
    "check_gate_table_vs_transcripts": (
        "re-derive the verdict from the transcript, or correct the published "
        "verdict to what the transcript supports",
        False, "the transcript is on disk"),
    "check_wall_credentials_vs_results": (
        "rebuild each credential from its own result file through the "
        "builder, and take the downgrades that fall out",
        False, "re-derivation, not re-measurement"),
    "check_benchmarks_vs_closure_record": (
        "regenerate the published block from the scored entry of record",
        False, "both files exist"),
    "check_fd_grades_current_standard": (
        "regrade from the stored FD tables against the current standard",
        False, "the tables are retained"),
    "check_statistical_labels": (
        "correct the caption; no value moves",
        False, "a display-layer edit"),
    "check_nonconclusive_band_readers": (
        "read the non-conclusive flag at the call site that reads the band",
        False, "a code edit"),
    "check_channel_totals_use_one_rule": (
        "make the total match the channel table it is shown beside, either by "
        "quantifying the input channel or by leaving it out of the total; "
        "which way is Katie's call",
        False, "making the two agree is arithmetic. Quantifying the input "
               "channel properly is a sweep and is a separate item"),
    "check_declared_fleet_vs_work": (
        "show no fleet on a path that dispatches nothing, or make the path do "
        "the work it displays; C-3 in PROPOSALS_OPEN.md puts both to Katie",
        False, "the first option is a code edit. The second costs the demo "
               "its warm replay time, which is wall clock on camera rather "
               "than solver cost"),
    "check_restated_thresholds": (
        "read the governed constant instead of restating its value",
        False, "a code edit"),
    "check_register_group_counts": (
        "recount the entries under each heading and correct the declared "
        "totals",
        False, "counting headings in one file"),
    "check_campaign_json_citations": (
        "restore the cited artifact or repoint the citation",
        False, "a record edit"),
    "check_studies_carry_what_the_fit_records": (
        "per fault, and the per-fault price is already printed with it: refit "
        "in place from the rungs the study stores, or, for a record with no "
        "rungs, re-run the ladder or mark the record unverifiable",
        False, "seven of the eight faults this check has ever raised were "
               "refittable in place; only a record storing no rungs needs a "
               "solve, and that case says so on its own line"),
    "check_declined_ladders_name_their_guard": (
        "recompute the guard map from the rungs the study stores, through "
        "uq.study_numerical",
        False, "same rungs, same arithmetic"),
    "check_order_window_declines_state_their_dimensionality": (
        "read the out-of-plane boundary types off the body's own archived "
        "case and record them on the study",
        False, "reading a boundary file and a checkMesh log"),
    "check_rung_estimates_state_their_iterations": (
        "state the iteration count each rung estimate assumes and the evidence "
        "for it, or record that the ladder stores no iterations so the figure "
        "prices the grid alone",
        False, "the settling curves are in the logs those rungs already "
               "wrote; reading them is not a solve"),
    "check_bundle_drift": (
        "rebuild the bundle from the tree WITH --zip so the tracked archive "
        "moves too, then verify by rendering from inside it rather than by "
        "diffing. Rebuilding only dist/certonomous-demo/ leaves the shipped "
        "zip stale and this check will say so",
        False, "a copy, and a render"),
    "check_record_writers_name_their_drops": (
        "at each site, either copy the source's .items() minus a named drop "
        "set, as uq.study_numerical does, or declare the exclusions in a "
        "constant with a reason per key, as lab.CREDENTIAL_NOT_ON_CARD does",
        False, "a code edit per site; no number moves and no run is needed"),
    "check_stored_rungs_carry_solved_precision": (
        "restore the rungs from the artifact the solve wrote, a forces file "
        "or a coefficient file, never a rendered table, and refit in place",
        False, "the solved values are on disk; the refit is arithmetic"),
    "check_ladder_rungs_share_one_recipe": (
        "read the refinement level off each rung's own "
        "system/snappyHexMeshDict and record which rungs share one recipe, as "
        "five studies already do; then either refit on a family that shares "
        "one, or record that this body has no usable ladder and say what it "
        "would need",
        False, "reading a meshing dictionary per rung; the R4 precedent shows "
               "BUILDING a valid family costs 6.2 core-minutes at 4 ranks, "
               "and that is a separate item"),
    "check_stored_fits_reproduce_their_values": (
        "refit the study in place from the rungs it already stores under "
        "levels[], through uq.study_numerical, and write back what the fit "
        "produces; for a record no current fit reproduces, establish which "
        "producer wrote it before touching a number",
        False, "the rungs are on disk; the fit is arithmetic on them"),
    "check_every_check_states_its_basis": (
        "declare in BASIS what the new check tests, what it catches and what "
        "it is blind to; for a GENERATOR check, name the symbol it shares "
        "with the producer",
        False, "reading the check that was just written"),
    "check_every_finding_prices_its_remedy": (
        "add the missing check to REMEDIES with its remedy and whether that "
        "remedy needs compute",
        False, "writing down a price nobody had written down"),
    "check_every_value_claim_names_its_source": (
        "for a missing declaration, add the check to GRADES as FORM, "
        "FORM-OVER-VALUE (naming the well-formed falsehood that passes it) or "
        "VALUE (naming the record it grades against). For a declaration the "
        "PROBE disproved, there is no wording that clears it: either make the "
        "check read the record it names -- so that taking the record away "
        "moves the verdict -- or move the declaration to FORM-OVER-VALUE and "
        "write down what gets through. NO COMPUTE either way; the probe is an "
        "in-process re-run of one check with one path hidden",
        False,
        "the four rules are arithmetic and file reads over records already on "
        "disk; nothing here needs a solver, and the expensive-looking rule -- "
        "re-running a check under a blindfold -- is cheap precisely when the "
        "check is compliant, because a check that depends on a record "
        "short-circuits the moment the record is gone"),
}


def check_every_finding_prices_its_remedy() -> Result:
    """Every check in this file states what clearing its findings costs.

    A finding without a price is a finding the reader has to price, and the
    reader guesses high. This audit has already lost two days that way. So the
    table above is required to cover every check, and a new check that lands
    without an entry fails here rather than shipping a finding nobody can
    weigh.
    """
    missing = [check.__name__ for check in CHECKS
               if check.__name__ not in REMEDIES]
    stale = [name for name in REMEDIES
             if name not in {check.__name__ for check in CHECKS}]
    detail = [f"{name}: no remedy and no price" for name in missing]
    detail += [f"{name}: priced here but is not a check any more"
               for name in stale]
    needs = sorted(name for name, (_, compute, _) in REMEDIES.items()
                   if compute)
    detail.append(f"{len(REMEDIES) - len(needs)} of {len(REMEDIES)} check(s) "
                  f"clear at no compute; the {len(needs)} that need a solver: "
                  f"{', '.join(needs) or 'none'}")
    if missing or stale:
        return Result("every finding prices its remedy", FAIL,
                      f"{len(missing)} check(s) state no remedy and "
                      f"{len(stale)} priced entry(s) name no check", detail)
    return Result("every finding prices its remedy", PASS,
                  f"all {len(CHECKS)} check(s) state what clearing their "
                  f"findings costs", detail)


CHECKS = (
    check_ledger_integrity,
    check_wall_counters_vs_ledger,
    check_ledger_stalls,
    check_closure_entry_of_record,
    check_rank_claim_surfaces,
    check_rank_claim_values,
    check_board_placement_words,
    check_memory_scaling_law,
    check_withdrawn_numbers,
    check_evidence_paths_exist,
    check_f2_reproduction,
    check_cost_predictions,
    check_ungated_completed_runs,
    check_gate_table_vs_transcripts,
    check_wall_credentials_vs_results,
    check_benchmarks_vs_closure_record,
    check_fd_grades_current_standard,
    check_statistical_labels,
    check_nonconclusive_band_readers,
    check_channel_totals_use_one_rule,
    check_declared_fleet_vs_work,
    check_restated_thresholds,
    check_register_group_counts,
    check_campaign_json_citations,
    check_studies_carry_what_the_fit_records,
    check_stored_fits_reproduce_their_values,
    check_stored_rungs_carry_solved_precision,
    check_ladder_rungs_share_one_recipe,
    check_record_writers_name_their_drops,
    check_declined_ladders_name_their_guard,
    check_order_window_declines_state_their_dimensionality,
    check_bundle_drift,
    check_rung_estimates_state_their_iterations,
    check_every_finding_prices_its_remedy,
    check_every_check_states_its_basis,
    # LAST, and it is a real dependency rather than a tidy habit.
    # `check_every_value_claim_names_its_source` reuses this process's own
    # already-computed verdicts as the unblinded half of its probe, so running
    # it after everything else is what keeps the audit from paying for a
    # second full pass. It does not DEPEND on that: any verdict not in
    # `_RESULTS_THIS_RUN` is computed on the spot, so the check is correct
    # standalone and correct if this tuple is ever reordered. Only slower.
    check_every_value_claim_names_its_source,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable results")
    parser.add_argument("--quiet", action="store_true",
                        help="show only WARN and FAIL results")
    args = parser.parse_args()

    results = []
    for check in CHECKS:
        try:
            outcome = check()
        except Exception as exc:  # noqa: BLE001 - a broken check is a finding
            outcome = Result(check.__name__, FAIL,
                             f"check raised {type(exc).__name__}: {exc}")
        results.append(outcome)
        # The unblinded half of check_every_value_claim_names_its_source's
        # probe, recorded as it happens rather than recomputed. See the note
        # on that check in CHECKS.
        _RESULTS_THIS_RUN[check.__name__] = outcome

    priced = []
    for check, result in zip(CHECKS, results):
        entry = REMEDIES.get(check.__name__)
        row = asdict(result)
        if entry:
            remedy, needs_compute, basis = entry
            row["remedy"] = remedy
            row["remedy_needs_compute"] = needs_compute
            row["remedy_basis"] = basis
        declared = BASIS.get(check.__name__)
        if declared:
            tests, catches, blind, shared = declared
            row["tests"] = tests
            row["catches"] = catches
            row["blind_to"] = blind
            # The measured half rides on the JSON as well as the terminal.
            # A hook that reads only `--json` was, until 2026-08-15, the ONLY
            # consumer that saw the thirty unprinted blind spots at all, and
            # the two surfaces must not now disagree about what they say.
            row["blind_to_measured"] = _derived_blind_spot(check.__name__)
            row["shares_with_producer"] = (
                f"{shared[0]} in {shared[1]}" if shared else None)
        priced.append(row)

    if args.json:
        print(json.dumps(priced, indent=1))
    else:
        width = max(len(r.name) for r in results)
        print(f"Certonomous self-audit  ({len(results)} checks)")
        print("=" * (width + 60))
        for check, result in zip(CHECKS, results):
            if args.quiet and result.status in (PASS, INFO):
                continue
            declared = BASIS.get(check.__name__)
            tests = declared[0] if declared else "UNDECLARED"
            print(f"[{result.status:<4}] {result.name:<{width}}  "
                  f"{result.summary}")
            print(f"         tests: {tests}")
            # ON THE VERDICT LINE, NOT ONLY IN THE DICT (D174). BASIS already
            # carried `PROPERTY` for check_rank_claim_surfaces on the day it
            # cleared a false rank claim on a shipped page, and the label did
            # not stop the verdict being quoted as reassurance -- because the
            # label was in a table and the verdict was in the report. So the
            # grade rides beside the status, and a FORM-OVER-VALUE line says
            # what gets through it right there.
            graded = GRADES.get(check.__name__)
            if graded:
                kind, evidence = graded
                if kind in (VALUE, VALUE_ON_A_PIN):
                    print(f"         grades: {kind} against "
                          f"{', '.join(evidence)}")
                elif kind == FORM_OVER_VALUE:
                    print(f"         grades: {kind} -- this verdict is about "
                          f"WORDING, not truth")
                    print(f"         PASSES A WELL-FORMED FALSEHOOD: "
                          f"{evidence}")
                else:
                    print(f"         grades: {kind}")
            else:
                print("         grades: UNDECLARED")
            for line in result.detail:
                print(f"         - {line}")
            # EVERY check states its blind spot, on EVERY status.
            #
            # This used to be gated: `GENERATOR`/`TRANSCRIBED`, or a declared
            # shared symbol. Four checks printed and thirty did not, and the
            # thirty had blind spots all along -- written into BASIS, carried
            # in the JSON, and never once put in front of the person reading
            # the report. A disclosure nobody reads is not a disclosure. The
            # gate was also the wrong shape for its own argument: it justified
            # itself by saying a PASS from a check nobody can FAIL should read
            # as one, which is true, and then inferred that a check which CAN
            # fail has nothing to disclose -- when a PROPERTY check that reads
            # only tracked UTF-8 markdown is blind to every claim in a PDF,
            # and says so, and said so only to the dict.
            if declared:
                print(f"         BLIND TO: {declared[2]}")
                measured = _derived_blind_spot(check.__name__)
                if measured:
                    # MEASURED, not typed. See the BLIND_DERIVED block: a
                    # blind spot that states a reach is stating a figure, and
                    # a typed figure rots.
                    print(f"         BLIND TO (measured now): {measured}")
                if declared[3]:
                    print(f"         shares {declared[3][0]} with "
                          f"{declared[3][1]}")
            entry = REMEDIES.get(check.__name__)
            if entry and result.status in (WARN, FAIL):
                remedy, needs_compute, basis = entry
                price = "NEEDS COMPUTE" if needs_compute else "NO COMPUTE"
                print(f"         remedy ({price}): {remedy}")
                print(f"         remedy basis: {basis}")
        print("=" * (width + 60))
        tally = {s: sum(1 for r in results if r.status == s)
                 for s in (PASS, WARN, FAIL, INFO, UNKNOWN)}
        unaccounted = sorted({r.status for r in results} - set(tally))
        if unaccounted:
            # A status the tally does not name would vanish from the summary
            # line, which is a silent zero in the reporter itself.
            print("  ".join(f"{s}: {sum(1 for r in results if r.status == s)}"
                            f" (UNTALLIED STATUS)" for s in unaccounted))
        print("  ".join(f"{k}: {v}" for k, v in tally.items() if v))
        kinds: dict[str, int] = {}
        for check in CHECKS:
            declared = BASIS.get(check.__name__)
            kinds[declared[0] if declared else "UNDECLARED"] = \
                kinds.get(declared[0] if declared else "UNDECLARED", 0) + 1
        print("what these checks test:  "
              + "  ".join(f"{k}: {v}" for k, v in sorted(kinds.items())))
        # THE CENSUS, printed every run. A number that only a FAIL would show
        # is a number nobody reads on the day it matters, and the point of the
        # declared column is that the gap is COUNTABLE rather than green.
        grades: dict[str, int] = {}
        unbacked = 0
        for check in CHECKS:
            declared = GRADES.get(check.__name__)
            kind = declared[0] if declared else "UNDECLARED"
            grades[kind] = grades.get(kind, 0) + 1
            if declared and declared[0] in (VALUE, VALUE_ON_A_PIN) \
                    and not declared[1]:
                unbacked += 1
        print("what these checks grade: "
              + "  ".join(f"{k}: {v}" for k, v in sorted(grades.items())))
        print(f"  {grades.get(VALUE, 0) + grades.get(VALUE_ON_A_PIN, 0)} of "
              f"{len(CHECKS)} grade whether a claim is TRUE "
              f"({grades.get(VALUE_ON_A_PIN, 0)} of those against a FROZEN "
              f"referent that is not what the claims are about, D176); "
              f"{grades.get(FORM_OVER_VALUE, 0)} grade SHAPE over a claim "
              f"whose failure mode is VALUE; {unbacked} claim VALUE without "
              f"naming a source record")

    # Three-valued exit, 2026-08-15 (D118). 1 on FAIL, 3 on UNKNOWN with no
    # FAIL, 0 otherwise. FAIL outranks UNKNOWN because a definite finding
    # outranks an indefinite one, and 3 is the code `scripts/lab_check.py`'s
    # EXIT_CONTRACT already reads as UNKNOWN, so a detector that turned itself
    # off now reddens the runner instead of exiting 0 beside the passes.
    if any(r.status == FAIL for r in results):
        return 1
    return 3 if any(r.status == UNKNOWN for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
