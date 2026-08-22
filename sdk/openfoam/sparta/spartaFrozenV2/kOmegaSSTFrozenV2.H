/*---------------------------------------------------------------------------*\
    kOmegaSSTFrozenV2  --  R5C, the omega-source repair.

    A COPY of RASModels::kOmegaSSTFrozen (sdk/openfoam/sparta/
    spartaTurbulenceModels/kOmegaSSTFrozen.H/.C) under a NEW type name, in a
    NEW library.  kOmegaSSTFrozen and libspartaTurbulenceModels.so are NOT
    modified and NOT rebuilt: R4's numbers came from those binaries
    (cases/RANS_LES_closure_models/R5C_omega_repair/PREREGISTRATION.md sec.2.3,
    NR-2).

    ONE behavioural switch, read from the RAS sub-dictionary of
    constant/turbulenceProperties:

        omegaSourceRepair   [ false | true ];      default: false

    false -- byte-for-byte the arithmetic of kOmegaSSTFrozen.C:197-211.  This
             branch exists so gate G2 can prove the new build is not a new
             solver (byte-identical reproduction of the W2 record).

    true  -- the registered repair.  The frozen omega source

               S = alpha*rho*gamma*(PkLim + Rterm)/max(nut,1e-12)

             is added FULLY EXPLICITLY by kOmegaSSTFrozen while every other
             term in the equation is implicit or a diagonal sink.  PkLim
             cancels inside S, so

               S = gamma*( div(phi,k) - lap(DkEff,k) + (2/3)divU*k
                           + betaStar*omega*k ) / max(nut,1e-12)

             which is gamma/nu_t times the convection-minus-diffusion residual
             of the FROZEN k field and therefore HAS NO SIGN.  A large negative
             right-hand side in a matrix whose diagonal carries no matching
             sink produces a negative solution directly -- omega < 0 on the
             first solve, which is R4's measured signature (initRes 0.933 then
             "bounding omega, min: -193215225.4 ... average: -50081.6").

             The repair is a Patankar split:

               Spos = max(S,0)   -> explicit, at its exact value (no lagging)
               Sneg = min(S,0)   -> - fvm::SuSp(-Sneg/max(omega,omegaMin), omega)

             i.e. the whole negative part of the source is placed on the
             DIAGONAL as a sink proportional to omega.  At a fixed point
             omega_prev == omega, so

               Spos + (Sneg/omega)*omega = Spos + Sneg = S    exactly,

             and the repaired operator has the legacy operator's fixed point in
             exact arithmetic.  The repair changes which part of the source
             sits on the diagonal -- the path -- not the answer.  That is why
             gate G1 (identity against R4's 12 targets, 1e-6) is a gate and not
             a hope.

    Diagnostics added in BOTH branches, touching no solved field (L-235: "count
    the solver's own bounding messages before the field write and refuse the
    run if there are any"):

        nBoundEvents()      iterations on which bound(omega,omegaMin) fired
        nNegOmegaCells()    cells with omega < omegaMin before the bound
        omegaMinPreBound()  min(omega) before the bound
        nNegSourceCells()   cells with S < 0 -- the switch-active control G1c

\*---------------------------------------------------------------------------*/

#ifndef kOmegaSSTFrozenV2_H
#define kOmegaSSTFrozenV2_H

#include "kOmegaSST.H"
#include "Switch.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace RASModels
{

/*---------------------------------------------------------------------------*\
                      Class kOmegaSSTFrozenV2 Declaration
\*---------------------------------------------------------------------------*/

template<class BasicTurbulenceModel>
class kOmegaSSTFrozenV2
:
    public kOmegaSST<BasicTurbulenceModel>
{
    // Private Member Functions

        //- No copy construct
        kOmegaSSTFrozenV2(const kOmegaSSTFrozenV2&) = delete;

        //- No copy assignment
        void operator=(const kOmegaSSTFrozenV2&) = delete;


protected:

    // Protected data

        //- Guard for divisions by the frozen k
        dimensionedScalar kSmall_;

        //- R5C: the one behavioural switch.  false == R4's legacy path.
        Switch omegaSourceRepair_;

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

        // ---- R5C diagnostics: no solved field depends on any of these ----

        //- Cumulative count of iterations on which bound(omega) fired
        label nBoundEvents_;

        //- Cells with omega < omegaMin on the last iteration, before the bound
        label nNegOmegaCells_;

        //- min(omega) on the last iteration, before the bound
        scalar omegaMinPreBound_;

        //- Cells with a NEGATIVE omega source on the last iteration (G1c)
        label nNegSourceCells_;


public:

    typedef typename BasicTurbulenceModel::alphaField alphaField;
    typedef typename BasicTurbulenceModel::rhoField rhoField;
    typedef typename BasicTurbulenceModel::transportModel transportModel;


    //- Runtime type information
    TypeName("kOmegaSSTFrozenV2");


    // Constructors

        //- Construct from components
        kOmegaSSTFrozenV2
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
    virtual ~kOmegaSSTFrozenV2() = default;


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

        // ---- R5C diagnostics ----

        bool omegaSourceRepair() const   { return bool(omegaSourceRepair_); }
        label nBoundEvents() const       { return nBoundEvents_; }
        label nNegOmegaCells() const     { return nNegOmegaCells_; }
        scalar omegaMinPreBound() const  { return omegaMinPreBound_; }
        label nNegSourceCells() const    { return nNegSourceCells_; }

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
    #include "kOmegaSSTFrozenV2.C"
#endif

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
