# A6 CRM wing-alone, rung N=16 (41,760 cells), np=1: THE REMAINING FIVE COMPONENTS — RESULTS

**Run 2026-08-22, DAFoam team LANE D.** Pre-registration: `PREREGISTRATION.md` in this directory,
committed **before any arm launched** (commit `baf4e68e`, subject *"dafoam team: A6 N=16 remaining
five components - pre-registration"*, blob `acfa5b9e2c7e3056f6b0f652c44f469876ecd76b`). **The frozen
file is verified to be the file that ran**: `git hash-object` of the working copy equals the committed
blob (`VERIFICATION_CHARTER.md` §2). **This file does not revise it.** Departures are recorded in §9
(Amendments), dated, and never by editing the frozen file.
**Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.**

**This is a PATCHED-IMAGE row** — `dafoam-idwarp-rot:v1`, `IDWARP_SO_MD5
85f59e87253e0a71a813f64ca6e4c425` asserted by the arm itself. It does not replace, merge with, or
re-grade the shipped-toolchain row at `../rung_n16_np1/RESULTS.md` §6.2. Two rows, never one.

---

## HEADLINE

**THE A6 N=16 NINE-COMPONENT TABLE IS NOW COMPLETE. EIGHT OF NINE ARE GRADED, ALL EIGHT AGREE, AND
THE NINTH IS FLAGGED BY NAME.** The five components nobody had re-measured — sitting at 57.62%,
67.93%, 57.06%, 90.17% and 82.79% from the noise-dominated step 1e-3 — come back at **1.359%,
1.733%, 1.032%, 0.389% and 0.569%** when the step is chosen against the measured noise. Nothing about
the derivative changed; only the reference did, for the second time on this rung and now on the
majority of it.

0. **THE GRADE: PASS on the graded set.** Eight components, vector-relative error
   **‖J_an − J_fd‖ / ‖J_fd‖ = 1.0432%**, **zero sign flips**, every component individually ≤ 5%,
   every plateau ≤ 3.7% against a registered 10% tolerance. `twist` idx6 remains **FLAGGED** and is
   excluded **by name**. **§4, §5.**

1. **All five predictions on the five components HIT, and so did all four instrument predictions.**
   Nine registered predictions, **nine HIT, zero MISS, zero NOT EVALUATED**. The bands were not
   generous — `patchV` idx0 was registered at ≤5% and landed at 0.569%; `twist` idx5, registered at
   ≤15% because it needed the largest step in the item, landed at **0.389%**, the best number in the
   nine-component table. **§6.**

2. **The mechanical step-selection rule works, and this was its first use.** Steps were fixed before
   the run as a function of the stored `|J|` and the registered `η` alone — never of any FD value.
   Every one of the ten registered steps cleared its predicted `C ≥ 5`, every component plateaued,
   and **not one of the five was flagged**. Registered falsifier (c) — *"more than one of the five
   flagged ⇒ the rule does not do what it was registered to do"* — did not fire. **§3.1.**

3. **The registered `η` was reproduced to four significant figures by this arm's own baseline.**
   Prediction P-η allowed ±20%; the measured last-200 peak-to-peak at `printInterval 10`, 20 samples,
   is **1.0910e-05** against a registered **1.0910e-05** — **ratio 1.000**. The cold A6 N=16 primal is
   bit-reproducible across items, images, days and now a fifth independent container run
   (`FD_BASELINE_CD 0.03506349413916734`, exact). **§2.2.**

4. **THE TRIVIAL BASELINE FIRED HARDER THAN LAST TIME, AND THE WAY IT FAILED IS ITSELF THE FINDING.**
   The re-bought `step = 1e-8` probe on `patchV` idx1 returns **−28.746957145275864** against an
   adjoint of `+9.01684e-03` — **100.031% and a SIGN FLIP**. The fixed-reference item's identical
   probe on the identical case, image and harness returned **+152.94**. **Same instrument, same
   configuration, two runs, and the answers differ by a factor of 5.3 AND in sign.** A wrong-step
   probe is not merely inaccurate — it is **not even reproducible**, which is a stronger demonstration
   that it measures round-off than any single large number could be. **§4.3.**

5. **A step that clears the noise floor can still be noise-limited, and `twist` idx5 shows it.**
   Its estimate improves from 3.316% at `1e-1` (C = 6.74×) to **0.389%** at `2e-1` (C = 13.87×). The
   registered reasoning for its wide band was *truncation* at the larger step; the measurement says
   the opposite — it was still **noise**-limited at the smaller one. **The prediction HIT and its
   stated reason was wrong, and that is recorded as a defect in the reasoning, not smoothed over.**
   **§6, §7.3.**

6. **The N=29 gate, under the two readings registered before the measurement.** **Reading 1**, the
   charter's text (PASS requires ≤5% aggregate **and zero flagged components**): **`NOT MET`**, and no
   FD arm can meet it, because `twist` idx6 is structurally ungradeable on this rung. **Reading 2**,
   subset-complete (every component graded or flagged by name with a measured reason, none merely
   un-measured): **`GATE REACHED`** — this arm closed the last five. **Neither reading is chosen
   here; the gate is Sanaa's.** **Under both readings `N=29` is `NOT RUN`, and nothing was staged,
   queued or costed for it.** **§8.**

7. **Cost: 39.15 core-min measured against a registered 46.0 and a hard ceiling of 60.0** — 14.9%
   under the registered figure, 34.8% under the ceiling, **zero waste, zero failed arms, zero
   re-runs**. **\$0.0335. §2.3.**

Raw log `/home/ubuntu/certonomous-runs/P3-a6-n16-rem/rem.log`; ledger `.../ledger.txt`; RSS samples
`.../rss_rem.txt`; queue `.../queue_rem.out`; analysis `.../analyse.py`; plan `.../fdplan_rem.json`.

---

## 1. The arm as executed

| arm | task | `endTime` | `primalMinResTolDiff` | `primalMinIters` | `printInterval` | rc | wall | core-min | peak RSS |
|---|---|---|---|---|---|---|---|---|---|
| **`rem`** | `fdsub`, 23 primals | 1000 | **1.0e4** (registered) | **1000** (= `endTime`) | **10** | **0** | **2,349 s** | **39.15** | **0.657 GiB** |

**Every registered assertion passed, and none is reported as passed without its value.**

| assertion (prereg §2) | required | measured |
|---|---|---|
| image identity | `IDWARP_SO_MD5 85f59e87253e0a71a813f64ca6e4c425` | **exact**, `ASSERT_MD5 OK` |
| `transonicPCOption` **activity proof** | `transonicPCOption 1;` in the option dump | **present** |
| decomposition | `nProcs : 1` | **1** |
| cold start | first `cumulative = -0.00504349133910657` | **exact** |
| **baseline objective** | `FD_BASELINE_CD 0.03506349413916734` | **exact** |
| mesh identity | `points.gz` md5 `11b84f0de5fdf2d3e947fee8cea412a9` | **equal to the fixed-reference tree** |
| script identity | `runScript.py` md5 `0de915d21166a91a9a54b37ab11214cf` | **equal** |
| harness identity | `gen_arm.py` md5 `ff85f67c304079349d378383ef46e67c` | **equal, byte-for-byte** |

**The `FD_BASELINE_CD` assertion is the load-bearing one and it did three jobs at once**, exactly as
prereg §2 registered: it proves the start was cold, it proves the primal state is the one the stored
adjoint was linearised about, and it proves registered **Edit 4 (`primalMinIters 1000`) is
numerically inert** — a run that had been altered by it could not have reproduced the value to the
last digit. **This is the fifth independent reproduction of `0.03506349413916734`** on this case
(shipped image, patched image, `s1d` `REPEAT_CALL 0`, `s2bpv`, `rem`).

**No arm is void on any registered ground. Nothing was killed, stopped, throttled or retried.**

## 2. Instrument controls, before the derivatives are read

### 2.1 The `-1e10` false-convergence exit did not fire, and it was closed by construction

Registered Edit 4 set `primalMinIters = 1000 = endTime`, so `DASolver.C:188`'s second clause
(`timeIndex > primalMinIters`) can never hold inside the run (N-D17). The string
`Minimal residual -10000000000` appears **zero** times in `rem.log`, and all 23 primals ran their
full 1,000 iterations. **The fixed-reference item's graded FD arms did not carry this edit**; they
were not bitten by it either, and the identical baseline CD across both is what shows the edit
changed nothing.

### 2.2 P-η — the noise control. **HIT, and it reproduced to four significant figures**

| | value | samples | source |
|---|---|---|---|
| **registered `η`** (prereg §4.1, fixed before the run) | **1.0910e-05** | 20 | fixed-reference `s1a`, `printInterval 10` (N-D13) |
| **measured here**, this arm's own baseline primal, last 200 iterations | **1.0910e-05** | **20** | `rem.log` |
| ratio | **1.000** | | registered band ±20% |

**P-η HIT.** The registered consequence branch — re-state clearances at both values and flag any
component that clears at one `η` and not the other — **was not needed and is recorded as not
needed**, rather than quietly omitted. `η` is unchanged, so every clearance below is the registered
arithmetic with no substitution anywhere.

### 2.3 Cost — measured against a registered 46.0 and a hard ceiling of 60.0

| | core-min | note |
|---|---|---|
| pre-launch reading (`cat`, `md5sum`, `/proc`; **no container started**) | **0.000** | registered at 0.0; **HIT** |
| **arm `rem`**, 23 primals | **39.150** | the whole item |
| **TOTAL SPENT** | **39.150** | **65.3% of the ceiling**; **14.9% under the registered 46.0** |
| of which waste | **0.000** | no failed arm, no re-run, no restage |
| arms not run | **0** | nothing `PENDING` |

**\$ at \$0.0513/core-hour** (owner-stated, CLAUDE.md rule 12): **39.150 core-min = 0.6525 core-h =
\$0.0335.** **Reported-by-owner, not measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

**Basis versus measurement, and the contention assumption graded as a prediction.**

| | value |
|---|---|
| registered basis (fixed-reference `s2btw`: 1,365 s / 13 primals, np=1, load ~20–24) | **105.0 s per primal** |
| corroborating basis (`s2bpv`: 738 s / 7 primals, `patchV`, no warp) | 105.4 s per primal |
| **measured here** (2,349 s / 23 primals) | **102.1 s per primal** |
| ratio measured / basis | **0.973** |

**The basis was 2.7% conservative and the item finished under it.** The registered contention
assumption was that the 105.0 s figure is contention-inclusive at load ~20–24 and that an idle box
would give ≈95 s (N-D10's 1.104×). **The box was quieter than the basis for most of this run** — Lane
A's `p3_a3_patched` had exited before the launch window opened (§9 Amendment 2) — and the measured
102.1 s sits between the contended 105.0 and the idle-projected 95.1, which is what a partially
relieved box should give. **The ×4 `cores × wall` ambiguity the fixed-reference item had to disclose
does not exist here**: `--cpus=1` at np=1 makes `ranks × wall` and `cores × wall` the same number.

**Billing basis: `ranks × wall`, np = 1, `--cpus=1`, whole clock** (`patched_build/subpclu/BUILD.md`
§2; `DAFOAM_CHARTER.md` §12).

### 2.4 P-RSS. **HIT, by 2.3× against the prediction and 18× against the cap**

Predicted ≤ 1.5 GiB, hard cap 12 GiB (`--memory=12g`). **Measured peak 0.657 GiB**, read from field
`$3` of `docker stats` (the field the predecessor's script got wrong). **No sample approached the
cap; no memory falsifier fired; the run was not stopped by memory and claims nothing about the
envelope beyond the sample** (`DAFOAM_CHARTER.md` §7).

## 3. The five components bought here — the full sweep, every step, both failure branches visible

`DAFOAM_CHARTER.md` §3 requires the sweep reported per component with its failed steps as rows.
Each component has **three** points: the predecessor's `1e-3` carried in at **zero cost**, and the two
registered steps. **Clearance below is computed with the MEASURED `|J_fd|`**, as prereg §4.1
registered; the pre-registered proxy value using `|J_adj|` is given beside it wherever the two differ
materially, because **a noise-dominated FD estimate inflates its own `|J_fd|` and therefore flatters
its own clearance** — which is precisely why the registered *gate* was written on the `|J_adj|` proxy
and not on this column.

| DV, idx | step | FD derivative | rel err vs adjoint | `C` (measured `\|J_fd\|`) | `C` (registered proxy `\|J_adj\|`) | sign |
|---|---|---|---|---|---|---|
| **`patchV` 0** | 1e-3 *(inherited)* | `+4.260410000e-03` | **82.786%** | 0.78× | **0.13×** | SAME |
| | 1e-1 | `+7.332506902e-04` | 0.020% | 13.44× | 13.44× | SAME |
| | **3e-1 — GRADED** | `+7.375983890e-04` | **0.569%** | **40.56×** | 40.33× | SAME |
| **`twist` 1** | 1e-3 *(inherited)* | `-4.130860000e-03` | **57.618%** | 0.76× | **0.32×** | SAME |
| | 3e-2 | `-1.768333907e-03` | 0.996% | 9.73× | 9.63× | SAME |
| | **1e-1 — GRADED** | `-1.774854641e-03` | **1.359%** | **32.54×** | 32.09× | SAME |
| **`twist` 2** | 1e-3 *(inherited)* | `-4.581510000e-03` | **67.927%** | 0.84× | **0.27×** | SAME |
| | 3e-2 | `-1.391684719e-03` | 5.588% | 7.65× | 8.08× | SAME |
| | **1e-1 — GRADED** | `-1.444417199e-03` | **1.733%** | **26.48×** | 26.94× | SAME |
| **`twist` 4** | 1e-3 *(inherited)* | `-1.461850000e-03` | **57.061%** | 0.27× | **0.12×** | SAME |
| | 5e-2 | `-6.356574723e-04` | 1.252% | 5.83× | 5.75× | SAME |
| | **1e-1 — GRADED** | `-6.212861219e-04` | **1.032%** | **11.39×** | 11.51× | SAME |
| **`twist` 5** | 1e-3 *(inherited)* | `-3.861320000e-03` | **90.166%** | 0.71× | **0.07×** | SAME |
| | 1e-1 | `-3.675408393e-04` | 3.316% | 6.74× | 6.96× | SAME |
| | **2e-1 — GRADED** | `-3.782595043e-04` | **0.389%** | **13.87×** | 13.92× | SAME |

**The plateau test, registered at 10% before any estimate existed:**

| component | `\|d(s_hi) − d(s_lo)\| / \|d(s_hi)\|` | verdict |
|---|---|---|
| `patchV` 0 | **0.589%** | plateau |
| `twist` 1 | **0.367%** | plateau |
| `twist` 2 | **3.651%** | plateau |
| `twist` 4 | **2.313%** | plateau |
| `twist` 5 | **2.834%** | plateau |

**All five plateau, the worst at 3.651% against a 10% bar — and against the 83.53% that flagged
`twist` idx6.** The registered tolerance separated the two populations it was calibrated on without
ever being adjusted.

### 3.1 The step-selection rule, scored

Prereg §4.2 fixed a mechanical rule — `s_lo` = smallest ladder rung with predicted `C ≥ 5`, `s_hi` =
smallest rung at ratio ≥ 2 — computed from the stored `|J|` and the registered `η` and **from nothing
else**. First use; here is its report card:

* **All ten registered steps cleared `C ≥ 5` on the measurement**, not merely on the proxy: the
  smallest measured clearance at any registered step is **5.83×** (`twist` 4 at `5e-2`), against a
  predicted 5.75×. **The proxy predicted the measurement to within 8% on every one of the ten.**
* **Zero of the five were flagged.** Registered falsifier (c) required more than one flagged to
  refute the rule; **it did not fire.**
* **The rule chose a different pair for four of the five components** — `{3e-2, 1e-1}` twice,
  `{5e-2, 1e-1}`, `{1e-1, 2e-1}`, `{1e-1, 3e-1}` — which is the point: a single hand-picked pair
  could not have cleared the floor on components spanning 4.6× in `|J|`.
* **What it does NOT establish.** One item, five components, one case, one `η`. The rule has not been
  tried where the proxy `|J_adj|` is itself wrong — which is the case it would be worst at, since it
  sizes the step from the very quantity under test. **§7 limitation 8.**

## 4. The nine-component table

### 4.1 The table

**The three already-verified components use their STORED values from `../rung_n16_fixed_reference/RESULTS.md`
§6.8 (commit `66f42398`) and were NOT re-bought.** The five bought here are the measurements of §3.
`twist` idx6 is carried at its flagged status from that same item and was not touched.

| # | DV, idx | adjoint (stored, patched) | FD reference (graded step) | rel err | `C` | plateau | status | origin |
|---|---|---|---|---|---|---|---|---|
| 1 | **`patchV` 0** | `+7.334000e-04` | `+7.375983890e-04` @ 3e-1 | **0.569%** | 40.56× | 0.59% | **GRADED** | this arm |
| 2 | **`patchV` 1** | `+9.016840e-03` | `+8.932878291e-03` @ 3e-2 | **0.940%** | 49.13× | 0.58% | **GRADED** | stored, `66f42398` |
| 3 | **`twist` 0** | `-2.100900e-03` | `-2.137369846e-03` @ 1e-1 | **1.706%** | 39.18× | 4.17% | **GRADED** | stored, `66f42398` |
| 4 | **`twist` 1** | `-1.750730e-03` | `-1.774854641e-03` @ 1e-1 | **1.359%** | 32.54× | 0.37% | **GRADED** | this arm |
| 5 | **`twist` 2** | `-1.469450e-03` | `-1.444417199e-03` @ 1e-1 | **1.733%** | 26.48× | 3.65% | **GRADED** | this arm |
| 6 | **`twist` 3** | `-1.010980e-03` | `-9.929378034e-04` @ 1e-1 | **1.817%** | 18.20× | 0.78% | **GRADED** | stored, `66f42398` |
| 7 | **`twist` 4** | `-6.277000e-04` | `-6.212861219e-04` @ 1e-1 | **1.032%** | 11.39× | 2.31% | **GRADED** | this arm |
| 8 | **`twist` 5** | `-3.797300e-04` | `-3.782595043e-04` @ 2e-1 | **0.389%** | 13.87× | 2.83% | **GRADED** | this arm |
| 9 | **`twist` 6** | `-1.361900e-04` | **none exists** | — | max **2.42×** | **83.53%** | **FLAGGED** | `66f42398` |

### 4.2 The aggregate, named as the statistic it is

> **Vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖` over the EIGHT GRADED components = 1.0432%.**
> **Sign flips: 0. Flagged and excluded BY NAME: `twist` idx6. Not reached: none.**
> **This is a vector norm and it is NEVER to be compared against the DAFoam papers' per-component
> average** (`DAFOAM_CHARTER.md` §2; He *et al.* C&F 168 §3.1 and AIAA J §2.4.2 report per-component
> and per-row errors, Kenway *et al.* PAS 2019 §5.1 reports significant digits — **no paper uses a
> vector-norm relative error**).

**Decomposition and sensitivities, so the number is auditable rather than merely stated:**

| set | components | aggregate |
|---|---|---|
| **the eight graded, at the registered graded steps** | 8 | **1.0432%** |
| the three stored alone | 3 | **1.0099%** — reproduces `66f42398`'s published figure exactly |
| the five bought here alone | 5 | **1.4185%** |
| **sensitivity: the same eight at the LOWER registered step** | 8 | **1.2921%** |
| *(NOT the aggregate)* if flagged `twist` idx6 were wrongly folded in at its best step | 9 | *1.0440%* |

**Three things this decomposition is for.** (i) The three-component sub-aggregate reproducing
**1.0099%** proves the arithmetic used here is the arithmetic that produced the published number, so
the 1.0432% is not a new statistic quietly substituted for the old one. (ii) The lower-step
sensitivity, **1.2921%**, shows the aggregate is not an artefact of the step-selection rule's
preference for the higher-clearance step: it moves by 0.25 percentage points and stays deep inside
the PASS band either way. (iii) **The last row is shown precisely because it is tempting.** Folding
the flagged component in would *lower* nothing and *raise* almost nothing — 1.0432% → 1.0440% — so a
reader might ask why bother excluding it. **It is excluded because the rule says so, not because the
number would move.** A flag that is honoured only when it is expensive is not a flag.

### 4.3 The trivial baseline — RE-BOUGHT, and it failed in a new and better way

Prereg §6.2 declined the Charter-§4 baseline by name, **conditionally**, and the condition fired
(§9 Amendment 1), so it was bought:

```
FD_DERIV dv=patchV idx=1 step=1e-08 deriv=-28.746957145275864
```

| | value | vs adjoint `+9.01684e-03` | clearance |
|---|---|---|---|
| **this item** | `-28.746957145275864` | **100.031%**, and the **SIGN IS FLIPPED** | **1.65e-05×** |
| fixed-reference item, identical probe (`66f42398` §6.5) | `+152.94101058174746` | 99.9941% | 1.65e-05× |

**The instrument that returns 0.020%–1.733% at steps with 5.8–40.6× clearance returns a
sign-flipped answer three orders of magnitude too large at a step with 1.65e-05× clearance.** The
0.569% and its siblings are therefore properties of the derivative, not of a harness incapable of
returning a large number (`DAFOAM_CHARTER.md` §4). The registered falsifier — a trivial baseline
≤ 5%, which *"would invalidate every FD number in this item"* — **did not fire.**

> **AND THE DIFFERENCE BETWEEN THE TWO RUNS IS THE REAL FINDING.** Same case, same image, same
> `gen_arm.py` (md5-identical), same driver, same DV, same step, same objective — and the two
> answers are **+152.94** and **−28.75**, differing by a factor of 5.3 **and in sign**. The reason
> is arithmetic: at `s = 1e-8` a central difference divides by `2e-8`, so the solve-to-solve noise
> `δ_repeat = 2.2104e-06` (N-D15) alone produces a spurious derivative of order **1.1e+02** — which
> brackets both observed values. **A wrong-step probe is not just inaccurate; it is not reproducible,
> and its sign is a coin flip.** A single large number from one such probe could in principle have
> been a real large derivative; two irreproducible ones of opposite sign cannot be. **This is a
> strictly stronger discharge of `DAFOAM_CHARTER.md` §4 than the single-run version, and it was
> obtained only because a registered md5 condition forced a re-buy nobody would have chosen.**

## 5. Verdicts — per component, in the lab vocabulary

### 5.1 The rung, component by component

| item | verdict |
|---|---|
| `patchV` idx0 — 0.569% at `C` 40.56×, plateau 0.59% | **PASS** |
| `patchV` idx1 — 0.940% at `C` 49.13× *(stored)* | **PASS** |
| `twist` idx0 — 1.706% at `C` 39.18× *(stored)* | **PASS** |
| `twist` idx1 — 1.359% at `C` 32.54×, plateau 0.37% | **PASS** |
| `twist` idx2 — 1.733% at `C` 26.48×, plateau 3.65% | **PASS** |
| `twist` idx3 — 1.817% at `C` 18.20× *(stored)* | **PASS** |
| `twist` idx4 — 1.032% at `C` 11.39×, plateau 2.31% | **PASS** |
| `twist` idx5 — 0.389% at `C` 13.87×, plateau 2.83% | **PASS** |
| **`twist` idx6** — max `C` 2.42×, plateau 83.53%, no reference exists at any feasible step | **NOT A RESULT** — flagged, excluded by name |
| **graded aggregate** (vector-relative error, 8 components) | **PASS**, **1.0432%**, zero sign flips |
| registered trivial baseline at `1e-8` | **PASS** — 100.031% with a sign flip; the instrument can still fail |
| P-η noise control | **PASS** — 1.0910e-05, ratio 1.000 |
| `shape` (~10² components) | **PENDING** — never graded by any item in this family, excluded on cost |
| **the item as a whole** | **PASS** |

### 5.2 Is the A6 N=16 adjoint verified?

> **VERIFIED ON EIGHT OF THE NINE GRADED COMPONENTS, TO ~1%. ONE COMPONENT HAS NO REFERENCE AT ALL,
> AND THE `shape` GROUP IS STILL UNTOUCHED.**
>
> * **Verified:** `patchV` idx 0 and 1, `twist` idx 0, 1, 2, 3, 4, 5 — **eight components**,
>   individually 0.389%–1.817%, aggregate **1.0432%**, zero sign flips.
> * **Not verified, flagged, named:** `twist` idx6 — the wing-tip twist derivative. **`|J|` =
>   1.362e-04 is too small for any feasible step to lift it over the noise floor**; the only lever
>   left is `η` itself, which is the unbought `useMeanStates` item on Sanaa's desk.
> * **Not addressed at all:** the `shape` group.
>
> **The predecessor rung's headline — *"the 517-iteration converged adjoint is unverified except on
> that one AoA derivative"* — is now superseded on eight of nine components.** The fixed-reference
> item's *"3 of 9 verified, 1 ungradeable, 5 never touched"* is superseded on the five.

**What the eight license, and what they do not.** Six of the eight are `twist` components, which
**do** cross the `DVGeo → warpDeriv` chain (`../rung_n16_np1/RESULTS.md` §6.4 proved all seven move
under the rotation patch), so this is emphatically **not** a `patchV`-only clearance — the mesh-warp
derivative chain is exercised across the whole span from root to tip and agrees at ~1.4%.
**It licenses nothing about `shape`, nothing about full-size A6, and nothing about np > 1.**

## 6. Predictions, scored honestly

| # | registered | measured | outcome |
|---|---|---|---|
| **P1** | `patchV` 0: graded, plateau ≤10%, sign **positive**, rel err **[0%, 5%]**, central ~2% | GRADED, plateau **0.589%**, sign SAME, **0.569%** | **HIT** (all four clauses) |
| **P2** | `twist` 1: graded, plateau ≤10%, sign negative, **[0%, 5%]**, central ~2% | GRADED, plateau **0.367%**, SAME, **1.359%** | **HIT** |
| **P3** | `twist` 2: graded, plateau ≤10%, sign negative, **[0%, 5%]**, central ~2% | GRADED, plateau **3.651%**, SAME, **1.733%** | **HIT** |
| **P4** | `twist` 4: graded, plateau ≤10%, sign negative, **[0%, 8%]**, central ~3% | GRADED, plateau **2.313%**, SAME, **1.032%** | **HIT** |
| **P5** | `twist` 5: graded, plateau ≤10%, sign negative, **[0%, 15%]**, central ~5% | GRADED, plateau **2.834%**, SAME, **0.389%** | **HIT** on the band; **the stated REASON was wrong — §7.3** |
| **P6** | 8 graded, 1 flagged (`twist` idx6) by name, zero sign flips, aggregate **[0.8%, 3.0%]**, central 1.3% | 8 graded, 1 flagged, 0 flips, **1.0432%** | **HIT** (all four clauses) |
| **P-η** | this arm's own last-200 p2p within ±20% of 1.0910e-05 | **1.0910e-05**, ratio **1.000** | **HIT** |
| **P-RSS** | ≤1.5 GiB; cap 12 GiB | **0.657 GiB** | **HIT** |
| **P-COST** | 36.8 predicted, 46.0 registered, 60.0 ceiling | **39.15** | **HIT** |

**Nine registered predictions, nine HIT, zero MISS, zero NOT EVALUATED — and a clean sweep is a
reason for scrutiny, not for satisfaction.** The honest account of why is that these bands were not
guesses: they were interpolations inside a bracket **already measured on this exact case, image,
harness and step ladder** by the fixed-reference item three hours earlier (`twist` idx0 at C 39.18 →
1.706%, `twist` idx3 at C 18.20 → 1.817%, `patchV` idx1 at C 49.13 → 0.940%). **A prediction made
between two measured points on the same instrument is a cheap prediction, and this record says so
rather than claiming foresight.** The one genuinely open question — whether the two smallest
components could be lifted over the floor at all — is the one where the *reasoning* failed even
though the band held (§7.3). **No registered falsifier fired anywhere in the item.**

## 7. What this item cannot see

**Prereg §9's nine limitations stand unchanged and unweakened.** Restated where measurement sharpened
them, plus four created by this run.

1. **`twist` idx6 has no reference at all** — not a bad one, a missing one. Nothing here says whether
   the adjoint is right on it, and this item added no instrument that could.
2. **`shape` (~10² components) is still not graded**, by any pre-registration in this
   family. **A nine-component table is not the whole gradient.**
3. **The adjoint column is INHERITED, not re-run**, and OpenMDAO printed it at numpy's default **6
   significant figures**, which caps every agreement claim here at about that precision. It was
   re-read from the raw log (`P2-a6-n16/patched.log:4993-5022`) rather than from a table, for all
   nine components — including the five this item graded, which the fixed-reference item's §3.3 check
   did not cover.
4. **No non-FD reference exists on this case.** Forward-mode AD returns `nan` (N-D16). FD carries the
   reference alone, and `DAFOAM_CHARTER.md` §2's duty to reach for a non-FD reference was discharged
   at cost by the fixed-reference item, not by this one. **This item did not reach again because the
   reach was already made and its answer was NOT AVAILABLE.**
5. **`np = 1` only** (`DAFOAM_CHARTER.md` §5; N-D12; L-229).
6. **It cannot separate truncation from noise above the graded step.** Three points per component
   resolve the *noise* branch (all five `1e-3` points are in it) and a plateau; **none of the five has
   a measured truncation branch**, so nothing here says where the plateau ends.
7. **It cannot see a systematic bias common to every FD step.** `η` measures scatter. An offset shared
   by all steps would be invisible to every instrument in this item, and the only thing that could
   have caught it — forward AD — does not run on this case.

**Four new ones, created by this run:**

8. **The step-selection rule of §3.1 is validated on one case only, and on the easy side of its own
   assumption.** It sizes the step from `|J_adj|` — the quantity under test. Here the adjoint turned
   out to be right, so the proxy was good. **On a rung where the adjoint is wrong by an order of
   magnitude, the rule would size the step from a wrong number and could register steps that cannot
   grade.** That failure mode is unmeasured and this record does not claim otherwise.
9. **The 100.031% trivial baseline is one draw from a distribution, and so was the 152.94%.** What is
   established is that the `1e-8` probe is irreproducible in magnitude and sign; **the distribution
   itself is characterised by two samples and that is not a characterisation.**
10. **`patchV` idx0 is a velocity-magnitude derivative that the optimiser holds FIXED**
    (`runScript.py:202`, `lower=[U0, 0.0]`, `upper=[U0, 10.0]`). It is a real entry in the gradient
    table and it is now verified, but **no optimisation on this case would ever move it**, so its
    verification carries less operational weight than the `twist` components'.
11. **Nothing here re-opens full-size A6.** It remains `BLOCKED` twice over — memory at 94.7–116 GiB
    against a 30 GiB box **and** conditioning independently (`DAFOAM_CHARTER.md` §7). This item can
    only change the *input* to Sanaa's N=29 decision, never take it.

### 7.3 The one place the reasoning was wrong inside a prediction that HIT

Prereg P5 registered `twist` idx5's wide `[0%, 15%]` band with this reason: it needs the largest step
in the item (`2e-1`), **truncation** grows as `s²`, so the largest step is the most exposed. The
measurement says the opposite: the estimate at `2e-1` (**0.389%**, C 13.87×) is **8.5× better** than
at `1e-1` (3.316%, C 6.74×). **`twist` idx5 was still noise-limited at `1e-1`, not truncation-limited
at `2e-1`.** The same shape appears on `twist` idx2 (5.588% at C 7.65× → 1.733% at C 26.48×).

> **The general statement, which is what makes this worth recording:** clearing `C ≥ 5` makes a
> component *gradeable*; it does not make it *converged*. Across the five components bought here,
> every one improved as clearance rose, and the two whose lower step sat nearest the bar (6.74× and
> 7.65×) improved the most. **A clearance bar is a floor, not a target, and a component sitting just
> above it should be read as marginal even when its plateau passes.**

## 8. Sanaa's N=29 gate

**Sanaa's condition, as held by this lane: N=29 is approved ONLY if N=16 passes on the patched image.**
Prereg §6.3 registered **both** readings of "passes" **before** the measurement and committed this
record to reporting under both and choosing neither. That is done here.

> ### READING 1 — the charter's text. **THE GATE IS `NOT MET`.**
>
> `DAFOAM_CHARTER.md` §2 grades a table **PASS at ≤ 5% aggregate with ZERO FLAGGED COMPONENTS**. The
> aggregate is 1.0432% and the flagged count is **one**. **`twist` idx6 is flagged, and the
> fixed-reference item established that it is structurally FD-ungradeable on this rung** — maximum
> clearance 2.42× at the largest defensible step, plateau disagreement 83.53%. **No FD arm can meet
> this reading**, this one included; it would take a reduction in `η` itself.

> ### READING 2 — subset-complete. **`GATE REACHED`.**
>
> Every one of the nine components is now either **graded inside the band** (eight, aggregate
> 1.0432%, zero sign flips) or **flagged by name with a measured reason** (one). **None is merely
> un-measured** — which was the fixed-reference item's stated reason for declaring the gate unmet
> (*"a gate that says 'N=16 passes' cannot be read as met while the majority of the graded row is
> untouched"*). **This arm closed the last five, which was the whole of what that item said was
> missing.**

> ### **`N=29` IS `NOT RUN`, UNDER EITHER READING.**
>
> **Nothing for N=29 was launched, staged, queued, meshed or costed by this item.** A lane does not
> launch a rung because a gate it graded came out favourably: approval of an item is approval of
> **its** cap, not a new ceiling (CLAUDE.md rule 9), and **the reading of Sanaa's own gate is Sanaa's,
> not this lane's** (rule 7; `SUPERVISION_CHARTER.md` §4). **The two readings are laid out above so
> that she can take the decision on a complete table rather than a partial one — which is the entire
> deliverable of this item.**

**What the decision now rests on, stated plainly for her desk.** Under Reading 1 the gate can only be
met by making `twist` idx6 gradeable, and the only lever is `η` — the `useMeanStates` + `fieldAverage`
item, **~5 core-min, \$0.004**, already priced on her desk by `66f42398` §11 and still unbought.
Under Reading 2 the gate is met now. **The gap between the two readings is one component out of nine,
worth 5 core-min to close, and this lane is not authorised to decide which reading governs or to buy
the closing arm.**

## 9. Amendments — departures from the frozen pre-registration, dated

**Amendment 1 (2026-08-22, 20:09Z, BEFORE launch) — `run_arm.sh` differs on two infrastructure lines,
so the registered VOID condition of prereg §6.2 fired and the trivial baseline was RE-BOUGHT.**
Prereg §6.2 declined the Charter-§4 trivial baseline by name — `patchV` idx1, central, `step = 1e-8`,
already bought by the fixed-reference item (`66f42398` §6.5, **99.9941%**) — **on the condition** that
`gen_arm.py` and `run_arm.sh` carry the md5s of the tree that produced that number, and registered
that *"if any of those md5s differs at launch the decline is void and the baseline is re-bought."*
`gen_arm.py` matches byte-for-byte (`ff85f67c304079349d378383ef46e67c`). `run_arm.sh` **cannot**: it
hard-codes its own run root and container name, and this item has a different run root. The complete
diff is two lines and is pasted rather than described:

```
6c6
< BASE=/home/ubuntu/certonomous-runs/P3-a6-n16-ref
---
> BASE=/home/ubuntu/certonomous-runs/P3-a6-n16-rem
11c11
< NAME="p3a6_$ARM"
---
> NAME="p3a6rem_$ARM"
```

md5 `6bd7e413a5d11edb4c8d0958613934a0` against the registered `5e2d0724a2a2b07ad1c92bdc40b896dc`.
**Nothing that touches the solver, the FD driver, the assertions, the RSS extractor's field `$3` or
the ledger changed.** The registered condition does not admit that judgement, and it was not made:
**the baseline was re-bought**, as fdplan entry 11, taking the plan from 21 primals to **23**.
**This is the registered branch firing, not a departure from it** — and §4.3 shows the outcome was
strictly better evidence than the decline would have been. **Cost of the re-buy: 2 primals,
3.40 core-min.** Recorded in the ledger at launch, before the arm ran, so the re-buy cannot be read
as a response to any result.

**Amendment 2 (2026-08-22, 20:12Z) — Lane A's A3 container was already gone when the window opened.**
Prereg §8.2 registers that `p3_a3_patched` holds the older claim on the box and that this item may run
beside it at one core (team cap 8; A3 takes 4, this arm 1). At 20:03Z `docker ps` showed
`p3_a3_patched` up 10 minutes at `--cpus=4 --memory=12g`; when the preflight passed at **20:12:15Z**
it was no longer running, which is why `free_cores` read **3** rather than the **−1** measured at
20:03Z. **No A3 container was stopped, throttled, paused or signalled by this lane** (prereg §8.2
rule 3), and nothing was waited on beyond the registered gate. Recorded because the cost basis was
measured under contention this arm then did not fully experience (§2.3).

**Amendment 3 (2026-08-22, 20:12Z) — the launch window opened on the second poll, and the registered
condition was applied unchanged.** Prereg §8.1: `MemAvailable ≥ 12 GiB` **and** `free_cores ≥ 1`,
`free_cores = 16 − median-of-5 runnable`, polled 60 s × 240, gate run as its own command (L-230).

```
2026-08-22T20:11:11Z preflight waiting MemAvailableGiB=13 runnable_med5=17 free_cores=-1 tries=0
2026-08-22T20:12:15Z PREFLIGHT OK       MemAvailableGiB=15 runnable_med5=13 free_cores=3  tries=1
```

**The 12 GiB memory floor was neither departed from nor argued down**, and this lane did not move it
— it is Sanaa's (prereg §8.1). **It cost 64 seconds of wall and nothing in core-minutes**, since an
arm that has not launched bills nothing. The fixed-reference item's standing recommendation to lower
the floor on measured grounds is **carried forward untaken**, and this run adds one more datum for
it: **peak RSS 0.657 GiB against a 12 GiB floor** (§2.4).

**No other departure. No arm was retried, re-staged, killed or stopped; no cap was raised; no step
was added, dropped or re-selected after any value was seen; `η` was not re-derived.**

## 10. What goes to Sanaa's desk

**Nothing here is taken, and nothing is filed.** All prices are core-minutes at \$0.0513/core-h,
reported-by-owner.

| item | price | what it decides |
|---|---|---|
| **The reading of the N=29 gate** — Reading 1 (`NOT MET`, charter text) vs Reading 2 (`GATE REACHED`, subset-complete), §8 | **0 compute** | **Whether N=29 runs at all.** Reserved to Sanaa; both readings are registered and neither is chosen by this lane. |
| **`useMeanStates: True` + `fieldAverage` in `controlDict`** — one primal + one re-differenced pair (`66f42398` §3.4) | **~5 core-min, \$0.004** | **Whether `η` itself can be reduced — the ONLY lever that reaches `twist` idx6**, since clearance is `\|J\|·2s/η` and no feasible `s` rescues it. **This is now the single item standing between A6 N=16 and a nine-of-nine table**, and it is the difference between the two gate readings. |
| `primalFuncStdTol {stdTol, slopeTol}` as the convergence criterion (`66f42398` §3.4) | **~2 core-min, \$0.002** | Whether A6's primal can be declared converged **honestly**, retiring the inherited `primalMinResTolDiff 1e4` widening rather than carrying it forever. |
| **`PBiCGStab`-pressure ADF arm** (`66f42398` §11.1 sweep 1) | **~5 core-min, \$0.004** | The **defect class** of the ADF non-reproduction (N-D16): conditioning/diagnosability if the NaN disappears, AD correctness if it persists. |
| ADF arms on A1 and A4 (`66f42398` §11.1 sweep 2) | **~10 core-min, \$0.009** | Whether forward-AD is unusable across this lab's Ladder A or only on the transonic solver. |
| **A third draw of the `1e-8` trivial baseline**, to turn §4.3's two-sample irreproducibility into a characterisation | **~3.4 core-min, \$0.003** | Whether the wrong-step probe's sign is genuinely a coin flip or the two draws were coincidence. **Low value; listed for completeness and NOT recommended** — the finding is already carried by the two. |
| **`shape` group** (~10² components) | **UNPRICED** | Never graded by any item in this family. A price would cross from a 9-component FD arm to a ~10²-component one and **`COMPUTE_BUDGET_CHARTER.md:375-395` forbids inventing it** without that case's own record. |
| **The step-selection rule on a rung whose adjoint is wrong** (§7 limitation 8) | **UNPRICED** | Whether §3.1's rule survives when its `\|J_adj\|` proxy is itself the error. A1 or A5 would be the case; no record prices it. |

**Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone**
(`DAFOAM_CHARTER.md` §10; `FAMILY_SUPERVISION_GUIDELINES.md` §3.6; CLAUDE.md rule 7).

**This is a PATCHED-image row and it says so. It does not replace, merge with, or re-grade the
shipped-toolchain row at `../rung_n16_np1/RESULTS.md` §6.2.**
