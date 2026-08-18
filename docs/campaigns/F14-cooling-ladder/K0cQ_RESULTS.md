# K0cQ. Constitutive anisotropy on both cavities: results

Campaign F14, gate K0c. Experiment **X2** of `K0c_THERMAL_CLOSURE_SYNTHESIS.md`
section 8. Solved 2026-08-18 22:06:27Z to 22:42:56Z; analysed 22:43Z.

Pre-registration `K0cQ_PREREGISTRATION.md`, committed `505bb5ac` at **22:05:16Z**,
**71 seconds before the first graded solve**.

Run tree `verification/runs/F14-cooling-ladder/K0cQ_runs/`, machine record
`gate_k0cq.json`. 6 cases, 6 completion markers, all `rc=0`.

---

## 1. Verdict: SMALL. The anisotropy route is ruled out and the synthesis's central reading survives

| Arm | Geometry | `Nu_hot` baseline | `Nu_hot` QCR | **dNu %** | **dS** | direction |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `Q_sq_c` | square, 14 400 | 54.60523 | 54.49905 | **-0.194** | -0.01239 | away |
| `Q_sq_f` | square, 36 864 | 54.95835 | 54.91277 | **-0.083** | -0.00412 | away |
| `Q_tl_c` | tall hi Ra, 4 800 | 5.66788 | 5.66913 | **+0.022** | +0.00014 | toward |
| `Q_tl_f` | tall hi Ra, 12 288 | 5.69368 | 5.69613 | **+0.043** | +0.00003 | toward |

**Registered SMALL threshold: `abs(dNu) < 1 %` and `abs(dS) < 0.02` on both
geometries.** The largest effect measured was **0.194 %**, five times inside the
threshold. The largest stratification move was **0.0124**, inside it.

**Registered LARGE threshold — the falsifier — was `abs(dNu)` at or above 10 %
(square) or 5.41 % (tall). The measurements fall short of it by a factor of 50
to 250.**

Per the rule fixed before compute: *the cavities sit with the hump and the
hills, not with the ducts; Pope's target is not made live by this measurement;
and the synthesis's group-C reading is not falsified.*

**Direction is registered separately and decides nothing** (`K0cQ_PREREGISTRATION.md`
§4.1). The square arms moved away from the experiment and the tall arms toward
it, at sizes where neither is meaningful.

---

## 2. Both controls returned exact machine zero, on two geometries and a solver the precedent did not cover

| Control | Against | Cells | `max abs dU` |
| --- | --- | ---: | ---: |
| `Z_sq_c` | `S_SST_c` stock `kOmegaSST` | 14 400 | **0.0 exactly** |
| `Z_tl_c` | `X_hi_c_SST` stock `kOmegaSST` | 4 800 | **0.0 exactly** |

The registered requirement (§4.2) was exactly 0.0, on the precedent of
`W3_QCR_DUCT_FALSIFIER.md`, which achieved it on the ducts under `simpleFoam`.

**This reproduces that result on a different solver and two different
geometries.** `buoyantBoussinesqSimpleFoam` with the QCR library loaded, the
`div(qcrStress)` scheme added and `Ccr1 = 0` is **bit-for-bit identical** to
stock `kOmegaSST`. So the library contributes nothing except the QCR term, and
**the one setup change this rung had to make — the added divergence scheme — is
proved inert**, which is what §2.1 registered it to prove.

Every difference in Section 1 is therefore attributable to the QCR term and to
nothing else.

---

## 3. The result's force comes from the contrast with the same instrument on the ducts

This is a null, and a null is only as strong as the instrument's demonstrated
ability to produce a non-null. **The same library, the same `Ccr1 = 0.3`, the
same bit-for-bit control:**

| Flow | Quantity | Linear `kOmegaSST` | `kOmegaSSTQCR` | Reference |
| --- | --- | ---: | ---: | ---: |
| Duct `AR_3_Ret_180` | in-plane secondary flow, % of Ubar | **5.5e-16** | **0.705** | 0.813 |
| Duct `AR_5_Ret_180` | in-plane secondary flow, % of Ubar | **8.3e-16** | **0.676** | 0.749 |
| **Square cavity** | hot-wall Nusselt | 54.61 | 54.50 | 63.45 |
| **Tall cavity** | hot-wall Nusselt | 5.694 | 5.696 | 7.57 |

**On the ducts the term creates a flow feature the linear model expresses at
machine zero, reaching 79-93 % of the reference. On the cavities it moves the
graded integrals by under a fifth of a percent.**

That contrast is the result. It is not that QCR is a weak correction; it is that
**this correction is decisive on the flow whose failure is structural and
inconsequential on the flows whose failure is a mis-scaling.** Rejection **R3**
of the synthesis — *the buoyant failure is the square-duct anisotropy failure in
another guise* — was previously *"rejected for want of evidence in both
directions"*. **It now has evidence, and it is rejected on it.**

---

## 4. The term is not inert on the cavities; the graded integrals are insensitive to it

Reported, never gated. The registered rule names only Nusselt and
stratification, and nothing below decides anything.

