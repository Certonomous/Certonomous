# VMFL029 — Anisotropic Conduction Heat Transfer — PRE-REGISTRATION **DRAFT**

> ## THIS IS NOT THE FREEZE COMMIT. THIS DOCUMENT IS NOT FROZEN AND IS NOT FREEZABLE AS IT STANDS.
>
> **Status:** `DRAFT — FEASIBILITY COMPLETE, REGISTRATION NOT RECOMMENDED IN THIS FORM.`
> **Nothing here has graded anything.** No run in `verification/runs/ansys_verification/`
> exists for VMFL029; no register row exists; no queue entry exists.
> **A freeze of this document would breach `ANSYS_VERIFICATION_CHARTER` §11.2**, and §0.6
> below states the two independent reasons why.
>
> Lane: `ansys-lane-opus` (Opus 5). Drafted 2026-08-31. Supervisor: `ansys-verification-supervisor`.
> Manual: `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
> VMFL029, p. 109–110.

---

## 0. THE HEADLINE, BEFORE ANYTHING ELSE

### 0.1 The finding

**VMFL029's conductivity tensor is a four-digit truncation of an exactly rank-one
(singular) matrix.** The archive (`VMFL029_aniso.cas:2628`, recovered by the sister lane)
stores

```
K_arch = [ 0.25   -0.433   0 ]
         [-0.433   0.75    0 ]   W/(m K)
         [ 0       0       1 ]
