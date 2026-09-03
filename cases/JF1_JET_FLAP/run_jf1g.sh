#!/usr/bin/env bash
# =============================================================================
# JF1G -- GRID CONVERGENCE STUDY AT C_mu = 0.1, alpha = 0, tau = 30 deg.
#
# Registration: verification/campaign/JF1G_GRID_CONVERGENCE_PREREGISTRATION.md
#   frozen 038f4bca160af8bc201f93805cb841a30236a28c, blob 0b9476598ef4467d...
#
# ONE FAMILY, ONE SCRIPT, ONE TOPOLOGY.  Levels C1/C2/C3/C4 at r = 1.5, emitted
# by cases/JF1_JET_FLAP/build_jf1.py with --n-rad PASSED EXPLICITLY.
#
# ##  THE --n-rad ARGUMENT IS LOAD-BEARING AND MUST NEVER BE DROPPED.  ##
# build_jf1.py's DEFAULT --n-rad 0 solves the wall-normal count from the growth
# cap, which moves it 98 -> 100 -> 103 across scale 1.0 / 1.5 / 2.25 while the
# tangential count moves 408 -> 612 -> 919.  That is a refinement ratio of 1.02
# in one direction and 1.5 in the other: a triple built that way measures the
# mixture, not the discretisation (registration section 1).  Passing --n-rad 98
# gives 98 -> 147 -> 220.  The similarity checker refuses on the cell ratio, but
# this comment is here so nobody has to be caught by it twice.
#
# rc DISCIPLINE: the return code is captured INSIDE this wrapper by its own EXIT
# trap.  `setsid timeout cmd` returns 0 for every outcome, so an rc taken AROUND
# a setsid line is not the solver's rc (lab memory: "setsid parent returns zero").
#
# ARTIFACT DISCIPLINE: every artifact is written under RUN_ROOT and retained.
# NOTHING goes to ${TMPDIR:-/tmp}.
#
# STATUS FILE NAME: RUN_STATUS.*.txt, NOT STATUS.* -- scripts/queue_runner.py:496
# truncates any file named STATUS.* in the launch cwd unconditionally.
# =============================================================================
set -u
set -o pipefail

CASE_DIR="/home/ubuntu/Certonomous/cases/JF1_JET_FLAP"
REPO="/home/ubuntu/Certonomous"
PREREG_PATH="verification/campaign/JF1G_GRID_CONVERGENCE_PREREGISTRATION.md"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

FREEZE_COMMIT="038f4bca160af8bc201f93805cb841a30236a28c"
FREEZE_BLOB="0b9476598ef4467dae3f9bcc0e4cf113254bd8e0"

# The frozen section 5.2 jet constants for C_mu = 0.1, verified below against
# the formulae rather than trusted as a transcription.
CMU="0.1"
VJ="31.622777"; KJET="1.5000000000e-01"; OMJET="2020.305089"

RANKS=1
LEVEL=""; PASS=""; PREFLIGHT=0; PREREG_COMMIT=""
for a in "$@"; do
  case "$a" in
    --prereg-commit=*) PREREG_COMMIT="${a#*=}" ;;
    --level=*)         LEVEL="${a#*=}" ;;
    --pass=*)          PASS="${a#*=}" ;;
    --preflight)       PREFLIGHT=1 ;;
    *) echo "REFUSED: unrecognised argument '$a'"; exit 3 ;;
  esac
done

# --- the frozen section 2 ladder table, VERBATIM ------------------------------
case "${LEVEL}" in
  C1) SCALE="1.000";  CELLS_EXPECT=39984  ;;
  C2) SCALE="1.500";  CELLS_EXPECT=89964  ;;
  C3) SCALE="2.250";  CELLS_EXPECT=202180 ;;
  C4) SCALE="3.375";  CELLS_EXPECT=455456 ;;
  *) echo "REFUSED: --level must be C1 C2 C3 or C4 (frozen section 2); got '${LEVEL}'"; exit 3 ;;
esac
NRAD=98   # NEVER defaulted.  See the header.

