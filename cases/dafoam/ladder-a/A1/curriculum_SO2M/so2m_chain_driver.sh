#!/usr/bin/env bash
# SO-2M chain driver -- DERIVED from curriculum_SO1a/so1a_chain_driver.sh
# (md5 4a5bd3c6a6dcbcf5f0b2a2c0d0000000 is NOT asserted here; the parent's md5 is
# read and printed at run time by the selftest, and the DELTAS are recorded in
# so2m_chain_driver_DELTAS_from_so1a.diff).
#
# THE REGISTERED DELTAS, and the four that are NEW MACHINERY rather than renaming:
#   (1) item names, run root, arms MESH X-S G-S X-P G-P, instrument so2m_xm.py,
#       producer so2m_runScript.py with its NEW md5 (the third functional CMZ is
#       added to daOptions -- SO-2a section 0.1(2) predicted exactly this), and the
#       frozen launcher/grader md5s.
#   (2) THE FOUR NO-LAUNCH BRANCHES of PREREGISTRATION.md section 10, each writing
#       its NAMED file and exiting with its NAMED rc, each costing 0.00 core-min:
#         NL-1 AGGREGATE  NOLAUNCH_AGGREGATE.txt  rc=6  BLOCKED
#         NL-2 PRODUCER   NOLAUNCH_PRODUCER.txt   rc=4  BLOCKED
#         NL-3 ROOT       NOLAUNCH_ROOT.txt       rc=3  BLOCKED
#         NL-4 FREEZE     NOLAUNCH_FREEZE.txt     rc=5  BLOCKED
#   (3) NL-2 IS COMPUTED, NOT ASSERTED.  The producer is diffed against the
#       TUTORIAL and the added lines must be EXACTLY the ten registered insertions
#       with NO removal; the tutorial's own md5 must be the frozen one.  The
#       offending hunks are written into NOLAUNCH_PRODUCER.txt.
#   (4) SECTION 18.7 -- THE AGGREGATE WAIT IS BOUNDED AND TERMINATES WITH A
#       NON-ZERO rc.  It NEVER blocks-and-continues, and NOLAUNCH_AGGREGATE.txt
#       STATES THE FRACTION OF THE DECLARED PROGRAM A BLOCK DISCARDS -- computed
#       from the arms already bought, not guessed.
#
# The inherited machinery below is unchanged: root staging on the first fire, the
# md5 assertion of every staged input before EVERY arm, the pidfile, STATUS.<arm>,
# the H5 window, ALREADY_BOUGHT, and the FROZEN grader run at chain end whose rc is
# INFRASTRUCTURE and never the verdict (L-342).
#
# Runs the named arms IN ORDER through the frozen launcher and STOPS AT THE FIRST
# NON-ZERO rc.  Started ONLY detached (the queue runner's own form, or
#   setsid nohup bash so2m_chain_driver.sh MESH X-S G-S X-P G-P > <root>/chain_launch.out 2>&1 &
# ) so it is its own session leader and outlives the agent that started it.
# cwd is the CASE directory, never the run root (G-ROOT.5 b).
# Permission for detached launches: bc0e687e (Sanaa, boarded verbatim).
#
# `set -e` DOES NOT GATE through pipes or heredocs.  Every step below gates
# explicitly with `|| { ...; exit N; }`, and every rc is captured DIRECTLY from the
# command, never through a pipe (a pipeline's `$?` is the LAST stage's).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/so2m_run_arm.sh"
GRADER="$HERE/so2m_grade.py"
IMG_SHIPPED=dafoam/opt-packages:latest
IMG_PATCHED=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient
TUT_SRC=/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible
PERMISSION=bc0e687e
H5_FLOOR_GIB=8.0; H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6
AGG_POLL_S=30; AGG_BOUND_S=14400
DECLARED_ARMS=5                       # the declared program: five arms (section 4)
# The launcher, grader and instruments are FROZEN (PREREGISTRATION.md section 10
# Stage-2 amendment); asserted before EVERY arm so a mid-chain edit cannot change
# what runs.  EVERY pin below is DRIVEN by so2m_pin_selftest.sh, which enumerates
# the MD5_* variables OUT OF THIS FILE'S OWN BYTES and checks each -- so "every
# pin" is a count, not a claim (SO-1c's driver carried twelve pins and its leg
# drove four while claiming every one).
MD5_LAUNCHER=3a4300c0545f23a1be5794449db01595
MD5_GRADER=4c355c3fb07276bee72cdd09a707638e
MD5_RUNSCRIPT=ae4a73429dd6972dc804b76d9a44aa05
MD5_XM=2bf45db9197c49d37bed30e55f6ff2ef
MD5_DECOMP=e6f1b0060944bc86d6dff56480ad2bd4
# the shipped tutorial's INPUT bytes, frozen here because the checkout is not
MD5_TUT_RUNSCRIPT=0557da51f6f179f6de865144343c499f
MD5_TUT_GEN=681f10659eb90457fca13fc933008b93
MD5_TUT_PREPROC=4a9395452540705686acf94898aa33af
MD5_TUT_PS=51dfed28e1bdb4cd33e0d8d7dabd586a
MD5_TUT_SS=4a6b8ef4501494c7693b71e88a2eabbf
MD5_TUT_FFD=6ddf378b028d03d8a18270488bee1759

