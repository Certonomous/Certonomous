#!/bin/bash
# =====================================================================================
# SUBOFF R1b GRADED-TRIPLE LAUNCHER  --  successor to run_suboff_r1_triple.sh
#
# R1b is a section-2bc FIX-UNTIL-RUNS SUCCESSOR to SUBOFF R1, which closed NOT A RESULT
# on a cap-stop.  It repairs EXACTLY TWO diagnosed defects and changes nothing else:
#
#   DEFECT 1 (the rung's):  R1's compute cap was derived from a SINGLE-TENANT smoke rate
#       and could not deliver its own registered endTime on the CONTENDED box the rung
#       actually ran on.  reg_coarse reached Time = 1445 of 2500 at its 900 s timeout.
#       A cap that cannot reach its own endTime is not a runaway guard, it is a
#       guaranteed NOT A RESULT.  R1b re-derives the caps from the MEASURED CONTENDED
#       rate.  See SUBOFF_R1b_PREREGISTRATION.md section 7.
#
#   DEFECT 2 (the launch path's):  run_suboff_r1_triple.sh grades ONLY under --grade,
#       and the R1 queue entry did not pass it.  With the fleet dead, a clean R1 would
#       have completed and produced NO VERDICT AT ALL.  In THIS launcher there is NO
#       GRADE FLAG: grading is UNCONDITIONAL, and an EXIT TRAP guarantees that a verdict
#       artifact exists no matter how this process ends -- clean, refused, capped,
#       crashed or killed.  A non-grading run of this launcher is not merely discouraged;
#       it is not expressible.
#
# EVERYTHING ELSE IS INHERITED FROM R1 UNCHANGED: gate D1 and its +/-10% band, the CT
# anchor 3.6e-3 (MANIFEST / BOUNDED-AGREEMENT), the pinned Aref 0.0831703362813915 m^2,
# the analytic wetted area 5.988264212260189 m^2, the 39,904 / 89,784 / 202,014-cell
# family at exactly 2.25x, the +/-70 deg / +/-4 admission gates, the grader
# grade_suboff.py, endTime 2500, deltaT 1, no residualControl, ranks 1.
# NO GATE, THRESHOLD, BAND OR LABEL MOVES.  This is a RESOURCE re-registration.
#
# THIS SCRIPT DOES NOT AUTHORISE ITS OWN RUN.  The pre-registration freeze (sha) and the
# graded launch are the cfd supervisor's SUPERVISION_CHARTER section 3 check-4, taken
# personally.  Being executable is not being approved.
#
# -------------------------------------------------------------------------------------
# THE R1 RULES ARE ALL STILL HERE, EACH EARNED BY A FAILURE.  Read them in
# run_suboff_r1_triple.sh lines 14-65; they are not restated at length.  In brief:
#   (1) rc is captured INSIDE this wrapper, never around a setsid line.
#   (2) NOTHING is deleted.  There is no `rm -rf` in this file.  A dirty target is a
#       REFUSAL, never a clearing.  This is why R1b uses NEW run roots (below).
#   (3) 0/ is created BY THIS SCRIPT at launch from 0.orig/, never pre-staged (age guard).
#   (4) Progress is read from ONE NAMED LOG ARTIFACT, never a glob.  grep here is
#       ugrep 7.8.4 (re-verified 2026-09-10), which interleaves multi-file output.
#   (5) No guard is an `assert`.  This is bash and every guard is an explicit if/refuse.
#       `set -e` is deliberately NOT used: it would abort between simpleFoam returning
#       and its rc being written.
#   (6) The grader and builder are pinned by absolute path and their sha256 recorded.
#
# -------------------------------------------------------------------------------------
# NEW IN R1b (a): NEW RUN ROOTS, AND WHY THEY ARE NEW.
# -------------------------------------------------------------------------------------
# reg_coarse and reg_medium now hold R1's cap-stop evidence: 0/, log.simpleFoam, rc,
# STATUS.R1_*, CAP_BREACH.txt, postProcessing/.  That evidence IS the measured basis of
# R1b's re-derived cap, and rule (2) forbids clearing it.  R1b therefore runs in THREE
# NEW roots -- r1b_coarse, r1b_medium, r1b_fine -- registered by name in the
# pre-registration section 4a as directories that DO NOT EXIST at registration time.
#
# NEW IN R1b (b): THE MESH IS PINNED BY sha256, NOT MERELY INHERITED BY ASSERTION.
# Staging new roots introduces a failure mode R1 did not have -- copying the WRONG mesh --
# so the forced change carries its own guard.  Each new root is staged from its R1
# counterpart's 0.orig/, constant/ and system/, and every one of the eight files below
# is sha256'd AFTER THE COPY against a value pinned in the pre-registration.  A mismatch
# is a refusal.  This pins the mesh family harder than R1 did; it moves no gate.
# =====================================================================================

