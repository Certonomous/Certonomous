#!/usr/bin/env bash
# =============================================================================
# VMFL046-R6 graded-run driver.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.155 (VMFL046).
#
# Solver: rhoCentralFoam (OpenFOAM v2606) -- DENSITY-BASED, TRANSIENT, KNP central-upwind
# shock capturing (Greenshields, Weller, Gasparini & Reese 2010, DOI 10.1002/fld.2069).
# 2-D half-nozzle, laminar.
#
# R6 IS TWO DELIBERATE CHANGES vs R5 AND NOTHING ELSE:
#   AXIS 1 (SOLVER)  rhoPimpleFoam -> rhoCentralFoam.  R4 hunted and R5 washed out under the
#                    pressure-based segregated solver; R6 moves to the density-based path.
#                    This forces the fvSchemes (fluxScheme Kurganov, reconstruct(rho/U/T)),
#                    fvSolution (diagonal + smoothSolver, no PIMPLE), controlDict
#                    (application, maxCo 0.5->0.2) and the REMOVAL of constant/fvOptions
#                    (rhoCentralFoam has no limitTemperature -- verified at source).
#   AXIS 2 (OUTLET)  0/p waveTransmissive lInf 2.0 -> 0.3 m -- the R5 back-pressure repair
#                    (register #62), a gate-blind geometric relaxation length (PREREG §3).
#
# THE MESH, endTime, the r=2 triple, the sampler, DELTA_X and the GATE are carried from R5
# BYTE-IDENTICAL.  The driver carries a BOTH-DIRECTIONS parity assert against R5 and REFUSES
# to launch (exit 7) if it is violated:
#   DIRECTION 1  the six carried inputs (0/T, 0/U, momentumTransport, thermophysicalProperties,
#                turbulenceProperties, blockMeshDict.template) must be byte-identical to R5's.
#   DIRECTION 2  the deliberate changes must be present AND be the registered ones:
#                  - 0/p differs from R5 AND carries waveTransmissive lInf 0.3 (NOT 2.0);
#                  - controlDict.template carries `application rhoCentralFoam` AND `maxCo 0.2`;
#                  - fvSchemes carries `fluxScheme Kurganov`;
#                  - fvSolution differs from R5 (rhoCentralFoam solver set);
#                  - constant/fvOptions is ABSENT (R5 carried it);
#                  - the case carries EXACTLY 10 files (R5's 11 minus fvOptions).
# A successor that reverted any of these, or touched a carried input, is UNFREEZABLE here.
#
# Frozen pre-registration: cases/ansys_verification/VMFL046-R6/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL046-R6/grade_vmfl046_r6.py
#                          (blob pinned in the pre-registration; selftest 70 ok, 0 FAILED)
# Frozen reference       : cases/ansys_verification/VMFL046/quasi1d_reference.py (R1, unchanged)
# Run root (cwd)         : verification/runs/ansys_verification/VMFL046-R6/ (never the case dir)
#
# THE DRIVER SOURCES ITS OWN OpenFOAM ENVIRONMENT AND ONLY THEN ASSERTS ITS TOOLS ON PATH
# (charter §14/§15; the VMFL072 G-00 lesson: a smoke in a shell the launch never gets has
# proved nothing about the launch).
#
# NO `set -u`.  THE CAP IS ENFORCED TWICE (rule 12, charter §26.2): a PER-LEVEL cap and a
# RUNNING TOTAL.  An overrun STOPS the run (rc 124); it does not get a new budget.
# =============================================================================

RANKS=1

# --- COST (PREREGISTRATION §7).  POINT ESTIMATE 538 core-min, from R4's measured per-level
# actuals (register #61: L1 8.07 / L2 54.67 / L3 426.27 = 489.0 core-min, a sustained shock
# transient at THIS mesh/endTime) times a solver-conversion factor f_solver = 1.10:
#   f_solver = m_steps * m_perstep
#     m_steps   = (maxCo_R4 / maxCo_R6) * ((U+c)/U)|_{M~2.2}
#               = (0.5/0.2) * (3.2c/2.2c) = 2.5 * 1.4545 = 3.64   (explicit ACOUSTIC Courant
#                 at 0.2 vs implicit CONVECTIVE Courant at 0.5)
#     m_perstep = 0.30   (rhoCentralFoam single explicit update + 2 light diffusion sweeps,
#                 vs rhoPimpleFoam's 3-outer x 2-inner PIMPLE implicit solves)
#   => f_solver = 3.64 * 0.30 = 1.09 ~= 1.10.
# Per level: L1 8.07*1.10=8.88 / L2 54.67*1.10=60.14 / L3 426.27*1.10=468.90 = 537.9 core-min.
# UNCERTAINTY: f_solver in [0.7, 1.5] (m_perstep in [0.2,0.4]); the ~3x cap absorbs the upside.
# If the outlet FAILS to anchor (a second wash-out, R5's fate) the run is far CHEAPER, not
# dearer -- so the estimate errs in the safe direction against §26.2's cap-kill trap.
#
# CAPS AT ~3x THE PER-LEVEL POINT ESTIMATE (charter §26.2).  An overrun STOPS the run (rc 124).
CAP_CORE_MIN=1614                # RUNNING TOTAL (>= 3 x 537.9)
declare -A CAP_LEVEL=( [L1]=27 [L2]=181 [L3]=1410 )  # >= 3x 8.88 / 60.14 / 468.90

