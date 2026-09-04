#!/usr/bin/env python3
"""M6SR CASE-FILE WRITER -- Section 8 of verification/campaign/M6SR_PREREGISTRATION.md.

WHAT THIS FILE IS.  Section 8 of the frozen registration enumerates, field by field and
dictionary by dictionary, "WHAT A RUNNABLE CASE NEEDS -- ENUMERATED, BECAUSE NONE EXISTS",
and its opening line concedes "Measured: no runnable case exists at any M6 level in any tree
on this box."  Amendment 10 item 10 records that NO REGISTERED ARTIFACT WRITES THEM.  This
file writes them.

IT IS A SOLVER INPUT, NOT A GRADER.  It computes no gate, reads no result and prints no
verdict.  Standing rule 2 fixes the GRADING path at the pre-registration commit; case files
are inputs and writing them before first compute is lawful (Amendment 10 item 10 states this
in terms).  NOTHING HERE MAY EVER GRADE.

EVERY VALUE BELOW IS EITHER QUOTED FROM SECTION 8 OR IS A CHOICE THIS FILE LABELS AS ONE.
The choices are enumerated in CHOICES_MADE_HERE below and are reproduced verbatim into
`<case>/CASE_PROVENANCE.json` at every write, so a reader of the run tree never has to come
back to this source to learn what was chosen.

EXIT VOCABULARY -- Section 9.2, and a CRASH IS NOT A REFUSAL:
    0   the case was written; CASE_PROVENANCE.json carries what was written and why.
    2   REFUSAL.  A precondition of Section 8 does not hold and this writer REFUSES rather
        than degrade -- it never writes a case it cannot justify.
    70  INTERNAL DEFECT of this writer.  Never a finding about the M6.

NO BARE `assert` ANYWHERE (Section 9.2, L-475).  `python3 -O` deletes assert statements, so
a guard set that is assert-based is one interpreter flag from absent.  Every guard below is
an explicit `raise`.  `--selftest` runs this writer's own planted controls and REQUIRES
them to fire.

NOTHING UNDER /home/ubuntu/certonomous-runs/ IS WRITTEN.  Meshes there are read only.
"""

import hashlib
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


class Refusal(Exception):
    """rc 2.  This writer REFUSES rather than write a case it cannot justify."""


class InternalDefect(Exception):
    """rc 70.  A defect in THIS writer.  Never a finding about the M6."""


# =======================================================================================
# SECTION 3 -- THE STATE PAIR.  Every number quoted from the frozen registration's own
# table; none is derived here except where the registration itself shows the arithmetic.
# =======================================================================================
T_INF = 288.15                 # K       Section 3, REGISTERED CHOICE (ISA sea level)
P_INF = 101325.0               # Pa      Section 3, REGISTERED CHOICE (ISA sea level)
GAMMA = 1.4                    #         Section 3
R_GAS = 287.058                # J/(kg K) Section 3 -- "the value matters"
PR_REGISTERED = 0.72           #         Section 3 -- SEE CHOICE 6: NOT SETTABLE under the
                               #         registered `sutherland` transport model.
MACH = 0.8395                  #         Section 3, AGARD AR-138 test 2308
ALPHA_DEG = 3.06               # deg     Section 3
A_INF = 340.297029             # m/s     Section 3, derived sqrt(gamma R T)
U_INF = 285.679356             # m/s     Section 3, derived M * a
RHO_INF = 1.224978126          # kg/m^3  Section 3, derived p/(R T)
MU_INF = 1.929120e-05          # Pa s    Section 3, BACK-SOLVED -- NOT a property of air
NU_INF = 1.574820e-05          # m^2/s   Section 3, derived mu/rho
MAC_C = 0.64607                # m       Section 3 / Amendment 4, the MAC
S_REF = 0.7532                 # m^2     Section 3 / Amendment 4b -- SEE CHOICE 4

# Section 8.1 -- the freestream turbulence CHOICE, with the registration's own formulae.
NUT_INF = 1.574820e-07         # m^2/s   = 0.01 * nu_inf
OMEGA_INF = 2210.901           # 1/s     = 5 * U_inf / MAC
K_INF = 3.481770e-04           # m^2/s^2 = nut_inf * omega_inf
PRT = 0.85                     #         Section 8.1, compressible::alphatWallFunction

# Section 8.4 -- thermophysical constants, every one registered.
MOL_WEIGHT = 28.964425         # NOT OpenFOAM's default 28.9647 (Section 8.4)
CP_THERMO = 1004.5             # J/(kg K)
SUTHERLAND_AS = 1.571860616e-06
SUTHERLAND_TS = 110.4

# Section 8.5 / Section 2.4 -- the per-level schedule.
LEVELS = {
    "L3": {"cells": 99840,   "end_time": 3000, "ranks": 4,  "cap_core_min": 31.0,
           "est_core_min": 10.18},
    "L2": {"cells": 399360,  "end_time": 4000, "ranks": 8,  "cap_core_min": 163.0,
           "est_core_min": 54.31},
    "L1": {"cells": 1597440, "end_time": 5000, "ranks": 16, "cap_core_min": 1630.0,
           "est_core_min": 543.13},
}

# Section 8.5 -- the sampling stations.  A_MAP_YB is Section 4's registered set and is
# imported from the comparator so the two can never drift apart; b_semi is Section 8.5's
# own registered figure.
B_SEMI_M = 1.19676             # Section 8.5, "measured independently from the registered STL"

L_HONEST = (
    "This is a SURFACE-REFINEMENT SENSITIVITY STUDY. Its GCI is a SURFACE-REFINEMENT BAND "
    "and a LOWER BOUND on total discretisation uncertainty. It is NOT an observed order of "
    "accuracy, and it is NOT the family band Sanaa named as her first deliverable."
)


