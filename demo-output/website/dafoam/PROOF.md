# DAFoam install and run proof

Date: 2026-07-26 (host time, AWS Linux, 16 vCPU / 30 GiB RAM instance)

## 1. Docker install

Installed via the approved apt route:

```
sudo apt-get update
sudo apt-get install -y docker.io
```

Result:

```
$ docker --version
Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2
```

`sudo systemctl status docker` showed `Active: active (running)`. The `ubuntu` user was NOT added to the
`docker` group (avoids needing a fresh login session); all docker commands below were run with `sudo`
consistently, as permitted by the task instructions.

## 2. Image pull

```
sudo docker pull dafoam/opt-packages:latest
```

Full pull log is in `pull.log`. Result:

```
latest: Pulling from dafoam/opt-packages
097ae9f9e9f3: Pull complete
Digest: sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc
Status: Downloaded newer image for dafoam/opt-packages:latest
docker.io/dafoam/opt-packages:latest
```

- Tag pulled: `dafoam/opt-packages:latest`
- Image digest: `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`
- Size as reported by `docker images` (decompressed on-disk size): **9.93 GB**
- Content size as reported by `docker images` (registry/compressed layer size): **2.1 GB**
- `docker image inspect` virtual size: 2097540464 bytes (~2.10 GB)
- Image build date (from inspect `.Created`): 2026-07-12T13:18:30Z

Internally the image reports:
- DAFoam version: **v5.0.0**
- OpenFOAM version: **v2506** (build `_615aae61d7-20250627`)

## 3. Proof case

No standalone `tutorials/` directory ships inside the image itself (it ships the DAFoam/OpenFOAM/PETSc/pyOptSparse/
pyGeo/MDO-Lab toolchain under `/home/dafoamuser/dafoam/`, not the tutorials repo). The tutorials repo
(`https://github.com/DAFoam/tutorials`, commit `d3b7e38b058aba2a98a74092e15c41ec455c570d`, 2026-05-16) was cloned
on the host and the case directory `NACA0012_Airfoil/incompressible` was bind-mounted into the container as the
work directory. This is standard DAFoam usage (the docker image is the solver/toolchain; tutorial cases are
supplied separately and mounted in).

**Case:** NACA0012 airfoil, low-speed incompressible RANS, Spalart-Allmaras turbulence model
(solver `DASimpleFoam`, i.e. SIMPLE steady-state incompressible solver with adjoint support).

**Mesh:** generated in-container with `pyHyp` (hyperbolic extrusion) from the case's `genAirFoilMesh.py`.
Actual measured mesh size, printed by the mesh generator itself (see `preproc_stdout.log` /
`work/NACA0012_Airfoil_Incompressible/logMeshGeneration.txt`):

```
nPoints for PS:  33
nPoints for SS:  33
nPoints for TE:  5
nPoints Total:  127
Mesh cells:  4032
```

So the primal/adjoint case has **4032 cells** (126 surface segments x 32 extrusion layers x 1 spanwise cell).

Flow conditions: U0 = 10 m/s, angle of attack = 5.13918623195176 deg, p0 = 0, nuTilda0 = 4.5e-5.
Functions of interest: CD (drag coefficient) and CL (lift coefficient), both defined as force-based
patch integrals over the `wing` patch.

## 4. Exact command sequence

All commands run as root inside the container (default image user), with the DAFoam environment sourced
from the image's own loader script:

```bash
# 1. install docker
sudo apt-get update && sudo apt-get install -y docker.io

# 2. pull image
sudo docker pull dafoam/opt-packages:latest

# 3. get the tutorial case (host side)
git clone --depth 1 https://github.com/DAFoam/tutorials.git
cp -r tutorials/NACA0012_Airfoil/incompressible  work/NACA0012_Airfoil_Incompressible

# 4. mesh generation (inside container)
sudo docker run --rm \
  -v <host>/work:/home/dafoamuser/mount \
  -w /home/dafoamuser/mount/NACA0012_Airfoil_Incompressible \
  dafoam/opt-packages:latest \
  bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh && ./preProcessing.sh'

# 5. primal + adjoint + total derivatives (compute_totals task)
sudo docker run --rm \
  -v <host>/work:/home/dafoamuser/mount \
  -w /home/dafoamuser/mount/NACA0012_Airfoil_Incompressible \
  dafoam/opt-packages:latest \
  bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh && \
            mpirun --allow-run-as-root -np 4 python runScript.py -task compute_totals'

# 6. adjoint-vs-finite-difference validation (check_totals task)
sudo docker run --rm \
  -v <host>/work:/home/dafoamuser/mount \
  -w /home/dafoamuser/mount/NACA0012_Airfoil_Incompressible \
  dafoam/opt-packages:latest \
  bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh && \
            mpirun --allow-run-as-root -np 4 python runScript.py -task check_totals'
```

Run 5 used 4 MPI ranks and completed in about 12.5 s of solver wall time (per the DAFoam-printed
`ExecutionTime`/timestamps in the log). Run 6 (finite-difference check) additionally reruns the primal
20 more times (central differences over the 10 design variables: 8 FFD shape variables + 2 flow variables
`[U0, AoA]`), for 21 total clean primal convergences across the two runs' overlapping baseline solve.

## 5. Real output: primal convergence

From `compute_totals_run1.log` (task `compute_totals`), the SIMPLE primal iterates and converges:

```
Time = 1     CD: 0.5135187891611549   CL: -0.04678609117213162
Time = 100   CD: 0.02199683668203143  CL: 0.4819232639265035
Time = 200   CD: 0.02094056970378843  CL: 0.4981695393862557
Time = 300   CD: 0.02091159294474717  CL: 0.4987468170490384
Time = 400   CD: 0.02091052894554104  CL: 0.4987649965352308
Time = 435   CD: 0.02091050986768742  CL: 0.4987652660392374
Minimal residual 9.716836625388712e-09 satisfied the prescribed tolerance 1e-08
```

Final residual statistics printed by the solver at convergence:

```
U Residual Norm2: (0.0002100417560633355 0.0002334620581360085 1.122999306626796e-12)
p Residual Norm2: 7.15098536250842e-05
nuTilda Residual Norm2: 8.963377556924731e-08
phi Residual Norm2: 3.228322394661262e-07
Total Residual Norm2: 0.0003220804919575545
```

**Converged objective values (run 5, task `compute_totals`):**
- CD = 0.02091050986768742
- CL = 0.4987652660392374

(A second independent run of the same case for the FD check, run 6, converged to CD = 0.02090808872445526,
CL = 0.4986761696487447; consistent to 4 significant figures, small difference is expected since it's a
distinct primal solve reaching the same 1e-8 residual tolerance from the same start point through the same
adjoint-and-restart code path.)

## 6. Real output: adjoint solve

Immediately after primal convergence, DAFoam builds the dR/dW coloring and solves the adjoint linear system
by GMRES/PETSc for each function of interest. From `compute_totals_run1.log`:

```
Calculating dRdW Coloring... Completed! 6.2 s

[adjoint for CD]
Solving Linear Equation... 7.78 s
Main iteration 0   KSP Residual norm 3.216467351430e-02  7.85 s
Main iteration 100 KSP Residual norm 6.766359576193e-05  9.01 s
Main iteration 169 KSP Residual norm 2.564218245345e-08  9.93 s
**Completed**! Total iterations: 169. PetscConvergedReason: 2. 9.93 s
Residual tolerance satisfied, solution finished!

[adjoint for CL]
Solving Linear Equation... 10.27 s
Main iteration 0   KSP Residual norm 1.951477078991e-01  10.27 s
Main iteration 100 KSP Residual norm 5.320887035473e-04  11.44 s
Main iteration 170 KSP Residual norm 1.844916467933e-07  12.37 s
**Completed**! Total iterations: 170. PetscConvergedReason: 2. 12.37 s
Residual tolerance satisfied, solution finished!
```

Both adjoint solves converge (KSP residual drops from O(1e-1) to O(1e-7/1e-8) in under 170-170 GMRES
iterations, PetscConvergedReason: 2 = converged on relative tolerance).

## 7. Real output: printed total derivatives

`prob.compute_totals()` (OpenMDAO reverse-mode total derivative call, which under the hood runs one adjoint
solve per function and chains it through the mesh/FFD Jacobians) printed, verbatim (trimmed to the
aerodynamic-function entries; full dictionary including the 3 geometric-constraint derivatives is in
`compute_totals_run1.log`):

```
('scenario1.aero_post.functionals.CD', 'dvs.shape'):
  [[-0.01134164 -0.02217957  0.00679851  0.01238016  0.03893831  0.0423425  0.00569075  0.00346681]]

('scenario1.aero_post.functionals.CD', 'dvs.patchV'):
  [[0.00391915 0.00241048]]

('scenario1.aero_post.functionals.CL', 'dvs.shape'):
  [[ 1.03747273  1.40092572  1.21579267  1.21368721  3.15699781  2.82181951 -0.46239171  0.67142062]]

('scenario1.aero_post.functionals.CL', 'dvs.patchV'):
  [[0.10070389 0.0892332 ]]
```

`dvs.shape` is the vector of 8 FFD shape design variables; `dvs.patchV` is `[U0, angle-of-attack]`.
These are the real, printed dCD/dshape, dCD/d(U0,AoA), dCL/dshape, dCL/d(U0,AoA) adjoint-based total
derivatives for the converged 4032-cell case above.

## 8. Validation: adjoint vs. finite difference (`check_totals`)

Per the task instructions, ran `runScript.py -task check_totals`, which reruns the primal at each of the
10 design variables perturbed by a central-difference step (`step=1e-3`, `form="central"`,
`step_calc="abs"`) and compares against the adjoint (`Jan` = analytic/adjoint, `Jfd` = finite difference).
Verbatim summary blocks from `check_totals_run1.log` (MPI rank 0):

