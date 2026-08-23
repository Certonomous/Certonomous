#!/usr/bin/env bash
# guard_selftest.sh -- prove the guards can fire, prove they do not fire when they should not, and
# prove the identity comparator can SEE a difference, all BEFORE any solver arm launches.
#
# CLAUDE.md standing rule 3, applied to guards and to a comparator: "a zero from a reader not shown
# able to see a non-zero is not evidence". A guard that never fires is indistinguishable from a
# guard that CANNOT fire, and A3 rung 2 shipped exactly that
# (../rung2_patched_idwarp_np4/RESULTS.md section 9.1; L-239). Rung 3's central claim is a NEGATIVE
# one -- "the patched residual path is indistinguishable from the shipped one" -- so the comparator
# that produces it must be shown able to distinguish paths before it is believed.
#
# THE WIRE: this script writes $ROOT/GUARD_SELFTEST_PASS only when every limb passes. drive.sh
# refuses to launch the arm unless that marker exists AND is newer than every guard script it
# depends on -- so editing a guard invalidates its own licence to run.
#
# Usage: guard_selftest.sh <root> <here>
# Cost:  2 short `alpine` containers at --cpus=1 plus file-only limbs; measured ceiling 2.0
#        core-min, see PREREGISTRATION.md section 8. It starts no solver and touches no case dir.
set -u
if [ "$#" -ne 2 ]; then echo "usage: guard_selftest.sh <root> <here>" >&2; exit 2; fi
ROOT="$1"; HERE="$2"
LOGF="$ROOT/guard_selftest.log"
SHIPPED_LOG=/home/ubuntu/certonomous-runs/A3-rung3-n52/rung3_stage1.log
CKPT="$HERE/shipped_cd_checkpoints.txt"
CONV=1.0e-03
mkdir -p "$ROOT"
PASS=1
say() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOGF"; }
fail() { say "LIMB FAILED: $*"; PASS=0; }

rm -f "$ROOT/GUARD_SELFTEST_PASS"
say "=== guard selftest begins. Nothing here is a solver; no case directory is touched. ==="

# ---------------------------------------------------------------------------
# LIMB 1 (POSITIVE, mem_guard): thresholds that CANNOT be satisfied. The guard must kill.
# ---------------------------------------------------------------------------
sudo -n docker rm -f a3r3_gs_pos >/dev/null 2>&1 || true
sudo -n docker run -d --rm --name a3r3_gs_pos --cpus=1 --memory=256m alpine sleep 300 >/dev/null 2>&1 \
  || fail "limb 1 could not start its alpine container"
sleep 3
timeout 90 "$HERE/mem_guard.sh" a3r3_gs_pos 0.0000001 99 "$ROOT" gs_pos
RC=$?
sleep 3
[ "$RC" -eq 4 ] || fail "limb 1: mem_guard exit $RC, expected 4 (STOP FIRED)"
[ -f "$ROOT/MEMORY_STOP_FIRED.gs_pos" ] || fail "limb 1: no MEMORY_STOP_FIRED marker written"
if sudo -n docker ps --format '{{.Names}}' | grep -qx a3r3_gs_pos; then
  fail "limb 1: THE CONTAINER IS STILL RUNNING -- the kill path does not work"
  sudo -n docker rm -f a3r3_gs_pos >/dev/null 2>&1 || true
fi
say "limb 1 (positive, mem_guard): exit=$RC -- guard fired and the container is gone"

# ---------------------------------------------------------------------------
# LIMB 2 (NEGATIVE, mem_guard): thresholds that CANNOT be breached. The guard must NOT kill.
# ---------------------------------------------------------------------------
sudo -n docker rm -f a3r3_gs_neg >/dev/null 2>&1 || true
sudo -n docker run -d --rm --name a3r3_gs_neg --cpus=1 --memory=256m alpine sleep 300 >/dev/null 2>&1 \
  || fail "limb 2 could not start its alpine container"
sleep 3
timeout 45 "$HERE/mem_guard.sh" a3r3_gs_neg 999 0.0001 "$ROOT" gs_neg
RC=$?
[ "$RC" -eq 124 ] || fail "limb 2: mem_guard exit $RC, expected 124 (still watching at timeout)"
[ -f "$ROOT/MEMORY_STOP_FIRED.gs_neg" ] && fail "limb 2: guard fired on an unbreachable threshold"
if ! sudo -n docker ps --format '{{.Names}}' | grep -qx a3r3_gs_neg; then
  fail "limb 2: the container was killed although no threshold was breached"
