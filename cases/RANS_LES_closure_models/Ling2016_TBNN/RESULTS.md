# RESULTS - Ling, Kurzawski & Templeton (2016) TBNN, VARIANT

Preregistration: `PREREGISTRATION.md`, written before any training and unchanged
except for a dated concurrency note appended as section 10. **The preregistration
is frozen: the correction below changes what this file claims, not what that file
says.**
Code: `train_tbnn.py`, `../Kaandorp2020_TBRF/tbrf.py`. Raw log: `train_log.json`.
Predictions, checkpoints and the derived dataset live outside the repo in
`/home/ubuntu/closure-data/`.

## VERDICT: **GATE REACHED** — and the reason is the whole result

**Correction, 2026-08-20.** An earlier draft recorded **GATE FAIL** on a falsifier
reading "model output must remain a physically meaningful anisotropy". **That
clause is not in `PREREGISTRATION.md`** — I wrote it after seeing the
realisability numbers. That is the move L-179 warns against (moving the goalposts,
even in the harsher direction), and it is corrected here rather than quietly
edited away.

**The ladder as `PREREGISTRATION.md` sec. 5 actually defines it:**

| Pre-registered criterion | Outcome |
|---|---|
| (i) TBNN test `b_rms` below k-omega SST on >= 6 of 8 TEST cases | **met — 7 of 8** |
| (ii) below `b = 0` (B2) and below the train-mean constant (B3) on >= 6 of 8 | **met — 7 of 8 against both** |
| (iii) TBNN **mean test `b_rms`** below the plain MLP's by more than the seed spread | **NOT met** — see sec. 4b |
| Pre-registered falsifier: *"if the plain MLP equals or beats the TBNN on the held-out ducts, the paper's central claim is not reproduced"* | **did NOT fire** — the TBNN wins all three ducts by 0.020–0.056, every margin beyond its seed spread |

(i) and (ii) met, (iii) not met → **GATE REACHED**: the method beats every physics
baseline, but the tensor-basis embedding is not shown, on the pre-registered
pooled metric, to be the reason.

**Why (iii) fails is the finding, and it is not "the embedding does not help".**
Read per case, the embedding helps almost everywhere: the TBNN beats its own
unconstrained control on **7 of 7** in-domain cases, by more than the seed spread
on **6 of 7**. It fails (iii) solely because the criterion is written on the
*pooled* test set, and the pooled number is dominated by the single
out-of-family case where the TBNN produces `||b|| ~ 1e7` and the MLP produces
0.3664. Both readings are given in sec. 4b; **the pooled one governs, because
that is what was registered**, and it is the reading less favourable to the model.

**The one-sentence result: Pope's tensor basis buys in-domain accuracy and buys
out-of-domain catastrophe.** The plain MLP is worse everywhere the model is asked
to interpolate and is the only one of the two still usable where it is asked to
extrapolate.

**A defect in the preregistration, recorded rather than retro-fitted.** Section 8
requires the realisability violation fraction to be *reported*; **no criterion
gates on it**. The TBNN puts **6.5–15.3%** of test cells outside the barycentric
triangle (truth 0.79%, SST 0.10%, and the MLP **1.24%**). Under the ladder as
written, a model unphysical on an eighth of the domain could have scored a PASS.
The fix belongs in the next preregistration, frozen before the next run:

> **NOT A RESULT** if the predicted `b` is non-realisable in more than 3x the
> truth's own violation fraction on the same cells, or if `max ||b||_F` exceeds
> `sqrt(2/3)` by more than a factor of 2, regardless of RMSE.

Applied retrospectively — which is *not* how this run is scored — the TBNN fails
that clause and the MLP passes it.

## 0. Run status and how to finish it

**All runs are complete.** The sweep launched at 20:47 ran on a machine carrying
four concurrent jobs (load average ~31 on 16 cores), which slowed it by roughly
an order of magnitude; the resume commands below are kept because they are how
the results are regenerated, not because anything is outstanding.

| Piece | Status |
|---|---|
| TBNN seeds 0-4 | **all complete**; predictions at `/home/ubuntu/closure-data/tbnn/ckpt/pred_TBNN_s{0..4}.npy` |
| Plain-MLP control | **all 5 seeds converged and scored** on the TEST set from their final prediction fields (sec. 4b). Seeds 0-2 were run twice, in two independent processes, and came out bit-identical |
| TBRF sibling comparator (secs. 7b, 7b-i) | **all 6 forests complete**: three 5-invariant seeds and three 17-feature seeds |

