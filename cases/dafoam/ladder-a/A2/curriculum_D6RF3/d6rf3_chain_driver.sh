#!/usr/bin/env bash
# D6RF chain driver -- F_mp then REF_off, the two arms D6R registered and never
# bought.  DERIVED from curriculum_D6R/d6r_chain_driver.sh (md5
# 623f3d3243ad5c9f092a7d4bfe1b01c5) with the registered deltas of D6RF
# PREREGISTRATION.md ADDENDUM 1.  THE DELTAS, enumerated:
#   1  item names, run root, launcher md5, arms F_mp REF_off
#   2  root staging also stages D4's four instruments and this item's three
#      (REF_off consumes D4's physical wrapper unmodified)
#   3  A CUMULATIVE SPEND ASSERTION before EVERY arm, against the item ceiling
#   4  the H5 and aggregate gates HOLD; they never refuse to launch
#
# Runs the named arms IN ORDER through the frozen launcher and STOPS AT THE
# FIRST NON-ZERO rc.  Started ONLY detached (the queue runner's own form, or
#   setsid nohup bash d6rf3_chain_driver.sh F_mp REF_off > <root>/chain_launch.out 2>&1 &
# ).
#
# rc PER ARM IS CAPTURED INSIDE THIS WRAPPER, never around a `setsid` line: it
# is the launcher's own exit, which is `docker inspect .State.ExitCode`, and it
# is written HERE into STATUS.<arm>.  `setsid timeout cmd` exits 0 for every
# outcome, so nothing here trusts `$?` of such a line.
#
# cwd is the CASE directory, never the run root (G-ROOT.5 b).
# Permission for detached launches: bc0e687e (Sanaa, boarded verbatim).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d6rf3_run_arm.sh"
IMG=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd
D4_CASE_DIR="$HERE/../curriculum_D4"
D6R_CASE_DIR="$HERE/../curriculum_D6R"
D4_BASE_SRC=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/base
AGGREGATE_READER="$D6R_CASE_DIR/d6r_aggregate_memory.py"
PERMISSION=bc0e687e

# ---- ITEM CEILING (PREREGISTRATION.md section 4d) -------------------------
ITEM_CEILING_CORE_MIN=670.0

# ---- H5 / AGGREGATE: THESE HOLD.  THEY NEVER REFUSE TO LAUNCH. ------------
# Sanaa 2026-09-03 ~21:00Z: resource gates are real physical limits, so they
# QUEUE -- "but queueing is not blocking; the run stays scheduled."  Her
# ~22:00Z ruling forbids any non-physics gate blocking a run, and the
# supervisor has separately ruled that d19t_run_arm.sh's G-QUIET
# refuse-to-launch form is NOT to be reproduced anywhere in this family.
# So: WAIT-AND-RETRY, every wait a line in STATUS.<arm>, and at the bound a
# RE-FIREABLE `BLOCKED` that has spent zero compute -- never a refusal.
# Measured at freeze: the only live container on this box is on cpuset 1 at
# 8 GiB, DISJOINT from this item's 2,3,4,14 at 20 GiB, and 8 + 20 + host RSS
# sits at or just over the 30.6 GiB ceiling.  HOLDING THE FIRST ARM UNTIL THAT
# CHAIN FINISHES IS THE CORRECT BEHAVIOUR AND IT IS REGISTERED, NOT DISCOVERED.
H5_FLOOR_GIB=24.0; H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6
AGG_POLL_S=30; AGG_BOUND_S=14400
H5_RETRY_S=60; H5_BOUND_S=14400

