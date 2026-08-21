#!/usr/bin/env python3
"""
T9a builder: composite wall and straight fin, solid conduction only.

Written AFTER the comparator was frozen (commit 239ed2b8, Charter 2d) and to
the specification in docs/campaigns/T-family/T9a_PREREGISTRATION.md.  The
case list, mesh ladder and every interpretation are the ones recorded in
T9a_registered.json; this file adds nothing the comparator does not already
expect.

DESIGN NOTES THAT ARE DECISIONS, NOT DEFAULTS:

  * laplacianFoam (ESI v2606).  The pre-registration names no solver; this is
    the simplest one that answers the registered question, and its
    createFields.H reads DT as a volScalarField READ_IF_PRESENT, so the
    three-layer conductivity map is a nonuniform 0/DT with the registered
    values.  DT carries diffusivity dimensions; numerically it is k.  Steady
    d/dx(k dT/dx) = 0 depends only on k ratios, and the comparator recovers
    q'' with the registered k, so the unit label is cosmetic.

  * THE LAYER INTERFACES SIT ON MESH FACES.  One blockMesh block per layer,
    uniform spacing within each layer.  The comparator refuses if a face is
    not at x = 0.05 and x = 0.15 exactly, and checks every cell's DT against
    the layer its centre lies in -- so the cell ordering this builder assumes
    when writing DT is verified against the mesh, never trusted.

  * laplacian(DT,T) IS LEFT AT Gauss linear.  Arithmetic face interpolation
    of DT at a 400x contrast is exactly the interface treatment the rung was
    designed to expose; it is not tuned to harmonic to make the row pass.

  * THE ROBIN CONDITION IS A mixed PATCH with valueFraction = 1/(1 + k/(h d)),
    d the wall-normal distance from the first cell centre to the face.  d
    changes with the level.  The comparator re-derives d from the mesh and
    refuses on a mismatch, which is the only reason it is safe to compute it
    here.

  * THREE LEVELS AT RATIO 1.6 with T1c's integer rounding (8 -> 13, 16 -> 26,
    80 -> 128).  A two-level ladder cannot produce an observed order.

  * writeInterval STRICTLY LESS THAN endTime (L-140), and NO residualControl
    (L-141): endTime governs, convergence is judged from written checkpoints.
"""
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REG = json.load(open(os.path.join(HERE, "T9a_registered.json")))

WALL = REG["wall"]
FIN = REG["fin"]
CASES = REG["cases"]

# 1D / 2D slabs need a finite, harmless extent in the empty directions
WALL_YZ = 0.01
FIN_DEPTH = 0.001

END_TIME = 1000
WRITE_INTERVAL = 100      # STRICTLY < END_TIME.  See L-140.


def header(cls, obj, loc):
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "{loc}";
    object      {obj};
}}
"""


# ---------------------------------------------------------------------------
# composite wall
# ---------------------------------------------------------------------------
def wall_block_mesh(cells):
    xs = [0.0]
    for ly in WALL["layers"]:
        xs.append(xs[-1] + ly["L"])
    y, z = WALL_YZ, WALL_YZ
    verts = []
    for x in xs:
        verts += [(x, 0, 0), (x, y, 0), (x, y, z), (x, 0, z)]
    vtxt = "\n".join(f"    ({vx:.10g} {vy:.10g} {vz:.10g})" for vx, vy, vz in verts)
    blocks = []
    for j, n in enumerate(cells):
        b = 4 * j
        # hex ordering: x0 face (0 1 2 3 as y-z loop) then x1 face
        blocks.append(f"    hex ({b} {b+4} {b+5} {b+1} {b+3} {b+7} {b+6} {b+2}) "
                      f"({n} 1 1) simpleGrading (1 1 1)")
    nb = len(cells)
    last = 4 * nb
    sides_y = " ".join(f"({4*j} {4*j+4} {4*j+7} {4*j+3}) "
                       f"({4*j+1} {4*j+2} {4*j+6} {4*j+5})" for j in range(nb))
    sides_z = " ".join(f"({4*j} {4*j+1} {4*j+5} {4*j+4}) "
                       f"({4*j+3} {4*j+7} {4*j+6} {4*j+2})" for j in range(nb))
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;

vertices
(
{vtxt}
);

blocks
(
{chr(10).join(blocks)}
);

edges ();

boundary
(
    hot     {{ type wall;  faces ( (0 3 2 1) ); }}
    cold    {{ type wall;  faces ( ({last} {last+1} {last+2} {last+3}) ); }}
    sidesY  {{ type empty; faces ( {sides_y} ); }}
    sidesZ  {{ type empty; faces ( {sides_z} ); }}
);

mergePatchPairs ();
"""


