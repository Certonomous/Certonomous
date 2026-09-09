#!/usr/bin/env bash
# ==========================================================================
# PRD-E1 CASE LAUNCHER -- Porous Radiator Duct, Navier-spine Case 3.
#
# The launcher the build_prd.py docstring specifies (build_prd.py:222-226):
#   blockMesh -> topoSet -> (copy 0.orig->0, touch 0/U LAST) -> simpleFoam.
# build_prd.py emits ONLY the case dicts; it launches nothing.  This script
# builds the mesh, creates the porous cellZone + the two Delta-p faceZones,
# arms 0/ from 0.orig, and runs simpleFoam -- with the SOLVER's rc captured
# INSIDE this wrapper (the setsid-parent-returns-zero lesson: `setsid timeout
# cmd` returns 0 for every child outcome, so rc is captured in the FOREGROUND
# `timeout` inside the detached re-exec, NEVER around a setsid line).
#
# Modelled line-for-line on verification/runs/T-family/T13_runs/run_one_t13.sh
# (rc-in-wrapper, detach-once re-exec, launch guard, foreign-process guard),
# with the T13 thermal specifics REPLACED by the PRD incompressible sequence:
#   * solver simpleFoam (not buoyantBoussinesqSimpleFoam);
#   * the age-guard datum is 0/U (mark_done_prd.py AGE_REF=(0,U)); a single-
#     region incompressible isothermal case has NO 0/T;
#   * the mesh is built HERE (blockMesh + topoSet), not by a separate builder:
#     build_prd.py emits dicts only, so the launcher runs blockMesh then
#     topoSet (topoSet MUST follow blockMesh -- the mesh must exist before
#     cellZone/faceZone selection -- and precede the arm/solve);
#   * the 0.orig field set is the incompressible {U,p,k,omega,nut} (phi is
#     written by the solver); no T/p_rgh/alphat;
#   * NO registered-cap JSON gate (T13 reads T13_registered.json): PRD-E1 is
#     NOT FROZEN, this is the STOP-BEFORE-FREEZE §2bb SMOKE; the graded ladder
#     and its registered caps come at launch, not here.  The cap is passed on
#     the command line and is the rule-12 STOP (overrun stops the run).
#
# GENERAL over the sweep (level, U_s, active/inert): pass --emit with
# --level/--us/[--inert] to have this launcher emit the case via build_prd.py
# first, or point --case-dir at a case build_prd.py already emitted.
# --endtime rewrites the emitted controlDict endTime AND writeInterval so a
# short smoke writes its fields at endTime (run-input edit, not a measurement-
# instrument edit; the FROZEN endTime for the graded ladder is pinned later).
#
# STOP-BEFORE-FREEZE.  This launcher freezes nothing, pins no comparator, and
# edits no measurement logic.  It runs OpenFOAM and records rc.
#
# usage: run_prd.sh --case-dir DIR --timeout SECONDS
#                   [--emit --level L1|L2|L3|L4 --us U [--inert]]
#                   [--endtime N] [--solver simpleFoam]
#                   [--foam-bashrc F] [--no-detach]
#   --timeout   hard wall-second cap; wall >= timeout => capped=yes (rule 12
#               STOP witness; the smoke uses 3600 = the ~1 h stall ceiling).
#   --no-detach run in the foreground (the detach re-exec passes this flag).
# Exit: the SOLVER's own rc (never a bare 0), or 2 on a pre-flight REFUSAL
# (a refusal writes NO STATUS: nothing ran, so there is no rc to invent).
# ==========================================================================
set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD="$SELF/build_prd.py"

usage() { sed -n '/^# usage:/,/^# ====/p' "$0" >&2; exit 2; }

CASE_DIR=""; TIMEOUT_S=""; SOLVER="simpleFoam"; DETACH=1
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
DO_EMIT=0; EMIT_LEVEL="L1"; EMIT_US="1.0"; EMIT_INERT=0; ENDTIME=""
RANKS=1
while [ $# -gt 0 ]; do
    case "$1" in
        --case-dir) CASE_DIR="${2:-}"; shift 2 ;;
        --timeout)  TIMEOUT_S="${2:-}"; shift 2 ;;
        --solver)   SOLVER="${2:-}"; shift 2 ;;
        --foam-bashrc) FOAM_BASHRC="${2:-}"; shift 2 ;;
        --emit)     DO_EMIT=1; shift ;;
        --level)    EMIT_LEVEL="${2:-}"; shift 2 ;;
        --us)       EMIT_US="${2:-}"; shift 2 ;;
        --inert)    EMIT_INERT=1; shift ;;
        --endtime)  ENDTIME="${2:-}"; shift 2 ;;
        --no-detach) DETACH=0; shift ;;
        *) usage ;;
    esac
