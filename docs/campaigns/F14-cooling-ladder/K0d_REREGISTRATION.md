# K0d. Turbulent mixed convection, Blay–Mergui–Niculae ventilated cavity: RE-REGISTRATION (template form)

**THIS DOCUMENT SUPERSEDES `docs/campaigns/F14-cooling-ladder/K0d_PREREGISTRATION.md`
(blob `e629f5c492a36772cf4ab0593440fd9666a119fe`, 3 759 lines, version 1.5 with
`AMENDMENT` 1–5).**

**WHY IT SUPERSEDES RATHER THAN AMENDS, in the supervisor's own terms:
TWO FROZEN AMENDMENTS RECONCILED ONE CONTRADICTION TWO DIFFERENT WAYS, SO THE
DOCUMENT DID NOT DETERMINE WHAT PHYSICS WAS BEING SIMULATED.** `AMENDMENT 1`
§A1.2 (2026-08-24) reconciled a 2.7539 % inconsistency in `Ra` by taking
`ν = 1.569e-5 m²/s`; `AMENDMENT 5` §A5.7 (2026-08-25) reconciled the **same**
inconsistency by superseding `β` to `3.26577e-3 K⁻¹` at `ν = 1.55e-5`. Both are
frozen, both are pre-compute, and they are mutually exclusive. A sixth amendment
could not repair that: a contradiction between two repairs is not a gap.

**SUPERSEDED, NOT DELETED.** `K0d_PREREGISTRATION.md` and all five of its
amendments **remain on disk byte-unchanged** (standing rule 6). Nothing in them
is edited, withdrawn or rewritten by this document. This document adopts named
sections of it by citation and states, section by section, which it does not.

**RESOLUTION CLASS: `[lab-attributed]`** — Sanaa's desk-item disposal rule
(`LAB_STATE.md:1880`): the heat-transfer supervisor's recommendation in
`K0d_FIRE_RULING_2026-08-25.md` §3 clause 3 was not ruled on within one day and
is therefore **ADOPTED and recorded `[lab-attributed]`**. Retiring a frozen
pre-registration was escalated, not taken unilaterally.

**Registered 2026-08-25, BEFORE ANY K0d COMPUTE.** Zero core-minutes have ever
been spent against K0d. `verification/runs/F14-cooling-ladder/K0d_runs/` does not
exist at this write, and this document does not create it. **This document
authorises no solve.** Standard-form registration under Sanaa's 2026-08-25
template directive; the exemplar is
`docs/campaigns/T-family/T1b_L4_EXT2_PREREGISTRATION.md`.

---

## 0. THIS DOCUMENT STATES ITS OWN CEILING, ON ITS FACE

**AS REGISTERED, THIS RUNG CANNOT REACH A GRADED VERDICT.** The primary —
Blay, D., Mergui, S. and Niculae, C. (1992) — is **`NOT OBTAINED`**. Every graded
row of the superseded §7.3 is `BLOCKED` by construction under its §7.4 order 4
until a reference addendum arms §7.6, and the rung's tally stands at **0 of 10**.
What firing this rung produces is the **solves and the physics-stage
instruments** — convergence, achieved `y⁺`, the five guards, the Roache triples,
the discrimination control — **not a gate.** Nobody may later read a completed
run of this rung as a graded result.

---

## 1. CASE

Blay–Mergui–Niculae ventilated cavity: an **isothermal supply jet entering a
cavity against a buoyant floor plume** — the aisle physics the DC-cooling spine
needs. 2D, `x ∈ [0, 1.04]`, `y ∈ [0, 1.04]`; inlet patch `x = 0,
y ∈ [1.022, 1.040]` (`h_in = 0.018 m`); outlet patch `x = 1.04, y ∈ [0, 0.024]`
(`h_out = 0.024 m`). Solver **`buoyantBoussinesqSimpleFoam`**, OpenFOAM v2606
stock, steady, `g = (0, −9.81, 0)`.

**Geometry and boundary conditions are ADOPTED UNCHANGED from the superseded
document §§3.1–3.3** — inlet `u = 0.57 m/s`, `v = 0`, `θ_in = 15 °C`; floor
isothermal **35.0 °C**; ceiling and both vertical walls isothermal 15 °C, no
slip; outlet zero-gradient on `U`, `T` and every turbulent variable; inlet
`k = 1.25e-3 m²/s²`, `ε = 5.76e-3 m²/s³`; `Pr_t = 0.85` everywhere, never tuned.
**`ΔT` is fixed at exactly 20.0 K** and the primary's arbitration cannot widen it.
The `fvSchemes`, `fvSolution`, per-patch boundary types, `ε → ω` conversion and
inlet `omega` values registered in `AMENDMENT 4` §§A4.2–A4.3 and `AMENDMENT 5`
§§A5.2–A5.5 are **adopted unchanged**; this document reopens none of them.

### 1.1 THE FLUID STATE, REGISTERED ONCE AND CONSISTENTLY — the whole point of this document

| quantity | **registered value** | basis |
| --- | ---: | --- |
| `T_ref` | **298.00 K** | lab choice; see 1.2 |
| `β` | **1/298 = 3.3557047e-03 K⁻¹** | **`β = 1/T_ref` BY IDENTITY for a Boussinesq air model** |
| `ν` | **1.569e-5 m²/s** | lab choice; air at 299.86 K by the Sutherland correlation |
| `Pr` | **0.71** | lab choice, standard air |
| `α = ν/Pr` | 2.209859e-05 m²/s | derived |
| `Pr_t` | 0.85, never tuned | lab standing value |

**`β` IS NOT A FREE PARAMETER IN A BOUSSINESQ AIR MODEL — IT IS `1/T_ref` BY
IDENTITY.** That identity is why the superseded `AMENDMENT 5` reconciliation is
rejected: its `β = 3.26577e-3` is `1/306.21`, so it silently redefines the
reference temperature to **306.21 K (33.06 °C)** while `TRef` stood registered at
298.15 K — an **8.06 K internal contradiction inside the one coefficient
Boussinesq validity rests on.** The same reading in measured internal spreads:
`β`-temperature against `ν`-temperature is **1.86 K** for the registered pair and
**8.40 K** for the rejected one. `ν`, by contrast, **is** a genuinely free
material property: 1.55e-5 and 1.569e-5 are air at 297.81 K and 299.86 K
respectively, both room air, and choosing between them is a legitimate
registration.

Fluid-state temperatures above are computed from the Sutherland correlation with
constants **read off this box** — `As = 1.4792e-06`, `Ts = 116` at
`/usr/lib/openfoam/openfoam2606/tutorials/heatTransfer/overBuoyantPimpleDyMFoam/movingBox/constant/thermophysicalProperties:41-42`
— with `ρ = p/(R T)`, `p = 101 325 Pa`, `R = 287.058 J/kg·K`.

### 1.2 `T_ref = 298.00 K`, AND THE ONE PLACE THIS DOCUMENT HAD TO DECIDE — FLAGGED FOR THE DIFF READ

The ruling this document implements says *"`β` stays 1/298"*. The superseded
`AMENDMENT 5` §A5.7.3 had registered `TRef = 298.15 K` alongside its rejected
`β`. **`1/298.15 = 3.3540164e-3 ≠ 1/298 = 3.3557047e-3`**, a 0.050 % gap, so
carrying `TRef = 298.15` forward beside `β = 1/298` would reintroduce a
`β`/`T_ref` mismatch of **exactly the kind this document exists to eliminate**,
merely 160× smaller.

**REGISTERED: `T_ref = 298.00 K`**, which makes `β = 1/T_ref` exact.

**THE ALTERNATIVE, COMPUTED IN FULL SO THE SUPERVISOR'S DIFF READ CAN OVERRULE
THIS WITHOUT RECOMPUTING ANYTHING.** If `T_ref = 298.15 K` is intended to
survive, then `β = 3.3540164e-03 K⁻¹`, `Ra` becomes **2.134896e9 (+0.2298 %)**,
`ε = β·ΔT` becomes 0.0670803 and the K2e floors become **1.6485 %** and
**0.03118 %**. **That correction must be made before this document fires**;
it moves no band and no gate.

**And it cannot move a graded value either way**, which is shown from solver
source rather than argued (`AMENDMENT 5` §A5.7.5, re-adopted here): `TEqn.H:26`
is the only place `TRef` enters — `rhok = 1.0 - beta*(T - TRef)` — and buoyancy
reaches `UEqn.H` and `pEqn.H:8` only through `fvc::snGrad(rhok)`. A uniform shift
in `rhok` has identically zero surface-normal gradient. Only the derived
`p = p_rgh + rhok*gh` (`pEqn.H:54`) changes, and `p` is in **no** completion
field set, **no** guard and **no** graded row.

### 1.3 `Ra` IS DERIVED AND REPORTED. IT IS NOT A TARGET, AND NO GATE DEPENDS ON MATCHING IT.

**This is the structural repair, and it is what stops the contradiction
recurring a seventh time.** The superseded document treated a **secondary
source's** `Ra` as a number to be hit, which is what over-determined it.

```
  Ra = g * beta * dT * H^3 * Pr / nu^2
     = 9.81 * 3.3557047e-3 * 20.0 * 1.124864 * 0.71 / (1.569e-5)^2
     = 2.135970e9
```

| derived group | value | note |
| --- | ---: | --- |
| **`Ra`** | **2.135970e9** | **DERIVED, REPORTED, NEVER A TARGET** |
| `Gr = Ra/Pr` | 3.008409e9 | derived |
| `Re` (slot) | **653.920** | `0.57 × 0.018 / ν`; the secondary quotes **654**, **−0.012 %** |
| `Re_H` | 3.778203e4 | `0.57 × 1.04 / ν` |
| `Ri = Gr/Re_H²` | **2.10749** | descriptive: the case is in the mixed regime by arithmetic |
| `ε = β·ΔT` | 0.0671141 | inside `physics_rules.yaml:279`'s `boussinesq_beta_dT_max: 0.1` |

