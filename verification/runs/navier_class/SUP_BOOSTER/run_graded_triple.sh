#!/bin/bash
# SUP_BOOSTER E1 graded-triple launcher -- DETACHED, serial, cost-capped (rule 12).
#
# Runs the coarse/medium/fine Taylor-Maccoll cone triple SEQUENTIALLY (1 rank each: good
# citizen -- ansys + heat-transfer solvers are live, R4 has first call on capacity). Meshes
# are regenerated from the PINNED generator (gen_cone_mesh.py, blob da65ffe2) so the grader's
# 2.25x-family assert holds. On completion it invokes the committed detached autograder, so
# grading fires from THIS detached OS process, independent of any live agent
# (detached-queue-runner ruling).
#
# CRITICAL (L: setsid parent returns zero): this script is launched under `setsid`, whose
# parent returns 0 for EVERY outcome. Real exit codes are captured INSIDE here and written to
# rc.* status files -- never inferred from the setsid line.
#
# COST CAP = 90 core-min = 5400 core-s. Serial (1 rank) => 5400 wall-s, split as per-level
# timeouts summing to the cap. A level that hits its timeout is STOPPED (rc 124); it does NOT
# get a new budget (rule 12) -- the grader then refuses it on rule-4 completion. Sends
# nothing, launches no graded compute beyond this frozen triple (rules 7, 16).
# source the OpenFOAM env BEFORE `set -u` -- its bashrc references unset vars and would
# abort the script under nounset (this bit the first launch: source aborted before any dir
# was created).
source /usr/lib/openfoam/openfoam2606/etc/bashrc 2>/dev/null
set -u
REPO=/home/ubuntu/Certonomous
CASE=$REPO/cases/navier_class/SUP_BOOSTER
GEN=$CASE/gen_cone_mesh.py
RUN=$REPO/verification/runs/navier_class/SUP_BOOSTER/graded
AUTOGRADE=$REPO/verification/runs/navier_class/SUP_BOOSTER/autograde_sup_booster.sh

mkdir -p "$RUN"
# per-level wall timeouts (s); sum = 5400 = 90 core-min cap (serial, 1 rank)
declare -A TMO=( [coarse]=1200 [medium]=1800 [fine]=2400 )

for lvl in coarse medium fine; do
    d="$RUN/$lvl"
    rm -rf "$d"; mkdir -p "$d"
    cp -r "$CASE/system" "$CASE/constant" "$d/"
    python3 "$GEN" --level "$lvl" --out "$d/system/blockMeshDict" 2>"$d/log.gen"
    (
        cd "$d" || exit 91
        t0=$(date +%s)
        blockMesh > log.blockMesh 2>&1; echo $? > rc.blockMesh
        cp -r "$CASE/0.orig" 0            # 0/T touched at launch -> dates the run (rule-4 age guard)
        timeout "${TMO[$lvl]}" rhoCentralFoam > log.rhoCentralFoam 2>&1; rc=$?
        echo "$rc" > rc.solve             # rc CAPTURED INSIDE the detached wrapper
        t1=$(date +%s)
        echo $((t1 - t0)) > wall_s
        echo "level=$lvl rc_solve=$rc wall_s=$((t1 - t0))" > STATUS
    )
done

# grading fires here, from within this detached process (independent of any live agent)
bash "$AUTOGRADE" > "$RUN/log.autograde" 2>&1
echo "done $(date -u +%FT%TZ)" > "$RUN/LAUNCHER_DONE"
