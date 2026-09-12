#!/bin/bash
# resume_k2h.sh -- K2h L3 RESUME driver, for after the instance stop/start.
#
#   ./resume_k2h.sh --check-only    # every guard, mutates nothing, launches nothing
#   ./resume_k2h.sh                 # assert, re-point startFrom, DETACHED launch
#
# WHY stage_and_run_k2h.sh CANNOT DO THIS -- the same lesson launch_k2g.sh taught.
# Its staging block REFUSES when `0/` or any time directory exists (both do now),
# and its G-03 asserts `startFrom startTime` / `startTime 0`, which are the
# INITIAL-LAUNCH values. Running it would refuse; forcing it would re-arm `0/`
# from 0.orig and destroy the t=5 checkpoint. It is neither edited nor called.
#
# THE ONE CHANGE THIS DRIVER MAKES, AND WHAT IT DOES NOT TOUCH.
# `startFrom startTime; startTime 0;` becomes `startFrom latestTime;`. Nothing
# else moves: endTime 112, writeInterval 5, purgeWrite 16 and the fieldAverage
# `timeStart 42` are all ASSERTED UNCHANGED below and refuse if they are not.
# S-SETTLE and S-WINDOW are ABSOLUTE simulated times (42 s and 42-112 s), so a
# resume at t=5 changes neither, and no gate, threshold, band, cap or label
# moves. THE REGISTRATION IS NOT EDITED BY THIS SCRIPT. It owes a dated addendum
# recording this re-point, and writing that is the supervisor's call, not this
# lane's.
#
# EXIT MAP: 0 OK, 2 REFUSE. No verdict is carried by an exit code.
set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO=/home/ubuntu/Certonomous
CASE="$HERE/K2h_L3"
CD="$CASE/system/controlDict"
PREREG="$REPO/docs/campaigns/F14-cooling-ladder/K2h_PREREGISTRATION.md"
RANKS=4
END_TIME=112
POINT_CORE_MIN=420
CAP_CORE_MIN=1260
MEM_NEED_GB=2.5
FIELDS="T U p_rgh alphat nut k omega phi"

CHECK_ONLY=0
[ "${1:-}" = "--check-only" ] && CHECK_ONLY=1
say()    { echo "[k2h-resume $(date -u +%H:%M:%SZ)] $*"; }
refuse() { echo "REFUSE: $*" >&2; exit 2; }

# --- G-01 FREEZE -------------------------------------------------------------
say "G-01 freeze verify"
REPO="$REPO" PREREG="$PREREG" python3 - <<'PYX' || exit 2
import hashlib, json, os, re, sys
repo, prereg = os.environ["REPO"], os.environ["PREREG"]
doc = open(prereg, "rb").read().decode()
m = re.search(r"```json FREEZE\n(.*?)```", doc, re.S)
if not m:
    print("REFUSE: no FREEZE block"); sys.exit(2)
bad = []
for rel, frozen in json.loads(m.group(1)).items():
    p = os.path.join(repo, rel)
    d = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None
    if d != frozen:
        bad.append("%s disk=%s frozen=%s" % (rel, (d or "ABSENT")[:12], frozen[:12]))
    else:
        print("  PINNED %-70s %s" % (rel, d[:16]))
if bad:
    print("REFUSE -- GRADING PATH NOT PINNED:\n  " + "\n  ".join(bad)); sys.exit(2)
PYX

# --- G-02 THE CHECKPOINT, and the ACCUMULATOR QUESTION ------------------------
say "G-02 resume checkpoint"
LATEST=""
for r in 0 1 2 3; do
  t=$(ls "$CASE/processor$r" 2>/dev/null | grep -E '^[0-9]+(\.[0-9]+)?$' \
      | sort -g | tail -1)
  [ -n "$t" ] || refuse "processor$r holds no time directory -- nothing to resume from"
  [ -z "$LATEST" ] && LATEST="$t"
  [ "$t" = "$LATEST" ] || refuse "RESUME-LATEST: processor$r's latest time is $t but processor0's is $LATEST -- the ranks DISAGREE and a resume from a torn checkpoint is not a resume"
  for f in $FIELDS; do
    p="$CASE/processor$r/$t/$f"
    [ -f "$p" ] || refuse "RESUME-FIELDS: $p absent"
    # closed by OpenFOAM's own end-of-file banner -- presence is not completeness
    tail -5 "$p" | grep -q '\*\*\*\*\*\*\*\*\*' \
      || refuse "RESUME-FIELDS: $p is present but NOT closed by OpenFOAM's end-of-file banner -- it was being written when the process stopped"
  done
  [ -d "$CASE/processor$r/0" ] || refuse "RESUME-ZERO: processor$r/0 absent"
