#!/usr/bin/env python3
"""Print the LEVER-ECHO block for THIS process's own working directory.

Run from inside the launched process, after any `cd`, so the block describes
the directory that actually executes rather than a path a caller supplied
describing what it intended (LESSONS.md L-45, Verification Charter v1.5 §9).

`scripts/launch_solve.sh` invokes this in the same shell that then `exec`s the
solver, so the working directory this reads is, by construction, the working
directory the solver inherits. There is no parameter here that could be wrong.

`LEVER_ECHO_DECLARED_CASE`, when set and non-empty, is the launcher's
`--case` argument. It is passed only so it can be DISAGREED with: a value that
does not resolve to this process's working directory refuses the echo with
both paths stated, instead of certifying dictionaries that may not be the ones
the solver opens.

Environment, not argv, because this is invoked from inside a single-quoted
`bash -c` string where every added quote is a new way to be wrong.

Exit status is always 0 and every failure is silent-but-stated: a launcher
must never be prevented from launching by its own bookkeeping. A missing block
costs a verification; a failed launch costs the run.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "sdk"))


def main() -> int:
    try:
        from chief_engineer import lever_echo
    except Exception as exc:  # the sdk is not importable from here
        sys.stdout.write(
            "==== LEVER-ECHO REFUSED ====\n"
            f"reason lever_echo is not importable: {type(exc).__name__}\n"
            "==== LEVER-ECHO REFUSED END ====\n")
        return 0
    declared = os.environ.get("LEVER_ECHO_DECLARED_CASE") or None
    try:
        sys.stdout.write(
            lever_echo.echo_block_for_run_dir(Path.cwd(), declared))
    except OSError as exc:
        sys.stdout.write(lever_echo.refusal_block(
            f"could not read the lever dictionaries: {type(exc).__name__}",
            run_directory=Path.cwd()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