| Derivative | Analytic magnitude | FD magnitude | Absolute error (Jan-Jfd) | Relative error |
|---|---|---|---|---|
| dCD/d(patchV) | 4.601100e-03 | 4.612222e-03 | 1.115573e-05 | 2.418731e-03 (0.24%) |
| dCD/d(shape)  | 6.460292e-02 | 6.489568e-02 | 7.415780e-03 | 1.142723e-01 (11.4%) |
| dCL/d(patchV) | 1.345505e-01 | 1.342662e-01 | 2.865285e-04 | 2.134033e-03 (0.21%) |
| dCL/d(shape)  | 4.958230e+00 | 4.977997e+00 | 8.315584e-02 | 1.670468e-02 (1.67%) |
| geometry.thickcon/d(shape) | 4.006319e+01 | 4.006319e+01 | 5.068010e-12 | 1.265004e-13 |
| geometry.volcon/d(shape)   | 5.225577e+00 | 5.225577e+00 | 2.281799e-13 | 4.366597e-14 |
| geometry.rcon/d(shape)     | 3.784176e+01 | 3.784176e+01 | 5.159691e-09 | 1.363491e-10 |
| all three geometric constraints wrt patchV | 0.0 | 0.0 | 0.0 | 0.0 (exact, physically expected: geometry doesn't depend on flow speed/AoA) |

**Verdict:** The adjoint matches finite-difference to sub-percent accuracy for dCD/d(U0,AoA) (0.24%),
dCL/d(U0,AoA) (0.21%), and dCL/d(shape) (1.67%). The purely-geometric constraint derivatives
(thickness, volume, leading-edge-radius constraints w.r.t. shape, which do not depend on the CFD solve
at all, only on the FFD/geometry Jacobian) match to 1e-10 - 1e-13 relative error, i.e. essentially machine
precision, which is strong independent confirmation that the adjoint's geometric/mesh-sensitivity chain
rule is implemented correctly.

The one outlier by the aggregate-vector metric is dCD/d(shape) at 11.4% relative error. An initial read
of the raw components suggested this was a single near-zero-derivative artifact. Section 8.1 below
re-examines that claim per-component and with a step-size study, at the coordinator's request, because
dCD/dshape is the gradient that actually drives shape descent in this lab's optimization work, and the
initial characterization turned out to be incomplete (see 8.1 for the corrected picture: two of the eight
components, not one, show double-digit relative error, and the step-size study does not cleanly resolve
the question either way).

Both the primal (baseline + 20 perturbed re-solves for the central-difference check) converged cleanly:
21 occurrences of `Minimal residual ... satisfied the prescribed tolerance 1e-08` across the two log
files, zero solver failures, zero exceptions, zero tracebacks.

## 8.1 Follow-up: per-component breakdown and step-size study on dCD/dshape

This section was requested as a follow-up because the aggregate 11.4% figure in section 8 is the least
verified number in this proof, and dCD/dshape is the specific gradient that would drive shape descent in
an actual optimization. Everything below was computed in the same container (`dafoam/opt-packages:latest`)
and the same case (NACA0012 incompressible, 4032 cells) as the rest of this document, using a new script,
`work/NACA0012_Airfoil_Incompressible/stepStudy.py`, which builds the identical OpenMDAO/DAFoam problem as
`runScript.py` (same `daOptions`, `meshOptions`, `Top` class, flow conditions) so the adjoint value is the
same case, not a different one. Raw stdout is in `stepstudy_run1.log`.

As a reproducibility check, the baseline CD computed by `stepStudy.py` from a cold start
(`STEPSTUDY BASELINE_CD 2.091050986768742e-02`) is bit-identical (all 16 significant digits) to the CD
reported by the original `compute_totals` run in section 5, and the freshly recomputed adjoint
`dCD/dshape` vector (`STEPSTUDY ADJOINT` lines in `stepstudy_run1.log`) is identical to the vector printed
in section 7. Both confirm this is genuinely the same case, run twice, not a different setup.

### 8.1.1 Per-component table (adjoint vs. FD at step = 1e-3, the step used in section 8)

Values below are the same `check_totals_run1.log` numbers as section 8, broken out per component instead
of as a vector norm (all numbers copied directly from the log / recomputed by direct arithmetic on those
numbers, no rounding-in-a-favorable-direction):

| idx | adjoint (Jan) | FD, step=1e-3 (Jfd) | abs diff (Jan-Jfd) | rel diff (Jan-Jfd)/Jfd |
|---|---|---|---|---|
| 0 | -0.01134164 | -0.01013201 | -0.00120963 | 11.94% |
| 1 | -0.02217957 | -0.01986298 | -0.00231659 | 11.66% |
| 2 |  0.00679851 |  0.00726477 | -0.00046626 | -6.42% |
| 3 |  0.01238016 |  0.01290202 | -0.00052186 | -4.05% |
| 4 |  0.03893831 |  0.03998417 | -0.00104586 | -2.62% |
| 5 |  0.04234250 |  0.04339009 | -0.00104759 | -2.41% |
| 6 |  0.00569075 | -0.00105305 |  0.00674380 | -640.4% (opposite sign) |
| 7 |  0.00346681 |  0.00353164 | -0.00006483 | -1.84% |

**Correction to the earlier characterization in section 8:** this is NOT "7 of 8 components agree well,
1 outlier." Five components (2, 3, 4, 5, 7) agree to within 1.8% to 6.4%. Two components, idx0 and idx1,
independently show 11.7% to 11.9% relative error, not tiny. One component, idx6, shows the adjoint and FD
disagreeing in sign entirely (adjoint positive, FD negative). Squared-difference contribution to the
aggregate 11.4% figure: idx6 alone accounts for 82.7% of the squared-difference norm, idx1 for 9.8%, idx0
for 2.7%, and the rest for under 2% each, which is why the aggregate metric reads as "one outlier" even
though idx0 and idx1 are individually not small disagreements.

### 8.1.2 Step-size study on the three flagged components (idx 0, 1, 6)

Central-difference FD was recomputed at step sizes 1e-4, 1e-5, 1e-6, 1e-7, 1e-8 inside the same running
OpenMDAO problem (warm-started primal, same mesh decomposition throughout, so run-to-run differences are
real physical response, not decomposition noise). The 1e-3 row is the value already reported in 8.1.1,
included here for continuity. All numbers below are copied directly from `stepstudy_run1.log`:

**idx 0** (adjoint = -0.01134164):

| step | FD value | adjoint - FD | rel diff |
|---|---|---|---|
| 1e-3 | -0.01013201 | -0.00120963 | 11.9% |
| 1e-4 | -0.01006134 | -0.00128030 | 12.7% |
| 1e-5 | -0.00956262 | -0.00177902 | 18.6% |
| 1e-6 | -0.00826318 | -0.00307846 | 37.3% |
| 1e-7 | -0.00410851 | -0.00723313 | 176.1% |
| 1e-8 |  0.01369806 | -0.02503970 | -182.8% |

**idx 1** (adjoint = -0.02217957):

| step | FD value | adjoint - FD | rel diff |
|---|---|---|---|
| 1e-3 | -0.01986298 | -0.00231659 | 11.7% |
| 1e-4 | -0.01979303 | -0.00238654 | 12.1% |
| 1e-5 | -0.01916658 | -0.00301299 | 15.7% |
| 1e-6 | -0.01692726 | -0.00525231 | 31.0% |
| 1e-7 | -0.01158326 | -0.01059631 | 91.5% |
| 1e-8 | -0.01743682 | -0.00474276 | 27.2% |

**idx 6** (adjoint = 0.00569075):

| step | FD value | adjoint - FD | rel diff |
|---|---|---|---|
| 1e-3 | -0.00105305 |  0.00674380 | -640.4% |
| 1e-4 | -0.00111429 |  0.00680504 | -610.7% |
| 1e-5 | -0.00138584 |  0.00707659 | -510.6% |
| 1e-6 | -0.00180321 |  0.00749396 | -415.6% |
| 1e-7 | -0.00206019 |  0.00775094 | -376.2% |
| 1e-8 |  0.00023192 |  0.00545883 | 2353.7% |

**What this step-size study actually shows, stated plainly:** this is not the clean result the coordinator's
message hoped for. For idx0 and idx1, the FD value is close to constant between step=1e-3 and step=1e-4
(a real, reproducible plateau, not noise), but that plateau sits 12% away from the adjoint, not on it, and
as the step shrinks further (1e-5 through 1e-7) the FD value moves monotonically further from the adjoint,
before becoming visibly erratic only at 1e-8 (sign flip for idx0, a jump for idx1). For idx6, FD keeps the
same sign (negative) across every step from 1e-3 through 1e-7, four decades, opposite to the adjoint's
positive sign, and drifts further from the adjoint (not closer) as the step shrinks over that range; only
at 1e-8 does it swing toward a small positive value, in a way that looks like round-off noise rather than
convergence.

By the coordinator's own decision rule ("if FD converges cleanly to something the adjoint does not match,
the adjoint has a genuine problem"): FD does not converge cleanly to a stable value at all here, in either
direction. There is no step size in the tested range (1e-3 to 1e-8) at which the FD estimate both (a) has
stopped drifting with further step reduction and (b) is not yet dominated by round-off. That means this
experiment cannot be read as a clean vindication of the adjoint ("11.4% was a finite-difference artifact")
for idx0, idx1, and idx6. It equally cannot be read as clean proof the adjoint is wrong, because "clean
convergence to a different value" is exactly the one pattern that does NOT appear in the data; instead the
FD estimate keeps changing at every step tested, including between the two largest, least-noise-prone
steps (1e-3 and 1e-4), which is not the expected signature of a well-resolved finite difference. The
honest conclusion is that this particular finite-difference experiment, on this mesh (4032 cells) and at
this residual tolerance (1e-8), is inconclusive for these three components: it does not have the resolving
power to arbitrate between "adjoint is right and FD cannot get close enough on this mesh" and "adjoint has
a real error on these three modes." Settling it would require a finer mesh and/or a tighter
`primalMinResTol` (to push the CD noise floor down far enough to open a usable step-size window between
truncation error and round-off), which was not attempted tonight.

### 8.1.3 Magnitude of the flagged components relative to the largest gradient component

The largest-magnitude component of the adjoint dCD/dshape vector is idx5, at 0.04234250. Relative to that:

- idx6 (the sign-flip component): 0.00569075 / 0.04234250 = 13.4% of the largest component
- idx0: 0.01134164 / 0.04234250 = 26.8% of the largest component
- idx1: 0.02217957 / 0.04234250 = 52.4% of the largest component

idx6 is genuinely small relative to the dominant gradient direction (about one-seventh of the largest
component), so a sign error there has limited leverage on a descent step. idx0 is a bit over a quarter of
the largest component, not negligible. idx1 is over half the largest component's magnitude; it cannot be
dismissed on magnitude grounds alone, which is exactly why section 8.1.4's direction-based metric matters
more than an eyeball "it's probably small" argument.

### 8.1.4 Cosine similarity (the metric that actually matters for descent direction)

Using the full 8-component adjoint vector and the full 8-component FD vector at step=1e-3 (the same two
vectors compared in section 8, self-consistent at one step size):

- cosine(adjoint, FD), all 8 components: **0.993452** (angle 6.56 degrees)
- cosine(adjoint, FD), idx6 excluded: **0.998895** (angle 2.69 degrees)
- cosine(adjoint, FD), idx0, idx1, idx6 all excluded: **0.999983** (angle 0.33 degrees)

Per-component contribution to the dot product that drives the cosine: idx4 contributes 37.4% and idx5
contributes 44.1% of the total (these are the two best-agreeing, largest-magnitude components), idx1
contributes 10.6%, idx0 contributes 2.8%, idx3 contributes 3.8%, idx2 contributes 1.2%, idx7 contributes
0.3%, and idx6 contributes -0.14% (its sign disagreement pulls the dot product down very slightly, but its
magnitude is too small to matter).

**Reading this honestly:** the direction that actually matters for gradient-based shape descent is well
aligned (6.56 degrees off, tightening to 0.33 degrees once the three inconclusive components are excluded)
because the descent direction is dominated by idx4 and idx5, which independently check out to 2.4% to 2.6%
in section 8.1.1 and are not in question. idx1's 52%-of-max magnitude sounds concerning in isolation, but
it only pulls the overall cosine from 0.999983 down to 0.993452, a small effect, because idx1 is still not
large enough relative to idx4/idx5 combined to swing the direction much, and because its FD comparison
value (not the adjoint) is itself unresolved per 8.1.2.

### 8.1.5 Plain verdict

The adjoint shape gradient dCD/dshape is **not fully verified, and it is also not shown to be wrong.** Two
distinct things are true at once, stated in exactly these terms:

1. For 5 of 8 components (idx 2, 3, 4, 5, 7), the adjoint and finite-difference agree to within 1.8% to
   6.4%, which is a normal level of agreement for a CFD-based finite-difference check. For the direction
   that matters for optimization, the gradient is well aligned: cosine similarity 0.993452 (6.56 degrees)
   against the full FD vector, rising to 0.999983 (0.33 degrees) once the three disputed components are
   set aside. On a practical, "will this gradient point the optimizer downhill" basis, this case checks
   out.
2. For 3 of 8 components (idx 0, 1, 6), the step-size study requested to settle the 11.4% figure did NOT
   produce the clean result needed to call it a finite-difference artifact. FD does not converge to a
   stable value anywhere in the tested step range (1e-3 to 1e-8) for these three components; it drifts
   monotonically with decreasing step before becoming noise-dominated at the smallest steps, and for idx6
   it disagrees with the adjoint in sign across four decades of step size without ever trending toward
   agreement. This is inconclusive, not exculpatory. It genuinely could be either an adjoint error on these
   three shape modes or a finite-difference resolving-power limit set by this mesh's coarseness (4032
   cells) and the 1e-8 residual tolerance; the data in hand cannot distinguish the two. idx6 is small
   relative to the gradient's dominant direction (13.4% of the largest component) so it is unlikely to
   matter for descent by itself; idx0 (26.8%) and especially idx1 (52.4% of the largest component) are not
   small enough to dismiss on magnitude alone, and their disagreement is exactly the part this experiment
   left unresolved.

