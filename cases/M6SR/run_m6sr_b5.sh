#!/bin/bash
# M6SR SOLVE DRIVER -- steps B4 and B5a/B5b/B5c of
# verification/campaign/M6SR_PREREGISTRATION.md.
#
# WHAT THIS FILE IS.  Amendment 10 item 10 records, measured, that "NO REGISTERED ARTIFACT
# RUNS `B5a`, `B5b` OR `B5c` -- 607.63 of 615.24 core-min, 98.8 % of the ladder -- AND NONE
# OF SECTION 8's CASE FILES EXISTS", and that in consequence "a queue row cannot be written
# today: its `launch_cmd` has no target for `B5`".  THIS FILE IS THAT TARGET.
#
# It also produces B4's `log.checkMesh`, which likewise had no producer: the registered
# build driver cases/M6SR/build_m6sr_l1.sh covers B1/B2/B3 only and its own closing line
# reads "THIS DRIVER GRADES NOTHING".
#
# IT IS A SOLVER DRIVER, NOT A GRADER.  It computes no gate, applies no threshold and
# prints no verdict.  Standing rule 2 fixes the GRADING path at the pre-registration
# commit; this file runs the solver and cases/M6SR/analyse_m6sr.py grades what it produced.
# NOTHING HERE MAY EVER GRADE.
#
# SECTIONS OF THE REGISTRATION IMPLEMENTED HERE:
#   Section 2.4   the per-step CAPS in core-minutes, enforced STRUCTURALLY by `timeout`.
#                 B5a/B5b/B5c caps are PER-LEVEL rows (31.0 / 163.0 / 1630.0).  B4's 2.0 is
#                 ONE row for "checkMesh x3", so it is a RUNNING budget across the three
#                 levels, tracked on disk and refused when exhausted.
#   Section 3.2   `hierarchical` decomposition; `scotch` is NOT used.
#   Section 7     the ill-posedness screen -- the driver REFUSES patch types it did not
#                 expect, through the case writer's CH1 classification.
#   Section 8     every case file, written by cases/M6SR/write_m6sr_case.py.
#   Section 8.6   the launcher REFUSES a case where `0` or any time directory exists, and
#                 the strict all-or-nothing completion rule is EVALUATED (never graded) here.
#   Section 9.2   execution and assertion mechanics -- every line of it, below.
#   Section 9.3   rule 12's estimate-versus-actual, owed at EVERY step.
#
# SECTION 9.2, BINDING, AND EACH LINE OF IT IS OBSERVED HERE:
#   * ASSERTIONS DO NOT GATE.  No `assert`, no bare `set -e`.  Every check is
#     `... || { echo "ABORT: <what>"; exit N; }`.  A guard set that is assert-based is one
#     interpreter flag from absent (L-475).
#   * SHAS ARE READ BACK BY SUBJECT LINE, never by position in a batch (L-479).
#   * `setsid timeout cmd` EXITS 0 FOR EVERY OUTCOME.  rc is captured INSIDE the wrapper
#     and written to a file; it is never taken from around the wrapper line.
#   * `grep ... log.* | tail -1` IS A COIN FLIP under multi-file output.  Every reading in
#     this file names ONE artifact by explicit path.
#   * RANKS ARE TAKEN FROM THE SOLVER LOG'S OWN BANNER, NEVER FROM decomposeParDict.  That
#     file can post-date the run, and the banner's FIRST occurrence is not necessarily the
#     primal's -- so this driver reads EVERY `nProcs` line in the ONE named solver log and
#     REFUSES if they are not all equal, and if they do not equal what it asked for.
#
# THE RANK-BASIS TRAP, CARRIED FORWARD FROM AMENDMENT 8 AND NOT RE-LITIGATED HERE.
# Section 2.4's solve rate 3.40e-8 core-min/cell/iteration is a FOUR-RANK measurement
# (`nProcs : 4` in the primal banner of A3-onera-m6-transonic/run_model_run3.log).  B5b
# runs at 8 ranks and B5c at 16, so the registered estimate applies a 4-rank rate at 2x and
# 4x the ranks and thereby ASSUMES PERFECT STRONG SCALING.  Real efficiency below 1 makes
# the actual core-minutes RISE, not fall.  This driver does not change a registered number;
# it records the measured core-minutes and the measured rank count side by side so the
# Section 9.3 calibration row can attribute the miss.
#
# COST.  Unit: core-minutes (wall s x ranks / 60).  Dollars are DERIVED, NOT MEASURED, at
# the owner-stated c7a.4xlarge $0.0513/core-h -- the box cannot read its own billing, so any
# dollar figure originating here is REPORTED-BY-OWNER.  AN OVERRUN STOPS THE RUN; it does
# not get a new budget.  Every cap below is enforced by `timeout`, so an overrun is
# structural rather than a matter of somebody noticing.
#
# NOTHING UNDER /home/ubuntu/certonomous-runs/ IS WRITTEN, MOVED OR DELETED.  L3's and L2's
# meshes are COPIED OUT of that tree; every product is written under the run root.
#
# SUBMISSIONS ARE PARKED (standing rule 7).  This driver sends nothing anywhere.
#
# USAGE:  run_m6sr_b5.sh <L3|L2|L1> [stage|solve|all]

