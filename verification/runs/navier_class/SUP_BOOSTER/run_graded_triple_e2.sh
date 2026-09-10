#!/bin/bash
# SUP_BOOSTER **E2** graded-triple launcher -- DETACHED, serial, cost-capped (rule 12).
#
# THIS IS NOT E1's LAUNCHER. run_graded_triple.sh (E1) pins the E1 grader, the E1 generator and
# E1's 90-core-min cap, and writes into the E1 run root `graded/`, which it `rm -rf`s level by
# level. Running it for E2 would DESTROY E1's evidence. This script:
#   * pins the E2 grading path  -- gen_cone_mesh_e2.py (GR_RADIAL 5) and, through the E2
#     autograder, grade_sup_booster_e2.py;
#   * writes ONLY under the registered E2 run root `graded_e2/`; E1's root appears in this
#     file only in these comment lines and is assigned to no variable and passed to no command;
#   * carries SUP_BOOSTER_E2_PREREGISTRATION.md section 5's cap of **60 core-min**, not E1's 90.
#
# Runs the coarse/medium/fine Taylor-Maccoll cone triple SEQUENTIALLY (1 rank each: good
# citizen). Meshes are regenerated from the PINNED E2 generator so the grader's 2.25x-family
# assert holds. On completion it invokes the committed detached E2 autograder, so grading fires
# from THIS detached OS process, independent of any live agent (detached-queue-runner ruling).
#
# COST CAP = 60 core-min = 3600 core-s. Serial (1 rank) => 3600 solver wall-s, split as
# per-level timeouts 800/1200/1600 that sum to exactly the cap. Every level has headroom over
# its E1 measured wall time (243/501/1107 s): 3.3x, 2.4x, 1.45x. A level that hits its timeout
# is STOPPED (rc 124); it does NOT get a new budget (rule 12) -- the grader then refuses it on
# rule-4 completion. blockMesh and the generator run outside the timeout (seconds per level).
#
# CRITICAL (L: setsid parent returns zero): this script is launched under `setsid`, whose parent
# returns 0 for EVERY outcome. Real exit codes are captured INSIDE this script and written to
# rc.* status files -- NEVER inferred from the setsid line, and never captured around it.
#
# Sends nothing, files nothing, launches no compute beyond this triple (rules 7, 16).

# source the OpenFOAM env BEFORE `set -u` -- its bashrc references unset vars and would abort
# the script under nounset (this bit E1's first launch: source aborted before any dir existed).
source /usr/lib/openfoam/openfoam2606/etc/bashrc 2>/dev/null
set -u
REPO=/home/ubuntu/Certonomous
CASE=$REPO/cases/navier_class/SUP_BOOSTER
GEN=$CASE/gen_cone_mesh_e2.py                                          # E2 generator, PINNED
RUN=$REPO/verification/runs/navier_class/SUP_BOOSTER/graded_e2         # E2 run root, REGISTERED
AUTOGRADE=$REPO/verification/runs/navier_class/SUP_BOOSTER/autograde_sup_booster_e2.sh

# Refuse rather than degrade: a missing pinned input is not something to work around.
for f in "$GEN" "$AUTOGRADE" "$CASE/system" "$CASE/constant" "$CASE/0.orig"; do
    [ -e "$f" ] || { echo "REFUSE: pinned input missing: $f" >&2; exit 2; }
done
# Never write into E1's root, whatever anyone passes.
case "$RUN" in *graded_e2) : ;; *) echo "REFUSE: run root is not graded_e2: $RUN" >&2; exit 2;; esac

mkdir -p "$RUN"
# per-level solver wall timeouts (s); sum = 3600 = 60 core-min cap (serial, 1 rank)
declare -A TMO=( [coarse]=800 [medium]=1200 [fine]=1600 )

T0=$(date +%s)
for lvl in coarse medium fine; do
    d="$RUN/$lvl"
    rm -rf "$d"; mkdir -p "$d"
    cp -r "$CASE/system" "$CASE/constant" "$d/"
    python3 "$GEN" --level "$lvl" --out "$d/system/blockMeshDict" 2>"$d/log.gen"
    echo $? > "$d/rc.gen"
    (
        cd "$d" || exit 91
        t0=$(date +%s)
        blockMesh > log.blockMesh 2>&1; echo $? > rc.blockMesh
        cp -r "$CASE/0.orig" 0            # 0/T touched at launch -> dates the run (rule-4 age guard)
        timeout "${TMO[$lvl]}" rhoCentralFoam > log.rhoCentralFoam 2>&1; rc=$?
        echo "$rc" > rc.solve             # rc CAPTURED INSIDE the detached wrapper
        t1=$(date +%s)
        echo $((t1 - t0)) > wall_s
        echo "level=$lvl rc_solve=$rc wall_s=$((t1 - t0)) timeout_s=${TMO[$lvl]}" > STATUS
        [ "$rc" = "124" ] && echo "level=$lvl STOPPED at its ${TMO[$lvl]} s share of the 60 core-min cap (rule 12): no new budget" > CAP_STOP.txt
        exit 0
    )
    echo $? > "$d/rc.wrapper"          # the subshell's own rc (91 = cd failed), captured INSIDE
done
T1=$(date +%s)
echo "solver+mesh wall_s=$((T1 - T0)) ranks=1 core_min=$(( (T1 - T0) / 60 )) cap_core_min=60" > "$RUN/COST.txt"

# grading fires here, from within this detached process (independent of any live agent)
bash "$AUTOGRADE" > "$RUN/log.autograde" 2>&1
echo "done $(date -u +%FT%TZ)" > "$RUN/LAUNCHER_DONE"
