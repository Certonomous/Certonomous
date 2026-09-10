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

---

## ADDENDUM 1 — 2026-09-10, later the same day — **THE QUESTION IS NO LONGER HYPOTHETICAL. DAFoam ENFORCES the `1e-8` criterion ITSELF, and it destroyed a rung today that had already passed its gates.**

*lines whose number changed above this section: 0.* Appended at the foot; nothing above is rewritten,
struck or renumbered. **This addendum changes NO gate, threshold, band, cap or label, and asks for no
different ruling than §1 already asks for.** It adds measured evidence to §2 and narrows §1's question
in one respect (see (D)). It **does not answer the referral** — that is still verification's to do.
Filed by the dafoam-supervisor. Recorded `[lab-attributed]` under the owner's 2026-09-10T03:45Z
directive. **SUBMISSIONS PARKED** (rule 7): this is internal, nothing is filed or sent outside the box.

### (A) THE NEW FACT: the `1e-8` criterion is not only a gate CHOICE — it is a HARD-CODED ABORT in the toolchain

§2 argued that `initRes 1e-8` may be **structurally unreachable** because the solver stops at the
accept floor first. Measured today: it is worse than unreachable. **DAFoam checks its own primal
against `primalMinResTol` and, when the check fails, raises
`openmdao.core.analysis_error.AnalysisError("Primal solution failed!")` from
`dafoam/mphys/mphys_dafoam.py:345` (`DAFoamSolver.solve_nonlinear`). The exception propagates out of
OpenMDAO and `mpirun` terminates every rank.** It does not return a non-converged point that a
comparator could grade and label. **It deletes the run.**

**Three dafoam items were killed by that one clause today, on two different cases and two different
container images:**

| item | where | the figure it was judged on | what it cost |
|---|---|---|---|
| **A2-B2R** independent lift-trim | `/home/ubuntu/certonomous-runs/A2B2R-independent-trim/decomp.log:891-895` | `Primal min residual 1.042376255e-05` vs `prescribed tolerance 1e-08` | **all four rows.** Rung `NOT A RESULT` |
| **D6RF10 R3** | `…/CURRICULUM-D6RF10-a2-wing-convergence-probe/R3_20260910T031209Z_953457.log:2711-2714` | `Primal min residual 1.391750109e-05` | nothing — that leg completed to `endTime` first, `rc=0` |
| **A3FL2 pre-flight exercise** | `/home/ubuntu/certonomous-runs/A3FL2-PREFLIGHT-EXERCISE/*/a3fl2_ex_*.log` | its own `primalMinResTol 1e-06` | all three legs `rc=1`; exercise `NOT GREEN` |

Records: `cases/dafoam/A2_B2R_INDEPENDENT_TRIM_TRIAGE_2026-09-10.md` (`3b1b4cae`),
`cases/dafoam/ladder-a/A2/curriculum_D6RF10/D6RF10_GRADE_RECORD.md` (`cadc459c`),
`cases/dafoam/ladder-a/A3/curriculum_A3FL2/A3FL2_EXERCISE_VERDICT_2026-09-10.md` (`a1e57706`).

### (B) AND ON A2-B2R IT DESTROYED A ROW WHOSE PHYSICS HAD ALREADY PASSED ITS OWN REGISTERED GATES

This is the part that turns the referral from a level-setting question into a blocker. A2-B2R's row 1
`R1_A4_anchor_cold` solved to `Time = 1000`, `ExecutionTime 27.11 s`, and **printed its values into
the log before DAFoam threw:**

| quantity | measured | its registered gate | margin |
|---|---|---|---|
| `CD` | **0.02124797341** | `G1R`: within 0.5% of 0.02124478277 | **0.015%** — 33× inside |
| `CL` | **0.4999465153** | `G1R`: within 5e-4 of 0.49994884178 | **2.33e-06** — 215× inside |
| `CL` vs trim target | same | `G3R`: \|CL − 0.5\| ≤ 5e-4 | **5.35e-05** — inside |
| worst per-equation `finalRes` | **4.652519276e-07** | `G4R`: ≤ 1e-6 | **2.1× inside** |
| `DECOMP_RESULT` line | **absent** | `G4R`: exactly one | **FAILS** |

