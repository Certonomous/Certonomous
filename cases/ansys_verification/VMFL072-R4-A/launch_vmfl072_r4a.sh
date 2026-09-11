#!/bin/bash
# ---------------------------------------------------------------------------
# VMFL072-R4-A -- THE LAB DRIVER.  ONE invocation runs the WHOLE ladder.
#
#     VMFL072R4A_PREREG_SHA=<freeze commit> ./launch_vmfl072_r4a.sh
#
# DRAFT, NOT FROZEN. Adapted from VMFL072-R3/launch_vmfl072_r3.sh. Two
# structural changes, both required by the R4-A pre-registration:
#
#   (A) ONE INVOCATION, THREE RUNGS, SERIAL, WITH AN ACCUMULATED FAMILY CAP.
#       Unlike R3 (one level per invocation), this driver runs A1 -> A2 -> A3
#       in a single invocation, WAITS for each rung to finish, and keeps a
#       running TOTAL_CORE_MIN that is set to 0 EXACTLY ONCE, before the loop,
#       and accumulated ACROSS rungs. This is the D604 FIX folded into the run:
#       D604 is the bug where `TOTAL_CORE_MIN=0` per invocation resets the cap,
#       so a relaunch restarts the running total from zero. Here the family cap
#       (120 core-min) binds across all three rungs; before each rung the driver
#       computes REMAIN = 120 - TOTAL and, if REMAIN <= 0, ABORTS the remaining
#       rungs (CLAUDE.md rule 12: an overrun stops the run, it is not
#       re-budgeted). The per-rung timeout is min(40, REMAIN) core-min so the
#       family cap binds even mid-rung. No persisted file is relied on.
#
#   (B) BY HAND, NOT A QUEUE ENTRY. This is fired by hand when box load drops;
#       no queue JSON is written and no daemon may pick it up (R4-A prereg 8).
#
# SERIAL: RANKS=1, so core-minutes == wall minutes and every timeout is exact.
#
# GUARDS, in order (each exits non-zero without launching), identical in intent
# to R3's:
#   G-00 every path this script reads or executes EXISTS
#   G-01 VMFL072R4A_PREREG_SHA is set
#   G-03 the comparator blob equals the pin RECORDED IN THE REGISTRATION
#   G-02 every frozen file hashes equal to its blob at that commit
#   G-04 the run root is under verification/runs/ and NOT under cases/
#   G-05 the run root does not already exist
#   G-06 after staging a rung, no time directory but 0/ exists
#   G-07 the age-guard marker 0/U is touched LAST and then ASSERTED
#   G-08 the solver runs under `timeout` at the rung cap, rc captured INSIDE
#        the detached wrapper (`setsid timeout cmd` exits 0 for every outcome)
#
# EXIT CODES  0 ladder ran to completion or a clean cap abort   2 a guard
# refused   3 bad usage
# ---------------------------------------------------------------------------
set -euo pipefail

if [ "${1:-}" != "" ]; then
  echo "usage: VMFL072R4A_PREREG_SHA=<sha> $0    (no arguments; runs A1 A2 A3)" >&2
  exit 3
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "${HERE}" rev-parse --show-toplevel)"
RELDIR="cases/ansys_verification/VMFL072-R4-A"

RUNGS=(A1 A2 A3)
FAMILY_CAP_CORE_MIN=120           # R4-A prereg 8
PER_RUNG_CAP_CORE_MIN=40          # R4-A prereg 8

# ===========================================================================
# G-00  EVERY PATH THIS SCRIPT READS OR EXECUTES EXISTS
# ===========================================================================
FROZEN_FILES=(
  "PREREGISTRATION.md"
  "compare_vmfl072_r4a.py"
  "apply_level.sh"
  "launch_vmfl072_r4a.sh"
)
CASE_INPUTS=(
  "base/constant/g"
  "base/constant/transportProperties"
  "base/constant/turbulenceProperties"
  "base/0.orig/U"
  "base/0.orig/p"
  "base/0.orig/finite-area/hf_film"
  "base/0.orig/finite-area/Uf_film"
  "base/system/blockMeshDict"
  "base/system/controlDict"
  "base/system/fvSchemes"
  "base/system/fvSolution"
  "base/system/finite-area/faMeshDefinition"
  "base/system/finite-area/faSchemes"
  "base/system/finite-area/faSolution"
)
missing=0
for f in "${FROZEN_FILES[@]}" "${CASE_INPUTS[@]}"; do
  [ -f "${HERE}/${f}" ] || { echo "G-00 MISSING: ${HERE}/${f}" >&2; missing=1; }
