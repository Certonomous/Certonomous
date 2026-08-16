#!/usr/bin/env python3
"""ONE ENTRY POINT. Everything this lab knows how to check, run once, three-valued.

WHY THIS EXISTS (docket D64, 2026-08-14)
========================================
D64 records the finding that outranks every individual defect this lab found on
2026-08-14: **nothing here is scheduled to run any check at all.** No CI, no
Makefile, no pytest config, no installed git hook, no Claude hook. The only cron
on the box is the five-minute `auto-stop.sh` and a `@reboot`. Every check that
exists -- `scripts/self_audit.py`'s 34, and every file under `sdk/tests/` --
reddens only when a human or an agent happens to type its name.

The day that produced D64 also produced, in one twelve-hour window:

  * a guard grading against a benchmark board three days stale, with three false
    claims live on travelling surfaces;
  * two hardcoded literals inside a guard that went false when the board moved
    and reddened nothing;
  * a "Full suite 115 passed" that was ONE test file run alone, against a tree
    of 1,609 tests (`7bf55c90`);
  * a shipped bundle that went stale seven minutes after it was rebuilt
    (D56, `bd3da3a1`);
  * a register of un-executable scripts that went stale the day after it was
    dated;
  * a control-room clause naming a directory that had migrated (D65, `b39df811`).

Every one of those is the same failure, and it is not "the check was missing".
**The check existed, the check was correct, and nobody ran it.** Building a
35th check changes nothing while that is true. This module is the other half.

WHAT IT PROMISES, AND WHAT IT DOES NOT
======================================
It promises to (1) find the checks mechanically rather than from a typed list,
(2) run what it is safe to run unattended, (3) return PASS / FAIL / UNKNOWN, and
(4) print its own frame -- how many candidates it found, how it found them, how
many ran, and what it could not run and why -- so that a green run is readable
as the narrow statement it actually is.

It does NOT promise coverage. The skip list is the interesting output. A run
that admits four checks out of sixty candidates is telling you something, and
this module prints that ratio on every run rather than in a footnote.

ENUMERATION IS THE POINT (and a hand-maintained list is the defect one level up)
===============================================================================
This lab has been bitten repeatedly by hand-maintained lists: the exec-bit
waiver register that went stale the day after it was dated, the docket rows that
name checks nobody ran, the "Full suite" that was one file. A runner with a
typed list of checks inside it is the same defect wearing a different hat: the
check you forget to add is invisible, and the runner is green anyway.

So the candidate set is DERIVED, in two frames, and both are printed:

    TRACKED   `git ls-files scripts sdk/tests`  -- what travels
    WORKTREE  the same directories on disk      -- what is here now

The difference between them is itself reported. A check that exists only in the
worktree does not travel, and a tracked path that is not on disk is a dangling
one; both are findings, and neither is visible to a runner that scans only one
frame. Note that this module never shells out to `grep` or `find`: the
interactive shell here aliases `grep` to `ugrep --ignore-files`, which honours
`.gitignore` and therefore sees about 23% of this tree, and its `find` is `bfs`,
which rejects GNU expressions. Both discrepancies have produced false findings
in this lab. Enumeration is `git ls-files` plus `os.walk`, and nothing else.

ADMISSION: THREE MECHANICAL PREDICATES, READ OUT OF THE CANDIDATE'S OWN SOURCE
=============================================================================
Enumeration finds candidates; it does not decide which of them is a check.
That decision is made by parsing the candidate, never by matching its name, and
every candidate's predicate vector is printed by `--list`.

  P1  ENTRY POINT.  The module has an `if __name__ == "__main__"` guard, and
      the guard's call resolves to a module-level function. Without one there is
      nothing to run.  ->  SKIP `no-entry-point`

  P2  IT CAN FAIL.  Somewhere in the entry function's own body (nested
      functions excluded, because they are not the exit path) there is an exit
      whose value is not the constant 0. This is D64's own criterion, quoted
      from the row: `scripts/gate_table.py` "scrapes act transcripts and its
      `main()` returns 0 unconditionally, so it cannot fail". A program whose
      exit code is a constant is a printer, not a gate, and scheduling a
      printer manufactures green.  ->  SKIP `cannot-fail`

  P3  IT NEEDS NOTHING THIS RUNNER MAY NOT SPEND.  Two sub-predicates, both
      structural rather than lexical:
        * REQUIRED ARGUMENTS -- the entry function's argparse declares a
          required positional, or the module indexes `sys.argv[1]`. A check
          that needs a case directory named on the command line has no
          scheduled meaning.  ->  SKIP `requires-arguments`
        * COMPUTE -- a `subprocess` call whose argv head is a solver binary
          (`simpleFoam`, `snappyHexMesh`, `mpirun`, `dafoam`, `vspaero`, ...).
          Compute authorisation is Katie's; a scheduled runner that can spend
          core-minutes is a runner that will.  ->  SKIP `needs-compute`,
          and the aggregate records it as an UNKNOWN with a reason, never a pass.

  P4  IT DOES NOT WRITE.  A module containing a write primitive
      (`open(..., "w")`, `write_text`, `mkdir`, `shutil.copy`, `os.remove`, a
      `git add`/`commit` subprocess) is not run against the live tree, because
      ten agents are working in it. Such a candidate is not dropped: it is run
      in `--tree snapshot` mode, where a `git worktree` of HEAD absorbs the
      writes. `scripts/withdrawal_sweep.py` is the honest instance -- it plants
      and removes its own L-84 controls in the tree, and that plant is not a
      defect, it is the control apparatus.  ->  SKIP `writes-to-tree` in live
      mode; ADMITTED in snapshot mode.

  SHELL is enumerated and never admitted, with the hazard named. This runner
  reads an exit contract out of a Python AST and cannot read one out of shell --
  and the shell files in `scripts/` are actuators, not checks:
  `auto-stop.sh` powers the box off, `kill_worker.sh` kills solvers,
  `launch_solve.sh` spends core-hours, `demo_servers.sh` and `lab.sh` start
  services. A runner that ran `scripts/*.sh` on a schedule would be the worst
  defect this lab has shipped. They are listed as a stated coverage gap.

THREE-VALUED, AND IT CANNOT PASS FROM AN EMPTY SET (defect class B1)
===================================================================
The silent-zero sweep -- a checker that examined nothing and reported clean --
is the class this lab ranks highest (D62: a corpus replay that "would return
clean having never opened the four records it exists to examine").

    PASS      at least one check ran, every check that ran said PASS,
              and nothing was skipped for a reason that hides a verdict.
    FAIL      some check that ran said FAIL. One is enough.
    UNKNOWN   zero checks ran; or a check could not be run, timed out,
              crashed without producing a verdict, or was skipped for a
              reason that could hide a verdict.

An empty admitted set is UNKNOWN with the reason `no check was admitted`, never
PASS.

Per-check verdicts come from the exit code under a published contract --
0 PASS, 1 or 2 FAIL, 3 UNKNOWN, anything else UNKNOWN with the code named. The
two checks that already carry a three-valued contract in their own source agree
with it by construction: `check_absolutes.py` returns
`{"CLEAN": 0, "FLAGGED": 1, "UNKNOWN": 3}[verdict]` and `sweep.py` returns
`{"MATCHES": 0, "ZERO": 1, "UNKNOWN": 3}[verdict]`.

A check that dies with a traceback is UNKNOWN, not FAIL. The difference
matters: FAIL is a statement about the lab, UNKNOWN is a statement about the
instrument, and merging them is how a broken checker gets read as a finding
(or, worse, how a finding gets read as a broken checker and then ignored).

THE GRADED PARTY MUST NOT CONTROL THE PREDICATE THAT DECIDES WHETHER IT WAS
GRADED (V15 round 7 F0, docket D101 -- repaired 2026-08-15)
==========================================================================
The paragraph above was true and the mechanism built on it was not. The
downgrade was `crashed = "Traceback (most recent call last)" in err`, over the
CHECK'S OWN STDERR, with no other condition; and `scripts/installed/pre-push`
mapped UNKNOWN, and every code outside the contract, to `rc=0`. Demonstrated in
a scratch repository with one gate, run twice, same finding and same exit 1,
differing by one line:

    plain                                   FAIL     exit 1   push blocked
    + sys.stderr.write("Traceback (most   UNKNOWN    exit 3   push ALLOWED
      recent call last)\n")

The finding was still on stdout in the second run. The runner read it, printed
it, and did not act on it. **A check that crashes is exactly the check most
likely to be hiding something, and this converted its crash into a pass.**

The repair is two locks, and each is stated here as the argument for why no
text a check emits can improve the aggregate:

  LOCK 1 -- A REPORTED FINDING SURVIVES ANY STDERR. The crash downgrade now
  requires that the check produced NO verdict line on its own stdout. This is
  the same standard the `usage_error` path has carried since it was written
  (`not out.strip()`), applied to the path that lacked it. A check that said
  FAIL has said FAIL; writing to stderr afterwards does not unsay it.

  LOCK 2 -- THE ESCAPE IS WORTH NOTHING EVEN WHEN IT WORKS. To reach UNKNOWN a
  check must now ALSO suppress its own finding from stdout -- and an UNKNOWN
  that a check produced by running exits `EXIT_UNSOUND` (4), which the hook
  BLOCKS on, exactly as it blocks on FAIL. So the best a graded check can do by
  emitting text is trade one blocking code for another blocking code while
  deleting the evidence of what it found. There is no monotone improvement
  available, which is the property that makes this a gate.

  The cut between the two UNKNOWNs is not a severity judgement, it is the
  control boundary: **a check controls its own output; it does not control the
  runner's reach.** UNKNOWN about a check's OUTPUT (crashed, timed out, would
  not start, exited outside the contract, returned its own UNKNOWN, or wrote to
  the tree it was being graded against) blocks. UNKNOWN about the runner's
  REACH (a candidate skipped `needs-compute` or `writes-to-tree`, `--no-tests`,
  an enumerated file that declares no test) does not block: nothing is hidden
  there, the coverage statement is printed in full on every run, and a hook
  that blocks on the permanent state of the repository is a hook that gets
  deleted -- after which it checks nothing at all.

  Note what is deliberately NOT done: the downgrade is not deleted. A traceback
  really can mean the instrument is broken rather than the lab, and calling
  that FAIL is how a finding gets read as a broken checker and ignored. What is
  removed is the REWARD for it.

THE EXIT CODES, AND WHERE THEY ARE PINNED
=========================================
    0  PASS
    1  FAIL
    3  UNKNOWN about reach          -- warn, do not block
    4  UNKNOWN about a check's output -- BLOCK; the runner does not know what
                                        that check would have found
Anything else is a runner this hook does not understand, and `pre-push` blocks
on it rather than waving it through. These four numbers are asserted as
literals in `sdk/tests/test_lab_check.py`, and the hook's behaviour on each of
them is asserted by RUNNING the hook against a stub runner rather than by
matching text in it.

NO `2>/dev/null`, ANYWHERE
==========================
Every subprocess's stderr is captured and reported. Nothing is discarded. On
2026-08-14 a `2>/dev/null` on a `find` invocation nearly turned a tool-not-found
error into a clean "nobody is working" -- the box would have powered itself off
under five working agents. D65's repair surfaced that stderr for exactly this
reason, and this runner inherits the rule: a silent stderr is a claim, and the
claim is "there was nothing on stderr".

WHAT A GREEN RUN DOES NOT MEAN (the half worth reading)
=======================================================
Measured against real defects from 2026-08-14, this runner catches: a shipped
bundle that drifted from the tree, an installed artifact that drifted from its
tracked copy, an unowned supersession, a tracked shebang script committed
without its exec bit, and a test file that declares tests and contributes none.
Each was demonstrated in both directions -- planted and unplanted -- in
`sdk/tests/test_lab_check.py` and in the reconstruction log on docket D64.

It does NOT catch, and a green run says nothing about:

  * A CHECK WHOSE REFERENT WENT STALE. This is the 2026-08-14 rank-guard defect
    and D65's auto-stop clause: the check was correct, the thing it named moved.
    A runner runs checks. Running a check whose referent is stale more often
    produces a stale answer more often, and that is all.
  * A DETECTOR THAT TURNED ITSELF OFF. `self_audit.py`'s two board-referent
    guards return WARN when their referent cannot be read, and `self_audit`
    exits non-zero only on FAIL -- so an OFF detector reddens nothing here
    either. Filed as docket D78; not repaired in this module, because the
    repair belongs in the check.
  * ANYTHING IN THE 15 SHELL FILES, six write-capable checks (in live mode), or
    any check that needs compute. All three are printed, every run, with the
    reason.
  * A FALSE CLAIM IN PROSE. `check_absolutes.py` is the instrument for that
    class and this lab measured its false-positive rate at 74%, which is why it
    is a reported FAIL here rather than something anybody can act on directly.

A HEAD WORKTREE IS NOT A GRADEABLE TREE HERE, and that is a finding
====================================================================
`--tree snapshot` grades a `git worktree` of HEAD. It is the tidier thing to
schedule -- write-capable checks become harmless, and the verdict is anchored to
a commit instead of to whatever was half-saved at 03:17 -- and it was MEASURED
before being recommended, which is why it is not recommended.

Measured 2026-08-14, same commit, snapshot against live:

    self_audit.py           `ledger integrity: ledger not found or empty`,
                            and 67 unresolved citations against 6 live
    check_convergence_sweep `RED: this sweep matched no logs at all ...
                            solve_registry DOES NOT EXIST`

Neither is a finding about the lab. Most of what these checks examine -- the
ledger, the solve registry, the case archives -- is GITIGNORED, so a HEAD
worktree is missing the evidence the checks are about. A nightly snapshot run
would cry wolf every night and be switched off inside a week, which is a worse
outcome than not scheduling it. So the scheduled run is the LIVE tree, snapshot
mode stays available for the write-capable checks and for grading a commit, and
the difference is written down here rather than discovered twice.

THE REPORT IS STREAMED, AND A TRUNCATED LOG SAYS SO (docket D148, 2026-08-16)
=============================================================================
Until 2026-08-16 this module built its entire report in a list and printed it
in ONE terminal write, after the last check had finished. Measured on the live
tree, and the artifact is the point:

    timeout 45 python3 scripts/lab_check.py --no-tests
      -> exit 124, stdout 0 bytes, stderr 0 bytes

A full run is ~20-24 minutes and the fast tier ~3, so that window is reachable
in ordinary operation, not only under contention. Two consequences, and the
second is the one that ranks:

  1. AN INTERRUPTED RUN DESTROYED EVERYTHING IT HAD ALREADY LEARNED. Twenty
     minutes of check output, including any FAIL already in hand, went with it.
  2. **"THE RUNNER TIMED OUT" AND "THE RUNNER FOUND NOTHING" WERE THE SAME
     ARTIFACT.** A nightly cron that hits its window appends a zero-byte block
     to `/home/ubuntu/lab-check.log`, and a zero-byte block is exactly what a
     clean run looks like to anyone who greps that log for faults. That is
     defect class B1, the silent-zero -- the class this lab ranks highest --
     sitting in the instrument that reports every other check's verdict.

The repair has two halves, and the second is the one that closes B1.

STREAMED. Every line is written and FLUSHED at the moment it is produced: the
frame first, then one block per check as that check returns. `stdout` is block
buffered when it is a file, which is exactly the cron case, so the flush is not
decoration -- without it a killed run loses the last 4-8 KB it had "written".

SELF-IDENTIFYING. Absence of output is not evidence of anything, so the run
does not rely on it. Three markers, all greppable, all at column 0:

    LAB-CHECK-BEGIN    written BEFORE enumeration, before any git call. Its
                       presence means a run started here.
    LAB-CHECK-PLAN     how many check units were admitted and are expected to
                       run, and their names. Written before the first one
                       starts, so the DENOMINATOR survives truncation.
    LAB-CHECK-END      the terminator, and the only line that certifies a
                       report. `LAB-CHECK-END COMPLETE ...` on a run that
                       finished; `LAB-CHECK-END INCOMPLETE ...` on one that was
                       interrupted and got as far as saying so.

Plus, inside the run, a `>>` line naming each check as it STARTS and a
`[VERDICT]` block as it finishes. A `>>` with no verdict block under it names
the check that was in flight when the log ends -- so "died at check 3 of 17" is
readable off the log rather than inferred from silence.

The reader's test, which is the requirement this was built against: someone who
greps a log for faults and finds none can now tell three states apart --

    LAB-CHECK-END COMPLETE     the run finished. No faults means no faults.
    LAB-CHECK-END INCOMPLETE   it was interrupted; the `ran=k/n` on that line
                               says how far it got, and everything up to there
                               is above it.
    no LAB-CHECK-END at all    it died without even getting to say so
                               (SIGKILL, the box went down, the disk filled).
                               A `LAB-CHECK-BEGIN` with no end is a truncated
                               log; NEITHER marker present is a run that never
                               started, which is its own finding.

WHAT THE EXIT CODE CAN AND CANNOT CARRY (measured, not assumed)
===============================================================
Under `timeout`, the runner does not get to choose. Measured on this box:

    timeout 2 python3 sigtest.py   (handler catches SIGTERM, exits 4)
      -> the shell sees 124, not 4

GNU `timeout` reports 124 whenever it had to kill, whatever the child then
chose. So on the path that produced D148's artifact THE EXIT CODE IS NOT THE
RUNNER'S TO SET, and any scheme that leans on it is broken at that exact point.
That is why the marker is in the LOG: the log is the one channel the runner
controls all the way through.

Where the runner IS asked -- a direct SIGTERM, a person's SIGINT, an unhandled
exception in the runner itself -- it answers `EXIT_UNSOUND` (4), measured at 4
through a direct `send_signal` in the same experiment. 4 is not a new code and
it is not a weakening: it already means "a check was launched and did not come
back with a usable verdict, and the runner cannot say what it would have
found", which is precisely an interrupted run, and `scripts/installed/pre-push`
already blocks on it. The existing contract is untouched: UNKNOWN about a
check's output still blocks (4), UNKNOWN about reach still does not (3), and a
`requires-arguments` skip still does not downgrade the aggregate.

An unhandled exception inside the runner used to exit 1, which is FAIL -- the
runner's own crash was reported in the vocabulary of a finding about the lab.
It now exits 4, with the traceback printed above an INCOMPLETE terminator.

STALE BYTECODE (a method note that is load-bearing here)
========================================================
`__pycache__` under this repo has INVERTED mutation results in this lab: the
clean control failed and the mutated case passed. `PYTHONDONTWRITEBYTECODE=1`
does not fix it -- it stops writing, not reading. This runner purges every
`__pycache__` under the tree before the test group runs, and says so in its
frame block.

USAGE
=====
    scripts/lab_check.py                 # live tree, everything safe to run
    scripts/lab_check.py --list          # enumerate and classify, run nothing
    scripts/lab_check.py --tree snapshot # a git worktree of HEAD; writers admitted
    scripts/lab_check.py --no-tests      # scripts only (the fast tier)
    scripts/lab_check.py --json          # machine-readable, same verdicts

Nothing here installs itself. See `scripts/installed/certonomous-lab-check.cron`
and `scripts/installed/pre-push`, both tracked, both registered in
`scripts/installed_registry.py`, and both UNINSTALLED: until someone runs the
install command, this file changes nothing.
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
import json
import os
import re
import resource
import shutil
import signal
import subprocess
import sys
import traceback as _traceback
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, Sequence

REPO = Path(__file__).resolve().parents[1]

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"

#: THE EXIT-CODE CONTRACT. Written as four named literals rather than as one
#: dictionary, because `sdk/tests/test_lab_check.py::TheExitCodeContractIsPinned`
#: asserts these NUMBERS. Every whole-runner assertion in that file used to read
#: `assertEqual(rc, lc.EXIT[lc.FAIL])`, which compares a subprocess's exit code
#: against the module-under-test's own dictionary: mutating the dictionary moves
#: both sides together, so `{PASS: 0, FAIL: 77, UNKNOWN: 99}` left 25 of 25
#: tests green while `scripts/installed/pre-push`, which reads the numbers
#: directly, fell through to its out-of-contract arm on every FAIL. A contract
#: shared by two files and pinned in neither is not a contract.
EXIT_PASS = 0
EXIT_FAIL = 1
#: UNKNOWN ABOUT REACH -- the runner knows exactly what it did and did not
#: examine, and nothing a check emitted is in question. Non-blocking.
EXIT_UNKNOWN = 3
#: UNKNOWN ABOUT A CHECK'S OUTPUT -- a check was launched and did not come back
#: with a usable verdict (crashed, timed out, would not start, exited outside
#: the contract, or returned its own UNKNOWN). The runner does not know what it
#: would have found. BLOCKING: see WHY A CRASH BLOCKS in the module docstring.
EXIT_UNSOUND = 4

#: Kept for the three-valued verdict word. It does NOT carry the blocking
#: dimension and must not be used to compute an exit code; `exit_code()` is.
EXIT = {PASS: EXIT_PASS, FAIL: EXIT_FAIL, UNKNOWN: EXIT_UNKNOWN}

#: Directories the enumeration reads. Both are DIRECTORIES, not file lists:
#: a check added to either is picked up without editing this module.
CHECK_DIRS = ("scripts", "sdk/tests")

#: The exit-code contract this runner publishes. A check that wants a different
#: mapping states it by exiting with one of these.
EXIT_CONTRACT = {0: PASS, 1: FAIL, 2: FAIL, 3: UNKNOWN}

#: argv heads that spend core-minutes. Compute authorisation is Katie's.
SOLVER_HEADS = re.compile(
    r"^(simpleFoam|pimpleFoam|pisoFoam|potentialFoam|interFoam|rhoSimpleFoam|"
    r"snappyHexMesh|blockMesh|surfaceFeatureExtract|decomposePar|"
    r"reconstructPar|foamRun|mpirun|mpiexec|dafoam|vspaero|vsp|"
    r"checkMesh|renumberMesh|topoSet)\b")

#: Write primitives, in two classes because precision matters in exactly one
#: direction: a false SKIP is printed and costs coverage, a false ADMIT writes
#: into a tree ten agents are working in.
#:
#: `_WRITE_ANY` are names that mean a write whoever the receiver is.
#: `_WRITE_QUALIFIED` are names that only mean a write when the receiver names
#: the module -- `str.replace` and `list.remove` are ubiquitous, and an early
#: cut of this predicate skipped `self_audit.py` and `installed_registry.py`,
#: the two most important checks in the lab, on a `line.replace("\n", ...)`.
_WRITE_ANY = {
    "write_text", "write_bytes", "mkdir", "touch", "copytree", "rmtree",
    "makedirs", "symlink_to", "writestr", "savefig",
}
_WRITE_QUALIFIED = {
    "os": {"remove", "unlink", "rename", "replace", "rmdir", "chmod",
           "symlink", "mkdir", "makedirs", "truncate"},
    "shutil": {"copy", "copy2", "copyfile", "copytree", "move", "rmtree"},
}
#: A write inside a function that also makes a temporary directory is scoped to
#: that directory. `detect_overwrite_signature.py`'s self-test builds its whole
#: control corpus under `tempfile.mkdtemp`, and refusing to run it on that
#: basis would drop a working control for nothing.
_TEMPMAKERS = {"mkdtemp", "mkstemp", "TemporaryDirectory", "NamedTemporaryFile",
               "TemporaryFile"}
_WRITE_GIT = re.compile(r"^(add|commit|checkout|reset|stash|apply|rm|mv)$")


# ---------------------------------------------------------------------------
# Enumeration -- two frames, both derived, neither typed
# ---------------------------------------------------------------------------

def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True)


def tracked_frame(root: Path) -> tuple[list[str], str]:
    """`git ls-files` over the check directories. Returns (paths, note)."""
    proc = _git(root, "ls-files", "-z", "--", *CHECK_DIRS)
    if proc.returncode != 0:
        return [], f"git ls-files failed rc={proc.returncode}: {proc.stderr.strip()}"
    return sorted(p for p in proc.stdout.split("\0") if p), ""


def worktree_frame(root: Path) -> list[str]:
    """Everything on disk under the check directories, `__pycache__` aside."""
    out: list[str] = []
    for d in CHECK_DIRS:
        base = root / d
        if not base.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames
                           if x not in ("__pycache__", ".pytest_cache")]
            for fn in filenames:
                p = Path(dirpath, fn)
                out.append(str(p.relative_to(root)))
    return sorted(out)


# ---------------------------------------------------------------------------
# Admission -- predicates read out of the candidate's own source
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class Candidate:
    path: str
    frames: tuple[str, ...]          # ("tracked",), ("worktree",) or both
    kind: str = ""                   # python-check / pytest / shell / other
    admitted: bool = False
    reason: str = ""                 # why skipped, or why admitted
    evidence: str = ""
    predicates: dict = dataclasses.field(default_factory=dict)


def _guard_entry_names(tree: ast.Module) -> list[str]:
    """Names called inside the `if __name__ == "__main__"` guard."""
    names: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        src = ast.dump(node.test)
        if "__main__" not in src:
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                fn = sub.func
                if isinstance(fn, ast.Name):
                    names.append(fn.id)
                elif isinstance(fn, ast.Attribute):
                    names.append(fn.attr)
    return names


def _own_body(fn: ast.FunctionDef) -> Iterable[ast.AST]:
    """Walk `fn` WITHOUT descending into nested function definitions.

    A nested helper's `return 1` is not the program's exit path, and counting it
    is how `ugrid_to_foam.py` -- a mesh converter whose nested writer returns a
    string -- reads as a gate.
    """
    nested = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
    stack = [n for n in fn.body if not isinstance(n, nested)]
    while stack:
        node = stack.pop()
        yield node
        for child in ast.iter_child_nodes(node):
            if isinstance(child, nested):
                continue
            stack.append(child)


def _nonzero_exit(fn: ast.FunctionDef, src: str) -> str:
    """Source of the first exit in `fn` that is not the constant 0/None."""
    for node in _own_body(fn):
        if isinstance(node, ast.Return) and node.value is not None:
            v = node.value
            if isinstance(v, ast.Constant) and v.value in (0, None):
                continue
            return f"return {ast.get_source_segment(src, v)}"
        if isinstance(node, ast.Call):
            f = node.func
            is_exit = ((isinstance(f, ast.Attribute) and f.attr == "exit")
                       or (isinstance(f, ast.Name) and f.id in ("exit", "SystemExit")))
            if is_exit and node.args:
                a = node.args[0]
                if isinstance(a, ast.Constant) and a.value in (0, None):
                    continue
                return f"exit({ast.get_source_segment(src, a)})"
        if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
            f = node.exc.func
            if isinstance(f, ast.Name) and f.id == "SystemExit" and node.exc.args:
                a = node.exc.args[0]
                if isinstance(a, ast.Constant) and a.value in (0, None):
                    continue
                return f"raise SystemExit({ast.get_source_segment(src, a)})"
    return ""


def _required_positional(fn: ast.FunctionDef, tree: ast.Module, src: str) -> str:
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"
                and node.args):
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str) \
                    and not first.value.startswith("-"):
                kw = {k.arg for k in node.keywords}
                if "nargs" in kw:
                    for k in node.keywords:
                        if k.arg == "nargs" and isinstance(k.value, ast.Constant) \
                                and k.value.value in ("?", "*"):
                            break
                    else:
                        return f"argparse positional {first.value!r}"
                    continue
                return f"argparse positional {first.value!r}"
        if (isinstance(node, ast.Subscript)
                and isinstance(node.value, ast.Attribute)
                and node.value.attr == "argv"
                and isinstance(node.slice, ast.Constant)
                and node.slice.value == 1):
            return "reads sys.argv[1]"
    return ""


def _compute_call(tree: ast.Module, src: str) -> str:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = getattr(f, "attr", None) or getattr(f, "id", None)
        if name not in ("run", "Popen", "check_output", "call", "check_call",
                        "system"):
            continue
        if not node.args:
            continue
        head = node.args[0]
        cand = None
        if isinstance(head, (ast.List, ast.Tuple)) and head.elts:
            e = head.elts[0]
            if isinstance(e, ast.Constant) and isinstance(e.value, str):
                cand = Path(e.value).name
        elif isinstance(head, ast.Constant) and isinstance(head.value, str):
            cand = head.value.strip().split()[0] if head.value.strip() else None
            cand = Path(cand).name if cand else None
        if cand and SOLVER_HEADS.match(cand):
            return f"line {node.lineno}: subprocess head {cand!r}"
    return ""


def _is_write_call(node: ast.Call) -> str:
    """Name the write this call performs, or "" if it performs none."""
    f = node.func
    name = getattr(f, "attr", None) or getattr(f, "id", None)
    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
        mod = f.value.id
        if name in _WRITE_QUALIFIED.get(mod, ()):  # os.remove, shutil.move
            return f"{mod}.{name}(...)"
    if name in _WRITE_ANY:
        return f"{name}(...)"
    if name == "open":
        # open(path, "w") and Path.open("w") -- the mode sits in a different
        # argument position in each.
        pos = 1 if isinstance(f, ast.Name) else 0
        if len(node.args) > pos:
            m = node.args[pos]
            if isinstance(m, ast.Constant) and isinstance(m.value, str) \
                    and any(c in m.value for c in "wax+"):
                return f"open(..., {m.value!r})"
    if name in ("run", "Popen", "check_output", "call", "check_call") \
            and node.args and isinstance(node.args[0], (ast.List, ast.Tuple)):
        elts = [e.value for e in node.args[0].elts
                if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        if elts and Path(elts[0]).name == "git":
            for tok in elts[1:]:
                if _WRITE_GIT.match(tok):
                    return f"subprocess git {tok}"
    return ""


def _receiver_is_cli_arg(node: ast.Call) -> bool:
    """`args.json.write_text(...)` -- a write that only happens if asked for.

    This runner passes no arguments, so a write reachable only through an
    option it does not pass cannot fire. `fail_open_scan.py` is the instance.
    """
    f = node.func
    while isinstance(f, ast.Attribute):
        f = f.value
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) \
                and f.value.id in ("args", "opts", "ns"):
            return True
        if isinstance(f, ast.Name) and f.id in ("args", "opts", "ns"):
            return True
    return False


def _write_primitive(tree: ast.Module, src: str) -> str:
    """First write this module performs that is neither temp-scoped nor CLI-gated."""
    scopes: list[tuple[ast.AST, bool]] = []
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            temps = any(
                isinstance(n, ast.Call)
                and (getattr(n.func, "attr", None) or getattr(n.func, "id", None))
                in _TEMPMAKERS for n in ast.walk(fn))
            scopes.append((fn, temps))
    for fn, temp_scoped in scopes:
        if temp_scoped:
            continue
        for node in ast.walk(fn):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and node is not fn:
                continue
            if not isinstance(node, ast.Call):
                continue
            what = _is_write_call(node)
            if what and not _receiver_is_cli_arg(node):
                # A write in a temp-scoped enclosing function is exempt; walk
                # up by checking whether any temp-scoped scope contains it.
                if any(t and any(n is node for n in ast.walk(s))
                       for s, t in scopes):
                    continue
                return f"line {node.lineno}: {what}"
    return ""


def classify(root: Path, cand: Candidate, *, allow_writers: bool) -> Candidate:
    """Decide, from the candidate's own source, whether it is a runnable check."""
    p = root / cand.path
    name = Path(cand.path).name

    if cand.path.startswith("sdk/tests/") and name.startswith("test_") \
            and name.endswith(".py"):
        cand.kind = "pytest"
        cand.admitted = True
        cand.reason = "pytest test file (run inside the one suite invocation)"
        return cand

    if Path(cand.path).resolve() == Path(__file__).resolve():
        cand.kind = "runner"
        cand.reason = "the runner itself"
        return cand

    if p.suffix in (".sh", ".ps1"):
        cand.kind = "shell"
        cand.reason = ("shell: no exit contract this runner can read, and this "
                       "directory's shell files are actuators (auto-stop powers "
                       "the box off, launch_solve spends core-hours)")
        return cand

    if p.suffix != ".py":
        cand.kind = "other"
        cand.reason = "not an executable module (data, prose or fixture)"
        return cand

    if not p.exists():
        cand.kind = "python"
        cand.reason = "tracked but absent from the worktree"
        return cand

    try:
        src = p.read_text(errors="replace")
        tree = ast.parse(src)
    except (OSError, SyntaxError) as exc:
        cand.kind = "python"
        cand.reason = f"unparseable: {type(exc).__name__}: {exc}"
        return cand

    cand.kind = "python"
    entries = _guard_entry_names(tree)
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    entry = next((funcs[n] for n in entries if n in funcs), None)
    cand.predicates["entry"] = entry.name if entry else None
    if entry is None:
        cand.reason = ("no-entry-point: no `if __name__ == \"__main__\"` guard "
                       "calling a module-level function")
        return cand

    nz = _nonzero_exit(entry, src)
    cand.predicates["can_fail"] = nz or False
    if not nz:
        cand.reason = ("cannot-fail: every exit from %s() is the constant 0, so "
                       "no finding can redden it (D64's own criterion)"
                       % entry.name)
        return cand

    need = _required_positional(entry, tree, src)
    cand.predicates["requires_args"] = need or False
    if need:
        cand.reason = f"requires-arguments: {need}"
        return cand

    comp = _compute_call(tree, src)
    cand.predicates["needs_compute"] = comp or False
    if comp:
        cand.reason = f"needs-compute: {comp} -- compute authorisation is Katie's"
        return cand

    wr = _write_primitive(tree, src)
    cand.predicates["writes"] = wr or False
    if wr and not allow_writers:
        cand.reason = (f"writes-to-tree: {wr} -- not run against the live tree; "
                       f"admitted under --tree snapshot")
        return cand

    cand.admitted = True
    cand.evidence = nz
    cand.reason = f"gate: {entry.name}() can exit non-zero ({nz})"
    return cand


