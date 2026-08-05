/*---------------------------------------------------------------------------*\
    kOmegaSSTQCR — implementation. See kOmegaSSTQCR.H for provenance.
\*---------------------------------------------------------------------------*/

#include "kOmegaSSTQCR.H"
#include "fvcGrad.H"
#include "fvcDiv.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace RASModels
{

// * * * * * * * * * * Protected Member Functions  * * * * * * * * * * * * * //

template<class BasicTurbulenceModel>
tmp<volSymmTensorField>
kOmegaSSTQCR<BasicTurbulenceModel>::qcrStress() const
{
    // Velocity gradient: gradU_ij = d(U_j)/d(x_i)
    const volTensorField gradU(fvc::grad(this->U_));

    // Normalisation sqrt(d_n U_m d_n U_m), floored to avoid 0/0 in
    // zero-shear cells (uniform-flow limit: O -> 0 there anyway since
    // the numerator vanishes at the same rate)
    const volScalarField normGradU
    (
        max
        (
            mag(gradU),
            dimensionedScalar("smallGrad", dimless/dimTime, SMALL)
        )
    );

    // Entry Eq. (1): O_ij = (d_j U_i - d_i U_j)/normGradU.
    // With gradU_ij = d_i U_j: d_j U_i = (gradU.T())_ij, so
    // O = (gradU.T() - gradU)/normGradU  (antisymmetric)
    const volTensorField O((gradU.T() - gradU)/normGradU);

    // Linear (Boussinesq) turbulent stress, deviatoric, kinematic:
    // tau^l = 2 nut S - (2/3) k I ; the isotropic part commutes into the
    // commutator as -(2/3)k(O - O) = 0, so only the deviatoric part
    // contributes to the QCR correction. Molecular viscosity excluded:
    // QCR corrects the Reynolds stress only.
    const volSymmTensorField taul(this->nut()*devTwoSymm(gradU));

    // tau_nl = -c_r (O.taul - taul.O)   (symmetric for antisymmetric O)
    return tmp<volSymmTensorField>::New
    (
        IOobject
        (
            IOobject::groupName("qcrStress", this->alphaRhoPhi_.group()),
            this->runTime_.timeName(),
            this->mesh_,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        -Ccr1_*symm((O & taul) - (taul & O))
    );
}


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

template<class BasicTurbulenceModel>
kOmegaSSTQCR<BasicTurbulenceModel>::kOmegaSSTQCR
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
    kOmegaSST<BasicTurbulenceModel>
    (
        alpha,
        rho,
        U,
        alphaRhoPhi,
        phi,
        transport,
        propertiesName,
        type
    ),
    Ccr1_
    (
        dimensioned<scalar>::getOrAddToDict
        (
            "Ccr1",
            this->coeffDict_,
            0.3
        )
    )
{
    if (type == typeName)
    {
        this->printCoeffs(type);
    }
}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

template<class BasicTurbulenceModel>
bool kOmegaSSTQCR<BasicTurbulenceModel>::read()
{
    if (kOmegaSST<BasicTurbulenceModel>::read())
    {
        Ccr1_.readIfPresent(this->coeffDict());
        return true;
    }

    return false;
}


template<class BasicTurbulenceModel>
tmp<volSymmTensorField>
kOmegaSSTQCR<BasicTurbulenceModel>::devRhoReff
(
    const volVectorField& U
) const
{
    return
    (
        // base devRhoReff = -tau_eff_linear; the QCR-corrected stress is
        // -(tau_eff_linear + tau_nl), consistent with divDevRhoReff below
        kOmegaSST<BasicTurbulenceModel>::devRhoReff(U)
      - this->alpha_*this->rho_*qcrStress()
    );
}


template<class BasicTurbulenceModel>
tmp<fvVectorMatrix>
kOmegaSSTQCR<BasicTurbulenceModel>::divDevRhoReff
(
    volVectorField& U
) const
{
    // LHS convention: base returns -div(tau_eff_linear); the total stress
    // gains tau_nl, so the matrix gains -div(alpha rho tau_nl), explicit
    return
    (
        kOmegaSST<BasicTurbulenceModel>::divDevRhoReff(U)
      - fvc::div(this->alpha_*this->rho_*qcrStress())
    );
}


template<class BasicTurbulenceModel>
tmp<fvVectorMatrix>
kOmegaSSTQCR<BasicTurbulenceModel>::divDevRhoReff
(
    const volScalarField& rho,
    volVectorField& U
) const
{
    return
    (
        kOmegaSST<BasicTurbulenceModel>::divDevRhoReff(rho, U)
      - fvc::div(this->alpha_*rho*qcrStress())
    );
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace RASModels
} // End namespace Foam

// ************************************************************************* //
