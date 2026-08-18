# K0cS. Square-cavity turbulent rung: executed

Campaign F14, gate K0c, square-cavity turbulent rung (K0cS). Executed
2026-08-18 under the standing $25 authorization. Reference values:
`K0cS_SQUARE_CAVITY_GATE.md`. Predictions and cost estimate:
`K0cS_PREREGISTRATION.md`, **committed at `6d149d51` before any result
existed**. Run tree: `verification/runs/F14-cooling-ladder/K0cS_runs/`.
Comparator: `analyse_k0cs.py`; machine-readable output `gate_k0cs.json`;
generated table `GATE_TABLE.md`; reported-not-graded measurements
`diagnostics_k0cs.json`.

---

## 0. Verdict

| Model | Verdict | Rows |
| --- | --- | --- |
| **kOmegaSST** | **GATE FAIL** | 8 of 10 graded rows failed |
| **kEpsilon** | **GATE FAIL** | 6 of 10 graded rows failed |
| **LaunderSharmaKE** | **REFUSED** | not graded: the fine mesh missed the registered convergence criterion |
| **The rung** | **GATE FAIL** | 14 of 20 graded rows failed; 0 models passed |

**The headline prediction registered before the run - "no model passes this
gate, and the three bracket the experiment rather than reproducing it" - held.**
The models bracket the measured hot-wall Nusselt of 63.45 from 53.69
(LaunderSharmaKE) to 76.49 (kEpsilon), and none is inside its band.

Every graded row was shown reachable in **both** directions by the mutation
control (`every_row_reachable_both_ways: true`), so no row on this gate is
decorative.

---

## 1. THE MOST IMPORTANT RESULT: two of this gate's rows cannot tell a turbulence model from no model at all

Control C1 ran the identical case with **no turbulence model**. It was
registered as a RECOGNITION control precisely because Tian p. 862 warns that
"laminar flow modelling can predict the right Nu even if as a whole, the
predicted temperature field is not good enough". **The warning was right, and
the result is worse than the warning.**

| | rows passed |
| --- | --- |
| C1, laminar, **no turbulence model** | **G3, G4, G5, G9 - four rows** |
| kOmegaSST, fine mesh | **G5, G9 - two rows** |
| kEpsilon, fine mesh | G7, G8, G9, G10 - four rows |

**The set of rows kOmegaSST passes that a laminar solve does not also pass is
EMPTY.** On hot-wall Nusselt the two sit **1.21 percent apart** (laminar 55.264,
kOmegaSST 54.605, same coarse mesh).

Two consequences, stated rather than softened:

1. **kOmegaSST's two passed rows carry no evidential weight about turbulence
   modelling on this case.** A row that cannot distinguish the thing it is
   testing is not a row that passed. G5 (local Nu at mid-height) and G9 (peak
   velocity location) are passed equally by a solve with the turbulence model
   switched off, so they measure the geometry and the mesh, not the closure.
2. **A laminar solve outperforms kOmegaSST on this gate, 4 rows to 2.** That is
   not an argument for running laminar; it is a measurement of how little
   kOmegaSST is contributing at Ra 1.58e9 in this cavity, and it is corroborated
   independently by the eddy viscosity: kOmegaSST's domain-maximum `nu_t/nu`
   **fell from 12.1 to 6.1 under mesh refinement**.

**kEpsilon is the only model on this rung whose passes discriminate.** It passes
three rows - G7 stratification, G8 peak velocity, G10 Reynolds shear stress -
that a laminar solve fails. Those three are the rows that carry information
about turbulence closure, and they are the rows kOmegaSST fails.

**Caveat carried, not buried:** C1 did not meet the convergence criterion
(Nu peak-to-peak 2.15 percent against 0.5 percent). A laminar solve of a square
cavity at Ra 1.58e9 is genuinely unsteady, so its numbers are a time-varying
quantity sampled at 30000 iterations. That widens C1's own error bars; it does
not rescue the two rows, because the gap on them is far inside any plausible
unsteady excursion.

---

## 2. Registered predictions against measurement

Registered in `K0cS_PREREGISTRATION.md` Section 3.1 before the run. **Most of
them were wrong, and two were wrong in direction.**

