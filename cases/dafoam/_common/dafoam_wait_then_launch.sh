#!/usr/bin/env bash
# =============================================================================
# dafoam_wait_then_launch.sh -- WAIT-THEN-LAUNCH WRAPPER FOR THE LATER PHASES OF A
# MULTI-PHASE DAFOAM ITEM.  Generic, dafoam-owned, and deliberately small.
#
# WHY THIS FILE EXISTS.  scripts/queue_runner.py (cfd's) launches every valid entry
# in a team's drop path and evaluates NO `precondition_artifact` (0 hits at HEAD,
# measured 2026-08-26).  Three dafoam later-phase entries (D12R phase 3, D12R phase
# 4, W2R phase 2) were launched on drop on 2026-08-26 and each aborted rc=1 on its
# absent step_plan*.json -- zero stages, but a launch record for nothing.  The
# supervisor's ruling: a later-phase entry reaches the drop path only behind a
# launcher that evaluates ITS OWN precondition and applies G-ROOT.5 before any
# destructive act.  The registered phase launchers are FROZEN INSTRUMENTS (md5 in
# their pre-registrations; rule 6) and are not edited.  This wrapper sits in front
# of them, unchanged, and does exactly three things:
#
#   (a) polls (30 s, registered) for a NAMED precondition artifact until a BOUNDED
#       deadline passed on the argv, writing every wait to STATUS.<case_id> in the
#       cwd (the case directory, never the run root);
#   (b) applies G-ROOT.5 immediately before the launch: REFUSES (rc 3) if
#       `sudo -n docker ps` shows a RUNNING container whose name carries the item's
#       container-name prefix, or if a driver pidfile in the run root names a LIVE
#       pid that is not an ancestor of this process or whose /proc/<pid>/cwd is the
#       run root (a stale pidfile -- dead pid -- never blocks); also refuses a
#       second wrapper for the same case id (its own pidfile names a live pid);
#   (c) runs the registered phase launcher argv UNCHANGED as a foreground child,
#       captures its exit status INSIDE this wrapper into STATUS.<case_id>, and
#       labels it as the LAUNCHER'S exit -- never the solver rc (L-342, d4d0c29d:
#       a bookkeeping failure invalidates the bookkeeping, never the physics).
#       At the deadline with the artifact still absent it REFUSES-AND-BLOCKS
#       (rc 6) with the wait series on record.  Nothing is launched at rc 6.
#
# WHAT IT NEVER DOES.  It does not choose a step, read a plan, compute a gate,
# apply a threshold, edit a launcher, remove a directory, kill a process or
# delete a file.  It carries no `assert` (L-332): every refusal is an `exit`.
# `scripts/queue_runner.py` overwrites STATUS.<case_id> with its own one
# `launcher_rc=` line when this wrapper exits (`>` at launch(), measured); the
# wrapper's full series therefore ALSO lands, identically, in
# WRAPPER.<case_id>.log beside it, which the runner never touches.
#
# EXIT CODES.  64 usage; 3 G-ROOT.5 refusal (nothing launched); 6 BLOCKED at the
# deadline (nothing launched); otherwise the registered launcher's own exit
# status, passed through and labelled.  Permission for detached launches:
# bc0e687e (Sanaa, boarded verbatim).
#
# USAGE
#   bash dafoam_wait_then_launch.sh --case-id <ID> --precondition <PATH> \
#        --prefix <CONTAINER_NAME_PREFIX> --run-root <DIR> --deadline-s <N> \
#        [--driver-pidfile <NAME>] [--poll-s <S>] -- <launcher argv...>
# =============================================================================
set -uo pipefail
PERMISSION=bc0e687e
WRAPPER_NAME="dafoam_wait_then_launch.sh"

