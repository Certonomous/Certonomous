#!/usr/bin/env python3
r"""HEAD vs the worktree, section-wise, for the shared board `docs/LAB_STATE.md`.

WHY THIS FILE EXISTS
====================
`docs/USING_THIS_LAB.md:1111-1118` states the mechanism in its own words:

    **The write-back is part of the protocol, not an afterthought.** ... So
    **every private-index commit widens the gap between HEAD and the worktree**,
    monotonically, and nothing in the repository reports it. ... Any agent that
    edits the worktree copy and commits it **by pathspec** ... silently reverts
    every private-index row landed since the worktree last matched HEAD.

Lines 1120-1138 then make a reconciliation check a **precondition of touching**
the shared record -- BEFORE the edit, because afterwards the two sides have been
merged and the check can no longer say which side an entry came from. The lab
built two such checks, `check_docket_reconciliation.py` and
`check_record_reconciliation.py`, whose registered paths are `docs/DOCKET.md`,
`docs/LESSONS.md` and `docs/NUMERICS_KNOWLEDGE.md`.

`docs/LAB_STATE.md` is registered in none of them, and it is the file the rule
bites hardest: `scripts/lab_state_section.py` REFUSES to write the worktree at
all (its line 71), so a conforming board commit updates git and never the disk.
The worktree copy is therefore a MIXED-VINTAGE artifact -- fresh in every section
whose last committer wrote it, stale in every section whose last committer
conformed. Measured here 2026-08-23T19:55:53Z at HEAD `890bfa7f`: the worktree
matched NO commit in the file's history, being simultaneously AHEAD of HEAD in
`## closure` and `## cfd`, equal in four, and carrying a `## verification`
section that existed in no commit at all. This module is the sibling those two
checks are owed for the board.

WHAT IT CANNOT SEE, AND THIS IS NOT A SMALL GAP
===============================================
It compares HEAD against the WORKTREE. A stale base held in an agent's scratch
directory or in its own context is invisible to it. At least one of the four
2026-08-23 reverts had such a base: `890bfa7f` is byte-exactly `0bbe62dc` -- the
committer's OWN previous board commit, five minutes old -- plus its new section,
and no reading of the worktree would have predicted it. Run
`check_board_sections.py --at <sha>` for that failure mode; the two checks cover
different halves and neither covers both.

It also cannot tell you WHOSE a section's worktree text is. Every commit in this
repository carries one `Ubuntu` identity.

EXIT CONTRACT -- identical to the docket and record modules, deliberately
========================================================================
    0  PASS      every section is byte-identical between the committed blob and
                 the worktree
    1  FAIL      a section at HEAD is not in the worktree -- WRITE-BACK OWED.
                 The worktree lags; a committer sourcing from it here would
                 revert that section
    2  FAIL      a section's worktree text is in NO commit -- UNLANDED WORK.
                 Somebody's uncommitted draft; committing over it destroys it
    3  UNKNOWN   a side could not be read, either side parsed to zero sections,
                 or the planted control did not hold
    4  FAIL      a duplicate `## ` heading on either side
    5  a planted control in --selftest did not behave as required
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import control_kind  # noqa: E402
from check_board_sections import (  # noqa: E402
    BOARD_PATH, PREAMBLE, split_sections,
)

EXIT_PASS = 0
EXIT_FAIL_WRITEBACK_OWED = 1
EXIT_FAIL_UNLANDED = 2
EXIT_UNKNOWN = 3
EXIT_FAIL_DUPLICATE = 4
EXIT_CONTROL_BROKEN = 5

DEFAULT_REV = "HEAD"
DEFAULT_HISTORY_LIMIT = 80


def duplicate_headings(text: str) -> list[str]:
    seen: dict[str, int] = {}
    for line in text.splitlines():
        if line.startswith("## "):
            name = line[3:].strip()
            seen[name] = seen.get(name, 0) + 1
    return sorted(n for n, c in seen.items() if c > 1)


def read_rev(repo: Path, rev: str, path: str) -> tuple[str | None, str]:
    done = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True, text=True)
    if done.returncode != 0:
        detail = done.stderr.strip().splitlines()
        return None, (detail[-1] if detail else f"git exited {done.returncode}")
    return done.stdout, ""


def history(repo: Path, path: str, limit: int) -> list[tuple[str, str]]:
    done = subprocess.run(
        ["git", "-C", str(repo), "log", f"-{limit}", "--format=%H|%ci", "--", path],
        capture_output=True, text=True)
    rows = []
    for line in done.stdout.splitlines():
        sha, _, when = line.partition("|")
        if sha:
            rows.append((sha, when))
    return rows


def provenance(repo: Path, path: str, section: str, text: str,
               limit: int) -> tuple[str, str] | None:
    """Newest commit whose `section` reads exactly `text`, or None."""
    for sha, when in history(repo, path, limit):
        blob, err = read_rev(repo, sha, path)
        if blob is None:
            continue
        if split_sections(blob).get(section) == text:
            return sha, when
    return None


def run_controls() -> control_kind.ControlLedger:
    """Plant HEAD/worktree divergences and prove the comparator sees them.

    RECOGNITION, not reachability. A PASS from this module is a ZERO -- an empty
    set of diverging sections -- and rule 3 says a zero from a reader not shown
    able to see a non-zero is not evidence. Two of the four planted forms are
    invisible to a comparator that only diffs the bodies of headings present on
    both sides, which is exactly the mistake this control exists to catch.
    """
    committed = ("preamble\n## CHIEF - directives\nchief\n"
                 "## closure\nclosure v1\n## dafoam\ndafoam v1\n")
    forms = {
        "a section edited in the worktree":
            committed.replace("dafoam v1", "dafoam v1 EDITED"),
        "a section missing from the worktree":
            committed.replace("## dafoam\ndafoam v1\n", ""),
        "a section only in the worktree":
            committed + "## cfd\nbrand new\n",
        "a heading altered in the worktree":
            committed.replace("## dafoam", "## dafoam-team"),
    }
    planted = {}
    for name, worktree in forms.items():
        a, b = split_sections(committed), split_sections(worktree)
        names = dict.fromkeys(list(a) + list(b))
        planted[name] = any(a.get(n) != b.get(n) for n in names)

    a = split_sections(committed)
    negatives = {
        "an identical worktree": any(
            a.get(n) != split_sections(committed).get(n) for n in a),
    }
    ledger = control_kind.ControlLedger(
        claim_class=f"a section of {BOARD_PATH} differing between HEAD and the worktree")
    ledger.plant("board divergence forms",
                 vocabulary=f"{BOARD_PATH} `## ` sections",
                 planted=planted, negative=negatives)
    return ledger


def reconcile(committed_text: str, worktree_text: str,
              ledger: control_kind.ControlLedger | None = None) -> dict:
    """Pure, so the controls and any test can drive it on fixtures."""
    ledger = run_controls() if ledger is None else ledger
    a, b = split_sections(committed_text), split_sections(worktree_text)
    names = list(dict.fromkeys(list(a) + list(b)))
    differing = [n for n in names if a.get(n) != b.get(n)]
    head_only = [n for n in names if n in a and n not in b]
    worktree_only = [n for n in names if n in b and n not in a]

    dupes = sorted(set(duplicate_headings(committed_text))
                   | set(duplicate_headings(worktree_text)))

    zero_verdict, zero_why = ledger.verdict_for(len(differing))
    return {"path": BOARD_PATH, "differing": differing,
            "head_only": head_only, "worktree_only": worktree_only,
            "duplicates": dupes,
            "n_committed": len(a), "n_worktree": len(b),
            "zero_verdict": zero_verdict, "zero_because": zero_why,
            "ledger": ledger}


def classify(result: dict, unlanded: list[str]) -> tuple[str, int, str]:
    ledger = result["ledger"]
    if result["n_committed"] <= 1 or result["n_worktree"] <= 1:
        return "UNKNOWN", EXIT_UNKNOWN, (
            f"a side parsed to {min(result['n_committed'], result['n_worktree'])} "
            f"`## ` section(s) -- the file changed shape; do not work around it")
    if ledger.kind == control_kind.BROKEN:
        return "UNKNOWN", EXIT_UNKNOWN, (
            f"the planted control did not hold: {result['zero_because']}")
    if result["duplicates"]:
        return "FAIL", EXIT_FAIL_DUPLICATE, (
            f"duplicate `## ` heading(s): {', '.join(result['duplicates'])} -- "
            f"section identity is ambiguous and nothing below can be trusted")
    if unlanded:
        return "FAIL", EXIT_FAIL_UNLANDED, (
            f"{len(unlanded)} section(s) whose worktree text is in NO commit: "
            f"{', '.join(unlanded)}. UNLANDED WORK -- inspect, never revert; "
            f"committing a board over this destroys it")
    if result["differing"]:
        return "FAIL", EXIT_FAIL_WRITEBACK_OWED, (
            f"{len(result['differing'])} section(s) differ and every one is "
            f"older on disk than in git: {', '.join(result['differing'])}. "
            f"WRITE-BACK OWED -- a commit sourced from the worktree here would "
            f"revert them")
    return "PASS", EXIT_PASS, "every section is byte-identical on both sides"


def render(result: dict, rev: str, worktree_file: Path,
           prov: dict[str, tuple[str, str] | None],
           verdict: str, code: int, why: str) -> None:
    print("=" * 78)
    print(f"BOARD RECONCILIATION -- {result['path']}")
    print("=" * 78)
    print(f"  committed side : {rev}:{result['path']}  "
          f"({result['n_committed']} sections)")
    print(f"  worktree side  : {worktree_file}  ({result['n_worktree']} sections)")
    if result["differing"]:
        print("  diverging sections, with the newest commit their WORKTREE text "
              "matches:")
        for name in result["differing"]:
            label = name if name != PREAMBLE else "(preamble)"
            hit = prov.get(name)
            where = (f"{hit[0][:8]}  {hit[1][:19]}" if hit
                     else "NO COMMIT -- unlanded draft")
            side = ("HEAD only" if name in result["head_only"]
                    else "worktree only" if name in result["worktree_only"]
                    else "both, differing")
            print(f"      {label:<34} [{side:<15}] {where}")
    else:
        print("  diverging sections: (none)")
    print(result["ledger"].render(len(result["differing"])))
    print("-" * 78)
    print(f"VERDICT: {verdict}   (exit {code})")
    print(f"BECAUSE: {why}")
    print(f"CANNOT SEE: a stale base held in an agent's scratch or context. "
          f"`890bfa7f` reverted two teams from a base that was its own previous "
          f"commit, not the worktree, and this check would have read PASS. "
          f"Use check_board_sections.py --at <sha> for that half.")


def selftest() -> int:
    committed = ("preamble\n## CHIEF - directives\nchief\n"
                 "## closure\nclosure v1\n## dafoam\ndafoam v1\n")
    checks: list[tuple[str, bool, str]] = []

    r = reconcile(committed, committed)
    v, c, _ = classify(r, [])
    checks.append(("identical sides -> PASS", c == EXIT_PASS, f"exit {c}"))

    # PLANTED: the worktree lags on a section that exists in an older commit
    stale = committed.replace("dafoam v1", "dafoam v0")
    r = reconcile(committed, stale)
    v, c, _ = classify(r, [])
    checks.append(("PLANTED stale worktree section -> WRITE-BACK OWED",
                   c == EXIT_FAIL_WRITEBACK_OWED and "dafoam" in r["differing"],
                   f"exit {c}"))

    # PLANTED: a worktree section in no commit at all
    r = reconcile(committed, stale)
    v, c, _ = classify(r, ["dafoam"])
    checks.append(("PLANTED unlanded worktree section -> UNLANDED (2 beats 1)",
                   c == EXIT_FAIL_UNLANDED, f"exit {c}"))

    # PLANTED: a duplicate heading outranks both
    dup = committed + "## dafoam\nsecond copy\n"
    r = reconcile(committed, dup)
    v, c, _ = classify(r, ["dafoam"])
    checks.append(("PLANTED duplicate heading -> DUPLICATE (4 beats 2)",
                   c == EXIT_FAIL_DUPLICATE, f"exit {c}"))

    # PLANTED: a section present at HEAD and absent from the worktree
    gone = committed.replace("## dafoam\ndafoam v1\n", "")
    r = reconcile(committed, gone)
    v, c, _ = classify(r, [])
    checks.append(("PLANTED section deleted from the worktree -> caught",
                   c == EXIT_FAIL_WRITEBACK_OWED and "dafoam" in r["head_only"],
                   f"exit {c}"))

    # a side that parses to nothing is UNKNOWN, never PASS
    r = reconcile(committed, "no headings here at all\n")
    v, c, _ = classify(r, [])
    checks.append(("worktree parses to zero sections -> UNKNOWN",
                   c == EXIT_UNKNOWN, f"exit {c}"))

    ledger = run_controls()
    checks.append(("planted control reaches RECOGNITION",
                   ledger.kind == control_kind.RECOGNITION, ledger.kind))

    print("=" * 78)
    print("check_board_reconciliation.py --selftest")
    print("=" * 78)
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}   [{detail}]")
    print(ledger.render(0))
    ok = all(x[1] for x in checks)
    print("-" * 78)
    print(f"VERDICT: {'PASS' if ok else 'FAIL'}")
    return EXIT_PASS if ok else EXIT_CONTROL_BROKEN


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--rev", default=DEFAULT_REV)
    ap.add_argument("--path", default=BOARD_PATH)
    ap.add_argument("--history-limit", type=int, default=DEFAULT_HISTORY_LIMIT)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    repo = Path(a.repo).resolve()
    worktree_file = repo / a.path
    committed, err = read_rev(repo, a.rev, a.path)
    if committed is None:
        print(f"UNKNOWN: could not read {a.rev}:{a.path} -- {err}")
        return EXIT_UNKNOWN
    if not worktree_file.exists():
        print(f"UNKNOWN: {worktree_file} is not on disk")
        return EXIT_UNKNOWN
    worktree = worktree_file.read_text(encoding="utf8")

    result = reconcile(committed, worktree)
    prov: dict[str, tuple[str, str] | None] = {}
    unlanded: list[str] = []
    for name in result["differing"]:
        if name in result["head_only"]:
            prov[name] = None
            continue
        hit = provenance(repo, a.path, name, split_sections(worktree)[name],
                         a.history_limit)
        prov[name] = hit
        if hit is None:
            unlanded.append(name)

    verdict, code, why = classify(result, unlanded)
    if a.json:
        out = {k: v for k, v in result.items() if k != "ledger"}
        out.update({"verdict": verdict, "exit": code, "because": why,
                    "unlanded": unlanded, "control_kind": result["ledger"].kind,
                    "provenance": {k: (v[0] if v else None)
                                   for k, v in prov.items()}})
        print(json.dumps(out, indent=2))
    else:
        render(result, a.rev, worktree_file, prov, verdict, code, why)
    return code


if __name__ == "__main__":
    sys.exit(main())
