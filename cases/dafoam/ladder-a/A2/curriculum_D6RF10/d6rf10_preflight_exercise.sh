#!/usr/bin/env bash
# =============================================================================
# curriculum D6RF10 -- THE §2bb / SIMPLEC PRE-FLIGHT MEASUREMENT run.
#
# PURPOSE: produce §2bb-valid per-step cost samples + the SIMPLEC
# `p_first_uncorrected` trajectory for the R2/R3/R4 configs, so the
# dafoam-supervisor can SIZE the R3/R4 deadlines and DECIDE their endTime
# (300 if the trajectory is flat by 300 outer iterations, else longer).
#
# THIS SCRIPT MEASURES. IT DOES NOT GRADE.
#   * It does NOT invoke `d6rf10_grade.py`, does NOT stage it, does NOT read the
#     frozen gate / floor / label, does NOT touch PREREGISTRATION.md or
#     PERMISSION. There is NO G-FREEZE limb here: the freeze is the graded run's
#     discipline (`d6rf10_run_arm.sh`), not a measurement's. No verdict is
#     declared by this script and none by its collector.
#   * It runs in a SEPARATE exercise root, never this item's registered graded
#     run root, so nothing it writes can be mistaken for a graded row.
#
# It reuses `d6rf10_run_arm.sh`'s PROVEN staging (flat P_conv topology + mp0X)
# INCLUDING the confound-(ii) `processor*`-strip at BOTH the staging half and the
# per-leg half -- the SIMPLEC path (DARhoSimpleCFoam) MUST decompose CLEAN, or it
# reproduces the D6RF9 `Case is already decomposed` rc=59 that made D6RF9 a
# CONFOUNDED NOT A RESULT. The endpoint is reconstructed once (endpoint_physical
# + units_assert) so the primal runs at the SAME design point D6RF7 measured; the
# per-leg driver is the byte-identical `d6rf10_run_leg.py`, so the log carries the
# SAME `Time =`, `ExecutionTime =` and `p initRes: ... finalRes: ... nIters:`
# lines the frozen grader parses -- but here they are read by the COLLECTOR
# (`d6rf10_preflight_collect.sh`), which declares no verdict and sizes no
# deadline.
#
# SELF-DETACH (same pattern as d6rf10_run_arm.sh): the plain command
# `bash cases/dafoam/ladder-a/A2/curriculum_D6RF10/d6rf10_preflight_exercise.sh`
# re-execs THIS script under setsid, fully detached; the exercise's rc/verdict is
# captured INSIDE the child by `docker inspect .State.ExitCode` per smoke and the
# `D6RF10_PREFLIGHT_DONE` ledger line -- NOT by the parent's `exit 0` (L "setsid
# parent returns zero"). The `docker run -d` containers survive fleet death; the
# self-setsid keeps the poll/log loop alive across it too.
#
# COST (rule 12): three smokes, each capped at PER_SMOKE_CAP_CORE_MIN=120 -- a
# smoke that has not reached endTime by its deadline is STOPPED (timeout -k rc
# 124) and its PARTIAL trajectory is still a measurement. Cumulative estimate is
# documented in the launch echo; every smoke is a CPU run under $25 (pre-authorised).
# =============================================================================
set -u
set -o pipefail

# --- SELF-DETACH (operational; identical pattern to d6rf10_run_arm.sh) --------
if [ -z "${D6RF10_PREFLIGHT_DETACHED:-}" ]; then
  export D6RF10_PREFLIGHT_DETACHED=1
  D6RF10_PREFLIGHT_OUT="/home/ubuntu/certonomous-runs/d6rf10_preflight_launch_$(date -u +%Y%m%dT%H%M%SZ)_$$.out"
  export D6RF10_PREFLIGHT_OUT
  setsid bash "$0" "$@" > "$D6RF10_PREFLIGHT_OUT" 2>&1 < /dev/null &
  echo "D6RF10_PREFLIGHT_DETACHED child_pid=$! launch_out=$D6RF10_PREFLIGHT_OUT"
  echo "  measurement only -- NO grading, NO frozen gate; per-smoke rc via docker inspect,"
  echo "  exercise completion via the D6RF10_PREFLIGHT_DONE ledger line (not this exit 0)."
  exit 0
