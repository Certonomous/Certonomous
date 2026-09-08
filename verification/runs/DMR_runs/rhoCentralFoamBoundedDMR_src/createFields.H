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

// --- Positivity-preserving e bound (DMR R3 L5, added for the Mach-10 DMR crash) ---
// The DMR case's constant/thermophysicalProperties uses `thermo hConst;`, whose
// limit() is a documented no-op (hConstThermoI.H) -- unlike `janaf`, which clamps T
// to [Tlow,Thigh] inside its own T-inversion. With hConst there is therefore no
// built-in guard against a bad cell's energy inverting to a negative T; that
// negative T reaches rPsi = 1/psi (proportional to R*T) at rhoCentralFoam.C:136,
// `c = sqrt(Cp/Cv*rPsi)`, and SIGFPEs on the negative sqrt argument -- exactly the
// crash (rc=136) this solver variant exists to prevent (measured at R3, t=0.15464).
//
// hConst's T-inversion is exact and linear: T = Tref + (e - eref)/Cv, with Cv and
// Tref both true constants for this thermo model (Cp has no T dependence, eref
// defaults to 0, Tref defaults to Tstd = 298.15 K -- none overridden in this case's
// thermophysicalProperties). Bounding e to the range that maps to [TMin,TMax] under
// that exact relation therefore bounds T exactly, not approximately.
//
//   DMR NONDIMENSIONAL thermo (constant/thermophysicalProperties, read verbatim):
//     Cp = 2.5, molWeight = 11640.3  ->  R  = 8314.47/11640.3 = 0.714283
//                                        Cv = Cp - R = 2.5 - 0.714283 = 1.785717 J/(kg K)
//                                        gamma = Cp/Cv = 1.40000
//   This is ~400x SMALLER than the SWBLI solver's Cv = 717.30 (Cp=1005, molWeight
//   28.9); using the SWBLI Cv here would misplace the e-bounds by that factor, which
//   is why DMR needs its OWN named solver.
//
//   TMin = 1e-3 is a pure POSITIVITY floor: ambient DMR T = p/(rho*R) =
//   1.0/(1.4*0.714283) = 1.000 (nondim); the flow is shock compression/reflection,
//   all heating, so no physical cell cools below ambient. TMin at 0.1% of ambient
//   (three orders below the coldest physical state) means the low clip can activate
//   ONLY on a nonphysical near-zero/negative-T excursion -- the plant-the-zero
//   discipline in the solver: inert unless the run is already producing an
//   impossible state. TMax = 1e4 is a symmetric runaway ceiling only (never expected
//   to bind; if it does, that is a reported diverging-solve finding). Both are read
//   from controlDict so they are transparent and adjustable without recompiling; the
//   registered values are TMin 1e-3, TMax 1e4.
const dimensionedScalar TMin
(
    "TMin", dimTemperature,
    runTime.controlDict().getOrDefault<scalar>("TMin", 1e-3)
);
const dimensionedScalar TMax
(
    "TMax", dimTemperature,
    runTime.controlDict().getOrDefault<scalar>("TMax", 1e4)
);
const scalar Cv_bound = 2.5 - 8314.47/11640.3;   // = 1.785717 J/(kg K), DMR nondim thermo
const scalar Tref_bound = 298.15;                // OpenFOAM's Tstd default (eref = 0)
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
Info<< "Bounding e (DMR positivity guard) to T in ["
    << TMin.value() << ", " << TMax.value() << "] -> e in ["
    << eMin_bound.value() << ", " << eMax_bound.value() << "] J/kg"
    << " (Cv = " << Cv_bound << ", Tref = " << Tref_bound << ")" << endl;

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
