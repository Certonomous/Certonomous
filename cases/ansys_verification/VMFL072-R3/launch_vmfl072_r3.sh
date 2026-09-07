#!/bin/bash
# ---------------------------------------------------------------------------
# VMFL072-R3 -- THE LAB DRIVER.  One registered level per invocation.
#
#     VMFL072R3_PREREG_SHA=<freeze commit> ./launch_vmfl072_r3.sh <L1|L2|L3|B2|C1>
#
# THIS IS NOT A TUTORIAL Allrun.  It never cd's into the case directory, never
# writes into cases/, and never runs a solver that has not passed every guard
# below.  Three freezes in this team have now been damaged by an executable
# whose LOGIC was read and whose CONTACT WITH REALITY was not:
#   - ANSYS_VERIFICATION_CHARTER 38.1: a launcher frozen referencing a base/
#     that did not exist; `bash -n` checks SYNTAX and never path existence.
#   - 39.2: a comparator frozen reading two filenames that exist in zero code
#     paths.
#   - and one frozen the same day whose only executable was a tutorial Allrun.
# Guard G-00 below therefore asserts THAT EVERY PATH THIS SCRIPT READS OR
# EXECUTES EXISTS, before anything else happens.
#
# GUARDS, in order.  Each exits non-zero without launching.
#   G-00  every path this script reads or executes EXISTS
#   G-01  VMFL072R3_PREREG_SHA is set
#   G-03  the comparator's blob equals the pin RECORDED IN THE REGISTRATION
#         (runs BEFORE G-02: it needs no commit, so it is the check that still
#         says something when G-02 cannot, and the predecessor's freeze had no
#         analogue of it)
#   G-02  every frozen file hashes equal to its blob at that commit
#   G-04  the run root is under verification/runs/ and NOT under cases/
#   G-05  the run root does not already exist
#   G-06  after staging, no time directory but 0/ exists
#   G-07  the age-guard marker 0/U is touched LAST and then ASSERTED:
#         `find 0 constant system -type f ! -path .../0/U -newer 0/U` is empty
#   G-08  the solver runs under `timeout` at the level's registered cap, and
#         rc is captured INSIDE the detached wrapper -- `setsid timeout cmd`
#         exits 0 for every outcome, so a wrapper that captures rc AROUND the
#         setsid line records a false success.
#
# EXIT CODES  0 launched   2 a guard refused   3 bad usage
# ---------------------------------------------------------------------------
set -euo pipefail

usage() { echo "usage: VMFL072R3_PREREG_SHA=<sha> $0 <L1|L2|L3|B2|C1>" >&2; exit 3; }

LEVEL="${1:-}"
case "${LEVEL}" in L1|L2|L3|B2|C1) ;; *) usage ;; esac

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "${HERE}" rev-parse --show-toplevel)"
RELDIR="cases/ansys_verification/VMFL072-R3"

# --- registered per-level caps, core-minutes (R3 8.2). SERIAL: 1 rank, so ---
# --- core-minutes == wall minutes and the timeout is exact. ----------------
case "${LEVEL}" in
  L1) CAP_CORE_MIN=1.5   ;;
  L2) CAP_CORE_MIN=9     ;;
  L3) CAP_CORE_MIN=65    ;;
  B2) CAP_CORE_MIN=100   ;;
  C1) CAP_CORE_MIN=9     ;;
esac
CAP_SEC="$(python3 -c "print(int(round(${CAP_CORE_MIN}*60)))")"

