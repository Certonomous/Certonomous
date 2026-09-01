# T23G2 — PRE-REGISTRATION. THE ORDER STUDY THAT T23G COULD NOT BE

**Version 1.0. Frozen at this file's commit. NO COMPUTE HAS RUN.**

**Status: PENDING — awaiting the supervisor's personal read of this document and
of the comparator as a diff, before any solver is launched
(`SUPERVISION_CHARTER.md` §3; `CLAUDE.md` rule 2).**

Successor to `T23G_PREREGISTRATION.md` / `T23G_RESULTS.md`, whose rung verdict was
**NOT A RESULT** on all three quantities: every level solved, converged and
plateaued, and the observed order came out **0.3744–0.3796**, below the 0.5
`STAGNANT` floor, making the triple `NOT A RESULT` under `CLAUDE.md` rule 5
clause (2) whatever the values said.

**Authority for this successor:** Sanaa's directive of 2026-09-01 ~15:45Z, commit
`f4c8e466`, `etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`,
§0 (the automatic convergence study) and §1 (motor in duct). Her §1 orders four
cause candidates checked **in order**, (a) through (d), plus y+ recorded on every
level and 8+ cells across the wall at the coarsest level.

**This registration supersedes nothing frozen.** `T23G_PREREGISTRATION.md` and
`T23G_RESULTS.md` stand unaltered; their rung is graded and closed. This is a new
rung with its own gates.

---

## 0. WHAT IS ALREADY MEASURED, AND THEREFORE CANNOT BE REGISTERED AS A PREDICTION

**This section exists because `CLAUDE.md` rule 2 makes the freeze the document's
entire evidentiary content.** Three of Sanaa's four candidates were settled from
artifacts the lab already owned, **before** this registration was written, by a
read-only reader that launched no solver and wrote nothing into the graded tree.
A gate cannot be registered on an answer already in hand. Each finding below is
therefore recorded as a **measurement**, never as a prediction, and none of them
gates this rung.

The reader used is
`docs/campaigns/T-family/t23g_readonly_diagnosis.py` — campaign helper code,
**not** a comparator, not on any grading path, and cited here only as the
provenance of §0. **Its
ability to see what it claims to see is established, not assumed**: it reproduces
T23G's three independently graded quantities bit-for-bit from the same fields —
`Q1` 343.91005562 / 342.15982893 / 340.81450113 K, `Q2` 342.07048118 /
340.33460278 / 338.99750093 K, `Q3` 348.00610508 / 346.26564091 / 344.92301454 K,
each identical to `T23G_GRADED.json` to every digit that record carries. Under
this rung the same measurements are **re-taken by the registered comparator**
(§7), and nothing in §0 is carried into a T23G2 verdict on the scratch reader's
word.

### 0.1 Candidate (a) — iterative convergence — is **EXCLUDED**, by data the lab already owned

Sanaa's premise was that T_max stationarity was 0.05 K and that the inter-level
differences might be of that same size. **The premise does not survive the raw
series.** Read at full precision from each level's own
`postProcessing/<region>/<region>_T/0/fieldMinMax.dat` (12 significant figures,
resolution ≈ 1e-10 K), the measured iterative change in max(T) is:

| level | region | change over last 1,000 it | over last 2,000 it | over last 5,000 it | first iteration from which \|T−T_final\| ≤ 1e-6 K |
|---|---|---|---|---|---|
| `T23G_C` | housing | 0.000000e+00 K | 0.000000e+00 K | 0.000000e+00 K | 600 |
| `T23G_M` | housing | 0.000000e+00 K | 0.000000e+00 K | 0.000000e+00 K | 1,900 |
| `T23G_F` | housing | 0.000000e+00 K | 0.000000e+00 K | 3.268260e-04 K | 6,900 |
| `T23G_C` | core | 0.000000e+00 K | 0.000000e+00 K | 0.000000e+00 K | 600 |
| `T23G_M` | core | 0.000000e+00 K | 0.000000e+00 K | 0.000000e+00 K | 1,900 |
| `T23G_F` | core | 0.000000e+00 K | 0.000000e+00 K | 3.273909e-04 K | 6,900 |

The inter-level differences are **1.750227 K** (C→M) and **1.345328 K** (M→F) on
Q1, and 1.740464 / 1.342626 K on Q3.

**Sanaa's §0 point 2 ratio test, taken on the actual measured iterative change
rather than on the registered criterion:** on the most pessimistic window that
shows any movement at all — the last 5,000 iterations of the finest level —

> 1.345328 K / 3.268260e-04 K = **4,116×**

against her requirement of **≥ 10×**. On the window the plateau gate actually
uses (the last 2,000 iterations) the measured change is an exact zero at 12
significant figures, and the ratio is bounded below by ≈ 1.3e+10.

**Candidate (a) is excluded by a factor of at least four hundred over her
threshold.** Tightening the energy residual to 1e-9 and the stationarity window
to 0.005 K over 2,000 iterations would change nothing that any of these
quantities can see: the energy residual at endTime was already
**8.724e-10 / 9.574e-10 / 9.996e-10** on C / M / F — i.e. already at her 1e-9
target — and the last 3,000 iterations of every level moved max(T) by nothing at
all. **Re-running the three levels to test (a) would have spent ~180 core-minutes
to reproduce a zero already on disk.**

*Provenance of the raw numbers: the six `fieldMinMax.dat` series named above; the
residuals from each level's own `log.solve`, final `Initial residual` per field.*

**One clause of her (a) IS carried forward as a gate anyway** — not because (a)
is live, but because the T23G instrument had a hole. See §0.4.

### 0.2 Candidate (b) — mesh similarity — is **A REAL DEFECT, MEASURED AND QUANTIFIED, AND IT IS NOT THE CAUSE**

