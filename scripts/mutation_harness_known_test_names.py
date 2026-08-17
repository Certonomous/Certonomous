#!/usr/bin/env python3
"""Planted-error control for `check_absolutes.known_test_names`'s FRAME.

WHAT WAS WRONG. `known_test_names()` decides whether a test named in an
absolute's prose actually exists. An absolute naming a test the function
cannot find is condemned `CITES_MISSING_CHECK`, which is the severe class.
Until this harness landed, the function enumerated the corpus with
`git ls-files` -- that is, from the INDEX. HEAD is the referent; the index is
a per-machine, per-moment scratch state no reader of a clone ever sees.
`scripts/lab_check.py:tracked_frame` carries the same repair under D274.

WHY THE BIAS IS THE WORST AVAILABLE ONE. This lab lands commits with a
PRIVATE INDEX (`GIT_INDEX_FILE=<tmp> git add` -> `write-tree` -> `commit-tree`
-> `update-ref`), which leaves the committed file with NO shared-index entry
at all. So the tests the old frame could not see were disproportionately the
NEWEST, and the claims most likely to be freshly evidenced were the ones most
likely to be called unevidenced. Measured in the live checkout: 2,597 names
off the index against 2,658 off HEAD -- 61 real test functions unable to back
a claim -- with 477 paths in HEAD and absent from the index and ZERO in the
index and absent from HEAD. The asymmetry names them as landed work the index
has not caught up with. The gap grows with every such commit.

WHY THE CONTROL HAS TO BE SHAPED THIS WAY, and this is the whole point of the
file: A NORMALLY STAGED FILE PASSES THROUGHOUT THE BROKEN PERIOD. Build the
positive control out of an ordinary `git add`-ed test and it is green before
the repair and green after it, and proves nothing whatever. The failing case
MUST be a file landed by the private-index form. Both are built below, and the
normally-staged one is asserted to be INSENSITIVE to the repair, so the
control's own discriminating power is measured rather than assumed.

AND THE REPAIR MUST NOT BE A BLINDING. Widening what counts as "known" until
nothing is condemned would also turn the frame green. So a third probe names a
test that exists in neither frame and must stay unknown to both, and a fourth
drives the whole condemnation path end to end: a planted absolute citing that
name must still come back CITES_MISSING_CHECK after the repair.

    python3 scripts/mutation_harness_known_test_names.py

Exit 0 when every control lands as specified, 1 otherwise.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))


def git(root: Path, *args: str, env: dict | None = None) -> str:
    e = dict(os.environ)
    e.update({
        "GIT_AUTHOR_NAME": "harness", "GIT_AUTHOR_EMAIL": "h@example.invalid",
        "GIT_COMMITTER_NAME": "harness", "GIT_COMMITTER_EMAIL": "h@example.invalid",
    })
    if env:
        e.update(env)
    p = subprocess.run(["git", "-C", str(root), *args],
                       capture_output=True, text=True, env=e)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout.strip()


#: The PRE-REPAIR enumeration, reproduced so the two frames are compared
#: against each other rather than one of them being described in prose.
def names_from_index(root: Path) -> set[str]:
    return _harvest(root, git(root, "ls-files", "-z").split("\0"))


def names_from_head(root: Path) -> set[str]:
    return _harvest(root, git(root, "ls-tree", "-r", "-z",
                              "--name-only", "HEAD").split("\0"))


def _harvest(root: Path, rels: list[str]) -> set[str]:
    names: set[str] = set()
    for rel in rels:
        if not rel.endswith(".py"):
            continue
        if "test" not in Path(rel).name and "/tests/" not in rel:
            continue
        try:
            body = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        names.update(m.group(1) for m in
                     re.finditer(r"^\s*def\s+(test_\w+)", body, re.MULTILINE))
        names.update(m.group(1) for m in
                     re.finditer(r"^\s*class\s+(\w*Tests?)\b", body, re.MULTILINE))
    return names


ORDINARY = "test_landed_by_an_ordinary_stage"
PRIVATE = "test_landed_by_the_private_index_form"
ABSENT = "test_this_name_is_in_neither_frame"


def build(root: Path) -> None:
    """A repo holding one normally staged test and one privately landed one."""
    git(root, "init", "-q", "-b", "main")
    (root / "sdk" / "tests").mkdir(parents=True)

    # --- control A: the ordinary path. Staged, then committed. In BOTH frames.
    (root / "sdk" / "tests" / "test_ordinary.py").write_text(
        f"def {ORDINARY}():\n    assert True\n")
    git(root, "add", "--", "sdk/tests/test_ordinary.py")
    git(root, "commit", "-q", "-m", "ordinary")

    # --- control B: THE DISCRIMINATING ONE. Landed by this lab's own
    # private-index protocol, so it is in HEAD with no shared-index entry.
    (root / "sdk" / "tests" / "test_private_index.py").write_text(
        f"def {PRIVATE}():\n    assert True\n")
    idx = root / ".prividx"
    env = {"GIT_INDEX_FILE": str(idx)}
    git(root, "read-tree", "HEAD", env=env)
    git(root, "add", "--", "sdk/tests/test_private_index.py", env=env)
    tree = git(root, "write-tree", env=env)
    head = git(root, "rev-parse", "HEAD")
    commit = git(root, "commit-tree", tree, "-p", head, "-m", "private-index land")
    git(root, "update-ref", "HEAD", commit)
    idx.unlink()


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "repo"
        root.mkdir()
        build(root)

        idx_names = names_from_index(root)
        head_names = names_from_head(root)
        in_head_only = sorted(head_names - idx_names)
        in_index_only = sorted(idx_names - head_names)

        import check_absolutes
        live = check_absolutes.known_test_names(root)

        # END TO END: the condemnation path itself, not just the name set.
        # An absolute citing the privately landed test must be BACKED, and one
        # citing a name that exists nowhere must stay CITES_MISSING_CHECK.
        resolved_p, dangling_p = check_absolutes._named_checks(
            f"Every case is checked; see {PRIVATE} for the proof.", live, None)
        resolved_a, dangling_a = check_absolutes._named_checks(
            f"Every case is checked; see {ABSENT} for the proof.", live, None)

        rows = [
            ("POS  privately landed test is INVISIBLE to the index frame",
             PRIVATE not in idx_names),
            ("POS  privately landed test IS visible to the HEAD frame",
             PRIVATE in head_names),
            ("POS  the shipped known_test_names() now sees it",
             PRIVATE in live),
            ("POS  an absolute citing it now RESOLVES end to end",
             PRIVATE in resolved_p and not dangling_p),
            ("CTL  normally staged test is visible to BOTH frames, so a",
             ORDINARY in idx_names and ORDINARY in head_names),
            ("CTL    control built on it would be green before AND after the",
             True),
            ("CTL    repair, and would have measured nothing at all",
             True),
            ("NEG  a name in neither frame stays unknown to the index frame",
             ABSENT not in idx_names),
            ("NEG  ... stays unknown to the HEAD frame",
             ABSENT not in head_names),
            ("NEG  ... stays unknown to the shipped function",
             ABSENT not in live),
            ("NEG  ... and an absolute citing it is STILL condemned, so the",
             ABSENT in dangling_a and ABSENT not in resolved_a),
            ("NEG    repair narrows the frame and does not blind the class",
             True),
            ("DIR  the gap runs one way only: HEAD-only is non-empty",
             len(in_head_only) > 0),
            ("DIR  ... and index-only is empty",
             len(in_index_only) == 0),
        ]

        print("=" * 74)
        print("MUTATION HARNESS -- known_test_names reads HEAD, never the index")
        print("=" * 74)
        print(f"  scratch repo      {root}")
        print(f"  names off index   {len(idx_names)}  {sorted(idx_names)}")
        print(f"  names off HEAD    {len(head_names)}  {sorted(head_names)}")
        print(f"  HEAD-only         {in_head_only}")
        print(f"  index-only        {in_index_only}")
        print(f"  dangling, absent  {dangling_a}")
        print()
        bad = 0
        for label, got in rows:
            bad += not got
            print(f"  [{'ok' if got else 'FAIL'}] {label}")
        print()
        print(f"VERDICT: {'PASS' if not bad else 'FAIL'}  "
              f"({len(rows) - bad}/{len(rows)})")
        return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
