#!/usr/bin/env bash
# ==========================================================================
# T21 CASE LAUNCHER -- chtMultiRegionSimpleFoam, two SOLID regions, serial.
#
# REGISTERED BY docs/campaigns/T-family/T21_PREREGISTRATION.md S6 (rule 4
# completion, in its steady form) and S7.4 (the contended-run disclosure).
# It is pinned by sha256 in that document's AMENDMENT 3.
#
# WHAT THIS FILE IS FOR, clause by clause, each traceable to a registered line:
#
#  * rc IS CAPTURED INSIDE THE DETACHED WRAPPER (S6 conjunct 1).  The solver
#    runs in THIS shell's foreground and `$?` is read on the very next line.
#    `setsid timeout cmd` exits 0 for EVERY outcome, so an rc captured around a
#    setsid line is not the solver's rc.  Detachment happens ONCE, by this file
#    re-executing itself with --no-detach; the inner copy is the one that
#    measures.
#
#  * START.<case> IS WRITTEN BEFORE THE SOLVER STARTS (S7.4).  It carries
#    start_utc, all three /proc/loadavg windows, procs_running, nproc and free
#    memory.  S7.4 registers the admissibility threshold ONE-WAY and IN ADVANCE:
#    load1 < 0.5*nproc (= 8.0 on this box, nproc 16).  Above it the row is A
#    COST AND NOT A CALIBRATION ROW -- the launcher writes that verdict into
#    START and STATUS as `calibration_admissible=no`, at the point of
#    measurement, so it is disclosed rather than argued about afterwards.
#
#  * 0/ IS ARMED FROM 0.orig/ WITH 0/housing/T TOUCHED LAST (S6 conjunct 6).
#    The comparator dates the whole run against 0/housing/T
#    (analyse_t21.py:421).  Touching it last is what makes the age guard mean
#    anything: every endTime field must be NEWER than it.
#
#  * NO CAP-DERIVED `timeout` THAT KILLS.  Sanaa, 2026-09-12 ~01:00Z, her own
#    words via the chief: "dont forget i dont want any cap on any run".  The
#    registered CAP (S7.2, 20.0 core-min over the set) stays as a PREDICTION
#    and a calibration input: STATUS records point_core_min, set_cap_core_min
#    and cap_exceeded as DISCLOSURE.  Nothing is killed.  This is safe here and
#    would not be everywhere: every T21 case has a natural terminus at
#    endTime = 3000 with NO residualControl (S6.1), so the run ends on its own.
#
#  * A PRE-FLIGHT REFUSAL WRITES NO STATUS.  Nothing ran, so there is no rc,
#    and inventing one is back-dating.
#
#  * AN EXISTING STATUS.<case> IS REFUSED.  A finished run's record is never
#    overwritten.
#
#  * STATUS.<case> AND START.<case> LIVE INSIDE THE CASE DIRECTORY, not beside
#    it.  That is not a preference: the frozen comparator reads
#    os.path.join(case_dir, "STATUS."+basename) at analyse_t21.py:370.
#
#  * THE BALANCE INSTRUMENT IS A POST-HOC postProcess PASS (S5.2a), run AFTER
#    STATUS is written, into its own log and its own POSTPROCESS.<case> record.
#    It can therefore never alter the solve's rc.  Its failure is a FINDING.
#
# usage: launch_t21.sh --case-dir DIR [--ranks 1] [--no-detach]
#                      [--solver chtMultiRegionSimpleFoam] [--foam-bashrc F]
#                      [--no-postprocess]
# ==========================================================================
set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() { sed -n '/^# usage:/,/^# ====/p' "$0" >&2; exit 2; }

CASE_DIR=""; RANKS=1; DETACH=1; POSTPROC=1
SOLVER="chtMultiRegionSimpleFoam"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
while [ $# -gt 0 ]; do
    case "$1" in
        --case-dir) CASE_DIR="${2:-}"; shift 2 ;;
        --ranks)    RANKS="${2:-}"; shift 2 ;;
        --solver)   SOLVER="${2:-}"; shift 2 ;;
        --foam-bashrc) FOAM_BASHRC="${2:-}"; shift 2 ;;
        --no-detach) DETACH=0; shift ;;
        --no-postprocess) POSTPROC=0; shift ;;
        *) usage ;;
    esac
