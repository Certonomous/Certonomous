#!/usr/bin/env bash
# ===========================================================================
# D19O CHAIN DRIVER -- the compressible single-point shape optimisation.
# SEVEN ARMS, BOTH ROWS, np = 1 THROUGHOUT.
#
# ARM ORDER IS NOT COSMETIC:
#     MESH  O-S  XE-S  FE-S  O-P  XE-P  FE-P
# Each row's endpoint arms follow THAT ROW'S optimiser, because
# `DAFOAM_CHARTER.md` section 9 requires the FD check at the FINAL DESIGN POINT
# and each row has its OWN final design point.  `XE-S` reads `O-S/d19o_xopt.json`
# and `XE-P` reads `O-P/d19o_xopt.json`; the launcher refuses to stage an
# endpoint arm whose own row's optimum does not exist, and `d19o_xf.py` refuses
# again if the artefact's row does not match the arm's.
#
# THE SHIPPED ROW RUNS FIRST AND ITS FAILURE IS THE RESULT, NOT WASTE.
# `DAFOAM_CHARTER.md` section 6: a DAFoam verdict is two rows or it is not a
# verdict about DAFoam.  D15 measured the SHIPPED adjoint missing FD by 44.8738 %
# on `shape[6]` on this very ground, where PATCHED misses by 0.0072 %, and
# `shape[6]` carries 76.414 % of the CD gradient's norm -- i.e. the shipped
# optimiser would follow a ~45 %-wrong DOMINANT search direction.  A shipped row
# that optimises badly IS this item's most informative single output.  Registered
# so that nobody later reads a shipped-row failure as a wasted arm.
#
# Started ONLY detached, so it outlives the agent that started it:
#   setsid nohup bash d19o_chain_driver.sh MESH O-S XE-S FE-S O-P XE-P FE-P \
#       > <root>/chain_launch.out 2>&1 &
# NOTE `setsid timeout cmd` returns 0 for EVERY outcome, so rc is captured INSIDE
# this script, never around the setsid line.
# ===========================================================================
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d19o_run_arm.sh"
GRADER="$HERE/d19o_grade.py"
XF="$HERE/d19o_xf.py"
AGE="$HERE/d19o_age_guard.py"
STALL="$HERE/d19o_stall.py"
AGGMEM="$HERE/d19o_aggregate_memory.py"
MARKER="$HERE/d19o_stop_marker.sh"
RUNSCRIPT="$HERE/d19o_runScript.py"
DECOMP="$HERE/d19o_decomposeParDict"

IMG_SHIPPED=dafoam/opt-packages:latest
IMG_PATCHED=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D19O-a1-naca0012-subsonic-optimisation
TUT_SRC=/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/subsonic

H5_FLOOR_GIB=16.0; H5_SAMPLES=45; H5_WINDOW_S=60
AGG_POLL_S=30; AGG_BOUND_S=14400; AGG_CEILING_GIB=30.6; ARM_MEM_GIB=12.0
DECLARED_ARMS=7

# ---- FROZEN INSTRUMENT PINS (PREREGISTRATION.md section 7) ------------------
# Set ONCE, for ALL of them together, by `d19o_repin.sh`.  A pin table filled in
# for the files that happen to exist, inside the executable that stages every
# arm, would read agreement on every pin it holds while a file this driver
# executes is still missing.  That is `SO2a-DRIVER-DEF-1` and it is why
# EXISTENCE IS ASSERTED FIRST AND SEPARATELY, BELOW, BEFORE ANY md5.
MD5_LAUNCHER=2dbb88346c0e7211ae0e9cd65a4041b9
MD5_GRADER=419ce2363743bd16109826f2bf75d4f2
MD5_XF=6f5e7ed9db76bf429b4031c6d87a8bf6
MD5_AGE=0293334b1e63f69fc2af8f54ce922a6c
MD5_STALL=c719951741b6d76faa07569d2da8b7de
MD5_AGGMEM=e4ad8d12d60ed2ad4710ce78e60d67cc
MD5_MARKER=c0ea73225089ce77ff8a558351c3164d
MD5_RUNSCRIPT=a5e18503ea29d0e37c3cf1668533cd34
MD5_DECOMP=68ecc827562886fb43c3aedb0627b344
# the shipped tutorial's INPUT bytes, frozen here because the checkout is not.
# RE-MEASURED at this freeze; tutorial commit d3b7e38b058aba2a98a74092e15c41ec455c570d.
MD5_TUT_RUNSCRIPT=6537fa7641c4ccb20056f60f96f63b11
MD5_TUT_GEN=681f10659eb90457fca13fc933008b93
MD5_TUT_PREPROC=e25c8f8c32886112e3f9591196c695ad
MD5_TUT_PS=51dfed28e1bdb4cd33e0d8d7dabd586a
MD5_TUT_SS=4a6b8ef4501494c7693b71e88a2eabbf
MD5_TUT_FFD=6ddf378b028d03d8a18270488bee1759