Sanaa asked whether the wall-layer count and growth ratio are identical across
levels with only the spacing scaled, and said that if the coarsest level had
fewer layers the ladder is not similar and must be rebuilt.

**Read from `build_t23.py` at each level, the parameters differ exactly as a
structured ladder requires** — every count scales by 2, so the topology is
similar and the layer count is not "dropped" in the snappyHexMesh sense her
question anticipates:

| parameter | `T23G_C` | `T23G_M` | `T23G_F` | ratio |
|---|---|---|---|---|
| `NR_BL_IN` (inner BL, fluid) | 20 | 40 | 80 | ×2, ×2 |
| `NR_MID` (fluid core band) | 20 | 40 | 80 | ×2, ×2 |
| `NR_BL_OUT` (outer BL, fluid) | 15 | 30 | 60 | ×2, ×2 |
| `NR_HOUS` (housing, radial) | **4** | 8 | 16 | ×2, ×2 |
| `NR_CORE` | 12 | 24 | 48 | ×2, ×2 |
| `NZ_UP / NZ_MID / NZ_DOWN` | 40/70/50 | 80/140/100 | 160/280/200 | ×2, ×2 |
| total expansion ratio in both BL bands | **40 (held FIXED)** | **40** | **40** | ×1 |

**The defect is in the last row.** Holding the *total* expansion ratio fixed at
40:1 while doubling the cell count in the band means the *first cell* does **not**
halve. Measured, wall-normal, from the polyMesh of each level:

| wall patch | first-cell centroid distance C / M / F [m] | C/M ratio | M/F ratio | required |
|---|---|---|---|---|
| `fluid_to_housing` | 2.2505e-05 / 1.1534e-05 / 5.8368e-06 | **1.951175** | **1.976110** | 2.000000 |
| `centrebody_up`, `centrebody_down` | 2.2505e-05 / 1.1534e-05 / 5.8368e-06 | **1.951175** | **1.976110** | 2.000000 |
| `duct_wall` | 2.9491e-05 / 1.5252e-05 / 7.7508e-06 | **1.933650** | **1.967745** | 2.000000 |

Independently corroborated by `checkMesh`'s own minimum cell volume in the fluid
region — 2.63050e-10 / 6.73949e-11 / 1.70507e-11 m³, ratios **3.903** and
**3.953** where exact 2-D similarity at r = 2 requires **4.000**.

**So the three T23G meshes are NOT geometrically similar in the boundary layer**,
the error is 2.44 % then 1.20 %, and it **drifts** between the two steps rather
than cancelling. That is a genuine similarity defect and this rung repairs it
(§2.2).

**And it is arithmetically far too small to be the cause of p ≈ 0.375.**
Substituting the measured effective ratio 1.9512 for the nominal 2.0000 in
`p = ln(e32/e21) / ln(r)` moves Q1's order from **0.3796 to 0.3931** — a shift of
0.014, against a shortfall of more than 1.1. **Candidate (b) is a defect to fix,
not an explanation.**

**Two further findings under (b), both against the directive:**