```

Its 2-D block has eigenvalues **1.10001210e-05** and **9.99989e-01** — condition number
**9.0907e+04**, determinant **1.100e-05**. Replace `0.433` by its intended value
`sqrt(3)/4 = 0.4330127...` and the matrix becomes **exactly** `v vᵀ` with
`v = (1/2, −sqrt(3)/2)`: conductivity 1 along −60°, **exactly zero** along 30°.
Verified in `vmfl029_exact.py` (`selftest`, check `K_rank1 == v vᵀ`, PASS at 1e-15).

So the case's intended physics is a **perfect directional insulator**, and the equation
the manual is really about, `div(K_rank1 grad T) = 0`, is **not elliptic** — it is
`∂²T/∂s² = 0`, an ODE along the chords in direction `v`.

### 0.2 What that does to a grid-convergence ladder — MEASURED, not argued

With the truncated tensor the problem *is* elliptic, but the transformed aspect ratio is
`sqrt(λ_hi/λ_lo) = 301.5`, so structure in the solution lives on a length scale of
**3.3167e-03 m in a 1 m domain**. Ten cells across that feature needs **≈3015 cells per
side (9.09e+06 cells in 2-D)**; a x4-per-level triple sitting on it needs up to
**1.46e+08 cells**.

Two independent instruments say the affordable ladder is nowhere near asymptotic:

| instrument | levels | observed order `p_obs` of `T` at `x = 0.5` |
|---|---|---|
| 9-point conservative FD (Python) | 160/320/640 | **0.62** (L∞), 0.83 (L2) |
| 9-point conservative FD (Python) | 320/640/1280 | **0.69** (L∞), 1.13 (L2) |
| cell-centred FV (Python, OpenFOAM's split) | 40/80/160 | **0.93** (L∞) |

The formal order of both schemes is 2. At `N = 1280` (`h = 7.8e-04`, ~4 cells across the
feature) the observed order is still **0.69**, and pointwise Cauchy orders along the
profile are **erratic and repeatedly negative** (measured: `p = −1.31` at `y = 0.200`,
`p = −0.95` at `y = 0.800`, `p = +5.24` at `y = 0.500`). **A Roache triple built on this
would return `OSCILLATORY`, hence `NOT A RESULT` under `CLAUDE.md` rule 5 step 2** —
which is precisely the VMFL038 R1 failure this team already paid for.

### 0.3 The §12.2 classification, and it is the one that decides the ceiling

Stated in full at §3. In one line: **the only closed-form reference this case admits is
the exact solution of the RANK-ONE equation, and the solver can only discretise the
TRUNCATED SPD one. Those are different continuum models** — one elliptic, one not — and
their solutions differ by up to **2.07e-01 K** on the gate profile (measured, §7.3).
Under `VERIFICATION_CHARTER §2h.6.1 (v1.27, 2026-08-31, the exact-PDE rule)` a
different-model reference **caps at `GATE REACHED`, however exact its own algebra**.

### 0.4 The solver question is answered, and answered YES

`solidFoam` + `constAnIso` **does** genuine anisotropic conduction, including the
off-diagonal terms, at the right magnitude **and the right sign**, and it **does** accept
and run the recovered near-singular tensor to `rc = 0`. Measurements in §5. This is not
the reason the case fails.

### 0.5 RECOMMENDATION

**Do not register VMFL029 as a graded case.** Record it as a case-selection finding.
The constructive alternative — an anisotropic-conduction credential that *is*
`PASS`-capable — is described at §11 and its central measurement already exists (§5.2).

### 0.6 THE TWO REASONS THIS DOCUMENT IS NOT FREEZABLE (`§11.2`)

1. **An open gate question of exactly the kind §11.2 bars.** The archive contradicts
   itself: the matrix's null direction is `(0.866, 0.5)`, while the archive's own
   orthotropic block claims the near-zero direction is `(0, 1, 0)` with `k₁ = 1e-10`.
   *Which tensor is the case* is unresolved on the archive's own face, the manual prints
   no values to break the tie, and the two answers give different gates. §11.2:
   *"A section that reads 'flagged for the supervisor' is a BLOCKER on the freeze."*

2. **AND THE ONE I MUST DISCLOSE AGAINST MY OWN WORK.** The feasibility described here
   **included solver runs on the actual VMFL029 configuration** — `solidFoam` at
   `N = 40/80/160` and Python solves to `N = 1280` — and §7 reports the resulting gate
   profile. **Any band written into this document from here on is informed by the
   answer.** `CLAUDE.md` rule 2 makes the freeze's entire evidentiary content the claim
   that the gate *could not have been fitted*; this document **cannot make that claim**,
   and a freeze would not cure it. Feasibility compute was the right call and I would run
   it again — but it spends the registration, and saying so is cheaper than a row that
   quietly does not mean what it says.

---

## 1. Case, as the manual states it

| item | value | source |
|---|---|---|
| Domain | 1 m × 1 m square | manual p. 109, printed |
| Physics | steady-state conduction, anisotropic conductivity | manual p. 109, printed |
| Density | 2719 kg/m³ | manual p. 109, printed |
| Specific heat | 871 J/(kg K) | manual p. 109, printed |
| Conductivity | "Anisotropic … specified using matrix components" | **values NOT printed** |
| BCs | two opposite walls at fixed 100 K and 200 K | manual p. 109, printed |
| BCs | "User-defined profile for temperature distribution" on the other two | **profile NOT printed** |
| Reference | "compared with analytical solution for temperature distribution" | **formula NOT printed** |
| Results artefact | **Figure .29.2** only — a FIGURE, no table | manual p. 110 |

**There is no printed number in VMFL029 that can serve as a reference.** The manual gives
a density, a specific heat and a domain size; everything a gate would need is a picture.
`VMFLGPU004` (p. 233–234) is the SAME case on the GPU solver and is equally silent.

**Therefore: the lab-derived analytical solution is the ONLY admissible gate for this
case.** A digitised figure is not a measurement of anything and is not admissible here.

## 2. Setup inputs vs gate values — the line, stated explicitly (Task 5)

> **Setup inputs MAY come from the Ansys archive. A GATE VALUE MAY NOT, EVER.**

- **Admissible from the archive:** geometry, the conductivity tensor, the wall profiles,
  material properties, and any statement of *which model* the manual's analytical
  solution belongs to.
- **Inadmissible from the archive, from the figure, or from any Ansys artefact:** the
  reference temperature profile itself, in whole or in part.
- The gate reference is **the lab's own evaluation, to full double precision, of the exact
  solution of the PDE named in §3**, computed by `vmfl029_exact.py` in this directory.

**A LEAD, recorded because it is a classification input and not a gate value:** the
manual lists `3d.csv` among `VMFLGPU004`'s input files (p. 233). If that file carries the
analytical curve plotted in Figure `.gpu004.2` / `.29.2`, it would settle **which model
Ansys called "the analytical solution"** — rank-one or truncated. That is a §12.2 input
and worth recovering. **It could not be used as a gate value even if recovered.**

## 3. §12.2 CLASSIFICATION — stated on the face of the registration, before compute

Required by `ANSYS_VERIFICATION_CHARTER` §12.2 in four parts.

**(1) The continuum model the lab's solver discretises for this case.**
`solidFoam` with `heSolidThermo`/`constAnIso` solves, in enthalpy form and at steady state,

```
    div( (K/Cp) grad h ) = 0 ,   h = Cp T ,  Cp constant
 ⟺  div( K grad T ) = 0 ,        K = R diag(k₁,k₂,k₃) Rᵀ , constant, SPD.