CASES_DIR=/home/ubuntu/Certonomous/cases/navier_class/SUBOFF
RUNS_DIR=/home/ubuntu/Certonomous/verification/runs/navier_class/SUBOFF

GRADER="$CASES_DIR/grade_suboff.py"
BUILDER="$CASES_DIR/build_suboff.py"
PREREG=/home/ubuntu/Certonomous/verification/campaign/SUBOFF_R1b_PREREGISTRATION.md
OPENFOAM_BASHRC=/usr/lib/openfoam/openfoam2606/etc/bashrc

# Registered in SUBOFF_R1b_PREREGISTRATION.md sections 5a and 7.  Transcribed, not invented.
# endTime/deltaT/ranks are INHERITED FROM R1 UNCHANGED.  Only the caps move.
ENDTIME_REGISTERED=2500
DELTAT_REGISTERED=1
RANKS=1
CAP_COREMIN_REGISTERED=400
CAP_CORESEC_REGISTERED=24000           # 400 * 60 / 1 rank

LEVELS=(coarse medium fine)            # coarse -> fine, the registered order
declare -A CASEOF=( [coarse]="$RUNS_DIR/r1b_coarse" \
                    [medium]="$RUNS_DIR/r1b_medium" \
                    [fine]="$RUNS_DIR/r1b_fine" )
declare -A SRCOF=(  [coarse]="$RUNS_DIR/reg_coarse" \
                    [medium]="$RUNS_DIR/reg_medium" \
                    [fine]="$RUNS_DIR/reg_fine" )
# Section 7 of the R1b pre-registration.  sub_cap = ceil(projection x 1.75).
declare -A SUBCAP_COREMIN=( [coarse]=46  [medium]=103  [fine]=231  )
declare -A TIMEOUT_S=(      [coarse]=2760 [medium]=6180 [fine]=13860 )  # sub_cap * 60 / RANKS

# Section 4a MESH PIN.  sha256 of the staged file, asserted AFTER the copy.
STAGED_FILES=(0.orig/U 0.orig/k 0.orig/nut 0.orig/omega 0.orig/p \
              constant/polyMesh/points constant/polyMesh/faces constant/polyMesh/owner \
              constant/polyMesh/neighbour constant/polyMesh/boundary \
              system/controlDict system/fvSolution system/fvSchemes)
declare -A PIN=(
  [coarse:constant/polyMesh/points]=88803d7a7aeff8b58a505d3b1640a2c9bdbd7c50f866884c24fb679f6a30512e
  [coarse:constant/polyMesh/faces]=117b09b3811f898e735c2accf068f33a4dd8e24289a82ecd8ca4de4969bfd7b8
  [coarse:constant/polyMesh/owner]=424790aafab345aa73a34444373137706a5b590d612b91014353769a7ba84957
  [coarse:constant/polyMesh/neighbour]=3721a50482435dd1dc22edc0189caa0811d3bfae3f94305b48f9e3c6e64795c4
  [coarse:constant/polyMesh/boundary]=7def99e69483e8f60b2dba179185ba32cf1a0187e40350314a151a16464c2a74
  [medium:constant/polyMesh/points]=125f7f6e9233ee3e6da450a06b3e9a133af3f06da06edb3c46264bc3679f88e4
  [medium:constant/polyMesh/faces]=11a86ed8b66c0e537c89c4acc3a9b02b9bb7203680dbb558f209f9185f485d08
  [medium:constant/polyMesh/owner]=2f3a7df3eb61359181ea5da9d2533b91f252cd69a3107352d1880c6e13f0faee
  [medium:constant/polyMesh/neighbour]=d2b913b7912b41f58f9ec8f2770b452a841ed650192eb18d951c71b5819c3688
  [medium:constant/polyMesh/boundary]=9d7352bfc94858d9ba4757ad24f1af201702d251bcfc82a2c79a408942596ef5
  [fine:constant/polyMesh/points]=fd720d27f98133ba71a8e2dba9d4ac7d02ac5e5713d2e251d90f251544ef0f49
  [fine:constant/polyMesh/faces]=d945be9f87c99821c62d2add85054cd1b91348ecae9903c745b30c468f32330e
  [fine:constant/polyMesh/owner]=f261ace8021ab386b087d44368b098d932e53f56cf349473565393b89c26acdc
  [fine:constant/polyMesh/neighbour]=b21bebd31dd6b2e667475577646fb6738af84f5c78e5b3b620ff88b9aa2baf9d
  [fine:constant/polyMesh/boundary]=957e432b7a6f62def9c165ce1c3e4c73766509d825d3e8fae6921905cc906f49
)
# controlDict / fvSolution / fvSchemes are BYTE-IDENTICAL across all three levels (that
# identity is the mechanical proof of the pinned-Aref and single-endTime rulings), so
# they are pinned once, not per level.
SHA_CONTROLDICT=f002ab4a10625dbbd888320e63cdc63af15420927d8246594a7156d2965649c8
SHA_FVSOLUTION=f9a35242200934b3c0d82b8384a3a1b6902f711f9863ad7d25f7989f5c1aa997
SHA_FVSCHEMES=62fc76f764ad4ac47f6329242821781e19900df4cf61cf2041d3075d40d0bef4

