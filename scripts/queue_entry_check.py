#!/usr/bin/env python3
"""Validate Certonomous run-queue entries. PASSIVE, ON DEMAND, AND IT EXITS.

WHAT THIS IS NOT, STATED FIRST BECAUSE IT IS THE POINT OF THE INSTRUMENT
----------------------------------------------------------------------
This file is **not a scheduler and not a daemon**. It has no service loop, no
timer, no watchdog, no restart logic, and it **never launches a solver or any
other run**. A previous proposal for a self-scheduling launcher was DENIED by
the permission system; that denial stands and is not routed around here. What
exists instead is a *validator*: a human or an agent runs it, it reads queue
entry files, prints one verdict per entry, and returns. Nothing it does can
happen while nobody is watching.

The only child process it ever starts is `git`, and only in a **read-only**
subcommand allowlist enforced by `_git()` -- `cat-file`, `rev-parse`,
`ls-tree`. It never commits, never stages, never touches an index, and the
string `add` is refused by that allowlist rather than by convention.

ENQUEUEING IS NOT AUTHORISATION
-------------------------------
`docs/charters/SUPERVISION_CHARTER.md` section 3 gives each family supervisor
four checks that may never be delegated, the fourth being **pre-registration
committed before compute**. That check happens at ENQUEUE time and is the
supervisor's own. The sha checks below are a **second, mechanical guard --
never a replacement for the personal check**. No entry has been authorised by
virtue of sitting in a queue directory.

INSTRUMENT RULES OBSERVED HERE, EACH PAID FOR BY A MEASURED FAILURE
-------------------------------------------------------------------
* **No `assert` carries a refusal, a guard, a control or a gate (L-332).**
  `python3 -O` and `PYTHONOPTIMIZE=1` delete every assert from the compiled
  code, so a refusal written as one is a refusal *offer* that the runner
  accepts or declines by an interpreter flag they usually do not know they are
  choosing. A cfd guard was measured refusing under `python3` and, under `-O`,
  proceeding to `git add -A` on the shared tree. Every refusal here is a
  `raise` or a `sys.exit(2)`. `--selftest` parses this file's own AST and
  refuses if a single `ast.Assert` node exists.
* **No unconditional success print.** Every `ACCEPTED`, `CONTROL FIRED` and
  `SELFTEST PASS` line is emitted from inside the branch that verified the
  thing it claims, so deleting a check deletes its claim rather than leaving
  the claim behind. A cfd instrument was measured printing "PLANTED CONTROL
  PASSED" and "SELFTEST PASS" under `-O` on an estimator returning zeros.
* **A zero needs a live planted control (standing rule 3).** `--selftest`
  plants one entry per refusal, requires each to fire, and then MUTATES the
  guard and requires the control to flip. A guard that has never been shown
  able to fail is not known to work.

EXIT CODES
----------
    0   every entry validated was accepted (printed per entry, inside the
        accepting branch)
    2   at least one entry was REFUSED, or the selftest failed, or the
        instrument's own AST check failed
    1   usage error

USAGE
-----
    python3 scripts/queue_entry_check.py verification/queue/cfd/*.json
    python3 scripts/queue_entry_check.py --dir verification/queue/cfd
    python3 scripts/queue_entry_check.py --selftest
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TEAMS = (
    "cfd",
    "heat-transfer",
    "ansys-verification",
    "closure",
    "dafoam",
    "verification",
)

# Required fields and the human-readable type each must carry.
REQUIRED_FIELDS = (
    "team",
    "case_id",
    "prereg_commit",
    "prereg_path",
    "launch_cmd",
    "cwd",
    "ranks",
    "cost_core_min_estimate",
    "cost_basis",
    "memory_floor_gb",
    "enqueued_by",
)

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
# An OpenFOAM time directory: 0, 0.1, 250, 1e-05, 2.5e+03.
TIME_DIR = re.compile(r"^[0-9]+(\.[0-9]*)?([eE][+-]?[0-9]+)?$")

# `git` subcommands this instrument may run. READ-ONLY, ENFORCED, NOT ADVISORY.
# The rule-10 catastrophes in this lab all begin with a write subcommand
# reaching a shared tree, so the write subcommands are refused at the one and
# only call site rather than merely avoided by discipline.
GIT_READ_ONLY = frozenset({"cat-file", "rev-parse", "ls-tree"})


class Refusal(Exception):
    """Raised for a condition that must stop the instrument under ANY flag."""


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run one READ-ONLY git subcommand. Refuses anything else.

    Written as an explicit `raise`, never an `assert`: under `python3 -O` an
    assert here would vanish and leave an unguarded passthrough to git.
    """
    if not args:
        raise Refusal("GIT-READ-ONLY: empty git argv")
    if args[0] not in GIT_READ_ONLY:
        raise Refusal(
            f"GIT-READ-ONLY: subcommand {args[0]!r} is not in the read-only "
            f"allowlist {sorted(GIT_READ_ONLY)}. This instrument never writes "
            f"to git -- no commit, no staging, no index, no add in any form."
        )
    return subprocess.run(
        ["git", "-C", str(cwd)] + args,
        capture_output=True, text=True,
    )


