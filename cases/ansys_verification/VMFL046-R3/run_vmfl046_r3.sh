#!/usr/bin/env bash
# =============================================================================
# VMFL046-R3 graded-run driver.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.155 (VMFL046).
#
# Solver: rhoPimpleFoam (OpenFOAM v2606), TRANSIENT compressible, laminar, 2-D half-nozzle.
# R3 is the successor VMFL046-R2's frozen branch (b) pre-committed BEFORE any R2 compute:
# it CHANGES THE NUMERICS and never the gate, the band or the plateau threshold.
#
# EXACTLY THREE case inputs differ from R2, and the R2-PARITY ASSERT below PROVES the other
# eight are byte-identical.  The three are system/fvSchemes (steadyState -> Euler; the five
# convective schemes upwind -> vanLeer TVD; div(phiv,p) added), system/fvSolution (SIMPLE ->
# PIMPLE) and system/controlDict.template (iterations -> physical seconds).
#
# Frozen pre-registration: cases/ansys_verification/VMFL046-R3/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL046-R3/grade_vmfl046_r3.py
# Frozen reference       : cases/ansys_verification/VMFL046/quasi1d_reference.py (R1, unchanged)
# Run root (cwd)         : verification/runs/ansys_verification/VMFL046-R3/ (never the case dir)
#
# THE DRIVER SOURCES ITS OWN OpenFOAM ENVIRONMENT AND ONLY THEN ASSERTS ITS TOOLS ON PATH
# (charter §14/§15).  VMFL072-R2's frozen driver checked `command -v` WITHOUT sourcing, and
# every one of its five queue rows refused at rc=2 under the daemon's bare PATH.  A smoke in
# a shell the launch never gets has proved nothing about the launch.
#
# NO `set -u`.  THE CAP IS ENFORCED TWICE (rule 12, charter §26.2): a PER-LEVEL cap and a
# RUNNING TOTAL.  An overrun STOPS the run (rc 124); it does not get a new budget.
# =============================================================================

RANKS=1

# --- COST (PREREGISTRATION §8).  Basis: the MEASURED equilibrium time step and MEASURED
# per-cell-step rate of THIS EXACT CONFIGURATION at ALL THREE LEVELS, from the §5.3
# stability probe (L1 5476 steps/20 ms/78.5 s; L2 1560 steps/8 ms/76.1 s; L3 3404 steps/
# 8 ms/661.6 s -- all three probes ran to their own endTime).  Estimate 162.08 core-min
# (L1 9.52 / L2 15.59 / L3 136.97); filed 180 with an 11 % allowance; caps >= 3x each.
CAP_CORE_MIN=540                 # RUNNING TOTAL across all three solves (>= 3x 162.08)
declare -A CAP_LEVEL=( [L1]=30 [L2]=50 [L3]=420 )   # >= 3x 9.52 / 15.59 / 136.97

# endTime is PHYSICAL SECONDS.  0.080 s ~ 20 upstream acoustic traverses of the 0.85 m
# subsonic section at c-u ~ 220 m/s (3.9 ms each) -- derived a priori in PREREGISTRATION
# §5.4 from geometry and the reference state, NOT read off any observed settling time.
# VMFL046R3_ENDTIME overrides ONLY for a CLAUSE-B smoke; the graded default is unchanged and
# the frozen comparator REFUSES any level whose controlDict does not carry it.
ENDTIME="${VMFL046R3_ENDTIME:-0.080}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
R2_CASE_DIR="$REPO_ROOT/cases/ansys_verification/VMFL046-R2/case"
RUN_ROOT="${1:?usage: run_vmfl046_r3.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"
SMOKE="${VMFL046R3_SMOKE:-0}"

# The GRADED centreline sampling interval is 5.0e-04 s and the frozen comparator refuses any
# other value (grade_vmfl046_r3.py SAMPLE_DT).  Overridable ONLY under a CLAUSE-B smoke, so
# that a handful of steps can prove the refined sampler really writes nPoints rows (§39.5).
SAMPLEDT=5.0e-04
if [ "$SMOKE" = "1" ] && [ -n "$VMFL046R3_SAMPLEDT" ]; then SAMPLEDT="$VMFL046R3_SAMPLEDT"; fi

