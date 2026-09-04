#!/usr/bin/env bash
# =============================================================================
# VMFL034-R2 graded-run driver.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.121-122 (VMFL034:
# Particle Aggregation inside a Turbulent Stirred Tank -- constant-kernel
# aggregation in a CMSMPR box).  SUCCESSOR to the struck VMFL034 (freeze f4f80b53).
# Solver: reactingTwoPhaseEulerFoam (OpenFOAM v2606), transient two-phase Euler +
#         sectional populationBalance, RESCALED operating point (walls 6.06/6.00 m/s,
#         inlet 0.10 m/s, tau=5 s, beta0_OF=2000, endTime=25 s = 5 tau) -- BYTE-
#         IDENTICAL to the struck case's settled physics (PREREGISTRATION s.R.6).
#
# Frozen pre-registration : cases/ansys_verification/VMFL034-R2/PREREGISTRATION.md
# Frozen comparator       : cases/ansys_verification/VMFL034-R2/analyse_vmfl034_r2.py
#                           (s.D pin: blob 7f2329485c2d33bd7bf053fc546c94191f979895)
# Pinned generator        : gen_sizegroups.py (blob d5dfff4fdb500bb9911b8051b4bf04bb6f9a5950)
# Pinned templates        : templates/phaseProperties.template (144b69ef...), f.template (c10243e0...)
# Run root (arg 1)        : verification/runs/ansys_verification/VMFL034-R2/  (NEVER the case dir)
#
# THE FROZEN GATE IS THE r=2 (N_g/2N_g/4N_g) SIZE-GROUP ROACHE TRIPLE 16/32/64
# (PREREGISTRATION s.R.1/s.7).  ALL THREE grid+feed instances are committed under
# grids/{S1,S2,S3}/ -- built by the PINNED generator from the frozen archive feed
# moments BEFORE the freeze commit.  This driver STAGES those frozen instances; it
# does NOT generate anything at grade time.  (This repairs the struck driver, which
# refused because two levels of its 25/35/50 spread were never committed.)
# =============================================================================

set -euo pipefail

RANKS=1        # serial (a small well-mixed box mesh; per-step cost measured single-rank).

# --- COST (PREREGISTRATION s.R.4).  N^2-anchored on the medium (32 groups) at
#     ~8.4 core-h:  S1(16)=8.4*(16/32)^2=2.1, S2(32)=8.4, S3(64)=8.4*(64/32)^2=33.4
#     core-h (sum ~43.9).  Per-level caps are 2x each estimate; the RUNNING TOTAL
#     cap is 88 core-h (2x). An overrun STOPS the run (rc 124, CLAUDE.md rule 12).
CAP_CORE_MIN=5280                                        # 88 core-h RUNNING TOTAL
declare -A CAP_LEVEL=( [S1]=252 [S2]=1004 [S3]=4014 )    # core-min: 4.2 / 16.7 / 66.9 core-h (2x)
declare -A NGRP=( [S1]=16 [S2]=32 [S3]=64 )              # frozen r=2 triple class counts (s.R.1)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
# FREEZE_COMMIT: the case-inputs freeze commit. It cannot exist before the freeze,
# so the SUPERVISOR sets it at freeze (env FREEZE_COMMIT=<sha> or edit here). A
# GRADED run REFUSES while it is the placeholder; a SMOKE (scratch) proceeds.
FREEZE_COMMIT="${FREEZE_COMMIT:-__SET_AT_FREEZE__}"
COMPARATOR_PIN="7f2329485c2d33bd7bf053fc546c94191f979895"
GENERATOR_PIN="d5dfff4fdb500bb9911b8051b4bf04bb6f9a5950"
TPL_PP_PIN="144b69ef775e82fefdf6d5a25df98fcf8c9ae3a3"
TPL_F_PIN="c10243e0f6f1c64056e2780274b365aed37902cb"
CASE_REL="cases/ansys_verification/VMFL034-R2"

RUN_ROOT="${1:?usage: run_vmfl034_r2.sh <run_root> [levels...]   (levels default: S1 S2 S3 = 16/32/64 groups)}"
shift 2>/dev/null || true
LEVELS_TO_RUN="${*:-S1 S2 S3}"
SMOKE="${VMFL034R2_SMOKE:-0}"
SMOKE_ENDTIME="${VMFL034R2_ENDTIME:-}"