**Recommendation, not attempted tonight:** rerun `check_totals` and this step-size sweep on a refined mesh
(more cells, tighter `primalMinResTol`, e.g. 1e-10 to 1e-12) specifically for shape indices 0, 1, and 6.
That would lower the CD noise floor enough to open a step-size window where FD truncation error has
genuinely decayed but round-off has not yet taken over, which is the only way to get a step-size study that
actually discriminates between "adjoint is right" and "adjoint is wrong" for these three components. Until
that is done, treat dCD/dshape components 0, 1, and 6 as unverified, and the descent-direction-relevant
aggregate gradient (dominated by components 3, 4, 5) as verified.

**Superseded by section 8.2 below.** The recommendation above was carried out the same night, at
`primalMinResTol` tightened to 1e-12 (four orders of magnitude tighter than this section's 1e-8). Section
8.2 is the decisive result and changes the verdict: the disagreement on idx0, idx1, and idx6 is not a
finite-difference artifact. Read 8.2 as the current conclusion; this section is kept as-is (unedited) as an
honest record of what was known and reasoned before the decisive test was run.

## 8.2 Decisive test: tightened primal tolerance (1e-12) resolves the question

The coordinator proposed a specific, testable hypothesis: that the disagreement on idx0, idx1, and idx6 was
a finite-difference artifact caused by the primal's residual noise floor (noise/h growing as h shrinks),
not a real adjoint error, and that tightening `primalMinResTol` by three to four orders of magnitude would
either open a step-size window where FD stabilizes on the adjoint value (hypothesis confirmed) or reveal a
clean FD convergence to something the adjoint does not match (hypothesis rejected, adjoint has a real
error). This section runs that test. Script: `work/NACA0012_Airfoil_Incompressible/stepStudy2.py`. Raw
stdout: `stepstudy2_run1.log`. `system/controlDict` `endTime` was raised from 1000 to 3000 so the
tighter-tolerance primal would have room to converge instead of hitting the iteration cap; this was the
only other change from the section 8.1 setup, apart from `primalMinResTol: 1.0e-8` to `1.0e-12`.

### 8.2.1 Achieved residual

`primalMinResTol` was set to 1e-12. Every one of the 41 primal solves in this run (2 baseline + 3 x 6
step-size perturbations x 2 signs + 3 post-sweep baselines) printed `Minimal residual ... satisfied the
prescribed tolerance 1e-12`, with achieved residuals ranging from 9.158341493665211e-13 to
9.973382053815905e-13 across all 41 solves (grep of every `Minimal residual` line in `stepstudy2_run1.log`,
sorted). No solve stalled; `endTime = 3000` was never reached (the largest `Time =` value seen was in the
low hundreds, consistent with warm-started convergence). The tolerance was achieved cleanly on every run,
so this is a real four-orders-of-magnitude tightening, not a partial one.

Cross-check: the adjoint `dCD/dshape` recomputed at this tighter tolerance
(`STEPSTUDY2 ADJOINT idx=0 value=-1.134165042409772e-02`,
`STEPSTUDY2 ADJOINT idx=1 value=-2.217959324547508e-02`,
`STEPSTUDY2 ADJOINT idx=6 value=5.690780047244999e-03`) is unchanged from the section 8.1 adjoint
(-0.01134164, -0.02217957, 0.00569075) to 5-6 significant figures. The adjoint does not move when the
primal is converged four orders of magnitude tighter, which is exactly what should happen if the adjoint
is already well-converged; the object under test here is the finite difference, not the adjoint.

### 8.2.2 Noise floor, measured directly

Per the coordinator's request, the baseline (shape = 0) CD was recomputed 5 times, each reached by a
different path (cold start; a warm restart from the same point; and after returning from the idx0, idx1,
and idx6 sweeps respectively), all at `primalMinResTol = 1e-12`. Verbatim from `stepstudy2_run1.log`:

```
cold_start:      2.091050444203950e-02
warm_restart_1:  2.091050444208167e-02
after_idx0:      2.091050444359648e-02
after_idx1:      2.091050444376891e-02
after_idx6:      2.091050444257538e-02
```

Spread (max - min): **1.7294117526933661e-12**. Standard deviation: 7.371857235064325e-13. That is the
measured CD noise floor at this tolerance, about four orders of magnitude smaller than the noise floor
implied by the section 8.1 (1e-8-tolerance) runs. The smallest finite-difference step that is safely above
this noise floor (by roughly 2-3 orders of magnitude, a normal safety margin) is on the order of h = 1e-7
to 1e-8 for derivatives of magnitude 0.005 to 0.02, since the expected FD signal is 2h times the
derivative.

### 8.2.3 Redone step-size study, idx 0, 1, 6, at the tightened tolerance

All values below are copied directly from `stepstudy2_run1.log` (`STEPSTUDY2 FD` lines).

**idx 0** (adjoint = -0.01134165):

| h | FD value | adjoint - FD | rel diff | signal / noise-floor |
|---|---|---|---|---|
| 1e-3 | -0.01013818 | -0.00120347 | 11.9% | 1.3e7 |
| 1e-4 | -0.01013387 | -0.00120778 | 11.9% | 1.3e6 |
| 1e-5 | -0.01013396 | -0.00120769 | 11.9% | 1.3e5 |
| 1e-6 | -0.01013568 | -0.00120597 | 11.9% | 1.3e4 |
| 1e-7 | -0.01018317 | -0.00115848 | 11.4% | 1.3e3 |
| 1e-8 | -0.01081658 | -0.00052507 | 4.9% | 131 |

Plateau over h = 1e-4 to 1e-6: mean -0.01013450, spread across those 3 steps (3 orders of magnitude of h)
is 1.813e-06, i.e. 0.018% of the plateau value. This is a converged finite difference by any normal
standard; it is not moving as h shrinks, and it disagrees with the adjoint by 11.9%, not by a shrinking
amount.

**idx 1** (adjoint = -0.02217959):

| h | FD value | adjoint - FD | rel diff | signal / noise-floor |
|---|---|---|---|---|
| 1e-3 | -0.01987256 | -0.00230703 | 11.6% | 2.6e7 |
| 1e-4 | -0.01987592 | -0.00230368 | 11.6% | 2.6e6 |
| 1e-5 | -0.01987787 | -0.00230173 | 11.6% | 2.6e5 |
| 1e-6 | -0.01987957 | -0.00230002 | 11.6% | 2.6e4 |
| 1e-7 | -0.01987989 | -0.00229970 | 11.6% | 2.6e3 |
| 1e-8 | -0.02043331 | -0.00174628 | 8.5% | 257 |

This one is even cleaner: the FD value is stable at -0.0199 (11.6% relative error, unchanged to 3
significant figures) across FIVE consecutive decades of step size, 1e-3 through 1e-7, with signal-to-noise
ratio ranging from 2.6e7 down to 2.6e3 across that span. There is no ambiguity here about truncation error
still being present at 1e-3 and decaying: if that were happening, the value would visibly change between
1e-3 and 1e-7 (a span where truncation error, which scales as h^2, should collapse by a factor of
10,000). It does not change. This is a converged finite difference, and it disagrees with the adjoint.

**idx 6** (adjoint = +0.00569078, positive):

| h | FD value | adjoint - FD | rel diff | signal / noise-floor |
|---|---|---|---|---|
| 1e-3 | -0.00105107 | +0.00674185 | -641.4% | 6.6e6 |
| 1e-4 | -0.00106544 | +0.00675622 | -634.1% | 6.6e5 |
| 1e-5 | -0.00106563 | +0.00675641 | -634.0% | 6.6e4 |
| 1e-6 | -0.00106626 | +0.00675704 | -633.7% | 6.6e3 |
| 1e-7 | -0.00107282 | +0.00676360 | -630.5% | 658 |
| 1e-8 | -0.00128220 | +0.00697298 | -543.8% | 66 |

The finite difference for idx6 is **negative** at every single step size tested, from 1e-3 through 1e-8,
six decades, with a signal-to-noise ratio never worse than 66:1. The adjoint says positive. This sign
disagreement is not a noise artifact; it is a converged, repeatable measurement.

### 8.2.4 Does a genuine step-size window open, and is the adjoint inside it?

Yes, a genuine window opens, cleanly, for all three components: h = 1e-4 to 1e-6 (extending to 1e-7 for
idx1 and idx6) is a region where the FD value stops moving as h changes (varying by 0.018% to 0.08% across
3 to 5 orders of magnitude of step size) while sitting 2 to 4 orders of magnitude above the measured noise
floor. That is exactly the "plateau" the coordinator's message described as the deciding signature.

**The adjoint is outside that window for all three components, by the coordinator's own criterion.** Not
by a small margin that could be step-size sensitivity: idx0 and idx1 disagree by a stable 11.6-11.9%, and
idx6 disagrees in sign. Per the coordinator's stated decision rule: *"If it opens and the adjoint is
outside it, the adjoint has a real error on those components and I need to know that in those words."*

**Stated in those words: the adjoint has a real error on shape components idx0, idx1, and idx6 of
dCD/dshape. This is not a finite-difference artifact. The hypothesis that the primal's residual noise floor
was responsible is rejected by this test:** tightening `primalMinResTol` by four orders of magnitude (1e-8
to 1e-12) reduced the measured CD noise floor by roughly four orders of magnitude (to 1.7e-12) and made the
finite-difference plateau tighter and better resolved (0.018-0.08% spread across multiple decades of h,
versus visible drift at every step in section 8.1's 1e-8-tolerance run), but the converged FD value did not
move toward the adjoint. It stayed almost exactly where the section 8.1 measurements (at the much noisier
1e-8 tolerance) already placed it: idx0 was 11.94% off in section 8.1 and is 11.9% off here; idx1 was
11.66% off in section 8.1 and is 11.6% off here; idx6 was sign-flipped in section 8.1 and is still
sign-flipped here, at a noise floor four orders of magnitude smaller. If the section 8.1 disagreement had
been a noise-floor artifact, tightening the tolerance this much should have visibly closed the gap. It did
not.

### 8.2.5 idx6 sign flip: survives the tighter primal

Directly addressing the coordinator's point 4: yes, the sign flip survives. The finite difference for idx6
is negative at all six step sizes tested (1e-3 through 1e-8) at both the original 1e-8 primal tolerance
(section 8.1) and the tightened 1e-12 tolerance (this section), while the adjoint is positive at both
tolerances. A wrong sign on a design variable sends a gradient-based optimizer the wrong way on that
variable regardless of how well-aligned the rest of the gradient is; this is not something the good overall
cosine similarity can excuse, and it is not being treated as excused here.

### 8.2.6 A pattern worth flagging for the follow-up investigation

Not requested, but visible in the data and worth recording: the three disagreeing components are not
randomly distributed across the 8 shape modes. Given how `runScript.py` builds the shape design variables
(interior FFD stations first, in chordwise order, followed by the leading-edge and trailing-edge combo
modes last), idx0 and idx1 are the two shape functions at the interior station closest to the leading edge,
and idx6 is the leading-edge combo mode itself (idx7, the equivalent trailing-edge combo mode, agrees with
the adjoint to 1.8% and is not in question). The three components with a real, converged disagreement are
exactly the three located at or nearest the leading edge; the components at mid-chord and aft (idx2-5) and
at the trailing edge (idx7) all check out to within single-digit percent. This looks like a localized
adjoint sensitivity problem specific to the leading-edge region of the mesh or geometry parameterization
(for example, the volume-mesh-warping Jacobian the adjoint uses near the highest-curvature part of the
airfoil, or the stagnation-point pressure response, which is strongly nonlinear right at the leading edge),
rather than a global adjoint bug. This is a hypothesis for where to look next, not a diagnosis; it was not
traced into the DAFoam source code tonight.

### 8.2.7 Updated plain verdict

The dCD/dshape adjoint gradient from this DAFoam installation is **verified for 5 of 8 components (idx 2,
3, 4, 5, 7) and shown to be genuinely wrong for 3 of 8 components (idx 0, 1, 6),** specifically at and near
the leading edge of the airfoil. This was settled, not merely argued, by the coordinator's decisive test:
tightening the primal residual tolerance by four orders of magnitude (1e-8 to 1e-12), confirming the
tolerance was actually achieved (9.2e-13 to 1.0e-12 across 41 solves, no stalling), measuring the resulting
CD noise floor directly (1.7e-12), and showing that the finite difference converges to a stable plateau
(varying by 0.018-0.08% across 3 to 5 decades of step size, at signal-to-noise ratios from the thousands to
the tens of millions) that still disagrees with the adjoint by 11.6-11.9% on idx0/idx1 and disagrees in
sign on idx6. The earlier section 8.1 finding ("inconclusive") is superseded: it is now conclusive, and the
conclusion is not the one the noise-floor hypothesis predicted. The overall descent-direction cosine
similarity of 0.993452 reported in section 8.1.4 remains an accurate number, but per the coordinator's own
note, direction alignment does not substitute for a correct gradient: a wrong sign on idx6 will corrupt the
optimality conditions at convergence even though the aggregate direction looks good. **Do not use this
DAFoam installation's dCD/dshape adjoint for shape components 0, 1, or 6 (or, until traced, any shape mode
near the leading edge of an airfoil-like geometry) without independent verification. Components 2, 3, 4,
5, and 7, and the flow-variable derivatives dCD/d(U0,AoA) and dCL/d(U0,AoA), and dCL/dshape, remain
verified by the evidence in sections 5 through 8.1.**

## 9. Evidence files in this directory

- `pull.log`; raw `docker pull` output (tag, digest, layer download)
- `preproc_stdout.log`; mesh generation stdout
- `compute_totals_run1.log`; full primal + adjoint + `compute_totals` run (raw, unedited)
- `check_totals_run1.log`; full primal + adjoint + finite-difference `check_totals` run (raw, unedited)
- `stepstudy_run1.log`; full primal + adjoint + per-component step-size sweep run for section 8.1
  (raw, unedited), `primalMinResTol = 1e-8`
- `stepstudy2_run1.log`; full primal + adjoint + per-component step-size sweep run for section 8.2
  (raw, unedited), `primalMinResTol = 1e-12`, the decisive test
- `work/NACA0012_Airfoil_Incompressible/`; the actual case directory as run (mesh files, OpenFOAM
  case dictionaries, `logMeshGeneration.txt`, decomposed processor directories, `runScript.py`,
  `stepStudy.py`, and `stepStudy2.py` as used; `system/controlDict` has `endTime = 3000`, raised from
  the original 1000 for the section 8.2 run, see section 10)

## 10. What blocked / had to be worked around

- The image's default container user is `dafoamuser` (uid 1002) but the bind-mounted host directory
  is owned by `ubuntu` (uid 1000); running as `-u dafoamuser` against the host mount produced
  `Permission denied` on file writes, and running as `-u 1000:1000` then couldn't read `/home/dafoamuser`
  (owned 750 by uid 1002). Fix: run the container as its default root user (root can both read
  `dafoamuser`'s files and write the bind mount); this is a normal, non-fabricated workaround, not a
  DAFoam problem.
- The image itself does not ship a tutorials directory; the tutorial case had to be pulled from the
  separate `DAFoam/tutorials` GitHub repo and bind-mounted in. This matches DAFoam's documented usage
  pattern (image = toolchain, tutorials = separate repo).
- No other failures. `dafoam.pull`, mesh generation, primal solve, adjoint solve, `compute_totals`, and
  `check_totals` all completed with exit code 0 on the first attempt (after the user/permission fix above).
- For the section 8.2 decisive test at `primalMinResTol = 1e-12`, `system/controlDict` `endTime` was raised
  from 1000 to 3000 as a precaution, so the tighter tolerance would have enough outer SIMPLE iterations to
  actually be reached rather than stalling at the old iteration cap. In the event, no run needed anywhere
  close to 3000 iterations (all converged within the low hundreds via warm start, per `stepstudy2_run1.log`),
  so this was a safety margin, not a workaround for an actual stall.
## 11. Session 2026-07-27: root-cause investigation, mesh-refinement corroboration on ALL 8 components, and a formal retraction

This section documents a follow-up investigation into the root cause of the idx0/1/6 disagreement
identified in section 8.2. It (a) rules out one more alternative explanation, (b) extends the
mesh-refinement check from section 8.2's 3 flagged components to all 8, (c) identifies but cannot
empirically confirm one concrete candidate mechanism, and (d) formally retracts two auxiliary scripts
written this session as invalid evidence. Nothing in this section loosens any tolerance; the verdict
remains "unresolved" for 3 of 8 components, stated plainly in section 11.6.

### 11.1 Ruled out: FFD/DVGeo Jacobian and design-variable convention (already established, restated)

Unchanged from section 8: the purely-geometric constraints (`thickcon`, `volcon`, `rcon`), which use the
identical `nom_addShapeFunctionDV` shape definitions and DVGeo Jacobian as `dCD/dshape` -- including the
near-leading-edge geometry (`leList` at `x=1e-4`) -- match FD to 1e-10 to 1e-13 relative error. Since idx0,
idx1, and idx6 are only 3 of the 8 shape components sharing that exact same Jacobian, and the Jacobian
itself checks out to machine precision everywhere including at the LE, a point-ordering or sign-convention
bug in the shape-function/DVGeo layer is ruled out.

### 11.2 Ruled out: plain coarse-mesh spatial discretization error (new this session, decisive)

`checkAll8Refined.py` (in `work_refined/NACA0012_Airfoil_Incompressible_refined/`) recomputes the FULL
8-component adjoint AND a single-step (`h=1e-4`) central-difference FD for all 8 shape components on the
refined mesh (14720 cells, `primalMinResTol=1e-11`), extending the section 8.2 refined-mesh test (which
only recomputed FD for the 3 flagged components). Raw stdout: `checkall8refined_run2.log`. All 17 primal
solves in this run converged cleanly to the prescribed 1e-11 tolerance (verified by grepping `Minimal
residual` in the log). Full before/after table, adjoint (`Jan`) vs FD (`Jfd`), coarse mesh (4032 cells,
section 8) vs refined mesh (14720 cells, this run):

| idx | Jan (coarse) | Jfd (coarse) | rel err (coarse) | Jan (refined) | Jfd (refined) | rel err (refined) |
|---|---|---|---|---|---|---|
| 0 | -0.01134164 | -0.01013201 | 11.94% | -0.003303428 | -0.002758638 | **+19.75%** |
| 1 | -0.02217957 | -0.01986298 | 11.66% | +0.005406883 | +0.006326557 | **-14.54%** |
| 2 |  0.00679851 |  0.00726477 | -6.42% | +0.006395491 | +0.006727379 | -4.93% |
| 3 |  0.01238016 |  0.01290202 | -4.05% | +0.015740751 | +0.016071505 | -2.06% |
| 4 |  0.03893831 |  0.03998417 | -2.62% | +0.028411665 | +0.029145566 | -2.52% |
| 5 |  0.04234250 |  0.04339009 | -2.41% | +0.034428941 | +0.035152972 | -2.06% |
| 6 |  0.00569075 | -0.00105305 | sign-reversed | -0.001775589 | -0.005219931 | **-65.98%** |
| 7 |  0.00346681 |  0.00353164 | -1.84% | -0.000760338 | -0.000749015 | +1.51% |

**Reading this table honestly:** refining the mesh 3.65x (4032->14720 cells) and tightening
`primalMinResTol` a further 3 orders of magnitude (1e-8->1e-11) did NOT shrink the idx0/idx1 disagreement
(it grew, from 11.9%/11.7% to 19.8%/14.5%). idx6's sign-vs-FD disagreement resolves on the refined mesh
(both adjoint and FD are now negative) but the magnitude gap, now cleanly measurable instead of dominated
by a near-zero denominator, is a large 66%. **This rules out plain coarse-mesh spatial-discretization error
as the (sole) explanation**: a genuine truncation-error artifact should shrink under 3.65x refinement, not
hold steady or grow.

Also notable, and not previously reported: idx1's and idx7's ADJOINT values (not just their FD comparisons)
both change sign between the coarse and refined mesh. For idx1, FD changes sign too, in the same direction
as the adjoint (both meshes: adjoint and FD agree in sign with each other, ~11-15% gap persists) -- this is
a shared, mesh-dependent physical/numerical sensitivity at this design station, not new evidence against the
adjoint specifically. For idx7 the same holds: coarse mesh has adjoint +0.00347 / FD +0.00353 (agree,
1.84%); refined mesh has adjoint -0.000760 / FD -0.000749 (agree, 1.51%) -- both flipped sign together and
remain in tight agreement at both resolutions. **idx7, which one earlier side-experiment this session
(section 11.4 below) appeared to flag as suspect, is fully exonerated by this direct, same-quantity,
same-pipeline refined-mesh FD check: it remains one of the best-agreeing components (1.5-1.8% across two
mesh resolutions).**

Cosine similarity, refined mesh, all 8 components: **0.997437** (4.10 degrees), improving from the coarse
mesh's 0.993452 (6.56 degrees); excluding idx0/1/6: **0.999990** (0.25 degrees), tighter than the coarse
mesh's equivalent (0.999983, 0.33 degrees). The descent-direction alignment is good and gets slightly
better with refinement, consistent with idx2-5 and idx7 remaining well-resolved and dominant in magnitude
at both resolutions; it is not evidence that idx0/1/6 are correct.

**Updated verdict after mesh refinement: the same 5 of 8 components (idx 2, 3, 4, 5, 7) are independently
verified at two mesh resolutions (coarse and 3.65x refined) to relative errors of 1.5% to 6.4%. The same 3
of 8 components (idx 0, 1, 6) show a disagreement that survives (and for idx0/idx1 slightly worsens under)
mesh refinement. This is the most complete, most mesh-independence-checked characterization of the defect
produced so far.**

### 11.3 Candidate mechanism identified, not confirmed: frozen wall-distance omits a shape-sensitivity term

`daOptions["forceMeshWaveFrozen"]` defaults to `True` in this DAFoam installation (confirmed: it is active
in every run in this document; the printed option dictionary in `diagnose_run1.log` shows
`forceMeshWaveFrozen 1;`). Per the comment in `pyDAFoam.py` (`packages/miniconda3/.../dafoam/pyDAFoam.py`,
line ~435): *"force to use meshWaveFrozen in fvSchemes->wallDist->method, regardless of what is actually set
in fvSchemes. meshWaveFrozen improves the parallel adjoint accuracy."* This freezes the wall-distance field
at the baseline mesh and does not differentiate d(wallDistance)/d(shape) as the shape design variables
deform the mesh -- textbook description of "an incomplete mesh-deformation sensitivity term," one of the
candidates named for this investigation. It should matter most exactly where d(wallDistance)/d(shape) is
largest: the highest-curvature part of the airfoil, the leading edge -- exactly the region where idx0, idx1
(interior FFD stations nearest the LE) and idx6 (the LE combo mode itself) sit, and exactly the region idx2-5
(mid-chord/aft) and idx7 (TE combo) are not.

Attempted direct test: `diagnose_frozen.py`, identical to `stepStudy.py`/`runScript.py` except
`daOptions["forceMeshWaveFrozen"] = False` (the only change). Two attempts:

- **Parallel (`mpirun -np 4`, matching every trusted number in this document):** the primal SEGFAULTs
  (PETSc "Caught signal number 11 SEGV") in all 4 MPI ranks, immediately after completing only the very
  first SIMPLE iteration (`diagnose_frozen_run1.log`).
- **Serial (`python`, np=1, a quick sanity check only -- not directly comparable to the np=4 production
  numbers):** a clean, non-fabricated `FOAM FATAL ERROR: failed lookup of yWall (objectRegistry region0)`
  from the SpalartAllmaras turbulence model, meaning the real (non-frozen) `meshWave` patch-distance method
  requires a `yWall` field object that this case is not set up to provide (`diagnose_frozen_serial_run1.log`).

**Neither path produces a working before/after comparison.** This candidate mechanism is consistent with
every piece of localization evidence gathered (LE-adjacent components fail, mid-chord/aft/TE components do
not; the mechanism is specifically a mesh-deformation-sensitivity omission, one of the named candidates;
disabling it is fatal in a way that matches the developers' own comment that the frozen path exists
specifically to keep the *parallel* adjoint from misbehaving) but **it is not empirically confirmed**. It
remains the best-supported candidate by elimination, not a proven root cause.

### 11.4 Formal retraction: two auxiliary scripts from this session are not valid evidence

Two scripts written this session (`work/NACA0012_Airfoil_Incompressible/diagnose_warp.py` and
`diagnose_chain.py`/`diagnose_chain2.py`) produced numbers that looked alarming in isolation (large,
widespread AD-vs-FD disagreement in `diagnose_warp_exact_run1.log`'s `verifyWarpDeriv` self-check; 6-of-8
components including two sign reversals in `diagnose_chain2_run1.log`'s dot-product consistency check).
Both are formally retracted as evidence for this investigation, for concrete reasons, not merely a hunch:

- Both ran in **serial** (`python`, nProcs=1), unlike every trusted number anywhere else in this document,
  which all use `mpirun -np 4`. IDWarp's own default option comment says `meshWaveFrozen` "improves the
  **parallel** adjoint accuracy" -- a serial-only mesh-warping test is the wrong regime to trust for this
  question.
- `diagnose_chain2.py` measures `dot(w, dXv/dShape_idx)` for an **arbitrary fixed random seed `w`** on the
  raw volume-mesh coordinates, via `mesh.warpDeriv`/`DVGeo.totalSensitivityProd`, with **no CFD and no flow
  adjoint anywhere in it**. This is not `dCD/dShape`. Proof the two are not interchangeable: in the real,
  trusted `dCD/dShape` check (section 11.2's table), idx7 is one of the best-agreeing components (1.5-1.8%
  at both mesh resolutions) and idx4 is a middling ~2.5-2.6%; in `diagnose_chain2`, idx7 shows a sign
  reversal (~119% disagreement) and idx4 shows near-perfect agreement (~0.1%) -- the opposite ranking. That
  inversion is itself the evidence these auxiliary scripts have a methodology problem (most likely the
  serial/parallel mismatch above, compounded by unclear internal indexing semantics in IDWarp's compiled
  `verifyWarpDeriv` self-test, which this investigation could not independently audit from Python), not
  evidence of a 6-of-8 mesh-chain defect. **Section 11.2's full 8-component, same-pipeline, same-quantity,
  two-mesh-resolution check supersedes both of these scripts. Their numbers should not be read alongside
  the `dCD/dShape` figures anywhere in this document.**

### 11.5 Not pursued: OpenMDAO `check_partials` on the mesh-warper component

`diagnose_partials.py` attempted to use OpenMDAO's own `check_partials` scoped to
`scenario1.aero_pre.warper` (the `DAFoamWarper` component that calls `mesh.warpDeriv`/`mesh.warpMesh()`) as
a framework-native alternative to hand-rolled isolation scripts. It did not complete: it was killed by a
550s wrapper timeout (`diagnose_partials_run1.log`, exit 124), almost certainly because each finite-
difference perturbation re-triggers something markedly more expensive than an isolated mesh warp (possibly
a full group re-solve). Abandoned as too costly for the session's compute budget; it established nothing,
positive or negative.

### 11.6 Plain verdict (session 2026-07-27)

**Root cause: not conclusively identified. Ruled out with evidence: FD/residual-tolerance noise (section
8.2), FFD/DVGeo Jacobian or shape-DV sign/ordering convention (section 8, restated in 11.1), and plain
coarse-mesh spatial-discretization error (section 11.2, new -- the disagreement survives, and for idx0/idx1
slightly worsens, under 3.65x mesh refinement). Best remaining candidate: DAFoam's forced frozen
wall-distance field omitting d(wallDistance)/d(shape) from the adjoint's mesh-sensitivity chain, localized
exactly where that omission would be largest (the leading edge) -- but this could not be empirically
confirmed because disabling it crashes this DAFoam v5.0.0 installation both in parallel (SEGV) and serial
(missing `yWall` field), in different ways, on the very first primal iteration. Two auxiliary scripts from
this session are formally retracted as unreliable (serial-vs-parallel mismatch; wrong quantity measured).

**dCD/dshape components 2, 3, 4, 5, and 7 are verified at two independent mesh resolutions (1.5% to 6.4%
relative error). Components 0, 1, and 6 remain genuinely wrong, confirmed not to be a finite-difference or
coarse-mesh-discretization artifact by direct evidence at two mesh resolutions, with a plausible but
unconfirmed mechanism. Per the standing instruction to state "unresolved" rather than loosen any tolerance:
this is unresolved for 3 of 8 components.** Do not use this DAFoam installation's dCD/dshape for shape
components 0, 1, or 6 (or, more conservatively, any shape mode at or adjacent to an airfoil leading edge)
without independent verification.

**Phase 2 gating:** the task's own instruction is to attempt the inventory-case gradient check "only after
Phase 1 resolves." Phase 1 has not resolved (3 of 8 components remain genuinely disagreeing, per the
verdict above). Per that explicit gating condition, Phase 2 was not attempted this session.

### 11.7 Evidence files added this session

- `diagnose_run1.log`, `diagnose_warp_run1.log`, `diagnose_warp_exact_run1.log` -- retracted (11.4);
  serial-only IDWarp `verifyWarpDeriv` self-checks
- `diagnose_chain_run1.log`, `diagnose_chain2_run1.log` -- retracted (11.4); serial, wrong-quantity
  mesh-chain dot-product checks
- `diagnose_partials_run1.log` -- abandoned (11.5); timed out, established nothing
- `diagnose_frozen_run1.log` (parallel, SEGV), `diagnose_frozen_serial_run1.log` (serial, `yWall` fatal
  error) -- the `forceMeshWaveFrozen=False` test (11.3); both failed, no working comparison obtained
- `checkall8refined_run1.log` -- first attempt, failed (`renameSolution` collision with stale
  `processorN/<time>` directories left over from `stepStudyRefined.py`'s earlier perturbed solves, owned by
  root; cleaned with `sudo rm -rf`)
- `checkall8refined_run2.log` -- the decisive full-8-component refined-mesh run reported in 11.2, clean
  exit, all 17 primal solves converged to 1e-11
- `work/NACA0012_Airfoil_Incompressible/diagnose.py`, `diagnose_warp.py`, `diagnose_warp_exact.py`,
  `diagnose_chain.py`, `diagnose_chain2.py`, `diagnose_partials.py`, `diagnose_frozen.py` -- scripts as run
- `work_refined/NACA0012_Airfoil_Incompressible_refined/checkAll8Refined.py` -- script as run

## 12. Session 2026-07-27 (continued): the frozen wall-distance candidate, tested to a decisive result

This session picked up section 11.3's identified-but-unconfirmed candidate exactly where it was left off
("do not repeat" instructions followed: no diagnose_warp*/diagnose_chain* work redone). Two things were
attempted, per the task's own two prescribed routes. Route 1 (make `forceMeshWaveFrozen=False` actually run)
is now understood, not just retried. Route 2 (quantify the omitted term directly) was carried out to
completion and gives a decisive, if unexpected, answer. Bottom line stated up front: **the frozen
wall-distance mechanism is CONFIRMED to exist exactly as hypothesized, but is REFUTED as the explanation for
the idx0/idx1/idx6 FD-vs-adjoint disagreement.** No number anywhere in this section is fabricated or
tolerance-loosened; every figure below is read directly from a log file named in 12.5.

### 12.1 Route 1, revisited: why `forceMeshWaveFrozen=False` crashes, precisely (source-level, container-verified)

Inside the `dafoam/opt-packages:latest` container, `grep -rn yWall src/adjoint/` locates every place the
field is read or written:

- `src/adjoint/DAModel/DATurbulenceModel/DASpalartAllmaras.C:94`, `DASpalartAllmarasFv3.C:104`,
  `DAkOmegaSST.C:125`, `DAkOmegaSSTLM.C:177` all do
  `y_(mesh.thisDb().lookupObject<volScalarField>("yWall"))` -- every DAFoam turbulence model that needs a
  wall distance looks up an object literally named `"yWall"` in the registry.
- The **only** code that ever registers an object under that literal name is
  `src/adjoint/DAMisc/meshWaveFrozen/meshWaveFrozenPatchDistMethod.C`, whose constructors build
  `y_(IOobject("yWall", ...), ...)`. Stock OpenFOAM's own `meshWave` patchDistMethod (what `fvSchemes`
  falls back to when `forceMeshWaveFrozen` is `False`) registers its result under the standard `wallDist`
  machinery's own name, not `"yWall"` -- so the moment the frozen class is bypassed, the lookup above has
  nothing to find. This is exactly why the serial test in section 11.3 produced a clean
  `failed lookup of yWall` fatal error immediately after `Selecting patchDistMethod meshWave` printed: the
  case correctly switched methods, and the switch itself is what breaks the lookup.
- The header comment in `meshWaveFrozenPatchDistMethod.H` (not previously quoted in this document) states
  the mechanism and the reason for it in the developers' own words: *"Basically, we compute the wall
  distance only once and save it to y_. When the mesh is deformed during optimization, we will NOT update
  y_. The reason we do this is that the meshWave function is not AD in parallel so it will impact the
  adjoint derivative. Also, not updating the wall distance during optimization has little impact on CFD."*
  This directly explains both section 11.3 crashes: parallel SEGVs because plain `meshWave` genuinely "is
  not AD in parallel" (the developers' own words, not a guess this session made), and serial fails on the
  `yWall` lookup because the non-frozen class never registers under that name. **Route 1 is now explained,
  not merely blocked** -- disabling `forceMeshWaveFrozen` cannot produce a working, trustworthy comparison in
  this installation, by the maintainers' own design, and no source patch was attempted to force it (patching
  a not-parallel-AD-safe algorithm back into the parallel adjoint path would reproduce exactly the failure
  mode the developers describe, for no evidential gain -- see 12.4).

