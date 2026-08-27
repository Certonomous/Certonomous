#!/usr/bin/env bash
# F27 -- LAUNCHER for pulsatile Womersley flow in a CIRCULAR PIPE on a GENUINE
# 3-D BUTTERFLY (O-GRID) MESH (pimpleFoam, PISO, laminar, cosine body force,
# alpha = 4; ladder nc/nr/nz = 8/8/12, 16/16/24, 32/32/48 = 3,840 / 30,720 /
# 245,760 cells, refined by exactly 2 in ALL THREE directions, FOUR RANKS at
# every level).  Lineage: cases/F25_DUCT3D/run_f25.sh (the cfd registration
# standard) -- WITH ITS PRE-SPEND PROJECTOR REPLACED, see below.
#
# FIRES NOTHING WITHOUT --prereg-commit.  `--preflight` runs every guard and
# every path resolution AND STOPS at zero compute, INCLUDING refusing to run
# blockMesh -- a gate a mesher grades is FIRED the moment the mesher runs.
#
# `set -e` DOES NOT GATE IN THIS HARNESS.  Every assertion carries an explicit
# `|| { echo ABORT ...; exit 1; }`.  `set -u` is DROPPED around the OpenFOAM
# bashrc source only (L-339: the bashrc reads an unbound WM_PROJECT_DIR at its
# line 184 and would kill this shell silently).
#
# L-343: USER is EXPORTED from LOGNAME/id -un BEFORE the bashrc is sourced -- a
# cron-started queue runner carries no USER, the bashrc then resolves
# WM_PROJECT_USER_DIR to the literal `user`, and every user-built library
# vanishes from the launched solver's path.  Preflight PROVES the solver still
# resolves in a USER-less environment by running `env -u USER` against it.
#
# NO `rm -rf`, NO `rmtree`, ON A CASE DIRECTORY, ANYWHERE IN THIS FILE.  A
# pre-existing `0/`, numeric time directory or processor* directory in the RUN
# ROOT or in a LEVEL directory is REFUSED, never deleted (here and again inside
# build_f27.py).  The RUN ROOT existing at all is exit 3.
#
# THE PRE-SPEND PROJECTOR IS proj_f27.py, NOT THE F23/F24/F25 FORM.  That form
# multiplies a frozen constant by `max(1, ranks / max(free_cores, 0.5))`, which
# pins at 8.0x for a 4-rank entry on a busy box; F24 halted at exit 3 before its
# fine level because of it, against a measured contention effect of 1.86x
# (cfd-supervisor, verified personally, 2026-08-27).  Here the FIRST level is
# projected from a rate MEASURED on this case, and every LATER level from THIS
# RUN's own completed levels; there is NO contention multiplier, because the
# frozen rates were themselves measured under load 19.66 on 16 cores.  The halt
# path is driven in both directions by `proj_f27.py --selftest` on INJECTED
# numbers -- it never reads the box.
#
# THE POST-LEVEL CHECK ON ACTUAL SPEND IS UNCHANGED: ClockTime x ranks / 60,
# summed, HALT at exit 3 on a crossing, cap never raised (rule 12).
#
# L-342: RC.txt, box probes, MESH_LINE.txt and STATUS.* are written by THIS
# shell, in the same process that ran the solver, never by an attached poller.
set -u
set -o pipefail

ROOT="/home/ubuntu/Certonomous/cases/F27_WOMERSLEY_PIPE"
CASE_SRC="$ROOT/case"
EXACT="$ROOT/exact_f27.py"
BUILD="$ROOT/build_f27.py"
GRADER="$ROOT/grade_f27.py"
PROJ_MOD="$ROOT/proj_f27.py"
FIO="$ROOT/foam_io_f27.py"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/F27_WOMERSLEY_PIPE_runs"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
STATUS="$ROOT/STATUS.F27_WOMERSLEY_PIPE"

CAP_CORE_MIN=680            # must equal grade_f27.py::CAP_CORE_MIN and the pre-registration
END_TIME=5.25               # 5 T + T/4; must equal controlDict.template endTime and exact_f27.T_END

