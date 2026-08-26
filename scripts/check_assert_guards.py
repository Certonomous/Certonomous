#!/usr/bin/env python3
"""ARM (c) OF THE `-O` SHAPE: an AST check requiring ZERO `ast.Assert` nodes.

WHY THIS EXISTS
---------------
`python3 -O` and `PYTHONOPTIMIZE=1` DELETE every `assert` statement outright.
An `assert` therefore cannot carry a refusal, a guard, a control or a gate: under
one interpreter flag the check is gone and the surrounding code walks on.  This
was measured, not argued:

  * `verification/runs/T-family/T8_runs/analyse_t8.py` under `-O` returns
    `GATE REACHED` where `CLAUDE.md` rule 5 forbids it, with no error and rc 0
    (`docs/campaigns/T-family/T8_REREGISTRATION_DRAFT_2026-08-25.md` section 4e.3).
  * a planted-control selftest under `-O` PRINTED `PLANTED CONTROL PASSED` on an
    estimator returning zeros (`verification/campaign/
    CFD_ASSERT_EXPOSURE_CLOSEOUT_2026-08-25.md` section 1, L-332).

The cfd supervisor's adopted three-arm shape
(`verification/campaign/CFD_ASSERT_RULE_REFINEMENT_2026-08-25.md` section 1) is:
  (a) the guarded path DRIVEN under `-O` and required to REFUSE;
  (b) a sacrificial MUTANT driven under `-O` and required to REFUSE;
  (c) AN AST CHECK REQUIRING ZERO `Assert` NODES -- which catches a revert
      WITHOUT RUNNING ANYTHING.

Arms (a) and (b) are per-instrument and belong in each instrument's own selftest.
ARM (c) IS GENERIC, AND THIS FILE IS IT.  It was the arm the cfd supervisor
recorded as *"the one I would not have thought of and the cheapest of the
three"*, and until now no committed instrument implemented it.

WHY IT MATTERS THAT THIS CHECK NEEDS NO EXECUTION
-------------------------------------------------
Arms (a) and (b) prove an instrument's refusals fire TODAY.  They cannot prove
that a later edit did not turn a `raise` back into an `assert`, because a
selftest exercising the CLEAN path passes either way.  Arm (c) reads the
statement TYPE and so catches the revert on the source alone.

    A REVERT THAT ARMS (a) AND (b) CANNOT SEE IS EXACTLY THE REVERT THAT
    MATTERS, BECAUSE IT REINTRODUCES A GUARD THAT EVAPORATES SILENTLY.

THIS FILE OBEYS ITS OWN RULE
----------------------------
It contains ZERO `assert` statements and every refusal is `sys.exit(2)`.
`--selftest` applies the check TO THIS FILE and refuses if it ever stops holding.

ENUMERATION -- `git ls-tree`, NEVER `git ls-files`
--------------------------------------------------
`git ls-files` reads the SHARED INDEX, which decays under this lab's
private-index protocol and carries phantom deletions.  Measured 2026-08-26 on
the heat-transfer territory: the index was missing FOUR tracked `.py` files that
HEAD has, and two of them were `T8_runs/analyse_t8.py` and
`T8_runs/build_t8.py` -- i.e. the file carrying the most serious `assert` in the
territory was INVISIBLE to an `ls-files` sweep.  This script enumerates from
`git ls-tree -r HEAD --name-only` and reads blobs from HEAD, and offers
`--worktree` for the on-disk state when that is what is wanted.

USAGE
-----
  check_assert_guards.py --selftest
  check_assert_guards.py --root <prefix> [--root <prefix> ...] [--worktree]
  check_assert_guards.py --require-clean <path> [<path> ...] [--worktree]

`--require-clean` is the gate form: rc 0 when every named file has zero `Assert`
nodes, rc 2 (a REFUSAL, not an exception) when any does.
"""
import argparse
import ast
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def refuse(msg):
    """The replacement form.  Unaffected by `-O`."""
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def source_of(path, worktree):
    if worktree:
        if not os.path.isfile(path):
            refuse("no such file in the worktree: %s" % path)
        with open(path, "rb") as fh:
            return fh.read()
    p = subprocess.run(["git", "-C", REPO, "show", "HEAD:" + path],
                       capture_output=True)
    if p.returncode != 0:
        refuse("not at HEAD: %s" % path)
    return p.stdout


def assert_nodes(src, path):
    """Every `ast.Assert` in `src`, as (lineno, source line).  A docstring or a
    comment containing the word `assert` is NOT an Assert node and is not
    reported -- the check is on STATEMENT TYPE, which is the whole point."""
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as exc:
        refuse("%s does not parse: %s" % (path, exc))
    lines = src.decode("utf-8", "replace").splitlines()
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            txt = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
            out.append((node.lineno, txt))
    return sorted(out)


def python_files_under(prefixes):
    p = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "HEAD",
                        "--name-only"], capture_output=True, text=True)
    if p.returncode != 0:
        refuse("git ls-tree failed; this check enumerates from HEAD, never from "
               "the shared index")
    names = p.stdout.splitlines()
    return sorted(n for n in names
                  if n.endswith(".py") and any(n.startswith(x) for x in prefixes))


