#!/usr/bin/env python3
"""K0d case builder -- writes ONLY what the frozen registration registers.

Written 2026-08-25 from the FROZEN registration and from nothing else:
  docs/campaigns/F14-cooling-ladder/K0d_REREGISTRATION.md   (v1.1, blob 36b302f1)
  docs/campaigns/F14-cooling-ladder/K0d_PREREGISTRATION.md  (v1.5, blob e629f5c4)

THE BINDING CONSTRAINT ON THIS FILE is superseded section A5.11, quoted:

  1. "It implements what this document registers, and nothing else."
  2. "IT MAY NOT CHOOSE ANYTHING THIS DOCUMENT LEAVES OPEN.  If the builder
     reaches a value this document does not fix, that is a finding, it is
     referred upward, and it is registered by amendment while the window is
     open -- IT IS NOT CHOSEN BY THE SCRIPT."
  3. "It copies nothing from the smoke-test directory without checking it
     against section A5.6's table entry by entry."

Clause 2 is implemented literally.  REGISTRATION_GAPS below lists every input
this builder needs that the registration does not fix.  While any of them is
unresolved THIS SCRIPT REFUSES (exit 2) AND WRITES NOTHING.  It does not take
them from the command line, from an environment variable or from a default:
each of those would be this script choosing, which clause 2 forbids.  They are
resolved by the supervisor registering them in an amendment, at which point the
value is written into the table below and this comment is why.

The smoke-test dictionaries in /home/ubuntu/certonomous-runs/K0d_smoke_L1/ are
SCRATCH DRAFTS (A5.11 clause 2, A2.4 clause 2).  This script reads them for
nothing and copies from them nothing.

Exit codes:  0  every requested case written
             1  a case could not be written for a stated reason
             2  REFUSAL -- an unresolved registration gap, an unregistered
                closure or seed, or a case directory that already exists

Usage:
    python3 build_k0f.py --root <K0f_runs dir> [case ...]
    python3 build_k0f.py --selftest
"""
import argparse
import os
import re
import sys

EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

# ==========================================================================
# THE REGISTRATION GAPS -- ALL FOUR CLOSED BY AMENDMENT 2, 2026-08-25.
#
# Each was None because the frozen registration did not fix it, and A5.11
# clause 2 forbids this script choosing any of them.  THE SCRIPT STILL DOES NOT
# CHOOSE THEM: each value below is READ OFF the amendment section named in its
# `fixed_by` field, which was committed BEFORE first compute and BEFORE this
# table was filled in.  The window was open (K0f_runs did not exist) and the
# condition was checked in the amendment's own committing invocation under a
# planted control.
#
#   writeFormat        ascii   AMENDMENT 2 section A2.1a
#   writePrecision     16      AMENDMENT 2 section A2.1b
#   writeCompression   off     AMENDMENT 2 section A2.1c
#   domain_thickness_t 0.010 m AMENDMENT 2 section A2.1d
#
# If a value here is ever edited without a corresponding amendment section,
# THAT IS THE SCRIPT CHOOSING and clause 2 is broken.
# ==========================================================================
REGISTRATION_GAPS = {
    "writeFormat": dict(
        value="ascii",
        fixed_by="K0d_REREGISTRATION.md AMENDMENT 2 section A2.1a",
        ruling="ascii is THE ONE SETTING UNDER WHICH EVERY REGISTERED "
               "INSTRUMENT ON THIS RUNG HAS BEEN SHOWN ABLE TO SEE.  "
               "check_k0f_mesh.py reads constant/polyMesh/{points,owner} "
               "through an ASCII regex reader and REFUSES what it cannot "
               "parse, so a binary mesh would not fail loudly -- it would "
               "SILENTLY DISARM refusal conditions A-F.  The planted-zero "
               "control (standing rule 3) must plant into a field on disk and "
               "read it back THROUGH THE SAME READER that produces the graded "
               "number, and binary cannot carry that readback through a parser "
               "this lab has neither written nor verified.  Sibling K0cS used "
               "ascii.  Disk size is not a registered constraint on this rung.",
        finding="FINDING 14 (superseded A5.13)",
        why="section 6 fixes endTime, deltaT, writeInterval and purgeWrite and "
            "fixes nothing else about writing.  The sibling K0cS uses ascii; "
            "the scratch smoke test used ascii."),
    "writePrecision": dict(
        value=16,
        fixed_by="K0d_REREGISTRATION.md AMENDMENT 2 section A2.1b",
        ruling="THE ARITHMETIC IS THE RULING, not the integer.  Section 7.1's "
               "criterion is 1e-6 of the field's range between two written "
               "checkpoints; the registered T range is 308.15-288.15 = 20.0 K, "
               "so the criterion is 2.0e-5 K.  An ASCII field at EIGHT "
               "significant digits near 300 K resolves to 300.00000 -- a "
               "last-digit quantum of ~1e-5 K, THE SAME ORDER AS THE CRITERION "
               "ITSELF -- so two successive checkpoints could differ by one "
               "quantum OF THE WRITER and the criterion could not distinguish "
               "that from convergence.  A CONVERGENCE CRITERION SITTING AT THE "
               "WRITE QUANTUM IS NOT A CRITERION.  At SIXTEEN digits the "
               "quantum is ~1e-13 K, EIGHT orders of magnitude below the "
               "criterion (2.0e-5/1e-13 = 2e8).  Sibling K0cS writes at 16.",
        finding="FINDING 14 (superseded A5.13)",
        why="LOAD-BEARING, not cosmetic.  Section 7.1's convergence criterion "
            "is 'at most 1e-6 of that field's range' between two written "
            "checkpoints; on the registered 20.0 K range that is 2e-5 K, which "
            "a coarse write precision cannot represent.  The sibling K0cS "
            "writes at 16; the scratch smoke test wrote at 8.  A criterion "
            "this rung cannot resolve is not a criterion."),
    "writeCompression": dict(
        value="off",
        fixed_by="K0d_REREGISTRATION.md AMENDMENT 2 section A2.1c",
        ruling="mark_done_k0f.py's field_path accepts T or T.gz, so the "
               "completion reader does not depend on the answer -- BUT ITS .gz "
               "BRANCH WAS NEVER EXERCISED BY ITS SELFTEST, and a reader branch "
               "not shown able to see is standing rule 3's defect class.  `off` "
               "puts every instrument on the path it has been demonstrated on.  "
               "AMENDMENT 2 section A2.1c ALSO REQUIRES, NOT OPTIONALLY, that "
               "mark_done_k0f.py's selftest exercise the .gz branch anyway: one "
               "gzipped clean case that must still PASS, and one gzipped case "
               "whose fields are older than 0/T where the age guard must still "
               "FIRE.  A branch kept alive in the code and dead in the test is "
               "a branch that will be believed the first time it is used.",
        finding="FINDING 14 (superseded A5.13)",
        why="decides whether the completion reader and the age guard of "
            "section 7.2 must find T or T.gz.  mark_done_k0f.py accepts either "
            "so it does not depend on the answer, but the BUILDER must write a "
            "controlDict that states one."),
    "domain_thickness_t": dict(
        value=0.010,
        fixed_by="K0d_REREGISTRATION.md AMENDMENT 2 section A2.1d",
        ruling="THIS BUILDER'S FINDING IS RIGHT AND IS WHY THE RULING IS OWED: "
               "A1.3a's 'cancels in every registered quantity' is true of the "
               "GRADED quantities and FALSE OF THE MESH FILE.  The case is "
               "registered 2D -- ONE CELL IN z, `empty` front and back patches "
               "-- and under that construction no graded quantity depends on t "
               "(the fields are z-invariant by construction, and Ra, Ri, Re and "
               "Re_H are every one built on the 1.040 m cavity dimension or the "
               "0.018 m slot, never on t), while the registered sampling plane "
               "z_m = t/2 is the SINGLE CELL'S CENTRE PLANE FOR ANY t and is "
               "therefore t-invariant too.  0.010 m is registered because the "
               "scratch smoke test used it and no registered quantity "
               "distinguishes it.  REGISTERED WITH THE TWO ASSERTIONS THAT MAKE "
               "IT REFUTABLE -- see assert_two_d_registration() below.  IF A "
               "GRADED NUMBER IS EVER FOUND TO MOVE WITH t, THAT IS A FINDING "
               "AGAINST THE 2D REGISTRATION, NOT AGAINST THIS RULING.",
        finding="FINDING 15 (superseded A5.13)",
        why="blockMeshDict CANNOT BE WRITTEN WITHOUT A z-EXTENT.  Re-registration "
            "A1.3a records t as unregistered and says it 'cancels in every "
            "registered quantity' -- which is true of the GRADED QUANTITIES and "
            "is not true of the mesh file.  It also fixes the registered "
            "sampling plane z_m = t/2, so the extraction dictionaries need it "
            "too.  The scratch smoke test used 0.01 m."),
}

# ==========================================================================
# REGISTERED CONSTANTS.  Every one carries the clause that fixes it.
# ==========================================================================
# --- geometry, superseded 3.1 --------------------------------------------
L = 1.040                                  # m, cavity length and height
Y_LINES = (0.000, 0.024, 1.022, 1.040)     # block splits, superseded 4
H_IN, H_OUT = 0.018, 0.024

