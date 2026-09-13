# DRIVAER — PARKING RECORD

**Status: PARKED, 2026-09-13.** Written by a cfd `lab-lane` on the cfd-supervisor's
instruction, after grading `r2c_medium_blended_R3` against the frozen registration
`verification/campaign/DRIVAER_R2C_MEDIUM_CONTINUATION_PREREGISTRATION.md` (v1.2: frozen
`9d1bcd902`, amendment 1 `d7fa960a0`, amendment 2 `94aeb5f96`).

**Parked under Sanaa's rule** — *"we can keep the level up to medium if the results are
good."* **They are not good, and this record says so in the measured units rather than in
adjectives.** Parked is not cancelled; nothing here is withdrawn and no artifact is deleted.

**This is an honest outcome, not a defeat.** Three runs graded on a pinned instrument, a
falsifier that fired exactly as designed and was written before the run that fired it, and a
mesh defect measured on nine arms rather than assumed on one.

---

## 1. THE VERDICT

**`Gate A1` — `GATE FAIL`.** Artifact:
`verification/runs/navier_class/DRIVAER/r2c_medium_blended_R3/GRADE_STAGE_A_medium.json`.

Graded with `cases/navier_class/DRIVAER/grade_drivaer.py`, sha256
`6106cf6db9ac7dd7d767e140de7ba2e389829d02c30f5d251fcec0c6b83c26d7`, **verified byte-identical
to the HEAD blob in the same shell invocation as the run**, on the §4 invocation exactly as
pinned. Grader exit 0.

**All three planted controls report `passed: true`** — the `p`-field reader (planted 5.0,
reader_delta 7.7405372e-05 against expected 7.7405372e-05, and planted a second time at a
multiplicity-2 cell per the 2d.1 repair, both arms passing), the Cd reader (planted 0.05,
delta 0.05) and the Cl reader (planted 0.05, delta 0.05). **Without all three this would be
NOT A RESULT**; they are the reason it is a verdict.

| gate | verdict | value |
|---|---|---|
| A1 completion and instrument | **GATE FAIL** | iterative state `NOT_CONVERGED`; Cd not plateaued; Cl not plateaued |
| A2 Cd gross-error diagnostic band | PASS | Cd 0.31496232237 in [0.15, 0.6] |
| A3 Cl gross-error diagnostic band | PASS | Cl 0.023291750055 in [-0.5, 0.5] |

Rule-4 completion held on every clause: `rc`=0, an `End` line, last time 10000 == `endTime`,
field set present, `ExecutionTime` count 10000 == `round(endTime/deltaT)`, age guard satisfied.
**The run is complete. It is the answer that fails, not the run.**

### 1.1 THE AMENDMENT-2 DISCLOSURE, WHICH IS NOT OPTIONAL AND IS STATED BESIDE THE RESIDUAL VERDICT

**`bounding k` fired on 9,999 of 10,000 iterations — 0.9999 per iteration.** `bounding omega`
fired 224 times (0.0224 per iteration). Per-1000-iteration blocks for `k`: **1000, 1000, 1000,
1000, 1000, 1000, 1000, 1000, 999, 1000** — **flat to the final iteration, and the last
clipping of `k` is at iteration 10000, the run's last.** This is not a decaying startup
transient and 8,000 extra iterations did not touch it.

**The control is the already-graded `r2c_medium_blended_R2`: `bounding k` on 2,000 of 2,000
iterations, 1.000 per iteration.** R3 at 0.9999 is statistically identical. **R3 did not cause
this; it is a property of this case, present throughout the run this lab has already graded.**

Per amendment 2 §A2.3, **no gate is added on the bounding rate and the R2 verdict stands
unchanged** — retro-fitting a gate would be grading after the fact. What R2's verdict lacked
was this disclosure, not a different result. **A residual verdict quoted without this rate is
an incomplete reading of this run:** the turbulence field was clipped from below on essentially
every solve for 10,000 iterations, so "the residuals descended" and "the field is healthy" are
two different claims and only the first is supported.

---

## 2. 🔴 THE REGISTERED FALSIFIER FIRED AND **BOTH** LIMBS FAILED

