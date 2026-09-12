#!/bin/bash
# resume_k2g.sh -- K2g L3 RESUME driver.  NEW FILE, 2026-09-12.
#
#   ./resume_k2g.sh --check-only     # every guard, mutates NOTHING, launches NOTHING
#   ./resume_k2g.sh                  # guards, prepare, then DETACHED launch
#
# ===========================================================================
# WHY THIS FILE EXISTS AND launch_k2g.sh DOES NOT DO THIS JOB
# ===========================================================================
# launch_k2g.sh is the FROZEN first-launch path (pinned by b456d1107).  It is
# NOT EDITED and NOT CALLED here, for two measured reasons:
#
#   1. Its first act is `mark_done_k2f.py --guard`, clause 7, which REFUSES a
#      case that already has a 0/ or a populated postProcessing/.  K2f_L3 has
#      both.  The guard is RIGHT to refuse: it protects an unstarted case.
#   2. Its next acts are `rm -rf 0 && cp -r 0.orig 0` and `decomposePar -force`,
#      which would DESTROY processor*/500 -- the only surviving product of the
#      13.1 wall-hours the pre-reboot run spent.
#
# So a resume needs its own driver.  This one never re-stages, never
# decomposes, never touches 0/ and never deletes a time directory.
#
# ===========================================================================
# THE THREE THINGS A RESUME BREAKS, AND WHAT IS DONE ABOUT EACH
# ===========================================================================
# (A) CLAUSE 5.  mark_done_k2f.py counts ExecutionTime lines and requires
#     round(endTime/deltaT) = 2000.  A resumed solver writes only iterations
#     501..2000 = 1500 lines.  Clause 5 would FAIL on a correct run.
# (B) D-CONV.  analyse_k2g.py:iterative_state takes the normalised start as
#     max(v[:5]) -- the FIRST FIVE residuals of the log.  A resume-only log
#     starts at iteration 501, where the residuals are already ~1e-4, so the
#     measured decade drop collapses to ~0 and every level would grade
#     NOT_CONVERGED -> NOT A RESULT.  THIS ALONE WOULD VOID THE RUNG.
# (C) postProcessing.  mark_done_k2f.py's own clause-7 note records it: on a
#     restart OpenFOAM writes a SECOND function-object file beside the first
#     and both match a glob.  That is a wrong number, not a crash.
#
# (A) and (B) have ONE joint repair and it is DISCLOSED, never silent:
# log.solve is REASSEMBLED as [pre-reboot iterations 1..500] + [resumed
# iterations 501..2000].  That is exactly the history of the graded solution
# path: the resume restarts from the t=500 checkpoint, so pre-reboot iterations
# 501..835 are DISCARDED and are not part of the answer.  The untouched
# original is kept forever as log.solve.prereboot_full with its sha256 in
# RESUME_RECORD.K2f_L3.md.  Every count is asserted, and a count that does not
# come out exactly right REFUSES rather than proceeds.
# (C) is repaired by MOVING postProcessing/ aside with its path recorded.
# NOTHING IS EVER DELETED BY THIS SCRIPT.
#
# ===========================================================================
# EXIT MAP: 0 OK, 2 REFUSE.  No verdict is carried by an exit code.
# ===========================================================================
set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO=/home/ubuntu/Certonomous
CASE="$HERE/K2f_L3"
K2F="$REPO/verification/runs/F14-cooling-ladder/K2f_runs"
PREREG="$REPO/docs/campaigns/F14-cooling-ladder/K2g_PREREGISTRATION.md"
PREREG_SHA=b456d1107b9b14cf501b83a4963552492d1604e7
RANKS=4
END_TIME=2000
RESUME_FROM=500
WRITE_INTERVAL=25
PURGE_WRITE=24
POINT_CORE_MIN=598
CAP_CORE_MIN=1200          # REGISTERED.  A FLAG, NOT A STOP (Sanaa 2026-09-12 #17).
MEM_NEED_GB=2.5
TS=$(date -u +%Y-%m-%dT%H%M%SZ)

CHECK_ONLY=0
[ "${1:-}" = "--check-only" ] && CHECK_ONLY=1

say() { echo "[resume_k2g $(date -u +%H:%M:%SZ)] $*"; }
refuse() { echo "REFUSE: $*" >&2; exit 2; }

