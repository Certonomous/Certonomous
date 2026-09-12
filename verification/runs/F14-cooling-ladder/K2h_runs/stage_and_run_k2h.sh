#!/bin/bash
# stage_and_run_k2h.sh -- K2h L3 launcher.  K2h_PREREGISTRATION.md section 10.
#
#   ./stage_and_run_k2h.sh --check-only   # every guard, mutates nothing, launches nothing
#   ./stage_and_run_k2h.sh                # stage, assert, then DETACHED launch
#
# STAGING IS DONE HERE AND NOT BEFORE THE QUEUE, DELIBERATELY. The case's `0/` is
# armed AT LAUNCH so that `0/T` dates the run for rule 4 clause 6's age guard, and
# so the case carries NO time directory at enqueue time, which is what lets the
# validator's AGE-GUARD read it clean without any resume declaration. This is a
# FRESH LAUNCH of a new case, not a resume: the 803 fields are an INITIAL
# CONDITION copied in, not a checkpoint being continued.
#
# NO KILLING TIMEOUT. Sanaa's 2026-09-12 04:20Z directive #17: no run is stopped
# by a time or budget cap. The registered cap is carried as a FLAG by the monitor.
# rc is captured INSIDE the detached wrapper -- `setsid cmd` returns 0 for every
# outcome, so a wrapper measuring its exit from outside measures nothing.
#
# EXIT MAP: 0 OK, 2 REFUSE. No verdict is carried by an exit code.
set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO=/home/ubuntu/Certonomous
CASE="$HERE/K2h_L3"
SRC="$REPO/verification/runs/F14-cooling-ladder/K2g_runs/K2f_L3"
PREREG="$REPO/docs/campaigns/F14-cooling-ladder/K2h_PREREGISTRATION.md"
PREREG_SHA=db523d06a
RANKS=4
IC_TIME=803
END_TIME=112
POINT_CORE_MIN=420
CAP_CORE_MIN=1260
MEM_NEED_GB=2.5

CHECK_ONLY=0
[ "${1:-}" = "--check-only" ] && CHECK_ONLY=1
say()    { echo "[k2h $(date -u +%H:%M:%SZ)] $*"; }
refuse() { echo "REFUSE: $*" >&2; exit 2; }

# --- G-01 FREEZE: the grading path must hash as the registration pinned it -----
say "G-01 freeze verify"
REPO="$REPO" PREREG="$PREREG" python3 - <<'PYX' || exit 2
import hashlib, json, os, re, sys
repo, prereg = os.environ["REPO"], os.environ["PREREG"]
doc = open(prereg, "rb").read().decode()
m = re.search(r"```json FREEZE\n(.*?)```", doc, re.S)
if not m:
    print("REFUSE: no FREEZE block in the registration"); sys.exit(2)
bad = []
for rel, frozen in json.loads(m.group(1)).items():
    p = os.path.join(repo, rel)
    if not os.path.exists(p):
        bad.append("%s ABSENT" % rel); continue
    d = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if d != frozen:
        bad.append("%s sha256 disk=%s frozen=%s" % (rel, d[:12], frozen[:12]))
    else:
        print("  PINNED %-70s %s" % (rel, d[:16]))
if bad:
    print("REFUSE -- GRADING PATH NOT PINNED:\n  " + "\n  ".join(bad)); sys.exit(2)
PYX

# --- G-02 the initial-condition source must be real ---------------------------
say "G-02 initial condition at $SRC/processor*/$IC_TIME"
for r in 0 1 2 3; do
  d="$SRC/processor$r/$IC_TIME"
  [ -d "$d" ] || refuse "$d absent -- there is no initial condition to stage from"
  for f in T U p_rgh alphat nut k omega phi p; do
    [ -f "$d/$f" ] || refuse "$d/$f absent -- the initial condition is incomplete"
  done
done
say "  G-02 OK: 4 ranks x 9 fields at t=$IC_TIME"