CASE_ID=""; PRECOND=""; PREFIX=""; RUN_ROOT=""; DEADLINE_S=""; DRIVER_PIDFILE="driver.pid"; POLL_S=30
usage () {
  echo "usage: $WRAPPER_NAME --case-id ID --precondition PATH --prefix CONTAINER_PREFIX --run-root DIR --deadline-s N [--driver-pidfile NAME] [--poll-s S] -- <launcher argv...>" >&2
  exit 64
}
while [ $# -gt 0 ]; do
  case "$1" in
    --case-id)        CASE_ID="$2"; shift 2;;
    --precondition)   PRECOND="$2"; shift 2;;
    --prefix)         PREFIX="$2"; shift 2;;
    --run-root)       RUN_ROOT="$2"; shift 2;;
    --deadline-s)     DEADLINE_S="$2"; shift 2;;
    --driver-pidfile) DRIVER_PIDFILE="$2"; shift 2;;
    --poll-s)         POLL_S="$2"; shift 2;;
    --)               shift; break;;
    *)                usage;;
  esac
done
[ -n "$CASE_ID" ] && [ -n "$PRECOND" ] && [ -n "$PREFIX" ] && [ -n "$RUN_ROOT" ] && [ -n "$DEADLINE_S" ] || usage
[ $# -ge 1 ] || usage
case "$DEADLINE_S" in ''|*[!0-9]*) usage;; esac
case "$POLL_S" in ''|*[!0-9]*) usage;; esac
[ "$POLL_S" -ge 1 ] || usage
case "$PRECOND" in /*) ;; *) echo "ABORT: --precondition must be an absolute path: $PRECOND" >&2; exit 64;; esac
case "$RUN_ROOT" in /*) ;; *) echo "ABORT: --run-root must be an absolute path: $RUN_ROOT" >&2; exit 64;; esac

CWD="$(pwd)"
STATUS="$CWD/STATUS.$CASE_ID"
WLOG="$CWD/WRAPPER.$CASE_ID.log"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)_$$"
utc () { date -u +%Y-%m-%dT%H:%M:%SZ; }
rec () {
  # one line, appended to BOTH records; the runner's final `>` overwrite of STATUS
  # never reaches WRAPPER.<case_id>.log.
  local line="stamp=$(utc) wrapper=$WRAPPER_NAME case=$CASE_ID $*"
  echo "$line" >> "$STATUS"; echo "$line" >> "$WLOG"; echo "$line"
}

ARGV_STR=""
for a in "$@"; do ARGV_STR="$ARGV_STR '$a'"; done
SID=$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ')
rec "event=START pid=$$ sid=${SID:-?} ppid=$PPID cwd=$CWD precondition=$PRECOND prefix=$PREFIX run_root=$RUN_ROOT deadline_s=$DEADLINE_S poll_s=$POLL_S driver_pidfile=$DRIVER_PIDFILE launcher_argv=[$ARGV_STR ] permission=$PERMISSION"

# ---- a second wrapper for the same case id is refused at START (two records for
# ---- one run is the defect).  The wrapper's own pidfile lives in the run root when
# ---- the run root exists (later phases continue a run that exists); otherwise the
# ---- check is recorded as not applicable rather than silently skipped.
OWN_PIDFILE="$RUN_ROOT/$CASE_ID.wrapper.pid"
if [ -d "$RUN_ROOT" ]; then
  if [ -f "$OWN_PIDFILE" ]; then
    OPID=$(tr -dc '0-9' < "$OWN_PIDFILE" | head -c 12)
    if [ -n "$OPID" ] && [ "$OPID" != "$$" ] && kill -0 "$OPID" 2>/dev/null; then
      rec "rc=3 event=DUPLICATE_WRAPPER_REFUSED own_pidfile=$OWN_PIDFILE live_pid=$OPID note=a-wrapper-for-this-case-is-already-live-NOTHING-LAUNCHED"
      exit 3
    fi
  fi
  echo "$$" > "$OWN_PIDFILE"
  trap 'rm -f "$OWN_PIDFILE"' EXIT
  rec "event=OWN_PIDFILE_WRITTEN file=$OWN_PIDFILE"
else
  rec "event=OWN_PIDFILE_NOT_APPLICABLE reason=run-root-absent-at-start run_root=$RUN_ROOT"
fi

# ---- (a) the bounded wait ---------------------------------------------------------
WAITED=0; N=0
while [ ! -e "$PRECOND" ]; do
  if [ "$WAITED" -ge "$DEADLINE_S" ]; then
    rec "rc=6 event=BLOCKED_AT_BOUND waited_s=$WAITED waits=$N deadline_s=$DEADLINE_S precondition=$PRECOND note=precondition-absent-at-the-registered-bound-NOTHING-LAUNCHED verdict=BLOCKED"
    exit 6
  fi
  N=$((N+1))
  rec "event=WAIT n=$N waited_s=$WAITED present=no precondition=$PRECOND"
  sleep "$POLL_S"; WAITED=$((WAITED+POLL_S))
done
PMD5=$(md5sum "$PRECOND" 2>/dev/null | cut -d' ' -f1)
rec "event=PRECONDITION_PRESENT waited_s=$WAITED waits=$N precondition=$PRECOND md5=${PMD5:-unreadable} size=$(stat -c %s "$PRECOND" 2>/dev/null || echo ?)"

# ---- (b) G-ROOT.5, immediately before the launch ------------------------------------
LIVE=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -F -- "$PREFIX" | grep -- "^$PREFIX" | head -5 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE" ]; then
  rec "rc=3 event=GROOT5_REFUSED clause=a live_containers_with_prefix=[$LIVE] prefix=$PREFIX note=a-RUNNING-container-carries-this-item-prefix-NOTHING-LAUNCHED"
  exit 3
fi
DPF="$RUN_ROOT/$DRIVER_PIDFILE"; DPF_STATE="absent"
if [ -f "$DPF" ]; then
  DPID=$(tr -dc '0-9' < "$DPF" | head -c 12)
  if [ -n "$DPID" ] && kill -0 "$DPID" 2>/dev/null; then
    ANCESTOR=no; p=$$
    for _ in $(seq 1 64); do
      if [ "$p" = "$DPID" ]; then ANCESTOR=yes; break; fi
      p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
      if [ -z "$p" ] || [ "$p" = "0" ]; then break; fi
    done
    DCWD=$(readlink -f "/proc/$DPID/cwd" 2>/dev/null)
    if [ "$ANCESTOR" = "no" ] || [ "$DCWD" = "$(realpath -m "$RUN_ROOT")" ]; then
      rec "rc=3 event=GROOT5_REFUSED clause=b driver_pidfile=$DPF live_pid=$DPID ancestor_of_this_wrapper=$ANCESTOR pid_cwd=$DCWD note=a-live-driver-holds-this-run-root-NOTHING-LAUNCHED"
      exit 3
    fi
    DPF_STATE="present_live_owner_is_ancestor_cwd_not_run_root"
  else
    DPF_STATE="present_stale_dead_pid_${DPID:-empty}_does_not_block"
  fi
fi
rec "event=GROOT5_PASS live_containers_with_prefix=none driver_pidfile=$DPF state=$DPF_STATE"

# ---- (c) the registered launcher, UNCHANGED, rc captured HERE -----------------------
OUT="$CWD/LAUNCH.$CASE_ID.$STAMP.out"
T0=$(date +%s)
rec "event=LAUNCH begin=$(utc) out=$OUT argv=[$ARGV_STR ]"
"$@" > "$OUT" 2>&1
LRC=$?
T1=$(date +%s)
rec "rc=$LRC event=LAUNCHER_EXIT wall_s=$((T1-T0)) out=$OUT note=exit-status-of-the-registered-launcher-NOT-the-solver-rc-L-342 permission=$PERMISSION"
exit "$LRC"