**THE RESIDUAL, STATED OPENLY RATHER THAN ENGINEERED AWAY: `Ra` = 2.135970e9 is
+0.2803 % from the published 2.13e9 — and that published figure was itself taken
at a DIFFERENT `ΔT`.** Oulghelou 2020 line 696 defines `Ra = 2.13e9` on
`θ_hot = 35.5 °C` against `θ_cold = 15 °C`, i.e. **`ΔT` = 20.5 K**, while this
rung runs and has always run at **`ΔT` = 20.0 K** (the value both secondaries
actually solved with, and the stricter one). **A 0.28 % residual against a target
taken at a different `ΔT` is not a defect to be closed; closing it was the
defect.** `Ri` inherits the provisional status of its parents and **no gate,
band, threshold, cap or label may depend on `Ri`** — the `AMENDMENT 1` §A1.2
fence, adopted here unchanged.

**Boussinesq model-form floor `M0`**, from K2e's measured laws at
`ε = 0.0671141`: peak velocity **1.6494 %**, Nusselt **0.03121 %**. **REPORTED
beside every velocity row and `G6`, never a correction, never subtracted from a
deviation**, in every branch — with `AMENDMENT 1` §A1.3's three-way disposition
of prediction 3 and its `~53×` magnitude discriminator adopted unchanged. The
exponents were measured on a **laminar differentially heated cavity at
`Ra = 1e5`**; carrying them to a turbulent mixed-convection cavity with a jet is
this lab's **extrapolation in flow class**, interpolated only in `ε`.

---

## 2. REFERENCE

**PRIMARY: Blay, D., Mergui, S. and Niculae, C. (1992), ASME HTD-213 — `NOT
OBTAINED`.** Not on this box at this write. Every graded reference value is
`PENDING` on it, and arming §7.6 of the superseded document is a **dated
reference addendum** that may fill reference values, uncertainties, page/figure
locators and digitisation increments **and nothing else**. If arming it would
require a band to move, the correct action is to record that the registration was
wrong — **not to move the band.**

**SECONDARIES HELD, and strictly bounded:**
`docs/papers/data_center_indoor_airflow/zou_zhao_chen_2018_building_simulation.txt`
(lines 667–705) and
`docs/papers/data_driven_rans/oulghelou_beghein_allery_2020_2009.06724.txt`
(lines 688–726). **They supply the CASE. They may never supply a graded
REFERENCE VALUE** — both only plot the Blay symbols, so any number from them is a
digitisation of a secondary's reproduction of a primary's figure, two removes from
the measurement.

**NEITHER SECONDARY STATES `ν`, `Pr` OR `β` FOR THIS CASE. This was CHECKED at
this registration, not assumed:** both were read at the line ranges cited and
grepped for *viscosity*, *Prandtl*, *expansion coefficient* and `1.5*e-5`.
Oulghelou defines `β` symbolically at line 134 and gives **no number**; every Zou
hit is a **turbulent** viscosity or Prandtl number, none molecular. **`ν`, `Pr`
and `β` are therefore LAB CHOICES and are labelled as such throughout.**

---

## 3. QUANTITIES

**ADOPTED BY CITATION, UNCHANGED, from the superseded document:** the **ten
graded rows** `G1, G2, G3, G4, G5a, G5b, G6, G7, G8, S1` of its §7.3; the
**thirteen graded stations** registered in `AMENDMENT 4` §A4.5; the reported row
**`M0`** (§3.5 and §7.3, REPORTED, NEVER GRADED); and the **five guards**
`HB`, `B`, `I`, `DC`, `MB` of §7.5 with their consequences unchanged — each
withdraws the run, never the hypothesis (Charter 2c).

**This document defines no new quantity and retires none.** The only numbers it
changes anywhere in the quantity set are the two `M0` figures, which move because
`ε` moves with `β`, and `M0` is reported and never graded.

---

## 4. BANDS

**NO BAND IS SET, WIDENED, NARROWED OR REINTERPRETED BY THIS DOCUMENT.** Every
band is adopted **byte-unchanged** from the superseded §7.2 and §7.3:
`± 1.00 K`, `± 0.0570 m/s`, `± 0.0208 m`, `± 0.104 m`, `± 10 % of |q_ref|`,
`EXACT MATCH REQUIRED`, the §7.2 conversion rule with its `max` form and its
anti-widening guard, `ΔT_band = 20.0 K`, the 0.5 % heat-balance tolerance, the
25 % discrimination threshold, and the `y⁺` windows **`≤ 5.0` on L1** and
**`≤ 3.3` on L2 and L3** (3.3 is Oulghelou's own measured maximum on this case,
line 719 — a published figure, not a preference). A case outside its `y⁺` window
has its rows **REPORTED, not graded**.

**The band set does not depend on `ν` or `β`.** `ΔT_band` is frozen
independently at 20.0 K, and every band is computed from it. **Moving `ν` moves
no band**, which is the property that makes this re-registration a physics
decision and not a gate decision.

---

## 5. LADDER

**Three levels, conformal `blockMesh`, three horizontal blocks** (A: `y ∈ [0,
0.024]`, the outlet band; B: `y ∈ [0.024, 1.022]`, the interior; C:
`y ∈ [1.022, 1.040]`, the inlet band), two-sided geometric grading with the
reciprocal written by hand for the second half of each direction (K0cS form,
L-142). Cell counts, block splits and refusal conditions A–G are **adopted
unchanged** from the superseded §4.

`r21 = √(50176/25600) =` **1.400000**; `r32 = √(98596/50176) =` **1.401786**;
both ≥ 1.30, and the comparator uses the **unequal-ratio fixed-point form**
(T3 §7.1) rather than assuming they are equal.

### 5.1 THE FIRST WALL-CELL COLUMN, RE-DERIVED FROM `ν` = 1.569e-5 — NOT COPIED ACROSS

**It could not be copied across, and the arithmetic is shown so a reader can
refuse it.** From `y_cell = 2 y⁺ ν / u_τ` with `u_τ = u_in √(C_f/2)`,
`C_f = 0.005` (wall-jet value), `y⁺ = 1`:

```
  u_tau = 0.57 * sqrt(0.005/2) = 0.57 * 0.05 = 0.028500 m/s

  L1: y = 2 * 1 * 1.569e-5 / 0.028500       = 1.101053e-03 m
  L2: y = 1.101053e-03 / r21 (= 1.400000)   = 7.864662e-04 m
  L3: y = 7.864662e-04 / r32 (= 1.401786)   = 5.610459e-04 m
```

| level | cells | **REGISTERED first wall cell** | superseded value at `ν` = 1.55e-5 |
| --- | ---: | ---: | ---: |
| **L1 coarse** | 25 600 | **1.101053e-03 m** | 1.09e-3 |
| **L2 medium** | 50 176 | **7.864662e-04 m** | 7.78e-4 |
| **L3 fine** | 98 596 | **5.610459e-04 m** | 5.56e-4 |

**WHY THE RE-DERIVATION WAS COMPULSORY.** The first cell is linear in `ν`, so it
moves by `1.569/1.55 =` **+1.2258 %**. §4 refusal condition D requires the first
wall-normal cell to equal the design value **to 1 %**. **1.2258 % > 1 %**: had the
superseded column been carried across, every level would have been refused by the
rung's own mesh guard. Paying this arithmetic to keep the physics coherent is the
correct trade; the reverse never is.

**A DISCREPANCY IN THE SUPERSEDED COLUMN, FOUND WHILE RE-DERIVING, DISCLOSED AND
NOT REPAIRED.** The superseded column cannot be reproduced from its own §4
formula at its own `ν = 1.55e-5`, which gives
`1.087719e-3 / 7.769424e-4 / 5.542519e-4`:

| level | superseded registered | its own formula gives | deviation |
| --- | ---: | ---: | ---: |
| L1 | 1.09e-3 | 1.087719e-03 | **+0.210 %** |
| L2 | 7.78e-4 | 7.769424e-04 | **+0.136 %** |
| L3 | 5.56e-4 | 5.542519e-04 | **+0.315 %** |

All three are inside condition D's 1 %, so nothing was ever refused by it. **The
third significant figure of the superseded L2 and L3 entries could not be
reproduced from any rounding rule this lane could identify, and no rule is
invented here.** The column registered above is **derived from the formula**, not
scaled from the superseded column, precisely so that this ambiguity is not
inherited. **The superseded document is not edited** (rule 6); this is the
disclosure.

**Every mesh is read from `constant/polyMesh` BEFORE any solver runs**, by
`check_k0d_mesh.py`, against refusal conditions A–G — including **condition G,
the planted-positive test: an inverted grading and a slot one cell short are each
injected and each must be REFUSED.** `checkMesh` birth certificate per case.
*T1b attempt 1 lost 57 core-hours to a grading direction nobody read from disk.*

### 5.2 THE NINE CASES

| case | closure | level | cells | `endTime` | purpose |
| --- | --- | --- | ---: | ---: | --- |
| `M1_c` | `kOmegaSST` | L1 | 25 600 | 40 000 | ladder |
| `M1_m` | `kOmegaSST` | L2 | 50 176 | 40 000 | ladder |
| `M1_f` | `kOmegaSST` | L3 | 98 596 | 40 000 | ladder, **graded level** |
| `M2_c` | `RNGkEpsilon` | L1 | 25 600 | 40 000 | ladder |
| `M2_m` | `RNGkEpsilon` | L2 | 50 176 | 40 000 | ladder |
| `M2_f` | `RNGkEpsilon` | L3 | 98 596 | 40 000 | ladder, **graded level** |
| `C_lam` | laminar | L2 | 50 176 | 40 000 | **Charter 2c discrimination control** |
| `B_hi` | `kOmegaSST`, floor **35.5 °C** | L2 | 50 176 | 40 000 | the `ΔT` arbitration guard |
| `I_hi` | `kOmegaSST`, inlet `k`, `ε` **× 4** | L2 | 50 176 | 40 000 | the unmeasured-inlet-turbulence sweep |

**Two closures because `NUMERICS_KNOWLEDGE` K0c-T says quote two models or quote
none.** `RNGkEpsilon` is chosen because it is the model Oulghelou 2020 used on
this exact case (line 699). `B_hi` takes the **same `β`, `T_ref` and `ν`** as
`M1_m` — it perturbs the floor temperature and nothing else, and giving it a
different fluid property would confound the guard it exists to be.

---

## 6. DECOMPOSITION SEED

**Serial. `nProcs = 1`. No decomposition, on all nine cases.** No
`decomposeParDict` is written, `decomposePar` is never run, no `reconstructPar`
is needed, and the solver is invoked directly rather than through `mpirun`.
**There is no partitioner, therefore there is no seed and no partition-dependence
to record.** *This field is recorded because the form requires it, not because
the value is in doubt.* Every case is 2D at ≤ 98 596 cells, which is why serial
is the right choice and not merely the convenient one: nine serial cases in one
batch saturate more of the box than any decomposed subset of them would.