# =======================================================================================
# THE CHOICES.  Section 2 makes a choice lawful BEFORE first compute and only if it is
# RECORDED.  Every one below is a thing Section 8 did not fix, or fixed in a form this
# OpenFOAM does not accept.  EACH CARRIES ITS BASIS AND ITS MEASUREMENT.
# =======================================================================================
CHOICES_MADE_HERE = [
    {
        "id": "CH1",
        "what": "Boundary conditions are attached BY PATCH TYPE, never by patch name.",
        "basis": (
            "Section 7 states in terms that the new L1's patch names 'are produced by "
            "`autoPatch 60` + `createPatch` and are NOT predicted here -- a driver assuming "
            "one name set across levels would silently mis-apply boundary conditions'. "
            "Section 8.1's own column headings are TYPE-labelled ('wing (wall)', 'farfield "
            "(patch)', 'symmetry'). This writer reads constant/polyMesh/boundary, requires "
            "exactly one patch typed 'wall', at least one typed 'symmetry' and at least one "
            "typed 'patch', and REFUSES otherwise."),
    },
    {
        "id": "CH2",
        "what": ("`div(phi,Ekp)  bounded Gauss upwind;` is written, AS RULED BY AMENDMENT 11 "
                 "RULING 1. It is NOT Section 8.2's `div(phi,K)` scheme carried across. "
                 "Section 8.2's `div(phi,K)` entry is ALSO written and is never requested by "
                 "this solver under `energy sensibleInternalEnergy`."),
        "basis": (
            "MEASURED, not recalled, in the solver that will run: "
            "OpenFOAM-v2506 applications/solvers/compressible/rhoSimpleFoam/EEqn.H reads "
            "`he.name() == \"e\" ? fvc::div(phi, volScalarField(\"Ekp\", 0.5*magSqr(U) + "
            "p/rho)) : fvc::div(phi, volScalarField(\"K\", 0.5*magSqr(U)))`. Section 8.4 "
            "registers `energy sensibleInternalEnergy`, so he.name() == \"e\" and the solver "
            "requests `div(phi,Ekp)`. It NEVER requests `div(phi,K)`. Section 8.2 rules "
            "`div(phi,K)` and sets `default none;`, which makes an unruled term a HARD SOLVER "
            "ABORT -- so the frozen fvSchemes as written CANNOT START. "
            "WHY THE SCHEME IS NOT CARRIED ACROSS: Section 8.2 justifies `bounded Gauss "
            "linear` by 'K = |U|^2/2 is a smooth, non-shock-bearing kinematic quantity', and "
            "THAT REASON DOES NOT TRANSFER -- Ekp = |U|^2/2 + p/rho and the p/rho part jumps "
            "across the shock. Amendment 11 Ruling 1 registers `bounded Gauss upwind`, the "
            "scheme Section 8.2 ALREADY ruled for the other half of the same flux "
            "(`div(phi,e)`), for three measured reasons: (i) EEqn.H sums div(phi,he) and "
            "div(phi,Ekp) into one total-enthalpy flux, so two different schemes on the two "
            "halves of one flux is inconsistent; (ii) Ekp enters EXPLICITLY (fvc), so an "
            "unbounded reconstruction across the shock feeds an unbounded source into the "
            "implicit he equation -- the negative-temperature route Section 8.2 already names "
            "for div(phi,e); (iii) in the v2506 tutorial tree, of the 8 fvSchemes under a "
            "STEADY compressible solver family that carry both entries, 8 of 8 give e and Ekp "
            "the IDENTICAL scheme and none splits them, and the only TRANSONIC rhoSimpleFoam "
            "tutorial (squareBend, `transonic yes;`) uses `bounded Gauss upwind` for both."),
    },
    {
        "id": "CH3",
        "what": ("The turbulence model is declared in `constant/turbulenceProperties` under "
                 "the key `RASModel`, NOT in `constant/momentumTransport` under `model`."),
        "basis": (
            "MEASURED in the solver that will run: OpenFOAM-v2506 is the ESI line, in which "
            "every rhoSimpleFoam tutorial in the shipped tree carries constant/"
            "turbulenceProperties and NONE carries constant/momentumTransport; the shipped "
            "aerofoilNACA0012 tutorial reads `RAS { RASModel kOmegaSST; turbulence on; "
            "printCoeffs on; }`. Section 8.4's `momentumTransport` / `RAS { model ... }` is "
            "the OpenFOAM Foundation spelling and would leave this solver with no turbulence "
            "model dictionary. The MODEL, the switches and their values are unchanged."),
    },
    {
        "id": "CH4",
        "what": ("forceCoeffs uses lRef = 0.64607 m (the MAC) and Aref = 0.7532 m^2 "
                 "(S_ref)."),
        "basis": (
            "forceCoeffs REQUIRES both. Section 3 registers both values. "
            "SUPERVISOR ITEM: Amendment 4b rules that 'S_ref IS DISSOLVED. IT IS CONSUMED BY "
            "NOTHING IN THIS DOCUMENT.' Using it as Aref MAKES it consumed. The GATES stay "
            "invariant -- G1's threshold is 1/10 of the L3-L2 C_D difference, G2c's is the "
            "same, and both are RATIOS in which any constant Aref cancels identically -- so "
            "Amendment 4a's gate-by-gate invariance still holds. What is NOT invariant is the "
            "PRINTED VALUE of C_D. The alternative, Aref = 1.0, keeps Amendment 4b literally "
            "true and makes the printed 'C_D' not a drag coefficient. This writer takes the "
            "conventional pair and reports the tension rather than burying either."),
    },
    {
        "id": "CH5",
        "what": "forceCoeffs writes EVERY time step (writeControl timeStep, writeInterval 1).",
        "basis": (
            "Gate G's own instruments demand it: G1 reads the C_D swing over the LAST 500 "
            "ITERATIONS and G2c reads stationarity over the LAST 2,000. Section 8.5 registers "
            "the case's field `writeInterval` as equal to `endTime`, so at the default "
            "`writeControl writeTime` the coefficient file would carry ONE sample and Gate G "
            "would REFUSE for want of a series. The registration fixes no writeControl for "
            "the function objects; this is the only value at which its own gates can be "
            "evaluated."),
    },
    {
        "id": "CH6",
        "what": ("`Pr` is NOT written into thermophysicalProperties. The registered "
                 "`sutherland` transport model does not accept it."),
        "basis": (
            "MEASURED: OpenFOAM-v2506 src/thermophysicalModels/specie/.../sutherlandTransport "
            "reads exactly two coefficients, `As_(readCoeff(\"As\", dict))` and "
            "`Ts_(readCoeff(\"Ts\", dict))`. There is no Pr key; under sutherland the thermal "
            "conductivity comes from the modified Eucken relation. "
            "SUPERVISOR ITEM: Section 3 registers `Pr = 0.72`. The Prandtl number this case "
            "will actually run at is DERIVED FROM THE DOCUMENTED EUCKEN RELATION, NOT "
            "MEASURED, and is reported in CASE_PROVENANCE.json as `Pr_achieved_derived`. It "
            "is NOT 0.72. Section 8.4 registers `sutherland` transport explicitly, so this "
            "writer does not substitute `const` transport to recover Pr; it reports the gap."),
    },
    {
        "id": "CH7",
        "what": "`solverInfo` is written where Section 8.5 registers `residuals`.",
        "basis": (
            "MEASURED: OpenFOAM-v2506 ships src/functionObjects/utilities/solverInfo and NO "
            "functionObject named `residuals`; etc/caseDicts/postProcessing/numerical/ "
            "contains solverInfo and solverInfo.cfg only. `residuals` is the pre-v1912 name. "
            "NOTHING GRADES ON IT: Section 5.1 names scripts/residual_max_over_equations.py "
            "as G2's ONLY instrument and it reads log.rhoSimpleFoam directly, so this "
            "function object is provenance, not an instrument."),
    },
    {
        "id": "CH8",
        "what": ("The freestream velocity vector is BUILT FROM THE DERIVED MESH AXES as "
                 "U_inf*(cos(alpha)*e_chord + sin(alpha)*e_thickness), and the writer "
                 "REFUSES if the derived axes do not put chord on x and thickness on y."),
        "basis": (
            "The comparator's own mesh_axes() records, MEASURED on this box's M6 meshes, that "
            "'the span runs along z (root plane at z = 0), the thickness along y, and the "
            "chord along x', while the registration's Section 5 writes the root section as "
            "'y = 0 exactly' -- the registration's NOTATION, not this box's geometry. "
            "Section 8.1's registered vector (285.2721, 15.2494, 0) is consistent with the "
            "MEASURED convention and not with the notational one. Building the vector from "
            "the derived axes and refusing on a mismatch means a mesh with a different "
            "convention is a FINDING, never a silently mis-oriented freestream."),
    },
    {
        "id": "CH9",
        "what": ("U_x = 285.2721 m/s is written, NOT Section 8.1's tabulated 285.221."),
        "basis": (
            "SUPERVISOR ITEM -- Section 8.1 CONTRADICTS ITSELF. Its table cell reads "
            "`(285.221 15.249 0)` while its own prose two lines below reads '285.679356 x "
            "cos(3.06 deg) = 285.2721'. Recomputed here: 285.679356 * cos(3.06 deg) = "
            "285.27208, which reproduces the PROSE and not the TABLE. Writing 285.221 would "
            "give |U| = 285.6285 m/s and hence M = 0.83935 instead of the registered 0.8395, "
            "and a Reynolds number 0.018 % off the registered 11.72e6 -- i.e. the table's "
            "value does not reproduce the registered state. Both cells write the same formula "
            "`U_inf*(cos 3.06, sin 3.06, 0)`; this writer takes the FORMULA, which is the "
            "content both cells agree on, and reports the transcription slip."),
    },
    {
        "id": "CH10",
        "what": ("`transonic` is left unset in the SIMPLE dictionary, so rhoSimpleFoam runs "
                 "its NON-transonic pressure equation."),
        "basis": (
            "Section 8.3 registers nNonOrthogonalCorrectors, consistent and residualControl "
            "and NOTHING ELSE, so `transonic` takes OpenFOAM's default of `no`. This writer "
            "does not set it, because setting it would be choosing an unregistered numerical "
            "parameter. "
            "SUPERVISOR ITEM: this is a M_inf = 0.8395 TRANSONIC case and rhoSimpleFoam's "
            "transonic switch selects a different pressure equation "
            "(pEqn.H line 14, `if (simple.transonic())`, giving `fvm::div(phid, p)`). "
            "Registration by omission is still registration, and the default is what runs -- "
            "but the registration nowhere states that it considered the switch."),
    },
    {
        "id": "CH11",
        "what": ("system/sampleDict samples the WING PATCH with point interpolation and the "
                 "`foam` surface writer; the seven registered station planes are recorded in "
                 "the same dictionary as data and are CUT BY THE COMPARATOR on that sampled "
                 "surface, not by an OpenFOAM cuttingPlane."),
        "basis": (
            "Section 8.5 registers 'seven constant-y planes at the registered y/b x semispan, "
            "b_semi = 1.19676 m'. An OpenFOAM `cuttingPlane` cuts the VOLUME field and cannot "
            "isolate the wing SURFACE, which is the quantity Gate P grades; and a "
            "functionObject that errors takes 607.63 core-min of solve down with it for an "
            "artifact nothing grades. Sampling the wall patch with `interpolate true` gives "
            "point-valued p on the patch triangulation, and cutting THAT by the seven planes "
            "in the comparator is exact linear interpolation along triangle edges -- it "
            "introduces NO spanwise binning tolerance, which a face-centre reader would have "
            "needed. The seven planes are at the registered stations either way. "
            "DEPARTURE IN FORM FROM SECTION 8.5, RECORDED: the planes are cut downstream of "
            "the solver rather than by it."),
    },
    {
        "id": "CH12",
        "what": ("The level's polyMesh is COPIED into <run_root>/<LEVEL>/constant/polyMesh "
                 "before anything runs."),
        "basis": (
            "L3's and L2's meshes live under /home/ubuntu/certonomous-runs/, which is READ "
            "ONLY, and a solver writes into its own case. The comparator's _discover_levels() "
            "already rules for this: 'An in-run-root copy, once it exists, SUPERSEDES the "
            "read-only source: nothing under /home/ubuntu/certonomous-runs/ is ever written "
            "by this comparator.' The copy is hashed on the DECOMPRESSED point stream and the "
            "hash is published, so Gate A's family-identity proof reads the same bytes it "
            "would have read at the source."),
    },
]