def scan(paths, worktree):
    total, dirty = 0, []
    for path in paths:
        found = assert_nodes(source_of(path, worktree), path)
        if found:
            dirty.append((path, found))
            total += len(found)
    return total, dirty


def report(paths, worktree):
    total, dirty = scan(paths, worktree)
    for path, found in dirty:
        for lineno, txt in found:
            print("%s:%d\t%s" % (path, lineno, txt[:140]))
    print("scanned %d file(s) from %s: %d ast.Assert node(s) in %d file(s)"
          % (len(paths), "the worktree" if worktree else "HEAD", total,
             len(dirty)))
    return total, dirty


CLEAN_FIXTURE = (
    "def f(x):\n"
    "    if x < 0:\n"
    "        raise ValueError('negative')\n"
    "    return x\n"
    "\n"
    "DOC = 'the word assert appears here and must not be counted'\n"
)
DIRTY_FIXTURE = (
    "def f(x):\n"
    "    assert x >= 0, 'negative'\n"
    "    return x\n"
)


def selftest():
    """Three things, and the PLANTED CONTROL is the first of them.

    A zero from a reader not shown able to see a non-zero is not evidence
    (`CLAUDE.md` rule 3).  So the dirty fixture is checked FIRST: if the checker
    cannot see a planted `assert`, everything after it is worthless.

    Every success print sits INSIDE the passing branch, so that removing a check
    removes the claim (L-332).
    """
    failures = []
    tmp = tempfile.mkdtemp(prefix="check_assert_guards_")
    dirty = os.path.join(tmp, "dirty_fixture.py")
    clean = os.path.join(tmp, "clean_fixture.py")
    with open(dirty, "w") as fh:
        fh.write(DIRTY_FIXTURE)
    with open(clean, "w") as fh:
        fh.write(CLEAN_FIXTURE)

    # (1) PLANTED CONTROL -- the checker must SEE the planted assert.
    found = assert_nodes(DIRTY_FIXTURE.encode(), dirty)
    if len(found) == 1 and found[0][0] == 2:
        print("PLANT SEEN: the planted `assert` at line 2 of the sacrificial "
              "fixture was detected.")
    else:
        failures.append("PLANTED CONTROL FAILED: the checker did not see the "
                        "planted assert; found %r" % (found,))

    # (2) the clean fixture must be clean, and a docstring mentioning the word
    #     `assert` must NOT be counted -- statement type, not text.
    found_clean = assert_nodes(CLEAN_FIXTURE.encode(), clean)
    if not found_clean:
        print("CLEAN FIXTURE CLEAN: a `raise` guard and the word 'assert' in a "
              "string literal produce zero Assert nodes.")
    else:
        failures.append("clean fixture reported %r" % (found_clean,))

    # (3) THE ARM THAT BITES -- this script DRIVEN under `python3 -O` against the
    #     dirty fixture must REFUSE with rc 2, identically to plain `python3`.
    #     Not "the selftest exits 0 under -O": a passing selftest exercises the
    #     clean path, and the clean path is the one an evaporated guard walks.
    me = os.path.abspath(__file__)
    rcs = {}
    for tag, argv in (("python3", [sys.executable, me]),
                      ("python3 -O", [sys.executable, "-O", me])):
        p = subprocess.run(argv + ["--require-clean", dirty, "--worktree"],
                           capture_output=True, text=True)
        rcs[tag] = p.returncode
    if rcs["python3"] == 2 and rcs["python3 -O"] == 2:
        print("REFUSAL FIRES UNDER `-O`: --require-clean on the sacrificial "
              "fixture returned rc 2 under BOTH `python3` and `python3 -O`.")
    else:
        failures.append("the refusal did not fire identically: %r" % (rcs,))

    # (4) self-application: this file must itself carry zero Assert nodes.
    found_self = assert_nodes(source_of(me, True), me)
    if not found_self:
        print("SELF-APPLICATION CLEAN: this checker carries zero ast.Assert "
              "nodes and so obeys the rule it enforces.")
    else:
        failures.append("this checker carries asserts at %r" % (found_self,))

    for path in (dirty, clean):
        os.unlink(path)
    os.rmdir(tmp)

    if failures:
        for f in failures:
            print("FAILED: " + f)
        return 1
    print("SELFTEST PASS: 4 arms, 0 FAILED.")
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", action="append", default=[])
    ap.add_argument("--require-clean", nargs="+", default=[], dest="require")
    ap.add_argument("--worktree", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.require:
        total, dirty = report(a.require, a.worktree)
        if total:
            refuse("%d ast.Assert node(s) in %d file(s) required to be clean; "
                   "an `assert` cannot carry a refusal, guard, control or gate "
                   "because `python3 -O` deletes it" % (total, len(dirty)))
        print("CLEAN: every named file carries zero ast.Assert nodes.")
        return 0
    if a.root:
        report(python_files_under(a.root), a.worktree)
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
