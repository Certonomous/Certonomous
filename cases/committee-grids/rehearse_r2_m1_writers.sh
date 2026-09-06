#!/bin/bash
# =====================================================================================
# R2-M1 MECHANISM-WRITER REHEARSAL -- PRE-FREEZE, PER ARM, NEGLIGIBLE COST
#
# WHY THIS EXISTS.
#   R2-M0's mechanism gate R2-G2 came back NOT A RESULT. The registration is
#   `verification/campaign/RUNG2_CRM_M0_PREREGISTRATION.md`; the calibration row is
#   `docs/COST_CALIBRATION.md` C-20260906T161200.871248Z-5aae017a. The money was spent and
#   the mechanism stayed unnamed. A successor that registers a second mechanism gate
#   WITHOUT first proving the writer writes is buying the same silence twice.
#
#   VERIFICATION_CHARTER.md section 2ap (corruption leg): PROVE THE WRITER WRITES BEFORE
#   THE RUN PAYS FOR IT.
#
# WHAT IT DOES.
#   Builds a 125-cell box -- NOT the DPW5 grid, and it is not pretending to be -- and runs
#   rhoSimpleFoam on it once per M1 arm, using THAT ARM'S OWN registered dictionaries
#   (thermophysicalProperties, fvSolution transonic switch, fvOptions bounds, controlDict
#   function objects). It then reads back, per arm:
#       W1  fieldMinMax records: one row per registered field per COMPLETED step
#       W2  the solver's own intra-step lines (pressureControl / continuity), which are
#           written DURING a step and therefore survive an abort that W1 cannot record
#   and it PLANTS A CONTROL on each reader in both directions.
#
# WHAT IT DOES NOT DO.
#   It says NOTHING about the physics on the DPW5 grid. It is a WRITER test. An arm that
#   writes here can still abort there; that is what the graded run is for.
#
# PER ARM, NOT ONCE. M0's A2 produced no postProcessing directory at all while A0, A1 and
# A4 produced one, on the same driver and the same function-object block. A rehearsal on
# one arm's configuration is therefore not evidence about another's.
#
# EXIT CODES
#   0  rehearsal ran and its verdict is in the record file (a FAIL is still exit 0)
#   2  a planted control did not fire -- the reader is not trusted, nothing is reported
#   3  the OpenFOAM environment did not come up
#   4  a source dictionary this rehearsal reads is missing
# =====================================================================================
set -uo pipefail

REPO=/home/ubuntu/Certonomous
SEEDARM="$REPO/verification/runs/RUNG2_CRM_runs/M0_compressible_admission/A0"
WORK=${1:?usage: rehearse_r2_m1_writers.sh <scratch workdir>}
OUT="$REPO/cases/committee-grids/R2_M1_WRITER_REHEARSAL.tsv"

ARMS="B0 B1 B2 B3 B4 B5 B6"
NSTEP=3

die() { echo "REHEARSAL DIED: $*" >&2; exit "${2:-4}"; }

for f in system/fvSchemes system/fvSolution constant/thermophysicalProperties \
         constant/turbulenceProperties; do
    [ -f "$SEEDARM/$f" ] || die "seed dictionary missing: $SEEDARM/$f" 4
done

# OpenFOAM's own bashrc dereferences unset variables; `set -u` turns that into a silent
# exit 1 before anything runs. Relax it for the source only, then restore.
set +u
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
command -v rhoSimpleFoam >/dev/null 2>&1 || die "rhoSimpleFoam not on PATH" 3
command -v blockMesh     >/dev/null 2>&1 || die "blockMesh not on PATH" 3

rm -rf "$WORK"; mkdir -p "$WORK"