# --- fluid state, re-registration 1.1 ------------------------------------
NU = 1.569e-05          # m2/s   -- THE re-registration's decision
PR = 0.71
PRT = 0.85              # never tuned
BETA = 3.3557047e-03    # 1/K, = 1/T_ref BY IDENTITY
TREF = 298.00           # K      -- re-registration 1.2, NOT 298.15
GRAVITY = (0.0, -9.81, 0.0)

# --- thermal boundary values in KELVIN, superseded A5.2 ------------------
T_COLD = 288.15         # 15 C: inlet, ceiling, leftWall, rightWall
T_FLOOR = 308.15        # 35 C
T_FLOOR_BHI = 308.65    # 35.5 C, B_hi only (superseded 3.3)
U_IN = 0.57

# --- inlet turbulence, superseded 3.2 and A4.3 ---------------------------
K_IN, EPS_IN, OMEGA_IN, NUT_IN = 1.25e-03, 5.76e-03, 51.2, 2.4414e-05
K_IN_IHI, EPS_IN_IHI, NUT_IN_IHI = 5.00e-03, 2.304e-02, 9.7656e-05
# I_hi's inlet omega is 51.2 EXACTLY, the same as M1_*: scaling k and eps by
# the same factor leaves omega = eps/(Cmu k) unchanged (A4.3, A4.4).
OMEGA_IN_IHI = 51.2

# --- controlDict timings, superseded 6 -----------------------------------
END_TIME, DELTA_T, WRITE_INTERVAL, PURGE_WRITE = 40000, 1, 4000, 2

# --- RANKS, ASSERTED AND NOT ASSUMED -------------------------------------
# Re-registration section 6: "Serial.  nProcs = 1.  No decomposition, on all
# nine cases.  ...  There is no partitioner, therefore there is no seed and no
# partition-dependence to record."  A1.2b's tenth case is L2 serial like the
# rest.
#
# A CAP ENFORCED AS A WALL-CLOCK timeout IS NOT A CORE-MINUTE CAP UNLESS IT IS
# CONVERTED:   timeout_s = cap_core_min * 60 / ranks   (re-registration 8.1).
# For K0d the conversion is the IDENTITY because ranks == 1 -- which is exactly
# why it is asserted here rather than assumed.  A later rung that decomposes
# would silently inherit a timeout 1/ranks too long if this were left implicit.
RANKS = 1


def _require(cond, msg):
    """A refusal that SURVIVES `python3 -O`.

    NO `assert` IN THIS INSTRUMENT MAY CARRY A REFUSAL, GUARD, CONTROL OR GATE.
    `assert` statements are REMOVED by `python3 -O` / PYTHONOPTIMIZE=1, so a
    guard written as an assert is not a guard under every interpreter this
    script can be launched with.  MEASURED ON THIS BOX, not relayed:

        python3     ranks=4 -> REFUSED: K0d is registered SERIAL
        python3 -O  ranks=4 -> proceeded

    A registration guard that evaporates under an interpreter flag would have
    let a NON-SERIAL run proceed unregistered, with every core-minute figure in
    the cost model wrong -- `timeout = cap * 60 / ranks` is the identity ONLY at
    ranks == 1.  This raises instead, and `raise` is not optimised away."""
    if not cond:
        raise SystemExit(f"REFUSE: {msg}")


_require(RANKS == 1,
         "K0d is registered SERIAL (re-registration section 6). The "
         "core-minute -> timeout conversion below is the identity ONLY at "
         "ranks == 1.")

# Per-case hard stop: 10x that case's registered POINT line (re-registration
# 8.1 rule 2).  UNDER SANAA'S 2026-08-25 DIRECTIVE THESE ARE RUNAWAY GUARDS,
# NOT BUDGET GATES: a case reaching its cap is REPORTED to the supervisor, who
# decides whether to extend by dated amendment or stop it as genuinely stuck,
# diverging or looping.  Reaching a cap is no longer an automatic kill.  The
# CONVERSION, however, is unchanged -- a guard set in the wrong units is not a
# guard.
CAP_CORE_MIN = {
    "M1_c": 435.00, "M2_c": 435.00,
    "M1_m": 852.70, "M2_m": 852.70, "B_hi": 852.70, "I_hi": 852.70,
    "M1_m_seed": 852.70,          # an L2 kOmegaSST case: M1_m's line exactly
    "M1_f": 1675.50, "M2_f": 1675.50,
    "C_lam": 639.50,
}
# The frozen section 8.1 table registers 51 161 s for the L2 row where
# 852.70 * 60 / 1 = 51 162 s.  The frozen figure is ONE SECOND LOW (0.002 %).
# It is a rounding artefact, it binds TIGHTER than the rule so it cannot
# license an overrun, and IT IS LEFT EXACTLY AS FROZEN (standing rule 6).
# timeout_for() reproduces the frozen table, not the recomputed value.
FROZEN_TIMEOUT_S = {435.00: 26100, 852.70: 51161, 1675.50: 100530, 639.50: 38370}


def timeout_for(case):
    """The enforced wall-clock timeout of one case, in seconds.

    cap_core_min * 60 / ranks, with ranks REQUIRED rather than assumed --
    via _require(), which survives `python3 -O`, never via assert."""
    _require(RANKS == 1, "ranks != 1; the core-minute -> timeout conversion "
                         "is not the identity and this refuses rather than "
                         "emitting a timeout 1/ranks too long")
    cap = CAP_CORE_MIN[case]
    computed = cap * 60.0 / RANKS
    frozen = FROZEN_TIMEOUT_S[cap]
    return frozen, computed

# --- patches, superseded A5.2 --------------------------------------------
WALLS = ("floor", "ceiling", "leftWall", "rightWall")

# --- the mesh family, superseded 4 + re-registration 5.1 -----------------
LEVELS = {
    "L1": dict(Nx=160, nA=12, nB=138, nC=10, cells=25600, first_cell=1.101053e-03),
    "L2": dict(Nx=224, nA=18, nB=192, nC=14, cells=50176, first_cell=7.864662e-04),
    "L3": dict(Nx=314, nA=24, nB=270, nC=20, cells=98596, first_cell=5.610459e-04),
}

# --- the ten cases, re-registration 5.2 + AMENDMENT 1 A1.2b --------------
CASES = {
    "M1_c":      dict(closure="kOmegaSST",   level="L1"),
    "M1_m":      dict(closure="kOmegaSST",   level="L2"),
    "M1_f":      dict(closure="kOmegaSST",   level="L3"),
    "M2_c":      dict(closure="RNGkEpsilon", level="L1"),
    "M2_m":      dict(closure="RNGkEpsilon", level="L2"),
    "M2_f":      dict(closure="RNGkEpsilon", level="L3"),
    "C_lam":     dict(closure="laminar",     level="L2"),
    "B_hi":      dict(closure="kOmegaSST",   level="L2", floor_T=T_FLOOR_BHI),
    "I_hi":      dict(closure="kOmegaSST",   level="L2", inlet_turb="x4"),
    "M1_m_seed": dict(closure="kOmegaSST",   level="L2", seed_T=308.15),
}

# --- THE REGISTERED SEED, PER CLOSURE.  Re-registration AMENDMENT 1 A1.2a.
# "A case whose closure does not appear above HAS NO REGISTERED SEED, and
#  build_k0f.py REFUSES (exit 2) rather than infer one."
SEED = {
    "kOmegaSST":   {"T": 288.15, "U": "(0 0 0)", "p_rgh": 0.0,
                    "k": 1.25e-03, "omega": 51.2, "nut": 0.0, "alphat": 0.0},
    "RNGkEpsilon": {"T": 288.15, "U": "(0 0 0)", "p_rgh": 0.0,
                    "k": 1.25e-03, "epsilon": 5.76e-03, "nut": 0.0, "alphat": 0.0},
    "laminar":     {"T": 288.15, "U": "(0 0 0)", "p_rgh": 0.0, "alphat": 0.0},
}

# --- the extraction, re-registration AMENDMENT 1 A1.3a -------------------
SAMPLE_N_POINTS = 2081                   # spacing exactly 5.000e-04 m
SAMPLE_SET_FORMAT = "raw"
SAMPLE_SCHEME_GRADED = "cellPoint"
SAMPLE_SCHEME_CONTROL = "cell"           # the dual-scheme control, A1.3b
VERTICAL_X, HORIZONTAL_Y = 0.52, 0.52

# --- fvSchemes, superseded A5.3, byte-equivalent to four sibling files ---
FV_SCHEMES = """ddtSchemes
{
    default         steadyState;
}
gradSchemes
{
    default         Gauss linear;
}
divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind grad(U);
    div(phi,T)      bounded Gauss limitedLinear 1;
    div(phi,k)      bounded Gauss limitedLinear 1;
    div(phi,omega)  bounded Gauss limitedLinear 1;
    div(phi,epsilon) bounded Gauss limitedLinear 1;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes
{
    default         Gauss linear corrected;
}
interpolationSchemes
{
    default         linear;
}
snGradSchemes
{
    default         corrected;
}
wallDist
{
    method          meshWave;
}
"""