def enumerate_candidates(root: Path, *, allow_writers: bool
                         ) -> tuple[list[Candidate], dict]:
    tracked, note = tracked_frame(root)
    disk = worktree_frame(root)
    tset, dset = set(tracked), set(disk)
    cands: dict[str, Candidate] = {}
    for pth in sorted(tset | dset):
        frames = tuple(f for f, s in (("tracked", tset), ("worktree", dset))
                       if pth in s)
        cands[pth] = Candidate(path=pth, frames=frames)
    out = [classify(root, c, allow_writers=allow_writers)
           for c in cands.values()]
    frame = {
        "how": "git ls-files + os.walk over " + ", ".join(CHECK_DIRS)
               + " (never the shell's grep/find)",
        "tracked": len(tset),
        "worktree": len(dset),
        "untracked_only": sorted(dset - tset),
        "tracked_only": sorted(tset - dset),
        "git_note": note,
    }
    return out, frame


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class Outcome:
    name: str
    verdict: str
    reason: str
    seconds: float = 0.0
    cpu: float = 0.0
    code: int | None = None
    stderr_lines: int = 0
    stderr_tail: str = ""
    detail: list[str] = dataclasses.field(default_factory=list)
    #: True when this outcome leaves the runner not knowing what the check
    #: would have found -- see THE GRADED PARTY MUST NOT CONTROL THE PREDICATE
    #: in the module docstring. Set at the point the verdict is manufactured,
    #: never derived from the verdict word afterwards, so that "UNKNOWN about a
    #: check's output" and "UNKNOWN about the runner's reach" cannot be
    #: confused by a later reader.
    blocking: bool = False