set +u
set +e

LEVEL="$1"
PHASE="${2:-all}"

RR=${M6SR_RUN_ROOT:-/home/ubuntu/Certonomous/verification/runs/M6SR_runs}
CR=/home/ubuntu/certonomous-runs
CASES=/home/ubuntu/Certonomous/cases/M6SR
IMG=${M6SR_IMAGE:-dafoam-idwarp-rot:v1}
RATE_USD_PER_CORE_H=0.0513

say(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }
abort(){ echo "ABORT: $1"; mkdir -p "$RR/$LEVEL" 2>/dev/null; echo "$1" > "$RR/$LEVEL/STOPPED.txt" 2>/dev/null; exit "${2:-1}"; }

# sha256 of ONE named file.  L-479: never a batch, never read back by position.
sha_of(){ sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

# ---------------------------------------------------------------------------------------
# 0.  THE LEVEL TABLE.  Section 2.2 / 2.4 / 8.5.  Nothing here is chosen by this driver.
# ---------------------------------------------------------------------------------------
case "$LEVEL" in
  L3) CELLS=99840   ; END_TIME=3000 ; RANKS=4  ; CAP_B5=31.0   ; EST_B5=10.18
      MESH_SRC="$CR/A3-onera-m6-adjoint-coarse/constant/polyMesh" ; STEP=B5a ;;
  L2) CELLS=399360  ; END_TIME=4000 ; RANKS=8  ; CAP_B5=163.0  ; EST_B5=54.31
      MESH_SRC="$CR/.mesh-cache/onera_m6/polyMesh"               ; STEP=B5b ;;
  L1) CELLS=1597440 ; END_TIME=5000 ; RANKS=16 ; CAP_B5=1630.0 ; EST_B5=543.13
      MESH_SRC="$RR/L1/constant/polyMesh"                        ; STEP=B5c ;;
  *)  echo "ABORT: level must be one of L3 L2 L1; got '${LEVEL:-<empty>}'"; exit 2 ;;
esac
case "$PHASE" in
  stage|solve|all) : ;;
  *) echo "ABORT: phase must be one of stage solve all; got '$PHASE'"; exit 2 ;;
esac

CASE="$RR/$LEVEL"
CAP_B4_TOTAL=2.0                       # Section 2.4: ONE row, "checkMesh x3", for all levels
B4_LEDGER="$RR/B4_SPENT_COREMIN.txt"

say "M6SR solve driver -- level $LEVEL ($STEP), phase $PHASE"
say "run root: $RR   (nothing under $CR is written)"
say "schedule: $CELLS cells, endTime $END_TIME, $RANKS ranks, cap $CAP_B5 core-min (est $EST_B5)"

# ---------------------------------------------------------------------------------------
# 1.  REFUSALS BEFORE ANY WORK.
# ---------------------------------------------------------------------------------------
[ -x "$CASES/write_m6sr_case.py" ] || [ -f "$CASES/write_m6sr_case.py" ] \
  || abort "the registered case writer $CASES/write_m6sr_case.py is ABSENT. This driver writes NO case file of its own -- there is ONE writer and it is that one." 3

