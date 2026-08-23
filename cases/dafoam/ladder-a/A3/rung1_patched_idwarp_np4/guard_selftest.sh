#!/usr/bin/env bash
# guard_selftest.sh -- prove the guards can fire, and prove they do not fire when they should not,
# BEFORE any solver arm launches.
#
# CLAUDE.md standing rule 3, applied to a guard rather than to a comparator: "a zero from a reader
# not shown able to see a non-zero is not evidence". A guard that never fires is indistinguishable
# from a guard that CANNOT fire, and rung 2 shipped exactly that (RESULTS.md section 9.1; L-239).
# So each guard is exercised twice here, with a planted condition that MUST trip it and a planted
# condition that MUST NOT, and the arms are blocked until both limbs pass.
#
# THE WIRE: this script writes $ROOT/GUARD_SELFTEST_PASS only when every limb passes. drive.sh
# refuses to launch any arm unless that marker exists AND is newer than every guard script it
# depends on -- so editing a guard invalidates its own licence to run.
#
# Usage: guard_selftest.sh <root> <here>
#   <root> = the run root under /home/ubuntu/certonomous-runs/
#   <here> = the directory holding mem_guard.sh and coloring_guard.sh (this file's directory)
# Cost:  4 short `alpine` containers at --cpus=1; measured ceiling 2.0 core-min, see
#        PREREGISTRATION.md section 8. It starts no solver and touches no case directory.
set -u
if [ "$#" -ne 2 ]; then echo "usage: guard_selftest.sh <root> <here>" >&2; exit 2; fi
ROOT="$1"; HERE="$2"
LOGF="$ROOT/guard_selftest.log"
mkdir -p "$ROOT"
PASS=1
say() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOGF"; }
fail() { say "LIMB FAILED: $*"; PASS=0; }

rm -f "$ROOT/GUARD_SELFTEST_PASS"
say "=== guard selftest begins. Nothing here is a solver; no case directory is touched. ==="

# ---------------------------------------------------------------------------
# LIMB 1 (POSITIVE, mem_guard): thresholds that CANNOT be satisfied. The guard must kill.
# ceiling 0.0001 GiB is below any container's RSS; floor 99 GiB is above this box's 30.64 GiB
# MemTotal. Both limbs of the breach test are therefore planted at once.
# ---------------------------------------------------------------------------
sudo -n docker rm -f a3r1_gs_pos >/dev/null 2>&1 || true
sudo -n docker run -d --rm --name a3r1_gs_pos --cpus=1 --memory=256m alpine sleep 300 >/dev/null 2>&1 \
  || { fail "limb 1 could not start its alpine container"; }
sleep 3
T0=$(date -u +%s)
timeout 90 "$HERE/mem_guard.sh" a3r1_gs_pos 0.0001 99 "$ROOT" gs_pos
RC=$?
T1=$(date -u +%s)
sleep 3
if [ "$RC" -ne 4 ]; then fail "limb 1: mem_guard exit $RC, expected 4 (STOP FIRED)"; fi
if [ ! -f "$ROOT/MEMORY_STOP_FIRED.gs_pos" ]; then fail "limb 1: no MEMORY_STOP_FIRED marker written"; fi
if sudo -n docker ps --format '{{.Names}}' | grep -qx a3r1_gs_pos; then
  fail "limb 1: THE CONTAINER IS STILL RUNNING -- the kill path does not work"
  sudo -n docker rm -f a3r1_gs_pos >/dev/null 2>&1 || true
fi
say "limb 1 (positive, mem_guard): exit=$RC elapsed=$((T1-T0))s -- guard fired and the container is gone"

# ---------------------------------------------------------------------------
# LIMB 2 (NEGATIVE, mem_guard): thresholds that CANNOT be breached. The guard must NOT kill.
# A guard that kills unconditionally would pass limb 1 and be worthless.
# ---------------------------------------------------------------------------
sudo -n docker rm -f a3r1_gs_neg >/dev/null 2>&1 || true
sudo -n docker run -d --rm --name a3r1_gs_neg --cpus=1 --memory=256m alpine sleep 300 >/dev/null 2>&1 \
  || { fail "limb 2 could not start its alpine container"; }
sleep 3
timeout 45 "$HERE/mem_guard.sh" a3r1_gs_neg 999 0.0001 "$ROOT" gs_neg
RC=$?
if [ "$RC" -ne 124 ]; then fail "limb 2: mem_guard exit $RC, expected 124 (still watching at timeout)"; fi
if [ -f "$ROOT/MEMORY_STOP_FIRED.gs_neg" ]; then fail "limb 2: guard fired on an unbreachable threshold"; fi
if ! sudo -n docker ps --format '{{.Names}}' | grep -qx a3r1_gs_neg; then
  fail "limb 2: the container was killed although no threshold was breached"
