#!/usr/bin/env bash
# ==========================================================================
# K0f EXTENSION LAUNCHER (ext1) -- the ONE registered +20 000-iteration
# continuation of K0f section 7.1, exercised on the frozen instrument's own
# terms.  rc-CAPTURING, DETACHED, QUEUE-COMPATIBLE.  Registered by K0f
# AMENDMENT 3 (2026-08-26, POST-compute, disclosure only: no gate, band,
# threshold, floor, control or label moves; the rung CEILING 2 750.70 binds).
#
# Modelled on scripts/launch_k0f.sh (its header records the measured trap:
# `setsid timeout ... ; rc=$?` writes rc=0 for a crashed solver because setsid
# forks) and on T3_runs/run_one_t3_ext1.sh (copy-edit + grep post-check on
# every controlDict edit).  The caller starts this file and returns; it
# re-execs itself ONCE under setsid; inside the detached copy the solver runs
# under `timeout` in the FOREGROUND, so $? is genuinely the solver's status.
#
# THE FORM IS THE FROZEN INSTRUMENT'S, NOT THIS FILE'S.  scripts/mark_done_k0f.py
# (frozen blob f01e3fce, section 7.7) already carries the extension clauses:
#   - the extension's rc is read from  <root>/STATUS.<case>.ext1
#   - its log is                       <case>/log.solve.ext1
#   - a                                <root>/STATUS.<case>.ext2  FAILS the case
#   - clause 3: last written time == controlDict endTime + 20000 -- so the
#     controlDict must READ 40000 AGAIN after the run; this file snapshots it,
#     edits a copy (startFrom latestTime; endTime 60000), and RESTORES the
#     snapshot byte-for-byte after the solver returns, cmp-checked;
#   - clause 5: ExecutionTime lines over BOTH logs == 60000, and the first
#     `Time =` of the extension == 40001 (a restart from latestTime 40000);
#   - clause 6: every field at 60000 NEWER than 0/T AND than STATUS.<case>.
# Therefore: 0/ IS NEVER TOUCHED, STATUS.<case> IS NEVER TOUCHED, log.solve IS
# NEVER TOUCHED.  The 40000 checkpoint is the RESTART SOURCE; the age-guard
# datums are the frozen clause's (0/T, STATUS.<case>).
#
# G2 is LINEAGE-AWARE from birth (T10aR2 9fa66065 / T4b 51618879 / T3 R_ff
# ba023a53): the queue runner's `bash -c 'cd <cwd>; ...'` wrapper shell is this
# launcher's own ancestor; any FOREIGN process in the case directory is refused.
# The queue entry's cwd is NOT the case directory (the validator refuses a cwd
# holding time directories): it is <root>/ext/<case>/, holding only the runner's
# own records; --case-dir names the real case.
# ==========================================================================
set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REG_EXTENSION=20000; REG_END=40000; NEW_END=$((REG_END + REG_EXTENSION))

usage() { cat >&2 <<'U'
usage: launch_k0f_ext1.sh --case-dir DIR --timeout SECONDS [--ranks 1] [--solver NAME]
                          [--foam-bashrc PATH|none] [--no-detach]
  --case-dir  the K0f case directory (holds 40000/); STATUS.<case>.ext1 is written to its PARENT
  --timeout   the case's registered EXTENSION cap, converted: cap_core_min x 60 / ranks
  --ranks     must be 1 (K0f is registered SERIAL)
  --no-detach run in the foreground (drive arms)
U
exit 2; }
CASE_DIR=""; TIMEOUT_S=""; RANKS=1; SOLVER=buoyantBoussinesqSimpleFoam; DETACH=1
FOAM_BASHRC=/usr/lib/openfoam/openfoam2606/etc/bashrc
while [ $# -gt 0 ]; do case "$1" in
  --case-dir) CASE_DIR="${2:-}"; shift 2;; --timeout) TIMEOUT_S="${2:-}"; shift 2;;
  --ranks) RANKS="${2:-}"; shift 2;; --solver) SOLVER="${2:-}"; shift 2;;
  --foam-bashrc) FOAM_BASHRC="${2:-}"; shift 2;; --no-detach) DETACH=0; shift;; *) usage;; esac; done