# --- the frozen section 8 caps, per level per pass ----------------------------
# Pass 0: endTime 8000, residualControl 1e-6, LABEL diagnostic (scores nothing).
# Pass 1: endTime 30000, residualControl 1e-8, the graded pass.
case "${PASS}" in
  0) ENDTIME=8000
     RESTOL="1e-06"
     case "${LEVEL}" in
       C1) CAP_CORE_MIN=40.0  ;; C2) CAP_CORE_MIN=80.0  ;;
       C3) CAP_CORE_MIN=170.0 ;; C4) CAP_CORE_MIN=380.0 ;;
     esac ;;
  1) ENDTIME=30000
     RESTOL="1e-08"
     case "${LEVEL}" in
       C1) CAP_CORE_MIN=110.0 ;; C2) CAP_CORE_MIN=240.0 ;;
       C3) CAP_CORE_MIN=520.0 ;; C4) CAP_CORE_MIN=1200.0 ;;
     esac ;;
  *) echo "REFUSED: --pass must be 0 or 1 (frozen section 4); got '${PASS}'"; exit 3 ;;
esac
# RANKS = 1, so the wall allowance in seconds is the cap x 60.
WALL_ALLOWANCE_S=$(awk -v c="${CAP_CORE_MIN}" 'BEGIN{printf "%d", c*60}')

CASE_ID="JF1G_P${PASS}_${LEVEL}_CMU010_A0"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/${CASE_ID}"
STATUS="${CASE_DIR}/RUN_STATUS.${CASE_ID}.guard.txt"

RC=99
STAGE="init"
CELLS_EMITTED="not-reached"
YPLUS_ROWS="not-reached"
FREEZE_CHECK="NOT REACHED -- refused at or before the freeze guard"
T_START=$(date +%s)

finish() {
  RC=$?
  local t_end elapsed core_min
  t_end=$(date +%s); elapsed=$(( t_end - T_START ))
  core_min=$(awk -v s="$elapsed" -v r="$RANKS" 'BEGIN{printf "%.4f", s*r/60.0}')
  # A GUARD FAILURE MUST NOT CREATE THE RUN ROOT: if it did, the age guard would
  # refuse every later attempt and a refusal at zero compute would permanently
  # block the level.
  if [ "${STAGE}" = "init" ] || [ "${STAGE}" = "guard" ] || [ "${STAGE}" = "foamenv" ]; then
    STATUS="${CASE_DIR}/RUN_STATUS.${CASE_ID}.guard.txt"
  else
    mkdir -p "$RUN_ROOT" 2>/dev/null || true
    STATUS="${RUN_ROOT}/RUN_STATUS.${CASE_ID}.txt"
  fi
  {
    echo "case_id            ${CASE_ID}"
    echo "study              JF1G grid convergence, C_mu_jet 0.1, alpha 0 deg, tau 30 deg"
    echo "level              ${LEVEL}   scale ${SCALE}   n_rad ${NRAD} (EXPLICIT, never defaulted)"
    echo "cells_expected     ${CELLS_EXPECT}"
    echo "cells_emitted      ${CELLS_EMITTED}"
    echo "pass               ${PASS}"
    if [ "${PASS}" = "0" ]; then
      echo "label              diagnostic -- SCORES NOTHING.  No PASS, no GATE REACHED,"
      echo "                   no observed order, no GCI may be quoted or implied from"
      echo "                   this run (registration section 4)."
    else
      echo "label              graded -- gates G1..G7 of the registration apply"
    fi
    echo "endTime            ${ENDTIME}"
    echo "residualControl    ${RESTOL} on p U k omega"
    echo "rc                 ${RC}"
    echo "stage_at_exit      ${STAGE}"
    echo "utc_start          $(date -u -d "@${T_START}" +%Y-%m-%dT%H:%M:%SZ)"
    echo "utc_end            $(date -u -d "@${t_end}" +%Y-%m-%dT%H:%M:%SZ)"
    echo "wall_s             ${elapsed}"
    echo "ranks              ${RANKS}"
    echo "core_min_MEASURED  ${core_min}"
    echo "cap_core_min       ${CAP_CORE_MIN}"
    echo "prereg_commit      ${PREREG_COMMIT}"
    echo "prereg_blob_pinned ${FREEZE_BLOB}"
    echo "freeze_commit      ${FREEZE_COMMIT}"
    echo "prereg_check       ${FREEZE_CHECK}"
    echo "yplus_data_rows    ${YPLUS_ROWS}"
    echo "run_root           ${RUN_ROOT}"
  } > "${STATUS}"
  exit "${RC}"
}
trap finish EXIT