test $# -ge 1 || { echo "ABORT usage: d19o_chain_driver.sh <ARM...>"; exit 64; }
ARMS="$*"
for a in $ARMS; do
  case "$a" in
    MESH|O-S|XE-S|FE-S|O-P|XE-P|FE-P) ;;
    *) echo "ABORT arm '$a' is not a registered D19O arm."
       echo "  Registered: MESH O-S XE-S FE-S O-P XE-P FE-P"
       exit 64 ;;
  esac
done
STATUS="$BASE/STATUS.D19O_chain"; PIDFILE="$BASE/d19o_driver.pid"
cd "$HERE" || exit 4

# ===========================================================================
# SECTION 18.3 -- EXISTENCE IS ASSERTED BEFORE ANY md5, FIRST AND SEPARATELY.
# `SO2a-DRIVER-DEF-1`: a gate was frozen without its implementation and its
# instrument table read "eight of eight AGREE" while the script that implemented
# the gate -- executed by the frozen driver, by name, inside its poll loop -- was
# absent from the freeze commit.  Existence and md5-agreement are DIFFERENT
# QUESTIONS and the second cannot be inferred from the first at any level of
# agreement: not at 8 of 8, not at 800 of 800.
# ===========================================================================
MISSING=""
for f in "$LAUNCHER" "$GRADER" "$XF" "$AGE" "$STALL" "$AGGMEM" "$MARKER" \
         "$RUNSCRIPT" "$DECOMP"; do
  test -f "$f" || MISSING="$MISSING $f"
done
if [ -n "$MISSING" ]; then
  echo "ABORT section 18.3 EXISTENCE: the frozen instrument set is incomplete."
  echo "  A registered gate whose implementing file is not present is not frozen --"
  echo "  it is UNIMPLEMENTED, and the item does not launch.  Missing:$MISSING"
  exit 4
fi
echo "D19O_18_3_EXISTENCE_OK files=9 (asserted BEFORE any md5)"

# ---- ONLY NOW, THE HASHES ---------------------------------------------------
for v in "$MD5_LAUNCHER" "$MD5_GRADER" "$MD5_XF" "$MD5_AGE" "$MD5_STALL" \
         "$MD5_AGGMEM" "$MD5_MARKER"; do
  case "$v" in
    *_UNSET) echo "ABORT a frozen pin is still the fail-closed sentinel ($v)."
             echo "  Run d19o_repin.sh and re-issue PREREGISTRATION.md section 7."
             exit 4 ;;
  esac
done
{ echo "$MD5_LAUNCHER  $LAUNCHER"; echo "$MD5_GRADER  $GRADER"; echo "$MD5_XF  $XF";
  echo "$MD5_AGE  $AGE"; echo "$MD5_STALL  $STALL"; echo "$MD5_AGGMEM  $AGGMEM";
  echo "$MD5_MARKER  $MARKER"; echo "$MD5_RUNSCRIPT  $RUNSCRIPT";
  echo "$MD5_DECOMP  $DECOMP"; } | md5sum -c - \
  || { echo "ABORT frozen instrument md5 drifted before staging"; exit 4; }
echo "D19O_PINS_OK nine files, existence asserted first, then md5"

# ---- THE INSTRUMENT SELFTESTS RUN BEFORE ANY COMPUTE IS BOUGHT --------------
# A comparator whose controls do not fire grades nothing, and finding that out
# AFTER the arms are bought is finding it out too late.
for t in "python3 $AGE --selftest" "python3 $STALL --selftest" \
         "python3 $HERE/d19o_xf_selftest.py" "python3 $HERE/d19o_grade_selftest.py"; do
  $t > "$HERE/$(echo "$t" | md5sum | cut -c1-8).selftest.out" 2>&1 || {
    echo "ABORT an instrument SELFTEST refused: $t"
    echo "  Its controls do not fire, so it grades nothing.  No arm is launched."
    exit 2; }
done
echo "D19O_SELFTESTS_OK age_guard + stall + instrument + comparator"

