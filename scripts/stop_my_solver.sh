#!/usr/bin/env bash
# stop_my_solver.sh RUNDIR [SIGNAL]
#
# Stop ONLY the solver ranks belonging to one run directory.
#
# WHY THIS EXISTS. On 2026-09-12 the CRM wing-body lane stopped its own diagnostics with
#     pkill -f "rhoSimpleFoam -parallel"
# and killed the M6I lane's graded run twice -- 23:18Z and 23:31:39Z -- because
# launch_m6i_v2.sh runs `mpirun -np N rhoSimpleFoam -parallel` and every one of its ranks
# carries that exact command line. The victim died with rc=1, EMPTY stderr, no signal string,
# healthy physics and no memory pressure: an external SIGTERM to mpirun leaves no trace inside
# the case, so the lane that owns it cannot diagnose it from its own logs.
#
# `ps` TELLS YOU WHAT, NEVER WHOSE. A process name, a binary, a command-line pattern and an RSS
# ranking are all properties of the WORKLOAD; none of them identifies the OWNER. The only thing
# on this box that says whose a solver is, is where it is running: /proc/<pid>/cwd.
#
# It also refuses to match its own shell -- a pattern broad enough to match its invoker is broad
# enough to match a stranger's solver, and that self-match is the tell, not a quirk.
set -o pipefail
RUNDIR="${1:?usage: stop_my_solver.sh RUNDIR [SIGNAL]}"
SIG="${2:-TERM}"
RUNDIR="$(readlink -f "$RUNDIR")" || { echo "REFUSE: cannot resolve $1"; exit 64; }
[ -d "$RUNDIR" ] || { echo "REFUSE: $RUNDIR is not a directory"; exit 64; }
SELF=$$

# Identify by cwd, re-read immediately before signalling. A pid may be recycled between a
# listing and a kill, so the cwd is confirmed again inside the signal loop.
mapfile -t CANDIDATES < <(ls /proc 2>/dev/null | grep -E '^[0-9]+$')
PIDS=()
for p in "${CANDIDATES[@]}"; do
  [ "$p" = "$SELF" ] && continue
  cwd="$(readlink /proc/$p/cwd 2>/dev/null)" || continue
  case "$cwd" in
    "$RUNDIR"|"$RUNDIR"/*) ;;
    *) continue ;;
  esac
  exe="$(readlink /proc/$p/exe 2>/dev/null)"
  case "$exe" in *Foam*|*foam*) PIDS+=("$p") ;; esac
done

if [ "${#PIDS[@]}" -eq 0 ]; then
  echo "no solver process has cwd under $RUNDIR -- nothing to stop"; exit 0
fi

echo "solver ranks owned by $RUNDIR:"
for p in "${PIDS[@]}"; do
  printf "  pid %-8s exe=%s\n" "$p" "$(readlink /proc/$p/exe 2>/dev/null)"
done

for p in "${PIDS[@]}"; do
  # RE-CONFIRM ownership at the instant of the signal: the pid may have been recycled.
  cwd="$(readlink /proc/$p/cwd 2>/dev/null)" || { echo "  pid $p vanished, skipped"; continue; }
  case "$cwd" in
    "$RUNDIR"|"$RUNDIR"/*) kill -"$SIG" "$p" 2>/dev/null && echo "  signalled $SIG -> $p" ;;
    *) echo "  pid $p CHANGED OWNER between check and signal (cwd=$cwd) -- NOT signalled" ;;
  esac
done
