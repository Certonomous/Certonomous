# RESULTS — b^Delta injection with FROZEN k

Preregistration: `PREREGISTRATION.md`, frozen before any solve, unedited.
Scored by `score.py` from `/home/ubuntu/closure-data/aposteriori_frozenk/wu2018/scores.json`.

## VERDICT: **NOT A RESULT** — the ceiling gate failed on both arms and all three cases, and the registered falsifier has fired

`PREREGISTRATION.md` sec. 5 registered H0 and its falsifier in advance:

> **"if TRUTH still fails with `k` frozen, the `k`-collapse explanation of the
> prior lane's NOT A RESULT was incomplete"**

**It still fails. The k-collapse explanation was incomplete.** That is this
lane's finding.

## 1. H0 — the ceiling gate (registered 30%, with the 50% reading beside)

| case | arm | NULL `U_rms` | TRUTH `U_rms` | change | gate 30% | gate 50% |
|---|---|---|---|---|---|---|
| `AR_1_Ret_360` | S | 0.1991 | **0.2109** | **+5.9%** | **FAIL** | **FAIL** |
| `AR_1_Ret_360` | L | 0.3686 | **0.2869** | **-22.2%** | **FAIL** | **FAIL** |
| `AR_3_Ret_360` | S | 0.1880 | **0.1941** | **+3.2%** | **FAIL** | **FAIL** |
| `AR_3_Ret_360` | L | 0.3556 | **0.2530** | **-28.9%** | **FAIL** | **FAIL** |
| `CBFS13700` | S | 0.0516 | **0.1085** | **+110.2%** | **FAIL** | **FAIL** |
| `CBFS13700` | L | 0.0498 | **0.1179** | **+136.6%** | **FAIL** | **FAIL** |

**Six of six fail.** Freezing `k` at the shipped SST value (arm S) leaves TRUTH
*worse* than doing nothing, on all three cases. Freezing at `k_LES` (arm L) — which
also removes the SST `k` error, and uses information unavailable at prediction
time — recovers a real improvement on the two ducts (**−22.2%**, **−28.9%**) but
both fall short of the registered 30%, and CBFS gets **worse by 137%**.

Per `PREREGISTRATION.md` sec. 5, a failed ceiling makes every case **NOT A
RESULT** and **voids H1, H2 and H3**. They are tabulated below because they were
run, not because they carry a claim.

## 2. Gate G0a — the freeze itself: PASS, bitwise

With `bijDelta = 0`, `kDeficit = 0`, 200 iterations:

| case | `k` bitwise unchanged | `omega` bitwise unchanged | max\|Δk\| | max\|Δω\| |
|---|---|---|---|---|
| `AR_1_Ret_360` | **yes** | **yes** | **0.000e+00** | **0.000e+00** |
| `AR_3_Ret_360` | **yes** | **yes** | **0.000e+00** | **0.000e+00** |
| `CBFS13700` | **yes** | **yes** | **0.000e+00** | **0.000e+00** |

And the freeze held for every scored run: **arm S `k`/`k`base = 1.000 exactly**;
**arm L `k`/`k_LES` = 1.000000** (max\|k − k_LES\| = 5.0e-04 on the ducts, which is
the float32 write precision of the field, and 5.0e-14 on CBFS).

The injected stress reached momentum: `max|U_truth − U_null| = 8.89` on
`AR_1_Ret_360`. The model does what it was built to do.

## 3. Per case and configuration


### AR_1_Ret_360 — n = 3,025, DNS secondary flow **1.508%** of bulk

**Comparators.** Shipped **BASE** `U_rms` = **0.1985**. **S_null** = STAGNATED-NOT-CONVERGED at 200,000 iters, residuals `Ux`=8.0e-16, `Uy`=2.2e-01, `Uz`=1.7e-01, `p`=1.4e-01. **NULL − BASE = +0.0006** (N-B23).

