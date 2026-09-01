#!/usr/bin/env python3
"""T25R2 CASE STAGER -- builds the four registered case directories by REUSING
the meshes already on disk, and writes the four dictionaries that T25R2 changes.

Registered at `docs/campaigns/T-family/T25R2_PREREGISTRATION.md` sections 2.5,
3.4 and 4.5.  Committed BEFORE ANY T25R2 COMPUTE.

*** THIS FILE HAS NEVER BEEN EXECUTED. ***  Section 10 registers the order
commit -> THE SUPERVISOR'S PERSONAL DIFF READ -> stage/verify -> launch.

=====================================================================
IT RUNS NOTHING.  THAT IS A CHECKABLE PROPERTY, AND IT IS CHECKED.
=====================================================================
This script starts no external program: it imports no `subprocess`, no `os.system`
and no `os.exec*`, and --selftest PROVES that by token search over its own
source.  It copies files and writes dictionaries.  `blockMesh`,
`splitMeshRegions` and `checkMesh` are NOT invoked from here, and neither is a
solver.  VERIFICATION_CHARTER 2d.2 closes a registration's gates at FIRST
COMPUTE, BUILD COMPUTE INCLUDED, so a stager that quietly meshed would close the
gates of a comparator the supervisor has not yet read.

=====================================================================
WHY THE MESH IS REUSED AND NOT REBUILT
=====================================================================
The three registered meshes ALREADY EXIST and are MEASURED CORRECT:

  T25R_MODULE_runs/T25R_L1         module 3840 + coolant 12768 = 16608 cells
  T25R_MODULE_runs/T25R_L2         module 8640 + coolant 28728 = 37368 cells
  T25R_MODULE_runs/T25R_L2_DT025   module 8640 + coolant 28728 = 37368 cells

with `Mesh OK`, max non-orthogonality 0 and max skewness ~1e-13 on every region
of every level (`log.checkMesh.<region>` in each case directory, read by this
lane).  THE T25R2 LOAD ENTERS AS AN `fvOptions` VOLUMETRIC SOURCE AND CHANGES NO
CELL, no boundary and no zone -- so a rebuild would produce the same mesh, cost
build compute, and put a live rule-6 referral (`build_t25R.py`, which differs
from its committed blob) on the critical path of a graded rung.

THE REUSE IS PROVED, NOT ASSERTED.  Every file under `constant/` and `0.orig/`
is hashed in the source and in the destination and the two digests must be
IDENTICAL, file for file, with identical file sets.  A single mismatch is a
REFUSAL.  The source tree is hashed again AFTER the copy and must be unchanged:
this script must be incapable of altering the evidence it reads.

=====================================================================
WHAT IS OVERWRITTEN, AND ONLY THIS
=====================================================================
  constant/module/fvOptions   -- section 4.5, SANAA'S VOLUMETRIC LOADS
  system/fvSolution           -- section 3.5, nOuterCorrectors PER CASE
  system/coolant/fvSolution   -- section 3.4, the T25RF arm A2T numerics
  system/module/fvSolution    -- section 3.4, arm A2T's solid dict

Everything else -- `controlDict` (endTime 900, the registered `deltaT`,
`adjustTimeStep no`, `writePrecision 12` and the `surfaceFieldValue`
instruments section 6.2 needs), `fvSchemes`, the thermophysical and turbulence
dictionaries, `g`, `regionProperties`, `0.orig` -- is COPIED UNCHANGED, because
T25R registered it correctly and section 0.1 inherits it verbatim.

=====================================================================
THE STAGER IS VALIDATED BY THE COMPARATOR'S OWN ADMISSION CHECKS
=====================================================================
After writing, this script calls `analyse_t25R2.numerics_check()` and
`analyse_t25R2.pulse_table_check()` on what it just wrote.  It therefore CANNOT
stage a case the comparator would refuse: the writer is graded by the reader,
in the same invocation, before anything is launched.

NO `assert` (L-332).  Every departure is an explicit REFUSAL (exit 2).

Usage: python3 stage_t25R2.py <CASE> [--root DIR] | --all | --selftest
Exit:  0 staged, 2 REFUSAL.
"""
import hashlib
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t25R2 as A                                       # noqa: E402

EXIT_OK, EXIT_REFUSE = 0, 2

