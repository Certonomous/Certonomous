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
  standalone      HEAD's BLOB vs the FILE ON DISK, per          seconds
                  declared path (+ any path another agent
                  staged into the SHARED index)
  hook            $GIT_INDEX_FILE vs HEAD -- all paths         zero
  --at <sha>      the commit object                            n/a (post hoc)

THE MODE THAT WAS BROKEN, AND THE ONE THAT WAS NOT (repaired 2026-08-16)
=======================================================================
The standalone mode used `git diff --numstat HEAD -- <paths>`. That is a
diff-INDEX walk: git reaches HEAD through `.git/index`, and a path with NO
index entry is not tracked as far as that walk is concerned, so a file sitting
on disk was reported as a whole-file DELETION.

This was not a rare edge. It is the state THIS LAB'S OWN COMMIT PROTOCOL
CREATES. A commit built with `GIT_INDEX_FILE` -- the private-index form
mandated on `docs/DOCKET.md` and preferred wherever the shared index is dirty
-- never writes the shared index, so every NEW file it lands is in HEAD and
absent from the index. Every later declaration against such a file was graded
against a phantom deletion. Measured at `1a9f7f12`: this module declared
`0+/289-` for `sdk/tests/test_docket_reconciliation.py` whose true delta was
`0+/1-`, and `git ls-files -s` on that path printed nothing at all.

So the gate that is this lab's primary defence against capture was FAIL-FALSE
for exactly the files its own protocol produces. Class B2.

The repair is immunity by construction rather than a correction bolted on: the
standalone mode now resolves each declared path from `git cat-file blob
<rev>:<path>` and the file on disk, compared with `git diff --no-index`, which
cannot reach an index by definition. `worktree_numstat` is that function.

`--at` WAS NEVER BROKEN, and this was verified rather than assumed: it uses
`git show --numstat`, which diffs a commit object against its parent, and no
index is consulted on either side. At `f12e40d4` the two modes were run against
the same file and the same declaration -- worktree mode said `0+/289-`, `--at`
said `0+/1-`, and `--at` was right. If you are ever unsure which mode you can
trust, `--at` is the one, at the cost of grading a commit that already exists.

The shared index is still read in ONE place, on purpose (`index_anomalies`),
because a peer's `git add` reaching your commit is the defect this module
exists to catch. It now distinguishes a genuinely STAGED foreign edit from a
path with NO INDEX ENTRY, which the old code would have reported as somebody
else's staged work and sent the reader hunting an agent who never touched it.

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
import tempfile

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}


def _git(root: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", root, *args],
                          capture_output=True, text=True)


def _git_bytes(root: str, *args: str) -> subprocess.CompletedProcess:
    """As `_git`, but binary-safe -- blobs are not necessarily text."""
    return subprocess.run(["git", "-C", root, *args], capture_output=True)


def _count_lines(data: bytes) -> int:
    return data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)


def _pair_numstat(text: str):
    """First numstat record of a two-file `--no-index` diff -> (added, removed)."""
    for line in text.splitlines():
        fields = line.split("\t")
        if len(fields) < 3:
            continue
        a, r = fields[0], fields[1]
        return (None if a == "-" else int(a), None if r == "-" else int(r))
    return (0, 0)


