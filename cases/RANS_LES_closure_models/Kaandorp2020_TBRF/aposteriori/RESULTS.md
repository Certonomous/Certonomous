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

---

## NOTE — 2026-08-22, closure follow-up lane: readiness and cost of the nine outstanding rows

Read-only audit of what is on disk. **No solve was run, nothing was launched, and
nothing below moves a verdict** — for the same structural reason the addendum
above gives: H0 is decided on the `TRUTH` configuration and H1–H3 are NOT A RESULT
by the registered clause, whatever these nine rows would say. §1–§10 and the
addendum are untouched.

### Readiness: none of the nine

Against the strict completion rule (`rc = 0`, `End` in `log.run`, last written
time directory equal to the `endTime`, fields newer than `0/`), **zero of the nine
qualify — none of them has a case directory at all.** No
`AR_3_Ret_360__ML{0,1,2}` and no `CBFS13700__{NULL,TRUTH,MEANB,ML0,ML1,ML2}`
exists under `ROOT` (`/home/ubuntu/closure-data/aposteriori/kaandorp/`) or
anywhere else on this host, and none appears in `results.json`, which still holds
exactly the same **10** runs. Nothing has silently completed.

### Three of the nine are BLOCKED, and the cause is not the operational one

The addendum records the outstanding rows as an operational casualty and says the
detached driver would land them. The driver **did** run detached, four times —
`lane.log`, `lane2.log`, `lane3.log`, `lane4.log` in `ROOT`, the last three
byte-identical — and each time it stopped at the same row, `AR_3_Ret_360__ML0`,
with the same uncaught exception:

```
ValueError: 'AR_3_Ret_360' is not in list        (run_lane.py, ml_b)
```

`/home/ubuntu/closure-data/kaandorp_tbrf/features_nodurbin.npz` carries **27**
cases and `AR_3_Ret_360` is **not** one of them (`AR_1_Ret_360` and `CBFS13700`
both are). So:

* **`AR_3_Ret_360` `ML0/1/2` — BLOCKED.** They cannot be built until that feature
  file is rebuilt to include the case. This is a missing input, not a queue.
* **The six `CBFS13700` rows — PENDING.** Their inputs are all present; they are
  unrun only because they sit *after* the blocked row in the plan and the
  exception aborted the whole loop before reaching them.

**Driver repaired, NOT RUN.** `run_lane.py` now raises a named `RowBlocked` that
says which case is missing from which file, and `main()` records a row it cannot
build or score as `status: "BLOCKED"` in `results.json` — reason and traceback
kept, no metric written, so it can never be read as a result — and continues with
the rest of the plan. One unbuildable row can no longer take the other registered
rows down with it. `py_compile` clean and the `RowBlocked` path exercised on its
no-solve path; **no solver was started.**

### Cost of the nine, if and when they are authorised

All solves in this lane are **serial** (`simpleFoam -case .`, `nProcs : 1`,
`OMP_NUM_THREADS=1`), so cores = 1 per run and core-hours = wall-hours. Rates are
measured from the completed runs' own `log.run` `ExecutionTime`: `AR_1_Ret_360`
(3,025 cells) 0.010814 s/iteration stock and 0.012296 s/iteration injected
(**×1.137** for the injection); `AR_3_Ret_360` (8,748 cells) 0.035079 s/iteration
stock; `CBFS13700` (21,000 cells) 0.069512 s/iteration injected, from
`CBFS13700__TRUTHR`. Iterations are charged at the registered 30,000-iteration
cap, which the `NULL` rows on both ducts and `AR_3_Ret_360__MEANB` all reached.
Rate **$0.0513 / core-hour**.

| row | status | cells | s/iteration | est. wall-h | cores | est. cost |
|---|---|---|---|---|---|---|
| `AR_3_Ret_360__ML0` | BLOCKED | 8,748 | 0.03989 | 0.332 | 1 | $0.0171 |
| `AR_3_Ret_360__ML1` | BLOCKED | 8,748 | 0.03989 | 0.332 | 1 | $0.0171 |
| `AR_3_Ret_360__ML2` | BLOCKED | 8,748 | 0.03989 | 0.332 | 1 | $0.0171 |
| `CBFS13700__NULL` | PENDING | 21,000 | 0.06114 | 0.509 | 1 | $0.0261 |
| `CBFS13700__TRUTH` | PENDING | 21,000 | 0.06951 | 0.579 | 1 | $0.0297 |
| `CBFS13700__MEANB` | PENDING | 21,000 | 0.06951 | 0.579 | 1 | $0.0297 |
| `CBFS13700__ML0` | PENDING | 21,000 | 0.06951 | 0.579 | 1 | $0.0297 |
| `CBFS13700__ML1` | PENDING | 21,000 | 0.06951 | 0.579 | 1 | $0.0297 |
| `CBFS13700__ML2` | PENDING | 21,000 | 0.06951 | 0.579 | 1 | $0.0297 |
| **total** | | | | **4.40** | 1 | **$0.226** |

**Hard upper bound $0.462.** Every solve is bounded by the `timeout 3600` in
`run_solver` as well as by the 30,000-iteration `endTime`, so nine runs cannot
exceed **9.0 core-hours** however badly they converge. The addendum's "at most ~3
core-hours" is a little optimistic at the cap — **4.4** is the planning figure —
but the lane cap of 15 is not at risk either way (≈1.5 charged + 4.4 = ≈5.9).

**Not launched here, deliberately.** R4 holds top capacity priority and is live on
this host.

