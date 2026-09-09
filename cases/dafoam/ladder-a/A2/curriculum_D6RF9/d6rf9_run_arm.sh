#!/usr/bin/env bash
# =============================================================================
# curriculum D6RF9 -- THE LAUNCHER for the A2-wing convergence probe `P_conv`,
# the OUTER-LOOP-CONVERGENCE successor to D6RF7.
#
# PERMISSION = NOT_FROZEN.  This is a lane's prediction-first DRAFT producer and
# it LAUNCHES NOTHING while unfrozen: the G-FREEZE limb below aborts (rc 3) on
# the placeholder token, before any directory is touched or container created.
# The freeze (PREREGISTRATION.md by sha), the per-instrument pin fixpoints and
# the enqueue belong to the dafoam-supervisor and are taken AFTER the
# supervisor's non-delegable check-1.  This file is OUTSIDE the freeze
# hash-lock (parent posture, D19T): it verifies the FROZEN INSTRUMENTS it
# stages, never itself.
#
# DERIVED FROM `curriculum_D6RF7/d6rf7_run_arm.sh` (the P_conv arm), adapted to
# an ORDERED LADDER.  The D6RF7 FD/CD/off/price staging (mp double-deformation
# S-steps, OptView copy) is CARRIED where the primal needs it and the FD-only
# machinery is dropped (D6RF9 delta D5).  The single new mechanism is
# `install_config`: per rung it sets the outer-loop numerics (fvSolution
# nNonOrthogonalCorrectors + relaxation, controlDict endTime) HELD-FIXED against
# the D6RF7 LIMITED fvSchemes, and echoes `D6RF9_CONFIG_INSTALLED` -- the marker
# the grader binds to the leg.  `solverName` is overridden per rung inside the
# driver (`d6rf9_run_leg.py`).
#
# THE LADDER (PREREGISTRATION.md section 3), run IN ORDER, STOPPED_AT_FIRST_PASS:
#   R1 DARhoSimpleFoam  nNonOrth 3  relax 0.30/0.70  endTime 2500
#   R2 DARhoSimpleFoam  nNonOrth 12 relax 0.30/0.70  endTime 2000
#   R3 DARhoSimpleCFoam nNonOrth 12 relax 0.70/0.70  endTime 2000
#   R4 DARhoSimpleCFoam nNonOrth 12 relax 0.15/0.50  endTime 4000
# Beside EACH rung, the D6RF7 FROZEN control config (DARhoSimpleFoam, nNonOrth 3,
# relax 0.30/0.70, endTime 1000) runs as the known-GATE-FAIL control (D4): a
# PASS on the control withdraws the rung's verdict.  After each rung's container
# the host grades that rung's log with `d6rf9_grade.py`; a binding PASS stops
# the ladder, else it advances -- and a CUMULATIVE 291 core-min HARD STOP bounds
# the whole ladder (rule 12; overrun stops the run, it does not get a budget).
#
# rc CAPTURE IS THE KERNEL'S, NOT `$?` OF A setsid/timeout LINE (L "setsid
# parent returns zero"): the container is the detached wrapper, `timeout -k`
# lives INSIDE it and survives shell death, and the rc is read from
# `docker inspect .State.ExitCode` before the container is removed (no --rm).
#
# EXITS: 0 ladder ran (see per-rung rc in the ledger) | 3 G-FREEZE / G-ROOT
# refusal (NOTHING launched) | 4 identity / staging / md5 failure | 5 field /
# path-existence refusal | 65 cap-identity refusal.
# =============================================================================
set -u
set -o pipefail

ITEM=D6RF9
ARM=P_conv
RANKS=4

# --- PERMISSION (freeze field). Assigned EXACTLY once; the last assignment
# --- would win in shell, so the count is pinned, not the appearance.
PERMISSION=ed1818473cdfbba551701e1d4824d1314e7c319b   # freeze sha (PREREGISTRATION.md FROZEN v1.0, 2026-09-08)
PERM_ASSIGNMENTS=$(grep -cE '^PERMISSION=' "${BASH_SOURCE[0]}")
if [ "$PERM_ASSIGNMENTS" != "1" ]; then
  echo "ABORT G-FREEZE-UNIQUE PERMISSION is assigned $PERM_ASSIGNMENTS time(s); the last wins silently. Pin the count."
  grep -nE '^PERMISSION=' "${BASH_SOURCE[0]}"
  exit 3
fi

REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF9-a2-wing-convergence-probe
BASE="${1:-$REGISTERED_BASE}"
REPO=/home/ubuntu/Certonomous
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREREG=cases/dafoam/ladder-a/A2/curriculum_D6RF9/PREREGISTRATION.md
RUNS_DIR=/home/ubuntu/certonomous-runs
# The registered SOURCE the primal state is staged from (D6RF7's own run root:
# base mesh + mp04/05/06 + OptView endpoint), READ-ONLY.
SRC_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF7-a2-wing-convergence-probe

# =============================================================================
# G-FREEZE.  The placeholder limb fires while unfrozen; the shape+resolution
# limbs survive the freeze so the control does not go silent once the field
# matters.  (Carried from d6rf7_run_arm.sh:108-175.)
# =============================================================================
if [ "$PERMISSION" = "NOT_FROZEN" ]; then
  echo "ABORT G-FREEZE this item is NOT FROZEN. PERMISSION is still the placeholder."
  echo "  CLAUDE.md rule 2: the gate/threshold/cap/label are committed BEFORE the"
  echo "  solver starts; the freeze and the enqueue belong to the dafoam-supervisor"
  echo "  and are NOT taken by a lane. NO CONTAINER IS CREATED. NO DIRECTORY IS TOUCHED."
  exit 3
fi
case "$PERMISSION" in *[!0-9a-f]*|"") BAD=yes ;; *) BAD=no ;; esac
if [ "$BAD" = "yes" ] || [ "${#PERMISSION}" -lt 7 ] || [ "${#PERMISSION}" -gt 40 ]; then
  echo "ABORT G-FREEZE-SHAPE PERMISSION='$PERMISSION' is neither NOT_FROZEN nor a 7-40 char hex sha."
  exit 3
fi
if command -v git >/dev/null 2>&1 && [ -d "$REPO/.git" ]; then
  RESOLVED=$(git -C "$REPO" rev-parse --verify --quiet "${PERMISSION}^{commit}" 2>/dev/null || true)
  [ -n "$RESOLVED" ] || { echo "ABORT G-FREEZE-SHA PERMISSION='$PERMISSION' names no commit."; exit 3; }
  git -C "$REPO" cat-file -e "${RESOLVED}:${PREREG}" 2>/dev/null || {
    echo "ABORT G-FREEZE-SHA commit $RESOLVED does not carry $PREREG (a sha for other work)."; exit 3; }
  PREREG_AT_FREEZE=$(git -C "$REPO" rev-parse "${RESOLVED}:${PREREG}")
else
  RESOLVED=UNMEASURED; PREREG_AT_FREEZE=UNMEASURED
fi
echo "D6RF9_G_FREEZE_PASS permission=$PERMISSION resolved=$RESOLVED prereg_blob=$PREREG_AT_FREEZE"

# =============================================================================
# G-ROOT -- no-delete, fresh root, no foreign root, no live pid rooted here.
# =============================================================================
BASE_REAL=$(realpath -m "$BASE")
REG_REAL=$(realpath -m "$REGISTERED_BASE")
SRC_REAL=$(realpath -m "$SRC_ROOT")

# G-ROOT.1 -- BASE must be THIS item's registered fresh root, normalised.
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
  echo "  given:      $BASE_REAL"
  echo "  registered: $REG_REAL"
  exit 3
fi
# G-ROOT.2 -- never THE SOURCE (D6RF7's graded root is READ-ONLY here).
if [ "$BASE_REAL" = "$SRC_REAL" ]; then
  echo "ABORT G-ROOT.2 BASE resolves to the READ-ONLY SOURCE $SRC_REAL (D6RF7's graded root)."
  exit 3
fi
# G-ROOT.2b -- never ANOTHER item's run root (enumerated from disk, never carried).
if [ -d "$RUNS_DIR" ]; then
  while IFS= read -r forb; do
    [ -z "$forb" ] && continue
    [ "$forb" = "$REG_REAL" ] && continue
    if [ "$BASE_REAL" = "$forb" ]; then
      echo "ABORT G-ROOT.2b BASE resolves to ANOTHER item's run root: $forb (holds graded rows)."
      exit 3
    fi
  done <<< "$(find "$RUNS_DIR" -maxdepth 1 -mindepth 1 -type d -exec realpath -m {} \; 2>/dev/null)"
