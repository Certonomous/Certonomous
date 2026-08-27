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
# The seven checks. Each returns a list of failure strings, each string opening
# with the NAME of the check that failed, so a refusal always names its cause.
# They are registered in CHECKS so --selftest can mutate one at a time.
#
# EVERY check takes (entry, root, entry_path). `entry_path` is the path the
# entry was READ FROM, and it is a REQUIRED argument of validate() -- never a
# defaulted one. docs/standards/QUEUE_ENTRY_TEAM_BINDING.md sec.5 P2: a caller
# that cannot supply it must fail LOUDLY, because a check that silently passes
# when its input is missing is a zero from a reader not shown able to see a
# non-zero (standing rule 3). Six of the seven ignore it.
# --------------------------------------------------------------------------


def containing_team_dir(entry_path) -> str | None:
    """The team drop directory an entry FILE sits in, or None when it is not in
    one at all.

    Recognises exactly `.../verification/queue/<team>/<file>.json` for a `<team>`
    in TEAMS -- the same six directories `queue_runner.list_entries()` globs
    (queue_runner.py:387-395). Anything else -- a draft beside its case, a copy
    in a scratch tree, a `held/` subdirectory -- returns None, which is NOT a
    failure: see check_team_binding and binding_note.
    """
    if entry_path is None:
        return None
    parent = Path(entry_path).resolve().parent
    if (parent.name in TEAMS and parent.parent.name == "queue"
            and parent.parent.parent.name == "verification"):
        return parent.name
    return None

def check_schema(entry: dict, root: Path, entry_path=None) -> list[str]:
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


def check_commit_exists(entry: dict, root: Path, entry_path=None) -> list[str]:
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


def check_prereg_at_commit(entry: dict, root: Path, entry_path=None) -> list[str]:
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


def check_age_guard(entry: dict, root: Path, entry_path=None) -> list[str]:
    """4. Standing rule 4's age guard, applied BEFORE the launch, not after.

    A run must never be launched into a tree that already holds an answer: the
    completion rule requires every field at endTime to be NEWER than the case's
    own 0/T, and a pre-existing time directory makes that unprovable for the
    run that follows.

    R-AGE-CWD (docs/standards/QUEUE_ENTRY_VALIDATOR_RULINGS.md, 2026-08-27,
    cfd-supervisor on Sanaa's section 1(b) delegation): THIS CLAUSE APPLIES
    ONLY TO A cwd THAT EXISTS. The previous text here claimed an absent
    directory "cannot be shown free of a prior answer"; that stated the
    opposite of the truth. An absent directory is the STRONGEST available
    proof that it holds no prior answer, and it is how CLAUDE.md rule 2's
    pre-compute condition is proven everywhere else in this lab -- name the
    run directory that does not exist. Absence therefore returns CLEAN from
    this clause. The real and separate problem with an absent cwd is that it
    cannot be EXECUTED in; that is check_cwd_launchable() below, refusing
    under its own word EXEC. Neither half is loosened: the refusal is
    re-labelled and correctly attributed, not removed.
    """
    cwd = entry.get("cwd")
    if not isinstance(cwd, str) or not cwd.startswith("/"):
        return []  # already refused by SCHEMA
    target = Path(cwd)
    if not target.is_dir():
        # R-AGE-CWD ruling clause 1. Absence is EXEC's finding, never this
        # clause's. Not a silent pass: check_cwd_launchable refuses it below.
        return []
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


def check_cwd_launchable(entry: dict, root: Path, entry_path=None) -> list[str]:
    """5. R-AGE-CWD clause 2: an absent cwd cannot be EXECUTED in.

    This is a launchability finding, not an age finding, and it carries its own
    word so a reader is never sent hunting for a rule-4 problem that does not
    exist. It is kept -- ansys's premise was right and its remedy was wrong --
    because deleting it would let an entry be ACCEPTED that cannot launch at
    all. Measured, not recalled: scripts/queue_runner.py:286 builds
    `cd '<cwd>' && <argv>` and :293 calls Popen(..., cwd=str(cwd)); Popen with
    an absent cwd raises FileNotFoundError [Errno 2] and `bash -c "cd
    <absent>"` returns rc 1. The runner writes its LAUNCHED record FIRST, so
    accepting such an entry converts a filing-time refusal into a launch-time
    death behind a stale LAUNCHED record -- exactly the class L-344 exists to
    kill. Refusing at filing time is strictly better.
    """
    cwd = entry.get("cwd")
    if not isinstance(cwd, str) or not cwd.startswith("/"):
        return []  # already refused by SCHEMA
    if Path(cwd).is_dir():
        return []
    return [
        f"EXEC: cwd {cwd} does not exist; queue_runner.py chdirs into it "
        f"(:286) and Popen(cwd=) raises FileNotFoundError (:293), so this "
        f"entry would be recorded LAUNCHED and die. Fix: name an existing "
        f"directory as cwd -- the CASE directory is the lab convention -- or "
        f"mkdir -p it before filing."
    ]


