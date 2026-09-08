#!/bin/bash
# DMR L5 BOUNDED-T / POSITIVITY-PRESERVING SUCCESSOR driver -- runs the fresh,
# self-contained three-level family R1/R2/R3 per
#   verification/campaign/DMR_R3_L5_BOUNDED_T_PREREGISTRATION_DRAFT.md
# (once FROZEN and after the cfd supervisor's check-1/check-4 and Sanaa's go).
#
# This mirrors run_dmr_l4_firstorder_t.sh's PROVEN idioms EXACTLY -- rc captured
# inside the wrapper at every step, ONE registered hard core-min cap that STOPS the
# run and writes a CAP_BREACH file (no new budget), the rule-4 ABSENT guard per
# level, and a per-level grade-path-hashed grading pass -- and changes only what the
# L5 family requires: the L5 generator make_case_l5_bounded_t.py, the fresh L5 run
# root, and the L5 solver binary rhoCentralFoamBoundedDMR.  The SINGLE registered
# lever vs the L4 first-order-T successor is the SOLVER BINARY: vanilla
# rhoCentralFoam -> rhoCentralFoamBoundedDMR, which floors internal energy e (hence
# T) to a positive value BEFORE thermo.correct(), applied UNIFORMLY to all three
# levels (a graded Roache triple requires one numerics family; the parent
# disqualifies any per-rung difference).  L5 keeps L4's numerics byte-identical
# (Tadmor, maxCo 0.1, Euler ddt, reconstruct(rho) Minmod, reconstruct(U) MinmodV,
# reconstruct(T) upwind); the clip is INERT unless a cell is already nonphysical.
#
# CAP -- THE ONE REGISTERED HARD CAP.  The pre-registration §6 registers a SINGLE
# hard cap: total 100.0 core-min.  The per-level §6b figures (R1 ~0.983, R2 ~4.483,
# R3 ~33, overhead ~1.5) are MEASURED-ANCHORED ESTIMATES (from the L4 family's own
# measured coresec), NOT registered per-level caps.  Per rule 2/rule 12 (do NOT
# invent a cap) this driver enforces the ONE registered hard cap via a SINGLE
# accumulator USED_CORESEC carried across ALL steps of ALL THREE levels.  The §6b
# per-level estimates are printed as ADVISORY watermarks for rule-12 calibration
# only.  core-min = wall_s * ranks / 60, accumulated per step with that step's OWN
# rank count -- serial steps count 1 rank, the solve counts 4.  The one-time wmake
# build (§6a) is a separate compile, NOT under this solve cap.
#
# rc IS MEASURED INSIDE THIS WRAPPER, NEVER AROUND THE setsid/timeout LINE.
# `setsid timeout cmd` exits 0 for every outcome, so a caller that reads the
# parent's status learns nothing.  Every step writes its own RC file here and syncs.
# An R3 SIGFPE (rc 136) despite the clip is a MEASURED negative result (the cell-e
# clip is insufficient -- the fault may live on a reconstructed FACE), recorded not
# softened -- under fix-until-runs it CONTINUES the ladder as a further dated
# successor, NEVER a capability finding from one/two SIGFPEs (L-501).
#
# HONEST CAVEAT (stated before the run, rule 2): the clip is NON-CONSERVATIVE in any
# cell where it fires (it injects the energy needed to lift e to eMin_bound).  This
# family may run to completion and then GATE FAIL on accuracy -- the wall-foot energy
# injection could displace the shock past tol 0.0231, or the triple could STAGNATE.
# That is a legitimate robustness-vs-accuracy trade finding (a REAL result), NOT a
# process failure and NOT a widening of the gate: the tolerance is held byte-identical
# to the frozen parent (DMR_PREREGISTRATION.md:88,:91).  A BOUND: line in any solver
# log means the clip fired and localises the offending cell(s).
#
# GUARD (rule 4): refuses each level whose run dir already exists.  A rung is not
# graded on a tree something else may have written.
#
# GRADE-PATH INTEGRITY (rule 2): before grading a level, the frozen grader
# dmr_locator_v2.py is hashed against its committed blob and grading is refused if
# it differs.  The grader reads shock POSITION and no scheme/solver file, so it is
# method-agnostic and grades the bounded-solver family unchanged (rule 6, not edited).

R=/home/ubuntu/Certonomous/verification/runs/DMR_R3_L5_BOUNDED_T_runs
GEN=/home/ubuntu/Certonomous/verification/runs/DMR_runs/make_case_l5_bounded_t.py
GRADER=/home/ubuntu/Certonomous/verification/runs/DMR_runs/dmr_locator_v2.py
FROZEN_GRADER_BLOB=52aacf9669bcf23e88a0bf7984b299fa8aaf286e
SOLVER=rhoCentralFoamBoundedDMR

RANKS=4
CAP_COREMIN=100.0
CAP_CORESEC=6000          # 100.0 * 60 -- the ONE registered hard cap (§6)

# The three registered levels, nested exactly 2:1.  N = cells per unit length;
# make_case_l5_bounded_t.py builds round(N/6) + round((4-1/6)*N) by N, i.e.
# (4N) x N: N=60 -> 240x60, N=120 -> 480x120, N=240 -> 960x240.
LVLS=(R1 R2 R3)
NS=(60 120 240)
# ADVISORY ONLY -- §6b per-level core-min ESTIMATES (measured-anchored on L4), NOT caps.
EST_COREMIN=(0.983 4.483 33.0)

mkdir -p "$R" || exit 1
cd "$R" || exit 1

source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>>"$R/log.sourceerr"
command -v "$SOLVER" >/dev/null || {
  echo "ABORT: $SOLVER not on PATH after sourcing (build the L5 solver first)" | tee "$R/REFUSED.txt"
  echo 91 > "$R/successor.rc.txt"; sync; exit 91; }