def _cpu_children() -> float:
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime + r.ru_stime


def _tree_state(root: Path) -> set[str]:
    return set(_git(root, "status", "--porcelain").stdout.splitlines())


def run_script(root: Path, cand: Candidate, timeout: int, *,
               exclusive: bool = False) -> Outcome:
    """Run one script gate, and OBSERVE whether it wrote to the tree.

    The static write predicate predicts; this measures. A check that changes
    tracked or untracked state is reported by name with the paths it touched,
    and its verdict is downgraded to UNKNOWN -- an exit code that grades a write
    the runner caused is not a finding about the lab.
    """
    before = _tree_state(root)
    t0, c0 = time.monotonic(), _cpu_children()
    argv = [sys.executable, str(root / cand.path)]
    try:
        proc = subprocess.run(argv, cwd=str(root), capture_output=True,
                              text=True, timeout=timeout)
        code, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        err = (exc.stderr or b"").decode(errors="replace") \
            if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return Outcome(cand.path, UNKNOWN,
                       f"timed out after {timeout}s -- no verdict was produced",
                       time.monotonic() - t0, _cpu_children() - c0, None,
                       len(err.splitlines()), _tail(err), blocking=True)
    except OSError as exc:
        return Outcome(cand.path, UNKNOWN, f"could not launch: {exc}",
                       time.monotonic() - t0, _cpu_children() - c0,
                       blocking=True)

    secs, cpu = time.monotonic() - t0, _cpu_children() - c0
    reported = _scrape_verdicts(out)
    # THE STDERR SUBSTRING IS NOT ENOUGH ON ITS OWN (F0, docket D101). `err` is
    # the CHECK'S OWN stderr and the check controls every byte of it, so this
    # predicate alone let the graded party decide whether it had been graded:
    # one `sys.stderr.write("Traceback (most recent call last)\n")` turned FAIL
    # / exit 1 / push blocked into UNKNOWN / exit 3 / push allowed, with the
    # finding still printed on stdout. A check that got as far as reporting a
    # verdict did not fail to start, and that report stands whatever it wrote
    # afterwards. This is the same "did it report anything?" standard
    # `usage_error` below has always carried; it was simply missing here.
    #
    # The bar is A REPORTED VERDICT, not "any stdout at all": a check that
    # prints its frame and then dies really has crashed, and calling that FAIL
    # is how a broken instrument gets read as a finding. `_scrape_verdicts`
    # already knows the three shapes a check in this repository reports in, so
    # the bar is the same one the runner uses to display sub-results -- no
    # second, quietly different notion of "it said something".
    crashed = "Traceback (most recent call last)" in err and not reported
    # argparse writes `usage: ...` and exits 2 when the invocation is wrong.
    # That is a statement about how THIS RUNNER called the check -- it passes no
    # arguments -- and reading it as a finding would manufacture red exactly as
    # readily as a swallowed error manufactures green.
    # `detect_overwrite_signature.py` (which wants a directory or --self-test)
    # prints argparse's own `usage:`; `sweep.py`, which deliberately has no
    # default frame, prints its own sentence instead and was read as FAIL by the
    # first two cuts of this runner. The general form catches both without
    # matching either by name: A CHECK THAT PRINTED NOTHING ON STDOUT NEVER GOT
    # AS FAR AS REPORTING. Every check in this repository prints its frame or
    # its verdict before it decides anything, so silence on stdout with a
    # complaint on stderr is a failure to start, not a finding.
    #
    # AND IT BLOCKS, WHICH IT DID NOT BEFORE (F0, docket D101). Every word of
    # this diagnosis is written by the graded check: `code`, `out` and `err`
    # are all its own. A check that would have exited 1 could instead exit 2
    # with an empty stdout and one word on stderr, and under the old mapping
    # that traded a blocking FAIL for a non-blocking UNKNOWN -- a strict
    # improvement bought by printing less. There is no signal here the check
    # does not control, so the hole cannot be closed by a better predicate;
    # it is closed by making the escape lead somewhere no better than FAIL.
    # The verdict stays UNKNOWN, because that is what is true, and the exit
    # code says BLOCKING, because "this check did not run and I cannot tell
    # you why not, in its own words" is not a state to push on top of.
    usage_error = code == 2 and (re.match(r"\s*usage:", err)
                                 or (not out.strip() and err.strip()))
    if usage_error:
        v, why = UNKNOWN, ("exited 2 on invocation, before reporting anything "
                           "on stdout: it requires arguments and this runner "
                           "passes none by design. A statement about the "
                           "runner, not about the lab -- but a BLOCKING one, "
                           "because nothing about it is outside this check's "
                           "control. Give it a schedulable default frame, or "
                           "make it exit 3 on purpose, or make the argument "
                           "REQUIRED so the static predicate skips it before "
                           "it is ever launched")
    elif crashed and code != 0:
        v, why = UNKNOWN, ("the check crashed; a traceback is a statement about "
                           "the instrument, not about the lab -- and it BLOCKS: "
                           "a check that crashed is the check most likely to be "
                           "hiding something, and the runner cannot say what it "
                           "would have found")
    else:
        v = EXIT_CONTRACT.get(code, UNKNOWN)
        why = {PASS: "exit 0", FAIL: f"exit {code}",
               UNKNOWN: f"exit {code} (outside the published contract)"}[v]
    # Every UNKNOWN reachable from here is UNKNOWN ABOUT THIS CHECK'S OUTPUT --
    # it ran (or was launched) and did not come back with a usable verdict --
    # which is the class the graded party controls and therefore the class that
    # must not pay. UNKNOWN about the runner's REACH never passes through
    # `run_script`; it comes from the skip list, and it does not block.
    blocking = v == UNKNOWN
    detail = list(reported)
    touched = sorted(_tree_state(root) - before)
    if touched:
        detail = [f"TREE CHANGED DURING THIS CHECK: {t}" for t in touched[:8]] \
            + detail
        if exclusive:
            v, blocking = UNKNOWN, True
            why = (f"{why}, but the check changed {len(touched)} path(s) in the "
                   f"tree; its exit code is not a clean finding")
        else:
            detail.insert(0, "(live tree: other agents write here too, so this "
                             "is reported and not charged to the check)")
    return Outcome(cand.path, v, why, secs, cpu, code,
                   len(err.splitlines()), _tail(err), detail=detail,
                   blocking=blocking)