def check_ranks(entry: dict, root: Path, entry_path=None) -> list[str]:
    """6. ranks >= 1."""
    r = entry.get("ranks")
    if isinstance(r, bool) or not isinstance(r, int):
        return []  # already refused by SCHEMA
    if r < 1:
        return [f"RANKS: ranks must be >= 1, got {r}"]
    return []


def check_team_binding(entry: dict, root: Path, entry_path=None) -> list[str]:
    """7. TEAM-BINDING -- an entry's `team` MUST equal the team directory it sits
    in. Specified BEFORE this code existed:
    docs/standards/QUEUE_ENTRY_TEAM_BINDING.md, frozen b23b5638 (amended
    2026-08-27, v1.1).

    WHY. scripts/queue_runner.py does not read `team` when deciding what to
    launch: list_entries() at :387-395 iterates BY DIRECTORY, and tick() carries
    that directory's name into the round-robin cursor, the LAUNCH_LOG.tsv row and
    the <team>/launched/ destination. check_schema only asks whether `team` is one
    of the six, never WHICH one. So an entry declaring one team while sitting in
    another's drop path launches and is recorded as the DIRECTORY's -- corrupting
    verdict ownership and per-team queue depth, and a metric that can be silently
    wrong is worse than one that is absent.

    THIS CLAUSE REFUSES EXACTLY ONE THING: an entry that contradicts its OWN
    declared `team` field. It reads no other field, consults nothing outside the
    file's own path, and has no other way to return a failure.

    Two non-refusals, both deliberate:
      * `team` missing or out of roster -> [] . That is SCHEMA's refusal
        (:154-155) and must not be reported twice (spec sec.5 P3).
      * the file is not in a team drop directory -> [] . An UNCHECKED condition,
        not a satisfied one; binding_note() reports it as NOT CHECKED, and
        --require-binding turns it into a refusal. Refusing here would force every
        lane to copy into the drop path BEFORE validating -- i.e. to validate only
        once the launch is already armed -- inverting the safe order and
        contradicting check-4-before-the-drop (spec sec.5 P6, cfd-supervisor
        2026-08-27).
    """
    team = entry.get("team")
    if not isinstance(team, str) or team not in TEAMS:
        return []
    where = containing_team_dir(entry_path)
    if where is None or where == team:
        return []
    return [
        f"TEAM-BINDING: entry declares team {team!r} but sits in "
        f"verification/queue/{where}/. The runner launches BY DIRECTORY "
        f"(queue_runner.py:387-395) and would record this run as {where!r}'s, so "
        f"the entry contradicts itself. Fix: set team to {where!r}, or move the "
        f"file to verification/queue/{team}/."
    ]


CHECKS: dict[str, object] = {
    "SCHEMA": check_schema,
    "COMMIT-EXISTS": check_commit_exists,
    "PREREG-AT-COMMIT": check_prereg_at_commit,
    "AGE-GUARD": check_age_guard,
    "EXEC": check_cwd_launchable,
    "RANKS": check_ranks,
    "TEAM-BINDING": check_team_binding,
}


def require_binding_clause(entry: dict, entry_path) -> list[str]:
    """--require-binding ONLY. Module-level and named so --selftest can replace it
    via globals() and show control C11 flip (the same shape queue_runner.py uses
    for its GPU clause). Returns a refusal ONLY when the file is not in a team
    drop directory; it can refuse for no other reason."""
    if containing_team_dir(entry_path) is not None:
        return []
    return [
        f"REQUIRE-BINDING: --require-binding was given and {entry_path} is not in "
        f"verification/queue/<team>/, so TEAM-BINDING could NOT be checked. This "
        f"refusal is the ABSENCE of a check, not a failed one. Validate the QUEUED "
        f"copy in place -- that is the validation that counts."
    ]