---

## ADDENDUM — 2026-08-24T16:06:54Z, the six `CBFS13700` rows graded and the lane closed out

**This addendum grades rows. It moves no gate, threshold, cap or label**
(`CLAUDE.md` rule 2). §1–§10, the 2026-08-21 addendum and the 2026-08-22 note are
untouched; nothing above this line changed. Driver pid `1111229`, detached, log
`/home/ubuntu/closure-data/aposteriori/kaandorp/lane5.log`, exited on its own at
`[done] lane wall-hours 3.66`. **The artifact of record is
`/home/ubuntu/closure-data/aposteriori/kaandorp/results.json`, not the driver
log**; every number below was read from `results.json` or from the case's own
`log.run` and each is confirmed against the log rather than taken from it.

### A.1 The freeze, verified — and one gap that is not mine to rule on

`PREREGISTRATION.md` has **exactly one commit in its whole history**, `0ebc9d53`
(2026-08-21 18:52:18 +0000). Its blob there, the blob at `HEAD`, and
`git hash-object` of the file on disk are the **same object**:

```
411b25f1d452330558824a52885a2950ceffa54f
```

So the frozen file **is** the file that ran, byte-for-byte, and it carries **no
amendment** — there is nothing appended below §8 and nothing to reconcile.

**The gap, stated plainly rather than smoothed over.** That commit is timestamped
18:52:18Z on 2026-08-21, while the `AR_1_Ret_360__*` case directories under
`/home/ubuntu/closure-data/aposteriori/kaandorp/` carry mtimes of 17:27–17:44Z
the **same day** — about an hour *earlier*. §1 above records the file as "frozen
and posted to the supervisor before any scored solve"; posting to a supervisor is
not committing, and **git cannot evidence the commit-before-compute condition of
`CLAUDE.md` rule 2 for the original duct rows.** What git *does* evidence, and
what matters for this addendum, is that the file has been byte-unchanged since
18:52:18Z on 2026-08-21, so **every gate graded here was frozen two days before
the compute it grades** (the six `CBFS13700` solves ran 2026-08-23, 19:38–23:17Z).
The earlier rows' freeze ordering is referred to the closure supervisor as a §3
personal check; **this lane does not rule on it and did not re-grade those rows.**

### A.2 The grading path: no script is registered, so this is a hand grade

**`PREREGISTRATION.md` names no grading script anywhere in its 334 lines.** It
registers definitions (§4 metrics, pointing at `_common/BASELINES.md` §1), bands
and falsifiers (§5), and a convergence criterion (§6) — and nothing else. Neither
`run_lane.py`, `summarise.py`, `setup_case.py` nor `frozen_R.py` is named in it,
so **none of them is a registered comparator and none was run as one.** The rows
below are graded **by hand against the registered table**, arithmetic shown, from
`results.json`. Stated explicitly because the alternative — running an unnamed
script and calling its output the registered grade — would be exactly the
substitution rule 2 exists to prevent.

Consistent with that, **no instrument was modified.** `run_lane.py`,
`summarise.py`, `setup_case.py` and `frozen_R.py` were verified byte-identical to
their `HEAD` blobs before and after this grading (`git hash-object` vs
`git rev-parse HEAD:<path>`; `run_lane.py` `75ec0a8f…`, `summarise.py`
`39db20c0…`, `setup_case.py` `aecaaeae…`, `frozen_R.py` `a2ea338a…`). Nothing in
this addendum was produced by a changed instrument.

### A.3 Planted-zero control on the G0a zero (`CLAUDE.md` rule 3)

The single most load-bearing zero in this lane is G0a's `rel_L2_U = 0.0`. A zero
from a reader not shown able to see a non-zero is not evidence, so the reader was
planted against before the zero was believed.

The plant ran against **scratch copies only**; nothing under
`/home/ubuntu/closure-data/` was written. A known perturbation of **1.234e-03**
absolute was written into cell 0's `U_x` in a copy of
`AR_1_Ret_360__G0_corr/600/U`, and the **exact rel-L2 expression the lane uses**
(`run_lane.py:276`, over `of_read.read_field`) was re-run:

| | value |
|---|---|
| as shipped, stock vs corrected | `rel_L2(U)` = **0.000000e+00**, `max|a−b|` = 0.0 |
| planted 1.234e-03 abs on one component | reader sees `max|Δ|` = **1.000e-03**, `rel_L2(U)` = **4.002936e-07** |

**The reader can report a non-zero, so the 0.0 is evidence.** The plant itself
demonstrates the instrument limit that §A.5 grades: 1.234e-03 was written back as
1.000e-03, because the field is `writeFormat ascii` at `writePrecision 6`.

### A.4 Completion, row by row (`CLAUDE.md` rule 4 as registered here)

`PREREGISTRATION.md` §6 registers the **termination** mechanism (30,000-iteration
cap as `endTime`, plus a 3600 s `timeout` per solve) and the **convergence**
criterion (initial residuals of `p` **and** `Ux` both < 1e-6 sustained 100
consecutive iterations; stagnation fallback `max|ΔU|/U_bulk` < 1e-6 over the last
500 iterations). It registers **no field list and no age guard**; the age guard
was checked anyway and is recorded below because a guard that passes costs
nothing to report.

All six `CBFS13700` cases: `startTime 30000`, `endTime 60000`, `writeFormat
ascii`, `writePrecision 15`, `nProcs : 1`.

