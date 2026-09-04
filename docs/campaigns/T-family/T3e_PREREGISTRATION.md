# T3e — the `R_fx` continuation (`R_fy`): settle whether `|U|`'s non-convergence is DECAYING or STALLED, on three surviving checkpoint pairs, through a builder and grader REHEARSED AGAINST EACH OTHER FIRST

> **STATUS AT THIS COMMIT: DRAFT. NOT FROZEN. NOT ENQUEUED. NOT LAUNCHED. AUTHORISES NO SOLVE.**
>
> **The freeze is deliberately WITHHELD, and the condition is named: §7's builder-grader
> rehearsal has NOT been performed.** T3d's entire failure was that its pinned builder and
> pinned grader were **never driven against each other** before freezing, and were mutually
> unsatisfiable from that moment. **This document will not repeat that by freezing on prose.**
> The freeze follows the rehearsal; it does not pre-empt it — the ordering `T21` established
> and the ordering T3d did not get.

**Authored personally by `heat-transfer-supervisor`**, on the chief's explicit ruling, under a
disclosed constraint recorded here rather than omitted: **the `Agent` tool was DENIED by the
permission classifier when this team attempted to dispatch a lane for this work.** The denial was
**not routed around** — no alternative dispatch path was attempted. The ruling covers a supervisor
doing directly what a denied lane could not, **with the denial disclosed in the registration's own
record**, which is this paragraph. **If T3e's execution later needs lanes and the denial persists,
that goes on Sanaa's desk as a named capability gap and is not worked around.**

---

## 1. THE THREE DEFECTS THIS RUNG EXISTS TO CARRY FORWARD — ALL OF THEM OURS

T3d graded **`NOT A RESULT`** (`T3d_RESULTS.md`). Under Sanaa's 2026-09-04 mandatory-completion
order that is a **waypoint, not a resting place**, and under `VERIFICATION_CHARTER` §2an
(`c46c196f`) with `NONCONVERGENCE_STANDARD` §4 a model-form failure **routes** rather than
terminates.

**D-1 — THE BUILDER DID NOT WRITE WHAT THE GRADER READS.** `build_t3d.py:89` wrote `CASE.txt` as
six lines of prose with **no key-value pairs**; `analyse_t3.py:461-468` reads **seven numeric keys**
from it (`H`, `nu`, `Pr`, `Prt`, `dTdn_wall`, `T_in`, `U_in`, `endTime`) and refused on the first.
Both were sha-pinned in the **same** frozen registration and both were byte-identical to HEAD.
**No outcome of the run could have been graded.** *Repair: §7.*

**D-2 — NO COMPLETION-MARKER PRODUCER WAS REGISTERED.** T3d registered three artifacts and no
marker producer, eight days after this same team registered one correctly for `R_ff` under a
`PRE-FIRST-COMPUTE` heading. It cost a §2d.1 petition, which `VERIFICATION_CHARTER` §2ao **refused
as unnecessary** while unblocking the result — and closed with the instruction this section
discharges. *Repair: §6.*

**D-3 — THE PHYSICS QUESTION WAS LEFT UNANSWERABLE BY A WRITE SETTING.** `|U|` finished at
`relative = 3.68937e-06` against `tol = 1e-06` — **3.69× over, NOT CONVERGED**. Whether that is
**decaying** or **stalled** is **UNDETERMINED and undeterminable from disk**, because
`purgeWrite 2` left only `22000/` and `24000/` — **one pair, and a trend needs at least three.**
*Repair: §4.*

---

## 2. THE CASE

Continuation of `R_fx`, itself the continuation of `R_ff`. **Mesh IDENTICAL to `R_ff` and `R_fx` —
602,128 cells. This is not a new ladder level and no refinement is introduced.**

| | |
|---|---|
| rung | T3 — heated backward-facing step, Vogel & Eaton 1985 conditions |
| case | `R_fy`, seeded from `R_fx/24000` |
| solver | `buoyantBoussinesqSimpleFoam`, **8 ranks**, `simple (8 1 1)` |
| model | `kOmegaSST`, wall-resolved |
| `H` | 0.038 m · `nu` 1.5e-05 m²/s · `Pr` 0.71 · `Prt` 0.85 |
| `Re_target` | 28,000 · `U_in` 10.35 m/s · `T_in` 300.0 K · `dTdn_wall` 10,000.0 K/m |

