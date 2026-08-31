#!/usr/bin/env bash
# SO-1bR chain driver -- DERIVED from
# `cases/dafoam/ladder-a/A1/curriculum_SO1b/so1b_chain_driver.sh`
# (md5 0d1180dea70d82794856598a644f8fe9) with the REGISTERED DELTAS listed in
# PREREGISTRATION.md AMENDMENT 1 section A1.3 and recorded in
# `so1br_chain_driver_DELTAS_from_so1b.diff`.
#
# THE ONE SUBSTANTIVE DELTA IS THE PRECONDITION, AND IT IS WHY SO-1bR EXISTS.
# SO-1b evaluated its dependency on SO-1a inside an INLINE HEREDOC that globbed
# `SO1a_grade_*.json`.  That form is UNTESTABLE BY CONSTRUCTION -- no selftest
# can drive a heredoc that exists only inside a shell script -- and on
# 2026-08-28T02:31:50Z it fired for real and closed the item at rc=7 with
# `REFUSE no_gates.G5_PATCHED`.  SO-1bR evaluates the same question by EXECUTING
# A FILE whose md5 is asserted here and which is DRIVEN END TO END by 27 units.
#
# THE OTHER DELTAS ARE NAMES AND HASHES: run root, launcher, grader entry point,
# the ledger ITEM line, the driver pidfile, the emitted SO1BR_* strings, the
# grade output name, and the sibling-dependency block described where it stands.
# NO THRESHOLD, CEILING, POLL, BOUND, FLOOR, CAP OR EXIT CODE IS TOUCHED.
#
# The inherited comments below describe machinery that is unchanged.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/so1br_run_arm.sh"
GRADER="$HERE/so1br_grade_cli.py"
IMG_SHIPPED=dafoam/opt-packages:latest
IMG_PATCHED=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt
TUT_SRC=/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible
PERMISSION=bc0e687e
H5_FLOOR_GIB=8.0; H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6
AGG_POLL_S=30; AGG_BOUND_S=14400
# The launcher and grader are FROZEN (PREREGISTRATION.md section 7/8);
# asserted before EVERY arm so a mid-chain edit cannot change what runs.
MD5_LAUNCHER=9e1b626dc26b7ee04ea4ed4c7cffdff1
MD5_GRADER=f8dfc85d827f6fbf66ec425753fbd669
MD5_RUNSCRIPT=0557da51f6f179f6de865144343c499f
MD5_OF=0f14244bee5fafc698e80060782a7606
MD5_DECOMP=e6f1b0060944bc86d6dff56480ad2bd4
# the shipped tutorial's INPUT bytes, frozen here because the checkout is not
MD5_TUT_RUNSCRIPT=0557da51f6f179f6de865144343c499f
MD5_TUT_GEN=681f10659eb90457fca13fc933008b93
MD5_TUT_PREPROC=4a9395452540705686acf94898aa33af
MD5_TUT_PS=51dfed28e1bdb4cd33e0d8d7dabd586a
MD5_TUT_SS=4a6b8ef4501494c7693b71e88a2eabbf
MD5_TUT_FFD=6ddf378b028d03d8a18270488bee1759
test $# -ge 1 || { echo "ABORT usage: so1b_chain_driver.sh <ARM...>"; exit 64; }
ARMS="$*"; STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/so1br_driver.pid"
cd "$HERE" || exit 4

