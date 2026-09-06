#!/usr/bin/env bash
# =============================================================================
# VMFL046-R5 graded-run driver.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.155 (VMFL046).
#
# Solver: rhoPimpleFoam (OpenFOAM v2606), TRANSIENT compressible, laminar, 2-D half-nozzle.
#
# R5 IS A ONE-LINE CONFIGURATION CHANGE AND NOTHING ELSE.  Exactly ONE of the eleven case/
# inputs moves -- 0/p, the OUTLET boundary condition, from a fully-reflecting `fixedValue`
# to a partially non-reflecting `waveTransmissive` (lInf 2.0 m, the full nozzle length; see
# PREREGISTRATION §2/§3).  The gate, the plateau threshold, DELTA_X, endTime, maxCo, the mesh,
# the r=2 triple, the sampler and the comparator are all carried forward from R4 byte-identical.
#
# THE SINGLE-VARIABLE CLAIM IS THE REGISTRATION'S WHOLE EVIDENTIARY BASIS, so this driver
# carries a BOTH-DIRECTIONS parity assert against R4 and REFUSES to launch (exit 7) if it is
# violated in EITHER direction:
#   DIRECTION 1  every case input EXCEPT 0/p must be byte-identical to R4's;
#   DIRECTION 2  0/p must DIFFER from R4's AND must carry the registered waveTransmissive
#                outlet with lInf 2.0 -- a bare "differs" is not enough, a random edit also
#                differs; the change on disk must be THE registered change.
# A successor that changed 0/p in some other way, or that touched any other input, or that made
# no change at all, is therefore UNFREEZABLE -- exactly the property R4's own R3-parity assert
# had, re-aimed at R5's axis (the boundary model) instead of R4's axis (the cost envelope).
#
# Frozen pre-registration: cases/ansys_verification/VMFL046-R5/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL046-R5/grade_vmfl046_r5.py
#                          (blob 476de16a..., byte-identical to R4's §2aw-repaired grader)
# Frozen reference       : cases/ansys_verification/VMFL046/quasi1d_reference.py (R1, unchanged)
# Run root (cwd)         : verification/runs/ansys_verification/VMFL046-R5/ (never the case dir)
#
# THE DRIVER SOURCES ITS OWN OpenFOAM ENVIRONMENT AND ONLY THEN ASSERTS ITS TOOLS ON PATH
# (charter §14/§15).  VMFL072-R2's frozen driver checked `command -v` WITHOUT sourcing, and
# every one of its five queue rows refused at rc=2 under the daemon's bare PATH (G-00 MISSING
# EXECUTABLE).  A smoke in a shell the launch never gets has proved nothing about the launch.
#
# NO `set -u`.  THE CAP IS ENFORCED TWICE (rule 12, charter §26.2): a PER-LEVEL cap and a
# RUNNING TOTAL.  An overrun STOPS the run (rc 124); it does not get a new budget.
# =============================================================================

RANKS=1

# --- COST (PREREGISTRATION §7).  THE BASIS IS NOT A PROBE and NOT AN R5 MEASUREMENT.  It is
# R4's OWN THREE GRADED-RUN ACTUALS at this mesh, these numerics, this clock, read from the
# final ClockTime line of each level's log and recorded in the R4 cost-calibration row
# (docs/COST_CALIBRATION.md id C-20260906T170500..., register row #61):
#
#   L1   8.07 core-min   MEASURED   (484 wall s   x 1 rank / 60)
#   L2  54.67 core-min   MEASURED   (3,280 wall s x 1 rank / 60)
#   L3 426.27 core-min   MEASURED   (25,576 wall s x 1 rank / 60)
#   ------------------------------------------------------------------------------------
#   POINT ESTIMATE 489.0 core-min.
#
# waveTransmissive changes a BOUNDARY EVALUATION on one outlet patch only -- it evaluates psi,
# a wave speed and a relaxation term on the exit faces each step -- NOT the per-cell-step rate
# of the 3,200 / 12,800 / 51,200-cell interior.  If it settles the flow (branch a) it can only
# REDUCE the number of steps; if it does not (branch b) the run still stops at the same
# geometric endTime.  So R4's measured cost is a CONSERVATIVE point estimate for R5.
#
# THE +10% CONTENTION ALLOWANCE GOES IN THE CAP, NOT THE POINT ESTIMATE.  This is the R4
# calibration lesson landed verbatim (COST_CALIBRATION id C-20260906T170500...): folded into
# the point estimate, the allowance biases every ratio to ~=0.91x on a quiet box and hides the
# accuracy of the underlying model.  The point estimate is the bare measured basis; the caps
# below carry the allowance and the ~3x charter headroom.
#
# CAPS AT ~3x THE PER-LEVEL BASIS (charter §26.2), mirroring R4's frozen caps 27/183/1400.
# An overrun STOPS the run (rc 124, rule 12); it does not get a new budget.
CAP_CORE_MIN=1610                # RUNNING TOTAL across all three solves (>= 3x 489.0)
declare -A CAP_LEVEL=( [L1]=27 [L2]=183 [L3]=1400 )  # >= 3x basis 8.07 / 54.67 / 426.27

