#!/bin/bash
# Build the M6I SOLVE CHAIN on all three existing TMR-generator levels.
#
#   ONE script, all three levels, so they stay similar (Sanaa, run instructions).
#   NO SOLVER IS LAUNCHED BY THIS SCRIPT.  It patches, dictionaries and inspects only.
#   It writes 0.orig/ and NEVER 0/ -- the age guard (CLAUDE.md rule 4) refuses a cwd
#   that already holds a time directory, and launch_m6i.sh materialises 0/ LAST.
#
# The meshes are single-patch (`defaultFaces`, type wall) as plot3dToFoam left them.
# The split is GEOMETRIC and was measured, not guessed:
#   symmetry  face centre y  < 1e-8            (the root plane; the grid is y >= 0)
#   wing      1e-6 <= y, |z| <= 1, -3 <= x <= 4 (the near-field body)
#   farfield  everything else (the r = 100 hemisphere about (0.5, 0, 0))
# Arithmetic check that the split is exhaustive and level-independent:
#   L3 768 + 480 + 480 = 1728;  L2 3072 + 1920 + 1920 = 6912;  L1 12288 + 7680 + 7680 = 27648
# which are exactly the nFaces in each level's own constant/polyMesh/boundary.
set -u
RUNS="$(cd "$(dirname "$0")" && pwd)"
COST="$RUNS/COST_SOLVECHAIN.tsv"
printf 'stage\twall_s\tranks\tcore_min\n' > "$COST"
t0=$(date +%s)
timed () { local name="$1" ranks="$2"; shift 3
  local s=$(date +%s); "$@"; local rc=$?; local w=$(( $(date +%s) - s ))
  printf '%s\t%d\t%d\t%.4f\n' "$name" "$w" "$ranks" "$(python3 -c "print($w*$ranks/60)")" >> "$COST"
  return $rc; }

set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1; set -u
command -v topoSet >/dev/null || { echo "NO OPENFOAM"; exit 1; }

# ---------------- the registered freestream, computed once, printed once -------------
python3 - "$RUNS" <<'PY'
import json,math,sys
R_u=8314.4621; MW=28.97; Cp=1005.0
R=R_u/MW; gamma=Cp/(Cp-R)
T=300.0; p=101325.0
M=0.8395                      # AGARD AR-138 TABLE B1-14 TEST 2308
alpha=3.06                    # degrees, same table header
Re_root=14.6e6                # input.nml target_reynolds_number, root chord = 1.0
a=math.sqrt(gamma*R*T); U=M*a; rho=p/(R*T); q=0.5*rho*U*U
L=1.0; mu=rho*U*L/Re_root; nu=mu/rho
# Sutherland constants: Ts fixed at the standard 110.4 K, As chosen so that mu(300 K) is
# EXACTLY the mu that puts the root-chord Reynolds number on the mesh's own design value
# 14.6e6 -- which is AGARD TEST 2308's Re 11.72e6 on the MAC re-referenced to the root
# chord (11.72e6 * 0.8059/0.64607 = 14.62e6).  The transport law is Sutherland, not const.
Ts=110.4; As=mu*(T+Ts)/T**1.5
b=1.4760179762198             # input.nml b, semi-span per unit root chord
tr=0.5625159852668158         # input.nml taper ratio
Aref=0.5*(1.0+tr)*b           # semispan planform area, grid units^2
lRef=0.64607/0.8059           # AGARD MAC / root chord, in grid units
d=dict(As_sutherland=As,Ts_sutherland=Ts,R_specific=R,gamma=gamma,T_inf=T,p_inf=p,M_inf=M,alpha_deg=alpha,
       a_inf=a,U_inf=U,rho_inf=rho,q_inf=q,mu=mu,nu=nu,Re_root_chord=Re_root,
       Ux=U*math.cos(math.radians(alpha)),Uy=0.0,Uz=U*math.sin(math.radians(alpha)),
       nuTilda_inf=3.0*nu,b_semi=b,taper_ratio=tr,Aref=Aref,lRef=lRef,c_root=1.0)
json.dump(d,open(sys.argv[1]+"/FREESTREAM_M6I.json","w"),indent=1)
for k,v in d.items(): print("%-16s %.10g"%(k,v))
PY
[ -f "$RUNS/FREESTREAM_M6I.json" ] || { echo "FREESTREAM COMPUTE FAILED"; exit 1; }
eval "$(python3 -c "
import json;d=json.load(open('$RUNS/FREESTREAM_M6I.json'))
for k in ('Ux','Uy','Uz','p_inf','T_inf','mu','nuTilda_inf','U_inf','rho_inf','Aref','lRef','M_inf','alpha_deg'):
    print('%s=%.12g'%(k,d[k]))
print('As_SUTH=%.12g'%d['As_sutherland'])
import math
print('liftDirZ=%.12g'%math.cos(math.radians(d['alpha_deg'])))
print('liftDirX=%.12g'%(-math.sin(math.radians(d['alpha_deg']))))
print('dragDirX=%.12g'%math.cos(math.radians(d['alpha_deg'])))
print('dragDirZ=%.12g'%math.sin(math.radians(d['alpha_deg'])))
")"

