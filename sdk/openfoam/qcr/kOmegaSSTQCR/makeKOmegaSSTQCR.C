/*---------------------------------------------------------------------------*\
    Runtime registration of kOmegaSSTQCR for incompressible transport
    models (simpleFoam et al.). Pattern follows
    src/TurbulenceModels/incompressible/turbulentTransportModels/
    turbulentTransportModels.{H,C}: the Types macro only lays down
    typedefs, so a user library may invoke it without duplicating the
    base-model symbols the stock library already owns.
\*---------------------------------------------------------------------------*/

#include "turbulentTransportModels.H"

#include "kOmegaSSTQCR.H"

makeRASModel(kOmegaSSTQCR);

// ************************************************************************* //
