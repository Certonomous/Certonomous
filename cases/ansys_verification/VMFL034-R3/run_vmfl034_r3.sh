#!/usr/bin/env bash
# =============================================================================
# VMFL034-R3 graded-run driver -- THE FROZEN-FLOW RE-SCOPE.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.121-122 (VMFL034:
# Particle Aggregation inside a Turbulent Stirred Tank; "Moments are solved on a
# frozen flow field").  Successor to VMFL034-R2 (register #59, NOT A RESULT: SIGFPE
# rc 136 in SchillerNaumann::CdRe, live two-phase drag).
#
# TWO-STAGE, the direct analogue of the manual journal:
#   STAGE 1 (answer-blind carrier):  simpleFoam single-phase k-epsilon on the box
#            mesh -> converged, FROZEN U/phi/k/epsilon/nut.  ("flow yes ke yes")
#   STAGE 2 (graded):  reactingTwoPhaseEulerFoamFrozen (frozen-flow build; PIMPLE
#            loop omits pU/UEqns.H+EEqns.H+pU/pEqn.H, the ONLY drag/CdRe site)
#            transports the constant-kernel population balance on the FROZEN
#            carrier.  ("flow no ke no; moments yes; iterate")
#
# Grading freeze (prereg + comparator + solver source): e0e3eddf
#   PREREGISTRATION.md, analyse_vmfl034_r3.py (blob 5fc867d9...),
#   solver/reactingTwoPhaseEulerFoamFrozen/ (blob 405273b1...).
# Case inputs: byte-for-byte reuse of R2's frozen physics (0.orig/constant/system/
#   grids) EXCEPT system/controlDict, whose `application` names the frozen solver.
#
# THIS DRIVER: NO queue-entry JSON, NO register write.  It compiles the pinned
# frozen solver, runs Stage 1 -> freezes/maps the carrier -> runs Stage 2 per level,
# under per-level and running-total core-min caps (rule 12).  Age-guard safe: it
# creates the run root ONLY at launch; the 0/ it stages is initial conditions.
# =============================================================================

set -euo pipefail

RANKS=1        # serial (small 2-D well-mixed box; per-step cost measured single-rank).

# --- COST (PREREGISTRATION s.12).  Frozen-flow smoke-anchored: 0.022 s/step @16 gr,
#     ~N^2 aggregation -> S1 1.5 / S2 6.1 / S3 24.4 core-h @ 2.5e5 steps; carrier ~0.5.
#     Per-level caps ~2x estimate; RUNNING TOTAL cap 3960 core-min (66 core-h, 2x ~33).
CAP_CORE_MIN=3960                                        # RUNNING TOTAL (Stage1 + Stage2 all levels)
CAP_CARRIER=60                                           # core-min for ONE Stage-1 carrier solve
declare -A CAP_LEVEL=( [S1]=200 [S2]=750 [S3]=3000 )    # core-min Stage-2 per level
declare -A NGRP=( [S1]=16 [S2]=32 [S3]=64 )             # frozen r=2 triple class counts

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CASE_REL="cases/ansys_verification/VMFL034-R3"

# FREEZE_COMMIT = the grading freeze (prereg + comparator + solver source).  Resolved
# from the short sha in-shell (NEVER hand-typed; L-382).  A GRADED run REFUSES if it
# cannot resolve, or if the pins below do not match it.
FREEZE_COMMIT="${FREEZE_COMMIT:-$(git -C "$SCRIPT_DIR" rev-parse e0e3eddf^{commit} 2>/dev/null || echo __UNRESOLVED__)}"

# grading-path pins (s.D of the frozen PREREGISTRATION).
COMPARATOR_REL="$CASE_REL/analyse_vmfl034_r3.py"
COMPARATOR_PIN="5fc867d964250b27639362e20f43b0af69c4840c"
declare -A SOLVER_PIN=(
  ["solver/reactingTwoPhaseEulerFoamFrozen/reactingTwoPhaseEulerFoamFrozen.C"]="405273b19dcf08641b9c555fae8ab04fe360d49b"
  ["solver/reactingTwoPhaseEulerFoamFrozen/createFields.H"]="df7c20a798bbc3663575aee20c06e4058fdd2b20"
  ["solver/reactingTwoPhaseEulerFoamFrozen/createFieldRefs.H"]="a8247c9e1cd5b5b240a57e1c0e31a07dfc5ce0e6"
  ["solver/reactingTwoPhaseEulerFoamFrozen/Make/files"]="e2a515e3d7ffbdfe76ad7cd5f56d93fdaa9996e7"
  ["solver/reactingTwoPhaseEulerFoamFrozen/Make/options"]="aba9ee616dc0999337b8bf8cab8287ae5ab24d5b"
)