fi
# re-exec'd child: record the script's OWN final rc to the launch OUT at the end.
trap '_pf_rc=$?; echo "PREFLIGHT_RC=$_pf_rc" >> "${D6RF10_PREFLIGHT_OUT:-/dev/null}"' EXIT

ITEM=D6RF10
ARM=P_conv
RANKS=4

REPO=/home/ubuntu/Certonomous
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNS_DIR=/home/ubuntu/certonomous-runs
# The registered SOURCE the primal state is staged from (D6RF7's own run root:
# base mesh + mp04/05/06 + OptView endpoint), READ-ONLY -- identical to run_arm.
SRC_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF7-a2-wing-convergence-probe
D6RF7_DIR=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6RF7
# FIXED exercise root -- SEPARATE from the graded run root, so the collector and
# the supervisor find it at a stable path and no measurement pollutes a graded row.
EXERCISE_BASE=/home/ubuntu/certonomous-runs/D6RF10-PREFLIGHT-EXERCISE

# ---- caps (rule 12). Each smoke reaches endTime 300 under both the optimistic-
# ---- plateau and the pure-quadratic D6RF9 escalation model within 120 core-min;
# ---- if a smoke has NOT reached endTime by its deadline it is STOPPED (rc 124)
# ---- and its partial trajectory is reported -- no new budget.
PER_SMOKE_CAP_CORE_MIN=120
FRAME_ALLOWANCE_S=90
KILL_GRACE_S=60
MEM=20g
CPUSET=4,5,11,12
IMG=dafoam-idwarp-rot:v1
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35

# ---- the three smokes (MEASUREMENT configs; endTime 300, writeInterval 20) ----
# leg  solver             nNonOrth  relax_p  relax_eqn  endTime  writeInterval
#  R2  DARhoSimpleFoam    12        0.30     0.70       300      20
#  R3  DARhoSimpleCFoam   12        0.70     0.70       300      20
#  R4  DARhoSimpleCFoam   12        0.15     0.50       300      20
# endTime 300 (NOT 50-100): the per-step cost ESCALATES, so an early sample
# under-sizes the deadline, and the plateau question the supervisor must answer
# is "flat by 300?". writeInterval 20 -> 15 field writes across 300 steps, and
# the per-iteration `Time =`/`ExecutionTime =` lines give >=10 samples for the
# late-window per-step estimate (§2bb n_steps_sampled >= 5). writeInterval does
# NOT gate the `Time =` cadence (that is per outer iteration); it guarantees the
# run writes developed-field snapshots so the measurement is complete.
smoke_solver()   { case "$1" in R2) echo DARhoSimpleFoam ;; R3|R4) echo DARhoSimpleCFoam ;; *) echo "" ;; esac; }
smoke_nnonorth() { case "$1" in R2|R3|R4) echo 12 ;; *) echo "" ;; esac; }
smoke_relaxp()   { case "$1" in R2) echo 0.30 ;; R3) echo 0.70 ;; R4) echo 0.15 ;; *) echo "" ;; esac; }
smoke_relaxeqn() { case "$1" in R2|R3) echo 0.70 ;; R4) echo 0.50 ;; *) echo "" ;; esac; }
smoke_endtime()  { case "$1" in R2|R3|R4) echo 300 ;; *) echo "" ;; esac; }
smoke_writeint() { case "$1" in R2|R3|R4) echo 20 ;; *) echo "" ;; esac; }

