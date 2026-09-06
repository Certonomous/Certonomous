#!/bin/bash
# =====================================================================================
# STAND-IN SEED BUILDER for the R2-M1 DRY RUN.
#
# WHY THIS EXISTS. `run_r2_m1.sh`'s cap, root guard, writer block and comparator have each
# been driven, but its PRODUCTION SEQUENCE -- assembly, then the warm-start
# reconstruct/guard/decompose chain, then the solve loop -- had never executed in ORDER.
# L-495: a selftest that exercises the PARTS but never the PRODUCTION SEQUENCE measures its
# own coverage, not the instrument, and it hides defects BEHIND each other. The fix for
# parts-coverage is to RUN THE SEQUENCE, not to run it bigger.
#
# The risk being bought down is NOT the 5.27 core-min. It is that a defect in assembly
# could produce a PLAUSIBLE WRONG ARTIFACT rather than a crash. A crash on the real grid we
# would see; a subtly mis-assembled arm we might grade.
#
# WHAT IT BUILDS. Two tiny decomposed cases with the SAME SHAPE the real ones have:
#
#   <dir>/seed   -- the compressible seed every arm is assembled from. Carries the REAL
#                   A0 dictionaries (thermophysicalProperties with sensibleInternalEnergy,
#                   fvSolution with `transonic no` and rhoMin/rhoMax, fvSchemes,
#                   turbulenceProperties) so every registered mutation -- the enthalpy sed,
#                   the transonic sed, the pMin/pMax insertion, the endTime rewrite, the
#                   writer-block insertion -- operates on the text it will operate on for
#                   real. Only the MESH is a stand-in.
#
#   <dir>/warm   -- the warm-start source, with processor*/200/{U,k,omega} ACTUALLY
#                   PRODUCED BY A SOLVER, and written in `writeFormat binary`.
#
# ⚠ THE BINARY FORMAT IS THE WHOLE POINT OF THE WARM CASE. M0's guard died reading a
# BINARY field in TEXT mode. A stand-in that wrote ASCII would sail through the repaired
# guard and prove nothing about the defect the repair exists for.
#
# ⚠ AND THE PATCH NAMES MUST BE wall / symmetry / farfield, because those are the three
# names the warm-start guard tests for. A stand-in with different patch names would drive
# the guard into its REFUSING branch and the dry run would report a mapping failure that is
# an artifact of the fixture.
#
# EXIT CODES: 0 built; 3 OpenFOAM did not come up; 4 a real dictionary is missing.
# =====================================================================================
set -uo pipefail

REPO=/home/ubuntu/Certonomous
REALARM="$REPO/verification/runs/RUNG2_CRM_runs/M0_compressible_admission/A0"
OUT=${1:?usage: build_r2_m1_standin.sh <output dir> [ranks]}
RANKS=${2:-4}
WARM_TIME=200

die() { echo "STAND-IN BUILD FAILED: $1" >&2; exit "${2:-4}"; }

for f in system/fvSchemes system/fvSolution constant/thermophysicalProperties \
         constant/turbulenceProperties; do
    [ -f "$REALARM/$f" ] || die "real dictionary missing: $REALARM/$f"
done

set +u
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
command -v blockMesh    >/dev/null 2>&1 || die "blockMesh not on PATH" 3
command -v decomposePar >/dev/null 2>&1 || die "decomposePar not on PATH" 3

rm -rf "$OUT"; mkdir -p "$OUT"

# ---------------------------------------------------------------- shared pieces

write_mesh_dict() {
    mkdir -p "$1/system" "$1/constant" "$1/0"
    cat > "$1/system/blockMeshDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }
scale 1;
vertices ( (0 0 0) (1 0 0) (1 1 0) (0 1 0) (0 0 1) (1 0 1) (1 1 1) (0 1 1) );
blocks ( hex (0 1 2 3 4 5 6 7) (6 6 6) simpleGrading (1 1 1) );
edges ();
boundary
(
    wall     { type wall;     faces ( (0 3 2 1) ); }
    symmetry { type symmetry; faces ( (1 5 4 0) ); }
    farfield { type patch;    faces ( (4 5 6 7) (2 6 5 1) (0 4 7 3) (3 7 6 2) ); }
);
mergePatchPairs ();
EOF
    cat > "$1/system/decomposeParDict" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $RANKS;
method scotch;
EOF
}

