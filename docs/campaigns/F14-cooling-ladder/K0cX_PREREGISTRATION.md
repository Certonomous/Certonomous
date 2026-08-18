# K0cX. Cross-geometry rung: pre-registration

Campaign F14, gate K0c. Written 2026-08-18, **before any graded case was
solved**. Two pilot solves preceded it and are charged in Section 7; they
produced a *rate*, not a result, and no case value in this document came from
them.

**The question.** The square-cavity rung K0cS graded three turbulence models
against Ampofo and Karayiannis (2003) and returned GATE FAIL on two and REFUSED
on the third. This rung takes the same three models, plus a laminar control, to
**Betts and Bokhari's 28.7 aspect-ratio tall cavity** — the same models, a
different geometry, three Rayleigh decades lower — and asks of each K0cS
failure: **does it travel?**

A model-form failure that appears in one geometry and not another is worth more
than either result alone. **A failure that does not travel is equally
informative**, and this document registers predictions in both directions so
that neither outcome can be read as the one that was hoped for.

Specification: `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` Section 2 and addendum
A1, written 2026-08-17 and 2026-08-18 by other agents. **Nothing here edits that
specification.** Every reference value and every band below is quoted from it and
is re-parsed out of it at analysis time by a comparator that holds no copy of its
own.

Run tree: `verification/runs/F14-cooling-ladder/K0cX_runs/`.

---

## 1. The four K0cS results this rung tests for transfer

| # | K0cS result | Record | What "travels" would mean here |
| --- | --- | --- | --- |
| **F1** | **kOmegaSST GATE FAIL**, 8 of 10 rows | `K0cS_RESULTS.md` §5.1 | kOmegaSST fails this geometry's gate too |
| **F2** | **Grid refinement moved the stratification parameter AWAY from the experiment** for kOmegaSST (+0.080) and LaunderSharmaKE (+0.158); the coarse agreement was cancellation | `K0cS_RESULTS.md` §3 | refining the tall-cavity mesh moves core stratification S further from 0.095 |
| **F3** | **LaunderSharmaKE relaminarised on refinement**: fmu 0.887 -> 0.034, 25 996 bounding-k events of 40 000 iterations, Reynolds stress four orders below molecular. **REFUSED**, not failed | `K0cS_RESULTS.md` §4 | LaunderSharmaKE's eddy viscosity collapses on a refined tall-cavity mesh |
| **F4** | **Constant turbulent Prandtl number closed NEGATIVE**: Prt 0.85 -> 1.28 moved hot-wall Nusselt by **1.75 %** against a registered 5-20 % | `K0cS_RESULTS.md` §7.1 | Prt is equally inconsequential here |

**F4 is why this rung exists in this geometry.** Addendum A1.6b DERIVED from
Betts Table 1 a *measured* centre-line turbulent Prandtl number of **1.071** (lo
Ra) and **1.283** (hi Ra), against the **0.85** the K0cT rung imposed — 21 and
34 percent low. The square cavity has no measured Prt at all. So the tall cavity
is the geometry where the constant-Prt assumption most demonstrably departs from
measurement, and it is the only place the question can be asked with a number on
both sides.

---

## 2. Reference values and bands, quoted from the specification

**Not retyped into the comparator.** `analyse_k0cx.py` parses each of these from
the specification at run time and exits 2 if any will not parse.

### 2.1 Section 2.3 (DERIVED from the ERCOFTAC Case 079 primary files) and A1.2