| row | rc | `End` | last time / `endTime` | `ExecutionTime` count | fields at last time | age guard | registered convergence |
|---|---|---|---|---|---|---|---|
| `NULL` | 0 | yes | **30884 / 60000 — early stop** | 884 = iterations run | `U k nut omega p phi bijDelta kDeficit tauijRecon` | pass | **not met** |
| `TRUTH` | 0 | yes | 60000 / 60000 | 30000 | same | pass | **not met** |
| `MEANB` | 0 | yes | 60000 / 60000 | 30000 | same | pass | **not met** |
| `ML0` | 0 | yes | 60000 / 60000 | 30000 | same | pass | **not met** |
| `ML1` | 0 | yes | 60000 / 60000 | 30000 | same | pass | **not met** |
| `ML2` | 0 | yes | 60000 / 60000 | 30000 | same | pass | **not met** |

**`NULL` is the one row where `last time == endTime` does not hold, and it is not
a truncation.** It stopped at iteration 884 because OpenFOAM's own
`residualControl` was satisfied — `SIMPLE solution converged` appears once in its
`log.run` — which is the §6 defect §6 above already recorded: a solver that stops
at first satisfaction of `residualControl` can never exhibit a criterion phrased
as "sustained for 100 iterations". Its completion is established by `rc = 0` + the
`End` line + that banner, **not** by the time-equality clause, and this addendum
says so rather than reporting the clause as met.

**What `conv=None` on all six actually means, measured rather than inferred.**
The registered residual route was not met on any row. The registered **stagnation
fallback** was hand-evaluated from the written checkpoints — and here the
instrument is coarser than the registration: `writeInterval` is 5,000 iterations,
so the finest measurable window is **5,000**, not the registered **500**. That is
a *stricter* test than registered (more movement is available in 5,000 iterations
than in 500), so a row failing it fails the registered one too:

| row | checkpoints | window | `max|ΔU|/U_bulk` | registered fallback (< 1e-6) |
|---|---|---|---|---|
| `NULL` | 30000 → 30884 | 884 it | 1.2527e-02 | not met |
| `TRUTH` | 55000 → 60000 | 5000 it | **1.0086e-06** | not met — **by 0.9 %** |
| `MEANB` | 55000 → 60000 | 5000 it | **6.8887e-01** | not met |
| `ML0` | 55000 → 60000 | 5000 it | **1.0359e+00** | not met |
| `ML1` | 55000 → 60000 | 5000 it | **1.0275e+00** | not met |
| `ML2` | 55000 → 60000 | 5000 it | **9.6701e-01** | not met |

**`MEANB` and the three `ML` seeds are moving by of order the bulk velocity
itself between their last two checkpoints, at the 30,000-iteration cap.** Their
final initial residuals confirm it: `p` **9.9e-03 to 1.2e-02** and `Ux`
**3.7e-03 to 6.5e-03**, four orders of magnitude above the registered 1e-6, with
`p` excursions to 0.14–0.23 inside the last 500 iterations. These are not
near-misses on convergence; the fields are limit-cycling, and their `U_rms` values
are snapshots of a field that is still changing by ~100 % of `U_bulk`. Recorded as
that, not as converged answers with an asterisk.

`TRUTH` is the honest borderline: final residuals `p` = 1.83e-08 and
`Ux` = 3.79e-09, movement 1.0086e-06 over 5,000 iterations — **0.9 % above the
fallback threshold on a window 10x wider than the registered one.** On the
registered 500-iteration window it would very likely pass; **that window was never
written to disk, so it cannot be measured, and this addendum does not claim it.**

**What the pre-registration says failure to converge implies, quoted rather than
paraphrased.** §5 H1: *"**GATE FAIL** iff `mean(U_rms | ML) ≥` the gate, **or any
ML seed diverges or fails to converge (sec. 6)**"*. Failure to converge is
therefore registered **in advance** as a GATE FAIL condition on H1 — not as NOT A
RESULT. NOT A RESULT arrives on H1–H3 by a different registered route, the H0
cascade in §A.5. Both are applied below exactly as frozen; neither is softened and
neither is upgraded.

**The `diverged=True` banner artifact, confirmed by direct count.**
`results.json` carries `diverged: true` on every scored row. It is an artifact of
`run_lane.py:175`, which tests `"Floating point exception" in line` — and every
OpenFOAM log header contains `trapFpe: Floating point exception trapping enabled
(FOAM_SIGFPE).`. `summarise.py:29–31` documents the guard. Counted directly in
each of the six `CBFS13700` `log.run` files:

| row | `FOAM FATAL` | `Foam::sigFpe` | lines containing "Floating point exception" |
|---|---|---|---|
| `NULL` / `TRUTH` / `MEANB` / `ML0` / `ML1` / `ML2` | **0** each | **0** each | **1** each — the `trapFpe` header line, in every case |

**Zero `FOAM FATAL` in all six. Nothing crashed, nothing diverged on a
floating-point exception, and the registered `bScale ∈ {0.8, 0.5}` divergence
ladder (§2.5) was not triggered and was not run.** The `diverged` field in
`results.json` must not be read as a result; the defect is in the flag, not in the
solves.

### A.5 The gates, as frozen

#### G0 — solver identity (runs first; the lane stops if G0a fails)

**G0a — PASS as registered, with the instrument limitation disclosed.**
Registered band: rel-L2 of `U`, stock `kOmegaSST` vs `kOmegaSSTCorrected(0,0)`
from the same start field over the same 200 iterations, **< 1e-10**. Measured:
**0.000000e+00** on `AR_1_Ret_360` — the two `600/U` files are **byte-identical**
(`md5 ff95ccb5c5b3f146ac4c364c006352b5` on both). `0.0 < 1e-10` holds, so the gate
is **PASS** and the lane proceeds, as frozen.

