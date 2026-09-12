#!/usr/bin/env bash
# =============================================================================
# PERMISSION: FROZEN by the dafoam-supervisor 2026-09-11.  ONE FREEZE PLACEHOLDER REMAINS BY
# DESIGN -- LAUNCH_BUDGET_S, which is MEASURED by the first arm's D4S_MPIRUN_EPOCH line
# and is never guessed -- so G-FREEZE.0 still refuses until that measurement is in.
# The file is FROZEN; it is deliberately NOT YET RUNNABLE, and those are different things.
#
# Curriculum D8G arm launcher -- A6 CRM WING-ALONE, a THREE-LEVEL GRID triple at
# r = 2 exactly on TWO TOOLCHAIN ROWS, with the adjoint and the FD table at L2.
#
# DERIVED FROM cases/dafoam/ladder-a/A6/curriculum_D8R/d8r_run_arm.sh -- A FROZEN
# INSTRUMENT BEHIND A GRADED TWO-ROW PASS, WHICH THIS FILE DOES NOT EDIT.  The
# deltas are recorded in d8g_run_arm_DELTAS_from_d8r.diff.  INHERITED UNCHANGED
# in substance: D4-LAUNCHER-DEF-1 and its G-ROOT.1/.2/.3 guards, G-ROOT.5, the
# cap assertion by inverted arithmetic, the host pre-read, the staged-instrument
# md5 check, the image-digest and G-ROW checks, the cold-start G-COLD sweep and
# the age datum, the in-container `timeout` deadline, the CPU sampler, the
# runaway guard, the kernel-verdict read before `docker rm`, and the ledger row.
# The container-printed strings (D4S_*) are inherited UNCHANGED so the grader
# greps what the launcher writes.
#
# THE ONE BEHAVIOURAL DELTA, AND ITS PLUMBING -- THE LAUNCH ASSERTION (LA.*):
#   "LAUNCHED" IS ASSERTED FROM THE SOLVER'S OWN FIRST ARTIFACT, NEVER FROM THE
#   LAUNCH COMMAND RETURNING AND NEVER FROM CONTAINER STATE ALONE.
#
# WHY -- three separate findings, all measured:
#  (1) cfd's scripts/case_protocol_stage4_run.py reported LAUNCHED on a Popen
#      return alone while the solver had already aborted; a manifest said
#      `launched: true` with no solve behind it.
#  (2) EVERY ONE of the 58 `cases/dafoam/**/*_run_arm.sh` launchers -- D8R and
#      the whole D6RF family included -- asserts CONTAINER STATE ONLY.  Each
#      polls `docker inspect --format '{{.State.Running}}'` and reads
#      `docker logs` ONLY AFTER that loop has already broken.  Not one of them
#      reads a solver artifact while the container is alive.
#  (3) THE OBVIOUS WITNESS IS A FALSE ONE.  `^Time = ` DOES NOT PROVE THE SOLVER
#      STARTED.  Measured on the D8R producer's own graded arm log
#        /home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/O-P_20260827T223101Z_1595223.log
#      `decomposePar` PRINTS `Time = 0` at line 142, 19 lines BEFORE its own
#      `End` at line 161 and 583 lines before the solver's first completed step.
#      Counted over the whole file: `^Time = ` occurs 1617 times,
#      `^ExecutionTime` 1616 -- the difference is exactly decomposePar's line.
#
# BINDING SCOPE (verification team, relayed by dafoam-supervisor):
#   "a launch is asserted only from the solver/container process's own liveness
#    or from a first artifact it produced (first log line, a time-dir or 0/
#    field mtime advancing past staging); a launch command returning is not a
#    witness; otherwise `launched: false` with a reason.  Wrapper stderr is
#    never discarded."
#
# THE BYTES BETWEEN `# >>> D8G_LAUNCH_ASSERT_BEGIN` AND `# <<< D8G_LAUNCH_ASSERT_END`
# ARE BYTE-IDENTICAL TO THOSE IN THE LAUNCHER THIS FILE SUPERSEDED, now
# d8g_run_arm.sh.SUPERSEDED-20260910T2141Z.DRAFT, WHICH THE dafoam-supervisor EXECUTED
# THROUGH d8g_launch_assert_selftest.sh (41 pass / 0 fail; the mutation control 31 pass /
# 10 fail).  THEY ARE NOT RE-AUTHORED HERE.
# RE-VERIFIED 2026-09-11, AT THE FREEZE RENAME, BECAUSE THE CLAIM CITED A FILENAME THAT HAD
# MOVED: both blocks are 9,481 bytes and hash to 7f73817a294c07e65b0ee0a3ab00ea75.  The
# claim was true; only its citation was stale.  (The first attempt at that comparison
# matched a PROSE MENTION of the marker instead of the marker itself -- the string occurs
# twice in this file -- and returned a confident, wrong `not identical`.  A reader that
# matches the wrong occurrence gives a wrong answer with no sign that it is wrong.)
# AND THE SELFTEST NOW TARGETS THIS FILE: until the rename it read `d8g_run_arm.sh.DRAFT`,
# which was the SUPERSEDED 444-line launcher, so its green was about the wrong file.
#
# 8.2 inherited from D8R: NO --rm, so `docker inspect .State.ExitCode/
# .State.OOMKilled` survives the arm and the KERNEL's verdict is read.
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call and
# `( set -e; ... )` does not gate either.  Every step below gates explicitly
# with `|| { echo ABORT...; exit N; }`.
# =============================================================================
set -uo pipefail

# ===========================================================================
# G-FREEZE.0 -- A DRAFT MUST NOT BE RUNNABLE BY ACCIDENT.
# Every constant D8G's PREREGISTRATION.md must fix that this lane COULD NOT
# MEASURE is written as a placeholder token, and this guard greps THIS FILE for
# it and REFUSES while ANY remains.  It is the first executable statement so no
# placeholder can reach a container.
#
# THE PATTERN IS ASSEMBLED FROM TWO HALVES, AND THAT IS DELIBERATE: written out
# whole, this guard's OWN source lines would match it, so the count could never
# reach zero and "more than N" would be the only rule expressible.  Assembled,
# the count is EXACTLY the number of real placeholders and the rule is the
# honest one: zero.
#
# AND THE PATTERN IS PLANTED BEFORE IT IS TRUSTED.  A grep that matches nothing
# and reports success is the planted zero this lab keeps paying for, so the
# guard first feeds itself a string that DOES carry the token and refuses if it
# cannot see it.  Only then is a zero from the real file evidence of anything.
# ===========================================================================
FREEZE_TOK='__D8G_'"UNFROZEN__"
printf '%s\n' "SELFCHECK${FREEZE_TOK}SENTINEL" | grep -q "$FREEZE_TOK" || {
  echo "ABORT G-FREEZE.0 the freeze-token pattern cannot see a PLANTED token."
  echo "  A reader not shown able to see a non-zero is not evidence (rule 3),"
  echo "  so its zero on the real file proves nothing.  REFUSED."
  exit 3; }
UNFROZEN_TOKENS=$(grep -c "$FREEZE_TOK" "${BASH_SOURCE[0]}" || true)
if [ "${UNFROZEN_TOKENS:-0}" -gt 0 ]; then
  echo "ABORT G-FREEZE.0 this file still carries $UNFROZEN_TOKENS unfrozen placeholder line(s):"
  grep -n "$FREEZE_TOK" "${BASH_SOURCE[0]}" | sed 's/^/    /'
  echo "  ONE PLACEHOLDER REMAINS BY DESIGN, AND IT IS NOT GUESSABLE FROM ANY DESK:"
  echo "   * WITNESS_BUDGET  -- the per-arm launch-witness deadline.  It must be SIZED"
  echo "     PER LEVEL from a measurement (D8R reached decomposePar 15 s after StartedAt"
  echo "     at 41,760 cells; D8G's L3 is 8.5x that mesh).  A guessed budget either"
  echo "     declares a slow-starting arm wedged or waits so long it stops bounding"
  echo "     anything.  IT IS LEFT AS A TOKEN DELIBERATELY."
  echo "  INSTRUMENT_MD5S WAS FILLED AT THE FREEZE, 2026-09-11, and is no longer owed."
  echo "  A launcher that ran on placeholders would produce a row no pre-registration"
  echo "  covers.  REFUSED."
  exit 3
fi

ITEM=D8G
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple
BASE="${BASE:-$REGISTERED_BASE}"
PREFIX=d8g

# ---- G-ROOT.1 -- BASE must be THIS item's registered root, normalised, so a
# ---- trailing slash, a `.`, a `..` or a symlink cannot walk around the check.
BASE_REAL=$(realpath -m "$BASE")
REG_REAL=$(realpath -m "$REGISTERED_BASE")
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
  echo "  given:      $BASE_REAL"
  echo "  registered: $REG_REAL"
  echo "  D4-LAUNCHER-DEF-1: a launcher pointed at another item's run root"
  echo "  deletes that item's graded arms.  REFUSED before any staging."
  exit 3
fi

