# RESULTS — a-posteriori re-solve of the TBRF anisotropy correction (Lane 1)

**Status: the preregistered propagation gate H0 FAILED. H1-H3 are therefore
NOT A RESULT, by the rule frozen in `PREREGISTRATION.md` §5 before any solve.**
The mechanism is measured, it is the same one Lane 2 found independently, and
that agreement is the finding.

Preregistration: `PREREGISTRATION.md` in this directory, frozen and posted to the
supervisor before any scored solve; unedited since. Nothing below is
re-registered. Parent record: `../RESULTS.md` (the a-priori TBRF reproduction).

Solver: `kOmegaSSTCorrected` from `sdk/openfoam/sparta` — **no new solver was
written**. OpenFOAM v2606. Cases copied out of the read-only benchmark clone to
`/home/ubuntu/closure-data/aposteriori/kaandorp/`.

---

## 1. Verdicts against the frozen ladder

| gate | preregistered band | measured | **VERDICT** |
|---|---|---|---|
| **G0a** solver identity | rel-L2 `U`, stock `kOmegaSST` vs `kOmegaSSTCorrected(0,0)`, same 200 iterations, < 1e-10 | **0.0 exactly** (bit-identical), `AR_1_Ret_360` | **PASS** |
| **G0b** null reproduces the SST row | \|Δ`U_rms`\| < 1e-3 absolute | T1 **2.4e-4** (0.19874 vs 0.1985); T2 **1.92e-3** (0.18652 vs 0.1846) | **PASS on T1, GATE FAIL on T2** (missed by 9.2e-4) |
| **H0** truth injection must cut `U_rms` ≥ 30 % | T1 `U_rms` ≤ 0.1390 | T1 **0.32151** — a **+62.0 %** *increase*; T2 **0.28980**, **+57.0 %** | **GATE FAIL** |
| **H1** ML beats SST, re-solved | `mean + 2sd < 0.1985` | 0.2594 ± 0.0007 (see §3) | **NOT A RESULT** (H0) |
| **H2** ML beats train-mean | `mean + 2sd <` MEANB | — | **NOT A RESULT** (H0) |
| **H3** ML within 2x the ceiling | `≤ 2.0 x` TRUTH | — | **NOT A RESULT** (H0) |
| **H4** ducts: secondary flow ≥ 0.3 % of bulk | ML in-plane \|U\| ≥ 0.3 % | **1.161 ± 0.016 %** (DNS 1.508 %) | **PASS** — with the §4 caveat |
| **H5** continuity < 1e-3 | RMS `div(U)` / gradient scale | ducts **6.1e-18 to 3.8e-4**; CBFS see §5 | **PASS on the ducts; NOT MEASURABLE on CBFS** |
| Kaandorp **Table 4** (BFS5100) | — | no such case on disk | **BLOCKED** |

`PREREGISTRATION.md` §5, H0: *"If H0 fails, H1-H3 are reported as NOT A RESULT,
not as failures of the model — a broken propagation path cannot grade a closure."*
That clause is why the ML numbers below are printed but not graded.

**The supervisor's stricter 50 % bar, reported beside every TRUTH row as
registered:** T1 would need `U_rms` ≤ 0.0993 and delivered 0.32151; T2 would need
≤ 0.0923 and delivered 0.28980. Both bars fail in the same direction, so the
choice between 30 % and 50 % changes nothing.

---

## 2. The table

`U_rms`, `U_mae` per `_common/BASELINES.md` §1 over all cells of the case's own
mesh. `k_mean` is the **transported** `k` at the graded checkpoint. `b_rms` is the
error of the **total** modelled anisotropy of the re-solved field. `divU` is
volume-weighted RMS `div(U)` divided by the field's own gradient scale. `2ndry` is
in-plane \|U\| as a percentage of bulk.