### 12.2 Route 2: measuring d(yWall)/d(shape) directly, via DAFoam's own field-query API

Rather than editing/rebuilding DAFoam (Route 1) or relying on a geometric proxy, this session used the
solver's own exposed API, `pyDASolvers.getOFField(fieldName, "scalar", array)`
(`src/pyDASolvers/pyDASolvers.pyx`, wrapping `DASolver::getOFField` in `DASolver.C:1253`, which does
`meshPtr_->thisDb().lookupObject<volScalarField>(fieldName)` -- the identical registry lookup the
turbulence models use), reachable in Python as
`prob.model.scenario1.aero_post.functionals.DASolver.solver.getOFField("yWall", "scalar", arr)`. This reads
the live, currently-registered field with no file I/O and no proxy approximation.

A new case copy, `work_refined/NACA0012_Airfoil_Incompressible_probe/` (identical `constant/` (14720-cell
refined mesh), `system/`, `FFD/`, `0.orig/` to the section 11.2 case; no source files touched), and a new
script `probeFreshY.py` were used to run **9 independent, brand-new processes** (`mpirun -np 4`, capped to 3
host CPU cores via `docker run --cpus=3`), each doing exactly one `prob.set_val("dvs.shape", ...)` followed
by exactly one `prob.run_model()` -- baseline, idx0 at h=+-1e-4 (the section 11.2 FD step), idx1 at h=+-1e-4,
idx6 at h=+-1e-4, idx4 (control, a well-agreeing component) at h=+-1e-4, and idx0 at a much larger,
unambiguously shape-changing step of 0.05. After each run, `yWall` was read via `getOFField` and reduced
(MPI min/max/sum) to a global min/max/mean over all 14720 cells.

