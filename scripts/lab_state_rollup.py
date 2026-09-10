#!/usr/bin/env python3
"""V-119 GENERATOR -- rebuild the docs/LAB_STATE.md rollup from its per-team sources.

Spec: docs/BOARD_MIGRATION_PROPOSAL.md s2 item 3 ("builds the rollup: preamble
template, then the seven sources in roster order").

The order is FIXED and DECLARED here, in ORDER (below), and it is the board's own
order at the migration revision -- not alphabetical, not directory order, because
a generator whose output order depends on the filesystem produces a different
board on a different box.

REFUSALS built in, per proposal s3:
  - zero source files -> REFUSE (limb `s2p.2`). "A board that emits an empty
    rollup reading 'nothing running' because its sources vanished is the worst
    output this tool can produce."
  - a declared source missing -> REFUSE. A rollup silently short one team is the
    same defect wearing a smaller hat.

THIS SCRIPT NEVER WRITES docs/LAB_STATE.md UNLESS EXPLICITLY POINTED AT IT.
Default is --dry-run; --write requires --out. The V-119 build task forbids
writing the live board, so --out defaults to nothing and must be given.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

HEADER_NAME = "LAB_STATE_HEADER.md"

# The declared order. Board order at HEAD 2026-09-10, measured with
# `git show HEAD:docs/LAB_STATE.md | grep -n '^## '`:
#   39 CHIEF, 1448 closure, 6673 dafoam, 19093 heat-transfer,
#   30683 cfd, 39580 verification, 42589 ansys-verification
ORDER = [
    "LAB_STATE_CHIEF.md",
    "LAB_STATE_CLOSURE.md",
    "LAB_STATE_DAFOAM.md",
    "LAB_STATE_HEAT-TRANSFER.md",
    "LAB_STATE_CFD.md",
    "LAB_STATE_VERIFICATION.md",
    "LAB_STATE_ANSYS-VERIFICATION.md",
]


def source_paths(srcdir: str) -> list[str]:
    return [os.path.join(srcdir, HEADER_NAME)] + [os.path.join(srcdir, n) for n in ORDER]


def build(srcdir: str) -> tuple[bytes, list[tuple[str, bytes]]]:
    """Concatenate header + declared sources in declared order. REFUSES on a gap."""
    paths = source_paths(srcdir)
    missing = [p for p in paths if not os.path.isfile(p)]
    if len(missing) == len(paths):
        raise SystemExit(f"REFUSED: zero source files under {srcdir} -- an empty rollup is "
                         "never emitted (proposal s3, limb s2p.2)")
    if missing:
        raise SystemExit("REFUSED: declared source(s) missing -- a rollup short a team is a "
                         "silent board loss:\n  " + "\n  ".join(missing))
    parts = []
    for p in paths:
        with open(p, "rb") as f:
            parts.append((os.path.basename(p), f.read()))
    return b"".join(b for _, b in parts), parts


def main() -> int:
    ap = argparse.ArgumentParser(description="V-119 rollup generator")
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--srcdir", default=os.path.join(repo, "docs"))
    ap.add_argument("--out", default=None, help="write HERE. Required with --write.")
    ap.add_argument("--compare", default=os.path.join(repo, "docs", "LAB_STATE.md"),
                    help="the current rollup to diff against (read-only)")
    ap.add_argument("--write", action="store_true", help="emit the rollup; without this it is a dry run")
    ap.add_argument("--dry-run", action="store_true", help="explicit no-op default")
    a = ap.parse_args()

    rollup, parts = build(a.srcdir)
    print("lab_state_rollup.py -- V-119 generator, spec docs/BOARD_MIGRATION_PROPOSAL.md s2.3")
    print(f"  srcdir           : {a.srcdir}")
    print(f"  declared order   : {len(ORDER)} team sources, header first")
    for name, b in parts:
        print(f"    {name:<34} {len(b):>8} bytes  sha256 {hashlib.sha256(b).hexdigest()[:16]}")
    print(f"  rollup           : {len(rollup)} bytes  sha256 {hashlib.sha256(rollup).hexdigest()[:16]}")

    if os.path.isfile(a.compare):
        with open(a.compare, "rb") as f:
            cur = f.read()
        if cur == rollup:
            print(f"  vs {a.compare}: IDENTICAL (0 bytes, 0 lines differ)")
        else:
            import difflib
            cl = cur.decode("utf-8", "replace").splitlines(True)
            rl = rollup.decode("utf-8", "replace").splitlines(True)
            n = sum(1 for d in difflib.ndiff(cl, rl) if d[0] in "+-")
            print(f"  vs {a.compare}: DIFFERS -- {len(rollup) - len(cur):+d} bytes, "
                  f"{n} differing lines ({len(cl)} -> {len(rl)} lines)")
    else:
        print(f"  vs {a.compare}: absent -- no comparison made")

    if not a.write:
        print("  --dry-run (default): nothing written.")
        print("VERDICT: OK")
        return 0
    if not a.out:
        raise SystemExit("REFUSED: --out is required with --write. This build does not write the "
                         "live board; adopting the generated board is Sanaa's call (CLAUDE.md rule 9).")
    with open(a.out, "wb") as f:
        f.write(rollup)
    print(f"  written          : {a.out}  ({len(rollup)} bytes)")
    print("VERDICT: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
