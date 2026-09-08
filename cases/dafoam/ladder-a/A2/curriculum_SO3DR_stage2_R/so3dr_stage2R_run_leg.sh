#!/usr/bin/env bash
# SO-3D-R STAGE 2 SUCCESSOR "R" -- per-leg standalone-primal LAUNCHER.  DRAFT -- NOT FROZEN.
#
# The V-127 fresh successor to SO3DR-F4 (curriculum_SO3DR_stage2/).  Feeds the
# FROZEN _R rig so3dr_stage2R_standalone_runScript.py (md5
# 9c1905c0220604946dbd6a8016d5b9de) -- byte-identical to the frozen parent rig
# EXCEPT the rank-0 injected_dv.json echo-sidecar write is moved to BEFORE
# prob.run_model() (rig write line 352 <= run line 359), so the F4 echo survives
# DAFoam's EXPECTED post-End primal-raise on the 32 primal-raised legs where the
# parent rig (write 328 after run 312) never reached it and the frozen grader's
# F4 arm hard-REFUSED (exit 2).  The grader and sample are re-frozen BYTE-IDENTICAL
# into the _R dir (grader md5 2d32ec9b933764b5eb3e3bb61e6657cd, sample md5
# 55bf8e2dcc07fbe3197f2c53421ad019 -- both unchanged from the parent).
#
# This launcher is OUTSIDE the hash-locked grading-path set (same posture as the
# parent launcher committed 527787c1 and the D6RF/D6RF4/D6RF7 stagers): the
# PREREGISTRATION.md §7/§8 freeze pins ONLY the rig, grader and sample; this
# launcher VERIFIES those frozen instruments against their registered md5 before
# invoking, it is not itself a §-pinned frozen instrument.  Nothing here modifies
# the frozen rig, grader or sample.
#
# DERIVED verbatim from the parent per-leg launcher
# (curriculum_SO3DR_stage2/so3dr_stage2_run_leg.sh, committed 527787c1).
# Enumerated departures vs the parent (companion diff
# so3dr_stage2R_run_leg_DELTAS_from_parent.diff):
#   R-D1  PINS REPOINTED to the _R frozen bytes: RIG -> so3dr_stage2R_standalone_runScript.py
#         md5 9c1905c0 (was so3dr_stage2_standalone_runScript.py dc67cced); GRADER ->
#         so3dr_stage2R_grade.py md5 2d32ec9b (path only; md5 unchanged); SAMPLE ->
#         so3dr_stage2R_registered_sample.json md5 55bf8e2d (path only; md5 unchanged).
#         CASE_DIR repointed to curriculum_SO3DR_stage2_R.  ITEM=SO3DR_STAGE2R.
#   R-D2  FRESH campaign run root: CURRICULUM-SO3DR-STAGE2R-a2-cl04-standalone-<STAMP>
#         under /home/ubuntu/certonomous-runs/ (parent's stamp pattern; the STAMP is
#         supplied by the caller/daemon via -base).  G-ROOT no-delete: refuse if -base exists.
#   R-D3  CAP REPOINTED to the _R prereg §5 literal: cap 198 core-min (was 585); the prereg
#         grep now requires the "198 core-min" literal in the _R PREREGISTRATION.md.
#   Everything else -- SO3DR-L1..L7 apparatus (one standalone cl04 primal per leg at np=4,
#   registered dv_block_line selection, L-504 md5 FIXPOINT ALL_PINS_MATCH, runtime
#   PATH-EXISTENCE fixpoint, D6R log sha256 host-side check, cold-start optimiser
#   time-dir drop, freeze-gate env SO3DR_STAGE2_FROZEN=1, per-leg stop/stall, the
#   reach-the-grader-path reconciliation) -- is inherited UNCHANGED from the parent.
#
# set -e does NOT gate at the top of a harness Bash call; every step gates with
# `|| { echo ABORT...; exit N; }`.  NO --rm, so docker inspect survives the leg.
# REGISTERED EXIT CODES: 0 leg rc (from docker inspect); 3 G-ROOT (base exists /
# forbidden root); 4 identity/staging (md5, digest, copy); 5 cold-start; 8
# path-existence (a referenced runtime path absent); 9 cap reached; 64 usage.
set -uo pipefail

ITEM=SO3DR_STAGE2R
REPO=/home/ubuntu/Certonomous
CASE_DIR="$REPO/cases/dafoam/ladder-a/A2/curriculum_SO3DR_stage2_R"

