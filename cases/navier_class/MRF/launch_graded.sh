#!/usr/bin/env bash
# MRF_R1 GRADED LEVEL LAUNCHER  --  usage: launch_graded.sh <RUNDIR> <RANKS> <ENDTIME> [STAGGER_S]
#
# v2, promoted 2026-09-10T22:33Z, AFTER all three graded levels had written
# RC.txt.  It was authored as a separate staging file rather than edited in
# place because medium and fine were still EXECUTING v1 at the time: bash reads
# a script incrementally by byte offset as it runs, so editing a running script
# can make the interpreter resume mid-token in a file whose bytes have shifted
# -- corrupting a live graded solve to improve a launcher, with a failure that
# would look like the solve's fault.  RULE, adopted by the cfd-supervisor:
# "THE LAUNCHER IS NOT CURRENTLY RUNNING" IS A PRECONDITION FOR EDITING ONE.
# Check it with a query that cannot match itself -- `pgrep -f launch_graded`
# matches the very shell running the check (measured: it returned two pids that
# were its own and already gone).  Test the script arg, and cross-check the
# unspoofable fact that no solver process is alive.
#
#   Registration: verification/campaign/MRF_R1_PREREGISTRATION.md
#   Frozen at commit ceacb3a2, registration blob 54aecef3.  THIS SCRIPT CHANGES
#   NOTHING IN IT.  The only controlDict edit is endTime (the controlDict's own
#   comment says "graded run: 4000, set by launcher").
#
# THE rc DISCIPLINE (prereg sec.5 clause 1; memory: setsid-parent-returns-zero).
#   `setsid timeout cmd` exits 0 for EVERY outcome including SIGFPE.  Every rc
#   below is captured INSIDE this wrapper from the process itself, never
#   inferred from the exit status of whatever launched it and never from an
#   `End` line.  The solver's own rc lands in RC.txt.
#
# THE LAUNCH-WITNESS DISCIPLINE (verification ruling 2026-09-10, adopted here).
#   `launched: true` is asserted FROM THE CHILD by two witnesses -- (a) liveness
#   of a SOLVER's own pid, never the setsid/nohup/mpirun parent's, which is
#   alive in every outcome; and (b) a first artifact the child produced.
#   Neither obtainable -> `launched: false` WITH A REASON.  And the wrapper's
#   own stderr is NEVER discarded: `>/dev/null 2>&1` on the bashrc source is
#   exactly what turned a loud abort into a silent one on 2026-09-10.
#
# REFUSES rather than proceeds (prereg sec.5 clause 7 / rule 4 age guard):
#   - a numeric time directory > 0 already exists  -> the age-guard precondition
#     is already broken; refuse.  NOTHING IS EVER DELETED to clear this.
#   - RC.txt already exists                        -> a graded run already ran.
#   - the MRFProperties active-toggle does not read back on either side.
#
# NEVER `rm -rf $RUNDIR` (prereg A1.5: build_mesh.sh opens that way and pointed
# at a graded level it deletes it).  constant/polyMesh is NEVER touched here.
set -u

RUNDIR="${1:?usage: launch_graded.sh <RUNDIR> <RANKS> <ENDTIME> [STAGGER_S]}"
RANKS="${2:?ranks}"
ENDTIME="${3:?endTime}"
STAGGER="${4:-0}"

cd "$RUNDIR" || exit 3
exec > LAUNCH.log 2>&1
# Rung-neutral label: this launcher is SHARED between MRF rungs, and hardcoding
# "MRF_R1" mislabelled every R2 artifact it wrote (found on R2 fine, 2026-09-11).
# The rundir below carries the rung; the banner must not contradict it.
echo "=== MRF graded launch  $(date -u +%FT%TZ)  rundir=$RUNDIR ranks=$RANKS endTime=$ENDTIME"

fail() { echo "REFUSE: $*"; echo "REFUSED" > RC.txt; exit 2; }

# ---- guards ---------------------------------------------------------------
[ -e RC.txt ] && { echo "REFUSE: RC.txt exists -- a graded run already ran here"; exit 2; }
EXTRA=$(find . -maxdepth 1 -type d -regextype posix-extended -regex '\./[0-9]+(\.[0-9]+)?' \
        ! -name 0 -printf '%f ' 2>/dev/null)
[ -n "$EXTRA" ] && fail "time directories already present ($EXTRA); age-guard precondition broken"
[ -d 0.orig ]   || fail "no 0.orig"
[ -d constant/polyMesh ] || fail "no polyMesh"

MESH_MD5_BEFORE=$(cat constant/polyMesh/points constant/polyMesh/faces \
                      constant/polyMesh/owner constant/polyMesh/neighbour \
                      constant/polyMesh/cellZones | md5sum | cut -d' ' -f1)
echo "mesh md5 before: $MESH_MD5_BEFORE"

