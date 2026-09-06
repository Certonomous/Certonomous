#!/bin/bash
# =====================================================================================
# R2-M2 SNAPSHOT-AT-ENDTIME REHEARSAL -- PRE-FREEZE, NEGLIGIBLE COST
#
# WHY THIS EXISTS.
#   R2-M1's admission gate R2M1-G4 came back GATE FAIL not on the physics but on the
#   RECORDING: B1 reached Time=50 rc=0 with an End line, the FIRST compressible arm to
#   carry past iteration 2 on this grid, yet wrote NO field snapshot at endTime.
#   Confirmed at source, 2026-09-06:
#     verification/runs/RUNG2_CRM_runs/M1_mechanism_and_warmstart/B1/system/controlDict
#       endTime 50 ; writeInterval 120 ; purgeWrite 1 ; writeControl timeStep ; deltaT 1
#     B1/processor0/ holds only  0  and  constant  -- no Time=50 dir  -- so the driver's
#     end-of-run reconstructPar (run_r2_m1.sh:659, guarded by `[ -d processor0/$et ]`)
#     never fired and no serial 50/ snapshot exists.
#   CAUSE, SETTLED (calibration row docs/COST_CALIBRATION.md C-20260906T174429...c13b2999,
#   commit 97e92465): run_r2_m1.sh:281 `cp -a "$SEED/system"` copies the seed's controlDict
#   verbatim; set_endtime (:325-334) rewrites endTime ONLY, leaving writeInterval 120. With
#   deltaT 1 the number of steps equals endTime numerically, so writeInterval 120 > 50 steps
#   and purgeWrite 1 => no write ever fires before the run ends. A COUPLED-SETTING defect:
#   endTime was rewritten without its coupled partner writeInterval.
#
#   VERIFICATION_CHARTER.md section 2ap: PROVE THE WRITER WRITES BEFORE THE RUN PAYS.
#   M1 paid a full 50-step arm (4.667 core-min) to discover the snapshot could not exist.
#
# WHAT IT DOES.
#   Builds a tiny, stable icoFoam cavity -- NOT the DPW5 grid, and not pretending to be --
#   and runs it in PARALLEL to endTime TWICE, both times with purgeWrite 1, writeFormat
#   binary, writeControl timeStep, exactly M1's controlDict shape, differing in one line:
#     BROKEN : writeInterval 120  (M1's inherited value; steps run = 5 < 120)
#     FIXED  : writeInterval == number of steps  (the coupled-setting fix)
#   Then, per config, it runs the SAME chain B1 runs -- parallel solve -> reconstructPar
#   -time <endTime> -> serial snapshot -- and reads back whether a snapshot exists at
#   endTime, both per-processor (parallel) and reconstructed (serial).
#
#   RULE 3 / section 2ap: the reader is planted in BOTH directions. It must see the snapshot
#   PRESENT under the fixed config AND ABSENT under the broken config; a reader that reports
#   PRESENT for both, or ABSENT for both, has measured nothing and this script exits 2.
#
# WHAT IT DOES NOT DO.
#   It says NOTHING about the DPW5 physics. It is a WRITER/IO test on controlDict semantics,
#   which are solver-agnostic. An arm that writes here can still abort there; that is what
#   the graded run is for. It does not touch any RUNG2_CRM run root.
#
# EXIT CODES
#   0  rehearsal ran; its verdict is in the record file (a FAIL is still exit 0)
#   2  the reader did not DISCRIMINATE -- nothing is trusted, nothing reported
#   3  the OpenFOAM environment did not come up
#   4  a source artifact this rehearsal needs is missing
# =====================================================================================
set -uo pipefail

REPO=/home/ubuntu/Certonomous
WORK=${1:?usage: rehearse_r2_m2_snapshot.sh <scratch workdir>}
OUT="$REPO/cases/committee-grids/R2_M2_SNAPSHOT_REHEARSAL.tsv"

DELTAT=0.005
NSTEP=5                       # steps to run; with writeInterval 120 (BROKEN) 5<120 => no write
ENDTIME=$(python3 -c "print(${DELTAT}*${NSTEP})")   # 0.025

die() { echo "REHEARSAL DIED: $*" >&2; exit "${2:-4}"; }

set +u
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
[ -n "${FOAM_APPBIN:-}" ] && command -v icoFoam >/dev/null 2>&1 || die "OpenFOAM env did not come up" 3
TUT="$FOAM_TUTORIALS/incompressible/icoFoam/cavity/cavity"
[ -d "$TUT" ] || die "cavity tutorial missing: $TUT" 4

rm -rf "$WORK"; mkdir -p "$WORK"

# The M2 controlDict shape -- M1's exact top-level keys. The ONLY line that differs between
# BROKEN and FIXED is writeInterval, which is the coupled partner of endTime.
write_controldict() {  # write_controldict <file> <writeInterval>
    cat > "$1" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     icoFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         ${ENDTIME};
deltaT          ${DELTAT};
writeControl    timeStep;
writeInterval   $2;
purgeWrite      1;
writeFormat     binary;
writePrecision  6;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
EOF
}