# Section 8.6: the launcher REFUSES a case where `0` or any time directory already exists.
if [ -d "$CASE" ]; then
  [ -d "$CASE/0" ] && abort "$CASE/0 already exists. The age guard dates the run from the case's own 0/U, so a pre-existing 0/ makes standing rule 4 unprovable. REFUSED (Section 8.6)." 4
  for D in "$CASE"/[0-9]*; do
    [ -d "$D" ] && abort "a time directory already exists: $D. REFUSED (Section 8.6)." 4
  done
fi

mkdir -p "$CASE" || abort "could not create $CASE" 3

# Docker preflight, BOTH limbs recorded, because the bare failure would be silent.
BARE_OUT=$(docker version --format '{{.Server.Version}}' 2>&1); BARE_RC=$?
SG_OUT=$(sg docker -c "docker version --format '{{.Server.Version}}'" 2>&1); SG_RC=$?
{ echo "bare_rc=$BARE_RC"; echo "bare_out=$BARE_OUT"
  echo "sg_rc=$SG_RC";     echo "sg_out=$SG_OUT"
  echo "groups=$(id -G)"; } > "$CASE/DOCKER_PREFLIGHT.txt"
if [ $SG_RC -ne 0 ] && [ $BARE_RC -ne 0 ]; then
  abort "docker unreachable both bare and through 'sg docker -c'. This grades THE DRIVER'S ABILITY TO RUN and nothing about the M6 -- BLOCKED, not GATE FAIL." 5
fi
if [ $BARE_RC -eq 0 ]; then DRUN="docker"; else DRUN="sg docker -c"; fi
say "docker reachable (bare rc=$BARE_RC, sg rc=$SG_RC); using '$DRUN'"

# ---------------------------------------------------------------------------------------
# 2.  THE CONTAINER WRAPPER.  rc IS CAPTURED INSIDE (Section 9.2) -- `setsid timeout cmd`
#     exits 0 for every outcome, so an rc taken from around the wrapper line is meaningless.
#     The cap is enforced by `timeout` and AN OVERRUN STOPS THE RUN.
# ---------------------------------------------------------------------------------------
run_in_container(){
  local tag="$1" tmo="$2" ranks="$3" cmd="$4"
  local t0 t1 rc wall inner
  t0=$(date +%s)
  timeout "${tmo}"s $DRUN "docker run --rm --name m6sr_${tag}_$$ -u 1002:1002 \
      -v '$CASE':/case -w /case $IMG \
      bash -c 'set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; \
               $cmd; echo \"WRAPPER_RC=\$?\" > RC_${tag}.txt'" \
      > "$CASE/log.$tag" 2>&1
  rc=$?
  t1=$(date +%s); wall=$((t1-t0))
  $DRUN "docker rm -f m6sr_${tag}_$$" >/dev/null 2>&1
  # THE INNER rc, read from the file the wrapper wrote, BY EXPLICIT PATH -- never from $?
  # around the timeout line, and never by `grep log.* | tail -1`.
  inner="ABSENT"
  [ -f "$CASE/RC_${tag}.txt" ] && inner=$(cut -d= -f2 "$CASE/RC_${tag}.txt")
  echo "$tag outer_rc=$rc inner_rc=$inner wall_s=$wall timeout_s=$tmo ranks=$ranks" \
      >> "$CASE/STEP_RC.txt"
  echo "$wall" > "$CASE/WALL_${tag}.txt"
  echo "$inner" > "$CASE/INNER_RC_${tag}.txt"
  say "$tag: outer rc=$rc  INNER rc=$inner  wall=${wall}s  cap=${tmo}s  ranks=$ranks"
  if [ "$rc" -eq 124 ]; then
    abort "$tag exceeded its structural cap of ${tmo} wall s at $ranks ranks. AN OVERRUN STOPS THE RUN. It does not get a new budget (rule 12)." 6
  fi
  [ "$inner" = "0" ] || abort "$tag inner rc=$inner (outer $rc). A non-zero rc inside the container is a FAILED STEP, whatever the outer wrapper returned." 6
}