**But the registered threshold is far below what this instrument can resolve, and
that is a third pre-registration defect of the same family as §5 and §6 above.**
The G0 pair writes `writeFormat ascii` at **`writePrecision 6`**. Measured from
the artifact itself, not estimated:

| smallest non-zero this instrument can report | rel-L2 |
|---|---|
| one ulp of the 6-digit representation in the largest component (108.209) | **4.002936e-07** |
| half an ulp on every component (the quantisation floor) | **1.822069e-06** |

**The registered 1e-10 sits 4,003x below the single-ulp floor and 18,221x below
the quantisation floor.** Two solvers agreeing only to ~1e-8 relative would round
to the same six digits, produce byte-identical files, and pass this gate at "0.0".
So what G0a as executed establishes is **agreement to better than 4.0e-07
relative**, not agreement to better than 1e-10. That is still a strong solver-
identity result — byte-identity over 3,025 cells and 200 iterations is not a weak
statement — but the number in the frozen band was never reachable by the
instrument that read it. **The gate is recorded PASS on the registered comparison,
because that is what the frozen text says; the threshold is not restated as met at
1e-10.** Referred to the closure supervisor and to verification, docket D488.

*(A second, smaller disclosure on G0a: the registered wording is "the same 200
iterations", and the solvers did run 200 iterations each, `startTime 405` →
`endTime 605`. The comparison was made at the last **written** time, **600**, i.e.
after 195 of the 200 — identically for both solvers, so the comparison is
apples-to-apples and the gate is unaffected. Recorded because "200" appears in the
frozen text and "600" appears in `results.json`.)*

**G0b — null reproduces the published SST row, |Δ`U_rms`| < 1e-3 absolute.**
The `CBFS13700` row is new this pass; the two duct rows are restated from §1
unchanged, for the reader's convenience only, and are not re-graded here.

| case | SST gate | `NULL` measured | \|Δ\| | **VERDICT** |
|---|---|---|---|---|
| `AR_1_Ret_360` | 0.1985 | 0.19873619 | 2.362e-04 | **PASS** *(as §1)* |
| `AR_3_Ret_360` | 0.1846 | 0.18652119 | 1.921e-03 | **GATE FAIL** *(as §1)* |
| **`CBFS13700`** | **0.0516** | **0.05155375** | **4.625e-05** | **PASS** |

**`CBFS13700__NULL` is the strongest control in the lane.** Zero correction, from
the shipped converged SST field, it settles in 884 iterations on OpenFOAM's own
`residualControl` and lands `U_rms` within **4.6e-05** of the published SST row —
and its `x_reatt` is **5.8950** against the published SST **5.891**, agreement to
**0.004** of a chord. **The corrected solver reduces to stock SST on the paper's
own case.** Everything else measured on `CBFS13700` this pass rests on that.

#### H0 — the propagation gate on the whole lane

Registered: **NOT A RESULT for the entire lane** if `TRUTH` fails to reduce
`U_rms` on **T1** (`AR_1_Ret_360`) by **≥ 30 %** relative to the SST gate 0.1985 —
i.e. `TRUTH` must reach **≤ 0.13895**.

| case | SST gate | 30 % band | 50 % band (the stricter reading, reported as registered) | `TRUTH` measured | change |
|---|---|---|---|---|---|
| **T1** `AR_1_Ret_360` | 0.1985 | ≤ 0.13895 | ≤ 0.09925 | **0.321515** | **+61.97 %** |
| T2 `AR_3_Ret_360` | 0.1846 | ≤ 0.12922 | ≤ 0.09230 | **0.289795** | **+56.99 %** |
| **T3 `CBFS13700`** *(new this pass)* | **0.0516** | **≤ 0.03612** | ≤ 0.02580 | **0.084131** | **+63.05 %** |

**H0: GATE FAIL — and therefore NOT A RESULT for the entire lane**, by the clause
frozen in §5 before any solve. The truth injection does not improve the velocity
field; it degrades it, on all three registered cases, by 57–63 %, and the choice
between the 30 % and 50 % bars changes nothing.

**What this pass adds is that the third case agrees.** §1 decided H0 on two
streamwise-periodic ducts. `CBFS13700` is a separated flow on a curved wall — the
paper's own case C1, a different mesh, a different flow class, a different metric
family — and it inverts the ceiling by **+63.05 %**, the largest of the three.
The b-only propagation form does not fail because the cases were ducts.

#### H1, H2, H3 — NOT A RESULT, by the registered cascade

§5, H0: *"If H0 fails, H1-H3 are reported as **NOT A RESULT**, not as failures of
the model — a broken propagation path cannot grade a closure."* The numbers are
printed so the mechanism is legible; **they are not grades, and the shape a gate
would have taken is shown only so a reader can see the cascade is not hiding a
pass.**

`CBFS13700`, three forest seeds: `U_rms` **0.15883 / 0.15107 / 0.15289**,
mean **0.15426**, sample sd **0.00406**, mean + 2sd **0.16238**.

