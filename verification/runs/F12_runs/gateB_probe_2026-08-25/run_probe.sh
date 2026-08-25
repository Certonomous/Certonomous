#!/bin/bash
# F12 GATE-B PROBE -- does rhoSimpleFoam print its own convergence statement on
# this box AT ALL?  Runs OUTSIDE the repository and outside every registered run
# path.  Touches no registered case, no gate, no threshold.
set -u
PB=/home/ubuntu/certonomous-runs/F12_gateB_probe_2026-08-25
REPO=/home/ubuntu/Certonomous
F12=$REPO/verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79

# ---- ASSERT the registered roots before ----------------------------------
for d in attempt2_medium_workshop_M0.734_a2.79 attempt2_fine_workshop_M0.734_a2.79 \
         attempt2_medium_tape_M0.730_a2.79 attempt2_medium_farfield2x_M0.734_a2.79; do
  [ -e "$REPO/verification/runs/F12_runs/$d" ] && { echo "ABORT: $d exists"; exit 1; }
done
ls -d $REPO/verification/runs/F12_runs/attempt3* >/dev/null 2>&1 && { echo "ABORT: attempt3 exists"; exit 1; }
find $F12 -type f | sort | xargs sha256sum 2>/dev/null | sha256sum > $PB/rung1_fingerprint_before.txt
echo "PRE-ASSERT OK  $(date -u +%FT%TZ)"

mk_box () {   # $1 = case dir
  local C=$1; mkdir -p $C/0 $C/constant $C/system
  cat > $C/system/blockMeshDict <<'EOF'
FoamFile{version 2.0;format ascii;class dictionary;object blockMeshDict;}
scale 1;
vertices ((0 0 0)(2 0 0)(2 0.5 0)(0 0.5 0)(0 0 0.05)(2 0 0.05)(2 0.5 0.05)(0 0.5 0.05));
blocks (hex (0 1 2 3 4 5 6 7) (40 10 1) simpleGrading (1 1 1));
edges ();
boundary
(
    inlet  { type patch; faces ((0 3 7 4)); }
    outlet { type patch; faces ((1 2 6 5)); }
    walls  { type wall;  faces ((0 1 5 4)(3 2 6 7)); }
    frontAndBack { type empty; faces ((0 1 2 3)(4 5 6 7)); }
);
EOF
}

# =========================== ARM 1: rhoSimpleFoam ==========================
A=$PB/arm1_rhoSimpleFoam_rc1e-1
mk_box $A
cp $F12/constant/thermophysicalProperties $A/constant/
cp $F12/constant/turbulenceProperties     $A/constant/
cp $F12/system/fvSchemes                  $A/system/
# F12's fvSolution with residualControl LOOSENED TO 1e-1 -- in the PROBE ONLY.
# The registered case is NOT touched: loosening a registered threshold is a
# threshold change and is not available post-freeze.
sed -e 's/p               1e-06;/p               1e-1;/' \
    -e 's/U               1e-06;/U               1e-1;/' \
    -e 's/"(k|omega|e)"   1e-06;/"(k|omega|e)"   1e-1;/' \
    $F12/system/fvSolution > $A/system/fvSolution
cat > $A/system/controlDict <<'EOF'
FoamFile{version 2.0;format ascii;class dictionary;object controlDict;}
application rhoSimpleFoam; startFrom startTime; startTime 0; stopAt endTime;
endTime 500; deltaT 1; writeControl timeStep; writeInterval 500; purgeWrite 1;
EOF
head_field () { cat <<EOF
FoamFile{version 2.0;format ascii;class $1;object $2;}
dimensions      $3;
internalField   uniform $4;
boundaryField
{
    inlet  { type fixedValue; value uniform $4; }
    outlet { type zeroGradient; }
    walls  { type $5; }
    frontAndBack { type empty; }
}
EOF
}
head_field volScalarField T "[0 0 0 1 0 0 0]" 300           "zeroGradient"  > $A/0/T
head_field volVectorField U "[0 1 -1 0 0 0 0]" "(20 0 0)"   "noSlip"        > $A/0/U
head_field volScalarField p "[1 -1 -2 0 0 0 0]" 100000      "zeroGradient"  > $A/0/p
head_field volScalarField k "[0 2 -2 0 0 0 0]" 0.1          "kqRWallFunction; value uniform 0.1" > $A/0/k
head_field volScalarField omega "[0 0 -1 0 0 0 0]" 10       "omegaWallFunction; value uniform 10" > $A/0/omega
head_field volScalarField nut "[0 2 -1 0 0 0 0]" 0          "nutkWallFunction; value uniform 0"   > $A/0/nut
head_field volScalarField alphat "[1 -1 -1 0 0 0 0]" 0      "compressible::alphatWallFunction; Prt 0.85; value uniform 0" > $A/0/alphat
sed -i 's/{ type fixedValue; value uniform 100000; }/{ type zeroGradient; }/' $A/0/p
sed -i 's/{ type zeroGradient; }$/{ type fixedValue; value uniform 100000; }/' $A/0/p
# outlet must fix p, inlet zeroGradient -- rewrite p cleanly
cat > $A/0/p <<'EOF'
FoamFile{version 2.0;format ascii;class volScalarField;object p;}
dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 100000;
boundaryField
{
    inlet  { type zeroGradient; }
    outlet { type fixedValue; value uniform 100000; }
    walls  { type zeroGradient; }
    frontAndBack { type empty; }
}
EOF