# =======================================================================================
# HELPERS
# =======================================================================================
def _header(cls, obj, loc=None):
    locline = f'    location    "{loc}";\n' if loc else ""
    return ("FoamFile\n{\n"
            "    version     2.0;\n"
            "    format      ascii;\n"
            f"    class       {cls};\n"
            f"{locline}"
            f"    object      {obj};\n"
            "}\n\n")


def _write(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)
    return path


def read_boundary_types(polymesh_dir):
    """-> [(name, type)] using the COMPARATOR'S OWN reader, so the two can never drift.

    A second, independent boundary parser in this repository would be a second definition of
    'what a patch is'.  There is one reader (Section 9.2's spirit) and it is the frozen one.
    """
    try:
        import analyse_m6sr as A
    except ImportError as exc:                                  # pragma: no cover
        raise Refusal(f"the registered comparator is not importable: {exc}. This writer "
                      "derives the patch types and the mesh axes with the COMPARATOR'S OWN "
                      "readers and refuses to carry a second definition of them.")
    try:
        bnd = A.read_boundary(polymesh_dir)
    except A.Refusal as exc:
        raise Refusal(f"the comparator's boundary reader REFUSED {polymesh_dir}: {exc}")
    return [(b["name"], b["type"]) for b in bnd], A


def classify_patches(polymesh_dir):
    """CHOICE CH1.  Attach by TYPE.  Refuse on any count Section 7's screen does not admit."""
    pairs, A = read_boundary_types(polymesh_dir)
    wall = [n for n, t in pairs if t == "wall"]
    symm = [n for n, t in pairs if t == "symmetry"]
    patch = [n for n, t in pairs if t == "patch"]
    empty = [n for n, t in pairs if t == "empty"]
    if empty:
        raise Refusal(
            f"{polymesh_dir}: patch(es) {empty} are typed 'empty'. Section 7 rules that is "
            "never acceptable for this configuration. REFUSED.")
    if len(wall) != 1:
        raise Refusal(
            f"{polymesh_dir}: {len(wall)} patches typed 'wall' ({wall}). Section 8.1 attaches "
            "the wing boundary conditions to THE wall patch and this writer refuses to guess "
            "which one that is. REFUSED.")
    if not symm:
        raise Refusal(
            f"{polymesh_dir}: no patch typed 'symmetry'. Section 7: RUNG1_M6's M0 was a closed "
            "all-wall box and a branch-killing decision was taken off a mesh that could never "
            "have been solved. REFUSED.")
    if not patch:
        raise Refusal(
            f"{polymesh_dir}: no patch typed 'patch'; there is no farfield to attach the "
            "freestream conditions to. REFUSED.")
    return {"wall": wall[0], "symmetry": symm, "farfield": patch, "all": pairs}, A


def freestream_vector(polymesh_dir, A):
    """CHOICE CH8/CH9.  Build U_inf from the DERIVED axes; refuse on an unexpected frame."""
    try:
        axes = A.mesh_axes(polymesh_dir)
    except A.Refusal as exc:
        raise Refusal(f"the comparator's mesh_axes() REFUSED {polymesh_dir}: {exc}. The "
                      "freestream direction cannot be oriented and this writer refuses to "
                      "assume a frame.")
    a = math.radians(ALPHA_DEG)
    vec = [0.0, 0.0, 0.0]
    vec[axes["chord"]] = U_INF * math.cos(a)
    vec[axes["thickness"]] = U_INF * math.sin(a)
    if not (axes["chord"] == 0 and axes["thickness"] == 1 and axes["span"] == 2):
        raise Refusal(
            f"{polymesh_dir}: the derived axes are chord={axes['axis_names']['chord']}, "
            f"thickness={axes['axis_names']['thickness']}, span={axes['axis_names']['span']}. "
            "Section 8.1 registers the freestream as (U cos a, U sin a, 0), which presumes "
            "chord=x and thickness=y. A different frame is a FINDING, not something to adapt "
            "to silently. REFUSED.")
    return vec, axes


def stations(a_map_yb):
    """Section 8.5.  The seven registered y/b times the registered semispan."""
    return [{"index": i + 1, "y_over_b": yb, "span_coord_m": yb * B_SEMI_M}
            for i, yb in enumerate(a_map_yb)]


def pr_achieved_from_eucken():
    """DERIVED FROM THE DOCUMENTED MODIFIED-EUCKEN RELATION.  NOT MEASURED.  See CH6.

    kappa = mu * Cv * (1.32 + 1.77 * R / Cv);  Pr = Cp * mu / kappa.  mu cancels identically,
    so the achieved Pr depends only on Cp and R -- both registered.
    """
    cv = CP_THERMO - R_GAS
    if cv <= 0.0:
        raise InternalDefect(f"Cv = Cp - R = {cv} is not positive; the registered Cp and R "
                             "cannot both be right.")
    return CP_THERMO / (cv * (1.32 + 1.77 * R_GAS / cv))


# =======================================================================================
# THE DICTIONARY WRITERS.  One function per Section 8 subsection.
# =======================================================================================
def write_zero(case, pat, uvec):
    """Section 8.1 -- the seven 0/ fields, with boundary conditions."""
    ff = " ".join(pat["farfield"])
    sy = " ".join(pat["symmetry"])
    w = pat["wall"]
    ux, uy, uz = uvec
    out = {}

    out["U"] = (
        _header("volVectorField", "U", "0") +
        f"dimensions      [0 1 -1 0 0 0 0];\n"
        f"internalField   uniform ({ux!r} {uy!r} {uz!r});\n\n"
        "boundaryField\n{\n"
        f"    {w}\n    {{ type noSlip; }}\n"
        f'    "({ff})"\n'
        f"    {{ type freestreamVelocity; freestreamValue $internalField; }}\n"
        f'    "({sy})"\n'
        "    { type symmetry; }\n}\n")

    out["p"] = (
        _header("volScalarField", "p", "0") +
        "dimensions      [1 -1 -2 0 0 0 0];\n"
        f"internalField   uniform {P_INF!r};\n\n"
        "boundaryField\n{\n"
        f"    {w}\n    {{ type zeroGradient; }}\n"
        f'    "({ff})"\n'
        f"    {{ type freestreamPressure; freestreamValue uniform {P_INF!r}; }}\n"
        f'    "({sy})"\n'
        "    { type symmetry; }\n}\n")

    out["T"] = (
        _header("volScalarField", "T", "0") +
        "dimensions      [0 0 0 1 0 0 0];\n"
        f"internalField   uniform {T_INF!r};\n\n"
        "boundaryField\n{\n"
        f"    {w}\n    {{ type zeroGradient; }}   // adiabatic (Section 8.1)\n"
        f'    "({ff})"\n'
        f"    {{ type inletOutlet; inletValue uniform {T_INF!r}; value $internalField; }}\n"
        f'    "({sy})"\n'
        "    { type symmetry; }\n}\n")

    out["nut"] = (
        _header("volScalarField", "nut", "0") +
        "dimensions      [0 2 -1 0 0 0 0];\n"
        f"internalField   uniform {NUT_INF!r};\n\n"
        "boundaryField\n{\n"
        f"    {w}\n    {{ type nutUSpaldingWallFunction; value uniform 0; }}\n"
        f'    "({ff})"\n'
        "    { type calculated; value $internalField; }\n"
        f'    "({sy})"\n'
        "    { type symmetry; }\n}\n")

    out["k"] = (
        _header("volScalarField", "k", "0") +
        "dimensions      [0 2 -2 0 0 0 0];\n"
        f"internalField   uniform {K_INF!r};\n\n"
        "boundaryField\n{\n"
        f"    {w}\n    {{ type kqRWallFunction; value $internalField; }}\n"
        f'    "({ff})"\n'
        "    { type inletOutlet; inletValue $internalField; value $internalField; }\n"
        f'    "({sy})"\n'
        "    { type symmetry; }\n}\n")

    out["omega"] = (
        _header("volScalarField", "omega", "0") +
        "dimensions      [0 0 -1 0 0 0 0];\n"
        f"internalField   uniform {OMEGA_INF!r};\n\n"
        "boundaryField\n{\n"
        f"    {w}\n    {{ type omegaWallFunction; value $internalField; }}\n"
        f'    "({ff})"\n'
        "    { type inletOutlet; inletValue $internalField; value $internalField; }\n"
        f'    "({sy})"\n'
        "    { type symmetry; }\n}\n")

    out["alphat"] = (
        _header("volScalarField", "alphat", "0") +
        "dimensions      [1 -1 -1 0 0 0 0];\n"
        "internalField   uniform 0;\n\n"
        "boundaryField\n{\n"
        f"    {w}\n"
        f"    {{ type compressible::alphatWallFunction; Prt {PRT!r}; value $internalField; }}\n"
        f'    "({ff})"\n'
        "    { type calculated; value $internalField; }\n"
        f'    "({sy})"\n'
        "    { type symmetry; }\n}\n")

    # THE AGE GUARD, Section 8.6: 0/U DATES the run.  It is written LAST so that no field
    # this writer produces can be newer than it, and every field the SOLVER produces must be.
    order = ["p", "T", "nut", "k", "omega", "alphat", "U"]
    if set(order) != set(out):
        raise InternalDefect(f"the 0/ write order {order} does not cover {sorted(out)}.")
    written = []
    for name in order:
        written.append(_write(os.path.join(case, "0", name), out[name]))
    return written