else
  say "limb 2 (negative, mem_guard): exit=$RC -- guard correctly did NOT fire; container still alive"
fi
sudo -n docker rm -f a3r1_gs_neg >/dev/null 2>&1 || true

# ---------------------------------------------------------------------------
# LIMB 3 (POSITIVE, coloring_guard): a planted log carrying the REBUILD signature. Must exit 3.
# Note the plant carries BOTH lines, because a real rebuild also prints "Reading Coloring"
# afterwards -- this limb is what proves the guard keys on the right one.
# ---------------------------------------------------------------------------
P="$ROOT/.selftest_rebuild.log"
{ echo "Checking if Coloring file exists.."
  echo "dRdWColoring_4.bin not found."
  echo "Calculating dRdW Coloring... 420.6 s"
  echo "Reading Coloring dRdWColoring_4"
  echo "dRdWTPC: 0 of 1233, ExecutionTime: 15.21 s"; } > "$P"
"$HERE/coloring_guard.sh" a3r1_nonexistent "$P" dRdWColoring_4 1233 "$ROOT" gs_col_pos --no-kill
RC=$?
[ "$RC" -eq 3 ] || fail "limb 3: coloring_guard exit $RC, expected 3 (rebuild detected)"
[ -f "$ROOT/COLORING_REBUILD_DETECTED.gs_col_pos" ] || fail "limb 3: no rebuild marker written"
say "limb 3 (positive, coloring_guard): exit=$RC -- rebuild detected through a masking 'Reading Coloring' line"

# ---------------------------------------------------------------------------
# LIMB 4 (NEGATIVE, coloring_guard): the genuine warm-cache signature of the rung-1 shipped arm,
# copied verbatim from A3-onera-m6-sweep-n15_21840/fd3_run.log:836,837,844,848. Must exit 0.
# ---------------------------------------------------------------------------
P="$ROOT/.selftest_warm.log"
{ echo "Checking if Coloring file exists.."
  echo "dRdWColoring_4.bin exists."
  echo "Reading Coloring dRdWColoring_4"
  echo "Validating Coloring..."
  echo "dRdWTPC: 0 of 1233, ExecutionTime: 15.21 s"; } > "$P"
"$HERE/coloring_guard.sh" a3r1_nonexistent "$P" dRdWColoring_4 1233 "$ROOT" gs_col_neg --no-kill
RC=$?
[ "$RC" -eq 0 ] || fail "limb 4: coloring_guard exit $RC, expected 0 (warm cache confirmed)"
say "limb 4 (negative, coloring_guard): exit=$RC -- warm cache confirmed, no fire"

# ---------------------------------------------------------------------------
# LIMB 5 (DISCRIMINATION, coloring_guard): the warm signature but the WRONG colour count. Must exit 5.
# ---------------------------------------------------------------------------
P="$ROOT/.selftest_wrongcolours.log"
{ echo "Checking if Coloring file exists.."
  echo "Reading Coloring dRdWColoring_4"
  echo "dRdWTPC: 0 of 1355, ExecutionTime: 15.21 s"; } > "$P"
"$HERE/coloring_guard.sh" a3r1_nonexistent "$P" dRdWColoring_4 1233 "$ROOT" gs_col_cnt --no-kill
RC=$?
[ "$RC" -eq 5 ] || fail "limb 5: coloring_guard exit $RC, expected 5 (colour-count mismatch)"
say "limb 5 (discrimination, coloring_guard): exit=$RC -- a rung-3 colour count (1355) is rejected at rung 1"

# ---------------------------------------------------------------------------
if [ "$PASS" = "1" ]; then
  { echo "GUARD SELFTEST PASS $(date -u +%FT%TZ)"
    echo "mem_guard.sh md5      $(md5sum "$HERE/mem_guard.sh" | awk '{print $1}')"
    echo "coloring_guard.sh md5 $(md5sum "$HERE/coloring_guard.sh" | awk '{print $1}')"
    echo "limbs: 1 POS-mem FIRED+killed, 2 NEG-mem silent, 3 POS-col rebuild, 4 NEG-col warm, 5 colour-count"; } \
    > "$ROOT/GUARD_SELFTEST_PASS"
  say "=== GUARD SELFTEST PASS -- arms may launch ==="
  exit 0
fi
say "=== GUARD SELFTEST FAILED -- NO ARM MAY LAUNCH. This is BLOCKED, not a result. ==="
exit 1
