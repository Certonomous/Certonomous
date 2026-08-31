#!/usr/bin/env bash
# =========================================================================
# T25 CASE LAUNCHER -- Case 4 8-cell battery module, UNGATED FEASIBILITY.
# Modelled on run_one_t20.sh.  The properties inherited, each paid for by a
# specific measured failure:
#   * the solver runs in THIS wrapper's FOREGROUND under `timeout`, with NO
#     `setsid` between them, so `$?` is the SOLVER's status.  Measured on this
#     box: `setsid timeout ... bash -c 'exit 7'` returns 0 -- capturing rc
#     AROUND a setsid line reports 0 for every outcome.  Detachment happens
#     ONCE, by re-exec'ing this file, BEFORE the solver is ever started.
#   * `capped` = (wall_s >= timeout_s) is an INDEPENDENT expiry witness: rc 124
#     collides with a solver that itself exits 124.  It LABELS a non-zero rc;
#     it never voids a run (L-342, bookkeeping never voids physics).
#   * a PRE-FLIGHT REFUSAL writes NO STATUS: nothing ran, so there is no rc,
#     and inventing one is back-dating.
#   * 0/ is armed from 0.orig/ and 0/<region>/T is touched LAST -- that file is
#     the age-guard datum and must date the run allowed to produce the answer.
#   * constant/g is ASSERTED present: T20_LC_c's first attempt died without it
#     (quarantined at T20_LC_c_FAILED_NO_G_20260831T001244Z).
#   * `exit "$RC"` is the LAST line: the wrapper reports the solver's own
#     status, never 0.
#
# usage: run_one_t25.sh --case-dir DIR --timeout SECONDS [--no-detach]
# =========================================================================
set -u
REGION="module"
SOLVER="chtMultiRegionFoam"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
CASE_DIR=""; TIMEOUT_S=""; RANKS=1; DETACH=1

while [ $# -gt 0 ]; do
    case "$1" in
        --case-dir)  CASE_DIR="${2:-}"; shift 2 ;;
        --timeout)   TIMEOUT_S="${2:-}"; shift 2 ;;
        --no-detach) DETACH=0; shift ;;
        *) echo "usage: $0 --case-dir DIR --timeout S [--no-detach]" >&2; exit 2 ;;
    esac
done
[ -n "$CASE_DIR" ] && [ -n "$TIMEOUT_S" ] || { echo "REFUSE: --case-dir and --timeout are required" >&2; exit 2; }
[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
case "$TIMEOUT_S" in ''|*[!0-9]*) echo "REFUSE: --timeout must be integer seconds" >&2; exit 2;; esac

CASE_DIR="$(cd "$CASE_DIR" && pwd)"
ROOT="$(dirname "$CASE_DIR")"
CASE="$(basename "$CASE_DIR")"
STATUS="$ROOT/STATUS.$CASE"

[ -e "$STATUS" ] && { echo "REFUSE: $STATUS exists -- a completed run's record is never overwritten" >&2; exit 2; }

# --- detach ONCE by re-executing this file in a new session ------------------
if [ "$DETACH" = "1" ] && [ "${T25_DETACHED:-}" != "1" ]; then
    T25_DETACHED=1 exec setsid "$0" --case-dir "$CASE_DIR" --timeout "$TIMEOUT_S" \
        --no-detach </dev/null >>"$CASE_DIR/log.launch" 2>&1 &
    echo "launched $CASE detached; STATUS will appear at $STATUS"
    exit 0
fi