def repo_root(start: Path) -> Path:
    out = _git(["rev-parse", "--show-toplevel"], start)
    if out.returncode != 0:
        raise Refusal(f"REPO-ROOT: {start} is not inside a git repository")
    return Path(out.stdout.strip())


# --------------------------------------------------------------------------
# The five checks. Each returns a list of failure strings, each string opening
# with the NAME of the check that failed, so a refusal always names its cause.
# They are registered in CHECKS so --selftest can mutate one at a time.
# --------------------------------------------------------------------------

def check_schema(entry: dict, root: Path) -> list[str]:
    """1. Schema complete, types correct."""
    fail: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in entry:
            fail.append(f"SCHEMA: required field {field!r} is missing")
    if fail:
        return fail

    if entry["team"] not in TEAMS:
        fail.append(f"SCHEMA: team {entry['team']!r} is not one of {list(TEAMS)}")
    for field in ("case_id", "prereg_path", "cost_basis", "enqueued_by"):
        if not isinstance(entry[field], str) or not entry[field].strip():
            fail.append(f"SCHEMA: {field!r} must be a non-empty string")

    if not isinstance(entry["prereg_commit"], str) or not FULL_SHA.match(entry["prereg_commit"]):
        fail.append(
            "SCHEMA: 'prereg_commit' must be a full 40-character lowercase hex "
            "sha. An abbreviated sha is ambiguous and a pre-registration freeze "
            "cannot rest on an ambiguous referent."
        )

    if isinstance(entry.get("prereg_path"), str):
        p = entry["prereg_path"]
        if p.startswith("/") or ".." in Path(p).parts:
            fail.append(
                "SCHEMA: 'prereg_path' is repository-relative and may not be "
                "absolute or contain '..'"
            )

    cmd = entry["launch_cmd"]
    if isinstance(cmd, str):
        fail.append(
            "SCHEMA: 'launch_cmd' is an argv LIST, not a shell string. A shell "
            "string hides word-splitting, globbing and redirection from every "
            "reader of the entry."
        )
    elif not isinstance(cmd, list) or not cmd or not all(isinstance(a, str) for a in cmd):
        fail.append("SCHEMA: 'launch_cmd' must be a non-empty list of strings")

    cwd = entry["cwd"]
    if not isinstance(cwd, str) or not cwd.startswith("/"):
        fail.append("SCHEMA: 'cwd' must be an ABSOLUTE path string")

    # bool is a subclass of int in Python; True would otherwise pass as ranks.
    if isinstance(entry["ranks"], bool) or not isinstance(entry["ranks"], int):
        fail.append("SCHEMA: 'ranks' must be an integer")

    for field in ("cost_core_min_estimate", "memory_floor_gb"):
        v = entry[field]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            fail.append(f"SCHEMA: {field!r} must be a number")
        elif v <= 0:
            fail.append(f"SCHEMA: {field!r} must be > 0, got {v!r}")

    # COMPUTE_BUDGET_CHARTER section 5: this box cannot read its own billing, so
    # any cost figure originating here is derived or reported-by-owner and must
    # SAY SO. A cost silently presented as measured is the shape the charter
    # exists to stop.
    basis = entry.get("cost_basis")
    if isinstance(basis, str):
        low = basis.lower()
        if "not measured" not in low:
            fail.append(
                "SCHEMA: 'cost_basis' must contain the phrase 'not measured' -- "
                "this box cannot read its own billing "
                "(COMPUTE_BUDGET_CHARTER.md section 5)"
            )
        if "derived" not in low and "reported-by-owner" not in low:
            fail.append(
                "SCHEMA: 'cost_basis' must state 'derived' or "
                "'reported-by-owner' as the origin of the figure"
            )
    return fail


