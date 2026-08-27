#!/bin/bash
# ---------------------------------------------------------------------------
# G2 grid-triple driver: square duct AR_1_Ret_360, three levels, ascending cost.
#
# RC CAPTURE.  Every child's rc is captured on the line AFTER the child, in this
# script's own foreground.  This script contains NO setsid and NO nohup.
# `setsid timeout cmd` exits 0 for EVERY outcome, so an rc taken around a setsid
# line is the wrapper's rc, not the child's.  Detaching is the queue daemon's
# job; if anyone later wraps a command here in setsid, the rc must be captured
# INSIDE the detached wrapper.
#
# This script NEVER touches git, NEVER writes into cases/, and writes every
# artifact under RUN_ROOT.
# ---------------------------------------------------------------------------
set -u

CASE_DIR="/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/G2_grid_triple_duct"
RUN_ROOT="/home/ubuntu/closure-data/g2"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

# Registered cap (PREREGISTRATION.md section 7).  ranks = 1, so core-min == wall-min.
CAP_CORE_MIN=120
CAP_S=7200

# level  nCells_expected  endTime  timeout_s   -- frozen, must match build_g2.py LEVELS
LEVELS="L1:1024:20000:300 L2:4096:30000:1500 L3:16384:40000:5400"

CHAIN="${RUN_ROOT}/CHAIN.log"
ELAPSED_S=0

log() { mkdir -p "${RUN_ROOT}"; echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "${CHAIN}"; echo "$*"; }
die() { log "CHAIN ABORT: $*"; log "CHAIN rc=2"; exit 2; }

log "CHAIN START  cap=${CAP_CORE_MIN} core-min (${CAP_S} s at ranks=1)"

# --- 0. environment -------------------------------------------------------
# `set -u` makes sourcing the OpenFOAM bashrc FATAL and SILENT: it reads
# WM_PROJECT_DIR unbound, which under nounset terminates a non-interactive shell
# immediately -- before `die` can run, and therefore with no CHAIN ABORT line.
# Nounset is lifted for the source alone and restored immediately, and the
# source's own diagnostics are KEPT in a log instead of being discarded.
[ -r "${FOAM_BASHRC}" ] || die "OpenFOAM bashrc not readable at ${FOAM_BASHRC}"
mkdir -p "${RUN_ROOT}"
# shellcheck disable=SC1090
set +u
source "${FOAM_BASHRC}" > "${RUN_ROOT}/log.foamenv" 2>&1
FOAMENV_RC=$?
set -u
log "FOAMENV rc=${FOAMENV_RC} (INFRASTRUCTURE: recorded; the binding check is the two command -v tests below)"
command -v blockMesh  >/dev/null 2>&1 || die "blockMesh not on PATH after sourcing the OpenFOAM environment"
command -v simpleFoam >/dev/null 2>&1 || die "simpleFoam not on PATH after sourcing the OpenFOAM environment"
log "ENV OK  $(simpleFoam -help 2>&1 | head -1 | tr -d '\r')"

# --- 1. stage.  build_g2.py refuses over an existing tree (the age guard) and
#        runs the RECONSTRUCTION CONTROL: the constructed dictionary must
#        regenerate the SHIPPED mesh before any level is staged.
python3 "${CASE_DIR}/build_g2.py" > "${RUN_ROOT}/log.build" 2>&1
RC=$?
log "STAGE rc=${RC}"
[ "${RC}" -eq 0 ] || die "build_g2.py refused; see ${RUN_ROOT}/log.build"

# --- 2. mesh every level FIRST: cheap, and it fails fast ------------------
for SPEC in ${LEVELS}; do
  L=${SPEC%%:*}; REST=${SPEC#*:}; NCE=${REST%%:*}
  D="${RUN_ROOT}/${L}"
  ( cd "${D}" && blockMesh > log.blockMesh 2>&1 ); RC=$?
  log "BLOCKMESH ${L} rc=${RC}"
  [ "${RC}" -eq 0 ] || die "blockMesh failed at ${L}"
  NC=$(grep -oP 'nCells:\s*\K[0-9]+' "${D}/constant/polyMesh/owner" | head -1)
  log "NCELLS ${L} = ${NC} (registered ${NCE})"
  [ "${NC}" = "${NCE}" ] || die "${L} meshed to ${NC} cells, registered ${NCE}; the refinement family is broken"
  ( cd "${D}" && checkMesh > log.checkMesh 2>&1 ); RC=$?
  log "CHECKMESH ${L} rc=${RC} (INFRASTRUCTURE: recorded, does not stop the chain)"
done

# --- 3. solve, cheapest level first, each gated on the previous -----------
for SPEC in ${LEVELS}; do
  L=${SPEC%%:*}; REST=${SPEC#*:}; NCE=${REST%%:*}; REST=${REST#*:}
  END=${REST%%:*}; TMO=${REST##*:}
  D="${RUN_ROOT}/${L}"

  REMAIN=$(( CAP_S - ELAPSED_S ))
  if [ "${TMO}" -gt "${REMAIN}" ]; then
    log "CAP WATCH: ${L} needs up to ${TMO} s, only ${REMAIN} s of the ${CAP_CORE_MIN} core-min cap remains."
    die "registered cap would be exceeded; an overrun stops the run, it does not get a new budget (standing rule 12)"
  fi

  # AGE MARKER, touched LAST, immediately before the solver launch, exactly as
  # the T-family touches 0/T.  Every field at endTime must be strictly newer.
  touch "${D}/0/U"
  T0=$(date +%s)
  ( cd "${D}" && /usr/bin/time -v -o mem_time.txt timeout "${TMO}" simpleFoam -case . > log.run 2>&1 ); RC=$?
  T1=$(date +%s)
  W=$(( T1 - T0 ))
  ELAPSED_S=$(( ELAPSED_S + W ))
  echo "${RC}"  > "${D}/rc.txt"
  echo "${W}"   > "${D}/wall_s.txt"
  log "SOLVE ${L} rc=${RC} wall_s=${W} core_min=$(awk -v w=${W} 'BEGIN{printf "%.2f", w/60}') cumulative_core_min=$(awk -v e=${ELAPSED_S} 'BEGIN{printf "%.2f", e/60}')"
  if [ "${RC}" -eq 124 ]; then
    die "${L} hit its registered ${TMO} s timeout. An overrun stops the run (standing rule 12)."
  fi
  [ "${RC}" -eq 0 ] || die "${L} simpleFoam rc=${RC}; a non-zero rc is a finding, triaged, never degraded"
  [ -d "${D}/${END}" ] || die "${L} has no ${END} time directory; the completion rule cannot hold"

  # --- 4. post-processing: INFRASTRUCTURE.  Failure is recorded, not fatal.
  for F in wallShearStress yPlus writeCellVolumes; do
    ( cd "${D}" && simpleFoam -postProcess -func "${F}" -latestTime > "log.post.${F}" 2>&1 ); RC=$?
    log "POST ${L} ${F} rc=${RC} (INFRASTRUCTURE)"
  done
  MAXRSS=$(grep -oP 'Maximum resident set size \(kbytes\): \K[0-9]+' "${D}/mem_time.txt" 2>/dev/null | head -1)
  log "MAXRSS ${L} = ${MAXRSS:-UNRECORDED} kB (measured; converts the registered memory allowance into a reading)"
done

log "CHAIN COMPLETE  total_core_min=$(awk -v e=${ELAPSED_S} 'BEGIN{printf "%.2f", e/60}') of cap ${CAP_CORE_MIN}"
log "NEXT: grade with  python3 ${CASE_DIR}/grade_g2.py"
log "CHAIN rc=0"
exit 0