USED_CORESEC=0
PROGRESS="$RUNS_DIR/PROGRESS.R1b_triple.txt"
VERDICT="$RUNS_DIR/VERDICT.R1b_triple.txt"

say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$PROGRESS"; }

# -------------------------------------------------------------------------------------
# THE VERDICT GUARANTEE.  DEFECT 2, closed structurally.
# -------------------------------------------------------------------------------------
# write_verdict() is the ONLY writer of $VERDICT and it writes at most once (VERDICT_WRITTEN
# latches).  The EXIT trap fires on every termination path bash can observe -- normal exit,
# refusal, `exit` from a subshell-free path, SIGTERM, SIGINT, SIGHUP -- and writes a
# NOT A RESULT if nothing else got there first.  There is therefore NO WAY to run this
# launcher and end with no verdict on disk.  The vocabulary is the fixed one
# (CLAUDE.md rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
VERDICT_WRITTEN=0
write_verdict() {
  if [ "$VERDICT_WRITTEN" -ne 0 ]; then return 0; fi
  VERDICT_WRITTEN=1
  {
    echo "SUBOFF R1b -- LAUNCHER VERDICT ARTIFACT"
    echo "written_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "prereg=$PREREG"
    echo "grader=$GRADER"
    echo "verdict=$1"
    echo "reason=$2"
    echo "spent_core_min=$(awk -v c=$USED_CORESEC 'BEGIN{printf "%.2f", c/60}') of registered cap $CAP_COREMIN_REGISTERED"
    echo "--"
    echo "This artifact is written UNCONDITIONALLY by run_suboff_r1b_triple.sh, including"
    echo "from its EXIT trap.  A launch of this script that produced no verdict is not a"
    echo "possible outcome; if this file is absent, the script never started."
    echo "A verdict here that is not PASS/GATE FAIL came from the LAUNCHER, not the grader."
    echo "Grader stdout, when the grader ran, is in $RUNS_DIR/grade.R1b_triple.out"
  } > "$VERDICT"
  sync "$VERDICT" 2>/dev/null
}
on_exit() {
  write_verdict "NOT A RESULT" \
    "launcher terminated without reaching its grading tail (signal, kill, or an unhandled path). No graded triple exists. This line was written by the EXIT trap."
}
trap on_exit EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
trap 'exit 129' HUP

refuse() {
  echo "REFUSED: $*" >&2
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] REFUSED: $*" >> "$PROGRESS" 2>/dev/null
  write_verdict "BLOCKED" "preflight refusal: $*"
  exit 2
}

for arg in "$@"; do
  case "$arg" in
    --help|-h) sed -n '1,60p' "$0"; VERDICT_WRITTEN=1; exit 0 ;;
    *) refuse "unknown argument '$arg' -- this launcher takes NO arguments. There is deliberately NO --grade flag and NO --no-grade flag: grading is unconditional (DEFECT 2)." ;;
  esac
done