# --- fvSolution, superseded A5.4.  residualControl DELIBERATELY ABSENT ---
FV_SOLUTION = """solvers
{
    "(p_rgh|p_rghFinal)"
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-10;
        relTol          0.01;
    }
    "(U|T|k|omega|epsilon)(Final)?"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-12;
        relTol          0.01;
    }
}
SIMPLE
{
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}
relaxationFactors
{
    fields
    {
        p_rgh           0.7;
    }
    equations
    {
        U               0.4;
        T               0.6;
        "(k|omega|epsilon)" 0.4;
    }
}
"""


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def unresolved_gaps():
    return [k for k, v in REGISTRATION_GAPS.items() if v["value"] is None]


def gap_report():
    out = ["THE FROZEN REGISTRATION DOES NOT FIX THE FOLLOWING INPUTS, AND",
           "A5.11 CLAUSE 2 FORBIDS THIS SCRIPT CHOOSING ANY OF THEM.",
           ""]
    for k in unresolved_gaps():
        g = REGISTRATION_GAPS[k]
        out.append(f"  {k}   [{g['finding']}]")
        for line in g["why"].split(". "):
            if line.strip():
                out.append(f"      {line.strip().rstrip('.')}.")
        out.append("")
    out.append("Each is resolved by a dated amendment while the pre-compute")
    out.append("window is open, not by this script and not by an operator flag.")
    return "\n".join(out)


# ==========================================================================
# the registered seed, applied per closure, with the registered refusal
# ==========================================================================
def registered_seed(case):
    spec = CASES.get(case)
    if spec is None:
        refuse(f"{case!r} is not one of the ten registered K0d cases")
    closure = spec["closure"]
    seed = SEED.get(closure)
    if seed is None:
        refuse(f"closure {closure!r} of case {case!r} HAS NO REGISTERED SEED. "
               f"Refusing rather than inferring one (re-registration A1.2a, "
               f"binding on build_k0f.py).")
    seed = dict(seed)
    if "seed_T" in spec:
        # M1_m_seed: identical to M1_m in every respect EXCEPT T's
        # internalField, which is a HOT START at the floor temperature.
        seed["T"] = spec["seed_T"]
    return closure, seed


# ==========================================================================
# mesh: two-sided geometric grading, the reciprocal WRITTEN OUT BY HAND
# ==========================================================================
def expansion_for(first_cell, half_length, m_cells):
    """blockMesh expansion (last/first cell) over a half with m cells whose
    first cell is `first_cell`.  Bisection on the geometric ratio."""
    if m_cells <= 1:
        return 1.0
    lo, hi = 1.0 + 1e-14, 10.0
    for _ in range(300):
        r = 0.5 * (lo + hi)
        s = first_cell * (r ** m_cells - 1.0) / (r - 1.0)
        if s > half_length:
            hi = r
        else:
            lo = r
    r = 0.5 * (lo + hi)
    return r ** (m_cells - 1)


