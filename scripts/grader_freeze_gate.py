#!/usr/bin/env python3
"""grader_freeze_gate.py -- STEP (1) of Sanaa's freeze-enforcement wiring order
(SANAA-DIRECT 2026-09-03 ~17:30Z, item 6, verbatim in
etc/sessions/2026-09-03T1730Z_sanaa_mesh_standard_and_freeze_enforcement.md:42-44):

    "(1) the queue daemon refuses to grade any run whose comparator's sha does not
     match its frozen registration -- enforcement at the choke point first,
     primitive is fine"

WHAT THIS FILE IS.  The primitive that answers ONE question about ONE queue entry:
does the comparator this entry names still hash to what its frozen registration
pinned?  It decides; it never moves, writes, launches or grades anything.  Two
callers use it, and only the first can refuse:

  * queue_entry_check.CHECKS["GRADER-FREEZE"] -- the LIVE refusal.  queue_runner.tick()
    calls qec.validate(entry, REPO, path) and routes any non-empty failure list
    straight into move_refused().  That is the daemon's one and only refusal choke
    point and this check now sits in it.
    CITED BY SYMBOL, NOT BY LINE, DELIBERATELY.  Every by-line citation of
    queue_runner.py in this repository that was checked on 2026-09-03 was STALE --
    four records cite `queue_runner.py:223` for list_entries(), which lives at :440,
    an error of 217 lines.  A citation that rots silently is worse than none.
  * queue_runner.launch() -- the RECORD.  Stamps `_grading_freeze` on the launched
    record so step (2) can COUNT coverage off disk instead of re-deriving it.

WHERE THE CHOKE POINT ACTUALLY IS, AND WHY THIS IS NOT A DEAD LIMB.  Measured
2026-09-03, not assumed: scripts/queue_runner.py has NO grading step.  main() loops
on tick(); tick() runs cap_watch() (which reports, never grades) and launch().  Of
the 306 queue entries on disk carrying a launch_cmd, exactly TWO name a grader
(ansys VMFL033-R2 and VMFL076-R2, both `run_vmfl0XX_r2.sh graded`); the other 304
launch a solver and grading happens afterwards, by hand or inside the run script.

So a hook placed at "where the daemon grades" would never fire -- the pathology this
codebase already carries twice (`launcher_rc`: one write, six selftest references,
zero production reads; `cap_watch` retiring on `status.exists()` without ever parsing
it).  THE HONEST CHOKE POINT IS THE LAUNCH, and refusing there is strictly STRONGER
than refusing at grading: a run whose comparator cannot be pinned never burns the
core-minutes in the first place.  What it does NOT cover is stated plainly in
COVERAGE below, because an enforcement claim wider than its mechanism is the failure
this lab keeps paying for.

THE PIN IS DERIVED, NEVER DECLARED.  The entry names only a PATH.  The pinned sha is
read from the entry's own `prereg_commit` -- `git rev-parse <prereg_commit>:<path>`.
A `grader_sha` field stated BY the entry would be self-certifying: whoever drifted the
comparator would write the drifted sha beside it and the gate would pass.  The freeze
commit is already validated to exist (COMMIT-EXISTS) and to hold the pre-registration
(PREREG-AT-COMMIT), so it is the one thing in the row that the row's author cannot
retrofit.  The disk side is hashed in pure Python (git's blob rule, sha1 over
`blob <len>\\0<bytes>`), so this instrument needs no git subcommand beyond the
read-only `rev-parse` that queue_entry_check already allowlists.

INSTRUMENT STATES ARE NOT GATE VERDICTS.  The words below -- PINNED, MISMATCH,
ABSENT-AT-FREEZE, ABSENT-ON-DISK, UNPINNED, UNREGISTERED, MALFORMED -- describe this
instrument's reading of a queue row.  They are deliberately OUTSIDE CLAUDE.md rule 1's
fixed gate vocabulary (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING), which grades physics results and is not this file's to spend.  Nothing here
attaches a verdict to any run.

THE TOLERANT DEFAULT, AND HOW IT STAYS VISIBLE.  An entry with no grading-path field
is UNPINNED and is NOT refused.  That is a deliberate choice with a measured reason:
all 306 entries on disk lack the field, so refusing on absence would refuse the
lab's entire queue on the day it landed -- a brick, not a gate.  But "no field,
therefore grade it anyway" silently reproduces today's state, so UNPINNED is made
COUNTABLE in three places, none of them prose:
    1. `_grading_freeze.verdict` stamped on every launched record (queue_runner.launch);
    2. a `GRADER-FREEZE <case>: UNPINNED` line in verification/queue/runner.log;
    3. `--coverage <queue root>`, which walks the queue and prints
       pinned / eligible as the fraction step (2) reports weekly.
UNPINNED is refusal-ELIGIBLE, not refused: flipping `--strict` (or, later, a ruling
that makes the field required) turns the same reading into a refusal with no change
to what is measured.

THE FIELD NAME IS PROPOSED, NOT SETTLED.  `grading_paths` is this lane's proposal;
the schema field name is an OPEN QUESTION ON THE CHIEF'S DESK (cfd board 47).
GRADING_PATHS_FIELD and GRADING_PATHS_ALIASES below are the single place it is
written down; a ruling renames it there and nowhere else.

USAGE
    python3 scripts/grader_freeze_gate.py <entry.json> [<entry.json> ...]
    python3 scripts/grader_freeze_gate.py --coverage verification/queue
    python3 scripts/grader_freeze_gate.py --selftest
Exit 0 = nothing refused; 2 = at least one entry REFUSED (or the instrument refused
itself).  Rule 4's precedent: refuse, never degrade.

NO `assert` ANYWHERE (L-332): `python3 -O` deletes them, and a gate that vanishes
under a flag is not a gate.  ast_self_check() below enforces that on this file.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

EXIT_REFUSE = 2

# THE PROPOSED SCHEMA FIELD. Name NOT final -- on the chief's desk (cfd board 47).
# A list, because a rung can be graded by more than one comparator, and because a
# scalar that later needs to be a list is a migration nobody performs.
GRADING_PATHS_FIELD = "grading_paths"
# Tolerated spellings, so a ruling that picks another name does not strand rows
# written against this one. Read in order; the first present wins.
GRADING_PATHS_ALIASES = (GRADING_PATHS_FIELD, "grader_paths", "comparator_paths")

FULL_SHA_CHARS = set("0123456789abcdef")

# Sanaa's 2026-08-31 ruling (9154c8ef), already honoured by queue_entry_check: an
# UNREGISTERED feasibility/physics rung is queue-legal with a tag in place of a freeze
# sha, and ITS OUTPUTS ARE NEVER GRADEABLE. Such a row has no freeze to pin against and
# is EXEMPT here -- exempt is not covered, and --coverage counts it in its own column.
UNREGISTERED_PREREG_TAGS = frozenset({"FEASIBILITY", "PHYSICS"})

# States that must stop a launch. Everything else is a reading, not a refusal.
REFUSING_STATES = ("MISMATCH", "ABSENT-AT-FREEZE", "ABSENT-ON-DISK", "MALFORMED")


class Refusal(Exception):
    """A condition that must stop this instrument under ANY flag."""


def is_full_sha(s) -> bool:
    return isinstance(s, str) and len(s) == 40 and set(s) <= FULL_SHA_CHARS


def blob_sha(data: bytes) -> str:
    """git's own blob hash, computed here rather than shelled out.

    `git hash-object` is NOT in queue_entry_check's enforced read-only allowlist
    (GIT_READ_ONLY = {cat-file, rev-parse, ls-tree}), and widening an allowlist whose
    whole purpose is to keep a write subcommand away from a shared tree would be a
    weakening bought for a convenience. sha1 over `blob <len>\\0<bytes>` is the format.
    """
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\0")
    h.update(data)
    return h.hexdigest()


def _git_rev_parse(repo: Path, spec: str) -> str | None:
    """Read-only. Returns the object sha for `<commit>:<path>`, or None if absent.

    `rev-parse` is on queue_entry_check's GIT_READ_ONLY allowlist, so this instrument
    adds no new git capability to the daemon's process.
    """
    try:
        out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify",
                              "--quiet", spec],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    sha = out.stdout.strip()
    return sha if is_full_sha(sha) else None


def declared_paths(entry: dict) -> tuple[list, str | None]:
    """(the declared grading paths, the field name they came from).

    ([], None) when the row declares none -- the tolerant-default case. A field
    present but not a list of non-empty strings is returned AS FOUND so the caller
    can call it MALFORMED; it is never quietly coerced into an empty list, because
    a malformed declaration reading as "no declaration" is how a gate goes silent.
    """
    for name in GRADING_PATHS_ALIASES:
        if name in entry:
            v = entry[name]
            if isinstance(v, str):
                v = [v]
            return (v if isinstance(v, list) else [v]), name
    return [], None


def _normalise(repo: Path, p: str) -> str | None:
    """Repo-relative POSIX path, or None if it escapes the repo."""
    q = Path(p)
    if q.is_absolute():
        try:
            q = q.resolve().relative_to(Path(repo).resolve())
        except ValueError:
            return None
    s = q.as_posix()
    if s.startswith("../") or s == ".." or not s:
        return None
    return s


def grading_freeze_record(entry: dict, repo: Path) -> dict:
    """THE PRIMITIVE. A dict reading of one entry. Never raises on entry content.

    Keys: verdict, detail, field, paths (one row per declared path with `path`,
    `frozen_sha`, `disk_sha`, `state`), prereg_commit, refusal_eligible.
    """
    repo = Path(repo)
    sha = entry.get("prereg_commit")
    case = str(entry.get("case_id", "<no case_id>"))
    paths, field = declared_paths(entry)

    if isinstance(sha, str) and sha in UNREGISTERED_PREREG_TAGS:
        return dict(
            verdict="UNREGISTERED", detail=(
                f"prereg_commit is the {sha!r} tag (Sanaa 2026-08-31, 9154c8ef): this row "
                f"carries NO freeze and its outputs are never gradeable as verdicts, so "
                f"there is nothing for a comparator pin to be checked against. EXEMPT, "
                f"which is not the same as covered."),
            field=field, paths=[], prereg_commit=sha, refusal_eligible=False)

    if not is_full_sha(sha):
        # SCHEMA/COMMIT-EXISTS already refuse this shape; do not double-report.
        return dict(verdict="UNPINNED", detail=(
            "prereg_commit is not a 40-hex sha; the freeze checks upstream own this "
            "row and there is no commit to derive a pin from."),
            field=field, paths=[], prereg_commit=sha, refusal_eligible=False)

    if not paths:
        return dict(verdict="UNPINNED", detail=(
            f"entry declares no {GRADING_PATHS_FIELD!r}: no comparator is named, so the "
            f"sha of the script that will grade case {case} is NOT pinned to freeze "
            f"{sha[:8]} and this launch is NOT covered by freeze enforcement. Tolerated "
            f"by the default policy and COUNTED as uncovered -- it is not a pass."),
            field=field, paths=[], prereg_commit=sha, refusal_eligible=True)

    rows = []
    worst = "PINNED"
    for raw in paths:
        if not isinstance(raw, str) or not raw.strip():
            rows.append(dict(path=repr(raw), frozen_sha=None, disk_sha=None,
                             state="MALFORMED"))
            worst = "MALFORMED"
            continue
        rel = _normalise(repo, raw)
        if rel is None:
            rows.append(dict(path=raw, frozen_sha=None, disk_sha=None,
                             state="MALFORMED"))
            worst = "MALFORMED"
            continue
        frozen = _git_rev_parse(repo, f"{sha}:{rel}")
        disk_p = repo / rel
        try:
            disk = blob_sha(disk_p.read_bytes()) if disk_p.is_file() else None
        except OSError:
            disk = None
        if frozen is None:
            state = "ABSENT-AT-FREEZE"
        elif disk is None:
            state = "ABSENT-ON-DISK"
        elif disk != frozen:
            state = "MISMATCH"
        else:
            state = "PINNED"
        rows.append(dict(path=rel, frozen_sha=frozen, disk_sha=disk, state=state))
        if state != "PINNED" and worst == "PINNED":
            worst = state

    bad = [r for r in rows if r["state"] in REFUSING_STATES]
    if not bad:
        return dict(verdict="PINNED", detail=(
            f"{len(rows)} comparator(s) named by {field!r} hash EXACTLY as commit "
            f"{sha[:8]} froze them."),
            field=field, paths=rows, prereg_commit=sha, refusal_eligible=False)
    return dict(verdict=worst, detail=(
        f"{len(bad)} of {len(rows)} comparator(s) named by {field!r} do NOT match "
        f"freeze {sha[:8]}."),
        field=field, paths=rows, prereg_commit=sha, refusal_eligible=True)


def refusals(entry: dict, repo: Path, strict: bool = False) -> list[str]:
    """The refusal strings for one entry. THE SHAPE queue_entry_check.CHECKS expects.

    Empty list = nothing to refuse. A refusal is returned ONLY for a state in
    REFUSING_STATES -- or, under `strict`, also for UNPINNED. `strict` is OFF on the
    live path today and is the single switch a ruling flips once coverage reaches
    145/145; nothing else changes when it does.
    """
    rec = grading_freeze_record(entry, repo)
    v = rec["verdict"]
    if v in REFUSING_STATES:
        lines = []
        for r in rec["paths"]:
            if r["state"] not in REFUSING_STATES:
                continue
            lines.append(
                f"        {r['path']}: {r['state']} "
                f"frozen={str(r['frozen_sha'])[:12]} disk={str(r['disk_sha'])[:12]}")
        return [
            "GRADER-FREEZE: the comparator named by this entry does not match the "
            f"sha its frozen registration ({rec['prereg_commit']}) pinned.\n"
            + "\n".join(lines)
            + "\n        A run graded by a script that has moved since the freeze cannot "
              "show the gate was not chosen to fit the answer (CLAUDE.md rule 2), so this "
              "run is REFUSED BEFORE it spends core-minutes rather than graded after.\n"
              "        TO CLEAR: commit the comparator, re-freeze the registration at the "
              "new commit, and re-enqueue. Nothing here edits, reverts or stages anything."
        ]
    if strict and v == "UNPINNED":
        return ["GRADER-FREEZE (--strict): " + rec["detail"]]
    return []


# ---------------------------------------------------------------- coverage (step 2's input)
def coverage(root: Path, repo: Path) -> dict:
    """Walk a queue root and count what freeze enforcement DOES and DOES NOT cover.

    This is not step (2) -- verification owns that report. It is the reading that makes
    step (2) sizeable, and it counts off disk so nobody has to take this lane's word.
    """
    root, repo = Path(root), Path(repo)
    tally = {k: 0 for k in ("PINNED", "UNPINNED", "UNREGISTERED", "MISMATCH",
                            "ABSENT-AT-FREEZE", "ABSENT-ON-DISK", "MALFORMED")}
    rows = []
    for p in sorted(root.glob("*/*.json")) + sorted(root.glob("*/launched/*.json")):
        try:
            e = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(e, dict):
            continue
        rec = grading_freeze_record(e, repo)
        tally[rec["verdict"]] = tally.get(rec["verdict"], 0) + 1
        rows.append((str(p), rec["verdict"]))
    eligible = sum(v for k, v in tally.items() if k != "UNREGISTERED")
    return dict(tally=tally, rows=rows, eligible=eligible, pinned=tally["PINNED"],
                total=sum(tally.values()))


# ---------------------------------------------------------------- instrument self-check
def count_assert_nodes(source: str) -> int:
    return sum(1 for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Assert))


def ast_self_check() -> list[str]:
    n = count_assert_nodes(Path(__file__).read_text())
    if n:
        return [f"AST-NO-ASSERT: this instrument carries {n} `assert` statement(s); "
                f"`python3 -O` deletes every one (L-332). A gate is a `raise` or a "
                f"`sys.exit(2)`, never an assert."]
    return []


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("entries", nargs="*")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--coverage", metavar="QUEUE_ROOT")
    ap.add_argument("--strict", action="store_true",
                    help="also REFUSE an entry that names no comparator (UNPINNED). "
                         "OFF on the live path; this is the switch a ruling flips.")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        import grader_freeze_gate_selftest as st  # noqa: E402
        return st.run()

    bad = ast_self_check()
    if bad:
        for b in bad:
            print("REFUSED (instrument): " + b)
        return EXIT_REFUSE

    repo = Path(a.repo)
    if a.coverage:
        cov = coverage(Path(a.coverage), repo)
        print(f"GRADER-FREEZE COVERAGE over {a.coverage} (repo {repo})")
        for k in sorted(cov["tally"]):
            print(f"  {k:18s} {cov['tally'][k]:5d}")
        print(f"  {'-'*24}")
        print(f"  PINNED / ELIGIBLE  {cov['pinned']}/{cov['eligible']}   "
              f"(UNREGISTERED rows are EXEMPT and excluded from the denominator; "
              f"exempt is not covered)")
        return 0

    if not a.entries:
        print("No entries given. Nothing was checked; nothing was refused.")
        return 0

    refused = 0
    for s in a.entries:
        p = Path(s)
        try:
            e = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"REFUSED {p}: cannot read as JSON: {exc}")
            refused += 1
            continue
        if not isinstance(e, dict):
            print(f"REFUSED {p}: not a JSON object")
            refused += 1
            continue
        rec = grading_freeze_record(e, repo)
        fails = refusals(e, repo, strict=a.strict)
        if fails:
            refused += 1
            print(f"REFUSED {p}  [{rec['verdict']}]")
            for f in fails:
                print("    " + f)
        else:
            # printed INSIDE the accepting branch, so the claim cannot outlive the check
            print(f"OK {p}  [{rec['verdict']}] {rec['detail']}")
    if refused:
        print(f"\n{refused} of {len(a.entries)} entr"
              f"{'ies' if len(a.entries) != 1 else 'y'} REFUSED by GRADER-FREEZE.")
        return EXIT_REFUSE
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        print(f"REFUSED: {exc}")
        sys.exit(EXIT_REFUSE)