Everything is bounded and restart-safe: a hard cap of 400 epochs, a wall-clock
self-timeout from launch, a checkpoint every 25 epochs, and a resume path that
reloads `{CKPT}/{tag}_s{seed}.pt` and continues from the stored epoch. **No
process needs to be killed.** Exact resume commands:

```bash
# TBNN sweep + in-sweep MLP control (checkpoints: /home/ubuntu/closure-data/tbnn/ckpt/)
cd /home/ubuntu/Certonomous/cases/RANS_LES_closure_models/Ling2016_TBNN
/home/ubuntu/closure-venv/bin/python train_tbnn.py --seeds 0 1 2 3 4

# isolated MLP control (checkpoints: /home/ubuntu/closure-data/tbnn/ckpt_mlponly/)
# NOTE: mlp_only.py lived in the session scratchpad, which was cleared by an
# unrelated workstream. It was a copy of train_tbnn.py with three lines changed:
#   CKPT -> /home/ubuntu/closure-data/tbnn/ckpt_mlponly
#   the (tag, Model, lr) tuple reduced to (("MLP", PlainMLP, LR_MLP),)
#   WALL_LIMIT_S 3*3600 -> 5*3600
# It is NOT recreated here, because the main sweep below already produced five
# MLP seeds in its own directory and those are the numbers section 4b reports.
# Re-deriving it is three edits to train_tbnn.py if an isolated arm is wanted again.

# TBRF sibling comparator (checkpoints: /home/ubuntu/closure-data/tbrf/*.pkl, per 10 trees)
cd /home/ubuntu/Certonomous/cases/RANS_LES_closure_models/Kaandorp2020_TBRF
OMP_NUM_THREADS=6 /home/ubuntu/closure-venv/bin/python run_tbrf.py

# then regenerate the tables in sections 4, 4b, 6, 7b, 7b-i and 10:
cd /home/ubuntu/Certonomous/cases/RANS_LES_closure_models/Ling2016_TBNN
/home/ubuntu/closure-venv/bin/python analyse_tbnn.py   # -> /home/ubuntu/closure-data/tbnn_analysis.json
/home/ubuntu/closure-venv/bin/python analyse_tbrf.py   # -> /home/ubuntu/closure-data/tbrf_analysis.json
```

`analyse_tbnn.py` and `analyse_tbrf.py` were **recreated in this directory on
2026-08-21** after the session scratchpad that held them was cleared by an
unrelated workstream. Behaviour is unchanged and their output reproduces the
tables below; only the output path moved, from the scratchpad to
`/home/ubuntu/closure-data/`. `mlp_only.py` was **not** recreated - see the
comment in the block above for exactly what it was, and why it is not needed.

Each resumes from checkpoints and skips completed work. Note that `mlp_only.py`
writes into a **separate** checkpoint directory from `train_tbnn.py`, deliberately,
so the two MLP arms cannot overwrite each other.

**Every pre-registered criterion is decided and every run has finished** (sec. 4b):
5 TBNN seeds, 5 plain-MLP seeds, 6 tensor-basis forests. **Tables refreshed
2026-08-21** by re-running `analyse_tbnn.py` after the fifth MLP seed landed;
the verdict is unchanged. The verdict was
unchanged at each stage it could have been called — a mid-run MLP checkpoint at
epoch 300, seed 0 alone, and all three converged seeds all give the same ordering
and the same answer, because criterion (iii) is failed on the pooled metric by
seven orders of magnitude on a single case.

## 1. What is NOT being claimed

**Ling et al.'s headline number, `b` RMSE 0.13 on duct flow at `Re_b` = 2000
(their Table I, p. 11), is not a target here and was never treated as one.** None
of their nine flows is on this machine (see `PREREGISTRATION.md` sec. 2). What is
tested is their *structural* claim: that embedding Pope's tensor basis in the
network makes it generalise to unseen flows better than a plain network of
comparable capacity on the same inputs.

## 2. Provenance

