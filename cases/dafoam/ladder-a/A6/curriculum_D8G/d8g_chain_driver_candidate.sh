#!/usr/bin/env bash
# =============================================================================
# D8G CHAIN DRIVER -- PERMISSION: FROZEN by the dafoam-supervisor 2026-09-11.
#
# DERIVED from curriculum_D8R/d8r_chain_driver.sh -- FROZEN behind a graded two-row PASS
# and NOT EDITED BY THIS ITEM.  The deltas are recorded in
# d8g_chain_driver_DELTAS_from_d8r.diff.  INHERITED IN SHAPE: the pidfile / two-records-is-
# the-defect refusal, ALREADY_BOUGHT, the windowed H5 gate, the AGGREGATE and G-CPUSET
# wait-and-retry guards, STATUS.<arm>, the CHAIN_DONE trap (D5 Addendum 3 A3.5), the
# per-arm image selection (*-P patched, *-S shipped) and the frozen grader at chain end
# whose rc is INFRASTRUCTURE (L-342) and NEVER the verdict.
#
# THE FOUR D8G DELTAS THAT ARE NOT TRANSLATION:
#
#  (1) TEN ARMS, NOT FOUR, AND TWO OF THEM HAVE A PREREQUISITE.  F2-P cannot run until
#      A2-P has an rc=0 ledger row AND has written d8g_A.json, because the F arm's FD table
#      must sit beside THAT ROW's adjoint (the comparator refuses on
#      adjoint_source.md5 != md5(<row>/A2/d8g_A.json)).  The launcher already checks this;
#      THE DRIVER CHECKS IT FIRST, before the 60 s H5 window and before a possibly
#      four-hour aggregate wait, so a mis-ordered chain fails in a second instead of after
#      an hour of queueing.
#
#  (2) THE DRIVER DOES NOT STAGE A MESH AND DOES NOT GENERATE ONE.  D8R copied a single
#      FROZEN base/ tree from D8's run root.  D8G has THREE meshes that do not exist until
#      d8g_genmesh.sh builds them, and mesh generation is a SEPARATELY COSTED step
#      (PREREGISTRATION.md section 6.3: 9.000 core-min, with L3 measured at 4.183) that
#      writes its own construction record.  A chain driver that silently generated meshes
#      would make the case's geometry a SIDE EFFECT OF THE SOLVE CHAIN, and the mesh record
#      the comparator's G-MESH / G-SYS / G-BODY / G-TE read would then have been produced by
#      the same fire that consumed it.  SO: the driver REQUIRES the three level bases and
#      the three mesh records, REFUSES if any is absent, and prints the command to run.
#
#  (3) WHAT IT ASSERTS ABOUT EACH LEVEL, AND WHAT IT CANNOT.  The cell count per level IS
#      registered (section 2.2) and is asserted against the mesh record.  The points md5
#      per level is NOT registered and CANNOT BE -- re-coarsening is not byte-reproducible
#      (the comparator says so in G-SYS: "md5 is NOT the instrument"), so the driver asserts
#      SELF-CONSISTENCY instead: base_<LEVEL>/constant/polyMesh/points.gz must hash to the
#      value the record claims.  The arm-side binding is the comparator's G-M2, which hashes
#      every arm's own points.gz against the same record.  Stating which of the two is a
#      frozen constant and which is a consistency check is the point.
#
#  (4) PER-ARM MEMORY CAPS AND H5 FLOORS COME FROM SECTION 5's THREE-TIER TABLE, not D8R's
#      two-tier one: L1/L2 primal 6 GiB / floor 8.0; L3 primal 12 GiB / floor 14.0; the L2
#      adjoint and FD arms 14 GiB / floor 16.0.  L3 ADJOINT IS NOT AN ARM OF THIS ITEM and
#      is not launchable from here (section 7: BLOCKED on memory AND, independently, on
#      conditioning).
#
# Runs the named arms IN ORDER through the launcher and STOPS AT THE FIRST NON-ZERO rc.
# Started ONLY detached, so it is its own session leader and outlives the agent:
#   setsid nohup bash d8g_chain_driver.sh L1-P L2-P L3-P A2-P F2-P L1-S L2-S L3-S A2-S F2-S \
#     > <root>/chain_launch.out 2>&1 &
# cwd is the CASE directory, never the run root (the launcher's G-ROOT.5 b).
# =============================================================================
set -uo pipefail