```

Verified at source: `heSolidThermo.C:165,189` forms `kappa/Cp` and applies
`csysPtr_().transformPrincipal(...)`, so the solved tensor is exactly an eigendecomposition
`R diag(k) Rᵀ`. **Every** SPD tensor has one, so a general SPD `K` is representable —
and `K` must be **strictly** SPD, because `k_i > 0` is what makes the operator elliptic
and the matrix solvable.

**(2) The model the reference is the exact solution of.**
The only closed form this case admits is the exact solution of

```
    div( K_rank1 grad T ) = 0 ,  K_rank1 = v vᵀ ,  v = (1/2, −sqrt(3)/2)
 ⟺  ∂²T/∂s² = 0  along the chords in direction v.
```

This is **not** an elliptic equation and `K_rank1` is **not** SPD (`det = 4.8e-17`).
Its exact solution is `T` linear along each chord between the two boundary points that
chord strikes — closed form and instrument in `vmfl029_exact.py`, `T_rank1_closed`.

**(3) SAME or DIFFERENT?**

> ### **DIFFERENT.**

Reasoning, and it is a difference of *type*, not of accuracy:

- `K_arch` is SPD and the problem is a well-posed elliptic BVP; `K_rank1` is singular and
  the problem is a family of two-point ODEs. **Ellipticity is not a small parameter.**
- The two solutions differ **measurably**: max **2.07e-01 K** on the `x = 0.5` profile at
  `N = 80`, and the difference is a *feature*, not a residual — the rank-one solution has
  a slope discontinuity at `y = 1 − sqrt(3)/2 = 0.1339746` which the truncated problem
  smooths over `3.3e-03 m`.
- No closed form exists for `K_arch`: the shear that removes the cross term,
  `ξ = x, η = (K_xx y − K_xy x)/sqrt(det K)`, maps the unit square to a parallelogram of
  shear **130.6** and height **75.4**, on which Laplace has no separable solution.

**(4) Consequence.** Under `VERIFICATION_CHARTER §2h.6.1 (v1.27, 2026-08-31, the exact-PDE
rule)`, carried into this team by `ANSYS_VERIFICATION_CHARTER` §12.2, a `DIFFERENT` limb
**is registered at `GATE REACHED` from the outset.** `§2h.4`'s five conditions are
therefore **not** declared: they are the conditions for seeking `PASS`, and `PASS` is not
available here. `§12.2`'s closing rule cuts the other way too — this is not a cap by
reflex, it is a classification, and I would have written `SAME` had the algebra allowed it.

*(Citation form per `ANSYS_VERIFICATION_CHARTER` §12.3: no bare `§2h.6` appears in this
document, because that label denotes two different rules.)*

## 4. The one open input — status

| input | status |
|---|---|
| Geometry, 1 m × 1 m | **closed** (manual, printed) |
| ρ = 2719, Cp = 871 | **closed** (manual, printed) |
| Wall 2 = 200 K, wall 4 = 100 K | **closed** (archive; checked by the sister lane) |
| UDF `prof_aniso`: `T = 100 + 100x` on `y = 0`, `T = 100 + 100x²` on `y = 1` | **closed** (archive); continuity round the boundary and corner agreement verified |
| **Conductivity tensor** | **OPEN — the archive contradicts itself (§0.6 item 1)** |

The BC recovery is clean and I re-derived its corner consistency independently:
`100 + 100·0 = 100` and `100 + 100·1 = 200` on both profiles, matching the two constant
walls at all four corners. The red flag on that input is cleared.

## 5. FEASIBILITY — does the solver actually do anisotropic conduction? (Task 1)

**`laplacianFoam` cannot**: its `DT` is a `dimensionedScalar`. Ruled out without a run.

### 5.1 The shipped tutorial runs

`tutorials/heatTransfer/solidFoam/multiSolidWithAnisoConduction` copied to scratch and run
through its own `Allrun`: **`rc = 0`**, an `End` line present, final
`volAverage(zoneC) of T = 350.348`. `constAnIso` accepts `kappa (k1 k2 k3)` as principal
conductivities together with a `coordinateSystem { rotation { type axes; e1 …; e2 …; } }`.

### 5.2 THE ANISOTROPY IS REAL — measured, not read off the dictionary

Reading a dictionary proves nothing. The measurement is a **manufactured solution that is
a solution for one rotation and not for the other**, with the rotation as the ONLY thing
that changes between two runs.

Take `kappa (4 1 1)`. With `e1 = (1,1,0)`, `e2 = (−1,1,0)` the solved tensor should be
`R diag(4,1,1) Rᵀ = [[2.5,1.5,0],[1.5,2.5,0],[0,0,1]]`. The field

```
    T_ex = 100 − 0.375 x² + 1.25 x y − 0.375 y²
