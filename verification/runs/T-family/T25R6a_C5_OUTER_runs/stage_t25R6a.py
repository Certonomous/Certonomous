#!/usr/bin/env python3
"""T25R6a STAGER -- build the four case directories for the outer-level probe.

Registration: docs/campaigns/T-family/T25R6a_PREREGISTRATION.md v1.1, section 9.

WHAT IT REUSES, AND WHY REUSE IS THE HONEST CHOICE HERE
-------------------------------------------------------
The load-bearing part of staging is `edit_controldict` -- the routine that
rewrites exactly three registered TOP-LEVEL controlDict keys and REFUSES on a
duplicate key, a missing key, or a donor whose value is not the expected one.
That routine is already committed, already frozen and already proven by T25R5.
It is IMPORTED here and blob-verified, not retyped: a retyped guard is a new
guard, and a new guard is unproven no matter how carefully it was copied.

Only the DESTINATION differs -- T25R6a's own run directory instead of T25R5's --
so only the destination is new code.

IT DOES NOT CREATE `0/` AND IT DOES NOT RUN decomposePar.  run_one_t25R6a.sh
does both, and REFUSES a case where `0/` or any time directory already exists:
`0/module/T` is touched LAST at launch and so DATES the run allowed to produce
the answer (rule 4's age guard).  A stager that pre-created `0/` would make the
age guard unevaluable for every arm.

    python3 stage_t25R6a.py --all
    python3 stage_t25R6a.py --arm C5 --level L3
"""
import hashlib
import importlib.util
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T25R5 = os.path.join(os.path.dirname(HERE), "T25R5_LINSOLVER_runs")
T25R4 = os.path.join(os.path.dirname(HERE), "T25R4_MODULE_runs")

# --- FROZEN, and verified by blob rather than asserted in prose.
STAGER_T25R5 = os.path.join(T25R5, "stage_t25R5.py")
STAGER_BLOB = "c4883cb96a3a16049d94fae4667ff31f068697a5"

# --- FROZEN AT PREREG 9: donors are T25R4's probe cases, one per level; arm
# --- dictionaries are T25R5's, UNCHANGED, which is what makes this rung's
# --- factors comparable to C4's to the digit.
DONORS = {"L1": "P1", "L3": "P3"}
ARMS = ["B0", "C5"]
LEVELS = ["L1", "L3"]
CASES = ["B0_L1", "C5_L1", "B0_L3", "C5_L3"]

EXIT_REFUSE = 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def git_blob(path):
    data = open(path, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def frozen_stager():
    """Import T25R5's stager AFTER verifying it is the registered blob."""
    if not os.path.isfile(STAGER_T25R5):
        refuse("the frozen stager is absent: %s" % STAGER_T25R5)
    got = git_blob(STAGER_T25R5)
    if got != STAGER_BLOB:
        refuse("stage_t25R5.py is NOT the registered blob.\n"
               "  registered %s\n  on disk    %s\n"
               "  Its edit_controldict is this stager's controlDict guard; a "
               "changed guard is an unproven guard." % (STAGER_BLOB, got))
    spec = importlib.util.spec_from_file_location("stage_t25R5", STAGER_T25R5)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("  ok   frozen stager is the registered blob %s" % STAGER_BLOB[:12])
    return mod


def stage(arm, level, mod, force=False):
    if level not in DONORS:
        refuse("%r is not a level this rung runs (L1 and L3 only)" % level)
    if arm not in ARMS:
        refuse("%r is not a registered arm of this rung" % arm)
    donor = os.path.join(T25R4, DONORS[level])
    case = os.path.join(HERE, "%s_%s" % (arm, level))
    src = os.path.join(T25R5, "arms", "fvSolution.coolant." + arm)

    if not os.path.isdir(donor):
        refuse("donor case absent: %s" % donor)
    if not os.path.isfile(src):
        refuse("no arm dictionary at %s" % src)

    if os.path.isdir(case):
        if not force:
            refuse("%s already exists. Refusing to overwrite a staged case; pass "
                   "--force only when you know nothing has run in it." % case)
        for t in os.listdir(case):
            if t == "0" or re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) or t.startswith("processor"):
                refuse("%s holds %r -- a run has happened here. A staged case is "
                       "NEVER rebuilt over compute output." % (case, t))
        shutil.rmtree(case)
    os.makedirs(case)

    for d in ("0.orig", "constant", "system"):
        s = os.path.join(donor, d)
        if not os.path.isdir(s):
            refuse("donor %s lacks %s" % (donor, d))
        shutil.copytree(s, os.path.join(case, d), symlinks=True)

    shutil.copyfile(src, os.path.join(case, "system", "coolant", "fvSolution"))

    # THE FROZEN GUARD, driven -- not a retyped copy of it.
    done = mod.edit_controldict(os.path.join(case, "system", "controlDict"))

    # ---- POST-CONDITIONS.  A stager that cannot prove its own output is not one.
    for bad in ("0", "processor0", "processor1"):
        if os.path.exists(os.path.join(case, bad)):
            refuse("%s: %s exists after staging. The age guard would be "
                   "unevaluable." % (case, bad))
    for t in os.listdir(case):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t):
            refuse("%s: time directory %r exists after staging." % (case, t))
    if open(os.path.join(case, "system", "coolant", "fvSolution")).read() != open(src).read():
        refuse("%s: the installed coolant fvSolution is not the arm dictionary." % case)

    # The registered window: 40 steps at dt 0.02, endTime 0.8, one write at the end.
    cd = open(os.path.join(case, "system", "controlDict")).read()
    for key, want in (("endTime", "0.8"), ("deltaT", "0.02"),
                      ("writeInterval", "40"), ("adjustTimeStep", "no")):
        if not re.search(r"^\s*%s\s+%s\s*;" % (key, re.escape(want)), cd, re.M):
            refuse("%s: controlDict does not carry the registered %s %s"
                   % (case, key, want))

    print("staged %-3s %s -> %s" % (arm, level, case))
    print("         donor %s; controlDict: %s" % (
        DONORS[level], ", ".join("%s %s->%s" % (k, o, n) for k, (o, n) in sorted(done.items()))))
    return 0


if __name__ == "__main__":
    force = "--force" in sys.argv
    mod = frozen_stager()
    if "--all" in sys.argv:
        for lv in LEVELS:
            for a in ARMS:
                stage(a, lv, mod, force)
        print("\nSTAGED %d cases: %s" % (len(CASES), ", ".join(CASES)))
        sys.exit(0)
    a = sys.argv[sys.argv.index("--arm") + 1]
    lv = sys.argv[sys.argv.index("--level") + 1]
    sys.exit(stage(a, lv, mod, force))