**§5 predicted the residual limb would clear and the Cd plateau limb would not. Neither
cleared.** The falsifier is read here against the document, not against expectation.

### 2.1 The residual limb — predicted to clear, did not

Every equation is outside `res_tol` 1e-4 at iteration 10000:

| equation | at 10000 | vs tol 1e-4 |
|---|---|---|
| Uy | **4.552e-03** | 45.5× |
| p | 1.771e-03 | 17.7× |
| Uz | 9.998e-04 | 10.0× |
| k | 1.943e-04 | 1.94× |
| Ux | 1.402e-04 | 1.40× |
| omega | 1.100e-04 | 1.10× |

### 2.2 The Cd plateau limb — predicted not to clear, did not clear

Trailing-200 excursion_rel at 10000 = **0.027553 against tol 0.005 — 5.51×.** On the grader's
own registered window (1,000 samples, 10 % of `endTime`) it is **0.062256 — 12.45×**.

**Note the window scales with `endTime`, so R2's graded 0.009578 and R3's 0.062256 are not
comparable.** Compared like with like on trailing-200: **R2 0.009578 (1.92× tol) → R3 0.027553
(5.51× tol). It got worse, by 2.9×.** That is not a regression in the physics; it is §0's point
arriving on schedule — R2's stopping point ranked **1 of 33** windows, the single lowest
excursion in its run, and R3's stopping point ranks **105 of 193**, the median. **The graded R2
number was flattered by where it stopped. The excursion never decayed at all.**

§5's clause therefore applies as written: **the plateau criterion is UNSATISFIABLE under a
steady SIMPLE treatment of this case, and that is a FINDING TO REPORT, NOT A FAIL TO RECORD.**
Supporting evidence, measured on R3: the Cd signal reverses direction on **9.8 %** of steps over
the last 400 samples (monotone approach ≈ 0 %, white noise ≈ 67 %) — a slowly wandering signal,
not a converging one, on a notchback with a separated wake. R2 measured 14.3 % at its own end.

---

## 3. THE CALIBRATION FINDING — HOW FAR THE §2 EXTRAPOLATION MISSED, AND WHY

**This is worth more than the verdict, and it is the reason this record exists.**

§2 derived `endTime` 10000 from a log-linear fit of ln(residual) against iteration over
iterations 1000→2000, with **Uy binding at 8,394**. Measured against what the run actually did:

| equation | §2 predicted @10000 | **ACTUAL @10000** | **miss factor** |
|---|---|---|---|
| Ux | 9.117e-07 | 1.402e-04 | **153.8×** |
| Uy *(the binding equation)* | 4.477e-05 | 4.552e-03 | **101.7×** |
| Uz | 9.988e-06 | 9.998e-04 | **100.1×** |
| p | 5.174e-05 | 1.771e-03 | **34.2×** |
| k | 2.166e-05 | 1.943e-04 | **9.0×** |
| omega | 8.962e-05 | 1.100e-04 | **1.2×** |

**Uy was predicted to cross 1e-4 at iteration 8,394. At 10,000 it is at 4.552e-03 — 45.5× the
tolerance, and 101.7× its own predicted value.**

### 3.1 The extrapolation did not merely undershoot — **the decay it extrapolated does not exist outside the window it was fitted on**

Median initial residual per 1,000-iteration block (median, so a single blip cannot set it):