---

## 7. CRITERIA

**7.1 Convergence — the residual is NOT the instrument.** T1c recorded a
genuinely unconverged case at residual `4e-05` (L-141), so `residualControl` is
not written. **CONVERGED** means the largest change of any cell value of `T`, and
separately of `U`, between the written checkpoints at `endTime − 4000` and
`endTime` is at most **`1e-6` of that field's range**. `endTime 40000`,
`deltaT 1`, `writeInterval 4000`, `purgeWrite 2`. One extension of **+20 000
iterations** is registered; a second is not authorised. **The decision to extend
is taken on the convergence state alone, never with a graded value in view.**
A ladder level that is NOT CONVERGED makes every triple containing it
**`NOT A RESULT`**.

**7.2 Strict completion rule with the age guard.** `rc = 0`; an `End` line; last
time == `endTime`; `ExecutionTime` count == `endTime`; **every field at `endTime`
NEWER than the case's own `0/T`**; and the **registered completion field set of
the case's own closure all present**:

| closure | cases | **registered completion field set** | count |
| --- | --- | --- | ---: |
| `kOmegaSST` | `M1_c`, `M1_m`, `M1_f`, `B_hi`, `I_hi` (five) | **`T U p_rgh alphat nut k omega phi`** | 8 |
| `RNGkEpsilon` | `M2_c`, `M2_m`, `M2_f` (three) | **`T U p_rgh alphat nut k epsilon phi`** | 8 |
| laminar | `C_lam` (one) | **`T U p_rgh alphat phi`** | 5 |

**`5×8 + 3×8 + 1×5 = 69` field-presence assertions, ZERO of them unsatisfiable.**

**THIS TABLE IS THE POST-REPAIR FORM AND IT IS REGISTERED HERE DELIBERATELY.**
The superseded §8.2's original clause 4 demanded `T U p_rgh alphat nut k omega`
of **every** case. `RNGkEpsilon` writes `epsilon` and **never writes `omega`**,
so `M2_c`, `M2_m` and `M2_f` could not have satisfied it, and `analyse_k0d.py`
refuses (exit 2) unless all nine `DONE.<case>` markers exist — **the whole rung
would have produced nothing.** That defect was repaired inside the superseded
document by `AMENDMENT 3` §A3.4 (per-closure enumeration) and tightened by
`AMENDMENT 5` §A5.8 (`phi` added to all three sets, verified present on five
solved cases on disk including two laminar ones). **This document carries the
repaired form; it does not reproduce the original tuple.**

**AND THE GENERALISED INSTRUCTION, adopted unchanged and binding on the script
author:** *no exemption and no field substitution may be inferred at grading
time.* A case whose closure does not appear above **has no registered completion
field set**, and `mark_done_k0d.py` **refuses (exit 2) rather than infer one.**
No such case is registered today; the clause exists so adding one later cannot be
done silently.

**7.3 Roache triple gating**, in this order: (1) any level not iteratively
converged or not plateaued → **`NOT A RESULT`**; (2) triple `DIVERGENT`,
`STAGNANT`, `OSCILLATORY` or `EXACT` → **`NOT A RESULT`**, value and both triples
and orders printed beside it; (3) `CONVERGING` → `PASS` inside the band else
`GATE FAIL`, GCI printed at `Fs = 1.25`. **The gate can only turn a PASS or GATE
FAIL INTO `NOT A RESULT`, never the reverse**, and a GCI is never quoted when the
three values are not monotone.

**7.4 Planted-zero control.** The comparator plants a known perturbation, reads
it back from disk and **REFUSES** if the reader cannot see it. A zero from a
reader not shown able to see a non-zero is not evidence.

**7.5 The order of operations, and the comparator freeze.**
`check_k0d_mesh.py` → solve → `mark_done_k0d.py` → `analyse_k0d.py`. **Every
comparator is hashed against its committed blob before analysis** (Charter 2d);
the grading path is fixed at this document's commit. `analyse_k0d.py` refuses
(exit 2) unless **all nine** `DONE.<case>` markers are present.

**7.6 No verdict may be assigned by the lane that runs this.** Verdicts come
from the fixed vocabulary — `PASS` / `GATE REACHED` / `GATE FAIL` /
`NOT A RESULT` / `BLOCKED` / `PENDING` — and §0 already states that no graded
verdict is reachable while the primary is `NOT OBTAINED`.

---

## 8. COST, REGISTERED BEFORE THE RUN (standing rule 12)

**Basis:** sibling **K0cS**, measured on this box 2026-08-18 at
**1.593e-6 s per cell-iteration** (fine 192² pilot, agreeing with the coarse
pilot to 2.4 % per cell), same solver class in all six respects — same solver,
steady, 2D, Boussinesq active, wall-resolved two-equation RANS with a coupled
energy equation, single rank. **× 1.6 developed-flow contingency** (the
multiplier K0cT registered and came in under). **POINT rate 2.549e-6 s per
cell-iteration; CEILING rate 2 × POINT.**

| case | cells | core-s | **core-min** |
| --- | ---: | ---: | ---: |
| `M1_c` | 25 600 | 2 610.2 | 43.50 |
| `M1_m` | 50 176 | 5 115.9 | 85.27 |
| `M1_f` | 98 596 | 10 052.8 | 167.55 |
| `M2_c` | 25 600 | 2 610.2 | 43.50 |
| `M2_m` | 50 176 | 5 115.9 | 85.27 |
| `M2_f` | 98 596 | 10 052.8 | 167.55 |
| `C_lam` | 50 176 | 3 837.0 | **63.95** — 0.75 × the L2 turbulent line, a registered **ESTIMATE**, not a measurement, and a named calibration item |
| `B_hi` | 50 176 | 5 115.9 | 85.27 |
| `I_hi` | 50 176 | 5 115.9 | 85.27 |
| **solver subtotal** | | | **827.11** |
| instruments (meshing 0.75, mesh reader 0.50, comparators 1.00) | | | **2.25** |
| **REGISTERED POINT** | | | **829.36** |

| component | core-min |
| --- | ---: |
| first pass at the CEILING rate (2 × 827.11) | 1 654.23 |
| continuation reserve at the CEILING rate (one +20 000 extension, all nine) | 827.11 |
| instruments, bounded | 3.50 |
| **REGISTERED CEILING / TOTAL CAP** | **2 484.84** |

**Both figures were RE-DERIVED from the basis at this registration and reproduce
the superseded §10.2/§10.3 exactly.** *Method note carried so a reader does not
find a phantom discrepancy: the registered figures use §10.1's rate rounded to
**2.549e-6**. At the unrounded `1.593e-6 × 1.6 = 2.5488e-6` the subtotal is
827.05 and the POINT 829.30.*

**THE FIELD-SET CHANGE DOES NOT MOVE THE COST, and the reason is stated rather
than asserted:** a completion field set is an **instrument over what must be on
disk at `endTime`**. It changes no transport equation, no iteration count and no
mesh. `kOmegaSST` and `RNGkEpsilon` are both **two-equation** closures, so the
per-cell-iteration rate measured on `kOmegaSST` is the rate the estimate already
applies to both — an assumption that predates the repair rather than being
created by it. `phi` is written by the solver whether or not a completion set
names it.

**Derived dollars: POINT 13.823 core-h = $0.709; CEILING 41.414 core-h = $2.125.**
**`cost_basis`: the per-cell-iteration rate is MEASURED (K0cS pilot on this box).
The $0.0513/core-h rate is REPORTED-BY-OWNER, and the dollar figures are
DERIVED, NOT MEASURED — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).** Against the $25 pre-authorisation the POINT
is 2.8 % and the CEILING 8.5 %; **the authorisation is not the binding
constraint, the cap below is.**

### 8.1 STOP RULES, AND THE CAPS AS ENFORCED

1. **THE TOTAL CAP IS 2 484.84 core-min. Reaching it STOPS THE RUN.** The rung
   reports what it has **with the unrun cases named**; a reduced run is never
   silently relabelled as the rung. **An overrun does not get a new budget**
   (rule 12) — more work is a new pre-registration with a corrected `cost_basis`.
2. **PER-CASE HARD STOP: 10× that case's POINT line**, the heat-transfer team's
   registered practice (`COST_CALIBRATION.md` C-1, C-21, C-34).
   **A CAP ENFORCED AS A WALL-CLOCK `timeout` IS NOT A CORE-MINUTE CAP UNLESS IT
   IS CONVERTED: `timeout = cap_core_min × 60 ÷ ranks`, and `ranks = 1` for every
   case here:**

| case | 10× POINT (core-min) | **enforced `timeout` (s)** |
| --- | ---: | ---: |
| `M1_c`, `M2_c` | 435.00 | **26 100** |
| `M1_m`, `M2_m`, `B_hi`, `I_hi` | 852.70 | **51 161** |
| `M1_f`, `M2_f` | 1 675.50 | **100 530** |
| `C_lam` | 639.50 | **38 370** |

   **For every case except the two coarse ones the RUNG CAP binds BEFORE the 10×
   per-case threshold.** Both are in force; whichever is reached first stops the
   run.
3. **RE-ESTIMATE TRIGGER at 1.6× a case's own line.** It does not stop the run;
   it forces the estimate to be re-made and the difference disclosed **before**
   the next case launches.
4. **A case that cannot meet 7.1 after its one registered continuation has its
   rows REPORTED AS REFUSED with the measured spread.**

**Wall clock, and the disclosure that stops a legitimate row being cleaned as a
stall:** the critical path is `M1_f`/`M2_f` at **10 052.8 wall s = 2.79 h** at
the POINT rate, **5.58 h** at the CEILING rate. **Those two rows exceed 3 600
wall s BY DESIGN**, so `COMPUTE_BUDGET_CHARTER.md`'s over-3600 stall rule does
**not** apply to them and they are **not** cleaned. A stall here means
`ExecutionTime` stops advancing, which `STATUS.<case>` and the log detect
separately.

### 8.2 CALIBRATION OBLIGATION (rule 12), REGISTERED NOW

