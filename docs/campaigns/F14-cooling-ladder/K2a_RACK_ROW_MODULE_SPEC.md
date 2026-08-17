# K2a. Rack-row module: geometry and boundary-condition specification

Campaign F14, rung K2a. Written 2026-08-17, zero compute spent, no solver
launched, no mesh built. **NO SOLVE MAY RUN AGAINST THIS SPECIFICATION UNTIL THE
OWNER HAS APPROVED IT AND AUTHORIZED THE COMPUTE.** The campaign order is
explicit on this and the cost estimate in Section 10 exists so the approval is a
decision against a number.

Written against the committed state: `docs/physics_rules.yaml` block `thermal`
at HEAD (the worktree copy of that file predates K1 and does not contain the
block — see the docket row filed with this spec), `docs/standards/
MONITOR_STANDARD.md` v1.9 signatures S13–S15, K0c's committed run tree, and
`K1_STANDING_THERMAL_CHECKS.md`. Every boundary-condition type named below was
verified to exist in the installed OpenFOAM v2606 source tree at
`/usr/lib/openfoam/openfoam2606/` this session, with the source path cited at
first use; that tier is written READ IN SOURCE. Values recalled from field
practice and not confirmed in any document this session are written RECALLED,
per the `docs/NUMERICS_KNOWLEDGE.md` convention, and none of them is a graded
quantity — they set defaults a later run reports, not references a run passes
against.

---

## 0. What this rung is and is not

K2a is a specification, not a result. It defines a parameterized rack-row
module a later agent can build **without rereading the literature or
reinterpreting this document**: dimensions with their sources, the parameter
list with ranges, a boundary condition on every surface, the mesh strategy, the
solver, and what is measured. The execution rung (K2b) is **unrun and
unauthorized**. K0a and K0b remain capability rungs and nothing here promotes
them.

The validation references this module can be graded against are K2c's business
(`K2c_RACK_ROW_VALIDATION_SEARCH.md`, filed alongside); this spec only has
to be *gateable* — every quantity K2c's gate names must be measurable from this
module as specified.

## 1. The modelling abstraction, and its stated limits

Per the campaign order:

> A rack is an inlet face plus an outlet face with deltaT = P / (mdot · cp),
> and the CRAC unit is the same box reversed.

So a rack is a solid rectangular obstruction whose front face **removes** air
from the cold aisle at a fixed flow rate and whose rear face **returns** the
same flow rate to the hot aisle, warmer by ΔT_rack = P/(ṁ·cp). No interior
volume is meshed. The CRAC is the identical construction with the sign of the
heat reversed: it removes air from the room (return face) and reintroduces it
colder (supply face). This is not the campaign's invention: the K2c primary
models its real facility with the same face-pair construction and the same
equation (the "black box model", ΔT = q/(ṁ·c_p), Wibron et al. 2018 Eq. (9),
READ IN FULL), and its validation record — accurate at room level, approximate
at rack level — is what scopes the claims below.

What this abstraction deliberately cannot represent, stated so nobody grades it
on these later:

- **No fan curve.** Rack flow is imposed, not pressure-dependent. A real
  server's flow rises when its inlet is starved of pressure; this module's
  cannot. Any comparison quantity that depends on flow-vs-pressure coupling is
  out of scope.
- **No internal distribution.** One ΔT per rack. Per-U or per-server inlet
  variation inside a single rack face does not exist in the model; the module's
  finest thermal granularity is the rack.
- **No leakage through the rack** (front-to-rear bypass around servers), no
  cable cutouts, no floor leakage paths. Leakage can be added later as an
  explicit parameter; in v1 it is absent and the omission is named.
- **No plenum.** The under-floor plenum is not meshed in v1; tile supply is
  imposed at the tile face (Section 3). Consequence, recorded here because it
  scopes K2c: published tile-flow-*split* measurements (which tile gets how
  much of the CRAC flow) validate a **plenum** model and cannot gate this
  module, whose per-tile flows are inputs. What this module can be gated on is
  the **room side**: rack-inlet temperatures and aisle temperature/velocity
  fields for given tile flows.