# ---------------------------------------------------------------------------
# G-01  FREEZE.  verify_freeze() doing its job EARLY: every file on the grading
#       path must hash on disk to what the registration's own FREEZE table
#       pinned, and that table must be the one committed at b456d1107.
# ---------------------------------------------------------------------------
say "G-01 freeze verify against $PREREG_SHA"
git -C "$REPO" cat-file -e "$PREREG_SHA" 2>/dev/null || refuse "prereg commit $PREREG_SHA does not exist"
git -C "$REPO" cat-file -e "$PREREG_SHA:docs/campaigns/F14-cooling-ladder/K2g_PREREGISTRATION.md" 2>/dev/null \
  || refuse "the registration does not exist at $PREREG_SHA -- the laundering shape"
REPO="$REPO" PREREG="$PREREG" PREREG_SHA="$PREREG_SHA" python3 - <<'PYX' || exit 2
import hashlib, json, os, re, subprocess, sys
repo, prereg, sha = os.environ["REPO"], os.environ["PREREG"], os.environ["PREREG_SHA"]
disk_doc = open(prereg, "rb").read()
committed = subprocess.run(["git", "-C", repo, "show",
                            sha + ":docs/campaigns/F14-cooling-ladder/K2g_PREREGISTRATION.md"],
                           capture_output=True).stdout
if disk_doc != committed:
    print("REFUSE: the registration on disk is not the one committed at %s" % sha); sys.exit(2)
m = re.search(r"```json FREEZE\n(.*?)```", disk_doc.decode(), re.S)
if not m:
    print("REFUSE: no FREEZE block in the registration"); sys.exit(2)
table, bad = json.loads(m.group(1)), []
for rel, frozen in table.items():
    p = os.path.join(repo, rel)
    if not os.path.exists(p):
        bad.append("%s ABSENT" % rel); continue
    disk = hashlib.sha256(open(p, "rb").read()).hexdigest()
    blob_disk = subprocess.run(["git", "-C", repo, "hash-object", p],
                               capture_output=True, text=True).stdout.strip()
    blob_frzn = subprocess.run(["git", "-C", repo, "rev-parse", "%s:%s" % (sha, rel)],
                               capture_output=True, text=True).stdout.strip()
    if disk != frozen:
        bad.append("%s sha256 disk=%s frozen=%s" % (rel, disk[:12], frozen[:12]))
    if blob_disk != blob_frzn:
        bad.append("%s blob disk=%s frozen=%s" % (rel, blob_disk[:12], blob_frzn[:12]))
    print("  PINNED %-70s %s" % (rel, disk[:16]))
if bad:
    print("REFUSE -- GRADING PATH NOT PINNED:\n  " + "\n  ".join(bad)); sys.exit(2)
print("  G-01 OK: %d grading-path files, sha256 disk == FREEZE table, blob disk == %s"
      % (len(table), sha[:9]))
PYX

# ---------------------------------------------------------------------------
# G-02  THE CHECKPOINT IS REALLY THERE.  Not "the census said so".
# ---------------------------------------------------------------------------
say "G-02 resume checkpoint"
[ -d "$CASE" ] || refuse "$CASE does not exist"
for r in 0 1 2 3; do
  d="$CASE/processor$r/$RESUME_FROM"
  [ -d "$d" ] || refuse "$d absent -- there is no checkpoint to resume from"
  for f in T U p_rgh alphat nut k omega phi p; do
    [ -f "$d/$f" ] || refuse "$d/$f absent -- the checkpoint is incomplete"
  done
  grep -q "index *$RESUME_FROM;" "$d/uniform/time" \
    || refuse "$d/uniform/time does not carry index $RESUME_FROM"
done
[ -f "$CASE/0/T" ] || refuse "$CASE/0/T absent -- rule 4 clause 6 has no age referent"
say "  G-02 OK: processor0..3/$RESUME_FROM complete, 0/T present"

