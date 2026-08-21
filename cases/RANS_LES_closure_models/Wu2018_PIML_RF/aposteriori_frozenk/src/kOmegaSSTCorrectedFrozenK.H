/*---------------------------------------------------------------------------*\
    kOmegaSSTCorrectedFrozenK

    kOmegaSSTCorrected with the k and omega transport equations NOT SOLVED.

    Both fields stay at their start-time values for the whole run; nu_t is
    updated from them through the inherited correctNut(), so the blending
    functions and Menter's a1 limiter remain the stock ones. divDevReff and
    divDevRhoReff are inherited UNCHANGED from kOmegaSSTCorrected, so the
    momentum equation still sees

        -nu_t(...) + div(2 k bScale bijDelta)

    but with k now a constant field, which is the whole point: the injected
    extra stress cannot be rescaled by a collapsing k budget.

    Registered in
      cases/RANS_LES_closure_models/Wu2018_PIML_RF/aposteriori_frozenk/
      PREREGISTRATION.md sec. 0.1.

    sdk/openfoam/sparta/ is NOT modified; the parent class is used as-is.
\*---------------------------------------------------------------------------*/

#ifndef kOmegaSSTCorrectedFrozenK_H
#define kOmegaSSTCorrectedFrozenK_H

#include "kOmegaSSTCorrected.H"

namespace Foam
{
namespace RASModels
{

template<class BasicTurbulenceModel>
class kOmegaSSTCorrectedFrozenK
:
    public kOmegaSSTCorrected<BasicTurbulenceModel>
{
    kOmegaSSTCorrectedFrozenK(const kOmegaSSTCorrectedFrozenK&) = delete;
    void operator=(const kOmegaSSTCorrectedFrozenK&) = delete;

public:

    typedef typename BasicTurbulenceModel::alphaField alphaField;
    typedef typename BasicTurbulenceModel::rhoField rhoField;
    typedef typename BasicTurbulenceModel::transportModel transportModel;

    TypeName("kOmegaSSTCorrectedFrozenK");

    kOmegaSSTCorrectedFrozenK
    (
        const alphaField& alpha,
        const rhoField& rho,
        const volVectorField& U,
        const surfaceScalarField& alphaRhoPhi,
        const surfaceScalarField& phi,
        const transportModel& transport,
        const word& propertiesName = turbulenceModel::propertiesName,
        const word& type = typeName
    );

    virtual ~kOmegaSSTCorrectedFrozenK() = default;

    //- Update nu_t from the FROZEN k and omega. Solves nothing.
    virtual void correct();
};

} // End namespace RASModels
} // End namespace Foam

#ifdef NoRepository
    #include "kOmegaSSTCorrectedFrozenK.C"
#endif

#endif
