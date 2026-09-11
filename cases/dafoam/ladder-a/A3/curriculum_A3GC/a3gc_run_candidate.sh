#!/usr/bin/env bash
# =====================================================================
# a3gc_run.sh -- **DRAFT, NOT FROZEN.**  The A3GC PRODUCING path.
#
# Stages 3-4 of A3GC (PREREGISTRATION.md Sec.6): take one registered level
# from a3gc_genmesh.sh, configure it, cold-start it, and solve it detached,
# leaving a case directory the FROZEN comparator can grade.
#
#   *** DIRECTION OF FIT IS ABSOLUTE.  a3gc_grade.py IS FROZEN
#   (commit 367799db0fba3968b641b5989470988d593c959a, AMENDMENT 4,
#    md5 73dbe368934956700da87e5a1f44ea0c) AND THIS FILE CONFORMS TO IT.
#   The comparator is the SPECIFICATION.  If something here cannot satisfy
#   the contract, that is a FINDING for the dafoam-supervisor and an
#   amendment or a BLOCKED rung -- IT IS NEVER A REASON TO EDIT THE
#   GRADER.  It was frozen BEFORE this file existed, deliberately, so the
#   grader could not be shaped to whatever the solver happens to emit. ***
#
# SUBMISSIONS PARKED.  Nothing here sends anything anywhere.
#
# Usage:
#   a3gc_run.sh --level L3|L2|L1 --root <parent-dir> [--template <case>]
#               [--stage prepare|launch|all] [--dry-run]
#
#   prepare  writes system/, the runScript, and the cold `0` -- NO COMPUTE.
#   launch   starts the detached solve and captures its exit code.
#   all      prepare then launch.
# =====================================================================
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GRADE="$HERE/a3gc_grade.py"

refuse() { printf '\nREFUSE [%s]\n  %s\n  exit 2 -- the runner could not establish what it was asked to establish.\n' "$1" "$2" >&2; exit 2; }

# =====================================================================
# THE QUARANTINE (dafoam-supervisor ruling S-153, PREREGISTRATION.md
# AMENDMENT 3 `G-QUARANTINE`).  The feasibility mesh probe's meshes MAY
# NEVER BE PROMOTED INTO THE GRADED RUN.  If any A3GC level is ever graded
# on a probe-generated mesh then the probe WAS first compute retroactively
# and AMENDMENT 3 falls with it, and the freeze with it.
# THIS IS A HARD REFUSAL ON ANY PATH, NOT A COMMENT.
# =====================================================================
QUARANTINED='A3GC-meshgen-probe'
assert_not_quarantined() {
  local what="$1" p="$2"
  case "$p" in
    *"$QUARANTINED"*)
      refuse "QUARANTINE" "$what resolves inside the QUARANTINED feasibility probe:
    $p
  AMENDMENT 3 G-QUARANTINE: the probe's meshes may never be promoted into the
  graded run.  Sec.6 stage 1 regenerates the family under this item's own
  registered roots.  Grading a probe mesh would retroactively make the probe
  FIRST COMPUTE and void AMENDMENT 3." ;;
  esac
}