write_status() {   # rc wall checkmesh_rc capped note
    tmp="$STATUS.tmp.$$"
    {
      echo "case=$CASE"
      echo "rc=$1"
      echo "wall_s=$2"
      echo "ranks=$RANKS"
      echo "core_min=$(awk -v w="$2" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')"
      echo "timeout_s=$TIMEOUT_S"
      echo "capped=$4"
      echo "checkmesh_rc=$3"
      echo "solver=$SOLVER"
      echo "region=$REGION"
      echo "note=$5"
      echo "tag=FEASIBILITY"
      echo "gated=no"
      echo "started_utc=$(date -u -d "@$T0" +%Y-%m-%dT%H:%M:%SZ)"
      echo "ended_utc=$(date -u -d "@$T1" +%Y-%m-%dT%H:%M:%SZ)"
      echo "loadavg_at_launch=$LOADAVG"
      echo "nproc=$(nproc)"
    } > "$tmp"
    mv -f "$tmp" "$STATUS"
}

cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

# --- 0. the solver must be reachable ----------------------------------------
[ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
set +u
# shellcheck disable=SC1090
. "$FOAM_BASHRC" >/dev/null 2>&1 || true
set -u
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' NOT RESOLVABLE; nothing ran, no STATUS written" >&2; exit 2; }

# --- 1. launch guards --------------------------------------------------------
[ -e "$CASE_DIR/0" ] && { echo "REFUSE: $CASE already has a 0/ directory (the age guard could not be evaluated)" >&2; exit 2; }
while IFS= read -r d; do
    [ -n "$d" ] && { echo "REFUSE: $CASE already has time directory $(basename "$d")" >&2; exit 2; }
done < <(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?' 2>/dev/null)
[ -d "$CASE_DIR/0.orig/$REGION" ] || { echo "REFUSE: no 0.orig/$REGION to arm from" >&2; exit 2; }
[ -f "$CASE_DIR/constant/$REGION/polyMesh/owner" ] || { echo "REFUSE: no mesh -- run build_t25.py" >&2; exit 2; }
[ -f "$CASE_DIR/constant/regionProperties" ] || { echo "REFUSE: no constant/regionProperties" >&2; exit 2; }
# THE T20_LC_c LESSON, ASSERTED RATHER THAN ASSUMED:
[ -f "$CASE_DIR/constant/g" ] || { echo "REFUSE: constant/g ABSENT -- this is exactly what killed T20_LC_c (T20_LC_c_FAILED_NO_G_20260831T001244Z)" >&2; exit 2; }
for f in T p; do
    [ -f "$CASE_DIR/0.orig/$REGION/$f" ] || { echo "REFUSE: 0.orig/$REGION/$f missing -- the field set is incomplete" >&2; exit 2; }
done

# --- 2. checkMesh, recorded rather than assumed (infrastructure) -------------
checkMesh -case "$CASE_DIR" -region "$REGION" > "$CASE_DIR/log.checkMesh" 2>&1
CHECKMESH_RC=$?

# --- 3. arm 0/ from 0.orig; 0/<region>/T touched LAST (age-guard datum) ------
cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/ from 0.orig" >&2; exit 2; }
sleep 1
touch "$CASE_DIR/0/$REGION/T" || { echo "REFUSE: could not touch 0/$REGION/T" >&2; exit 2; }

# --- 4. the solver, in the FOREGROUND, rc captured FROM IT -------------------
LOADAVG="$(cut -d' ' -f1-3 /proc/loadavg | tr ' ' '/')"
T0=$(date +%s)
timeout --signal=TERM --kill-after=60 "$TIMEOUT_S" "$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.solve" 2>&1
RC=$?
T1=$(date +%s)
WALL=$((T1 - T0))
if [ "$WALL" -ge "$TIMEOUT_S" ]; then CAPPED=yes; else CAPPED=no; fi
NOTE=clean
if [ "$RC" = "124" ]; then NOTE=CAP_EXPIRED_or_child_exit_124
elif [ "$RC" -gt 128 ] 2>/dev/null; then NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then NOTE=SOLVER_NONZERO_EXIT
fi
write_status "$RC" "$WALL" "$CHECKMESH_RC" "$CAPPED" "$NOTE"
echo "$CASE finished: rc=$RC wall=${WALL}s capped=$CAPPED note=$NOTE -> $STATUS"
exit "$RC"