At rung completion the comparison is **not optional and a completion report
without it is incomplete**: actual core-minutes from `STATUS.<case>` and
`ExecutionTime`; the ratios **actual/POINT** and **actual/CEILING**; the gap
attributed; **waste and contention NAMED SEPARATELY and never absorbed into the
ratio** (`COMPUTE_BUDGET_CHARTER.md` §6); dollars derived at $0.0513/core-h and
**labelled derived**; landing as a row in **`docs/COST_CALIBRATION.md`** under
the rule-10 private-index protocol. **Three named calibration items are
registered in advance:** the `0.75` laminar scale factor, the `1.6×` developed-flow
contingency, and the **per-case memory estimates of §9.2**.

---

## 9. SCHEDULING — REGISTERED, INCLUDING THE PART THAT IS UNFLATTERING

### 9.1 Concurrency

**REGISTERED CONCURRENCY CAP: 9. One batch of all nine cases, serial,
`nProcs = 1`.** This **raises the superseded §10.3's cap of 6**; raising it is a
new registration's call and it **moves no gate, band, threshold or label**.

Measured on this box at **2026-08-25T18:07Z**: 16 cores, five processes at
≥ 95 % CPU. **`5 + 9 = 14` of 16 = 87.5 %**, inside Sanaa's 80–90 % saturation
band, leaving 2 cores for the session, git and the instruments.

### 9.2 Memory

**Measured rate:** `buoyantBoussinesqSimpleFoam` at **209 920 cells** holds
**487–507 MB RSS** (three live T-family cases), i.e. **~2.4 kB/cell** flat, or
~2.08 kB/cell above a **~60 MB baseline**. **THE 2.4 kB/cell RATE IS MEASURED;
THE ~60 MB BASELINE IS INFERRED FROM `simpleFoam` AT 2 500 CELLS, WHICH IS A
DIFFERENT SOLVER.** Both statuses are stated because they are not the same
status.

| level | cells | estimate | conservative bound |
| --- | ---: | ---: | ---: |
| L1 | 25 600 | ~113 MB | ~162 MB |
| L2 | 50 176 | ~164 MB | ~220 MB |
| L3 | 98 596 | ~265 MB | ~337 MB |

**All nine concurrent: ~1.58 GB estimated, ~2.15 GB on the conservative bound**,
against `MemAvailable` 17.7 GiB and this family's **standing 12 GiB floor**
(`LAB_STATE.md:1871`) — **5.7 GiB of headroom, so ~3.5 GiB to spare at the
bound.** **The binding memory risk is not K0d**: a single 10.39 GB adjoint was
live on the box at this write, and a second such job makes the floor the
constraint, not the cores. **A batch that OOMs is worse than a batch that
queues**; if `MemAvailable` is under 14 GiB at launch, the batch drops to the
seven non-L3 cases and the two L3 cases queue behind them.

### 9.3 THE UTILISATION DECAY — A REGISTERED EXPECTATION, NOT A FOOTNOTE

**K0d's ladder is imbalanced (167.55 core-min against 43.50), so the batch cannot
hold the saturation band for its own window. Registered in advance so it is
neither discovered nor hidden:**

| elapsed (POINT rate) | still running | cores busy | utilisation |
| ---: | --- | ---: | ---: |
| 0 | all nine | 14 | **87.5 %** |
| ~43.5 min | `M1_c`, `M2_c` done | 12 | 75.0 % |
| ~64 min | `C_lam` done | 11 | 68.8 % |
| ~85 min | `M1_m`, `M2_m`, `B_hi`, `I_hi` done | 7 | 43.8 % |
| ~168 min | `M1_f`, `M2_f` done | 5 | 31.3 % |

**Mean K0d occupancy over its own critical path is `827.11 / 167.55 =` 4.94
cores, so mean utilisation is `(4.94 + 5)/16 =` 62 % — BELOW Sanaa's 80–90 %
band. K0d ALONE CANNOT HOLD THAT BAND FOR ITS OWN WINDOW**, and the retiring
cores **must be backfilled from the team's queue** rather than the batch being
inflated. Under-loaded-with-a-queue is the same defect as idle, at lower
severity; this table is what makes it visible before the run rather than after.

### 9.4 Contention

**At the disclosed-acceptable 5–11 %, the solver subtotal inflates to
868.5–918.1 core-min — 35–37 % of the CEILING**, which the 2× ceiling absorbs
with a wide margin. **Contention is NAMED SEPARATELY at completion and never
absorbed into the actual/predicted ratio** (`COMPUTE_BUDGET_CHARTER.md` §6). A
per-case contention file is kept.

---

## 10. DISCLOSURES — CARRIED UNSOFTENED

1. **No held source states `ν`, `Pr` or `β` for this case.** Checked, not
   assumed (§2). All three are lab choices.
2. **The primary, Blay, Mergui and Niculae (1992), is `NOT OBTAINED`.** No graded
   verdict is reachable until it lands and is **title-page verified** (L-144).
3. **The Sutherland fluid-state argument is a CONSISTENCY argument and NOT an
   ATTRIBUTION.** It shows that `β = 1/306.21` contradicts a registered `T_ref`
   of 298.15 K. It does **not** establish that `ν = 1.569e-5` is the right
   viscosity for this experiment, and nothing in this document claims it does.
4. **The memory baseline (~60 MB) is INFERRED from a different solver; the
   2.4 kB/cell rate is MEASURED.** (§9.2)
5. **Unattributed contention, recorded and deliberately NOT rationalised.** At
   2026-08-25T18:07Z `/proc/loadavg` read **21.01 / 14.40 / 10.20** while only
   **five** processes were at ≥ 95 % CPU. The 1-minute figure includes the
   registering lane's own sweeps; **the 15-minute 10.20 exceeds the five visible
   processes and this document does not explain it.** It is a real observation
   and rationalising it would be worse than leaving it open.
6. **THE THIRD RECONCILIATION ROUTE IS PHYSICALLY REFUTED, recorded so it is not
   proposed again.** Making `Pr` the free variable at `ν = 1.55e-5`,
   `β = 1/298` requires `Pr = 0.71 × 2.13/2.188657 =` **0.6910**. Air's molecular
   Prandtl number does not fall below ~0.70 anywhere near room temperature.
   **Moving `Pr` is not available.**
7. **The `AMENDMENT 5` §A5.7.4 `ΔT` exposure is CARRIED, not closed.** If the
   primary establishes `ΔT = 20.5 K`, this rung ran at a `ΔT` 2.5 % low. That is
   a **DISCLOSED INPUT ERROR reported as one** beside every affected row; it is
   **not silently re-run**, and **`ΔT_band` does not move** — a `β` or `ΔT` error
   is an error in the physics the solver ran, never a licence to widen a band.
   Guard `B` measures the same discrepancy from the solution side.
8. **`RNGkEpsilon` takes high-Re wall functions against a `y⁺ ≤ 1` mesh.**
   OpenFOAM's `RNGkEpsilon` carries no low-Reynolds damping and this lab has no
   low-Re wall set for it. The measured-and-reported `y⁺` window of §4 is the
   instrument that surfaces this, and a case outside it is **REPORTED, not
   graded**.
9. **The initial `internalField` of every field, and the profile sampling method,
   remain items the superseded `AMENDMENT 5` §A5.13 referred (Findings 10 and
   11).** **Both can move a graded value.** They are **not** resolved by this
   document and **must be ruled before the first case starts.** Named here rather
   than left in a superseded document's appendix.
10. **The shared git index is still stale in the reverting direction.** At this
    write it staged the superseded `K0d_PREREGISTRATION.md` at **986 lines**
    against HEAD's **3 759** — a bare `git commit` by any agent deletes 2 773
    lines and all five amendments. **Inspected, never reverted** (rule 10); the
    index is the chief's call. Every commit in this line used the private-index
    protocol.

---

## 11. WHAT THIS DOCUMENT DOES NOT DO

- **It authorises no solve.** The supervisor reads it as a **diff** before any
  compute — an undelegatable check under `SUPERVISION_CHARTER.md` §3, which no
  throughput directive overrides. Firing without it is a standing rule 2
  violation.
- **It deletes nothing.** `K0d_PREREGISTRATION.md` (`e629f5c4`) and all five
  amendments stay on disk byte-unchanged.
- **It moves no gate, band, threshold or label.** The only registered numbers it
  changes are `ν`, the first wall-cell column that depends on `ν`, `Ra`'s status
  (target → derived and reported), the two reported `M0` figures, and the
  concurrency cap.
- **It ran no compute.** Zero core-minutes. `K0d_runs/` does not exist. Rule 12's
  estimate-versus-actual calibration is **not triggered**, because no process
  completed.
- **It sent nothing** (standing rule 7). Submissions remain **PARKED**.
- **It touched no permission setting, no `CLAUDE.md` and no `.claude/` config.**

**K0d is RE-REGISTERED, FROZEN AND UNFIRED.**

*Registered by a heat-transfer lane on the supervisor's `ν`-versus-`β` ruling,
2026-08-25. Resolution class `[lab-attributed]`. Zero compute.*

---

# AMENDMENT 1 — 2026-08-25, BEFORE FIRST COMPUTE. Version 1.0 → 1.1.

**lines whose number changed above this section: 0.** This amendment is appended
at the foot; nothing above it is edited (standing rule 6). The parent blob
`498793838939dcca873289bfd5c85b39025a65e0` is a **byte prefix** of this file.

**IT IMPLEMENTS THREE SUPERVISOR RULINGS, ALL OF WHICH TIGHTEN. AND IT REACHES
ONE CONCLUSION THE RULINGS DID NOT ANTICIPATE: THE RUNG NO LONGER FITS ITS OWN
REGISTERED CAP, SO IT DOES NOT FIRE UNDER THIS AMENDMENT.** §A1.5 states that
plainly and §A1.6 records the verdict.

## A1.0 The condition under which this amendment is legal, and how it was checked

Standing rule 2: before first compute, amendments are legal **and must state the
condition and how it was checked**. The condition is that **no K0d compute has
run**, and it was checked by naming the run directory that does not exist:
`test -e verification/runs/F14-cooling-ladder/K0d_runs` returned **ABSENT** in
the invocation that wrote this amendment, **under a planted control** in which
the same reader returned PRESENT on a directory that does exist — a zero from a
reader not shown able to see a non-zero is not evidence (standing rule 3).

**This amendment alters no gate, no band, no threshold and no label.** It alters
the **cost registration**, which §A1.4 states in full, and the alteration is the
reason the rung stops.