**Inherited unchanged and NOT re-derived here:** every geometric and physical constant above is
`R_ff`'s, and `build_t3e.py` copies them into `R_fy/CASE.txt` **from `R_ff/CASE.txt` by key**,
never by retyping (§7.2).

---

## 3. WHAT IS AND IS NOT PREDICTED — AND THE ONE THING THIS RUNG REFUSES TO GUESS

**THE DECAY RATE OF `|U|` IS UNMEASURED, AND THIS DOCUMENT DOES NOT INVENT ONE.** Exactly one
pair exists on disk. **A rate cannot be fitted to one point**, so no prediction is registered that
would require one, and **no number here is reverse-engineered from a trend nobody has seen.**

**P-1 — PRIMARY, AND THE ONLY DIRECTIONAL PREDICTION. `|U|`'s relative change DECAYS MONOTONICALLY
across the three graded pairs.** Formally: `rel(2000,4000) > rel(4000,6000) > rel(6000,8000)`,
strictly, on `iterative_convergence_vector(case, "U")`.
**FALSIFIER F-1: any non-monotone or increasing sequence falsifies P-1**, and the non-convergence
is then **not settling** — which routes to numerical rule-out (§9), not to more iterations.

**P-2 — `T` STAYS CONVERGED.** `T` finished T3d at 8.03132e-07 ≤ 1e-06. It is expected to remain
below tolerance on all three pairs. **FALSIFIER F-2: `T` rising back above 1e-06 falsifies P-2 and
is a finding about the restart, not about the mesh.**

**P-3 — NO RESTART SPIKE.** T3d measured no spike at all on seeding (largest excursion `p_rgh`
5.6 % at iteration 9). The same is expected here. **F-3: a residual maximum above the seed value in
any solved field falsifies P-3.**

> ### ⚖ **WHETHER `|U|` REACHES 1e-06 IS *MEASURED*, NOT PREDICTED — AND BOTH OUTCOMES ARE GRADEABLE**
> This is the T19 lesson applied forward. **A rung whose registered rule only one outcome can
> satisfy is a defect, not a gate.** So:
> - **`|U|` reaches `≤ 1e-06` at the last pair → the level is iteratively converged**, and the
>   composed `convergence_state` clears rule 5 clause (1).
> - **`|U|` does not reach it, but P-1 holds (decaying)** → **`GATE REACHED`** on the trend
>   question, and the rung reports the measured decay with the iterations-to-tolerance it implies,
>   **explicitly as an extrapolation and never as a measurement.**
> - **P-1 falsified (stalled or rising)** → **`NOT A RESULT`** on rule 5 clause (1), and the item
>   routes under §2an to numerical rule-out.
>
> **All three are honest completions. None requires the answer to come out any particular way.**

---

## 4. THE CHECKPOINT DESIGN — D-3's REPAIR, AND IT IS THE WHOLE REASON THIS RUNG IS SHORT

| | |
|---|---|
| `endTime` | **8,000** additional iterations (counter restarts at 0) |
| `writeControl` | `timeStep` · `writeInterval` **2000** |
| **`purgeWrite`** | **0 — KEEP EVERY CHECKPOINT** |
| surviving time dirs | `2000, 4000, 6000, 8000` — **four**, plus the seed at `0` |
| **graded pairs** | **(2000,4000), (4000,6000), (6000,8000) — THREE consecutive pairs** |

**Three pairs is the minimum that can distinguish a decaying trend from a stalled one, and this
rung buys exactly that and no more.** T3d's `purgeWrite 2` is the single setting that made the
question unanswerable after 4,723 core-min had been spent; **`purgeWrite 0` is registered here so
that no outcome of this run can leave the same hole.**

**WHY NOT SIMPLY RUN LONGER.** A 24,000-iteration repeat would cost ~3× this rung and would still
answer the trend question **at its first four checkpoints** — the rest is spent on a convergence
outcome whose rate is currently unknowable. **Measuring the rate first is cheaper than assuming
it**, and is the same discipline that put `D0` ahead of K0eR3's main arms and the coarse level
ahead of T5d's fine one.

**Disk, stated because `purgeWrite 0` is a deliberate change:** four time directories at 602,128
cells across eight written fields, ≈ **400 MB on disk**. **Not committed to git** — case
directories in this family stay untracked (the T5b/T19b convention).

---

## 5. THE GATE

**Graded quantity: the composed `convergence_state` at each of the three pairs**, from
`analyse_t3.py`'s own `iterative_convergence` (`T`) and `iterative_convergence_vector` (`|U|`),
**`tol = 1e-06`, inherited unchanged from T3d and NOT moved.**

