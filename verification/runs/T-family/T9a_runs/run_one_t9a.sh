#!/bin/bash
# T9a per-case wrapper. Run FROM INSIDE the case directory:  setsid nohup ../run_one_t9a.sh <case> &
# Writes log.solve in the case and STATUS.<case> in the run tree (rc= wall= checkMesh_rc=).
# 0/ is re-copied from 0.orig at the start so that 0/T is dated by THIS run (mark_done age test).
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
name="$1"; here="$(pwd)"; root="$(dirname "$here")"
rm -rf 0 && cp -r 0.orig 0
checkMesh > log.checkMesh 2>&1; cm=$?
t0=$(date +%s.%N)
laplacianFoam > log.solve 2>&1; rc=$?
t1=$(date +%s.%N)
wall=$(python3 -c "print(f'{$t1-$t0:.2f}')")
echo "rc=$rc wall=${wall}s checkMesh_rc=$cm case=$name end=$(date -u +%FT%TZ) pid=$$" > "$root/STATUS.$name"