**Result: in all 9 runs, global `yWall` min/max/mean were bit-identical to 10 printed significant figures:
`min=5.2095665138e-04`, `max=1.8292100778e+01`, `mean=2.6516752604e+00`.** This includes the 0.05-step run,
which is a clearly real, large geometry change: its CD (`0.01810495098120565`) differs from baseline
(`0.01814605531303470`) by 0.23%, a solidly converged, physically meaningful difference (residual norm2
`4.75e-06` at `primalMinResTol=1e-11`, same as every other run in this document).

**Cross-validation that this is not a stale/cached `getOFField` bug:** the same two runs (baseline and the
0.05-step run) also queried the pressure field `p` via the identical API. `p` changed substantially and
sensibly between the two runs (`p_mean`: `-2.4020459735` to `-2.1394578907`; `p_min`: `-89.12` to `-81.82`;
`p_max`: `50.17` to `49.90`), proving `getOFField` faithfully returns live, run-specific solver state. In the
very same two runs, `yWall` did not move by even the smallest printed digit. This rules out a Python/API
artifact and leaves only one explanation: **`yWall` genuinely never responds to shape, at any perturbation
size tested (1e-4 to 0.05, a 500x range), in any process (fresh or reused).**

### 12.3 Fresh-process FD reproduces the established (persistent-process) FD, ruling out a process-lifetime confound

