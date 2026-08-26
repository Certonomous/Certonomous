#!/usr/bin/env bash
# SELFTEST for dafoam_wait_then_launch.sh -- every refusal is DRIVEN, never assumed
# (CLAUDE.md rule 3: a zero from a reader not shown able to see a non-zero is not
# evidence).  Sacrificial objects only: a throwaway run root under
# /home/ubuntu/certonomous-runs/_dwtl_selftest_<stamp> (removed at the end), a
# sacrificial `sleep` container carrying a selftest-only name prefix on cpu 14 at
# 64 MiB, and a sacrificial `sleep` pid whose cwd is the throwaway root.  No
# registered run root, launcher, container or entry is touched.  The launcher argv
# under test is `true` / `bash -c 'exit 7'` -- zero compute.
# Legs:
#   L0  bash -n on the wrapper and on this file; `assert` count 0 with a planted
#       positive showing the counter can see one (L-332)
#   L1  artifact ABSENT -> WAIT lines -> artifact PRESENT -> G-ROOT.5 pass -> `true`
#       executed, rc 0 captured and labelled LAUNCHER_EXIT
#   L1b launcher exit 7 passes through as rc 7, labelled
#   L2  G-ROOT.5 (a): sacrificial RUNNING container with the prefix -> rc 3
#   L3  G-ROOT.5 (b): sacrificial LIVE pid, cwd = run root, named in driver.pid -> rc 3
#   L3b STALE driver.pid (dead pid) does NOT block -> rc 0
#   L4  BOUND reached with the artifact absent -> rc 6, series recorded, no launch
#   L5  DUPLICATE wrapper for the same case id -> rc 3 while the first still waits
#   L6  usage: missing arguments -> rc 64
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; W="$HERE/dafoam_wait_then_launch.sh"
IMG=dafoam/opt-packages:latest
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
ROOT="/home/ubuntu/certonomous-runs/_dwtl_selftest_$STAMP"
CASEDIR="$ROOT/casedir"; RUNROOT="$ROOT/runroot"
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "DWTL SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) wrapper_md5=$(md5sum "$W" | cut -d' ' -f1) sacrificial_root=$ROOT"
mkdir -p "$CASEDIR" "$RUNROOT" || { bad "cannot create sacrificial root"; exit 2; }

# ---- L0
if bash -n "$W" && bash -n "$0"; then ok "L0 bash -n clean on wrapper and selftest"; else bad "L0 bash -n"; fi
# code lines only: the wrapper's HEADER names L-332 by the word `assert`, which is prose, not a statement
NA=$(grep -v '^[[:space:]]*#' "$W" | grep -cw 'assert'); NP=$(printf 'x\nassert y\n# assert in a comment\n' | grep -v '^[[:space:]]*#' | grep -cw 'assert')
if [ "$NA" -eq 0 ] && [ "$NP" -eq 1 ]; then ok "L0 assert count in wrapper code lines = 0; planted positive counted = $NP (the counter can see one, and ignores a commented one)"; else bad "L0 assert count=$NA planted=$NP"; fi

run_wrapper () {   # $1 case_id, $2 precondition, $3 prefix, $4 deadline, then argv
  local cid="$1" pre="$2" pfx="$3" dl="$4"; shift 4
  ( cd "$CASEDIR" && bash "$W" --case-id "$cid" --precondition "$pre" --prefix "$pfx" --run-root "$RUNROOT" --deadline-s "$dl" --poll-s 1 -- "$@" )
}

# ---- L1 absent -> wait -> present -> true
PRE="$RUNROOT/step_plan.selftest.json"; rm -f "$PRE"
( sleep 3; echo '{"selftest": true}' > "$PRE" ) &
out=$(run_wrapper L1 "$PRE" "dwtl_selftest_" 30 true 2>&1); rc=$?
NW=$(grep -c 'event=WAIT ' "$CASEDIR/STATUS.L1" 2>/dev/null || echo 0)
if [ "$rc" -eq 0 ] && [ "$NW" -ge 1 ] && grep -q 'event=PRECONDITION_PRESENT' "$CASEDIR/STATUS.L1" && grep -q 'event=GROOT5_PASS' "$CASEDIR/STATUS.L1" && grep -q '^stamp=.* rc=0 event=LAUNCHER_EXIT .*NOT-the-solver-rc' "$CASEDIR/STATUS.L1" && cmp -s "$CASEDIR/STATUS.L1" "$CASEDIR/WRAPPER.L1.log"; then
  ok "L1 absent->present: rc=$rc, WAIT lines=$NW, PRECONDITION_PRESENT, GROOT5_PASS, LAUNCHER_EXIT rc=0 labelled; STATUS == WRAPPER log"
else bad "L1 rc=$rc waits=$NW: $(tail -2 "$CASEDIR/STATUS.L1" 2>/dev/null)"; fi
wait

# ---- L1b launcher rc passes through
out=$(run_wrapper L1b "$PRE" "dwtl_selftest_" 5 bash -c 'exit 7' 2>&1); rc=$?
if [ "$rc" -eq 7 ] && grep -q ' rc=7 event=LAUNCHER_EXIT ' "$CASEDIR/STATUS.L1b"; then ok "L1b launcher exit 7 -> wrapper rc=7, labelled LAUNCHER_EXIT"; else bad "L1b rc=$rc"; fi

