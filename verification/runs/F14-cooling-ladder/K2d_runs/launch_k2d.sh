#!/bin/bash
# K2d launcher. Registration section 10. Frozen path e7979e29b.
# set +u BEFORE sourcing the bashrc: under set -u it aborts on an unset var and
# the solver never runs -- rc=127 with NO output, which reads as silence.
set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
set -e
CASE="$1"; RANKS="$2"; GUARD_S="$3"
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE/$CASE"

# clause 7 immediately before arming, from the FROZEN instrument
python3 "$HERE/mark_done_k2d.py" --guard "$HERE/$CASE" >/dev/null || exit 2

# ARM 0/ FROM 0.orig AT LAUNCH -- 0/T is touched last and dates the run, which
# is what the age guard (rule 4 clause 6) compares every field against.
rm -rf 0 && cp -r 0.orig 0 && touch 0/T

cat > system/decomposeParDict <<EOD
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $RANKS;
method scotch;
EOD
decomposePar -force > log.decomposePar 2>&1

# WITNESS, captured BEFORE the launch. No absolute time, no slack: the test is
# a STRICT INCREASE against this exact value.
WIT_BEFORE=$(stat -c %Y log.decomposePar)
echo "$WIT_BEFORE" > WITNESS.before

cat > .run_inner.sh <<'EOI'
set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
cd "$1"; RANKS="$2"; GUARD_S="$3"
T0=$(date +%s)
# rc captured INSIDE the wrapper. `setsid timeout cmd` exits 0 for EVERY
# outcome, so an rc captured around the setsid line is meaningless.
timeout "$GUARD_S" mpirun -np "$RANKS" buoyantBoussinesqSimpleFoam -parallel > log.solve 2>&1
RC=$?
T1=$(date +%s); WALL=$((T1-T0))
# A PARALLEL run leaves its fields in processor*/<t>/, so the case root has NO
# time directory and rule 4 clauses 3 and 4 CANNOT pass.  Reconstruct before
# writing STATUS.  This is post-processing, not a grading-path change: the
# fields are this run's, and they postdate 0/T, so the age guard still binds.
if [ "$RC" = "0" ]; then reconstructPar -latestTime > log.reconstructPar 2>&1 || true; fi
CM=$(python3 -c "print(f'{$WALL*$RANKS/60:.3f}')")
NOTE=clean
[ "$RC" = "124" ] && NOTE=HANG_GUARD_TRIPPED
[ "$RC" != "0" ] && [ "$RC" != "124" ] && NOTE=SOLVER_NONZERO_EXIT
{ echo "case=$(basename "$1")"; echo "rc=$RC"; echo "wall_s=$WALL"
  echo "ranks=$RANKS"; echo "core_min=$CM"; echo "timeout_s=$GUARD_S"
  echo "solver=buoyantBoussinesqSimpleFoam"; echo "note=$NOTE"
  echo "ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "../STATUS.$(basename "$1")"
EOI
chmod +x .run_inner.sh
setsid bash .run_inner.sh "$PWD" "$RANKS" "$GUARD_S" </dev/null >.run_outer.out 2>&1 &
echo $! > PIDS.launcher