def worktree_numstat(root, rev, declared):
    """Added/removed per declared path, comparing *rev* to the FILE ON DISK.

    INDEX-FREE BY CONSTRUCTION, and that is the whole point of this function
    rather than an implementation detail. It never runs `git diff HEAD`,
    `git diff-index` or anything else that consults `.git/index`. Each path is
    resolved from three facts only: whether the blob exists at *rev*, whether
    the file exists on disk, and -- when both -- a `git diff --no-index`
    between a temporary copy of the blob and the file, which by definition
    cannot reach an index.

    The four cases are all first-class; none is a degenerate diff:

        in rev, on disk        -> the real line delta
        NOT in rev, on disk    -> N+/0-, a wholly new file
        in rev, NOT on disk    -> 0+/N-, a deletion
        neither                -> absent from the result ("nothing changed")
    """
    actual = {}
    for path in sorted(declared):
        disk = os.path.join(root, path)
        on_disk = os.path.isfile(disk)
        in_rev = _git(root, "cat-file", "-e", "%s:%s" % (rev, path)).returncode == 0
        if not on_disk and not in_rev:
            continue
        if not in_rev:
            with open(disk, "rb") as fh:
                actual[path] = (_count_lines(fh.read()), 0)
            continue
        blob = _git_bytes(root, "cat-file", "blob", "%s:%s" % (rev, path))
        if blob.returncode != 0:                      # unreadable -> ungradeable
            actual[path] = (None, None)
            continue
        if not on_disk:
            actual[path] = (0, _count_lines(blob.stdout))
            continue
        with tempfile.TemporaryDirectory() as tmp:
            ref = os.path.join(tmp, "ref")
            with open(ref, "wb") as fh:
                fh.write(blob.stdout)
            cp = _git(root, "diff", "--no-index", "--numstat", "--no-renames",
                      ref, os.path.abspath(disk))
        delta = _pair_numstat(cp.stdout)
        # An UNCHANGED file stays ABSENT from the result, which is what the old
        # `git diff` call did and what the B1 clause of this module's contract
        # requires: "nothing changed at the declared path" must reach the
        # UNKNOWN branch of `reconcile`, never be graded as a 0+/0- FAIL.
        # Reporting (0, 0) here turned that clause into a FAIL and reddened
        # test_nothing_changed_at_the_declared_path_is_UNKNOWN_and_not_PASS --
        # caught by running the pre-existing suite against both versions.
        if delta == (0, 0):
            continue
        actual[path] = delta
    return actual


def index_anomalies(root, declared):
    """What the SHARED index holds that the author did not declare.

    This is the one place the index is read ON PURPOSE, because a peer's
    `git add` landing in your commit is the defect this module exists to catch.
    It distinguishes two states that `git diff --cached` renders identically:

      STAGED      the path has an index entry differing from HEAD -- somebody
                  staged an edit, and a pathspec-less commit would land it.
      NO ENTRY    the path is in HEAD and has NO index entry at all. That is
                  the private-index protocol's own by-product, not a peer's
                  edit, and calling it "staged" would send the reader hunting
                  for an agent who never touched the file.
    """
    tracked = {p for p in _git(root, "ls-files").stdout.splitlines() if p}
    changed = {p for p in _git(root, "diff", "--cached", "--name-only",
                               "--no-renames", "HEAD").stdout.splitlines() if p}
    staged, missing = set(), set()
    for path in changed - set(declared):
        (missing if path not in tracked else staged).add(path)
    return staged, missing


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
        # SOUND, and verified rather than assumed: `git show --numstat` diffs
        # the commit object against its parent. Neither side is the index, so
        # this mode never had the defect the worktree mode had.
        cp = _git(root, "show", "--numstat", "--no-renames", "--format=", rev)
        return parse_numstat(cp.stdout), (set(), set()), f"commit {rev}"
    if os.environ.get("GIT_INDEX_FILE"):
        # Reads an index ON PURPOSE -- the private one git builds for the hook,
        # holding exactly what it is about to write. Not the shared index.
        cp = _git(root, "diff-index", "--cached", "--numstat", "--no-renames",
                  "HEAD")
        return parse_numstat(cp.stdout), (set(), set()), "hook ($GIT_INDEX_FILE)"
    # INDEX-FREE. `git diff HEAD -- <path>` walked the index and reported a
    # phantom whole-file DELETION for any path with no index entry -- exactly
    # what the private-index protocol leaves behind for every new file it
    # lands. See "THE MODE THAT WAS BROKEN" in the module docstring.
    actual = worktree_numstat(root, "HEAD", declared)
    return actual, index_anomalies(root, declared), "worktree vs HEAD"


def _fmt(pair):
    return "%s+/%s-" % tuple("?" if n is None else n for n in pair)


def reconcile(decl, actual, staged_extra):
    """-> (verdict, [findings], [ungraded]).  Never PASS from an empty set."""
    staged_extra, missing_entry = staged_extra
    if not decl:
        return UNKNOWN, [], ["no declaration supplied -- nothing to compare "
                             "against, so this is not a pass"]
    if not actual and not staged_extra and not missing_entry:
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
    for path in sorted(missing_entry):
        ungraded.append("%s: in HEAD with NO shared-index entry -- the "
                        "private-index protocol's by-product, not a peer's "
                        "edit. A pathspec-less commit would DELETE it. Not a "
                        "finding against your declaration" % path)
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
