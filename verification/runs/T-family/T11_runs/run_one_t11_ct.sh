#!/bin/bash
# T11 CONTROL C-T -- run the temporal-bias control case T11_PW_f_CT (deltaT halved at level f),
# capture the SOLVER's rc, write STATUS.T11_PW_f_CT. NEW FILE (AMENDMENT 2): the frozen
# run_one_t11.sh accepts only c|m|f and rule 2 forbids editing it after first compute.
# Modelled line-for-line on run_one_t11.sh (blob 249eb813); the only departures are
# the level literal, the self-detach block below, and the case name.
# Usage: run_one_t11_ct.sh <cap_core_min> <ranks>      (level is fixed: f_CT)
#
# rc comes from the solver itself, never from a setsid or nohup wrapper that
# returns 0 for a crashed child. STATUS carries `capped`, an INDEPENDENT expiry
# witness derived from measured wall_s against the registered timeout_s, because
# rc alone cannot separate a cap-stop from a crash: measured on this box (GNU
# coreutils 9.4) a child that genuinely exits 124 is indistinguishable from a
# wall-clock expiry, and 137 is both a --kill-after expiry AND the OOM killer.
#
# no `set -e` / `set -u`: the OpenFOAM etc/bashrc dereferences unset variables.
set -o pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LEVEL="f_CT"; CAP_CORE_MIN="$1"; RANKS="$2"
die() { echo "REFUSE: $*" >&2; exit 3; }
# level is not an argument: this wrapper runs exactly one case, T11_PW_f_CT
[ -n "$CAP_CORE_MIN" ] || die "G0: cap_core_min is required (CLAUDE.md rule 12)"
[ -n "$RANKS" ]        || die "G0: ranks is required"
CASE="T11_PW_$LEVEL"; CDIR="$HERE/$CASE"
TIMEOUT_S=$(( CAP_CORE_MIN * 60 / RANKS ))
[ -d "$CDIR" ] || die "G1: no case directory $CDIR -- built by hand from T11_PW_f (AMENDMENT 2)"
# Detach ONCE by re-executing this same file under setsid (scripts/launch_k0f.sh
# pattern). The caller's rc is meaningless and is never trusted; inside the
# detached copy the solver runs under `timeout` in the FOREGROUND with no setsid
# between them, so $? is the solver's own status.
if [ "${T11CT_DETACHED:-}" != "1" ]; then
    T11CT_DETACHED=1 exec setsid "$0" "$CAP_CORE_MIN" "$RANKS" </dev/null >> "$HERE/launch.f_CT.log" 2>&1 &
    echo "launched $CASE detached; STATUS.$CASE will appear in $HERE"
    exit 0
fi

# G2 -- launch guard (rule 4). Time directories are matched by a REGEX with
# fullmatch semantics, NEVER a shell glob: `[0-9]*` matches `0.orig` too, and
# that collision made T4's launcher unable to pass its own guard (L-341's
# sibling; scripts/check_launcher_can_launch.py ARM 1).
[ -e "$CDIR/0" ] && die "G2: $CASE already has a 0/ directory; refusing (the age guard could not be evaluated)"
while IFS= read -r d; do
    [ -n "$d" ] && die "G2: $CASE already has time directory $(basename "$d"); refusing"
done < <(find "$CDIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended \
              -regex '.*/[0-9]+(\.[0-9]+)?' 2>/dev/null)
[ -d "$CDIR/0.orig" ] || die "G2: $CASE has no 0.orig to arm from"
for p in /proc/[0-9]*; do
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ] && \
        die "G3: pid ${p#/proc/} is already running in $CASE"
done

cp -r "$CDIR/0.orig" "$CDIR/0" || die "could not create 0/ from 0.orig"
[ -f "$CDIR/0/T" ] || die "0/T missing after arming"
sleep 1
touch "$CDIR/0/T" || die "could not touch 0/T (the age-guard reference)"

source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>&1 || die "no OpenFOAM environment"
blockMesh -case "$CDIR" > "$CDIR/log.blockMesh" 2>&1
BM_RC=$?
[ "$BM_RC" -eq 0 ] || die "blockMesh failed rc=$BM_RC"
checkMesh -case "$CDIR" > "$CDIR/log.checkMesh" 2>&1
CHECKMESH_RC=$?

START=$(date -u +%s)
timeout --signal=TERM --kill-after=60 "$TIMEOUT_S" \
    laplacianFoam -case "$CDIR" > "$CDIR/log.solve" 2>&1
RC=$?
END=$(date -u +%s)
WALL_S=$(( END - START ))
CORE_MIN=$(awk -v w="$WALL_S" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')
if [ "$WALL_S" -ge "$TIMEOUT_S" ]; then CAPPED=yes; else CAPPED=no; fi
{
  echo "case=$CASE"; echo "level=$LEVEL"; echo "rc=$RC"; echo "wall_s=$WALL_S"
  echo "ranks=$RANKS"; echo "core_min=$CORE_MIN"; echo "cap_core_min=$CAP_CORE_MIN"
  echo "timeout_s=$TIMEOUT_S"; echo "capped=$CAPPED"; echo "checkmesh_rc=$CHECKMESH_RC"
  echo "started_utc=$(date -u -d "@$START" +%Y-%m-%dT%H:%M:%SZ)"
  echo "ended_utc=$(date -u -d "@$END" +%Y-%m-%dT%H:%M:%SZ)"
} > "$HERE/STATUS.$CASE"
echo "$CASE rc=$RC wall=${WALL_S}s core_min=$CORE_MIN cap=$CAP_CORE_MIN capped=$CAPPED"
# EXIT WITH THE SOLVER'S OWN rc, NEVER 0: a launcher that ends `exit 0` lets a
# queue driver chaining on && march straight past a crash.
exit "$RC"