# --- guards, FAIL-CLOSED ------------------------------------------------------
STAGE="guard"
[ -n "${PREREG_COMMIT}" ] || { echo "REFUSED: --prereg-commit=<40hex> is required"; exit 3; }
[ ${#PREREG_COMMIT} -eq 40 ] || { echo "REFUSED: prereg commit is not 40 hex"; exit 3; }
case "${PREREG_COMMIT}" in
  *[!0-9a-f]*) echo "REFUSED: prereg commit is not lowercase hex"; exit 3 ;;
esac
[ "${PREREG_COMMIT}" = "${FREEZE_COMMIT}" ] \
  || { echo "REFUSED: prereg commit ${PREREG_COMMIT} is not the freeze commit ${FREEZE_COMMIT}"; exit 3; }
git -C "${REPO}" cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "REFUSED: prereg commit does not exist"; exit 3; }
git -C "${REPO}" cat-file -e "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null \
  || { echo "REFUSED: ${PREREG_PATH} absent at ${PREREG_COMMIT}"; exit 3; }
# THE BLOB CHECK -- rule 2, "verify the frozen file IS the file that ran".
# Fail-closed: an empty rev-parse result is a REFUSAL, never a pass.
GOT_BLOB="$(git -C "${REPO}" rev-parse "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null || true)"
[ -n "${GOT_BLOB}" ] || { echo "REFUSED: could not read the prereg blob sha"; exit 3; }
[ "${GOT_BLOB}" = "${FREEZE_BLOB}" ] \
  || { echo "REFUSED: prereg blob ${GOT_BLOB} != frozen blob ${FREEZE_BLOB}"; exit 3; }
WT_BLOB="$(git -C "${REPO}" hash-object "${REPO}/${PREREG_PATH}" 2>/dev/null || true)"
[ "${WT_BLOB}" = "${FREEZE_BLOB}" ] \
  || { echo "REFUSED: working-tree ${PREREG_PATH} (${WT_BLOB}) is not the frozen blob"; exit 3; }
FREEZE_CHECK="VERIFIED -- commit is the freeze commit; document present at it; its blob and the working-tree copy both hash to the pinned blob"

# The substituted jet constants must be REPRODUCED from the registered formulae,
# never merely transcribed.
awk -v cmu="${CMU}" -v vj="${VJ}" -v kj="${KJET}" -v om="${OMJET}" 'BEGIN{
    Uinf=10.0; hoc=0.005; I=0.01; lj=0.07*0.005; Cmt=0.09; kinf=1.5e-04; ominf=5.0;
    v = Uinf*sqrt(cmu/(2*hoc));
    k = 1.5*(I*v)^2; if (k < kinf) k = kinf;
    o = sqrt(k)/((Cmt^0.25)*lj); if (o < ominf) o = ominf;
    bad = 0;
    if ((v-vj)/v >  1e-6 || (v-vj)/v < -1e-6) { printf "V_j mismatch: derived %.9f vs table %s\n", v, vj; bad=1 }
    if ((k-kj)/k >  1e-9 || (k-kj)/k < -1e-9) { printf "k_jet mismatch: derived %.12e vs table %s\n", k, kj; bad=1 }
    if ((o-om)/o >  1e-8 || (o-om)/o < -1e-8) { printf "omega_jet mismatch: derived %.9f vs table %s\n", o, om; bad=1 }
    exit bad
}' || { echo "REFUSED: substituted jet constants do not reproduce the frozen section 5.2 formulae"; exit 3; }

# AGE GUARD (rule 4): never launch into a tree that already holds an answer.
[ -e "${RUN_ROOT}" ] && { echo "REFUSED: run root already exists: ${RUN_ROOT}"; exit 3; }

