# Curriculum item D1 — A1 NACA0012, lift-constrained drag minimisation: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-24T16:22:08Z by Lane Z (Opus), DAFoam team — every stamp in this file is `date -u`
output read in the same shell invocation that wrote it (`PREREGISTRATION.md` §15 A1.2).**

**This file does not revise the pre-registration.** The governing document is
`PREREGISTRATION.md` in this directory, frozen before any container started, as amended by its own
**Amendment 1** (§15), **Amendment 2** (§16 AMENDMENT) and **Addendum §16** (after first compute,
landed by the dafoam supervisor at `668ce997`). No gate, threshold, cap, prediction band or label
was altered by this lane, and **no script, driver or case file was edited by this lane.**

**Executed by two lanes.** Lane Y staged the run root, ran arm E (twice — see §2) and was killed by
the session limit at arm O's launch gate. Lane Z (this lane) ran arms O and C under the same frozen
file and the same instruments, on an execution-only continuation.

---

## 1. Verdicts — two toolchain rows, never merged (R11)

| row | image | what it graded | verdict |
|---|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1` (`2927768a16ac`) | the constrained optimisation (arm O) **and** its endpoint gradient re-verified against finite differences at the design point the optimiser actually reached | **PASS** |
| **SHIPPED** | `dafoam/opt-packages:latest` (`9d45679d55fd`) | the shipped endpoint gradient at arm O's own final design point (arm C) | **BLOCKED** |

**Item as a whole: `PENDING`.** Two of the three registered arms are complete and graded; arm C is
`BLOCKED` on a defect in the frozen driver `d1_fd_endpoint.py` that this lane is not permitted to
repair (§8). The §3.3 deliverable — *a clean toolchain comparison at a deformed design point* — is
therefore **NOT DELIVERED** and is `BLOCKED`, not failed.

**The graded claim, stated once, in full.** On the patched toolchain, IPOPT terminated on its own
statement `EXIT: Optimal Solution Found.` after **11 major iterations** with `Overall NLP error
4.0871293161759560e-07` against `tol 1e-5`; the accepted design satisfies `CL = 0.5` to
**`1.879064e-07`** and every one of the 24 geometric constraint rows lies inside its registered
bound; `CD` fell from **`0.020943920630946831`** (post-feasibility) to **`0.017527899854535338`**,
a reduction of **16.310321%**; and the analytic gradient at that design point agrees with a
central-difference reference on all four named components at **≤ 0.2553%**, with **zero sign
flips**, at steps chosen from `|J_adj|` and `η` alone before any FD value existed.

---

## 2. Arm ledger — every container this item ever started

All rows read from `/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/ledger.txt`,
whose every stamp is `date -u` at write. **Four containers, not three: arm E ran twice.**

| # | arm | image | task | UTC launch | rc | wall s | core-min | `.State.ExitCode` / `.State.OOMKilled` | peak RSS GiB | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | armE run 1 | patched | `d1_eta` | 2026-08-23T21:25:21Z | 0 | 18 | **0.300** | `0` / `false` | 0.8076 | **VOID** under §4.2(c) — driver edited after it launched (Addendum §16 item 3). **Named waste.** |
| 2 | armE run 2 | patched | `d1_eta` | 2026-08-23T21:26:57Z | 0 | 27 | **0.450** | `0` / `false` | 0.6291 | **graded** — η measured, 24 constraint rows dumped |
| 3 | armO | patched | `d1_opt` | 2026-08-24T16:05:53Z | 0 | 361 | **6.017** | `0` / `false` | **1.6964** | **graded** — `EXIT: Optimal Solution Found.`, endpoint adjoint + FD + trivial baseline |
| 4 | armC | shipped | `d1_endpoint_shipped` | 2026-08-24T16:14:06Z | **1** | 14 | **0.233** | `1` / `false` | NOT MEASURED | **BLOCKED** — `KeyError: 'CD_final'` in the frozen G5 comparator, before any solve. **Named waste.** |

**Total gross 7.000 core-min. Named waste 0.533 core-min** (rows 1 and 4), reported separately and
**never netted off** (`COMPUTE_BUDGET_CHARTER.md` §6).

Artifacts, all in the run root, all cited by path and none from a scratchpad (`CLAUDE.md` rule 13):
`ledger.txt`, `preflight_history.txt`, `eta.json`, `eta.txt`, `selftest_cubic.txt`,
`selftest_plant.txt`, `d1_script.diff`, the four `<arm>_${STAMP}.log` files with their
`.ok.${STAMP}` sentinels, `armO/opt_IPOPT.txt`, and
`armO/endpoint_20260824T160552Z_1399954.json` (md5 `e63f57710cee6e2170f2e9cef39f8b2a`,
verified byte-unchanged after arm C read it).

**Instrument identity, asserted by this lane before any launch and re-asserted here:**
`d1_fd_endpoint.py` md5 **`7e454d2f1830a40086465d9b5c57a941`** (the repaired driver named as the
instrument by Addendum §16); `d1_opt_runScript.py` md5 **`4c9811d16f344bc23136981cd6092d8f`**
(the value frozen in `ledger.txt` before the first launch). Neither file was edited by this lane.
**`d1_script.diff` carries exactly 3 hunks** (`@@ -42,6 +42,7 @@`, `@@ -206,7 +207,7 @@`,
`@@ -247,6 +248,224 @@`), matching §9.3's three registered changes and no others — the assertion
§9.3 requires of this file.

---

## 3. Arm E — the baseline, η, and the constraint normalisation (run 2; run 1 VOID)

Both arm E runs are reported, as Addendum §16 requires.

| quantity | run 1 (VOID) | run 2 (graded) | registered reference | reading |
|---|---|---|---|---|
| cold baseline `CD` | `0.020910510006792161` | **`0.020910510006792161`** | `0.02091051000679216` (corrected F1, np=1) | **all printed digits match — F1 did not fire** |
| cold baseline `CL` | — | **`0.49876526415423195`** | `0.4987652667308054` (np=2 record) | np=1/np=2 difference, disclosed |
| **η** (last 5 samples, `printInterval 10`, t = 400…435) | `1.957350e-08` | **`1.957349804806996e-08`** | P7 band `[2e-10, 5e-8]` | **HIT**; run 1 and run 2 agree to every printed digit |
| `η_A6window` (last 200 iters, 20 samples) | — | **`7.824304910440671e-06`** | reported only, **sizes no step** | **400× larger** — Amendment 2's §A2.2 reason for pinning the window is confirmed by measurement |
| peak RSS | 0.8076 GiB | 0.6291 GiB | — | both far under the 2.0 GiB ceiling |

**The np=2 ↔ np=1 gap Amendment 2 predicted, measured:**
`0.020910510006792161 − 0.0209105098587985 = **1.479937e-10**` — the exact figure §A2.1 stated in
advance, at the 11th significant digit. **Amendment 2 saved this run:** F1 as originally written
would have fired on a benign decomposition difference and stopped a healthy arm.

**The constraint normalisation, asserted not assumed (§2.1, falsifier F8).** All **24** rows at the
undeformed baseline read `1.0`:

| family | rows | max deviation from 1.0 | F8 threshold |
|---|---|---|---|
| `geometry.thickcon` | 20 | **2.243e-14** | ±1e-9 |
| `geometry.volcon` | 1 | **1.716e-13** | ±1e-9 |
| `geometry.rcon` | 2 | **6.706e-14** | ±1e-9 |

**F8 did not fire.** §2.1's `t_min = 0.5 × baseline thickness` and `V_min = 1.0 × baseline volume`
readings stand as measured statements, not assumptions.

---

## 4. Arm O — the optimisation

### 4.1 The feasibility step (§2.4)

| quantity | DERIVED in §2.4, zero compute | MEASURED | P3b band | reading |
|---|---|---|---|---|
| `CD_feasible` | `0.02095273` (point `0.020953`) | **`0.020943920630946831`** | `[0.02090, 0.02100]` | **HIT** |
| `AoA_feasible` | `5.148362` deg (point `5.1484`) | **`5.153023459675001`** deg | `[5.13, 5.17]` | **HIT** |
| `CL` after the step | `0.500000` | **`0.49999943897261456`** | — | 5.61e-07 from target |
| `ΔAoA` | `9.176e-03` deg | **`1.383723e-02`** deg | — | 1.51× the derived value |
| `ΔCD` | `4.222e-05` | **`3.341062e-05`** | — | 0.79× the derived value |

The two-step derivation of §2.4 — `ΔAoA` from `|dCL/dAoA|`, `ΔCD` from `|dCD/dAoA|`, both taken as
2-vector norms on the inference that the `U0` component is negligible — landed both endpoints
inside their bands while missing each intermediate by ~25–50% in **opposite** directions. **The
inference is not vindicated by the band HIT and is not upgraded here**: two errors of opposite sign
cancelled in `CD_feasible`, which is the same shape as the C-3 and B3 calibration findings.

### 4.2 Termination — gate G2

**`EXIT: Optimal Solution Found.`** — printed in `armO/opt_IPOPT.txt`.

| IPOPT statement | value | registered threshold |
|---|---|---|
| Number of Iterations | **11** | cap `max_iter 40` — **not reached** |
| Objective (scaled = unscaled) | `1.7527900345066981e-02` | — |
| Dual infeasibility | `4.0871293161759560e-07` | — |
| **Constraint violation** | **`1.9421312102974042e-07`** | G1: ≤ `1.0e-5` |
| **Overall NLP error** | **`4.0871293161759560e-07`** | G2: `< tol 1e-5` |
| objective function / gradient evaluations | 12 / 12 | — |
| Total CPU secs in NLP function evaluations | 261.615 | — |

**G2 outcome: `gradeable`** — the first row of G2's table, not the cap/timeout/ceiling row. **No
cap, no timeout and no ceiling bound this arm**: 11 majors of a 40 cap, 361 s of a 2,700 s
`timeout`, 6.017 core-min of a 120.0 core-min ceiling. **`GATE REACHED` is therefore not the
verdict and the 2.0% intermediate threshold was never reached for**; the arm is graded PASS/FAIL on
G1 and G3, and both hold.

### 4.3 The optimiser's own column — falsifier F4

| major | objective | `inf_pr` | `\|\|d\|\|` | `alpha_pr` | `ls` |
|---|---|---|---|---|---|
| 0 | `2.0943920e-02` | 5.60e-07 | 0.00e+00 | 0.00e+00 | 0 |
| 1 | `2.0895996e-02` | 3.99e-06 | 1.17e-02 | 1.00e+00 | 1 |
| 2 | `1.9594869e-02` | 2.60e-03 | 1.43e-01 | 1.00e+00 | 1 |
| 3 | `1.8521867e-02` | 2.25e-03 | 2.01e-01 | 1.00e+00 | 1 |
| 4 | `1.7895031e-02` | 1.44e-03 | 1.58e-01 | 1.00e+00 | 1 |
| 5 | `1.7676933e-02` | 8.60e-04 | 1.65e-01 | 1.00e+00 | 1 |
| 6 | `1.7568100e-02` | 1.73e-03 | 2.70e-01 | 1.00e+00 | 1 |
| 7 | `1.7539826e-02` | 1.09e-04 | 7.41e-02 | 1.00e+00 | 1 |
| 8 | `1.7529358e-02` | 1.36e-05 | 4.00e-02 | 1.00e+00 | 1 |
| 9 | `1.7528086e-02` | 2.38e-06 | 3.41e-02 | 1.00e+00 | 1 |
| 10 | `1.7527903e-02` | 3.65e-06 | 2.52e-02 | 1.00e+00 | 1 |
| 11 | **`1.7527900e-02`** | **1.94e-07** | 6.09e-03 | 1.00e+00 | 1 |

**The objective column is strictly monotone decreasing on all 11 accepted steps. F4 did not fire.**
Every step took a full primal step (`alpha_pr = 1.00e+00`) with **`ls = 1`** — *no line search
backtracked on any major of this run.* That fact is not decoration; it is the measured cause of
P5's cost miss (§9).

**Reported rather than folded away:** the **constraint-violation** column `inf_pr` is *not*
monotone — it rises at majors 2, 6 and 10 (`8.60e-04 → 1.73e-03` at major 6 is the largest
excursion) before collapsing to `1.94e-07`. That is ordinary interior-point behaviour under an
adaptive barrier and it is **not** what F4 registers; F4 is about the objective column, and the
objective column is clean. The `inf_pr` excursions are recorded here so that no future reader has
to rediscover them from the log.

### 4.4 The accepted design, and gate G1

| quantity | value |
|---|---|
| `CD` at the accepted design | **`0.017527899854535338`** |
| `CL` at the accepted design | **`0.4999998120936336`** |
| **`\|CL − 0.500000\|`** | **`1.879064e-07`** |
| `AoA` (`patchV[1]`) | **`1.128636497545056`** deg (from `5.153023459675001`) |
| `patchV[0]` (`U0`) | `10.0` — pinned and inert, as registered |
| `shape` (8 modes) | `+2.8765045846e-02, +4.7201042921e-02, +1.6871666038e-02, +3.6676713888e-02, +4.7228926536e-02, +2.2959816884e-02, +8.2626231129e-03, +3.6138219757e-02` |

**Reduction, against both references:**

| against | value | reduction |
|---|---|---|
| `CD_feasible` (**the registered reference**, §2.4) | `0.020943920630946831` | **16.310321%** |
| cold np=1 baseline (arm E run 2) | `0.020910510006792161` | **16.176603%** |

**Gate G1 — every registered row checked, none assumed:**

| G1 condition | registered bound | measured | reading |
|---|---|---|---|
| `\|CL − 0.5\|` | ≤ `1.0e-5` | **`1.879064e-07`** | **inside, by 53×** |
| IPOPT `Constraint violation....:` | ≤ `1.0e-5` | **`1.9421312102974042e-07`** | **inside, by 51×** |
| `thickcon`, 20 rows | ∈ `[0.5 − 1e-6, 3.0 + 1e-6]` | min **`0.500000125773`**, max **`1.101702451432`** | **all 20 inside** |
| `volcon`, 1 row | ≥ `1.0 − 1e-6` | **`1.000000017320`** | **inside** |
| `rcon`, 2 rows | ≥ `0.8 − 1e-6` | **`0.800000261506`** (both) | **both inside** |

**G1: `PASS`.** The design is accepted.

**What the numbers say about the optimum, stated because it is the mechanism behind §7's P3 MISS.**
Three of the four constraint families are **ACTIVE**: `volcon` sits at `1.000000017` against its
`1.0` floor, both `rcon` rows at `0.800000262` against `0.8`, and the binding `thickcon` row at
`0.500000126` against `0.5`. **The optimum is in a corner of the feasible set.** The design it
reached is a **cambered** section — all eight `shape` modes moved positive — flying at **1.13°**
instead of **5.15°**. That is the classical camber-for-incidence trade: the same `CL = 0.5` bought
by section shape rather than by angle of attack, at markedly lower drag. **The registered
constraint set does not forbid it**, and that is exactly why P3's band was wrong (§7).

---

## 5. Gate G3 — the endpoint gradient, per component, in full

**Never folded into an aggregate** (`DAFOAM_CHARTER.md` §2). All values from arm O's in-process
endpoint block, run immediately after `run_driver()` returned, **with the design vector still in
memory — no reload, no restart, no directory reuse** (§4 arm O row).

### 5.1 The step plan — chosen from `|J_adj|` and η alone, before any FD value existed

`η = 1.957349804806996e-08` (arm E run 2). `C(s) = |J_adj|·2s/η`. `s_lo` = smallest rung with
`C ≥ 5` and `s ≥` floor; `s_hi` = smallest rung with `s_hi ≥ 3·s_lo`.

| component | `J_adj` (endpoint) | `s_lo` | `C(s_lo)` | **`s_hi`** (graded) | `C(s_hi)` | source |
|---|---|---|---|---|---|---|
| `shape[6]` | `-2.77015704e-02` | `1e-4` | **283.1** | **`3e-4`** | **849.2** | rule |
| `shape[1]` | `+1.91129336e-02` | `1e-4` | **195.3** | **`3e-4`** | **585.9** | rule |
| `shape[5]` | `+3.88660685e-02` | `1e-4` | **397.1** | **`3e-4`** | **1191.4** | rule |
| `patchV[1]` | `+1.12325011e-03` | `1e-3` | **114.8** | **`3e-3`** | **344.3** | rule |

**§6 G3 item 3's advance prediction was exact.** It registered, before any compute, *"Predicted
registered pair for every `shape` component: `{1e-4, 3e-4}`, graded at `3e-4`. Predicted for
`patchV[1]`: `{1e-3, 3e-3}`, graded at `3e-3`."* **Every component landed on precisely those
pairs** — and it did so from **endpoint** `|J_adj|` values the pre-registration could not have
known. Two of them moved a long way from the baseline magnitudes Amendment 2 computed the
clearances from: `shape[6]` grew from `|J| = 1.07e-03` to `2.77e-02` (26×, so `C(1e-4)` rose from
**10.9** to **283.1**) and `patchV[1]` fell (so `C(1e-3)` dropped from **470** to **114.8**). **The
floor bound in every case, exactly as §6 G3 item 3 said it would**, and the clearance test never
bound. The registered risk — *"if the measured plateau η comes back far larger than 4.3e-08,
`shape[6]` no longer clears `C ≥ 5`"* — did not materialise: η came in at `1.957e-08`.

**L-266's repair is visible here and is correct.** `s_hi = 3e-4` is the rung the registered
arithmetic selects for `s_lo = 1e-4` and the rung the pre-repair floating-point comparison would
have skipped. The repaired driver selected it on all three `shape` components.

### 5.2 The graded table — PATCHED, at the endpoint

| component | `J_adj` | FD @ `s_lo` | rel. err | FD @ **`s_hi`** (graded) | **rel. err** | sign flip | plateau (2-step) | `C` measured @ `s_hi` | graded? |
|---|---|---|---|---|---|---|---|---|---|
| `shape[6]` | `-2.77015704e-02` | `-2.76751976e-02` | 0.0953% | **`-2.76870222e-02`** | **0.0525%** | **no** | **0.0427%** | 848.7 | **YES** |
| `shape[1]` | `+1.91129336e-02` | `+1.91851082e-02` | 0.3762% | **`+1.91442968e-02`** | **0.1638%** | **no** | **0.2132%** | 586.8 | **YES** |
| `shape[5]` | `+3.88660685e-02` | `+3.89825724e-02` | 0.2989% | **`+3.89138868e-02`** | **0.1229%** | **no** | **0.1765%** | 1192.9 | **YES** |
| `patchV[1]` | `+1.12325011e-03` | `+1.13155890e-03` | 0.7343% | **`+1.12612462e-03`** | **0.2553%** | **no** | **0.4826%** | 345.2 | **YES** |

**4 of 4 components GRADED. Zero FLAGGED. Zero excluded. Zero sign flips.** Every component
cleared both grading tests: `C ≥ 5` at the graded step (worst **345.2**, i.e. 69× the requirement)
and two-step plateau agreement within 10% (worst **0.4826%**, i.e. 21× inside).

**Aggregate, named as the statistic it is and printed second, never instead of the table:** the
**vector-relative error `‖J_an − J_fd‖/‖J_fd‖` over the four graded components** is
**`1.147919e-03` = 0.11479%**. It is not a per-component average and is never compared to one.

**G3 verdict: `PASS`** — every graded component ≤ 5% with zero sign flips.

### 5.3 What this measured that the baseline record could not

`DAFOAM_CHARTER.md` §9's warning — *a gradient verified at iteration 0 is not verified at iteration
47* — is the reason G3 exists. The comparison, both columns measured on the same patched image:

| component | patched **baseline** rel. err (`reverify_patched_idwarp_np1/RESULTS.md` §4.2, step 1e-3) | patched **endpoint** rel. err (here, step 3e-4) |
|---|---|---|
| `shape[6]` | **1.1888%** | **0.0525%** |
| `shape[1]` | 0.0738% | 0.1638% |
| `shape[5]` | 0.0104% | 0.1229% |
| `patchV[1]` | (not separately reported at baseline) | 0.2553% |

**The endpoint gradient did not degrade; the worst component improved by 23×.** `shape[6]` — the
LE combo mode, the defect's own component, `640.3696%` and sign-flipped on the shipped image at
baseline — reads **0.0525%** with the right sign at the optimum. A1's own §7.3 concern that
*"regime 2 would govern any optimisation run from iteration 1"* is not borne out on this case at
this design point. **The steps differ between the two columns (1e-3 vs 3e-4) and both sit inside
A1's measured 1e-4…3e-2 plateau; the comparison is therefore read as a like-for-like plateau
reading, and it is not claimed to be tighter than that.**

**The registered limitation stands, unweakened.** η was measured at the **baseline** design (arm
E), not at the endpoint. `A4/shipped_optimisation_np1/RESULTS.md` §3.2 measured the FD reference at
a deformed design point to be **path-dependent** (two runs, same optimum to 1.8e-07, FD references
0.183% apart). The registered mitigation — the **two-step plateau test at the endpoint** — was
executed and every component passed it by more than an order of magnitude. **It is a mitigation,
not a measurement of the endpoint's own noise floor, and this record does not upgrade it into one.**

---

## 6. Gates G4 – G10

### G4 — trivial baseline (`DAFOAM_CHARTER.md` §4)

The same probe, same stack, same component, at a deliberately wrong step:

| component | step | `J_adj` | FD | **rel. err** | sign flip |
|---|---|---|---|---|---|
| `shape[6]` | **`1e-8`** | `-2.77015704e-02` | **`+2.19846668e-01`** | **112.6004%** | **YES** |

**Registered prediction P8: > 50%. Measured 112.6004%, with a sign flip. HIT.**
**The instrument can fail, and does, on a step A1's own roundoff branch is known to destroy. G3's
verdict is NOT withdrawn** — falsifier F6 (*trivial baseline ≤ 5%*) did not fire, and it was never
close: the wrong step is off by **2,144×** relative to the graded step's 0.0525%.

### G5 — planted-zero control (`CLAUDE.md` rule 3): **NOT EXERCISED**

The frozen comparator's two zero-compute controls **passed before any container started** and are
on disk in the run root:

* `selftest_cubic.txt` — the difference kernel on `f(x)=x³` at `x=2`, `s=1e-4`:
  `12.00000001000845` against `12.0`, rel. err `8.34e-10`, **pass**, 2 evaluations.
* `selftest_plant.txt` — the reader planted with `PLANT = 1.234e-03` **on a synthetic fixture**:
  read-back delta `0.001233999999999999`, shape residual `0.0`, **pass**; and its negative control,
  a deliberately blind reader, **refused with exit 2** as registered.

**But the control was never run against the file the producer actually writes.** Arm C invoked
`planted_zero_control` on arm O's real `endpoint_20260824T160552Z_1399954.json` and it raised
`KeyError: 'CD_final'` — the comparator's key does not exist in the producer's schema (§8).

**Consequence, stated plainly and not softened.** **G5 is `NOT EXERCISED` on this item's only
cross-arm file read.** It is **not** a G5 refusal (a refusal prints `D1_G5_PLANTED_ZERO REFUSE`
and exits 2; this was a crash before any plant was made), and it is **not** a G5 pass.
Correspondingly, **falsifier F7 did not fire and was not tested.** What protects this record is
that **no figure in §4 or §5 is read from a file**: every arm O number is computed and printed
in-process, in the same process that held the design vector, and this document quotes those printed
values. **No comparator number computed from a file is reported anywhere in this record**, so no
graded figure depends on the unexercised control.

### G6 — launch gate, re-run immediately before each launch

Every reading is a row in `preflight_history.txt` with a `date -u` stamp read in the same
invocation as the write. **The gate refused a launch on this item for the first time, and the arm
waited rather than departing on this lane's authority.**

| UTC | arm | `nproc` | `load1` | `free_cores` | `MemAvailable` GiB | gate | action |
|---|---|---|---|---|---|---|---|
| 2026-08-23T21:25:16Z | armE | 16 | 6.08 | 9.92 | 18.31 | **OPEN** | launched (run 1) |
| 2026-08-23T21:26:57Z | armE-rerun | 16 | 6.12 | 9.88 | 14.81 | **OPEN** | launched (run 2) |
| 2026-08-23T21:28:20Z | armO | 16 | 5.77 | 10.23 | 27.31 | **OPEN** | **Lane Y killed before launching** |
| 2026-08-24T16:05:53Z | armO | 16 | 4.24 | 11.76 | 27.33 | **OPEN** | launched |
| 2026-08-24T16:12:53Z | armC | 16 | **14.02** | **1.98** | 27.45 | **NOT_OPEN** | **NO LAUNCH** |
| 2026-08-24T16:13:06Z | armC | 16 | **13.40** | **2.60** | 27.79 | **NOT_OPEN** | **NO LAUNCH** |
| 2026-08-24T16:14:06Z | armC | 16 | 7.04 | 8.96 | 27.41 | **OPEN** | launched |

**G6: honoured on every launch.** The two `NOT_OPEN` readings are the box's own load average still
decaying from arm O's own 361 s of solver; the arm waited **73 s** and re-ran the gate, exactly as
§6 G6 registers. **No departure was taken and none was requested.** The memory limb was never near
binding (worst reading 14.81 GiB against a 12 GiB floor); the **core** limb is the one that bound.

### G7 — image identity

| arm | printed `IDWARP_SO_MD5` (from inside the loading process) | registered | `nProcs` | uid |
|---|---|---|---|---|
| armE run 1 | `85f59e87253e0a71a813f64ca6e4c425` | patched ✓ | `1` | `0` |
| armE run 2 | `85f59e87253e0a71a813f64ca6e4c425` | patched ✓ | `1` | `0` |
| armO | `85f59e87253e0a71a813f64ca6e4c425` | patched ✓ | `1` | `0` |
| armC | `f0fcb488e0e98156575cd19548e91663` | **shipped ✓** | `1` | `0` |

**G7: PASS on all four. Falsifier F2 did not fire, arm C included** — arm C loaded the correct
shipped library and its failure has nothing to do with image identity. Image digests re-read on
this box in the same session: patched `sha256:2927768a16acdea…f6d35`, shipped
`sha256:9d45679d55fd47…f07fc`, both matching §3 exactly.

### G8 — cold start, verified before every launch

`d1_run_arm.sh` asserts, **before** the container starts, that the freshly staged arm directory has
no `0.0001`, no other numeric time directory, no `processor*`, no `reports/`, and a populated `0/`
restored from `0.orig/`. It printed `G8 OK` for arm O and for arm C. Each arm is staged as a
pristine `cp -a` of `base/`, whose three registered md5s were re-asserted by this lane:
`points.gz` `38a486d29a540ecd1b06e006e66475e7`, `wingFFD.xyz` `6ddf378b028d03d8a18270488bee1759`,
`runScript.py` `0557da51f6f179f6de865144343c499f`. **`base/` is copied FROM and never run IN.**
The check that this held is F1's bit-identical baseline `CD`, and it held (§3).

### G9 — memory envelope (`DAFOAM_CHARTER.md` §7)

| reading | value |
|---|---|
| predicted peak (P9 point) | 1.2 GiB |
| **registered ceiling (P9 band)** | **2.0 GiB** |
| kernel cap | `--memory=6g --memory-swap=6g` (equal — **no swap escape**), `--oom-score-adj=500` |
| **measured peak, whole item** | **1.6964 GiB** (arm O, `getrusage(RUSAGE_SELF).ru_maxrss` taken by the process itself) |
| arm E run 1 / run 2 | 0.8076 / 0.6291 GiB |
| arm C | **NOT MEASURED** — crashed before the marker printed |
| `.State.OOMKilled` | **`false` on all four containers** |
| unused headroom at the cap | **4.30 GiB** (6.0 − 1.696) |

**G9: PASS.** No container was OOM-killed and no `timeout` fired.
**P9 is graded, not `NOT EVALUATED`**, because §8.1's fallback applied: `/usr/bin/time` is **absent
from both images** (`D1_USRBIN_TIME: absent`), but the figure that replaces it is a `getrusage`
reading **taken by the process itself**, which is precisely what §8.1 permits and is not a polling
process. **No watcher of any kind was started by this lane** (§8.1); the record-only host
`MemAvailable` floor remains record-only in flight and this record claims nothing else for it.
**L-15 reading, stated because the opposite error is the easy one: arm C's failure is NOT a memory
finding.** It died with **4.30 GiB of unused headroom** under its cap, on a Python `KeyError`.

### G10 — cost ceiling

**7.000 core-min gross against the 120.0 core-min HARD ceiling — 5.83% of it.** No overrun; the
ceiling was never approached and no run was stopped by it. `$0.005985 DERIVED` against
`$0.1026 DERIVED`. Full comparison in §9.

---

## 7. Predictions — every one scored, MISSes reported as MISSes

| id | prediction | HIT band | measured | **score** |
|---|---|---|---|---|
| **P1** | termination class | `EXIT: Optimal Solution Found.` with `Overall NLP error < 1e-5` | **`EXIT: Optimal Solution Found.`**, Overall NLP error **`4.087129e-07`** | **HIT** |
| **P2** | major iterations, point **18** | **[8, 30]** | **11** | **HIT** (point over by 1.64×) |
| **P3** | `CD` reduction vs `CD_feasible`, point **5.0%** | **[2.0%, 12.0%]** | **16.310321%** | **MISS — high** |
| **P3b** | `CD_feasible` / `AoA_feasible` | `[0.02090, 0.02100]` / `[5.13, 5.17]` | **`0.020943920630946831`** / **`5.153023459675001`** | **HIT** (both) |
| **P4** | final `\|CL − CL*\|`, point ≈**1e-8** | **≤ 1.0e-6** | **`1.879064e-07`** | **HIT** (point under by 19×) |
| **P5** | per-major cost, point **1.0 core-min/major** | **[0.4, 3.5]** | **0.42127 core-min/major** (`D1_DRIVER_WALL_S 278.04` s ÷ 11) | **HIT — at the band floor** |
| **P6** | endpoint FD agreement, patched, point **≤ 1.5%** per component | **every graded component ≤ 5.0% AND zero sign flips** | worst graded **0.2553%**, **zero flips**, 4 of 4 graded | **HIT** (point and band) |
| **P7** | η on this case, point **2e-9** | **[2e-10, 5e-8]** | **`1.957349804806996e-08`** | **HIT on band; the point estimate MISSES high by 9.8×** |
| **P8** | trivial baseline at `1e-8` | **> 50%** | **112.6004%**, sign-flipped | **HIT** |
| **P9** | peak memory, point **1.2 GiB** | **≤ 2.0 GiB** | **1.6964 GiB** | **HIT on band; point under-predicted by 1.41×** |
| **P10** | total cost, point **23.0 core-min** | **≤ 46.0 core-min** | **7.000 core-min gross** | **HIT on band — but see the caveat below** |

**Score: 10 HIT, 1 MISS on the bands.** Two point estimates are separately reported as misses
inside HIT bands (P7, P9) and one more as a large over-estimate (P2), because a band HIT is not a
good point estimate and this record does not let one stand in for the other.

**P3 — the MISS, with its reason named and not explained away.** The reduction came in at
**16.310321%**, **1.36× above the band's ceiling** and **3.26× the point estimate**. The band's
registered basis was: *"The constraint set here is tight — `volcon ≥ 1.0` forbids net volume loss,
`thickcon ≥ 0.5`, `rcon ≥ 0.8` — so a large reduction is not available at fixed `CL`."*
**That reasoning was wrong, and measurably so.** The constraints did bind — three of the four
families are **active at the optimum** (§4.4) — and the optimiser still found 16.3%, because the
drag reduction it bought was **not** bought by any of the things those constraints forbid. It was
bought by **camber traded against incidence**: all eight `shape` modes moved positive and `AoA`
fell from **5.15°** to **1.13°** at fixed `CL = 0.5`. A volume floor, a thickness floor and an LE
radius floor do not forbid re-cambering a section at constant volume. **The band was set by
reasoning about which constraints were tight rather than about which directions in the 9-DV space
were still free, and that is the calibration content of this MISS.** The historical A2 anchor the
band quoted as an unreachable upper limit — **−28.275%** at matched `CL ≈ 0.5`, itself
`NOT A RESULT` — now looks less like an outlier and more like the same mechanism on a wing.

**P10 — the caveat, because a HIT on an unfinished item is not a HIT on the item.** 7.000 core-min
is inside the ≤ 46.0 band and far inside the 120.0 ceiling, **but arm C did not deliver its
registered work** (§8). The measured total is therefore a **lower bound on the item's eventual
cost**, not a completed-item figure, and §9's calibration row says so in its own words. Arm C's
registered price was 2.0 core-min; even spent in full, the item would land at ~9.0 core-min and the
band would still hold — **but that is an estimate, and this record does not book it as a
measurement.**

---

## 8. Arm C — `BLOCKED`, and the defect, triaged not waved through

**A crash is a finding until triage says otherwise** (`SUPERVISION_CHARTER.md` §3). This is the
triage, and it is not a red with an innocent explanation.

**What happened.** Arm C launched at `2026-08-24T16:14:06Z` on the shipped image on an OPEN gate,
loaded the correct shipped `libidwarp.so` (`f0fcb488e0e98156575cd19548e91663`), read the mesh
(`Total Volume Nodes : 8316`, `nProcs : 1`), built the whole OpenMDAO/DAFoam problem, and then died
at **14 s** — **before injecting a single design variable and before any primal solve** — at:

```
File "/mnt/armC/d1_opt_runScript.py", line 454, in <module>
    _d1.planted_zero_control(src_json)      # gate G5, refuses on failure