## 2. Geometry, parameterized

All boxes are axis-aligned. Coordinates: x along the rack row, y across it
(cold aisle → racks → hot aisle), z vertical. The module is one row of N racks
between one cold aisle and one hot aisle. Two-row (mirrored cold-aisle) layouts
are a doubling of this module across the cold-aisle midplane and are not
specified separately.

```
 z ^   ceiling (return patch above hot aisle in open-loop mode)
   |  +----------------------------------------------+
   |  |                                              |
   |  |   cold aisle      RACK      hot aisle        |
   |  |                 (solid,                      |
   |  |   tiles in      faces cut                    |
   |  |   floor)        into it)                     |
   |  +====TTTT=========+------+---------------------+  floor
   +--------------------------------------------------> y
```

### 2.1 Parameter list

| Symbol | Meaning | Default | Range | Source of default |
| --- | --- | --- | --- | --- |
| N | racks in the row | 4 | 1–10 | module choice; cost scales near-linearly (Section 10) |
| W_r × D_r × H_r | rack width × depth × height | 0.60 × 1.10 × 2.00 m | ±20% each | RECALLED: EIA-310 19-inch rack exterior convention (0.6 m footprint width, ~1.0–1.2 m deep, 42U ≈ 2.0 m). The standard document was not opened this session; the 0.60 m width is corroborated by the K2c primary's real facility ("600 mm wide pre-assembled cabinets", Wibron et al. 2018 §3.1, READ IN FULL). When the module is built to mirror a validation facility, that facility's stated dimensions **replace** these defaults and carry the facility's citation |
| W_ca | cold aisle width (rack front to opposite boundary) | 1.20 m | 0.9–1.8 m | RECALLED: two-tile (2 × 0.6 m) cold aisle convention |
| W_ha | hot aisle width | 1.20 m | 0.9–1.8 m | as above |
| H | ceiling height above floor | 2.70 m | 2.4–3.6 m | module choice |
| L_end | end margin beyond first/last rack | 0.60 m | 0.3–1.2 m | module choice, one tile pitch |
| s_t | tile pitch (tile is s_t × s_t in the floor) | 0.60 m | fixed in v1 | RECALLED: 600 mm raised-floor grid convention |
| n_t | number of supply tiles in the cold aisle | N | 1–2N | one tile per rack default |
| Qv_t | volumetric supply flow per tile | Σ Qv_r,i / n_t | 0.05–0.6 m³/s per tile | balance default: supply matches total rack flow; imbalance is a swept parameter (under/over-provisioning ±30%) |
| Qv_r,i | volumetric flow through rack i | 0.35 m³/s | 0.1–1.0 m³/s | derived from default P_i and ΔT_i via Qv = P/(ρ·cp·ΔT); see property note below |
| ΔT_i | temperature rise across rack i | 12.0 K | 5–20 K, and see Section 4 for the admissibility bands above 20 K | field-typical rise, RECALLED; **the primitive parameter is ΔT_i, not P_i** — the Boussinesq solve never needs ρ·cp, so P_i is derived for reporting as P_i = ρ·cp·Qv_r,i·ΔT_i and the recalled ρ·cp enters reporting only, never the solve |
| T_sup | supply air temperature at the tile (or overhead) face | 289 K (16 °C) | 285–300 K | RECALLED as field-typical; reported, not graded |
| supply_type | `tile` or `overhead` | `tile` | enum | campaign order names both |
| loop_mode | `open` (fixed T_sup, pressure return) or `closed` (CRAC face pair, Section 3.4) | `open` | enum | open loop is well-posed with fewer couplings and is the v1 default |