def write_fv_schemes(case):
    """Section 8.2, plus CHOICE CH2's `div(phi,Ekp)`."""
    return _write(os.path.join(case, "system", "fvSchemes"), (
        _header("dictionary", "fvSchemes", "system") +
        "ddtSchemes      { default steadyState; }\n\n"
        "gradSchemes     { default Gauss linear; }\n\n"
        "divSchemes\n{\n"
        "    default                                       none;\n"
        "    div(phi,U)                                    bounded Gauss linearUpwind grad(U);\n"
        "    div(phi,k)                                    bounded Gauss upwind;\n"
        "    div(phi,omega)                                bounded Gauss upwind;\n"
        "    div(phi,e)                                    bounded Gauss upwind;   // Section 8.2\n"
        "    div(phi,K)                                    bounded Gauss linear;   // Section 8.2\n"
        "    // CHOICE CH2, AS RULED BY AMENDMENT 11 RULING 1.  MEASURED in OpenFOAM-v2506\n"
        "    // rhoSimpleFoam/EEqn.H: with `energy sensibleInternalEnergy` (Section 8.4) the\n"
        "    // solver requests Ekp and NEVER K.  `default none;` makes an unruled term a\n"
        "    // hard abort, so Section 8.2 as frozen cannot start.\n"
        "    // THE SCHEME IS NOT CARRIED ACROSS FROM `div(phi,K)`, AND THE REASON IS THE\n"
        "    // POINT: Section 8.2 justifies `bounded Gauss linear` by 'K = |U|^2/2 is a\n"
        "    // smooth, non-shock-bearing kinematic quantity', and Ekp = |U|^2/2 + p/rho,\n"
        "    // whose p/rho part JUMPS ACROSS THE SHOCK.  Amendment 11 Ruling 1 registers a\n"
        "    // scheme for a SHOCK-BEARING quantity: the same `bounded Gauss upwind` Section\n"
        "    // 8.2 already ruled for `div(phi,e)`, because EEqn.H sums div(phi,he) and\n"
        "    // div(phi,Ekp) into ONE total-enthalpy flux and Ekp enters EXPLICITLY (fvc),\n"
        "    // so an unbounded reconstruction across the shock feeds an unbounded source\n"
        "    // into the implicit he equation.\n"
        "    div(phi,Ekp)                                  bounded Gauss upwind;\n"
        "    div(((rho*nuEff)*dev2(T(grad(U)))))           Gauss linear;           // Section 8.2\n"
        "}\n\n"
        "laplacianSchemes     { default Gauss linear limited corrected 0.5; }\n\n"
        "interpolationSchemes { default linear; }\n\n"
        "snGradSchemes        { default limited corrected 0.5; }\n\n"
        "wallDist             { method meshWave; }\n"))


def write_fv_solution(case):
    """Section 8.3, verbatim.  residualControl is ZERO on every equation, DELIBERATELY."""
    return _write(os.path.join(case, "system", "fvSolution"), (
        _header("dictionary", "fvSolution", "system") +
        "solvers\n{\n"
        "    p       { solver GAMG; smoother GaussSeidel; tolerance 1e-8;  relTol 0.01; }\n"
        '    "(U|e|k|omega)"\n'
        "            { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0.1; }\n"
        "    rho     { solver diagonal; }\n"
        "}\n\n"
        "SIMPLE\n{\n"
        "    nNonOrthogonalCorrectors 2;\n"
        "    consistent               no;\n"
        "    // Section 8.3: ZERO ON EVERY EQUATION, DELIBERATELY.  A non-zero\n"
        "    // residualControl makes simpleFoam write `End` and exit BEFORE endTime,\n"
        "    // which silently breaks standing rule 4's `last time == endTime` clause and\n"
        "    // turns a legitimate run into an un-gradeable one.\n"
        "    residualControl { p 0; U 0; e 0; k 0; omega 0; }\n"
        "    // CHOICE CH10: `transonic` is NOT set.  Section 8.3 registers it nowhere, so\n"
        "    // OpenFOAM's default (no) runs.  See CASE_PROVENANCE.json.\n"
        "}\n\n"
        "relaxationFactors\n"
        "{\n"
        "    fields    { p 0.3; rho 0.05; }\n"
        '    equations { U 0.7; e 0.7; "(k|omega)" 0.7; }\n'
        "}\n"))


def write_constant(case):
    """Section 8.4, with CHOICE CH3 (turbulenceProperties/RASModel) and CH6 (no Pr)."""
    thermo = (
        _header("dictionary", "thermophysicalProperties", "constant") +
        "thermoType\n{\n"
        "    type            hePsiThermo;\n"
        "    mixture         pureMixture;\n"
        "    transport       sutherland;\n"
        "    thermo          hConst;\n"
        "    equationOfState perfectGas;\n"
        "    specie          specie;\n"
        "    energy          sensibleInternalEnergy;\n"
        "}\n\n"
        "// SECTION 8.4: THE SUTHERLAND COEFFICIENTS ARE BACK-SOLVED, NOT PHYSICAL.\n"
        "// As is back-solved so that mu(288.15 K) = 1.929120e-05 Pa s, which is the value\n"
        "// that reproduces Re = 11.72e6 at the registered state pair.  OpenFOAM's own\n"
        "// default air pair (As = 1.4792e-06, Ts = 116) gives mu = 1.790244e-05 Pa s.\n"
        "// THE REGISTERED PAIR IS 7.76 % HIGHER AND IS NOT A PROPERTY OF AIR.  Any\n"
        "// document, figure, table or certificate that cites it as an air viscosity is\n"
        "// citing it wrongly (Section 3).\n"
        "//\n"
        "// CHOICE CH6: Section 3 registers Pr = 0.72.  sutherlandTransport in this\n"
        "// OpenFOAM reads As and Ts ONLY -- there is no Pr key and the conductivity comes\n"
        "// from the modified Eucken relation.  The Pr this case runs at is DERIVED, NOT\n"
        "// MEASURED, and is recorded in CASE_PROVENANCE.json.  It is NOT 0.72.\n"
        "mixture\n{\n"
        f"    specie          {{ molWeight {MOL_WEIGHT!r}; }}\n"
        f"    thermodynamics  {{ Cp {CP_THERMO!r}; Hf 0; }}\n"
        f"    transport       {{ As {SUTHERLAND_AS!r}; Ts {SUTHERLAND_TS!r}; }}\n"
        "}\n")

    turb = (
        _header("dictionary", "turbulenceProperties", "constant") +
        "// CHOICE CH3.  Section 8.4 registers this content in `momentumTransport` under\n"
        "// the key `model`, which is the OpenFOAM Foundation spelling.  MEASURED: this\n"
        "// solver is OpenFOAM-v2506 (ESI), every shipped rhoSimpleFoam tutorial carries\n"
        "// constant/turbulenceProperties and none carries momentumTransport, and the key\n"
        "// is RASModel.  THE MODEL AND THE SWITCHES ARE UNCHANGED.\n"
        "simulationType  RAS;\n\n"
        "RAS\n{\n"
        "    RASModel        kOmegaSST;\n"
        "    turbulence      on;\n"
        "    printCoeffs     on;\n"
        "}\n")
    return [_write(os.path.join(case, "constant", "thermophysicalProperties"), thermo),
            _write(os.path.join(case, "constant", "turbulenceProperties"), turb)]


