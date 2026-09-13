#!/usr/bin/env python3
"""DRIVAER R1 STAGE A -- write the solver case onto an already-built mesh level.

EVERY REFERENCE QUANTITY IS READ FROM THE PINNED REFERENCE FILE, never typed here.
That is the whole point: `grade_drivaer.py` asserts the on-disk forceCoeffs constants
against that same file, so if this script held its own literals the two could disagree
and the assertion would be comparing one lane's typo with another's.  Tonight two
separate cases -- the CRM's `Aref 1.0` on an inch mesh and the Ahmed's factor-3.586
planform/frontal rebase -- were reference-quantity errors that would have produced
confident wrong drag.

It writes `0.orig/`, NEVER `0/`.  The launcher copies 0.orig -> 0 at launch so the
rule-4 age guard dates the run; a `0/` written now would date the SETUP and the guard
would pass on stale fields.  REFUSES if `0/` or any time directory already exists.
"""
from __future__ import annotations
import argparse, json, os, re, shutil, sys
from pathlib import Path

DOMAIN_PATCHES = ("inlet", "outlet", "floorSlip", "floorNoSlip",
                  "top", "sideMinus", "sidePlus")
SLIP_PATCHES = ("floorSlip", "top", "sideMinus", "sidePlus")
TURB_INTENSITY = 0.001      # 0.1% -- open-road freestream (Spalart-Rumsey 2007 class)
NUT_RATIO = 1.0             # nut_inf / nu


def head(cls, obj, loc):
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            f"    class {cls};\n    location \"{loc}\";\n    object {obj};\n}}\n")


def boundary_patches(root: Path):
    txt = (root / "constant" / "polyMesh" / "boundary").read_text(errors="replace")
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    txt = txt[txt.index("}", txt.index("FoamFile")) + 1:]
    txt = txt[txt.index("("):]
    return [m.group(1) for m in re.finditer(r"(\S+)\s*\{[^}]*nFaces", txt)]


def field(obj, cls, dims, internal, bcs, vehicle):
    b = [f"    {n}\n    {{\n{v}    }}\n" for n, v in bcs]
    b.append("    \".*\"\n    {\n" + vehicle + "    }\n")
    return (head(cls, obj, "0") +
            f"\ndimensions      {dims};\n\ninternalField   uniform {internal};\n\n"
            "boundaryField\n{\n" + "".join(b) + "}\n")



NUT_WALL_RE = re.compile(r"\bnut[A-Za-z]*WallFunction\b")


