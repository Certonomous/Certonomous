#!/usr/bin/env bash
# ==========================================================================
# T4f CASE LAUNCHER (DRAFT) -- PARALLEL, modelled on the frozen launch_t4e.sh.
#
# T4f runs with DETERMINISTIC domain decomposition (verification ruling 19b7330a,
# application of PARALLEL_GATE_DOCTRINE; NOT a relaxation).  This launcher adds
# decomposePar -> mpirun -np N solver -parallel -> reconstructPar to the T4e
# discipline, keeping every safety property:
#
#   * the solver runs in THIS wrapper's FOREGROUND under `timeout`, with NO
#     `setsid` between `timeout` and `mpirun`, so `$?` is mpirun's status (the
#     setsid-parent-returns-zero discipline: rc captured INSIDE the wrapper);
#   * rc (the SOLVE rc) is written to STATUS.<case> in the case's PARENT dir --
#     the physics-critical field mark_done_t4f.py reads; decompose_rc /
#     reconstruct_rc are written as INFRASTRUCTURE witnesses beside it;
#   * `capped` = (wall_s >= timeout_s) is the independent expiry witness;
#   * the graded fieldAverage (UMean) is read from the RECONSTRUCTED field
#     (reconstructPar), per ruling condition 3;
#   * numerics are IDENTICAL to a serial run (fixed dt, adjustTimeStep off);
#     ONLY the rank column / decomposeParDict differs (ruling condition 4);
#   * --ranks must EQUAL the registered nRanks (a caller can neither widen nor
#     change the frozen decomposition at launch);
#   * 0/ is armed from 0.orig with 0/T touched LAST (age-guard datum) BEFORE
#     decomposePar; reconstructPar writes the endTime fields AFTER the solve, so
#     they are newer than 0/T;
#   * a PRE-FLIGHT REFUSAL writes NO STATUS; an existing STATUS is never overwritten.
#
# STATUS: DRAFT.  NOT FROZEN.  `bash -n`-checked only; NOTHING is launched, no
# decomposePar/solver/reconstructPar is run.  HELD for a later box window.
#
# usage: launch_t4f.sh --case-dir DIR --timeout SECONDS --ranks N
#                      [--solver buoyantBoussinesqPimpleFoam] [--foam-bashrc F]
#                      [--no-detach]
# ==========================================================================
set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGJSON="$SELF/t4f_registered.json"

usage() { sed -n '/^# usage:/,/^# ====/p' "$0" >&2; exit 2; }

CASE_DIR=""; TIMEOUT_S=""; RANKS=""
SOLVER="buoyantBoussinesqPimpleFoam"; DETACH=1
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
while [ $# -gt 0 ]; do
    case "$1" in
        --case-dir) CASE_DIR="${2:-}"; shift 2 ;;
        --timeout)  TIMEOUT_S="${2:-}"; shift 2 ;;
        --ranks)    RANKS="${2:-}"; shift 2 ;;
        --solver)   SOLVER="${2:-}"; shift 2 ;;
        --foam-bashrc) FOAM_BASHRC="${2:-}"; shift 2 ;;
        --no-detach) DETACH=0; shift ;;
        *) usage ;;
    esac
done
[ -n "$CASE_DIR" ] && [ -n "$TIMEOUT_S" ] && [ -n "$RANKS" ] || usage
[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
case "$RANKS" in ''|*[!0-9]*) echo "REFUSE: --ranks must be an integer" >&2; exit 2;; esac
case "$TIMEOUT_S" in ''|*[!0-9]*) echo "REFUSE: --timeout must be integer seconds" >&2; exit 2;; esac

CASE_DIR="$(cd "$CASE_DIR" && pwd)"
ROOT="$(dirname "$CASE_DIR")"
CASE="$(basename "$CASE_DIR")"
STATUS="$ROOT/STATUS.$CASE"