def write_control_dict(case, end_time, uvec, pat):
    """Section 8.5.  writeInterval == endTime, and WHY that clause is load-bearing."""
    ux, uy, uz = uvec
    mag = math.sqrt(ux * ux + uy * uy + uz * uz)
    a = math.radians(ALPHA_DEG)
    # drag along the freestream, lift normal to it in the same plane (span component zero).
    drag = (math.cos(a), math.sin(a), 0.0)
    lift = (-math.sin(a), math.cos(a), 0.0)
    return _write(os.path.join(case, "system", "controlDict"), (
        _header("dictionary", "controlDict", "system") +
        "application     rhoSimpleFoam;\n"
        "startFrom       startTime;\n"
        "startTime       0;\n"
        "stopAt          endTime;\n"
        f"endTime         {int(end_time)};\n"
        "deltaT          1;\n\n"
        "// SECTION 8.5, AND THIS CLAUSE IS LOAD-BEARING: endTime MUST be an exact multiple\n"
        "// of writeInterval or NO FIELDS ARE WRITTEN AT endTime and standing rule 4's\n"
        "// fields-present clause fails on a run that otherwise succeeded.  Here they are\n"
        "// equal, so exactly one field write happens and it happens at endTime.\n"
        "writeControl    timeStep;\n"
        f"writeInterval   {int(end_time)};\n"
        "purgeWrite      0;\n"
        "writeFormat     ascii;\n"
        "writePrecision  10;\n"
        "writeCompression off;\n"
        "timeFormat      general;\n"
        "timePrecision   6;\n"
        "runTimeModifiable false;\n\n"
        "functions\n{\n"
        "    // CHOICE CH5: forceCoeffs writes EVERY TIME STEP.  G1 needs the C_D swing over\n"
        "    // the last 500 iterations and G2c stationarity over the last 2,000; at the\n"
        "    // default writeControl the coefficient file would carry ONE sample and Gate G\n"
        "    // would REFUSE for want of a series.\n"
        "    forceCoeffs\n"
        "    {\n"
        "        type            forceCoeffs;\n"
        "        libs            (forces);\n"
        "        writeControl    timeStep;\n"
        "        writeInterval   1;\n"
        "        log             yes;\n"
        f"        patches         ({pat['wall']});\n"
        "        rho             rhoInf;\n"
        f"        rhoInf          {RHO_INF!r};\n"
        f"        magUInf         {mag!r};\n"
        f"        liftDir         ({lift[0]!r} {lift[1]!r} {lift[2]!r});\n"
        f"        dragDir         ({drag[0]!r} {drag[1]!r} {drag[2]!r});\n"
        "        CofR            (0 0 0);\n"
        "        pitchAxis       (0 0 1);\n"
        f"        lRef            {MAC_C!r};    // CHOICE CH4: the MAC\n"
        f"        Aref            {S_REF!r};    // CHOICE CH4: S_ref -- see Amendment 4b\n"
        "    }\n\n"
        "    yPlus\n"
        "    {\n"
        "        type            yPlus;\n"
        "        libs            (fieldFunctionObjects);\n"
        "        writeControl    writeTime;\n"
        "        log             yes;\n"
        "    }\n\n"
        "    // CHOICE CH7: `solverInfo` is v2506's name for what Section 8.5 calls\n"
        "    // `residuals`.  NOTHING GRADES ON IT -- Section 5.1 names\n"
        "    // scripts/residual_max_over_equations.py as G2's ONLY instrument and it reads\n"
        "    // log.rhoSimpleFoam directly.  This is provenance.\n"
        "    solverInfo\n"
        "    {\n"
        "        type            solverInfo;\n"
        "        libs            (utilityFunctionObjects);\n"
        "        writeControl    timeStep;\n"
        "        writeInterval   1;\n"
        "        fields          (p U e k omega);\n"
        "    }\n\n"
        '    #include "sampleDict"\n'
        "}\n"))


def write_decompose_par_dict(case, ranks):
    """Section 8.5.  hierarchical (n 1 1), order xyz.  `scotch` is NOT used (Section 3.2)."""
    return _write(os.path.join(case, "system", "decomposeParDict"), (
        _header("dictionary", "decomposeParDict", "system") +
        f"numberOfSubdomains  {int(ranks)};\n\n"
        "// SECTION 3.2: hierarchical is pure geometric bisection with NO RNG, so the\n"
        "// partition is a deterministic function of the recorded coefficient triple and the\n"
        "// cell centres.  scotch is NOT reproducible run-to-run and is NOT used.\n"
        "//\n"
        "// SECTION 9.2, AND IT BINDS EVERY READER OF THIS RUN: RANKS ARE TAKEN FROM THE\n"
        "// SOLVER LOG'S OWN BANNER, NEVER FROM THIS FILE.  This file can post-date the run.\n"
        "method              hierarchical;\n\n"
        "coeffs\n{\n"
        f"    n               ({int(ranks)} 1 1);\n"
        "    order           xyz;\n"
        "}\n"))


def write_sample_dict(case, pat, axes, stns):
    """Section 8.5 / CHOICE CH11.  The wing-patch producer for Gate P's cfd_sections."""
    sp = "xyz"[axes["span"]]
    rows = "\n".join(
        f"//     station {s['index']}  y/b = {s['y_over_b']}  ->  {sp} = "
        f"{s['span_coord_m']:.9f} m" for s in stns)
    path = _write(os.path.join(case, "system", "sampleDict"), (
        _header("dictionary", "sampleDict", "system") +
        "// SECTION 8.5 registers 'seven constant-y planes at the registered y/b x semispan,\n"
        "// b_semi = 1.19676 m'.  CHOICE CH11: the WING PATCH is sampled here with point\n"
        "// interpolation, and the seven planes are cut BY THE COMPARATOR on that sampled\n"
        "// surface -- exact linear interpolation along triangle edges, with NO spanwise\n"
        "// binning tolerance.  An OpenFOAM cuttingPlane cuts the VOLUME field and cannot\n"
        "// isolate the wing SURFACE, which is the quantity Gate P grades.\n"
        "//\n"
        "// THE SEVEN REGISTERED STATIONS, on the DERIVED span axis (the comparator's\n"
        "// mesh_axes() measures the span; Section 5's 'y = 0' is the registration's\n"
        f"// NOTATION and this mesh's span runs along {sp}):\n"
        f"{rows}\n"
        "//\n"
        "// RULE 14: the `libs` entry below is INSERTED, never replaced, and the writer\n"
        "// verifies it is present in the file it just wrote.\n"
        "sampleDict\n"
        "{\n"
        "    type            surfaces;\n"
        "    libs            (sampling);\n"
        "    writeControl    writeTime;\n"
        "    surfaceFormat   foam;\n"
        "    fields          (p);\n"
        "    interpolate     true;\n"
        "    surfaces\n"
        "    {\n"
        "        wingSurface\n"
        "        {\n"
        "            type        patch;\n"
        f"            patches     ({pat['wall']});\n"
        "            interpolate true;\n"
        "            triangulate false;\n"
        "        }\n"
        "    }\n"
        "}\n"))
    text = open(path).read()
    if "libs            (sampling);" not in text:
        raise InternalDefect("the sampleDict was written without its `libs` entry. Rule 14: "
                             "a libs entry is INSERTED WITH AN ASSERT, never assumed.")
    if f"({pat['wall']})" not in text:
        raise InternalDefect("the sampleDict does not name the derived wall patch "
                             f"{pat['wall']!r}; Gate P's producer would sample nothing.")
    return path


# =======================================================================================
# THE ENTRY POINT
# =======================================================================================
def mesh_identity_token(polymesh_dir):
    """A raw-file identity token tying the two write phases to ONE mesh.  -> str.

    IT IS NOT `points_stream_sha` AND IS NOT OFFERED AS ONE.  That function hashes the
    DECOMPRESSED stream and belongs to the comparator's Gate A item A5; this hashes the
    RAW BYTES of exactly the two files BOTH write phases read -- `boundary`, which CH1
    classifies patches from, and the points file, which the freestream axes come from.
    Its ONLY job is to refuse a `zero` phase run against a different mesh from the one the
    `pre-check` phase wrote `system/` for.  It is deliberately a plain hash of named files
    and NOT an import of the grading path (Section 9.1: this file is a solver INPUT).
    """
    parts = []
    for name in ("boundary", "points", "points.gz"):
        p = os.path.join(polymesh_dir, name)
        if os.path.exists(p):
            with open(p, "rb") as fh:
                parts.append(f"{name}:{hashlib.sha256(fh.read()).hexdigest()}")
    if not parts:
        raise Refusal(f"{polymesh_dir} carries neither a boundary file nor a points file, so "
                      "no mesh identity token can be taken. A missing token is a REFUSAL, "
                      "never a fallback.")
    return hashlib.sha256(" ".join(parts).encode()).hexdigest()