# ---- FROZEN _R pins reconciled to PREREGISTRATION.md §7/§8 (the registered source) ----
RIG="$CASE_DIR/so3dr_stage2R_standalone_runScript.py"
RIG_MD5="9c1905c0220604946dbd6a8016d5b9de"                 # _R rig (ordering-fixed); was dc67cced
SAMPLE="$CASE_DIR/so3dr_stage2R_registered_sample.json"
SAMPLE_MD5="55bf8e2dcc07fbe3197f2c53421ad019"              # byte-identical re-freeze (unchanged)
GRADER="$CASE_DIR/so3dr_stage2R_grade.py"
GRADER_MD5="2d32ec9b933764b5eb3e3bb61e6657cd"              # byte-identical re-freeze (unchanged)

D6R_LOG="/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp_20260828T162849Z_1898072.log"
D6R_LOG_SHA256="394d9f5d8c59ea79602e678cec7a75915bef53a048b61e153d835fce57fc675d"
SRC_ROOT="/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp"
SRC_CASE="$SRC_ROOT/mp04"       # the cl04 scenario case (np=4 decomposed)
SRC_FFD="$SRC_ROOT/FFD"         # wingFFD.xyz (rig reads FFD/wingFFD.xyz from cwd)

IMG="${IMG:-dafoam-idwarp-rot:v1}"
IMG_DIGEST="sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"
RANKS=4

# ---- cost (prereg §5): item cap 198 core-min (_R MAX form), per-leg stop ~3x the 5.4 envelope ----
CAP_CORE_MIN="198.0"
REGISTERED_CAP_CORE_MIN="198.0"
PER_LEG_STOP_CORE_MIN="16.0"    # ~3x 5.4; a leg beyond this is stopped and recorded
PER_LEG_STALL_WALL_S=3600       # rule-12 stall
TMO_LEG=1200                    # per-leg container wall timeout (5.4 core-min ~ 81 wall-s at np=4; generous)

# ---- args ----
BASE="${BASE:-}"
CPUSET="${CPUSET:-}"
ONLY_LINE=""
while [ $# -gt 0 ]; do
  case "$1" in
    -base) BASE="$2"; shift 2;;
    -cpuset) CPUSET="$2"; shift 2;;
    -only_dv_block_line) ONLY_LINE="$2"; shift 2;;
    *) echo "ABORT usage: -base <root> -cpuset <cores> [-only_dv_block_line N]"; exit 64;;
  esac
done
[ -n "$BASE" ]   || { echo "ABORT: -base must be given (fresh timestamped campaign root)"; exit 64; }
[ -n "$CPUSET" ] || { echo "ABORT: -cpuset must be given explicitly; placement is never defaulted"; exit 64; }

# ============================================================================
# L-504 md5 FIXPOINT (SO3DR-L3): re-hash every pinned file to its registered md5
# ============================================================================
ALL_PINS_MATCH=1
check_pin() { local f="$1" want="$2"; local got; got=$(md5sum "$f" 2>/dev/null | awk '{print $1}');
  if [ "$got" = "$want" ]; then echo "PIN OK $(basename "$f") $got"; else echo "PIN MISMATCH $(basename "$f") got=$got want=$want"; ALL_PINS_MATCH=0; fi; }
check_pin "$RIG" "$RIG_MD5"
check_pin "$SAMPLE" "$SAMPLE_MD5"
check_pin "$GRADER" "$GRADER_MD5"
[ "$ALL_PINS_MATCH" = "1" ] || { echo "ABORT: ALL_PINS_MATCH=0 -- a frozen instrument drifted from its registered pin"; exit 4; }
echo "ALL_PINS_MATCH=1"

# ============================================================================
# L-504 AMENDMENT (SO3DR-L4): RUNTIME PATH-EXISTENCE FIXPOINT -- every runtime
# path this launcher references must EXIST before any container runs.
# ============================================================================
path_exists() { [ -e "$1" ] || { echo "ABORT path-existence: referenced runtime path ABSENT: $1"; exit 8; }; }
path_exists "$RIG"
path_exists "$SAMPLE"
path_exists "$D6R_LOG"
path_exists "$SRC_CASE"
path_exists "$SRC_CASE/0"
path_exists "$SRC_CASE/constant"
path_exists "$SRC_CASE/system"
path_exists "$SRC_CASE/system/decomposeParDict"
path_exists "$SRC_FFD/wingFFD.xyz"
echo "PATH_EXISTENCE_FIXPOINT OK (rig, sample, D6R log, SRC mp04 0/constant/system/decomposeParDict, FFD)"

