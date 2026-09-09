#!/usr/bin/env python3
"""T23G2Rn rule-4 completion instrument -- OPTION (b), the THIN WRAPPER.

======================================================================
DRAFT -- NOT FROZEN, NOTHING RUN
======================================================================
Authored by a heat-transfer lab-lane for the §2ba numerics successor T23G2Rn
(T23G2Rn_PREREGISTRATION.md section 5.1).  The supervisor picked OPTION (b): keep
the frozen `mark_done_t23.py` (blob 982e1db6622454c2e5cc3e9eb4d6811e87735b78)
BYTE-INVARIANT and reach the T23G2Rn levels through a thin import-wrapper instead
of editing the frozen file's allow-list.

WHAT THIS FILE IS, AND WHAT IT DELIBERATELY IS NOT.
  * IT IMPORTS `mark_done_t23` and REUSES ITS CLAUSE LOGIC VERBATIM.  It does NOT
    copy `check()`, `run()`, `read_status()`, `dict_num()`, `NEEDED`, `AGE_REF`,
    `INFRA` or the six completion clauses -- there is exactly one implementation
    of them, in the frozen file, and this wrapper calls it.  No drift is possible
    because there is nothing to drift.
  * IT WIDENS THE ALLOW-LIST IN MEMORY ONLY.  It rebinds `mark_done_t23.CASES`
    (an ALLOW-LIST; widening it can never make a failing case pass -- the same
    ground the v1.2/v1.3 in-file extensions rest on) to include
    `T23G2Rn_L1/L2/L3`, then delegates to `mark_done_t23.main`.  `run()` resolves
    the module global `CASES` at call time, so the widened tuple is what it
    checks.  The frozen file ON DISK is never written.

FAIL-CLOSED EXACTLY AS THE BASE (nothing is relaxed):
  * a name not in the widened allow-list is REFUSED (exit 2) by the base `run()`;
  * an absent STATUS file is REFUSED (exit 2) by the base `read_status()`;
  * an absent log.solve / absent case directory / any failed clause is NOT DONE
    (exit 1) by the base `check()`;
  * clauses 1-4, the FIXED-dt clause 5 (`n_exec == round(endTime/deltaT)`, which
    is `== endTime` because T23G2Rn uses `deltaT 1` exactly as T23G2R --
    build_t23g2r.py:562, inherited unchanged by build_t23g2rn.py), and the age
    guard against `0/housing/T` are the base's, unmodified.

CLAUSE-5 IS THE FIXED-dt FORM, NOT THE ADAPTIVE ONE, AND IT IS NOT REIMPLEMENTED.
The base reads `deltaT` from each case's own controlDict (mark_done_t23.py:161)
and computes `want = int(round(endTime/deltaT))` (mark_done_t23.py:234); with
`deltaT 1` this is `n_exec == endTime`, byte-for-byte the clause that graded the
T23G2R levels.  This wrapper changes none of it.

Usage (identical CLI to mark_done_t23.py):
    python3 mark_done_t23g2rn.py [CASE ...] [--root DIR] | --selftest
Exit: 0 all DONE, 1 at least one NOT DONE, 2 REFUSAL.  (`--selftest` runs the
base's own selftest over its unchanged CASES[0] forged case.)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mark_done_t23 as MD          # the frozen base; imported, never copied

# The T23G2Rn levels, added to the base's ALLOW-LIST in memory only.
T23G2RN_CASES = ("T23G2Rn_L1", "T23G2Rn_L2", "T23G2Rn_L3")


def widen_cases():
    """Rebind the base module's CASES to include the T23G2Rn levels, IN MEMORY.
    The frozen file on disk is untouched.  Additive: no base name is removed, so
    every case the frozen instrument accepted is still accepted, and the six
    clauses are unchanged.  Returns the widened tuple for the caller to log."""
    missing = tuple(c for c in T23G2RN_CASES if c not in MD.CASES)
    if missing:
        MD.CASES = tuple(MD.CASES) + missing
    return MD.CASES


def main(argv):
    widen_cases()
    # Delegate to the base's main -- which parses --root / --selftest and calls
    # the base run() -> check().  All completion logic is the base's.
    return MD.main(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
