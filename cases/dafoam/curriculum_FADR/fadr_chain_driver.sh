#!/usr/bin/env bash
# FADR chain driver -- DAFoam's OWN shipped forward-AD regression, run UNMODIFIED,
# on BOTH toolchain rows.  Frozen with PREREGISTRATION.md; the grading path is
# fixed at that commit and this file re-asserts it against the committed blob
# before a single container starts.
#
#   usage: fadr_chain_driver.sh <freeze-sha-40hex> [S|P ...]
#
# EVERY GUARD REFUSES BEFORE A CORE-SECOND IS SPENT.  rc is read from
# `docker inspect .State.ExitCode`, NEVER from a `setsid`/`timeout` parent --
# `setsid timeout cmd` exits 0 for every outcome.
set -u
set -o pipefail

REPO="/home/ubuntu/Certonomous"
CASE_DIR="${REPO}/cases/dafoam/curriculum_FADR"
PREREG_REL="cases/dafoam/curriculum_FADR/PREREGISTRATION.md"
STORE="/home/ubuntu/certonomous-runs/FADR-fixture"
ARCHIVE="${STORE}/reg_test_files-main.tar.gz"
PROV="${CASE_DIR}/FIXTURE_PROVENANCE.md"
ROOT="/home/ubuntu/certonomous-runs/CURRICULUM-FADR-forward-ad-regression"

CPUSET="5,6,7"          # REGISTERED, PREREGISTRATION.md section 6
NP=4                    # UPSTREAM'S OWN, not changed
MEM="8g"                # REGISTERED
DEADLINE=1800           # s, in-container, per arm; REGISTERED

IMG_S="dafoam/opt-packages:latest"
DIG_S="sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"
IMG_P="dafoam-idwarp-rot:v1"
DIG_P="sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"

MD5_REG="e03630f44a016c3a8b23bcbc8b4b8128"   # runRegTests_DASimpleFoamForward.py
MD5_TF="fb11e90630aeba07c62c14afc5ed2ceb"    # testFuncs.py
MD5_REF="ac46aca2f10e68da43dbe74be0dd3c29"   # refs/DAFoam_Test_DASimpleFoamForwardRef.txt

die() { echo "REFUSAL: $*" >&2; exit 2; }
log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

# ---------------------------------------------------------------- G-FREEZE --
SHA="${1:-}"
[ -n "${SHA}" ] || die "no freeze sha given. usage: $0 <40-hex sha> [S|P ...]"
echo "${SHA}" | grep -qE '^[0-9a-f]{40}$' || die "freeze sha '${SHA}' is not 40 hex"
shift
ARMS=("$@"); [ ${#ARMS[@]} -gt 0 ] || ARMS=(S P)

cd "${REPO}" || die "cannot cd ${REPO}"
git cat-file -e "${SHA}^{commit}" 2>/dev/null || die "freeze sha ${SHA} is not a commit in this repo"
git cat-file -e "${SHA}:${PREREG_REL}" 2>/dev/null \
  || die "commit ${SHA} does not hold ${PREREG_REL}. A freeze sha is NEVER derived from a
     commit subject line (VERIFICATION_CHARTER v1.12): two commits in this lab shared a
     subject 52 s apart and the wrong one resolved to a real commit, failing only here."

# --------------------------------------------------- G-PATH: the grading path --
# Standing rule 2: verify the frozen file IS the file that runs, by hashing the
# on-disk file against the blob committed at the freeze.
for f in PREREGISTRATION.md fadr_chain_driver.sh fadr_grade.py fadr_fetch_fixture.sh; do
  disk="$(md5sum "${CASE_DIR}/${f}" 2>/dev/null | awk '{print $1}')"
  [ -n "${disk}" ] || die "instrument ${f} is missing from ${CASE_DIR}"
  blob="$(git cat-file blob "${SHA}:cases/dafoam/curriculum_FADR/${f}" 2>/dev/null | md5sum | awk '{print $1}')"
  [ -n "${blob}" ] || die "instrument ${f} is not in the freeze commit ${SHA}"
  [ "${disk}" = "${blob}" ] \
    || die "GRADING PATH MOVED: ${f} on disk is ${disk}, the freeze holds ${blob}.
     The file that would run is not the file that was frozen."
done
log "G-PATH: 4 instruments hashed against the freeze blob, all identical"

# ------------------------------------------------------------- G-FIXTURE --
[ -f "${PROV}" ] || die "no ${PROV}: the inbound retrieval has not been recorded (branch P-C)"
[ -f "${ARCHIVE}" ] || die "no fixture archive at ${ARCHIVE} (branch P-C)"
WANT_SHA="$(grep -oE '^\| \*\*sha256\*\* \| `[0-9a-f]{64}`' "${PROV}" | grep -oE '[0-9a-f]{64}')"
[ -n "${WANT_SHA}" ] || die "no sha256 recorded in ${PROV}"
GOT_SHA="$(sha256sum "${ARCHIVE}" | awk '{print $1}')"
[ "${GOT_SHA}" = "${WANT_SHA}" ] \
  || die "FIXTURE DIGEST: on disk ${GOT_SHA}, recorded ${WANT_SHA}. The digest is a GATE, not a note."
tar -tzf "${ARCHIVE}" | head -1 | grep -q '^reg_test_files-main/' \
  || die "the archive's top-level directory is not reg_test_files-main/ -- the test script
     chdirs into ./reg_test_files-main/ConvergentChannel by that literal name"
log "G-FIXTURE: sha256 ${GOT_SHA} matches the recorded provenance; top-level name confirmed"

# --------------------------------------------------------------- G-ROOT --
for a in "${ARMS[@]}"; do
  [ ! -e "${ROOT}/${a}" ] || die "arm directory ${ROOT}/${a} ALREADY EXISTS -- refusing to
     write into a directory that may hold another run's answer"
done
mkdir -p "${ROOT}" || die "cannot create ${ROOT}"
log "G-ROOT: ${ROOT} ready; no arm directory pre-existed"

# ------------------------------------------------------------- the arms --
run_arm() {
  local ARM="$1" IMG DIG
  case "${ARM}" in
    S) IMG="${IMG_S}"; DIG="${DIG_S}" ;;
    P) IMG="${IMG_P}"; DIG="${DIG_P}" ;;
    *) die "unknown arm '${ARM}' (S or P)" ;;
  esac

  # Toolchain identity is the DIGEST, never the tag and never the version string.
  local live
  live="$(sudo -n docker inspect --format '{{.Id}}' "${IMG}" 2>/dev/null)"
  [ "${live}" = "${DIG}" ] \
    || { echo "{\"arm\":\"${ARM}\",\"verdict_hint\":\"BLOCKED\",\"reason\":\"image ${IMG} is ${live}, registered ${DIG}\"}" \
           > "${ROOT}/${ARM}_IMAGE_REFUSAL.json"; die "IMAGE DIGEST: ${IMG} is ${live}, registered ${DIG}"; }

  local A="${ROOT}/${ARM}"
  mkdir -p "${A}" || die "cannot create ${A}"
  chmod 777 "${A}"

  cat > "${A}/fadr_expected.md5" <<MD5EOF
