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
    # The runtime envelope first: what actually bound this run. `--ranks` is
    # a number the CALLER declares and the lab's cost arithmetic multiplies by
    # (core-minutes = wall x ranks / 60), and nothing used to check it against
    # the `-np` in the command that ran. A declared rank count nobody verified
    # is the rank-clamp defect with the clamp removed: the arithmetic is still
    # wrong and still silent.
    declared_ranks = os.environ.get("LEVER_ECHO_DECLARED_RANKS") or None
    observed_ranks = os.environ.get("LEVER_ECHO_OBSERVED_RANKS") or None
    if declared_ranks or observed_ranks:
        sys.stdout.write(lever_echo.runtime_envelope_block(
            ranks_declared=declared_ranks,
            ranks_observed=observed_ranks,
            # NOT_COMPARABLE, not UNCAPPED: "no limit was applied" and "these
            # two numbers cannot be compared" are different facts, and the
            # envelope exists so a later reader never has to guess which.
            ranks_agree=("NOT_COMPARABLE"
                         if observed_ranks in (None, "UNVERIFIABLE")
                         or declared_ranks is None
                         else str(declared_ranks == observed_ranks)),
            cost_basis=("ranks_observed" if observed_ranks
                        not in (None, "UNVERIFIABLE") else "ranks_declared")))
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
