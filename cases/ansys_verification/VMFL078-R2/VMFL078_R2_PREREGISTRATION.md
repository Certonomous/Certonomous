# VMFL078-R2 — PRE-REGISTRATION: does removing the symmetry plane move the answer, and where is Figure .78.2 actually sampled?

**Version 1.0 — 2026-09-12 — ansys-verification / ansys-lane-opus**
**Status at writing: NOT YET COMMITTED. No R2 solver run exists. The run root
`verification/runs/ansys_verification/VMFL078-R2/` DOES NOT EXIST on disk at the time
this sentence is written, and the freeze is worthless if it does.**

**This is a SUCCESSOR, not an amendment.** `VMFL078`'s gates closed at its first
compute. `cases/ansys_verification/VMFL078/PREREGISTRATION.md`,
`VMFL078_LIMB_B_PREREGISTRATION.md` and `grade_vmfl078.py` are **frozen and are not
touched by this document** (rule 6). VMFL078's verdicts stand exactly as graded:
limb A `GATE REACHED`, limb B `GATE FAIL`.

---

## 0. THE FINDING THAT PRODUCED THIS REGISTRATION — including the part that kills the hypothesis I was sent to test

This lane was dispatched to test the hypothesis that **the VMFL078 grid family is
anisotropic in the spanwise direction** and that its limb-B `GATE FAIL` is the
signature of a triple converging cleanly to its own under-resolved answer.

**That hypothesis is false, and it is false on the face of the case files.** It is
recorded here because a supervisor who dispatched a wrong hypothesis is entitled to be
told, and because the registration must not quietly test something else.

### 0.1 The family is already isotropic. There is no spanwise anisotropy to fix.

VMFL078's counts are 32×32×16 / 64×64×32 / 128×128×64 over a domain of
**1 × 1 × 0.5 m**. The 1 : 1 : 0.5 *count* ratio matches the 1 : 1 : 0.5 *edge-length*
ratio exactly, so Δx = Δy = Δz = 1/N at every level and **every cell is a cube**.
`checkMesh` measured max aspect ratio **1.0**. The halved spanwise *count* is the
halved spanwise *domain*, not halved spanwise *resolution*. An "isotropic-z family"
would be the family that already ran.

### 0.2 Refinement cannot close the gap, and this is measured, not argued.

From the three committed probe files under `verification/runs/ansys_verification/VMFL078/`:

| | L1 | L2 | L3 | L3−L2 | L3 − reference |
|---|---|---|---|---|---|
| centreline zero-crossing y (m) | 0.48627 | 0.47451 | 0.47287 | −0.00164 | **−0.0800** |
| u at y = 0.4505 (m/s) | −0.012092 | −0.007755 | −0.007135 | +0.00062 | **+0.02467** |
| u at y = 0.5000 (m/s) | +0.004293 | +0.007528 | +0.007931 | +0.00040 | **+0.02212** |

The crossing's level-to-level changes are −0.011763 then −0.001631, a ratio of
**0.1387** — observed order **p = 2.85** at r = 2 — and the Richardson extrapolate is
**y = 0.47261**, against the digitised reference's **0.5529**. In the core the L2→L3
change is **0.0004–0.0019 m/s** while the gap to the reference is **0.017–0.025 m/s**,
an order of magnitude larger, and **the refinement is moving away from the reference,
not toward it**. A fourth or fifth level of the same family would land on 0.4726.
**Grid resolution is exonerated by the data already on disk. Re-running a finer
uniform family would spend core-minutes to reproduce the answer we have.**

### 0.3 What else was ruled out, and how

* **Iterative convergence.** L3 stopped on `residualControl` at iteration 1921 with
  `Solving for Ux, Initial residual = 1.334e-10` and one
  `SIMPLE solution converged` line (`L3/log.simpleFoam`). Iterative error is ~7 orders
  below the discrepancy. It was not a stall.
* **Turbulence.** `L3/log.simpleFoam` prints `Selecting turbulence model type laminar`
  / `Selecting laminar stress model Stokes`. The manual specifies laminar. No closure
  is active.
* **Discretisation scheme.** `div(phi,U) bounded Gauss linear` is unlimited central
  differencing, 2nd-order and **consistent**; the `bounded` correction is
  `−Sp(div(phi), U)`, which vanishes identically at a converged solution and is
  ~1e−10 here. A consistent scheme converges to the right answer, and §0.2 shows this
  one has converged. The scheme is not a bias source at this residual level.