# r=2 grid triple, IDENTICAL to R1 and R2: converging / diverging axial counts and the
# transverse count all double.  NPOINTS = 2*(NXA+NXB)+1 -- the sampler refines with the mesh.
declare -A NXA=( [L1]=40  [L2]=80  [L3]=160 )
declare -A NXB=( [L1]=120 [L2]=240 [L3]=480 )
declare -A NY=(  [L1]=20  [L2]=40  [L3]=80  )
declare -A NPOINTS=( [L1]=321 [L2]=641 [L3]=1281 )

echo "=== VMFL046-R3 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  endTime=$ENDTIME s  sampleDt=$SAMPLEDT s  smoke=$SMOKE"

# ---- 0. EVERY PATH THIS DRIVER REFERENCES, CHECKED TO EXIST BEFORE ANYTHING RUNS.
#         charter §39.5's driver-side face, and it is NOT the freeze checker's job:
#         check_freeze_ready.py's C2 defers every runtime-composed path as UNDETERMINED,
#         so the checker passing is NOT §39.5 compliance.  This loop is.
#         (`bash -n` checks syntax and never checks path existence.)
for p in "$CASE_DIR" "$CASE_DIR/0" "$CASE_DIR/constant" "$CASE_DIR/system" \
         "$CASE_DIR/system/blockMeshDict.template" "$CASE_DIR/system/controlDict.template" \
         "$CASE_DIR/system/fvSchemes" "$CASE_DIR/system/fvSolution" \
         "$CASE_DIR/0/T" "$CASE_DIR/0/U" "$CASE_DIR/0/p" \
         "$CASE_DIR/constant/fvOptions" "$CASE_DIR/constant/momentumTransport" \
         "$CASE_DIR/constant/thermophysicalProperties" "$CASE_DIR/constant/turbulenceProperties" \
         "$R2_CASE_DIR" ; do
  [ -e "$p" ] || { echo "ABORT: driver references a path that does not exist: $p"; exit 2; }
done

# ---- 1. OpenFOAM environment, SOURCED BY THE DRIVER ITSELF, THEN asserted (charter §14/§15).
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
command -v blockMesh     >/dev/null || { echo "ABORT: blockMesh not on PATH after sourcing the v2606 bashrc"; exit 2; }
command -v rhoPimpleFoam >/dev/null || { echo "ABORT: rhoPimpleFoam not on PATH after sourcing the v2606 bashrc"; exit 2; }

# ---- 2. R2-PARITY ASSERT: the physics is UNCHANGED and the numerics change is EXACTLY the
#         three declared files.  This is the mechanical proof of the R3 experimental design,
#         and it fails loudly if anyone edits a BC, the mesh, the thermophysics or fvOptions.
PARITY_SAME="0/T 0/U 0/p constant/fvOptions constant/momentumTransport constant/thermophysicalProperties constant/turbulenceProperties system/blockMeshDict.template"
PARITY_DIFF="system/fvSchemes system/fvSolution system/controlDict.template"
for rel in $PARITY_SAME; do
  [ -f "$R2_CASE_DIR/$rel" ] || { echo "ABORT: R2 parity reference missing: $R2_CASE_DIR/$rel"; exit 7; }
  cmp -s "$CASE_DIR/$rel" "$R2_CASE_DIR/$rel" || { echo "ABORT: R3 case input $rel DIFFERS from R2 -- the physics-unchanged claim in PREREGISTRATION §6 is false"; exit 7; }
done
for rel in $PARITY_DIFF; do
  [ -f "$R2_CASE_DIR/$rel" ] || { echo "ABORT: R2 parity reference missing: $R2_CASE_DIR/$rel"; exit 7; }
  cmp -s "$CASE_DIR/$rel" "$R2_CASE_DIR/$rel" && { echo "ABORT: R3 case input $rel is IDENTICAL to R2 -- the NUMERICS CHANGE that branch (b) pre-committed was never made"; exit 7; }
done
echo "R2-parity OK: 8 physics inputs byte-identical, 3 numerics inputs changed (exactly as declared in §6)"

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
    rel="cases/ansys_verification/VMFL046-R3/case/${f#$CASE_DIR/}"
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

echo "=== VMFL046-R3 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