| Arm | `nu_t/nu` domain max | change | Reynolds shear stress | change |
| --- | --- | ---: | --- | ---: |
| `Q_sq_c` | 12.074 -> 10.801 | **-10.54 %** | 4.4794e-4 -> 4.4748e-4 | -0.102 % |
| `Q_sq_f` | 6.088 -> 6.336 | **+4.08 %** | 4.7145e-4 -> 4.7067e-4 | -0.165 % |
| `Q_tl_c` | 21.863 -> 21.887 | +0.11 % | 2.6258e-3 -> 2.6262e-3 | +0.014 % |
| `Q_tl_f` | 21.762 -> 21.787 | +0.12 % | 2.6617e-3 -> 2.6624e-3 | +0.024 % |

**QCR perturbs the square cavity's peak eddy viscosity by 4 to 11 percent and
still moves its wall heat flux by 0.19 percent.** So the term is acting, and the
graded quantities do not respond to it.

**The sign of that perturbation flips between the two square meshes**, -10.5 %
coarse and +4.1 % fine. `nu_t/nu` domain maximum is a **single-cell** quantity,
so it is the noisiest measure in this table and a sign flip between meshes is
not evidence of a mesh-dependent mechanism. It is reported as measured and no
reading is placed on it.

**The Reynolds shear stress — the quantity a constitutive anisotropy correction
acts on most directly — moved by at most 0.165 percent on either geometry.**
That is the sharpest form of the null and it is the reason Section 3's reading
is about the cavity rather than about QCR.

---

## 5. What this rung does NOT establish, stated as narrowly as its pre-registration required

- **It does not prove the Reynolds stress tensor is isotropic on either
  cavity.** Neither cavity has a measured anisotropy tensor in this lab's
  library. Ampofo p. 3559 measured the isotropy assumption to be **false** on
  the square cavity, and nothing here contradicts that. What is ruled out is
  that **this** constitutive correction, of the family a two-equation model can
  carry, changes the graded integrals.
- **A null from QCR2000 is a null from QCR2000.** It is one closure of a family.
  A full Reynolds-stress transport model is a different instrument and is
  **X3**, which this result now makes worth scheduling: X2 was registered as the
  experiment that must report before X3 is scheduled, and it has.
- **It grades nothing against experiment.** Every number is a difference from a
  baseline twin. `K0cS` and `K0cX` keep their verdicts untouched.
- **It says nothing about the heat flux closure**, which is the other half of
  the synthesis's central split. Section 4's Reynolds-stress null bears on the
  stress side only.
- **The tall coarse pair inherits a defect**, disclosed in the
  pre-registration §5: the baseline `X_hi_c_SST` missed its convergence
  criterion (`K0cX_RESULTS.md` §7). The tall cavity's primary comparison is the
  **fine** mesh, `Q_tl_f`, whose baseline converged, and which returned the same
  answer at +0.043 %.

---

## 6. Provenance of the analysis, since this rung's finding is a null

A null is the result most easily produced by an instrument that is not looking
properly, so the chain is stated rather than assumed.

- **Pre-registration committed 71 seconds before the first graded solve**, with
  the decision rule, both thresholds and the control requirement fixed in it.
- **The comparator was committed at 22:10:06Z with ZERO completion markers on
  disk**, while all six cases were mid-solve, and it was **verified
  byte-identical at analysis time to that committed version** (sha256 prefix
  `94eddde98f0f61cf` on both sides). `K0cX_RESULTS.md` §11 had to disclose a
  comparator extended after solving began; **that disclosure is not owed here.**
- **Each QCR arm was measured by its own geometry's instrument** — the same
  `measure()` function that produced its baseline — so a difference is not an
  artefact of two instruments.
- **No baseline case directory was written to.** Baseline values were read from
  the committed `gate_k0cs.json` and `gate_k0cx.json` rather than re-measured,
  because both `measure()` functions run a `postProcess` call that writes into
  the case it is pointed at.
- **Both controls returned exact zero**, which is the strongest available
  evidence that the instrument was connected to the case at all.

**Falsifier for this record:** exhibit a QCR arm, built by
`K0cQ_runs/build_cases.sh` from these baselines, whose hot-wall Nusselt differs
from its twin by 1 % or more.

---

## 7. Cost

| Case | exec s | baseline s | ratio |
| --- | ---: | ---: | ---: |
| `Q_sq_c` | 648.25 | 696.76 | 0.930 |
| `Q_sq_f` | 2188.78 | 2170.42 | 1.008 |
| `Q_tl_c` | 454.07 | 384.98 | 1.179 |
| `Q_tl_f` | 849.51 | 923.17 | 0.920 |
| `Z_sq_c` | 660.86 | 696.76 | 0.948 |
| `Z_tl_c` | 474.35 | 384.98 | 1.232 |
| **Total** | **5275.8 s** | | |

**87.9 core-minutes = 1.466 core-hours = $0.075**, against a pre-registered
estimate of $0.094 and the synthesis's $0.087. Wall clock 36.5 minutes.

**The pre-registration's x1.25 QCR overhead factor is NOT confirmed and the
measurement cannot confirm it.** Measured ratios ran 0.920 to 1.232, including
two arms that ran *faster* than their baselines. These six cases ran six-way
concurrent on 16 vCPU while the baselines ran under different and unrecorded
concurrency, so the ratio measures machine load as much as it measures the QCR
term. **No overhead figure is claimed from it.**
