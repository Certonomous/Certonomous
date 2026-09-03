#!/usr/bin/env python3
"""T25R6c-R2 STAGER -- build the ONE case this rung runs.

Registration: docs/campaigns/T-family/T25R6cR2_PREREGISTRATION.md section 4
("Case provenance").

WHAT IT BUILDS
--------------
    verification/runs/T-family/T25R6cR2_LEGAB_runs/W1150_C4_L1/

from the donor `verification/runs/T-family/T25R5_LINSOLVER_runs/C4_L1` -- the
SAME donor T25R6c used, so R2 and R6c differ in leg-B length and nothing else.
`0.orig/`, `constant/` and `system/` copied; `system/controlDict` is C4_L1's
LEG A **UNCHANGED** (startTime, endTime 0.8, deltaT 0.02, 40 steps -- the window
every C4/C5 wall factor was measured on); `system/controlDict.legB` is rewritten
to `startFrom latestTime`, `deltaT 0.1`, `endTime 111.8`, and --

THE ONE THING THAT CHANGED FROM T25R6c, AND WHY
-----------------------------------------------
    writeControl runTime;   writeInterval 111;      (was: timeStep / 400)

T25R6c wrote NO field directory at its registered endTime and graded NOT A
RESULT on rule 4 for exactly that.  `writeControl timeStep` tests

    writeTime_ = !(timeIndex_ % label(writeInterval_))        Time.C:1114

and `timeIndex_` is the GLOBAL time index, which does NOT reset across a
`startFrom latestTime` restart.  Leg A had already advanced it to 40, so
`writeInterval 400` fired at global index 400 = LEG-B STEP 360, t = 36.8, and
nothing wrote at the registered 40.8.  The run directory carries 36.8/ and no
40.8/.

`writeControl runTime` computes                          Time.C:1117-1131
    writeIndex = label(((value() - startTime_) + 0.5*deltaT_) / writeInterval_)
    write iff writeIndex > writeTimeIndex_               (writeTimeIndex_ = 0,
                                                         TimeState.C:38)
and `startFrom latestTime` sets `startTime_` to the restart time (Time.C:180-183).
The index is therefore RELATIVE TO THE RESTART and is INDEPENDENT OF LEG A'S
STEP COUNT ENTIRELY.  With startTime_ = 0.8 and writeInterval 111, the index
first exceeds 0 at t = 111.8 and at no earlier step: ONE write, AT endTime.
The `+ 0.5*deltaT_` term also makes it robust to accumulated float drift in
`value()`, which `timeStep` has no equivalent of.

THE ALTERNATIVE WAS REJECTED, NOT OVERLOOKED.  Keeping `timeStep` and setting
`writeInterval` to N_A + N_B = 1150 would also write once, at leg-B step 1110 --
but ONLY by arithmetic coincidence with leg A's step count, which is the exact
quantity that caused the defect.  Change leg A's length and the write moves
again, silently.  A fix that still depends on what broke it is not a fix.

VERIFIED, NOT ASSUMED: derive_t25R6cR2.py steps the transcribed Time.C branch
over the full 1110-step schedule and its selftest requires that (i) runTime
writes exactly once at endTime, (ii) the timeStep setting T25R6c used reproduces
the OBSERVED failure -- a write at leg-B step 360 and none at 40.8, and (iii) a
mutated interval writes more than once.  The run itself is the final check:
P-R2-6 predicts exactly one field directory at t = 111.8 and rule 4 measures it.

IT DOES NOT CREATE `0/` AND IT DOES NOT RUN decomposePar.
`run_one_t25R6cR2.sh` does both, and REFUSES a case where `0/` or any numeric
time directory already exists.  `0/module/T` is touched LAST at launch and so
DATES the run allowed to produce the answer (rule 4's age guard).  A stager that
pre-created `0/` would make the age guard UNEVALUABLE, and it would never say so.

THE REGION IS `module`.  This family is chtMultiRegionFoam and the dating file
is `0/module/T`, NOT `0/T`.  A successor that gets this wrong produces a rule-4
defect that is SILENT.

    python3 stage_t25R6cR2.py
    python3 stage_t25R6cR2.py --force     # only when NOTHING has run in the case
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TFAM = os.path.dirname(HERE)
DONOR = os.path.join(TFAM, "T25R5_LINSOLVER_runs", "C4_L1")
ARM_DICT = os.path.join(TFAM, "T25R5_LINSOLVER_runs", "arms", "fvSolution.coolant.C4")
CASE = "W1150_C4_L1"

EXIT_REFUSE = 2

# --- FROZEN AT THE REGISTRATION.  Leg A is the donor's, untouched; leg B is the
# --- only thing this stager writes.
LEGA_EXPECT = {"startFrom": "startTime", "endTime": "0.8", "deltaT": "0.02",
               "adjustTimeStep": "no", "writeInterval": "40"}
LEGB_SET = {"startFrom": "latestTime", "endTime": "111.8", "deltaT": "0.1",
            "adjustTimeStep": "no", "writeControl": "runTime",
            "writeInterval": "111"}


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def top_level_key(text, key):
    """Value of a TOP-LEVEL controlDict key -- one that starts at column 0.

    Anchoring at column 0 is load-bearing: `writeControl` and `writeInterval`
    also appear INDENTED inside functionObjects, and a pattern that matched
    those would edit a function object and leave the run's own write control
    untouched, silently.  That is the same class of defect as the one this rung
    exists to repair, so it is guarded rather than trusted."""
    return re.findall(r"^%s\s+([^;]+);" % re.escape(key), text, re.M)


def set_top_level_key(text, key, value):
    hits = top_level_key(text, key)
    if len(hits) == 0:
        refuse("controlDict has no TOP-LEVEL key %r to set" % key)
    if len(hits) > 1:
        refuse("controlDict has %d top-level %r keys; refusing to guess which one "
               "governs" % (len(hits), key))
    new, n = re.subn(r"^(%s\s+)([^;]+);" % re.escape(key),
                     lambda m: m.group(1) + value + ";", text, count=1, flags=re.M)
    if n != 1:
        refuse("failed to rewrite top-level key %r" % key)
    return new


def main(argv):
    force = "--force" in argv
    case = os.path.join(HERE, CASE)

    if not os.path.isdir(DONOR):
        refuse("donor case absent: %s" % DONOR)
    if not os.path.isfile(ARM_DICT):
        refuse("the C4 arm dictionary is absent: %s" % ARM_DICT)

    if os.path.isdir(case):
        if not force:
            refuse("%s already exists.  Refusing to overwrite a staged case; pass "
                   "--force only when you know nothing has run in it." % case)
        for t in os.listdir(case):
            if t == "0" or re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) \
                    or t.startswith("processor"):
                refuse("%s holds %r -- A RUN HAS HAPPENED HERE.  A staged case is "
                       "NEVER rebuilt over compute output." % (case, t))
        shutil.rmtree(case)
    os.makedirs(case)

    for d in ("0.orig", "constant", "system"):
        s = os.path.join(DONOR, d)
        if not os.path.isdir(s):
            refuse("donor %s lacks %s" % (DONOR, d))
        shutil.copytree(s, os.path.join(case, d), symlinks=True)

    # ---- LEG A: the donor's, VERIFIED UNCHANGED, never rewritten ----------
    cdp = os.path.join(case, "system", "controlDict")
    cd = open(cdp).read()
    for k, want in sorted(LEGA_EXPECT.items()):
        hits = top_level_key(cd, k)
        if len(hits) != 1 or hits[0].strip() != want:
            refuse("leg A controlDict: top-level %s is %r, registered %r.  Leg A "
                   "is the donor's window UNCHANGED and this stager does not edit "
                   "it." % (k, hits, want))
    print("  ok   leg A controlDict is the donor's, unchanged: " +
          ", ".join("%s %s" % (k, v) for k, v in sorted(LEGA_EXPECT.items())))

    # ---- LEG B: the only thing written here -------------------------------
    lbp = os.path.join(case, "system", "controlDict.legB")
    if not os.path.isfile(lbp):
        refuse("donor carries no system/controlDict.legB to base leg B on")
    lb = open(lbp).read()
    for k, v in sorted(LEGB_SET.items()):
        lb = set_top_level_key(lb, k, v)
    open(lbp, "w").write(lb)
    got = open(lbp).read()
    for k, want in sorted(LEGB_SET.items()):
        hits = top_level_key(got, k)
        if len(hits) != 1 or hits[0].strip() != want:
            refuse("leg B controlDict: %s did not take (%r != %r)" % (k, hits, want))
    print("  ok   leg B controlDict written and READ BACK FROM DISK: " +
          ", ".join("%s %s" % (k, v) for k, v in sorted(LEGB_SET.items())))
    # THE DEFECT GUARD.  The T25R6c write control must not survive anywhere at
    # top level in the file that governs leg B.
    if top_level_key(got, "writeControl") != ["runTime"]:
        refuse("leg B controlDict still carries a non-runTime top-level "
               "writeControl -- THE T25R6c DEFECT WOULD REPEAT.")
    print("  ok   the T25R6c `writeControl timeStep` is GONE from leg B, checked "
          "on the bytes on disk and not on the bytes written")

    # ---- the arm dictionary must be C4's, checked, not assumed ------------
    got_arm = open(os.path.join(case, "system", "coolant", "fvSolution")).read()
    if got_arm != open(ARM_DICT).read():
        refuse("%s: the coolant fvSolution is NOT the registered C4 arm "
               "dictionary.  rho is a ratio inside ONE run, but the run must "
               "still be the registered arm." % case)
    print("  ok   coolant fvSolution IS the registered C4 arm dictionary")

    # ---- POST-CONDITIONS.  A stager that cannot prove its own output is not one.
    for bad in ("0", "processor0", "processor1"):
        if os.path.exists(os.path.join(case, bad)):
            refuse("%s: %s exists after staging.  THE AGE GUARD WOULD BE "
                   "UNEVALUABLE." % (case, bad))
    for t in os.listdir(case):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t):
            refuse("%s: time directory %r exists after staging." % (case, t))
    if not os.path.isfile(os.path.join(case, "0.orig", "module", "T")):
        refuse("%s: 0.orig/module/T absent -- the runner could not create the "
               "file that DATES the run, and rule 4's age guard would never "
               "evaluate." % case)
    print("  ok   no 0/, no time directory, no processor* -- the age guard is "
          "evaluable and 0.orig/module/T exists to be copied from")

    print("\nSTAGED %s" % case)
    print("  donor  %s" % DONOR)
    print("  leg A    40 steps, deltaT 0.02, t 0 -> 0.8       (log.solve.legA)")
    print("  leg B  1110 steps, deltaT 0.1,  t 0.8 -> 111.8   (log.solve.legB)")
    print("         first 40 leg-B steps DISCARDED as the restart transient;")
    print("         graded on steps 41..1110 as two halves of 535")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
