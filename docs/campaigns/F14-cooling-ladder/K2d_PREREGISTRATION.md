# K2d — the three-level realisation of the owner-approved K2a rack-row module: PRE-REGISTRATION

**Campaign F14, DC-cooling spine. Rung `K2d`. Team: heat-transfer.**
**Written 2026-09-10 by a heat-transfer `lab-lane` at ZERO solver core-minutes.**

> # DRAFT — NOT FROZEN. NO COMPUTE UNDER THIS DOCUMENT.
>
> **No gate, band, threshold, floor, cap or label in this file is frozen.**
> `GRADING_PATH_FREEZE_COMMIT` reads **`PIN-AT-FREEZE`** throughout. Until the
> heat-transfer supervisor freezes this document by sha, it is amendable, and
> **every amendment must state its condition and how it was checked** (standing
> rule 2).
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
> **Threshold: peak-to-peak spread of `U_ha` ≤ 0.5 % of its sample mean** over
> the same 400-iteration window, **≥ 9 samples, REFUSED below that**. The
> `CYCLING` and `DRIFTING` discriminators are **identical** to §3.3's — ≥ 3 sign
> changes in the first difference, and linear trend explaining < 25 % of sample
> variance.
>
> **Any level `CYCLING` or `DRIFTING` on EITHER `T_in,max` OR `U_ha` → every
> graded row `NOT A RESULT`.** Both states are printed for every level whichever
> fires.

**Why 0.5 % and not S13's 0.02 %, stated because a threshold chosen to be
passable is worthless.** S13's 0.02 % governs a *mass-flow-weighted inlet
temperature* — an intrinsically smooth, strongly constrained quantity. `U_ha` is
a volume-averaged velocity in a buoyancy-dominant recirculating region and is
intrinsically more variable; 0.02 % there would fire on every run and produce a
gate that cannot be passed, which is not a gate. **0.5 % is 25× looser and is
chosen so the SPREAD limb only decides whether to look**, while the sign-change
and trend criteria do the actual discrimination between an oscillation and a
descent. **The risk of this choice runs one way and is named:** too tight gives
`NOT A RESULT`, the conservative direction; too loose could miss a
small-amplitude cycle — **which is exactly what §3.3b exists to bound, and why
it reports a measured detection floor rather than asserting one.**

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

**The measurement that motivates it, and it is live in this family tonight.**
The T26 lane measured its mesh-defect population growing **faster than its cell
count** — small-determinant cells ×3.37 and concave cells ×5.06 against a 2.66×
cell increase. **A defect fraction that RISES under refinement drives `p`
down**, so a low `p` is the signature of exactly that failure. `G-CHECKMESH` at
zero tolerance (§5.1) should prevent it here — K2d's rack row is axis-aligned
rectilinear `blockMesh` with no refinement transitions — **but the annotation
costs nothing and is the diagnostic that catches it if that expectation is
wrong.**

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
| `GRADING_PATH_FREEZE_COMMIT` | `PIN-AT-FREEZE` |
| `build_k2d.py` | `PIN-AT-FREEZE` |
| `analyse_k2d.py` | `PIN-AT-FREEZE` |
| `mark_done_k2d.py` | `PIN-AT-FREEZE` |
| `scripts/roache_triple.py` | `PIN-AT-FREEZE` |
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

*Nothing was sent, filed, uploaded, registered, posted or commented outside this
box (rule 7). Zero solver core-minutes spent in writing this document.*