Derived defaults at the table's values: total rack flow 4 × 0.35 = 1.40 m³/s;
per-tile superficial velocity Qv_t/s_t² = 0.35/0.36 = **0.97 m/s**; rack front
face velocity Qv_r/(W_r·H_r) = 0.35/1.2 = **0.29 m/s**; per-rack load at
recalled ρ = 1.177 kg/m³, cp = 1006 J/(kg·K) (both RECALLED, reporting only):
P = 1.177·1006·0.35·12 ≈ **5.0 kW**.

Fluid properties for the solve are taken from the lab's own committed K0c
dictionaries, not from recall: ν = 1.589461e-05 m²/s, β = 3.333333e-03 1/K,
TRef = 300.0 K, Pr = 0.71, Prt = 0.85
(`K0c_runs/Ra1e5_m128/constant/transportProperties` at HEAD).

### 2.2 Tile modelling choice, and its ungraded limitation

In v1 a tile is a flat patch in the floor issuing the tile flow at the
**superficial** velocity (flow ÷ full tile area), uniform over the patch. Real
perforated tiles issue higher-momentum jets through the open fraction (25–56%
open area is the field-typical range, RECALLED), and the superficial-velocity
simplification under-delivers momentum — a documented modelling sensitivity in
the tile literature K2c catalogues (Abdelmaksoud et al. 2010 studied exactly
this; NOT OBTAINED, so the magnitude is **ungraded** here and no number is
quoted). The spec therefore carries the open-area fraction σ_t as a dormant
parameter: a later revision may switch the tile patch to jet velocity
Qv_t/(σ_t·s_t²) over an equivalent reduced area, but v1 fixes the choice to
superficial and names it, so a K2b deviation against a rack-inlet reference is
read with this limitation in view.

## 3. Boundary conditions, every surface

Solver context: `buoyantBoussinesqSimpleFoam` (steady SIMPLE, Boussinesq;
verified present at
`/usr/lib/openfoam/openfoam2606/applications/solvers/heatTransfer/`), fields
U, p_rgh, T, k, omega, nut, alphat. The compressible variant is Section 4's
business.

### 3.1 Passive surfaces

| Patch | U | p_rgh | T | k / omega / nut / alphat |
| --- | --- | --- | --- | --- |
| floor (outside tiles), ceiling, side walls, end walls, rack casing (all faces of each rack box except the two active ones) | `noSlip` | `fixedFluxPressure` | `zeroGradient` (adiabatic) | `kqRWallFunction` / `omegaWallFunction` / `nutkWallFunction` / `alphatJayatillekeWallFunction` (Prt 0.85; incompressible variant verified at `src/TurbulenceModels/incompressible/.../alphatWallFunctions/alphatJayatillekeWallFunction/`) |

Adiabatic walls are a modelling choice, recorded: real room envelopes leak
heat, and every watt of envelope loss shows up in the heat-balance audit
(Section 8) as imbalance. Keeping them adiabatic keeps the audit's ledger
closed over the named sources alone.

### 3.2 Supply and return (open-loop default)

| Patch | U | p_rgh | T | k / omega |
| --- | --- | --- | --- | --- |
| tile_j (floor, cold aisle), supply_type `tile` | `flowRateInletVelocity`, volumetricFlowRate Qv_t (verified at `src/finiteVolume/fields/fvPatchFields/derived/flowRateInletVelocity/`) | `fixedFluxPressure` | `fixedValue` T_sup | `turbulentIntensityKineticEnergyInlet` at intensity I_sup; `turbulentMixingLengthFrequencyInlet` at 0.1·s_t. **I_sup is a swept parameter (5–20%), not a known**: no measured value exists on this module and the sensitivity block (Section 9) sweeps it |
| overhead_j (ceiling, cold aisle), supply_type `overhead` | same as tile_j, mounted in the ceiling over the cold aisle | same | same | same |
| return (ceiling above hot aisle; area = one tile per rack equivalent) | `pressureInletOutletVelocity` | `fixedValue` 0 (gauge) | `inletOutlet`, inletValue T_sup | `inletOutlet` |

### 3.3 Rack faces — the abstraction itself