# =======================================================================================
# THE TWO WRITE PHASES -- AMENDMENT 21, ITEM 48, ON THE SUPERVISOR'S RULING.
#
# WHY THE CASE WRITE IS SPLIT, AND WHY MOVING THE WHOLE CALL WOULD HAVE BEEN WRONG.
# Section 19.3 ruled, pre-compute, that Section 8's case is written BEFORE `B4` as step
# `B3c`, because `checkMesh` cannot start without `system/`.  MEASURED (Amendment 21):
# `checkMesh -constant` on a case carrying `system/` + `constant/` and NO `0/` returns
# inner rc 0 and a 3330-byte log ending `Mesh OK.` -- byte-for-byte the same size as the
# same probe with `0/` present -- while the same mesh with no `system/` returns inner rc 1.
# SO `checkMesh` NEEDS `system/` AND DOES NOT NEED `0/`.
#
# 🔴 AND MOVING THE WHOLE WRITE WOULD HAVE MADE STANDING RULE 4's AGE GUARD VACUOUS.
# The age guard requires every field at `endTime` to be NEWER than the case's own `0/U`,
# because `0/U` is touched LAST AT LAUNCH and therefore DATES THE RUN ALLOWED TO PRODUCE
# THE ANSWER.  Write `0/` at STAGE time and it predates the solve by the whole stage, so
# every field the solve writes is NECESSARILY newer and THE GUARD PASSES UNCONDITIONALLY.
# A vacuous guard that reports green is worse than an absent one, because it CERTIFIES.
# The supervisor refused this exact substitution on another campaign the same day.
#
# SO: `pre-check` writes `constant/` + `system/` ONLY, and `zero` writes `0/` at solve
# time, keeping the anchor on the launch being graded.  THERE IS STILL ONE CASE WRITER
# (Section 8) -- this is one file with two phases, not a second writer.
# =======================================================================================
def _refuse_if_zero_or_time_dirs(case):
    """SECTION 8.6 -- THE LAUNCHER REFUSES A CASE WHERE `0` OR ANY TIME DIRECTORY EXISTS."""
    if os.path.isdir(os.path.join(case, "0")):
        raise Refusal(f"{case}/0 already exists. The age guard dates the run from the case's "
                      "own 0/U, so a pre-existing 0/ makes standing rule 4 unprovable. "
                      "REFUSED (Section 8.6).")
    for entry in sorted(os.listdir(case)) if os.path.isdir(case) else []:
        if entry[:1].isdigit() and os.path.isdir(os.path.join(case, entry)):
            raise Refusal(f"a time directory already exists: {case}/{entry}. REFUSED "
                          "(Section 8.6).")


def write_case(case, level, polymesh_dir=None, phase="all"):
    if level not in LEVELS:
        raise Refusal(f"{level!r} is not one of {sorted(LEVELS)}. REFUSED.")
    if phase not in ("all", "pre-check", "zero"):
        raise Refusal(f"{phase!r} is not a write phase. REFUSED.")
    spec = LEVELS[level]
    pm = polymesh_dir or os.path.join(case, "constant", "polyMesh")
    if not os.path.isdir(pm):
        raise Refusal(f"{pm} is ABSENT. Section 8.1 attaches boundary conditions BY PATCH "
                      "TYPE (CH1) and there is no boundary file to read them from. An absent "
                      "mesh never reads as a default patch set. REFUSED.")

    _refuse_if_zero_or_time_dirs(case)

    token = mesh_identity_token(pm)
    token_path = os.path.join(case, "MESH_IDENTITY_TOKEN.txt")

    if phase == "zero":
        # THE `zero` PHASE RUNS AT SOLVE TIME, AGAINST A `system/` WRITTEN AT STAGE TIME.
        # It REFUSES unless that `system/` exists and unless the mesh under it is the SAME
        # mesh -- otherwise the two halves of one case could describe two meshes and
        # nothing would announce it.
        for need in (os.path.join(case, "system", "controlDict"),
                     os.path.join(case, "constant", "thermophysicalProperties")):
            if not os.path.exists(need):
                raise Refusal(
                    f"phase 'zero' requires the 'pre-check' phase to have run first, and "
                    f"{need} is ABSENT. This phase writes 0/ ONLY; it does not silently "
                    f"write the rest of the case. REFUSED.")
        prev = open(token_path).read().split()[0] if os.path.exists(token_path) else None
        if prev is None:
            raise Refusal(
                f"phase 'zero' found no mesh identity token at {token_path}. The token is "
                "what ties 0/ to the same mesh system/ was written for; without it that tie "
                "cannot be checked and this phase will NOT assume it. REFUSED.")
        if prev != token:
            raise Refusal(
                f"MESH IDENTITY MISMATCH: system/ was written for a mesh hashing {prev}, and "
                f"{pm} now hashes {token}. 0/ attaches boundary conditions BY PATCH TYPE from "
                "this mesh's boundary file while system/ already names patches from another. "
                "REFUSED rather than writing half a case against each.")

    pat, A = classify_patches(pm)
    uvec, axes = freestream_vector(pm, A)
    stns = stations(A.A_MAP_YB)

    written = []
    if phase in ("all", "pre-check"):
        written += write_constant(case)
        written.append(write_fv_schemes(case))
        written.append(write_fv_solution(case))
        written.append(write_decompose_par_dict(case, spec["ranks"]))
        written.append(write_sample_dict(case, pat, axes, stns))
        written.append(write_control_dict(case, spec["end_time"], uvec, pat))
        written.append(_write(token_path, token + "\n"))
    if phase in ("all", "zero"):
        # 0/ LAST, and 0/U last within it -- Section 8.6's age guard.
        written += write_zero(case, pat, uvec)

    mag = math.sqrt(sum(c * c for c in uvec))
    prov = {
        "level": level,
        "case": case,
        "polymesh_read": pm,
        "write_phase": phase,
        "mesh_identity_token": token,
        "write_phase_note": (
            "AMENDMENT 21, ITEM 48. 'pre-check' writes constant/ + system/ only, at step "
            "B3c, BEFORE B4's checkMesh -- MEASURED: checkMesh -constant returns inner rc 0 "
            "and a 3330-byte log ending 'Mesh OK.' on a case with system/ and NO 0/, and "
            "inner rc 1 with no system/ at all. 'zero' writes 0/ ONLY, at solve time. "
            "0/ IS NOT WRITTEN EARLY ON PURPOSE: rule 4's age guard dates the run from the "
            "case's own 0/U, so a 0/U written at stage time would predate every field the "
            "solve writes and THE GUARD WOULD PASS UNCONDITIONALLY. The token above ties "
            "the two phases to one mesh and 'zero' REFUSES on a mismatch."),
        "written": written,
        "registration": "verification/campaign/M6SR_PREREGISTRATION.md Section 8",
        "THIS_FILE_IS_A_SOLVER_INPUT_NOT_A_GRADER": (
            "It computes no gate, reads no result and prints no verdict. Standing rule 2 "
            "fixes the GRADING path at the pre-registration commit; case files are INPUTS "
            "and writing them before first compute is lawful (Amendment 10 item 10)."),
        "schedule": {"end_time": spec["end_time"], "ranks": spec["ranks"],
                     "cells": spec["cells"], "cap_core_min": spec["cap_core_min"],
                     "est_core_min": spec["est_core_min"]},
        "patches_by_TYPE_never_by_name": pat,
        "derived_axes": axes,
        "freestream": {
            "U_vector_written": uvec,
            "magnitude_written": mag,
            "Section_8_1_table_cell": "(285.221 15.249 0)",
            "Section_8_1_prose": "285.679356 * cos(3.06 deg) = 285.2721",
            "DISCREPANCY": (
                "The Section 8.1 TABLE and its own PROSE disagree in the fourth significant "
                "figure of U_x. The formula both cells carry gives 285.27208. The table's "
                "285.221 would give |U| = 285.6285 m/s, M = 0.83935 against the registered "
                "0.8395, and Re 0.018 % from the registered 11.72e6. CHOICE CH9 takes the "
                "formula. REPORTED, NOT REPAIRED."),
            "Mach_reproduced": mag / A_INF,
            "Reynolds_reproduced_on_MAC": RHO_INF * mag * MAC_C / MU_INF,
        },
        "stations_Section_8_5": stns,
        "b_semi_m_REGISTERED": B_SEMI_M,
        "A_MAP_YB_source": (
            "the comparator's own frozen A_MAP_YB constant, which Section 16.4 records as "
            "read at source in docs/papers/benchmark_test_cases/"
            "agard_1979_ar138_experimental_data_base.txt lines 13728-13729: '271 pressure "
            "orifices divided in 7 sections (y/b = 0.20/0.44/0.65/0.80/0.90/0.96 and 0.99)'. "
            "THE SIXTH STATION IS 0.96, NOT NASA TMR's 0.95, and Section 16.4 registers that "
            "divergence as REPORTED, NOT GATED."),
        "Pr_registered_Section_3": PR_REGISTERED,
        "Pr_achieved_derived": pr_achieved_from_eucken(),
        "Pr_basis": (
            "DERIVED FROM THE DOCUMENTED MODIFIED-EUCKEN RELATION kappa = mu Cv (1.32 + 1.77 "
            "R/Cv), NOT MEASURED IN A SOLVER RUN. mu cancels, so it depends only on the "
            "registered Cp and R. See CHOICE CH6: sutherland transport accepts no Pr key."),
        "choices": CHOICES_MADE_HERE,
        "cost_basis": (
            "core-minutes = wall s x ranks / 60. Dollars are DERIVED, NOT MEASURED, at the "
            "owner-stated c7a.4xlarge $0.0513/core-h -- the box cannot read its own billing "
            "(COMPUTE_BUDGET_CHARTER.md 5), so any dollar figure originating here is "
            "REPORTED-BY-OWNER. RANKS ARE READ FROM THE SOLVER LOG'S BANNER, NEVER FROM "
            "system/decomposeParDict (Section 9.2, Amendment 8)."),
        "L_HONEST": L_HONEST,
    }
    _write(os.path.join(case, "CASE_PROVENANCE.json"), json.dumps(prov, indent=2) + "\n")
    return prov


