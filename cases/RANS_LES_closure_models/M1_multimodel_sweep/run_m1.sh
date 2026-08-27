#!/bin/bash
#!/bin/bash
# NOTE: line 1 is the mandatory DRAFT banner, so THIS SHEBANG IS INERT -- the
# kernel only honours a shebang on line 1.  Every queue entry therefore invokes
# this file as `/bin/bash run_m1.sh ...`, never as `./run_m1.sh`, which would
# fall through to /bin/sh and break `set -o pipefail` and the [[ ]]-free but
# bash-specific constructs below.
# ---------------------------------------------------------------------------
# M1 multi-model sweep -- THE DRIVER A QUEUE ENTRY NAMES.  One case, one arm,
# one rank.  Writes STATUS at exit (Sanaa 2026-08-27 section 2) so the runner
# can detect completion and trigger grading.
#
#   run_m1.sh --case-dir <abs> --timeout-s <n> --cap-core-min <x> [--arm <a>]
#
# THE rc IS CAPTURED INSIDE THIS WRAPPER.  `setsid timeout cmd` exits 0 for
# every outcome, so an rc captured AROUND a setsid line is meaningless
# (setsid-parent-returns-zero).  This script runs simpleFoam in its own
# foreground and reads $? from it directly.  Anything may detach this script;
# the rc is already inside STATUS by then.
#
# It REFUSES, and writes NO STATUS, when nothing ran: an unreachable solver, a
# missing 0.orig, an already-armed case.  Inventing an rc for a run that never
# started is back-dating.
# ---------------------------------------------------------------------------
set -u
set -o pipefail

CASE_DIR=""; TIMEOUT_S=""; CAP_CORE_MIN=""; ARM=""
RANKS=1
SOLVER="simpleFoam"
FOAM_BASHRC="${FOAM_BASHRC:-/usr/lib/openfoam/openfoam2606/etc/bashrc}"
END_TIME=20000                  # PREREGISTRATION.md section 3.  Registered.
AGE_DATUM_FIELD="U"             # PREREGISTRATION.md section 6 C4.  Registered.

while [ $# -gt 0 ]; do
    case "$1" in
        --case-dir)     CASE_DIR="$2"; shift 2 ;;
        --timeout-s)    TIMEOUT_S="$2"; shift 2 ;;
        --cap-core-min) CAP_CORE_MIN="$2"; shift 2 ;;
        --arm)          ARM="$2"; shift 2 ;;
        --foam-bashrc)  FOAM_BASHRC="$2"; shift 2 ;;
        *) echo "REFUSE: unknown argument $1" >&2; exit 2 ;;
    esac
done
[ -n "$CASE_DIR" ]     || { echo "REFUSE: --case-dir is required" >&2; exit 2; }
[ -n "$TIMEOUT_S" ]    || { echo "REFUSE: --timeout-s is required (the cap is not optional)" >&2; exit 2; }
[ -n "$CAP_CORE_MIN" ] || { echo "REFUSE: --cap-core-min is required" >&2; exit 2; }
case "$TIMEOUT_S" in ''|*[!0-9]*) echo "REFUSE: --timeout-s must be an integer" >&2; exit 2 ;; esac

CASE="$(basename "$CASE_DIR")"
[ -n "$ARM" ] || ARM="$(basename "$(dirname "$CASE_DIR")")"
STATUS="$CASE_DIR/STATUS"

write_status() {   # rc wall_s capped checkMesh_rc note
    # ATOMIC: temp file in the SAME directory, then renamed.  A reader never
    # sees a half-written STATUS, and a crash mid-write leaves NO STATUS at all
    # -- which the comparator treats as INFRASTRUCTURE NOT MEASURED (L-342,
    # Sanaa desk ruling R-RC), never as a passing rc.
    local tmp="$STATUS.tmp.$$"
    local core_min
    core_min="$(awk -v w="$2" -v r="$RANKS" 'BEGIN{printf "%.4f", w*r/60.0}')"
    local over
    over="$(awk -v c="$core_min" -v cap="$CAP_CORE_MIN" 'BEGIN{print (c>cap)?1:0}')"
    printf 'case=%s\narm=%s\nrc=%s\nwall_s=%s\nranks=%s\ncore_min=%s\ncap_core_min=%s\ncap_core_min_exceeded=%s\ntimeout_s=%s\ncapped=%s\ncheckMesh_rc=%s\nendTime=%s\nsolver=%s\nsolver_path=%s\nstarted_utc=%s\nfinished_utc=%s\nhost=%s\nnote=%s\n' \
        "$CASE" "$ARM" "$1" "$2" "$RANKS" "$core_min" "$CAP_CORE_MIN" "$over" \
        "$TIMEOUT_S" "$3" "$4" "$END_TIME" "$SOLVER" "${SOLVER_PATH:-unresolved}" \
        "${T0_UTC:-unknown}" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(hostname)" "$5" > "$tmp"
    mv -f "$tmp" "$STATUS"
}

cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

