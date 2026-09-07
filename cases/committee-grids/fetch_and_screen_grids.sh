#!/bin/bash
# fetch_and_screen_grids.sh -- RUNG 2 grid-family acquisition runner.
#
# Registration: verification/campaign/RUNG2_CRM_GRID_ACQUISITION_PREREGISTRATION.md (v1.1,
#   check 4 GO 2026-09-07). Grader: cases/committee-grids/grade_grid_acq.py (check 1 PASS,
#   git blob 40effb60762597a47f63efd354911f066a4f8dce, sha256 8a4ed26b...e409fdb).
#
# WHAT IT DOES, per level (L2.C then L3.M), and NOTHING ELSE:
#   1. confirms an idle box / no foreign live solver at START (a WAIT, not a stop: exit 3 = HELD,
#      the queue daemon retries later -- RUNG2_CRM_M0 §14.2, "do not race a foreign job");
#   2. fetches the ugrid INBOUND (read-only public download; rule 7 -- inbound only, nothing sent),
#      byte count captured;
#   3. runs the §4.A TITLE-PAGE admission FIRST, via grade_grid_acq.py's title_page_check path
#      (imported, not reimplemented). A file that FAILS admission (short read, lookalike, wrong level)
#      is DISCARDED and NEVER CONVERTED -- no conversion core-minutes are spent on a bad grid;
#   4. converts each ADMITTED ugrid with the committed, Rung-0b-PASSed ugrid_to_foam.py (unmodified);
#   5. runs checkMesh, writing the per-level log (its own mesh VERDICT is never read -- L-459);
#   6. invokes grade_grid_acq.py --grade <level> <ugrid> <checkMesh_log> <birth_cert.json> to write
#      the birth certificate and the FINDING (screen_clears_hard_gates true/false).
#
# THE CAP IS STRUCTURAL (registration §6/§7: 30.0 core-min). At ranks = 1 that is 1800 wall s,
# enforced by a `timeout` budget RECOMPUTED BEFORE EVERY STEP from one total. An overrun STOPS THE
# RUN; it does not get a new budget (CLAUDE.md rule 12). A cap nothing enforces is not a cap.
#
# rc IS CAPTURED INSIDE THIS SCRIPT, immediately after each step, never around a `setsid` line:
# `setsid timeout cmd` exits 0 for every outcome (L-382), so this script writes its OWN rc and never
# relies on a parent reading a setsid return.
#
# A FAILED MESH-GATE SCREEN IS NOT A RUNNER FAILURE. A grid that fails §3.1/§3.2 is the EXPECTED
# negative finding (RUNG2_CRM_M0 §15 ground (i)); it is recorded in the birth certificate, not raised
# as an error. The runner fails only on a PROCESS failure (fetch error, conversion crash, checkMesh
# process error, or a title-page refusal -- a wrong/short grid).
#
# mapbc: the committee family's boundary-tag scheme is shared across refinement levels, so the on-box
# dpw5_L1T.mapbc is reused. Patch NAMING is all the mapbc affects; the mesh-gate metrics this screen
# reads (max non-orthogonality, max skewness) are GEOMETRIC and patch-name-independent, so this reuse
# cannot bias the finding. Stated so it is not discovered later.
set -u

BASE="https://dpw.larc.nasa.gov/DPW5/unstructured_grids.REV01"
RAW_DIR=/home/ubuntu/certonomous-runs/RUNG2_grid_acquisition/grid   # large raw ugrids live OUTSIDE git
RUN_ROOT=/home/ubuntu/Certonomous/verification/runs/RUNG2_GRID_ACQUISITION_runs
CG=/home/ubuntu/Certonomous/cases/committee-grids
CONV="$CG/ugrid_to_foam.py"
GRADE="$CG/grade_grid_acq.py"
MAPBC=/home/ubuntu/certonomous-runs/dpw5-committee-probe/grid/dpw5_L1T.mapbc