# ---------------------------------------------------------------------------------------
# 3.  PHASE `stage` -- the mesh into the run root, its published hash, and B4's checkMesh.
#
#     CHOICE CH12 (recorded in CASE_PROVENANCE.json): the mesh is COPIED in.  L3's and L2's
#     meshes live under $CR, which is READ ONLY, and a solver writes into its own case.  The
#     comparator's _discover_levels() already rules for exactly this: "An in-run-root copy,
#     once it exists, SUPERSEDES the read-only source."
#
#     SUPERVISOR ITEM, REPORTED AND NOT ABSORBED: Section 2.4's cost table has NO ROW for
#     staging L3's and L2's pre-existing meshes into the run root.  B3 covers the L1 build
#     only.  The staging cost is measured and reported below on its own line as `B3s`; it is
#     NOT folded into any registered row and it is NOT absorbed into a ratio (Section 9.3).
# ---------------------------------------------------------------------------------------
if [ "$PHASE" = "stage" ] || [ "$PHASE" = "all" ]; then
  if [ -d "$CASE/constant/polyMesh" ]; then
    say "stage: $CASE/constant/polyMesh already present; NOT overwritten"
  else
    [ -d "$MESH_SRC" ] || abort "the level's mesh source is ABSENT: $MESH_SRC. An absent mesh is a REFUSAL, never an empty level. (L1's mesh is built by cases/M6SR/build_m6sr_l1.sh -- run B1/B2/B3 first.)" 3
    T0S=$(date +%s)
    mkdir -p "$CASE/constant" || abort "could not create $CASE/constant" 3
    cp -a -- "$MESH_SRC" "$CASE/constant/polyMesh" || abort "mesh copy-out of $MESH_SRC failed" 3
    T1S=$(date +%s)
    echo "$((T1S-T0S))" > "$CASE/WALL_stage.txt"
    say "stage: copied $MESH_SRC -> $CASE/constant/polyMesh in $((T1S-T0S))s (step B3s, UNBUDGETED in Section 2.4)"
  fi

  # The points-stream sha, PUBLISHED here so Gate A's family-identity proof reads the same
  # bytes at the copy that it would have read at the source.  Hashed on the DECOMPRESSED
  # stream (Section 1.4): a gzip hash also encodes the compressor's settings and mtime.
  PSHA=$(python3 -c "
import sys
sys.path.insert(0, '$CASES')
import analyse_m6sr as A
print(A.points_stream_sha('$CASE/constant/polyMesh'))
" 2>"$CASE/log.pointshash.err")
  [ -n "$PSHA" ] || abort "could not compute the decompressed points-stream sha of $CASE/constant/polyMesh (see $CASE/log.pointshash.err). A missing hash is a REFUSAL, never a fallback." 3
  echo "$PSHA" > "$CASE/points_stream.sha256"
  say "stage: points-stream sha256 $PSHA  -- PUBLISHED for Gate A item A5"

  # ---- B4's checkMesh.  Section 2.4 gives ONE row (cap 2.0 core-min) for "checkMesh x3",
  # so the cap is a RUNNING budget across the three levels, tracked on disk.
  if [ -f "$CASE/log.checkMesh" ]; then
    say "stage: $CASE/log.checkMesh already present; checkMesh NOT re-run"
  else
    SPENT=$(cat "$B4_LEDGER" 2>/dev/null); [ -n "$SPENT" ] || SPENT=0
    TMO_B4=$(python3 -c "
rem = $CAP_B4_TOTAL - $SPENT
print(int(rem * 60) if rem > 0 else 0)")
    [ "$TMO_B4" -gt 0 ] || abort "B4's registered cap of $CAP_B4_TOTAL core-min is EXHAUSTED ($SPENT core-min already spent across levels). AN OVERRUN STOPS THE RUN; it does not get a new budget (rule 12)." 6
    say "B4: checkMesh, remaining budget $(python3 -c "print(round($CAP_B4_TOTAL - $SPENT, 4))") core-min -> ${TMO_B4}s at 1 rank"
    run_in_container checkMesh "$TMO_B4" 1 "checkMesh -constant > log.checkMesh 2>&1"
    W4=$(cat "$CASE/WALL_checkMesh.txt" 2>/dev/null || echo 0)
    python3 -c "
spent = $SPENT + $W4 * 1 / 60.0
open('$B4_LEDGER', 'w').write('%.6f\n' % spent)
print('B4 ledger: %.6f core-min spent of $CAP_B4_TOTAL' % spent)"
    [ -s "$CASE/log.checkMesh" ] || abort "checkMesh produced no log.checkMesh. Gate A reads NAMED NUMERIC MAXIMA off that file; an absent checkMesh log reads ABSENT and NEVER reads clean (Section 5, L-459)." 6
  fi
fi

[ "$PHASE" = "stage" ] && { say "stage complete for $LEVEL. THIS DRIVER GRADES NOTHING."; exit 0; }

# ---------------------------------------------------------------------------------------
# 4.  PHASE `solve` -- Section 8's case files, then $STEP.
# ---------------------------------------------------------------------------------------
[ -d "$CASE/constant/polyMesh" ] || abort "$CASE/constant/polyMesh is ABSENT; run phase 'stage' first." 3

# The case writer carries Section 8 and REFUSES on any precondition it cannot satisfy.  Its
# own planted controls must fire before it is trusted to have written what it says it wrote
# (rule 3): a writer whose plant did not fire is not evidence about the case it produced.
python3 "$CASES/write_m6sr_case.py" --selftest > "$CASE/log.writer_controls" 2>&1
WRC=$?
[ "$WRC" -eq 0 ] || abort "the case writer's PLANTED CONTROLS did not fire (rc $WRC; see $CASE/log.writer_controls). A case written by a writer whose plant did not fire is not evidence (rule 3). REFUSED." 6
say "case writer: ALL PLANTED CONTROLS FIRED (see $CASE/log.writer_controls)"

python3 "$CASES/write_m6sr_case.py" --case "$CASE" --level "$LEVEL" \
    > "$CASE/log.write_case" 2>&1
WRC=$?
[ "$WRC" -eq 0 ] || abort "the case writer REFUSED or failed (rc $WRC; see $CASE/log.write_case). Section 8's case files were NOT written and there is nothing to solve." 6
[ -f "$CASE/0/U" ] || abort "the case writer returned 0 but $CASE/0/U is absent. REFUSED." 70
say "case written: Section 8's seven 0/ fields, fvSchemes, fvSolution, constant/, controlDict, decomposeParDict, sampleDict"
say "case provenance and EVERY CHOICE MADE: $CASE/CASE_PROVENANCE.json"

# uid 1002 inside the container must be able to write the case it solves.
chmod -R 777 "$CASE" 2>/dev/null

# ---- $STEP.  Cap from Section 2.4's own per-level row, converted at THIS step's ranks.
TMO_B5=$(python3 -c "print(int($CAP_B5 * 60.0 / $RANKS))")
say "$STEP: decomposePar + mpirun -np $RANKS rhoSimpleFoam -parallel + reconstructPar"
say "$STEP: cap $CAP_B5 core-min at $RANKS ranks -> ${TMO_B5} wall s.  AN OVERRUN STOPS THE RUN."

# ONE named solver log.  `log.rhoSimpleFoam` is the artifact Section 8.6's completion rule
# and Section 5.1's residual reducer both read, so it carries the SOLVER and nothing else --
# decomposePar and reconstructPar write their own logs.  This is what makes the nProcs
# banner reading unambiguous.
run_in_container "$STEP" "$TMO_B5" "$RANKS" \
  "decomposePar -force > log.decomposePar 2>&1 && \
   mpirun -np $RANKS rhoSimpleFoam -parallel > log.rhoSimpleFoam 2>&1; \
   SOLVER_RC=\$?; echo \$SOLVER_RC > SOLVER_RC.txt; \
   reconstructPar -latestTime > log.reconstructPar 2>&1; \
   exit \$SOLVER_RC"

# ---------------------------------------------------------------------------------------
# 5.  THE RANK READING.  Section 9.2 and Amendment 8: RANKS COME FROM THE SOLVER LOG'S OWN
#     BANNER, NEVER FROM system/decomposeParDict, and the banner's FIRST occurrence is not
#     necessarily the primal's -- so EVERY occurrence in the ONE named log is read and they
#     must ALL agree.
# ---------------------------------------------------------------------------------------
[ -f "$CASE/log.rhoSimpleFoam" ] || abort "$CASE/log.rhoSimpleFoam is ABSENT after the solve step. The completion rule and G2's reducer both read that ONE artifact; without it there is nothing to grade." 6

RANKS_SEEN=$(python3 -c "
import re, sys
txt = open('$CASE/log.rhoSimpleFoam', errors='replace').read()
vals = sorted({int(m) for m in re.findall(r'^nProcs\s*:\s*(\d+)', txt, re.M)})
sys.stdout.write(','.join(str(v) for v in vals))
")
say "$STEP: nProcs values in the solver log's banner(s): [${RANKS_SEEN:-none}]"
[ -n "$RANKS_SEEN" ] || abort "no 'nProcs' banner line in $CASE/log.rhoSimpleFoam. Ranks are READ FROM THE BANNER and never from decomposeParDict; a log with no banner is a REFUSAL, not an assumption of $RANKS." 6
case "$RANKS_SEEN" in
  *,*) abort "the solver log carries DISAGREEING nProcs values [$RANKS_SEEN]. Amendment 8's own basis defect was exactly this -- the file's FIRST nProcs match was 'nProcs : 1' while the primal ran at 4. A log this reader cannot resolve to one rank count is a REFUSAL." 6 ;;
esac
[ "$RANKS_SEEN" = "$RANKS" ] || abort "the solver log's banner reads nProcs = $RANKS_SEEN but this step asked for $RANKS. The COST BASIS is the banner's count, so a mismatch invalidates the core-minute figure. REFUSED." 6
echo "$RANKS_SEEN" > "$CASE/RANKS_FROM_BANNER.txt"

# ---------------------------------------------------------------------------------------
# 6.  SECTION 8.6's STRICT COMPLETION RULE -- EVALUATED, NEVER GRADED.  The verdict belongs
#     to cases/M6SR/analyse_m6sr.py, which is the frozen grading path.  This driver reports
#     the clauses so an operator learns at the drop path rather than at grading time.
# ---------------------------------------------------------------------------------------
python3 -c "
import json, sys
sys.path.insert(0, '$CASES')
import analyse_m6sr as A
cl = A.completion_clauses('$CASE', $END_TIME)
print('COMPLETION CLAUSES (Section 8.6) -- REPORTED BY THE DRIVER, GRADED BY THE COMPARATOR')
for k, v in cl.items():
    print('  %-52s %s' % (k, v))
json.dump(cl, open('$CASE/COMPLETION_CLAUSES.json', 'w'), indent=2)
" 2>&1 | tee "$CASE/log.completion"

# ---------------------------------------------------------------------------------------
# 7.  RULE 12's ESTIMATE-VERSUS-ACTUAL, OWED AT EVERY STEP (Section 9.3).  A completion
#     report without this comparison is INCOMPLETE.  Waste is named SEPARATELY and is never
#     absorbed into the ratio.  RANKS COME FROM THE BANNER.
# ---------------------------------------------------------------------------------------
W_STAGE=$(cat "$CASE/WALL_stage.txt"     2>/dev/null || echo 0)
W_CHECK=$(cat "$CASE/WALL_checkMesh.txt" 2>/dev/null || echo 0)
W_SOLVE=$(cat "$CASE/WALL_$STEP.txt"     2>/dev/null || echo 0)

python3 - "$CASE" "$LEVEL" "$STEP" "$W_STAGE" "$W_CHECK" "$W_SOLVE" "$RANKS_SEEN" \
         "$CELLS" "$END_TIME" "$EST_B5" "$CAP_B5" <<'PYC'
import json, sys
case, level, step = sys.argv[1], sys.argv[2], sys.argv[3]
w_stage, w_check, w_solve = (int(x) for x in sys.argv[4:7])
ranks, cells, end_time = int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9])
est_b5, cap_b5 = float(sys.argv[10]), float(sys.argv[11])

