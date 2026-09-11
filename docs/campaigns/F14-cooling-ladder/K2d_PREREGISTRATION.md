# K2d — the three-level realisation of the owner-approved K2a rack-row module: PRE-REGISTRATION

**Campaign F14, DC-cooling spine. Rung `K2d`. Team: heat-transfer.**
**Written 2026-09-10 by a heat-transfer `lab-lane` at ZERO solver core-minutes.**

> # FROZEN 2026-09-11 by heat-transfer-supervisor. GATES ARE CLOSED.
>
> **Every gate, band, threshold, floor, cap and label in this file is FROZEN**
> and may no longer be amended. The grading path is pinned by blob in section 9;
> the freeze commit's own sha is recorded in that commit's message, because a
> file cannot contain its own committed hash. Changes land only as dated addenda
> that cannot alter a gate, threshold, cap or label (standing rule 2); originals
> are struck, never rewritten.
>
> **STRUCK AT FREEZE:** the DRAFT banner this replaces, together with its
> amendment condition *"`K2d_runs/` does not exist"* — superseded before this
> freeze by section 14's stricter restatement. **First SOLVER compute has NOT
> occurred.** `blockMesh` and `checkMesh` are meshing and inspection utilities;
> L1 is built at **58,368 cells** and returns **`Failed 0 mesh checks`** under
> `-allGeometry -allTopology`, with `Mesh has 3 geometric (non-empty/wedge)
> directions (1 1 1)` and no `0/`. Later sections stating this document is not
> frozen are dated records of past amendments, true when written and superseded
> by this banner.
>
> **THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED:**
> *"`verification/runs/F14-cooling-ladder/K2d_runs/` does not exist."*
> **Checked by its absence on disk, 2026-09-10, by `test -d`** — not by asking
> git, not by reading a document. It did not exist at that reading.
>
> **No run directory may be created and no solver may be launched until the
> freeze commit exists on `main`** — and the check is that the commit *is there*,
> not that someone meant to write one.

---

## 0. WHAT THIS RUNG IS, AND THE THREE THINGS IT IS NOT

**K2d runs the rack-row module defined by `K2a_RACK_ROW_MODULE_SPEC.md`, on a
three-level grid ladder, and grades a Roache triple on it.** Geometry, boundary
conditions, fluid properties, solver, turbulence model, measured quantities and
convergence rule are **inherited from K2a by citation** and are not re-derived
here. Where this document departs from K2a it says so, in §1.3, with the reason.

### 0.1 IT IS NOT VALIDATION, AND THE REFERENCE TIER IS `NONE`

**Every graded quantity in this rung carries reference tier `NONE`.** There is
no experimental or published referent for the graded rows. **K2d is
VERIFICATION** — it measures whether the discrete solution converges under grid
refinement, and it makes **no claim whatever about agreement with reality.**

Wibron, Ljung & Lundström (2018) is cited in this document and its digitised
data is read by the comparator, **as a REPORT-ONLY referent and never as a
gate.** §4.4 fixes exactly what that comparison may and may not be said to show.

**Why it cannot be validation, stated so a later reader cannot mistake it.**
The Wibron measurements were taken in a *different room with a different
layout*, and the difference is structural, not a matter of parameter values:

| | **K2a module — what K2d runs** | **Wibron 2018 — the report-only referent** |
|---|---|---|
| layout | **one row** of N racks, one cold aisle, one hot aisle (`K2a:81`–`:82`) | **two rows** of five, back-to-back, forming a contained hot aisle |
| domain | 3.6 × 3.5 × 2.7 m ≈ **34 m³** (`K2a` §6) | 5.084 × 6.484 × 3.150 m ≈ **104 m³** |
| racks | 4 at the defaults (`K2a:102`) | 10, of which R5 is empty and R6 half-populated |
| supply | tile or overhead; **plenum not meshed** (`K2a` §3.2, `:71`) | **hard floor** — four CRAC units supplying directly into the room |
| containment | none | **partial hot-aisle containment with a door** at the row end |
| obstructions | none | switchgear and UPS modelled as flow blockages |
| measurement points | generic | L1–L5 at fixed coordinates *in that room* |

**`K2a:82` excludes the Wibron configuration in terms:** *"Two-row (mirrored
cold-aisle) layouts are a doubling of this module across the cold-aisle
midplane and are **not** [modelled]."* Wibron's configuration is precisely that
excluded case. **Matching quantity *types* — rack-front temperatures, aisle
velocity profiles — is not matching a *configuration*.** A number computed on
this module and set beside a number measured in that room is a curiosity, not
evidence, and this rung will not present it as evidence.

The rung that *would* earn the validation claim is drafted separately as a
proposal for Sanaa's desk (§12). **It is not registered here and nothing in this
document authorises it.**

### 0.2 IT IS NOT A NEW EXPERIMENT, AND IT DOES NOT STRETCH AN APPROVAL

Sanaa approved **K2a** in her own words at ~20:20Z on 2026-09-10. **K2d changes
neither of K2a's two specified mesh levels.** K2a §6 specifies coarse ≈ 0.20 M
and fine ≈ 0.70 M cells; both survive in this ladder unchanged, as **L2** and
**L3**. K2d **adds one cheaper level below them** and nothing else.

**K2a's own re-pricing clause was checked and is NOT triggered.** §6 reads: *"a
build that departs from them by more than 2× re-prices the rung and goes back to
the owner."* The two numbers that clause protects are 0.20 M and 0.70 M. Both are
preserved. Adding a level *below* them departs from neither.

### 0.3 IT IS NOT A CLAIM THAT TWO LEVELS WOULD HAVE DONE

**The third level exists because two levels cannot carry a Roache triple.** K2a
§6 inherits *"K0c's mandatory two-mesh convention … coarse solved first, both
reported, grading on the fine"*, and a grep of K2a for `triple`, `roache`, `gci`
and `three level` returns nothing. **Two levels give a difference, not a
convergence order.** Under standing rule 5 a row without a `CONVERGING` triple is
`NOT A RESULT` whatever its value, and no GCI may be quoted from it. Running K2a
exactly as specified would therefore have spent its approved budget and been
*unable* to produce the mesh convergence the owner asked for at 19:45Z. The third
level is what makes the approved spend answer the approved question.

---

## 1. THE LADDER

### 1.1 Target cell counts, and the fact that they are targets

| level | **target** cells | role |
|---|---:|---|
| **L1** | **59,259** | added by this rung; the 3D rate probe (§7.2) runs here |
| **L2** | **200,000** | **K2a's approved coarse level, unchanged** |
| **L3** | **675,000** | **K2a's approved fine level, unchanged; the grading level** |

Target step **3.3750** at each pair, so **r = 1.5000 in three directions**
(1.5³ = 3.375). This is the 3D refinement signature and it is consistent by
construction across both pairs.

### 1.2 THE LADDER IS GATED ON THE **BUILT** COUNTS, NOT ON THESE TARGETS

**A ladder that grades on intended counts is grading on an intention.** A
`blockMesh` built from integer block divisions will not land exactly on the
numbers above.

**Registered:** the comparator reads the **actual cell count of each level from
its own built `constant/polyMesh`**, computes the actual pair ratios, and gates
them. Precedent: the `G-MESHSIM` limb of the T23G2 line, which measures cell
ratios *"from the BUILT polyMesh"*.

- **`G-MESHSIM`** — actual `N(L2)/N(L1)` and `N(L3)/N(L2)` must each lie in
  **[3.2063, 3.5438]**, i.e. 3.375 ± 5 %, equivalently **r ∈ [1.4747, 1.5245]**.
  A pair outside the window → **every graded row `NOT A RESULT`**, both actual
  ratios and both actual counts printed beside it.
- The **targets above are never used in any computation.** They size the build
  and appear in the cost basis; the gate never reads them.

### 1.3 EVERY DEPARTURE FROM K2a, AND ITS REASON

| # | departure | reason |
|---|---|---|
| **D1** | a third mesh level below K2a's two | §0.3 — two levels cannot carry a Roache triple |
| **D2** | Roache triple gating, `Fs` = 1.25, observed order and GCI | K2a registers no triple; standing rule 5 requires the gating once one exists |
| **D3** | every `checkMesh` carries `-allGeometry -allTopology` | §5.1 — K2a §6's *"checkMesh gates as standing"* inherits a check set that cannot fail the way it needs to |
| **D4** | a registered **limit-cycle limb** (§3.3) | §3.3 — K2a §5 names the risk and routes it to a solver change; this rung must grade it instead, because a post-compute solver switch is a gate change |
| **D5** | a **D-3D dimensionality gate** (§5.2) | T4e and the whole T23G2 line proved 2D wedges on 2026-09-10 while carrying 3D language |
| **D6** | an observed-order band wider than the lab's usual | §4.3 — calibrated on the reference's own measured order spread, before compute |

**No band, threshold, floor, reference or reader inherited from K2a is widened,
moved or loosened by any of these.** D6 sets a band K2a never had; it does not
relax one.

---

## 2. GEOMETRY, BOUNDARY CONDITIONS AND PROPERTIES — INHERITED BY CITATION

**Read `K2a_RACK_ROW_MODULE_SPEC.md` §2, §2.1, §3 at the freeze commit. Nothing
is re-derived here and nothing there is edited.** The configuration is K2a's
**defaults**: `N` = 4, `W_r × D_r × H_r` = 0.60 × 1.10 × 2.00 m, `W_ca` = `W_ha`
= 1.20 m, `H` = 2.70 m, `L_end` = 0.60 m, `s_t` = 0.60 m, `n_t` = `N`,
`Qv_r,i` = 0.35 m³/s, `ΔT_i` = 12.0 K, `T_sup` = 289 K, `supply_type` = `tile`,
`loop_mode` = `open` (`K2a` §2.1).

Fluid properties are taken from the lab's committed K0c dictionaries and not
from recall (`K2a` §2.1, sourced to
`K0c_runs/Ra1e5_m128/constant/transportProperties` at HEAD):
**ν = 1.589461e-05 m²/s, β = 3.333333e-03 1/K, TRef = 300.0 K, Pr = 0.71,
Prt = 0.85.**

**Regime numbers at these defaults**, transcribed from `K2a` §5, which computed
them: `Re_tile` **3.7e4**, `Re_rack` **1.1e4**, `Ri_tile` **0.25**, `Ri_rack`
**9.3**, `Ra_H` **3.0e10**. The module spans mixed-to-natural convection; a
laminar treatment is not defensible anywhere in the range.

