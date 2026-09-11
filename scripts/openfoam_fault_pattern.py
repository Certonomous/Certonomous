#!/usr/bin/env python3
"""ONE validated regex: does an OpenFOAM log carry a REAL solver fault?

This file exists because a pattern composed from memory got it wrong TWICE in one
night, in two independent cfd lanes, the same way.  It does one thing.  Import
``OPENFOAM_FAULT_PATTERN`` or call ``has_fault(text)``; run ``--selftest`` with no
arguments to prove the pattern can both stay quiet and speak.

-----------------------------------------------------------------------------
THE TRAP, MEASURED -- DO NOT "SIMPLIFY" THE PATTERN BACK INTO IT
-----------------------------------------------------------------------------
Every OpenFOAM log carries this at line 29, FROM ITERATION 0, on a perfectly
healthy run:

    trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).

It announces that FPE trapping is ARMED.  It is the OPPOSITE of a fault.  A
detector containing the bare substring ``Floating point exception`` matches it
on its FIRST poll of a healthy run.

  * 2026-09-10, an MRF lane: a state detector reported NOT_CONVERGED on THREE
    healthy runs off this line (M6CP1 Amendment 4; board block 134).
  * 2026-09-11, a DrivAer lane: a fault monitor fired on it two minutes after
    arming and EXITED -- so for three minutes "no notification" meant "nothing is
    watching", which is indistinguishable from "everything is fine".  That is the
    worst failure available to a monitor: its silence is read as health.

The first fix lived in one lane's own script and in an addendum.  A record did
not stop the second instance.  Hence a file with a test: records inform, code
refuses.

The second near-miss, one line further on (line 33 of a normal log):

    --> FOAM Warning : allowSystemOperations : ...

A pattern shortened to ``^--> FOAM`` matches that WARNING.  It must be
``^--> FOAM FATAL``.

BOTH near-misses are asserted in ``--selftest``: if someone widens the pattern to
match either line, the selftest FAILS.  That assertion is the structural guard --
the reason cannot be stepped over without stepping over a failing test.
-----------------------------------------------------------------------------
"""
from __future__ import annotations

import argparse
import re
import sys

#: Real fault signatures only.  Note what is deliberately ABSENT: the bare string
#: "Floating point exception" (matches the trapFpe banner) and the bare token
#: "signal" (far too generic).  An FPE that actually kills a run surfaces as
#: sigFpe::sigHandler in the stack, or as mpirun's "exited on signal 8".
OPENFOAM_FAULT_PATTERN = (
    r"^--> FOAM FATAL"                     # FOAM FATAL ERROR / FOAM FATAL IO ERROR
    r"|sigFpe::sigHandler"                 # a real trapped FPE, from the stack trace
    r"|sigSegv::sigHandler"                # a real segfault, from the stack trace
    r"|^\[\d+\] \*\*\*"                    # MPI abort banner
    r"|mpirun noticed that process rank"   # a rank died; mpirun says why
    r"|Segmentation fault"
    r"|signal \(8\)"                       # SIGFPE, as mpirun reports it
    r"|signal \(11\)"                      # SIGSEGV, as mpirun reports it
)

_RE = re.compile(OPENFOAM_FAULT_PATTERN, re.M)

#: Verbatim from a healthy run's log (DrivAer Stage A fine, 2026-09-11T00:35Z).
#: Kept in-file so --selftest needs no run directory and stays runnable after
#: every run tree on this box has been deleted.
HEALTHY_LOG_EXCERPT = """\
Build  : _481094f-20260618 OPENFOAM=2606 version=2606
Exec   : simpleFoam -parallel
nProcs : 8
Pstream initialized with:
    node communication : off [type=host] (8 ranks, 1 nodes)
trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
memory pool : not available
fileModificationChecking : Monitoring run-time modified files using timeStampMaster

--> FOAM Warning : allowSystemOperations : Allowing user-supplied system call operations.
                   This can be a security risk if running untrusted cases
Selecting turbulence model type RAS
Time = 1

smoothSolver:  Solving for Ux, Initial residual = 0.9999993362, Final residual = 0.007837773301, No Iterations 19
GAMG:  Solving for p, Initial residual = 1, Final residual = 0.009004667934, No Iterations 14
bounding omega, min: -584.353009 max: 17720.99561 average: 145.0878055
bounding k, min: -0.121 max: 157.2 average: 3.73
ExecutionTime = 15.57 s  ClockTime = 16 s
End
"""

#: Real fault signatures the pattern MUST catch, one per fault class.
FAULT_SIGNATURES = (
    "--> FOAM FATAL ERROR: ",
    "Foam::sigFpe::sigHandler(int) at ??:?",
    "mpirun noticed that process rank 3 with PID 0 on node ip-172-31-43-247 "
    "exited on signal 8 (Floating point exception).",
    "Segmentation fault",
)

#: Healthy lines that must NEVER match.  Both have bitten a lane.
MUST_NOT_MATCH = (
    "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).",
    "--> FOAM Warning : allowSystemOperations : Allowing user-supplied system call operations.",
)


def has_fault(text: str) -> str | None:
    """Return the first real fault signature in ``text``, or None."""
    m = _RE.search(text)
    return m.group(0) if m else None


def _selftest() -> int:
    bad = []
    print("openfoam_fault_pattern --selftest")

    # (1) SILENT on a healthy log -- including both lines that have bitten a lane.
    got = has_fault(HEALTHY_LOG_EXCERPT)
    ok = got is None
    print(f"  [{'PASS' if ok else 'FAIL'}] silent on a healthy log"
          + ("" if ok else f" -- matched {got!r}"))
    if not ok:
        bad.append("matched a healthy log")

    # (2) STRUCTURAL GUARD: neither known near-miss may match, on its own.
    #     Widen the pattern to the bare "Floating point exception" or to
    #     "^--> FOAM" and this fails.  That is the point.
    for line in MUST_NOT_MATCH:
        got = has_fault(line)
        ok = got is None
        print(f"  [{'PASS' if ok else 'FAIL'}] must NOT match: {line[:62]}..."
              + ("" if ok else f" -- matched {got!r}"))
        if not ok:
            bad.append(f"matched near-miss {line[:40]!r}")

    # (3) SPEAKS on every real fault class.
    for sig in FAULT_SIGNATURES:
        got = has_fault(HEALTHY_LOG_EXCERPT + sig + "\n")
        ok = got is not None
        print(f"  [{'PASS' if ok else 'FAIL'}] fires on: {sig[:62]}"
              + (f" -- matched {got!r}" if ok else " -- BLIND"))
        if not ok:
            bad.append(f"blind to {sig[:40]!r}")

    if bad:
        print(f"SELFTEST FAILED: {len(bad)} problem(s): {bad}")
        return 1
    print("SELFTEST OK -- shown able to stay quiet AND able to speak")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true",
                    help="validate the pattern in both directions; needs no arguments")
    ap.add_argument("--log", help="scan this OpenFOAM log; exit 1 if a fault is found")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.log:
        ap.error("give --selftest or --log <path>")
    with open(a.log, errors="replace") as fh:
        got = has_fault(fh.read())
    if got:
        print(f"FAULT: {got}")
        return 1
    print("no fault signature")
    return 0


if __name__ == "__main__":
    sys.exit(main())