write_field() {  # write_field <case> <name> <class> <dims> <internal> <wallBC> <ffBC>
    cat > "$1/0/$2" <<EOF
FoamFile { version 2.0; format ascii; class $3; location "0"; object $2; }
dimensions      [$4];
internalField   uniform $5;
boundaryField
{
    wall     { $6 }
    symmetry { type symmetry; }
    farfield { $7 }
}
EOF
}

write_common_fields() {
    write_field "$1" U volVectorField "0 1 -1 0 0 0 0" "(30 0 0)" \
        "type noSlip;" \
        "type freestreamVelocity; freestreamValue uniform (30 0 0); value uniform (30 0 0);"
    write_field "$1" k volScalarField "0 2 -2 0 0 0 0" "1.0" \
        "type kqRWallFunction; value uniform 1.0;" \
        "type freestream; freestreamValue uniform 1.0; value uniform 1.0;"
    write_field "$1" omega volScalarField "0 0 -1 0 0 0 0" "10.0" \
        "type omegaWallFunction; value uniform 10.0;" \
        "type freestream; freestreamValue uniform 10.0; value uniform 10.0;"
    write_field "$1" nut volScalarField "0 2 -1 0 0 0 0" "0" \
        "type nutkWallFunction; value uniform 0;" "type calculated; value uniform 0;"
}

# ---------------------------------------------------------------- the WARM source
# Fields are PRODUCED BY A SOLVER, not fabricated, and written in BINARY -- the format that
# killed M0's guard.

WARMC="$OUT/warm"
write_mesh_dict "$WARMC"
write_common_fields "$WARMC"
write_field "$WARMC" p volScalarField "0 2 -2 0 0 0 0" "0" \
    "type zeroGradient;" "type freestreamPressure; freestreamValue uniform 0; value uniform 0;"