# --- 0. THE SOLVER MUST BE REACHABLE BEFORE ANYTHING ELSE ------------------
# A detached wrapper inherits no login shell, so nothing has put the solver on
# PATH.  An unreachable solver is a case that CANNOT RUN: it REFUSES and writes
# NO STATUS.  Nothing ran, there is no rc, and inventing one would be back-dating.
if [ "$FOAM_BASHRC" != "none" ]; then
    [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
    # `set -u` must be lifted across the source: the OpenFOAM bashrc aborts
    # under -u at an unbound variable and the solver is then still not on PATH.
    # The lift covers the source and nothing else.
    set +u
    # shellcheck disable=SC1090
    . "$FOAM_BASHRC" >/dev/null 2>&1 || true
    set -u
fi
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' NOT RESOLVABLE after sourcing $FOAM_BASHRC. Nothing ran, so no STATUS is written and no rc is invented." >&2; exit 2; }

export OMP_NUM_THREADS=1        # ranks = 1 means ranks = 1

# --- 1. ARMING GUARD: refuse a case that has been armed before ------------
[ -e "$CASE_DIR/0" ] && { echo "REFUSE: $CASE_DIR/0 already exists -- armed before" >&2; exit 2; }
STALE=$(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' -printf '%f ' 2>/dev/null || true)
[ -n "$STALE" ] && { echo "REFUSE: $CASE_DIR already holds time directories: $STALE -- a run is never launched into a tree that already holds an answer" >&2; exit 2; }

# --- 2. the registered configuration must be the one on disk --------------
[ -d "$CASE_DIR/0.orig" ] || { echo "REFUSE: no 0.orig to arm from" >&2; exit 2; }
[ -f "$CASE_DIR/system/controlDict" ] || { echo "REFUSE: no system/controlDict" >&2; exit 2; }
CD_END=$(sed -n 's/^[[:space:]]*endTime[[:space:]]\{1,\}\([^;]*\);.*/\1/p' "$CASE_DIR/system/controlDict" | head -1 | tr -d '[:space:]')
[ "$CD_END" = "$END_TIME" ] || { echo "REFUSE: controlDict endTime is '$CD_END', the registered cap is $END_TIME" >&2; exit 2; }
CD_FROM=$(sed -n 's/^[[:space:]]*startFrom[[:space:]]\{1,\}\([^;]*\);.*/\1/p' "$CASE_DIR/system/controlDict" | head -1 | tr -d '[:space:]')
[ "$CD_FROM" = "startTime" ] || { echo "REFUSE: controlDict startFrom is '$CD_FROM', not startTime -- the run would restart from a shipped answer" >&2; exit 2; }
RASM=$(sed -n 's/^[[:space:]]*RASModel[[:space:]]\{1,\}\([^;]*\);.*/\1/p' "$CASE_DIR/constant/turbulenceProperties" 2>/dev/null | head -1 | tr -d '[:space:]')
case "$ARM:$RASM" in
    kOmegaSST_null:kOmegaSST) : ;;
    kOmega:kOmega)            : ;;
    *) echo "REFUSE: arm '$ARM' but constant/turbulenceProperties says RASModel '$RASM'" >&2; exit 2 ;;
esac

# --- 3. arm: 0/ from 0.orig ------------------------------------------------
cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/" >&2; exit 2; }

# --- 4. checkMesh, RECORDED rather than assumed ---------------------------
# NOTE the shape.  `checkMesh ... || true; RC=$?` records $? AFTER `|| true`,
# which is ALWAYS 0 -- the field would record nothing.  rc is captured directly.
CHECKMESH_RC="na"
if command -v checkMesh >/dev/null 2>&1; then
    set +e
    checkMesh -case "$CASE_DIR" > "$CASE_DIR/log.checkMesh" 2>&1
    CHECKMESH_RC=$?
    set -e
fi

# --- 5. THE AGE-GUARD DATUM, TOUCHED LAST ---------------------------------
# `0/U` is the registered age datum for this incompressible family (the
# analogue of the thermal family's `0/T`).  It is touched IMMEDIATELY before
# the solver so its mtime dates the run allowed to produce the answer
# (standing rule 4).  Absent, the guard would be deciding on nothing, so the
# run must not start.
AGE_DATUM="$CASE_DIR/0/$AGE_DATUM_FIELD"
[ -f "$AGE_DATUM" ] || { echo "REFUSE: no 0/$AGE_DATUM_FIELD, so the age guard has no datum" >&2; exit 2; }
sleep 1
touch "$AGE_DATUM"

# --- 6. THE SOLVER, IN THIS SHELL'S FOREGROUND, rc CAPTURED FROM IT -------
T0_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
set +e
T0=$(date +%s)
timeout "$TIMEOUT_S" "$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.run" 2>&1
RC=$?
T1=$(date +%s)
set -e
WALL=$((T1 - T0))

# --- 7. `capped` FROM AN INDEPENDENT WITNESS, NEVER FROM THE rc ----------
# 137 is SIGKILL -- produced by `timeout --kill-after` AND by the OOM killer.
# 124 is timeout's expiry code AND a legal exit status for any child.  Deciding
# "was I stopped by my own budget?" from the rc alone would silently relabel an
# OOM KILL as a BUDGET STOP.  The wall clock comes from outside the dying
# process and cannot be forged.
CAPPED=0
[ "$WALL" -ge "$TIMEOUT_S" ] && CAPPED=1

NOTE=clean
if [ "$CAPPED" = "1" ]; then
    NOTE=CAP_EXPIRED_wall_ge_timeout
elif [ "$RC" = "124" ]; then
    NOTE=CHILD_EXIT_124_NOT_an_expiry_wall_under_cap
elif [ "$RC" -gt 128 ] 2>/dev/null; then
    NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then
    NOTE=SOLVER_NONZERO_EXIT
fi

write_status "$RC" "$WALL" "$CAPPED" "$CHECKMESH_RC" "$NOTE"

echo "STATUS written: $STATUS  (rc=$RC wall_s=$WALL capped=$CAPPED note=$NOTE)"
exit "$RC"
