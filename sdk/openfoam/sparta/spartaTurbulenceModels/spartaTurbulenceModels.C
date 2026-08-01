/*---------------------------------------------------------------------------*\
    Runtime registration of the SpaRTA reproduction turbulence models for
    incompressible transport (stock v2606 registration pattern).
\*---------------------------------------------------------------------------*/

#include "turbulentTransportModels.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#include "kOmegaSSTFrozen.H"
makeRASModel(kOmegaSSTFrozen);

#include "kOmegaSSTCorrected.H"
makeRASModel(kOmegaSSTCorrected);

#include "kOmegaSSTSparta.H"
makeRASModel(kOmegaSSTSparta);

// ************************************************************************* //
