# K2b-pilot — the rack-row module as a 2D vertical slice

Campaign F14, rung K2b. Executed 2026-08-18 against
`K2a_RACK_ROW_MODULE_SPEC.md` section 6 under three authorisations: **60
core-minutes for the 2D pilot**, then **1.4 for a 3D coarse cost probe** and
**20 to finish control C3**. Spend: **65.4 of 81.4 core-minutes; 16.0 returned
unspent**, itemised in section 9.

**The 3D graded pair remains unrun and unauthorized.** Section 9 now carries a
*measured* rate rather than an assumed one, and the estimate it supports is a
number to decide against, not a request.

Section 11 records a repair to the **standing** convergence criterion that this
rung's own data forced, and which is lab-wide rather than local to K2b.

---

## 0. What this rung is and is not

K2a section 6 puts the pilot's status in its own sentence and it is carried here
unchanged:

> It exists to shake down the BC coupling, the monitor wiring and the
> heat-balance path at ~1/15 the cost before the 3D module burns anything, and
> **it is a capability case in the K0a/K0b sense — never a result.**

Nothing below is a validation of anything. No number here is compared against a
measurement of a real facility, because no such comparison is in scope — that is
K2c's gate, and K2c has not run. The internal name for this work is **F14**;
nothing in it reaches the website or any application material.

Every thermal claim below carries its regime numbers and its heat-balance
closure, per the campaign's standing requirement.

---

## 1. What ran

Seven single-core `buoyantBoussinesqSimpleFoam` solves plus one timing probe,
k-ω SST throughout, on the 2D vertical slice built by `K2b_runs/build_k2b.py`.

| case | what it is | cells | iterations | core·min |
|---|---|---:|---:|---:|
| `K2bP_coarse` | the pilot at the spec's defaults: tile supply exactly matches rack demand | 46,400 | 9,000 | 13.46 |
| `K2bP_under` | tile supply at 70 % of rack demand — spec section 9's own imbalance parameter | 46,400 | 5,000 | 8.03 |
| `K2bP_fine` | the same balanced case at 1.5× per direction, capped at the budget line | 104,400 | 1,500 | 6.66 |
| `K2bP_C1_g0` | control C1: gravity off. Restart twin of `K2bP_under` | 46,400 | 800 | 2.76 |
| `K2bP_C2_dT13` | control C2: the ΔT plant moved +10 % to 13.2 K. Restart twin | 46,400 | 800 | 1.22 |
| `K2bP_C3_plant` | control C3: a planted volumetric source of 500.000 W. Restart twin | 46,400 | 5,000 | 6.63 |
| `K2bP_C3b_noplant` | C3's negative twin: identical, no `fvOptions` | 46,400 | 5,000 | 6.88 |
| `K2b3D_probe` | the 3D coarse cost probe — 4 racks, open row ends, 200 iterations | 132,840 | 200 | 1.12 |

Geometry, one rack pitch deep (Δx = W_r = 0.60 m) so that per-slice flows **are**
per-rack flows and no scaling factor is introduced anywhere:

```
 z=2.70  +---------------------------------------------+  ceiling / RETURN
         |                    .....RETURN.....         |
 z=2.00  +--------------+#####+------------------------+
         |  cold aisle  #RACK#      hot aisle          |
         |  rack_in --> #####| --> rack_out            |
 z=0.00  +-----[TILE]---+####+--------------------------+  floor
         y=0         0.6   1.2   2.3  2.6   3.2      3.5
```

Every surface carries the spec's section 3 boundary condition. The rack interior
is an **unmeshed void**: `rack_in` is a `flowRateOutletVelocity` face,
`rack_out` a `flowRateInletVelocity` face whose temperature is
`outletMappedUniformInlet` mapping `rack_in` with `offset` ΔT_rack. That is the
spec's section 1 abstraction and nothing about a server exists in the model.
`checkMesh` reports `Mesh OK` on both meshes, max non-orthogonality **0**, max
skewness **2.49e-13**, max aspect ratio **1**.

### Regime numbers at the defaults

Arithmetic on the case's own dictionary values (VERIFIED by calculation), not a
measurement:

| group | definition | value | reading |
|---|---|---:|---|
| Re_tile | U_tile·s_t/ν = 0.9722·0.6/1.589461e-5 | **3.67e4** | turbulent supply jet |
| Re_rack | U_face·W_r/ν = 0.2917·0.6/1.589461e-5 | **1.10e4** | turbulent rack stream |
| Ri_tile | g·β·ΔT·s_t/U_tile² | **0.249** | mixed convection at the tile |
| Ri_rack | g·β·ΔT·H_r/U_face² | **9.23** | buoyancy-dominant at the rack faces |
| Ra_H | g·β·ΔT·H³/(ν·α), α = ν/Pr | **2.99e10** | fully turbulent natural convection at room scale |

Fluid from `K0c_runs/Ra1e5_m128/constant/transportProperties` at HEAD:
ν = 1.589461e-05 m²/s, β = 3.333333333e-03 1/K, TRef = 300.0 K, Pr = 0.71.
**Prt = 0.85**, read from the case's own `constant/transportProperties` and
recorded per solve per the physics rules — and on this module it **does** enter
the answer.

---

## 2. The four establishing measurements

### (a) The case runs

Both meshes build and both solve with no divergence, no clipping and no
floating-point trap. `checkMesh` OK on both. The solver's own `Time =` count
matches the requested `endTime` on every case that ran to it. Boundary
conditions, function objects and the fvOptions plant are all constructed by the
solver and witnessed in its log (section 5).

### (b) Recirculation structure appears — and at balanced supply it does not

This is the pilot's most consequential finding and it is a **negative one first**.

| case | tile provisioning | θ_in = (T_in − T_sup)/ΔT | θ_out | implied recirculated fraction r |
|---|---|---:|---:|---:|
| `K2bP_coarse` | 100 % | **0.0071** | 1.0071 | **0.0070** |
| `K2bP_under` | 70 % | **0.4321** | 1.4326 | **0.3020** |
| `K2bP_C1_g0` | 70 %, g = 0 | 0.3159 | 1.3155 | 0.2398 |

At balanced supply the 2D slice is **contained**: the tile delivers exactly what
the rack draws, there is no deficit to make up, and across 9,000 iterations the
rack inhales 0.085 K of its own exhaust. θ is computed, it is correct, and it
**cannot move** — which is KV1b's degenerate-control defect wearing a new face.
It would have been easy to report "recirculation index measured, θ ≈ 0" as an
instrument reading when it is a construction.

Under-provisioning the tile by 30 % — spec section 9's own sensitivity parameter,
not a new one — forces the rack to draw 0.105 of its 0.35 m³/s from the room. The
**a-priori** prediction from that deficit alone is r = 0.105/0.35 = **0.3000**.
The solve's own mixing relation, r = 1 − 1/θ_out read off the field, gives
**0.3020** — agreement to **+0.67 %** between an independent prediction and the
measurement.

**What this establishes.** The module represents recirculation; θ is a live
instrument on it; and spec section 4's steady-mixing relation θ_out = ΔT/(1−r)
holds on this geometry to sub-percent. **What it does not establish.** Anything
about whether the aisle flow field resembles a real room's. That is K2c's gate
and this rung does not touch it.

### (c) Per-rack inlet-temperature extraction works

The graded quantity of spec section 7 row 1 — **mass-flow-weighted T over
`rack_in`** — is printed by the running solver every 50 outer iterations and is
read back from the log alone by `K2b_runs/analyse_k2b.py`. `postProcessing/` is
`.gitignore`d and is deliberately not a source. With N = 1 in the slice this is
T_in,max, the S13 monitored quantity for the module.

Spec section 3.3 mandates printing the mass-flow-weighted and area-weighted
averages of the same face once and showing their difference is below the gate
resolution. Measured:

