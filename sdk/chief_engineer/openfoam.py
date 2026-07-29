"""OpenFOAM adapter: 2D steady laminar flow past a circular cylinder.

Phase 1 of the OpenFOAM integration.  The case is fully generated from Python
— an O-grid `blockMesh` annulus around the cylinder with a circular farfield,
solved with `simpleFoam`, forces extracted through the `forceCoeffs` function
object — so no external template files, STL geometry, or snappyHexMesh are
required.  Design parameters cover geometry (cylinder diameter), flow state
(inlet velocity, kinematic viscosity — together the Reynolds number), and
numerics (mesh refinement), which lets the chief trade solver cost against
accuracy and lets the uncertainty layer flag under-resolved or non-converged
evidence.

Two backends, mirroring the OpenVSP adapter pair:

- ``OpenFoamCylinderApi`` runs the real solvers via subprocess.  It needs the
  OpenFOAM binaries (``blockMesh``, ``simpleFoam``) on PATH, in
  ``OPENFOAM_BINDIR``, or behind an ``OPENFOAM_RUN_PREFIX`` launcher (e.g. a
  container or WSL shim).
- ``SyntheticOpenFoamApi`` is a deterministic stand-in built on the classical
  empirical cylinder-drag correlation, so missions, tests, and the chief's
  uncertainty verdicts run on machines without OpenFOAM.  It is not a physics
  substitute.

Steady laminar validity: the wake is steady below Re ≈ 47; above that the true
flow sheds vortices and simpleFoam convergence degrades.  The adapter reports
``convergence_residual`` and ``converged`` as first-class metrics so the chief
can constrain missions to trustworthy evidence instead of silently averaging a
non-converged solve.
"""

from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .adapters import AdapterManifest, SoftwareAdapterRegistry
from .models import Domain, MetricSpec, ParameterSpec

ProgressSink = Callable[[dict[str, Any]], None]

PARAMETER_SPECS = (
    ParameterSpec("cylinder_diameter", 0.5, 2.0, 0.10, "m", "Cylinder diameter", (Domain.GEOMETRY, Domain.AERODYNAMICS)),
    ParameterSpec("inlet_velocity", 0.5, 4.0, 0.12, "m/s", "Freestream velocity", (Domain.AERODYNAMICS,)),
    ParameterSpec("kinematic_viscosity", 0.01, 0.2, 0.15, "m2/s", "Fluid kinematic viscosity", (Domain.AERODYNAMICS,)),
    ParameterSpec("mesh_refinement", 0.5, 3.0, 0.20, "factor", "Mesh density multiplier", (Domain.GEOMETRY,)),
)

METRIC_SPECS = (
    MetricSpec("Cd", "aerodynamics", "min", ("drag coefficient", "drag", "cd"), "coefficient", (Domain.AERODYNAMICS, Domain.GEOMETRY)),
    MetricSpec("Cl", "aerodynamics", "min", ("lift coefficient", "lift", "cl"), "coefficient", (Domain.AERODYNAMICS,)),
    MetricSpec("Re", "aerodynamics", "max", ("reynolds number", "reynolds"), "dimensionless", (Domain.AERODYNAMICS,)),
    MetricSpec("convergence_residual", "aerodynamics", "min", ("residual", "convergence"), "residual", (Domain.AERODYNAMICS,)),
    MetricSpec("converged", "aerodynamics", "max", ("solver converged",), "boolean", (Domain.AERODYNAMICS,)),
    MetricSpec("solver_iterations", "aerodynamics", "min", ("iterations", "solver cost"), "iterations", (Domain.AERODYNAMICS,)),
    MetricSpec("cell_count", "geometry", "min", ("cells", "mesh size"), "cells", (Domain.GEOMETRY,)),
)

DEFAULT_DESIGN = {
    "cylinder_diameter": 1.0,
    "inlet_velocity": 1.0,
    "kinematic_viscosity": 0.05,
    "mesh_refinement": 1.0,
}

DOMAIN_DEPENDENCIES = {"aerodynamics": ("geometry",)}