# name  nc  nr  nz  steps  ranks   (ranks must equal exact_f27.RANKS and decomposeParDict numberOfSubdomains)
LEVELS=("coarse 8 8 12 672 4" "medium 16 16 24 1344 4" "fine 32 32 48 2688 4")
DECOMP_METHOD="simple n (1 1 4), 4 subdomains, AXIAL bands; the butterfly cross-section is never cut"
DECOMP_SEED="none (simple geometric decomposition from system/decomposeParDict; deterministic; no RNG)"

PREREG_COMMIT=""
PREFLIGHT=0
DETACH=0
SELFTEST_PROJ=0
for a in "$@"; do
  case "$a" in
    --preflight) PREFLIGHT=1 ;;
    --detach) DETACH=1 ;;
    --selftest-projector) SELFTEST_PROJ=1 ;;
    --prereg-commit=*) PREREG_COMMIT="${a#*=}" ;;
    *) echo "ABORT: unknown argument $a"; exit 1 ;;
  esac
done
say() { printf '%s\n' "$*"; }

# THE STATUS FILE.  Written by an EXIT TRAP so the rc it records is THIS
# script's own, captured INSIDE the process that produced it -- never around a
# `setsid` line, which returns 0 for every outcome of its child.  When the queue
# runner launches this script it writes its own STATUS line after the argv
# returns, superseding this one with the identical meaning.
write_status() {
  local R=$1
  printf 'launcher_rc=%s end=%s note=exit-status-of-run_f27.sh-NOT-the-solver-rc cap_core_min=%s spent_core_min=%s\n' \
    "$R" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$CAP_CORE_MIN" "${SPENT:-0}" > "$STATUS"
}
on_exit() { local R=$?; write_status "$R"; }
SPENT=0
trap on_exit EXIT

if [ "$SELFTEST_PROJ" = "1" ]; then
  python3 "$PROJ_MOD" --selftest
  exit $?
fi

probe_box() {   # $1 = label, $2 = destination file.  INFRASTRUCTURE ONLY (L-342):
                # this reading is RECORDED and enters NO arithmetic.  See proj_f27.py.
  local L1 MEMKB NP FREE
  L1=$(awk '{print $1}' /proc/loadavg)
  MEMKB=$(awk '/^MemAvailable/{print $2}' /proc/meminfo)
  NP=$(nproc)
  FREE=$(python3 -c "print(max(0.5, $NP - $L1))")
  printf 'label=%s\nload1=%s\nnproc=%s\nfree_cores=%s\nMemAvailable_kB=%s\nutc=%s\nnote=%s\n' \
    "$1" "$L1" "$NP" "$FREE" "$MEMKB" "$(date -u +%FT%TZ)" \
    "INFRASTRUCTURE observation only: the pre-spend projector does NOT read it" > "$2"
}

