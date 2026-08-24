#include "createRDeltaT.H"

Info<< "Reading thermophysical properties\n" << endl;

autoPtr<psiThermo> pThermo
(
    psiThermo::New(mesh)
);
psiThermo& thermo = pThermo();

volScalarField& e = thermo.he();

Info<< "Reading field U\n" << endl;
volVectorField U
(
    IOobject
    (
        "U",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

volScalarField rho
(
    IOobject
    (
        "rho",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    thermo.rho()
);

volVectorField rhoU
(
    IOobject
    (
        "rhoU",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::NO_WRITE
    ),
    rho*U
);

volScalarField rhoE
(
    IOobject
    (
        "rhoE",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::NO_WRITE
    ),
    rho*(e + 0.5*magSqr(U))
);

surfaceScalarField pos
(
    IOobject
    (
        "pos",
        runTime.timeName(),
        mesh
    ),
    mesh,
    dimensionedScalar("pos", dimless, 1.0)
);

surfaceScalarField neg
(
    IOobject
    (
        "neg",
        runTime.timeName(),
        mesh
    ),
    mesh,
    dimensionedScalar("neg", dimless, -1.0)
);

surfaceScalarField phi("phi", fvc::flux(rhoU));

// --- Explicit T bound (diagnostic/protective, added for f4_swbli_warmup20) ---
// This case's constant/thermophysicalProperties uses `thermo hConst;`, whose
// limit() is a documented no-op (hConstThermoI.H) -- unlike `janaf`, which
// clamps T to [Tlow,Thigh] inside its own T-inversion (janafThermoI.H). With
// hConst there is therefore no built-in guard against a bad cell's energy
// inverting to a wild T, which then reaches Sutherland's mu = As*sqrt(T)/
// (1+Ts/T) and SIGFPEs on a negative argument -- exactly the crash this
// solver variant exists to diagnose and guard against.
//
// hConst's T-inversion is exact and linear: T = Tref + (e - eref)/Cv, with
// Cv and Tref both true constants for this thermo model (Cp has no T
// dependence, eref defaults to 0, Tref defaults to Tstd=298.15 K -- none of
// which are overridden in this case's thermophysicalProperties). Bounding e
// to the range that maps to [TMin,TMax] under that exact relation therefore
// bounds T exactly, not approximately.
//   Cv = Cp - R = 1005 - (8314.47/28.9) = 1005 - 287.699... = 717.30 J/(kg K)
//   (Cp=1005, molWeight=28.9: both read verbatim from this case's
//   constant/thermophysicalProperties `mixture` sub-dict.)
const dimensionedScalar TMin
(
    "TMin", dimTemperature,
    runTime.controlDict().getOrDefault<scalar>("TMin", 20.0)
);
const dimensionedScalar TMax
(
    "TMax", dimTemperature,
    runTime.controlDict().getOrDefault<scalar>("TMax", 5000.0)
);
const scalar Cv_bound = 1005.0 - 8314.47/28.9;   // 717.30 J/(kg K)
const scalar Tref_bound = 298.15;                // OpenFOAM's Tstd default
const dimensionedScalar eMin_bound
(
    "eMin_bound", dimEnergy/dimMass,
    Cv_bound*(TMin.value() - Tref_bound)
);
const dimensionedScalar eMax_bound
(
    "eMax_bound", dimEnergy/dimMass,
    Cv_bound*(TMax.value() - Tref_bound)
);
Info<< "Bounding e (SWBLI crash guard) to T in ["
    << TMin.value() << ", " << TMax.value() << "] K -> e in ["
    << eMin_bound.value() << ", " << eMax_bound.value() << "] J/kg" << endl;

Info<< "Creating turbulence model\n" << endl;
autoPtr<compressible::turbulenceModel> turbulence
(
    compressible::turbulenceModel::New
    (
        rho,
        U,
        phi,
        thermo
    )
);