# frozen instrument md5 fixpoints (verified before staging; the SAME frozen
# d6rf7_* carries the graded run uses -- measurement runs the identical primal).
MD5_RUNSCRIPT=137539e0a99be27f27fdb69e063b2a87
MD5_FVSCHEMES_LIMITED=8374443e7a374e9d353cffccdb654aaf
MD5_FVSOL=67fed3c2ffd2765e51f2563270060648
MD5_UNITS=34f477f92b23e27896b458475eef0f78
MD5_ENDPOINT_PHYS=625bacf5b1489989f9a2638dd99e2e52
MD5_LOCUS=341189ca866f302a7e1bba8eefad3a57
MD5_EXTRACT=baedb673e9c88291f6724794681bc9a7
MD5_OPTVIEW=70fafa07bdee618fef13039433c01114
# instrument path -> pin. NOTE: d6rf10_grade.py and d6rf10_accept_floor_control.py
# are DELIBERATELY ABSENT -- this exercise does not grade. d6rf10_run_leg.py's own
# md5 is left to the driver's internal RUNSCRIPT_MD5 self-check (it verifies the
# runScript it execs); it is staged by existence, not pinned here.
declare -A INSTR_MD5=(
  [d6rf7_opt_runScript.py]=$MD5_RUNSCRIPT
  [d6rf7_fvSchemes_LIMITED]=$MD5_FVSCHEMES_LIMITED
  [d6rf7_fvSolution]=$MD5_FVSOL
  [d6rf7_units_assert.py]=$MD5_UNITS
  [d6rf7_endpoint_physical.py]=$MD5_ENDPOINT_PHYS
  [d6rf7_endpoint_locus.py]=$MD5_LOCUS
  [d6rf7_extract_endpoint.py]=$MD5_EXTRACT
)

# =============================================================================
# G-ROOT (measurement variant): fresh root, never the source, never the graded
# run root, never another item's root, no live pid rooted here.
# =============================================================================
BASE_REAL=$(realpath -m "$EXERCISE_BASE")
SRC_REAL=$(realpath -m "$SRC_ROOT")
GRADED_REAL=$(realpath -m "$RUNS_DIR/CURRICULUM-D6RF10-a2-wing-convergence-probe")
if [ "$BASE_REAL" = "$SRC_REAL" ]; then
  echo "ABORT G-ROOT exercise base resolves to the READ-ONLY SOURCE $SRC_REAL"; exit 3; fi
if [ "$BASE_REAL" = "$GRADED_REAL" ]; then
  echo "ABORT G-ROOT exercise base resolves to the GRADED run root $GRADED_REAL (measurement must not pollute it)"; exit 3; fi
if [ -d "$RUNS_DIR" ]; then
  while IFS= read -r forb; do
    [ -z "$forb" ] && continue
    [ "$forb" = "$BASE_REAL" ] && continue
    if [ "$BASE_REAL" = "$forb" ]; then
      echo "ABORT G-ROOT exercise base resolves to ANOTHER item's run root: $forb"; exit 3; fi
  done <<< "$(find "$RUNS_DIR" -maxdepth 1 -mindepth 1 -type d -exec realpath -m {} \; 2>/dev/null)"
fi
if [ -e "$BASE_REAL" ]; then
  echo "ABORT G-ROOT $BASE_REAL already exists. A re-run needs the prior exercise root ARCHIVED by mv, not deleted here."; exit 3; fi
LIVE_HERE=""
for pid in $(ls /proc 2>/dev/null | grep -E '^[0-9]+$'); do
  cwd=$(readlink -f "/proc/$pid/cwd" 2>/dev/null) || continue
  case "$cwd" in "$BASE_REAL"|"$BASE_REAL"/*) LIVE_HERE="$LIVE_HERE $pid" ;; esac
done
[ -z "$LIVE_HERE" ] || { echo "ABORT G-ROOT live pid(s) [$LIVE_HERE] rooted at $BASE_REAL"; exit 3; }
echo "D6RF10_PREFLIGHT_G_ROOT_PASS base=$BASE_REAL fresh=yes no_live_pid=yes"

# =============================================================================
# STAGING (reuses d6rf10_run_arm.sh's FLAT topology + confound-(ii) strip).
# =============================================================================
test -d "$SRC_REAL" || { echo "ABORT staging: source $SRC_REAL absent"; exit 5; }
mkdir -p "$BASE_REAL" || { echo "ABORT staging: could not create fresh exercise root"; exit 4; }
WORK="$BASE_REAL/$ARM"
mkdir -p "$WORK"
# primary case dirs, FLAT at WORK, from $SRC/$ARM (the proven D6RF7 topology).
for d in system constant 0 0.orig FFD mp04 mp05 mp06; do
  [ -d "$SRC_REAL/$ARM/$d" ] || { echo "ABORT staging: primary case dir $SRC_REAL/$ARM/$d absent"; exit 5; }
  cp -a "$SRC_REAL/$ARM/$d" "$WORK/$d" || { echo "ABORT staging: copy of primary case dir $d failed"; exit 5; }
done
# CONFOUND-(ii) STRIP, staging half: the D6RF7 source mp0X carry stale processor*
# dirs; strip so the SIMPLEC path decomposes CLEAN (no D6RF9 rc=59 collision).
for d in . mp04 mp05 mp06; do
  rm -rf "$WORK/$d"/processor* 2>/dev/null || true
done
if ls -d "$WORK"/processor* "$WORK"/mp0*/processor* >/dev/null 2>&1; then
  echo "ABORT staging: stale processor* dirs remain under WORK after strip (confound ii not removed)"; exit 5
