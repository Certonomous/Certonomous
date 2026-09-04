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

### 6.6 **THE CUMULATIVE ITEM CEILING — A GAP IN §6 AS DRAFTED, CLOSED HERE**

**Added 2026-09-04 by a dafoam `lab-lane`, BEFORE first compute, and stating the condition
per `CLAUDE.md` rule 2: the Arm A run root `CURRICULUM-D12R2W3S-GSCAN-cylinder-unsteady`
does not exist and the arm has not run.** §6.1 registers an **arm** cap and no **item**
ceiling and no **per-leg** caps, so nothing compares anything to anything **between** legs.
That is the shape `SO3aF2` ran 3.15 % past, and **only 2 of 40 chain drivers in this family
guard theirs.** Registered now:

| leg | predicted (§6.1) | **registered cap** |
|---|---|---|
| setup (`S0`+`S1a`+`S1b`+`S2a`) | 1.75 | **5.0** |
| `A0` `S5` repeat, `W = 2,000` | 66.78 | **100.0** |
| `A1` `S5`, `W = 1,400` | 46.34 | **70.0** |
| `A2` `S5`, `W = 3,000` | 100.84 | **155.0** |
| **sum** | 215.71 | **330.0 = `ITEM_CEILING_CORE_MIN`, EXACTLY `CAP_CORE_MIN_A`** |

**The sum being exact is checked by the guard, not assumed** — a registration whose parts
exceed its whole aborts `rc=64` before any leg runs. Before **every** leg the guard reads
spend to date from the ledger, adds **that leg's** cap, and refuses if the projection clears
the ceiling: **an overrun stops the run, it does not get a new budget.** Spend is summed
**across roots**, because a per-arm cap cannot see an item walking past its ceiling one arm
at a time.

**AND THE READER IS NOT PORTED FROM `d6rf`, WHICH FAILS OPEN.** Measured at
`d6rf_chain_driver.sh:129-141`: `except IOError: pass` returns **`0.0`** for a missing or
unreadable ledger — a planted zero in the guard's own input — and its `[0-9.]+` matches
`1.2` out of a malformed `core_min=1.2.3` while the resulting `ValueError` is **not caught
at all**, so `$SPENT` returns empty, the projection comparison fails and **the `if`
evaluates false**. `a1wrt_run_unit.sh:297-305` is the **primary**: it refuses on an
`UNMEASURED` prior spend rather than assuming zero. The reader here is written fresh inside
the AST-audited instrument, returns **`UNMEASURED` and never `0.0`** on any read or parse
failure, and adds three limbs neither parent has — a root that exists with stage logs and
**no** ledger is `UNMEASURED`; a ledger with **zero** spend rows beside stage logs is
`UNMEASURED`; the caps are checked to fit the ceiling. **The genuinely fresh case is kept
separate**: no root *and* no ledger is `0.000`, because a blanket refusal on an absent
ledger makes a first leg unlaunchable forever. All six branches are driven, plus the
reader's own **planted non-zero** (`GA-P3`) — a spend reader that silently returns zero
reports **full headroom**.

---

## 7. INSTRUMENTS — TO BE BUILT AND FROZEN BY MD5 AT THE FREEZE COMMIT. **NONE EXISTS YET.**

**No instrument in this table has been written.** Listed so the freeze knows what it must pin,
and so the drafting cost is visible rather than discovered later. All drafting is **zero
compute**.

> **STATUS UPDATE 2026-09-04, by a dafoam `lab-lane`.** Three of the five rows below now
> exist and are driven; the launcher does not. **Nothing is frozen and nothing has been
> queued.** `w3s_grade.py` does not COPY any parent gate — it **imports the frozen parent
> after checking its md5** and calls `g0_completion` and `_w_from_record` directly, so the
> "every existing gate function byte-identical" assertion is discharged by construction
> rather than by a diff a reader must trust.

| file | derived from | what changes |
|---|---|---|
| `w3s_grade.py` **WRITTEN, md5 `d24d632cd37f587ebaca7999d9088dec`** | `d12y_grade_w3.py` (`3950d30fd09c9b56213a02f5e9864e20`, **UNEDITED**), **imported, not copied** | a `--gscan` mode reading `\|g(W)\|` per leg from a multi-leg manifest and grading `W·\|g\|` against the DERIVED bar (never a typed product); the three-deep structural bar on `admissible` (§7a); `--cumulative-item-ceiling` (§6.6); `--selftest` 50/50, `--selftest-narrowing` 30/30, `--olimb` 5 mutants caught under **both** `python3` and `python3 -O`, `--assert-audit` **0 whole-file and 0 outside the selftests**. |
| `w3s_chain_driver.sh` **WRITTEN**, pins bumped in the same commit | `d6rf_chain_driver.sh`, `a1wrt_run_unit.sh` | the cumulative item-ceiling guard (§6.6) and **PREFLIGHT 0**, which aborts `rc=70 NOT_FROZEN` while `PREREG_COMMIT` is empty. **The driver is INERT today and its `--selfcheck` proves it, 10/10.** |
| `w3s_grade_NARROWING.diff` **WRITTEN** | — | the `--gscan` binding extracted beside the inherited `_w_from_record` for the supervisor's §3-check-1 read. **The diff is not the proof**; `--selftest-narrowing` is. |
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