# endTime is PHYSICAL SECONDS and is R4's (== R3's), UNCHANGED: 0.080 s.  VMFL046R5_ENDTIME
# overrides ONLY for a CLAUSE-B smoke; the graded default is unchanged and the frozen
# comparator REFUSES any level whose controlDict does not carry it.
ENDTIME="${VMFL046R5_ENDTIME:-0.080}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
R4_CASE_DIR="$REPO_ROOT/cases/ansys_verification/VMFL046-R4/case"
RUN_ROOT="${1:?usage: run_vmfl046_r5.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"
SMOKE="${VMFL046R5_SMOKE:-0}"

# The single registered change lives in this ONE file; the parity assert below is aimed at it.
THE_ONE_CHANGE="0/p"

# The GRADED centreline sampling interval is 5.0e-04 s and the frozen comparator refuses any
# other value (grade_vmfl046_r5.py SAMPLE_DT).  Overridable ONLY under a CLAUSE-B smoke.
SAMPLEDT=5.0e-04
if [ "$SMOKE" = "1" ] && [ -n "$VMFL046R5_SAMPLEDT" ]; then SAMPLEDT="$VMFL046R5_SAMPLEDT"; fi

# r=2 grid triple, IDENTICAL to R1-R4: converging / diverging axial counts and the transverse
# count all double.  NPOINTS = 2*(NXA+NXB)+1 -- the sampler refines with the mesh.
declare -A NXA=( [L1]=40  [L2]=80  [L3]=160 )
declare -A NXB=( [L1]=120 [L2]=240 [L3]=480 )
declare -A NY=(  [L1]=20  [L2]=40  [L3]=80  )
declare -A NPOINTS=( [L1]=321 [L2]=641 [L3]=1281 )

echo "=== VMFL046-R5 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  endTime=$ENDTIME s  sampleDt=$SAMPLEDT s  smoke=$SMOKE"

# ---- 0. EVERY PATH THIS DRIVER REFERENCES, CHECKED TO EXIST BEFORE ANYTHING RUNS.
#         charter §39.5's driver-side face, and it is NOT the freeze checker's job:
#         check_freeze_ready.py's C2 defers every runtime-composed path as UNDETERMINED.
#         (`bash -n` checks syntax and never checks path existence.)
for p in "$CASE_DIR" "$CASE_DIR/0" "$CASE_DIR/constant" "$CASE_DIR/system" \
         "$CASE_DIR/system/blockMeshDict.template" "$CASE_DIR/system/controlDict.template" \
         "$CASE_DIR/system/fvSchemes" "$CASE_DIR/system/fvSolution" \
         "$CASE_DIR/0/T" "$CASE_DIR/0/U" "$CASE_DIR/0/p" \
         "$CASE_DIR/constant/fvOptions" "$CASE_DIR/constant/momentumTransport" \
         "$CASE_DIR/constant/thermophysicalProperties" "$CASE_DIR/constant/turbulenceProperties" \
         "$R4_CASE_DIR" ; do
  [ -e "$p" ] || { echo "ABORT: driver references a path that does not exist: $p"; exit 2; }
done

# ---- 1. OpenFOAM environment, SOURCED BY THE DRIVER ITSELF, THEN asserted (charter §14/§15).
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
command -v blockMesh     >/dev/null || { echo "ABORT: blockMesh not on PATH after sourcing the v2606 bashrc"; exit 2; }
command -v rhoPimpleFoam >/dev/null || { echo "ABORT: rhoPimpleFoam not on PATH after sourcing the v2606 bashrc"; exit 2; }