* **The digitisation.** `figure_78_2/digitize_fig782.py` calibrates on 11 x-ticks and
  8 y-ticks with RMS residuals of **0.132 px** and **0.139 px**, and validates against
  the two *exact* physical data printed in the figure itself: the floor no-slip point
  reads **0.001262** where 0 is required, and the lid reads **1.001052** where 1 is
  required. A shared additive calibration bias of the size in question (0.02 m/s) is
  excluded by those two anchors. The band is not the problem.
* **The symmetry-plane patch behaving as a wall.** VMFL078's `symmetryCheck` probes
  give |u(z=0.5) − u(z=0.4)| = 0.002–0.003 m/s at every level; a no-slip face would
  drive u(z=0.5) to zero, and it reads −0.2662 at y = 0.1. The patch is a symmetry
  plane, not a wall.

### 0.4 What the data DOES point at — and why it must be tested, not believed

The same L3 field, read directly from `L3/1921/U`, carries the following. `u` on the
vertical line x = 0.5 was evaluated at every spanwise cell layer and scored against the
**frozen limb-B band** (§3), unchanged:

| spanwise station z | n inside band / 18 | RMS Δ (m/s) |
|---|---|---|
| 0.0586 | 13 | 0.0512 |
| 0.1836 | 14 | 0.0138 |
| **0.2461** | **18** | **0.00161** |
| 0.3086 | 18 | 0.00946 |
| 0.3320 | 16 | 0.0121 |
| 0.4336 | 9 | 0.0168 |
| **0.4961 (the symmetry plane — what limb B graded)** | **9** | **0.0171** |

At **z ≈ 0.25** the solution reproduces the manual's reference on all three independent
characteristics at once — zero-crossing 0.5498 against 0.5529, extremum −0.2690 against
−0.2687, extremum location 0.1055 against 0.0985 — at **18 of 18 points inside the
band with RMS 0.00161 m/s, an order of magnitude inside the band's own 0.017917.**
At the symmetry plane it is 9 of 18.

**z = 0.25 is exactly half of the manual's half-domain breadth of 0.5 m** — the
geometric mid-plane of the *computational domain*, and the *quarter-span* plane of the
physical cube.

**THIS OBSERVATION IS ANSWER-INFORMED AND IS NOT EVIDENCE.** It was found by scanning
64 spanwise stations against a known answer. Sixty-four tries will find a match. It is
recorded as the *motivation* for a prediction, and it is the prediction — made below,
before the run exists — that carries the evidential weight. Nothing in §0.4 is a
result, and no verdict in this document rests on it.

### 0.5 The one assumption no desk check can close

VMFL078 models the manual's **half** domain with a `symmetryPlane` at mid-span. That
patch **enforces** ∂u/∂z = 0 there. A solution computed with it therefore **cannot
testify that the true solution is symmetric**: the diagnostic in §0.3 measures the
gradient the constraint already imposed. At Re = 1000 the cubic cavity is conventionally
taken to be steady and mirror-symmetric — symmetry breaking is reported well above this
Reynolds number — but *conventionally taken* is not *measured here*, and it is the only
structural assumption in VMFL078 that has never been exercised.

**So R2 removes it.** That is a real experiment with a real falsification, and it
carries the sampling-plane prediction as a second, independently gated limb.

---

## 1. Case identity and manual provenance

| | |
|---|---|
| Case | **VMFL078-R2** (successor to VMFL078; supersedes nothing) |
| Document | Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026 |
| Printed pages | 223–224 (PDF 237–238) |
| Manual's reference | Jifei Wang & Decheng Wan, *Parallel Simulation of 3D Lid-driven Cubic Cavity Flows by Finite Element Method*, Proc. 21st (2011) ISOPE, Maui, June 19–24 2011 |
| Manual's result | **Figure .78.2** only — VM2026R1 prints no scalar for this case |
| Manual's own mesh | polyhedral, 279,894 cells (a **disclosed modelling difference**: this lab runs structured hex; OpenFOAM builds no polyhedra natively) |
| Solver | `simpleFoam`, OpenFOAM v2606, steady laminar SIMPLEC, 4 MPI ranks |

---

## 2. Physics, geometry, boundary conditions — and the single change from VMFL078