[ -n "$CASE_DIR" ] && [ -n "$TIMEOUT_S" ] || usage
[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
case "$TIMEOUT_S" in ''|*[!0-9]*) echo "REFUSE: --timeout must be integer seconds" >&2; exit 2;; esac
[ "$RANKS" = "1" ] || { echo "REFUSE: K0f is registered SERIAL (section 6); --ranks=$RANKS" >&2; exit 2; }
CASE_DIR="$(cd "$CASE_DIR" && pwd)"; ROOT="$(dirname "$CASE_DIR")"; CASE="$(basename "$CASE_DIR")"
STATUS1="$ROOT/STATUS.$CASE"; STATUS="$ROOT/STATUS.$CASE.ext1"; CD="$CASE_DIR/system/controlDict"

# --- guards, BEFORE detaching and before anything is written ---------------
[ -f "$CASE_DIR/log.solve" ] || { echo "REFUSE: no log.solve -- there is no first segment to extend" >&2; exit 2; }
[ -f "$STATUS1" ] || { echo "REFUSE: no $STATUS1 -- the first segment never finished; an extension needs a finished segment" >&2; exit 2; }
grep -Eq '(^|[[:space:]])rc=0([[:space:]]|$)' "$STATUS1" || { echo "REFUSE: $STATUS1 does not report rc=0; a failed first segment is not extended" >&2; exit 2; }
[ -e "$STATUS" ] && { echo "REFUSE: $STATUS exists -- the ONE registered extension has already run (section 7.1: a second is not authorised)" >&2; exit 2; }
[ -e "$ROOT/STATUS.$CASE.ext2" ] && { echo "REFUSE: STATUS.$CASE.ext2 exists -- no second extension is authorised" >&2; exit 2; }
[ -e "$CASE_DIR/log.solve.ext1" ] && { echo "REFUSE: log.solve.ext1 exists -- an extension has already started" >&2; exit 2; }
[ -d "$CASE_DIR/$REG_END" ] || { echo "REFUSE: no $REG_END/ checkpoint -- nothing to restart from" >&2; exit 2; }
[ -f "$CASE_DIR/0/T" ] || { echo "REFUSE: no 0/T -- the age guard has no datum" >&2; exit 2; }
[ -f "$CD" ] || { echo "REFUSE: no system/controlDict" >&2; exit 2; }
grep -Eq "^[[:space:]]*endTime[[:space:]]+$REG_END[[:space:]]*;" "$CD" || { echo "REFUSE: controlDict endTime is not the registered $REG_END (a previous edit was not restored?)" >&2; exit 2; }
grep -Eq '^[[:space:]]*stopAt[[:space:]]+endTime[[:space:]]*;' "$CD" || { echo "REFUSE: controlDict stopAt is not endTime" >&2; exit 2; }
while IFS= read -r d; do [ -n "$d" ] && { t="$(basename "$d")"; awk -v t="$t" -v e="$REG_END" 'BEGIN{exit !(t+0>e)}' && { echo "REFUSE: time directory $t beyond $REG_END already exists" >&2; exit 2; }; }; done \
  < <(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?' 2>/dev/null)
# G2, lineage-aware (own pid, ancestors to pid 1, descendants excluded; any foreign process refused by pid)
ppid_of() { sed 's/.*) //' "/proc/$1/stat" 2>/dev/null | awk '{print $2}'; }
LINEAGE=" $$ "; a="$PPID"
while [ -n "$a" ] && [ "$a" != "0" ] && [ "$a" != "1" ]; do LINEAGE="$LINEAGE$a "; a="$(ppid_of "$a")"; done
own_lineage() {
    case "$LINEAGE" in *" $1 "*) return 0;; esac
    a="$1"
    while [ -n "$a" ] && [ "$a" != "0" ] && [ "$a" != "1" ]; do
        [ "$a" = "$$" ] && return 0
        a="$(ppid_of "$a")"
    done
    return 1
}
for p in /proc/[0-9]*; do
    q="${p#/proc/}"
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CASE_DIR" ] || continue
    own_lineage "$q" && continue
    echo "REFUSE: G2: pid $q already running in $CASE" >&2; exit 2
done

if [ "$DETACH" = "1" ] && [ "${K0FEXT_DETACHED:-}" != "1" ]; then
    K0FEXT_DETACHED=1 exec setsid "$0" --case-dir "$CASE_DIR" --timeout "$TIMEOUT_S" --ranks "$RANKS" \
        --solver "$SOLVER" --foam-bashrc "$FOAM_BASHRC" --no-detach </dev/null >>"$CASE_DIR/log.launch.ext1" 2>&1 &
    echo "launched $CASE ext1 detached; STATUS will appear at $STATUS"; exit 0