| Quantity | Ra 0.86e6 | Ra 1.43e6 | Band (spec §2.4 / A1.5) |
| --- | ---: | ---: | --- |
| Core stratification S | 0.016 (below its own 0.02 resolvable increment) | 0.095 | \|S\| <= **0.07** (lo, a BOUND); \|S - 0.095\| <= **0.05** (hi) |
| Mid-height peak upward velocity | +0.140 m/s at x = 71.2 mm | +0.190 m/s at x = 70.2 mm | REL <= **15 %**; location within **5 mm** |
| Mid-height peak downward velocity | -0.135 m/s at x = 6.2 mm | -0.189 m/s at x = 5.0 mm | REL <= **15 %**; location within **5 mm** |
| Mid-width mean T at y/H = 0.30 / 0.50 / 0.70 | 25.07 / 25.26 / 25.39 C | 34.58 / 34.74 / 36.02 C | within **1.0 K** (lo), **2.0 K** (hi) |
| Antisymmetry defect of the two peaks | 3.6 % | 0.5 % | defect <= **10 %** |
| **Average Nusselt number** (A1.2, Betts Table 1 p. 682) | **5.85** | **7.57** | \|E\| <= **u_val** = 5.43 % (lo), 5.41 % (hi) |

**10 rows per Rayleigh number, 20 graded rows per model.** Four models are run;
the laminar control's 20 rows are reported on the same footing (Section 4) and
are not counted toward any model's verdict.

### 2.2 The two cautions carried from the lane that extracted the Nusselt reference

Neither is resolved here, and neither is quietly dropped.

**(a) The paper disagrees with itself.** The Nusselt definition `Nu = g W / dT`
was recovered from a parenthetical on p. 677 (A1.4) and tested against Betts
Table 1's own numbers: it reproduces the **hi-Ra row to 0.14 %** and the **lo-Ra
row to 2.08 %**. Table 1's tabulated Nu cannot be recovered from Table 1's own
tabulated gradient and wall temperatures at the lower Rayleigh number. That
inconsistency is **carried into u_val as a component** (2.09 % lo, 2.00 % hi in
A1.5) rather than resolved in either direction, because nothing in the paper says
which entry is the rounded one. **This rung carries it the same way.**

**(b) The honest uncertainty is the reproducibility spread, not the authors' error
bars.** The authors state ±5 % on the wall gradient (p. 681) and under 1.2 % on
several other quantities. Two experiments in the same rig disagree by **up to
8.8 %**. Every deviation in the results record will therefore be reported
**against u_val AND against the 8.8 % reproducibility spread**, and no model will
be called validated on an agreement inside 8.8 %. A reference with a ±5 % stated
uncertainty and an 8.8 % rig-to-rig spread is not an instrument that can certify
a 5 % agreement.

---

## 3. Models, meshes, and the case set

### 3.1 Models

| Tag | Model | Wall treatment | Why it is here |
| --- | --- | --- | --- |
| SST | `kOmegaSST` | low-Re, integrate to wall (`nutLowReWallFunction`) | GATE FAIL at K0cS **and** at K0cT; the reference leg |
| KE | `kEpsilon` | **high-Re wall functions** (`nutkWallFunction`, `kqRWallFunction`) | GATE FAIL at K0cS, but **the only model there whose passes discriminated**. Never run on this geometry |
| LS | `LaunderSharmaKE` | low-Re, integrate to wall | REFUSED at K0cS for relaminarising; **NOT GRADED at K0cT for lacking a mesh pair**. It gets one here |
| LAM | `laminar` | none | the control, and a **first-class row** (Section 4) |

kEpsilon is given the high-Re treatment it was built for. Giving it a low-Re
treatment it has no damping functions for would be building a straw man. The
gate's own argument (`K0cT_RESULTS.md` §1.2a) is that wall functions are
inadmissible at this cavity's y+ of about 0.19; **that argument is tested here
rather than used to exclude the model without evidence.** y+ is measured on every
case from the solve's own near-wall velocity gradient, not read from the `yPlus`
function object, which reports the wall function's own y+ and prints zero where
there is none.

### 3.2 Meshes — three levels, and why a pair is not enough

