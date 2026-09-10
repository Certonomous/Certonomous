#!/usr/bin/env python3
"""V-119 STALENESS / DIGEST CHECK -- ADVISORY ONLY. ALWAYS EXITS 0.

Does the generated rollup still equal the concatenation of its per-team sources?
Two failure modes matter and both have this one observable signature (proposal
docs/BOARD_MIGRATION_PROPOSAL.md s2 item 4):
  (a) the rollup was HAND-EDITED -- somebody wrote the generated file directly;
  (b) the rollup is STALE -- a source moved and nobody regenerated.

=========================== ADVISORY, BY RULING ===============================
The proposal's s2.4 asks for a checker that REFUSES (exit 2) at a choke point.
THIS BUILD DOES NOT REFUSE AND IS WIRED INTO NOTHING. D539, this team's own
ruling, reserves "a checker that refuses" to Sanaa alone; arming this one --
turning a detection into a refusal, or terminating any invocation with `|| exit
1` -- is HERS, and no agent's message is her consent (CLAUDE.md rule 9).
Until she arms it this script PRINTS and exits 0. That is the exact shape the
proposal s3 calls a dead lever, and it is being shipped knowingly and labelled,
not shipped quietly.
===============================================================================

DETECTION IS NOT REFUSAL. --selftest proves this checker DETECTS a matching
rollup as matching and a MISMATCHING rollup as mismatching -- a checker that has
only ever been shown to pass is indistinguishable, from its verdicts alone, from
one that never looks (charter s2p.3(e), s2o). The selftest drives the PRODUCTION
comparison path via evaluate() and the production generator's build()
(s2p.3(d): a test that exercises a copy of the guarded logic tests nothing).

The selftest uses explicit `if not cond: sys.exit(2)` and NEVER `assert`:
`python3 -O` strips asserts and would turn a failing selftest green. L-332;
docketed again by this team today at D594.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_state_rollup import ORDER, HEADER_NAME, build, source_paths  # PRODUCTION generator

ADVISORY_BANNER = (
    "ADVISORY -- THIS CHECK DOES NOT REFUSE AND EXITS 0 WHATEVER IT FINDS.\n"
    "ADVISORY -- advisory under D539: 'a checker that refuses' is Sanaa's alone.\n"
    "ADVISORY -- arming it (exit 2, or `|| exit 1` at a choke point) is HERS, not any agent's."
)


def evaluate(srcdir: str, rollup_path: str) -> dict:
    """PRODUCTION comparison. Returns a finding dict; raises nothing the caller must handle."""
    out = {"match": None, "reason": "", "sources": [], "rollup_bytes": None, "expected_bytes": None}
    try:
        expected, parts = build(srcdir)
    except SystemExit as e:
        out["reason"] = f"sources unusable: {e}"
        return out
    out["sources"] = [(n, len(b), hashlib.sha256(b).hexdigest()) for n, b in parts]
    out["expected_bytes"] = len(expected)
    if not os.path.isfile(rollup_path):
        out["reason"] = f"rollup absent: {rollup_path}"
        return out
    with open(rollup_path, "rb") as f:
        cur = f.read()
    out["rollup_bytes"] = len(cur)
    out["match"] = (cur == expected)
    if out["match"]:
        out["reason"] = "rollup equals the concatenation of its declared sources"
    else:
        d = next((i for i in range(min(len(cur), len(expected))) if cur[i] != expected[i]),
                 min(len(cur), len(expected)))
        out["reason"] = (f"rollup DIFFERS from its sources: {len(cur) - len(expected):+d} bytes, "
                         f"first differing byte offset {d} -- hand-edited rollup, or stale "
                         f"(a source moved without regeneration)")
    return out


def report(f: dict, srcdir: str, rollup_path: str) -> None:
    print(ADVISORY_BANNER)
    print(f"check_lab_state_rollup.py -- srcdir {srcdir}")
    print(f"  rollup           : {rollup_path}")
    for n, ln, sha in f["sources"]:
        print(f"    {n:<34} {ln:>8} bytes  sha256 {sha[:16]}")
    print(f"  expected (sources concatenated): {f['expected_bytes']} bytes")
    print(f"  rollup on disk                 : {f['rollup_bytes']} bytes")
    if f["match"] is True:
        print("  FINDING          : MATCHES")
    elif f["match"] is False:
        print("  FINDING          : DOES NOT MATCH")
    else:
        print("  FINDING          : CANNOT SEE")
    print(f"  detail           : {f['reason']}")
    print(ADVISORY_BANNER)


def _mkcase(root: str) -> str:
    """Build a real source set + a correctly generated rollup, using the production generator."""
    src = os.path.join(root, "docs")
    os.makedirs(src, exist_ok=True)
    with open(os.path.join(src, HEADER_NAME), "w", encoding="utf-8", newline="") as fh:
        fh.write("# LAB_STATE -- selftest header\n\n")
    for i, n in enumerate(ORDER):
        with open(os.path.join(src, n), "w", encoding="utf-8", newline="") as fh:
            fh.write(f"## team{i}\nbody {i}\n\n")
    expected, _ = build(src)
    with open(os.path.join(root, "ROLLUP.md"), "wb") as fh:
        fh.write(expected)
    return src


def selftest() -> int:
    root = tempfile.mkdtemp(prefix="v119_selftest_")
    fails = []
    try:
        src = _mkcase(root)
        rollup = os.path.join(root, "ROLLUP.md")

        # ARM 1 -- POSITIVE CONTROL: correctly generated rollup must be DETECTED as matching.
        f1 = evaluate(src, rollup)
        print(f"  arm 1 positive   : match={f1['match']} (expected True)")
        if f1["match"] is not True:
            fails.append("arm 1: a correctly generated rollup was NOT detected as matching")

        # ARM 2 -- PLANTED MISMATCH (a): one byte hand-edited INTO THE ROLLUP.
        with open(rollup, "rb") as fh:
            b = bytearray(fh.read())
        i = len(b) // 2
        b[i] = ord("X") if b[i] != ord("X") else ord("Y")
        with open(rollup, "wb") as fh:
            fh.write(bytes(b))
        f2 = evaluate(src, rollup)
        print(f"  arm 2 plant(roll): match={f2['match']} (expected False) -- one byte at offset {i}")
        if f2["match"] is not False:
            fails.append("arm 2: a one-byte hand edit in the rollup was NOT detected")

        # ARM 3 -- PLANTED MISMATCH (b): a SOURCE moved, rollup never regenerated (staleness).
        shutil.rmtree(root)
        src = _mkcase(root)
        rollup = os.path.join(root, "ROLLUP.md")
        p = os.path.join(src, ORDER[3])
        with open(p, "a", encoding="utf-8", newline="") as fh:
            fh.write("a source moved and nobody regenerated\n")
        f3 = evaluate(src, rollup)
        print(f"  arm 3 plant(src) : match={f3['match']} (expected False) -- {os.path.basename(p)} moved")
        if f3["match"] is not False:
            fails.append("arm 3: a moved source (stale rollup) was NOT detected")

        # ARM 4 -- the checker itself must never refuse: prove main() exits 0 on a MISMATCH.
        rc = subprocess.call([sys.executable, os.path.abspath(__file__),
                              "--srcdir", src, "--rollup", rollup],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  arm 4 exit code  : rc={rc} on a KNOWN MISMATCH (expected 0 -- advisory, D539)")
        if rc != 0:
            fails.append(f"arm 4: the advisory checker exited {rc} on a mismatch; it must exit 0")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # NO bare `assert` anywhere above or below: python3 -O strips them (L-332, D594).
    if fails:
        for m in fails:
            print("  SELFTEST FAIL    : " + m)
        print("VERDICT: SELFTEST FAIL")
        sys.exit(2)
    print("VERDICT: SELFTEST PASS -- matching DETECTED as matching, both mismatch plants DETECTED, "
          "and the checker still exits 0 (detection is not refusal).")
    return 0


def main() -> int:
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(description="V-119 rollup staleness check -- ADVISORY, always exit 0")
    ap.add_argument("--srcdir", default=os.path.join(repo, "docs"))
    ap.add_argument("--rollup", default=os.path.join(repo, "docs", "LAB_STATE.md"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    report(evaluate(a.srcdir, a.rollup), a.srcdir, a.rollup)
    return 0  # ALWAYS. D539.


if __name__ == "__main__":
    sys.exit(main())