| Item | Value |
|---|---|
| paper | `docs/papers/closure/Ling2016_tbnn_embedded_invariance.pdf`, **VERIFIED-PDF**, printed title page `SAND2016-7345J`, dated July 24 2016 (JFM 807:155-166) |
| data | Closure Challenge benchmark, `https://github.com/rmcconke/closure-challenge-benchmark.git`, commit `deb91557184af3cb95f5190494ec52d8f2c6a0d1`, local clone `/home/ubuntu/closure-challenge-benchmark` (outside the repo); `sha256` of `git ls-files -s data` = `e9cd3f22ec235bd3e218931dfb76d522b429b63883a16f2c86cbb3993a360401` |
| derived arrays | `/home/ubuntu/closure-data/tbnn/dataset.npz` (`_common/build_dataset.py`), provenance json alongside |
| architecture | as Ling p. 9: 5 invariants -> 8 hidden layers x 30 nodes -> 10 `g^(n)` -> element-wise multiply with `T^(1..10)` -> sum. LeakyReLU(0.01) |
| control | as Ling p. 6: 10 hidden layers x 10 nodes, regressing the 6 independent components of `b` directly from the same 5 invariants, then made traceless |
| optimiser | Adam, lr 1e-3, batch 8192, <= 400 epochs, early stop on validation `b_rms` with patience 60 |
| seeds | 0, 1, 2, 3, 4 |
| threads | `torch.set_num_threads(4)` - **not** 16; see sec. 8 |

## 3. Disjointness assertion, printed verbatim from the run

```
[assert] case sets pairwise disjoint: train=23 val=5 test=8
[assert] (alpha,length) groups disjoint: train=13 val=3 test=6; no group appears on both sides
[assert] cells are never split across cases: every case contributes all of its cells to exactly one of train/val/test
```

Cells: train **342,014**, validation 77,611, test 152,634 — all on the
**LES-only mask** (`valid_les_only` in `_common/score_prediction.py`: `k_LES`
above the anisotropy floor, so `b_LES` is defined), which is the right mask here
because the TBNN never touches `b_RANS`; `BASELINES.md` sec. 6.4 quotes **341,717**
for the same training split on the stricter `valid` mask that additionally
requires a finite `b_RANS`, and the 297-cell difference is entirely cells where
the converged RANS `k` underflows although `k_LES` does not. Four hills
(`alpha_15_13929_3036`, `alpha_05_4071_3036`, `alpha_05_10071_3036`,
`alpha_15_7929_3036`) were **removed from training** although the benchmark
permits them, because each differs from a TEST or VALIDATION hill only in domain
height (`BASELINES.md` sec. 6.2 warns about exactly this near-duplicate leak).

## 4. Test results: RMS of `||b_pred - b_LES||_F`, mean over all 5 seeds

| Case | cells | TBNN (5 seeds) | seed spread | k-omega SST (B1) | `b = 0` (B2) | train-mean (B3) | beats SST? | beats B3? | beyond train Mahalanobis p99 |
|---|---|---|---|---|---|---|---|---|---|
| `AR_14_Ret_180` | 31624 | **0.1105** | 0.0071 | 0.5799 | 0.5842 | 0.4036 | **yes** | **yes** | 0.00% |
| `AR_1_Ret_360` | 2955 | **0.1222** | 0.0053 | 0.5972 | 0.5996 | 0.4221 | **yes** | **yes** | 0.00% |
| `AR_3_Ret_360` | 8644 | **0.1229** | 0.0078 | 0.5523 | 0.5580 | 0.3866 | **yes** | **yes** | 0.00% |
| `NASA_2DWMH` | 47102 | **1.48e+07** | 3.71e+07 | 0.3318 | 0.3398 | 0.2949 | **NO** | **NO** | 13.17% |
| `alpha_05_4071_2024` | 15503 | **0.1881** | 0.0029 | 0.3271 | 0.3457 | 0.2586 | **yes** | **yes** | 0.57% |
| `alpha_05_4071_4048` | 15543 | **0.2364** | 0.0038 | 0.3512 | 0.3791 | 0.3014 | **yes** | **yes** | 0.57% |
| `alpha_15_13929_2024` | 15573 | **0.2257** | 0.0090 | 0.3339 | 0.3355 | 0.2714 | **yes** | **yes** | 0.70% |
| `alpha_15_13929_4048` | 15576 | **0.1362** | 0.0038 | 0.2889 | 0.3128 | 0.2258 | **yes** | **yes** | 0.39% |

Validation `b_rms` (best epoch, per seed): 0.1693, 0.1653, 0.1620, 0.1623, 0.1648.

**All 5 seeds complete.** TBNN beats SST on **7 of 8** and beats the
train-mean constant (B3, `BASELINES.md` sec. 6.4) on **7 of 8** - the same 7.

## 4b. Criterion (iii): the TBNN against Ling's own control

The plain MLP (10 x 10, same five invariants, no tensor basis — Ling 2016 p. 6)
was trained on the **identical** split. **All five seeds have converged**, matching
the TBNN's five, so both models carry their own seed spread over the same number
of runs.

