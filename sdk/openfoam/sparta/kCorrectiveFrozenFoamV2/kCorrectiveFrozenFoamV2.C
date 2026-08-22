/*---------------------------------------------------------------------------*\
    kCorrectiveFrozenFoamV2   --  R5C, the omega-source repair.

    A COPY of kCorrectiveFrozenFoam (sdk/openfoam/sparta/kCorrectiveFrozenFoam/)
    driving kOmegaSSTFrozenV2 instead of kOmegaSSTFrozen.  The original solver
    and libspartaTurbulenceModels.so are NOT modified and NOT rebuilt: R4's
    numbers came from those binaries (R5C PREREGISTRATION.md sec. 2.3, NR-2).

    Driver for SpaRTA step 1, k-corrective-frozen-RANS (Schmelzer, Dwight &
    Cinnella 2020, section 2.1). No momentum or pressure equation is solved:
    0/U and 0/k must hold the high-fidelity (LES) mean fields and 0/tauij
    the high-fidelity Reynolds stress; 0/omega and 0/nut hold the baseline
    k-omega SST solution as the initial condition.

    Convergence criterion, UNCHANGED from the original and from R4: omega
    initial residual < residTol AND max relative iteration change of omega
    < changeTol, sustained for nSettle consecutive iterations; then 20%
    further iterations are run and the L2 drift of R over them is reported.
    endTime in controlDict is the backstop cap; hitting it without settling
    is reported as NOT CONVERGED.

    TWO DIAGNOSTIC ADDITIONS, neither of which touches a solved field:

    1. <case>/omegaHistory.csv, one row PER ITERATION:
         iter,initRes,maxRelDomega,minOmegaPreBound,nNegOmegaCells,
         nNegSourceCells
       The original prints only every 50th iteration, which cannot resolve a
       clip that happens on iteration 1 -- and that is exactly the shape R4
       measured (L-235).  Gate G3 (d) and (e) are graded on this file.

    2. A cumulative count of bound(omega, omegaMin) events, printed before the
       field write.  L-235's own prescribed repair: "count the solver's own
       bounding messages before the field write and refuse the run if there
       are any."

    After the frozen solve, the L-26 sign experiment runs, unchanged.
\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "singlePhaseTransportModel.H"
#include "turbulentTransportModel.H"
#include "OFstream.H"
#include "kOmegaSSTFrozenV2.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "R5C repaired SpaRTA k-corrective-frozen-RANS: passive omega solve"
        " with U, k, bij frozen at high-fidelity values"
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

    typedef RASModels::kOmegaSSTFrozenV2
    <
        IncompressibleTurbulenceModel<transportModel>
    > frozenModelType;

    if (!isA<frozenModelType>(*turbulence))
    {
        FatalErrorInFunction
            << "turbulenceProperties must select RASModel kOmegaSSTFrozenV2"
            << exit(FatalError);
    }

    frozenModelType& frozen = refCast<frozenModelType>(*turbulence);

    // Pre-registered settle criteria (identical to R4's)
    const scalar residTol = 1e-8;
    const scalar changeTol = 1e-9;
    const label nSettle = 50;

    label settledCount = 0;
    label convergedAt = -1;
    scalar RNormAtConverged = -1;
    label extraIters = 0;

    const volScalarField& omegaField = frozen.omegaRef();
    scalarField omegaPrev(omegaField.primitiveField());

    // R5C: per-iteration convergence history, the artefact gate G3 reads.
    autoPtr<OFstream> histPtr;
    if (Pstream::master())
    {
        histPtr.reset(new OFstream(runTime.path()/"omegaHistory.csv"));
        histPtr() << "iter,initRes,maxRelDomega,minOmegaPreBound,"
                     "nNegOmegaCells,nNegSourceCells" << endl;
        histPtr().precision(15);
    }

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

        if (histPtr)
        {
            histPtr() << runTime.timeIndex() << ','
                      << initRes << ','
                      << maxRelChange << ','
                      << frozen.omegaMinPreBound() << ','
                      << frozen.nNegOmegaCells() << ','
                      << frozen.nNegSourceCells() << nl;
        }

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

    if (histPtr)
    {
        histPtr().flush();
    }

    // L-235's prescribed check, stated before the write so the log carries it
    // in the region r4_lib.frozen_complete inspects.  The wording deliberately
    // does not contain the substring the bound() message carries.
    Info<< "\nR5C omega clip audit: bound events before write = "
        << frozen.nBoundEvents()
        << ", negative-source cells on the last iteration = "
        << frozen.nNegSourceCells()
        << ", omegaSourceRepair = " << Switch(frozen.omegaSourceRepair())
        << endl;

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
