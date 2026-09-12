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
#   a3gc_run.sh --level L3|L2|L1|AR1 --root <parent-dir> [--template <case>]
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
# *** `100` WAS A PYTHON `int` AND pyDAFoam REFUSES IT AT ITS OWN TYPE CHECK.
# MEASURED 2026-09-11 21:32Z, four ranks, pyDAFoam.py:2029:
#   "Datatype for Option primalMinResTolDiff was not valid.
#    Expected data type is <class 'float'>  Received data type is <class 'int'>"
# THE VALUE DOES NOT MOVE AND NO GATE MOVES WITH IT.  The frozen a3gc_grade.py
# already registers REG_PRIMAL_MIN_RES_TOL_DIFF = 100.0 (line 232) and reads the
# solver's own DAOption dump through float() (line 619), so `100` and `100.0`
# are the SAME NUMBER to G-TOL.  This is a Python literal-type spelling forced
# by the solver, not a threshold edit.
PRIMAL_MIN_RES_TOL_DIFF="100.0"    # Sec.3.5 -- the accept floor is the PRODUCT (N-D43)
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
declare -A RANKS=( [L3]=4 [L2]=8 [L1]=8 [AR1]=4 )
# Sec.2.5: the registered exit condition, re-checked here before any solve
declare -A WANT_CELLS=( [L3]=99840 [L2]=798720 [L1]=6389760 [AR1]=399360 )
declare -A WANT_WING=(  [L3]=6240  [L2]=24960  [L1]=99840   [AR1]=6240   )

# Sec.2.2 / DAFOAM_CHARTER Sec.6: the image is pinned BY DIGEST, never by tag.
IMAGE_DIGEST="sha256:8352629516bb363345fd802ed6092f878bad0a612c05c98d492a14bd94729d46"

