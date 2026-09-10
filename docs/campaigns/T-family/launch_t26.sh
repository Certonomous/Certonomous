#!/usr/bin/env bash
# ==========================================================================
# T26 LEVEL LAUNCHER -- rc-CAPTURING, DETACHED, AND THE LIVE CALL SITE FOR
# CLAUSE 7 (call site CS-1, T26_PREREGISTRATION.md:647).
#
# REGISTERED PATH: T26_PREREGISTRATION.md:802 registers this file at
# `docs/campaigns/T-family/launch_t26.sh`.  It is NOT under
# verification/runs/T-family/T26_runs/, because :106 makes the ABSENCE of that
# directory the rule-2 pre-compute condition of the registration.  THIS SCRIPT
# is what creates the run root, at launch and not before.
#
# WHY THIS FILE MATTERS MORE THAN ITS SIZE SUGGESTS.  The supervisor's finding
# of 2026-09-10: clause 7 is DEFINED in seven K0-family instruments and CALLED
# BY ZERO LAUNCHERS.  Every one of those builders created `0/` itself, so
# "refuse if 0/ exists" could never fire on a legitimate launch.  Seven dead
# levers.  Here the guard is CALLED, from `mark_done_t26.py --launch-guard`,
# BEFORE `cp -r 0.orig 0`, and `--selftest-clause7` PROVES IT FIRES by driving
# the three registered arms through this very file as a subprocess.
#
#   * the solver runs in THIS wrapper's FOREGROUND under `timeout`, with NO
#     `setsid` between them, so `$?` is the solver's own status.  Measured on
#     this box and recorded in launch_t4e.sh:6-9: `setsid timeout ... bash -c
#     'exit 7'` returns 0 for every outcome -- rc is captured INSIDE the
#     detached wrapper, never around the setsid line.
#   * `capped` = (wall_s >= timeout_s) is an INDEPENDENT expiry witness: rc 124
#     collides with a solver that itself exits 124, and 137 with an OOM kill.
#     It is INFRASTRUCTURE (L-342): it LABELS a non-zero rc, it never voids a
#     run.
#   * the `timeout` here is the HANG GUARD of registration :737, NOT a budget
#     cap.  Sanaa's CASE_PROTOCOL closing clause suspends the cap-stop for this
#     rung (:716); this guard is against a wedged or spinning process, and it
#     is named a hang guard everywhere it appears so no later reader mistakes
#     it for the cap she suspended.
#   * a PRE-FLIGHT REFUSAL WRITES NO STATUS: nothing ran, so there is no rc,
#     and inventing one is the back-dating these guards exist to prevent.
#   * `0/fluid/T` is touched LAST, so it dates the run allowed to produce the
#     answer -- the referent of clause 6, the age guard.
#   * `exit "$RC"` is the LAST line: the wrapper reports the solver's own
#     status to its caller, never 0.
#
# usage: launch_t26.sh --case-dir DIR --timeout SECONDS [--ranks N]
#                      [--solver chtMultiRegionSimpleFoam] [--foam-bashrc F]
#                      [--no-detach] [--dry-run]
#        launch_t26.sh --selftest-clause7
#   --dry-run  run every guard and every pre-flight check, then STOP before the
#              solver.  Used by the clause-7 selftest so the guard really
#              executes while no solver is ever started.
# ==========================================================================
set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARD="$SELF/mark_done_t26.py"

usage() { sed -n '/^# usage:/,/^# ====/p' "$0" >&2; exit 2; }