def binding_note(entry: dict, entry_path) -> str:
    """One line for a bound entry; a block for an unbound one.

    The two are deliberately DIFFERENT SHAPES. `NOT BOUND` would describe the
    entry's state; `NOT CHECKED` describes the limit of our knowledge, and the
    planted-zero principle is about knowledge (cfd-supervisor, 2026-08-27,
    adopting the lane's wording over his own)."""
    where = containing_team_dir(entry_path)
    if where is not None:
        return f"TEAM-BINDING: bound to {where}/"
    team = entry.get("team")
    team_s = team if isinstance(team, str) and team in TEAMS else "<unset>"
    name = Path(entry_path).name if entry_path is not None else "<no path>"
    return (
        f"TEAM-BINDING: NOT CHECKED -- {entry_path} is outside "
        f"verification/queue/<team>/.\n"
        f"    This is an UNCHECKED condition, not a passing one. The entry declares\n"
        f"    team={team_s!r}; nothing here has compared that to a queue directory,\n"
        f"    because this file is not in one. It is checked when the QUEUED copy is\n"
        f"    validated in place:\n"
        f"        queue_entry_check.py --require-binding verification/queue/{team_s}/{name}\n"
        f"    -- that run is the validation that counts."
    )


# --------------------------------------------------------------------------
# MUTANT clauses, used ONLY by --selftest. Each is a deliberate reintroduction
# of a defect, so the control that catches it can be shown to FLIP. A clause
# that has never been seen to fail is not known to be load-bearing (L-314).
# None of these is registered in CHECKS; they are handed to validate() as a
# one-off override and never reach a live entry.
# --------------------------------------------------------------------------

def _mutant_noop(entry: dict, root: Path, entry_path=None) -> list[str]:
    """A clause deleted outright."""
    return []


def _mutant_age_guard_without_scan(entry: dict, root: Path, entry_path=None) -> list[str]:
    """check_age_guard with its TIME-DIRECTORY SCAN removed, nothing else."""
    cwd = entry.get("cwd")
    if not isinstance(cwd, str) or not cwd.startswith("/"):
        return []
    if not Path(cwd).is_dir():
        return []
    return []  # the scan that would have run here is the planted deletion


def _mutant_age_guard_pointed_at_absence(entry: dict, root: Path, entry_path=None) -> list[str]:
    """The PRE-RULING defect, reintroduced verbatim: AGE-GUARD refusing on
    absence with the wording R-AGE-CWD found to state the opposite of the
    truth. Present so the selftest can show the defect is catchable, never so
    it can run."""
    cwd = entry.get("cwd")
    if not isinstance(cwd, str) or not cwd.startswith("/"):
        return []
    if not Path(cwd).is_dir():
        return [
            f"AGE-GUARD: cwd {cwd} does not exist as a directory, so it cannot "
            f"be shown free of a prior answer."
        ]
    return check_age_guard(entry, root, entry_path)


