# Closure Challenge — master statistics table

Assembled 2026-08-05 by `sdk/scripts/closure_eval_battery/build_master_table.py` from records already on disk. **No scoring call and no ground-truth read happens in this script.** Companion: `CLOSURE_EVALUATION_PROTOCOL.md` (what each metric is and who uses it).

---

## A. The public leaderboard, as published

Transcribed by machine from `~/closure-challenge-benchmark/README.md` (the benchmark's own statement that it, not the preprint, is "the main source of up-to-date information"). **These are other people's numbers on the eight official test cases. We did not recompute them and could not** — three of the four entrants' prediction files are in the repo, but re-scoring them would consume scoring calls on ground truth to no purpose. Our row is our own recorded round-4 result, not a leaderboard entry: **the entry has not been submitted**, so we do not appear on the board.

| source | overall | alpha_15_13929_4048 | alpha_15_13929_2024 | alpha_05_4071_4048 | alpha_05_4071_2024 | AR_1_Ret_360 | AR_3_Ret_360 | AR_14_Ret_180 | NASA_2DWMH |
|---|---|---|---|---|---|---|---|---|---|
| 1. Reissmann, Fang, and Sandberg (published) | 0.0595 | 0.0592 | 0.1339 | 0.0606 | 0.0760 | 0.0387 | 0.0341 | 0.0325 | 0.0412 |
| 2. Wu and Zhang (published) | 0.0624 | 0.0813 | 0.1195 | 0.0569 | 0.0848 | 0.0455 | 0.0399 | 0.0350 | 0.0364 |
| 3. Liu, Wang, Zhao, and Xiao (published) | 0.0737 | 0.0600 | 0.1308 | 0.0613 | 0.0769 | 0.0875 | 0.0805 | 0.0548 | 0.0377 |
| 4. Montoya, Oulghelou, and Cinnella (published) | 0.0779 | 0.0680 | 0.1364 | 0.0591 | 0.0882 | 0.0895 | 0.0866 | 0.0487 | 0.0464 |
| **ours, round 4 (recorded, not submitted)** | **0.0654** | **0.0501** | **0.1011** | **0.0461** | **0.0719** | **0.0811** | **0.0775** | **0.0325** | **0.0632** |
| raw-RANS floor (our measurement, zero ML) | 0.1036 | 0.1320 | 0.2049 | 0.0461 | 0.0719 | 0.1288 | 0.1243 | 0.0590 | 0.0621 |

Leaderboard caveat, recorded because it matters for any rank claim: the challenge preprint (arXiv:2603.28884) Table 1 lists **three** entrants; this README lists **four** (it adds Liu, Wang, Zhao & Xiao). The README is the later and self-declared authoritative source, and is what is transcribed above.

---

## B. The battery: what the metric sees, and what it does not

Train and validation cases only — the cases where reading truth is legal under the benchmark's own split. **The models are the entry of record's own**, re-fit and anchored: PH pooled validation scaled MAE came back 0.0876 against the recorded 0.0876; duct variant D's `AR_7_Ret_180` came back 0.0135 against the pre-registered 0.01345.

The scaled-MAE columns are the **challenge's own formula** (`mean ||U_pred - U_true|| / mean ||U_true||`) evaluated on every mesh cell rather than the 1000 official points, so they are comparable in kind to a leaderboard number but not identical to one.

### B1. Periodic hills

| case | role | cells | scaled MAE, RANS | scaled MAE, corrected | error removed | continuity error, RANS | continuity error, corrected |
|---|---|---|---|---|---|---|---|
| `alpha_05_10071_4048` | validation | 15600 | 0.0759 | 0.0772 | -1.7% | 0.64% | 17.39% |
| `alpha_05_10071_2024` | validation | 15600 | 0.1368 | 0.0858 | +37.3% | 0.42% | 14.58% |
| `alpha_15_7929_4048` | validation | 15600 | 0.0916 | 0.0463 | +49.5% | 0.15% | 11.43% |
| `alpha_15_7929_2024` | validation | 15600 | 0.1957 | 0.1310 | +33.1% | 0.08% | 8.20% |
| `alpha_10_9000_3036` | train | 15600 | 0.1304 | 0.0371 | +71.5% | 0.33% | 9.72% |
| `alpha_05_7071_3036` | train | 15600 | 0.0552 | 0.0589 | -6.7% | 0.61% | 13.98% |
| `alpha_15_10929_3036` | train | 15600 | 0.1676 | 0.0662 | +60.5% | 0.20% | 8.27% |

### B2. Ducts — the column the challenge metric has no way to show

Secondary-flow intensity is the volume-weighted mean in-plane speed `|(Uy,Uz)|` divided by `U_b`. It is not a challenge metric and not taken from any paper; it is our scalar summary of the quantity Ling et al. (JFM 2016) Fig. 6 draws.

| case | role | cells | AR | scaled MAE, RANS | scaled MAE, corrected | secondary-flow intensity: RANS | corrected | truth | fraction recovered |
|---|---|---|---|---|---|---|---|---|---|
| `AR_7_Ret_180` | validation | 15463 | 7 | 0.0807 | 0.0135 | 1.2e-17 | 0.0030 | 0.0027 | 112% |
| `AR_1_Ret_180` | train | 2209 | 1 | 0.1073 | 0.0341 | 5.4e-18 | 0.0043 | 0.0063 | 69% |
| `AR_3_Ret_180` | train | 6627 | 3 | 0.1112 | 0.0224 | 6.4e-18 | 0.0044 | 0.0051 | 87% |

---

## C. The mapping: where a good score hides a bad field

Figure: `closure_eval/metric_vs_physics.png`. Continuity numbers are quoted from `closure_challenge_stability_physicality_audit.md` §2 and its record `closure_challenge_divergence_audit.json` — not recomputed here.

| test case | submitted field | score, floor → submitted | continuity error, floor → submitted | continuity ratio |
|---|---|---|---|---|
| `alpha_15_13929_4048` | PH-corrected | 0.1320 → **0.0501** | 0.18% → **10.46%** | 58.0× |
| `alpha_15_13929_2024` | PH-corrected | 0.2049 → **0.1011** | 0.08% → **9.67%** | 123.6× |
| `alpha_05_4071_4048` | declined (raw RANS) | 0.0461 → **0.0461** | 0.47% → **0.47%** | — |
| `alpha_05_4071_2024` | declined (raw RANS) | 0.0719 → **0.0719** | 0.27% → **0.27%** | — |
| `AR_1_Ret_360` | duct-corrected | 0.1288 → **0.0811** | 0.00% → **2.29%** | 1e+15× (÷ machine zero) |
| `AR_3_Ret_360` | duct-corrected | 0.1243 → **0.0775** | 0.00% → **3.08%** | 4e+14× (÷ machine zero) |
| `AR_14_Ret_180` | duct-corrected | 0.0590 → **0.0325** | 0.00% → **3.41%** | 7e+14× (÷ machine zero) |
| `NASA_2DWMH` | PH-corrected | 0.0621 → **0.0632** | 0.43% → **0.66%** | 1.5× |

**What the table says, stated with the sign against us.** On the two hills the correction is applied to, the score improves by 0.082 and 0.104 while the field's continuity error goes from 0.18% and 0.08% of its own velocity-gradient scale to 10.5% and 9.7% — a factor 58 and 124. On the three ducts the RANS field is divergence-free to machine precision (its fully-developed unidirectional solution is exactly solenoidal cell-wise) and the corrected field is not, at 2.3–3.4%. **The scoring metric never sees any of this**, and nothing here changes the recorded 0.0654.

**The two declined cases are the only submissions that are both competitive and clean.** They ship the organisers' own solve, so they inherit its physicality untouched (ratio 1.000 by construction) — and on both, the raw RANS floor already beats every published entrant for that case (0.0461 vs best-published 0.0569; 0.0719 vs 0.0760). The part of the entry that does nothing is the part that survives a physics check.