| block | Uy | p | Uz | k | Ux | omega |
|---|---|---|---|---|---|---|
| 1–1000 | 5.831e-03 | 2.326e-03 | 1.266e-03 | 2.072e-04 | 1.796e-04 | 1.181e-04 |
| **1001–2000** | **2.362e-03** | **1.033e-03** | **5.197e-04** | **1.329e-04** | **7.082e-05** | 1.137e-04 |
| 2001–3000 | 2.960e-03 | 1.329e-03 | 6.386e-04 | 1.445e-04 | 8.740e-05 | 1.133e-04 |
| 3001–4000 | 3.807e-03 | 1.582e-03 | 8.173e-04 | 1.689e-04 | 1.170e-04 | 1.154e-04 |
| 4001–5000 | 4.542e-03 | 1.818e-03 | 9.467e-04 | 1.855e-04 | 1.364e-04 | 1.152e-04 |
| 5001–6000 | 4.223e-03 | 1.803e-03 | 9.141e-04 | 1.766e-04 | 1.291e-04 | 1.154e-04 |
| 6001–7000 | 2.546e-03 | 1.120e-03 | 5.578e-04 | 1.374e-04 | 7.648e-05 | 1.146e-04 |
| 7001–8000 | 6.109e-03 | 2.041e-03 | 1.203e-03 | 2.235e-04 | 1.853e-04 | 1.159e-04 |
| 8001–9000 | 2.620e-03 | 1.142e-03 | 5.818e-04 | 1.406e-04 | 7.929e-05 | 1.146e-04 |
| 9001–10000 | 4.336e-03 | 1.724e-03 | 9.287e-04 | 1.783e-04 | 1.320e-04 | 1.150e-04 |

**For five of the six equations the best block in the entire run is 1001–2000 — the exact window
§2 fitted — and no later block ever beats it.** Regression from best block to final block: Uy
1.84×, Ux 1.86×, Uz 1.79×, p 1.67×, k 1.34×, omega 1.02×. Fitting R3's **own** last 1,000
iterations gives a **positive** slope on every equation, so **no equation projects to 1e-4 at
all.**

**§2 fitted the tail of the startup transient and extrapolated it 3.2× beyond its window. The
residuals do not decay; they wander in a band** — Uy between roughly 2.4e-03 and 6.1e-03 with
no trend.

### 3.2 🔴 THE SAME DOCUMENT DIAGNOSED THIS FAILURE MODE ON ONE LIMB AND THEN COMMITTED IT ON THE OTHER

**§0 is the most careful section of the registration.** It refused to derive `endTime` from the
Cd excursion precisely because the log-linear fit's 95 % CI **contained zero** (slope −1.432e-04
/it, se 1.127e-04, t = −1.270), and it explicitly registered the tempting four-window fit and its
answer of 2671 as **REFUSED** because it was set by one outlier.

**Then §2 performed a log-linear fit on the residual trajectory and reported no standard error,
no t-statistic and no confidence interval at all** — and that fit is the one that produced the
number the run was bought with. §0's stated ground for trusting it was that the residual
trajectory *"does decay, monotonically and measurably."* **Over the fitted window it did. Over
the next 8,000 iterations it did not.** The residual limb failed the same test §0 applied to the
Cd limb, and nobody applied it.

**The transferable lesson is not "the fit was wrong."** It is that **§0's own scepticism was
applied to one limb and not carried to the other in the same document**, and that the limb which
escaped scrutiny is the one that set the cost. A refusal registered against one statistic is not
a habit until it is applied to every statistic in the document — including, and especially, the
one that gives an answer you can act on.

---

## 4. THE THREE FROZEN CONCLUSIONS — RESTATED, NOT SOFTENED

These are §3 of the registration. They are unchanged by anything R3 measured.

1. **THE MESH IS NON-CONFORMING AND NO NUMBER FROM THIS FAMILY IS A CREDENTIAL.**
   `log.checkMeshFull` measures **max skewness 5.450006 on 2 faces against
   `docs/standards/MESH_STANDARD.md`'s hard gate of 4.0 — exceedance factor 1.3625** (max
   non-orthogonality 64.914456; three failed full-flag checks). The grader emits
   `credential_eligible: false` and a CLAIM CAP. **Matrix status: STATED LIMITATION — never
   HOLDS, never GATE REACHED, never a credential.** Running longer fixes Gate A1 and **cannot**
   fix the mesh; R3 is the proof, having run 5× longer and moved the mesh not at all.

2. **AN IN-BAND Cd IS NOT AGREEMENT WITH DrivAerML.** Gate A2's band [0.15, 0.6] is a
   **gross-error diagnostic, not a validation gate**. `Cd_ref = 0.2758368` is **NOT GATED
   AGAINST**. R3's Cd 0.31496 sits 14.2 % above that reference; **that comparison is recorded
   here as context and is not a result.** A reader who cites the A2 PASS as agreement with
   DrivAerML has misread both the grader's own `interpretation` field and this record.