for f in "${CASE_DIR}/case_blown/0/U.template" \
         "${CASE_DIR}/case_blown/0/k.template" \
         "${CASE_DIR}/case_blown/0/omega.template" \
         "${CASE_DIR}/case_blown/0/nut" \
         "${CASE_DIR}/case_blown/0/p" \
         "${CASE_DIR}/case_blown/system/controlDict" \
         "${CASE_DIR}/case/system/fvSchemes" \
         "${CASE_DIR}/case/system/fvSolution" \
         "${CASE_DIR}/case/constant/transportProperties" \
         "${CASE_DIR}/case/constant/turbulenceProperties" \
         "${CASE_DIR}/build_jf1.py" ; do
  [ -f "$f" ] || { echo "REFUSED: required input absent: $f"; exit 3; }
done
[ -f "${FOAM_BASHRC}" ] || { echo "REFUSED: OpenFOAM bashrc absent"; exit 3; }

# The environment step is PART of the preflight: the OpenFOAM bashrc expands
# unset variables and `set -u` exits a non-interactive shell on that.  A
# preflight that stops short of the environment is not a preflight.
STAGE="foamenv"
set +u
# shellcheck disable=SC1090
source "${FOAM_BASHRC}" "" > /dev/null 2>&1 || true
set -u
command -v simpleFoam > /dev/null 2>&1 || { echo "REFUSED: simpleFoam not on PATH"; exit 3; }
command -v checkMesh  > /dev/null 2>&1 || { echo "REFUSED: checkMesh not on PATH"; exit 3; }

if [ "${PREFLIGHT}" = "1" ]; then
  echo "PREFLIGHT OK -- guards pass, OpenFOAM environment live, zero compute"
  echo "  case_id : ${CASE_ID}"
  echo "  level   : ${LEVEL}  scale ${SCALE}  n_rad ${NRAD}  cells_expected ${CELLS_EXPECT}"
  echo "  pass    : ${PASS}   endTime ${ENDTIME}  residualControl ${RESTOL}"
  echo "  freeze  : ${FREEZE_COMMIT} blob ${FREEZE_BLOB} (commit, blob and worktree verified)"
  echo "  cap     : ${CAP_CORE_MIN} core-min (${WALL_ALLOWANCE_S} wall s at ${RANKS} rank)"
  exit 0
fi

# --- stage --------------------------------------------------------------------
STAGE="stage"
mkdir -p "${RUN_ROOT}/0" "${RUN_ROOT}/system" "${RUN_ROOT}/constant"
cp "${CASE_DIR}/case/system/fvSchemes"                "${RUN_ROOT}/system/fvSchemes"
cp "${CASE_DIR}/case/system/fvSolution"               "${RUN_ROOT}/system/fvSolution"
cp "${CASE_DIR}/case_blown/system/controlDict"        "${RUN_ROOT}/system/controlDict"
cp "${CASE_DIR}/case/constant/transportProperties"    "${RUN_ROOT}/constant/transportProperties"
cp "${CASE_DIR}/case/constant/turbulenceProperties"   "${RUN_ROOT}/constant/turbulenceProperties"
cp "${CASE_DIR}/case_blown/0/nut"                     "${RUN_ROOT}/0/nut"
cp "${CASE_DIR}/case_blown/0/p"                       "${RUN_ROOT}/0/p"

VJX=$(awk -v v="${VJ}" 'BEGIN{printf "%.8f", v*cos(3.14159265358979323846/6.0)}')
VJY=$(awk -v v="${VJ}" 'BEGIN{printf "%.8f", -v*sin(3.14159265358979323846/6.0)}')
sed -e "s|@VJX@|${VJX}|" -e "s|@VJY@|${VJY}|" \
    "${CASE_DIR}/case_blown/0/U.template"     > "${RUN_ROOT}/0/U"
sed -e "s|@KJET@|${KJET}|"      "${CASE_DIR}/case_blown/0/k.template"     > "${RUN_ROOT}/0/k"
sed -e "s|@OMEGAJET@|${OMJET}|" "${CASE_DIR}/case_blown/0/omega.template" > "${RUN_ROOT}/0/omega"
if grep -l '@[A-Z]*@' "${RUN_ROOT}"/0/U "${RUN_ROOT}"/0/k "${RUN_ROOT}"/0/omega > /dev/null 2>&1; then
  echo "SUBSTITUTION INCOMPLETE: an @TOKEN@ survived into a 0/ field"; exit 8
