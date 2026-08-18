# Reproducer bundle: `mesh.warpDeriv` mis-linearizes the surface-to-volume mesh warp

Companion to `../UPSTREAM_BUG_REPORT_mesh_warpDeriv.md`. **Nothing here has been sent anywhere.**

Everything in this directory has been executed end-to-end from a **fresh `git clone` of the
official upstream tutorials repository, outside this project's tree**, on 2026-07-31. Nothing
depends on any file, patch, mesh, or setting from this project. The two reproducers use only:

- the official image `dafoam/opt-packages:latest`, and
- the official `DAFoam/tutorials` repository at a pinned commit,

and each is a **single self-contained Python file dropped into the tutorial's own case directory
after that tutorial's own `preProcessing.sh` has run.** No tutorial file is edited by either one.

## Exact environment used for every number in the report

| component | version |
|---|---|
| Docker image | `dafoam/opt-packages:latest`, digest `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` |
| OpenFOAM | `v2506`, build `_615aae61d7-20250627` |
| `dafoam` | 5.0.0 |
| `idwarp` | **2.6.2** (the package containing the function under test) |
| `pygeo` | 1.13.0 |
| `pyspline` | 1.5.2 |
| `mphys` | 1.1.0 |
| `openmdao` | 3.26.0 |
| `petsc4py` | 3.15.5 |
| `mpi4py` | 4.1.1 |
| `numpy` | 1.23.5 |
| Python | 3.10.8 |
| tutorials | `https://github.com/DAFoam/tutorials.git` @ `d3b7e38b058aba2a98a74092e15c41ec455c570d` (2026-05-16) |
| host | AWS Linux, 16 vCPU / 32 GiB |

## Files

| file | what it is |
|---|---|
| `repro_warpderiv_ubend.py` | **Primary reproducer.** `UBend_Channel`, 4,800 cells. Plain single-point single-axis `nom_addLocalDV` design variables. Tests all 27 components at once. Runs in ~15 s including the primal and adjoint. |
| `repro_warpderiv_airfoil.py` | Secondary reproducer. `NACA0012_Airfoil/incompressible`, 4,032 cells. Opposing-direction `addShapeFunctionDV` combination modes. Pure geometry, **no CFD solve at all**, runs in seconds. |
| `run_repro.sh` | Clone-to-result driver for both, from nothing. |

## Quick start (both cases, from nothing)

```bash
./run_repro.sh              # clones, meshes, runs, prints the tables below
```

or, by hand:

```bash
git clone https://github.com/DAFoam/tutorials.git
cd tutorials && git checkout d3b7e38b058aba2a98a74092e15c41ec455c570d && cd ..

CASE=tutorials/UBend_Channel
cp repro_warpderiv_ubend.py "$CASE"/
cd "$CASE"

DOCK="docker run --rm --cpus=4 --memory=6g -v $(pwd):/home/dafoamuser/mount \
      -w /home/dafoamuser/mount dafoam/opt-packages:latest bash -lc"

$DOCK 'source /home/dafoamuser/dafoam/loadDAFoam.sh && ./preProcessing.sh'

# the test you would naturally write -- reports the function CLEAN
$DOCK 'source /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun --allow-run-as-root -np 4 \
       python repro_warpderiv_ubend.py --seed random'

# the same analytic call, contracted with the seed the real adjoint actually uses
$DOCK 'source /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun --allow-run-as-root -np 4 \
       python repro_warpderiv_ubend.py --seed real'
```

