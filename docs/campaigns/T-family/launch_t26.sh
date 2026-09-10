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

# ==========================================================================
# --selftest-witness : A FORK RETURNING IS NOT A LAUNCH, proved BOTH ways by
# execution.  Arm W-GOOD's solver really starts and writes; arm W-DEAD's dies
# instantly.  The launcher must record the first as launched and the second as
# `launched: false` / PENDING -- never as launched.
# ==========================================================================
if [ "${1:-}" = "--selftest-witness" ]; then
    TMP="$(mktemp -d -t t26_w_XXXXXX)"
    trap 'rm -rf "$TMP"' EXIT
    RCALL=0
    mkcase() {
        d="$TMP/$1"; mkdir -p "$d/0.orig/fluid" "$d/constant/polyMesh" "$d/system"
        for f in T U p_rgh alphat nut k omega; do echo x > "$d/0.orig/$f"; done
        echo x > "$d/0.orig/fluid/T"; echo x > "$d/constant/polyMesh/owner"
        echo "endTime 10;" > "$d/system/controlDict"; echo "$d"
    }
    # a stub "solver" that writes output then lingers -> W1 must fire
    GOOD="$TMP/good_solver"; printf '#!/bin/bash\necho "Starting time loop"\nsleep 25\n' > "$GOOD"; chmod +x "$GOOD"
    # a stub that dies instantly having written NOTHING -> no witness
    DEAD="$TMP/dead_solver"; printf '#!/bin/bash\nexit 127\n' > "$DEAD"; chmod +x "$DEAD"

    A="$(mkcase wgood)"
    OUT="$(T26_WITNESS_DEADLINE_S=30 bash "$0" --case-dir "$A" --timeout 60 \
           --ranks 1 --solver "$GOOD" --foam-bashrc none 2>&1)"; RC=$?
    if [ "$RC" = "0" ] && printf '%s' "$OUT" | grep -q 'launched: true' \
       && printf '%s' "$OUT" | grep -qE 'witness: W[12]'; then
        echo "  [ok ] W-GOOD solver starts and writes -> launched: true, $(printf '%s' "$OUT" | grep -oE 'witness: W[12]')"
    else
        echo "  [BAD] W-GOOD exit $RC; expected launched: true with a W1/W2 witness"
        printf '%s\n' "$OUT" | sed 's/^/        /' | head -4; RCALL=1
    fi

    # W-DEAD: a solver that STARTS and immediately exits 127.
    # `launched` MEANS "A SOLVER WAS STARTED", AND NOTHING ELSE (cfd 7d7fcebf).
    # A solver that ran and crashed IS launched, reported WITH its rc as a
    # CRASH FINDING. Collapsing that into `launched: false` would hide a
    # finding about the case behind a launch failure. My first draft of this
    # arm expected `launched: false` and was WRONG on exactly that point; the
    # arm is corrected here rather than the instrument being bent to match it.
    B="$(mkcase wdead)"
    OUT="$(T26_WITNESS_DEADLINE_S=8 bash "$0" --case-dir "$B" --timeout 60 \
           --ranks 1 --solver "$DEAD" --foam-bashrc none 2>&1)"; RC=$?
    if [ "$RC" = "0" ] && printf '%s' "$OUT" | grep -q 'launched: true' \
       && printf '%s' "$OUT" | grep -q 'FINISHED WITH CRASH' \
       && printf '%s' "$OUT" | grep -q 'rc=127'; then
        echo "  [ok ] W-DEAD solver STARTS then exits 127 -> launched: true WITH rc=127,"
        echo "        state FINISHED WITH CRASH -- a crash is a finding about the CASE,"
        echo "        never hidden inside a launch failure"
    else
        echo "  [BAD] W-DEAD exit $RC; expected launched:true + FINISHED WITH CRASH rc=127"
        printf '%s\n' "$OUT" | sed 's/^/        /' | head -5; RCALL=1
    fi

    # ---- W-NOARM: THE BRANCH cfd's TWO CODE READS MISSED --------------------
    # A child that dies BEFORE EVER TOUCHING 0/T. This is the branch where an
    # absolute-time mtime test (`mtime >= t_launch - 1.0`) CONFIRMS A LAUNCH
    # THAT NEVER HAPPENED. Here 0.orig/fluid/T is BACK-DATED an hour, so any
    # absolute-time or slack-window test would still pass it, and only a STRICT
    # INCREASE over the captured baseline correctly reports no arming.
    C="$(mkcase wnoarm)"
    touch -d '1 hour ago' "$C/0.orig/fluid/T"
    rm -f "$C/constant/polyMesh/owner"     # child refuses at pre-flight, before arming 0/
    OUT="$(T26_WITNESS_DEADLINE_S=8 bash "$0" --case-dir "$C" --timeout 60 \
           --ranks 1 --solver "$GOOD" --foam-bashrc none 2>&1)"; RC=$?
    ARMEDNO=0; printf '%s' "$OUT" | grep -q 'armed=no' && ARMEDNO=1
    NOZERO=1; [ -e "$C/0/fluid/T" ] && NOZERO=0
    if [ "$RC" = "9" ] && printf '%s' "$OUT" | grep -q 'launched: false' \
       && [ "$ARMEDNO" = "1" ] && [ "$NOZERO" = "1" ]; then
        echo "  [ok ] W-NOARM child dies BEFORE arming 0/ -> armed=no, launched: false, exit 9"
        echo "        0/T never created, baseline back-dated 1 h: an absolute-time or"
        echo "        slack test would have PASSED this; the strict increase does not."
    else
        echo "  [BAD] W-NOARM exit $RC (wanted 9); armed=no seen=$ARMEDNO; 0/T absent=$NOZERO"
        printf '%s\n' "$OUT" | sed 's/^/        /' | head -6; RCALL=1
    fi

    # ---- W-INSTR: the INSTRUMENT could not run -> exit 8, NOT exit 9 --------
    E="$(mkcase winstr)"; rm -f "$E/0.orig/fluid/T"      # baseline uncapturable
    OUT="$(T26_WITNESS_DEADLINE_S=5 bash "$0" --case-dir "$E" --timeout 60 \
           --ranks 1 --solver "$GOOD" --foam-bashrc none 2>&1)"; RC=$?
    if [ "$RC" = "8" ] && printf '%s' "$OUT" | grep -q 'THE INSTRUMENT COULD NOT RUN'; then
        echo "  [ok ] W-INSTR baseline uncapturable -> exit 8 (instrument), NOT exit 9 (case)"
    else
        echo "  [BAD] W-INSTR exit $RC (wanted 8) -- an instrument failure collapsed into a case failure"
        printf '%s\n' "$OUT" | sed 's/^/        /' | head -4; RCALL=1
    fi
    echo "  [ok ] exit 8 (instrument could not run) and exit 9 (case died) are DISTINCT,"
    echo "        the same discipline that keeps BROKEN_GUARD_RC_n out of REFUSED."

    # NEGATIVE CONTROL on the witness itself: the setsid/timeout PARENT is alive
    # in BOTH arms, so a launcher that witnessed the parent would pass W-DEAD too.
    # W-DEAD failing is therefore attributable to the SOLVER witness and nothing else.
    echo "  [ok ] NEGATIVE CONTROL: the setsid/timeout parent was alive in both arms;"
    echo "        only the SOLVER-side witness separates them, which is the rule."
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