# ---- G-ROOT.2 -- and NAME the roots that must never be written by this file.
# ---- D8G REGISTERED DELTA: CURRICULUM-D8R-a6-twist-opt-conv IS ADDED AT THE
# ---- HEAD OF THE LIST.  D8G inherits D8R's producer and its instruments are
# ---- named d8g_* precisely so nothing here can land in the directory holding
# ---- the graded two-row PASS this item is built on.
FORBIDDEN_ROOTS="/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv
/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-R-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density
/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D14-a2-wing-remesh
/home/ubuntu/certonomous-runs/CURRICULUM-D14M-a2-wing-remesh
/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd
/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D13-a1-basin-restart
/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic
/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic
/home/ubuntu/certonomous-runs/CURRICULUM-D17-cone-supersonic
/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt
/home/ubuntu/certonomous-runs/A6-crm-wing
/home/ubuntu/certonomous-runs/P2-a6-n16
/home/ubuntu/certonomous-runs/P3-a6-n16-ref
/home/ubuntu/certonomous-runs/P3-a6-n16-rem
/home/ubuntu/certonomous-runs/A2-mach-wing
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/transonic
/home/ubuntu/dafoam-tutorials
/home/ubuntu/certonomous-runs
/home/ubuntu/Certonomous"
while IFS= read -r forb; do
  [ -z "$forb" ] && continue
  if [ "$BASE_REAL" = "$(realpath -m "$forb")" ]; then
    echo "ABORT G-ROOT.2 BASE resolves to ANOTHER ITEM'S RUN ROOT: $forb"
    echo "  That directory holds a graded row.  This launcher stages by removing"
    echo "  the arm directory, so writing there would destroy it.  REFUSED."
    exit 3
  fi
done <<< "$FORBIDDEN_ROOTS"

# ---- G-ROOT.3 -- the LEDGER must belong to this item and to no other.  D8G
# ---- BUYS BOTH ROWS, so a ROW=SHIPPED row is NOT foreign here; only a foreign
# ---- ITEM= line refuses.
if [ -f "$BASE/ledger.txt" ]; then
  FOREIGN_ITEM=$(grep -a "^ITEM=" "$BASE/ledger.txt" 2>/dev/null | grep -av "^ITEM=$ITEM$" | head -1)
  if [ -n "$FOREIGN_ITEM" ]; then
    echo "ABORT G-ROOT.3 the ledger at $BASE/ledger.txt carries another item: $FOREIGN_ITEM"
    echo "  Appending here would interleave two items' rows in one file and"
    echo "  neither row could be graded cleanly afterwards.  REFUSED."
    exit 3
  fi
fi
echo "D4S_G_ROOT_PASS item=$ITEM base=$BASE_REAL ledger_clean=yes"

# ---- REGISTERED CPU PLACEMENT ---------------------------------------------
# `mpirun` inside a `--cpus=N` container binds rank 0 to the FIRST CORE OF THE
# HOST TOPOLOGY.  Concurrent containers then land on the same host core and
# throughput collapses as 1/N while the box reports itself idle.  `--cpus=4`
# does NOT hand out four distinct cores.  So: PIN, and MEASURE the placement.
#
# DISCLOSED, BECAUSE IT IS NOT A MEASUREMENT THIS LANE MADE: PREREGISTRATION.md
# section 3 registers "cpuset assigned by the launcher" and NO SPECIFIC SET.
# The value below is INHERITED FROM THE D8R PRODUCER (d8r_run_arm.sh:141).  THE
# SUPERVISOR MUST REGISTER IT AT THE FREEZE; d8g_grade.py asserts every arm
# carries it AND that it is the SAME on every arm (a family whose placement
# changes between levels is not a family).
CPUSET=0,1,12,15

# For containerised MPI the conditioning variable is CONCURRENT CONTAINERS, not
# loadavg -- `uptime` will lie.  Censused before and after every arm.
container_census() {
  docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d8g_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED CAP TABLE.  EVERY NUMBER IS DERIVED IN PLACE FROM
# ---- PREREGISTRATION.md section 6.3, SO NO CAP IS INVENTED:
# ----   cap = 3 x the section 6.3 per-arm point estimate (CASE_PROTOCOL section 1)
# ----   L1 primal 15.659 -> 46.977   L2 primal 17.472 -> 52.416
# ----   L3 primal 31.974 -> 95.922   L2 adjoint 40.652 -> 121.956
# ----   L2 FD (patched) 67.840 -> 203.520   L2 FD (shipped) 71.395 -> 214.185
# ----   sum = 1,052.247 core-min, inside section 6.4's registered 1,079.25 cap.
# ---- MEMORY comes from section 5's envelope table, per arm.
# ---- THE CAP IS CALIBRATION, NOT A STOP (section 6.4, Sanaa 2026-09-10): the
# ---- in-container `timeout` is CONTAINMENT, the ledger records a crossing, and
# ---- d8g_grade.py's G10 is REPORT-ONLY.  A rc = 124 is an over-wall event and
# ---- is NOT A RESULT on that arm.
cap_core_min() {
  case "$1" in
    L1-P|L1-S) echo 46.977 ;;
    L2-P|L2-S) echo 52.416 ;;
    L3-P|L3-S) echo 95.922 ;;
    A2-P|A2-S) echo 121.956 ;;
    F2-P)      echo 203.520 ;;
    F2-S)      echo 214.185 ;;
    *) echo "" ;;
  esac
}
cap_memory() {
  case "$1" in
    L1-P|L1-S|L2-P|L2-S) echo 6g ;;    # section 5: ~0.09 and ~0.70 GiB predicted
    L3-P|L3-S)           echo 12g ;;   # section 5: ~5.62 GiB predicted (a MODEL, not a measurement)
    A2-P|A2-S)           echo 14g ;;   # section 5: ~10.5 GiB predicted, M2 de-biased
    F2-P|F2-S)           echo 6g ;;    # primals only, D8R's F-arm envelope
    *) echo "" ;;
  esac
}
ranks_of() {
  case "$1" in
    L1-P|L2-P|L3-P|A2-P|F2-P|L1-S|L2-S|L3-S|A2-S|F2-S) echo 4 ;;   # section 3: every arm np = 4, scotch
    *) echo "" ;;
  esac
}
level_of() {
  case "$1" in
    L1-*) echo L1 ;; L2-*) echo L2 ;; L3-*) echo L3 ;;
    A2-*|F2-*) echo L2 ;;                         # section 4.7: the adjoint and the FD table are at L2
    *) echo "" ;;
  esac
}
mode_of() {
  case "$1" in
    L1-*|L2-*|L3-*) echo P ;; A2-*) echo A ;; F2-*) echo F ;;
    *) echo "" ;;
  esac
}

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER section 11)
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc

# ---- FROZEN INSTRUMENT HASHES.  STILL A TOKEN, AND HERE IS WHY: d8g_of.py,
# ---- d8g_runScript.py and d8g_decomposeParDict DO NOT EXIST YET.  A launcher
# ---- cannot assert the hash of a file nobody has written, and writing a
# ---- plausible-looking hash here would be the exact defect the check exists to
# ---- catch.  At the freeze the supervisor replaces the token with three
# ---- `<md5>  <path>` lines; the check below asserts THREE `OK` lines came back,
# ---- so a manifest that silently loses a row cannot pass.
# FILLED AT THE FREEZE, 2026-09-11.  Three `<md5>  <path>` lines; the check below asserts
# THREE `OK` lines came back, so a manifest that silently loses a row cannot pass.  @BASE@ is
# substituted with the run root.  TAKEN AFTER THE RENAME AND THE PERMISSION FLIP, because a
# hash taken before every byte that will ever change has changed names a file that no longer
# exists in that form.
INSTRUMENT_MD5S="28c7819487a025a5f6554d38062a2b66  @BASE@/d8g_runScript.py\nf17b4a26fc5dcbbb44e9c820ba16df6c  @BASE@/d8g_of.py\n1dbd9ead3f40a29f483444dc5fa1288b  @BASE@/d8g_decomposeParDict"

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: d8g_run_arm.sh <L1-P|L2-P|L3-P|A2-P|F2-P|L1-S|L2-S|L3-S|A2-S|F2-S> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: d8g_run_arm.sh <arm> <image>"; exit 64; }
RANKS=$(ranks_of "$ARM"); test -n "$RANKS" || { echo "ABORT arm $ARM carries no registered rank count"; exit 64; }
LEVEL=$(level_of "$ARM"); test -n "$LEVEL" || { echo "ABORT arm $ARM carries no registered level"; exit 64; }
MODE=$(mode_of "$ARM");  test -n "$MODE"  || { echo "ABORT arm $ARM carries no registered mode"; exit 64; }