def check_commit_exists(entry: dict, root: Path) -> list[str]:
    """2. The pre-registration commit must EXIST."""
    sha = entry.get("prereg_commit")
    if not isinstance(sha, str) or not FULL_SHA.match(sha):
        return []  # already refused by SCHEMA; do not double-report
    out = _git(["cat-file", "-e", f"{sha}^{{commit}}"], root)
    if out.returncode != 0:
        return [
            f"COMMIT-EXISTS: prereg_commit {sha} is not a commit in {root}. "
            f"A freeze cites a sha that exists or it cites nothing."
        ]
    return []


def check_prereg_at_commit(entry: dict, root: Path) -> list[str]:
    """3. The pre-registration must exist AT that commit.

    A sha with no document at it is the laundering shape: a real-looking freeze
    reference that proves nothing, because the document it names was never in
    the tree that the sha fixes.
    """
    sha = entry.get("prereg_commit")
    path = entry.get("prereg_path")
    if not isinstance(sha, str) or not FULL_SHA.match(sha):
        return []
    if not isinstance(path, str) or not path:
        return []
    if _git(["cat-file", "-e", f"{sha}^{{commit}}"], root).returncode != 0:
        return []  # already refused by COMMIT-EXISTS
    out = _git(["cat-file", "-e", f"{sha}:{path}"], root)
    if out.returncode != 0:
        return [
            f"PREREG-AT-COMMIT: {path!r} does not exist at commit {sha}. "
            f"A sha with no document at it is not a pre-registration freeze."
        ]
    return []


def check_age_guard(entry: dict, root: Path) -> list[str]:
    """4. Standing rule 4's age guard, applied BEFORE the launch, not after.

    A run must never be launched into a tree that already holds an answer: the
    completion rule requires every field at endTime to be NEWER than the case's
    own 0/T, and a pre-existing time directory makes that unprovable for the
    run that follows. The directory must also EXIST -- a directory that is not
    there cannot be shown clean, and an argv cannot run in it.
    """
    cwd = entry.get("cwd")
    if not isinstance(cwd, str) or not cwd.startswith("/"):
        return []  # already refused by SCHEMA
    target = Path(cwd)
    if not target.is_dir():
        return [
            f"AGE-GUARD: cwd {cwd} does not exist as a directory, so it cannot "
            f"be shown free of a prior answer."
        ]
    dirty: list[str] = []
    try:
        for child in sorted(target.iterdir()):
            if child.is_dir() and TIME_DIR.match(child.name):
                dirty.append(child.name)
    except OSError as exc:
        return [f"AGE-GUARD: cannot read cwd {cwd}: {exc}"]
    if dirty:
        return [
            f"AGE-GUARD: cwd {cwd} already contains time director"
            f"{'ies' if len(dirty) > 1 else 'y'} {dirty}. Standing rule 4: a "
            f"run is never launched into a tree that already holds an answer."
        ]
    return []


def check_ranks(entry: dict, root: Path) -> list[str]:
    """5. ranks >= 1."""
    r = entry.get("ranks")
    if isinstance(r, bool) or not isinstance(r, int):
        return []  # already refused by SCHEMA
    if r < 1:
        return [f"RANKS: ranks must be >= 1, got {r}"]
    return []


CHECKS: dict[str, object] = {
    "SCHEMA": check_schema,
    "COMMIT-EXISTS": check_commit_exists,
    "PREREG-AT-COMMIT": check_prereg_at_commit,
    "AGE-GUARD": check_age_guard,
    "RANKS": check_ranks,
}


def validate(entry: dict, root: Path, checks: dict | None = None) -> list[str]:
    """Run every registered check. Returns the list of failure strings."""
    active = CHECKS if checks is None else checks
    fail: list[str] = []
    for fn in active.values():
        fail.extend(fn(entry, root))
    return fail


def load_entry(path: Path) -> tuple[dict | None, list[str]]:
    try:
        text = path.read_text()
    except OSError as exc:
        return None, [f"SCHEMA: cannot read {path}: {exc}"]
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, [f"SCHEMA: {path} is not valid JSON: {exc}"]
    if not isinstance(obj, dict):
        return None, [f"SCHEMA: {path} must be a JSON object, got {type(obj).__name__}"]
    return obj, []


# --------------------------------------------------------------------------
# The instrument's check on ITSELF.
# --------------------------------------------------------------------------

def count_assert_nodes(source: str) -> int:
    """Count `assert` statements in a source string. L-332's mechanical half."""
    return sum(1 for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Assert))


def ast_self_check() -> list[str]:
    """Refuse if this file carries a single `assert`."""
    source = Path(__file__).read_text()
    n = count_assert_nodes(source)
    if n:
        return [
            f"AST-NO-ASSERT: this instrument contains {n} `assert` statement(s). "
            f"`python3 -O` deletes every one of them (L-332). A refusal, guard, "
            f"control or gate is a `raise` or a `sys.exit(2)`, never an assert."
        ]
    return []


