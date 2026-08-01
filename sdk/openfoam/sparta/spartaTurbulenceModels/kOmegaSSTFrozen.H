/*---------------------------------------------------------------------------*\
    kOmegaSSTFrozen

    SpaRTA step 1: k-corrective-frozen-RANS
    (Schmelzer, Dwight & Cinnella, Flow Turb. Combust. 104:579-603, 2020,
     section 2.1, Eqs. 4-6).

    Solves ONLY the omega transport equation, with U, k and b_ij frozen at
    their high-fidelity values:
      - U   is the solver's velocity field (load 0/U with the LES mean field),
      - k   is read from 0/k (load with the LES turbulent kinetic energy),
      - b_ij is formed once from the field "tauij" (load with the LES
        Reynolds stress), b_ij = tauij/(2 max(k, kSmall)) - delta_ij/3.

    At each iteration the residual of the (steady, discrete) k equation is
    computed as the additive correction R ("kDeficit") and fed back into the
    omega equation production as (gamma/nu_t)(Pk + R), per Eq. 5. Pk uses the
    frozen data anisotropy and Menter's limiter, Eq. 6:
        Pk = min(-2 k b_ij dUi/dxj, 10 betaStar omega k).
    nu_t follows the stock SST definition nu_t = a1 k / max(a1 omega, F23 S),
    identical to the paper's expression.

    On convergence the model holds:
      - kDeficit  (R, dimensions m^2/s^3), AUTO_WRITE
      - bijDelta  (b_ij^Delta = b_ij,data + (nu_t/k) S_ij), AUTO_WRITE

    verifyKEquation() implements the L-26 controlled sign experiment: the k
    equation with the extracted R (times RScale) is re-solved from a perturbed
    initial k and the relative L2 drift from the frozen data k is returned.

    Derived from stock v2606 kOmegaSST so that all coefficients, blending
    functions and wall functions are the stock ones.
\*---------------------------------------------------------------------------*/

#ifndef kOmegaSSTFrozen_H
#define kOmegaSSTFrozen_H

#include "kOmegaSST.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace RASModels
{

/*---------------------------------------------------------------------------*\
                       Class kOmegaSSTFrozen Declaration
\*---------------------------------------------------------------------------*/

template<class BasicTurbulenceModel>
class kOmegaSSTFrozen
:
    public kOmegaSST<BasicTurbulenceModel>
{
    // Private Member Functions

        //- No copy construct
        kOmegaSSTFrozen(const kOmegaSSTFrozen&) = delete;

        //- No copy assignment
        void operator=(const kOmegaSSTFrozen&) = delete;


protected:

    // Protected data

        //- Guard for divisions by the frozen k
        dimensionedScalar kSmall_;

        //- Frozen high-fidelity Reynolds stress (read from "tauij")
        volSymmTensorField tauijData_;

        //- Frozen data anisotropy b_ij = dev(tauij/(2 max(k,kSmall)))
        volSymmTensorField bijData_;

        //- k-equation residual correction R
        volScalarField kDeficit_;

        //- Anisotropy correction b_ij^Delta
        volSymmTensorField bijDelta_;

        //- Initial residual of the last omega solve
        scalar omegaInitialResidual_;


public:

    typedef typename BasicTurbulenceModel::alphaField alphaField;
    typedef typename BasicTurbulenceModel::rhoField rhoField;
    typedef typename BasicTurbulenceModel::transportModel transportModel;


    //- Runtime type information
    TypeName("kOmegaSSTFrozen");


    // Constructors

        //- Construct from components
        kOmegaSSTFrozen
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


    //- Destructor
    virtual ~kOmegaSSTFrozen() = default;


    // Member Functions

        //- Solve the frozen omega equation and update R, bijDelta, nut
        virtual void correct();

        //- Initial residual of the last omega solve
        scalar omegaInitialResidual() const
        {
            return omegaInitialResidual_;
        }

        //- Direct const access to the omega field (no tmp indirection)
        const volScalarField& omegaRef() const
        {
            return this->omega_;
        }

        //- Const access to the extracted correction fields
        const volScalarField& kDeficit() const
        {
            return kDeficit_;
        }

        const volSymmTensorField& bijDelta() const
        {
            return bijDelta_;
        }

        //- L-26 sign experiment: re-solve the k equation with RScale*R from
        //  a perturbed initial condition (perturbFactor * k_data) for nIters
        //  iterations; returns the relative L2 drift of the solved k from
        //  the frozen data k. Restores k and nut afterwards.
        scalar verifyKEquation
        (
            const scalar RScale,
            const scalar perturbFactor,
            const label nIters
        );
};


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace RASModels
} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#ifdef NoRepository
    #include "kOmegaSSTFrozen.C"
#endif

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