# ---- G-ROOT.5 -- A LIVE ARM IS NEVER RE-STAGED.  G-ROOT.1-.3 see only ledger
# ---- rows; a queue-runner re-firing this launcher on a RUNNING arm would pass
# ---- them and reach `rm -rf "$WORK"`.  Two live readings, taken BEFORE any
# ---- destructive act: (a) a RUNNING container carrying this item's prefix and
# ---- this arm; (b) a driver pidfile naming a LIVE pid that is not an ancestor
# ---- of this process, or whose cwd is the run root.  A stale pidfile does not
# ---- block.
LIVE_SAME_ARM=$(docker ps --format '{{.Names}}' --filter "name=^d8g_${ARM}_" 2>/dev/null | grep "^d8g_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  echo "  Re-staging would remove the live arm directory under it.  REFUSED."
  exit 3
fi
PIDFILE="$BASE/d8g_driver.pid"
if [ -f "$PIDFILE" ]; then
  DPID=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$DPID" ] && kill -0 "$DPID" 2>/dev/null; then
    ANCESTOR=no; p=$$
    for _ in $(seq 1 64); do
      if [ "$p" = "$DPID" ]; then ANCESTOR=yes; break; fi
      p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
      if [ -z "$p" ] || [ "$p" = "0" ]; then break; fi
    done
    DCWD=$(readlink -f "/proc/$DPID/cwd" 2>/dev/null)
    if [ "$ANCESTOR" = "no" ] || [ "$DCWD" = "$(realpath -m "$BASE")" ]; then
      echo "ABORT G-ROOT.5 driver pidfile $PIDFILE names LIVE pid $DPID (ancestor_of_this_launcher=$ANCESTOR cwd=$DCWD)."
      echo "  Another driver owns this run root, or a process sits inside it.  REFUSED."
      exit 3
    fi
  fi
fi
echo "D4S_G_ROOT5_PASS arm=$ARM live_same_arm_containers=none driver_pidfile=$([ -f "$PIDFILE" ] && echo present_owner_is_ancestor_or_stale || echo absent)"

CAP=$(cap_core_min "$ARM")
MEM=$(cap_memory "$ARM")
test -n "$CAP" || { echo "ABORT unknown arm $ARM -- no registered cap"; exit 64; }
test -n "$MEM" || { echo "ABORT unknown arm $ARM -- no registered memory cap"; exit 64; }

# THE ASSERTION.  The enforced wall timeout is DERIVED from the registered
# core-minute cap and the registered rank count, and is then re-checked against
# that cap by inverting the arithmetic.  There is no second number anywhere in
# this file that could drift from the first.
TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)))") || { echo "ABORT tmo calc"; exit 65; }
# *** THE INVERSION IS AGAINST THE UNROUNDED DERIVATION.  MEASURED 2026-09-11
# 23:08:15Z, the first real launch attempt of this item: L1-P ABORTED with
#   "ABORT CAP MISMATCH registered=46.977 enforced=47.0"
# on a cap that is perfectly correct.  TMO is rounded to an INTEGER SECOND, and
# the old back-check reconstructed the cap FROM THAT ROUNDED INTEGER and
# compared it to the registered cap at a 0.02 core-min tolerance.  Rounding is
# worth up to 0.5 s, which at 4 ranks is 0.5*4/60 = 0.0333 core-min -- LARGER
# THAN THE TOLERANCE THE SAME CODE ENFORCED.  So the guard could refuse a
# correct cap, and WHICH arms it refused was decided by nothing but where
# cap*60/RANKS fell relative to a half-second.  MEASURED across the ten
# registered arms, four died: L1-P, L1-S (err 0.0230) and A2-P, A2-S (0.0227).
#
# WHY THE FREEZE DID NOT CATCH IT: this assertion was inherited "unchanged in
# substance" from d8r_run_arm.sh, a frozen instrument behind a graded two-row
# pass.  D8R's caps are 1000.0 and 120.0, which divide to EXACT integer seconds
# (15000 and 1800), so its back-check error is IDENTICALLY ZERO and the
# assertion COULD NEVER FIRE THERE.  It rode a whole graded campaign without
# once being executed against a case able to fail it.  A GUARD INHERITED FROM A
# PASSING INSTRUMENT IS NOT A GUARD THAT HAS BEEN SHOWN TO WORK.
#
# THE REPAIR, AND WHAT IT IS NOT.  The tolerance is NOT widened -- widening it
# would weaken a real guard to hide an arithmetic artifact.  The caps are NOT
# touched; they are registered numbers.  The comparison is moved onto the
# quantity the code actually derived: the UNROUNDED wall cap*60/RANKS, in
# SECONDS, and the admitted difference is EXACTLY the rounding quantum of 0.5 s
# and nothing more.  That is the tightest bound that can admit a correct
# rounding, so the guard is not loosened -- it is pointed at the right number.
# A genuinely mismatched wall is still refused: the planted control shows a
# hard-coded TMO of 700 s against L1-P's exact 704.655 s aborting on a 4.655 s
# drift.  This repairs an implementation that failed to test what it claimed to
# test; it changes no gate, cap, band or label.
EXACT_WALL=$(python3 -c "print('%.6f' % ($CAP*60.0/$RANKS))") || { echo "ABORT exact wall calc"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % ($TMO*$RANKS/60.0))") || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
tmo, exact, cap, back = $TMO, $EXACT_WALL, $CAP, $BACKCHECK
QUANTUM = 0.5   # one rounding of int(round()), in seconds.  Not a fudge factor:
                # it is the exact width of the operation performed above.
drift = abs(tmo - exact)
if drift > QUANTUM + 1e-9:
    sys.stderr.write('ABORT CAP MISMATCH registered_cap=%r exact_wall_s=%r enforced_wall_s=%r drift_s=%r exceeds rounding quantum %r (enforced_core_min=%r)\n'
                     % (cap, exact, tmo, drift, QUANTUM, back)); sys.exit(1)
" || { echo "ABORT enforced wall != wall derived from registered cap"; exit 65; }
echo "D4_CAP_ASSERT arm=$ARM level=$LEVEL mode=$MODE registered_core_min=$CAP ranks=$RANKS exact_wall_s=$EXACT_WALL enforced_wall_s=$TMO drift_s=$(python3 -c "print('%.6f' % abs($TMO-$EXACT_WALL))") enforced_core_min=$BACKCHECK memory=$MEM"

# ---- host state, read before ranks are claimed ---------------------------
MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D4_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 run root mode $(stat -c '%a' "$BASE")"; exit 4; }

# ---- staged-instrument identity, re-asserted before EVERY launch ---------
# THE COUNT IS ASSERTED, NOT JUST THE EXIT CODE: `md5sum -c` on an EMPTY list
# exits 0, which would be a passing check that checked nothing.
MD5_OUT=$(printf '%b\n' "$INSTRUMENT_MD5S" | sed "s#@BASE@#$BASE#g" | md5sum -c - 2>&1) \
  || { echo "ABORT staged-instrument md5: $MD5_OUT"; exit 4; }
MD5_OK=$(printf '%s\n' "$MD5_OUT" | grep -c ': OK$')
test "$MD5_OK" -eq 3 || { echo "ABORT staged-instrument md5 manifest returned $MD5_OK OK lines, not 3: $MD5_OUT"; exit 4; }
echo "D4S_INSTRUMENT_MD5_PASS arm=$ARM checked=3"

# ---- image identity by DIGEST, resolved from the local store -------------
GOT_DIGEST=$(docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1)       WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  dafoam/opt-packages:latest) WANT=$IMG_SHIPPED_DIGEST; ROW=SHIPPED ;;
  *) echo "ABORT image $IMG is not a registered row"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }

# ---- G-ROW.  THE ROW A RUN CLAIMS AND THE ROW IT RAN MUST BE THE SAME HASH.
case "$ARM" in
  *-S) WANT_ROW=SHIPPED ;;
  *-P) WANT_ROW=PATCHED ;;
  *)   WANT_ROW="" ;;
esac
test "$ROW" = "$WANT_ROW" || {
  echo "ABORT G-ROW arm $ARM is registered on the $WANT_ROW row; got ROW=$ROW ($IMG)."
  echo "  A row a run claims and a row it ran must be the same hash.  REFUSED."
  exit 4; }
echo "D4S_G_ROW_PASS row=$ROW digest=$GOT_DIGEST"
echo "D4_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d8g_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- stage a pristine copy for the arm ------------------------------------
# D8G REGISTERED DELTA: there is no ONE base/.  THE MESH IS PER LEVEL, and each
# arm stages a COLD copy of THIS LEVEL'S base_<LEVEL>/, written by
# d8g_genmesh.sh into this same run root together with mesh_record_<LEVEL>.json.
# THE MESH IDENTITY IS ASSERTED AGAINST THAT RECORD, NOT AGAINST A LITERAL IN
# THIS FILE: the meshes have not been generated, so a literal here would be a
# guess, and d8g_grade.py's G-M2 re-asserts the same equality independently
# while G-MESH gates the record's own contents against the registered cell
# counts, patch faces and dimensionality.
LBASE="$BASE/base_$LEVEL"
MREC="$BASE/mesh_record_$LEVEL.json"
test -d "$LBASE" || { echo "ABORT arm $ARM expects a staged $LBASE (d8g_genmesh.sh writes it)"; exit 5; }
test -f "$MREC"  || { echo "ABORT arm $ARM expects $MREC (the level's construction record)"; exit 5; }
test -f "$LBASE/constant/polyMesh/points.gz" || { echo "ABORT $LBASE carries no constant/polyMesh/points.gz"; exit 5; }
test -f "$LBASE/0/U" || { echo "ABORT $LBASE carries no 0/U"; exit 5; }
REC_MD5=$(python3 -c "import json,sys; print(json.load(open('$MREC'))['points_md5'])") \
  || { echo "ABORT cannot read points_md5 from $MREC"; exit 5; }
