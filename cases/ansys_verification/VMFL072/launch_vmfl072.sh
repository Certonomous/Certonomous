#!/bin/bash
# VMFL072 launcher -- DRAFT, UNTRACKED, NOT YET FROZEN. NOT RUN.
#
# REPAIR 4. The comparator's age guard (CLAUDE.md rule 4, prereg 5.5 clause 6)
# dates every endTime field against `0/U`. That is only valid if `0/U` is
# touched LAST at launch. Until this file existed that was an ASSUMPTION.
# Here it becomes a PROPERTY: 0/U is touched last, and the launcher ASSERTS it
# before releasing the solver. If the assertion fails, nothing launches.
#
# This script is also the environment the Clause B smoke must run in
# (ANSYS_VERIFICATION_CHARTER 14.3 as sharpened by 15.1): the smoke sources
# THIS file's environment, never `env -i` and never a hand-sourced shell,
# because a smoke that proves something about a shell the launch never gets has
# proved nothing about the launch.
#
# Usage:  ./launch_vmfl072.sh <LEVEL>   with LEVEL in L1 L2 L3 B2 C1
set -euo pipefail

CASE_ID="VMFL072"
REPO="/home/ubuntu/Certonomous"
RUNS="${REPO}/verification/runs/ansys_verification/${CASE_ID}"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
ENDTIME="10.0"

LEVEL="${1:?usage: launch_vmfl072.sh <L1|L2|L3|B2|C1>}"
case "${LEVEL}" in L1|L2|L3|B2|C1) ;; *) echo "bad level: ${LEVEL}" >&2; exit 3 ;; esac
DIR="${RUNS}/${LEVEL}"

# ---------------------------------------------------------------------------
# 0. FREEZE GATE. No solver launches without a named, committed pre-registration
#    (CLAUDE.md rule 2; ANSYS_VERIFICATION_CHARTER 5.1). The sha is passed in by
#    the supervisor at the freeze; there is no default.
# ---------------------------------------------------------------------------
if [ -z "${VMFL072_PREREG_SHA:-}" ]; then
  echo "REFUSING: VMFL072_PREREG_SHA is unset. The freeze is the supervisor" >&2
  echo "  undelegable check and must be NAMED at launch (CLAUDE.md rule 2)." >&2
  exit 2
fi

PREREG="${REPO}/cases/ansys_verification/${CASE_ID}/PREREGISTRATION.md"
HAVE="$(cd "${REPO}" && git hash-object "${PREREG}")"
BLOB="$(cd "${REPO}" && git rev-parse "${VMFL072_PREREG_SHA}:cases/ansys_verification/${CASE_ID}/PREREGISTRATION.md")"
if [ "${HAVE}" != "${BLOB}" ]; then
  echo "REFUSING: the pre-registration on disk is NOT the frozen file." >&2
  echo "  on disk   ${HAVE}" >&2
  echo "  committed ${BLOB}  (at ${VMFL072_PREREG_SHA})" >&2
  exit 2
fi
echo "freeze verified: PREREGISTRATION.md == blob ${BLOB} at ${VMFL072_PREREG_SHA}"

# ---------------------------------------------------------------------------
# 1. LAUNCH GUARD (rule 4). Refuse a case where 0/ or any time dir already
#    exists -- a pre-existing field could carry an answer this run did not make.
# ---------------------------------------------------------------------------
if [ -e "${DIR}/0" ]; then
  echo "REFUSING: ${DIR}/0 already exists. A guard refuses a case whose 0/ is" >&2
  echo "  already present; re-running into it would defeat the age guard." >&2
  exit 2
fi
if compgen -G "${DIR}/[0-9]*" > /dev/null 2>&1; then
  echo "REFUSING: time directories already exist under ${DIR}" >&2
  exit 2
fi

mkdir -p "${DIR}"
cp -r "${REPO}/cases/ansys_verification/${CASE_ID}/base/." "${DIR}/"
cp -r "${DIR}/0.orig" "${DIR}/0"
"${REPO}/cases/ansys_verification/${CASE_ID}/apply_level.sh" "${DIR}" "${LEVEL}"

# ---------------------------------------------------------------------------
# 2. ENVIRONMENT -- sourced HERE, so the smoke and the solve share it exactly.
# ---------------------------------------------------------------------------
# shellcheck disable=SC1090
source "${FOAM_BASHRC}"
echo "env: WM_PROJECT_VERSION=${WM_PROJECT_VERSION} FOAM_APPBIN=${FOAM_APPBIN}"

( cd "${DIR}" && blockMesh > log.blockMesh 2>&1 )
( cd "${DIR}" && makeFaMesh > log.makeFaMesh 2>&1 )

# ---------------------------------------------------------------------------
# 3. AGE-GUARD MARKER. 0/U is touched LAST, after every other input file, so it
#    dates the run allowed to produce the answer -- then the property is
#    ASSERTED, not assumed.
# ---------------------------------------------------------------------------
sync
sleep 1.1                      # ensure a strictly greater mtime at 1 s resolution
touch "${DIR}/0/U"

NEWER="$(find "${DIR}/0" "${DIR}/constant" "${DIR}/system" \
              -type f ! -path "${DIR}/0/U" -newer "${DIR}/0/U" 2>/dev/null | head -5)"
if [ -n "${NEWER}" ]; then
  echo "REFUSING: 0/U is NOT the newest input; the age guard would be blind to" >&2
  echo "  a stale field. Files newer than 0/U:" >&2
  echo "${NEWER}" >&2
  exit 2
fi
echo "age-guard marker asserted: 0/U is strictly the newest input file"

# ---------------------------------------------------------------------------
# 4. DETACHED LAUNCH. rc is captured INSIDE the wrapper -- `setsid timeout cmd`
#    exits 0 for every outcome, so an rc captured around the setsid line is
#    meaningless (lesson: setsid-parent-returns-zero).
# ---------------------------------------------------------------------------
CAP_COREMIN="${VMFL072_CAP_COREMIN:-800}"
RANKS="${VMFL072_RANKS:-4}"
WALL_S="$(python3 -c "print(int(${CAP_COREMIN}*60/${RANKS}))")"

cat > "${DIR}/run_inner.sh" <<INNER
#!/bin/bash
cd "${DIR}"
source "${FOAM_BASHRC}"
decomposePar > log.decomposePar 2>&1
mpirun -np ${RANKS} pimpleFoam -parallel > log.pimpleFoam 2>&1
rc=\$?                                  # captured INSIDE the wrapper
reconstructPar -latestTime >> log.reconstructPar 2>&1
echo "\${rc}" > "${DIR}/rc"
INNER
chmod +x "${DIR}/run_inner.sh"

echo "launching ${LEVEL}: ${RANKS} ranks, cap ${CAP_COREMIN} core-min => wall ${WALL_S} s"
setsid timeout "${WALL_S}" "${DIR}/run_inner.sh" < /dev/null > "${DIR}/log.wrapper" 2>&1 &
echo "detached pid $! ; rc will appear at ${DIR}/rc"
