# SO-3D-R STAGE 1 — RESULTS

**Dated 2026-09-03.** Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor` (checks 1 and 4 discharged personally; first compute authorised by him).

**Pre-registration:** `PREREGISTRATION.md`, frozen v1.0 2026-09-03, ADDENDUM 1 (v1.0a) same day. **Grading path:** `so3dr_replay.py`, blob `55b918edf4f8246c79c7e631a3bd6864eb86ec52`, md5 `007328fe6777b23d6d81a1a7e8fedcd0` — **hashed against its committed blob in the launching invocation, before the reader was invoked, and the two matched** (`STATUS.SO3DR`, `G1 OK`).

**Toolchain row** (`DAFOAM_CHARTER.md` §6): every log replayed here was produced on the **PATCHED** row — `dafoam-idwarp-rot:v1`, digest `sha256:2927768a…`, `IDWARP_SO_MD5 85f59e87253e0a71a813f64ca6e4c425`. **There is no shipped row for the multipoint pathology and this rung does not manufacture one.**

**SUBMISSIONS PARKED.**

---

## 1. THE VERDICTS, AS THE READER EMITTED THEM

| gate | question | measured | threshold | **verdict** |
|---|---|---|---|---|
| **G-SO3D-P** | plant control | all three plants detected exactly as registered | — | **PASS** |
| **G-SO3D-1** | value channel or flag channel? | **0** non-finite tokens, in-scope **and** unrestricted, lines 1–264048 | P1: count == 0 | **PASS** |
| **G-SO3D-2** | dose-response in CL target | `r(cl04) = 0.882895`, `r(cl05) = 0.0`, `r(cl06) = 0.0` | P2: strict monotone increasing | **GATE FAIL** |
| **G-SO3D-3** | multipoint-specific vs case-specific | `min(r) = 0.0` | P3: `min(r) ≥ 0.1111` | **GATE FAIL** |
| **G-SO3D-4** | single-scenario poisoning of the sum | `665 / 673 = 0.988113` | P4: ≥ 0.90 | **PASS** |

**§8's null criterion did NOT trigger** (it requires G-SO3D-1 PASS **and** G-SO3D-2 GATE FAIL **and** G-SO3D-4 GATE FAIL; G-SO3D-4 passed). **§7 tension flagged in §5 below — the lane does not resolve it.**

Attribution was clean: **0 unattributed records**; **39 PRETRIM** records excluded **by name** (they precede the first design-vector block). 760 + 89 + 89 + 39 = **977**, the log's own primal count.

---

## 2. THE PLANT CONTROL — AND IT VINDICATES THE SUCCESSOR IN ITS OWN ARTIFACT

| plant | channel | signature | status |
|---|---|---|---|
| PLANT-A | value | census delta **+1**, at the planted line, field `CD` | **PASS** |
| PLANT-B | flag | record moves **`{ordinal 368: +1, ordinal 739: −1}`**, owners **`cl04` / `cl04`**, total 671 → 671 | **PASS** |
| PLANT-C | dose / classification | `R = 1.111224917e-05` → `1.111224917e-09`, **exactly one** record flipped failed→converged | **PASS** |

> **⚠ READ THE PLANT-B ROW BESIDE ITS OWN `per_scenario_moves` FIELD, WHICH IS `{cl04: 0, cl05: 0, cl06: 0}`.**
>
> This is precisely the configuration that made the predecessor's frozen predicate **degenerate**: both anchors owned by one scenario, so the per-scenario vector is all zeros — **byte-for-byte what a reader attributing nothing emits.** The successor scored the same bytes at the **record** level, named both owners, and returned a **non-degenerate PASS**. The reason SO-3D-R exists is demonstrated in SO-3D-R's own plant report, not merely argued in its pre-registration.

Each plant's status is a **fact on disk**: the report was written incrementally, so no pass here rests on an inference from control flow.

---

## 3. WHAT THE GATES SAY ABOUT THE MECHANISM

### 3.1 H1 STANDS — the failure is on the FLAG channel, not the value channel

**Zero non-finite numeric tokens** in the 264,048 lines before the IPOPT summary — and the **unrestricted** count is also **0**, so the in-scope whitelist made **no difference whatever** to this verdict. The concern registered against that whitelist in SO-3D's AMENDMENT 1 is retired by measurement: there was nothing for it to exclude.

**Consequence.** IPOPT's guard at `IpOrigIpoptNLP.cpp:487` is `success && IsFiniteNumber(ret)`, a conjunction whose failure is disjunctive. The value channel is clean, so the exception is being thrown on **`success == false`** — DAFoam's own boolean `primalFail`, propagated through mphys → OpenMDAO → pyOptSparse. **`Invalid number in NLP function or derivative` is IPOPT's wording for a failed-flag, not for a NaN.** §3 of the pre-registration predicted exactly this and predicted it **before the reader existed**.

**H6 (adjoint non-finite) is refuted on this evidence**: the census covered the sensitivity blocks and found nothing.

### 3.2 H2 IS REFUTED — and refuted in the OPPOSITE direction to the prediction

| scenario | CL target | primal starts | failure banners | rate |
|---|---|---|---|---|
| `cl04` | 0.4 | **760** | **671** | **88.29 %** |
| `cl05` | 0.5 | 89 | **0** | **0.00 %** |
| `cl06` | 0.6 | 89 | **0** | **0.00 %** |

**Every one of the 671 failures is in `cl04`, the LOWEST CL target.** `cl05` and `cl06` never failed once in 89 evaluations each. P2 predicted `r(cl04) < r(cl05) < r(cl06)`; the measurement is the reverse and is not close.

> **THE LANE'S OWN DISCLOSED CONTRARY DATUM WAS THE WHOLE STORY.** §2 A16 of SO-3D's freeze recorded, and flagged as betting against P2, that the single terminal failing primal inspected before the freeze reported `CL: 0.3953622816` — attributing to `cl04`. P2 was registered **against** that observation, on mechanism rather than on data, and the freeze said so in terms. **The observation won.** This is what pre-registration is for: the prediction was falsifiable, it was registered before the reader existed, and it was falsified.

**H2 (AoA/CL dose-response) is REFUTED.** The SIMPLE pressure equation does not stall preferentially at the higher trimmed angle; the failures are not dose-dependent in CL at all.

### 3.3 H5 IS STRONGLY SUPPORTED — 665 of 673 cutbacks follow EXACTLY ONE banner

`banner_count_distribution` = **`{1: 665, 0: 8}`**. Not one cutback in the run follows two or more failure banners. §4's registered reading: *"A dominant single-banner population is consistent with H5 and inconsistent with a global blow-up."* A 665/673 single-banner population is as dominant as the measurement can be.

**Read together with §3.2, the two give a coherent mechanism.** `cl04` is evaluated **760** times against 89 for each of the others. That asymmetry is not a property of the physics — it is what happens when the **first** scenario in the assembly fails, the trial is abandoned, and the remaining two scenarios are **never evaluated for that design point**. One scenario's boolean failure kills a trial that two healthy scenarios would have carried.

**The registered limit is respected: this does NOT prove the `om.ExecComp` propagation path.** §4 H5 states that is a code-read, not a log-read, and it remains **not done**.

### 3.4 H3 — GATE FAIL as emitted, and the gate could not express what it meant

`min(r) = 0.0 < 0.1111`. **P3 is refuted and the verdict is GATE FAIL. That verdict is not reinterpreted here.**

> **⚠ BUT THE GATE'S STRUCTURE IS A FINDING, AND IT IS REPORTED RATHER THAN USED TO SOFTEN THE VERDICT.** `min(r)` is zero **not because `cl05` and `cl06` are healthy at the multipoint condition, but because they are barely evaluated and never reached in a failing trial.** The gate was written to ask *"is the multipoint failure rate high relative to the single-point control?"* and it answers it with the minimum over three scenarios — a statistic that the aborted-trial mechanism drives to zero regardless of the answer. The datum the question wanted is beside it and is **not** a gate: `cl04` fails at **88.29 %** against the `D4` single-point control's **2.222 %** on the same base mesh, same solver, same image digest and identical `primalMinResTol` / `primalMinResTolDiff` — a **39.7×** elevation. **A reader may not take that ratio as a graded verdict: it was not the registered gate, and quoting it as one would be choosing the statistic after seeing the answer.** It is recorded so the supervisor can decide whether a successor gate is warranted.

### 3.5 H7 eliminated on the record; H4 remains unreachable

`Finding a feasible design using the Newton method` appears **exactly once** in **both** the D6R and D6 logs. The CL trim is an initial feasibility solve, not an inner loop. **H7 is eliminated**, and the count is on the record rather than in a paragraph.

**H4 (line-search mesh warp) is NOT DISCRIMINABLE by Stage 1**, exactly as §4 registered before the run: `Checking mesh quality` is printed only at setup, never per trial point. **Settling H4 requires the Stage-2 instrument and Stage 2 is not frozen.**

### 3.6 The controls, which is what makes any of the above specific

| log | starts | banners | rate |
|---|---|---|---|
| **D4** single-point control | 135 | 3 | **2.2222 %** |
| **D5** single-point control | 171 | 2 | **1.1696 %** |
| **D6** multipoint (killed at its container deadline) | 822 | 546 | 66.42 % |
| **D6R** multipoint, whole log | 977 | 671 | 68.68 % |

Every one of these re-derives the figure SO-3D's freeze declared in §2 A7–A10 **exactly** — 977/671, 822/546, 135/3, 171/2 — from an independent instrument. The pre-freeze declarations were sound.

---

## 4. NO REMEDY IS PROPOSED

§8 and §10 forbid it and nothing here proposes one: no tolerance change, no solver change, no `max_iter` change, no restart strategy, no multipoint reformulation. **Stage 2 and Stage 3 remain unfrozen.**

---

## 5. TWO THINGS THE LANE FOUND AND DOES NOT RULE ON

1. **§5's 2×2 and §8's null criterion disagree on this outcome.** §5 registers *"P2✗P3✗ ⇒ NULL, see §8"*, and the measurement is P2✗P3✗. But §8's operative criterion requires **G-SO3D-1 PASS and G-SO3D-2 GATE FAIL and G-SO3D-4 GATE FAIL**, and **G-SO3D-4 PASSED**, so `null_result.triggered` is **False**. The reader implemented §8 literally, and §5 points at §8 (*"see §8"*), so §8 governs on the plainest reading — **but the two clauses do not say the same thing and a reader should not have to notice that.** Reported for the supervisor's ruling; the lane does not resolve it and has not adjusted any verdict on account of it.
2. **G-SO3D-3's statistic, per §3.4.** Reported as a finding about the gate, not as a reason to move its verdict.

---

## 6. COST — RULE 12

| field | value |
|---|---|
| unit | core-minutes = wall s × ranks ÷ 60 |
| ranks | **1** — host post-processing; **no container, no MPI job, no OpenFOAM process** |
| **wall** | **4.277 s** [MEASURED, captured **inside** the detached wrapper] |
| **actual** | **0.0713 core-min** [MEASURED] — the reader's own internal clock recorded **0.0703**; the difference is the launcher's `git` hashing and interpreter start, and the larger figure is the one reported |
| registered point estimate | **6.0 core-min** (bracket 3–10), **carried forward unrevised from SO-3D** |
| **ratio actual/predicted** | **0.0119** |
| cap | **12.0 core-min — not approached** (0.59 % of it) |
| solver core-min | **0.000** of a **0.0** cap — honoured **by construction** |
| dollars | actual **$0.000061**, predicted $0.00513 — **DERIVED at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** |
| waste | the aborted 21:18:12Z launch attempt, **~0 core-min**, named in ADDENDUM 1 and **not** absorbed into the ratio |

**Gap attribution: MISPREDICTION, and now measured on a COMPLETE pass.** SO-3D's row could only report a floor, because it aborted at the plant control. **This row is the honest one**: the full pipeline — four logs, the census, the attribution, the coupling, the three plant passes over a 264,607-line log and both JSON writes — completed in **4.277 s**. The registration costed the work as I/O-bound line counting and over-predicted by **~84×** against the point estimate. **Not contention**: the box was heavily loaded and this run took four seconds of it.

---

## 7. WHAT THIS ITEM DOES NOT CLAIM

**It computes no gradient, no FD table, no adjoint and no GCI, and quotes none.** It establishes nothing about the shipped toolchain — every log is on the patched row. It does not prove the `om.ExecComp` propagation path (§3.3), does not settle H4 (§3.5), and does not reopen SO-3D's `NOT A RESULT`, which stands as SO-3D's verdict.