| Case | TBNN (5 seeds) | TBNN spread | MLP (5 seeds) | MLP spread | TBNN advantage | beyond the LARGER spread? |
|---|---|---|---|---|---|---|
| `AR_14_Ret_180` | 0.1105 | 0.0071 | 0.1378 | 0.0237 | 0.0273 | yes |
| `AR_1_Ret_360` | 0.1222 | 0.0053 | 0.1811 | 0.0130 | 0.0589 | yes |
| `AR_3_Ret_360` | 0.1229 | 0.0078 | 0.1707 | 0.0132 | 0.0478 | yes |
| `NASA_2DWMH` | 1.48e+07 | 3.71e+07 | 0.4073 | 0.1730 | 1.48e+07 WORSE | n/a |
| `alpha_05_4071_2024` | 0.1881 | 0.0029 | 0.1971 | 0.0045 | 0.0090 | yes |
| `alpha_05_4071_4048` | 0.2364 | 0.0038 | 0.2503 | 0.0086 | 0.0139 | yes |
| `alpha_15_13929_2024` | 0.2257 | 0.0090 | 0.2310 | 0.0050 | 0.0053 | no |
| `alpha_15_13929_4048` | 0.1362 | 0.0038 | 0.1548 | 0.0087 | 0.0186 | yes |

The "beyond spread" column uses the **larger** of the two models' spreads, which
is the conservative choice.

**Determinism check, unplanned and worth recording.** MLP seed 0 was trained twice
by two independent processes, in separate checkpoint directories, minutes apart on
a loaded machine (one as part of the main sweep after five TBNN runs, one in an
isolated control run). The two prediction fields over all 641,652 cells are
**bit-identical** (`max|diff| = 0.0`), and both report validation `b_rms`
0.17271. `torch.manual_seed` is re-set per (model, seed) inside the loop, so the
preceding TBNN runs do not perturb the control — which is what makes the two
arms comparable rather than merely similar.

**Two readings of criterion (iii), both given:**

* **Per case, in-domain (7 cases):** TBNN better on **7 of 7**, by more than the
  larger of the two seed spreads on **6 of 7**. Only `alpha_15_13929_2024` is
  inside the spread (advantage 0.0053 against a TBNN spread of 0.0090). On this
  reading the invariance embedding earns its keep and criterion (iii) is met.
* **Pooled over the whole test set, which is what was registered:** TBNN
  **8.56e+06** against MLP **0.2501 / 0.3328 / 0.2764 / 0.2635 / 0.2561** (5 seeds,
  mean 0.2758). The TBNN's pooled error is entirely `NASA_2DWMH` (1.48e+07 against
  the MLP's 0.4073), so it is worse by seven orders of magnitude and (iii) fails.

**The pooled reading governs.** It is what the preregistration says, and it is the
one less favourable to the model. Both are printed so no reader has to take my
word for which was chosen.

**Realisability, the same comparison:** TBNN **6.5–15.3%** of test cells
non-realisable across 5 seeds; converged MLP **0.88% / 2.27% / 2.45% / 2.66% /
1.05%** across 5 seeds (mean 1.86%); truth **0.79%**; SST **0.10%**. The
unconstrained network stays within **1.1x–3.4x** of the truth's own violation
rate; the tensor-basis network is **8x–19x** worse than it. The two ranges do not
overlap. The unconstrained network — which has no mechanism
enforcing anything — stays an order of magnitude closer to physically admissible
states than the network built around an exactly-invariant tensor basis. The basis
constrains the *form* of `b` and nothing about its *magnitude*, and on this
benchmark the basis has numerical rank 3-to-4, so six or seven of the ten
coefficients are multiplying directions the training data cannot pin down
(sec. 7, and `docs/closure/FOUNDATIONAL_MODELS_INVENTORY.md` sec. 6.5).

## 5. The trivial baseline that beats k-omega SST on every test case

Pre-registered baseline **B3** is a *single constant tensor*: the mean `b_LES`
over all 342,014 training cells (LES-only mask; 341,717 on the stricter mask
`BASELINES.md` sec. 6.4 uses — see sec. 3),

```
b_mean =  [  0.1756  -0.0382   0.0018 ]
          [ -0.0382  -0.1479  -0.0006 ]
          [  0.0018  -0.0006  -0.0276 ]
```

**It beats k-omega SST on all 8 TEST cases** (0.4036 vs 0.5799 on `AR_14_Ret_180`,
0.2258 vs 0.2889 on `alpha_15_13929_4048`, and so on down the B3 and B1 columns
above). Predicting one constant anisotropy everywhere, with no inputs at all, is
a better a-priori anisotropy model than the linear eddy-viscosity closure that
the benchmark ships.