# =======================================================================================
# PLANTED CONTROLS -- rule 3.  A writer that cannot be shown to WRITE the value it claims
# to write is not evidence that the case says what this file says it says.
# =======================================================================================
def _fixture_boundary(path, entries):
    """A polyMesh/boundary file in the EXACT form the comparator's reader parses.

    The form is not cosmetic: the reader's _strip_foam_header() keys on the `// * * *`
    separator and on the `<count>\\n(` list opening, and its per-entry regex requires the
    patch name on its own line.  A fixture in any other shape would make the control pass
    by not being read at all, which is precisely the zero rule 3 forbids.
    """
    body = "".join(f"    {n}\n    {{\n        type            {t};\n"
                   f"        nFaces          {nf};\n        startFace       {sf};\n    }}\n"
                   for n, t, nf, sf in entries)
    return _write(path,
                  _header("polyBoundaryMesh", "boundary", "constant") +
                  "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n"
                  f"{len(entries)}\n(\n{body})\n")


def _mutate_k_and_write(case4, pm, pat, uvec, keep, bad):
    """W4's mutation, isolated so the module-global rebind is the ONLY thing in scope.

    -> True if the case written under the CORRUPTED k_inf still carries the registered
    value, i.e. if W3's reader would have been fooled.  It must come back False.
    """
    import shutil
    global K_INF
    try:
        K_INF = bad
        os.makedirs(os.path.join(case4, "constant"), exist_ok=True)
        shutil.copytree(pm, os.path.join(case4, "constant", "polyMesh"))
        write_zero(case4, pat, uvec)
        return f"uniform {keep!r};" in open(os.path.join(case4, "0", "k")).read()
    finally:
        K_INF = keep


_SELFTEST_REAL_POLYMESH = (
    "/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/constant/polyMesh")


def _run_phase_controls(scratch, pm_real, rec, shutil):
    """W6 and W7 -- Amendment 21, item 48.  Driven on a REAL polyMesh."""
    # ---- W6.  AMENDMENT 21, ITEM 48 -- THE TWO WRITE PHASES, AND THE PROPERTY THAT MATTERS.
    # `pre-check` MUST NOT write `0/`.  That is not tidiness: rule 4's age guard dates the run
    # from the case's own `0/U`, and `0/U` earns that role only by being touched LAST AT
    # LAUNCH.  Written at STAGE time it predates every field the solve writes, so THE GUARD
    # PASSES UNCONDITIONALLY -- a guard that cannot fail is worse than an absent one because
    # it certifies.  Both halves are driven here and read back FROM DISK.
    w6 = os.path.join(scratch, "w6", "L3")
    os.makedirs(os.path.join(w6, "constant"), exist_ok=True)
    shutil.copytree(pm_real, os.path.join(w6, "constant", "polyMesh"))
    write_case(w6, "L3", phase="pre-check")
    w6_pre_no_zero = not os.path.isdir(os.path.join(w6, "0"))
    w6_sys = os.path.exists(os.path.join(w6, "system", "controlDict"))
    w6_tok = os.path.exists(os.path.join(w6, "MESH_IDENTITY_TOKEN.txt"))
    time.sleep(0.02)
    write_case(w6, "L3", phase="zero")
    w6_zero = os.path.isdir(os.path.join(w6, "0"))
    u_m = os.path.getmtime(os.path.join(w6, "0", "U"))
    cd_m = os.path.getmtime(os.path.join(w6, "system", "controlDict"))
    w6_anchor_last = u_m > cd_m
    rec("W6", w6_pre_no_zero and w6_sys and w6_tok and w6_zero and w6_anchor_last,
        f"phase 'pre-check' wrote system/controlDict={w6_sys} and the mesh identity "
        f"token={w6_tok} and DID NOT write 0/ ({w6_pre_no_zero}); phase 'zero' then wrote 0/ "
        f"({w6_zero}) with 0/U NEWER than system/controlDict ({w6_anchor_last}). THE ANCHOR "
        f"IS LAID AT SOLVE TIME, NOT AT STAGE TIME -- a 0/U written by 'pre-check' would "
        f"predate every field the solve writes and rule 4's age guard would pass "
        f"UNCONDITIONALLY while still reporting green.")

    # ---- W7.  THE `zero` PHASE'S TWO REFUSALS, EACH PLANTED.  A phase that cannot refuse a
    # missing `system/` or a MOVED MESH would let one case describe two meshes silently.
    w7a = os.path.join(scratch, "w7a", "L3")
    os.makedirs(os.path.join(w7a, "constant"), exist_ok=True)
    shutil.copytree(pm_real, os.path.join(w7a, "constant", "polyMesh"))
    try:
        write_case(w7a, "L3", phase="zero")
        w7_nosys, m7a = False, "phase 'zero' ran with NO system/ and did not refuse"
    except Refusal as exc:
        w7_nosys = "requires the 'pre-check' phase to have run first" in str(exc)
        m7a = str(exc)[:110]
    w7b = os.path.join(scratch, "w7b", "L3")
    os.makedirs(os.path.join(w7b, "constant"), exist_ok=True)
    shutil.copytree(pm_real, os.path.join(w7b, "constant", "polyMesh"))
    write_case(w7b, "L3", phase="pre-check")
    _write(os.path.join(w7b, "MESH_IDENTITY_TOKEN.txt"), "0" * 64 + "\n")   # THE PLANT
    try:
        write_case(w7b, "L3", phase="zero")
        w7_tok, m7b = False, "a MOVED mesh identity token did not refuse"
    except Refusal as exc:
        w7_tok = "MESH IDENTITY MISMATCH" in str(exc)
        m7b = str(exc)[:110]
    rec("W7", w7_nosys and w7_tok,
        f"planted a 'zero' phase with no system/ at all -- REFUSED: {m7a}. Planted a MOVED "
        f"mesh identity token on an otherwise complete case -- REFUSED: {m7b}. Neither "
        f"refusal existed before Amendment 21, because neither phase existed.")