3. **NO ROACHE TRIPLE, NO OBSERVED ORDER, NO GCI.** The family is **two-level** and Gate G is
   **deliberately unregistered**, because y⁺ varies ~2.5× across the levels without wall layers,
   so an order taken off it would measure the wall model changing rather than the grid. **No GCI
   may be quoted for DrivAer from any artifact in this family.**

---

## 5. TWO DEFECTS FOUND WHILE GRADING, NEITHER OF WHICH CHANGES THE VERDICT

Recorded because they are true, not because they help.

### 5.1 THE FAMILY'S PUBLISHED CELL COUNTS ARE FACE COUNTS — EVERY RECORD OF THIS FAMILY IS 3.1× TOO LARGE

§3 states the family is two-level at **"592,877 / 3,060,269"** and the grade JSON carries
`nCells: 3060269`. **Those are face counts.** The `constant/polyMesh/owner` headers read:

- `r2_coarse`: `nPoints:221464  nCells:186709  nFaces:592877`
- `r2_medium`: `nPoints:1100653  nCells:983106  nFaces:3060269`

and `log.checkMeshFull` agrees (`cells: 983106`, `faces: 3060269`). **The true cell counts are
186,709 and 983,106.** The grader's `nCells` field is mislabelled and the registration inherited
it.

**Why it does not change the verdict:** no gate in this registration is a function of cell count,
and Gate G is unregistered, so nothing turns on it. The refinement ratio is barely affected —
**1.740 by cells vs 1.728 by faces, 0.7 %.** **Why it must be fixed anyway:** the medium level has
been described everywhere as a 3-million-cell mesh and it is a **983-thousand-cell** mesh. Any
future reader sizing a successor run, or comparing this family to DrivAerML's published meshes,
would be wrong by 3.1×.

### 5.2 THE GRADER REFUSED FIRST ON A STAGING OMISSION, AND THE REFUSAL WAS CORRECT

The first graded invocation exited 2: *"no `log.checkMeshFull`. An unmeasured mesh is not a
conforming one."* **That refusal is correct behaviour and was not worked around.** `_R3` was
staged with `constant/polyMesh` symlinked to `r2_medium/constant/polyMesh` but without the
mesh-quality artifact that the already-graded `r2c_medium_blended_R2` carries as a symlink to
`r2_medium/log.checkMeshFull`.

**Before replicating that symlink I verified the artifact describes the mesh that actually ran**,
rather than assuming it: `_R3`'s `polyMesh` symlink resolves to the identical target as `_R2`'s,
and the `owner` header (`nPoints:1100653 nCells:983106 nFaces:3060269`) matches the
`log.checkMeshFull` header field-for-field. **The skewness 5.450006 is read off the mesh that
solved.** The staging template for this family should carry the symlink so the next case does not
depend on a lane noticing.

---

## 6. THE FULL ACTION HISTORY

### 6.1 Three graded runs

| run | endTime | Gate A1 | Cd | trailing-200 excursion | `bounding k` rate |
|---|---|---|---|---|---|
| `r2c_coarse_blended_R2` | 2000 | GATE FAIL | — | — | — |
| `r2c_medium_blended_R2` | 2000 | GATE FAIL | 0.31507317629 | 0.009578 (1.92× tol) | 1.000/it |
| **`r2c_medium_blended_R3`** | **10000** | **GATE FAIL** | **0.31496232237** | **0.027553 (5.51× tol)** | **0.9999/it** |

**Cd moved by 0.00011 — 0.035 % — across a 5× increase in iterations.** The force coefficient is
not what longer running was ever going to change.

### 6.2 The five-arm wall-layer ladder, and four diagnostic arms before it — **max skewness measured on every one**

