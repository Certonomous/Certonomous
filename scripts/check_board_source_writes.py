#!/usr/bin/env python3
r"""Did a landed commit write a per-team board source that is not its own?

WHAT THIS EXISTS FOR
====================
`scripts/check_board_sections.py` grades the MONOLITH: one file,
`docs/LAB_STATE.md`, carrying a `## <team>` section per team, and it answers
"did this commit change a section that is not its own?" by reconstructing the
before/after blobs section-wise.

After the board migration that file is GENERATED (`merge_lab_state.py`) and the
writable surface moves to `docs/lab_state/<team>.md` -- one path per writer.
`check_board_sections.py` knows nothing about that layout (grep it: no
`lab_state/`), so at cutover the lab loses its only cross-team-write detector at
exactly the moment the layout changes. This file is its successor for the split
layout. Both are kept: the monolith check still grades history.

WHY A CHECK IS STILL NEEDED WHEN THE PATHS ARE ALREADY SEPARATE
===============================================================
The migration's whole claim is that path separation ends the clobber class, and
for the MECHANISM that produced it, that claim is exact. The private-index
protocol isolates by path -- `read-tree HEAD` then
`update-index --add -- <explicit paths>` -- and `update-index` reads the DISK, so
a correct `read-tree` does not protect against a stale working file and the CAS
proves the PARENT, never the TREE. With `docs/LAB_STATE.md` one path written by
six teams, that protocol provided NO isolation for this file: whoever committed
first published everyone's pending edits, and whoever committed from a stale
worktree deleted everyone else's (L-223 / L-483; three events on 2026-09-03:
`f996344f` 50 deletions, `1bc1775d` 265 deletions, and `d92356e2` which carried a
foreign board write intact but under the wrong authorship).

One file per team removes that mechanism outright, because a team that names only
its own path in `update-index` cannot reach a peer's. What it does NOT remove is
an agent naming the WRONG PATH -- a typo, a copied command line, a lane briefed
with another team's stem. That residual is small, but it is the entire remaining
way a peer's board is lost, and `lab_state_sources.py` records the owner of each
file as DATA that nothing enforces:

    TEAMS = [("closure", "closure-supervisor"), ...]   # owner, never checked

This file is what checks it.

THE VERDICT IS FAIL-CLOSED ON ATTRIBUTION
=========================================
Every commit in this repository carries one `Ubuntu` identity, so who wrote a
commit is NOT derivable from git (see the standing lesson: independence is not
verifiable from git). Attribution comes from a `Lab-Team:` trailer the committer
declares, the same convention `check_board_sections.py` uses. A commit that
touches a board source with NO attribution is `PENDING`, never `PASS`: an
ungradeable commit is not a clean one, and reporting it clean is precisely how a
foreign write survives review. `--team` supplies a REVIEWER'S CLAIM for auditing
pre-trailer history and is printed as such; a commit-declared trailer always wins.

DELETIONS ARE COUNTED AND PRINTED SEPARATELY
============================================
Sanaa, 2026-09-03: "board migration approved and shared-index deletions frozen
until it lands". Deletions are the signature of the clobber class -- a stale-base
write shows up as a large negative on someone else's content -- so this check
prints per-path deletion counts beside the verdict whether or not the ownership
clause fired. `--max-deletions` makes that a gate for a caller that wants one;
by default it is REPORTED, NOT GATED (the standard's default mode, Sanaa
2026-09-03), because a team legitimately pruning its own board is not a defect.

  exit 0   PASS   -- the commit touched only its own source (or none)
  exit 1   GATE FAIL -- a foreign board source was written
  exit 2   REFUSED -- bad invocation, unreadable revision, broken selftest
  exit 3   PENDING -- a board source was touched and attribution is unavailable

USAGE
    python3 scripts/check_board_source_writes.py                 # grade HEAD
    python3 scripts/check_board_source_writes.py --at <sha>
    python3 scripts/check_board_source_writes.py --range main~20..main
    python3 scripts/check_board_source_writes.py --selftest      # planted control
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_state_sources as srcs  # noqa: E402

REPO_DEFAULT = Path(srcs.REPO)
SRC_DIR = srcs.SRC_DIR_REL          # "docs/lab_state"
BOARD = srcs.BOARD_REL              # "docs/LAB_STATE.md"

TRAILER = re.compile(r"^Lab-Team:[ \t]*(\S+)[ \t]*$", re.M)


# ---------------------------------------------------------------- git plumbing

def git(repo: Path, *args: str) -> str:
    """Run git in `repo`, returning stdout. Raises on non-zero."""
    out = subprocess.run(["git", "-C", str(repo), *args],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout


def owners() -> dict[str, str]:
    """{'docs/lab_state/dafoam.md': 'dafoam', ...} -- the stem is the owning team.

    Derived from `lab_state_sources.order()` so a seventh team added to the
    roster cannot be silently ungraded here: that module asserts itself against
    `harness/teams.yaml`.
    """
    return {f"{SRC_DIR}/{stem}.md": stem for stem, _owner, _h in srcs.order()}


def numstat(repo: Path, sha: str) -> tuple[str, list[tuple[int, int, str]]]:
    """(parent_sha, [(added, deleted, path), ...]) for one commit.

    A root commit is graded against the empty tree. Binary rows ('-') are
    reported as -1 rather than dropped: a board source that has become binary is
    a finding, not a row to skip.
    """
    parents = git(repo, "rev-list", "--parents", "-n", "1", sha).split()
    parent = parents[1] if len(parents) > 1 else git(
        repo, "hash-object", "-t", "tree", "/dev/null").strip()
    raw = git(repo, "diff", "--numstat", "-M", parent, sha)
    rows: list[tuple[int, int, str]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        a, d, path = line.split("\t", 2)
        # rename rows arrive as `old => new`; grade the destination
        if " => " in path:
            path = path.split(" => ")[-1].rstrip("}")
        rows.append((-1 if a == "-" else int(a),
                     -1 if d == "-" else int(d), path))
    return parent, rows


def attribution(repo: Path, sha: str, asserted: str | None) -> tuple[str | None, str]:
    """(team, source). The commit's own trailer wins over any reviewer claim."""
    msg = git(repo, "log", "-1", "--format=%B", sha)
    m = TRAILER.search(msg)
    if m:
        return m.group(1).strip(), "commit trailer"
    if asserted:
        return asserted, "REVIEWER-ASSERTED (a claim, not evidence)"
    return None, "unavailable"


