#!/usr/bin/env python3
"""D6R3 MULTIPOINT STAGER -- derives the arm's runScript.py from the FROZEN producer by inserting
ONE daOptions block, and REFUSES (exit 10) on anything else.

THE FROZEN PRODUCER IS NEVER EDITED.  It is read, one block is inserted into the staged COPY, and
the diff is asserted to be exactly that block.

WHAT IS INSERTED, and it is DAFoam's OWN published convergence mode -- not an invention:

    "primalFuncStdTol": {
        "stdTol": 3.0e-05,
        "slopeTol": 3.0e-05,
        "funcNames": ["CD"],
        "nStepsFrac": 0.25,
    },

Read from the installed source rather than from documentation:
  DASolver.C:99-110   reads stdTol, slopeTol (auto-set to stdTol if absent), funcNames, nStepsFrac
  DASolver.C:230-262  calcFuncStd(): window = round(nStepsFrac * (timeIndex)),
                      funcStd = sqrt(mean((f-mean)^2)) / |mean|  -- a RELATIVE standard deviation
  DASolver.C:188      converged if  primalMaxRes < primalMinResTol
                                OR (funcStd < stdTol AND |funcSlope| < slopeTol),  past primalMinIters
  DASolver.C:2730     checkPrimalFailure() returns 0 whenever stdTol > 0 -- the residual abort is
                      DISABLED BY THIS OPTION, so primalMinResTolDiff is NEVER RAISED and stays at
                      its published default 1.0e2 (pyDAFoam.py:517).

usage: d6r3_mp_stage_runscript.py <frozen_producer> <staged_output>
"""
import hashlib
import sys

FROZEN_MD5 = "efc3e62699690edd32e4ee910aad09c8"

ANCHOR = '    "primalMinResTol": 1.0e-8,\n'
BLOCK = '''    "primalMinResTol": 1.0e-8,
    # --- D6R3 MULTIPOINT, THE ONLY INSERTED BLOCK.  DAFoam's OWN published convergence mode.
    # --- Registered in D6R3_MULTIPOINT_PREREGISTRATION.md Amendment 2.  Setting stdTol > 0 makes
    # --- DASolver::checkPrimalFailure() return 0 (DASolver.C:2730), so the residual-based abort is
    # --- disabled WITHOUT raising primalMinResTolDiff, which stays at its published default 1.0e2.
    # --- Convergence becomes: funcStd(CD) < stdTol AND |slope| < slopeTol over a trailing window of
    # --- nStepsFrac * steps  (DASolver.C:188, :230-262).  Drag stability IS the gate.
    "primalFuncStdTol": {
        "stdTol": 3.0e-05,
        "slopeTol": 3.0e-05,
        "funcNames": ["CD"],
        "nStepsFrac": 0.25,
    },
'''


def main(src, dst):
    raw = open(src).read()
    got = hashlib.md5(raw.encode()).hexdigest()
    if got != FROZEN_MD5:
        print("REFUSE: producer md5 %s, frozen %s" % (got, FROZEN_MD5))
        return 10
    if raw.count(ANCHOR) != 1:
        print("REFUSE: the anchor line occurs %d times, expected exactly 1" % raw.count(ANCHOR))
        return 10
    if "primalFuncStdTol" in raw:
        print("REFUSE: the frozen producer already carries primalFuncStdTol")
        return 10
    out = raw.replace(ANCHOR, BLOCK)
    open(dst, "w").write(out)

    # ASSERT the staged file differs from the frozen one by EXACTLY the inserted block
    a, b = raw.split("\n"), out.split("\n")
    added = len(b) - len(a)
    if added != len(BLOCK.split("\n")) - 2:
        print("REFUSE: staged file added %d lines, expected %d"
              % (added, len(BLOCK.split("\n")) - 2))
        return 10
    # every original line must still be present, in order
    i = 0
    for ln in a:
        while i < len(b) and b[i] != ln:
            i += 1
        if i >= len(b):
            print("REFUSE: an original producer line is missing from the staged file: %r" % ln)
            return 10
        i += 1
    print("D6R3_MP_STAGE OK src=%s md5=%s -> %s  (+%d lines, one block, every original line intact)"
          % (src, got, dst, added))
    # READ-BACK: the values the solver will actually read
    for key in ('"stdTol": 3.0e-05', '"slopeTol": 3.0e-05', '"funcNames": ["CD"]',
                '"nStepsFrac": 0.25'):
        if key not in open(dst).read():
            print("REFUSE: %s not readable back from the staged file" % key)
            return 10
    print("D6R3_MP_STAGE READBACK stdTol=3.0e-05 slopeTol=3.0e-05 funcNames=[CD] nStepsFrac=0.25")
    print("D6R3_MP_STAGE primalMinResTolDiff NOT PRESENT and NOT RAISED -- published default 1.0e2 stands")
    # Match an ASSIGNMENT, not the bare word: the inserted comment MENTIONS primalMinResTolDiff
    # to explain why it is NOT raised, and the first version of this guard fired on its own
    # documentation.  Driven to both sides below.
    body = open(dst).read().split("daOptions = {")[1].split("\n}")[0]
    if '"primalMinResTolDiff"' in body:
        print("REFUSE: primalMinResTolDiff is ASSIGNED in the staged daOptions; it must not be")
        return 10
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