fi

# --- endTime and residualControl for this pass --------------------------------
# =============================================================================
# CLASS FIX, 2026-09-03, cfd lab-lane on cfd-supervisor's instruction, after the
# rc=9 triage recorded below.  THE INSTANCE WAS A DELIMITER; THE CLASS IS A BLIND
# GUARD, AND THE CLASS IS WHAT IS FIXED HERE.
#
# THE INSTANCE, MEASURED.  The residualControl substitution used `|` as the s///
# DELIMITER while its own alternation `(p|U|k|omega)` carries four UNESCAPED `|`.
# sed read the command as s|^( +)(p| ... | with `U` as the replacement and `k` as
# a flag, died with `sed: -e expression #1, char 13: unknown option to `s'`, rc=1,
# AND DID NOT EDIT THE FILE.  On pass 1 the value check then correctly REFUSED at
# rc=9, stage `dicts`, 0 wall s, 0 solver compute -- which is how the defect
# finally surfaced, preserved at
# verification/runs/JF1_jet_flap/JF1G_P1_C1_CMU010_A0.attempt1_FAILED_2026-09-03T190419Z_PRESERVED/.
# Only the DELIMITER changed (`@` for `|`); the regex, the capture groups, the
# replacement and the -E flag are character-for-character what they were.
#
# THE CLASS, AND WHY THE INSTANCE HID FOR TWO DAYS.  BOTH guards below verified
# THE VALUE and only the value.  A value check cannot distinguish "the
# substitution RAN and set X" from "the substitution NEVER RAN and X was already
# the shipped template default" -- and BOTH substitutions here are blind in
# exactly that way ON PASS 0, because both pass-0 targets EQUAL the template:
#     endTime          pass-0 target 8000  == case_blown/system/controlDict:21
#     residualControl  pass-0 target 1e-06 == case/system/fvSolution:46-49
# So every pass-0 run printed no complaint while substituting nothing at all, and
# the guard was blindest exactly where the desired value equals the default.
# This is docs/FAIL_OPEN_GATE_AUDIT.md section 28's caller-side defect arriving in
# a LAUNCHER rather than in a grader, which is why the fix below is a helper
# applied to BOTH sites and not a one-line delimiter change.
#
# PASS 0 IS NOT CONTAMINATED, CHECKED ON DISK RATHER THAN ASSUMED: the staged
# system/fvSolution of JF1G_P0_C1, P0_C2 and P0_C3 each read p/U/k/omega 1e-06 and
# their controlDict reads endTime 8000, which is exactly what the frozen
# registration prescribes for pass 0.  The broken sed was inert there, not wrong.
# =============================================================================
STAGE="dicts"