For rack i:

| Patch | U | p_rgh | T | k / omega |
| --- | --- | --- | --- | --- |
| rack_i_in (front face, cold aisle side) — air **leaves** the room here | `flowRateOutletVelocity`, volumetricFlowRate Qv_r,i (verified at `src/finiteVolume/fields/fvPatchFields/derived/flowRateOutletVelocity/`) | `fixedFluxPressure` | `zeroGradient` | `zeroGradient` |
| rack_i_out (rear face, hot aisle side) — air **returns** here | `flowRateInletVelocity`, volumetricFlowRate Qv_r,i | `fixedFluxPressure` | **`outletMappedUniformInlet`** mapping from rack_i_in with `fraction` 1 and `offset` ΔT_i | `turbulentIntensityKineticEnergyInlet` I_rack (default 10%, swept) / `turbulentMixingLengthFrequencyInlet` at 0.1·H_r |

The T coupling is the load-bearing row. `outletMappedUniformInlet`
(`src/finiteVolume/fields/fvPatchFields/derived/outletMappedUniformInlet/
outletMappedUniformInletFvPatchField.H`, READ IN SOURCE this session) averages
the field over a named outlet patch and imposes average + offset uniformly on
this patch: exactly ΔT = P/(ṁ·cp) with ΔT specified directly, since ṁ is
pinned by the paired `flowRateOutletVelocity`. No cp ever enters the Boussinesq
case. The face-averaging in the BC is area-weighted (`gWeightedAverage` over
`magSf` in the source); the *graded* rack-inlet temperature in Section 7 is
computed by function object as the **mass-flow-weighted** average of the same
face, and on a patch with uniform imposed normal flow the two coincide up to
the nonuniformity of the solved face flux — the analyser must print both once
and show their difference is below the gate resolution, or switch the grading
to the BC's own area average. That check costs nothing and closes off a
units-of-averaging dispute before it happens.

### 3.4 CRAC as the same box reversed (closed-loop mode)

`loop_mode: closed` replaces the supply/return patches of 3.2 with a CRAC box
standing at one end of the row: return face (hot aisle side or ceiling)
carrying `flowRateOutletVelocity` at Qv_CRAC, supply face (tile array or cold
aisle floor end) carrying `flowRateInletVelocity` with T from
`outletMappedUniformInlet` mapping the return face with **negative** offset
ΔT_CRAC = −Q_CRAC/(ṁ_CRAC·cp). This is literally the rack construction with
the sign reversed, per the order. Closed loop couples supply temperature to
load (T_sup is no longer a parameter but an outcome, and the absolute
temperature level is set by the ΔT ledger rather than pinned); it is the
right configuration for containment/failure studies and the wrong first
configuration for a validation gate, which is why `open` is the default.

For the compressible escalation (Section 4) the same coupling exists as
`outletMappedUniformInletHeatAddition`
(`src/thermoTools/derivedFvPatchFields/outletMappedUniformInletHeatAddition/`,
READ IN SOURCE): it imposes T_avg(outletPatch) + Q/(Σφ·Cp) with Q in watts and
Cp from the thermo package — the abstraction's formula implemented literally,
so P_i is then the primitive instead of ΔT_i. **Its TMin/TMax clamp (defaults
0/5000 K) is a silent limiter: set TMax far above the admissibility line or a
runaway sits invisibly on the clamp.**

## 4. Boussinesq validity — where the ranges sit against the lab's own limit

