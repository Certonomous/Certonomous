#!/usr/bin/env bash
# CRM WING-BODY (D8G) GRADED LAUNCHER v2 -- usage: launch_crm_wb_v2.sh <RUNDIR> <RANKS> [ENDTIME]
#
# WRITTEN AS A NEW FILE, NOT AN EDIT OF v1, on the M6 lane's standing rule: bash reads a script
# incrementally by byte offset while it runs, so editing a live launcher can resume the
# interpreter mid-token. v1 stays on disk as the record of the probes.
#
# WHAT v2 ADDS: the TWO-STAGE ROBUST STARTUP RAMP that Sanaa's section C.6 registered for this
# solver class and that this act has never had.
#   STAGE 1  first N iterations on system/fvSchemes.startup (every convective term first-order)
#            and system/fvSolution.startup (heavy relaxation). PRODUCES NO GRADED ANSWER.
#   STAGE 2  the REGISTERED schemes and solution restored BYTE-IDENTICALLY, md5 asserted on both
#            sides, from the stage-1 checkpoint to endTime. THE GRADED ANSWER COMES FROM THESE.
#
# WHY IT IS NEEDED, measured not assumed (ADDENDUM 2/3): with `bounded` wrongly on div(phid,p)
# the transonic pressure equation was INERT and the startup transient could not occur. With the
# scheme corrected the first pressure solve DIVERGED -- initial residual 0.999993, FINAL 1.611 --
# and drove p to 11,727,427 Pa against a freestream of 4,007 Pa, 2,926x, with a negative minimum.
#
# endTime is moved ONLY between stages. A pristine system/controlDict.registered is kept and the
# final state is asserted md5-identical to it, so a crash between stages cannot leave a truncated
# budget committed. Every rc is captured INSIDE this wrapper from the process itself.
# NO CAP KILLS THIS RUN: no timeout, no clock check, no spend check anywhere below (directive #17).
set -u
RUNDIR="${1:?usage: launch_crm_wb_v2.sh <RUNDIR> <RANKS> [ENDTIME]}"
RANKS="${2:?ranks}"
ENDTIME_ARG="${3:-}"
STARTUP_ITERS="${STARTUP_ITERS:-200}"
# Registered freestream of pre-registration section 4; the initialiser self-checks that these
# reproduce T_inf and p_inf EXACTLY at |U| = U_inf before it writes anything.
T_INF="${T_INF:-310.0}"
P_INF="${P_INF:-4007.394649}"
M_INF="${M_INF:-0.85}"
ISEN_TOOL="${ISEN_TOOL:-/home/ubuntu/Certonomous/cases/CRM_wingbody/tools/isentropic_init.py}"
cd "$RUNDIR" || exit 3
exec >> LAUNCH.log 2>&1
echo "=== CRM-WB launch v2  $(date -u +%FT%TZ)  rundir=$RUNDIR ranks=$RANKS"
fail() { echo "REFUSE: $*"; echo "REFUSED" > RC.txt; exit 2; }

[ "$(id -u)" -eq 0 ] && fail "running as root"
[ -d constant/polyMesh ] || fail "no polyMesh"
[ -d processor0 ]        || fail "not decomposed"
[ -d 0.orig ]            || fail "no 0.orig"
[ -f system/fvSchemes.startup ]  || fail "no system/fvSchemes.startup -- v2 requires the ramp"
[ -f system/fvSolution.startup ] || fail "no system/fvSolution.startup"
[ -f constant/fvOptions ]        || fail "no constant/fvOptions"
grep -q 'limitTemperature' constant/fvOptions || fail "constant/fvOptions carries no limitTemperature"
grep -q defaultFaces constant/polyMesh/boundary 2>/dev/null && \
  fail "defaultFaces present -- level failed the registered acceptance test"

# ---- resume detection: never restart from zero when a checkpoint exists -------------------
RESUME=no
LATEST=$(find processor0 -maxdepth 1 -type d -regextype posix-extended \
         -regex '.*/[0-9]+(\.[0-9]+)?$' -printf '%f\n' 2>/dev/null | sort -g | tail -1)
if [ -n "${LATEST:-}" ] && [ "$LATEST" != "0" ]; then
  RESUME=yes; echo "RESUME: processor0 holds a checkpoint at t=$LATEST"
else
  [ -e RC.txt ] && fail "RC.txt exists and there is no checkpoint to resume from"
  EXTRA=$(find . -maxdepth 1 -type d -regextype posix-extended -regex '\./[0-9]+(\.[0-9]+)?' \
          ! -name 0 -printf '%f ' 2>/dev/null)
  [ -n "$EXTRA" ] && fail "time directories already present ($EXTRA); age-guard precondition broken"
fi