# ---------------------------------------------------------------------------
# G-03  controlDict SHAPE (directive items 1-4: the launcher refuses a case
#       whose controlDict does not satisfy the checkpoint rules).
# ---------------------------------------------------------------------------
CD="$CASE/system/controlDict"
say "G-03 controlDict"
grep -qx "startFrom latestTime;" "$CD" || refuse "controlDict is not startFrom latestTime -- this would RESTART, not resume"
grep -qx "endTime $END_TIME;"     "$CD" || refuse "controlDict endTime is not $END_TIME (E-ENDTIME)"
grep -qx "deltaT 1;"              "$CD" || refuse "controlDict deltaT is not 1 -- clause 5 arithmetic assumes it"
say "  G-03 OK: startFrom latestTime, endTime $END_TIME, deltaT 1"

# ---------------------------------------------------------------------------
# G-04  MEMORY GUARD (directive item 7).  Refused if it does not fit.
# ---------------------------------------------------------------------------
AVAIL_GB=$(awk '/MemAvailable/ {printf "%.1f", $2/1048576}' /proc/meminfo)
say "G-04 memory: need ${MEM_NEED_GB} GB, MemAvailable ${AVAIL_GB} GB"
awk -v a="$AVAIL_GB" -v n="$MEM_NEED_GB" 'BEGIN{exit !(a >= n + 2)}' \
  || refuse "memory: ${AVAIL_GB} GB available is not ${MEM_NEED_GB} GB + 2 GB headroom"
SWAP_USED=$(awk '/SwapTotal/{t=$2}/SwapFree/{f=$2}END{print t-f}' /proc/meminfo)
[ "$SWAP_USED" -gt 262144 ] && refuse "swap in use (${SWAP_USED} kB) -- directive item 18 makes that a defect that stops new launches"
say "  G-04 OK"

# ---------------------------------------------------------------------------
# G-05  CORE GUARD (directive item 8).  ranks + live solver ranks <= 16.
# ---------------------------------------------------------------------------
LIVE=$(pgrep -c -f '[F]oam -parallel' 2>/dev/null || echo 0)
NPROC=$(nproc)
say "G-05 cores: ranks=$RANKS live solver ranks=$LIVE nproc=$NPROC"
[ $((RANKS + LIVE)) -le "$NPROC" ] || refuse "core guard: $RANKS + $LIVE > $NPROC"
say "  G-05 OK"

if [ "$CHECK_ONLY" = "1" ]; then
  # the log arithmetic, COUNTED, without writing anything
  N1=$(awk '/^Time = /{t=$3} /^ExecutionTime = /{n++; if(t+0<='"$RESUME_FROM"') k=n} END{print k+0}' "$CASE/log.solve")
  say "CHECK-ONLY: pre-reboot log carries $N1 ExecutionTime lines at or below t=$RESUME_FROM"
  say "CHECK-ONLY: $N1 + $((END_TIME - RESUME_FROM)) = $((N1 + END_TIME - RESUME_FROM)) vs clause-5 requirement $END_TIME"
  [ $((N1 + END_TIME - RESUME_FROM)) -eq "$END_TIME" ] || refuse "clause-5 arithmetic does not close"
  say "ALL GUARDS PASS. NOTHING WAS CHANGED AND NOTHING WAS LAUNCHED."
  exit 0
fi

# ===========================================================================
# PREPARE.  Everything below mutates the case and is asserted by READ-BACK.
# ===========================================================================
REC="$CASE/../RESUME_RECORD.K2f_L3.md"

# --- P-01 checkpoint policy, applied to the GENERATED controlDict ----------
# NOT a frozen file: build_k2f.py (frozen, unedited) generated it; the frozen
# launcher already edits this same file for E-ENDTIME.  No gate, threshold, cap
# or label moves.  writeInterval 25 DIVIDES 2000 (so endTime is a write point)
# and DIVIDES 500 (so t=1500 is a write point -- analyse_k2g.py hardcodes
# CHECKPOINT_BACK = 500 and D-PLATEAU reads endTime-500).  purgeWrite 24 keeps
# t=1425..2000, which is the SMALLEST retention that keeps BOTH grading inputs
# with margin; purgeWrite 2 would keep only 1950 and 2000 and would DESTROY the
# t=1500 input, refusing the comparator at exit 2 after the full spend.
CASE="$CASE" WI="$WRITE_INTERVAL" PW="$PURGE_WRITE" python3 - <<'PYX' || exit 2
import hashlib, os, re, shutil, sys
cd = os.path.join(os.environ["CASE"], "system", "controlDict")
wi, pw = os.environ["WI"], os.environ["PW"]
raw = open(cd).read()
if re.search(r"^writeInterval %s;$" % wi, raw, re.M) and re.search(r"^purgeWrite %s;$" % pw, raw, re.M) \
   and re.search(r"type\s+abort;", raw):
    print("  P-01 already applied; re-asserting only");