---

## 3. SOLVER, TURBULENCE, AND THE TWO FAILURE MODES REGISTERED IN ADVANCE

### 3.1 Solver — K2a's, unchanged

**`buoyantBoussinesqSimpleFoam`, steady SIMPLE** (`K2a` §9), stock ESI v2606 at
the system path, with the K0c two-stage relaxation pattern and the K0c
`fvSchemes` extended with turbulence divergence entries, exactly as `K2a` §9
specifies. `residualControl` is set loose enough never to stop a case before
S13 is satisfied (`K2a` §9, L-89).

### 3.2 Turbulence — `kOmegaSST`, and a PREDICTED FAILURE we can lose

**`kOmegaSST` with the wall functions of `K2a` §3.1, `Prt` = 0.85** (`K2a` §5).

**`LRR` and `SSG` were both verified present** in the installed v2606 tree at
`src/TurbulenceModels/turbulenceModels/RAS/{LRR,SSG}`, so the Reynolds-stress
class *is* reachable. **This rung does not reach for it**, for two registered
reasons: K2a's approved specification fixes `kOmegaSST`, and a rung that changes
the model *and* adds a mesh level confounds the two.

**REGISTERED PREDICTION `P-K2d-1`, fixed before compute and losable.**
The report-only referent's own central finding (Wibron 2018, abstract, READ AT
SOURCE) is: *"The k–ε model fails to predict low velocity regions. RSM and DES
produce very similar results and, based on the solution times, it is recommended
to use RSM."* `kOmegaSST` is an eddy-viscosity model of the same class — it
carries the turbulent-viscosity hypothesis and isotropic-stress assumption that
finding indicts.

> **`P-K2d-1` predicts: in the REPORT-ONLY comparison of §4.4, the deviation
> between this module's computed aisle velocity and the referent's profiles
> will be LARGER at the low-velocity sample points than at the high-velocity
> sample points.** The split is fixed now and not after looking: a sample point
> is **LOW-velocity** if the referent's velocity there is **< 0.50 m/s** and
> **HIGH-velocity** if **≥ 0.50 m/s**. The prediction HOLDS if the median
> absolute deviation over the LOW set exceeds that over the HIGH set; it
> **LOSES** otherwise.
>
> **`P-K2d-1` GRADES NOTHING.** It is scored HIT or LOSS and reported either
> way. It cannot move a gate, a band or a verdict, and it inherits the
> report-only status of everything in §4.4 — including the configuration
> mismatch of §0.1, which means a LOSS is not evidence the model class is sound
> and a HIT is not evidence it is unsound. **It is registered because a
> prediction we can lose is worth more than a model chosen to pass**, and
> because scoring it after compute without having written it down first would
> be worthless.

**A second named risk, carried from `K2a` §5 and not re-derived:** SST has a
documented trap in room flows on this campaign's own record — K0d's evaluation
notes SST predicting a spurious occupied-zone recirculation against Annex 20 LDA
data. Model-form deviation is not measurable by this rung and no K2d sentence
may claim it is.

### 3.3 `G-CYCLE` — THE LIMIT-CYCLE LIMB, AND WE EXPECT IT TO FIRE

**This is the sharpest risk in the rung and it is registered as a gate, not as a
hope.**

Two independent measurements say a steady solver may not converge on this flow:

1. **The report-only referent measured it on its own module** — Wibron 2018
   §3.4, READ AT SOURCE: *"As could be expected, **steady-state simulations had
   difficulties converging due to fluctuations in the flow field. Therefore,
   transient simulations were considered instead**"*, moving to 60 s of start-up
   and 600 s of transient averaging at dt = 0.05 s.
2. **This family already hit it in this geometry.** K2b-U found a 2D limit cycle
   in the rack-row module, and `K2b_3D_UNSTEADINESS_PREREGISTRATION.md` exists
   only because of it.

**`K2a` §5 anticipated this and routed it to a solver change** — *"if the graded
quantity will not meet `monitor_peak_to_peak_max_pct` over the fixed window, the
case is not forced — it moves to unsteady (`buoyantBoussinesqPimpleFoam`)"*.
**K2d does not take that route, and the reason is standing rule 2:** after first
compute, gates are closed. Switching solver mid-rung would change the registered
grading path to fit the answer. **So the failure mode is graded here instead.**

> **`G-CYCLE`, evaluated per level, BEFORE any triple is classified.**
> The S13 quantity `T_in,max` is sampled every 50 outer iterations. Over the
> **last 400 iterations** (≥ 9 samples, REFUSED below that):
> - **CONVERGED** — peak-to-peak spread ≤ **0.02 %** of the sample mean. This is
>   S13 unchanged, thresholds read from `docs/physics_rules.yaml` at run time and
>   never copied into a case script (`K2a` §8).
> - **CYCLING** — peak-to-peak spread **> 0.02 %**, AND the sample series shows
>   **≥ 3 sign changes** in its first difference over the window, AND the linear
>   trend over the window explains **< 25 %** of the sample variance. A series
>   that oscillates about a level rather than descending toward one.
> - **DRIFTING** — spread > 0.02 % and not CYCLING.
>
> **Any level `CYCLING` or `DRIFTING` → EVERY graded row of the rung is
> `NOT A RESULT`**, with the per-level state, spread, sign-change count and
> trend fraction printed beside it. This is standing rule 5 clause (1) — *"any
> level not iteratively converged or not plateaued → `NOT A RESULT`"* — evaluated
> **before** any triple is classified, and it is evaluated **first**.

#### 3.3a `U_ha` — THE DETECTOR MUST LOOK WHERE THE PREDICTION POINTS

**A defect found in this document's own first draft, at the supervisor's §3 diff
read, and corrected here before compute.** `P-K2d-2` predicts cycling **at the
hot-aisle side of the rack faces**. The limb above samples **`T_in,max`, a
COLD-AISLE quantity at the rack inlets**. *If the cycle lives where the rung
predicts, a detector watching only the inlet may never see it* — the rung would
read `CONVERGED`, grade a triple, and report `P-K2d-2` as a `LOSS` when the gate
was simply not pointed at the phenomenon. **A prediction whose detector does not
look at the predicted location is not falsifiable**, and this is the same shape
standing rule 3 forbids: a reader not shown able to see the thing it must see.

**REGISTERED: a second monitored quantity, at the predicted location.**

> **`U_ha`** — the **volume-averaged velocity magnitude over the hot-aisle
> control volume**: the full hot-aisle width `W_ha`, spanning the rack row in
> `x` from the first to the last rack face, and from the floor to the rack top
> `H_r` = 2.00 m in `z`. This is the volume where the opposing rack-exit jets
> meet and where `Ri_rack` = 9.3 puts the flow in the buoyancy-dominant regime.
> It is written by an in-pass function object at the **same 50-iteration
> cadence** as `T_in,max`, so `G-CYCLE` reads it from the log alone.
>
> **Threshold: peak-to-peak spread of `U_ha` ≤ 0.02 % of the RANGE THE QUANTITY
> SPANNED OVER THE RUN** — S13's threshold and S13's normaliser, unchanged —
> over the same 400-iteration window, **≥ 9 samples, REFUSED below that**. The
> `CYCLING` and `DRIFTING` discriminators are **identical** to §3.3's — ≥ 3 sign
> changes in the first difference, and linear trend explaining < 25 % of sample
> variance.
>
> **Any level `CYCLING` or `DRIFTING` on EITHER `T_in,max` OR `U_ha` → every
> graded row `NOT A RESULT`.** Both states are printed for every level whichever
> fires.

**Both limbs CALL the canonical implementation and neither reimplements it.**
`scripts/check_convergence.py::classify_monitor` (`:576`) is S13, it applies the
range normaliser at `:629`, and it carries the **null-variation refusal** — a
quantity that never resolvably moved is REFUSED, never passed. The comparator
calls it for `T_in,max` and for `U_ha` alike, so there is one implementation of
S13 for this rung and no drift is possible, and `U_ha` inherits the
null-variation refusal for free. Thresholds are read from
`docs/physics_rules.yaml` at run time and **never copied into a case script**
(`K2a` §8).

#### 3.3a.1 WHY THE THRESHOLD IS 0.02 % AND NOT THE 0.5 % THIS DOCUMENT FIRST REGISTERED

**A defect in this rung's own first draft of §3.3a, found by checking a docket
citation at source instead of adopting it, and corrected here before compute.**

This section first registered **0.5 % of the sample MEAN**, justified as *"a
velocity in a buoyancy-dominant recirculation is noisier than a mass-flow-
weighted inlet temperature."* **That was wrong in its normaliser, and the
justification was arguing for a rule the lab no longer uses.**

**`D389` IS NOT OPEN. `D393` SETTLED IT on 2026-08-18 and the repair is live.**
D389 recorded that S13 normalised the peak-to-peak spread by the quantity's
**absolute mean** — on a rack-inlet temperature of mean 289 K and range 0.086 K,
a factor of **3,343** looser than it read. **D393 repaired it**: the spread is
now referred to **`max(series) − min(series)` over the whole run**, carried in
`docs/physics_rules.yaml` as **`heat_monitor_normaliser: range_spanned_over_run`**
and implemented at `scripts/check_convergence.py:629`. **The threshold number
was deliberately left at 0.02 %**, because its derivation — *"one fiftieth of
the tightest pass band K0c gated on"* — was always meant as a fraction of the
thing being resolved, and the mean was only ever a proxy for that.

**So the mean-normalised arithmetic describes S13 as it was three weeks ago, not
as it is.** Under the live rule both quantities are referred to **their own
travelled range**, which is what the residual wiggle must be small against. The
asymmetry that motivated 0.5 % **does not exist** once the normaliser is the
right one: a velocity's range and a temperature's range are each the distance
that quantity actually moved, and 0.02 % of each means the same thing.

**A mean-normalised threshold on `U_ha` would have reintroduced, in this rung,
precisely the defect D393 repaired** — and it would have done so while citing
the repair's own docket number as its justification.

**The honest limit on carrying 0.02 % across, named rather than glossed.**
D393's threshold-insensitivity sweep — an identical verdict set anywhere in
**(0.0027, 0.0642] %**, a 24× span with 0.02 inside it — was measured over 49
committed cases that grade **Nusselt-like groups and absolute temperatures**.
**No velocity was in that corpus.** So 0.02 % reaches `U_ha` by **consistency of
normaliser**, not by a measured sweep on this quantity class, and this document
says so rather than implying the sweep covers it. **That is exactly the gap
§3.3b's measured detection floor exists to bound**, and it is why the floor is
reported beside every `CONVERGED` reading rather than asserted.