fi
# G-ROOT.3 -- FRESH ROOT, NO rm. A re-fire finds a stale root and REFUSES; the
# recovery is an explicit archive (mv), never an implicit delete (S-29).
if [ -e "$BASE_REAL" ]; then
  echo "ABORT G-ROOT.3 $BASE_REAL already exists. This launcher does NOT remove a run root."
  echo "  A re-fire needs the prior root ARCHIVED by mv, not deleted here."
  exit 3
fi
# G-ROOT.4 -- NO LIVE PID is rooted at BASE (its cwd resolves there). A running
# solver's directory is never re-staged (fleet agents are invisible to pgrep;
# this reads /proc cwds directly).
LIVE_HERE=""
for pid in $(ls /proc 2>/dev/null | grep -E '^[0-9]+$'); do
  cwd=$(readlink -f "/proc/$pid/cwd" 2>/dev/null) || continue
  case "$cwd" in
    "$BASE_REAL"|"$BASE_REAL"/*) LIVE_HERE="$LIVE_HERE $pid" ;;
  esac
done
if [ -n "$LIVE_HERE" ]; then
  echo "ABORT G-ROOT.4 live pid(s) [$LIVE_HERE] have a cwd rooted at $BASE_REAL. Not re-staging a live root."
  exit 3
fi
echo "D6RF9_G_ROOT_PASS item=$ITEM base=$BASE_REAL fresh=yes no_live_pid=yes"

# =============================================================================
# FROZEN-INSTRUMENT md5 FIXPOINT (L-504).  The launcher verifies the frozen
# instruments it stages, not itself.  The d6rf7_* carries and the byte-identical
# accept-floor control have REAL pins; the D6RF9-authored grader/driver pins are
# PLACEHOLDER_AT_FREEZE and the supervisor sets them at freeze -- a launch is
# refused while any pin is a placeholder.  (Never reached pre-freeze: G-FREEZE
# aborts first; present so the fixpoint exists once frozen.)
# =============================================================================
MD5_RUNSCRIPT=137539e0a99be27f27fdb69e063b2a87          # d6rf7_opt_runScript.py (D6RF7 MD5_RUNSCRIPT6)
MD5_FVSCHEMES_LIMITED=8374443e7a374e9d353cffccdb654aaf  # d6rf7_fvSchemes_LIMITED (held fixed)
MD5_FVSOL=67fed3c2ffd2765e51f2563270060648              # d6rf7_fvSolution (base for the config install)
MD5_ACCEPT_FLOOR=c6e63098e7afd542ea379a03eccfaf12       # d6rf9_accept_floor_control.py (byte-identical to D6RF7)
MD5_UNITS=34f477f92b23e27896b458475eef0f78              # d6rf7_units_assert.py
MD5_ENDPOINT_PHYS=625bacf5b1489989f9a2638dd99e2e52      # d6rf7_endpoint_physical.py (endpoint reconstruction)
MD5_LOCUS=341189ca866f302a7e1bba8eefad3a57              # d6rf7_endpoint_locus.py (D6RF7 MD5_LOCUS6; imported by endpoint_physical:90 + units_assert:82 -- was dropped from the D6RF9 adaptation, restored 2026-09-09)
MD5_EXTRACT=baedb673e9c88291f6724794681bc9a7            # d6rf7_extract_endpoint.py
MD5_GRADE=6e76ed57ac6890b0a7fa260c46dc517b              # d6rf9_grade.py (pinned at freeze 2026-09-08)
MD5_RUN_LEG=ae6ee60ce40239e6579b0ba59ae311a9            # d6rf9_run_leg.py (pinned at freeze 2026-09-08)
# OptView.hst is DATA (the pyOptSparse optimisation history that DEFINES the endpoint design point), not a staged instrument, so it lives OUTSIDE INSTR_MD5. Its md5 is the canonical endpoint pinned by d6rf7_extract_endpoint.py's own registration (:14). Staged below; was dropped from the D6RF9 adaptation, restored 2026-09-09.
MD5_OPTVIEW=70fafa07bdee618fef13039433c01114

# instrument path -> pin (staged into $BASE beside the case)
declare -A INSTR_MD5=(
  [d6rf7_opt_runScript.py]=$MD5_RUNSCRIPT
  [d6rf7_fvSchemes_LIMITED]=$MD5_FVSCHEMES_LIMITED
  [d6rf7_fvSolution]=$MD5_FVSOL
  [d6rf9_accept_floor_control.py]=$MD5_ACCEPT_FLOOR
  [d6rf7_units_assert.py]=$MD5_UNITS
  [d6rf7_endpoint_physical.py]=$MD5_ENDPOINT_PHYS
  [d6rf7_endpoint_locus.py]=$MD5_LOCUS
  [d6rf7_extract_endpoint.py]=$MD5_EXTRACT
  [d6rf9_grade.py]=$MD5_GRADE
  [d6rf9_run_leg.py]=$MD5_RUN_LEG
)
D6RF7_DIR=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6RF7
verify_and_stage_instruments() {   # $1 = destination work root
  local dst="$1" f src pin got
  for f in "${!INSTR_MD5[@]}"; do
    pin="${INSTR_MD5[$f]}"
    case "$pin" in
      PLACEHOLDER_AT_FREEZE)
        echo "ABORT md5 fixpoint: $f pin is still PLACEHOLDER_AT_FREEZE -- the"
        echo "  dafoam-supervisor sets the D6RF9-authored instrument pins at freeze."; exit 4 ;;
    esac
    # source: a d6rf9_* file lives in HERE; a d6rf7_* carry lives in D6RF7_DIR
    case "$f" in
      d6rf9_*) src="$HERE/$f" ;;
      *)       src="$D6RF7_DIR/$f" ;;
    esac
    [ -f "$src" ] || { echo "ABORT md5 fixpoint: instrument source absent: $src"; exit 4; }
    got=$(md5sum "$src" | cut -d' ' -f1)
    [ "$got" = "$pin" ] || { echo "ABORT md5 fixpoint: $f md5 $got != frozen $pin"; exit 4; }
    cp -a "$src" "$dst/$f" || { echo "ABORT staging copy failed: $f"; exit 4; }
    got=$(md5sum "$dst/$f" | cut -d' ' -f1)
    [ "$got" = "$pin" ] || { echo "ABORT post-stage md5: $f $got != $pin"; exit 4; }
  done
  echo "D6RF9_INSTRUMENTS_STAGED n=${#INSTR_MD5[@]} all_pins_match=yes dst=$dst"
}

# =============================================================================
# CAPS -- per-rung (PREREGISTRATION.md section 5) + cumulative 291 hard stop.
# =============================================================================
rung_cap()      { case "$1" in R1) echo 48 ;; R2) echo 63 ;; R3) echo 68 ;; R4) echo 112 ;; *) echo "" ;; esac; }
rung_solver()   { case "$1" in R1|R2) echo DARhoSimpleFoam ;; R3|R4) echo DARhoSimpleCFoam ;; *) echo "" ;; esac; }
rung_nnonorth() { case "$1" in R1) echo 3 ;; R2|R3|R4) echo 12 ;; *) echo "" ;; esac; }
rung_relaxp()   { case "$1" in R1|R2) echo 0.30 ;; R3) echo 0.70 ;; R4) echo 0.15 ;; *) echo "" ;; esac; }
rung_relaxeqn() { case "$1" in R1|R2|R3) echo 0.70 ;; R4) echo 0.50 ;; *) echo "" ;; esac; }
rung_endtime()  { case "$1" in R1) echo 2500 ;; R2|R3) echo 2000 ;; R4) echo 4000 ;; *) echo "" ;; esac; }
# the D6RF7 FROZEN control config, run beside every rung (D4).
CTRL_SOLVER=DARhoSimpleFoam; CTRL_NNONORTH=3; CTRL_RELAXP=0.30; CTRL_RELAXEQN=0.70; CTRL_ENDTIME=1000
CUMULATIVE_HARD_STOP_CORE_MIN=291
FRAME_ALLOWANCE_S=90
KILL_GRACE_S=60
MEM=20g
CPUSET=9,10,11,12
IMG=dafoam-idwarp-rot:v1
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35

# =============================================================================
# STAGING.  A fresh root, the source's mesh + run dirs copied in, the frozen
# instruments verified-and-staged, and a PATH-EXISTENCE FIXPOINT before any
# solver arm.  (endpoint reconstruction runs once in a setup container.)
# =============================================================================
test -d "$SRC_REAL" || { echo "ABORT staging: source $SRC_REAL absent"; exit 5; }
mkdir -p "$BASE_REAL" || { echo "ABORT staging: could not create fresh root"; exit 4; }
WORK="$BASE_REAL/$ARM"
mkdir -p "$WORK"
# base mesh + the three multipoint run dirs (the primal setup, held fixed)
for d in base mp04 mp05 mp06; do
  if [ -d "$SRC_REAL/$ARM/$d" ]; then cp -a "$SRC_REAL/$ARM/$d" "$WORK/$d"
  elif [ -d "$SRC_REAL/$d" ]; then cp -a "$SRC_REAL/$d" "$WORK/$d"
  else echo "ABORT staging: neither $SRC_REAL/$ARM/$d nor $SRC_REAL/$d present"; exit 5; fi
done
# OptView.hst -- the loose optimisation-history file at the arm root that DEFINES
# the endpoint (d6rf7_extract_endpoint.py reads it; the dir loop above copies only
# DIRECTORIES, so it was dropped -- lines 17/70 say it is carried).  md5-pinned to
# the canonical endpoint (70fafa07) so the reconstructed design point is reproducible.
if [ -f "$SRC_REAL/$ARM/OptView.hst" ]; then OPTVIEW_SRC="$SRC_REAL/$ARM/OptView.hst"
elif [ -f "$SRC_REAL/OptView.hst" ]; then OPTVIEW_SRC="$SRC_REAL/OptView.hst"
else echo "ABORT staging: OptView.hst absent under $SRC_REAL/$ARM or $SRC_REAL -- no endpoint to reconstruct"; exit 5; fi
OPTVIEW_SRC_MD5=$(md5sum "$OPTVIEW_SRC" | cut -d' ' -f1)
[ "$OPTVIEW_SRC_MD5" = "$MD5_OPTVIEW" ] || { echo "ABORT staging: OptView.hst md5 $OPTVIEW_SRC_MD5 != pinned $MD5_OPTVIEW (wrong endpoint)"; exit 5; }
cp -a "$OPTVIEW_SRC" "$WORK/OptView.hst" || { echo "ABORT staging: OptView.hst copy failed"; exit 5; }
[ -f "$WORK/OptView.hst" ] && [ "$(md5sum "$WORK/OptView.hst" | cut -d' ' -f1)" = "$MD5_OPTVIEW" ] || { echo "ABORT staging: OptView.hst post-copy md5 mismatch"; exit 5; }
echo "D6RF9_OPTVIEW_STAGED md5=$MD5_OPTVIEW src=$OPTVIEW_SRC (endpoint design point)"
verify_and_stage_instruments "$WORK"

# PATH-EXISTENCE FIXPOINT before the solver arm: the files the container will
# read must be on disk NOW, or a container would run against a name that is not
# there and the grader would read BAR_NOT_PRODUCED for a staging reason.
PATH_FIXPOINT_OK=yes
for need in \
  "$WORK/d6rf7_opt_runScript.py" "$WORK/d6rf9_run_leg.py" \
  "$WORK/d6rf7_fvSchemes_LIMITED" "$WORK/d6rf7_fvSolution" \
  "$WORK/d6rf7_endpoint_physical.py" "$WORK/d6rf7_units_assert.py" \
  "$WORK/OptView.hst"; do
  [ -f "$need" ] || { echo "ABORT path-existence fixpoint: $need is not on disk"; PATH_FIXPOINT_OK=no; }
done
for d in base mp04 mp05 mp06; do
  [ -d "$WORK/$d/system" ] || { echo "ABORT path-existence fixpoint: $WORK/$d/system absent"; PATH_FIXPOINT_OK=no; }
done
[ "$PATH_FIXPOINT_OK" = "yes" ] || { echo "ABORT path-existence fixpoint FAILED before the solver arm."; exit 5; }
echo "D6RF9_PATH_FIXPOINT_OK all staged instruments, the runScript, the driver and base/mp04/mp05/mp06/system present"

# --- image identity by DIGEST ------------------------------------------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
test "$GOT_DIGEST" = "$IMG_PATCHED_DIGEST" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$IMG_PATCHED_DIGEST"; exit 4; }
echo "D6RF9_G_ROW_PASS row=PATCHED digest=$GOT_DIGEST"

# =============================================================================
# THE install_config CONTAINER FUNCTION (emitted into every rung's cmd file).
# It installs the LIMITED fvSchemes (held fixed, md5-checked), sets the rung's
# nNonOrthogonalCorrectors + (p|p_rgh)/equations relaxation in the SIMPLE-scope
# ONLY, sets controlDict endTime, and echoes D6RF9_CONFIG_INSTALLED. It REFUSES
# on a zero-site install (a swap that swapped nothing).
# =============================================================================
read -r -d '' INSTALL_FN <<'FNEOF' || true
install_config() {   # $1=leg $2=solver $3=nNonOrth $4=relax_p $5=relax_eqn $6=endTime $7=fvSchemesMd5
  n=0
  for sd in system mp04/system mp05/system mp06/system; do
    [ -f "$sd/fvSolution" ] || { echo "D6RF9_LEG_ABORT leg=$1 no fvSolution at $sd"; return 5; }
    [ -f "$sd/controlDict" ] || { echo "D6RF9_LEG_ABORT leg=$1 no controlDict at $sd"; return 5; }
    cp -a d6rf7_fvSchemes_LIMITED "$sd/fvSchemes" || { echo "D6RF9_LEG_ABORT leg=$1 fvSchemes install failed at $sd"; return 5; }
    got=$(md5sum "$sd/fvSchemes" | cut -d' ' -f1)
    [ "$got" = "$7" ] || { echo "D6RF9_LEG_ABORT leg=$1 fvSchemes post-image $got != $7 at $sd"; return 5; }
    # nNonOrthogonalCorrectors: SIMPLE scope only (potentialFlow's 20 untouched)
    awk -v v="$3" 'BEGIN{b=0} /^SIMPLE/{b=1} b&&/nNonOrthogonalCorrectors/{sub(/[0-9]+;/, v";")} /^}/{if(b)b=0} {print}' "$sd/fvSolution" > "$sd/fvSolution.t1" && mv "$sd/fvSolution.t1" "$sd/fvSolution" || { echo "D6RF9_LEG_ABORT leg=$1 nNonOrth set failed at $sd"; return 5; }
    grep -qE "nNonOrthogonalCorrectors[[:space:]]+$3;" "$sd/fvSolution" || { echo "D6RF9_LEG_ABORT leg=$1 nNonOrthogonalCorrectors $3 not set at $sd"; return 5; }
    # relaxation (p|p_rgh) in the fields block, and equations block
    awk -v v="$4" '/\(p\|p_rgh\)/{sub(/[0-9.]+;/, v";")} {print}' "$sd/fvSolution" > "$sd/fvSolution.t2" && mv "$sd/fvSolution.t2" "$sd/fvSolution" || { echo "D6RF9_LEG_ABORT leg=$1 relax_p set failed at $sd"; return 5; }
    awk -v v="$5" '/\(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega\)/{sub(/[0-9.]+;/, v";")} {print}' "$sd/fvSolution" > "$sd/fvSolution.t3" && mv "$sd/fvSolution.t3" "$sd/fvSolution" || { echo "D6RF9_LEG_ABORT leg=$1 relax_eqn set failed at $sd"; return 5; }
    grep -qE "\(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega\)\"?[[:space:]]+$5;" "$sd/fvSolution" || { echo "D6RF9_LEG_ABORT leg=$1 relax_eqn $5 not set at $sd"; return 5; }
    grep -qE "\(p\|p_rgh\)\"?[[:space:]]+$4;" "$sd/fvSolution" || { echo "D6RF9_LEG_ABORT leg=$1 relax_p $4 not set at $sd"; return 5; }
    # controlDict endTime
    awk -v v="$6" '/^endTime/{$0="endTime         "v";"} {print}' "$sd/controlDict" > "$sd/controlDict.t1" && mv "$sd/controlDict.t1" "$sd/controlDict" || { echo "D6RF9_LEG_ABORT leg=$1 endTime set failed at $sd"; return 5; }
    grep -qE "^endTime[[:space:]]+$6;" "$sd/controlDict" || { echo "D6RF9_LEG_ABORT leg=$1 endTime $6 not set at $sd"; return 5; }
    n=$((n+1))
  done
  [ "$n" -ge 1 ] || { echo "D6RF9_LEG_ABORT leg=$1 installed ZERO sites -- a swap that swapped nothing"; return 5; }
  echo "D6RF9_CONFIG_INSTALLED leg=$1 endTime=$6 solverName=$2 relax_p=$4 relax_eqn=$5 nNonOrthogonalCorrectors=$3 sites=$n"
  return 0
}
FNEOF

# =============================================================================
# SETUP CONTAINER -- reconstruct the endpoint DVs ONCE (endpoint_physical) so
# every rung's primal runs at the SAME design point D6RF7 measured.
# =============================================================================
AGE_DATUM=$(date -u +%s.%N)   # SUB-SECOND: %s alone floors to the whole second, moving the datum EARLIER and opening rule-4's age guard fail-open by up to 1.000 s (both consumers accept on mt>datum). The frozen d6rf7_endpoint_physical.py C3 check REFUSES a truncated datum -- restored fractional part 2026-09-09 (mirrors D6RF7 launcher L.1153-1166 repair).
echo "$AGE_DATUM" > "$WORK/.d6rf9_age_datum"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
run_container() {   # $1 = cmd file (relative to $WORK), $2 = name, $3 = deadline_s -> echoes rc
  local cmdfile="$1" name="$2" tmo="$3" cid
  sudo -n docker run -d --name "$name" \
      --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
      -v "$BASE_REAL":/mnt -w "/mnt/$(basename "$WORK")" "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
       timeout -k $KILL_GRACE_S $tmo bash /mnt/$(basename "$WORK")/$cmdfile" > /dev/null 2>&1 \
    || { echo "125"; return 0; }
  # wait for exit (the cap is INSIDE the container; the kernel is the verdict)
  while [ "$(sudo -n docker inspect --format '{{.State.Running}}' "$name" 2>/dev/null)" = "true" ]; do sleep 10; done
  local rc; rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$name" 2>/dev/null)
  test -n "$rc" || rc=125
  echo "$rc"
}

# ---- the setup cmd (endpoint reconstruction + units gate) -------------------
SETUP_CMD="$WORK/d6rf9_setup_cmd.sh"
{
  echo "set -o pipefail"
  echo "python d6rf7_endpoint_physical.py --age-datum $AGE_DATUM && \\"
  echo "python d6rf7_units_assert.py d6rf7_endpoint_dvs.json --runscript d6rf7_opt_runScript.py"
} > "$SETUP_CMD"
SETUP_TMO=$(python3 -c "print(int(round(30*60.0/$RANKS)) - $FRAME_ALLOWANCE_S)")
echo "D6RF9_SETUP_CONTAINER reconstruct endpoint DVs (deadline_s=$SETUP_TMO)"
SETUP_RC=$(run_container "d6rf9_setup_cmd.sh" "d6rf9_setup_${STAMP}" "$SETUP_TMO")
sudo -n docker logs "d6rf9_setup_${STAMP}" > "$BASE_REAL/setup_${STAMP}.log" 2>&1
sudo -n docker rm "d6rf9_setup_${STAMP}" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$BASE_REAL" 2>/dev/null
[ "$SETUP_RC" = "0" ] || { echo "ABORT setup container rc=$SETUP_RC (endpoint reconstruction / units gate failed)"; exit 4; }
# path-existence fixpoint on the reconstructed product before any rung
[ -f "$WORK/d6rf7_endpoint_dvs.json" ] || { echo "ABORT the endpoint DV file was not produced by the setup container"; exit 5; }
echo "D6RF9_ENDPOINT_READY d6rf7_endpoint_dvs.json present"

# =============================================================================
# THE LADDER.  R1..R4 in order, STOPPED_AT_FIRST_PASS, under the 291 core-min
# cumulative hard stop.  Per rung: install candidate config -> run candidate
# leg; install control config -> run control leg; grade on the host.
# =============================================================================
LEDGER="$BASE_REAL/ledger.txt"
echo "ITEM=$ITEM" > "$LEDGER"
CUM_CORE_MIN=0
LADDER_VERDICT="ALL_RUNGS_MEASURED_NONE_PASSED"

leg_cmd_file() {   # build a one-leg cmd file: install_config + mpirun run_leg
  # $1=cmdpath $2=leg $3=solver $4=nnonorth $5=relaxp $6=relaxeqn $7=endtime
  {
    printf '%s\n' "$INSTALL_FN"
    echo "set -o pipefail"
    echo "install_config $2 $3 $4 $5 $6 $7 $MD5_FVSCHEMES_LIMITED && \\"
    echo "mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH \\"
    echo "  python d6rf9_run_leg.py --leg-tag $2 --solver $3 --runscript d6rf7_opt_runScript.py --endpoint-dvs d6rf7_endpoint_dvs.json"
  } > "$1"
}

for RUNG in R1 R2 R3 R4; do
  CAP=$(rung_cap "$RUNG")
  DEADLINE=$(python3 -c "print(int(round($CAP*60.0/$RANKS)) - $FRAME_ALLOWANCE_S)")
  test "$DEADLINE" -gt 0 || { echo "ABORT cap-identity: rung $RUNG deadline<=0 at cap=$CAP"; exit 65; }
  RSTAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
  echo "D6RF9_RUNG_BEGIN rung=$RUNG cap_core_min=$CAP deadline_s=$DEADLINE cumulative_core_min=$CUM_CORE_MIN hard_stop=$CUMULATIVE_HARD_STOP_CORE_MIN" | tee -a "$LEDGER"

  # ---- candidate leg + control leg, one container each ----
  LOG="$BASE_REAL/${RUNG}_${RSTAMP}.log"
  : > "$LOG"
  for PHASE in candidate control; do
    if [ "$PHASE" = "candidate" ]; then
      TAG="$RUNG"; SOL=$(rung_solver "$RUNG"); NNO=$(rung_nnonorth "$RUNG")
      RP=$(rung_relaxp "$RUNG"); RE=$(rung_relaxeqn "$RUNG"); ET=$(rung_endtime "$RUNG")
    else
      TAG="${RUNG}_control"; SOL=$CTRL_SOLVER; NNO=$CTRL_NNONORTH
      RP=$CTRL_RELAXP; RE=$CTRL_RELAXEQN; ET=$CTRL_ENDTIME
    fi
    CMDF="$WORK/d6rf9_cmd_${TAG}.sh"
    leg_cmd_file "$CMDF" "$TAG" "$SOL" "$NNO" "$RP" "$RE" "$ET"
    # placeholder guard: no unsubstituted token may reach the container
    case "$(cat "$CMDF")" in *__*__*) echo "ABORT cmd file for $TAG carries an unsubstituted __TOKEN__"; exit 4 ;; esac
    NAME="d6rf9_${TAG}_${RSTAMP}"
    T0=$(date -u +%s)
    RC=$(run_container "d6rf9_cmd_${TAG}.sh" "$NAME" "$DEADLINE")
    T1=$(date -u +%s); WALL=$((T1-T0))
    sudo -n docker logs "$NAME" >> "$LOG" 2>&1
    sudo -n docker rm "$NAME" >/dev/null 2>&1
    sudo -n chown -R ubuntu:ubuntu "$BASE_REAL" 2>/dev/null
    CM=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
    CUM_CORE_MIN=$(python3 -c "print(round($CUM_CORE_MIN + $CM,3))")
    echo "ARM=$ARM rung=$RUNG phase=$PHASE leg=$TAG rc=$RC wall_s=$WALL core_min=$CM cumulative_core_min=$CUM_CORE_MIN log=$(basename "$LOG")" | tee -a "$LEDGER"
    # CUMULATIVE HARD STOP (rule 12): overrun stops the run; no new budget.
    if [ "$(python3 -c "print(1 if $CUM_CORE_MIN > $CUMULATIVE_HARD_STOP_CORE_MIN else 0)")" = "1" ]; then
      echo "D6RF9_CUMULATIVE_HARD_STOP cumulative_core_min=$CUM_CORE_MIN > $CUMULATIVE_HARD_STOP_CORE_MIN action=STOP_LADDER" | tee -a "$LEDGER"
      LADDER_VERDICT="STOPPED_AT_CUMULATIVE_HARD_STOP"
      break 2
    fi
  done
  test -s "$LOG" && touch "$LOG.ok.${RSTAMP}"

  # ---- grade this rung on the HOST (single reader). STOP at first PASS. ----
  GRADE=$(python3 "$WORK/d6rf9_grade.py" --log "$LOG" --rung "$RUNG" 2>/dev/null || true)
  BINDING=$(printf '%s' "$GRADE" | python3 -c "import sys,json
try: d=json.load(sys.stdin); print(d.get('binding_verdict') or d.get('verdict'))
except Exception: print('UNREADABLE')" 2>/dev/null)
  echo "D6RF9_RUNG_GRADED rung=$RUNG binding_verdict=$BINDING" | tee -a "$LEDGER"
  if [ "$BINDING" = "PASS" ]; then
    LADDER_VERDICT="STOPPED_AT_FIRST_PASS_${RUNG}"
    echo "D6RF9_LADDER_STOP rung=$RUNG reason=binding_PASS" | tee -a "$LEDGER"
    break
  fi
done

echo "D6RF9_LADDER_DONE verdict=$LADDER_VERDICT cumulative_core_min=$CUM_CORE_MIN hard_stop=$CUMULATIVE_HARD_STOP_CORE_MIN" | tee -a "$LEDGER"
echo "STAMP=$STAMP LADDER_VERDICT=$LADDER_VERDICT CUM_CORE_MIN=$CUM_CORE_MIN"
exit 0