done
[ -f "$CASE/0/T" ] || refuse "RESUME-ZERO: $CASE/0/T absent -- rule 4 clause 6 has no age referent"
say "  G-02 OK: all 4 ranks agree on latest time t=$LATEST, 8 fields each, banner-closed, 0/ present"

# --- G-02b THE ACCUMULATOR. The clause that would poison the number silently. --
TSTART=$(sed -e 's://.*::' "$CD" | sed -n 's/^[[:space:]]*timeStart[[:space:]]\+\([0-9.]\+\)[[:space:]]*;.*/\1/p' | head -1)
[ -n "$TSTART" ] || refuse "G-02b: controlDict carries no fieldAverage timeStart"
ACC=$(find "$CASE" -name 'fieldAverageProperties*' 2>/dev/null | head -1)
if [ -n "$ACC" ]; then
  # An accumulator EXISTS. It must be inside the resume time directory of EVERY
  # rank, or the average resumes from a partial state on some ranks and a blank
  # one on others -- a wrong number, not a crash.
  for r in 0 1 2 3; do
    [ -f "$CASE/processor$r/$LATEST/uniform/fieldAverageProperties" ] \
      || refuse "G-02b: an accumulator exists somewhere in this case but processor$r/$LATEST/uniform/fieldAverageProperties is ABSENT. Resuming would average a partial window on some ranks and a blank one on others. STOP and triage."
  done
  say "  G-02b OK: accumulator present on all 4 ranks at t=$LATEST; the average RESUMES"
else
  awk -v t="$LATEST" -v s="$TSTART" 'BEGIN{exit !(t+0 < s+0)}' \
    || refuse "G-02b: NO fieldAverageProperties exists anywhere, but the latest time $LATEST is at or past the registered timeStart $TSTART. Averaging should have begun and left an accumulator. Its absence is then a DEFECT, not a normal state. STOP and triage."
  say "  G-02b OK: no accumulator, and none is DUE -- latest time $LATEST is before the registered timeStart $TSTART, so averaging has not begun. Absence here is EXPECTED, and this guard proves it rather than assuming it."
fi

# --- G-03 every OTHER registered value asserted UNCHANGED ---------------------
cd_value() { sed -e 's://.*::' "$CD" \
  | sed -n "s/^$1[[:space:]]\+\([^;[:space:]]\+\)[[:space:]]*;.*/\1/p" | head -1; }
assert_cd() { local got; got="$(cd_value "$1")"
  [ -n "$got" ] || refuse "G-03: controlDict carries no top-level \`$1\`"
  [ "$got" = "$2" ] || refuse "G-03: controlDict \`$1\` is '$got', registered '$2'"
  say "    $1 = $got"; }
say "G-03 controlDict, every registered value except startFrom"
assert_cd application    buoyantBoussinesqPimpleFoam
assert_cd endTime        "$END_TIME"
assert_cd deltaT         0.005
assert_cd adjustTimeStep yes
assert_cd maxCo          2.0
assert_cd writeControl   adjustableRunTime
assert_cd writeInterval  5
assert_cd purgeWrite     16
grep -qE '^[[:space:]]*restartOnRestart[[:space:]]+false[[:space:]]*;' "$CD" \
  || refuse "G-03: fieldAverage does not declare restartOnRestart false -- a restart would DISCARD the accumulator and poison the number SILENTLY"
grep -qE '^[[:space:]]*timeStart[[:space:]]+42[[:space:]]*;' "$CD" \
  || refuse "G-03: fieldAverage timeStart is not the registered 42 s"
say "  G-03 OK"

# --- G-04/05 memory and cores -------------------------------------------------
AVAIL_GB=$(awk '/MemAvailable/ {printf "%.1f", $2/1048576}' /proc/meminfo)
awk -v a="$AVAIL_GB" -v n="$MEM_NEED_GB" 'BEGIN{exit !(a >= n + 2)}' \
  || refuse "memory: ${AVAIL_GB} GB available is not ${MEM_NEED_GB} GB + 2 GB headroom"
