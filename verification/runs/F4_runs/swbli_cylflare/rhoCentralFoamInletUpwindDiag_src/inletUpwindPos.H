// STEP 1 DISCRIMINATOR (F4_SIGFPE_STEP01_PREREGISTRATION.md §5).
// Restore an upwind bias at the fixedValue supersonic INLET patch only, by
// replacing the _pos face states there with the owner cell's own values while
// leaving the _neg states at the patch value. Everywhere else -- every internal
// face, and every other patch -- nothing is touched.
//
// Scope, and why it is the inlet ONLY: at a no-slip wall the pos==neg identity
// is what makes phi vanish, so breaking it leaks mass through a solid wall; on
// the zeroGradient farfield/outlet patchInternalField() IS the patch value, so
// the overwrite is an exact no-op; on the two wedge patches it would change the
// flux on every one of the 29,700 cells. See the prereg's §1.5 table.
{
    const label inletPatchi = mesh.boundaryMesh().findPatchID("inlet");

    // Refuse rather than silently do nothing: a missing or empty inlet patch
    // would make this arm a null-by-construction, which is exactly the failure
    // mode control C2 exists to catch.
    if (inletPatchi < 0 || mesh.boundary()[inletPatchi].size() == 0)
    {
        FatalErrorInFunction
            << "STEP1: inlet patch not found or empty -- refusing to run a "
            << "discriminator whose lever cannot act." << exit(FatalError);
    }

    rho_pos.boundaryFieldRef()[inletPatchi] =
        rho.boundaryField()[inletPatchi].patchInternalField()();

    rhoU_pos.boundaryFieldRef()[inletPatchi] =
        rhoU.boundaryField()[inletPatchi].patchInternalField()();

    rPsi_pos.boundaryFieldRef()[inletPatchi] =
        rPsi.boundaryField()[inletPatchi].patchInternalField()();

    e_pos.boundaryFieldRef()[inletPatchi] =
        e.boundaryField()[inletPatchi].patchInternalField()();

    // Derived _pos states must be rebuilt from the overwritten primitives,
    // or U_pos and p_pos would still carry the patch state.
    U_pos.boundaryFieldRef()[inletPatchi] =
        rhoU_pos.boundaryField()[inletPatchi]
      / rho_pos.boundaryField()[inletPatchi];

    p_pos.boundaryFieldRef()[inletPatchi] =
        rho_pos.boundaryField()[inletPatchi]
      * rPsi_pos.boundaryField()[inletPatchi];

    // Wave speed must follow the state it belongs to, or ap/am are inconsistent.
    cSf_pos.boundaryFieldRef()[inletPatchi] =
        c.boundaryField()[inletPatchi].patchInternalField()()
      * mesh.magSf().boundaryField()[inletPatchi];

    // phiv_pos was formed from U_pos at :121-123 and must be re-formed.
    phiv_pos.boundaryFieldRef()[inletPatchi] =
        U_pos.boundaryField()[inletPatchi]
      & mesh.Sf().boundaryField()[inletPatchi];
}
