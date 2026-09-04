# ⚠ DRAFT — **UNFROZEN**, **NOT QUEUED**, **NOT LAUNCHED**, **NO COMMITTED SHA**. AWAITING `dafoam-supervisor`'s READ AND FREEZE.

> **THIS DOCUMENT IS NOT A PRE-REGISTRATION YET.** It carries no freeze, no committed sha, and
> no instrument md5 that has been asserted against a HEAD blob. **Nothing in it authorises
> compute.** Under `CLAUDE.md` rule 2 the gates are open only until first compute, and under
> `SUPERVISION_CHARTER.md` §3 check 4 the *pre-registration committed before compute* check is
> **the supervisor's own and may not be delegated** — this lane has not discharged it and does
> not claim to. **Nothing launches without the supervisor's read of the COMMITTED
> pre-registration.**
>
> **Nothing in this item is filed, sent, uploaded, registered, posted or commented outside this
> box** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS REMAIN PARKED.**
>
> **Drafted 2026-09-04 by a dafoam `lab-lane` for `dafoam-supervisor`, `[lab-attributed]`.**
> Every decision below is `[lab-attributed]` and **Sanaa can overrule any of it.**

---

# `W3S` — DOES **ANY** AVERAGING WINDOW ADMIT AN FD STEP ON THIS CELL? THE DIAGNOSTIC ARM FIRST, THE WINDOW ARM ONLY IF THE DIAGNOSTIC SAYS SO

**Item id:** `W3S` (**W3 Successor**; the family's suffix convention, as `W2R` is W2's re-run).
`W4` and `W5` are **not** available as ids — they name standing DAFoam wells in the roster
(`DAFOAM_CHARTER.md`, `cases/dafoam/`), and reusing one would collide.
**Case directory:** `cases/dafoam/curriculum_D12R2`.
**Predecessors:** `PREREGISTRATION.md` (D12R2, `W = 300`), `W2_PREREGISTRATION.md`,
`W2R_PREREGISTRATION.md` (`W = 900`), `W3_PREREGISTRATION.md` v1.4 (`W = 2,000`).
**The result this item answers:** `RESULTS_W3.md` §6.5 — **`W·|g(W)|` FELL from `W = 900` to
`W = 2,000`.**

---

## 0. WHY THIS ITEM EXISTS, AND WHY IT IS **NOT** "RUN W3 AGAIN AT A BIGGER `W`"

W3's registered fallback (`W3_PREREGISTRATION.md:55`) is a `W = 2,400` variant. **Measured on
W3's own gradient, that fallback is not admissible** — `h_min,env(2400) = 0.075994` against
`h_max = 0.05`, 1.52× over (`RESULTS_W3.md` §6.3). Firing it as written would spend a registered
236.5 core-min to reproduce the same `NOT A RESULT` on the same branch.

**And the naive repair — set `W = 4,000` — is worse, because it registers a prediction the
record already falsifies.** Admissibility on the envelope depends on `W` **only** through the
product `W·|g(W)|`:

```
h_min,env(W) = 100 · (C_ENV / W) / |g(W)| = 100 · C_ENV / ( W · |g(W)| )
```

so admissibility at `h_max = 0.05` requires **`W·|g(W)| ≥ 100 · 0.8907 / 0.05 = 1781.4`**.

**MEASURED, three points, three artefacts on disk:**

| `W` | `\|g(W)\|` | `W·\|g(W)\|` | `h_min,env` | artefact |
|---|---|---|---|---|
| 300 | `1.0304158599180422` | **309.12** | 0.288136 | `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady/step_plan.json` |
| 900 | `1.1398352621255485` | **1025.85** | 0.086825 | `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady/step_plan.json` |
| 2,000 | `0.48835975139977306` | **976.72** | 0.091193 | `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady/step_plan.json` |
| **required** | — | **≥ 1781.4** | ≤ 0.05 | — |