def validate(entry: dict, root: Path, entry_path, checks: dict | None = None,
             require_binding: bool = False) -> list[str]:
    """Run every registered check. Returns the list of failure strings.

    `entry_path` is POSITIONAL AND REQUIRED, by spec sec.5 P2: a caller that cannot
    say where the entry came from raises TypeError here, loudly, rather than
    silently skipping TEAM-BINDING. It is never given a default. Pass None only
    where there genuinely is no file (a dict built in a control), and understand
    that None means TEAM-BINDING is NOT CHECKED for that call."""
    active = CHECKS if checks is None else checks
    fail: list[str] = []
    for fn in active.values():
        fail.extend(fn(entry, root, entry_path))
    if require_binding:
        fail.extend(require_binding_clause(entry, entry_path))
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
    # `python3 -O` refusal, at the entry of the only path whose verdict depends
    # on the interpreter executing this source as written. The controls below
    # mutate guards and take an AST reading of this file; under -O that reading
    # is of source the interpreter is NOT running as written, so a PASS printed
    # here would not be a reading of the shipped behaviour. Same idiom as
    # cases/F25_DUCT3D/grade_f25.py:918. Returns a real exit code -- `set -e` is
    # not in force in this harness and a printed refusal is not a gate (L-314).
    if not __debug__:
        print("REFUSED: --selftest must not run under `python3 -O` or "
              "PYTHONOPTIMIZE (L-332). Re-run under plain `python3`.")
        return 2
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
            fails = validate(entry, root, None)
            fired = [f for f in fails if f.startswith(owner + ":")]
            if not fired:
                problems.append(
                    f"CONTROL FAILED ({name}): expected {owner} to refuse; "
                    f"got {fails or 'NO REFUSAL AT ALL'}"
                )
                continue
            # Mutate the owning guard to a no-op and require the control to FLIP.
            mutated = dict(CHECKS)
            mutated[owner] = lambda e, r, p: []
            after = [f for f in validate(entry, root, None, mutated) if f.startswith(owner + ":")]
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
        fails = validate(valid, root, None)
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

        # ==================================================================
        # R-AGE-CWD controls A / B / C, and the three planted failures the
        # ruling requires. Every planted failure must FLIP its control: that
        # is what distinguishes a clause that is load-bearing and REACHABLE
        # from a clause that is merely present in the file.
        # ==================================================================
        absent = Path(td) / "run_root_that_does_not_exist"   # never created
        b_dir = Path(td) / "holds_a_time_dir"
        (b_dir / "0.1").mkdir(parents=True)

        entry_a = _base_entry(head, live_prereg, str(absent))
        entry_b = _base_entry(head, live_prereg, str(b_dir))
        entry_c = _base_entry(head, live_prereg, str(clean))

        def _clauses(fails: list[str]) -> set:
            return {f.split(":", 1)[0] for f in fails}

        if absent.exists():
            problems.append("CONTROL FAILED (A setup): the absent cwd exists")

        fa = validate(entry_a, root, None)
        ca = _clauses(fa)
        if "EXEC" not in ca:
            problems.append(
                f"CONTROL A FAILED (cwd absent): expected an EXEC refusal, got {fa or 'NO REFUSAL'}")
        elif "AGE-GUARD" in ca:
            problems.append(
                f"CONTROL A FAILED (cwd absent): AGE-GUARD also refused it. "
                f"R-AGE-CWD clause 1 forbids this: absence is not an age finding. Got {fa}")
        else:
            lines.append(
                "CONTROL A FIRED (cwd absent): refused under EXEC and NOT under "
                "AGE-GUARD, naming queue_runner.py:286/:293 and FileNotFoundError.")

        fb = validate(entry_b, root, None)
        cb = _clauses(fb)
        if "AGE-GUARD" not in cb:
            problems.append(
                f"CONTROL B FAILED (cwd holds 0.1/): expected AGE-GUARD, got {fb or 'NO REFUSAL'}")
        elif "EXEC" in cb:
            problems.append(
                f"CONTROL B FAILED (cwd holds 0.1/): EXEC also refused a cwd that EXISTS. Got {fb}")
        else:
            lines.append(
                "CONTROL B FIRED (cwd exists and holds 0.1/): refused under "
                "AGE-GUARD and NOT under EXEC.")

        fc = validate(entry_c, root, None)
        if fc:
            problems.append(f"CONTROL C FAILED (cwd exists, clean): expected ACCEPTED, got {fc}")
        else:
            lines.append("CONTROL C FIRED (cwd exists, clean): ACCEPTED, zero refusals.")

        # --- planted failure 1: delete check_cwd_launchable -> A ACCEPTS ---
        m1 = dict(CHECKS); m1["EXEC"] = _mutant_noop
        f1 = validate(entry_a, root, None, m1)
        if f1:
            problems.append(
                f"PLANT 1 DID NOT FLIP: with check_cwd_launchable deleted, control A "
                f"was still refused by {f1}. A's refusal is not coming from that clause.")
        else:
            lines.append(
                "PLANT 1 FLIPPED control A: deleting check_cwd_launchable made the "
                "absent-cwd entry ACCEPTED, so EXEC is the clause that catches it.")

        # --- planted failure 2: delete the time-dir scan -> B ACCEPTS ------
        m2 = dict(CHECKS); m2["AGE-GUARD"] = _mutant_age_guard_without_scan
        f2 = validate(entry_b, root, None, m2)
        if f2:
            problems.append(
                f"PLANT 2 DID NOT FLIP: with the time-directory scan deleted, control B "
                f"was still refused by {f2}.")
        else:
            lines.append(
                "PLANT 2 FLIPPED control B: deleting the time-directory scan made the "
                "0.1/-bearing entry ACCEPTED, so the scan is the clause that catches it.")

        # --- planted failure 3: re-point AGE-GUARD at absence -> A refuses
        #     under AGE-GUARD. This is the DEFECT R-AGE-CWD removes, shown
        #     reintroducible and shown caught.
        m3 = dict(CHECKS); m3["AGE-GUARD"] = _mutant_age_guard_pointed_at_absence
        f3 = validate(entry_a, root, None, m3)
        if "AGE-GUARD" not in _clauses(f3):
            problems.append(
                f"PLANT 3 DID NOT FLIP: the pre-ruling defect was reintroduced and "
                f"control A did NOT pick up an AGE-GUARD refusal. Got {f3}. The "
                f"selftest cannot detect a regression it cannot reproduce.")
        else:
            lines.append(
                "PLANT 3 FLIPPED control A: re-pointing check_age_guard at absence "
                "reintroduced the pre-ruling AGE-GUARD refusal and the control saw "
                "it, so a regression to that defect is detectable, not silent.")
        # And the shipped code must NOT be the mutant.
        if "AGE-GUARD" in _clauses(validate(entry_a, root, None)):
            problems.append(
                "PLANT 3 RESIDUE: the SHIPPED code still refuses an absent cwd under "
                "AGE-GUARD. The mutant was not confined to the selftest.")

        # --- L-314 Instance 1, MEASURED IN THIS HARNESS, NOT RECALLED ------
        #     `set -e` is NOT in force here. Measured at the harness top level:
        #     `python3 -c "raise SystemExit(1)"; echo REACHED` prints REACHED,
        #     and `bash -c 'python3 -c "raise SystemExit(1)"; echo REACHED_D'`
        #     exits 0 -- the failure is swallowed whole. So a refusal that is
        #     only PRINTED is not a gate. Two shapes are driven below: the
        #     hazard shape, shown live to swallow the rc, and the correct
        #     shape, in which a caller with no `set -e` still detects the
        #     refusal because it tests rc explicitly and the refusal line is
        #     greppable in the output.
        planted_file = Path(td) / "planted_absent_cwd_entry.json"
        planted_file.write_text(json.dumps(entry_a))
        me = Path(__file__).resolve()

        hazard = subprocess.run(
            ["bash", "-c", f"python3 {me} {planted_file} > {td}/hz.txt 2>&1\necho SWALLOWED\n"],
            capture_output=True, text=True)
        if hazard.returncode != 0 or "SWALLOWED" not in hazard.stdout:
            problems.append(
                f"L-314 HAZARD CONTROL FAILED: the ignoring caller was expected to run "
                f"on and exit 0 (that is the hazard being demonstrated); got rc "
                f"{hazard.returncode}, stdout {hazard.stdout!r}.")
        else:
            lines.append(
                "L-314 HAZARD SHOWN LIVE: a caller that does not test rc ran the "
                "refusing guard, continued past it and exited 0. `set -e` is not in "
                "force in this harness; a printed refusal alone would have been lost.")

        checked = subprocess.run(
            ["bash", "-c",
             f"rc=0\npython3 {me} {planted_file} > {td}/ck.txt 2>&1 || rc=$?\n"
             f"echo RC=$rc\necho REACHED_ANYWAY\n"],
            capture_output=True, text=True)
        out_txt = (Path(td) / "ck.txt").read_text() if (Path(td) / "ck.txt").exists() else ""
        rc_line = [l for l in checked.stdout.splitlines() if l.startswith("RC=")]
        greppable = "REFUSED" in out_txt and "EXEC:" in out_txt
        if not rc_line or rc_line[0] != "RC=2":
            problems.append(
                f"L-314 CONTROL FAILED: the refusing invocation did not return rc 2 to "
                f"a caller that tested it; saw {rc_line or 'no RC line'}.")
        elif "REACHED_ANYWAY" not in checked.stdout:
            problems.append(
                "L-314 CONTROL FAILED: the caller did not reach the line after the rc "
                "test, so the rc could not have been acted on.")
        elif not greppable:
            problems.append(
                "L-314 CONTROL FAILED: rc 2 was returned but the output carries no "
                "greppable 'REFUSED' / 'EXEC:' line. A gate whose failure is invisible "
                "in the log is not a gate.")
        else:
            lines.append(
                "L-314 CONTROL FIRED: with NO `set -e`, a caller that tested rc "
                "explicitly read RC=2 from the refusing guard, reached the line after "
                "it, and the output carries a greppable 'REFUSED' + 'EXEC:' line. The "
                "refusal survives the exact shell shape that swallowed it above.")

        # ==================================================================
        # TEAM-BINDING controls C1-C12.
        # docs/standards/QUEUE_ENTRY_TEAM_BINDING.md sec.6, spec frozen b23b5638,
        # amended v1.1 2026-08-27. Written BEFORE this code existed so the code
        # could not be shaped to pass its own test. Nothing real is touched: the
        # whole scratch queue tree lives under the TemporaryDirectory above.
        # ==================================================================
        qroot = Path(td) / "verification" / "queue"
        for _t in TEAMS:
            (qroot / _t).mkdir(parents=True, exist_ok=True)
        drafts = Path(td) / "queue_drafts"
        drafts.mkdir(exist_ok=True)

        def _write(where: Path, name: str, ent: dict) -> Path:
            p = where / name
            p.write_text(json.dumps(ent))
            return p

        base_ok = _base_entry(head, live_prereg, str(clean))

        # --- C1: MATCH ACCEPTED ------------------------------------------
        c1_entry = {**base_ok, "team": "cfd"}
        c1_path = _write(qroot / "cfd", "C1_MATCH.json", c1_entry)
        c1 = validate(c1_entry, root, c1_path)
        if _clauses(c1) & {"TEAM-BINDING"}:
            problems.append(
                f"C1 FAILED (match accepted): a cfd entry in cfd/ drew a TEAM-BINDING "
                f"refusal. Got {c1}. A check that refuses everything is not a check.")
        elif c1:
            problems.append(f"C1 FAILED (match accepted): unexpected refusals {c1}")
        else:
            lines.append("C1 FIRED (match accepted): team='cfd' in verification/queue/cfd/ "
                         "-> zero refusals, no TEAM-BINDING clause.")

        # --- C2: MISMATCH REFUSED -- THE MANDATORY PLANTED FAILURE --------
        c2_entry = {**base_ok, "team": "closure"}
        c2_path = _write(qroot / "cfd", "C2_MISMATCH.json", c2_entry)
        c2 = validate(c2_entry, root, c2_path)
        c2_fired = [f for f in c2 if f.startswith("TEAM-BINDING:")]
        c2_names_both = bool(c2_fired) and "'closure'" in c2_fired[0] and "queue/cfd/" in c2_fired[0]
        if not c2_fired:
            problems.append(
                f"C2 FAILED (planted mismatch): team='closure' sitting in cfd/ was NOT "
                f"refused. Got {c2 or 'NO REFUSAL AT ALL'}.")
        elif not c2_names_both:
            problems.append(
                f"C2 FAILED (planted mismatch): refused, but the message does not name "
                f"BOTH the declared team and the directory. Got {c2_fired[0]!r}")
        else:
            lines.append("C2 FIRED (planted mismatch): team='closure' in "
                         "verification/queue/cfd/ REFUSED under TEAM-BINDING, message "
                         "naming both the declared team and the directory.")

        # --- C3: MUTATION OF C2 -- the check no-opped, C2 must FLIP -------
        m_bind = dict(CHECKS); m_bind["TEAM-BINDING"] = _mutant_noop
        c3 = [f for f in validate(c2_entry, root, c2_path, m_bind) if f.startswith("TEAM-BINDING:")]
        if c3:
            problems.append(
                f"C3 DID NOT FLIP: check_team_binding was mutated to a no-op and C2's "
                f"refusal PERSISTED ({c3}). C2 is not coming from the clause it is "
                f"credited to, so C2 tested nothing.")
        else:
            lines.append("C3 FLIPPED C2: with check_team_binding no-opped the mismatch "
                         "was ACCEPTED -- C2's refusal comes from that clause and no other.")

        # --- C4: a caller that cannot supply the path FAILS LOUDLY -------
        c4_raised = ""
        try:
            validate(c1_entry, root)          # entry_path omitted: must not be silent
        except TypeError as exc:
            c4_raised = str(exc)
        if not c4_raised:
            problems.append(
                "C4 FAILED (blind reader): validate() accepted a call with NO entry_path "
                "and did not raise. A check that silently passes when its input is "
                "missing is a zero from a reader not shown able to see a non-zero.")
        else:
            lines.append("C4 FIRED (blind reader): validate() with no entry_path raised "
                         "TypeError loudly rather than skipping TEAM-BINDING.")

        # --- C5: MUTATION OF C4 -- give the path a skipping default ------
        def _mutant_validate_optional_path(entry, root_, entry_path=None, checks=None,
                                           require_binding=False):
            """The defect C4 exists to prevent, reintroduced: entry_path defaulted, so
            an omitting caller silently skips TEAM-BINDING instead of failing."""
            return validate(entry, root_, entry_path, checks, require_binding)

        c5_raised = ""
        c5_out = None
        try:
            c5_out = _mutant_validate_optional_path(c2_entry, root)
        except TypeError as exc:
            c5_raised = str(exc)
        if c5_raised:
            problems.append(
                f"C5 DID NOT FLIP: even with entry_path defaulted the call still raised "
                f"({c5_raised}), so C4 was not testing the required-ness of the argument.")
        elif [f for f in (c5_out or []) if f.startswith("TEAM-BINDING:")]:
            problems.append(
                "C5 DID NOT FLIP: the defaulted-path mutant still produced a TEAM-BINDING "
                "refusal, so the silent-skip defect was not reproduced.")
        else:
            lines.append("C5 FLIPPED C4: with entry_path defaulted, the very entry C2 "
                         "refuses validated CLEAN and silently -- that is the defect C4 "
                         "prevents, shown reproducible.")

        # --- C6: NO DOUBLE REPORT ----------------------------------------
        c6_entry = {k: v for k, v in base_ok.items() if k != "team"}
        c6_path = _write(qroot / "cfd", "C6_NOTEAM.json", c6_entry)
        c6 = validate(c6_entry, root, c6_path)
        c6_team_fails = [f for f in c6 if "team" in f]
        c6_bind = [f for f in c6 if f.startswith("TEAM-BINDING:")]
        if len(c6_team_fails) != 1 or c6_bind:
            problems.append(
                f"C6 FAILED (no double report): a missing `team` produced "
                f"{len(c6_team_fails)} team failure(s) and {len(c6_bind)} TEAM-BINDING "
                f"failure(s); expected exactly 1 and 0. Got {c6}")
        else:
            lines.append("C6 FIRED (no double report): a missing `team` is refused ONCE, "
                         "by SCHEMA, and TEAM-BINDING stays silent.")

        # --- C7: NOT CHECKED IS PRINTED, and is not a refusal ------------
        c7_path = _write(drafts, "C7_DRAFT.json", c1_entry)
        c7 = validate(c1_entry, root, c7_path)
        c7_note = binding_note(c1_entry, c7_path)
        if c7:
            problems.append(
                f"C7 FAILED (draft outside the queue): a valid draft was REFUSED ({c7}). "
                f"Refusing here would force lanes to copy into the drop path BEFORE "
                f"validating -- i.e. to validate after the launch is armed.")
        elif "NOT CHECKED" not in c7_note:
            problems.append(
                f"C7 FAILED (draft outside the queue): accepted, but the verdict does not "
                f"say NOT CHECKED. Got {c7_note!r}")
        else:
            lines.append("C7 FIRED (draft outside the queue): ACCEPTED with no refusal, "
                         "and the verdict carries the NOT CHECKED block naming what was "
                         "not checked and where it will be.")

        # --- C8: MUTATION OF C7 -- suppress the note; C7 must FLIP -------
        def _mutant_binding_note_silent(entry, entry_path):
            """The defect: an unchecked condition reported as nothing at all."""
            return ""

        c8_note = _mutant_binding_note_silent(c1_entry, c7_path)
        if "NOT CHECKED" in c8_note:
            problems.append(
                "C8 DID NOT FLIP: the suppressed note still contained NOT CHECKED, so C7 "
                "was not reading the note.")
        else:
            lines.append("C8 FLIPPED C7: with binding_note suppressed the unbound entry "
                         "reads exactly like a bound one -- C7 is reading the note itself, "
                         "not merely the absence of a refusal.")

        # --- C9: END TO END THROUGH ONE REAL tick() OF THE DAEMON --------
        # queue_runner is imported HERE, not at module scope: queue_runner imports
        # this module, and the runner's own selftest must stay untouched.
        # The scratch root must carry the SPEC'S OWN PATH SHAPE --
        # <...>/verification/queue/<team>/ -- because that shape is what
        # containing_team_dir() recognises (sec.1 of the spec). Measured while
        # writing this control: a root NOT of that shape leaves TEAM-BINDING
        # unbound, and the first draft of C9 used one and watched the mismatched
        # entry LAUNCH. That is the control doing its job, and it is why the
        # shape is asserted here rather than assumed.
        c9_dir = Path(td) / "c9" / "verification" / "queue"
        for _t in TEAMS:
            (c9_dir / _t).mkdir(parents=True, exist_ok=True)
        c9_path = _write(c9_dir / "cfd", "C9_MISMATCH.json", {**base_ok, "team": "dafoam"})
        if containing_team_dir(c9_path) != "cfd":
            problems.append(
                f"C9 PRECONDITION FAILED: the scratch root is not the shape the check "
                f"recognises (containing_team_dir -> {containing_team_dir(c9_path)!r}). "
                f"The control would pass vacuously.")
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import queue_runner as _qr
            _log = _qr.Log(c9_dir / "runner.log", echo=False)
            _verdict = _qr.tick(c9_dir, _log, 100.0, 1.0, 0.2, {},
                                measure=lambda: (0.0, 9_999.0))
            moved = (c9_dir / "cfd" / "refused" / "C9_MISMATCH.json").exists()
            reason = (c9_dir / "cfd" / "refused" / "C9_MISMATCH.REFUSED.txt")
            named = reason.exists() and "TEAM-BINDING" in reason.read_text()
            launched_any = any((c9_dir / _t / "launched").exists() for _t in TEAMS)
            still_there = c9_path.exists()
            if _verdict != "REFUSED-ONLY" or not moved or not named or launched_any or still_there:
                problems.append(
                    f"C9 FAILED (end to end): tick returned {_verdict!r}, moved={moved}, "
                    f"reason_names_clause={named}, any_launched_dir={launched_any}, "
                    f"still_in_drop_path={still_there}. Expected REFUSED-ONLY, moved to "
                    f"refused/ with the clause named, and NOTHING launched.")
            else:
                lines.append(
                    "C9 FIRED (end to end): one real queue_runner.tick() over a scratch "
                    "root moved the mismatched entry to cfd/refused/ with "
                    "C9_MISMATCH.REFUSED.txt naming TEAM-BINDING, returned REFUSED-ONLY, "
                    "and created no launched/ directory anywhere -- nothing was launched.")
        except Exception as exc:                      # a control that cannot run is a FAIL
            problems.append(f"C9 FAILED (end to end): {type(exc).__name__}: {exc}")

        # --- C10: the instrument still carries zero asserts ---------------
        c10 = count_assert_nodes(Path(__file__).read_text())
        if c10 != 0:
            problems.append(
                f"C10 FAILED: {c10} `assert` node(s) in this file. Under python3 -O every "
                f"one of them vanishes, so a refusal written as one is a refusal OFFER.")
        else:
            lines.append("C10 FIRED: zero `ast.Assert` nodes after the change -- every "
                         "refusal added here is a return into the failure list (L-332).")

        # --- C11: --require-binding, and its planted failure --------------
        c11_off = validate(c1_entry, root, c7_path, require_binding=False)
        c11_on = validate(c1_entry, root, c7_path, require_binding=True)
        c11_fired = [f for f in c11_on if f.startswith("REQUIRE-BINDING:")]
        if c11_off:
            problems.append(
                f"C11 FAILED: WITHOUT the flag the unbound draft was refused ({c11_off}). "
                f"The draft workflow must be untouched by default.")
        elif not c11_fired:
            problems.append(
                f"C11 FAILED: WITH --require-binding the unbound draft was NOT refused. "
                f"Got {c11_on or 'NO REFUSAL AT ALL'}. Printed-never-silent alone is "
                f"reading-dependent; the flag is what makes it machine-checkable.")
        else:
            lines.append("C11 FIRED (planted, --require-binding): the same unbound draft "
                         "is ACCEPTED without the flag and REFUSED with it, the refusal "
                         "saying it is the ABSENCE of a check and not a failed one.")

        # --- C12: MUTATION OF C11 -- disable the flag's effect ------------
        _real_clause = require_binding_clause
        try:
            globals()["require_binding_clause"] = lambda entry, entry_path: []
            c12 = [f for f in validate(c1_entry, root, c7_path, require_binding=True)
                   if f.startswith("REQUIRE-BINDING:")]
        finally:
            globals()["require_binding_clause"] = _real_clause
        if c12:
            problems.append(
                f"C12 DID NOT FLIP: require_binding_clause was replaced by a no-op and the "
                f"refusal PERSISTED ({c12}), so C11 is not testing the flag.")
        else:
            lines.append("C12 FLIPPED C11: with require_binding_clause no-opped the flag "
                         "stopped refusing -- C11's refusal comes from that clause alone.")

        # A last standing check: nothing above may have reached outside td.
        if list(Path("/home/ubuntu/Certonomous/verification/queue/cfd").glob("C*_*.json")):
            problems.append(
                "CONTROL HYGIENE FAILED: a control artefact was written into the REAL cfd "
                "drop path. The drop path is a launch button; a test file there is a launch.")
        else:
            lines.append("CONTROL HYGIENE: no control artefact reached the real drop path.")

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
    ap.add_argument("--require-binding", action="store_true",
                    help="REFUSE an entry that is not in verification/queue/<team>/, "
                         "so TEAM-BINDING cannot go unchecked. Use this on the QUEUED "
                         "copy, in the team directory, after the copy: that run is the "
                         "validation that counts (cfd-supervisor, 2026-08-27).")
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
            fails = validate(entry, root, path,
                             require_binding=args.require_binding)
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
            # Printed on EVERY acceptance, bound or not. An unbound entry says
            # NOT CHECKED in a different SHAPE from a bound one, because an
            # unchecked condition must never report like a satisfied one.
            print("    " + binding_note(entry, path))
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