# --- the registered cap AND the registered rank count are read, not trusted ---
if [ -f "$REGJSON" ]; then
    REG_T=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('cost',{}).get('parallel',{}).get('timeout_s','MISSING'))" "$REGJSON" 2>/dev/null || echo UNREADABLE)
    REG_R=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('parallel_decomposition',{}).get('nRanks','MISSING'))" "$REGJSON" 2>/dev/null || echo UNREADABLE)
    case "$REG_T$REG_R" in *UNREADABLE*|*MISSING*) echo "REFUSE: cannot read registered timeout_s / nRanks from $REGJSON" >&2; exit 2 ;; esac
    [ "$TIMEOUT_S" -eq "$REG_T" ] || { echo "REFUSE: --timeout $TIMEOUT_S != registered timeout_s=$REG_T (rule 12: a cap is neither widened nor narrowed at launch)" >&2; exit 2; }
    [ "$RANKS" -eq "$REG_R" ] || { echo "REFUSE: --ranks $RANKS != registered nRanks=$REG_R (the frozen decomposition is not changed at launch; ruling condition 1/4)" >&2; exit 2; }
else
    echo "REFUSE: registered JSON $REGJSON is missing; cap and rank count cannot be checked" >&2; exit 2
fi

[ -e "$STATUS" ] && { echo "REFUSE: $STATUS exists -- a completed run's record is never overwritten" >&2; exit 2; }

# --- detach ONCE by re-executing in a new session --------------------------
if [ "$DETACH" = "1" ] && [ "${T4F_DETACHED:-}" != "1" ]; then
    T4F_DETACHED=1 exec setsid "$0" --case-dir "$CASE_DIR" --timeout "$TIMEOUT_S" \
        --ranks "$RANKS" --solver "$SOLVER" --foam-bashrc "$FOAM_BASHRC" \
        --no-detach </dev/null >>"$CASE_DIR/log.launch" 2>&1 &
    echo "launched $CASE detached; STATUS will appear at $STATUS"
    exit 0
fi

write_status() {   # rc wall checkmesh_rc capped note decompose_rc reconstruct_rc
    tmp="$STATUS.tmp.$$"
    {
      echo "case=$CASE"; echo "rc=$1"; echo "wall_s=$2"; echo "ranks=$RANKS"
      echo "core_min=$(awk -v w="$2" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')"
      echo "timeout_s=$TIMEOUT_S"; echo "capped=$4"; echo "checkmesh_rc=$3"
      echo "decompose_rc=$6"; echo "reconstruct_rc=$7"
      echo "solver=$SOLVER"; echo "solver_path=${SOLVER_PATH:-unresolved}"; echo "note=$5"
      echo "started_utc=$(date -u -d "@$T0" +%Y-%m-%dT%H:%M:%SZ)"
      echo "ended_utc=$(date -u -d "@$T1" +%Y-%m-%dT%H:%M:%SZ)"
    } > "$tmp"
    mv -f "$tmp" "$STATUS"
}

cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