# ------------------------------------------------------------------- grading

def grade(rows, team, team_source, max_deletions):
    """Pure verdict function over one commit's numstat rows."""
    own = owners()
    touched = [(a, d, p) for (a, d, p) in rows if p in own]
    board_touched = [(a, d, p) for (a, d, p) in rows if p == BOARD]

    res = {
        "sources_touched": [p for _a, _d, p in touched],
        "foreign": [],
        "own": [],
        "board_hand_edit": [p for _a, _d, p in board_touched],
        "deletions": {p: d for a, d, p in touched},
        "team": team,
        "team_source": team_source,
        "notes": [],
    }

    if board_touched:
        res["notes"].append(
            f"{BOARD} is written in this commit. After cutover that file is "
            f"GENERATED by merge_lab_state.py; a hand edit to it is drift and "
            f"`merge_lab_state.py --check` (rc 4) is the instrument that grades "
            f"it. REPORTED, not gated here.")

    if not touched:
        res["verdict"] = "PASS"
        res["reason"] = "no per-team board source was written by this commit"
        return res

    if team is None:
        res["verdict"] = "PENDING"
        res["reason"] = (
            "a board source was written and no `Lab-Team:` trailer declares the "
            "writer. Attribution is not derivable from git in this repository "
            "(one Ubuntu identity), so this commit CANNOT be graded. An "
            "ungradeable commit is not a clean one.")
        return res

    for _a, _d, p in touched:
        (res["own"] if own[p] == team else res["foreign"]).append(p)

    total_del = sum(d for _a, d, _p in touched if d > 0)
    res["total_deletions"] = total_del

    if res["foreign"]:
        res["verdict"] = "GATE FAIL"
        res["reason"] = (
            f"commit declares Lab-Team: {team} and writes board sources owned by "
            f"{sorted({own[p] for p in res['foreign']})}. One writer per file is "
            f"the whole content of the migration; this commit defeats it.")
        return res

    if max_deletions is not None and total_del > max_deletions:
        res["verdict"] = "GATE FAIL"
        res["reason"] = (
            f"{total_del} deletions to its OWN source exceeds the caller's "
            f"--max-deletions {max_deletions}. Ownership is clean; the size is "
            f"not. A large negative on a board is the signature of a stale-base "
            f"write (L-483).")
        return res

    res["verdict"] = "PASS"
    res["reason"] = (f"wrote only {', '.join(res['own'])}, which {team} owns; "
                     f"{total_del} deletions")
    return res