| arm | max skewness | vs gate 4.0 |
|---|---|---|
| `DIAG_v1_coarse_explicitSnap_tol2_noCarLayers` | 84,202.365 | catastrophic |
| `DIAG_v2_coarse_implicitSnap_tol1_layersON_BROKEN` | 25,103.247 | catastrophic |
| `DIAG_v3_coarse_explicitSnap_tol2_layersFixed` | 84,202.365 | catastrophic |
| `DIAG_v5_coarse_layersON_mergeTol1e-8` | 1,627,951.5 | catastrophic |
| `LAYERFIX_A1_coarse_relativeSizes` | **4.7820293** | FAIL |
| `LAYERFIX_B1_coarse_medialRatio` | 4.8491528 | FAIL |
| `LAYERFIX_B2_coarse_medialAxisAngle` | 4.8750343 | FAIL |
| `LAYERFIX_C1_coarse_absoluteFirstLayer` | **4.7820293** | FAIL |
| `LAYERFIX_C2_coarse_absoluteFirstLayer_5mm` | **4.7820293** | FAIL |
| `r2_coarse` (the level that shipped) | 4.7820293 | FAIL |
| `r2_medium` (the level graded) | 5.450006 | FAIL |

**Nine arms. Not one reached 4.0. The best is 4.782 — 1.20× the gate.**

**And the sharpest result in the table: `LAYERFIX_A1`, `C1`, `C2` and `r2_coarse` produce
`4.7820293` — bit-identical to eight significant figures — across a relative first-layer spec, an
absolute spec, and a 5 mm absolute spec.** Three genuinely different layer specifications move the
skewness-limiting faces **not at all**. **Those faces are therefore not in the layer region.** They
are a snapping/geometry artifact on the notchback surface, which is precisely why a layer dial
cannot reach them — and why more iterations of the same ladder were never going to.

The `h_surf` diagnostic (`verification/runs/navier_class/DRIVAER/H_SURF_DIAGNOSTIC_2026-09-12.md`)
independently found the layer machinery **over-delivers** what it is asked for — relative spec by
1.2315×, absolute spec by 1.6758× — so the ladder's dials were not even controlling the quantity
they were assumed to control.

### 6.3 Structural findings already filed from this campaign

- **Rule 4 has a resume-shaped hole** (amendment 1 §A1.4): the unit-step `ExecutionTime` clause
  makes any resume ungradeable by a comparator implementing it literally, and this lab's
  comparators **disagree** — form A (`n_exec == endTime`, used by `grade_drivaer.py:242`,
  `analyse_m6i.py:234`, `analyse_m6sr.py:1810`) **refuses** a resume; form B
  (`n_exec == n_time`, used by `rc3_ceiling.py:1018`, `rc4_score.py:239`) **accepts** it. Not a
  comparator bug — a rule question, unruled. Draft at
  `verification/runs/navier_class/DRIVAER/DOCKET_D631_DRAFT_rule4_resume_hole.md`.
- **A dead pid in a handoff record reads identically to a dead run** (amendment 2 §A2.5).

---

## 7. COST CALIBRATION — STANDING RULE 12

| | core-min | derived $ | wall |
|---|---|---|---|
| **Predicted (amended §6, the live figure)** | **1,781** | $1.52 | 7.42 h |
| ~~Predicted (§6 original, STRUCK PRE-COMPUTE)~~ | ~~1,425~~ | ~~$1.22~~ | ~~5.94 h~~ |
| **ACTUAL (MEASURED, `RUN_META.txt`)** | **1,286.5** | **$1.10** | **5.36 h** |
| **ratio actual/predicted** | **0.722** | | |