# ---- environment. `set +u` is REQUIRED: the OpenFOAM bashrc reads unset variables and under
# ---- `set -u` aborts the shell with status 1, silently if its stderr is discarded.
set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc > log.env 2>&1; ENV_RC=$?; set -u
{ [ "$ENV_RC" -ne 0 ] || ! command -v rhoSimpleFoam >/dev/null 2>&1; } && { cat log.env; fail "OpenFOAM env did not load (rc=$ENV_RC)"; }

# ---- assert the registered dictionaries; NEVER rewrite them with foamDictionary, which
# ---- inlines every #include and froze a stale forces dict into this case once already.
grep -qE '^application +rhoSimpleFoam;' system/controlDict || fail "application is not rhoSimpleFoam"
# purgeWrite must be AT LEAST 2, not exactly 2. The gate's intent is "never keep fewer than two
# checkpoints"; MORE retention strictly dominates it. Hardcoding equality encoded the
# restart-economy assumption as law and refused a legitimate DIAGNOSTIC run that needed to keep
# every early field -- the same defect the purgeWrite lesson names, written into the guard itself.
# AND purgeWrite 0 MEANS KEEP EVERY TIME DIRECTORY in OpenFOAM -- it is MAXIMUM retention, not
# minimum. The numeric ordering and the semantic ordering disagree at exactly one value, and it is
# the value a diagnostic run is most likely to use. `-ge 2` refused it, which left the very hole
# the previous fix's own commit message described.
PW=$(grep -oE '^purgeWrite +[0-9]+;' system/controlDict | grep -oE '[0-9]+')
{ [ -n "$PW" ] && { [ "$PW" -eq 0 ] || [ "$PW" -ge 2 ]; }; } \
  || fail "purgeWrite is ${PW:-unset}; must be 0 (keep all) or >= 2"
grep -q  '#include'                     system/controlDict || fail "controlDict lost its #include"
# THE CLOSURE IS REGISTERED, NOT HARD-CODED. Section C.6 registers Spalart-Allmaras as PRIMARY
# and k-omega SST as the REGISTERED SECOND CLOSURE, and ADDENDUM 12's exhaustion clause climbs
# to SST. A guard that names one model by literal REFUSES the other: the launcher would have
# blocked the very successor its own act registers. The registered closure is therefore read
# from the environment, defaulted to the primary, checked against a closed set, ASSERTED against
# the dictionary that will run, and LOGGED -- so LAUNCH.log names what actually ran instead of
# leaving its reader to assume the default.
CLOSURE="${CLOSURE:-SpalartAllmaras}"
case "$CLOSURE" in
  SpalartAllmaras|kOmegaSST) ;;
  *) fail "CLOSURE=$CLOSURE is not a closure section C.6 registers (SpalartAllmaras, kOmegaSST)";;
esac
grep -qE "RASModel +${CLOSURE};" constant/turbulenceProperties \
  || fail "constant/turbulenceProperties does not carry RASModel $CLOSURE"
echo "closure: $CLOSURE  (ASSERTED against constant/turbulenceProperties, not assumed)"
# `transonic yes` is the REGISTERED physics and is asserted for every graded run. A registered
# DIAGNOSTIC that deliberately turns it off must declare itself, exactly as the runner requires a
# `purge_waiver` for purgeWrite 0 -- A DECLARED EXCEPTION, NEVER A SILENT ONE. Without the
# declaration this refuses, which is what blocked the A10.4 probe until it was declared.
if grep -qE 'transonic +no;' system/fvSolution.startup 2>/dev/null; then
  [ "${TRANSONIC_DIAGNOSTIC:-}" = "yes" ] \
    || fail "system/fvSolution.startup sets 'transonic no' but TRANSONIC_DIAGNOSTIC=yes was not declared"
  echo "*** TRANSONIC DIAGNOSTIC: stage 1 runs with 'transonic no'. THIS IS NOT THE REGISTERED"
  echo "*** PHYSICS AT M 0.85 AND ITS ANSWER IS NEVER GRADED (ADDENDUM 10.4). Stage 2 restores the"
  echo "*** registered dictionaries md5-identically, so no graded answer can come from this branch."
  grep -qE 'transonic +yes;' system/fvSolution || fail "the GRADED fvSolution must still be transonic yes"
else
  grep -qE 'transonic +yes;' system/fvSolution || fail "transonic is not yes"
fi
grep -qE 'div\(phid,p\) +Gauss upwind;' system/fvSchemes  || fail "div(phid,p) is not the corrected unbounded form"
for K in rhoInf Aref lRef CofR magUInf; do
  foamDictionary -entry "functions/forceCoeffs/$K" system/controlDict >/dev/null 2>&1 \
    || fail "forceCoeffs missing the registered entry $K"
done