RUN_ROOT="${1:?usage: run_vmfl034_r3.sh <run_root> [levels...]   (levels default: S1 S2 S3 = 16/32/64 groups)}"
shift 2>/dev/null || true
LEVELS_TO_RUN="${*:-S1 S2 S3}"
SMOKE="${VMFL034R3_SMOKE:-0}"
SMOKE_ENDTIME="${VMFL034R3_ENDTIME:-}"

echo "=== VMFL034-R3 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  levels='$LEVELS_TO_RUN'  smoke=$SMOKE"
echo "    FREEZE_COMMIT=$FREEZE_COMMIT"

# ---- 0. every path this driver references EXISTS (s.39.5 applied to the launcher).
SRC="$SCRIPT_DIR"
for p in "$SRC/0.orig" "$SRC/constant" "$SRC/system" "$SRC/grids" "$SRC/stage1" \
         "$SRC/0.orig/alpha.air" "$SRC/0.orig/U.air" "$SRC/0.orig/U.water" \
         "$SRC/0.orig/p" "$SRC/0.orig/p_rgh" "$SRC/0.orig/km" "$SRC/0.orig/epsilonm" \
         "$SRC/constant/g" "$SRC/constant/phaseProperties" \
         "$SRC/constant/turbulenceProperties.air" "$SRC/constant/turbulenceProperties.water" \
         "$SRC/system/controlDict" "$SRC/system/blockMeshDict" "$SRC/system/topoSetDict" \
         "$SRC/system/fvSchemes" "$SRC/system/fvSolution" \
         "$SRC/stage1/system/controlDict" "$SRC/stage1/system/fvSchemes" "$SRC/stage1/system/fvSolution" \
         "$SRC/stage1/constant/transportProperties" "$SRC/stage1/constant/turbulenceProperties" \
         "$SRC/stage1/0/U" "$SRC/stage1/0/p" "$SRC/stage1/0/k" "$SRC/stage1/0/epsilon" "$SRC/stage1/0/nut" \
         "$SRC/analyse_vmfl034_r3.py" "$SRC/gen_sizegroups.py" "$SRC/map_carrier.py" \
         "$SRC/solver/reactingTwoPhaseEulerFoamFrozen/reactingTwoPhaseEulerFoamFrozen.C" \
         "$SRC/grids/S1/constant/phaseProperties" "$SRC/grids/S1/0.orig/f0.air.bubbles" \
         "$SRC/grids/S3/constant/phaseProperties" "$SRC/grids/S3/0.orig/f0.air.bubbles" ; do
  [ -e "$p" ] || { echo "ABORT: driver references a path that does not exist: $p"; exit 2; }
done

# ---- 1. OpenFOAM environment, sourced by the driver ITSELF, BEFORE any command -v.
set +u
# shellcheck disable=SC1091
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source v2606 bashrc"; exit 2; }
set -u
for exe in blockMesh topoSet simpleFoam wmake; do
  command -v "$exe" >/dev/null || { echo "ABORT: $exe not on PATH after sourcing v2606 bashrc"; exit 2; }
done