| case | T_in mass-weighted | T_in area-weighted | difference | as % of ΔT_rack |
|---|---:|---:|---:|---:|
| `K2bP_coarse` | 289.085107 K | 289.205849 K | −1.207e-01 K | **−1.01 %** |
| `K2bP_under` | 294.185416 K | 293.782445 K | +4.030e-01 K | **+3.36 %** |
| `K2bP_C1_g0` | 292.790573 K | 294.742765 K | −1.952e+00 K | **−16.27 %** |

**The difference is not below any gate resolution.** On the recirculating case it
is 3.4 % of the rack rise and on the forced-convection twin it is a sixth of it.
The two averages are different quantities on this geometry and the choice between
them is a reportable modelling decision, not a rounding question. Section 7.1
records why the spec expected otherwise and why its stated remedy pointed the
wrong way.

### (d) The heat balance closes

`scripts/heat_balance.py` with `--allow-advective --allow-turbulent
--length 2.7`, at the case's own TRef = 300 K datum, against the governed
`heat_balance_tol_pct` of 0.5 %:

| case | iteration | imbalance | auditor exit | verdict |
|---|---:|---:|---:|---|
| `K2bP_under` | 1,000 | 31.0420 % | 1 | FAIL |
| `K2bP_under` | 3,000 | 3.7812 % | 1 | FAIL |
| `K2bP_under` | **5,000** | **0.1272 %** | **0** | **PASS** |
| `K2bP_coarse` | 500 | 17.2486 % | 1 | FAIL |
| `K2bP_coarse` | 2,500 | 1.5770 % | 1 | FAIL |
| `K2bP_coarse` | 5,000 | 0.5244 % | 1 | FAIL |
| `K2bP_coarse` | 7,000 | 0.8020 % | 1 | FAIL |
| `K2bP_coarse` | 9,000 | 0.7857 % | 1 | FAIL |
| `K2bP_fine` | 1,500 | 2.6632 % | 1 | FAIL |

**Closure is established on `K2bP_under` at 0.1272 %.** Per-patch at that point,
in watts into the domain: `tile` −3151.88, `return` −1768.75, `rack_in` +2380.12,
`rack_out` +2534.26, and **all five wall rows exactly zero** (adiabatic). Heat in
4.914376e+03 W, net −6.252348e+00 W. Boundary mass imbalance 0.0649 %, inside the
same governed band that `heat_balance_open_case_gates_mass_imbalance` requires
before the enthalpy ledger means anything at all.

**`K2bP_coarse` never closes, and that is the more interesting half.** Its
imbalance bottoms at 0.5244 % at iteration 5,000 and comes back up to 0.7857 % at
9,000 — while its S13 monitor reads 0.00101 %. Section 4 shows why, and it is not
a defect in the audit.

---

## 3. The Boussinesq span against the limit

`docs/physics_rules.yaml` block `thermal` carries `boussinesq_beta_dT_max: 0.1`,
reached at **ΔT = 30.0 K exactly** at TRef = 300. The quantity the limit binds is
the **domain span**, not the rack rise, and spec section 4 makes an in-run
`fieldMinMax` span check mandatory for that reason. It ran on every case **at
every monitor sample**, not only at the end.

| case | ΔT_rack | final span | β·span | worst span (iteration) | β·span worst | breached |
|---|---:|---:|---:|---:|---:|---|
| `K2bP_coarse` | 12.0 K | 12.0864 K | 0.040288 | 12.1265 K (7,000) | 0.040422 | **no** |
| `K2bP_under` | 12.0 K | 17.6268 K | 0.058756 | **17.7694 K (2,300)** | **0.059231** | **no** |
| `K2bP_fine` | 12.0 K | 12.0000 K | 0.040000 | 12.0551 K (1,000) | 0.040184 | **no** |
| `K2bP_C1_g0` | 12.0 K | 17.1082 K | 0.057027 | 17.6084 K (50) | 0.058695 | **no** |
| `K2bP_C2_dT13` | 13.2 K | 18.9471 K | 0.063157 | 18.9471 K (800) | 0.063157 | **no** |
| `K2bP_C3_plant` | 12.0 K | 20.8873 K | 0.069624 | 21.3000 K (650) | 0.071000 | **no** |

**Nothing breached, and the check was still worth running.** On `K2bP_under` the
span peaked at iteration 2,300 and fell back 0.14 K; on `K2bP_C3_plant` it peaked
at 650 and fell back 0.41 K. An end-of-run-only reading would have reported a
smaller number for the same run in both cases. The instrument was exercised where
a breach would have been visible **only** mid-run.

### The measured recirculation moves the admissibility line into the spec's own default band

At the measured r, the domain span is ΔT_rack/(1−r), so the 30.0 K limit is
reached at ΔT_rack = 30.0·(1−r):

| case | measured r | ΔT_rack on the 30.0 K line |
|---|---:|---:|
| `K2bP_coarse` (contained) | 0.0070 | **29.79 K** |
| `K2bP_C1_g0` (g = 0) | 0.2398 | **22.81 K** |
| `K2bP_under` (70 % provisioned) | 0.3020 | **20.94 K** |
| `K2bP_C3_plant` (70 % + 500 W room plant) | 0.3327 | **20.02 K** |

K2a's table admits ΔT_rack ≤ 20.0 K a priori and calls 20–30 K *conditionally*
admissible. **On this geometry the conditional band is entirely inadmissible and
the top of the unconditional band clears the limit by 4 %:** at r = 0.3020 a
20.0 K rack sits at a 28.65 K span, β·span = **0.0955** against a limit of 0.1.
Add the 500 W room plant and 20.0 K is already over the line.

**So the admissibility line is a property of the LAYOUT, not of the rack** — a
statement the spec could not make before this rung, and one the 3D module will
have to re-measure at its own r. The a-priori screen is necessary and, exactly as
the spec says, not sufficient; the pilot has now put a number on how little
margin it leaves.

### And passing the scalar limit is not the same as being inside the model

Rung **K2e** landed while this pilot was running (`K2e_RESULTS.md`, HEAD
`b845b603`) and it measures something this section cannot ignore: **the standing
`boussinesq_beta_dT_max: 0.1` is not one number, because the two models do not
separate on one quantity.** Measured on the de Vahl Davis cavity at Ra = 1e5
with only ε = β·ΔT moving, the **peak velocity separates first, in the bracket
ε ∈ (0.0333, 0.0500]** and diverges **first order**, D = 24.91·ε^1.005 %, while
the **Nusselt number is second order**, D = 6.355·ε^1.968 %, and is only 0.063 %
apart at ε = 0.1.

**K2b's graded quantities are of the first-order class, not the second.** θ and
T_in are recirculation and flow-structure quantities; they are not a wall heat
flux, and this module has no wall heat flux at all — every wall reads exactly
0 W. So every case here except the balanced one runs **past the bracket where
K2e measured the velocity field beginning to separate**:

| case | β·span | against K2e's velocity-separation bracket (0.0333, 0.0500] |
|---|---:|---|
| `K2bP_fine` | 0.0400 | inside the bracket |
| `K2bP_coarse` | 0.0403 | inside the bracket |
| `K2bP_C1_g0` | 0.0587 (worst) | **past it** |
| `K2bP_under` | 0.0592 (worst) | **past it** |
| `K2bP_C2_dT13` | 0.0632 | **past it** |
| `K2bP_C3_plant` | 0.0710 (worst) | **past it** |

Applying K2e's first-order law as an **indication of magnitude only** gives a
model-form deviation on the velocity field of ≈1.0 % at β·span = 0.040 and
≈1.8 % at 0.071. **That law does not transfer as a number and is not quoted as
one here:** K2e measured it on a laminar cavity at Ra = 1e5, and this module is
turbulent at Ra ≈ 3e10 with imposed through-flow. What transfers is the
*ordering* — flow structure first order, wall heat flux second — and the
ordering says that a rung graded on recirculation sits on the sensitive side of
the limit while a rung graded on Nusselt number sits on the protected side.

**Consequence for the 3D module, and it is a change to how the span check is
read.** Passing β·span < 0.1 is necessary and is now visibly not sufficient for a
recirculation-graded claim. The 3D module should either report its β·span
against the **0.05 velocity bracket** as well as against the 0.1 scalar limit, or
carry a compressible twin at one operating point. Neither is done here; the pilot
grades nothing and this is recorded so the 3D rung inherits it rather than
rediscovering it.