# ===========================================================================
# G-FREEZE.0 -- A DRAFT MUST NOT BE RUNNABLE BY ACCIDENT.  Same form as the
# launcher's, and for the same reason: every constant this item must fix that
# THIS LANE COULD NOT MEASURE is a placeholder token, and this guard refuses
# while ANY remains.  It is the first executable statement.
#
# THE PATTERN IS ASSEMBLED FROM TWO HALVES so this guard's own source lines do
# not match it and the honest rule -- zero -- is expressible.  AND IT IS PLANTED
# BEFORE IT IS TRUSTED: a grep that matches nothing and reports success is the
# planted zero this lab keeps paying for (rule 3).
# ===========================================================================
FREEZE_TOK='__D8G_'"UNFROZEN__"
printf '%s\n' "SELFCHECK${FREEZE_TOK}SENTINEL" | grep -q "$FREEZE_TOK" || {
  echo "ABORT G-FREEZE.0 the freeze-token pattern cannot see a PLANTED token."
  echo "  A reader not shown able to see a non-zero is not evidence (rule 3),"
  echo "  so its zero on the real file proves nothing.  REFUSED."
  exit 3; }
UNFROZEN_TOKENS=$(grep -c "$FREEZE_TOK" "${BASH_SOURCE[0]}" || true)
if [ "${UNFROZEN_TOKENS:-0}" -gt 0 ]; then
  echo "ABORT G-FREEZE.0 this file still carries $UNFROZEN_TOKENS unfrozen placeholder line(s):"
  grep -n "$FREEZE_TOK" "${BASH_SOURCE[0]}" | sed 's/^/    /'
  echo "  STILL OWED, AND NONE OF IT IS GUESSABLE FROM A LANE'S DESK:"
  echo "   * MD5_LAUNCHER / MD5_GRADER / MD5_GENMESH -- these files exist but are NOT FROZEN"
  echo "     (d8g_run_arm.sh itself still carries two unfrozen tokens).  Pinning the md5 of a"
  echo "     file that is about to change is worse than not pinning it: it manufactures the"
  echo "     appearance of a freeze."
  echo "  A driver that ran on placeholders would produce a chain no pre-registration governs."
  exit 3
fi

HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d8g_run_arm.sh"
GRADER="$HERE/d8g_grade.py"
GENMESH="$HERE/d8g_genmesh.sh"
DECOMP="$HERE/d8g_decomposeParDict"
AGGPY="$HERE/d8g_aggregate_memory.py"
CPUPY="$HERE/d8g_cpuset_overlap.py"
IMG_SHIPPED=dafoam/opt-packages:latest
IMG_PATCHED=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple
CPUSET_REGISTERED=0,1,12,15
LEVELS="L1 L2 L3"
# section 2.2, registered; the ONLY mesh constant this driver may assert as frozen
cells_of() { case "$1" in L1) echo 5568 ;; L2) echo 44544 ;; L3) echo 356352 ;; *) echo "" ;; esac; }
H5_SAMPLES=45; H5_WINDOW_S=60
# THE AGGREGATE CEILING IS A FORMULA, NOT A LITERAL, AND IT IS NO LONGER A TOKEN:
# PREREGISTRATION.md AMENDMENT 2 (b) registers `AGG_CEILING = MemTotal_GiB - RESERVE_GIB`
# with RESERVE_GIB = 4.0, DERIVED on this box (MemTotal 30.644 GiB; worst arm cap 14 GiB;
# host non-container RSS measured 10.741 GiB, giving 24.741 presented against a 26.644
# ceiling).  D8R's 30.6 GiB IS NOT CARRIED ACROSS: against this MemTotal it is
# `MemTotal - 0.044`, i.e. the whole machine, a value that can essentially never refuse.
# The reserve travels; the ceiling is computed from the box the reading is taken on, so an
# instance change cannot leave a literal silently describing the wrong machine.
AGG_RESERVE_GIB=4.0
AGG_POLL_S=30; AGG_BOUND_S=14400
# ---- FROZEN INSTRUMENT HASHES.  See G-FREEZE.0 above for why five of the six are tokens.
MD5_LAUNCHER=7ce53b9242ac6e850cc330712d93d5b0
MD5_GRADER=12688063e20cbb6fa79cf08d0996d4e1
MD5_GENMESH=0d18d20d9bea13d1ef794892a1d4edd5
MD5_RUNSCRIPT=28c7819487a025a5f6554d38062a2b66
MD5_OF=f17b4a26fc5dcbbb44e9c820ba16df6c
# THE ONE HASH THIS FILE MAY ASSERT, AND WHY IT IS NOT A GUESS: d8g_decomposeParDict is a
# BYTE COPY of curriculum_D8R/d8r_decomposeParDict, which is FROZEN BEHIND A GRADED TWO-ROW
# PASS.  The hash was verified against both files by the lane that wrote this line.  The
# decomposition is therefore NOT a D8G choice at all -- it is D8R's graded one, unchanged.
MD5_DECOMP=1dbd9ead3f40a29f483444dc5fa1288b

test $# -ge 1 || { echo "ABORT usage: d8g_chain_driver.sh <ARM...>   (registered order: L1-P L2-P L3-P A2-P F2-P L1-S L2-S L3-S A2-S F2-S)"; exit 64; }
ARMS="$*"; STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/d8g_driver.pid"
cd "$HERE" || exit 4
for pair in "$MD5_LAUNCHER $LAUNCHER" "$MD5_GRADER $GRADER" "$MD5_GENMESH $GENMESH" "$MD5_DECOMP $DECOMP"; do
  echo "${pair% *}  ${pair#* }" | md5sum -c - || { echo "ABORT instrument md5 drifted before staging: ${pair#* }"; exit 4; }
done

# ---- ROOT AND LEVEL BASES.  THE DRIVER LAUNCHES NO MESH GENERATION. --------
# THE DRIVER DOES NOT CREATE THE RUN ROOT, AND THAT IS A SAFETY PROPERTY, NOT TIDINESS.
# d8g_genmesh.sh:127 creates it (`mkdir -p "$ROOT"`), as the step that first has something to
# put in it.  A driver that created it would mean MERELY RUNNING THIS FILE falsifies the
# "the run root does not exist" condition on which PREREGISTRATION.md's AMENDMENTS 1, 2 AND 3
# each rest -- an irreversible edit to the evidence for three registrations, made by a script
# that then aborts because there is nothing to run.  It refuses instead, and names the step.
if [ ! -d "$BASE" ]; then
  echo "ABORT the run root $BASE does not exist."
  echo "  This driver does not create it: d8g_genmesh.sh does, as the step that first has"
  echo "  something to put in it.  Creating it here would falsify the 'run root does not exist'"
  echo "  condition PREREGISTRATION.md's AMENDMENTS 1, 2 and 3 are each registered against."
  echo "  Run, per level:"
  for LV in $LEVELS; do echo "    bash $GENMESH $LV"; done
  exit 5
fi
MISSING=""
for LV in $LEVELS; do
  test -d "$BASE/base_$LV" || MISSING="$MISSING base_$LV"
  test -f "$BASE/mesh_record_$LV.json" || MISSING="$MISSING mesh_record_$LV.json"