| Row | reference | model | **predicted** | **measured (fine)** | prediction |
| --- | ---: | --- | ---: | ---: | --- |
| G1 Nu hot | 63.45 | kOmegaSST | 52 (-18 %) | **54.96 (-13.4 %)** | direction right, magnitude close |
| G1 Nu hot | 63.45 | kEpsilon | 100 (+58 %) | **76.49 (+20.5 %)** | direction right, **magnitude 3x too large** |
| G1 Nu hot | 63.45 | LaunderSharmaKE | 72 (+13 %) | **53.69 (-15.4 %)** | **WRONG DIRECTION** |
| G7 Sp | 0.481 | kOmegaSST | 0.65 | **0.7541** | direction right, under-predicted |
| G7 Sp | 0.481 | kEpsilon | 0.30 | **0.4888** | **WRONG: predicted FAIL, it PASSED, and it is the closest number on the rung (dev 0.008)** |
| G7 Sp | 0.481 | LaunderSharmaKE | 0.35 | **0.7784** | **WRONG DIRECTION** |
| G8 V peak | 0.2127 | kOmegaSST | 0.24 (+13 %) | **0.2552 (+20.0 %)** | direction right |
| G8 V peak | 0.2127 | kEpsilon | 0.28 (+32 %) | **0.1965 (-7.6 %)** | **WRONG DIRECTION, and it PASSED** |
| G9 location | 0.00667 | kEpsilon | **FAIL**, "peak too close to the wall" | **0.00673, PASS** | **WRONG** |
| G10 u'v' | 1.08e-3 | kOmegaSST | 0.5e-3 (-54 %) | **4.71e-4 (-56.3 %)** | **accurate to 2 percentage points** |
| G10 u'v' | 1.08e-3 | kEpsilon | 2.5e-3 (+130 %) | **1.25e-3 (+15.4 %)** | direction right, magnitude 8x too large |

Verdict-level predictions:

| Model | predicted verdict | predicted failing rows | **actual** |
| --- | --- | --- | --- |
| kOmegaSST | GATE FAIL | G1, G2, G5, G7, G10 | **GATE FAIL** on G1, G2, G3, G4, G6, G7, G8, G10. G5 was predicted to fail and **passed**; G3, G4, G6, G8 failed unpredicted |
| kEpsilon | GATE FAIL | G1-G7, G9, G10 | **GATE FAIL** on G1-G6 only. **G7, G8, G9, G10 all passed against prediction** |
| LaunderSharmaKE | GATE FAIL | G1, G2, G7, G8, G10 | **REFUSED.** Not a failure against the experiment at all - see Section 4 |

**What the misses are worth saying about.** The pre-registration reasoned from
the K0cT tall-cavity rung, where kOmegaSST under-mixed and LaunderSharmaKE
over-mixed, and it carried that one-line reading onto a different geometry three
Rayleigh decades away. **The kOmegaSST half transferred and the LaunderSharmaKE
half inverted**: on the square cavity LaunderSharmaKE under-mixed so severely
that it left turbulence modelling entirely. The prediction that kEpsilon would be
the worst performer - built from two published statements about k-epsilon in
cavities - was **the most wrong prediction on the page**: kEpsilon is the only
model here whose passes discriminate.

---

## 3. Grid refinement moved the stratification AWAY from the experiment

**This is the finding this ladder exists to catch, and it gets its own section.**

| Model | Sp coarse (120x120) | Sp fine (192x192) | reference | moved |
| --- | ---: | ---: | ---: | --- |
| kOmegaSST | 0.6738 (dev 0.193) | **0.7541 (dev 0.273)** | 0.481 | **AWAY, by 0.080** |
| LaunderSharmaKE | 0.6199 (dev 0.139) | **0.7784 (dev 0.297)** | 0.481 | **AWAY, by 0.158** |
| kEpsilon | 0.4925 (dev 0.012) | 0.4888 (dev 0.008) | 0.481 | toward, by 0.004 |

For kOmegaSST and LaunderSharmaKE the coarse mesh sat **closer to the experiment
than the converged answer does**. Their coarse agreement was cancellation between
a model error and a discretisation error, and refining the mesh removed the
discretisation error and exposed the model error. **A single-mesh solve of either
model would have reported a better number and a worse result.** That is exactly
why the specification's Section 2.5 grid-pair rule exists, and this rung is its
justification rather than merely its application.

