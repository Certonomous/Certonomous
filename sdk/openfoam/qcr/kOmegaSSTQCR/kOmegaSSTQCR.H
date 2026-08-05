/*---------------------------------------------------------------------------*\
    kOmegaSSTQCR — k-omega SST with the QCR2000 quadratic constitutive
    relation added to the Reynolds stress the momentum equation sees.

    Implements exactly the rank-2 closure-challenge entry's Eq. (1)
    (Zhang, "The Training of the SST-QCRC Model", read in full 2026-08-04,
    W2_WU_ZHANG_DESTRUCTION_FIML_READING.md):

        tau_ij = tau^l_ij - c_r ( O_ik tau^l_kj - tau^l_ik O_kj )
        O_ij   = (d_j U_i - d_i U_j) / sqrt(d_n U_m d_n U_m)
        c_r    = 0.3   (Spalart 2000, untrained)

    which is algebraically identical to NASA TMR's SA-QCR2000 form
    tau_ij,QCR = tau_ij - Ccr1 [O_ik tau_jk + O_jk tau_ik] for symmetric
    tau and antisymmetric O.

    Only the *turbulent* part of the stress (2 nut S, deviatoric) enters
    tau^l; the molecular stress is untouched. The k and omega transport
    equations are inherited unchanged from kOmegaSST — QCR2000 is a
    constitutive-only modification, per Spalart (2000) and per the entry.

    W3 item: w3-qcr-constitutive-term-for-rank2-parity.
    Falsifier instrument for:
    w2-the-duct-zero-stated-as-a-structural-limit-with-a-falsifier.
\*---------------------------------------------------------------------------*/

#ifndef kOmegaSSTQCR_H
#define kOmegaSSTQCR_H

#include "kOmegaSST.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace RASModels
{

/*---------------------------------------------------------------------------*\
                        Class kOmegaSSTQCR Declaration
\*---------------------------------------------------------------------------*/

template<class BasicTurbulenceModel>
class kOmegaSSTQCR
:
    public kOmegaSST<BasicTurbulenceModel>
{
    // Private Member Functions

        //- No copy construct
        kOmegaSSTQCR(const kOmegaSSTQCR&) = delete;

        //- No copy assignment
        void operator=(const kOmegaSSTQCR&) = delete;


protected:

    // Protected data

        //- QCR2000 coefficient (Spalart 2000; entry uses 0.3 untrained)
        dimensionedScalar Ccr1_;


    // Protected Member Functions

        //- The QCR extra stress tau_nl = -c_r (O.taul - taul.O), specific
        //  (kinematic) units, deviatoric turbulent stress taul = 2 nut S
        tmp<volSymmTensorField> qcrStress() const;


public:

    typedef typename BasicTurbulenceModel::alphaField alphaField;
    typedef typename BasicTurbulenceModel::rhoField rhoField;
    typedef typename BasicTurbulenceModel::transportModel transportModel;


    //- Runtime type information
    TypeName("kOmegaSSTQCR");


    // Constructors

        //- Construct from components
        kOmegaSSTQCR
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
    virtual ~kOmegaSSTQCR() = default;


    // Member Functions

        //- Re-read model coefficients if they have changed
        virtual bool read();

        //- Return the effective deviatoric stress (incl. QCR term)
        virtual tmp<volSymmTensorField> devRhoReff
        (
            const volVectorField& U
        ) const;

        //- Return the source term for the momentum equation (incl. QCR)
        virtual tmp<fvVectorMatrix> divDevRhoReff(volVectorField& U) const;

        //- Return the source term for the momentum equation (incl. QCR)
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
    #include "kOmegaSSTQCR.C"
#endif

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
