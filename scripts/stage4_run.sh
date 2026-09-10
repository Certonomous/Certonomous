#!/usr/bin/env bash
# CASE PROTOCOL -- STAGE 4 FULL RUN.  BUILT, NOT LAUNCHED.
#
# AUTHORITY.  CASE_PROTOCOL_CHARTER v1.0 section 4, verbatim:
#   "Launched detached from any agent: the runner daemon owns it, THE PROCESS IS PARENTED
#    TO INIT, the autograder and the monitor ARE PARENTED TO INIT WITH IT.  The fleet dying
#    does not touch the solver.  Checkpoints written at the registered interval so a kill
#    resumes from committed state."
#   "Completion: exit status read, artifacts hashed, cost written.  COMPLETION IS NOT
#    CERTIFICATION."
#
# THREE THINGS THIS SCRIPT WILL NOT DO, and each is a rule paid for by a specific failure:
#   1. IT WILL NOT LAUNCH WITHOUT --i-have-committed-the-registration <path>, and it
#      verifies that path is TRACKED and CLEAN at HEAD.  Compute behind an uncommitted
#      registration is rule 2's whole prohibition (the supervisor's check-4).
#   2. IT WILL NOT INFER rc FROM AN 'End' LINE.  `setsid timeout cmd` exits 0 for every
#      outcome, so rc is captured INSIDE the detached wrapper, never around the setsid
#      line, and written to a sidecar the grader reads.
#   3. IT WILL NOT RAISE A CAP, EVER.  Whether a cap STOPS this run is read from the
#      registration (monitor.cap_stops_run); if the registration does not say, the monitor
#      refuses to decide and the stop goes to the supervisor.  Section 9's closing clause
#      suspends budget gates for the 3D cases that still need to run, and that scope
#      question is not this script's to settle.
#
# PPID 1 IS ASSERTED, NOT ASSUMED.  After setsid the wrapper reads /proc/<pid>/stat and
# refuses to continue unless the parent really is init.  "Detached" claimed by a flag and
# not measured is how a fleet death takes a solver with it.
set -u
usage() { sed -n '2,34p' "$0"; exit 2; }

PROFILE=""; CASE=""; RUNS=""; REG=""; DRY=1
while [ $# -gt 0 ]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2;;
    --case)    CASE="$2";    shift 2;;
    --runs)    RUNS="$2";    shift 2;;
    --i-have-committed-the-registration) REG="$2"; shift 2;;
    --launch)  DRY=0; shift;;             # WITHOUT THIS FLAG NOTHING IS LAUNCHED
    -h|--help) usage;;
    *) echo "unknown argument: $1" >&2; usage;;
  esac
done
[ -n "$PROFILE" ] && [ -n "$CASE" ] && [ -n "$RUNS" ] || usage

REPO=$(python3 -c "import json,sys;print(json.load(open('$PROFILE'))['repo'])")
RANKS=$(python3 -c "import json;print(json.load(open('$PROFILE')).get('ranks',1))")
SOLVER=$(python3 -c "import json;print(json.load(open('$PROFILE'))['solver']['binary'])")
BASHRC=$(python3 -c "import json;print(json.load(open('$PROFILE'))['solver'].get('bashrc',''))")
MON="$REPO/scripts/stage4_monitor.py"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
REC="$RUNS/STAGE4.$STAMP"
mkdir -p "$RUNS"

say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$REC.progress"; }

# ---- GUARD 1: the registration is committed and clean ---------------------------------
if [ -z "$REG" ]; then
  say "REFUSE: no --i-have-committed-the-registration. Stage 4 spends compute and compute"
  say "        behind an uncommitted registration is exactly what rule 2 forbids."
  exit 2
fi
REL=$(python3 -c "import os,sys;print(os.path.relpath('$REG','$REPO'))")
if ! git -C "$REPO" cat-file -e "HEAD:$REL" 2>/dev/null; then
  say "REFUSE: $REL is NOT TRACKED AT HEAD. A registration that is not in the commit graph"
  say "        cannot have been frozen before this run."
  exit 2
fi
if ! git -C "$REPO" diff --quiet HEAD -- "$REL"; then
  say "REFUSE: $REL differs from HEAD. The frozen file must BE the file that runs."
  exit 2