cat > "$WARMC/constant/transportProperties" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object transportProperties; }
transportModel Newtonian;
nu 1.5e-05;
EOF
cp -f "$REALARM/constant/turbulenceProperties" "$WARMC/constant/turbulenceProperties"
cat > "$WARMC/system/controlDict" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     simpleFoam;
startFrom       startTime; startTime 0;
stopAt          endTime;   endTime   $WARM_TIME;
deltaT          1;
writeControl    timeStep;  writeInterval $WARM_TIME;
purgeWrite      0;
writeFormat     binary;    writePrecision 8; writeCompression off;
timeFormat      general;   timePrecision 6; runTimeModifiable false;
EOF
cat > "$WARMC/system/fvSchemes" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes      { default none; div(phi,U) bounded Gauss upwind;
                  div(phi,k) bounded Gauss upwind; div(phi,omega) bounded Gauss upwind;
                  div((nuEff*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes{ default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
wallDist        { method meshWave; }
EOF
cat > "$WARMC/system/fvSolution" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    p { solver GAMG; tolerance 1e-06; relTol 0.05; smoother GaussSeidel; }
    "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-05; relTol 0.1; }
}
SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; }
relaxationFactors { equations { U 0.9; ".*" 0.9; } }
EOF
blockMesh    -case "$WARMC" > "$WARMC/log.blockMesh"    2>&1 || die "warm blockMesh"
decomposePar -case "$WARMC" > "$WARMC/log.decomposePar" 2>&1 || die "warm decomposePar"
mpirun -np "$RANKS" simpleFoam -case "$WARMC" -parallel > "$WARMC/log.simpleFoam" 2>&1 \
    || die "warm simpleFoam did not run"

for i in $(seq 0 $((RANKS-1))); do
    for f in U k omega; do
        [ -f "$WARMC/processor$i/$WARM_TIME/$f" ] \
            || die "warm source has no processor$i/$WARM_TIME/$f -- the dry run could not exercise the warm-start chain"
    done
done
# ASSERT THE FIELD IS ACTUALLY BINARY. If it is not, the dry run would exercise the guard
# on ASCII and prove nothing about the defect the repair exists for.
head -c 4096 "$WARMC/processor0/$WARM_TIME/U" | grep -q "format *binary" \
    || die "warm processor0/$WARM_TIME/U is NOT binary -- the dry run would not exercise the guard's repair"
echo "STAND-IN warm source: processor*/$WARM_TIME/{U,k,omega} produced by simpleFoam, BINARY -- verified"

# ---------------------------------------------------------------- the SEED
# Carries the REAL A0 dictionaries so every registered mutation edits real text.

SEEDC="$OUT/seed"
write_mesh_dict "$SEEDC"
write_common_fields "$SEEDC"
write_field "$SEEDC" p volScalarField "1 -1 -2 0 0 0 0" "101325" \
    "type zeroGradient;" \
    "type freestreamPressure; freestreamValue uniform 101325; value uniform 101325;"
write_field "$SEEDC" T volScalarField "0 0 0 1 0 0 0" "300" \
    "type zeroGradient;" "type freestream; freestreamValue uniform 300; value uniform 300;"
write_field "$SEEDC" alphat volScalarField "1 -1 -1 0 0 0 0" "0" \
    "type compressible::alphatWallFunction; Prt 0.85; value uniform 0;" \
    "type calculated; value uniform 0;"

cp -f "$REALARM/system/fvSchemes"                  "$SEEDC/system/fvSchemes"
cp -f "$REALARM/system/fvSolution"                 "$SEEDC/system/fvSolution"
cp -f "$REALARM/constant/thermophysicalProperties" "$SEEDC/constant/thermophysicalProperties"
cp -f "$REALARM/constant/turbulenceProperties"     "$SEEDC/constant/turbulenceProperties"
# ⚠ ONE KEY PER LINE, AND `endTime` ON A LINE OF ITS OWN.
# The driver's mutations are TEXT operations on this file, and `set_endtime` anchors on
# `^\s*endTime\s+<number>;`. The first build of this stand-in wrote
# `stopAt endTime;   endTime 120;` on ONE line -- semantically identical, textually
# different -- and the driver refused with "endTime not rewritten", exit 7.
# THE REAL SEED HAS THEM ON SEPARATE LINES (A0/system/controlDict:12-13), so this was a
# FIXTURE defect, not a driver defect, and the driver was right to refuse. A stand-in for a
# text-mutating driver must reproduce the seed's LINE SHAPE, not merely its meaning.
cat > "$SEEDC/system/controlDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     rhoSimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         120;
deltaT          1;
writeControl    timeStep;
writeInterval   120;
purgeWrite      0;
writeFormat     binary;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
EOF

# EVERY mutation the driver applies must have text to bite on. Asserted HERE rather than
# discovered as a silent no-op -- or, as happened on the first build, as an exit 7 four
# steps into the sequence.
# ⚠ THIS LIST WAS INCOMPLETE ONCE ALREADY: it checked three anchors and omitted `endTime`,
# because that line was hand-written here and assumed correct. An enumeration that can
# silently be incomplete is the same failure mode as cleaning up globals by listing them.
# If you add a mutation to the driver, add its anchor here.
grep -q sensibleInternalEnergy "$SEEDC/constant/thermophysicalProperties" \
    || die "seed thermophysicalProperties has no sensibleInternalEnergy -- the B3/B6 sed would be a silent no-op"
grep -q 'transonic no;' "$SEEDC/system/fvSolution" \
    || die "seed fvSolution has no 'transonic no;' -- the B4/B6 sed would be a silent no-op"
grep -qE 'rhoMin +[0-9.]+ *; *rhoMax +[0-9.]+ *;' "$SEEDC/system/fvSolution" \
    || die "seed fvSolution has no rhoMin/rhoMax pair -- add_bounds would take its fallback branch"
grep -qE '^ *endTime +[0-9.]+ *;' "$SEEDC/system/controlDict" \
    || die "seed controlDict has no line-anchored 'endTime <n>;' -- set_endtime would refuse (exit 7)"
grep -qE '^functions' "$SEEDC/system/controlDict" \
    && die "seed controlDict already has a functions block -- add_writers' insert branch would differ from the real seed's"

blockMesh    -case "$SEEDC" > "$SEEDC/log.blockMesh"    2>&1 || die "seed blockMesh"
decomposePar -case "$SEEDC" > "$SEEDC/log.decomposePar" 2>&1 || die "seed decomposePar"

cells=$(awk '/^ *nCells:/ {print $2}' "$SEEDC/log.blockMesh" | tail -1)
echo "STAND-IN seed: ${cells:-?} cells, $RANKS subdomains, REAL A0 dictionaries, all three mutation anchors present"
echo "STAND-IN BUILT: $OUT"
exit 0