done
for exe in blockMesh makeFaMesh checkFaMesh pimpleFoam setsid timeout python3 git; do
  command -v "${exe}" >/dev/null 2>&1 || { echo "G-00 MISSING EXECUTABLE: ${exe}" >&2; missing=1; }
done
[ -d "${REPO}/verification/runs/ansys_verification" ] || {
  echo "G-00 MISSING: ${REPO}/verification/runs/ansys_verification" >&2; missing=1; }
[ "${missing}" -eq 0 ] || { echo "G-00 REFUSED: not launching." >&2; exit 2; }

# ===========================================================================
# G-01  THE FREEZE COMMIT MUST BE NAMED
# ===========================================================================
if [ -z "${VMFL072R4A_PREREG_SHA:-}" ]; then
  echo "G-01 REFUSED: VMFL072R4A_PREREG_SHA is not set. Without the freeze" >&2
  echo "  commit this script cannot prove the frozen file IS the file that ran" >&2
  echo "  (CLAUDE.md rule 2) and will not launch." >&2
  exit 2
fi

# ===========================================================================
# G-03  THE COMPARATOR PIN, READ OUT OF THE REGISTRATION (before G-02).
# ===========================================================================
PIN="$(grep -oE 'COMPARATOR_BLOB[[:space:]]*=[[:space:]]*[0-9a-f]{40}' \
         "${HERE}/PREREGISTRATION.md" | grep -oE '[0-9a-f]{40}' | head -1 || true)"
if [ -z "${PIN}" ]; then
  echo "G-03 REFUSED: PREREGISTRATION.md carries no COMPARATOR_BLOB pin." >&2
  exit 2
fi
CMP="$(git -C "${REPO}" hash-object "${HERE}/compare_vmfl072_r4a.py")"
if [ "${CMP}" != "${PIN}" ]; then
  echo "G-03 REFUSED: comparator blob ${CMP} != registered pin ${PIN}" >&2
  exit 2
fi

# ===========================================================================
# G-02  EVERY FROZEN FILE HASHES EQUAL TO ITS BLOB AT THE FREEZE COMMIT
# ===========================================================================
if ! git -C "${REPO}" rev-parse --verify --quiet "${VMFL072R4A_PREREG_SHA}^{commit}" >/dev/null; then
  echo "G-02 REFUSED: '${VMFL072R4A_PREREG_SHA}' is not a commit in this repository." >&2
  exit 2
fi
for f in "${FROZEN_FILES[@]}"; do
  have="$(git -C "${REPO}" hash-object "${HERE}/${f}")"
  want="$(git -C "${REPO}" rev-parse --verify --quiet \
            "${VMFL072R4A_PREREG_SHA}:${RELDIR}/${f}" || true)"
  if ! [[ "${want}" =~ ^[0-9a-f]{40}$ ]]; then
    echo "G-02 REFUSED: ${RELDIR}/${f} does not exist at ${VMFL072R4A_PREREG_SHA}" >&2
    exit 2
  fi
  if [ "${have}" != "${want}" ]; then
    echo "G-02 REFUSED: ${f} on disk is ${have}, frozen blob is ${want}" >&2
    exit 2
  fi
done

# ===========================================================================
# G-04/G-05  THE RUN ROOT (the whole family dir; one invocation owns it)
# ===========================================================================
RUNBASE="${REPO}/verification/runs/ansys_verification/VMFL072-R4-A"
case "${RUNBASE}" in
  "${REPO}/verification/runs/"*) ;;
  *) echo "G-04 REFUSED: run root ${RUNBASE} is not under verification/runs/" >&2; exit 2 ;;