fi
echo "D6RF10_PREFLIGHT_PROCDIRS_STRIPPED_STAGING no processor* under WORK or mp04/mp05/mp06"
# OptView.hst (the endpoint-defining optimisation history), md5-pinned.
if [ -f "$SRC_REAL/$ARM/OptView.hst" ]; then OPTVIEW_SRC="$SRC_REAL/$ARM/OptView.hst"
elif [ -f "$SRC_REAL/OptView.hst" ]; then OPTVIEW_SRC="$SRC_REAL/OptView.hst"
else echo "ABORT staging: OptView.hst absent -- no endpoint to reconstruct"; exit 5; fi
OPTVIEW_SRC_MD5=$(md5sum "$OPTVIEW_SRC" | cut -d' ' -f1)
[ "$OPTVIEW_SRC_MD5" = "$MD5_OPTVIEW" ] || { echo "ABORT staging: OptView.hst md5 $OPTVIEW_SRC_MD5 != pinned $MD5_OPTVIEW"; exit 5; }
cp -a "$OPTVIEW_SRC" "$WORK/OptView.hst" || { echo "ABORT staging: OptView.hst copy failed"; exit 5; }
echo "D6RF10_PREFLIGHT_OPTVIEW_STAGED md5=$MD5_OPTVIEW"
# verify + stage the frozen instruments (grader/accept-floor DELIBERATELY absent).
for f in "${!INSTR_MD5[@]}"; do
  pin="${INSTR_MD5[$f]}"; src="$D6RF7_DIR/$f"
  [ -f "$src" ] || { echo "ABORT staging: instrument source absent: $src"; exit 4; }
  got=$(md5sum "$src" | cut -d' ' -f1)
  [ "$got" = "$pin" ] || { echo "ABORT staging: $f md5 $got != frozen $pin"; exit 4; }
  cp -a "$src" "$WORK/$f" || { echo "ABORT staging copy failed: $f"; exit 4; }
done
# the per-leg driver (byte-identical D6RF7-derived); md5-self-checked at runtime.
[ -f "$HERE/d6rf10_run_leg.py" ] || { echo "ABORT staging: d6rf10_run_leg.py absent in $HERE"; exit 4; }
cp -a "$HERE/d6rf10_run_leg.py" "$WORK/d6rf10_run_leg.py" || { echo "ABORT staging: run_leg copy failed"; exit 4; }
echo "D6RF10_PREFLIGHT_INSTRUMENTS_STAGED n=$((${#INSTR_MD5[@]}+1)) grader_absent=yes"

# path-existence fixpoint before any container.
PF_OK=yes
for need in \
  "$WORK/d6rf7_opt_runScript.py" "$WORK/d6rf10_run_leg.py" \
  "$WORK/d6rf7_fvSchemes_LIMITED" "$WORK/d6rf7_fvSolution" \
  "$WORK/d6rf7_endpoint_physical.py" "$WORK/d6rf7_units_assert.py" \
  "$WORK/OptView.hst"; do
  [ -f "$need" ] || { echo "ABORT path-existence fixpoint: $need is not on disk"; PF_OK=no; }
