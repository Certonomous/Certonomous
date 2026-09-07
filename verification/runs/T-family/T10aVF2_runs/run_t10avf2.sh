#!/bin/bash
# run_t10avf2.sh -- T10a-VF2 sweep runner (STAGING DRAFT, NOT FROZEN, NOT PINNED).
#
# Authored by a heat-transfer lane on the staging dispatch, 2026-09-07. Per
# T10aVF2_PREREGISTRATION.md (frozen c4d1e30a) sec.6 this driver is "cut at
# BUILD/launch ... diff-read and pinned before the run" -- that diff-read is the
# SUPERVISOR's SUPERVISION_CHARTER sec.3 check and is NOT done by this lane.
#
# Mesh-side preprocessing ONLY: blockMesh (+ optional faceAgglomerate) then
# viewFactorsGen. NO SOLVER IS EVER STARTED. viewFactorsGen writes constant/F;
# no case in this tree holds a solver time directory.
#
# CAP ENFORCEMENT (exemplar discipline, T5b_runs/run_one_t5b.sh: "an argv cannot
# widen a cap"). --cap-core-min is REQUIRED; the whole sweep runs under a hard
# `timeout` derived from it. The sweep is SERIAL (one utility at a time), so at
# --ranks 1 core-minutes == wall-minutes and CAP_WALL_S = cap_core_min * 60. A
# viewFactorsGen that ignores SIGTERM is SIGKILLed 30 s later (timeout -k 30).
#
# Reused VERBATIM from the frozen predecessor run_t10avf.sh: the per-case body
# (rm stale outputs; blockMesh; checkMesh; faceAgglomerate when agglom!=0;
# viewFactorsGen; STATUS line) and the disclosed plumbing fix -- neither `set -u`
# nor `set -e` is in force while the openfoam2606 bashrc is sourced.

usage() { echo "usage: $0 --root DIR --cap-core-min N --ranks 1 [--no-detach]" >&2; }

# ---- the actual sweep phase (re-entered under `timeout`) --------------------
if [ "$1" = "--_sweep" ]; then
    shift
    ROOT=""
    while [ $# -gt 0 ]; do
        case "$1" in
            --root) ROOT="$2"; shift 2;;
            *) shift;;
        esac
    done
    . /usr/lib/openfoam/openfoam2606/etc/bashrc 2>/dev/null || true
    export WM_NCOMPPROCS=1
    export OMP_NUM_THREADS=1
    run_one() {
        local d="$1" nm agg t0 t1
        nm="$(basename "$d")"
        [ -f "$d/CASE.json" ] || { echo "SKIP $nm (no CASE.json)"; return; }
        agg=$(python3 -c "import json;print(json.load(open('$d/CASE.json'))['agglomeration'])")
        ( cd "$d"
          rm -rf constant/polyMesh constant/F constant/globalFaceFaces \
                 constant/mapDist constant/finalAgglom processor* 0 1
          t0=$(date +%s.%N)
          blockMesh > log.blockMesh 2>&1        || { echo "FAIL blockMesh $nm"; exit 1; }
          checkMesh > log.checkMesh 2>&1        || true
          if [ "$agg" != "0" ]; then
              faceAgglomerate -dict constant/viewFactorsDict > log.faceAgglomerate 2>&1 \
                  || { echo "FAIL faceAgglomerate $nm"; exit 1; }
          fi
          viewFactorsGen > log.viewFactorsGen 2>&1 || { echo "FAIL viewFactorsGen $nm"; exit 1; }
          t1=$(date +%s.%N)
          printf 'case=%s wall_s=%.2f nFaces=%s\n' "$nm" "$(echo "$t1-$t0" | bc)" \
                 "$(grep -c '' constant/globalFaceFaces 2>/dev/null || echo 0)" > STATUS
          echo "OK   $nm  $(awk '{print $2}' STATUS)"
        )
    }
    for d in "$ROOT"/*/; do
        [ -d "$d" ] || continue
        run_one "$d"          # SERIAL by construction: no `&`, no MAXJOBS
    done
    echo "ALL DONE"
    exit 0
fi

# ---- argument parsing + cap arming (the launch entry point) -----------------
ROOT=""; CAP=""; RANKS=""; DETACH=1
while [ $# -gt 0 ]; do
    case "$1" in
        --root) ROOT="$2"; shift 2;;
        --cap-core-min) CAP="$2"; shift 2;;
        --ranks) RANKS="$2"; shift 2;;
        --no-detach) DETACH=0; shift;;
        *) echo "unknown arg: $1" >&2; usage; exit 2;;
    esac
done
[ -n "$ROOT" ] || { echo "REFUSE: --root is required" >&2; usage; exit 2; }
[ -d "$ROOT" ] || { echo "REFUSE: --root $ROOT is not a directory" >&2; exit 2; }
# An argv cannot omit or widen the cap.
[ -n "$CAP" ] || { echo "REFUSE: --cap-core-min is required (an argv cannot run uncapped)" >&2; exit 2; }
# This sweep is serial; at ranks 1 core-min == wall-min. Refuse any other rank
# count so the entry's declared ranks cannot silently disagree with reality.
[ "$RANKS" = "1" ] || { echo "REFUSE: this sweep is serial; --ranks must be 1, got '$RANKS'" >&2; exit 2; }

CAP_WALL_S=$(python3 -c "print(int(round(float('$CAP')*60)))")
HERE="$(cd "$(dirname "$0")" && pwd)"
echo "T10aVF2 sweep: root=$ROOT cap=${CAP} core-min -> hard wall ceiling ${CAP_WALL_S}s (ranks 1, serial)"
# Hard cap: SIGTERM at the ceiling, SIGKILL 30 s later if it is ignored.
timeout --preserve-status -s TERM -k 30 "$CAP_WALL_S" \
    bash "$HERE/$(basename "$0")" --_sweep --root "$ROOT"
rc=$?
if [ $rc -eq 124 ] || [ $rc -eq 137 ]; then
    echo "CAP OVERRUN: sweep hit the ${CAP} core-min ceiling and was stopped (rc $rc). The run does not get a new budget (CLAUDE.md rule 12)."
fi
exit $rc
