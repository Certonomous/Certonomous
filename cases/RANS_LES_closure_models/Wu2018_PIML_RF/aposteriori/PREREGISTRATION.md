# PREREGISTRATION - a-posteriori re-solve of the Wu 2018 PIML random forest

Written **before any solve**. Frozen on completion; every later departure goes in
a dated "Departures" section of `RESULTS.md`, never by editing this file.

Date written: 2026-08-21. Lane 2 of two (Lane 1 = CLOSURE-REPRO, Kaandorp TBRF).

## 0. Why this test exists

The a-priori result (`../RESULTS.md`) is a **PASS**: the forest cuts `b_rms` from
SST's 0.4138 to **0.2213-0.2225** pooled over the 8 held-out cases, beating SST on
7 of 8 and the train-mean constant on the same 7. That number **bounds nothing
about the solved flow**. The map from `b` to `U` runs through the momentum balance
and is not monotone, and the paper that says so quantitatively is on disk and
verified: Wu, Xiao, Sun & Wang, *RANS Equations with Explicit Data-Driven Reynolds
Stress Closure Can Be Ill-Conditioned*, arXiv:1803.05581v3 (JFM 869:553-586, 2019).
**This is the test that decides whether the a-priori PASS meant anything.**

## 1. Solver: the lab's existing injection model. No new solver is being written

Read before writing this file:
`/home/ubuntu/Certonomous/sdk/openfoam/sparta/spartaTurbulenceModels/kOmegaSSTCorrected.{H,C}`.

It is stock v2606 `kOmegaSST` augmented by two static fields read at start time,
and it reduces **exactly** to stock `kOmegaSST` when both are zero. It does
precisely what this test needs and **it can take a `b^Delta` with `R = 0`**, so
there is no gap and no minimal change to cost.

**Two interface corrections to the note I was sent** (verified in the source, both
would have been hard failures):

1. The fields are named **`kDeficit`** and **`bijDelta`**, *not* `R` and
   `bijDelta`. Both are `IOobject::MUST_READ`
   (`kOmegaSSTCorrected.C` lines 69-93), so a wrong filename aborts the run.
2. `kDeficit` must still be **present** even when unused; `R = 0` is expressed by
   writing a `uniform 0` `kDeficit` field, not by omitting it. (`RScale` in
   `kOmegaSSTCorrectedCoeffs` would also switch it off; we do not rely on it, so
   the coefficients stay at their defaults `RScale = bScale = 1`.)

Run configuration, registered: `simpleFoam`, `libs ("libspartaTurbulenceModels.so")`
(built, present at `$FOAM_USER_LIBBIN/libspartaTurbulenceModels.so`),
`RASModel kOmegaSSTCorrected`. `sdk/` and the W2 run directories are **read-only**
to this lane. Case copies live at
`/home/ubuntu/closure-data/aposteriori/wu2018/<case>/`, outside the repo.

### 1.1 What is frozen and what is transported - registered

* **`k` and `omega` are TRANSPORTED**, not frozen. This is a full SST solve with
  an added anisotropy; both transport equations are integrated to convergence.
* **`bijDelta` is FROZEN** at the value injected at start time. It is not
  re-predicted as the flow evolves.
* **`nu_t` is LIVE.** The model realises
  `b_total = -(nu_t/k) S + bijDelta` with `nu_t`, `k`, `S` taken from the current
  iterate, so the *linear* part of the anisotropy is implicit and updates while
  the *nonlinear* part stays fixed. That is Wu 2018's own prescription and the
  conditioning fix their companion paper argues for.

**A consequence that must be stated before the run, not discovered after it:**
because `bijDelta` is frozen while `nu_t` and `S` move, the converged `b_total`
is **not** the `b` the forest predicted. The a-priori `b_rms` of 0.2213 is
therefore not recoverable from the converged solution even in principle, and no
claim in `RESULTS.md` will assert otherwise.

### 1.2 The injected field, exact formula and sign convention

The solver's reconstruction (`kOmegaSSTCorrected.H`, and `.C` line 315) is

```
tauijRecon = (2/3) k I - 2 nu_t S + 2 k bScale bijDelta
```

so, with `b = tau/(2k) - I/3` and `bScale = 1`,

```
b_total = -(nu_t/k) S + bijDelta          <- matches Schmelzer et al. 2020 eq. (3)
```

The forest's regression target is `Delta b = b_LES - b_RANS` with
`b_RANS = -(nu_t^base/k^base) S^base` from the shipped converged SST fields
(`../run_rf.py`, `dB = to6(bL - bR)`). Those two definitions coincide at the
baseline state, so