**K2d SETTLES NOTHING ABOUT D389 OR D393 AND CHANGES NO EXISTING VERDICT.** It
registers a threshold on a **new** quantity in a **new** rung, under the
normaliser already in force. **`T_in,max`'s limb carries S13 at 0.02 % of range,
unchanged and untouched by this rung** — if the S13 constants are ever revisited,
that limb moves with the standard and this section does not shield it.

#### 3.3b PLANTED-CYCLE CONTROL — the detector must be SHOWN able to detect a cycle

**A cycle detector never shown able to detect a cycle is worth exactly as much
as a zero from a blind reader.** Standing rule 3's principle is applied to the
detector itself.

Before any level is classified, for **every level and both monitored
quantities**, the comparator:

1. **POSITIVE ARM.** Plants a synthetic sinusoid into a copy of the sampled
   series — **amplitude 2× the quantity's registered spread threshold**, **period
   200 iterations** (4 samples, giving ≥ 4 sign changes across the 400-iteration
   window) — runs it through the **identical** `G-CYCLE` classifier, and
   **REFUSES (exit 2) if the planted cycle is not classified `CYCLING`.**
2. **NEGATIVE ARM.** Plants a clean monotone decaying series with spread below
   threshold, runs the same classifier, and **REFUSES (exit 2) if it is
   classified `CYCLING`.** A detector that calls everything a cycle is as
   useless as one that calls nothing a cycle.
3. **DETECTION FLOOR, measured and reported, never asserted.** Plants a ladder
   of sinusoids at decreasing amplitude — **1.0×, 0.5×, 0.25×, 0.125×, 0.0625×
   the spread threshold** — and **reports the smallest planted amplitude still
   classified `CYCLING`.** That figure is printed in the gate JSON and quoted in
   the results record beside any `CONVERGED` reading, so a reader knows what
   amplitude of cycle the rung was capable of seeing.

**The comparator REFUSES rather than degrading.** It does not grade a rung whose
cycle detector has not demonstrated, on that run's own data, that it works.

**REGISTERED PREDICTION `P-K2d-2`, and we predict against ourselves.**

> **`P-K2d-2` predicts that at least one of the three levels will read
> `CYCLING`, and that the finest level L3 is the most likely to.** The named
> location is the **hot-aisle side of the rack faces**, where `Ri_rack` = 9.3
> puts the flow in the buoyancy-dominant regime and where opposing jets meet.
>
> **What we conclude if it appears:** the rung reports `NOT A RESULT` and the
> steady treatment of this module is **measured** to be inadequate rather than
> assumed to be — which is a finding the campaign does not currently hold, and
> is the registered ground for a transient successor rung under its own
> pre-registration and its own cost. **What we conclude if it does not appear:**
> the steady treatment survives at these three resolutions, and `P-K2d-2` is
> reported as a LOSS. Either outcome is reported; neither is preferred; and
> **`NOT A RESULT` here is a result about the method, not a failed run.**

---

## 4. THE GATE

Graded quantities are K2a's (`K2a` §7), unchanged: **`T_in,i`** (mass-flow
weighted mean `T` over `rack_i_in`, per rack), **`T_in,max`** (the S13 monitored
quantity), and **`θ_i` = (T_in,i − T_sup)/ΔT_rack,i** (dimensionless
recirculation index). All are computed by in-pass function objects at the
monitor cadence so S13 reads them from the log alone.

### 4.1 The graded rows

| row | quantity | dim | triple? |
|---|---|---|---|
| **G1** | `T_in,max` — the worst-rack inlet temperature | K | yes |
| **G2** | `θ_max` = max over i of `θ_i` | – | yes |
| **G3** | `T_in,1` — the end rack, where end effects are largest | K | yes |
| **G4** | volume-averaged `T` over the cold aisle | K | yes |

### 4.2 The order of evaluation — standing rule 5, one-way

Evaluated in this order, and the order is part of the registration:

1. **Admission.** `G-MESHSIM` (§1.2), `G-CHECKMESH` and `G-MINCELL` (§5.1),
   `G-3D` (§5.2), the planted-zero control (§6.1), and the strict completion
   rule (§6.2). **Any failure → every graded row `NOT A RESULT`.**
2. **`G-CYCLE`** (§3.3) per level. **Any level not CONVERGED → every graded row
   `NOT A RESULT`.**
3. **Triple classification** per row. **`DIVERGENT`, `STAGNANT`, `OSCILLATORY`
   or `EXACT` → that row `NOT A RESULT`**, with the value, the triple and the
   order printed beside it, and **no GCI quoted.**
4. **`CONVERGING`** → the row is graded against §4.3, and the GCI at
   **`Fs` = 1.25** is printed.

**The gate is one-way. It may turn a `PASS` or `GATE FAIL` *into*
`NOT A RESULT`, and never the reverse.** No later section of this document, and
no addendum to it, may rehabilitate a row upward.

**Never quote a GCI when the three values are not monotone.** The comparator
refuses to emit one and prints `null`.

### 4.3 `G-ORDER` — the observed-order band, WIDENED, with the measurement that widened it

**Band: observed order `p` ∈ (0.5, 3.5).** A row whose triple is `CONVERGING`
with `p` inside the band and a monotone triple → **`PASS`**; `CONVERGING` with
`p` outside → **`GATE FAIL`**.

**This band is wider than the lab's usual (1.5, 2.5), it was widened BEFORE
compute, and the reason is a measurement rather than a preference.** The
report-only referent ran a three-grid convergence study on this exact flow class
— a data-centre room with racks and aisles — at a constant `r` = 1.31 on
298,535 / 668,242 / 1,486,077 tetrahedra, and reports (§4.1, READ AT SOURCE):
*"The local order of accuracy `p` ranges from **0.0197 to 27.70**, with a global
average of **6.583**."*

**A published study of this flow class could not obtain a clean order on its own
grids.** Registering (1.5, 2.5) into that class would be registering a miss, and
a band chosen after seeing our own `p` would be worthless.

**Two things stated plainly against the convenient reading.** First, **a wide
band is a WEAKER claim**, and a `PASS` inside (0.5, 3.5) establishes far less
than a `PASS` inside (1.5, 2.5) would; no K2d sentence may cite this `PASS` as
second-order accuracy. Second, **`p` = 6.583 — the referent's own global average
— lies OUTSIDE even this widened band**, so the band is not so wide that it
cannot fail, and the referent's own result would have failed it.

**One point of genuine agreement with the referent, noted because it is rare:**
its GCI is computed at **`Fs` = 1.25** (its eq. 7), the same factor of safety
this lab uses. And our **`r` = 1.5 is a coarser step than its 1.31**, which
helps an order estimate rather than hurting it.

#### 4.3a `A-SUBFIRST` — A REPORTING REQUIREMENT ON THE BAND'S LOWER LIMB

**This is NOT a gate change.** The band stays (0.5, 3.5), the one-way property of
§4.2 is untouched, and nothing here narrows anything or moves a verdict.

**The lower limb at 0.5 is the band's weak point, and a `PASS` there must not
pass silently.** On a nominally second-order scheme, an observed order below
about 1.0 is **not "converging slowly"** — it is evidence that something
*structural* dominates the discretisation error: an unresolved feature, a
discontinuity, or **mesh defects that do not scale down under refinement.**
Grading those `PASS` without comment conflates two very different situations.

> **REGISTERED: any row graded `PASS` with observed order `p` < 1.0 carries a
> printed annotation**, in the comparator's stdout, in the gate JSON as an
> `annotations` field on that row, and reproduced in the results record:
>
> *"`p` = ⟨value⟩ < 1.0 on a nominally second-order scheme. Sub-first-order
> convergence indicates an unresolved or structurally-dominant error source —
> an unresolved feature, a discontinuity, or mesh defects that do not scale
> down under refinement — and NOT merely slow convergence. This `PASS` is
> inside the registered band and stands; it may not be cited as evidence of
> asymptotic convergence."*

**The MECHANISM that motivates it, stated without leaning on any particular
measurement.** A Roache order estimate assumes the error is dominated by a term
that scales as `h^p`. **A defect population that does not DILUTE under
refinement violates that assumption directly**: if degenerate cells — small
determinant, concave, high skew — persist as a roughly constant *fraction* of
the mesh, or grow as one, their contribution to the error does not fall like
`h^p`, and the fitted `p` is pulled toward zero. **A sub-first-order `p` on a
nominally second-order scheme is that failure's signature**, and it is
indistinguishable, from the order alone, from an unresolved feature or a
discontinuity. All three want naming rather than absorbing into a wide band.

`G-CHECKMESH` at zero tolerance (§5.1) should prevent the mesh-defect route
here — K2d's rack row is axis-aligned rectilinear `blockMesh` with no refinement
transitions and no curved or cusped features — **but the annotation costs
nothing and is the diagnostic that catches it if that expectation is wrong.**

> **A WITHDRAWN CITATION, RECORDED RATHER THAN DELETED.** An earlier draft of
> this section motivated `A-SUBFIRST` on a T26 measurement of a defect
> population growing **faster** than its cell count (small-determinant ×3.37,
> concave ×5.06 against 2.66× cells). **Those figures are WITHDRAWN by the T26
> lane**: the experiment was confounded — it changed surface-refinement *depth*
> at a fixed base cell rather than refining the base cell, so it added octree
> transitions instead of refining, and **on the true triple both fractions
> FALL.** The citation is struck and this section is re-motivated on the
> mechanism above, **which does not depend on whether any particular rung
> exhibits it.** It is recorded rather than silently removed so a reader can see
> that the gate survived the loss of its original example.

### 4.4 THE REPORT-ONLY COMPARISON — computed, printed, and GRADING NOTHING

The comparator reads the digitised referent files and prints a comparison:

- `reference-data/wibron_2018_digitized/fig6_rack_temperatures.dat` — **15
  experimental rows** (8 front, 7 back; R5 and R6 carry `NODATUM`).
- `reference-data/wibron_2018_digitized/fig7_velocity_profiles.dat` — **17
  experimental rows** across L1(3), L2(3), L3(3), L4(4), L5(4).