That is the most useful number in this file. **"Beats SST on `b_rms`" is a very
low bar**, and any data-driven closure paper reporting only that comparison has
not shown much. Every reproduction in this directory tree is therefore scored
against B3 as well as B1, and the supervisor should treat a method that beats B1
but not B3 as having produced nothing.

## 6. Realisability of the predicted anisotropy

Fraction of the 152,634 test cells whose predicted `b` lies outside the
barycentric triangle, reported beside the truth's own rate as `BASELINES.md`
sec. 5 requires:

| Predictor | violation fraction on TEST cells |
|---|---|
| **TBNN, seeds 0/1/2/3/4** | **15.34% / 9.84% / 6.47% / 14.79% / 9.10%** |
| tensor-basis RF, 5 invariants, 3 seeds | 10.16% / 11.36% / 10.55% |
| tensor-basis RF, 17 features, 3 seeds | 9.66% / 9.27% / 9.74% |
| **plain MLP (no tensor basis), 5 converged seeds** | **0.88% / 2.27% / 2.45% / 2.66% / 1.05%** |
| Wu 2018 random forest, same split (sibling directory) | 1.54-1.60% |
| the LES/DNS **truth** itself | **0.79%** |
| k-omega SST | 0.10% (all of it on the hump) |

**Every model built on the tensor basis is 8x-19x worse than the truth's own
violation rate; every model without one is within 2x of it — the converged MLP is
within 1.13x.** That is the
cleanest single line in this file: the structure that guarantees Galilean
invariance is the same structure that destroys realisability, because it
constrains the form of `b` and nothing about its magnitude.

The TBNN is 8x to 19x worse than the truth's own violation rate and two orders of
magnitude worse than SST. **Embedding the tensor basis buys Galilean invariance
and buys nothing else**: `b = sum g^(n) T^(n)` is unbounded, and nothing in the
architecture constrains the eigenvalues. The seed-to-seed spread (6.5% to 15.3%)
is itself larger than any other quantity in this file, which says the violation
rate is governed by where the optimiser happened to land, not by the data.

## 7. Why the NASA hump explodes, measured rather than guessed

Two pre-registered diagnostics, neither fitted to the outcome:

**(a) Extrapolation.** Mahalanobis distance of each test cell's five invariants
from the training distribution (training 99th percentile = 8.56):

| Case | median | p99 | fraction beyond the training p99 |
|---|---|---|---|
| `AR_14_Ret_180` | 0.77 | 5.44 | **0.00%** |
| `AR_1_Ret_360` | 1.52 | 5.53 | **0.00%** |
| `AR_3_Ret_360` | 0.82 | 5.46 | **0.00%** |
| `alpha_05_4071_2024` | 0.92 | 6.49 | 0.57% |
| `alpha_05_4071_4048` | 0.72 | 5.28 | 0.57% |
| `alpha_15_13929_2024` | 0.87 | 6.54 | 0.70% |
| `alpha_15_13929_4048` | 0.79 | 4.87 | 0.39% |
| **`NASA_2DWMH`** | 0.72 | **58.03** | **13.17%** |

The hump is the only test case with a stagnation region, and it is the only one
with a double-digit percentage of cells outside the training envelope. The
statistic identifies the failing case without being told which case failed.

**(b) Basis degeneracy.** The RMS Frobenius norms of `T^(1..10)` over the training
set span seven orders of magnitude
(`15.4, 3.5e3, 1.0e3, 1.0e3, 2.0e2, 5.3e5, 8.4e7, 8.4e7, 4.9e7, 1.4e6`), and the
**per-cell rank of the ten tensors runs 3.006-3.987 by case mean, and never
exceeds 5 in any cell** on this benchmark - because every case is a
statistically two-dimensional mean flow and Pope's basis collapses to three tensors in two dimensions [VERIFIED-PDF: Pope
1975, JFM 72(2), p. 335]. The network is therefore free to place large,
mutually-cancelling coefficients on six or seven null directions. In-distribution
they cancel. On the hump they do not. Measurement and full discussion:
`docs/closure/FOUNDATIONAL_MODELS_INVENTORY.md` sec. 6.5.

**A benchmark of 2-D flows cannot test the claim that ten tensors are what these
methods need.** Everything above is a result for a three-tensor model.

## 7b. Sibling comparator: a tensor-basis RANDOM FOREST on the identical split