LIVE=$(pgrep -c -f '[F]oam -parallel' 2>/dev/null || echo 0)
if [ $((RANKS + LIVE)) -gt "$(nproc)" ]; then
  refuse "G-05 CORE GUARD, TRANSIENT BOX CONDITION AND NOT A DEFECT IN THIS CASE:
        $RANKS + $LIVE live ranks > $(nproc) cores. Retry in the next wave."
fi
say "G-04/05 OK: ${AVAIL_GB} GB available, $LIVE live ranks, $(nproc) cores"

if [ "$CHECK_ONLY" = "1" ]; then
  say "CHECK-ONLY: all guards pass. NOTHING WAS CHANGED AND NOTHING WAS LAUNCHED."
  exit 0
fi

# --- P-01 the ONE re-point, read back from disk -------------------------------
if [ "$(cd_value startFrom)" != "latestTime" ]; then
  cp -p "$CD" "$CD.pre_resume_$(date -u +%Y%m%dT%H%M%SZ)"
  sed -i 's/^startFrom[[:space:]]\+startTime;/startFrom latestTime;/' "$CD"
fi
[ "$(cd_value startFrom)" = "latestTime" ] \
  || refuse "P-01: startFrom did not become latestTime; controlDict reads '$(cd_value startFrom)'"
assert_cd endTime "$END_TIME"        # re-asserted AFTER the edit, not before
assert_cd writeInterval 5
assert_cd purgeWrite 16
say "  P-01 OK: startFrom = latestTime, and endTime/writeInterval/purgeWrite re-asserted after the edit"

# --- LAUNCH, detached, rc INSIDE ---------------------------------------------
cat > "$CASE/.k2h_inner.sh" <<'EOI'
set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
CASE="$1"; RANKS="$2"; HERE="$3"
cd "$CASE"
T0=$(date +%s); echo "$T0" > .k2h_t0
mpirun -np "$RANKS" buoyantBoussinesqPimpleFoam -parallel >> log.solve 2>&1
RC=$?
T1=$(date +%s); WALL=$((T1-T0))
if [ "$RC" = "0" ]; then reconstructPar -latestTime > log.reconstructPar 2>&1 || true; fi
CM=$(python3 -c "print(f'{$WALL*$RANKS/60:.3f}')")
EX=$(grep -oE 'ExecutionTime = [0-9.]+' log.solve | tail -1 | grep -oE '[0-9.]+$' || echo "")
NSTEP=$(grep -c '^ExecutionTime = ' log.solve || echo 0)
NOTE=clean
[ -f ABORT ] && NOTE=STOPPED_BY_REGISTERED_STOP_RULE
[ "$RC" != "0" ] && [ "$NOTE" = "clean" ] && NOTE=SOLVER_NONZERO_EXIT
{ echo "case=$(basename "$CASE")"; echo "rc=$RC"; echo "wall_s=$WALL"
  echo "ranks=$RANKS"; echo "core_min=$CM"
  echo "timeout_s=0_NO_KILLING_CAP_SANAA_20260912_17"
  echo "execution_time_s=$EX"; echo "n_timesteps=$NSTEP"
  echo "resumed=yes"; echo "solver=buoyantBoussinesqPimpleFoam"
  echo "note=$NOTE"; echo "ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } \
  > "$HERE/STATUS.$(basename "$CASE")"
EOI
chmod +x "$CASE/.k2h_inner.sh"
setsid bash "$CASE/.k2h_inner.sh" "$CASE" "$RANKS" "$HERE" </dev/null > "$CASE/.k2h_outer.out" 2>&1 &
echo $! > "$CASE/PIDS.solver"
setsid python3 "$REPO/verification/runs/F14-cooling-ladder/K2g_runs/monitor_k2g.py" \
  "$CASE" "$RANKS" "$POINT_CORE_MIN" "$CAP_CORE_MIN" R4 </dev/null > "$CASE/.monitor_outer.out" 2>&1 &
echo $! > "$CASE/PIDS.monitor"
say "RESUMED from t=$LATEST  solver_sid=$(cat "$CASE/PIDS.solver") monitor_sid=$(cat "$CASE/PIDS.monitor")"
exit 0
