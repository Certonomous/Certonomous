#include "kOmegaSSTCorrectedFrozenK.H"

namespace Foam
{
namespace RASModels
{

template<class BasicTurbulenceModel>
kOmegaSSTCorrectedFrozenK<BasicTurbulenceModel>::kOmegaSSTCorrectedFrozenK
(
    const alphaField& alpha,
    const rhoField& rho,
    const volVectorField& U,
    const surfaceScalarField& alphaRhoPhi,
    const surfaceScalarField& phi,
    const transportModel& transport,
    const word& propertiesName,
    const word& type
)
:
    kOmegaSSTCorrected<BasicTurbulenceModel>
    (
        alpha, rho, U, alphaRhoPhi, phi, transport, propertiesName, type
    )
{
    Info<< "kOmegaSSTCorrectedFrozenK: k and omega are FROZEN at their "
        << "start-time values; only nu_t is updated." << nl;
}


template<class BasicTurbulenceModel>
void kOmegaSSTCorrectedFrozenK<BasicTurbulenceModel>::correct()
{
    if (!this->turbulence_)
    {
        return;
    }
    // Deliberately NOT calling kOmegaSSTCorrected::correct(): that solves the
    // k and omega equations. We update the eddy viscosity from the frozen
    // fields and nothing else. eddyViscosity::correct() refreshes the strain
    // measures that correctNut() needs.
    eddyViscosity<RASModel<BasicTurbulenceModel>>::correct();
    this->correctNut();
}

} // End namespace RASModels
} // End namespace Foam