# ==========================================================================
# --selftest-clause7 : THE THREE ARMS, registration :655-661.
# Arm C is the NEGATIVE CONTROL and is what makes arm B evidence: without it,
# arm B's refusal could be caused by anything in this file; with it, the
# refusal is attributable to the guard and to nothing else.  ONLY the guard's
# verdict is intercepted in arm C -- the guard REALLY EXECUTES in all three.
# ==========================================================================
if [ "${1:-}" = "--selftest-clause7" ]; then
    TMP="$(mktemp -d -t t26_c7_XXXXXX)"
    trap 'rm -rf "$TMP"' EXIT
    RCALL=0
    mk() {  # $1 = name, $2 = "dirty" to pre-create 0/
        d="$TMP/$1"; mkdir -p "$d/0.orig" "$d/constant/polyMesh" "$d/system"
        for f in T U p_rgh alphat nut k omega; do echo "x" > "$d/0.orig/$f"; done
        echo "x" > "$d/constant/polyMesh/owner"
        echo "endTime 10;" > "$d/system/controlDict"
        [ "${2:-}" = "dirty" ] && mkdir -p "$d/0"
        echo "$d"
    }

    # ---- ARM A: clean case -> the guard PASSES and the launcher PROCEEDS ----
    A="$(mk armA)"
    OUT="$(bash "$0" --case-dir "$A" --timeout 60 --no-detach --dry-run 2>&1)"; RC=$?
    if [ "$RC" = "0" ] && printf '%s' "$OUT" | grep -q 'CLAUSE 7 launch guard PASSED'; then
        echo "  [ok ] ARM A clean case (only 0.orig/) -> guard PASSED, launcher proceeded (exit 0)"
    else
        echo "  [BAD] ARM A clean case -> exit $RC; expected the guard to pass and the launcher to proceed"
        RCALL=1
    fi

    # ---- ARM B: 0/ pre-created -> REFUSE, exit 2, `CLAUSE 7`, nothing run ---
    B="$(mk armB dirty)"
    OUT="$(bash "$0" --case-dir "$B" --timeout 60 --no-detach --dry-run 2>&1)"; RC=$?
    HASC7=0; printf '%s' "$OUT" | grep -q 'CLAUSE 7' && HASC7=1
    NOSTATUS=1; [ -e "$TMP/STATUS.armB" ] && NOSTATUS=0
    NORUN=1; printf '%s' "$OUT" | grep -q 'DRY RUN: every guard passed' && NORUN=0
    if [ "$RC" = "2" ] && [ "$HASC7" = "1" ] && [ "$NOSTATUS" = "1" ] && [ "$NORUN" = "1" ]; then
        echo "  [ok ] ARM B 0/ pre-created -> REFUSED exit 2, 'CLAUSE 7' in output, no STATUS, nothing launched"
    else
        echo "  [BAD] ARM B exit=$RC clause7=$HASC7 no_status=$NOSTATUS nothing_launched=$NORUN"
        RCALL=1
    fi

    # ---- ARM C: NEGATIVE CONTROL -- guard forced clear, SAME dirty case -----
    # A stub guard that always exits 0 is placed ahead of the real one via
    # T26_GUARD_OVERRIDE.  Nothing else about the launcher changes.  If the
    # dirty case now LAUNCHES, arm B's refusal was the guard's doing and
    # nothing else's.
    STUB="$TMP/stub_guard.py"
    printf '%s\n' 'import sys; print("STUB GUARD: verdict forced clear"); sys.exit(0)' > "$STUB"
    C="$(mk armC dirty)"
    OUT="$(T26_GUARD_OVERRIDE="$STUB" bash "$0" --case-dir "$C" --timeout 60 --no-detach --dry-run 2>&1)"; RC=$?
    if [ "$RC" = "0" ] && printf '%s' "$OUT" | grep -q 'DRY RUN: every guard passed'; then
        echo "  [ok ] ARM C NEGATIVE CONTROL: guard forced clear, SAME dirty case -> it LAUNCHES."
        echo "        Arm B's refusal is therefore attributable to CLAUSE 7 and to nothing else."
    else
        echo "  [BAD] ARM C negative control: exit $RC -- the dirty case did NOT launch with the"
        echo "        guard forced clear, so arm B's refusal is NOT attributable to the guard."
        RCALL=1
    fi
    exit "$RCALL"
fi

CASE_DIR=""; TIMEOUT_S=""; RANKS=8; DRYRUN=0
SOLVER="chtMultiRegionSimpleFoam"; DETACH=1
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
while [ $# -gt 0 ]; do
    case "$1" in
        --case-dir) CASE_DIR="${2:-}"; shift 2 ;;
        --timeout)  TIMEOUT_S="${2:-}"; shift 2 ;;
        --ranks)    RANKS="${2:-}"; shift 2 ;;
        --solver)   SOLVER="${2:-}"; shift 2 ;;
        --foam-bashrc) FOAM_BASHRC="${2:-}"; shift 2 ;;
        --no-detach) DETACH=0; shift ;;
        --dry-run)  DRYRUN=1; shift ;;
        *) usage ;;
    esac
done
[ -n "$CASE_DIR" ] && [ -n "$TIMEOUT_S" ] || usage
[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
case "$RANKS"     in ''|*[!0-9]*) echo "REFUSE: --ranks must be an integer" >&2; exit 2;; esac
case "$TIMEOUT_S" in ''|*[!0-9]*) echo "REFUSE: --timeout must be integer seconds" >&2; exit 2;; esac

CASE_DIR="$(cd "$CASE_DIR" && pwd)"
ROOT="$(dirname "$CASE_DIR")"
CASE="$(basename "$CASE_DIR")"
STATUS="$ROOT/STATUS.$CASE"

# --- a completed run's record is never overwritten --------------------------
[ -e "$STATUS" ] && { echo "REFUSE: $STATUS exists -- a completed run's record is never overwritten; nothing ran, nothing written" >&2; exit 2; }

