/*---------------------------------------------------------------------------*\
    kCorrectiveFrozenFoam

    Driver for SpaRTA step 1, k-corrective-frozen-RANS (Schmelzer, Dwight &
    Cinnella 2020, section 2.1). No momentum or pressure equation is solved:
    0/U and 0/k must hold the high-fidelity (LES) mean fields and 0/tauij
    the high-fidelity Reynolds stress; 0/omega and 0/nut hold the baseline
    k-omega SST solution as the initial condition. The turbulence model must
    be kOmegaSSTFrozen (it is what this driver drives).

    Convergence (pre-registered in W2_SPARTA_PREREGISTRATION.md): omega
    initial residual < residTol AND max relative iteration change of omega
    < changeTol, sustained for nSettle consecutive iterations; then 20%
    further iterations are run and the L2 drift of R over them is reported.
    endTime in controlDict is the backstop cap; hitting it without settling
    is reported as NOT CONVERGED.

    After the frozen solve, the L-26 sign experiment runs: the k equation
    with the extracted R is re-solved from 0.5*k_LES with RScale = +1 and
    RScale = -1, and both drifts are reported.
\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "singlePhaseTransportModel.H"
#include "turbulentTransportModel.H"
#include "kOmegaSSTFrozen.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "SpaRTA k-corrective-frozen-RANS: passive omega solve with U, k,"
        " bij frozen at high-fidelity values"
    );

    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    Info<< "Reading frozen high-fidelity velocity field U\n" << endl;
    volVectorField U
    (
        IOobject
        (
            "U",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );

    Info<< "Computing flux field phi from frozen U\n" << endl;
    surfaceScalarField phi
    (
        IOobject
        (
            "phi",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        fvc::flux(U)
    );

    singlePhaseTransportModel laminarTransport(U, phi);

    autoPtr<incompressible::turbulenceModel> turbulence
    (
        incompressible::turbulenceModel::New(U, phi, laminarTransport)
    );

    typedef RASModels::kOmegaSSTFrozen
    <
        IncompressibleTurbulenceModel<transportModel>
    > frozenModelType;

    if (!isA<frozenModelType>(*turbulence))
    {
        FatalErrorInFunction
            << "turbulenceProperties must select RASModel kOmegaSSTFrozen"
            << exit(FatalError);
    }

    frozenModelType& frozen = refCast<frozenModelType>(*turbulence);

    // Pre-registered settle criteria
    const scalar residTol = 1e-8;
    const scalar changeTol = 1e-9;
    const label nSettle = 50;

    label settledCount = 0;
    label convergedAt = -1;
    scalar RNormAtConverged = -1;
    label extraIters = 0;

    const volScalarField& omegaField = frozen.omegaRef();
    scalarField omegaPrev(omegaField.primitiveField());

    Info<< "\nStarting frozen omega iterations\n" << endl;

    while (runTime.loop())
    {
        turbulence->correct();

        const scalarField& omegaNow = omegaField.primitiveField();
        const scalar maxOmega = gMax(mag(omegaNow)());
        const scalar maxRelChange =
            gMax(mag(omegaNow - omegaPrev)())/max(maxOmega, SMALL);
        omegaPrev = omegaNow;

        const scalar initRes = frozen.omegaInitialResidual();

        if ((runTime.timeIndex() % 50) == 0 || convergedAt > 0)
        {
            Info<< "Iter " << runTime.timeIndex()
                << "  omega initRes = " << initRes
                << "  max rel domega = " << maxRelChange << endl;
        }

        if (convergedAt < 0)
        {
            if (initRes < residTol && maxRelChange < changeTol)
            {
                ++settledCount;
            }
            else
            {
                settledCount = 0;
            }

            if (settledCount >= nSettle)
            {
                convergedAt = runTime.timeIndex();
                RNormAtConverged = ::sqrt
                (
                    gSum(sqr(frozen.kDeficit().primitiveField()))
                );
                extraIters = (convergedAt + 4)/5;  // ceil(20%)
                Info<< "\nCONVERGED (settle criterion) at iteration "
                    << convergedAt << "; running " << extraIters
                    << " verification iterations" << endl;
            }
        }
        else if (runTime.timeIndex() >= convergedAt + extraIters)
        {
            const scalar RNormNow = ::sqrt
            (
                gSum(sqr(frozen.kDeficit().primitiveField()))
            );
            const scalar RDrift =
                mag(RNormNow - RNormAtConverged)
               /max(RNormAtConverged, SMALL);

            Info<< "\nSettle verification: L2(R) moved "
                << 100*RDrift << "% over the "
                << extraIters << " verification iterations"
                << (RDrift < 1e-4 ? "  [SETTLED]" : "  [NOT SETTLED]")
                << endl;
            break;
        }
    }

    if (convergedAt < 0)
    {
        Info<< "\nNOT CONVERGED: backstop cap reached at iteration "
            << runTime.timeIndex() << endl;
    }

    Info<< "\nWriting fields at iteration " << runTime.timeIndex() << endl;
    runTime.writeNow();

    // L-26 controlled sign experiment on R in the k equation
    Info<< "\nL-26 sign experiment: re-solving the k equation from"
        << " 0.5*k_data for 500 iterations" << endl;

    const scalar driftPlus = frozen.verifyKEquation(+1.0, 0.5, 500);
    Info<< "  RScale = +1: relative L2 drift of recovered k from k_data = "
        << driftPlus << endl;

    const scalar driftMinus = frozen.verifyKEquation(-1.0, 0.5, 500);
    Info<< "  RScale = -1: relative L2 drift of recovered k from k_data = "
        << driftMinus << endl;

    Info<< "  drift ratio (-1 / +1) = "
        << driftMinus/max(driftPlus, SMALL) << endl;

    Info<< "\nExecutionTime = " << runTime.elapsedCpuTime() << " s"
        << "  ClockTime = " << runTime.elapsedClockTime() << " s"
        << nl << endl;

    Info<< "End\n" << endl;

    return 0;
}

// ************************************************************************* //