if [ -n "$ENDTIME_ARG" ] && [ "$RESUME" = "no" ]; then
  sed -i -E "s/^([[:space:]]*endTime[[:space:]]+)[0-9.eE+-]+;/\1${ENDTIME_ARG};/" system/controlDict
fi
ET=$(grep -oE '^[[:space:]]*endTime[[:space:]]+[0-9]+;' system/controlDict | grep -oE '[0-9]+')
[ -n "$ET" ] || fail "could not read endTime"
[ -f system/controlDict.registered ] || cp system/controlDict system/controlDict.registered
CD_MD5=$(md5sum < system/controlDict.registered)
SCH_MD5=$(md5sum < system/fvSchemes)
SOL_MD5=$(md5sum < system/fvSolution)
cp system/fvSchemes  system/fvSchemes.registered
cp system/fvSolution system/fvSolution.registered
echo "registered endTime=$ET  ramp=$STARTUP_ITERS iterations"

set_endtime () {
  sed -i -E "s/^([[:space:]]*endTime[[:space:]]+)[0-9]+;/\1${1};/" system/controlDict
  grep -qE "^[[:space:]]*endTime[[:space:]]+${1};" system/controlDict || fail "endTime -> $1 did not read back"
  echo "endTime set to $1 (read back OK)"
}
# The progress line goes to STDERR, never stdout: `RC=$(run_solver ...)` captures stdout, so an
# echo here becomes part of RC. That defect let a FAILED stage 1 fall through into stage 2 --
# `[ "$RC" -ne 0 ]` cannot compare a multi-line string and the guard silently did not fire.
run_solver () {
  echo "--- mpirun -np $RANKS rhoSimpleFoam -parallel  ($1)" >&2
  mpirun -np "$RANKS" rhoSimpleFoam -parallel >> log.rhoSimpleFoam 2>&1
  echo "$?"
}

RC=0
# ---- STAGE 0: potentialFoam initialisation (ADDENDUM 5, the A3.4 rung, fired on the supervisor's
# ---- ruling). The violence comes from solving a pressure equation on a uniform freestream WITH A
# ---- WING-BODY IN IT: that field is not merely inaccurate, it is inconsistent with the geometry,
# ---- and the first solve must invent the whole flow at once. potentialFoam produces a
# ---- divergence-free velocity field that already goes AROUND the aircraft.
# ---- REGISTERED PREDICTION, ABLE TO REFUTE THE REASON FOR FIRING: with this initialisation
# ---- stage 1's first pressure solve COMPLETES. If it still faults before emitting a line, the
# ---- hypothesis is wrong, the rung was mis-aimed, and the ladder climbs elsewhere.
if [ "$RESUME" = "no" ] && [ "${POTENTIAL_INIT:-yes}" = "yes" ]; then
  [ -f system/fvSolution.potential ] || fail "no system/fvSolution.potential"
  [ -f system/fvSchemes.potential ]  || fail "no system/fvSchemes.potential"
  echo "=== STAGE 0: potentialFoam initialisation ==="
  cp system/fvSchemes.potential  system/fvSchemes
  cp system/fvSolution.potential system/fvSolution
  mpirun -np "$RANKS" potentialFoam -parallel -writePhi >> log.potentialFoam 2>&1
  RC0=$?
  echo "STAGE 0 rc=$RC0"
  case "$RC0" in ''|*[!0-9]*) fail "stage 0 returned a non-numeric rc";; esac
  if [ "$RC0" -ne 0 ]; then
    echo "RC=$RC0" > RC.txt
    echo "STAGE 0 FAILED -- no ramp, no graded stage. potentialFoam could not initialise the field."
    exit "$RC0"
  fi
  # a zero exit is not evidence of output: the initialised U must be back in processor*/0
  grep -q 'End' log.potentialFoam || fail "stage 0 exited 0 but log.potentialFoam has no End line"
  echo "STAGE 0a complete: divergence-free U written into processor*/0"

  # ---- STAGE 0b: ISENTROPIC THERMODYNAMIC STATE (ADDENDUM 7). potentialFoam sets U and phi and
  # ---- NO thermodynamic state, so stage 1 previously began with a developed velocity field on a
  # ---- UNIFORM 310 K: the energy equation had to invent the whole thermal field at once
  # ---- (enthalpy initial residual 0.999999999957) and by iteration 2 the temperature had been
  # ---- driven through BOTH limiter bounds. AN INITIAL CONDITION MUST BE SELF-CONSISTENT ACROSS
  # ---- ALL FIELDS, NOT JUST THE ONE THAT FAILED LAST.
  python3 "$ISEN_TOOL" --case . --Tinf "$T_INF" --pinf "$P_INF" --Minf "$M_INF" \
      >> log.isentropic_init 2>&1 || fail "isentropic initialisation failed"
  grep -q 'wrote T, p, rho over' log.isentropic_init || fail "stage 0b wrote no fields"
  echo "STAGE 0b complete: $(grep -h 'wrote T, p, rho over' log.isentropic_init | tail -1)"
  grep -h 'range' log.isentropic_init | tail -2