_VERDICT_LINE = re.compile(
    r"^\s*(?:\[(PASS|FAIL|WARN|INFO|UNKNOWN)\]|VERDICT:\s*(\S+))\s*(.*)$")

#: A bare status word at the start of a line, which is the third shape a check
#: in this repository reports in. It matters more than it looks: the auto-stop
#: repair of D65 sits in the registry as `PENDING`, the registry exits 0 on a
#: declared PENDING, and a runner that printed only the exit code would show
#: `[PASS] installed_registry.py` and hide the fact that the box is running an
#: uninstalled power gate. A declared divergence must stay loud.
_STATUS_WORD = re.compile(
    r"^(PENDING|DRIFT|DANGLING|STALE|GHOST|ABSENT|RED|BLIND|WARNING)\s+\S")


def _scrape_verdicts(out: str) -> list[str]:
    """Generic sub-verdict scrape. No per-check adapter lives in this module.

    `self_audit.py` prints `[FAIL] name  summary`; `withdrawal_sweep.py` and
    `check_absolutes.py` print `VERDICT: X`; `installed_registry.py` prints
    `PENDING  auto-stop gate ...`. All three shapes are read the same way, so a
    new check that prints any of them gets its sub-results reported for free and
    one that prints none loses nothing but detail.
    """
    hits: list[str] = []
    for line in out.splitlines():
        m = _VERDICT_LINE.match(line)
        if m and (m.group(1) in ("FAIL", "WARN", "UNKNOWN")
                  or (m.group(2) and m.group(2) not in ("PASS", "CLEAN",
                                                        "MATCHES"))):
            hits.append(line.strip()[:160])
        elif _STATUS_WORD.match(line):
            hits.append(line.strip()[:160])
    return hits[:40]


