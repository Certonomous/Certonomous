#!/usr/bin/env python3
"""SO-3 PATH CENSUS -- EVERY PATH, DIRECTORY AND ARTEFACT NAME THIS ITEM CITES,
CHECKED AGAINST THE DISK.

WHY THIS EXISTS AND WHY IT IS SEPARATE FROM THE PIN CENSUS
-----------------------------------------------------------
`so3_pin_census.py` proves that every md5 constant names bytes that agree with
it.  IT CANNOT SEE A PATH THAT IS SIMPLY WRONG, because a wrong path carries no
pin.  And this family's most expensive derivation failures have been exactly
that:

  * **SO-3aR's falsified citation.**  `so3ar_run_arm.sh:228` protects
    `CURRICULUM-SO3aRF-a1-naca0012-alpha-feasibility`.  THAT DIRECTORY DOES NOT
    EXIST.  A mechanical rename turned SO-3a's real root name into one that
    does not.
  * **SO-3aR2 INHERITED IT AND DEEPENED IT.**  Its rename produced
    `CURRICULUM-SO3aR2F-...` -- also absent -- and its own comment at
    `so3ar2_run_arm.sh:174-178` describes that entry, in terms, as one of "FOUR
    roots that DO exist, and hold real evidence".  Three of the four do.
  * The real root, on disk with real evidence in it, is
    `CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility`, and NEITHER ancestor
    protected it.

**A MECHANICAL RENAME MOVES TOKENS; IT CANNOT MAKE PROSE TRUE.**  A pin census
run over either ancestor would have come back GREEN.

THE THREE DISPOSITIONS, AND THE MIDDLE ONE IS THE POINT
---------------------------------------------------------
  MUST_EXIST     an input, an instrument or a run root this item reads.  Absent
                 -> RED.
  MUST_NOT_EXIST a RUN OUTPUT.  This item has not run, so its run root and every
                 artefact under it MUST be absent.  Present -> RED, because a
                 pre-existing artefact is what a cold-start guard exists to
                 refuse and what a comparator could grade as this run's.
  GHOST          a name deliberately kept in a protected-root list although it
                 is not on disk, because a free name can be taken tomorrow and
                 keeping it costs one string comparison.  A GHOST IS PRINTED AS
                 A GHOST.  It is never described as a root that exists, which is
                 the sentence both ancestors carried.

REFUSAL TOKENS -- exit 2 and a named token, so an unrelated crash cannot read as
an expected refusal:
    REFUSE_MUST_EXIST_ABSENT      a cited input/instrument/root is not on disk
    REFUSE_MUST_NOT_EXIST_PRESENT a run output already exists before any run
    REFUSE_UNCLASSIFIED_PATH      a path is cited and this census was not told
                                  which of the three it is
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = "/home/ubuntu/certonomous-runs"
TUT = "/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible"
BASE = os.path.join(RUNS, "CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation")

# ---------------------------------------------------------------------------
# THE REGISTERED CLASSIFICATION.  Each entry is (path, disposition, why).
# ---------------------------------------------------------------------------
MUST_EXIST = [
    # ---- this item's own instruments.  Every file the chain EXECUTES or
    # ---- IMPORTS (DAFOAM section 18.3), plus every selftest that drives one.
    (os.path.join(HERE, f), "instrument") for f in (
        "so3_chain_driver.sh", "so3_run_arm.sh", "so3_grade.py", "so3_runScript.py",
        "so3_xf.py", "so3_stall.py", "so3_age_guard.py", "so3_aggregate_memory.py",
        "so3_stop_marker.sh", "so3_decomposeParDict", "so3_pin_census.py",
        "so3_path_census.py", "so3_repin.sh", "so3_derive_from_so3ar2.sh",
        "so3_xf_selftest.py", "so3_run_arm_selftest.sh",
        "so3_chain_driver_selftest.sh", "so3_runScript_selftest.py",
        "so3_grade_selftest.py",
    )
] + [
    # ---- the shipped tutorial's own INPUT bytes, pinned by md5 in the driver.
    (os.path.join(TUT, p), "tutorial input") for p in (
        "runScript.py", "genAirFoilMesh.py", "preProcessing.sh",
        "profiles/NACA0012PS.profile", "profiles/NACA0012SS.profile",
        "FFD/wingFFD.xyz", "0.orig", "constant", "system",
    )
] + [
    # ---- the comparator's reference bytes: REAL logs from SO-1a's run root.
    (os.path.join(HERE, "reference", f), "real OpenFOAM reference bytes") for f in (
        "REAL_SO1a_MESH_checkMesh.log", "REAL_SO1a_X-S_arm.log",
    )
] + [
    # ---- THE UPSTREAM THIS ITEM'S EVERY CLAIM RESTS ON.  A record that cites a
    # ---- grade object must be able to point at it.
    (os.path.join(RUNS, "CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient",
                  "SO3aR2_grade_20260831T230221Z.json"),
     "SO-3aR2's grade object -- the item verdict GATE FAIL and the PATCHED PASS "
     "this item inherits"),
    (os.path.join(HERE, "..", "curriculum_SO3aR2", "PREREGISTRATION.md"),
     "SO-3aR2's frozen pre-registration"),
    (os.path.join(HERE, "..", "SO3_MULTIPOINT_SCOPE_MEMO.md"),
     "the scope memo that names SO-3 the optimisation rung"),
    # ---- THE COST ANCHORS, BY ARTEFACT.  DAFOAM section 18.1: a cost anchor
    # ---- names the program it prices.  Both are quoted in so3_grade.py's CAPS
    # ---- block and both must be readable.
    (os.path.join(RUNS, "CURRICULUM-D1-a1-constrained-opt", "armO", "opt_IPOPT.txt"),
     "C-24's anchor: 0.42127 core-min/major on THIS A1 case at np=1"),
    (os.path.join(RUNS, "CURRICULUM-D6-a2-wing-multipoint", "O_mp", "opt_IPOPT.txt"),
     "C-188's anchor: the 1.6308x multipoint correction and the stall this "
     "item's detector is calibrated on"),
    (os.path.join(RUNS, "A2-mach-wing", "opt_IPOPT.txt"),
     "section 9's own A2 incident: 47 majors, no EXIT line"),
    # ---- the feasibility root BOTH ancestors failed to protect.
    (os.path.join(RUNS, "CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility"),
     "the REAL feasibility run root; SO-3aR and SO-3aR2 each protected a "
     "renamed GHOST of it instead"),
]

MUST_NOT_EXIST = [
    (BASE, "this item's own run root.  IT HAS NOT RUN.  A pre-existing root is "
           "what the cold-start guard refuses and what a comparator could grade "
           "as this run's output"),
] + [
    (os.path.join(BASE, a), "a declared arm directory of a run that has not happened")
    for a in ("MESH", "O-S", "XE-S", "FE-S", "O-P", "XE-P", "FE-P")
] + [
    (os.path.join(BASE, f), "a run output of a run that has not happened")
    for f in ("ledger.txt", "STATUS.chain", "so3_driver.pid")
]

# NAMES KEPT IN A PROTECTED-ROOT LIST THAT ARE NOT ON DISK.  Kept deliberately:
# a name that is free today can be taken tomorrow, and keeping it costs one
# string comparison.  PRINTED AS GHOSTS AND NEVER AS ROOTS THAT EXIST.
GHOSTS_EXPECTED = {
    "CURRICULUM-SO3F-a1-naca0012-alpha-feasibility":
        "the token SO-3's own rename produced from SO-3aR2's ghost.  Kept as a "
        "reserved name; NAMED HERE AS A GHOST, which is the sentence both "
        "ancestors did not write",
    "CURRICULUM-SO1b-a1-naca0012-dragmin-opt":
        "SO-1b's original root; the real one is CURRICULUM-SO1bR-...",
    "CURRICULUM-SO1c-a1-naca0012-postopt":
        "an SO-1c name that was never taken; the real one is "
        "CURRICULUM-SO1c-a1-naca0012-dragmin-npinv",
    # ---- TWO MORE GHOSTS FOUND BY THIS CENSUS ON ITS FIRST DRIVE, INHERITED
    # ---- THROUGH THE SAME LIST AND NEVER CHECKED BY EITHER ANCESTOR.  Neither
    # ---- is protected wrongly -- keeping a free name is cheap and G-ROOT.1
    # ---- already refuses everything -- but neither was TRUE, and the ancestors'
    # ---- comments made no distinction between the names they listed.  MEASURED
    # ---- 2026-09-01 by `ls -d /home/ubuntu/certonomous-runs/CURRICULUM-D4*`
    # ---- and `...D14*`.
    "CURRICULUM-D4-SHIPPED-R-a2-wing-cdmin":
        "an assumed successor of CURRICULUM-D4-SHIPPED-... that was never "
        "created; the D4 roots on disk are D4-a2-wing-cdmin, "
        "D4-SHIPPED-a2-wing-cdmin, D4S-F3S-a2-wing-cdmin and D4S-F3SR-...",
    "CURRICULUM-D14-a2-wing-remesh":
        "D14's un-suffixed name; the only remesh root on disk is "
        "CURRICULUM-D14M-a2-wing-remesh, which IS protected beside it",
}


def refuse(token, detail):
    print("%s %s" % (token, detail))
    sys.exit(2)


def forbidden_roots():
    """The launcher's G-ROOT.2 list, read out of ITS OWN BYTES."""
    src = open(os.path.join(HERE, "so3_run_arm.sh"), errors="replace").read()
    m = re.search(r'^FORBIDDEN_ROOTS="(.*?)"$', src, re.S | re.M)
    if not m:
        refuse("REFUSE_UNCLASSIFIED_PATH", "no FORBIDDEN_ROOTS block in so3_run_arm.sh")
    return [x.strip() for x in m.group(1).splitlines() if x.strip()]