# CONTAINER IDENTITY -- the same measured choice a3gc_genmesh.sh makes, and for
# the same two measured reasons.  uid 1002 is the image's own dafoamuser, and
# /home/dafoamuser is drwxr-x--- 1002:1002, so ONLY uid 1002 can traverse it to
# reach loadDAFoam.sh.  The gid is the HOST's, with `umask 0002` below, so the
# solver's time directories land group-writable to the host and the host can
# still clean its own run root.  THE LAUNCH PREVIOUSLY PASSED NO `-u` AT ALL,
# so it ran as 1002:1002 into a 2775 ubuntu:ubuntu case directory, where
# "other" is r-x: THE SOLVER COULD NOT HAVE WRITTEN A SINGLE TIME DIRECTORY
# even if its environment had loaded.
CONTAINER_UID="1002"
CONTAINER_GID="$(id -g)"

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
[ -n "$LEVEL" ] || refuse "ARGS" "--level is required (L3, L2, L1 or AR1)"
[ -n "$ROOT" ]  || refuse "ARGS" "--root is required"
case "$LEVEL" in L3|L2|L1|AR1) ;; *) refuse "ARGS" "--level must be L3, L2, L1 or AR1, got '$LEVEL'" ;; esac
case "$STAGE" in prepare|launch|all|assertframe) ;; *) refuse "ARGS" "--stage must be prepare, launch, all or assertframe" ;; esac

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

  # ==================================================================
  # constant/ MODEL DICTS -- STAGED, THEN ASSERTED.  NOT A BLIND COPY.
  #
  # *** MEASURED 2026-09-11 21:40Z: the case had constant/polyMesh AND NOTHING
  # ELSE.  a3gc_genmesh.sh builds the mesh and the runner wrote system/ and 0,
  # but NEITHER EVER STAGED constant/thermophysicalProperties.  DARhoSimpleCFoam
  # is COMPRESSIBLE and stops dead without it:
  #   [0] --> FOAM FATAL ERROR: cannot find file
  #       ".../processor0/constant/thermophysicalProperties"
  # reached only AFTER "DAOption created.  DASolver initialized." and
  # "Calculations will run for 6000 steps" -- i.e. every earlier repair held and
  # this was the next thing in the way.
  #
  # THE PREREGISTRATION GOVERNS BOTH DICTS, so this is staging a REGISTERED
  # input, not choosing physics.  Sec.4.1: "solver DARhoSimpleCFoam; turbulence
  # SpalartAllmaras with wall functions ... the same definitions the validated
  # run used", and the validated run is $TEMPLATE.  The runner's "nothing is
  # inherited" rule (see the header) names THREE disagreements with the shipped
  # producer -- primalMinResTol, endTime, numberOfSubdomains -- and all three
  # live in the runScript and system/, NOT in constant/.
  #
  # BUT A REGISTERED SOURCE IS STILL NOT EVIDENCE THAT THE FILE SAYS WHAT IT
  # SHOULD.  Each staged dict is READ BACK and must declare the registered
  # model, and the thermo dict must REPRODUCE THE REGISTERED FREESTREAM MACH
  # NUMBER from its own molWeight and Cp.  That last check is the discriminating
  # one: a plausible-looking thermo dict for a DIFFERENT gas would pass a
  # filename check, pass a "perfectGas" grep, and silently solve the wrong
  # freestream.  MEASURED on the staged file: R = 286.99, gamma = 1.4001,
  # a = 347.17 m/s, M = 291.6/347.17 = 0.83994 against Sec.4.1's 0.83997.
  # ==================================================================
  for d in thermophysicalProperties turbulenceProperties; do
    [ -f "$TEMPLATE/constant/$d" ] || refuse "PREPARE" "Sec.4.1 registers the validated
  run's model definitions, and $TEMPLATE/constant/$d is not there.  Refusing rather
  than solving with whatever default the solver would invent."
    [ "$DRY" = 1 ] && printf '  [dry-run] would stage constant/%s from the validated template\n' "$d"
  done

  # *** VALIDATE THE TEMPLATE, THEN COPY.  NEVER COPY AND THEN VALIDATE.
  # MEASURED, and it is the reason this block was rewritten: the first spelling
  # copied both dicts into the case and asserted afterwards.  A REFUSAL THEN
  # LEFT THE REJECTED DICT SITTING IN THE CASE DIRECTORY.  Planting an
  # oxygen-like molWeight (32) produced a correct, loud refusal -- and left the
  # case holding constant/thermophysicalProperties with molWeight 32.000000.
  # Any later `--stage launch` that did not re-run prepare would have solved the
  # WRONG GAS with nothing in the record to say so.  A GUARD THAT WRITES BEFORE
  # IT JUDGES CONVERTS A CLEAN REFUSAL INTO A CONTAMINATED CASE.  Everything
  # below now reads $TEMPLATE; the case is written only once all of it passes. ***
  TT="$TEMPLATE/constant/turbulenceProperties"
  TH="$TEMPLATE/constant/thermophysicalProperties"
  if [ "$DRY" != 1 ]; then
    grep -qE '^[[:space:]]*RASModel[[:space:]]+SpalartAllmaras;' "$TT" \
      || refuse "PREPARE" "Sec.4.1 registers turbulence SpalartAllmaras and the staged
  constant/turbulenceProperties does not declare it."
    grep -qE '^[[:space:]]*turbulence[[:space:]]+on;' "$TT" \
      || refuse "PREPARE" "the staged constant/turbulenceProperties does not have
  turbulence on -- a laminar solve is not what Sec.4.1 registered."
    grep -q 'hePsiThermo' "$TH" \
      || refuse "PREPARE" "the staged constant/thermophysicalProperties is not
  hePsiThermo -- DARhoSimpleCFoam's compressible thermo is what Sec.4.1 registered."
    MACH=$(python3 - "$TH" "$U0" "$T0" <<'MPY'
import re, sys, math
txt = open(sys.argv[1]).read(); U0 = float(sys.argv[2]); T0 = float(sys.argv[3])
def val(key):
    m = re.search(r'^\s*%s\s+([0-9.eE+-]+)\s*;' % key, txt, re.M)
    if not m: sys.exit("MISSING:" + key)
    return float(m.group(1))
W = val("molWeight"); Cp = val("Cp")
R = 8314.462618 / W; gamma = Cp / (Cp - R)
print("%.5f" % (U0 / math.sqrt(gamma * R * T0)))
MPY
)   || refuse "PREPARE" "could not read molWeight/Cp out of the staged thermo dict:
  $MACH.  A dict this runner cannot read is a dict it will not solve with."
    printf '  staged constant/: SpalartAllmaras on, hePsiThermo, M(from the dict) = %s (Sec.4.1: 0.83997)\n' "$MACH"
    python3 -c "import sys; sys.exit(0 if abs(float('$MACH') - 0.83997) <= 2.0e-4 else 1)" \
      || refuse "PREPARE" "the staged constant/thermophysicalProperties gives freestream
  Mach $MACH from its OWN molWeight and Cp, but Sec.4.1 registers 0.83997 at
  U0=$U0, T0=$T0.  THE STAGED GAS IS NOT THE REGISTERED GAS.  Refusing."
    # Only now, with every assertion passed, is anything written into the case.
    for d in thermophysicalProperties turbulenceProperties; do
      cp -a "$TEMPLATE/constant/$d" "$WD/constant/$d"
      chmod g+w "$WD/constant/$d" 2>/dev/null || true
    done
  fi

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
    # ================================================================
    # THE REGISTERED INCIDENCE IS APPLIED TO THE INLET.  Sec.4.1 registers
    # aoa0 = 3.06 deg and the frame flowAxis x / normalAxis y.
    #
    # *** MEASURED 2026-09-11 22:03Z, ON A COMPLETE rc=0 RUN TO endTime 6000:
    # `aoa0` WAS DEFINED ON ONE LINE AND APPLIED NOWHERE.  grep for aoa/alpha/
    # incidence in the generated runScript returned exactly ONE hit -- the
    # assignment -- while the inlet read [U0, 0.0, 0.0], pure x, ZERO INCIDENCE.
    # The run answered a different question from the one registered:
    #   CD = 0.018382325936750141  against Sec.4.1's anchor 0.0229956
    #   CL = 2.9541973523006249e-06 against Sec.4.1's anchor 0.3131159
    # CL five orders of magnitude low is not a near miss; on the M6's symmetric
    # section it is the SIGNATURE of alpha = 0.  Graded NOT A RESULT.
    #
    # WHY THE COMPONENTS ARE COMPUTED HERE AND EMITTED AS LITERALS, rather than
    # written as `U0*cos(radians(aoa0))` in the runScript: so that the assertion
    # below can read THE NUMBERS THAT ACTUALLY REACH THE CASE and take their own
    # arctangent, instead of re-reading the same expression that produced them.
    # A check that evaluates the author's formula agrees with the author by
    # construction.  This one can disagree.
    #
    # DAFoam's own definition, pyDAFoam.py inputInfo docstring, is what makes the
    # boundary the right place:  "alpha = atan( U_normal / U_flow ) at patches".
    # The incidence is DERIVED FROM THE PATCH VELOCITY, so setting the inlet
    # vector is what sets alpha for both the solve and the parallelToFlow /
    # normalToFlow force resolution.  No angle is invented and Sec.4.1 is not
    # touched: the registered value and the registered axes are read and applied.
    # ================================================================
    read UX UY <<EOFUV