## A1.1 RULING 1 — `T_ref` = 298.00 K UPHELD; the alternative is marked OVERRULED

§1.2's registered `T_ref = 298.00 K` and `β = 1/298 = 3.3557047e-03 K⁻¹` **stand
unchanged.** The supervisor re-derived the whole fluid state and the first-cell
column independently and reproduced every figure.

**§1.2's computed alternative — `T_ref` = 298.15 K, `β` = 3.3540164e-03,
`Ra` = 2.134896e9 (+0.2298 %), `M0` floors 1.6485 % and 0.03118 % — is
`OVERRULED`.** It stays in the document, marked overruled, so a later reader can
see what was considered and rejected rather than only what was chosen. The
reason it is rejected is recorded in the supervisor's terms: registering
`T_ref` = 298.15 beside `β` = 1/298 would ship this document with a 0.050 %
instance of **the exact defect class it exists to eliminate**, and *"160× smaller
is not a defence — it is the same error at a size chosen for comfort."*

## A1.2 RULING 2 — the initial field is REGISTERED, and the seed dependence is MEASURED rather than assumed away

### A1.2a THE SEED, REGISTERED AND FROZEN — **PER CLOSURE**, and the reason that is not a widening

The ruling registers the smoke test's seed *"verbatim and frozen for all nine
cases — `T` 288.15, `U` (0 0 0), `p_rgh` 0, `k` 1.25e-3, `omega` 51.2, `nut` 0,
`alphat` 0"*.

**APPLIED LITERALLY TO ALL CASES, THAT LIST RECREATES §8.2's ORIGINAL CLAUSE-4
DEFECT EXACTLY.** `RNGkEpsilon` has **no `omega` field**, so `M2_c`, `M2_m` and
`M2_f` cannot carry an `omega` seed; the laminar case has **no `k`, no `omega`
and no `nut`**, so `C_lam` cannot carry three of the seven. **This is the same
failure this document was written to remove, arriving through the initial
condition instead of the completion check.** It is therefore registered
**per closure**, on the identical pattern as §7.2, and that is an implementation
of the ruling rather than a widening of it:

| closure | cases | **registered `internalField` seed** |
| --- | --- | --- |
| `kOmegaSST` | `M1_c`, `M1_m`, `M1_f`, `B_hi`, `I_hi`, `M1_m_seed` (six) | `T` **288.15**, `U` **(0 0 0)**, `p_rgh` **0**, `k` **1.25e-3**, `omega` **51.2**, `nut` **0**, `alphat` **0** |
| `RNGkEpsilon` | `M2_c`, `M2_m`, `M2_f` (three) | `T` **288.15**, `U` **(0 0 0)**, `p_rgh` **0**, `k` **1.25e-3**, `epsilon` **5.76e-3**, `nut` **0**, `alphat` **0** |
| laminar | `C_lam` (one) | `T` **288.15**, `U` **(0 0 0)**, `p_rgh` **0**, `alphat` **0** |

**`epsilon` = 5.76e-3 IS NOT A NEW NUMBER — IT IS THE SAME SEED.** The registered
`omega` 51.2 **is** that `epsilon` under the conversion `ω = ε/(C_μ k)`:
`5.76e-3 / (0.09 × 1.25e-3) =` **51.2000**, exact. The two rows are one physical
seed expressed in each closure's own variable, and neither is chosen freely.

**`T` = 288.15 K is a physically coherent cold start** — it is the inlet
temperature and the temperature of the ceiling and both vertical walls (15 °C),
so the field is seeded at the boundary value that three of four wall groups
already hold. **That is why it is defensible and not merely convenient**, and it
is the reason it is registered rather than replaced.

**No exemption and no seed substitution may be inferred at build time.** A case
whose closure does not appear above **has no registered seed**, and
`build_k0d.py` **refuses (exit 2) rather than infer one.**

### A1.2b `M1_m_seed` — a seed-perturbation CONTROL, REPORTED, NEVER GRADED

**REGISTERED: a tenth case, `M1_m_seed`.** `kOmegaSST`, L2, 50 176 cells,
`endTime` 40 000, completion field set `T U p_rgh alphat nut k omega phi` (8).
**Identical to `M1_m` in every respect — mesh, closure, schemes, solvers,
boundary types, `β`, `ν`, `T_ref`, `endTime`, convergence criterion — except one
field: `T`'s `internalField` is a HOT START at 308.15 K, the floor temperature.**
Every other seed entry is the registered `kOmegaSST` row above, unchanged.

**CLASSIFICATION: `CONTROL — REPORTED, NEVER GRADED`.** It produces no graded
value and appears in no graded row.

**ITS CRITERION, FROZEN NOW AND NOT CHOSEN AFTERWARDS:** at L2, every graded
quantity of §3 is extracted from `M1_m` and from `M1_m_seed` and the two are
differenced. **If ANY graded quantity differs between the two seeds by more than
that quantity's own registered band, then the rung's graded rows are `REPORTED,
NOT GRADED`, and SEED-DEPENDENCE IS THE FINDING.**

**Why this control exists rather than an assurance.** §10 item 9 of this document
already records that a steady SIMPLE solve of a buoyant cavity is **not
guaranteed to be seed-independent**, and this family built
`verification/runs/F14-cooling-ladder/K0cS_runs/C2_seed_d100` for exactly that
question. Having decided once that the risk is real enough to measure, it is not
now assumed away on a rung whose graded levels are the expensive ones.
**Registering a seed makes a run REPRODUCIBLE; it does not make it
SEED-INDEPENDENT, and only the control can tell those two apart.** This is the
planted-zero principle applied to initial conditions.

**`analyse_k0d.py`'s refusal count moves from NINE to TEN.** It refuses (exit 2)
unless all **ten** `DONE.<case>` markers are present. §10 item 9's Finding 10 is
**CLOSED** by this section.

## A1.3 RULING 3 — the extraction method is REGISTERED, and a dual-scheme control measures what it costs

### A1.3a REGISTERED, and every choice named

| item | **registered value** |
| --- | --- |
| `setFormat` | **`raw`** |
| `interpolationScheme` (**graded**) | **`cellPoint`** |
| `interpolationScheme` (**control**) | **`cell`** |
| sample set type | **`uniform`**, `axis distance` |
| vertical mid-plane set | start `(0.52, 0, z_m)` → end `(0.52, 1.04, z_m)` |
| horizontal mid-plane set | start `(0, 0.52, z_m)` → end `(1.04, 0.52, z_m)` |
| `nPoints`, both sets | **2081**, i.e. a sample spacing of exactly **5.000e-04 m** |
| sample plane `z_m` | **the mid-thickness CELL-CENTRE plane**, `z_m = t/2` |

**"FACE CENTRES OR CELL CENTRES" — ANSWERED EXPLICITLY, BECAUSE IT IS NEITHER.**
The profile is taken at **registered uniform points on the line**, not at face
centres and not at cell centres. The value at each point is `cellPoint`-
interpolated from vertex values for the graded extraction, and looked up from the
containing cell (piecewise-constant) for the control. The line lies in the
**mid-thickness cell-centre plane**; because the mesh is one cell thick in `z`,
that plane is the cell-centre plane for any thickness `t`, so this choice is
independent of `t`. *(`t` itself remains the superseded `AMENDMENT 5` §A5.13
Finding 15 item — unregistered, and it cancels in every registered quantity.
This amendment does not register it and does not need to.)*

**WHY `cellPoint` AND NOT `cell`, WITH THE ARITHMETIC.** `cell` is
piecewise-constant, so it **quantises a peak location to the cell size**. The L3
uniform interior cell is `1.04/314 =` **3.3121e-03 m**, against `G5b`'s band of
**±0.0208 m** — **15.92 % of the band, put there by the extraction method
alone**, which reproduces the supervisor's "about a sixth". The registered
sample spacing of **5.000e-04 m** puts **2.40 %** into `G5b` and **0.481 %** into
`G8`'s ±0.104 m, and is **finer than the finest cell anywhere in the domain**
(the L3 first wall cell is 5.610459e-04 m).

### A1.3b THE DUAL-SCHEME CONTROL

**REGISTERED: `G1`, `G2`, `G3`, `G4`, `G5b` and `G8` are extracted under BOTH
`cell` AND `cellPoint`, and the difference is reported for every one.**

**FROZEN CRITERION: any graded row where the two schemes differ by more than its
own registered band is `REPORTED, NOT GRADED`** — because such a number is an
artefact of an extraction choice and not a property of the solution.

**It requires no additional solve.** It is pure post-processing over time
directories that already exist. §10 item 9's Finding 11 is **CLOSED** by this
section.

## A1.4 THE COST, RE-DERIVED — AND IT DOES NOT FIT THE REGISTERED CAP

**Re-derived from the registered per-case figures, not estimated.**
`M1_m_seed` is an L2 `kOmegaSST` case, so it takes the **identical POINT line to
`M1_m`: 85.27 core-min** (50 176 cells × 40 000 iterations × 2.549e-6 s).

