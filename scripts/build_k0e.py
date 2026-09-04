#!/usr/bin/env python3
"""build_k0e.py -- build ONE K0e arm from the recorded TMR flat-plate reference.

K0e (campaign F14, cooling ladder) is the forced-convection flat plate registered
in docs/campaigns/F14-cooling-ladder/K0e_PREREGISTRATION.md.  This script builds
a buoyantBoussinesqSimpleFoam case that is IDENTICAL to the recorded simpleFoam
reference in mesh, decomposition, schemes and linear-solver settings, and differs
from it ONLY by the thermal fields and by the solver binary.

WHY IT COPIES THE DECOMPOSED MESH RATHER THAN RE-DECOMPOSING
------------------------------------------------------------
M4 (the momentum control) compares this arm's processor-local U at endTime with
the reference's processor-local U at endTime, cell for cell.  That comparison is
only meaningful if the two cases carry the SAME decomposition.  Re-running
`decomposePar` with `method scotch` would re-derive a decomposition rather than
reproduce one, so this script COPIES processorN/constant/polyMesh (including
cellProcAddressing / faceProcAddressing / pointProcAddressing /
boundaryProcAddressing) from the reference and then runs `decomposePar -fields`,
which maps fields onto the EXISTING processor meshes and derives nothing.

THE AGE GUARD (standing rule 4) IS ENFORCED HERE AND REFUSES
------------------------------------------------------------
The script REFUSES (exit 2) if the target case already holds `0/` or any numeric
time directory.  A run is never built into a tree that already holds an answer.

Nothing here grades anything.  No verdict is assigned by this file.
"""

import sys

# No .pyc may land beside a pinned build path: a stale __pycache__ has been
# measured to invert a mutation test in this lab (clean control failing while
# the mutated case passed).  PYTHONDONTWRITEBYTECODE set in the environment is
# not relied on, because this file may be invoked by a launcher that does not
# set it.
sys.dont_write_bytecode = True

import argparse
import os
import re
import shutil
import subprocess

EXIT_REFUSE = 2

# ---------------------------------------------------------------------------
# THE REGISTERED PHYSICS.  These constants are the pre-registration's, and this
# file is committed WITH the pre-registration that fixes them (rule 2).
# ---------------------------------------------------------------------------
NU = "2e-07"          # m2/s, the reference's own value (constant/transportProperties)
BETA = "0"            # 1/K -- buoyancy removed exactly
TREF = "300"          # K
PR = "0.71"           # air
PRT = "0.85"          # the thermal ladder's value
G_VECTOR = "(0 0 0)"  # buoyancy removed again, independently

ARMS = {
    # arm id      T_inf,  T_wall
    "FP_T10": ("300", "310"),   # thermal arm, dT = 10 K
    "FP_T00": ("300", "300"),   # zero-dT control, dT = 0 K exactly -- K0eR2's,
                                # RETIRED by K0eR3 as degenerate by design and
                                # KEPT HERE so the rule-14 guard below has a
                                # baseline to check against.  K0eR3 does not
                                # build it.
    # ---- INSERTED BY K0eR3, NEVER REPLACING AN ENTRY (standing rule 14) -----
    "FP_T290": ("300", "290"),  # cooled arm, dT = -10 K.  M4b's second operand.
    "D0_A": ("300", "310"),     # determinism twin A -- IDENTICAL spec to FP_T10
    "D0_B": ("300", "310"),     # determinism twin B -- IDENTICAL spec to D0_A
}

# STANDING RULE 14: a libs/table entry is INSERTED WITH AN ASSERT, NEVER
# REPLACED, and the lesson is not applied until EVERY CALL SITE asserts it.
# This baseline is the K0eR2-registered content of ARMS, frozen at
# docs/campaigns/F14-cooling-ladder/K0eR2_PREREGISTRATION.md section 4.3.  The
# check below is an EXPLICIT REFUSAL WITH A MESSAGE and not a bare `assert`
# (L-332): a bare assert vanishes under `python -O` and takes the guard with it.
ARMS_BASELINE_K0eR2 = {
    "FP_T10": ("300", "310"),
    "FP_T00": ("300", "300"),
}

# The K0eR3 determinism twins must remain BYTE-IDENTICAL in spec to each other
# and to FP_T10, or D0 stops being a determinism test and becomes a comparison
# of two different problems.
D0_TWINS = ("D0_A", "D0_B")

