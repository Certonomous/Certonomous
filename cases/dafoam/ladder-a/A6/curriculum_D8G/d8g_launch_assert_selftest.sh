#!/usr/bin/env bash
# =============================================================================
# PERMISSION: FROZEN by the dafoam-supervisor 2026-09-11.
#
# SELFTEST FOR THE D8G LAUNCH ASSERTION.
#
# WHAT IT DRIVES: the bytes between `# >>> D8G_LAUNCH_ASSERT_BEGIN` and
# `# <<< D8G_LAUNCH_ASSERT_END` in d8g_run_arm.sh.  They are EXTRACTED
# FROM THAT FILE AND EVAL'D -- not copied here.  A selftest that tests a copy
# tests the copy.
#
# WHY IT EXISTS: an assertion never shown able to REFUSE is not an assertion.
# This team produced three false zeros in one day and every one was a reader
# nobody had shown could see the other answer (CLAUDE.md rule 3).  So the
# controls below are PLANTED and run in BOTH directions, and the sharpest pair
# (P2 vs N1) differ by EXACTLY ONE LINE -- the planted witness.
#
# WHAT IT DOES NOT TEST, STATED PLAINLY: docker.  The client is injected
# through $DOCKER and replaced by a fixture-driven stub, so what is exercised
# is THE READER, ITS THREE-WAY OUTCOME AND ITS REFUSAL WIRING, not the daemon.
# A green here does NOT mean the assertion has ever watched a real DAFoam
# container.  That evidence can only come from the first D8G arm.
# =============================================================================
set -uo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TARGET="$HERE/d8g_run_arm.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
PASS=0; FAIL=0

say() { printf '%s\n' "$*"; }
check() {  # $1 = name, $2 = expected, $3 = got
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); say "  PASS  $1  (expected=$2 got=$3)"
  else FAIL=$((FAIL+1)); say "  FAIL  $1  (expected=$2 got=$3)"; fi
}

# ---------------------------------------------------------------------------
# C0 -- THE EXTRACTION IS ITSELF A PLANTED-ZERO RISK AND IS GUARDED.
# A sed range that matches nothing yields an empty block; `eval ""` succeeds;
# every case below would then fail loudly OR, worse, a future refactor could
# make them pass against nothing.  So: assert the block is non-empty AND
# carries the three function definitions by name, BEFORE anything is eval'd.
# ---------------------------------------------------------------------------
test -f "$TARGET" || { say "REFUSE C0 target not found: $TARGET"; exit 2; }
sed -n '/^# >>> D8G_LAUNCH_ASSERT_BEGIN$/,/^# <<< D8G_LAUNCH_ASSERT_END$/p' "$TARGET" > "$TMP/block.sh"
BLOCK_LINES=$(wc -l < "$TMP/block.sh")
say "C0 extraction: $BLOCK_LINES lines from $TARGET"
[ "$BLOCK_LINES" -ge 40 ] || { say "REFUSE C0 extracted block is $BLOCK_LINES lines -- an empty or truncated extraction would make every case below vacuous"; exit 2; }
for fn in la_state la_logs la_assert_launch la_kill la_capture_pre la_mtime_witness; do
  grep -q "^$fn() {" "$TMP/block.sh" || { say "REFUSE C0 extracted block does not define $fn()"; exit 2; }
done
say "C0 OK  block defines la_state la_logs la_assert_launch la_kill la_capture_pre la_mtime_witness"
grep -q 'slack' "$TMP/block.sh" && ! grep -q 'NO SLACK TERM EXISTS' "$TMP/block.sh" && { say "REFUSE C0 the block mentions slack outside its prohibition"; exit 2; }