# ------------------------------------------------------------------ the readers
# W1: count DISTINCT Time values carrying a record for a named field.
# W2: count intra-step solver lines.
# Both are defined ONCE here and used for the real read AND for the planted control, so
# the control exercises the same code path the measurement uses.
read_w1() {   # read_w1 <fieldMinMax.dat> <field> -> distinct Time count
    [ -f "$1" ] || { echo 0; return; }
    awk -v f="$2" '$1 !~ /^#/ && $2 == f { t[$1]=1 } END { print length(t) }' "$1"
}
# NOTE, and it cost a cycle: `grep -c PAT f || echo 0` emits TWO lines on no-match --
# grep -c prints "0" AND exits 1, so the `|| echo 0` fires too. The reader then returned
# "0\n0", `[` refused it as a non-integer, and the control was scored
# DOES_NOT_DISCRIMINATE for a reason that had nothing to do with discrimination. awk
# returns exactly one integer on every path, matched or not, file present or absent.
read_w2() {   # read_w2 <log> -> intra-step line count
    awk '/^pressureControl: p min/ || /^time step continuity errors/ { n++ }
         END { print n+0 }' "$1" 2>/dev/null || echo 0
}
read_steps() { # read_steps <log> -> COMPLETED steps (an ExecutionTime line ends a step)
    awk '/^ExecutionTime = / { n++ } END { print n+0 }' "$1" 2>/dev/null || echo 0
}

# ------------------------------------------------------------------ the tiny mesh
build_mesh() {
    local d=$1
    mkdir -p "$d/system" "$d/constant" "$d/0"
    cat > "$d/system/blockMeshDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }
scale 1;
vertices ( (0 0 0) (1 0 0) (1 1 0) (0 1 0) (0 0 1) (1 0 1) (1 1 1) (0 1 1) );
blocks ( hex (0 1 2 3 4 5 6 7) (5 5 5) simpleGrading (1 1 1) );
edges ();
boundary
(
    wall     { type wall;     faces ( (0 3 2 1) ); }
    symmetry { type symmetry; faces ( (1 5 4 0) ); }
    farfield { type patch;    faces ( (4 5 6 7) (2 6 5 1) (0 4 7 3) (3 7 6 2) ); }
);
mergePatchPairs ();
EOF
    cat > "$d/system/controlDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     rhoSimpleFoam;
startFrom       startTime; startTime 0;
stopAt          endTime;   endTime   3;
deltaT          1;
writeControl    timeStep;  writeInterval 120;
purgeWrite      0;
writeFormat     binary;    writePrecision 8; writeCompression off;
timeFormat      general;   timePrecision 6; runTimeModifiable false;
EOF
    blockMesh -case "$d" > "$d/log.blockMesh" 2>&1 || die "blockMesh failed in $d" 3
}

# ------------------------------------------------------------------ the fields
write_fields() {
    local d=$1
    _f() { # _f <name> <class> <dims> <internal> <wallbc> <ffbc>
        cat > "$d/0/$1" <<EOF
FoamFile { version 2.0; format ascii; class $2; location "0"; object $1; }
dimensions      [$3];
internalField   uniform $4;
boundaryField
{
    wall     { $5 }
    symmetry { type symmetry; }
    farfield { $6 }
}
EOF
    }
    _f p     volScalarField "1 -1 -2 0 0 0 0" "101325" \
             "type zeroGradient;" \
             "type freestreamPressure; freestreamValue uniform 101325; value uniform 101325;"
    _f T     volScalarField "0 0 0 1 0 0 0"   "300" \
             "type zeroGradient;" \
             "type freestream; freestreamValue uniform 300; value uniform 300;"
    _f U     volVectorField "0 1 -1 0 0 0 0"  "(50 0 0)" \
             "type noSlip;" \
             "type freestreamVelocity; freestreamValue uniform (50 0 0); value uniform (50 0 0);"
    _f k     volScalarField "0 2 -2 0 0 0 0"  "1.0" \
             "type kqRWallFunction; value uniform 1.0;" \
             "type freestream; freestreamValue uniform 1.0; value uniform 1.0;"
    _f omega volScalarField "0 0 -1 0 0 0 0"  "10.0" \
             "type omegaWallFunction; value uniform 10.0;" \
             "type freestream; freestreamValue uniform 10.0; value uniform 10.0;"
    _f nut   volScalarField "0 2 -1 0 0 0 0"  "0" \
             "type nutkWallFunction; value uniform 0;" \
             "type calculated; value uniform 0;"
    _f alphat volScalarField "1 -1 -1 0 0 0 0" "0" \
             "type compressible::alphatWallFunction; Prt 0.85; value uniform 0;" \
             "type calculated; value uniform 0;"
}