$(python3 -c "import math;a=math.radians($AOA0);print('%.17g %.17g' % ($U0*math.cos(a), $U0*math.sin(a)))")
EOFUV
    [ -n "$UX" ] && [ -n "$UY" ] || refuse "PREPARE" "could not compute the registered
  inlet vector from U0=$U0 aoa0=$AOA0.  Refusing rather than writing a runScript
  with an inlet this runner cannot state."

    # *** STAGED, THEN ASSERTED, THEN MOVED INTO PLACE.  ITEM 6 AGAIN, IN A NEW
    # SPOT AND CAUGHT BY ITS OWN PLANT: the first spelling wrote the runScript
    # STRAIGHT INTO THE CASE and asserted afterwards, so a refusal left the
    # REJECTED inlet sitting there.  MEASURED -- after the wrong-magnitude plant
    # refused, the case held "value": [145.59211560722454, 7.7830503668272781,
    # 0.0], a half-Mach freestream, ready for any later `--stage launch` that did
    # not re-run prepare.  A GUARD THAT WRITES BEFORE IT JUDGES TURNS A CLEAN
    # REFUSAL INTO A CONTAMINATED CASE -- the same lesson the constant/ staging
    # paid for two hours earlier, which is why it is written twice. ***
    RS_STAGING="$WD/.runScript_a3gc.py.staging"
    rm -f "$RS_STAGING"
    # ================================================================
    # THE RUNSCRIPT HEREDOC IS UNQUOTED, AND COMMAND SUBSTITUTION IN IT RUNS ON
    # THE HOST WHILE THE FILE IS BEING WRITTEN.
    #
    # *** MEASURED, AND SELF-INFLICTED, 2026-09-11 22:36Z: twelve backticks in a
    # COMMENT block of this heredoc were executed by the host shell -- six
    # "command not found" errors -- and the quoted words were SILENTLY DELETED
    # from the generated runScript, leaving sentences like "and  is , so it
    # assigns refValue()". The CODE was untouched, which is exactly what makes it
    # dangerous: nothing failed, and the file looked fine unless read closely.
    # The wrapper heredoc in do_launch() HAS CARRIED THIS GUARD FOR HOURS. This
    # heredoc did not, and paid within minutes of being edited. Rule 14: a lesson
    # is not applied until EVERY call site asserts it -- so it is asserted here.
    # A backtick and a $( are both command substitution; neither belongs in
    # generated Python, while the bare $VAR expansions in this heredoc are
    # deliberate and are what carry the registered values in.
    # ================================================================
    PYHD=$(sed -n '/^    cat > "$RS_STAGING" <<PYEOF$/,/^PYEOF$/p' "$0" || true)
    case "$PYHD" in
      '') refuse "PREPARE" "the heredoc self-check extracted no runScript source from
  $0.  A check that reads nothing passes everything.  Refusing." ;;
    esac
    case "$PYHD" in
      *'`'*) refuse "PREPARE" "the runScript heredoc in $0 contains a BACKTICK.  This
  heredoc is UNQUOTED, so the HOST shell will execute that text while writing the
  runScript and the quoted words will not survive into the generated file.
  Refusing." ;;
    esac
    case "$PYHD" in
      *'$('*) refuse "PREPARE" "the runScript heredoc in $0 contains a \$( command
  substitution.  This heredoc is UNQUOTED, so the HOST shell will run it while
  writing the runScript.  Refusing." ;;
    esac
    printf '  runScript heredoc asserted: no backtick, no command substitution\n'
    cat > "$RS_STAGING" <<PYEOF
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
import numpy as np

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
        "U0": {"variable": "U", "patches": ["inout"], "value": [$UX, $UY, 0.0]},   # Sec.4.1 aoa0=$AOA0 deg, flowAxis x / normalAxis y
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