# Mesh topology constants.
_FARFIELD_DIAMETERS = 10.0    # farfield radius, in cylinder diameters
_SPAN_THICKNESS = 0.1         # one-cell extrusion depth of the 2D plane, m
_BASE_RADIAL_CELLS = 30
_BASE_TANGENTIAL_CELLS = 20   # per 90-degree block
_RADIAL_GRADING = 40.0        # cell-size expansion from cylinder to farfield
_MAX_ITERATIONS = 2000


def host_launch_prefix() -> list[str]:
    """The argv prefix that reaches the OpenFOAM toolchain on THIS host.

    One code path, both hosts. Resolution order:

    1. ``OPENFOAM_RUN_PREFIX`` when set, split on whitespace. Explicit wins.
    2. Native: if the toolchain is reachable from this process, no prefix at
       all. On Linux the solver binaries live behind the ``openfoam2606``
       launcher rather than on PATH, so callers still invoke that wrapper;
       what they must NOT do is prepend a WSL hop that does not exist here.
    3. WSL fallback, for the Windows laptop where the toolchain lives inside
       a distribution and must be reached through ``wsl``.

    Before this existed, two modules hard-coded the WSL form. On a Linux host
    there is no ``wsl`` binary, so every act died before writing a log file --
    the case directory was staged and then nothing happened, with no error
    surfaced.
    """
    explicit = os.environ.get("OPENFOAM_RUN_PREFIX")
    if explicit:
        return explicit.split()
    if shutil.which("openfoam2606") or available():
        return []
    if shutil.which("wsl"):
        return ["wsl", "-d", "Ubuntu", "-u", "foam", "--"]
    return []


def host_run_prefix() -> list[str]:
    """Like :func:`host_launch_prefix` but including the ``openfoam2606``
    launcher itself, for callers that pass a prefix to an API rather than
    building a ``bash -c`` line of their own."""
    base = host_launch_prefix()
    launcher = shutil.which("openfoam2606")
    if base and shutil.which("wsl") and base[0] == "wsl":
        return [*base, "openfoam2606"]
    return ["openfoam2606"] if launcher else []


def available() -> bool:
    """True when the real OpenFOAM toolchain is reachable from this process."""
    if os.environ.get("OPENFOAM_RUN_PREFIX"):
        return True
    bindir = os.environ.get("OPENFOAM_BINDIR")
    if bindir and (Path(bindir) / "simpleFoam").exists():
        return True
    return shutil.which("simpleFoam") is not None and shutil.which("blockMesh") is not None


# --------------------------------------------------------------------------
# Case generation
# --------------------------------------------------------------------------

def build_case(case_dir: Path, design: Mapping[str, float]) -> dict[str, float]:
    """Write a complete OpenFOAM case for the given design; return the resolved design."""
    resolved = {**DEFAULT_DESIGN, **{key: float(value) for key, value in design.items()}}
    case_dir = Path(case_dir)
    for sub in ("0", "constant", "system"):
        (case_dir / sub).mkdir(parents=True, exist_ok=True)

    diameter = resolved["cylinder_diameter"]
    velocity = resolved["inlet_velocity"]
    viscosity = resolved["kinematic_viscosity"]
    refinement = resolved["mesh_refinement"]

    (case_dir / "system" / "blockMeshDict").write_text(_block_mesh_dict(diameter, refinement))
    (case_dir / "system" / "controlDict").write_text(_control_dict(diameter, velocity))
    (case_dir / "system" / "fvSchemes").write_text(_FV_SCHEMES)
    (case_dir / "system" / "fvSolution").write_text(_FV_SOLUTION)
    (case_dir / "constant" / "transportProperties").write_text(_transport_properties(viscosity))
    (case_dir / "constant" / "turbulenceProperties").write_text(_TURBULENCE_PROPERTIES)
    (case_dir / "0" / "U").write_text(_initial_velocity(velocity))
    (case_dir / "0" / "p").write_text(_INITIAL_PRESSURE)
    return resolved


def _foam_header(cls: str, location: str, name: str) -> str:
    return (
        "FoamFile\n{\n"
        "    version     2.0;\n"
        "    format      ascii;\n"
        f"    class       {cls};\n"
        f"    location    \"{location}\";\n"
        f"    object      {name};\n"
        "}\n\n"
    )


