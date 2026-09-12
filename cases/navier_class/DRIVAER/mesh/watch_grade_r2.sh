#!/bin/bash
# DRIVAER R2 -- DURABLE DETACHED WATCH-AND-GRADE for ONE level.
#
# WHY THIS EXISTS.  The two r2 solves were launched by launch_r2_solve.sh with their
# stdout redirected into a DEAD agent session's scratchpad.  The scratchpad is temp
# only and is NEVER a handoff channel (CLAUDE.md rule 13 / L-186); it has been wiped
# three times in one day.  If it is wiped, or if the launching agent dies, the solve
# lands and NOTHING grades it.  This script lives under the CASE directory, writes
# every artifact BESIDE THE RUN, and is launched under setsid so it outlives its
# parent agent.
#
# IT KILLS NOTHING.  There is NO spend cap and NO clock cap in this script -- Sanaa
# has ruled three times that nothing may stop on spend or clock.  MemAvailable is
# OBSERVED and LOGGED ONLY; no signal is ever sent to any process by this script.
#
# IT NEVER TOUCHES ANOTHER TEAM'S PROCESS.  The solver is identified by
# /proc/<pid>/cwd AND /proc/<pid>/cmdline, RE-CONFIRMED ON EVERY POLL (L-557: `ps`
# tells you WHAT, never WHOSE).  If the identity ever stops matching, this script
# STOPS WATCHING AND EXITS.  It does not signal, and it does not grade a run it can
# no longer prove it was watching.
#
# rc IS CAPTURED INSIDE THIS WRAPPER, never around a setsid line -- `setsid timeout
# cmd` exits 0 for every outcome.  The SOLVER's rc is NOT invented here: it is read
# from the sidecar launch_r2_solve.sh writes inside ITS OWN wrapper ($ROOT/rc).  If
# that sidecar never appears, this script says so and lets grade_drivaer.py REFUSE
# on the rule-4 rc clause.  It writes no file matching the grader's rc globs
# (rc, *.rc, DONE*), so it cannot fabricate a completion.
#
# usage: watch_grade_r2.sh <LEVEL_DIR> <LEVEL_NAME> <SOLVER_PID> <WRAPPER_PID>
set -u
ROOT="$1"; NAME="$2"; SPID="$3"; WPID="$4"
REPO=/home/ubuntu/Certonomous
GRADER="$REPO/cases/navier_class/DRIVAER/grade_drivaer.py"
REF="$REPO/verification/runs/navier_class/DRIVAER/drivaer_reference_notchback.json"
LOG="$ROOT/GRADE_WATCH.log"
POLL=30
RC_WAIT_S=3600          # how long to wait for the launcher's rc sidecar after exit

say () { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" >> "$LOG"; }
finish () { printf 'watcher_rc=%s\n' "$1" > "$ROOT/GRADE_WATCH_RC.txt"; exit "$1"; }

[ -d "$ROOT" ] || { echo "no such level root $ROOT"; exit 2; }
say "WATCH START level=$NAME root=$ROOT solver_pid=$SPID wrapper_pid=$WPID grader=$GRADER"

# ---- identity, asserted before anything and re-asserted on every poll -------------
identity_ok () {
  local cwd cmd
  cwd=$(readlink "/proc/$1/cwd" 2>/dev/null) || return 1
  cmd=$(tr '\0' ' ' < "/proc/$1/cmdline" 2>/dev/null) || return 1
  [ "$cwd" = "$ROOT" ] || return 2
  case "$cmd" in *simpleFoam*) ;; *) return 3 ;; esac
  return 0
}
identity_ok "$SPID"; rc=$?
if [ $rc -ne 0 ]; then
  say "REFUSE: pid $SPID is not the solve in $ROOT at start (identity code $rc). NOTHING WATCHED, NOTHING SIGNALLED."
  finish 4
fi
say "IDENTITY CONFIRMED: /proc/$SPID/cwd=$ROOT and cmdline carries simpleFoam"

# ---- wait for the solve.  Observe only. ------------------------------------------
n=0
while :; do
  if [ ! -d "/proc/$SPID" ]; then say "SOLVER PID $SPID GONE"; break; fi
  identity_ok "$SPID"; rc=$?
  if [ $rc -ne 0 ]; then
    say "IDENTITY LOST on pid $SPID (code $rc) -- the pid was recycled or is no longer this solve. STOPPING. No signal sent, no grade attempted."
    finish 5
  fi
  n=$((n+1))
  if [ $((n % 20)) -eq 1 ]; then
    t=$(grep '^Time = ' "$ROOT/log.simpleFoam" 2>/dev/null | tail -1)
    ma=$(awk '/^MemAvailable:/{printf "%.2f", $2/1048576}' /proc/meminfo)
    say "alive: $t MemAvailable=${ma}GiB (OBSERVED ONLY -- this script stops nothing)"
  fi
  sleep $POLL
done

# ---- the launcher's own rc sidecar.  Not invented here. ---------------------------
waited=0
while [ ! -f "$ROOT/rc" ] && [ $waited -lt $RC_WAIT_S ]; do
  if [ ! -d "/proc/$WPID" ] && [ ! -f "$ROOT/rc" ] && [ $waited -gt 300 ]; then
    say "WRAPPER $WPID gone and no rc sidecar after ${waited}s"
    break
  fi
  sleep 15; waited=$((waited+15))
