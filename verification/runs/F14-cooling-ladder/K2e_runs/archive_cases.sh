#!/usr/bin/env bash
# archive_cases.sh -- copy the committable part of a solved K2e run tree.
#
#   ./archive_cases.sh <solved-run-dir> <archive-dir>
#
# WHAT IS KEPT AND WHY
#   0.orig/  constant/  system/   the case, exactly as build_cases.py wrote it
#   COST.txt                       the per-case core-minutes
#   log.blockMesh, log.checkMesh   the mesh, witnessed by the utility itself
#   log.<app>.monitor              a FILTERED solver log: the banner, every
#                                  `Time =` line and every function-object
#                                  output line.  This is the convergence
#                                  evidence, and `scripts/check_convergence.py
#                                  --monitor-regex` reads it directly and
#                                  reproduces the gate from it.  The unfiltered
#                                  logs run to 4.6 MB each and 88 MB for the
#                                  sweep, which is not a thing to commit.
#   <latestTime>/T, U, alphat      the fields analyse_k2e.py measures
#                                  Q2..Q6 from, so every number in the results
#                                  can be re-derived without re-solving.
#
# WHAT IS DROPPED
#   constant/polyMesh/             regenerated exactly by `blockMesh`
#   p, p_rgh, phi, alphat          not read by any graded quantity
#   postProcessing/                and NOT because it is large.  On the twelve
#                                  Boussinesq cases of the first pass it no
#                                  longer exists: `scripts/heat_balance.py:770`
#                                  deletes `<case>/postProcessing` outright
#                                  before its own postProcess pass, so auditing
#                                  a case destroys its function-object history.
#                                  Archiving a directory that is present on some
#                                  cases and absent on others, for a reason
#                                  nothing in the tree explains, would be worse
#                                  than archiving none of it.  The monitor log
#                                  carries the same series and nothing deletes
#                                  it.  Docketed.
set -eo pipefail
SRC=$(readlink -f "$1"); DST=$(readlink -f "$2")
mkdir -p "$DST"
for case in "$SRC"/m*; do
    [ -d "$case" ] || continue
    n=$(basename "$case"); out="$DST/$n"
    mkdir -p "$out"
    cp -r "$case/0.orig" "$out/"
    mkdir -p "$out/constant"
    for f in "$case"/constant/*; do
        [ "$(basename "$f")" = "polyMesh" ] && continue
        cp -r "$f" "$out/constant/"
    done
    cp -r "$case/system" "$out/"
    cp "$case/COST.txt" "$out/"
    cp "$case/log.blockMesh" "$case/log.checkMesh" "$out/"
    log=$(ls "$case"/log.buoyant* | head -1)
    app=$(basename "$log")
    { sed -n '1,40p' "$log"
      grep -E '^Time = |of k2eGradT = |of k2eMagU = |of T = |^End$' "$log"
    } > "$out/$app.monitor"
    t=$(ls "$case" | grep -E '^[0-9]+$' | sort -n | tail -1)
    mkdir -p "$out/$t"
    cp "$case/$t/T" "$case/$t/U" "$out/$t/"
    # alphat where the solver wrote it: scripts/heat_balance.py reads it to
    # decide laminar against turbulent and REFUSES rather than assume.
    [ -f "$case/$t/alphat" ] && cp "$case/$t/alphat" "$out/$t/"
done
echo "archived $(ls -d "$DST"/m* | wc -l) cases to $DST"
du -sh "$DST"