def grading_pair(first_cell, length, n_cells):
    """Return the multi-grading string for a two-sided direction.

    The reciprocal of the second half is WRITTEN OUT AS A LITERAL rather than
    as 1/E -- the K0cS form, L-142.  T1b attempt 1 lost 57 core-hours to a
    grading direction nobody read from disk, and a hand-written reciprocal is
    the form check_k0f_mesh.py condition D can catch when it is wrong."""
    m = max(n_cells // 2, 1)
    e = expansion_for(first_cell, 0.5 * length, m)
    return f"( (0.5 0.5 {e:.10g}) (0.5 0.5 {1.0 / e:.10g}) )"


def blockmesh_dict(level, thickness):
    s = LEVELS[level]
    y0, y1, y2, y3 = Y_LINES
    t = thickness
    verts = []
    for z in (0.0, t):
        for y in (y0, y1, y2, y3):
            for x in (0.0, L):
                verts.append((x, y, z))
    # index(i, j, k) = k*8 + j*2 + i
    def v(i, j, k):
        return k * 8 + j * 2 + i
    blocks = []
    for blk, (jlo, n) in (("A", (0, s["nA"])), ("B", (1, s["nB"])), ("C", (2, s["nC"]))):
        hexa = (v(0, jlo, 0), v(1, jlo, 0), v(1, jlo + 1, 0), v(0, jlo + 1, 0),
                v(0, jlo, 1), v(1, jlo, 1), v(1, jlo + 1, 1), v(0, jlo + 1, 1))
        gy = grading_pair(s["first_cell"], Y_LINES[jlo + 1] - Y_LINES[jlo], n)
        gx = grading_pair(s["first_cell"], L, s["Nx"])
        blocks.append("    hex (%s) (%d %d 1)\n    simpleGrading (%s %s 1)"
                      % (" ".join(str(h) for h in hexa), s["Nx"], n, gx, gy))
    faces = dict(
        inlet=[(v(0, 2, 0), v(0, 2, 1), v(0, 3, 1), v(0, 3, 0))],
        outlet=[(v(1, 0, 0), v(1, 1, 0), v(1, 1, 1), v(1, 0, 1))],
        floor=[(v(0, 0, 0), v(1, 0, 0), v(1, 0, 1), v(0, 0, 1))],
        ceiling=[(v(0, 3, 0), v(0, 3, 1), v(1, 3, 1), v(1, 3, 0))],
        leftWall=[(v(0, 0, 0), v(0, 0, 1), v(0, 1, 1), v(0, 1, 0)),
                  (v(0, 1, 0), v(0, 1, 1), v(0, 2, 1), v(0, 2, 0))],
        rightWall=[(v(1, 1, 0), v(1, 2, 0), v(1, 2, 1), v(1, 1, 1)),
                   (v(1, 2, 0), v(1, 3, 0), v(1, 3, 1), v(1, 2, 1))],
        frontAndBack=[(v(0, j, k), v(0, j + 1, k), v(1, j + 1, k), v(1, j, k))
                      for j in range(3) for k in (0, 1)],
    )
    types = dict(inlet="patch", outlet="patch", floor="wall", ceiling="wall",
                 leftWall="wall", rightWall="wall", frontAndBack="empty")
    bnd = []
    for name in ("inlet", "outlet", "floor", "ceiling", "leftWall",
                 "rightWall", "frontAndBack"):
        f = "\n".join("            (%s)" % " ".join(str(i) for i in q)
                      for q in faces[name])
        bnd.append("    %s\n    {\n        type %s;\n        faces\n        (\n%s\n        );\n    }"
                   % (name, types[name], f))
    return ("scale   1;\n\nvertices\n(\n"
            + "\n".join("    (%.9g %.9g %.9g)" % p for p in verts)
            + "\n);\n\nblocks\n(\n" + "\n".join(blocks)
            + "\n);\n\nedges\n(\n);\n\nboundary\n(\n"
            + "\n".join(bnd) + "\n);\n\nmergePatchPairs\n(\n);\n")


# ==========================================================================
# 0/ field files -- superseded A5.5, per closure
# ==========================================================================
def _fmt(v):
    """Format a field value as OpenFOAM requires.

    REPAIRED 2026-08-25, SECOND MEASURED FAILURE OF THE SAME CLASS.  This used
    to be `return v if isinstance(v, str) else ...`, which passed a STRING
    THROUGH RAW.  The registered kOmegaSST / RNGkEpsilon / laminar seeds carry
    U as the string "(0 0 0)", so 0/U went out as

        internalField   (0 0 0);

    with NO `uniform` keyword, and the solver refused every case with

        --> FOAM FATAL IO ERROR: Expected keyword 'uniform' or 'nonuniform',
            found on line 9: punctuation '('   (file: 0/U/internalField)

    The BOUNDARY entries were unaffected because they spell "uniform (...)"
    out in full -- so, exactly as with the missing FoamFile headers, one half
    of the file was right and the broken half had nothing checking it.

    A string that ALREADY declares uniform/nonuniform is passed through; a bare
    literal gets the keyword it needs.

    THE FIRST VERSION OF THIS REPAIR WAS ITSELF WRONG, and the solver arm below
    caught it rather than a launch: the registered wall entries carry the
    OpenFOAM MACRO string "$internalField", which already expands to
    `uniform <value>`.  Prepending the keyword produced

        value           uniform $internalField;   ->   uniform uniform 0.00125

    and the solver refused 0/k with "Wrong token type - expected scalar value,
    found word 'uniform'".  A `$` macro is therefore passed through with the
    other two forms.  Recorded rather than quietly corrected, because it is the
    same failure mode twice in one function: assuming what a string means
    instead of checking what OpenFOAM does with it."""
    if not isinstance(v, str):
        return f"uniform {v:.10g}"
    s = v.strip()
    if s.startswith("uniform") or s.startswith("nonuniform") or s.startswith("$"):
        return s
    return f"uniform {s}"


def field_file(name, dims, internal, boundary):
    body = ["FoamFile\n{\n    version 2.0;\n    format ascii;\n    class %s;\n"
            "    object %s;\n}\n" % ("volVectorField" if name == "U"
                                     else "volScalarField", name),
            "dimensions      %s;\n" % dims,
            "internalField   %s;\n\nboundaryField\n{\n" % _fmt(internal)]
    for patch, entry in boundary:
        body.append("    %s\n    {\n%s    }\n" % (patch, entry))
    body.append("}\n")
    return "".join(body)


def _e(typ, value=None):
    s = f"        type            {typ};\n"
    if value is not None:
        s += f"        value           {_fmt(value)};\n"
    return s


def zero_dir(case):
    """Every 0/ field of one case, from superseded A5.5 and the registered
    seed of A1.2a.  The internalField is the SEED; the patch entries are the
    registered boundary types and values."""
    spec = CASES[case]
    closure, seed = registered_seed(case)
    floor_T = spec.get("floor_T", T_FLOOR)
    ihi = spec.get("inlet_turb") == "x4"
    out = {}

    out["U"] = field_file("U", "[0 1 -1 0 0 0 0]", seed["U"], [
        ("inlet", _e("fixedValue", "uniform (%.10g 0 0)" % U_IN)),
        ("outlet", _e("zeroGradient")),
        ('"(floor|ceiling|leftWall|rightWall)"', _e("noSlip")),
        ("frontAndBack", _e("empty"))])

    out["T"] = field_file("T", "[0 0 0 1 0 0 0]", seed["T"], [
        ("inlet", _e("fixedValue", T_COLD)),
        ("outlet", _e("zeroGradient")),
        ("floor", _e("fixedValue", floor_T)),
        ('"(ceiling|leftWall|rightWall)"', _e("fixedValue", T_COLD)),
        ("frontAndBack", _e("empty"))])

    out["p_rgh"] = field_file("p_rgh", "[0 2 -2 0 0 0 0]", seed["p_rgh"], [
        ("inlet", _e("fixedFluxPressure", 0.0)),
        ("outlet", _e("fixedValue", 0.0)),
        ('"(floor|ceiling|leftWall|rightWall)"', _e("fixedFluxPressure", 0.0)),
        ("frontAndBack", _e("empty"))])

    out["alphat"] = field_file("alphat", "[0 2 -1 0 0 0 0]", seed["alphat"], [
        ("inlet", _e("calculated", 0.0)),
        ("outlet", _e("calculated", 0.0)),
        ('"(floor|ceiling|leftWall|rightWall)"', _e("calculated", 0.0)),
        ("frontAndBack", _e("empty"))])

    if closure == "kOmegaSST":
        out["k"] = field_file("k", "[0 2 -2 0 0 0 0]", seed["k"], [
            ("inlet", _e("fixedValue", K_IN_IHI if ihi else K_IN)),
            ("outlet", _e("zeroGradient")),
            ('"(floor|ceiling|leftWall|rightWall)"',
             _e("kLowReWallFunction", "$internalField")),
            ("frontAndBack", _e("empty"))])
        out["omega"] = field_file("omega", "[0 0 -1 0 0 0 0]", seed["omega"], [
            ("inlet", _e("fixedValue", OMEGA_IN_IHI if ihi else OMEGA_IN)),
            ("outlet", _e("zeroGradient")),
            ('"(floor|ceiling|leftWall|rightWall)"',
             _e("omegaWallFunction", "$internalField")),
            ("frontAndBack", _e("empty"))])
        out["nut"] = field_file("nut", "[0 2 -1 0 0 0 0]", seed["nut"], [
            ("inlet", _e("calculated", NUT_IN_IHI if ihi else NUT_IN)),
            ("outlet", _e("calculated", 0.0)),
            ('"(floor|ceiling|leftWall|rightWall)"',
             _e("nutLowReWallFunction", 0.0)),
            ("frontAndBack", _e("empty"))])
    elif closure == "RNGkEpsilon":
        out["k"] = field_file("k", "[0 2 -2 0 0 0 0]", seed["k"], [
            ("inlet", _e("fixedValue", K_IN)),
            ("outlet", _e("zeroGradient")),
            ('"(floor|ceiling|leftWall|rightWall)"',
             _e("kqRWallFunction", "$internalField")),
            ("frontAndBack", _e("empty"))])
        out["epsilon"] = field_file("epsilon", "[0 2 -3 0 0 0 0]",
                                    seed["epsilon"], [
            ("inlet", _e("fixedValue", EPS_IN)),
            ("outlet", _e("zeroGradient")),
            ('"(floor|ceiling|leftWall|rightWall)"',
             _e("epsilonWallFunction", "$internalField")),
            ("frontAndBack", _e("empty"))])
        out["nut"] = field_file("nut", "[0 2 -1 0 0 0 0]", seed["nut"], [
            ("inlet", _e("calculated", NUT_IN)),
            ("outlet", _e("calculated", 0.0)),
            ('"(floor|ceiling|leftWall|rightWall)"', _e("nutkWallFunction", 0.0)),
            ("frontAndBack", _e("empty"))])
    # laminar: exactly T, U, p_rgh, alphat -- A5.5.4, no wider
    return out


def constant_dir(case):
    closure = CASES[case]["closure"]
    tp = ("transportModel  Newtonian;\n"
          f"nu              {NU:.10g};\n"
          f"Pr              {PR:.10g};\n"
          f"Prt             {PRT:.10g};\n"
          f"beta            {BETA:.10g};\n"
          f"TRef            {TREF:.10g};\n")
    if closure == "laminar":
        turb = "simulationType  laminar;\n"
    else:
        turb = ("simulationType  RAS;\n\nRAS\n{\n"
                f"    RASModel        {closure};\n"
                "    turbulence      on;\n    printCoeffs     on;\n}\n")
    g = ("dimensions      [0 1 -2 0 0 0 0];\nvalue           (%.10g %.10g %.10g);\n"
         % GRAVITY)
    return {"transportProperties": tp, "turbulenceProperties": turb, "g": g}


def system_dir(case, thickness, gaps):
    s = LEVELS[CASES[case]["level"]]
    cd = ("application     buoyantBoussinesqSimpleFoam;\nstartFrom       startTime;\n"
          "startTime       0;\nstopAt          endTime;\n"
          f"endTime         {END_TIME};\ndeltaT          {DELTA_T};\n"
          "writeControl    timeStep;\n"
          f"writeInterval   {WRITE_INTERVAL};\npurgeWrite      {PURGE_WRITE};\n"
          f"writeFormat     {gaps['writeFormat']};\n"
          f"writePrecision  {gaps['writePrecision']};\n"
          f"writeCompression {gaps['writeCompression']};\n"
          "timeFormat      general;\ntimePrecision   6;\nrunTimeModifiable false;\n")
    zm = 0.5 * thickness
    def sample(scheme):
        return (f"setFormat       {SAMPLE_SET_FORMAT};\n"
                f"interpolationScheme {scheme};\n"
                "fields          ( T U k );\n\nsets\n(\n"
                "    vertical_midplane\n    {\n        type    uniform;\n"
                "        axis    distance;\n"
                f"        start   ({VERTICAL_X:.10g} 0 {zm:.10g});\n"
                f"        end     ({VERTICAL_X:.10g} {L:.10g} {zm:.10g});\n"
                f"        nPoints {SAMPLE_N_POINTS};\n    }}\n"
                "    horizontal_midplane\n    {\n        type    uniform;\n"
                "        axis    distance;\n"
                f"        start   (0 {HORIZONTAL_Y:.10g} {zm:.10g});\n"
                f"        end     ({L:.10g} {HORIZONTAL_Y:.10g} {zm:.10g});\n"
                f"        nPoints {SAMPLE_N_POINTS};\n    }}\n);\n")
    return {"controlDict": cd, "fvSchemes": FV_SCHEMES, "fvSolution": FV_SOLUTION,
            "blockMeshDict": blockmesh_dict(CASES[case]["level"], thickness),
            "sampleDict.graded": sample(SAMPLE_SCHEME_GRADED),
            "sampleDict.control": sample(SAMPLE_SCHEME_CONTROL)}


def assert_two_d_registration(d, thickness):
    """THE TWO ASSERTIONS THAT MAKE RULING 4 REFUTABLE (AMENDMENT 2 A2.1d).

    domain_thickness_t = 0.010 m is registered on the claim that NO GRADED
    QUANTITY DEPENDS ON t, which holds ONLY under the registered 2D
    construction.  A claim of invariance that nothing can contradict is not a
    claim, so the construction is ASSERTED HERE, READ BACK FROM WHAT WAS
    ACTUALLY WRITTEN TO DISK -- not from the variables that wrote it.

      A1  exactly ONE cell in z, and `empty` front and back patches, on every
          block of every case;
      A2  every sampling z in both extraction dictionaries equals that single
          cell's CENTRE PLANE, t/2.

    If a graded number is ever found to move with t, THAT IS A FINDING AGAINST
    THE 2D REGISTRATION, not against the ruling -- and these assertions are
    what make such a finding possible instead of invisible.
    """
    bm = open(os.path.join(d, "system", "blockMeshDict")).read()

    # --- A1a: every hex block is (Nx n 1) -- exactly one cell in z ----------
    zc = re.findall(r"hex\s*\([^)]*\)\s*\(\s*\d+\s+\d+\s+(\d+)\s*\)", bm)
    if not zc:
        refuse(f"{d}: no hex block cell counts could be read back from the "
               f"blockMeshDict that was just written")
    if len(zc) != 3:
        refuse(f"{d}: read back {len(zc)} hex blocks, expected 3")
    if any(int(n) != 1 for n in zc):
        refuse(f"{d}: A1 VIOLATED -- z cell counts {zc} are not all 1.  The 2D "
               f"registration that makes domain_thickness_t irrelevant to every "
               f"graded quantity DOES NOT HOLD (AMENDMENT 2 A2.1d).")

    # --- A1b: frontAndBack is an `empty` patch -----------------------------
    m = re.search(r"frontAndBack\s*\{\s*type\s+(\w+)\s*;", bm)
    if not m or m.group(1) != "empty":
        refuse(f"{d}: A1 VIOLATED -- frontAndBack patch type is "
               f"{m.group(1) if m else 'UNREADABLE'}, not `empty`.  Without an "
               f"empty front/back the case is not 2D and t enters the physics "
               f"(AMENDMENT 2 A2.1d).")

    # --- A1c: the two z planes are exactly 0 and t -------------------------
    zs = sorted({float(z) for _, _, z in
                 re.findall(r"\(\s*([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+"
                            r"([-0-9.eE+]+)\s*\)", bm.split("blocks")[0])})
    if len(zs) != 2 or abs(zs[0]) > 1e-12 or abs(zs[1] - thickness) > 1e-12:
        refuse(f"{d}: A1 VIOLATED -- vertex z planes read back as {zs}, "
               f"expected exactly [0.0, {thickness}]")

    # --- A2: sampling z == the single cell's CENTRE PLANE, t/2 -------------
    z_centre = 0.5 * thickness
    for which in ("graded", "control"):
        sd = open(os.path.join(d, "system", f"sampleDict.{which}")).read()
        zsamp = [float(z) for _, _, z in
                 re.findall(r"\(\s*([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+"
                            r"([-0-9.eE+]+)\s*\)", sd)]
        if len(zsamp) != 4:
            refuse(f"{d}: sampleDict.{which} -- read back {len(zsamp)} sample "
                   f"endpoints, expected 4 (two sets x start/end)")
        bad = [z for z in zsamp if abs(z - z_centre) > 1e-12]
        if bad:
            refuse(f"{d}: A2 VIOLATED -- sampleDict.{which} samples at z={bad}, "
                   f"not at the single cell's centre plane t/2 = {z_centre}.  "
                   f"The registered sampling plane is t-invariant ONLY at the "
                   f"cell centre (AMENDMENT 2 A2.1d).")
    return True


# ==========================================================================
# THE FoamFile HEADER.  ADDED 2026-08-25 AFTER A MEASURED FAILURE.
#
# THE DEFECT: this builder wrote every system/ and constant/ dictionary with NO
# FoamFile header.  OpenFOAM REQUIRES one on every dictionary it reads, so
# blockMesh REFUSED ALL TEN CASES with
#
#     --> FOAM FATAL IO ERROR: problem while reading header for object
#         controlDict   (file: system/controlDict at line 1)
#
# and the rung could not mesh, let alone solve.  field_file() already emitted a
# header for the 0/ fields, so the FIELDS were readable and the DICTIONARIES
# were not -- which is why nothing in this script noticed.
#
# WHY THE SELFTEST DID NOT CATCH IT, and this is the same lesson AMENDMENT 2
# section A2.3 records one layer up: EVERY CHECK EXERCISED THE WRONG CHANNEL.
# The selftest asserted the dictionaries' CONTENT -- that controlDict carries
# endTime 40000, that blockMeshDict has three hex blocks and seven patches --
# and it read those assertions back from the strings this script had just
# written.  IT NEVER ASKED THE ONE PROGRAM THAT HAS TO READ THEM WHETHER IT
# COULD.  A green selftest is not a green instrument.
#
# THE REPAIR IS AT THE SINGLE WRITE POINT, so no dictionary can be added later
# that misses it, and a body that already carries a header is left alone.
FOAM_CLASS = {"g": "uniformDimensionedVectorField"}


def foam_header(obj, location):
    """The FoamFile header OpenFOAM requires on every dictionary it reads."""
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            f"    class       {FOAM_CLASS.get(obj, 'dictionary')};\n"
            f"    location    \"{location}\";\n    object      {obj};\n}}\n\n")