| line | before | **after** |
| --- | ---: | ---: |
| solver subtotal | 827.11 | **912.38** (`+85.27`) |
| meshing (5 core-s per case) | 0.75 (9 cases) | **0.83** (10 cases), bounded ≤ 2.00 |
| `check_k0d_mesh.py`, three `polyMesh` reads | 0.50 | 0.50 (unchanged — `M1_m_seed` reuses L2's mesh) |
| `mark_done_k0d.py` + `analyse_k0d.py` + `--selftest` | 1.00 | 1.00 |
| **dual-scheme extraction (NEW)** | — | **≤ 8.00** |
| **POINT TOTAL** | 829.36 | **922.71** (`+93.35`, **+11.26 %**) |

**THE DUAL-SCHEME EXTRACTION IS REGISTERED AS `≤ 8.00 core-min`, NOT AS ZERO,
AND THE DEPARTURE FROM THE RULING'S WORDING IS DISCLOSED HERE RATHER THAN TAKEN
SILENTLY.** The ruling says it *"must be registered as zero rather than left
uncosted."* It is correctly **zero additional SOLVE**, and that is the load-bearing
claim. But it is **ten cases × two schemes of `postProcess -func sample`**, each
reading a time directory of up to 98 596 cells and writing thirteen station
profiles, and that is **not** zero core-minutes. **A cost known to be non-zero
must not be registered as zero** — `cost_basis` honesty is the clause that makes
every other figure in this section readable. It is registered as a **bounded
ESTIMATE**, basis stated: ≤ 24 core-s per extraction × 20 extractions = 480
core-s = 8.00 core-min. **No measurement backs the 24 core-s** and it is
therefore not called measured. If the supervisor's intent was that it be
absorbed into the existing 1.00 comparator line, that is a one-line correction
and it **does not change §A1.5's conclusion**, which holds at every instrument
figure tried below.

**THE CEILING, and this is where the rung stops.** The registered structure is
`CEILING = 2×S (first pass) + S (continuation reserve at the ceiling rate) +
instruments = 3S + I`:

| arrangement | CEILING | vs the registered cap **2 484.84** |
| --- | ---: | ---: |
| `3 × 912.38 + 12.00` (instruments bounded for the new line) | **2 749.14** | **+264.30 (+10.64 %)** |
| `3 × 912.38 + 3.50` (instruments left at the old bound) | 2 740.64 | **+255.80 (+10.29 %)** |
| `2×912.38 + 827.11 + 12.00` (seed control denied a continuation reserve) | 2 663.87 | **+179.03 (+7.20 %)** |
| `2×912.38 + 827.11 + 3.50` (both concessions together) | 2 655.37 | **+170.53 (+6.86 %)** |

**EVERY ARRANGEMENT EXCEEDS THE REGISTERED CAP. There is no way to seat a tenth
L2 case inside 2 484.84 core-min**, and the two levers that might have done it —
denying the control a continuation reserve, and shrinking the instruments — are
worth 93.77 core-min together against a 264.30 core-min gap.

**Moving `M1_m_seed` to L1 would fit (43.50 instead of 85.27), and it is
REJECTED:** the ruling requires the control to be *"identical to `M1_m` in every
respect except `T`'s `internalField`"*, and a control on a different mesh
measures mesh sensitivity confounded with seed sensitivity. **That is not the
instrument the ruling registered**, and a lane does not narrow a ruling to make a
budget fit.

Derived dollars at the owner-reported $0.0513/core-h, **derived and not
measured**: POINT 15.379 core-h = **$0.789**; CEILING 45.819 core-h = **$2.351**.
**The $25 pre-authorisation is not the binding constraint. The registered cap
is**, and Sanaa's 2026-08-21 blanket is not a per-item read (standing rule 9).

## A1.5 CONSEQUENCE: THE RUNG DOES NOT FIRE UNDER THIS AMENDMENT

**Standing rule 12: an overrun STOPS THE RUN; it does not get a new budget.**
The supervisor's ruling anticipated this exact branch and pre-committed the
response: *"confirm the new total sits inside the 2 484.84 core-min ceiling. If
it does not, stop and tell me."*

**It does not. The launch authorisation in that ruling is therefore not
exercised, and no case was built, no mesh generated and no solver started.**

**Raising a registered cap is legal before first compute** — rule 2 closes gates,
thresholds, caps and labels **after** first compute, and no K0d compute has run.
**So this is a decision that CAN be taken; it is simply not a lane's to take.**
A lane that quietly re-registered a cap to fit work it had been told to do would
be laundering an authorisation whose whole content was the number it changed
(standing rule 9: *approval of an item is approval of ITS cap, not a new
ceiling*). **The cap decision is REFERRED to the supervisor, with all four
arrangements costed above so it can be made from arithmetic.**

## A1.6 VERDICT

**`BLOCKED`** — on the registered compute cap, pending a supervisor ruling on
§A1.4. Zero core-minutes spent. `verification/runs/F14-cooling-ladder/K0d_runs/`
does not exist.

**This is a cap decision, not a defect.** Rulings 1, 2 and 3 are implemented
above **in full and as written**, the document is otherwise ready to fire, and
nothing in the physics, the gate, the instruments or the mesh is outstanding.

## A1.7 THIS TIGHTENS AND CANNOT LOOSEN — shown, in a form a reader can refuse

- **Registering a seed removes a degree of freedom** that `build_k0d.py` would
  otherwise have chosen unregistered. Choices before: 7 unregistered
  `internalField` values × 9 cases. After: **0**.
- **`M1_m_seed`'s criterion can only move a row from GRADED to REPORTED.** It
  produces no graded value, appears in no graded row, and **cannot turn a
  `GATE FAIL` into a `PASS`.**
- **The dual-scheme criterion has the same one-way property**, for the same
  reason.
- **Registering `cellPoint` and the sample geometry removes four unregistered
  extraction choices** (`setFormat`, `interpolationScheme`, set type, sample
  plane) that sat directly under `G1`–`G4`, `G5b` and `G8`.
- **The completion-marker count rises from nine to ten** — a case added to a
  refusal, never removed from one.
- **Field-presence assertions rise from 69 to 77** (`6×8 + 3×8 + 1×5`), **eight
  added, zero removed, and still zero that no run could satisfy.**

## A1.8 WHAT THIS AMENDMENT DID NOT DO — each stated explicitly

- **No GATE moved.** The ten graded rows, the thirteen stations, the five guards,
  the verdict ladder, Roache triple gating and the planted-zero control are
  untouched.
- **No BAND, THRESHOLD or LABEL moved.** Every band adopted in §4 is
  byte-unchanged.
- **The physics did not move.** `ν` = 1.569e-5, `β` = 1/298, `T_ref` = 298.00 K,
  `Pr` = 0.71, `ΔT` = 20.0 K, `Ra` = 2.135970e9 derived-and-reported, and the
  first wall-cell column of §5.1 all stand exactly as registered.
- **The CAP was NOT raised.** 2 484.84 core-min stands as the registered cap, and
  this amendment records that the amended scope does not fit inside it rather
  than moving it.
- **NOTHING WAS LAUNCHED.** No case directory, no mesh, no solver, no pid. Zero
  core-minutes. Rule 12's estimate-versus-actual calibration is **not
  triggered**, because no process completed.
- **The superseded `K0d_PREREGISTRATION.md` was not touched.** Blob `e629f5c4`
  re-verified against HEAD in this amendment's own invocation.
- **`docs/LAB_STATE.md`, `docs/DOCKET.md`, `docs/LESSONS.md` and
  `docs/COST_CALIBRATION.md` were not touched**, and `scripts/append_record.py`
  was not used for any id.
- **Nothing was sent** (standing rule 7). Submissions remain **PARKED**.

*Amendment written by a heat-transfer lane on the supervisor's three rulings,
2026-08-25. Zero compute. The rung is `BLOCKED` on its cap.*

---

# AMENDMENT 2 — 2026-08-25, BEFORE FIRST COMPUTE. Version 1.1 → 1.2.

**lines whose number changed above this section: 0.** This amendment is appended
at the foot; nothing above it is edited (standing rule 6). **The assertion was
VERIFIED, not typed:** in the invocation that wrote this amendment the first 929
lines of this file were compared byte-for-byte against the committed blob of
v1.1 at the captured HEAD, and the comparison was clean. Other records cite this
file by line and one citation sits inside an executable check, so the assertion
is made only because it was checked.

## A2.0 The condition under which this amendment is legal, and how it was checked

Standing rule 2: before first compute, amendments are legal **and must state the
condition and how it was checked**. The condition is that **no K0d compute has
run**, and it was checked by naming the run directory that does not exist:
`test -e verification/runs/F14-cooling-ladder/K0d_runs` returned **ABSENT** at
**2026-08-25 20:39:05Z**, re-proved inside this amendment's own committing shell
invocation and not cited from any upstream message, **under a planted control**
in which the same reader returned PRESENT on
`verification/runs/F14-cooling-ladder/K0cS_runs`, which does exist — a zero from
a reader not shown able to see a non-zero is not evidence (standing rule 3).

**This amendment alters no gate, no band, no threshold and no label.** It:

1. closes the four `REGISTRATION_GAPS` on which `build_k0d.py` refuses (§A2.1);
2. **raises the registered CEILING** from 2 484.84 to **2 748.64 core-min**, and
   records the intermediate figure 2 749.14 as **SUPERSEDED** rather than
   deleting it (§A2.2) — a cap change, legal only because no compute has run;
3. registers a **defect and repair in `check_k0d_mesh.py` condition C** (§A2.3);
4. states plainly **what this rung can and cannot earn** (§A2.4);
5. **corrects a claim standing elsewhere in the repository that K0d is `BLOCKED`
   on an over-determined `Ra`** (§A2.5).

**Attribution.** The four gap rulings of §A2.1 and the ceiling ruling of §A2.2
are the **heat-transfer supervisor's**. None is a tier definition, an external
send, a constitutional change, or compute above a cap, so all sit inside the
supervisor's authority. They were referred to Sanaa's desk under her desk-item
disposal rule of 2026-08-25 and **adopted by silence within one day**; they are
recorded **`[lab-attributed]`**. No agent message is Sanaa's consent (standing
rule 9) and this amendment does not claim otherwise.

---

## A2.1 THE FOUR REGISTRATION GAPS, CLOSED — with the derivation, not only the value

`build_k0d.py`'s `REGISTRATION_GAPS` table carries four entries at `value=None`,
and the builder **refuses (exit 2) and writes nothing** while any is unresolved.
**The builder is correct to refuse.** Superseded §A5.11 clause 2 forbids the
script choosing what this document leaves open: *"If the builder reaches a value
this document does not fix, that is a finding, it is referred upward, and it is
registered by amendment while the window is open — IT IS NOT CHOSEN BY THE
SCRIPT."* The refusal is the clause working, not a fault. **These four values are
registered here, and the builder reads them from this registration.**

### A2.1a RULING 1 — `writeFormat` = **`ascii`**

**Registered because it is the one setting under which every registered
instrument on this rung has been SHOWN ABLE TO SEE.**

- `check_k0d_mesh.py` reads `constant/polyMesh/points` and `constant/polyMesh/owner`
  through an **ASCII regex reader** (`read_points`, `read_n_cells`) and **refuses
  what it cannot parse**. A binary mesh would not fail loudly; it would **silently
  disarm refusal conditions A–F**, which is the worse failure.
- The planted-zero control (standing rule 3) must plant a known perturbation
  **into a field on disk** and read it back **through the same reader that
  produces the graded number**. Binary cannot carry that readback through a
  parser this lab has neither written nor verified. **A control that cannot be
  read back is not a control.**
- Sibling **K0cS** used `ascii`, so the choice is the family's demonstrated path
  and not a new one.