done
[ -n "$CASE_DIR" ] || usage
[ -d "$CASE_DIR" ] || { echo "REFUSE: no case directory $CASE_DIR" >&2; exit 2; }
[ "$RANKS" = "1" ] || { echo "REFUSE: T21 is registered SERIAL, ranks 1 on every case (S8.4); --ranks=$RANKS" >&2; exit 2; }

CASE_DIR="$(cd "$CASE_DIR" && pwd)"
CASE="$(basename "$CASE_DIR")"
STATUS="$CASE_DIR/STATUS.$CASE"
START="$CASE_DIR/START.$CASE"

# --- the registered run set and its registered POINT costs (S8.1, S8.4) -----
# core-min per case; ranks 1; endTime 3000 every case.  PREDICTIONS, not caps.
case "$CASE" in
    T21_CYL_c)     POINT_CM=0.3006 ;;
    T21_CYL_m)     POINT_CM=0.6523 ;;
    T21_CYL_f)     POINT_CM=2.0593 ;;
    T21_CYL_W1)    POINT_CM=2.0593 ;;
    T21_CYL_P1000) POINT_CM=2.0593 ;;
    T21_CYL_S10)   POINT_CM=2.0593 ;;
    *) echo "REFUSE: '$CASE' is not one of the six registered T21 cases (S8.1); nothing ran, nothing written" >&2; exit 2 ;;
esac
SET_CAP_CM=20.0            # S7.2, the whole set, HARD as a prediction
END_TIME_REG=3000          # S8.1

# --- a finished run's record is never overwritten ---------------------------
[ -e "$STATUS" ] && { echo "REFUSE: $STATUS exists -- a finished run's record is never overwritten; nothing ran, nothing written" >&2; exit 2; }

# --- detach ONCE by re-executing this file in a new session ------------------
if [ "$DETACH" = "1" ] && [ "${T21_DETACHED:-}" != "1" ]; then
    PPFLAG=""; [ "$POSTPROC" = "0" ] && PPFLAG="--no-postprocess"
    T21_DETACHED=1 exec setsid "$0" --case-dir "$CASE_DIR" --ranks "$RANKS" \
        --solver "$SOLVER" --foam-bashrc "$FOAM_BASHRC" $PPFLAG \
        --no-detach </dev/null >>"$CASE_DIR/log.launch" 2>&1 &
    echo "launched $CASE detached; START at $START, STATUS will appear at $STATUS"
    exit 0
fi
# ---- FROM HERE DOWN WE ARE INSIDE THE DETACHED WRAPPER.  rc is measured here.

write_status() {   # rc wall checkmesh_rc note
    tmp="$STATUS.tmp.$$"
    CM=$(awk -v w="$2" -v r="$RANKS" 'BEGIN{printf "%.4f", w*r/60.0}')
    OVER=$(awk -v a="$CM" -v b="$SET_CAP_CM" 'BEGIN{print (a>b)?"yes":"no"}')
    {
      echo "case=$CASE"
      echo "rc=$1"
      echo "wall_s=$2"
      echo "ranks=$RANKS"
      echo "core_min=$CM"
      echo "point_core_min=$POINT_CM"
      echo "set_cap_core_min=$SET_CAP_CM"
      echo "cap_exceeded=$OVER"
      echo "cap_enforcement=none  # Sanaa 2026-09-12 ~01:00Z: no cap on any run. Terminus is endTime=$END_TIME_REG, no residualControl (S6.1)."
      echo "checkmesh_rc=$3"
      echo "solver=$SOLVER"
      echo "solver_path=${SOLVER_PATH:-unresolved}"
      echo "endTime_registered=$END_TIME_REG"
      echo "note=$4"
      echo "loadavg_at_launch=$LOAD_AT_LAUNCH"
      echo "load1_at_launch=$LOAD1"
      echo "procs_running_at_launch=$PROCS_RUN"
      echo "nproc=$NPROC"
      echo "calibration_admissible=$CAL_OK  # S7.4 [REGISTERED]: load1 < 0.5*nproc = $CAL_THRESH"
      echo "mem_available_gib_at_launch=$MEM_AVAIL"
      echo "started_utc=$(date -u -d "@$T0" +%Y-%m-%dT%H:%M:%SZ)"
      echo "ended_utc=$(date -u -d "@$T1" +%Y-%m-%dT%H:%M:%SZ)"
    } > "$tmp"
    mv -f "$tmp" "$STATUS"
}

