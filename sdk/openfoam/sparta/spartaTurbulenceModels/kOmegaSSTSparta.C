/*---------------------------------------------------------------------------*\
    kOmegaSSTSparta - implementation. See kOmegaSSTSparta.H.

    correct() is the kOmegaSSTCorrected body with the static-field
    corrections replaced by updateCorrections(), which evaluates the
    symbolic model from the current solution each iteration.
\*---------------------------------------------------------------------------*/

#include "kOmegaSSTSparta.H"
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
kOmegaSSTSparta<BasicTurbulenceModel>::kOmegaSSTSparta
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

    RScale_
    (
        dimensioned<scalar>::getOrAddToDict
        (
            "RScale",
            this->coeffDict_,
            1.0
        )
    ),

    bScale_
    (
        dimensioned<scalar>::getOrAddToDict
        (
            "bScale",
            this->coeffDict_,
            1.0
        )
    ),

    RTerms_
    (
        this->coeffDict_.template getOrDefault<List<FixedList<scalar, 4>>>
        (
            "RTerms",
            List<FixedList<scalar, 4>>()
        )
    ),

    bDeltaTerms_
    (
        this->coeffDict_.template getOrDefault<List<FixedList<scalar, 4>>>
        (
            "bDeltaTerms",
            List<FixedList<scalar, 4>>()
        )
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

    tauijRecon_
    (
        IOobject
        (
            "tauijRecon",
            this->runTime_.timeName(),
            this->mesh_,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        this->mesh_,
        dimensionedSymmTensor(sqr(dimVelocity), Zero),
        zeroGradientFvPatchSymmTensorField::typeName
    )
{
    if (type == typeName)
    {
        this->correctNut();
        this->printCoeffs(type);

        Info<< "kOmegaSSTSparta: " << RTerms_.size() << " R term(s), "
            << bDeltaTerms_.size() << " bDelta term(s)" << nl;

        // Evaluate from the construction-time fields so the momentum
        // equation of the very first iteration already sees the model
        {
            tmp<volTensorField> tgradU = fvc::grad(this->U_);
            updateCorrections(tgradU());
        }

        if (this->coeffDict_.template getOrDefault<bool>
            (
                "writeInitialCorrections", false
            ))
        {
            // IC1 implementation cross-check against the Python builder
            kDeficit_.write();
            bijDelta_.write();
        }
    }
}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

template<class BasicTurbulenceModel>
bool kOmegaSSTSparta<BasicTurbulenceModel>::read()
{
    if (kOmegaSST<BasicTurbulenceModel>::read())
    {
        RScale_.readIfPresent(this->coeffDict());
        bScale_.readIfPresent(this->coeffDict());
        this->coeffDict().readIfPresent("RTerms", RTerms_);
        this->coeffDict().readIfPresent("bDeltaTerms", bDeltaTerms_);
        return true;
    }

    return false;
}


template<class BasicTurbulenceModel>
void kOmegaSSTSparta<BasicTurbulenceModel>::updateCorrections
(
    const volTensorField& gradU
)
{
    // Paper conventions (Eqs. 10-12, taken literally):
    //   A_ij = d_j U_i.  OpenFOAM's fvc::grad(U) is (gradU)_ij = d_i U_j,
    //   so A = T(gradU).
    const volTensorField A(T(gradU));

    // tau = 1/omega; omega is bounded below by omegaMin_, so tau is finite
    const volScalarField tau
    (
        dimensionedScalar("one", dimless, 1.0)/this->omega_
    );

    const volSymmTensorField S(tau*symm(A));   // (tau/2)(A + A^T)
    const volTensorField W(tau*skew(A));       // (tau/2)(A - A^T)

    // Invariants: I1 = S_mn S_nm = S && S;  I2 = W_mn W_nm = tr(W.W)
    // = -W_mn W_mn for antisymmetric W, hence I2 <= 0.
    const volScalarField I1(S && S);
    const volScalarField I2(-magSqr(W));

    // Base tensors
    const volSymmTensorField T1(S);
    const volSymmTensorField T2(twoSymm(S & W));          // S.W - W.S
    const volSymmTensorField T3
    (
        symm(S & S) - (scalar(1)/scalar(3))*I*tr(symm(S & S))
    );

    volSymmTensorField bSum
    (
        IOobject("bSum", this->runTime_.timeName(), this->mesh_),
        this->mesh_,
        dimensionedSymmTensor(dimless, Zero)
    );

    for (const FixedList<scalar, 4>& term : bDeltaTerms_)
    {
        const label n = label(term[0]);
        const volSymmTensorField& Tn(n == 1 ? T1 : n == 2 ? T2 : T3);
        bSum += term[3]*pow(I1, term[1])*pow(I2, term[2])*Tn;
    }

    volScalarField rSum
    (
        IOobject("rSum", this->runTime_.timeName(), this->mesh_),
        this->mesh_,
        dimensionedScalar(dimless/dimTime, Zero)
    );

    for (const FixedList<scalar, 4>& term : RTerms_)
    {
        const label n = label(term[0]);
        const volSymmTensorField& Tn(n == 1 ? T1 : n == 2 ? T2 : T3);
        rSum += term[3]*pow(I1, term[1])*pow(I2, term[2])*(Tn && A);
    }

    bijDelta_ = bSum;
    bijDelta_.correctBoundaryConditions();

    // R = 2 k b^R_ij d_j U_i (Eq. 12)
    kDeficit_ = scalar(2)*this->k_*rSum;
    kDeficit_.correctBoundaryConditions();
}


template<class BasicTurbulenceModel>
Foam::tmp<Foam::fvVectorMatrix>
kOmegaSSTSparta<BasicTurbulenceModel>::divDevRhoReff
(
    volVectorField& U
) const
{
    // Stock linearViscousStress terms + divergence of the extra
    // anisotropic stress 2 k b_ij^Delta (Eq. 3 propagated to momentum)
    return
    (
      - fvc::div
        (
            (this->alpha_*this->rho_*this->nuEff())
           *dev2(T(fvc::grad(U)))
        )
      - fvm::laplacian(this->alpha_*this->rho_*this->nuEff(), U)
      + fvc::div
        (
            dev((this->alpha_*this->rho_*((2.0*bScale_)*this->k_))*bijDelta_)
        )
    );
}


template<class BasicTurbulenceModel>
Foam::tmp<Foam::fvVectorMatrix>
kOmegaSSTSparta<BasicTurbulenceModel>::divDevRhoReff
(
    const volScalarField& rho,
    volVectorField& U
) const
{
    return
    (
      - fvc::div
        (
            (this->alpha_*rho*this->nuEff())
           *dev2(T(fvc::grad(U)))
        )
      - fvm::laplacian(this->alpha_*rho*this->nuEff(), U)
      + fvc::div
        (
            dev((this->alpha_*rho*((2.0*bScale_)*this->k_))*bijDelta_)
        )
    );
}


template<class BasicTurbulenceModel>
void kOmegaSSTSparta<BasicTurbulenceModel>::correct()
{
    if (!this->turbulence_)
    {
        return;
    }

    // Local references
    const alphaField& alpha = this->alpha_;
    const rhoField& rho = this->rho_;
    const surfaceScalarField& alphaRhoPhi = this->alphaRhoPhi_;
    const volVectorField& U = this->U_;
    volScalarField& nut = this->nut_;
    volScalarField& k = this->k_;
    volScalarField& omega = this->omega_;
    fv::options& fvOptions(fv::options::New(this->mesh_));

    BasicTurbulenceModel::correct();

    const volScalarField::Internal divU
    (
        fvc::div(fvc::absolute(this->phi(), U))
    );

    tmp<volTensorField> tgradU = fvc::grad(U);
    const volScalarField S2(this->S2(tgradU()));
    volScalarField::Internal GbyNu0(this->GbyNu0(tgradU(), S2));
    volScalarField::Internal G(this->GName(), nut*GbyNu0);

    // Evaluate the symbolic model on the current solution
    updateCorrections(tgradU());

    // Corrections
    const volScalarField::Internal Gextra
    (
        (-2.0*bScale_)*k()*(bijDelta_() && tgradU()())
    );
    const volScalarField::Internal Rcorr
    (
        RScale_*kDeficit_()
    );

    // Update omega and G at the wall (stock pattern)
    omega.boundaryFieldRef().updateCoeffs();
    omega.boundaryFieldRef().template evaluateCoupled<coupledFvPatch>();

    const volScalarField CDkOmega
    (
        (2*this->alphaOmega2_)*(fvc::grad(k) & fvc::grad(omega))/omega
    );

    const volScalarField F1(this->F1(CDkOmega));
    const volScalarField F23(this->F23());

    {
        const volScalarField::Internal gamma(this->gamma(F1));
        const volScalarField::Internal beta(this->beta(F1));

        GbyNu0 = this->GbyNu(GbyNu0, F23(), S2());

        const dimensionedScalar nutSmall
        (
            "nutSmall", nut.dimensions(), 1e-12
        );
        const volScalarField::Internal nutBounded(max(nut(), nutSmall));

        // Turbulent frequency equation: stock + gamma*(Gextra + R)/nut
        tmp<fvScalarMatrix> omegaEqn
        (
            fvm::ddt(alpha, rho, omega)
          + fvm::div(alphaRhoPhi, omega)
          - fvm::laplacian(alpha*rho*this->DomegaEff(F1), omega)
         ==
            alpha()*rho()*gamma*GbyNu0
          + alpha()*rho()*gamma*(Gextra + Rcorr)/nutBounded
          - fvm::SuSp((2.0/3.0)*alpha()*rho()*gamma*divU, omega)
          - fvm::Sp(alpha()*rho()*beta*omega(), omega)
          - fvm::SuSp
            (
                alpha()*rho()*(F1() - scalar(1))*CDkOmega()/omega(),
                omega
            )
          + alpha()*rho()*beta*sqr(this->omegaInf_)
          + this->Qsas(S2(), gamma, beta)
          + this->omegaSource()
          + fvOptions(alpha, rho, omega)
        );

        omegaEqn.ref().relax();
        fvOptions.constrain(omegaEqn.ref());
        omegaEqn.ref().boundaryManipulate(omega.boundaryFieldRef());
        solve(omegaEqn);
        fvOptions.correct(omega);
        bound(omega, this->omegaMin_);
    }

    {
        // Turbulent kinetic energy equation:
        // Pk(G + Gextra) per Eq. 6, plus the R source per Eq. 4
        const volScalarField::Internal Gaug(G + Gextra);

        tmp<fvScalarMatrix> kEqn
        (
            fvm::ddt(alpha, rho, k)
          + fvm::div(alphaRhoPhi, k)
          - fvm::laplacian(alpha*rho*this->DkEff(F1), k)
         ==
            alpha()*rho()*this->Pk(Gaug)
          + alpha()*rho()*Rcorr
          - fvm::SuSp((2.0/3.0)*alpha()*rho()*divU, k)
          - fvm::Sp(alpha()*rho()*this->epsilonByk(F1, tgradU()), k)
          + alpha()*rho()*this->betaStar_*this->omegaInf_*this->kInf_
          + this->kSource()
          + fvOptions(alpha, rho, k)
        );

        kEqn.ref().relax();
        fvOptions.constrain(kEqn.ref());
        solve(kEqn);
        fvOptions.correct(k);
        bound(k, this->kMin_);
    }

    this->correctNut(S2);

    // Reconstructed Reynolds stress for scoring:
    //   tau = (2/3) k I - 2 nu_t S + 2 k bScale bijDelta
    const dimensionedSymmTensor Ident
    (
        "Ident", dimless, symmTensor(1, 0, 0, 1, 0, 1)
    );
    tauijRecon_ =
        (2.0/3.0)*k*Ident
      - 2.0*nut*symm(tgradU())
      + (2.0*bScale_)*k*bijDelta_;

    tgradU.clear();
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace RASModels
} // End namespace Foam

// ************************************************************************* //
