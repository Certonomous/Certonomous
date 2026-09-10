#!/usr/bin/env bash
# ==========================================================================
# K0h CASE LAUNCHER -- rc-CAPTURING, DETACHED, AND QUEUE-COMPATIBLE.
#
# NO K0d ANCESTOR EXISTS.  This is the one instrument in the K0h set with no
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
# ========================================================================
# K0h DERIVATION BLOCK -- READ THIS BEFORE THE DIFF.
#
# This file is a DERIVATION of the FROZEN K0g instrument
#     scripts/launch_k0g.sh
#     git blob e14de416050c12d6cafe60a6a2bc4ff4d4127a86
# registered at docs/campaigns/F14-cooling-ladder/K0h_PREREGISTRATION.md
# section 7.7.  THE K0g ANCESTOR IS NOT EDITED (standing rule 6); this
# file was written from its HEAD BLOB, not from the worktree.
#
# THE DERIVATION IS MECHANICALLY CHECKABLE.  Outside this block every
# byte of this file is the ancestor's bytes under the UNCONDITIONAL
# substitution
#     k0g -> k0h ,  K0g -> K0h ,  K0G -> K0H
# and NOTHING ELSE.  There is no functional change in this file.
#
# CONSEQUENCE OF AN UNCONDITIONAL RENAME, DISCLOSED RATHER THAN
# SMOOTHED.  A historical note below that now reads "K0h attempt 1",
# "measured on K0h" or similar describes an event that happened under
# K0g, this file's ancestor.  NO HISTORICAL CLAIM IN THIS FILE IS A K0h
# MEASUREMENT.  K0h HAS RUN NO COMPUTE: no
# verification/runs/F14-cooling-ladder/K0h_runs/ exists, and none may be
# created until the supervisor FREEZES the pre-registration by sha.
#
# PROVENANCE PINS -- DECLARATIVE AND PRINT-ONLY.  They gate nothing and
# no code branches on them.  GRADING_PATH_FREEZE_COMMIT is the DRAFT
# placeholder "PIN-AT-FREEZE"; THE SUPERVISOR SETS IT AT FREEZE and no
# lane, and no run, sets it.
# ========================================================================
GRADING_PATH_FREEZE_COMMIT="PIN-AT-FREEZE"   # SUPERVISOR SETS THIS AT FREEZE
SELF_REL="scripts/launch_k0h.sh"
export GRADING_PATH_FREEZE_COMMIT SELF_REL

set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    cat >&2 <<'U'
usage: launch_k0h.sh --case-dir DIR --timeout SECONDS [--ranks N]
                     [--solver NAME] [--no-detach]

  --case-dir  the case directory; STATUS is written to its PARENT as
              STATUS.<basename>, which is where mark_done_k0h.py reads it
  --timeout   the registered per-case cap, ALREADY CONVERTED to wall seconds:
              timeout_s = cap_core_min * 60 / ranks   (K0d re-registration 8.1)
  --ranks     default 1; K0h is registered SERIAL (section 6)
  --solver    default buoyantBoussinesqPimpleFoam (K0h is TRANSIENT)
  --foam-bashrc  the OpenFOAM environment to source; default
              /usr/lib/openfoam/openfoam2606/etc/bashrc.  Pass "none" ONLY in
              a selftest whose solver is already on PATH.
  --no-detach run in the foreground (used by the selftest)
U
    exit 2
}

CASE_DIR=""; TIMEOUT_S=""; RANKS=1
SOLVER="buoyantBoussinesqPimpleFoam"; DETACH=1
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
while [ $# -gt 0 ]; do
    case "$1" in
        --case-dir) CASE_DIR="${2:-}"; shift 2 ;;
        --timeout)  TIMEOUT_S="${2:-}"; shift 2 ;;
        --ranks)    RANKS="${2:-}"; shift 2 ;;
        --solver)   SOLVER="${2:-}"; shift 2 ;;
        --foam-bashrc) FOAM_BASHRC="${2:-}"; shift 2 ;;
        --no-detach) DETACH=0; shift ;;
        --selftest) exec bash "$SELF/launch_k0h_selftest.sh" ;;  # via bash: no +x dependency (see re-exec note below)
        *) usage ;;
    esac
done
[ -n "$CASE_DIR" ] && [ -n "$TIMEOUT_S" ] || usage
[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
case "$RANKS" in ''|*[!0-9]*) echo "REFUSE: --ranks must be an integer" >&2; exit 2;; esac
case "$TIMEOUT_S" in ''|*[!0-9]*) echo "REFUSE: --timeout must be integer seconds" >&2; exit 2;; esac
[ "$RANKS" = "1" ] || { echo "REFUSE: K0h is registered SERIAL (section 6); --ranks=$RANKS" >&2; exit 2; }

CASE_DIR="$(cd "$CASE_DIR" && pwd)"
ROOT="$(dirname "$CASE_DIR")"
CASE="$(basename "$CASE_DIR")"
STATUS="$ROOT/STATUS.$CASE"

