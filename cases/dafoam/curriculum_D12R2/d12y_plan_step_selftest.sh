#!/usr/bin/env bash
# SELFTEST for d12y_plan_step.sh -- every refusal DRIVEN against sacrificial objects only
# (rule 3).  A throwaway root under /home/ubuntu/certonomous-runs/_d12y_planstep_selftest_<stamp>
# (removed at the end), a stand-in "comparator" python file whose blob is passed with --blob/--md5,
# and a sacrificial sleep container carrying a selftest-only prefix on cpu 14 at 64 MiB.  The
# registered root, comparator, launcher and containers are never touched; nothing is run against
# the real run root.  Legs:
#   P0  bash -n; assert count 0 in code lines with a planted positive (L-332)
#   P1  witness ABSENT -> WAIT lines -> PHASE1_COMPLETE line appended -> prefix clear -> blob
#       asserted -> stand-in comparator runs (writes step_plan.json) -> rc 0, labelled COMPARATOR_EXIT
#   P1b the comparator's non-zero rc (2) passes through, labelled
#   P2  blob DRIFT (registered sha deliberately wrong) -> rc 4, nothing run
#   P3  bound reached with the witness absent -> rc 6, series recorded, nothing run
#   P4  a live prefixed container at witness time is WAITED OUT (never refused) -> rc 0 after removal
#   P5  duplicate plan step for the same case id -> rc 3 while the first waits
#   P6  usage: missing --deadline-s / bad mode -> rc 64
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; P="$HERE/d12y_plan_step.sh"
IMG=dafoam/opt-packages:latest
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
ROOT="/home/ubuntu/certonomous-runs/_d12y_planstep_selftest_$STAMP"; RUNROOT="$ROOT/runroot"; CASEDIR="$ROOT/casedir"
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "D12Y_PLAN_STEP SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) planstep_md5=$(md5sum "$P" | cut -d' ' -f1) sacrificial_root=$ROOT"
mkdir -p "$RUNROOT" "$CASEDIR" || { bad "cannot create sacrificial root"; exit 2; }
: > "$RUNROOT/manifest.jsonl"
# the stand-in comparator: writes the artifact the mode names, exits with $STANDIN_RC (default 0)
STANDIN="$ROOT/standin_grade.py"
cat > "$STANDIN" <<'EOF'
import os, sys
root = sys.argv[sys.argv.index("--root") + 1]
mode = [a for a in sys.argv if a.startswith("--plan")][0].lstrip("-")
open(os.path.join(root, "step_" + mode + ".json"), "w").write('{"standin": true}\n')
sys.exit(int(os.environ.get("STANDIN_RC", "0")))
EOF
SBLOB=$(git -C "$HERE" hash-object "$STANDIN"); SMD5=$(md5sum "$STANDIN" | cut -d' ' -f1)
run_step () {  # $1 mode $2 case_id $3 deadline [extra args...]
  local mode="$1" cid="$2" dl="$3"; shift 3
  ( cd "$CASEDIR" && bash "$P" "$mode" --deadline-s "$dl" --case-id "$cid" --poll-s 1 --root "$RUNROOT" --gradepy "$STANDIN" --blob "$SBLOB" --md5 "$SMD5" --prefix "d12yst_" "$@" )
}

# ---- P0
if bash -n "$P" && bash -n "$0"; then ok "P0 bash -n clean"; else bad "P0 bash -n"; fi
NA=$(grep -v '^[[:space:]]*#' "$P" | grep -cw 'assert'); NP=$(printf 'assert y\n# assert c\n' | grep -v '^[[:space:]]*#' | grep -cw 'assert')
if [ "$NA" -eq 0 ] && [ "$NP" -eq 1 ]; then ok "P0 assert count in code lines = 0, planted positive = $NP"; else bad "P0 assert=$NA planted=$NP"; fi

# ---- P1 witness absent -> appended -> run
printf 'STAGE=S0 rc=0\nSTAGE=S1 rc=0\n' > "$RUNROOT/ledger.txt"; rm -f "$RUNROOT/step_plan.json"
( sleep 3; echo 'PHASE1_COMPLETE spent=1.0 core-min' >> "$RUNROOT/ledger.txt" ) &
run_step plan P1 30 >/dev/null 2>&1; rc=$?
NW=$(grep -c 'event=WAIT ' "$CASEDIR/STATUS.P1" 2>/dev/null || echo 0)
if [ "$rc" -eq 0 ] && [ "$NW" -ge 1 ] && grep -q 'event=WITNESS_PRESENT .*line=\[PHASE1_COMPLETE spent=1.0 core-min\]' "$CASEDIR/STATUS.P1" && grep -q 'event=PREFIX_CLEAR' "$CASEDIR/STATUS.P1" && grep -q "event=COMPARATOR_ASSERTED blob=$SBLOB" "$CASEDIR/STATUS.P1" && grep -q ' rc=0 event=COMPARATOR_EXIT .*present=yes' "$CASEDIR/STATUS.P1" && [ -f "$RUNROOT/step_plan.json" ] && cmp -s "$CASEDIR/STATUS.P1" "$CASEDIR/PLANSTEP.P1.log"; then
  ok "P1 witness absent -> $NW waits -> PHASE1_COMPLETE -> prefix clear -> blob asserted -> comparator ran, step_plan.json present, rc=0 labelled; STATUS == PLANSTEP log"; else bad "P1 rc=$rc waits=$NW: $(tail -1 "$CASEDIR/STATUS.P1" 2>/dev/null)"; fi