```

satisfies `K_xx T_xx + 2 K_xy T_xy + K_yy T_yy = 2.5(−0.75) + 2(1.5)(1.25) + 2.5(−0.75) = 0`
**only when `K_xy = +1.5`**. For `K_xy = 0` the residual is `−3.75`; for `K_xy = −1.5` it is
`−7.50`. So the test is sharp on the presence, the magnitude **and the sign** of the
off-diagonal conduction.

Two runs, 60×60, identical Dirichlet data from `T_ex` on all four walls, identical
`kappa (4 1 1)`, **differing only in the `coordinateSystem` rotation**:

| run | rotation | `max |T − T_ex|` | rms |
|---|---|---|---|
| `probeA_R45` | `e1 (1 1 0)`, `e2 (−1 1 0)` | **2.604e-05 K** | 2.604e-05 K |
| `probeA_R0` | `e1 (1 0 0)`, `e2 (0 1 0)` | **1.067e-01 K** | 6.223e-02 K |

`max|T_R45 − T_R0| = 1.0668e-01 K`, rms `6.2203e-02 K`. **The rotated run reproduces the
off-diagonal exact solution to 2.6e-05 K; the unrotated run, with the same conductivity
vector and the same boundary data, misses it by 4,100×.** Heat is being conducted at an
angle to the temperature gradient, and `solidFoam` has the sign right.

**General SPD tensors: YES.** `constAnIso` + `coordinateSystem` *is* the eigendecomposition
`K = R diag(k) Rᵀ`, and every SPD tensor has one — supply the eigenvalues as `kappa` and
the eigenvectors as `e1`, `e2`. **A rank-one projection is NOT representable**, and no
solver in this repository could represent it as an elliptic problem, because it is not one.

### 5.3 The recovered near-singular tensor RUNS

`kappa (0.999989 1.10001210e-05 1.0)` with `e1 = (−0.499994, 0.866029, 0)`,
`e2 = (−0.866029, −0.499994, 0)` — the eigendecomposition of `K_arch`, `k₃ = 1` out of
plane (irrelevant in a one-cell-thick `empty` case). `N = 80`, `blockMesh` + `solidFoam`:
**`rc = 0`**, `End` present, `residualControl h 1e-11` met at outer iteration **93**.

This was not a foregone conclusion. OpenFOAM's `gaussLaplacianScheme` splits
`Sf & K` into an implicit normal part `SfGammaSn` and an **explicit** tangential
correction `SfGammaCorr` (`gaussLaplacianScheme.C:170-190`). On an axis-aligned mesh with
this tensor the explicit part is `0.433` against an implicit `0.25` — **a deferred-correction
ratio of 1.73**, well above the usual stability rule of thumb. It converges anyway, with
`nNonOrthogonalCorrectors 3` and **relaxation 1.0**. Measured the other way: relaxation
`0.3` **stalls** at residual `1.4e-06` and never reaches the control in 3000 outer
iterations. Under-relaxing this case makes it worse, not safer.

### 5.4 Cross-instrument agreement, OpenFOAM vs an independent Python FD

At `N = 80`, the same problem solved by `solidFoam` (cell-centred FV, deferred correction)
and by an independent 9-point conservative finite-difference code:

- `max |T_OF − T_FD|` on the `x = 0.5` profile = **5.118e-03 K**, rms **3.340e-03 K**
  — on a 100 K range, i.e. 5e-05 relative.
- Deviation from the rank-one closed form: `2.0686e-01 K` (OpenFOAM) vs `2.0716e-01 K`
  (FD). **The two schemes disagree with the rank-one reference by the same amount to three
  figures** — so that deviation is physics-and-model, not a solver defect in either.

## 6. THE ANALYTICAL SOLUTION AND ITS TWO-INSTRUMENT CROSS-CHECK (Task 2)

Module: `cases/ansys_verification/VMFL029/vmfl029_exact.py`. Run `python3 vmfl029_exact.py
selftest`. All checks **PASS**.

### 6.1 The derivation

For constant SPD `K`, `div(K grad T) = 0` becomes Laplace's equation under the linear map
that diagonalises and equilibrates `K`. For `K_rank1 = v vᵀ` the map degenerates and the
operator collapses to `∂²T/∂s² = 0` along `v` — so `T` is **linear along each chord**.

Write `T = 100 + 100x + u`. The linear part `100 + 100x` satisfies *every* constant-`K`
equation and already matches three of the four walls, so `u = 0` on `x = 0`, `x = 1`,
`y = 0` and `u = 100(x² − x)` on `y = 1`. A chord through `(x,y)` leaves backwards through
`y = 1` **iff** `x > (1−y)/sqrt(3)`; otherwise both its endpoints carry `u = 0` and `u ≡ 0`.
Hence the closed form

```
  x_b = x − (1−y)/sqrt(3) ;  t₋ = 2(1−y)/sqrt(3) ;  t₊ = min( 2y/sqrt(3), 2(1−x) )
  u(x,y) = 0                                       if x_b ≤ 0
  u(x,y) = 100 (x_b² − x_b) · t₊/(t₊ + t₋)         otherwise
  T(x,y) = 100 + 100 x + u(x,y)