Between runs, remove `processor*` and any numbered time directories the solver wrote
(**not** `0/` or `0.orig/`), or DAFoam's `renameSolution` aborts with `already exists, moving
failed!` on the next invocation.

## What the reproducers measure

`mesh.warpDeriv` is a reverse-mode Jacobian-transpose-vector product: given a seed `w` in
volume-mesh-coordinate (`Xv`) space it returns `w^T (dXv/dXs)` in surface-coordinate (`Xs`) space.
It exposes no forward Jacobian column, so it is checked against a pure finite difference of the
nonlinear warp it claims to differentiate, using the standard dot-product identity, per design
variable `idx`:

```
<w, dXv/dShape_idx>_FD   ==   <warpDeriv(w), dXs/dShape_idx>_analytic
```

The FD side perturbs the **surface** coordinates directly along `eta = dXs/dShape_idx` and calls
`mesh.warpMesh()`. `DVGeo.update()` is never called on that side, so the FFD parameterization
cannot contribute to the measurement and `warpDeriv` is exercised alone. `--fd-via-dvgeo` runs the
composed variant as well; the two agree to `1e-7`–`1e-11` in every configuration tested, which is
the check that FFD nonlinearity is not the explanation.

## The seed is the whole point

`--seed random` contracts the error with an arbitrary direction. `--seed real` contracts it with
the vector the real adjoint actually passes to this function: the objective's own reverse-mode
`d(OBJ)/dXv`, captured verbatim by hooking `DAFoamWarper.compute_jacvec_product`, which is where
`mphys_dafoam.py` calls `self.DASolver.mesh.warpDeriv(dxV)`.

**The analytic side is byte-identical in the two runs. Only the direction it is contracted against
changes.** A random-seed test of this function does not clear it — the difference between the two
runs is the bug's *visibility*, not its existence. This is not a hypothetical caution: a
random-seed test of exactly this form cleared the U-bend case in this lab on 2026-07-29, and that
clearance was wrong and has been retracted.

As a validity check the script prints, next to each analytic scalar, the framework's own
`compute_totals` column for the same component. They agree to `~1e-15`, which confirms both that
the captured seed is the real one and that the disagreement is not in OpenMDAO's assembly.

## Results, as produced by the commands above

### 1. `UBend_Channel`, tutorial's own objective, **not one character changed**

`--objective stock` (the default), `--seed real`, `h=1e-4`, `np=4`. Log:
`repro_ubend_stock_real_np4.log`.

Errors span 0.5% to **80.8%**, and **13 of 27 components exceed 30%**. No sign flips at this
objective. The same run with `--seed random` (`repro_ubend_stock_random_np4.log`) reports **20 of
27 components under 4%** and a worst case of 60.6%.

| idx | FD(warp) | AN(`warpDeriv`) | rel. err |
|---|---|---|---|
| 21 | -1.35428608e-02 | -2.60189995e-03 | **80.8%** |
| 17 | 4.73834770e-02 | 1.53530191e-02 | **67.6%** |
| 13 | -1.62414143e-02 | -7.17551784e-03 | **55.8%** |
| 12 | -1.01274691e-01 | -4.79974181e-02 | **52.6%** |
| 14 | 7.16305550e-02 | 3.51892681e-02 | **50.9%** |
| ... | | | (full 27-row table in the log) |
| 2 | -1.04166347e-02 | -1.04708718e-02 | 0.5% |

### 2. `UBend_Channel`, one-line objective change, **sign flips**

`--objective pressure-loss` replaces the tutorial's weighted `scalePL*(TP1-TP2) + scaleHFX*HFX`
with `val = TP1 - TP2` and sets `HFX`'s `addToAdjoint` to `False`. That is the entire diff, it is
applied by a flag rather than by editing the tutorial, and it is a physically ordinary objective
(total pressure loss through a duct). `--seed real`, `h=1e-4`, `np=4`. Log:
`repro_ubend_pressureloss_real_np4.log`.

| idx | FD(warp) | AN(`warpDeriv`) | rel. err | sign | FFD-nonlinearity control |
|---|---|---|---|---|---|
| 2 (control) | -4.06880154e-01 | -4.17657510e-01 | 2.65% | ok | 8.59e-07 |
| 3 | 7.08623060e-01 | 1.96883727e+00 | **177.8%** | ok | 1.71e-06 |
| **8** | 7.87898342e-01 | **-8.43372580e-01** | **207.0%** | **FLIP** | 1.01e-07 |
| 15 | -2.42564294e+01 | -1.38604167e+01 | **42.9%** | ok | 3.83e-08 |
| **17** | 2.91315567e+00 | **-6.28812054e-01** | **121.6%** | **FLIP** | 2.98e-07 |
| 26 (control) | -1.89917527e+00 | -1.95653977e+00 | 3.02% | ok | 1.25e-06 |

The same six components with `--seed random` (`repro_ubend_pressureloss_random_np4.log`):
**0.01% – 40.7%, zero sign flips.** idx8 measures 0.32% and idx17 measures 1.30% — the two
components that are 207% and 122% wrong under the real seed.

`AN(warpDeriv)` in this table equals the framework's own `compute_totals` column exactly, and the
`FD(warp)` column reproduces the tutorial's own `check_totals` finite-difference column to
0.07%–1.5% — so this solve-free geometric test is measuring the same disagreement a full
`check_totals` sweep measures, decomposed to show which link owns it.

**These design variables are `nom_addLocalDV(dvName=..., pointSelect=PS, axis="x")` — one FFD
control point moving along one axis, unconditionally.** There is no opposing-direction or
multi-point construction anywhere in this case.

### 3. `NACA0012_Airfoil/incompressible`, unmodified, pure geometry, no CFD

`repro_warpderiv_airfoil.py`, `--seed 2026`, `h=1e-4`, `np=4`, run on a freshly cloned and freshly
meshed tutorial:

| idx | construction | FD_scalar | AN_scalar | rel. err | sign |
|---|---|---|---|---|---|
| 4 | single-station (control) | 4.852993e+02 | 4.968000e+02 | 2.37% | agree |
| **6** | combination (LE) | 1.313376e+01 | **-1.559997e+00** | **111.9%** | **FLIP** |
| **7** | combination (TE) | -7.434965e+00 | **1.059256e+00** | **114.2%** | **FLIP** |

These are bit-identical to the numbers already in the bug report, which were obtained on a
different copy of the case months earlier — the result is stable across independent setups.

## Reading the two cases together

| | NACA0012 | UBend_Channel |
|---|---|---|
| flow | external, 2D airfoil | internal, 3D curved duct (half-model) |
| mesh | 4,032 cells, `pyHyp` hyperbolic C-mesh | 4,800 cells, 6-block `blockMesh` |
| objective | drag force integral | total-pressure loss / wall heat flux |
| DV API | `addShapeFunctionDV`, opposing-direction pairs | `addLocalDV`, one point, one axis |
| `symmetryPlanes` | two declared | `[]` (empty, as the tutorial ships it) |
| result | sign flips at 108–149% | sign flips at 122–207% |

Two unrelated meshes, two mesh generators, two objective types, two design-variable APIs, opposite
symmetry-plane configurations. The one thing they share is `mesh.warpDeriv`.