# subst_or_refuse <file> <sed-expression> <expected-match-count> <label>
#
# Closes the class on three axes, and the middle one is the new one:
#   (1) sed's EXIT STATUS is captured into a variable ON ITS OWN LINE and a
#       non-zero value REFUSES.  The delimiter collision exited 1 and NOTHING
#       LOOKED.  This clause alone would have caught it on day one.
#   (2) the number of lines the pattern actually MATCHES is counted BEFORE the
#       file is touched, and must equal the expected count.  This is the clause a
#       value check cannot have: it fires on an expression that compiles and
#       matches NOTHING even when the desired value is already sitting in the
#       file, so the guard can now see its own absence on pass 0.
#   (3) the value is verified afterwards by the caller, exactly as before -- the
#       old check is KEPT, not replaced.
# Writes through a temp file and installs with mv, so a refusal never leaves a
# half-edited dictionary behind.  No exit status is chained: each is assigned to
# a variable on the line after the command that produced it, because a guard
# folded into an && chain is a guard that a broken earlier link silently skips.
subst_or_refuse() {
    local target="$1" expr="$2" want="$3" what="$4"
    local tmp_m tmp_o rc n
    tmp_m="${target}.matchcount.$$"
    tmp_o="${target}.subst.$$"

    sed -n -E -e "${expr}p" "${target}" > "${tmp_m}"
    rc=$?
    if [ "${rc}" -ne 0 ]; then
        rm -f "${tmp_m}" "${tmp_o}"
        echo "REFUSED: the ${what} substitution EXPRESSION FAILED, sed rc=${rc}."
        echo "         Nothing was written and no value check was consulted: a guard"
        echo "         that reads only the value cannot tell a no-op from a success"
        echo "         (docs/FAIL_OPEN_GATE_AUDIT.md section 28)."
        exit 9
    fi

    n=$(wc -l < "${tmp_m}")
    rm -f "${tmp_m}"
    if [ "${n}" -ne "${want}" ]; then
        rm -f "${tmp_o}"
        echo "REFUSED: the ${what} substitution MATCHED ${n} line(s), expected ${want}."
        echo "         The expression compiled but did not reach what it was written"
        echo "         for.  THIS REFUSAL FIRES EVEN WHEN THE DESIRED VALUE IS ALREADY"
        echo "         PRESENT, which is precisely the pass-0 case a value check is"
        echo "         structurally blind to."
        exit 9
    fi

    sed -E -e "${expr}" "${target}" > "${tmp_o}"
    rc=$?
    if [ "${rc}" -ne 0 ]; then
        rm -f "${tmp_o}"
        echo "REFUSED: the ${what} substitution FAILED on the write pass, sed rc=${rc}."
        exit 9
    fi

    mv "${tmp_o}" "${target}"
    rc=$?
    if [ "${rc}" -ne 0 ]; then
        rm -f "${tmp_o}"
        echo "REFUSED: could not install the substituted ${what} file, mv rc=${rc}."
        exit 9
    fi
}

subst_or_refuse "${RUN_ROOT}/system/controlDict" \
                "s@^endTime .*@endTime         ${ENDTIME};@" 1 "endTime"
grep -qE "^endTime +${ENDTIME};" "${RUN_ROOT}/system/controlDict" \
  || { echo "REFUSED: endTime ${ENDTIME} did not take in controlDict"; exit 9; }

subst_or_refuse "${RUN_ROOT}/system/fvSolution" \
                "s@^( +)(p|U|k|omega)( +)1e-0[0-9];@\1\2\3${RESTOL};@" 4 "residualControl"
for fld in p U k omega; do
  grep -qE "^ +${fld} +${RESTOL};" "${RUN_ROOT}/system/fvSolution" \
    || { echo "REFUSED: residualControl ${RESTOL} did not take for ${fld}"; exit 9; }
done

# --- mesh, WITH THE SLOT AS A FLOW PATCH AND --n-rad EXPLICIT -----------------
STAGE="mesh"
python3 "${CASE_DIR}/build_jf1.py" \
    --out "${RUN_ROOT}" --level "${LEVEL}" --slot-type patch \
    --scale "${SCALE}" --n-rad "${NRAD}" \
    > "${RUN_ROOT}/log.build_jf1" 2>&1 \
  || { echo "MESH BUILD FAILED"; exit 4; }

# The emitted cell count must be the frozen section 2 number.  This is the cheap
# arithmetic clause that catches a dropped --n-rad: under the default the C2
# count would read 61200, not 89964.
CELLS_EMITTED=$(grep -oE 'CELLS +=.*= [0-9]+' "${RUN_ROOT}/log.build_jf1" | grep -oE '[0-9]+$')
[ "${CELLS_EMITTED}" = "${CELLS_EXPECT}" ] \
  || { echo "REFUSED: level ${LEVEL} emitted ${CELLS_EMITTED} cells, frozen section 2 says ${CELLS_EXPECT}"; exit 10; }

STAGE="checkMesh"
checkMesh -case "${RUN_ROOT}" > "${RUN_ROOT}/log.checkMesh" 2>&1 || true
grep -q "^Mesh OK" "${RUN_ROOT}/log.checkMesh" \
  || { echo "checkMesh did not print Mesh OK"; exit 5; }

