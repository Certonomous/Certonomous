#!/bin/bash
# launch_k2g.sh -- K2g launcher.  Registration sections 7, 8 and 9.
#
#   ./launch_k2g.sh --stage                      # build L3, apply E-ENDTIME, assert
#   ./launch_k2g.sh --check-only K2f_L3 <R> <G>  # assert the row, launch nothing
#   ./launch_k2g.sh K2f_L3 <RANKS> <GUARD_S>     # launch
#
# The registered table below is the ONLY legitimate source of ranks and guard;
# a handed pair that is not a row REFUSES at exit 2.  K2d_L3 died on a
# hand-passed 8034 s guard against a registered 20,250 s and lost 535.6
# core-minutes: the assertion exists because of that run.
#
# The fine level is the directory K2f_L3 so that the FROZEN build_k2f.py and the
# FROZEN mark_done_k2f.py -- the instruments that built and certified L1 and L2
# -- are reused BIT FOR BIT with no edit (CLAUDE.md rule 6).
#
# EXIT MAP: 0 OK, 1 FAIL, 2 REFUSE.  No verdict is carried by an exit code.

set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
K2F="$(cd "$HERE/../K2f_runs" && pwd)"
END_TIME=2000            # registration section 6.  L1 and L2 ran to 3000.

# ======================= THE REGISTERED TABLE (section 8) ===================
# guard_s = CAP x 60 / ranks, CAP = 1200 core-min at every row.
reg_row() {
  case "$1:$2" in
    K2f_L3:main) echo "4 18000" ;;
    K2f_L3:alt)  echo "2 36000" ;;
    *)           echo ""        ;;
  esac
}

# ------------------------------- STAGING -----------------------------------
if [ "${1:-}" = "--stage" ]; then
  if [ -d "$HERE/K2f_L3" ]; then
    echo "REFUSE: $HERE/K2f_L3 already exists. Staging never overwrites a case."
    exit 2
  fi
  python3 -c "
import sys; sys.path.insert(0, '$K2F')
import build_k2f
r = build_k2f.build('K2f_L3', root='$HERE')
print('built cells=%s predicted=%s checkMesh_failed=%s'
      % (r.get('cells'), r['predicted_cells'], r.get('checkmesh_failed')))
" || exit 1

  CD="$HERE/K2f_L3/system/controlDict"
  # --- E-ENDTIME: the one registered edit to a GENERATED dictionary. --------
  # build_k2f.py writes endTime 3000 and is frozen, so it is not edited; the
  # case it generates is.  Exactly one line may change and this asserts it.
  BEFORE=$(md5sum "$CD" | cut -d' ' -f1)
  sed -i "s/^endTime 3000;$/endTime $END_TIME;/" "$CD"
  if ! grep -qx "endTime $END_TIME;" "$CD"; then
    echo "REFUSE: E-ENDTIME did not apply; controlDict does not read endTime $END_TIME;"
    exit 2
  fi
  if grep -qx "endTime 3000;" "$CD"; then
    echo "REFUSE: E-ENDTIME left an endTime 3000; line in place"; exit 2
  fi
  AFTER=$(md5sum "$CD" | cut -d' ' -f1)
  [ "$BEFORE" = "$AFTER" ] && { echo "REFUSE: E-ENDTIME changed nothing"; exit 2; }
  echo "E-ENDTIME applied: endTime $END_TIME; (was 3000)"

  # --- M-REPRO: the fresh mesh must reproduce the 664,848-cell mesh already on
  # disk from the RETIRED K2d_L3 build -- cell count AND every patch face count.
  K2G_HERE="$HERE" python3 - <<'PYX' || exit 1
import re, os, sys
HERE = os.environ.get("K2G_HERE")
old = os.path.join(HERE, "..", "K2d_runs", "RETIRED_2026-09-11", "K2d_L3",
                   "constant", "polyMesh")
new = os.path.join(HERE, "K2f_L3", "constant", "polyMesh")
def meta(pm):
    raw = open(os.path.join(pm, "boundary")).read()
    raw = re.sub(r"/\*.*?\*/", " ", raw, flags=re.S)
    d = {}
    for m in re.finditer(r"([A-Za-z_][\w.]*)\s*\{([^}]*)\}", raw):
        nf = re.search(r"nFaces\s+(\d+)", m.group(2))
        if nf:
            d[m.group(1)] = int(nf.group(1))
    n = re.search(r"nCells:(\d+)", open(os.path.join(pm, "owner")).read())
    return int(n.group(1)), d
if not os.path.isdir(old):
    print("M-REPRO SKIPPED: the retired K2d_L3 mesh is not on disk"); sys.exit(0)