test $# -ge 1 || { echo "ABORT usage: so2m_chain_driver.sh <ARM...>"; exit 64; }
ARMS="$*"; STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/so2m_driver.pid"
cd "$HERE" || exit 4
STAMP0=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# ---- the NO-LAUNCH writers.  Each writes its NAMED file into the CASE directory
# ---- (always writable, and where the pre-registration lives) and, when the run
# ---- root exists, a copy beside the ledger.  Each costs 0.00 core-min.
nolaunch() {
  NLNAME="$1"; NLRC="$2"; NLBODY="$3"
  {
    echo "SO2M NO-LAUNCH BRANCH $NLNAME"
    echo "verdict=BLOCKED rc=$NLRC core_min=0.00 stamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "registered at: PREREGISTRATION.md section 10"
    echo "SUBMISSIONS PARKED (CLAUDE.md rule 7): nothing about this item leaves this box."
    echo "---"
    printf '%s\n' "$NLBODY"
  } > "$HERE/NOLAUNCH_${NLNAME}.txt"
  if [ -d "$BASE" ]; then cp -a "$HERE/NOLAUNCH_${NLNAME}.txt" "$BASE/NOLAUNCH_${NLNAME}.txt" 2>/dev/null; fi
  echo "SO2M_NOLAUNCH $NLNAME rc=$NLRC verdict=BLOCKED file=$HERE/NOLAUNCH_${NLNAME}.txt"
}

# =============================================================================
# NL-4 FREEZE (rc=5) -- the FROZEN grader and launcher must be the frozen bytes.
# Checked FIRST because everything below trusts them.
# =============================================================================
echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - > /dev/null
RC_L=$?
echo "$MD5_GRADER  $GRADER" | md5sum -c - > /dev/null
RC_G=$?
if [ "$RC_L" -ne 0 ] || [ "$RC_G" -ne 0 ]; then
  nolaunch FREEZE 5 "launcher $LAUNCHER pinned $MD5_LAUNCHER got $(md5sum "$LAUNCHER" 2>/dev/null | cut -d' ' -f1)
grader   $GRADER   pinned $MD5_GRADER   got $(md5sum "$GRADER"   2>/dev/null | cut -d' ' -f1)
A frozen file whose md5 has drifted is not the file that was registered.  Nothing staged, no container started."
  exit 5
fi