# ---- 2. R4-PARITY ASSERT -- R5's OWN BOTH-DIRECTIONS ASSERT, AIMED AT THE SINGLE 0/p DELTA.
#   DIRECTION 1: every case input EXCEPT 0/p must be byte-identical to R4's.  R5 is a single
#     boundary-condition change; if it touched any other input, its verdict would not isolate
#     the outlet reflectivity and §2/§5's single-variable premise would be false.
#   DIRECTION 2: 0/p must DIFFER from R4's AND carry the registered waveTransmissive outlet
#     with lInf 2.0.  A no-op successor (0/p still fixedValue) is killed here; so is one whose
#     0/p differs in some UNregistered way.  That makes both a no-op and an off-spec edit
#     UNFREEZABLE.
N_SAME=0
FOUND_CHANGE=0
while IFS= read -r f; do
  rel="${f#$CASE_DIR/}"
  [ -f "$R4_CASE_DIR/$rel" ] || { echo "ABORT: R4 parity reference missing: $R4_CASE_DIR/$rel"; exit 7; }
  if [ "$rel" = "$THE_ONE_CHANGE" ]; then
    FOUND_CHANGE=1
    cmp -s "$f" "$R4_CASE_DIR/$rel" && { echo "ABORT: R5 case input $rel is IDENTICAL to R4 -- the ONE registered change (fixedValue -> waveTransmissive outlet) was never made; the single-variable premise of PREREGISTRATION §2/§5 is false"; exit 7; }
    grep -q "waveTransmissive" "$f" || { echo "ABORT: R5 $rel does not carry a waveTransmissive outlet -- the change on disk is not the registered change (PREREGISTRATION §2)"; exit 7; }
    grep -Eq "lInf[[:space:]]+2\.0([^0-9]|$)" "$f" || { echo "ABORT: R5 $rel does not carry the registered relaxation length lInf 2.0 (PREREGISTRATION §3)"; exit 7; }
  else
    cmp -s "$f" "$R4_CASE_DIR/$rel" || { echo "ABORT: R5 case input $rel DIFFERS from R4 -- R5 is a SINGLE outlet-BC change on 0/p and is NOT permitted to touch any other input; the single-variable claim in PREREGISTRATION §2/§8 is false"; exit 7; }
    N_SAME=$((N_SAME+1))
  fi
done < <(find "$CASE_DIR" -type f | sort)
[ "$FOUND_CHANGE" = "1" ] || { echo "ABORT: the registered changed file $THE_ONE_CHANGE was not found in R5's case tree"; exit 7; }
N_R4=$(find "$R4_CASE_DIR" -type f | wc -l)
# R5 must carry EXACTLY R4's file set (no file added or removed): the byte-identical count
# plus the single changed 0/p must equal R4's total.
[ "$((N_SAME+1))" = "$N_R4" ] || { echo "ABORT: R5 carries $((N_SAME+1)) case inputs against R4's $N_R4 -- a file was added or removed, so this is not a single-variable delta"; exit 7; }
echo "R4-parity OK: $N_SAME inputs byte-identical to R4, exactly one changed ($THE_ONE_CHANGE = fixedValue -> waveTransmissive, lInf 2.0), file set identical ($N_R4 files)"