**Exactly one thing changes: the symmetry plane is removed and the whole cube is
solved.** Everything else is byte-identical, and the launcher **refuses to start** if
it is not: `case/system/fvSchemes`, `case/system/fvSolution`,
`case/constant/transportProperties` and `case/constant/momentumTransport` are each
hashed against VMFL078's own `HEAD` blob at launch. A second simultaneous change
would confound the experiment, so the launcher makes it impossible.

| | VMFL078 | **VMFL078-R2** |
|---|---|---|
| domain | x,y ∈ [0,1], **z ∈ [0,0.5]** | x,y,z ∈ **[0,1]** |
| z = 0 | no-slip wall | no-slip wall |
| z = 0.5 | **`symmetryPlane`** | **interior** |
| z = 1 | — | **no-slip wall** |
| lid (y=1) | `fixedValue (1 0 0)` | same |
| floor, x-walls | `noSlip` | same |
| p | `zeroGradient` everywhere, `pRefCell 0`, `pRefValue 0` | same |
| ν | 0.001 m²/s ⇒ Re = U·L/ν = 1000 | same |

---

## 3. The grid family — declared a priori, r = 2, isotropic, three levels

| level | n × n × n | cells | Δx = Δy = Δz | cell Re = U·Δx/ν |
|---|---|---|---|---|
| **F1** | 32³ | 32,768 | 1/32 | 31.25 |
| **F2** | 64³ | 262,144 | 1/64 | 15.63 |
| **F3** | 128³ | **2,097,152** | 1/128 | 7.81 |

* Constant refinement ratio **r = 2** in all three directions. Every cell is a cube at
  every level; the family is isotropic in cell shape, as VMFL078's already was.
* **n is divisible by 4 at every level**, so the three sampling planes z = 0.25, 0.50
  and 0.75 fall on **cell faces at every level** — the sampling geometry is identical
  across the triple, which is what keeps the VMFL054 locator pollution out of the order.
* **Three levels, one triple, no selection freedom.**
* `nRanks = 4`, constant across levels: between levels **only the mesh changes**.

---

## 4. The gate readers — the SAME 201 abscissae, on three lines

`case/system/controlDict.template` carries three `probes` function objects, each with
`interpolationScheme cellPoint` and **the 201 frozen abscissae of VMFL078, lifted
verbatim from its committed `controlDict.template`** (y = 0.005 … 0.995, uniform step
0.00495):

| reader | line | role |
|---|---|---|
| `midspanProbe` | x = 0.5, **z = 0.50** | the cube's mid-span — what Figure .78.2's caption names. **Limbs A and B.** |
| `quarterProbe` | x = 0.5, **z = 0.25** | the cube's quarter-span = the mid-plane of the manual's half domain. **Limb C.** |
| `quarter75Probe` | x = 0.5, **z = 0.75** | the mirror of z = 0.25. Read **only** for limb D. **It is not a second chance at agreement: limb C gates on z = 0.25 alone.** |

The window excludes y = 0 and y = 1: they carry *exactly* the imposed boundary values
at every level, and `VERIFICATION_CHARTER §2a` forbids gating on a quantity derivable
by construction from its own inputs.

---

## 5. THE GATES

### 5.1 Limb A — Roache triple. Criteria carried UNCHANGED from VMFL078.

Functional **J = sqrt( (1/(y_hi−y_lo)) ∫ u_x² dy )**, trapezoid over the 201 abscissae
on the **mid-span** line. Roache at **r = 2, Fs = 1.25**.

* **`PASS`** iff the triple is `CONVERGING` **and** observed order **p ∈ [1.0, 3.0]**
  **and** **GCI_fine ≤ 5.0 %**.
* **`GATE FAIL`** if `CONVERGING` but outside either band.
* **`NOT A RESULT`** if any level is not iteratively converged, or the triple is
  `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` (rule 5, fixed order, one-way).

**Provenance:** `p ∈ [1.0, 3.0]`, `GCI ≤ 5.0 %`, `Fs = 1.25` are the class default,
carried unchanged from VMFL054-R3 through VMFL078 §6. **Not one threshold is re-chosen
here.**

### 5.2 Limb B — agreement with Figure .78.2 at the MID-SPAN plane. PRIMARY.