| cfg | `U_rms` | `U_mae` | sec% | `k`/`k`base | `b_rms` vs LES | viol | continuity | gate 1e-4 | iters | converged |
|---|---|---|---|---|---|---|---|---|---|---|
| `S_null` | **0.1991** | 0.1413 | 0.0000 | 1.000 | 0.5978 | 0.0000 | 1.10e-13 | ok | 200,000 | **no** |
| `S_truth` | **0.2109** | 0.1649 | 0.5888 | 1.000 | 0.0450 | 0.0142 | 5.96e-05 | ok | 290 | yes |
| `S_mean` | **0.5679** | 0.4544 | 1.5461 | 1.000 | 0.4371 | 0.0000 | 4.26e-05 | ok | 760 | yes |
| `S_ml_s0` | **0.3087** | 0.2246 | 0.4962 | 1.000 | 0.1346 | 0.0003 | 1.23e-04 | **BREACH** | 466 | **NOT CONVERGED** |
| `S_ml_s1` | **0.3124** | 0.2273 | 0.5161 | 1.000 | 0.1347 | 0.0000 | 1.57e-04 | **BREACH** | 490 | **NOT CONVERGED** |
| `S_ml_s2` | **0.3183** | 0.2308 | 0.4946 | 1.000 | 0.1356 | 0.0000 | 1.67e-04 | **BREACH** | 478 | **NOT CONVERGED** |
| `L_null` | **0.3686** | 0.2658 | 0.0000 | 1.627 | 0.5942 | 0.0000 | 8.65e-14 | ok | 200,000 | **no** |
| `L_truth` | **0.2869** | 0.2011 | 0.4334 | 1.627 | 0.0443 | 0.0138 | 5.51e-05 | ok | 620 | yes |
| `L_mean` | **0.3626** | 0.3176 | 3.1125 | 1.627 | 0.4392 | 0.0000 | 8.83e-05 | ok | 524 | yes |
| `L_ml_s0` | **0.3506** | 0.2599 | 0.9849 | 1.627 | 0.1349 | 0.0000 | 2.16e-04 | **BREACH** | 721 | **NOT CONVERGED** |
| `L_ml_s1` | **0.3503** | 0.2611 | 1.0100 | 1.627 | 0.1351 | 0.0000 | 2.20e-04 | **BREACH** | 710 | **NOT CONVERGED** |
| `L_ml_s2` | **0.3617** | 0.2683 | 0.9436 | 1.627 | 0.1357 | 0.0000 | 2.32e-04 | **BREACH** | 716 | **NOT CONVERGED** |

### AR_3_Ret_360 — n = 8,748, DNS secondary flow **1.411%** of bulk

**Comparators.** Shipped **BASE** `U_rms` = **0.1846**. **S_null** = STAGNATED-NOT-CONVERGED at 123,096 iters, residuals `Ux`=9.7e-16, `Uy`=3.7e-01, `Uz`=3.2e-01, `p`=2.6e-01. **NULL − BASE = +0.0035** (N-B23).

| cfg | `U_rms` | `U_mae` | sec% | `k`/`k`base | `b_rms` vs LES | viol | continuity | gate 1e-4 | iters | converged |
|---|---|---|---|---|---|---|---|---|---|---|
| `S_null` | **0.1880** | 0.1425 | 0.0000 | 1.000 | 0.5530 | 0.0000 | 9.43e-13 | ok | 123,096 | **no** |
| `S_truth` | **0.1941** | 0.1613 | 0.4632 | 1.000 | 0.0466 | 0.0033 | 1.06e-05 | ok | 1,534 | yes |
| `S_mean` | **0.7283** | 0.6299 | 1.0316 | 1.000 | 0.4088 | 0.0000 | 1.34e-05 | ok | 4,668 | yes |
| `S_ml_s0` | **0.2767** | 0.2105 | 0.4428 | 1.000 | 0.1240 | 0.0000 | 1.59e-05 | ok | 1,836 | yes |
| `S_ml_s1` | **0.2774** | 0.2105 | 0.4418 | 1.000 | 0.1242 | 0.0000 | 1.46e-05 | ok | 1,815 | yes |
| `S_ml_s2` | **0.2786** | 0.2113 | 0.4698 | 1.000 | 0.1258 | 0.0000 | 1.82e-05 | ok | 1,898 | yes |
| `L_null` | **0.3556** | 0.2786 | 0.0000 | 1.683 | 0.5489 | 0.0000 | 1.91e-12 | ok | 122,898 | **no** |
| `L_truth` | **0.2530** | 0.1880 | 0.4094 | 1.683 | 0.0458 | 0.0033 | 1.37e-05 | ok | 2,619 | yes |
| `L_mean` | **0.5296** | 0.4774 | 2.1190 | 1.683 | 0.4062 | 0.0000 | 1.78e-05 | ok | 5,313 | yes |
| `L_ml_s0` | **0.3348** | 0.2490 | 0.5254 | 1.683 | 0.1244 | 0.0000 | 1.96e-05 | ok | 3,352 | yes |
| `L_ml_s1` | **0.3374** | 0.2505 | 0.5280 | 1.683 | 0.1246 | 0.0000 | 1.81e-05 | ok | 3,426 | yes |
| `L_ml_s2` | **0.3373** | 0.2500 | 0.5590 | 1.683 | 0.1262 | 0.0000 | 2.22e-05 | ok | 3,248 | yes |