**Every one of these is `REPORTED`, never graded.** They set no band, move no
verdict, and enter no tally. **The comparison is between different rooms** (§0.1)
and the printed block says so on its own face, in the output, not only here.

**Digitisation increments, carried from the files' own headers so no reader may
quote finer than the data was read (L-28):** temperature **±0.03 K**, velocity
**±0.007 m/s**, height **±0.005 m**. **Referent instrument uncertainties, read
from the paper:** temperature sensor DPX2-T1H1 **±1 °C**; velocity probe
**±2 % of reading ±0.02 m/s** (0.05–1 m/s) and **±5 %** (1–5 m/s).

**Title-page verification (L-144), performed and recorded.** The referent PDF at
`docs/papers/data_center_indoor_airflow/wibron_ljung_lundstrom_2018_en11030644.pdf`
was verified **by reading its title page on 2026-09-10**, not by filename, hash
or manifest: *"Computational Fluid Dynamics Modeling and Validating Experiments
of Airflow in a Data Center"*, Wibron, Ljung & Lundström, **Energies 2018, 11,
644**, doi:10.3390/en11030644, MDPI, received 24 Feb 2018 / accepted 12 Mar 2018
/ published 14 Mar 2018. Open access, CC-BY.

---

## 5. MESH GATES

### 5.1 `G-CHECKMESH` and `G-MINCELL` — the full check set, and why bare `checkMesh` is not enough

**Finding that produced this section, measured on 2026-09-10 and recorded here
because it reaches a graded case.** Plain `checkMesh` prints `Mesh OK.` on a mesh
that fails the face-tet and cell-determinant checks — those run only under
`-allGeometry -allTopology`. The K2b line uses the bare form throughout:
`build_k2bU3R3.py:168` runs `checkMesh > log.checkMesh 2>&1` and `:169`–`:170`
gate on `grep -q '^Mesh OK'`; `run_k2b.sh:59`–`:60` does the same; and
`K2b_runs/K2b3D_probe/log.checkMesh` records `Exec : checkMesh` with **no flags**
and **zero** face-tet or cell-determinant lines. `K2a` §6's *"checkMesh gates as
standing"* inherits the same lineage. **cfd's M6CP1 burned three smoke rungs on a
mesh its gate could never have refused.**

**THIS LIMB IS NOT THEORETICAL — IT HAS ALREADY CAUGHT A LIVE RUNG IN THIS
FAMILY.** The T26 lane ran the two check sets against each other on a real mesh
on 2026-09-10 (commit `015c620c5`): **bare `checkMesh` reported `Mesh OK.` while
`checkMesh -allGeometry -allTopology` on the same mesh reported `Failed 2 mesh
checks` — 2,320 small-determinant cells and 13,099 concave cells.** The
supervisor ordered that mesh fixed rather than the gate relaxed, and K2d
registers the same posture in advance: **if K2d's rack-row mesh fails the full
check set, the mesh is repaired and the level re-built — the tolerance is not
widened after seeing the answer.**

**The tolerance, registered now rather than discovered afterwards:** `G-CHECKMESH`
requires the full-check-set run to report **zero failed checks**. There is no
allowance for a nonzero count of small-determinant or concave cells, and none may
be introduced by addendum after compute — a level whose full check set fails is
**`NOT A RESULT`** and its mesh is rebuilt. The axis-aligned rectilinear
`blockMesh` of `K2a` §6 has no curved or cusped features and should produce
neither defect; if it does, that is a finding about the builder and is reported
as one.

**Registered for K2d:**

- **Every `checkMesh` invocation carries `-allGeometry -allTopology`**, and the
  **exact command line is written into `log.checkMesh`** so a reader can tell
  which check set produced the log.
- **`G-CHECKMESH`, provenance limb** — the comparator **REFUSES** a
  `log.checkMesh` that does not evidence both flags. That level's rows are
  **`NOT A RESULT`**, reason stated. *A log missing half the checks is not
  evidence of a sound mesh*, and the D-3D gate of §5.2 reads that same log.
- **`G-CHECKMESH`, VERDICT limb — the comparator reads `checkMesh`'s OWN
  verdict, and this limb exists because its absence was measured.** The T26
  lane found that its comparator *"would have graded — with a clean
  '3D CONFIRMED' — a mesh whose own quality tool had failed it"*, because
  nothing in it read the `Failed N mesh checks` line: the directions line was
  perfect while 2,320 small-determinant and 13,099 concave cells sat under it.
  **Checking directions, patch types and minimum cell size does not check
  whether `checkMesh` passed the mesh.** Registered:
  - the comparator parses the **`Failed N mesh checks`** line and the
    **`Mesh OK.`** line explicitly;
  - **`N > 0` → that level's rows `NOT A RESULT`**, with every failed check line
    printed;
  - **`Mesh OK.` is NOT accepted as a pass on its own** — it is precisely what
    bare `checkMesh` prints on a mesh the full set fails;
  - **neither line present → `NOT A RESULT`.** Mesh quality is then *unmeasured*,
    and **unmeasured is not passing.**
  - **Tolerance registry: EMPTY, i.e. zero tolerance** (§5.1's tolerance
    paragraph). Any future entry must carry its own written justification and be
    registered **before** the freeze — the gate is never relaxed to let a mesh
    through after the mesh has been seen.
- **`G-MINCELL`** — minimum cell dimension is reported **per named feature** and
  gated against a registered floor. The features, named now: **rack front face**,
  **rack rear face**, **rack side faces**, **supply tile face**, **return face**,
  **cold-aisle/rack interface band**, **hot-aisle/rack interface band**,
  **floor boundary layer**, **ceiling boundary layer**, **row-end margin**.
  **Floor: 5.0 mm** at every named feature on every level.
  **Justification, registered now while gates are open:** K2a §6 sets a 60 mm
  coarse base cell with 30 mm refinement bands at active faces; at L3 the base
  cell is 60/1.5² = **26.7 mm** and the refined band **13.3 mm**. A floor of
  5.0 mm sits a factor **2.7 below** the finest intended dimension, so it cannot
  be tripped by the intended build and can only be tripped by a degenerate one —
  which is what it is for. cfd's finding is the reason a floor exists at all: a
  cusped trailing edge passed **both** check sets and still destroyed the M6, so
  a geometry limb independent of `checkMesh` is required.
  Below floor at any named feature → that level's rows **`NOT A RESULT`**.

### 5.2 `G-3D` — the dimensionality gate

**T4e proved a 2D axisymmetric wedge and the entire T23G2 line proved 2D wedges
on 2026-09-10, all while carrying 3D language.** This rung will not repeat it.

Per level, the comparator:
- reads the **verbatim** line `Mesh has N geometric (non-empty/wedge) directions
  (i j k)` from `log.checkMesh` and records it into the gate JSON as a string;
- **censuses patch types** from `constant/polyMesh/boundary` and records the
  counts of `empty` and `wedge`;
- turns **every graded row `NOT A RESULT`** if `N ≠ 3`, or if any `empty` or
  `wedge` patch is present at any level.

**Two rules on how that line is read, and both are registered because both have
already caught somebody.** (i) The same log prints `Mesh has 3 solution
(non-empty) directions (1 1 1)` a few lines away, and **for a wedge mesh it says
3 while the mesh is 2D** — the comparator matches the `geometric
(non-empty/wedge)` line **specifically** and never the first `directions` hit.
(ii) **`blockMeshDict` is never read for this.** The gate reads what was built,
not what was asked for.

---

## 6. CONTROLS AND COMPLETION

### 6.1 Planted-zero control — plants, reads back, and REFUSES

**A zero from a reader not shown able to see a non-zero is not evidence.**

For **every graded row on every level**, the comparator plants a known
perturbation of **`1.234e-03`** (the family constant) into the field on disk by
index, re-reads it **through the production reader from disk**, and asserts the
reader returns the planted value. **If the reader cannot see the plant the
comparator REFUSES — exit 2 — and grades nothing.** It does not degrade, and it
does not report a zero it has not earned. A negative arm re-reads the unplanted
field and asserts the reader returns the original value.

### 6.2 Strict completion rule — all of it, including the age guard

A level is DONE only if **all** hold: `rc = 0`; an `End` line in `log.solve`;
**last written time == `endTime`**; the required fields present at `endTime`;
`ExecutionTime` count consistent with the steps written; and **every field at
`endTime` NEWER than that case's own `0/T`** — the **age guard**, because `0/T`
is touched last at launch and so dates the run allowed to produce the answer.

**A run that fails any clause is not done, and the comparator REFUSES (exit 2)
rather than grading it.** The instrument is `mark_done_k2d.py`, and the
comparator **calls** it rather than reimplementing its clauses.

### 6.3 Clause 7 — the launch guard, PROVED FIRING BY EXECUTION

The guard **refuses to launch into a case directory where `0/` or any time
directory already exists.**

**It is not enough that the clause is present in the file.** Before freeze the
guard is demonstrated **BY EXECUTION, in both directions, on real paths**: it
must **refuse** a directory seeded with a `0/` and it must **stay silent** on a
clean one, and both invocations and their exit codes are recorded in
`K2d_CLAUSE7_DEMONSTRATION.txt` in the run tree. A clause that has never been
executed is a claim, not a guard.

### 6.4 Exit map

**`0 = EXIT_OK`, `1 = EXIT_FAIL`, `2 = EXIT_REFUSE`** — T3's convention, the
canonical one. **The exit code does not carry the verdict**, and the record must
not read it as one: T16c returned `rc = 0` while every row read `NOT A RESULT`,
and T25R6c-R2 crashed to `1` after grading correctly. The verdict is read from
the gate JSON and stdout.

### 6.5 Mutation matrix

Every instrument carries a mutation matrix run before freeze: a control arm that
must stay silent, and one corruption arm per limb that must fire. **`__pycache__`
is cleared between every run** — stale bytecode has inverted mutation tests in
this lab. Negative arms registered explicitly, per the supervisor's brief:
a `log.checkMesh` produced **without** the flags must be refused, and a
**sub-floor minimum cell** must be caught.

---

## 7. COST — rule 12, COSTED BEFORE COMPUTE

### 7.1 The two bases, reconciled, and the wider bracket carried

**Basis A — K2a's own §10 estimate**, at the levels it specified: 3D coarse
**167** core-min at 0.20 M, 3D fine **933** core-min at 0.70 M.
**Basis B — the K2b pilot's MEASURED rate**, 4.8e5 cell·iter/(core·s) =
**2.88e7 cell·iter/core-min** on turbulent SST on this box.