Metric **Δ(y) = u_x^ours(y) − u_x^ref,dig(y)**, in m/s, graded at **F3**.
The 18 sampling locations, u_ref and U95 are **inherited unchanged** from
`cases/ansys_verification/VMFL078/VMFL078_LIMB_B_PREREGISTRATION.md`, freeze commit
**`98ba5a532e30ecee4e6da3a61be8a7dcf2e4a8dc`**, and from its machine copy
`cases/ansys_verification/VMFL078/figure_78_2/limbB_band_table.json`, blob
**`0fbe690025b11d23ca53106cf69385e2961b3e51`**. The launcher refuses to start if that
blob has moved, and the comparator refuses if its own inline literals disagree with it.

| # | probe idx | y (m) | u_ref (m/s) | U95 (m/s) |
|---|---|---|---|---|
| 1 | 9 | 0.04955 | −0.219074 | 0.026956 |
| 2 | 19 | 0.09905 | −0.268669 | 0.015580 |
| 3 | 29 | 0.14855 | −0.247146 | 0.017144 |
| 4 | 39 | 0.19805 | −0.201566 | 0.021337 |
| 5 | 49 | 0.24755 | −0.151656 | 0.020292 |
| 6 | 60 | 0.30200 | −0.105835 | 0.018298 |
| 7 | 70 | 0.35150 | −0.072230 | 0.015797 |
| 8 | 80 | 0.40100 | −0.049907 | 0.015731 |
| 9 | 90 | 0.45050 | −0.031800 | 0.015849 |
| 10 | 100 | 0.50000 | −0.014191 | 0.015675 |
| 11 | 110 | 0.54950 | −0.000797 | 0.015691 |
| 12 | 120 | 0.59900 | +0.017061 | 0.015696 |
| 13 | 130 | 0.64850 | +0.029707 | 0.016547 |
| 14 | 140 | 0.69800 | +0.048313 | 0.015585 |
| 15 | 151 | 0.75245 | +0.070635 | 0.015744 |
| 16 | 161 | 0.80195 | +0.095123 | 0.018303 |
| 17 | 171 | 0.85145 | +0.124209 | 0.015896 |
| 18 | 181 | 0.90095 | +0.163260 | 0.021784 |

* **B1** — RMS₁₈(Δ) ≤ **0.017917** m/s.
* **B2** — at least **16 of 18** points satisfy |Δᵢ| ≤ U95,ᵢ.
* **B3** — over y ∈ [0.05, 0.20]: |u_min^ours − (**−0.2687**)| ≤ **0.0156** m/s **and**
  |y_min^ours − **0.0985**| ≤ **0.0336** m.

**`PASS`** iff B1 ∧ B2 ∧ B3; **`GATE FAIL`** if any fails.
**THE FIGURE IS NOT RE-DIGITISED AND THE BAND IS NOT RE-DERIVED.** Re-digitising now,
with the answer known, would be answer-informed; the existing series and band table are
reused byte-for-byte and the launcher enforces it by hash.

### 5.3 Limb C — the SAME gate at the QUARTER-SPAN plane z = 0.25. The hypothesis test.

**Identical metric, identical 18 abscissae, identical u_ref, identical U95, identical
B1/B2/B3 thresholds.** The only difference from limb B is the spanwise station of the
reader. **No threshold in limb C is chosen for limb C**; every one is limb B's, which
is limb A's predecessor's, which was frozen at `98ba5a53` before any R2 compute existed.

### 5.4 Limb D — symmetry fidelity of the full cube. DEMOTE-ONLY.

Metric: **max over the 18 graded abscissae of |u(z = 0.25) − u(z = 0.75)|** at F3.
**Threshold 0.005 m/s.**

* **`PASS`** — the full cube's own solution is mirror-symmetric about its mid-span, so
  VMFL078's half-domain `symmetryPlane` model was an admissible representation.
* **`GATE FAIL`** — the full cube is **not** mirror-symmetric. Then VMFL078's
  half-domain model was invalid, every VMFL078 number is **`NOT A RESULT`**, and R2
  tests neither hypothesis because the premise of both is gone.

Limb D can only turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the
reverse (rule 5, one-way).

### 5.5 Label vocabulary and the row verdict

Rule 1 vocabulary only: **`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` /
`BLOCKED` / `PENDING`**. No synonyms, no softening adjectives.

* **Row verdict = `NOT A RESULT`** if limb D fails or limb A is `NOT A RESULT`.
* Otherwise **row verdict = limb B's verdict** — the mid-span comparison is the
  manual's own stated figure and is the primary claim.