# --- CLAUSE 7, CALL SITE 1 OF 2 IN THIS FILE: BEFORE THE DETACH FORK ------
# K0H_CLAUSE7_GUARD  (this sentinel is what the selftest's NEGATIVE CONTROL
# strips, so the guard can be shown to be the thing that refuses)
#
# THE DEFECT THIS REPAIRS.  `mark_done_k0h.py --launch-guard` implements
# standing rule 4's clause 7 -- REFUSE a case in which `0` or any numeric time
# directory already exists -- and until this line it HAD NO CALL SITE ANYWHERE.
# A grep for `launch_guard|launch-guard` across `orchestrate_k0h.py`,
# `build_k0h.py` and this file returned ZERO
# (`verification/campaign/K0H_AGE_GUARD_RESTART_RULING_2026-09-10.md` section 8).
# Its selftest passed the whole time because it drove the function DIRECTLY --
# a green control over zero call sites is a pass about the code, not the world.
#
# WHY HERE, AND WHY ALSO AGAIN BELOW.  This point is reached by BOTH the parent
# and the re-exec'd detached child, so a refusal is visible SYNCHRONOUSLY to
# whoever invoked the launcher -- including `orchestrate_k0h.py`, whose
# `Popen` sends this file's output to DEVNULL and would otherwise never see it.
# The second call site, immediately before the stage, is defence in depth in
# the lab's own precedented form: `launch_t1b_L4.sh` applies G3 in the
# foreground and `run_one_t1b_L4.sh:40` re-checks it before `cd`.
if ! python3 "$SELF/mark_done_k0h.py" --root "$ROOT" --launch-guard "$CASE"; then
    echo "REFUSE: $CASE failed clause 7 (launch guard); no solver started, no STATUS written" >&2
    exit 2
fi

# --- detach, ONCE, by re-executing this same file in a new session --------
# The wrapper below then runs the solver in its own FOREGROUND, which is the
# only way `$?` is the solver's status and not setsid's fabricated 0.
# RE-EXEC VIA `bash "$0"`, NOT `"$0"` DIRECTLY: setsid execs its argument, so a
# bare `"$0"` demands the executable bit on this file.  git here has
# core.fileMode=false and stores mode 100644, so a fresh checkout would lack +x
# and the DETACHED (default) path would die with "setsid: Permission denied"
# while check_comparator_freeze IDENTITY still passed -- a masked break.
# Invoking the interpreter explicitly makes the detached path independent of the
# +x bit.  Do NOT change this back to a bare `"$0"`.
if [ "$DETACH" = "1" ] && [ "${K0H_DETACHED:-}" != "1" ]; then
    K0H_DETACHED=1 exec setsid bash "$0" --case-dir "$CASE_DIR" --timeout "$TIMEOUT_S" \
        --ranks "$RANKS" --solver "$SOLVER" --foam-bashrc "$FOAM_BASHRC" \
        --no-detach </dev/null \
        >>"$CASE_DIR/log.launch" 2>&1 &
    echo "launched $CASE detached; STATUS will appear at $STATUS"
    exit 0
fi

write_status() {   # rc wall checkmesh_rc note
    # ATOMIC: written to a temp file in the SAME directory and renamed, so a
    # reader never sees a half-written STATUS and a crash mid-write leaves no
    # STATUS at all -- which mark_done_k0h.py REFUSES on, rather than reading
    # a truncated rc as a passing one.
    tmp="$STATUS.tmp.$$"
    printf 'rc=%s wall=%s checkMesh_rc=%s timeout_s=%s ranks=%s solver=%s solver_path=%s case=%s note=%s\n' \
        "$1" "$2" "$3" "$TIMEOUT_S" "$RANKS" "$SOLVER" "${SOLVER_PATH:-unresolved}" "$CASE" "$4" > "$tmp"
    mv -f "$tmp" "$STATUS"
}

cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