*Cost note:* `ascii` is larger on disk than `binary`. Disk is not a registered
constraint on this rung and no cap in §8 or §A2.2 is denominated in bytes.

### A2.1b RULING 2 — `writePrecision` = **`16`**, **and the arithmetic is the ruling**

**This entry registers the arithmetic, not merely the integer**, because the
integer without the arithmetic is a preference and the arithmetic is a
constraint.

§7.1's iterative-convergence criterion is **at most `1e-6` of the field's range
between two written checkpoints**. The registered `T` range is
**308.15 − 288.15 = 20.0 K**, so the criterion is:

```
  criterion = 1e-6 * 20.0 K = 2.0e-5 K
```

An ASCII field written at **8 significant digits** near 300 K resolves to
`300.00000`, i.e. a **last-digit quantum of ~1e-5 K — the same order of magnitude
as the criterion itself.** Two successive checkpoints could then differ by **one
quantum of the WRITER**, and the criterion could not distinguish that from
convergence. **A convergence criterion sitting at the write quantum is not a
criterion; it is a coin toss the document would have called a gate.**

At **16 significant digits** the quantum near 300 K is **~1e-13 K**.

```
  2.0e-5 / 1e-13 = 2e8   ->  EIGHT orders of magnitude below the criterion
```

**A CORRECTION MADE VISIBLY RATHER THAN QUIETLY (this document's own standard,
§A2.2):** the supervisor's ruling as transmitted described 1e-13 K as *"five
orders below"* the criterion. The correct separation is **eight orders**. **The
registered value `16` is unchanged and the ruling's substance is unchanged** —
the correction makes the margin larger, never smaller, so it cannot have been
chosen to make a threshold fit. It is recorded here rather than silently
propagated. Sibling **K0cS** also writes at 16.

### A2.1c RULING 3 — `writeCompression` = **`off`**, **and the selftest is extended anyway**

`mark_done_k0d.py`'s `field_path` accepts **either** `T` or `T.gz`, so the
completion reader does not depend on the answer. **But its `.gz` branch is never
exercised by its selftest, and a reader branch not shown able to see is exactly
standing rule 3's defect class.** `off` puts every instrument on the path it has
been demonstrated on. Disk is cheap and no registered cap is denominated in
bytes.

**REGISTERED AS REQUIRED, NOT OPTIONAL:** `mark_done_k0d.py`'s selftest is
extended to exercise the `.gz` branch **even though this rung will not produce a
gzipped field** —

1. a **gzipped clean case** that must still **PASS** every clause of the strict
   completion rule; and
2. a **gzipped case whose fields are older than its own `0/T`**, on which the
   **age guard must still FIRE**.

**A branch kept alive in the code and dead in the test is a branch that will be
believed the first time it is used.** Registering `off` closes the exposure on
this rung; extending the selftest closes it on the next.

### A2.1d RULING 4 — `domain_thickness_t` = **`0.010 m`**

**The builder's finding is right and is why this ruling is owed.** §A1.3a's
*"cancels in every registered quantity"* is **true of the GRADED quantities and
false of the MESH FILE**: `blockMeshDict` cannot be written without a z-extent,
and the registered sampling plane `z_m = t/2` puts `t` into the extraction
dictionaries as well.

The case is registered **2D: one cell in z, `empty` front and back patches.**
Under that construction:

- **no graded quantity depends on `t`** — the fields are z-invariant by
  construction, and `Ra`, `Ri`, `Re` and `Re_H` are every one of them built on
  the 1.040 m cavity dimension or the 0.018 m slot height, **never on `t`**
  (§1.3's derivation contains no `t`);
- the registered sampling plane `z_m = t/2` is the **single cell's centre plane
  for ANY `t`**, so the sampling geometry is `t`-invariant too.

`0.010 m` is registered because the scratch smoke test used it and no registered
quantity distinguishes it from any other positive value.

**REGISTERED WITH THE TWO ASSERTIONS THAT MAKE IT REFUTABLE**, because a claim of
invariance that nothing can contradict is not a claim:

- **A1.** `build_k0d.py` asserts **exactly one cell in z** and **`empty` front and
  back patches** on every case it writes.
- **A2.** The extraction dictionaries assert the **sampling `z` equals that
  single cell's centre plane**.

**If a graded number is ever found to move with `t`, that is a finding against
the 2D registration, not against this ruling** — and the two assertions are what
would make that finding possible instead of invisible.

---

## A2.2 THE CEILING — RE-DERIVED, RAISED, AND BOTH FIGURES ON THE RECORD

**Two figures for the same cap were standing in two places. Both are recorded
here and the superseding one is named. A ruling quietly corrected is worse than
one visibly corrected.**

### A2.2a The instrument enumeration, and the check that it is the right one

§A1.4's instrument enumeration is:

| instrument | bounded core-min |
| --- | ---: |
| meshing (10 cases) | 2.00 |
| `check_k0d_mesh.py` mesh reader | 0.50 |
| `mark_done_k0d.py` + `analyse_k0d.py` + `--selftest` | 1.00 |
| dual-scheme extraction (§A1.3b) | ≤ 8.00 |
| **`I` = instruments, bounded** | **11.50** |

**The check that this is the right enumeration:** the first three lines sum to
**3.50**, which **reproduces §8's frozen `instruments, bounded | 3.50` line
exactly.** The frozen line is therefore accounted for term by term, and the only
new term is the dual-scheme extraction the ruling itself added.

**The `12.00` that appears in §A1.4's arrangement table is NOT reproducible from
§A1.4's own enumeration.** `3.50 + 8.00 = 11.50`; the remaining **0.50 is
unexplained** and no line of §A1.4 accounts for it.

### A2.2b The registered ceiling

The registered structure is `CEILING = 2S (first pass at the ceiling rate) + S
(continuation reserve) + I = 3S + I`, with the solver subtotal
**`S` = 912.38 core-min** after `M1_m_seed`'s 85.27 line (§A1.4).

```
  CEILING = 3 * 912.38 + 11.50 = 2 737.14 + 11.50 = 2 748.64 core-min
```

| figure | status |
| --- | --- |
| **2 748.64 core-min** | **REGISTERED CEILING, current, from `3S + I` at `I` = 11.50** |
| 2 749.14 core-min | **SUPERSEDED.** It stands in §A1.4's arrangement table and on the board at `docs/LAB_STATE.md`, and it carries the unexplained 0.50 of §A2.2a. **Recorded as superseded with its reason, not deleted.** |
| 2 484.84 core-min | **SUPERSEDED** — the v1.0 §8 cap, raised here. It predates `M1_m_seed` and the dual-scheme extraction and could never have held them (§A1.4). |

**The POINT is unchanged at 922.71 core-min** (§A1.4).

**Derived dollars at the owner-reported $0.0513/core-h — DERIVED, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5; this box cannot read its own billing):

```
  CEILING  2 748.64 / 60 = 45.8107 core-h  x $0.0513 = $2.3501   (9.40 % of $25)
  POINT      922.71 / 60 = 15.3785 core-h  x $0.0513 = $0.7889   (3.16 % of $25)
```

**`cost_basis`:** the per-cell-iteration rate is **MEASURED** (K0cS pilot on this
box, 2026-08-18). The $0.0513/core-h rate is **REPORTED-BY-OWNER**. The dollar
figures are **DERIVED, NOT MEASURED**. The `C_lam` 0.75 laminar scale factor, the
1.6× developed-flow contingency, the §9.2 memory estimates and the ≤ 24 core-s
per extraction remain **named calibration items** and none is called measured.

**The POINT against both ceilings, stated both ways so no reader has to guess
which denominator was used:**

```
  922.71 / 2 748.64 = 33.57 %   (against the ceiling registered here)
  922.71 / 2 484.84 = 37.13 %   (against the SUPERSEDED v1.0 cap)
```

**A CORRECTION MADE VISIBLY:** the supervisor's ruling as transmitted gave *"34 %
of even the OLD ceiling"*. **34 % is the fraction of the NEW ceiling (33.57 %);
against the OLD cap it is 37.13 %.** Both are recorded. **Neither reading changes
the conclusion**, which does not depend on the denominator: **what never fit was
the worst-case envelope, never the expected run.**

### A2.2c A cap is a RUNAWAY GUARD, not a budget gate

Under Sanaa's directive of 2026-08-25, **a case reaching its cap is REPORTED TO
THE SUPERVISOR, who decides** — extended by dated amendment if the work is sound,
stopped only if it is genuinely stuck, diverging or looping. `build_k0d.py`'s
header already states this correctly and is left as it stands. **Standing rule
12's "an overrun stops the run" is not thereby retired**: the run still stops at
the cap; what the directive changes is that the stop is a report to a decision,
not an automatic abandonment.

### A2.2d Neither concession of §A1.4 is taken

**`M1_m_seed` STAYS AT L2 AND STAYS IN THE RUNG.** Moving it to L1 would fit
inside the old cap (43.50 instead of 85.27) and is **REJECTED**: a control on a
different mesh **confounds mesh sensitivity with seed sensitivity**, which is not
the instrument §A1.2b registered. It is the planted-zero principle applied to
initial conditions — a control that varies two things at once measures neither.
**The continuation reserve is likewise not denied to it.**

---

## A2.3 AN INSTRUMENT DEFECT IN `check_k0d_mesh.py` CONDITION C, AND ITS REPAIR

**This section exists because condition C as frozen was DESCRIBED as reading from
disk and DID NOT.**

### A2.3a The defect, stated exactly

`check_k0d_mesh.py`'s module docstring asserts *"refusal conditions A-G, every
one READ FROM DISK"*. **That assertion is FALSE for condition C.** In `main()`
the call is `condition_C(None, LEVELS[lo], None, LEVELS[hi])` — **both mesh
arguments are `None`** — and the body computes its refinement ratio from the
hard-coded `LEVELS` specification constants. **At run time condition C is a
tautology over the script's own constants and cannot fail on any real mesh.**

**Why a passing selftest hid it:** the selftest's condition-C "FIRES" check
plants into a **modified specification** — `dict(LEVELS["L2"], nB=400)` — **not
into a modified mesh.** It is a planted control planted **into the wrong
channel**. It proves the arithmetic reacts to its own constants; it proves
nothing about the instrument's ability to see a mesh.