# --------------------------------------------------------------------------
# Planted controls. Every refusal gets an entry shaped exactly like the failure
# it exists to catch; each must FIRE, and then the guard is MUTATED and the
# control must FLIP. A control that has never been shown able to fail proves
# nothing about the guard behind it.
# --------------------------------------------------------------------------

NONEXISTENT_SHA = "de1e7ed0de1e7ed0de1e7ed0de1e7ed0de1e7ed0"


def _base_entry(sha: str, prereg: str, cwd: str) -> dict:
    return {
        "team": "cfd",
        "case_id": "PLANTED_CONTROL",
        "prereg_commit": sha,
        "prereg_path": prereg,
        "launch_cmd": ["simpleFoam", "-parallel"],
        "cwd": cwd,
        "ranks": 8,
        "cost_core_min_estimate": 240.0,
        "cost_basis": "derived at $0.0513/core-h, reported-by-owner, not measured",
        "memory_floor_gb": 4.0,
        "enqueued_by": "selftest",
    }


def selftest() -> int:
    root = repo_root(Path(__file__).resolve().parent)
    problems: list[str] = []
    lines: list[str] = []

    # --- control 0a: the instrument's own AST carries no assert -------------
    ast_fail = ast_self_check()
    if ast_fail:
        problems.extend(ast_fail)
    else:
        lines.append("AST-NO-ASSERT: zero `assert` nodes in this instrument (L-332).")
    # ...and the AST counter is shown able to see a non-zero, or its zero is
    # not evidence (standing rule 3).
    planted_assert_src = "def f(x):\n    assert x > 0, 'planted'\n    return x\n"
    n_planted = count_assert_nodes(planted_assert_src)
    if n_planted != 1:
        problems.append(
            f"CONTROL FAILED (ast counter): planted source carries 1 assert, "
            f"counter returned {n_planted}. Its zero on this file means nothing."
        )
    else:
        lines.append(
            "CONTROL FIRED (ast counter): counted the 1 planted `assert` in a "
            "synthetic source, so the zero above is a reading, not a blind spot."
        )

    # --- control 0b: the read-only git allowlist refuses a write -----------
    wrote = False
    try:
        _git(["add", "-A"], root)
        wrote = True
    except Refusal as exc:
        lines.append(f"CONTROL FIRED (git allowlist): {exc}")
    if wrote:
        problems.append(
            "CONTROL FAILED (git allowlist): `git add -A` was NOT refused. "
            "This instrument must never write to git in any form."
        )

    # --- enumerate HEAD with ls-tree, and plant a control on the sweep -----
    out = _git(["ls-tree", "-r", "HEAD", "--name-only"], root)
    if out.returncode != 0:
        problems.append("CONTROL FAILED (ls-tree): could not enumerate HEAD")
        tracked: list[str] = []
    else:
        tracked = [l for l in out.stdout.splitlines() if l]
    known = "CLAUDE.md"
    if known not in tracked:
        problems.append(
            f"CONTROL FAILED (ls-tree): {known!r} is not in the enumeration of "
            f"{len(tracked)} paths, so the enumeration is not shown able to see "
            f"a member it must contain."
        )
        live_prereg = None
    else:
        lines.append(
            f"CONTROL FIRED (ls-tree): enumeration of HEAD returned "
            f"{len(tracked)} paths and contains the known member {known!r}."
        )
        live_prereg = known

    head = _git(["rev-parse", "HEAD"], root).stdout.strip()
    if not FULL_SHA.match(head or ""):
        problems.append("CONTROL FAILED: could not resolve HEAD to a full sha")
        return _selftest_verdict(lines, problems)

    with tempfile.TemporaryDirectory() as td:
        clean = Path(td) / "clean_case"
        clean.mkdir()
        (clean / "system").mkdir()
        (clean / "constant").mkdir()

        dirty = Path(td) / "already_answered"
        (dirty / "0").mkdir(parents=True)

        # (name, entry, the check that MUST be the one to refuse it)
        controls = [
            (
                "no prereg_commit",
                {k: v for k, v in _base_entry(head, live_prereg, str(clean)).items()
                 if k != "prereg_commit"},
                "SCHEMA",
            ),
            (
                "well-formed but nonexistent sha",
                _base_entry(NONEXISTENT_SHA, live_prereg, str(clean)),
                "COMMIT-EXISTS",
            ),
            (
                "sha exists, prereg_path absent at it",
                _base_entry(head, "docs/NO_SUCH_PREREGISTRATION_PLANTED.md", str(clean)),
                "PREREG-AT-COMMIT",
            ),
            (
                "cwd already holds 0/",
                _base_entry(head, live_prereg, str(dirty)),
                "AGE-GUARD",
            ),
            (
                "ranks below one",
                {**_base_entry(head, live_prereg, str(clean)), "ranks": 0},
                "RANKS",
            ),
        ]

        for name, entry, owner in controls:
            fails = validate(entry, root)
            fired = [f for f in fails if f.startswith(owner + ":")]
            if not fired:
                problems.append(
                    f"CONTROL FAILED ({name}): expected {owner} to refuse; "
                    f"got {fails or 'NO REFUSAL AT ALL'}"
                )
                continue
            # Mutate the owning guard to a no-op and require the control to FLIP.
            mutated = dict(CHECKS)
            mutated[owner] = lambda e, r: []
            after = [f for f in validate(entry, root, mutated) if f.startswith(owner + ":")]
            if after:
                problems.append(
                    f"CONTROL DID NOT FLIP ({name}): {owner} was mutated to a "
                    f"no-op and the refusal persisted -- it is not coming from "
                    f"the guard it is credited to."
                )
                continue
            lines.append(
                f"CONTROL FIRED ({name}): refused by {owner}, and the refusal "
                f"DISAPPEARED when {owner} was mutated to a no-op."
            )

        # --- the positive control: a valid entry must be ACCEPTED ----------
        valid = _base_entry(head, live_prereg, str(clean))
        fails = validate(valid, root)
        if fails:
            problems.append(
                f"CONTROL FAILED (valid entry): a well-formed entry was refused "
                f"by {fails}. A validator that refuses everything is not a check."
            )
        else:
            lines.append(
                f"CONTROL FIRED (valid entry): accepted, with prereg_commit "
                f"{head[:12]} and prereg_path {live_prereg!r} both verified "
                f"present in git, and cwd {clean} free of any time directory."
            )

    return _selftest_verdict(lines, problems)