Ling's paper compares the TBNN to a plain MLP; Kaandorp & Dwight's compares a
tensor-basis random forest (TBRF) to Ling's TBNN. To make the second comparison
on identical data, a TBRF was trained here on **exactly this split**, with
Kaandorp's own settings (100 tensor-basis decision trees, 21,000 sampled training
cells, minimum 9 samples per leaf, median over trees) and the same five Pope
invariants as features. **Note:** a second agent is independently running a more
faithful Kaandorp reproduction in `../Kaandorp2020_TBRF/` using their exact
FS1/FS2/FS3 feature sets and a different split; the numbers below are *this*
file's experiment and must not be confused with theirs.

Three seeds complete (the pre-registered minimum), RMS of `||b_pred - b_LES||_F`
on the 8 TEST cases:

| Case | TBRF (5 invariants) | seed range | TBNN (same split) | k-omega SST |
|---|---|---|---|---|
| `AR_14_Ret_180` | **0.0788** | 0.0777-0.0807 | 0.1108 | 0.5799 |
| `AR_1_Ret_360` | **0.1157** | 0.1150-0.1165 | 0.1225 | 0.5972 |
| `AR_3_Ret_360` | **0.1216** | 0.1215-0.1217 | 0.1227 | 0.5523 |
| `NASA_2DWMH` | **197.3** | 136.2-282.1 | 1.74e+07 | 0.3318 |
| `alpha_05_4071_2024` | 0.1918 | 0.1903-0.1930 | **0.1881** | 0.3271 |
| `alpha_05_4071_4048` | 0.2365 | 0.2352-0.2376 | **0.2360** | 0.3512 |
| `alpha_15_13929_2024` | **0.2220** | 0.2195-0.2264 | 0.2254 | 0.3339 |
| `alpha_15_13929_4048` | 0.1451 | 0.1362-0.1589 | **0.1366** | 0.2889 |

**In-family vs out-of-family, which the table above does not show by itself.**
The training set contains `AR_1/3/5/10_Ret_180`, `PHLL10595` and `CBFS13700`.
So of the eight TEST cases:

* `AR_1_Ret_360`, `AR_3_Ret_360` are **geometry-in-family, Reynolds-out-of-family**
  (the same aspect ratios at roughly twice `Re_tau`);
* `AR_14_Ret_180` is **Reynolds-in-family, geometry-out-of-family** (1.4x the
  widest trained aspect ratio);
* the four `alpha_05`/`alpha_15` hills are in-family in flow class and
  out-of-family in hill shape, with the `(alpha, length)` group-leak exclusions
  of sec. 3 enforced;
* **`NASA_2DWMH` is out-of-family in every respect** - a different flow class, a
  Reynolds number 170x the hills', and the only stagnation region in the set.

The strong scores (0.079-0.123) are all on the duct cases, which are the most
in-family; the failure is on the only wholly out-of-family case. Read the table
with that ordering in mind, not as eight equivalent held-out flows.

Three readings:

1. **TBRF and TBNN are within a few per cent of each other on seven of eight
   cases** - TBRF ahead on the ducts, TBNN ahead on two hills, and the gaps are
   comparable to the seed spread. On this data the choice of regressor is not
   what matters, which is Kaandorp & Dwight's own conclusion arrived at
   independently.
2. **Both blow up on the NASA hump**, the extrapolation case: TBRF by a factor of
   ~600 over the realisable bound, TBNN by a factor of ~2e7. The failure is a
   property of the model *class* - `b = sum g^(n) T^(n)` with a rank-3 basis and
   unconstrained coefficients - and not of the regressor.
3. **TBRF's realisability violation on the test cells is 10.2%, 11.4% and 10.6%**
   (three seeds), against the TBNN's 6.5-15.3%, the truth's 0.79% and SST's 0.10%.
   A forest with bounded leaf values is no safer here than a network.

### 7b-i. The 17-feature arm: Kaandorp & Dwight's central claim reproduces

The 17-feature TBRF (`_common/features_ext.py`, three seeds) against the
5-invariant TBRF (three seeds), the TBNN (five seeds) and the plain MLP (three
seeds), on the identical split — **all six forests and all eight models now
complete**:

| Case | TBRF **17 features** | TBRF 5 invariants | TBNN | plain MLP | k-omega SST | train-mean (B3) |
|---|---|---|---|---|---|---|
| `AR_14_Ret_180` | **0.0440** | 0.0788 | 0.1105 | 0.1379 | 0.5799 | 0.4036 |
| `AR_1_Ret_360` | **0.0849** | 0.1157 | 0.1222 | 0.1807 | 0.5972 | 0.4221 |
| `AR_3_Ret_360` | **0.0899** | 0.1216 | 0.1229 | 0.1705 | 0.5523 | 0.3866 |
| `alpha_05_4071_2024` | **0.1404** | 0.1918 | 0.1881 | 0.1981 | 0.3271 | 0.2586 |
| `alpha_05_4071_4048` | **0.2024** | 0.2365 | 0.2364 | 0.2510 | 0.3512 | 0.3014 |
| `alpha_15_13929_2024` | **0.1786** | 0.2220 | 0.2257 | 0.2311 | 0.3339 | 0.2714 |
| `alpha_15_13929_4048` | **0.0841** | 0.1451 | 0.1362 | 0.1552 | 0.2889 | 0.2258 |
| `NASA_2DWMH` | 471.1 | 197.3 | 1.48e+07 | **0.4299** | 0.3318 | 0.2949 |

**The 17-feature arm wins on all seven in-domain cases**, by 15% to 44% over the
5-invariant arm, against a 5-invariant seed spread of 0.0001-0.023 — every margin
far outside seed noise. It also beats the TBNN on all seven, and the plain MLP on
all seven.

That is **Kaandorp & Dwight's central claim, reproduced**: *"the introduction of
extra features has significantly more effect than the choice of neural-networks
versus random-forests"* [VERIFIED-PDF: arXiv:1810.08794v2, p. 36]. On this data
the regressor choice moves `b_rms` by a few per cent and the feature set moves it
by tens of per cent, in their direction.

**The seed spreads say where the model is identified and where it is not.** The
17-feature arm's three seeds agree to **0.0001-0.0104** on every in-domain case,
and span a **factor of 3.5** on the hump (208.6 to 733.3). A model reproducible
to three or four significant figures in-domain and to half an order of magnitude
out-of-domain is not "slightly less accurate" outside its envelope; the
coefficients doing the work out there are simply not determined by the training
data. Same diagnosis as sec. 7: rank-3-to-4 basis, six or seven unidentifiable
directions. Adding seeds *widened* the hump range (208.6-282.1 at two seeds,
208.6-733.3 at three) — the out-of-domain prediction has no converged value to
estimate.

**The ordering across all four models on the hump is the cleanest statement of
the failure**: plain MLP **0.4299**, TBRF-5 **197**, TBRF-17 **471**, TBNN
**1.48e+07** — against SST 0.3318 and a realisable bound of 0.8165. **The only
model with no tensor basis is the only one that is still usable**, and it is the
worst of the four everywhere else.