kEpsilon is grid-converged on this quantity (0.004 change over a 1.6x
refinement), which is a further reason its passes mean more than the others'.

---

## 4. LaunderSharmaKE was REFUSED, and it did not lose to the experiment

**REFUSED is not GATE FAIL and the distinction is the result.** The model was
not outperformed by the data; **it stopped modelling turbulence when the
near-wall mesh was refined**, and a model outside its own validity domain cannot
be graded against an experiment.

| | coarse 120x120 | fine 192x192 |
| --- | ---: | ---: |
| Convergence (registered: Nu p2p < 0.5 %, V p2p < 1.0 %) | **FAIL** (3.09 %, 2.76 %) | **FAIL** (0.18 %, **1.50 %**) |
| `nu_t/nu`, domain maximum | 17.3 | **6.1e-4** |
| Damping function `fmu`, implied maximum | 0.887 | **0.034** |
| `Cmu k^2 / eps`, maximum | 3.06e-4 | 2.80e-7 |
| Peak Reynolds shear stress at mid-height | 3.15e-5 | **3.89e-17** |
| Solver `bounding k` events in the run | - | **25 996 of 40 000 iterations** |
| Same count for kEpsilon on the same mesh | - | **0** |

The mechanism is the model's own low-Reynolds-number damping. As the near-wall
cells shrink, the turbulent Reynolds number in them falls, `fmu` collapses, `k`
is driven onto its 1e-15 floor across the domain, and the eddy viscosity ends
**four orders of magnitude below molecular**. The solve is then a laminar solve
in all but name, which is why it also fails the convergence criterion: a laminar
square cavity at Ra 1.58e9 is unsteady.

**Its numbers are recorded for the record and grade nothing:** Nu_hot 53.694,
Nu_cold 52.750, Sp 0.7784, V peak 0.2778 m/s at X = 0.0062.

This is a **cross-mesh** failure of the kind the day order asked for - "where
near-wall treatment breaks" - and it is the sharpest one on the rung: the same
model, same case, same boundary conditions, turbulent on one mesh and laminar on
a mesh 1.6x finer.

---

## 5. The graded tables

Deviation `REL = 100 |q_solve - q_ref| / |q_ref|`, or absolute where the
specification says so. Verdict on the **fine** mesh; coarse carried alongside.

### 5.1 kOmegaSST - GATE FAIL, 8 of 10

| row | quantity | reference | coarse | **fine** | deviation | band | verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| G1 | Nu avg hot wall | 63.45 | 54.605 | **54.958** | 13.383 % | 10 % | **GATE FAIL** |
| G2 | Nu avg cold wall | 63.95 | 54.332 | **54.781** | 14.337 % | 10 % | **GATE FAIL** |
| G3 | Nu avg bottom wall | 14.44 | 10.970 | **11.359** | 21.337 % | 20 % | **GATE FAIL** |
| G4 | Nu avg top wall | 15.04 | 11.197 | **11.568** | 23.088 % | 20 % | **GATE FAIL** |
| G5 | local Nu at mid-height | 58.75 | 53.032 | **53.907** | 8.243 % | 12 % | PASS |
| G6 | max local Nu, hot wall | 136.5 | 95.573 | **96.275** | 29.469 % | 20 % | **GATE FAIL** |
| G7 | stratification Sp | 0.481 | 0.6738 | **0.7541** | 0.273 | 0.12 | **GATE FAIL** |
| G8 | peak mid-height velocity | 0.2127 | 0.2539 | **0.2552** | 19.976 % | 15 % | **GATE FAIL** |
| G9 | peak location X | 0.00667 | 0.00608 | **0.00570** | 0.001 | 0.005 | PASS |
| G10 | peak Reynolds stress | 1.08e-3 | 4.48e-4 | **4.71e-4** | 56.348 % | 40 % | **GATE FAIL** |

### 5.2 kEpsilon - GATE FAIL, 6 of 10