esac
case "${RUNBASE}" in
  *"/cases/"*) echo "G-04 REFUSED: a run may never be written under cases/" >&2; exit 2 ;;
esac
if [ -e "${RUNBASE}" ]; then
  echo "G-05 REFUSED: ${RUNBASE} already exists. A run directory is never" >&2
  echo "  reused; an existing one is INSPECTED, never overwritten." >&2
  exit 2
fi

mkdir -p "${RUNBASE}"
cat > "${RUNBASE}/LAUNCH_RECORD.txt" <<REC
case            VMFL072-R4-A
rungs           ${RUNGS[*]}  (serial, 1 rank each)
prereg sha      ${VMFL072R4A_PREREG_SHA}
comparator pin  ${PIN}
comparator blob ${CMP}
run base        ${RUNBASE}
family cap      ${FAMILY_CAP_CORE_MIN} core-min (accumulated ACROSS rungs -- D604 fix)
per-rung cap    ${PER_RUNG_CAP_CORE_MIN} core-min
launched        $(date -u +%Y-%m-%dT%H:%M:%SZ)
load at launch  $(uptime | grep -oE 'load average.*' || echo unknown)
guards passed   G-00 G-01 G-02 G-03 G-04 G-05
REC

# ===========================================================================
# THE LADDER.  TOTAL_CORE_MIN is set to 0 HERE, ONCE, and accumulated across
# rungs -- NEVER reset per rung (the D604 fix).
# ===========================================================================
TOTAL_CORE_MIN=0

for RUNG in "${RUNGS[@]}"; do
  REMAIN="$(python3 -c "print(round(${FAMILY_CAP_CORE_MIN} - ${TOTAL_CORE_MIN}, 4))")"
  if python3 -c "import sys; sys.exit(0 if ${REMAIN} <= 0 else 1)"; then
    echo "FAMILY CAP REACHED before ${RUNG}: spent ${TOTAL_CORE_MIN} of ${FAMILY_CAP_CORE_MIN} core-min."
    echo "  rule 12: an overrun stops the run. Remaining rungs are NOT launched."
    echo "family_cap_reached before ${RUNG}: spent ${TOTAL_CORE_MIN}" >> "${RUNBASE}/LAUNCH_RECORD.txt"
    break
  fi
  RUNG_CAP_CM="$(python3 -c "print(min(${PER_RUNG_CAP_CORE_MIN}, ${REMAIN}))")"
  CAP_SEC="$(python3 -c "print(int(round(${RUNG_CAP_CM}*60)))")"

  RUNROOT="${RUNBASE}/${RUNG}"
  if [ -e "${RUNROOT}" ]; then
    echo "G-05 REFUSED: ${RUNROOT} already exists." >&2; exit 2
  fi

  # ---- STAGE ----
  mkdir -p "${RUNROOT}"
  cp -r "${HERE}/base/." "${RUNROOT}/"
  cp -r "${RUNROOT}/0.orig" "${RUNROOT}/0"
  bash "${HERE}/apply_level.sh" "${RUNROOT}" "${RUNG}"

  # G-06  no time directory but 0/
  stray="$(find "${RUNROOT}" -maxdepth 1 -mindepth 1 -type d \
            -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' \
            ! -name '0' -printf '%f ' 2>/dev/null || true)"
  if [ -n "${stray}" ]; then
    echo "G-06 REFUSED: pre-existing time directories in ${RUNG}: ${stray}" >&2
    exit 2
  fi

  # ---- MESH (before the age-guard touch: blockMesh writes into constant/) ----
  ( cd "${RUNROOT}" && blockMesh    > log.blockMesh   2>&1 )
  ( cd "${RUNROOT}" && makeFaMesh   > log.makeFaMesh  2>&1 )
  ( cd "${RUNROOT}" && checkFaMesh  > log.checkFaMesh 2>&1 )
  grep -q "Face area:" "${RUNROOT}/log.checkFaMesh" || {
    echo "G-00 REFUSED: ${RUNG} log.checkFaMesh has no 'Face area:' block." >&2
    exit 2; }

  # ---- G-07  AGE GUARD ----
  touch "${RUNROOT}/0/U"
  newer="$(cd "${RUNROOT}" && find 0 constant system -type f ! -path '0/U' -newer 0/U -print)"
  if [ -n "${newer}" ]; then
    echo "G-07 REFUSED: inputs NEWER than the age-guard marker 0/U in ${RUNG}:" >&2
    echo "${newer}" >&2
    exit 2
  fi

  # ---- G-08  LAUNCH.  rc captured INSIDE the wrapper.  Run SYNCHRONOUSLY
  #      (setsid for session isolation, then WAIT) so the family cap can
  #      accumulate from this rung's measured wall time. ----
  cat > "${RUNROOT}/run_inner.sh" <<INNER
