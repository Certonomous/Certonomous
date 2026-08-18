# K0cS. Pre-registration: square-cavity turbulent re-gate

Campaign F14, gate K0c, square-cavity turbulent rung (K0cS). Registered
**2026-08-18, before any graded case was launched.** The two pilots charged in
Section 2 were run outside the case tree before this document was written and
are the only compute that preceded it.

Reference values and pass bands are **not** in this document. They are in
`K0cS_SQUARE_CAVITY_GATE.md`, written first, and the analyser parses them from
there. This document holds only what must be fixed before the answer is known:
the cost, the predictions, and the stop rules.

---

## 1. What this rung was for

`K0cT_RESULTS.md` recorded a **GATE FAIL** for kOmegaSST against the Betts and
Bokhari *tall* cavity, and its Section 5 model twin showed kOmegaSST and
LaunderSharmaKE **bracketing** the experiment on both graded quantities with
neither inside the band. The open question that left was whether that bracketing
was a property of the tall cavity's geometry or of the models.

This rung answered it on a **different geometry at a Rayleigh number three
decades higher** (square, Ra 1.58e9, against tall, Ra 0.86-1.43e6), against two
independent experiments in the same rig. Per the day order, a model that passes
one geometry and fails the other is the interesting result, and the failure modes
are the deliverable.

---

## 2. Compute cost, estimated BEFORE the run

**The clause is "less than $25 in your estimated computations", which makes the
estimate an instrument.** This campaign has form here: `K2b`'s 374-697
core-minute estimate went **VOID** mid-rung because it priced steady runs for an
unsteady question. The basis below is therefore measured on this case, on this
machine, today, and not recalled.

### 2.1 The measured basis

Two pilots were run in the session scratchpad, **outside** the case tree, at 300
iterations each, on the same dictionaries the graded cases use. Both are charged
below.

| pilot | cells | iterations | solver ExecutionTime | s/iteration | s/(cell.iteration) |
| --- | ---: | ---: | ---: | ---: | ---: |
| coarse, 120 x 120 | 14400 | 300 | 6.72 s | 2.240e-02 | 1.556e-06 |
| fine, 192 x 192 | 36864 | 300 | 17.62 s | 5.873e-02 | 1.593e-06 |

The two rates agree to **2.4 percent per cell**, which is the check that the
number is a rate and not an artefact of one mesh.

**CONTINGENCY ON THE RATE: 1.6x**, stated rather than hidden. The pilots are 300
iterations into a developing flow where `p_rgh` converged in few PCG sweeps; a
developed buoyant field at Ra 1.58e9 takes more, so the pilot rate underestimates
the steady-state rate. 1.6x is the same multiplier the K0cT rung registered, and
that rung came in at 95.0 core-minutes against a 119.6 estimate, so the
multiplier has been calibrated once on this case class and was not generous.

### 2.2 The estimate

```
  coarse case:  30000 x 2.240e-02 s x 1.6 = 1075.2 s = 17.92 core-minutes
  fine case:    40000 x 5.873e-02 s x 1.6 = 3758.7 s = 62.65 core-minutes

  7 coarse cases (S_SST_c, S_KE_c, S_LS_c, C1, C2, C3, C4)   125.4 core-minutes
  3 fine cases   (S_SST_f, S_KE_f, S_LS_f)                   188.0 core-minutes
  pilots already spent (6.72 + 17.62 + 0.53 s of failed starts) 0.4 core-minutes
                                                            --------------------
  first pass                                                 313.8 core-minutes
  continuation reserve: one further stage at half length on
    any case missing the convergence criterion (the K0cT
    rung needed this on every fine mesh)                     157.0 core-minutes
                                                            --------------------
  TOTAL PROPOSED                                             470.8 core-minutes
                                                           =   7.85 core-hours
```

**In dollars, at the measured $0.0513 per core-hour: $0.403.** Against the $25
standing authorization that is **1.6 percent of it**, and the authorization is
not the binding constraint. Wall clock is: the box has 16 cores, every solve here
is single-core, and the ten cases were run concurrently, so wall clock is set by
the longest single case at about 63 minutes plus any continuation.

### 2.3 Stop rules, fixed now

1. **If the running total reaches 700 core-minutes** (1.5x the proposal), the
   remaining cases are abandoned and the rung reports what it has, with the unrun
   cases named. A reduced run is not silently relabelled as the rung.