| case | config | state | iters | `U_rms` | `U_mae` | `k_mean` | `k/k_base` | `k/k_LES` | `b_rms` | unreal | `divU` | 2ndry % | `x_reatt` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **AR_1_Ret_360** | shipped SST (BASE) | — | — | **0.1985** | — | 26.679 | 1.000 | 0.615 | 0.5843 | 0.0000 | 4.5e-18 | 4e-16 | — |
| | `NULL` | CONVERGED-stagnation | 30000 | 0.19874 | 0.12655 | 26.712 | 1.001 | 0.615 | 0.5824 | 0.0000 | **6.1e-18** | 0.0000 | — |
| | `TRUTH` | CONVERGED-residualControl | 528 | **0.32151** | 0.24305 | **8.740** | **0.328** | 0.201 | 0.0261 | 0.0000 | 1.1e-04 | 0.4675 | — |
| | `MEANB` | CONVERGED-residualControl | 5026 | 0.68256 | 0.52595 | **0.128** | **0.005** | 0.003 | 0.3750 | 0.0000 | 4.0e-05 | 0.2102 | — |
| | `MEANB64` (LEAKY) | CONVERGED-residualControl | 1455 | 0.67169 | 0.51744 | 0.182 | 0.007 | 0.004 | 0.3414 | 0.0000 | 3.7e-05 | 0.2090 | — |
| | `ML0` | CAPPED-NOT-CONVERGED | 30000 | 0.25938 | 0.18972 | 5.247 | 0.197 | 0.121 | 0.2008 | 0.0249 | 3.2e-04 | 1.1430 | — |
| | `ML1` | CONVERGED-residualControl | 2490 | 0.26071 | 0.18818 | 5.216 | 0.196 | 0.120 | 0.1967 | 0.0601 | 3.8e-04 | 1.1733 | — |
| | `ML2` | CONVERGED-residualControl | 2869 | 0.26052 | 0.18794 | 5.286 | 0.198 | 0.122 | 0.2024 | 0.0281 | 3.1e-04 | 1.1672 | — |
| | **`TRUTH+R` POST-HOC** | CONVERGED-residualControl | 383 | **0.00341** | 0.00244 | **43.465** | 1.629 | **1.001** | 0.0023 | 0.0152 | 1.7e-04 | **1.4963** | — |
| **AR_3_Ret_360** | shipped SST (BASE) | — | — | **0.1846** | — | 29.238 | 1.000 | 0.594 | 0.5431 | 0.0000 | 1.2e-17 | 8e-16 | — |
| | `NULL` | CONVERGED-stagnation | 30000 | 0.18652 | 0.12707 | 29.267 | 1.001 | 0.595 | 0.5417 | 0.0000 | **9.6e-18** | 0.0000 | — |
| | `TRUTH` | CONVERGED-residualControl | 3052 | **0.28980** | 0.22975 | **10.504** | **0.359** | 0.213 | 0.0268 | 0.0000 | 8.6e-05 | 0.3891 | — |
| | `MEANB` | CAPPED-NOT-CONVERGED | 30000 | 0.75945 | 0.62376 | **0.000** | **0.000** | 0.000 | n/a | n/a | 2.5e-06 | 0.0219 | — |
| | `ML0/1/2` | PENDING (see §7) | | | | | | | | | | | |
| **CBFS13700** | shipped SST (BASE) | — | — | **0.0516** | 0.0258 | 0.00303 | 1.000 | 0.72 | 0.3051 | 0.0000 | 5.2e-03 | — | 5.891 |
| | registered rows | PENDING (see §7) | | | | | | | | | | | |
| | **`TRUTH+R` POST-HOC** | CAPPED (see §5) | 30000 | **0.03073** | 0.00920 | 0.00427 | 1.41 | 1.02 | 0.0228 | 0.0269 | 3.2e-01 | — | **4.384** |

LES truth for reference: `AR_1_Ret_360` `k` = 43.418, secondary flow **1.508 %**;
`AR_3_Ret_360` `k` = 49.216, secondary flow **1.411 %**; `CBFS13700`
`x_reatt` = **4.241**.

---

## 3. Seed spread

Three forest seeds, `AR_1_Ret_360`:

| quantity | ML0 | ML1 | ML2 | mean ± sd |
|---|---|---|---|---|
| `U_rms` | 0.25938 | 0.26071 | 0.26052 | **0.2594 ± 0.0007** |
| in-plane \|U\| (% bulk) | 1.1430 | 1.1733 | 1.1672 | **1.161 ± 0.016** |
| unrealisable fraction | 0.0249 | 0.0601 | 0.0281 | 0.0377 ± 0.0194 |
| RMS `div(U)`/grad scale | 3.2e-4 | 3.8e-4 | 3.1e-4 | 3.4e-4 ± 3.7e-5 |

The velocity spread is **0.27 % of the mean** — the three forests propagate to
essentially the same field. Whatever is wrong here is not seed noise.

---

## 4. The mechanism: transported `k` collapses, and that is what broke the ceiling