def _block_mesh_dict(diameter: float, refinement: float) -> str:
    """O-grid annulus: cylinder wall to circular farfield, four 90-degree blocks.

    Block corners sit on the +-45-degree diagonals of the inner and outer
    circles; arc edges pass through the axis-aligned midpoints.  One cell
    through the span with empty front/back patches makes the case 2D.
    """
    inner = diameter / 2.0
    outer = _FARFIELD_DIAMETERS * diameter
    half = math.sqrt(0.5)
    n_radial = max(8, round(_BASE_RADIAL_CELLS * refinement))
    n_tangential = max(8, round(_BASE_TANGENTIAL_CELLS * refinement))

    corner_angles = (-45.0, 45.0, 135.0, 225.0)
    arc_angles = (0.0, 90.0, 180.0, 270.0)

    def ring(radius: float, z: float) -> list[str]:
        points = []
        for angle in corner_angles:
            radians = math.radians(angle)
            points.append(f"    ({radius * math.cos(radians):.8g} {radius * math.sin(radians):.8g} {z:.8g})")
        return points

    vertices = (
        ring(inner, 0.0) + ring(outer, 0.0)
        + ring(inner, _SPAN_THICKNESS) + ring(outer, _SPAN_THICKNESS)
    )

    blocks, edges, cylinder_faces, farfield_faces, empty_faces = [], [], [], [], []
    for k in range(4):
        k2 = (k + 1) % 4
        i, o, i2, o2 = k, 4 + k, k2, 4 + k2
        ti, to, ti2, to2 = 8 + k, 12 + k, 8 + k2, 12 + k2
        blocks.append(
            f"    hex ({i} {o} {o2} {i2} {ti} {to} {to2} {ti2}) "
            f"({n_radial} {n_tangential} 1) simpleGrading ({_RADIAL_GRADING:g} 1 1)"
        )
        mid = math.radians(arc_angles[k])
        for radius, a, b in ((inner, i, i2), (outer, o, o2)):
            for lift in (0, 8):
                edges.append(
                    f"    arc {a + lift} {b + lift} "
                    f"({radius * math.cos(mid):.8g} {radius * math.sin(mid):.8g} "
                    f"{0.0 if lift == 0 else _SPAN_THICKNESS:.8g})"
                )
        cylinder_faces.append(f"            ({i} {i2} {ti2} {ti})")
        farfield_faces.append(f"            ({o} {o2} {to2} {to})")
        empty_faces.append(f"            ({i} {o} {o2} {i2})")
        empty_faces.append(f"            ({ti} {to} {to2} {ti2})")

    return (
        _foam_header("dictionary", "system", "blockMeshDict")
        + "convertToMeters 1;\n\n"
        + "vertices\n(\n" + "\n".join(vertices) + "\n);\n\n"
        + "blocks\n(\n" + "\n".join(blocks) + "\n);\n\n"
        + "edges\n(\n" + "\n".join(edges) + "\n);\n\n"
        + "boundary\n(\n"
        + "    cylinder\n    {\n        type wall;\n        faces\n        (\n"
        + "\n".join(cylinder_faces) + "\n        );\n    }\n"
        + "    farfield\n    {\n        type patch;\n        faces\n        (\n"
        + "\n".join(farfield_faces) + "\n        );\n    }\n"
        + "    frontAndBack\n    {\n        type empty;\n        faces\n        (\n"
        + "\n".join(empty_faces) + "\n        );\n    }\n"
        + ");\n\nmergePatchPairs\n(\n);\n"
    )