def wall_field_T(T_hot, T_cold):
    T0 = 0.5 * (T_hot + T_cold)
    return header("volScalarField", "T", "0") + f"""
dimensions      [0 0 0 1 0 0 0];
internalField   uniform {T0:.10g};
boundaryField
{{
    hot     {{ type fixedValue; value uniform {T_hot:.10g}; }}
    cold    {{ type fixedValue; value uniform {T_cold:.10g}; }}
    sidesY  {{ type empty; }}
    sidesZ  {{ type empty; }}
}}
"""


def wall_field_DT(cells):
    # block-by-block cell ordering, x fastest: layer 1 cells first.  VERIFIED
    # BY THE COMPARATOR against cell-centre positions, never trusted.
    vals = []
    for ly, n in zip(WALL["layers"], cells):
        vals += [ly["k"]] * n
    body = "\n".join(f"{v:.10g}" for v in vals)
    return header("volScalarField", "DT", "0") + f"""
dimensions      [0 2 -1 0 0 0 0];
internalField   nonuniform List<scalar>
{len(vals)}
(
{body}
)
;
boundaryField
{{
    hot     {{ type zeroGradient; }}
    cold    {{ type zeroGradient; }}
    sidesY  {{ type empty; }}
    sidesZ  {{ type empty; }}
}}
"""


# ---------------------------------------------------------------------------
# fin
# ---------------------------------------------------------------------------
def fin_block_mesh(nx, ny):
    L, t, W = FIN["L"], FIN["t"], FIN_DEPTH
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;

vertices
(
    (0      0      0)
    ({L:.10g} 0      0)
    ({L:.10g} {t:.10g} 0)
    (0      {t:.10g} 0)
    (0      0      {W:.10g})
    ({L:.10g} 0      {W:.10g})
    ({L:.10g} {t:.10g} {W:.10g})
    (0      {t:.10g} {W:.10g})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) simpleGrading (1 1 1)
);

edges ();

boundary
(
    base         {{ type wall;  faces ( (0 4 7 3) ); }}
    tip          {{ type wall;  faces ( (1 2 6 5) ); }}
    top          {{ type wall;  faces ( (3 7 6 2) ); }}
    bottom       {{ type wall;  faces ( (0 1 5 4) ); }}
    frontAndBack {{ type empty; faces ( (0 3 2 1) (4 5 6 7) ); }}
);

mergePatchPairs ();
"""


def fin_value_fraction(ny):
    d = 0.5 * FIN["t"] / ny            # first cell centre to the face
    return 1.0 / (1.0 + FIN["k"] / (FIN["h"] * d)), d


def fin_field_T(ny):
    f, d = fin_value_fraction(ny)
    robin = (f"{{ type mixed; refValue uniform {FIN['T_inf']:.10g}; "
             f"refGradient uniform 0; valueFraction uniform {f:.12e}; "
             f"value uniform {FIN['T_inf']:.10g}; }}")
    return header("volScalarField", "T", "0") + f"""
// Robin condition -k dT/dn = h (T_face - T_inf) as a mixed patch:
//   valueFraction = 1/(1 + k/(h d)),  d = {d:.10e} m  (half the y spacing)
dimensions      [0 0 0 1 0 0 0];
internalField   uniform {FIN['T_base']:.10g};
boundaryField
{{
    base         {{ type fixedValue; value uniform {FIN['T_base']:.10g}; }}
    tip          {{ type zeroGradient; }}
    top          {robin}
    bottom       {robin}
    frontAndBack {{ type empty; }}
}}
"""


def fin_field_DT():
    return header("volScalarField", "DT", "0") + f"""
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform {FIN['k']:.10g};
boundaryField
{{
    base         {{ type zeroGradient; }}
    tip          {{ type zeroGradient; }}
    top          {{ type zeroGradient; }}
    bottom       {{ type zeroGradient; }}
    frontAndBack {{ type empty; }}
}}
"""


# ---------------------------------------------------------------------------
# shared dictionaries
# ---------------------------------------------------------------------------
def transport(k_fallback):
    # read by laplacianFoam ONLY if 0/DT is absent; every case writes 0/DT
    return header("dictionary", "transportProperties", "constant") + f"""
DT              {k_fallback:.10g};
"""


def control_dict():
    return header("dictionary", "controlDict", "system") + f"""