def selftest(scratch):
    """Each control PLANTS a change and READS IT BACK FROM DISK, and the suite refuses if
    any of them does not fire.  A control that cannot be broken is not a control, so W4
    MUTATES a shipped value and requires exactly its own control to go red."""
    import shutil
    import tempfile
    fired, detail = {}, {}

    def rec(cid, ok, msg):
        fired[cid] = bool(ok)
        detail[cid] = msg

    # ---- W1.  A synthetic polyMesh boundary with KNOWN, UNGUESSABLE patch names.  If the
    # writer attached by NAME rather than by TYPE (CH1) this control could not pass.
    root = os.path.join(scratch, "w1")
    pm = os.path.join(root, "constant", "polyMesh")
    os.makedirs(pm, exist_ok=True)
    _fixture_boundary(os.path.join(pm, "boundary"),
                      [("zzWingSurfaceQ7", "wall", 4, 0),
                       ("zzOuterQ7", "patch", 4, 4),
                       ("zzRootPlaneQ7", "symmetry", 1, 8)])
    pairs, A = read_boundary_types(pm)
    pat, _A = classify_patches(pm)
    rec("W1", pat["wall"] == "zzWingSurfaceQ7"
        and pat["farfield"] == ["zzOuterQ7"]
        and pat["symmetry"] == ["zzRootPlaneQ7"],
        f"planted unguessable patch NAMES {[n for n, _ in pairs]}; the writer classified "
        f"them by TYPE as wall={pat['wall']}, farfield={pat['farfield']}, "
        f"symmetry={pat['symmetry']}")

    # ---- W2.  Plant a SECOND wall patch.  The writer must REFUSE, not pick one.
    pm2 = os.path.join(scratch, "w2", "constant", "polyMesh")
    os.makedirs(pm2, exist_ok=True)
    _fixture_boundary(os.path.join(pm2, "boundary"),
                      [("zzWingSurfaceQ7", "wall", 4, 0),
                       ("zzSecondWallQ7", "wall", 4, 4),
                       ("zzOuterQ7", "patch", 4, 8),
                       ("zzRootPlaneQ7", "symmetry", 1, 12)])
    try:
        classify_patches(pm2)
        rec("W2", False, "a second wall patch was planted and the writer did NOT refuse")
    except Refusal as exc:
        rec("W2", "2 patches typed 'wall'" in str(exc),
            f"planted a second wall patch; the writer REFUSED: {exc}")

    # ---- W3.  THE ZERO IS PLANTED.  Write a case, then read the seven 0/ fields BACK FROM
    # DISK and require the registered internal values to be THERE.  A writer whose reader
    # cannot see a non-value is not evidence (rule 3).
    case = os.path.join(scratch, "w3", "L3")
    os.makedirs(os.path.join(case, "constant"), exist_ok=True)
    shutil.copytree(pm, os.path.join(case, "constant", "polyMesh"))
    # mesh_axes needs points/faces; the synthetic boundary alone cannot supply them, so W3
    # writes only the parts that do not need a frame, and W3b proves the frame guard fires.
    pat3, A3 = classify_patches(os.path.join(case, "constant", "polyMesh"))
    uvec3 = [U_INF * math.cos(math.radians(ALPHA_DEG)),
             U_INF * math.sin(math.radians(ALPHA_DEG)), 0.0]
    write_zero(case, pat3, uvec3)
    seen = {}
    for f, want in (("p", repr(P_INF)), ("T", repr(T_INF)), ("nut", repr(NUT_INF)),
                    ("k", repr(K_INF)), ("omega", repr(OMEGA_INF))):
        txt = open(os.path.join(case, "0", f)).read()
        seen[f] = (f"uniform {want};" in txt)
    utxt = open(os.path.join(case, "0", "U")).read()
    seen["U"] = (repr(uvec3[0]) in utxt and repr(uvec3[1]) in utxt)
    seen["alphat_Prt"] = (f"Prt {PRT!r};" in open(os.path.join(case, "0", "alphat")).read())
    rec("W3", all(seen.values()),
        f"wrote the seven 0/ fields and read every registered internal value BACK FROM "
        f"DISK: {seen}")

    # ---- W3b.  THE AGE GUARD's ordering.  0/U must be the NEWEST file this writer produced,
    # because Section 8.6 dates the run from it.  Read the mtimes back from disk.
    mts = {f: os.path.getmtime(os.path.join(case, "0", f))
           for f in ("p", "T", "nut", "k", "omega", "alphat", "U")}
    rec("W3b", mts["U"] >= max(v for k, v in mts.items() if k != "U"),
        f"0/U mtime {mts['U']!r} is >= every other 0/ field's; Section 8.6's age guard dates "
        "the run from 0/U, so it must be written LAST")

    # ---- W6 / W7 NEED A REAL polyMesh, and that dependency is NAMED rather than hidden.
    # The W1/W3 fixture is a BOUNDARY FILE ONLY -- W3's own comment says so: "mesh_axes needs
    # points/faces; the synthetic boundary alone cannot supply them".  `write_case()` derives
    # the freestream frame from the mesh, so the phase controls cannot run on that fixture.
    # They use THIS FAMILY'S OWN L3 polyMesh, and if it is absent they go RED WITH A REASON
    # rather than being skipped -- a control that quietly does not run is worse than one that
    # fails, and Amendment 20's C29 already takes this shape for the createPatchDict pin.
    pm_real = _SELFTEST_REAL_POLYMESH
    if not os.path.isdir(pm_real):
        rec("W6", False, f"the real polyMesh {pm_real} is ABSENT, so the phase controls "
                         "could not be driven. THIS IS RED, NOT SKIPPED.")
        rec("W7", False, f"the real polyMesh {pm_real} is ABSENT, so the phase refusals "
                         "could not be driven. THIS IS RED, NOT SKIPPED.")
    else:
      _run_phase_controls(scratch, pm_real, rec, shutil)

    # ---- W4.  THE MUTATION CONTROL.  Break a SHIPPED statistic and require the suite RED.
    # The test is on the DELTA -- exactly W3 must flip -- because 'the suite went red' is
    # worthless once anything is red for an unrelated reason.
    keep = K_INF
    mutated_seen = _mutate_k_and_write(os.path.join(scratch, "w4", "L3"), pm, pat3, uvec3,
                                       keep, keep * 1.5)
    rec("W4", not mutated_seen,
        f"MUTATION: k_inf replaced by {keep * 1.5!r}; the file then does NOT carry the "
        f"registered {keep!r}, so W3's reader would have gone red. A shipped value that "
        "cannot be broken is not being read.")

    # ---- W5.  The frame guard.  A mesh whose axes are not (chord=x, thickness=y, span=z)
    # must REFUSE, never silently re-orient the freestream.
    class _FakeAxes:
        Refusal = Refusal

        @staticmethod
        def mesh_axes(_p):
            return {"span": 0, "chord": 1, "thickness": 2, "root_value": 0.0,
                    "axis_names": {"span": "x", "chord": "y", "thickness": "z"}}
    try:
        freestream_vector("irrelevant", _FakeAxes)
        rec("W5", False, "a rotated frame was planted and the writer did NOT refuse")
    except Refusal as exc:
        rec("W5", "REFUSED" in str(exc),
            f"planted a rotated axis frame (chord=y, span=x); the writer REFUSED: {exc}")

    del tempfile
    return fired, detail


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(add_help=True, description=__doc__)
    ap.add_argument("--case", help="the case directory to write into")
    ap.add_argument("--level", choices=sorted(LEVELS), help="L3 / L2 / L1")
    ap.add_argument("--polymesh", default=None,
                    help="override the polyMesh read for patch types and axes")
    ap.add_argument("--phase", default="all", choices=("all", "pre-check", "zero"),
                    help="AMENDMENT 21, ITEM 48. `pre-check` writes constant/ + system/ "
                         "ONLY, for step B3c before B4's checkMesh -- MEASURED: checkMesh "
                         "needs system/ and does NOT need 0/. `zero` writes 0/ ONLY, at "
                         "solve time, so rule 4's age-guard anchor is still touched at the "
                         "launch being graded; writing 0/ at stage time would make that "
                         "guard PASS UNCONDITIONALLY. Default `all` is the unchanged "
                         "single-shot behaviour.")
    ap.add_argument("--selftest", action="store_true",
                    help="run this writer's planted controls and the mutation control")
    ap.add_argument("--scratch", default=None)
    args = ap.parse_args(argv[1:])

    if args.selftest:
        import tempfile
        scratch = args.scratch or tempfile.mkdtemp(prefix="m6sr_writer_controls_")
        os.makedirs(scratch, exist_ok=True)
        fired, detail = selftest(scratch)
        for cid in sorted(fired, key=lambda s: (len(s), s)):
            print(f"WRITER CONTROL {cid:4s} {'FIRED' if fired[cid] else 'DID NOT FIRE'} : "
                  f"{detail[cid]}")
        if not all(fired.values()):
            raise Refusal(
                "A PLANTED CONTROL DID NOT FIRE: "
                f"{[c for c in sorted(fired) if not fired[c]]}. A case written by a writer "
                "whose plant did not fire is not evidence that the case says what this file "
                "says it says (rule 3). REFUSED.")
        print("ALL WRITER CONTROLS FIRED.")
        print(f"L-HONEST: {L_HONEST}")
        return 0

    if not args.case or not args.level:
        ap.print_help()
        return 0
    prov = write_case(args.case, args.level, args.polymesh, phase=args.phase)
    print(json.dumps(prov, indent=2, default=str))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Refusal as _exc:
        print(f"REFUSED: {_exc}", file=sys.stderr)
        sys.exit(2)
    except InternalDefect as _exc:
        print(f"INTERNAL DEFECT of the case writer: {_exc}", file=sys.stderr)
        sys.exit(70)
    except Exception as _exc:            # a crash is NOT a refusal -- it is rc 70
        import traceback
        traceback.print_exc()
        print(f"INTERNAL DEFECT (unhandled {type(_exc).__name__}): {_exc}", file=sys.stderr)
        sys.exit(70)
