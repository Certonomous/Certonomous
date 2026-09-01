# T25R — 8-cell aviation battery module, **RESOLVED COOLING CHANNELS**, true transient conjugate: PRE-REGISTRATION

**Version 1.0. Written 2026-09-01T03:39Z (`date -u` at write) by a heat-transfer
`lab-lane` for `heat-transfer-supervisor`.**
Repository HEAD at write: `3265f79fe8144a4026d31d5dfbbbb8c7f4c67260`.

**THIS DOCUMENT IS FROZEN BY ITS COMMIT SHA. NO COMPUTE OF ANY KIND HAS RUN FOR
THIS RUNG — NO SOLVER, NO `blockMesh`, NO `checkMesh`, NO FEASIBILITY PROBE.**
Every gate, threshold, cap and label below was fixed before the first byte of
compute, which is the entire evidentiary content of `CLAUDE.md` rule 2.

Verdict vocabulary is fixed by `CLAUDE.md` rule 1 and is used nowhere loosely:
`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`.

---

## 0. WHAT THIS RUNG IS, AND THE FIVE THINGS A READER MUST NOT TAKE FROM IT

### 0.1 What it is

Sanaa's Act C upgrade, ordered verbatim at
`etc/sessions/2026-09-01T0330Z_sanaa_actC_overnight_upgrade.md` (commit
`6ad8f5b7`) and amended at
`etc/sessions/2026-09-01T0335Z_sanaa_actC_no_hard_deadline.md` (commit
`7b9ae703`). The registered real module of directive CASE 4
(`etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md` §4.1–§4.7),
with:

- the **cooling channels RESOLVED as a meshed air region** — inlet velocity and
  temperature imposed, outlet pressure — **coupled to the solid at every channel
  face** by `compressible::turbulentTemperatureRadCoupledMixed`;
- a **true transient conjugate** solve, `chtMultiRegionFoam`, 900 s;
- a **realistic aviation takeoff load derived from a stated C-rate class**, 60 s
  pulse then cruise;
- **two mesh levels**, with **wall layers on both channel faces** and **24 cells
  across each 3 mm channel** at the coarse level;
- **two time steps on the finer mesh**.

### 0.2 THE FIVE THINGS THIS RUNG DOES NOT PRODUCE

1. **NO ROACHE TRIPLE, NO GCI, NO OBSERVED ORDER — spatial or temporal.** Two
   mesh levels are **two points**. Two points cannot measure an observed order
   and cannot yield a GCI. §6.3 registers the mesh pair and the step pair as
   **SENSITIVITY DIFFERENCES** and nothing else. The comparator **computes none,
   quotes none, and emits no `CONVERGING` / `DIVERGENT` / `STAGNANT` /
   `OSCILLATORY` / `EXACT` classification.** `CLAUDE.md` rule 5 is not weakened
   by that: it governs a **grid triple**, and this rung produces none. Precedent
   for printing this on the artifact's own face:
   `verification/runs/T-family/T23_runs/analyse_t23.py:477` and
   `verification/runs/T-family/T24_runs/analyse_t24.py:744`. **This family's most
   repeated failure is smuggling an order out of two points. It does not happen
   here.** A third level is priced at §8.5 and is **NOT REGISTERED**.
2. **NO INHERITED PASS FROM T20.** See §6.1 — the T20 exact gate has **NOT
   discharged**; it is on record as `NOT A RESULT` on its own registered terms.
3. **NO TRANSIENT FLOW DYNAMICS.** §3.3 registers the quasi-steady flow framing
   and what is given up by it.
4. **NO CELL-TO-CELL STREAMWISE ORDERING.** §5.2 — the registered geometry has
   seven **parallel** channels, so no cell is downstream of another. Sanaa's
   acceptance criterion is registered as a **within-cell streamwise** criterion
   and an **outlet-above-inlet** criterion, both of which are the mechanism she
   named. **This is a disclosure, not a substitution**, and it is flagged for
   her ruling.
5. **NO ANISOTROPIC CONDUCTIVITY, NO LAMINAR-VS-SST MODEL-FORM BAND.** Both are
   directive rungs and both are deferred (§9).

### 0.3 THE HONESTY GATE, REGISTERED IN ADVANCE

- **A partially converged transient is NEVER presented as complete.** A run that
  fails any clause of §6.4 is `NOT A RESULT`, and no figure, table or screen
  derived from it may carry a verdict word. There is no "roughly converged".
- **The 0.4 K feasibility run stays off every Act C screen.**
  `verification/runs/T-family/T25_MODULE_runs/T25_MOD_L1` and `_DT025` are
  `FEASIBILITY`, ungated, and are **not** this rung. They are cited in this
  document only for the cost and physics reasoning they paid for.
- Sanaa's amendment (`7b9ae703`, verbatim): *"no its fine. Let it run till it
  converges. If it doesnt do it early enough its fine. I dont have a HARRRD
  deadline. We just need to act asap, but this case running is more important."*
  **Launch speed is the urgency; run length is not.** The 08:00Z clause of
  `6ad8f5b7` is superseded. **The 600 core-min cap is NOT superseded** and rule
  12 stands: an overrun **stops the run** and returns as a report.

---

## 1. THE REGISTERED RUN SET — THREE RUNS, NAMED AND CLOSED

| id | mesh | `deltaT` | steps | purpose |
|---|---|---|---|---|
| `T25R_L1` | L1 | 0.5 s | 1800 | coarse arm of the **mesh-sensitivity pair** |
| `T25R_L2` | L2 | 0.5 s | 1800 | fine arm of the mesh pair; **primary reporting run** |
| `T25R_L2_DT025` | L2 | 0.25 s | 3600 | second arm of the **step-sensitivity pair** |

**Three runs. No fourth.** Anything else is a different rung with its own
pre-registration.

`case_root = /home/ubuntu/Certonomous/verification/runs/T-family/T25R_MODULE_runs/`

---

## 2. GEOMETRY, MESH AND THE TWO LEVELS

### 2.1 Geometry (directive §4.2, and the plenums now built)

| quantity | value | provenance |
|---|---|---|
| n cells | 8 | directive §4.2 |
| cell `Lx` (flow) | 0.100 m | directive §4.2 |
| cell `Ly` (thickness) | 0.030 m | directive §4.2 |
| depth | 1.000 m, **EMPTY** direction | 2-D at OpenFOAM unit depth |
| channel gap | 0.003 m | directive §4.2 |
| n channels | **7**, all **PARALLEL**, flow in `+x` | derived from the row geometry |
| module height | 0.261 m = 8×0.030 + 7×0.003 | DERIVED |
| inlet plenum | 0.050 m upstream of `x=0` | directive §4.2:401 — **BUILT** (the feasibility rung omitted it) |
| exit plenum | 0.100 m downstream of `x=0.100` | directive §4.2:401 — **BUILT** |
| total channel length | 0.250 m | DERIVED |

Cell *i* occupies `y ∈ [(i−1)·0.033, (i−1)·0.033 + 0.030]`; channel *i* is the
3 mm gap above cell *i*. **Cells 1 and 8 have ONE channel face; cells 2–7 have
TWO.** The outer casing faces (`y=0`, `y=0.261`) and the cell streamwise ends
(`x=0`, `x=0.100`) are **adiabatic, declared** (directive §4.2:408).

### 2.2 The mesh levels — refinement ratio **r = 1.5 in both resolved directions**