# ================================================================
# THE REGISTERED INCIDENCE IS DRIVEN INTO THE SOLVER, NOT ONLY INTO THE INLET.
#
# *** MEASURED 2026-09-11: ROTATING THE INLET IS ONLY HALF THE FIX, AND THE HALF
# THAT SHOWS.  'patchV' is declared in inputInfo above and named by BOTH
# functions as 'patchVelocityInputName', and in a bare PYDAFOAM primal NOTHING
# EVER GAVE IT A VALUE.  In the image (digest 8352629516bb...), read from source:
#   DAGlobalVar.H:59      scalarList patchVelocity = {0.0, 0.0};   <- DEFAULT AoA 0
#   DAFunctionForce.C:100 scalar aoaDeg = globalVar.patchVelocity[1];
#                         forceDir_ is built from THAT STORED SCALAR.
#   DAInputPatchVelocity.C is the ONLY writer of globalVar.patchVelocity, and it
#                         runs ONLY when the input is driven.
# So the force-resolution frame is NOT measured from the flow.  With the inlet
# rotated but patchV unset, the FLOW is at aoa0 and the FRAME is at ZERO:
# 'parallelToFlow' degenerates to +x and 'normalToFlow' to +y.
#
# WHAT THAT COSTS, AT THIS CASE'S OWN NUMBERS: the omitted induced projection is
# CL*sin(aoa0) = 0.016257 against a reported CD = 0.013543 -- THE MISSING TERM IS
# 120% OF THE REPORTED VALUE, larger than the value itself.  CL meanwhile moves
# by +0.25%, which is why CL CANNOT DETECT THIS AND CD CAN.
#
# pyDAFoam.py:243 reads "alpha = atan( U_normal / U_flow ) at patches".  THAT IS
# THE CONVENTION, NOT A MEASUREMENT: the code measures nothing, it reads a scalar
# that defaults to zero.  Reading it as a measurement is what cost the frame.
#
# DAInputPatchVelocity::run sets BOTH globalVar.patchVelocity AND the inlet U
# components, from the scalars [UMag, aoa] -- BY ASSIGNMENT, never from the
# current field -- and 'inout' is 'inletOutlet', so it assigns refValue()[faceI]
# componentwise.  THE primalBC ROTATION ABOVE IS THEREFORE REDUNDANT-AND-
# CONSISTENT, NOT DOUBLED: both paths assign the same absolute vector computed
# from the same two registered scalars, so no ordering of them can compound an
# angle.  It is KEPT because it is what the staged-file arctangent assertion
# reads, and that assertion catches a bad vector BEFORE compute is spent.
# The claim is not left as reasoning: run_a3gc asserts the applied angle back out
# of the solver's own written U field (see assert_frame), where a doubled angle
# would read 6.12 deg and a single one reads aoa0.
#
# Sec.4.1 supplies BOTH numbers and nothing here invents either: [U0, aoa0].
# ================================================================
DASolver.set_solver_input({"patchV": np.array([U0, aoa0])})

DASolver()
funcs = {}
DASolver.evalFunctions(funcs)
if MPI.COMM_WORLD.rank == 0:
    print("A3GC_PRIMAL_DONE $LEVEL", flush=True)
    for k in sorted(funcs):
        print("A3GC_FUNC %s = %.17g" % (k, funcs[k]), flush=True)
PYEOF
    # ================================================================
    # THE INCIDENCE IS ASSERTED FROM THE GENERATED FILE, BY ARCTANGENT.
    #
    # *** A `grep` FOR aoa0 WOULD HAVE PASSED THE FILE THAT JUST SPENT 63.7
    # core-min ANSWERING THE WRONG QUESTION.  The variable was present the whole
    # time; presence was never the property that mattered.  So the check does not
    # look for a name.  It reads the two numbers actually written into the inlet
    # vector, takes atan2(Uy, Ux) itself, and demands Sec.4.1's registered angle
    # back -- and demands the magnitude back too, because an angle alone would
    # accept a vector that had quietly lost its Mach number. ***
    # ================================================================
    IVEC=$(grep -oE '"U0": \{"variable": "U", "patches": \["inout"\], "value": \[[^]]*\]' \
             "$RS_STAGING" | grep -oE '\[[-0-9.eE+, ]*\]$')
    # PLANT THE ZERO: an extraction that matched nothing would pass every test
    # below vacuously.  Demand it saw a three-component vector first.
    case "$IVEC" in
      \[*,*,*\]) : ;;
      *) refuse "PREPARE" "the incidence check could not extract an inlet vector from
  $RS_STAGING (got [$IVEC]).  A check that reads nothing passes
  everything.  Refusing." ;;
    esac
    AOA_BACK=$(python3 - "$IVEC" "$U0" <<'APY'
import math, sys
v = [float(x) for x in sys.argv[1].strip("[]").split(",")]
ux, uy, uz = v[0], v[1], v[2]
print("%.6f %.6f %.6f" % (math.degrees(math.atan2(uy, ux)), math.hypot(ux, uy), uz))
APY
)   || refuse "PREPARE" "could not read the inlet vector back out of the generated
  runScript: $AOA_BACK"
    set -- $AOA_BACK
    printf '  inlet asserted: vector %s -> aoa = %s deg (Sec.4.1: %s), |U| = %s (U0 = %s), Uz = %s\n' \
      "$IVEC" "$1" "$AOA0" "$2" "$U0" "$3"
    python3 -c "
