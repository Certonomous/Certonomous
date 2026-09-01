#!/bin/bash
# T25R4 PROBE RUNNER -- ONE LEVEL, LEG A ONLY, endTime 2.0 s (prereg section 2).
# Invoke as:  setsid nohup bash run_probe_t25R4.sh <P1|P2|P3> </dev/null >log 2>&1 &  ; disown
# rc IS CAPTURED INSIDE, immediately after mpirun. `setsid timeout` exits 0 for
# every outcome including a kill, so an rc read around it is a constant zero.
RUN="$1"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE="$HERE/$RUN"
trap 'S=$?; [ -d "$CASE" ] && echo "$S" > "$CASE/.rc.$RUN.launcher"; \
      echo "launcher exit rc=$S"' EXIT
case "$RUN" in
  P1) TO=240  ;;   # cap 8  core-min at 2 ranks
  P2) TO=540  ;;   # cap 18
  P3) TO=1200 ;;   # cap 40
  *) echo "REFUSE: $RUN is not a registered probe level"; exit 91 ;;
esac
[ -d "$CASE" ] || { echo "REFUSE: no case dir $CASE"; exit 89; }
. /usr/lib/openfoam/openfoam2606/etc/bashrc > "$CASE/log.foamenv" 2>&1
command -v chtMultiRegionFoam >/dev/null 2>&1 || { echo "REFUSE: solver not on PATH"; exit 88; }
cd "$CASE" || exit 90
[ -d "$CASE/0" ] && { echo "REFUSE: 0/ exists; the age guard would be unevaluable"; exit 92; }
TD=$(find "$CASE" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended \
     -regex '.*/[0-9]+(\.[0-9]+)?$' 2>/dev/null | head -3)
[ -n "$TD" ] && { echo "REFUSE: time directory present: $TD"; exit 93; }
cp -r "$CASE/0.orig" "$CASE/0" || exit 94
sleep 1; touch "$CASE/0/module/T" || exit 95
decomposePar -allRegions -force > log.decomposePar 2>&1
D=$?; echo "$D" > ".rc.$RUN.decomposePar"; [ "$D" -eq 0 ] || exit 96
timeout "$TO" mpirun --bind-to none -np 2 chtMultiRegionFoam -parallel > log.solve.legA 2>&1
RC=$?                                   # <-- INSIDE
echo "$RC" > ".rc.$RUN.legA"
echo "PROBE $RUN legA rc=$RC (124 = CAP STOP; rule 12: an overrun stops the run)"
exit "$RC"