REF_DEFAULT = "/home/ubuntu/certonomous-runs/tmr-flatplate-finer"
REG_END_TIME_DEFAULT = 9000

HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
| K0e arm field, written by scripts/build_k0e.py                              |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "{loc}";
    object      {obj};
}}
"""


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def arms_intact_or_refuse():
    """STANDING RULE 14, AT EVERY CALL SITE.

    The K0eR3 arms were INSERTED into ARMS.  This refuses if that insertion
    ever becomes a replacement -- if a baseline entry disappears, or if its
    registered (T_inf, T_wall) pair moves.  A silent replacement would rebuild
    a K0eR2 arm at a K0eR3 temperature and nothing downstream would notice.

    It also refuses if the two determinism twins ever stop being identical to
    each other or to FP_T10, because D0 is only a determinism test while they
    are the SAME problem run twice."""
    for name, spec in sorted(ARMS_BASELINE_K0eR2.items()):
        if name not in ARMS:
            refuse(f"standing rule 14: registered arm {name!r} has been REMOVED "
                   f"from ARMS.  The K0eR3 arms were inserted, never as a "
                   f"replacement; refusing rather than building against a table "
                   f"that no longer matches the registration.")
        if ARMS[name] != spec:
            refuse(f"standing rule 14: registered arm {name!r} now reads "
                   f"{ARMS[name]!r} where the K0eR2 registration fixes {spec!r}. "
                   f"An entry was REPLACED, not inserted; refusing.")
    for twin in D0_TWINS:
        if twin not in ARMS:
            refuse(f"standing rule 14: determinism twin {twin!r} is absent from "
                   f"ARMS; D0 cannot be built.")
        if ARMS[twin] != ARMS["FP_T10"]:
            refuse(f"D0 twin {twin!r} reads {ARMS[twin]!r} where FP_T10 reads "
                   f"{ARMS['FP_T10']!r}.  The twins must be the SAME problem as "
                   f"each other and as FP_T10, or D0 measures a difference in "
                   f"the problem rather than in the solver; refusing.")
    if ARMS[D0_TWINS[0]] != ARMS[D0_TWINS[1]]:
        refuse(f"the two D0 twins differ: {ARMS[D0_TWINS[0]]!r} vs "
               f"{ARMS[D0_TWINS[1]]!r}.  D0 would then be a comparison of two "
               f"different problems and could not test determinism; refusing.")


def is_time_dir(name):
    return bool(re.fullmatch(r"[0-9]+(\.[0-9]+)?", name))


def age_guard_refuse_if_answered(case):
    """Standing rule 4's guard: refuse a case that already holds an answer."""
    if not os.path.isdir(case):
        return
    for entry in sorted(os.listdir(case)):
        if entry == "0" or is_time_dir(entry):
            refuse(f"{case}/{entry} already exists.  Standing rule 4's guard "
                   f"refuses a case where 0/ or a time directory is already "
                   f"present -- a run is never built into a tree that already "
                   f"holds an answer.")
    for p in sorted(os.listdir(case)):
        if p.startswith("processor"):
            for entry in sorted(os.listdir(os.path.join(case, p))):
                if entry == "0" or is_time_dir(entry):
                    refuse(f"{case}/{p}/{entry} already exists -- same guard, "
                           f"on the decomposed side.")


def read_boundary_patch_block(path, patch):
    """Return the raw text of one patch block in a field file's boundaryField.

    Used to carry the reference's OWN boundary conditions across unchanged --
    a hand-retyped boundary condition is a silent physics change."""
    with open(path) as fh:
        txt = fh.read()
    m = re.search(r"\n(\s*)" + re.escape(patch) + r"\s*\n\s*\{(.*?)\n\1\}",
                  txt, re.S)
    if not m:
        refuse(f"{path}: patch block {patch!r} not found; refusing rather than "
               f"inventing a boundary condition.")
    return m.group(2)


def write_field(case, tdir, obj, cls, dims, internal, patches):
    path = os.path.join(case, tdir, obj)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(HEADER.format(cls=cls, loc=tdir, obj=obj))
        fh.write(f"\ndimensions      {dims};\n\n")
        fh.write(f"internalField   uniform {internal};\n\n")
        fh.write("boundaryField\n{\n")
        for name, body in patches:
            fh.write(f"    {name}\n    {{\n")
            for line in body:
                fh.write(f"        {line}\n")
            fh.write("    }\n")
        fh.write("}\n")
    return path