# =====================================================================
# REGISTERED VALUES.  EVERY ONE CITES THE SECTION THAT FIXES IT.
#
# *** READ THIS BEFORE "HELPFULLY" RESTORING A SHIPPED VALUE. ***
# The shipped producer /home/ubuntu/certonomous-runs/A3-onera-m6-transonic/
# DISAGREES WITH THIS ITEM ON THREE VALUES, and inheriting any of them
# would have produced three complete solves and had all three REFUSED at
# grading -- the entire 1,525 core-min spent to earn a refusal:
#
#   runScript.py:63        "primalMinResTol": 1.0e-6   <- RELAXED for the FD
#                          stage; its own comment says the validated primal
#                          ran separately at 1.0e-8.  G-TOL REFUSES anything
#                          but 1e-8 x 100.
#   system/controlDict:21  endTime 1500               <- the validated run
#                          used 6000.
#   system/decomposeParDict numberOfSubdomains 2      <- Sec.5 registers
#                          np=4 (L3) and np=8 (L2, L1).
#
# EVERY VALUE BELOW IS SET EXPLICITLY AND NONE IS INHERITED.
# =====================================================================
PRIMAL_MIN_RES_TOL="1.0e-8"        # Sec.3.5 -- G-TOL refuses anything else
PRIMAL_MIN_RES_TOL_DIFF="100"      # Sec.3.5 -- the accept floor is the PRODUCT (N-D43)
END_TIME="6000"                    # Sec.4.1 anchor / Sec.5 cost basis
DELTA_T="1"                        # Sec.4.1 -- unit steps
PRINT_INTERVAL="100"               # AMENDMENT 1(a): 1+floor(6000/100)=61 samples
WRITE_INTERVAL="2000"              # MUST DIVIDE endTime -- see the G-COMPLETE note
# *** THE LOG NAME IS LOAD-BEARING AND `log.primal` WOULD HAVE BEEN WRONG. ***
# `find_log` globs BOTH `log*` and `*.log` and REFUSES on >= 2 candidates.
# G-COMPLETE clause 1 reads the exit code from `<case>/<log>.rc` first.  With a
# log named `log.primal` the rc artifact is `log.primal.rc` -- WHICH ITSELF
# MATCHES `log*` -- so a SOLVED case would present TWO candidates and the
# comparator would refuse it for ambiguity.  Measured in this runner's own
# selftest (unit E0 caught it: expected 1, got 2).
# `primal.log` matches `*.log`; `primal.log.rc` matches NEITHER glob.  Exactly
# one candidate, and the rc still lands on the comparator's PREFERRED name.
LOG_NAME="primal.log"

# Sec.4.1 flow conditions -- re-asserted per level, never carried across
U0="291.6"; P0="101325.0"; T0="300.0"; NUTILDA0="4.5e-5"
AOA0="3.06"; A0="0.7575"; RHO0="1.0"

# Sec.5: ranks per level
declare -A RANKS=( [L3]=4 [L2]=8 [L1]=8 )
# Sec.2.5: the registered exit condition, re-checked here before any solve
declare -A WANT_CELLS=( [L3]=99840 [L2]=798720 [L1]=6389760 )
declare -A WANT_WING=(  [L3]=6240  [L2]=24960  [L1]=99840   )

# Sec.2.2 / DAFOAM_CHARTER Sec.6: the image is pinned BY DIGEST, never by tag.
IMAGE_DIGEST="sha256:8352629516bb363345fd802ed6092f878bad0a612c05c98d492a14bd94729d46"

# --------------------------------------------------------------------
LEVEL=""; ROOT=""; TEMPLATE="/home/ubuntu/certonomous-runs/A3-onera-m6-transonic"
STAGE="all"; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --level) LEVEL="$2"; shift 2 ;;
    --root) ROOT="$2"; shift 2 ;;
    --template) TEMPLATE="$2"; shift 2 ;;
    --stage) STAGE="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '1,30p' "$0"; exit 0 ;;
    *) refuse "ARGS" "unknown argument: $1" ;;
  esac
done
[ -n "$LEVEL" ] || refuse "ARGS" "--level is required (L3, L2 or L1)"
[ -n "$ROOT" ]  || refuse "ARGS" "--root is required"
case "$LEVEL" in L3|L2|L1) ;; *) refuse "ARGS" "--level must be L3, L2 or L1, got '$LEVEL'" ;; esac
case "$STAGE" in prepare|launch|all) ;; *) refuse "ARGS" "--stage must be prepare, launch or all" ;; esac

ROOT="$(cd "$ROOT" 2>/dev/null && pwd || echo "$ROOT")"
WD="$ROOT/A3GC-$LEVEL"
assert_not_quarantined "--root"     "$ROOT"
assert_not_quarantined "the case dir" "$WD"
assert_not_quarantined "--template"  "$TEMPLATE"

NP="${RANKS[$LEVEL]}"
printf '=====================================================================\n'
printf 'A3GC RUNNER (DRAFT)  level=%s  np=%s  case=%s\n' "$LEVEL" "$NP" "$WD"
printf 'grading path FROZEN: %s\n' "$GRADE"
printf '  md5 %s  (expected 73dbe368934956700da87e5a1f44ea0c)\n' "$(md5sum "$GRADE" 2>/dev/null | cut -d' ' -f1)"
printf 'quarantine: paths must not contain %s\n' "$QUARANTINED"
printf '=====================================================================\n'

