# MRF R2 ET8000 — PRE-STATEMENT ON THE TRIPLE, FROZEN **BEFORE FINE LANDS**

**This alters no gate, threshold, cap, band or label of `MRF_R2_PREREGISTRATION.md`.** It
is a **prediction**, written down at a moment when it can still turn out wrong, about
whether the Roache triple will mean anything when it is computable. Fine is at
~4,400 of 8,000 at the time of this commit; its `rc` sidecar does not exist.

Asked for by the cfd-supervisor, 2026-09-11: *state, before fine lands, whether the
level-to-level differences in `Np` are expected to EXCEED the noise in the graded
statistic.*

---

## 1. THE MEASUREMENT, FROM THE TWO LEVELS THAT HAVE LANDED

Quantity: **power number `Np`, derived from `total_z`** — the **third column** of
`moment.dat`, resolved **by name from the header**. Column −1 is `viscous_z` and yields
plausible wrong numbers. All values via `measure_states_mrf.{read_total_axial,
power_number, s12}` **imported as functions**; `main()` is **never called** — it is
hardcoded to R1 at `:152` and would silently grade the wrong campaign.

| level | `Np` at endTime 8000 | `Np` on the S12 window mean | window-mean sd over 41 stopping points | window-mean range |
|---|---:|---:|---:|---:|
| coarse | 4.193491 | **4.228316** | 1.455882e-03 | **5.187192e-03** |
| medium | 4.281132 | **4.231680** | 6.588451e-04 | **2.591881e-03** |

**The level-to-level difference, which is the quantity a Roache triple differences:**

| estimator | \|Np(medium) − Np(coarse)\| | worst within-level range | **signal / noise** |
|---|---:|---:|---:|
| **S12 window mean** (the settled estimate) | **3.364298e-03** | 5.187192e-03 | **0.649** |
| raw value at endTime (one instantaneous sample) | 8.764152e-02 | 5.187192e-03 | 16.896 |

## 2. THE PREDICTION, STATED PLAINLY SO IT CAN BE FALSIFIED

**On the settled estimator the coarse→medium signal is ALREADY BELOW the within-level
noise floor — 0.649× it.** Two levels do not make a triple, and fine may sit far from
both. But **I expect the R2 triple to be arithmetically computable and physically
meaningless**, in exactly the sense that has already outlived two rungs here: three
numbers that a Roache calculation will happily accept and difference, whose differences
are smaller than the variation each number shows across its own nearby stopping points.

**What would falsify this prediction:** fine's settled `Np` landing far enough from
medium's that the coarse→medium→fine differences are monotone AND both gaps exceed
~5.2e-03. That is the outcome I am predicting against.

## 3. THE TRAP THE RAW-ENDPOINT COLUMN SETS, AND WHY IT MUST NOT BE USED ALONE

The raw-endpoint estimator shows signal/noise **16.9** and looks entirely healthy. **It is
an artifact of differencing two instantaneous samples of an oscillating quantity.** The
proof is on coarse's own series: `Np(8000)` = 4.193491 against a window mean of 4.228316,
a gap of **3.48e-02** — **ten times the 3.36e-03 difference between the two levels'
settled means.** **Each level's endpoint carries a wobble an order of magnitude larger
than the signal the triple is trying to resolve**, so the apparent 16.9 is mostly that
wobble, not mesh convergence.

**A triple computed on raw endpoint values may therefore report a clean order of
convergence that is an artifact of where three oscillations happened to be sampled.**
Both estimators are to be printed side by side when fine lands; **neither is to be quoted
alone.**

## 4. THE GATING ORDER, FIXED HERE RATHER THAN IMPROVISED WHEN FINE LANDS

Unchanged from rule 5, restated so it cannot be re-ordered under the pressure of a result:

1. Any level **not iteratively converged or not plateaued** → **`NOT A RESULT`**.
2. Triple **`DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT`** → **`NOT A RESULT`**, with
   the value, **both triples and both orders printed beside it**.
3. Only **`CONVERGING`** reaches `PASS` (inside the pre-registered band) or `GATE FAIL`.
4. **GCI at Fs = 1.25. NEVER quoted when the three values are not monotone.**
5. The gate may turn a PASS or GATE FAIL **into** `NOT A RESULT`, **never the reverse**.

**Refinement ratio is to be taken in CELL LAYERS, not node counts.**

## 5. WHAT IS ALREADY KNOWN AND MUST TRAVEL WITH ANY TRIPLE VERDICT

- **Both landed levels are over the §9 drift limb at both stopping points** — coarse
  −1.605588e-03 @ 4000 and −2.591013e-03 @ 8000; medium −1.867907e-03 @ 4000 and
  +1.310541e-03 @ 8000. **Four readings, four over.** §9's contingency is defined on
  **fine**, so none of this fires it; these are **measurements, not gate verdicts**.
- **The two levels disagree in sign at 8000**, and medium changed sign between 4000 and
  8000. The drift is not behaving as a mesh-convergent quantity.
- **Stopping-point spreads: coarse 4.862826e-03 (4.9× the 1e-3 limb, limb cleared at
  28/41), medium 5.736344e-03 (5.7×, cleared at 15/41).** Both sign-changing.
- **No significance claim is attached to any of it.** Adjacent stopping points share ~99 %
  of their S12 window, so a p-value against an independence null would launder
  autocorrelation as evidence. The descents are reported as **visible**, never as
  significant.
- **A wide spread is NOT a licence for a third extension; §9 forecloses one. There is no
  16000.**

---

*Frozen 2026-09-11, before fine's `rc` sidecar exists. Submissions parked.*
