/*---------------------------------------------------------------------------*\
    Runtime registration of the R5C repaired frozen-RANS turbulence model for
    incompressible transport (stock v2606 registration pattern).

    This library is SEPARATE from libspartaTurbulenceModels.so on purpose:
    R4's numbers came from that library and it is neither modified nor rebuilt
    (R5C PREREGISTRATION.md sec. 2.3, NR-2).
\*---------------------------------------------------------------------------*/

#include "turbulentTransportModels.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#include "kOmegaSSTFrozenV2.H"
makeRASModel(kOmegaSSTFrozenV2);

// ************************************************************************* //