# =============================================================================
# NL-2 PRODUCER (rc=4) -- the producer must differ from the TUTORIAL by EXACTLY
# the ten registered insertions of section 3 and by NO removal, and the
# tutorial's own md5 must be the frozen one.  COMPUTED, not asserted.
# =============================================================================
test -f "$HERE/so2m_runScript.py" || { nolaunch PRODUCER 4 "so2m_runScript.py is absent from $HERE"; exit 4; }
PRODUCER_REPORT=$(python3 - "$TUT_SRC/runScript.py" "$HERE/so2m_runScript.py" "$MD5_TUT_RUNSCRIPT" "$MD5_RUNSCRIPT" <<'PYEOF'
import difflib, hashlib, json, os, sys
tut, prod, tut_md5_want, prod_md5_want = sys.argv[1:5]
INSERTIONS = (
    "L0 = 1.0",
    '        "CMZ": {',
    '            "type": "moment",',
    '            "source": "patchToFace",',
    '            "patches": ["wing"],',
    '            "axis": [0.0, 0.0, 1.0],',
    '            "center": [0.25, 0.0, 0.05],',
    "            # NOTE. We scale it with -1 because DAFoam's CMZ calculation is positive for nose down",
    '            "scale": -1.0 / (0.5 * U0 * U0 * A0 * L0),',
    "        },",
)
def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()
out = {"ok": False}
if not os.path.isfile(tut):
    out["problem"] = "tutorial source absent: %s" % tut
else:
    tm, pm = md5(tut), md5(prod)
    added, removed, hunks = [], [], []
    for line in difflib.unified_diff(open(tut).read().split("\n"),
                                     open(prod).read().split("\n"), lineterm="", n=0):
        if line.startswith(("+++", "---")):
            continue
        hunks.append(line)
        if line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("-"):
            removed.append(line[1:])
    out.update({"tutorial_md5": tm, "tutorial_md5_want": tut_md5_want,
                "producer_md5": pm, "producer_md5_want": prod_md5_want,
                "n_added": len(added), "n_removed": len(removed)})
    problems = []
    if tm != tut_md5_want:
        problems.append("the TUTORIAL checkout moved under this item: md5 %s != %s" % (tm, tut_md5_want))
    if pm != prod_md5_want:
        problems.append("the PRODUCER md5 %s != the pinned %s" % (pm, prod_md5_want))
    if removed:
        problems.append("the producer REMOVES %d tutorial line(s); the registration adds only" % len(removed))
    if tuple(added) != INSERTIONS:
        problems.append("the added lines are not EXACTLY the ten registered insertions")
    out["ok"] = not problems
    out["problems"] = problems
    if problems:
        out["offending_hunks"] = hunks[:80]
print(json.dumps(out, indent=1))
PYEOF
)
RC_P=$?
PRODUCER_OK=$(printf '%s' "$PRODUCER_REPORT" | python3 -c "import sys,json
try: print('1' if json.load(sys.stdin).get('ok') else '0')
except Exception: print('0')")
if [ "$RC_P" -ne 0 ] || [ "$PRODUCER_OK" != "1" ]; then
  nolaunch PRODUCER 4 "$PRODUCER_REPORT"
  exit 4
fi
echo "SO2M_PRODUCER_OK $(printf '%s' "$PRODUCER_REPORT" | tr -d '\n' | cut -c1-220)"

# =============================================================================
# NL-3 ROOT (rc=3) -- three disjuncts, exactly as section 10 registers them:
#   (a) the run root ALREADY EXISTS at driver start (the freeze condition of
#       section 2 is that it does not);
#   (b) a LIVE container or a LIVE driver holds this item's prefix;
#   (c) an rc=0 ledger row would be RE-FIRED (ALREADY_BOUGHT) -- checked per arm
#       inside the loop, and routed through this same branch.
# =============================================================================
LIVE_PREFIX=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep '^so2m_' | head -5 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_PREFIX" ]; then
  nolaunch ROOT 3 "a LIVE container carries this item's prefix: [$LIVE_PREFIX]
Two records for one run is the defect.  Nothing staged."
  exit 3
fi
if [ -e "$BASE" ]; then
  nolaunch ROOT 3 "the run root ALREADY EXISTS: $BASE
PREREGISTRATION.md section 2 records this item's freeze condition as the ABSENCE of that
directory, verified at 2026-08-31T17:18:59Z beside a known positive.  A root that exists at
driver start means a previous invocation created it, so this fire would be a SECOND record
for one run.  The existing root is INSPECTED, never deleted and never overwritten by this
driver (CLAUDE.md rule 10: an unexpected artefact is inspected, never reverted).
contents: $(ls -1 "$BASE" 2>/dev/null | head -20 | tr '\n' ' ')"
  exit 3
fi
if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    nolaunch ROOT 3 "another driver is LIVE (pid $OLD, $PIDFILE).  Two records for one run is the defect."
    exit 3
  fi
fi

# ---- ROOT STAGING on the first fire only ------------------------------------
test -d "$TUT_SRC" || { nolaunch PRODUCER 4 "tutorial source absent: $TUT_SRC"; exit 4; }
{ echo "$MD5_TUT_RUNSCRIPT  $TUT_SRC/runScript.py"; echo "$MD5_TUT_GEN  $TUT_SRC/genAirFoilMesh.py"; echo "$MD5_TUT_PREPROC  $TUT_SRC/preProcessing.sh";
  echo "$MD5_TUT_PS  $TUT_SRC/profiles/NACA0012PS.profile"; echo "$MD5_TUT_SS  $TUT_SRC/profiles/NACA0012SS.profile"; echo "$MD5_TUT_FFD  $TUT_SRC/FFD/wingFFD.xyz"; } | md5sum -c - > /dev/null
RC_T=$?
[ "$RC_T" -eq 0 ] || { nolaunch PRODUCER 4 "tutorial input md5 drifted (the checkout moved under this item; nothing staged)"; exit 4; }
mkdir -p "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
chmod 777 "$BASE" || { echo "ABORT chmod 777 $BASE (L-251)"; exit 4; }
mkdir -p "$BASE/base" || exit 4
cp -a "$TUT_SRC/0.orig" "$TUT_SRC/FFD" "$TUT_SRC/constant" "$TUT_SRC/system" "$TUT_SRC/profiles" "$TUT_SRC/genAirFoilMesh.py" "$TUT_SRC/preProcessing.sh" "$BASE/base/" || { echo "ABORT copy tutorial inputs"; exit 4; }
rm -rf "$BASE/base/constant/polyMesh" 2>/dev/null
cp -a "$HERE/so2m_decomposeParDict" "$BASE/base/system/decomposeParDict" || { echo "ABORT overlay decomposeParDict"; exit 4; }
cp -a "$HERE/so2m_runScript.py" "$HERE/so2m_xm.py" "$BASE/" || { echo "ABORT copy instruments"; exit 4; }
echo "ITEM=SO2M" > "$BASE/ledger.txt"
echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) tut_src=$TUT_SRC tut_commit=$(git -C "$TUT_SRC" rev-parse HEAD 2>/dev/null || echo NOT_MEASURED) permission=$PERMISSION" >> "$BASE/ledger.txt"
echo "SO2M_ROOT_STAGED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ) mode=$(stat -c '%a' "$BASE") permission=$PERMISSION"