# ---- 2. SMOKE run_root must be under a scratch area (never verification/runs/).
if [ "$SMOKE" = "1" ]; then
  case "$RUN_ROOT" in
    /tmp/*|*/scratchpad/*) : ;;
    *) echo "ABORT smoke: run_root $RUN_ROOT is not under a scratch area"; exit 3 ;;
  esac
fi

# ---- 3. GRADING-PATH PINS (rule 2).  Comparator + solver source must hash to their
#         committed blobs AND match FREEZE_COMMIT (the grading freeze e0e3eddf).
if [ "$FREEZE_COMMIT" = "__UNRESOLVED__" ]; then
  echo "ABORT: cannot resolve FREEZE_COMMIT (git rev-parse e0e3eddf). Grading path unverifiable."; exit 5
fi
git -C "$SCRIPT_DIR" cat-file -e "${FREEZE_COMMIT}^{commit}" 2>/dev/null || { echo "ABORT: FREEZE_COMMIT $FREEZE_COMMIT not found"; exit 5; }
pin_fail=0
chk() { local rel="$1" want="$2"; local disk blob
  disk="$(git -C "$SCRIPT_DIR" hash-object "$REPO_ROOT/$rel")"
  blob="$(git -C "$SCRIPT_DIR" rev-parse "${FREEZE_COMMIT}:$rel" 2>/dev/null || echo MISSING)"
  [ "$disk" = "$want" ] || { echo "PIN FAIL: $rel disk=$disk != pin $want"; pin_fail=1; }
  [ "$disk" = "$blob" ] || { echo "FREEZE FAIL: $rel disk=$disk != ${FREEZE_COMMIT}:$rel=$blob"; pin_fail=1; }
}
chk "$COMPARATOR_REL" "$COMPARATOR_PIN"
for rel in "${!SOLVER_PIN[@]}"; do chk "$CASE_REL/$rel" "${SOLVER_PIN[$rel]}"; done
[ "$pin_fail" = "0" ] || { echo "ABORT: grading-path pin/freeze mismatch (rule 2)"; exit 6; }
echo "grading-path pins OK: comparator + solver source match their s.D pins AND FREEZE_COMMIT"

# ---- 3b. CASE-INPUT SELF-CHECK (rule 2).  The staged case inputs must match the
#          committed materialization (HEAD).  Physics is byte-for-byte R2 reuse; this
#          proves the file that runs is the file that was committed.
head_commit="$(git -C "$SCRIPT_DIR" rev-parse HEAD)"
ci_fail=0
while IFS= read -r f; do
  rel="$CASE_REL/${f#$SRC/}"
  disk="$(git -C "$SCRIPT_DIR" hash-object "$f")"
  blob="$(git -C "$SCRIPT_DIR" rev-parse "${head_commit}:$rel" 2>/dev/null || echo MISSING)"
  [ "$disk" = "$blob" ] || { echo "CASE-INPUT FAIL: $rel disk=$disk head=$blob"; ci_fail=1; }
done < <(find "$SRC/0.orig" "$SRC/constant" "$SRC/system" "$SRC/grids" "$SRC/stage1" -type f | sort)
[ "$ci_fail" = "0" ] || { echo "ABORT: case-input self-check failed (rule 2)"; exit 6; }
echo "case-input self-check OK: all staged inputs match committed HEAD $head_commit"

# ---- 3c. COMPILE the pinned frozen solver into FOAM_USER_APPBIN (answer-blind).
export FOAM_USER_APPBIN="${FOAM_USER_APPBIN:-$HOME/OpenFOAM/$USER-v2606/platforms/${WM_OPTIONS}/bin}"
mkdir -p "$FOAM_USER_APPBIN"
( cd "$SRC/solver/reactingTwoPhaseEulerFoamFrozen" && wmake ) > "$SRC/solver/log.wmake" 2>&1 \
  || { echo "ABORT: wmake of reactingTwoPhaseEulerFoamFrozen failed (see solver/log.wmake)"; exit 7; }
FROZEN_BIN="$FOAM_USER_APPBIN/reactingTwoPhaseEulerFoamFrozen"
[ -x "$FROZEN_BIN" ] || { echo "ABORT: frozen solver binary not built at $FROZEN_BIN"; exit 7; }
echo "frozen solver compiled: $FROZEN_BIN  (sha1 $(sha1sum "$FROZEN_BIN" | cut -d' ' -f1))"

# ---- 3d. run root must NOT already exist (age-guard safe; rule 4).  Created ONLY here.
if [ -e "$RUN_ROOT" ]; then
  echo "ABORT: run root $RUN_ROOT already exists (rule 4: it must not exist until launch)"; exit 4
fi
mkdir -p "$RUN_ROOT"

# ---- 4. run each requested level.
CORE_MIN_USED=0
cap_stop() { # $1 = core-min just consumed; abort if running total exceeds cap
  CORE_MIN_USED="$(awk "BEGIN{print $CORE_MIN_USED+$1}")"
  if awk "BEGIN{exit !($CORE_MIN_USED > $CAP_CORE_MIN)}"; then
    echo "ABORT: running-total core-min $CORE_MIN_USED > cap $CAP_CORE_MIN (rc 124, rule 12; no new budget)"; exit 124
  fi
}

for L in $LEVELS_TO_RUN; do
  [ -n "${NGRP[$L]:-}" ] || { echo "ABORT: unknown level '$L' (known: S1 S2 S3)"; exit 2; }
  ng="${NGRP[$L]}"
  if [ "$L" = "S2" ]; then FSRC="$SRC"; else FSRC="$SRC/grids/$L"; fi
  [ -d "$FSRC" ] || { echo "ABORT $L: frozen instance $FSRC missing"; exit 20; }
  ngrid="$(grep -cE '^\s*f[0-9]+\{d ' "$FSRC/constant/phaseProperties")"
  [ "$ngrid" = "$ng" ] || { echo "ABORT $L: $FSRC has $ngrid groups, registered $ng"; exit 20; }
  echo "  NOTE $L: a SINGLE grid alone grades NOT A RESULT (rule 5); a verdict needs the full 16/32/64 triple."

  LD="$RUN_ROOT/$L"
  if [ -e "$LD/0" ] || ls -d "$LD"/[0-9]* >/dev/null 2>&1; then
    echo "ABORT $L: $LD already holds 0/ or a numeric time dir (rule 4 launch guard)"; exit 4
  fi
  mkdir -p "$LD/0" "$LD/constant" "$LD/system"

  # --- 4c. stage FROZEN Stage-2 inputs.  0.orig holds the 18 shared fields PLUS the
  #         S2 f-fields; exclude all f-fields from the shared copy, overlay per-level.
  for f in "$SRC/0.orig/"*; do
    b="$(basename "$f")"
    case "$b" in f.air.bubbles|f[0-9]*) : ;; *) cp "$f" "$LD/0/" ;; esac
  done
  cp "$FSRC/0.orig/"f*.air.bubbles "$LD/0/"
  for f in "$SRC/constant/"*; do
    b="$(basename "$f")"
    [ "$b" = "phaseProperties" ] || cp -a "$f" "$LD/constant/"
  done
  cp "$FSRC/constant/phaseProperties" "$LD/constant/"
  cp "$SRC/system/"* "$LD/system/" 2>/dev/null || true
  [ -f "$LD/system/controlDict" ] || cp "$SRC/system/controlDict" "$LD/system/"
  if [ "$SMOKE" = "1" ] && [ -n "$SMOKE_ENDTIME" ]; then
    sed -i "s/^endTime .*/endTime         $SMOKE_ENDTIME;/" "$LD/system/controlDict"
  fi

  # --- 4d. mesh + zones.
  ( cd "$LD" && blockMesh ) > "$LD/log.blockMesh" 2>&1 || { echo "ABORT $L: blockMesh rc=$?"; exit 10; }
  ( cd "$LD" && topoSet )   > "$LD/log.topoSet"   2>&1 || { echo "ABORT $L: topoSet rc=$?";   exit 10; }

  # --- 4e. STAGE 1: single-phase carrier on the same mesh (answer-blind).
  S1D="$LD/stage1"
  mkdir -p "$S1D/system" "$S1D/constant" "$S1D/0"
  cp "$SRC/stage1/system/"*    "$S1D/system/"
  cp "$SRC/stage1/constant/"*  "$S1D/constant/"
  cp "$SRC/stage1/0/"*         "$S1D/0/"
  cp -a "$LD/constant/polyMesh" "$S1D/constant/polyMesh"
  carrier_to_s="$(awk "BEGIN{printf \"%d\", $CAP_CARRIER*60/$RANKS}")"
  cat > "$S1D/_carrier_inner.sh" <<'INNER'