| | L1 | L2 | L3 *(not registered, §8.5)* |
|---|---|---|---|
| `NX` upstream plenum (50 mm) | 16 | 24 | 36 |
| `NX` cell zone (100 mm) | 40 | 60 | 90 |
| `NX` downstream plenum (100 mm) | 20 | 30 | 45 |
| `NX` total per channel | **76** | **114** | 171 |
| `NY` **across each 3 mm channel** | **24** | **36** | 54 |
| `NY` across each 30 mm cell | **12** | **18** | 27 |
| fluid cells | 12,768 | 28,728 | 64,638 |
| solid cells | 3,840 | 8,640 | 19,440 |
| **total cells** | **16,608** | **37,368** | 84,078 |

**Cell-count ratio L2/L1 = 2.2500 exactly = r² at r = 1.5 in two resolved
directions.** Every `N` is an exact 1.5× of the level below; **no rounding
anywhere**, which is registered here because a non-integer refinement ratio is
the standard way a "grid study" quietly stops being one.

### 2.3 Wall layers on **both** channel faces — the registered sizing

`Re_Dh = U·Dh/ν = 8 × 0.006 / 1.5e-5 = **3200**` (transitional; **DISCLOSED**,
directive §4.4). Blasius `f = 0.316·Re^(−1/4) = 0.042010`;
`τ_w = (f/8)·ρU² = 0.4033 Pa`; `u_τ = √(τ_w/ρ) = 0.5798 m/s`;
`y(y⁺=1) = ν/u_τ = **2.587e-05 m**`, so the **first cell height is
5.175e-05 m** at L1 (cell centre at y⁺ ≈ 1).

Each channel is **symmetrically double-graded** about its mid-plane, 12 cells per
half at L1. The first cell height refines with the level (`5.175e-05 / 1.5` at
L2), so **y⁺ ≈ 1 at L1 and ≈ 0.67 at L2** — both inside the low-Re requirement
of `kOmegaSST` with `*LowRe` wall treatments.

| level | cells per half-channel | first cell (m) | per-cell expansion `r_g` | `simpleGrading` expansion (last/first over the half) |
|---|---|---|---|---|
| L1 | 12 | 5.1750e-05 | 1.14991 | **4.6484** |
| L2 | 18 | 3.4500e-05 | 1.09520 | **4.6925** |
| L3 | 27 | 2.3000e-05 | 1.06151 | 4.7213 |

Every per-cell expansion is **≤ 1.15**, inside the usual ≤ 1.2–1.3 quality
guideline. The solid cells are **uniform** across thickness: the solid Biot
number `Bi = h·L/k = 53.9 × 0.015 / 3 = 0.27` is modest, so no through-thickness
layer is registered, and that is **a choice, disclosed**, not an oversight.

### 2.4 Mesh quality gate (`docs/standards/MESH_STANDARD.md`)

Registered **before** meshing: `checkMesh` on each region of each level must
return **"Mesh OK"** with **zero** failures. Registered thresholds:
**max non-orthogonality < 70**, **max skewness < 4**, **min cell volume > 0**.
A level failing any of these is `NOT A RESULT` for every run on that level, and
the other level is untouched.

### 2.5 Meshing route

One `blockMesh` of the whole domain with `cellZones` `module` (8 blocks) and
`coolant` (21 blocks: 7 channels × 3 streamwise bands), then
**`splitMeshRegions -cellZones -overwrite`**, which creates the coupled
interface patches `module_to_coolant` / `coolant_to_module` on **every internal
face between a cell and a channel**. This is the T24 route
(`verification/runs/T-family/T24_runs/build_t24.py:828`), which is on disk and
has produced a three-region conjugate case at v2606.

**Registered assertion, checked by the builder before any field is written:**
each region carries **exactly one** `*_to_*` interface patch, and the
`module_to_coolant` patch face count equals **the number of channel-facing solid
faces implied by the level's `NX` and the 14 cell/channel contacts**
(7 channels × 2 faces). A mismatch is a **REFUSAL**, not a warning.

---

## 3. NUMERICS — AND WHY THE TIME STEP IS **NOT** DERIVED FROM A COURANT NUMBER

### 3.1 The cost problem, stated before it is resolved

The feasibility rung's own case record states it
(`verification/runs/T-family/T25_MODULE_runs/T25_MOD_L1/CASE.txt:54-56`,
verbatim):

> *"a Courant-limited coupled solve at max Co 1 in a 3 mm gap at 8 m/s needs
> dt ~ 4e-5 s; 900 s of that is ~2e7 steps and is not a tonight-sized job."*

**That is correct and it is binding.** 2e7 steps cannot fit 600 core-min: the cap
is 36,000 core-seconds, which would demand **1.8 µs per multi-region conjugate
step**. No such step exists. **A pre-registration that books a Courant-limited
coupled transient against this cap is disqualified before it starts.**

### 3.2 The resolution, registered explicitly with its justification

Two independent facts, either of which alone settles it:

1. **`chtMultiRegionFoam` is an implicit PIMPLE solver, so `max Co = 1` is a
   CHOICE, not a stability requirement.** The directive's §4.5 wording *"PIMPLE,
   Courant-limited: max Co 1 in the fluid"* is an **accuracy** choice inherited
   from explicit practice, and this rung departs from it **deliberately and on
   the record**. `adjustTimeStep no` is registered (§3.4), so `maxCo` is inert
   and is **not written into `controlDict` at all** — an inert control in a
   frozen dictionary is a future reader's trap.
2. **The channel flow is quasi-steady on the thermal time scale.** The flow time
   scale is the channel residence time `L/U = 0.250 / 8 = **31.25 ms**`. The
   thermal time scale is the lumped `τ = ρ·c_p·V/(h·A)`:
   - interior cell (`A = 0.2 m²/m`, `h = 53.9 W/m²K`): `τ = 2500·1000·3.0e-3 /
     (53.9·0.2)` = **695.7 s**
   - end cell (`A = 0.1 m²/m`): **1391.5 s**

   The two scales differ by a factor of **2.2e4**. With a steady inlet and fixed
   geometry the flow field is established within one residence time and then
   changes only as slowly as the wall temperature does.

### 3.3 THE TIME STEP, DERIVED FROM THE PHYSICS THAT MUST BE RESOLVED

Two constraints, and **not one of them is a Courant number**:

- **(a) The pulse edge at t = 60 s.** The 60 s pulse is the shortest feature the
  answer depends on, and time-of-peak is a registered output. To resolve the
  pulse to **1 % of its own length**: `dt ≤ 0.01 × 60 = **0.6 s**`.
- **(b) The lumped thermal exponential.** Euler-implicit integration of
  `dT/dt = (T_∞−T)/τ` carries an accumulated relative error of order
  `(dt/2τ)`. For **0.1 %** on the smaller (interior) `τ = 695.7 s`:
  `dt ≤ 0.002 × 695.7 = **1.39 s**`.

**(a) binds. The registered step is `deltaT = 0.5 s`** (1800 steps over 900 s),
which is **0.83 % of the pulse length** and `dt/τ = 7.2e-4`. The step-sensitivity
arm halves it to **0.25 s** (3600 steps).

**THE ARITHMETIC IS SHOWN BECAUSE THE DERIVATION IS THE POINT.** At `dt = 0.5 s`
the streamwise Courant number is `U·dt/Δx = 8 × 0.5 / 0.0025 = **1600** at L1`.
That number is **reported, not controlled**, and the reason is registered here:

> **WHAT IS GIVEN UP.** Transient flow dynamics are not resolved. Nothing this
> rung produces says anything about flow start-up, unsteady separation, or any
> time-dependent behaviour of the coolant on a sub-second scale. With a **steady
> inlet velocity, a steady inlet temperature and fixed geometry**, there is no
> such behaviour in the registered configuration to lose.
>
> **WHAT SURVIVES INTACT — every item Sanaa asked for.** The air region is
> meshed and solved. The conjugate coupling is evaluated at **every channel
> face**. Energy transport **in the flow field** — the mechanism that makes the
> coolant hotter downstream and the solid hotter where the coolant is hotter — is
> fully captured, because it is the steady advection–diffusion balance the large
> step converges to within each step. The coolant outlet temperature is a genuine
> solved quantity. The **thermal** transient — the only transient the answer
> depends on — is resolved to 0.83 % of the pulse and 7.2e-4 of `τ`.

### 3.4 Registered numerics

| item | value | note |
|---|---|---|
| solver | `chtMultiRegionFoam` (transient) | directive §4.5 |
| `adjustTimeStep` | **no** | no adaptive stepping on gated runs (directive §4.5, reproducibility) |
| `deltaT` | 0.5 s / 0.25 s | §3.3 |
| `endTime` | 900 s | directive §4.3, §4.5 |
| `writeControl` / `writeInterval` | `runTime` / **5 s** | directive §4.5 → 180 write times + `0` |
| `writePrecision` | **12** | T21 §2.4: default 6 leaves a ~1 mK write quantum, larger than what this rung reports |
| solid `ddtSchemes` | `Euler` | first order in time, **declared** |
| fluid `ddtSchemes` | `Euler` | first order in time, **declared** |
| fluid `divSchemes` | `bounded Gauss upwind` on `U`, `Gauss upwind` on `h,k,omega` | first order in space on the advected scalars, **declared**; upwind is chosen for boundedness at Co ≫ 1 and it is a **registered accuracy cost**, not a hidden one |
| top-level `PIMPLE` | `nOuterCorrectors 5`, `nNonOrthogonalCorrectors 0` | §3.5 |
| fluid `PIMPLE` | `momentumPredictor yes`, `nCorrectors 2` | |
| turbulence | `kOmegaSST`, `*LowRe` wall treatments | directive §4.4; `Re_Dh = 3200` **transitional, DISCLOSED** |
| `g` | **(0 0 0)** | §3.6 |
| radiation | **off**, disclosed | directive is silent; declared omission |
| solid `kappa` | **isotropic 3.0 W/mK** | the directive's **own** stated fallback at §4.2:406-407, taken with the DISCLOSE it demands |
| air | `rho` 1.2, `cp` 1005, `k` 0.026, `mu` 1.8e-5, `rhoConst` | directive-class constants; `Pr` DERIVED as `mu·cp/k` so `k` is exactly 0.026 |
| solid | `rho` 2500, `cp` 1000 | directive §4.2 |

### 3.5 The outer-loop convergence diagnostic — registered as a GATE, in advance

At `Co ≈ 1600` the honest risk is that the outer loop does not converge within
`nOuterCorrectors`. **This is registered as a measured gate, not hoped away.**

**⚠ FIRST, A v2606 FACT ESTABLISHED AT SOURCE BEFORE THIS GATE WAS WRITTEN, AND
IT KILLED THE OBVIOUS FORM OF IT.** `chtMultiRegionFoam` does **not** use
`pimpleControl` for its outer loop. `chtMultiRegionFoam.C:109` is a **plain
`for (int oCorr=0; oCorr<nOuterCorr; ++oCorr)`** over `nOuterCorrectors` read
from `system/fvSolution` by `readPIMPLEControls.H`, and the per-region controls
(`fluid/readFluidMultiRegionPIMPLEControls.H`,
`solid/readSolidMultiRegionPIMPLEControls.H`) read **only** `nCorrectors`,
`nNonOrthogonalCorrectors`, `momentumPredictor` and `frozenFlow`.

**There is NO `residualControl` on this solver's outer loop, and it therefore
emits NO `PIMPLE: converged in` / `PIMPLE: not converged within` line.** The
loop runs **exactly `nOuterCorrectors` sweeps every time step, unconditionally**.
A gate written against `residualControl` would have been **unevaluable**, and —
worse — a comparator counting zero "not converged" lines in a log that can never
contain one would have reported a **planted zero** as a clean pass. That is
`CLAUDE.md` rule 3's failure mode exactly, and it was found by reading the
solver source rather than by assuming the family's usual PIMPLE behaviour.

**THE GATE, IN THE FORM THE SOLVER ACTUALLY SUPPORTS.** The linear solvers print
`Solving for <field>, Initial residual = X` on **every** sweep. The **initial
residual at the LAST outer sweep of a time step** is the residual of the state
entering the final corrector, and is a direct measure of how converged the outer
loop was when the step ended. The comparator splits `log.solve` on `^Time = `
and, per step, takes the **last** initial residual reported for each registered
field:

| region | field | registered threshold on the last-sweep initial residual | provenance |
|---|---|---|---|
| `coolant` | `p_rgh` | **< 1e-6** | directive §4.5 "fluid p/U < 1e-6 per PIMPLE loop" |
| `coolant` | `Ux`, `Uy` | **< 1e-6** | directive §4.5 |
| `coolant` | `h` | **< 1e-6** | directive §4.5, applied to the fluid energy equation |
| `module` | `h` | **< 1e-8** | directive §4.5 "energy residual < 1e-8 (solid)" |

- **THRESHOLD, FROZEN HERE: if more than 5.0 % of the registered step count has
  ANY of those fields above its threshold at the last sweep, that run is
  `NOT A RESULT`.** The count and the percentage are printed beside every number
  the run produced, pass or fail.
- **Startup steps are NOT exempted and NOT excluded from the count.** The 5.0 %
  allowance (90 steps of 1800) is what covers them, and it is registered as an
  allowance rather than applied as a silent exclusion.
- **The comparator REFUSES (exit 2) if `log.solve` carries no `Initial residual`
  lines at all.** A census with no evidence is a planted zero, not a clean run.

**`frozenFlow` IS AVAILABLE AND IS DELIBERATELY NOT USED.** v2606 accepts
`frozenFlow true` in a fluid region's `PIMPLE` dict, which would stop solving
momentum entirely and advance energy alone. That is a **stronger** approximation
than §3.3's quasi-steady framing and it is **not taken**: `frozenFlow` is left at
its default `false` and the **full momentum and turbulence equations are solved
on every outer sweep of every time step**. The flow field in this rung is
solved, not imposed.

### 3.6 `g = (0 0 0)`, and the Richardson check declared **VACUOUS**

`Gr = gβΔT·Dh³/ν² = 9.81 × (1/293) × 8 × (0.006)³ / (1.5e-5)² = **257.2**`;
`Re² = 3200² = 1.024e7`; **`Gr/Re² = 2.51e-05`**. Forced convection dominates by
four and a half orders of magnitude, and `rhoConst` removes buoyancy from the
equations regardless of `g`.

**Following T24's precedent exactly** (`analyse_t24.py` header): with
`g = (0 0 0)` registered, a `Ri < 0.1` criterion is **identically zero by
construction**, cannot fail and cannot inform. It is therefore **NOT reported as
a passing check**. The honest statement is the one registered here: buoyancy is
switched **OFF**, its neglect is a **declared omission**, and whether forced
convection genuinely dominates is established by the `Gr/Re²` arithmetic above
and **not** by any check this rung runs.

---

## 4. THE HEAT LOAD — **C-RATE FIRST, RISE SECOND**

### 4.1 The rule this section obeys

