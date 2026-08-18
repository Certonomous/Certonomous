#!/usr/bin/env python3
"""Every `docs/papers/...` citation in the tree must leave its reader a route.

WHY THIS EXISTS. Commit `5c0d2483` (2026-08-18) refiled the paper library into
topic subdirectories and renamed almost every file in it, and `4323d7e3`
lowercased two of the new names afterwards. 26 distinct pre-move paths were left
standing in 40 tracked files. A blanket find-and-replace would have repaired the
pointers and, in the same pass, falsified every dated sentence that recorded where
a file had been fetched to. So the corpus carries two different repairs, and this
check is written to accept both and to accept nothing else.

A citation passes if EITHER:

  RESOLVED  -- the path exists on the frame being read; or
  FORWARDED -- the citing file also carries the path that holds the same blob
               today, so a reader who tries the dead path and reads on is not
               stranded. That is what an appended forwarding note supplies, and
               what a forwarding table row supplies on its own line.

It fails on a citation that is neither, which is the only state that strands a
reader.

A third outcome is NOT a failure and is printed rather than dropped: a
`docs/papers/...` path that named no library file at ANY frame is not a citation
at all. `scripts/check_filing.py` plants seven of them as controls for its own
paper-naming rule, and a fabricated control path must never resolve. They are
listed by file and line because that is also where a genuine typo would land, and
silently discarding the class would discard the typo with it.

The old->new pairing is NOT hardcoded and is NOT read from any prose table. It is
re-derived on every run from git, by BLOB IDENTITY: each path in the pre-move tree
is matched to the path in the post-move tree carrying the identical blob hash.
Name similarity decides nothing, which is why `Paper1.pdf` resolves to
`verification_validation/eca_hoekstra_2014_numerical_uncertainty.pdf` -- a pair no
name-based map would have made.

Reads a git tree by default rather than the working directory. The working
checkout in this lab lags HEAD on files landed by the private-index commit form
(DOCKET.md D356), so a scan of the checkout reports staleness that the repository
does not have. `--worktree` reads the checkout instead, and says so.

    python3 scripts/check_paper_citations.py                # HEAD
    python3 scripts/check_paper_citations.py --rev <commit>
    python3 scripts/check_paper_citations.py --worktree

Exit 0 if no citation is stranded, 1 if any is, 2 if the check could not run.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOVE_COMMIT = "5c0d2483"

#: A citation is a path with one of these suffixes. Bare directory mentions are
#: not citations and are deliberately out of scope.
CITE = re.compile(r"docs/papers/[A-Za-z0-9_\-./]*[A-Za-z0-9_\-]")
SUFFIX = re.compile(r"\.(pdf|txt|md|json|csv|html|bib)$")


def _run(args: list[str]) -> str:
    """git, with the exit status checked rather than piped away."""
    proc = subprocess.run(args, cwd=REPO, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(f"FAILED: {' '.join(args)}\n{proc.stderr}")
        raise SystemExit(2)
    return proc.stdout


def _papers(rev: str) -> dict[str, list[str]]:
    """blob hash -> paths under docs/papers/ at `rev`."""
    out: dict[str, list[str]] = {}
    for line in _run(["git", "ls-tree", "-r", rev,
                      "--format=%(objectname) %(path)"]).splitlines():
        obj, path = line.split(" ", 1)
        if path.startswith("docs/papers/"):
            out.setdefault(obj, []).append(path)
    return out


def forwarding_map(rev: str) -> dict[str, str]:
    """Pre-move path -> the path holding the same blob at `rev`.

    Built by blob identity against the move commit's own parent, so the map is a
    measurement of what git did and not a transcription of what anyone reported.
    An old blob that reaches more than one live path is ambiguous and is dropped
    rather than guessed at.
    """
    old = _papers(MOVE_COMMIT + "^")
    now = _papers(rev)
    pairs: dict[str, str] = {}
    for obj, olds in old.items():
        live = now.get(obj, [])
        if len(live) != 1:
            continue
        for path in olds:
            pairs[path] = live[0]
    return pairs


def _files(rev: str, worktree: bool) -> list[str]:
    if worktree:
        return _run(["git", "ls-files"]).splitlines()
    return [ln.split("\t", 1)[1] for ln in
            _run(["git", "ls-tree", "-r", rev, "--format=%(objecttype)\t%(path)"]
                 ).splitlines() if ln.startswith("blob\t")]


def _text(path: str, rev: str, worktree: bool) -> str | None:
    try:
        if worktree:
            with open(os.path.join(REPO, path), encoding="utf-8") as handle:
                return handle.read()
        proc = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=REPO,
                              capture_output=True)
        if proc.returncode != 0:
            return None
        return proc.stdout.decode("utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--worktree", action="store_true",
                    help="read the checkout instead of a git tree")
    args = ap.parse_args()

    rev = _run(["git", "rev-parse", args.rev]).strip()
    pairs = forwarding_map(rev)
    live = set()
    for paths in _papers(rev).values():
        live.update(paths)

    stranded: list[tuple[str, int, str]] = []
    forwarded: list[tuple[str, int, str, str]] = []
    foreign: list[tuple[str, int, str]] = []
    table_rows = 0
    resolved = 0

    for path in _files(rev, args.worktree):
        if path.startswith("docs/papers/"):
            continue
        text = _text(path, rev, args.worktree)
        if text is None:
            continue
        seen = set(CITE.findall(text))
        for line_no, line in enumerate(text.splitlines(), 1):
            for cite in CITE.findall(line):
                if not SUFFIX.search(cite):
                    continue
                if cite in live:
                    resolved += 1
                elif cite not in pairs:
                    # Never named a library file at any frame, so it is not a
                    # citation. `scripts/check_filing.py` plants seven such
                    # paths as controls for its own paper-naming rule --
                    # `docs/papers/bench/no_year_in_this_name.pdf` and friends
                    # are fabricated on purpose and must never exist. Reported
                    # by name rather than dropped, because this is also where a
                    # genuine typo would land.
                    foreign.append((path, line_no, cite))
                elif pairs[cite] in line:
                    # a forwarding-table row: it carries its own destination
                    table_rows += 1
                elif pairs[cite] in seen:
                    forwarded.append((path, line_no, cite, pairs[cite]))
                else:
                    stranded.append((path, line_no, cite))

    frame = "worktree" if args.worktree else f"tree {rev[:8]}"
    print(f"frame: {frame}")
    print(f"forwarding pairs re-derived from git by blob identity: {len(pairs)}")
    print(f"citations that resolve on the frame: {resolved}")
    print(f"forwarding-table rows (old and new on one line): {table_rows}")
    print(f"historical citations left verbatim, forwarded in their own file: "
          f"{len(forwarded)}"
          f" across {len({f for f, _, _, _ in forwarded})} file(s)")
    for path, line_no, cite, new in sorted(forwarded):
        print(f"  FORWARDED {path}:{line_no}  {cite} -> {new}")
    print(f"paths that named no library file at any frame, in scope for no "
          f"forwarding and reported rather than dropped: {len(foreign)}")
    for path, line_no, cite in sorted(foreign):
        print(f"  NOT-A-LIBRARY-PATH {path}:{line_no}  {cite}")
    if stranded:
        print(f"\nSTRANDED: {len(stranded)} citation(s) that neither resolve "
              f"nor carry a route in their own file")
        for path, line_no, cite in sorted(stranded):
            print(f"  STRANDED  {path}:{line_no}  {cite}")
        return 1
    print("\nno stranded citation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