import sys
aoa, mag, uz = float('$1'), float('$2'), float('$3')
ok = abs(aoa - $AOA0) <= 1.0e-4 and abs(mag - $U0) <= 1.0e-6 * $U0 and abs(uz) <= 1.0e-12
sys.exit(0 if ok else 1)" || refuse "PREPARE" "Sec.4.1 registers aoa0 = $AOA0 deg at
  U0 = $U0 in the flowAxis x / normalAxis y frame, but the inlet vector actually
  written into the staged runScript is $IVEC, whose own arctangent is $1 deg with
  |U| = $2 and Uz = $3.  THE CASE DOES NOT CARRY THE REGISTERED FLOW CONDITION.
  A complete, well-formed solve of the wrong freestream is what this refusal
  exists to prevent -- one has already been paid for.  Refusing."
    # ================================================================
    # AND THE INPUT THAT SETS THE FORCE FRAME IS ASSERTED TOO.
    #
    # *** THE ARCTANGENT CHECK ABOVE IS NECESSARY AND NOT SUFFICIENT.  It reads
    # the INLET VECTOR, and a file can carry a perfect inlet vector while the
    # force-resolution frame sits at zero -- that is exactly the state a stopped
    # run was caught in at Time = 3500.  `patchV` is declared in inputInfo and
    # named by both functions, and NOTHING GAVE IT A VALUE; DAGlobalVar.H:59
    # defaults it to {0.0, 0.0} and DAFunctionForce.C:100 builds forceDir_ from
    # that default.  So this check demands the DRIVING CALL, demands it lands
    # BEFORE the primal, and reads the two registered scalars back out of the
    # file's own assignments.  A DECLARATION IS NOT A VALUE. ***
    # ================================================================
    DRIVE_LN=$(grep -n 'set_solver_input' "$RS_STAGING" | grep 'patchV' | head -1 | cut -d: -f1 || true)
    # PLANT THE ZERO: an extraction that matched nothing must refuse, not pass.
    case "$DRIVE_LN" in
      ''|*[!0-9]*) refuse "PREPARE" "the staged runScript $RS_STAGING contains NO
  set_solver_input call driving patchV.  patchV is declared in inputInfo and is
  named by both CD and CL as patchVelocityInputName, but DECLARING AN INPUT DOES
  NOT GIVE IT A VALUE: DAGlobalVar defaults patchVelocity to {0.0, 0.0} and the
  force direction is built from that default, so both functions would resolve in
  a ZERO-INCIDENCE FRAME while the flow ran at $AOA0 deg.  A complete solve in the
  wrong force frame has already been paid for once.  Refusing." ;;
    esac
    PRIMAL_LN=$(grep -n '^DASolver()' "$RS_STAGING" | head -1 | cut -d: -f1 || true)
    case "$PRIMAL_LN" in
      ''|*[!0-9]*) refuse "PREPARE" "could not locate the primal call in
  $RS_STAGING.  A check that cannot find the thing it orders cannot order it.
  Refusing." ;;
    esac
    [ "$DRIVE_LN" -lt "$PRIMAL_LN" ] || refuse "PREPARE" "the patchV driving call is at
  line $DRIVE_LN and the primal call is at line $PRIMAL_LN.  AN INPUT DRIVEN AFTER
  THE SOLVE IS AN INPUT THAT NEVER REACHED IT.  Refusing."
    # The call passes the file's own U0 and aoa0, so those two assignments are
    # the numbers that reach the solver.  READ THEM BACK, numerically.
    FU0=$(grep -oE '^U0 = [-0-9.eE+]+' "$RS_STAGING" | head -1 | awk '{print $3}' || true)
    FAOA=$(grep -oE '^aoa0 = [-0-9.eE+]+' "$RS_STAGING" | head -1 | awk '{print $3}' || true)
    { [ -n "$FU0" ] && [ -n "$FAOA" ]; } || refuse "PREPARE" "could not read U0/aoa0 back
  out of $RS_STAGING (got U0=[$FU0] aoa0=[$FAOA]).  A check that reads nothing
  passes everything.  Refusing."
    python3 -c "
import sys
sys.exit(0 if abs(float('$FU0') - $U0) <= 1.0e-9 and abs(float('$FAOA') - $AOA0) <= 1.0e-9 else 1)" \
      || refuse "PREPARE" "Sec.4.1 registers U0 = $U0 and aoa0 = $AOA0, but the staged
  runScript drives patchV with U0 = $FU0 and aoa0 = $FAOA.  Refusing."
    printf '  patchV asserted: driven at line %s (primal at %s) with [U0=%s, aoa0=%s deg]\n' \
      "$DRIVE_LN" "$PRIMAL_LN" "$FU0" "$FAOA"
    # Every assertion passed.  ONLY NOW does the runScript enter the case.
    mv "$RS_STAGING" "$WD/runScript_a3gc.py"
    [ -f "$WD/runScript_a3gc.py" ] || refuse "PREPARE" "the asserted runScript did not
  land at $WD/runScript_a3gc.py."
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
    # *** AND THE PREVIOUS ATTEMPT'S DECOMPOSITION.  G-COLD above has ALREADY
    # refused any processor*/<non-zero time>, so anything surviving here is a
    # cold decomposition from an attempt that never produced a result.  Leaving
    # it would let the solver read processor fields this cold start did not
    # write, which is exactly what the age guard exists to prevent.  Evidence is
    # not destroyed by this: a failed attempt is preserved in a sibling
    # directory before any relaunch. ***
    rm -rf "$WD"/processor*
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
  # *** THE DAFOAM ENVIRONMENT IS LOADED BEFORE DAFOAM TOOLS ARE INVOKED.
  # This line previously ran `mpirun -np N python runScript...` as the container's
  # command with NO shell and NO environment load whatsoever, and it died rc=134:
  #   "mpirun was unable to find the specified executable file ... Executable:
  #    python ... 4 total processes failed to start".
  # `python`, `mpirun` and the DAFoam libraries live behind loadDAFoam.sh; without
  # it the container has no DAFoam at all.  THIS IS THE THIRD INSTRUMENT IN THIS
  # RUNG FAMILY TO INVOKE A CONTAINERISED TOOL WITHOUT ESTABLISHING ITS
  # ENVIRONMENT FIRST, and the three failed three different ways: a3gc_genmesh.sh
  # SUPPRESSED the load with `|| true` and reported a missing binary; D8G's
  # cmd.sh put `set -e` AHEAD of the load and aborted inside OpenFOAM's bashrc;
  # this one OMITTED the load entirely and blamed mpirun.
  # The environment is checked by a POSITIVE CAPABILITY ASSERTION, not by rc --
  # the source returns 0 even when nothing loaded -- and `set -e` is armed AFTER
  # the assertion, because armed BEFORE the source it aborts in
  # OpenFOAM-v2506/etc/config.sh/setup:207 (measured).
  # *** WHY THE ASSERTION NAMES `python` AND WHY `mpirun` ALONE WOULD HAVE BEEN
  # WORTHLESS.  PLANTED CONTROL, MEASURED ON THIS BOX 2026-09-11 21:29Z, this
  # exact prologue, this pinned image, a scratch mount:
  #   uid 1000:1000 (cannot traverse drwxr-x--- /home/dafoamuser) -> exit 97,
  #     WM_PROJECT_DIR=[]  python=MISSING  mpirun=/usr/bin/mpirun
  #   uid 1002:<host gid> -> SENTINEL_PASS,
  #     WM_PROJECT_DIR=/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506
  #     python=/home/dafoamuser/dafoam/packages/miniconda3/bin/python
  #     mpirun=/usr/bin/mpirun
  # *** `mpirun` RESOLVES IDENTICALLY IN BOTH -- IT IS THE DISTRIBUTION'S
  # /usr/bin/mpirun AND IS PRESENT WITH NO DAFOAM ENVIRONMENT AT ALL.  An
  # assertion that demanded only `mpirun` would have PASSED the very environment
  # that produced rc=134.  `python` is the miniconda interpreter that exists ONLY
  # after the load, so `python` is the discriminating term; `mpirun` is asserted
  # too, but it is not what makes this assertion an assertion. ***
  # NOTE THE ESCAPING: this heredoc is UNQUOTED (<<WEOF), so every `$` that must
  # survive to the CONTAINER is backslash-escaped, exactly as the existing
  # `rc=\$?` and `"\$rc"` are.  `$NP`, `$WD`, `$LOG` and `$IMAGE_DIGEST` are
  # deliberately NOT escaped: those are host values, resolved as the wrapper is
  # written. ***
  rm -f "$RC"
  cat > "$WD/_a3gc_wrapper.sh" <<WEOF
