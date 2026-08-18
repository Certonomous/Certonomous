#!/usr/bin/env bash
set -e
cd "$1"
openfoam2606 simpleFoam -postProcess -func yPlus -latestTime > log.yPlus 2>&1 || true
grep -E "patch body.*y\+|min = .*max = .*average" log.yPlus | tail -2
