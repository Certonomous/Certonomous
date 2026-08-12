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

Exit status is 0 when every check passes, 1 when any check FAILs, so a cron
entry or a CI step can gate on it. The weekly schedule is one line and it is
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
the box and it went 32 commits behind with nothing noticing.

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

import argparse
import ast
import functools
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

PASS, WARN, FAIL, INFO = "PASS", "WARN", "FAIL", "INFO"


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

def check_ledger_integrity() -> Result:
    """Every ledger line parses. A torn line is silent data loss."""
    torn, total = [], 0
    for number, row in _iter_ledger():
        total += 1
        if row is None:
            torn.append(number)
    if not total:
        return Result("ledger integrity", FAIL, "ledger not found or empty")
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
    per_solver: dict[str, list] = {}
    for _, row in _iter_ledger():
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
    for _, row in _iter_ledger():
        if row is None:
            continue
        seconds = float(row.get("wall_seconds") or 0.0)
        if row.get("ok"):
            ok_seconds += seconds
        if seconds > STALL_SECONDS:
            stalls.append((row.get("solver"), seconds, row.get("timestamp")))
    if not stalls:
        return Result("ledger stall contamination", PASS,
                      "no row exceeds the stall threshold")
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


def check_closure_entry_of_record() -> Result:
    """The credentials wall must quote the closure entry of record, not a
    superseded round."""
    wall = _load_json(WALL)
    closure = ((wall.get("counters") or {}).get("research") or {}).get("closure") or {}
    # The entry of record is ROUND 5 since 2026-08-07 (commit 07a7fe9e). This
    # check was pinned to the round-3 file and so failed the wall for being
    # CORRECT: it reported "wall says 0.0566, the entry of record scores 0.0676".
    # Re-pinned by Ladder V Pass 2 (V6/V10, 2026-08-10). When a later round
    # lands, repoint this file and the counts below in the same commit --
    # a guard that cries wolf is worse than no guard, because the cheapest way
    # to silence it is to "fix" the surface that was right.
    entry = _load_json(WEB / "closure_challenge_round5_qcr.json")
    if "__error__" in entry:
        return Result("closure entry of record", WARN,
                      "round-5 entry file not readable; cannot verify the wall")

    published_score = closure.get("our_score")
    published_text = str(closure.get("our_entry") or "")

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
    if re.search(r"\b(three|five) of the eight\b", published_text, re.I):
        problems.append(
            "our_entry quotes a stale best-on-board count; round 5 records "
            "four of eight (the AR_14 tie was lost, priced in writing)")
    if re.search(r"best.{0,60}\bfour of the eight\b", published_text, re.I) \
            and "belongs to the baseline" not in published_text:
        problems.append(
            "our_entry states best-on-board 4 of 8 without the disclosure that "
            "two of those four rows are the organisers' own unmodified RANS "
            "field (SUBMISSION_DRAFT sec 4.7, the highest-priority disclosure)")
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
        if not re.search(r"2\s*[-–]\s*100\s*%", published_text):
            missing.append("its 2-100% at 95% interval")
        if "not statistically decided" not in published_text:
            missing.append("the sweep token 'not statistically decided'")
        if missing:
            problems.append(
                "our_entry makes a rank claim without " + ", ".join(missing)
                + " (Ladder V rung V8 as amended 2026-08-10; source "
                "campaign/PROBABILITY_OF_RANK_2026-08-10.md)")
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
_RANK_INTERVAL = re.compile("2\\s*[-\u2010-\u2015]\\s*100\\s*%")
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
    if not _RANK_INTERVAL.search(text):
        missing.append("its 2-100% at 95% interval")
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
    """
    names: set[str] = set()
    for archive in _shipping_archives():
        try:
            with zipfile.ZipFile(archive) as zf:
                names.update(Path(n).name for n in zf.namelist())
        except (OSError, zipfile.BadZipFile):
            continue
    for package in sorted(WEB.glob("closure_challenge_submission*")):
        if package.is_dir():
            names.update(p.name for p in package.rglob("*") if p.is_file())
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
    internal or external, must carry P(rank 1), its interval (an eight-case
    sample cannot pin it tighter than 2-100% at 95%) and the comparisons that
    are not statistically decided. No surface may state the figure without the
    interval -- a bare 68% is a worse claim than none, because 68% sounds
    settled and eight cases do not support settled.

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
        return Result("rank claims carry their probability", WARN,
                      "could not enumerate tracked files (git unavailable): "
                      "this detector is OFF, not reporting nothing to find")

    travelling = _travelling_names()
    surfaces: list[tuple[str, str, bool]] = []   # (label, text, travels)
    opened = skipped = 0
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
            surfaces.append((f"{archive.relative_to(REPO)} (unreadable: "
                             f"{exc})", "", False))

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
    if shipped_faults:
        return Result("rank claims carry their probability", FAIL,
                      f"{len(shipped_faults)} surface(s) that TRAVEL claim "
                      f"rank 1 without what V8 requires "
                      f"({len(internal_faults)} more on lab records)",
                      shipped_faults + internal_faults + [frame])
    if internal_faults:
        return Result("rank claims carry their probability", WARN,
                      f"every travelling surface complies; "
                      f"{len(internal_faults)} lab record(s) claim rank 1 "
                      f"without what V8 requires", internal_faults + [frame])
    return Result("rank claims carry their probability", PASS,
                  f"all {claiming} surface(s) that claim rank 1 carry the "
                  f"figure, its interval and the not-decided pairs", [frame])


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
_PLACE_OFN = re.compile(r"^\s*of\s+\d", re.I)         # rank 1 of 5: OUR claim,
                                                      # owned by the sibling guard
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
    """RULE B: our comparison, someone else's position, nobody's name.

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