[ "$STAGGER" -gt 0 ] && { echo "stagger ${STAGGER}s"; sleep "$STAGGER"; }

# ---- OpenFOAM env: stderr CAPTURED, never discarded -----------------------
# `set -u` + this bashrc = the shell EXITS at
#   /usr/lib/openfoam/openfoam2606/etc/bashrc: line 184: WM_PROJECT_DIR: unbound variable
# rc=127, BEFORE fail() can run -- the launcher dies writing no RC.txt and no
# refusal.  `set -u` is kept for the rest of the script and lifted ONLY across
# the source; the output goes to log.env so an erased error and an error that
# never happened do not leave the same trace.
set +u
source /usr/lib/openfoam/openfoam2606/etc/bashrc > log.env 2>&1
ENV_RC=$?
set -u
if [ "$ENV_RC" -ne 0 ] || ! command -v simpleFoam >/dev/null 2>&1; then
    echo "----- captured output of etc/bashrc (log.env) -----"; cat log.env
    fail "OpenFOAM env did not load (source rc=$ENV_RC, simpleFoam not on PATH)"
fi
echo "OpenFOAM env OK: $(command -v simpleFoam)  (source rc=$ENV_RC, output in log.env)"

# ---- endTime, substituted with an assert on both sides (L-221/L-222) ------
N=$(grep -cE '^endTime +[0-9]+;' system/controlDict)
[ "$N" = "1" ] || fail "expected exactly 1 endTime line in controlDict, found $N"
sed -i -E "s/^endTime +[0-9]+;/endTime         ${ENDTIME};/" system/controlDict
grep -qE "^endTime +${ENDTIME};" system/controlDict || fail "endTime substitution did not read back"
echo "endTime set to $ENDTIME (read back OK)"
grep -E '^(deltaT|writeInterval|writeControl|startFrom|stopAt)' system/controlDict

# ---- 0/ is created LAST before compute: it dates the run (rule 4 age guard)
rm -rf 0 && cp -r 0.orig 0 || fail "could not stage 0/ from 0.orig"
STAGE_EPOCH=$(stat -c %Y 0)
echo "0/ staged at $(date -u -d @$STAGE_EPOCH +%FT%TZ) -- this is the age-guard baseline"

# ---- potentialFoam init with the MRF zone DEACTIVATED (prereg sec.4) ------
# sec.4: "init is run with active false, no -writephi, then restored".
# -writephi is NOT passed (F8 sec.15: it writes a toxic absolute-frame flux).
ORIG_MRF_MD5=$(md5sum < constant/MRFProperties)
N=$(grep -c '^    active      yes;$' constant/MRFProperties)
[ "$N" = "1" ] || fail "expected exactly 1 'active yes' in MRFProperties, found $N"
cp constant/MRFProperties constant/MRFProperties.graded
sed -i 's/^    active      yes;$/    active      no;/' constant/MRFProperties
grep -q '^    active      no;$' constant/MRFProperties || fail "MRF deactivate did not read back"

potentialFoam > log.potentialFoam 2>&1; PF_RC=$?
echo "$PF_RC" > rc.potentialFoam
echo "potentialFoam(MRF inactive) rc=$PF_RC"

cp constant/MRFProperties.graded constant/MRFProperties
[ "$(md5sum < constant/MRFProperties)" = "$ORIG_MRF_MD5" ] \
  || fail "MRFProperties restore is NOT byte-identical to the original"
grep -q '^    active      yes;$' constant/MRFProperties \
  || fail "PRE-SOLVE ASSERT: MRF zone is not active -- refusing to solve wrong physics"
echo "MRF restored and asserted active BEFORE the solve"
[ "$PF_RC" = "0" ] || fail "potentialFoam rc=$PF_RC"

# ---- decompose ------------------------------------------------------------
cat > system/decomposeParDict <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains ${RANKS};
method          scotch;
EOF
decomposePar -force > log.decomposePar 2>&1; DP_RC=$?
echo "$DP_RC" > rc.decomposePar
[ "$DP_RC" = "0" ] || fail "decomposePar rc=$DP_RC"
echo "decomposePar rc=0 into $RANKS subdomains"

# ---- THE GRADED SOLVE.  rc captured from the solver itself. ---------------
echo "$RANKS" > RANKS.txt
date -u +%FT%TZ > SOLVE_START_UTC.txt
T0=$(date +%s)
mpirun -np "$RANKS" simpleFoam -parallel > log.simpleFoam 2>&1 &
MPIRUN_PID=$!