# --------------------------------------------------------------------
# STAGE: prepare
# --------------------------------------------------------------------
do_prepare() {
  [ -d "$WD" ] || refuse "PREPARE" "$WD does not exist.  Run a3gc_genmesh.sh first
  (Sec.6 stage 1); this runner does not generate meshes and NEVER copies one
  from the quarantined probe."
  [ -d "$WD/constant/polyMesh" ] || refuse "PREPARE" "$WD has no constant/polyMesh"

  # ---- 1. RE-CHECK Sec.2.5's registered counts THROUGH THE FROZEN READER.
  # Not a second opinion: the same `probe` subcommand the comparator uses, so a
  # level this runner accepts is one the grader can read.
  if [ "$DRY" = 1 ]; then
    printf '  [dry-run] would verify cells == %s and wing nFaces == %s via the frozen probe\n' \
      "${WANT_CELLS[$LEVEL]}" "${WANT_WING[$LEVEL]}"
  else
    PROBE="$(python3 "$GRADE" probe --case "$WD")" || \
      refuse "PREPARE" "the frozen comparator could not read $WD"
    GOT_C=$(printf '%s' "$PROBE" | python3 -c 'import json,sys;print(json.load(sys.stdin)["cells"])')
    GOT_W=$(printf '%s' "$PROBE" | python3 -c 'import json,sys;print(json.load(sys.stdin)["patches"]["wing"]["nFaces"])')
    printf '  measured: cells = %s (want %s), wing nFaces = %s (want %s)\n' \
      "$GOT_C" "${WANT_CELLS[$LEVEL]}" "$GOT_W" "${WANT_WING[$LEVEL]}"
    [ "$GOT_C" = "${WANT_CELLS[$LEVEL]}" ] || refuse "PREPARE" \
      "Sec.2.5: $LEVEL has $GOT_C cells, registered ${WANT_CELLS[$LEVEL]}.  'Any
  departure is a LAUNCH-BLOCKING REFUSAL, not a note.'"
    [ "$GOT_W" = "${WANT_WING[$LEVEL]}" ] || refuse "PREPARE" \
      "Sec.2.5/Sec.3.1 limb 2: $LEVEL wing nFaces = $GOT_W, registered ${WANT_WING[$LEVEL]}.
  CELL COUNT ALONE DOES NOT IDENTIFY A LEVEL."
  fi

  # ---- 2. EXACTLY ONE SOLVER LOG IN THE CASE ROOT.
  # *** A MEASURED CONTRACT COLLISION, AND THE REASON THIS STEP EXISTS. ***
  # `find_log` globs `log*` AND `*.log` in the case root and REFUSES on 0 and on
  # >=2 rather than coin-flipping.  a3gc_genmesh.sh leaves THREE files that match:
  #     logMeshGeneration.txt   (log*)
  #     checkMesh_plain.log     (*.log)
  #     checkMesh_allGeometry_allTopology.log   (*.log)
  # Measured 2026-09-11 on a real generated level.  A case handed to the grader
  # without --log-name would therefore be REFUSED for ambiguity.  They are moved
  # into meshgen/ -- MOVED, never deleted: they are the mesh's provenance.
  if [ "$DRY" = 1 ]; then
    printf '  [dry-run] would move genmesh log artifacts into %s/meshgen/\n' "$WD"
  else
    mkdir -p "$WD/meshgen"
    for f in "$WD"/log* "$WD"/*.log; do
      [ -e "$f" ] || continue
      [ "$(basename "$f")" = "$LOG_NAME" ] && continue
      mv -f "$f" "$WD/meshgen/"
    done
  fi

  # ---- 3. system/controlDict.
  # *** G-COMPLETE CLAUSE 3 READS endTime FROM THIS FILE. ***  The solver log
  # does not print endTime (measured: zero occurrences in the validated primal),
  # so the comparator REFUSES if this file is absent.  It must therefore carry
  # the endTime the run ACTUALLY used.
  # *** AND writeInterval MUST DIVIDE endTime, or clause 4 fails: a run whose
  # endTime is not a write time writes NO FIELDS THERE and the comparator
  # correctly calls that incomplete.  6000 / 2000 = 3, exact.
  if [ "$DRY" = 1 ]; then
    printf '  [dry-run] would write system/controlDict endTime=%s writeInterval=%s (%s %% %s == 0)\n' \
      "$END_TIME" "$WRITE_INTERVAL" "$END_TIME" "$WRITE_INTERVAL"
  else
    [ $(( END_TIME % WRITE_INTERVAL )) -eq 0 ] || refuse "PREPARE" \
      "writeInterval $WRITE_INTERVAL does not divide endTime $END_TIME: endTime would
  write NO FIELDS and G-COMPLETE clause 4 would correctly call the run incomplete."
    mkdir -p "$WD/system"
    cat > "$WD/system/controlDict" <<CDEOF
/*--------------------------------*- C++ -*----------------------------------*\\
| A3GC $LEVEL -- written by a3gc_run.sh.  Do not hand-edit; re-run the runner. |
\\*---------------------------------------------------------------------------*/
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }

application     DARhoSimpleCFoam;   // PREREG Sec.4.1
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         $END_TIME;          // Sec.4.1 anchor / Sec.5 cost basis -- NOT the shipped 1500
deltaT          $DELTA_T;
writeControl    timeStep;
writeInterval   $WRITE_INTERVAL;    // MUST DIVIDE endTime (G-COMPLETE clause 4)
purgeWrite      0;                  // never purge: endTime must survive to be graded
writeFormat     ascii;
writePrecision  10;
writeCompression on;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
CDEOF
  fi

  # ---- 4. system/decomposeParDict -- Sec.5 ranks, NOT the shipped 2.
  if [ "$DRY" = 1 ]; then
    printf '  [dry-run] would write system/decomposeParDict numberOfSubdomains=%s (Sec.5)\n' "$NP"
  else
    cat > "$WD/system/decomposeParDict" <<DPEOF
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
// PREREG Sec.5 registers np=4 for L3 and np=8 for L2/L1.  The shipped case
// carries numberOfSubdomains 2; that value is NOT inherited.
// DAFOAM_CHARTER Sec.5: decomposition is disclosed with every number.
numberOfSubdomains $NP;
method          scotch;
DPEOF
  fi

  # ---- 5. the runScript, with the REGISTERED tolerance.
  if [ "$DRY" = 1 ]; then
    printf '  [dry-run] would write runScript_a3gc.py with primalMinResTol=%s primalMinResTolDiff=%s\n' \
      "$PRIMAL_MIN_RES_TOL" "$PRIMAL_MIN_RES_TOL_DIFF"
  else
    cat > "$WD/runScript_a3gc.py" <<PYEOF
#!/usr/bin/env python
"""A3GC $LEVEL PRIMAL -- generated by a3gc_run.sh.  Do not hand-edit.

DERIVED FROM the shipped producer
/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/runScript.py, WITH THREE
VALUES DELIBERATELY NOT INHERITED (see a3gc_run.sh's header for the measurement):
  primalMinResTol      1.0e-8, NOT the shipped 1.0e-6   (PREREG Sec.3.5)
  endTime              6000,   NOT the shipped 1500     (Sec.4.1 / Sec.5)
  numberOfSubdomains   $NP,      NOT the shipped 2        (Sec.5)
G-TOL REFUSES anything but 1e-8 x 100, so restoring the shipped tolerance would
have the grader refuse every level after the compute was already spent.
"""
from mpi4py import MPI
from dafoam import PYDAFOAM

# --- PREREG Sec.4.1 flow conditions, re-asserted per level, never carried across
U0 = $U0            # 0.84 * 347.08 m/s -> M_inf = 0.83997
p0 = $P0
T0 = $T0
nuTilda0 = $NUTILDA0
aoa0 = $AOA0
A0 = $A0            # reference area
rho0 = $RHO0

daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DARhoSimpleCFoam",          # Sec.4.1
    "primalMinResTol": $PRIMAL_MIN_RES_TOL,        # Sec.3.5 -- G-TOL refuses anything else
    "primalMinResTolDiff": $PRIMAL_MIN_RES_TOL_DIFF,  # Sec.3.5 -- accept floor is the PRODUCT (N-D43)
    "printInterval": $PRINT_INTERVAL,              # AMENDMENT 1(a): 61 samples over 6000 iters
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
        "T0": {"variable": "T", "patches": ["inout"], "value": [T0]},
        "nuTilda0": {"variable": "nuTilda", "patches": ["inout"], "value": [nuTilda0]},
        "useWallFunction": True,               # Sec.2.6 -- s0 fixed, y+ in wall-function range
    },
    "function": {
        # Sec.4.1: the same definitions the validated run used.
        "CD": {"type": "force", "source": "patchToFace", "patches": ["wing"],
               "directionMode": "parallelToFlow", "patchVelocityInputName": "patchV",
               "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)},
        "CL": {"type": "force", "source": "patchToFace", "patches": ["wing"],
               "directionMode": "normalToFlow", "patchVelocityInputName": "patchV",
               "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)},
    },
    "inputInfo": {
        "patchV": {"type": "patchVelocity", "patches": ["inout"],
                   "flowAxis": "x", "normalAxis": "y",
                   "components": ["solver", "function"]},
    },
}

# A3GC computes NO adjoint and claims NO gradient (PREREG Sec.0), so no
# FD table is owed (DAFOAM_CHARTER Sec.1).  This is a PRIMAL ONLY.
DASolver = PYDAFOAM(options=daOptions, comm=MPI.COMM_WORLD)
DASolver()
funcs = {}
DASolver.evalFunctions(funcs)
if MPI.COMM_WORLD.rank == 0:
    print("A3GC_PRIMAL_DONE $LEVEL", flush=True)
    for k in sorted(funcs):
        print("A3GC_FUNC %s = %.17g" % (k, funcs[k]), flush=True)
PYEOF
  fi

  # ---- 6. THE COLD START, AND THE AGE-GUARD ORDERING.
  # G-COMPLETE clause 6 requires every endTime field to be NEWER than the case's
  # own `0/T`, because `0/T` is touched LAST at launch and so DATES THE RUN
  # ALLOWED TO PRODUCE THE ANSWER.  THAT ORDERING IS PRODUCED HERE, NOT HOPED FOR:
  # `0` is rebuilt from `0.orig` and then `0/T` is touched LAST, as the final act
  # of prepare.  Sec.3.3 G-COLD also requires NO time directory other than `0`.
  if [ "$DRY" = 1 ]; then
    printf '  [dry-run] would rebuild %s/0 from %s/0.orig, then TOUCH 0/T LAST (age-guard ordering)\n' "$WD" "$TEMPLATE"
  else
    [ -d "$TEMPLATE/0.orig" ] || refuse "PREPARE" "template has no 0.orig: $TEMPLATE"
    # Sec.3.3: a guard refuses a case where a time dir already exists.  The
    # runner does not "clean up and proceed" on a graded case -- it refuses.
    # *** THE GLOB IS NOT A TIME-DIRECTORY TEST, AND THAT IS A DEFECT THIS
    #     GUARD HAD.  `[0-9]*` is a SHELL GLOB: it matches any name STARTING
    #     with a digit, so it matches `0.orig` -- which is not a time directory
    #     at all, but OpenFOAM's standard pristine initial-conditions template.
    #     The FROZEN a3gc_genmesh.sh copies `0.orig` into every case directory
    #     it builds (its `HOST cp -r "$TEMPLATE/0.orig" "$WD/"`), and the shipped
    #     M6 template always has one, SO THE FROZEN STAGE-1 GENERATOR GUARANTEED
    #     THIS GUARD REFUSED EVERY LEVEL AT STAGE 2.  Measured: prepare on the
    #     freshly generated, correct 99,840-cell L3 exited 2 with
    #     "a non-zero time directory already exists: .../0.orig".
    #     G-COLD'S INTENT IS UNCHANGED AND IS NOT WEAKENED: a real time
    #     directory other than `0` still REFUSES, in the case dir and in every
    #     processor* dir.  What changes is that the guard now CLASSIFIES the
    #     name instead of pattern-matching its first character -- and anything
    #     it CANNOT classify REFUSES rather than being ignored, so this repair
    #     cannot become a hole. ***
    for d in "$WD"/[0-9]* "$WD"/processor*/[0-9]*; do
      [ -e "$d" ] || continue
      b="$(basename "$d")"
      case "$b" in
        0) ;;                                  # the cold start itself: expected
        *[!0-9.]* | *.*.* | .* | *.)           # not a valid OpenFOAM time name
          if [ "$b" = "0.orig" ]; then
            :   # OpenFOAM's pristine IC template, written by stage 1.  NOT a
                # time directory, and never read by this runner -- the cold `0`
                # is built from "$TEMPLATE/0.orig", never from "$WD/0.orig".
          else
            refuse "PREPARE" "Sec.3.3 G-COLD: $d starts with a digit but is not a
  valid OpenFOAM time name and is not the known 0.orig template.  The guard
  REFUSES what it cannot classify rather than ignoring it."
          fi
          ;;
        *) refuse "PREPARE" "Sec.3.3 G-COLD: a non-zero time directory
  already exists: $d.  This case has been run before.  A guard that finds this
  REFUSES the level; it does not clean up and proceed." ;;
      esac
    done
    rm -rf "$WD/0"
    cp -a "$TEMPLATE/0.orig" "$WD/0"
    [ -f "$WD/0/T" ] || refuse "PREPARE" "$WD/0/T absent after cold start -- the age
  guard's reference would not exist and G-COMPLETE clause 6 is NOT waived for
  want of a reference."
    sync
    sleep 1          # so 0/T is strictly, measurably older than anything written later
    touch "$WD/0/T"  # *** LAST.  This timestamps the run allowed to answer. ***
  fi
  printf '  prepare: complete for %s\n' "$LEVEL"
}