def with_header(name, body, location):
    """Prepend the header unless the body already carries one.

    0/ field bodies come from field_file(), which emits its own header; those
    are passed through untouched rather than double-headed."""
    if body.lstrip().startswith("FoamFile"):
        return body
    return foam_header(name, location) + body


# --------------------------------------------------------------------------
# THE CONSUMER-SIDE COMPLETENESS ASSERTION (K0f section 3A).
#
# THE DEFECT CLASS THIS CLOSES.  A launcher elsewhere in the lab hashed the
# field directory it had staged and re-asserted that manifest faithfully before
# all 23 stages, PASSING EVERY TIME -- while four fields were staged and eleven
# were needed, and every stage died on `cannot find file 0/nut`.  Internally
# perfect, externally false.  A comparator-side md5 of the same directory would
# not have caught it either: BOTH READERS AGREE ON THE SAME WRONG FILES.
#
# The assertion below is against WHAT THE CONSUMER DEMANDS -- the fields the
# SOLVER will look for -- never against a hash of what the producer wrote.
#
# AND THE ENUMERATION IS NOT TRIVIAL, WHICH IS WHY IT IS SPECIFIED RATHER THAN
# LEFT TO AN IMPLEMENTER.  `fvSolution`'s registered solver regex is
# "(U|T|k|omega|epsilon)(Final)?" and its relaxation regex is "(k|omega|epsilon)"
# -- BOTH NAME `omega` AND `epsilon`, because one dictionary serves all three
# closures.  A NAIVE ENUMERATION FROM `fvSolution` ALONE WOULD DEMAND `epsilon`
# OF A kOmegaSST CASE AND REFUSE A CORRECT RUN.  The required set is therefore
# the INTERSECTION of the dictionary's names with the closure declared in
# `constant/turbulenceProperties`, reconciled against the registered
# per-closure completion table.  `phi` is EXCLUDED: the solver generates it, it
# is never staged in `0/`, and that is why `0/` correctly holds seven files
# where the completion set names eight.
#
# IT RUNS BEFORE THE SOLVER STARTS.  Under a detached queue there is nobody to
# diagnose a crash, so a pre-flight refusal is worth far more than a post-hoc
# one.
# --------------------------------------------------------------------------

# The registered per-closure completion field set (re-registration section 7.2),
# carried here so the reconciliation has something to reconcile AGAINST.
COMPLETION_FIELDS = {
    "kOmegaSST":   ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi"),
    "RNGkEpsilon": ("T", "U", "p_rgh", "alphat", "nut", "k", "epsilon", "phi"),
    "laminar":     ("T", "U", "p_rgh", "alphat", "phi"),
}
SOLVER_GENERATED = ("phi",)
# THE FIELDS THAT CARRY A TRANSPORT EQUATION, and therefore the ONLY ones that
# may be cross-checked against `fvSolution`.
#
# A FINDING AGAINST THIS FUNCTION'S OWN FIRST DRAFT, RECORDED RATHER THAN
# QUIETLY CORRECTED.  This tuple first read ("k", "omega", "epsilon", "nut"),
# and the assertion then REFUSED every correct turbulent case with "the
# registered completion set names 'nut' but system/fvSolution never mentions
# it".  IT WAS RIGHT TO REFUSE AND THE ENUMERATION WAS WRONG: `nut` and
# `alphat` are CALCULATED fields -- staged in `0/` because the solver reads
# them, never solved, so `fvSolution` correctly has no entry for either.  This
# is section 3A's own warning arriving from the opposite direction: the naive
# enumeration demands `epsilon` of a kOmegaSST case; the over-eager
# reconciliation demands an `fvSolution` entry for a field that has no
# equation.  BOTH ARE THE SAME MISTAKE -- reading one dictionary as though it
# described the whole consumer.  The defect was caught by DRIVING the
# assertion on all three closures BEFORE any launch, which is the only reason
# it is a footnote here instead of a refused batch in a detached queue.
SOLVED_CLOSURE_VARIABLES = ("k", "omega", "epsilon")
CALCULATED_FIELDS = ("nut", "alphat")


def declared_closure(case_dir):
    """The closure the SOLVER will read, from constant/turbulenceProperties.

    Read from the file on disk, never from this script's CASES table: the
    table describes what was meant to be written and the file is what the
    solver will actually consume.  Those are the two channels whose divergence
    is this whole section's subject.
    """
    p = os.path.join(case_dir, "constant", "turbulenceProperties")
    if not os.path.isfile(p):
        return None, f"{p}: absent, so the closure cannot be read"
    txt = open(p).read()
    if re.search(r"\bsimulationType\s+laminar\s*;", txt):
        return "laminar", "simulationType laminar"
    m = re.search(r"\bRASModel\s+(\w+)\s*;", txt)
    if not m:
        return None, f"{p}: neither `simulationType laminar` nor `RASModel`"
    return m.group(1), f"RASModel {m.group(1)}"


def fvsolution_names(case_dir):
    """Every field name `system/fvSolution` mentions, from BOTH its solver and
    its relaxation entries.  This is the OVER-SET -- it names all three
    closures' variables at once -- and is intersected, never used raw."""
    p = os.path.join(case_dir, "system", "fvSolution")
    if not os.path.isfile(p):
        return None, f"{p}: absent"
    txt = open(p).read()
    names = set()
    for m in re.finditer(r'"\(([^)]*)\)(?:\(Final\)\?)?"', txt):
        for part in m.group(1).split("|"):
            part = part.strip()
            if part and not part.endswith("Final"):
                names.add(part)
    for m in re.finditer(r"^\s{8,}(\w+)\s+[0-9.]+\s*;", txt, re.M):
        names.add(m.group(1))
    return names, "read"