# --- 0. solver reachable ----------------------------------------------------
if [ "$FOAM_BASHRC" != "none" ]; then
    [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
    set +u; . "$FOAM_BASHRC" >/dev/null 2>&1 || true; set -u
fi
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' NOT RESOLVABLE after sourcing $FOAM_BASHRC" >&2; exit 2; }
command -v mpirun >/dev/null 2>&1 || { echo "REFUSE: mpirun not resolvable; parallel run cannot start" >&2; exit 2; }
[ -f "$CASE_DIR/system/decomposeParDict" ] || { echo "REFUSE: no system/decomposeParDict; the frozen decomposition is missing" >&2; exit 2; }

# --- 1. launch guard: no 0/, no numeric time dir, no processor*, 0.orig present ---
[ -e "$CASE_DIR/0" ] && { echo "REFUSE: $CASE already has a 0/ directory (age guard unevaluable)" >&2; exit 2; }
while IFS= read -r d; do
    [ -n "$d" ] && { echo "REFUSE: $CASE already has time directory $(basename "$d")" >&2; exit 2; }
done < <(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?' 2>/dev/null)
ls -d "$CASE_DIR"/processor* >/dev/null 2>&1 && { echo "REFUSE: $CASE already has processor* dirs -- a prior decomposition; refusing" >&2; exit 2; }
[ -d "$CASE_DIR/0.orig" ] || { echo "REFUSE: $CASE has no 0.orig to arm from" >&2; exit 2; }
[ -f "$CASE_DIR/constant/polyMesh/owner" ] || { echo "REFUSE: $CASE has no mesh (constant/polyMesh/owner)" >&2; exit 2; }
for f in U p_rgh T alphat nut k omega; do
    [ -f "$CASE_DIR/0.orig/$f" ] || { echo "REFUSE: 0.orig/$f missing" >&2; exit 2; }
done

# --- 1b. provenance: no compressible-family token in an incompressible case ---
if ! python3 "$SELF/../../../../scripts/check_case_provenance.py" --case "$CASE_DIR" >>"$CASE_DIR/log.launch" 2>&1; then
    echo "REFUSE: $CASE failed check_case_provenance.py; nothing started, no STATUS" >&2; exit 2; fi

# --- 2. checkMesh (infrastructure) ------------------------------------------
checkMesh -case "$CASE_DIR" > "$CASE_DIR/log.checkMesh" 2>&1
CHECKMESH_RC=$?

# --- 3. arm 0/ from 0.orig; 0/T touched LAST (age-guard datum) BEFORE decompose ---
cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/ from 0.orig" >&2; exit 2; }
sleep 1
touch "$CASE_DIR/0/T" || { echo "REFUSE: could not touch 0/T" >&2; exit 2; }

T0=$(date +%s)
# --- 4. decomposePar (deterministic simple; C1 verify: identical per-rank counts on a repeat) ---
decomposePar -case "$CASE_DIR" -force > "$CASE_DIR/log.decomposePar" 2>&1
DECOMP_RC=$?
if [ "$DECOMP_RC" != "0" ]; then
    T1=$(date +%s)
    write_status "$DECOMP_RC" "$((T1 - T0))" "$CHECKMESH_RC" no DECOMPOSE_FAILED "$DECOMP_RC" NA
    echo "$CASE decomposePar FAILED rc=$DECOMP_RC -> $STATUS" >&2; exit "$DECOMP_RC"
fi

# --- 5. the solver, PARALLEL, FOREGROUND under timeout, rc captured from mpirun ---
timeout "$TIMEOUT_S" mpirun -np "$RANKS" "$SOLVER_PATH" -case "$CASE_DIR" -parallel > "$CASE_DIR/log.solve" 2>&1
RC=$?
T1=$(date +%s)
WALL=$((T1 - T0))
if [ "$WALL" -ge "$TIMEOUT_S" ]; then CAPPED=yes; else CAPPED=no; fi

# --- 6. reconstructPar so the graded UMean/endTime fields exist in the case root (ruling cond 3) ---
RECON_RC=NA
if [ "$RC" = "0" ]; then
    reconstructPar -case "$CASE_DIR" > "$CASE_DIR/log.reconstructPar" 2>&1
    RECON_RC=$?
fi

NOTE=clean
if [ "$RC" = "124" ]; then NOTE=CAP_EXPIRED_or_child_exit_124
elif [ "$RC" -gt 128 ] 2>/dev/null; then NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then NOTE=SOLVER_NONZERO_EXIT
elif [ "$RECON_RC" != "0" ]; then NOTE=RECONSTRUCT_FAILED
fi
write_status "$RC" "$WALL" "$CHECKMESH_RC" "$CAPPED" "$NOTE" "$DECOMP_RC" "$RECON_RC"
echo "$CASE finished: rc=$RC wall=${WALL}s ranks=$RANKS capped=$CAPPED decompose_rc=$DECOMP_RC reconstruct_rc=$RECON_RC note=$NOTE -> $STATUS"
exit "$RC"