else:
    if not os.path.exists(cd + ".pre_resume"):
        shutil.copy2(cd, cd + ".pre_resume")
    new = re.sub(r"^writeInterval \d+;$", "writeInterval %s;" % wi, raw, count=1, flags=re.M)
    new = re.sub(r"^purgeWrite \d+;$",    "purgeWrite %s;" % pw,    new, count=1, flags=re.M)
    FO = '''
    // ADDED FOR THE RESUME, 2026-09-12.  DIAGNOSTIC AND CONTROL ONLY.
    // dp_tile/dp_return are the monitor channel Sanaa's directive item 11
    // requires (the monitor writes the GRADED QUANTITY per iteration).  THEY
    // ARE NEVER A GRADING INPUT: DP_module is read from the field files by the
    // FROZEN foam_patch_reader.area_average (registration section 4).  At
    // endTime the two are cross-checked and must agree, which makes this an
    // INDEPENDENT CONTROL ON THE READER rather than a second grading path.
    dp_tile
    {
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            tile;
        operation       areaAverage;
        fields          (p_rgh);
        writeFields     false;
        executeControl  timeStep;
        executeInterval 1;
        writeControl    timeStep;
        writeInterval   1;
        log             false;
    }
    dp_return
    {
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            return;
        operation       areaAverage;
        fields          (p_rgh);
        writeFields     false;
        executeControl  timeStep;
        executeInterval 1;
        writeControl    timeStep;
        writeInterval   1;
        log             false;
    }
    // THE CLEAN STOP for directive item 12.  The monitor TOUCHES this file and
    // the solver writes its fields and ends itself at the end of the current
    // iteration.  NOTHING KILLS A RANK -- which is precisely how the pre-reboot
    // run was lost: its wrapper took SIGKILL at 04:21:26Z and four orphaned
    // ranks ran on for another 12.9 hours into a reboot.
    stop_on_rule
    {
        type            abort;
        libs            (utilityFunctionObjects);
        file            "<case>/ABORT";
        action          writeNow;
    }
}
'''
    new = new.rstrip()
    new = new[:new.rfind("}")].rstrip("\n") + "\n" + FO
    open(cd, "w").write(new)

# READ BACK FROM DISK.  Nothing above this line is trusted.
chk, bad = open(cd).read(), []
for pat, label in ((r"^writeInterval %s;$" % wi, "writeInterval %s" % wi),
                   (r"^purgeWrite %s;$" % pw, "purgeWrite %s" % pw),
                   (r"^startFrom latestTime;$", "startFrom latestTime"),
                   (r"^endTime 2000;$", "endTime 2000"),
                   (r"^deltaT 1;$", "deltaT 1"),
                   (r"type\s+abort;", "abort FO"),
                   (r"libs\s+\(utilityFunctionObjects\);", "abort libs (rule 14)"),
                   (r'file\s+"<case>/ABORT";', "ABORT trigger path"),
                   (r"action\s+writeNow;", "abort action writeNow"),
                   (r"^    dp_tile$", "dp_tile FO"),
                   (r"^    dp_return$", "dp_return FO")):
    if not re.search(pat, chk, re.M):
        bad.append("MISSING " + label)
# rule 14: libs are INSERTED WITH AN ASSERT, never replaced -- every original
# function object and its libs entry must still be there.
for fo in ("magU", "U_ha", "T_ca", "T_in_0", "T_in_1", "T_in_2", "T_in_3"):
    if not re.search(r"^    %s$" % fo, chk, re.M):
        bad.append("ORIGINAL FO %s LOST" % fo)
n = len(re.findall(r"libs\s+\(fieldFunctionObjects\);", chk))
if n != 9:
    bad.append("fieldFunctionObjects libs count %d, expected 9 (7 original + 2 new)" % n)
if bad:
    if os.path.exists(cd + ".pre_resume"):
        shutil.copy2(cd + ".pre_resume", cd)
        bad.append("(controlDict RESTORED from .pre_resume)")
    print("REFUSE P-01: " + "; ".join(bad)); sys.exit(2)