echo "=== VMFL034-R2 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  levels='$LEVELS_TO_RUN'  smoke=$SMOKE"

# ---- 0. every path this driver references EXISTS (charter s.39.5 applied to the
#         launcher: `bash -n` checks syntax, never path existence).
SRC="$SCRIPT_DIR"
for p in "$SRC" "$SRC/0.orig" "$SRC/constant" "$SRC/system" "$SRC/grids" \
         "$SRC/0.orig/alpha.air" "$SRC/0.orig/U.air" "$SRC/0.orig/U.water" \
         "$SRC/0.orig/p" "$SRC/0.orig/p_rgh" \
         "$SRC/constant/g" "$SRC/constant/thermophysicalProperties.air" \
         "$SRC/constant/thermophysicalProperties.water" \
         "$SRC/constant/turbulenceProperties.air" "$SRC/constant/turbulenceProperties.water" \
         "$SRC/system/controlDict" "$SRC/system/blockMeshDict" "$SRC/system/topoSetDict" \
         "$SRC/system/fvSchemes" "$SRC/system/fvSolution" \
         "$SRC/constant/phaseProperties" "$SRC/0.orig/f0.air.bubbles" \
         "$SRC/analyse_vmfl034_r2.py" "$SRC/gen_sizegroups.py" \
         "$SRC/templates/phaseProperties.template" "$SRC/templates/f.template" \
         "$SRC/grids/S1/constant/phaseProperties" "$SRC/grids/S1/0.orig/f0.air.bubbles" \
         "$SRC/grids/S3/constant/phaseProperties" "$SRC/grids/S3/0.orig/f0.air.bubbles" ; do
  [ -e "$p" ] || { echo "ABORT: driver references a path that does not exist: $p"; exit 2; }
done

# ---- 1. OpenFOAM environment, sourced by the driver ITSELF, BEFORE any command -v
#         (charter s.14/s.15; VMFL046-R2 pattern: a smoke in a shell the launch
#         never gets proves nothing; the daemon's bare PATH has no OpenFOAM).
set +u
# shellcheck disable=SC1091
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
set -u
command -v blockMesh                 >/dev/null || { echo "ABORT: blockMesh not on PATH after sourcing v2606 bashrc"; exit 2; }
command -v topoSet                   >/dev/null || { echo "ABORT: topoSet not on PATH after sourcing v2606 bashrc"; exit 2; }
command -v reactingTwoPhaseEulerFoam >/dev/null || { echo "ABORT: reactingTwoPhaseEulerFoam not on PATH after sourcing v2606 bashrc"; exit 2; }