def main():
    print("SO-3 PATH CENSUS")
    fails = []

    print("\n[MUST_EXIST] every input, instrument, reference and cited artefact")
    for p, why in MUST_EXIST:
        rp = os.path.realpath(p)
        good = os.path.exists(rp)
        print("  %-6s %-78s %s" % ("OK" if good else "ABSENT",
                                   rp.replace(RUNS + "/", "runs/").replace(HERE + "/", "./"),
                                   why[:60]))
        if not good:
            fails.append("REFUSE_MUST_EXIST_ABSENT %s (%s)" % (rp, why))

    print("\n[MUST_NOT_EXIST] this item's OWN run outputs.  IT HAS NOT RUN.")
    n_absent = 0
    for p, why in MUST_NOT_EXIST:
        good = not os.path.exists(p)
        n_absent += 1 if good else 0
        if not good:
            print("  %-6s %s -- %s" % ("PRESENT", p, why))
            fails.append("REFUSE_MUST_NOT_EXIST_PRESENT %s (%s)" % (p, why))
    print("  %d of %d run outputs correctly ABSENT (the run root and all seven "
          "declared arm directories)" % (n_absent, len(MUST_NOT_EXIST)))

    print("\n[G-ROOT.2] the protected-root list, EVERY entry against the disk.")
    print("           A GHOST IS PRINTED AS A GHOST.  SO-3aR2's comment called")
    print("           one of its ghosts a root that DOES exist; that sentence is")
    print("           the thing this section makes unwritable.")
    live, ghosts = 0, []
    for r in forbidden_roots():
        if os.path.isdir(r):
            live += 1
        else:
            ghosts.append(r)
    for g in ghosts:
        base = os.path.basename(g)
        note = GHOSTS_EXPECTED.get(base)
        if note:
            print("  GHOST  %-62s REGISTERED: %s" % (base, note[:60]))
        else:
            print("  GHOST  %-62s *** UNREGISTERED GHOST ***" % base)
            fails.append("REFUSE_UNCLASSIFIED_PATH an unregistered ghost is in the "
                         "protected-root list: %s.  Either it exists and the list "
                         "is stale, or it is a reserved name and this census must "
                         "be told so." % g)
    print("  %d protected roots: %d LIVE, %d GHOST" % (live + len(ghosts), live, len(ghosts)))

    print("\n[NEGATIVE CONTROL] the census must be able to SEE a bad path.")
    probe = os.path.join(RUNS, "CURRICULUM-THIS-ROOT-DOES-NOT-EXIST")
    if os.path.exists(probe):
        fails.append("the negative-control probe path EXISTS; this control is void")
        print("  the probe path exists -- CONTROL VOID")
    else:
        print("  a deliberately absent path is correctly reported absent: %s"
              % os.path.basename(probe))
        # AND THE POSITIVE HALF: a path that DOES exist must read as existing, or
        # the check is a function that returns False.
        if os.path.exists(HERE):
            print("  and a path that DOES exist reads as existing: %s"
                  % os.path.basename(HERE))
        else:
            fails.append("the census cannot see its own directory")

    print("")
    if fails:
        for f in fails:
            print("  %s" % f)
        print("PATH CENSUS RED -- %d failure(s)" % len(fails))
        return 2
    print("PATH CENSUS GREEN -- %d cited paths exist, %d run outputs correctly "
          "absent, %d protected roots checked (%d live, %d registered ghosts), and "
          "the check was shown able to see both a present and an absent path."
          % (len(MUST_EXIST), len(MUST_NOT_EXIST), live + len(ghosts), live,
             len(ghosts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