#!/bin/bash
# rc is captured INSIDE this wrapper. \`setsid timeout cmd\` returns 0 for every
# outcome, so a wrapper capturing rc AROUND the setsid line records a false
# success on a timeout, a signal or a solver crash alike.
cd "${RUNROOT}"
timeout --signal=TERM --kill-after=60 ${CAP_SEC} pimpleFoam > log.pimpleFoam 2>&1
rc=\$?
echo "rc=\${rc}"                                    >  RC.txt
echo "cap_sec=${CAP_SEC}"                            >> RC.txt
echo "cap_core_min=${RUNG_CAP_CM}"                   >> RC.txt
echo "ranks=1"                                       >> RC.txt
echo "finished=\$(date -u +%Y-%m-%dT%H:%M:%SZ)"      >> RC.txt
if [ "\${rc}" = "124" ] || [ "\${rc}" = "137" ]; then
  echo "OVERRUN: the ${RUNG_CAP_CM} core-min cap STOPPED this rung."  >> RC.txt
  echo "CLAUDE.md rule 12: an overrun stops the run; no new budget."  >> RC.txt
fi
INNER
  chmod +x "${RUNROOT}/run_inner.sh"

  echo "LAUNCH ${RUNG}  cap ${RUNG_CAP_CM} core-min (${CAP_SEC} s)  remaining ${REMAIN} of ${FAMILY_CAP_CORE_MIN} ..."
  t_start=${SECONDS}
  setsid "${RUNROOT}/run_inner.sh" < /dev/null > "${RUNROOT}/log.wrapper" 2>&1 &
  wpid=$!
  wait "${wpid}" || true
  t_wall=$(( SECONDS - t_start ))
  CORE_MIN="$(python3 -c "print(round(${t_wall}/60.0, 4))")"
  TOTAL_CORE_MIN="$(python3 -c "print(round(${TOTAL_CORE_MIN} + ${CORE_MIN}, 4))")"
  RC="$(grep -oE 'rc=[-0-9]+' "${RUNROOT}/RC.txt" 2>/dev/null | head -1 | cut -d= -f2 || echo NA)"
  echo "done ${RUNG}: rc=${RC}  wall ${t_wall}s = ${CORE_MIN} core-min  (family total ${TOTAL_CORE_MIN} of ${FAMILY_CAP_CORE_MIN})"
  echo "${RUNG}: rc=${RC} wall_s=${t_wall} core_min=${CORE_MIN} total=${TOTAL_CORE_MIN} cap=${RUNG_CAP_CM}" >> "${RUNBASE}/LAUNCH_RECORD.txt"
done

echo "family_total_core_min=${TOTAL_CORE_MIN} of ${FAMILY_CAP_CORE_MIN}" >> "${RUNBASE}/LAUNCH_RECORD.txt"
echo ""
echo "LADDER DONE. family total ${TOTAL_CORE_MIN} of ${FAMILY_CAP_CORE_MIN} core-min."
echo "grade only after the invocation returns:"
echo "  python3 ${HERE}/compare_vmfl072_r4a.py --runroot ${RUNBASE}"