done
[ -d "$WORK/system" ] || { echo "ABORT path-existence fixpoint: top-level $WORK/system absent"; PF_OK=no; }
for d in mp04 mp05 mp06; do
  [ -d "$WORK/$d/system" ] || { echo "ABORT path-existence fixpoint: $WORK/$d/system absent"; PF_OK=no; }
done
[ "$PF_OK" = "yes" ] || { echo "ABORT path-existence fixpoint FAILED before any smoke."; exit 5; }
echo "D6RF10_PREFLIGHT_PATH_FIXPOINT_OK"

# --- image identity by DIGEST (mirror run_arm) -------------------------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
test "$GOT_DIGEST" = "$IMG_PATCHED_DIGEST" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$IMG_PATCHED_DIGEST"; exit 4; }
echo "D6RF10_PREFLIGHT_G_ROW_PASS digest=$GOT_DIGEST"

# =============================================================================
# install_config (MEASUREMENT variant): identical to d6rf10_run_arm.sh's, PLUS a
# writeInterval install ($8) so developed-field snapshots land. SIMPLE-scope
# nNonOrth only; (p|p_rgh) + equations relaxation; controlDict endTime +
# writeControl timeStep + writeInterval. REFUSES on a zero-site install.
# =============================================================================
read -r -d '' INSTALL_FN <<'FNEOF' || true
install_config() {   # $1=leg $2=solver $3=nNonOrth $4=relax_p $5=relax_eqn $6=endTime $7=fvSchemesMd5 $8=writeInterval
  n=0
  for sd in system mp04/system mp05/system mp06/system; do
    [ -f "$sd/fvSolution" ] || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 no fvSolution at $sd"; return 5; }
    [ -f "$sd/controlDict" ] || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 no controlDict at $sd"; return 5; }
    cp -a d6rf7_fvSchemes_LIMITED "$sd/fvSchemes" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 fvSchemes install failed at $sd"; return 5; }
    got=$(md5sum "$sd/fvSchemes" | cut -d' ' -f1)
    [ "$got" = "$7" ] || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 fvSchemes post-image $got != $7 at $sd"; return 5; }
    awk -v v="$3" 'BEGIN{b=0} /^SIMPLE/{b=1} b&&/nNonOrthogonalCorrectors/{sub(/[0-9]+;/, v";")} /^}/{if(b)b=0} {print}' "$sd/fvSolution" > "$sd/fvSolution.t1" && mv "$sd/fvSolution.t1" "$sd/fvSolution" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 nNonOrth set failed at $sd"; return 5; }
    grep -qE "nNonOrthogonalCorrectors[[:space:]]+$3;" "$sd/fvSolution" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 nNonOrthogonalCorrectors $3 not set at $sd"; return 5; }
    awk -v v="$4" '/\(p\|p_rgh\)/{sub(/[0-9.]+;/, v";")} {print}' "$sd/fvSolution" > "$sd/fvSolution.t2" && mv "$sd/fvSolution.t2" "$sd/fvSolution" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 relax_p set failed at $sd"; return 5; }
    awk -v v="$5" '/\(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega\)/{sub(/[0-9.]+;/, v";")} {print}' "$sd/fvSolution" > "$sd/fvSolution.t3" && mv "$sd/fvSolution.t3" "$sd/fvSolution" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 relax_eqn set failed at $sd"; return 5; }
    grep -qE "\(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega\)\"?[[:space:]]+$5;" "$sd/fvSolution" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 relax_eqn $5 not set at $sd"; return 5; }
    grep -qE "\(p\|p_rgh\)\"?[[:space:]]+$4;" "$sd/fvSolution" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 relax_p $4 not set at $sd"; return 5; }
    awk -v v="$6" '/^endTime/{$0="endTime         "v";"} {print}' "$sd/controlDict" > "$sd/controlDict.t1" && mv "$sd/controlDict.t1" "$sd/controlDict" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 endTime set failed at $sd"; return 5; }
    grep -qE "^endTime[[:space:]]+$6;" "$sd/controlDict" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 endTime $6 not set at $sd"; return 5; }
    awk '/^writeControl/{$0="writeControl    timeStep;"} {print}' "$sd/controlDict" > "$sd/controlDict.t2" && mv "$sd/controlDict.t2" "$sd/controlDict" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 writeControl set failed at $sd"; return 5; }
    awk -v v="$8" '/^writeInterval/{$0="writeInterval   "v";"} {print}' "$sd/controlDict" > "$sd/controlDict.t3" && mv "$sd/controlDict.t3" "$sd/controlDict" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 writeInterval set failed at $sd"; return 5; }
    grep -qE "^writeInterval[[:space:]]+$8;" "$sd/controlDict" || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 writeInterval $8 not set at $sd"; return 5; }
    n=$((n+1))
  done
  [ "$n" -ge 1 ] || { echo "D6RF10_PREFLIGHT_LEG_ABORT leg=$1 installed ZERO sites"; return 5; }
  echo "D6RF10_PREFLIGHT_CONFIG_INSTALLED leg=$1 endTime=$6 writeInterval=$8 solverName=$2 relax_p=$4 relax_eqn=$5 nNonOrthogonalCorrectors=$3 sites=$n"
  return 0
}
FNEOF