`docs/physics_rules.yaml` block `thermal` (HEAD): `boussinesq_beta_dT_max: 0.1`,
reached at **ΔT = 30.0 K exactly** at TRef = 300 (β = 1/TRef ideal gas,
measured from K0a's own dictionaries at K1a). A realistic rack ΔT crosses that,
and this spec does not get to ignore its own lab's rule.

The quantity the limit binds is the **domain temperature span**
ΔT_dom = T_max − T_min, not the rack rise alone, and on this geometry the two
are related by recirculation. Let r be the recirculated fraction of a rack's
inlet air (steady mixing): the rack-inlet excess over supply is
θ_in = r·θ_out and θ_out = θ_in + ΔT_rack, so

    θ_out = ΔT_rack / (1 − r),   and   ΔT_dom ≥ θ_out.

At r = 1/3, a 20 K rack already puts 30 K in the domain. So the a-priori
parameter screen is necessary but not sufficient, and the spec mandates both:

| ΔT_rack (max over racks) | Status under this spec |
| --- | --- |
| ≤ 20.0 K (default range) | **Admissible a priori** (β·ΔT ≤ 0.067 before recirculation), **and** the a-posteriori check below is still mandatory, because recirculation can carry the domain span past the limit from inside this range |
| 20.0 – 30.0 K | **Conditionally admissible**: build permitted, but the case is flagged at build time and the a-posteriori check is FATAL-on-breach rather than warn |
| ≥ 30.0 K | **Inadmissible under Boussinesq — the lab's own physics rules refuse it.** The case must be built on `buoyantSimpleFoam` (compressible, ideal-gas thermo; verified present in the installed solver tree) with the rack coupling switched to `outletMappedUniformInletHeatAddition` per Section 3.4. No Boussinesq case is specified at or beyond this line |

**A-posteriori check, wired into every run of this module:** a `fieldMinMax`
function object on T prints the running domain span every 50 iterations
(monitor cadence), and the analyser computes β·(T_max − T_min) at the graded
iteration. Breach at or above 0.1 on a Boussinesq case: the run is reported
with the breach stamped on its face and **is not evidence**; the case moves to
the compressible formulation. This is the same shape as S14's stamp — the
number is not wrong, the sentence about to be written on it would be.

The K0c laminar rung ran at β·ΔT ≈ 3.6e-03 (dimensionless unit cavity);
nothing this module does inherits that margin, which is exactly why the block's
comment says the crossing "is not academic".

## 5. Regime numbers for the default configuration

Stated because every thermal claim in this campaign carries its regime numbers.
Formulas per `docs/NUMERICS_KNOWLEDGE.md` regime map; properties from the K0c
dictionary values above; every number below is arithmetic on this spec's own
defaults (VERIFIED by calculation), not a measurement.

| Group | Definition | Value at defaults | Reading |
| --- | --- | --- | --- |
| Re_tile | U_tile·s_t/ν = 0.97·0.6/1.589e-5 | **3.7e4** | turbulent supply jet |
| Re_rack | U_face·W_r/ν = 0.29·0.6/1.589e-5 | **1.1e4** | turbulent rack streams |
| Ri_tile | g·β·ΔT·s_t/U_tile² = 9.81·3.333e-3·12·0.6/0.97² | **0.25** | mixed convection at the supply jet |
| Ri_rack | g·β·ΔT·H_r/U_face² = 9.81·3.333e-3·12·2.0/0.29² | **9.3** | buoyancy-dominant at the rack faces |
| Ra_H | g·β·ΔT·H³/(ν·α), α = ν/Pr | **3.0e10** | fully turbulent natural convection at room scale |

The module therefore spans mixed-to-natural convection depending on which
length you stand on — a laminar or steady-forced-only treatment is not
defensible anywhere in the parameter range. Model: **k-ω SST with the wall
functions of Section 3.1**, Prt = 0.85 recorded per solve with provenance per
the physics rules. Two consequences carried as named risks:

1. **Steadiness is an assumption, not a given — and the published record on
   exactly this module class says it fails.** The K2c primary reports that
   steady-state simulations of its 10-rack module "had difficulties converging
   due to fluctuations in the flow field" and moved to transient averaging over
   600 s (Wibron et al. 2018 §3.4, READ IN FULL). At Ra_H ~ 1e10 with opposing
   jets the same should be expected here. The S13 monitor (Section 8) is the
   instrument that says so; if the graded quantity will not meet
   `monitor_peak_to_peak_max_pct` over the fixed window, the case is not
   forced — it moves to unsteady (`buoyantBoussinesqPimpleFoam`) with
   statistical averaging, at roughly 5–10x the steady cost (planning figure,
   labelled estimate, same basis as Section 10). Section 10's steady-case
   totals are therefore a floor, and the pilot's first job is to report which
   regime the module is actually in.
2. **SST in room flows has a documented trap** on the record this campaign
   already holds: K0d's evaluation notes SST predicting a spurious
   occupied-zone recirculation against Annex 20 LDA data (Nielsen, Rong,
   Olmedo 2010, READ IN FULL at K0d). Model-form deviation is exactly what
   K2c's gate exists to measure; no model claim travels without it.

## 6. Mesh strategy

Axis-aligned rectilinear geometry throughout — **blockMesh multi-block, no
snappyHexMesh**. Racks are unmeshed voids whose faces are patches. Grading
concentrates resolution at tile faces, rack faces, and the floor/ceiling
boundary layers.

- Base cell (coarse): 60 mm; refined bands at active faces: 30 mm.
- Fine mesh: uniform factor ≥ 1.5 per direction on the coarse (K0c's mandatory
  two-mesh convention, inherited unchanged: coarse solved first, both reported,
  grading on the fine).
- Wall treatment: wall functions; target y+ in the log-law band (30–300,
  RECALLED as the standard wall-function band; to be *measured* by the
  mesh-report function object and reported per case, not assumed).
- Cell-count consequences at the N = 4 defaults (domain 3.6 × 3.5 × 2.7 m ≈
  34 m³): coarse ≈ **0.20 M** cells, fine ≈ **0.7 M** cells. These two numbers
  are inputs to Section 10, so they are stated here rather than left to the
  builder's taste; a build that departs from them by more than 2x re-prices the
  rung and goes back to the owner.
- Mesh acceptance per `docs/MESH_STANDARD.md` (checkMesh gates as standing).

A 2D vertical-slice pilot (x = const through one rack: cold aisle, rack,
hot aisle) is specified alongside as **K2b-pilot**: same BCs collapsed to the
slice, 42 k / 95 k cell pair. It exists to shake down the BC coupling, the
monitor wiring and the heat-balance path at ~1/15 the cost (Section 10) before
the 3D module burns anything, and **it is a capability case in the K0a/K0b
sense — never a result.**

## 7. What is measured

Grading quantities, all computed by in-pass function objects at the monitor
cadence (every 50 outer iterations) so S13 can read them from the log alone:

| Quantity | Definition | Why it is the graded set |
| --- | --- | --- |
| T_in,i | mass-flow-weighted average T over rack_i_in, per rack | the quantity the field's practice and every candidate reference in K2c measures at the rack front |
| T_in,max | max over i of T_in,i | the failure-mode quantity (worst rack); **the S13 monitored quantity for this module** |
| θ_i | (T_in,i − T_sup)/ΔT_rack,i | dimensionless recirculation index, defined here and self-contained: θ = 0 is perfect supply capture, θ ≥ 1 means rack i inhales its own class of exhaust. Defined internally so the gate needs no external index citation |
| ΔT_dom | domain max T − min T (`fieldMinMax`) | the Section 4 admissibility instrument |
| Q_patch ledger | conductive + advective heat flux through every active patch | Section 8's audit inputs |
| vertical T profiles | line samples up the cold-aisle and hot-aisle midplanes | the profile shape is what published room measurements offer where rack averages are absent (K2c) |

Velocity field snapshots at the aisle midplanes are written at the graded
iteration for qualitative comparison; they grade nothing by themselves.

## 8. Convergence, audits, and what heat-balance closure means HERE

**Convergence** is S13, inherited whole: peak-to-peak spread of T_in,max below
`monitor_peak_to_peak_max_pct` (0.02%) over `monitor_window_iterations` (400)
sampled every 50, minimum 9 samples, REFUSED below that — thresholds read from
`docs/physics_rules.yaml`, never copied into a case script. Residuals meeting
`residualControl` are not evidence (that is S13's whole content, measured at
K0c).

**Heat balance on this geometry — the required statement.** The physics rules
carry `heat_balance_closure_is_evidence_on_sealed_case: false` because on a
sealed impermeable steady box the balance is a near-identity (K0b measured
0.0128% at iteration 10 against a predicted >20%). **This module is not a
sealed box**, and neither inherited answer applies unexamined:

- *What closure DOES establish here.* With through-flow, the boundary ledger
  Σᵢ ṁᵢcp·T̄_in,i − Σᵢ ṁᵢcp·T̄_out,i + supply/return advective fluxes + wall
  conduction must net to zero **only at convergence** — the advective enthalpy
  flux is an independent contribution the discretisation does not force (the
  physics rules block says exactly this, and K1c measured the contrast: a
  convergence-sensitive recovery tracks the T residual across seven decades
  while the sealed closure sits at 0.01% from iteration 10). So on this
  geometry a closure number **is** a convergence- and bookkeeping-sensitive
  measurement: it catches an unconverged energy field, a mis-set ΔT offset, a
  flow-rate mismatch between a rack's face pair, a patch omitted from the
  ledger, and the BC clamp silently limiting (Section 3.4).
- *What closure does NOT establish here.* Circulation. A solve with the aisle
  flow structure entirely wrong — supply short-circuiting to the return,
  reversed aisle recirculation — still closes perfectly once converged,
  because closure tests conservation, not *where* the energy travelled.
  θ_i and T_in,i move by factors under those failures while closure does not
  move at all. Closure is therefore **necessary, never sufficient**, and no
  K2b sentence may cite it as validation evidence; validation is K2c's gate
  alone.

**Instrument prerequisite, named so it cannot be skipped:**
`scripts/heat_balance.py` (HEAD) REFUSES non-wall patches unless
`--allow-advective`, and its own docstring stamps the advective path
**UNVALIDATED**. Before any K2b closure figure is quoted, the audit's advective
path must be validated on a control the way K1c validated the sealed path:
**KV1** — a straight duct with imposed ṁ, inlet T, and a planted volumetric
source of known watts; the audited net must recover the plant within
`heat_balance_source_recovery_tol_pct` (0.1%). KV1 is part of K2b's control
budget (Section 10), and until it passes, every advective closure number is
reported UNVALIDATED in the script's own words.

**Pre-registered controls for K2b** (kinds per the K0c convention, budgeted in
Section 10): C1 gravity-off twin (θ becomes pure forced transport; predicted
direction: cold-aisle stratification collapses), C2 ΔT-plant (+10% on one
rack's offset; predicted: that rack's outlet ledger row moves by 10%, its θ
unchanged to first order — the discriminating pair), C3 planted volumetric
source (KV1's plant in the room), C4 comparator mutation on every gate row (no
compute). S14's identity-class stamp must read **not-identity-class** on this
geometry — the stamp being *present and false* is itself checked, because a
missing stamp reads exactly like a sealed-case pass. S15's fvOptions witness
runs wherever a plant exists.

## 9. Solver, numerics, sensitivity block

- Solver: `buoyantBoussinesqSimpleFoam` inside the Section 4 envelope;
  `buoyantSimpleFoam` beyond it. Steady SIMPLE with the K0c two-stage
  relaxation pattern as the starting point (the committed
  `K0c_runs/*/system/fvSolution*` are the lineage; C5 at K0c measured
  relaxation moving the path, not the answer).
- Schemes: the committed K0c `fvSchemes` extended with turbulence divergence
  entries (`div(phi,k)`, `div(phi,omega)` bounded upwind; `div(phi,T)` and
  `div(phi,U)` second-order limited as in K0c). Exact dictionaries land with
  the case build and are diffed against this paragraph at review.
- `residualControl` is set loose enough never to stop a case before S13 is
  satisfied — K0c's lesson (L-89) written into the controlDict rather than
  re-learned.
- Sensitivity block (each a cheap coarse-mesh delta, budgeted): supply
  turbulence intensity I_sup ∈ {5, 10, 20}%; tile/rack flow imbalance ±30%;
  supply type tile vs overhead; N = 2 vs 4 (end effects). Reported as trends;
  none of it grades.

## 10. Compute cost — ESTIMATE, with its basis

**Every figure in this section is an estimate.** Basis: the measured K0c
cell-iteration throughput on this machine (single core, the committed logs and
COST.txt files at HEAD), derated for 3D + turbulence by an assumed factor —
the derate is an engineering assumption, stated, not a measurement.

Measured rates (cells × outer iterations ÷ wall seconds, from the committed
K0c logs; iterations counted as `Time = ` lines across all stages):

| case | cells | iters | wall s | cell·iter/(core·s) |
| --- | ---: | ---: | ---: | ---: |
| Ra1e3_m64 | 4,096 | 4,016 | 36.1 | 4.6e5 |
| Ra1e5_m64 | 4,096 | 5,073 | 37.2 | 5.6e5 |
| Ra1e5_m128 | 16,384 | 7,709 | 355.5 | 3.6e5 |
| Ra1e6_m192 | 36,864 | 7,885 | 1,081.7 | 2.7e5 |

Planning rate: take the low end (2.7e5, the largest case) and derate ÷2.7 for
3D turbulent SST (three velocity components, two turbulence equations, ~50%
more faces per cell) → **1.0e5 cell·iter/(core·s)**. Iteration counts to meet
the S13 criterion are taken from K0c's own range (4,000–7,900 on buoyant
steady cases): 5,000 coarse / 8,000 fine planning figures.