**`W·|g|` rose 3.32× from `W = 300` to `W = 900`, then FELL 4.79 % to `W = 2,000`.** The best
value the family has ever measured is **1025.85 at `W = 900`** — a factor **1.74 short** of the
requirement — **and it occurs in the MIDDLE of the measured range, not at its end.** Over
`900 → 2,000` the two-point exponent is `|g| ∝ W^(−1.061)`; at any exponent steeper than `−1`,
**a longer window RAISES `h_min`.**

**So the question this item must answer first is not "which `W`", it is "does `W·|g(W)|` ever
reach 1781.4 at all".** That question is answered by three adjoint solves, not by a 33-stage
phase 1 at a guessed window.

---

## 1. THE AMENDMENT CONDITION, TO BE STATED **AND CHECKED** AT FREEZE — NOT CHECKED YET

At freeze this section must name the run root and record `test -e` returning **false**, with a
timestamp, per `VERIFICATION_CHARTER.md` §2b. **Proposed roots:**

- Arm A: `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3S-GSCAN-cylinder-unsteady`
- Arm B: `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3S-WINDOW-cylinder-unsteady`

**Neither has been created and neither check has been driven by this lane.** At the time of
drafting neither path exists, but that is a *reading taken while drafting*, **not** the §2b
condition — the §2b condition is checked at the freeze commit, in the freeze commit's own shell
invocation, and is the supervisor's to see driven. **This draft does not claim it.**

---

## 2. WHAT IS INHERITED UNCHANGED, AND WHY EACH INHERITANCE IS DELIBERATE

Inherited **byte-unchanged in intent** from `W3_PREREGISTRATION.md` §0 and §5: the mesh
(2,450 cells), `TRANSIENT_DISCARD = 300`, `NSHAPES = 4`, `DPERT_HA/HB = 1e-6 / 1e-5`,
`ENV_STEPS = 20 40 80`, `h_max = 0.05`, `EPS_NOISE_TARGET = 0.01`, `C_ENV = 0.8907`, band D at
`G12R-6`, the trivial baseline at `10·h*` (`G12R-7`), the envelope `3σ` (`G12R-8`), planted
zeros (`G12R-9`), the two-row rule (`G12R-10`), `MEM_LIMIT = 8g`,
`MEMAVAIL_FLOOR_GIB = 14.0` (**not lowered**), `np = 1`, `numberOfSubdomains = 1`, the producer
`d12y_run_script.py` md5 `2790c39a09cd458d5a3263d7f1811da5`, and the SHIPPED row first
(`--image shipped`).

**Three inheritances are called out because leaving them alone COSTS money and doing so is the
point:**

1. **`h_max = 0.05` IS NOT WIDENED.** It is 10 % of the cylinder radius and is a geometric
   limit on how far an FFD shape mode may move before the perturbed body is a different body.
   **Widening `h_max` would manufacture admissibility by moving the gate**, which Sanaa's own
   T25 ruling forbids (*no widening on optimism*) and which the 2026-09-04 mandatory-completion
   order explicitly excludes: *"Working a case to a pass means fixing OUR side until the physics
   can speak; it never means adjusting the gate until the answer fits."*
2. **`EPS_NOISE_TARGET = 0.01` IS NOT RELAXED**, for the same reason. Both `h_max` and
   `EPS_NOISE_TARGET` enter the admissibility test directly and both are frozen at their
   inherited values.