echo "$REC_MD5  $LBASE/constant/polyMesh/points.gz" | md5sum -c - \
  || { echo "ABORT level mesh md5 does not match $MREC (G-M2 at staging)"; exit 4; }
REC_CELLS=$(python3 -c "import json; print(json.load(open('$MREC'))['cells'])")
echo "D8G_LEVEL_MESH_OK arm=$ARM level=$LEVEL cells=$REC_CELLS points_md5=$REC_MD5 record=$(basename "$MREC")"

# An F arm additionally needs the SAME ROW's L2 adjoint artefact; it REFUSES
# without it, and the ledger must already carry that arm at rc = 0.
case "$ARM" in
  F2-*) AARM="A2-${ARM#F2-}"
        test -f "$BASE/$AARM/d8g_A.json" || { echo "ABORT arm $ARM expects $AARM/d8g_A.json (the same row's L2 adjoint)"; exit 5; }
        grep -aq "^ARM=$AARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null || { echo "ABORT arm $ARM: $AARM has no rc=0 ledger row"; exit 5; } ;;
esac
# D8G-R3-EVIDENCE  2026-09-12.  THIS LINE WAS `sudo -n rm -rf "$WORK" 2>/dev/null`.
# IT DELETED THE ARM'S PREVIOUS RUN TREE, AS ROOT, SILENTLY, AT EVERY LAUNCH.
#
# WORK="$BASE/$ARM" (:415), so a re-launch against the same BASE destroyed the completed
# arm -- logs, processor trees, d8g_P.json, the ledger datum -- and `2>/dev/null` meant
# it never said so.  CLAUDE.md rule 4: a guard REFUSES a case whose run directory exists.
# A failed or stopped run root is EVIDENCE, never written into and still less removed.
# `sudo` was here only because the container ran as root and left root-owned output the
# host could not delete -- THIS LINE EXISTED TO CLEAN UP AFTER THE DEFECT REPAIRED
# BELOW, and it disappears with it.
#
# FOR WHOEVER RELAUNCHES: the registered pattern is a FRESH TIMESTAMPED BASE (ADDENDUM 7
# already required "a fresh root"), against which $WORK does not exist and this is
# silent.  If an aborted arm leaves $WORK, MOVE IT ASIDE BY HAND -- a decision a person
# takes while looking at what is in it.
if [ -e "$WORK" ]; then
  echo "ABORT [EVIDENCE] $WORK already exists.  A run root is evidence and is never"
  echo "                 deleted to make room.  Use a fresh timestamped BASE, or move"
  echo "                 this tree aside by hand after looking at it."
  exit 6
fi
cp -a "$LBASE" "$WORK" || { echo "ABORT stage copy from $LBASE"; exit 4; }
rm -f "$WORK/runScript.py" "$WORK/logMeshGeneration.txt" "$WORK/volumeMesh.xyz" "$WORK/surfMesh.cgns" "$WORK/CRM_surfMesh.cgns.tar.gz" "$WORK/genWingMesh.py" "$WORK/preProcessing.sh" "$WORK/Allclean.sh" 2>/dev/null
cp -a "$BASE/d8g_runScript.py" "$BASE/d8g_of.py" "$WORK/" || { echo "ABORT stage instruments"; exit 4; }
case "$ARM" in
  F2-*) cp -a "$BASE/$AARM/d8g_A.json" "$WORK/d8g_A_gradient.json" || { echo "ABORT copy gradient"; exit 4; }
        echo "D8G_GRADIENT_STAGED arm=$ARM from=$AARM md5=$(md5sum "$WORK/d8g_A_gradient.json" | cut -d' ' -f1)" ;;
esac
# COLD START, verified BEFORE the launch, and the AGE GUARD's datum: 0/ is
# touched LAST at stage time, so every artifact the run produces must be
# strictly newer than 0/U or it did not come from this run.  pyDAFoam writes the
# primal end state back into time 0, so a second run of a directory silently
# warm-starts -- which is why a pre-existing time dir REFUSES.
for bad in "$WORK/reports" "$WORK/d8g_P.json" "$WORK/d8g_A.json" "$WORK/d8g_F.json" "$WORK/d8g_F.jsonl" "$WORK/d8g_P.jsonl" "$WORK/d8g_A.jsonl" "$WORK/OptView.hst" "$WORK/opt_IPOPT.txt" "$WORK/dRdWColoring_1.bin" "$WORK/dRdWColoring_4.bin"; do
  test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
done
test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
for d in "$WORK"/*/; do
  n=$(basename "$d")
  case "$n" in 0|0.orig) ;; [0-9]*) echo "ABORT G-COLD time dir present: $n"; exit 5 ;; esac
done
test -f "$WORK/0/U" || { echo "ABORT G-COLD 0/U missing"; exit 5; }
touch "$WORK/0"/* || { echo "ABORT age-guard datum"; exit 5; }
AGE_DATUM=$(stat -c '%Y' "$WORK/0/U")
echo "$AGE_DATUM" > "$WORK/.d8g_age_datum"
echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM datum_file=0/U"

# D8G REGISTERED DELTA: three modes, not two.  P = one cold primal to the
# registered endTime at this level; A = the L2 adjoint compute_totals at the
# BASELINE design; F = the L2 central-FD sweep beside it, including the
# section-4 trivial baseline step.  NO OPTIMISER RUNS IN THIS ITEM.
case "$MODE" in
  P) CMD="mpirun -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d8g_of.py -mode P -level $LEVEL" ;;
  A) CMD="mpirun -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d8g_of.py -mode A -level $LEVEL" ;;
  F) CMD="mpirun -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d8g_of.py -mode F -level $LEVEL" ;;
esac

# ---- the arm command goes to a FILE the container executes under its OWN
# ---- `timeout` at the registered cap wall (TMO), so the deadline is INSIDE the
# ---- container and survives every host shell.  `-k 60` escalates TERM to KILL;
# ---- the kernel exit code (124/137) is then the record.
CMDFILE="$WORK/${PREFIX}_cmd.sh"
# ---- RULING 3 (PREREGISTRATION.md AMENDMENT 2 (c)).  THE LAUNCH-WITNESS BUDGET
# ---- IS UNMEASURED AND CANNOT BE MEASURED FROM D8R's SURVIVING ARTEFACTS:
# ---- `StartedAt` is in the inspect record and the decomposePar banner is in the
# ---- log, but NOTHING TIMESTAMPS the gap between decomposePar finishing and the
# ---- first `^ExecutionTime = ` line the witness actually fires on.  (The
# ---- `ClockTime = 3-4 s` on that line is the SOLVER'S OWN clock and says nothing
# ---- about DASolver construction.)  One echo closes that gap on the FIRST D8G
# ---- arm and costs nothing, so the WITNESS_BUDGET placeholder below gets filled from
# ---- a MEASUREMENT rather than from a judgement.
# ---- IT IS NOT A GATE AND CANNOT BECOME ONE: it is a stdout line, read by a human
# ---- and by the cost calibration, never by a gate.
# ---- THREE PROPERTIES THAT ARE LOAD-BEARING:
# ----  1. `mpirun` REMAINS THE LAST COMMAND IN THE FILE, so `bash <cmdfile>` still
# ----     exits with mpirun's status and the kernel exit code the ledger records
# ----     is unchanged.  AN ECHO THAT MOVED THE EXIT STATUS WOULD BE A WORSE
# ----     DEFECT THAN THE ONE IT FIXES.
# ----  2. The prefix is `D4S_`, matching every other launcher line, and the line
# ----     matches NONE of the comparator's log readers (`^\s*primalMinResTol`,
# ----     `^(U0|U1|U2|he|p|nuTilda)\s+initRes:`, `^Time = `, `^Running Primal
# ----     Solver`, `^CD:`, `^CL:`), NOR the launch witness `^ExecutionTime = `,
# ----     NOR its forbidden decoy `^Time = `.  A launcher line that parsed as
# ----     solver output would be forged evidence for a gate that reads the log.
# ----  3. It is INSIDE the container and inside the `timeout`, so it dates the
# ----     moment the solver command was actually reached -- not the moment the
# ----     host decided to ask for it.
{ printf '%s\n' 'echo "D4S_MPIRUN_EPOCH: $(date -u +%s) iso=$(date -u +%Y-%m-%dT%H:%M:%SZ) arm='"$ARM"'"'
  printf '%s\n' "$CMD"; } > "$CMDFILE" || { echo "ABORT cmd file"; exit 4; }
echo "D4S_CMDFILE arm=$ARM md5=$(md5sum "$CMDFILE" | cut -d' ' -f1) deadline_in_container_s=$TMO"
CPUSAMPLE="$BASE/${ARM}_${STAMP}.cpu.jsonl"
# DELIVERED CORES ARE MEASURED, NOT INFERRED FROM THE QUOTA FLAG.  This sampler
# polls the container's own cgroup cpu.stat and writes cores-delivered to a
# FILE.  It is a passive reader: it starts nothing, kills nothing, and its
# failure cannot change a verdict -- an absent sample file is reported as
# NOT_MEASURED, never as a passing placement gate.
(
  for _ in $(seq 1 100000); do
    cid=$(docker ps -q --filter "name=^${NAME}$" 2>/dev/null | head -1)
    if [ -n "$cid" ]; then break; fi
    sleep 1
  done
  cg=""
  for cand in /sys/fs/cgroup/system.slice/docker-${cid}*.scope/cpu.stat \
              /sys/fs/cgroup/cpu/docker/${cid}*/cpuacct.usage; do
    if [ -e "$cand" ]; then cg="$cand"; break; fi
  done
  if [ -z "$cg" ]; then echo '{"delivered_cores":null,"note":"cgroup path not found"}' >> "$CPUSAMPLE"; exit 0; fi
  prev=""; prevt=""
  while docker ps -q --filter "name=^${NAME}$" 2>/dev/null | grep -q .; do
    now=$(date +%s.%N)
    if [ "$(basename "$cg")" = "cpu.stat" ]; then
      u=$(awk '/^usage_usec/{print $2}' "$cg" 2>/dev/null)
      t=$(awk '/^throttled_usec/{print $2}' "$cg" 2>/dev/null)
      n=$(awk '/^nr_throttled/{print $2}' "$cg" 2>/dev/null)
    else
      u=$(( $(cat "$cg" 2>/dev/null || echo 0) / 1000 )); t=0; n=0
    fi
    if [ -n "$prev" ] && [ -n "$u" ]; then
      python3 -c "