def required_zero_fields(case_dir):
    """The field set the SOLVER REQUIRES in `0/`, and the derivation with it.

    (a) the closure is READ FROM `constant/turbulenceProperties`;
    (b) `system/fvSolution`'s names are the over-set;
    (c) the required set is the registered completion set for THAT closure,
        MINUS the solver-generated fields;
    (d) the two are RECONCILED: a closure variable that fvSolution does not
        name, or a required field fvSolution names for a different closure,
        is a finding and REFUSES.
    """
    closure, how = declared_closure(case_dir)
    if closure is None:
        return None, closure, how
    if closure not in COMPLETION_FIELDS:
        return None, closure, (
            f"closure {closure!r} has NO REGISTERED COMPLETION FIELD SET. "
            f"Re-registration section 7.2: no exemption and no field "
            f"substitution may be inferred at grading time, and none is "
            f"inferred at launch time either.")
    names, note = fvsolution_names(case_dir)
    if names is None:
        return None, closure, note
    required = [f for f in COMPLETION_FIELDS[closure]
                if f not in SOLVER_GENERATED]
    # (d) the reconciliation, in the direction that can actually bite
    for f in required:
        if f in SOLVED_CLOSURE_VARIABLES and f not in names:
            return None, closure, (
                f"the registered completion set for {closure} names {f!r} but "
                f"system/fvSolution never mentions it, so the solver would "
                f"have no entry for a field this rung grades.  Refusing "
                f"rather than launching on a dictionary that disagrees with "
                f"the registration.")
    return required, closure, f"{how}; fvSolution names {sorted(names)}"


def assert_zero_complete(case_dir, verbose=True):
    """REFUSE (exit 2) if any field the solver requires is absent from `0/`."""
    required, closure, note = required_zero_fields(case_dir)
    if required is None:
        refuse(f"{case_dir}: the required field set could not be enumerated. "
               f"{note}")
    zdir = os.path.join(case_dir, "0")
    if not os.path.isdir(zdir):
        refuse(f"{case_dir}: no 0/ directory, so no field is staged at all")
    missing = [f for f in required
               if not (os.path.isfile(os.path.join(zdir, f))
                       or os.path.isfile(os.path.join(zdir, f + ".gz")))]
    if missing:
        refuse(f"{case_dir}: 0/ is MISSING {missing}, which the solver "
               f"REQUIRES for closure {closure!r}.  The assertion is against "
               f"what the CONSUMER demands, not against a hash of what the "
               f"producer wrote -- a hash of the wrong files agrees with "
               f"itself.  Refusing to launch.")
    if verbose:
        print(f"  PRE-FLIGHT OK  {os.path.basename(case_dir)}: closure "
              f"{closure}, requires {required}, all present in 0/")
    return required, closure


def write_case(root, case, gaps):
    d = os.path.join(root, case)
    if os.path.exists(d):
        refuse(f"{d} already exists.  The builder refuses a case directory "
               f"that already exists so a stray write from an earlier process "
               f"can neither be overwritten nor certified "
               f"(re-registration 7.2 clause 7).")
    t = gaps["domain_thickness_t"]
    for sub, files in (("0", zero_dir(case)),
                       ("constant", constant_dir(case)),
                       ("system", system_dir(case, t, gaps))):
        os.makedirs(os.path.join(d, sub))
        for name, body in files.items():
            open(os.path.join(d, sub, name), "w").write(
                with_header(name, body, sub))
    # 0/T is touched LAST, so its mtime dates the run allowed to produce the
    # answer.  The age guard of section 7.2 clause 6 rests on this ordering.
    # RULING 4's two refutability assertions, READ BACK FROM DISK, BEFORE the
    # age-guard touch so that a case that fails them is never dated as launched.
    assert_two_d_registration(d, t)
    os.utime(os.path.join(d, "0", "T"), None)
    return d


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--preflight", metavar="CASE_DIR", default=None,
                    help="the CONSUMER-SIDE COMPLETENESS ASSERTION (section "
                         "3A): enumerate the field set the SOLVER requires and "
                         "REFUSE (exit 2) if any is absent from 0/.  Run "
                         "BEFORE the solver, by the launcher.")
    ap.add_argument("cases", nargs="*")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.preflight:
        if not os.path.isdir(a.preflight):
            refuse(f"{a.preflight}: not a case directory")
        assert_zero_complete(a.preflight)
        return EXIT_OK

    gaps = unresolved_gaps()
    if gaps:
        print(gap_report())
        refuse(f"{len(gaps)} unresolved registration gap(s): "
               f"{', '.join(gaps)}.  NOTHING WAS WRITTEN.")
    if not a.root:
        refuse("--root is required; this script does not guess.")
    resolved = {k: v["value"] for k, v in REGISTRATION_GAPS.items()}
    os.makedirs(a.root, exist_ok=True)
    for c in (a.cases or list(CASES)):
        if c not in CASES:
            refuse(f"{c!r} is not one of the ten registered K0d cases")
        print("wrote " + write_case(a.root, c, resolved))
    return EXIT_OK