# ---------------- per-level endTime / writeInterval, registered ----------------------
# writeInterval 200 on every level: the directive's OWN fallback -- "if the rate is
# unknown, checkpoint every 200 iterations until it is" -- and the rate IS unknown
# because no M6I solve has ever run.  endTime/200 is an exact integer on every level so
# the last write lands ON endTime.  purgeWrite 2 keeps the last two.
endtime_for () { case "$1" in L1) echo 8000;; L2) echo 5000;; L3) echo 3000;; esac; }

for L in L3 L2 L1; do
  C="$RUNS/$L"
  echo "=================== $L ==================="
  [ -d "$C/constant/polyMesh" ] || { echo "$L: NO MESH"; exit 1; }
  for t in "$C"/[0-9]* ; do [ -e "$t" ] && { echo "$L: AGE GUARD -- time directory $t exists, refusing"; exit 1; }; done
  ET=$(endtime_for "$L")
  mkdir -p "$C/system" "$C/constant" "$C/0.orig"

  # ---------- topoSet: the three face sets -----------------------------------------
  cat > "$C/system/topoSetDict" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object topoSetDict; }
actions
(
    { name symmetry; type faceSet; action new;    source boundaryToFace; }
    { name symmetry; type faceSet; action subset; source boxToFace; box (-200 -1e-8 -200) (200 1e-8 200); }

    { name wing;     type faceSet; action new;    source boundaryToFace; }
    { name wing;     type faceSet; action subset; source boxToFace; box (-3 1e-6 -1) (4 3 1); }

    { name farfield; type faceSet; action new;    source boundaryToFace; }
    { name farfield; type faceSet; action subtract; source faceToFace; sets (symmetry); }
    { name farfield; type faceSet; action subtract; source faceToFace; sets (wing); }
);
EOF
  cat > "$C/system/createPatchDict" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object createPatchDict; }
pointSync false;
patches
(
    { name wing;     patchInfo { type wall; }     constructFrom set; set wing; }
    { name symmetry; patchInfo { type symmetry; } constructFrom set; set symmetry; }
    { name farfield; patchInfo { type patch; }    constructFrom set; set farfield; }
);
EOF
  # a minimal controlDict must exist before topoSet runs
  cat > "$C/system/controlDict" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     rhoSimpleFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         $ET;
deltaT          1;
writeControl    timeStep;
writeInterval   200;
purgeWrite      2;
writeFormat     binary;
writePrecision  10;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
functions
{
    forceCoeffs
    {
        type            forceCoeffs;
        libs            (forces);
        writeControl    timeStep;
        writeInterval   1;
        log             yes;
        patches         (wing);
        rho             rho;
        rhoInf          $rho_inf;
        magUInf         $U_inf;
        lRef            $lRef;
        Aref            $Aref;
        CofR            (0.25 0 0);
        liftDir         ($liftDirX 0 $liftDirZ);
        dragDir         ($dragDirX 0 $dragDirZ);
        pitchAxis       (0 1 0);
    }
    residuals
    {
        type            solverInfo;
        libs            (utilityFunctionObjects);
        writeControl    timeStep;
        writeInterval   1;
        fields          (U p e nuTilda);
    }
    yPlus
    {
        type            yPlus;
        libs            (fieldFunctionObjects);
        writeControl    writeTime;
        patches         (wing);
    }
}
EOF
  ( cd "$C" && timed "topoSet_$L" 1 -- topoSet > log.topoSet 2>&1 ) || { echo "$L topoSet FAILED"; tail -20 "$C/log.topoSet"; exit 1; }
  ( cd "$C" && timed "createPatch_$L" 1 -- createPatch -overwrite > log.createPatch 2>&1 ) || { echo "$L createPatch FAILED"; tail -20 "$C/log.createPatch"; exit 1; }

  # ---------- constant/ ------------------------------------------------------------
  cat > "$C/constant/thermophysicalProperties" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; location "constant"; object thermophysicalProperties; }
thermoType
{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       sutherland;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleInternalEnergy;
}
mixture
{
    specie          { molWeight 28.97; }
    thermodynamics  { Cp 1005; Hf 0; }
    transport       { As $As_SUTH; Ts 110.4; }
}
EOF
  cat > "$C/constant/turbulenceProperties" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; location "constant"; object turbulenceProperties; }
simulationType  RAS;
RAS
{
    RASModel        SpalartAllmaras;
    turbulence      on;
    printCoeffs     on;
}
EOF

  # ---------- system/ --------------------------------------------------------------
  cat > "$C/system/fvSchemes" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes      { default steadyState; }
