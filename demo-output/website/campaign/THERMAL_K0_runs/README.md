# THERMAL_K0_runs — rung K0 of the cooling ladder, campaign F14

Cases, scripts and logs for **K0a** (feasibility) and **K0b** (physics) of the
cooling / buoyancy ladder, run 2026-08-17 with `buoyantBoussinesqSimpleFoam`,
OpenFOAM v2606, laminar, steady, serial.

- Predictions, written before anything ran: `../THERMAL_K0_PREREGISTRATION.md`
- Outcomes: `../THERMAL_K0_RESULTS.md`
- The standing heat-balance check built here: `../../../../scripts/heat_balance.py`

> **These are CAPABILITY rungs.** They show the solver runs and that its watts
> balance. They are validated against **no published reference datum** and carry
> **no** claim about the world. Nothing here goes on the wall, the website,
> application materials or any external surface as a result, and no data-center
> or cooling language attaches to it. The validation gate is **K0c**, which was
> not in this dispatch and was not run.

> **Campaign label: F14, ruled 2026-08-17.** This work was dispatched as "F11",
> but `F11` was already the 2026-07-30 lid-driven-cavity verification ladder
> (`../F11_lid_driven_cavity_ladder.md`, `../F11_runs/`), which keeps the tag by
> precedence. The cooling campaign is **F14**; its gate specifications live at
> `../../../../docs/campaigns/F14-cooling-ladder/`. `THERMAL_K0` is a physics
> name, it never collided, and it does not change.

## Cases

| directory | what it is | cells | role |
|---|---|---:|---|
| `K0a_heated_box/` | 2D box, hot floor strip, cold ceiling, adiabatic sides | 400 | **K0a**, the feasibility rung |
| `K0a_heated_box_g0/` | identical but `g = 0` | 400 | control C1: pure conduction, so the Nusselt ratio is a real advection test and the "no motion" zero has a meaning |
| `K0a_heated_box_source/` | identical but with a planted 5.000e-03 W volumetric source in `constant/fvOptions` | 400 | control C3b: the auditor's positive control — it must report a large, exactly predicted imbalance |
| `K0b_cavity_Ra1e5/` | differentially heated square cavity, Ra = 1.000e+05 | 4096 | **K0b**, the physics rung |
| `K0b_cavity_g0/` | identical but `g = 0` | 4096 | control C2: exact 1-D conduction, used to calibrate the auditor against a closed-form answer |

## Scripts

| file | what it does |
|---|---|
| `build_cases.py` | writes all five case trees from one place. Fluid properties, geometry and the dT that lands on Ra = 1e5 live here and nowhere else. |
| `run_cases.sh` | meshes and solves. Copies `0.orig/` to `0/`, runs `blockMesh`, `checkMesh`, then the solver, and reports wall clock per case. |
| `run_controls.sh` | the headline audits and all five controls, each printing its **anchor readback** before its measurement. Writes `log.controls`. |
| `analyse.py` | the physics measurements — Nusselt ratios, plume velocities, core stratification — plus residual histories. Writes `analysis.json` and `log.analysis`. |

Order: `build_cases.py` → `run_cases.sh` → `run_controls.sh` → `analyse.py`.
`analyse.py` reads the JSON that `run_controls.sh` writes, so that order matters.

## What travels in git, and what does not

Travels: `system/` and `constant/` dictionaries, `0.orig/` initial conditions,
`log.*`, `audit/*.json`, `analysis.json`, the scripts, this README.

Does not travel, by repo policy, and is rebuilt by `run_cases.sh`:
`constant/polyMesh/`, `0/`, every numbered time directory, `postProcessing/`.

Initial conditions are kept in **`0.orig/`** rather than `0/` because the repo's
ignore rule `demo-output/website/campaign/*_runs/*/[0-9]*/` correctly excludes
solver time directories and `0/` matches it. `0.orig/` is re-included by an
explicit negation in `.gitignore`.

The five cases were left holding only the time directories this record cites
(`0` and the final time; plus 10, 20, 50, 100, 500 for K0b, which the C3 control
reads). The rest — 244 MB of them — were deleted; `run_cases.sh` regenerates
them.

## Reproducing

```bash
cd demo-output/website/campaign/THERMAL_K0_runs
python3 build_cases.py
./run_cases.sh                 # ~51 s wall on one core, all five cases
./run_controls.sh              # exit 0 = every control behaved
python3 analyse.py
```

Read the exit status of `run_controls.sh` directly. Do not pipe it into `head`
or `tail` and read that — you get the pipe's status, not the check's, and this
lab has been burned by exactly that.
