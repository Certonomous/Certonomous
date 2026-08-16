#!/usr/bin/env python3
"""Refuse a commit whose contents the author cannot name in advance (docket D220).

THE DEFECT CLASS
================
Under a live fleet a pathspec commit isolates by FILE, not by AUTHOR. On
2026-08-15 FIVE commits in one evening carried edits their author never wrote
(re-counted by execution on D220 -- the sixth in the records never became a
commit, and one of the six shas is an amend of another): two mutation-harness
mutants into `scripts/self_audit.py` (`fb30e00f`, live in HEAD for 65 minutes),
census mutant RC10 into the commit that repaired them (`0a3e82d7`), four other
agents' docket rows into a docket commit (`49b36e57`), one more into an earlier
one (`1aa90081`), and the chief's own acceptance block into an agent's commit
about something else (`d6ff862d`). EVERY author checked
`git status` or `git diff`, and every one was clean at the instant checked. The
window is between the check and the `git add`, and `git log -1 --stat` does not
show it, because a plausible stat is exactly what a capture produces.

Both of the two that WERE caught were caught the same way: the author counted
the changes they expected and found a different number. This module is that
count, made mechanical.

WHAT IT COMPARES, AND WHY IT IS A DECLARATION AND NOT A HEURISTIC
================================================================
A tool that guessed which hunks "look like yours" would be another instrument
grading FORM where the failure mode is AUTHORSHIP. So the author states, in one
token per path, what they are committing:

    <path>:<added>            e.g.  docs/DOCKET.md:1        one row appended
    <path>:<added>-<removed>  e.g.  scripts/self_audit.py:1-1
    ? for either number       e.g.  scripts/self_audit.py:?-0
                                    "I cannot predict my additions; I removed
                                     nothing" -- that path is then UNGRADED and
                                     the run is UNKNOWN, never PASS.

Added/removed LINES, not `@@` hunks, because the real captures were contiguous
appends: five docket rows on five adjacent lines are ONE hunk at any -U, and a
hunk count would have missed three of the five. The hunk count is printed
alongside as context; it is not what is graded.

THE THREE MODES, AND WHICH ONE IS DEFEATABLE
============================================
Measured in a scratch repository, not assumed (the transcript is on D220):

  * `git commit -F msg -- <paths>` takes those paths' content FROM THE WORKING
    TREE and IGNORES THE INDEX. Stage 1+/1-, let a concurrent agent append one
    line, commit with the pathspec: `git diff --cached` still reads 1+/1- and
    the commit lands 2+/1-. So a check that reads the index is defeated by
    exactly the failure it prevents, and the default mode reads the WORKTREE.

  * Under that same pathspec commit, git builds a temporary index containing
    precisely what it is about to write, exports `GIT_INDEX_FILE` at it, and
    runs `pre-commit` against it -- verified: the hook saw `2 1 f.txt` and
    `2 1 f.txt` landed. After the hook returns, git does not re-read the
    worktree. Installed as `.git/hooks/pre-commit` this module's window is
    ZERO. Run by hand it is NOT zero, and that is stated rather than papered
    over: standalone it narrows the window from `check -> add -> commit` to
    `add -> check -> commit` and no further.

  * `--at <sha>` grades a commit that already exists. A commit object cannot be
    rewritten under you, so this mode is not defeatable at all -- at the cost
    that the capture has already happened. It turns a silent capture into a
    loud one in the same minute, which is what the two caught ones had.

  MODE            SOURCE OF TRUTH                              WINDOW
  standalone      worktree vs HEAD, restricted to the          seconds
                  declared paths (+ any path another agent
                  staged into the SHARED index)
  hook            $GIT_INDEX_FILE vs HEAD -- all paths         zero
  --at <sha>      the commit object                            n/a (post hoc)

THREE-VALUED, AND IT CANNOT PASS FROM AN EMPTY SET (defect class B1)
===================================================================
No declaration is UNKNOWN with a reason. Nothing changed at the declared paths
is UNKNOWN with a reason. A `?` anywhere is UNKNOWN with a reason. PASS requires
a non-empty declaration, a non-empty actual, and every number graded and equal.

EXIT CONTRACT -- `scripts/lab_check.py`'s: 0 PASS, 1 FAIL, 3 UNKNOWN.

SCHEDULING: this check declares a REQUIRED positional on purpose, so
`lab_check.py` skips it `requires-arguments`, non-blocking. That is the honest
outcome, not a limitation worked around: there is no declaration on a schedule,
and a scheduled run of this check could only ever return UNKNOWN.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}


def _git(root: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", root, *args],
                          capture_output=True, text=True)


def parse_declaration(items):
    """`path:A[-R]` -> {path: (A, R)}, where A/R are ints or None for '?'."""
    decl, bad = {}, []
    for item in items:
        if not item.strip():          # an empty token is an ABSENT declaration,
            continue                  # which is UNKNOWN below, never PASS
        path, _, counts = item.rpartition(":")
        if not path or not counts:
            bad.append(item)
            continue
        a, _, r = counts.partition("-")
        r = r or "0"
        try:
            decl[path] = (None if a == "?" else int(a),
                          None if r == "?" else int(r))
        except ValueError:
            bad.append(item)
    return decl, bad


def parse_numstat(text):
    """git --numstat output -> {path: (added, removed)}; '-' (binary) -> None."""
    out = {}
    for line in text.splitlines():
        fields = line.split("\t")
        if len(fields) < 3:
            continue
        a, r, path = fields[0], fields[1], fields[-1]
        out[path] = (None if a == "-" else int(a), None if r == "-" else int(r))
    return out


def collect(root, rev, declared):
    """(actual, staged_but_undeclared, mode) for whichever mode applies."""
    if rev:
        cp = _git(root, "show", "--numstat", "--no-renames", "--format=", rev)
        return parse_numstat(cp.stdout), set(), f"commit {rev}"
    if os.environ.get("GIT_INDEX_FILE"):
        cp = _git(root, "diff-index", "--cached", "--numstat", "--no-renames",
                  "HEAD")
        return parse_numstat(cp.stdout), set(), "hook ($GIT_INDEX_FILE)"
    cp = _git(root, "diff", "--numstat", "--no-renames", "HEAD", "--",
              *sorted(declared))
    actual = parse_numstat(cp.stdout)
    # `git diff HEAD -- <path>` is BLIND to an untracked path, so a declared
    # new file read as "nothing changed". Found by dogfooding this check on its
    # own first commit. A path that is on disk and not in HEAD is wholly added.
    for path in declared:
        disk = os.path.join(root, path)
        if path in actual or not os.path.isfile(disk):
            continue
        if _git(root, "cat-file", "-e", "HEAD:" + path).returncode == 0:
            continue
        with open(disk, "rb") as fh:
            data = fh.read()
        actual[path] = (data.count(b"\n")
                        + (1 if data and not data.endswith(b"\n") else 0), 0)
    staged = _git(root, "diff", "--cached", "--name-only", "--no-renames",
                  "HEAD")
    extra = {p for p in staged.stdout.splitlines() if p and p not in declared}
    return actual, extra, "worktree vs HEAD"


def _fmt(pair):
    return "%s+/%s-" % tuple("?" if n is None else n for n in pair)


def reconcile(decl, actual, staged_extra):
    """-> (verdict, [findings], [ungraded]).  Never PASS from an empty set."""
    if not decl:
        return UNKNOWN, [], ["no declaration supplied -- nothing to compare "
                             "against, so this is not a pass"]
    if not actual and not staged_extra:
        return UNKNOWN, [], ["nothing changed at the declared path(s) and "
                             "nothing is staged -- there is no commit to grade"]
    findings, ungraded = [], []
    for path in sorted(set(decl) | set(actual)):
        want, got = decl.get(path), actual.get(path)
        if want is None:
            findings.append("%s: changed (%s) and was NOT DECLARED"
                            % (path, _fmt(got)))
            continue
        if got is None:
            findings.append("%s: declared %s, but nothing changed there"
                            % (path, _fmt(want)))
            continue
        for i, label in ((0, "added"), (1, "removed")):
            if want[i] is None or got[i] is None:
                ungraded.append("%s: %s declared '?' -- UNGRADED (actual %s)"
                                % (path, label, _fmt(got)))
            elif want[i] != got[i]:
                findings.append("%s: %s lines declared %d, actual %d"
                                % (path, label, want[i], got[i]))
    for path in sorted(staged_extra):
        findings.append("%s: STAGED in the shared index and NOT DECLARED "
                        "(another agent's `git add` reaches your index)" % path)
    if findings:
        return FAIL, findings, ungraded
    if ungraded:
        return UNKNOWN, [], ungraded
    return PASS, [], []


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="hunk_check",
        description="Refuse a commit whose contents the author cannot name.")
    p.add_argument("expect", nargs="+", metavar="PATH:ADDED[-REMOVED]",
                   help="what you are committing; ? for a number you cannot "
                        "predict (that path is then UNGRADED, never PASS)")
    p.add_argument("--at", default=None, metavar="SHA",
                   help="grade an existing commit instead of the worktree. "
                        "Pass the sha you captured, not the moving HEAD")
    p.add_argument("--root", default=".")
    args = p.parse_args(argv)

    decl, bad = parse_declaration(args.expect)
    if bad:
        print("UNKNOWN  unparseable declaration: %s" % ", ".join(bad))
        print("         expected PATH:ADDED or PATH:ADDED-REMOVED")
        return EXIT[UNKNOWN]

    actual, extra, mode = collect(args.root, args.at, decl)
    verdict, findings, ungraded = reconcile(decl, actual, extra)

    print("hunk_check  source: %s" % mode)
    for path in sorted(set(decl) | set(actual)):
        print("  %-52s declared %-9s actual %s"
              % (path, _fmt(decl[path]) if path in decl else "-",
                 _fmt(actual[path]) if path in actual else "nothing"))
    for line in findings:
        print("  FINDING   %s" % line)
    for line in ungraded:
        print("  UNGRADED  %s" % line)
    print("%s" % verdict)
    return EXIT[verdict]


if __name__ == "__main__":
    sys.exit(main())
