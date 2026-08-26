#!/bin/bash
# T11 -- run ONE registered level, capture the SOLVER's rc, write STATUS.<case>.
# Usage: run_one_t11.sh <level: c|m|f> <cap_core_min> <ranks>
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
LEVEL="$1"; CAP_CORE_MIN="$2"; RANKS="$3"
die() { echo "REFUSE: $*" >&2; exit 3; }
case "$LEVEL" in c|m|f) ;; *) die "G0: level must be c, m or f; got '$LEVEL'";; esac
[ -n "$CAP_CORE_MIN" ] || die "G0: cap_core_min is required (CLAUDE.md rule 12)"
[ -n "$RANKS" ]        || die "G0: ranks is required"
CASE="T11_PW_$LEVEL"; CDIR="$HERE/$CASE"
TIMEOUT_S=$(( CAP_CORE_MIN * 60 / RANKS ))
[ -d "$CDIR" ] || die "G1: no case directory $CDIR -- run build_t11.py first"

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
