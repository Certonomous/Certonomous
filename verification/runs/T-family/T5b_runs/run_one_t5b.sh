#!/bin/bash
# T5b LAUNCHER -- rc IS THE SOLVER'S, AND THE CAP IS ENFORCED, NOT REPORTED.
#
# ===========================================================================
# WHAT THIS FILE CHANGES FROM `../T5_runs/run_one_t5.sh`, AND WHY
# ===========================================================================
# The detach architecture, the B1 `setsid` finding, the arming guard, the age
# guard and the independent-witness `capped` flag are ADOPTED VERBATIM from
# run_one_t5.sh.  That file already enforces its cap: it runs the solver under
# `timeout "$TIMEOUT_S"`.  Two things it does NOT do are added here.
#
# 1. THE CAP AND THE ARGV CANNOT DISAGREE.  In T5 the wall-seconds timeout was
#    typed into the queue entry's argv by hand, INDEPENDENTLY of the registered
#    cap.  `T5_CUBE_c` then ran with `timeout_s=8208` (136.8 core-min) against a
#    registered 45.6 core-min, and `verification/runs/T-family/T5_runs/
#    T5_CUBE_c/CAP_OVERRUN.txt` records the result verbatim:
#
#      "CAP OVERRUN REPORTED, NOT ENFORCED: case T5_C elapsed 11433 s > 1.10 x
#       registered 2736 s (45.6 core-min / 1 ranks). The run was NOT killed"
#
#    A cap that reports is not a cap.  CLAUDE.md rule 12: an overrun STOPS the
#    run.  So THIS file takes `--cap-core-min`, derives the wall-seconds itself
#    (`cap * 60 / ranks`), and REFUSES unless that cap equals the one in the
#    frozen `T5B_CAPS.txt` for this case.  It prints `CAP AGREES <case> <cap>`
#    before the solver starts.  A hand-typed argv can no longer widen a cap.
#
# 2. `--kill-after`.  Bare `timeout` sends SIGTERM.  A solver that traps or
#    ignores SIGTERM keeps running and the cap is again advisory.
#    `--kill-after=120` follows with SIGKILL, which nothing survives.
#
# STILL NOT `timeout --preserve-status` -- run_one_t5.sh's measurement stands:
# expiry and a genuine SIGTERM death become indistinguishable.  `capped` is
# taken from the WALL CLOCK, an independent witness no dying process can forge.
# ===========================================================================
set -eu

usage() {
    cat >&2 <<'U'
usage: run_one_t5b.sh --case-dir DIR --cap-core-min N [--ranks N] [--solver NAME]
                      [--foam-bashrc PATH|none] [--no-detach]
       run_one_t5b.sh --drive-cap-kill        (driven proof that the cap KILLS)
  --cap-core-min  the REGISTERED cap in core-minutes.  Wall seconds are derived
                  HERE as cap*60/ranks and checked against T5B_CAPS.txt.
                  There is no --timeout: an argv cannot set the cap.
U
    exit 2
}

CASE_DIR=""; CAP_CORE_MIN=""; RANKS=1
SOLVER="chtMultiRegionSimpleFoam"; DETACH=1; DRIVE_KILL=0
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
while [ $# -gt 0 ]; do
    case "$1" in
        --case-dir) CASE_DIR="${2:-}"; shift 2 ;;
        --cap-core-min) CAP_CORE_MIN="${2:-}"; shift 2 ;;
        --ranks)    RANKS="${2:-}"; shift 2 ;;
        --solver)   SOLVER="${2:-}"; shift 2 ;;
        --foam-bashrc) FOAM_BASHRC="${2:-}"; shift 2 ;;
        --no-detach) DETACH=0; shift ;;
        --drive-cap-kill) DRIVE_KILL=1; shift ;;
        *) usage ;;
    esac