done
if [ -n "$MISSING" ]; then
  echo "ABORT the level bases and their construction records must exist BEFORE any arm."
  echo "  MISSING:$MISSING"
  echo "  Mesh generation is a SEPARATELY COSTED step (section 6.3: 9.000 core-min) that writes"
  echo "  the evidence the comparator's G-MESH / G-SYS / G-BODY / G-TE read.  A driver that"
  echo "  generated it would make the geometry a side effect of the chain that consumes it."
  echo "  Run, per level, and only then re-fire this driver:"
  for LV in $LEVELS; do echo "    bash $GENMESH $LV"; done
  exit 5
fi

# ---- PER LEVEL: the registered cell count, the record's self-consistency, and the
# ---- decomposition overlay.  Two different kinds of claim, and they are labelled.
for LV in $LEVELS; do
  REC="$BASE/mesh_record_$LV.json"
  PTS="$BASE/base_$LV/constant/polyMesh/points.gz"
  test -f "$PTS" || { echo "ABORT base_$LV has no constant/polyMesh/points.gz"; exit 4; }
  RC_CELLS=$(python3 -c "import json,sys; print(json.load(open('$REC')).get('cells'))") || { echo "ABORT unreadable $REC"; exit 4; }
  WANT_CELLS=$(cells_of "$LV")
  if [ "$RC_CELLS" != "$WANT_CELLS" ]; then
    echo "ABORT level $LV: the mesh record says $RC_CELLS cells; section 2.2 registers $WANT_CELLS."
    echo "  This is a FROZEN CONSTANT and a mismatch is not a warning."
    exit 4
  fi
  RC_PTS=$(python3 -c "import json; print(json.load(open('$REC')).get('points_md5'))")
  GOT_PTS=$(md5sum "$PTS" | cut -d' ' -f1)
  if [ "$RC_PTS" != "$GOT_PTS" ]; then
    echo "ABORT level $LV: base_$LV/constant/polyMesh/points.gz ($GOT_PTS) does not match the"
    echo "  md5 its own construction record claims ($RC_PTS).  THIS IS A CONSISTENCY CHECK, NOT"
    echo "  A FROZEN CONSTANT -- re-coarsening is not byte-reproducible, so the points md5 is"
    echo "  not registerable; what IS checkable is that the record describes the mesh beside it."
    exit 4
  fi
  cp -a "$DECOMP" "$BASE/base_$LV/system/decomposeParDict" || { echo "ABORT overlay decomposeParDict into base_$LV"; exit 4; }
  echo "$MD5_DECOMP  $BASE/base_$LV/system/decomposeParDict" | md5sum -c - || { echo "ABORT staged decomposeParDict md5 in base_$LV"; exit 4; }
  # ---- MODEL DICTS.  STAGED FROM THE REGISTERED ARCHIVE, ASSERTED, THEN MOVED.
  ARCH_CONST=/home/ubuntu/certonomous-runs/A6-crm-wing/constant
  for d in thermophysicalProperties turbulenceProperties; do
    test -f "$ARCH_CONST/$d" || { echo "ABORT model dict $d absent from the registered archive $ARCH_CONST"; exit 4; }
    cp -a "$ARCH_CONST/$d" "$BASE/base_$LV/constant/.$d.staging" || { echo "ABORT stage $d into base_$LV"; exit 4; }
  done
  TH="$BASE/base_$LV/constant/.thermophysicalProperties.staging"
  TT="$BASE/base_$LV/constant/.turbulenceProperties.staging"
  grep -qE '^[[:space:]]*RASModel[[:space:]]+SpalartAllmaras;' "$TT" \
    || { echo "ABORT staged turbulenceProperties does not declare SpalartAllmaras"; rm -f "$TH" "$TT"; exit 4; }
  grep -qE '^[[:space:]]*turbulence[[:space:]]+on;' "$TT" \
    || { echo "ABORT staged turbulenceProperties does not have turbulence on"; rm -f "$TH" "$TT"; exit 4; }
  grep -q 'hePsiThermo' "$TH" \
    || { echo "ABORT staged thermophysicalProperties is not hePsiThermo (DARhoSimpleCFoam is compressible)"; rm -f "$TH" "$TT"; exit 4; }
  # THE DISCRIMINATING CHECK IS ARITHMETIC, NOT A grep.  The frozen d8g_runScript.py
  # computes rho0 = p0 / T0 / 287.0, so 287.0 is a REGISTERED constant of this item.
  # The staged gas must reproduce it from its OWN molWeight: R = 8314.462618/W.
  # A file-presence check passes any gas; this one does not.
  GASR=$(python3 -c "
import re,sys
t=open('$TH').read()
m=re.search(r'^\s*molWeight\s+([0-9.eE+-]+)\s*;', t, re.M)
if not m: sys.exit('MISSING molWeight')
print('%.4f' % (8314.462618/float(m.group(1))))
") || { echo "ABORT could not read molWeight from the staged thermo dict: $GASR"; rm -f "$TH" "$TT"; exit 4; }
  python3 -c "
import sys
sys.exit(0 if abs(float('$GASR') - 287.0) <= 0.01 else 1)" || {
    echo "ABORT THE STAGED GAS IS NOT THE REGISTERED GAS: its molWeight gives R=$GASR J/kg/K,"
    echo "  but the frozen d8g_runScript.py computes rho0 = p0/T0/287.0.  A wrong gas would"
    echo "  silently mis-normalise every force this arm reports.  REFUSED."
    rm -f "$TH" "$TT"; exit 4; }
  # Only now, with every assertion passed, do the dicts enter the case.
  mv "$TH" "$BASE/base_$LV/constant/thermophysicalProperties" || { echo "ABORT move thermo into base_$LV"; exit 4; }
  mv "$TT" "$BASE/base_$LV/constant/turbulenceProperties"     || { echo "ABORT move turbulence into base_$LV"; exit 4; }
  echo "D8G_MODEL_DICTS_STAGED level=$LV source=$ARCH_CONST SpalartAllmaras=on thermo=hePsiThermo R_from_dict=$GASR registered_R=287.0"
  echo "D8G_LEVEL_STAGED level=$LV cells=$RC_CELLS points_md5=$GOT_PTS decomposeParDict=$MD5_DECOMP"