# -------------------------------------------------------------------------------------
# PREFLIGHT.  Everything that can refuse, refuses BEFORE any level starts.
# -------------------------------------------------------------------------------------
if [ ! -f "$GRADER" ];  then refuse "pinned grader missing: $GRADER"; fi
if [ ! -f "$BUILDER" ]; then refuse "pinned builder missing: $BUILDER"; fi
if [ ! -f "$PREREG" ];  then refuse "pre-registration missing: $PREREG"; fi
if [ ! -f "$OPENFOAM_BASHRC" ]; then refuse "OpenFOAM bashrc missing: $OPENFOAM_BASHRC"; fi
if [ -e "$VERDICT" ]; then refuse "$VERDICT already exists -- this rung has already produced a verdict artifact. Refusing; nothing is deleted. Inspect it, do not clear it."; fi

GRADER_SHA=$(sha256sum "$GRADER"  | cut -d' ' -f1)
BUILDER_SHA=$(sha256sum "$BUILDER" | cut -d' ' -f1)
PREREG_SHA=$(sha256sum "$PREREG"  | cut -d' ' -f1)

# The SOURCE roots must still hold the R1 mesh, and the TARGET roots must not exist.
for L in "${LEVELS[@]}"; do
  S="${SRCOF[$L]}"
  C="${CASEOF[$L]}"
  if [ ! -d "$S/constant/polyMesh" ]; then refuse "$L: mesh source $S/constant/polyMesh absent -- R1b stages its mesh from the R1 root and does not rebuild."; fi
  if [ ! -d "$S/0.orig" ];            then refuse "$L: mesh source $S/0.orig absent"; fi
  if [ -e "$C" ]; then refuse "$L: registered R1b run root $C ALREADY EXISTS. Section 4a registers it as a directory that does not exist. Refusing; nothing is deleted. Inspect it, do not clear it."; fi
done

# The global cap must be able to cover the sub-caps this run intends to spend.
PLANNED=0
for L in "${LEVELS[@]}"; do PLANNED=$(( PLANNED + SUBCAP_COREMIN[$L] )); done
if [ "$PLANNED" -gt "$CAP_COREMIN_REGISTERED" ]; then refuse "planned sub-caps total ${PLANNED} core-min > the ONE registered cap ${CAP_COREMIN_REGISTERED} (section 7). An overrun stops the run; it does not get a new budget."; fi

# ---- STAGE THE THREE ROOTS, THEN ASSERT THE MESH PIN ON WHAT LANDED. -----------------
for L in "${LEVELS[@]}"; do
  S="${SRCOF[$L]}"
  C="${CASEOF[$L]}"
  mkdir -p "$C" || refuse "$L: mkdir $C failed"
  cp -r "$S/0.orig"  "$C/0.orig"  || refuse "$L: cp 0.orig from $S failed"
  cp -r "$S/constant" "$C/constant" || refuse "$L: cp constant from $S failed"
  cp -r "$S/system"  "$C/system"  || refuse "$L: cp system from $S failed"

  for F in constant/polyMesh/points constant/polyMesh/faces constant/polyMesh/owner \
           constant/polyMesh/neighbour constant/polyMesh/boundary; do
    if [ ! -f "$C/$F" ]; then refuse "$L: staged file missing: $C/$F"; fi
    GOT=$(sha256sum "$C/$F" | cut -d' ' -f1)
    WANT="${PIN[$L:$F]}"
    if [ "$GOT" != "$WANT" ]; then refuse "$L: MESH PIN MISMATCH on $F -- staged sha256 $GOT, section-4a pinned $WANT. The mesh that landed is NOT the registered mesh. Refusing; nothing is deleted."; fi
  done
  for PAIR in "system/controlDict:$SHA_CONTROLDICT" "system/fvSolution:$SHA_FVSOLUTION" "system/fvSchemes:$SHA_FVSCHEMES"; do
    F="${PAIR%%:*}"; WANT="${PAIR##*:}"
    if [ ! -f "$C/$F" ]; then refuse "$L: staged file missing: $C/$F"; fi
    GOT=$(sha256sum "$C/$F" | cut -d' ' -f1)
    if [ "$GOT" != "$WANT" ]; then refuse "$L: CONFIG PIN MISMATCH on $F -- staged sha256 $GOT, section-4a pinned $WANT. Refusing; nothing is deleted."; fi
  done
  say "$L: staged from $S; mesh + config sha256 pins ALL MATCH section 4a."
