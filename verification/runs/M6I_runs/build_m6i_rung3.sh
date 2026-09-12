#!/bin/bash
# M6I RUNG 3 -- ROBUST STARTUP.  Applied identically to L1, L2 and L3.
#
# WHY THERE IS A RUNG 3 (Sanaa's item 13: two stops on the same cause -> climb the ladder).
#   attempt 1 (M6I-R1-L3,    22:01:39Z) SIGFPE at iteration 2.  SIMPLEC, p field relax 1.
#   attempt 2 (M6I-R1-L3-R2, 22:08:51Z) SIGFPE at iteration 2.  SIMPLE,  p field relax 0.3.
#   Same cause both times, and it is now PROVED rather than inferred:
#   sutherlandTransport::mu is As*sqrt(T)/(1+Ts/T) -- sutherlandTransportI.H:120 -- so a
#   NEGATIVE T raises SIGFPE inside libm, which is exactly the frame sitting directly
#   beneath libfluidThermophysicalModels in both stack traces.  T goes negative because a
#   transonic cold start from a uniform freestream drives a violent first pressure
#   excursion: p max 417,018 Pa on attempt 1 and 22,368,256 Pa on attempt 2, against a
#   101,325 Pa freestream.
#
# THE RUNG, pre-declared in ADDENDUM 1 section A1.3 before either number was known:
#   (1) the pressure equation gets its diagonal-dominance relaxation back;
#   (2) the thermo is BOUNDED so a startup excursion CLIPS instead of FAULTING;
#   (3) a 200-iteration first-order startup ramp, then the registered second-order schemes.
# The non-orthogonality treatment is NOT touched: `limited corrected 0.33` survived both
# iteration 1s intact, so changing it would be a change made against the evidence.
set -u
RUNS="$(cd "$(dirname "$0")" && pwd)"

for L in L1 L2 L3; do
  C="$RUNS/$L"
  [ -d "$C/system" ] || { echo "$L: no system/"; exit 1; }

  # ---- (1) fvSolution: SIMPLE, with `equations p` RESTORED -------------------------
  # ATTEMPT 2'S ERROR, CORRECTED AT SOURCE.  ADDENDUM 1 section A1.2 asserted that
  # `relaxationFactors.equations.p` was a dead lever and deleted it.  THAT WAS WRONG, and
  # a measurement caught it, not an argument: pEqn.H:35-36 reads
  #     // Relax the pressure equation to ensure diagonal-dominance
  #     pEqn.relax();
  # and fvMatrix::relax() does NOTHING when no relaxation factor is registered for the
  # field.  Deleting the entry removed the diagonal-dominance enforcement the TRANSONIC
  # pressure equation needs -- fvm::div(phid,p) is asymmetric -- and p max went from
  # 417,018 to 22,368,256 Pa, 54x WORSE.  It is restored here.
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
    // `consistent` IS ABSENT, and this is SIMPLE, not SIMPLEC.  ADDENDUM 1 called
    // `consistent` a dead lever in rhoSimpleFoam ON THE STRENGTH OF pEqn.H ALONE.
    // THAT WAS WRONG: rhoSimpleFoam.C:78 reads `if (simple.consistent())` and includes a
    // SEPARATE FILE, pcEqn.H, which carries 10 occurrences of rAtU.  The lever selects an
    // entirely different pressure equation and is fully live.  Attempt 1 therefore ran
    // correct SIMPLEC and still crashed; SIMPLEC is not the fix and is not the fault.
    // ADDENDUM 2, 2026-09-12.
    // NO residualControl BY REGISTRATION: rule 4 reads last time == endTime.
}
relaxationFactors
{
    // equations.p 1 is the DIAGONAL-DOMINANCE relaxation pEqn.H:35 asks for by name.
    // It is not a no-op at 1.0: fvMatrix::relax sets D = max(|D|, sumMagOffDiag) BEFORE
    // dividing by alpha.  Deleting it is what made attempt 2 worse than attempt 1.
    fields    { p 0.3; rho 0.05; }
    equations { p 1; U 0.7; e 0.7; nuTilda 0.7; }
}
EOF

  # ---- fvSolution.startup: the tight first 200 iterations --------------------------
  sed -e 's/    fields    { p 0.3; rho 0.05; }/    fields    { p 0.2; rho 0.02; }/' \
      -e 's/    equations { p 1; U 0.7; e 0.7; nuTilda 0.7; }/    equations { p 1; U 0.5; e 0.5; nuTilda 0.5; }/' \
      "$C/system/fvSolution" > "$C/system/fvSolution.startup"
  grep -q '{ p 0.2; rho 0.02; }' "$C/system/fvSolution.startup" || { echo "$L: startup fvSolution substitution did not read back"; exit 1; }

  # ---- (3) fvSchemes.startup: FIRST ORDER on every convective term -----------------
  # The Laplacian and snGrad limiters are BYTE-IDENTICAL to the registered ones.  The
  # non-orthogonality treatment is deliberately NOT part of this rung.
  cat > "$C/system/fvSchemes.startup" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
// STARTUP RAMP ONLY -- the first 200 iterations.  Sanaa's CRM instruction section 6
// prescribes a robust-startup ramp for pressure-based compressible with the transonic
// option.  Every convective term is first-order upwind here; the registered second-order
// fvSchemes is restored byte-identically for the remaining iterations, and the graded
// answer is produced by THOSE schemes, never by these.
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
    div(phi,U)      bounded Gauss upwind;
    div(phi,e)      bounded Gauss upwind;
    div(phi,K)      bounded Gauss upwind;
    div(phi,Ekp)    bounded Gauss upwind;
    div(phi,nuTilda) bounded Gauss upwind;
    div(phid,p)     Gauss upwind;
    div((phi|interpolate(rho)),p) bounded Gauss upwind;
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear limited corrected 0.33; }
interpolationSchemes { default linear; }
snGradSchemes   { default limited corrected 0.33; }
wallDist        { method meshWave; }
EOF

  # ---- (2) BOUND THE THERMO --------------------------------------------------------
  # THE PROVED FAULT: sutherlandTransportI.H:120, mu = As*sqrt(T)/(1+Ts/T).  T < 0 makes
  # sqrt(T) raise SIGFPE in libm.  limitTemperature CLIPS T into a physical window every
  # iteration, so a startup excursion becomes a bounded, visible, recoverable event
  # instead of a fault.  The window is WIDE ON PURPOSE: at M 0.8395 with T_inf 300 K the
  # stagnation temperature is 342 K, so [100, 1500] cannot clip any physical state this
  # case can reach, and a clip therefore MEANS the solution left physics.  The number of
  # clipping events is read out of the log and gated by IC-5.
  cat > "$C/constant/fvOptions" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; location "constant"; object fvOptions; }
limitT
{
    type            limitTemperature;
    selectionMode   all;
    min             100;
    max             1500;
}
EOF
  echo "$L: rung 3 applied"
done
echo "RUNG 3 BUILT ON ALL THREE LEVELS"