#!/usr/bin/env bash
cd "$1" || { echo 98 > RUN_RC; exit 98; }
timeout "$2" simpleFoam > log.simpleFoam 2>&1
echo $? > RUN_RC
INNER
  chmod +x "$S1D/_carrier_inner.sh"
  t0="$(date +%s)"; setsid "$S1D/_carrier_inner.sh" "$S1D" "${carrier_to_s}s" || true; t1="$(date +%s)"
  crc="$(cat "$S1D/RUN_RC" 2>/dev/null || echo 97)"
  cap_stop "$(awk "BEGIN{print ($t1-$t0)*$RANKS/60}")"
  [ "$crc" = "0" ] || { echo "ABORT $L: Stage-1 simpleFoam carrier rc=$crc (a non-zero rc is a finding)"; exit 11; }
  # converged carrier = latest numeric time dir in stage1 (> 0).
  CT="$(cd "$S1D" && ls -d [0-9]* 2>/dev/null | sort -g | tail -1)"
  [ -n "$CT" ] && [ "$CT" != "0" ] || { echo "ABORT $L: Stage-1 wrote no converged carrier time dir"; exit 11; }
  echo "  $L: Stage-1 carrier converged at $S1D/$CT (rc 0)"

  # --- 4f. FREEZE/MAP the carrier internal field into the Stage-2 0/ fields.
  python3 "$SRC/map_carrier.py" --carrier "$S1D/$CT" --target "$LD/0" \
    || { echo "ABORT $L: map_carrier failed (exit $?)"; exit 12; }

  # --- 4g. AGE-GUARD MARKER, touched LAST then ASSERTED (rule 4).  The mapping above
  #         has finished writing 0/ fields; now 0/alpha.air is made newest.
  find "$LD/0" -type f -exec touch {} +
  touch "$LD/0/alpha.air"
  newer="$(find "$LD/0" -type f -newer "$LD/0/alpha.air" -not -path "$LD/0/alpha.air" || true)"
  if [ -n "$newer" ]; then
    echo "ABORT $L: age-guard assert FAILED -- 0/ files newer than the 0/alpha.air marker:"; echo "$newer"; exit 4
  fi
  echo "  $L: age-guard marker 0/alpha.air asserted newest"

  # --- 4h. STAGE 2: the frozen-flow solver, rc CAPTURED INSIDE the detached wrapper.
  remaining="$(awk "BEGIN{print ($CAP_CORE_MIN-$CORE_MIN_USED)}")"
  lvlcap="${CAP_LEVEL[$L]}"
  budget="$(awk "BEGIN{print ($remaining < $lvlcap) ? $remaining : $lvlcap}")"
  timeout_s="$(awk "BEGIN{printf \"%d\", $budget*60/$RANKS}")"
  if [ "$timeout_s" -le 0 ]; then echo "ABORT $L: cap exhausted before Stage-2 launch (rc 124, rule 12)"; exit 124; fi
  echo "  $L: Stage-2 budget=${budget} core-min (level cap $lvlcap, remaining total $remaining) -> timeout ${timeout_s}s"
  cat > "$LD/_run_inner.sh" <<INNER