print("  P-01 OK, read back from disk: writeInterval %s, purgeWrite %s, +dp_tile +dp_return "
      "+stop_on_rule; all 7 original function objects intact; sha256 %s"
      % (wi, pw, hashlib.sha256(chk.encode()).hexdigest()[:16]))
PYX

# --- P-02 postProcessing moved aside, RECORDED, NEVER DELETED -------------
if [ -d "$CASE/postProcessing" ] && [ -n "$(find "$CASE/postProcessing" -type f -print -quit)" ]; then
  PP_ASIDE="$CASE/postProcessing.prereboot_$TS"
  mv "$CASE/postProcessing" "$PP_ASIDE"
  [ -d "$PP_ASIDE" ] || refuse "P-02: postProcessing move did not land"
  say "  P-02 OK: pre-reboot postProcessing moved to $(basename "$PP_ASIDE") -- NOT deleted"
else
  PP_ASIDE="(none)"
  say "  P-02: no populated postProcessing to move"
fi

# --- P-03 log reassembly, every count asserted ----------------------------
LOG="$CASE/log.solve"
ORIG="$CASE/log.solve.prereboot_full"
[ -f "$ORIG" ] || cp -p "$LOG" "$ORIG"
ORIG_SHA=$(sha256sum "$ORIG" | cut -d' ' -f1)
awk -v cut="$RESUME_FROM" '
  /^Time = /   { t = $3 + 0 }
  { print }
  /^ExecutionTime = / { if (t >= cut) exit }
' "$ORIG" > "$CASE/log.solve.part1"
N1=$(grep -c '^ExecutionTime = ' "$CASE/log.solve.part1")
LASTT=$(grep '^Time = ' "$CASE/log.solve.part1" | tail -1 | awk '{print $3}')
[ "$N1" = "$RESUME_FROM" ] || refuse "P-03: log.solve.part1 has $N1 ExecutionTime lines, expected $RESUME_FROM"
[ "$LASTT" = "$RESUME_FROM" ] || refuse "P-03: log.solve.part1 ends at Time = $LASTT, expected $RESUME_FROM"
say "  P-03 OK: part1 = iterations 1..$N1; + $((END_TIME - RESUME_FROM)) resumed = $END_TIME (clause 5)"

# --- P-04 the record ------------------------------------------------------
cat > "$REC" <<EOR
# RESUME RECORD -- K2f_L3 (K2g L3), $TS

**This case was RESUMED, not restarted, and this file says exactly what was
changed so that no reader has to infer it from a log.**