application     laplacianFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         {END_TIME};
deltaT          1;
writeControl    timeStep;
writeInterval   {WRITE_INTERVAL};
purgeWrite      2;
writeFormat     ascii;
writePrecision  16;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
"""


def fv_schemes():
    return header("dictionary", "fvSchemes", "system") + """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes      { default none; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
"""


def fv_solution():
    # NO residualControl (L-141): endTime governs, checkpoints are compared.
    return header("dictionary", "fvSolution", "system") + """
solvers
{
    T
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-14;
        relTol          0;
    }
}
SIMPLE
{
    nNonOrthogonalCorrectors 0;
}
"""


def case_txt(name, c):
    lines = [f"case              {name}",
             "rung              T9a (composite wall + fin efficiency, EXACT tier)",
             f"kind              {c['kind']}",
             "solver            laplacianFoam (ESI v2606), steadyState ddt",
             f"endTime           {END_TIME}",
             f"writeInterval     {WRITE_INTERVAL}  (strictly less than endTime, L-140)",
             "residualControl   none (L-141; convergence from written checkpoints)"]
    if c["kind"].startswith("wall"):
        for j, (ly, n) in enumerate(zip(WALL["layers"], c["cells_per_layer"])):
            lines.append(f"layer_{j+1}           L = {ly['L']} m, k = {ly['k']} W/mK,"
                         f" {n} cells, dx = {ly['L']/n:.6e} m")
        if c["kind"] == "wall":
            lines += [f"T_hot             {WALL['T_hot']} K",
                      f"T_cold            {WALL['T_cold']} K",
                      f"reference_q       {WALL['q']} W/m2",
                      f"reference_T_i1    {WALL['T_i1']} K",
                      f"reference_T_i2    {WALL['T_i2']} K"]
        else:
            lines += [f"T_hot             {WALL['T_hot']} K  (C3: BOTH faces)",
                      f"T_cold            {WALL['T_hot']} K  (C3: BOTH faces)",
                      "control           C3 trivial baseline -- uniform-temperature solid, MUST FAIL"]
    else:
        f, d = fin_value_fraction(c["ny"])
        lines += [f"k                 {FIN['k']} W/mK",
                  f"t                 {FIN['t']} m",
                  f"L                 {FIN['L']} m",
                  f"h                 {FIN['h']} W/m2K  (both faces, mixed/Robin)",
                  f"mesh              {c['nx']} x {c['ny']}  dx = {FIN['L']/c['nx']:.6e}"
                  f"  dy = {FIN['t']/c['ny']:.6e}",
                  f"d_wall            {d:.10e} m",
                  f"valueFraction     {f:.12e}",
                  f"T_base            {FIN['T_base']} K",
                  f"T_inf             {FIN['T_inf']} K",
                  f"reference_eta     {FIN['eta']}",
                  f"reference_tip     {FIN['tip_ratio']}",
                  f"model_error_floor {FIN['model_error_floor_pct']} %  (O(Bi), Bi = {FIN['Bi']})"]
    return "\n".join(lines) + "\n"


def main():
    made = []
    for name, c in CASES.items():
        d = os.path.join(HERE, name)
        if os.path.exists(d):
            shutil.rmtree(d)
        for sub in ("0.orig", "constant", "system"):
            os.makedirs(os.path.join(d, sub))
        w = lambda rel, txt: open(os.path.join(d, rel), "w").write(txt)
        w("system/controlDict", control_dict())
        w("system/fvSchemes", fv_schemes())
        w("system/fvSolution", fv_solution())
        if c["kind"] in ("wall", "wall_uniform_control"):
            cells = c["cells_per_layer"]
            w("system/blockMeshDict", wall_block_mesh(cells))
            T_cold = WALL["T_cold"] if c["kind"] == "wall" else WALL["T_hot"]
            w("0.orig/T", wall_field_T(WALL["T_hot"], T_cold))
            w("0.orig/DT", wall_field_DT(cells))
            w("constant/transportProperties", transport(WALL["layers"][0]["k"]))
            ncell = sum(cells)
        else:
            w("system/blockMeshDict", fin_block_mesh(c["nx"], c["ny"]))
            w("0.orig/T", fin_field_T(c["ny"]))
            w("0.orig/DT", fin_field_DT())
            w("constant/transportProperties", transport(FIN["k"]))
            ncell = c["nx"] * c["ny"]
        w("CASE.txt", case_txt(name, c))
        made.append((name, ncell, c["kind"]))

    print(f"T9a: {len(made)} cases built in {HERE}")
    print(f"  endTime {END_TIME}, writeInterval {WRITE_INTERVAL} (STRICTLY less)")
    print(f"\n  {'case':8s} {'cells':>6s}  kind")
    for n, cells, kind in made:
        print(f"  {n:8s} {cells:6d}  {kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