def _control_dict(diameter: float, velocity: float) -> str:
    reference_area = diameter * _SPAN_THICKNESS
    return (
        _foam_header("dictionary", "system", "controlDict")
        + "application     simpleFoam;\n"
        + "startFrom       startTime;\n"
        + "startTime       0;\n"
        + "stopAt          endTime;\n"
        + f"endTime         {_MAX_ITERATIONS};\n"
        + "deltaT          1;\n"
        + "writeControl    timeStep;\n"
        + f"writeInterval   {_MAX_ITERATIONS};\n"
        + "purgeWrite      0;\n"
        + "writeFormat     ascii;\n"
        + "writePrecision  8;\n"
        + "timeFormat      general;\n"
        + "runTimeModifiable no;\n\n"
        + "functions\n{\n"
        + "    forceCoeffs1\n    {\n"
        + "        type            forceCoeffs;\n"
        + "        libs            (\"libforces.so\");\n"
        + "        writeControl    timeStep;\n"
        + "        writeInterval   1;\n"
        + "        patches         (cylinder);\n"
        + "        rho             rhoInf;\n"
        + "        rhoInf          1.0;\n"
        + "        liftDir         (0 1 0);\n"
        + "        dragDir         (1 0 0);\n"
        + "        CofR            (0 0 0);\n"
        + "        pitchAxis       (0 0 1);\n"
        + f"        magUInf         {velocity:g};\n"
        + f"        lRef            {diameter:g};\n"
        + f"        Aref            {reference_area:g};\n"
        + "    }\n"
        + "}\n"
    )


def _transport_properties(viscosity: float) -> str:
    return (
        _foam_header("dictionary", "constant", "transportProperties")
        + "transportModel  Newtonian;\n\n"
        + f"nu              [0 2 -1 0 0 0 0] {viscosity:g};\n"
    )


_TURBULENCE_PROPERTIES = (
    _foam_header("dictionary", "constant", "turbulenceProperties")
    + "simulationType  laminar;\n"
)


def _initial_velocity(velocity: float) -> str:
    return (
        _foam_header("volVectorField", "0", "U")
        + "dimensions      [0 1 -1 0 0 0 0];\n\n"
        + f"internalField   uniform ({velocity:g} 0 0);\n\n"
        + "boundaryField\n{\n"
        + "    farfield\n    {\n"
        + "        type            freestreamVelocity;\n"
        + f"        freestreamValue uniform ({velocity:g} 0 0);\n"
        + f"        value           uniform ({velocity:g} 0 0);\n"
        + "    }\n"
        + "    cylinder\n    {\n        type            noSlip;\n    }\n"
        + "    frontAndBack\n    {\n        type            empty;\n    }\n"
        + "}\n"
    )


_INITIAL_PRESSURE = (
    _foam_header("volScalarField", "0", "p")
    + "dimensions      [0 2 -2 0 0 0 0];\n\n"
    + "internalField   uniform 0;\n\n"
    + "boundaryField\n{\n"
    + "    farfield\n    {\n"
    + "        type            freestreamPressure;\n"
    + "        freestreamValue uniform 0;\n"
    + "        value           uniform 0;\n"
    + "    }\n"
    + "    cylinder\n    {\n        type            zeroGradient;\n    }\n"
    + "    frontAndBack\n    {\n        type            empty;\n    }\n"
    + "}\n"
)


_FV_SCHEMES = (
    _foam_header("dictionary", "system", "fvSchemes")
    + "ddtSchemes\n{\n    default         steadyState;\n}\n\n"
    + "gradSchemes\n{\n    default         Gauss linear;\n}\n\n"
    + "divSchemes\n{\n"
    + "    default         none;\n"
    + "    div(phi,U)      bounded Gauss linearUpwind grad(U);\n"
    + "    div((nuEff*dev2(T(grad(U))))) Gauss linear;\n"
    + "}\n\n"
    + "laplacianSchemes\n{\n    default         Gauss linear corrected;\n}\n\n"
    + "interpolationSchemes\n{\n    default         linear;\n}\n\n"
    + "snGradSchemes\n{\n    default         corrected;\n}\n"
)