gradSchemes
{
    default         Gauss linear;
    limitedGrad     cellLimited Gauss linear 1;
    grad(U)         $limitedGrad;
    grad(nuTilda)   $limitedGrad;
    grad(e)         $limitedGrad;
}
divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind limitedGrad;
    div(phi,e)      bounded Gauss linearUpwind limitedGrad;
    div(phi,K)      bounded Gauss linearUpwind limitedGrad;
    div(phi,Ekp)    bounded Gauss linearUpwind limitedGrad;
    div(phi,nuTilda) bounded Gauss upwind;
    div(phid,p)     Gauss upwind;
    div((phi|interpolate(rho)),p) bounded Gauss upwind;
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}
// max non-orthogonality on this family is 86.5-87.7 deg on EVERY level (R0_RESULTS
// section 3).  'limited corrected 0.33' is the registered remedy and it is applied
// identically on all three levels so the family stays similar.
laplacianSchemes { default Gauss linear limited corrected 0.33; }
interpolationSchemes { default linear; }
snGradSchemes   { default limited corrected 0.33; }
wallDist        { method meshWave; }
EOF
  cat > "$C/system/fvSolution" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    p
    {
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-9;
        relTol          0.01;
        nCellsInCoarsestLevel 100;
    }
    "(U|e|nuTilda)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-10;
        relTol          0.01;
    }
}
SIMPLE
{
    nNonOrthogonalCorrectors 2;
    pMinFactor      0.2;
    pMaxFactor      2.0;
    transonic       yes;
    consistent      yes;
    // NO residualControl BY REGISTRATION.  A residualControl exit stops the solver
    // BEFORE endTime, and rule 4's completion clause reads last time == endTime.
    // Convergence is graded from the residual and coefficient histories instead
    // (IC-1..IC-4 of the pre-registration), never by letting the solver decide.
}
relaxationFactors
{
    fields    { p 1; rho 0.05; }
    equations { p 1; U 0.7; e 0.7; nuTilda 0.7; }
}
EOF
  cat > "$C/system/decomposeParDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
// hierarchical, NOT scotch: scotch is non-deterministic across runs and the graded
// quantity is read off a surface field.  4 ranks on every level, registered.
numberOfSubdomains 4;
method          hierarchical;
coeffs          { n (2 2 1); }
EOF

  # ---------- 0.orig/ ---------------------------------------------------------------
  cat > "$C/0.orig/U" <<EOF
FoamFile { version 2.0; format ascii; class volVectorField; location "0"; object U; }
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ($Ux $Uy $Uz);
boundaryField
{
    wing     { type noSlip; }
    symmetry { type symmetry; }
    farfield { type freestreamVelocity; freestreamValue uniform ($Ux $Uy $Uz); value uniform ($Ux $Uy $Uz); }
}
EOF
  cat > "$C/0.orig/p" <<EOF
FoamFile { version 2.0; format ascii; class volScalarField; location "0"; object p; }
dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform $p_inf;
boundaryField
{
    wing     { type zeroGradient; }
    symmetry { type symmetry; }
    farfield { type freestreamPressure; freestreamValue uniform $p_inf; value uniform $p_inf; }
}
EOF
  cat > "$C/0.orig/T" <<EOF
FoamFile { version 2.0; format ascii; class volScalarField; location "0"; object T; }
dimensions      [0 0 0 1 0 0 0];
internalField   uniform $T_inf;
boundaryField
{
    wing     { type zeroGradient; }
    symmetry { type symmetry; }
    farfield { type inletOutlet; inletValue uniform $T_inf; value uniform $T_inf; }
}
EOF
  cat > "$C/0.orig/nuTilda" <<EOF
FoamFile { version 2.0; format ascii; class volScalarField; location "0"; object nuTilda; }
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform $nuTilda_inf;
boundaryField
{
    wing     { type fixedValue; value uniform 0; }
    symmetry { type symmetry; }
    farfield { type freestream; freestreamValue uniform $nuTilda_inf; value uniform $nuTilda_inf; }
}
EOF
  cat > "$C/0.orig/nut" <<'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; location "0"; object nut; }
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    // y+ is 0.25 / 0.5 / 1.0 on L1 / L2 / L3 by construction (R0_RESULTS section 1:
    // target_y_plus 0.25 on the fine level, doubled by each coarsening).  Every level
    // is wall-resolved, so the LOW-Re wall treatment is the registered one.
    wing     { type nutLowReWallFunction; value uniform 0; }
    symmetry { type symmetry; }
    farfield { type calculated; value uniform 0; }
}
EOF
  cat > "$C/0.orig/alphat" <<'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; location "0"; object alphat; }
dimensions      [1 -1 -1 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    wing     { type compressible::alphatWallFunction; Prt 0.85; value uniform 0; }
    symmetry { type symmetry; }
    farfield { type calculated; value uniform 0; }
}
EOF

  ( cd "$C" && timed "checkMesh_$L" 1 -- checkMesh > log.checkMesh_patched 2>&1 )
  echo "$L: patches now ->"; grep -E "^\s+(wing|symmetry|farfield|defaultFaces)$" -A3 "$C/constant/polyMesh/boundary" | grep -E "wing|symmetry|farfield|defaultFaces|nFaces"
done
printf 'TOTAL\t%d\t1\t%.4f\n' "$(( $(date +%s) - t0 ))" "$(python3 -c "print(($(date +%s)-$t0)/60)")" >> "$COST"
echo "SOLVE CHAIN BUILT"