wait

# ---- P1b comparator rc passes through
echo 'PHASE2_COMPLETE spent=2.0 core-min' >> "$RUNROOT/ledger.txt"
STANDIN_RC=2 run_step plan2 P1b 5 >/dev/null 2>&1; rc=$?
if [ "$rc" -eq 2 ] && grep -q ' rc=2 event=COMPARATOR_EXIT ' "$CASEDIR/STATUS.P1b"; then ok "P1b comparator exit 2 (REFUSAL shape) -> rc=2, labelled COMPARATOR_EXIT"; else bad "P1b rc=$rc"; fi

# ---- P2 blob drift
( cd "$CASEDIR" && bash "$P" plan2 --deadline-s 5 --case-id P2 --poll-s 1 --root "$RUNROOT" --gradepy "$STANDIN" --blob 0000000000000000000000000000000000000000 --md5 "$SMD5" --prefix "d12yst_" ) >/dev/null 2>&1; rc=$?
rm -f "$RUNROOT/step_plan2.json.P2"
if [ "$rc" -eq 4 ] && grep -q 'rc=4 event=COMPARATOR_BLOB_DRIFT' "$CASEDIR/STATUS.P2" && ! grep -q 'event=RUN ' "$CASEDIR/STATUS.P2"; then ok "P2 registered blob deliberately wrong -> rc=4 COMPARATOR_BLOB_DRIFT, nothing run"; else bad "P2 rc=$rc"; fi

# ---- P3 bound
rm -f "$RUNROOT/step_plan3.json"
run_step plan3 P3 3 >/dev/null 2>&1; rc=$?
NW=$(grep -c 'event=WAIT ' "$CASEDIR/STATUS.P3" 2>/dev/null || echo 0)
if [ "$rc" -eq 6 ] && [ "$NW" -ge 3 ] && grep -q 'rc=6 event=BLOCKED_AT_BOUND .*verdict=BLOCKED' "$CASEDIR/STATUS.P3" && ! grep -q 'event=RUN ' "$CASEDIR/STATUS.P3" && [ ! -f "$RUNROOT/step_plan3.json" ]; then ok "P3 bound (3 s, poll 1 s) with PHASE3_COMPLETE absent -> rc=6, $NW WAIT lines, nothing run"; else bad "P3 rc=$rc waits=$NW"; fi

# ---- P4 live prefixed container at witness time is waited out
CN="d12yst_selftest_${STAMP}"
if sudo -n docker run -d --name "$CN" --cpus=0.1 --cpuset-cpus=14 --memory=64m --memory-swap=64m "$IMG" bash -c "sleep 120" >/dev/null 2>&1; then
  ( run_step plan2 P4 30 >/dev/null 2>&1; echo $? > "$ROOT/P4.rc" ) &
  sleep 4; sudo -n docker rm -f "$CN" >/dev/null 2>&1; wait
  rc=$(cat "$ROOT/P4.rc" 2>/dev/null || echo ?); NC=$(grep -c 'event=WAIT_PREFIX_CLEAR ' "$CASEDIR/STATUS.P4" 2>/dev/null || echo 0)
  if [ "$rc" = "0" ] && [ "$NC" -ge 2 ] && grep -q "event=WAIT_PREFIX_CLEAR .*live_containers_with_prefix=\[$CN" "$CASEDIR/STATUS.P4" && grep -q 'event=PREFIX_CLEAR' "$CASEDIR/STATUS.P4" && grep -q ' rc=0 event=COMPARATOR_EXIT ' "$CASEDIR/STATUS.P4"; then ok "P4 live container $CN waited out ($NC WAIT_PREFIX_CLEAR lines), then ran, rc=0 -- never refused"; else bad "P4 rc=$rc clear_waits=$NC: $(tail -1 "$CASEDIR/STATUS.P4" 2>/dev/null)"; fi
else bad "P4 could not start the sacrificial container"; fi

# ---- P5 duplicate
rm -f "$RUNROOT/step_plan3.json"
( run_step plan3 P5 20 >/dev/null 2>&1 ) & A=$!
sleep 2
run_step plan3 P5 5 >/dev/null 2>&1; rc=$?
if [ "$rc" -eq 3 ] && grep -q 'rc=3 event=DUPLICATE_PLANSTEP_REFUSED' "$CASEDIR/STATUS.P5"; then ok "P5 second plan step for case P5 -> rc=3 DUPLICATE_PLANSTEP_REFUSED while the first waits"; else bad "P5 rc=$rc"; fi
echo 'PHASE3_COMPLETE spent=3.0 core-min' >> "$RUNROOT/ledger.txt"; wait "$A" 2>/dev/null

# ---- P6 usage
( cd "$CASEDIR" && bash "$P" plan ) >/dev/null 2>&1; rc1=$?
( cd "$CASEDIR" && bash "$P" plan9 --deadline-s 5 ) >/dev/null 2>&1; rc2=$?
if [ "$rc1" -eq 64 ] && [ "$rc2" -eq 64 ]; then ok "P6 missing --deadline-s -> 64; bad mode -> 64"; else bad "P6 rc1=$rc1 rc2=$rc2"; fi

rm -rf "$ROOT"
[ ! -e "$ROOT" ] && ok "sacrificial root removed: $ROOT" || bad "sacrificial root still present"
sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^d12yst_" && bad "a selftest container survived" || ok "no d12yst_ container survives"
echo "D12Y_PLAN_STEP SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
