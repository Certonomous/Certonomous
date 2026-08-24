# RESULTS — Ling, Kurzawski & Templeton (2016) TBNN, GPU arm

# VERDICT: NOT A RESULT

**Graded against `PREREGISTRATION.md`, FROZEN and committed ALONE at `e8309b6c`
before any compute** — sha256 `61b2097f63a38f320aeb98275f4a7aaba8454880fe2389398ee59678d4d81d97`,
re-verified equal to the committed blob and to the copy the node ran from.
Comparator `score_gpu_ling.py` sha256 `4f9eda16…6aac`, driver `train_gpu_ling.py`
`1bac03bd…0ed3`, launcher `run_all_gpu.sh` `5b9c68eb…6fad` — all equal to the
frozen F.4 table and to the `11f93da6` blobs; the driver copy on `gpu1` hashes
the same. Written 2026-08-24T16:07:25Z by the closure supervisor, who graded personally.
Lane: closure. Node: `gpu1` (`g6.xlarge`, NVIDIA L4), the registered class.
**VARIANT** on the Closure Challenge benchmark, exactly as the CPU lane
(`../RESULTS.md`, GATE REACHED): none of Ling's nine flows is on this machine
and the paper's Table I numbers are not targets.

**The registered ladder (§8), in the registered order:**

| gate | registered | measured | |
|---|---|---|---|
| **G0** planted-zero | plant `1.234e-03` read back within 1e-9 relative; `diag(1,1,-2)` flagged; refusal → NOT A RESULT | recovered `1.234000000e-03`, rel err **1.6e-14** (identical on the node and on the lab box); flagged, min barycentric −5.0 | **PASS** |
| **G1** ARM-A TBNN a-priori | below SST, `b = 0` and train-mean on ≥ 6 of 8 TEST cases; 4–5 → GATE FAIL; ≤ 3, **or failure to beat `b = 0` anywhere** → NOT A RESULT | beats SST **0 of 8**, `b = 0` **0 of 8**, train-mean **0 of 8** (per-case mean over 5 seeds, best-val; identical reading per seed and for the final epoch) | **NOT A RESULT** |
| **G2** invariance embedding | TBNN pooled test `b_rms` below the plain MLP's by more than the seed spread | TBNN **3.90e7** (spread 3.46e7) vs MLP **0.3604** (spread 0.091) | **GATE FAIL** |
| **G3** realisability (Charter §4) | violation fraction ≤ 3× truth's own = **2.374 %** (truth 0.7914 % on the scored TEST cells); `max ‖b‖_F` ≤ 2·√(2/3) = **1.633** | ARM-A TBNN: **3.10–5.34 %**, `max ‖b‖_F` **7.8e9–2.1e10**; ARM-B: **4.30–14.44 %**, **5.6e6–9.4e8** — every seed of both models fails both clauses | **NOT A RESULT** (both TBNN models) |
| **G4** a-posteriori (CPU) | runs only if G3 has not fired (F.6); not run → capped at GATE REACHED | **not run** — G3 fired on both models | — |

**Lane verdict: NOT A RESULT.** §8 G1's own branch fires ("failure to beat
`b = 0` anywhere"), and G3 fires independently on both TBNN models. The a-priori
control MLP and the ARM-B search are reported below because they carry the
findings; neither is a gated model under §8.

---

## 1. What was measured, in one paragraph

Two things, and they pull in opposite directions. **Ling's own learning rate,
run for 200,000 full-batch epochs, does not train the 8×30 TBNN at all**: the
validation `b_rms` starts at 3–10 from the random initialisation and ends at
3–7; one seed's best epoch is epoch 0. The same optimiser at the paper's MLP rate
(2.5e-6) *does* train the 10×10 control to 0.30–0.37 — better than SST and
`b = 0` on 8 of 8 cases, worse than the train-mean tensor on 8 of 8. **And the
Bayesian architecture search, given the paper's own five-dimensional freedom,
converged back onto the CPU lane's training recipe** — batch 8192, Adam at
1.02e-3 — with a 9×77 network whose validation score (0.1595 mean) beats the
CPU lane's 8×30 (0.1646) by less than the seed spread (0.0073). That network
beats every baseline on 7 of 8 test cases by a wide margin (ducts 0.11–0.12
against train-mean 0.39–0.42), explodes on the out-of-family `NASA_2DWMH`
exactly as the CPU lane's did, **and violates realisability on up to 46 % of
duct cells while scoring its best RMSE there** — the axis RMSE cannot see,
which is why Charter §4 is a gate now.