done
if [ -f "$ROOT/rc" ]; then
  say "solver rc sidecar present: $(tr -d '\n' < "$ROOT/rc") (written inside launch_r2_solve.sh)"
else
  say "NO rc SIDECAR. The launching wrapper did not write one, so the solver's exit status is UNKNOWN to this lab. It is NOT invented. grade_drivaer.py will REFUSE on the rule-4 rc clause and that refusal is the correct outcome."
  cat > "$ROOT/GRADE_WATCH_RC_MISSING.txt" <<TXT
NO SOLVER rc SIDECAR at $(date -u +%FT%TZ).
launch_r2_solve.sh writes \$ROOT/rc and \$ROOT/RC.txt inside its own wrapper at exit.
Neither appeared within ${RC_WAIT_S}s of the solver pid disappearing, and the wrapper
pid $WPID is gone.  The solver's exit status is therefore UNKNOWN.  It is NOT guessed
here.  Rule-4 clause 1 (rc==0) cannot be evaluated -> the level is BLOCKED on
completion, not PASS and not GATE FAIL.
TXT
fi

# ---- reconstruct, only if the launcher did not ------------------------------------
END=$(awk '/^endTime[ \t]/{gsub(";","",$2); print $2}' "$ROOT/system/controlDict" | tail -1)
if [ ! -d "$ROOT/$END" ]; then
  say "no reconstructed $END/ -- running reconstructPar -newTimes (rc captured here)"
  ( set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1; set -u
    cd "$ROOT" && nice -n 5 reconstructPar -newTimes > log.reconstructPar.watch 2>&1 )
  rrc=$?
  say "reconstructPar(watch) rc=$rrc"
else
  say "reconstructed $END/ already present"
fi

# ---- multi-window drift.  A PLATEAU IS NOT A FLAT SPELL: report several windows. ---
python3 - "$ROOT" > "$ROOT/DRIFT_WINDOWS.tsv" 2>> "$LOG" <<'PY'
import sys, glob, os
root = sys.argv[1]
dats = sorted(glob.glob(os.path.join(root, "postProcessing", "forceCoeffs*", "*", "coefficient.dat")))
if not dats:
    print("NO coefficient.dat"); raise SystemExit(0)
lines = open(dats[-1]).read().splitlines()
cols = None
for h in reversed([l for l in lines if l.startswith("#")]):
    t = h.lstrip("#").split()
    if "Cd" in t: cols = t; break
rows = [l.split() for l in lines if l and not l.startswith("#")]
print("# multi-window drift. excursion=(max-min)/|mean|; endpoint=(last-first)/|mean|")
print("# A SINGLE WINDOW IS NOT EVIDENCE OF A PLATEAU. The grader's registered limb is W=10% of endTime.")
print("artifact\t%s\trows\t%d" % (dats[-1], len(rows)))
print("quantity\twindow\tmean\tmin\tmax\texcursion_rel\tendpoint_drift_rel")
for q in ("Cd", "Cl"):
    ci = cols.index(q)
    v = [float(r[ci]) for r in rows if len(r) > ci]
    for W in (10, 20, 30, 50, 100, 200, 300, 500):
        if len(v) < W: continue
        w = v[-W:]; m = sum(w)/W
        if m == 0: continue
        print("%s\t%d\t%.8g\t%.8g\t%.8g\t%.6e\t%+.6e" % (q, W, m, min(w), max(w),
              (max(w)-min(w))/abs(m), (w[-1]-w[0])/abs(m)))
PY
say "DRIFT_WINDOWS.tsv written"

# ---- grade.  rc captured here. ----------------------------------------------------
say "grading: $GRADER --stage-a --levels $NAME=$ROOT --reference $REF"
python3 "$GRADER" --stage-a --levels "$NAME=$ROOT" --reference "$REF" \
        --report "$ROOT/GRADE_STAGE_A_${NAME}.json" > "$ROOT/GRADE_STAGE_A_${NAME}.out" 2>&1
grc=$?
say "grade_drivaer.py exit rc=$grc (0=verdict produced, 2=REFUSED, 70=internal defect)"

# ---- cost actual, from the run's own record ---------------------------------------
{ echo "# DRIVAER R2 $NAME -- ACTUAL SOLVER COST, measured from RUN_META.txt"
  grep -E '^(launched_utc|solver_started_utc|finished_utc|wall_s|core_min|ranks|simpleFoam rc)' "$ROOT/RUN_META.txt" 2>/dev/null
  awk -F= '/^wall_s=/{w=$2} /^ranks=/{n=$2} END{if(w&&n){cm=w*n/60.0;
     printf "actual_core_min=%.2f\n", cm;
     printf "derived_usd=%.4f  # DERIVED, NOT MEASURED: core-min/60 * $0.0513/core-h, owner-stated rate; the box cannot read its own billing\n", cm/60.0*0.0513}}' "$ROOT/RUN_META.txt"
  cat "$ROOT/CAP_SCORED.txt" 2>/dev/null
} > "$ROOT/COST_ACTUAL.txt" 2>/dev/null
say "COST_ACTUAL.txt written"
say "WATCH DONE level=$NAME grade_rc=$grc"
finish $grc