${MD5_REG}  runRegTests_DASimpleFoamForward.py
${MD5_TF}  testFuncs.py
${MD5_REF}  refs/DAFoam_Test_DASimpleFoamForwardRef.txt
MD5EOF

  # The in-container recipe.  Steps 1, 3 and 4 are tests/Allrun:20-37 VERBATIM.
  # Step 2 is this item's ONE disclosed addition (PREREGISTRATION.md section 4.1):
  # it copies the produced output aside BEFORE the comparator runs, because
  # upstream's reg_file_comp REWRITES the file it compares.
  cat > "${A}/fadr_cmd.sh" <<CMDEOF
set -u
cd /mnt/${ARM} || exit 30
tar -xzf /fixture/reg_test_files-main.tar.gz -C . || exit 31
cp -a /home/dafoamuser/dafoam/repos/dafoam/tests ./tests || exit 32
mv reg_test_files-main ./tests/ || exit 33
cd tests || exit 34
md5sum -c ../fadr_expected.md5 >../MD5_CHECK.txt 2>&1 || exit 35
cp runRegTests_DASimpleFoamForward.py ../AGE_DATUM_runRegTests_DASimpleFoamForward.py || exit 36
touch ../AGE_DATUM_runRegTests_DASimpleFoamForward.py
cp refs/DAFoam_Test_DASimpleFoamForwardRef.txt ../DAFoam_Test_DASimpleFoamForwardRef.txt || exit 37
sleep 1
# OpenMPI refuses to run as uid 0 without these two.  They confirm a choice; they
# change NO numerical setting and leave the command line unmodified.
export OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
rm -rf DAFoam_Test_DASimpleFoamForward.txt
timeout -k 60 ${DEADLINE} mpirun --oversubscribe -np ${NP} python runRegTests_DASimpleFoamForward.py | tee DAFoam_Test_DASimpleFoamForward.txt
MPIRC=\${PIPESTATUS[0]}
cp DAFoam_Test_DASimpleFoamForward.txt ../DAFoam_Test_DASimpleFoamForward.RAW.txt 2>/dev/null
sed -i 's/\[0m//g' DAFoam_Test_DASimpleFoamForward.txt 2>/dev/null
sed -i 's/[^[:print:]\t]//g' DAFoam_Test_DASimpleFoamForward.txt 2>/dev/null
python testFuncs.py refs/DAFoam_Test_DASimpleFoamForwardRef.txt DAFoam_Test_DASimpleFoamForward.txt
CMPRC=\$?
BANNER=\$(grep -c 'Primal solution failed!' ../DAFoam_Test_DASimpleFoamForward.RAW.txt 2>/dev/null || echo 0)
NVAL=\$(grep -c '^@value' ../DAFoam_Test_DASimpleFoamForward.RAW.txt 2>/dev/null || echo 0)
echo "MPIRC=\${MPIRC}" > ../RC.txt
echo "CMPRC=\${CMPRC}" >> ../RC.txt
echo "BANNER=\${BANNER}" >> ../RC.txt
echo "NVAL=\${NVAL}" >> ../RC.txt
exit 0
CMDEOF

  local NAME="fadr_${ARM}_$(date -u +%Y%m%dT%H%M%SZ)_$$"
  local T0 T1
  T0=$(date +%s)
  log "ARM ${ARM}: launching ${IMG} (${DIG}) cpuset=${CPUSET} np=${NP} mem=${MEM} deadline=${DEADLINE}s"
  sudo -n docker run -d --name "${NAME}" \
      --user 0:0 --cpuset-cpus="${CPUSET}" --memory="${MEM}" --memory-swap="${MEM}" \
      --oom-score-adj=500 \
      -v "${ROOT}":/mnt -v "${STORE}":/fixture:ro -w "/mnt/${ARM}" \
      "${IMG}" bash -lc "bash /mnt/${ARM}/fadr_cmd.sh" \
      > "${A}/container_id.txt" 2>"${A}/container_launch_err.txt" \
    || { log "ARM ${ARM}: docker run FAILED"; echo "docker_run_failed" > "${A}/LAUNCH_FAILED"; return 1; }

  sudo -n docker wait "${NAME}" > "${A}/docker_wait_rc.txt" 2>/dev/null
  T1=$(date +%s)
  local DRC
  DRC="$(sudo -n docker inspect --format '{{.State.ExitCode}}' "${NAME}" 2>/dev/null)"
  sudo -n docker logs "${NAME}" > "${A}/container.log" 2>&1
  sudo -n docker rm -f "${NAME}" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "${A}" 2>/dev/null

  local MPIRC CMPRC BANNER NVAL
  MPIRC="null"; CMPRC="null"; BANNER="null"; NVAL="null"
  if [ -f "${A}/RC.txt" ]; then
    MPIRC="$(grep '^MPIRC=' "${A}/RC.txt" | cut -d= -f2)"
    CMPRC="$(grep '^CMPRC=' "${A}/RC.txt" | cut -d= -f2)"
    BANNER="$(grep '^BANNER=' "${A}/RC.txt" | cut -d= -f2)"
    NVAL="$(grep '^NVAL=' "${A}/RC.txt" | cut -d= -f2)"
  fi
  local BANNER_BOOL="null"
  [ "${BANNER}" = "null" ] || { [ "${BANNER}" -gt 0 ] && BANNER_BOOL="true" || BANNER_BOOL="false"; }

  cat > "${A}/ARM_STATUS.json" <<STEOF
{
  "arm": "${ARM}",
  "image": "${IMG}",
  "image_digest_verified_live": "${live}",
  "cpuset": "${CPUSET}",
  "ranks": ${NP},
  "wall_s": $((T1 - T0)),
  "core_min": $(python3 -c "print(round(($T1-$T0)*${NP}/60.0,4))"),
  "docker_rc": ${DRC:-null},
  "mpirun_rc": ${MPIRC},
  "comparator_rc": ${CMPRC},
  "n_value_lines_raw": ${NVAL},
  "primal_failure_banner": ${BANNER_BOOL},
  "freeze_sha": "${SHA}",
  "fixture_sha256": "${GOT_SHA}",
  "utc_end": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
STEOF
  log "ARM ${ARM}: docker_rc=${DRC} mpirun_rc=${MPIRC} comparator_rc=${CMPRC} values=${NVAL} banner=${BANNER_BOOL} wall=$((T1-T0))s"
}

for a in "${ARMS[@]}"; do
  run_arm "${a}" || log "ARM ${a}: driver-level failure recorded, chain continues to the next row"
done

# ------------------------------------------------------------- the grader --
# rc from the grader is INFRASTRUCTURE, never the verdict (L-342).
log "grading"
python3 "${CASE_DIR}/fadr_grade.py" --run-root "${ROOT}" \
        --json-out "${ROOT}/FADR_GRADE.json" | tee "${ROOT}/FADR_GRADE.txt"
GRC=${PIPESTATUS[0]}
log "grader rc=${GRC} (INFRASTRUCTURE, not the verdict)"
exit 0