# Section 2.5: which ALREADY-BUILT mesh each registered case reuses.
SOURCE = {
    "T25R2_L1":       "T25R_L1",
    "T25R2_L1_OC20":  "T25R_L1",
    "T25R2_L2":       "T25R_L2",
    "T25R2_L2_DT025": "T25R_L2_DT025",
}
SRC_ROOT = os.path.abspath(os.path.join(HERE, "..", "T25R_MODULE_runs"))

# The measured cell counts of the meshes being reused (section 2.2), checked
# against `constant/<region>/polyMesh/owner`'s own header count.
CELLS = {"T25R_L1": {"module": 3840, "coolant": 12768},
         "T25R_L2": {"module": 8640, "coolant": 28728},
         "T25R_L2_DT025": {"module": 8640, "coolant": 28728}}

COPY_TREES = ("constant", "0.orig", "system")
COPY_FILES = ("log.blockMesh", "log.splitMeshRegions",
              "log.checkMesh.module", "log.checkMesh.coolant")
# HASHED FOR IDENTITY: the mesh and the initial fields.  `system` is excluded
# because this script deliberately overwrites three files inside it.
HASH_TREES = ("constant", "0.orig")

# NEVER COPIED: they belong to the T25R run, not to this rung.
#   0/ and every time directory  -- rule 4's guard refuses a case that has them
#   log.solve, STATUS.*, .rc.*   -- the record of the 04:09Z divergence
#   postProcessing/              -- T25R's instruments, not T25R2's
#   *.CELLZONES_FAILED*          -- the first, abandoned splitMeshRegions attempt


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def _tree_digests(root, trees):
    """{relative path -> sha256} over the named subtrees.  Deterministic."""
    out = {}
    for t in trees:
        base = os.path.join(root, t)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames.sort()
            for fn in sorted(filenames):
                p = os.path.join(dirpath, fn)
                out[os.path.relpath(p, root)] = _sha(p)
    return out


def _owner_count(path):
    """The cell count in a polyMesh `owner` header -- `note ... nCells: N`."""
    txt = open(path, errors="replace").read(4096)
    m = re.search(r"nCells\s*:\s*(\d+)", txt)
    return int(m.group(1)) if m else None


# ==========================================================================
# THE FOUR DICTIONARIES T25R2 WRITES.
# ==========================================================================

_HDR = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "%s";
    object      %s;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
"""


def fvoptions_text():
    """Section 4.5.  SANAA'S VOLUMETRIC LOADS, and the per-cell wattages stated
    ONLY as derived consequences so no reader converts one silently."""
    return _HDR % ("constant/module", "fvOptions") + """
// SECTION 4.2 -- SANAA'S 2026-09-01 04:20Z ORDER, VERBATIM:
//   "set the heat source as a volumetric rate from a real cell, not a per-cell
//    wattage on a unit-depth model. Takeoff: q''' ~ 1e5 W/m3 (~40-50 W in a
//    100x30x150 mm cell, 5-8C class); cruise ~ 2.5e4 W/m3."
//
// *** THE VOLUMETRIC RATE IS THE REGISTERED QUANTITY.  A PER-CELL WATTAGE IS
// NOT AN INPUT ANYWHERE IN THIS RUNG. ***
//   basis, HERS: 1.0e5 W/m3 x (0.100 x 0.030 x 0.150 m) = 45.0 W in the real
//                cell, inside her stated 40-50 W band.  Cruise: 11.25 W.
//   DERIVED CONSEQUENCE of the 2-D UNIT-DEPTH model, NOT a claim about a cell:
//                1.0e5 x 3.000e-03 m3 = 300.0 W per metre of depth (75.0 W at
//                cruise).  T25R's 210 W/cell construction is what she rejected
//                by name and it is gone.
//   Her 100 x 30 mm SECTION is the registered 2-D section EXACTLY; only the
//   depth differs, and a VOLUMETRIC rate is depth-independent, so q''' carries
//   across with no conversion at all.
//
// SECTION 4.3, REGISTERED BEFORE THE RUN: the adiabatic bound on the pulse rise
// is q'''*t/(rho*cp) = 2.4000 K, and over the full 900 s it is 10.8000 K.
// SANAA'S RULING IS BINDING: "The temperature rise is then whatever the physics
// gives... If the result is 8 K, 8 K is the answer."  NOTHING IS TUNED TOWARD A
// TARGET, and 8 K falling inside the band this basis implies is a consequence
// of her basis, not of any choice made after seeing it.
//
// THREE v2606 FACTS, EACH ALREADY PAID FOR BY THIS FAMILY:
//  1. THE FIELD IS `h`, NOT `T`.  The solid energy equation is in ENTHALPY; an
//     entry on T is NEVER APPLIED and the solid is SILENTLY UNHEATED.
//  2. `injectionRate` DOES NOT EXIST at v2606; the accepted forms are `sources`
//     (2206+) or the legacy `injectionRateSuSp`.
//  3. `volumeMode` IS MANDATORY and the wrong mode is a SILENT scale error by
//     exactly the zone volume.  `specific` => the values below are in W/m3.
//
// THE BREAKPOINT PLACEMENT.  `Function1 table` defaults interpolationScheme to
// `linear`, so the two breakpoints at the edge are the ends of a 1 ms RAMP.
// The ramp ENDS at 60.000, so t = 60 samples the CRUISE endpoint exactly.
// Registered condition, checked by the comparator: no step time on either
// registered deltaT falls strictly inside (59.999, 60.000).

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
                (  0.000  100000.000000)
                ( 59.999  100000.000000)
                ( 60.000   25000.000000)
                (900.000   25000.000000)
            );
            implicit    none;
        }
    }
}