cd "$CASE_DIR" || { echo "REFUSE: cannot enter $CASE_DIR" >&2; exit 2; }

# --- 0. the solver must be reachable ---------------------------------------
if [ "$FOAM_BASHRC" != "none" ]; then
    [ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
    set +u
    # shellcheck disable=SC1090
    . "$FOAM_BASHRC" >/dev/null 2>&1 || true
    set -u
fi
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' is NOT RESOLVABLE after sourcing ${FOAM_BASHRC}. Nothing ran, no STATUS written." >&2; exit 2; }

# --- 1. the launch guard: no 0/, no time directory, 0.orig and mesh present --
[ -e "$CASE_DIR/0" ] && { echo "REFUSE: $CASE already has a 0/ directory -- the age guard could not be evaluated. If this is splitMeshRegions scaffolding, run 'build_t21.py --postsplit $CASE' (T-8); this launcher moves NOTHING." >&2; exit 2; }
while IFS= read -r d; do
    [ -n "$d" ] && { echo "REFUSE: $CASE already has time directory $(basename "$d") -- a run is never started over an answer" >&2; exit 2; }
done < <(find "$CASE_DIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?' 2>/dev/null)
[ -d "$CASE_DIR/0.orig" ] || { echo "REFUSE: $CASE has no 0.orig to arm from" >&2; exit 2; }
for r in core housing; do
    [ -f "$CASE_DIR/constant/$r/polyMesh/owner" ] || { echo "REFUSE: $CASE region '$r' has no mesh (constant/$r/polyMesh/owner) -- blockMesh + splitMeshRegions have not run" >&2; exit 2; }
    for f in T p; do
        [ -f "$CASE_DIR/0.orig/$r/$f" ] || { echo "REFUSE: 0.orig/$r/$f missing -- the registered field set (S6 conjunct 4) is incomplete" >&2; exit 2; }
    done
    [ -f "$CASE_DIR/constant/$r/thermophysicalProperties" ] || { echo "REFUSE: constant/$r/thermophysicalProperties missing -- --physics has not run" >&2; exit 2; }
done
[ -f "$CASE_DIR/constant/g" ] || { echo "REFUSE: constant/g missing -- MANDATORY at file scope even with zero fluid regions (S6.2); the solver would fatal" >&2; exit 2; }
[ -f "$CASE_DIR/constant/regionProperties" ] || { echo "REFUSE: constant/regionProperties missing" >&2; exit 2; }
[ -f "$CASE_DIR/system/fvSolution" ] || { echo "REFUSE: top-level system/fvSolution missing -- MANDATORY (Amendment 1 A1.2)" >&2; exit 2; }
[ -f "$CASE_DIR/constant/core/fvOptions" ] || { echo "REFUSE: constant/core/fvOptions missing -- absent in constant AND system is a SILENT ZERO SOURCE (S3)" >&2; exit 2; }
grep -q 'residualControl' "$CASE_DIR"/system/*/fvSolution 2>/dev/null && { echo "REFUSE: a residualControl block is present -- FORBIDDEN by S6.1; this family was killed by it (T19)" >&2; exit 2; }
EREG=$(sed -n 's/^[[:space:]]*endTime[[:space:]]\+\([0-9]\+\)[[:space:]]*;.*/\1/p' "$CASE_DIR/system/controlDict" | head -1)
[ "$EREG" = "$END_TIME_REG" ] || { echo "REFUSE: controlDict endTime='$EREG', registered $END_TIME_REG (S8.1)" >&2; exit 2; }

# foreign process already in the case directory (this shell's lineage excluded)
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
    echo "REFUSE: pid $q is already running in $CASE" >&2; exit 2
done

# --- 2. checkMesh, all regions, recorded rather than assumed (infrastructure) -
checkMesh -case "$CASE_DIR" -allRegions -allTopology -allGeometry \
    > "$CASE_DIR/log.checkMesh.allregions.prelaunch" 2>&1
CHECKMESH_RC=$?

# --- 3. THE CONTENTION DISCLOSURE, WRITTEN BEFORE THE SOLVER (S7.4) ---------
NPROC=$(nproc)
LOAD_AT_LAUNCH="$(cut -d' ' -f1-3 /proc/loadavg)"
LOAD1="$(cut -d' ' -f1 /proc/loadavg)"
PROCS_RUN="$(cut -d' ' -f4 /proc/loadavg)"
MEM_AVAIL="$(awk '/MemAvailable/{printf "%.2f", $2/1048576}' /proc/meminfo)"
CAL_THRESH=$(awk -v n="$NPROC" 'BEGIN{printf "%.1f", 0.5*n}')
CAL_OK=$(awk -v l="$LOAD1" -v t="$CAL_THRESH" 'BEGIN{print (l<t)?"yes":"no"}')
{
  echo "case=$CASE"
  echo "start_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "loadavg_at_launch=$LOAD_AT_LAUNCH"
  echo "load1_at_launch=$LOAD1"
  echo "procs_running_at_launch=$PROCS_RUN"
  echo "nproc=$NPROC"
  echo "calibration_threshold=$CAL_THRESH  # S7.4 [REGISTERED] 0.5*nproc, one-way, registered in advance"
  echo "calibration_admissible=$CAL_OK"
  echo "mem_available_gib_at_launch=$MEM_AVAIL"
  echo "ranks=$RANKS"
  echo "point_core_min=$POINT_CM"
  echo "set_cap_core_min=$SET_CAP_CM"
  echo "cap_enforcement=none  # Sanaa 2026-09-12 ~01:00Z, no cap on any run"
  echo "solver_path=$SOLVER_PATH"
  echo "checkmesh_rc=$CHECKMESH_RC"
} > "$START"
if [ "$CAL_OK" = "no" ]; then
    echo "DISCLOSED AT THE POINT OF MEASUREMENT (S7.4): load1=$LOAD1 >= $CAL_THRESH. This row is A COST AND NOT A CALIBRATION ROW. The rung still runs and still grades; the calibration row is owed and unpaid."
fi

# --- 4. arm 0/ from 0.orig; 0/housing/T touched LAST (the age-guard datum) ---
cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0" || { echo "REFUSE: could not create 0/ from 0.orig" >&2; exit 2; }
sleep 1
touch "$CASE_DIR/0/core/T" "$CASE_DIR/0/core/p" "$CASE_DIR/0/housing/p" || { echo "REFUSE: could not touch the armed 0/ fields" >&2; exit 2; }
sleep 1
touch "$CASE_DIR/0/housing/T" || { echo "REFUSE: could not touch 0/housing/T" >&2; exit 2; }

# --- 5. THE SOLVER, IN THIS SHELL'S FOREGROUND.  NO timeout.  rc read next line
T0=$(date +%s)
"$SOLVER_PATH" -case "$CASE_DIR" > "$CASE_DIR/log.solve" 2>&1
RC=$?
T1=$(date +%s)
WALL=$((T1 - T0))
NOTE=clean
if [ "$RC" -gt 128 ] 2>/dev/null; then NOTE="KILLED_BY_SIGNAL_$((RC - 128))"
elif [ "$RC" != "0" ]; then NOTE=SOLVER_NONZERO_EXIT
fi
write_status "$RC" "$WALL" "$CHECKMESH_RC" "$NOTE"
echo "$CASE finished: rc=$RC wall=${WALL}s core_min=$(awk -v w="$WALL" -v r="$RANKS" 'BEGIN{printf "%.4f", w*r/60.0}') note=$NOTE  ->  $STATUS"

# --- 6. THE BALANCE INSTRUMENT: a POST-HOC postProcess pass (S5.2a) ---------
# After STATUS.  Its rc is recorded separately and can never alter the solve's.
if [ "$POSTPROC" = "1" ] && [ "$RC" = "0" ]; then
    postProcess -case "$CASE_DIR" -region housing -func wallHeatFlux -latestTime \
        > "$CASE_DIR/log.postProcess.wallHeatFlux" 2>&1
    PPRC=$?
    {
      echo "case=$CASE"
      echo "pass=wallHeatFlux (post-hoc postProcess, S5.2a -- NOT an inline function object)"
      echo "region=housing"
      echo "rc=$PPRC"
      echo "log=log.postProcess.wallHeatFlux"
      echo "dat_expected=postProcessing/wallHeatFlux/<t>/wallHeatFlux.dat"
      echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      echo "note=a NON-ZERO rc here is a FINDING, not a silent skip; the solve's rc is unaffected"
    } > "$CASE_DIR/POSTPROCESS.$CASE"
    echo "postProcess wallHeatFlux: rc=$PPRC -> $CASE_DIR/POSTPROCESS.$CASE"
fi

exit "$RC"