* Limb C never lifts the row verdict. A limb-C `PASS` beside a limb-B `GATE FAIL` is
  reported as exactly that: a `GATE FAIL` with a named, tested explanation beside it.
* **A `GATE FAIL` is reported as a `GATE FAIL`.** The band is not widened.

---

## 6. Cost (rule 12) — a PREDICTION, not a cap. THERE IS NO CAP.

**Sanaa's directive #17, 2026-09-12, her fourth ruling on this point: no run on any
team is stopped by a time or budget cap.** Nothing in the launcher, the comparator or
the watcher kills a solve for spending. There is no `timeout`. The only ceiling is
`endTime = 40000`, an **iteration** ceiling; a level that reaches it without printing
`SIMPLE solution converged` is `NOT A RESULT` under rule 5 limb 1 and the comparator
refuses it. **Removing the cap does not remove the calibration duty**, which is why
every figure below exists.

**Anchors — MEASURED, from `verification/runs/ansys_verification/VMFL078/RUN_RC.L*`:**

| VMFL078 level | cells | iterations | core-min (measured) | core-min per cell·iteration |
|---|---|---|---|---|
| L1 | 16,384 | 458 | 1.80 | 2.40 × 10⁻⁷ |
| L2 | 131,072 | 939 | 27.67 | 2.25 × 10⁻⁷ |
| L3 | 1,048,576 | 1921 | 916.27 | **4.55 × 10⁻⁷** (box at loadavg ≈ 48 on 16 vCPU; the ≈ 2× is contention, named not absorbed — `COMPUTE_BUDGET_CHARTER §6`) |

**R2 is exactly 2× the cells of VMFL078 at every level** (32³ vs 32×32×16, etc.).
Iteration counts are predicted equal to VMFL078's at the same 1/N, the conditioning
being unchanged.

| R2 level | cells | predicted iterations | rate used | **predicted core-min** |
|---|---|---|---|---|
| F1 | 32,768 | ≈ 460 | 2.40 × 10⁻⁷ | **3.6** |
| F2 | 262,144 | ≈ 940 | 2.25 × 10⁻⁷ | **55.4** |
| F3 | 2,097,152 | ≈ 1930 | 4.55 × 10⁻⁷ | **1,840** |
| | | | **total** | **≈ 1,900 core-minutes** |

* **Plausible range 900 – 2,800 core-minutes.** The low end is F3 at L2's uncontended
  rate (≈ 906 core-min for F3); the high end is a 3× contention factor. The box is at
  loadavg ≈ 48–64 on 16 vCPU at launch and the launch record captures it.
* **Derived dollars: ≈ $1.62** (1,900 core-min = 31.7 core-h at the owner-stated
  c7a.4xlarge rate $0.0513/core-h). **DERIVED, NOT MEASURED** — the box cannot read its
  own billing (`COMPUTE_BUDGET_CHARTER §5`). Well inside the pre-authorised band.
* **Post-run duty:** the estimate-versus-actual row lands in `docs/COST_CALIBRATION.md`
  at completion, stating the ratio actual/predicted and attributing the gap between
  contention, waste and misprediction separately.

---

## 7. THE PREDICTION, AND WHAT FALSIFIES IT — written before the run exists

**Hypothesis H:** our solve of the manual's stated geometry is correct, and the
discrepancy graded `GATE FAIL` at VMFL078 limb B arises because **Figure .78.2 is
sampled at the quarter-span plane of the cube (z = 0.25) — the geometric mid-plane of
the modelled half domain — and not at the mid-span symmetry plane its caption names.**

**Predicted outcome, quantitative, on a run that does not yet exist:**

| limb | plane | prediction |
|---|---|---|
| A | mid-span | `CONVERGING`, p ∈ [1.0, 3.0], GCI_fine ≤ 5 % ⇒ `PASS` |
| **B** | z = 0.50 | **`GATE FAIL`**, n_inside ≈ **9 of 18** (predicted band 7–11), RMS ≈ 0.017 m/s |
| **C** | z = 0.25 | **`PASS`**, n_inside ≥ **16 of 18**, RMS ≤ **0.006 m/s** |
| D | 0.25 vs 0.75 | `PASS`, max asymmetry ≤ 0.005 m/s |