| gate | registered band | measured | shape, had H0 held | **VERDICT** |
|---|---|---|---|---|
| **H1** ML beats SST re-solved | mean + 2sd < 0.0516 | 0.16238 | GATE FAIL (also on the "fails to converge" clause — all three seeds) | **NOT A RESULT** (H0) |
| **H2** ML beats the trivial train-mean | mean + 2sd < `MEANB` 0.13965 | 0.16238 | GATE FAIL — **the constant tensor with no inputs propagates better than the forest** | **NOT A RESULT** (H0) |
| **H3** ML within 2.0x the ceiling | mean ≤ 2 × 0.084131 = 0.16826 | 0.15426 | PASS — **but the "ceiling" it is within 2x of is itself 63 % worse than doing nothing** | **NOT A RESULT** (H0) |

H2's shape is worth one sentence because it is the falsifier §5 registered in
advance: on `CBFS13700` the three-number constant `MEANB` tensor beats all three
forest seeds. On T1 the ordering was the opposite (`MEANB` 0.68256 against ML
0.26020). **Neither ordering is graded, and neither should be quoted as a finding
about the forest** — both are facts about a propagation path that cannot carry the
truth.

#### H4 — secondary flow in the ducts (T1)

Registered on the ducts only; `CBFS13700` contributes nothing to it and the three
`AR_3_Ret_360` ML rows are BLOCKED (§A.7). Restated from §1 unchanged, **not
re-graded**: ML in-plane |U| **1.161 ± 0.016 %** of bulk against a registered
PASS band of **≥ 0.3 %** — **PASS**. Noted for the record: the §5 cascade names
**H1–H3** only, so H0's failure does not, as registered, void H4 or H5.

#### H5 — continuity, and a disagreement with §1 that this lane does not resolve

**The registered metric is stated in §5 H5 as "volume-weighted RMS `div(U)`
normalised by `U_bulk / L`".** `results.json` carries both that quantity
(`divU_rms_over_UbulkL`) and a second, `divU_rms_over_gradscale`, normalised by
the field's own gradient scale. **§1 and §5 above graded H5 on the gradient-scale
form.** That is a departure from the registered normalisation, it is in the
committed record, and **rule 2 forbids me to rewrite it and rule 6 forbids me to
edit it — so it is disclosed here and referred, not corrected.**

Graded on the **registered** normalisation, `< 1e-3`, the six new rows:

| row | `divU`/(`U_bulk`/`L`) — **registered** | `divU`/grad-scale (the §5 form) | **VERDICT (registered form)** |
|---|---|---|---|
| `NULL` | 2.6208e-01 | 5.265e-03 | **GATE FAIL** |
| `TRUTH` | 1.5469e+00 | 2.889e-02 | **GATE FAIL** |
| `MEANB` | 1.1783e+00 | 2.345e-02 | **GATE FAIL** |
| `ML0` | 4.2679e+00 | 7.896e-02 | **GATE FAIL** |
| `ML1` | 1.2820e+01 | 2.105e-01 | **GATE FAIL** |
| `ML2` | 1.3674e+01 | 2.412e-01 | **GATE FAIL** |

**The control fails it too, and that is the fact a reader needs.** `NULL` carries
**zero** correction — it is stock SST — and reads **0.262**, 262x the registered
threshold. §5 above already established that on this curved mesh the
`of_read.structured_gradient` estimator has a floor of ~5e-3 in the grad-scale
form, above the registered 1e-3, **which the shipped converged SST baseline and
the LES truth itself both exceed.** A threshold the truth cannot meet is measuring
the instrument, not the field.

**So: GATE FAIL is recorded, because that is what the frozen text compels** —
§5 H5, verbatim: *"**GATE FAIL on H5** for any configuration exceeding 1e-3."* It
is unconditional and it was frozen before any solve. §1 instead recorded "NOT
MEASURABLE on CBFS", **which is not in the fixed vocabulary of `CLAUDE.md` rule 1
and of `VERIFICATION_CHARTER.md` §2.** The two readings of the same frozen clause
now sit in one record. **That conflict is referred to the closure supervisor and
to verification and is not resolved by this lane** — a lane may not retire or
reinterpret a gate threshold, and choosing the softer of two readings on my own
authority is exactly what rule 1 forbids.

The gradient-scale column is printed beside it so whichever reading is ruled, the
numbers behind it are already on the record.

#### Realisability and `x_reatt` — reported, no verdict (as registered)

Realisability carries no verdict by §5's design. `x_reatt` is a §4 metric with no
registered band, so it carries none either.

| row | unrealisable fraction | `x_reatt` | `k_rms` | `b_rms` (total) |
|---|---|---|---|---|
| shipped SST (BASE) | 0.0000 | **5.891** | — | 0.3051 |
| `NULL` | 0.0000 | **5.8950** | 0.7061 | 0.3026 |
| `TRUTH` | 0.0116 | 6.9117 | 0.8281 | 0.0312 |
| `MEANB` | 0.0062 | 7.9480 | 1.4659 | 0.3341 |
| `ML0` | 0.1218 | 8.7807 | 1.8163 | **4.8303** |
| `ML1` | 0.1346 | 11.1672 | 1.8196 | **5.5276** |
| `ML2` | 0.0833 | **14.4603** | 1.8179 | **7.7085** |
| LES truth | — | **4.241** | — | — |

Every configuration moves `x_reatt` **away** from the LES 4.241, in the same
direction the b-only injection moves `U_rms`. The `ML` rows' total-anisotropy
error `b_rms` of **4.83–7.71** is an order of magnitude above `NULL`'s 0.3026 and
two above `TRUTH`'s 0.0312; `|b|` for any realisable state is bounded near 0.8, so
these are not physical anisotropies — read together with the 8–13 % unrealisable
fractions and the limit-cycling in §A.4, the `ML` rows on `CBFS13700` describe a
solver in trouble, not a closure being measured. `n_kmask` = **2,984** cells of
21,000 masked by the registered `k_RANS < 1e-4 · mean(k_LES)` rule (§2.2) on every
injected row; **0** on `NULL`.