| Level | nx x ny | cells | first cell at each plate | endTime |
| --- | --- | ---: | ---: | ---: |
| coarse `c` | 40 x 120 | 4 800 | 0.2000 mm | 60 000 |
| fine `f` | 64 x 192 | 12 288 | 0.1250 mm | 50 000 |
| extra-fine `x` (hi Ra only) | 102 x 307 | 31 314 | 0.0784 mm | 30 000 |

Refinement 1.6 in each direction at each step, with the near-wall cell refined in
the same ratio as the cell count, so each step is a **uniform** refinement and
not a core-only one. The coarse/fine pair is **identical to K0cT's**, which makes
the kOmegaSST leg a reproduction check on an independently written build script
(control C-REPRO).

The third level exists because **F2 and F3 are both grid-refinement failures**,
and a two-point difference cannot show a trend. It is registered at the higher
Rayleigh number only, where the reference stratification is resolvable.

**The near-wall geometry that makes F3 predictable is worth stating now, before
the answer exists.** LaunderSharmaKE relaminarised at K0cS between a first cell of
**0.250 mm** and one of **0.156 mm**. The tall cavity's *fine* mesh here has a
first cell of **0.125 mm** — already 20 percent finer than the mesh on which the
model collapsed — and K0cT's `M_hi_f_LS` ran on exactly that mesh and returned an
eddy viscosity ratio of about 40. So the relaminarisation, if it travels at all,
has already had its chance on the fine mesh and did not take it. The extra-fine
level is the honest extension of the axis, not a fishing expedition.

### 3.3 The 22 cases

| Group | Cases | Count |
| --- | --- | ---: |
| Graded mesh pairs | `X_{lo,hi}_{c,f}_{SST,KE,LS,LAM}` | 16 |
| Mesh-trend leg, hi Ra | `X_hi_x_{SST,KE,LS}` | 3 |
| Prt SENSITIVITY | `P_lo_f_SST` (Prt 1.071), `P_hi_f_SST` (1.283), `P_hi_f_KE` (1.283) | 3 |

Every case differs from every other in the dictionary entries named and in no
other. Plate temperatures, the Ra-matching viscosity, the measured rubber-wall
boundary profiles and the convection schemes are held at exactly the values
`K0cT_runs/build_cases.py` derived, so this rung is a model comparison and not a
re-specification of the case.

---

## 4. The laminar control is a first-class row, and the discrimination baseline is registered here

Docket **D411** records that on the square cavity **the set of rows kOmegaSST
passed that the laminar control did not was EMPTY** — two gate rows could not
distinguish a turbulence model from no model at all. That is a defect in the
*gate*, not only in the model, and it is invisible unless the control is run on
every row.

So the laminar control runs on the **full mesh pair at both Rayleigh numbers** —
four cases, not one — and its 20 rows per Ra are reported beside every model's,
**whether or not the comparison flatters this rung**.

### 4.1 Two discrimination measures, both registered before compute

Verdict-level discrimination alone is a weak instrument when the model and the
control both fail a row, which is the common case here. Both are therefore
registered:

- **D-a (verdict discrimination, the D411 measure).** A row discriminates for
  model M iff **M PASSES it and the laminar control FAILS it**, same mesh, same
  Ra. The reported quantity is the *set* of such rows, and an empty set is the
  D411 finding repeated.
- **D-b (separation).** A row discriminates iff
  **\|q_M - q_laminar\| > the row's own band**. This detects rows where both fail
  but the closure is nonetheless doing something the gate can see.

### 4.2 Which rows are predicted to discriminate — registered in advance