**Three things it does not buy.** It does not fix the hump (3-seed mean 471,
*worse* than the 5-feature arm's 197.3). It does not fix realisability (9.66% of
test cells outside the barycentric triangle, against the truth's 0.79%). And it
does not change the ordering of the failure: more features make the model better
where it already worked and no safer where it did not.

**Independent corroboration.** A second agent (CLOSURE-REPRO) ran a more faithful
Kaandorp reproduction with the paper's own FS1/FS2/FS3 feature sets and a
different split, and reproduced the out-of-family blow-up independently: hump
values **136 / 282 / 174** over three seeds, with per-cell basis rank **~3.1-4.0**
on the 2-D training data and unconstrained `g^(5..10)` multiplying non-zero
`T^(5..10)` once a 3-D flow is presented. Two implementations, two feature sets
and two splits give the same failure, which makes it a property of the model
class rather than of either implementation.

**Code-provenance note, 2026-08-20.** `tbrf.py` was overwritten by another agent
at 20:54:57Z and recovered from transcript. The recovered file was the
**pre-patch** version - it carried the plain `Gamma = 1e-12` ridge, which is the
version that scores training `b_rms` 0.81. The running process (pid 153860) had
already loaded the patched module and its results are unaffected, but the file on
disk could not have reproduced them. The eigendecomposition patch has been
re-applied; the file is now 7,478 bytes, `sha256 d84220e27f045950...`. The
pre-patch recovery is kept at `Kaandorp2020_TBRF/tbrf_original_recovered.py` (same bytes; the scratchpad copy was wiped 2026-08-21) (6,800
bytes, `sha256 b39536ebde4bd481...`) so the difference is auditable.

The TBRF's own `Gamma = 1e-12` ridge (VERIFIED-PDF: arXiv:1810.08794v2, p. 30)
had to be replaced by a truncated eigendecomposition at `1e-8 lambda_max` to make
the method work at all on this data - with their published constant the *training*
`b_rms` was 0.81, worse than predicting zero. That departure is disclosed in
`tbrf.py` and its cause is sec. 6.5 of `docs/closure/FOUNDATIONAL_MODELS_INVENTORY.md`.

## 8. Departures from the paper, all disclosed

* **D1 (flows).** Entirely different flow set - see sec. 1.
* **D2 (time scale).** Ling normalise `S` and `R` "using the turbulent kinetic
  energy `k` and the turbulent dissipation rate `eps`" (p. 6). The benchmark
  ships `omega`, so `eps = beta* k omega` with `beta* = 0.09` [VERIFIED-PDF:
  Menter 1994, eq. (A4), p. 1603], with Durbin's lower bound
  `T >= 6 sqrt(nu/eps)` applied. Ling do not state an equivalent bound.
* **D3 (optimiser).** Ling report lr 2.5e-7 for the TBNN (p. 7) and 2.5e-6 for
  the MLP (p. 6) with plain SGD. We use Adam at 1e-3 for both, because their
  rates with Adam do not move in 400 epochs on this data. This is a real
  departure and it is the most likely place a faithful reproduction would differ.
* **D4 (input scaling).** The invariants span `1e-3` to `7e7` on a single hill,
  so inputs are signed-`log1p` compressed and then standardised on **training
  cells only**. Ling state no input scaling.
* **D5 (basis scaling).** Each `T^(n)` is divided by its training-set RMS
  Frobenius norm. This is an exact reparametrisation of `g^(n)` and does not
  change the model class; it is recorded because it changes the optimisation.
* **D6.** A-priori only; no solve. See sec. 10.

## 9. Compute

`torch.set_num_threads(4)`, batch 8192. Measured on this machine: **0.78 s per
epoch at 4 threads against 49.4 s at 16** - a factor of 63, and the reason the
sweep took about an hour instead of the 66 hours the first configuration was on
track for. Full numbers in `docs/NUMERICS_KNOWLEDGE.md`, closure section, N-B4. Anyone repeating
this must pin the thread count.

## 10. What this result cannot see

* **It cannot see what happens in a solver.** No velocity field was produced and
  nothing was re-solved. **OpenFOAM v2606 is installed at
  `/usr/lib/openfoam/openfoam2606` and `simpleFoam` runs on this machine**, so
  this is a scope decision, not a capability limit. Given that 6-15% of predicted
  cells are non-realisable, an a-posteriori solve would very likely diverge, and
  that is a prediction this file makes and does not test.
* **No continuity check is applicable**: no velocity field.
* **It cannot compare to Ling's 0.13.** Different flows entirely.
* **It cannot see 3-D behaviour**: rank-3 basis throughout (sec. 7b).
* **It cannot see the truth's uncertainty**: the benchmark ships no error bar,
  and the truth is itself non-realisable in 0.79% of these cells.
* **Criterion (iii) is resolved on three converged control seeds.** All are
  scored from their final prediction fields, not checkpoints, and both models
  carry their own spread. Intermediate scorings (a mid-run checkpoint at epoch
  300, and seed 0 alone) gave the same verdict and the same per-case ordering, so
  the result is not sensitive to where the control was stopped or to how many of
  its seeds were counted. What it still cannot see: three seeds is a small sample
  for a spread, and the one case inside the spread (`alpha_15_13929_2024`) would
  need more seeds to call either way.
* **A pre-sweep observation, recorded because it was seen early and must not be
  dropped now that the answer went the other way.** A 2-epoch smoke test before
  the sweep had the MLP *ahead* of the TBNN on validation (0.264 against 0.577).
  Two epochs prove nothing about converged performance, and the converged result
  is the opposite; it is kept here so the record shows what was seen and when.


---

**Provenance repair, 2026-08-21.** An earlier figure of "3.24 on average, never above 5" for the per-cell rank of Pope's ten-tensor basis was quoted here from `Kaandorp2020_TBRF/train_log.json`, **which does not exist** (charter section 5(b)). It has been replaced by a live re-measurement: per-cell rank of **3.006-3.987 by case mean** (mean of case means **3.738**), **never above 5 in any cell**, source `_common/features/FS2_DEGENERACY_REPORT.md` sec. 4 and `/home/ubuntu/closure-data/features/fs2_audit.json` -> `tensor_basis_rank`. 3.24 was a pooled-sample statistic over randomly drawn training cells, which the low-rank duct family pulls down; the case-mean statistic is 3.738. They are different statistics and are not interchangeable. **The bound that carries the argument is unchanged: never above 5, against a nominal basis size of 10.**