done

# ---- The rule-4 / age-guard pre-launch guards, on the staged roots. ------------------
for L in "${LEVELS[@]}"; do
  C="${CASEOF[$L]}"
  if [ ! -f "$C/0.orig/U" ];           then refuse "$L: 0.orig/U missing in $C -- the age guard needs 0/U"; fi
  if [ -e "$C/0" ];                    then refuse "$L: $C/0 already exists -- 0/ must be created BY THIS LAUNCHER at launch (age guard). Refusing; nothing is deleted."; fi
  if [ -e "$C/rc" ];                   then refuse "$L: $C/rc exists -- already launched. Refusing; nothing is deleted."; fi
  if [ -e "$C/log.simpleFoam" ];       then refuse "$L: $C/log.simpleFoam exists -- already launched. Refusing; nothing is deleted."; fi
  if [ -e "$C/postProcessing" ];       then refuse "$L: $C/postProcessing exists. Refusing; nothing is deleted."; fi
  DIRTY=$(find "$C" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]*)?' -printf '%f ')
  if [ -n "$DIRTY" ]; then refuse "$L: $C already holds numeric time director(ies): $DIRTY -- rule 4: a run is never launched into a tree that already holds an answer. Refusing; nothing is deleted."; fi

  ET=$(grep -m1 -oE '^endTime[[:space:]]+[0-9.eE+-]+' "$C/system/controlDict" | grep -oE '[0-9.eE+-]+$')
  DT=$(grep -m1 -oE '^deltaT[[:space:]]+[0-9.eE+-]+'  "$C/system/controlDict" | grep -oE '[0-9.eE+-]+$')
  if [ "$ET" != "$ENDTIME_REGISTERED" ]; then refuse "$L: controlDict endTime is '$ET', not the registered $ENDTIME_REGISTERED (INHERITED FROM R1 UNCHANGED). 50 is the SMOKE default and a graded run at 50 is NOT A RESULT by truncation."; fi
  if [ "$DT" != "$DELTAT_REGISTERED" ];  then refuse "$L: controlDict deltaT is '$DT', not the registered $DELTAT_REGISTERED -- rule-4 clause 5 is written for the unit step."; fi
  if grep -q 'residualControl' "$C/system/fvSolution"; then refuse "$L: system/fvSolution contains residualControl -- section 5 requires a HARD stop with NO early exit."; fi
done

if [ -z "${USER:-}" ]; then export USER=ubuntu; fi
# shellcheck disable=SC1090
. "$OPENFOAM_BASHRC" > /dev/null 2>&1
if ! command -v simpleFoam > /dev/null 2>&1; then refuse "simpleFoam not on PATH after sourcing $OPENFOAM_BASHRC"; fi
SIMPLEFOAM_BIN=$(command -v simpleFoam)

say "SUBOFF R1b graded triple -- PREFLIGHT PASSED on all three levels."
say "  endTime=$ENDTIME_REGISTERED deltaT=$DELTAT_REGISTERED ranks=$RANKS (INHERITED FROM R1 UNCHANGED)"
say "  cap=${CAP_COREMIN_REGISTERED} core-min; sub-caps ${SUBCAP_COREMIN[coarse]}/${SUBCAP_COREMIN[medium]}/${SUBCAP_COREMIN[fine]} core-min (R1b section 7, re-derived from the MEASURED CONTENDED rate)"
say "  grader  $GRADER  sha256 $GRADER_SHA"
say "  builder $BUILDER sha256 $BUILDER_SHA"
say "  prereg  $PREREG  sha256 $PREREG_SHA"
say "  simpleFoam $SIMPLEFOAM_BIN"
say "  GRADING IS UNCONDITIONAL. There is no grade flag. A verdict artifact is guaranteed at $VERDICT."