#!/usr/bin/env bash
# Generated by a3gc_run.sh.  The exit code is captured HERE, INSIDE the
# detached process, for the reason in the runner's do_launch().
cd "$WD"
# The environment is established before any DAFoam tool runs; the runner
# comments above do_launch() carry the whole reasoning, and are kept THERE
# because THIS heredoc is unquoted.  No backtick and no bare dollar below.
docker run --rm --cpus=$NP -u $CONTAINER_UID:$CONTAINER_GID -e HOME=/home/dafoamuser \\
  -v "$WD":"$WD" -w "$WD" \\
  "$IMAGE_DIGEST" \\
  bash -lc 'umask 0002; source /home/dafoamuser/dafoam/loadDAFoam.sh; if [ -z "\${WM_PROJECT_DIR:-}" ] || ! command -v python >/dev/null 2>&1 || ! command -v mpirun >/dev/null 2>&1; then printf "REFUSE [ENV] loadDAFoam.sh did not populate the environment: WM_PROJECT_DIR=[%s] python=%s mpirun=%s id=%s\\n" "\${WM_PROJECT_DIR:-}" "\$(command -v python || echo MISSING)" "\$(command -v mpirun || echo MISSING)" "\$(id)" >&2; exit 97; fi; set -e; exec mpirun -np $NP python runScript_a3gc.py' > "$LOG" 2>&1