- **`NR_HOUS = 4` at the coarsest level.** Sanaa requires 8+ cells across the wall
  at the coarsest level; T23G's coarsest carries 4, and `build_t23.py`'s own
  comment says so in terms ("the COARSE arm of a ladder is deliberately below
  it"). **This rung's coarsest level carries 8** (§2.1).
- **The wall is 3.9962 mm, not the 3.5 mm the directive names.** Measured from the
  housing region's bounding box, radial extent 0.0374643083093 − 0.0334681154230
  = **3.99618 mm**. The 8-cell floor is applied to the wall this geometry actually
  has. Recorded so no reader has to reconcile two numbers silently.

### 0.3 Candidate (d) — a smoother companion quantity — is **MEASURED, AND IT DOES NOT RESCUE THE ORDER**

Sanaa's (d) prescribes the **core's volume-averaged temperature** and the
**housing surface heat flux** as order-study quantities, on the ground that a
single-cell maximum is a poor one. **Both were computed, this session, from the
T23G fields already on disk — no solver, no new compute.** Result:

| quantity | `T23G_C` | `T23G_M` | `T23G_F` | e(C−M) | e(M−F) | ratio | **p** |
|---|---|---|---|---|---|---|---|
| **core volume-averaged T** [K] | 344.47519848 | 342.74242857 | 341.40808211 | 1.732770 | 1.334346 | 1.2986 | **0.3769** |
| housing volume-averaged T [K] | 342.13180239 | 340.39683113 | 339.06015644 | 1.734971 | 1.336675 | 1.2980 | **0.3763** |
| Q2 interface areaAvg T [K] *(graded)* | 342.07048118 | 340.33460278 | 338.99750093 | 1.735878 | 1.337102 | 1.2982 | **0.3766** |
| Q1 housing max T [K] *(graded)* | 343.91005562 | 342.15982893 | 340.81450113 | 1.750227 | 1.345328 | 1.3010 | **0.3796** |
| Q3 core max T [K] *(graded)* | 348.00610508 | 346.26564091 | 344.92301454 | 1.740464 | 1.342626 | 1.2963 | **0.3744** |
| **housing surface heat flux** [W] | 1.89743422 | 1.89740022 | 1.89733182 | 3.399e-05 | 6.840e-05 | **0.4970** | **−1.0087** |

**The order is 0.3744 to 0.3796 across every temperature quantity the case can
produce** — two single-cell maxima, one boundary area-average, and two true
volume integrals over two different regions. The spread is 0.0052. **Replacing a
max with a volume integral moves the observed order by half a percent.**
Non-smoothness of the sampling is decisively **not** the cause, and candidate (d)
alone will not move p into any acceptance band.

**The housing surface heat flux behaves worse, not better, and for a physical
reason.** Its successive differences *grow* with refinement (3.4e-5 then 6.8e-5 W,
ratio 0.497 < 1), which is a **DIVERGENT** triple. The quantity is pinned by the
imposed 305 W sector source to within 3.6e-5 relative, so what varies across the
ladder is the source-imposition residual, not the discretisation error. It is
registered under this rung because Sanaa named it, and it is registered as
**REPORTED, NEVER GATED** (§5.2).

*Caveat, stated rather than buried: the two volume averages and the surface heat
flux are the scratch reader's own constructions. The volume averages inherit the
reader's validation, since the same cell-volume machinery reproduces the graded
area-average `Q2` exactly. The **heat flux does not** — it is a one-sided
wall-gradient construct with no independently graded counterpart, and its
absolute value (1.897 W against a fluid-side enthalpy rise of 1.827 W, a 3.8 %
imbalance) is **not** offered as a verified number. Its **e-ratio of 0.497 is
what §0.3 rests on**, and that conclusion survives any constant offset in the
construction.*

### 0.4 What T23G could NOT measure, and what this rung does about it

- **y+ was `BLIND` on all three T23G levels.** `log.yPlus.fluid` says on its own
  face *"Unable to find turbulence model in the database"* and prints
  `min = max = average = 0` on all four patches; the comparator refused those
  zeros rather than reading them, which is rule 3 working. **The cause is now
  identified**: `postProcess` does not construct the compressible turbulence
  model, so `compressible::turbulenceModel` is absent from its object registry.
  The registered fix is to run the function object through the solver's own
  `-postProcess` mode (§5.4).
- **`Q2` had no `G-PLATEAU` at all** — `T23G_GRADED.json` carries
  `/plateau/Q2 = "NOT MEASURED"`. Nothing in that artifact bounds Q2's iterative
  change, so Sanaa's §0 point 2 ratio test **cannot be applied to Q2 at all**.
  That is a registrable instrument gap and this rung closes it: **stationarity is
  measured on EVERY graded quantity, not only on the maxima** (§5.3).
- **A published record carries a false justification.** `roache_triple`'s `why`
  string, printed for all three T23G quantities and stored in the json, ends
  *"NO GCI is quoted because the three values are not monotone"*, while the same
  record carries `monotone: true` on all three and the values descend cleanly.
  The **action** is correct — rule 5 forbids a GCI beside a non-`CONVERGING`
  triple — and only the stated reason is wrong. It matters diagnostically,
  because a reader told "not monotone" will hunt oscillatory convergence when the
  real signature is clean monotone convergence whose differences shrink too
  slowly. **Referred as a docket row against the comparator; NOT repaired here.**
  `scripts/roache_triple.py` is on the grading path of a rung whose compute has
  run, and no exception has been granted for it.

---

## 1. THE FINDING THAT REFRAMES THE WHOLE STUDY, AND THE ONE THING IN §1 THAT CANNOT BE DONE AS WRITTEN

`T23G_F/system/fluid/fvSchemes`, read this session:

```
div(phi,U)      bounded Gauss linearUpwind grad(U);     <- second order
div(phi,K)      bounded Gauss upwind;                   <- FIRST order
div(phi,h)      bounded Gauss upwind;                   <- FIRST order
div(phi,k)      bounded Gauss upwind;                   <- FIRST order
div(phi,omega)  bounded Gauss upwind;                   <- FIRST order
```

**The energy equation's convection term is first-order upwind.** Every quantity
this rung grades is a temperature, set by that equation.

Sanaa's own §0 point 3 fixes the acceptance band as *"p within 0.5 of the
scheme's formal order"*, and gives *"second order: p in 1.5 to 2.5"* as the
worked example. **For `div(phi,h) = bounded Gauss upwind` the formal order is 1,
so her rule yields an acceptance band of [0.5, 1.5] — not [1.5, 2.5].**

> **NAMED PLAINLY, AS THE BRIEF REQUIRES: a p inside 1.5–2.5 is UNREACHABLE on
> this case by mesh refinement alone.** No ladder, however fine, however similar,
> however many levels, will drive a first-order scheme to second-order
> convergence. Sanaa's §1 instruction *"run until p lands in 1.5 to 2.5"*
> therefore **cannot be executed as written on the T23G discretisation.** It
> requires a change to the scheme, which is a change to the physics model's
> numerics and not a mesh parameter, and it means every level must be re-run.
> **That is a decision above a lane, and it is put to the supervisor here rather
> than taken quietly.**

**This registration takes the scheme change** (§2.3), because the alternative —
keeping upwind and targeting [0.5, 1.5] — would return a rung that satisfies
Sanaa's *arithmetic* while failing her *stated goal*, and would leave the
sixteen-point map banded off a first-order solution.

**It also does not claim the scheme is the whole answer.** The measured order is
**0.375, which is below first order.** A first-order scheme explains p ≤ 1; it
does not by itself explain p = 0.375. The second measured cause is §1.1.

### 1.1 y+ — measured for the first time on this family, and it disqualifies the coarsest level

Computed from the `U`, `nut` and polyMesh already on disk, with
`u_tau = sqrt((nu + nut_w)·U_t / y)` and `nut_w = 0` exactly (the wall condition
is `nutLowReWallFunction`, verified present at endTime, not merely in `0.orig`):

| patch | `T23G_C` min/avg/max | `T23G_M` min/avg/max | `T23G_F` min/avg/max |
|---|---|---|---|
| **`fluid_to_housing`** *(the heat-transfer surface)* | 1.4045 / **1.4203** / 1.4393 | 0.7334 / **0.7416** / 0.7515 | 0.3766 / **0.3809** / 0.3861 |
| `centrebody_down` | 1.3569 / 1.3764 / 1.4034 | 0.7086 / 0.7187 / 0.7331 | 0.3640 / 0.3692 / 0.3766 |
| `centrebody_up` | 1.4406 / 1.5603 / 2.9707 | 0.7518 / 0.8135 / 1.8260 | 0.3862 / 0.4184 / 1.1097 |
| `duct_wall` | 1.7269 / 1.8603 / 3.8534 | 0.9057 / 0.9741 / 2.3957 | 0.4676 / 0.5034 / 1.4671 |

**Sanaa's §0 point 1 requires y+ under 1 on every level of a wall-resolved case.
`T23G_C` fails it on every patch, including the heat-transfer surface, where y+
is 1.42.** The wall treatment itself does *not* change across the ladder —
`nutLowReWallFunction` sets `nut_w = 0` at every level, so there is no
wall-function switch, and the T23G record's stated worry that the levels might
not share one wall treatment is **relieved**. What the coarse level fails is not
consistency but **resolution**: its first cell straddles out of the viscous
sublayer, so it is not solving the same boundary-layer problem the finer levels
are.

**That is Sanaa's candidate (c) — the coarsest level outside the asymptotic
range — now with an instrument behind it.** This rung drops that resolution
entirely: **the coarsest T23G2 level sits at the T23G_M resolution or finer, and
every level is registered to satisfy y+ < 1 on the heat-transfer surface.**

`T23G_F` also carries y+max = 1.4671 on `duct_wall` and 1.1097 on
`centrebody_up` — so **no level of T23G met y+ < 1 everywhere.** The near-wall
spacing on the outer band is refined independently in this rung to fix that
(§2.2).

### 1.2 The fifth candidate — the conjugate interface — read, and its damaging variant EXCLUDED

Beyond Sanaa's four, this lab's own candidate was the conjugate interface
treatment: all graded quantities sit on or behind a solid/fluid interface, and
this family has been at an interface before (H-4 / T9a, D454, L-227).

Read this session, costing no compute:

- Both sides use `compressible::turbulentTemperatureRadCoupledMixed` with
  `Tnbr T`, `useImplicit true` — the current, implicitly coupled conjugate
  condition, not a legacy explicit one.
- The interface is **1:1 face-matched** — `fluid_to_housing` and
  `housing_to_fluid` carry 70 / 140 / 280 faces at C / M / F on both sides. There
  is no mapping interpolation error.
- The fluid side declares `kappaMethod fluidThermo`. **The concern was that this
  might return the laminar conductivity and drop the turbulent contribution at
  the wall.** Read at source —
  `/usr/lib/openfoam/openfoam2606/src/thermoTools/lnInclude/temperatureCoupledBase.C`,
  `case mtFluidThermo` — the branch looks up `compressible::turbulenceModel` by
  `turbulenceModel::propertiesName` and, when it is present, returns
  **`ptr->kappaEff(patchi)`**. Inside the solver it is present. **The conjugate
  coupling uses the effective conductivity. The damaging variant is excluded.**

*(The same registry lookup is the one `postProcess` cannot satisfy — which is
exactly why y+ came back blind while the conjugate coupling worked. One cause,
two symptoms.)*

**What is NOT excluded:** the interface flux is reconstructed from one-sided
normal gradients on each side, which is formally **first order in the wall-normal
cell size**, on both sides, regardless of the interior scheme. That remains a
live candidate and is named in §6 as the falsifier of this rung's whole reading.

---

## 2. THE LADDER

### 2.1 Three levels, r = 1.5 exactly, from ONE parametric script

Sanaa's §0 point 1 asks for a uniform refinement ratio between 1.5 and 2.0 in
every direction, and her §1 (c) names r = 1.5. Every count below is an integer at
every level and every ratio is exactly 1.5.

| parameter | `T23G2_L1` | `T23G2_L2` | `T23G2_L3` |
|---|---|---|---|
| `NR_BL_IN` (inner BL) | 40 | 60 | 90 |
| `NR_MID` (fluid core band) | 40 | 60 | 90 |
| `NR_BL_OUT` (outer BL) | 32 | 48 | 72 |
| `NR_HOUS` | **8** | 12 | 18 |
| `NR_CORE` | 24 | 36 | 54 |
| `NZ_UP / NZ_MID / NZ_DOWN` | 80 / 140 / 100 | 120 / 210 / 150 | 180 / 315 / 225 |
| **fluid cells** | 35,840 | 80,640 | 181,440 |
| **housing cells** | 1,120 | 2,520 | 5,670 |
| **core cells** | 3,360 | 7,560 | 17,010 |
| **TOTAL** | **40,320** | **90,720** | **204,120** |

Cell-count ratio **2.250000** at both steps, in every region separately. The case
is a 5° wedge one cell thick circumferentially, so refinement acts in **two**
directions: `dim = 2`, and 2.25× cells is **r = 1.5000000**, not 1.5³.

**`NR_HOUS = 8` at the coarsest level satisfies Sanaa's 8-cells-across-the-wall
requirement**, on the 3.9962 mm wall this geometry actually has (§0.2).

### 2.2 The similarity repair — first-cell spacing is REGISTERED and the grading is DERIVED

**This is the (b) fix.** T23G specified `(n, total expansion ratio)` and let the
first cell fall where it may, which is why the first cell refined by 1.951 and
1.976 instead of 2.000. **T23G2 specifies `(n, first-cell height)` and derives
the expansion ratio**, so the first cell scales by exactly 1/r at every step, in
every band, by construction.

Registered first-cell heights (full cell height, wall-normal, metres):

| band | `T23G2_L1` | `T23G2_L2` | `T23G2_L3` | ratio |
|---|---|---|---|---|
| inner BL (`fluid_to_housing`, `centrebody_*`) | 2.306800e-05 | 1.537867e-05 | 1.025245e-05 | 1.500000 |
| outer BL (`duct_wall`) | 7.750800e-06 | 5.167200e-06 | 3.444800e-06 | 1.500000 |

The inner value is `T23G_M`'s measured first cell, whose y+ on the heat-transfer
surface is a **measured** 0.7416. The outer value is **half** `T23G_F`'s measured
`duct_wall` first cell, chosen so that the outer band's y+ maximum clears 1 at
every level — the thing no T23G level achieved.

The build script computes the per-cell growth `k` from `(n, L, delta1)` for each
band and each level. **Predicted growth ratios, all comfortably inside the 1.25
cap Sanaa's §4 sets for the F28 generator**: inner band k ≈ 1.099 / 1.070 /
1.043; outer band k ≈ 1.187 / 1.126 / 1.078. **`G-MESHSIM` gates all of this from
the built mesh (§5.5); none of it is taken on the script's word.**

### 2.3 The scheme change — second-order energy convection

Registered change to `system/fluid/fvSchemes`, and the ONLY change to the
discretisation:

| term | T23G (frozen) | **T23G2 (registered)** |
|---|---|---|
| `div(phi,U)` | `bounded Gauss linearUpwind grad(U)` | **unchanged** |
| `div(phi,h)` | `bounded Gauss upwind` | **`bounded Gauss limitedLinear 1`** |
| `div(phi,K)` | `bounded Gauss upwind` | **`bounded Gauss limitedLinear 1`** |
| `div(phi,k)` | `bounded Gauss upwind` | **`bounded Gauss limitedLinear 1`** |
| `div(phi,omega)` | `bounded Gauss upwind` | **`bounded Gauss limitedLinear 1`** |
| `div(phid,p)` | `bounded Gauss upwind` | **unchanged** — pressure-flux term, kept upwind for stability; it does not carry the graded quantity |
| everything else | — | **unchanged** |

Rationale in §1. `limitedLinear 1` is a bounded second-order TVD scheme:
second-order accurate where the solution is smooth, degrading locally at extrema,
which is what makes it admissible on `h`, `k` and `omega` where an unbounded
`linear` is not.

**Consequence, registered in advance: `G-REPRO` is NOT APPLICABLE to this rung.**
T23G_M reproduced a prior case bit-exactly because it shared that case's
discretisation. No prior case shares T23G2's. **This is recorded as
`NOT APPLICABLE` with its reason, and never as a pass** — an unevaluated gate is
not a passed one.

### 2.4 Everything held invariant

Geometry, operating point and physical properties are **byte-identical to T23G**
and are re-asserted, not assumed: `P_LOSS = 305 W` (full 360°, applied as the 5°
sector share), `U_INF = 20 m/s`, `T_INF = 288 K`, air (rho 1.2, cp 1005,
k 0.026, mu 1.8e-5, Pr derived so k is exactly 0.026), aluminium housing
(2700 / 900 / 167), core (7000 / 450 / 40), 6 mm shaft bore, wedge 5.0°. Turbulence
model, wall conditions (`nutLowReWallFunction`, `alphatWallFunction` Prt 0.85,
`noSlip`) and the conjugate interface condition are unchanged.

**Level invariants, asserted by the comparator across all three levels:** the
`0.orig/` file set, the `constant/` file set (excluding `cellToRegion`, a build
artefact, exempted by name), the `system/` file set, and the `blockMeshDict`
`vertices` block. Anything that differs and is not in the §2.1/§2.2/§2.3 tables
is a **REFUSAL**, not a note.

### 2.5 Ranks and decomposition — recorded explicitly as the absence it is

**`ranks = 1` on every level. `decomposePar` is NOT run. There is no
decomposition, and therefore no decomposition seed or method.** This is stated
positively so that no reader has to infer it from silence, and so that the
arithmetic path is identical in kind at all three levels.

**Any later move to `ranks > 1` requires a dated addendum and cannot be made
silently**, because it changes the summation order and would place a per-level
perturbation inside an order study. Budget: 3 single-rank cores, one per level,
launched concurrently.

---

## 3. THE GRADED QUANTITIES, AND WHICH ONE CARRIES THE ORDER

**Sanaa's §1 (d) is followed literally, and this record says so explicitly as she
requires:**

> **The ORDER STUDY is carried by the core's volume-averaged temperature (`Q4`)
> and the housing surface heat flux (`Q5`). The BAND that `Q4` produces is
> APPLIED TO THE REPORTED MAXIMUM TEMPERATURES `Q1` and `Q3`, which are the
> numbers the sixteen-point map and Act A actually display.**

| id | quantity | region / patch | role |
|---|---|---|---|
| **`Q4`** | **volume-averaged T** | core | **PRIMARY ORDER QUANTITY — `G-ORDER` and the GCI are computed on this and on nothing else** |
| **`Q5`** | **surface heat flux** | `housing_to_fluid` | **SECOND ORDER QUANTITY — REPORTED, NEVER GATED** (§5.2) |
| `Q1` | max(T) | housing | reported; **receives `Q4`'s band** |
| `Q3` | max(T) | core | reported; **receives `Q4`'s band** |
| `Q2` | areaAvg(T) | `housing_to_fluid` | reported; receives `Q4`'s band |
| `Q6` | volume-averaged T | housing | reported; carried because §0.3 measured it and it costs nothing |

Triples are graded on **ΔT = T − 288.0 K** for temperatures, and on the raw value
for `Q5`. `Fs = 1.25`. `dim = 2`.

**Grade the FINE value.** The Richardson extrapolate is **REPORTED beside the
fine value and is NEVER GATED ON**, at any level of this rung, for any quantity.
*Reason, stated because a registration written after a defect is known must not
make it load-bearing:* the extrapolate sign inversion is a known live defect in
this family's comparators, survivable only because it is display-only everywhere
it currently lives. **This registration does not change that.**

---

## 4. THE REGISTERED PREDICTIONS — EVERY ONE OF THEM CAN LOSE

The gates are §5. These are the falsifiable claims, recorded separately so that a
prediction holding cannot be mistaken for a gate passing.

**P1 — the observed order.** I predict **p(`Q4`) = 1.7**, inside **[1.3, 2.1]**.
> **This can lose in both directions, and one loss mode is registered
> explicitly: if p lands in [1.3, 1.5), P1 HOLDS while `G-ORDER` GATE FAILS. That
> combination is a GATE FAIL. A prediction that held is not a rescue and will not
> be reported as one.**
> Basis: the scheme change lifts the formal order from 1 to 2, and dropping the
> non-wall-resolved level removes a level that was not solving the same
> boundary-layer problem. Basis for the doubt: the measured 0.375 is below first
> order, so at least part of the shortfall is unexplained by either change.

**P2 — the fine value, and its direction.** I predict
**ΔT_max(`Q1`, `T23G2_L3`) = 50.0 K**, inside **[46, 55] K**, and I make the
sharper directional claim that **the second-order value will be BELOW the
first-order upwind value at comparable resolution** (T23G_F gave 52.81450113 K at
158,720 cells), because upwind's numerical diffusion inflates a peak temperature.
**If the second-order fine value comes out ABOVE 52.81 K, this directional claim
has lost outright.**

**P3 — y+.** I predict max y+ on `fluid_to_housing` of **0.752 / 0.501 / 0.334**
at L1 / L2 / L3, each within ±20 %, and **max y+ < 1.0 on every wall patch of
every level** — the condition no T23G level met.

**P4 — `Q5` will fail again, and this rung says so before running it.** I predict
the housing surface heat flux returns **DIVERGENT or STAGNANT**, for the reason in
§0.3: it is pinned by the imposed source to within ~4e-5 relative. **If `Q5`
returns CONVERGING with p in [1.5, 2.5], P4 has lost**, and that will be recorded
as the positive surprise it is.

**P5 — the similarity repair alone moves p by less than 0.05.** Basis and
arithmetic in §0.2. This is a prediction about a change this rung makes and
cannot isolate; it is registered so that a later single-variable rung can test
it, and it is **not** used to argue that the repair was unnecessary.

**P6 — cost.** Campaign point **993 core-minutes**; I predict the measured actual
lands inside **[700, 1600] core-minutes**, i.e. a ratio actual/predicted in
[0.70, 1.61]. T23G's campaign ratio was 1.132 with a per-level drift from 0.803
to 1.206, so this can lose.

---

## 5. THE GATES

Every gate below is frozen at this file's commit. `CLAUDE.md` rule 5 is supreme
over all of them: **a non-`CONVERGING` triple is `NOT A RESULT` whatever any
number says, and the gate can only turn a PASS or GATE FAIL INTO `NOT A RESULT`,
never the reverse.**

### 5.1 `G-DONE` — the strict completion rule (rule 4), all six clauses, per level

`rc = 0`; an `End` line; **last time == `endTime`**; fields present;
`ExecutionTime` count == `endTime`; and **every field at `endTime` NEWER than the
case's own `0/housing/T`** — the age guard.

**The field tuple, per region, named here so it is not inferred at grading time:**

| region | required at `endTime` |
|---|---|
| `fluid` | `T U p p_rgh alphat nut k omega phi rho` |
| `housing` | `T p` |
| `core` | `T p` |
| `<case>/<endTime>/uniform` | `time` |

**Age-guard referent: `0/housing/T`, touched last at launch**, exactly as
`run_t23g.sh` does it. The launcher **REFUSES** a case where `0` or any time
directory already exists.

Completion is **DELEGATED** to `verification/runs/T-family/T23_runs/mark_done_t23.py`
and called as a subprocess. No completion logic is reimplemented in the
comparator.

### 5.2 `G-BAND` and `G-ORDER`

| gate | quantity | criterion | on failure |
|---|---|---|---|
| **`G-ORDER`** | **`Q4`** | observed order **p ∈ [1.5, 2.5]** from the finest three levels | `GATE FAIL` |
| **`G-BAND`** | `Q1` (ΔT) | fine-level value ∈ **[45.0, 60.0] K** | `GATE FAIL` |
| `G-GCI` | `Q4` | GCI reported at `Fs = 1.25`; **quoted only in the `CONVERGING` state**, never beside a non-monotone triple | — |
| `Q5` | heat flux | **REPORTED, NEVER GATED.** Its triple state and order are printed in full; a `DIVERGENT` reading is pre-registered as the expected outcome (§0.3, P4) and **is not a failure of this rung** | — |

The band `Q4`'s GCI produces is applied to the reported `Q1` and `Q3` maxima
(§3), and the record must say on its face that the band was earned on `Q4` and
transferred.

### 5.3 `G-CONV`, `G-PLATEAU` and `G-RATIO` — iterative convergence, tightened as Sanaa asked

- **`G-CONV`:** at `endTime`, on every level, **`h` ≤ 1e-9** (Sanaa's (a)
  criterion, adopted although (a) is excluded — a criterion she named is not
  dropped because it is already met), and `Uy Uz p_rgh k omega` ≤ 1e-8. `Ux` is
  excluded **by measurement, re-taken per level and never assumed**: the
  comparator computes max\|Ux\|/max\|Uz\| and refuses the exclusion unless it is
  below 1e-12. **No `residualControl` is set** — an early exit would leave the
  last time directory below `endTime` and fail rule 4 clause 3. Convergence is an
  assertion on the log, never a stopping rule.
- **`G-PLATEAU`, on EVERY graded quantity, not only the maxima.** This closes the
  T23G gap where `Q2` had no plateau reading at all (§0.4). Criterion: the
  peak-to-peak spread of the last **11 samples spanning 2,000 iterations** must be
  **≤ 0.005 K** for `Q1 Q2 Q3 Q4 Q6`, and **≤ 0.1 % of the value** for `Q5`.
  Sampling every 200 iterations. **A quantity with no series reads `NOT MEASURED`
  and that is never a pass.**
  *This requires function objects that T23G did not have:* a `volAverage(T)` on
  `core` and on `housing`, and a patch heat-flux integral on `housing_to_fluid`,
  added to the respective `system/<region>/controlDict`. **They are part of the
  registered case build, not a post-hoc addition.**
- **`G-RATIO` — Sanaa's §0 point 2, promoted to a gate.** For every graded
  quantity: the measured iterative change on the finest level (peak-to-peak over
  the last 2,000 iterations) must be **≤ 1/10 of the smallest consecutive
  inter-level difference** for that quantity. **A quantity failing `G-RATIO` is
  `NOT A RESULT`**, because its observed order is then noise rather than
  discretisation. Measured, both sides; neither side is a registered criterion
  standing in for a measurement.

### 5.4 `G-YPLUS` — recorded on every level, gated on the heat-transfer surface

- **RECORDED** on every level and every wall patch: min, avg, max.
- **GATED:** max y+ ≤ **1.0** on **`fluid_to_housing`** on every level.
- **REPORTED, not gated:** `duct_wall`, `centrebody_up`, `centrebody_down`.
  *Reason: they are adiabatic (`zeroGradient` on T) and off the conjugate heat
  path; a y+ excursion there perturbs the bulk flow, not the graded temperatures.
  P3 predicts they clear 1 anyway, and if they do not, that is disclosed, not
  waived.*
- **Instrument, PRIMARY:**
  `chtMultiRegionSimpleFoam -postProcess -func yPlus -region fluid -latestTime`,
  because plain `postProcess -func yPlus` is **measured blind on this family**
  (§0.4) — the compressible turbulence model is not in its registry.
- **Instrument, CROSS-CHECK:** an independent reader computing y+ from `U`, `nut`
  and the polyMesh. **It must plant a known perturbation and read it back, and
  refuse if it cannot see it** (rule 3). The two instruments must agree to within
  2 %; a disagreement is a **REFUSAL**, not an average.
- **A perfect zero from either instrument is REFUSED, never read.**

### 5.5 `G-MESHSIM` — mesh similarity, gated from the BUILT mesh

Measured from each level's `polyMesh` and `checkMesh`, never from the build
script's parameters:

| clause | criterion |
|---|---|
| cell-count ratio | **exactly 2.250000** between consecutive levels, in `fluid`, `housing` and `core` **separately** |
| first-cell wall-normal height ratio | **1.500 ± 0.005** between consecutive levels, on **every** wall patch — the clause T23G would have failed at 1.9512 / 1.9761 against 2.0000 |
| per-cell growth ratio | **≤ 1.25** in every graded band on every level |
| housing wall cells at the coarsest level | **≥ 8** |
| `checkMesh` | "Mesh OK" on all three regions of all three levels; no failure, no warning that is not itemised and justified in the results record |
| geometry invariance | the `blockMeshDict` `vertices` block byte-identical across all three levels |

**A `G-MESHSIM` failure stops the rung before any solver is launched.** It is
cheap, it is checkable at build time, and it is the check T23G did not have.

### 5.6 Planted-zero controls — rule 3

**Every reader plants a known perturbation into the artifact on disk, reads it
back, and REFUSES if it cannot see it.** Six quantities × three levels = **18
controls**, plus the two y+ readers = **20**. `PLANT` is imported from
`scripts/roache_triple.py` and **never redefined**. For area- and
volume-integrated quantities the plant goes into **every** cell or face of the
set, so the expected shift is `mag` and not `mag/N`, and the expected shift is
computed and asserted, not eyeballed.

**A control that cannot be constructed is a REFUSAL. It is never a pass, and it
is never annotated as diagnostic-only.**

---

## 6. WHAT WOULD FALSIFY THIS RUNG'S ENTIRE READING

Recorded now, so that a null result is informative rather than merely
disappointing.

**If the rebuilt ladder — second-order energy convection, wall-resolved at every
level, first-cell spacing similar to 0.5 %, iterative change 10× below the
inter-level differences on every graded quantity — still returns p ≈ 0.375, then
none of Sanaa's (a) through (d) and none of the scheme change is the cause.** The
reading in §1 would be wrong, and the surviving candidate would be **§1.2: the
conjugate interface flux reconstruction**, which is one-sided and formally first
order in the wall-normal cell size on both sides of the interface, and which no
mesh refinement at fixed reconstruction order can lift.

**That would be a finding worth more than a passing gate**, and this record
commits in advance to reporting it as such rather than as a failure to explain.

A second, weaker falsifier: if p rises but lands between 0.5 and 1.5, the honest
reading is that the **scheme change did not take** — that some other first-order
term (`div(phid,p)`, the interface, or the wall treatment) is rate-limiting — and
the next rung is a single-variable scheme sweep, not another mesh level.

---

## 7. THE COMPARATOR, AND WHAT THIS DOCUMENT DOES NOT AUTHORISE

The comparator will be
`verification/runs/T-family/T23G2_runs/analyse_t23g2.py`. **It does not exist
yet.** It will:

- import `roache_triple` and **never** redefine `PLANT`, `FS` or the state names;
- **delegate** rule 4 to `mark_done_t23.py`, calling it as a subprocess;
- plant and read back on every reader (§5.6);
- **refuse (exit 2) rather than degrade** on any missing artifact, unparsable
  block or unconstructable control;
- print the verdict block to stdout, and record its own grading-path shas on the
  artifact's face.

> **This registration authorises NO COMPUTE.** It is a document. The comparator
> must be **written and read by the supervisor as a diff** before any solver is
> launched, and the pre-registration must be **committed** before compute — both
> are the supervisor's personal, undelegable checks under
> `SUPERVISION_CHARTER.md` §3 and `CLAUDE.md` rule 2. The lane that wrote this
> stops here.

**Grading path is fixed at this file's commit.** Before grading, the frozen file
is hashed against the committed blob to prove that the file which ran is the file
that was frozen.

**Amendment status.** No compute has run. Amendments are legal until first
compute and **must state the condition and how it was checked**. The condition is
that `verification/runs/T-family/T23G2_runs/` does not exist; checked
2026-09-01T16:12:36Z by `ls`, which returned *"No such file or directory"*. After
first compute the gates close, and changes land only as dated addenda that cannot
alter a gate, threshold, cap or label; originals are struck, never rewritten.

---

## 8. COST — RULE 12

**Basis.** Calibrated from T23G's own measured actuals, not from a fresh guess:
`T23G_F` ran **145.75 core-min** for 10,000 iterations at 158,720 cells at
`ranks = 1`, giving **0.0145750 core-min/iteration**. T23G's measured superlinear
scaling was `F/M = 5.240` for a 4× cell ratio, i.e. an exponent of
**ln 5.240 / ln 4 = 1.1957** on cell count. Both figures are **MEASURED**, from
`STATUS.T23G_F` and `STATUS.T23G_M`.

**Two ASSUMPTIONS, labelled as such and not as measurements:**
1. `limitedLinear 1` costs **×1.35** per iteration against `upwind` (an extra
   gradient evaluation and a limiter). **ASSUMED.**
2. Iterations to stationarity scale as `h^-1.77`, from T23G's measured
   600 / 1,900 / 6,900 iterations to reach \|ΔT_max\| ≤ 1e-6 K at linear ratio 2
   per step. At r = 1.5 that is ×2.02 per step. **DERIVED from measurement, then
   extrapolated.**

| level | cells | per-iter [core-min] | `endTime` | iterations predicted needed | **POINT [core-min]** | **CAP [core-min]** | timeout [s] | margin |
|---|---|---|---|---|---|---|---|---|
| `T23G2_L1` | 40,320 | 0.0038205 | 9,000 | ~2,850 | **34.4** | **90** | 5,400 | 2.62× |
| `T23G2_L2` | 90,720 | 0.0100795 | 16,000 | ~5,760 | **161.3** | **400** | 24,000 | 2.48× |
| `T23G2_L3` | 204,120 | 0.0265835 | 30,000 | ~11,640 | **797.5** | **1,800** | 108,000 | 2.26× |
| **CAMPAIGN** | | | | | **993.2** | **2,290** | | **2.31×** |

**The timeout IS the cap.** An overrun **STOPS the run**; it does not get a new
budget, and a capped level is not restarted with a bigger number.

**USD — DERIVED, NEVER MEASURED.** The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so any dollar figure from it is
reported-by-owner. At the owner-stated c7a.4xlarge rate of **$0.0513/core-h**:
campaign point 16.55 core-h = **$0.849**; campaign cap 38.17 core-h = **$1.958**.
Under the $25 pre-authorisation. **A blanket authorisation is not a per-item
reading (rule 9), and this row is the per-item costing.**

**HONEST WALL CLOCK.** Three levels, one rank each, launched concurrently on the
three cores budgeted: the campaign finishes when `T23G2_L3` does.
**~13.3 wall-hours at the point estimate, 30 wall-hours at the cap.** The build
and mesh gates add minutes, the comparator under one minute. **There is no
version of this study that returns a defensible p today**, and this record says so
rather than promising one.

**Calibration duty at completion (rule 12).** At every process completion the
pre-registered estimate is compared against the actual incurred cost: actuals in
core-minutes read from each level's own `STATUS.<case>`; the ratio
actual/predicted stated per level and for the campaign; the gap attributed to
contention, waste or misprediction, **with waste named separately and never
absorbed into the ratio**; dollars derived at the recorded rate and labelled
derived. A row lands in **`docs/COST_CALIBRATION.md`** under that file's append
rules and the rule-10 private-index protocol. **A completion report without this
comparison is incomplete.**

---

## 9. WHAT THIS RUNG CANNOT DO, WHATEVER IT RETURNS

- **It cannot move the P column.** A grid triple is code-and-grid convergence
  evidence, not validation against a physical experiment, and there is no primary
  experimental source for this geometry.
- **It cannot transfer to any other point of the T23 map.** Sanaa's §1 authorises
  measuring the band at (305 W, 20 m/s) and **applying it to all sixteen points
  with the transfer disclosed**; the transfer is a disclosed assumption, not a
  measurement, and every displayed point must carry that disclosure.
- **It licenses no display precision on its own.** Whether Act A may print 0.1 °C
  significant figures is decided by the GCI against that quantum, and only in the
  `CONVERGING` state.
- **It sends nothing.** SUBMISSIONS ARE PARKED (`CLAUDE.md` rule 7). Nothing in
  this rung is filed, uploaded, posted or shown outside this box.

---

*Drafted 2026-09-01T16:12Z by a heat-transfer lane, against HEAD
`1b15d0d7503ff1887e1093210e93780d530bde64`. **No solver was launched and nothing
was written into `T23G_runs/` in the course of the diagnosis behind §0 and §1.**
The measurements in §0 and §1 were taken read-only from artifacts already on
disk, by an instrument whose ability to see them is demonstrated by its bit-exact
reproduction of T23G's three graded quantities. **PENDING the supervisor's read.***