# -------------------------------------------------------------------------------------
# THE LEVELS.
# -------------------------------------------------------------------------------------
OVERALL=0
STOPNOTE=""
for L in "${LEVELS[@]}"; do
  C="${CASEOF[$L]}"
  TO="${TIMEOUT_S[$L]}"
  SUB="${SUBCAP_COREMIN[$L]}"

  WOULD=$(( USED_CORESEC + SUB * 60 / RANKS ))
  if [ "$WOULD" -gt "$CAP_CORESEC_REGISTERED" ]; then
    STOPNOTE="global cap stop before $L"
    say "CAP STOP: starting $L (sub-cap ${SUB} core-min) would take the rung to $(( WOULD / 60 )) core-min, past the ONE registered ${CAP_COREMIN_REGISTERED}. STOPPING. An overrun does not get a new budget."
    echo "cap_coremin_registered=$CAP_COREMIN_REGISTERED used_coresec=$USED_CORESEC stopped_before=$L" > "$RUNS_DIR/CAP_STOP.R1b_triple.txt"
    OVERALL=3
    break
  fi

  cp -r "$C/0.orig" "$C/0"
  CPRC=$?
  if [ "$CPRC" -ne 0 ]; then refuse "$L: cp -r 0.orig -> 0 failed rc=$CPRC in $C"; fi
  touch "$C/0"/*
  if [ ! -f "$C/0/U" ]; then refuse "$L: 0/U absent after the copy -- the age guard has nothing to date the run by"; fi
  ZERO_EPOCH=$(stat -c %Y "$C/0/U")
  say "$L: 0/ created from 0.orig/ at epoch $ZERO_EPOCH ($(date -u -d @"$ZERO_EPOCH" +%Y-%m-%dT%H:%M:%SZ)); the age guard dates this run from here."

  {
    echo "grader  $GRADER  sha256 $GRADER_SHA"
    echo "builder $BUILDER sha256 $BUILDER_SHA"
    echo "prereg  $PREREG  sha256 $PREREG_SHA"
    echo "launched_utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "endTime $ENDTIME_REGISTERED deltaT $DELTAT_REGISTERED ranks $RANKS"
    echo "subcap_core_min $SUB  wall_timeout_s $TO  (= subcap * 60 / ranks)"
    echo "cap_core_min_registered $CAP_COREMIN_REGISTERED (R1b section 7)"
    echo "mesh staged from ${SRCOF[$L]} ; section-4a sha256 pins asserted post-copy"
    echo "GRADED UNCONDITIONALLY BY THIS LAUNCHER. Verdict artifact: $VERDICT"
  } > "$C/GRADE_PATH.txt"

  say "$L: launching simpleFoam in $C -- timeout ${TO}s (sub-cap ${SUB} core-min at ranks $RANKS)"
  T0=$(date +%s)
  ( cd "$C" && timeout "${TO}s" simpleFoam -case "$C" ) > "$C/log.simpleFoam" 2>&1
  RC=$?
  T1=$(date +%s)
  printf 'rc=%d\n' "$RC" > "$C/rc"
  WALL=$(( T1 - T0 ))
  CORESEC=$(( WALL * RANKS ))
  USED_CORESEC=$(( USED_CORESEC + CORESEC ))

  {
    echo "level=$L"
    echo "case=$C"
    echo "rc=$RC"
    echo "rc_captured=inside_this_wrapper"
    echo "wall_s=$WALL"
    echo "ranks=$RANKS"
    echo "core_min=$(awk -v w=$WALL -v r=$RANKS 'BEGIN{printf "%.3f", w*r/60}')"
    echo "subcap_core_min=$SUB"
    echo "wall_timeout_s=$TO"
    echo "cap_core_min_registered=$CAP_COREMIN_REGISTERED"
    echo "used_core_min_so_far=$(awk -v c=$USED_CORESEC 'BEGIN{printf "%.3f", c/60}')"
    echo "zero_dir_epoch=$ZERO_EPOCH"
    echo "endTime_registered=$ENDTIME_REGISTERED"
    echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$C/STATUS.R1b_$L"
  sync "$C/rc" "$C/STATUS.R1b_$L" 2>/dev/null

  LASTTIME=$(grep '^Time = ' "$C/log.simpleFoam" | tail -1)
  NEXEC=$(grep -c '^ExecutionTime' "$C/log.simpleFoam")
  ENDLINE=$(grep -c '^End' "$C/log.simpleFoam")
  say "$L: rc=$RC wall=${WALL}s core-min=$(awk -v w=$WALL -v r=$RANKS 'BEGIN{printf "%.2f", w*r/60}') used=$(awk -v c=$USED_CORESEC 'BEGIN{printf "%.2f", c/60}')/${CAP_COREMIN_REGISTERED}"
  say "$L: last '$LASTTIME' ; ExecutionTime lines=$NEXEC (registered $ENDTIME_REGISTERED) ; End lines=$ENDLINE"

  if [ "$RC" -eq 124 ]; then
    STOPNOTE="$L hit its ${TO}s wall timeout (sub-cap ${SUB} core-min) at '$LASTTIME' of $ENDTIME_REGISTERED"
    say "$L: CAP BREACH -- simpleFoam hit its ${TO}s wall timeout (sub-cap ${SUB} core-min). The level is STOPPED at the core-minutes spent and gets NO new budget. The level is NOT complete and is NOT gradeable. R1b section 7 registered this outcome IN ADVANCE: it is answered by a re-registered successor, NEVER by extending a cap mid-run."
    echo "level=$L rc=124 wall_timeout_s=$TO subcap_core_min=$SUB last_time=$LASTTIME" > "$C/CAP_BREACH.txt"
    OVERALL=4
  elif [ "$RC" -ne 0 ]; then
    STOPNOTE="$L exited rc=$RC"
    say "$L: rc=$RC -- recorded, not softened. The level is NOT complete and is NOT gradeable. A crash is a FINDING until the supervisor's check-3 triage says otherwise."
    OVERALL=5
  fi

  if [ "$USED_CORESEC" -gt "$CAP_CORESEC_REGISTERED" ]; then
    STOPNOTE="global cap stop after $L"
    say "CAP STOP: the rung has spent $(awk -v c=$USED_CORESEC 'BEGIN{printf "%.2f", c/60}') core-min, past the ONE registered ${CAP_COREMIN_REGISTERED}. STOPPING before any further level."
    echo "cap_coremin_registered=$CAP_COREMIN_REGISTERED used_coresec=$USED_CORESEC stopped_after=$L" > "$RUNS_DIR/CAP_STOP.R1b_triple.txt"
    OVERALL=3
    break
  fi
done

say "TRIPLE FINISHED with launcher status $OVERALL; total spent $(awk -v c=$USED_CORESEC 'BEGIN{printf "%.2f", c/60}') core-min of the registered ${CAP_COREMIN_REGISTERED}."
say "Rule-12 estimate-vs-actual calibration against R1b section 7 (216.2 core-min projected for the triple) is OWED as a row in docs/COST_CALIBRATION.md."

# -------------------------------------------------------------------------------------
# THE GRADING TAIL.  UNCONDITIONAL.  NO FLAG GUARDS IT.
# -------------------------------------------------------------------------------------
if [ "$OVERALL" -ne 0 ]; then
  say "NOT GRADING: the triple did not finish clean (launcher status $OVERALL). A level that is not rule-4 complete is not gradeable and the grader would refuse (exit 2) anyway. The LAUNCHER writes the verdict instead, so this run still ends with one."
  write_verdict "NOT A RESULT" "$STOPNOTE (launcher status $OVERALL). No Roache triple can exist: rule 5 clause 1. Answered by a re-registered successor with its own pre-registration, never by extending a cap mid-run."
else
  say "GRADING with the pinned grader $GRADER (sha256 $GRADER_SHA). This is unconditional; no flag was needed and none exists."
  python3 "$GRADER" --coarse "${CASEOF[coarse]}" --medium "${CASEOF[medium]}" --fine "${CASEOF[fine]}" \
    > "$RUNS_DIR/grade.R1b_triple.out" 2>&1
  GRC=$?
  say "grade_suboff.py rc=$GRC ; stdout in $RUNS_DIR/grade.R1b_triple.out"
  if [ "$GRC" -eq 0 ]; then
    write_verdict "SEE GRADER OUTPUT" "grade_suboff.py exited 0, so it produced a verdict. The GRADED verdict is in $RUNS_DIR/grade.R1b_triple.out and is the one that counts; this artifact only records that grading ran and completed."
  elif [ "$GRC" -eq 2 ]; then
    write_verdict "NOT A RESULT" "grade_suboff.py REFUSED (exit 2) rather than degrade. See $RUNS_DIR/grade.R1b_triple.out for which input or planted control it refused on."
  else
    write_verdict "NOT A RESULT" "grade_suboff.py exited $GRC (70 = internal grader defect). See $RUNS_DIR/grade.R1b_triple.out."
  fi
  trap - EXIT
  exit "$GRC"
fi

trap - EXIT
exit "$OVERALL"