rc=\$?
printf '%d\\n' "\$rc" > "$RC"
WEOF
  chmod +x "$WD/_a3gc_wrapper.sh"

  # ================================================================
  # THE GENERATOR ASSERTS WHAT IT ACTUALLY WROTE.  MEASURED, NOT ASSUMED.
  #
  # *** THIS GUARD EXISTS BECAUSE THIS GENERATOR ONCE WROTE A FILE IT DID NOT
  # INTEND.  The heredoc below is UNQUOTED (<<WEOF, deliberately -- $WD, $NP,
  # $LOG and $IMAGE_DIGEST must resolve as the wrapper is written).  An
  # explanatory comment block was added INSIDE it carrying backticks and bare
  # dollars; the HOST shell command-substituted them while writing the file and
  # ACTUALLY EXECUTED `mpirun` on the host.  The wrapper still ran, so nothing
  # announced the damage.  A GENERATOR THAT IS NOT ASKED WHAT IT WROTE WILL
  # WRITE ANYTHING.  Every term below is one this launch cannot be correct
  # without, so the assertion FAILS if the expansion is ever damaged again. ***
  # ================================================================
  W="$WD/_a3gc_wrapper.sh"
  bash -n "$W" || refuse "WRAPPER" "the generated wrapper does not parse: $W"
  for need in "loadDAFoam.sh" \
              "WM_PROJECT_DIR" \
              "exit 97" \
              "-u $CONTAINER_UID:$CONTAINER_GID" \
              "-e HOME=/home/dafoamuser" \
              "exec mpirun -np $NP python runScript_a3gc.py" \
              "$IMAGE_DIGEST"; do
    grep -qF -- "$need" "$W" || refuse "WRAPPER" "the generated wrapper is missing
  a load-bearing term: [$need]
  The generator did not write what it intended.  Refusing to launch rather than
  discovering it from a solver log an hour later."
  done
  # ================================================================
  # AND THE FAILURE MODE ABOVE CANNOT BE SEEN IN THE PRODUCT AT ALL.
  #
  # *** MEASURED, PLANTED CONTROL 2026-09-11 21:36Z: a comment carrying
  # backticks was re-inserted into the heredoc, and the guard that inspected the
  # WRITTEN WRAPPER passed it.  It had to.  THE HOST SHELL CONSUMES THE
  # BACKTICKS AS IT WRITES -- the substitution's OUTPUT lands in the file and the
  # backticks are gone, so the wrapper on disk looks innocent while `mpirun` has
  # already been executed on the host.  A PRODUCT-SIDE CHECK IS STRUCTURALLY
  # BLIND TO THIS DEFECT.  The only place the evidence still exists is THE
  # GENERATOR'S OWN SOURCE, so that is what is checked. ***
  # ================================================================
  HD=$(sed -n '/^  cat > "\$WD\/_a3gc_wrapper.sh" <<WEOF$/,/^WEOF$/p' "$0")
  # PLANT THE ZERO (CLAUDE.md rule 3): an extraction that silently matched
  # nothing would pass every test below vacuously.  Demand it saw the real text.
  case "$HD" in
    *"docker run --rm --cpus="*) : ;;
    *) refuse "WRAPPER" "the heredoc self-check extracted no wrapper source from $0.
  A check that reads nothing passes everything.  Refusing." ;;
  esac
  case "$HD" in
    *'`'*) refuse "WRAPPER" "the wrapper heredoc in $0 contains a BACKTICK.  This
  heredoc is UNQUOTED, so the host shell will execute that text while writing the
  wrapper and the evidence will not survive into the file.  Refusing." ;;
  esac
  # Every '$' in the heredoc must be either escaped (\$, meant for the container)
  # or one of the SEVEN host values this runner deliberately resolves at write
  # time.  Anything else is an expansion nobody intended.
  HDCHK=$(printf '%s' "$HD" | sed -e 's/\\\$/@/g' \
      -e 's/\$WD/@/g' -e 's/\$NP/@/g' -e 's/\$LOG/@/g' -e 's/\$RC/@/g' \
      -e 's/\$IMAGE_DIGEST/@/g' -e 's/\$CONTAINER_UID/@/g' -e 's/\$CONTAINER_GID/@/g')
  case "$HDCHK" in
    *'$'*) refuse "WRAPPER" "the wrapper heredoc in $0 contains an UNESCAPED '\$' that is
  not one of the seven host values this runner resolves at write time.  It will be
  expanded by the HOST while writing the wrapper, not by the container.  Escape it
  as \\\$ if it is meant for the container.  Refusing." ;;
  esac
  printf '  heredoc source asserted: no backtick, no unintended expansion\n'
  printf '  wrapper asserted: parses, and carries all 7 load-bearing terms\n'
  if [ "$DRY" = 1 ]; then
    printf '  [dry-run] wrapper written; would run: setsid nohup %s &\n' "$WD/_a3gc_wrapper.sh"
    printf '  [dry-run] rc would be captured INSIDE the wrapper into %s\n' "$RC"
    return 0
  fi
  printf '  launching detached (parented to init, so the fleet dying does not touch it)\n'
  setsid nohup "$WD/_a3gc_wrapper.sh" >/dev/null 2>&1 &
  printf '  launched.  log  %s\n  rc   %s\n' "$LOG" "$RC"
}