def board_placement_faults(text: str, board: dict[str, int]
                           ) -> tuple[list[str], list[str]]:
    """(rule A faults, rule B faults) for one surface."""
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
        beyond = ("" if n <= len(board) else
                  f" -- and rank {n} is a position this board does not have")
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
        unnamed.append(f"{m.group(0)!r} compares us to a board position "
                       f"without naming who holds it")
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
            disagree, unnamed = board_placement_faults(text, board)
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
    frame = (f"frame: board read from the benchmark's own README table at "
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
             f"a correct rank near a wrong one clears it; and a board surname "
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
    problems, checked = [], []
    for value, reason, surfaces in sentinels:
        for surface in surfaces:
            if not surface.exists():
                continue
            text = surface.read_text(encoding="utf-8", errors="replace")
            checked.append(f"{value} not on {surface.name}")
            if value in text:
                problems.append(
                    f"{value} ({reason}) appears on {surface.name}")
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
    if missing:
        return Result("cited evidence paths", FAIL,
                      f"{len(missing)} of {total} repo-rooted citations do "
                      f"not resolve", missing[:25])
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
    if ladder.exists():
        text = ladder.read_text(encoding="utf-8", errors="replace")
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
    return Result("completed but ungated runs", PASS,
                  "no completed run is missing its gate verdict")


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
    surfaces = [ACTIVE]
    surfaces += sorted(WEB.rglob("*.md"))
    seen, problems, ungraded = set(), [], []
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
            if stated[0] != expected:
                problems.append(
                    f"{where}: graded {stated[0]} at {value}%"
                    f"{' with a sign flip' if sign_flip else ''}; the current "
                    f"standard grades it {expected}. Row reads: {line.strip()}")
    if problems:
        return Result("FD grades vs current standard", FAIL,
                      f"{len(problems)} FD row(s) carry a grade the current "
                      f"standard does not give", problems + ungraded[:5])
    return Result("FD grades vs current standard", PASS,
                  f"no published FD grade disagrees with the current standard",
                  ungraded[:10])


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
    caption = "95% confidence interval"
    for source in sorted(REPO.rglob("certificate.py")):
        if "__pycache__" in source.parts:
            continue
        text = source.read_text(encoding="utf-8", errors="replace")
        if caption not in text:
            continue
        checked += 1
        if "_looks_like_interval" not in text:
            problems.append(
                f"{source.relative_to(REPO)} prints {caption!r} with no "
                f"interval test in the file; every envelope it is handed "
                f"becomes a statistical claim")
    for transcript in sorted(MISSION.glob("*/transcript.*")):
        checked += 1
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
    return Result("statistical labels", PASS,
                  f"{checked} caption site(s) and transcripts carry no "
                  f"unearned confidence interval")


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
    for source in _py_sources():
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
    for source in _py_sources():
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
    for source in _py_sources():
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
    problems, pinned = [], 0
    for source in _py_sources():
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
    return Result("restated thresholds", PASS,
                  f"{pinned} threshold default(s) read the governed constant")


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
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
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
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
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
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
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
    for source in _py_sources():
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
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
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
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
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
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
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
        return Result("order-window declines state their dimensionality", PASS,
                      "no stored ladder is declined on order_window")
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

    for source in sorted(CAMPAIGN.glob("*.json")):
        walk(_load_json(source), "", source.relative_to(REPO))
    if missing:
        return Result("campaign json citations", FAIL,
                      f"{len(missing)} of {total} machine-readable citations "
                      f"do not resolve", missing[:25])
    return Result("campaign json citations", PASS,
                  f"all {total} machine-readable campaign citations resolve")


# The three sets of files the laptop bundle copies VERBATIM out of this tree,
# each as (label, source directory, bundle directory, glob). Everything else in
# the bundle is derived at build time -- the recorded missions, the artifacts
# those recordings point at, and the credentials and lab-stats snapshot, which
# are deliberately computed with the whole repo present because copying their
# small inputs gets them wrong in the direction that CLAIMS MORE. Comparing a
# derived file against the tree would report drift on every build, so this
# check compares only what is supposed to be a copy.
_BUNDLE_VERBATIM = (
    ("control room", Path("sdk/chief_engineer"), Path("sdk/chief_engineer"),
     "**/*"),
    ("launcher", Path("scripts/laptop_bundle"), Path("."), "*"),
)
# The static pages, which move from demo-output/website into site/ and are the
# one set whose bundle path is not its repo path.
_BUNDLE_PAGES = (
    ("closure.html", Path("demo-output/website/closure.html"),
     Path("site/closure.html")),
    ("benchmarks.html", Path("demo-output/website/benchmarks.html"),
     Path("site/benchmarks.html")),
    ("wall.html", Path("demo-output/website/wall/wall.html"),
     Path("site/wall/wall.html")),
)
_BUNDLE_SKIP = ("__pycache__", ".pyc")


def _bundle_pairs() -> list[tuple[str, Path, Path]]:
    """(label, source, bundle) for every file the builder copies verbatim."""
    pairs: list[tuple[str, Path, Path]] = []
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
            pairs.append((label, src, REPO / "dist" / "certonomous-demo"
                          / dst_dir / rel))
    for label, src, dst in _BUNDLE_PAGES:
        if (REPO / src).is_file():
            pairs.append((f"page {label}", REPO / src,
                          REPO / "dist" / "certonomous-demo" / dst))
    return pairs


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
    second is. Only the files the builder copies VERBATIM are compared; the
    recorded missions and the credentials snapshot are derived at build time
    and would report drift on every build if they were included.

    A file missing from the bundle FAILs on its own, per this check's gate: an
    absent module is worse than a stale one, because a stale module still
    answers and an absent one takes a page down with an import error.
    """
    bundle = REPO / "dist" / "certonomous-demo"
    if not bundle.is_dir():
        # FAIL, not WARN (2026-08-10). An absent bundle does not mean "nothing
        # to report" -- it means THIS DETECTOR IS OFF, for the one artifact
        # that leaves this box. The bundle shipped ten days stale while this
        # check named the stale pages by name; the failure mode a missing
        # bundle adds on top is silence read as success, which is the class
        # closed everywhere else in this tree the same day (L-45).
        return Result("bundle drift vs tree", FAIL,
                      "NO BUNDLE at dist/certonomous-demo: the drift detector "
                      "for the shipped artifact is OFF, not merely uninformative",
                      ["nothing is being checked against the tree while this "
                       "directory is absent -- a stale zip beside it would "
                       "report clean",
                       "build it with scripts/build_laptop_bundle.py --zip, or "
                       "record that the lab no longer ships one"])
    pairs = _bundle_pairs()
    if not pairs:
        return Result("bundle drift vs tree", WARN,
                      "found no files the builder copies verbatim; the "
                      "builder's copy list and this check have diverged")
    missing, differs = [], []
    for label, src, dst in pairs:
        rel = src.relative_to(REPO)
        if not dst.is_file():
            missing.append(f"{label}: {rel} is ABSENT from the bundle")
            continue
        if src.read_bytes() != dst.read_bytes():
            differs.append(f"{label}: {rel} differs from the shipped copy")
    stale = [p for _, _, p in pairs]
    extra = []
    for shipped in sorted((bundle / "sdk" / "chief_engineer").rglob("*")):
        if not shipped.is_file() or any(
                part in str(shipped) for part in _BUNDLE_SKIP):
            continue
        if shipped not in stale:
            extra.append(f"control room: {shipped.relative_to(bundle)} is "
                         f"shipped and is not in the tree")
    detail = missing + differs + extra
    if missing or differs:
        return Result("bundle drift vs tree", FAIL,
                      f"{len(missing)} file(s) missing from the bundle and "
                      f"{len(differs)} behind the tree, of {len(pairs)} "
                      f"copied verbatim", detail[:30])
    if extra:
        return Result("bundle drift vs tree", WARN,
                      f"all {len(pairs)} copied file(s) match, and "
                      f"{len(extra)} shipped file(s) no longer exist in the "
                      f"tree", extra[:15])
    return Result("bundle drift vs tree", PASS,
                  f"all {len(pairs)} file(s) the builder copies verbatim "
                  f"match the tree byte for byte")


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
    docket = _load_json(REPO / "demo-output" / "website" / "agenda"
                        / "docket.json")
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
        return Result("rung estimates state their iterations", PASS,
                      "no rung-shaped compute proposal is on the docket")
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
        "whether the file it opens is the entry of record; that name is "
        "hard-coded here", None),
    "check_rank_claim_surfaces": (
        PROPERTY,
        "a surface that asserts a rank-1 placement for this lab's entry "
        "without P(rank 1), without its 2-100% at 95% interval, or without "
        "the literal 'not statistically decided' UNBROKEN on one line -- "
        "across every tracked file and every member of every archive under "
        "dist/, found by search, so a surface nobody listed is still covered",
        "a rank claim phrased outside its patterns (\"we top the board\"); "
        "anything that does not decode as UTF-8, which is every compiled PDF "
        "in the tree, so a claim living only in a built PDF is invisible "
        "here while its .tex source is not; untracked files; files over 4 MB; "
        "text produced at render time by a generator or a browser; and WHERE "
        "the companion sits -- the companion test is per file, so one "
        "compliant paragraph clears every claim in that file", None),
    "check_board_placement_words": (
        EVIDENCE,
        "an ordinal this lab pins on a leaderboard entrant that disagrees with "
        "the entrant's rank on the published board, the board being parsed "
        "from the benchmark's own README table rather than transcribed here; "
        "and a comparison of ours whose opponent is a placement word instead "
        "of a name (\"our margin over the <position>\"). Matched over whole "
        "text with whitespace collapsed, so a placement a reflow split across "
        "two lines still binds",
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
    "check_studies_carry_what_the_fit_records": (
        EVIDENCE,
        "a record writer that whitelists keys and has dropped a field the fit "
        "learned to emit; the writer and the fit are different code paths, so "
        "the comparison is real",
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
        "a shipped file that is absent from the bundle or behind the tree, by "
        "byte comparison",
        "whether the tree is right; a defect copied faithfully into the "
        "bundle is a match. Already self-declared in the module docstring",
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
        "made, not discovered from scratch", None),
}


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
        "add P(rank 1), its 2-100% at 95% interval and the not-decided pairs "
        "to each named surface, keeping the literal 'not statistically "
        "decided' unbroken on one line; a fault on an archive member clears "
        "by rebuilding the bundle after the tree copy is fixed",
        False, "text on surfaces already on disk"),
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
        "rebuild the bundle from the tree and verify by rendering from inside "
        "it rather than by diffing",
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
            results.append(check())
        except Exception as exc:  # noqa: BLE001 - a broken check is a finding
            results.append(Result(check.__name__, FAIL,
                                  f"check raised {type(exc).__name__}: {exc}"))

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
            for line in result.detail:
                print(f"         - {line}")
            # A GENERATOR or TRANSCRIBED verdict states its blind spot on
            # EVERY status, not only on a failure. The point of the
            # declaration is that a PASS from a check nobody can fail should
            # read as one.
            if declared and (declared[0] in (GENERATOR, TRANSCRIBED)
                             or declared[3]):
                print(f"         BLIND TO: {declared[2]}")
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
                 for s in (PASS, WARN, FAIL, INFO)}
        print("  ".join(f"{k}: {v}" for k, v in tally.items() if v))
        kinds: dict[str, int] = {}
        for check in CHECKS:
            declared = BASIS.get(check.__name__)
            kinds[declared[0] if declared else "UNDECLARED"] = \
                kinds.get(declared[0] if declared else "UNDECLARED", 0) + 1
        print("what these checks test:  "
              + "  ".join(f"{k}: {v}" for k, v in sorted(kinds.items())))

    return 1 if any(r.status == FAIL for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