def assert_nut_treatments(text, vehicle, floor):
    """COUNT the nut wall-function tokens on disk; never merely look for them.

    A PRESENCE check cannot work here.  In the normal case the two treatments
    DIFFER -- Spalding on the vehicle, nutk on the floor, which is what R5
    registers -- so both strings are legitimately present and `X in text` is
    satisfied by a STALE THIRD OCCURRENCE as readily as by the right one.
    That is L-607's shape (one hit is a value, several hits are a hierarchy)
    in the very script written to prevent it.

    This writer emits EXACTLY TWO wall-function blocks: floorNoSlip, and the
    ".*" default.  So the expected multiset is known exactly and is derived
    from the arguments, never hardcoded -- a hardcoded count taken from some
    other artifact would refuse every case this script writes, and a guard
    that refuses lawful work is a defect too.

    Returns the measured counts so the caller can RECORD them as evidence.
    """
    from collections import Counter
    want = Counter([vehicle, floor])
    got = Counter(NUT_WALL_RE.findall(text))
    if got != want:
        raise SystemExit(
            "REFUSE: 0.orig/nut does not carry exactly the requested wall "
            "treatments.\n"
            f"  requested (vehicle={vehicle}, floor={floor}): {dict(want)}\n"
            f"  found on disk:                                {dict(got)}\n"
            "  A count mismatch means a stale literal survived, a block was "
            "written twice, or a spelling nobody asked for is present. "
            "Presence alone would not have caught this.")
    return dict(got)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--end-time", type=int, default=3000)
    # WALL TREATMENT IS STATED, NEVER DEFAULTED.  A default is what let R5 stage
    # from a case carrying nutkWallFunction while its registration said
    # nutUSpaldingWallFunction: the R2c arm got Spalding as a registered
    # one-change and every arm after inherited nutk in silence.  Both are
    # required with NO default, so this script REFUSES to write a case whose
    # wall treatment nobody stated.  The value lived at two hardcoded sites and
    # one of them always won -- L-607's shape -- so each now has one decision.
    ap.add_argument("--nut-wall-vehicle", required=True,
                    choices=("nutkWallFunction", "nutUSpaldingWallFunction"),
                    help="nut wall function on the \".*\" vehicle block. "
                         "The registration names it; this script does not guess.")
    ap.add_argument("--nut-wall-floor", required=True,
                    choices=("nutkWallFunction", "nutUSpaldingWallFunction"),
                    help="nut wall function on floorNoSlip. Stated separately "
                         "because it legitimately differs from the vehicle.")
    ap.add_argument("--write-interval", type=int, default=1000)
    a = ap.parse_args()
    root = Path(a.root)
    if not (root / "constant" / "polyMesh" / "boundary").is_file():
        raise SystemExit(f"REFUSE: no built mesh at {root}")
    if (root / "0.orig").exists():
        raise SystemExit(f"REFUSE: {root}/0.orig already exists. This script never "
                         f"overwrites a written case; move it aside by hand if you "
                         f"mean to rewrite it.")
    if (root / "0").exists():
        raise SystemExit(f"REFUSE: {root}/0 already exists. This script writes 0.orig "
                         f"only; a pre-existing 0/ would defeat the rule-4 age guard.")
    times = [d for d in os.listdir(root)
             if re.fullmatch(r"\d+(\.\d+)?", d) and d != "0" and (root / d).is_dir()]
    if times:
        raise SystemExit(f"REFUSE: {root} already holds time directories {sorted(times)}")

    ref = json.load(open(a.reference))["reference"]
    need = ("magUInf_m_s", "L_ref_m", "Aref_m2", "rho_kg_m3", "nu_m2_s", "CofR_m")
    for k in need:
        if ref.get(k) is None:
            raise SystemExit(f"REFUSE: reference {a.reference}: '{k}' absent or null")
    U, lRef, Aref = float(ref["magUInf_m_s"]), float(ref["L_ref_m"]), float(ref["Aref_m2"])
    rho, nu = float(ref["rho_kg_m3"]), float(ref["nu_m2_s"])
    cofr = [float(x) for x in ref["CofR_m"]]

    pats = boundary_patches(root)
    missing = [d for d in DOMAIN_PATCHES if d not in pats]
    if missing:
        raise SystemExit(f"REFUSE: domain patches missing from the mesh: {missing}")
    vehicle = [p for p in pats if p not in DOMAIN_PATCHES]
    if not vehicle:
        raise SystemExit("REFUSE: no vehicle patches on this mesh")

    k_in = 1.5 * (U * TURB_INTENSITY) ** 2
    nut_in = NUT_RATIO * nu
    omega_in = k_in / nut_in

    (root / "0.orig").mkdir()
    slip = "|".join(SLIP_PATCHES)
    def blk(*lines): return "".join(f"        {l}\n" for l in lines)

    (root / "0.orig" / "U").write_text(field(
        "U", "volVectorField", "[0 1 -1 0 0 0 0]", f"({U} 0 0)",
        [("inlet", blk("type            fixedValue;", f"value           uniform ({U} 0 0);")),
         ("outlet", blk("type            inletOutlet;", "inletValue      uniform (0 0 0);",
                        f"value           uniform ({U} 0 0);")),
         (f'"({slip})"', blk("type            slip;")),
         ("floorNoSlip", blk("type            noSlip;"))],
        blk("type            noSlip;")))

    (root / "0.orig" / "p").write_text(field(
        "p", "volScalarField", "[0 2 -2 0 0 0 0]", "0",
        [("inlet", blk("type            zeroGradient;")),
         ("outlet", blk("type            fixedValue;", "value           uniform 0;")),
         (f'"({slip})"', blk("type            slip;")),
         ("floorNoSlip", blk("type            zeroGradient;"))],
        blk("type            zeroGradient;")))

    (root / "0.orig" / "k").write_text(field(
        "k", "volScalarField", "[0 2 -2 0 0 0 0]", f"{k_in:.8g}",
        [("inlet", blk("type            fixedValue;", f"value           uniform {k_in:.8g};")),
         ("outlet", blk("type            inletOutlet;", f"inletValue      uniform {k_in:.8g};",
                        f"value           uniform {k_in:.8g};")),
         (f'"({slip})"', blk("type            slip;")),
         ("floorNoSlip", blk("type            kqRWallFunction;",
                             f"value           uniform {k_in:.8g};"))],
        blk("type            kqRWallFunction;", f"value           uniform {k_in:.8g};")))

    (root / "0.orig" / "omega").write_text(field(
        "omega", "volScalarField", "[0 0 -1 0 0 0 0]", f"{omega_in:.8g}",
        [("inlet", blk("type            fixedValue;", f"value           uniform {omega_in:.8g};")),
         ("outlet", blk("type            inletOutlet;", f"inletValue      uniform {omega_in:.8g};",
                        f"value           uniform {omega_in:.8g};")),
         (f'"({slip})"', blk("type            slip;")),
         ("floorNoSlip", blk("type            omegaWallFunction;",
                             f"value           uniform {omega_in:.8g};"))],
        blk("type            omegaWallFunction;", f"value           uniform {omega_in:.8g};")))

    (root / "0.orig" / "nut").write_text(field(
        "nut", "volScalarField", "[0 2 -1 0 0 0 0]", f"{nut_in:.8g}",
        [("inlet", blk("type            calculated;", f"value           uniform {nut_in:.8g};")),
         ("outlet", blk("type            calculated;", f"value           uniform {nut_in:.8g};")),
         (f'"({slip})"', blk("type            slip;")),
         ("floorNoSlip", blk(f"type            {a.nut_wall_floor};",
                             "value           uniform 0;"))],
        blk(f"type            {a.nut_wall_vehicle};", "value           uniform 0;")))

    # READ BACK FROM DISK AND COUNT (rule 3).  An argument that was accepted is
    # not evidence the bytes carry it, and a file saying "Spalding requested" is
    # the same class of artifact as the accepted argument.  The counts are.
    counts = assert_nut_treatments((root / "0.orig" / "nut").read_text(),
                                   a.nut_wall_vehicle, a.nut_wall_floor)
    (root / "WALL_TREATMENT_AS_REQUESTED.txt").write_text(
        f"nut_wall_vehicle={a.nut_wall_vehicle}\n"
        f"nut_wall_floor={a.nut_wall_floor}\n"
        "stated on the command line; no default exists in this script\n"
        "counts ASSERTED against the written bytes of 0.orig/nut:\n"
        + "".join(f"  {k}={v}\n" for k, v in sorted(counts.items()))
        + "  any other nut*WallFunction spelling=0 (asserted by exact "
          "multiset equality, not by presence)\n")

    (root / "constant" / "transportProperties").write_text(
        head("dictionary", "transportProperties", "constant") +
        f"\ntransportModel  Newtonian;\nnu              {nu:.8g};\n")
    (root / "constant" / "turbulenceProperties").write_text(
        head("dictionary", "turbulenceProperties", "constant") +
        "\nsimulationType  RAS;\n\nRAS\n{\n    RASModel        kOmegaSST;\n"
        "    turbulence      on;\n    printCoeffs     on;\n}\n")

    plist = "\n".join(f"        {p}" for p in vehicle)
    (root / "system" / "forceCoeffs").write_text(f"""// DRIVAER R1 STAGE A -- forceCoeffs.
// EVERY constant below was read from the pinned reference file, not typed:
//   {a.reference}
// PER-GEOMETRY convention (geo_ref_466.csv + force_mom_466.csv).  The dataset also
// ships a NOMINAL basis (Aref 2.17, lRef 2.78618) whose Cd differs by 5.57%.  Mixing
// them is the single most expensive error available on this case.
// rhoInf is the paper's Table 3 value, 1 kg/m3 -- NOT 1.225.  In incompressible
// OpenFOAM it cancels between force and dynamic pressure, but grade_drivaer.py
// asserts it on disk against the same file, so it must be the upstream value.
// patches: ALL {len(vehicle)} vehicle patches (every patch that is not a domain patch).
forceCoeffs1
{{
    type            forceCoeffs;
    libs            (forces);
    writeControl    timeStep;
    writeInterval   1;
    log             yes;
    patches
    (
{plist}
    );
    rho             rhoInf;
    rhoInf          {rho:.8g};
    magUInf         {U:.8g};
    lRef            {lRef:.8g};
    Aref            {Aref:.8g};
    CofR            ({cofr[0]:.8g} {cofr[1]:.8g} {cofr[2]:.8g});
    liftDir         (0 0 1);
    dragDir         (1 0 0);
    pitchAxis       (0 1 0);
}}
""")

    for nm in ("controlDict", "fvSchemes", "fvSolution"):
        src = root / "system" / nm
        if src.is_file() and not (root / "system" / (nm + ".meshbuild")).exists():
            shutil.copy2(src, root / "system" / (nm + ".meshbuild"))

    (root / "system" / "controlDict").write_text(
        head("dictionary", "controlDict", "system") + f"""
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {a.end_time};
deltaT          1;
writeControl    timeStep;
writeInterval   {a.write_interval};
purgeWrite      0;
writeFormat     ascii;          // grade_drivaer.py plants into and re-reads 0/p and
writePrecision  10;             // <time>/p as TEXT; binary would defeat the control
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;

// NO residualControl, DELIBERATELY: the run must reach endTime so that
// last == endTime and the ExecutionTime count == round(endTime/deltaT).  Iterative
// convergence is judged by the grader from the final Initial residuals, not by an
// early solver stop.

functions
{{
    #include "forceCoeffs"
}}
""")
    (root / "system" / "fvSchemes").write_text(
        head("dictionary", "fvSchemes", "system") + """
ddtSchemes      { default steadyState; }
gradSchemes     { default cellLimited Gauss linear 1; }
divSchemes
{
    default                       none;
    div(phi,U)                    bounded Gauss linearUpwind grad(U);
    div(phi,k)                    bounded Gauss limitedLinear 1;
    div(phi,omega)                bounded Gauss limitedLinear 1;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes     { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes        { default corrected; }
wallDist             { method meshWave; }
""")
    (root / "system" / "fvSolution").write_text(
        head("dictionary", "fvSolution", "system") + """
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-8;
        relTol          0.01;
        smoother        GaussSeidel;
        nPreSweeps      0;
        nPostSweeps     2;
        cacheAgglomeration true;
        nCellsInCoarsestLevel 100;
        agglomerator    faceAreaPair;
        mergeLevels     1;
    }
    "(U|k|omega)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-9;
        relTol          0.01;
        nSweeps         1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    consistent               yes;
}

relaxationFactors { equations { U 0.9; ".*" 0.9; } }
""")

    meta = dict(level_root=str(root), reference=a.reference,
                magUInf=U, lRef=lRef, Aref=Aref, rhoInf=rho, nu=nu, CofR=cofr,
                k_inlet=k_in, omega_inlet=omega_in, nut_inlet=nut_in,
                turbulence_intensity=TURB_INTENSITY, nut_ratio=NUT_RATIO,
                endTime=a.end_time, writeInterval=a.write_interval,
                n_vehicle_patches=len(vehicle), vehicle_patches=vehicle,
                domain_patches=list(DOMAIN_PATCHES))
    (root / "SOLVER_CASE_SPEC.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps({k: v for k, v in meta.items() if k != "vehicle_patches"}, indent=1))


if __name__ == "__main__":
    main()
