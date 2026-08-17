#!/usr/bin/env bash
# run_cases.sh -- mesh and solve the K0 thermal capability cases.
#
#   ./run_cases.sh [case_dir ...]      (default: all four)
#
# Each case is a single-core laminar 2D solve of a few thousand cells. Nothing
# here is decomposed, nothing here needs the owner's compute word beyond the
# K0a/K0b authorisation. Total is under ten core-minutes.
#
# `0.orig/` holds the initial conditions and travels in git. It is copied to
# `0/` here; `0/` and every later time directory are solver output and do not
# travel (.gitignore: demo-output/website/campaign/*_runs/*/[0-9]*/).
FOAM_BASHRC="${FOAM_BASHRC:-/usr/lib/openfoam/openfoam2606/etc/bashrc}"
# NOTE: the OpenFOAM bashrc dereferences unset variables, so `set -u` must NOT
# be in force while it is sourced -- under `set -u` a non-interactive shell
# exits there and this script dies before printing a single line. It did
# exactly that on first invocation.
# shellcheck disable=SC1090
. "$FOAM_BASHRC" >/dev/null 2>&1
command -v blockMesh >/dev/null 2>&1 || {
    echo "FAIL: OpenFOAM environment not available from $FOAM_BASHRC"; exit 2; }
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
CASES=()
if [ $# -gt 0 ]; then
    CASES=("$@")
else
    CASES=(K0a_heated_box K0a_heated_box_g0 K0a_heated_box_source
           K0b_cavity_Ra1e5 K0b_cavity_g0)
fi

rc_all=0
for name in "${CASES[@]}"; do
    C="$HERE/$name"
    [ -d "$C" ] || { echo "FAIL: no case $C"; rc_all=1; continue; }
    echo "=== $name ==="

    # wipe previous run state; keep 0.orig, system, constant dictionaries
    find "$C" -maxdepth 1 -type d -regex '.*/[0-9][0-9.eE+-]*' -exec rm -rf {} + 2>/dev/null
    rm -rf "$C/postProcessing" "$C/constant/polyMesh" "$C/processor"*
    cp -r "$C/0.orig" "$C/0"

    blockMesh -case "$C" > "$C/log.blockMesh" 2>&1
    if [ $? -ne 0 ]; then echo "  FAIL blockMesh"; tail -5 "$C/log.blockMesh"; rc_all=1; continue; fi
    checkMesh -case "$C" > "$C/log.checkMesh" 2>&1

    t0=$(date +%s.%N)
    ( cd "$C" && buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam 2>&1 )
    rc=$?
    t1=$(date +%s.%N)
    wall=$(python3 -c "print(f'{$t1-$t0:.2f}')")

    if [ $rc -ne 0 ]; then
        echo "  FAIL solver rc=$rc after ${wall}s"
        tail -15 "$C/log.buoyantBoussinesqSimpleFoam"
        rc_all=1
        continue
    fi
    last=$(find "$C" -maxdepth 1 -type d -regex '.*/[0-9][0-9.eE+-]*' \
             -printf '%f\n' 2>/dev/null | sort -g | tail -1)
    echo "  ok  wall=${wall}s  last time=${last}"

    # ---- trim regenerable intermediate time directories --------------------
    # K0b at writeInterval 10 writes 400 of these; the five cases together came
    # to 244 MB before this step and 15 MB after. They are gitignored and this
    # script rebuilds them, so only the snapshots the written record cites are
    # kept: time 0, the final time, and KEEP_TIMES (which the C3 control reads).
    #
    # NOTE the -regex, and do not replace it with a `[0-9]*` glob. `0.orig`
    # starts with a digit, so a glob matches it, and a trim written that way
    # deleted every case's initial conditions -- the tracked input the whole
    # tree is rebuilt from. The same `[0-9]*` collision also makes the repo's
    # time-directory ignore rule swallow `0.orig`, which is why .gitignore
    # carries an explicit negation for it.
    KEEP_TIMES="${KEEP_TIMES:-0 10 20 50 100 500}"
    for d in $(find "$C" -maxdepth 1 -type d -regex '.*/[0-9][0-9.eE+-]*' -printf '%f\n'); do
        keep=0
        [ "$d" = "$last" ] && keep=1
        for k in $KEEP_TIMES; do [ "$d" = "$k" ] && keep=1; done
        [ "$keep" -eq 0 ] && rm -rf "${C:?}/$d"
    done
done
exit $rc_all