def render(res, sha, parent):
    print(f"commit           : {sha}")
    print(f"parent           : {parent}")
    print(f"declared team    : {res['team'] or '(none)'}")
    print(f"attribution from : {res['team_source']}")
    print(f"board sources    : {', '.join(res['sources_touched']) or '(none)'}")
    if res["sources_touched"]:
        for p, d in res["deletions"].items():
            print(f"   deletions     : {d:>7}  {p}")
    for n in res["notes"]:
        print(f"NOTE             : {n}")
    print(f"VERDICT: {res['verdict']} -- {res['reason']}")


EXIT = {"PASS": 0, "GATE FAIL": 1, "PENDING": 3}


# ------------------------------------------------------------- planted control

def selftest() -> int:
    r"""PLANTED CONTROL: a real git repository, real commits, real numstat.

    Rule 3: a zero from a reader not shown able to see a non-zero is not
    evidence. So this does not assert that a clean commit passes and stop there
    -- that is a reachability probe and it would still pass if the ownership
    clause were deleted from `grade()`. It PLANTS a cross-team write and REFUSES
    unless the check names the foreign path.

    Four cases, each a distinct way the instrument could be wrong:

      1  clean      cfd writes docs/lab_state/cfd.md                -> PASS
      2  PLANTED    cfd writes docs/lab_state/dafoam.md             -> GATE FAIL
      3  PLANTED    cfd writes its own AND dafoam's in one commit   -> GATE FAIL
                    (the realistic shape: the foreign path rides along with a
                     legitimate one, so a check that stops at "found my own
                     file" passes it)
      4  no trailer, writes a source                                -> PENDING
                    (fail-closed: the ungradeable commit must not read clean)

    Case 3 is the one that matters. Case 2 alone would be satisfied by an
    instrument that merely counts paths.
    """
    banner = "PLANTED CONTROL -- check_board_source_writes.py"
    print(banner)
    print("=" * len(banner))
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        env = {**os.environ,
               "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

        def run(*a):
            r = subprocess.run(["git", "-C", str(repo), *a],
                               capture_output=True, text=True, env=env)
            if r.returncode != 0:
                raise RuntimeError(f"git {' '.join(a)}: {r.stderr}")
            return r.stdout

        run("init", "-q", "-b", "main")
        (repo / SRC_DIR).mkdir(parents=True)
        for stem, _o, heading in srcs.order():
            head = (srcs.TITLE_LINE if stem == "chief" else heading)
            (repo / SRC_DIR / f"{stem}.md").write_text(
                f"{head}\n\nbaseline line A\nbaseline line B\n")
        run("add", "-A")
        run("commit", "-q", "-m", "baseline")

        def commit(msg, edits):
            for rel, text in edits.items():
                (repo / rel).write_text(text)
            run("add", *edits)
            run("commit", "-q", "-m", msg)
            return run("rev-parse", "HEAD").strip()

        cfd_p, daf_p = f"{SRC_DIR}/cfd.md", f"{SRC_DIR}/dafoam.md"
        cfd_ok = "## cfd\n\nbaseline line A\nbaseline line B\ncfd new row\n"
        # the planted foreign write: dafoam's two baseline lines destroyed
        daf_bad = "## dafoam\n\nWRITTEN BY THE WRONG TEAM\n"

        cases = [
            ("1 clean own-file write",
             commit("cfd board\n\nLab-Team: cfd", {cfd_p: cfd_ok}),
             "cfd", "PASS", []),
            ("2 PLANTED foreign write, alone",
             commit("cfd board\n\nLab-Team: cfd", {daf_p: daf_bad}),
             "cfd", "GATE FAIL", [daf_p]),
            ("3 PLANTED foreign write riding along with own",
             commit("cfd board\n\nLab-Team: cfd",
                    {cfd_p: cfd_ok + "more\n",
                     daf_p: daf_bad + "and again\n"}),
             "cfd", "GATE FAIL", [daf_p]),
            ("4 board source written with NO attribution",
             commit("cfd board, no trailer", {cfd_p: cfd_ok + "x\n"}),
             None, "PENDING", []),
        ]

        for name, sha, expect_team, expect_verdict, expect_foreign in cases:
            _parent, rows = numstat(repo, sha)
            team, tsrc = attribution(repo, sha, None)
            res = grade(rows, team, tsrc, None)
            ok = res["verdict"] == expect_verdict
            if expect_foreign and sorted(res["foreign"]) != sorted(expect_foreign):
                ok = False
            if team != expect_team:
                ok = False
            print(f"  [{'ok' if ok else 'FAIL'}] {name}: "
                  f"{res['verdict']} foreign={res['foreign'] or '[]'}")
            if not ok:
                failures.append(
                    f"{name}: expected {expect_verdict} foreign={expect_foreign} "
                    f"team={expect_team}, got {res['verdict']} "
                    f"foreign={res['foreign']} team={team}")

    print()
    if failures:
        print("CONTROL DID NOT FIRE -- the instrument is broken, not clean:")
        for f in failures:
            print(f"  {f}")
        print("VERDICT: REFUSED (exit 2)")
        return 2
    print("The planted cross-team write was DETECTED in both its bare form and")
    print("its riding-along form, and the unattributed commit did NOT read clean.")
    print("A PASS from this check is therefore a measurement, not an absence.")
    print("VERDICT: PASS")
    return 0


# ------------------------------------------------------------------------ cli

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.split("\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=str(REPO_DEFAULT))
    ap.add_argument("--at", default="HEAD", help="commit sha to grade")
    ap.add_argument("--range", dest="rng",
                    help="grade every commit in a rev range, e.g. main~20..main")
    ap.add_argument("--team", help="REVIEWER-ASSERTED attribution, for auditing a "
                    "commit that predates the `Lab-Team:` trailer. It is a "
                    "reviewer's claim, printed as such; a commit-declared "
                    "trailer always wins")
    ap.add_argument("--max-deletions", type=int, default=None,
                    help="gate a commit whose deletions to its OWN source exceed "
                    "this. Off by default: reported, not gated")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    repo = Path(a.repo)
    try:
        srcs.assert_matches_roster()
    except Exception as e:                                    # noqa: BLE001
        print(f"REFUSED: the board manifest disagrees with the roster: {e}")
        return 2

    try:
        shas = ([s for s in git(repo, "rev-list", "--reverse", a.rng).split()]
                if a.rng else [git(repo, "rev-parse", a.at).strip()])
    except RuntimeError as e:
        print(f"REFUSED: {e}")
        return 2

    worst, results = 0, []
    for sha in shas:
        try:
            parent, rows = numstat(repo, sha)
        except RuntimeError as e:
            print(f"REFUSED: {e}")
            return 2
        team, tsrc = attribution(repo, sha, a.team)
        res = grade(rows, team, tsrc, a.max_deletions)
        res["sha"], res["parent"] = sha, parent
        results.append(res)
        if not a.json:
            render(res, sha, parent)
            if len(shas) > 1:
                print("-" * 70)
        worst = max(worst, EXIT[res["verdict"]])

    if a.json:
        print(json.dumps(results if a.rng else results[0], indent=2))
    return worst


if __name__ == "__main__":
    sys.exit(main())
