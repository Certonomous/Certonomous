/*---------------------------------------------------------------------------*\
    kOmegaSSTSparta

    SpaRTA symbolic-model propagation (Schmelzer, Dwight & Cinnella 2020,
    Eqs. 9-15, 21-24): stock v2606 kOmegaSST augmented by the two additive
    model-form corrections EVALUATED FROM A SYMBOLIC MODEL each iteration,
    instead of read as static fields (that variant is kOmegaSSTCorrected).

    Model terms are read from kOmegaSSTSpartaCoeffs as lists of
    (tensorIndex I1exponent I2exponent coefficient) quadruples:

        RTerms      ( (1 0 0 0.93) );          // M_R = 0.93 T(1)
        bDeltaTerms ( (1 0 0 0.1) (2 0 0 4.09) );

    with the paper's 2-D basis (Eqs. 10-11), built from the CURRENT solution:
        tau   = 1/omega,
        A_ij  = d_j U_i            (paper's velocity-gradient convention),
        S     = (tau/2) (A + A^T),  W = (tau/2) (A - A^T),
        T(1)  = S,
        T(2)  = S.W - W.S,
        T(3)  = S.S - (1/3) I tr(S.S),
        I1    = S_mn S_nm,          I2 = W_mn W_nm  (I2 <= 0).

    The corrections then are
        bijDelta = sum_m c_m I1^p_m I2^q_m T(n_m)          (dimensionless)
        kDeficit = R = 2 k sum_m c_m I1^p_m I2^q_m (T(n_m) && A)   [m^2/s^3]

    and enter the k, omega and momentum equations exactly as in
    kOmegaSSTCorrected (Eqs. 3-6; same declared omega-limiter deviation).
    RScale/bScale (default 1.0) scale the evaluated corrections for the
    L-26 controlled sign experiments. At zero terms (or RScale = bScale = 0)
    the model reduces exactly to the stock kOmegaSST.

    If writeInitialCorrections is true (default false) the corrections
    evaluated from the construction-time fields are written immediately;
    used by the IC1 implementation cross-check against the Python library
    builder (sdk/scripts/sparta_regression.py).

    tauijRecon = (2/3) k I - 2 nu_t S_dim + 2 k bScale bijDelta is
    registered AUTO_WRITE for scoring, as in kOmegaSSTCorrected.
\*---------------------------------------------------------------------------*/

#ifndef kOmegaSSTSparta_H
#define kOmegaSSTSparta_H

#include "kOmegaSST.H"
#include "FixedList.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace RASModels
{

/*---------------------------------------------------------------------------*\
                      Class kOmegaSSTSparta Declaration
\*---------------------------------------------------------------------------*/

template<class BasicTurbulenceModel>
class kOmegaSSTSparta
:
    public kOmegaSST<BasicTurbulenceModel>
{
    // Private Member Functions

        //- No copy construct
        kOmegaSSTSparta(const kOmegaSSTSparta&) = delete;

        //- No copy assignment
        void operator=(const kOmegaSSTSparta&) = delete;


protected:

    // Protected data

        //- Scale on the evaluated R correction (1 = model, -1 = sign test)
        dimensionedScalar RScale_;

        //- Scale on the evaluated bijDelta correction
        dimensionedScalar bScale_;

        //- Symbolic model terms (tensorIndex, I1 exp, I2 exp, coefficient)
        List<FixedList<scalar, 4>> RTerms_;
        List<FixedList<scalar, 4>> bDeltaTerms_;

        //- Evaluated correction field R (m^2/s^3)
        volScalarField kDeficit_;

        //- Evaluated anisotropy correction b_ij^Delta (dimensionless)
        volSymmTensorField bijDelta_;

        //- Reconstructed Reynolds stress, for scoring
        volSymmTensorField tauijRecon_;


    // Protected Member Functions

        //- Evaluate bijDelta_ and kDeficit_ from the given velocity gradient
        void updateCorrections(const volTensorField& gradU);


public:

    typedef typename BasicTurbulenceModel::alphaField alphaField;
    typedef typename BasicTurbulenceModel::rhoField rhoField;
    typedef typename BasicTurbulenceModel::transportModel transportModel;


    //- Runtime type information
    TypeName("kOmegaSSTSparta");


    // Constructors

        //- Construct from components
        kOmegaSSTSparta
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
    virtual ~kOmegaSSTSparta() = default;


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
    #include "kOmegaSSTSparta.C"
#endif

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