def _tail(text: str, n: int = 12) -> str:
    lines = [l for l in text.splitlines() if l.strip()]
    return "\n".join(lines[-n:])


def purge_pycache(root: Path) -> int:
    """Stale bytecode has INVERTED mutation results in this lab (see docstring)."""
    n = 0
    for dirpath, dirnames, _ in os.walk(root):
        if ".git" in dirnames:
            dirnames.remove(".git")
        for d in list(dirnames):
            if d == "__pycache__":
                shutil.rmtree(Path(dirpath, d), ignore_errors=True)
                dirnames.remove(d)
                n += 1
    return n


def run_pytest(root: Path, files: Sequence[str], timeout: int,
               target: Sequence[str] | None = None) -> tuple[Outcome, dict]:
    """One invocation over the whole directory; per-file verdicts from junit XML.

    The suite is run over the DIRECTORY, not over the enumerated file list, and
    then the two are diffed. That is the direct answer to `7bf55c90`: a run of
    one file labelled "Full suite". A file that this runner enumerated and that
    the suite did not collect is reported by name and read as UNKNOWN.
    """
    purged = purge_pycache(root)
    xml = Path(tempfile.mkstemp(prefix="lab_check_junit_", suffix=".xml")[1])
    argv = [sys.executable, "-m", "pytest", *(target or ["sdk/tests"]), "-q",
            "-p", "no:cacheprovider", f"--junitxml={xml}"]
    t0, c0 = time.monotonic(), _cpu_children()
    try:
        proc = subprocess.run(argv, cwd=str(root), capture_output=True,
                              text=True, timeout=timeout)
        code, err = proc.returncode, proc.stderr
    except subprocess.TimeoutExpired:
        return (Outcome("sdk/tests (pytest)", UNKNOWN,
                        f"suite timed out after {timeout}s",
                        time.monotonic() - t0, _cpu_children() - c0,
                        blocking=True),
                {"purged_pycache_dirs": purged})
    except OSError as exc:
        return (Outcome("sdk/tests (pytest)", UNKNOWN, f"could not launch: {exc}",
                        time.monotonic() - t0, _cpu_children() - c0,
                        blocking=True),
                {"purged_pycache_dirs": purged})
    secs, cpu = time.monotonic() - t0, _cpu_children() - c0

    per_file: dict[str, dict] = {}
    total = fails = errors = skips = 0
    parse_note = ""
    # pytest 9's junit writer emits no `file` attribute for unittest-style
    # classes -- only `classname`, e.g. `sdk.tests.test_planted.T`. Mapping a
    # case back to the file it came from is what makes "enumerated but not
    # collected" possible, so it is done from whichever of the two is present.
    by_stem = {Path(p).stem: p for p in files}
    try:
        root_el = ET.parse(xml).getroot()
        for case in root_el.iter("testcase"):
            f = case.get("file") or ""
            if not f:
                for part in reversed((case.get("classname") or "").split(".")):
                    if part in by_stem:
                        f = by_stem[part]
                        break
            d = per_file.setdefault(f, {"tests": 0, "fail": 0, "error": 0,
                                        "skip": 0})
            d["tests"] += 1
            total += 1
            for child in case:
                if child.tag == "failure":
                    d["fail"] += 1
                    fails += 1
                elif child.tag == "error":
                    d["error"] += 1
                    errors += 1
                elif child.tag == "skipped":
                    d["skip"] += 1
                    skips += 1
    except (OSError, ET.ParseError) as exc:
        parse_note = f"junit XML unreadable: {exc}"
    finally:
        xml.unlink(missing_ok=True)

    enumerated = set(files)
    collected = {f for f in per_file if f}
    missing = sorted(enumerated - collected)
    extra = sorted(collected - enumerated)

    # `blocking` is set per branch rather than derived from `v`, because the two
    # UNKNOWNs this function can produce are on opposite sides of the control
    # boundary (see the module docstring): a suite that would not run or would
    # not parse is UNKNOWN ABOUT ITS OUTPUT and blocks; an enumerated file that
    # declares no test is UNKNOWN ABOUT REACH and must not, or the runner earns
    # a permanent false alarm on every helper named `test_*.py` and gets
    # switched off, which is L-84's warning with the sign flipped.
    blocking = False
    if parse_note or (total == 0 and code != 0):
        v, why = UNKNOWN, parse_note or f"no tests were collected (rc={code})"
        blocking = True
    elif total == 0:
        v, why = UNKNOWN, "zero tests collected -- an empty suite is not a pass"
        blocking = True
    elif fails or errors:
        v = FAIL if fails else UNKNOWN
        blocking = not fails
        why = f"{fails} failed, {errors} errored, out of {total}"
    elif missing:
        # A file that DECLARES tests and contributed none is a defect in the
        # check corpus, not an uncertainty about it -- `7bf55c90`'s shape, and
        # D62's class. A file that declares none (a helper that happens to be
        # named test_*) is only an uncertainty, and reading the two the same way
        # is how a runner earns a permanent false alarm and gets switched off.
        declaring = [f for f in missing
                     if re.search(r"def test_|TestCase|@pytest",
                                  (root / f).read_text(errors="replace"))]
        if declaring:
            v = FAIL
            why = (f"{len(declaring)} test file(s) declare tests and "
                   f"contributed none to this run")
        else:
            v = UNKNOWN
            # REACH, not output: the suite ran, everything it collected passed,
            # and the runner is telling you which enumerated files contributed
            # nothing. Nothing is hidden, so this does not block.
            why = (f"{len(missing)} enumerated test file(s) produced no "
                   f"collected test (none of them declares a test)")
    else:
        v, why = EXIT_CONTRACT.get(code, UNKNOWN), f"{total} tests, exit {code}"
        if v is PASS and code != 0:
            v = UNKNOWN
        blocking = v == UNKNOWN

    detail = []
    for f in missing:
        detail.append(f"enumerated but not collected: {f}")
    for f in extra:
        detail.append(f"collected but not enumerated: {f}")
    for f, d in sorted(per_file.items()):
        if d["fail"] or d["error"]:
            detail.append(f"{f}: {d['fail']} failed, {d['error']} errored, "
                          f"{d['tests']} tests")
    frame = {
        "files_enumerated": len(enumerated),
        "files_collected": len(collected),
        "files_missing": missing,
        "tests_collected": total,
        "failed": fails, "errored": errors, "skipped": skips,
        "purged_pycache_dirs": purged,
        "argv": " ".join(argv),
    }
    return (Outcome("sdk/tests (pytest)", v, why, secs, cpu, code,
                    len(err.splitlines()), _tail(err), detail,
                    blocking=blocking), frame)


