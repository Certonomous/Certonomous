# Archive replay for `w3-no-ladder-feature-without-draw-scatter` — results

Pre-registration: `W3_DRAW_SCATTER_RULE_REPLAY_PREREGISTRATION.md`, commit
**`6f196082`**, definitions and predictions fixed before counting.
**0 solver core-min**, as approved.

---

## 1. The counts the chief asked for

| question | answer |
| --- | --- |
| campaign + website records scanned | **151** |
| **records that STATE a ladder feature** | **16** |
| of those, **have evidence at the deciding rung** | **4** |
| **already compliant** (state the absence themselves) | **1** |
| **would be RESTATED** | **5** |
| **would be WITHDRAWN** | **5** — *all five withdrawn today, before this replay* |
| amended today for other reasons | 1 |

**Entry condition: PASSED.** 16 of 151 fire — neither every record nor none.

## 2. The predictions, scored

**P1 — a minority fire. TRUE.** 16 of 151, ≈11%. Most records report values,
gates, costs or verdicts without asserting a shape.

**P2 — ≥70% of firing records are RESTATE rather than WITHDRAW. FALSE as
written: the split is 50/50 (5 and 5).**

I am scoring this FALSE rather than reframing it, because the prediction was
fixed before the count. **But the number needs its structure stated, and the
structure changes what it means:**

> **All five withdrawals happened TODAY, before this replay ran** — B-52
> (`7abb0ba3`) and Ahmed 25° (`8f5bf878`). **The replay found ZERO further
> withdrawal candidates.**
>
> **Prospectively — which is how a rule operates — the split is 5 RESTATE, 0
> WITHDRAW: 100% restate.** The 50% is retrospective, and it says something
> different and already known: *both* families whose scatter has actually been
> measured failed.

So P2's prediction was wrong about the arithmetic and right about the
consequence. **The rule is cheap discipline, not an expensive purge** — that was
the question the chief said this number decides, and the answer does not depend
on which way P2 is scored.

**P3 — no more than two further withdrawal candidates, and any would be the
wings. TRUE, and stronger than predicted: zero.** Both wing families already
carry replicate evidence, so they fall under HAS EVIDENCE rather than needing
withdrawal — and `W3_WING_VALID_FAMILY_RESULTS.md:114` had **already restated
itself** unprompted (*"the ladder is not established as non-monotone; it is
established as unresolved"*). That sentence is the rule, written by this lab
before the rule existed.

## 3. The classification

**WITHDRAWN — 5** (all applied today, none new)
`B52_RUNG7_RESULTS.md` · `NOT_PASSING_REGISTER.md` §B-52 · `R4_ASYMPTOTIC_RESULTS.md` ·
`W1_AHMED_LADDER_DISPOSITION.md` · `W3_WING_VALID_FAMILY_RESULTS.md` (B-52 + Ahmed rows)

**HAS EVIDENCE AT THE DECIDING RUNG — 4** (no action)
`B52_RUNG8_RESULTS.md` (the rung-7→8 increment is measured against the noise floor
and survives) · `W3_GUARD_SWEEP.md:69` (NACA 0012, replicate family exists) ·
`W3_NACA4412_LAYERED_REPLICATES.md` · `W3_MESH_QUALITY_GATE_TWO_VALUES.md:152`

**ALREADY COMPLIANT — 1**
`W3_WING_VALID_FAMILY_RESULTS.md:114`

**RESTATE — 5** (the rule's whole remaining cost)
| record | body | what it asserts |
| --- | --- | --- |
| `NEXT_CASES_SLATE.md:179` | Ahmed 25° | *"non-monotone, increments −5.442e-3, −5.367e-3, then…"* |
| `W3_LADDER_RECIPE_AUDIT.md:134` | four two-knob ladders | *"increments, non-monotone"* |
| `DPW8_V2_joukowski.md:88` | DPW8 | *"despite the finer mesh — non-monotonic"* (already carries a force-noise-floor caveat) |
| `OTHER_WORK_STATUS.md:120` | TMR NACA 0012 | *"Cl non-monotonicity survives… ladder remains non-asymptotic"* |
| `4G_tmr_mesh_aspect_ratio.md:645` | TMR bump | *"the second increment grows"* |

**Nothing in this list has been amended by this replay** — it produces the
classification; the chief rules on adoption and on what moves.

## 4. Method, and the outstanding reconciliation

Per §7 of the family guidelines, the count is derived twice by different routes.

- **Route A (this document):** pattern enumeration over 151 records, then a
  context filter requiring the assertion to concern **grid-refinement**
  increments rather than force-in-time or residual oscillation (the raw pattern
  returned 231 lines across 58 files; **207 of them were not ladder features** —
  wake oscillation, residual oscillation, "turns out", non-monotone tier scales),
  then classification by reading each survivor.
- **Route B:** an independent search agent sweeping the same corpus without Route
  A's pattern list. **Dispatched; reconciliation OUTSTANDING at the time of
  writing.**

**The counts above are Route A only and are provisional until Route B lands.**
The pre-registration binds me to report disagreements rather than resolve them
silently, and it would be a poor advertisement for the recount rule to publish a
single-route count as final. **Any disagreement will be reported as a correction
to this document.**

**One judgement worth exposing:** the largest source of uncertainty in these
counts is not the search, it is the **definition** — 207 of 231 raw hits were
excluded as not-a-ladder-feature, so the count is dominated by that filter.
The definition was fixed in the pre-registration before any counting, which is
the only reason the number means anything.

## 5. What this says about the rule

**The rule fires on 16 of 151 records, would act on 10, and has 5 restatements
of prospective work left in the entire corpus.** Against that, the retrofit price
for the 5 unchecked ladders is **12.8–21.7 core-min** — less than checking the
B-52 alone cost (40.9, which ended in a withdrawal).

**And the argument the rule rests on is unchanged by the replay: the replicate
check is four for four.** B-52's turn withdrawn; NACA 0012's published mesh
sitting at the family maximum at +1.35σ; NACA 4412's scatter at 5.8–12.7% of the
mean; Ahmed's increment inverting or halving. **A check with a 100% hit rate
across four independent families is not a precaution — it is a measurement
everyone has been skipping.**