---

## 4. Convergence — and the sentinel that was watching the wrong room

The criterion is S13, inherited whole from `docs/physics_rules.yaml` block
`thermal`: **peak-to-peak spread** of the graded quantity over a **fixed window**
of 400 outer iterations sampled every 50, minimum 9 samples, threshold
`monitor_peak_to_peak_max_pct` = 0.02 %. Not a residual reading, not an endpoint
difference, not a fraction of the run. `analyse_k2b.py` reads all four thresholds
from the rules file and none is copied into any case script.

| case | window | quantity | mean | peak-to-peak | as % | S13 |
|---|---|---|---:|---:|---:|---|
| `K2bP_coarse` | 8,600–9,000 | **T_in** (the specified monitored quantity) | 289.085349 K | 2.929e-03 K | **0.00101 %** | **PASS** |
| `K2bP_coarse` | 8,600–9,000 | T_return (the room's only free boundary) | 300.980141 K | 1.196e-01 K | **0.03973 %** | **FAIL** |
| `K2bP_under` | 4,600–5,000 | T_in | 294.094692 K | 1.016 K | **0.34553 %** | **FAIL** |
| `K2bP_under` | 4,600–5,000 | T_return | 306.160028 K | 2.052e-01 K | **0.06702 %** | **FAIL** |

| `K2bP_fine` | 1,100–1,500 | **T_in** | 289.000000 K | **1.0e-07 K** | **0.00000 %** | **PASS** → **REFUSED** (§11) |
| `K2bP_fine` | 1,100–1,500 | T_return | 300.613670 K | 7.090e-01 K | **0.23585 %** | **FAIL** |

### The sharpest instance is the fine mesh, and it scored a perfect pass — until section 11 repaired the criterion

`K2bP_fine` at 1,500 iterations is manifestly nowhere near converged: its heat
balance reads **2.6632 %**, five times worse than the coarse mesh at the same
stage, and its free boundary is swinging **0.23585 %**. **On the specified
monitored quantity it scores 0.00000 % — the best score the criterion can
return.** T_in reads exactly 289.000000 K because at 1,500 iterations nothing has
reached the cold aisle at all; θ_in is exactly 0.0000 and the recirculated
fraction is exactly 0.

Two more instruments go the same way on that case, and for the same reason:

| instrument on `K2bP_fine` @ 1,500 | reading | why it is not a good sign |
|---|---:|---|
| offset readback | **12.000000000 K**, error **0.000e+00** | the rack face is uniform, so the mass- and area-weighted averages coincide exactly |
| averaging comparison | −8.1e-06 K, **−0.0001 % of ΔT** | same reason |
| S13 on T_in | 1.0e-07 K, **0.00000 %** | the quantity has not moved from its initial value |

**Every one of those is a best-possible reading produced by a field that has not
yet developed** — the same shape as KV1b, where a uniform field made the
advective sum identically zero and every mutation correctly invisible. A control
or a monitor is most flattering exactly where the case is least converged, which
is the opposite of informative, and none of these three numbers is offered here
as evidence of anything except that the wiring is connected.

### The specified monitored quantity certified a run that was still swinging

On `K2bP_coarse` the two sentinels differ by a factor of **39** on the same run,
at the same cadence, over the same window. T_in,max is the **failure-mode**
quantity for this module — it is the right thing to grade — but it sits in a
**contained** cold aisle, and an oscillation in the room's free outlet never
reaches it. The return temperature swings 0.12 K over the last 250 iterations and
`sum(phi)` on the return swings between 0.34971 and 0.35037 m³/s. That
oscillation is what the heat balance is reading at 0.7857 %, and S13 on the
specified quantity alone is blind to it.

**The three verdicts agree once the right quantity is read.** The run is not
converged; the specified monitor said it was. The same sentence holds on
`K2bP_fine` with the numbers a factor of 200 further apart.

### And the disagreement runs the other way too

| case @ 5,000 | S13 on T_in | heat-balance closure |
|---|---|---|
| `K2bP_coarse` | **PASS** 0.00136 % | **FAIL** 0.5244 % |
| `K2bP_under` | **FAIL** 0.34553 % | **PASS** 0.1272 % |

Neither criterion implies the other, and the counterexample exists in both
directions on the same module. On the recirculating case the ledger closes while
the monitored quantity is still swinging by a full kelvin, because closure is an
integral over the whole boundary and averages the swing away.

### The endpoint test would have passed the case the spread failed

On `K2bP_under`, over the same nine samples, the **endpoint difference is
0.06764 % — five times smaller than the 0.34553 % spread.** That is precisely the
aliasing the rules block describes, measured here on a case of this module's own
class rather than inherited from K0c.

### This failure was pre-registered

K2a section 5 risk 1 quotes the K2c primary reporting that steady-state
simulations of its 10-rack module "had difficulties converging due to
fluctuations in the flow field", and moving to transient averaging over 600 s.
**The pilot reproduces that at ~1/15 the cost of the 3D module**, which is what
the pilot was for. Running the steady solver longer will not fix an oscillation;
spec section 5 already prices the remedy (unsteady, 5–10×).

---

## 5. Controls — every one verified in the solver's own output

| control | kind | can it fail? |
|---|---|---|
| C0 ΔT offset readback | **reachability** | yes — reads 0 K on the BC's fallback branch |
| C0m mass ledger | **reachability** | yes — a mismatched face pair moves it |
| C1 gravity-off twin | **reachability**, value-level | yes — reads exactly 0 on a g = 0 case |
| C2 ΔT plant, +10 % | **reachability** | yes — reads 12.0 K if the offset is ignored |
| C3 planted 500.000 W source | **reachability**, noise-floor-limited | yes — readback travelled 155.55 → 536.47 W; **not landed**, see below |
| C3b negative twin | **discriminating** | it is what makes C3 mean anything |
| S15 fvOptions witness | **recognition** | yes — it reports the log, and it discriminates |

### C0 — the ΔT offset readback (reachability)

`T̄(rack_out) − T̄_ṁ(rack_in)` must equal ΔT_rack, printed by the running solver
every 50 iterations:

| case | measured | expected | error |
|---|---:|---:|---:|
| `K2bP_coarse` | 12.000002100 K | 12.0 K | **+1.75e-05 %** |
| `K2bP_under` | 12.005809400 K | 12.0 K | +4.84e-02 % |
| `K2bP_C1_g0` | 11.995426200 K | 12.0 K | −3.81e-02 % |
| `K2bP_C2_dT13` | **13.192727100 K** | **13.2 K** | **−5.51e-02 %** |
| `K2bP_C3_plant` | 11.998417900 K | 12.0 K | −1.32e-02 % |
| `K2bP_C3b_noplant` | 11.991572700 K | 12.0 K | −7.02e-02 % |

The residual on the converged `K2bP_coarse` is at the log's own 10-significant-
digit print precision, not at the boundary condition's; KV1a's +2.40e-08 % is not
reachable through a log at this precision and is not claimed. The larger
residuals elsewhere are the cases' own oscillation: the BC sets `rack_out` from
the mass-weighted average at the start of an outer iteration and the function
object reports both faces at the end of it, so a case still swinging by a kelvin
is read a fraction of a swing apart.

**This control can fail — but by construction, not by demonstration, and that
distinction is the one this campaign holds itself to.** The
`outletMappedUniformInlet` implementation has two branches (section 7.1) and the
fallback branch **drops the offset entirely**: a rack that adds no heat would then
read exactly like a converged rack, and this readback would print 0.000 K.
**No K2b case ever entered that branch.** `gSum(phi)` on a rack front face never
approached `SMALL`, so the readback has only ever been observed *passing*, and
"it can fail" rests on reading the source rather than on having seen it fail.
That is precisely the standard KV1b was held to and failed. The demonstration is
cheap — a case with a zero or sign-reversed rack flow rate — and it is filed as
**D391** rather than claimed here.

### C0m — the mass ledger (reachability)

`sum(phi)` on all four open patches, from the log:

| case | tile | return | rack_in | rack_out | net | as % of through-flow |
|---|---:|---:|---:|---:|---:|---:|
| `K2bP_coarse` | −0.350000 | +0.349710 | +0.350000 | −0.350000 | −2.898e-04 | 0.04141 % |
| `K2bP_under` | −0.245000 | +0.245387 | +0.350000 | −0.350000 | +3.866e-04 | 0.06495 % |
| `K2bP_C1_g0` | −0.245000 | +0.245000 | +0.350000 | −0.350000 | −2.351e-07 | **0.00004 %** |

Both imposed flow rates land on their dictionary values exactly, the rack pair is
internally balanced to the printed precision, and the free outlet carries the
remainder. All three pass the same governed 0.5 % band the enthalpy ledger rests
on.

### C2 — the ΔT plant, and the discriminating pair the spec predicted

K2a section 8 predicts of C2: *"that rack's outlet ledger row moves by 10 %, its
θ unchanged to first order — the discriminating pair."* Measured against its
parent `K2bP_under`:

| quantity | parent (ΔT = 12.0) | C2 (ΔT = 13.2) | change | prediction |
|---|---:|---:|---:|---|
| offset readback | 12.0058 K | **13.1927 K** | **+9.89 %** | +10 % ✓ |
| implied r | 0.3020 | 0.3033 | **+0.43 %** | unchanged to first order ✓ |
| domain span | 17.6268 K | 18.9471 K | +7.49 % | ΔT/(1−r) = 18.946 K ✓ |

Both halves of the prediction land: the plant moves by its planted amount and the
recirculation index does not move with it.

### C1 — the gravity-off twin, and why the log alone is not enough

`buoyantBoussinesqSimpleFoam` prints **`Reading g`** at line 79 of its log and
**never prints g's value**. The log alone is therefore a **recognition** control:
it proves the file was opened, not what was in it — and S15's whole content is
that a dictionary is not the referent.

The value-level witness used instead is the solver's own written fields. In this
solver `p = p_rgh + ρ_k·gh`, so `max|p − p_rgh|` over the internal field **is**
|g| times the domain height as the solver actually applied it:

| case | max\|p − p_rgh\| over 46,400 cells |
|---|---:|
| `K2bP_coarse` (g = −9.81 ẑ) | 26.786643 m²/s² |
| `K2bP_under` (g = −9.81 ẑ) | 25.995574 m²/s² |
| `K2bP_C2_dT13` (g = −9.81 ẑ) | 25.965920 m²/s² |
| `K2bP_C3b_noplant` (g = −9.81 ẑ) | 25.970026 m²/s² |
| **`K2bP_C1_g0` (g = 0)** | **0.000000 m²/s²** |

Exactly zero against ~26 on every buoyant case: the control both reaches the
momentum equation and demonstrates its own fail state. (The spread among the
buoyant cases is the Boussinesq ρ_k = 1 − β(T−TRef) varying with each case's own
temperature field, which is the coefficient the buoyancy term carries.)

The **physical** prediction K2a section 8 makes for C1 is *"cold-aisle
stratification collapses"*. Measured at the same 70 % provisioning: r falls from
**0.3020 to 0.2398, −20.6 %**, and T_in falls 1.395 K. The measured r is a
*thermal* mixing fraction, not a mass fraction — without stratification the
makeup air the rack draws is a cooler blend rather than a ceiling-pooled plume.
The direction is the predicted one.

This readback reads a written time directory, which is `.gitignore`d; the number
is reproduced by re-running the recipe in section 10, not by reading a tracked
file, and `analyse_k2b.py` says so in its own output.

### S15 — the fvOptions witness (recognition), and it discriminates

`heat_balance.py` reads the **solver log**, not the dictionary:

| case | `fvOptions in the SOLVER LOG` | dictionary |
|---|---|---|
| `K2bP_C3_plant` | **`constructed ['roomPlant']`** | `constant/fvOptions` present |
| `K2bP_C3b_noplant` | **`none`** | no `constant/fvOptions` |

And the solver log itself carries the construction at lines 88–94:
`Creating finite-volume options from "constant/fvOptions"` /
`Selecting finite volume options type scalarSemiImplicitSource` /
`Source: roomPlant` / `State: active` /
`- selected 46400 cell(s) with volume 4.35`.

### C3 — the plant, the size that makes it a control, and the honest verdict

KV1a planted **5.000e-03 W** into a duct whose ledger carried 0.146 W: the plant
was 3.4 % of the ledger and its recovery was a real measurement at
+2.40e-08 % error. **This room's ledger carries 4.914e+03 W.** The same 5 mW here
is **1.0e-06 of the ledger** — nine orders below the 0.5 % closure band and
several orders below the case's own closure noise in watts. **An instrument that
returned exactly zero would have "recovered" it.** That is KV1b's defect arriving
by a different route: not a degenerate *field*, a degenerate *size*.

The plant is therefore sized to **this** ledger at **500.000 W**, ≈10 % of the
rack load, so that the governed 0.1 % recovery tolerance is 0.5 W and the control
can fail. `K2bP_C3b_noplant` is byte-identical except that `constant/fvOptions`
does not exist, starts from the same seeded field and runs the same 800
iterations, so the recovered plant is the **difference of two ledgers at matched
state** and the closure error common to both subtracts out.

**Run to 5,000 iterations on both twins under a separate 20 core-minute
authorisation** (13.51 spent). The first pass, at 800 iterations, read 315.57 W
and was still climbing; the question was whether it converges on the plant.

| iteration | net, plant case | net, no-plant twin | recovered | error vs 500.000 W |
|---:|---:|---:|---:|---:|
| 1,000 | −311.0800 W | +42.2570 W | **353.337 W** | −29.33 % |
| 2,000 | −399.1559 W | +7.1338 W | **406.290 W** | −18.74 % |
| 3,000 | −496.2579 W | −35.8655 W | **460.392 W** | −7.92 % |
| 4,000 | −573.4445 W | −36.9751 W | **536.469 W** | **+7.29 %** |
| 5,000 | −454.9621 W | +11.3376 W | **466.300 W** | −6.74 % |

**It reaches the plant and then oscillates about it. It does not converge on
it.** The recovery crosses 500 W between iterations 3,000 and 4,000, overshoots
to +7.29 %, and falls back to −6.74 %. More iterations will not fix that, and the
reason is measurable rather than a guess:

> **The no-plant twin's own ledger net wanders by 48.313 W peak-to-peak** across
> iterations 2,000–5,000 (+7.134, −35.866, −36.975, +11.338 W). The governed
> recovery tolerance is 0.1 % of 500.000 W = **0.500 W**. **The noise floor is
> 97× the tolerance.**

**Verdict: the planted-source recovery control cannot be landed to its governed
tolerance on this geometry, and the obstruction is the case's unsteadiness, not
the instrument.** `K2bP_under` fails S13 at 0.34553 %; its ledger therefore
oscillates by tens of watts, and the matched-twin difference does not cancel that
because the plant perturbs the flow enough that the two twins no longer sit in
the same phase of the same oscillation. On a **steady** case the same control is
excellent — KV1a recovered its plant at +2.40e-08 % on a laminar duct.

**What C3 does establish, stated at the accuracy it supports:** the boundary
ledger recovers a planted volumetric source on the rack-row geometry **to about
7 %**, from a starting error of −68.89 %, moving monotonically toward the plant
across four decades of the run. That is a real result about the audit's
bookkeeping on this geometry and it is not a pass against the 0.1 % rule.
**The control is not degenerate** — its readback travelled from 155.55 W to
536.47 W — and it is not a pass. Both halves are reported. Filed at **D381** and
settled at **D388**, which supersedes D381's "needs ~16 more core-minutes": the
obstruction is not iteration count.

**Consequence for the 3D module:** a planted-source recovery control is only
worth its compute on a case that meets S13. On an unsteady one it should either
be run against a time-averaged ledger, or replaced by a control that does not
depend on ledger closure.

---

## 6. What closure means on this geometry — carried, not re-derived

K2a section 8 and `docs/physics_rules.yaml` section 4b state this, and it is
quoted rather than paraphrased because the wording is the point:

> **What closure DOES establish here.** With through-flow, the boundary ledger
> must net to zero **only at convergence** — the advective enthalpy flux is an
> independent contribution the discretisation does not force. So on this
> geometry a closure number **is** a convergence- and bookkeeping-sensitive
> measurement: it catches an unconverged energy field, a mis-set ΔT offset, a
> flow-rate mismatch between a rack's face pair, a patch omitted from the
> ledger, and the BC clamp silently limiting.
>
> **What closure does NOT establish here.** Circulation. A solve with the aisle
> flow structure entirely wrong — supply short-circuiting to the return,
> reversed aisle recirculation — still closes perfectly once converged, because
> closure tests conservation, not *where* the energy travelled. θ_i and T_in,i
> move by factors under those failures while closure does not move at all.
> Closure is therefore **necessary, never sufficient**, and no K2b sentence may
> cite it as validation evidence; validation is K2c's gate alone.

The convergence sensitivity is measured on this module rather than inherited:
**31.0420 % → 3.7812 % → 0.1272 %** at iterations 1,000 / 3,000 / 5,000 on
`K2bP_under`, with the auditor's own exit code flipping 1 → 0 across the 0.5 %
band. Set that beside K0b's **sealed** case, which read 0.0128 % at iteration 10
and never rose above 0.13 % at any iteration: one of those two numbers is
measuring the solution and the other is measuring the discretisation.

`MONITOR_STANDARD.md` **S16** exists to stop the inference this section forbids.
**No sentence in this document cites a closure number as evidence about a flow
field.** In particular, section 2(b)'s recirculation result rests on θ and on the
independent flow-deficit prediction, and on nothing in the ledger.

---

## 7. Where this departs from K2a, and why

### 7.1 The spec described the boundary condition's fallback branch as its normal one

Spec section 3.3 — the load-bearing row of the whole module — states:

> The face-averaging in the BC is area-weighted (`gWeightedAverage` over `magSf`
> in the source); the *graded* rack-inlet temperature in Section 7 is computed by
> function object as the **mass-flow-weighted** average of the same face, and on
> a patch with uniform imposed normal flow the two coincide up to the
> nonuniformity of the solved face flux — the analyser must print both once and
> show their difference is below the gate resolution, **or switch the grading to
> the BC's own area average**.

Read in the v2606 source this session —
`src/finiteVolume/fields/fvPatchFields/derived/outletMappedUniformInlet/outletMappedUniformInletFvPatchField.txx`,
`updateCoeffs()` — the boundary condition has **two branches**, and the
area-weighted one the spec quotes is the **fallback**:

```cpp
const scalar sumOutletPhi = gSum(outletPhi);
if (sumOutletPhi > SMALL)
    mapField.append(gSum(outletPhi*outletFld)/sumOutletPhi*fraction + offset);
else
    mapField.append(gWeightedAverage(outlet.magSf(), outletFld));
```

Three consequences, and the third is the one that matters:

1. **In normal operation the BC is mass-flux-weighted**, identical in kind to the
   graded quantity of section 7, so the units-of-averaging dispute the spec set
   out to close does not arise in the direction it expected.
2. **The spec's own fallback advice was the wrong way round.** "Switch the
   grading to the BC's own area average" would have moved the graded quantity
   *away* from what the BC computes. Measured cost of taking that advice:
   **0.403 K on `K2bP_under`, 3.4 % of the rack rise**, and −16.27 % of it on the
   g = 0 twin.
3. **The fallback branch appends no `offset`.** If the rack front face ever loses
   net outflow — reversed flow, a mis-signed flow rate — the rack rear inlet is
   handed the front face's own temperature with no ΔT at all, and a rack that
   adds no heat looks exactly like a converged one. The spec did not name this
   and it is the sharper hazard of the two.

The `T̄(rack_out) − T̄_ṁ(rack_in)` readback of section 5 is the control adopted
against it. Filed as **D380**.

### 7.2 The instrument prerequisite K2a named was not the one K2b needed

Spec section 8 makes KV1 the prerequisite for quoting any closure number, and
KV1 closed: the advective path is implemented and validated, a planted
5.000e-03 W recovered at +2.40e-08 % error.

**KV1 is a laminar rung** — `KV1_RESULTS.md` section 10 says so in its own words.
Every case in this module is turbulent by the spec's own section 5 regime
numbers, so `alphat` is non-zero, `alphaEff` varies over every patch, and
`scripts/heat_balance.py` **refuses outright, exit 2**:

> REFUSE: alphat is non-zero (max 1.047795e-02 m^2/s), so alphaEff varies over
> the patches and the laminar coefficient used here is wrong. The turbulent path
> exists behind `--allow-turbulent` but has never been calibrated; it is not
> trusted and its report is stamped UNVALIDATED.

**So every closure number in this document is produced through an uncalibrated
code path, and the spec's section 8 prerequisite did not cover it.** That is
stated first and bounded second, never the other way round.

**The bound is measured, not argued.** The uncalibrated path affects only the
**conductive** rows. Every wall in this module is adiabatic, and all five wall
rows read **exactly zero** at every audit; the only non-zero conductive rows are
`tile` and `rack_out`, whose temperatures are imposed:

| case @ iteration | total conduction | heat in | conduction as a fraction of the ledger |
|---|---:|---:|---:|
| `K2bP_under` @ 5,000 | −2.695e-02 W | 4.914e+03 W | **5.5e-04 %** |
| `K2bP_coarse` @ 9,000 | +2.216e-03 W | 4.912e+03 W | **4.5e-05 %** |

The UNVALIDATED stamp is correct and on this module it bites on 5.5e-04 % of the
ledger. **It would bite much harder on any variant with a non-adiabatic
envelope**, which spec section 3.1 already records as a modelling choice.
Calibrating the turbulent conduction path is a prerequisite for the *next*
variant, not for this one. Filed as **D378**.

### 7.3 Cell counts, properties, and two cases the spec did not name

- **Cell counts.** Spec section 6 names a 42 k / 95 k pilot pair. The meshes built
  are **46,400 / 104,400**, +10.5 % on each, because the cell size was chosen to
  divide every geometric interval exactly (12.5 mm coarse, 1/120 m fine) rather
  than to hit a round cell count. The ratio between them is exactly **1.5 per
  direction**, which is what K0c's convention requires. Well inside the spec's
  own 2× re-pricing trigger.
- **Properties.** Spec section 2.1 derives P_i for reporting at RECALLED
  ρ = 1.177 kg/m³, cp = 1006 J/kg/K. This build uses the pair every case the
  auditor has been calibrated against carries — ρ = 1.1614, cp = 1007.0,
  ρ·cp = 1169.5298 J/m³/K, from `constant/thermalAuditProperties` — so that the
  audited watts and the reported watts are the same watts. P_rack is then
  **4912.0 W** against the spec's 4973.1 W, a **+1.24 %** gap recorded rather
  than hidden. The Boussinesq solve sees neither: the primitive parameter is
  ΔT_rack, exactly as the spec requires.
- **`K2bP_under`.** Tile at 70 % of rack demand. That is spec section 9's own
  sensitivity parameter, not a new one, and section 2(b) records why the pilot
  could not have established its second establishing measurement without it.
- **`K2bP_C3b_noplant`.** C3's negative twin. Not in the spec's control list;
  added because KV1 established that a positive control without its negative
  twin cannot tell "the instrument recovered the plant" from "the instrument
  returns that number for anything".

---

## 8. What did not work

- **The balanced pilot cannot demonstrate recirculation.** Section 2(b). Not a
  bug — a property of a 2D slice with balanced supply, a full-height rack and no
  leakage. It scopes the 3D module: **on this geometry recirculation is produced
  by provisioning imbalance, and the 3D module's additional sources of it — row
  ends and finite row length — are exactly the things the slice cannot have.**
- **`K2bP_coarse` never closes its heat balance**, bottoming at 0.5244 % and
  returning to 0.7857 % by 9,000 iterations, because its free outlet is
  oscillating and its specified monitor cannot see it. Section 4.
- **`K2bP_under` does not reach S13**, and running the steady solver longer will
  not fix an oscillation. Pre-registered by K2a section 5 risk 1; remedy priced
  there at 5–10× (unsteady with statistical averaging).
- **C3's plant recovery cannot be landed to its governed tolerance on this
  geometry.** Section 5. Run to 5,000 iterations on both twins it reaches the
  plant and oscillates about it, best reading 466.300 W of 500.000 W, because
  the no-plant twin's own ledger wanders 48.313 W peak-to-peak against a
  0.500 W tolerance — a floor 97× the tolerance. Not an iteration-count
  problem. **D388**, settling **D381**.
- **The mesh pair is not a mesh-convergence result and is not offered as one.**
  The fine mesh ran 1,500 iterations against the coarse mesh's 9,000, at
  3.92e5 cell·iter/(core·s) for 6.66 core-minutes. Per the rules block's own
  1/N² statement, a 1.5× refinement needs ≈2.25× the iterations to reach the same
  convergence state — ≈20,000 here, **≈89 core-minutes for that mesh alone**
  against a 60 core-minute authorisation for the whole pilot. Its `endTime` was
  lowered twice, to 1,500, and the committed dictionary was lowered with it so
  the recipe reproduces the artefact rather than describing a run that was
  killed. **Comparing the two at unequal convergence would be reporting
  iteration error as mesh error**, the exact error K0c's Ra = 1e3 pair would have
  made. It is a build-and-cost demonstration and grades nothing.
- **y+ is below the wall-function band on every wall.** Spec section 6 names
  30–300 and requires it measured, not assumed. Measured on `K2bP_coarse` at
  9,000: per-patch averages **2.9 / 4.1 / 5.2 / 6.6 / 9.1**, maxima 10.7 to 24.8,
  minima as low as 0.165, and on the fine mesh they fall further still (3.3 to
  5.4). **Refining the mesh moves y+ away from the band, not toward it**, so this
  is a wall-treatment decision and not something more cells will fix. At a
  12.5 mm cell the near-wall cell is far too fine for
  standard wall functions. `nutkWallFunction` and `omegaWallFunction` blend
  continuously so the solve is stable and no claim here rests on a wall heat flux
  (every wall reads exactly 0 W), but **the wall treatment the mesh delivers is
  not the one the spec names**. Filed as **D379**.
- **A 100-iteration probe mis-priced the run by 1.9×.** The probe read
  2.70e5 cell·iter/(core·s) — the spec's section 10 planning rate exactly — while
  the full 5,000-iteration cases read 5.22e5 and 4.81e5. Mesh construction,
  `wallDist` and first-matrix assembly are amortised over 100 iterations instead
  of 5,000. Every figure in section 9 is priced at the long-run rate.
- **A cost record almost outlived the run it described.** `run_k2b.sh` wrote
  `COST.txt` only after the solver exited and never removed the previous one, so
  when `K2bP_C3b_noplant` was re-run from 800 to 5,000 iterations the stale file
  — `iterations 800`, `1.2083 core-min` — sat beside a log already past 3,460,
  and a wait armed on that file returned instantly against it. Repaired in the
  script; filed as **D390** with the general rule, since stale `HEATBALANCE_*`
  reports from audits aimed at not-yet-written time directories bit the same way
  in the same session.
- **One operational stumble, recorded because it is already a documented trap.**
  A `pkill -f "run_k2b.sh ..."` issued to stop the over-running fine mesh matched
  its own invoking shell and killed the command that issued it —
  `docs/USING_THIS_LAB.md` section 8.4, exactly as written there. The solver had
  already been stopped by PID resolved through `/proc/<pid>/cwd`, so nothing was
  lost but the shell; the working form in section 8.4 is the one to use.

---

## 9. Cost, and the 3D module — a proposal with a measured cost

### What this pilot spent

| item | wall s | core·min |
|---|---:|---:|
| 100-iteration timing probe | 17.2 | 0.29 |
| `K2bP_coarse`, first pass at 5,000 iterations (superseded) | 444.8 | 7.41 |
| `K2bP_coarse`, 9,000 iterations | 807.5 | 13.46 |
| `K2bP_under`, 5,000 iterations | 482.1 | 8.03 |
| `K2bP_fine`, first attempt, stopped at 767 iterations | ~219 | ~3.65 |
| `K2bP_fine`, second attempt, stopped at 1,014 by the budget line | ~309 | ~5.15 |
| `K2bP_fine`, final run to 1,500 | 399.4 | 6.66 |
| `K2bP_C1_g0` | 165.8 | 2.76 |
| `K2bP_C2_dT13` | 73.3 | 1.22 |
| `K2bP_C3_plant` | 66.2 | 1.10 |
| `K2bP_C3b_noplant` | 72.5 | 1.21 |
| 16 `heat_balance.py` audit passes, `blockMesh`/`checkMesh` | ~70 | ~1.2 |
| **subtotal, the pilot as originally authorised (60)** | | **≈ 52** |
| `K2b3D_probe`, authorised separately 2026-08-18 | 67.0 | 1.12 |
| `K2bP_C3_plant` re-run to 5,000, authorised separately (20) | 397.6 | 6.63 |
| `K2bP_C3b_noplant` re-run to 5,000, same authorisation | 412.7 | 6.88 |
| **TOTAL, all three authorisations** | | **65.4** |
| **total** | | **≈ 52** |

Against an authorisation of **60 core-minutes**. The fine mesh was stopped twice
rather than allowed to run to its original 4,000-iteration `endTime`, which is
where the remaining margin came from; the committed `endTime` was then lowered to
match what actually ran, so the recipe in section 10 reproduces the artefact.

### The measured rate

| case | cells | iterations | wall s | cell·iter/(core·s) |
|---|---:|---:|---:|---:|
| probe | 46,400 | 100 | 17.24 | 2.70e5 |
| `K2bP_coarse` (5,000) | 46,400 | 5,000 | 444.76 | **5.22e5** |
| `K2bP_coarse` (9,000) | 46,400 | 9,000 | 807.51 | **5.17e5** |
| `K2bP_under` | 46,400 | 5,000 | 482.09 | **4.81e5** |
| `K2bP_C2_dT13` | 46,400 | 800 | 73.32 | **5.06e5** |
| `K2bP_C3b_noplant` | 46,400 | 800 | 72.50 | **5.12e5** |
| `K2bP_fine` | 104,400 | 1,500 | 399.37 | **3.92e5** |
| `K2bP_C1_g0` | 46,400 | 800 | 165.82 | 2.24e5 |

Single core throughout, on a machine carrying up to **eight other agents' solves**
concurrently. `K2bP_C1_g0`'s 2.24e5 is that contention and is why the planning
figure below is **4.8e5** — the value the repeated 46,400-cell cases agree on —
and not the best of them. The 104,400-cell mesh runs at **3.92e5**, 19 % slower
per cell·iteration than the 46,400-cell mesh, which is the same
throughput-falls-with-case-size trend K0c measured across its four meshes; the
3D estimate below does **not** carry that extra derate and is optimistic by
roughly that much.

### The revised 3D estimate

Spec section 6's 3D cell counts at N = 4 are 0.20 M coarse and 0.70 M fine. The
iteration counts are the part this pilot changes: the coarse pilot needed
**9,000** iterations and still did not close, not the 5,000 the spec assumed, and
the 1/N² argument puts a 1.5× fine mesh at ≈2.25× that.

| item | cells | iterations | core·min at 4.8e5 | K2a section 10 said |
|---|---:|---:|---:|---:|
| 3D coarse | 2.0e5 | 9,000 | **62** | 167 |
| 3D fine | 7.0e5 | 20,000 | **486** | 933 |
| controls C1–C3 + twins, restart class | 2.0e5 | 800 × 5 | **28** | ~430 |
| **graded pair + controls** | | | **≈ 580** | ≈ 1,600 |
| sensitivity block, 6 coarse deltas at 9,000 | 2.0e5 | | ≈ 375 | ~1,000 |
| **everything specified** | | | **≈ 955** | ≈ 2,700 |

### THE DERATE IS NO LONGER AN ASSUMPTION — MEASURED 2026-08-18

The paragraph this section originally ended with said the derate was the only
remaining assumption and that a 200-iteration 3D coarse run would collapse the
range for ≈1.4 core·minutes. **That probe was authorised and run.**
`K2b3D_probe`: the full spec-default 3D module — N = 4 racks with per-rack
`rack_i_in`/`rack_i_out` face pairs each carrying `outletMappedUniformInlet`,
four supply tiles, ceiling return, k-ω SST, buoyancy on, **132,840 cells**,
`checkMesh` OK (non-orthogonality 0, skewness 5.92e-14, max aspect 1.048).

| | |
|---|---|
| measured | **3.968e5 cell·iter/(core·s)**, 200 iterations in 66.96 s = **1.12 core·min** |
| against the 2D measurement of 4.8e5 | **the real 3D+SST derate is 1.21** |
| against K2a section 10's planning rate of 1.0e5 | **K2a is 3.97× low** |

K2a derated 2.7e5 by an assumed **2.7**. The measured derate is **1.21** — the
assumption was pessimistic by a factor of 2.2, and going from a 2D slice to a
full 3D room with eight rack faces costs only 21 % per cell·iteration. Two
things explain most of it: the block-structured hex mesh has the same
per-cell face count in 3D as in 2D once the `empty` pair is replaced by real
faces, and the SST equations were already being solved in the 2D case.

### The 3D estimate, at the measured rate

| item | cells | iterations | core·min |
|---|---:|---:|---:|
| 3D coarse (spec's 0.20 M) | 2.0e5 | 9,000 | 75.6 |
| 3D fine (spec's 0.70 M) | 7.0e5 | 20,000 | 588.0 |
| controls ×5, coarse class, restart | 2.0e5 each | 800 | 33.6 |
| **graded pair + controls, at the spec's cell counts** | | | **697** |
| same, at the mesh this probe actually built (132,840 / 448,335) | | | **454** |
| spec counts, if the fine mesh needs only 9,000 iterations | | | **374** |

> **The range collapses to the LOW end: 374 to 697 core·minutes for the 3D
> graded pair with controls, against the 580–1,600 this document previously
> could not narrow.** The upper bound fell by more than half.

**And the remaining uncertainty has changed identity, which matters more than
the number.** The rate is now measured on the real geometry; what is left is the
**iteration count**, and only half of that is measured. The coarse figure of
9,000 comes from this pilot — and even at 9,000 the 2D coarse case had not
closed its heat balance, so it is a floor, not a converged count. The fine
figure of 20,000 is the 1/N² *inference*, never measured on anything. That
single unmeasured factor is what separates 374 from 697.

**Nothing further is requested here.** The graded 3D pair remains unauthorized,
and this section is the number to decide against, not a request.

### Four things the pilot says the 3D module must carry

1. **Two convergence sentinels, not one.** Section 4. The specified monitored
   quantity certified a run its own free boundary said was still swinging, by a
   factor of 39, and the heat balance agreed with the free boundary.
2. **A deliberate recirculation source.** Section 2(b). A balanced, contained,
   leak-free module reports θ ≈ 0 for a reason that is a construction, and its
   recirculation instrument is then dead on arrival. Whether the row-end margins
   (L_end = 0.60 m) supply enough is unmeasured and is the first thing a 3D
   coarse run should report.
3. **A plant sized to the 3D ledger, and its negative twin.** Section 5. Neither
   KV1's 5 mW nor this pilot's 500 W transfers without re-derivation.
4. **A turbulent-conduction calibration before any non-adiabatic envelope.**
   Section 7.2, filed as D375.

---

## 10. Reproduction

**Verified from a fresh temporary directory before this document was called
done, and the verification is stated exactly rather than claimed loosely.** A
replica holding only the files this rung tracks — no `constant/polyMesh/`, no
`0/`, no time directories, no `postProcessing/` — was built at the same relative
paths beside a copy of `scripts/` and `docs/physics_rules.yaml`, and every step
below was run in it. Steps 1, 3, 4 and 5 were executed to completion: step 1
exits 0 and rewrites the dictionaries; step 3 **refuses** correctly, both halves
(`seed_k2b.py` exits 1 with "no written time directory to seed from",
`run_k2b.sh` exits 2 with "no seeded 0/ directory"); step 4 reproduces the
reported numbers from the tracked logs alone; step 5 resolves the repository root
and the auditor from the run tree's own location. Step 2 was verified through
`blockMesh` (46,400 cells), `checkMesh` (`Mesh OK`) and 57 solver iterations
under a 12-second cap — **the full 41 core-minutes of solving was not re-run**,
because re-running it is the thing the authorisation is spent on.

```bash
cd docs/campaigns/F14-cooling-ladder/K2b_runs

# 1. write every case from the one table that defines them
python3 build_k2b.py

# 2. the two primaries and the recirculation bed
bash run_k2b.sh K2bP_coarse K2bP_under K2bP_fine

# 2b. the 3D coarse COST PROBE (200 iterations, ~1.1 core-min, grades nothing)
python3 build_k2b3d.py
( . /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
  cd K2b3D_probe && rm -rf 0 && cp -r 0.orig 0 && blockMesh > log.blockMesh 2>&1 \
  && checkMesh > log.checkMesh 2>&1 \
  && /usr/bin/time -f "%e s" buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam 2>&1 )

# 3. the controls are RESTART twins and must be seeded from their parent first
python3 seed_k2b.py
bash run_k2b.sh K2bP_C1_g0 K2bP_C2_dT13 K2bP_C3_plant K2bP_C3b_noplant

# 4. the measurements, read from the solver logs alone
python3 analyse_k2b.py K2bP_coarse K2bP_under K2bP_fine \
                       K2bP_C1_g0 K2bP_C2_dT13 K2bP_C3_plant K2bP_C3b_noplant

# 5. the closure audits.  heat_balance.py DELETES and rebuilds postProcessing/,
#    so never run this against a case whose solver is still running.
bash audit_k2b.sh K2bP_under  1000 3000 5000
bash audit_k2b.sh K2bP_coarse 500 2500 5000 7000 9000
bash audit_k2b.sh K2bP_C3_plant    1000 2000 3000 4000 5000
bash audit_k2b.sh K2bP_C3b_noplant 1000 2000 3000 4000 5000

# 6. the S13 repair, proved both ways and re-graded over all fourteen affected
#    cases (K0c's eleven and K2b's three). Reads the committed logs only.
cd ../../../..
python3 scripts/check_convergence.py \
  docs/campaigns/F14-cooling-ladder/K2b_runs/K2bP_fine/log.buoyantBoussinesqSimpleFoam \
  --monitor-regex 'weightedAverage\(rack_in\) of T = ([-0-9.eE+]+)' --json    # CANNOT_TELL
python3 scripts/check_convergence.py \
  docs/campaigns/F14-cooling-ladder/K2b_runs/K2bP_coarse/log.buoyantBoussinesqSimpleFoam \
  --monitor-regex 'weightedAverage\(rack_in\) of T = ([-0-9.eE+]+)' --json    # CONVERGED
```

**The auditor mutates the case it audits, and this rung is arranged so that costs
nothing.** `heat_balance.py` deletes and rebuilds `postProcessing/` and writes
its own function-object dictionaries into `system/` before removing them — the
defect class rung K2e filed as **L-118** on the same day, and whose sharpest
form was repaired at `e4a977ef` (**D375**: the audit was deleting the *whole*
`postProcessing/` tree, including the solver's own in-pass history, which is the
series this campaign's convergence criterion reads; twelve K2e cases lost it).
**This rung was hit by that defect too, and no grade of it depended on what was
lost.** Checked after the repair landed: every K2b case's `postProcessing/` now
holds only `hbAudit_*` directories — the solver's own `T_rack_in_mdot`, `Tspan`,
`phi_*` and `aisleProfiles` series are gone, destroyed by the audits run in
section 2(d). **Every graded series survives at full cadence in the tracked
solver log**, which is where S13 requires it to be read from and where this rung
read it: 180 monitor samples on `K2bP_coarse`, 100 on `K2bP_under`, 30 on
`K2bP_fine`, on both T_in and the domain span — the same samples every
peak-to-peak verdict in section 4 is computed over, nine per 400-iteration
window at interval 50. A reader can recompute every S13 verdict here from a
committed file. That is not luck: `postProcessing/` is `.gitignore`d and would
never have travelled, which is why `analyse_k2b.py` was written against the log
in the first place. Every measurement in
sections 2–5 above is read from `log.buoyantBoussinesqSimpleFoam`, which the
auditor never touches, and `analyse_k2b.py` reads only that log — its own
docstring says `postProcessing/` "is `.gitignore`d and is deliberately not a
source here". The audit reports committed with this rung were produced by the
auditor as it stood *before* `e4a977ef`; that repair changes only which
directories are removed and no computed quantity, so every closure figure above
is unaffected. Verified after the fact: no `hbAudit*` file survives
anywhere in the run tree outside `postProcessing/`, and every `system/` directory
holds its original four dictionaries and nothing else.

`constant/polyMesh/`, `0/` and every solved time directory are not tracked
(`.gitignore`, the K2b block) and are rebuilt by steps 2 and 3. Step 1 is
idempotent and rewrites only dictionaries. Step 3 **refuses** rather than
silently starting a control from `0.orig`. Step 5's script reads
`heat_balance.py`'s **own** exit status — piping it into `head` reports `head`'s
status, and that mistake has cost this lab a false pass before.

Approximate cost of a full reproduction: **≈55 core-minutes** — ≈41 for the 2D
set, ≈1.1 for the 3D probe, ≈13.5 for the C3 pair at 5,000 iterations each (the two stopped `K2bP_fine` attempts and the superseded
5,000-iteration `K2bP_coarse` pass are not part of the recipe).

---

## 11. The S13 repair — a criterion that scored perfectly on a field that never moved

Section 4 reported that `K2bP_fine` scored **0.00000 %** on S13 — the best score
the criterion can return — with its heat balance 2.6632 % out. That was reported
as a finding about the case. **It is a defect in the standing criterion**, it is
lab-wide, and it has been repaired there rather than worked around here.

### The defect

The raw samples, from the solver's own log, over the whole graded window:

```
289.0000002  289.0000002  289.0000002  289.0000001  289.0000001
289.0000001  289.0000001  289          289          289
```

T_in is sitting at **exactly the supply temperature**, 289.000 K, because the
cold aisle has not been reached. It moves by **1 unit in the last place of a
ten-significant-figure print** across 400 iterations. S13 asks *has the graded
quantity stopped moving?* and cannot answer that on a quantity that never
started — so it returned the most flattering answer available.

**This is the identity defect the physics rules already record for the
sealed-case heat balance, arriving in the convergence criterion.** K0b's
sealed-case closure was near-identity and therefore could not gate; here **a
quantity that cannot move scores perfectly on a test of whether it has stopped
moving.** Two of this rung's own controls read perfectly on the same case for
the same reason — the offset readback erred by 0.000e+00 and the
mass-versus-area comparison by −0.0001 %, both because the rack face was still
uniform.

### The repair

A spread that the log cannot **resolve** is now `CANNOT_TELL`, never a pass —
the same refusal `heat_balance.py` makes on an undefined imbalance ratio instead
of printing a flattering number. The spread is compared against the precision
the series is actually printed at, **measured from the samples themselves**
(the most precise sample fixes it, since OpenFOAM strips trailing zeros, so
`289` and `289.0000002` are the same ten-figure series). Below
`thermal.monitor_min_resolved_ulp` = **10** units in the last place, it refuses.

Landed in three places so every future thermal rung inherits it, not just this
one: `docs/physics_rules.yaml` (the governed threshold and its reasoning),
`docs/standards/MONITOR_STANDARD.md` **S13** (bumped to v1.11, no new rule), and
`scripts/check_convergence.py` (`print_resolution()` and the refusal in
`classify_monitor()`).

### The two-way proof

| case | spread | resolution | resolved ulp | verdict |
|---|---:|---:|---:|---|
| `K2bP_fine` — the stalled case, **must now refuse** | 1.0e-07 K | 1e-07 | **1.0** | **CANNOT_TELL** ✓ |
| `K2bP_coarse` — genuinely converged, **must still pass** | 2.929e-03 K | 1e-07 | **29,290** | **CONVERGED** ✓ |

Scoring the refused case would have returned 3.46e-08 %, a pass by five orders
of magnitude.

### The re-grade of all fourteen affected cases

Every case ever graded under the old reading: K0c's eleven and K2b's three.

| corpus | CONVERGED | NOT_CONVERGED | CANNOT_TELL | changed |
|---|---:|---:|---:|---:|
| K0c, eleven cases | 4 | 7 | 0 | **0** |
| K2b, three cases | 1 | 1 | 1 | **1** |

**Exactly one verdict changes: `K2bP_fine`, CONVERGED → CANNOT_TELL.** The
eleven K0c cases are untouched — which is the point, because a repair that moved
the existing corpus would be a new criterion wearing the old one's name. The
closest K0c case to the new floor is `Ra1e3_m32` at **13,161 ulp**, three orders
clear.

Section 4's table is corrected by this: `K2bP_fine`'s row now reads REFUSED, and
the sentence "it scores a perfect pass" describes what the criterion *did* before
the repair, not what it does now.

### The constant is not load-bearing, and that is measured

Sweeping the floor across all fourteen cases, the verdict set is **identical for
every value from 2 to 13,161 ulp — 3.8 orders of magnitude**:

| floor | refuses |
|---:|---|
| 1 | nothing — too low to catch the defect at all |
| **2 … 13,161** | **`K2bP_fine` only — the adopted plateau, 10 sits inside it** |
| 13,200 and above | also `Ra1e3_m32`, a genuinely converged K0c case |

### What the repair does not do, and one thing it does not reach

`CANNOT_TELL` is **not** `NOT_CONVERGED`. It says the log cannot support either
verdict on that quantity; the action is to run further, print more digits, or
grade a quantity that has responded.

And the clause is a **resolution** test, not a physics test: it fires when the
log cannot express the spread. A quantity genuinely pinned by a boundary
condition but printed at enough digits to show numerical noise would still pass.
**A stronger test exists and is not adopted here** — requiring that the quantity
have travelled further over the run than it now wiggles — because it would
false-positive on legitimate restart twins like this rung's own controls, which
begin from a converged field and are *supposed* to move very little. That is
filed rather than shipped.

### A second defect found on the way, reported and not repaired

**S13 normalises the peak-to-peak spread by the MEAN of the quantity.** For K0c's
Nusselt number, an O(1) dimensionless group, that is the right scale. For an
absolute temperature it is not: the mean is ~289–300 K while the physically
meaningful scale is ΔT_rack = 12 K, so **0.02 % of the mean is 0.058 K where
0.02 % of the signal would be 0.0024 K — the criterion is 24× looser than it
reads, purely because the quantity is reported in kelvin rather than as an
excess over supply.** Measured consequence: `K2bP_coarse` passes at 2.929e-03 K
against the mean-normalised band and would **fail** against the ΔT-normalised
one — which would agree with its heat balance, still 0.7857 % out at 9,000
iterations.

**Not repaired here, deliberately.** Changing the gate's normalisation would move
verdicts across the whole thermal corpus — K0c's eleven, K2e's thirty, KV1's
three — and this rung is not the right place to take that decision unilaterally.
Filed as **D389**, owner: chief.
