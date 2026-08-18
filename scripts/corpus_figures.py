#!/usr/bin/env python3
"""Regenerate the corpus figures that documents keep quoting stale.

WHY THIS EXISTS. `docs/MEMORY_ARCHITECTURE.md` is the lab's map of its own
record. Cold-start run 2 (2026-08-11) found its counts drifted across the board
one day after it was written: the lesson corpus quoted at 53 blocks when it held
79, the product list at 60 items, the changelog at 53 entries when it held 113,
the memory store at 17 files when it held 19, the most-cited lesson at 93
citations when it had 101.

None of those was careless. Every one was correct when written, and the tree
moved under it -- the same shape as L-79, where prose was correct at 06:04 and
the code moved beneath it at 06:56, including one copy inside a sentence
asserting that it could not drift.

The repair is not better numbers. Numbers written by hand into prose go stale
at the rate the tree moves, which here is hourly. The repair is that a figure is
either REGENERATED at read time or carries the moment it was taken. This script
is the regeneration half: run it, and every figure the map quotes comes back
measured, with the commit it was measured at.

    python3 scripts/corpus_figures.py            # human-readable, stamped
    python3 scripts/corpus_figures.py --json     # for a doc build or a test

FRAME. Every count here is over `git ls-files` -- TRACKED files, and it says so
in its own output. That is not the same population as the filesystem, and it is
deliberately not `grep -r`: in this environment `grep` execs
`ugrep --ignore-files`, which honours `.gitignore` and silently skips the run
archives. A denominator from `git ls-files` is honest about being tracked-only.
That is lesson L-75.

Adding a figure here is cheap and is the right instinct. The rule for a new one:
it must be DERIVED from the tree by this script, never passed in, and it must
name the population it counts.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[1]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

#: R1 moves this file to `docs/`.  It is named through `lab_paths`, which binds
#: the legacy path and the successor as a PAIR, because `_read` below returns
#: `""` for a file that is not there and every lesson figure would then be a
#: clean zero -- and `scripts/lab_check.py` classifies this module `cannot-fail`
#: and never runs it, so no suite could have caught that.
LESSONS_REL = str(lab_paths.LESSONS.relative_to(REPO))

#: The out-of-repo auto-memory store. Durable against session end, NOT against a
#: fresh clone -- which is why the map counts it separately from the repo.
MEMORY_STORE = Path.home() / (
    ".claude/projects/-home-ubuntu-Certonomous/memory")


def _run(*args: str) -> str:
    out = subprocess.run(args, cwd=REPO, capture_output=True, text=True)
    return out.stdout


def _tracked() -> list[str]:
    return [p for p in _run("git", "ls-files").splitlines() if p]


def _read(rel: str) -> str:
    path = REPO / rel
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _head() -> tuple[str, bool]:
    sha = _run("git", "rev-parse", "--short", "HEAD").strip()
    dirty = bool(_run("git", "status", "--porcelain").strip())
    return sha or "UNKNOWN", dirty


def lesson_figures() -> dict:
    """LESSONS.md: lines, blocks, and the highest number actually present.

    The block regex is anchored to the heading form the file uses. It is
    reported alongside the max number because the corpus is KNOWN to be gapped
    and non-monotonic -- there is no L-52, L-4 sits after L-7, and one block is
    an unaddressable 'second corollary'. So `blocks` and `highest` are two
    different facts and neither is the other's check.
    """
    text = _read(LESSONS_REL)
    heads = [int(n) for n in re.findall(r"^#+\s*\**\s*L-(\d+)", text, re.M)]
    nums = sorted(set(heads))
    # Found by a SEPARATE pass over the same headings, so that `blocks -
    # distinct` and this dict are two routes to one quantity and can disagree.
    # That disagreement is the whole value: see the check line in _emit.
    duplicated = {n: heads.count(n) for n in nums if heads.count(n) > 1}
    return {
        "population": f"{LESSONS_REL}, headings matching '# L-<n>'",
        "lines": text.count("\n") + (1 if text and not text.endswith("\n") else 0),
        "bytes": len(text.encode("utf-8")),
        "blocks": len(heads),
        "distinct_numbers": len(nums),
        "duplicated": duplicated,
        "highest": nums[-1] if nums else None,
        "missing_below_highest": [
            n for n in range(1, (nums[-1] if nums else 0)) if n not in nums],
    }


def product_list_figures() -> dict:
    """The checklist and its changelog, counted by their own markers."""
    text = _read("docs/PRODUCT_LIST.md")
    items = re.findall(r"^\s*[-*]\s*\[([ x~\-])\]", text, re.M)
    tally: dict[str, int] = {}
    for mark in items:
        key = {" ": "open", "x": "done", "~": "pending_verification",
               "-": "blocked_or_failed"}[mark]
        tally[key] = tally.get(key, 0) + 1
    entries = re.findall(r"^### (.+)$", text, re.M)
    return {
        "population": "docs/PRODUCT_LIST.md checkbox items and '### ' changelog headings",
        "lines": text.count("\n"),
        "items": len(items),
        "by_status": tally,
        "changelog_entries": len(entries),
    }


def citation_ranking(top: int = 8) -> dict:
    """Which lessons the corpus actually leans on, measured not remembered.

    Counted over TRACKED files EXCLUDING LESSONS.md itself, so a lesson's own
    body and its cross-references to siblings do not inflate it. `L-4` must not
    match inside `L-40`, hence the trailing boundary.
    """
    counts: dict[str, int] = {}
    pattern = re.compile(r"\bL-(\d+)(?![\d])")
    for rel in _tracked():
        if rel == LESSONS_REL:
            continue
        path = REPO / rel
        try:
            if not path.is_file() or path.stat().st_size > 4_000_000:
                continue
            body = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeDecodeError):
            continue
        for num in pattern.findall(body):
            key = f"L-{int(num)}"
            counts[key] = counts.get(key, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return {
        "population": f"tracked files under 4 MB decoding as UTF-8, EXCLUDING {LESSONS_REL}",
        "cited_lessons": len(counts),
        "total_citations": sum(counts.values()),
        "top": ranked[:top],
    }


def tracked_shape() -> dict:
    """What the tracked tree is made of -- source versus solver output.

    The split matters for the repo-professionalization item (Katie's §7 G5),
    which asks that generated artifacts leave version control. A field file
    under `0/` is an INITIAL CONDITION and is source; the same filename under a
    non-zero time directory is solver output. Counting them together would
    overstate the generated set by roughly a thousand files.
    """
    tracked = _tracked()
    time_dir = re.compile(r"/[0-9]+\.?[0-9]*(?:e-?[0-9]+)?/[^/]+$")
    zero_dir = re.compile(r"/0/[^/]+$")
    output = [p for p in tracked if time_dir.search(p) and not zero_dir.search(p)]
    return {
        "population": "git ls-files -- TRACKED ONLY, not the filesystem",
        "tracked_files": len(tracked),
        "solver_output_files": len(output),
        "initial_condition_files": sum(1 for p in tracked if zero_dir.search(p)),
        "case_dict_files": sum(
            1 for p in tracked if re.search(r"/(constant|system)/", p)),
        "log_files": sum(1 for p in tracked if re.search(r"(^|/)log\.", p)),
        "under_runs_dirs": sum(
            1 for p in tracked if re.search(r"(^|/)[A-Za-z0-9_]+_runs/", p)),
    }


def memory_store() -> dict:
    """The out-of-repo store. Counted because the map cites its size.

    Reported as unreachable rather than zero when the directory is absent: this
    script runs on a fresh clone too, where the store genuinely does not exist,
    and a zero there would read as 'the store is empty' rather than 'this is not
    that machine'. A count that cannot distinguish those is the fail-open shape.
    """
    if not MEMORY_STORE.is_dir():
        return {"population": str(MEMORY_STORE), "reachable": False}
    files = sorted(p for p in MEMORY_STORE.glob("*.md"))
    return {
        "population": f"{MEMORY_STORE}/*.md",
        "reachable": True,
        "files": len(files),
        "indexed_in_MEMORY_md": sum(
            1 for line in _read_store_index().splitlines()
            if line.strip().startswith("- [")),
    }


def _read_store_index() -> str:
    index = MEMORY_STORE / "MEMORY.md"
    if not index.is_file():
        return ""
    return index.read_text(encoding="utf-8", errors="replace")


def collect() -> dict:
    sha, dirty = _head()
    return {
        "commit": sha,
        "working_tree_dirty": dirty,
        "frame": "tracked files (git ls-files); NOT the filesystem, NOT grep -r",
        "lessons": lesson_figures(),
        "product_list": product_list_figures(),
        "citations": citation_ranking(),
        "tracked_shape": tracked_shape(),
        "memory_store": memory_store(),
    }


def _emit(data: dict) -> None:
    sha = data["commit"]
    dirty = " +dirty working tree" if data["working_tree_dirty"] else ""
    print(f"CORPUS FIGURES at {sha}{dirty}")
    print(f"FRAME: {data['frame']}")
    print()

    les = data["lessons"]
    gaps = les["missing_below_highest"]
    gap_note = f", gaps at {gaps}" if gaps else ", no gaps"
    print(f"LESSONS.md  {les['lines']} lines, {les['bytes'] // 1024} KB, "
          f"{les['blocks']} blocks, {les['distinct_numbers']} distinct numbers, "
          f"highest L-{les['highest']}{gap_note}")
    # THE CONSTRAINT, PRINTED RATHER THAN LEFT TO BE NOTICED. A single number
    # has nothing to be wrong against and is believed exactly as far as it is
    # plausible; a number with a second quantity that constrains it, derived by
    # a different route, can be caught. Here: blocks minus distinct IS the count
    # of duplicate occurrences, and the duplicate list is found by a separate
    # pass. A shell pipeline reported three duplicated lesson numbers on this
    # file when there are two -- and the wrong answer survived because the
    # corpus really does carry duplicates, so it sat inside what a reader
    # already believed. This line is the check that reader would have needed.
    dup = les["duplicated"]
    excess = les["blocks"] - les["distinct_numbers"]
    agrees = "agrees" if excess == sum(n - 1 for n in dup.values()) else "DISAGREES"
    print(f"            check: {les['blocks']} - {les['distinct_numbers']} = "
          f"{excess} duplicate occurrence(s); the duplicate pass names "
          f"{sorted(dup)} -- {agrees}")

    pl = data["product_list"]
    by = pl["by_status"]
    print(f"PRODUCT_LIST  {pl['lines']} lines, {pl['items']} items "
          f"({', '.join(f'{v} {k}' for k, v in sorted(by.items()))}), "
          f"{pl['changelog_entries']} changelog entries")

    cit = data["citations"]
    top = ", ".join(f"{k} ({v})" for k, v in cit["top"])
    print(f"MOST-CITED  {cit['total_citations']} citations of "
          f"{cit['cited_lessons']} lessons across the corpus: {top}")

    ts = data["tracked_shape"]
    print(f"TRACKED SHAPE  {ts['tracked_files']} files: "
          f"{ts['solver_output_files']} solver output (non-zero time dirs), "
          f"{ts['log_files']} logs, {ts['initial_condition_files']} initial "
          f"conditions, {ts['case_dict_files']} case dictionaries, "
          f"{ts['under_runs_dirs']} under *_runs/")

    ms = data["memory_store"]
    if ms.get("reachable"):
        print(f"MEMORY STORE  {ms['files']} files, "
              f"{ms['indexed_in_MEMORY_md']} indexed in MEMORY.md")
    else:
        print(f"MEMORY STORE  UNREACHABLE from here ({ms['population']}) -- "
              f"this is expected on any machine but the owner's, and is "
              f"reported as unreachable rather than as zero")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true",
                        help="emit JSON for a doc build or a test")
    args = parser.parse_args(argv)
    data = collect()
    if args.json:
        json.dump(data, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        _emit(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
