#!/usr/bin/env bash
# FADR -- the INBOUND retrieval of DAFoam's own regression fixture, and the
# provenance record it writes.  PREREGISTRATION.md section 2 is the authority.
#
# INBOUND ONLY.  Nothing of this lab leaves the box in this act: no account, no
# login, no token, no header carrying lab data, no issue, no comment, no upload.
# SUBMISSIONS REMAIN PARKED (standing rule 7).
#
# Standing rule 15: the sha256 is PROVENANCE, NOT IDENTIFICATION.  This script
# OPENS the archive and records what it SAW inside -- never a filename, never a
# file type, never a hash alone.
#
# Refuses (exit 2) rather than degrading, at every step.

set -u
set -o pipefail

URL="https://github.com/DAFoam/reg_test_files/archive/refs/heads/main.tar.gz"
STORE="/home/ubuntu/certonomous-runs/FADR-fixture"
ARCHIVE="${STORE}/reg_test_files-main.tar.gz"
CASE_DIR="/home/ubuntu/Certonomous/cases/dafoam/curriculum_FADR"
PROV="${CASE_DIR}/FIXTURE_PROVENANCE.md"

die() { echo "REFUSAL: $*" >&2; exit 2; }

# --- guard: never silently reuse or silently overwrite -----------------------
if [ -e "${ARCHIVE}" ]; then
  die "the archive already exists at ${ARCHIVE}. This script never overwrites a
     fixture: a second retrieval with a different digest would rewrite provenance
     that a frozen driver already gates on. Inspect it, do not re-fetch."
fi
if [ -e "${PROV}" ]; then
  die "${PROV} already exists. Provenance is written once."
fi
mkdir -p "${STORE}" || die "cannot create ${STORE}"

UTC_START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- the retrieval -----------------------------------------------------------
# --no-check-certificate is upstream's own flag (tests/Allrun:13); it is NOT
# used here.  A retrieval that needs certificate checking disabled is a
# retrieval whose provenance this lab cannot state, and it would be refused.
if ! wget --tries=3 --timeout=60 -q -O "${ARCHIVE}" "${URL}"; then
  rm -f "${ARCHIVE}"
  die "wget failed for ${URL} at ${UTC_START} -- branch P-C: the item is BLOCKED
     on the fixture and NOTHING is concluded about DAFoam."
fi

UTC_DONE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
SHA="$(sha256sum "${ARCHIVE}" | awk '{print $1}')" || die "sha256sum failed"
BYTES="$(stat -c %s "${ARCHIVE}")" || die "stat failed"
[ "${BYTES}" -gt 1024 ] || die "archive is ${BYTES} B -- too small to be the fixture"

# --- CONTENT VERIFICATION: OPEN IT, AND SAY WHAT WAS SEEN (rule 15) ----------
WORK="$(mktemp -d)" || die "mktemp failed"
trap 'rm -rf "${WORK}"' EXIT
tar -xzf "${ARCHIVE}" -C "${WORK}" || die "the archive does not extract as gzip+tar"

ROOT="$(find "${WORK}" -mindepth 1 -maxdepth 1 -type d | head -1)"
[ -n "${ROOT}" ] || die "the archive holds no top-level directory"
CC="${ROOT}/ConvergentChannel"
[ -d "${CC}" ] || die "no ConvergentChannel case in the archive -- this is NOT the
     fixture runRegTests_DASimpleFoamForward.py chdirs into (it does
     os.chdir('./reg_test_files-main/ConvergentChannel'))"

# Every path the test script actually reaches for, checked by EXISTENCE.
MISSING=""
for p in 0 0.incompressible system system.incompressible \
         constant/turbulenceProperties.sa FFD/FFD.xyz; do
  [ -e "${CC}/${p}" ] || MISSING="${MISSING} ${p}"
done
[ -z "${MISSING}" ] || die "ConvergentChannel is missing:${MISSING}"

# Read INSIDE two files and confirm they are what they claim to be, by CONTENT.
CD_HDR="$(grep -m1 -E '^\s*(class|object)\s' "${CC}/system/controlDict" 2>/dev/null | tr -s ' ')"
grep -q 'OpenFOAM' "${CC}/system/controlDict" \
  || die "ConvergentChannel/system/controlDict carries no OpenFOAM banner --
     verified by CONTENT, and it failed"