`PREREGISTRATION.md` §2.3 set `kDeficit` (Schmelzer's `R`) to zero because the TBRF
predicts `b` and nothing else, with the registered consequence *"our truth-b
ceiling is a b-only ceiling and is necessarily weaker than Schmelzer's Table 1"*.
**"Weaker" turned out to be "inverted", and the registration did not predict a
sign change.**

`k` is transported (registered §2.4). Injecting `b^Delta` changes the k-production
term by `Gextra = -2 k (b^Delta : grad U)`, strongly negative on these flows. With
no `R` to balance it, `k` collapses — and `nu_t` follows it, and the momentum
correction `2 k b^Delta` shrinks toward zero at the same time:

| configuration | `k/k_base` (T1) | `k/k_base` (T2) |
|---|---|---|
| `NULL` (control) | 1.001 | 1.001 |
| `TRUTH` (b only) | **0.328** | **0.359** |
| `MEANB` (b only) | 0.005 | ~0.000 |
| `ML` (b only) | 0.197 | pending |
| `TRUTH+R` (post-hoc) | 1.629, and `k/k_LES` = **1.001** | — |

**Cross-lane confirmation.** Lane 2 (Wu2018) reports independently that b-only
injection with transported `k` collapsed `k` to **0.33x**. Our `TRUTH` row is
**0.328x** on T1 and **0.359x** on T2. Different lane, different code path,
different learned model, same number. Lane 2 also reports `TRUTH` `U_rms` of
0.3215 on `AR_1_Ret_360` and 0.2898 on `AR_3_Ret_360`: **identical to ours to
five significant figures**, as they must be — both lanes push the same `b_LES`
through the same solver — which makes the pair a working cross-check on both
setups rather than an independent measurement.

Note the ordering this produces, which is diagnostic and not flattering to anyone:
**the ML injection scores better than the TRUTH injection** (0.2594 vs 0.32151),
and produces **more** secondary flow than the truth injection (1.161 % vs
0.4675 %, against a DNS 1.508 %). On a path that cannot carry the truth, being
closer to the truth is not rewarded. Reporting "the ML correction degrades `U` by
31 %" as a fact about the model would be wrong; it is a fact about the
propagation.

### The post-hoc run that isolates the cause — and what it is not

Decided **after** H0 failed, therefore **carrying no verdict** and **not part of
this test's ladder**: `kCorrectiveFrozenFoam` (the W2 SpaRTA frozen step,
`verification/campaign/W2_SPARTA_FROZEN_CBFS.md`) was run on the LES fields to
*extract* `R` and `bijDelta`, and both were propagated.

* `AR_1_Ret_360`: `U_rms` **0.00341** against the SST baseline's 0.1985 — a
  **98.3 % reduction**; transported `k` recovers to **43.465** against a truth of
  43.418 (0.1 %); secondary flow **1.4963 %** against a DNS 1.508 % (0.8 %).
  Frozen extraction cost 6.0 s; propagation converged in 383 iterations.
* `CBFS13700`: `U_rms` **0.03073** against 0.0516 (40.4 % reduction) and
  `x_reatt` **4.384** against the LES 4.241 (SST 5.891) — but see §5, its
  continuity number says it is not converged, so treat it as indicative only.

**The propagation path is not broken. The omission of `R` broke the ceiling.**
That is the whole content of this diagnostic. It does not rescue H1-H3, it is not
a variant of this test, and **a frozen-`k` arm or a `kDeficit`-carrying learned
model is a NEW preregistered test, not a continuation of this one** — nothing of
that kind is run or claimed here.

---

## 5. Continuity, and the limit of the instrument

Registered prediction (H5): volume-weighted RMS `div(U)` normalised by the field's
own gradient scale, **below 1e-3 for every re-solved configuration**, against this
lab's own published post-hoc figures of 10.5 % and 9.7 %
(`Certonomous_closure_challenge/description/METHOD.md` §6.2).

**On the ducts the prediction holds with room to spare** — 6.1e-18 (null),
2.5e-06 to 1.1e-04 (truth, train-mean), 3.1e-04 to 3.8e-04 (ML). Against 10.5 %
that is between **2.8e4x** and **1.7e16x** better. Charter §22.2's "continuity by
construction" is five to sixteen orders of magnitude, measured.

**On CBFS the registered threshold is below what the instrument can measure, and
that is a defect of this preregistration.** `div(U)` is computed from
`of_read.structured_gradient`, a curvilinear chain-rule gradient. Calibrated on
fields that are not ours:

| field | RMS `div(U)` / gradient scale |
|---|---|
| shipped converged SST, `AR_1_Ret_360` | 4.5e-18 |
| shipped converged SST, `AR_3_Ret_360` | 1.2e-17 |
| **shipped converged SST, `CBFS13700`** | **5.2e-03** |
| **LES truth, `CBFS13700`** | **4.3e-03** |