# REFUSE, NEVER DELETE: a `0/`, numeric time or processor* directory as a direct child of $1.
refuse_if_answered() {
  local D="$1"
  if [ -e "$D/0" ]; then
    echo "ABORT: $D/0 already exists. Standing rule 4's age guard dates every"
    echo "       endTime field against this case's own 0/U, and a pre-existing 0/"
    echo "       destroys that. REFUSED, not deleted."
    exit 1
  fi
  while IFS= read -r d; do
    echo "ABORT: $D already holds $(basename "$d"). REFUSED, not deleted."; exit 1
  done < <(find "$D" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/([0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?|processor[0-9]+)' 2>/dev/null)
}

# --------------------------------------------------------------------------
# PATH RESOLUTION against the disk IN THIS INVOCATION
# --------------------------------------------------------------------------
for p in "$CASE_SRC" "$CASE_SRC/0" "$CASE_SRC/constant" "$CASE_SRC/system"; do
  [ -d "$p" ] || { echo "ABORT: required directory does not exist: $p"; exit 1; }
done
for f in "$CASE_SRC/0/U.template" "$CASE_SRC/0/p.template" \
         "$CASE_SRC/constant/transportProperties" "$CASE_SRC/constant/turbulenceProperties" \
         "$CASE_SRC/constant/fvOptions" \
         "$CASE_SRC/system/fvSchemes" "$CASE_SRC/system/fvSolution" "$CASE_SRC/system/decomposeParDict" \
         "$CASE_SRC/system/blockMeshDict.template" "$CASE_SRC/system/controlDict.template" \
         "$EXACT" "$BUILD" "$GRADER" "$PROJ_MOD" "$FIO" "$FOAM_BASHRC"; do
  [ -f "$f" ] || { echo "ABORT: required file does not exist: $f"; exit 1; }
done
say "PATHS RESOLVED against disk in this invocation: 16 files, 4 directories."

# --------------------------------------------------------------------------
# THE INSTRUMENT MUST BE GREEN BEFORE ANY COMPUTE
# --------------------------------------------------------------------------
python3 "$EXACT" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: exact_f27.py --selftest did not pass; the Bessel closed form has not been shown to satisfy the equation the solver integrates and NOTHING may be launched against it"; exit 1; }
python3 "$GRADER" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: grade_f27.py --selftest did not pass; the grading path is not established"; exit 1; }
python3 -O "$GRADER" --selftest > /dev/null 2>&1
[ $? -eq 2 ] || { echo "ABORT: grade_f27.py did not exit 2 under python3 -O; the -O refusal is not armed"; exit 1; }
python3 "$PROJ_MOD" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: proj_f27.py --selftest did not pass; the pre-spend projector is not established and NOTHING may be launched behind it"; exit 1; }
python3 -O "$PROJ_MOD" --selftest > /dev/null 2>&1
[ $? -eq 2 ] || { echo "ABORT: proj_f27.py did not exit 2 under python3 -O"; exit 1; }
say "INSTRUMENT GREEN: exact_f27, grade_f27 and proj_f27 selftests pass; grade_f27 and proj_f27 exit 2 under -O."

CAP_GRADER=$(grep -E '^CAP_CORE_MIN' "$GRADER" | head -1 | sed -E 's/^CAP_CORE_MIN[[:space:]]*=[[:space:]]*([0-9.]+).*/\1/')
python3 -c "import sys; sys.exit(0 if abs(float('$CAP_GRADER') - $CAP_CORE_MIN) < 1e-9 else 1)" \
  || { echo "ABORT: launcher cap $CAP_CORE_MIN disagrees with grade_f27.py CAP_CORE_MIN $CAP_GRADER"; exit 1; }
say "CAP AGREES between launcher and grader: $CAP_CORE_MIN core-minutes."

python3 - "$CASE_SRC" "$END_TIME" "$CAP_CORE_MIN" <<'PY' \
  || { echo "ABORT: the dictionaries on disk disagree with exact_f27 (nu, drive, ranks, endTime, schemes, tolerances)"; exit 1; }
import re, sys, math
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F27_WOMERSLEY_PIPE")
import exact_f27 as EX
cs, end_time = sys.argv[1], float(sys.argv[2])
tp = open(cs + "/constant/transportProperties").read()
m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
if not m or abs(float(m.group(1)) - EX.NU) > 1e-15: sys.exit(1)
cd = open(cs + "/system/controlDict.template").read()
m = re.search(r"^\s*endTime\s+([0-9.]+)\s*;", cd, re.M)
if not (m and abs(float(m.group(1)) - end_time) < 1e-12 and abs(EX.T_END - end_time) < 1e-12): sys.exit(1)
if not re.search(r"adjustTimeStep\s+no\s*;", cd) or not re.search(r"application\s+pimpleFoam\s*;", cd): sys.exit(1)
mw = re.search(r"^\s*writeInterval\s+([0-9.]+)\s*;", cd, re.M)
wi = float(mw.group(1)) if mw else 0.0
if not wi or abs(EX.PERIOD/wi - round(EX.PERIOD/wi)) > 1e-12 or abs(EX.T_END/wi - round(EX.T_END/wi)) > 1e-12: sys.exit(1)
fo = open(cs + "/constant/fvOptions").read()
m = re.search(r"type\s+cosine\s*;\s*frequency\s+([0-9.eE+\-]+)\s*;\s*amplitude\s+([0-9.eE+\-]+)\s*;\s*scale\s+\(\s*0\s+0\s+1\s*\)", fo)
if not m or abs(float(m.group(1)) - EX.OMEGA/(2*math.pi)) > 1e-15 or abs(float(m.group(2)) - EX.A_DRIVE) > 1e-15: sys.exit(1)
fs = open(cs + "/system/fvSolution").read()
if not re.search(r"nNonOrthogonalCorrectors\s+1\s*;", fs) or not re.search(r"nOuterCorrectors\s+1\s*;", fs): sys.exit(1)
sch = open(cs + "/system/fvSchemes").read()
if not re.search(r"laplacianSchemes\s*\{\s*default\s+Gauss\s+linear\s+corrected\s*;", sch): sys.exit(1)
if not re.search(r"ddtSchemes\s*\{\s*default\s+backward\s*;", sch): sys.exit(1)
dp = open(cs + "/system/decomposeParDict").read()
m = re.search(r"numberOfSubdomains\s+([0-9]+)\s*;", dp)
if not (m and int(m.group(1)) == EX.RANKS == 4 and re.search(r"n\s+\(\s*1\s+1\s+4\s*\)", dp)): sys.exit(1)
sys.exit(0)
PY
say "nu, drive, endTime, writeInterval, BDF2, corrected Laplacian, PISO, non-orthogonal corrector AND ranks ON DISK AGREE with exact_f27."

# --------------------------------------------------------------------------
# L-343: THE SOLVER MUST RESOLVE IN A USER-LESS ENVIRONMENT
# --------------------------------------------------------------------------
USER_PROBE=$(env -u USER bash -c '. '"$FOAM_BASHRC"' >/dev/null 2>&1; printf "%s|%s|%s" "${USER:-UNSET}" "${FOAM_USER_LIBBIN:-UNSET}" "$(command -v pimpleFoam || echo NOTFOUND)"')
case "$USER_PROBE" in
  *NOTFOUND*) echo "ABORT (L-343): pimpleFoam does NOT resolve in a USER-less environment ($USER_PROBE). A cron-started queue runner carries no USER and this launch would die there. FAILING LOUDLY rather than launching."; exit 1 ;;
esac
say "L-343 PROBE: with USER unset, pimpleFoam still resolves. Probe reading: $USER_PROBE"

if [ "$PREFLIGHT" = "1" ]; then
  say ""
  say "PREFLIGHT ONLY -- ZERO COMPUTE. blockMesh was NOT run. build_f27.py was NOT called. decomposePar was NOT run."
  say "decomposition method: $DECOMP_METHOD"
  say "decomposition seed:   $DECOMP_SEED"
  say "pre-spend projector:  proj_f27.py (NOT the F23/F24/F25 max(free_cores, 0.5) form; no contention multiplier)"
  SP=0
  for L in "${LEVELS[@]}"; do
    set -- $L
    say "  level $1: nc $2, nr $3, nz $4 -> $(python3 -c "print(($2*$2+4*$2*$3)*$4)") cells, $5 steps (dt = $END_TIME/$5), ranks $6, target $RUN_ROOT/$1"
    say "    $(python3 "$PROJ_MOD" --level "$1" --spent "$SP" --cap "$CAP_CORE_MIN" --completed '[]' 2>&1 | head -1)"
    [ -e "$RUN_ROOT/$1/0" ] && say "    NOTE: $RUN_ROOT/$1/0 EXISTS -- a real launch would REFUSE here."
  done
  say "  CAP AGREES $CAP_CORE_MIN"
  if [ -e "$RUN_ROOT" ]; then
    say "  NOTE: run root $RUN_ROOT EXISTS -- a real launch REFUSES with exit 3."
  else
    say "  run root $RUN_ROOT is ABSENT at $(date -u +%FT%TZ) (rule-2 absence condition holds)."
  fi
  exit 0
fi

[ -n "$PREREG_COMMIT" ] \
  || { echo "ABORT: --prereg-commit=<sha> is required. Rule 2: the gate, threshold, cap and label are committed BEFORE the solver starts."; exit 1; }
git -C /home/ubuntu/Certonomous cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "ABORT: $PREREG_COMMIT is not a commit in this repository"; exit 1; }

