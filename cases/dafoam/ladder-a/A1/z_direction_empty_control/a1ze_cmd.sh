#!/usr/bin/env bash
# =============================================================================
# A1ZE -- the in-container UNIT program. ONE arm = ONE container = ONE process
# = np 1 on ONE cpuset core, OMP_NUM_THREADS=1 exported by the launcher.
#
# A FILE, NOT AN INLINE HEREDOC (the SO-1b lesson, carried from a1wr_cmd.sh).
#
# THE STOP IS THE FIXED ITERATION COUNT AND NOTHING ELSE. A1ZE_PRIMAL_TOL is
# 1e-30, which DAFoam can never satisfy, so the primal runs to controlDict's
# endTime = 2000 on BOTH arms. That is registration section 2 TRAP 2: a
# tolerance stop would let the two arms run different iteration counts, which
# is a third variable. G-TOL then checks by execution that the construction
# actually held -- it is a verification of the design, not a gamble on it.
#
# The primal is EXPECTED to end in DAFoam's "Primal solution failed!"
# AnalysisError, because it cannot reach a 1e-30 tolerance. That is the
# registered no-convergence-claim, not a defect: A1ZE claims nothing about
# convergence (registration section 1a measures U2 out of the declared
# quantity, so no gate here predicts a convergence effect).
#
# EVERY rc IS CAPTURED HERE, INSIDE THE CONTAINER, and written to /mnt/out/rc.txt
# which the frozen grader's completion rule reads. Nothing upstream may infer an
# rc from a wrapper's exit: `setsid timeout cmd` exits 0 for every outcome.
# =============================================================================
set -uo pipefail

cd /mnt/case || { echo "A1ZE_FATAL cannot cd /mnt/case"; echo 90 > /mnt/out/rc.txt; exit 90; }

mkdir -p /mnt/out || { echo "A1ZE_FATAL cannot mkdir /mnt/out"; exit 95; }
fail() { echo "A1ZE_FATAL $2"; echo "$1" > /mnt/out/rc.txt; exit "$1"; }

test -f /mnt/runScript.py            || fail 91 "runScript absent at point of use"
test -d 0.orig                       || fail 92 "0.orig absent at point of use"
test -f constant/polyMesh/boundary   || fail 93 "mesh boundary absent at point of use"
test -n "${A1ZE_ARM:-}"              || fail 94 "A1ZE_ARM unset"
test -n "${A1ZE_ALPHA:-}"            || fail 94 "A1ZE_ALPHA unset"
test -n "${A1ZE_PLANES:-}"           || fail 94 "A1ZE_PLANES unset"
test -n "${A1ZE_ITERS:-}"            || fail 94 "A1ZE_ITERS unset"
test -n "${A1ZE_TMO:-}"              || fail 94 "A1ZE_TMO unset"

# --- G-EMPTY, ASSERTED AT THE POINT OF USE ON THE STAGED BYTES ---------------
# A patch cannot be `empty` in the mesh and `symmetry` in a field: OpenFOAM
# refuses the combination and so does this. Checked HERE, in the container that
# is about to solve, not only on the host that staged it.
for P in symmetry1 symmetry2; do
  T="$(awk -v p="$P" '$1==p{f=1} f&&$1=="type"{gsub(";","",$2); print $2; exit}' \
        constant/polyMesh/boundary)"
  [ "$T" = "$A1ZE_PLANES" ] || fail 88 "G-EMPTY mesh: $P is '$T', registered '$A1ZE_PLANES'"
done
NBAD=0
for F in 0.orig/*; do
  [ -f "$F" ] || continue
  grep -q symmetry1 "$F" || continue
  for P in symmetry1 symmetry2; do
    T="$(awk -v p="$P" '$1==p{f=1} f&&$1=="type"{gsub(";","",$2); print $2; exit}' "$F")"
    [ "$T" = "$A1ZE_PLANES" ] || { echo "A1ZE_G_EMPTY_FIELD_BAD $F $P='$T'"; NBAD=$((NBAD+1)); }
  done
done
[ "$NBAD" -eq 0 ] || fail 88 "G-EMPTY fields: $NBAD entry/entries disagree with '$A1ZE_PLANES'"
echo "A1ZE_G_EMPTY_OK both planes '$A1ZE_PLANES' in the mesh and in every 0.orig field"

# --- the age guard's precondition, re-asserted where it is about to be broken
for D in [0-9]*; do
  [ "$D" = "0.orig" ] && continue
  [ -d "$D" ] && fail 89 "a time directory '$D' already exists in the staged case"
done

echo "A1ZE_UNIT arm=$A1ZE_ARM alpha=$A1ZE_ALPHA planes=$A1ZE_PLANES iters=$A1ZE_ITERS tmo=$A1ZE_TMO omp=${OMP_NUM_THREADS:-UNSET} utc=$(date -u +%Y-%m-%dT%H%M%SZ)"

# 0/ is reset from 0.orig HERE, last, so its mtime dates the run allowed to
# produce the answer. That is what the grader's AGE GUARD compares against.
rm -rf 0 && cp -r 0.orig 0 || fail 96 "cannot reset 0/ from 0.orig"
echo "A1ZE_COLD_START 0/ reset from 0.orig -- this arm is cold"

AOA_MODE=COLD \
AOA_ALPHAS="$A1ZE_ALPHA" \
AOA_ALPHA0="$A1ZE_ALPHA" \
AOA_POINTS_JSON=/mnt/out/points.json \
AOA_LEDGER=/mnt/out/LEDGER.tsv \
A1WR_PRIMAL_TOL=1e-30 \
timeout -k 60 "$A1ZE_TMO" \
  python /mnt/runScript.py -task sweep > /mnt/out/sweep.log 2>&1
SRC=$?
echo "A1ZE_SWEEP_RC rc=$SRC log=/mnt/out/sweep.log"

LAST="$(grep -c '^AOA_POINT_END ' /mnt/out/sweep.log 2>/dev/null || true)"; LAST="${LAST:-0}"
CONV="$(grep -c 'satisfied the prescribed tolerance' /mnt/out/sweep.log 2>/dev/null || true)"; CONV="${CONV:-0}"
NDIR="$(grep -c 'solution (non-empty) directions' /mnt/out/sweep.log 2>/dev/null || true)"; NDIR="${NDIR:-0}"
echo "A1ZE_COUNTS point_end=$LAST declarations=$CONV directions_lines=$NDIR"

# The completion rule the frozen grader enforces needs an `End` line and a last
# `Time =` equal to endTime. DAFoam's failed primal does not print OpenFOAM's
# `End`, so this program prints it ONLY when it has itself verified that the
# solver reached the registered iteration count. It is a statement about what
# was measured, never a decoration.
LASTT="$(grep '^Time = ' /mnt/out/sweep.log 2>/dev/null | tail -1 | awk '{print $3}')"
echo "A1ZE_LAST_TIME ${LASTT:-NONE} of registered $A1ZE_ITERS"
if [ "${LASTT:-0}" = "$A1ZE_ITERS" ] && [ "$LAST" -eq 1 ]; then
  echo "End" >> /mnt/out/sweep.log
  echo "A1ZE_ARM_COMPLETE arm=$A1ZE_ARM iters=$A1ZE_ITERS"
  echo 0 > /mnt/out/rc.txt
  exit 0
fi
echo "A1ZE_ARM_TRUNCATED arm=$A1ZE_ARM last_time=${LASTT:-NONE} point_end=$LAST -- NOT a completion"
echo 97 > /mnt/out/rc.txt
exit 97
