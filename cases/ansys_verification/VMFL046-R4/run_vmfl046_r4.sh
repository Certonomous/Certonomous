#!/usr/bin/env bash
# =============================================================================
# VMFL046-R4 graded-run driver.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.155 (VMFL046).
#
# Solver: rhoPimpleFoam (OpenFOAM v2606), TRANSIENT compressible, laminar, 2-D half-nozzle.
#
# R4 IS A COST FIX AND A READER-WINDOW FIX.  THE PHYSICS AND THE NUMERICS ARE R3's, BYTE
# FOR BYTE.  All ELEVEN case/ inputs are byte-identical to R3's and this driver ABORTS if
# any one of them differs (exit 7).  What R4 changes is the COST ENVELOPE -- the estimate,
# the filing and the caps -- and this driver ABORTS if THAT is unchanged (exit 7 as well).
# The parity assert therefore fires in BOTH DIRECTIONS on R4's OWN delta, exactly as R3's
# fired on R3's: A SUCCESSOR THAT CHANGED NOTHING IS UNFREEZABLE.
#
# The R2-parity assert is ALSO carried forward verbatim and also fires in both directions
# (8 physics inputs byte-identical to R2, 3 numerics inputs necessarily different), so the
# R3 experimental design remains mechanically proved in R4's bytes and not merely cited.
#
# WHY R4 EXISTS -- charter §26.2 / §27, verbatim in its own words:
#   "AN UNDER-FILED ESTIMATE DOES NOT OVERSPEND.  IT STRANGLES ITS OWN RUN, AND IT COSTS
#    IT AT THE END, AFTER ALL THE COMPUTE HAS BEEN SPENT."
# R3's numerics change WORKED at L1 (rc 0, one End, last Time = 0.08 exactly).  L2 and L3
# died rc 124 on their own caps -- L3 at 99.21 % of endTime after seven hours -- because
# their estimates came from probes covering 10 % of the graded clock, and a rate taken from
# the first 10 % of an adaptive-timestep transient prices a workload that does not exist.
#
# Frozen pre-registration: cases/ansys_verification/VMFL046-R4/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL046-R4/grade_vmfl046_r4.py
# Frozen reference       : cases/ansys_verification/VMFL046/quasi1d_reference.py (R1, unchanged)
# Run root (cwd)         : verification/runs/ansys_verification/VMFL046-R4/ (never the case dir)
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

# --- COST (PREREGISTRATION §8).  THE BASIS IS NOT A PROBE.  It is R3's own three graded
# runs, at the graded mesh, the graded numerics and the graded clock, read from their logs:
#
#   L1  8.0452 core-min  MEASURED COMPLETE          rc 0, one End, last Time 0.08 = endTime
#   L2 55.3292 core-min  49.8660 measured to 91.485 % of endTime + 5.4632 at the settled
#                        last-decile rate 0.80197 core-min/ms over the remaining 6.8122 ms
#   L3 423.6292 core-min 419.8393 measured to 99.214 % of endTime + 3.7898 at the settled
#                        last-decile rate 6.03031 core-min/ms over the remaining 0.6285 ms
#   ------------------------------------------------------------------------------------
#   BASIS 487.00 core-min.  FILED 536 (a disclosed +10 % contention allowance).
#
# Per-step cost FALLS through the run at every level (s/step, first decile -> last:
# 0.01472 -> 0.01405 at L1, 0.04783 -> 0.04480 at L2, 0.18529 -> 0.17222 at L3), so the
# extrapolations above are not optimistic; the linear and settled-rate extrapolations agree
# to 0.11 % at L3.  Waste is MEASURED, not inferred: ExecutionTime/ClockTime = 0.99940 /
# 0.99732 / 0.99962, i.e. 0.06 % / 0.27 % / 0.04 %.
#
# CAPS AT ~3x THE FILED FIGURE (charter §26.2, Sanaa 2026-09-03 clause 2).  THE ESTIMATE
# WAS MADE GOOD AND THE CAP WAS THEN SET ON IT -- the cap was NOT loosened around a bad
# number, which §27 forbids in terms.
CAP_CORE_MIN=1610                # RUNNING TOTAL across all three solves (>= 3x 536 = 1608)
declare -A CAP_LEVEL=( [L1]=27 [L2]=183 [L3]=1400 )  # >= 3x filed 8.85 / 60.86 / 465.99
# R3's caps, recorded so the R4-delta assert below can prove the envelope actually changed:
declare -A CAP_LEVEL_R3=( [L1]=30 [L2]=50 [L3]=420 )
CAP_CORE_MIN_R3=540

