#!/bin/bash
# CRM-M085 STAGE A detached launcher. rc is captured INSIDE this wrapper, from the
# solver process, and written to BOTH `rc` and `RC.txt` (the lab's two graders read
# different names). `setsid timeout cmd` exits 0 for every outcome including SIGFPE,
# so no launching process's exit status is consulted anywhere.
set -u
CASE="$1"; SOLVER="$2"; RANKS="$3"
LOG="$CASE/log.$SOLVER"; STATUS="$CASE/STATUS.stageA"
SRCLOG="$CASE/log.foam_bashrc_source"

# ===== CANONICAL GUARD: `set -u` + OpenFOAM's etc/bashrc. COPY THIS BLOCK. =====
# etc/bashrc dereferences WM_PROJECT_DIR while unset (its line 184); under `set -u`
# that is fatal and this wrapper would die HERE before its first write, while the
# launcher prints success. Measured twice on 2026-09-10 in two teams. Stderr KEPT.
set +u
source /usr/lib/openfoam/openfoam2606/etc/bashrc '' > "$SRCLOG" 2>&1
SRC_RC=$?
set -u
if [ "$SRC_RC" -ne 0 ]; then
    echo "91" > "$CASE/rc"; echo "RC=91" > "$CASE/RC.txt"
    echo "REFUSED=foam_bashrc_source_failed rc=$SRC_RC see $SRCLOG" > "$STATUS"; exit 91
fi
cd "$CASE" || exit 90

[ -d "$CASE/0" ] || cp -r "$CASE/0.orig" "$CASE/0"
{ echo "launched_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "ppid=$PPID"
  echo "ranks=$RANKS"; echo "solver=$SOLVER"; } > "$STATUS"

# 0/T is touched LAST, immediately before the solver. Rule 4's age guard dates the
# run by it: every field at endTime must be NEWER than this file.
touch "$CASE/0/T"
T0=$(date +%s)
if [ "$RANKS" -gt 1 ]; then
    decomposePar -case "$CASE" -force > "$CASE/log.decomposePar" 2>&1
    DRC=$?; echo "decomposePar_rc=$DRC" >> "$STATUS"
    if [ "$DRC" -ne 0 ]; then echo "$DRC" > "$CASE/rc"; echo "RC=$DRC" > "$CASE/RC.txt"; exit "$DRC"; fi
    mpirun -np "$RANKS" "$SOLVER" -case "$CASE" -parallel > "$LOG" 2>&1
    RC=$?
    [ "$RC" -eq 0 ] && { reconstructPar -case "$CASE" -latestTime > "$CASE/log.reconstructPar" 2>&1
                         echo "reconstructPar_rc=$?" >> "$STATUS"; }
else
    "$SOLVER" -case "$CASE" > "$LOG" 2>&1
    RC=$?
fi
T1=$(date +%s)
echo "$RC" > "$CASE/rc"          # grader A reads `rc`
echo "RC=$RC" > "$CASE/RC.txt"   # grader B reads `RC.txt`
{ echo "solver_rc=$RC"; echo "wall_s=$((T1-T0))"
  echo "core_min=$(echo "($T1-$T0)*$RANKS/60" | bc -l)"
  echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } >> "$STATUS"
exit "$RC"