USED_CORESEC=0            # ONE accumulator across ALL levels and ALL steps
CASE=""                   # set per level; step() writes RC files into it
LVL=""                    # current level label, for RC/breach filenames

breach() {
  echo "CAP BREACH: ${USED_CORESEC}s core-seconds > ${CAP_CORESEC} (${CAP_COREMIN} core-min total)" \
       "-- L5 BOUNDED-T SUCCESSOR STOPPED at level '${LVL}' step '$1', no new budget" \
       | tee -a "$R/CAP_BREACH.txt"
  echo 9 > "$R/successor.rc.txt"; sync; exit 9
}

# step <label> <ranks> <logfile> -- command follows
step() {
  local label=$1 ranks=$2 log=$3; shift 3
  local remaining=$(( CAP_CORESEC - USED_CORESEC ))
  [ "$remaining" -le 0 ] && breach "$label"
  local budget_wall=$(( remaining / ranks ))
  local s=$(date +%s)
  timeout "${budget_wall}s" "$@" > "$log" 2>&1
  local rc=$?
  local e=$(( $(date +%s) - s ))
  USED_CORESEC=$(( USED_CORESEC + e * ranks ))
  echo "$rc" > "$CASE/RC_${label}.txt" 2>/dev/null || echo "$rc" > "$R/RC_${LVL}_${label}.txt"
  sync
  echo "[${LVL}/${label}] rc=$rc wall=${e}s ranks=$ranks used=${USED_CORESEC}core-s" \
    | tee -a "$R/PROGRESS.txt"
  if [ "$rc" -eq 124 ]; then breach "$label (timeout at its cap slice)"; fi
  if [ "$rc" -ne 0 ]; then
    echo "STEP FAILED: ${LVL}/${label} rc=$rc -- recorded, not softened" | tee -a "$R/PROGRESS.txt"
    echo "$rc" > "$R/successor.rc.txt"; sync; exit "$rc"
  fi
  [ "$USED_CORESEC" -gt "$CAP_CORESEC" ] && breach "$label"
  return 0
}

date -u +%Y%m%dT%H%M%SZ > "$R/successor.t0.txt"; sync

for i in 0 1 2; do
  LVL=${LVLS[$i]}
  N=${NS[$i]}
  CASE="$R/$LVL"
  LVL_START_CORESEC=$USED_CORESEC

  # ---- guard: never write into a populated case (rule 4) -------------------
  if [ -e "$CASE" ]; then
    echo "REFUSED: $CASE already exists. A rung is not graded on a pre-existing tree." \
      | tee "$R/${LVL}_REFUSED.txt"
    echo 90 > "$R/successor.rc.txt"; sync; exit 90
  fi

  # ---- generate the bounded-solver case via the L5 generator ---------------
  python3 "$GEN" "$CASE" "$N" > "$R/log.makeCase_${LVL}" 2>&1 || {
    echo "ABORT: make_case_l5_bounded_t.py failed for ${LVL} (N=$N)" | tee "$R/${LVL}_REFUSED.txt"
    echo 92 > "$R/successor.rc.txt"; sync; exit 92; }

  cd "$CASE" || exit 1
  step blockMesh        1 "$CASE/log.blockMesh"        blockMesh
  step checkMesh        1 "$CASE/log.checkMesh"        checkMesh
  step setExprFields    1 "$CASE/log.setExprFields"    setExprFields
  step decomposePar     1 "$CASE/log.decomposePar"     decomposePar
  step "$SOLVER"        4 "$CASE/log.${SOLVER}"        mpirun -np 4 "$SOLVER" -parallel
  step reconstructPar   1 "$CASE/log.reconstructPar"   reconstructPar
  step writeCellCentres 1 "$CASE/log.writeCellCentres" postProcess -func writeCellCentres -time 0.2

  # ---- grade-path integrity (rule 2) THEN grade ----------------------------
  GB=$(git -C /home/ubuntu/Certonomous hash-object "$GRADER" 2>/dev/null)
  if [ "$GB" != "$FROZEN_GRADER_BLOB" ]; then
    echo "REFUSED: grader blob '$GB' != frozen '$FROZEN_GRADER_BLOB' -- grading path not the frozen instrument" \
      | tee "$R/${LVL}_GRADE_REFUSED.txt"
    echo 93 > "$R/successor.rc.txt"; sync; exit 93
  fi
  step grade 1 "$CASE/log.grade" python3 "$GRADER" "$CASE" "$N" --out "$CASE/locator_result.json"

  cd "$R" || exit 1
  LVL_USED=$(( USED_CORESEC - LVL_START_CORESEC ))
  printf '%s\n' "$LVL_USED" > "$R/${LVL}.coresec.txt"; sync
  echo "[${LVL}] level complete: used $(echo "scale=3; $LVL_USED/60" | bc) core-min" \
       "(§6b ADVISORY estimate ${EST_COREMIN[$i]} core-min -- NOT a cap; rule-12 calibration)" \
    | tee -a "$R/PROGRESS.txt"
done

date -u +%Y%m%dT%H%M%SZ > "$R/successor.t1.txt"
echo 0 > "$R/successor.rc.txt"
printf '%s\n' "$USED_CORESEC" > "$R/successor.coresec.txt"
sync
echo "L5 BOUNDED-T SUCCESSOR COMPLETE: used ${USED_CORESEC} core-seconds = $(echo "scale=2; $USED_CORESEC/60" | bc) core-min against the ${CAP_COREMIN} core-min total cap" \
  | tee -a "$R/PROGRESS.txt"