```

evaluated to full double precision. At `x = 0.5` it is flat at exactly 150 K for
`y ≤ 1 − sqrt(3)/2 = 0.1339746` and falls to 125 K at `y = 1`.

### 6.2 Instrument 1 vs instrument 2 — closed form vs independent ray-trace

`T_rank1_ray` computes the same object through a code path that shares **no algebra** with
the closed form: a generic ray/box intersection finds the two chord endpoints numerically,
then interpolates. Over **4000 random interior points**:

> **max |I1 − I2| = 5.684e-14 K.**

### 6.3 Instrument 3 — the closed form satisfies the PDE

`pde_residual_along_chord` differentiates the closed form twice along `v` by central
differences. Over 1484 points off the corner characteristic:

> **max |∂²T/∂s²| = 5.684e-06 K/m²**, against a field of order 150 K.

### 6.4 PLANTED-ZERO CONTROL on that reader

A zero from a reader not shown able to see a non-zero is not evidence (`CLAUDE.md` rule 3).
The residual reader is handed `T_closed + 1.234e-03 x²`, whose analytic second derivative
along `v` is `2·1.234e-03·v_x² = 6.170e-04`. The reader returns **6.167511e-04**. It sees
the plant; its zeros in §6.3 are therefore evidence. **The control runs before the check it
guards.**

### 6.5 Instrument 4 — the closed form is the `λ_min → 0` limit

Full 2-D anisotropic FD solves at `N = 400`, principal directions fixed, `λ_min` swept:

| `λ_min` | `max|T − T_closed|` | `L2` |
|---|---|---|
| 1e-02 | 3.7743e-01 K | 1.8302e-01 K |
| 1e-03 | 1.2862e-01 K | 3.1419e-02 K |
| 1e-04 | 8.3222e-02 K | 1.7277e-02 K |
| 1.100e-05 (the archive) | 7.8282e-02 K | 1.6391e-02 K |

Monotone approach, flattening into the `N = 400` discretisation floor. The closed form is
the right limit object — **and the table is also the §12.2 evidence: at the archive's own
`λ_min` the two models still differ by 7.8e-02 K, and that gap is not shrinking with mesh.**

## 7. THE CONSERVATION-IDENTITY MEASUREMENT (Task 3)

**The trap, named:** VMFL038's `τ_w` came out bit-exact on every mesh because the face
fluxes telescope. On a conduction problem **any net or integrated wall heat flux has
exactly that shape.** Tested, not assumed, in a cell-centred FV built the way OpenFOAM
builds it (implicit `SfGammaSn` + explicit `SfGammaCorr`), so the answer is about the
discretisation we would actually run.

### 7.1 NET wall heat flux — **PINNED. NON-DISCRIMINATING. DO NOT GATE ON IT.**

| `N` | left | right | bottom | top | **NET** | `|NET|/scale` |
|---|---|---|---|---|---|---|
| 40 | +2.4880043e+01 | −4.2675734e+01 | −4.8223740e+01 | +6.6019431e+01 | **+4.28e-11** | **6.48e-13** |
| 80 | +2.4940531e+01 | −4.2740071e+01 | −4.8159247e+01 | +6.5958787e+01 | **+1.72e-10** | **2.61e-12** |
| 160 | +2.4970258e+01 | −4.2764816e+01 | −4.8132163e+01 | +6.5926721e+01 | **+6.88e-10** | **1.04e-11** |

The net is at the linear-solver floor on **every** mesh and carries **no** mesh
information — it tracks the deferred-correction tolerance, nothing else. It is an
algebraic identity: every internal face flux enters two cell equations with opposite
signs, and each cell equation is zero at convergence. **Exactly the VMFL038 shape.**

### 7.2 SINGLE-wall heat flux — refines, but only at first order

Left-wall flux `24.880043 → 24.940531 → 24.970258` W/m. Successive changes
`6.049e-02` then `2.973e-02` → **`p_obs = 1.02`**, against a formal order of 2.

### 7.3 NORMALIZED TEMPERATURE ALONG `x = 0.5` — the manual's own quantity

Successive-level changes in the profile: `6.853e-01 K` (40→80), `3.604e-01 K` (80→160) →
**`p_obs = 0.93`**. Refines genuinely — it is not pinned — but **not at the formal order**,
and the finer Python ladder (§0.2) shows it does not recover second order by `N = 1280`.

### 7.4 The gate quantity, chosen

**Normalized temperature `Tnorm = (T − 100)/100` along the line `x = 0.5 m`**, the manual's
own comparison quantity, is the correct gate — the flux quantities are either pinned (net)
or no better behaved (single wall) while also not being what the manual compares.
**The measurement supports the brief's default and I record it either way.**

## 8. IF THE CASE WERE REGISTERED ANYWAY — the clauses, in full, for review

Recorded so the supervisor can rule on a complete object rather than a sketch.
**These are not in force. Nothing below is frozen.**

**8.1 Solver / discretisation.** `solidFoam`, OpenFOAM v2606; `heSolidThermo` /
`pureMixture` / `constAnIso` / `hConst` / `rhoConst`; `ddtSchemes steadyState`;
`laplacian(alpha,h) Gauss linear corrected`; `snGradSchemes corrected`;
`nNonOrthogonalCorrectors 3`; `relaxationFactors { h 1.0 }` (**0.3 stalls — measured,
§5.3**); `PCG`/`DIC`, `tolerance 1e-12`, `relTol 0`.

**8.2 The isotropic ladder, and why the triple would be entitled to Roache treatment.**
40×40 → 80×80 → 160×160, uniform, **cells ×4 per level, refinement ratio r = 2 in each
direction, aspect ratio 1 held constant at every level** — an isotropic family, which is
the condition VMFL038 R1 lacked and the reason its triple was not entitled to Roache
treatment. **Entitlement is necessary and not sufficient: §0.2 measures that this
particular triple would not be `CONVERGING`.**

**8.3 Completion clause, with the anchored-pattern trap named.** A level is complete only
if **all** hold: `rc = 0`; an `End` line; **the last time directory equals `endTime`**;
field `T` present at that time; the `ExecutionTime` line count equals the step count; and
**every field file at `endTime` is NEWER than the case's own `0/T`** (the age guard —
`0/T` is touched last at launch and so dates the run allowed to produce the answer). The
guard **refuses** a case where `0` or any time directory already exists.
**THE ANCHORED-PATTERN TRAP:** every one of these greps is anchored — `^End`,
`^ExecutionTime`, `^\s*rc=` — because an unanchored pattern matches the same word inside a
banner, a path or a warning and turns a failed run into a complete one. The comparator
**refuses (exit 2) rather than degrade.**

**8.4 Convergence clause, satisfiable across the whole honest range.** VMFL006 R1 died on
a clause that could not be met by a converged run. This one is satisfied by **either**
limb: (a) the initial residual of `h` has reached `residualControl` `1e-11`, **or**
(b) the initial residual is flat at the machine floor over the last 20 outer iterations
(`max/min < 10` with `max < 1e-10`), **or** (c) the residual is still monotonically
descending with `|d log10 r / d iter| > 1e-3` averaged over the last 50 iterations **and**
`r < 1e-8`. **Converged-flat-at-machine-floor and still-descending both PASS**; only
stalled-above-floor and rising fail.

**8.5 Planted-zero control, at EVERY level, BEFORE any clause that can refuse.** The
comparator plants `1.234e-03` into the read-back field at each level, re-reads it from
disk, and asserts it is seen; **this runs before the completion clause, the convergence
clause and the grading**, so no refusal can pre-empt the control and no zero can be
reported by a reader never shown able to see a non-zero.

**8.6 Roache gating and the GCI ceiling.** `P_MIN = 1.5`. **`GCI_MAX = 5 %`** at
`Fs = 1.25`: a triple whose fine-grid GCI exceeds `GCI_MAX` is `NOT A RESULT` even if
`CONVERGING`. No GCI is quoted when the three values are not monotone. Rule 5's one-way
conversion is unchanged: the gate can only turn `PASS`/`GATE FAIL` **into** `NOT A RESULT`.

**8.7 Numeric time-directory selection with a cardinality refusal.** The comparator
selects the time directory by **numeric** value (`max` over names matching `^[0-9]+$`),
never lexicographically. It asserts **exactly one** directory matches `endTime`; zero or
more than one is a **refusal (exit 2)**, not a choice.

**8.8 Zero-`assert` AST guard.** A guard walks the comparator's AST and refuses if any
`ast.Assert` node is present, so no check can be silently disabled by `python -O`. All
checks are explicit `if … : sys.exit(2)`.

**8.9 Machine-readable grading record.** `GRADING.json` beside the run root, carrying:
case id, `prereg_commit`, the sha256 of every frozen file at grading time, the three level
values, the triple classification, the observed order, the GCI, the reference value with
its instrument, the band, the verdict from the fixed vocabulary, and the measured
core-minutes.

**8.10 `writeFields` on every `fieldValue` object**, so every reported number has an
artefact on disk that outlives the log.

**8.11 Ceiling.** `GATE REACHED` maximum on every limb, by §3(4). **`PASS` is not
available for this case and is not sought.**

**8.12 Band — NOT SET, AND DELIBERATELY SO.** Under §0.6 item 2 any band written now is
informed by the answer. **No band appears in this document**, and one added later would
not be a pre-registration.

## 9. COST (`CLAUDE.md` rule 12)

Unit: **core-minutes** = wall s × ranks ÷ 60. All runs 1 rank, serial, c7a.4xlarge.

**Measured in scratch** (`solidFoam`, `ExecutionTime`, the real tensor and BCs):

| level | wall s | ranks | core-min |
|---|---|---|---|
| 40×40 | 0.18 | 1 | 0.0030 |
| 80×80 | 1.87 | 1 | 0.0312 |
| 160×160 | 20.05 | 1 | 0.3342 |
| **ladder total** | **22.10** | 1 | **0.368** |

Add meshing and grading: **EXTRAPOLATED BRACKET 0.40 – 0.75 core-min** for the whole
three-level ladder, point estimate **0.50 core-min**. Basis: measured solver time above
plus a 2× allowance for `blockMesh`, `postProcess` and comparator passes. **Extrapolated,
not measured**, for the total; the three solver rows are measured.

Derived dollars at the recorded `$0.0513/core-h`: **≈ $0.0004**. **Derived, not measured**
— the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5).

**The cost that actually matters, and it is the one that kills the case.** Extrapolating
the measured ×10 per level (0.18 → 1.87 → 20.05 s):

| level | extrapolated wall s | core-min |
|---|---|---|
| 320 | ≈ 2.0e+02 | ≈ 3.3 |
| 640 | ≈ 2.0e+03 | ≈ 33 |
| 1280 | ≈ 2.0e+04 | ≈ 333 |
| 2560 | ≈ 2.0e+05 | ≈ 3.3e+03 |
| **3015 (10 cells across the feature)** | **≈ 3.4e+05** | **≈ 5.7e+03** |

A triple *sitting in* the asymptotic range — 3015/6030/12060 — is **≈ 6.3e+05 core-min
(≈ 10,500 core-hours, ≈ $540 derived)** for a case whose entire value is one figure the
manual does not even tabulate. **Cheap in principle, unaffordable in practice.**

**Cap.** Were this run at 40/80/160, the cap would be **2.0 core-min**, ~4× the point
estimate. An overrun **stops the run**; it does not get a new budget.

**Runner cap enforcement is `ADVISORY` / `INERT` / `OFF`.** No `ENFORCE` claim is made
here: the queue runner writes `CAP_OVERRUN.txt` but this document does not assert that
anything kills the process at the cap.

## 10. WHAT I COULD NOT VERIFY

- **Which tensor is the case.** The archive's matrix and its orthotropic block disagree
  (§0.6). I did not open the archive; that recovery is the sister lane's and I take its
  numbers as reported, having re-derived every consequence from them myself.
- **What model the manual's "analytical solution" belongs to.** The manual prints no
  formula and no table. My §3 classification rests on what closed forms *exist* for this
  tensor, not on a reading of Ansys's intent. `VMFLGPU004`'s `3d.csv` (§2) could settle it.
- **The OpenFOAM-side observed order beyond `N = 160`.** The orders in §0.2 above 160 are
  from the Python instruments. `solidFoam` and the FD agree to `5.1e-03 K` at `N = 80`
  (§5.4), so I expect the same behaviour, but I did not run OpenFOAM at 320+ and do not
  report it as measured.
- **Whether `constAnIso` is bit-identical to Fluent's matrix input.** Not tested; not
  needed, since no Ansys number is admissible as a gate value here.

## 11. THE CONSTRUCTIVE ALTERNATIVE

If the team wants an anisotropic-conduction credential that is genuinely `PASS`-capable,
**the central measurement already exists and is in §5.2.** A well-conditioned SPD tensor —
e.g. `K = [[2.5,1.5,0],[1.5,2.5,0],[0,0,1]]`, condition number 4 — admits an **exact
solution of the SAME PDE the solver discretises** in closed form, so §12.2 answers `SAME`
and `PASS` is available subject to §2h.4's five conditions. On such a case the solution is
smooth, the layer parameter is `O(1)`, and a 40/80/160 triple is genuinely asymptotic.

That is a **new registration on a clean case**, frozen before any compute on it, not a
repair of this one — and today's runs on the manufactured quadratic must **not** be
reused as its feasibility, for the same rule-2 reason set out in §0.6 item 2.

---

## APPENDIX A — artefacts

| artefact | path |
|---|---|
| This draft | `cases/ansys_verification/VMFL029/PREREGISTRATION.md` |
| Reference module + selftest | `cases/ansys_verification/VMFL029/vmfl029_exact.py` |
| Manual sidecar, VMFL029 | `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt` (p. 109–110) |
| OpenFOAM tutorial exercised | `/usr/lib/openfoam/openfoam2606/tutorials/heatTransfer/solidFoam/multiSolidWithAnisoConduction` |
| Solver source read | `.../solidThermo/lnInclude/heSolidThermo.C:155-189`; `.../finiteVolume/lnInclude/gaussLaplacianScheme.C:159-190` |

**Feasibility runs were made in the lane's scratch directory and are NOT cited as a path
here** (`CLAUDE.md` rule 13: a repository document never cites a scratch path). Every
number in this document is reproducible from `vmfl029_exact.py selftest` and from the
case-generation recipe in §8.1 and §5.2/§5.3.

## APPENDIX B — amendment log

*(none — this document has never been frozen and has graded nothing)*