# ------------------------------------------------------------------ the writer block
# THIS IS THE BLOCK M1 REGISTERS. It is written here character-for-character as the
# registration will carry it, so that what is rehearsed IS what runs.
add_writers() {
    cat >> "$1/system/controlDict" <<'EOF'

functions
{
    r2m1MinMax
    {
        type            fieldMinMax;
        libs            (fieldFunctionObjects);
        writeControl    timeStep;
        writeInterval   1;
        mode            magnitude;
        log             true;
        fields          (T p rho U);
    }
}
EOF
}

add_bounds() {
    cat > "$1/constant/fvOptions" <<'EOF'
limitT
{
    type            limitTemperature;
    active          yes;
    selectionMode   all;
    min             100;
    max             1000;
}
EOF
    python3 - "$1/system/fvSolution" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
if "pMin" not in s:
    s2, n = re.subn(r"(rhoMin\s+[0-9.]+\s*;\s*rhoMax\s+[0-9.]+\s*;)",
                    r"\g<1> pMin 1000; pMax 1e7;", s, count=1)
    if n != 1:
        raise SystemExit("could not insert pressure bounds")
    open(p, "w").write(s2)
PY
}

# ------------------------------------------------------------------ assemble + run one arm
run_arm() {
    local arm=$1 d="$WORK/$arm"
    build_mesh "$d"
    write_fields "$d"
    cp -f "$SEEDARM/system/fvSchemes"                "$d/system/fvSchemes"
    cp -f "$SEEDARM/system/fvSolution"               "$d/system/fvSolution"
    cp -f "$SEEDARM/constant/thermophysicalProperties" "$d/constant/thermophysicalProperties"
    cp -f "$SEEDARM/constant/turbulenceProperties"   "$d/constant/turbulenceProperties"
    add_writers "$d"

    # the registered per-arm mutations, identical in text to what M1 will apply
    case "$arm" in
      B0) : ;;                                                    # seed, no bounds
      B2) : ;;                                                    # seed, no bounds, no FPE trap
      B1|B5) add_bounds "$d" ;;                                   # bounds, e, transonic no
      B3) add_bounds "$d"
          sed -i 's/sensibleInternalEnergy/sensibleEnthalpy/' "$d/constant/thermophysicalProperties" ;;
      B4) add_bounds "$d"
          sed -i 's/transonic no;/transonic yes;/'            "$d/system/fvSolution" ;;
      B6) add_bounds "$d"
          sed -i 's/sensibleInternalEnergy/sensibleEnthalpy/' "$d/constant/thermophysicalProperties"
          sed -i 's/transonic no;/transonic yes;/'            "$d/system/fvSolution" ;;
    esac

    local t0 t1
    t0=$(date +%s%N)
    if [ "$arm" = "B2" ]; then
        FOAM_SIGFPE=false rhoSimpleFoam -case "$d" > "$d/log.solve" 2>&1
    else
        rhoSimpleFoam -case "$d" > "$d/log.solve" 2>&1
    fi
    local rc=$?
    t1=$(date +%s%N)
    echo "$rc"  > "$d/rc.txt"
    echo "$(( (t1 - t0) / 1000000 ))" > "$d/wall_ms.txt"
}

# ===================================================================== MAIN
echo "R2-M1 WRITER REHEARSAL -- $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUT.tmp"
{
  echo "# 125-cell box, 1 rank, $NSTEP steps. NOT the DPW5 grid. A WRITER TEST ONLY."
  echo "# seed dictionaries: $SEEDARM"
  printf "arm\trc\twall_ms\tsteps_completed\tW1_T\tW1_p\tW1_rho\tW1_magU\tW2_intrastep\tW1_verdict\tW2_verdict\n"
} >> "$OUT.tmp"