# ---------------------------------------------------------------------------
# THE STUB CLIENT.  Fixture-driven, and it RECORDS what was asked of it so the
# kill in the refusal path is verified by observation, not by reading the code.
# ---------------------------------------------------------------------------
FD_LOG=""        # fixture file served as container stdout
FD_STATE=true    # what `inspect .State.Running` reports
FD_LOGS_RC=0     # non-zero => the log reader itself fails
FD_INSPECT_RC=0  # non-zero => the state reader itself fails
FD_KILL_RC=0     # non-zero => the kill client fails
FD_KILL_STOPS=yes # does the kill actually stop it?
# THE KILL TALLY LIVES IN A FILE, NOT A VARIABLE.  `la_kill` is invoked inside
# a command substitution, i.e. a SUBSHELL: an incremented variable dies with
# it and the tally read back as 0 -- a false zero in the very control that
# proves L-540's kill was issued.  The selftest caught this on its first run.
FD_KILLFILE=""

fake_docker() {
  case "$1" in
    inspect)
      if [ "$FD_INSPECT_RC" -ne 0 ]; then
        echo "Cannot connect to the Docker daemon at unix:///var/run/docker.sock." >&2
        return "$FD_INSPECT_RC"
      fi
      case "$*" in
        *State.Running*) echo "$FD_STATE" ;;
        *) echo "0 false" ;;
      esac
      return 0 ;;
    logs)
      if [ "$FD_LOGS_RC" -ne 0 ]; then
        echo "Error response from daemon: No such container: ${*: -1}" >&2
        return "$FD_LOGS_RC"
      fi
      cat "$FD_LOG"
      return 0 ;;
    kill)
      [ -n "$FD_KILLFILE" ] && echo "kill ${*: -1}" >> "$FD_KILLFILE"
      [ "$FD_KILL_RC" -eq 0 ] || { echo "Error response from daemon: cannot kill" >&2; return "$FD_KILL_RC"; }
      [ "$FD_KILL_STOPS" = "yes" ] && FD_STATE=false
      return 0 ;;
    *) return 0 ;;
  esac
}

DOCKER=fake_docker
LAUNCH_WITNESS_POLL_S=1
LAUNCH_READER_RETRIES=2
# shellcheck disable=SC1090
eval "$(cat "$TMP/block.sh")"

# ---------------------------------------------------------------------------
# THE FIXTURES.  F_SETUP is a faithful reduction of the REAL D8R arm log
#   /home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/O-P_20260827T223101Z_1595223.log
# lines 1-745: the container banner, mpirun's rank bindings, the DAFoam banner,
# the WHOLE of decomposePar INCLUDING ITS `Time = 0` AT LINE 142 AND ITS `End`,
# then DASolver construction.  It stops one line short of the witness.
# ---------------------------------------------------------------------------
cat > "$TMP/f_setup.log" <<'EOF'
D4S_CONTAINER_UID: 0
D4S_IDWARP_IMPORTED_FROM: /opt/idwarp_patched/idwarp/__init__.py
D4S_IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425
D4S_DEADLINE_IN_CONTAINER_S: 15000
[cb36d9fd8766:00265] MCW rank 0 bound to socket 0[core 0[hwt 0]]: [B/././.]
|                               DAFoam v5.0.0                                 |
Exec   : decomposePar
Create time
Time = 0

Processor 0: field transfer
End

Initializing mesh and runtime for DASolver
Create mesh for time = 0
DAOption created. DASolver initialized.
Initializing fields for DARhoSimpleCFoam
Setting primal boundary conditions...
Running Primal Solver 001
Time = 1
EOF
# THE PLANT.  P2's fixture is N1's fixture PLUS EXACTLY THIS ONE LINE.
cp "$TMP/f_setup.log" "$TMP/f_solved.log"
echo 'ExecutionTime = 2.58 s  ClockTime = 4 s' >> "$TMP/f_solved.log"
# The decoy fixture: decomposePar ONLY.  Everything a launcher waiting on
# `^Time = ` would have accepted, and nothing a solver produced.
sed -n '1,12p' "$TMP/f_setup.log" > "$TMP/f_decoy.log"
# A crash fixture: python raised at import, the chain is winding down.
cat > "$TMP/f_crash.log" <<'EOF'
D4S_CONTAINER_UID: 0
D4S_DEADLINE_IN_CONTAINER_S: 15000
Traceback (most recent call last):
  File "d8g_of.py", line 3, in <module>
    from mphys.multipoint import Multipoint