{ echo "$MD5_RUNSCRIPT  $BASE/so2m_runScript.py"; echo "$MD5_XM  $BASE/so2m_xm.py"; echo "$MD5_DECOMP  $BASE/base/system/decomposeParDict";
  echo "$MD5_TUT_GEN  $BASE/base/genAirFoilMesh.py"; echo "$MD5_TUT_PREPROC  $BASE/base/preProcessing.sh";
  echo "$MD5_TUT_PS  $BASE/base/profiles/NACA0012PS.profile"; echo "$MD5_TUT_SS  $BASE/base/profiles/NACA0012SS.profile"; echo "$MD5_TUT_FFD  $BASE/base/FFD/wingFFD.xyz"; } | md5sum -c - > /dev/null
RC_S=$?
[ "$RC_S" -eq 0 ] || { nolaunch FREEZE 5 "staged instrument/input md5 mismatch under $BASE"; exit 5; }
test -f "$BASE/base/0.orig/U" || { echo "ABORT staged base/ has no 0.orig/U"; exit 4; }

echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"' EXIT
echo "SO2M_DRIVER start=$STAMP0 pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] permission=$PERMISSION"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) permission=$PERMISSION" >> "$STATUS"
mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
cap_mem_gib() { echo 4; }   # every arm 4g (PREREGISTRATION.md section 4)
img_of() { case "$1" in MESH|*-S) echo "$IMG_SHIPPED" ;; *-P) echo "$IMG_PATCHED" ;; *) echo "" ;; esac; }
BOUGHT=0
CHAIN_RC=0
for ARM in $ARMS; do
  IMG=$(img_of "$ARM"); test -n "$IMG" || { echo "ABORT arm $ARM names no registered row"; echo "chain=ABORT arm=$ARM reason=no_row stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=64; break; }
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - > /dev/null
  RC_LA=$?
  if [ "$RC_LA" -ne 0 ]; then
    nolaunch FREEZE 5 "launcher md5 drifted mid-chain, before arm $ARM.  Arms already bought: $BOUGHT of $DECLARED_ARMS."
    echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=5; break
  fi
  echo "preflight arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ image=$IMG permission=$PERMISSION" > "$BASE/STATUS.$ARM"
  # ---- NL-3 (c) ALREADY BOUGHT ---------------------------------------------
  if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
    nolaunch ROOT 3 "ALREADY_BOUGHT: arm $ARM already has an rc=0 ledger row.  A second record
for one run is the defect.  The existing rc=0 rows are KEPT, never re-run and never deleted."
    echo "rc=3 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=ALREADY_BOUGHT permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=REFUSED_ALREADY_BOUGHT arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=3; break
  fi
  # ---- H5: a WINDOW of MemAvailable, every sample above the floor -----------
  H5_FILE="$BASE/${ARM}_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"; BELOW=0; N=0; MIN=999; MAX=0
  STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))")
  for _ in $(seq 1 $H5_SAMPLES); do
    s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"
    MIN=$(python3 -c "print(min($MIN,$s))"); MAX=$(python3 -c "print(max($MAX,$s))")
    [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1))
    sleep "$STEP"
  done
  echo "SO2M_H5_WINDOW arm=$ARM n=$N window_s=$H5_WINDOW_S floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAX samples_below_floor=$BELOW file=$(basename "$H5_FILE")"
  if [ "$BELOW" -gt 0 ] || [ "$N" -ne "$H5_SAMPLES" ]; then
    DISCARD=$((DECLARED_ARMS-BOUGHT))
    nolaunch AGGREGATE 6 "H5 WINDOW REFUSED before arm $ARM: $BELOW of $N samples below $H5_FLOOR_GIB GiB (min $MIN, max $MAX).