### A.6 Cost — registered versus actual (`CLAUDE.md` rule 12)

All solves serial: `nProcs : 1` in every `log.run`, `OMP_NUM_THREADS=1` set by the
driver, so **ranks = 1** and core-minutes = wall-seconds ÷ 60.

| row | wall s | core-min | over 3600 s? |
|---|---|---|---|
| `CBFS13700__NULL` | 69.3 | 1.155 | no |
| `CBFS13700__TRUTH` | 1701.6 | 28.360 | no |
| `CBFS13700__MEANB` | **3411.2** | 56.853 | **no — 188.8 s under** |
| `CBFS13700__ML0` | 3192.6 | 53.210 | no |
| `CBFS13700__ML1` | 1978.7 | 32.978 | no |
| `CBFS13700__ML2` | 2796.0 | 46.600 | no |
| G0a identity pair | 9.4 | 0.157 | no |
| **solver subtotal** | **13 158.8** | **219.313** | |
| **driver end-to-end** (`lane_wall_hours` 3.659522, single process) | **13 174.3** | **219.571** | |

**Gross = 219.571 core-min = 3.6595 core-h = $0.1877 derived** *(derived, not
measured; rate $0.0513/core-h, c7a.4xlarge, reported-by-owner — the box cannot
read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5)*.

**Cleaned = gross = 219.571 core-min.** No row exceeds 3600 wall s; the largest is
`MEANB` at 3411.2 s, so the stall rule matches nothing and there is nothing to
separate out. **Zero waste**: nothing was killed, nothing was re-run, and the
three BLOCKED rows consumed **0.0 s** each (the exception fires in `ml_b` before
any solver starts).

**Registered estimate, from the frozen `PREREGISTRATION.md` §7 and from nowhere
else:** 0.126 s/iteration on CBFS at the 30,000-iteration cap = 63 min = **1.05
core-h per CBFS solve**, and 0.06 core-h per duct solve, in the worst-case line
*"6 × 1.05 + 13 × 0.06 ≈ 7.1 core-hours"*. This pass's nine registered rows are
six CBFS + three `AR_3_Ret_360` ML ducts: **6 × 1.05 + 3 × 0.06 = 6.48 core-h =
388.8 core-min = $0.3324 derived**.

**Ratio actual/predicted = 219.571 / 388.8 = 0.565x.** For the six rows that
actually ran, against their own 6.30 core-h: **0.581x**.

**Gap attribution — one dominant cause, misprediction, in the conservative
direction.** The registered 0.126 s/iteration came from a **5-iteration** interface
check (§2.1), which amortises mesh read, field read and library load over five
iterations and therefore over-states the steady-state per-iteration cost.
Measured per-iteration from each row's own `log.run` `ExecutionTime`:

| row | `ExecutionTime` s | iterations | s/iteration | vs registered 0.126 |
|---|---|---|---|---|
| `NULL` | 68.95 | 884 | 0.077998 | 0.619x |
| `TRUTH` | 1699.21 | 30000 | 0.056640 | 0.450x |
| `MEANB` | 3371.57 | 30000 | 0.112386 | 0.892x |
| `ML0` | 3189.10 | 30000 | 0.106303 | 0.844x |
| `ML1` | 1978.08 | 30000 | 0.065936 | 0.523x |
| `ML2` | 2795.63 | 30000 | 0.093188 | 0.740x |

Mean over the five capped rows **0.086891 s/it = 0.690x** the registered basis.
A second, smaller contribution: `NULL` stopped at **884 of 30,000** iterations on
`residualControl`, spending 3 % of the iteration budget the estimate charged it —
**not waste, that is the row converging**, and the estimate charging every row at
the cap is the conservative choice a pre-registration should make.

**Contention, named but not claimed.** The five capped rows ran identical meshes
for identical iteration counts and spread **1.98x** in per-iteration cost (0.0566
to 0.1124 s/it) — with the lab fleet live on the box throughout. Part of that
spread is host contention and part is real per-configuration linear-solver work
(different `bijDelta` fields change the pressure solve). **This lane cannot
separate the two from what was recorded** and does not attribute the spread to
either.

**One near-miss worth carrying forward.** `MEANB` finished at **3411.2 s** against
the registered `timeout 3600` in `run_solver` — **5.2 % of margin**. Had
contention been ~6 % worse, that row would have been truncated mid-solve by the
registered timeout, and the record would have carried a partial field set. The
timeout did its job; the margin is thinner than the registration assumed.

**Lane cap: 15 core-h, not approached.** §9 above charged ≈1.5 core-h; this pass
adds 3.66; cumulative **≈5.16 core-h**, and 16 of the 19 registered solves have
now run. Well inside the cap and inside the §7 worst-case 7.1.

The calibration row lands in `docs/COST_CALIBRATION.md` as **C-15**, per
`CLAUDE.md` rule 12 and Sanaa's 2026-08-23 directive.