> **`bijDelta` := the forest's predicted `Delta b`, injected directly, no
> transformation and no sign flip.**

**Registered pre-solve gate G0 (sign and convention check).** Before any solve,
reconstruct `b_total` from the shipped baseline `nu_t`, `k`, `S` plus the injected
`bijDelta` and compare against the forest's own `b_pred = b_RANS + Delta b`. They
must agree to **relative L2 < 1e-10**. If they do not, the sign or convention is
wrong and **no solve is launched**. The measured value is reported whatever it is.

## 2. Cases, and one that is BLOCKED

| Case | cells | status |
|---|---|---|
| `AR_1_Ret_360` | 3,025 | **in scope** - stock `kOmegaSST`, drop-in swap |
| `AR_3_Ret_360` | 8,644 | **in scope** - same |
| `CBFS13700` | 21,000 | **in scope** - the lab's `cbfs_prop` case is a working `kOmegaSSTCorrected` template |
| `NASA_2DWMH` | 51,626 | **BLOCKED - see below** |

**The hump is blocked, and the reason is not compute.** Its shipped case runs
`RASModel AugmentedkOmegaSST` from `libfrozenIncompressibleTurbulenceModels.so`,
and **that library does not exist anywhere on this machine**
(`$FOAM_USER_LIBBIN`, `$FOAM_LIBBIN`, `$FOAM_SITE_LIBBIN` all checked). Options,
costed:

* **(a) Solve it under `kOmegaSSTCorrected` with zero corrections and use *that*
  as the baseline.** ~0.5 core-h. Honest, but it is then **not** the shipped SST
  baseline that `BASELINES.md` and the a-priori study score against, so the hump
  row stops being comparable to the other three cases and to Lane 1.
* **(b) Obtain or rebuild `AugmentedkOmegaSST`.** Not costed - the source is not
  on this machine and its differences from stock SST are unknown, so any estimate
  would be invented.

**Registered decision: the hump is reported as BLOCKED**, with the missing library
named, and option (a) is *not* silently substituted. If budget remains after the
three in-scope cases, option (a) may be run as an explicitly labelled
`hump-VARIANT-nonComparableBaseline` and reported separately; it can never fill
the hump row of the main table.

## 3. Four configurations per case

| Tag | `bijDelta` injected | purpose |
|---|---|---|
| **BASE** | none - the shipped converged SST solution, no solve re-run | the comparator every row is measured against |
| **TRUTH** | `b_LES - b_RANS` from the shipped `tauij_LES`, `k_LES` | the **ceiling**: the best any perfect anisotropy predictor could do through this injection path |
| **MEAN** | `b_mean - b_RANS`, `b_mean` the Charter-2c train-mean constant (`BASELINES.md` sec. 6.4) | the trivial comparator that already beats SST a-priori on 8 of 8 |
| **ML** | the forest's `Delta b`, **3 seeds** (0, 1, 2) | the thing under test |

`kDeficit = uniform 0` in all injected configurations.

### 3.1 Registered ceiling threshold - when this test is NOT A RESULT

**If TRUTH does not cut `U_rms` by at least 50% relative to BASE on a case, that
case is reported NOT A RESULT** and its ML row is not interpreted. Rationale: if
injecting the *true* anisotropy through this path cannot move the velocity field,
the path is not capable of expressing the correction and nothing about the forest
can be learned from it. The 50% figure is registered now.

## 4. Metrics - `BASELINES.md` sec. 1, on the same cells

Per case x configuration:

* **`U_rms`** = `sqrt(mean(|U - U_LES|^2)) / mean(|U_LES|)`; **`U_mae`** likewise.
* **RMS `div(U)`**, normalised as `RMS(div U) * L / U_bulk` (`L` = case reference
  length from `caseDef`/`transportProperties`, `U_bulk` from the LES field).
  Registered prediction: at solver tolerance this should be **at or below 1e-6**
  for every converged configuration, i.e. three to four orders of magnitude below
  the ~10% the lab's *post-hoc* (non-re-solved) correction incurs
  (`METHOD.md` sec. 6). **A solved field that does not satisfy continuity to
  <= 1e-4 is reported as not converged**, whatever its `U_rms`.
* **Ducts:** in-plane secondary-flow magnitude as % of bulk. Registered
  comparators: `AR_1_Ret_360` DNS **1.508%** mean / 4.759% max, SST **3.96e-16**;
  `AR_3_Ret_360` DNS **1.411%** / 4.595%, SST **7.58e-16**.