# ==========================================================================
def selftest():
    import shutil
    import subprocess
    import tempfile
    print("=" * 74)
    print("build_k0f.py -- SELFTEST (planted controls)")
    print("=" * 74)
    fails = []

    def check_(label, cond, detail=""):
        print(f"  {'OK  ' if cond else 'FAIL'}  {label}"
              + (f"   [{detail}]" if detail else ""))
        if not cond:
            fails.append(label)

    check_("ten registered cases (nine + M1_m_seed)", len(CASES) == 10,
           str(len(CASES)))
    check_("M1_m_seed differs from M1_m in the T SEED AND NOTHING ELSE",
           CASES["M1_m_seed"]["closure"] == CASES["M1_m"]["closure"]
           and CASES["M1_m_seed"]["level"] == CASES["M1_m"]["level"]
           and CASES["M1_m_seed"]["seed_T"] == 308.15,
           "L2 kOmegaSST, hot start 308.15 K")
    check_("the RNGkEpsilon seed carries epsilon and NO omega",
           "epsilon" in SEED["RNGkEpsilon"] and "omega" not in SEED["RNGkEpsilon"])
    check_("the laminar seed carries no k, no omega, no nut",
           not ({"k", "omega", "nut"} & set(SEED["laminar"])))
    check_("omega 51.2 IS the registered epsilon under omega = eps/(Cmu k)",
           abs(EPS_IN / (0.09 * K_IN) - OMEGA_IN) < 1e-9,
           f"{EPS_IN / (0.09 * K_IN):.6f}")
    check_("I_hi's x4 sweep leaves inlet omega EXACTLY unchanged (A4.4)",
           abs(EPS_IN_IHI / (0.09 * K_IN_IHI) - OMEGA_IN_IHI) < 1e-9)
    check_("beta == 1/TRef by identity (re-registration 1.1)",
           abs(BETA - 1.0 / TREF) / BETA < 1e-7, f"1/{TREF} = {1.0 / TREF:.10e}")
    check_("TRef is 298.00, NOT the superseded 298.15", TREF == 298.00)
    check_("nu is 1.569e-5, the re-registration's decision", NU == 1.569e-05)

    # ranks and the cap conversion, asserted rather than assumed
    check_("RANKS is asserted == 1, so cap_core_min * 60 / ranks is the "
           "identity", RANKS == 1)
    check_("every one of the ten cases carries a registered cap",
           set(CAP_CORE_MIN) == set(CASES), str(len(CAP_CORE_MIN)))
    check_("M1_m_seed takes M1_m's cap line exactly (both L2 kOmegaSST)",
           CAP_CORE_MIN["M1_m_seed"] == CAP_CORE_MIN["M1_m"])
    drift = []
    for c in CASES:
        frozen, computed = timeout_for(c)
        if abs(frozen - computed) > 0.5:
            drift.append((c, frozen, computed))
    check_("the conversion reproduces the frozen 8.1 table on every row "
           "except the L2 row, which is frozen ONE SECOND LOW and is LEFT AS "
           "FROZEN because it binds tighter",
           all(abs(f - cc) <= 1.0 for _, f, cc in drift),
           "; ".join(f"{c}: frozen {f} vs {cc:.0f}" for c, f, cc in drift[:2])
           or "no drift")

    # ----------------------------------------------------------------------
    # THE GAP REFUSAL, in a subprocess so exit 2 is OBSERVED and not inferred.
    #
    # REPAIRED 2026-08-25.  THIS BLOCK USED TO BE BOTH STALE AND DANGEROUS, and
    # both halves are recorded because the second one nearly cost the rung its
    # pre-compute absence proof:
    #
    #   STALE -- it asserted that the builder REFUSES because a registration
    #   gap is unresolved.  AMENDMENT 2 sections A2.1a-A2.1d RESOLVED all four
    #   gaps, so that refusal no longer fires and the check could never pass
    #   again.  A check that can no longer pass is not a check.
    #
    #   DANGEROUS -- it invoked the REAL builder against a REAL fixed path,
    #   "/tmp/should_never_be_written", and asserted nothing was written there.
    #   With the gaps closed the builder DID write there: all ten case
    #   directories, measured.  HAD THAT PATH BEEN THE REGISTERED RUN TREE, THE
    #   SELFTEST ITSELF WOULD HAVE CREATED K0f_runs/ AND DESTROYED THE
    #   PRE-COMPUTE ABSENCE PROOF THAT EVERY AMENDMENT'S LEGALITY RESTS ON.
    #
    # AS REPAIRED, and it is the same shape as the AMENDMENT 2 section A2.3
    # lesson: PLANT INTO THE REAL CHANNEL, NEVER INTO A SPEC.  A copy of THIS
    # SCRIPT is written with ONE GAP RE-OPENED to None, and that copy is run.
    # The refusal it produces is the real refusal path, on the real code.
    # Every root used here is a fresh tempdir; no fixed path is ever passed.
    gap_tmp = tempfile.mkdtemp(prefix="k0d_gap_probe_")
    try:
        mutated = os.path.join(gap_tmp, "build_k0f_gap_reopened.py")
        src = open(os.path.abspath(__file__)).read()
        anchor = '"writeFormat": dict('
        _require(anchor in src, "gap-probe anchor not found")
        # re-open the gap by blanking the value this script would otherwise use
        # THE MUTATION MUST LAND *BEFORE* THE __main__ BLOCK.  Appending it to
        # the end of the file puts it after `sys.exit(main())`, where it never
        # executes -- the probe then proves nothing and reports a pass.  That
        # mistake was made once here and is recorded rather than smoothed over.
        entry = '\nif __name__ == "__main__":'
        _require(entry in src, "__main__ entry point not found")
        injection = (
            "\n\n# INJECTED BY selftest(): re-open one registration gap so the\n"
            "# REFUSAL PATH ITSELF is exercised on the real code, before main().\n"
            "REGISTRATION_GAPS['writePrecision']['value'] = None\n")
        mutated_src = src.replace(entry, injection + entry, 1)
        _require("REGISTRATION_GAPS['writePrecision']['value'] = None" in
                 mutated_src.split(entry)[0],
                 "injection did not land before main()")
        open(mutated, "w").write(mutated_src)
        never = os.path.join(gap_tmp, "never_written")
        r = subprocess.run([sys.executable, mutated, "--root", never],
                           capture_output=True, text=True)
        check_("NEGATIVE: with a gap RE-OPENED the builder REFUSES (exit 2) -- "
               "the refusal path is exercised on the real code, not asserted",
               r.returncode == EXIT_REFUSE, f"rc={r.returncode}")
        check_("the re-opened-gap refusal NAMES the gap and WRITES NOTHING",
               "writePrecision" in r.stdout and not os.path.exists(never),
               "nothing written" if not os.path.exists(never) else "WROTE")

        # POSITIVE counterpart: with every gap CLOSED the builder proceeds.
        # This is what proves the AMENDMENT 2 rulings actually cleared the
        # refusal, and it is why the check above is a control and not a
        # tautology.  IT IS RUN AGAINST A TEMPDIR AND NEVER AGAINST THE
        # REGISTERED RUN TREE.
        ok_root = os.path.join(gap_tmp, "writes_here")
        r2 = subprocess.run([sys.executable, os.path.abspath(__file__),
                             "--root", ok_root], capture_output=True, text=True)
        wrote = os.path.isdir(os.path.join(ok_root, "M1_c"))
        check_("POSITIVE: with all four AMENDMENT 2 gaps CLOSED the builder no "
               "longer refuses and BUILDS -- so the refusal above is a control, "
               "not a tautology", wrote and r2.returncode == EXIT_OK,
               f"rc={r2.returncode}, M1_c written={wrote}")
        check_("every gap carries a resolved value from AMENDMENT 2 A2.1a-A2.1d",
               all(v["value"] is not None for v in REGISTRATION_GAPS.values()),
               ", ".join(f"{k}={v['value']!r}"
                         for k, v in REGISTRATION_GAPS.items()))
        check_("NO FIXED PATH IS PASSED AS --root ANYWHERE IN THIS SELFTEST; "
               "every root is a fresh tempdir, so the selftest can never "
               "create the registered run tree",
               gap_tmp.startswith(tempfile.gettempdir())
               and never.startswith(gap_tmp) and ok_root.startswith(gap_tmp))

        # ------------------------------------------------------------------
        # THE READABILITY ARM.  ADDED 2026-08-25 BECAUSE ITS ABSENCE COST THE
        # RUNG A FAILED BUILD OF ALL TEN CASES.
        #
        # Every other check in this selftest reads the dictionaries back as
        # STRINGS THIS SCRIPT JUST WROTE.  That proves the CONTENT and proves
        # NOTHING about whether OpenFOAM can PARSE them -- and it could not:
        # every system/ and constant/ dictionary went out with no FoamFile
        # header and blockMesh refused all ten with a FATAL IO ERROR.
        #
        # THIS ARM ASKS THE CONSUMING PROGRAM.  It runs the real blockMesh on a
        # real built case in a tempdir and requires rc == 0 AND a polyMesh on
        # disk.  It is the same shape as AMENDMENT 2 section A2.3's repair:
        # exercise the channel that actually consumes the artifact.
        #
        # If OpenFOAM is not installed the arm SAYS SO and does not silently
        # pass -- a check skipped in silence reads as a check passed.
        foam_bashrc = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
        if not os.path.isfile(foam_bashrc):
            check_("OPENFOAM READABILITY ARM COULD NOT RUN: no OpenFOAM at "
                   f"{foam_bashrc}.  NOT SILENTLY SKIPPED -- reported as "
                   "unrun, because a check omitted in silence reads as a "
                   "check passed", False, "openfoam absent")
        else:
            bm_case = os.path.join(ok_root, "M1_c")
            r3 = subprocess.run(
                ["bash", "-c",
                 f"source {foam_bashrc} >/dev/null 2>&1 && "
                 f"blockMesh -case {bm_case}"],
                capture_output=True, text=True)
            pm = os.path.join(bm_case, "constant", "polyMesh", "points")
            check_("OPENFOAM ITSELF READS WHAT THIS BUILDER WRITES: real "
                   "blockMesh on a real built case returns 0 and produces a "
                   "polyMesh.  THIS IS THE ARM WHOSE ABSENCE LET TEN "
                   "HEADERLESS CASES BE WRITTEN",
                   r3.returncode == 0 and os.path.isfile(pm),
                   f"rc={r3.returncode}, polyMesh={os.path.isfile(pm)}")
            # NEGATIVE half: strip the header back off and blockMesh must FAIL.
            # Without this the arm above is not shown able to fire.
            strip_root = os.path.join(gap_tmp, "headerless")
            subprocess.run([sys.executable, os.path.abspath(__file__),
                            "--root", strip_root], capture_output=True,
                           text=True)
            hc = os.path.join(strip_root, "M1_c")
            for sub in ("system", "constant"):
                for fn in os.listdir(os.path.join(hc, sub)):
                    fp = os.path.join(hc, sub, fn)
                    txt = open(fp).read()
                    if txt.lstrip().startswith("FoamFile"):
                        open(fp, "w").write(txt.split("}\n", 1)[1].lstrip("\n"))
            r4 = subprocess.run(
                ["bash", "-c",
                 f"source {foam_bashrc} >/dev/null 2>&1 && "
                 f"blockMesh -case {hc}"],
                capture_output=True, text=True)
            check_("NEGATIVE: with the FoamFile headers STRIPPED BACK OFF, "
                   "blockMesh FAILS -- so the arm above was shown able to "
                   "fire and is not a probe that passes on anything",
                   r4.returncode != 0, f"rc={r4.returncode}")

            # --------------------------------------------------------------
            # THE SOLVER ARM.  blockMesh READS system/ AND constant/ AND NEVER
            # LOOKS AT 0/.  The blockMesh arm above therefore passed while
            # 0/U was still unreadable -- `internalField (0 0 0);` with no
            # `uniform` keyword -- and the solver refused every case on launch.
            # ONE READABILITY ARM WAS NOT ENOUGH BECAUSE IT EXERCISED ONLY THE
            # CHANNEL IT HAPPENED TO TOUCH.  This arm runs THE REAL SOLVER,
            # which is the only program that reads every 0/ field, for a
            # couple of iterations against a shortened endTime.
            cd_path = os.path.join(bm_case, "system", "controlDict")
            cd_txt = open(cd_path).read()
            open(cd_path, "w").write(
                cd_txt.replace("endTime         40000;", "endTime         2;")
                      .replace("writeInterval   4000;", "writeInterval   2;"))
            r5 = subprocess.run(
                ["bash", "-c",
                 f"source {foam_bashrc} >/dev/null 2>&1 && "
                 f"buoyantBoussinesqSimpleFoam -case {bm_case}"],
                capture_output=True, text=True)
            reached = "Time = 1" in r5.stdout
            check_("THE REAL SOLVER READS EVERY 0/ FIELD THIS BUILDER WRITES: "
                   "buoyantBoussinesqSimpleFoam runs two iterations and "
                   "reaches a Time line.  blockMesh NEVER READS 0/, which is "
                   "why the arm above passed while 0/U was unreadable",
                   r5.returncode == 0 and reached,
                   f"rc={r5.returncode}, reached Time=1: {reached}")
            # NEGATIVE half: put 0/U back into the broken form and require the
            # solver to refuse it.
            up = os.path.join(bm_case, "0", "U")
            open(up, "w").write(open(up).read().replace(
                "internalField   uniform (0 0 0);",
                "internalField   (0 0 0);"))
            r6 = subprocess.run(
                ["bash", "-c",
                 f"source {foam_bashrc} >/dev/null 2>&1 && "
                 f"buoyantBoussinesqSimpleFoam -case {bm_case}"],
                capture_output=True, text=True)
            check_("NEGATIVE: with 0/U's `uniform` keyword REMOVED the solver "
                   "REFUSES -- so the solver arm was shown able to fire on the "
                   "exact defect that reached the launch",
                   r6.returncode != 0, f"rc={r6.returncode}")

        # ------------------------------------------------------------------
        # THE `python3 -O` ARM.  `assert` IS REMOVED BY -O / PYTHONOPTIMIZE=1,
        # so a refusal carried by an assert is not a refusal under every
        # interpreter this script can be launched with.  Measured on this box:
        # a guard written as `assert RANKS == 1` REFUSED under python3 and
        # PROCEEDED under python3 -O.
        #
        # THIS ARM DOES NOT MERELY RUN THE SELFTEST UNDER -O.  A passing
        # selftest proves only the CLEAN path, and the clean path is exactly
        # the one an evaporated guard still walks.  IT DRIVES AN ACTUAL
        # REFUSAL UNDER -O AND REQUIRES IT TO STILL FIRE.
        r7 = subprocess.run(
            [sys.executable, "-O", mutated, "--root",
             os.path.join(gap_tmp, "never_written_dash_O")],
            capture_output=True, text=True)
        check_("THE REGISTERED REFUSAL STILL FIRES UNDER `python3 -O`: the "
               "re-opened-gap builder refuses with the optimiser on, so the "
               "refusal is not carried by an assert",
               r7.returncode == EXIT_REFUSE
               and not os.path.exists(os.path.join(gap_tmp,
                                                   "never_written_dash_O")),
               f"rc={r7.returncode}")
        # And the RANKS registration guard, driven under -O against a
        # sacrificial copy with ranks deliberately wrong.
        ranks_mut = os.path.join(gap_tmp, "build_k0f_ranks4.py")
        rsrc = open(os.path.abspath(__file__)).read()
        _require("\nRANKS = 1\n" in rsrc, "RANKS anchor not found")
        open(ranks_mut, "w").write(rsrc.replace("\nRANKS = 1\n",
                                                "\nRANKS = 4\n", 1))
        r8 = subprocess.run([sys.executable, "-O", ranks_mut, "--selftest"],
                            capture_output=True, text=True)
        check_("THE SERIAL REGISTRATION GUARD REFUSES UNDER `python3 -O` when "
               "RANKS is mutated to 4 -- under an assert it would have "
               "PROCEEDED and every core-minute figure would be wrong",
               r8.returncode != 0
               and "registered SERIAL" in (r8.stdout + r8.stderr),
               f"rc={r8.returncode}")
        # STATEMENT-TYPE MUTANT: reverting _require -> assert must be caught on
        # statement type alone.  Cheap and decisive; it needs no execution.
        import ast as _ast
        tree = _ast.parse(open(os.path.abspath(__file__)).read())
        n_assert = sum(1 for n in _ast.walk(tree) if isinstance(n, _ast.Assert))
        check_("NO `assert` STATEMENT ANYWHERE IN THIS INSTRUMENT carries a "
               "refusal, guard, control or gate -- checked on STATEMENT TYPE "
               "via the AST, so a revert of _require() -> assert is caught "
               "without running anything",
               n_assert == 0, f"{n_assert} assert statement(s) found")
    finally:
        shutil.rmtree(gap_tmp, ignore_errors=True)

    # the machinery, exercised under EXPLICITLY TEST-ONLY values.  These can
    # never reach a real build: main() reads REGISTRATION_GAPS, not this dict.
    testonly = {"writeFormat": "ascii", "writePrecision": 16,
                "writeCompression": "off", "domain_thickness_t": 0.01}
    tmp = tempfile.mkdtemp(prefix="k0d_build_")
    try:
        d = write_case(tmp, "M1_m", testonly)
        for f in ("T", "U", "p_rgh", "alphat", "k", "omega", "nut"):
            check_(f"M1_m 0/{f} written",
                   os.path.isfile(os.path.join(d, "0", f)))
        check_("M1_m has no 0/epsilon (kOmegaSST)",
               not os.path.exists(os.path.join(d, "0", "epsilon")))
        dl = write_case(tmp, "C_lam", testonly)
        check_("C_lam 0/ contains EXACTLY T U p_rgh alphat (A5.5.4)",
               sorted(os.listdir(os.path.join(dl, "0")))
               == ["T", "U", "alphat", "p_rgh"],
               str(sorted(os.listdir(os.path.join(dl, "0")))))
        db = write_case(tmp, "B_hi", testonly)
        tb = open(os.path.join(db, "0", "T")).read()
        check_("B_hi imposes 308.65 K on the floor and 288.15 elsewhere",
               "308.65" in tb and "288.15" in tb and "308.15" not in tb)
        ds = write_case(tmp, "M1_m_seed", testonly)
        ts = open(os.path.join(ds, "0", "T")).read()
        check_("M1_m_seed internalField is the HOT START 308.15 K",
               "internalField   uniform 308.15" in ts)
        tm = open(os.path.join(d, "0", "T")).read()
        check_("M1_m internalField is the registered cold seed 288.15 K",
               "internalField   uniform 288.15" in tm)
        check_("M1_m_seed and M1_m differ ONLY in T's internalField",
               all(open(os.path.join(ds, "0", f)).read()
                   == open(os.path.join(d, "0", f)).read()
                   for f in ("U", "p_rgh", "alphat", "k", "omega", "nut")))
        bm = open(os.path.join(d, "system", "blockMeshDict")).read()
        check_("blockMeshDict has three hex blocks and seven patches",
               bm.count("hex (") == 3
               and all(p in bm for p in ("inlet", "outlet", "floor", "ceiling",
                                         "leftWall", "rightWall", "frontAndBack")))
        check_("the reciprocal of every graded half is WRITTEN OUT, not '1/E'",
               "1/" not in bm and bm.count("(0.5 0.5 ") == 12,
               f"{bm.count('(0.5 0.5 ')} half-gradings")
        # the grading actually delivers the registered first cell
        s = LEVELS["L2"]
        e = expansion_for(s["first_cell"], 0.5 * L, s["Nx"] // 2)
        m = s["Nx"] // 2
        r_ = e ** (1.0 / (m - 1))
        first = 0.5 * L * (r_ - 1.0) / (r_ ** m - 1.0)
        check_("the solved x-expansion reproduces the registered L2 first cell "
               "to well inside condition D's 1 %",
               abs(first - s["first_cell"]) / s["first_cell"] < 1e-6,
               f"{first:.6e} vs {s['first_cell']:.6e}")
        cd = open(os.path.join(d, "system", "controlDict")).read()
        check_("controlDict carries the registered timings",
               all(x in cd for x in ("endTime         40000", "deltaT          1",
                                     "writeInterval   4000", "purgeWrite      2")))
        fs = open(os.path.join(d, "system", "fvSolution")).read()
        check_("fvSolution carries NO residualControl block (section 6)",
               "residualControl" not in fs)
        sd = open(os.path.join(d, "system", "sampleDict.graded")).read()
        sc = open(os.path.join(d, "system", "sampleDict.control")).read()
        check_("the graded extraction is cellPoint and the control is cell",
               "cellPoint" in sd and "interpolationScheme cell;" in sc)
        check_("both sample sets are uniform with 2081 points "
               "(spacing 5.000e-04 m)",
               sd.count("nPoints 2081") == 2
               and abs(L / (SAMPLE_N_POINTS - 1) - 5.0e-04) < 1e-12,
               f"{L / (SAMPLE_N_POINTS - 1):.6e} m")
        # the builder refuses a directory that already exists
        r2 = subprocess.run([sys.executable, "-c",
                             "import sys; sys.path.insert(0, %r); import build_k0f as B;"
                             "B.write_case(%r, 'M1_m', %r)"
                             % (os.path.dirname(os.path.abspath(__file__)), tmp, testonly)],
                            capture_output=True, text=True)
        check_("REFUSES (exit 2) a case directory that already exists "
               "(clause 7 precondition)", r2.returncode == EXIT_REFUSE,
               f"rc={r2.returncode}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s) did not hold")
        for f in fails:
            print("   - " + f)
        return EXIT_FAIL
    print("SELFTEST PASSED: every probe was shown able to FIRE on a planted")
    print("defect and to STAY QUIET on its clean counterpart.")
    print("")
    print("WHAT A PASS HERE DOES AND DOES NOT MEAN, stated because the old")
    print("banner here became FALSE and an instrument may not assert something")
    print("false about itself (AMENDMENT 2 section A2.3c item 4):")
    print("  * AMENDMENT 2 sections A2.1a-A2.1d RESOLVED all four registration")
    print("    gaps, so main() NO LONGER REFUSES on them.  GIVEN --root, THIS")
    print("    SCRIPT NOW WRITES TEN CASE DIRECTORIES THERE.")
    print("  * It therefore MUST NOT be pointed at")
    print("    verification/runs/F14-cooling-ladder/K0f_runs until the")
    print("    supervisor has read the diffs and fired: creating that tree")
    print("    destroys the pre-compute absence proof every amendment's")
    print("    legality rests on.")
    print("  * A PASS here is still not a proof of correctness.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
