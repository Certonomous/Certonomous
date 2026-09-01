#!/usr/bin/env python3
"""T25R3 STAGER.  Writes dictionaries and copies meshes.  EXECUTES NOTHING.

Registration: docs/campaigns/T-family/T25R3_PREREGISTRATION.md v1.1, §15 step 4.

WHAT IT INHERITS UNCHANGED, and this is deliberate: the thermophysical
properties, the turbulence model, both regions' fvSchemes, both regions'
fvSolution (including the five LITERAL `Final` relaxation keys that are the fix
for the T25R_L1 divergence), the 0.orig fields and the controlDict `functions`
block all come from the staged, verified T25R2_L2 tree BY COPY.  Retyping a
thermophysical property to change a time step is how a rung acquires a defect
that no gate is looking for.

WHAT IT OVERWRITES, and only this:
  constant/module/fvOptions   -- the 1 s ramps (§5.1)
  system/fvSolution           -- nOuterCorrectors 15 (30 on W30)  (§4.1)
  system/controlDict          -- LEG A; and controlDict.legB beside it (§6)
  system/decomposeParDict     -- 2 ranks, `simple (2 1 1)`, both regions (§11)

`0` IS NOT CREATED HERE.  It is created by the LAUNCHER from `0.orig`
immediately before the solver starts, so that `0/module/T` dates the run allowed
to produce the answer.  Rule 4's age guard depends on that ordering and this
script must not pre-empt it.

    python3 stage_t25R3.py --selftest
    python3 stage_t25R3.py --stage <RUN_ID>
    python3 stage_t25R3.py --stage-all
"""

import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TF = os.path.dirname(HERE)
EXIT_REFUSE = 2

DICT_SRC = os.path.join(TF, "T25R2_MODULE_runs", "T25R2_L2")
MESH_SRC = {
    "L1": os.path.join(TF, "T25R2_MODULE_runs", "T25R2_L1"),
    "L2": os.path.join(TF, "T25R2_MODULE_runs", "T25R2_L2"),
    "L3": os.path.join(HERE, "_meshsrc_L3"),
}
CELLS = {"L1": 16608, "L2": 37368, "L3": 84078}
IFACE = {"L1": 560, "L2": 840, "L3": 1260}
NY_CH = {"L1": 24, "L2": 36, "L3": 54}

# §2/§6.1: (level, dt_legA, dt_legB, nOuterCorrectors, stepsA, stepsB)
RUNS = {
    "S1":  ("L1", 0.02,  0.1,   15, 3500,  8300),
    "S2":  ("L2", 0.02,  0.1,   15, 3500,  8300),
    "S3":  ("L3", 0.02,  0.1,   15, 3500,  8300),
    "T2":  ("L2", 0.01,  0.05,  15, 7000,  16600),
    "T4":  ("L2", 0.005, 0.025, 15, 14000, 33200),
    "W30": ("L2", 0.02,  0.1,   30, 3500,  8300),
}
LEG_A_END, T_END, WRITE_INTERVAL = 70.0, 900.0, 5.0
RANKS = 2