# ---- THE TWO LAUNCH WITNESSES, both taken FROM THE CHILD ------------------
# (a) a live SOLVER pid -- an actual `simpleFoam` process, NOT this wrapper,
#     NOT the setsid parent and NOT mpirun (all three are alive in every
#     outcome, which is precisely why none of them is a witness);
# (b) a first artifact ONLY THE SOLVER can have produced -- the first
#     `^ExecutionTime` line.
#
#     *** NOT `^Time = `.  ***  Found by dafoam 2026-09-10 and CONFIRMED here
#     against this case's own logs: `decomposePar` PRINTS `Time = 0`
#     (verification/runs/navier_class/MRF/coarse/log.decomposePar line 99) and
#     prints NO ExecutionTime line at all.  A witness keyed on `Time = ` can
#     therefore declare LAUNCHED on decomposePar, before the solver exists --
#     the same class of defect as the one this file was written to fix: a
#     witness that fires on the wrong actor.
#     This launcher happened to be immune because decomposePar goes to its own
#     log.decomposePar and the witness reads log.simpleFoam (measured: 4000
#     `^Time = ` vs 4000 `^ExecutionTime`, no off-by-one).  That immunity is an
#     accident of file separation and one refactor would undo it, so the
#     witness is corrected rather than left to rely on it.
#     ExecutionTime is emitted only by the solver, once per completed
#     iteration; in coarse's log `Time = 1` is line 89 and the first
#     `ExecutionTime` line 100, so the stricter witness costs ~11 lines.
SOLVER_PIDS=""; FIRST_TIME=""
for _ in $(seq 1 90); do
    [ -z "$SOLVER_PIDS" ] && SOLVER_PIDS=$(pgrep -P "$MPIRUN_PID" -x simpleFoam 2>/dev/null | tr '\n' ' ')
    [ -z "$FIRST_TIME" ]  && FIRST_TIME=$(grep -m1 '^ExecutionTime' log.simpleFoam 2>/dev/null)
    [ -n "$SOLVER_PIDS" ] && [ -n "$FIRST_TIME" ] && break
    kill -0 "$MPIRUN_PID" 2>/dev/null || break     # mpirun already gone; stop waiting
    sleep 2
done
if [ -n "$SOLVER_PIDS" ] && [ -n "$FIRST_TIME" ]; then
    { echo "launched: true"
      echo "witness_a_solver_pids: $SOLVER_PIDS"
      echo "witness_b_first_artifact: $FIRST_TIME"
      echo "mpirun_pid: $MPIRUN_PID   (NOT a witness -- alive in every outcome)"
      echo "utc: $(date -u +%FT%TZ)"; } > LAUNCHED.txt
else
    { echo "launched: false"
      echo "reason: witness_a_solver_pids='${SOLVER_PIDS:-NONE}' witness_b_first_artifact='${FIRST_TIME:-NONE}'"
      echo "mpirun_pid: $MPIRUN_PID alive=$(kill -0 "$MPIRUN_PID" 2>/dev/null && echo yes || echo no)"
      echo "utc: $(date -u +%FT%TZ)"; } > LAUNCHED.txt
fi
cat LAUNCHED.txt

wait "$MPIRUN_PID"; SF_RC=$?
T1=$(date +%s)
WALL=$((T1-T0))
echo "$WALL" > WALL_SECONDS_SOLVE.txt
awk -v w="$WALL" -v r="$RANKS" 'BEGIN{printf "%.2f\n", w*r/60.0}' > CORE_MINUTES.txt
echo "simpleFoam rc=$SF_RC  wall=${WALL}s  ranks=$RANKS  core-min=$(cat CORE_MINUTES.txt)"

# ---- reconstruct ONLY the latest time (the graded fields at endTime) ------
if [ "$SF_RC" = "0" ]; then
  reconstructPar -latestTime > log.reconstructPar 2>&1; RP_RC=$?
  echo "$RP_RC" > rc.reconstructPar
  echo "reconstructPar -latestTime rc=$RP_RC"
fi

MESH_MD5_AFTER=$(cat constant/polyMesh/points constant/polyMesh/faces \
                     constant/polyMesh/owner constant/polyMesh/neighbour \
                     constant/polyMesh/cellZones | md5sum | cut -d' ' -f1)
[ "$MESH_MD5_AFTER" = "$MESH_MD5_BEFORE" ] \
  && echo "mesh md5 UNCHANGED: $MESH_MD5_AFTER" \
  || echo "WARNING: mesh md5 CHANGED $MESH_MD5_BEFORE -> $MESH_MD5_AFTER"

# The solver's own rc, written LAST, so its existence means the solve stage
# completed and was measured.
#
# BOTH NAMES, and the second one is not decoration: grade_mrf_np.py:251 reads
# `<case_dir>/rc` and REFUSES the level outright if that exact filename is
# absent -- "no rc sidecar; rc==0 cannot be verified".  v1 wrote only RC.txt,
# so the first graded attempt on a triple that had run perfectly REFUSED on a
# FILENAME.  The frozen grader is the authority on the name; the launcher
# conforms to it, never the reverse.
echo "$SF_RC" > RC.txt
echo "$SF_RC" > rc
echo "=== done $(date -u +%FT%TZ)  RC.txt=$SF_RC"
