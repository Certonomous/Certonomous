#!/usr/bin/env bash
# restage_m1c.sh -- M1-C staging via the FROZEN stage_m1.py, scoped by prune.
# FROZEN 2026-09-09 (§3 check-1 done, SOUND).  NO transforms of our own: staging is done
# ENTIRELY by the frozen stage_m1.py (set_ras_model, R16 planted zero, mesh copy,
# 0.orig).  The only new logic is cleanup (cleanup_m1c.sh) and PRUNE, because the
# frozen stage_m1.py (a) ignores --case [L-511(A)] so it stages all cases per arm,
# and (b) makedirs(exist_ok=False) [L-511(B)] so the tree must be empty first.
#
# Sequence:  cleanup -> stage --arm kOmega -> stage --arm kOmegaSST_null
#            -> PRUNE to exactly the 6 target arms -> VERIFY each of the 6.
# DRYRUN default; --execute gated.  Post-freeze use only.
set -uo pipefail

HERE="/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/M1c_multimodel_sweep_completion"
STAGER="/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/M1_multimodel_sweep/stage_m1.py"
SRC="/home/ubuntu/closure-challenge-benchmark/data"
ROOT="/home/ubuntu/closure-data/m1c_completion"
CLEANUP="$HERE/cleanup_m1c.sh"

# The 6 keep targets, arm -> space-separated cases.
KEEP_kOmega="PH_Breuer AR_14_Ret_180 AR_7_Ret_180 AR_1_Ret_180"
KEEP_kOmegaSST_null="PH_Breuer AR_1_Ret_180"

DRYRUN=1
[ "${1:-}" = "--execute" ] && DRYRUN=0
RUN(){ if [ "$DRYRUN" = 1 ]; then echo "DRYRUN would: $*"; else echo "+ $*"; "$@"; fi; }

# --- fail-closed on ROOT (same discipline as cleanup) ------------------------
[ "$ROOT" = "/home/ubuntu/closure-data/m1c_completion" ] || { echo "REFUSE: ROOT not the literal M1-C tree" >&2; exit 2; }
case "$(realpath "$ROOT" 2>/dev/null)" in *multimodel_sweep*) echo "REFUSE: ROOT into evidence" >&2; exit 2 ;; esac

# --- 1. cleanup to an empty tree --------------------------------------------
if [ "$DRYRUN" = 1 ]; then bash "$CLEANUP"; else bash "$CLEANUP" --execute || { echo "REFUSE: cleanup failed" >&2; exit 2; }; fi

# --- 2. stage per-arm via the FROZEN stage_m1.py (all cases per arm) ---------
RUN python3 "$STAGER" --src-root "$SRC" --dst-root "$ROOT" --arm kOmega          --execute
RUN python3 "$STAGER" --src-root "$SRC" --dst-root "$ROOT" --arm kOmegaSST_null  --execute

# --- 3. PRUNE to exactly the 6 -----------------------------------------------
prune_arm(){  # arm  keep-list
  local arm="$1"; shift; local keep=" $* "
  for cdir in "$ROOT/$arm"/*/; do
    [ -d "$cdir" ] || continue
    local cid; cid=$(basename "$cdir")
    local crp; crp=$(realpath "$cdir") || { echo "REFUSE: cannot resolve $cdir" >&2; exit 2; }
    case "$crp" in "$ROOT/$arm/"*) : ;; *) echo "REFUSE: $cdir escapes ROOT" >&2; exit 2 ;; esac
    if [[ "$keep" == *" $cid "* ]]; then
      echo "  keep $arm/$cid"
    else
      RUN rm -rf "$cdir"
    fi
  done
}
prune_arm kOmega          $KEEP_kOmega
prune_arm kOmegaSST_null  $KEEP_kOmegaSST_null

# stage_m1.py wrote STAGING_MANIFEST_M1.json describing the pre-prune 80-arm set;
# rename it so no reader mistakes it for the 6-arm record, and log the prune.
if [ "$DRYRUN" = 0 ] && [ -f "$ROOT/STAGING_MANIFEST_M1.json" ]; then
  mv "$ROOT/STAGING_MANIFEST_M1.json" "$ROOT/STAGING_MANIFEST_M1.preprune.json"
  printf '{\n  "kept": ["kOmega/PH_Breuer","kOmega/AR_14_Ret_180","kOmega/AR_7_Ret_180","kOmega/AR_1_Ret_180","kOmegaSST_null/PH_Breuer","kOmegaSST_null/AR_1_Ret_180"],\n  "note": "frozen stage_m1.py staged all 40 cases per arm (its --case is dead, L-511); pruned to these 6. Pre-prune manifest kept as STAGING_MANIFEST_M1.preprune.json.",\n  "utc": "%s"\n}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$ROOT/PRUNE_LOG_M1C.json"
fi

# --- 4. VERIFY each of the 6 -------------------------------------------------
# NOTE: a freshly STAGED case has 0.orig/ and NO 0/ (run_m1.sh arms 0.orig->0 and
# touches 0/U LAST at LAUNCH, run_m1.sh:112/134).  So the age datum "0/U newest in
# 0/" is a LAUNCH-time property, verified post-run, NOT at stage time.  Here we
# verify the STAGE-time invariants: 0.orig present, RASModel correct, polyMesh
# present, and NO time dir (no 0/, so the queue AGE-GUARD stays clean).
declare -A MODEL=( [kOmega]="kOmega" [kOmegaSST_null]="kOmegaSST" )
verify_one(){  # arm case
  local arm="$1" c="$2" d="$ROOT/$1/$2" ok=1
  [ -d "$d/0.orig" ]                || { echo "  FAIL $arm/$c: no 0.orig"; ok=0; }
  [ -f "$d/0.orig/U" ]              || { echo "  FAIL $arm/$c: no 0.orig/U"; ok=0; }
  [ ! -e "$d/0" ]                   || { echo "  FAIL $arm/$c: 0/ already exists (armed?)"; ok=0; }
  [ -d "$d/constant/polyMesh" ]    || { echo "  FAIL $arm/$c: no polyMesh"; ok=0; }
  local ras; ras=$(sed -n 's/^[[:space:]]*RASModel[[:space:]]\{1,\}\([^;]*\);.*/\1/p' "$d/constant/turbulenceProperties" 2>/dev/null | head -1 | tr -d '[:space:]')
  [ "$ras" = "${MODEL[$arm]}" ]    || { echo "  FAIL $arm/$c: RASModel '$ras' != expected '${MODEL[$arm]}'"; ok=0; }
  # no numeric time dir at all
  local td; td=$(ls -d "$d"/[0-9]* 2>/dev/null | grep -vE '/0\.orig$' | head -1)
  [ -z "$td" ]                     || { echo "  FAIL $arm/$c: has a time dir $td"; ok=0; }
  [ "$ok" = 1 ] && echo "  OK   $arm/$c: 0.orig+U present, RASModel=$ras, polyMesh present, no time dir"
}
if [ "$DRYRUN" = 0 ]; then
  echo "=== VERIFY the 6 ==="
  verify_one kOmega PH_Breuer; verify_one kOmega AR_14_Ret_180
  verify_one kOmega AR_7_Ret_180; verify_one kOmega AR_1_Ret_180
  verify_one kOmegaSST_null PH_Breuer; verify_one kOmegaSST_null AR_1_Ret_180
  echo "=== M1-C tree case dirs remaining ==="
  find "$ROOT" -mindepth 2 -maxdepth 2 -type d | sort
else
  echo "DRYRUN complete -- pass --execute (post-freeze) to cleanup+stage+prune+verify."
fi