**Both selftests PASS and `scripts/check_grader_self_blindness.py` reports both
scripts clean on both probes. A GREEN SELFTEST IS NOT A GREEN INSTRUMENT**, and
that is the general lesson this section records.

### A2.3b The hole is exploitable, not theoretical

A mesh that **redistributes cells between blocks A / B / C** while holding
`Ny = nA + nB + nC` and `Nx * Ny` fixed:

- **passes condition A** (total cell count, genuinely read from disk — unchanged);
- **passes condition B** (per-slot resolution, tested with `>=` minimums, so a
  LARGER slot passes);
- **is never looked at by condition C.**

**Block B is the cavity interior.** Such a mesh would be **under-resolved in the
cavity** and **nothing in the instrument would catch it**. **Condition C
underwrites the refinement ratio that the entire Roache triple rests on**
(standing rule 5), so a condition C that cannot see the mesh puts every observed
order and every GCI on this rung on an unchecked footing.

### A2.3c The repair, registered

**Required before any solver fires:**

1. **Condition C counts each block's cells FROM THE MESH.** For a level's
   already-read `y_lines`, cells are counted in each of the three registered
   `BLOCK_Y` bands with `_count_between` — the same disk-reading helper condition
   B already uses; `Nx` is taken as `len(x_lines) - 1`; each block's 2D cell count
   is formed from the mesh; and the linear refinement ratio between consecutive
   levels is computed from **mesh-derived counts, never from `LEVELS`.**
2. **The specification check is KEPT and LABELLED for what it is.** Verifying that
   the REGISTERED table scales by 1.40 is worth doing — it is simply **not a check
   on the mesh**. The two are reported **separately**, so no reader can mistake
   one for the other.
3. **The planted control plants into the MESH.** A synthetic mesh is built with
   cells redistributed between blocks (`nB` reduced, `nA`/`nC` raised by the same
   total) so that `Ny`, `Nx*Ny` and **both** slot minimums still hold, and the
   selftest **asserts repaired condition C REFUSES it while conditions A and B
   both stay quiet.** That assertion **is** the proof the hole is closed. If A or
   B fires on the synthetic mesh, the control is wrong and the proof is not made.
4. **The module docstring is corrected.** An instrument may not assert something
   false about itself.
5. **Condition C is not in `judge()`**, so a `--case` invocation never evaluates
   it. A single-level invocation must **say plainly that C was not evaluated**
   rather than silently omitting it. **A check omitted in silence reads as a check
   passed.**
6. **All selftests and `scripts/check_grader_self_blindness.py` are re-run after
   the repair**, and the rung does not fire unless they are clean **after** it.

### A2.3d This tightens and cannot loosen

Repaired condition C **adds** a refusal channel that reads the mesh and **removes
none**. It can turn a mesh that would have passed into one that is refused; it
can never turn a refusal into a pass. **No graded band, threshold or label is
touched**, and no number this rung will produce is changed by the repair — only
the set of meshes allowed to produce one.

---

## A2.4 WHAT THIS RUNG CAN AND CANNOT EARN — stated plainly, and NOT a reason to withhold the run

**§0 stands, unsoftened.** The primary — Blay, D., Mergui, S. and Niculae, C.
(1992) — is **`NOT OBTAINED`**, and **no graded verdict against the reference is
reachable while that holds.**

**Sanaa settled the `V`/`P` question on 2026-08-25: *"a. Uphold."* `V` and `P`
are SEPARATE COLUMNS and one artifact cannot discharge both.** Therefore:

| column | reachable on this rung | why |
| --- | --- | --- |
| **`V`** | **YES** | verification is a property of the numerics and the grid, measurable without any reference |
| **`G`** | **YES** | a **CONVERGING three-level Roache triple** with observed order and GCI at `Fs = 1.25` is a **grid property**, measurable without any reference |
| **`P`** | **NO** | prediction against the primary is unreachable while Blay 1992 is `NOT OBTAINED` |

**The rung verdict is therefore `GATE REACHED`, naming `P` as the unreached
column. It can never read `HOLDS` in this state.** Nobody may later read a
completed run of this rung as a graded result against the reference.

**Obtaining Blay 1992 is from OUTSIDE THE BOX, is Sanaa's alone (standing rules 7
and 8), and IS NOT TO BE ATTEMPTED by any agent.**

**`V` and `G` are exactly the columns this lab is short of. That is a reason to
RUN this rung, not a reason to withhold it.** A rung that cannot reach `P` still
produces the solves, the convergence histories, the achieved `y⁺`, the five
guards, the Roache triples and the discrimination control — every one of which is
an artifact this lab keeps.

**Sanaa's grid ruling, recorded as received:** *"A converging three-level family
with observed order and GCI is the lab's gate standard (Roache-standard
minimum). More levels are a research option, never a gate requirement."*
**It relaxes nothing.** K0d's `L1`/`L2`/`L3` family is **exactly three** —
**confirmed, not extended.** Standing rule 5 continues to bind in full: a triple
that is not `CONVERGING` is **`NOT A RESULT`**, whatever its value, and no GCI is
quoted when the three values are not monotone.

---

## A2.5 CORRECTION: **K0d IS NOT `BLOCKED` ON AN OVER-DETERMINED `Ra`**

**A claim standing elsewhere in this repository is wrong, and this section
corrects it in the document that actually settles the question.**

`docs/campaigns/T-family/THERMAL_SATURATION_QUEUE_2026-08-25b.md` §3 states that
K0d *"MUST BE STRUCK FROM THE SCHEDULE"* because its defining parameter is
over-determined, and commit `107489e4` carries that claim in its subject line.
**That reading cites `docs/campaigns/F14-cooling-ladder/K0d_FIRE_RULING_2026-08-25.md`,
which is SUPERSEDED.**

**THIS DOCUMENT EXISTS BECAUSE OF THAT FIRE RULING, AND IT DISSOLVES THE
CONTRADICTION STRUCTURALLY RATHER THAN PATCHING IT:**

- **§1.1** registers the fluid state **once and consistently**: `T_ref` = 298.00 K;
  **`β` = 1/298 = 3.3557047e-03 K⁻¹ BY IDENTITY** — in a Boussinesq air model `β`
  is **not a free parameter**, it is the reciprocal of the registered reference
  temperature; `ν` = 1.569e-5 m²/s. **`AMENDMENT 5`'s rejected
  `β = 3.26577e-3` is `1/306.21`**, an **8.06 K internal contradiction inside the
  one coefficient Boussinesq validity rests on** — which is why it is
  **rejected**, not merely disagreed with.
- **§1.3** is the structural repair, in its own registered heading: **"`Ra` IS
  DERIVED AND REPORTED. IT IS NOT A TARGET, AND NO GATE DEPENDS ON MATCHING IT."**
  `Ra` = **2.135970e9**, derived from `(g, β, ΔT, H, Pr, ν)`. The **+0.2803 %**
  residual against the published 2.13e9 is **disclosed and explained**: the
  published figure was taken at **ΔT = 20.5 K** (Oulghelou 2020, `θ_hot` = 35.5 °C
  against `θ_cold` = 15 °C) while this rung runs — and has always run — at
  **ΔT = 20.0 K**. §1.3's own words: *"A 0.28 % residual against a target taken
  at a different `ΔT` is not a defect to be closed; closing it was the defect."*

**There is ONE registered `(ν, β, T_ref)` triple and `Ra` is an OUTPUT. The
over-determination is gone.** `build_k0d.py` already carries exactly those values
(`NU = 1.569e-05`, `BETA = 3.3557047e-03`, `TREF = 298.00`).

**The real blocker was never `Ra`. It was the four `REGISTRATION_GAPS` of §A2.1**,
on which the builder refused correctly — and they are closed above.

**`K0d_FIRE_RULING_2026-08-25.md` and the T-family queue document were NOT
edited by this amendment.** An unexpected or mistaken record in another team's
committed file is **inspected, never reverted** (standing rule 10). The
correction is made **here**, in the frozen registration that governs the
question, and referred to the supervisor to correct the board.

---

## A2.6 WHAT THIS AMENDMENT DID NOT DO — each stated explicitly

- **No GATE moved.** The ten graded rows, the thirteen stations, the five guards,
  the verdict ladder, Roache triple gating and the planted-zero control are
  untouched.
- **No BAND, THRESHOLD or LABEL moved.** Every band adopted in §4 is
  byte-unchanged.
- **The physics did not move.** `ν` = 1.569e-5, `β` = 1/298, `T_ref` = 298.00 K,
  `Pr` = 0.71, `Pr_t` = 0.85, `ΔT` = 20.0 K, `Ra` = 2.135970e9
  derived-and-reported, and the first wall-cell column of §5.1 all stand exactly
  as registered.
- **The CAP WAS RAISED, and that is stated rather than buried**: 2 484.84 →
  **2 748.64 core-min** (§A2.2). It is legal **only** because no K0d compute has
  run (§A2.0) and it is the supervisor's ruling, `[lab-attributed]`.
- **The POINT did not move**: 922.71 core-min.
- **The rung count did not move**: **ten** cases — `M1_c`, `M1_m`, `M1_f`,
  `M2_c`, `M2_m`, `M2_f`, `C_lam`, `B_hi`, `I_hi`, `M1_m_seed`. **Serial,
  `ranks = 1`, asserted and not assumed.**
- **The grid family did not move**: **exactly three levels**, `L1`/`L2`/`L3`.
- **NOTHING WAS LAUNCHED BY THIS AMENDMENT.** No case directory, no mesh, no
  solver, no pid. **Zero core-minutes.** Rule 12's estimate-versus-actual
  calibration is **not triggered**, because no process completed.
- **No other repository file was edited** — not
  `K0d_FIRE_RULING_2026-08-25.md`, not the T-family queue document, not
  `docs/LAB_STATE.md`, not `docs/DOCKET.md`, not `docs/LESSONS.md`, not
  `docs/COST_CALIBRATION.md`. **`scripts/append_record.py` was not used and no
  lesson, docket or record id was pre-assigned or reserved.**
- **Nothing was sent** (standing rule 7). Submissions remain **PARKED**. Nothing
  was fetched from outside the box (standing rule 8).
- **No permission setting, `CLAUDE.md` or `.claude/` configuration was touched**
  (standing rule 9).

*Amendment written by a heat-transfer lane on the supervisor's gap, ceiling and
condition-C rulings, 2026-08-25, before first compute. Zero core-minutes spent
in writing it.*