### 7a. **THE BINDING AS BUILT, AND THE ONE CLAIM ABOVE THAT IS NOT SATISFIABLE**

**Added 2026-09-04 by a dafoam `lab-lane`. The paragraph above stands as written and is
not rewritten; this section records what could and could not be built to it.**

**THE UNSATISFIABLE CLAIM, NAMED.** "Strictly more constrained than the inherited gate"
cannot mean *`--gscan` refuses everything the inherited gate refuses*, because the
inherited gate refuses **Arm A's own manifest** — that refusal is the whole reason this
item needs a successor — and a `--gscan` that also refused it would grade nothing. Any
freeze resting on the literal sentence would be resting on a proposition that is false by
construction. **The narrowing is therefore stated over two disjoint domains, and BOTH
halves are DRIVEN against the frozen parent's own function**, imported from disk after its
md5 is checked, never re-implemented:

| direction | claim | driven |
|---|---|---|
| **D1** | On **window-homogeneous** row sets — the entire domain the inherited gate governs — `--gscan` **REFUSES EVERYTHING**, the parent's accepts included. Not a superset of its refusals: the whole domain. | 11 inputs; the parent **ACCEPTED 5**, `--gscan` accepted **0**. The vacuity guard is itself a unit: a direction in which the parent accepted nothing would prove nothing. |
| **D2** | Off that domain, the parent's **five structural limbs still run, per leg** (row carries `W`; `W` parses; the leg agrees on one `W`; the ledger carries exactly one line for the leg; the ledger agrees). | 5 mutations, each run through **both** gates; both refuse. Two positive controls first, so the battery is not a battery of refusals. |
| **D3** | `--gscan` adds **seven** refusals the parent cannot express: no `leg` key, unregistered `leg`, **leg/W mislabel**, missing leg, extra leg, duplicate `S5` in a leg, per-leg ledger line absent / doubled / disagreeing. | 8 units, each paired with the parent **ACCEPTING the same defect once relabelled** — which is what makes each an *added* constraint and not a renamed one. |
| **D4** | The absent-ledger branch is the parent's own L-342 reasoning and does **not** become a way to lose the windows. | 2 units; with the ledger absent a leg at `W = 1399` is **still refused**, because the window is checked against a typed constant. |

**THE SHARPEST SINGLE UNIT, and the reason the leg pin exists.** Legs `A1` and `A2` with
their windows **SWAPPED** — every leg present, every leg internally homogeneous, the ledger
agreeing with the rows — is `W2R-GRADER-DEF-1` wearing a leg name: the wrong window graded
under the right label. The parent's single `W_PRIMARY` constant cannot see it. **`--gscan`
refuses it, and that unit is what the `--olimb` narrowing mutant breaks.**

**A MEASURED PROPERTY WORTH THE SUPERVISOR'S ATTENTION, because it looks like a hole and is
not.** The leg-set closure is **over-determined by three limbs** — `N2` gives
⊆ `LEG_NAMES`, `N4` gives equality, the per-leg zero-rows refusal gives ⊇ — so **deleting
any one of the three is masked by the other two**. That was found by trying to build a
mutant for it and watching the mutant survive. It is a good property of the binding and it
is why the `--olimb` mutant targets **N3**, the per-leg registered-window pin, which is the
only limb in the binding nothing else covers.

**ARM A'S STRUCTURAL BAR ON `admissible: true` IS THREE-DEEP**, per §3.1:
**BAR-1** the sizing entry point for gscan data raises, always;
**BAR-2** `--plan`/`--plan2`/`--plan3` on a gscan manifest refuses **before any gate runs**;
**BAR-3** the emitted object is walked and refused if `admissible`, `steps`, `h_min`,
`h_star` or `step_plan` carries anything but the registered refusal string — **nested at any
depth**. BAR-3 is the limb that survives a future edit, because a re-introduced step plan
has to travel through the emitted object to reach a reader. All three are driven.

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

---

## 11. **CORRECTIONS TO §0 AND §6, MEASURED FROM THE ARTEFACTS BEFORE THE FREEZE**

