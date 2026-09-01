#!/usr/bin/env python3
"""T23G -- MESH THE THREE LEVELS.  LAUNCHES NO SOLVER.

This is the FIRST COMPUTE under T23G_PREREGISTRATION.md, and section 8.5 costs
it: POINT 1.0 core-min, CAP 5.0 core-min for blockMesh + splitMeshRegions +
checkMesh x 3 regions x 3 levels.  VERIFICATION_CHARTER section 2d.2 closes the
gates here, which is why the v1.1 amendment was landed BEFORE this ran.

  * THE CAP IS ENACTED, NOT MERELY WRITTEN.  A per-level and a total wall budget
    are enforced by subprocess timeout.  An overrun STOPS the build; CLAUDE.md
    rule 12 gives it no new budget.
  * build_t23.py drives blockMesh and splitMeshRegions and carries its own hard
    refusal on solver names.  IT IS NOT MODIFIED HERE and no solver is invoked.
  * THE PHASE-B `0/` TRAP.  splitMeshRegions -overwrite deposits cellToRegion
    into `0/`.  run_t23.sh:47 REFUSES to launch into a case that already has a
    `0/`, because rule 4's age guard could not then date the run.  The source
    case renamed it, and this script renames it identically, BEFORE any launch.
  * checkMesh is run per region because build_t23.py does not run it, and the
    comparator MEASURES every level's cell count from these logs rather than
    reciting the registration.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = ("T23G_C", "T23G_M", "T23G_F")
FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
ARTEFACT = "0_BUILD_ARTEFACT_cellToRegion_from_splitMeshRegions"

BUILD_CAP_CORE_MIN = 5.0                    # section 8.5, HARD
TOTAL_CAP_S = int(BUILD_CAP_CORE_MIN * 60)  # 300 s at 1 rank
PER_LEVEL_CAP_S = 200


def sh(cmd, cwd, log, timeout):
    """One OpenFOAM MESHING/INSPECTION utility.  Never a solver."""
    for banned in ("chtMultiRegionSimpleFoam", "chtMultiRegionFoam",
                   "simpleFoam", "solidFoam"):
        if banned in cmd:
            raise SystemExit("REFUSE: this script never launches a solver (%s)"
                             % banned)
    full = ". %s >/dev/null 2>&1; cd %s && %s" % (FOAM, cwd, cmd)
    t0 = time.time()
    try:
        r = subprocess.run(["bash", "-c", full], capture_output=True,
                           text=True, timeout=timeout)
        rc = r.returncode
        out = r.stdout
    except subprocess.TimeoutExpired:
        rc, out = 124, "TIMEOUT after %ds -- CAP ENACTED, build STOPPED" % timeout
    dt = time.time() - t0
    if log:
        open(os.path.join(cwd, log), "a").write(out or "")
    return rc, dt


def main():
    t_all = time.time()
    per = {}
    for lvl in LEVELS:
        d = os.path.join(HERE, lvl)
        if not os.path.isdir(d):
            raise SystemExit("REFUSE: %s does not exist -- run "
                             "build_ladder_t23g.py first" % d)
        if os.path.exists(os.path.join(d, "constant", "polyMesh")):
            raise SystemExit("REFUSE: %s already carries a mesh" % d)
        spent = time.time() - t_all
        budget = min(PER_LEVEL_CAP_S, TOTAL_CAP_S - spent)
        if budget <= 0:
            raise SystemExit("REFUSE: build cap %.1f core-min reached before "
                             "%s -- an overrun STOPS the build (rule 12)"
                             % (BUILD_CAP_CORE_MIN, lvl))

        t0 = time.time()
        rc, dt = sh("python3 build_t23.py all", d, "build.out", budget)
        if rc != 0:
            raise SystemExit("REFUSE: %s build_t23.py rc=%d after %.1fs"
                             % (lvl, rc, dt))

        # THE PHASE-B `0/` TRAP -- rename before any launch can see it.
        z = os.path.join(d, "0")
        if os.path.isdir(z):
            os.rename(z, os.path.join(d, ARTEFACT))
        if os.path.exists(os.path.join(d, "0")):
            raise SystemExit("REFUSE: %s/0 still exists; run_t23.sh:47 would "
                             "refuse and rule 4's age guard could not date the "
                             "run" % d)

        for region in ("fluid", "housing", "core"):
            spent = time.time() - t_all
            b = min(PER_LEVEL_CAP_S, TOTAL_CAP_S - spent)
            if b <= 0:
                raise SystemExit("REFUSE: build cap reached during checkMesh")
            rc, _ = sh("checkMesh -region %s > log.checkMesh.%s 2>&1"
                       % (region, region), d, None, b)
            p = os.path.join(d, "log.checkMesh.%s" % region)
            if not os.path.isfile(p):
                raise SystemExit("REFUSE: %s was not written" % p)

        wall = time.time() - t0
        per[lvl] = wall
        print("%s meshed  wall %.1f s  = %.4f core-min at 1 rank"
              % (lvl, wall, wall / 60.0))

    total = time.time() - t_all
    print("\nBUILD COMPUTE, MEASURED: %.1f wall s = %.4f core-min at 1 rank"
          % (total, total / 60.0))
    print("  section 8.5 POINT 1.0 core-min, CAP 5.0 core-min -> ratio "
          "actual/predicted = %.3f" % (total / 60.0 / 1.0))
    print("\nTHREE LEVELS MESHED.  NO SOLVER HAS BEEN LAUNCHED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