| Row | D-a predicted | D-b predicted | Reasoning |
| --- | --- | --- | --- |
| Core stratification S, both Ra | **NO** (both fail) | **YES** | K0cT C1 measured laminar S in 0.415-0.600 against kOmegaSST's 0.243 on the same mesh, a separation of 0.17 against a 0.05 band |
| Average Nusselt, both Ra | **NO** for SST (both fail); **YES for KE and LS** if either lands inside u_val | **YES** for all three | K0cT: laminar Nu 4.72 vs SST 5.70, separation 21 % against a 5.4 % band |
| Mid-width T at y/H = 0.50 and 0.70, both Ra | **YES** — 4 rows | **YES** | the models pass these; a strongly stratified laminar core cannot |
| Mid-height peak velocity magnitude, both signs, both Ra | **NO** (all fail) | **YES** | the laminar cavity is unsteady with much larger excursions |
| Peak **locations**, 4 rows | **NO** | **NO** | these measure the geometry and the near-wall mesh, not the closure — the tall-cavity analogue of K0cS's G9 |
| **Antisymmetry defect**, 2 rows | **NO** | **NO** | a 2-D Boussinesq cavity is very nearly centro-symmetric by construction. `K0cT_RESULTS.md` §2.1 already says this row is not evidence for anything |
| Mid-width T at y/H = 0.30, both Ra | **NO** (both fail) | **YES** | |

**Registered headline: D-a is predicted to be NON-EMPTY for kOmegaSST here (at
least 4 rows), so the square cavity's empty-discrimination failure is predicted
NOT to travel.** Six rows — the four locations and the two antisymmetry defects —
are predicted to discriminate on **neither** measure, and are named now so that
their passing cannot later be read as evidence about turbulence modelling.

---

## 5. Registered predictions, per model, per row

Point predictions with ranges. Where a K0cT or K0cS number grounds a prediction
it is named; where nothing grounds it, that is said.

### 5.1 kOmegaSST — predicted **GATE FAIL, 10 of 20 rows**

kOmegaSST has already been run on this geometry (`K0cT_RESULTS.md`,
`K0cT_NUSSELT_REGRADE.md`). This leg is therefore predicted to **reproduce**
those numbers, and that is control C-REPRO rather than a discovery.

| Row | Ra | K0cT published (fine) | **predicted here** | predicted verdict |
| --- | --- | ---: | ---: | --- |
| S | lo | 0.2209 | 0.221 +/- 0.010 | **FAIL** |
| S | hi | 0.2353 | 0.235 +/- 0.010 | **FAIL** |
| V up magnitude | lo | +15.94 % | +16 % +/- 2 | **FAIL** |
| V up magnitude | hi | +16.38 % | +16 % +/- 2 | **FAIL** |
| V down magnitude | lo | +20.23 % | +20 % +/- 2 | **FAIL** |
| V down magnitude | hi | +17.00 % | +17 % +/- 2 | **FAIL** |
| peak locations (4 rows) | both | 0.20-1.45 mm | < 3 mm | **PASS** x4 |
| T at y/H = 0.30 | lo | 1.208 K | 1.21 +/- 0.15 K | **FAIL** |
| T at y/H = 0.30 | hi | 2.029 K | 2.03 +/- 0.20 K | **FAIL — and flagged MARGINAL**, a fail by 1.5 % of its band |
| T at y/H = 0.50, 0.70 (4 rows) | both | 0.23-0.49 K | < 0.8 K | **PASS** x4 |
| antisymmetry (2 rows) | both | 0.003-0.006 % | < 0.1 % | **PASS** x2 |
| **Average Nu** | lo | 4.8680 (-16.79 %) | 4.87 +/- 0.05 | **FAIL** |
| **Average Nu** | hi | 5.6965 (-24.75 %) | 5.70 +/- 0.06 | **FAIL** |

**F1 is predicted to TRAVEL.** kOmegaSST is predicted to fail both geometries'
gates, and to fail this one in a specific direction: **under-predicting the wall
heat transfer while over-predicting the core stratification and the peak
velocity** — a model producing too little turbulent mixing at every scale the
gate can see.

**C-REPRO threshold, registered:** every row above must land within its stated
range. A deviation larger than **1 %** on S or Nu between this build and K0cT's
published fine-mesh value is a **build defect**, not a finding, and the rung is
BLOCKED until it is explained.