# --- G-03 controlDict shape (Sanaa items 1-4) ---------------------------------
CD="$CASE/system/controlDict"
say "G-03 controlDict"
# ---------------------------------------------------------------------------
# DEFECT REPAIRED 2026-09-12T19:48Z, AND IT WAS THIS GUARD'S FAULT, NOT THE
# CASE'S.  The previous version tested `grep -qx "endTime 112;"` -- a WHOLE-LINE
# match -- against a controlDict whose registered values carry trailing `//`
# comments explaining them.  The file was CORRECT and byte-identical to its
# committed blob; the guard could not match it, and refused a good case at
# exit 2.  That is the mirror image of the failure this lab hunts: not a guard
# that cannot fire, but one that fires on the wrong thing, and it would have
# refused every future level of this family for the same reason.
#
# The repair reads the VALUE instead of the line: comments are stripped FIRST
# (so a commented-out `// endTime 112;` can never satisfy the test), only
# column-0 top-level keys are matched (so the function objects' own
# `writeInterval 1;` cannot be mistaken for the run's), and an ABSENT key
# REFUSES rather than passing -- an unevaluated policy is not a satisfied one.
# ---------------------------------------------------------------------------
cd_value() {   # $1 = top-level key; prints its value, or nothing if absent
  sed -e 's://.*::' "$CD" \
    | sed -n "s/^$1[[:space:]]\+\([^;[:space:]]\+\)[[:space:]]*;.*/\1/p" | head -1
}
assert_cd() {  # $1 = key, $2 = registered value
  local got; got="$(cd_value "$1")"
  [ -n "$got" ] || refuse "G-03: controlDict carries no top-level \`$1\`. An unevaluated policy is not a satisfied one (Sanaa item 4)."
  [ "$got" = "$2" ] || refuse "G-03: controlDict \`$1\` is '$got', but K2h_PREREGISTRATION.md registers '$2'."
  say "    $1 = $got"
}
# Every value below is TRANSCRIBED from the registration, not chosen here.
assert_cd application    buoyantBoussinesqPimpleFoam   # section 4
assert_cd startFrom      startTime                     # section 4: the clock starts at 0 ...
assert_cd startTime      0                             # ... with the 803 fields as the INITIAL CONDITION
assert_cd endTime        "$END_TIME"                   # section 5 E-ENDTIME
assert_cd deltaT         0.005                         # section 4
assert_cd adjustTimeStep yes                           # section 8's mean-deltaT projection assumes it
assert_cd maxCo          2.0                           # section 4, K2b's measured setting
assert_cd writeControl   adjustableRunTime             # section 9
assert_cd writeInterval  5                             # section 9: ~5.0 min wall worst-case loss
assert_cd purgeWrite     16                            # section 9: retains t=42..112
# --- the two function-object limbs, matched on CONTENT and not on whitespace --
grep -qE '^[[:space:]]*restartOnRestart[[:space:]]+false[[:space:]]*;' "$CD" \
  || refuse "G-03: fieldAverage does not declare \`restartOnRestart false\` -- Sanaa item 3. A restart would DISCARD the averaging accumulator and poison the graded number SILENTLY rather than stopping the run."
grep -qE '^[[:space:]]*timeStart[[:space:]]+42[[:space:]]*;' "$CD" \
  || refuse "G-03: fieldAverage does not start averaging at the registered 42 s (section 5 S-SETTLE)."
grep -qE '^[[:space:]]*type[[:space:]]+abort[[:space:]]*;' "$CD" \
  || refuse "G-03: no \`abort\` function object -- Sanaa item 12 would have no clean stop and a stop would have to kill a rank."
grep -rqE 'restartOnRestart[[:space:]]+(yes|true|on|1)[[:space:]]*;' "$CASE/system" \
  && refuse "G-03: a restartOnRestart TRUE is declared in system/ -- it would DISCARD the averaging accumulator on restart"
say "  G-03 OK: every registered controlDict value read back BY VALUE from disk"

# --- G-04/05 memory and cores -------------------------------------------------
AVAIL_GB=$(awk '/MemAvailable/ {printf "%.1f", $2/1048576}' /proc/meminfo)
awk -v a="$AVAIL_GB" -v n="$MEM_NEED_GB" 'BEGIN{exit !(a >= n + 2)}' \
  || refuse "memory: ${AVAIL_GB} GB available is not ${MEM_NEED_GB} GB + 2 GB headroom"
LIVE=$(pgrep -c -f '[F]oam -parallel' 2>/dev/null || echo 0)
# A FULL BOX IS A TRANSIENT CONDITION, NOT A DEFECT IN THIS CASE, and the wording
# matters because a refusal here reads as a finding about the entry. It is not:
# nothing about the registration, the case or the policy is wrong when the box is
# busy. queue_runner.py's own gate C HOLDS for exactly this reason and schedules
# the entry into the next wave rather than consuming a frozen registration over a
# resource condition. This launcher cannot hold -- it is one-shot -- so it refuses
# to START, which is the safe direction, and says plainly which kind of refusal
# it is so nobody triages a busy box as a broken case.
if [ $((RANKS + LIVE)) -gt "$(nproc)" ]; then
  refuse "G-05 CORE GUARD, TRANSIENT BOX CONDITION AND NOT A DEFECT IN THIS CASE:
        $RANKS requested ranks + $LIVE live solver ranks > $(nproc) cores.
        NOTHING IS WRONG WITH THE ENTRY, THE REGISTRATION OR THE CASE. The correct
        response is to RETRY IN THE NEXT WAVE, exactly as queue_runner.py gate C
        does by HOLDING. Do not move this entry to refused/ on this line."
