#!/bin/bash
# DRIVAER R1 STAGE A -- launch ONE level.  Never deletes a run directory.
#
# rc IS CAPTURED INSIDE THIS WRAPPER.  `setsid timeout cmd` exits 0 for every outcome,
# so an rc read around the setsid line is meaningless.  Both `rc` and `RC.txt` are
# written: grade_drivaer.py:read_rc globs ("rc", "*.rc", "DONE*") and DOES NOT match
# "RC.txt" -- `rc` is the load-bearing one for THIS grader and RC.txt is there for the
# next reader who assumes the other convention.
ROOT="$1"; NP="${2:-8}"
[ -d "$ROOT" ] || { echo "REFUSE: no such level root $ROOT"; exit 2; }
[ -d "$ROOT/0.orig" ] || { echo "REFUSE: no 0.orig in $ROOT -- run write_solver_case.py"; exit 2; }
[ -e "$ROOT/0" ] && { echo "REFUSE: $ROOT/0 exists; a pre-existing 0/ defeats the age guard"; exit 2; }
for d in "$ROOT"/[1-9]*; do
  [ -d "$d" ] && { echo "REFUSE: time directory $d already exists"; exit 2; }
done

set +u
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
cd "$ROOT" || exit 2

# 0.orig -> 0 AT LAUNCH: 0/U is what the rule-4 age guard dates the run from, so it
# must be stamped now and not when the case was written.
cp -r 0.orig 0
touch 0/U 0/p 0/k 0/omega 0/nut

: > RUN_META.txt
{ echo "launched_utc=$(date -u +%FT%TZ)"; echo "cwd=$ROOT"; echo "ranks=$NP"
  echo "wrapper_pid=$$"; echo "host=$(hostname)"; } >> RUN_META.txt

write_rc () {   # write_rc <n>
  printf 'rc=%s\n' "$1" > "$ROOT/rc"
  printf 'rc=%s\n' "$1" > "$ROOT/RC.txt"
}

if [ "$NP" -gt 1 ]; then
  cat > system/decomposeParDict <<DPD
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $NP;
method scotch;
DPD
  nice -n 5 decomposePar -force > log.decomposePar 2>&1
  rc=$?; echo "decomposePar rc=$rc" >> RUN_META.txt
  [ $rc -ne 0 ] && { write_rc $rc; exit $rc; }
  echo "solver_started_utc=$(date -u +%FT%TZ)" >> RUN_META.txt
  nice -n 5 mpirun -np "$NP" simpleFoam -parallel > log.simpleFoam 2>&1
  rc=$?                                  # <-- captured INSIDE the wrapper
  echo "simpleFoam rc=$rc" >> RUN_META.txt
  if [ $rc -eq 0 ]; then
    # -newTimes skips time 0, which is already present.  Reconstructing 0 would stamp
    # 0/U NEWER than the endTime fields and the age guard would then refuse the run.
    nice -n 5 reconstructPar -newTimes > log.reconstructPar 2>&1
    rrc=$?; echo "reconstructPar rc=$rrc" >> RUN_META.txt
    [ $rrc -ne 0 ] && rc=$rrc
  fi
else
  echo "solver_started_utc=$(date -u +%FT%TZ)" >> RUN_META.txt
  nice -n 5 simpleFoam > log.simpleFoam 2>&1
  rc=$?
  echo "simpleFoam rc=$rc" >> RUN_META.txt
fi

echo "finished_utc=$(date -u +%FT%TZ)" >> RUN_META.txt
write_rc $rc
exit $rc