// ************************************************************************* //
"""


def fvsolution_top_text(case):
    """Section 3.5.  nOuterCorrectors PER CASE.  This one number is the whole
    outer-loop gate: `T25R2_L1` and `T25R2_L1_OC20` differ in NOTHING ELSE."""
    return _HDR % ("system", "fvSolution") + """
// The TOP-LEVEL PIMPLE dict is the one chtMultiRegionFoam reads for its outer
// loop: readPIMPLEControls.H builds an fvSolution on the runTime (there is no
// top-level mesh) and takes nOuterCorrectors from it.
//
// *** THERE IS NO residualControl ON THIS SOLVER'S OUTER LOOP. ***
// chtMultiRegionFoam.C:109 is a plain `for (oCorr=0; oCorr<nOuterCorr; ++oCorr)`
// -- NOT pimpleControl -- so the loop runs EXACTLY nOuterCorrectors sweeps every
// step, unconditionally, and emits no "converged in"/"not converged within"
// line, ever.
//
// *** T25R's SECTION 3.5 GATE IS INVALID HERE AND IS GONE. ***  It thresholded
// the LAST-SWEEP INITIAL RESIDUAL at 1e-6, a threshold calibrated for an
// UNRELAXED final sweep -- and the unrelaxed final sweep is what diverged
// T25R_L1.  T25R2 relaxes it (system/coolant/fvSolution), which fixes the crash
// and DESTROYS that calibration.  The census is retained as a REPORT with no
// threshold; the outer loop is gated instead by DEMONSTRATED SWEEP-COUNT
// INDEPENDENCE, IN KELVIN, between this case at 10 sweeps and T25R2_L1_OC20 at
// 20.  MEASURED JUSTIFICATION (T25RF addendum A2): 5 sweeps against 10 differed
// by 6.02e-3 K after only 30 s of a 900 s case -- HALF the 10*PLANT signal
// scale -- AND WERE STILL DIVERGING.  10 sweeps is therefore DEMONSTRATED here,
// never assumed.
//
// THIS VALUE IS CHECKED AGAINST THE REGISTERED ONE BY analyse_t25R2's
// `numerics_check`, WHICH REFUSES ON A MISMATCH.  A swapped sweep count would
// make the section 3.5 gate meaningless while leaving every other check green.
PIMPLE
{
    nOuterCorrectors %d;
    nNonOrthogonalCorrectors 0;
}

// ************************************************************************* //
""" % A.NOUTER[case]


def fvsolution_coolant_text():
    """Section 3.4.  T25RF arm A2T, VERBATIM in every registered value:
    `T25RF_runs/A2T/system/coolant/fvSolution`."""
    return _HDR % ("system/coolant", "fvSolution") + """