fi
say "G-04/05 OK: ${AVAIL_GB} GB available, $LIVE live solver ranks, $(nproc) cores"

if [ "$CHECK_ONLY" = "1" ]; then
  say "CHECK-ONLY: all guards pass. NOTHING WAS STAGED AND NOTHING WAS LAUNCHED."
  exit 0
fi

# --- STAGE. Refuses rather than overwrites an already-armed case. -------------
[ -d "$CASE/0" ] && refuse "$CASE/0 already exists -- this case is NOT unstarted; staging never overwrites an armed case"
ls -d "$CASE"/[0-9]* >/dev/null 2>&1 && refuse "$CASE already holds a time directory"

say "STAGING (mesh and fields are COPIED, never re-meshed and never interpolated)"
[ -d "$CASE/constant" ] || cp -r "$SRC/constant" "$CASE/constant"
[ -d "$CASE/0.orig" ]   || cp -r "$SRC/0.orig"   "$CASE/0.orig"
for r in 0 1 2 3; do
  P="$CASE/processor$r"
  mkdir -p "$P"
  [ -d "$P/constant" ] || cp -r "$SRC/processor$r/constant" "$P/constant"
  [ -d "$P/0" ]        || cp -r "$SRC/processor$r/$IC_TIME" "$P/0"
  # the time index inside a copied checkpoint still says 803; the run starts at 0
  if [ -f "$P/0/uniform/time" ]; then
    sed -i -e 's/^value .*/value           0;/' -e 's/^name .*/name            "0";/' \
           -e 's/^index .*/index           0;/' "$P/0/uniform/time"
    grep -q 'index           0;' "$P/0/uniform/time" || refuse "$P/0/uniform/time did not reset to index 0"
  fi
  for f in T U p_rgh alphat nut k omega phi; do
    [ -f "$P/0/$f" ] || refuse "STAGING: $P/0/$f missing after the copy"
  done
done
# 0/ is armed LAST so its mtime dates the run for the age guard.
cp -r "$CASE/0.orig" "$CASE/0"
touch "$CASE/0/T"
[ -f "$CASE/0/T" ] || refuse "STAGING: 0/T was not armed"
say "  STAGED: 4 ranks armed from t=$IC_TIME, 0/ armed last (age-guard referent)"

# --- LAUNCH, detached, parented to init ---------------------------------------
cat > "$CASE/.k2h_inner.sh" <<'EOI'
set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
CASE="$1"; RANKS="$2"; HERE="$3"
cd "$CASE"
T0=$(date +%s); echo "$T0" > .k2h_t0
mpirun -np "$RANKS" buoyantBoussinesqPimpleFoam -parallel > log.solve 2>&1
RC=$?                                    # <-- INSIDE. Never around a setsid line.
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
  echo "ic_from=K2f_L3/processor*/803"
  echo "solver=buoyantBoussinesqPimpleFoam"; echo "note=$NOTE"
  echo "ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$HERE/STATUS.$(basename "$CASE")"
EOI
chmod +x "$CASE/.k2h_inner.sh"

setsid bash "$CASE/.k2h_inner.sh" "$CASE" "$RANKS" "$HERE" </dev/null > "$CASE/.k2h_outer.out" 2>&1 &
echo $! > "$CASE/PIDS.solver"
setsid python3 "$REPO/verification/runs/F14-cooling-ladder/K2g_runs/monitor_k2g.py" \
  "$CASE" "$RANKS" "$POINT_CORE_MIN" "$CAP_CORE_MIN" R4 </dev/null > "$CASE/.monitor_outer.out" 2>&1 &
# ^ R4 is SUSPENDED for this TRANSIENT level, registered in K2h_PREREGISTRATION.md
#   AMENDMENT 1 (pre-compute, rule 2). R1, R2 and R3 stay ARMED. The monitor writes
#   RULES_SUSPENDED.txt beside the case so the absence is visible on disk.
echo $! > "$CASE/PIDS.monitor"
say "LAUNCHED solver_sid=$(cat "$CASE/PIDS.solver") monitor_sid=$(cat "$CASE/PIDS.monitor") ranks=$RANKS"
say "  NO killing timeout. Stops come only from the registered rules, through ABORT."
exit 0
