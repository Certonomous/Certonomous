#!/usr/bin/env bash
# build_and_run.sh -- the K0b mesh-sensitivity pair.  F14, proposal P2.
#
# WHAT THIS IS
# ------------
# `verification/campaign/THERMAL_K0_RESULTS.md` (R21; it was
# `demo-output/website/campaign/THERMAL_K0_RESULTS.md` when this was written),
# proposal P2: "Every K0b
# number above is from a single 64x64 mesh. A single-mesh number is not a
# converged number."  P2 costed a 32/64/128 triple at 4.85 core-minutes measured
# plus this lab's 3x planning multiplier, i.e. an ask of 15 core-minutes.  The
# 64x64 leg is already run and committed at 183c91c0, so this script runs the
# two NEW legs -- 32x32 and 128x128 -- and the analysis reads the third leg from
# the committed K0b case.  That is the "pair" in the authorisation.
#
# WHAT IS AND IS NOT ALLOWED TO CHANGE
# ------------------------------------
# Exactly one line of the DISCRETISATION changes: the cell counts in
# system/blockMeshDict.  Everything else -- Pr = 0.706814, the
# limitedLinear/linearUpwind schemes, relaxation, residualControl, the 0.orig
# fields -- is copied byte-for-byte from the committed K0b case.  A mesh study
# that also changes the scheme is not a mesh study.  In particular these cases
# deliberately do NOT adopt the central-difference schemes or the Pr = 0.71 of
# the K0c gate cases next door: the question here is whether K0b's OWN
# published numbers move with mesh.
#
# The ITERATION COUNT is not in that list, and the distinction is the whole of
# D406.  A leg that stops before its residuals have fallen is not a coarser or
# finer answer to the mesh question, it is iteration error wearing a mesh
# study's clothes; iteration count is not a discretisation parameter, so
# running a leg further is not a change to the study.  See THE CONTINUATION
# below, which is now a step of this script rather than a step of a README.
#
# The `[0-9]*` glob is not used anywhere here; see the note in
# ../K0c_runs/run_cases.sh for what it cost the last time it was.
set -eo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)

# THE ARCHIVE IS ASKED FOR BY NAME, NOT SPELLED OUT.
#
# D403.  This used to read `$(cd "$HERE/../../../.." && pwd)` followed by the
# literal `demo-output/website/campaign/THERMAL_K0_runs/K0b_cavity_Ra1e5`.  R20
# moved that archive to `verification/runs/THERMAL_K0_runs` and this rung has
# been unrunnable since: the guard below REFUSED on every invocation.  The repo
# root is now FOUND rather than counted -- a counted chain of `..` is silent
# when the count is wrong and the directory it lands on is readable -- and the
# archive is resolved through `lab_paths.run_archive`, which probes every
# spelling the map knows and prefers the successor.  Correct on both sides of
# that move and of the next one.
REPO=$HERE
while [ ! -f "$REPO/scripts/lab_paths.py" ]; do
    parent=$(dirname "$REPO")
    if [ "$parent" = "$REPO" ]; then
        echo "REFUSE: no scripts/lab_paths.py in any parent of $HERE"; exit 2
    fi
    REPO=$parent
done

SRC=$(python3 - "$REPO" <<'PY'
import os, sys
sys.path.insert(0, os.path.join(sys.argv[1], "scripts"))
import lab_paths
p = lab_paths.run_archive("THERMAL_K0_runs")
sys.stdout.write("" if p is None else os.path.join(str(p), "K0b_cavity_Ra1e5"))
PY
)
[ -n "$SRC" ] || { echo "REFUSE: no THERMAL_K0_runs archive under any spelling lab_paths knows"; exit 2; }
FOAM_BASHRC=${FOAM_BASHRC:-/usr/lib/openfoam/openfoam2606/etc/bashrc}

[ -d "$SRC/0.orig" ] || { echo "REFUSE: K0b source case not found at $SRC"; exit 2; }