TOT_MS=0
for arm in $ARMS; do
    run_arm "$arm"
    d="$WORK/$arm"
    rc=$(cat "$d/rc.txt"); ms=$(cat "$d/wall_ms.txt"); TOT_MS=$((TOT_MS + ms))
    dat="$d/postProcessing/r2m1MinMax/0/fieldMinMax.dat"
    st=$(read_steps "$d/log.solve")
    wT=$(read_w1 "$dat" T); wp=$(read_w1 "$dat" p)
    wr=$(read_w1 "$dat" rho); wu=$(read_w1 "$dat" "mag(U)")
    w2=$(read_w2 "$d/log.solve")
    # THE REGISTERED CONDITION: one record per COMPLETED step, per field. Not "some rows".
    if [ "$st" -gt 0 ] && [ "$wT" -eq "$st" ] && [ "$wp" -eq "$st" ] \
       && [ "$wr" -eq "$st" ] && [ "$wu" -eq "$st" ]; then v1=PASS; else v1=FAIL; fi
    if [ "$w2" -ge "$st" ] && [ "$st" -gt 0 ]; then v2=PASS; else v2=FAIL; fi
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$arm" "$rc" "$ms" "$st" "$wT" "$wp" "$wr" "$wu" "$w2" "$v1" "$v2" >> "$OUT.tmp"
done

# ------------------------------------------------------------------ PLANTED CONTROLS
# Rule 3. A reader that reports a number has not been shown able to report its ABSENCE,
# and a reader that reports an absence has not been shown able to see a presence. Both
# directions, on the SAME functions the measurement above used, on EVERY arm.
{
  echo ""
  echo "# PLANTED CONTROLS (rule 3) -- per arm, both directions, same reader functions"
  printf "arm\tW1_live\tW1_after_removal\tW1_after_restore\tW2_live\tW2_after_scrub\tW2_after_restore\tDISCRIMINATES\n"
} >> "$OUT.tmp"

CTRL_FAIL=0
for arm in $ARMS; do
    d="$WORK/$arm"
    dat="$d/postProcessing/r2m1MinMax/0/fieldMinMax.dat"
    log="$d/log.solve"

    a1=$(read_w1 "$dat" T)
    if [ -f "$dat" ]; then mv "$dat" "$dat.hidden"; fi
    b1=$(read_w1 "$dat" T)
    if [ -f "$dat.hidden" ]; then mv "$dat.hidden" "$dat"; fi
    c1=$(read_w1 "$dat" T)

    a2=$(read_w2 "$log")
    grep -v "^pressureControl: p min\|^time step continuity errors" "$log" > "$log.scrub" 2>/dev/null
    b2=$(read_w2 "$log.scrub")
    c2=$(read_w2 "$log")
    rm -f "$log.scrub"

    # DISCRIMINATES requires: live > 0, absent == 0, restored == live, on BOTH readers.
    if [ "$a1" -gt 0 ] && [ "$b1" -eq 0 ] && [ "$c1" -eq "$a1" ] \
    && [ "$a2" -gt 0 ] && [ "$b2" -eq 0 ] && [ "$c2" -eq "$a2" ]; then
        disc=DISCRIMINATES
    else
        disc=DOES_NOT_DISCRIMINATE; CTRL_FAIL=1
    fi
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$arm" "$a1" "$b1" "$c1" "$a2" "$b2" "$c2" "$disc" >> "$OUT.tmp"
done

{
  echo ""
  echo "# COST, MEASURED (rule 12)"
  echo "total_solver_wall_ms	$TOT_MS"
  echo "ranks	1"
  printf "core_min_MEASURED\t%.6f\n" "$(echo "$TOT_MS" | awk '{printf "%.6f", $1/1000/60}')"
  echo "cost_basis	on-box-owner-stated, c7a.4xlarge \$0.0513/core-h; DOLLARS DERIVED NOT MEASURED"
} >> "$OUT.tmp"

if [ "$CTRL_FAIL" -ne 0 ]; then
    echo "" >> "$OUT.tmp"
    echo "REHEARSAL VERDICT: REFUSED -- a planted control did not fire. No writer claim is made." >> "$OUT.tmp"
    mv "$OUT.tmp" "$OUT"
    echo "REFUSED: planted control did not fire" >&2
    exit 2
fi

echo "" >> "$OUT.tmp"
echo "REHEARSAL VERDICT: all planted controls DISCRIMINATE; per-arm writer verdicts above." >> "$OUT.tmp"
mv "$OUT.tmp" "$OUT"
exit 0