solvers
{
    rho
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-08;
        relTol          0;
    }
    rhoFinal { $rho; relTol 0; }

    // *** THE p_rgh TOLERANCE IS 1e-8 AND 1e-9 IS UNREACHABLE. ***  MEASURED,
    // T25RF addendum A2: GAMG STALLS at ~4.4e-9 on this system.  266 of 600
    // p_rgh solves in the 5-sweep arm and 608 of 1200 in the 10-sweep arm
    // terminated at maxIter 1000 WITHOUT reaching 1e-9, and the waste GREW as
    // the field settled.  Relaxing one digit removed 601,763 GAMG iterations
    // (627,533 -> 25,770, 24.4x) and changed the last-sweep Min/max T at
    // Time = 30 by 0.000e+00 K -- 292.985283351 / 294.125534239 in both arms.
    // CLAUDE.md rule 12: that is WASTE, named, not absorbed into a cost ratio.
    "p_rgh.*"
    {
        solver          GAMG;
        tolerance       1e-08;
        relTol          0.01;
        smoother        GaussSeidel;
    }
    p_rghFinal
    {
        $p_rgh;
        tolerance       1e-08;
        relTol          0;
    }

    "(U|h|k|omega)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-10;
        relTol          0.01;
    }
    "(U|h|k|omega)Final"
    {
        $U;
        tolerance       1e-10;
        relTol          0;
    }
}

PIMPLE
{
    momentumPredictor true;
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
    // frozenFlow IS AVAILABLE at v2606 and IS DELIBERATELY NOT USED.  It would
    // stop solving momentum entirely and advance energy alone -- a STRONGER
    // approximation than section 3.3's quasi-steady framing.  T25RF arm A3 was
    // registered to reach for it only if A1 and A2 both failed; both held, A3
    // was NEVER REACHED and NEVER RUN, and no departure was taken.  Left at its
    // default false: the full momentum and turbulence equations are solved on
    // every outer sweep of every time step.  The flow field is SOLVED, not
    // imposed.
}

relaxationFactors
{
    // *** THIS BLOCK IS THE FIX FOR THE T25R_L1 DIVERGENCE, AND EVERY `Final`
    // KEY IS WRITTEN OUT LITERALLY. ***
    //
    // MECHANISM, read at v2606 source and then CONFIRMED BY MEASUREMENT (T25RF
    // arm A0 reproduced the crash under the NEW loads to the same three steps,
    // T0 = -14.458 against the reference run's -14.459, so the divergence is
    // NUMERICAL and not load-driven):
    //   chtMultiRegionFoam.C:111 sets finalIter on the last outer sweep;
    //   fvMatrix::relax() (fvMatrix.C:1249) looks its key up as
    //   psi_.select(isFinalIteration()); GeometricField::select(bool)
    //   (GeometricField.C:1179) returns name() + "Final".
    //   *** OPENFOAM KEYWORD REGEXES MATCH IN FULL, so T25R's
    //   "(U|h|k|omega)" DID NOT MATCH UFinal OR hFinal *** and momentum and
    //   energy ran UNRELAXED on the final sweep.  At Co ~ 1600 the 1/dt term
    //   adds almost nothing to the momentum diagonal, so that one unrelaxed
    //   sweep had no diagonal dominance left to stabilise it: continuity
    //   sum local went 3.609 -> 125.93 across sweeps 4 and 5 of Time = 1.0 and
    //   Min T fell from 288.21 to -73.54.
    //
    // A QUOTED REGEX IS NOT USED HERE EVEN THOUGH ONE WOULD MATCH.  The failure
    // being guarded against is a pattern that LOOKS like it matches and does
    // not; the registered form is decidable by reading, and analyse_t25R2's
    // `numerics_check` REFUSES a quoted key.
    fields
    {
        p_rgh       0.3;
        p_rghFinal  0.3;
    }
    equations
    {
        U           0.7;
        UFinal      0.7;
        h           0.7;
        hFinal      0.7;
        k           0.7;
        kFinal      0.7;
        omega       0.7;
        omegaFinal  0.7;
    }
}

// ************************************************************************* //
"""


def fvsolution_module_text():
    """Section 3.4.  T25RF arm A2T's solid dict, verbatim."""
    return _HDR % ("system/module", "fvSolution") + """
solvers
{
    h
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-12;
        relTol          0;
    }
    hFinal { $h; tolerance 1e-12; relTol 0; }
}

PIMPLE
{
    nNonOrthogonalCorrectors 0;
}

relaxationFactors { equations { h  1; } }

// ************************************************************************* //
"""


# ==========================================================================
# STAGING
# ==========================================================================

