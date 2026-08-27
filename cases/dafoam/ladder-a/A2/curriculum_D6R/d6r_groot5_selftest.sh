#!/usr/bin/env bash
# D6R G-ROOT.5 SELFTEST -- the D6/D4-SHIPPED pattern, driven against D6R's OWN
# launcher, WITH ONE REGISTERED DEPARTURE FROM THE PREDECESSOR:
#
#   D6 PROVED CLAUSE (a) BY STARTING A SACRIFICIAL CONTAINER.  D6R DOES NOT
#   CREATE A CONTAINER AT ALL.  The supervisor's bound on this registration is
#   LAUNCH NOTHING / prove zero containers created, and D8R is live on this box
#   (d8r_O-P_20260827T223101Z_1595223, cpuset 0,1,12,15, 14g) and must not be
#   disturbed.  Clause (a) is therefore driven in TWO halves, which together
#   are STRONGER than a sacrificial container, not weaker:
#     (a0) THE READER IS SHOWN ABLE TO SEE A NON-ZERO.  `docker ps` is read
#          READ-ONLY and must return at least one live container name.  A guard
#          whose reader has not been shown able to see a non-zero is not
#          evidence (CLAUDE.md rule 3).
#     (a1) THE REAL LAUNCHER BYTES ARE DRIVEN THROUGH THE REAL BRANCH with a
#          PLANTED container name, via a `sudo` shim on PATH.  rc=3 expected.
#     (a2) THE NEGATIVE CONTROL: the same shim with an UNRELATED name -- the
#          clause must NOT fire, and control must reach the L-251 abort.  A
#          positive branch proved only by the ORDER of refusals, never by
#          executing the protected path.
#
# (b) a LIVE HOST pid (not a container) whose cwd is the run root, named in the
#     driver pidfile; (b2) a STALE pidfile must not block; (c) clear must pass;
# (d) D4's, D4-SHIPPED's, D5's, D6's and D8R's roots refuse at G-ROOT.1.
# SAFETY: every invocation passes a BOGUS IMAGE NAME and the run root is a
# temporary EMPTY directory (mode 775), so a launcher that got past G-ROOT.5
# aborts at the L-251 mode check (exit 4) BEFORE any staging.  The temporary
# root is removed with rmdir (refuses a non-empty directory) and its ABSENCE
# afterwards is asserted -- the freeze condition of PREREGISTRATION.md section 8.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; L="$HERE/d6r_run_arm.sh"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint
BOGUS=no-such-image:selftest; ARM=ACC_mp
SHIM=$(mktemp -d)
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "D6R G-ROOT.5 SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) launcher_md5=$(md5sum "$L" | cut -d' ' -f1)"

CONTAINERS_BEFORE=$(sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | wc -l)
echo "  containers_before=$CONTAINERS_BEFORE"

G5=$(grep -n 'G_ROOT5_PASS' "$L" | head -1 | cut -d: -f1)
FIRSTOP=$(grep -nE '^[[:space:]]*[^#]*((sudo -n )?rm -rf|cp -a|docker run)' "$L" | grep -v '^[0-9]*:[[:space:]]*#' | head -1 | cut -d: -f1)
if [ -n "$G5" ] && [ -n "$FIRSTOP" ] && [ "$FIRSTOP" -gt "$G5" ]; then ok "G-ROOT.5 completes at :$G5, first destructive op at :$FIRSTOP"; else bad "order G5=$G5 FIRSTOP=$FIRSTOP"; exit 2; fi
CAPL=$(grep -n '^FRAME_ALLOWANCE_S=90' "$L" | head -1 | cut -d: -f1)
if [ -n "$CAPL" ] && [ "$FIRSTOP" -gt "$CAPL" ]; then ok "the CAP FRAME assertion at :$CAPL also precedes the first destructive op at :$FIRSTOP"; else bad "cap frame order CAPL=$CAPL FIRSTOP=$FIRSTOP"; fi
NBT=$(grep -vE '^[[:space:]]*#' "$L" | grep -c '`' || true)
if [ "$NBT" = "0" ]; then ok "zero backticks on executable lines of the launcher"; else bad "$NBT backticks on executable lines"; fi
if grep -q '__D6R\?_' "$L"; then bad "launcher still carries an unfilled placeholder"; exit 2; else ok "no unfilled md5 placeholder in the launcher"; fi
if [ -e "$BASE" ]; then bad "run root $BASE already EXISTS -- refusing to test over a real root (freeze condition violated)"; exit 2; else ok "run root ABSENT before the test: $BASE"; fi
mkdir -p "$BASE" || { bad "could not create the temporary empty run root"; exit 2; }