Before drawing conclusions from 12.2, this session checked whether "fresh, single-shot process" FD differs
at all from section 11.2's persistent-process (`prob.check_totals`-style, one process reused for baseline +
all 16 perturbations) FD, since a difference would itself be informative. Central differences from the 12.2
probe runs (h=1e-4):

| idx | Jfd (this session, fresh single-shot process) | Jfd (section 11.2, persistent process, established) | Jan (section 11.2, adjoint, established) |
|---|---|---|---|
| 0 | -0.0027593046 | -0.002758638 | -0.003303428 |
| 1 | +0.0063258933 | +0.006326557 | +0.005406883 |
| 6 | -0.0052204825 | -0.005219931 | -0.001775589 |
| 4 (control) | +0.0291452744 | +0.029145566 | +0.028411665 |

Fresh-process FD matches established persistent-process FD to 0.001%-0.02% at all four components (well
within normal step-size/solver noise) -- **not** to the adjoint. This is expected given 12.2's finding: since
`yWall` is frozen at the pristine, undeformed mesh at construction time regardless of whether the process is
fresh or long-lived, there is no "fresh vs. reused" distinction for this particular field, and no reason for
the two FD methodologies to disagree. This also incidentally re-validates the new probe case/script against
the established numbers (same mesh, same tolerance, same baseline CD to 10 significant figures: `1.81460553e-02` both ways).