### 5.2 kEpsilon — predicted **GATE FAIL, 4 to 8 of 20 rows**, and the widest error bars on this page

kEpsilon has **never been run on this geometry**. Nothing anchors these numbers
to a prior tall-cavity solve, and the ranges are correspondingly wide. The
reasoning is transferred from K0cS §5.2, where kEpsilon "moved the right amount
of fluid and the wrong amount of heat".

| Row | Ra | **predicted** | predicted verdict |
| --- | --- | ---: | --- |
| S | lo | 0.05 - 0.16 | **PASS** (bound 0.07) — *low confidence, this straddles the band* |
| S | hi | 0.08 - 0.18 | **PASS** |
| V up / down magnitude (4 rows) | both | 0 % to +16 % | **PASS** x4 |
| peak locations (4 rows) | both | < 4 mm | **PASS** x4 |
| T at y/H = 0.30 | both | 0.9 - 1.8 K (lo), 1.6 - 3.0 K (hi) | **FAIL** x2 |
| T at y/H = 0.50, 0.70 (4 rows) | both | < 1.0 K | **PASS** x4 |
| antisymmetry (2 rows) | both | < 0.5 % | **PASS** x2 |
| **Average Nu** | lo | 5.2 - 6.6 (-11 % to +13 %) | **FAIL**, marginal |
| **Average Nu** | hi | 6.8 - 8.6 (-10 % to +14 %) | **FAIL**, marginal |

**The mechanism predicted:** kEpsilon carries no low-Reynolds-number damping, so
its eddy viscosity in the near-wall cells stays far larger than kOmegaSST's;
that mixes the core harder, lowers the stratification toward the measured 0.095,
and raises the wall heat flux toward the measured value. Its wall functions
cannot fire at y+ 0.19 — below `yPlusLam` the high-Re treatment returns the
molecular branch — so the **wall flux is predicted to be essentially molecular
while the interior is over-mixed**. Registered consequence: kEpsilon's
alphat at the wall is predicted **below 1 % of alpha** on every case, and if it
is not, the wall function is firing outside its design range and the Nusselt row
must be read with that stated.

**Registered directional prediction: kEpsilon lands CLOSER to the experiment
than kOmegaSST on S and on Nu at both Rayleigh numbers.** If it does, the K0cS
finding that "kEpsilon is the only model whose passes discriminate" has
travelled. If it does not, that finding is square-cavity-specific.

### 5.3 LaunderSharmaKE — predicted **GATE FAIL, 8 to 12 of 20 rows**, and predicted **NOT to relaminarise**

Anchored on K0cT's single fine-mesh case `M_hi_f_LS`, which was reported and
never graded.

| Row | Ra | K0cT `M_hi_f_LS` | **predicted here** | predicted verdict |
| --- | --- | ---: | ---: | --- |
| S | hi | 0.0186 (-80.4 %) | 0.015 - 0.045 | **FAIL** (deviation ~0.06-0.08 on a 0.05 band) |
| S | lo | — | 0.00 - 0.05 | **PASS** (bound 0.07) |
| V up / down magnitude | hi | -33.3 % | -25 % to -40 % | **FAIL** x2 |
| V up / down magnitude | lo | — | -25 % to -40 % | **FAIL** x2 |
| peak locations (4 rows) | both | — | < 5 mm | **PASS** x4, low confidence |
| T at y/H = 0.30 (2 rows) | both | — | 1.0 - 2.5 K | **FAIL** x2 |
| T at 0.50, 0.70 (4 rows) | both | — | < 1.5 K | **PASS** x2 (lo), **PASS** x2 (hi), low confidence |
| antisymmetry (2 rows) | both | — | < 1 % | **PASS** x2 |
| **Average Nu** | hi | 7.9866 (+5.50 %) | 7.6 - 8.4 | **FAIL, marginal** (\|E\|/u_val ~1.0) |
| **Average Nu** | lo | — | 5.6 - 6.4 | **FAIL, marginal** |