**Rule 5 applies and is not waived.** **NO ROACHE TRIPLE IS FORMED** — this is one mesh at one
refinement, so **no observed order, no GCI and no Richardson extrapolate is computed, quoted or
derivable**, and **every number this rung produces carries NO DISCRETISATION BOUND AT ALL.** Rule 5
clause (1) **is** reached: a level not iteratively converged is `NOT A RESULT` whatever its value.

**D-J1 discipline, carried forward:** the grader **must emit `field_range` beside every
`convergence_state`** it reports. T3d's `analyse_t3d.py:242-245` built its `measurements` block from
a key list carrying `convergence_state` and **neither** `convergence_T` **nor** `convergence_U` — the
only dicts holding the denominator — so `gate_t3d.json` would have recorded the word without the
number. **`analyse_t3e.py` emits both denominators or it refuses.** A zero denominator returns
`NOT A RESULT`, **never `0.0`**.

---

## 6. THE COMPLETION-MARKER PRODUCER — REGISTERED HERE, BEFORE COMPUTE. D-2's REPAIR.

**`verification/runs/T-family/T3_runs/mark_done_t3.py`, git blob `5da28c733e47a4a6c8046dfdf8674c2af27ab81a`, is T3e's registered completion-marker producer**, invoked as:

```
python3 mark_done_t3.py --root verification/runs/T-family/T3_runs R_fy
```

**No new file is created and no existing file is edited.** `VERIFICATION_CHARTER` §2ao established
at source that `check(root, case)` is **generic by construction** — `CASES` at `:105` is a default,
not a domain; every criterion resolves from the case's own artifacts — and that it is **stricter
than `CLAUDE.md` rule 4** (`:34` requires `phi`). **Its invocation and full output are recorded
beside the case**, per §2ao condition 1.

**IF IT REFUSES, THE REFUSAL IS THE FINDING** and is not worked around (§2ao condition 2). The six
clauses are then not met and this rung is `NOT A RESULT` on completion grounds.

**`reconstructpar_rc = 0` is additionally required** and is checked from `STATUS.R_fy` — `R_fy` runs
decomposed on 8 ranks, so the reconstruction is load-bearing. **This is stricter than the marker,
and it is registered here rather than assumed.**

---

## 7. ⚠ THE BUILDER-GRADER REHEARSAL — D-1's REPAIR, AND THE CONDITION ON THIS DOCUMENT'S OWN FREEZE

### 7.1 THE REQUIREMENT

**Before this document is frozen, `build_t3e.py` and `analyse_t3e.py` MUST BE DRIVEN END-TO-END
AGAINST EACH OTHER ON A SYNTHETIC CASE**, and the transcript committed. The rehearsal must
demonstrate, on a case built by the builder and never touched by hand:

1. the grader **reads every key it needs** from the builder's `CASE.txt` — all seven of `H`, `nu`,
   `Pr`, `Prt`, `dTdn_wall`, `T_in`, `U_in`, `endTime` — **and names each one it read**;
2. the grader **runs to a verdict** on synthetic fields rather than refusing;
3. **a deliberately corrupted `CASE.txt` (one key removed) makes the grader REFUSE at exit 2** —
   the positive control on the negative result, so that (1) is not a vacuous pass;
4. the completion-marker producer of §6 **writes a marker on a synthetic complete case and refuses
   on an incomplete one.**

**Clause 3 is the one that matters most and is the one T3d never had.** A rehearsal that only shows
success does not show the check is live. *(This is the lab's unrehearsed-success lesson, recorded
at `FAIL_OPEN_GATE_AUDIT` §28.)*

### 7.2 THE BUILDER'S CONTRACT

`build_t3e.py` writes `R_fy/CASE.txt` **carrying the full structured key-value block**, with every
inherited constant **copied from `R_ff/CASE.txt` by key** and never retyped, plus the continuation
keys (`endTime`, `writeInterval`, `purgeWrite`, seed source). **The prose header T3d wrote may be
appended BELOW the block; it may not replace it.**

### 7.3 THE FREEZE THIS DOCUMENT WILL TAKE

At freeze, §8 will pin **by git blob sha**: `build_t3e.py`, `run_one_t3e.sh`, `analyse_t3e.py`, and
the §6 marker producer. **Until those four pins exist, this document authorises nothing**, and
`SUPERVISION_CHARTER` §3 check 4 cannot be discharged against it.

---

