/*---------------------------------------------------------------------------*\
    Runtime registration of the frozen-k propagation model
    (stock v2606 registration pattern, as sdk/openfoam/sparta uses).
\*---------------------------------------------------------------------------*/

#include "turbulentTransportModels.H"

#include "kOmegaSSTCorrectedFrozenK.H"
makeRASModel(kOmegaSSTCorrectedFrozenK);

// ************************************************************************* //
