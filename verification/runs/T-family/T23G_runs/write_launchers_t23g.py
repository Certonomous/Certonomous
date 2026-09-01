#!/usr/bin/env python3
"""T23G -- write the three per-level detached launchers.  LAUNCHES NOTHING.

Ported in shape from T23_P305_U20/run_t23.sh, which landed that case clean, with
two additions and no subtractions:

  * A `START.<case>` RECORD IS WRITTEN BEFORE THE SOLVER LINE, carrying the box
    load at the moment of launch.  A contended core-min measured after the fact
    is indistinguishable from a mispredicted one, so the load is recorded when
    it can still mean something.
  * THE PER-LEVEL CAP FROM SECTION 8.2 IS ENACTED as the `timeout`, not merely
    written down: 1500 / 6000 / 24000 s at 1 rank = 25.0 / 100.0 / 400.0
    core-min.  CLAUDE.md rule 12 -- AN OVERRUN STOPS THE RUN.  A capped level is
    `capped=1`, fails rule 4's End-line clause, and its quantity is NOT A
    RESULT.  IT IS NOT RESTARTED WITH A BIGGER NUMBER.

THE setsid TRAP, which is why rc is captured where it is: `setsid timeout cmd`
EXITS 0 FOR EVERY OUTCOME.  rc is therefore captured INSIDE this wrapper on the
line IMMEDIATELY after the solver call, and the setsid that detaches the script
is never the thing whose status is read.  Otherwise rule 4 clause 1 is unevidenced.

`endTime` IS A LEVEL INVARIANT AND IS NOT TOUCHED HERE.  It is 10000 at every
level, byte-compared across the three system/controlDict files by the comparator.
Nothing in this file may tune it, and nothing here may rescue a level that fails
to converge -- no extra iterations, no relaxed residual, no scheme change.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# section 8.2: cap seconds at 1 rank -> core-min
CAPS = {"T23G_C": 1500, "T23G_M": 6000, "T23G_F": 24000}
POINT = {"T23G_C": 7.56, "T23G_M": 30.22, "T23G_F": 120.88}

TMPL = r"""#!/bin/bash
# T23G level %(name)s -- DETACHED LAUNCHER.  Serial, 1 rank.
# CAP (CLAUDE.md rule 12, T23G section 8.2): the timeout IS the cap.  An overrun
# STOPS the run; it does not get a new budget.
set -u

CASE="%(case)s"
NAME="%(name)s"
RANKS=1
TIMEOUT_S=%(timeout)d           # cap %(cap).1f core-min at 1 rank
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
SOLVER="chtMultiRegionSimpleFoam"

[ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
set +u
# shellcheck disable=SC1090
. "$FOAM_BASHRC" >/dev/null 2>&1 || true
set -u
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' is NOT RESOLVABLE after sourcing ${FOAM_BASHRC}." >&2; exit 2; }

cd "$CASE" || exit 2

# Rule 4 age guard: refuse a case that already carries a 0/ or a time directory.
if [ -e "$CASE/0" ]; then
    echo "REFUSE: $CASE/0 already exists -- the age guard cannot date this run" >&2
    exit 2
fi
for d in "$CASE"/[1-9]*; do
    [ -e "$d" ] && { echo "REFUSE: time directory $d already exists" >&2; exit 2; }
done

cp -r 0.orig 0 || exit 2
# 0/housing/T IS TOUCHED LAST, so it dates the run allowed to produce the answer.
# Every field at endTime must be NEWER than this file (mark_done_t23.py:14-22).
touch 0/housing/T

# THE START RECORD, WRITTEN BEFORE THE SOLVER LINE.  The load is recorded when it
# can still mean something; measured after the fact it proves nothing.
{
    echo "case=$NAME"
    echo "start_utc=$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)"
    echo "ranks=$RANKS"
    echo "timeout_s=$TIMEOUT_S"
    echo "cap_core_min=%(cap).1f"
    echo "point_core_min=%(point).2f"
    echo "endTime=10000   # LEVEL INVARIANT, identical at all three levels"
    echo "nproc=$(nproc)"
    echo "loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
    echo "solver=$SOLVER"
    echo "solver_path=$SOLVER_PATH"
    echo "prereg=docs/campaigns/T-family/T23G_PREREGISTRATION.md v1.1"
    echo "note=box load recorded BEFORE the solver line, not after"
} > "START.$NAME"

T0=$(date +%%s)
timeout "${TIMEOUT_S}s" "$SOLVER" > log.solve 2>&1
rc=$?                                    # <-- IMMEDIATELY after the solver line
T1=$(date +%%s)

WALL=$((T1 - T0))
CORE_MIN=$(python3 -c "print('%%.4f' %% ($WALL * $RANKS / 60.0))")
CAP_CORE_MIN=$(python3 -c "print('%%.4f' %% ($TIMEOUT_S * $RANKS / 60.0))")
if [ "$rc" -eq 124 ]; then CAPPED=1; else CAPPED=0; fi

{
    echo "case=$NAME"
    echo "rc=$rc"
    echo "wall_s=$WALL"
    echo "ranks=$RANKS"
    echo "core_min=$CORE_MIN"
    echo "cap_core_min=$CAP_CORE_MIN"
    echo "point_core_min=%(point).2f"
    echo "timeout_s=$TIMEOUT_S"
    echo "capped=$CAPPED"
    echo "solver=$SOLVER"
    echo "end_utc=$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)"
    echo "note=rc captured inside this wrapper on the line after the solver call, never around a setsid"
    echo "note=a capped level is NOT restarted with a bigger number (rule 12)"
} > "STATUS.$NAME"

# y+ per level, section 7.4: MEASURED and REPORTED, NEVER GATED.  Only after a
# clean solve -- a y+ read off a capped or crashed run would be meaningless.
if [ "$rc" -eq 0 ]; then
    postProcess -func yPlus -region fluid -latestTime > log.yPlus.fluid 2>&1 || true
fi

exit "$rc"
"""


def main():
    for name, timeout in CAPS.items():
        case = os.path.join(HERE, name)
        if not os.path.isdir(case):
            raise SystemExit("REFUSE: %s does not exist" % case)
        if os.path.exists(os.path.join(case, "0")):
            raise SystemExit("REFUSE: %s/0 exists; the age guard cannot date "
                             "this run" % case)
        p = os.path.join(case, "run_t23g.sh")
        open(p, "w").write(TMPL % dict(case=case, name=name, timeout=timeout,
                                       cap=timeout / 60.0, point=POINT[name]))
        os.chmod(p, 0o755)
        print("%s  launcher written  timeout %ds = %.1f core-min cap  "
              "(POINT %.2f)" % (name, timeout, timeout / 60.0, POINT[name]))
    print("\nTHREE LAUNCHERS WRITTEN.  NOTHING HAS BEEN LAUNCHED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