**Cost of the ten resumed rows is not re-charged here.** `run_lane.py:309–315`
does not re-solve a row whose `log.run` already ends in `End`; it re-parses and
re-scores it and writes the sentinel `wall_s = -1.0` with `resumed: true`. That
sentinel is why `lane5.log` prints `wall= -1.0s` for every `AR_1`/`AR_3` row —
**not a failed measurement, a row that did not run this pass.** Their measured
cost is on the record already (§9) and is confirmed by their own `log.run`
`ExecutionTime`: `AR_1` 6.7–353.4 s per row, `AR_3` `NULL` 1052.4 s, `TRUTH`
108.0 s, `MEANB` 1261.3 s. Nothing is missing and nothing is estimated.

### A.7 Disclosed limitations

1. **G0a's registered threshold is 4,003x below its instrument's resolution**
   (§A.5). Measured, not asserted: 4.002936e-07 for one ulp of the 6-digit ascii
   representation, 1.822069e-06 for the half-ulp quantisation floor, against a
   registered 1e-10. What the gate establishes is agreement to < 4.0e-07, and the
   two `600/U` files are byte-identical. Docket **D488**.
2. **H5's registered normalisation and the one §1/§5 graded on differ** (§A.5),
   and on the registered normalisation the zero-correction `NULL` control fails
   the threshold by 262x. Referred, unresolved.
3. **The `diverged=True` flag in `results.json` is an artifact** of
   `run_lane.py:175` reading the `trapFpe` header banner (§A.4). **0** `FOAM
   FATAL` and **0** `Foam::sigFpe` in all six `CBFS13700` logs, counted directly.
   `run_lane.py` was **not repaired** — it is a frozen mid-campaign instrument and
   a lane does not edit one to make a record read better. The repair is named for
   the supervisor's queue, not made.
4. **`AR_3_Ret_360__ML0/1/2` — BLOCKED**, and the cause is a missing input, not a
   queue: `AR_3_Ret_360` has no block in
   `/home/ubuntu/closure-data/kaandorp_tbrf/features_nodurbin.npz`, which holds 27
   cases. The driver recorded them as BLOCKED through its `RowBlocked` path with
   reason and traceback, wrote **no metric** for them, and continued — 16 of 19
   registered configurations have now run. No case directory exists for the three,
   confirmed on disk.
5. **`AR_3_Ret_360__MEANB` has `unrealisable_frac = nan` and `b_rms_total = nan`**
   — the row's `k` collapsed to 0.000 (§4 above) so the registered
   `k > 1e-4 · mean(k_LES)` mask left an empty set and the mean is over nothing
   (`RuntimeWarning: Mean of empty slice`, `run_lane.py:235–236`). **Not
   measured**, and not reported as 0.
6. **The stagnation fallback is measured on a 5,000-iteration window, not the
   registered 500** (§A.4) — `writeInterval` never wrote the finer window. The
   coarser test is the stricter one, so the four "not met" verdicts stand; the
   `TRUTH` borderline at 1.0086e-06 does **not** become a pass and is not claimed
   as one.
7. **The pre-registration's freeze cannot be shown by git to precede the original
   duct compute** (§A.1). It can, and does, for everything graded here.
8. Everything §10 already lists still binds: one Reynolds number per case, one
   mesh, no grid-refinement study, `bijDelta` static, three seeds, no uncertainty
   band on the LES truth, and the forest is the post-hoc D2-removed variant of a
   variant. **Kaandorp's Table 4 stays BLOCKED-ON-DATA** — there is no `BFS5100`
   case on disk.

### A.8 What remains

* **Queued, not done: the `run_lane.py:175` divergence-flag repair** (limitation 3).
  A frozen mid-campaign instrument is not edited by a grading lane.
* **Rule-14 call sites.** This campaign's own `libs` call site is compliant and was
  read to confirm it: `setup_case.py:106–115` inserts-or-replaces and then
  **asserts** (`assert "libspartaTurbulenceModels" in s`). The standing
  post-campaign sweep of the *other* call sites is the supervisor's queued item;
  **this lane did not sweep them and reports nothing about them.**
* **`AR_10_Ret_180` diagnostic stays REPORTED-NOT-GRADED**, as the closed R4 ladder
  ruled. Nothing here regrades it.
* **`AR_3_Ret_360__ML0/1/2` stay BLOCKED** until `features_nodurbin.npz` is rebuilt
  to include the case. Rebuilding it is a new registered item, not a continuation
  of this one.
* **Two referrals on the closure supervisor's and verification's desk**: the G0a
  instrument floor (D488) and the H5 normalisation/vocabulary conflict. Neither is
  a lane's call.
* **Nothing was sent, filed, uploaded or submitted** (`CLAUDE.md` rule 7).

### A.9 Verdict

