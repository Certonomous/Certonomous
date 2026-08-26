#!/usr/bin/env bash
# ==========================================================================
# K0f CASE LAUNCHER -- rc-CAPTURING, DETACHED, AND QUEUE-COMPATIBLE.
#
# NO K0d ANCESTOR EXISTS.  This is the one instrument in the K0f set with no
# K0d file to descend from, and that absence IS the defect it repairs: K0d had
# no launcher at all.  Its L1 launch (commit bf7e9428) was an ad-hoc command
# line, so no `STATUS.<case>` was ever written, so standing rule 4's `rc = 0`
# limb could not be evaluated, so `M1_c` and `M2_c` are NOT DONE despite
# reaching endTime with an End line, a full ExecutionTime count, every
# registered field present and a passing age guard -- SIX CLAUSES OUT OF SEVEN.
# The lane that refused to back-date `rc=0` was right: a plausible
# reconstruction is not the measurement the clause requires.
#
# WRITTEN TO A LAB-WIDE INTERFACE, NOT A RUNG-LOCAL ONE.  With cfd building a
# detached queue runner, a run has no agent watching it, and `STATUS.<case>`
# becomes the ONLY evidence the run terminated cleanly -- it IS rule 4's rc
# limb.  So this script takes its case directory, its cap and its ranks as
# arguments, hard-codes no rung, and writes the pool STATUS format that
# `mark_done_*.py` already parses.
#
# ------------------------------------------------------------------------
# THE TRAP THAT MAKES THE OBVIOUS REPAIR WORSE THAN THE DEFECT.
# MEASURED ON THIS BOX (util-linux 2.39.3, GNU coreutils 9.4), NOT RECALLED:
#
#     setsid timeout 5 bash -c 'exit 7'   ->  rc = 0        <-- NOT 7
#     setsid --wait timeout 5 bash -c 'exit 7'   ->  rc = 7
#
# `setsid` FORKS when it is not already a process-group leader, and the parent
# exits 0 IMMEDIATELY while the child carries the real status into a new
# session where nothing collects it.  So a launcher written as
# `setsid timeout ... ; rc=$?` WRITES rc=0 FOR A CRASHED SOLVER.  That is
# strictly worse than K0d's absent STATUS: an absent STATUS produced an honest
# NOT DONE; a fabricated rc=0 produces a FALSE PASS on the load-bearing limb of
# the completion rule, with nobody watching.
#
# THE ARCHITECTURE THAT AVOIDS IT.  This script is the WRAPPER.  The caller (an
# agent, or the queue) starts THIS FILE under bare `setsid` and returns
# immediately; the wrapper's own exit status is meaningless and is not used.
# Inside the wrapper the solver runs under `timeout` in the FOREGROUND with no
# `setsid` between them, so `$?` is genuinely the solver's status.
#
# THE STATUSES, AND WHY THEY MUST NOT BE CONFLATED (all measured here):
#     child exits n           ->  timeout passes n through          (7 -> 7)
#     child dies on signal n  ->  128 + n           (SIGSEGV -> 139)
#     cap expires             ->  124
# A 124 is a CAP-STOP (rule 12: an overrun stops the run) and a non-zero child
# status is a CRASH (a crash is a finding until triage says otherwise).  Those
# are opposite meanings and STATUS records them distinguishably.
# DO NOT ADD `timeout --preserve-status`: measured here it turns expiry into
# 143 = 128 + SIGTERM, which COLLIDES with a genuine SIGTERM death and destroys
# the distinction.
# RESIDUAL AMBIGUITY, DISCLOSED RATHER THAN PAPERED OVER: a solver that itself
# exits 124 is indistinguishable from an expiry.  STATUS therefore also records
# `timeout_s` and `wall`, so a reader can see whether the wall clock reached
# the cap; that is a discriminator, not a proof.
# ==========================================================================
set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    cat >&2 <<'U'
usage: launch_k0f.sh --case-dir DIR --timeout SECONDS [--ranks N]
                     [--solver NAME] [--no-detach]

  --case-dir  the case directory; STATUS is written to its PARENT as
              STATUS.<basename>, which is where mark_done_k0f.py reads it
  --timeout   the registered per-case cap, ALREADY CONVERTED to wall seconds:
              timeout_s = cap_core_min * 60 / ranks   (K0d re-registration 8.1)
  --ranks     default 1; K0f is registered SERIAL (section 6)
  --solver    default buoyantBoussinesqSimpleFoam
  --no-detach run in the foreground (used by the selftest)
U
    exit 2
}

CASE_DIR=""; TIMEOUT_S=""; RANKS=1
SOLVER="buoyantBoussinesqSimpleFoam"; DETACH=1
while [ $# -gt 0 ]; do
    case "$1" in
        --case-dir) CASE_DIR="${2:-}"; shift 2 ;;
        --timeout)  TIMEOUT_S="${2:-}"; shift 2 ;;
        --ranks)    RANKS="${2:-}"; shift 2 ;;
        --solver)   SOLVER="${2:-}"; shift 2 ;;
        --no-detach) DETACH=0; shift ;;
        --selftest) exec "$SELF/launch_k0f_selftest.sh" ;;
        *) usage ;;
    esac