done
[ -n "$CASE_DIR" ] && [ -n "$TIMEOUT_S" ] || usage
case "$TIMEOUT_S" in ''|*[!0-9]*) echo "REFUSE: --timeout must be integer seconds" >&2; exit 2;; esac
[ -n "$ENDTIME" ] && case "$ENDTIME" in ''|*[!0-9]*) echo "REFUSE: --endtime must be an integer" >&2; exit 2;; esac

# --- emit the case first if asked (delegates to build_prd.py; launches nothing)
if [ "$DO_EMIT" = "1" ]; then
    [ -f "$BUILD" ] || { echo "REFUSE: no build_prd.py at $BUILD" >&2; exit 2; }
    INERT_FLAG=""; [ "$EMIT_INERT" = "1" ] && INERT_FLAG="--inert"
    python3 "$BUILD" --emit "$CASE_DIR" --level "$EMIT_LEVEL" --us "$EMIT_US" $INERT_FLAG \
        || { echo "REFUSE: build_prd.py --emit failed" >&2; exit 2; }
fi

[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
CASE_DIR="$(cd "$CASE_DIR" && pwd)"
CASE="$(basename "$CASE_DIR")"
# STATUS lives INSIDE the case dir -- mark_done_prd.py reads it at
# root/<case>/STATUS.<case> (mark_done_prd.py read_status: os.path.join(root,
# case, "STATUS.<case>")).  Writing it beside the case dir (the T13 run-root
# convention) leaves the completion instrument unable to find it (measured in
# the §2bb smoke: mark_done_prd REFUSED "no STATUS" until STATUS was moved
# inside the case dir; then DONE).
STATUS="$CASE_DIR/STATUS.$CASE"

# --- a completed run's record is never overwritten ---------------------------
[ -e "$STATUS" ] && { echo "REFUSE: $STATUS exists -- a completed run's record is never overwritten; nothing ran, nothing written" >&2; exit 2; }

# --- endTime rewrite for a short smoke (run input, not measurement logic) -----
if [ -n "$ENDTIME" ]; then
    CD="$CASE_DIR/system/controlDict"
    [ -f "$CD" ] || { echo "REFUSE: no system/controlDict to set --endtime" >&2; exit 2; }
    # set endTime and writeInterval to ENDTIME so fields are written AT endTime
    sed -i -E "s/^(endTime[[:space:]]+)[0-9]+/\1$ENDTIME/; s/^(writeInterval[[:space:]]+)[0-9]+/\1$ENDTIME/" "$CD"
fi

# --- detach ONCE by re-executing this file in a new session ------------------
if [ "$DETACH" = "1" ] && [ "${PRD_DETACHED:-}" != "1" ]; then
    EXTRA=""; [ -n "$ENDTIME" ] && EXTRA="--endtime $ENDTIME"
    PRD_DETACHED=1 exec setsid "$0" --case-dir "$CASE_DIR" --timeout "$TIMEOUT_S" \
        --solver "$SOLVER" --foam-bashrc "$FOAM_BASHRC" $EXTRA \
        --no-detach </dev/null >>"$CASE_DIR/log.launch" 2>&1 &
    echo "launched $CASE detached; STATUS will appear at $STATUS"
    exit 0
fi

write_status() {   # rc wall blockmesh_rc toposet_rc checkmesh_rc capped note
    tmp="$STATUS.tmp.$$"
    {
      echo "case=$CASE"
      echo "rc=$1"
      echo "wall_s=$2"
      echo "ranks=$RANKS"
      echo "core_min=$(awk -v w="$2" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')"
      echo "cap_core_min=$(awk -v t="$TIMEOUT_S" -v r="$RANKS" 'BEGIN{printf "%.3f", t*r/60.0}')"
      echo "timeout_s=$TIMEOUT_S"
      echo "capped=$6"
      echo "blockmesh_rc=$3"
      echo "toposet_rc=$4"
      echo "checkmesh_rc=$5"
      echo "solver=$SOLVER"
      echo "solver_path=${SOLVER_PATH:-unresolved}"
      echo "note=$7"
      echo "started_utc=$(date -u -d "@$T0" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo NA)"
      echo "ended_utc=$(date -u -d "@$T1" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo NA)"
    } > "$tmp"
    mv -f "$tmp" "$STATUS"
}

cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

# --- 0. the solver must be reachable -----------------------------------------
if [ "$FOAM_BASHRC" != "none" ]; then
    [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
    set +u
    # shellcheck disable=SC1090
    . "$FOAM_BASHRC" >/dev/null 2>&1 || true
    set -u
fi
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' NOT RESOLVABLE after sourcing $FOAM_BASHRC; nothing ran, no STATUS" >&2; exit 2; }
command -v blockMesh >/dev/null 2>&1 || { echo "REFUSE: blockMesh NOT RESOLVABLE; nothing ran, no STATUS" >&2; exit 2; }
command -v topoSet   >/dev/null 2>&1 || { echo "REFUSE: topoSet NOT RESOLVABLE; nothing ran, no STATUS" >&2; exit 2; }

# --- 1. LAUNCH GUARD: no 0/, no numeric time dir, 0.orig present + field set --
[ -e "$CASE_DIR/0" ] && { echo "REFUSE: $CASE already has a 0/ directory (age guard could not be trusted)" >&2; exit 2; }
while IFS= read -r d; do
    [ -n "$d" ] && { echo "REFUSE: $CASE already has time directory $(basename "$d")" >&2; exit 2; }
done < <(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?' 2>/dev/null)
[ -d "$CASE_DIR/0.orig" ] || { echo "REFUSE: $CASE has no 0.orig to arm from -- run build_prd.py --emit" >&2; exit 2; }
for f in U p k omega nut; do
    [ -f "$CASE_DIR/0.orig/$f" ] || { echo "REFUSE: 0.orig/$f missing -- the incompressible field set is incomplete" >&2; exit 2; }
done

# --- foreign-process guard (lineage-aware; T10aR2 AMENDMENT 1 pattern) --------
ppid_of() { sed 's/.*) //' "/proc/$1/stat" 2>/dev/null | awk '{print $2}'; }
LINEAGE=" $$ "; a="$PPID"
while [ -n "$a" ] && [ "$a" != "0" ] && [ "$a" != "1" ]; do LINEAGE="$LINEAGE$a "; a="$(ppid_of "$a")"; done
own_lineage() {
    case "$LINEAGE" in *" $1 "*) return 0;; esac
    a="$1"
    while [ -n "$a" ] && [ "$a" != "0" ] && [ "$a" != "1" ]; do
        [ "$a" = "$$" ] && return 0
        a="$(ppid_of "$a")"
    done
    return 1
}
for p in /proc/[0-9]*; do
    q="${p#/proc/}"
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CASE_DIR" ] || continue
    own_lineage "$q" && continue
    echo "REFUSE: pid $q already running in $CASE (foreign process)" >&2; exit 2
done

# --- 2. blockMesh (mesh must exist before topoSet) ---------------------------
T0=$(date +%s)
blockMesh -case "$CASE_DIR" > "$CASE_DIR/log.blockMesh" 2>&1
BM_RC=$?
if [ "$BM_RC" != "0" ]; then
    T1=$(date +%s); write_status "$BM_RC" "$((T1-T0))" "$BM_RC" NA NA no "blockMesh_failed"
    echo "$CASE: blockMesh FAILED rc=$BM_RC -> $STATUS" >&2; exit "$BM_RC"
fi

# --- 3. topoSet: porous cellZone + inletPlane/outletPlane faceZones ----------
topoSet -case "$CASE_DIR" > "$CASE_DIR/log.topoSet" 2>&1
TS_RC=$?
if [ "$TS_RC" != "0" ]; then
    T1=$(date +%s); write_status "$TS_RC" "$((T1-T0))" "$BM_RC" "$TS_RC" NA no "topoSet_failed"
    echo "$CASE: topoSet FAILED rc=$TS_RC -> $STATUS" >&2; exit "$TS_RC"
fi

# --- 4. checkMesh, recorded (infrastructure; not a gate here) ----------------
checkMesh -case "$CASE_DIR" > "$CASE_DIR/log.checkMesh" 2>&1
CM_RC=$?

# --- 5. arm 0/ from 0.orig; 0/U touched LAST (the age-guard datum) -----------
cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/ from 0.orig" >&2; exit 2; }
sleep 1
touch "$CASE_DIR/0/U" || { echo "REFUSE: could not touch 0/U" >&2; exit 2; }

# --- 6. the solver, FOREGROUND, rc captured from IT (never from setsid) -------
timeout --signal=TERM --kill-after=60 "$TIMEOUT_S" "$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.simpleFoam" 2>&1
RC=$?
T1=$(date +%s)
WALL=$((T1 - T0))
if [ "$WALL" -ge "$TIMEOUT_S" ]; then CAPPED=yes; else CAPPED=no; fi
NOTE=clean
if [ "$RC" = "124" ]; then NOTE=CAP_EXPIRED_or_child_exit_124
elif [ "$RC" -gt 128 ] 2>/dev/null; then NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then NOTE=SOLVER_NONZERO_EXIT
fi
write_status "$RC" "$WALL" "$BM_RC" "$TS_RC" "$CM_RC" "$CAPPED" "$NOTE"
echo "$CASE finished: rc=$RC wall=${WALL}s capped=$CAPPED note=$NOTE  ->  $STATUS"
# EXIT WITH THE SOLVER'S OWN rc, NEVER 0.
exit "$RC"