# --- 0. THE SOLVER MUST BE REACHABLE, AND THIS IS CHECKED BEFORE ANYTHING -
#
# ATTEMPT 1 OF K0h DIED HERE, ON ALL SEVEN FIRED CASES: `rc=127 wall=0
# checkMesh_rc=na`, "timeout: failed to run command
# 'buoyantBoussinesqSimpleFoam': No such file or directory".  THIS FILE SOURCED
# NO OpenFOAM ENVIRONMENT AT ALL.  A detached wrapper re-exec'd under `setsid`
# inherits no login shell, so nothing had ever put the solver on PATH.
#
# WHY THE SELFTEST DID NOT CATCH IT, WHICH IS THE PART WORTH KEEPING:
# every arm installed a FAKE SOLVER ON PATH and drove it to a real exit state.
# That proved the rc plumbing -- and it did work: rc=127 was captured
# truthfully and atomically, and `checkMesh_rc=na` recorded honestly that
# `checkMesh` was equally unreachable rather than inventing a pass.  But A
# LAUNCHER SELFTEST THAT SUPPLIES ITS OWN FIXTURES IS TESTING THE LAUNCHER
# AGAINST ITSELF.  It proves the code paths and says nothing about the one
# thing a launcher exists to do: REACH A REAL SOLVER IN A REAL ENVIRONMENT.
# The negative-control arm in launch_k0h_selftest.sh resolves the REAL binary
# on the REAL PATH, with no fixture, and is the arm that would have caught this.
#
# AND THE REFUSAL IS THE POINT, NOT THE SOURCING.  Sourcing alone would turn a
# loud 127 into a quiet success-until-it-is-not.  An unreachable solver is a
# case that CANNOT RUN, so it REFUSES (exit 2) and WRITES NO STATUS -- nothing
# ran, there is no rc, and inventing one is the back-dating this file exists to
# prevent.  rc=127 in a STATUS file is a solver that ran and failed; this is a
# solver that never started, and the two must not read alike.
if [ "$FOAM_BASHRC" != "none" ]; then
    [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC; refusing rather than launching into a shell where the solver cannot be found (K0h attempt 1: seven cases, rc=127, wall=0)" >&2; exit 2; }
    # `set -u` MUST BE LIFTED ACROSS THE SOURCE, AND THIS IS NOT A STYLE POINT.
    # MEASURED ON THIS BOX: under `set -u` the OpenFOAM bashrc ABORTS at
    #     /usr/lib/openfoam/openfoam2606/etc/bashrc: line 184:
    #     WM_PROJECT_DIR: unbound variable
    # and the solver is then STILL not on PATH.  This file sets -u at the top,
    # so the first version of this very repair WOULD HAVE FAILED THE SAME WAY
    # -- the environment would silently not load and the launch would refuse
    # again.  It was caught by the real-solver negative-control arm in
    # launch_k0h_selftest.sh BEFORE the re-fire, which is exactly the arm's
    # purpose.  -u is restored immediately after; the lift covers the source
    # and nothing else.
    set +u
    # shellcheck disable=SC1090
    . "$FOAM_BASHRC" >/dev/null 2>&1 || true
    set -u
fi
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' is NOT RESOLVABLE after sourcing ${FOAM_BASHRC}. Nothing ran, so no STATUS is written and no rc is invented." >&2; exit 2; }

# --- 1'. CLAUSE 7, CALL SITE 2 OF 2, THEN THE STAGE `0.orig` -> `0` -------
# K0H_CLAUSE7_GUARD
# Re-checked here because the environment sourcing above can take real time and
# because a directly-invoked `--no-detach` run must be guarded on its own path,
# not only on the path that forked it.  `run_one_t1b_L4.sh:40` is the same
# discipline.  NOTHING HAS BEEN WRITTEN TO THE CASE YET at this point, so a
# refusal here leaves the case exactly as the builder left it.
if ! python3 "$SELF/mark_done_k0h.py" --root "$ROOT" --launch-guard "$CASE"; then
    echo "REFUSE: $CASE failed clause 7 (launch guard, re-check); no solver started, no STATUS written" >&2
    exit 2
fi

# THE STAGE.  `build_k0h.py` writes `0.orig/` and NO `0/`; this line creates
# `0/` -- the T-family pattern of `T1b_L4_AMENDMENT.md` section 7 and
# `launch_t4d.sh:158-160`.  It is what makes clause 7 above judgeable (there is
# no `0/` until this instant) and clause 6's age guard meaningful (`0/T` is
# touched at section 3 below, LAST, and so dates THIS run).
# NO SILENT FALLBACK IN EITHER DIRECTION:
#   - an absent `0.orig/` REFUSES, rather than launching a case that was never
#     built or was built by a pre-repair builder;
#   - the `cp` is skipped only when `0/` ALREADY exists, which the two guards
#     above make unreachable in production.  That branch exists so the
#     selftest's negative control -- the same dirty case with the guard
#     stripped -- can be shown to LAUNCH.  A control shown only in its silent
#     direction is not a control.
[ -d "$CASE_DIR/0.orig" ] || { echo "REFUSE: no 0.orig/ in $CASE, so there is nothing to stage 0/ from and no age-guard datum; the case was not built by this builder" >&2; exit 2; }
if [ ! -d "$CASE_DIR/0" ]; then
    cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/ from 0.orig/" >&2; exit 2; }
fi

# --- 1. THE CONSUMER-SIDE COMPLETENESS ASSERTION, BEFORE THE SOLVER -------
# Under a detached queue there is nobody to diagnose a crash, so this refusal
# is worth far more here than a post-hoc log read.  NO STATUS IS WRITTEN on a
# pre-flight refusal: nothing ran, so there is no rc to report, and inventing
# one would be the back-dating this whole file exists to prevent.
if ! python3 "$SELF/build_k0h.py" --preflight "$CASE_DIR"; then
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
timeout "$TIMEOUT_S" "$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.solve" 2>&1
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