# ==========================================================================
# CS-1: CLAUSE 7, CALLED -- NEVER REIMPLEMENTED (CLAUDE.md rule 14).
# This runs BEFORE `cp -r 0.orig 0` and before anything is written.  The
# override exists ONLY for the arm-C negative control and is named so in the
# output, so a forced-clear guard can never pass silently.
# ==========================================================================
GUARD_PROG="${T26_GUARD_OVERRIDE:-$GUARD}"
[ "$GUARD_PROG" != "$GUARD" ] && echo "WARNING: clause-7 guard OVERRIDDEN with $GUARD_PROG -- this is the arm-C negative control and is NEVER a production path"
[ -f "$GUARD_PROG" ] || { echo "REFUSE: the clause-7 guard $GUARD_PROG is absent; a launcher with no guard is the seven-dead-levers defect" >&2; exit 2; }
if ! python3 "$GUARD_PROG" --launch-guard "$CASE_DIR"; then
    echo "REFUSE: CLAUSE 7 refused $CASE. Nothing ran, no STATUS written. A refusal STOPS THE LEVEL SET; it does not skip a level (registration :650)." >&2
    exit 2
fi

# --- detach ONCE by re-executing this file in a new session -----------------
if [ "$DETACH" = "1" ] && [ "${T26_DETACHED:-}" != "1" ]; then
    T26_DETACHED=1 exec setsid "$0" --case-dir "$CASE_DIR" --timeout "$TIMEOUT_S" \
        --ranks "$RANKS" --solver "$SOLVER" --foam-bashrc "$FOAM_BASHRC" \
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
      echo "solver_path=${SOLVER_PATH:-unresolved}"
      echo "note=$5"
      echo "started_utc=$(date -u -d "@$T0" +%Y-%m-%dT%H:%M:%SZ)"
      echo "ended_utc=$(date -u -d "@$T1" +%Y-%m-%dT%H:%M:%SZ)"
    } > "$tmp"
    mv -f "$tmp" "$STATUS"
}

cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

# --- the registered field set must be staged in 0.orig ----------------------
for f in T U p_rgh alphat nut k omega; do
    [ -f "$CASE_DIR/0.orig/$f" ] || { echo "REFUSE: 0.orig/$f missing -- the registered field set is incomplete" >&2; exit 2; }
done
[ -f "$CASE_DIR/constant/polyMesh/owner" ] || { echo "REFUSE: $CASE has no mesh (constant/polyMesh/owner)" >&2; exit 2; }

# --- the solver must be reachable BEFORE anything is written ----------------
if [ "$DRYRUN" = "0" ] && [ "$FOAM_BASHRC" != "none" ]; then
    [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
    set +u
    # shellcheck disable=SC1090
    . "$FOAM_BASHRC" >/dev/null 2>&1 || true
    set -u
    SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
    [ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' is NOT RESOLVABLE after sourcing $FOAM_BASHRC. Nothing ran, no STATUS written." >&2; exit 2; }
fi

# --- START.<level>: the load witness of registration :763-765 ---------------
# A level whose recorded load average at launch shows a saturated box produces
# a COST but NOT a calibration row.  Written BEFORE the solver starts.
{
  echo "start_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "loadavg=$(cat /proc/loadavg)"
  echo "nproc=$(nproc)"
  echo "ranks=$RANKS"
  echo "hang_guard_s=$TIMEOUT_S   # a HANG guard, NOT the budget cap Sanaa suspended"
} > "$ROOT/START.$CASE"

if [ "$DRYRUN" = "1" ]; then
    echo "DRY RUN: every guard passed and nothing was launched. No solver started, no STATUS written."
    exit 0
fi

# --- checkMesh, recorded rather than assumed (infrastructure) ---------------
checkMesh -case "$CASE_DIR" -allRegions > "$CASE_DIR/log.checkMesh" 2>&1
CHECKMESH_RC=$?

# --- arm 0/ from 0.orig; 0/fluid/T touched LAST (the age-guard datum) -------
cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/ from 0.orig" >&2; exit 2; }
sleep 1
touch "$CASE_DIR/0/fluid/T" || { echo "REFUSE: could not touch 0/fluid/T -- the age guard would have no referent" >&2; exit 2; }

# --- the solver, in the FOREGROUND of THIS wrapper, rc captured from it -----
T0=$(date +%s)
if [ "$RANKS" -gt 1 ]; then
    timeout "$TIMEOUT_S" mpirun -np "$RANKS" "$SOLVER_PATH" -case "$CASE_DIR" -parallel > "$CASE_DIR/log.solve" 2>&1
else
    timeout "$TIMEOUT_S" "$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.solve" 2>&1
fi
RC=$?
T1=$(date +%s)
WALL=$((T1 - T0))
if [ "$WALL" -ge "$TIMEOUT_S" ]; then CAPPED=yes; else CAPPED=no; fi
NOTE=clean
if [ "$RC" = "124" ]; then NOTE=HANG_GUARD_EXPIRED_or_child_exit_124
elif [ "$RC" -gt 128 ] 2>/dev/null; then NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then NOTE=SOLVER_NONZERO_EXIT
fi
write_status "$RC" "$WALL" "$CHECKMESH_RC" "$CAPPED" "$NOTE"
echo "$CASE finished: rc=$RC wall=${WALL}s capped=$CAPPED note=$NOTE  ->  $STATUS"
exit "$RC"