# ---- 2. SMOKE run_root must be under a scratch area (never verification/runs/).
if [ "$SMOKE" = "1" ]; then
  case "$RUN_ROOT" in
    /tmp/*|*/scratchpad/*) : ;;
    *) echo "ABORT smoke: run_root $RUN_ROOT is not under a scratch area"; exit 3 ;;
  esac
fi

# ---- 3. GRADING-PATH PINS (CLAUDE.md rule 2).  The comparator, the generator and
#         the two templates must hash to their committed blob pins -- always, even
#         before FREEZE_COMMIT is known (they are self-contained frozen material).
pin_fail=0
check_pin() { local f="$1" want="$2"; local got; got="$(git -C "$SCRIPT_DIR" hash-object "$f")"
  if [ "$got" != "$want" ]; then echo "PIN FAIL: $f disk=$got != pin $want"; pin_fail=1; fi; }
check_pin "$SRC/analyse_vmfl034_r2.py" "$COMPARATOR_PIN"
check_pin "$SRC/gen_sizegroups.py"     "$GENERATOR_PIN"
check_pin "$SRC/templates/phaseProperties.template" "$TPL_PP_PIN"
check_pin "$SRC/templates/f.template"  "$TPL_F_PIN"
[ "$pin_fail" = "0" ] || { echo "ABORT: grading-path pin mismatch (rule 2) -- the file that would run is not the pinned file"; exit 6; }
echo "grading-path pins OK: comparator + generator + templates match their s.D pins"

# ---- 3b. CASE-INPUT FREEZE GATE (rule 2).  Every staged case input hashes to its
#          committed blob at FREEZE_COMMIT.  A GRADED run REFUSES until the
#          supervisor sets FREEZE_COMMIT; a SMOKE proceeds in scratch.
freeze_verify() {
  local commit="$1"; local ff=0
  git -C "$SCRIPT_DIR" cat-file -e "${commit}^{commit}" 2>/dev/null || { echo "ABORT: freeze commit $commit not found"; exit 5; }
  while IFS= read -r f; do
    rel="$CASE_REL/${f#$SRC/}"
    disk="$(git -C "$SCRIPT_DIR" hash-object "$f")"
    blob="$(git -C "$SCRIPT_DIR" rev-parse "${commit}:$rel" 2>/dev/null || echo MISSING)"
    [ "$disk" = "$blob" ] || { echo "FREEZE-GATE FAIL: $rel disk=$disk frozen=${blob}"; ff=1; }
  done < <(find "$SRC/0.orig" "$SRC/constant" "$SRC/system" "$SRC/grids" -type f | sort)
  [ "$ff" = "0" ] || { echo "ABORT: freeze gate failed (rule 2)"; exit 6; }
  echo "freeze-gate OK: all case inputs match $commit"
}
if [ "$FREEZE_COMMIT" = "__SET_AT_FREEZE__" ]; then
  if [ "$SMOKE" != "1" ]; then
    echo "ABORT: FREEZE_COMMIT is unset (placeholder). A GRADED run must verify the"
    echo "  case inputs against the freeze commit. The SUPERVISOR sets it at freeze"
    echo "  (env FREEZE_COMMIT=<sha> or edit this driver). The comparator, generator"
    echo "  and templates were pin-verified above; only the case-input freeze ref is missing."
    exit 5
  fi
  echo "SMOKE: FREEZE_COMMIT unset -- case-input freeze verification skipped (scratch only)."
else
  freeze_verify "$FREEZE_COMMIT"
fi

# ---- 4. run each requested level.
CORE_MIN_USED=0
for L in $LEVELS_TO_RUN; do
  [ -n "${NGRP[$L]:-}" ] || { echo "ABORT: unknown level '$L' (known: S1 S2 S3)"; exit 2; }
  ng="${NGRP[$L]}"
  # per-level FROZEN source: the MEDIUM (S2, 32 groups) lives at the case root; the
  # COARSE (S1) and FINE (S3) live under grids/.  This is the frozen-VMFL034 layout.
  if [ "$L" = "S2" ]; then FSRC="$SRC"; else FSRC="$SRC/grids/$L"; fi
  [ -d "$FSRC" ] || { echo "ABORT $L: frozen instance $FSRC missing"; exit 20; }
  # the instance's committed group count must match the registered NGRP.
  ngrid="$(grep -cE '^\s*f[0-9]+\{d ' "$FSRC/constant/phaseProperties")"
  [ "$ngrid" = "$ng" ] || { echo "ABORT $L: $FSRC has $ngrid groups, registered $ng"; exit 20; }
  echo "  NOTE $L: a SINGLE grid alone grades NOT A RESULT (rule 5); a verdict needs the full 16/32/64 triple."

  # --- 4b. LAUNCH GUARD (rule 4): refuse a level dir that already holds 0/ or a time dir.
  LD="$RUN_ROOT/$L"
  if [ -e "$LD/0" ] || ls -d "$LD"/[0-9]* >/dev/null 2>&1; then
    echo "ABORT $L: $LD already holds 0/ or a numeric time dir (rule 4 launch guard)"; exit 4
  fi
  mkdir -p "$LD/0" "$LD/constant" "$LD/system"

  # --- 4c. stage FROZEN inputs.  Nothing is generated.  The case-root 0.orig holds
  #         the 18 SHARED fields PLUS the medium (32-group) f-fields, so the SHARED
  #         copy EXCLUDES all population-balance f-fields and the correct per-level
  #         f-fields are overlaid from FSRC.
  for f in "$SRC/0.orig/"*; do
    b="$(basename "$f")"
    case "$b" in f.air.bubbles|f[0-9]*) : ;; *) cp "$f" "$LD/0/" ;; esac
  done
  cp "$FSRC/0.orig/"f*.air.bubbles          "$LD/0/"          # per-level f<i> + parent f.air.bubbles
  for f in "$SRC/constant/"*; do
    b="$(basename "$f")"
    [ "$b" = "phaseProperties" ] || cp "$f" "$LD/constant/"
  done
  cp "$FSRC/constant/phaseProperties"       "$LD/constant/"   # per-level sizeGroups
  cp "$SRC/system/"*                        "$LD/system/"

  if [ "$SMOKE" = "1" ] && [ -n "$SMOKE_ENDTIME" ]; then
    sed -i "s/^endTime .*/endTime         $SMOKE_ENDTIME;/" "$LD/system/controlDict"
  fi

  # --- 4d. mesh + zones, into logs (silent operation, rule 16).
  ( cd "$LD" && blockMesh ) > "$LD/log.blockMesh" 2>&1 || { echo "ABORT $L: blockMesh rc=$?"; exit 10; }
  ( cd "$LD" && topoSet )   > "$LD/log.topoSet"   2>&1 || { echo "ABORT $L: topoSet rc=$?";   exit 10; }

  # --- 4e. AGE-GUARD MARKER, touched LAST then ASSERTED (rule 4).  The comparator
  #         dates every endTime field against 0/alpha.air, so it must be newest.
  find "$LD/0" -type f -exec touch {} +
  touch "$LD/0/alpha.air"
  newer="$(find "$LD" -type f -newer "$LD/0/alpha.air" -not -path "$LD/0/alpha.air" || true)"
  if [ -n "$newer" ]; then
    echo "ABORT $L: age-guard assert FAILED -- files newer than the 0/alpha.air marker:"; echo "$newer"; exit 4
  fi
  echo "  $L: age-guard marker 0/alpha.air asserted newest"

  # --- 4f. CAP (rule 12): per-level and running-total, converted to a wall timeout.
  remaining="$(awk "BEGIN{print ($CAP_CORE_MIN-$CORE_MIN_USED)}")"
  lvlcap="${CAP_LEVEL[$L]}"
  budget="$(awk "BEGIN{print ($remaining < $lvlcap) ? $remaining : $lvlcap}")"
  timeout_s="$(awk "BEGIN{printf \"%d\", $budget*60/$RANKS}")"
  if [ "$timeout_s" -le 0 ]; then echo "ABORT $L: cap exhausted before launch (rule 12)"; exit 124; fi
  echo "  $L: budget=${budget} core-min (level cap $lvlcap, remaining total $remaining) -> timeout ${timeout_s}s"

  # --- 4g. rc CAPTURED INSIDE the detached wrapper (setsid timeout cmd exits 0 for
  #         every outcome -- rc is written from inside, never read off setsid).
  cat > "$LD/_run_inner.sh" <<'INNER'