done

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- THE DRIVEN CAP PROOF -------------------------------------------------
# Runs the SAME enforcement line this file uses on the solver, against a child
# that would run for 600 s, with a 5 s cap.  A cap that cannot be shown to kill
# is an assertion.  L-314: every guard ships its planted-failure proof.
if [ "$DRIVE_KILL" = "1" ]; then
    echo "run_one_t5b.sh --drive-cap-kill"
    # The drive uses kill-after=3 so the proof finishes in seconds; PRODUCTION
    # uses kill-after=120, a grace for a solver that is mid-field-write when
    # SIGTERM arrives.  The MECHANISM proved here is identical; only the grace
    # differs, and the grace can only DELAY a kill, never prevent one.
    F=0
    T0=$(date +%s)
    set +e
    timeout --kill-after=120 --signal=TERM 5 bash -c 'sleep 600'
    RC=$?
    set -e
    T1=$(date +%s); W=$((T1 - T0))
    echo "  arm 1 : a WELL-BEHAVED 'sleep 600' under a 5 s cap"
    echo "          wall ${W} s   rc ${RC}"
    [ "$W" -ge 5 ] && [ "$W" -le 20 ] || { echo "  FAIL the cap did not stop a 600 s child"; F=1; }
    [ "$RC" -ne 0 ] || { echo "  FAIL the capped child returned rc 0"; F=1; }
    [ "$F" = "0" ] && echo "  ok    STOPPED AT THE CAP by SIGTERM (wall ${W}s, rc ${RC})"

    T0=$(date +%s)
    set +e
    timeout --kill-after=3 --signal=TERM 5 bash -c 'trap "" TERM; sleep 600'
    RC3=$?
    set -e
    T1=$(date +%s); W3=$((T1 - T0))
    echo "  arm 2 : a SIGTERM-IGNORING 'sleep 600' under a 5 s cap, kill-after 3 s"
    echo "          wall ${W3} s   rc ${RC3}"
    [ "$W3" -ge 5 ] && [ "$W3" -le 25 ] || { echo "  FAIL a SIGTERM-ignoring child outlived the cap"; F=1; }
    [ "$RC3" -ne 0 ] || { echo "  FAIL the SIGKILLed child returned rc 0"; F=1; }
    [ "$F" = "0" ] && echo "  ok    A SIGTERM-IGNORING CHILD IS STILL KILLED (SIGKILL after the grace)"
    # the negative half: a child INSIDE the cap must NOT be killed
    T0=$(date +%s); set +e
    timeout --kill-after=120 --signal=TERM 30 bash -c 'sleep 2'
    RC2=$?; set -e
    T1=$(date +%s); W2=$((T1 - T0))
    [ "$RC2" = "0" ] && [ "$W2" -lt 30 ] || { echo "  FAIL a child INSIDE the cap was disturbed (rc $RC2, wall $W2)"; F=1; }
    [ "$F" = "0" ] && echo "  ok    a child INSIDE the cap runs to completion untouched (wall ${W2}s, rc ${RC2})"
    echo "CAP-KILL PROOF $([ "$F" = "0" ] && echo PASS || echo FAIL)"
    exit "$F"
fi

[ -n "$CASE_DIR" ] && [ -n "$CAP_CORE_MIN" ] || usage
[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
case "$RANKS" in ''|*[!0-9]*) echo "REFUSE: --ranks must be an integer" >&2; exit 2;; esac
case "$CAP_CORE_MIN" in ''|*[!0-9.]*) echo "REFUSE: --cap-core-min must be numeric" >&2; exit 2;; esac

CASE_DIR="$(cd "$CASE_DIR" && pwd)"
ROOT="$(dirname "$CASE_DIR")"
CASE="$(basename "$CASE_DIR")"
STATUS="$ROOT/STATUS.$CASE"

# --- CAP AGREEMENT: the argv may not widen the registered cap -------------
CAPS="$SELF_DIR/T5B_CAPS.txt"
[ -f "$CAPS" ] || { echo "REFUSE: no frozen cap table at $CAPS; a cap nobody registered is not a cap" >&2; exit 2; }
REG_CAP="$(awk -v c="$CASE" -F'=' '$1==c {print $2}' "$CAPS")"
[ -n "$REG_CAP" ] || { echo "REFUSE: case $CASE has no row in $CAPS" >&2; exit 2; }
AGREE=$(awk -v a="$CAP_CORE_MIN" -v b="$REG_CAP" 'BEGIN{print (a==b)?"1":"0"}')
[ "$AGREE" = "1" ] || { echo "REFUSE: --cap-core-min $CAP_CORE_MIN DISAGREES with the registered cap $REG_CAP for $CASE. This is the T5 CAP_OVERRUN shape and it stops here." >&2; exit 2; }
TIMEOUT_S=$(awk -v c="$CAP_CORE_MIN" -v r="$RANKS" 'BEGIN{printf "%d", (c*60.0)/r}')
[ "$TIMEOUT_S" -gt 0 ] || { echo "REFUSE: derived timeout is not positive" >&2; exit 2; }
echo "CAP AGREES $CASE $CAP_CORE_MIN core-min at $RANKS ranks -> timeout ${TIMEOUT_S} s"

if [ "$DETACH" = "1" ] && [ "${T5B_DETACHED:-}" != "1" ]; then
    T5B_DETACHED=1 exec setsid "$0" --case-dir "$CASE_DIR" --cap-core-min "$CAP_CORE_MIN" \
        --ranks "$RANKS" --solver "$SOLVER" --foam-bashrc "$FOAM_BASHRC" \
        --no-detach </dev/null >>"$CASE_DIR/log.launch" 2>&1 &
    echo "launched $CASE detached; STATUS will appear at $STATUS"
    exit 0