**Attribution of the gap: rate misprediction, not waste and not contention.** The basis rate was
2.672 s/iteration measured on `r2c_medium_blended_R2`; R3 ran at **1.930 s/iteration**
(19,297 s wall ÷ 10,000 iterations at 4 ranks), a ratio of **0.722** — **identical to the
core-minute ratio**, so the entire difference is the per-iteration rate and **no waste is
absorbed into it.** §6 predicted this direction explicitly (*"if the box is quieter the actual
will come in under"*) and was right; **it is the one prediction in this registration that held.**
Solver-only `ExecutionTime` was 19,247.15 s, so 49.85 s of the wall is `decomposePar` +
`reconstructPar`.

**Dollars are DERIVED, NOT MEASURED**, at the owner-stated $0.0513/core-h; the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER` §5). **No cap applied** — Sanaa's directive #17,
2026-09-12. A row is owed to `docs/COST_CALIBRATION.md` recording the actual against **1,781**
and noting that **1,425 was struck pre-compute** by amendment 1 and why; both figures must stay
visible.

---

## 8. WHAT A SUCCESSOR WOULD TRY FIRST, AND WHY

**§5 of the frozen registration already answers this, and it forbids the obvious move:**

> *"If the falsifier fires, the successor is an unsteady treatment, **not a larger endTime**, and
> this document forbids simply registering a bigger number a third time."*

**That clause is binding and R3 is the evidence that earns it.** 8,000 extra iterations moved Cd
by 0.035 %, moved the trailing-200 excursion the **wrong way** by 2.9×, left every residual
outside tolerance with a **positive** terminal slope, and left `bounding k` firing on the final
iteration. **A third, larger `endTime` is registered here as REFUSED.**

In priority order, a successor should:

1. **An unsteady treatment — URANS or DDES — because the plateau criterion is unsatisfiable, not
   unmet.** The measured evidence is that the Cd signal wanders rather than converges (9.8 %
   sign-reversal rate over the last 400 samples; the excursion ranks at the **median** of its own
   distribution after 10,000 iterations). A notchback's separated wake is not steady, so a steady
   SIMPLE solve has no fixed point to find and a time-averaged Cd from an unsteady run is the
   physically correct quantity — **not the last sample of a wandering steady solve.** This is the
   registration's own named successor.

2. **Fix the mesh at the snapping stage, not the layer stage, and gate on it before any solve.**
   §6.2's bit-identical `4.7820293` across three different layer specs is the measurement that
   says where the defect is: **the skew-limiting faces are outside the layer region**, so
   `snappyHexMesh` feature capture / surface refinement on the notchback surface is the dial to
   turn, and the wall-layer ladder is exhausted. **Until max skewness is under 4.0 no DrivAer
   number can be a credential however well it converges** — so this is a precondition for the
   campaign mattering, not an improvement to it.

3. **Explain `bounding k`, or register it as accepted, before trusting any DrivAer turbulence
   field.** Clipping `k` from below on ~100 % of iterations across **both** graded runs, flat to
   the last iteration, is an unexplained property of this case. Candidates worth measuring: the
   wall-function state at y⁺ ≈ 585–2342 without layers; the inlet/initial `k`–`omega` pair; the
   `blended`/limited scheme set. **It is not a known-benign behaviour and it has never been
   diagnosed** — amendment 2 deliberately declined to gate on it to avoid grading after the fact,
   which leaves the diagnosis owed.

4. **Correct the cell-count mislabelling (§5.1) and the staging template (§5.2)** before the next
   registration quotes 3,060,269 cells again.

**A successor should not:** register a larger `endTime`; add a gate on the bounding rate
retroactively; cite the A2 PASS as agreement with DrivAerML; or quote a GCI or observed order
from this two-level family.

---

## 9. WHAT IS PARKED, AND WHAT REMAINS TRUE

**Parked:** further compute on the DrivAer Stage A steady ladder at any level.

**Not withdrawn:** the three graded `GATE FAIL` verdicts, which are correct and stand; the mesh
non-conformance measurement on nine arms; the rule-4 resume finding; the `h_surf` over-delivery
measurement; amendment 2's disclosure requirement; and every artifact cited above, which remains
on disk.

**Not claimed, at any point, by anything in this campaign:** a credential, a validated Cd, an
observed order, a GCI, or agreement with DrivAerML.

**The campaign did what a verification campaign is for.** It registered a falsifier before the
run, the falsifier fired, both limbs failed, and the reason is now measured rather than guessed:
a steady solver was asked to find a fixed point that a separated wake does not have, on a mesh
whose defect is in the snapping and not in the layers. **That is a finding. It is not a result,
and this record does not dress it as one.**

---

*Drafted by a cfd `lab-lane`, 2026-09-13. Not committed by its author. Contains no submission,
no external communication and no claim outside this box.*