fi

if [ "$RESUME" = "no" ] && [ "$STARTUP_ITERS" -gt 0 ]; then
  echo "=== STAGE 1: ramp, $STARTUP_ITERS iterations, first-order, heavy relaxation ==="
  cp system/fvSchemes.startup  system/fvSchemes
  cp system/fvSolution.startup system/fvSolution
  set_endtime "$STARTUP_ITERS"
  RC=$(run_solver "stage 1")
  echo "STAGE 1 rc=$RC"
  # RESTORE THE REGISTERED DICTIONARIES ON EVERY EXIT PATH, NOT ONLY ON SUCCESS. Stage 1 copies
  # the ramp dictionaries over fvSchemes/fvSolution; if it FAILS, stage 2 never runs and the case
  # is left holding the RAMP dictionaries under the registered names. A resume would then continue
  # silently on first-order schemes -- and the launcher's own "transonic yes" assertion would read
  # the ramp file and refuse, which is how this was found.
  cp system/fvSchemes.registered  system/fvSchemes
  cp system/fvSolution.registered system/fvSolution
  [ "$(md5sum < system/fvSchemes)"  = "$SCH_MD5" ] || fail "fvSchemes restore after stage 1 is not byte-identical"
  [ "$(md5sum < system/fvSolution)" = "$SOL_MD5" ] || fail "fvSolution restore after stage 1 is not byte-identical"
  echo "registered dictionaries restored after stage 1 (md5-identical), whatever its rc"
  case "$RC" in ''|*[!0-9]*) fail "stage 1 returned a non-numeric rc (\"$RC\") -- refusing to guess";; esac
  if [ "$RC" -ne 0 ]; then
    echo "RC=$RC" > RC.txt
    echo "STAGE 1 FAILED -- STAGE 2 NOT ENTERED. The graded schemes are never run on a failed ramp."
    exit "$RC"
  fi
fi

# ---- ASSERT THE HANDOVER ITSELF. A ZERO EXIT IS NOT EVIDENCE OF OUTPUT. Stage 1 could exit 0
# ---- having written no time directory, and `startFrom latestTime` would then resolve to 0 and
# ---- silently restart stage 2 from the uniform freestream -- which is exactly the void reading
# ---- this act already produced once. Verification must BIND the action, not accompany it.
if [ "$RESUME" = "no" ] && [ "$STARTUP_ITERS" -gt 0 ]; then
  HANDOVER=$(find processor0 -maxdepth 1 -type d -regextype posix-extended \
             -regex '.*/[0-9]+(\.[0-9]+)?$' -printf '%f\n' 2>/dev/null | sort -g | tail -1)
  [ -n "${HANDOVER:-}" ] || fail "stage 1 exited 0 but processor0 holds NO time directory at all"
  [ "$HANDOVER" != "0" ] || fail "stage 1 exited 0 but the latest time in processor0 is still 0 -- nothing was handed over, and stage 2 would silently restart from the uniform freestream"
  MISSING=0
  for d in processor*; do [ -d "$d/$HANDOVER" ] || MISSING=$((MISSING+1)); done
  [ "$MISSING" -eq 0 ] || fail "stage-1 handover time $HANDOVER is missing from $MISSING processor tree(s)"
  echo "HANDOVER ASSERTED: stage 1 wrote t=$HANDOVER in every one of $(ls -d processor* | wc -l) processor trees; startFrom latestTime will resolve to it"
fi

echo "=== STAGE 2: REGISTERED schemes restored, graded answer produced here ==="
cp system/fvSchemes.registered  system/fvSchemes
cp system/fvSolution.registered system/fvSolution
[ "$(md5sum < system/fvSchemes)"  = "$SCH_MD5" ] || fail "fvSchemes restore is not byte-identical"
[ "$(md5sum < system/fvSolution)" = "$SOL_MD5" ] || fail "fvSolution restore is not byte-identical"
cp system/controlDict.registered system/controlDict
[ "$(md5sum < system/controlDict)" = "$CD_MD5" ] || fail "controlDict restore is not byte-identical"
echo "registered dictionaries restored, all three md5-identical"
RC=$(run_solver "stage 2")
case "$RC" in ''|*[!0-9]*) fail "stage 2 returned a non-numeric rc (\"$RC\")";; esac
echo "RC=$RC" > RC.txt
echo "=== END $(date -u +%FT%TZ) rc=$RC"
exit "$RC"