| row | quantity | reference | coarse | **fine** | deviation | band | verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| G1 | Nu avg hot wall | 63.45 | 74.329 | **76.488** | 20.548 % | 10 % | **GATE FAIL** |
| G2 | Nu avg cold wall | 63.95 | 74.037 | **76.178** | 19.121 % | 10 % | **GATE FAIL** |
| G3 | Nu avg bottom wall | 14.44 | 8.819 | **8.828** | 38.868 % | 20 % | **GATE FAIL** |
| G4 | Nu avg top wall | 15.04 | 9.111 | **9.137** | 39.246 % | 20 % | **GATE FAIL** |
| G5 | local Nu at mid-height | 58.75 | 78.616 | **80.976** | 37.832 % | 12 % | **GATE FAIL** |
| G6 | max local Nu, hot wall | 136.5 | 96.700 | **98.335** | 27.959 % | 20 % | **GATE FAIL** |
| G7 | stratification Sp | 0.481 | 0.4925 | **0.4888** | 0.008 | 0.12 | PASS |
| G8 | peak mid-height velocity | 0.2127 | 0.1961 | **0.1965** | 7.595 % | 15 % | PASS |
| G9 | peak location X | 0.00667 | 0.00692 | **0.00673** | 0.000 | 0.005 | PASS |
| G10 | peak Reynolds stress | 1.08e-3 | 1.21e-3 | **1.25e-3** | 15.358 % | 40 % | PASS |

**kEpsilon's failure has a shape.** It reproduces the *flow* - stratification to
0.008, peak velocity to 7.6 percent, peak location to 0.0001 in X, Reynolds
stress to 15 percent - and gets the *heat transfer* wrong by 20 percent on the
vertical walls and 38-39 percent on the horizontal ones, over-predicting the
vertical and under-predicting the horizontal. It moves the right amount of fluid
and the wrong amount of heat. On a mesh with y+ under 0.4 its wall functions are
far outside their design range (Section 6.3), which is the natural place to look
for a defect that lands on wall heat flux and spares the interior flow.

---

## 6. Reported, and never graded

Per `VERIFICATION_CHARTER.md` lines 106-111, an identity is not a control.

### 6.1 Heat balance - a near-identity, and it earned its keep as an instrument

| case | closure | case | closure |
| --- | ---: | --- | ---: |
| S_KE_c / S_KE_f | **0.0000 % / 0.0000 %** | S_LS_c / S_LS_f | 2.837 % / 1.610 % |
| S_SST_c / S_SST_f | 0.085 % / 0.058 % | C1_laminar | **8.967 %** |
| C2 / C3 / C4 | 0.063 / 0.024 / 0.231 % | | |

**This is not evidence that any physics is right**, and it is counted toward no
verdict. Its value on this rung was diagnostic: **the closure is what found a
real error in the comparator.** `Nu_avg` was first formed as an arithmetic mean
over wall faces, but this mesh is graded 117:1 and Ampofo's average is an area
average, so the tiny corner cells - where local Nu runs from 136 to 17 - were
weighted a hundredfold too heavily. The closure sat at 2.5-8.4 percent. With
area weighting it fell to **0.0000 percent** on the fully converged kEpsilon
cases, and every Nusselt number on this page moved (kOmegaSST 47.2 to 54.6,
kEpsilon 58.3 to 74.3). The closure also tracks convergence quality exactly: the
two cases that failed the convergence criterion are the two with closures above
1 percent.

### 6.2 theta at the cavity centre - a near-identity for a Boussinesq solve

| | Ampofo | Tian | S_SST_f | S_KE_f | S_LS_f | C1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| theta centre | **0.5174** | **0.514** | 0.4973 | 0.4999 | 0.4809 | 0.4877 |

Tian p. 862 states outright that a Boussinesq solve predicts 0.5 by symmetry.
Every converged case here returns 0.497-0.500. **This measures the
non-Boussinesq defect - about 0.017 in theta, 0.7 K - and not any turbulence
model**, which is why it is gated on nothing. `beta.dT` on this case is 0.132,
above the lab's own 0.1 line, and Ampofo p. 3564 independently measured the 40 K
difference as an 11 percent density variation.

### 6.3 Wall-gradient method sensitivity, and where the near-wall treatment breaks

Both experiments extracted the wall gradient by **linear best fit over the first
6-9 near-wall points** (Ampofo p. 3564; Tian p. 859). The comparator grades on
the two-point wall gradient. On a solved field those need not agree, and how much
they disagree is a property of the model's near-wall structure:

| case | two-point | LSQ over 6 cells | LSQ over 9 cells | spread |
| --- | ---: | ---: | ---: | ---: |
| S_SST_c | 54.605 | 54.419 | 53.685 | 1.69 % |
| S_LS_c | 53.445 | 53.066 | 52.171 | 2.38 % |
| **S_KE_c** | 74.329 | 70.914 | 67.712 | **8.90 %** |
| S_SST_f | - | - | - | 0.30 % |
| S_LS_f | - | - | - | 0.36 % |
| **S_KE_f** | - | - | - | **2.91 %** |

**kEpsilon is three to nine times more sensitive to the fitting window than
either low-Re model**, because its near-wall temperature profile curves more
sharply just outside the conductive layer. Within the 2 mm conductive layer every
model is linear (R-squared 0.99998 or better), so the experiment's own assumption
holds; the divergence is in how fast each leaves it. **The experimental
measurement procedure, applied to the kEpsilon field, would return a different
Nusselt number than its wall gradient does** - which is a concrete statement of
where the high-Re wall treatment stops being commensurate with the measurement it
is compared against.

### 6.4 Mid-height traverse against Ampofo Table 2, 62 stations

| case | theta rms, boundary layers | theta rms, core | v rms, BL | v rms, core |
| --- | ---: | ---: | ---: | ---: |
| S_SST_f | 6.17 K | 0.90 K | - | - |
| S_KE_f | 6.11 K | 0.94 K | - | - |
| S_LS_f | 6.23 K | 1.78 K | - | - |
| C1_laminar | 6.28 K | 2.05 K | - | - |

**Every model, including no model at all, mis-predicts the near-wall temperature
field by the same 6.1-6.3 K rms.** The models differ from each other far less in
the boundary layer than each differs from the experiment. That is a failure mode
none of the three closures addresses, and it is invisible in the integral
Nusselt rows.

### 6.5 Others reported

Peak rms vertical velocity (the row withdrawn before compute, gate spec Section
3.2 amendment), turbulence kinetic energy, wall shear stress, turbulent Prandtl
number. Antisymmetry defect of the two mid-height velocity peaks: converged cases
0.05-0.34 percent against the experiment's own 2.7 percent; C1_laminar 9.61
percent, which is the unsteadiness showing.

---

## 7. Controls and sensitivities

| case | KIND | registered | measured | outcome |
| --- | --- | --- | --- | --- |
| **C1_laminar** | RECOGNITION of a confound | Sp **or** peak velocity differs from S_SST_c by more than 10 % | Sp differs 4.1 %, **peak velocity 13.2 %** | **MET** on velocity - and it exposed far more than it was built for (Section 1) |
| **C2_seed_d100** | RECOGNITION of a confound | k seed / 100; \|dSp\| <= 0.02 **and** \|dV\|/V <= 3 % | **dSp 0.0147**, **dV 0.57 %** | **MET.** The answer is not the initial condition |
| **C3_prt128** | SENSITIVITY | Prt 0.85 -> 1.28; Nu_hot falls **5-20 %** | Nu_hot fell **1.75 %** | **PREDICTION MISSED - and the miss is the finding.** See below |
| **C4_adiabatic** | SENSITIVITY | horizontal walls -> zeroGradient; Nu_hot moves > 5 % **and** Sp moves > 0.05 | Nu_hot **+10.22 %**, Sp **+0.1355** | **MET.** Corroborates the 13 % idealisation split the specification cited from Beghein via Tian p. 861 |
| **C5_mutation** | CONTROL, zero compute | every graded row flippable both ways | all 20 rows | **MET** |

### 7.1 C3: a named failure mode CLOSED NEGATIVE for this geometry

**Stated positively, because an eliminated hypothesis is a result and not an
absence.** The day order named "where a constant turbulent Prandtl number
strains" as one of three failure modes to hunt. **On the square cavity it does
not strain.** Moving Prt from 0.85 to 1.28 - a 51 percent change, and 1.28 is not
an arbitrary value but the number **derived from Betts Table 1 p. 682** for the
tall cavity - moved hot-wall Nusselt by **1.75 percent**, far below the 5-20
percent registered and far below the 20 percent this rung is wrong by. The
eddy viscosity responded strongly (`nu_t/nu` max 12.1 to 19.2, +59 percent) while
the heat transfer did not. **Constant Prt is not where this geometry loses
accuracy, and effort spent tuning it would be wasted.**