import json,sys
du=($u-$prev)/1e6; dt=$now-$prevt
print(json.dumps({'t':round($now,2),'delivered_cores':round(du/dt,4) if dt>0 else None,'throttled_usec':$t,'nr_throttled':$n}))
" >> "$CPUSAMPLE" 2>/dev/null
    fi
    prev=$u; prevt=$now
    sleep 15
  done
) &
SAMPLER=$!

# ===========================================================================
# LA.0 -- THE REGISTERED LAUNCH WITNESS, AND WHY IT IS THIS ONE.
#
# Candidates considered, each against the question "does its appearance prove
# THE SOLVER ITSELF started?", with the line number it occupies in the D8R
# producer's graded O-P arm log (named in full at the head of this file):
#
#  line   marker                                   proves
#  ----   --------------------------------------   ---------------------------
#     1   D4S_CONTAINER_UID: 0                     the container bash chain runs
#     6   D4S_DEADLINE_IN_CONTAINER_S: 15000       env sourced, idwarp imported
#    18   MCW rank 0 bound to socket 0[core 0...]  mpirun placed the ranks
#    46   Exec   : decomposePar                    decomposePar started
#   142   Time = 0                                 *** decomposePar's OWN time
#                                                  loop.  A FALSE WITNESS.
#   161   End                                      decomposePar finished
#   177   Initializing mesh and runtime for        DASolver construction BEGUN
#         DASolver                                 -- can print and then wedge
#                                                  in Create mesh / wallDist
#   185   DAOption created. DASolver initialized.  DASolver object exists
#   213   Initializing fields for DARhoSimpleCFoam the solver class is named and
#                                                  its fields are being built
#   725   Running Primal Solver 001                solvePrimal() was CALLED
#   730   Time = 1                                 first primal step begun
#   745   ExecutionTime = 2.58 s  ClockTime = 4 s  *** FIRST PRIMAL STEP
#                                                  COMPLETED
#
# REJECTED, with reasons:
#  - `log.decomposePar` completing / `Exec : decomposePar` / processor* dirs
#    appearing: decomposePar succeeding proves NOTHING about the solver.  All
#    three are satisfied at line 161, 584 lines before any solver step.
#  - `^Time = ` : REFUTED BY MEASUREMENT (line 142).  Any bare-regex wait on it
#    declares LAUNCHED on decomposePar.  It is registered below as a FORBIDDEN
#    pattern precisely so a successor cannot quietly reintroduce it.
#  - `Initializing mesh and runtime for DASolver` (177) : too optimistic.  It
#    is printed BEFORE `Create mesh for time = 0` and before wallDist; an MPI
#    or mesh hang after it still shows the marker.  It proves construction was
#    ENTERED, not that anything solved.
#  - `Running Primal Solver 001` (725) : strong -- it is the last thing printed
#    before solvePrimal() -- but it proves the CALL, not a step.  It is
#    recorded as a corroborator (LA.3), not as the gate.
#  - a processor time directory appearing : written at writeInterval, i.e.
#    hundreds of steps later.  Far too late to bound a launch wait.
#
# REGISTERED: the FIRST `^ExecutionTime = ` line in the container's own stdout.
#  (a) It is emitted ONLY by an OpenFOAM solver's time loop.  MEASURED on this
#      harness: 1616 occurrences against `^Time = `'s 1617, the one-line
#      difference being decomposePar's.  It cannot be produced by decomposePar,
#      by python import, or by the container shell.
#  (b) It proves a COMPLETED first iteration, not merely a call -- the
#      strongest claim available from stdout, and it is EARLY: 2.58 s of solver
#      time, ClockTime 4 s, at log line 745 of 1.9 MB.
#  (c) It is the SAME token CLAUDE.md rule 4 already counts for completion
#      (`ExecutionTime` count == steps).  One reader, one idiom; no second
#      vocabulary to drift from the first.
# ===========================================================================
# >>> D8G_LAUNCH_ASSERT_BEGIN
# ---------------------------------------------------------------------------
# THE BYTES BETWEEN THESE TWO MARKERS ARE EXTRACTED AND DRIVEN BY
#   d8g_launch_assert_selftest.sh
# The selftest evals THIS FILE'S bytes, not a copy, so a divergence between the
# tested assertion and the shipped one is impossible.  Every external
# dependency is injected through a variable so the selftest can substitute a
# fixture; NOTHING here is hard-coded to the docker client.
# ---------------------------------------------------------------------------
: "${DOCKER:=docker}"                       # injectable client
: "${LAUNCH_WITNESS_RE:=^ExecutionTime = }"         # LA.0, registered
: "${LAUNCH_WITNESS_FORBIDDEN_RE:=^Time = }"        # the decomposePar decoy
: "${LAUNCH_CORROBORATOR_RE:=^Running Primal Solver}"
: "${LAUNCH_WITNESS_POLL_S:=5}"                     # poll period
: "${LAUNCH_READER_RETRIES:=6}"                     # consecutive unreadable ticks tolerated
: "${LAUNCH_KILL:=yes}"                             # L-540: refusal kills the container

# --- LA.1  READERS THAT PRESERVE STDERR ------------------------------------
# The defect being repaired: every dafoam launcher writes
#     docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null
# so a daemon error, a sudo refusal and a typo'd name ALL read as the empty
# string, which the caller then compares against "true" and treats as "not
# running".  A daemon failure and a finished container become the same event.
# Here stderr is CAPTURED and reported, and "could not look" is a THIRD return
# value that never collapses into either of the other two.

la_state() {            # $1 = container id/name, $2 = path to append stderr to
  # echoes exactly one of: true | false | UNREADABLE
  local out rc
  out=$($DOCKER inspect --format '{{.State.Running}}' "$1" 2>>"$2"); rc=$?
  if [ "$rc" -ne 0 ]; then echo "UNREADABLE"; return 0; fi
  case "$out" in
    true|false) echo "$out" ;;
    *) printf 'la_state: inspect rc=0 but value was %q\n' "$out" >> "$2"; echo "UNREADABLE" ;;
  esac
}

la_logs() {             # $1 = container id/name, $2 = destination file
  # rc 0 = the log was read (destination holds container stdout+stderr).
  # rc != 0 = COULD NOT LOOK; the destination holds the client's own error text,
  #           which is DELIBERATELY not discarded -- it becomes the reason.
  $DOCKER logs "$1" > "$2" 2>&1
}