# ==========================================================================
# DETACH, THEN WITNESS.  A FORK RETURNING IS NOT A LAUNCH.
#
# THE DEFECT THIS CLOSES.  The previous form backgrounded `setsid "$0"
# --no-detach` and, on the very next line, printed "launched $CASE detached"
# and exited 0 -- on THE FORK SUCCEEDING, with no witness that the solver ever
# started.  `scripts/case_protocol_stage4_run.py` wrote `launched: true` on a
# Popen return alone after dying under `set -u` at the bashrc source, and
# cfd's first --go produced a FALSE LAUNCH RECORD with 0/T untouched.
#
# This launcher's blast radius was smaller -- nothing persists `launched:
# true`, and STATUS.<case> is written only AFTER the solver returns, via
# tmp+mv -- so no false GRADED artifact could result.  But the printed claim
# was unwitnessed, and a child that dies instantly (bashrc failure in the
# child's environment, unresolvable solver, missing `timeout` binary) left the
# parent having already said "launched" and exited 0.
#
# VERIFICATION'S RULE, applied: a launch is asserted ONLY from the SOLVER's own
# pid being alive -- NEVER the setsid/timeout parent, which is alive whatever
# the child did -- or from a FIRST ARTIFACT THE SOLVER PRODUCED.
#
# Witnesses polled here, strongest first:
#   W1  log.solve exists and is NON-EMPTY  -- the solver wrote output. This is
#       the solver's own artifact and is the strongest available.
#   W2  a process whose /proc/<pid>/cwd is this case AND whose exe basename is
#       the solver -- the solver itself alive, resolved by exe, never by the
#       setsid or timeout parent.
#   W3  0/fluid/T exists -- the CHILD reached the arming step. This is a
#       WEAKER witness: it proves the child lives, NOT that the solver
#       started, so it does NOT satisfy the deadline on its own. It is
#       reported because it distinguishes "child died at the bashrc" from
#       "child alive, solver slow to write".
#
# On NO W1/W2 inside the deadline: print `launched: false` with the reason and
# the state PENDING, and exit 3 -- never a silent exit 0. An unwitnessed
# launch is not a launch, and the level set must not proceed past one.
# ==========================================================================
# EXIT CODES FOR THE WITNESS, kept DISTINCT on purpose (the same discipline
# that keeps BROKEN_GUARD_RC_n from collapsing into REFUSED):
#   8  THE INSTRUMENT COULD NOT RUN -- the fork failed, or the baseline could
#      not be captured, so the witness was never EVALUATED. This is a finding
#      about the instrument.
#   9  THE CASE DIED -- the witness machinery worked and reports that no solver
#      was started. This is a finding about the case.
# Collapsing these into one non-zero would hide a dead instrument behind a
# dead case, which is how mark_done_k2bU3R3.py stayed invisible.
EXIT_WITNESS_INSTRUMENT=8
EXIT_WITNESS_CASE_DIED=9
witness_deadline_s="${T26_WITNESS_DEADLINE_S:-120}"
# Bounds the PRE-SOLVER work only: clause 7, the field checks, and checkMesh
# -allRegions -allGeometry -allTopology over four regions, which at L3's
# 2.99M cells is minutes, not seconds. Generous on purpose -- the child dying
# is detected immediately and does not wait for this cap.
prestart_cap_s="${T26_PRESTART_CAP_S:-1800}"