**The tension, recorded rather than resolved:** this does **not** transfer to the
tall cavity. Betts Table 1 gives a *measured* centre-line Prt of **1.07 (Ra
0.86e6) and 1.28 (Ra 1.43e6)**, against the 0.85 the K0cT rung used - 21 and 34
percent low - and that measurement stands whatever the square cavity does. The
square cavity has no measured Prt at all (Section 9). So the correct reading is
narrow: **the square cavity's Nusselt error is insensitive to Prt; the tall
cavity's Prt is measurably wrong.** Those are two different statements and
neither licenses the other.

---

## 8. Cost, against the estimate written first

| | core-minutes |
| --- | ---: |
| 7 coarse cases (S_SST_c 11.61, S_KE_c 11.17, S_LS_c 11.67, C1 7.84, C2 11.70, C3 11.68, C4 11.88) | 77.6 |
| 3 fine cases (S_SST_f 36.17, S_LS_f 41.45, S_KE_f 50.93) | 128.6 |
| pilots (charged) | 0.4 |
| **TOTAL** | **206.5** |

**206.5 core-minutes = 3.44 core-hours = $0.177** at the measured $0.0513 per
core-hour.

| | core-minutes | outcome |
| --- | ---: | --- |
| Registered first pass | 313.8 | came in at **66 %** |
| Registered total incl. continuation reserve | 470.8 | came in at **44 %** |
| Dollar authorization | $25 | spent **0.71 %** |

**The continuation reserve was not drawn**: every case reached its registered
endTime in one stage. No stop rule fired. Wall clock, the binding constraint, was
about 51 minutes for the longest case with all ten run concurrently on a 16-core
box shared with another lane.

The estimate was **conservative by a factor of 2.3 overall**, driven by the 1.6x
rate contingency plus iteration budgets set from the K0cT rung's worst case. An
estimate that overshoots is not free - it reserves capacity others could use -
and the next rung on this case class should carry a contingency nearer 1.2x.

---

## 9. Filed NOT OBTAINED

| Quantity | Consequence |
| --- | --- |
| **Tian and Karayiannis Part II** (turbulence quantities) | Every turbulence statistic on this rung is **single-source** (Ampofo Table 2 only). G10 carries the widest band on the gate for this reason and is marked SINGLE SOURCE |
| **Turbulent Prandtl number for the square cavity** | Neither paper reports an eddy diffusivity or eddy viscosity for this cavity. Prt was an ungrounded modelling input; C3 measured its influence rather than its correctness |
| **Any author's uncertainty on the stratification parameter** | Tian p. 862 gives Sp = 0.50 with no error bar **and no fitting window**. The G7 band was built from the measured window sensitivity (0.16 across windows) instead |
| **Peak rms vertical velocity as a graded row** | Withdrawn **before compute** and recorded in the open (gate spec Section 3.2 amendment): no two-equation model can answer it without an isotropy assumption that Ampofo p. 3559 measured to be false |

---

## 10. Defects found while executing this rung

1. **`Nu_avg` was an arithmetic mean on a 117:1 graded mesh** where the reference
   is an area average. Every Nusselt number was wrong by 10-27 percent before the
   fix. **Found by the heat balance**, a near-identity that grades nothing.
2. **`build_cases.py` resolved the specification through an assembled
   `"../../../.."` literal** - the same L-137 class that left `analyse_k0ct.py`
   broken at HEAD. **Found by the reproducibility control**, which rebuilt from a
   directory one level away, refused with rc=2, and wrote nothing; the control's
   own first version misread that as "120 differing dictionaries". Both fixed to
   resolve by upward search. All **147 dictionaries now regenerate
   byte-identically**.
3. **The Ampofo Table 4 parser swallowed two rows from a different table**,
   reporting 23 stations where the table has 21, and would have imposed a
   corrupted wall temperature on every case. Found by an **exact** station count,
   which is why the count is an equality and not a lower bound.