def build(arm, ref, out_root, foam_bashrc, end_time=REG_END_TIME_DEFAULT):
    arms_intact_or_refuse()   # STANDING RULE 14 -- CALL SITE 1 of 2
    if arm not in ARMS:
        refuse(f"unknown arm {arm!r}; registered arms are {sorted(ARMS)}")
    if not isinstance(end_time, int) or end_time <= 0:
        refuse(f"--end-time must be a positive integer; got {end_time!r}")
    t_inf, t_wall = ARMS[arm]
    case = os.path.join(out_root, arm)

    if not os.path.isdir(ref):
        refuse(f"reference case {ref} does not exist")
    ref_procs = sorted(d for d in os.listdir(ref) if d.startswith("processor"))
    if not ref_procs:
        refuse(f"{ref}: no processor directories; the registered comparison is "
               f"processor-local and cannot be built without them.")

    age_guard_refuse_if_answered(case)
    os.makedirs(case, exist_ok=True)

    # ---- mesh and decomposition, COPIED, never re-derived --------------
    shutil.copytree(os.path.join(ref, "constant", "polyMesh"),
                    os.path.join(case, "constant", "polyMesh"),
                    dirs_exist_ok=True)
    for p in ref_procs:
        shutil.copytree(os.path.join(ref, p, "constant", "polyMesh"),
                        os.path.join(case, p, "constant", "polyMesh"),
                        dirs_exist_ok=True)

    # ---- system/, copied verbatim except controlDict --------------------
    os.makedirs(os.path.join(case, "system"), exist_ok=True)
    for f in ("decomposeParDict", "blockMeshDict"):
        src = os.path.join(ref, "system", f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(case, "system", f))

    # fvSchemes: the reference's, PLUS the one entry it could not carry.
    #
    # The reference is a simpleFoam case.  It solves no energy equation, so its
    # divSchemes has no `div(phi,T)` and its `default none;` makes the omission
    # fatal rather than silent -- buoyantBoussinesqSimpleFoam refuses to start
    # (measured: rc=1 in 0 wall s, FOAM FATAL IO ERROR, attempt 1 preserved at
    # K0e_runs/FP_T10.attempt1_MISSING_div_phi_T_FAILED).
    #
    # THE SCHEME IS THE LADDER'S OWN, NOT THIS FILE'S CHOICE.  `bounded Gauss
    # limitedLinear 1` is what K0f (M1_c/system/fvSchemes line 22) and K0cS
    # (S_SST_c/system/fvSchemes line 28) register for div(phi,T).  K0e exists to
    # be comparable to those rungs, so it adopts their scheme rather than
    # inventing one.
    #
    # IT DOES NOT TOUCH ANY MOMENTUM-RELEVANT SCHEME.  div(phi,U), gradSchemes,
    # laplacianSchemes, snGradSchemes and interpolationSchemes are copied
    # byte-unchanged, so M4 -- the only gated row -- is unaffected by this edit.
    with open(os.path.join(ref, "system", "fvSchemes")) as fh:
        fvsch = fh.read()
    if "div(phi,T)" in fvsch:
        refuse("the reference fvSchemes already carries div(phi,T); refusing "
               "rather than inserting a second, possibly conflicting entry")
    fvsch2 = fvsch.replace(
        "    div(phi,U)                      bounded Gauss linearUpwind grad(U);",
        "    div(phi,U)                      bounded Gauss linearUpwind grad(U);\n"
        "    div(phi,T)                      bounded Gauss limitedLinear 1;")
    if "div(phi,T)" not in fvsch2:
        refuse("fvSchemes edit did not take: no div(phi,T) entry was produced. "
               "Refusing rather than starting a solver that cannot discretise "
               "its own energy equation.")
    if fvsch2.count("div(phi,U)") != fvsch.count("div(phi,U)"):
        refuse("fvSchemes edit changed the div(phi,U) entry count; refusing "
               "rather than running with a momentum scheme this edit touched")
    with open(os.path.join(case, "system", "fvSchemes"), "w") as fh:
        fh.write(fvsch2)

    # fvSolution: the reference's, with `p` renamed to `p_rgh` and T added.
    # The rename is the ONLY change to the momentum-relevant settings, and it is
    # a rename of a key, not a change of a value.
    with open(os.path.join(ref, "system", "fvSolution")) as fh:
        fvsol = fh.read()
    fvsol = fvsol.replace("\n    p\n", "\n    p_rgh\n")
    fvsol = fvsol.replace("        p               1e-06;",
                          "        p_rgh           1e-06;")
    fvsol = fvsol.replace("fields    { p 0.3; }", "fields    { p_rgh 0.3; }")
    fvsol = fvsol.replace('"(U|k|omega)"', '"(U|k|omega|T)"')
    fvsol = fvsol.replace("equations { U 0.7; k 0.7; omega 0.7; }",
                          "equations { U 0.7; k 0.7; omega 0.7; T 0.7; }")
    if "p_rgh" not in fvsol:
        refuse("fvSolution rewrite did not take: no p_rgh entry was produced. "
               "Refusing rather than running with the reference's own p entry, "
               "which buoyantBoussinesqSimpleFoam would ignore.")
    with open(os.path.join(case, "system", "fvSolution"), "w") as fh:
        fh.write(fvsol)

    # controlDict: the reference's endTime / write settings, new application.
    with open(os.path.join(ref, "system", "controlDict")) as fh:
        cd = fh.read()
    cd = cd.replace("application     simpleFoam;",
                    "application     buoyantBoussinesqSimpleFoam;")
    if "buoyantBoussinesqSimpleFoam" not in cd:
        refuse("controlDict rewrite did not take")
    # endTime, and writeInterval WITH IT.  The reference carries
    # `endTime 9000; writeInterval 9000;`, so a shortened run that moved only
    # endTime would write NO FIELDS AT ALL and produce a case the completion
    # rule could never pass.  Both are rewritten together, and both rewrites
    # are verified rather than trusted.
    if end_time != REG_END_TIME_DEFAULT:
        cd2 = re.sub(r"(?m)^endTime\s+[0-9]+\s*;\s*$",
                     f"endTime         {end_time};", cd)
        cd2 = re.sub(r"(?m)^writeInterval\s+[0-9]+\s*;\s*$",
                     f"writeInterval   {end_time};", cd2)
        if not re.search(r"(?m)^endTime\s+%d\s*;\s*$" % end_time, cd2):
            refuse(f"controlDict endTime rewrite to {end_time} did not take; "
                   f"refusing rather than running to the reference's own "
                   f"endTime under a registration that asked for {end_time}.")
        if not re.search(r"(?m)^writeInterval\s+%d\s*;\s*$" % end_time, cd2):
            refuse(f"controlDict writeInterval rewrite to {end_time} did not "
                   f"take.  A run whose writeInterval exceeds its endTime "
                   f"writes no fields and can never satisfy clause 4 of the "
                   f"strict completion rule; refusing.")
        cd = cd2
    if "writeCompression" not in cd:
        cd = cd.replace("writeFormat     ascii;",
                        "writeFormat     ascii;\nwriteCompression off;")
    with open(os.path.join(case, "system", "controlDict"), "w") as fh:
        fh.write(cd)

    # ---- constant/ ------------------------------------------------------
    shutil.copy2(os.path.join(ref, "constant", "turbulenceProperties"),
                 os.path.join(case, "constant", "turbulenceProperties"))
    # The mesh's birth certificate travels WITH the mesh, so the case carries
    # its own measured quality figures and the grader never has to reach into
    # another directory to learn whether this mesh is orthogonal.
    bc = os.path.join(ref, "constant", "birth_certificate.json")
    if os.path.isfile(bc):
        shutil.copy2(bc, os.path.join(case, "constant", "birth_certificate.json"))
    else:
        refuse(f"{bc} missing: the grader asserts the mesh's MEASURED "
               f"non-orthogonality before it reads any wall gradient, and it "
               f"cannot do that from a mesh with no birth certificate.")
    with open(os.path.join(case, "constant", "transportProperties"), "w") as fh:
        fh.write(HEADER.format(cls="dictionary", loc="constant",
                               obj="transportProperties"))
        fh.write("\ntransportModel  Newtonian;\n\n")
        fh.write(f"nu              {NU};\n")
        fh.write(f"beta            {BETA};\n")
        fh.write(f"TRef            {TREF};\n")
        fh.write(f"Pr              {PR};\n")
        fh.write(f"Prt             {PRT};\n")
    with open(os.path.join(case, "constant", "g"), "w") as fh:
        fh.write(HEADER.format(cls="uniformDimensionedVectorField",
                               loc="constant", obj="g"))
        fh.write("\ndimensions      [0 1 -2 0 0 0 0];\n")
        fh.write(f"value           {G_VECTOR};\n")

    # ---- 0/ : momentum fields copied verbatim from the reference --------
    os.makedirs(os.path.join(case, "0"), exist_ok=True)
    for f in ("U", "k", "nut", "omega"):
        shutil.copy2(os.path.join(ref, "0", f), os.path.join(case, "0", f))
    # p_rgh and p carry the reference's OWN p boundary conditions.
    with open(os.path.join(ref, "0", "p")) as fh:
        ptxt = fh.read()
    for obj in ("p", "p_rgh"):
        out = ptxt.replace("object      p;", f"object      {obj};")
        with open(os.path.join(case, "0", obj), "w") as fh:
            fh.write(out)

    # T: the arm's thermal boundary condition.
    write_field(
        case, "0", "T", "volScalarField", "[0 0 0 1 0 0 0]", t_inf,
        [("inlet", [f"type            fixedValue;",
                    f"value           uniform {t_inf};"]),
         ("outlet", ["type            zeroGradient;"]),
         ("top", ["type            zeroGradient;"]),
         ("bottomSym", ["type            symmetry;"]),
         ("plate", [f"type            fixedValue;",
                    f"value           uniform {t_wall};"]),
         ("frontAndBack", ["type            empty;"])])

    # alphat: WALL-RESOLVED.  y+ max on this mesh is 0.209 (reference
    # postProcessing/yPlus1/0/yPlus.dat), and nut carries nutLowReWallFunction,
    # so nut_wall = 0 and alphat_wall = nut_wall/Prt = 0.  A Jayatilleke wall
    # function here would impose a high-Re thermal law on a resolved wall.
    write_field(
        case, "0", "alphat", "volScalarField", "[0 2 -1 0 0 0 0]", "0",
        [("inlet", ["type            calculated;", "value           uniform 0;"]),
         ("outlet", ["type            calculated;", "value           uniform 0;"]),
         ("top", ["type            calculated;", "value           uniform 0;"]),
         ("bottomSym", ["type            symmetry;"]),
         ("plate", ["type            calculated;", "value           uniform 0;"]),
         ("frontAndBack", ["type            empty;"])])

    # ---- decompose the fields onto the COPIED processor meshes ----------
    cmd = (f"source {foam_bashrc} >/dev/null 2>&1 && cd {case} && "
           f"decomposePar -fields -force > log.decomposePar 2>&1")
    rc = subprocess.call(["bash", "-lc", cmd])
    if rc != 0:
        refuse(f"decomposePar -fields returned {rc}; see {case}/log.decomposePar")

    need = {"U", "k", "nut", "omega", "p", "p_rgh", "T", "alphat"}
    for p in ref_procs:
        have = set(os.listdir(os.path.join(case, p, "0")))
        missing = need - have
        if missing:
            refuse(f"{case}/{p}/0 is missing {sorted(missing)} after "
                   f"decomposePar -fields")

    print(f"BUILT {case}")
    print(f"  arm            {arm}  (T_inf={t_inf} K, T_wall={t_wall} K)")
    print(f"  endTime        {end_time}  (writeInterval set to match)")
    print(f"  reference      {ref}")
    print(f"  processors     {len(ref_procs)} (decomposition COPIED, not re-derived)")
    print(f"  beta={BETA}  g={G_VECTOR}  Pr={PR}  Prt={PRT}  nu={NU}")
    return 0


def main():
    arms_intact_or_refuse()   # STANDING RULE 14 -- CALL SITE 2 of 2.  The guard
    # runs BEFORE argparse builds its `choices` from ARMS, because a replaced
    # entry would otherwise be offered to the caller as a legitimate choice.
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--reference", default=REF_DEFAULT)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--end-time", type=int, default=REG_END_TIME_DEFAULT,
                    help="controlDict endTime AND writeInterval.  9000 for the "
                         "K0eR3 arms; 200 for the D0 determinism twins.")
    ap.add_argument("--foam-bashrc",
                    default="/usr/lib/openfoam/openfoam2606/etc/bashrc")
    a = ap.parse_args()
    return build(a.arm, a.reference, a.out_root, a.foam_bashrc, a.end_time)


if __name__ == "__main__":
    sys.exit(main())