# ===========================================================================
# G-SO1AR -- SO-1bR's REGISTERED DEPENDENCY, RE-REGISTERED AGAINST SO-1aR.
#
# SO-1b optimises using the gradients SO-1a finite-difference verifies.  The
# dependency is registered in PREREGISTRATION.md section 5 / AMENDMENT 1 and it
# is EVALUATED HERE, before the run root is created and before any container
# starts, so a failed precondition costs SO-1bR ZERO core-minutes.
#
# WHAT IS CHECKED, and why it is NOT the upstream item verdict.  The upstream
# ITEM verdict is `GATE FAIL` -- its SHIPPED row fails band D at shape[0] and
# shape[6], and that failure is the finding, not a defect.  Gating on the ITEM
# verdict would kill SO-1bR in exactly the case the upstream item expects.  What
# SO-1bR needs is narrower: the PATCHED row's OBJECTIVE gradient G5 and its
# CONSTRAINT gradient G5c must BOTH read PASS, because those are the two
# gradients a constrained optimiser consumes.
#
# G-PROV RIDES HERE.  The precondition REFUSES unless the upstream SHIPPED row
# status travels with the reading, so this driver CANNOT START A CHAIN without
# the upstream GATE FAIL on the record.  The reading is written to a file and
# echoed, and it is composed in Python and passed through `printf %s` -- never
# interpolated into an unquoted heredoc, which is how this lab lost those two
# words from its only handoff channel on 2026-08-30 (commit e779bdc7).
#
# THREE OUTCOMES, all registered before compute; the exit codes are the
# precondition file's own and are driven in its selftest:
#   rc=0  PROCEED -- the chain proceeds
#   rc=7  the registered NO-LAUNCH branch -- ZERO core-minutes, verdict BLOCKED
#   rc=4  a REFUSAL (input absent, md5 moved, channels disagree, provenance
#         missing) -- ZERO core-minutes, verdict BLOCKED.  An unreadable
#         dependency is not a licence to proceed.
# ===========================================================================
PRECOND="$HERE/so1br_precondition.py"
AGG="$HERE/so1br_aggregate_memory.py"
MD5_PRECOND=447eaada4a896fc5f8b0f4ced4cb2af8
MD5_AGG=709ab0b98ef0302a3a3a318588f9493f
test -f "$PRECOND" || { echo "ABORT the registered precondition file is absent: $PRECOND"; exit 4; }
echo "$MD5_PRECOND  $PRECOND" | md5sum -c - || { echo "ABORT precondition md5 drifted"; exit 4; }
GSO1AR_OUT="$HERE/G_SO1AR.$(date -u +%Y%m%dT%H%M%SZ).txt"
GSO1AR_OUTPUT=$(python3 "$PRECOND" 2>&1); GSO1AR_RC=$?
GSO1AR_LINE=$(printf '%s\n' "$GSO1AR_OUTPUT" | head -1)
printf '%s\n' "SO1BR_G_SO1AR stamp=$(date -u +%Y%m%dT%H%M%SZ) rc=$GSO1AR_RC reading=[$GSO1AR_LINE]" | tee "$GSO1AR_OUT"
printf '%s\n' "$GSO1AR_OUTPUT" >> "$GSO1AR_OUT"
if [ "$GSO1AR_RC" -ne 0 ]; then
  echo "ABORT G-SO1AR the registered precondition did not PROCEED (rc=$GSO1AR_RC)."
  echo "  SO-1bR's registered no-launch branch: NOTHING IS LAUNCHED, ZERO core-minutes"
  echo "  are spent, and the SO-1bR item verdict is BLOCKED."
  echo "  reading: $GSO1AR_LINE"
  exit 7
fi

# ---- the launcher's SELFTEST-ONLY variables must be unset in a real chain ----
# The G-ROOT.5 / cap-preflight selftest drives PLANTED COPIES of the launcher and
# never the frozen file, so nothing here should ever be set.  Refusing on it
# anyway costs nothing and closes the shape of hole that an env hook would open.
for _v in SO1BR_SELFTEST SO1BR_SELFTEST_PREREG SO1BR_PREREG; do
  if [ -n "${!_v:-}" ]; then echo "ABORT selftest variable $_v is set in a real chain"; exit 4; fi