# ---- THE RUN-ROOT GUARD. REFUSE (exit 3), NEVER DELETE. ---------------------
if [ -e "$RUN_ROOT" ]; then
  echo "REFUSED (exit 3): the run root $RUN_ROOT already exists."
  echo "  This rung's answer is produced ONCE. A second launch over an existing"
  echo "  run root would date its fields against somebody else's 0/U and would"
  echo "  overwrite an answer that may already be graded. REFUSED, not deleted."
  exit 3
fi

# ---- SELF-DETACH: rc captured INSIDE the wrapper, never around setsid --------
# `setsid timeout cmd` exits 0 for EVERY outcome of its child, so the rc is
# captured by the inner shell that actually ran the command and written to
# STATUS there.  This branch re-execs THIS script without --detach.
if [ "$DETACH" = "1" ]; then
  trap - EXIT
  ME="$ROOT/run_f27.sh"
  OUT="$ROOT/launcher.detached.out"
  nohup setsid bash -c "cd '$ROOT' && bash '$ME' --prereg-commit=$PREREG_COMMIT > '$OUT' 2>&1; R=\$?; printf 'launcher_rc=%s end=%s note=exit-status-of-run_f27.sh-NOT-the-solver-rc\n' \"\$R\" \"\$(date -u +%Y-%m-%dT%H:%M:%SZ)\" > '$STATUS'" \
    > /dev/null 2>&1 < /dev/null &
  say "DETACHED: pid $!, output $OUT, status $STATUS (rc captured INSIDE the wrapper)."
  exit 0