ModuleNotFoundError: No module named 'mphys'
EOF
say ""
say "fixtures: f_setup=$(wc -l < "$TMP/f_setup.log")L  f_solved=$(wc -l < "$TMP/f_solved.log")L (= f_setup + 1 planted line)  f_decoy=$(wc -l < "$TMP/f_decoy.log")L  f_crash=$(wc -l < "$TMP/f_crash.log")L"
say ""

reset_stub() { FD_STATE=true; FD_LOGS_RC=0; FD_INSPECT_RC=0; FD_KILL_RC=0; FD_KILL_STOPS=yes
  FD_KILLFILE="$TMP/kills.$RANDOM"; : > "$FD_KILLFILE"; }
kills_seen() { wc -l < "$FD_KILLFILE" | tr -d ' '; }

# ===========================================================================
say "P1  POSITIVE -- the witness is present.  The assertion must PASS."
reset_stub; FD_LOG="$TMP/f_solved.log"
la_assert_launch cid_p1 4 "$TMP"; RC=$?
check "P1 rc" 0 "$RC"
case "$LA_REASON" in *"ExecutionTime"*) check "P1 reason names the witness" yes yes ;; *) check "P1 reason names the witness" yes "no [$LA_REASON]" ;; esac
check "P1 corroborator (Running Primal Solver) seen" yes "$LA_CORROBORATED"

# ===========================================================================
say ""
say "N1  NEGATIVE -- container alive, witness never appears.  MUST REFUSE 89 AND KILL."
reset_stub; FD_LOG="$TMP/f_setup.log"; FD_STATE=true
la_assert_launch cid_n1 2 "$TMP"; RC=$?
check "N1 rc (wedged)" 89 "$RC"
case "$LA_REASON" in *never_started_wedged*) check "N1 reason" yes yes ;; *) check "N1 reason" yes "no [$LA_REASON]" ;; esac
KRES=$(la_kill cid_n1 "$TMP/la.stderr")
check "N1 L-540 docker kill invoked (counted on disk, not in a subshell)" 1 "$(kills_seen)"
check "N1 kill verified by read-back" killed "$KRES"

# P2  THE MUTATION CONTROL.  Same fixture as N1 PLUS the one planted line.
say ""
say "P2  PLANTED-MUTATION CONTROL -- N1's fixture + exactly one witness line."
reset_stub; FD_LOG="$TMP/f_solved.log"; FD_STATE=true
la_assert_launch cid_p2 2 "$TMP"; RC=$?
check "P2 rc (the ONE planted line flips 89 -> 0)" 0 "$RC"

# ===========================================================================
say ""
say "N2  NEGATIVE -- container exited before any witness (python raised)."
reset_stub; FD_LOG="$TMP/f_crash.log"; FD_STATE=false
la_assert_launch cid_n2 4 "$TMP"; RC=$?
check "N2 rc (never started, exited)" 88 "$RC"
case "$LA_REASON" in *never_started_container_exited*) check "N2 reason" yes yes ;; *) check "N2 reason" yes "no [$LA_REASON]" ;; esac
check "N2 rc is DISTINCT from the wedged rc" distinct "$([ 88 -ne 89 ] && echo distinct || echo same)"

# ===========================================================================
say ""
say "N3  DECOY -- decomposePar ran to End, printed 'Time = 0', and nothing solved."
say "    This is the case that refutes '^Time = ' as a witness."
reset_stub; FD_LOG="$TMP/f_decoy.log"; FD_STATE=false
la_assert_launch cid_n3 4 "$TMP"; RC=$?
check "N3 rc (decomposePar is NOT a launch)" 88 "$RC"
check "N3 the decoy WAS seen (so the decoy fixture is not vacuous)" yes "$LA_DECOY_SEEN"
check "N3 no solver call was seen" no "$LA_CORROBORATED"
# and prove the decoy fixture really would have satisfied the naive witness:
check "N3 fixture DOES match the forbidden ^Time = pattern" 1 "$(grep -acE '^Time = ' "$TMP/f_decoy.log")"
check "N3 fixture does NOT match the registered witness" 0 "$(grep -acE '^ExecutionTime = ' "$TMP/f_decoy.log")"