# ---------------------------------------------------------------------------
# Snapshot tree
# ---------------------------------------------------------------------------

def make_snapshot(root: Path) -> tuple[Path, str]:
    tmp = Path(tempfile.mkdtemp(prefix="lab_check_snapshot_"))
    wt = tmp / "tree"
    proc = _git(root, "worktree", "add", "--detach", str(wt), "HEAD")
    if proc.returncode != 0:
        raise RuntimeError(f"git worktree add failed: {proc.stderr.strip()}")
    head = _git(root, "rev-parse", "--short", "HEAD").stdout.strip()
    return wt, head


def drop_snapshot(root: Path, wt: Path) -> None:
    _git(root, "worktree", "remove", "--force", str(wt))
    shutil.rmtree(wt.parent, ignore_errors=True)


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

def aggregate(outcomes: Sequence[Outcome], skipped_hiding: Sequence[Candidate]
              ) -> tuple[str, list[str], bool]:
    """(verdict, reasons, blocking).

    `blocking` is the second half of the F0 repair and it is NOT a function of
    the verdict word. It answers a different question -- *is there a check whose
    finding this run cannot state?* -- and it is what the exit code and the
    pre-push hook act on. See THE GRADED PARTY MUST NOT CONTROL THE PREDICATE
    in the module docstring for why the two questions had to be separated.
    """
    reasons: list[str] = []
    if not outcomes:
        # B1, the silent-zero sweep: examined nothing, reported clean. This is
        # the class the lab ranks highest, so it blocks as well as reading
        # UNKNOWN -- a run that checked nothing must not be pushable as though
        # it had.
        return UNKNOWN, ["no check was admitted -- an empty check set is not a "
                         "pass (defect class B1, the silent-zero sweep)"], True
    fails = [o for o in outcomes if o.verdict == FAIL]
    unks = [o for o in outcomes if o.verdict == UNKNOWN]
    for o in fails:
        reasons.append(f"FAIL {o.name}: {o.reason}")
    for o in unks:
        reasons.append(f"{'BLOCKING ' if o.blocking else ''}UNKNOWN {o.name}: "
                       f"{o.reason}")
    for c in skipped_hiding:
        reasons.append(f"UNKNOWN {c.path}: skipped -- {c.reason}")
    blocking = bool(fails) or any(o.blocking for o in outcomes)
    if fails:
        return FAIL, reasons, blocking
    if unks or skipped_hiding:
        return UNKNOWN, reasons, blocking
    return PASS, [f"{len(outcomes)} check(s) ran, every one returned PASS"], False


def exit_code(verdict: str, blocking: bool) -> int:
    """THE ONLY PLACE A VERDICT BECOMES A NUMBER.

    Pinned as literals by `sdk/tests/test_lab_check.py::TheExitCodeContractIsPinned`,
    and consumed by `scripts/installed/pre-push`, whose behaviour on each of
    these four codes is asserted by RUNNING it against a stub runner.
    """
    if verdict == PASS:
        return EXIT_PASS
    if verdict == FAIL:
        return EXIT_FAIL
    return EXIT_UNSOUND if blocking else EXIT_UNKNOWN


#: Skip reasons that could be hiding a verdict, so they downgrade a PASS to
#: UNKNOWN rather than being silently forgiven. `needs-compute` is the sharp
#: one: the check exists, it would have an answer, and this runner is not
#: allowed to buy it.
HIDING_PREFIXES = ("needs-compute:", "writes-to-tree:", "unparseable:",
                   "tracked but absent")


# ---------------------------------------------------------------------------
# Streaming -- see THE REPORT IS STREAMED in the module docstring (D148)
# ---------------------------------------------------------------------------

#: The four markers, at column 0 so `grep -c '^LAB-CHECK-END'` over an appended
#: log counts finished runs. They are typed as literals HERE and as literals
#: again in `sdk/tests/test_lab_check.py`, for the reason the exit codes are:
#: a test that asks the module under test what the marker is has pinned nothing.
MARK_BEGIN = "LAB-CHECK-BEGIN"
MARK_PLAN = "LAB-CHECK-PLAN"
MARK_END = "LAB-CHECK-END"
#: The in-flight line. Indented, because it belongs to the CHECKS RUN block and
#: is read positionally (last one without a verdict under it), not counted.
MARK_RUNNING = ">>"


class _Interrupted(Exception):
    """A signal the runner caught. Carries the number so the log can name it."""

    def __init__(self, signum: int):
        self.signum = signum
        self.name = signal.Signals(signum).name
        super().__init__(self.name)


def _install_interrupt_handlers() -> None:
    """Catch SIGTERM and SIGINT so the run can say it was interrupted.

    RAISING rather than exiting from the handler is deliberate: the handler
    runs in the main thread, so the exception propagates out of whatever
    `subprocess.run` is blocked in a check, and `subprocess.run`'s own bare
    `except:` arm kills that child on the way out. Exiting from the handler
    would leave a check process orphaned, still holding whatever it holds.
    """
    def handler(signum, _frame):
        raise _Interrupted(signum)

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, handler)
        except (ValueError, OSError):    # not the main thread; nothing to do
            pass


@dataclasses.dataclass
class Progress:
    """What the run has got through so far, readable at any instant.

    This exists so the terminator can state `ran=k/n` on the interrupted path,
    where `n` was fixed and printed before the first check started. A partial
    run that could not say what it was aiming at would be only half repaired.
    """
    expected: int = 0
    completed: int = 0
    in_flight: str = ""
    outcomes: list = dataclasses.field(default_factory=list)

    def start(self, name: str) -> None:
        self.in_flight = name

    def finish(self, outcome: "Outcome") -> None:
        self.outcomes.append(outcome)
        self.completed += 1
        self.in_flight = ""