Sanaa wrote *"so the rise is tens of kelvin, not tenths"* and asked for the loss
and its **C-rate class basis** in the assumptions box. **The basis is chosen
first and the rise is whatever results.** Tuning the input until the output
matches a sentence is precisely what pre-registration exists to prevent, and her
instruction to state the basis only means something if the basis came first.
**Nothing in §4.2 was chosen by looking at §4.3.**

### 4.2 THE ASSUMPTIONS BOX — the basis, in the order it was decided

| # | assumption | value | basis |
|---|---|---|---|
| 1 | cell chemistry class | high-**power** aviation pouch (NMC/NCA class) | eVTOL / hybrid-electric propulsion packs trade energy density for power density |
| 2 | **volumetric energy density** | **350 Wh/L** | DECLARED REPRESENTATIVE for a high-power aviation pouch. High-**energy** automotive NMC reaches ~500 Wh/L; a power-optimised aviation cell sits materially below it |
| 3 | cell volume (2-D, per metre depth) | `V = 0.100 × 0.030 × 1.000` = **3.000e-03 m³** | the registered geometry |
| 4 | **energy per cell** | `350 Wh/L × 1000 L/m³ × 3.000e-03 m³` = **1050.0 Wh** | DERIVED from 2 and 3 |
| 5 | **takeoff C-rate** | **5C** | eVTOL takeoff/hover is the peak-power phase; published duty cycles put it at 3C–8C for 60–120 s. 5C is mid-range |
| 6 | takeoff electrical power | `5 × 1050.0` = **5250.0 W** | DERIVED |
| 7 | **heat fraction at 5C** | **4.0 %** | irreversible I²R plus entropic. A good high-power cell dissipates 3–6 % of discharge power at 5C |
| 8 | **`P_takeoff` (heat)** | `0.040 × 5250.0` = **210.00 W per cell** | DERIVED |
| 9 | **`q_takeoff`** | `210.00 / 3.000e-03` = **70,000 W/m³** | DERIVED |
| 10 | **cruise C-rate** | **1C** | sustained cruise draw for a hybrid/eVTOL, 0.8–1.5C |
| 11 | cruise electrical power | **1050.0 W** | DERIVED |
| 12 | **heat fraction at 1C** | **0.8 %** | I²R heat scales as `I²` while power scales as `I`, so the **fraction** scales as `I`: `4.0 % × (1/5)` = 0.8 % |
| 13 | **`P_cruise` (heat)** | `0.008 × 1050.0` = **8.400 W per cell** | DERIVED |
| 14 | **`q_cruise`** | `8.400 / 3.000e-03` = **2,800 W/m³** | DERIVED |
| 15 | pulse | `q_takeoff` for `0 ≤ t < 60 s`; `q_cruise` for `60 ≤ t ≤ 900 s` | directive §4.3 |

`q_takeoff / q_cruise = 25`, not the feasibility rung's 3.75. **The 25× ratio is
the `I²` scaling and is a physical consequence of the C-rate basis, not a
tuning knob.**

The 2-D slab of assumption 3 is **not a real cell**: it is 100 mm × 30 mm in
section at OpenFOAM's unit depth. Every watt above is **per metre of depth** and
the normalisation is stated here so no reader converts it silently.

### 4.3 THE PREDICTION THIS BASIS IMPLIES — REGISTERED BEFORE THE RUN

**The adiabatic bound on the pulse rise, which no amount of cooling can exceed:**

```
ΔT_pulse ≤ q_takeoff · t_pulse / (ρ·c_p) = 70,000 × 60 / (2500 × 1000) = 1.680 K
```

This bound depends on **only** the loss and the cell's own thermal mass. It is
independent of `h`, of the mesh, of the turbulence model and of every other
modelling choice in this document.

**REGISTERED PREDICTION: the rise at the end of the pulse will be of order
1.4–1.7 K, NOT tens of kelvin.** The measured value is the deliverable whatever
it is.

**⚠ WHY "TENS OF KELVIN" IS NOT REACHABLE, AND THIS IS A FINDING, NOT A
FAILURE.** To reach 20 K in 60 s requires `q''' = 20 × 2.5e6 / 60 = 8.33e5 W/m³`
= 2500 W of heat per cell = at a 4 % heat fraction, **62.5 kW of discharge from a
3-litre cell ≈ 60C**. That is not a battery. Even at the aggressive end of the
defensible range — **8C** takeoff and a **6 %** heat fraction — `q''' = 168,000
W/m³` and the adiabatic bound is **4.03 K**. **A 60-second pulse cannot produce
tens of kelvin in a body with `ρc_p = 2.5e6 J/m³K` at any defensible aviation
C-rate.** The physics that prevents it is the same large thermal mass that makes
the case interesting: `τ ≈ 700 s` against a 60 s pulse.

**This is registered as a PRE-COMPUTE DECISION POINT (§8.4).** Amendments before
first compute are legal under rule 2 and must state the condition and how it was
checked. If Sanaa wants a larger rise, the lever is the **pulse duration or the
C-rate**, not the reported number.

### 4.4 The other registered predictions

`ṁ_total = ρ_air·U·A_ch·n_ch = 1.2 × 8 × (0.003 × 1.0) × 7 = **0.20160 kg/s**`

| quantity | value | derivation |
|---|---|---|
| coolant outlet rise, takeoff, **quasi-steady bound** | **8.292 K** | `8 × 210.00 / (0.20160 × 1005)` |
| coolant outlet rise, cruise, quasi-steady bound | **0.3317 K** | `8 × 8.400 / (0.20160 × 1005)` |
| coolant outlet rise **at t = 60 s** (expected) | **≈ 0.8 K** | ~90 % of the pulse energy is **stored** in the solid at 60 s (`ρc_pVΔT×8 ≈ 90 kJ` of `1680 W × 60 s = 100.8 kJ`), so only ~10 % is convected |
| total generated energy over 900 s | **157,248 J** | `8 × 3.0e-3 × (70,000×60 + 2,800×840)` |
| solid streamwise conduction length in 60 s | **8.5 mm** | `√(αt)`, `α = 3/2.5e6 = 1.2e-6 m²/s` — small against 100 mm, so a streamwise gradient survives |

### 4.5 The pulse dictionary — the trap already paid for, kept

The source is `scalarSemiImplicitSource` on the enthalpy field **`h`**, with
`volumeMode specific` and a `Function1 table`. **Three v2606 facts, each already
paid for by this family and each carried forward verbatim:**

1. **The field is `h`, NOT `T`.** The solid energy equation is in enthalpy; an
   `fvOptions` entry on `T` is **never matched and never applied**, and OpenFOAM
   emits one non-fatal warning and then converges cleanly to a **silently
   unheated** solid. That is exactly the failure `CLAUDE.md` rule 3 exists for.
   (`build_t24.py:write_fv_options`, with the v2606 file:line citations.)
2. **`injectionRate` does not exist at v2606**; the accepted forms are `sources`
   (2206+) or the legacy `injectionRateSuSp`.
3. **`volumeMode` is MANDATORY** and decides the units — a missing key is a fatal
   read and the wrong mode is a **silent scale error by exactly the zone
   volume**. `specific` is registered here, so the entered values are in W/m³.

**THE BREAKPOINT PLACEMENT.** `Function1 table` defaults
`interpolationScheme` to `linear`
(v2606 `src/OpenFOAM/primitives/functions/Function1/Table/TableBase.C`), so the
two breakpoints around the pulse edge are the ends of a **ramp**, not a step. The
registered table is:

```
    (  0.000  70000.000000)
    ( 59.999  70000.000000)
    ( 60.000   2800.000000)
    (900.000   2800.000000)
```