# endTime is PHYSICAL SECONDS and is R5's (== R4's == R3's), UNCHANGED: 0.080 s.
# VMFL046R6_ENDTIME overrides ONLY for a CLAUSE-B smoke; the frozen comparator REFUSES any
# level whose controlDict does not carry the graded value.
ENDTIME="${VMFL046R6_ENDTIME:-0.080}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
R5_CASE_DIR="$REPO_ROOT/cases/ansys_verification/VMFL046-R5/case"
RUN_ROOT="${1:?usage: run_vmfl046_r6.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"
SMOKE="${VMFL046R6_SMOKE:-0}"

# The GRADED centreline sampling interval is 5.0e-04 s and the frozen comparator refuses any
# other value (grade_vmfl046_r6.py SAMPLE_DT).  Overridable ONLY under a CLAUSE-B smoke.
SAMPLEDT=5.0e-04
if [ "$SMOKE" = "1" ] && [ -n "$VMFL046R6_SAMPLEDT" ]; then SAMPLEDT="$VMFL046R6_SAMPLEDT"; fi

# The six inputs carried from R5 BYTE-IDENTICAL (mesh, IC/BC, thermo, transport).
CARRIED=( "0/T" "0/U" "constant/momentumTransport" "constant/thermophysicalProperties" \
          "constant/turbulenceProperties" "system/blockMeshDict.template" )

# r=2 grid triple, IDENTICAL to R1-R5.  NPOINTS = 2*(NXA+NXB)+1 -- the sampler refines with
# the mesh.
declare -A NXA=( [L1]=40  [L2]=80  [L3]=160 )
declare -A NXB=( [L1]=120 [L2]=240 [L3]=480 )
declare -A NY=(  [L1]=20  [L2]=40  [L3]=80  )
declare -A NPOINTS=( [L1]=321 [L2]=641 [L3]=1281 )

echo "=== VMFL046-R6 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  endTime=$ENDTIME s  sampleDt=$SAMPLEDT s  smoke=$SMOKE"

# ---- 0. EVERY PATH THIS DRIVER REFERENCES, CHECKED TO EXIST BEFORE ANYTHING RUNS.
for p in "$CASE_DIR" "$CASE_DIR/0" "$CASE_DIR/constant" "$CASE_DIR/system" \
         "$CASE_DIR/system/blockMeshDict.template" "$CASE_DIR/system/controlDict.template" \
         "$CASE_DIR/system/fvSchemes" "$CASE_DIR/system/fvSolution" \
         "$CASE_DIR/0/T" "$CASE_DIR/0/U" "$CASE_DIR/0/p" \
         "$CASE_DIR/constant/momentumTransport" \
         "$CASE_DIR/constant/thermophysicalProperties" "$CASE_DIR/constant/turbulenceProperties" \
         "$R5_CASE_DIR" ; do
  [ -e "$p" ] || { echo "ABORT: driver references a path that does not exist: $p"; exit 2; }
done

# ---- 1. OpenFOAM environment, SOURCED BY THE DRIVER ITSELF, THEN asserted (charter §14/§15).
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
command -v blockMesh      >/dev/null || { echo "ABORT: blockMesh not on PATH after sourcing the v2606 bashrc"; exit 2; }
command -v rhoCentralFoam >/dev/null || { echo "ABORT: rhoCentralFoam not on PATH after sourcing the v2606 bashrc"; exit 2; }

# ---- 2. R5-PARITY ASSERT -- BOTH DIRECTIONS.
# DIRECTION 1: the six carried inputs byte-identical to R5.
for rel in "${CARRIED[@]}"; do
  [ -f "$CASE_DIR/$rel" ]     || { echo "ABORT: R6 carried input missing: $rel"; exit 7; }
  [ -f "$R5_CASE_DIR/$rel" ]  || { echo "ABORT: R5 parity reference missing: $R5_CASE_DIR/$rel"; exit 7; }
  cmp -s "$CASE_DIR/$rel" "$R5_CASE_DIR/$rel" \
    || { echo "ABORT: R6 carried input $rel DIFFERS from R5 -- R6 is a solver+outlet change and must NOT touch the mesh/IC/thermo (PREREG §8)"; exit 7; }