CAP_CORE_MIN=30.0
RANKS=1
BUDGET=1800                                  # 30.0 * 60 / 1. THE WHOLE RUN'S BUDGET. Registered cap.
START=$(date +%s)

# level -> fetched filename (hex family only: the solvable topology and the refinement axis).
declare -A FNAME=( [L2.C]="L2.C.rev01.p3d.hex.r8.ugrid" [L3.M]="L3.M.rev01.p3d.hex.r8.ugrid" )
LEVELS_TO_FETCH="L2.C L3.M"

say()       { echo "[$(date -u +%H:%M:%S)] $*"; }
remaining() { local now; now=$(date +%s); echo $(( BUDGET - (now - START) )); }

# --- idle-box check. Best-effort: fleet agents are invisible to pgrep (L-41), so the supervisor
#     re-confirms idle at launch; this catches the common case (a foreign OpenFOAM solver running).
foreign_solver_running() {
  # EXACT process-name matches ONLY. A substring `pgrep -f Foam` false-matches any bash whose command
  # line mentions a Foam path -- including THIS runner's own subshells -- and would HELD forever
  # (measured: it matched three unrelated `bash` processes on a box with no solver live). pgrep -x
  # matches the binary name each MPI rank runs, so it catches parallel solvers too.
  local s
  for s in simpleFoam rhoSimpleFoam rhoPimpleFoam pimpleFoam potentialFoam \
           checkMesh snappyHexMesh decomposePar; do
    if pgrep -x "$s" >/dev/null 2>&1; then return 0; fi
  done
  return 1
}

# =====================================================================================
#  --dry: exercise every piece that needs NO bulk download. Creates no run root, fetches nothing.
# =====================================================================================
if [ "${1:-}" = "--dry" ]; then
  say "DRY: idle-box check (report only)"
  if foreign_solver_running; then say "DRY: a foreign OpenFOAM process is live -> would exit 3 HELD";
  else say "DRY: no foreign OpenFOAM solver detected -> would proceed"; fi

  say "DRY: cap arithmetic self-check"
  python3 - "$BUDGET" <<'PY'