#!/usr/bin/env bash
cd "$1" || { echo 98 > RUN_RC; exit 98; }
timeout "$2" reactingTwoPhaseEulerFoam > log.reactingTwoPhaseEulerFoam 2>&1
echo $? > RUN_RC
INNER
  chmod +x "$LD/_run_inner.sh"

  t0="$(date +%s)"
  setsid "$LD/_run_inner.sh" "$LD" "${timeout_s}s" || true
  t1="$(date +%s)"
  rc="$(cat "$LD/RUN_RC" 2>/dev/null || echo 97)"
  wall=$((t1-t0))
  used="$(awk "BEGIN{print $wall*$RANKS/60}")"
  CORE_MIN_USED="$(awk "BEGIN{print $CORE_MIN_USED+$used}")"
  echo "  $L: rc=$rc wall=${wall}s core_min_used=$CORE_MIN_USED / cap $CAP_CORE_MIN"
  if [ "$rc" = "124" ]; then echo "ABORT $L: cap overrun stopped the run (rc 124, rule 12)"; exit 124; fi
  if [ "$rc" != "0" ]; then echo "ABORT $L: reactingTwoPhaseEulerFoam rc=$rc (a non-zero rc is a finding, not a retry)"; exit 11; fi
done

echo "=== VMFL034-R2 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