**The four outcomes, enumerated here so that no fifth can be invented afterwards.**
The comparator's `hypothesis_readout()` selects among exactly these and its `--selftest`
drives all four:

1. **Limb B `PASS`.** Removing the symmetry plane moved the mid-span answer into the
   band. **Then the symmetry plane was the defect**, VMFL078's half-domain model was
   wrong, **H is FALSIFIED**, and R2's mid-span result supersedes VMFL078's. Limb C is
   then irrelevant however it lands.
2. **Limb B `GATE FAIL` and limb C `PASS`.** Removing the symmetry plane did *not*
   move the mid-span answer, and the same gate — same band, same points, same
   thresholds — passes at the quarter-span. **H is supported.** The finding is filed
   against the manual's figure, not against our solve. The row verdict is still
   `GATE FAIL`.
3. **Limb B `GATE FAIL` and limb C `GATE FAIL`.** **Both hypotheses are dead.** The
   symmetry plane was not the cause and neither is the sampling plane. The cause is
   elsewhere, **this run does not name it, and no third explanation is to be invented
   after reading the numbers.**
4. **Limb D `GATE FAIL`.** The full cube is not mirror-symmetric at Re = 1000.
   Everything above is void; every VMFL078 number becomes `NOT A RESULT`; and that is
   the finding.

**If the full cube lands the same mid-span offset as the half domain — which is what
prediction B says — then the symmetry plane is EXONERATED and spanwise modelling is
exonerated with it.** That is stated here, in advance, as the outcome this registration
expects, precisely so that it cannot later be presented as a surprise.

---

## 8. Refusal conditions — the comparator refuses (exit 2), it never degrades

1. `grade_vmfl078_r2.py` does not hash to the blob committed with this file.
2. The inherited band table disagrees with the comparator's inline literals, or
   `U_RMS95` is not the RMS of the 18 U95.
3. A frozen probe index does not sit at its registered y, x ≠ 0.5, or z ≠ the
   registered plane (tol 1e−9).
4. A probe file is absent, has no data row, carries ≠ 201 vectors, or holds NaN/Inf.
5. A level's `controlDict` is missing any of the three probe blocks, carries ≠ 201
   locations in one, or has had the `interpolationScheme cellPoint` line deleted.
6. **The mesh or `0/U` of any level carries a symmetry patch** — removing it *is* the
   experiment.
7. Any level fails strict completion (rule 4): no `End` line, no
   `SIMPLE solution converged` line, last log time ≠ latest time directory, `U`/`p`/`phi`
   missing, or a field at the latest time **not newer than that level's own `0/U`**
   (the age guard).
8. **Planted-zero control fails** (rule 3): a 1.234 × 10⁻³ m/s plant written into the
   **real bytes of a copy** of the graded probe file must be seen by the gate reader at
   that index and at exactly that size (**P1a**), must not leak to any other index, must
   **move the gate functional** (**P1b**), and an unmodified copy must leave it unmoved
   (**P1c**). **The graded tree is never written to.**
9. A registered level directory is absent.

**The comparator contains no `assert`** — its own AST guard counts them and refuses if
the count is non-zero — so every control above is live under `python3 -O` as well
(L-332). The launcher runs `--selftest` under **both** interpreters and refuses to
launch unless the PASS count, FAIL count and exit rc agree and every named control was
driven.

---

## 9. Freeze list — the files this commit freezes

| path | role |
|---|---|
| `cases/ansys_verification/VMFL078-R2/VMFL078_R2_PREREGISTRATION.md` | this document |
| `cases/ansys_verification/VMFL078-R2/grade_vmfl078_r2.py` | the comparator; the grading path, fixed at this commit |
| `cases/ansys_verification/VMFL078-R2/run_vmfl078_r2.sh` | the launcher |
| `cases/ansys_verification/VMFL078-R2/case/**` | the case inputs, each hashed against its own HEAD blob at launch |
| `cases/ansys_verification/VMFL078-R2/autograde_watch_vmfl078_r2.sh` | the detached grader. It lives with the case, not in the run root, so that committing the freeze does not create the run root — the claim at the head of this document that the run root does not exist is checkable at this commit. |

**Inherited, unchanged, and hash-enforced at launch:**
`cases/ansys_verification/VMFL078/figure_78_2/limbB_band_table.json`
(blob `0fbe690025b11d23ca53106cf69385e2961b3e51`) and
`cases/ansys_verification/VMFL078/figure_78_2/fig_78_2_digitised.json`.