2. **If any single case overruns its own line above by more than 1.6x, the run
   stops and the estimate is re-made.** An estimate that turns out low is not a
   licence to continue.
3. **If a graded case cannot meet the convergence criterion after its
   continuation stage, its rows are REPORTED AS REFUSED with the measured
   spread.** A transient leg is not run inside this authorization and is proposed
   rather than executed.

### 2.4 What would blow this estimate, named in advance

1. **Ra 1.58e9 is three decades above the K0cT rung and steady RANS may not
   converge.** The peak-to-peak criterion in Section 4 decides that, not
   residuals, and a refusal is a reported outcome rather than an overrun.
2. **LaunderSharmaKE is a low-Reynolds-number k-epsilon with exponential damping
   functions and is stiffer than kOmegaSST.** It was the named most likely
   consumer of the K0cT continuation reserve and is named again here.
3. **kEpsilon with wall functions on a y+ < 1 mesh is being run outside the
   treatment's design range on purpose** (Section 3). If it diverges rather than
   converging to a wrong answer, that is a reported outcome and not a retry.

---

## 3. Predictions, registered before the answer was known

**Pre-registration before compute is what makes fleet death survivable here and
it is not optional.** Each prediction below is a number or a verdict, not a
direction, so it can be wrong.

The evidence they are built on is the K0cT tall-cavity rung plus the newly
obtained Betts Table 1 (p. 682), which for the first time gave that rung a
Nusselt reference. Against it, on the tall cavity: **kOmegaSST under-predicted
Nusselt by 24.7 percent and over-stratified the core by 2.5x; LaunderSharmaKE
over-predicted Nusselt by 5.5 percent and under-stratified.** The one-line
reading carried into these predictions is that **kOmegaSST under-mixes a buoyant
cavity and LaunderSharmaKE over-mixes it.**

### 3.1 Per-model point predictions

| Quantity | reference | kOmegaSST | kEpsilon | LaunderSharmaKE |
| --- | ---: | ---: | ---: | ---: |
| G1 Nu_avg hot wall | 63.45 | **52** (-18 %) | **100** (+58 %) | **72** (+13 %) |
| G7 Sp (Y 0.30-0.70) | 0.481 | **0.65** | **0.30** | **0.35** |
| G8 peak mid-height vertical velocity | 0.2127 m/s | **0.24** (+13 %) | **0.28** (+32 %) | **0.17** (-20 %) |
| G9 peak location X | 0.00667 | PASS | **FAIL**, peak too close to the wall | PASS |
| G10 peak \|u'v'\| | 1.08e-3 | **0.5e-3** (-54 %) | **2.5e-3** (+130 %) | **1.4e-3** (+30 %) |

### 3.2 Per-model verdict predictions

| Model | predicted verdict | rows predicted to fail |
| --- | --- | --- |
| kOmegaSST | **GATE FAIL** | G1, G2, G5, G7, G10 |
| kEpsilon | **GATE FAIL** | G1-G7, G9, G10 |
| LaunderSharmaKE | **GATE FAIL** | G1, G2, G7, G8, G10 |

**Headline prediction: no model passes this gate, and the three bracket the
experiment rather than reproducing it** - kEpsilon high, kOmegaSST low,
LaunderSharmaKE between them and closest on integral heat transfer while worst on
velocity. If any model passes every row, this prediction was wrong and the
results record says so in those words.

### 3.3 Why kEpsilon was given the treatment it was, and why that is not a straw man

kEpsilon is the **high**-Reynolds-number model and was built with the high-Re wall
treatment (`nutkWallFunction`, `kqRWallFunction`, `epsilonWallFunction`). Giving
it the low-Re treatment the other two use would have been building a straw man:
it has no damping functions to make that treatment mean anything.

But the mesh is a low-Re mesh (first cell 0.25 mm, y+ under 1), because G6 and the
Nusselt definition itself require resolving a 2 mm conductive layer. **So kEpsilon
is being run with a wall treatment outside its design range, and that is the
point rather than an oversight.** The primaries predict the outcome directly:
Tian p. 859 states that "the logarithmic velocity profile does not exist in this
low turbulence natural convection in a square cavity", and Ampofo p. 3559 records
that the k-epsilon results of Barozzi et al. showed "a steeper velocity gradient
near the wall and the location of the peak velocity much closer to the wall than
in the present study", concluding that "near the wall, the k-epsilon model
predicts a higher rate of change of velocity which can lead to overestimation of
the wall shear stress". The prediction in Section 3.1 is that published
observation turned into numbers.