3. **THE 16 `S3b` STAGES ARE KEPT IN ARM B, AT 55 % OF ITS COST, DELIBERATELY.** On W3 they
   produced `δ_pert = 1.660120842239543e-06`, **268× below** the term that decided the verdict,
   and `detectable: false` on 2 of 4 components. Dropping them is the single largest available
   economy — **and it is forbidden here**, because `δ_eff` is a **maximum** and **removing a term
   from a maximum can only LOWER `h_min`**, i.e. move toward `admissible: true`.
   `W3_PREREGISTRATION.md:76` states the one-way argument in the safe direction (*"Adding a term
   to a maximum can only RAISE `h_min` … it can cause a `NOT A RESULT`, it cannot manufacture a
   `PASS`"*); its converse is why this economy is refused. **The saving is named so that nobody
   proposes it later without seeing why it was declined.**

---

## 3. THE TWO ARMS

### 3.1 ARM A — `GSCAN`: buy `|g(W)|` at three windows, and nothing else

**Stage graph (proposed, 6 stages):** `S0` (mesh) · `S1a` · `S1b` · `S2a` (transient discard →
`FIELD_B`) · then **three `S5` adjoint stages** at `W ∈ {2000, 1400, 3000}` from that same
`FIELD_B`.

**It deliberately omits** `S2b` (the CD series), `S3 ×3`, `S3b ×16`, `S4 ×6` and `S7 ×2`.
**Arm A grades NO admissibility verdict and computes NO `h_min` that gates anything** — it
measures `|g(W)|` and the product `W·|g(W)|` against the fixed requirement 1781.4, on the
**envelope** `δ_window,env = C_ENV/W`, which is already measured to ≤ 0.3 % at the local maxima
across 92 windows (`W3_PREREGISTRATION.md` §2). **Because Arm A drops terms from `δ_eff`, it is
barred from producing an `admissible: true`**; it can only produce the diagnostic and the
no-launch decision. That asymmetry is registered here, before the arm runs, and the successor
comparator must **refuse** if Arm A is asked for a step plan.

**`W = 2,000` is repeated in a FRESH ROOT as the first leg, and it is a planted-style control on
the finding itself.** The entire §0 argument rests on one measurement, `|g(2000)| = 0.48836`,
taken once. **A single sample is not a trend.** Leg A0 re-measures it through the whole chain —
fresh mesh, fresh init, fresh transient discard — and if it does not reproduce, §0's finding is
a single-sample artefact and this item's whole design changes. **The control is registered
first, before the two new windows, so an unreproducible anchor stops the arm at 69.6 core-min
instead of 215.7.**

**`W = 1,400` and `W = 3,000` are chosen to BRACKET, not to extend.** 1,400 lies between the
900 maximum and the 2,000 decline and tests whether the peak in `W·|g|` is real and where it
sits; 3,000 tests whether the decline continues. **Neither is chosen because it is expected to
pass** — §5 predicts both will fail — and that is what makes them a measurement rather than a
search.

### 3.2 ARM B — `WINDOW`: the full 33-stage phase 1, **CONDITIONAL**, and it fires on a rule fixed here

**Arm B fires if and only if `FS-1` HITS** (§4). Its window `W_adm` is **not chosen by a lane
after seeing the data**; it is fixed by this rule, registered now:

> `W_adm` = the **smallest** window `W` in the measured set `{300, 900, 1400, 2000, 3000}` for
> which `W·|g(W)| ≥ 1781.4 × 1.15` — i.e. a **15 % margin** on the requirement, because a
> window that clears it by 0 % is a window sized to fit its own answer. If no measured `W`
> clears the margined bar, **Arm B does not fire**, whatever the unmargined value.

Arm B is then W3's item form unchanged at `W = W_adm`: the 33-stage graph, every gate
`G12R-0` … `G12R-11` / `G12R-W`, phases 1 → 4 as one detached driver stopping at the first
non-zero rc, and the same verdict mapping (`W3_PREREGISTRATION.md` §7).

---

## 4. THE FALSIFIERS, REGISTERED BEFORE ANY COMPUTE

| id | falsifier | HIT | MISS |
|---|---|---|---|
| **`FS-0` (GATING, BINARY)** | `\|g(2000)\|` reproduces in a fresh root | leg A0 returns `\|g\|` within **±1 %** of `0.48835975139977306` | outside ±1 % → **Arm A STOPS at leg A0**, the item is **`NOT A RESULT`** on a **reproducibility** finding, and `RESULTS_W3.md` §6.5's `W·\|g\|` reading is withdrawn as single-sample. This is the more important outcome of the two, because it would invalidate the reasoning that sized this item. |
| **`FS-1` (PRIMARY, BINARY)** | **some** measured window satisfies `W·\|g(W)\| ≥ 1781.4 × 1.15 = 2048.6` | Arm B fires at `W_adm` per §3.2 | **no** measured window clears it → **Arm B LAUNCHES NOTHING** (the registered no-launch branch, W3's form), the item is **`NOT A RESULT`**, and the registered structural finding is recorded: *on this cell, at the inherited `h_max = 0.05` and `EPS_NOISE_TARGET = 0.01`, no averaging window in the measured set `[300, 3000]` admits an FD step, and `W·\|g(W)\|` does not increase with `W` over `[900, 3000]`.* |
| `FS-2` (Arm B, inherited) | at `W_adm`, `G12R-4` returns `admissible: true` and `G12R-6` grades in band D | W3's `PASS` / `GATE REACHED` mapping | W3's `GATE FAIL` / `NOT A RESULT` mapping, unchanged |

**`FS-1` is registered in the direction the record points, and this registration PREDICTS ITS
OWN PRIMARY FALSIFIER WILL MISS** (§5, `Q4`). That is deliberate. An item that can only be
"successful" by finding what it hoped for is an item whose gate was chosen to fit; this one
buys a decisive **no** for 215.7 core-min instead of buying a hopeful **maybe** for 525.

**Verdict mapping (the fixed vocabulary, `CLAUDE.md` rule 1):**

| outcome | verdict |
|---|---|
| `FS-0` MISS | **`NOT A RESULT`** — reproducibility |
| `FS-0` HIT, `FS-1` MISS | **`NOT A RESULT`** — the structural finding; Arm B never fires |
| `FS-1` HIT, Arm B `G12R-4` `admissible: false` | **`NOT A RESULT`** |
| `FS-1` HIT, `G12R-6` outside band D or any sign flip | **`GATE FAIL`** |
| `FS-1` HIT, `G12R-6` band D `PASS`, S8 `Optimal Solution Found.` | **`PASS`** |
| `FS-1` HIT, `G12R-6` band D `PASS`, S8 stopped on `CAP_S8` or its wall bound | **`GATE REACHED`** (`DAFOAM_CHARTER.md` §9) |
| any refusal (completion, manifest/ledger `W` mismatch, row count, planted zero unseen) | **`NOT A RESULT`** |
| aggregate-cap bound, `MemAvailable` floor, an S5 OOM, a PETSc failure | **`BLOCKED`** |

---

## 5. PREDICTIONS `Q1`–`Q6` — HIT/MISS, scored by the successor comparator and the record, never adjusted

| # | prediction | basis | HIT form | MISS form |
|---|---|---|---|---|
| **Q1** | leg A0 reproduces `\|g(2000)\|` | np = 1, `δ_repeat = 0.0` measured on W3's `S3_r1/r2/r3` (all three `0.6561057342918396`), so the primal chain is bit-deterministic and the adjoint from a byte-identical field should be too | within **±1 %** of `0.48835975139977306` | outside — `FS-0` MISS |
| **Q2** | `\|g(1400)\|` | the two-point power law `\|g\| = 0.48836·(W/2000)^(−1.061)` fitted on `W = 900` and `W = 2,000`, **explicitly labelled a two-point slope and NOT a law** (`RESULTS_W3.md` §6.6 item 1) | in **`[0.499, 0.927]`** (point 0.713, ±30 %) | outside — the power law is refuted, which is itself a finding |
| **Q3** | `\|g(3000)\|` | same | in **`[0.222, 0.413]`** (point 0.318, ±30 %) | outside |
| **Q4 (the one that matters)** | **`W·\|g(W)\|` stays BELOW 2048.6 at every measured window** — i.e. **`FS-1` MISSES** | the power law gives `W·\|g\|` = **998.4** (1400), **976.7** (2000), **952.7** (3000), against the 1025.85 measured at `W = 900`: essentially flat at ~1000 and never within a factor 1.7 of the bar | no window clears 2048.6 → the structural finding, Arm B not fired | some window clears it → Arm B fires, ~525 core-min is spent, and **this registration's own primary prediction is REFUTED, which is a better outcome for the lab than being right** |
| **Q5** | Arm A cost lands on the S5 wall model | `S5_wall(W) ≈ −81 + 2.0438·W` seconds, least-squares on the family's three measured anchors (654 / 1,570 / 4,073 s at `W = 300 / 900 / 2,000`; residuals **−18.6 % / +12.0 % / −1.6 %**) | **`215.7 ± 20 %` core-min `[172.6, 258.8]`** from the ledger's `PHASE1_COMPLETE spent=` | outside — re-anchors the model, does not re-cost the run |
| **Q6** | Arm A's peak RSS stays under the inherited 8g cap | D12R2 phase-1 peak RSS **1.3461 GiB**; W3's `S4` envelope flat in `n` (1.3145 → 1.3129 GiB over `n = 20/40/80`); W3's `S5` at `W = 2,000` ran with `oomkilled = false` under 8g. **Whether the unsteady adjoint's checkpointing memory grows with `W` is NOT MEASURED** (`W3_PREREGISTRATION.md:82`) | no `oomkilled`, no `MemAvailable` refusal | an S5 OOM at `W = 3,000` → **`BLOCKED`**, and the memory envelope becomes the finding (`DAFOAM_CHARTER.md` §7: the prediction is written before the launch, and a memory-ended run is graded as such) |

---

## 6. COST — **PER ARM, IN THIS FROZEN DOCUMENT**, anchored on W3's own measured per-stage ledger

> **This section exists in this form because a queue row is not a registration.** The rule-12
> gap found in this family on 2026-09-03 was estimates living only in the queue entry; this
> family's forward-only rule is that **per-arm estimates are IN the frozen document**. A
> proposal with no cost is disqualified (`CLAUDE.md` rule 12).

**The anchors, all MEASURED, all from W3's 33 manifest rows at `W = 2,000`
(`/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady/manifest.jsonl`, whose
`core_min` fields sum to 271.2501 = the ledger's `PHASE1_COMPLETE spent=`):**

| anchor | value | derivation |
|---|---|---|
| setup (`S0`+`S1a`+`S1b`+`S2a`), `W`-independent | **1.7500** core-min | 0.0667 + 0.25 + 0.5333 + 0.9 |
| `S4 ×6`, `W`-independent | **14.7001** core-min | runs `n = 20/40/80`, not `W` |
| `S2b`, per registered step | **2.7847e-03** core-min/step | 6.6833 / 2,400 |
| the 22 `W`-proportional stages (`S3 ×3`, `S3b ×16`, `S5`, `S7 ×2`), per stage-step | **5.6390e-03** core-min | (19.1 + 149.2168 + 67.8833 + 11.9166) / (22 × 2,000) |
| `S5` wall | **`−81 + 2.0438·W` s** at `np = 1` | least squares on 654 / 1,570 / 4,073 s |

### 6.1 ARM A — `GSCAN`

| leg | `W` | predicted | basis |
|---|---|---|---|
| setup (`S0`+`S1a`+`S1b`+`S2a`) | — | **1.75** core-min | measured, `W`-independent |
| `A0` `S5` repeat | 2,000 | **66.78** core-min | model; **measured on W3 at 67.8833**, +1.6 % — the model is anchored here |
| `A1` `S5` | 1,400 | **46.34** core-min | model (2,780 s) |
| `A2` `S5` | 3,000 | **100.84** core-min | model (6,050 s) |
| **ARM A POINT** | | **215.71 core-min** | |
| **ARM A BAND ±20 %** | | **`[172.6, 258.8]`** | the model's worst residual on its own anchors is 18.6 % |
| **ARM A CAP (registered, cumulative, asserted before every stage)** | | **`CAP_CORE_MIN_A = 330.0`** | 1.53× the point; **an overrun STOPS the run, it does not get a new budget** |
| **early-stop** | | **`FS-0` MISS at leg A0 stops the arm at ≈ 68.5 core-min** | registered, §4 |
| dollars, **DERIVED NOT MEASURED** | | **$0.1844** at point, **$0.2822** at cap | $0.0513/core-h, c7a.4xlarge, **REPORTED-BY-OWNER** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |

### 6.2 ARM B — `WINDOW`, **conditional, and not queued until `FS-1` HITS**

| `W_adm` | `S2b` steps | predicted | band ±20 % | cap |
|---|---|---|---|---|
| 3,000 | 3,400 | **398.09** core-min | `[318, 478]` | `CAP_CORE_MIN_B = 650.0` |
| 4,000 | 4,400 | **524.94** core-min | `[420, 630]` | `CAP_CORE_MIN_B = 800.0` |

Arithmetic at `W = 4,000`: `16.4501` (setup + `S4 ×6`) `+ 4,400 × 2.7847e-03 = 12.25` (`S2b`)
`+ 22 × 4,000 × 5.6390e-03 = 496.23` (the 22 `W`-proportional stages) = **524.94**.
Dollars **DERIVED NOT MEASURED**: **$0.4488** at the `W = 4,000` point.
`CAP_S8 = 400.0` inherited unchanged.

**Both arms sit under the $25 pre-authorisation and are still costed, because a proposal with no
cost is disqualified.** `cost_basis` for both: **derived / REPORTED-BY-OWNER, NOT MEASURED.**

### 6.3 **THE `S2b` LENGTHENING REQUIREMENT, AND WHAT IT COSTS**

`d12y_grade_w3.py:202-209`, `block_averages`, **refuses** on `len(cd) < W`:

> `raise Refusal("series of %d samples cannot support a %d-step window" % (len(cd), W))`

**`S2_STEPS` currently stands at 2,400** (`d12y_w3_stage_and_run.sh:153`). Therefore:

| `W_adm` | minimum `S2b` to grade at all | `S2b` for 401 sliding windows (`W + 400`) | `S2b` cost at 2.7847e-03 core-min/step | delta over the inherited 2,400 |
|---|---|---|---|---|
| 3,000 | 3,000 | **3,400** | 9.47 core-min | **+2.78** core-min |
| 4,000 | 4,000 | **4,400** | 12.25 core-min | **+5.57** core-min |

**`S2_STEPS` is a registered constant and moving it is a registered change.** It is small in
money and large in principle: the sliding-window count sets how much phase the `δ_window`
statistic sees, and W3's reading used **401 windows spanning 21 periods**. `W + 400` preserves
that count exactly, so the statistic is the same statistic at the new window and not a different
one wearing the same name.

### 6.4 **THE `S5` STAGE WALL BOUND MUST RISE, AND THIS IS THE REAL REASON ARM B NEEDS A NEW REGISTRATION**

The inherited per-stage wall bound is **7,200 s** for every stage except `S8`
(`W3_PREREGISTRATION.md` §5). On the `S5` wall model:

| `W` | predicted `S5` wall | against the 7,200-s bound |
|---|---|---|
| 2,000 | 4,007 s (**measured 4,073**) | ok |
| 3,000 | 6,050 s | ok, 16 % headroom |
| **3,562** | **7,200 s** | **the crossing** |
| 3,648 | 7,375 s | **EXCEEDS** |
| 4,000 | 8,094 s | **EXCEEDS by 12 %** |

**Any Arm B at `W ≥ ~3,560` would have its adjoint killed by the registered stage timeout.**
Proposed for Arm B at `W_adm ≥ 3,000`: **`S5` stage wall bound 7,200 → 12,000 s** (48 % margin
over the `W = 4,000` prediction), every other stage unchanged. **A timeout is not a
measurement** — a run ended by a wall bound would be `NOT A RESULT` about convergence and would
have bought nothing, which is the shape `DAFOAM_CHARTER.md` §7 names.

### 6.5 CALIBRATION COMMITMENT

**At each arm's completion**, the actual/predicted ratio is entered in
`docs/COST_CALIBRATION.md` under that file's append rules and the rule-10 private-index
protocol, with waste named separately and never folded into the ratio, and dollars labelled
**derived, not measured**. The `S5` wall model's own test is whether a fourth and fifth window
land on its line (`Q5`).

---

## 7. INSTRUMENTS — TO BE BUILT AND FROZEN BY MD5 AT THE FREEZE COMMIT. **NONE EXISTS YET.**

**No instrument in this table has been written.** Listed so the freeze knows what it must pin,
and so the drafting cost is visible rather than discovered later. All drafting is **zero
compute**.

| file | derived from | what changes |
|---|---|---|
| `w3s_grade.py` | `d12y_grade_w3.py` (`3950d30fd09c9b56213a02f5e9864e20`, **UNEDITED**) by a disclosed `.diff` | a `--gscan` mode reading `\|g(W)\|` from a multi-window manifest and grading `W·\|g\|` against 2048.6; a **REFUSAL** if `--gscan` is asked for a step plan (§3.1); `W_PRIMARY`/`W_CONTINGENCY` constants; `S2_STEPS`. **Every existing gate function byte-identical**, asserted in the freeze. |
| `w3s_stage_and_run.sh` | `d12y_w3_stage_and_run.sh` (`8a92f3f84f72d6806a2e5c5df88d82ef`, **UNEDITED**) | the Arm A 6-stage graph; three `S5` call sites with per-stage `W`; `S2_STEPS`; the `S5` wall bound; roots; container prefix; caps; **the `W` key already written into every manifest row is written PER STAGE for Arm A**, since Arm A's rows carry three different windows — **and `_w_from_record`'s single-`W` refusal must therefore be re-registered for Arm A rather than silently relaxed.** |
| `w3s_chain_driver.sh` | `d12y_w3_chain_driver.sh` (`2b6ac7bbc6a5593940a0f2d217005b10`) | the arm sequence; `MD5_LAUNCHER` / `MD5_GRADER` pinned **in the same commit as the files they pin** (the `D8R-DRIVER-DEF-1` / `2026-08-28T02:15:29Z` death) |
| `d12y_run_script.py` | — | **UNCHANGED**, `2790c39a09cd458d5a3263d7f1811da5` |
| planted-failure controls | `d12y_w3_fatal_scan_control.sh` (36/36), `d12y_w3_pin_guard_control.sh` (6/6), `d12y_w3_s2b_selection_control.sh` (11/11) | re-driven against the new instruments; **a control not shown able to FAIL is not a control** (rule 3, L-314) |

> ⚠ **THE ONE THING IN THIS TABLE THAT IS A REAL RISK, FLAGGED FOR THE SUPERVISOR RATHER THAN
> DECIDED BY THIS LANE.** `_w_from_record` (`d12y_grade_w3.py:2437`) **refuses if the manifest
> rows disagree on `W`** — that gate exists because of `W2R-GRADER-DEF-1`, where a comparator
> graded the wrong window silently. **Arm A's manifest rows deliberately disagree on `W`.**
> Relaxing that refusal is the single most dangerous edit in this successor, and it must not be
> done by widening the existing gate. The proposed shape is a **separate `--gscan` binding** that
> requires each row's `W` to match **that row's own registered leg**, refusing on any row whose
> `W` is not one of the three registered values and on any duplicate — strictly *more*
> constrained than the inherited gate, not less. **The supervisor should read that diff as a
> diff** (`SUPERVISION_CHARTER.md` §3 check 1, which may not be delegated).

---

## 8. WHAT THIS ITEM WILL **NOT** ESTABLISH

- **Nothing about the PATCHED row.** The two-row rule is carried, not discharged.
- **Nothing on a second mesh.** 2,450 cells, one mesh, no grid family, **NO GCI**, and standing
  rule 5 has no row. `St ≈ 0.53` remains a resolution artefact.
- **Nothing about `|g(W)|` for `W` outside `{300, 900, 1400, 2000, 3000}`.** `FS-1`'s MISS
  finding is scoped to **the measured set** and says nothing about `W > 3,000`. A record that
  wrote *"no window ever"* would be claiming an enumeration it did not finish.
- **Nothing about whether `|g|` is CORRECT at any window.** `DAFOAM_CHARTER.md` §2: a DAFoam
  gradient is not a result until an FD table stands beside it at a step proved to lie in the
  plateau. **No `|g(W)|` in this family has ever been FD-verified**, and this item does not
  verify one — Arm A uses `|g|` purely as a step-sizing scalar. **The admissibility test divides
  by an unverified number. That circularity is structural to the cell and this item does not
  break it; Arm B is the only leg that could, and only if `FS-1` HITS.**
- **Nothing about the mechanism of the `|g(W)|` collapse.** Arm A measures the *behaviour*, not
  the *cause*. A linear transient-dilution model was already **refuted** by the three points on
  record (`RESULTS_W3.md` §6.6 item 3) and is not re-proposed.
- **The perturbed arms' series are still not on record at any window**, so `C_ENV` remains the
  **baseline** series' envelope constant.
- **The unsteady adjoint's memory at `W = 3,000` is NOT MEASURED.** `Q6` predicts; it does not
  report.

---

## 9. IF `FS-1` MISSES — WHAT THE LAB SHOULD CONSIDER NEXT, RECORDED AS OPTIONS AND NOT AS A PLAN

Registered here so a successor-to-the-successor does not restart from the beginning. **None of
these is proposed for compute by this draft, and none of them is a gate change.**

1. **A different objective.** `δ_window` is the window residual of a **time-averaged `CD`** on a
   limit cycle. An objective with a smaller window residual per unit sensitivity — e.g. a
   phase-locked or cycle-resolved functional — changes `C_ENV` and `|g|` **together**, and it is
   the only lever in the identity that has not been tried.
2. **A finer mesh or a smaller `Δt`.** `St ≈ 0.53` is a stated resolution artefact; the limit
   cycle's amplitude `A = 0.06581` sets `C_ENV`, and `C_ENV` is in the numerator of `h_min`. **A
   better-resolved cycle may have a different `A`. This is not measured and is not assumed.**
3. **A non-FD reference.** `DAFOAM_CHARTER.md` §2 second clause: *"where a complex-step or
   forward-AD reference is available, it is the reference"*, and the images on this box ship
   `libDASolverADF.so`, a forward-AD build, in all three tags
   (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §6a). **A forward-AD reference has no step size at all,
   so `h_min ≤ h_max` is not a question it has to answer.** §2 also requires that *"a record
   that reports only an FD table where a forward-AD or complex-step reference was reachable
   states that it did not reach for it, and why"* — **this lane states it: no lane in this family
   has reached for the forward-AD reference, and this is the first item whose failure mode makes
   that omission the live question rather than a footnote.** **This is the option this lane would
   put in front of the supervisor first**, and it is a proposal, not a decision.
4. **Recording the cell honestly.** If no lever works, `docs/capability/dafoam_GRID.md`'s
   2D · unsteady · incompressible cell keeps `gradients: CAN DO, CAVEATS — no admissible FD
   step` / `optimisation: CAN NOT DO`, with the **measured** reason attached: `W·|g(W)|` peaks
   near 1026 at `W ≈ 900` against a requirement of 1781.4. **That is an honest capability
   finding, and under the 2026-09-04 order a measured persistent failure of this class goes to
   Sanaa with the evidence — it is not laundered into a pass and it is not silently parked.**

---

## 10. FREEZE CHECKLIST — **NONE OF THIS IS DONE**

- [ ] §1's §2b condition **driven** and the reading recorded with its timestamp
- [ ] `w3s_grade.py`, `w3s_stage_and_run.sh`, `w3s_chain_driver.sh` written, with disclosed diffs against their unedited parents
- [ ] every planted-failure control re-driven, **both directions**, under `python3` and `python3 -O`, with the negative legs shown REFUSING
- [ ] §7's `_w_from_record` / `--gscan` binding read **as a diff** by the supervisor personally
- [ ] instrument md5s asserted against **committed HEAD blobs**, pins bumped in the same commit as the files they pin
- [ ] the document **committed**, and the sha recorded, **before any container starts**
- [ ] queue entry drafted with `cost_core_min_estimate`, `cap_core_min_registered`, `cost_basis`, `prereg_commit` — **and enqueueing is not authorisation**