**F3 is predicted NOT to travel. This is the sharpest prediction on the page and
it is registered with its consequences in both directions.**

Registered relaminarisation thresholds, per case, all three meshes, both Ra:

| Diagnostic | K0cS fine mesh (relaminarised) | **predicted here** |
| --- | ---: | ---: |
| `nu_t/nu`, domain maximum | **6.1e-4** | **> 10** |
| solver `bounding k` events | **25 996** of 40 000 iterations | **< 1 000** |
| implied damping function `fmu` maximum | **0.034** | **> 0.5** |
| peak Reynolds shear stress at mid-height | 3.89e-17 | > 1e-5 |

**If the prediction holds:** the K0cS relaminarisation is a property of the
square cavity at Ra 1.58e9 and not of the model, and F3 does not travel.

**If the prediction fails:** LaunderSharmaKE's +5.50 % Nusselt at K0cT — the only
number produced on this case class that sits inside the experiment's own stated
uncertainty — is an artefact of one mesh, and the regrade's "refuted / merely
not refuted" asymmetry between the two models collapses. **That would be the more
important outcome, and it is registered as such so that it cannot later be
presented as a disappointment.**

### 5.4 The laminar control — predicted **17 to 20 of 20 rows FAIL**

| Row | Ra | K0cT `C1_hi_c_laminar` | **predicted here** | predicted verdict |
| --- | --- | ---: | ---: | --- |
| S | hi | 0.4157 (window 0.415-0.600) | 0.30 - 0.65 | **FAIL** |
| S | lo | — | 0.25 - 0.65 | **FAIL** |
| V magnitude (4 rows) | both | — | > +30 % or < -30 % | **FAIL** x4 |
| peak locations (4 rows) | both | — | < 5 mm | **PASS** x4 |
| T rows (6 rows) | both | — | > 2 K (lo), > 4 K (hi) | **FAIL** x6 |
| antisymmetry (2 rows) | both | — | < 10 % | **PASS** x2 |
| **Average Nu** | hi | 4.7197 (-37.65 %) | 4.3 - 5.3 | **FAIL** |
| **Average Nu** | lo | — | 3.6 - 4.5 | **FAIL** |

**Registered in advance: the laminar control is expected to converge on none or
almost none of these cases.** A laminar tall cavity at Ra 1.4e6 in a 28.7
aspect-ratio enclosure is genuinely unsteady; K0cT's C1 failed all three
convergence criteria by wide margins. Its numbers are therefore a time-varying
quantity sampled at endTime, its error bars are its own peak-to-peak window, and
**the S prediction above is registered as a regime bound tested across the whole
window rather than at one snapshot** — the same form K0cT used, and for the same
reason.

### 5.5 F2 — grid refinement — predicted **NOT to travel**

| Model | K0cS: Sp coarse -> fine | K0cT tall (fine - coarse) | **predicted here, S over three meshes** |
| --- | --- | ---: | --- |
| kOmegaSST | 0.674 -> 0.754, **AWAY by 0.080** | 0.2428 -> 0.2353, toward by 0.0075 | **monotone TOWARD**, total movement over both refinement steps < 0.02, ending 0.225 - 0.240 |
| LaunderSharmaKE | 0.620 -> 0.778, **AWAY by 0.158** | no coarse twin existed | **TOWARD**, S rising from below toward 0.095, total movement < 0.03 |
| kEpsilon | 0.4925 -> 0.4888, grid-converged | never run here | **grid-converged**, \|dS\| < 0.02 per step |

**Registered: F2 does not travel.** The prediction is that no model's core
stratification moves away from the experiment by more than 0.01 under refinement
on this geometry, against 0.080 and 0.158 at the square cavity.