### CBFS13700 — n = 21,000

**Comparators.** Shipped **BASE** `U_rms` = **0.0516**. **S_null** = CONVERGED at 12 iters, residuals `Ux`=2.0e-09, `Uy`=1.2e-08, `p`=1.4e-09. **NULL − BASE = -0.0000** (N-B23).

| cfg | `U_rms` | `U_mae` | sec% | `k`/`k`base | `b_rms` vs LES | viol | continuity | gate 1e-4 | iters | converged |
|---|---|---|---|---|---|---|---|---|---|---|
| `S_null` | **0.0516** | 0.0291 | -- | 1.000 | 0.3187 | 0.0000 | 5.66e-15 | ok | 12 | yes |
| `S_truth` | **0.1085** | 0.0620 | -- | 1.000 | 0.0403 | 0.0002 | 9.88e-14 | ok | 2,586 | yes |
| `S_mean` | **0.2732** | 0.1858 | -- | 1.000 | 0.3428 | 0.0027 | 2.59e-09 | ok | 22,757 | **no** |
| `S_ml_s0` | **0.0921** | 0.0520 | -- | 1.000 | 0.0494 | 0.0004 | 8.45e-14 | ok | 2,313 | yes |
| `S_ml_s1` | **0.0892** | 0.0502 | -- | 1.000 | 0.0488 | 0.0013 | 9.01e-14 | ok | 2,247 | yes |
| `S_ml_s2` | **0.0904** | 0.0510 | -- | 1.000 | 0.0491 | 0.0006 | 8.08e-14 | ok | 2,262 | yes |
| `L_null` | **0.0498** | 0.0297 | -- | 1.343 | 0.3229 | 0.0000 | 3.93e-14 | ok | 1,969 | yes |
| `L_truth` | **0.1179** | 0.0691 | -- | 1.343 | 0.0484 | 0.0070 | 1.49e-13 | ok | 3,849 | yes |
| `L_mean` | **0.2936** | 0.2102 | -- | 1.343 | 0.3526 | 0.0020 | 3.85e-13 | ok | 2,834 | yes |
| `L_ml_s0` | **0.0415** | 0.0188 | -- | 1.343 | 0.0536 | 0.0062 | 4.87e-14 | ok | 2,199 | yes |
| `L_ml_s1` | **0.0422** | 0.0195 | -- | 1.343 | 0.0549 | 0.0071 | 5.16e-14 | ok | 2,150 | yes |
| `L_ml_s2` | **0.0418** | 0.0190 | -- | 1.343 | 0.0542 | 0.0064 | 5.75e-14 | ok | 2,173 | yes |

## 4. The result that matters most, and it is not the ceiling

**On `CBFS13700` arm L the learned anisotropy beats both the baseline and the
true anisotropy.**

| CBFS13700, arm L | `U_rms` | `x_reatt` (LES **4.170**) |
|---|---|---|
| `L_null` | 0.0498 | 3.350 |
| **`L_ml_s0/1/2`** | **0.0415 / 0.0422 / 0.0418** | **3.022** |
| `L_truth` | 0.1179 | 9.088 |