## 10. What this pre-registration does not claim

* It does **not** claim the manual is wrong. It registers a prediction that, if it
  holds, localises the discrepancy to a sampling plane; outcomes 1, 3 and 4 all say
  something else, and all four are written above.
* It does **not** re-open VMFL078. Those gates are closed and those verdicts stand.
* It does **not** claim a polyhedral-mesh result. This lab runs structured hex; the
  manual demonstrates polyhedra. That disclosed difference is carried forward from
  VMFL078 §3 and is a standing reason a bare `PASS` on limb A says nothing about the
  manual's actual claim.
* **SUBMISSIONS ARE PARKED** (rule 7). Whatever this run finds — including a finding
  about a published figure — goes nowhere outside this box. Sending is Sanaa's
  decision alone.

---

## DATED AMENDMENT — 2026-09-12 — LAUNCHER SYMMETRY-GUARD REPAIR, BEFORE FIRST COMPUTE

**Version 1.0 → 1.1.** *Lines whose number changed above this section: 0.*

**What happened.** The first launch at 06:38:17Z, against freeze
`dd84534ca435c11afe8db7b0272fe517dedac114`, aborted with
`launcher_rc=2` at level F1 on this line of `run_vmfl078_r2.sh`:

```
grep -qi 'symmetry' "$OUT/system/blockMeshDict" "$OUT/0/U" && { echo "ABORT: ..."; exit 2; }
```

**The guard measured something other than what it claimed to measure.** It grepped the
raw files, so it matched the word *symmetry* inside the **explanatory comments** of
`blockMeshDict` and `0/U` — comments that exist precisely *because* removing the
symmetry plane is this case's experiment — and refused a correct case. This is the same
class of defect as the VMFL078 abscissa-count guard, amended there on the same grounds.

**The repair.** The guard now strips `//` comments before testing, so it reads **patch
declarations and nothing else**, and it additionally **proves itself live at every
level** by planting a `type symmetryPlane;` declaration into a scratch file and refusing
if the guard fails to fire on it. Measured at repair time: the repaired guard passes the
real `0/U` and the real `blockMeshDict.template`, and fires on a real
`symmetryPlane` declaration.

**NOTHING ELSE CHANGES.** No gate, threshold, cap, label, band, abscissa, sampling
plane, level count, refinement ratio or predicted outcome is touched. The **registered
refusal condition of §8.6 is unchanged** — *no symmetry patch, anywhere* — and the
comparator's own implementation of it was never defective: `check_bc_provenance()` reads
the patch **types** in `constant/polyMesh/boundary` and the `boundaryField` entries of
`0/U`, never comment prose, and its `--selftest` control
*"BC provenance REFUSES a mesh that still carries a SYMMETRY patch"* passes unchanged.

**THE CONDITION, AND HOW IT WAS CHECKED (rule 2).** This amendment is made **before
first compute**, and that is not asserted, it is measured. At the moment of writing,
under `verification/runs/ansys_verification/VMFL078-R2/`:

| checked | found | required |
|---|---|---|
| `RUN_RC.*` files | **0** | 0 |
| `polyMesh` directories | **0** | 0 — *`blockMesh` never ran*; the guard sits ahead of it |
| `log.simpleFoam` files | **0** | 0 |
| `postProcessing` directories | **0** | 0 |
| numeric time directories under `F1` | **1**, and it is `0/`, holding exactly `U` and `p` — the copied **initial condition**, not an answer | no answer directory |

`LAUNCHER_RC.txt` records `launcher_rc=2`: the launcher refused and stopped. **No
solver process ever started, no field was written, no probe file exists, and no gate has
been evaluated.** The aborted `F1/` tree is **not deleted** — it is moved intact to
`F1_ABORTED_GUARD_FALSE_POSITIVE_2026-09-12T0638Z/` inside the run root so it stays
inspectable, and because the launcher's own age guard (rule 4) must find `F1/` absent
before it will launch into it.

**What this amendment costs the freeze.** The gate-bearing content of the freeze —
§5's four limbs, §3's family, §6's cost prediction and §7's prediction and its four
enumerated outcomes — is byte-identical to commit `dd84534c`, and a reader can verify
that by diffing this file against that blob: the only change is this section, appended.