# reader: count time directories == endTime. Uses awk so it returns exactly ONE integer on
# every path (grep -c prints "0" AND exits 1 on no-match, which the M1 rehearsal proved
# poisons `||` fallbacks; awk does not). ENDTIME may be written by OpenFOAM as 0.025.
count_snapshot() {  # count_snapshot <dir> ; counts entries whose name numerically == ENDTIME
    ls -1 "$1" 2>/dev/null | awk -v t="$ENDTIME" '($0+0)==(t+0) && $0 ~ /^[0-9]/ {n++} END{print n+0}'
}

run_config() {  # run_config <label> <writeInterval>
    local label=$1 wi=$2
    local d="$WORK/$label"
    cp -a "$TUT" "$d"
    write_controldict "$d/system/controlDict" "$wi"
    # 2-way decomposition so the reconstruct chain B1 uses is exercised.
    cat > "$d/system/decomposeParDict" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains 2;
method simple;
coeffs { n (2 1 1); }
EOF
    blockMesh -case "$d"            >"$d/log.blockMesh"   2>&1 || die "$label blockMesh" 4
    decomposePar -case "$d"        >"$d/log.decomposePar" 2>&1 || die "$label decomposePar" 4
    mpirun -np 2 icoFoam -case "$d" -parallel >"$d/log.solve" 2>&1
    local solve_rc=$?
    # B1's chain: reconstruct the endTime snapshot IF it exists per-processor (the driver's
    # own guard, run_r2_m1.sh:659). We do NOT force it; whether it exists is the measurement.
    local per_proc; per_proc=$(count_snapshot "$d/processor0")
    if [ "$per_proc" -ge 1 ]; then
        reconstructPar -case "$d" -time "$ENDTIME" >"$d/log.reconstructPar" 2>&1 || true
    fi
    local serial; serial=$(count_snapshot "$d")
    # fields actually present in the reconstructed snapshot?
    local fields=0
    if [ "$serial" -ge 1 ]; then
        for f in U p; do [ -f "$d/$ENDTIME/$f" ] && fields=$((fields+1)); done
    fi
    echo "$label	$wi	$solve_rc	$per_proc	$serial	$fields"
}

echo "# R2-M2 SNAPSHOT-AT-ENDTIME REHEARSAL -- tiny icoFoam cavity, NOT the DPW5 grid, NOT a physics result." >  "$OUT"
echo "# Generated $(date -u +%Y-%m-%dT%H:%M:%SZ). deltaT=$DELTAT nStep=$NSTEP endTime=$ENDTIME writeFormat=binary purgeWrite=1 writeControl=timeStep ranks=2." >> "$OUT"
echo "# Proves: a rewrite of endTime that leaves writeInterval > nStep (M1's defect) writes NO snapshot at endTime; the coupled fix (writeInterval==nStep) writes one." >> "$OUT"
echo "config	writeInterval	solve_rc	per_processor_snap_at_endTime	reconstructed_serial_snap_at_endTime	fields_UP_present" >> "$OUT"

BROKEN=$(run_config BROKEN 120)   ; echo "$BROKEN" >> "$OUT"
FIXED=$(run_config  FIXED  $NSTEP) ; echo "$FIXED"  >> "$OUT"

bp=$(echo "$BROKEN" | cut -f4); bs=$(echo "$BROKEN" | cut -f5)
fp=$(echo "$FIXED"  | cut -f4); fs=$(echo "$FIXED"  | cut -f5); ff=$(echo "$FIXED" | cut -f6)

# THE DISCRIMINATES LINE. The reader must see the endTime snapshot under FIXED and NOT under
# BROKEN, in BOTH the per-processor and the reconstructed serial views.
DISC=0
if [ "$fp" -ge 1 ] && [ "$fs" -ge 1 ] && [ "$ff" -eq 2 ] && [ "$bp" -eq 0 ] && [ "$bs" -eq 0 ]; then
    DISC=1
fi
{
echo "#"
echo "# DISCRIMINATES: reader sees endTime snapshot present under FIXED (per-proc=$fp serial=$fs fields=$ff/2)"
echo "#               and ABSENT under BROKEN=M1's config (per-proc=$bp serial=$bs) -- $([ $DISC -eq 1 ] && echo DISCRIMINATES || echo DOES_NOT_DISCRIMINATE)"
echo "# VERDICT: $([ $DISC -eq 1 ] && echo 'PASS -- the coupled-setting fix makes a field snapshot land at endTime, per-processor and reconstructed; M1 config writes none' || echo 'FAIL')"
} >> "$OUT"

cat "$OUT"
[ "$DISC" -eq 1 ] || exit 2
exit 0