| Item | cells | iters | core·s | core·min |
| --- | ---: | ---: | ---: | ---: |
| K2b-pilot 2D pair (42 k + 95 k, rate 2.7e5) | — | 5,000/8,000 | 3.6e3 | **60** |
| 3D coarse (0.20 M) | 2.0e5 | 5,000 | 1.0e4 | 167 |
| 3D fine (0.70 M) | 7.0e5 | 8,000 | 5.6e4 | 933 |
| controls C1–C3 + KV1 (coarse-mesh class) | — | — | 2.6e4 | ~430 |
| sensitivity block (6 coarse deltas) | — | — | 6.0e4 | ~1,000 |
| **K2b graded pair + controls (excl. sensitivity)** | | | | **≈ 1,600** |
| **everything specified** | | | | **≈ 2,700** |

For scale against this campaign's record: K0a + K0b cost 0.86 core-minutes,
K0c 41.7, K1 3.0. The full K2b module is **~40x K0c** — which is why this
number goes to the owner attached to a specification rather than discovered in
a ledger afterwards. Uncertainty on the estimate: the derate and iteration
count are each good to a factor ~2, so read the bottom line as **1,300–5,500
core·min** (22–90 core·h). The staged path exists precisely to spend 60
core·min of pilot before anyone authorizes 1,600. Wall-clock is divisible by
domain decomposition (the rate is per core); parallel efficiency on ~1e5
cells/core is high for this solver class (RECALLED, reported not promised).

## 11. What the owner is approving

1. The abstraction and its stated limits (Section 1), the geometry and
   parameter ranges (Section 2), and the BC table (Section 3) — as the
   buildable definition of the F14 rack-row module.
2. The Boussinesq admissibility policy (Section 4), including the mandatory
   a-posteriori span check and the compressible escalation path.
3. The measurement and audit plan (Sections 7–8), including KV1 as a
   prerequisite to quoting any closure number.
4. Optionally, in increasing order of spend: K2b-pilot (~60 core·min), the K2b
   graded pair with controls (~1,600 core·min), the sensitivity block
   (~1,000 core·min). **Nothing runs until this document is approved and the
   spend is authorized; approval of the spec alone authorizes zero
   core-minutes.**