**They reconcile.** Basis A's 167 core-min at 0.20 M implies **24,048**
iterations under basis B, and 933 at 0.70 M implies **38,386** — a consistent
iteration ladder rising with mesh, not two incompatible numbers.

| level | cells (target) | **POINT** core-min | implied iters | basis |
|---|---:|---:|---:|---|
| L1 | 59,259 | **33** | 16,038 | B, scaled from A |
| L2 | 200,000 | **167** | 24,048 | **A — K2a's approved figure, unchanged** |
| L3 | 675,000 | **900** | 38,400 | A, rescaled 933 × (0.675/0.70) |
| **ladder** | | **1,100** | | |

**Carried bracket, not the point estimate: 1,150 – 1,650 core-min** including
controls and the rate probe. **$0.98 – $1.41 derived** at $0.0513/core-h —
**derived, never measured**; the box cannot read its own billing.

**The added cost of the third level is ~33 core-min on an approved ~1,067 for
the approved pair — about 3 %.**

**Honest limits on this cost, stated because a cost is not measured until a
record backs it.** (i) Basis B's rate was measured in **2D**; it has never been
measured in 3D on this box, which is exactly why §7.2 exists. (ii) Both bases
assume the steady solve **converges**; `K2a` §5 states its own steady totals are
*"a floor"*, and if `G-CYCLE` fires the spend buys a `NOT A RESULT` and the
transient successor is 5–10× (K2a's planning figure, labelled estimate).

### 7.2 `STAGE-1` — the 3D rate probe, and L3 is CONDITIONAL on it

**Registered as a stage, not an intention.** L1 runs **first and alone**. From
its log the comparator measures the **actual 3D** cell·iter/core-min rate and
re-derives the L2 and L3 POINT figures from it.

> **If the re-derived ladder total exceeds 1,650 core-min — the top of the
> carried bracket — L3 IS NOT LAUNCHED.** The rung stops, reports `PENDING` on
> its ungraded rows with the measured rate and the re-derived cost printed, and
> goes back to the supervisor for a re-cost. **An overrun stops the run; it does
> not get a new budget.**

**A rung that discovers its own cost after launching its most expensive level
has discovered it too late.**

### 7.3 Cap, and the hang guard which is NOT the cap

**Cap: 1,650 core-min for the ladder.** Under Sanaa's 16:50Z words cap-*stops*
are exempt for 3D runs; the run is costed here regardless and calibrated against
actuals at completion into `docs/COST_CALIBRATION.md` (rule 12).

**The timeout is a HANG GUARD and is deliberately NOT equal to any cap or POINT
multiple that could be mistaken for a budget stop.** It is set at **≈3× POINT**
per level:

| level | ranks | POINT | **timeout (hang guard)** |
|---|---:|---:|---:|
| L1 | 4 | 33 core-min | **1,485 s** |
| L2 | 8 | 167 core-min | **3,757 s** |
| L3 | 8 | 900 core-min | **20,250 s** |

**Why 3× and why that matters.** A timeout numerically equal to a cap, or to a
round multiple like 2.0000× POINT, makes a *labelled* hang guard function as a
*budget stop*, and a reader cannot tell which fired — this was found in T4e's
fine leg on 2026-09-10. **3× POINT is far enough above any plausible honest
overrun that a trip means the solver has hung, not that it was slow.** The cap is
enforced by §7.2's staging and by the cost record, never by the timeout.

**Ranks: 8 maximum, and more than 8 requires the supervisor's coordination** —
T4e's fine leg holds a core for ~40 more hours and T26 will want capacity.

---

## 8. WHAT THIS RUNG CANNOT REACH

- **It is not validation and establishes no agreement with any experiment** (§0.1).
- **It measures grid convergence of one module at one configuration** — `N` = 4,
  one row, K2a's defaults. It says nothing about other `N`, two-row layouts,
  containment, raised floors or plena.
- **It cannot measure model-form error.** `P-K2d-1` is report-only and inherits
  the configuration mismatch.
- **A `PASS` inside the widened (0.5, 3.5) band is a weak claim** and is not a
  claim of second-order accuracy (§4.3).
- **Closure is necessary, never sufficient** (`K2a` §8): a solve with the aisle
  flow entirely wrong still closes once converged. No K2d sentence cites closure
  as evidence of circulation.

---

## 9. FREEZE BLOCK

| item | value |
|---|---|
| `GRADING_PATH_FREEZE_COMMIT` | recorded in THIS freeze commit's message |
| `build_k2d.py` | ~~`36a2f3e3ad2133f7b7a7af77d657fea9047edc25`~~ STRUCK -> **`0be84519c033e5b663e63043bc01bfa0a91319d5`** (re-pinned under the granted VERIFICATION_CHARTER section 2d.1 repair; see Addendum 2) |
| `analyse_k2d.py` | `f61ab074425f2664929abb15cce6e0f403cb5b9f` |
| `mark_done_k2d.py` | `0a095552afc051b3ce3795cb471deb145da53db2` |
| `scripts/roache_triple.py` | `78e56a3bc2c2a07571db1cf3c91f4c2c31f246b8` |
| referent PDF sha256 | `4de4798ed5eed60feda123c7a2398674a6a9177f44906175847d90f5227d7b77` |

**The grading path is fixed at the freeze commit.** The comparator verifies each
frozen file **is** the file that ran by hashing it against the committed blob,
and **REFUSES (exit 2)** rather than grading if any digest fails to reproduce.

---

## 10. ORDER OF OPERATIONS — binding

1. This document committed, then **frozen by sha by the heat-transfer supervisor**.
2. Instruments written; **mutation matrix run**, `__pycache__` cleared between runs.
3. **Clause 7 demonstrated BY EXECUTION**, both directions, recorded.
4. **Supervisor reads every measurement script AS A DIFF, personally.**
5. **Freeze commit verified present on `main`** — the commit *is* there, not meant to be.
6. `STAGE-1`: L1 only. Rate measured, L2/L3 re-derived, §7.2 stop evaluated.
7. L2, then L3, if and only if §7.2 permits.

**Detachment:** `setsid`, with **`rc` captured INSIDE the wrapper** — `setsid
timeout cmd` exits 0 for every outcome, so an `rc` captured around the `setsid`
line is meaningless.

**On launch, reported immediately:** pid, cwd, registration sha, ranks, cap in
core-minutes, timeout.

---

## 11. WHAT THIS DRAFT DOES NOT DECIDE

1. **Whether the Wibron room is built as a validation rung.** §12 is a proposal
   for Sanaa's desk. **A lane does not register it and no agent's message is her
   approval.**
2. **Whether a transient successor follows a `G-CYCLE` fire.** That is a new
   rung, a new registration and a new cost.
3. **Whether K2bU3R3's mesh acceptance needs revisiting** in light of §5.1. The
   supervisor has booked it as a disclosure; this document only records the
   measurement.

---

## 12. POINTER — the validation successor is NOT registered here

The rung that would earn a validation claim is drafted separately as a proposal
for Sanaa's desk: the **Wibron SICS ICE Module 1 room** — 5.084 × 6.484 × 3.150 m,
two rows of five racks, four CRAC units, hard floor, partial hot-aisle
containment — against **32 armable experimental rows**. **It is a proposal. It is
not registered, not frozen, and nothing in this document authorises any compute
against it.**

---

---

## 13. PRE-FREEZE AMENDMENT 1 — 2026-09-10, at the supervisor's §3 diff read

**This document is NOT FROZEN, so this is a legal pre-compute amendment under
standing rule 2, which requires the condition and how it was checked to be
stated.**

**CONDITION:** *"`verification/runs/F14-cooling-ladder/K2d_runs/` does not
exist."*
**HOW CHECKED:** by its absence on disk with `test -d`, re-run immediately
before this amendment was written, 2026-09-10. It did not exist. **No compute
has been spent against this document; no gate is being changed after an
answer was seen.**

**Base version amended:** commit `c1ef8385`, blob
`0bae89b0a571835157ddded8064ed87689064019`.

### What changed, and why

**1. §3.3a — `G-CYCLE` did not look where `P-K2d-2` points.** The supervisor's
diff read found that the limb sampled `T_in,max`, a **cold-aisle** quantity,
while the prediction names the **hot-aisle** rack faces. A prediction whose
detector cannot see the predicted location is not falsifiable, and the rung
would have reported a `LOSS` that was really a blind spot. **Added `U_ha`**, a
hot-aisle volume-averaged velocity magnitude at the predicted location, with its
own registered 0.5 % threshold and its justification for differing from S13's
0.02 %. Either quantity cycling or drifting now voids every graded row.

**2. §3.3b — the cycle detector is now itself planted-zero controlled.** A
positive arm (a planted sinusoid must be caught), a negative arm (a planted
clean monotone series must not be called a cycle), and a **measured detection
floor** reported beside any `CONVERGED` reading. The comparator refuses at
exit 2 rather than grading a rung whose detector has not demonstrated it works.

**3. §4.3a — `A-SUBFIRST`, a REPORTING requirement, not a gate change.** The
band stays (0.5, 3.5) and the one-way property is untouched. A `PASS` with
`p` < 1.0 now carries a printed annotation naming sub-first-order convergence as
evidence of a structurally-dominant error source rather than slow convergence.
Motivated by T26's measurement that its mesh-defect population grows faster than
its cell count, which drives `p` down.

**4. §5.1 — `G-CHECKMESH` gained a VERDICT limb.** It now reads `checkMesh`'s
own `Failed N mesh checks` line, refuses on `N > 0`, refuses when neither
verdict line is present (*unmeasured is not passing*), and **does not accept
`Mesh OK.` on its own**. Added because the T26 lane measured that its comparator
would have graded a mesh its own quality tool had failed, printing
"3D CONFIRMED" over 2,320 small-determinant and 13,099 concave cells.

### What did NOT change

**No band, threshold, floor, cap, label or verdict was widened, moved or
loosened.** §4.2's evaluation order, its one-way property and its GCI refusal on
non-monotone values are untouched. The order band's numeric limits are
unchanged. Every threshold added here is **new**, not a relaxation of an
existing one, and each is set **before** any compute exists to fit it to.

---

## 14. PRE-FREEZE AMENDMENT 2 — 2026-09-10: **I BROKE MY OWN AMENDMENT CONDITION, AND THIS SECTION SAYS SO RATHER THAN QUIETLY RESTATING IT**

**The condition this document has cited twice — *"`K2d_runs/` does not
exist"* — IS NOW FALSE, and it was made false BY ME**, when I created
`verification/runs/F14-cooling-ladder/K2d_runs/` to hold this rung's
instruments. A reader checking §0's condition today will find it fails.

**It is disclosed rather than rewritten, because a condition that is silently
restated the moment it becomes inconvenient is not a condition.**

### 14.1 What is and is not affected

- **§0's and §13's amendments are NOT retroactively invalidated.** Each was
  checked with `test -d` and was **true at the moment it was made**. The record
  of that check stands.
- **The wording was the wrong proxy for the thing it was protecting.** Standing
  rule 2's concern is *first compute* — that no gate is changed after an answer
  exists to fit it to. A directory holding a comparator and a completion
  instrument is not an answer.

### 14.2 THE CONDITION, RESTATED PRECISELY, and it is stricter not looser

For every further pre-freeze amendment to this document, the condition is:

> **No case directory exists under `verification/runs/F14-cooling-ladder/K2d_runs/`
> — no `K2d_L1`, `K2d_L2` or `K2d_L3` — no `STATUS.*` file, no `log.solve`, no
> time directory and no field.** The run tree contains instruments and their
> selftest output only.

**How it is checked:** by listing the run tree on disk and asserting that every
entry is an instrument or an instrument artifact, never by asking git and never
by reading a document. **This is a stricter test than the one it replaces** — the
old wording would have been satisfied by an absent directory while saying
nothing about a case tree created beside it under another name.

**Checked at this amendment, 2026-09-10: the run tree holds
`mark_done_k2d.py` and no case directory, no `STATUS.*`, no `log.solve`, no
time directory and no field. ZERO solver core-minutes have been spent against
this document.**

### 14.2a THE BOUNDARY — this manoeuvre must never become routine

**Amending a condition that your own action falsified is a manoeuvre one step
away from an abuse**, and it is worth naming the step. The general form —
*"the condition I registered has become inconvenient, so I have replaced it"* —
is how a pre-registration stops meaning anything.

**The only thing that makes it legitimate here is that the replacement is
STRICTER and better aimed at standing rule 2's actual concern — FIRST COMPUTE,
not directory existence.** A restatement that loosened the condition, or that
aimed at the same concern less precisely, would not be legitimate no matter how
it was disclosed. **Disclosure is necessary and is not sufficient.**

**The T26 lane faced the identical choice tonight and went the other way**,
declining to create its run tree at all, because T26's registration makes the
directory's *absence* itself load-bearing at freeze (its §12 item 3). **Both
choices are defensible, and the difference is not taste: it is what each
registration made load-bearing.** K2d's condition was aimed at first compute and
the directory was a proxy for it; T26's condition is aimed at the directory. A
reader comparing the two rungs should not have to guess why they diverged, so
it is written here.

### 14.3 What this amendment does NOT do

**It changes no gate, band, threshold, floor, cap or label**, and it does not
touch §4.2's one-way property. It restates an amendment-eligibility condition
and discloses that the earlier wording was broken. **A future reader who finds
`K2d_runs/` populated with cases must treat every gate in this document as
closed**, whatever this section says — first compute closes them, and no
disclosure reopens them.

---

## 15. ADDENDUM 1 — 2026-09-11. **GATES ARE CLOSED. THIS ALTERS NO GATE, THRESHOLD, CAP OR LABEL.** A §2d.1 repair to `build_k2d.py`, and the failed launch that forced it

**Gates closed at the freeze commit `e7979e29b706c1f4b91404c04731f29a80f128bd`.
This is a dated addendum under standing rule 2, not an amendment.** It changes
no gate, no band, no threshold, no floor, no cap and no label. Nothing above is
edited; **lines whose number changed above this section: 0.**

### 15.1 THE FIRST LAUNCH, RECORDED BEFORE ANYTHING ELSE

| | |
|---|---|
| launched | **true, by witness** — `log.solve` mtime `1789090917` strictly greater than the before-launch captured `1789090915`; corroborated by a live solver pid. No absolute time, no slack |
| pid | **1890509** |
| cwd | `verification/runs/F14-cooling-ladder/K2d_runs/K2d_L1` |
| ranks | 4 |
| timeout | 1,485 s (hang guard; did not trip) |
| outcome | **`rc = 1`, `note=SOLVER_NONZERO_EXIT`, wall 1 s** |
| **cost** | **0.067 core-min, MEASURED** from `STATUS.K2d_L1` |

**This was `launched: true` with a fault, not a failed launch.** The solver
started, read its dictionaries and exited nonzero. Collapsing that into
`launched: false` would have hidden a finding about the case behind a launch
failure.

### 15.2 THE DEFECT, AND A SECOND ONE THE REPAIR'S OWN NEW CONTROL THEN FOUND

**Defect 1, which killed the launch.** `buoyantBoussinesqSimpleFoam` with
`kOmegaSST` requires a wall-distance method and the builder emitted none:

> `FOAM FATAL IO ERROR: Entry 'method' not found in dictionary "system/fvSchemes/wallDist"`

**Defect 2, found by the new control described in §15.4 and not by any human
re-reading.** With `wallDist` supplied the solver got past parsing and then
aborted on `Different dimensions for '(a + b)': [1 -1 -2 0 0 0 0] !=
[0 2 -2 0 0 0 0]`. **In this solver `p_rgh` and `p` are KINEMATIC** (m²/s²),
not pressures in Pa, and **`alphat` is a kinematic turbulent diffusivity**
(m²/s), not a dynamic one — and its wall function is the incompressible
`alphatJayatillekeWallFunction`, not `compressible::alphatWallFunction`. All
four were read from a **committed case of the same solver**
(`K2b_runs/K2bP_coarse/0.orig/{p_rgh,alphat}`) rather than recalled.

### 15.3 THE FOUR §2d.1 CONDITIONS, EACH CHECKED

**Granted by the heat-transfer supervisor, 2026-09-11.**

1. **A demonstrable error, not a preference.** The solver cannot start. There is
   no version of this rung that runs without these entries.
2. **Established by an instrument INDEPENDENT OF THE HYPOTHESIS, one that grades
   nothing** — **OpenFOAM's own dictionary reader and dimension checker.** The
   charter calls this the load-bearing condition. It holds here in a *stronger*
   form than in K0cS, the case §2d.1 was cut from: that repair was found by a
   heat balance, a near-identity that at least produces a number. **A dictionary
   parser has no numerical opinion at all** and cannot have been selected to
   move a verdict in a wanted direction.
3. **Disclosed, instrument named, and WHAT MOVED quantified: NOTHING MOVED.** No
   graded row existed before the repair. No band, threshold, floor, cap or label
   changes.
4. **Pre-repair values recorded beside the published ones: THERE ARE NONE.** The
   solver produced no field, no time directory and no value.

**The contrast §2d.1 exists to forbid — *"the numbers looked wrong, so the band
was widened"* — is absent: no number exists.**

**BOTH READINGS ARE RECORDED, and the conservative one was taken.** §2d.1's
trigger is *"a change on the grading path made after the FIRST GRADED SOLVE."*
**There has been no graded solve** — one second, no field, nothing graded — so
§2d arguably never bit at all. **The repair is nonetheless taken under §2d.1
with all four conditions recorded**, because where both routes are open, putting
the repair on the record under discipline is worth more than resting it on a
definitional escape.

### 15.4 THE GENERALIZABLE DEFECT — the selftest had eight arms and none started a solver

**This is the finding, and it is worth more than the two fixes.**

The builder's eight original arms tested its **outputs**: that files exist, that
`0/` does not, that the block count is right. **Not one started a solver.** A
case can be **structurally complete and dictionary-incomplete**, and no amount
of checking a builder's outputs against that builder's own intentions can see
it — *both sides of the comparison share the omission.*

**A ninth and tenth arm are added: build a real mesh, run the real solver for
one iteration, and require that it gets past dictionary parsing AND reaches a
`Time =` step.** It costs a few seconds and is the cheapest available insurance
against the entire class.

**It earned itself immediately: defect 2 above was found by that arm, not by a
human re-reading the file.** The arm that was added because of defect 1 caught
defect 2 on its first execution.

### 15.5 The re-pinned instrument

`build_k2d.py` changes blob. `analyse_k2d.py`, `mark_done_k2d.py` and
`scripts/roache_triple.py` are **untouched** and their §9 pins stand. The new
`build_k2d.py` blob is recorded in the re-freeze commit's message, since a file
cannot contain its own hash.

---

*Nothing was sent, filed, uploaded, registered, posted or commented outside this
box (rule 7). Solver compute spent against this document to date: **0.067
core-min, measured.***

---

## 16. ADDENDUM 3 — 2026-09-11. The MEASURED 3D rate, the §7.2 re-derivation, and **A PREDICTION ABOUT L3 REGISTERED BEFORE L3 RUNS**

**Gates closed. This addendum records MEASUREMENTS and one PREDICTION. It
alters no gate, band, threshold, floor, cap or label.** Nothing above is
edited; **lines whose number changed above this section: 0.**

**WRITTEN AND COMMITTED BEFORE `K2d_L3` IS LAUNCHED.** That is the whole
evidentiary content of §16.3: a prediction stated afterwards is worthless.

### 16.1 THE MEASURED 3D RATE — the bracket survived contact, the point estimate would not have

Derived from **L1's own artifacts**, not from any relayed figure:
58,368 cells × 3,000 iterations ÷ (235 s × 4 ranks) — which reproduces
`STATUS.K2d_L1`'s `core_min = 15.667` exactly.

| | |
|---|---|
| **measured 3D rate** | **1.863e5 cell-iter/core-s** |
| basis it replaces | **4.8e5**, K2b's pilot rate, **measured in 2D** |
| **derate** | **2.577×** |

**§7.1 named this gap in advance and refused a point estimate because of it:**
*"Basis B's rate was measured in 2D; it has never been measured in 3D on this
box, which is exactly why §7.2 exists."* It had not been, and 2D was optimistic
by two and a half times. **A bracket carried honestly survived the measurement;
a point estimate would not have.**

### 16.2 THE §7.2 RE-DERIVATION — the stop does NOT trigger

| level | cells (BUILT) | core-min at the measured rate |
|---|---:|---:|
| L1 | 58,368 | **15.667 — MEASURED** |
| L2 | 196,992 | 52.9 |
| L3 | 664,848 | 178.5 |
| **ladder** | | **247.0**, **$0.211 derived** (never measured) |

**247.0 against the 1,650 cap. §7.2's stop does not fire, no cap is exceeded,
and no overrun exists to name.**

### 16.3 ⚠ WHY THE LADDER IS CHEAP, AND THE PREDICTION THAT FOLLOWS FROM IT

**THE 247 core-min IS A SYMPTOM, NOT A SAVING, AND IT MUST NOT BE READ AS
EFFICIENCY.**

**§7.1's cost basis implied iterations RISING with mesh — 16,038 / 24,048 /
38,400. The frozen `build_k2d.py` writes `endTime 3000` FLAT at every level**
(`build_k2d.py:387`). The ladder is cheap because **L3 is under-iterated by up
to 12.8× against its own registered cost basis**, not because the solver is
fast. *A cost that comes in at 15 % of estimate because the work was not done
is not a saving.*

**A flat `endTime` is not automatically wrong.** A Roache triple requires each
level to be converged **to its own steady state**; it does not require equal
iteration counts. If all three plateau by 3,000, the triple is valid and 3,000
was merely generous at L1.

**It is wrong only if the finer levels have not plateaued — and then it is
badly wrong, not marginally.** The inter-level differences would measure
**convergence state rather than discretisation error**, and the observed order
would be meaningless.

> ### REGISTERED PREDICTION `P-K2d-3`, stated before `K2d_L3` runs
>
> **The registration's own cost basis expected iterations to rise with mesh;
> the frozen builder holds them flat. Its authors therefore implicitly
> predicted that 3,000 iterations would be insufficient at the finest level.**
>
> **`P-K2d-3` predicts: `K2d_L3` reads `DRIFTING` or `CYCLING` under
> `G-CYCLE` on at least one of the two monitored quantities, and is the level
> most likely of the three to do so.**
>
> **If it HOLDS**, the rung is **`NOT A RESULT`** under standing rule 5 clause
> (1), and that is **a measurement about the method, not a failed run** — the
> registered ground for a successor with a per-level `endTime`, under its own
> pre-registration and its own cost.
> **If it LOSES**, all three levels plateaued at 3,000 and the flat `endTime`
> was simply generous at L1.
>
> **`P-K2d-3` grades nothing and moves no verdict.** It is scored HIT or LOSS
> and reported either way.

**NOTHING IS CHANGED TO AVOID THIS.** Lengthening L3's `endTime` now would
alter the grading path after first compute, which standing rule 2 forbids and
which `build_k2d.py`'s pin would in any case refuse. **`G-CYCLE` was registered
before compute precisely for this condition, is evaluated per level ahead of
any triple, and will catch it.** The system is being allowed to work.

### 16.4 A COMPLETED RUN THAT WAS *NOT DONE*, AND THE INSTRUMENT CAUGHT IT

`K2d_L1` finished with **`rc = 0`, 3,000 iterations and an `End` line** — and
`mark_done_k2d.py` **REFUSED it**: *"no time directory beyond 0"*. A **parallel**
run leaves its fields in `processor*/3000/`, so the case root holds no time
directory and rule 4's clauses 3 and 4 cannot pass. The launcher did not
reconstruct.

**This is the clause the strict completion rule exists for**, and the failure
mode is the dangerous one: everything that is easy to look at said the run was
fine.

Repaired by `reconstructPar -latestTime`; **L1 is now DONE on all six clauses
including the age guard**, its fields genuinely postdating `0/T`. The launcher
now reconstructs before writing `STATUS`. `launch_k2d.sh` is **not** a pinned
file and reconstruction is post-processing, not a grading-path change.

### 16.5 Cost calibration (rule 12), for the levels that have run

| level | predicted (§7.1 POINT) | actual | ratio | attribution |
|---|---:|---:|---:|---|
| L1 | 33 core-min | **15.667 measured** | **0.475×** | not efficiency — §7.1 assumed 16,038 iterations and the builder ran 3,000 (§16.3) |

A full ladder row lands in `docs/COST_CALIBRATION.md` at rung completion, per
rule 12, with the same attribution stated rather than absorbed into the ratio.

---

*Nothing was sent, filed, uploaded, registered, posted or commented outside this
box (rule 7). Solver compute against this document to date: **15.734 core-min,
measured** (0.067 failed launch + 15.667 L1); `K2d_L2` in flight.*

---

## Addendum 2 — 2026-09-11, re-pin of `build_k2d.py` under a granted section 2d.1 repair

**Lines whose number changed above this section: 0.** The section 9 row for
`build_k2d.py` was STRUCK IN PLACE on one line and its replacement written
beside it; no line above this section moved, and no gate, band, threshold,
floor, cap or label is altered by this addendum.

**Ruled by heat-transfer-supervisor, personally, against the charter read at
source.** The section 2d.1 four-condition test is discharged in Addendum 1 and
is not restated here. This addendum records only the mechanical consequence:
the grading path's `build_k2d.py` entry moves from `36a2f3e3` to `0be84519`.

**TWO defects were repaired, and the second is the one that matters.**

1. `wallDist { method meshWave; }` was absent; `kOmegaSST` cannot start without
   it. Found by **OpenFOAM's own dictionary reader** at launch — pid 1890509,
   `rc=1`, `SOLVER_NONZERO_EXIT`, wall 1 s, **0.067 core-min MEASURED**.
2. With that supplied the solver parsed and then aborted on
   `Different dimensions for '(a + b)': [1 -1 -2 0 0 0 0] != [0 2 -2 0 0 0 0]`.
   **In `buoyantBoussinesqSimpleFoam`, `p_rgh` and `p` are KINEMATIC** (m^2/s^2),
   not pressures in Pa, and **`alphat` is a kinematic diffusivity** whose wall
   function is the incompressible `alphatJayatillekeWallFunction`, not
   `compressible::alphatWallFunction`. All four were read from a committed case
   of the same solver, `K2b_runs/K2bP_coarse/0.orig/`, not from recall.

**Defect 2 was caught by an arm added because of defect 1, before it reached the
box.** The builder's original eight selftest arms could not have found either:
**they test the builder's outputs against the builder's own intentions, and both
sides of that comparison share the omission.** Only the solver's own reader sits
outside that loop. The selftest now carries **16 arms, all green, and requires
the solver to reach a `Time =` step.**

**Nothing moved and no pre-repair values exist** — no field, no time directory
and no graded row were produced before the repair. The contrast section 2d.1
forbids, *"the numbers looked wrong, so the band was widened"*, is absent: no
number existed and no band was touched.

---

## 17. ADDENDUM 4 — 2026-09-11. **K2d IS RETIRED.** The rung could never have been graded, and the timeout is not why

**Document version 1.3 → 1.4.**
**Lines whose number changed above this section: 0.** Nothing above is edited.
**Gates were closed at the freeze commit `e7979e29b706c1f4b91404c04731f29a80f128bd`.**
This is a dated addendum under standing rule 2 and standing rule 6. **It alters
no gate, no band, no threshold, no floor, no cap and no label. It records that
they could never be evaluated.**

Ruled by heat-transfer-supervisor 2026-09-11, on a triage carried out by a
heat-transfer `lab-lane` from the artifacts. The supervisor verified both
blockers of §17.2 personally before accepting them (`SUPERVISION_CHARTER.md` §3
check 3).

### 17.1 THE THREE VERDICTS

| subject | verdict |
|---|---|
| **`K2d_L3`** | **`NOT A RESULT`** |
| **Every registered quantity of K2d — `G1`, `G2`, `G3`, `G4` — at ALL THREE LEVELS** | **`NOT A RESULT`** |
| **The rung** | **`BLOCKED` on a defective frozen grading path** |

**`K2d_L3` fails standing rule 4 on five of its six conjuncts**, measured from
`log.solve` and `STATUS.K2d_L3` at their retired path (§17.6): no `End` line;
last written time 995 ≠ `endTime` 3000; no fields at `endTime`; 994
`ExecutionTime` lines ≠ 3000; and no field exists to age-guard. Only clause 1's
negation is unambiguous — `rc = 124`, not 0.

**L1 and L2 are as ungradeable as L3, and the ground is the instrument, not the
timeout.** `G-CYCLE` is evaluated per level and **before** any triple is
classified (§4.2 step 2), so standing rule 5 clause (1) bites at every level.
Its two inputs were never written (§17.2) and **cannot be reconstructed**: every
level wrote fields only at `endTime` under `writeInterval 3000`, and a
400-iteration monitor series at a 50-iteration cadence cannot be recovered from
one end-of-run snapshot. There is no re-analysis that rescues L1 or L2.

### 17.2 THE TWO BLOCKERS — both on the pinned grading path, both independent of the timeout

**BLOCKER 1 — the gate's own inputs were never written.**

This document registers both monitored quantities as in-pass function-object
output:

- `:290` — `U_ha` is *"written by an in-pass function object at the **same
  50-iteration cadence** as `T_in,max`, so `G-CYCLE` reads it from the log
  alone."*
- `:413` — `T_in,i`, `T_in,max` and `θ_i` are *"all computed by in-pass function
  objects at the monitor cadence so S13 reads them from the log alone."*

**The pinned builder emits no function objects.** `build_k2d.py` writes
`system/controlDict` at `:384`–`:385`; `grep -c functions` returns **0** on all
three built `system/controlDict` files, which end at `runTimeModifiable false;`.
The only "functions" matches in `build_k2d.py` are the prose words *"wall
functions"* at `:50` and `:203`. **No `postProcessing/` directory exists anywhere
under `K2d_runs/`**, no `T_in*.dat`, no `U_ha` output, and no matching string in
any of the three `log.solve` files. `G-CYCLE` has no input at any level.

**BLOCKER 2 — the pinned comparator has no grading path.**
`analyse_k2d.py:613`–`:619` is a two-branch stub: `--selftest`, or a
**hardcoded** `EXIT_REFUSE` printing *"no K2d case directory exists yet."*
`main()` never reads a case directory. `read_checkmesh`, `read_patch_census`,
`gate_mincell` and `built_cell_count` all take a `case_dir` that `main()` never
supplies. Every gate function exists and is exercised by 31 selftest arms;
**nothing wires any of them to a run.**

**All four §9 pins reproduce byte-exact on disk** — `build_k2d.py`
`0be84519c033e5b663e63043bc01bfa0a91319d5`, `analyse_k2d.py`
`f61ab074425f2664929abb15cce6e0f403cb5b9f`, `mark_done_k2d.py`
`0a095552afc051b3ce3795cb471deb145da53db2`, `scripts/roache_triple.py`
`78e56a3bc2c2a07571db1cf3c91f4c2c31f246b8` — and the freeze commit is an
ancestor of `main`. **The stub IS the pinned comparator.** §9 fixes the grading
path at the freeze commit, so this is not a file that can be quietly completed.

**THE STANDING CORRECTION, recorded by the heat-transfer supervisor under their
own name.** This document was frozen on a comparator whose 31 selftest arms were
green, and the arms were read while the entry point was not. **A selftest count
is evidence about gate functions and evidence about nothing else. The check is
that the comparator can be pointed at a case directory and return a verdict.**

### 17.3 WHY NOT A §2d.1 REPAIR

The four-condition repair exception (`VERIFICATION_CHARTER.md:1914`–`:1945`) is
plausibly satisfiable here — condition (2) in its strongest form, since **no
graded value exists that a repair could have been selected to favour.** It is
declined anyway, and the ground is that **§2d.1 buys nothing**: a repaired
comparator would still have nothing to grade, because every level must rerun
regardless. An exception invoked where it preserves no evidence is an exception
invoked to keep a document alive. `VERIFICATION_CHARTER.md:2155`–`:2157` points
the same way — where a repair would make a graded refinement family
incommensurable, the whole ladder is re-registered rather than patched.

**The route out is a successor registration, `K2f`, drafted separately and
UNFROZEN.** Sanaa approved **K2a** — the rack-row module — in her own words on
2026-09-10. **That approval travels with the case, not with this document's
filename**, and K2f realises the same approved module unchanged. Nothing here
goes back to her desk and no agent's message is her consent.

### 17.4 `note=HANG_GUARD_TRIPPED` IS FACTUALLY WRONG

`STATUS.K2d_L3` carries `note=HANG_GUARD_TRIPPED`. That string is written
mechanically by `launch_k2d.sh:45` on any `rc=124` and carries **no diagnosis
whatever**. The solver had not hung.

**Measured from `log.solve`:** over its last 194 iterations L3 ran at **5.610
`ExecutionTime` s/iteration and 8.974 `ClockTime` s/iteration** — it was doing
work at the instant it died. Its final step block is **10 lines with no
`ExecutionTime` line**: the kill landed *inside* iteration 995, after that
step's two `p_rgh` solves and its continuity line and before its `k` and `omega`
solves. `rc=124` is GNU `timeout`'s kill code and `wall_s` **8034** equals
`timeout_s` **8034** exactly.

**This was a budget stop wearing a hang guard's name — the exact confusion §7.3
was written to prevent**, and §7.3 says so in terms: *"A timeout numerically
equal to a cap … makes a labelled hang guard function as a budget stop, and a
reader cannot tell which fired."*

**A second correction, against the convenient reading.** L3's residual
*magnitudes* at the kill were small, but its *trajectory* had already reversed.
L3 descended cleanly for three decades to a minimum at iteration ~945 (Ux
initial residual **1.1271e-04**, T **7.8362e-05**) and was **rising** when it
died: at 995, Ux **1.5725e-04** (**+39.5 %** off its own minimum) and T
**1.0293e-04** (**+31.3 %**). It was killed on the rising limb of an
oscillation, not on a converged step. **This is diagnostic evidence and is NOT
the registered gate** — `G-CYCLE` gates on `T_in,max` and `U_ha` normalised by
range-spanned, never on solver residuals. It is recorded because it is the only
convergence evidence this rung produced.

### 17.5 THE §7.3 DEPARTURE — and L1 shows the launcher had the registered value right one level earlier

§7.3's frozen table registers ranks and hang guard per level. What ran:

| level | §7.3 registered | as run (`STATUS.K2d_L*`) | departure |
|---|---|---|---|
| **L1** | 4 ranks, **1,485 s** | 4 ranks, **1,485 s** | **none — the registered value, used exactly** |
| **L2** | 8 ranks, **3,757 s** | 4 ranks, **2,381 s** | ranks halved; guard **1.58× tighter** |
| **L3** | 8 ranks, **20,250 s** (`:779`) | 4 ranks, **8,034 s** | ranks halved; guard **2.52× tighter** |

**L1 used the registered guard.** That makes L2 and L3 a departure from a value
the launcher had demonstrably been using correctly one level earlier — sharper
than "a different basis was used", because nothing changed but the caller.

**Provenance of 8,034 s: a hand-passed argument, not a registered cap and not a
computed one.** `launch_k2d.sh:7` reads `CASE="$1"; RANKS="$2"; GUARD_S="$3"` —
the launcher computes no guard and asserts nothing about the one it is handed.
The value came from the retired L3 watcher at
`K2d_runs/RETIRED_2026-09-11/watch_l3.sh:46`–`:47`:

> `# hang guard 3x the re-derived POINT (178.5 core-min on 4 ranks = 2678 s wall)`
> `./launch_k2d.sh K2d_L3 4 8034`

178.5 core-min ÷ 4 ranks = 2,677.5 s → 2,678 × 3 = **8,034**, exactly. The
178.5 is Addendum 3 §16.2's re-derivation, i.e. §7.3's *rule* ("≈3× POINT")
applied to a **re-derived** POINT rather than to the POINT in the frozen table.

**Whether §7.3's timeout column sits inside the freeze is left open and is
recorded as open.** §7.3 disclaims it as a cap in terms; standing rule 2 freezes
"gate, threshold, cap and label". It is nonetheless a numeric value in a frozen
document that was departed from downward without an addendum at the time. **No
verdict in this document turns on the answer** — every row is `NOT A RESULT` on
§17.2's grounds, which are independent of the guard.

**Why the re-derivation was wrong, measured.** §16.2 extrapolated L2 and L3 from
L1 at a **constant** cell-iter rate. The measured rate falls steeply with mesh
(`ExecutionTime` basis, contention removed):

| level | cells (built) | cell-iter/core-s | vs previous | contention (`ClockTime`/`ExecutionTime`) |
|---|---:|---:|---|---:|
| L1 | 58,368 | 187,700 | — | 1.003 |
| L2 | 196,992 | 93,986 | ÷1.997 | 1.320 |
| L3 | 664,848 | 37,051 | ÷2.537 | 1.775 |

Cost per iteration scales as roughly **N^1.6 – N^1.77**, not N^1.0.
**And the evidence was on disk before L3 launched and nobody read it:** §16.2
predicted **52.9** core-min for L2 and `STATUS.K2d_L2` records **138.400** — a
**2.617×** miss, written at 02:48:02Z. L3 had launched at 02:36:58Z.

### 17.6 `endTime 3000` WAS NOT ADEQUATE, AND L2 IS THE PROOF

**L2 completed all 3,000 iterations with `rc = 0` and an `End` line — and never
plateaued.** Its initial residuals bottomed at iteration ~800 (Ux
**1.7465e-04**) and then rose and oscillated for the remaining 2,200 iterations
with no further descent, peaking at ~1000 (5.28e-04), ~1800 (4.84e-04) and
~2800 (3.16e-04). Over its final 400 iterations:

| quantity | min | max | peak-to-peak / mean | sign changes in 1st difference |
|---|---|---|---:|---:|
| Ux initial residual | 1.6524e-04 | 5.0873e-04 | **109.1 %** | 6 |
| T | 1.5570e-04 | 4.6188e-04 | **104.5 %** | 16 |
| `p_rgh` | 1.5301e-03 | 4.3454e-03 | **100.6 %** | 16 |

That is the signature of a limit cycle, not a plateau, and L3 was arriving at
the same place by the same route (§17.4). It is what Wibron 2018 §3.4 reported
for this flow class and what K2b-U found in 2D in this geometry — both already
cited in §3.3 as the reason `G-CYCLE` exists.

**`P-K2d-2` and `P-K2d-3` ARE SCORED NEITHER HIT NOR LOSS.** Both are predictions
about a `G-CYCLE` reading, and `G-CYCLE` was never evaluable. Scoring them from
residuals would be scoring them on a quantity they were not written against.
**They are carried UNSCORED into K2f**, where the detector they need will exist.
`P-K2d-1` is likewise unscored: §4.4's report-only comparison never ran.

### 17.7 WHAT WAS SPENT, AND ALL OF IT IS WASTE

| stage | ranks | wall | core-min | outcome |
|---|---:|---:|---:|---|
| failed launch (Addendum 1) | 4 | 1 s | 0.067 | `rc=1`, dictionary fault |
| L1 | 4 | 235 s | 15.667 | rule-4 DONE — **ungradeable** |
| L2 | 4 | 2,076 s | 138.400 | 3,000 iters, `End` line — **ungradeable, not plateaued** |
| L3 | 4 | 8,034 s | 535.600 | **0 fields, 0 time dirs, no restart point** |
| **total, gross** | | | **689.734** | |

**All 689.734 core-min is WASTE** under `COMPUTE_BUDGET_CHARTER.md` §6 — not
merely L3's 535.600. L1 and L2 bought completed solves that no instrument on the
frozen path can grade. **$0.590 derived** at $0.0513/core-h — **derived, never
measured**; the box cannot read its own billing. The row lands in
`docs/COST_CALIBRATION.md` under that file's append rules, waste separately
named and never absorbed into a ratio.

### 17.8 THE EVIDENCE, AND WHERE IT NOW LIVES

`K2d_L3` and `STATUS.K2d_L3` were **MOVED, never deleted**, to
`verification/runs/F14-cooling-ladder/K2d_runs/RETIRED_2026-09-11/`, so that no
future reader takes the old `rc=124` for a new run's. `log.solve` is
byte-identical across the move (sha256
`2731e614ab63019fcae12ef5085213e2501991aa5a7ca8515c8e686075eb55b0`, 1,098,002
bytes) and mtimes are preserved. `K2d_L1` and `K2d_L2` remain in place.

**Both frozen instruments refuse the case in place, verified by execution:**
`mark_done_k2d.py --guard K2d_L3` returned **rc=1** on the pre-existing `0/`
limb, and `build_k2d.py:433` refuses the same condition independently. A restart
would in any case have bought nothing — `startFrom latestTime` with
`processor*/` holding only `0` means latestTime **is** 0.

---

*Nothing was sent, filed, uploaded, registered, posted or commented outside this
box (rule 7). K2d is retired. Total solver compute against this document:
**689.734 core-min, measured, all of it waste.***