---

## 2. The numbers

Scored on **152,520** TEST cells (`valid` ∧ finite `b_LES` ∧ finite `b_RANS`;
114 cells = 0.075 % dropped for non-finite `b_RANS`, the CPU lane's convention,
F.5(4)); train 341,717 cells. Per-case `b_rms` = RMS of `‖b_pred − b_LES‖_F`.

| model / baseline | AR_14_Ret_180 | AR_1_Ret_360 | AR_3_Ret_360 | NASA_2DWMH | α05_4071_2024 | α05_4071_4048 | α15_13929_2024 | α15_13929_4048 | pooled |
|---|---|---|---|---|---|---|---|---|---|
| SST (`b_RANS`) | 0.5799 | 0.5972 | 0.5523 | 0.3318 | 0.3271 | 0.3512 | 0.3339 | 0.2889 | 0.4138 |
| `b = 0` | 0.5842 | 0.5996 | 0.5580 | 0.3398 | 0.3457 | 0.3791 | 0.3355 | 0.3128 | 0.4234 |
| train-mean tensor | 0.4036 | 0.4221 | 0.3866 | 0.2949 | 0.2586 | 0.3014 | 0.2714 | 0.2258 | 0.3183 |
| **ARM-A TBNN** (SGD 2.5e-7, mean of 5) | 0.918 | 1.053 | 0.905 | **7.01e7** | 0.362 | 0.400 | 0.493 | 0.318 | 3.90e7 |
| **ARM-A MLP** (SGD 2.5e-6, mean of 5) | 0.485 | 0.498 | 0.462 | 0.301 | 0.295 | 0.332 | 0.298 | 0.258 | 0.3604 |
| **ARM-B best** (9×77, mean of 5) | **0.109** | **0.121** | **0.121** | **2.75e6** | **0.191** | **0.240** | **0.220** | **0.135** | 1.53e6 |

Per-seed pooled: TBNN 2.0e7–5.5e7; MLP 0.318–0.410; ARM-B 1.5e4–2.4e6 (the
NASA cells dominate every pooled TBNN-family figure).

**`NASA_2DWMH`, graded per case and not absorbed into a pooled mean.** Both
TBNN-family arms explode on this one case — ARM-A TBNN **7.01e7** (5-seed mean;
per seed 2.0e7–9.9e7), ARM-B **2.75e6** (1.5e4–4.4e6) — while the other seven
cases sit at 0.32–1.05 (ARM-A) and 0.11–0.24 (ARM-B). §8 anticipated exactly
this in G2's wording: *"both pooled and with the pooled figure reported beside
the per-case reading, because the CPU lane's (iii) failed only on the pooled
metric, by seven orders of magnitude on one case"* — so G2's pooled verdict
stands as registered (GATE FAIL) and the per-case split is its registered
companion: on the seven in-family cases ARM-A TBNN is still worse than the MLP
on every one (0.32–1.05 vs 0.26–0.50); ARM-B is better than the MLP on all
seven. **G1 is per-case by construction (≥ 6 of 8) and is unaffected by the
blow-up**: ARM-A TBNN loses on the seven in-family cases too. This is the same
case the FS5/D476 standing-gate instrument flagged at **9.596 % of cells above
the training unclipped `q1_wallRe` max** (docket D484, N-B39): an
out-of-training-range feature case, which is what a tensor-basis network with
`tscale` up to 8.4e7 on bases 7–8 amplifies. Reported, not gated here — no §8
clause registers a per-case reservation for G1 or G3, and none is added after
the fact. Best-val and final-epoch
readings differ only on TBNN seed 1 and on ARM-B (final worse on NASA).

**Realisability (G3), per seed** — `viol %` on all scored TEST cells /
`max ‖b‖_F`:

| model | s0 | s1 | s2 | s3 | s4 |
|---|---|---|---|---|---|
| ARM-A TBNN | 3.10 / 1.7e10 | 4.61 / 1.3e10 | 5.34 / 1.6e10 | 4.51 / 2.1e10 | 5.04 / 7.8e9 |
| ARM-A MLP | 0.00 / 0.148 | 0.00 / 0.123 | 0.00 / 0.118 | 0.00 / 0.209 | 0.00 / 0.222 |
| ARM-B best | 12.46 / 8.2e8 | 4.30 / 9.4e8 | 11.99 / 5.6e6 | 6.33 / 8.7e8 | 14.44 / 3.2e8 |
| truth / SST | 0.79 / — | | | | 0.10 / 3.48 |

**Where the violations sit** (per-case, from the same predictions, the CPU lane's
`realisability_violation`): ARM-B on `NASA_2DWMH` **10.1–12.1 %** on every seed
with `‖b‖_F` up to 9.4e8; on the three ducts **0.5–1.2 %** (seed 1), **6.1–6.8 %**
(seed 3), **24.7–46.4 %** (seeds 0, 2, 4) — with `max ‖b‖_F` ≈ 0.76–0.83 there,
i.e. inside the norm bound and outside the barycentric triangle. The hills sit
at 1.2–4.1 %. **The non-realisability is not confined to the out-of-family
case**; it is largest, in cell fraction, exactly where the RMSE is best.

**Training histories** (no NaN/inf in any of the 15 files): TBNN train loss
0.18–0.42 → 0.16–0.27 over 200,000 epochs, val 2.98–9.61 → 2.98–7.11 (seed 1's
best is epoch 0); MLP train 0.22–1.15 → 0.083–0.120, val 0.49–1.09 → 0.30–0.37,
best = last epoch on every seed (still descending at the cap); ARM-B retrain
val 0.39–0.99 → best 0.1575–0.1611 within 400 epochs.

**ARM-B search** (100 TPE trials × 3 seeds × 400 epochs, VAL-only objective):
best `depth 9, width 77, LeakyReLU(0.01), batch 8192, lr 1.0229e-3`,
best objective 0.16040; retrain 5 seeds val 0.1575–0.1611 (mean **0.1595**,
spread 0.0035). CPU lane's frozen 8×30 under the same optimiser regime
(`../train_log.json`): val 0.1620–0.1693 (mean **0.1646**, spread 0.0073).

---

## 3. The two pre-stated falsifiers (§10), graded as written

**Falsifier 1 — departure D3.** Registered: *if ARM-A at Ling's own SGD rates
and a 200,000-epoch budget produces a TBNN whose pooled test `b_rms` is not
better than the CPU lane's Adam-trained TBNN by more than the seed spread, then
D3 is not the reason the CPU lane fell short.* Measured: ARM-A's TBNN is worse
than the CPU lane's on every case and every baseline (the CPU lane's TBNN beat
SST, `b = 0` and train-mean on 7 of 8; this one on 0 of 8). **The falsifier
fires as written.** What it licenses is bounded by disclosure D-1 below: the
frozen ARM-A ran the paper's *rate* under **one update per epoch**, and the
paper updated **after each training point** — so the experiment that ran tests
"2.5e-7 at 200,000 updates", not "2.5e-7 at ~7.8e10 updates". D3 is therefore
**not settled** by this arm; what is settled is that the rate alone, under the
registered batch regime, is inert.

**Falsifier 2 — the architecture search.** Registered: *fires if the search
selects an architecture materially different from 8×30 (> 2 layers or > 10
nodes away) AND that architecture scores better than 8×30 on validation by more
than the seed spread.* Measured: 9×77 is materially different (47 nodes wider);
its validation advantage is **0.0051 (0.1595 vs 0.1646)**, **inside** the
CPU lane's seed spread of 0.0073 (and outside ARM-B's own 0.0035; the larger
spread governs a falsifier). **Does not fire.** The paper's 8×30 is not shown to
be off the optimum of its own procedure on this data — the optimum is flat in
width and depth, and the search's real output is that it re-selected the CPU
lane's batch and learning rate to three significant figures.

---

## 4. Disclosures and departures — dated 2026-08-24

**D-1 (design defect in the frozen file, graded as written, not regraded).**
§6 registered ARM-A "at full batch by construction" to bound the GPU cost, and
§2 called that "Ling's own optimiser". The paper's sidecar, lines 131–132: *"For
the Tensor Basis Neural Network (TBNN), stochastic gradient descent was used, in
which the weights were updated after each training point."* Full-batch SGD at
the paper's rate is a different optimiser — **~3.4e5 times fewer updates per
epoch** on 341,717 training cells — and the frozen file removed the CPU lane's
learning-rate departure (D3) by introducing an update-count departure five
orders larger. The gate fired on the registered configuration; the threshold,
budget and arm are not rewritten (rule 2). The next pre-registration must
register **updates**, not epochs, and cost them (L-264).

