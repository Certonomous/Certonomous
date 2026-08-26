#!/bin/bash
# run_one_t5_x2d.sh -- THE PRECURSOR LAUNCHER (T5 AMENDMENT 1, pre-first-compute).
# Line-for-line the frozen run_one_t5.sh (blob 313df45c), with ONE change: the
# age-guard datum is 0/**/U, because the simpleFoam precursor X_2d carries no T
# field and the frozen launcher REFUSED it at zero compute on 2026-08-26T16:28:57Z
# ("REFUSE: no 0/**/T, so the age guard has no datum").  The frozen file is
# untouched.  X_2d is UNGRADED: nothing a verdict depends on is readable from it.
# T5 LAUNCHER -- rc IS THE SOLVER'S, MEASURED, NEVER FABRICATED.
#
# ============================================================================
# B1: WHY THIS FILE IS NOT WRITTEN `setsid nohup ... ; RC=$?`
# ============================================================================
# The T5 draft's section 15 said the solver would be launched "detached with
# `setsid nohup`".  MEASURED ON THIS BOX, 2026-08-26, before this file existed:
#
#     setsid timeout 5 bash -c 'exit 7'          ->  rc = 0      NOT 7
#     timeout 5 bash -c 'exit 7'                 ->  rc = 7
#     setsid nohup bash -c 'exit 7'              ->  rc = 0      NOT 7
#     timeout 5 bash -c 'kill -8 $$'             ->  rc = 136    (SIGFPE, cored)
#     setsid timeout 5 bash -c 'kill -8 $$'      ->  rc = 0      <-- THE KILLER
#
# `setsid` FORKS when it is not already a process-group leader.  The parent
# exits 0 IMMEDIATELY while the child carries the real status into a new
# session where nothing collects it.  THE LAST LINE IS THE ONE THAT MATTERS:
# a solver that dies of a floating-point exception and dumps core is recorded
# as rc=0 -- A FALSE PASS ON THE LOAD-BEARING LIMB OF THE STRICT COMPLETION
# RULE, with nobody watching.  T8's level `m` died exactly that way and
# returned an honest 136 only because it was NOT launched under setsid.
#
# That is STRICTLY WORSE than K0d's absent STATUS file, which at least produced
# an honest NOT DONE.  A missing rc is a gap; a fabricated rc is a lie.
#
# ARCHITECTURE, adopted from `scripts/launch_k0f.sh` rather than invented
# (the territory rule: adopt the registered shape):
#   * the caller starts THIS FILE, which re-execs ITSELF ONCE under `setsid`;
#   * THE WRAPPER'S OWN EXIT STATUS IS MEANINGLESS AND IS NOT USED;
#   * inside the wrapper the solver runs under `timeout` in the wrapper's OWN
#     FOREGROUND with no `setsid` between them, so `$?` IS the solver's;
#   * the last line is `exit "$RC"` so a foreground caller gets the truth too.
#
# DO NOT ADD `timeout --preserve-status`.  MEASURED HERE:
#     timeout --preserve-status 1 sleep 5   ->  rc = 143
#     timeout 5 bash -c 'kill -15 $$'       ->  rc = 143
# expiry and a genuine SIGTERM death become INDISTINGUISHABLE.  Instead this
# file records `capped` from an INDEPENDENT WITNESS -- the wall clock -- which
# no dying process can forge by choosing its exit status.
# ============================================================================
set -eu

SELF="$(cd "$(dirname "$0")" && pwd)"

usage() {
    cat >&2 <<'U'
usage: run_one_t5.sh --case-dir DIR --timeout SECONDS [--ranks N] [--solver NAME]
                     [--foam-bashrc PATH|none] [--no-detach]
  --timeout   the registered per-case cap ALREADY CONVERTED to wall seconds:
              timeout_s = cap_core_min * 60 / ranks
U
    exit 2
}

CASE_DIR=""; TIMEOUT_S=""; RANKS=1
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
        *) usage ;;
    esac
done
[ -n "$CASE_DIR" ] && [ -n "$TIMEOUT_S" ] || usage
[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
case "$TIMEOUT_S" in ''|*[!0-9]*) echo "REFUSE: --timeout must be integer seconds" >&2; exit 2;; esac
case "$RANKS" in ''|*[!0-9]*) echo "REFUSE: --ranks must be an integer" >&2; exit 2;; esac

CASE_DIR="$(cd "$CASE_DIR" && pwd)"
ROOT="$(dirname "$CASE_DIR")"
CASE="$(basename "$CASE_DIR")"
STATUS="$ROOT/STATUS.$CASE"

# --- detach ONCE, by re-executing this same file in a new session ----------
if [ "$DETACH" = "1" ] && [ "${T5_DETACHED:-}" != "1" ]; then
    T5_DETACHED=1 exec setsid "$0" --case-dir "$CASE_DIR" --timeout "$TIMEOUT_S" \
        --ranks "$RANKS" --solver "$SOLVER" --foam-bashrc "$FOAM_BASHRC" \
        --no-detach </dev/null >>"$CASE_DIR/log.launch" 2>&1 &
    echo "launched $CASE detached; STATUS will appear at $STATUS"
    exit 0