A batch that OOMs is worse than a batch that queues.
SECTION 18.7 DISCARD ACCOUNTING: arms bought $BOUGHT of $DECLARED_ARMS; this block discards
$DISCARD of $DECLARED_ARMS arms, and the ledger's rc=0 rows are KEPT, never re-run, never deleted.
series: $(basename "$H5_FILE")"
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_REFUSED below=$BELOW min_GiB=$MIN permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_H5 arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=6; break
  fi
  # ---- NL-1 AGGREGATE: a BOUNDED WAIT that TERMINATES WITH A NON-ZERO rc ----
  # ---- It NEVER proceeds after a wait it lost and NEVER returns 0 on expiry.
  WAITED=0; AGG_SERIES="$BASE/${ARM}_aggregate_series.txt"; AGG_BLOCKED=no
  while true; do
    AGG=$(python3 "$HERE/so2m_aggregate_memory.py" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
    echo "$(date -u +%s) $AGG" >> "$AGG_SERIES"
    if [ "$(printf '%s' "$AGG" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ]; then break; fi
    if [ "$WAITED" -ge "$AGG_BOUND_S" ]; then AGG_BLOCKED=yes; break; fi
    echo "AGGREGATE_WAIT waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM $AGG" >> "$BASE/STATUS.$ARM"
    sleep "$AGG_POLL_S"; WAITED=$((WAITED+AGG_POLL_S))
  done
  if [ "$AGG_BLOCKED" = "yes" ]; then
    DISCARD=$((DECLARED_ARMS-BOUGHT))
    nolaunch AGGREGATE 6 "AGGREGATE still over $AGG_CEILING_GIB GiB after ${WAITED}s against the registered
BOUND of ${AGG_BOUND_S}s.  The wait is BOUNDED and TERMINATES WITH A NON-ZERO rc; it does not
block-and-continue and it does not return 0 on expiry (PREREGISTRATION.md section 10, 18.7).
sampled: $AGG
SECTION 18.7 DISCARD ACCOUNTING: arms bought $BOUGHT of $DECLARED_ARMS; this block discards
$DISCARD of $DECLARED_ARMS arms ($(python3 -c "print('%.0f' % (100.0*$DISCARD/$DECLARED_ARMS))") %% of the declared program).
The ledger's rc=0 rows are KEPT, never re-run and never deleted.
series: $(basename "$AGG_SERIES")"
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=AGGREGATE_BLOCKED_AT_BOUND waited=$WAITED series=$(basename "$AGG_SERIES") permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=BLOCKED_AGGREGATE arm=$ARM waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=6; break
  fi
  echo "SO2M_AGGREGATE arm=$ARM waited=$WAITED $AGG"
  echo "SO2M_DRIVER arm=$ARM image=$IMG begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID permission=$PERMISSION"
  # rc CAPTURED DIRECTLY from the launcher, never through a pipe.
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "SO2M_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN aggregate_waited_s=$WAITED permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=$rc; break; fi
  BOUGHT=$((BOUGHT+1))
done
[ "$CHAIN_RC" -eq 0 ] && echo "chain=COMPLETE arms_bought=$BOUGHT of $DECLARED_ARMS stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
# ---- the FROZEN grader on the artefacts (zero compute); its rc is INFRASTRUCTURE (L-342)
GSTAMP=$(date -u +%Y%m%dT%H%M%SZ)
echo "$MD5_GRADER  $GRADER" | md5sum -c - > /dev/null
RC_GE=$?
if [ "$RC_GE" -eq 0 ]; then
  python3 "$GRADER" --root "$BASE" --out "$BASE/SO2M_grade_${GSTAMP}.json" > "$BASE/SO2M_grade_${GSTAMP}.out" 2>&1
  GRC=$?
  echo "grader_rc=$GRC stamp=$GSTAMP out=SO2M_grade_${GSTAMP}.json note=comparator-exit-status-NOT-the-verdict" >> "$STATUS"
else
  nolaunch FREEZE 5 "the grader's md5 drifted BETWEEN the chain start and the chain end; the
artefacts are intact and are NOT graded by a file that is not the frozen one."
  echo "grader_rc=NOT_RUN stamp=$GSTAMP note=grader-md5-drifted-at-chain-end" >> "$STATUS"
fi
echo "SO2M_DRIVER end=$(date -u +%Y%m%dT%H%M%SZ) chain_rc=$CHAIN_RC arms_bought=$BOUGHT of $DECLARED_ARMS"
exit "$CHAIN_RC"