### 12.4 Verdict: mechanism confirmed to exist; refuted as the explanation for the FD-vs-adjoint gap

Section 11.3 posed the hypothesis as: the adjoint omits d(yWall)/d(shape), while FD (which just re-solves
the primal at perturbed shapes) presumably captures it, and the difference is the gap. Section 12.2-12.3
show this framing is not correct for this installation: **d(yWall)/d(shape) is measured at exactly zero not
only in the adjoint (by design) but in every finite-difference computation this installation can produce**,
because `yWall` is computed once, unconditionally, at case/solver construction time (before any design
variable is ever set), in both the persistent-process FD loop used throughout this document and in
brand-new, single-shot processes alike. FD and the adjoint are, provably, differentiating the *exact same*
frozen-`yWall` discrete function throughout this entire investigation -- there is no accessible regime in
this DAFoam v5.0.0 installation in which FD reflects a "complete" wall-distance-shape coupling that the
adjoint is missing. Consequently:

- **Confirmed** (source-level, in the developers' own comment, and now empirically, via direct field query
  across 9 independent runs spanning 1e-4 to 0.05-sized perturbations at idx0, idx1, idx4, idx6): DAFoam's
  `forceMeshWaveFrozen` freezes `yWall` at the pristine, undeformed mesh, unconditionally, for the entire
  life of a process, and this is why `forceMeshWaveFrozen=False` cannot be made to run in this installation
  (12.1).