a, pa = meta(old); b, pb = meta(new)
if a != b or pa != pb:
    print("REFUSE M-REPRO: fresh build %d cells %s vs retired %d cells %s"
          % (b, pb, a, pa)); sys.exit(1)
print("M-REPRO OK: fresh build reproduces %d cells and every patch face count "
      "of the independently built retired mesh" % b)
PYX
  echo "STAGED. Nothing is running. Launch with:"
  echo "  $0 K2f_L3 4 18000"
  exit 0
fi

CHECK_ONLY=0
if [ "${1:-}" = "--check-only" ]; then CHECK_ONLY=1; shift; fi
CASE="${1:-}"; RANKS="${2:-}"; GUARD_S="${3:-}"; ROW="main"
[ "${4:-}" = "--alt" ] && ROW="alt"
if [ -z "$CASE" ] || [ -z "$RANKS" ] || [ -z "$GUARD_S" ]; then
  echo "REFUSE: usage: $0 [--stage | --check-only] <CASE> <RANKS> <GUARD_S> [--alt]"
  exit 2
fi
WANT="$(reg_row "$CASE" "$ROW")"
if [ -z "$WANT" ]; then
  echo "REFUSE: $CASE is not a K2g level. The only level K2g launches is K2f_L3;"
  echo "        K2g_L1 and K2g_L2 are K2f_L1 and K2f_L2 REUSED BY CITATION and"
  echo "        are never re-run."
  exit 2
fi
W_RANKS="${WANT% *}"; W_GUARD="${WANT#* }"
if [ "$RANKS" != "$W_RANKS" ] || [ "$GUARD_S" != "$W_GUARD" ]; then
  echo "REFUSE: handed ranks=$RANKS guard=${GUARD_S}s for $CASE ($ROW row),"
  echo "        but the REGISTERED row is ranks=$W_RANKS guard=${W_GUARD}s."
  exit 2
fi
echo "ASSERT OK: $CASE ($ROW row) ranks=$RANKS guard=${GUARD_S}s matches the registered row."

CD="$HERE/$CASE/system/controlDict"
if [ ! -f "$CD" ] || ! grep -qx "endTime $END_TIME;" "$CD"; then
  echo "REFUSE: $CASE is not staged, or E-ENDTIME is not applied to its controlDict."
  exit 2
fi
[ "$CHECK_ONLY" = "1" ] && exit 0

cd "$HERE/$CASE"
python3 "$K2F/mark_done_k2f.py" --guard "$HERE/$CASE" >/dev/null || exit 2
rm -rf 0 && cp -r 0.orig 0 && touch 0/T
cat > system/decomposeParDict <<EOD
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $RANKS;
method scotch;
EOD
decomposePar -force > log.decomposePar 2>&1
stat -c %Y log.decomposePar > WITNESS.before

cat > .run_inner.sh <<'EOI'
set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
cd "$1"; RANKS="$2"; GUARD_S="$3"
T0=$(date +%s)
timeout "$GUARD_S" mpirun -np "$RANKS" buoyantBoussinesqSimpleFoam -parallel > log.solve 2>&1
RC=$?
T1=$(date +%s); WALL=$((T1-T0))
if [ "$RC" = "0" ]; then reconstructPar -latestTime > log.reconstructPar 2>&1 || true; fi
CM=$(python3 -c "print(f'{$WALL*$RANKS/60:.3f}')")
EX=$(grep -oE 'ExecutionTime = [0-9.]+' log.solve | tail -1 | grep -oE '[0-9.]+$' || echo "")
CL=$(grep -oE 'ClockTime = [0-9.]+'     log.solve | tail -1 | grep -oE '[0-9.]+$' || echo "")
NOTE=clean
[ "$RC" = "124" ] && NOTE=GUARD_TRIPPED_TRIAGE_REQUIRED
[ "$RC" != "0" ] && [ "$RC" != "124" ] && NOTE=SOLVER_NONZERO_EXIT
{ echo "case=$(basename "$1")"; echo "rc=$RC"; echo "wall_s=$WALL"
  echo "ranks=$RANKS"; echo "core_min=$CM"; echo "timeout_s=$GUARD_S"
  echo "execution_time_s=$EX"; echo "clock_time_s=$CL"
  echo "solver=buoyantBoussinesqSimpleFoam"; echo "note=$NOTE"
  echo "ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "../STATUS.$(basename "$1")"
EOI
chmod +x .run_inner.sh
setsid bash .run_inner.sh "$PWD" "$RANKS" "$GUARD_S" </dev/null >.run_outer.out 2>&1 &
echo $! > PIDS.launcher
echo "LAUNCHED pid=$(cat PIDS.launcher) cwd=$PWD ranks=$RANKS guard=${GUARD_S}s row=$ROW"
