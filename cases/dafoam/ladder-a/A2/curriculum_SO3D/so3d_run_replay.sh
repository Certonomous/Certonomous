#!/bin/bash
# so3d_run_replay.sh -- detached launcher for the SO-3D Stage-1 reader.
#
# THIS SCRIPT GRADES NOTHING AND COMPUTES NOTHING. It is infrastructure: it
# proves the frozen instrument is the one that ran, invokes it, and records the
# outcome. Every gate, threshold, plant and refusal lives in so3d_replay.py.
#
# WHY THE rc IS CAPTURED INSIDE. `setsid timeout cmd` exits 0 for every outcome
# of what it wraps, so an rc taken AROUND the setsid line records success for a
# crash. It is captured here, inside the detached wrapper, immediately after the
# reader returns, and written to STATUS.SO3D with the wall clock and a UTC stamp.
# The record does not depend on any agent still being alive.
#
# EVERY VARIABLE THIS SCRIPT REFERENCES IS DEFINED IN IT. `set -u` turns an
# undefined name into a bash error with no abort text of its own -- the exact
# failure A1WRT's recovered repair carried (board S-42 §1). Nothing below is
# referenced before it is assigned.

set -uo pipefail

REPO="/home/ubuntu/Certonomous"
CASE="${REPO}/cases/dafoam/ladder-a/A2/curriculum_SO3D"
REL="cases/dafoam/ladder-a/A2/curriculum_SO3D/so3d_replay.py"
READER="${CASE}/so3d_replay.py"
RUN_ROOT="/home/ubuntu/certonomous-runs/CURRICULUM-SO3D-a2-wing-multipoint-rootcause"
STATUS="${CASE}/STATUS.SO3D"
STAMP="$(date -u +%Y-%m-%dT%H%M%SZ)"
OUT="${CASE}/SO3D_replay_${STAMP}.out"
RANKS=1

say() { printf '%s\n' "$*" >> "${STATUS}"; }

: > "${STATUS}"
say "SO3D STAGE 1 -- launcher record"
say "launched_utc   ${STAMP}"
say "launcher       ${CASE}/so3d_run_replay.sh"
say "reader         ${READER}"
say "run_root       ${RUN_ROOT}"
say "ranks          ${RANKS}"
say "cap_core_min_registered 12.0"
say "solver_core_min_cap     0.0"
say ""

# ---- G1: the frozen file must BE the file that runs (CLAUDE.md rule 2) -----
BLOB_HEAD="$(cd "${REPO}" && git rev-parse "HEAD:${REL}" 2>/dev/null)"
BLOB_DISK="$(cd "${REPO}" && git hash-object "${REL}" 2>/dev/null)"
MD5_DISK="$(md5sum "${READER}" | cut -d' ' -f1)"
say "grading_path_blob_at_HEAD ${BLOB_HEAD}"
say "grading_path_blob_on_disk ${BLOB_DISK}"
say "reader_md5                ${MD5_DISK}"
if [ -z "${BLOB_HEAD}" ] || [ -z "${BLOB_DISK}" ]; then
  say "ABORT G1: could not hash the reader against its committed blob. UNMEASURED, not assumed."
  say "rc 6"
  exit 6
fi
if [ "${BLOB_HEAD}" != "${BLOB_DISK}" ]; then
  say "ABORT G1: the reader on disk is NOT the committed grading path."
  say "ABORT G1: HEAD ${BLOB_HEAD} vs disk ${BLOB_DISK}. The grading path is fixed at"
  say "ABORT G1: the pre-registration commit and a substituted file is not it."
  say "rc 6"
  exit 6
fi
say "G1 OK   the reader on disk IS the committed grading path"

# ---- G2: the run root must be absent BEFORE the reader is invoked ---------
if [ -e "${RUN_ROOT}" ]; then
  say "ABORT G2: run root already exists. Archive by mv, never delete."
  say "rc 7"
  exit 7
fi
say "G2 OK   run root ABSENT at launch"
say ""

# ---- invoke, and capture the rc INSIDE this wrapper ------------------------
T0="$(date +%s.%N)"
python3 "${READER}" > "${OUT}" 2>&1
RC=$?
T1="$(date +%s.%N)"
WALL="$(python3 -c "print('%.3f' % (${T1} - ${T0}))")"
CORE="$(python3 -c "print('%.4f' % ((${T1} - ${T0}) * ${RANKS} / 60.0))")"
USD="$(python3 -c "print('%.6f' % ((${T1} - ${T0}) * ${RANKS} / 3600.0 * 0.0513))")"

say "finished_utc   $(date -u +%Y-%m-%dT%H%M%SZ)"
say "rc             ${RC}"
say "wall_s         ${WALL}"
say "core_min       ${CORE}   [MEASURED, wall_s x ranks / 60]"
say "usd            ${USD}    [DERIVED at the owner-stated \$0.0513/core-h; REPORTED-BY-OWNER, NOT MEASURED]"
say "stdout         ${OUT}"
say "result_json    ${RUN_ROOT}/so3d_replay.json"
say "plant_json     ${RUN_ROOT}/so3d_plant_report.json"
say ""
case "${RC}" in
  0) say "reader exit 0 -- every gate scored; verdicts are in so3d_replay.json" ;;
  2) say "reader exit 2 -- REFUSAL / NOT A RESULT" ;;
  3) say "reader exit 3 -- BLOCKED on the registered cost cap" ;;
  *) say "reader exit ${RC} -- UNREGISTERED EXIT CODE. This is a finding, not a result." ;;
esac
exit "${RC}"