# ---- L2 G-ROOT.5 (a): sacrificial RUNNING container carrying the prefix
CN="dwtl_selftest_${STAMP}"
if sudo -n docker run -d --name "$CN" --cpus=0.1 --cpuset-cpus=14 --memory=64m --memory-swap=64m "$IMG" bash -c "sleep 120" >/dev/null 2>&1; then
  out=$(run_wrapper L2 "$PRE" "dwtl_selftest_" 5 true 2>&1); rc=$?
  if [ "$rc" -eq 3 ] && grep -q "event=GROOT5_REFUSED clause=a live_containers_with_prefix=\[$CN" "$CASEDIR/STATUS.L2" && ! grep -q 'event=LAUNCH ' "$CASEDIR/STATUS.L2"; then
    ok "L2 G-ROOT.5(a) live container $CN -> rc=3, named, nothing launched"; else bad "L2 rc=$rc: $(tail -1 "$CASEDIR/STATUS.L2" 2>/dev/null)"; fi
  sudo -n docker rm -f "$CN" >/dev/null 2>&1
else bad "L2 could not start the sacrificial container"; fi

# ---- L3 G-ROOT.5 (b): sacrificial LIVE pid, cwd = run root, named in driver.pid
( cd "$RUNROOT" && exec sleep 120 ) & SPID=$!
echo "$SPID" > "$RUNROOT/driver.pid"
out=$(run_wrapper L3 "$PRE" "dwtl_selftest_" 5 true 2>&1); rc=$?
if [ "$rc" -eq 3 ] && grep -q "event=GROOT5_REFUSED clause=b driver_pidfile=$RUNROOT/driver.pid live_pid=$SPID" "$CASEDIR/STATUS.L3" && ! grep -q 'event=LAUNCH ' "$CASEDIR/STATUS.L3"; then
  ok "L3 G-ROOT.5(b) live pid $SPID cwd=$RUNROOT in driver.pid -> rc=3, nothing launched"; else bad "L3 rc=$rc: $(tail -1 "$CASEDIR/STATUS.L3" 2>/dev/null)"; fi
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null

# ---- L3b STALE driver.pid must not block
echo "999999" > "$RUNROOT/driver.pid"
out=$(run_wrapper L3b "$PRE" "dwtl_selftest_" 5 true 2>&1); rc=$?
if [ "$rc" -eq 0 ] && grep -q 'event=GROOT5_PASS .*state=present_stale_dead_pid_999999' "$CASEDIR/STATUS.L3b"; then ok "L3b stale driver.pid (999999) ignored -> rc=0"; else bad "L3b rc=$rc"; fi
rm -f "$RUNROOT/driver.pid"

# ---- L4 the bound: artifact absent for the whole deadline -> rc 6, series on record
PRE4="$RUNROOT/never_written.json"; rm -f "$PRE4"
out=$(run_wrapper L4 "$PRE4" "dwtl_selftest_" 3 true 2>&1); rc=$?
NW=$(grep -c 'event=WAIT ' "$CASEDIR/STATUS.L4" 2>/dev/null || echo 0)
if [ "$rc" -eq 6 ] && [ "$NW" -ge 3 ] && grep -q 'rc=6 event=BLOCKED_AT_BOUND .*verdict=BLOCKED' "$CASEDIR/STATUS.L4" && ! grep -q 'event=LAUNCH ' "$CASEDIR/STATUS.L4"; then
  ok "L4 bound reached (deadline 3 s, poll 1 s): rc=6, $NW WAIT lines recorded, BLOCKED, nothing launched"; else bad "L4 rc=$rc waits=$NW"; fi

# ---- L5 duplicate wrapper for one case id is refused while the first waits
PRE5="$RUNROOT/late.json"; rm -f "$PRE5"
( run_wrapper L5 "$PRE5" "dwtl_selftest_" 20 true >/dev/null 2>&1 ) & A=$!
sleep 2
out=$(run_wrapper L5 "$PRE5" "dwtl_selftest_" 5 true 2>&1); rc=$?
if [ "$rc" -eq 3 ] && grep -q 'rc=3 event=DUPLICATE_WRAPPER_REFUSED' "$CASEDIR/STATUS.L5"; then ok "L5 second wrapper for case L5 -> rc=3 DUPLICATE_WRAPPER_REFUSED while the first waits"; else bad "L5 rc=$rc"; fi
echo '{}' > "$PRE5"; wait "$A" 2>/dev/null

# ---- L6 usage
( cd "$CASEDIR" && bash "$W" --case-id X -- true ) >/dev/null 2>&1; rc=$?
if [ "$rc" -eq 64 ]; then ok "L6 missing arguments -> rc=64"; else bad "L6 rc=$rc"; fi

# ---- clean up the sacrificial root; census that nothing else was created
rm -rf "$ROOT"
[ ! -e "$ROOT" ] && ok "sacrificial root removed: $ROOT" || bad "sacrificial root still present"
sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^dwtl_selftest_" && bad "a selftest container survived" || ok "no dwtl_selftest_ container survives"
echo "DWTL SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