done

# ---- the two instruments the arms execute, staged once at the run root ------
# THE THREE STAGED INSTRUMENTS THE LAUNCHER's INSTRUMENT_MD5S MANIFEST CHECKS.  The
# decomposeParDict is ALSO overlaid per level above; this root copy is the one the manifest
# names, because the manifest is level-independent (the launcher only substitutes @BASE@).
cp -a "$HERE/d8g_runScript.py" "$HERE/d8g_of.py" "$HERE/d8g_decomposeParDict" "$BASE/" \
  || { echo "ABORT copy instruments to $BASE"; exit 4; }
{ echo "$MD5_RUNSCRIPT  $BASE/d8g_runScript.py"; echo "$MD5_OF  $BASE/d8g_of.py"; } | md5sum -c - \
  || { echo "ABORT staged instrument md5"; exit 4; }

# ---- the ledger opens with an exact ITEM= line; staging metadata on a line that
# ---- does NOT start with ITEM= (D5-DRIVER-DEF-1 corrected form, inherited).
if [ ! -f "$BASE/ledger.txt" ]; then
  echo "ITEM=D8G" > "$BASE/ledger.txt"
  echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) levels=[$LEVELS] decomposeParDict=$MD5_DECOMP genmesh=$MD5_GENMESH" >> "$BASE/ledger.txt"
  echo "D8G_ROOT_STAGED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ) mode=$(stat -c '%a' "$BASE")"
else
  echo "D8G_ROOT_PRESENT base=$BASE (ledger not re-opened)"
fi

if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."; exit 3
  fi