fi

write_status() {  # rc wall note restored
    tmp="$STATUS.tmp.$$"
    printf 'rc=%s wall=%s checkMesh_rc=na timeout_s=%s ranks=%s solver=%s solver_path=%s case=%s note=%s segment=ext1 restart_from=%s endTime_ext=%s controldict_restored=%s started_utc=%s ended_utc=%s\n' \
        "$1" "$2" "$TIMEOUT_S" "$RANKS" "$SOLVER" "${SOLVER_PATH:-unresolved}" "$CASE" "$3" "$REG_END" "$NEW_END" "$4" \
        "$(date -u -d "@${T0:-0}" +%Y-%m-%dT%H:%M:%SZ)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$tmp"
    mv -f "$tmp" "$STATUS"
}

# --- environment; the solver must resolve BEFORE anything is edited --------
if [ "$FOAM_BASHRC" != "none" ]; then
    [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
    set +u; . "$FOAM_BASHRC" >/dev/null 2>&1 || true; set -u
fi
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' is NOT RESOLVABLE; nothing ran, no STATUS written" >&2; exit 2; }
if ! python3 "$SELF/build_k0f.py" --preflight "$CASE_DIR" >>"$CASE_DIR/log.launch.ext1" 2>&1; then
    echo "REFUSE: $CASE failed the consumer-side completeness assertion; no solver started, no STATUS written" >&2; exit 2; fi

# --- controlDict: snapshot, copy-edit, post-check after EACH edit -----------
cp -p "$CD" "$CD.pre_ext1" || { echo "REFUSE: could not snapshot controlDict" >&2; exit 2; }
sed -E 's|^([[:space:]]*startFrom[[:space:]]+).*;|\1latestTime;|' "$CD" > "$CD.tmp" && mv "$CD.tmp" "$CD" || { echo "REFUSE: startFrom edit failed" >&2; exit 2; }
grep -Eq '^[[:space:]]*startFrom[[:space:]]+latestTime[[:space:]]*;' "$CD" || { cp -p "$CD.pre_ext1" "$CD"; echo "REFUSE: POST-CHECK: startFrom is not latestTime; controlDict restored; refusing to start a solver that might restart from 0" >&2; exit 2; }
sed -E "s|^([[:space:]]*endTime[[:space:]]+)[0-9.eE+-]+;|\1$NEW_END;|" "$CD" > "$CD.tmp" && mv "$CD.tmp" "$CD" || { cp -p "$CD.pre_ext1" "$CD"; echo "REFUSE: endTime edit failed; controlDict restored" >&2; exit 2; }
grep -Eq "^[[:space:]]*endTime[[:space:]]+$NEW_END[[:space:]]*;" "$CD" || { cp -p "$CD.pre_ext1" "$CD"; echo "REFUSE: POST-CHECK: endTime is not $NEW_END; controlDict restored" >&2; exit 2; }
echo "controlDict for ext1: $(grep -E '^[[:space:]]*(startFrom|endTime|stopAt)' "$CD" | tr -s ' \n' ' ')"

# --- the solver, FOREGROUND, under timeout, rc captured from it ------------
# 0/ NOT touched; STATUS.<case> NOT touched; log.solve NOT touched.
cd "$CASE_DIR" || exit 2
T0=$(date +%s)
timeout "$TIMEOUT_S" "$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.solve.ext1" 2>&1
RC=$?
T1=$(date +%s); WALL=$((T1 - T0))

# --- restore the controlDict byte-for-byte (frozen clause 3 reads endTime 40000 + 20000)
cp -p "$CD.pre_ext1" "$CD"; RESTORED=no
cmp -s "$CD.pre_ext1" "$CD" && RESTORED=yes
NOTE=clean
if [ "$RC" = "124" ]; then NOTE=CAP_EXPIRED_or_child_exit_124
elif [ "$RC" -gt 128 ] 2>/dev/null; then NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then NOTE=SOLVER_NONZERO_EXIT; fi
[ "$RESTORED" = "yes" ] || NOTE="${NOTE}_CONTROLDICT_NOT_RESTORED"
write_status "$RC" "$WALL" "$NOTE" "$RESTORED"
echo "$CASE ext1 finished: rc=$RC wall=${WALL}s note=$NOTE controldict_restored=$RESTORED -> $STATUS"
exit "$RC"