The ramp **ends at 60.000**, so `t = 60` samples the **cruise** endpoint exactly,
which is where the directive pins it (`60 ≤ t ≤ 900`). **Registered condition,
checked by the comparator on both arms: no step time on either registered
`deltaT` falls strictly inside the 1 ms ramp `(59.999, 60.000)`.** Step times are
integer multiples of 0.25 s; the nearest are 59.75 and 60.00, both outside.
**A `deltaT` finer than 1 ms would sample the ramp, and that is the condition
under which this placement must be revisited.** The comparator **refuses** if a
run's `deltaT` violates it.

---

## 5. THE ACCEPTANCE CRITERION SANAA NAMED

### 5.1 Her words

> *"Downstream cells must be able to run hotter than upstream ones."* — `6ad8f5b7`

and the supervisor's framing: *that is her acceptance criterion and the whole
point of resolving the channel.*

### 5.2 ⚠ THE GEOMETRY DISCLOSURE — READ THIS BEFORE THE CRITERION

**In the registered geometry there is no cell-to-cell streamwise ordering.** The
8 cells are stacked in the **thickness** direction `y` and separated by **7
parallel channels**; every cell spans the same streamwise extent `x ∈ [0,
0.100]`. **No cell is downstream of another.** (Arithmetic: `8 × 0.030 + 7 ×
0.003 = 0.261 m`, the module height — the separation direction is `y`, so the
channels are in parallel.)

The **mechanism** Sanaa named — coolant heating along the channel, making the
solid hotter where the coolant is hotter — is real, is resolvable, and is exactly
what resolving the channel buys. In this geometry it appears as a **within-cell
streamwise gradient** and as an **outlet above inlet**. The criterion is
registered in that form.

**This is disclosed, not substituted.** If Sanaa intended a **serial** channel
arrangement, that is a **different geometry** and a different rung, and this
document does not pretend otherwise. **Flagged for her ruling; it does not block
launch.**

### 5.3 The registered criterion — **D1, D2, D3**, thresholds frozen here

Let `T_up(i)` = volume-average solid temperature of cell *i* over
`x ∈ [0.000, 0.010]`, and `T_dn(i)` = the same over `x ∈ [0.090, 0.100]`, both at
the **end of the pulse, `t = 60 s`**, and both computed on the **primary run
`T25R_L2`**.

| id | criterion | threshold | verdict on failure |
|---|---|---|---|
| **D1** | `T_dn(i) > T_up(i)` for **every** cell `i = 1..8` | strict inequality, all 8 | **GATE FAIL** |
| **D2** | coolant area-weighted mean `T` at `outlet` > at `inlet`, at every written time `t > 0` | strict inequality, all 180 | **GATE FAIL** |
| **D3** | `min_i [ T_dn(i) − T_up(i) ] > 10 × PLANT` = **1.234e-02 K** | the signal must exceed ten times the registered reader-control perturbation, so it is not write-precision noise | **GATE FAIL** |

`PLANT = 1.234e-03` K, **imported** from `scripts/roache_triple.py` and never
redefined (§7.1).

**D1/D2/D3 are PASS-or-GATE-FAIL, not `NOT A RESULT`**: they ask a physical
question with a pre-registered threshold, and a `no` is an answer. Only §6.4
completion, §2.4 mesh quality, §3.5 outer-loop convergence and §7.1 instrument
admission can make a row `NOT A RESULT`.

---

## 6. THE CHECK SET SANAA ORDERED — EACH REGISTERED IN ADVANCE

### 6.1 ⚠ THE T20 EXACT GATE — CITED HONESTLY, AND IT HAS **NOT** DISCHARGED

Sanaa ordered *"T20 exact gate cited as the machinery proof"*. **The citation is
made and the truth about it is stated in the same breath.**

`docs/campaigns/T-family/T20_PREREGISTRATION.md:21` registers T20 as *"the **V
exact tier of Sanaa's CASE 4**"* — the lumped-capacitance transient control with
internal generation, against the closed-form
`T(t) = T_∞ + (q'''V/hA)(1 − exp(−t/τ))`, banded at 1 % of the analytic rise at
`t = τ, 2τ, 3τ`. It is the **right** machinery proof for this rung.

**IT HAS NOT PASSED.** `verification/runs/T-family/T20_runs/T20_P10_CONDITION_iii_MEASUREMENT.md:9`,
read at source by this lane, states verbatim:

> *"**T20 remains `NOT A RESULT` on its own registered terms**"*

with condition (iii) **PASSED** and condition (c)/(ii) **FAILED** by measurement,
under the `DEAD_LEVER_AUDIT.md` §26.6 deadlock referred to verification at
`docs/campaigns/T-family/T20_P10_REFERRAL_26_6_DEADLOCK.md`. **`T20_LC_P10` has
not run; zero core-minutes of solver compute.**

**REGISTERED CONSEQUENCE, frozen here:**

- The T20 citation is a **POINTER to the registered exact tier**, **NOT a
  discharged machinery proof**.
- **T25R INHERITS NO `PASS` FROM T20.** No output of this rung may be described
  as resting on a verified transient-machinery proof.
- The comparator **prints this status on its own face**, in the header, on every
  invocation, so that no downstream reader can pick up the citation without the
  caveat attached to it.
- This does **not** block T25R. T25R's own energy-conservation gate (§6.2) is an
  independent, self-contained check on the transient machinery, and it is
  reported as **the** machinery evidence this rung actually carries.

### 6.2 Cumulative energy conservation over 900 s — **GATE**

```
E_gen  =  ΔE_solid  +  ΔE_fluid  +  ∫₀⁹⁰⁰ ṁ·c_p·(T_out − T_in) dt   +  R
```

- `E_gen = 157,248 J` (§4.4), computed from the **registered** `q'''(t)` and the
  volume **OpenFOAM itself measures** and prints (`cellSetOption.C:166-168`) —
  never a hand-typed volume.
- `ΔE_solid = Σ_cells ρ·c_p·V_cell·(T̄ − 293)` at `t = 900`, from the written
  fields.
- `ΔE_fluid` likewise over the coolant region.
- The convected term is accumulated from `surfaceFieldValue` `weightedSum` of
  `phi·T` on `inlet` and `outlet`, written **every time step**. `phi` is the mass
  flux and is **negative on an inflow face**, so the two rows **add**.

**THRESHOLD, FROZEN: `|R| / E_gen ≤ 2.0 %`** (directive §4.5). Outside ⇒
**`GATE FAIL`**, with `R`, `E_gen` and all four terms printed. The feasibility
rung measured 0.146 % at `dt` 0.5 on a solid-only configuration, so 2 % is a real
but attainable band.