# ---- D6R log sha256 host-side (in addition to the rig's own in-container check) ----
GOT_SHA=$(sha256sum "$D6R_LOG" | awk '{print $1}')
[ "$GOT_SHA" = "$D6R_LOG_SHA256" ] || { echo "ABORT: D6R log sha256 mismatch host-side (got $GOT_SHA)"; exit 4; }
echo "D6R_LOG_SHA256 OK $GOT_SHA"

# ---- image digest ----
GOT_DIGEST=$(sudo -n docker inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
[ -z "$GOT_DIGEST" ] && GOT_DIGEST=$(sudo -n docker inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
echo "IMAGE $IMG digest/id=$GOT_DIGEST (registered $IMG_DIGEST)"

# ---- cap assertion vs the frozen _R prereg literal (prereg §5/§8) ----
python3 -c "assert abs(float('$CAP_CORE_MIN')-float('$REGISTERED_CAP_CORE_MIN'))<1e-9" \
  || { echo "ABORT: enforced cap != registered cap"; exit 65; }
grep -qF "198 core-min" "$CASE_DIR/PREREGISTRATION.md" 2>/dev/null \
  || { echo "ABORT: _R prereg does not carry the 198 core-min cap literal"; exit 65; }

# ---- campaign root + shared ledger (cumulative spend vs 198 cap) ----
[ -e "$BASE" ] && { echo "ABORT G-ROOT: $BASE exists; guards refuse a pre-existing run root -- use a fresh timestamped dir, never delete an interrupted tree"; exit 3; }
mkdir -p "$BASE" || { echo "ABORT: cannot mkdir $BASE"; exit 3; }
chmod 777 "$BASE"
LEDGER="$BASE/ledger.txt"
SPENTFILE="$BASE/.spent_core_min"; echo "0" > "$SPENTFILE"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
echo "=== SO3DR_STAGE2R CAMPAIGN $STAMP cpuset=$CPUSET ranks=$RANKS cap=$CAP_CORE_MIN img=$IMG ===" | tee -a "$LEDGER"

# ---- the leg list: the registered dv_block_lines from the frozen sample ----
LEGS=$(python3 -c "
import json,sys
d=json.load(open('$SAMPLE'))['sample']
only='$ONLY_LINE'
for e in d:
    ln=e.get('dv_block_line')
    if only=='' or str(ln)==only: print(ln)
")
[ -n "$LEGS" ] || { echo "ABORT: no legs selected (sample empty or -only_dv_block_line not in sample)"; exit 64; }
NLEG=$(echo "$LEGS" | wc -w)
echo "LEGS_SELECTED n=$NLEG (of the frozen 36-leg sample)" | tee -a "$LEDGER"

# ============================================================================
# run_leg <dv_block_line>
# ============================================================================
run_leg() {
  local dvline="$1"
  local leg="leg_${dvline}"
  local work="$BASE/$leg"

  # cap check BEFORE the leg (rule 12: an overrun stops the campaign)
  local spent over
  spent=$(cat "$SPENTFILE")
  over=$(python3 -c "print('1' if float('$spent')>=float('$CAP_CORE_MIN') else '0')")
  [ "$over" = "1" ] && { echo "STOP: cap $CAP_CORE_MIN core-min reached at $spent before $leg; campaign STOPS, no new budget" | tee -a "$LEDGER"; return 9; }

  # ---- stage WORK: mp04 (cold) + FFD (SO3DR-L5) ----
  mkdir -p "$work" || { echo "ABORT: mkdir $work"; exit 5; }
  cp -a "$SRC_CASE" "$work/mp04" || { echo "ABORT: stage mp04 for $leg"; exit 4; }
  cp -a "$SRC_FFD" "$work/FFD"   || { echo "ABORT: stage FFD for $leg"; exit 4; }
  cp "$RIG" "$work/runScript.py" || { echo "ABORT: stage rig for $leg"; exit 4; }
  # re-hash the staged rig (the file that will actually run) against the pin
  echo "$RIG_MD5  $work/runScript.py" | md5sum -c - >/dev/null 2>&1 \
    || { echo "ABORT: staged runScript.py md5 != $RIG_MD5 for $leg"; exit 4; }

  # COLD START: drop optimiser output time dirs at top level and in every processorN
  for t in $(ls -1 "$work/mp04" 2>/dev/null | grep -E '^[0-9]+(\.[0-9]+)?$' | grep -v '^0$'); do
    rm -rf "$work/mp04/$t" || { echo "ABORT: cannot drop non-0 time dir $t"; exit 5; }
  done
  for pd in "$work"/mp04/processor*; do
    [ -d "$pd" ] || continue
    for t in $(ls -1 "$pd" 2>/dev/null | grep -E '^[0-9]+(\.[0-9]+)?$' | grep -v '^0$'); do
      rm -rf "$pd/$t" || { echo "ABORT: cannot drop $pd/$t"; exit 5; }
    done
    [ -d "$pd/0" ] || { echo "ABORT cold-start: $pd/0 absent after drop"; exit 5; }
  done
  [ -d "$work/mp04/0" ] || { echo "ABORT cold-start: $work/mp04/0 absent"; exit 5; }
  # assert NO non-0 top-level time dir remains (first grep lists, second tests)
  if ls -1 "$work/mp04" 2>/dev/null | grep -E '^[0-9]+(\.[0-9]+)?$' | grep -qv '^0$'; then
    echo "ABORT cold-start: a non-0 time dir survived in $work/mp04"; exit 5; fi
  chmod -R 777 "$work"
  echo "COLDSTART_PROVED leg=$dvline dropped optimiser time dirs, mp04/0 + processorN/0 present" | tee -a "$LEDGER"

  # ---- run the leg: rig from cwd=$work, np=4, freeze gate via env ----
  local cname="so3dr_r_${leg}_${STAMP}"
  # SO3DR-L4 (L-504 path reconciliation): the FROZEN _R grader reads the leg log via
  # glob(runs_root/leg_<bl>/*.log) -- INSIDE the leg dir -- so the log MUST live there,
  # not at the campaign-root top level. Verified against so3dr_stage2R_grade.py grade():
  # leg_dir=runs_root/leg_%d/mp04 ; log_glob=runs_root/leg_%d/*.log. The rig writes
  # injected_dv.json to run_dir_abs=cwd/mp04=$work/mp04, which is exactly leg_dir the
  # grader's F4 reads.
  local log="$work/run_${STAMP}.log"
  local t0 t1 wall rc
  t0=$(date +%s)
  timeout "$TMO_LEG" sudo -n docker run --name "$cname" --user 0:0 \
      --cpuset-cpus="$CPUSET" --cpus="$RANKS" --memory=20g --memory-swap=20g --oom-score-adj=500 \
      -e SO3DR_STAGE2_FROZEN=1 -e PYTHONHASHSEED=0 \
      -v "$work":/mnt -v "$D6R_LOG":"$D6R_LOG":ro -w /mnt "$IMG" \
      bash -lc "source /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun --allow-run-as-root -np $RANKS --bind-to core -x PYTHONPATH -x PYTHONHASHSEED -x SO3DR_STAGE2_FROZEN python runScript.py -dv_block_line $dvline -case_dir /mnt" \
      > "$log" 2>&1
  rc=$?
  t1=$(date +%s); wall=$((t1-t0))
  local insp; insp=$(sudo -n docker inspect -f '{{.State.ExitCode}} {{.State.OOMKilled}}' "$cname" 2>/dev/null); [ -n "$insp" ] || insp="NA NA"
  local cm; cm=$(python3 -c "print(round($wall*$RANKS/60.0,4))")
  spent=$(python3 -c "print(round(float('$(cat "$SPENTFILE")')+float('$cm'),4))"); echo "$spent" > "$SPENTFILE"
  local stall=""; [ "$wall" -gt "$PER_LEG_STALL_WALL_S" ] && stall=" STALL(>3600s)"
  local overleg; overleg=$(python3 -c "print('1' if float('$cm')>float('$PER_LEG_STOP_CORE_MIN') else '0')")
  [ "$overleg" = "1" ] && stall="$stall PER_LEG_STOP(>$PER_LEG_STOP_CORE_MIN core-min)"
  echo "LEG=$dvline rc=$rc wall_s=$wall ranks=$RANKS core_min=$cm inspect(exit,oom)=[$insp] spent=$spent/$CAP_CORE_MIN log=$(basename "$log")$stall" | tee -a "$LEDGER"
  return $rc
}

for dvl in $LEGS; do
  run_leg "$dvl" || echo "  (leg $dvl returned non-zero; recorded, campaign continues to next leg unless cap reached)" | tee -a "$LEDGER"
done

echo "TOTAL_SPENT_CORE_MIN=$(cat "$SPENTFILE") CAP=$CAP_CORE_MIN STAMP=$STAMP" | tee -a "$LEDGER"
echo "TO GRADE: python3 $GRADER --runs-root $BASE   # grader arg is --runs-root (not --root); NO --skip-freeze; grade() self-runs freeze_check + control_planted_zero + F6 sample-recompute (verified by --selftest)" | tee -a "$LEDGER"