fi
REGBLOB=$(git -C "$REPO" rev-parse "HEAD:$REL")
say "registration $REL tracked and clean at HEAD; blob $REGBLOB"

# ---- GUARD 2: the case root is clean (a guard refuses a dirty root, it never clears one)
if [ -d "$CASE/0" ] || ls -d "$CASE"/[1-9]* >/dev/null 2>&1; then
  say "REFUSE: $CASE already holds 0/ or a time directory. A guard refuses a dirty root and"
  say "        NEVER clears one -- clearing it would destroy somebody's evidence."
  exit 2
fi

# ---- GUARD 3: stage 2 must be green for this case -------------------------------------
S2="$RUNS/stage2_report.json"
if [ ! -f "$S2" ]; then
  say "REFUSE: no stage-2 report at $S2. Section 2 is an exit condition, not a courtesy."
  exit 2
fi
S2STATE=$(python3 -c "import json;print(json.load(open('$S2'))['overall'])")
if [ "$S2STATE" != "GREEN" ]; then
  say "REFUSE: stage 2 is $S2STATE, not GREEN. A case whose instruments are RED cannot"
  say "        produce a graded number, so spending on it buys nothing."
  exit 2
fi
say "stage 2 GREEN for this case"

if [ "$DRY" -eq 1 ]; then
  say "DRY: every guard passed and NOTHING WAS LAUNCHED (--launch was not given)."
  say "DRY: would run: $SOLVER -case $CASE   at ranks $RANKS, detached, PPID 1"
  say "DRY: would run: $MON --profile $PROFILE --case $CASE --pid <solver> --record $REC.monitor.jsonl"
  exit 0
fi

# ---- LAUNCH.  rc IS CAPTURED INSIDE THE WRAPPER. --------------------------------------
WRAP="$REC.wrapper.sh"
cat > "$WRAP" <<WEOF
#!/usr/bin/env bash
set -u
[ -n "$BASHRC" ] && . "$BASHRC" >/dev/null 2>&1
cp -a "$CASE/0.orig" "$CASE/0"          # 0/ is touched LAST: it dates the run (age guard)
"$SOLVER" -case "$CASE" > "$CASE/log.simpleFoam" 2>&1
RC=\$?                                   # <-- INSIDE the wrapper. setsid's parent returns 0.
echo "rc=\$RC" > "$CASE/rc"
echo "finished_utc=\$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$CASE/rc"
WEOF
chmod +x "$WRAP"

setsid "$WRAP" < /dev/null > "$REC.solver.out" 2>&1 &
sleep 2
SPID=$(pgrep -n -f "$SOLVER -case $CASE" || true)
if [ -z "$SPID" ]; then say "REFUSE: solver did not appear in the process table"; exit 2; fi

# ---- ASSERT PPID 1.  Detachment is MEASURED, not claimed. -----------------------------
PPID_OF=$(awk '{print $4}' "/proc/$SPID/stat" 2>/dev/null || echo "")
if [ "$PPID_OF" != "1" ]; then
  say "REFUSE: solver pid $SPID has PPID $PPID_OF, not 1. It is NOT parented to init and the"
  say "        fleet dying WOULD take it. Killing it rather than leaving a false 'detached'."
  kill -TERM "$SPID" 2>/dev/null || true
  exit 2
fi
say "solver pid $SPID launched detached, PPID 1 ASSERTED from /proc/$SPID/stat"

STARTED=$(date +%s)
setsid python3 "$MON" --profile "$PROFILE" --case "$CASE" --pid "$SPID" \
       --started "$STARTED" --record "$REC.monitor.jsonl" \
       --interval "$(python3 -c "import json;print(json.load(open('$PROFILE'))['monitor'].get('poll_s',60))")" \
       < /dev/null > "$REC.monitor.out" 2>&1 &
sleep 1
MPID=$(pgrep -n -f "stage4_monitor.py --profile $PROFILE" || true)
MPPID=$(awk '{print $4}' "/proc/$MPID/stat" 2>/dev/null || echo "")
say "monitor pid $MPID PPID $MPPID (1 required by section 4: the monitor is parented to init WITH the solver)"
say "LAUNCHED. solver=$SPID monitor=$MPID record=$REC.*  Completion is not certification."
exit 0
