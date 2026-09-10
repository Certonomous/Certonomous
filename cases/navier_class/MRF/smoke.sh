#!/usr/bin/env bash
# MRF_R1 EXERCISE smoke (A3FL1): NOT the graded run. Initialises the fields,
# runs potentialFoam (NO -writephi -- F8 sec.15: -writephi inside an active MRF
# zone writes a toxic absolute-frame flux), then simpleFoam to the smoke endTime
# (controlDict: 50 iters). rc is captured INSIDE this wrapper (the rc sidecar),
# never inferred from an End line (setsid-parent-returns-zero lesson).
#   smoke.sh <RUNDIR>
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
RUNDIR="${1:?usage: smoke.sh <RUNDIR>}"
cd "$RUNDIR" || exit 3

rm -rf 0; cp -r 0.orig 0

potentialFoam > log.potentialFoam 2>&1; echo "potentialFoam rc=$?"

simpleFoam > log.simpleFoam 2>&1; SF_RC=$?
echo "$SF_RC" > rc
echo "simpleFoam rc=$SF_RC (written to $(pwd)/rc)"
echo "DONE smoke $RUNDIR"
