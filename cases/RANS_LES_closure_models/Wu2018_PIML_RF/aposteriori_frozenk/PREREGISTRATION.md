# PREREGISTRATION — b^Delta injection with FROZEN k

Written **before any solve**. Frozen on completion; departures go in a dated
section of `RESULTS.md`, never by editing this file. Date: 2026-08-21.

**This is a NEW registered test, not a continuation.** The prior lane
(`../aposteriori/`) returned **NOT A RESULT**: injecting the *true* anisotropy
with `kDeficit = 0` made `U_rms` **57-63% worse** on all three cases, because
transported `k` collapsed to **0.33x** baseline on the duct. This lane tests
whether that mechanism is the whole explanation.

## 0. THE GAP: both registered options are unavailable as-is

I read the solver before designing. Neither option in the task can be run
without new code, and the evidence is specific.

**Option (ii) — `kOmegaSSTCorrected` with `k` and `omega` frozen: NOT SUPPORTED.**
`kOmegaSSTCorrected.C` overrides exactly two methods, `read()` (line 121) and
`correct()` (line 184), plus `divDevReff`/`divDevRhoReff`. There is **no freeze
switch** — no `Switch`, no `solveK`/`solveOmega` flag anywhere in the class.
`correct()` unconditionally solves both transport equations.

**Option (i) — `kOmegaSSTFrozen` carrying the data stress into momentum: NOT
SUPPORTED.** `kOmegaSSTFrozen` overrides only `correct()` (line 117) and adds
`verifyKEquation()` (line 231). **It does not override `divDevReff` or
`divDevRhoReff`.** It therefore inherits the stock Boussinesq momentum coupling,
and the `tauij` field it reads (`MUST_READ`, line 51) is used **only** to form
`b_ij` for the omega-equation production and the `bijDelta` output — it never
reaches the momentum equation. Running `simpleFoam` with it would solve `U`
against `-nu_t grad U` with `nu_t` from frozen `k` and solved `omega`, which is
not the prescribed-stress test the design intends.

**`sdk/openfoam/sparta/` is read-only to this lane** and is not modified.

### 0.1 The costed minimal change, registered before writing it

A **new, lane-local** turbulence model `kOmegaSSTCorrectedFrozenK`, deriving from
`kOmegaSSTCorrected` and overriding `correct()` only:

* do **not** solve the `k` or `omega` equations; leave both fields at their
  start-time values;
* update `nu_t` from those frozen fields via the inherited `correctNut()`, so the
  blending functions and the `a1` limiter remain the stock ones;
* inherit `divDevReff`/`divDevRhoReff` **unchanged** from `kOmegaSSTCorrected`,
  so momentum sees `-nu_t(...) + div(2 k bijDelta)` with `k` now constant.

Cost: ~120 lines in a new library `libwu2018FrozenK.so` under this case
directory; ~1 h of work; **< 0.05 core-hours** of compute to build. Risk: the
`nu_t` update path must be exercised without the solves — covered by gate G0a.
Nothing in `sdk/` changes; the parent class is used as-is.

**If G0a fails, this lane reports BLOCKED and does not proceed.**

## 1. What is injected, exactly

`kOmegaSSTCorrected` realises (its `divDevReff`, and `.C` line 315):

```
tau = (2/3) k I - 2 nu_t S + 2 k bScale bijDelta        =>  b_total = -(nu_t/k) S + bijDelta
```

with `k` from the current iterate — **which is now frozen**, so the injected
extra stress `2 k bijDelta` is a fixed field for the whole solve. This is the
property the lane exists to obtain.

**Sign convention, registered:** `bijDelta := Delta b = b_LES - b_RANS`, with
`b_RANS = -(nu_t^base/k^base) S^base` from the shipped converged SST fields —
identical to `../aposteriori/`, where gate G0 verified it at **1.24e-16**.
`kDeficit = uniform 0` (`MUST_READ`, so it must be present, not omitted).

**Two frozen-`k` arms**, registered as separate configurations:

* **arm S** — `k` frozen at the **shipped SST** `k`. The stress is then exactly
  what the a-priori study scored, and `b_total` at every iteration equals the
  model's prediction.
* **arm L** — `k` frozen at **`k_LES`**. This removes the SST `k` error as well,
  and is the true ceiling for a `b`-only correction.

Arm L is the stricter test of H0; arm S is the one a deployed model could
actually use, since `k_LES` is not available at prediction time. **Both are run
and both are reported; no verdict rests on arm L alone.**

## 2. Gates, all before any scored solve

* **G0 (algebra, no solve).** Reconstruct `b_total = b_RANS + bijDelta` from the
  shipped baseline and check it equals the forest's `b_pred`. Threshold
  **rel-L2 < 1e-10**. (Already passed at 1.24e-16 for these exact fields; re-run
  and re-reported here.)
* **G0a (identity, the new model).** With `bijDelta = 0`, `kDeficit = 0` and `k`,
  `omega` frozen at the shipped values, `kOmegaSSTCorrectedFrozenK` must
  reproduce a momentum-only solve at fixed `nu_t`: `k` and `omega` must be
  **bitwise unchanged** after 200 iterations, and `nu_t` must equal the value
  computed from the frozen fields to **rel-L2 < 1e-12**. Failure => **BLOCKED**.