fi
echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"; echo "chain_done stamp=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ arms=[$ARMS] last=[$(tail -n 1 "$STATUS" 2>/dev/null)]" >> "$BASE/CHAIN_DONE"' EXIT
echo "D8G_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS]"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"

mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
# section 5's THREE-TIER table.  L3 ADJOINT IS NOT AN ARM OF THIS ITEM (section 7).
cap_mem_gib()  { case "$1" in L1-*|L2-*) echo 6 ;; L3-*) echo 12 ;; A2-*|F2-*) echo 14 ;; *) echo "" ;; esac; }
h5_floor_gib() { case "$1" in L1-*|L2-*) echo 8.0 ;; L3-*) echo 14.0 ;; A2-*|F2-*) echo 16.0 ;; *) echo "" ;; esac; }
img_of()       { case "$1" in *-S) echo "$IMG_SHIPPED" ;; *-P) echo "$IMG_PATCHED" ;; *) echo "" ;; esac; }
# THE PREREQUISITE ARM.  An F arm's FD table must sit beside ITS OWN ROW's adjoint.
dep_of()       { case "$1" in F2-P) echo A2-P ;; F2-S) echo A2-S ;; *) echo "" ;; esac; }

CHAIN_RC=0
for ARM in $ARMS; do
  IMG=$(img_of "$ARM"); CAP=$(cap_mem_gib "$ARM"); H5_FLOOR_GIB=$(h5_floor_gib "$ARM")
  if [ -z "$IMG" ] || [ -z "$CAP" ] || [ -z "$H5_FLOOR_GIB" ]; then
    echo "ABORT arm $ARM names no registered row/cap/floor.  The ten registered arms are:"
    echo "  L1-P L2-P L3-P A2-P F2-P L1-S L2-S L3-S A2-S F2-S"
    echo "chain=ABORT arm=$ARM reason=unregistered_arm stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=64; break
  fi
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before arm $ARM"; echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=4; break; }
  echo "preflight arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ image=$IMG cap_GiB=$CAP h5_floor_GiB=$H5_FLOOR_GIB" > "$BASE/STATUS.$ARM"

  # ---- ALREADY BOUGHT ------------------------------------------------------
  if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT ALREADY_BOUGHT arm $ARM has an rc=0 ledger row; a second record for one run is the defect."
    echo "rc=3 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=ALREADY_BOUGHT" >> "$BASE/STATUS.$ARM"
    echo "chain=REFUSED_ALREADY_BOUGHT arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=3; break
  fi

  # ---- THE PREREQUISITE, CHECKED FIRST.  D8G DELTA (1): the launcher checks this
  # ---- too, but only AFTER the driver's 60 s H5 window and a possibly four-hour
  # ---- aggregate wait.  A mis-ordered chain should cost a second, not an hour.
  DEP=$(dep_of "$ARM")
  if [ -n "$DEP" ]; then
    DEPOK=yes
    grep -aq "^ARM=$DEP .* rc=0 " "$BASE/ledger.txt" 2>/dev/null || DEPOK=no
    test -f "$BASE/$DEP/d8g_A.json" || DEPOK=no
    if [ "$DEPOK" != "yes" ]; then
      echo "ABORT arm $ARM requires $DEP -- an rc=0 ledger row AND $DEP/d8g_A.json."
      echo "  ledger_row_rc0=$(grep -acq "^ARM=$DEP .* rc=0 " "$BASE/ledger.txt" 2>/dev/null && echo yes || echo no) artefact=$(test -f "$BASE/$DEP/d8g_A.json" && echo present || echo absent)"
      echo "  The FD table must stand beside ITS OWN ROW's adjoint: the comparator refuses on"
      echo "  adjoint_source.md5 != md5($DEP/d8g_A.json), and a patched row never stands in for"
      echo "  a shipped one."
      echo "rc=5 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=PREREQUISITE_MISSING dep=$DEP" >> "$BASE/STATUS.$ARM"
      echo "chain=STOPPED_PREREQUISITE arm=$ARM dep=$DEP stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=5; break
    fi
    echo "D8G_PREREQUISITE arm=$ARM dep=$DEP ok=yes a_md5=$(md5sum "$BASE/$DEP/d8g_A.json" | cut -d' ' -f1)"
  fi

  # ---- H5: a WINDOW of MemAvailable, every sample above the PER-ARM floor ----
  H5_FILE="$BASE/${ARM}_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"; BELOW=0; N=0; MIN=999; MAX=0
  STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))")
  for _ in $(seq 1 $H5_SAMPLES); do
    s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"
    MIN=$(python3 -c "print(min($MIN,$s))"); MAX=$(python3 -c "print(max($MAX,$s))")
    [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1))
    sleep "$STEP"
  done
  echo "D8G_H5_WINDOW arm=$ARM n=$N window_s=$H5_WINDOW_S floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAX samples_below_floor=$BELOW file=$(basename "$H5_FILE")"
  if [ "$BELOW" -gt 0 ] || [ "$N" -ne "$H5_SAMPLES" ]; then
    echo "ABORT H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB.  A batch that OOMs is worse than a batch that queues.  REFUSED."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_REFUSED below=$BELOW min_GiB=$MIN" >> "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_H5 arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=6; break
  fi

  # ---- AGGREGATE: wait-and-retry, bounded; every wait written to STATUS.<arm> ----
  WAITED=0; AGG_SERIES="$BASE/${ARM}_aggregate_series.txt"; AGG_BLOCKED=no
  while true; do
    AGG=$(python3 "$AGGPY" "$CAP" "reserve=$AGG_RESERVE_GIB")
    echo "$(date -u +%s) $AGG" >> "$AGG_SERIES"
    if [ "$(printf '%s' "$AGG" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ]; then break; fi
    if [ "$WAITED" -ge "$AGG_BOUND_S" ]; then
      echo "ABORT AGGREGATE still over (MemTotal - ${AGG_RESERVE_GIB} GiB) after ${WAITED}s.  BLOCKED.  Series: $(basename "$AGG_SERIES")"
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=AGGREGATE_BLOCKED_AT_BOUND waited=$WAITED series=$(basename "$AGG_SERIES")" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_AGGREGATE arm=$ARM waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; AGG_BLOCKED=yes; break
    fi
    echo "AGGREGATE_WAIT waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM $AGG" >> "$BASE/STATUS.$ARM"
    sleep "$AGG_POLL_S"; WAITED=$((WAITED+AGG_POLL_S))
  done
  if [ "$AGG_BLOCKED" = "yes" ]; then CHAIN_RC=6; break; fi
  echo "D8G_AGGREGATE arm=$ARM waited=$WAITED $AGG"

  # ---- G-CPUSET: no LIVE container may share a core with this item's cpuset ----
  CWAITED=0; CPU_SERIES="$BASE/${ARM}_cpuset_series.txt"; CPU_BLOCKED=no
  while true; do
    CPU=$(python3 "$CPUPY" "$CPUSET_REGISTERED" "d8g_")
    echo "$(date -u +%s) $CPU" >> "$CPU_SERIES"
    if [ "$(printf '%s' "$CPU" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ]; then break; fi
    if [ "$CWAITED" -ge "$AGG_BOUND_S" ]; then
      echo "ABORT G-CPUSET a live container still shares a core of $CPUSET_REGISTERED after ${CWAITED}s.  BLOCKED.  Series: $(basename "$CPU_SERIES")"
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=CPUSET_BLOCKED_AT_BOUND waited=$CWAITED series=$(basename "$CPU_SERIES")" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_CPUSET arm=$ARM waited=$CWAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CPU_BLOCKED=yes; break
    fi
    echo "CPUSET_WAIT waited=$CWAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM $CPU" >> "$BASE/STATUS.$ARM"
    sleep "$AGG_POLL_S"; CWAITED=$((CWAITED+AGG_POLL_S))
  done
  if [ "$CPU_BLOCKED" = "yes" ]; then CHAIN_RC=6; break; fi
  echo "D8G_CPUSET arm=$ARM waited=$CWAITED $CPU"

  echo "D8G_DRIVER arm=$ARM image=$IMG begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "D8G_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN aggregate_waited_s=$WAITED cpuset_waited_s=$CWAITED" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=$rc; break; fi
done
[ "$CHAIN_RC" -eq 0 ] && echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"

# ---- the FROZEN comparator on the artefacts at chain end (ZERO COMPUTE).  Its rc is
# ---- INFRASTRUCTURE (L-342) and is NEVER the verdict: the verdict is in the JSON.
GSTAMP=$(date -u +%Y%m%dT%H%M%SZ)
if echo "$MD5_GRADER  $GRADER" | md5sum -c - > /dev/null; then
  python3 "$GRADER" --root "$BASE" --out "$BASE/D8G_grade_${GSTAMP}.json" > "$BASE/D8G_grade_${GSTAMP}.out" 2>&1; GRC=$?
  echo "grader_rc=$GRC stamp=$GSTAMP out=D8G_grade_${GSTAMP}.json note=comparator-exit-status-NOT-the-verdict" >> "$STATUS"
else
  echo "grader_rc=NOT_RUN stamp=$GSTAMP note=grader-md5-drifted-at-chain-end" >> "$STATUS"
fi
echo "D8G_DRIVER end=$(date -u +%Y%m%dT%H%M%SZ) chain_rc=$CHAIN_RC"
exit "$CHAIN_RC"

# =============================================================================
# AMENDMENT (candidate) -- 2026-09-11 -- TWO STALE INSTRUMENT PINS
# lines whose number changed above this section: 0
#
# MD5_LAUNCHER  05b7f8b1446968b64bc74d2f0f531fcb -> 7ce53b9242ac6e850cc330712d93d5b0
# MD5_GENMESH   5b9db5102a4ffe04abffec6f7648d0c1 -> 0d18d20d9bea13d1ef794892a1d4edd5
# (MD5_GRADER and MD5_DECOMP were checked and are CORRECT; they are not touched.)
#
# MEASURED 2026-09-11 23:24:54Z: the driver aborted at its FIRST pin --
#   "ABORT instrument md5 drifted before staging: .../d8g_run_arm.sh"
# -- because d8g_run_arm.sh was re-frozen three times tonight (ADDENDA 1-3) and
# the driver still pinned its pre-addendum hash.
#
# *** THE SECOND PIN IS THE MORE SERIOUS ONE, AND THE DRIVER NEVER REACHED IT.
# MD5_GENMESH pinned 5b9db5102a4ffe04abffec6f7648d0c1, which git shows is the
# genmesh at commit 075f6edf6 (17:50) -- the ORIGINAL freeze, superseded by
# AMENDMENT 4 at 18:37 (40ef1f42d) and again by AMENDMENT 5 at 21:58
# (5fc6aa53a).  SO THIS PIN HAS BEEN STALE SINCE 18:37, HOURS BEFORE TONIGHT'S
# LAUNCHER WORK, AND THE CHAIN DRIVER HAS NOT BEEN RUNNABLE SINCE THEN.  Fixing
# only the pin that fired would have produced one more abort at the next one. ***
#
# THE STRUCTURAL POINT, for whoever reads this next: a frozen instrument that
# pins the md5 of ANOTHER frozen instrument creates a CASCADE -- every amendment
# to the pinned file invalidates the pinning file, and because both are frozen,
# one repair costs two amendments.  Tonight that cascade was invisible because
# the driver had not been run since the first link moved.  The pins are correct
# as a mechanism (they are what makes "not built by the frozen path" detectable);
# the cost is real and belongs in the item's maintenance record, not hidden.
# =============================================================================