else
  say "limb 2 (negative, mem_guard): exit=$RC -- guard correctly did NOT fire; container still alive"
fi
sudo -n docker rm -f a3r3_gs_neg >/dev/null 2>&1 || true

# ---------------------------------------------------------------------------
# LIMB 3 (POSITIVE, coloring_guard): a planted log carrying the REBUILD signature, WITH the masking
# "Reading Coloring" line a real rebuild also prints. Must exit 3.
# ---------------------------------------------------------------------------
P="$ROOT/.selftest_rebuild.log"
{ echo "Checking if Coloring file exists.."
  echo "Calculating dRdW Coloring... 900.0 s"
  echo "Reading Coloring dRdWColoring_4"
  echo "dRdWTPC: 0 of 1355, ExecutionTime: 49.24 s"; } > "$P"
"$HERE/coloring_guard.sh" a3r3_nonexistent "$P" dRdWColoring_4 1355 "$ROOT" gs_col_pos --no-kill
RC=$?
[ "$RC" -eq 3 ] || fail "limb 3: coloring_guard exit $RC, expected 3 (rebuild detected)"
say "limb 3 (positive, coloring_guard): exit=$RC -- rebuild detected through a masking 'Reading Coloring' line"

# ---------------------------------------------------------------------------
# LIMB 4 (NEGATIVE, coloring_guard): the genuine warm-cache signature of the shipped rung-3 arm,
# copied verbatim from A3-rung3-n52/rung3_stage1.log:835,836,843,844,847. Must exit 0.
# ---------------------------------------------------------------------------
P="$ROOT/.selftest_warm.log"
{ echo "Checking if Coloring file exists.."
  echo "dRdWColoring_4.bin exists."
  echo "Reading Coloring dRdWColoring_4"
  echo "Validating Coloring..."
  echo "dRdWTPC: 0 of 1355, ExecutionTime: 49.24 s"; } > "$P"
"$HERE/coloring_guard.sh" a3r3_nonexistent "$P" dRdWColoring_4 1355 "$ROOT" gs_col_neg --no-kill
RC=$?
[ "$RC" -eq 0 ] || fail "limb 4: coloring_guard exit $RC, expected 0 (warm cache confirmed)"
say "limb 4 (negative, coloring_guard): exit=$RC -- warm cache confirmed, no fire"

# ---------------------------------------------------------------------------
# LIMB 5 (DISCRIMINATION, coloring_guard): the warm signature with rung 1's colour count. Must exit 5.
# ---------------------------------------------------------------------------
P="$ROOT/.selftest_wrongcolours.log"
{ echo "Reading Coloring dRdWColoring_4"; echo "dRdWTPC: 0 of 1233, ExecutionTime: 15.21 s"; } > "$P"
"$HERE/coloring_guard.sh" a3r3_nonexistent "$P" dRdWColoring_4 1355 "$ROOT" gs_col_cnt --no-kill
RC=$?
[ "$RC" -eq 5 ] || fail "limb 5: coloring_guard exit $RC, expected 5 (colour-count mismatch)"
say "limb 5 (discrimination, coloring_guard): exit=$RC -- a rung-1 colour count (1233) is rejected at rung 3"

# ---------------------------------------------------------------------------
# LIMB 6 (THE PLANTED-DIFFERENCE CONTROL, part A -- identity_stop must report MATCH on the real
# thing). Read against the actual shipped rung-3 log this arm is compared to. Must exit 5.
# This limb also proves the comparator can parse genuine DAFoam output, not just planted text.
# ---------------------------------------------------------------------------
if [ ! -f "$SHIPPED_LOG" ]; then
  fail "limb 6: the shipped rung-3 log $SHIPPED_LOG is MISSING -- the comparator has no reference and NO ARM MAY RUN"
else
  "$HERE/identity_stop.sh" a3r3_nonexistent "$SHIPPED_LOG" "$CKPT" "$CONV" "$ROOT" gs_id_match --no-kill
  RC=$?
  [ "$RC" -eq 5 ] || fail "limb 6: identity_stop exit $RC on the shipped log itself, expected 5 (identity confirmed)"
  [ -f "$ROOT/IDENTITY_CONFIRMED.gs_id_match" ] || fail "limb 6: no IDENTITY_CONFIRMED marker written"
  say "limb 6 (identity_stop, MATCH on the real shipped log): exit=$RC"