# =============================================================================
# SETUP CONTAINER -- reconstruct the endpoint DVs ONCE, so every smoke's primal
# runs at the SAME design point D6RF7 measured (identical to run_arm's setup).
# =============================================================================
AGE_DATUM=$(date -u +%s.%N)   # fractional part REQUIRED (endpoint_physical C3 refuses a truncated datum)
echo "$AGE_DATUM" > "$WORK/.d6rf10_age_datum"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$

run_container() {   # $1 = cmd file (relative to WORK), $2 = name, $3 = deadline_s -> echoes rc
  local cmdfile="$1" name="$2" tmo="$3"
  sudo -n docker run -d --name "$name" \
      --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
      -v "$BASE_REAL":/mnt -w "/mnt/$(basename "$WORK")" "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
       timeout -k $KILL_GRACE_S $tmo bash /mnt/$(basename "$WORK")/$cmdfile" > /dev/null 2>&1 \
    || { echo "125"; return 0; }
  while [ "$(sudo -n docker inspect --format '{{.State.Running}}' "$name" 2>/dev/null)" = "true" ]; do sleep 10; done
  local rc; rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$name" 2>/dev/null)
  test -n "$rc" || rc=125
  echo "$rc"
}

SETUP_CMD="$WORK/d6rf10_preflight_setup_cmd.sh"
{
  echo "set -o pipefail"
  echo "python d6rf7_endpoint_physical.py --age-datum $AGE_DATUM && \\"
  echo "python d6rf7_units_assert.py d6rf7_endpoint_dvs.json --runscript d6rf7_opt_runScript.py"
} > "$SETUP_CMD"
SETUP_TMO=$(python3 -c "print(int(round(30*60.0/$RANKS)) - $FRAME_ALLOWANCE_S)")
echo "D6RF10_PREFLIGHT_SETUP_CONTAINER reconstruct endpoint DVs (deadline_s=$SETUP_TMO)"
SETUP_RC=$(run_container "d6rf10_preflight_setup_cmd.sh" "d6rf10_pf_setup_${STAMP}" "$SETUP_TMO")
sudo -n docker logs "d6rf10_pf_setup_${STAMP}" > "$BASE_REAL/preflight_setup_${STAMP}.log" 2>&1
sudo -n docker rm "d6rf10_pf_setup_${STAMP}" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$BASE_REAL" 2>/dev/null
[ "$SETUP_RC" = "0" ] || { echo "ABORT setup container rc=$SETUP_RC (endpoint reconstruction / units gate failed)"; exit 4; }
[ -f "$WORK/d6rf7_endpoint_dvs.json" ] || { echo "ABORT the endpoint DV file was not produced by the setup container"; exit 5; }
echo "D6RF10_PREFLIGHT_ENDPOINT_READY d6rf7_endpoint_dvs.json present"

# =============================================================================
# THE THREE SMOKES (R2, R3, R4). One container each; MEASUREMENT only -- NO grade
# call. Per-leg: strip processor* (confound-(ii) per-leg half), install_config
# (incl. writeInterval), then mpirun the byte-identical driver so the log carries
# the Time / ExecutionTime / `p initRes:` lines the collector reads.
# =============================================================================
LEDGER="$BASE_REAL/preflight_ledger.txt"
echo "ITEM=$ITEM EXERCISE=preflight arm=$ARM" > "$LEDGER"
CUM_CORE_MIN=0