fi

# `-u` dropped around the source ONLY (L-339).  USER exported first (L-343).
export USER="${USER:-${LOGNAME:-$(id -un)}}"
set +u
# shellcheck disable=SC1090
. "$FOAM_BASHRC" || { echo "ABORT: could not source $FOAM_BASHRC"; exit 1; }
set -u
command -v pimpleFoam    > /dev/null || { echo "ABORT: pimpleFoam not on PATH after sourcing"; exit 1; }
command -v blockMesh     > /dev/null || { echo "ABORT: blockMesh not on PATH after sourcing"; exit 1; }
command -v decomposePar  > /dev/null || { echo "ABORT: decomposePar not on PATH after sourcing"; exit 1; }
command -v mpirun        > /dev/null || { echo "ABORT: mpirun not on PATH after sourcing"; exit 1; }
say "ENVIRONMENT: USER=$USER  id -un=$(id -un)  FOAM_USER_LIBBIN=${FOAM_USER_LIBBIN:-UNSET}  (INFRASTRUCTURE record, L-343)"

mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
SPENT=0
COMPLETED='[]'

for L in "${LEVELS[@]}"; do
  set -- $L
  NAME=$1; NC=$2; NR=$3; NZ=$4; NSTEP=$5; RANKS=$6
  CD="$RUN_ROOT/$NAME"
  CELLS=$(python3 -c "print(($NC*$NC+4*$NC*$NR)*$NZ)")
  CELLSTEPS=$(python3 -c "print(($NC*$NC+4*$NC*$NR)*$NZ*$NSTEP)")
  # ---- THE LEVEL GUARD. REFUSE, NEVER DELETE. ------------------------------
  [ -e "$CD" ] && refuse_if_answered "$CD"
  mkdir -p "$CD" || { echo "ABORT: cannot create $CD"; exit 1; }

  # ---- PROBE THIS BOX: RECORDED, NOT USED (L-342 infrastructure) ------------
  probe_box "$NAME-pre" "$CD/box_before.txt"

  # ---- PROJECT: proj_f27.py, from THIS RUN's own completed levels -----------
  PROJLINE=$(python3 "$PROJ_MOD" --level "$NAME" --spent "$SPENT" --cap "$CAP_CORE_MIN" --completed "$COMPLETED")
  PROJRC=$?
  say "level $NAME projection: $PROJLINE"
  if [ "$PROJRC" -eq 3 ]; then
    echo "HALT BEFORE SPENDING: level $NAME is PROJECTED to cross the registered"
    echo "      cap of $CAP_CORE_MIN core-min. The cap is NOT raised. Levels not"
    echo "      launched stay PENDING (CLAUDE.md rule 12)."
    exit 3
  fi
  [ "$PROJRC" -eq 0 ] || { echo "ABORT: proj_f27.py exited $PROJRC (a projector that cannot project is not a guard)"; exit 1; }

  # ---- BUILD: templating, blockMesh, checkMesh (gates), 0/C, 0/V, 0/p, 0/U LAST
  python3 "$BUILD" "$CD" --level "$NAME" > "$CD/log.build" 2>&1 \
    || { echo "ABORT: build_f27.py failed at level $NAME; see $CD/log.build"; exit 1; }
  [ -f "$CD/0/U" ] || { echo "ABORT: build did not leave $CD/0/U"; exit 1; }
  [ -f "$CD/MESH_LINE.txt" ] || { echo "ABORT: build did not leave $CD/MESH_LINE.txt"; exit 1; }
  say "level $NAME built: $(cat "$CD/MESH_LINE.txt")"

  # ---- DECOMPOSE (after 0/U: the serial 0/U remains the age guard's datum) ----
  say "level $NAME decomposition: $DECOMP_METHOD. Decomposition seed: $DECOMP_SEED"
  decomposePar -case "$CD" > "$CD/log.decomposePar" 2>&1 \
    || { echo "ABORT: decomposePar failed at level $NAME; see $CD/log.decomposePar"; exit 1; }
  NPROC=$(find "$CD" -maxdepth 1 -type d -name 'processor[0-9]*' | wc -l)
  [ "$NPROC" -eq "$RANKS" ] || { echo "ABORT: decomposePar left $NPROC processor directories, registered $RANKS"; exit 1; }

  say "level $NAME runs on $RANKS ranks: mpirun -np $RANKS pimpleFoam -parallel ($NSTEP fixed steps, $CELLS cells)"
  mpirun -np "$RANKS" pimpleFoam -parallel -case "$CD" > "$CD/log.pimpleFoam" 2>&1
  RC=$?
  echo "$RC" > "$CD/RC.txt"
  probe_box "$NAME-post" "$CD/box_after.txt"
  [ "$RC" -eq 0 ] || { echo "ABORT: pimpleFoam exited $RC at level $NAME (rc recorded in $CD/RC.txt). A crash is a FINDING until triage says otherwise; it is not retried here."; exit 1; }

  CLOCK=$(grep "ClockTime = " "$CD/log.pimpleFoam" | tail -1 | sed 's/.*ClockTime = \([0-9][0-9]*\) s.*/\1/')
  [ -n "$CLOCK" ] || { echo "ABORT: no ClockTime in $CD/log.pimpleFoam; the cap cannot be checked and an unchecked cap is not a cap"; exit 1; }
  SPENT=$(python3 -c "print($SPENT + $CLOCK * $RANKS / 60.0)")
  COMPLETED=$(python3 -c "
import json,sys
c=json.loads('''$COMPLETED''')
c.append(dict(name='$NAME', cell_steps=$CELLSTEPS, clock_s=float($CLOCK), ranks=$RANKS))
print(json.dumps(c))")
  say "level $NAME COMPLETE: ClockTime ${CLOCK}s x $RANKS ranks -> cumulative $SPENT core-min of $CAP_CORE_MIN"
  say "  MEASURED RATE at $NAME: $(python3 -c "print('%.3f core-us per cell-step' % ($CLOCK*$RANKS*1e6/$CELLSTEPS))") -- the NEXT level is projected from THIS."
  say "  QUANTISATION: ClockTime has INTEGER-SECOND resolution: +/- $(python3 -c "print(0.5*$RANKS/60.0)") core-min per level."
  python3 -c "import sys; sys.exit(0 if $SPENT <= $CAP_CORE_MIN else 1)" || {
    echo "HALT: THE REGISTERED CAP OF $CAP_CORE_MIN CORE-MINUTES HAS BEEN CROSSED"
    echo "      at level $NAME; cumulative spend $SPENT core-min."
    echo "      An overrun STOPS the run. It does not get a new budget"
    echo "      (CLAUDE.md rule 12). Levels not launched stay PENDING."
    exit 3
  }
done

say ""
say "ALL THREE LEVELS COMPLETE. Cumulative spend: $SPENT core-min of $CAP_CORE_MIN."
say "Grading is a SEPARATE invocation:"
say "  python3 $GRADER --prereg-commit=$PREREG_COMMIT"