MD5_LAUNCHER=58684b91f6aced35f500fc947517a8e4   # d6rf3_run_arm.sh, RE-PINNED to this item's launcher
# 2026-09-03: re-pinned from 01e034e1c611e7fc4f0f4e31d3e34511 after the G-DELIVERY
# repair added the anchor gate to both arms' staging lists and inserted the derived
# delivery guard.  THE PIN IS NOT A FORMALITY: this driver asserts it TWICE per fire
# (:79 before staging, :152 before each arm) and a stale pin aborts at rc=4 before any
# container -- which is exactly what d6rf3_guard_selftest.py control U37 caught here,
# on the launcher's own bytes, before the re-fire.  The repair changed a file another
# file asserts about; updating the assertion is the second half of the repair and is
# not optional (CLAUDE.md rule 14: a lesson is not applied until EVERY call site
# asserts it).
MD5_CEILING_GUARD=1ea97c9245dedbc451d62e1bcfe26eb9   # cases/dafoam/_common/item_ceiling_guard.py
MD5_AGGREGATE=709ab0b98ef0302a3a3a318588f9493f
MD5_RUNSCRIPT6=137539e0a99be27f27fdb69e063b2a87
MD5_FD=24586c9ab7f733cd2b642775aaf7fbe3
MD5_EXTRACT6=7adc049421cce82f021603bbbe93dd1e
MD5_REFOFF=4f0e564fc9855f179cb3d0e55d306af6
MD5_EXTRACT4=ee7d3c99fd716da23779cb651961918e
MD5_RUNSCRIPT4=2906d52a5dbed2bacbaeaf85a37d3fe8
MD5_LOCUS4=e63df1845771c3e67457443918f5b82e
MD5_PHYS4=74c35c80bb4d395cf8939d851bc6b3f9
MD5_LOCUS6=341189ca866f302a7e1bba8eefad3a57
MD5_PHYS6=750fb6336502ca5f71c954298e995f58
MD5_UNITS=885ce236ed20d4be0337f4382346500a
MD5_ANCHOR_GATE=e823689c15c2459097d0441e553f565c

test $# -ge 1 || { echo "ABORT usage: d6rf3_chain_driver.sh <ARM...>"; exit 64; }
ARMS="$*"
for a in $ARMS; do
  case "$a" in
    F_mp|REF_off) : ;;
    *) echo "ABORT '$a' is not one of this item's two REGISTERED arms (F_mp, REF_off)."; exit 64 ;;
  esac
done
STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/d6rf3_driver.pid"
cd "$HERE" || exit 4
echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before staging"; exit 4; }
echo "$MD5_AGGREGATE  $AGGREGATE_READER" | md5sum -c - || { echo "ABORT aggregate reader md5 (D6R's, staged by path, unmodified)"; exit 4; }

# ---- ROOT STAGING on the first fire only ----------------------------------
if [ ! -d "$BASE" ]; then
  test -d "$D4_BASE_SRC" || { echo "ABORT D4 base source absent: $D4_BASE_SRC"; exit 4; }
  mkdir -p "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
  chmod 777 "$BASE" || { echo "ABORT chmod 777 $BASE (L-251)"; exit 4; }
  cp -a "$D4_BASE_SRC" "$BASE/base" || { echo "ABORT copy base/"; exit 4; }
  cp -a "$HERE/d6rf3_opt_runScript.py" "$HERE/d6rf3_fd_endpoint.py" \
        "$HERE/d6rf3_extract_endpoint.py" "$HERE/d6rf3_ref_off.py" \
        "$D4_CASE_DIR/d4_extract_endpoint.py" "$D4_CASE_DIR/d4_opt_runScript.py" \
        "$D4_CASE_DIR/d4_endpoint_locus.py" "$D4_CASE_DIR/d4_endpoint_physical.py" \
        "$HERE/d6rf3_endpoint_locus.py" "$HERE/d6rf3_endpoint_physical.py" \
        "$HERE/d6rf3_units_assert.py" "$HERE/d6rf3_anchor_gate.py" \
        "$BASE/" || { echo "ABORT copy instruments"; exit 4; }
  # G-ROOT.3 accepts ONLY an exact `ITEM=D6RF3` line; staging metadata goes on a
  # line that does not start with ITEM= (D5-DRIVER-DEF-1, inherited).
  echo "ITEM=D6RF3" > "$BASE/ledger.txt"
  echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) base_src=$D4_BASE_SRC permission=$PERMISSION" >> "$BASE/ledger.txt"
  echo "D6RF3_ROOT_STAGED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ) mode=$(stat -c '%a' "$BASE") permission=$PERMISSION"
else
  echo "D6RF3_ROOT_PRESENT base=$BASE (not re-staged)"