# ---- ROOT STAGING on the first fire only ------------------------------------
if [ ! -d "$BASE" ]; then
  test -d "$TUT_SRC" || { echo "ABORT tutorial source absent: $TUT_SRC"; exit 4; }
  { echo "$MD5_TUT_RUNSCRIPT  $TUT_SRC/runScript.py"; echo "$MD5_TUT_GEN  $TUT_SRC/genAirFoilMesh.py";
    echo "$MD5_TUT_PREPROC  $TUT_SRC/preProcessing.sh";
    echo "$MD5_TUT_PS  $TUT_SRC/profiles/NACA0012PS.profile";
    echo "$MD5_TUT_SS  $TUT_SRC/profiles/NACA0012SS.profile";
    echo "$MD5_TUT_FFD  $TUT_SRC/FFD/wingFFD.xyz"; } | md5sum -c - \
    || { echo "ABORT tutorial input md5 drifted (the checkout moved under this item; nothing staged)"; exit 4; }
  mkdir -p "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
  chmod 777 "$BASE" || { echo "ABORT chmod 777 $BASE (L-251)"; exit 4; }
  mkdir -p "$BASE/base" || exit 4
  cp -a "$TUT_SRC/0.orig" "$TUT_SRC/FFD" "$TUT_SRC/constant" "$TUT_SRC/system" \
        "$TUT_SRC/profiles" "$TUT_SRC/genAirFoilMesh.py" "$TUT_SRC/preProcessing.sh" \
        "$BASE/base/" || { echo "ABORT copy tutorial inputs"; exit 4; }
  rm -rf "$BASE/base/constant/polyMesh" 2>/dev/null
  # D15's decomposeParDict VERBATIM, so the mesh this item builds is
  # byte-identical to the one D15/D19/D19R measured on and the MESH arm's
  # identity assertion can be made at all.  At np = 1 `decomposePar` never runs,
  # so this file is never rewritten -- which is exactly why D19R2's
  # MANIFEST_ENTRY_MUTATED blocker cannot fire here.
  cp -a "$DECOMP" "$BASE/base/system/decomposeParDict" \
    || { echo "ABORT overlay decomposeParDict"; exit 4; }
  cp -a "$RUNSCRIPT" "$XF" "$STALL" "$BASE/" || { echo "ABORT copy instruments"; exit 4; }
  echo "ITEM=D19O" > "$BASE/ledger.txt"
  echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) tut_src=$TUT_SRC rows=SHIPPED_AND_PATCHED np=1" >> "$BASE/ledger.txt"

  # ---- THE COST, REGISTERED BEFORE THE FIRST ARM FIRES (rule 12) -----------
  cat > "$BASE/COST_ESTIMATE.txt" <<EST
D19O -- COST REGISTERED BEFORE LAUNCH (CLAUDE.md rule 12)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
unit=core-minutes (wall_s x ranks / 60)
  arm    ranks   predicted   cap
  MESH     1        0.20      5.0
  O-S      1        7.57     40.0
  XE-S     1        1.40     10.0
  FE-S     1        2.98     20.0
  O-P      1        7.57     40.0
  XE-P     1        1.40     10.0
  FE-P     1        2.98     20.0
  ITEM             24.10    145.0
band (P_COST): [15.0, 65.0] core-min.
THE OPTIMISER ARMS ARE PRICED AT AN EXPECTED MAJOR COUNT, NOT AT max_iter.
  SO-3 registered 228.59 core-min and spent 28.900 (ratio 0.126x) because its
  IPOPT arms were priced at their max_iter of 50 and converged in 10.  Here the
  O arms are priced at EXPECTED_MAJOR_ROWS = 12 -- MEASURED: SO-1bR O-P, SO-1bR
  O-S and D1 armO each returned exactly 11 IPOPT iterations / 12 table rows on
  this A1 case at np=1 -- and max_iter = 40 is the CAP, priced into the 40.0
  core-min per-arm cap and nowhere else.
basis: 0.3924 core-min/major [MEASURED, incompressible A1 single-point IPOPT at
  np=1: SO-1bR O-P 4.700/12 = 0.3917 and O-S 4.717/12 = 0.3931, agreeing to
  0.36 %] x 1.6086 [MEASURED compressible/incompressible primal ratio on THIS
  4,032-cell mesh at np=1: D19 S1 51 s / 12 primals = 4.250 s against SO-3
  FE-S 267 s / 102 primals = 2.618 s and FE-P 272/102 = 2.667 s, mean 2.642 s]
  = 0.6312 core-min/major [EXTRAPOLATED -- the ratio is measured on the PRIMAL
  and carried onto a major that is primal + 2 adjoints + mesh warp].