def _selftest_verdict(lines: list[str], problems: list[str]) -> int:
    for line in lines:
        print("  " + line)
    if problems:
        # The FAILING branch. No success string is reachable from here.
        print("")
        for p in problems:
            print("  " + p)
        print("")
        print(f"SELFTEST FAILED: {len(problems)} control(s) did not behave.")
        return 2
    # The PASSING branch, and the ONLY place the pass is claimed. Deleting the
    # checks above deletes this claim with them.
    print("")
    print(f"SELFTEST PASS: {len(lines)} controls fired, each shown able to fail.")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Validate queue entries. Passive: reads, prints a verdict per "
            "entry, and exits. Never launches anything."
        )
    )
    ap.add_argument("entries", nargs="*", help="entry .json files to validate")
    ap.add_argument("--dir", help="validate every *.json in this directory")
    ap.add_argument("--selftest", action="store_true",
                    help="run the planted controls and the AST self-check")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    # The AST self-check runs before any verdict is issued: an instrument that
    # carries an assert cannot be trusted to have refused anything.
    ast_fail = ast_self_check()
    if ast_fail:
        for f in ast_fail:
            print("REFUSED (instrument): " + f)
        return 2

    paths: list[Path] = [Path(p) for p in args.entries]
    if args.dir:
        d = Path(args.dir)
        if not d.is_dir():
            print(f"usage: --dir {args.dir} is not a directory")
            return 1
        paths.extend(sorted(d.glob("*.json")))
    if not paths:
        print("No entries given. Nothing to validate; nothing was launched.")
        return 0

    root = repo_root(Path(__file__).resolve().parent)
    refused = 0
    for path in paths:
        entry, fails = load_entry(path)
        if entry is not None:
            fails = validate(entry, root)
        if fails:
            refused += 1
            print(f"REFUSED {path}")
            for f in fails:
                print(f"    {f}")
        else:
            # Printed INSIDE the accepting branch, so no check can be removed
            # without removing this claim.
            print(f"ACCEPTED {path}  team={entry['team']} case={entry['case_id']} "
                  f"ranks={entry['ranks']} est={entry['cost_core_min_estimate']} core-min")
            print("    NOTE: acceptance is a mechanical guard only. Enqueueing is "
                  "not authorisation; SUPERVISION_CHARTER section 3 check 4 is "
                  "the supervisor's own and is not performed by this script.")
    if refused:
        print(f"\n{refused} of {len(paths)} entr{'ies' if len(paths) != 1 else 'y'} REFUSED.")
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        print(f"REFUSED: {exc}")
        sys.exit(2)