# THE CONTINUATION, AND WHY IT IS HERE RATHER THAN IN THE README.
#
# D406.  This script used to run every leg to the source case's `endTime 4000`
# and stop.  The published 128x128 leg of this rung was NOT produced that way:
# it was continued BY HAND to 16000 iterations, and the only executable trace
# of that step was `K0b_m128/system/controlDict.4000`, a file left behind by
# the human who made the edit.  Two consequences, both measured on 2026-08-18
# during the D403 re-run:
#
#   1. Running the two commands this rung's README documents, in the order it
#      documents them, produced Nu_avg_hot = 4.3254648850 against the published
#      4.5288167412 -- 4.490 % low -- and an observed order of -1.25 against
#      the published +1.94, five of six orders negative and the sixth
#      non-monotone.  A reader of that table would conclude the case DIVERGES
#      under refinement.  It does not; the leg was unconverged, at initial
#      residuals of 8.7e-05 on Ux against 2.4e-08 after the continuation.
#
#   2. The copy step below overwrites `system/controlDict` from the source case
#      on every invocation, so the hand edit could not survive a re-run of the
#      very script that was supposed to have produced the result.  The state
#      the rung depended on was destroyed by the thing that depended on it.
#
# Both are removed by the same change: the second stage is DERIVED here, by
# this script, from the source case's own dictionary, every time.  Nothing
# hand-edited has to survive anything, so there is nothing for the copy step to
# clobber.  `system/controlDict.4000` is still written -- it is the stage-1
# dictionary and the published leg carries it -- but it is now an OUTPUT of
# this script rather than an input to it.
#
# The stage is entered only by a leg that did NOT stop itself on
# `residualControl`.  The 32x32 leg converges at t = 1386 and is therefore left
# exactly where it stopped; continuing a converged leg would move its written
# times and change a published number for no reason.  The 64x64 leg is read in
# place from the committed archive by `analyse_k0b_mesh.py` and is not built,
# solved or continued here at all.
CONT_END=16000
CONT_WRITE_INTERVAL=2000

# D410. THE REFUSAL GUARD, BECAUSE A PROSE WARNING IS NOT A GUARD.
#
# The loop below opens each leg with `rm -rf "$dst"`. Run where this script's own
# README documents it, that DESTROYS 36 TRACKED FILES -- the published record of
# the rung -- before rebuilding half of them. `git ls-files` over K0b_m32 and
# K0b_m128 counts 17 and 19: both COST.txt, every solver log, system/controlDict.4000
# and every dictionary of both legs.
#
# The D406 repair answered this with a README paragraph saying "run it somewhere
# else". D406's entire finding was that a REQUIRED STEP EXISTED ONLY AS PROSE.
# Answering an adjacent hazard in the same file with more prose is the same shape
# one hazard along, so it is answered here in the only place a warning cannot be
# skipped: the code that does the deleting.
#
# The guard asks git, not a path pattern, because the hazard is "this directory
# holds committed work" and git is the only thing that knows that. Running in a
# scratch tree -- which is what both the D403 re-run and the D406 proof did --
# has no tracked files and passes straight through.
#
# K0B_ALLOW_DESTRUCTIVE=1 overrides, for the one legitimate case: deliberately
# regenerating the archive with intent to commit the result.
for n in 32 128; do
    dst="$HERE/K0b_m$n"
    if [ -d "$dst" ] && [ -z "${K0B_ALLOW_DESTRUCTIVE:-}" ]; then
        tracked=$(cd "$dst" 2>/dev/null && git ls-files 2>/dev/null | wc -l | tr -d ' ')
        if [ "${tracked:-0}" -gt 0 ]; then
            echo "REFUSE: $dst holds $tracked TRACKED files and this script would delete them."
            echo "        Running here destroys the published record of the rung before"
            echo "        rebuilding part of it. Copy the rung to a scratch tree and run it"
            echo "        there, as K0b_D403_RERUN_RESULTS.md section 3 and the D406 proof"
            echo "        run both did. To regenerate the archive on purpose, and only with"
            echo "        intent to commit the result, set K0B_ALLOW_DESTRUCTIVE=1."
            exit 2
        fi
    fi
    rm -rf "$dst"
    mkdir -p "$dst"
    cp -r "$SRC/0.orig" "$SRC/constant" "$SRC/system" "$dst/"
    rm -rf "$dst/constant/polyMesh"
    sed -i "s/hex (0 1 3 2 4 5 7 6) (64 64 1)/hex (0 1 3 2 4 5 7 6) ($n $n 1)/" \
        "$dst/system/blockMeshDict"
    grep -q "($n $n 1)" "$dst/system/blockMeshDict" \
        || { echo "REFUSE: blockMeshDict edit did not take for n=$n"; exit 2; }
    # Prove nothing else moved.
    for f in system/fvSchemes system/fvSolution system/controlDict \
             constant/transportProperties constant/g constant/turbulenceProperties \
             constant/thermalAuditProperties 0.orig/T 0.orig/U 0.orig/p_rgh 0.orig/alphat; do
        cmp -s "$SRC/$f" "$dst/$f" \
            || { echo "REFUSE: $f differs from the committed K0b case"; exit 2; }
    done
done

