# OpenFOAM adapter (phase 1)

> ## RE-SCOPE NOTE — 2026-08-23 (cfd team)
>
> **This document was written for a Windows host driving OpenFOAM through WSL2.
> This box is not that machine.** The engineering content below (the cylinder
> case, the backends, the validation table) is unchanged and still stands; the
> *launch instructions* are the stale part. Read this note before following any
> command in this file.
>
> **What is true on this box, verified 2026-08-23:**
>
> - **Host:** native Linux — Ubuntu 24.04.4 LTS, kernel `7.0.0-1010-aws`, on one
>   AWS instance. There is no WSL (`wsl` is not on `PATH`; no Windows host).
> - **OpenFOAM:** **v2606, dpkg-installed, at `/usr/lib/openfoam/openfoam2606`**
>   — the *only* install on the box. `dpkg -S
>   /usr/lib/openfoam/openfoam2606/etc/bashrc` → `openfoam2606-common`.
>   Corroborated at `docs/OPENFOAM_SOLVER_BUILD.md:78`. **The v2606 claim in the
>   validation table below is therefore VALID**; only its "(WSL2 Ubuntu)"
>   parenthetical is historical.
> - **How solvers are launched here.** The Bash tool runs **non-login** shells,
>   so `/etc/profile.d/openfoam-selector.sh` never executes and **OpenFOAM
>   binaries are not on `PATH`** (`command -v simpleFoam` → nothing). The
>   environment must be sourced **in the same shell invocation as the launch**,
>   never in a preceding call:
>
>   ```bash
>   source /usr/lib/openfoam/openfoam2606/etc/bashrc "" && simpleFoam -case . ...
>   ```
>
>   After sourcing, `simpleFoam` resolves to
>   `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/simpleFoam`.
>   The launcher form `openfoam2606 -c '<cmds>'` (`/usr/bin/openfoam2606`, from
>   `openfoam-selector`) is the equivalent one-shot; it is a launcher, not a shell
>   you stay in (`docs/OPENFOAM_SOLVER_BUILD.md` §3).
>
>   **This trap has already cost a run.** The first DPW8_V2 L4 relaunch died
>   instantly with `nohup: failed to run command 'simpleFoam'` for exactly this
>   reason, and the `OPENFOAM_RUN_PREFIX` export in the WSL subsection below
>   (cited there as `docs/OPENFOAM.md:118`, before this note shifted the line
>   numbering) was identified as a Windows/WSL instruction that must not be
>   used on this box — see
>   `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_PREREGISTRATION.md`
>   §9 (Operational notes) item 1.
>
> **What is stale below, and marked in place rather than deleted:**
>
> 1. **"Container worker"** — `sdk/docker/Dockerfile.openfoam-worker`
>    **does not exist** on this box, and `sdk/docker/` does not exist either
>    (nor is any such path tracked in git). Its build command cannot run.
> 2. **"Running through WSL (Windows host)"** — HISTORICAL. The
>    `OPENFOAM_RUN_PREFIX="wsl -d Ubuntu -- openfoam2606"` line is a
>    Windows/WSL-host instruction and is **inapplicable here**.
>
> Nothing in this note asserts a capability that was not checked on disk on the
> date given. Sections are marked, not removed, so the Windows-phase record and
> any external citation of it survive.

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
  *(2026-08-23: the three-way resolution in `sdk/chief_engineer/openfoam.py` is
  real and unchanged. On THIS box the WSL-shim form of `OPENFOAM_RUN_PREFIX` is
  inapplicable — see the re-scope note at the top; the native equivalents are
  sourcing `/usr/lib/openfoam/openfoam2606/etc/bashrc` in the same invocation,
  or the bare launcher `openfoam2606`, which `scripts/demo_servers.sh:36`
  already defaults to.)*
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

## Container worker — ARTIFACT DOES NOT EXIST ON THIS BOX (2026-08-23)

> **Do not run the build command in this section.** Verified 2026-08-23:
> `sdk/docker/Dockerfile.openfoam-worker` does not exist, the directory
> `sdk/docker/` does not exist, and `git ls-files sdk/docker` is empty — the file
> is not tracked and no commit ever carried it. `docker` is installed
> (`/usr/bin/docker`), so the command will *start* and then fail on the missing
> `-f` target. The section is kept as the record of an intended design, not as a
> live instruction. Nothing in this repository depends on the image existing.

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

**Validated end-to-end against real OpenFOAM v2606** (WSL2 Ubuntu, 2026-07-19
— *the WSL2 host is historical; the v2606 version claim holds on this box, where
the same v2606 is dpkg-installed at `/usr/lib/openfoam/openfoam2606`. These
numbers were produced on the Windows-phase machine and have not been re-run
here*):
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

### Running through WSL (Windows host) — HISTORICAL, NOT THIS BOX (2026-08-23)

> **This subsection describes the Windows-host phase and does not apply here.**
> This box is native Linux (Ubuntu 24.04.4, kernel `7.0.0-1010-aws`); `wsl` is
> not on `PATH` and there is no Windows host or `/mnt/c`. The export below was
> identified in
> `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_PREREGISTRATION.md` §9
> item 1 as an instruction that nearly misled the L4 relaunch — **do not use
> it.** The native equivalent is in the re-scope note at the top of this file:
> source `/usr/lib/openfoam/openfoam2606/etc/bashrc` in the *same* shell
> invocation as the launch. Retained verbatim below as the Windows-phase record.

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