If any model *does* move away by more than 0.02, F2 has travelled, and the
consequence registered now is that **no single-mesh tall-cavity result on this
case class may be quoted again**, including the ones already published.

### 5.6 F4 — the Prt sensitivity — predicted **to travel, i.e. NOT to close negative here**

`P_*` cases move Prt from 0.85 to the value **measured in this very cavity**
(A1.6b, DERIVED from Betts Table 1): 1.071 at lo Ra, 1.283 at hi Ra. This is not
an arbitrary perturbation and it is not a tuning: the target is a measurement.

| Registered prediction | Value |
| --- | --- |
| kOmegaSST, hi Ra: change in average Nu | **-3 % to -12 %** |
| kOmegaSST, lo Ra: change in average Nu | **-2 % to -8 %** |
| kEpsilon, hi Ra: change in average Nu | **-5 % to -20 %** |
| change in core stratification S, all three | **+0.01 to +0.06** |
| **cross-geometry statement** | **the tall cavity's Nusselt sensitivity to Prt EXCEEDS the square cavity's 1.75 %** |

**And the direction is the part that matters.** kOmegaSST already under-predicts
this cavity's Nusselt number by 17 to 25 percent. Raising Prt to the measured
value **reduces** the turbulent heat transport and is predicted to make the
Nusselt number **worse, not better**. So the registered prediction is that using
the correct, measured turbulent Prandtl number **does not repair the model** —
which, if it holds, is a finding about where the model's error is *not*.

**If instead the sensitivity comes out under 1.75 %,** F4 closes negative on both
geometries: the constant-Prt assumption is measurably wrong at the tall cavity
and *consequentially* irrelevant on both, and effort spent on it anywhere in this
case class would be wasted. That outcome is registered as fully acceptable.

### 5.7 Rung-level prediction

**GATE FAIL. No model passes. 30 to 38 of the 60 graded rows fail.** The three
models are predicted to **bracket** the experiment on average Nusselt at the
higher Rayleigh number — kOmegaSST low near 5.7, kEpsilon near 7.6, LaunderSharma
near 8.0 against a reference of 7.57 — and, exactly as at K0cS, **bracketing is
not reproducing**.

---

## 6. Convergence, refusal, and the controls

### 6.1 Convergence criterion — registered, and identical to K0cT's

**Peak-to-peak spread over a fixed window of the last 400 outer iterations,
sampled every 50 (9 samples).** Not residuals. Not an endpoint difference. Three
quantities, **all** of which must pass:

| | threshold |
| --- | --- |
| (a) average Nu on the hot wall | spread < **0.02 %** |
| (b) core stratification S | spread < **0.001** absolute |
| (c) peak \|Uy\| in the domain | spread < **0.02 %** |

A case failing any of the three is **REFUSED** — reported with its measured
spreads and **not graded**. The criterion is not loosened for any case and no
averaging scheme will be invented after the fact. `residualControl` is removed
from every case so that no solve stops before its endTime; K0cT §4 measured that
residual stops fired at 6-10 k iterations, two orders of magnitude before the
graded quantities were steady.

**Registered expectation: the laminar cases and the coarse hi-Ra cases are the
likely refusals**, on the K0cT precedent.

### 6.2 Controls

| Tag | KIND | Registered criterion |
| --- | --- | --- |
| **C-LAM** | RECOGNITION | the laminar control separates from kOmegaSST on S by more than the row band (0.05) on the same mesh at hi Ra. If it does not, this gate cannot tell a turbulence model from none and every verdict on it is void |
| **C-REPRO** | RECOGNITION of a build defect | this build's `X_hi_f_SST` and `X_lo_f_SST` reproduce K0cT's published fine-mesh S and Nu within **1 %**. Larger, and the rung is BLOCKED |
| **C-MUT** | CONTROL, zero compute | every graded row is flippable in **both** directions by perturbing the reference. A row that cannot fail is decorative |
| **S-PRT** | SENSITIVITY — grades nothing | Section 5.6 |
| **S-MESH** | SENSITIVITY — grades nothing | the third mesh level, Section 5.5 |