**Added 2026-09-04 by a dafoam `lab-lane`. Every number below was read from the file named
beside it. §0 is NOT rewritten — it is unfrozen, but a table that is corrected in place
leaves no record of what was believed.**

**C-1 — §0's `h_min,env` COLUMN CITES ARTEFACTS THAT DO NOT CARRY THOSE NUMBERS.** The
column is an **envelope recomputation** under W3-A1, not a reading. What the three
`step_plan.json` files actually carry:

| `W` | `h_min` **in the artefact** | `delta_eff` **in the artefact** | §0's `h_min,env` |
|---|---|---|---|
| 300 | **0.1742837908900481** | **0.0017958478225974517** | 0.288136 |
| 900 | **0.15755327829116114** | **0.0017958478225974517** | 0.086825 |
| 2,000 | **0.0911930188193242** | 0.00044535 | 0.091193 ✓ |

Only the `W = 2,000` row matches its own artefact. **Either the column is relabelled as a
recomputation or the numbers are replaced by the artefacts' own — the freeze may not carry
it as it stands.**

**C-2 — THE `W = 300` AND `W = 900` ROOTS CARRY THE SAME `delta_eff`, TO THE LAST DIGIT.**
That is not a coincidence: `W2R` was graded under `W2R-GRADER-DEF-1`, where the comparator
passed the literal `W_PRIMARY = 300` while the launcher ran `W = 900`. **The `W = 900`
root's `delta_eff` is the `W = 300` window's.** Consequences, stated separately because they
differ: **`|g(900)| = 1.1398352621255485` is unaffected** — it is the adjoint's own output —
so §0's `W·|g|` column and `FS-1` survive intact. **Every `delta_eff`-derived quantity at
`W = 900` does not**, including that row's `h_min`.

**C-3 — THE PRIORS' WINDOWS ARE CORROBORATED FROM THEIR LEDGERS, NOT THEIR STEP PLANS.**
Both prior `step_plan.json` files carry **no `W` key and no `C_ENV`** — they predate W3-A1
and W3-A2. Their ledgers each carry **exactly one** `W_STEPS=` line (`300` and `900`,
measured), so the cross-read is available but only from there. **The comparator reads the
priors' windows from the ledgers and refuses on disagreement**; where a prior ledger is
absent the cross-read is recorded `NOT MEASURED` (INFRASTRUCTURE, L-342) rather than waived
silently.

**C-4 — `|g(W)|` IS COMPONENT 0, NOT A NORM, AND THE ADMISSIBILITY TEST IS COMPONENT-0-ONLY
WHILE `G12R-6` GRADES ALL FOUR.** Inherited from `d12y_grade_w3.py:2543`
(`g_comp = float(s5["dobj_dshape"][0])`) and coherent — the sweep `S6_s{k}` perturbs index 0,
so the plateau and the sizing are on the same component. But at `W = 2,000` the gradient is
`[0.48836, 0.42401, 0.23027, −1.14264]`, and the same `delta_eff` gives:

| component | `\|g_i\|` | `h_min = 100·C_ENV/(W·\|g_i\|)` | vs `h_max = 0.05` |
|---|---|---|---|
| 0 (**the registered sizing component**) | 0.48836 | **0.091193** | 1.82× over |
| 1 | 0.42401 | 0.105032 | 2.10× over |
| 2 | 0.23027 | 0.193403 | 3.87× over |
| 3 | 1.14264 | **0.038975** | **inside** |

**THIS IS FLAGGED AND IS NOT PROPOSED AS A REPAIR, AND THE REASON IS THE RULE ITSELF.**
Moving the sizing component to the largest would **manufacture admissibility by changing the
instrument after seeing the answer** — Sanaa's T25 ruling (*no widening on optimism*) and the
2026-09-04 order (*"it never means adjusting the gate until the answer fits"*). Moving it to
the **weakest** component (2) would be a tightening and would make the miss worse. **The
honest statement is the structural one: the step is sized on one component and the bright
line is then taken at that step on all four, so component 2's noise budget at `h*` is ~2.1×
the registered 1 %. That is an inherited property of the D12R2 gate, not a W3S choice, and
it is the supervisor's call whether it belongs on Sanaa's desk beside the window finding.**

**C-5 — THE SUPERVISOR'S OWN FACTORS CHECK OUT.** `delta_eff` fell **4.0324×**
(0.0017958478225974517 → 0.00044535), `|g|` fell **2.1100×**, `h_min` improved **1.9112×**
(0.174284 → 0.091193) and is **1.8239×** short of `h_max`. All four reproduce from the
artefacts. **It is the draft's §0 table, not the supervisor's reading, that does not.**