class Report:
    """One line at a time, flushed at the moment it is produced.

    The flush is the whole point on the cron path: `stdout` redirected to a log
    is BLOCK buffered, so a run killed at minute 19 would lose the last several
    KB it believed it had written. Nothing here accumulates.
    """

    def __init__(self, stream):
        self.stream = stream

    def line(self, text: str = "") -> None:
        self.stream.write(text + "\n")
        self.stream.flush()

    def begin(self, args_desc: str) -> None:
        self.line(f"{MARK_BEGIN} {time.strftime('%Y-%m-%dT%H:%M:%S%z')} "
                  f"pid={os.getpid()} argv={args_desc}")
        self.line(f"  This report is STREAMED as it is produced, and it is "
                  f"COMPLETE only if it ends")
        self.line(f"  with a `{MARK_END} COMPLETE` line. A log that stops "
                  f"before one is a run that")
        self.line(f"  was interrupted, NOT a run that found nothing "
                  f"(docket D148).")

    def plan(self, names: Sequence[str], note: str) -> None:
        self.line(f"{MARK_PLAN} expected={len(names)} -- {note}")
        for n in names:
            self.line(f"  will run  {n}")
        self.line("")

    def end_complete(self, verdict: str, rc: int, prog: Progress,
                     elapsed: float) -> None:
        self.line(f"{MARK_END} COMPLETE verdict={verdict} exit={rc} "
                  f"ran={prog.completed}/{prog.expected} "
                  f"elapsed={elapsed:.1f}s")

    def end_incomplete(self, cause: str, prog: Progress, elapsed: float,
                       rc: int) -> None:
        """The line that makes a truncated log unmistakable.

        `INCOMPLETE` is stated, not implied, and `ran=k/n` against the `n`
        printed in the plan line says how much of the lab this log covers.
        """
        self.line("")
        self.line("=" * 78)
        self.line(f"VERDICT: {UNKNOWN}")
        self.line(f"  THIS RUN DID NOT FINISH: {cause}")
        self.line(f"  {prog.completed} of {prog.expected} check unit(s) "
                  f"completed. Their results are above this line and are "
                  f"good; ")
        self.line(f"  the remaining "
                  f"{max(prog.expected - prog.completed, 0)} were NOT RUN and "
                  f"this run says nothing about them.")
        if prog.in_flight:
            self.line(f"  IN FLIGHT WHEN INTERRUPTED: {prog.in_flight} "
                      f"-- no verdict was produced for it.")
        self.line(f"  exit {rc} -- BLOCKING, and it is UNKNOWN about those "
                  f"checks' output, not about reach.")
        self.line(f"  NOTE: under `timeout` the shell sees 124 and not {rc}; "
                  f"`timeout` reports its own")
        self.line(f"  code whatever the runner chose, which is why the "
                  f"{MARK_END} line below is the")
        self.line(f"  channel that carries this and the exit code is not.")
        self.line("=" * 78)
        self.line(f"{MARK_END} INCOMPLETE cause={cause.split()[0]} "
                  f"ran={prog.completed}/{prog.expected} "
                  f"in-flight={prog.in_flight or '(none)'} "
                  f"elapsed={elapsed:.1f}s")


def _emit_outcome(rep: Report, o: Outcome, prog: Progress) -> None:
    """One check's block, written the instant that check returns."""
    rep.line(f"  [{o.verdict:<7}] {o.name}")
    rep.line(f"            {o.reason}   "
             f"({o.seconds:.1f}s wall, {o.cpu:.1f}s cpu)")
    for d in o.detail[:25]:
        rep.line(f"            - {d}")
    if len(o.detail) > 25:
        # Silent truncation is the class this module exists to close.
        rep.line(f"            - ... and {len(o.detail) - 25} "
                 f"further sub-result line(s), not shown")
    if o.stderr_lines:
        rep.line(f"            stderr ({o.stderr_lines} lines, NOT discarded):")
        for l in o.stderr_tail.splitlines():
            rep.line(f"              | {l[:150]}")


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="lab_check",
        description="One entry point: enumerate every check this lab has, run "
                    "what is safe to run, return PASS/FAIL/UNKNOWN.")
    p.add_argument("--root", default=str(REPO))
    p.add_argument("--tree", choices=("live", "snapshot"), default="live",
                   help="live: the working tree. snapshot: a git worktree of "
                        "HEAD, in which write-capable checks are admitted")
    p.add_argument("--list", action="store_true",
                   help="enumerate and classify, run nothing")
    p.add_argument("--admit-writers", action="store_true",
                   help="admit write-capable checks against the live tree. "
                        "Only meaningful when the tree is yours: in this "
                        "repository ten agents write concurrently, which is "
                        "why it is not the default. --tree snapshot implies it")
    p.add_argument("--no-tests", action="store_true",
                   help="skip the pytest group (the fast tier)")
    p.add_argument("--only", default=None,
                   help="substring filter over candidate paths")
    p.add_argument("--timeout", type=int, default=600,
                   help="per-script timeout in seconds")
    p.add_argument("--suite-timeout", type=int, default=3600)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    # STREAMED, AND THE STREAM IS CHOSEN BY MODE. In `--json` the document on
    # stdout has to stay ONE parseable object, so the narration goes to stderr
    # -- where the cron line's `2>&1` puts it in the same log anyway, and where
    # an interrupted `--json` run still leaves its markers. In every other mode
    # the narration IS the output and goes to stdout, unchanged in shape.
    rep = Report(sys.stderr if args.json else sys.stdout)
    _install_interrupt_handlers()
    prog = Progress()
    t_start = time.monotonic()

    rep.line("=" * 78)
    rep.line("LAB CHECK -- one entry point, three-valued  (docket D64)")
    rep.line("=" * 78)
    rep.begin(" ".join(sys.argv[1:] if argv is None else argv) or "(none)")
    rep.line("")

    try:
        verdict, rc = _execute(rep, args, prog)
    except _Interrupted as exc:
        # SIGTERM (what `timeout` sends, and what D148's artifact came from) or
        # SIGINT (a person at a terminal). Everything above this line is real.
        _interrupted_exit(rep, args, prog, t_start,
                          f"{exc.name} was received and the run stopped there")
        return EXIT_UNSOUND
    except KeyboardInterrupt:
        # Reachable only in the window before the handler is installed, or if
        # the interpreter is not on the main thread. Same treatment.
        _interrupted_exit(rep, args, prog, t_start,
                          "KeyboardInterrupt was received and the run stopped "
                          "there")
        return EXIT_UNSOUND
    except BrokenPipeError:
        # THE READER HUNG UP (`lab_check.py | head`). There is nobody left to
        # tell, so nothing is written -- but the report IS truncated, so this
        # exits BLOCKING like every other unfinished run, and the log ends
        # without a terminator, which is exactly the true statement about it.
        # stdout is redirected to /dev/null first or the interpreter's own
        # shutdown flush raises again and turns this into a bare exit 120.
        try:
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        except OSError:
            pass
        return EXIT_UNSOUND
    except Exception:
        # THE RUNNER ITSELF CRASHED. This used to be an uncaught traceback and
        # a Python exit 1 -- which is EXIT_FAIL, so a broken instrument was
        # reported in the vocabulary of a finding about the lab, and every line
        # it had already produced was lost with it. It is UNKNOWN about the
        # checks that never ran, it BLOCKS, and the traceback is printed rather
        # than swallowed.
        rep.line("")
        rep.line("RUNNER TRACEBACK -- this is the instrument, not the lab:")
        for l in _traceback.format_exc().splitlines():
            rep.line(f"  | {l}")
        _interrupted_exit(rep, args, prog, t_start,
                          "an unhandled exception inside the runner itself "
                          "(traceback above)")
        return EXIT_UNSOUND

    rep.end_complete(verdict, rc, prog, time.monotonic() - t_start)
    return rc


def _interrupted_exit(rep: Report, args, prog: Progress, t_start: float,
                      cause: str) -> None:
    rep.end_incomplete(cause, prog, time.monotonic() - t_start, EXIT_UNSOUND)
    if args.json:
        # stdout in `--json` mode carries a document or nothing. A partial run
        # gets a partial document, explicitly flagged, rather than silence.
        print(json.dumps({
            "verdict": UNKNOWN,
            "complete": False,
            "interrupted": cause,
            "blocking": True,
            "exit": EXIT_UNSOUND,
            "expected": prog.expected,
            "completed": prog.completed,
            "in_flight": prog.in_flight,
            "checks": [dataclasses.asdict(o) for o in prog.outcomes],
        }, indent=1), flush=True)