# --------------------------------------------------------------------
# STAGE: assertframe -- THE SOLVER'S OWN RECEIPT THAT THE REGISTERED FRAME RAN
#
# *** THIS IS THE ASSERTION THE FILE CHECKS CANNOT MAKE.  The arctangent check
# asserts a property of THE FILE; this one asserts a property of THE SOLVER.
# Both limbs of its control were already on disk before it was written, at zero
# cost, which is why it is trusted:
#   anchor  A3-onera-m6-transonic/run_model_run3.log  -> banner PRESENT (patchV
#           driven by the mphys wrapper), and that log carries Sec.4.1's
#           registered anchors CD 0.02299545506274655 / CL 0.3131158997344331
#   graded  A3GC-L3-NOT-A-RESULT-ZERO-INCIDENCE-.../primal.log -> banner ABSENT
#   stopped A3GC-L3-STOPPED-WRONG-FORCE-FRAME-.../primal.log   -> banner ABSENT
# A READER THAT HAS BEEN SHOWN BOTH A ZERO AND A NON-ZERO IS A READER.
#
# It also settles, BY MEASUREMENT AND NOT BY REASONING, the one thing that could
# silently double the angle.  primalBC rotates the inlet and DAInputPatchVelocity
# also sets it; if those compounded, the applied angle would be 2*aoa0 = 6.12 deg.
# They cannot compound -- both ASSIGN an absolute vector computed from the same
# two registered scalars, and `inout` is `inletOutlet`, whose branch assigns
# refValue() componentwise -- but the claim is not left as reasoning: the angle
# is read back out of the U field THE SOLVER ITSELF WROTE and must come back
# aoa0, with 2*aoa0 named explicitly as the failure it is looking for.
# --------------------------------------------------------------------
do_assert_frame() {
  local LOG="$WD/$LOG_NAME"
  [ -f "$LOG" ] || refuse "ASSERTFRAME" "no solver log at $LOG.  A MISSING LOG IS NOT A
  PASSING LOG.  Refusing."

  # ---- 1. the banner, counted and READ BACK NUMERICALLY.
  local NB
  NB=$(grep -c 'Setting UMag' "$LOG" || true)
  [ "$NB" = "1" ] || refuse "ASSERTFRAME" "the DAInputPatchVelocity banner appears $NB
  time(s) in $LOG; this runScript drives patchV exactly once, so exactly one is
  expected.  ZERO means the input never ran and the force frame sat at the
  DAGlobalVar default of 0.0 deg while the flow ran at $AOA0 -- the exact state a
  run was stopped in at Time = 3500.  Refusing."
  local BU BA
  BU=$(grep -m1 'Setting UMag' "$LOG" | sed -n 's/.*UMag = \([-0-9.eE+]*\).*/\1/p' || true)
  BA=$(grep -m1 'Setting UMag' "$LOG" | sed -n 's/.*AoA = \([-0-9.eE+]*\).*/\1/p' || true)
  { [ -n "$BU" ] && [ -n "$BA" ]; } || refuse "ASSERTFRAME" "the banner is present but its
  numbers could not be read back (UMag=[$BU] AoA=[$BA]).  A check that reads
  nothing passes everything.  Refusing."
  python3 -c "
import sys
sys.exit(0 if abs(float('$BU') - $U0) <= 1.0e-6 * $U0 and abs(float('$BA') - $AOA0) <= 1.0e-6 else 1)" \
    || refuse "ASSERTFRAME" "the solver reports it applied UMag = $BU, AoA = $BA deg, but
  Sec.4.1 registers U0 = $U0, aoa0 = $AOA0.  Refusing."
  printf '  frame asserted (solver receipt): banner x%s, UMag = %s, AoA = %s deg\n' "$NB" "$BU" "$BA"

  # ---- 2. the APPLIED angle, out of the field THE SOLVER WROTE.
  local UF=""
  # *** THE FIELDS ARE WRITTEN COMPRESSED ON THIS CASE, AND THE FIRST SPELLING OF
  # THIS LOOP LOOKED ONLY FOR `U`.  It therefore fell through to the case's own
  # cold-start 0/U, whose inout entry is the UNEXPANDED `$internalField` token and
  # carries no vector at all -- so the reader REFUSED (NOVEC) instead of passing,
  # which is the right failure, but it was reading the wrong artifact.  The
  # solver-written processor*/0/U.gz is the one DAInputPatchVelocity::run wrote. ***
  for c in "$WD"/processor*/0/U "$WD"/processor*/0/U.gz "$WD"/0/U "$WD"/0/U.gz; do
    if [ -f "$c" ]; then UF="$c"; break; fi
  done
  [ -n "$UF" ] || refuse "ASSERTFRAME" "no written U field found under $WD to read the
  applied inlet back from.  Refusing."
  local APPLIED
  APPLIED=$(python3 - "$UF" "$AOA0" "$U0" <<'APY'
import math, re, sys, gzip
_p = sys.argv[1]
txt = (gzip.open(_p, "rt").read() if _p.endswith(".gz") else open(_p).read())
aoa0 = float(sys.argv[2]); u0 = float(sys.argv[3])
m = re.search(r'\binout\b\s*\{(.*?)\}', txt, re.S)
if not m:
    print("NOINOUT"); raise SystemExit(0)
t = re.search(r'\(\s*([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\s*\)', m.group(1))
if not t:
    print("NOVEC"); raise SystemExit(0)
ux, uy, uz = (float(t.group(i)) for i in (1, 2, 3))
print("%.6f %.6f %.6f %.6f" % (math.degrees(math.atan2(uy, ux)), math.hypot(ux, uy), uz, 2.0 * aoa0))
APY
)
  case "$APPLIED" in
    NOINOUT|NOVEC|'') refuse "ASSERTFRAME" "could not read an inout velocity vector out of
  $UF (got [$APPLIED]).  A check that reads nothing passes everything.  Refusing." ;;
  esac
  set -- $APPLIED
  printf '  frame asserted (written field %s): applied aoa = %s deg, |U| = %s, Uz = %s\n' \
    "$UF" "$1" "$2" "$3"
  local RC_A=0
  python3 -c "
import sys
aoa, mag, uz, dbl = float('$1'), float('$2'), float('$3'), float('$4')
if abs(aoa - 2.0 * $AOA0) <= 1.0e-3:
    sys.stderr.write('DOUBLED\n'); sys.exit(2)
sys.exit(0 if abs(aoa - $AOA0) <= 1.0e-3 and abs(mag - $U0) <= 1.0e-4 * $U0 and abs(uz) <= 1.0e-9 else 1)" || RC_A=$?
  if [ "$RC_A" = "2" ]; then refuse "ASSERTFRAME" "THE ANGLE IS DOUBLED.  The inlet the solver
  wrote carries $1 deg, which is 2 x Sec.4.1's aoa0 = $AOA0.  primalBC and
  DAInputPatchVelocity have compounded instead of both assigning the same vector.
  Refusing."; fi
  [ "$RC_A" = "0" ] || refuse "ASSERTFRAME" "the inlet the solver actually wrote into $UF
  carries aoa = $1 deg, |U| = $2, Uz = $3, against Sec.4.1's aoa0 = $AOA0 and
  U0 = $U0.  Refusing."
  printf '  assertframe: PASSED for %s\n' "$LEVEL"
}

case "$STAGE" in
  prepare)     do_prepare ;;
  launch)      do_launch ;;
  all)         do_prepare; do_launch ;;
  assertframe) do_assert_frame ;;
esac