# ===========================================================================
# G-00  EVERY PATH THIS SCRIPT READS OR EXECUTES EXISTS
# ===========================================================================
FROZEN_FILES=(
  "PREREGISTRATION.md"
  "compare_vmfl072_r3.py"
  "apply_level.sh"
  "launch_vmfl072_r3.sh"
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
#       (an explicit test, not `${VAR:?}` -- that exits 1 under set -e and this
#        script documents 2 for every guard refusal)
# ===========================================================================
if [ -z "${VMFL072R3_PREREG_SHA:-}" ]; then
  echo "G-01 REFUSED: VMFL072R3_PREREG_SHA is not set. The frozen file must be" >&2
  echo "  THE FILE THAT RAN (CLAUDE.md rule 2); without the freeze commit this" >&2
  echo "  script cannot prove that and will not launch." >&2
  exit 2
fi

# ===========================================================================
# G-03  THE COMPARATOR PIN, READ OUT OF THE REGISTRATION ITSELF.
#       One source of truth: the pin lives in PREREGISTRATION.md 9.1 and this
#       script reads it there rather than carrying a second copy that could
#       drift.  It runs BEFORE G-02 deliberately: it needs no commit, so it is
#       the check that still says something when G-02 cannot.
# ===========================================================================
PIN="$(grep -oE 'COMPARATOR_BLOB[[:space:]]*=[[:space:]]*[0-9a-f]{40}' \
         "${HERE}/PREREGISTRATION.md" | grep -oE '[0-9a-f]{40}' | head -1 || true)"
if [ -z "${PIN}" ]; then
  echo "G-03 REFUSED: PREREGISTRATION.md carries no COMPARATOR_BLOB pin." >&2
  exit 2
fi
CMP="$(git -C "${REPO}" hash-object "${HERE}/compare_vmfl072_r3.py")"
if [ "${CMP}" != "${PIN}" ]; then
  echo "G-03 REFUSED: comparator blob ${CMP} != registered pin ${PIN}" >&2
  exit 2
fi

# ===========================================================================
# G-02  EVERY FROZEN FILE HASHES EQUAL TO ITS BLOB AT THE FREEZE COMMIT
# ===========================================================================
# `git rev-parse <bad>:<path>` ECHOES ITS INPUT and does not fail cleanly, so a
# bare capture yields the literal string "deadbeef:cases/..." and the mismatch
# message becomes nonsense. --verify plus a 40-hex assertion is what makes the
# refusal readable and correct.  Found by running this guard, not by reading it.
if ! git -C "${REPO}" rev-parse --verify --quiet "${VMFL072R3_PREREG_SHA}^{commit}" >/dev/null; then
  echo "G-02 REFUSED: '${VMFL072R3_PREREG_SHA}' is not a commit in this repository." >&2
  exit 2
fi
for f in "${FROZEN_FILES[@]}"; do
  have="$(git -C "${REPO}" hash-object "${HERE}/${f}")"
  want="$(git -C "${REPO}" rev-parse --verify --quiet \
            "${VMFL072R3_PREREG_SHA}:${RELDIR}/${f}" || true)"
  if ! [[ "${want}" =~ ^[0-9a-f]{40}$ ]]; then
    echo "G-02 REFUSED: ${RELDIR}/${f} does not exist at ${VMFL072R3_PREREG_SHA}" >&2
    exit 2
  fi
  if [ "${have}" != "${want}" ]; then
    echo "G-02 REFUSED: ${f} on disk is ${have}, frozen blob is ${want}" >&2
    exit 2
  fi
done

# ===========================================================================
# G-04/G-05  THE RUN ROOT
# ===========================================================================
RUNROOT="${REPO}/verification/runs/ansys_verification/VMFL072-R3/${LEVEL}"
case "${RUNROOT}" in
  "${REPO}/verification/runs/"*) ;;
  *) echo "G-04 REFUSED: run root ${RUNROOT} is not under verification/runs/" >&2; exit 2 ;;
esac
case "${RUNROOT}" in
  *"/cases/"*) echo "G-04 REFUSED: a run may never be written under cases/" >&2; exit 2 ;;
esac
if [ -e "${RUNROOT}" ]; then
  echo "G-05 REFUSED: ${RUNROOT} already exists. A run directory is never" >&2
  echo "  reused; an existing one is INSPECTED, never overwritten." >&2
  exit 2
fi

