#!/usr/bin/env python3
"""T3d builder — the R_ff CONTINUATION case `R_fx`, seeded from R_ff's converged-
so-far state at iteration 118 000.

WHY A NEW CASE DIRECTORY AND NOT A RESTART IN PLACE.  `R_ff` holds `0/` and two
numeric time directories, so BOTH the queue validator's AGE-GUARD
(`scripts/queue_entry_check.py:326`) and the launcher's own G3 guard
(`launch_t3_rff.sh:48-50`) refuse it -- correctly, under standing rule 4: a run
is never launched into a tree that already holds an answer.  **The lab's queue
substrate therefore has no route for an in-place continuation**, which is a
finding reported to the supervisor and not worked around here.  The clean route
is a FRESH case whose `0.orig/` IS R_ff's final state, so the age guard is
satisfied honestly rather than bypassed.

WHAT IS COPIED, AND WHAT IS DELIBERATELY NOT.
  constant/    the IDENTICAL mesh (602 128 cells).  The continuation is not a
               mesh study; changing the mesh would make it a different level.
  system/      copied, with endTime rewritten.  The iteration counter RESTARTS
               at 0 because `startFrom latestTime` will find only `0/`; endTime
               is therefore the number of ADDITIONAL iterations, not a total.
  0.orig/      T U p_rgh p alphat nut k omega phi from R_ff/118000/ -- the seven
               fields the strict completion rule names, plus p and phi.
  NOT copied:  C, Cx, Cy, Cz (cell-centre fields written by a function object,
               not solution state) and 118000/uniform (time bookkeeping that
               would contradict a restart at 0).

THIS SCRIPT WRITES ONLY INTO ITS OWN TARGET AND REFUSES IF THE TARGET EXISTS.
It never writes into R_ff.  Exit 0 built, 2 refusal.
"""
import os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "R_ff")
SRC_TIME = "118000"
DST = os.path.join(HERE, "R_fx")
ADDITIONAL_ITERATIONS = 24000          # registered; T3d_PREREGISTRATION.md §4
WRITE_INTERVAL = 2000                  # unchanged from R_ff
SEED_FIELDS = ("T", "U", "p_rgh", "p", "alphat", "nut", "k", "omega", "phi")


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(2)


def main():
    if os.path.exists(DST):
        refuse("%s already exists -- this builder never overwrites a case" % DST)
    if not os.path.isdir(os.path.join(SRC, SRC_TIME)):
        refuse("source state %s/%s absent" % (SRC, SRC_TIME))
    for f in SEED_FIELDS:
        if not os.path.isfile(os.path.join(SRC, SRC_TIME, f)):
            refuse("source field %s missing at %s/%s" % (f, SRC, SRC_TIME))

    os.makedirs(DST)
    print("mesh + constant ...")
    shutil.copytree(os.path.join(SRC, "constant"), os.path.join(DST, "constant"))
    print("system ...")
    shutil.copytree(os.path.join(SRC, "system"), os.path.join(DST, "system"))

    # rewrite endTime; leave every other entry byte-identical
    cd = os.path.join(DST, "system", "controlDict")
    lines = open(cd).read().split("\n")
    hits = 0
    for i, ln in enumerate(lines):
        if ln.strip().startswith("endTime") and ln.strip().endswith(";") \
                and "stopAt" not in ln:
            lines[i] = "endTime         %d;" % ADDITIONAL_ITERATIONS
            hits += 1
    if hits != 1:
        refuse("expected exactly one endTime line in controlDict, found %d" % hits)
    open(cd, "w").write("\n".join(lines))
    print("controlDict endTime -> %d (ADDITIONAL iterations; counter restarts at 0)"
          % ADDITIONAL_ITERATIONS)

    print("0.orig from %s/%s ..." % (os.path.basename(SRC), SRC_TIME))
    os.makedirs(os.path.join(DST, "0.orig"))
    for f in SEED_FIELDS:
        shutil.copy(os.path.join(SRC, SRC_TIME, f), os.path.join(DST, "0.orig", f))
        print("   %s" % f)

    # the age guard must be satisfiable: no 0/ and no numeric time directory
    bad = [d for d in os.listdir(DST)
           if d == "0" or (d.replace(".", "", 1).isdigit() and os.path.isdir(
               os.path.join(DST, d)))]
    if bad:
        refuse("age guard would refuse: %s present in the built case" % bad)

    open(os.path.join(DST, "CASE.txt"), "w").write(
        "R_fx -- T3d continuation of R_ff\n"
        "seeded from %s/%s by build_t3d.py\n"
        "mesh IDENTICAL to R_ff (not a new level)\n"
        "endTime %d = ADDITIONAL iterations; the counter restarts at 0\n"
        "writeInterval %d, purgeWrite unchanged from R_ff\n"
        "registration: docs/campaigns/T-family/T3d_PREREGISTRATION.md\n"
        % (os.path.basename(SRC), SRC_TIME, ADDITIONAL_ITERATIONS, WRITE_INTERVAL))
    print("\nbuilt %s" % DST)
    print("age guard: no 0/ and no numeric time directory -- launchable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
