"""
F6d -- direct demonstration, on the F6b periodic-hill case, of what the
eigenvalue-perturbation source term in

    demo-output/website/dafoam/f6a_epistemic_band/*/system/fvOptions

actually does to the effective Reynolds stress, versus what its own comment
says it intends.

Two cases, identical in every respect except one character of C++:

  f6asign_threeC   codeAddSup ends with  eqn += fvc::div(deltaR);
                   -- verbatim the operator used by every F6a channel-3 and r4
                      sweep case (grep 'eqn += fvc::div(deltaR)' under
                      f6a_epistemic_band/).
  corrected_threeC codeAddSup ends with  eqn -= fvc::div(deltaR);

Everything else -- the eigen-decomposition, eLambda, the blend, the mesh, the
schemes, the restart field -- is byte-identical between the two, and the
deltaR expression is copied unchanged from F6a's dictionary.

Why threeC:  eLambda = (0,0,0), so bPert = 0 and deltaR = -2k*bB exactly.
The intended perturbed state is therefore ZERO deviatoric Reynolds stress
(the 3-component / isotropic limit).  Under `eqn +=` the effective deviatoric
stress is instead  R_model - deltaR = 2k*bB - (-2k*bB) = 2*(2k*bB), i.e. the
baseline anisotropy DOUBLED rather than removed.  The two predictions are
qualitatively opposite and cannot be confused for one another in the result.

The turbulence model is left LIVE here (`turbulence on`), exactly as F6a ran
it -- this is a replication of F6a's mechanism, not of this study's
prescribed-stress propagation model.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE = HERE.parent / "f6b_periodic_hills" / "case_breuer_re10595"
OUT = HERE / "signdemo"
FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
BASE_T = "10000"

# --- the deltaR body below is copied verbatim from
# --- f6a_epistemic_band/r4_band_tightening_hump/oneC_delta0.05/system/fvOptions
FVO = """FoamFile
{{
    version 2.0; format ascii; class dictionary; location "system"; object fvOptions;
}}
momentumSource
{{
    type            meanVelocityForce;
    selectionMode   all;
    fields          (U);
    Ubar            (0.72 0 0);
}}

UQEigenPerturb
{{
    type            vectorCodedSource;
    active          true;
    name            uqEig{tag};

    vectorCodedSourceCoeffs
    {{
        selectionMode   all;
        fields          (U);
        name            uqEig{tag};

        perturbCorner   {corner};
        blendDelta      1.0;

        codeInclude
        #{{
            #include "fvCFD.H"
        #}};

        codeCorrect   #{{ #}};
        codeConstrain #{{ #}};

        codeAddSup
        #{{
            const fvMesh& mesh = this->mesh();
            const volVectorField& U = eqn.psi();
            const volScalarField& k = mesh.lookupObject<volScalarField>("k");
            const volScalarField& nut = mesh.lookupObject<volScalarField>("nut");

            const word corner(this->coeffs().get<word>("perturbCorner"));
            const scalar blendDelta(this->coeffs().get<scalar>("blendDelta"));

            vector eLambda(Zero);
            if (corner == "oneC")
            {{
                eLambda = vector(-1.0/3.0, -1.0/3.0, 2.0/3.0);
            }}
            else if (corner == "twoC")
            {{
                eLambda = vector(-1.0/3.0, 1.0/6.0, 1.0/6.0);
            }}
            else if (corner == "threeC")
            {{
                eLambda = vector(0, 0, 0);
            }}
            else
            {{
                FatalErrorInFunction
                    << "perturbCorner must be oneC, twoC or threeC, got "
                    << corner << exit(FatalError);
            }}

            const volSymmTensorField Sij("Sij", symm(fvc::grad(U)));
            const dimensionedScalar kSmall("kSmall", k.dimensions(), 1e-8);
            const volScalarField bCoeff("bCoeff", (-1.0)*nut/max(k, kSmall));
            volSymmTensorField bBoussField("bBoussField", bCoeff*Sij);

            volSymmTensorField deltaR
            (
                "deltaR",
                2.0*k*bBoussField - 2.0*k*bBoussField
            );

            const scalar kMinCell = 1e-8;
            forAll(k, celli)
            {{
                if (k[celli] < kMinCell) continue;

                const symmTensor& bB = bBoussField[celli];
                const vector eVals(eigenValues(bB));
                const tensor eVecs(eigenVectors(bB, eVals));

                const symmTensor bPert =
                    eLambda.x()*sqr(eVecs.x())
                  + eLambda.y()*sqr(eVecs.y())
                  + eLambda.z()*sqr(eVecs.z());

                deltaR.primitiveFieldRef()[celli] =
                    blendDelta*2.0*k[celli]*(bPert - bB);
            }}

            eqn {op} fvc::div(deltaR);
        #}};
    }}
}}
"""

CTRL = """FoamFile
{{
    version 2.0; format ascii; class dictionary; location "system"; object controlDict;
}}
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end};
deltaT          1;
writeControl    timeStep;
writeInterval   {end};
purgeWrite      0;
writeFormat     ascii;
writePrecision  15;
writeCompression uncompressed;
timeFormat      general;
timePrecision   15;
runTimeModifiable no;

functions
{{
  #includeFunc  singleGraph_x0
  #includeFunc  singleGraph_x1
  #includeFunc  singleGraph_x2
  #includeFunc  singleGraph_x3
  #includeFunc  singleGraph_x4
  #includeFunc  singleGraph_x5
  #includeFunc  singleGraph_x6
  #includeFunc  singleGraph_x7
  #includeFunc  singleGraph_x8

    wallShearStress
    {{
        type            wallShearStress;
        libs            (fieldFunctionObjects);
        writeFields     yes;
        executeControl  writeTime;
        writeControl    writeTime;
    }}
}}
"""


def build(name, corner, op, end=4000):
    dst = OUT / name
    if dst.exists():
        shutil.rmtree(dst)
    (dst / "0").mkdir(parents=True)
    shutil.copytree(CASE / "constant", dst / "constant")
    shutil.copytree(CASE / "system", dst / "system")
    shutil.copy(CASE / "fieldDef", dst / "fieldDef")
    for f in ("U", "p", "k", "omega", "nut", "phi"):
        shutil.copy(CASE / BASE_T / f, dst / "0" / f)
    # only momentumSourceProperties -- see build_ensemble.py for why
    # <time>/uniform/time must NOT be copied.
    msp = CASE / BASE_T / "uniform" / "momentumSourceProperties"
    if msp.is_file():
        (dst / "0" / "uniform").mkdir(exist_ok=True)
        shutil.copy(msp, dst / "0" / "uniform" / "momentumSourceProperties")
    (dst / "system" / "controlDict").write_text(CTRL.format(end=end))
    tag = name.replace("_", "")
    (dst / "system" / "fvOptions").write_text(
        FVO.format(tag=tag, corner=corner, op=op))
    return dst


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    jobs = [
        ("f6asign_threeC", "threeC", "+="),
        ("corrected_threeC", "threeC", "-="),
    ]
    procs = []
    for name, corner, op in jobs:
        d = build(name, corner, op)
        print("built", d)
        procs.append(subprocess.Popen(
            ["bash", "-lc",
             f"source {FOAM} && cd {d} && simpleFoam > log.simpleFoam 2>&1"]))
    for p in procs:
        p.wait()
    print("done")
