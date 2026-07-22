# OpenFOAM adapter (phase 1)

Certonomous's second real engineering adapter after OpenVSP: CFD missions driven
through OpenFOAM, with the chief's epistemic-uncertainty verdicts
(`docs/UNCERTAINTY.md`) applying to every CFD metric automatically.

## The case

2D steady laminar flow past a circular cylinder — an O-grid `blockMesh`
annulus (cylinder wall → circular farfield at 10 diameters), solved with
`simpleFoam`, forces via the `forceCoeffs` function object. The entire case is
generated from Python (`sdk/chief_engineer/openfoam.py`): no template files,
STL geometry, or snappyHexMesh.

Design parameters (adapter-declared, so the chief's generic specialists
explore them with no CFD-specific code):

| Parameter | Range | Domain |
|---|---|---|
| `cylinder_diameter` | 0.5–2.0 m | geometry |
| `inlet_velocity` | 0.5–4.0 m/s | flow |
| `kinematic_viscosity` | 0.01–0.2 m²/s | flow |
| `mesh_refinement` | 0.5–3.0× | numerics |

Metrics: `Cd`, `Cl`, `Re`, `convergence_residual`, `converged`,
`solver_iterations`, `cell_count` (plus `Cd_oscillation` from the real
solver's final-window statistics). Convergence is a first-class metric on
purpose: the steady wake breaks down above Re ≈ 47, and the chief should
constrain missions to trustworthy evidence — e.g.

```
Minimize drag while keeping convergence_residual below 0.00001
```

— rather than silently averaging a non-converged solve.

## Backends

- **`OpenFoamCylinderApi`** — real solvers by subprocess, one generated case
  per design. Binary resolution: PATH, `OPENFOAM_BINDIR`, or
  `OPENFOAM_RUN_PREFIX` (a launcher prefix such as a container or WSL shim).
- **`SyntheticOpenFoamApi`** — deterministic stand-in on the classical
  empirical drag correlation Cd ≈ 1 + 10·Re^(−2/3), with a second-order
  mesh-convergence error term and a convergence penalty past Re ≈ 47. Runs
  missions and tests on machines without OpenFOAM. Not a physics substitute.

`openfoam_registry(synthetic=None)` auto-detects which backend is available.

## Run a CFD mission

```python
from chief_engineer.mission import AutonomousChief
from chief_engineer.openfoam import openfoam_registry

registry = openfoam_registry()          # auto-detects real vs synthetic
chief = AutonomousChief(
    "cfd-mission",
    api_factory=registry.composite_factory(),
    parameter_specs=registry.parameter_specs(),
    metric_specs=registry.metric_specs(),
    domain_dependencies=registry.domain_dependencies(),
    domain_parameter_counts=registry.domain_parameter_counts(),
)
outcome = chief.run("Minimize drag while keeping convergence_residual below 0.00001")
print(outcome.uncertainty.narration)    # the chief's sure / not-sure verdicts
```

## Container worker

`sdk/docker/Dockerfile.openfoam-worker` builds an isolated worker on the
official `opencfd/openfoam-default` image, reusing the OpenVSP worker's HTTP
control plane — `worker_server` now selects its adapter via
`WORKER_ADAPTER=openfoam-cylinder2d`, so the fleet and controller are
unchanged.

```bash
cd sdk
docker build -f docker/Dockerfile.openfoam-worker -t certonomous-openfoam-worker:2412 .
```

## Validation status

**Validated end-to-end against real OpenFOAM v2606** (WSL2 Ubuntu, 2026-07-19):
the generated O-grid meshes cleanly and the steady laminar drag matches the
experimental literature (Tritton):

| Case | Cd (simpleFoam) | Literature | Result |
|---|---|---|---|
| Re = 10 | 3.011 | ≈ 2.8–3.0 | pass |
| Re = 20 | 2.161 | ≈ 2.0–2.2 | pass |
| Re = 30 | 1.815 | ≈ 1.7–1.8 | pass |
| Re = 40 | 1.618 | ≈ 1.5–1.7 | pass |
| Re = 200 | — | unsteady regime | correctly flagged `converged = 0` |

Grid study at Re = 20: 600 → 2400 → 9600 → 21600 cells gives Cd 2.191 →
2.161 → 2.156 → 2.158 (asymptote ≈ 2.156; 1.6% coarse-grid error). Lift is
O(1e-6) in all steady cases (symmetric flow).

**Known subtlety — convergence is not physical validity.** At Re = 100 the
steady solver *converges* (residual 1e-7) onto the symmetric steady branch,
which is unstable in reality above Re ≈ 47: the physical flow sheds vortices
and its time-averaged Cd (≈ 1.3–1.4) exceeds the steady-branch value (1.181
computed). `converged = 1` therefore certifies the numerics, not the regime;
missions exploring above Re ≈ 47 need the unsteady (pimpleFoam) track on the
roadmap. Re = 200 does not even reach the steady branch and is honestly
reported unconverged.

Case generation, both result parsers, solver-log convergence detection, the
synthetic backend, and a full synthetic mission with uncertainty verdicts are
covered by `sdk/tests/test_openfoam.py`.

### Running through WSL (Windows host)

With OpenFOAM installed in a WSL distro, no code changes are needed — the
launcher prefix translates everything:

```bash
export OPENFOAM_RUN_PREFIX="wsl -d Ubuntu -- openfoam2606"
```

The adapter invokes solvers with `-case .` from inside each case directory,
so WSL's automatic `/mnt/c` path translation does the rest.

## Roadmap

- Unsteady missions: `pimpleFoam` above Re ≈ 47 with time-averaged
  coefficients and shedding amplitude as metrics.
- Turbulent external aero (kOmegaSST) and an airfoil case with
  angle-of-attack as a design parameter.
- Mesh-convergence (GCI) as a second uncertainty channel alongside the
  epistemic GP layer — numerical error vs sampling error, reported separately.
- snappyHexMesh for arbitrary geometry from CAD artifacts.
