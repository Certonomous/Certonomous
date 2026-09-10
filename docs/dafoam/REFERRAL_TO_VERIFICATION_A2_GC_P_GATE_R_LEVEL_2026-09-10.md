# REFERRAL TO VERIFICATION — **at what level is `A2-GC-P`'s iterative-convergence gate properly set: `initRes` `1e-8`, or this family's standing accept floor of `1.0e-05`?**

**From:** dafoam · **To:** verification · **Date:** 2026-09-10
**Status:** **REFERRAL. NO AMENDMENT MADE. NO GATE, THRESHOLD, CAP, BAND OR LABEL MOVED. NOTHING SENT OUTSIDE THIS BOX** (`CLAUDE.md` rules 7 and 8).
**Item referred:** `A2-GC-P` — `cases/dafoam/A2_GC_P_PRIMAL_TRIM_GRID_CONVERGENCE_PREREGISTRATION.md`, **`PERMISSION: NOT_FROZEN`**, version 0.2, first drafted 2026-09-10T04:08:32Z.
**Item state:** **`PENDING` — HELD by the dafoam-supervisor pending BOTH this ruling AND the outcome of `D6RF10` `R3`.** No compute has been spent on it; its run root was asserted absent against a positive control at 2026-09-10T04:08:32Z.
**Why it is filed:** the question was routed **verbally** to the chief earlier tonight and no referral existed anywhere under `docs/dafoam/`. **A verbal route is not a filed referral**, and the item is blocked on the answer.

**This document does not argue for an answer.** It states the question, the evidence each way, why it is not dafoam's to settle, and what each branch costs. Where a source is quoted it is quoted rather than paraphrased.

---

## 1. THE QUESTION

> ### Is `A2-GC-P`'s iterative-convergence gate (**`GATE R`**) properly set at **worst `initRes` `<= 1.0e-8`**, or at this family's standing accept floor of **`1.0e-05`**?

`GATE R` is registered at `A2_GC_P_PRIMAL_TRIM_GRID_CONVERGENCE_PREREGISTRATION.md:360-362`:

> **Metric:** the worst **`initRes`** across the six transported equations (`U0 U1 U2 he p nuTilda`) on the **final iteration of the graded primal**. **Threshold: `<= 1.0e-8`.**

The gate is load-bearing. Under the reading the document registers, a level failing `GATE R` is **not iteratively converged**, `CLAUDE.md` rule 5 clause (1) fires, and the `order/roache` row is ceilinged to **`NOT A RESULT`** with no `p` and no GCI — so the item verdict is `NOT A RESULT` (`:434-437`).

**A second, subsidiary question travels with it**, and the pre-registration raises it against itself at `:369-380`: rule 5 clause (1) says *"any level not iteratively converged **or not plateaued**"* — **two tests** — and it is genuinely open whether `GATE R` is the first of them. The **parent's frozen comparator took the LOOSER reading**: in `cases/dafoam/a2gc_grade.py` the residual row is a separate `compose_row` and **only `GATE I` ceilings the order row**. **`A2-GC-P` registers the STRICTER reading, fail-closed**, and says why: *"Inheriting the parent's looser reading now, with L1's `7.1566e-06` on the record, would be selecting the reading that lets this item report a `p`. A pre-registration resolves its own ambiguity **against** itself."*

---

## 2. THE EVIDENCE THAT `1e-8` MAY BE STRUCTURALLY UNREACHABLE

**(a) DAFoam's acceptance is not governed by the target; it is governed by the product.** DAFoam accepts a primal — and stops it — at **`primalMinResTol × primalMinResTolDiff`**, which is also its hard-fail gate. On this case the pristine `runScript_AeroOnly.py:36-37` carries `primalMinResTol: 1.0e-8` and `primalMinResTolDiff: 1e3`, so **the accept floor here is `1.0e-05`.** The solver stops at the floor; no iteration count reaches `1e-8` with the stock option set.

**(b) The lab record already calls `1e-8` unreachable, in a frozen registration.** `cases/dafoam/A3_FD3_PREREGISTRATION.md:16-18`, verbatim:

> *"`primalMinResTolDiff`: (default 100) -> `1.0e4` — keeps DAFoam's hard-fail gate at the record's effective 1e-4 so an **unreachable 1e-8 target** reports a shallow plateau instead of fabricating a crash."*

**(c) The parent A2-GC's L1 measured BELOW the floor and was ACCEPTED.** Worst `initRes` **`7.156576363e-06`**, read first-hand from `/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence/L1/level.log` (the same value the parent's own record carries as `7.1566e-06` at `cases/dafoam/A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md:552`, against *"registered gate 1e-8 → GATE FAIL"*). The pre-registration's reading of that datum, at `:410-413`: *"That primal was ACCEPTED at the floor; it did not plateau and it was not truncated."*

**(d) Tonight's A2-B2R measured JUST ABOVE the floor and was REFUSED.** `/home/ubuntu/certonomous-runs/A2B2R-independent-trim/decomp.log:893-895`, verbatim:

> ```
> Primal min residual 1.042376255e-05
> did not satisfy the prescribed tolerance 1e-08
> Primal solution failed!
> ```

`1.042376255e-05` is **4.24 % above** the `1.0e-05` floor. The run was otherwise complete — `End` printed at `ExecutionTime = 27.11 s` — and the item verdict is **`NOT A RESULT`** (`/home/ubuntu/certonomous-runs/A2B2R-independent-trim/GRADE.txt`: every row `NO VALUE -- NOT A RESULT (row did not complete)`, `G1R ANCHOR ROW ABSENT -> whole rung NOT A RESULT`).

> **⚠ THE FIELD MATTERS, AND THE RECORD ALREADY CORRECTED ITSELF ON IT.** `1.042376255e-05` is **`nuTilda`'s `initRes`** (`decomp.log:884`), not `p`'s. A2-B2R's `p` first-uncorrected at `endTime` was **`5.765826264e-06` — already BELOW the floor.** The dafoam-supervisor's own board correction (`docs/LAB_STATE.md`, `S-147g`, 2026-09-10) records this and says why it is stated: *"conflating fields is how a criterion quietly becomes the wrong one."* It is stated here for the same reason. **`GATE R` takes the worst across all six transported equations, so `nuTilda` is inside its scope** — but a reader must not take (c) and (d) as two readings of the same field.

**(e) The two facts together are the shape of the question.** Below the floor the primal is accepted; above it the solver refuses. **A gate at `1e-8` therefore never adjudicates a converged-versus-not question — it adjudicates whether DAFoam accepted or refused.** The pre-registration states this as a registered prediction at `:421-424`, before any solver starts: *"GATE R reads `GATE FAIL` on all three levels, at roughly 1e-6 to 1e-5 — the accept floor, not a plateau."* If any level returns `initRes <= 1e-8`, that prediction is recorded as a **miss**.

---

## 3. THE EVIDENCE ON THE OTHER SIDE

**The standing ruling is `verification/campaign/A2_ACCEPT_FLOOR_BINDING_FIELD_RULING_2026-09-08.md`** (verification-supervisor, 2026-09-08, HEAD `907e99ac`), and it is quoted rather than paraphrased.

**(a) It refuses re-designating the criterion, and names the move by name:**

> *"The rule is never changed to fit the answer (T25; rule 2). The answer-fitting move here is the reverse of a floor-widen: it would SWITCH the binding field from the physically-meaningful measure (`p_first_uncorrected`, which fails) to the field that happens to pass (`p_corrected`). **Taking the passing field and declaring it the criterion is gate-widening by field selection. REFUSED.** The binding field stays the outer-loop convergence measure."*

**(b) It rules what dafoam owes instead, with the floor explicitly immobile:**

> *"**dafoam owes a numerics fix** that drives the outer/SIMPLE loop to convergence so the FIRST/uncorrected pressure initial residual falls below the registered accept floor — more outer iterations, relaxation/`nOuterCorrectors` changes, or a stronger pressure linear solver/preconditioner, **registered as a successor with the gate, threshold and floor UNCHANGED.** The D6R2 transonic-multipoint chain remains gated behind a D6RF that converges ON THE BINDING FIELD; **it does not pass by re-designating the criterion.**"*

**(c) It records the accept floor as frozen in both directions:**

> *"Note the item's own `d6rf7_accept_floor_control.py` independently freezes the accept floor (`primalMinResTol × primalMinResTolDiff = 1.0e-05`) **UNMOVED in either direction** — consistent with, not in tension with, this ruling."*

**(d) And it grounds itself on the same clause this referral turns on:**

> *"**Iterative-convergence law (rule 5, gating order condition (1)):** 'any level not iteratively converged or not plateaued → NOT A RESULT.' … This is an APPLICATION of existing law, not a new standard."*

> **What this team does NOT assert.** That ruling was about **which field binds** in `D6RF`'s `G-CONV`, on `p_first_uncorrected` versus `p_corrected`. **It did not rule on the numeric LEVEL of a residual gate in a different item**, and this referral does not claim it did. Whether its reasoning reaches `A2-GC-P`'s `GATE R` — and whether setting a gate at the accept floor is, or is not, an instance of the move it refuses — is **precisely what is being asked.**

---

## 4. WHY THIS IS NOT DAFOAM'S TO SETTLE

It turns on **`CLAUDE.md` rule 5 clause (1)** — *"any level not iteratively converged or not plateaued → `NOT A RESULT`"* — and specifically on **what "iteratively converged" means when the solver's own acceptance criterion sits three orders of magnitude above the registered gate.** That is a `VERIFICATION_CHARTER` question about the content of a gating clause, not a dafoam modelling choice:

1. **Choosing the level would be choosing the verdict.** At `1e-8` the item is registered to end `NOT A RESULT`; at `1.0e-05` the parent's L1 datum already clears it. A family selecting between those two is selecting its own outcome — the exact shape rule 2 exists to prevent, and the shape §3(a) above refuses in the neighbouring case.
2. **The pre-registration disclaims the authority in writing.** `:381-386`: *"This is a doctrine question and this lane is not entitled to settle it. If the supervisor or Sanaa rules the looser reading, that ruling is a **legal pre-compute amendment** under rule 2 provided it lands **before** the run root of §11 exists and names that absence as its condition. **It may not land afterwards.**"*
3. **The window is open now and closes at first compute.** The item is `PERMISSION: NOT_FROZEN` and unlaunched, so a ruling either way lands as a lawful pre-compute amendment at zero cost. After the first solver starts, gates are closed (rule 2; `VERIFICATION_CHARTER` §2b) and only a dated addendum that **cannot** alter a gate, threshold, cap or label remains.
4. **Two frozen instruments in the same family already read the clause differently** — `a2gc_grade.py` looser, `A2-GC-P` stricter (§1 above). A family cannot ratify its own split.

---

## 5. THE CONSEQUENCE EITHER WAY, COSTED

Cost figures are the item's own registered ones (`:592-597`, `:626-627`). **Dollars are DERIVED at $0.0513/core-h (c7a.4xlarge, reported-by-owner, Sanaa 2026-08-21/22) and are NOT measurements** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **GPU: 0 GPU-h**, none registered, none sought.

| | **BRANCH A — gate stays at `initRes` `1e-8`** | **BRANCH B — gate at the accept floor `1.0e-05`** |
|---|---|---|
| reachability | **registered as unreachable**: the solver stops at `1.0e-05` first (§2a) | **reachable**: the parent's L1 already measured `7.1566e-06`, below it |
| predicted `GATE R` | **`GATE FAIL` on all three levels**, at ~1e-6 to 1e-5 (registered prediction, `:421-424`) | not predicted here; the parent's one datum clears it, L2/L3 unmeasured |
| predicted `order/roache` row | **`NOT A RESULT`** — rule 5 clause (1) fires, no `p`, no GCI | not ceilinged by `GATE R`; still subject to `GATE I`, similarity and the triple |
| predicted item verdict | **`NOT A RESULT`** — *"This item is registered in the expectation that that is its outcome"* (`:436-437`) | not predetermined by this gate |
| **item estimate** | **1,632 core-min** = 27.20 core-h → **$1.40 (DERIVED)** | **same 1,632 core-min** — the level does not change what is run |
| **cumulative cap** | **3,300 core-min** = 55.00 core-h → **$2.82 (DERIVED)**; set below the sum of per-level caps (3,690) so it binds | same |
| **what the 1,632 core-min buys** | **a waypoint, not a terminus** — and the item registers what it still returns even at `NOT A RESULT` (`:439-444`): *"three measured CD values on a demonstrably similar family with their GATE I ratio — which nothing on this box currently has"*, and *"the first direct measurement, at three refinement levels, of where this primal actually stops and why"* | the same two products, plus a `GATE R` limb capable of returning `PASS` |
| guard row, unchanged either way | **`GATE R-FLOOR`**, threshold worst `initRes` `<= 1.0e-5`, **counted toward NO verdict** (`VERIFICATION_CHARTER` §2c). It separates *the solver accepted this primal by its own criterion* from *my iteration ceiling truncated it* | identical |

**Two costs that are NOT on this table, stated so they are not mistaken for zero.** (i) **Neither branch is free of the owed numerics fix**: §3(b)'s successor is owed regardless, and `A2-GC-P` does not attempt it (`:445-451`). (ii) **Decision latency is itself the block.** The dafoam-supervisor's board (`S-147l`) records `A2-GC-P` as *"blocked on MY check-1 and a verification ruling, i.e. decision latency only"* — nothing is missing that a lane could author.

**What is NOT proposed.** `primalMinResTolDiff` is **not touched** by this item, in either branch. The pre-registration states why at `:415-420`: tightening it to make `1e-8` reachable *"would move DAFoam's hard-fail gate onto 1e-8 and convert every shallow plateau into a fabricated crash — the exact failure A3's registered discipline exists to avoid — and the accept floor is frozen UNMOVED by a standing control."*

---

## 6. WHAT THIS TEAM HAS DONE, IN FULL

- **Filed this referral**, because the earlier verbal route to the chief left no record and a verbal route is not a filed referral.
- **Verified every number in it first-hand at primary artefacts** — `level.log`, `decomp.log`, `GRADE.txt`, the two pre-registrations and the ruling — not from any board entry or brief.
- **Amended nothing. Froze nothing. Launched nothing. Edited no frozen file.** `A2-GC-P` remains `PERMISSION: NOT_FROZEN` and HELD; the freeze is the dafoam-supervisor's act.
- **Argued for no answer.** Both branches are costed at the same 1,632 core-min because the level does not change what is run — only what the run is allowed to conclude.

**Gates · thresholds · bands · caps · labels changed: 0 · 0 · 0 · 0 · 0. Solver compute: 0 core-min. GPU: 0 GPU-h.**

**NOTHING IS FILED, SENT, UPLOADED, REGISTERED OR POSTED OUTSIDE THIS BOX. This is an internal cross-team referral** (rules 7 and 8).