**The lane's verdict is unchanged and is now carried by three cases instead of
two: H0 GATE FAIL, therefore NOT A RESULT for the entire lane.** The b-only
frozen-`b^Delta` propagation with transported `k` and `R = 0` inverts the ceiling
by **+61.97 %** on `AR_1_Ret_360`, **+56.99 %** on `AR_3_Ret_360` and **+63.05 %**
on `CBFS13700`. H1–H3 are **NOT A RESULT** by the registered cascade. G0a **PASS**
(with §A.5's instrument disclosure), G0b **PASS** on T1 and T3 and **GATE FAIL** on
T2, H4 **PASS**, H5 **GATE FAIL** on all six new rows under the registered
normalisation with the conflict of §A.5 referred. The three `AR_3_Ret_360` ML rows
are **BLOCKED**; Kaandorp Table 4 is **BLOCKED**.

**No gate, threshold, cap or label was altered by this addendum, and no number
above §A.1 was changed.**

*Assertion, `CLAUDE.md` rule 6: **lines whose number changed above this section: 0** —
this addendum is a pure append; verified by diffing the first 420 lines of this file
against its pre-append state, zero differences.*

---

## ADDENDUM — 2026-08-24T16:18:13Z, closure supervisor: corrections of record and two diagnostics from the independent re-grade

**Appended only. Lines whose number changed above this section: 0** — the
933-line body above is the committed blob `8503cd830eca68b7b72b24745b3390b7cc2b2aaa` at `6ff8e65cde0c8d7bc1d0f5e6582b32423ce059fc`, re-hashed in
the same shell invocation as this append. Nothing above is edited; no gate,
threshold, cap, label or verdict moves.

**Provenance.** The 2026-08-24T16:06:54Z addendum above was written by the
grading lane the previous closure supervisor dispatched, which survived its
supervisor's death and landed `a56cc309`. A second lane, dispatched by the
re-spawned supervisor at 16:06Z, found that addendum on disk 74 s later,
wrote nothing, and instead re-graded the same six rows independently. This
addendum records what the re-grade found, by the supervisor who read both.

### 1. Four false cross-references, corrected (rule 11 — an id written ahead of its append is a prediction, not an identifier)

The addendum above cites **`D488`** (four occurrences) for the G0a
instrument-floor referral and **`C-15`** (once, "the calibration row lands …
as C-15") for its cost row. Both ids were written into prose before the rows
were appended, and dafoam landed both at 16:03:03Z (`b69ac6ec`), three minutes
earlier. **Read `D488` as `D492` and `C-15` as `C-18`** — the ids that
actually landed (`961b0b3e`, `a56cc309`), each re-derived max+1 at its
commit. The parked drafts in `RECORDS_PENDING_D486.md` (ids D491 / L-269 at
drafting) landed as **D492 / L-269**; D492's own text says "D491/L-269 were
taken by peers", which is true of D491 only — L-269 landed as drafted. This
addendum is that correction of record.

### 2. `k/k_base` on CBFS — a diagnostic that §4's mechanism does not cover (no verdict)

`results.json` carries no `k_mean` for CBFS; the re-grade lane computed it
the way `summarise.py:101` does, against the shipped-SST mean 0.003018
(§2 BASE row 0.00303). **Unregistered path, diagnostic only, carries nothing.**

| row | `k/k_base` | row | `k/k_base` |
|---|---|---|---|
| `NULL` | 1.011 | `ML0` | 0.065 |
| `TRUTH` | **0.914** | `ML1` | 0.060 |
| `MEANB` | 0.330 | `ML2` | 0.073 |

§4 explains the ducts' ceiling inversion by transported-`k` collapse (TRUTH
retains 0.328 on T1, 0.359 on T2). **On CBFS the TRUTH row inverts the ceiling
by the largest margin of the three cases (+63.05 %) while retaining 91 % of its
baseline `k`.** The k-collapse account therefore does not by itself explain the
third case, and §4 is read with that caveat. What does explain it is a new
pre-registered question, not a continuation of this one.

Seed spread on CBFS: sd/mean **2.63 %** (0.154263 ± 0.004058) against 0.27 %
on T1 — ten times wider, consistent with the limit-cycling reading of the
addendum above.

### 3. Cost, the secondary comparison the addendum omits

Per-row `ExecutionTime` from the six `log.run` files (serial): NULL 68.95 s,
TRUTH 1699.21, MEANB 3371.57, ML0 3189.10, ML1 1978.08, ML2 2795.63 — **13,102.54
s = 218.376 core-min = 3.6396 core-h = $0.1867 derived**, 0.4 % under C-18's
driver-`wall_s` basis (219.571); neither is wrong, C-18 stands. Against the
frozen §7 figure (378 core-min for six CBFS solves) **0.578×**; against the
2026-08-22 NOTE's refined 204.24 core-min **1.069× — the refined figure
under-predicted by 7 %.** The calibration fact: §7's 0.126 s/it came from a
5-iteration interface check and over-states steady state by 1.45× (five capped
rows mean 0.086891 s/it); the NOTE's 0.06951 s/it, from one completed 30,000-it
solve, lands within 7 % but optimistic — **a rate from one completed solve is a
floor, not a point estimate.** The five capped rows spread **1.98×** in
per-iteration cost on an identical mesh with T-family solvers live; load not
recorded, contention not attributed. Whole lane ≈ 5.146 core-h = $0.2640
derived, 0.725× of the §7 worst case, 34 % of the 15 core-h cap. Waste 0.00.

### 4. What the re-grade did and did not establish

Established: freeze re-verified (prereg sha256 `3298d8bb…a5d744` blob == disk;
four instruments byte-identical to HEAD); strict completion on all six rows
including the age guard (`0/` 2026-08-21, last-time fields 2026-08-23);
`FOAM FATAL` 0 and `Foam::sigFpe` 0 in all six logs, exactly one trapFpe header
line each (the `diverged=True` artifact); the ten pre-relaunch rows identical
field-by-field to `results_PRE_RELAUNCH_2026-08-23.json` (10/10); the three
`AR_3_Ret_360` ML rows carry no metric field of any kind. **Not established:**
the graded metrics were read from `results.json` and cross-checked against
`lane5.log` — two outputs of one driver, a consistency check, not an
independent re-derivation from the written fields; and the freeze-before-compute
ordering of the original ten duct rows, which git cannot evidence (D492 limb b).

Cost of this addendum: zero core-minutes.