4. **A strict monotonicity check refused Ampofo's own measured top-wall
   profile.** The rise is 0.0009 in theta = 0.036 K at X = 0.0133, **inside the
   paper's stated 0.10 K air-temperature accuracy**. The non-monotonicity is in
   the measurement, not the parse; the tolerance was set to the instrument's
   figure and no wider.
5. **OpenFOAM v2606's expression parser has a ternary nesting limit.** A
   21-station piecewise-linear boundary condition written as 20 nested `? :`
   operators was refused at position 1523, the eighteenth ternary. Rewritten as a
   mathematically identical **flat sum of clamped ramps**, asserted equal at every
   tabulated station.
6. **`set -u` silently killed all ten runs at launch.** OpenFOAM's `etc/bashrc`
   dereferences unset variables, so sourcing it under `set -u` exited each runner
   **before its completion marker was written**. All ten "finished" in 62 seconds
   with zero markers. **The marker discipline caught it**; a process-table check
   would have shown no solvers running and read exactly like success.

---

## 11. What this rung does NOT establish

- **It does not validate kEpsilon.** kEpsilon is GATE FAIL. That its passes
  discriminate where kOmegaSST's do not is a statement about which rows carry
  information, not a promotion.
- **It does not transfer to the tall cavity.** The K0cT rung is a separate
  geometry three Rayleigh decades away, and Section 7.1 records one quantity that
  demonstrably does not transfer.
- **It does not resolve the near-wall temperature error** (Section 6.4), which is
  common to all three closures and to no closure at all.
- **No trust tier above TREND ONLY is claimed for any model on this case.** The
  gate's own Section 3.4 makes VALIDATED conditional on passing every row, and
  none did.
- **Nothing here was submitted, sent, filed, uploaded or registered.**
  Submissions are PARKED.

---

## Dated correction, 2026-08-18 — the square-cavity turbulent Prandtl number was NOT missing

**Nothing above is edited.** Appended under W-4, superseding one entry of §9.

**§9 filed the square cavity's turbulent Prandtl number as NOT OBTAINED. It is
reported by the primary this rung is graded against.** Ampofo and Karayiannis
(2003), p. 3569, in the text beside Fig. 11:

> *"In the comparatively wide region (X = 0.015–0.03 of Fig. 11), turbulent
> viscosity and turbulent diffusivity have a similar profile and so the turbulent
> Prandtl number takes a value of about unity."*

Figure 11 plots the distribution alongside turbulent diffusivity and turbulent
viscosity. **It was missed because it is prose and a figure rather than a table
row**, and because the sweep that looked for it ran over a paper directory in
which 13 PDFs had no extracted-text sidecar at all — a defect recorded and
repaired the same day.

**The paper says something sharper than "about unity", and it matters more.**
Same page:

> *"the distribution of turbulent viscosity for momentum has a discontinuity at
> the maximum velocity location. On the other hand, turbulent diffusivity for
> heat shows a continuous profile. As a consequence, the distribution of
> turbulent Prandtl number ... also has a discontinuity at the maximum velocity
> location."*

**A constant turbulent Prandtl number cannot represent a discontinuous field**,
whatever constant is chosen. That is a statement about the FORM of the closure,
not about the value of a coefficient, and it is exactly the distinction control
C3 could not reach: C3 varied the constant from 0.85 to 1.28 and moved the
average Nusselt number by 1.75 %, which establishes that the integral heat
transfer is insensitive to **the value**. It says nothing about the form.

**Neither the C3 result nor this rung's verdict moves.** C3 closed negative and
still closes negative: on this geometry, changing the constant does not recover
the missing heat transfer. What changes is what may be concluded from it — the
earlier reading, that constant-Prt is not where this geometry loses accuracy, is
now bounded to *the value of the constant* and does not extend to the assumption
of constancy itself. **An insensitivity to a parameter is not evidence that the
parameter's functional form is adequate.**

**Tier: PRIMARY** for the "about unity" value and for the discontinuity, both
READ IN FULL from `docs/papers/buoyant_natural_convection/ampofo_karayiannis_2003_ijhmt_46.pdf`,
p. 3569. **The numerical distribution itself remains NOT OBTAINED**: Fig. 11 has
not been digitised, and no digitisation increment is stated here, so no reference
column is armed by this correction. Recorded under D415.