# --- LA.2  THE ASSERTION ----------------------------------------------------
# Returns:
#   0  witness seen                       -> launched: true
#  88  container exited before any witness -> launched: false, never started
#  89  bounded wait elapsed, still alive, no witness -> launched: false, wedged
#  90  the witness reader itself failed    -> launched: false, could not look
# 88/89/90 are DISJOINT from every exit code this family's solver produces
# (0, 1, 77 units refusal, 124/137 from the in-container timeout, 125 docker),
# so "never started" is never confusable with "started and failed".
# LIMIT, STATED: nothing prevents a future solver from exiting 88/89/90 of its
# own accord.  That is why the LEDGER carries an explicit `launched: false
# reason=<r>` token and the grader reads the TOKEN, not the number alone.
la_assert_launch() {    # $1 = cid  $2 = deadline seconds  $3 = scratch dir
  local cid="$1" budget="$2" tmp="$3"
  local logf="$tmp/la.log" errf="$tmp/la.stderr" t0 el st rc
  # TWO COUNTERS, NOT ONE.  THE SELFTEST CAUGHT THIS: with a single counter, a
  # SUCCESSFUL `docker inspect` reset the tally of FAILED `docker logs` reads on
  # every tick, so a permanently broken log reader could never reach the retry
  # threshold and was reported as `never_started_wedged` (89) instead of
  # `witness_reader_unreadable` (90).  That is exactly the conflation the rule
  # forbids -- "I could not look" reported as "I looked and saw nothing".
  # Each reader's failures are counted and cleared BY THAT READER ALONE.
  local unread_logs=0 unread_state=0
  : > "$errf"
  t0=$(date -u +%s)
  LA_REASON=""; LA_WITNESS_LINE=""; LA_WAITED_S=0; LA_CORROBORATED=no; LA_DECOY_SEEN=no
  while :; do
    el=$(( $(date -u +%s) - t0 )); LA_WAITED_S=$el

    if la_logs "$cid" "$logf"; then
      unread_logs=0
      if grep -aqE "$LAUNCH_CORROBORATOR_RE" "$logf" 2>/dev/null; then LA_CORROBORATED=yes; fi
      if grep -aqE "$LAUNCH_WITNESS_FORBIDDEN_RE" "$logf" 2>/dev/null; then LA_DECOY_SEEN=yes; fi
      LA_WITNESS_LINE=$(grep -anE "$LAUNCH_WITNESS_RE" "$logf" 2>/dev/null | head -1)
      if [ -n "$LA_WITNESS_LINE" ]; then
        LA_REASON="witness=$LAUNCH_WITNESS_RE seen after ${el}s at log line ${LA_WITNESS_LINE%%:*}"
        return 0
      fi
    else
      unread_logs=$((unread_logs+1))
      # the client's own error text, kept, not discarded
      printf 'la_logs failed (attempt %d): %s\n' "$unread_logs" "$(head -c 400 "$logf" 2>/dev/null | tr '\n' ' ')" >> "$errf"
      if [ "$unread_logs" -ge "$LAUNCH_READER_RETRIES" ]; then
        LA_REASON="witness_reader_unreadable (docker logs) after $unread_logs consecutive failures: $(tail -1 "$errf" | head -c 300)"
        return 90
      fi
    fi

    st=$(la_state "$cid" "$errf")
    case "$st" in
      false)
        # The container is gone and no witness was ever seen.  ONE FINAL READ:
        # the last poll may have raced the final flush.  Only after that read
        # comes back witness-free is "never started" asserted.
        if la_logs "$cid" "$logf"; then
          LA_WITNESS_LINE=$(grep -anE "$LAUNCH_WITNESS_RE" "$logf" 2>/dev/null | head -1)
          if [ -n "$LA_WITNESS_LINE" ]; then
            LA_REASON="witness seen on the final read after ${el}s at log line ${LA_WITNESS_LINE%%:*}"
            return 0
          fi
        fi
        LA_REASON="never_started_container_exited after ${el}s with no ${LAUNCH_WITNESS_RE} line; decomposePar_decoy_seen=$LA_DECOY_SEEN solver_call_seen=$LA_CORROBORATED"
        return 88 ;;
      UNREADABLE)
        unread_state=$((unread_state+1))
        if [ "$unread_state" -ge "$LAUNCH_READER_RETRIES" ]; then
          LA_REASON="witness_reader_unreadable (docker inspect) after $unread_state consecutive failures: $(tail -1 "$errf" | head -c 300)"
          return 90
        fi ;;
      true) unread_state=0 ;;
    esac

    if [ "$el" -ge "$budget" ]; then
      LA_REASON="never_started_wedged: ${budget}s elapsed, container still Running, no ${LAUNCH_WITNESS_RE} line; decomposePar_decoy_seen=$LA_DECOY_SEEN solver_call_seen=$LA_CORROBORATED"
      return 89
    fi
    sleep "$LAUNCH_WITNESS_POLL_S"
  done
}

# --- LA.1b  THE mtime WITNESS: A STRICT INCREASE AGAINST A RECORDED CAPTURE --
# cfd's stage-4 repair (commit 7d7fcebf) found a witness of the form
#     mtime >= t_launch - slack
# CONFIRMING A LAUNCH WHERE NO SOLVER STARTED: pre-existing STAGED files
# satisfied it.  Any absolute-time comparison, and any slack term, has that
# hole.  The required form, implemented here:
#   - capture every file's mtime BEFORE the container starts;
#   - WRITE THE CAPTURE TO DISK so a later reader can see what was compared
#     against -- a before-value held only in a shell variable is not auditable;
#   - assert a STRICT increase against that captured value.  Not `>=`.  Not
#     `>= t - slack`.  Not against wall-clock at all.  NO SLACK TERM EXISTS IN
#     THIS FILE, and none may be added: a witness needing slack is the wrong
#     witness.
la_capture_pre() {      # $1 = work dir, $2 = capture file.  echoes the row count.
  : > "$2"
  find "$1" -type f -printf '%T@ %p\n' 2>/dev/null | sort > "$2"
  wc -l < "$2" | tr -d ' '
}

la_mtime_witness() {    # $1 = work dir, $2 = the capture written by la_capture_pre
  # rc 0 = at least one file is STRICTLY newer than its captured mtime, or did
  #        not exist at capture time.   rc 1 = the tree is unchanged since the
  #        capture, i.e. NOTHING WROTE -- staged files alone can never satisfy
  #        this, because they are IN the capture at their own mtimes.
  LA_MTIME_EVIDENCE=$(find "$1" -type f -printf '%T@ %p\n' 2>/dev/null | sort | awk -v prefile="$2" '
    BEGIN { while ((getline l < prefile) > 0) { i=index(l," "); p=substr(l,i+1); pre[p]=substr(l,1,i-1)+0; seen[p]=1 } }
    { i=index($0," "); p=substr($0,i+1); m=substr($0,1,i-1)+0
      if (!(p in seen))      { print "NEW "      p;                              n++ }
      else if (m > pre[p])   { print "ADVANCED " p " " pre[p] " -> " m;          n++ } }
    END { exit (n > 0 ? 0 : 1) }')
  return $?
}

# --- LA.2b  THE REFUSAL PATH KILLS THE CONTAINER (L-540) --------------------
# `timeout` around a docker CLIENT does not stop the CONTAINER.  A lane on this
# team leaked a container that ran 2,834 s against a 300 s timeout and helped
# starve the box.  A launch refusal therefore KILLS, and it RECORDS whether the
# kill itself succeeded -- an unverified kill is not a kill.
la_kill() {             # $1 = cid, $2 = stderr sink ; echoes killed|kill_failed|not_attempted
  [ "$LAUNCH_KILL" = "yes" ] || { echo "not_attempted"; return 0; }
  if $DOCKER kill "$1" >/dev/null 2>>"$2"; then
    # READ BACK.  A kill that returns 0 and leaves the container Running is the
    # same false zero as a reader that cannot see a non-zero.
    local st; st=$(la_state "$1" "$2")
    case "$st" in false) echo "killed" ;; *) echo "kill_failed(state_after=$st)" ;; esac
  else
    echo "kill_failed(client_error)"
  fi
}
# <<< D8G_LAUNCH_ASSERT_END

# ===========================================================================
# LA.3 -- WHERE THE ASSERTION SITS IN THE ARM, AND THE CORROBORATORS.
# It sits BETWEEN the `docker run -d` and the runaway-guard poll loop, so no
# ledger row and no downstream grading can be reached without it.
# ===========================================================================

# THE BEFORE-LAUNCH CAPTURE.  Taken AFTER staging (so every staged file is in
# it, at its own mtime) and BEFORE `docker run` (so nothing the container does
# can be in it).  IT IS WRITTEN TO DISK AND ITS PATH AND ROW COUNT GO INTO THE
# LEDGER, so a later reader can see exactly what the strict comparison was
# made against.  A zero-row capture would make the witness vacuous -- every
# file would read as NEW -- so the row count is ASSERTED non-zero.
LAUNCH_PRE="$BASE/${ARM}_${STAMP}.launch_pre.tsv"
PRE_ROWS=$(la_capture_pre "$WORK" "$LAUNCH_PRE")
test "${PRE_ROWS:-0}" -gt 0 || { echo "ABORT LA.1b the before-launch capture of $WORK is EMPTY; the mtime witness would call every file NEW and confirm a launch that never happened"; exit 5; }
echo "D8G_LAUNCH_PRECAPTURE arm=$ARM capture=$(basename "$LAUNCH_PRE") rows=$PRE_ROWS staging_anchor_epoch=$AGE_DATUM comparison=strict_increase slack=none"