### 3.4 Controls and sensitivities, with their kinds and their registered thresholds

| case | KIND | registered prediction | what its failure would mean |
| --- | --- | --- | --- |
| **C1_laminar** | **RECOGNITION of a confound** | Sp or peak velocity differs from S_SST_c by **more than 10 %**. **Nu is NOT predicted to differ**, and that is deliberate: Tian p. 862 warns that "laminar flow modelling can predict the right Nu even if as a whole, the predicted temperature field is not good enough", and Lankhorst's laminar correlation gives 59.38 at this Ra against a measured 63.45 | If laminar lands inside the Nu bands, **the Nu rows do not discriminate a turbulence model from no model at all on this case**, and the results record must say so at full volume rather than quietly banking a passed row |
| **C2_seed_d100** | **RECOGNITION of a confound** | k seed reduced **100x**; \|dSp\| <= 0.02 and \|dV\|/V <= 3 % | If exceeded, the answer is the initial condition and every graded row on this rung is void |
| **C3_prt128** | **SENSITIVITY**, not a control | Prt 0.85 -> **1.28**, the value derived from Betts Table 1 p. 682 (`nu_T/nu = 55`, `alpha_T/alpha = 30`, `Pr = 0.700` at the centre-line, giving `Prt = (55/30) x 0.700 = 1.28`). Nu_hot predicted to **fall by 5-20 %** | Quantifies how much of the model-to-model spread a constant turbulent Prandtl number explains. If Nu moves by under 1 %, the constant-Prt assumption is not where this case class is losing accuracy and the day order's third named failure mode is closed negative |
| **C4_adiabatic** | **SENSITIVITY**, not a control | horizontal walls replaced by `zeroGradient`; Nu_hot moves by **more than 5 %** and Sp by **more than 0.05** | Tests specification Section 2.2's claim that the idealisation choice is a 13 % effect (Beghein et al. via Tian p. 861). If it moves Nu by under 1 %, that concern was misplaced and the specification is wrong on a point it argued at length |
| **C5_mutation** | **CONTROL**, zero compute | Every graded row must be made to FAIL by perturbing its reference, and every failing row made to PASS. Both directions | A gate whose rows cannot be flipped in both directions is not measuring anything (L-84) |

---

## 4. Convergence criterion, fixed before the run

From `docs/physics_rules.yaml`, thermal block, unchanged from the K0cT rung:
**peak-to-peak spread** of the graded quantity over a **fixed window of 400 outer
iterations** at a 50-iteration sample interval, minimum 9 samples. Not residuals.
Not an endpoint difference. Not a fraction of the run.

Three quantities must all pass:

| quantity | criterion |
| --- | --- |
| (a) Nu_avg on the hot wall | peak-to-peak spread < 0.5 % |
| (b) Sp, mid-width Y 0.30-0.70 | peak-to-peak spread < 0.005 |
| (c) peak mid-height vertical velocity | peak-to-peak spread < 1.0 % |

A case failing any of the three has its rows **REPORTED AS REFUSED** with the
measured spread printed. It is not graded and it is not quietly dropped.

---

## 5. What is reported and never gated, restated here so the run cannot forget

Per `VERIFICATION_CHARTER.md` lines 106-111, **an identity is not a control**.

- **Heat balance on the sealed cavity** is a near-identity: the discrete
  temperature equation conserves at every iteration whether or not the solve has
  converged. Reported. Never counted as a passed gate.
- **theta at the cavity centre** is a near-identity for a Boussinesq solve, which
  Tian p. 862 states outright. Reported as a measurement of the non-Boussinesq
  defect. Never gated.
- **Turbulence kinetic energy** and **peak rms vertical velocity** each require a
  modelling assumption on at least one side. Reported. Never gated. The reason
  the second of these was withdrawn from the graded set is recorded in the
  specification's Section 3.2 amendment note, in the open, because a row removed
  without its reason reads later as a row that passed.

---

## 6. Provenance note on the three primaries

The paths in the day order (`docs/papers/heat_transfer_paper/...`) **did not
exist** by the time this rung ran; a concurrent lane had reorganised
`docs/papers/` into topic subdirectories. Every primary here was therefore
located **by content** - matched on the DOI or PII string in its own PDF metadata
- and not by an assembled path literal. That is the L-137 failure class, and the
K2c lane hit a live instance of it at this same HEAD on the same day. No script in
`K0cS_runs/` holds a path to a paper.