def stage(case, root=None, src_root=None):
    root = HERE if root is None else root
    src_root = SRC_ROOT if src_root is None else src_root
    if case not in SOURCE:
        refuse("%r is not a registered T25R2 case (section 1): %s"
               % (case, " ".join(sorted(SOURCE))))
    src = os.path.join(src_root, SOURCE[case])
    dst = os.path.join(root, case)

    if not os.path.isdir(src):
        refuse("the source mesh case %s does not exist. Section 2.5 registers "
               "REUSE of an already-built mesh; there is nothing to reuse"
               % src)
    if os.path.realpath(src) == os.path.realpath(dst):
        refuse("source and destination are the same directory")

    # --- GUARD: never stage over a case that has already run or been staged.
    if os.path.isdir(dst):
        stale = [x for x in os.listdir(dst)
                 if x == "0" or re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)
                 or x == "log.solve"]
        if stale:
            refuse("%s already holds %s. Rule 4's age guard dates the run "
                   "against 0/module/T and a pre-existing 0 or time directory "
                   "makes it unevaluable. This is REFUSED, never cleaned"
                   % (dst, ",".join(sorted(stale))))

    # --- THE SOURCE IS EVIDENCE.  Hash it before, and again after.
    before = _tree_digests(src, HASH_TREES)
    if not before:
        refuse("the source case %s holds no constant/ or 0.orig/ to reuse"
               % src)

    os.makedirs(dst, exist_ok=True)
    for t in COPY_TREES:
        s, d = os.path.join(src, t), os.path.join(dst, t)
        if not os.path.isdir(s):
            refuse("the source case has no %s/ -- it is not a staged case" % t)
        if os.path.isdir(d):
            shutil.rmtree(d)
        shutil.copytree(s, d, symlinks=True)
    for f in COPY_FILES:
        s = os.path.join(src, f)
        if not os.path.isfile(s):
            refuse("the source case has no %s. Section 2.4's mesh gate is "
                   "evaluated on that log and is not graded on trust" % f)
        shutil.copy2(s, os.path.join(dst, f))

    # --- THE REUSE PROOF.  Identical file sets, identical digests.
    after_src = _tree_digests(src, HASH_TREES)
    if after_src != before:
        refuse("THE SOURCE TREE CHANGED WHILE THIS SCRIPT RAN. %s is the record "
               "of the 04:09Z T25R divergence and is EVIDENCE; this script must "
               "be incapable of altering it" % src)
    got = _tree_digests(dst, HASH_TREES)
    if set(got) != set(before):
        only_s = sorted(set(before) - set(got))
        only_d = sorted(set(got) - set(before))
        refuse("the staged mesh is not the source mesh: %d file(s) missing "
               "(%s), %d extra (%s)" % (len(only_s), ",".join(only_s[:5]),
                                        len(only_d), ",".join(only_d[:5])))
    diff = sorted(k for k in before if before[k] != got[k])
    if diff:
        refuse("the staged mesh differs from the source at %d file(s): %s. "
               "Section 2.5 registers BYTE-IDENTICAL reuse and a difference is "
               "REFUSED" % (len(diff), ",".join(diff[:5])))

    # --- the cell counts the frozen document names, read from the mesh itself.
    counts = {}
    for region in ("module", "coolant"):
        p = os.path.join(dst, "constant", region, "polyMesh", "owner")
        if not os.path.isfile(p):
            refuse("no constant/%s/polyMesh/owner in the staged case" % region)
        n = _owner_count(p)
        want = CELLS[SOURCE[case]][region]
        if n != want:
            refuse("staged %s mesh holds %r cells, not the %d section 2.2 "
                   "registers for %s" % (region, n, want, SOURCE[case]))
        counts[region] = n

    # --- WHAT T25R2 OVERWRITES, AND ONLY THIS.
    written = []
    for rel, txt in (
            (os.path.join("constant", "module", "fvOptions"),
             fvoptions_text()),
            (os.path.join("system", "fvSolution"),
             fvsolution_top_text(case)),
            (os.path.join("system", "coolant", "fvSolution"),
             fvsolution_coolant_text()),
            (os.path.join("system", "module", "fvSolution"),
             fvsolution_module_text())):
        p = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(txt)
        written.append(rel)

    # --- THE WRITER IS GRADED BY THE READER, HERE, BEFORE ANYTHING IS LAUNCHED.
    nc = A.numerics_check(dst, case)
    pt = A.pulse_table_check(dst, case)
    mq = A.mesh_quality(dst)
    if not all(mq[r]["ok"] for r in A.REGIONS):
        refuse("the staged case fails the section 2.4 mesh gate: %r" % mq)

    print("STAGED  %-16s from %s" % (case, os.path.relpath(src, src_root)))
    print("  mesh REUSED and PROVED IDENTICAL: %d files under constant/ and "
          "0.orig/, sha256 for sha256, and the source tree is unchanged."
          % len(before))
    print("  cells: module %d + coolant %d = %d"
          % (counts["module"], counts["coolant"],
             counts["module"] + counts["coolant"]))
    for r in A.REGIONS:
        print("  checkMesh %-8s Mesh OK=%s maxNonOrth=%.4g maxSkew=%.4g -> OK"
              % (r, mq[r]["mesh_ok"], mq[r]["nonorth"], mq[r]["skew"]))
    print("  WROTE: %s" % ", ".join(written))
    print("  numerics VERIFIED by the comparator's own check: "
          "nOuterCorrectors %d, the five LITERAL final-sweep relaxation keys "
          "present, p_rgh tolerance %g."
          % (nc["nOuterCorrectors"], nc["p_rgh_tol"]))
    print("  pulse table VERIFIED: %r W/m3, no step time inside the ramp."
          % (pt["table"],))
    print("  NOTHING WAS EXECUTED. No blockMesh, no splitMeshRegions, no "
          "checkMesh, no solver.")
    return dict(case=case, source=SOURCE[case], cells=counts, wrote=written,
                hashed=len(before), numerics=nc)