# ===========================================================================
say ""
say "N4  READER FAILURE -- 'docker logs' itself fails.  MUST be 'could not look',"
say "    NOT 'looked and saw nothing' and NOT success."
reset_stub; FD_LOG="$TMP/f_solved.log"; FD_LOGS_RC=1; FD_STATE=true
la_assert_launch cid_n4 4 "$TMP"; RC=$?
check "N4 rc (witness reader unreadable)" 90 "$RC"
case "$LA_REASON" in *witness_reader_unreadable*) check "N4 reason distinguishes could-not-look" yes yes ;; *) check "N4 reason distinguishes could-not-look" yes "no [$LA_REASON]" ;; esac
case "$LA_REASON" in *"No such container"*|*"daemon"*) check "N4 the client's stderr is CARRIED, not discarded" yes yes ;; *) check "N4 the client's stderr is CARRIED, not discarded" yes "no [$LA_REASON]" ;; esac

say ""
say "N5  READER FAILURE -- 'docker inspect' fails (daemon unreachable).  The"
say "    repaired defect: 2>/dev/null made this read as the empty string and"
say "    then as 'not running', i.e. as a finished container."
reset_stub; FD_LOG="$TMP/f_setup.log"; FD_INSPECT_RC=1; FD_STATE=true
la_assert_launch cid_n5 6 "$TMP"; RC=$?
check "N5 rc (state reader unreadable)" 90 "$RC"
case "$LA_REASON" in *"docker inspect"*) check "N5 reason names the failing reader" yes yes ;; *) check "N5 reason names the failing reader" yes "no [$LA_REASON]" ;; esac
# and the direct unit check on the three-way return:
FD_INSPECT_RC=1; check "N5 la_state returns UNREADABLE, not false" UNREADABLE "$(la_state cid_n5 "$TMP/e5")"
FD_INSPECT_RC=0; FD_STATE=false; check "N5 la_state returns false when it CAN look" false "$(la_state cid_n5 "$TMP/e5")"

# ===========================================================================
say ""
say "N6  A KILL THAT DID NOT KILL is reported as a failed kill, never as killed."
reset_stub; FD_KILL_STOPS=no; FD_STATE=true
KRES=$(la_kill cid_n6 "$TMP/e6")
case "$KRES" in kill_failed*) check "N6 unverified kill is reported failed" yes yes ;; *) check "N6 unverified kill is reported failed" yes "no [$KRES]" ;; esac

# ===========================================================================
# ===========================================================================
# PART TWO -- THE FAKE-SOLVER EXECUTION HARNESS.
#
# cfd found their defect BY EXECUTING THE LAUNCHER THROUGH A NO-SOLVER BRANCH
# WITH A FAKE SOLVER, NOT BY READING IT (their commit 7d7fcebf).  A code read
# would not have caught it: `mtime >= t_launch - slack` LOOKS like a witness
# and is only exposed when the thing runs and the solver does not.
#
# So Part Two RUNS.  The "container" is a real background bash process writing
# a real log into a real staged work tree; the docker stub reports that
# process's actual liveness and cats its actual log.  Nothing here is a
# fixture standing in for behaviour -- the behaviour happens.
# ===========================================================================
say ""
say "=================== PART TWO: FAKE SOLVER, EXECUTED ==================="

FS_PIDFILE=""; FS_LOGFILE=""
fake_docker_proc() {
  case "$1" in
    inspect)
      if [ "$FD_INSPECT_RC" -ne 0 ]; then echo "Cannot connect to the Docker daemon." >&2; return "$FD_INSPECT_RC"; fi
      case "$*" in
        *State.Running*)
          if [ -s "$FS_PIDFILE" ] && kill -0 "$(cat "$FS_PIDFILE")" 2>/dev/null; then echo true; else echo false; fi ;;
        *) echo "0 false" ;;
      esac
      return 0 ;;
    logs)
      if [ "$FD_LOGS_RC" -ne 0 ]; then echo "Error response from daemon: No such container: ${*: -1}" >&2; return "$FD_LOGS_RC"; fi
      cat "$FS_LOGFILE" 2>/dev/null; return 0 ;;
    kill)
      [ -n "$FD_KILLFILE" ] && echo "kill ${*: -1}" >> "$FD_KILLFILE"
      [ -s "$FS_PIDFILE" ] && kill -9 "$(cat "$FS_PIDFILE")" 2>/dev/null
      sleep 0.3; return 0 ;;
    *) return 0 ;;
  esac
}