* **CBFS13700:** `x_reatt` against LES **4.241** (SST **5.891**), `x_sep` against
  LES 0.915 (SST 0.741), by the first-cell-row sign criterion of `BASELINES.md`.
* **Realisability** of the injected `b_total` at iteration 0 and of the converged
  `b_total`, as the fraction outside the barycentric triangle, reported beside the
  truth's own rate (`AR_1_Ret_360` 1.59%, `AR_3_Ret_360` 0.42%, `CBFS13700` 0.00%).

Registered BASE values (`sst_baseline_metrics.json`, md5
`4fc917f2300bcada2fa6eb25f454e9b5`): `U_rms` **0.1985** (`AR_1_Ret_360`),
**0.1846** (`AR_3_Ret_360`), **0.0516** (`CBFS13700`).

## 5. Hypotheses, falsifiers, and the verdict ladder

* **H1** - ML `U_rms` **below** BASE `U_rms` by more than the ML seed spread, on a
  case whose TRUTH row passed the sec. 3.1 ceiling threshold.
* **H2** - ML `U_rms` **below** MEAN `U_rms`.
* **H3** - ML `U_rms` within a factor **2.0** of the TRUTH ceiling
  (registered factor).

Verdicts, from the fixed vocabulary:

* **PASS** - H1 and H2 and H3 hold on at least 2 of the 3 in-scope cases.
* **GATE REACHED** - H1 and H2 hold but H3 does not (beats the baselines, but far
  from what a perfect predictor achieves through the same path).
* **GATE FAIL** - H1 fails on 2 or more in-scope cases (the a-priori improvement
  does not survive the solve); **or any injected configuration diverges or fails
  to converge**, in which case the residual history is recorded and reported.
* **NOT A RESULT** - the TRUTH ceiling threshold of sec. 3.1 is not met.
* **BLOCKED** - `NASA_2DWMH`, per sec. 2.

**Explicit falsifiers, registered:**

1. If ML `U_rms` > BASE `U_rms` on the ducts or CBFS, then **an a-priori `b_rms`
   improvement of 2x did not survive being solved**, and that is the headline
   finding, reported as GATE FAIL and not retried with a different blending.
2. If MEAN `U_rms` <= ML `U_rms`, the forest has added nothing a constant tensor
   does not, a-posteriori.
3. If TRUTH itself makes `U_rms` **worse** than BASE on any case, the injection
   path is reported as unable to express the correction on that case, and every
   ML row for it is void.

## 6. Numerics, bounding and stopping - all registered

* **Convergence:** initial residuals of `Ux, Uy, Uz, p, k, omega` all
  **< 1e-6**, sustained for 100 consecutive iterations.
* **Stagnation test:** if the maximum initial residual fails to decrease by 10%
  over 5,000 consecutive iterations, the run stops and is recorded as *stagnated*
  with its residual history; stagnation is **not** silently treated as converged.
* **Hard iteration caps:** ducts **200,000**; CBFS **40,000**.
* **Wall-clock timeout inside the script:** **3,600 s per solve**, via `timeout`.
  No process ever needs to be killed by hand.
* **Under-relaxation and blending:** the case's own shipped `fvSolution` values
  are used unchanged. **No blending or clipping of `bijDelta` is applied: the
  registered clipping factor is 1.0 (i.e. none), and the injected field is used
  raw.** If a run diverges, a clipped or ramped variant may be run **only** as a
  separate, explicitly labelled configuration; the raw result is reported
  regardless and is the one the verdict is taken on.
* Every solve runs in the background with its own log file; logs are the evidence.

## 7. Compute

15 solves (3 cases x [TRUTH, MEAN, ML x3]); BASE needs no solve. At ~0.1-0.3
core-h each: **estimate 2.5-4 core-hours**. **Lane cap: 15 core-hours**; if the
running total passes 12, remaining ML seeds are dropped in favour of completing
TRUTH and MEAN on every case, and the reduction is reported.

## 8. What this test cannot see

* **It cannot recover the a-priori number.** `bijDelta` is frozen while `nu_t`
  moves (sec. 1.1), so the converged `b` is not the predicted `b`.
* **It cannot separate model error from injection-path error** except through the
  TRUTH row, which is exactly why TRUTH is registered as a configuration and as a
  gate.
* **It says nothing about the NASA hump**, the one case the a-priori study failed,
  because that case is BLOCKED on a missing library (sec. 2). The a-priori failure
  there therefore remains untested a-posteriori.
* **Three in-scope cases, two of them ducts**, is a narrow basis; the ducts share
  a flow class and differ only in aspect ratio.