#!/usr/bin/env bash
cd "\$1" || { echo 98 > RUN_RC; exit 98; }
timeout "\$2" "$FROZEN_BIN" > log.reactingTwoPhaseEulerFoamFrozen 2>&1
echo \$? > RUN_RC
INNER
  chmod +x "$LD/_run_inner.sh"
  t0="$(date +%s)"; setsid "$LD/_run_inner.sh" "$LD" "${timeout_s}s" || true; t1="$(date +%s)"
  rc="$(cat "$LD/RUN_RC" 2>/dev/null || echo 97)"
  cap_stop "$(awk "BEGIN{print ($t1-$t0)*$RANKS/60}")"
  echo "  $L: Stage-2 rc=$rc  core_min_used=$CORE_MIN_USED / cap $CAP_CORE_MIN"
  if [ "$rc" = "124" ]; then echo "ABORT $L: cap overrun stopped Stage-2 (rc 124, rule 12)"; exit 124; fi
  if [ "$rc" != "0" ]; then echo "ABORT $L: reactingTwoPhaseEulerFoamFrozen rc=$rc (a non-zero rc is a finding, not a retry)"; exit 11; fi
done

echo "=== VMFL034-R3 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "    grade with: python3 $CASE_REL/analyse_vmfl034_r3.py --triple $RUN_ROOT/S1 $RUN_ROOT/S2 $RUN_ROOT/S3"