done
[ -n "$CASE_DIR" ] && [ -n "$TIMEOUT_S" ] || usage
[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
case "$RANKS" in ''|*[!0-9]*) echo "REFUSE: --ranks must be an integer" >&2; exit 2;; esac
case "$TIMEOUT_S" in ''|*[!0-9]*) echo "REFUSE: --timeout must be integer seconds" >&2; exit 2;; esac
[ "$RANKS" = "1" ] || { echo "REFUSE: K0f is registered SERIAL (section 6); --ranks=$RANKS" >&2; exit 2; }

CASE_DIR="$(cd "$CASE_DIR" && pwd)"
ROOT="$(dirname "$CASE_DIR")"
CASE="$(basename "$CASE_DIR")"
STATUS="$ROOT/STATUS.$CASE"

# --- detach, ONCE, by re-executing this same file in a new session --------
# The wrapper below then runs the solver in its own FOREGROUND, which is the
# only way `$?` is the solver's status and not setsid's fabricated 0.
if [ "$DETACH" = "1" ] && [ "${K0F_DETACHED:-}" != "1" ]; then
    K0F_DETACHED=1 exec setsid "$0" --case-dir "$CASE_DIR" --timeout "$TIMEOUT_S" \
        --ranks "$RANKS" --solver "$SOLVER" --no-detach </dev/null \
        >>"$CASE_DIR/log.launch" 2>&1 &
    echo "launched $CASE detached; STATUS will appear at $STATUS"
    exit 0
fi

write_status() {   # rc wall checkmesh_rc note
    # ATOMIC: written to a temp file in the SAME directory and renamed, so a
    # reader never sees a half-written STATUS and a crash mid-write leaves no
    # STATUS at all -- which mark_done_k0f.py REFUSES on, rather than reading
    # a truncated rc as a passing one.
    tmp="$STATUS.tmp.$$"
    printf 'rc=%s wall=%s checkMesh_rc=%s timeout_s=%s ranks=%s solver=%s case=%s note=%s\n' \
        "$1" "$2" "$3" "$TIMEOUT_S" "$RANKS" "$SOLVER" "$CASE" "$4" > "$tmp"
    mv -f "$tmp" "$STATUS"
}

cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

# --- 1. THE CONSUMER-SIDE COMPLETENESS ASSERTION, BEFORE THE SOLVER -------
# Under a detached queue there is nobody to diagnose a crash, so this refusal
# is worth far more here than a post-hoc log read.  NO STATUS IS WRITTEN on a
# pre-flight refusal: nothing ran, so there is no rc to report, and inventing
# one would be the back-dating this whole file exists to prevent.
if ! python3 "$SELF/build_k0f.py" --preflight "$CASE_DIR"; then
    echo "REFUSE: $CASE failed the consumer-side completeness assertion; no solver started, no STATUS written" >&2
    exit 2
fi

# --- 2. checkMesh, recorded rather than assumed ---------------------------
CHECKMESH_RC=""
if command -v checkMesh >/dev/null 2>&1; then
    checkMesh -case "$CASE_DIR" > "$CASE_DIR/log.checkMesh" 2>&1
    CHECKMESH_RC=$?
else
    CHECKMESH_RC="na"
fi

# --- 3. THE AGE-GUARD DATUM, TOUCHED LAST -------------------------------
# `0/T` is touched IMMEDIATELY before the solver so its mtime dates the run
# allowed to produce the answer (standing rule 4, the age guard).  If it is
# absent the run must not start: the guard would have no datum and would then
# be deciding on a None.
[ -f "$CASE_DIR/0/T" ] || { echo "REFUSE: no 0/T, so the age guard has no datum" >&2; exit 2; }
touch "$CASE_DIR/0/T"

# --- 4. THE SOLVER, IN THE FOREGROUND, rc CAPTURED FROM IT ---------------
T0=$(date +%s)
timeout "$TIMEOUT_S" "$SOLVER" -case "$CASE_DIR" > "$CASE_DIR/log.solve" 2>&1
RC=$?
T1=$(date +%s)
WALL=$((T1 - T0))

NOTE=clean
if [ "$RC" = "124" ]; then
    NOTE=CAP_EXPIRED_or_child_exit_124
elif [ "$RC" -gt 128 ] 2>/dev/null; then
    NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then
    NOTE=SOLVER_NONZERO_EXIT
fi
write_status "$RC" "$WALL" "$CHECKMESH_RC" "$NOTE"
echo "$CASE finished: rc=$RC wall=${WALL}s note=$NOTE  ->  $STATUS"
exit "$RC"