* **No uncertainty band on the truth.** The benchmark ships none, so no margin
  here can be compared against data uncertainty.
* **`k` and `omega` are transported with an added production term but their own
  model constants are unchanged**, so any error attributable to the SST transport
  equations themselves is present in every configuration including TRUTH.

---

# ADDENDUM, 2026-08-21, post-freeze. Nothing above is altered.

Added after the freeze, before any solve, at the supervisor's request and because
the additions strictly tighten the test. Everything above stands as written.

## A1. Clarification: the frozen G0 is not the gate the note describes

The note warns against a gate of the form *"zero-correction re-solve vs the
shipped field, rel-L2 < 1e-10"*, on the ground that the shipped benchmark fields
are not converged to 1e-10 (Lane 1 measured an initial `Ux` residual of **1.8e-5**
on a zero-correction restart of `AR_1_Ret_360`). That is a correct warning about a
different gate.

**The frozen G0 (sec. 1.2) contains no solve.** It is pure algebra on the injected
field: reconstruct `b_total = b_RANS + bijDelta` from the shipped baseline
`nu_t`, `k`, `S` and check it equals the forest's `b_pred`, which tests only that
the sign and the convention of the injected tensor are right. It is unaffected by
the benchmark's convergence level. **It has been run and it PASSED**: worst
relative L2 over all 15 injected fields = **1.02e-16**. Nothing was reported
BLOCKED on this account and no solver defect was inferred.

## A2. Two additional gates adopted from Lane 1 (G0a, G0b)

These test the *solver setup*, which the frozen G0 does not, and are adopted
verbatim in substance so the two lanes are comparable:

* **G0a - the correction terms are inert when zero.** Run stock `kOmegaSST` and
  `kOmegaSSTCorrected` with `kDeficit = 0`, `bijDelta = 0`, from the **same**
  shipped fields for the **same** fixed **200** iterations. Registered threshold:
  relative L2 difference in `U` **< 1e-10**. This isolates the added terms from
  everything else. Failure here means the model is not a faithful superset of
  stock SST and **no injected result may be reported**.
* **G0b - the case setup reproduces the published baseline.** Run the NULL
  (zero-correction) configuration to convergence and compare `U_rms` against
  `BASELINES.md` for that case. Registered threshold: **< 1e-3 absolute**.
  Failure here means our case copy differs from the benchmark's own solve, and
  every row for that case is reported with that offset stated.

**NULL becomes a fifth configuration** in the sec. 3 table, run on every in-scope
case. It is not merely a check: it is the correct comparator for the injected
runs, because it shares their solver, mesh copy, stopping rule and iteration
count. Where NULL and BASE differ, **NULL is used for the H1 comparison** and the
BASE-vs-NULL gap is reported as the benchmark's own convergence offset.

## A3. Cross-lane reporting of the ceiling

The frozen ceiling threshold of sec. 3.1 stays at **50%** as registered. Lane 1
registered **30%**, reasoning that a `b`-only ceiling with no `k`-deficit term
must be weaker than Schmelzer et al.'s 52% (which had both corrections). That
reasoning is sound and applies here too, since this lane also injects `b` alone
with `kDeficit = 0`. **Both readings will be reported beside every TRUTH row**:
the pass/fail against the frozen 50% carries the verdict, and the 30% reading is
printed alongside so the lanes can be read side by side.

## A4. Realisability reporting tolerance, fixed after a measurement

The injected-field realisability numbers are reported at **tol = 1e-6**, not at
`tol = 0`. Reason, measured while generating the fields: on `CBFS13700`, 4.6% of
the truth cells have a minimum barycentric coordinate of **exactly -2.98e-08**
- one float32 ulp - i.e. they are exact two-component states in the shipped
float32 data, and promoting them to float64 exposes a one-ulp negative. At
`tol = 0` they are counted as violations and the truth appears 4.6%
non-realisable on a case where it is not. `tol = 1e-6` is far below any physical
anisotropy scale and far above the float32 ulp. Both numbers are recorded in
`fields_report.json` (`viol_injected_b_total` and `..._tol0`).

## A5. In-sample caveat on CBFS13700, stated before the solves

`CBFS13700` is a **training** case of the forest's E1 split; `AR_1_Ret_360` and
`AR_3_Ret_360` are strict TEST cases. The CBFS ML rows are therefore in-sample and
carry no generalisation claim. They are still run, because an in-sample
a-posteriori failure would be a stronger negative result than an out-of-sample
one, but no PASS may rest on CBFS alone.