import sys
budget = int(sys.argv[1])
# remaining must fall as elapsed rises, and a step is refused once remaining <= 0.
for elapsed in (0, budget // 2, budget, budget + 5):
    rem = budget - elapsed
    ok = "PROCEED" if rem > 0 else "STOP(cap)"
    print(f"  elapsed={elapsed:5d}s remaining={rem:6d}s -> {ok}")
assert budget - (budget + 5) < 0
print("  cap arithmetic OK: an overrun yields a negative remaining and STOPS the step")
PY

  say "DRY: title-page plumbing against a SYNTHETIC file (the exact import path production uses)"
  TMP=$(mktemp -d)
  python3 - "$TMP" <<'PY'
import sys, struct, os
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/committee-grids")
import grade_grid_acq as g
tmp = sys.argv[1]
good = os.path.join(tmp, "good.ugrid")
# a valid raw-C-stream hex ugrid: nodes=103, hex=100 -> ratio 1.03, size 28+103*24+100*32 = 5700
open(good, "wb").write(struct.pack("<7i", 103, 0, 0, 0, 0, 0, 100) + b"\x00" * (103*24 + 100*32))
spec = dict(content_length=5700, nodes=103, cells=100, hex=100, tet=0, pyr=0, prism=0)
# 1) correct file admits VERIFIED through the same function production calls
r = g.title_page_check(spec, good)
print("  admit(correct) ->", r["title_page"], "nodes", r["nodes"], "cells", r["cells"])
# 2) a truncated file (short read) is REFUSED -- would be DISCARDED, never converted
open(good, "wb").write(struct.pack("<7i", 103, 0, 0, 0, 0, 0, 100) + b"\x00" * (103*24 + 100*32 - 10))
try:
    g.title_page_check(spec, good)
    print("  admit(truncated) -> DID NOT REFUSE  *** UNEXPECTED"); sys.exit(1)
except g.Refusal:
    print("  admit(truncated) -> REFUSED (would be discarded before any conversion)")
print("  title-page plumbing OK")
PY
  DRYRC=$?
  rm -rf "$TMP"
  [ $DRYRC -eq 0 ] || { say "DRY: title-page plumbing FAILED (rc=$DRYRC)"; exit 1; }
  say "DRY: all no-download pieces behaved. NOTHING fetched, NOTHING converted, no run root created."
  exit 0
fi

# =====================================================================================
#  production run. GATED: run-root no-clobber, then idle-box (HELD, not fail), then the pipeline.
# =====================================================================================
STATUS="$RUN_ROOT/STATUS.RUNG2_GRID_ACQUISITION"

# rule 4 no-clobber: refuse a run root that already holds an answer.
if [ -e "$RUN_ROOT" ]; then
  echo "rc=3 no-clobber: $RUN_ROOT already exists" ; exit 3
fi

# idle-box: a WAIT, not a stop. Exit 3 HELD so the daemon retries; do NOT race a foreign job.
if foreign_solver_running; then
  echo "[$(date -u +%H:%M:%S)] HELD: a foreign OpenFOAM process is live. Not racing it (RUNG2_CRM_M0 §14.2). Retry later."
  exit 3
fi

mkdir -p "$RUN_ROOT" "$RAW_DIR"
say "RUN_ROOT $RUN_ROOT   RAW_DIR $RAW_DIR   cap ${CAP_CORE_MIN} core-min (${BUDGET}s at ${RANKS} rank)"
date +%s.%N > "$RUN_ROOT/RUN_ROOT_CREATED_EPOCH"     # age-guard datum, stamped before any artifact
[ -f "$MAPBC" ] || { echo "rc=4 mapbc missing: $MAPBC" > "$STATUS"; say "STOPPED rc=4 mapbc missing"; exit 4; }

fail() { say "STOPPED rc=$1: $2"; echo "rc=$1 $2" > "$STATUS"; exit "$1"; }

set +u
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
[ -n "${FOAM_APPBIN:-}" ] || fail 4 "FOAM_APPBIN unset after sourcing the OpenFOAM bashrc"
export PATH="$FOAM_APPBIN:$PATH"
command -v checkMesh >/dev/null || fail 4 "checkMesh not on PATH after sourcing the OpenFOAM bashrc"
say "OpenFOAM environment up: $(command -v checkMesh)"

one_level() {
  local LEVEL=$1 UG="$RAW_DIR/${FNAME[$1]}" URL="$BASE/${FNAME[$1]}" C="$RUN_ROOT/$1" R T0 T1 BYTES
  mkdir -p "$C/constant" "$C/system"

  # --- 2. FETCH (inbound, read-only). --max-time bounded by the remaining cap budget. ---
  [ "$(remaining)" -gt 0 ] || fail 6 "cap exhausted before fetching $LEVEL"
  say "fetch $LEVEL  <- $URL"
  T0=$(date +%s)
  timeout "$(remaining)" curl -fsS --max-time "$(remaining)" -o "$UG" "$URL"; R=$?
  [ $R -eq 0 ] || fail 7 "curl rc=$R fetching $LEVEL (124 = cap stop). Nothing converted."
  BYTES=$(stat -c%s "$UG"); T1=$(date +%s)
  say "$LEVEL fetched: $BYTES bytes in $((T1-T0))s (remaining $(remaining)s)"

  # --- 3. TITLE-PAGE admission FIRST, via grade_grid_acq.title_page_check. Refuse -> DISCARD. ---
  say "title-page admission $LEVEL (§4.A, L-144)"
  timeout "$(remaining)" python3 - "$LEVEL" "$UG" <<'PY'
import sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/committee-grids")
import grade_grid_acq as g
level, ug = sys.argv[1], sys.argv[2]
try:
    r = g.title_page_check(g.LEVELS[level], ug)
    print("TITLEPAGE VERIFIED nodes=%d cells=%d ratio=%s" % (r["nodes"], r["cells"], r["node_cell_ratio"]))
except g.Refusal as exc:
    print("TITLEPAGE REFUSED: %s" % exc); sys.exit(2)
PY
  R=$?
  if [ $R -ne 0 ]; then
    rm -f "$UG"                                  # a bad grid is DISCARDED before any conversion
    fail 5 "$LEVEL failed §4.A title-page admission (rc=$R) -- file discarded, NOT converted. NOT A RESULT for $LEVEL."
  fi

  # --- 4. CONVERT the admitted ugrid (committed, unmodified ugrid_to_foam.py). ---
  cat > "$C/system/controlDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     simpleFoam;
startFrom       startTime;  startTime 0;
stopAt          endTime;    endTime   1;
deltaT          1;          writeControl timeStep;  writeInterval 1000;
runTimeModifiable false;
EOF
  cat > "$C/system/fvSchemes" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes { default steadyState; } gradSchemes { default Gauss linear; }
divSchemes { default none; } laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; } snGradSchemes { default corrected; }
EOF
  cat > "$C/system/fvSolution" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers { }
EOF
  [ "$(remaining)" -gt 0 ] || fail 6 "cap exhausted before converting $LEVEL"
  say "convert $LEVEL"
  T0=$(date +%s)
  timeout "$(remaining)" python3 "$CONV" "$UG" "$MAPBC" "$C" > "$C/log.convert" 2>&1; R=$?
  [ $R -eq 0 ] || fail 8 "ugrid_to_foam rc=$R on $LEVEL (124 = cap stop)"
  T1=$(date +%s); say "$LEVEL converted in $((T1-T0))s (remaining $(remaining)s)"

  # --- 5. checkMesh. rc!=0 is a PROCESS failure; the mesh VERDICT string is never read (L-459). ---
  [ "$(remaining)" -gt 0 ] || fail 6 "cap exhausted before checkMesh on $LEVEL"
  say "checkMesh $LEVEL"
  T0=$(date +%s)
  ( cd "$C" && timeout "$(remaining)" checkMesh > log.checkMesh 2>&1 ); R=$?
  [ $R -eq 0 ] || fail 9 "checkMesh rc=$R on $LEVEL (124 = cap stop) -- PROCESS failure"
  T1=$(date +%s); say "$LEVEL checkMesh in $((T1-T0))s (remaining $(remaining)s)"

  # --- 6. GRADE via the frozen comparator: writes the birth certificate and the finding. ---
  [ "$(remaining)" -gt 0 ] || fail 6 "cap exhausted before grading $LEVEL"
  say "grade $LEVEL (§4.A re-verify + §4.B mesh-gate screen -> birth certificate)"
  timeout "$(remaining)" python3 "$GRADE" --grade "$LEVEL" "$UG" "$C/log.checkMesh" \
      "$C/birth_certificate.json" > "$C/log.grade" 2>&1; R=$?
  [ $R -eq 0 ] || fail 5 "$LEVEL grade REFUSED (rc=$R) -- NOT A RESULT for $LEVEL. See $C/log.grade"
  say "$LEVEL graded. Finding in $C/birth_certificate.json"
}

for L in $LEVELS_TO_FETCH; do one_level "$L"; done

TOTAL=$(( $(date +%s) - START ))
CORE_MIN=$(python3 -c "print(round($TOTAL*$RANKS/60.0,4))")
say "DONE. ${TOTAL} wall s at ${RANKS} rank = ${CORE_MIN} core-min (cap ${CAP_CORE_MIN})."
echo "rc=0 total_wall_s=$TOTAL core_min=$CORE_MIN cap_core_min=$CAP_CORE_MIN" > "$STATUS"
say "Per-level findings: $RUN_ROOT/{L2.C,L3.M}/birth_certificate.json"
exit 0