# --- age guard on the fields, re-asserted after staging -----------------------
# 0/ is touched LAST before the solver so every endTime field must be newer.
STAGE="touch0"
touch "${RUN_ROOT}"/0/*

# --- solve --------------------------------------------------------------------
STAGE="simpleFoam"
timeout --signal=TERM --kill-after=60 "${WALL_ALLOWANCE_S}" \
    simpleFoam -case "${RUN_ROOT}" > "${RUN_ROOT}/log.simpleFoam" 2>&1
SOLVER_RC=$?
echo "solver_rc ${SOLVER_RC}" > "${RUN_ROOT}/SOLVER_RC.txt"

YPLUS_DAT="${RUN_ROOT}/postProcessing/yPlus/0/yPlus.dat"
# `grep -c -v` is NOT used: grep exits 1 on a zero count, so `$(grep -c ... ||
# echo 0)` yields the two-line string "0\n0" on exactly the case this exists to
# detect.
if [ -f "${YPLUS_DAT}" ]; then
  YPLUS_ROWS=$(grep -v '^#' "${YPLUS_DAT}" | wc -l | tr -d ' ')
else
  YPLUS_ROWS=0
fi

if [ ${SOLVER_RC} -eq 124 ] || [ ${SOLVER_RC} -eq 137 ]; then
  echo "CAP REACHED: solver killed at the ${WALL_ALLOWANCE_S} s wall allowance"
  echo "(${CAP_CORE_MIN} core-min at ${RANKS} rank).  The cap is NEVER raised"
  echo "(CLAUDE.md rule 12); an overrun stops the run."
  exit 6
fi
[ ${SOLVER_RC} -eq 0 ] || { echo "SOLVER FAILED rc=${SOLVER_RC}"; exit 7; }

# --- post ---------------------------------------------------------------------
STAGE="post"
{
  echo "== ${CASE_ID} -- JF1G READOUT, level ${LEVEL}, pass ${PASS} =="
  if [ "${PASS}" = "0" ]; then
    echo "== LABEL diagnostic: THIS RUN SCORES NOTHING.  No PASS, no GCI, no    =="
    echo "== observed order, no verdict of the fixed vocabulary.                =="
  fi
  echo
  echo "-- ladder placement --"
  echo "   level ${LEVEL}  scale ${SCALE}  n_rad ${NRAD} (EXPLICIT)  cells ${CELLS_EMITTED}"
  echo "-- jet BCs actually written into 0/ --"
  echo "   V_j ${VJ}   U_jetSlot (${VJX} ${VJY} 0)   k_jet ${KJET}   omega_jet ${OMJET}"
  echo "-- last 3 forceCoeffs rows (column order read from the file's own header) --"
  find "${RUN_ROOT}/postProcessing/forceCoeffs" -name 'coefficient*.dat' \
    -exec sh -c 'grep "^#" "$1" | tail -1; grep -v "^#" "$1" | tail -3' _ {} \;
  echo "-- End line count --"
  grep -c "^End" "${RUN_ROOT}/log.simpleFoam" || true
  echo "-- last Time --"
  grep "^Time = " "${RUN_ROOT}/log.simpleFoam" | tail -1
  echo "-- SIMPLE convergence line, if any --"
  grep -c "SIMPLE solution converged" "${RUN_ROOT}/log.simpleFoam" || true
  echo "-- final residuals --"
  grep -E "Solving for (Ux|Uy|p|k|omega)" "${RUN_ROOT}/log.simpleFoam" | tail -6
  echo "-- CLIPPING (L-235): bounding events, WHOLE RUN --"
  echo "   bounding k     $(grep -c 'bounding k' "${RUN_ROOT}/log.simpleFoam" || true)"
  echo "   bounding omega $(grep -c 'bounding omega' "${RUN_ROOT}/log.simpleFoam" || true)"
  echo "-- continuity --"
  grep "continuity errors" "${RUN_ROOT}/log.simpleFoam" | tail -2
  echo "-- y+ : LAST ROW PER PATCH, and the DATA-ROW COUNT (gate G2: max < 1) --"
  echo "   yplus_data_rows ${YPLUS_ROWS}"
  grep -v '^#' "${YPLUS_DAT}" 2>/dev/null | tail -3
} > "${RUN_ROOT}/READOUT.txt" 2>&1

STAGE="done"
exit 0