- **Refuted**: this omission is the explanation for the idx0/idx1/idx6 FD-vs-adjoint disagreement reported
  in sections 8.2 and 11.2. The omitted term's measured contribution to the FD estimate of dCD/dShape is
  exactly zero at every one of idx0, idx1, idx6 (and the idx4 control) -- it cannot be "the right size and
  sign to close the gaps," because the two quantities being compared (Jan and Jfd) already, identically,
  both exclude it. No fix was applied, because there is nothing here to fix that would change either
  measured number: unfreezing `yWall` (even if Route 1's crashes could be worked around) would change the
  *adjoint's* Jacobian, and section 12.2-12.3 show it would leave the *FD* baseline this document has always
  compared against completely unchanged (FD does not see a frozen-vs-unfrozen distinction either way, since
  it never observes an unfrozen `yWall` in the first place). Per the standing hard rule, this refutation is
  reported plainly rather than dressed up or reframed as a partial confirmation.

**What remains:** the root cause of the idx0/idx1/idx6 disagreement (11.94%-19.75%, 11.66%-14.54%, and a
sign-reversal-to-65.98% respectively, per the section 11.2 two-mesh-resolution table) is still not
identified. The frozen-wall-distance mechanism is a real, confirmed, source-verified design choice in this
DAFoam installation, and a legitimate reason `forceMeshWaveFrozen=False` cannot be tested directly here --
but it is not the mechanism behind the specific defect this investigation was chartered to explain. The
leading-edge localization noted in 11.3 (idx0/idx1 nearest the LE, idx6 the LE mode itself) remains an
unexplained coincidence, not a mechanism, now that its best-supported candidate has been directly measured
and found not to apply. Do not use this DAFoam installation's dCD/dshape for shape components 0, 1, or 6
without independent verification; the cause of their disagreement with finite differences is open.

### 12.5 Evidence files added this session

- `probe_baseline_run1.log` -- baseline sanity probe (`idx=-1`), confirms `CD0` matches section 11.2's
  `1.814605531269509e-02` to 10 significant figures
- `probe_idx0_1eneg4_run1.log`, `probe_idx0_neg1e-4_run1.log`, `probe_idx1_1e-4_run1.log`,
  `probe_idx1_neg1e-4_run1.log`, `probe_idx6_1e-4_run1.log`, `probe_idx6_neg1e-4_run1.log`,
  `probe_idx4_1e-4_run1.log`, `probe_idx4_neg1e-4_run1.log` -- the 8 h=+-1e-4 fresh-process probes behind the
  12.3 table
- `probe_idx0_LARGE_run1.log`, `probe_baseline_pcheck_run1.log`, `probe_idx0_LARGE_pcheck_run1.log` -- the
  large-perturbation (0.05) and `p`-field cross-validation runs behind 12.2's decisive result
- `run_all_probes.log`, `pcheck_wrapper.log` -- wrapper-script stdout for the batched probe runs
- `work_refined/NACA0012_Airfoil_Incompressible_probe/` -- new case copy (mesh/FFD/system/0.orig identical to
  the section 11.2 refined case), `probeFreshY.py` (the fresh-process CD+field probe script),
  `run_all_probes.sh` (batch driver)

## 13. Session 2026-07-29: wall-function branch-crossing hypothesis, tested and killed

A new, previously-untested mechanism was proposed for the idx0/idx1/idx6 defect: that DAFoam's SA
wall treatment contains a discrete (non-differentiable) branch on near-wall cell state, and that if a
leading-edge wall face crosses that branch between the plus and minus evaluations of a central
difference, the FD estimate is measuring the secant slope across a kink rather than a derivative --
which would make the FD **check** wrong and the **adjoint** right, the opposite of every prior
session's working assumption. This section tests that hypothesis directly, on this case's real
source code and real converged fields, budget-capped at 3 cores / 3 GB (`--cpus=3 --memory=3g`),
serial (`np=1`, deliberately -- see 13.2), never exceeding budget.

### 13.1 Locating the actual discrete branch (source-level)

This case's `0.orig/nut` uses `nutUSpaldingWallFunction` on the `wing` patch -- Spalding's law, a
single smooth formula valid across all y+ regimes, specifically chosen in the OpenFOAM/DAFoam
ecosystem to avoid the classic hard y+-regime switch that plain `nutkWallFunction`/`nutUWallFunction`
have. DAFoam does not use the stock OpenFOAM class for this BC; it overrides it at the same runtime-
selection name with its own differentiated version,
`src/adjoint/DAMisc/nutUSpaldingWallFunctionDF/nutUSpaldingWallFunctionFvPatchScalarFieldDF.C`
(confirmed by reading it directly out of the `dafoam/opt-packages:latest` container). Reading
`calcNut()` and `calcUTau()` line by line, there is exactly one genuine hard branch in the whole
class:

```cpp
tmp<scalarField> tnutw(
    max(scalar(0), sqr(calcUTau(magGradU)) / (magGradU + ROOTVSMALL) - nuw));
```

i.e. the wall-face turbulent viscosity `nutw` is clipped to exactly `0` whenever the raw Newton-
converged value would be negative -- a genuine kink at `nutw == 0`. (Two other candidate branches
were read and ruled out as inactive for this case: `if (tolerance_ != 1.e-14)` is never taken because
`daOptions` never overrides the wall-function tolerance, so `tolerance_` stays at its `1.e-14`
default; and `if (ROOTVSMALL < ut)` guards only against a literal near-machine-zero initial Newton
seed, not a physical regime.)

### 13.2 Measurement: does any wing-patch face cross the `nutw == 0` clip?

`getOFField` (the only field-query API DAFoam exposes to Python) only returns a `volScalarField`'s
**internal** field -- a wall function's face value lives in the `boundaryField`, which is not
reachable through that API. So this session read it the direct way: off disk, from the field file
OpenFOAM itself writes at convergence. `DASolver::solve()` calls `runTime.writeNow()`
(`DASolver.C:205`) the moment `primalMaxRes < primalMinResTol`, regardless of `writeInterval` -- so
every converged run leaves the wing patch's exact 126-face `nutw` array sitting in
`<time>/nut(.gz)`'s `boundaryField` block. Run serial (`np=1`, capped `--cpus=3 --memory=3g`)
specifically so that block lands in one plain file at `<caseDir>/<time>/nut`, with no processorN
merging needed and the full 126-face patch visible in one place after a single `run_model()` call.
Script: `work/NACA0012_Airfoil_Incompressible/probeWallBranch.py` (new this session). Five fresh,
independent, single-shot processes were run: baseline (`shape=0`), idx6 at `+1e-4`/`-1e-4` (the
defective LE combo mode), idx4 at `+1e-4`/`-1e-4` (control -- a well-agreeing, large-magnitude
component, 2.6-3.0% FD error in every prior session). `h=1e-4` is the step already established
(section 8.2, `A_stepsize_study.json`) to sit inside the well-converged, step-independent FD plateau
for this exact case, so this is not a step-size artifact of the measurement itself.

**Sanity cross-check (methodology validity, before trusting the result):** baseline CD from this
serial probe, `2.091051001294601e-02`, matches the trusted np=4 production baseline
(`2.091050986768742e-02`) to 8 significant figures. Central-difference `(CD+ - CD-)/(2h)` computed
directly from this session's own 5 CD values gives idx6 = **-1.0661e-3** (established fresh-process
value at this same step, section 8.2.3: -1.06544e-3 -- matches to 4 sig figs, sign negative, same as
every trusted number in this document) and idx4 = **+3.9993e-2** (adjoint = +0.038938, ~2.6% off, the
same healthy-agreement band established in every prior session). This confirms the probe reproduces
the case's own established, trusted behavior in both directions (the broken one and the healthy one)
before drawing any conclusion from the new measurement.

**Result, read directly from the parsed `nut` boundaryField blocks (raw values and zero/near-zero
counts in `probewallbranch_*_run1.log`, `PROBE`/`PROBE_VALUES`/`PROBE_ZEROMASK` lines):**

| config | nZero (== 0.0 exactly) | global min nutw | at true LE stagnation face (idx 63) |
|---|---|---|---|
| baseline | 0 / 126 | 5.935e-06 | 5.9350e-06 |
| idx6, h=+1e-4 | 0 / 126 | 5.940e-06 | 5.9402e-06 |
| idx6, h=-1e-4 | 0 / 126 | 5.930e-06 | 5.9298e-06 |
| idx4, h=+1e-4 | 0 / 126 | 5.933e-06 | 5.9335e-06 |
| idx4, h=-1e-4 | 0 / 126 | 5.937e-06 | 5.9365e-06 |

**Zero wing-patch faces are clipped (`nutw == 0`) at baseline, at either sign of idx6's perturbation,
or at either sign of idx4's perturbation. Crossing count: idx6 = 0, idx4 (control) = 0.** The global
minimum `nutw` anywhere on the patch, at every one of the 5 configurations, sits at the physical
leading-edge stagnation face (patch index 63) at a stable ~5.93-5.94e-06 -- roughly 400x above the
`max(0, ...)` clip floor, not near it. Under the h=1e-4 perturbation, that face's value moves by
+0.18%/-0.11% for idx6 and by -0.05%/-0.08% for idx4 (full 8-face near-LE table in the raw logs) --
small, smooth, and not meaningfully more erratic for the broken component (idx6) than for the healthy
control (idx4). No face anywhere on the patch, at any configuration tested, is within an order of
magnitude of the branch.

### 13.3 Verdict: the branch-crossing hypothesis is dead, cleanly

**The coordinator's stated prediction ("idx6 crosses, idx4 does not") did not hold. Neither crosses.
Both counts are exactly zero.** This is not "inconclusive" or "small effect below detection" --
the measured nutw values sit ~400x away from the clip floor and move by well under a fifth of a
percent between the plus and minus evaluations, at the exact face (the LE stagnation point, patch
index 63) where the wall function's own physics makes this branch most likely to be approached. The
one genuine hard branch that exists in DAFoam's actual, differentiated, container-verified wall-
function source code for this case's actual boundary condition (`nutUSpaldingWallFunctionFvPatchScalarFieldDF`,
Spalding's law, deliberately branch-free-by-formula across y+ regimes save this one clip) is never
engaged anywhere on the wing patch, for either the defective component or the healthy control, at
this case's own already-established well-converged FD step size. **Per the standing hard rule, this
refutation is reported plainly: the SA wall-function switching-threshold hypothesis, as specifically
and testably framed (a discrete branch on near-wall cell state that the plus/minus FD evaluations
straddle), is refuted for A1 by direct measurement, not merely unconfirmed.**

This adds a fourth ruled-out mechanism to the three already eliminated (FD/residual-tolerance noise,
section 8.2; FFD/DVGeo Jacobian or shape-DV convention, section 8/11.1; plain coarse-mesh spatial-
discretization error, section 11.2) and supersedes the frozen-wall-distance mechanism already
separately refuted in section 12. **Root cause of the idx0/idx1/idx6 defect remains unidentified.**
Two concrete, not-yet-tested candidates remain, both flagged by the coordinator going into this
session and untouched by it: (1) idx6 is the LE **combo** mode (the only shape function whose FFD
control points move the LE point and its mirror in *opposite* directions simultaneously to hold the
LE fixed, per `runScript.py`'s `configure()`), unlike every one of idx0-idx5 which are single
interior stations -- nobody has yet checked whether that combined perturbation produces a smooth
volume-mesh deformation at the LE the same way a single-station perturbation does; (2) negative or
near-degenerate cell volumes appearing transiently at the leading edge under either sign of
perturbation, not yet checked via `checkMesh`/`DACheckMesh` output on the perturbed (not just
baseline) meshes.

### 13.4 Preflight check added

Per the task's own instruction ("a wall-function case cannot be gradient-verified by finite
difference at the wall without first checking for branch crossings" -- which this session's own
result does NOT bear out for this specific mechanism, but the check is generically cheap and worth
having on file for future cases that DO use a hard-switch wall function like `nutkWallFunction`), a
`--check-wall-branch` note was considered for `scripts/case_preflight.sh` and NOT added: preflight
runs before a solve, with no converged fields to inspect, so a real branch-crossing check can only
run post-hoc (as `probeWallBranch.py` does here, off two already-converged perturbed solves) --
bolting a no-op flag onto preflight for a check it structurally cannot perform would be misleading,
not useful. `probeWallBranch.py` is kept in the case directory as the reusable, ready-to-run
diagnostic for any future case using a hard-switching wall function.

### 13.5 Evidence files added this session

- `work/NACA0012_Airfoil_Incompressible/probeWallBranch.py` -- the fresh-process, off-disk
  `nut` boundaryField probe script (new this session)
- `probewallbranch_baseline_run1.log`, `probewallbranch_idx6_plus_run1.log`,
  `probewallbranch_idx6_minus_run1.log`, `probewallbranch_idx4_plus_run1.log`,
  `probewallbranch_idx4_minus_run1.log` -- the 5 raw runs behind this section's table, each
  containing the full 126-value `nut` wing-patch array (`PROBE_VALUES`) and per-face zero mask
  (`PROBE_ZEROMASK`)