# THE CONTAINER ID IS CAPTURED.  D8R throws it away (`> /dev/null 2>&1` on the
# run line, d8r_run_arm.sh:410) and then addresses the container BY NAME for
# the rest of the arm.  Names are reusable; ids are not.  Every reader below
# addresses the ID.
CIDFILE="$BASE/${ARM}_${STAMP}.cid"
# D8G-R3-UID  2026-09-12.  WAS `docker run ... --user 0:0`.  TWO PRIVILEGE
# DEFECTS ON ONE LINE.  (a) Sanaa 2026-09-12 item 6: "As ubuntu.  Never root.
# Container jobs included."  The 2026-09-12 census attributes 642 root-owned files in
# THIS curriculum to this line.  uid 1000 AND gid 1000 are both `ubuntu`; 1002 is the
# IMAGE's dafoamuser group, SUPPLEMENTARY, solely to traverse the 0750 /home/dafoamuser
# -- MEASURED: `-u 1000:1000` alone dies "Permission denied" sourcing loadDAFoam.sh.
# CORROBORATED BY A LIVE PEER RUN on this same image: d6r2c_KR_REF, uid=1000:1000+1002.
# (b) `id ubuntu` carries 113(docker), the socket is 660 root:docker, so the CLIENT
# never needed root either -- MEASURED: plain `docker ps` as ubuntu returns rc=0 and
# lists the live peer container.  The container's user is set by `--user`, not the client.
CID=$(docker run -d --name "$NAME" \
    -u 1000:1000 --group-add 1002 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4S_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4S_IDWARP_IMPORTED_FROM:\",p); print(\"D4S_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     echo D4S_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k 60 $TMO bash /mnt/$ARM/${PREFIX}_cmd.sh" 2> "$BASE/${ARM}_${STAMP}.runerr") \
  || { echo "ABORT could not start container: $(head -c 400 "$BASE/${ARM}_${STAMP}.runerr")"; exit 4; }
# THE RUN COMMAND RETURNING IS NOT A WITNESS.  It has bought exactly one thing:
# an id to address.  Everything else is asserted below.
case "$CID" in
  [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]*) : ;;
  *) echo "ABORT docker run returned something that is not a container id: '$CID'"; exit 4 ;;
esac
echo "$CID" > "$CIDFILE"
T0=$(date -u +%s)
echo "D8G_CONTAINER_ID arm=$ARM name=$NAME cid=$CID launched_claim=NOT_YET_ASSERTED"