On the ducts the estimator is exact to round-off (the streamwise derivative is
identically zero for a fully-developed flow, so there is nothing to discretise).
On the curved CBFS mesh it has a **floor of ~5e-3**, above the registered 1e-3
threshold, which therefore **cannot be met by any field on that mesh — including
the shipped baseline and the LES truth itself**. H5 is graded on the ducts and
recorded as **NOT MEASURABLE** on CBFS. The post-hoc CBFS `TRUTH+R` value of
**0.322** is 60x that floor and is read as a genuine failure to converge, not as
estimator noise.

---

## 6. Convergence state per row, and a second preregistration defect

Every row's state is in §2. Three things are worth stating plainly.

**The registered convergence criterion cannot be satisfied by a converged duct.**
`PREREGISTRATION.md` §6 registered "initial residuals of `p` and `Ux` both below
1e-6, sustained 100 iterations". After **30,000 iterations** of the
zero-correction control on `AR_1_Ret_360` the initial residuals are `p` = **0.144**
and `Ux` = **8.4e-16**, with RMS `div(U)`/gradient scale = **6.1e-18** and
`U_rms` = 0.19874 against the published 0.1985. The field has not moved. The duct
is streamwise-periodic with a `meanVelocityForce`, so the cross-plane pressure is
nearly uniform and OpenFOAM's residual normaliser divides by a near-zero scale.
**The `p` residual on this case class is not a convergence measure.** The
registered stagnation fallback (field movement between checkpoints) is what grades
those rows, labelled `CONVERGED-stagnation`.

The criterion *does* work once the correction creates a real cross-plane pressure
field: `AR_3_Ret_360__TRUTH` met it at iteration **2283**.

**A solver that stops at first satisfaction of its own `residualControl` can never
exhibit a criterion phrased as "sustained for 100 iterations".** Rows labelled
`CONVERGED-residualControl` met OpenFOAM's per-iteration test (`p` **and all**
`U` components below 1e-6), which is stricter per iteration than the registered
one. The two mechanisms are mutually unsatisfiable as written, and that is a
defect of this preregistration, recorded rather than smoothed over.

**`CAPPED-NOT-CONVERGED` rows are scored at the cap**, per the registered rule.
Two rows: `AR_1_Ret_360__ML0` and `AR_3_Ret_360__MEANB`, both at 30,000. The
`MEANB` row is a collapse, not a near-miss: its transported `k` reached
**0.000** and its anisotropy error is undefined there.

---

## 7. What is PENDING, and why it does not move a verdict

Ten of the nineteen registered configurations completed before this lane's
session was interrupted at the credit limit; the driver was restarted with its
resume logic and the remainder were still running at the time of writing:
**`AR_3_Ret_360` ML0/1/2 and all six `CBFS13700` rows.**

**No pending row can change a verdict**, and the reason is structural rather than
optimistic: H0 is decided on the `TRUTH` configuration of T1, which is complete;
it failed on T2 as well; and H1-H3 are NOT A RESULT by the registered clause
regardless of what the remaining ML rows say. The pending rows would sharpen §4's
`k/k_base` table and supply CBFS's `x_reatt` under a b-only injection. They are
reported as **PENDING**, not omitted.

---

## 8. Realisability

Reported, no verdict (registered): the a-priori claim (iii) in `../RESULTS.md`
already returned GATE FAIL for this forest configuration at **0.1339**.

Re-solved, the total modelled anisotropy `-(nu_t/k)S + b^Delta` on
`AR_1_Ret_360` is outside the barycentric triangle in **0.0377 ± 0.0194** of cells
(ML seeds), against the truth's own **0.0159** and SST's **0.0000**. Re-solving
therefore *improves* realisability relative to the a-priori 0.1339 — because the
collapsed `k` shrinks `2 k b^Delta` toward zero, which is not a repair, it is the
same failure wearing a better number. `TRUTH` and `MEANB` inject realisable or
near-realisable tensors and score 0.0000. No clipping was applied anywhere
(`bScale` = 1.0 throughout, registered §2.5), and no configuration required the
registered `{0.8, 0.5}` divergence ladder: **nothing diverged.**

---

## 9. Compute