stage_tree() {   # $1 = work dir.  A plausible staged DAFoam case, mtimes NOW.
  local w="$1"; rm -rf "$w"; mkdir -p "$w/0" "$w/constant/polyMesh" "$w/system" "$w/processor0/0"
  echo U      > "$w/0/U";        echo p > "$w/0/p"
  echo points > "$w/constant/polyMesh/points"
  echo cd     > "$w/system/controlDict"
  echo pU     > "$w/processor0/0/U"
  touch "$w"/0/* "$w"/constant/polyMesh/* "$w"/system/* "$w"/processor0/0/*
}

start_fake_solver() {   # $1 = work dir  $2 = mode: writes|silent|none
  FS_LOGFILE="$TMP/fs.log"; FS_PIDFILE="$TMP/fs.pid"; : > "$FS_LOGFILE"; : > "$FS_PIDFILE"
  case "$2" in
    none) return 0 ;;   # NOTHING IS LAUNCHED.  The staged tree is all there is.
  esac
  ( cat "$TMP/f_setup.log" >> "$FS_LOGFILE"
    if [ "$2" = "writes" ]; then
      sleep 1
      # a real write into the real staged tree, and a real witness line
      echo 1000 > "$1/processor0/0/phi"
      echo 'ExecutionTime = 2.58 s  ClockTime = 4 s' >> "$FS_LOGFILE"
      sleep 30
    else
      sleep 30    # STARTS BUT NEVER WRITES
    fi ) & echo $! > "$FS_PIDFILE"; disown 2>/dev/null
  sleep 0.4
}
stop_fake_solver() { [ -s "$FS_PIDFILE" ] && kill -9 "$(cat "$FS_PIDFILE")" 2>/dev/null; wait 2>/dev/null; }

DOCKER=fake_docker_proc
W="$TMP/work"

# --- FS1  the fake solver WRITES the artifact -------------------------------
say ""
say "FS1  fake solver STARTS AND WRITES.  Expect launched: true, mtime advanced."
reset_stub; stage_tree "$W"
PRE="$TMP/pre1.tsv"; ROWS=$(la_capture_pre "$W" "$PRE")
check "FS1 before-launch capture is non-empty and ON DISK (5 staged files)" 5 "$ROWS"
start_fake_solver "$W" writes
la_assert_launch cid_fs1 8 "$TMP"; RC=$?
check "FS1 launch rc" 0 "$RC"
if la_mtime_witness "$W" "$PRE"; then MW=advanced; else MW=unchanged_since_capture; fi
check "FS1 mtime witness (strict, vs the recorded capture)" advanced "$MW"
case "$LA_MTIME_EVIDENCE" in *"NEW $W/processor0/0/phi"*) check "FS1 evidence names the file the solver wrote" yes yes ;; *) check "FS1 evidence names the file the solver wrote" yes "no [$LA_MTIME_EVIDENCE]" ;; esac
stop_fake_solver

# --- FS2  the fake solver STARTS BUT NEVER WRITES ---------------------------
say ""
say "FS2  fake solver STARTS BUT NEVER WRITES.  Expect launched: false (89) + kill."
reset_stub; stage_tree "$W"
PRE="$TMP/pre2.tsv"; ROWS=$(la_capture_pre "$W" "$PRE")
start_fake_solver "$W" silent
la_assert_launch cid_fs2 3 "$TMP"; RC=$?
check "FS2 launch rc (wedged)" 89 "$RC"
case "$LA_REASON" in *never_started_wedged*) check "FS2 reason" yes yes ;; *) check "FS2 reason" yes "no [$LA_REASON]" ;; esac
if la_mtime_witness "$W" "$PRE"; then MW=advanced; else MW=unchanged_since_capture; fi
check "FS2 mtime witness sees NOTHING written" unchanged_since_capture "$MW"
KRES=$(la_kill cid_fs2 "$TMP/e_fs2")
check "FS2 L-540 kill invoked" 1 "$(kills_seen)"
check "FS2 kill verified: the process is really gone" killed "$KRES"
stop_fake_solver

# --- FS3  NO SOLVER AT ALL, staged files present with plausible mtimes ------
#     THIS IS cfd's EXACT DEFECT.  `mtime >= t_launch - slack` PASSES HERE.
say ""
say "FS3  NO SOLVER AT ALL -- staged files present, mtimes NOW, nothing runs."
say "     This is the case cfd's stage-4 witness CONFIRMED.  It must REFUSE."
reset_stub; stage_tree "$W"
PRE="$TMP/pre3.tsv"; ROWS=$(la_capture_pre "$W" "$PRE")
start_fake_solver "$W" none          # nothing is launched; log is empty
T_LAUNCH=$(date +%s)
la_assert_launch cid_fs3 3 "$TMP"; RC=$?
check "FS3 log witness REFUSES (no solver ran)" 88 "$RC"
case "$LA_REASON" in *never_started_container_exited*) check "FS3 reason" yes yes ;; *) check "FS3 reason" yes "no [$LA_REASON]" ;; esac
if la_mtime_witness "$W" "$PRE"; then MW=advanced; else MW=unchanged_since_capture; fi
check "FS3 mtime witness REFUSES on staged-only files" unchanged_since_capture "$MW"
# AND THE DIRECT REPRODUCTION OF THE DEFECT, so the control is not vacuous:
# the REJECTED form would have confirmed this very tree.
NAIVE=$(find "$W" -type f -newermt "@$((T_LAUNCH-5))" 2>/dev/null | wc -l | tr -d ' ')
check "FS3 the REJECTED form (mtime >= t_launch - 5s slack) WOULD have confirmed" 5 "$NAIVE"
say "     ^ 5 staged files satisfy the slack form and 0 satisfy the strict form."
stop_fake_solver

# --- FS4  the witness reader itself fails -----------------------------------
say ""
say "FS4  READER FAILURE against a LIVE fake solver that IS writing."
say "     Must be 'could not look' (90), distinguishable from FS2 and FS3."
reset_stub; stage_tree "$W"
PRE="$TMP/pre4.tsv"; ROWS=$(la_capture_pre "$W" "$PRE")
start_fake_solver "$W" writes
FD_LOGS_RC=1                          # docker unreachable / wrong container name
la_assert_launch cid_fs4 8 "$TMP"; RC=$?
check "FS4 launch rc (could not look)" 90 "$RC"
case "$LA_REASON" in *witness_reader_unreadable*) check "FS4 reason distinguishes reader failure" yes yes ;; *) check "FS4 reason" yes "no [$LA_REASON]" ;; esac
check "FS4 rc differs from FS2 (started, never wrote)" different "$([ "$RC" -ne 89 ] && echo different || echo same)"
check "FS4 rc differs from FS3 (no solver at all)"     different "$([ "$RC" -ne 88 ] && echo different || echo same)"
stop_fake_solver
DOCKER=fake_docker

# ===========================================================================
say ""
say "================= D8G LAUNCH-ASSERT SELFTEST ================="
say "pass=$PASS fail=$FAIL"
if [ "$FAIL" -eq 0 ] && [ "$PASS" -ge 40 ]; then
  say "RESULT: PASS -- the assertion was shown to ACCEPT a real witness and to"
  say "REFUSE, with a distinct reason, in four independent ways: wedged (89),"
  say "exited (88), decomposePar-decoy (88), reader-failure (90).  The kill in"
  say "the refusal path was observed, and a kill that did not kill was reported"
  say "as a failure.  SCOPE: docker is a stub; this is not evidence the"
  say "assertion has ever watched a real DAFoam container."
  exit 0
fi
say "RESULT: GATE FAIL -- pass=$PASS fail=$FAIL (a run with fewer than 40 passing"
say "checks is a truncated selftest and is refused rather than reported green)."
exit 1