fi

# ---------------------------------------------------------------------------
# LIMB 7 (THE PLANTED-DIFFERENCE CONTROL, part B -- the comparator must SEE a difference).
# Planted with A3 RUNG 2's real CD adjoint path (A3-rung2-n28-tpc1/fd3_run.log:863-864): a genuine
# DAFoam residual path from the same solver and case family that differs from rung 3's in the 5th
# significant figure at iteration 0. A comparator that cannot see this cannot certify a match.
# Must exit 6 (DIVERGED: the value differs and is still above the converging threshold).
# ---------------------------------------------------------------------------
P="$ROOT/.selftest_rung2path.log"
{ echo "Main iteration 0 KSP Residual norm 2.121211553380e-02 80.36 s. "
  echo "Main iteration 100 KSP Residual norm 1.248117871596e-02 94.66 s. "; } > "$P"
"$HERE/identity_stop.sh" a3r3_nonexistent "$P" "$CKPT" "$CONV" "$ROOT" gs_id_differ --no-kill
RC=$?
[ "$RC" -eq 6 ] || fail "limb 7: identity_stop exit $RC on a KNOWN-DIFFERENT path, expected 6 (DIVERGED). THE COMPARATOR IS BLIND."
[ -f "$ROOT/PATH_DIVERGED.gs_id_differ" ] || fail "limb 7: no PATH_DIVERGED marker written"
say "limb 7 (identity_stop, planted difference from rung 2's real path): exit=$RC -- the comparator sees it"

# ---------------------------------------------------------------------------
# LIMB 8 (THE STAND-DOWN, identity_stop): a path that matches at iteration 0 and then drops BELOW
# the converging threshold. The guard must NOT kill -- a patched adjoint that actually converges at
# rung 3 is the largest result this arm could produce and must survive its own guard.
# Must exit 7 (single-pass: stood down, no decision to act on).
# ---------------------------------------------------------------------------
P="$ROOT/.selftest_converging.log"
{ echo "Main iteration 0 KSP Residual norm 2.121343646203e-02 151.36 s. "
  echo "Main iteration 100 KSP Residual norm 5.000000000000e-04 178.14 s. "; } > "$P"
"$HERE/identity_stop.sh" a3r3_nonexistent "$P" "$CKPT" "$CONV" "$ROOT" gs_id_conv --no-kill
RC=$?
[ "$RC" -eq 7 ] || fail "limb 8: identity_stop exit $RC on a converging path, expected 7 (stood down)"
[ -f "$ROOT/PATH_CONVERGING.gs_id_conv" ] || fail "limb 8: no PATH_CONVERGING marker written"
[ -f "$ROOT/PATH_DIVERGED.gs_id_conv" ] && fail "limb 8: the guard treated a CONVERGING path as a divergence and would have killed it"
say "limb 8 (identity_stop, stand-down on a converging path): exit=$RC -- guard correctly did NOT fire"

# ---------------------------------------------------------------------------
if [ "$PASS" = "1" ]; then
  { echo "GUARD SELFTEST PASS $(date -u +%FT%TZ)"
    echo "mem_guard.sh md5                 $(md5sum "$HERE/mem_guard.sh" | awk '{print $1}')"
    echo "coloring_guard.sh md5            $(md5sum "$HERE/coloring_guard.sh" | awk '{print $1}')"
    echo "identity_stop.sh md5             $(md5sum "$HERE/identity_stop.sh" | awk '{print $1}')"
    echo "shipped_cd_checkpoints.txt md5   $(md5sum "$CKPT" | awk '{print $1}')"
    echo "limbs: 1 POS-mem, 2 NEG-mem, 3 POS-col, 4 NEG-col, 5 col-count, 6 ID-match-on-real-log,"
    echo "       7 ID-sees-planted-difference, 8 ID-stands-down-on-convergence"; } \
    > "$ROOT/GUARD_SELFTEST_PASS"
  say "=== GUARD SELFTEST PASS -- the arm may launch ==="
  exit 0
fi
say "=== GUARD SELFTEST FAILED -- NO ARM MAY LAUNCH. This is BLOCKED, not a result. ==="
exit 1