fi

write_status() {   # rc wall capped checkmesh_rc note
    # ATOMIC: temp file in the SAME directory then renamed, so a reader never
    # sees a half-written STATUS, and a crash mid-write leaves NO STATUS at all
    # -- which the comparator refuses on, rather than reading a truncated rc as
    # a passing one.
    tmp="$STATUS.tmp.$$"
    printf 'case=%s\nrc=%s\nwall_s=%s\nranks=%s\ncore_min=%s\ntimeout_s=%s\ncapped=%s\ncheckMesh_rc=%s\nsolver=%s\nsolver_path=%s\nnote=%s\n' \
        "$CASE" "$1" "$2" "$RANKS" \
        "$(awk -v w="$2" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')" \
        "$TIMEOUT_S" "$3" "$4" "$SOLVER" "${SOLVER_PATH:-unresolved}" "$5" > "$tmp"
    mv -f "$tmp" "$STATUS"
}

cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

# --- 0. THE SOLVER MUST BE REACHABLE BEFORE ANYTHING ELSE -----------------
# K0f attempt 1 died here on all seven fired cases: rc=127, wall=0, because a
# detached wrapper inherits no login shell and nothing had put the solver on
# PATH.  AND THE REFUSAL IS THE POINT, NOT THE SOURCING: an unreachable solver
# is a case that CANNOT RUN, so it REFUSES and WRITES NO STATUS.  Nothing ran,
# there is no rc, and inventing one would be back-dating.
if [ "$FOAM_BASHRC" != "none" ]; then
    [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
    # `set -u` must be lifted across the source: measured, the OpenFOAM bashrc
    # aborts under -u at `WM_PROJECT_DIR: unbound variable` and the solver is
    # then still not on PATH.  The lift covers the source and nothing else.
    set +u
    # shellcheck disable=SC1090
    . "$FOAM_BASHRC" >/dev/null 2>&1 || true
    set -u
fi
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' NOT RESOLVABLE after sourcing $FOAM_BASHRC. Nothing ran, so no STATUS is written and no rc is invented." >&2; exit 2; }

# --- 1. ARMING GUARD: refuse a case that has been armed before ------------
[ -e "$CASE_DIR/0" ] && { echo "REFUSE: $CASE_DIR/0 already exists -- armed before" >&2; exit 2; }
STALE=$(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' -printf '%f ' 2>/dev/null || true)
[ -n "$STALE" ] && { echo "REFUSE: $CASE_DIR already holds time directories: $STALE" >&2; exit 2; }

# --- 2. arm: 0/ from 0.orig, region fields included -----------------------
[ -d "$CASE_DIR/0.orig" ] || { echo "REFUSE: no 0.orig to arm from" >&2; exit 2; }
cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/" >&2; exit 2; }

# --- 3. checkMesh, RECORDED rather than assumed --------------------------
CHECKMESH_RC="na"
if command -v checkMesh >/dev/null 2>&1; then
    checkMesh -case "$CASE_DIR" -allRegions > "$CASE_DIR/log.checkMesh" 2>&1 || true
    CHECKMESH_RC=$?
fi

# --- 4. THE AGE-GUARD DATUM, TOUCHED LAST -------------------------------
# `0/**/T` is touched IMMEDIATELY before the solver so its mtime dates the run
# allowed to produce the answer (standing rule 4).  Absent, the guard would be
# deciding on a None, so the run must not start.
AGE_DATUM="$(find "$CASE_DIR/0" -name U -type f | head -1)"
[ -n "$AGE_DATUM" ] || { echo "REFUSE: no 0/**/U, so the age guard has no datum" >&2; exit 2; }
sleep 1
touch "$AGE_DATUM"

# --- 5. THE SOLVER, IN THIS SHELL'S FOREGROUND, rc CAPTURED FROM IT ------
set +e
T0=$(date +%s)
timeout "$TIMEOUT_S" "$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.solve" 2>&1
RC=$?
T1=$(date +%s)
set -e
WALL=$((T1 - T0))

# --- 6. `capped` FROM AN INDEPENDENT WITNESS, NEVER FROM THE rc ----------
# 137 is SIGKILL -- produced by `timeout --kill-after` on expiry AND by the OOM
# killer.  124 is timeout's expiry code AND a legal exit status for any child.
# Deciding "was I stopped by my own budget?" from the rc alone would silently
# relabel an OOM KILL as a BUDGET STOP, and a budget stop is right-censored
# PENDING rather than a failure -- so the real defect would never be triaged.
# The wall clock comes from outside the dying process and cannot be forged.
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
echo "$CASE finished: rc=$RC wall=${WALL}s capped=$CAPPED note=$NOTE -> $STATUS"

# --- 7. the launcher's OWN status carries the solver's -------------------
# The alternative is `exit 0` with the rc only in STATUS, which is defensible
# but is a trap for a detached queue driven by `&&`: T8's launcher exited 0
# while its level `m` was dumping core.  Choosing is mandatory; this rung
# chooses to carry it.
exit "$RC"
