#!/bin/bash
# T4 impinging jet -- run ONE registered level, capture the solver's rc, and
# write a STATUS file that a mark_done can evaluate WITHOUT INFERENCE.
#
# Usage: run_one_t4.sh <level: c|m|f> <cap_core_min> <ranks>
#
# WHY THIS FILE EXISTS IN THIS FORM.  K0d's L1 pair reached endTime and is
# NOT DONE forever, because the launcher that fired it started the solver and
# never captured its exit status (K0d_FORENSICS_2026-08-25.md:971-978).  The
# lab's shared detached launcher, scripts/launch_solve.sh, has the same defect
# by construction: `$?` appears 0 times in its 487 lines, `wait` appears 0
# times, and its collector is `while kill -0 "$PID"; do sleep 15; done`, which
# tests EXISTENCE and discards STATUS.  Its completion record carries 22 fields
# and not one of them is rc.  Nothing here routes through it.
#
# THE `capped` WITNESS, AND WHY rc ALONE IS NOT ENOUGH.  Measured on this box,
# GNU coreutils 9.4, 2026-08-26:
#     child exits 0                        -> 0
#     child exits 7                        -> 7      (crash, passed through)
#     child takes SIGFPE                   -> 136    (crash, passed through)
#     wall-clock expiry, default            -> 124
#     expiry with --kill-after, TERM ignored-> 137
#     CHILD GENUINELY EXITS 124             -> 124    <-- COLLIDES with expiry
# and 137 is ALSO what the OOM killer produces.  So `rc` alone cannot separate
# a cap-stop (rule 12: an overrun STOPS the run, NOT A RESULT) from a crash
# (a finding, needing triage) or from an OOM kill.  This launcher therefore
# records an INDEPENDENT expiry witness -- wall_s measured against the
# registered timeout_s -- and mark_done_t4.py decides from the witness, not
# from the rc value.  A solver that exits 124 on its own has wall_s < timeout_s.
#
# no `set -e` / `set -u` anywhere: the OpenFOAM v2606 etc/bashrc dereferences
# unset variables and exits a `set -u` shell silently, BEFORE the completion
# record is written.  Every step below is gated explicitly instead.
set -o pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LEVEL="$1"; CAP_CORE_MIN="$2"; RANKS="$3"

die() { echo "REFUSE: $*" >&2; exit 3; }

case "$LEVEL" in
    c|m|f) ;;
    *) die "G0: level must be one of c m f (the three registered levels); got '$LEVEL'";;
esac
[ -n "$CAP_CORE_MIN" ] || die "G0: cap_core_min is required -- an uncosted run is disqualified (CLAUDE.md rule 12)"
[ -n "$RANKS" ]        || die "G0: ranks is required"

CASE="T4_IJ_$LEVEL"
CDIR="$HERE/$CASE"

# The registered cap identity.  Written this way so a later parallel level
# cannot inherit a silent factor-of-ranks overrun.
TIMEOUT_S=$(( CAP_CORE_MIN * 60 / RANKS ))

[ -d "$CDIR" ] || die "G1: no case directory $CDIR -- run build_t4.py first"

# ---- G2  THE LAUNCH GUARD (CLAUDE.md rule 4, final clause) -----------------
# A guard refuses a case where 0 or a numeric time directory already exists,
# because such a case cannot be dated by its own 0/T and its age guard is
# therefore unevaluable.  This fires BEFORE anything is written.
[ -e "$CDIR/0" ] && die "G2: $CASE already has a 0/ directory; refusing (the age guard could not be evaluated)"
for d in "$CDIR"/[0-9]*; do
    [ -d "$d" ] && die "G2: $CASE already has time directory $(basename "$d"); refusing"
done
[ -d "$CDIR/0.orig" ] || die "G2: $CASE has no 0.orig to arm from"

# ---- G3  no other process may already be running in this case dir ----------
# Applied BEFORE any cd, so this process never matches its own cwd.
for p in /proc/[0-9]*; do
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ] && \
        die "G3: pid ${p#/proc/} ($(readlink "$p/exe" 2>/dev/null)) is already running in $CASE"
done

# ---- arm 0/ from 0.orig, with 0/T touched LAST ----------------------------
# 0/T is touched last so that it DATES THE RUN: the age guard requires every
# field at endTime to be NEWER than the case's own 0/T.  The sleep 1 makes the
# ordering visible at 1 s filesystem timestamp granularity.
cp -r "$CDIR/0.orig" "$CDIR/0" || die "could not create 0/ from 0.orig"
for f in U p_rgh T alphat nut k omega; do
    [ -f "$CDIR/0/$f" ] || die "0/$f missing after arming -- the registered field set is incomplete"
done
sleep 1
touch "$CDIR/0/T" || die "could not touch 0/T (the age-guard reference)"

# ---- solve -----------------------------------------------------------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>&1 || die "no OpenFOAM environment"

checkMesh -case "$CDIR" > "$CDIR/log.checkMesh" 2>&1
CHECKMESH_RC=$?

START=$(date -u +%s)
if [ "$RANKS" -gt 1 ]; then
    decomposePar -case "$CDIR" > "$CDIR/log.decomposePar" 2>&1
    timeout --signal=TERM --kill-after=60 "$TIMEOUT_S" \
        mpirun -np "$RANKS" buoyantBoussinesqSimpleFoam -case "$CDIR" -parallel \
        > "$CDIR/log.solve" 2>&1
    RC=$?
    reconstructPar -case "$CDIR" -latestTime > "$CDIR/log.reconstructPar" 2>&1
else
    timeout --signal=TERM --kill-after=60 "$TIMEOUT_S" \
        buoyantBoussinesqSimpleFoam -case "$CDIR" > "$CDIR/log.solve" 2>&1
    RC=$?
fi
END=$(date -u +%s)

WALL_S=$(( END - START ))
CORE_MIN=$(awk -v w="$WALL_S" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')

# THE INDEPENDENT EXPIRY WITNESS.  Derived from measured wall time against the
# registered timeout, NOT from the rc value, because 124 and 137 are both
# ambiguous (see the header).  This is the field mark_done_t4.py reads to tell
# a cap-stop from a crash.
if [ "$WALL_S" -ge "$TIMEOUT_S" ]; then CAPPED=yes; else CAPPED=no; fi

{
  echo "case=$CASE"
  echo "level=$LEVEL"
  echo "rc=$RC"
  echo "wall_s=$WALL_S"
  echo "ranks=$RANKS"
  echo "core_min=$CORE_MIN"
  echo "cap_core_min=$CAP_CORE_MIN"
  echo "timeout_s=$TIMEOUT_S"
  echo "capped=$CAPPED"
  echo "checkmesh_rc=$CHECKMESH_RC"
  echo "started_utc=$(date -u -d "@$START" +%Y-%m-%dT%H:%M:%SZ)"
  echo "ended_utc=$(date -u -d "@$END" +%Y-%m-%dT%H:%M:%SZ)"
} > "$HERE/STATUS.$CASE"

echo "$CASE rc=$RC wall=${WALL_S}s core_min=$CORE_MIN cap=$CAP_CORE_MIN capped=$CAPPED"

# EXIT WITH THE SOLVER'S OWN rc, NEVER 0.
# run_one_t8.sh ends `exit 0`, so a queue driver chaining on `&&` marches
# straight past a SIGFPE that killed the solve.  The STATUS file records the
# truth either way, but a launcher that reports success to its own caller has
# put the defect back one level up.
exit "$RC"