FFD_L1="$(head -1 "${CC}/FFD/FFD.xyz" | tr -d '\r')"
FFD_L2="$(sed -n 2p "${CC}/FFD/FFD.xyz" | tr -d '\r')"
NCELLS_HINT="$(grep -c . "${CC}/FFD/FFD.xyz" 2>/dev/null || echo 0)"
TOP_LISTING="$(tar -tzf "${ARCHIVE}" | head -25)"
N_ENTRIES="$(tar -tzf "${ARCHIVE}" | wc -l)"
N_CASES="$(find "${ROOT}" -mindepth 1 -maxdepth 1 -type d | wc -l)"
CASE_NAMES="$(find "${ROOT}" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort | tr '\n' ' ')"

# --- the provenance record ---------------------------------------------------
cat > "${PROV}" <<PROV_EOF
# FADR fixture provenance -- the INBOUND retrieval, recorded under PREREGISTRATION.md section 2

**INBOUND ONLY. Nothing of this lab left the box in this act.** No account, no login, no token,
no header carrying lab data, no issue, no comment, no upload. **SUBMISSIONS REMAIN PARKED**
(\`CLAUDE.md\` standing rule 7). This record is the retrieval's whole evidentiary content.

| field | value |
|---|---|
| **source URL** | \`${URL}\` |
| **sha256** | \`${SHA}\` |
| **bytes** | ${BYTES} |
| **UTC, request issued** | ${UTC_START} |
| **UTC, retrieval complete** | ${UTC_DONE} |
| **stored at** | \`${ARCHIVE}\` (outside git: binary) |
| **retrieved by** | dafoam lane C, \`fadr_fetch_fixture.sh\` |
| **certificate checking** | ENABLED. Upstream's own \`tests/Allrun:13\` passes \`--no-check-certificate\`; this retrieval does NOT, because a retrieval needing certificate checking disabled is one whose provenance cannot be stated. |

## CONTENT VERIFICATION -- the archive was OPENED, and this is what was SEEN

**Standing rule 15: never by filename, never by file type, never by hash alone. The sha256 above is
PROVENANCE, NOT IDENTIFICATION.**

- The archive extracts as gzip+tar and holds **${N_ENTRIES} entries** under a single top-level
  directory \`$(basename "${ROOT}")\`.
- It holds **${N_CASES} case directories**: ${CASE_NAMES}
- **\`ConvergentChannel\` IS PRESENT** -- the case
  \`runRegTests_DASimpleFoamForward.py\` chdirs into
  (\`os.chdir("./reg_test_files-main/ConvergentChannel")\`).
- Every path the test script reaches for exists inside it, checked by EXISTENCE:
  \`0/\`, \`0.incompressible/\`, \`system/\`, \`system.incompressible/\`,
  \`constant/turbulenceProperties.sa\`, \`FFD/FFD.xyz\`.
- **Read INSIDE the files, not at them:** \`ConvergentChannel/system/controlDict\` carries the
  OpenFOAM banner and its class/object line reads \`${CD_HDR}\`. \`ConvergentChannel/FFD/FFD.xyz\`
  opens with \`${FFD_L1}\` then \`${FFD_L2}\` -- a PLOT3D FFD block, which is what
  \`OM_DVGEOCOMP(file="FFD/FFD.xyz", type="ffd")\` requires.
- First entries of the archive listing, as read:

\`\`\`
${TOP_LISTING}
\`\`\`

## WHAT THIS RECORD DOES NOT ESTABLISH

It does not establish that the fixture is unchanged from the one upstream's stored reference values
were produced against -- upstream publishes a moving \`main\` branch, not a tag, and the digest above
therefore pins **what this box received at ${UTC_DONE}**, nothing earlier. If the regression fails,
**fixture drift is a candidate explanation and is named here before the run**, not after it.

## THE DIGEST IS A GATE, NOT A NOTE

\`fadr_chain_driver.sh\` recomputes the sha256 at launch and **refuses (exit 2)** if it is not
\`${SHA}\`.
PROV_EOF

echo "FETCH COMPLETE"
echo "  url    ${URL}"
echo "  sha256 ${SHA}"
echo "  bytes  ${BYTES}"
echo "  utc    ${UTC_DONE}"
echo "  cases  ${CASE_NAMES}"
echo "  record ${PROV}"
exit 0