**D-2 (idle waste, named, not absorbed).** The batch completed at
2026-08-24T08:03:58Z (the driver's own final status stamp; `driver.log` and
`spend.json` mtimes coincide). The session limit had killed the whole agent
fleet overnight, so no agent existed to report completion; the node idled
until the sync-back verification at 15:56:45Z — **7 h 52 m 47 s = 7.88 GPU-h
≈ $6.34 derived** at $0.8048/GPU-h, plus an unmeasured pre-launch idle (Sanaa
launched the node before 21:20Z on 2026-08-23; the launch time is not on this
box) and an unmeasured post-15:56:45Z idle until her console stop. Cause: the
completion→stop path depended on a live agent (L-265).

**D-3 (scoring cells).** 114 TEST cells with non-finite `b_RANS` dropped so
that every model and baseline is scored on identical cells — the convention
F.5(4) ratified at freeze; recorded in the grading JSON.

**D-4 (lane communications).** The execution and read-back lanes addressed
their interim reports to `claude`/`closure-supervisor` and bounced to the
chief, who relayed them. No number in this record came from a relay: every
figure above was re-read by the supervisor from `grading_gpu_ling.json`, the
`status_*.json` files, `spend.json` and the history CSVs after sync-back.

**D-5 (comparator witness, caught by the peer session's closure supervisor).**
`score_gpu_ling.py` writes no comparator sha or commit into its JSON, so the
artefact does not itself witness which comparator produced it. Repaired in the
record, not in the frozen script: `artefacts/grading_witness.json` (committed
with this file) carries the on-disk comparator's sha256 re-hashed in the same
invocation as the commit, asserted equal to the `11f93da6` blob and to the
frozen F.4 table, plus the grading JSON's own sha256 and byte size. A future
comparator writes its own hash into its output.

**Not a departure, recorded because a reader will look for it.** The fleet
kill did not touch the run: the driver was detached under `nohup`, its status
stamps are continuous (21:21:32Z → 08:03:58Z), no BLOCKED or REFUSED state was
ever written, and the cap guard never fired (10.71 of 60 GPU-h).

---

## 5. Compute — actual against registered, and the calibration

Rate **$0.8048/GPU-h**, `g6.xlarge` Linux on-demand us-east-2, **published
price list retrieved 2026-08-23** (`docs/GPU_CAPABILITY_STATE.md` §9).
Dollars **derived, not measured** — the box cannot read its own billing.

| item | registered / projected | actual |
|---|---|---|
| ARM-A TBNN, 5 × 200,000 full-batch epochs | (P0 rate 18.645 ms/epoch → 5.18 h) | **19,278.6 s = 5.355 h** (19.3 ms/epoch) |
| ARM-A MLP, 5 × 200,000 | (5.18 h at the TBNN rate — F.5(5) said the MLP would run under it) | **9,742.5 s = 2.706 h** (9.7 ms/epoch, 0.52×) |
| ARM-B search, 300 trial-runs × 400 epochs | (0.62 h at the TBNN rate — F.5(5) said mini-batch trials would run OVER it) | **9,309.3 s = 2.586 h** (77.6 ms/epoch mean, **4.2×**) |
| ARM-B retrain, 5 × 400 | (0.01 h) | 204.6 s = 0.057 h |
| G0 + P0 | — | 4.6 s |
| **total, `spend.json`** | **P0 projection 10.99 GPU-h**; registered range **12–52**; cap **60** | **10.7054 GPU-h gross = cleaned** (stages are hours-long by design; no solver stall rule applies) = **$8.62 derived** |
| run window (wall) | — | 21:21:29Z → 08:03:58Z = 10.708 h; inter-stage overhead 10 s |
| **waste, separately named** | 0 | **7.88 GPU-h idle after completion = $6.34 derived** (D-2), plus unmeasured pre-launch and post-sync idle |

**Ratios.** Actual/P0-projection **0.974**. Actual/registered-floor **0.892 —
below the 12–52 range.** Attribution: the registered range assumed a 5–20×
GPU-over-CPU throughput on a 0.78–1.5 s/epoch CPU basis; measured full-batch
throughput was 18.6 ms/epoch = **42–80×**, so the range's floor was twice too
high. Inside the projection, two errors cancelled: the F.5(5) caveat was
confirmed (mini-batch ARM-B trials ran **4.2×** the projected per-epoch cost)
and the MLP ran at **0.52×**. The calibration row is `docs/COST_CALIBRATION.md`
C-15.

---

## 6. What this arm did NOT do

No a-posteriori propagation (G4 not run — G3 fired). No test-case influence on
the search (VAL-only objective; TEST rows appear only in the prediction dump,
whose row indices the comparator verified against the clean dataset). No edit
to any script after the freeze (hashes re-verified on both machines after the
run). Nothing sent, filed, uploaded, posted or registered outside this box. The
other four GPU drafts were not started; they proceed only under
`docs/closure/GPU_REPRODUCTION_PLAN.md`'s own order and terms.

## 7. Artefacts

| what | where |
|---|---|
| frozen pre-registration | `PREREGISTRATION.md`, sha256 `61b2097f…1d97`, commit `e8309b6c` |
| driver / comparator / launcher | this directory, commit `11f93da6` |
| grading JSON (numbers only) | `/home/ubuntu/closure-data/tbnn_gpu/grading_gpu_ling.json` — NOT committed (bulk data rule); **its sha256 and the comparator that produced it are witnessed in `artefacts/grading_witness.json` (committed)**, because the JSON itself records no comparator sha — a defect the peer closure supervisor caught (D-5) |
| synced run directory: 6 `status_*.json`, `spend.json`, 15 `pred_*.npz`, 15 `hist_*.csv`, 10 `ck_*.pt`, `armb_optuna.db` | `/home/ubuntu/closure-data/tbnn_gpu/out/` (89,609,821 B, byte-identical to the node) |
| node root: `driver.log`, `driver.pid`, `pip_install.log`, driver copy | `/home/ubuntu/closure-data/tbnn_gpu/node_root/` |
| run window | `/home/ubuntu/closure-data/tbnn_gpu/run_window.json` (start 2026-08-23T21:21:29Z, live clock read) |

## CORRECTION — 2026-08-24T17:25:01Z — two lesson citations (pass 8 §40)

Two forward citations in §4 name lessons that belong to another team. Struck,
not rewritten (rule 6 form; this is a grading record, not a frozen
pre-registration, but the lab's convention is struck-not-rewritten and the lines
above are cited elsewhere by number).

- **Line 164** (disclosure **D-1**, the optimiser design defect). The citation
  ~~**(L-264)**~~ is struck and reads **(L-267)**.
  L-267 is *"A learning rate is not an optimiser — reproducing a paper's rate
  under a different update count is a different experiment, and a batch size
  chosen for the cost estimate silently changed the optimiser"*, whose own
  **Where it fired** names `Ling2016_TBNN/gpu/RESULTS.md` D-1, §3.
  L-264 is dafoam's W4 O2 re-buy lesson on a kernel-enforced memory cap.

- **Line 174** (disclosure **D-2**, the idle waste). The citation
  ~~**(L-265)**~~ is struck and reads **(L-268)**.
  L-268 is *"A detached job survives the fleet; the bill survives with it — the
  completion-to-stop path for a paid node must not depend on a live agent"*,
  whose own **Where it fired** names `Ling2016_TBNN/gpu/RESULTS.md` D-2, §5 and
  ledger row C-16. L-265 is dafoam's W4 O2 re-buy lesson on a spend prediction
  tested only by a run that stops for the predicted reason.

**Cause.** The draft's ids were written **ahead of** the `LESSONS.md` append and
reached **below** the tail, not past it: at the parent of `353925c7`
(`1a634bb2`) the maximum existing lesson id was **L-266**, so L-264 and L-265
were already occupied by dafoam when this record was drafted. `353925c7` itself
re-derived the tail correctly and created **L-267** and **L-268** — rule 11 was
applied in the file that *defines* an id and not in the file that *names* it.
The mechanism, as pass 8 puts it: a commit that assigns a new id must re-derive
it in every file that names it.

**Scope.** Confined to these two forward references. Every back-reference was
already correct and is unchanged — the `LESSONS.md` L-267/L-268 blocks,
`docs/DOCKET.md` D490, calibration ledger row C-16, and `docs/LAB_STATE.md`
(verified by pass 8, `docs/CROSS_TEAM_GATE_AUDIT.md` lines 1386–1391).

**No verdict moves.** No gate, threshold, cap, budget, label or measured number
in this record is touched by this correction. Pass 8's own row records the same:
*"Confined to the grading record; every back-reference is correct; no verdict
moves."*

**Source.** `docs/CROSS_TEAM_GATE_AUDIT.md` §40, lines **1370–1405** (pass 8,
verification LANE, CANDIDATE); summary row at line **1641**.

**lines whose number changed above this section: 0** — verified in the same
shell invocation as the commit by hashing the pre-correction body (the file's
first 249 lines) with `git hash-object` and comparing it to the HEAD blob of
this file, `4c8afddea6cc83c23e3cd28afbc27d19706af358`. Result stated in the
commit message.

## CORRECTION 2 — 2026-08-24T18:36:49Z — pass 8, believed at 8cbe716b

Two verdict-neutral items owed to this record by the verification supervisor's
own read of audit pass 8 — `docs/CROSS_TEAM_GATE_AUDIT.md` §82, commit
`8cbe716b`, stamped 2026-08-24T17:57:20Z, where **pass 8 is recorded BELIEVED in
full** after the supervisor re-derived all five gate labels from the grading JSON
against the frozen thresholds at `e8309b6c`. Struck, not rewritten (rule 6 form);
the table and prose above are unedited.

### (a) Line 22 — "identical reading per seed" is an overstatement, and the per-case reading

Pass 8, verbatim (§82): *"`RESULTS.md:22` "identical reading per seed" is an
overstatement — seed 2 beats b=0 on `alpha_15_13929_4048` (0.310588 vs
0.312796)"*.

The G1 row's *measured* cell (line 22) reads *"beats SST **0 of 8**, `b = 0`
**0 of 8**, train-mean **0 of 8** (per-case mean over 5 seeds, best-val;
identical reading per seed and for the final epoch)"*.

- ~~**identical reading per seed**~~ is **struck**. It reads: **the per-seed
  tallies are 0 of 8 against all three baselines on seeds 0, 1, 3 and 4; seed 2
  is 1 of 8 against `b = 0` — on `alpha_15_13929_4048` and on no other case —
  and 0 of 8 against SST and against the train-mean tensor.**
- Everything else in the cell **stands, unchanged and re-verified**: the three
  headline `0 of 8` tallies are the tallies of the **registered G1 statistic**
  (the per-case mean over the five seeds, best-val), and *"and for the final
  epoch"* is correct — the `pred_final` tallies are the same 0 of 8 / 0 of 8 /
  0 of 8 on the seed mean, with the same single seed-2 exception.

**The case seed 2 beats `b = 0` on, and by how much.** Re-read by this lane from
`/home/ubuntu/closure-data/tbnn_gpu/grading_gpu_ling.json` — the artefact §7
lists — at
`models["ARM-A TBNN [pred_best]"].per_seed["2"].per_case` against
`baselines.zero.per_case`; not from any summary field and not from pass 8's text:

| case | seed 2 `b_rms` | `b = 0` | ratio | below `b = 0`? |
|---|---|---|---|---|
| AR_14_Ret_180 | 0.861340 | 0.584175 | 1.4745 | no |
| AR_1_Ret_360 | 0.993210 | 0.599591 | 1.6565 | no |
| AR_3_Ret_360 | 0.849678 | 0.557973 | 1.5228 | no |
| NASA_2DWMH | 7.4832e+07 | 0.339821 | 2.2021e+08 | no |
| α05_4071_2024 | 0.352318 | 0.345719 | 1.0191 | no |
| α05_4071_4048 | 0.380451 | 0.379091 | 1.0036 | no |
| α15_13929_2024 | 0.385426 | 0.335471 | 1.1489 | no |
| **α15_13929_4048** | **0.310587543** | **0.312796084** | **0.9929** | **YES** |

**Margin on the one case it wins: 0.002208542 absolute, 0.7061 % below `b = 0`**
(0.310587543 against 0.312796084). It is the only sub-1.0 ratio in the row; the
next closest is `α05_4071_4048` at **1.0036**, i.e. **0.36 % above** `b = 0`
(0.380451 against 0.379091). On the same case seed 2 is **not** below the other
two baselines — SST reads **0.288872485** and the train-mean tensor
**0.225804652** there, both below seed 2's 0.310588. `pred_final` for seed 2 on
this case is the identical **0.310587543**, consistent with §2's statement that
best-val and final-epoch readings differ only on TBNN seed 1 and on ARM-B.

**Why no verdict moves.** G1's registered statistic is the per-case figure of the
**5-seed mean**, and on `α15_13929_4048` that mean is **0.317814688** (lo
0.310587543, hi 0.328567749, n = 5) — **above** `b = 0`'s 0.312796084 by
**0.005018603**. So the gate's own reading is still 0 of 8 against all three
baselines, and §8's *"failure to beat `b = 0` anywhere"* branch still fires on
its own terms. **G1 remains NOT A RESULT; the lane verdict remains NOT A RESULT.**
The seed-2 win is one seed on one of eight cases, 0.7 % on a case where SST and
the train-mean are both better still — a within-noise crossing of the weakest
baseline, not a result about the model.

### (b) Line 25 — the G4 VERDICT cell, which held `—`

Pass 8, verbatim (§82): *"the G4 cell is an em-dash outside the rule-1
vocabulary"* — and, on the gate itself, *"G4 capped (not run)"*.

The frozen pre-registration, verbatim, registers the consequence rather than a
verdict token. §8, `PREREGISTRATION.md:303` (blob frozen at `e8309b6c`):

> **"Capped verdict if G4 is not run: GATE REACHED, and no higher."**

and F.6, the same file at :499–500:

> *"Runs on the lab box only after G0-G3 are graded and only if G3 has not fired
> NOT A RESULT; … If G4 is not run the verdict is capped at GATE REACHED, as
> sec. 8 registers."*

- ~~**—**~~ is **struck**. The cell reads: **capped at GATE REACHED** — the
  registered consequence phrase, F.6's own words ("the verdict is capped at GATE
  REACHED").
- **Reason.** G4 was **not run**, and under F.6 it could not be: it runs *"only
  if G3 has not fired NOT A RESULT"*, and G3 fired NOT A RESULT on both TBNN
  models. The frozen file attaches no verdict token to a not-run G4; it attaches
  a cap on the **arm's** verdict, which is what the cell must carry.
- **Why not `PENDING`.** Rule 1 reserves `PENDING` for "not yet run" (a
  display/queue state). This arm's G4 will **never** run — F.6's precondition
  cannot now be met on this arm's artefacts — so `PENDING` would assert a queued
  future run that does not exist.
- **Why not a bare `GATE REACHED`.** That token in the cell would read as G4
  having reached a gate. It did not run; the cap is on the arm, not a grade of
  the gate.
- **The cap is moot here, and is stated so it cannot be misread as a lift.** The
  arm's verdict is **NOT A RESULT**, which is below GATE REACHED. A cap of GATE
  REACHED cannot raise it. Line 3's `# VERDICT: NOT A RESULT` and the lane
  verdict at lines 27–30 are untouched.
- **The frozen clause and pass 8 agree** — pass 8's own words for this row are
  *"G4 capped (not run)"*, which is the same reading. No SUPERVISOR flag is
  raised on this item.

### Scope

Confined to the two cells named. **No gate, threshold, cap, budget, label,
registered cost or measured number in this record is touched**, and neither item
alters the arm verdict or any of G0–G3. Pass 8 classifies both as
verdict-neutral, and the supervisor's own read at `8cbe716b` records the same
after re-deriving every gate label independently.

**Source.** `docs/CROSS_TEAM_GATE_AUDIT.md` §82 (commit `8cbe716b`, the
verification supervisor's own read: *"Pass 8 BELIEVED in full"*), the pass 8
body at §35–§47 (commit `9573db65`, CANDIDATE lane pass), and this lane's own
re-read of `grading_gpu_ling.json` for the numbers in (a).

**lines whose number changed above this section: 0** — verified in the same shell
invocation as the commit by hashing the pre-correction body (the file's first 300
lines, i.e. everything through CORRECTION 1) with `git hash-object` and comparing
it to the HEAD blob of this file, `e690bca3b4b6c30f3a0fc33e71a59c4da5dc6d3e`.
Result stated in the commit message.