File "/mnt/armC/d1_fd_endpoint.py", line 110, in planted_zero_control
    pert["CD_final"] = base["CD_final"] + plant
KeyError: 'CD_final'
```

**The defect, isolated to one key.** The producer and the consumer of the endpoint hand-off
disagree about a field name, and the two halves are in two different frozen files:

| role | file, line | key |
|---|---|---|
| **producer** — writes `endpoint_${STAMP}.json` | `d1_opt_runScript.py:417` (`_fd_suite` return) | **`"CD"`** |
| **consumer** — the G5 planted-zero control | `d1_fd_endpoint.py:110, 116` | **`"CD_final"`** |

The producer's actual top-level keys, read from the file on disk:
`['CD', 'CL', 'J_adj', 'cons', 'eta', 'fd', 'feasible_note', 'maxrss_GiB', 'patchV', 'plan',
'shape', 'tag', 'trivial']` — **`CD_final` is absent; `CD` is present.**

**This is exactly one key.** Every other field arm C needs is present and correctly named:
`ep["shape"]`, `ep["patchV"]`, `ep["plan"]`, `ep["eta"]` all resolve. The DV injection, the FD
suite and the step reuse would all have worked. **The blocking surface is the G5 control alone.**

**Why the zero-compute self-test did not catch it — and this is the transferable finding.**
`selftest_plant.txt` records `D1_G5_PLANTED_ZERO OK` **and** a negative control that correctly
refused with exit 2. Both are genuine. But the fixture the self-test planted into was **synthetic**
— a hand-built dict carrying `CD_final` — **not a file the producer wrote.** The control therefore
verified that the reader can see a plant *in a schema the pipeline never produces*. A planted-zero
control that plants into its own fixture proves the arithmetic and not the coupling; the coupling
is the half that broke. **This sits directly beside `CLAUDE.md` rule 3's own logic: a zero from a
reader not shown able to see a non-zero is not evidence — and a plant seen in a file no producer
writes is not that demonstration.**

**What this lane did, and did not do.**

* **Did not edit `d1_fd_endpoint.py`, `d1_opt_runScript.py`, `d1_run_arm.sh` or any case file.**
  §4.2(c) is registered — *"it is not edited after the first launch — an edit voids every arm that
  ran before it"* — and this item has already spent that exception once, at the cost of a voided
  arm and L-266. **A second post-first-compute edit on the same item, by a lane, on its own
  reading, is not this lane's call.** `VERIFICATION_CHARTER.md` §2d.1's four conditions are not
  assessed here; that assessment is the supervisor's.
* **Did not retry, re-launch, or route around the control** — not by exporting a different file, not
  by pre-writing a `CD_final` key into arm O's endpoint JSON, not by invoking the shipped task with
  the control skipped. Each of those is a repair wearing an operational costume.
* **Did not touch arm O's endpoint JSON.** Verified byte-unchanged after arm C read it
  (md5 `e63f57710cee6e2170f2e9cef39f8b2a`); no `.plant` file was written, because the crash preceded
  the write. Arm O's evidence is intact.
* **Removed the container after reading the kernel's verdict** (§8.2): `ExitCode 1`,
  `OOMKilled false`. No `d1_*` container remains on the box.

**Arm C verdict: `BLOCKED`.** Not `GATE FAIL` — no gate was reached and no shipped gradient exists
to fail one. Not `NOT A RESULT` about the shipped toolchain — nothing about the shipped toolchain
was measured. **The shipped row of §1 is `BLOCKED`, and the §3.3 deliverable it was bought for
remains open exactly where `A4/shipped_optimisation_np1/RESULTS.md` §8 limit 3 left it.**

**Cost of the block: 0.233 core-min, named as waste, not netted** (§9).

**What the supervisor is asked to rule on — and nothing is pre-judged here.** Whether the one-key
mismatch in `d1_fd_endpoint.py` may be repaired under `VERIFICATION_CHARTER.md` §2d.1 after first
compute, and if so whether arm C re-runs under this frozen file or under a fresh registration. If
it is repaired: **arms E and O were graded on a driver whose FD algorithm, ladder, step rule and
clearance arithmetic the repair would not touch** — the defect is confined to
`planted_zero_control`, which arms E and O never call — but §4.2(c) as written voids on any edit,
and **it is the supervisor, not this lane, that reads that clause against this fact pattern.**
The deferred shipped-image *optimisation* twin (§3.3, priced 19.8 core-min) is **not** entered here
and remains deferred.

---

## 9. Cost — §7.2 predicted-versus-actual, the registered deliverable

`cost_basis: c7a.4xlarge at $0.0513/core-h — REPORTED-BY-OWNER (owner-stated 2026-08-21/22), NOT
MEASURED.` The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Every dollar
figure below is DERIVED.** Core-minutes are wall seconds × ranks ÷ 60, billed as cores × wall for
the whole clock — the lab's DAFoam convention, because `docker run` holds its cpu allocation
whether the solver saturates it or not. **All wall figures are read from the run root's own
`ledger.txt`, not from memory** (append rule 2).

### 9.1 Per-arm

| stage | predicted core-min | **actual core-min (from logs)** | ratio | note |
|---|---|---|---|---|
| zero-compute reads, staging, driver self-tests | 0.000 | **0.000** | exact | no container started |
| **arm E** | 1.2 | **0.750** gross (0.450 graded + **0.300 void**) | 0.63× gross / **0.38× graded** | run 1 voided under §4.2(c) |
| **arm O** | 19.8 | **6.017** | **0.30×** | 11 majors, `Optimal Solution Found.` |
| **arm C** | 2.0 | **0.233** | **not comparable** | crashed at 14 s of a 400 s cap; **no registered work performed** |
| **TOTAL** | **23.0** | **7.000 gross** | **0.304×** | **$0.005985 DERIVED** vs $0.01967 DERIVED |
| with 100% contingency | 46.0 | — | 0.152× | band **HIT** |
| HARD CEILING | 120.0 | — | **0.058×** | no overrun, nothing stopped |

**Cleaned = gross = 7.000 core-min.** The 3,600-s stall rule matches **no row**: the longest wall on
this item is **361 s**, an order of magnitude clear. The record says so rather than leaving the
column blank (§7.2 item 1).

**WASTE, named separately and never laundered into the ratio or either column
(`COMPUTE_BUDGET_CHARTER.md` §6): 0.533 core-min = $0.000456 DERIVED.**

| waste row | core-min | cause |
|---|---|---|
| arm E run 1, VOID | **0.300** | driver edited after it launched; §4.2(c) applied as written — voided, not repaired (Addendum §16, L-266) |
| arm C, crashed | **0.233** | `KeyError: 'CD_final'` in the frozen G5 comparator; zero registered work produced (§8) |

### 9.2 Per-major — why §7.2 item 3 asked for it

| | predicted | measured | ratio |
|---|---|---|---|
| majors | **18** | **11** | 0.61× |
| core-min per major | **1.0** | **0.42127** (`D1_DRIVER_WALL_S 278.04` s ÷ 11 ÷ 60) | **0.42×** |
| driver cost = majors × per-major | **18.0** | **4.634** | **0.26×** |

Cross-check on the whole-arm clock rather than the driver marker: 361 s ÷ 11 = **0.54697
core-min/major**, also inside P5's [0.4, 3.5]. The driver-wall figure is reported as primary
because it is the like-for-like work marker (`prob.run_driver()` alone), and the whole-arm figure
is given beside it so a reader can see the 83 s the endpoint block and container startup cost.

### 9.3 Gap attribution — three ways, waste kept separate

**MISPREDICTION — the whole of the gap, and it compounds.** The 0.30× total is the product of two
independent over-estimates in the same direction, which is why it is much larger than either:

* **Majors over-predicted 18 → 11 (0.61×).** P2's band was registered wide *on purpose* and it
  held; its **point** did not. The registered reasoning ("A1 has 9 live DVs and 24 constraint rows;
  per-DV extrapolation from A4's 1-DV case is not defensible") was sound, and the honest reading is
  that the width carried the prediction and the point carried nothing.
* **Per-major cost over-predicted 1.0 → 0.42127 core-min (0.42×).** **The cause is measured, not
  guessed.** P5's basis budgeted a major as *"≈ 1 deformed primal + the CD and CL adjoints + ~1
  line-search primal."* **The line-search primal never happened**: all 11 majors took
  `alpha_pr = 1.00e+00` with **`ls = 1`** (§4.3) — IPOPT accepted the full step every time and
  backtracked on none. A basis that prices a line-search trial into every major over-prices every
  major on a run that never backtracks. **The labelled A4-scaled cross-check (≈3.3 core-min/major,
  which set P5's band ceiling at 3.5) was wrong by 7.8×**, and A1's own measured np=1 anchor was
  the better of the two by a wide margin — as §7 predicted it would be.

**CONTENTION — measured where it could be, and not asserted where it could not.** Arm O launched
onto `load1 4.24` of 16 cores and ran `--cpus=1`; **no contention penalty is claimed against it.**
The like-for-like work-marker method (`A4` §6.1) **cannot** be applied on this item, because it
needs the same work timed in two arms and **arm C produced no work** — so the contention column is
reported as **not separately measured**, not as zero. What *is* measured is contention's effect on
the **schedule** rather than the cost: arm C's launch was **delayed 73 s** by two `NOT_OPEN` gate
readings (`free_cores` 1.98 and 2.60), and that delay is **0.000 core-min** — the gate costs
waiting, never core-minutes.

**WASTE — 0.533 core-min, named above, and NOT absorbed into either of the other two, nor into the
ratio's explanation.** Stated as a fraction so it is legible: waste is **7.6%** of this item's gross
spend, and it is **100%** of arm C's spend.

### 9.4 The calibration row, **DRAFTED for the supervisor to land** (Amendment 1 §A1.1)

**This lane does not write `docs/COST_CALIBRATION.md`.** Amendment 1 §A1.1 supersedes §7.2 item 5 on
exactly this point. The row below is drafted in that file's registered ten-column format; the
supervisor lands it, reading the file's current tail with `git show HEAD:` **inside the committing
invocation**, asserting the diff is **insertions only**, under the rule-10 private-index protocol.

**Row id: `C-24`** — derived at drafting time from `git show HEAD:docs/COST_CALIBRATION.md | grep
-oE '^\| C-[0-9]+'`, whose **maximum** is `C-23` (`CLAUDE.md` rule 11: the maximum existing number,
never a count). **Re-derive at append time**; peers commit constantly.

```
| C-24 | 2026-08-24 | dafoam | Curriculum D1 — A1 lift-constrained drag minimisation (arm E graded, arm O PASS, **arm C BLOCKED — item INCOMPLETE**) | **23.0 core-min** registered (§7 of the prereg, frozen before first compute; contingency 46.0, HARD CEILING 120.0) = $0.01967 derived | **7.000 core-min measured** (wall × ranks ÷ 60, all four rows from the run-root `ledger.txt`: armE run 1 18 s, armE run 2 27 s, armO 361 s, armC 14 s, all np=1) = **$0.005985 derived** | **= gross, 7.000 core-min.** Longest wall on the item is 361 s, so the 3600-s stall rule matches no row and there is nothing to clean out. Waste is named separately below and is **not** netted off either column | **0.304×** cleaned/predicted (7.000 / 23.0); **0.058× of the 120.0 ceiling**; **per-major 0.421×** (0.42127 vs 1.0 core-min/major) | **INCOMPLETE SCOPE — the figure is a lower bound, not a completed-item cost: arm C (registered 2.0 core-min) delivered none of its registered work.** **Misprediction, compounding, in the conservative direction:** majors 11 vs 18 predicted (0.61×) **and** per-major 0.42127 vs 1.0 core-min predicted (0.42×), so the driver cost landed at 0.26× (4.634 vs 18.0). **The per-major cause is measured, not inferred:** P5's basis priced "~1 line-search primal" into every major, and **all 11 majors took `alpha_pr = 1.00e+00` with `ls = 1` — IPOPT backtracked on none**, so that primal was never bought. The labelled A4-scaled cross-check (≈3.3 core-min/major, which set P5's band ceiling) was wrong by 7.8×; A1's own np=1 `check_totals` anchor was much the better basis. **Contention: NOT SEPARATELY MEASURED** — the A4 §6.1 like-for-like work-marker method needs the same work timed twice and arm C produced no work; arm O launched at `load1 4.24`/16 cores and no penalty is claimed. Contention did cost **schedule**: arm C waited **73 s** across two `NOT_OPEN` launch-gate readings (`free_cores` 1.98, 2.60), at **0.000 core-min** — the gate costs waiting, never core-minutes. **WASTE NAMED, 0.533 core-min = $0.000456 derived, 7.6% of gross, never absorbed into the ratio: 0.300** (armE run 1 VOID under the prereg's own §4.2(c) — driver edited after launch; Addendum §16, L-266) **+ 0.233** (armC crashed at 14 s on `KeyError: 'CD_final'` in the frozen G5 comparator, zero registered work). **Calibration lesson: an estimate built from a whole-`check_totals` anchor prices a line search into every major; when the optimiser accepts full steps, the per-major basis must be re-derived from the accepted-step composition, and the `ls` column is where that is read.** **A correcting row is owed if arm C later runs.** | `cases/dafoam/ladder-a/A1/curriculum_D1/RESULTS.md` §9; prereg frozen before first compute, Addendum §16 landed at `668ce997`; run-root ledger (measured, outside git): `/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/ledger.txt` |
```

---

## 10. Falsifiers — every one, scored

| id | falsifier | outcome |
|---|---|---|
| **F1** (as corrected by Amendment 2 §A2.1) | arm E's cold baseline `CD` ≠ `0.02091051000679216` (np=1) | **did not fire** — `0.020910510006792161`, all printed digits; np=2 gap `1.479937e-10` reported beside it |
| **F2** | any arm's printed `IDWARP_SO_MD5` ≠ §3's row → that arm void | **did not fire** on any of the four containers |
| **F3** | reduction ≤ 0% | **did not fire** — **+16.310321%** |
| **F4** | objective non-monotone on an accepted step | **did not fire** — strictly decreasing on all 11; `inf_pr` non-monotonicity reported at §4.3 and is not what F4 registers |
| **F5** | any endpoint component shows a sign flip | **did not fire** — zero flips at both steps on all four components |
| **F6** | trivial baseline at `1e-8` returns ≤ 5% | **did not fire** — **112.6004%**, sign-flipped; G3's verdict stands |
| **F7** | the planted-zero comparator cannot see its plant → exit 2 | **NOT TESTED — the comparator crashed before planting** (§8, §6 G5). Not a fire and not a pass. **No comparator figure computed from a file is reported anywhere in this record** |
| **F8** | `volcon` or any `thickcon` row ≠ `1.0 ± 1e-9` at the undeformed baseline | **did not fire** — worst deviation **2.243e-14** across all 24 rows |

---

## 11. Records DRAFTED for the supervisor to append — never appended by this lane

`DAFOAM_CHARTER.md` §11 and `PREREGISTRATION.md` §12 item 4. **Every number below is re-derived
from the tail at drafting time and MUST be re-derived again in the committing invocation**
(`CLAUDE.md` rule 11 — the **maximum existing number**, never a count). Maxima at
`9d1d348a9725879e98b4d575d9bd973bb9fa17de`: `L-272`, `N-D27`, `D495`, `C-23`.

### 11.1 Proposed lesson (next id; `L-273` at drafting time)

> **L-273. A planted-zero control that plants into its own fixture proves the arithmetic and not
> the coupling — plant into a file the producer actually wrote.**
>
> Curriculum D1 arm C: the G5 control passed its zero-compute self-test **and** its negative control
> (a deliberately blind reader refused with exit 2), then killed the arm at 14 s on
> `KeyError: 'CD_final'` — the producer writes `"CD"` (`d1_opt_runScript.py:417`) and the consumer
> reads `"CD_final"` (`d1_fd_endpoint.py:110`). The self-test had planted into a hand-built dict
> carrying the consumer's own key, so it verified the reader against a schema the pipeline never
> produces. `CLAUDE.md` rule 3's logic applies to the control itself: a plant seen in a file no
> producer writes is not the demonstration the rule asks for. Cost: 0.233 core-min of named waste
> and a `BLOCKED` toolchain row that a 2.0 core-min arm was bought to fill. **The habit that closes
> it: the pre-launch control consumes a real artifact from the producing step — or, where none can
> exist before the run, asserts the producer's key set against the consumer's, in the same
> invocation that freezes both.** Same family as L-266 on this same item: both defects were
> findable by dry-running the frozen code against its own frozen inputs before the freeze.

### 11.2 Proposed numerics facts (next ids; `N-D28`, `N-D29` at drafting time)

> **N-D28.** *A1's patched adjoint does not degrade at a converged constrained optimum.* On A1
> NACA0012 (4,032 cells, np=1, `dafoam-idwarp-rot:v1`), at the design point IPOPT reached after 11
> majors, the endpoint analytic gradient agrees with central differences at **0.0525%
> (`shape[6]`)**, **0.1638% (`shape[1]`)**, **0.1229% (`shape[5]`)** and **0.2553% (`patchV[1]`)**,
> **zero sign flips**, vector-relative **0.11479%** over the four graded components. `shape[6]` —
> the LE combo mode that reads **640.3696% and sign-flipped** on the shipped image at baseline and
> **1.1888%** patched at baseline — reads **0.0525%** here, a **23× improvement over its own
> patched baseline**. `DAFOAM_CHARTER.md` §9's warning (*a gradient verified at iteration 0 is not
> verified at iteration 47*) is **not** borne out on this case at this design point. The two
> columns are read at different steps (baseline 1e-3, endpoint 3e-4), both inside A1's measured
> 1e-4…3e-2 plateau, and the comparison claims no more than that. **The shipped-image companion at
> the same design point was BLOCKED, so this is a patched-row fact and carries no toolchain
> comparison.**
>
> **N-D29.** *A1's η is a plateau reading and the window is the whole measurement.* Cold np=1
> baseline primal exiting on `primalMinResTol 1e-8`: peak-to-peak of `CD` over the **last 5 printed
> samples** (t = 400…435, `printInterval 10`) is **`1.957350e-08`**, reproduced to every printed
> digit across two independent cold starts. The same case's **last-200-iteration, 20-sample**
> peak-to-peak (A6's definition, N-D13) reads **`7.824305e-06`** — **400× larger** — because A1's
> tolerance exit makes its final 200 iterations a convergence tail, not a plateau, where A6's fixed
> `endTime 1000` made them a plateau. **The same formula measures noise on one case and convergence
> on the other; η is a property of a configuration, never of a case.** Consequence measured on this
> item: at the endpoint the A6-window reading would have driven `shape[6]` below `C ≥ 5` at every
> admissible rung and flagged it, while the registered plateau reading cleared it at **283.1**.

### 11.3 Proposed docket row (next id; `D496` at drafting time)

> **D496 — CURRICULUM D1 GRADED ON THE PATCHED ROW AND BLOCKED ON THE SHIPPED ROW.** A1
> NACA0012 lift-constrained drag minimisation: IPOPT `EXIT: Optimal Solution Found.` in **11
> majors**, `Overall NLP error 4.087129e-07`; `CD` **0.020943920630946831 → 0.017527899854535338**
> = **−16.310321%** at `|CL − 0.5| = 1.879064e-07` with all **24** geometric rows inside their
> registered bounds (**G1 PASS**); the endpoint gradient re-verified in the same process at
> **≤ 0.2553%** on all four named components with **zero sign flips** (**G3 PASS**), steps chosen
> from `|J_adj|` and η alone and landing on exactly the pairs §6 G3 item 3 registered in advance;
> trivial baseline **112.6004%** sign-flipped, so the instrument can fail (**G4**). **P3 MISSED
> HIGH — 16.31% against a registered [2%, 12%] band** — because the band reasoned about which
> constraints were tight rather than which directions were free: three constraint families are
> active at the optimum and the optimiser still bought 16.3% by trading camber for incidence
> (`AoA` 5.15° → 1.13°, all eight `shape` modes positive). **ARM C IS `BLOCKED`** on a one-key
> mismatch in the frozen G5 comparator (producer writes `"CD"`, consumer reads `"CD_final"`),
> found at 14 s before any solve; **the lane did not repair it, did not retry and did not route
> around it** — §4.2(c) has already been spent once on this item (L-266) and a second
> post-first-compute edit is the supervisor's call under `VERIFICATION_CHARTER.md` §2d.1. **The
> §3.3 toolchain comparison at a common deformed design point remains open**, exactly where
> `A4/shipped_optimisation_np1/RESULTS.md` §8 limit 3 left it. Spend **7.000 core-min gross**
> (0.304× of 23.0 registered, 5.83% of the 120.0 ceiling) = **$0.005985 DERIVED**, **0.533
> core-min named waste**; peak RSS **1.6964 GiB** against a 2.0 GiB registered ceiling and a 6 GiB
> kernel cap, no container OOM-killed. **G6 refused a launch for the first time on this item** and
> the arm waited 73 s rather than departing. **NOT FILED ANYWHERE.**

### 11.4 Proposed `EXPERTISE_CURRICULUM.md` §7 execution-ledger row

> **D1 — A1 lift-constrained drag minimisation.** State: *prereg dispatched* → **`PENDING` —
> patched row `PASS`, shipped row `BLOCKED`.** Pre-registration:
> `cases/dafoam/ladder-a/A1/curriculum_D1/PREREGISTRATION.md`, frozen before first compute,
> Amendments 1–2 before first compute, Addendum §16 after first compute (`668ce997`). Results:
> `cases/dafoam/ladder-a/A1/curriculum_D1/RESULTS.md`. Arms E and O complete and graded; arm C
> `BLOCKED` on a frozen-driver defect awaiting a supervisor ruling. **Cost: 7.000 core-min gross
> against the curriculum's own ~70 core-min estimate and the lane's re-derived 23.0** — the
> lane's re-derivation was the better estimate by 3.0× and still over-predicted by 3.3×.
> Calibration row **drafted** at RESULTS §9.4 as `C-24`, **not landed by the lane**.
> **NOT FILED ANYWHERE.**

**None of the four rows above has been written to any file by this lane.** `docs/LESSONS.md`,
`docs/NUMERICS_KNOWLEDGE.md`, `docs/DOCKET.md`, `docs/COST_CALIBRATION.md`,
`cases/dafoam/EXPERTISE_CURRICULUM.md` and `cases/dafoam/LADDER_A_STATUS.md` are **untouched**.

---

## 12. Verdict vocabulary

**`PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`.** No other word grades
anything in this file. Every verdict above is stated against a falsifier or a gate registered in
`PREREGISTRATION.md` **before** the run that produced it. Shipped and patched rows are reported
separately and are never merged. The optimiser was **not** stopped by a wall clock, an iteration cap
or a budget, so `GATE REACHED` is not in play; and no verdict anywhere in this file is described by
the size of the improvement it reached.

**NOT FILED ANYWHERE.**