HDR = """/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       %(cls)s;
%(loc)s    object      %(obj)s;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
"""


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def w(case, rel, cls, obj, body, location=None):
    p = os.path.join(case, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    loc = '    location    "%s";\n' % location if location else ""
    with open(p, "w") as f:
        f.write(HDR % dict(cls=cls, obj=obj, loc=loc))
        f.write("\n" + body.rstrip() + "\n\n")
        f.write("// " + "*" * 73 + " //\n")
    return p


# ==========================================================================
# THE RAMPED SOURCE.  §5.1, and its energy is §5.2's, computed not typed.
# ==========================================================================

RAMP_TABLE = ((0.000, 0.0), (1.000, 100000.0), (60.000, 100000.0),
              (61.000, 25000.0), (900.000, 25000.0))


def ramp_energy():
    """J/m3 over 0-900 s.  EXACT for a piecewise-linear Function1 table."""
    return sum(0.5 * (a + b) * (t1 - t0)
               for (t0, a), (t1, b) in zip(RAMP_TABLE, RAMP_TABLE[1:]))


FV_OPTIONS = """// §5.1 -- SANAA'S §2, VERBATIM: "replace the step at t = 0 and t = 60 s with
// a 1 s linear ramp (a discontinuous source destroys time accuracy at the
// jump)". Loads as ruled: 1e5 W/m3 pulse, 2.5e4 W/m3 cruise.
//
// *** THE VOLUMETRIC RATE IS THE REGISTERED QUANTITY. A PER-CELL WATTAGE IS NOT
// AN INPUT ANYWHERE IN THIS RUNG. ***
//
// `Function1 table` defaults interpolationScheme to `linear`, so consecutive
// breakpoints are the ends of a LINEAR RAMP. Registered and CHECKED by
// verify_mesh_t25R3.py: every breakpoint (1, 60, 61 s), the leg boundary (70 s)
// and the write interval (5 s) is an EXACT integer multiple of EVERY registered
// time step in both ladders, so no step lands inside a ramp without also
// landing on both its ends. The coarsest ladder level resolves each ramp with
// 50 steps; the finest with 200. T25R2's 1 ms ramp at deltaT 0.5 resolved it
// with ZERO, which is the defect this rung exists to remove.
//
// ENERGY, computed here and NOT typed (§5.2): the integral over 0-900 s is
// 2.698750e+07 J/m3, an adiabatic bound of 10.7950 K, and 647,700 J over the
// 0.024 m3 solid. The two ramps cost EXACTLY 0.0050 K of bound and EXACTLY
// 300 J against T25R2's stepped source. The comparator's C1 ledger gates
// against the RAMPED figure; gating against the stepped one would hide a 300 J
// error inside a 2 % residual and it would look like physics.
//
// `volumeMode specific` IS MANDATORY: the wrong mode is a SILENT scale error by
// exactly the zone volume. `injectionRate` does not exist at v2606; the
// accepted form is `sources`.

volumetricHeatSource
{
    type            scalarSemiImplicitSource;
    active          yes;
    selectionMode   all;
    volumeMode      specific;
    sources
    {
        h
        {
            explicit    table
            (
__ROWS__
            );
            implicit    none;
        }
    }
}
"""


def fv_options_body():
    rows = "\n".join("                ( %8.3f  %13.6f)" % (t, q)
                     for t, q in RAMP_TABLE)
    return FV_OPTIONS.replace("__ROWS__", rows)


TOP_SOLUTION = """// The TOP-LEVEL PIMPLE dict is the one chtMultiRegionFoam reads for its outer
// loop: readPIMPLEControls.H builds an fvSolution on the runTime (there is no
// top-level mesh) and takes nOuterCorrectors from it.
//
// *** THERE IS NO residualControl ON THIS SOLVER'S OUTER LOOP, AND SANAA'S §2
// ASKED FOR ONE. *** chtMultiRegionFoam.C:109 is a plain
//     for (int oCorr=0; oCorr<nOuterCorr; ++oCorr)
// -- NOT a pimpleControl -- so the loop runs EXACTLY nOuterCorrectors sweeps
// every step, unconditionally, and readPIMPLEControls.H reads that ONE key and
// nothing else. "No fixed-count sweeps anywhere" is not achievable here without
// patching OpenFOAM. Registered departure 1, prereg §0.1.
//
// WHAT REPLACES IT IS NOT NOTHING. The tolerance guarantee is replaced by a
// MEASURED prerequisite, gate G-I (§7.3): the change in the graded quantity
// between 15 and 30 outer sweeps must be at least 10x smaller than the
// difference between consecutive mesh levels -- Sanaa's own §0.2 rule, promoted
// to a gate, expressed in kelvin rather than in a residual whose mapping to
// kelvin nobody knows. Run W30 exists for no other purpose.
//
// COMPOSED WITH G-S (Amendment A1.2), THIS DEMANDS ITERATIVE CONVERGENCE TO
// 1.000e-02 K. T25R2 failed at 2.315190e-02 K. The substitute is 2.32x TIGHTER
// than the number that failed the predecessor, not looser.
//
// CHECKED against the registered value by verify_mesh_t25R3.py, which REFUSES
// on a mismatch: a swapped sweep count would make G-I meaningless while leaving
// every other check green.
PIMPLE
{
    nOuterCorrectors %d;
    nNonOrthogonalCorrectors 0;
}
"""

X_SPLIT = 0.050        # m -- the SHARED cutting plane, x = LX/2.

DECOMPOSE = """// 11 + ADDENDUM D1 -- RECORDED EXPLICITLY, IDENTICAL ON ALL SIX RUNS.
//
// *** `method simple` WAS REGISTERED AND IT CANNOT WORK HERE. MEASURED, NOT
// PREDICTED: it was staged, launched, and chtMultiRegionFoam REFUSED at the
// first coupled solve of t=0 with
//     "The number of faces on either side of the coupled patch 3 are not the
//      same. This might be due to the decomposition used."
//     (lduPrimitiveMeshAssemblyTemplates.C:72)
//
// THE MECHANISM, and it would defeat ANY bounding-box method. The staged
// interface carries `useImplicit true`, so the conjugate coupling is assembled
// into ONE lduMatrix across both regions, which requires both sides of every
// interface face to live on the SAME rank. But `decomposePar` decomposes EACH
// REGION INDEPENDENTLY, and `simple` cuts each at ITS OWN bounding-box
// midpoint. The module spans x in [0, 0.100]; the coolant spans [-0.050,
// 0.200] because of the plenums. So the two cuts fall at x = 0.0500 and
// x = 0.0750, and every interface face in that 25 mm band has its two sides on
// DIFFERENT ranks. `hierarchical` cuts on the same bounding boxes and fails
// identically; `scotch` is refused for its own reasons and gives no alignment
// guarantee either.
//
// WHAT IS REGISTERED INSTEAD: `manual`, from a cell map this lab computes on a
// SINGLE SHARED PLANE x = %.4f m applied to BOTH regions, so the interface
// partition is identical on both sides by construction. x = 0.050 is a mesh
// FACE on every level (nx_mid 40/60/90 over 0.100 m) and never a cell centre,
// so no cell straddles it.
//
// 11's PURPOSE IS FULLY PRESERVED, and that is why this is an addendum and not
// a new gate: the partition must not VARY ACROSS THE LADDER or it contaminates
// the observed order. One rule, one plane, all six runs, both regions. There is
// still NO SEED -- `manual` reads a file this lab wrote deterministically from
// cell centres, which is stronger than `simple`, not weaker.
//
// DISCLOSED: T25R2 ran SERIAL. No T25R3 number is bit-comparable with a T25R2
// number.

numberOfSubdomains %d;
method          manual;
manualCoeffs
{
    dataFile    "cellDecomposition";
}
"""


def write_decomposition(case, region, nranks):
    """Write constant/<region>/cellDecomposition: rank by the SHARED plane.

    Computed from the staged polyMesh, never assumed. REFUSES if any cell
    centre lands on the plane (a straddling cell would split an interface face)
    or if either rank would receive no cells."""
    sys.path.insert(0, HERE)
    import analyse_t25R3 as A
    m = A.Mesh(case, region)
    ranks = []
    for i in range(m.n):
        if abs(m.cx[i] - X_SPLIT) < 1e-12:
            refuse("%s cell %d has its centre ON the split plane x = %.6f; a "
                   "straddling cell would tear an interface face" % (region, i,
                                                                     X_SPLIT))
        ranks.append(0 if m.cx[i] < X_SPLIT else 1)
    if len(set(ranks)) != nranks:
        refuse("%s: the split plane gives %d non-empty ranks, not %d"
               % (region, len(set(ranks)), nranks))
    p = os.path.join(case, "constant", region, "cellDecomposition")
    with open(p, "w") as f:
        f.write(HDR % dict(cls="labelList", loc='    location    "constant/%s";\n'
                           % region, obj="cellDecomposition"))
        f.write("\n%d\n(\n" % m.n)
        f.write("\n".join(str(r) for r in ranks))
        f.write("\n)\n;\n")
    return ranks.count(0), ranks.count(1)


def control_dict(leg, dt, end_t, start_from, steps, run):
    functions = open(os.path.join(DICT_SRC, "system", "controlDict")).read()
    m = re.search(r"^functions\s*$.*?^\}\s*$", functions, re.M | re.S)
    if not m:
        refuse("could not locate the inherited `functions` block in %s -- it is "
               "copied VERBATIM and never retyped" % DICT_SRC)
    return """application     chtMultiRegionFoam;

// §6 -- LEG %s of TWO. chtMultiRegionFoam reads ONE scalar deltaT from this
// dictionary and, with adjustTimeStep no, never changes it. The registered
// schedule has two segments (dt = 0.02 s to t = 70 s, 0.1 s after -- Sanaa's
// §2 first option, her exact numbers), so it is run as TWO CHAINED
// INVOCATIONS.
//
// WHY NOT THE `setTimeStep` FUNCTION OBJECT, WHICH EXISTS AND WOULD PROBABLY
// WORK: it requires adjustTimeStep true, which activates the solver's own
// Courant/diffusion control, and its interaction with that control on the FIRST
// step cannot be established without running the solver. THE PRINCIPLE THAT
// DECIDES IT: a time-step schedule that can only be verified from a log line
// AFTER the solver ran cannot be pre-registered as an INPUT. Here deltaT is a
// literal scalar a supervisor reads as a diff before compute.
//
// FLOATING POINT, SETTLED AT SOURCE BEFORE REGISTERING: 0.02 is not a
// binary-exact fraction. Time.C:1120-1124 computes the write index as
//     label(((value() - startTime_) + 0.5*deltaT_)/writeInterval_)
// and that +0.5*deltaT guard makes the index immune to drift of order 1e-13.
// Names are formatted `general` at timePrecision 12; drift to t = 900 is ~1e-11
// against a 12-significant-digit resolution of 1e-9 there. Two orders of margin.

startFrom       %s;
startTime       0;
stopAt          endTime;
endTime         %g;
deltaT          %.6g;

// NO ADAPTIVE STEPPING ON GATED RUNS. With adjustTimeStep no, maxCo and maxDi
// are INERT and are therefore NOT WRITTEN AT ALL -- an inert control in a frozen
// dictionary is a future reader's trap. Sanaa's second option (adaptive at
// maxCo 0.5) is REFUSED and priced in §0.3: Co ~ 1600 at the old step scales to
// dt ~ 1.6e-04 s, ~5.8 MILLION steps, ~490x the registered count, and it would
// destroy the time ladder because an adaptively chosen dt is not exactly
// halvable. Co is REPORTED per level, never controlled.
adjustTimeStep  no;

// %d registered steps on this leg. Rule 4's ExecutionTime clause is a
// STEP-COUNT identity, not a time-value identity (§9.1 conjunct 5), and
// mark_done_t25R3.py checks it PER LEG.

writeControl    runTime;
writeInterval   %g;
purgeWrite      0;

// writePrecision 12, NOT the default 6. At T ~ 293 K six significant figures
// leave a ~1 mK write quantum, LARGER than the discretisation signals this rung
// gates on. It is also what bounds the leg-B restart truncation at ~3e-10 K,
// which is ~3.3e8 times smaller than tau (§6.3).
writeFormat     ascii;
writePrecision  12;
writeCompression off;
timeFormat      general;
timePrecision   12;
runTimeModifiable false;

// INSTRUMENTS -- COPIED VERBATIM from the staged T25R2_L2 controlDict, never
// retyped. A function object with an unknown `operation` aborts AT
// CONSTRUCTION and would throw away the whole solve.
%s
""" % (leg, start_from, end_t, dt, steps, WRITE_INTERVAL, m.group(0))


# ==========================================================================
# STAGING
# ==========================================================================

_MESH_REL = ("constant/polyMesh", "constant/coolant/polyMesh",
             "constant/module/polyMesh")


def stage(run):
    if run not in RUNS:
        refuse("%r is not one of the six registered runs of §2; the run set is "
               "CLOSED" % run)
    level, dtA, dtB, nouter, stepsA, stepsB = RUNS[run]
    case = os.path.join(HERE, run)
    if os.path.exists(case):
        refuse("%s already exists. This stager never overwrites a case: a "
               "restage on top of a run would leave time directories that make "
               "rule 4's age guard unevaluable." % case)
    for src in (DICT_SRC, MESH_SRC[level]):
        if not os.path.isdir(src):
            refuse("source tree %s is absent" % src)

    shutil.copytree(
        DICT_SRC, case, symlinks=False,
        ignore=shutil.ignore_patterns("log.*", "*.py", "*.sh", "processor*",
                                      "postProcessing", "COMPLETION.*",
                                      "STATUS.*", ".rc.*"))
    for junk in ("0",):
        p = os.path.join(case, junk)
        if os.path.isdir(p):
            shutil.rmtree(p)
    for e in list(os.listdir(case)):
        if re.fullmatch(r"\d+(\.\d+)?", e) and os.path.isdir(
                os.path.join(case, e)):
            shutil.rmtree(os.path.join(case, e))

    if os.path.realpath(MESH_SRC[level]) != os.path.realpath(DICT_SRC):
        for rel in _MESH_REL:
            dst = os.path.join(case, rel)
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            shutil.copytree(os.path.join(MESH_SRC[level], rel), dst)
        c2r = os.path.join(MESH_SRC[level], "constant", "cellToRegion")
        if os.path.isfile(c2r):
            shutil.copyfile(c2r, os.path.join(case, "constant", "cellToRegion"))

    w(case, "constant/module/fvOptions", "dictionary", "fvOptions",
      fv_options_body(), location="constant/module")
    w(case, "system/fvSolution", "dictionary", "fvSolution",
      TOP_SOLUTION % nouter, location="system")
    w(case, "system/controlDict", "dictionary", "controlDict",
      control_dict("A", dtA, LEG_A_END, "startTime", stepsA, run),
      location="system")
    w(case, "system/controlDict.legB", "dictionary", "controlDict",
      control_dict("B", dtB, T_END, "latestTime", stepsB, run),
      location="system")
    for region in ("coolant", "module"):
        n0, n1 = write_decomposition(case, region, RANKS)
        print("      %-8s manual split at x=%.3f -> rank0 %d cells, rank1 %d"
              % (region, X_SPLIT, n0, n1))
    for rel in ("system/decomposeParDict",
                "system/coolant/decomposeParDict",
                "system/module/decomposeParDict"):
        w(case, rel, "dictionary", "decomposeParDict",
          DECOMPOSE % (X_SPLIT, RANKS), location=os.path.dirname(rel))

    if os.path.isdir(os.path.join(case, "0")):
        refuse("`0` exists after staging. It must be created by the LAUNCHER "
               "from 0.orig immediately before the solve, so that 0/module/T "
               "dates the run; rule 4's age guard depends on that ordering.")
    print("staged %-4s level %s  %d cells  nOuterCorrectors %d  "
          "dt %.6g / %.6g  steps %d + %d"
          % (run, level, CELLS[level], nouter, dtA, dtB, stepsA, stepsB))
    return case


def selftest():
    fails = [0]

    def chk(name, cond):
        print("  %-4s %s" % ("ok" if cond else "FAIL", name))
        if not cond:
            fails[0] += 1

    e = ramp_energy()
    chk("ramped source integral is 2.698750e+07 J/m3 (COMPUTED from the table, "
        "not typed)", abs(e - 2.698750e7) < 1.0)
    chk("adiabatic bound on the 900 s rise is 10.7950 K",
        abs(e / (2500.0 * 1000.0) - 10.7950) < 1e-4)
    chk("total generated energy over the 0.024 m3 solid is 647,700 J -- the "
        "figure C1 gates against",
        abs(e * 0.024 - 647700.0) < 1.0)
    e60 = sum(0.5 * (a + b) * (t1 - t0)
              for (t0, a), (t1, b) in zip(RAMP_TABLE, RAMP_TABLE[1:]) if t1 <= 60)
    chk("adiabatic bound on the pulse alone is 2.3800 K (T25R2's stepped source "
        "gave 2.4000; the ramp costs EXACTLY 0.0200 K)",
        abs(e60 / 2.5e6 - 2.3800) < 1e-4)
    chk("the ramps start at ZERO at t=0 -- a source that is already on at t=0 "
        "is the discontinuity Sanaa ordered removed", RAMP_TABLE[0][1] == 0.0)

    for run, (lv, dtA, dtB, n, sa, sb) in RUNS.items():
        chk("%s: leg A steps %d == 70/%g" % (run, sa, dtA),
            abs(sa - LEG_A_END / dtA) < 1e-6)
        chk("%s: leg B steps %d == 830/%g" % (run, sb, dtB),
            abs(sb - (T_END - LEG_A_END) / dtB) < 1e-6)
        for bp in (1.0, 60.0, 61.0, 70.0, WRITE_INTERVAL):
            chk("%s: %g s is an exact multiple of dt %g" % (run, bp, dtA),
                abs(round(bp / dtA) - bp / dtA) < 1e-9)
        for bp in (70.0, WRITE_INTERVAL):
            chk("%s: %g s is an exact multiple of dt %g" % (run, bp, dtB),
                abs(round(bp / dtB) - bp / dtB) < 1e-9)
    chk("the space triple is exactly r=1.5 in cell count (2.25 per level, 2D)",
        abs(CELLS["L2"] / CELLS["L1"] - 2.25) < 1e-12
        and abs(CELLS["L3"] / CELLS["L2"] - 2.25) < 1e-12)
    chk("the time triple halves EXACTLY at both steps",
        RUNS["S2"][1] / RUNS["T2"][1] == 2.0
        and RUNS["T2"][1] / RUNS["T4"][1] == 2.0)
    chk("W30 differs from S2 in nOuterCorrectors and NOTHING ELSE -- G-I is a "
        "sweep-count comparison and any other difference would confound it",
        RUNS["W30"][:3] == RUNS["S2"][:3] and RUNS["W30"][3] == 30
        and RUNS["S2"][3] == 15)
    chk("staging an unregistered run id REFUSES",
        _refuses(lambda: stage("S9")))
    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails[0] else "FAIL",
                                         fails[0]))
    return 0 if not fails[0] else 1


def _refuses(fn):
    try:
        fn()
    except SystemExit as ex:
        return ex.code == EXIT_REFUSE
    return False


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--stage-all" in argv:
        for r in ("S1", "S2", "S3", "T2", "T4", "W30"):
            stage(r)
        return 0
    if "--stage" in argv:
        stage(argv[argv.index("--stage") + 1])
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