def _execute(rep: Report, args, prog: Progress) -> tuple[str, int]:
    """The run, streaming into `rep`. Returns (verdict, exit code)."""
    root = Path(args.root).resolve()
    snapshot = None
    head = _git(root, "rev-parse", "--short", "HEAD").stdout.strip() or "?"
    dirty = len([l for l in _git(root, "status", "--porcelain").stdout.splitlines()])
    tree_desc = f"live working tree ({dirty} path(s) modified or untracked)"

    if args.tree == "snapshot" and not args.list:
        try:
            snapshot, snap_head = make_snapshot(root)
        except RuntimeError as exc:
            rep.line(f"VERDICT: {UNKNOWN}\n  because the snapshot could not be "
                     f"made: {exc}\n  exit {EXIT_UNSOUND} -- BLOCKING: nothing "
                     f"was checked, and a run that checked nothing is not a "
                     f"pass")
            return UNKNOWN, EXIT_UNSOUND
        tree_desc = f"snapshot worktree of HEAD {snap_head} at {snapshot}"

    try:
        run_root = snapshot or root
        writers_ok = args.tree == "snapshot" or args.admit_writers
        cands, frame = enumerate_candidates(run_root, allow_writers=writers_ok)
        only_note = ""
        if args.only:
            kept = [c for c in cands if args.only in c.path]
            # A FILTERED RUN MUST NOT READ AS A FULL ONE. That is `7bf55c90`
            # exactly -- one test file's green labelled "Full suite" -- and it
            # would be indefensible for this module of all modules to repeat it.
            only_note = (f"--only {args.only!r} IN EFFECT: {len(kept)} of "
                         f"{len(cands)} candidates considered. This run is NOT "
                         f"a full check of this lab.")
            cands = kept

        admitted = [c for c in cands if c.admitted]
        scripts = [c for c in admitted if c.kind == "python"]
        tests = [c for c in admitted if c.kind == "pytest"]
        skipped = [c for c in cands if not c.admitted]
        hiding = [c for c in skipped
                  if c.reason.startswith(HIDING_PREFIXES)]

        # THE FRAME GOES OUT FIRST, so it survives truncation. It is the
        # coverage statement, and a partial log without it would say what was
        # found while hiding what was looked at.
        rep.line("FRAME -- what was looked at, and how it was found")
        rep.line(f"  repo               {root}")
        rep.line(f"  HEAD               {head}")
        rep.line(f"  tree               {tree_desc}")
        rep.line(f"  enumeration        {frame['how']}")
        rep.line(f"  candidates         {len(cands)}  "
                 f"(tracked {frame['tracked']}, on disk {frame['worktree']})")
        if frame["untracked_only"]:
            rep.line(f"  untracked only     {len(frame['untracked_only'])}"
                     f" -- present here, will not travel: "
                     + ", ".join(frame["untracked_only"][:6])
                     + (" ..." if len(frame["untracked_only"]) > 6 else ""))
        if frame["tracked_only"]:
            rep.line(f"  tracked, absent    "
                     + ", ".join(frame["tracked_only"][:6]))
        if frame["git_note"]:
            rep.line(f"  git note           {frame['git_note']}")
        if only_note:
            rep.line(f"  FILTER             {only_note}")
        rep.line(f"  admitted           {len(admitted)}  "
                 f"({len(scripts)} script gate(s), {len(tests)} test file(s))")
        rep.line(f"  skipped            {len(skipped)}  "
                 f"({len(hiding)} of them could be hiding a verdict)")
        rep.line("")

        by_reason: dict[str, list[str]] = {}
        for c in skipped:
            by_reason.setdefault(c.reason.split(":")[0], []).append(c.path)
        rep.line("SKIPPED, BY REASON -- this list is the coverage statement")
        for r, paths in sorted(by_reason.items(), key=lambda kv: -len(kv[1])):
            rep.line(f"  {len(paths):3d}  {r}")
            for path in sorted(paths)[:4]:
                rep.line(f"         {path}")
            if len(paths) > 4:
                rep.line(f"         ... and {len(paths) - 4} more")
        rep.line("")

        if args.list:
            rep.plan([], "--list: nothing will be run")
            rep.line("ADMITTED")
            for c in sorted(admitted, key=lambda c: c.path):
                rep.line(f"  {c.kind:8s} {c.path}")
                if c.kind == "python":
                    rep.line(f"           {c.reason}")
            rep.line("")
            rep.line(f"--list: nothing was run, so there is no verdict. "
                     f"Exit {EXIT_UNKNOWN} (UNKNOWN about reach, "
                     f"non-blocking): nothing was ASKED to run, so there is "
                     f"no check whose finding is being withheld.")
            return UNKNOWN, EXIT_UNKNOWN

        # THE DENOMINATOR, PRINTED BEFORE THE FIRST CHECK STARTS. This is what
        # makes `ran=3/17` on an interrupted run mean something: `17` was fixed
        # and written down while the log was still being produced, so a reader
        # of a truncated log knows what it was aiming at and not merely what it
        # reached. A test file group counts as ONE unit because it is one
        # pytest invocation and dies as one.
        plan = [c.path for c in sorted(scripts, key=lambda c: c.path)]
        if tests and not args.no_tests:
            plan.append(f"sdk/tests (pytest) -- {len(tests)} file(s), "
                        f"one invocation")
        prog.expected = len(plan)
        rep.plan(plan, "check unit(s) admitted and expected to run in this "
                       "order; every one of them reports below as it finishes")

        outcomes: list[Outcome] = []
        suite_frame: dict = {}
        if tests and args.no_tests:
            rep.line(f"NOTE: --no-tests, so {len(tests)} test file(s) were "
                     f"enumerated and NOT run.")
            hiding = list(hiding) + [Candidate(
                path="sdk/tests (pytest)", frames=(),
                reason="needs-compute: --no-tests was passed; the suite was not run")]

        rep.line("CHECKS RUN")
        rep.line(f"  Streamed: a `{MARK_RUNNING}` line is written when a check "
                 f"STARTS and its [VERDICT]")
        rep.line(f"  block when it finishes. A `{MARK_RUNNING}` with no block "
                 f"under it is the check that")
        rep.line(f"  was still running when this log ends.")
        for c in sorted(scripts, key=lambda c: c.path):
            prog.start(c.path)
            rep.line(f"  {MARK_RUNNING} ({prog.completed + 1}/{prog.expected}) "
                     f"{c.path} ...")
            o = run_script(run_root, c, args.timeout,
                           exclusive=(args.tree == "snapshot"))
            outcomes.append(o)
            prog.finish(o)
            _emit_outcome(rep, o, prog)
        if tests and not args.no_tests:
            # Without a filter the suite is run over the DIRECTORY and then
            # diffed against the enumeration -- that diff is the point. With a
            # filter it is run over the named files, because running the whole
            # directory under a filter would report a coverage the caller did
            # not ask for and did not get.
            prog.start("sdk/tests (pytest)")
            rep.line(f"  {MARK_RUNNING} ({prog.completed + 1}/{prog.expected}) "
                     f"sdk/tests (pytest), {len(tests)} file(s) -- this is the "
                     f"long one (~15 min)")
            o, suite_frame = run_pytest(
                run_root, [c.path for c in tests], args.suite_timeout,
                target=[c.path for c in tests] if args.only else None)
            outcomes.append(o)
            prog.finish(o)
            _emit_outcome(rep, o, prog)
        rep.line("")

        if suite_frame:
            rep.line("SUITE FRAME -- what 'the suite' meant on this run")
            rep.line(f"  argv                 {suite_frame['argv']}")
            rep.line(f"  test files enumerated {suite_frame['files_enumerated']}")
            rep.line(f"  test files collected  {suite_frame['files_collected']}")
            rep.line(f"  tests collected       {suite_frame['tests_collected']}"
                     f"  (failed {suite_frame['failed']}, errored "
                     f"{suite_frame['errored']}, skipped {suite_frame['skipped']})")
            rep.line(f"  __pycache__ purged    "
                     f"{suite_frame['purged_pycache_dirs']} directories, before "
                     f"the run (stale bytecode has inverted results here)")
            for f in suite_frame["files_missing"]:
                rep.line(f"  NOT COLLECTED         {f}")
            rep.line("")

        verdict, reasons, blocking = aggregate(outcomes, hiding)
        rc = exit_code(verdict, blocking)
        ran = len(outcomes)
        rep.line("=" * 78)
        rep.line(f"VERDICT: {verdict}")
        rep.line(
            f"  exit {rc} -- "
            + ("BLOCKING. At least one check did not come back with a usable "
               "verdict, so this run cannot say what it would have found."
               if blocking and verdict == UNKNOWN else
               "BLOCKING. A check that ran returned a finding."
               if blocking else
               "not blocking. Every UNKNOWN above is about this runner's REACH "
               "-- what it did not examine, printed in full in the coverage "
               "statement -- and not about any check's output."
               if verdict == UNKNOWN else
               "clean."))
        if only_note:
            rep.line(f"  {only_note}")
        rep.line(f"  frame: {ran} check(s) ran, {len(skipped)} not "
                 f"admitted, {len(hiding)} unrun check(s) whose skip "
                 f"reason could be hiding a verdict")
        for r in reasons:
            rep.line(f"  {r}")
        rep.line("=" * 78)

        if args.json:
            print(json.dumps({
                "verdict": verdict,
                #: Additive, and the one key a consumer of a partial document
                #: needs: the interrupted path emits `false` here.
                "complete": True,
                "blocking": blocking,
                "exit": rc,
                "expected": prog.expected,
                "completed": prog.completed,
                "reasons": reasons,
                "frame": frame,
                "suite": suite_frame,
                "checks": [dataclasses.asdict(o) for o in outcomes],
                "skipped": [{"path": c.path, "reason": c.reason} for c in skipped],
            }, indent=1), flush=True)
        return verdict, rc
    finally:
        if snapshot is not None:
            drop_snapshot(root, snapshot)


if __name__ == "__main__":
    raise SystemExit(main())