pids=()
for n in 32 128; do
(
    dst="$HERE/K0b_m$n"
    start=$(date +%s.%N)
    bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$dst'; foamListTimes -rm >/dev/null 2>&1 || true"
    rm -rf "$dst/0" "$dst/postProcessing"
    cp -r "$dst/0.orig" "$dst/0"
    bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$dst'; blockMesh > log.blockMesh 2>&1"
    bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$dst'; checkMesh > log.checkMesh 2>&1"
    bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$dst'; buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam 2>&1"
    end=$(date +%s.%N)
    el=$(echo "$end - $start" | bc)
    printf 'case K0b_m%s\nwall_clock_s %.3f\ncores 1\ncore_minutes %.4f\n' \
        "$n" "$el" "$(echo "$el / 60" | bc -l)" > "$dst/COST.txt"
    printf 'K0b_m%s  wall %.2f s\n' "$n" "$el"

    # --- stage 2, the continuation.  D406; see the block above. ---------------
    #
    # HOW THE STOPPING REASON IS READ, and it is read rather than assumed.
    # buoyantBoussinesqSimpleFoam prints `SIMPLE solution converged in N
    # iterations` when residualControl fires and stops it, and prints no such
    # line when it runs out at endTime.  The line is the solver's own statement
    # about its own termination; the time directories cannot distinguish the
    # two cases and neither can a residual read off the last iteration.
    if grep -q "SIMPLE solution converged in" "$dst/log.buoyantBoussinesqSimpleFoam"; then
        printf 'K0b_m%s  stopped itself on residualControl; NOT continued\n' "$n"
    else
        # The stage-1 dictionary is preserved BEFORE it is rewritten, and it is
        # proved to be the source case's own at the moment it is preserved --
        # not assumed to have survived the solve.
        cmp -s "$SRC/system/controlDict" "$dst/system/controlDict" \
            || { echo "REFUSE: K0b_m$n/system/controlDict is not the committed case's at the end of stage 1"; exit 2; }
        cp "$dst/system/controlDict" "$dst/system/controlDict.4000"
        awk -v e="$CONT_END" -v w="$CONT_WRITE_INTERVAL" '
            $1 == "startFrom"     { printf "%-16s%s;\n", "startFrom", "latestTime"; next }
            $1 == "endTime"       { printf "%-16s%s;\n", "endTime", e; next }
            $1 == "writeInterval" { printf "%-16s%s;\n", "writeInterval", w; next }
                                  { print }
        ' "$dst/system/controlDict.4000" > "$dst/system/controlDict.next"
        mv "$dst/system/controlDict.next" "$dst/system/controlDict"

        # Prove the rewrite moved those three keys and NOTHING else.  A
        # continuation dictionary that had also picked up a scheme, a
        # relaxation factor or a residualControl target would be a different
        # case wearing the same leg's name.
        kept_before=$(grep -vE '^(startFrom|endTime|writeInterval)[[:space:]]' "$dst/system/controlDict.4000")
        kept_after=$(grep -vE '^(startFrom|endTime|writeInterval)[[:space:]]' "$dst/system/controlDict")
        [ "$kept_before" = "$kept_after" ] \
            || { echo "REFUSE: the continuation controlDict for n=$n changed a line outside the three declared keys"; exit 2; }
        grep -qE '^startFrom[[:space:]]+latestTime;$' "$dst/system/controlDict" \
            || { echo "REFUSE: continuation controlDict for n=$n does not restart from latestTime"; exit 2; }
        grep -qE "^endTime[[:space:]]+$CONT_END;\$" "$dst/system/controlDict" \
            || { echo "REFUSE: continuation controlDict for n=$n does not carry endTime $CONT_END"; exit 2; }
        grep -qE "^writeInterval[[:space:]]+$CONT_WRITE_INTERVAL;\$" "$dst/system/controlDict" \
            || { echo "REFUSE: continuation controlDict for n=$n does not carry writeInterval $CONT_WRITE_INTERVAL"; exit 2; }

        start2=$(date +%s.%N)
        bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$dst'; buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam.continue 2>&1"
        end2=$(date +%s.%N)
        el2=$(echo "$end2 - $start2" | bc)
        # APPENDED, never rewritten.  `analyse_k0b_mesh.cost` sums
        # `wall_clock_s` and `continue_wall_clock_s`, and a cost line that
        # quietly omits the expensive half is worse than no cost line.
        printf 'continue_wall_clock_s %s\n' "$el2" >> "$dst/COST.txt"
        printf 'K0b_m%s  continued to t = %s, wall %.2f s\n' "$n" "$CONT_END" "$el2"
    fi
) &
pids+=($!)
done

# WAIT ON EACH LEG BY PID AND CHECK EACH STATUS.  A bare `wait` returns 0 no
# matter how its jobs ended, so a leg that REFUSED -- or a continuation that
# never ran -- would have left this script exiting 0 with a half-built rung
# behind it, which is the same class of silence D406 is about.
rc=0
for p in "${pids[@]}"; do
    if ! wait "$p"; then rc=1; fi
done
[ "$rc" -eq 0 ] || { echo "REFUSE: at least one leg failed; see the logs above"; exit 3; }
