#!/usr/bin/env bash
# A1d bare-hull mesh build. Run BY THE RUNNER, never by hand (Sanaa item 19).
# Usage: build_barehull.sh <CASE_DIR> <LEVEL>
#
# rc is captured INSIDE this wrapper, never around a setsid line: `setsid timeout cmd`
# exits 0 for every outcome, so an outer rc is meaningless.
set -u
REPO=/home/ubuntu/Certonomous
CASE=${1:?case dir}
LEVEL=${2:?level}
A1D="$REPO/cases/navier_class/SUBOFF_A1d"
ST="$CASE/STATUS.build"
mkdir -p "$CASE"
: > "$ST"
say() { echo "$*" | tee -a "$ST"; }
fail() { say "BUILD_RC=$1"; say "BUILD_RESULT=FAILED at: $2"; exit "$1"; }

say "A1d BARE-HULL BUILD  case=$CASE  level=$LEVEL  started=$(date -u +%FT%TZ)"
say "run_as=$(id -un) uid=$(id -u)"
[ "$(id -u)" -eq 0 ] && fail 2 "running as root -- Sanaa item 6 forbids it"

# ---- GATE X5 FIRST, BEFORE ANYTHING IS BUILT --------------------------------
# A geometry gate that can only be evaluated after a build is a gate evaluated under
# pressure to pass. This runs against the analytic function, needs no mesh, and its
# --selftest arms the planted control before the real comparison.
say "--- GATE X5 (geometry vs Roddy 1990 Table 2, with planted control) ---"
python3 "$A1D/check_barehull_geometry.py" --selftest 2>&1 | tee -a "$ST"
X5=${PIPESTATUS[0]}
[ "$X5" -eq 0 ] || fail "$X5" "GATE X5 -- geometry rejected BEFORE it was meshed"
say "GATE X5: PASS"

# ---- emit the case ----------------------------------------------------------
say "--- emit case (geometry + dicts) ---"
python3 "$A1D/build_barehull_case.py" --case "$CASE" --level "$LEVEL" 2>&1 | tee -a "$ST"
RC=${PIPESTATUS[0]}; [ "$RC" -eq 0 ] || fail "$RC" "build_barehull_case.py"

cd "$CASE" || fail 2 "cd $CASE"
FOAM_BASHRC=$(ls -1 /usr/lib/openfoam/openfoam*/etc/bashrc 2>/dev/null | sort -V | tail -1)
[ -n "${FOAM_BASHRC:-}" ] || fail 2 "no OpenFOAM bashrc found under /usr/lib/openfoam/openfoam*/etc/"
say "sourcing $FOAM_BASHRC"
# shellcheck disable=SC1090
. "$FOAM_BASHRC" || fail 2 "sourcing $FOAM_BASHRC failed"

for STEP in blockMesh snappyHexMesh checkMesh; do
  say "--- $STEP ---"
  if [ "$STEP" = snappyHexMesh ]; then
    "$STEP" -overwrite > "log.$STEP" 2>&1; RC=$?
  else
    "$STEP" > "log.$STEP" 2>&1; RC=$?
  fi
  tail -3 "log.$STEP" | tee -a "$ST"
  [ "$RC" -eq 0 ] || fail "$RC" "$STEP (see $CASE/log.$STEP)"
  grep -q '^End' "log.$STEP" || fail 3 "$STEP produced no End line"
done

# ---- post-build refusals ----------------------------------------------------
B=constant/polyMesh/boundary
grep -qE '^\s+sail$' "$B" && fail 4 "a 'sail' patch exists -- A1d is HULL ONLY, wrong geometry built"
for P in inlet outlet farfield symm hull; do
  grep -qE "^\s+$P\$" "$B" || fail 4 "expected patch '$P' missing from $B"
done
NP=$(grep -cE '^\s{4}[a-zA-Z_]+$' "$B")
say "patches=$NP (expected 5)"
[ "$NP" -eq 5 ] || fail 4 "patch count $NP != 5"

CELLS=$(grep -m1 -oE 'cells: *[0-9]+' log.checkMesh | grep -oE '[0-9]+')
say "CELLS=$CELLS"
grep -qi 'Mesh OK' log.checkMesh && say "CHECKMESH=OK" || say "CHECKMESH=FAILED_CHECKS (read log.checkMesh; a finding, not a pass)"

say "BUILD_RC=0"
say "BUILD_RESULT=OK  finished=$(date -u +%FT%TZ)"
say "NOTE: the mesh is BUILT, not admitted. Admission and the A1d freeze block are the"
say "      cfd-supervisor's check 4, personally and undelegated."
exit 0