# --------------------------------------------------------------------
# STAGE: launch
# --------------------------------------------------------------------
do_launch() {
  local LOG="$WD/$LOG_NAME" RC="$WD/$LOG_NAME.rc"
  # G-COMPLETE clause 1 reads <case>/<log>.rc then <case>/rc, and REFUSES if
  # neither exists, because A MISSING EXIT CODE IS NOT A ZERO EXIT CODE.
  #
  # *** THE rc IS CAPTURED INSIDE THE DETACHED WRAPPER, NEVER AROUND THE setsid
  # LINE.  `setsid timeout cmd` EXITS 0 FOR EVERY OUTCOME -- success, timeout,
  # SIGKILL -- so an rc taken around the launch measures nothing at all. ***
  rm -f "$RC"
  cat > "$WD/_a3gc_wrapper.sh" <<WEOF
#!/usr/bin/env bash
# Generated by a3gc_run.sh.  The exit code is captured HERE, INSIDE the
# detached process, for the reason in the runner's do_launch().
cd "$WD"
docker run --rm --cpus=$NP -v "$WD":"$WD" -w "$WD" \\
  "$IMAGE_DIGEST" \\
  mpirun -np $NP python runScript_a3gc.py > "$LOG" 2>&1
rc=\$?
printf '%d\\n' "\$rc" > "$RC"
WEOF
  chmod +x "$WD/_a3gc_wrapper.sh"
  if [ "$DRY" = 1 ]; then
    printf '  [dry-run] wrapper written; would run: setsid nohup %s &\n' "$WD/_a3gc_wrapper.sh"
    printf '  [dry-run] rc would be captured INSIDE the wrapper into %s\n' "$RC"
    return 0
  fi
  printf '  launching detached (parented to init, so the fleet dying does not touch it)\n'
  setsid nohup "$WD/_a3gc_wrapper.sh" >/dev/null 2>&1 &
  printf '  launched.  log  %s\n  rc   %s\n' "$LOG" "$RC"
}

case "$STAGE" in
  prepare) do_prepare ;;
  launch)  do_launch ;;
  all)     do_prepare; do_launch ;;
esac