# endTime is PHYSICAL SECONDS and is R3's, UNCHANGED.  0.080 s ~ 20 upstream acoustic
# traverses of the 0.85 m subsonic section at c-u ~ 220 m/s -- derived a priori in R3
# §5.4 from geometry and the reference state, NOT read off any observed settling time, and
# NOT re-derived here.  §26.3 forbids re-pricing a workload without re-deriving the
# estimate; R4 does the converse and re-derives the estimate without touching the workload.
# VMFL046R4_ENDTIME overrides ONLY for a CLAUSE-B smoke; the graded default is unchanged and
# the frozen comparator REFUSES any level whose controlDict does not carry it.
ENDTIME="${VMFL046R4_ENDTIME:-0.080}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
R2_CASE_DIR="$REPO_ROOT/cases/ansys_verification/VMFL046-R2/case"
R3_CASE_DIR="$REPO_ROOT/cases/ansys_verification/VMFL046-R3/case"
R3_DRIVER="$REPO_ROOT/cases/ansys_verification/VMFL046-R3/run_vmfl046_r3.sh"
RUN_ROOT="${1:?usage: run_vmfl046_r4.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"
SMOKE="${VMFL046R4_SMOKE:-0}"

# The GRADED centreline sampling interval is 5.0e-04 s and the frozen comparator refuses any
# other value (grade_vmfl046_r4.py SAMPLE_DT).  Overridable ONLY under a CLAUSE-B smoke, so
# that a handful of steps can prove the refined sampler really writes nPoints rows (§39.5).
SAMPLEDT=5.0e-04
if [ "$SMOKE" = "1" ] && [ -n "$VMFL046R4_SAMPLEDT" ]; then SAMPLEDT="$VMFL046R4_SAMPLEDT"; fi

# r=2 grid triple, IDENTICAL to R1, R2 and R3: converging / diverging axial counts and the
# transverse count all double.  NPOINTS = 2*(NXA+NXB)+1 -- the sampler refines with the mesh.
declare -A NXA=( [L1]=40  [L2]=80  [L3]=160 )
declare -A NXB=( [L1]=120 [L2]=240 [L3]=480 )
declare -A NY=(  [L1]=20  [L2]=40  [L3]=80  )
declare -A NPOINTS=( [L1]=321 [L2]=641 [L3]=1281 )

echo "=== VMFL046-R4 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  endTime=$ENDTIME s  sampleDt=$SAMPLEDT s  smoke=$SMOKE"

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
         "$R2_CASE_DIR" "$R3_CASE_DIR" "$R3_DRIVER" ; do
  [ -e "$p" ] || { echo "ABORT: driver references a path that does not exist: $p"; exit 2; }
done

# ---- 1. OpenFOAM environment, SOURCED BY THE DRIVER ITSELF, THEN asserted (charter §14/§15).
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
command -v blockMesh     >/dev/null || { echo "ABORT: blockMesh not on PATH after sourcing the v2606 bashrc"; exit 2; }
command -v rhoPimpleFoam >/dev/null || { echo "ABORT: rhoPimpleFoam not on PATH after sourcing the v2606 bashrc"; exit 2; }

# ---- 2a. R2-PARITY ASSERT, CARRIED FORWARD FROM R3 VERBATIM.  The physics is UNCHANGED
#          and the numerics change is EXACTLY the three declared files.  It fails loudly if
#          anyone edits a BC, the mesh, the thermophysics or fvOptions, AND if the numerics
#          change branch (b) pre-committed was quietly reverted.
PARITY_SAME="0/T 0/U 0/p constant/fvOptions constant/momentumTransport constant/thermophysicalProperties constant/turbulenceProperties system/blockMeshDict.template"
PARITY_DIFF="system/fvSchemes system/fvSolution system/controlDict.template"
for rel in $PARITY_SAME; do
  [ -f "$R2_CASE_DIR/$rel" ] || { echo "ABORT: R2 parity reference missing: $R2_CASE_DIR/$rel"; exit 7; }
  cmp -s "$CASE_DIR/$rel" "$R2_CASE_DIR/$rel" || { echo "ABORT: R4 case input $rel DIFFERS from R2 -- the physics-unchanged claim in PREREGISTRATION §4 is false"; exit 7; }
done
for rel in $PARITY_DIFF; do
  [ -f "$R2_CASE_DIR/$rel" ] || { echo "ABORT: R2 parity reference missing: $R2_CASE_DIR/$rel"; exit 7; }
  cmp -s "$CASE_DIR/$rel" "$R2_CASE_DIR/$rel" && { echo "ABORT: R4 case input $rel is IDENTICAL to R2 -- the NUMERICS CHANGE that branch (b) pre-committed was never made"; exit 7; }