solver_pid_in_case() {   # echo the SOLVER's pid, never the setsid/timeout parent
    for pd in /proc/[0-9]*; do
        q="${pd#/proc/}"
        [ "$(readlink "$pd/cwd" 2>/dev/null)" = "$CASE_DIR" ] || continue
        exe="$(basename "$(readlink "$pd/exe" 2>/dev/null || echo '')")"
        case "$exe" in
            "$(basename "$SOLVER")"|mpirun|orterun) [ "$exe" = "mpirun" ] || [ "$exe" = "orterun" ] || { echo "$q"; return 0; } ;;
        esac
    done
    return 1
}

if [ "$DETACH" = "1" ] && [ "${T26_DETACHED:-}" != "1" ]; then
    # BEFORE-LAUNCH CAPTURE of the age-guard datum's baseline. 0/ cannot exist
    # here (clause 7 refuses it), so the baseline is the STAGED 0.orig/fluid/T,
    # which launch arms 0/ from and then touches LAST. A strict increase over
    # this captured value is therefore a real event, not a clock reading.
    ORIG_T_MTIME="$(stat -c %Y "$CASE_DIR/0.orig/fluid/T" 2>/dev/null || echo '')"
    if [ -z "$ORIG_T_MTIME" ]; then
        echo "launched: false" >&2; echo "state: PENDING" >&2
        echo "reason: THE INSTRUMENT COULD NOT RUN -- could not capture the baseline mtime of 0.orig/fluid/T, so the W3 witness cannot be evaluated at all. Nothing was forked." >&2
        exit "$EXIT_WITNESS_INSTRUMENT"
    fi
    T26_DETACHED=1 setsid "$0" --case-dir "$CASE_DIR" --timeout "$TIMEOUT_S" \
        --ranks "$RANKS" --solver "$SOLVER" --foam-bashrc "$FOAM_BASHRC" \
        --no-detach </dev/null >>"$CASE_DIR/log.launch" 2>&1 &
    FORK_PID=$!
    if ! kill -0 "$FORK_PID" 2>/dev/null && [ ! -e "$CASE_DIR/log.launch" ]; then
        echo "launched: false" >&2; echo "state: PENDING" >&2
        echo "reason: THE INSTRUMENT COULD NOT RUN -- the fork did not produce a live child and no log.launch appeared. The witness was never evaluated. This is a finding about the launcher, not about the case." >&2
        exit "$EXIT_WITNESS_INSTRUMENT"
    fi
    # THE DEADLINE RUNS FROM `SOLVER_STARTING`, NOT FROM THE FORK.
    # `prestart_cap_s` bounds the pre-solver work (guard + checkMesh over four
    # regions); `witness_deadline_s` bounds only the interval in which a solver
    # that HAS been started must show itself. Conflating the two is what made
    # my first draft report a healthy launch as a dead case under load.
    W=""; WPID=""; ARMED=no; ARMED_MTIME=""; i=0; waited=0; STARTED_AT=""
    while :; do
        if [ -s "$CASE_DIR/log.solve" ]; then W="W1 log.solve is non-empty -- the solver wrote output"; break; fi
        if WPID="$(solver_pid_in_case)"; then W="W2 solver pid $WPID alive, cwd $CASE_DIR, resolved BY EXE -- never the setsid/timeout parent"; break; fi
        [ -f "$CASE_DIR/SOLVER_STARTING" ] && [ -z "$STARTED_AT" ] && STARTED_AT="$(cat "$CASE_DIR/SOLVER_STARTING" 2>/dev/null || echo "")"
        # THE CHILD DYING IS DEFINITIVE AND DOES NOT WAIT FOR A TIMER.
        if ! kill -0 "$FORK_PID" 2>/dev/null; then
            if [ -e "$STATUS" ]; then
                # W4: the child completed and wrote STATUS faster than the poll.
                # A SOLVER DID RUN. `launched` MEANS "A SOLVER WAS STARTED",
                # AND NOTHING ELSE -- cfd's committed rule (7d7fcebf). An early
                # crash is `launched: true` WITH its rc, never `launched:
                # false`: collapsing a crash into "not launched" would hide a
                # real finding about the case behind a launch failure, which is
                # the same conflation as BROKEN_GUARD_RC_n inside REFUSED.
                src="$(sed -n 's/^rc=\([-0-9]*\)$/\1/p' "$STATUS" | head -1)"
                echo "launched: true"
                echo "witness: W4 the child completed and wrote $STATUS -- a solver ran"
                if [ "${src:-0}" = "0" ]; then
                    echo "state: FINISHED CLEAN (rc=0)"
                else
                    echo "state: FINISHED WITH CRASH (rc=${src:-unrecorded})"
                    echo "NOTE: this is a CRASH FINDING about the case, and it is a"
                    echo "      finding until triage says otherwise. It is NOT a launch"
                    echo "      failure -- a solver was started, so launched is true."
                fi
                exit 0
            fi
            echo "  child exited with no witness and no STATUS -- definitive, not a timeout" >&2
            break
        fi
        if [ -n "$STARTED_AT" ]; then
            i=$((i + 1)); [ "$i" -ge "$witness_deadline_s" ] && break
        else
            waited=$((waited + 1))
            if [ "$waited" -ge "$prestart_cap_s" ]; then
                echo "  no SOLVER_STARTING marker within ${prestart_cap_s}s of pre-solver work" >&2
                break
            fi
        fi
        # W3, the age-guard datum. STRICT INCREASE against a BEFORE-LAUNCH
        # CAPTURE -- never an absolute-time comparison and never a slack window.
        # cfd's `mtime >= t_launch - 1.0` CONFIRMED A LAUNCH WHERE NO SOLVER EVER
        # STARTED; a branch test caught what two code reads missed. W3 is
        # recorded as EVIDENCE and, deliberately, DOES NOT SATISFY THE DEADLINE
        # ON ITS OWN: it proves the CHILD armed 0/, not that a SOLVER started,
        # and verification's rule is that a launch is asserted only from the
        # solver's own pid or a solver-produced artifact.
        if [ -f "$CASE_DIR/0/fluid/T" ]; then
            m="$(stat -c %Y "$CASE_DIR/0/fluid/T" 2>/dev/null || echo '')"
            if [ -n "$m" ] && [ -n "$ORIG_T_MTIME" ] && [ "$m" -gt "$ORIG_T_MTIME" ]; then
                ARMED=yes; ARMED_MTIME="$m"
            fi
        fi
        sleep 1; i=$((i + 1))
    done
    echo "witness evidence (auditable, not asserted):"
    echo "  0.orig/fluid/T mtime captured BEFORE the fork : ${ORIG_T_MTIME:-UNCAPTURED}"
    echo "  0/fluid/T mtime observed AFTER the fork       : ${ARMED_MTIME:-none}"
    echo "  strict increase required (never >=, no slack) : armed=$ARMED"
    echo "  log.solve non-empty (W1)                      : $([ -s "$CASE_DIR/log.solve" ] && echo yes || echo no)"
    echo "  solver pid by exe (W2)                        : ${WPID:-none}"
    echo "  SOLVER_STARTING marker (deadline origin)      : ${STARTED_AT:-NOT REACHED}"
    echo "  child (setsid pid $FORK_PID) still alive        : $(kill -0 "$FORK_PID" 2>/dev/null && echo yes || echo no)"
    if [ -z "$W" ]; then
        echo "launched: false" >&2
        echo "state: PENDING" >&2
        echo "reason: THE CASE DIED -- no SOLVER witness (deadline ${witness_deadline_s}s after SOLVER_STARTING, pre-solver cap ${prestart_cap_s}s; marker seen: ${STARTED_AT:-NO}). The fork returned (setsid pid $FORK_PID) but A FORK RETURNING IS NOT A LAUNCH, and the setsid/timeout parent is alive whatever the child did. Child armed 0/fluid/T: $ARMED." >&2
        if [ "$ARMED" = "no" ]; then
            echo "hint: the child died BEFORE arming 0/ -- read $CASE_DIR/log.launch for a bashrc or solver-resolution failure. A `set -u` bashrc source exits 127 with NO output." >&2
        else
            echo "hint: the child DID arm 0/ (mtime $ARMED_MTIME strictly above the captured $ORIG_T_MTIME) but no solver was ever witnessed -- it died between arming and the solver." >&2
        fi
        echo "An unwitnessed launch is not a launch; the level set must not proceed." >&2
        exit "$EXIT_WITNESS_CASE_DIED"
    fi
    echo "launched: true"
    echo "witness: $W"
    echo "state: RUNNING -- STATUS will appear at $STATUS"
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
SOLVER_PATH=""
if [ "$DRYRUN" = "0" ]; then
    if [ "$FOAM_BASHRC" != "none" ]; then
        [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
        # `set +u` around the source is NOT cosmetic. MEASURED on this box:
        # `set -u; . etc/bashrc` exits rc=127 with NO output and nothing after
        # it runs -- the wrapper's own refusal never gets to speak. K0f hit it
        # seven times (launch_t4e.sh:112) and this lane reproduced it again
        # 2026-09-10 in a throwaway script written an hour after reading the
        # warning. DO NOT REMOVE OR REORDER.
        set +u
        # shellcheck disable=SC1090
        . "$FOAM_BASHRC" >/dev/null 2>&1 || true
        set -u
    fi
    SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
    [ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' is NOT RESOLVABLE (foam-bashrc=$FOAM_BASHRC). Nothing ran, no STATUS written." >&2; exit 2; }
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

# --- checkMesh, WITH ITS FULL CHECK SET, recorded rather than assumed -------
# -allGeometry and -allTopology ARE NOT OPTIONAL. Bare `checkMesh` prints
# `Mesh OK.` on a mesh that FAILS checks which only run under those flags.
# MEASURED ON T26's OWN PROBE MESH, 2026-09-10, same mesh and same binary:
#     checkMesh                              -> "Mesh OK."
#     checkMesh -allGeometry -allTopology    -> "Failed 2 mesh checks."
#                                               2,320 small-determinant cells
#                                              13,099 concave cells
# cfd spent three M6CP1 smoke rungs on a mesh its stage-2 gate could never have
# refused, and the M6 flow verdict is NOT A RESULT on a trailing-edge cusp.
# The binary's own help on this box: -allGeometry "Include bounding box
# checks", -allTopology "Include extra topology checks".
# -allRegions is kept: T26 is four-region CHT and every region is graded.
CHECKMESH_CMD="checkMesh -case $CASE_DIR -allRegions -allGeometry -allTopology"
# The command line is recorded INTO the log, so a reader can tell which check
# set produced it. analyse_t26.py REFUSES a log that does not carry both flags:
# the artifact must prove which instrument produced it.
# NOT prefixed `//`: analyse_t26.py strips OpenFOAM comments before matching
# (so a commented-out directions line cannot be read as live), and a `//`
# prefix here would have made the provenance line invisible to the very reader
# that must check it. Caught before the freeze; the reader also reads RAW for
# this one line, so the two defences are independent.
echo "CHECKMESH COMMAND LINE: $CHECKMESH_CMD" > "$CASE_DIR/log.checkMesh"
$CHECKMESH_CMD >> "$CASE_DIR/log.checkMesh" 2>&1
CHECKMESH_RC=$?

# --- arm 0/ from 0.orig; 0/fluid/T touched LAST (the age-guard datum) -------
cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/ from 0.orig" >&2; exit 2; }
sleep 1
touch "$CASE_DIR/0/fluid/T" || { echo "REFUSE: could not touch 0/fluid/T -- the age guard would have no referent" >&2; exit 2; }

# --- SOLVER_STARTING: the marker the PARENT's witness deadline runs from ----
# Everything above -- the clause-7 guard, the field checks, checkMesh with its
# full check set over four regions -- happens BEFORE any solver exists. On a
# real T26 level that is MINUTES, and a witness deadline measured from the FORK
# would call a perfectly healthy launch "the case died". This marker separates
# "still doing pre-solver work" from "the solver should exist by now", so the
# deadline measures the right interval.
date +%s > "$CASE_DIR/SOLVER_STARTING"

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
