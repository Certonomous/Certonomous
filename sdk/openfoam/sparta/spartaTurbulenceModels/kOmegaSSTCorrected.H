/*---------------------------------------------------------------------------*\
    kOmegaSSTCorrected

    SpaRTA propagation model (Schmelzer, Dwight & Cinnella 2020, Eqs. 3-6):
    stock v2606 kOmegaSST augmented by the two additive model-form
    corrections read as STATIC fields from the start-time directory:

      - kDeficit  (R):        added to the k-equation production and, divided
                              by nu_t and multiplied by gamma, to the omega
                              equation production (Eq. 4, 5);
      - bijDelta  (b_ij^Delta): enters the turbulent production
                              G_extra = -2 k b^Delta_ij dUi/dxj inside
                              Menter's limiter (Eq. 6), the omega production,
                              and the momentum equation through
                              div(2 k b^Delta) (Eq. 3).

    Two coefficients, RScale and bScale (default 1.0, settable in
    kOmegaSSTCorrectedCoeffs), scale the corrections; they exist for the
    L-26 controlled sign experiments (set to -1) and to switch a correction
    off (0). At RScale = bScale = 0 the model reduces exactly to the stock
    kOmegaSST.

    The reconstructed Reynolds stress
        tauijRecon = (2/3) k I - 2 nu_t S + 2 k bScale b^Delta
    is registered AUTO_WRITE for scoring.

    Deviation from the paper, declared in W2_SPARTA_PREREGISTRATION.md:
    the omega production keeps OpenFOAM's stock limited GbyNu term for the
    baseline part and adds gamma*(G_extra + R)/max(nu_t, 1e-12) explicitly,
    so the model reduces exactly to stock at zero corrections.
\*---------------------------------------------------------------------------*/

#ifndef kOmegaSSTCorrected_H
#define kOmegaSSTCorrected_H

#include "kOmegaSST.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace RASModels
{

/*---------------------------------------------------------------------------*\
                     Class kOmegaSSTCorrected Declaration
\*---------------------------------------------------------------------------*/

template<class BasicTurbulenceModel>
class kOmegaSSTCorrected
:
    public kOmegaSST<BasicTurbulenceModel>
{
    // Private Member Functions

        //- No copy construct
        kOmegaSSTCorrected(const kOmegaSSTCorrected&) = delete;

        //- No copy assignment
        void operator=(const kOmegaSSTCorrected&) = delete;


protected:

    // Protected data

        //- Scale on the R (kDeficit) correction (1 = paper, -1 = sign test)
        dimensionedScalar RScale_;

        //- Scale on the bijDelta correction
        dimensionedScalar bScale_;

        //- Static correction field R (m^2/s^3), MUST_READ
        volScalarField kDeficit_;

        //- Static anisotropy correction b_ij^Delta (dimensionless), MUST_READ
        volSymmTensorField bijDelta_;

        //- Reconstructed Reynolds stress, for scoring
        volSymmTensorField tauijRecon_;


public:

    typedef typename BasicTurbulenceModel::alphaField alphaField;
    typedef typename BasicTurbulenceModel::rhoField rhoField;
    typedef typename BasicTurbulenceModel::transportModel transportModel;


    //- Runtime type information
    TypeName("kOmegaSSTCorrected");


    // Constructors

        //- Construct from components
        kOmegaSSTCorrected
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
    virtual ~kOmegaSSTCorrected() = default;


    // Member Functions

        //- Re-read model coefficients if they have changed
        virtual bool read();

        //- Solve the augmented k and omega equations and update nut
        virtual void correct();

        //- Momentum-equation stress divergence, including div(2 k bijDelta)
        virtual tmp<fvVectorMatrix> divDevRhoReff(volVectorField& U) const;

        //- Momentum-equation stress divergence (rho version)
        virtual tmp<fvVectorMatrix> divDevRhoReff
        (
            const volScalarField& rho,
            volVectorField& U
        ) const;
};


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace RASModels
} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#ifdef NoRepository
    #include "kOmegaSSTCorrected.C"
#endif

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