# ---- (a0) THE READER, SHOWN ABLE TO SEE A NON-ZERO ------------------------
LIVE_NOW=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | tr '\n' ',' | sed 's/,$//')
LIVE_N=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | wc -l)
if [ "$LIVE_N" -ge 1 ]; then ok "(a0) PLANTED POSITIVE FOR THE READER: docker ps returns $LIVE_N live container(s) [$LIVE_NOW] -- the reader is NOT blind"; else bad "(a0) docker ps returned nothing; the reader cannot be shown able to see a non-zero"; fi

# ---- (a1) THE REAL LAUNCHER, REAL BRANCH, PLANTED NAME, ZERO CONTAINERS ----
PLANT_NAME="d6r_${ARM}_planted_20260827T000000Z_999999"
cat > "$SHIM/sudo" <<SH
#!/usr/bin/env bash
# selftest shim: intercepts ONLY \`docker ps\`; everything else is refused so a
# stray daemon call cannot slip past unnoticed.
if [ "\${1:-}" = "-n" ]; then shift; fi
if [ "\${1:-}" = "docker" ] && [ "\${2:-}" = "ps" ]; then echo "\$PLANTED_NAMES"; exit 0; fi
echo "SHIM REFUSED: \$*" >&2; exit 97
SH
chmod +x "$SHIM/sudo"
out=$(PATH="$SHIM:$PATH" PLANTED_NAMES="$PLANT_NAME" bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 a RUNNING container"; then ok "(a1) planted live container [$PLANT_NAME] -> rc=3: $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-110)"; else bad "(a1) rc=$rc: $(echo "$out" | tail -2)"; fi
out=$(PATH="$SHIM:$PATH" PLANTED_NAMES="d8r_O-P_unrelated_container" bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "G_ROOT5_PASS" && echo "$out" | grep -q "ABORT L-251 run root mode"; then ok "(a2) NEGATIVE CONTROL: an UNRELATED live container does NOT fire the clause; control reaches the L-251 abort (rc=4), nothing staged"; else bad "(a2) rc=$rc: $(echo "$out" | tail -2)"; fi

# ---- (b) a LIVE HOST pid whose cwd is the run root ------------------------
( cd "$BASE" && exec sleep 120 ) & SPID=$!
echo "$SPID" > "$BASE/d6r_driver.pid"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 driver pidfile"; then ok "(b) live HOST pid $SPID cwd=$BASE -> rc=3: $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-130)"; else bad "(b) rc=$rc: $(echo "$out" | tail -2)"; fi
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null; rm -f "$BASE/d6r_driver.pid"
echo "999999" > "$BASE/d6r_driver.pid"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "G_ROOT5_PASS" && echo "$out" | grep -q "ABORT L-251 run root mode"; then ok "(b2) stale pidfile ignored; launcher went on to abort at the L-251 mode check (rc=4) -- nothing staged"; else bad "(b2) rc=$rc: $(echo "$out" | tail -2)"; fi
rm -f "$BASE/d6r_driver.pid"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "G_ROOT5_PASS"; then ok "(c) clear -> G-ROOT.5 passes; L-251 mode check aborts (rc=4) before any staging"; else bad "(c) rc=$rc"; fi
if echo "$out" | grep -q "D4S_CAP_FRAME arm=$ARM .* deadline_in_container_s=360 frame_allowance_s=90 worst_case_host_core_min=30.000000"; then ok "(c2) the CAP FRAME line is emitted BEFORE the abort: ACC_mp deadline 360 s + 90 s allowance INVERTS to the registered 30.0 core-min"; else bad "(c2) cap frame line: $(echo "$out" | grep D4S_CAP_FRAME | cut -c1-160)"; fi
for forb in /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin /home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin /home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density /home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint /home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv; do
  out=$(BASE="$forb" bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.1"; then ok "(d) BASE=$forb -> rc=3 G-ROOT.1 REFUSED"; else bad "(d) $forb rc=$rc"; fi
done
N=$(find "$BASE" -mindepth 1 | wc -l)
if [ "$N" = "0" ]; then ok "temporary run root still EMPTY after every invocation ($N entries)"; else bad "run root gained $N entries"; fi
rmdir "$BASE" 2>/dev/null
if [ ! -e "$BASE" ]; then ok "run root ABSENT after the test (freeze condition): test -e $BASE -> false"; else bad "run root still present"; fi
rm -rf "$SHIM"
CONTAINERS_AFTER=$(sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | wc -l)
if [ "$CONTAINERS_AFTER" = "$CONTAINERS_BEFORE" ]; then ok "ZERO CONTAINERS CREATED: $CONTAINERS_BEFORE before, $CONTAINERS_AFTER after"; else bad "container count moved $CONTAINERS_BEFORE -> $CONTAINERS_AFTER"; fi
echo "D6R G-ROOT5 SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