**A sensitivity is not a control.** It cannot pass or fail; it is a measured
difference used to attribute a deviation.

### 6.3 Reported, and never graded

Heat balance on this sealed cavity is a **near-identity**
(`VERIFICATION_CHARTER.md:106-111`) and is reported, never gated on. So are: y+
at the first cell off each plate; wall alphat as a fraction of alpha; the eddy
viscosity ratio against Betts Table 1's measured centre-line 35 and 55; the
implied `fmu`; bounding-k, bounding-epsilon and bounding-omega event counts; and
the wall-gradient method sensitivity.

---

## 7. Cost — the estimate is an instrument, and it is written before the spend

**Basis: two pilot solves, measured, not recalled.** Both ran 1000 iterations of
the actual built cases in a scratch directory outside the run tree:

| pilot | cells | iterations | solver `ExecutionTime` | s / cell / iteration |
| --- | ---: | ---: | ---: | ---: |
| `X_hi_c_SST` | 4 800 | 1 000 | 9.42 s | **1.963e-06** |
| `X_hi_x_SST` | 31 314 | 1 000 | 65.86 s | **2.103e-06** |

The two agree to **7 %**, which is the check that the number is a *rate* and not
an artefact of one mesh. The higher of the two is used.

| group | cases | cells x iterations | core-minutes |
| --- | ---: | ---: | ---: |
| coarse, 60 000 iterations | 8 | 4 800 x 60 000 | 80.6 |
| fine, 50 000 iterations | 8 | 12 288 x 50 000 | 172.0 |
| extra-fine, 30 000 iterations | 3 | 31 314 x 30 000 | 98.6 |
| Prt sensitivity (fine) | 3 | 12 288 x 50 000 | 64.5 |
| **subtotal** | **22** | | **415.7** |
| **contingency x1.20** | | | **498.8** |
| pilots, charged | 2 | | 1.8 |
| **TOTAL ESTIMATE** | | | **500.6 core-minutes** |

**500.6 core-minutes = 8.34 core-hours = $0.428** at the measured $0.0513 per
core-hour.

**The contingency is 1.20x and not the 2.3x the K0cS rung overshot by.** That
lane's own recommendation was "nearer 1.2x on the next rung on this case class",
and an estimate that overshoots is not free — it reserves capacity other lanes
could use. The estimate is deliberately tight enough to be falsifiable.

| | |
| --- | --- |
| Standing authorisation | **$25** per run by own estimate |
| This estimate | **$0.428**, 1.7 % of it |
| **Hard stop, declared in advance** | **700 core-minutes / $0.60.** Reaching it stops the rung and the shortfall is reported as PENDING rather than absorbed |

Wall clock is not the charged quantity but it is the binding constraint on a
shared box. The 22 cases run in two waves of 14 and 8 on a 16-core machine, so at
most 14 solvers are resident at once and no case is charged for contention it did
not cause. Both `ExecutionTime` (solver CPU) and wall clock are recorded per
case.

---

## 8. What this rung cannot establish, said before it runs

- **It cannot validate any model.** Specification §2.5 makes VALIDATED
  conditional on passing every row, and the rung-level prediction is that none
  will.
- **It cannot resolve Betts Table 1's 2.08 % internal inconsistency** at the
  lower Rayleigh number. That is carried in u_val and stays carried.
- **It cannot distinguish a 5 % agreement from the experiment.** The stated
  uncertainty is ±5 % on the wall gradient and the rig-to-rig reproducibility
  spread is 8.8 %; nothing inside that is a result.
- **It cannot transfer back to the square cavity.** A failure that does not
  travel from K0cS to K0cX says nothing about a third geometry.
- **Nothing here will be submitted, sent, filed, uploaded or registered.**
  Submissions are PARKED.