## 8. ARTIFACTS AND PINS

**NOT YET CUT.** `verification/runs/T-family/T3e_runs/` does not exist and is not created by this
commit. No case, no builder, no launcher, no grader, no queue entry.

---

## 9. COST — RULE 12

**Basis: T3d's OWN MEASURED rate on this exact mesh, `0.196800` core-min/iteration**
(4,723.200 core-min ÷ 24,000, from `STATUS.R_fx`). **Not `R_ff`'s 0.226755** — that figure was a
whole-run average taken on a saturated box and it mispredicted T3d by 13.21 % in the favourable
direction. **Using the predecessor's own measured rate is the calibration lesson of
`C-20260904T150910.320385Z-a636135b` applied forward.**

| | |
|---|---|
| **POINT** | **1,574.4 core-min** = `0.196800 × 8,000` |
| **HARD CAP** | **4,723.2 core-min** = `3 × POINT` |
| registered `timeout_s` | **35,424 s** = `4,723.2 × 60 ÷ 8 ranks` |
| dollars at POINT | **$1.3461** — **DERIVED at $0.0513/core-h, reported-by-owner, NEVER MEASURED** |

**An overrun stops the run; it does not get a new budget.** **A predicted-versus-actual row is owed
to `docs/COST_CALIBRATION.md` at completion and at no earlier point** — no projection is entered as
an actual.

**THE COST ARGUMENT, STATED PLAINLY:** the predecessor spent **4,723.200 core-min** and produced no
graded row. **This rung spends one third of that to answer the one question that would make a
longer run worth launching.** That is the case for spending a few more properly, not for spending
many more hopefully.

---

## 10. WHAT THIS DOCUMENT DOES **NOT** DO

- It **does not freeze.** §7's rehearsal has not happened.
- It **does not create** `T3e_runs/`, build a case, write a builder, launcher or comparator, enqueue anything, or launch anything.
- It **does not move** any gate, threshold, band, cap or label. `tol = 1e-06` is T3d's, unchanged.
- It **does not re-grade** T3d or any sibling. T3d's `NOT A RESULT` stands.
- It **does not assert any verdict**, and no term of `CLAUDE.md` rule 1's vocabulary is claimed for T3e anywhere in it.
- It **does not claim** that `|U|` will converge, will not converge, or is close to converging. **That is the measurement this rung exists to take.**

---

## ADDENDUM 1 — 2026-09-04 (PRE-FIRST-COMPUTE) — §7's REHEARSAL IS NO LONGER THIS RUNG'S OWN IDEA; IT IS CHARTER LAW, AND THIS DOCUMENT IS ITS REFERENCE FORM

**Appended by `heat-transfer-supervisor`. Lines whose number changed above this section: 0.**
**Condition for a pre-compute amendment (`CLAUDE.md` rule 2), stated and checked:
`verification/runs/T-family/T3e_runs/` does not exist; no builder, launcher, comparator or queue
entry naming T3e exists; zero core-minutes have been spent against this rung. Verified on disk in
the invocation that committed this addendum. No gate, threshold, band, cap or label moves.**

`VERIFICATION_CHARTER` **§2ap** (v1.60, extended v1.61) now makes §7's rehearsal **binding law**:

> **where a registration pins both a producer and a consumer of the same artifact, it freezes only
> after the producer's REAL OUTPUT has been driven through the consumer — one SUCCESS leg and one
> CORRUPTION leg, recorded in the registration.**

**§7 as written already satisfies it and exceeds it**: clause 1 is the success leg naming every key
read, **clause 3 is the corruption leg** (one key removed → the grader must REFUSE at exit 2), and
clauses 2 and 4 extend the same discipline to the verdict path and the completion-marker producer.
**Clause 3 remains the load-bearing one: a rehearsal that only shows success does not show the check
is live.**

**The clause is FORWARD-ONLY with NO BACKFILL**, so nothing above is reopened and no frozen sibling
acquires a defect it did not have. **§7.3's freeze condition is unchanged and is now doubly
binding** — by this document's own terms and by charter.

**Recorded for accuracy, not credit:** the charter cites this team's three-instance argument
(T19, T3d, T5b — each a *different* mutual incompatibility between separately-pinned components,
**none detectable by reading either component alone**, ~4,752 core-minutes between them), and it
arrived alongside `dafoam`'s and `cfd`'s independent arrivals at the same rule. **Three teams
reaching one conclusion separately is the evidence; this rung is one of its three instances, not
its author.**