# =========================== ARM 2: simpleFoam control =====================
B=$PB/arm2_simpleFoam_rc1e-1_CONTROL
mk_box $B
cp $A/0/U $A/0/k $A/0/omega $A/0/nut $B/0/ 2>/dev/null
cp $A/system/fvSchemes $B/system/
cat > $B/0/p <<'EOF'
FoamFile{version 2.0;format ascii;class volScalarField;object p;}
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    inlet  { type zeroGradient; }
    outlet { type fixedValue; value uniform 0; }
    walls  { type zeroGradient; }
    frontAndBack { type empty; }
}
EOF
cat > $B/constant/transportProperties <<'EOF'
FoamFile{version 2.0;format ascii;class dictionary;object transportProperties;}
transportModel  Newtonian;
nu              1e-05;
EOF
cp $F12/constant/turbulenceProperties $B/constant/
cat > $B/system/fvSolution <<'EOF'
FoamFile{version 2.0;format ascii;class dictionary;object fvSolution;}
solvers
{
    p { solver GAMG; tolerance 1e-08; relTol 0.01; smoother GaussSeidel; }
    "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-08; relTol 0.1; }
}
SIMPLE
{
    residualControl { p 1e-1; U 1e-1; "(k|omega)" 1e-1; }
    nNonOrthogonalCorrectors 0;
    consistent no;
}
relaxationFactors { fields { p 0.3; } equations { U 0.7; "(k|omega)" 0.7; } }
EOF
cat > $B/system/controlDict <<'EOF'
FoamFile{version 2.0;format ascii;class dictionary;object controlDict;}
application simpleFoam; startFrom startTime; startTime 0; stopAt endTime;
endTime 500; deltaT 1; writeControl timeStep; writeInterval 500; purgeWrite 1;
EOF

# =========================== run both ======================================
for CASE in $A $B; do
  APP=$(grep -oE '^application [a-zA-Z]+' $CASE/system/controlDict | awk '{print $2}')
  ( cd $CASE && openfoam2606 blockMesh > log.blockMesh 2>&1; echo "$?" > RC.blockMesh )
  T0=$(date +%s.%N)
  ( cd $CASE && openfoam2606 $APP > log.$APP 2>&1; echo "$?" > RC.txt; sync )
  T1=$(date +%s.%N)
  echo "$(echo "$T1 - $T0" | bc)" > $CASE/WALL_S.txt
done

# ---- ASSERT the registered roots after ------------------------------------
find $F12 -type f | sort | xargs sha256sum 2>/dev/null | sha256sum > $PB/rung1_fingerprint_after.txt
cmp -s $PB/rung1_fingerprint_before.txt $PB/rung1_fingerprint_after.txt \
  && echo "POST-ASSERT OK: rung 1's directory is byte-unchanged by the probe" \
  || echo "POST-ASSERT FAILED: rung 1's directory CHANGED"
for d in attempt2_medium_workshop_M0.734_a2.79 attempt2_fine_workshop_M0.734_a2.79 \
         attempt2_medium_tape_M0.730_a2.79 attempt2_medium_farfield2x_M0.734_a2.79; do
  [ -e "$REPO/verification/runs/F12_runs/$d" ] && echo "POST-ASSERT FAILED: $d appeared"
done
echo "POST-ASSERT: rungs 2-5 still absent"
