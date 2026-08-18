#!/bin/bash
# W3 channel-M setup: one shared mesh, five closures, everything else identical.
# The mesh is built ONCE and copied, so no member can differ by a mesh detail.
source /usr/lib/openfoam/openfoam2606/etc/bashrc 2>/dev/null || true
set -eo pipefail
ROOT=/home/ubuntu/Certonomous/demo-output/website/campaign/W3_runs
ACT=/home/ubuntu/Certonomous/mission-output/ahmed-body/act7-ahmed_25/case

# --- shared mesh -----------------------------------------------------------
if [ ! -d "$ROOT/mesh/constant/polyMesh" ]; then
  rm -rf "$ROOT/mesh"; mkdir -p "$ROOT/mesh"
  cp -r "$ACT"/0 "$ACT"/constant "$ACT"/system "$ROOT/mesh"/
  cd "$ROOT/mesh"
  blockMesh                 > log.blockMesh 2>&1
  surfaceFeatureExtract     > log.surfaceFeatureExtract 2>&1
  snappyHexMesh -overwrite  > log.snappyHexMesh 2>&1
  checkMesh                 > log.checkMesh 2>&1
fi
grep -m1 "    cells:" "$ROOT/mesh/log.checkMesh"

# --- freestream values, all derived from the act's own 0/ fields ------------
# k = 0.24, omega = 8.56731  ->  nut_inf = k/omega = 0.02801375
# epsilon_inf = Cmu*k*omega  = 0.09*0.24*8.56731 = 0.18505390
# nuTilda_inf is set to nut_inf so every member starts from the SAME freestream
# eddy viscosity rather than an arbitrary multiple of nu. Declared, not assumed.
EPS=0.18505390
NUT=0.02801375

mkfield () { # name dim value wallfn
  cat > "$1" <<EOF
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      $2;
}

dimensions      $3;

internalField   uniform $4;

boundaryField
{
    farfield
    {
        type            inletOutlet;
        inletValue      uniform $4;
        value           uniform $4;
    }
    body
    {
        type            $5;
        value           uniform $4;
    }
}
EOF
}

for M in kOmegaSST kEpsilon kOmega realizableKE SpalartAllmaras; do
  D="$ROOT/$M"
  rm -rf "$D"; mkdir -p "$D"
  cp -r "$ROOT/mesh/0" "$ROOT/mesh/constant" "$ROOT/mesh/system" "$D"/

  # closure
  sed -i "s/RASModel        kOmegaSST;/RASModel        $M;/" "$D/constant/turbulenceProperties"

  # extra transported fields
  case "$M" in
    kEpsilon|realizableKE)
      mkfield "$D/0/epsilon" epsilon "[0 2 -3 0 0 0 0]" "$EPS" epsilonWallFunction ;;
    SpalartAllmaras)
      mkfield "$D/0/nuTilda" nuTilda "[0 2 -1 0 0 0 0]" "$NUT" fixedValue
      sed -i 's/type            nutkWallFunction;/type            nutUSpaldingWallFunction;/' "$D/0/nut" ;;
  esac

  # schemes for the extra fields (same limitedLinear 1 the act uses for k/omega)
  sed -i 's|div(phi,omega)  bounded Gauss limitedLinear 1;|div(phi,omega)  bounded Gauss limitedLinear 1;\n    div(phi,epsilon) bounded Gauss limitedLinear 1;\n    div(phi,nuTilda) bounded Gauss limitedLinear 1;|' "$D/system/fvSchemes"

  # solvers and residualControl for the extra fields
  sed -i 's|"(U\|k\|omega)"|"(U\|k\|omega\|epsilon\|nuTilda)"|' "$D/system/fvSolution"
  sed -i 's|"(k\|omega)" 1e-4;|"(k\|omega\|epsilon\|nuTilda)" 1e-4;|' "$D/system/fvSolution"

  # room to converge; the act's 300 was enough for SST only
  sed -i 's/^endTime         300;/endTime         4000;/' "$D/system/controlDict"
  sed -i 's/^writeInterval   300;/writeInterval   4000;/' "$D/system/controlDict"
done
echo "SETUP OK"
