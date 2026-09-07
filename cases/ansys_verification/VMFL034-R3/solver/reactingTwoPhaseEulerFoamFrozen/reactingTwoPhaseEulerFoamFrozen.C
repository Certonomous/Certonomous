/*---------------------------------------------------------------------------*\
  reactingTwoPhaseEulerFoamFrozen -- FROZEN-FLOW variant of
  reactingTwoPhaseEulerFoam for VMFL034-R3.

  The carrier (k-epsilon) flow field is solved ONCE and FROZEN; only the
  dispersed-phase alpha continuity and the population-balance (constant-kernel
  aggregation) moments are transported, on the frozen phase fluxes.  This is the
  direct OpenFOAM analogue of the Ansys VMFL034 journal:
      solve set equations mixture flow no ke no mp no
      solve set equations phase-2 moment-0..5 yes ; solve iterate
  and of the manual's statement "Moments are solved on a frozen flow field."

  ROOT REMOVAL OF THE R2 SIGFPE: the pressure-velocity-energy block
  (pU/UEqns.H, EEqns.H, pU/pEqn.H) is the ONLY place fluid.Kd()/
  fluid.momentumTransfer() -> dragModels::SchillerNaumann::CdRe() (Re^0.687) is
  invoked.  It is removed here, so the CdRe domain error that killed R2 (rc 136)
  cannot recur -- structurally, not by bounding.  fluid.solve()
  (twoPhaseSystem::solve alpha-continuity via MULES + populationBalances_.solve())
  does NOT call Kd (verified against the v2606 source).
\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "twoPhaseSystem.H"
#include "phaseCompressibleTurbulenceModel.H"
#include "pimpleControl.H"
#include "localEulerDdtScheme.H"
#include "fvcSmooth.H"
#include "fvOptions.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "FROZEN-FLOW two-phase Euler solver: transports alpha-continuity and the"
        " population balance on a frozen carrier; NO momentum/pressure/energy"
        " solve, so no drag (SchillerNaumann::CdRe) is ever evaluated."
    );

    #include "postProcess.H"

    #include "addCheckCaseOptions.H"
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createControl.H"
    #include "createTimeControls.H"
    #include "createFields.H"
    #include "createFieldRefs.H"

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    Info<< "\nStarting time loop (FROZEN FLOW: alpha continuity + population"
        << " balance only; U, phi, k, epsilon held frozen)\n" << endl;

    while (runTime.run())
    {
        #include "readTimeControls.H"

        ++runTime;
        Info<< "Time = " << runTime.timeName() << nl << endl;

        // --- Frozen-flow corrector loop: NO UEqns / EEqns / pEqn.
        // fluid.solve() advances the dispersed-phase continuity and the
        // constant-kernel population balance on the FROZEN phase fluxes.
        while (pimple.loop())
        {
            fluid.solve();
            fluid.correct();
        }

        runTime.write();

        runTime.printExecutionTime(Info);
    }

    Info<< "End\n" << endl;

    return 0;
}

// ************************************************************************* //