# THE WITNESS BUDGET.  It is registered per arm, and it is ASSERTED to be a
# strict fraction of the in-container deadline: a launch wait as long as the
# cap is not a wait, it is the run.  The WITNESS_BUDGET placeholder below is
# fixed in PREREGISTRATION.md alongside the cap table.
# SIZING EVIDENCE: on D8R's O-P arm (41,760 cells, 4 ranks) the container
# reached `Exec : decomposePar` 15 s after StartedAt (container start
# 22:31:01Z from the arm stamp; decomposePar's own header `Time : 22:31:16`)
# and the first `ExecutionTime` line came after decomposePar plus DASolver
# construction plus a 4 s solver ClockTime.  D8G's coarse and medium levels are
# SMALLER than D8R's mesh and its fine level larger; the budget must be sized
# PER LEVEL from that scaling and written into the cap table, not guessed here.
# ---------------------------------------------------------------------------
# THE WITNESS BUDGET IS DERIVED FROM THE DEADLINE, NEVER WRITTEN AS A LITERAL.
#
# The registered design requires LAUNCH_BUDGET_S to be a STRICT MINORITY of the
# in-container deadline TMO, and LA.3 below enforces exactly that (0 < b < t/2).
# TMO is itself derived at the cap assertion from the registered core-minute cap
# and the registered rank count, so deriving the budget FROM TMO keeps one
# number in this file where a literal would create a second that can drift.
# A hard-coded 352 is correct only while L1-P's cap is 46.977 core-min at 4
# ranks; move either and the literal is silently wrong, which is the same defect
# class as a memory ceiling describing the wrong machine.
#
# THE FORM: floor((TMO-1)/2) is the LARGEST INTEGER STRICTLY BELOW TMO/2, for
# both parities of TMO.  Largest is the right choice, and it is a safety choice
# rather than a permissive one: this budget decides when a launch is declared
# DEAD, so every second removed from it is added to the chance of killing a
# HEALTHY run that was merely slow to reach its first iteration.  There is no
# benefit to a smaller value -- a dead container is detected by the container
# state reader, not by this clock.
#
# *** AND THE WITNESS IS NOT THE MPIRUN LINE.  LAUNCH_WITNESS_RE is
# `^ExecutionTime = ` -- THE FIRST SOLVER ITERATION -- so this budget must cover
# container start + the TensorFlow import + DASolver construction + decomposePar
# + one iteration, not merely the moment mpirun was reached.  MEASURED TONIGHT
# on A3GC L3 (99,840 cells, 4 ranks, this box): launch 22:15:33Z, first
# `ExecutionTime` line ~22:19-22:20Z -- about 270-290 s at load 26-32, and
# ~370 s on the earlier attempt at load 37-70.  D8G L1 is 5,568 cells, so its
# mesh read and decomposePar are near-instant, but THE TENSORFLOW IMPORT IS
# MESH-INDEPENDENT and was ~60-70 s of that.  Against L1-P's derived budget of
# 352 s the headroom is real but THINNER THAN IT LOOKS, and it cannot be widened
# -- 352 IS the ceiling.  If a future level ever fails LA with a healthy
# container, this is the paragraph to read first. ***
# ---------------------------------------------------------------------------
LAUNCH_BUDGET_S=$(python3 -c "
import math, sys
t = $TMO
b = int(math.floor((t - 1) / 2))
if not (0 < b < 0.5 * t):
    sys.stderr.write('derived budget %r is not a strict minority of deadline %r\n' % (b, t))
    sys.exit(1)
print(b)
") || { echo "ABORT LA.3a could not derive the launch-witness budget from TMO=$TMO"; exit 65; }
echo "D4S_LAUNCH_BUDGET_DERIVED arm=$ARM tmo_s=$TMO budget_s=$LAUNCH_BUDGET_S rule=floor((TMO-1)/2) strict_minority=yes"
python3 -c "
import sys
b, t = $LAUNCH_BUDGET_S, $TMO
if not (0 < b < 0.5*t):
    sys.stderr.write('ABORT LA budget %r is not a strict minority of the deadline %r\n' % (b, t)); sys.exit(1)
" || { echo "ABORT LA.3 launch-witness budget vs deadline"; exit 65; }

LA_TMP="$BASE/.la_${ARM}_${STAMP}"; mkdir -p "$LA_TMP"
la_assert_launch "$CID" "$LAUNCH_BUDGET_S" "$LA_TMP"; LA_RC=$?

# THE mtime WITNESS, EVALUATED AGAINST THE RECORDED CAPTURE (LA.1b).
# It is CORROBORATING, NOT GATING, and the reason is specific to this harness:
# DAFoam writes its fields to processor*/ at writeInterval, hundreds of steps
# after launch, while processor*/ ITSELF is created by decomposePar -- so as a
# GATE it would either fire on decomposePar (the same false witness as
# `^Time = `) or fire far too late to bound a wait.  The LOG witness gates.
# But it is recorded on every arm, in both directions, because a `launched:
# true` from the log witness with NOTHING written since the capture is a
# contradiction a grader must be able to see.
if la_mtime_witness "$WORK" "$LAUNCH_PRE"; then
  LA_MTIME=advanced
else
  LA_MTIME=unchanged_since_capture
fi
echo "D8G_LAUNCH_MTIME_WITNESS arm=$ARM result=$LA_MTIME capture=$(basename "$LAUNCH_PRE") rows=$PRE_ROWS gating=no evidence=[$(printf '%s' "${LA_MTIME_EVIDENCE:-none}" | tr '\n' ';' | head -c 300)]"
if [ "$LA_RC" -eq 0 ] && [ "$LA_MTIME" = "unchanged_since_capture" ]; then
  echo "D8G_LAUNCH_CONTRADICTION arm=$ARM the log witness fired but NOT ONE FILE in $WORK is strictly newer than the recorded capture.  A grader must treat this row as suspect."  | tee -a "$BASE/ledger.txt"
fi

# ===========================================================================
# LA.4 -- `launched: false` WITH A REASON.  Not a bare false, not an rc alone.
# ===========================================================================
if [ "$LA_RC" -ne 0 ]; then
  KILLED=$(la_kill "$CID" "$LA_TMP/la.stderr")
  docker logs "$CID" > "$LOG" 2>&1
  EXITCODE=$(docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$CID" 2>>"$LA_TMP/la.stderr")
  kill $SAMPLER 2>/dev/null; wait $SAMPLER 2>/dev/null
  {
    echo "ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST launched: false reason=[$LA_REASON] launch_rc=$LA_RC waited_s=$LA_WAITED_S budget_s=$LAUNCH_BUDGET_S mtime_witness=$LA_MTIME precapture=$(basename "$LAUNCH_PRE") precapture_rows=$PRE_ROWS cid=$CID container_kill=$KILLED inspect(exit,oomkilled)=[$EXITCODE] decomposePar_decoy_seen=$LA_DECOY_SEEN solver_call_seen=$LA_CORROBORATED log=$(basename "$LOG") stamp=$STAMP"
    echo "D8G_LAUNCH_REFUSED arm=$ARM rc=$LA_RC -- THE SOLVER'S FIRST ARTIFACT NEVER APPEARED.  This row is NOT A RESULT and no grading may read it."
    echo "D8G_LAUNCH_READER_STDERR arm=$ARM: $(tr '\n' ' ' < "$LA_TMP/la.stderr" | head -c 600)"
  } | tee -a "$BASE/ledger.txt"
  docker rm "$CID" >/dev/null 2>&1
  exit "$LA_RC"
fi
echo "D8G_LAUNCH_ASSERTED arm=$ARM launched: true reason=[$LA_REASON] waited_s=$LA_WAITED_S budget_s=$LAUNCH_BUDGET_S mtime_witness=$LA_MTIME precapture=$(basename "$LAUNCH_PRE") precapture_rows=$PRE_ROWS cid=$CID solver_call_seen=$LA_CORROBORATED" | tee -a "$BASE/ledger.txt"

# ===========================================================================
# THE RUNAWAY GUARD AND THE LEDGER -- D8R's tail, with TWO LA-DRIVEN CHANGES:
#   * every reader addresses THE CONTAINER ID, not the NAME.  Names are
#     reusable; ids are not.
#   * every `docker inspect` keeps its stderr (appended to la.stderr) and
#     carries an UNREADABLE branch, so "I could not look" never collapses into
#     "I looked and it had stopped" -- the same conflation LA.1 repairs.
#   * T0 was set at LA.3, BEFORE the launch wait, so the launch wait is INSIDE
#     the graded wall and cannot be spent for free.
#
# The cap is a RUNAWAY GUARD THAT REPORTS (Sanaa, 2026-08-25), not a budget
# rigor is trimmed to fit -- and on THIS item PREREGISTRATION.md section 6.4
# suspends the stop entirely (Sanaa, 2026-09-10: no budget gates on the 3D
# cases).  A crossing is written to the ledger and CONTINUES.  CEILING = 4 x CAP
# remains a hard stop so a genuine runaway is still bounded WHILE THIS SHELL
# LIVES; the in-container `timeout` is the containment that survives shell death.
# ===========================================================================
CEILING=$(python3 -c "print('%.1f' % (4.0*$CAP))")
echo "D4S_RUNAWAY_GUARD arm=$ARM cap_core_min=$CAP ceiling_core_min=$CEILING mode=report_then_stop_at_ceiling cap_is_a_stop=no_section_6.4"
CAP_REPORTED=no; CEILING_HIT=no; UNREADABLE_TICKS=0
while true; do
  RUNNING=$(docker inspect --format '{{.State.Running}}' "$CID" 2>>"$LA_TMP/la.stderr")
  RIRC=$?
  NOW=$(date -u +%s); EL=$((NOW-T0))
  CM=$(python3 -c "print(round($EL*$RANKS/60.0,3))")
  if [ "$RIRC" -ne 0 ] || { [ "$RUNNING" != "true" ] && [ "$RUNNING" != "false" ]; }; then
    UNREADABLE_TICKS=$((UNREADABLE_TICKS+1))
    if [ "$UNREADABLE_TICKS" -ge "$LAUNCH_READER_RETRIES" ]; then
      echo "D8G_GUARD_READER_UNREADABLE arm=$ARM after $UNREADABLE_TICKS consecutive failures: $(tail -1 "$LA_TMP/la.stderr" | head -c 300)" | tee -a "$BASE/ledger.txt"
      break
    fi
    sleep 10; continue
  fi
  UNREADABLE_TICKS=0
  if [ "$RUNNING" != "true" ]; then break; fi
  if [ "$CAP_REPORTED" = "no" ] && [ "$(python3 -c "print(1 if $CM > $CAP else 0)")" = "1" ]; then
    CAP_REPORTED=yes
    echo "D4S_CAP_CROSSED arm=$ARM core_min=$CM cap=$CAP ceiling=$CEILING action=REPORTED_RUN_CONTINUES section_6.4_exemption supervisor_decides" | tee -a "$BASE/ledger.txt"
  fi
  if [ "$(python3 -c "print(1 if $CM > $CEILING else 0)")" = "1" ]; then
    CEILING_HIT=yes
    echo "D4S_CEILING_HIT arm=$ARM core_min=$CM ceiling=$CEILING action=HARD_STOP" | tee -a "$BASE/ledger.txt"
    docker stop -t 30 "$CID" >/dev/null 2>>"$LA_TMP/la.stderr"
    break
  fi
  sleep 10
done
docker logs "$CID" > "$LOG" 2>&1
# THE KERNEL'S VERDICT, read BEFORE the container is removed.
rc=$(docker inspect --format '{{.State.ExitCode}}' "$CID" 2>>"$LA_TMP/la.stderr")
test -n "$rc" || rc=125
T1=$(date -u +%s)
WALL=$((T1-T0))
kill $SAMPLER 2>/dev/null; wait $SAMPLER 2>/dev/null
SIBLINGS_POST=$(container_census)
DELIVERED=$(python3 -c "
import json,sys,os
p='$CPUSAMPLE'
if not os.path.exists(p): print('NOT_MEASURED'); sys.exit()
v=[]
thr=0
for line in open(p):
    try: d=json.loads(line)
    except Exception: continue
    if d.get('delivered_cores') is not None: v.append(d['delivered_cores'])
    thr=max(thr, d.get('nr_throttled') or 0)
print('%s n=%d max_nr_throttled=%d' % (('%.4f'%(sum(v)/len(v)) if v else 'NOT_MEASURED'), len(v), thr))
" 2>/dev/null)

# ---- the KERNEL's verdict, read BEFORE the container is removed (8.2) ----
INSPECT=$(docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$CID" 2>>"$LA_TMP/la.stderr")
echo "$(docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.StartedAt}} {{.State.FinishedAt}} {{.HostConfig.CpusetCpus}} {{.HostConfig.Memory}}' "$CID" 2>>"$LA_TMP/la.stderr") $GOT_DIGEST" > "$BASE/${ARM}_${STAMP}.inspect.txt"   # the surviving kernel record (the grader's L-342 fallback)
docker rm "$CID" >/dev/null 2>&1
# D8G-R3-UID: was `sudo -n chown`.  It existed ONLY to undo the root ownership the
# container created.  The container is now ubuntu, so this is a successful no-op and
# needs no privilege.  Kept rather than deleted: it still normalises anything a
# PREVIOUS root-era run left in a reused tree.
chown -R ubuntu:ubuntu "$LOG" "$WORK" 2>/dev/null

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/ledger.txt"
{
  echo "ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM inspect(exit,oomkilled)=[$INSPECT] memavail_pre_GiB=$MEMAVAIL_GIB memavail_post_GiB=$MEMAVAIL_POST cpuset=$CPUSET delivered_cores_mean=[$DELIVERED] siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] log=$(basename "$LOG") stamp=$STAMP"
  echo "D8G_ARM_CONTEXT arm=$ARM level=$LEVEL mode=$MODE cells=$REC_CELLS points_md5=$REC_MD5 launched=true launch_waited_s=$LA_WAITED_S mtime_witness=$LA_MTIME cid=$CID"
  grep -a "D4S_CONTAINER_UID\|D4S_IDWARP_SO_MD5\|D4S_DEADLINE_IN_CONTAINER_S" "$LOG" | head -3   # the strings the container prints
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc

# =============================================================================
# AMENDMENT 3 -- 2026-09-11 -- THE STAGED-INSTRUMENT MANIFEST SEPARATOR
# lines whose number changed above this section: 0
#
# ONE CHARACTER CHANGED, AT THE `MD5_OUT=` LINE: printf '%s\n' -> printf '%b\n'.
# Nothing is inserted above it, so every line number cited by any record --
# INSTRUMENT_MD5S at 275, LAUNCH_WITNESS_RE at 588, LAUNCH_BUDGET_S at 838 --
# is unchanged.  That is why the fix is %b rather than rewriting the manifest
# with real newlines, which would have shifted 760 lines of cited file.
#
# THE DEFECT: INSTRUMENT_MD5S separates its three rows with a LITERAL
# BACKSLASH-n -- two characters inside a double-quoted bash string.  Bash does
# not interpret it and `printf %s` does not interpret it, so md5sum received ONE
# filename containing the whole manifest and the check COULD NEVER PASS,
# whatever was staged.  MEASURED with all three instruments present and every
# md5 MATCHING:
#     printf '%s\n'  ->  rc 1, 0 OK lines, "No such file or directory"
#     printf '%b\n'  ->  rc 0, 3 OK lines
# and the guard demands 3, so it could only ever abort.
#
# THE MIRROR OF TONIGHT'S PATTERN: not a check that cannot FAIL, but a check
# that cannot PASS.  It fails SAFE -- refusing a correct staging rather than
# admitting a wrong one -- which is why it cost zero core-min.
#
# WHY %b IS SAFE HERE: the manifest holds only hex digests, spaces, slashes and
# the @BASE@ token -- no other backslash sequence -- and @BASE@ is replaced by
# sed AFTER printf runs, so no path content is ever exposed to escape
# interpretation.  DO NOT "SIMPLIFY" IT BACK TO %s: that is the defect.
# =============================================================================