act_solve = round(w_solve * ranks / 60.0, 4)
act_check = round(w_check * 1 / 60.0, 4)
act_stage = round(w_stage * 1 / 60.0, 4)
rate = (act_solve / (cells * end_time)) if cells and end_time else None

out = {
    "level": level, "step": step, "cells": cells, "end_time": end_time,
    "ranks_FROM_SOLVER_LOG_BANNER": ranks,
    "ranks_NOT_taken_from": "system/decomposeParDict -- that file can post-date the run "
                            "(Section 9.2, Amendment 8)",
    "calibration": {
        step: {"estimate_core_min": est_b5, "cap_core_min": cap_b5,
               "actual_core_min": act_solve,
               "ratio_actual_over_predicted": (round(act_solve / est_b5, 3)
                                               if est_b5 else None),
               "within_cap": act_solve <= cap_b5},
        "B4_checkMesh_this_level": {
            "actual_core_min": act_check,
            "note": "Section 2.4 gives ONE B4 row (cap 2.0 core-min) for checkMesh x3; the "
                    "running total across levels is in <run_root>/B4_SPENT_COREMIN.txt"},
        "B3s_mesh_staging": {
            "actual_core_min": act_stage,
            "UNBUDGETED": "Section 2.4's cost table has NO ROW for staging L3's and L2's "
                          "pre-existing meshes into the run root. B3 covers the L1 build "
                          "only. This figure is REPORTED ON ITS OWN LINE and is NOT folded "
                          "into any registered row and NOT absorbed into any ratio "
                          "(Section 9.3, COMPUTE_BUDGET_CHARTER 6)."},
    },
    "measured_solve_rate_core_min_per_cell_per_iteration": rate,
    "registered_rate_and_its_basis": {
        "value": 3.40e-8,
        "basis_ranks": 4,
        "why_it_matters": "The registered rate is a FOUR-RANK measurement "
                          "(A3-onera-m6-transonic/run_model_run3.log, nProcs : 4 in the "
                          "primal banner). Applying it at 8 or 16 ranks ASSUMES PERFECT "
                          "STRONG SCALING; real efficiency below 1 makes core-minutes "
                          "RISE. The ratio above is the measurement of that assumption.",
    },
    "attribution": "UNATTRIBUTED at driver exit -- contention / waste / misprediction is a "
                   "reading a human makes against the box's own load record. Waste is named "
                   "SEPARATELY and is NEVER absorbed into the ratio (Section 9.3).",
    "cost_basis": "core-minutes = wall s x ranks / 60, ranks from the SOLVER LOG BANNER. "
                  "Dollars are DERIVED, NOT MEASURED, at the owner-stated c7a.4xlarge "
                  "$0.0513/core-h -- the box cannot read its own billing "
                  "(COMPUTE_BUDGET_CHARTER.md 5), so any dollar figure originating here is "
                  "REPORTED-BY-OWNER.",
    "derived_usd_this_level": round((act_solve + act_check + act_stage) / 60.0 * 0.0513, 6),
    "L_HONEST": ("This is a SURFACE-REFINEMENT SENSITIVITY STUDY. Its GCI is a "
                 "SURFACE-REFINEMENT BAND and a LOWER BOUND on total discretisation "
                 "uncertainty. It is NOT an observed order of accuracy, and it is NOT the "
                 "family band Sanaa named as her first deliverable."),
}
json.dump(out, open(case + "/SOLVE_RESULT.json", "w"), indent=2)
print(json.dumps(out, indent=2))
PYC

say "$STEP complete for $LEVEL."
say "Gate P's producer wrote: $CASE/postProcessing/sampleDict/$END_TIME/wingSurface/"
say "NEXT: B0 is Gate GF, B4 is Gate A and B6 is Gate G + Gate P, all in cases/M6SR/analyse_m6sr.py."
say "THIS DRIVER GRADES NOTHING."
exit 0