cost_basis: core-minutes are MEASURED from this launcher's own per-arm ledger
  rows.  Dollars are DERIVED at the c7a.4xlarge rate of \$0.0513/core-h:
  \$0.0206 point, \$0.1240 at the ceiling.  THAT RATE IS REPORTED BY THE OWNER
  (Sanaa, 2026-08-21/22) AND IS NOT MEASURED BY THIS BOX -- the box cannot read
  its own billing (COMPUTE_BUDGET_CHARTER.md section 5).  No dollar figure here
  is a measurement and none is presented as one.  GPU: 0 GPU-h.
STOP RULE: an arm exceeding its cap STOPS.  An overrun does not get a new budget.
EST
  echo "D19O_ROOT_STAGED base=$BASE mode=$(stat -c '%a' "$BASE")"
  echo "D19O_ESTIMATE_REGISTERED 24.10 core-min predicted / 145.0 ceiling"
else
  echo "D19O_ROOT_PRESENT base=$BASE (not re-staged)"
fi

{ echo "$MD5_RUNSCRIPT  $BASE/d19o_runScript.py"; echo "$MD5_XF  $BASE/d19o_xf.py";
  echo "$MD5_STALL  $BASE/d19o_stall.py";
  echo "$MD5_DECOMP  $BASE/base/system/decomposeParDict";
  echo "$MD5_TUT_GEN  $BASE/base/genAirFoilMesh.py";
  echo "$MD5_TUT_PREPROC  $BASE/base/preProcessing.sh";
  echo "$MD5_TUT_PS  $BASE/base/profiles/NACA0012PS.profile";
  echo "$MD5_TUT_SS  $BASE/base/profiles/NACA0012SS.profile";
  echo "$MD5_TUT_FFD  $BASE/base/FFD/wingFFD.xyz"; } | md5sum -c - \
  || { echo "ABORT staged instrument/input md5"; exit 4; }
test -f "$BASE/base/0.orig/U" || { echo "ABORT staged base/ has no 0.orig/U"; exit 4; }

if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."
    exit 3
  fi
fi
echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"' EXIT
echo "D19O_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS]"
echo "chain=started arms=[$ARMS] declared=$DECLARED_ARMS pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) rows=SHIPPED_AND_PATCHED np=1" >> "$STATUS"

image_of() {
  case "$1" in
    MESH|O-S|XE-S|FE-S) echo "$IMG_SHIPPED" ;;
    O-P|XE-P|FE-P)      echo "$IMG_PATCHED" ;;
  esac
}
mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }

CHAIN_RC=0
EXECUTED=0
for ARM in $ARMS; do
  IMG=$(image_of "$ARM")
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || {
    echo "ABORT launcher md5 drifted before arm $ARM"
    echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    CHAIN_RC=4; break; }
  echo "preflight arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ image=$IMG" > "$BASE/STATUS.$ARM"

  if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT ALREADY_BOUGHT arm $ARM has an rc=0 ledger row; a second record for one run is the defect."
    echo "rc=3 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=ALREADY_BOUGHT" >> "$BASE/STATUS.$ARM"
    echo "chain=REFUSED_ALREADY_BOUGHT arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    CHAIN_RC=3; break
  fi

  # ---- H5: a WINDOW of MemAvailable, every sample above the floor -----------
  H5_FILE="$BASE/${ARM}_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"; BELOW=0; N=0; MIN=999
  STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))")
  for _ in $(seq 1 $H5_SAMPLES); do
    s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"
    MIN=$(python3 -c "print(min($MIN,$s))")
    [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1))
    sleep "$STEP"
  done
  echo "D19O_H5_WINDOW arm=$ARM n=$N floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN samples_below_floor=$BELOW"
  if [ "$BELOW" -gt 0 ] || [ "$N" -ne "$H5_SAMPLES" ]; then
    echo "ABORT H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB.  A batch that OOMs is worse than a batch that queues."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_REFUSED below=$BELOW min_GiB=$MIN" >> "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_H5 arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    CHAIN_RC=6; break
  fi

  # ---- THE AGGREGATE MEMORY CEILING, IN THE WAITING FORM --------------------
  # Every wait is a LINE in STATUS.<arm>; at the bound the chain STOPS and names
  # the series file.  A block DISCARDS the arm's remaining budget and buys
  # nothing, and this driver says so where the guard fires.
  AGG_SERIES="$BASE/${ARM}_aggregate_series.txt"
  WAITED=0; AGG_OK=no
  while [ "$WAITED" -lt "$AGG_BOUND_S" ]; do
    AGGOUT=$(python3 "$AGGMEM" "$ARM_MEM_GIB" "$AGG_CEILING_GIB" 2>&1); ARC=$?
    echo "$(date -u +%s) rc=$ARC $AGGOUT" >> "$AGG_SERIES"
    if [ "$ARC" -eq 0 ]; then AGG_OK=yes; break; fi
    if [ "$ARC" -eq 2 ]; then
      echo "ABORT the aggregate-memory READER refused (rc=2); it is not a WAIT."
      echo "chain=STOPPED_AGGMEM_REFUSE arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
      CHAIN_RC=2; break
    fi
    echo "wait arm=$ARM aggregate_ceiling_GiB=$AGG_CEILING_GIB waited_s=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$BASE/STATUS.$ARM"
    sleep "$AGG_POLL_S"; WAITED=$((WAITED+AGG_POLL_S))
  done
  if [ "$CHAIN_RC" -ne 0 ]; then break; fi
  if [ "$AGG_OK" != "yes" ]; then
    echo "ABORT aggregate memory stayed above $AGG_CEILING_GIB GiB for the whole ${AGG_BOUND_S}s bound."
    echo "  A block DISCARDS this arm's remaining budget and buys nothing.  Series: $AGG_SERIES"
    echo "chain=STOPPED_AGGMEM_BOUND arm=$ARM series=$AGG_SERIES stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    CHAIN_RC=6; break
  fi
  echo "D19O_AGGMEM_GO arm=$ARM waited_s=$WAITED series=$(basename "$AGG_SERIES")"

  echo "D19O_DRIVER arm=$ARM image=$IMG begin=$(date -u +%Y%m%dT%H%M%SZ)"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  EXECUTED=$((EXECUTED+1))
  echo "D19O_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then
    echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    CHAIN_RC=$rc; break
  fi
done

echo "chain=ARMS_COMPLETE declared=$DECLARED_ARMS executed=$EXECUTED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"

# ---- the FROZEN grader on the artefacts (zero compute) ----------------------
# The comparator's EXIT STATUS IS INFRASTRUCTURE AND IS NOT THE VERDICT (L-342).
# `--out` is MANDATORY and the DRIVER names it: SO-1c refused because a
# comparator composed its own stamped path and wrote to an address the driver
# never looked at.
GSTAMP=$(date -u +%Y%m%dT%H%M%SZ)
GRADE_OUT="$BASE/D19O_grade_${GSTAMP}.json"
if echo "$MD5_GRADER  $GRADER" | md5sum -c - > /dev/null; then
  python3 "$GRADER" --root "$BASE" --out "$GRADE_OUT" \
      > "$BASE/D19O_grade_${GSTAMP}.out" 2>&1
  GRC=$?
  echo "grader_rc=$GRC stamp=$GSTAMP out=$(basename "$GRADE_OUT") note=comparator-exit-status-NOT-the-verdict" >> "$STATUS"
else
  GRC=4; GRADE_OUT=""
  echo "grader_rc=NOT_RUN stamp=$GSTAMP note=grader-md5-drifted-at-chain-end" >> "$STATUS"
fi

# ---- THE STOP MARKER IS WRITTEN ON EVERY EXIT PATH -------------------------
bash "$MARKER" "$BASE" "chain_rc=$CHAIN_RC grader_rc=$GRC executed=$EXECUTED/$DECLARED_ARMS" \
     "$GRADE_OUT" || echo "WARN stop marker did not write"

echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ) chain_rc=$CHAIN_RC declared=$DECLARED_ARMS executed=$EXECUTED" >> "$STATUS"
echo "D19O_DRIVER end=$(date -u +%Y%m%dT%H%M%SZ) chain_rc=$CHAIN_RC executed=$EXECUTED/$DECLARED_ARMS"
echo "THIS ITEM CANNOT PUBLISH PASS.  Its verdict is CEILINGED at GATE REACHED,"
echo "because it spends a compressible gradient with NO GRADED VERDICT whose"
echo "plateau did not close (shape[7]/CD one-sided at 21.060684242435336 %)."
exit "$CHAIN_RC"