# ===========================================================================
# STAGE
# ===========================================================================
mkdir -p "${RUNROOT}"
cp -r "${HERE}/base/." "${RUNROOT}/"
cp -r "${RUNROOT}/0.orig" "${RUNROOT}/0"
bash "${HERE}/apply_level.sh" "${RUNROOT}" "${LEVEL}"

# G-06  no time directory but 0/
stray="$(find "${RUNROOT}" -maxdepth 1 -mindepth 1 -type d \
          -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' \
          ! -name '0' -printf '%f ' 2>/dev/null || true)"
if [ -n "${stray}" ]; then
  echo "G-06 REFUSED: pre-existing time directories: ${stray}" >&2
  exit 2
fi

# ===========================================================================
# MESH -- before the age-guard touch, because blockMesh writes into constant/
# ===========================================================================
( cd "${RUNROOT}" && blockMesh    > log.blockMesh   2>&1 )
( cd "${RUNROOT}" && makeFaMesh   > log.makeFaMesh  2>&1 )
( cd "${RUNROOT}" && checkFaMesh  > log.checkFaMesh 2>&1 )
grep -q "Face area:" "${RUNROOT}/log.checkFaMesh" || {
  echo "G-00 REFUSED: log.checkFaMesh has no 'Face area:' block -- the" >&2
  echo "  comparator's C-16 cross-check would have nothing to read." >&2
  exit 2; }

# ===========================================================================
# G-07  AGE GUARD.  0/U is touched LAST and then ASSERTED.  The comparator's
#       C-07 and this assertion are two halves of one control; neither is
#       sufficient alone.
# ===========================================================================
touch "${RUNROOT}/0/U"
newer="$(cd "${RUNROOT}" && find 0 constant system -type f ! -path '0/U' -newer 0/U -print)"
if [ -n "${newer}" ]; then
  echo "G-07 REFUSED: these inputs are NEWER than the age-guard marker 0/U," >&2
  echo "  so the marker does not date the run and C-07 would be vacuous:" >&2
  echo "${newer}" >&2
  exit 2
fi

# ===========================================================================
# G-08  LAUNCH.  rc is captured INSIDE the wrapper.
# ===========================================================================
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
echo "cap_core_min=${CAP_CORE_MIN}"                  >> RC.txt
echo "ranks=1"                                       >> RC.txt
echo "finished=\$(date -u +%Y-%m-%dT%H:%M:%SZ)"      >> RC.txt
if [ "\${rc}" = "124" ] || [ "\${rc}" = "137" ]; then
  echo "OVERRUN: the ${CAP_CORE_MIN} core-min cap STOPPED this run."  >> RC.txt
  echo "CLAUDE.md rule 12: an overrun stops the run; it does not get" >> RC.txt
  echo "a new budget."                                                >> RC.txt
fi
INNER
chmod +x "${RUNROOT}/run_inner.sh"

cat > "${RUNROOT}/LAUNCH_RECORD.txt" <<REC
case            VMFL072-R3
level           ${LEVEL}
prereg sha      ${VMFL072R3_PREREG_SHA}
comparator pin  ${PIN}
comparator blob ${CMP}
run root        ${RUNROOT}
cap             ${CAP_CORE_MIN} core-min (${CAP_SEC} s, serial, 1 rank)
launched        $(date -u +%Y-%m-%dT%H:%M:%SZ)
guards passed   G-00 G-01 G-02 G-03 G-04 G-05 G-06 G-07
REC

setsid "${RUNROOT}/run_inner.sh" < /dev/null > "${RUNROOT}/log.wrapper" 2>&1 &
echo "LAUNCHED ${LEVEL}  ->  ${RUNROOT}  (cap ${CAP_CORE_MIN} core-min)"
echo "grade only after ALL FIVE levels are complete:"
echo "  python3 ${HERE}/compare_vmfl072_r3.py --runroot ${REPO}/verification/runs/ansys_verification/VMFL072-R3"