fi
{ echo "$MD5_RUNSCRIPT6  $BASE/d6rf3_opt_runScript.py"
  echo "$MD5_FD  $BASE/d6rf3_fd_endpoint.py"
  echo "$MD5_EXTRACT6  $BASE/d6rf3_extract_endpoint.py"
  echo "$MD5_REFOFF  $BASE/d6rf3_ref_off.py"
  echo "$MD5_EXTRACT4  $BASE/d4_extract_endpoint.py"
  echo "$MD5_RUNSCRIPT4  $BASE/d4_opt_runScript.py"
  echo "$MD5_LOCUS4  $BASE/d4_endpoint_locus.py"
  echo "$MD5_PHYS4  $BASE/d4_endpoint_physical.py"
  echo "$MD5_LOCUS6  $BASE/d6rf3_endpoint_locus.py"
  echo "$MD5_PHYS6  $BASE/d6rf3_endpoint_physical.py"
  echo "$MD5_UNITS  $BASE/d6rf3_units_assert.py"
  echo "$MD5_ANCHOR_GATE  $BASE/d6rf3_anchor_gate.py"
  echo "$MD5_RUNSCRIPT6  $BASE/d6rf3_opt_runScript.py"
  echo "$MD5_FD  $BASE/d6rf3_fd_endpoint.py"
  echo "$MD5_REFOFF  $BASE/d6rf3_ref_off.py"; } | md5sum -c - || { echo "ABORT staged instrument md5"; exit 4; }
test -f "$BASE/base/FFD/wingFFD.xyz" || { echo "ABORT staged base/ has no FFD/wingFFD.xyz"; exit 4; }

if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."; exit 3
  fi
fi
echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"; echo "chain_done stamp=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ arms=[$ARMS] last=[$(tail -n 1 "$STATUS" 2>/dev/null)] permission=$PERMISSION" >> "$BASE/CHAIN_DONE"' EXIT
echo "D6RF3_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] permission=$PERMISSION"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) permission=$PERMISSION" >> "$STATUS"

mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
cap_mem_gib() { echo 20; }   # both D6RF arms 20g (section 4g); never 8g
arm_cap() { case "$1" in F_mp) echo 480.0 ;; REF_off) echo 190.0 ;; *) echo "" ;; esac; }
# ---- THE CUMULATIVE ITEM-CEILING GUARD -------------------------------------
# `d6rf_chain_driver.sh`'s guard -- which this file's parent inherited -- FAILS
# OPEN TWO WAYS, both measured:
#   (1) `except IOError: pass` then `print('%.3f' % tot)`, so an ABSENT or
#       UNREADABLE ledger returns `0.000`, INDISTINGUISHABLE from a ledger that
#       exists and records nothing spent. A planted zero inside the guard's own
#       input (CLAUDE.md rule 3).
#   (2) its regex `\bcore_min=([0-9.]+)` puts a LITERAL dot in a character
#       class, so `core_min=1.2.3` is captured WHOLE and `float()` raises
#       ValueError -- uncaught -- so `$SPENT` comes back EMPTY and
#       `print('%.3f' % ( $SPENT + $ACAP ))` becomes Python's UNARY PLUS on the
#       cap. The projection prints a clean `480.000` and THE GUARD PASSES WITH
#       THE PRIOR SPEND SILENTLY DROPPED.
# NEITHER IS RE-IMPLEMENTED AND NEITHER IS PORTED. This item calls the one
# known-good implementation, `cases/dafoam/_common/item_ceiling_guard.py`:
# 31 driven limbs, `UNMEASURED` primary and REFUSING (absent, unreadable and
# unparseable are ONE state, never `0.0`), the token captured and validated
# WHOLE with `\S+` so a partial sum can never stand in for a total, spend
# re-read from disk on every call, and NO NUMBER EVER REACHING A SHELL
# ARITHMETIC CONTEXT -- the guard answers on its EXIT CODE, not on a string
# this script interpolates.
CEILING_GUARD="$HERE/../../../_common/item_ceiling_guard.py"
test -f "$CEILING_GUARD" || { echo "ABORT item ceiling guard absent: $CEILING_GUARD"; exit 4; }
echo "$MD5_CEILING_GUARD  $CEILING_GUARD" | md5sum -c - || { echo "ABORT item ceiling guard md5"; exit 4; }