leg_cmd_file() {   # $1=cmdpath $2=leg $3=solver $4=nnonorth $5=relaxp $6=relaxeqn $7=endtime $8=writeint
  {
    printf '%s\n' "$INSTALL_FN"
    echo "set -o pipefail"
    # CONFOUND-(ii) per-leg strip -- SIMPLEC decomposes FRESH.
    echo "rm -rf processor* mp04/processor* mp05/processor* mp06/processor* 2>/dev/null || true"
    echo "install_config $2 $3 $4 $5 $6 $7 $MD5_FVSCHEMES_LIMITED $8 && \\"
    echo "mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH \\"
    echo "  python d6rf10_run_leg.py --leg-tag $2 --solver $3 --runscript d6rf7_opt_runScript.py --endpoint-dvs d6rf7_endpoint_dvs.json"
  } > "$1"
}

DEADLINE=$(python3 -c "print(int(round($PER_SMOKE_CAP_CORE_MIN*60.0/$RANKS)) - $FRAME_ALLOWANCE_S)")
test "$DEADLINE" -gt 0 || { echo "ABORT deadline<=0 at cap=$PER_SMOKE_CAP_CORE_MIN"; exit 65; }

for SM in R2 R3 R4; do
  SOL=$(smoke_solver "$SM"); NNO=$(smoke_nnonorth "$SM")
  RP=$(smoke_relaxp "$SM"); RE=$(smoke_relaxeqn "$SM")
  ET=$(smoke_endtime "$SM"); WI=$(smoke_writeint "$SM")
  RSTAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
  LOG="$BASE_REAL/${SM}_smoke_${RSTAMP}.log"
  : > "$LOG"
  echo "D6RF10_PREFLIGHT_SMOKE_BEGIN smoke=$SM solver=$SOL nNonOrth=$NNO relax_p=$RP relax_eqn=$RE endTime=$ET writeInterval=$WI cap_core_min=$PER_SMOKE_CAP_CORE_MIN deadline_s=$DEADLINE log=$(basename "$LOG")" | tee -a "$LEDGER"
  CMDF="$WORK/d6rf10_preflight_cmd_${SM}.sh"
  leg_cmd_file "$CMDF" "$SM" "$SOL" "$NNO" "$RP" "$RE" "$ET" "$WI"
  case "$(cat "$CMDF")" in *__*__*) echo "ABORT cmd file for $SM carries an unsubstituted __TOKEN__"; exit 4 ;; esac
  NAME="d6rf10_pf_${SM}_${RSTAMP}"
  T0=$(date -u +%s)
  RC=$(run_container "d6rf10_preflight_cmd_${SM}.sh" "$NAME" "$DEADLINE")
  T1=$(date -u +%s); WALL=$((T1-T0))
  sudo -n docker logs "$NAME" >> "$LOG" 2>&1
  sudo -n docker rm "$NAME" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "$BASE_REAL" 2>/dev/null
  CM=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
  CUM_CORE_MIN=$(python3 -c "print(round($CUM_CORE_MIN + $CM,3))")
  STOPPED=no
  [ "$RC" = "124" ] && STOPPED=deadline_reached_partial_trajectory
  echo "D6RF10_PREFLIGHT_SMOKE_DONE smoke=$SM rc=$RC wall_s=$WALL core_min=$CM cumulative_core_min=$CUM_CORE_MIN stopped=$STOPPED log=$(basename "$LOG")" | tee -a "$LEDGER"
  test -s "$LOG" && touch "$LOG.ok.${RSTAMP}"
done

echo "D6RF10_PREFLIGHT_DONE smokes=R2,R3,R4 cumulative_core_min=$CUM_CORE_MIN NOTE=measurement_only_no_grade_no_verdict" | tee -a "$LEDGER"
echo "STAMP=$STAMP CUM_CORE_MIN=$CUM_CORE_MIN"
exit 0