# ==========================================================================
# SELFTEST.  Drives every refusal by mutation, on forged trees in scratch.
# ==========================================================================

def selftest():
    fails = 0

    def chk(name, cond):
        nonlocal fails
        print("  %-4s %s" % ("ok" if cond else "FAIL", name))
        if not cond:
            fails += 1

    def refuses(fn):
        try:
            fn()
        except SystemExit as e:
            return e.code == A.EXIT_REFUSE
        return False

    src = open(os.path.abspath(__file__)).read()
    code = src[src.index("import hashlib"):]
    banned = ["sub" + "process", "os." + "system", "os." + "exec",
              "os." + "popen", "os." + "spawn", "shutil." + "which"]
    hit = [t for t in banned if t in code]
    chk("*** THIS SCRIPT STARTS NO EXTERNAL PROGRAM *** -- none of the "
        "process-spawning names is anywhere in its code, so it CANNOT mesh or "
        "solve and cannot close this registration's gates "
        "(VERIFICATION_CHARTER 2d.2). Banned tokens found: %r" % hit, not hit)
    chk("the four registered cases map onto the three already-built meshes, "
        "and the two L1 arms share one",
        sorted(SOURCE) == sorted(A.CASES)
        and SOURCE["T25R2_L1"] == SOURCE["T25R2_L1_OC20"] == "T25R_L1")
    chk("the OC20 arm's dictionary differs from L1's ONLY in "
        "nOuterCorrectors: 20 against 10",
        A.NOUTER["T25R2_L1_OC20"] == 20 and A.NOUTER["T25R2_L1"] == 10
        and (fvsolution_top_text("T25R2_L1_OC20")
             .replace("nOuterCorrectors 20", "nOuterCorrectors 10")
             == fvsolution_top_text("T25R2_L1")))
    chk("the coolant dictionary carries all five LITERAL final-sweep "
        "relaxation keys, none of them quoted",
        all(re.search(r"^\s+%s\s+0\.[37];" % k, fvsolution_coolant_text(),
                      re.M) for k in A.RELAX_FINAL_KEYS))
    chk("the fvOptions table carries SANAA'S VOLUMETRIC LOADS and NOT T25R's",
        "100000.000000" in fvoptions_text()
        and "25000.000000" in fvoptions_text()
        and "70000" not in fvoptions_text()
        and "2800." not in fvoptions_text())

    root = tempfile.mkdtemp(prefix="t25R2stg_")
    try:
        # --- a forged SOURCE case: a real mesh, real dictionaries, real logs.
        sroot = os.path.join(root, "src")
        os.makedirs(sroot)
        fake_src = A._forge_case(sroot, "T25R2_L1", 0.5)
        os.rename(fake_src, os.path.join(sroot, "T25R_L1"))
        fake_src = os.path.join(sroot, "T25R_L1")
        os.makedirs(os.path.join(fake_src, "0.orig", "module"), exist_ok=True)
        open(os.path.join(fake_src, "0.orig", "module", "T"), "w").write("x\n")
        for f in COPY_FILES:
            p = os.path.join(fake_src, f)
            if not os.path.exists(p):
                open(p, "w").write("ok\n")
        # the forged mesh's real cell count, so the section 2.2 check is live
        real = {}
        for region in ("module", "coolant"):
            pm = os.path.join(fake_src, "constant", region, "polyMesh", "owner")
            txt = open(pm).read()
            n = 8 * 20 * 2 if region == "module" else 7 * 20
            open(pm, "w").write(txt.replace(
                "FoamFile{ version 2.0; }",
                "FoamFile{ version 2.0; note \"nCells: %d\"; }" % n))
            real[region] = n
        CELLS["T25R_L1"] = dict(real)

        droot = os.path.join(root, "dst")
        os.makedirs(droot)
        r = stage("T25R2_L1", root=droot, src_root=sroot)
        chk("a clean stage succeeds and proves the mesh identical file for "
            "file", r["hashed"] > 0 and r["cells"] == real)
        chk("the staged case carries the registered numerics",
            r["numerics"]["nOuterCorrectors"] == 10)
        chk("the OC20 arm stages from the SAME mesh at 20 sweeps",
            stage("T25R2_L1_OC20", root=droot,
                  src_root=sroot)["numerics"]["nOuterCorrectors"] == 20)
        chk("the two L1 arms' staged meshes are byte-identical",
            _tree_digests(os.path.join(droot, "T25R2_L1"), HASH_TREES)
            == _tree_digests(os.path.join(droot, "T25R2_L1_OC20"),
                             HASH_TREES))

        # --- NEGATIVE ARMS.
        chk("an unregistered case name REFUSES",
            refuses(lambda: stage("T25R2_L9", root=droot, src_root=sroot)))
        chk("a missing source mesh REFUSES rather than rebuild",
            refuses(lambda: stage("T25R2_L2", root=droot, src_root=sroot)))
        os.makedirs(os.path.join(droot, "T25R2_L1", "0"), exist_ok=True)
        chk("staging over a case that already holds `0` REFUSES -- rule 4's "
            "age guard would be unevaluable",
            refuses(lambda: stage("T25R2_L1", root=droot, src_root=sroot)))
        shutil.rmtree(os.path.join(droot, "T25R2_L1", "0"))
        open(os.path.join(droot, "T25R2_L1", "log.solve"), "w").write("End\n")
        chk("staging over a case that already holds a log.solve REFUSES -- "
            "that is a run's record, not a staging area",
            refuses(lambda: stage("T25R2_L1", root=droot, src_root=sroot)))
        os.remove(os.path.join(droot, "T25R2_L1", "log.solve"))
        CELLS["T25R_L1"] = {"module": real["module"] + 1,
                            "coolant": real["coolant"]}
        chk("a staged mesh whose cell count is not the registered one REFUSES",
            refuses(lambda: stage("T25R2_L1", root=os.path.join(root, "d2"),
                                  src_root=sroot)))
        CELLS["T25R_L1"] = dict(real)
        shutil.rmtree(os.path.join(fake_src, "0.orig"))
        chk("a source case with no 0.orig/ REFUSES",
            refuses(lambda: stage("T25R2_L1", root=os.path.join(root, "d3"),
                                  src_root=sroot)))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("SELFTEST %s (%d failed)" % ("PASS" if fails == 0 else "FAIL", fails))
    return EXIT_OK if fails == 0 else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = None
    if "--root" in argv:
        i = argv.index("--root")
        root = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    want = sorted(SOURCE) if "--all" in argv else [a for a in argv
                                                   if not a.startswith("-")]
    if not want:
        refuse("name a registered case, or --all. This script does not default "
               "to staging everything silently")
    for c in want:
        stage(c, root=root)
    return EXIT_OK


def _guarded(argv, _fn=None):
    """An uncaught traceback exits on the REFUSE path (2), never on a path a
    caller could mistake for success."""
    fn = main if _fn is None else _fn
    try:
        return fn(argv)
    except SystemExit:
        raise
    except BaseException:
        import traceback
        traceback.print_exc()
        print("REFUSE: stage_t25R2.py raised an uncaught exception. A CRASHED "
              "STAGER HAS STAGED NOTHING TRUSTWORTHY and exits 2.")
        return EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(_guarded(sys.argv[1:]))