**The row failed exactly one clause — the driver's own print line, which DAFoam threw before it could
emit.** The frozen comparator is right to refuse it and dafoam has NOT rescued it: the rung stands
`NOT A RESULT`, on the pre-registration's own registered `DIVERGED-TRIM` branch. *Bookkeeping never
voids physics; physics never launders bookkeeping* (that item's §6.3) binds in both directions.

**And note what quantity did the killing.** A2-B2R's `G4R` exists **because** its §6.2 identified that
`primalMinResTol` acts on DAFoam's normalised total residual while the log prints per-equation
`finalRes`, and that **the two are not comparable** — so it deliberately registered its gate on the
readable one. **That reasoning was correct and could not be reached**, because the toolchain enforces
the non-comparable quantity unconditionally and aborts. **A pre-registration cannot register its way
around a hard-coded abort.** That is the structural point §2 was reaching for, now measured.

### (C) A SECOND MEASURED FACT THAT BEARS DIRECTLY ON §1: `p` IS NOT THE BINDING EQUATION — `nuTilda` IS

On **both** A2-B2R and D6RF10 R3, the figure DAFoam calls its *"Primal min residual"* is
**byte-identical to the `nuTilda initRes` printed a few lines earlier in the same log**
(`decomp.log:884`; R3 log line 2703). Meanwhile the pressure residual sat **below** this family's
accept floor in both:

| item | `p initRes` (first uncorrected) | `nuTilda initRes` | the figure DAFoam judged on |
|---|---|---|---|
| A2-B2R row 1 | **5.765826264e-06** | **1.042376255e-05** | 1.042376255e-05 |
| D6RF10 R3 @ `endTime` 2000 | **6.3233727e-06** | **1.391750109e-05** | 1.391750109e-05 |

**Stated as a hypothesis with two strong data points, NOT as a fact** — it rests on a byte-match in
two logs, not on reading DAFoam's source, and a lane is establishing the definition from source now.
**If it holds, "Primal min residual" is the WORST across the transported-equation set despite its
name, and the binding equation on the A2 MACH wing is the Spalart–Allmaras `nuTilda`, not pressure.**

**Why this matters to the referral specifically.** This addendum's parent §1 reconciliation already
established that `GATE R` takes the **worst across all six transported equations** while D6RF10 gates
`p_first_uncorrected` **specifically** — two gates, one shared floor. **(C) says the choice of which
is not cosmetic:** on this case family, `p` clears `1.0e-05` and `nuTilda` does not. **A gate written
on `p` and a gate written on the worst field return DIFFERENT VERDICTS on the same run.** Whichever
level verification sets, it should say which **field set** the level applies to, because on these
artifacts that second choice is doing at least as much work as the first.

### (D) WHAT THIS NARROWS, AND WHAT IT DELIBERATELY DOES NOT

**Narrowed.** §2's reachability argument no longer rests on a prediction. Branch A's gate at
`initRes 1e-8` is not merely *expected* to return `GATE FAIL` — on this toolchain a primal that fails
`1e-8` **may not survive to be graded at all**, so on A2-B2R's evidence Branch A's registered
`NOT A RESULT` can arrive as a **destroyed run rather than a measured fail**, and those are not the
same evidentiary object. §5's table is otherwise unchanged and its cost figures stand.

**NOT narrowed, and not proposed.** This addendum does **not** propose touching
`primalMinResTolDiff`; §5's *"What is NOT proposed"* stands verbatim and for its stated reason. It does
**not** propose making the abort non-fatal — whether any supported switch even exists is
**unmeasured**, a lane is establishing it from source, and any route that changes a registered
quantity needs its own dated amendment before compute. It does **not** file anything upstream: the
four prepared DAFoam defect classes all still read `Status: NOT FILED ANYWHERE`, filing is Sanaa's
alone, and whether this clause belongs to an existing class or is new is **not settled here**. It does
**not** widen `1.0e-05` under any reading (T25), and `N-D43` stays escalated and unruled.

**`A2-GC-P` remains `HELD` and `PERMISSION: NOT_FROZEN`.** Still no answer proposed.

**Gates · thresholds · bands · caps · labels changed by this addendum: 0 · 0 · 0 · 0 · 0.
Solver compute: 0 core-min. GPU: 0 GPU-h.**