| item | value |
|---|---|
| resumed from | t = $RESUME_FROM, \`processor0..3/$RESUME_FROM\`, written 2026-09-12 06:08Z |
| pre-reboot run | started 04:06:20Z, reached iteration 835, wrapper took SIGKILL at 04:21:26Z (\`STATUS.K2f_L3\` rc=137), four ranks orphaned and ran on until the 17:36:41Z reboot |
| pre-reboot log kept as | \`log.solve.prereboot_full\`, sha256 \`$ORIG_SHA\` |
| log.solve reassembled | \`log.solve.part1\` (iterations 1..$N1, from the pre-reboot log) + the resumed run's own output (iterations $((RESUME_FROM+1))..$END_TIME) |
| iterations DISCARDED | pre-reboot $((RESUME_FROM+1))..835 -- recomputed from the checkpoint, so they are NOT part of the graded answer |
| why reassembled | clause 5 counts ExecutionTime lines and needs $END_TIME; and \`analyse_k2g.py:iterative_state\` takes the normalised start from \`max(v[:5])\`, so a resume-only log starting at iteration 501 would measure ~0 decades and grade every level NOT_CONVERGED -> NOT A RESULT |
| controlDict changed | \`writeInterval\` 500 -> $WRITE_INTERVAL; \`purgeWrite\` 0 -> $PURGE_WRITE; added \`dp_tile\`, \`dp_return\` (monitor channel, NEVER a grading input) and \`stop_on_rule\` (type abort, action writeNow) |
| controlDict NOT changed | \`startFrom latestTime\`, \`endTime 2000\`, \`deltaT 1\`, \`application\`, schemes, solution -- and NO FROZEN FILE WAS EDITED |
| postProcessing | moved aside to \`$(basename "$PP_ASIDE")\`, never deleted (mark_done_k2f.py clause 7's own registered instruction) |
| grading path | verified sha256-on-disk == the registration's FREEZE table, and blob-on-disk == commit $PREREG_SHA, before anything was touched |

**Nothing here alters a gate, a threshold, a cap or a label.**
EOR
say "  P-04 OK: $REC"

# ===========================================================================
# LAUNCH.  Detached, parented to init.  rc is captured INSIDE the wrapper --
# `setsid cmd` returns 0 for every outcome and a wrapper that measures its own
# exit from outside the setsid line measures nothing.
# NO KILLING TIMEOUT: Sanaa's 2026-09-12 directive #17 -- no run is stopped by
# a time or budget cap.  The registered cap is carried as a FLAG by the monitor.
# ===========================================================================
cat > "$CASE/.resume_inner.sh" <<'EOI'
set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
CASE="$1"; RANKS="$2"; HERE="$3"; END_TIME="$4"
cd "$CASE"
cp -p log.solve.part1 log.solve
T0=$(date +%s); echo "$T0" > .resume_t0
mpirun -np "$RANKS" buoyantBoussinesqSimpleFoam -parallel >> log.solve 2>&1
RC=$?                                   # <-- INSIDE. Never around a setsid line.
T1=$(date +%s); WALL=$((T1-T0))
if [ "$RC" = "0" ]; then reconstructPar -latestTime > log.reconstructPar 2>&1 || true; fi
CM=$(python3 -c "print(f'{$WALL*$RANKS/60:.3f}')")
EX=$(grep -oE 'ExecutionTime = [0-9.]+' log.solve | tail -1 | grep -oE '[0-9.]+$' || echo "")
CL=$(grep -oE 'ClockTime = [0-9.]+'     log.solve | tail -1 | grep -oE '[0-9.]+$' || echo "")
NEXEC=$(grep -c '^ExecutionTime = ' log.solve || echo 0)
NOTE=clean
[ -f ABORT ] && NOTE=STOPPED_BY_REGISTERED_STOP_RULE
[ "$RC" != "0" ] && [ "$NOTE" = "clean" ] && NOTE=SOLVER_NONZERO_EXIT
{ echo "case=$(basename "$CASE")"; echo "rc=$RC"; echo "wall_s=$WALL"
  echo "ranks=$RANKS"; echo "core_min=$CM"; echo "timeout_s=0_NO_KILLING_CAP_SANAA_20260912_17"
  echo "execution_time_s=$EX"; echo "clock_time_s=$CL"
  echo "n_executiontime_lines=$NEXEC"; echo "resumed_from=500"
  echo "solver=buoyantBoussinesqSimpleFoam"; echo "note=$NOTE"
  echo "ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$HERE/STATUS.$(basename "$CASE")"
# AUTOGRADER, in the SAME detached session -> parented to init, survives the
# fleet, a supervisor ending and an ssh close (directive items 9 and 11).
bash "$HERE/autograde_k2g.sh" >> "$HERE/autograde.K2f_L3.out" 2>&1 || true
EOI
chmod +x "$CASE/.resume_inner.sh"

setsid bash "$CASE/.resume_inner.sh" "$CASE" "$RANKS" "$HERE" "$END_TIME" \
  </dev/null > "$CASE/.resume_outer.out" 2>&1 &
SOLVER_PID=$!
echo "$SOLVER_PID" > "$CASE/PIDS.resume"

setsid python3 "$HERE/monitor_k2g.py" "$CASE" "$RANKS" "$POINT_CORE_MIN" "$CAP_CORE_MIN" \
  </dev/null > "$CASE/.monitor_outer.out" 2>&1 &
MON_PID=$!
echo "$MON_PID" > "$CASE/PIDS.monitor"

say "LAUNCHED solver_sid=$SOLVER_PID monitor_sid=$MON_PID cwd=$CASE ranks=$RANKS"
say "  NO killing timeout. Stops come only from the registered rules, through ABORT."
say "  monitor  -> $CASE/MONITOR.K2f_L3.tsv"
say "  autograde-> $HERE/autograde.K2f_L3.out, K2g_GATE.json"
exit 0
