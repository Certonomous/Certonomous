"""Build a complete external-aerodynamics case around an arbitrary surface.

Given any watertight STL or OBJ, this writes a runnable OpenFOAM case: a
farfield domain sized from the body's own bounding box, a snappyHexMesh setup
that refines toward the surface, k-omega SST closure with wall functions, and
a ``forceCoeffs`` function object referencing the body's measured planform
area and streamwise length.

Everything is derived from the geometry rather than assumed, because the point
is to accept a surface nobody has seen before.  The streamwise axis is the
longest horizontal extent, the span is the next, and the remaining axis is
vertical — a convention that is correct for aircraft and stated plainly so it
can be overridden when it is not.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from .geometry import load_surface

# Domain, in multiples of the body's streamwise length.
UPSTREAM = 3.0
DOWNSTREAM = 6.0
LATERAL = 3.0
VERTICAL = 3.0


def _raster_area(vertices, faces, keep, cells: int = 420) -> float:
    """Silhouette area by rasterising the projection onto a grid.

    Summing triangle areas would count a wing lying above a fuselage twice.
    The shadow a body casts is a union, not a sum, so the honest measure is
    the occupied area of that union.
    """
    us = [v[keep[0]] for v in vertices]
    vs = [v[keep[1]] for v in vertices]
    u_low, u_high = min(us), max(us)
    v_low, v_high = min(vs), max(vs)
    u_span = (u_high - u_low) or 1.0
    v_span = (v_high - v_low) or 1.0
    du, dv = u_span / cells, v_span / cells

    occupied: set[tuple[int, int]] = set()
    for face in faces:
        pts = [(vertices[i][keep[0]], vertices[i][keep[1]]) for i in face]
        (ax, ay), (bx, by), (cx, cy) = pts
        lo_u = max(0, int((min(ax, bx, cx) - u_low) / du))
        hi_u = min(cells - 1, int((max(ax, bx, cx) - u_low) / du))
        lo_v = max(0, int((min(ay, by, cy) - v_low) / dv))
        hi_v = min(cells - 1, int((max(ay, by, cy) - v_low) / dv))
        area2 = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
        if abs(area2) < 1e-15:
            continue
        for iu in range(lo_u, hi_u + 1):
            pu = u_low + (iu + 0.5) * du
            for iv in range(lo_v, hi_v + 1):
                if (iu, iv) in occupied:
                    continue
                pv = v_low + (iv + 0.5) * dv
                # Barycentric containment test on the projected triangle.
                w0 = ((bx - ax) * (pv - ay) - (pu - ax) * (by - ay)) / area2
                w1 = ((pu - ax) * (cy - ay) - (cx - ax) * (pv - ay)) / area2
                if w0 >= -1e-9 and w1 >= -1e-9 and w0 + w1 <= 1 + 1e-9:
                    occupied.add((iu, iv))
    return len(occupied) * du * dv


def analyse_surface(path: str | Path,
                    streamwise_axis: int | None = None) -> dict[str, Any]:
    """Measure the body: extent, axis roles, planform and frontal area.

    ``streamwise_axis`` overrides the axis heuristic when the caller already
    knows how the body meets the flow.  The heuristic reads a fuselage well but
    cannot know that a bare wing should face the flow chord-first rather than
    along its longer span, or that a finite cylinder belongs in crossflow — so
    those bodies state their streamwise axis rather than leave it to be guessed.
    """
    surface = load_surface(path, max_faces=200_000)
    vertices, faces = surface["vertices"], surface["faces"]
    low = surface["bounds"]["min"]
    high = surface["bounds"]["max"]
    extent = [high[i] - low[i] for i in range(3)]

    if streamwise_axis is not None:
        # The caller fixed the streamwise axis; vertical stays the shallowest
        # of the remaining two, and the last axis is the span.
        streamwise = int(streamwise_axis)
        others = [i for i in range(3) if i != streamwise]
        vertical = min(others, key=lambda i: extent[i])
        span_axis = [i for i in others if i != vertical][0]
        reach = {i: extent[i] for i in range(3) if i != vertical}
    else:
        # Vertical is the shallowest axis. Choosing streamwise by "longest" fails
        # on aircraft, whose span routinely exceeds their length — a B-52 is 56 m
        # across and 48 m long. The fuselage is the discriminator: it is where the
        # body is tall, so the axis along which the tall region runs furthest is
        # the streamwise one.
        vertical = min(range(3), key=lambda i: extent[i])
        horizontal = [i for i in range(3) if i != vertical]
        tall_cut = low[vertical] + 0.45 * extent[vertical]
        tall = [v for v in vertices if v[vertical] >= tall_cut] or vertices
        reach = {}
        for axis in horizontal:
            values = [v[axis] for v in tall]
            reach[axis] = max(values) - min(values)
        streamwise = max(horizontal, key=lambda i: reach[i])
        span_axis = [i for i in horizontal if i != streamwise][0]

    keep_plan = [i for i in range(3) if i != vertical]
    keep_front = [i for i in range(3) if i != streamwise]
    return {
        "min": low, "max": high, "extent": extent,
        "streamwise_axis": streamwise, "span_axis": span_axis,
        "vertical_axis": vertical,
        "length": extent[streamwise], "span": extent[span_axis],
        "height": extent[vertical],
        "planform_area": _raster_area(vertices, faces, keep_plan),
        "frontal_area": _raster_area(vertices, faces, keep_front),
        "triangles": surface["triangles_total"],
        "fuselage_reach": reach,
    }


def _header(cls: str, location: str, name: str) -> str:
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            f"    class       {cls};\n    location    \"{location}\";\n"
            f"    object      {name};\n}}\n\n")


def _vector(values) -> str:
    return "(" + " ".join(f"{v:.6g}" for v in values) + ")"


def build_case(case_dir: str | Path, surface_file: str, geometry: dict[str, Any],
               *, velocity: float = 100.0, viscosity: float = 1.5e-5,
               scale: float = 1.0, refinement: int = 2,
               iterations: int = 300) -> dict[str, Any]:
    """Write the whole case; return the reference values it was built with."""
    case = Path(case_dir)
    for sub in ("0", "constant/triSurface", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)

    stream = geometry["streamwise_axis"]
    span_axis = geometry["span_axis"]
    vert = geometry["vertical_axis"]
    length = geometry["length"] * scale
    span = geometry["span"] * scale
    area = geometry["planform_area"] * scale * scale

    low = [geometry["min"][i] * scale for i in range(3)]
    high = [geometry["max"][i] * scale for i in range(3)]
    centre = [(low[i] + high[i]) / 2 for i in range(3)]

    box_min, box_max = list(centre), list(centre)
    box_min[stream] = low[stream] - UPSTREAM * length
    box_max[stream] = high[stream] + DOWNSTREAM * length
    box_min[span_axis] = centre[span_axis] - LATERAL * span
    box_max[span_axis] = centre[span_axis] + LATERAL * span
    box_min[vert] = centre[vert] - VERTICAL * length
    box_max[vert] = centre[vert] + VERTICAL * length

    # Flow runs from the high-streamwise face toward the low one: the nose of
    # an aircraft model points along +streamwise, so the wind comes to meet it.
    flow = [0.0, 0.0, 0.0]
    flow[stream] = -1.0
    lift_dir = [0.0, 0.0, 0.0]
    lift_dir[vert] = 1.0

    cells = [0, 0, 0]
    base = max(box_max[i] - box_min[i] for i in range(3)) / 60.0
    for i in range(3):
        cells[i] = max(6, int(round((box_max[i] - box_min[i]) / base)))

    (case / "system" / "blockMeshDict").write_text(_block_mesh(box_min, box_max, cells))
    (case / "system" / "snappyHexMeshDict").write_text(
        _snappy(surface_file, centre, box_min, box_max, stream, length, refinement,
                body_min=low, body_max=high))
    (case / "system" / "meshQualityDict").write_text(_MESH_QUALITY)
    (case / "system" / "surfaceFeatureExtractDict").write_text(_features(surface_file))
    (case / "system" / "controlDict").write_text(
        _control(iterations, velocity, length, area, flow, lift_dir, centre))
    (case / "system" / "fvSchemes").write_text(_FV_SCHEMES)
    (case / "system" / "fvSolution").write_text(_FV_SOLUTION)
    (case / "system" / "decomposeParDict").write_text(_DECOMPOSE)
    (case / "constant" / "transportProperties").write_text(
        _header("dictionary", "constant", "transportProperties")
        + "transportModel  Newtonian;\n\n"
        + f"nu              [0 2 -1 0 0 0 0] {viscosity:g};\n")
    (case / "constant" / "turbulenceProperties").write_text(
        _header("dictionary", "constant", "turbulenceProperties")
        + "simulationType  RAS;\n\nRAS\n{\n    RASModel        kOmegaSST;\n"
        + "    turbulence      on;\n    printCoeffs     on;\n}\n")

    inlet = [flow[i] * -velocity for i in range(3)]   # wind blows toward the body
    reynolds = velocity * length / viscosity
    intensity = 0.01
    k = 1.5 * (velocity * intensity) ** 2
    omega = math.sqrt(k) / (0.09 ** 0.25 * 0.1 * length)
    for name, text in _fields(inlet, k, omega, viscosity).items():
        (case / "0" / name).write_text(text)

    return {"length": length, "span": span, "planform_area": area,
            "velocity": velocity, "viscosity": viscosity, "reynolds": reynolds,
            "domain_min": box_min, "domain_max": box_max,
            "background_cells": cells, "flow_direction": flow,
            "turbulence": "kOmegaSST"}


def _block_mesh(low, high, cells) -> str:
    corners = [
        (low[0], low[1], low[2]), (high[0], low[1], low[2]),
        (high[0], high[1], low[2]), (low[0], high[1], low[2]),
        (low[0], low[1], high[2]), (high[0], low[1], high[2]),
        (high[0], high[1], high[2]), (low[0], high[1], high[2]),
    ]
    return (_header("dictionary", "system", "blockMeshDict")
            + "scale 1;\n\nvertices\n(\n"
            + "\n".join(f"    {_vector(c)}" for c in corners)
            + "\n);\n\nblocks\n(\n"
            + f"    hex (0 1 2 3 4 5 6 7) ({cells[0]} {cells[1]} {cells[2]}) simpleGrading (1 1 1)\n"
            + ");\n\nedges ();\n\nboundary\n(\n"
            + "    farfield\n    {\n        type patch;\n        faces\n        (\n"
            + "            (0 3 2 1)\n            (4 5 6 7)\n            (0 1 5 4)\n"
            + "            (2 3 7 6)\n            (1 2 6 5)\n            (0 4 7 3)\n"
            + "        );\n    }\n);\n\nmergePatchPairs ();\n")


def _snappy(surface_file: str, centre, low, high, stream: int, length: float,
            refinement: int, body_min=None, body_max=None) -> str:
    inside = list(centre)
    # A point inside the domain but well clear of the body: step downstream so
    # it can never land on the surface itself.
    inside[stream] = high[stream] - 0.05 * (high[stream] - low[stream])
    near = max(2, refinement)

    # Concentrate cells where the flow decides the forces: a box hugging the
    # body and trailing behind it, rather than refining the whole farfield.
    region_geometry = ""
    region = "    refinementRegions {}\n\n"
    if body_min and body_max:
        pad = [0.4 * (body_max[i] - body_min[i]) for i in range(3)]
        region_min = [body_min[i] - pad[i] for i in range(3)]
        region_max = [body_max[i] + pad[i] for i in range(3)]
        region_min[stream] -= 0.5 * length
        region_max[stream] += 1.5 * length
        region_geometry = (
            "    nearBody\n    {\n        type searchableBox;\n"
            f"        min {_vector(region_min)};\n"
            f"        max {_vector(region_max)};\n    }}\n")
        region = ("    refinementRegions\n    {\n"
                  "        nearBody\n        {\n"
                  f"            mode inside;\n"
                  f"            levels ((1e15 {max(1, near - 1)}));\n"
                  "        }\n    }\n\n")

    return (_header("dictionary", "system", "snappyHexMeshDict")
            + "castellatedMesh true;\nsnap            true;\naddLayers       false;\n\n"
            + "geometry\n{\n"
            + f"    body\n    {{\n        type triSurfaceMesh;\n        file \"{surface_file}\";\n    }}\n"
            + region_geometry
            + "}\n\ncastellatedMeshControls\n{\n"
            + "    maxLocalCells   4000000;\n    maxGlobalCells  8000000;\n"
            + "    minRefinementCells 10;\n    maxLoadUnbalance 0.1;\n"
            + "    nCellsBetweenLevels 3;\n\n"
            + "    features\n    (\n"
            + f"        {{ file \"{Path(surface_file).stem}.eMesh\"; level {near}; }}\n"
            + "    );\n\n    refinementSurfaces\n    {\n"
            + f"        body {{ level ({near} {near + 1}); }}\n    }}\n\n"
            + "    resolveFeatureAngle 30;\n\n"
            + region
            + f"    locationInMesh {_vector(inside)};\n"
            + "    allowFreeStandingZoneFaces true;\n}\n\n"
            + "snapControls\n{\n    nSmoothPatch    3;\n    tolerance       2.0;\n"
            + "    nSolveIter      30;\n    nRelaxIter      5;\n"
            + "    nFeatureSnapIter 10;\n    implicitFeatureSnap false;\n"
            + "    explicitFeatureSnap true;\n    multiRegionFeatureSnap false;\n}\n\n"
            + "addLayersControls\n{\n    relativeSizes true;\n    layers {}\n"
            + "    expansionRatio 1.0;\n    finalLayerThickness 0.3;\n"
            + "    minThickness 0.1;\n    nGrow 0;\n    featureAngle 60;\n"
            + "    nRelaxIter 3;\n    nSmoothSurfaceNormals 1;\n    nSmoothNormals 3;\n"
            + "    nSmoothThickness 10;\n    maxFaceThicknessRatio 0.5;\n"
            + "    maxThicknessToMedialRatio 0.3;\n    minMedialAxisAngle 90;\n"
            + "    nBufferCellsNoExtrude 0;\n    nLayerIter 50;\n}\n\n"
            + "meshQualityControls\n{\n    #include \"meshQualityDict\"\n}\n\n"
            + "writeFlags ( scalarLevels layerSets layerFields );\nmergeTolerance 1e-6;\n")


def _features(surface_file: str) -> str:
    return (_header("dictionary", "system", "surfaceFeatureExtractDict")
            + f"{surface_file}\n{{\n    extractionMethod    extractFromSurface;\n"
            + "    includedAngle       150;\n    subsetFeatures\n    {\n"
            + "        nonManifoldEdges no;\n        openEdges       yes;\n    }\n"
            + "    writeObj            no;\n}\n")


def _control(iterations: int, velocity: float, length: float, area: float,
             flow, lift_dir, centre) -> str:
    drag_dir = [-flow[i] for i in range(3)]
    return (_header("dictionary", "system", "controlDict")
            + "application     simpleFoam;\nstartFrom       startTime;\nstartTime 0;\n"
            + f"stopAt          endTime;\nendTime         {iterations};\ndeltaT 1;\n"
            + f"writeControl    timeStep;\nwriteInterval   {iterations};\npurgeWrite 0;\n"
            + "writeFormat     ascii;\nwritePrecision  8;\ntimeFormat general;\n"
            + "runTimeModifiable no;\n\nfunctions\n{\n    forceCoeffs1\n    {\n"
            + "        type            forceCoeffs;\n        libs            (\"libforces.so\");\n"
            + "        writeControl    timeStep;\n        writeInterval   1;\n"
            + "        patches         (body);\n        rho             rhoInf;\n"
            + "        rhoInf          1.225;\n"
            + f"        liftDir         {_vector(lift_dir)};\n"
            + f"        dragDir         {_vector(drag_dir)};\n"
            + f"        CofR            {_vector(centre)};\n"
            + "        pitchAxis       (0 1 0);\n"
            + f"        magUInf         {velocity:g};\n"
            + f"        lRef            {length:g};\n"
            + f"        Aref            {area:g};\n    }}\n}}\n")


def _fields(inlet, k: float, omega: float, viscosity: float) -> dict[str, str]:
    def field(cls, name, dimensions, internal, farfield, body):
        return (_header(cls, "0", name)
                + f"dimensions      {dimensions};\n\n"
                + f"internalField   uniform {internal};\n\nboundaryField\n{{\n"
                + f"    farfield\n    {{\n{farfield}    }}\n"
                + f"    body\n    {{\n{body}    }}\n}}\n")

    velocity_text = _vector(inlet)
    return {
        "U": field("volVectorField", "U", "[0 1 -1 0 0 0 0]", velocity_text,
                   f"        type            freestreamVelocity;\n"
                   f"        freestreamValue uniform {velocity_text};\n",
                   "        type            noSlip;\n"),
        "p": field("volScalarField", "p", "[0 2 -2 0 0 0 0]", "0",
                   "        type            freestreamPressure;\n"
                   "        freestreamValue uniform 0;\n",
                   "        type            zeroGradient;\n"),
        "k": field("volScalarField", "k", "[0 2 -2 0 0 0 0]", f"{k:g}",
                   f"        type            inletOutlet;\n"
                   f"        inletValue      uniform {k:g};\n"
                   f"        value           uniform {k:g};\n",
                   f"        type            kqRWallFunction;\n"
                   f"        value           uniform {k:g};\n"),
        "omega": field("volScalarField", "omega", "[0 0 -1 0 0 0 0]", f"{omega:g}",
                       f"        type            inletOutlet;\n"
                       f"        inletValue      uniform {omega:g};\n"
                       f"        value           uniform {omega:g};\n",
                       f"        type            omegaWallFunction;\n"
                       f"        value           uniform {omega:g};\n"),
        "nut": field("volScalarField", "nut", "[0 2 -1 0 0 0 0]", "0",
                     "        type            calculated;\n        value uniform 0;\n",
                     "        type            nutkWallFunction;\n        value uniform 0;\n"),
    }


_MESH_QUALITY = (
    _header("dictionary", "system", "meshQualityDict")
    # Boundary skewness is held to the same 4.0 the lab's checkMesh guidance
    # uses (the stock 20 allowance left faces checkMesh then flagged: the
    # B-52 read max skewness 5.06 with it, under 4 with this gate).
    + "maxNonOrtho 65;\nmaxBoundarySkewness 4;\nmaxInternalSkewness 4;\n"
    + "maxConcave 80;\nminVol 1e-13;\nminTetQuality 1e-15;\nminArea -1;\n"
    + "minTwist 0.02;\nminDeterminant 0.001;\nminFaceWeight 0.05;\n"
    + "minVolRatio 0.01;\nminTriangleTwist -1;\nnSmoothScale 4;\n"
    + "errorReduction 0.75;\n\nrelaxed\n{\n    maxNonOrtho 75;\n}\n")

_FV_SCHEMES = (
    _header("dictionary", "system", "fvSchemes")
    + "ddtSchemes { default steadyState; }\n\n"
    + "gradSchemes { default Gauss linear; limited cellLimited Gauss linear 1; }\n\n"
    + "divSchemes\n{\n    default none;\n"
    + "    div(phi,U)      bounded Gauss linearUpwind limited;\n"
    + "    div(phi,k)      bounded Gauss limitedLinear 1;\n"
    + "    div(phi,omega)  bounded Gauss limitedLinear 1;\n"
    + "    div((nuEff*dev2(T(grad(U))))) Gauss linear;\n}\n\n"
    + "laplacianSchemes { default Gauss linear corrected; }\n\n"
    + "interpolationSchemes { default linear; }\n\n"
    + "snGradSchemes { default corrected; }\n\n"
    + "wallDist { method meshWave; }\n")

_FV_SOLUTION = (
    _header("dictionary", "system", "fvSolution")
    + "solvers\n{\n"
    + "    p { solver GAMG; smoother GaussSeidel; tolerance 1e-7; relTol 0.01; }\n"
    # potentialFoam solves for the velocity potential and looks for its own
    # solver entry; without it the initialisation step cannot start.
    + "    Phi { solver GAMG; smoother DIC; tolerance 1e-6; relTol 0.01; }\n"
    + "    \"(U|k|omega)\" { solver smoothSolver; smoother symGaussSeidel;\n"
    + "        tolerance 1e-8; relTol 0.1; }\n}\n\n"
    + "SIMPLE\n{\n    nNonOrthogonalCorrectors 1;\n    consistent yes;\n\n"
    + "    residualControl { p 1e-4; U 1e-4; \"(k|omega)\" 1e-4; }\n}\n\n"
    + "potentialFlow\n{\n    nNonOrthogonalCorrectors 10;\n}\n\n"
    + "relaxationFactors\n{\n    equations { U 0.9; \".*\" 0.9; }\n}\n")

_DECOMPOSE = (
    _header("dictionary", "system", "decomposeParDict")
    + "numberOfSubdomains 6;\nmethod hierarchical;\n"
    + "coeffs { n (3 2 1); }\n")