fi

write_status() {   # rc wall capped checkmesh_rc note
    tmp="$STATUS.tmp.$$"
    printf 'case=%s\nrc=%s\nwall_s=%s\nranks=%s\ncore_min=%s\ncap_core_min=%s\ntimeout_s=%s\ncapped=%s\ncheckMesh_rc=%s\nsolver=%s\nsolver_path=%s\nnote=%s\n' \
        "$CASE" "$1" "$2" "$RANKS" \
        "$(awk -v w="$2" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')" \
        "$CAP_CORE_MIN" "$TIMEOUT_S" "$3" "$4" "$SOLVER" "${SOLVER_PATH:-unresolved}" "$5" > "$tmp"
    mv -f "$tmp" "$STATUS"
}

cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

if [ "$FOAM_BASHRC" != "none" ]; then
    [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
    set +u
    # shellcheck disable=SC1090
    . "$FOAM_BASHRC" >/dev/null 2>&1 || true
    set -u
fi
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' NOT RESOLVABLE. Nothing ran, so no STATUS is written and no rc is invented." >&2; exit 2; }

# --- T5b PRECONDITION: the repaired function objects must be on disk ------
# The whole rung exists to make the y+ instrument fire.  Launching a case whose
# controlDict still carries `writeControl writeTime` would reproduce the defect
# and burn the budget doing it.
CD="$CASE_DIR/system/controlDict"
grep -q 'writeTime' "$CD" && { echo "REFUSE: $CD still carries a writeTime control -- that is the T5 defect and this rung exists to remove it" >&2; exit 2; }
[ "$(grep -c 'executeControl  timeStep;' "$CD")" = "2" ] || { echo "REFUSE: $CD does not carry exactly two repaired function objects" >&2; exit 2; }

[ -e "$CASE_DIR/0" ] && { echo "REFUSE: $CASE_DIR/0 already exists -- armed before" >&2; exit 2; }
STALE=$(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' -printf '%f ' 2>/dev/null || true)
[ -n "$STALE" ] && { echo "REFUSE: $CASE_DIR already holds time directories: $STALE" >&2; exit 2; }

[ -d "$CASE_DIR/0.orig" ] || { echo "REFUSE: no 0.orig to arm from" >&2; exit 2; }
cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/" >&2; exit 2; }

CHECKMESH_RC="na"
if command -v checkMesh >/dev/null 2>&1; then
    checkMesh -case "$CASE_DIR" -allRegions > "$CASE_DIR/log.checkMesh" 2>&1 || true
    CHECKMESH_RC=$?
fi

AGE_DATUM="$(find "$CASE_DIR/0" -name T -type f | head -1)"
[ -n "$AGE_DATUM" ] || { echo "REFUSE: no 0/**/T, so the age guard has no datum" >&2; exit 2; }
sleep 1
touch "$AGE_DATUM"

# --- THE SOLVER, UNDER AN ENFORCED CAP ------------------------------------
set +e
T0=$(date +%s)
timeout --kill-after=120 --signal=TERM "$TIMEOUT_S" "$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.solve" 2>&1
RC=$?
T1=$(date +%s)
set -e
WALL=$((T1 - T0))

CAPPED=0
[ "$WALL" -ge "$TIMEOUT_S" ] && CAPPED=1

NOTE=clean
if [ "$CAPPED" = "1" ]; then
    NOTE=CAP_ENFORCED_run_STOPPED_at_registered_cap
    printf '%s CAP ENFORCED: %s was STOPPED at the registered cap %s core-min (%s s wall at %s ranks). CLAUDE.md rule 12: an overrun stops the run; it does not get a new budget. This is a right-censored PENDING, not a failure.\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$CASE" "$CAP_CORE_MIN" "$TIMEOUT_S" "$RANKS" > "$CASE_DIR/CAP_ENFORCED.txt"
elif [ "$RC" = "124" ]; then
    NOTE=CHILD_EXIT_124_NOT_an_expiry_wall_under_cap
elif [ "$RC" -gt 128 ] 2>/dev/null; then
    NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then
    NOTE=SOLVER_NONZERO_EXIT
fi
write_status "$RC" "$WALL" "$CAPPED" "$CHECKMESH_RC" "$NOTE"
echo "$CASE finished: rc=$RC wall=${WALL}s capped=$CAPPED note=$NOTE -> $STATUS"
exit "$RC"
