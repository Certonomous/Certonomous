/*---------------------------------------------------------------------------*\
    kOmegaSSTFrozen - implementation. See kOmegaSSTFrozen.H.
\*---------------------------------------------------------------------------*/

#include "kOmegaSSTFrozen.H"
#include "fvOptions.H"
#include "bound.H"
#include "coupledFvPatch.H"
#include "zeroGradientFvPatchFields.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace RASModels
{

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

template<class BasicTurbulenceModel>
kOmegaSSTFrozen<BasicTurbulenceModel>::kOmegaSSTFrozen
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

    kSmall_("kSmall", sqr(dimVelocity), 1e-10),

    tauijData_
    (
        IOobject
        (
            "tauij",
            this->runTime_.timeName(),
            this->mesh_,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE  // re-written plain (no #include macros)
                                  // so Python-side scoring can read it
        ),
        this->mesh_
    ),

    bijData_
    (
        IOobject
        (
            "bijData",
            this->runTime_.timeName(),
            this->mesh_,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        dev(tauijData_/(2.0*max(this->k_, kSmall_)))
    ),

    kDeficit_
    (
        IOobject
        (
            "kDeficit",
            this->runTime_.timeName(),
            this->mesh_,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        this->mesh_,
        dimensionedScalar(sqr(dimVelocity)/dimTime, Zero),
        zeroGradientFvPatchScalarField::typeName
    ),

    bijDelta_
    (
        IOobject
        (
            "bijDelta",
            this->runTime_.timeName(),
            this->mesh_,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        this->mesh_,
        dimensionedSymmTensor(dimless, Zero),
        zeroGradientFvPatchSymmTensorField::typeName
    ),

    omegaInitialResidual_(GREAT)
{
    if (type == typeName)
    {
        this->correctNut();
        this->printCoeffs(type);
    }
}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

template<class BasicTurbulenceModel>
void kOmegaSSTFrozen<BasicTurbulenceModel>::correct()
{
    if (!this->turbulence_)
    {
        return;
    }

    // Local references (U and k are FROZEN data; only omega is solved)
    const alphaField& alpha = this->alpha_;
    const rhoField& rho = this->rho_;
    const surfaceScalarField& alphaRhoPhi = this->alphaRhoPhi_;
    const volVectorField& U = this->U_;
    const volScalarField& k = this->k_;
    volScalarField& omega = this->omega_;

    const volScalarField::Internal divU
    (
        fvc::div(fvc::absolute(this->phi(), U))
    );

    tmp<volTensorField> tgradU = fvc::grad(U);
    const volScalarField S2(this->S2(tgradU()));

    // Register G under GName() before the omega wall functions run: they
    // look it up and stamp wall-adjacent cell values (stock pattern).
    volScalarField::Internal GbyNu0(this->GbyNu0(tgradU(), S2));
    volScalarField::Internal G(this->GName(), this->nut_*GbyNu0);

    // Update omega wall values (stock pattern: updateCoeffs early, then
    // push wall-function-modified cell values to coupled neighbours)
    omega.boundaryFieldRef().updateCoeffs();
    omega.boundaryFieldRef().template evaluateCoupled<coupledFvPatch>();

    const volScalarField CDkOmega
    (
        (2*this->alphaOmega2_)*(fvc::grad(k) & fvc::grad(omega))/omega
    );

    const volScalarField F1(this->F1(CDkOmega));

    // Production from the frozen data anisotropy, Menter-limited (Eq. 6):
    //   Pk = min(-2 k b_ij dUi/dxj, c1 betaStar k omega), c1 = 10
    const volScalarField::Internal Pk0
    (
        -2.0*k()*(bijData_() && tgradU()())
    );
    const volScalarField::Internal PkLim
    (
        min(Pk0, (this->c1_*this->betaStar_)*k()*omega())
    );

    // R = residual of the steady discrete k equation given the data
    // (Eq. 4 rearranged; OpenFOAM's (2/3) divU correction term included so
    // that R compensates exactly the operators it is propagated through)
    const volScalarField::Internal Rterm
    (
        fvc::div(this->phi(), k)()()
      - fvc::laplacian(this->DkEff(F1), k)()()
      - PkLim
      + (2.0/3.0)*divU*k()
      + this->betaStar_*omega()*k()
    );

    kDeficit_.primitiveFieldRef() = Rterm;
    kDeficit_.correctBoundaryConditions();

    // Frozen omega equation, Eq. 5: production = (gamma/nu_t)(Pk + R)
    {
        const volScalarField::Internal gamma(this->gamma(F1));
        const volScalarField::Internal beta(this->beta(F1));

        const dimensionedScalar nutSmall
        (
            "nutSmall", this->nut_.dimensions(), 1e-12
        );
        const volScalarField::Internal nutBounded
        (
            max(this->nut_(), nutSmall)
        );

        tmp<fvScalarMatrix> omegaEqn
        (
            fvm::ddt(alpha, rho, omega)
          + fvm::div(alphaRhoPhi, omega)
          - fvm::laplacian(alpha*rho*this->DomegaEff(F1), omega)
         ==
            alpha()*rho()*gamma*(PkLim + Rterm)/nutBounded
          - fvm::SuSp((2.0/3.0)*alpha()*rho()*gamma*divU, omega)
          - fvm::Sp(alpha()*rho()*beta*omega(), omega)
          - fvm::SuSp
            (
                alpha()*rho()*(F1() - scalar(1))*CDkOmega()/omega(),
                omega
            )
        );

        omegaEqn.ref().relax();
        omegaEqn.ref().boundaryManipulate(omega.boundaryFieldRef());
        const SolverPerformance<scalar> sp = solve(omegaEqn);
        omegaInitialResidual_ = sp.initialResidual();
        bound(omega, this->omegaMin_);
    }

    // nu_t = a1 k / max(a1 omega, F23 sqrt(S2))  (stock == paper)
    this->correctNut(S2);

    // b_ij^Delta = b_ij,data + (nu_t/k) S_ij   (Eq. 3 rearranged)
    bijDelta_ =
        bijData_
      + (this->nut_/max(k, kSmall_))*symm(tgradU());
}


template<class BasicTurbulenceModel>
Foam::scalar kOmegaSSTFrozen<BasicTurbulenceModel>::verifyKEquation
(
    const scalar RScale,
    const scalar perturbFactor,
    const label nIters
)
{
    // Save frozen state
    const volScalarField kSave("kSave", this->k_);
    const volScalarField nutSave("nutSave", this->nut_);

    volScalarField& k = this->k_;
    const volScalarField& omega = this->omega_;
    const volVectorField& U = this->U_;

    // Perturb the interior
    k.primitiveFieldRef() *= perturbFactor;
    k.correctBoundaryConditions();

    tmp<volTensorField> tgradU = fvc::grad(U);
    const volScalarField::Internal divU
    (
        fvc::div(fvc::absolute(this->phi(), U))
    );

    // Pk is linear in k for fixed b, omega:
    //   Pk = k * min(-2 b_ij dUi/dxj, c1 betaStar omega)
    const volScalarField::Internal pkCoeff
    (
        min
        (
            -2.0*(bijData_() && tgradU()()),
            (this->c1_*this->betaStar_)*omega()
        )
    );

    for (label i = 0; i < nIters; ++i)
    {
        const volScalarField CDkOmega
        (
            (2*this->alphaOmega2_)
           *(fvc::grad(k) & fvc::grad(omega))/omega
        );
        const volScalarField F1(this->F1(CDkOmega));

        tmp<fvScalarMatrix> kEqn
        (
            fvm::div(this->phi(), k)
          - fvm::laplacian(this->DkEff(F1), k)
         ==
            fvm::SuSp(pkCoeff - (2.0/3.0)*divU, k)
          + RScale*kDeficit_()
          - fvm::Sp(this->betaStar_*omega(), k)
        );

        kEqn.ref().relax();
        solve(kEqn);
        bound(k, this->kMin_);
    }

    // Relative L2 drift of the recovered k from the frozen data k
    const scalarField& kNew = k.primitiveField();
    const scalarField& kOld = kSave.primitiveField();
    const scalar drift =
        ::sqrt(gSum(sqr(kNew - kOld)))
       /max(::sqrt(gSum(sqr(kOld))), SMALL);

    // Restore frozen state
    k = kSave;
    this->nut_ = nutSave;
    k.correctBoundaryConditions();
    this->nut_.correctBoundaryConditions();

    return drift;
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace RASModels
} // End namespace Foam

// ************************************************************************* //