done
echo "R2-parity OK: 8 physics inputs byte-identical, 3 numerics inputs changed (exactly as declared in §4)"

# ---- 2b. R3-PARITY ASSERT -- R4's OWN BOTH-DIRECTIONS ASSERT, AND ITS AXIS IS THE COST
#          ENVELOPE, BECAUSE THAT IS WHAT R4 CHANGES.
#          DIRECTION 1: EVERY case input must be byte-identical to R3's.  R4 is not allowed
#            to touch the physics or the numerics; if it did, its verdict would not be a
#            re-run of R3's configuration and the whole premise ("the physics is already
#            right, the cost estimate killed it") would be false.
#          DIRECTION 2: the COST ENVELOPE must actually differ from R3's.  A successor that
#            re-files R3's caps has changed nothing and would simply be killed again at the
#            same place.  THAT MAKES A NO-OP SUCCESSOR UNFREEZABLE, which is the property
#            R3's own assert had and which a lane could easily have lost by copying the
#            file and editing two numbers.
N_SAME=0
while IFS= read -r f; do
  rel="${f#$CASE_DIR/}"
  [ -f "$R3_CASE_DIR/$rel" ] || { echo "ABORT: R3 parity reference missing: $R3_CASE_DIR/$rel"; exit 7; }
  cmp -s "$f" "$R3_CASE_DIR/$rel" || { echo "ABORT: R4 case input $rel DIFFERS from R3 -- R4 is a COST fix and a READER fix, and is NOT permitted to change the physics or the numerics"; exit 7; }
  N_SAME=$((N_SAME+1))
done < <(find "$CASE_DIR" -type f | sort)
N_R3=$(find "$R3_CASE_DIR" -type f | wc -l)
[ "$N_SAME" = "$N_R3" ] || { echo "ABORT: R4 carries $N_SAME case inputs against R3's $N_R3 -- a file was added or removed"; exit 7; }

CHANGED=0
for L in L1 L2 L3; do
  [ "${CAP_LEVEL[$L]}" != "${CAP_LEVEL_R3[$L]}" ] && CHANGED=$((CHANGED+1))
done
[ "$CAP_CORE_MIN" != "$CAP_CORE_MIN_R3" ] && CHANGED=$((CHANGED+1))
[ "$CHANGED" -ge 1 ] || { echo "ABORT: R4's cost envelope is IDENTICAL to R3's (running cap $CAP_CORE_MIN, levels ${CAP_LEVEL[L1]}/${CAP_LEVEL[L2]}/${CAP_LEVEL[L3]}) -- R4 changed NOTHING and would be killed at exactly the same place"; exit 7; }

# And the recorded R3 caps must be R3's REAL caps, read from R3's own frozen driver -- a
# hardcoded pair of numbers that nobody checks is a comparison against a memory, not a file.
for L in L1 L2 L3; do
  got=$(grep -o "\[$L\]=[0-9]*" "$R3_DRIVER" | head -1 | cut -d= -f2)
  [ "$got" = "${CAP_LEVEL_R3[$L]}" ] || { echo "ABORT: CAP_LEVEL_R3[$L]=${CAP_LEVEL_R3[$L]} does not match R3's frozen driver, which says $got -- the both-directions assert is comparing against a number this file invented"; exit 7; }
done
got=$(grep -oE '^CAP_CORE_MIN=[0-9]+' "$R3_DRIVER" | head -1 | cut -d= -f2)
[ "$got" = "$CAP_CORE_MIN_R3" ] || { echo "ABORT: CAP_CORE_MIN_R3=$CAP_CORE_MIN_R3 does not match R3's frozen driver, which says $got"; exit 7; }
echo "R3-parity OK: all $N_SAME case inputs byte-identical to R3, and the cost envelope CHANGED in $CHANGED of 4 registered figures (running cap $CAP_CORE_MIN_R3 -> $CAP_CORE_MIN, levels ${CAP_LEVEL_R3[L1]}/${CAP_LEVEL_R3[L2]}/${CAP_LEVEL_R3[L3]} -> ${CAP_LEVEL[L1]}/${CAP_LEVEL[L2]}/${CAP_LEVEL[L3]}), verified against R3's own frozen driver"

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
    rel="cases/ansys_verification/VMFL046-R4/case/${f#$CASE_DIR/}"
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

echo "=== VMFL046-R4 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