if [ "$SMOKE" = "1" ]; then
  case "$RUN_ROOT" in
    /tmp/*|*/scratchpad/*) : ;;
    *) echo "ABORT smoke: run_root $RUN_ROOT is not under a scratch area"; exit 3 ;;
  esac
fi

# ---- 3. rule-4 age guard, BEFORE anything is written.
for L in $LEVELS_TO_RUN; do
  if [ -d "$RUN_ROOT/$L" ] && ls -d "$RUN_ROOT/$L"/[0-9]* >/dev/null 2>&1; then
    echo "ABORT: $RUN_ROOT/$L already holds a numeric time dir (rule 4 age guard)"; exit 4
  fi
done

# ---- 4. input integrity: every case input matches its committed blob (rule 2).
if [ "$SMOKE" != "1" ]; then
  H=$(git -C "$SCRIPT_DIR" rev-parse HEAD) || { echo "ABORT: no HEAD"; exit 5; }
  while IFS= read -r f; do
    rel="cases/ansys_verification/VMFL046-R5/case/${f#$CASE_DIR/}"
    disk=$(git -C "$SCRIPT_DIR" hash-object "$f")
    blob=$(git -C "$SCRIPT_DIR" rev-parse "HEAD:$rel" 2>/dev/null)
    if [ "$disk" != "$blob" ]; then
      echo "ABORT: case input $rel does not match its HEAD blob (disk=$disk blob=${blob:-MISSING})"; exit 6
    fi
  done < <(find "$CASE_DIR" -type f | sort)
  echo "input-integrity OK: all case inputs match HEAD $H (caveat: pins to HEAD not prereg_commit; rule 6 is the backstop)"
fi

CORE_MIN_USED=0
for L in $LEVELS_TO_RUN; do
  LD="$RUN_ROOT/$L"
  mkdir -p "$LD"
  cp -r "$CASE_DIR"/* "$LD"/
  rm -f "$LD/system/blockMeshDict.template" "$LD/system/controlDict.template"
  sed "s/__NXA__/${NXA[$L]}/g; s/__NXB__/${NXB[$L]}/g; s/__NY__/${NY[$L]}/g" "$CASE_DIR/system/blockMeshDict.template" > "$LD/system/blockMeshDict"
  sed "s/__ENDTIME__/$ENDTIME/g; s/__NPOINTS__/${NPOINTS[$L]}/g; s/__SAMPLEDT__/$SAMPLEDT/g" "$CASE_DIR/system/controlDict.template" > "$LD/system/controlDict"
  grep -q "__ENDTIME__\|__NPOINTS__\|__SAMPLEDT__\|__NXA__\|__NXB__\|__NY__" "$LD/system/controlDict" "$LD/system/blockMeshDict" \
    && { echo "ABORT $L: an unsubstituted template token survived into a live dictionary"; exit 8; }
  touch "$LD/0/U" "$LD/0/p" "$LD/0/T"   # 0/ dated LAST (rule 4 age-guard reference)

  ( cd "$LD" && blockMesh ) > "$LD/log.blockMesh" 2>&1 || { echo "ABORT $L: blockMesh rc=$?"; exit 10; }

  remaining=$(awk "BEGIN{print ($CAP_CORE_MIN-$CORE_MIN_USED)}")
  lvlcap="${CAP_LEVEL[$L]}"
  budget=$(awk "BEGIN{print ($remaining < $lvlcap) ? $remaining : $lvlcap}")
  timeout_s=$(awk "BEGIN{printf \"%d\", $budget*60/$RANKS}")
  if [ "$timeout_s" -le 0 ]; then echo "ABORT $L: cap exhausted before launch (rule 12)"; exit 124; fi
  echo "  $L: budget=${budget} core-min (level cap $lvlcap, remaining total $remaining) -> timeout ${timeout_s}s"

  # rc is captured DIRECTLY from the timeout subshell, on the line immediately after it -- the
  # subshell's exit status IS timeout's (124 on kill, else the solver's rc).  There is NO
  # setsid here; if one were ever introduced, the rc MUST be captured INSIDE the setsid wrapper
  # (setsid-parent-returns-zero: `setsid timeout cmd` exits 0 for every outcome).
  t0=$(date +%s)
  ( cd "$LD" && timeout "${timeout_s}s" rhoPimpleFoam ) > "$LD/log.rhoPimpleFoam" 2>&1
  rc=$?
  echo "$rc" > "$LD/RUN_RC"
  t1=$(date +%s); wall=$((t1-t0))
  used=$(awk "BEGIN{print $wall*$RANKS/60}")
  CORE_MIN_USED=$(awk "BEGIN{print $CORE_MIN_USED+$used}")
  echo "  $L: rc=$rc wall=${wall}s core_min_used=$CORE_MIN_USED / cap $CAP_CORE_MIN"
  if [ "$rc" = "124" ]; then echo "ABORT $L: cap overrun stopped the run (rc 124, rule 12)"; exit 124; fi
  if [ "$rc" != "0" ]; then echo "ABORT $L: rhoPimpleFoam rc=$rc"; exit 11; fi
done

echo "=== VMFL046-R5 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