done
echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before staging"; exit 4; }
echo "$MD5_GRADER  $GRADER" | md5sum -c - || { echo "ABORT grader md5 drifted before staging"; exit 4; }
# ---- SO2a-DRIVER-DEF-1: EVERY SIBLING THIS DRIVER EXECUTES OR COPIES IS
# ---- ASSERTED TO **EXIST** BEFORE ANY md5 IS CHECKED.
# SO-2a's copy-forward took the chain driver and NOT the `*_aggregate_memory.py`
# it calls inside a `while true` loop.  The reference resolved to nothing, AGG
# was the empty string, the `ok` test could never be true, and the chain was
# GUARANTEED to poll to its 4 h bound at the first arm -- an 8 GiB reservation
# held for four hours to produce no verdict.  The freeze did not catch it
# because an instrument table that enumerates INSTRUMENTS but not their
# DEPENDENCIES can be complete and wrong at the same time: eight of eight md5s
# AGREED while the ninth file had never existed in any commit.
# EXISTENCE FIRST, md5 SECOND.  A missing file must not reach a hash check.
for _dep in "$PRECOND" "$AGG" "$HERE/so1br_decomposeParDict" "$HERE/so1b_runScript.py" \
            "$HERE/so1b_of.py" "$LAUNCHER" "$GRADER"; do
  test -f "$_dep" || { echo "ABORT DEP-ABSENT this driver executes or copies a file that DOES NOT EXIST: $_dep"; exit 4; }
done
echo "SO1BR_DEPS_PRESENT n=7 note=existence-asserted-BEFORE-any-md5 (SO2a-DRIVER-DEF-1)"
{ echo "$MD5_AGG  $AGG"; echo "$MD5_DECOMP  $HERE/so1br_decomposeParDict";
  echo "$MD5_RUNSCRIPT  $HERE/so1b_runScript.py"; echo "$MD5_OF  $HERE/so1b_of.py"; } | md5sum -c - \
  || { echo "ABORT sibling dependency md5 drifted"; exit 4; }
# ---- (4) ROOT STAGING on the first fire only ------------------------------
if [ ! -d "$BASE" ]; then
  test -d "$TUT_SRC" || { echo "ABORT tutorial source absent: $TUT_SRC"; exit 4; }
  { echo "$MD5_TUT_RUNSCRIPT  $TUT_SRC/runScript.py"; echo "$MD5_TUT_GEN  $TUT_SRC/genAirFoilMesh.py"; echo "$MD5_TUT_PREPROC  $TUT_SRC/preProcessing.sh";
    echo "$MD5_TUT_PS  $TUT_SRC/profiles/NACA0012PS.profile"; echo "$MD5_TUT_SS  $TUT_SRC/profiles/NACA0012SS.profile"; echo "$MD5_TUT_FFD  $TUT_SRC/FFD/wingFFD.xyz"; } | md5sum -c - \
    || { echo "ABORT tutorial input md5 drifted (the checkout moved under this item; nothing staged)"; exit 4; }
  mkdir -p "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
  chmod 777 "$BASE" || { echo "ABORT chmod 777 $BASE (L-251)"; exit 4; }
  mkdir -p "$BASE/base" || exit 4
  cp -a "$TUT_SRC/0.orig" "$TUT_SRC/FFD" "$TUT_SRC/constant" "$TUT_SRC/system" "$TUT_SRC/profiles" "$TUT_SRC/genAirFoilMesh.py" "$TUT_SRC/preProcessing.sh" "$BASE/base/" || { echo "ABORT copy tutorial inputs"; exit 4; }
  rm -rf "$BASE/base/constant/polyMesh" 2>/dev/null
  cp -a "$HERE/so1br_decomposeParDict" "$BASE/base/system/decomposeParDict" || { echo "ABORT overlay decomposeParDict"; exit 4; }
  cp -a "$HERE/so1b_runScript.py" "$HERE/so1b_of.py" "$BASE/" || { echo "ABORT copy instruments"; exit 4; }
  # D5-DRIVER-DEF-1 corrected form, inherited: identity on its own line;
  # staging metadata on a line that does not start with ITEM=.
  echo "ITEM=SO1bR" > "$BASE/ledger.txt"
  echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) tut_src=$TUT_SRC tut_commit=$(git -C "$TUT_SRC" rev-parse HEAD 2>/dev/null || echo NOT_MEASURED) permission=$PERMISSION" >> "$BASE/ledger.txt"
  echo "SO1BR_ROOT_STAGED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ) mode=$(stat -c '%a' "$BASE") permission=$PERMISSION"
else
  echo "SO1BR_ROOT_PRESENT base=$BASE (not re-staged)"