**PLANTED CONTROL ON THE BALANCE INSTRUMENT (directive §4.6, "planted +10 %
source control"):** the comparator re-computes `E_gen` from the fvOptions table
with the takeoff level scaled by **+10 %** and asserts the residual `R` moves by
`0.10 × 4.2e6 × 0.024` = **10,080 J ± 1e-6 J**. **An instrument that does not
move when the source moves is refused (exit 2), not reported.**

### 6.3 Step-sensitivity and mesh-sensitivity panels — **REPORT, NOT GATE**

Registered as **DIFFERENCES**, with the words that must appear beside them:

- **Step pair**: `T25R_L2` (`dt` 0.5) vs `T25R_L2_DT025` (`dt` 0.25), same mesh.
  Reported: signed and percentage difference in peak cell temperature, time of
  peak, end-of-pulse temperature, module spread and outlet temperature.
- **Mesh pair**: `T25R_L1` vs `T25R_L2`, same `dt`. Same quantity list.

**NO observed order. NO GCI. NO Roache classification.** Two points do not
measure an order (§0.2 clause 1). The comparator prints, verbatim, on both
panels: *"TWO POINTS. NO LADDER IS REGISTERED. No observed order, no GCI and no
Roache classification is computed, quoted or quotable from this artifact."*

**Registered interpretive limit:** a small difference between two points is
**consistent with** convergence and is **not evidence of** it. The report says
so, in those words.

### 6.4 STRICT COMPLETION — `CLAUDE.md` rule 4, delegated and never reimplemented

Completion is decided by
**`verification/runs/T-family/T25R_MODULE_runs/mark_done_t25R.py`**, which is
**called** by the comparator and **never reimplemented inside it**. A run without
a `DONE.<case>` marker from that instrument is `NOT A RESULT` and its numbers are
not printed as results.

**⚠ THIS RUNG'S FIELD TUPLE — STATED EXPLICITLY, BECAUSE IT NOW HAS A FLUID
REGION AND THE SOLID-ONLY TUPLE DOES NOT APPLY.** The feasibility rung's
`{T, p}` on one region is **wrong for T25R**.

| conjunct | T25R's registered form |
|---|---|
| 1. `rc = 0` | **DERIVED FROM `log.solve`** — exactly one `End`, zero `FOAM FATAL`, last time == `endTime`. `launcher_rc` is **NEVER** accepted as `rc`, **even at 0**: `setsid timeout cmd` exits 0 for every outcome (T24 §3.5a; the queue runner is known to clobber `STATUS`) |
| 2. `End` line | exactly one |
| 3. last time == `endTime` | `900` exactly, to 1e-9 |
| 4. **fields present, PER REGION** | `<endTime>/module/` : **`T`, `p`** — a solid region of `chtMultiRegionFoam` requires `p`.<br>`<endTime>/coolant/` : **`T`, `U`, `p`, `p_rgh`, `alphat`, `nut`, `k`, `omega`** |
| 5. `ExecutionTime` count | **`T25R_L1` 1800, `T25R_L2` 1800, `T25R_L2_DT025` 3600.** Rule 4's *"`ExecutionTime` count == `endTime`"* is a **SHORTHAND literally true only at `deltaT = 1`**. The operative test is **count == REGISTERED STEP COUNT** — a **step-count identity, not a time-value identity**. Precedent verified inside this family: `T20_LC_c`, `endTime` 4500 at `deltaT` 6, 750 registered steps, `ExecutionTime` count 750 (`docs/LAB_STATE.md:11221`). On an adaptive or non-unit step the substantive form is **one `ExecutionTime` per advanced step with no truncated tail**; this rung is **non-adaptive** (`adjustTimeStep no`), so the count is exact and any shortfall is a **truncated tail** and is `NOT DONE` |
| 6. **the age guard** | **`0/module/T`**, not `0/T` — a multi-region case has no `0/T`. The launcher `touch`es `0/module/T` **LAST**, on the line immediately before the start block, so that file dates the run allowed to produce the answer. **Every** field named in conjunct 4, in **both** regions, must be **strictly newer** than it |
| 0. guard | the launcher **refuses** a case where `0` or any time directory already exists |

`STATUS.<case>` lives **inside** the case directory. An **absent** `STATUS` is a
**REFUSAL (exit 2)**, never inferred from an `End` line (K0d L1).
**L-342 field classes:** PHYSICS-CRITICAL = the six conjuncts above.
INFRASTRUCTURE = `wall_s`, `ranks`, `core_min`, `cap_core_min`, `timeout_s`,
`capped`, `solver` — an absent infrastructure field is **NOT MEASURED** and is
**reported**; it never voids a run (Sanaa's universal rule 2026-08-26:
**bookkeeping never voids physics**).

**THE STALE-MARKER RE-CHECK.** A `DONE.<case>` marker found on disk is **not**
accepted on sight: the instrument **re-runs every conjunct** and **removes** a
marker whose case no longer satisfies them. A marker is a cache, never evidence.

**THE CAP IS A NAMED OUTCOME.** `capped=yes` or `rc=124` ⇒ that row is
`NOT A RESULT`, named as a **cap stop** under rule 12, and it **does not get a
new budget**. The other rows are untouched, and a cap is reported as its own
finding, never folded into the cost ratio.

---

## 7. INSTRUMENT ADMISSION — THE PLANTED-PERTURBATION CONTROLS

### 7.1 Every reader, no exceptions — the nine clauses

`CLAUDE.md` rule 3: **a zero from a reader not shown able to see a non-zero is
not evidence.** The pattern is
`verification/runs/T-family/T24_runs/analyse_t24.py:459-530`, followed clause for
clause:

1. **COPY FIRST.** The control copies the case into `tempfile.mkdtemp()` and
   **refuses** if the scratch path resolves **inside** the case
   (`realpath(scratch) == realpath(case)` or starts with `realpath(case)+os.sep`).
   The case is **never written to**.
2. **NEGATIVE ARM at bitwise `0.0`, with NO tolerance.** Two reads of identical
   bytes must differ by **exactly** `0.0`. A noisy reader is **refused**.
3. **POSITIVE ARM: a MEASURED magnitude ladder**, epsilon-free.
   `LADDER = (10.0, 1.0, 1e-1, 1e-2, PLANT, 1e-3, 1e-4, 1e-5, 1e-6)`. `floor` is
   the smallest magnitude with a **strictly non-zero** read.
4. **REFUSE IF BLIND.** If no magnitude produces a non-zero read, the reader
   cannot certify anything and the control **refuses (exit 2)**.
5. **THE ONLY SIZING TOLERANCE, AND IT IS RELATIVE:**
   **`got >= PLANT * (1.0 - 1e-9)`**. The absolute form
   `seen >= PLANT - 1e-15` of `analyse_t3.py:327` is **EXPRESSLY NOT ADOPTED**:
   an absolute epsilon at this magnitude is decided by rounding wiggle rather
   than by whether the reader saw the plant.
6. **`PLANT` IS IMPORTED, NEVER REDEFINED.** `from scripts/roache_triple.py`,
   `PLANT = 1.234e-03`. The comparator asserts `PLANT == RT.PLANT` and refuses
   otherwise.
7. **Plants are written BY LINE INDEX**, inside a window taken from the field's
   **own header**. Nothing is located by value. A patch plant writes **every**
   face of the patch so the expected shift is **exactly** `mag`, never `mag/N`.
   The count planted is recorded and asserted.
8. **The case bytes are compared before and after** and the scratch tree is
   removed in a `finally`.
9. **`__pycache__` is cleared** before the control runs (stale bytecode inverts
   mutation tests).

**A REFUSAL ON ANY READER MAKES THE WHOLE RUNG `NOT A RESULT`.**

### 7.2 The registered readers — every one carries a control

| reader | what it reads | plant, and why it is shaped that way |
|---|---|---|
| `read_cell_T` | per-cell volume-average solid `T` | **every mesh cell of the hottest of the 8 module cells** |
| `read_spread` | `T_max − T_min` across the 8 cells | the same — planting *all* cells would move the spread by **zero** |
| `read_updown` | `T_up(i)` / `T_dn(i)` for D1/D3 | **every** `internalField` cell |
| `read_outlet_T` | area-weighted mean `T` on `coolant` `outlet` | **every face** of the `outlet` patch of `<t>/coolant/T` |
| `read_inlet_T` | area-weighted mean `T` on `coolant` `inlet` | every face of the `inlet` patch |
| `read_energy` | the four terms of §6.2 | **the +10 % source control of §6.2** |

**⚠ WHY THE SOLID PLANTS COVER A WHOLE MODULE CELL, AND WHY THIS IS NOT A
LOOSENING.** Every solid reader above returns a **volume average** over one
module cell. Planting a **single mesh cell** would move that average by
`mag · V_i/V_cell` — i.e. by **`mag/N`**, with `N` = 480 at L1 — and the control
would then fail clause 5 for a reason that has nothing to do with whether the
reader can see the plant. Planting the **whole module cell** makes the expected
shift **exactly `mag`**, which is the identical correction
`analyse_t24.py:443` makes for its patch plant. The module cell is chosen **by
its volume-average rank**, never by locating a value in the file (clause 7).
**The `mag/N` failure mode is driven as a LIVE NEGATIVE ARM of the comparator's
selftest**: a single-cell plant under a volume-average reader must **REFUSE**,
and it does.

---

## 8. COST — `CLAUDE.md` RULE 12

### 8.1 The rate, and the warning it comes with

**MEASURED ANCHOR:** `verification/runs/T-family/T24_runs/T24_P080_U10/log.solve`
— `chtMultiRegionSimpleFoam`, **39,680 cells** (35,200 fluid + 1,120 + 3,360
solid), **10,000 outer iterations**, `ExecutionTime = 2251.46 s`, `nProcs : 1`
(read from the log; `ranks = 1`).

> **rate = 2251.46 / (10,000 × 39,680) = 5.674042e-06 core-s per cell per outer
> iteration**

**⚠ THIS RATE IS BORROWED ACROSS BOTH A MESH JUMP AND A SOLVER/PHYSICS CHANGE,
AND THAT IS NAMED, NOT HIDDEN.** T24 is **steady** SIMPLE on a **three-region**
mesh 1.1×–2.3× the size of these; T25R is **transient** PIMPLE on **two**
regions with a time derivative in every equation and a `Function1` source. **This
family has already missed by 31.4 % borrowing a cell-rate across a mesh jump
alone.** T25R crosses **two** boundaries at once.

**The conversion, stated as the assumption it is:** one PIMPLE time step is
priced at **5 SIMPLE-equivalent outer iterations** (`nOuterCorrectors 5`). The
dominant misprediction risk is that a transient outer corrector — which also
solves the ddt terms and re-couples both regions — costs materially more than a
steady one.

**THE MISPREDICTION IS SIZED AT ×3, NOT ×1.314.** The hard cap on every run is
**three times its POINT**, because two independent error sources compound: the
measured 31.4 % mesh-jump miss, and an unmeasured solver/physics conversion that
could plausibly be 2× on its own.

### 8.2 The registered cost table

| run | cells | steps | **POINT (core-min)** | **HARD CAP (core-min)** | `timeout_s` |
|---|---|---|---|---|---|
| `T25R_L1` | 16,608 | 1,800 | **14.14** | **42.41** | **2545** |
| `T25R_L2` | 37,368 | 1,800 | **31.80** | **95.41** | **5725** |
| `T25R_L2_DT025` | 37,368 | 3,600 | **63.61** | **190.82** | **11450** |
| **build compute** (§8.3) | — | — | **2.00** | **2.00** | 600 |
| **TOTAL** | | | **111.55** | **330.64** | |

**Against the 600 core-min cap: headroom 269.36 core-min at hard cap = 44.9 %.**

**Dollars, DERIVED and NOT MEASURED.** At **$0.0513/core-h**, c7a.4xlarge,
**owner-stated 2026-08-21/22** and corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`. The box **cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5), so **`cost_basis = REPORTED-BY-OWNER, NOT
MEASURED`**:
POINT `111.55/60 × $0.0513` = **$0.0954**; HARD CAP `330.64/60 × $0.0513` =
**$0.2827**. Both **under $25** and inside the 2026-08-21 blanket — **and still
costed here, because a blanket is not a per-item read** (rule 9).

**RULE 12 IS NOT DECORATION HERE: an overrun STOPS the run.** `timeout_s` is the
hard cap in wall-seconds at `ranks = 1`. A `timeout` kill leaves no `End` line
and a last time below `endTime`, so §6.4 conjuncts 1, 2 and 3 all fail and the
row is `NOT A RESULT` **by construction**. It **does not get a new budget** and
it is reported as a **cap stop**, never absorbed.

### 8.3 Build compute is COSTED so it cannot be taken as a free action

`blockMesh` + `splitMeshRegions` + `checkMesh` × 2 levels. Anchor: the
feasibility rung measured `blockMesh` + `checkMesh` at **0.04 wall s** on 960
cells (`T25_MESH_FACTS.json`, `live_mesh_timing_measured_this_turn`). At 37,368
cells with `splitMeshRegions` added, **2.00 core-min POINT and HARD CAP** is
generous by more than an order of magnitude, and it is registered rather than
treated as costless. **Build compute is compute:** `VERIFICATION_CHARTER.md`
§2d.2 closes gates at **first compute, feasibility and build compute included**,
which is why nothing has been meshed (§10).

### 8.4 Wall-clock estimate

| | sequential | 3 concurrent, `ranks = 1` each |
|---|---|---|
| **POINT** | 111.55 min = **1.86 h** | max = 63.61 min = **1.06 h** |
| **HARD CAP** | 330.64 min = **5.51 h** | max = 190.82 min = **3.18 h** |

Sanaa's *"let it run till it converges"* is satisfied with room in every branch.
**Registered launch order: `T25R_L1` first**, because the directive itself says
*"calibrate on L1 first"* (§4.7) and because an L1 actual gives a **measured,
same-solver, same-physics** rate for the calibration row before the two larger
runs are half done. **The registered caps do NOT move on that measurement** —
gates close at first compute.

### 8.5 A THIRD MESH LEVEL — PRICED, AND **NOT REGISTERED**

The supervisor asked that a third level be priced if it fits. **It is priced
here and the honest answer is that it does not fit comfortably.**

| | L3 |
|---|---|
| cells | 84,078 (exactly 2.25 × L2) |
| POINT | **71.56 core-min** |
| HARD CAP at ×3 | **214.68 core-min** |
| `timeout_s` | 12881 |
| **four-run total at HARD CAP** | **545.82 core-min** |
| **headroom against 600** | **54.18 core-min = 9.0 %** |

**RECOMMENDATION, and it is the lab's, not Sanaa's:** do **not** add L3 to this
rung. A ×3 contingency that turns out to be ×3.3 blows the cap, and a cap stop on
L3 would cost the compute and buy nothing. The right way to a genuine Roache
triple is a **separate later rung priced off T25R's own MEASURED rate**, where a
×1.5 contingency is defensible and the whole triple fits easily.

**If the supervisor accepts L3 anyway, it must be accepted at the diff read,
BEFORE ANY COMPUTE**, as a pre-compute amendment under rule 2 stating the
condition and how it was checked. **After first compute it cannot be added**, and
a two-level run may not be retro-fitted with a third to manufacture an order.

**IF AND ONLY IF L3 IS ACCEPTED** does §6.3 change: the mesh set becomes a triple
and the comparator computes the Roache classification, observed order and GCI at
`Fs = 1.25` under `CLAUDE.md` rule 5, quoting **no** GCI where the three values
are not monotone. **In the registered two-level configuration it computes none.**

### 8.6 Estimate-versus-actual calibration — rule 12, mandatory

At **every process completion** — each run graded, and the rung closed — the
pre-registered estimate is compared with the actual. Actuals in **core-minutes
from `log.solve` `ExecutionTime` × ranks ÷ 60**; dollars **derived at
$0.0513/core-h and labelled derived-not-measured**. Each row states the
**ratio actual/predicted** and **attributes the gap** — contention, waste or
misprediction — with **waste named separately and never absorbed into the
ratio**. Rows land in **`docs/COST_CALIBRATION.md`** under that file's append
rules and the rule-10 private-index protocol. **A completion report without this
comparison is incomplete.**

---

## 9. OUTPUTS — exactly what Sanaa ordered

**Fields** written at `t = 0, 30, 60, 120, 300, 900 s` (all are multiples of the
5 s write interval, so all exist without a special write control).

| # | output | gradeable? |
|---|---|---|
| 1 | solid `T` fields at t = 0, 30, 60, 120, 300, 900 s | `FEASIBILITY` (illustrative) |
| 2 | **all-8-cell** temperature histories, **pulse shaded** 0–60 s | `FEASIBILITY` |
| 3 | module spread `T_max − T_min` vs time | `FEASIBILITY` |
| 4 | **coolant outlet temperature vs time — genuinely defined, and the point of the upgrade** | **GRADED** by D2 (§5.3) |
| 5 | per-cell table: **peak `T`, time of peak, `T` at end of pulse (t = 60 s), time to settle** (`dT/dt < 0.01 K/s`, directive §4.6) | `FEASIBILITY` for the values; the **within-cell streamwise** column is **GRADED** by D1/D3 |
| 6 | energy-conservation ledger, four terms + residual | **GRADED** by §6.2 |
| 7 | step-sensitivity panel | **REPORT ONLY**, no order, no GCI |
| 8 | mesh-sensitivity panel | **REPORT ONLY**, no order, no GCI |
| 9 | outer-loop convergence census | **GATE** by §3.5 |

**PER-OUTPUT LABELLING IS MANDATORY.** Every number this rung emits carries
either a **GRADED** verdict from the fixed vocabulary or the tag
**`FEASIBILITY`** meaning *not gradeable, no gate exists for it, and none may be
invented after the fact*. **A number with neither label is a defect in the
report.**

**DEFERRED, and named so no reader assumes them:** anisotropic solid conductivity
(directive §4.2 escalation rung); the laminar-vs-SST model-form band (directive
§4.6); the SOC-dependent source; 3-D; the liquid cold plate; cell-to-cell
conduction paths.

---

## 10. THE ORDER OF OPERATIONS — REGISTERED, AND NOT NEGOTIABLE

`SUPERVISION_CHARTER.md` §3 reserves to the supervisor **personally**: the
confirmation that the pre-registration is **committed** before compute, and the
**diff read** of the measurement script. Neither may be delegated, and a relayed
check is a summary, not a check.

```
  1. COMMIT this document, the comparator, the completion instrument
     and the builder.                                    <-- this lane, DONE at §11
  2. THE SUPERVISOR'S PERSONAL DIFF READ.                <-- STOP. Not this lane.
  3. mesh  (blockMesh, splitMeshRegions, checkMesh)      <-- only after 2
  4. launch                                              <-- only after 3
```

**NOTHING HAS BEEN MESHED AND NOTHING HAS BEEN LAUNCHED.** `VERIFICATION_CHARTER.md`
§2d.2 closes gates at **first compute — feasibility and build compute included**
— so meshing before the diff read would close the gates of a comparator the
supervisor has not yet accepted. **The builder is written and has NEVER BEEN
EXECUTED.** Its `foam()` driver **refuses by name** to launch any solver.

**Before first compute, amendments are legal** and **must state the condition and
how it was checked**. Two are already open and both must be decided at step 2:

- **§4.3 — the load.** The registered 5C / 4 % basis implies a pulse rise of
  order 1.5 K, and *"tens of kelvin"* is not reachable from a 60 s pulse at any
  defensible aviation C-rate. Condition, checked: **no run directory exists under
  `verification/runs/T-family/T25R_MODULE_runs/`** — verified by this lane at
  write; the directory holds only the four instruments.
- **§8.5 — L3.** Priced; **not registered**; lab recommends **no**.

---

## 11. FREEZE

| artifact | path |
|---|---|
| this pre-registration | `docs/campaigns/T-family/T25R_PREREGISTRATION.md` |
| comparator | `verification/runs/T-family/T25R_MODULE_runs/analyse_t25R.py` |
| completion instrument | `verification/runs/T-family/T25R_MODULE_runs/mark_done_t25R.py` |
| builder (**never executed**) | `verification/runs/T-family/T25R_MODULE_runs/build_t25R.py` |
| launcher (**never executed**) | `verification/runs/T-family/T25R_MODULE_runs/run_one_t25R.sh` |

**The grading path is fixed at this commit.** Before grading, the comparator
hashes the frozen pre-registration against the committed blob and **refuses** if
they differ — verifying that *the frozen file is the file that ran*
(`CLAUDE.md` rule 2; `scripts/check_comparator_freeze.py`).

**Frozen files are never edited.** Any departure lands as a **dated amendment
appended at the foot**, with a version bump and the assertion `lines whose number
changed above this section: 0`.

**SUBMISSIONS PARKED** (rule 7). **Permanently private** (rule 8). Nothing here
is sent, filed, uploaded or registered anywhere outside this box.

---

## 12. WHAT THIS LANE COULD NOT VERIFY

Stated plainly, because an honest gap is worth more than a confident guess.

1. **The builder has never run.** Not one line of `build_t25R.py` has been
   executed — by design (§10). Its dictionaries are patterned on
   `build_t24.py` (a three-region conjugate case that meshed and solved at v2606)
   and on the feasibility rung's `fvOptions` (which ran, `rc=0`), but **the
   T25R blockMeshDict, the 29-block zone layout, the `splitMeshRegions` interface
   naming and every `0.orig` field are UNTESTED**. The first `blockMesh` may fail.
   **That is a build risk, not a physics risk, and it is the largest single
   threat to launch speed.**
2. **The 5.674e-06 core-s/cell/outer rate is T24's, not T25R's.** It is measured,
   but on a different solver, different physics and a different mesh (§8.1). The
   ×3 hard cap is a **judgement**, not a measurement.
3. **`nOuterCorrectors 5` is a choice, not a measurement.** Whether PIMPLE meets
   `residualControl` inside 5 outer iterations at `Co ≈ 1600` is **unknown until
   the run**. §3.5 turns that unknown into a **pre-registered gate** rather than a
   surprise, but it may well be the clause that fires.
4. **`h = 53.9 W/m²K` is Dittus–Boelter, declared-representative and NOT
   measured.** It is used **only** for the `τ` arithmetic of §3.2, the Biot
   estimate of §2.3 and the §4.4 predictions. **It is imposed nowhere in the
   solve** — the whole point of this rung is that the channel resolves its own
   heat transfer coefficient.
5. **The ~795 s lumped `τ` quoted to this lane in its brief could not be located
   in any artifact.** This document uses **695.7 s (interior)** and **1391.5 s
   (end)**, both re-derived here from `ρ c_p V/(hA)` with every input shown. If
   795 s exists somewhere with a different derivation, this document does not
   depend on it.
6. **Sanaa's "downstream cells hotter than upstream" cannot be tested cell-to-cell
   in the registered geometry** (§5.2). The registered D1/D2/D3 test the
   mechanism she named; whether that is what she meant is **hers to rule**.
7. **The T20 exact gate has not discharged** (§6.1). Read at source, but the
   §26.6 deadlock is a live referral in another team's territory and this lane
   did not adjudicate it.

<!-- END OF T25R PRE-REGISTRATION v1.0 -->