_FV_SOLUTION = (
    _foam_header("dictionary", "system", "fvSolution")
    + "solvers\n{\n"
    + "    p\n    {\n"
    + "        solver          GAMG;\n"
    + "        smoother        GaussSeidel;\n"
    + "        tolerance       1e-07;\n"
    + "        relTol          0.01;\n"
    + "    }\n"
    + "    U\n    {\n"
    + "        solver          smoothSolver;\n"
    + "        smoother        symGaussSeidel;\n"
    + "        tolerance       1e-08;\n"
    + "        relTol          0.1;\n"
    + "    }\n"
    + "}\n\n"
    + "SIMPLE\n{\n"
    + "    nNonOrthogonalCorrectors 1;\n"
    + "    consistent      no;\n"
    + "    residualControl\n    {\n"
    + "        p               1e-05;\n"
    + "        U               1e-06;\n"
    + "    }\n"
    + "}\n\n"
    + "relaxationFactors\n{\n"
    + "    fields\n    {\n        p               0.3;\n    }\n"
    + "    equations\n    {\n        U               0.7;\n    }\n"
    + "}\n"
)


# --------------------------------------------------------------------------
# Result parsing
# --------------------------------------------------------------------------

def parse_force_coefficients(text: str) -> dict[str, float]:
    """Parse a forceCoeffs output table (coefficient.dat / forceCoeffs.dat).

    Header layout differs across OpenFOAM versions; the last comment line
    naming the columns is authoritative.  The steady value is the mean over
    the final 20% of iterations, and the oscillation of Cd over that window is
    exposed as ``Cd_oscillation`` — a direct numerical-convergence indicator.
    """
    header: list[str] = []
    rows: list[list[float]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            tokens = stripped.lstrip("#").split()
            if len(tokens) > 1:
                header = tokens
            continue
        try:
            rows.append([float(token) for token in stripped.split()])
        except ValueError:
            continue
    if not header or not rows:
        return {}
    columns = {name: index for index, name in enumerate(header)}
    window = rows[-max(2, len(rows) // 5):] if len(rows) > 1 else rows
    output: dict[str, float] = {}
    for source, target in (("Cd", "Cd"), ("Cl", "Cl"), ("CL", "Cl"), ("CD", "Cd")):
        index = columns.get(source)
        if index is None or target in output:
            continue
        values = [row[index] for row in window if index < len(row)]
        if not values:
            continue
        mean = sum(values) / len(values)
        output[target] = mean
        if target == "Cd" and len(values) > 1:
            variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
            output["Cd_oscillation"] = math.sqrt(variance)
    return output


def parse_solver_log(text: str) -> dict[str, float]:
    """Final residuals, iteration count, and convergence flag from a simpleFoam log."""
    residuals: dict[str, float] = {}
    iterations = 0.0
    converged = 0.0
    for line in text.splitlines():
        match = re.search(r"Solving for (\w+),.*Final residual = ([0-9.eE+-]+)", line)
        if match:
            residuals[match.group(1)] = float(match.group(2))
            continue
        match = re.match(r"Time = ([0-9]+)", line.strip())
        if match:
            iterations = float(match.group(1))
            continue
        match = re.search(r"solution converged in ([0-9]+) iterations", line)
        if match:
            iterations = float(match.group(1))
            converged = 1.0
    tracked = [value for key, value in residuals.items() if key in {"Ux", "Uy", "p"}]
    output = {
        "solver_iterations": iterations,
        "converged": converged,
    }
    if tracked:
        output["convergence_residual"] = max(tracked)
    return output


def parse_mesh_log(text: str) -> dict[str, float]:
    match = re.search(r"nCells:\s*([0-9]+)", text)
    return {"cell_count": float(match.group(1))} if match else {}


# --------------------------------------------------------------------------
# Real solver backend
# --------------------------------------------------------------------------

class OpenFoamCylinderApi:
    """Run blockMesh + simpleFoam on a generated cylinder case, one case per design."""

    PARAMETER_SPECS = PARAMETER_SPECS
    METRIC_SPECS = METRIC_SPECS

    def __init__(
        self,
        workdir: str | os.PathLike[str],
        *,
        bindir: str | os.PathLike[str] | None = None,
        run_prefix: Sequence[str] | None = None,
        timeout_s: float = 900.0,
        progress_sink: ProgressSink | None = None,
    ):
        self.workdir = Path(workdir).resolve()
        self.bindir = Path(bindir or os.environ.get("OPENFOAM_BINDIR", "")) if (bindir or os.environ.get("OPENFOAM_BINDIR")) else None
        prefix = run_prefix if run_prefix is not None else os.environ.get("OPENFOAM_RUN_PREFIX", "")
        self.run_prefix = list(prefix.split()) if isinstance(prefix, str) else list(prefix)
        self.timeout_s = timeout_s
        self._progress_sink = progress_sink
        self._artifacts: list[dict[str, Any]] = []

    def set_progress_sink(self, sink: ProgressSink | None) -> None:
        self._progress_sink = sink

    def evaluate(self, design: Mapping[str, float], analyses: Sequence[str]) -> Mapping[str, float]:
        case = self.workdir
        if case.exists():
            shutil.rmtree(case, ignore_errors=True)
        self._progress("case-setup", 0.05, "Generating parameterized OpenFOAM case")
        resolved = build_case(case, design)
        results: dict[str, float] = dict(resolved)
        results["Re"] = _reynolds(resolved)

        self._progress("meshing", 0.15, "Running blockMesh")
        mesh_log = self._run("blockMesh", case)
        results.update(parse_mesh_log(mesh_log))
        self._progress("mesh-ready", 0.30, f"Mesh complete ({int(results.get('cell_count', 0))} cells)")

        requested = set(analyses)
        if "geometry" in requested:
            results["geometry_valid"] = 1.0
        if "aerodynamics" in requested:
            self._progress("solving", 0.40, "Running simpleFoam to steady state")
            solver_log = self._run("simpleFoam", case)
            results.update(parse_solver_log(solver_log))
            self._progress("post-processing", 0.90, "Parsing force coefficients")
            coefficients = self._read_coefficients(case)
            if not coefficients:
                raise RuntimeError("simpleFoam produced no force-coefficient output")
            results.update(coefficients)
        self._progress("evidence-ready", 1.0, "Structured metrics and artifacts ready")
        return results

    def _run(self, tool: str, case: Path) -> str:
        executable = str(self.bindir / tool) if self.bindir else tool
        # The working directory *is* the case, so "-case ." keeps the command
        # portable across launcher prefixes (WSL, containers) whose filesystem
        # view translates the cwd but could not parse a host-native case path.
        command = [*self.run_prefix, executable, "-case", "."]
        log_path = case / f"log.{tool}"
        with log_path.open("w") as log:
            completed = subprocess.run(
                command,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=self.timeout_s,
                cwd=case,
            )
        text = log_path.read_text(errors="replace")
        self._artifacts.append(_artifact(log_path, f"{tool} log", "text/plain"))
        if completed.returncode != 0:
            tail = " ".join(text.splitlines()[-8:])
            raise RuntimeError(f"{tool} failed with code {completed.returncode}: {tail}")
        return text

    def _read_coefficients(self, case: Path) -> dict[str, float]:
        roots = (
            case / "postProcessing" / "forceCoeffs1",
            case / "postProcessing" / "forceCoeffs",
        )
        for root in roots:
            if not root.exists():
                continue
            candidates = sorted(root.rglob("*.dat")) + sorted(root.rglob("*.txt"))
            for path in candidates:
                parsed = parse_force_coefficients(path.read_text(errors="replace"))
                if parsed:
                    self._artifacts.append(_artifact(path, "Force coefficients", "text/openfoam-forcecoeffs"))
                    return parsed
        return {}

    def close(self) -> None:
        return None

    def artifacts(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._artifacts if Path(str(item.get("path", ""))).exists()]

    def _progress(self, phase: str, progress: float, detail: str) -> None:
        if self._progress_sink:
            self._progress_sink({
                "phase": phase,
                "progress": max(0.0, min(1.0, float(progress))),
                "detail": detail,
            })


# --------------------------------------------------------------------------
# Deterministic development backend
# --------------------------------------------------------------------------

class SyntheticOpenFoamApi:
    """Deterministic cylinder-flow stand-in for machines without OpenFOAM.

    Drag follows the classical empirical correlation Cd ≈ 1 + 10·Re^(-2/3)
    (steady laminar range), with a second-order mesh-convergence error term so
    ``mesh_refinement`` genuinely trades cost against accuracy, and a
    convergence penalty above the steady-wake limit (Re ≈ 47) so the chief can
    learn the feasibility boundary.  Not a physics substitute.
    """

    def __init__(self, defaults: Mapping[str, float] | None = None, latency_s: float = 0.0):
        self.defaults = dict(DEFAULT_DESIGN)
        if defaults:
            self.defaults.update({key: float(value) for key, value in defaults.items()})
        self.latency_s = max(0.0, float(latency_s))

    def evaluate(self, design: Mapping[str, float], analyses: Sequence[str]) -> Mapping[str, float]:
        if self.latency_s:
            time.sleep(self.latency_s)
        p = {**self.defaults, **{key: float(value) for key, value in design.items()}}
        reynolds = _reynolds(p)
        refinement = max(p["mesh_refinement"], 0.1)
        drag = (1.0 + 10.0 * reynolds ** (-2.0 / 3.0)) * (1.0 + 0.12 / refinement ** 2)
        lift = 0.001 * math.tanh(reynolds / 100.0)
        residual = min(1.0, 1e-6 * math.exp(max(0.0, reynolds - 47.0) / 12.0))
        converged = 1.0 if residual <= 1e-5 else 0.0
        iterations = round(250.0 * (1.0 + refinement) + reynolds)
        cells = float(4 * max(8, round(_BASE_RADIAL_CELLS * refinement)) * max(8, round(_BASE_TANGENTIAL_CELLS * refinement)))
        results = dict(p)
        results.update({
            "Cd": round(drag, 6),
            "Cl": round(lift, 6),
            "Re": round(reynolds, 4),
            "convergence_residual": residual,
            "converged": converged,
            "solver_iterations": float(iterations),
            "cell_count": cells,
        })
        if "geometry" in set(analyses):
            results["geometry_valid"] = 1.0
        return results

    def close(self) -> None:
        return None

    def artifacts(self) -> list[dict[str, Any]]:
        return []


# --------------------------------------------------------------------------
# Registration
# --------------------------------------------------------------------------

MANIFEST = AdapterManifest(
    name="openfoam-cylinder2d",
    version="phase-1",
    analyses=("geometry", "aerodynamics"),
    input_parameters=tuple(spec.name for spec in PARAMETER_SPECS),
    output_metrics=tuple(spec.name for spec in METRIC_SPECS),
    artifact_types=("design-state/json", "text/plain", "text/openfoam-forcecoeffs"),
    concurrency="isolated-process",
    parameter_specs=PARAMETER_SPECS,
    metric_specs=METRIC_SPECS,
    domain_dependencies=DOMAIN_DEPENDENCIES,
)


def openfoam_registry(
    work_root: str | os.PathLike[str] | None = None,
    *,
    synthetic: bool | None = None,
) -> SoftwareAdapterRegistry:
    """Registry exposing the cylinder case to the chief.

    ``synthetic=None`` auto-detects: the real backend when the OpenFOAM
    toolchain is reachable, the deterministic stand-in otherwise.
    """
    use_synthetic = (not available()) if synthetic is None else bool(synthetic)
    root = Path(work_root or os.environ.get("OPENFOAM_WORK_ROOT", "openfoam-runs")).resolve()
    counter = {"next": 0}

    def factory(handle) -> Any:
        if use_synthetic:
            return SyntheticOpenFoamApi()
        counter["next"] += 1
        worker = getattr(handle, "vm_id", None) or getattr(handle, "id", None) or f"worker-{counter['next']:03d}"
        return OpenFoamCylinderApi(root / str(worker) / f"case-{counter['next']:04d}")

    registry = SoftwareAdapterRegistry()
    registry.register(MANIFEST, factory)
    return registry


def _reynolds(design: Mapping[str, float]) -> float:
    return (
        design["inlet_velocity"] * design["cylinder_diameter"]
        / max(design["kinematic_viscosity"], 1e-12)
    )


def _artifact(path: Path, label: str, kind: str) -> dict[str, Any]:
    return {
        "name": path.name,
        "label": label,
        "kind": kind,
        "path": str(path.resolve()),
        "bytes": path.stat().st_size if path.exists() else 0,
    }