fi
{ echo "$MD5_RUNSCRIPT  $BASE/so1b_runScript.py"; echo "$MD5_OF  $BASE/so1b_of.py"; echo "$MD5_DECOMP  $BASE/base/system/decomposeParDict";
  echo "$MD5_TUT_GEN  $BASE/base/genAirFoilMesh.py"; echo "$MD5_TUT_PREPROC  $BASE/base/preProcessing.sh";
  echo "$MD5_TUT_PS  $BASE/base/profiles/NACA0012PS.profile"; echo "$MD5_TUT_SS  $BASE/base/profiles/NACA0012SS.profile"; echo "$MD5_TUT_FFD  $BASE/base/FFD/wingFFD.xyz"; } | md5sum -c - || { echo "ABORT staged instrument/input md5"; exit 4; }
test -f "$BASE/base/0.orig/U" || { echo "ABORT staged base/ has no 0.orig/U"; exit 4; }
if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."; exit 3
  fi
fi
echo "$$" > "$PIDFILE"
# ---- CHAIN_DONE: the FIXED-NAME chain-end marker.  SO-1a has none, which is
# ---- why SO-1b's wait-wrapper had to take SO-1a's LAST ARM ARTEFACT as its
# ---- precondition instead (PREREGISTRATION.md section 1a).  SO-1c and anything
# ---- else that must wait on THIS chain gets a marker written on EVERY exit of
# ---- a started chain, success or stop -- the D5 Addendum 3 / D6 Addendum 3 form.
trap 'rm -f "$PIDFILE"; echo "chain_done stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ arms=[$ARMS]" >> "$BASE/CHAIN_DONE"' EXIT
echo "SO1BR_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] permission=$PERMISSION"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) permission=$PERMISSION" >> "$STATUS"
mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
cap_mem_gib() { echo 4; }   # every arm 4g (PREREGISTRATION.md section 4)
img_of() { case "$1" in MESH|O-S|E-S) echo "$IMG_SHIPPED" ;; O-P|E-P) echo "$IMG_PATCHED" ;; *) echo "" ;; esac; }
CHAIN_RC=0
for ARM in $ARMS; do
  IMG=$(img_of "$ARM"); test -n "$IMG" || { echo "ABORT arm $ARM names no registered row"; echo "chain=ABORT arm=$ARM reason=no_row stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=64; break; }
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before arm $ARM"; echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=4; break; }
  # ---- (5) STATUS.<arm> is OPENED here (preflight line) and APPENDED from now
  # ---- on; the LAST line carries the rc.  Every AGGREGATE_WAIT is a line in it.
  echo "preflight arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ image=$IMG permission=$PERMISSION" > "$BASE/STATUS.$ARM"
  # ---- (3) ALREADY BOUGHT: a launcher-written rc=0 row for this arm means a
  # ---- re-fire would re-stage a graded arm.  REFUSED.
  if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT ALREADY_BOUGHT arm $ARM has an rc=0 ledger row; a second record for one run is the defect."
    echo "rc=3 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=ALREADY_BOUGHT permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=REFUSED_ALREADY_BOUGHT arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=3; break
  fi
  # ---- H5: a WINDOW of MemAvailable, every sample above the floor
  H5_FILE="$BASE/${ARM}_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"; BELOW=0; N=0; MIN=999; MAX=0
  STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))")
  for _ in $(seq 1 $H5_SAMPLES); do
    s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"
    MIN=$(python3 -c "print(min($MIN,$s))"); MAX=$(python3 -c "print(max($MAX,$s))")
    [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1))
    sleep "$STEP"
  done
  echo "SO1BR_H5_WINDOW arm=$ARM n=$N window_s=$H5_WINDOW_S floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAX samples_below_floor=$BELOW file=$(basename "$H5_FILE")"
  if [ "$BELOW" -gt 0 ] || [ "$N" -ne "$H5_SAMPLES" ]; then
    echo "ABORT H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB.  A batch that OOMs is worse than a batch that queues.  REFUSED."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_REFUSED below=$BELOW min_GiB=$MIN permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_H5 arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=6; break
  fi
  # ---- (2) AGGREGATE: live container caps + this cap + host non-container RSS,
  # ---- WAIT-AND-RETRY (UPDATE F ruling): poll AGG_POLL_S, bounded AGG_BOUND_S;
  # ---- every wait written to STATUS.<arm>; refuse-and-BLOCK at the bound.
  WAITED=0; AGG_SERIES="$BASE/${ARM}_aggregate_series.txt"; AGG_BLOCKED=no
  while true; do
    # ---- CALL-SITE GUARD (ADDENDUM 3, 2026-08-31; CLAUDE.md rule 14) ---------
    # $AGG must STILL name the registered script AT THE POINT OF USE.  The
    # startup existence check (:121) and the md5 registration (:126) both ran
    # while AGG held a path, and NOTHING re-asserted it here -- so when the old
    # line below overwrote AGG with its own JSON output, the second arm polled
    # silently to AGG_BOUND_S and wrote a FALSE BLOCKED_AGGREGATE record.
    # A lesson is not applied until EVERY call site asserts it.  `break 2`
    # leaves the while AND the arm loop, landing exactly where :217's break
    # lands, so no path from here reaches the launcher.
    test -f "$AGG" || { echo "ABORT AGG no longer names an existing file at the point of use: [$AGG]"; echo "rc=4 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=AGG_PATH_DESTROYED_AT_CALL_SITE permission=$PERMISSION" >> "$BASE/STATUS.$ARM"; echo "chain=ABORT arm=$ARM reason=agg_path_destroyed stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=4; break 2; }
    AGG_JSON=$(python3 "$AGG" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
    echo "$(date -u +%s) $AGG_JSON" >> "$AGG_SERIES"
    if [ "$(printf '%s' "$AGG_JSON" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ]; then break; fi
    if [ "$WAITED" -ge "$AGG_BOUND_S" ]; then
      echo "ABORT AGGREGATE still over $AGG_CEILING_GIB GiB after ${WAITED}s.  BLOCKED.  Series: $(basename "$AGG_SERIES")"
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=AGGREGATE_BLOCKED_AT_BOUND waited=$WAITED series=$(basename "$AGG_SERIES") permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_AGGREGATE arm=$ARM waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; AGG_BLOCKED=yes; break
    fi
    echo "AGGREGATE_WAIT waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM $AGG_JSON" >> "$BASE/STATUS.$ARM"
    sleep "$AGG_POLL_S"; WAITED=$((WAITED+AGG_POLL_S))
  done
  if [ "$AGG_BLOCKED" = "yes" ]; then CHAIN_RC=6; break; fi
  echo "SO1BR_AGGREGATE arm=$ARM waited=$WAITED $AGG_JSON"
  echo "SO1BR_DRIVER arm=$ARM image=$IMG begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID permission=$PERMISSION"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "SO1BR_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN aggregate_waited_s=$WAITED permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=$rc; break; fi
done
[ "$CHAIN_RC" -eq 0 ] && echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
# ---- (6) the FROZEN grader on the artefacts (zero compute); its rc is INFRASTRUCTURE (L-342)
GSTAMP=$(date -u +%Y%m%dT%H%M%SZ)
if echo "$MD5_GRADER  $GRADER" | md5sum -c - > /dev/null; then
  python3 "$GRADER" --root "$BASE" --out "$BASE/SO1bR_grade_${GSTAMP}.json" > "$BASE/SO1bR_grade_${GSTAMP}.out" 2>&1; GRC=$?
  echo "grader_rc=$GRC stamp=$GSTAMP out=SO1bR_grade_${GSTAMP}.json note=comparator-exit-status-NOT-the-verdict" >> "$STATUS"
else
  echo "grader_rc=NOT_RUN stamp=$GSTAMP note=grader-md5-drifted-at-chain-end" >> "$STATUS"
fi
echo "SO1BR_DRIVER end=$(date -u +%Y%m%dT%H%M%SZ) chain_rc=$CHAIN_RC"
exit "$CHAIN_RC"