done
# DIRECTION 2: the deliberate changes are present and are the REGISTERED ones.
cmp -s "$CASE_DIR/0/p" "$R5_CASE_DIR/0/p" && { echo "ABORT: 0/p IDENTICAL to R5 -- the registered outlet change (lInf 2.0 -> 0.3) was never made"; exit 7; }
# The lInf checks read the CONFIG, not the comments: strip `//` comments first (the header
# comment legitimately narrates "lInf 2.0 -> 0.3", which must not trip the negative assert).
P_NOCOMMENT="$(sed 's://.*::' "$CASE_DIR/0/p")"
echo "$P_NOCOMMENT" | grep -q "waveTransmissive" || { echo "ABORT: 0/p does not carry a waveTransmissive outlet (PREREG §3)"; exit 7; }
echo "$P_NOCOMMENT" | grep -Eq "lInf[[:space:]]+0\.3([^0-9]|$)" || { echo "ABORT: 0/p does not carry the registered relaxation length lInf 0.3 (PREREG §3)"; exit 7; }
echo "$P_NOCOMMENT" | grep -Eq "lInf[[:space:]]+2\.0([^0-9]|$)" && { echo "ABORT: 0/p still carries R5's lInf 2.0 in the CONFIG -- the wash-out defect was not repaired"; exit 7; }
grep -q "application[[:space:]]\+rhoCentralFoam" "$CASE_DIR/system/controlDict.template" || { echo "ABORT: controlDict.template does not carry application rhoCentralFoam (AXIS 1)"; exit 7; }
grep -Eq "maxCo[[:space:]]+0\.2([^0-9]|$)" "$CASE_DIR/system/controlDict.template" || { echo "ABORT: controlDict.template does not carry the registered maxCo 0.2 (PREREG §6)"; exit 7; }
grep -q "fluxScheme[[:space:]]\+Kurganov" "$CASE_DIR/system/fvSchemes" || { echo "ABORT: fvSchemes does not carry fluxScheme Kurganov (AXIS 1)"; exit 7; }
grep -q "reconstruct(rho)" "$CASE_DIR/system/fvSchemes" || { echo "ABORT: fvSchemes does not carry the rhoCentralFoam reconstruct schemes (AXIS 1)"; exit 7; }
cmp -s "$CASE_DIR/system/fvSolution" "$R5_CASE_DIR/system/fvSolution" && { echo "ABORT: fvSolution IDENTICAL to R5 -- the rhoCentralFoam solver set was not installed (AXIS 1)"; exit 7; }
[ -e "$CASE_DIR/constant/fvOptions" ] && { echo "ABORT: constant/fvOptions is PRESENT -- rhoCentralFoam has no limitTemperature; R6 removes it (AXIS 1)"; exit 7; }
[ -e "$R5_CASE_DIR/constant/fvOptions" ] || { echo "ABORT: R5 parity reference constant/fvOptions missing -- cannot confirm the removal is a real delta"; exit 7; }
N_R6=$(find "$CASE_DIR" -type f | wc -l)
[ "$N_R6" = "10" ] || { echo "ABORT: R6 carries $N_R6 case inputs, expected 10 (R5's 11 minus constant/fvOptions)"; exit 7; }
echo "R5-parity OK: 6 carried inputs byte-identical to R5; 0/p (lInf 0.3), controlDict (rhoCentralFoam, maxCo 0.2), fvSchemes (Kurganov), fvSolution changed; fvOptions removed; 10 files."

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
    rel="cases/ansys_verification/VMFL046-R6/case/${f#$CASE_DIR/}"
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

  # rc is captured DIRECTLY from the timeout subshell (its exit status IS timeout's: 124 on
  # kill, else the solver's rc).  NO setsid (setsid-parent-returns-zero).
  t0=$(date +%s)
  ( cd "$LD" && timeout "${timeout_s}s" rhoCentralFoam ) > "$LD/log.rhoCentralFoam" 2>&1
  rc=$?
  echo "$rc" > "$LD/RUN_RC"
  t1=$(date +%s); wall=$((t1-t0))
  used=$(awk "BEGIN{print $wall*$RANKS/60}")
  CORE_MIN_USED=$(awk "BEGIN{print $CORE_MIN_USED+$used}")
  echo "  $L: rc=$rc wall=${wall}s core_min_used=$CORE_MIN_USED / cap $CAP_CORE_MIN"
  if [ "$rc" = "124" ]; then echo "ABORT $L: cap overrun stopped the run (rc 124, rule 12)"; exit 124; fi
  if [ "$rc" != "0" ]; then echo "ABORT $L: rhoCentralFoam rc=$rc"; exit 11; fi
done

echo "=== VMFL046-R6 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