| item | core-hours |
|---|---|
| G0a identity pair (2 x 200 iterations) | 0.002 |
| 10 completed registered solves | **0.86** |
| post-hoc frozen extraction + propagation, `AR_1_Ret_360` | 0.004 |
| post-hoc frozen extraction + propagation, `CBFS13700` | 0.62 |
| **total charged to this lane so far** | **≈ 1.5** |

Lane cap 15 core-hours; the pending rows add at most ~3 more. Nothing here
approaches the 487-core-hour authorisation. Every solve was bounded by a
30,000-iteration `endTime` **and** a 3600 s `timeout` inside the script; no
process was ever killed.

---

## 10. What this test CANNOT see

* **It cannot grade the model.** H0 failed, so H1-H3 are NOT A RESULT. The ML
  numbers in §2 are printed so the mechanism is legible, not so they can be read
  as performance.
* **A frozen-`k` arm, or a learned model that also predicts `kDeficit`, is a NEW
  preregistered test.** Neither is run here. The post-hoc `TRUTH+R` diagnostic in
  §4 uses `R` extracted from the LES truth, not from any model, and is evidence
  about the *path*, not about a closure.
* **One Reynolds number per case, one mesh, no grid-refinement study.**
* **`bijDelta` is static**, frozen at the baseline SST `nu_t`, `k`, `S`, so the
  total anisotropy at convergence is not the forest's `b`. This test cannot
  separate "the forest's `b` is wrong" from "the frozen-`b^Delta` propagation form
  loses information" — and §4 shows the second effect is large enough to invert
  the ceiling on its own.
* **The forest is the POST-HOC D2-removed configuration** of `../RESULTS.md` §6,
  which itself carries no preregistered a-priori verdict. This is a variant of a
  variant, and **Kaandorp's Table 4 stays BLOCKED-ON-DATA**.
* **The ducts are streamwise-periodic with a `meanVelocityForce`**, so the bulk
  velocity is imposed and cannot be got wrong; the entire `U` error is profile
  shape and secondary flow.
* **`div(U)` on the CBFS mesh is estimator-limited at ~5e-3** (§5), so continuity
  claims below that on that case are not available from this pipeline.
* **Three seeds**, so the ± is a 3-sample standard deviation.
* **G0b failed on T2 by 9.2e-4.** The `AR_3_Ret_360` null re-solve settles 1.0 %
  away from the shipped `U_rms`, which is drift of the shipped field under 30,000
  further iterations rather than a correction effect (its `div(U)` is 9.6e-18 and
  its `k` moves 0.1 %). It is recorded as a failed gate, not explained away.

---

## ADDENDUM — 2026-08-21, completion status of the PENDING rows

**Nothing in this addendum can move a verdict, and the reason is structural, not
optimistic.** H0 is decided on the `TRUTH` configuration of T1, which was complete
before §1 was written; it failed on T2 as well; and H1-H3 are NOT A RESULT by the
registered clause regardless of what any remaining ML row says. The addendum
exists so the record shows what ran and what did not, not to change a grade.

**Completed and already tabulated in §2:** all seven `AR_1_Ret_360` rows, plus
`AR_3_Ret_360` `NULL`, `TRUTH` and `MEANB` — **10 of the 19 registered
configurations**, plus the two post-hoc `TRUTH+R` diagnostics.

**Still outstanding:** `AR_3_Ret_360` `ML0/1/2` and all six `CBFS13700` rows.
They are outstanding for an operational reason with no scientific content: this
lane's driver process was terminated three times by session-level interruption
(twice by the credit limit, once by session teardown), and each restart resumed
from the last completed row through the driver's own resume logic rather than
re-solving. The driver has been relaunched detached (`setsid`) and the rows will
land in `/home/ubuntu/closure-data/aposteriori/kaandorp/results.json`; a further
dated addendum can append them without touching §1-§10.

**What the outstanding rows would add, stated so their absence is legible:**

* `AR_3_Ret_360` ML seeds would give a second case's `k/k_base` for the ML arm.
  The T1 value is 0.197 and the T2 `TRUTH` value is 0.359; the mechanism in §4 is
  already established on both cases by their `TRUTH` and `MEANB` rows.
* The `CBFS13700` registered rows would give `x_reatt` under a b-only injection.
  The post-hoc `TRUTH+R` row already reports `x_reatt` = **4.384** against the LES
  4.241 and SST 5.891, and the b-only `TRUTH` rows on both ducts already show the
  ceiling inverted, so the CBFS b-only rows are expected to confirm rather than
  test.

**Compute unchanged in kind:** the outstanding rows add at most ~3 core-hours to
the ~1.5 already charged, against a lane cap of 15.