The ML field is **16% better than NULL** in `U_rms` but FARTHER from the LES
reattachment (error 1.148 against NULL's 0.820 — NULL undershoots, ML undershoots
slightly more) [dated correction 2026-08-21: this sentence originally read "closer to the LES
reattachment", contradicting its own numbers], while the **exact** anisotropy is **137% worse** and puts
reattachment at 9.088 against a truth of 4.170.

A *less accurate* `b` produced a *better* velocity field than the exact one. That
is the ill-conditioning of the explicit-closure RANS operator in its purest
observable form — the claim of
`Wu2018_rans_explicit_closure_ill_conditioned.pdf` (arXiv:1803.05581v3), now
measured twice in this programme on the lab's own data, and it is **not**
explicable by the `k` budget, because `k` is frozen and exact here.

For contrast, `b_rms` against the LES orders the configurations exactly as
expected — TRUTH **0.0403–0.0484**, ML **0.0488–0.0549**, NULL **0.3187–0.3229**.
**The anisotropy ranking and the velocity ranking are inverted.** An a-priori
`b_ij` score does not merely fail to bound the solved field; on this case it
points the wrong way.

## 5. Secondary flow, recovered from a structural zero

| case | arm | NULL | TRUTH | ML | DNS |
|---|---|---|---|---|---|
| `AR_1_Ret_360` | S | 0.0000% | 0.589% | 0.494–0.516% | **1.508%** |
| `AR_1_Ret_360` | L | 0.0000% | 0.433% | 0.944–1.010% | **1.508%** |
| `AR_3_Ret_360` | S | 0.0000% | 0.463% | 0.442–0.470% | **1.411%** |
| `AR_3_Ret_360` | L | 0.0000% | 0.409% | 0.525–0.559% | **1.411%** |

Every injected configuration produces the secondary motion a linear
eddy-viscosity model cannot make at all. In arm L the **ML** field recovers
**63–67%** of the DNS magnitude on `AR_1_Ret_360` — more than TRUTH does — while
still being worse in `U_rms`. The three instruments disagree with each other, and
that disagreement is the honest summary of this lane.

## 6. Continuity gate, graded

Registered: `> 1e-4` ⇒ **NOT CONVERGED** whatever the `U_rms`. **Six rows breach
it**, all ML, all on `AR_1_Ret_360`: `S_ml_s0` 1.23e-04, `S_ml_s1` 1.57e-04,
`S_ml_s2` 1.67e-04, `L_ml_s0` 2.16e-04, `L_ml_s1` 2.20e-04, `L_ml_s2` 2.32e-04.
They are marked in the tables. Every TRUTH and NULL row is inside the gate, so
the H0 verdict rests only on rows that pass it.

Note the pattern: the breaches are exactly the configurations with the least
smooth injected field, on the smallest mesh (3,025 cells).

## 7. Realisability

Injected-field violation at `tol = 1e-6`, beside the truth's own rate:
TRUTH **0.0142** (`AR_1`, truth's own **0.0159**), **0.0033** (`AR_3`, own
**0.0042**), **0.0002–0.0070** (CBFS, own **0.0000**). ML **0.0000–0.0071**.
MEAN **0.0000–0.0083**. No configuration is materially less realisable than the
data it is built from.

## 8. Compute

Measured from `log.solve.done`, summed over every completed solve: **18,835 core-seconds
= 5.23 core-hours**, plus gate G0a (600 iterations over three cases) and one duct
`L_null` still executing. **Total ≈ 5.8 core-hours of the 10-hour cap.**
Arm L was **not** dropped: the registered trigger was 8 core-hours and it was
never approached. Nothing was killed by hand.

## 9. Departures from the frozen preregistration — dated 2026-08-21

* **D-1. Arm L had to be rebuilt before it could run at all.** All eighteen arm-L
  configurations died in one second on the first launch: the benchmark ships
  `k_LES` as `#include "interpolatedFields/k_internalField"`, and the case copy
  did not carry the include target. They exited `rc=1` while still writing
  `log.solve.done`, so a completion check counting `.done` files reported the arm
  as finished. Fixed by resolving the macro through `of_read.read_field` and
  writing a plain field into the **shipped `k` file's** header and boundary
  conditions, so the frozen field keeps valid BCs. **This is completing the
  registered run — arm L had never executed — not a re-run of a scored result.**
* **D-2. `tauijRecon` is never written by the frozen model.** That field is
  assembled inside `kOmegaSSTCorrected::correct()`, which
  `kOmegaSSTCorrectedFrozenK::correct()` deliberately does not call. Momentum is
  unaffected (`divDevReff` uses `bijDelta_` and `k_` directly, and the measured
  `max|U_truth − U_null| = 8.89` confirms the stress reached it), but the
  diagnostic output is absent. `b_total = −(nu_t/k) S + bijDelta` is therefore
  reconstructed in `score.py` from written fields. Caught because reading a
  `uniform` field raised an `IndexError` rather than silently returning zeros.
* **D-3. Duct `L_null` runs outlasted the first scoring pass.**
  `AR_1_Ret_360/L_null` has since run to its registered 200,000-iteration cap
  (2,202 s) and the tables are refreshed from that final state. Its `U_rms` is
  **0.3686 — unchanged** from the 113,379-iteration scoring, because the run is
  STAGNATED and the field had stopped moving; only the iteration count, wall time
  and continuity figure changed. `AR_3_Ret_360/L_null` is still executing and its
  row is reported from its last written state. Both were scorable throughout
  because `writeInterval 1000` was registered from the start for exactly this
  reason. Neither is a TRUTH row, and **the refresh confirms H0 and the verdict
  are unaffected**.

## 10. What this result cannot see

* **It cannot say the injection path is wrong in general.** The same solver with
  **both** corrections reaches the published `eps(U)/eps(U_0) = 0.00165` (lab W2 measurement 0.003331) [dated correction 2026-08-21: originally quoted 0.0017 as the lab's own] on PH10595
  (`verification/campaign/W2_SPARTA_FROZEN_CBFS.md`). What fails is `b`-only
  injection, which is all a `b_ij`-predicting model can supply.
* **Neither arm is deployable.** Arm S freezes `k` at a value that is itself
  wrong (`k`/`k_LES` = 0.61 on `AR_1_Ret_360`); arm L uses `k_LES`, unavailable at
  prediction time. Both are diagnostics.
* **Frozen `k` is not a turbulence model.** The `k` equation is simply not
  enforced, so this answers "does momentum use a prescribed anisotropy well" and
  not "is this consistent".
* **`NASA_2DWMH` remains BLOCKED** on the missing `AugmentedkOmegaSST` library —
  the one case the a-priori study failed is still untested a-posteriori.
* **`CBFS13700` is in-sample** for this forest (a training case of the E1 split).
  **The sec. 4 result carries no generalisation claim**; it is a statement about
  the solver's response to an injected field, not about the model's skill.
* **Three cases, two of them same-class ducts**, and no uncertainty band on the
  truth.


---

**Dated note appended 2026-08-21 — the NASA hump BLOCK is liftable by equivalence gate, and the gate PASSED.**
*Appended note; nothing above this line was edited.*

The hump's shipped baseline was blocked because `constant/turbulenceProperties`
selects **`AugmentedkOmegaSST`**, whose library is absent on this machine. That
model is not a mystery: `data/NASA_2DWMH/log.run` line 153 selects it and prints
its full coefficient dictionary — `baseline true`, `usekDeficit false`,
`usebijDelta false`, `useSigma false`, `modelbijDelta false`,
`modelkDeficit false`, `modelSigma false`, with every printed coefficient the
stock Menter SST value (`alphaK1 0.85`, `alphaOmega2 0.856`, `gamma1 0.555556`,
`beta1 0.075`, `betaStar 0.09`, `a1 0.31`, `b1 1`, `c1 10`, `F3 false`). It is a
SpaRTA-style corrected SST **run with every augmentation switched off**.

A preregistered equivalence gate
(`cases/RANS_LES_closure_models/NASA_hump_gate/`) tested that behaviourally:

* **B-G0a** (two-sided, 200 identical iterations) is **BLOCKED** — the shipped
  model cannot be instantiated here at all (`Unknown RAS model type
  AugmentedkOmegaSST`), which the preregistration registered as BLOCKED rather
  than failed.
* **B-G0b** (converged NULL against the published row) **PASSES**:
  `kOmegaSSTCorrected` with `bijDelta = 0`, `kDeficit = 0`, `omegaMin 0.1` and the
  shipped `fvOptions`, restarted from the shipped `2000/` field, **converged in
  156 iterations** to `U_rms` = **0.1261769** against the published **0.1260**
  (Δ **1.77e-4**, band 5e-3) and `U_mae` = **0.0621203** against **0.0620**
  (Δ 1.2e-4). `kOmegaSSTCorrected(0,0)` is separately measured **bit-identical**
  (rel-L2 = 0.0) to stock `kOmegaSST`.

**Consequence: the hump is scorable comparably through the `kOmegaSSTCorrected`
path**, so a lane that previously recorded it as BLOCKED-on-a-missing-library may
now run it — as **UNBLOCKABLE-BY-EQUIVALENCE-GATE**, citing this note. The
limitation stands and is not erased: equivalence is **behavioural, one-sided, on
one case, from one restart**, because the shipped model could not be loaded to
compare against. Details and the full 'cannot see' list:
`cases/RANS_LES_closure_models/NASA_hump_gate/RESULTS.md`.