* **G0b (comparator honesty, N-B23).** NULL = zero-correction run of the **same**
  model with the same freezing and stopping rule. Every row reports NULL beside
  the shipped BASE from `BASELINES.md`, with `NULL - BASE` named.

## 3. Configurations and cases

Cases: `AR_1_Ret_360`, `AR_3_Ret_360`, `CBFS13700` (`NASA_2DWMH` remains
**BLOCKED** on the missing `libfrozenIncompressibleTurbulenceModels.so` /
`AugmentedkOmegaSST`, as established in `../aposteriori/PREREGISTRATION.md` sec. 2).

Per case: **BASE** (shipped, no re-solve), **NULL** (`bijDelta = 0`, frozen `k`),
**TRUTH** (`b_LES - b_RANS`), **MEAN** (train-mean constant), **ML** (forest,
seeds 0/1/2) — each in **arm S** and **arm L**.

## 4. The ceiling gate: 30%, and why 30 rather than 50

**Registered: TRUTH must cut `U_rms` by >= 30% relative to NULL.** The prior lane
registered 50% and I am lowering it here, with the reason recorded in advance:
this injection supplies **`b` only, with `kDeficit = 0`**, whereas Schmelzer et
al. reach `eps(U)/eps(U_0) = 0.0017` with **both** `b^Delta` and `R`. A `b`-only
correction cannot be expected to match a two-correction result, so a 50%
threshold would fail a configuration that is working as designed. **The 50%
reading is reported beside every TRUTH row** so the two lanes stay comparable and
neither threshold is hidden.

## 5. Predictions and falsifiers

* **H0 (the mechanism test).** With `k` frozen, TRUTH passes the 30% gate.
  **Falsifier, registered: if TRUTH still fails with `k` frozen, the `k`-collapse
  explanation of the prior lane's NOT A RESULT was incomplete**, and this lane
  reports that as its finding rather than reaching for a further fix.
* **H1** ML `U_rms` < NULL by more than the ML seed spread.
* **H2** ML < MEAN.
* **H3** ML within a factor **2.0** of TRUTH.

Verdicts: **PASS** = H0 and H1 and H2 and H3 on >= 2 of 3 cases. **GATE REACHED**
= H0 passes, H1/H2 hold, H3 does not. **GATE FAIL** = H0 passes but H1 fails on
>= 2 cases, or any injected run diverges/does not converge (residual history
recorded). **NOT A RESULT** = H0 fails (ceiling unmet). **BLOCKED** = G0a fails,
or the hump.

## 6. Reported for every row, whatever the outcome

`U_rms`, `U_mae` (vs LES, `BASELINES.md` sec. 1 definitions); **transported-vs-frozen
`k`** (`k`/`k`base and `k`/`k_LES`, which must be exactly 1.000 and constant by
construction — a drift is a bug and is reported as one); `b_rms` of the **injected**
field against `b_LES`; duct secondary-flow magnitude as % of bulk (DNS 1.508% /
1.411%, SST ~4e-16); `CBFS13700` `x_reatt` (LES **4.241**, SST **5.891**);
**normalised RMS `div(U)`** with the registered prediction `<= 1e-6` at solver
tolerance and **NOT CONVERGED** reported if `> 1e-4`; realisability of the
injected and converged `b` at `tol = 1e-6` beside the truth's own rate; **NULL
state** (CONVERGED / STAGNATED-NOT-CONVERGED with iteration count and final
residuals) and shipped BASE beside it, with `NULL - BASE` named.

## 7. Numerics, bounding, stopping

Convergence: initial residuals of `Ux, Uy, Uz, p` below **1e-6** sustained 100
iterations (`k`, `omega` are frozen and excluded from the criterion — registered,
because including a frozen field's residual would be meaningless). Stagnation:
no 10% drop in the max initial residual over 5,000 iterations => stop, record,
**not** counted as converged. Caps: ducts **200,000**, CBFS **40,000**.
`timeout 3600` per solve inside the script. `writeInterval 1000`, `purgeWrite 2`
**from the start** — the prior lane had to patch this mid-run (its D-1). No
clipping or ramping of `bijDelta`: registered factor **1.0**.

## 8. Compute

Build < 0.05. 3 cases x 5 configurations x 2 arms = 30 solves at ~0.05-0.3
core-h => **1.5-6 core-hours**. **Cap 10.** Past 8, arm L is dropped in favour of
completing arm S, and the reduction is reported.

## 9. What this cannot see

* **It cannot restore the `k` error.** Arm S freezes `k` at the SST value, which
  is itself wrong (`k`/`k_LES` = 0.61 on `AR_1_Ret_360`); arm L removes that but
  uses information unavailable at prediction time. Neither arm is a deployable
  configuration; both are diagnostics.
* **Frozen `k` breaks the energy budget it was solving.** The `k` equation is
  simply not enforced, so the result answers "does the momentum equation use a
  prescribed anisotropy well" and **not** "is this a consistent turbulence model".
* **`NASA_2DWMH` stays BLOCKED**, so the one case the a-priori study failed
  remains untested a-posteriori in both lanes.
* **`CBFS13700` is in-sample** for this forest; only the two ducts are held out.
* **No uncertainty band on the truth.**