for ARM in $ARMS; do
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before arm $ARM"; echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 4; }
  echo "preflight arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ permission=$PERMISSION" > "$BASE/STATUS.$ARM"
  if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT ALREADY_BOUGHT arm $ARM has an rc=0 ledger row; a second record for one run is the defect."
    echo "rc=3 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=ALREADY_BOUGHT permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=REFUSED_ALREADY_BOUGHT arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 3
  fi

  # ---- CUMULATIVE SPEND ASSERTED AGAINST THE ITEM CEILING, BEFORE EVERY ARM.
  # An overrun STOPS the run; it does not get a new budget (CLAUDE.md rule 12).
  # The check is cumulative because a per-arm cap alone cannot see an item
  # walking past its own ceiling one arm at a time.
  ACAP=$(arm_cap "$ARM")
  test -n "$ACAP" || { echo "ABORT no registered cap for arm $ARM"; exit 64; }
  # The guard answers on its EXIT CODE. `$SPENT` no longer exists in this
  # script and no spend figure is interpolated into any arithmetic context,
  # which is what closed fail-open (2) above. UNMEASURED refuses like a breach.
  if ! python3 "$CEILING_GUARD" --check \
        --ledger "$BASE/ledger.txt" --cap "$ACAP" \
        --ceiling "$ITEM_CEILING_CORE_MIN" --label "D6RF3/$ARM"; then
    echo "ABORT ITEM CEILING or UNMEASURED SPEND for arm $ARM."
    echo "  An overrun stops the run; it does not get a new budget (rule 12),"
    echo "  and an unreadable ledger is UNMEASURED, which refuses like a breach."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=ITEM_CEILING cap=$ACAP ceiling=$ITEM_CEILING_CORE_MIN permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=ABORT arm=$ARM reason=ITEM_CEILING cap=$ACAP ceiling=$ITEM_CEILING_CORE_MIN stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    exit 6
  fi

  # ---- H5: a WINDOW of MemAvailable, every sample above the floor, in the
  # ---- WAIT-AND-RETRY form.  IT HOLDS; IT DOES NOT REFUSE.
  H5_WAITED=0
  while true; do
    H5_FILE="$BASE/${ARM}_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"; BELOW=0; N=0; MIN=999; MAX=0
    STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))")
    for _ in $(seq 1 $H5_SAMPLES); do
      s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"
      MIN=$(python3 -c "print(min($MIN,$s))"); MAX=$(python3 -c "print(max($MAX,$s))")
      [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1))
      sleep "$STEP"
    done
    echo "D6RF3_H5_WINDOW arm=$ARM n=$N window_s=$H5_WINDOW_S floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAX samples_below_floor=$BELOW waited_s=$H5_WAITED file=$(basename "$H5_FILE")"
    if [ "$BELOW" -eq 0 ] && [ "$N" -eq "$H5_SAMPLES" ]; then break; fi
    if [ "$H5_WAITED" -ge "$H5_BOUND_S" ]; then
      echo "HELD H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB after ${H5_WAITED}s of HOLDING.  BLOCKED at the bound -- RE-FIREABLE, zero compute spent."
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_BLOCKED_AT_BOUND waited=$H5_WAITED below=$BELOW min_GiB=$MIN permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_H5 arm=$ARM waited=$H5_WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 6
    fi
    echo "H5_HOLD waited=$H5_WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM below=$BELOW of=$N min_GiB=$MIN floor_GiB=$H5_FLOOR_GIB note=holding_not_refusing" >> "$BASE/STATUS.$ARM"
    sleep "$H5_RETRY_S"; H5_WAITED=$((H5_WAITED+H5_RETRY_S+H5_WINDOW_S))
  done

  # ---- AGGREGATE: the same shape, and the same rule -- HOLD, never refuse.
  WAITED=0; AGG_SERIES="$BASE/${ARM}_aggregate_series.txt"
  while true; do
    AGG=$(python3 "$AGGREGATE_READER" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
    echo "$(date -u +%s) $AGG" >> "$AGG_SERIES"
    if [ "$(printf '%s' "$AGG" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ]; then break; fi
    if [ "$WAITED" -ge "$AGG_BOUND_S" ]; then
      echo "HELD AGGREGATE still over $AGG_CEILING_GIB GiB after ${WAITED}s of HOLDING.  BLOCKED at the bound -- RE-FIREABLE, zero compute spent.  Series: $(basename "$AGG_SERIES")"
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=AGGREGATE_BLOCKED_AT_BOUND waited=$WAITED series=$(basename "$AGG_SERIES") permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_AGGREGATE arm=$ARM waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 6
    fi
    echo "AGGREGATE_HOLD waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM $AGG note=holding_not_refusing" >> "$BASE/STATUS.$ARM"
    sleep "$AGG_POLL_S"; WAITED=$((WAITED+AGG_POLL_S))
  done
  echo "D6RF3_AGGREGATE arm=$ARM waited=$WAITED $AGG"

  echo "D6RF3_DRIVER arm=$ARM begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID permission=$PERMISSION"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "D6RF3_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN aggregate_waited_s=$WAITED h5_waited_s=$H5_WAITED spent_before_arm=SEE_ITEM_CEILING_GUARD_LINE permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" = "77" ]; then
    echo "D6RF3_UNITS_REFUSAL arm=$ARM rc=77 -- the design vector could not prove it was PHYSICAL and in bounds; THE MESH WAS NEVER TOUCHED.  This is a REGISTERED outcome, not an infrastructure failure." >> "$BASE/STATUS.$ARM"
  fi
  if [ "$rc" -ne 0 ]; then
    # The stop line NAMES the registered arm order and the arms that will NOT
    # run, so the grader reads the census from the driver's own record instead
    # of inferring it (D6R repair 1/3, carried forward).
    NOTRUN=""; seen=0
    for a in $ARMS; do
      if [ "$seen" = "1" ]; then NOTRUN="$NOTRUN $a"; fi
      if [ "$a" = "$ARM" ]; then seen=1; fi
    done
    echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc order=[$ARMS] not_run=[${NOTRUN# }] stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    exit "$rc"
  fi
done
# ---- THE FINAL SPEND, READ THROUGH THE SAME GUARD --------------------------
# `spent_core_min()` was REMOVED with the fail-open reader above and this call
# site was left pointing at it -- an undefined function, so `FINAL_SPEND` came
# back EMPTY and this line wrote `total_core_min=` INTO THE LEDGER, which reads
# to a human as ZERO SPEND RECORDED. It fired ONLY on `chain=COMPLETE`: the
# success path, the one least likely to be examined and the one whose figure
# gets quoted into a cost calibration. `bash -n` cannot see it -- an undefined
# function is a RUNTIME failure, so a syntax check certifies the file and
# misses this entirely, the same family as `assert` vanishing under `python -O`.
#
# NO LOCAL SPEND READER IS RE-INTRODUCED. The figure comes from the one
# known-good guard. `--cap 0` makes the projection equal the spend itself, so
# this is a REPORT and not a second admission test: a chain that completed
# cannot be refused by its own closing line.
FINAL_LINE=$(python3 "$CEILING_GUARD" --check --ledger "$BASE/ledger.txt" \
             --cap 0 --ceiling "$ITEM_CEILING_CORE_MIN" --label "D6RF3/FINAL" 2>&1 | head -1)
FINAL_SPEND=$(printf '%s' "$FINAL_LINE" | grep -oE 'spent_core_min=[^ ]+' | cut -d= -f2)
# THE FIELD IS NEVER EMPTY. An unreadable ledger yields the guard's own
# `UNMEASURED`; anything else that could empty this yields it too. An empty
# field is the thing to catch -- a wrong number would at least look wrong.
[ -n "$FINAL_SPEND" ] || FINAL_SPEND=UNMEASURED
echo "D6RF3_SPEND_FINAL total_core_min=$FINAL_SPEND item_ceiling=$ITEM_CEILING_CORE_MIN" | tee -a "$BASE/ledger.txt"
echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
exit 0
