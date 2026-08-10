# B-52 turn closure — five draws at rung 6, three at rung 7: results

Pre-registration: `B52_TURN_CLOSURE_PREREGISTRATION.md`, commit **`f4ccfe92`**,
committed before any new mesh existed. Chief-approved at ≈31 core-min. Record:
`B52_RUNG6_REPLICATE_runs/closure_record.json`. Run 2026-08-10 17:01–17:15 UTC.

---

## 1. The pre-registered verdict

> ### **INDETERMINATE** — and **SIGNAL is excluded.**

| quantity | measured |
| --- | --- |
| `s₆` (n = 5) | **2.1579 × 10⁻³** |
| `s₇` (n = 3) | **1.1090 × 10⁻³** |
| `√(s₆² + s₇²)` | 2.4266 × 10⁻³ |
| **`T̂` = \|turn\| / √(s₆²+s₇²)** | **1.671** |
| Welch ν | 5.61 |
| **90% CI on T** | **[0.846, 2.445]** |

The interval straddles 1.0, so neither NOISE (needs T_hi ≤ 1.0) nor MARGINAL
(needs T_lo > 1.0) can be declared. **Branch: INDETERMINATE — a precision
failure, not a physical finding**, exactly as §4 of the pre-registration defined
it.

**But the upper bound is 2.445, below 3.0.** Per the pre-registered bracket,
**SIGNAL is excluded at 90% confidence.** That is a definitive sub-result and it
is the one the audit needed: every Tier-1 claim treating the turn as established
structure **stays withdrawn**. What remains open is only whether the turn is
*pure noise* or *genuinely marginal* — a distinction with no consequence for any
claim in the audit.

**The pre-registered predictions, scored:**

| | prediction | outcome |
| --- | --- | --- |
| **P1** | *"the branch will be INDETERMINATE"* | **TRUE** — stated as the expected outcome from §1's arithmetic before meshing, not as a hedge |
| **P2** | *"`s₆` at n = 5 lands in [1.2, 3.2] × 10⁻³"* | **TRUE** — 2.158 × 10⁻³, near the middle |
| **P3** | *"`s₇` and `s₆` differ by more than a factor of 2"* | **FALSE**, and only just: the ratio is **1.946** against a bar of 2.0. With ν = 4 and 2 the ratio itself is enormously uncertain, so this is **not** evidence that the two rungs share a σ — it is a failure to show they do not. The `√2σ` shorthand is neither vindicated nor refuted |

## 2. The finding that outranks the verdict — NOT pre-registered, labelled as such

**This is a secondary analysis. It was not in the pre-registration, it did not
decide the verdict, and it is reported separately so it cannot be mistaken for
the pre-registered result.** It is also, by a wide margin, the most important
number this arm produced.

**All eight draws:**

| rung | draws (Cd, sorted) | mean |
| --- | --- | --- |
| **6** (n = 5) | 0.0469209, 0.0482808, 0.0486611, 0.0509543, **0.0522755** | **0.0494185** |
| **7** (n = 3) | **0.0482202**, 0.0501348, 0.0501473 | **0.0495007** |

**The published turn is `finer2 − rung7` = −4.0553 × 10⁻³. In the eight-draw
sample, `finer2` is the MAXIMUM of the five rung-6 draws and `rung7` is the
MINIMUM of the three rung-7 draws.** The number this lab has carried as its
ladder's largest signal is the **extreme-to-extreme pairing** of the two rungs.
Nobody chose it that way; one draw was taken at each rung and that is where they
fell.

**Re-estimated from all eight draws:**

> **mean(rung 7) − mean(rung 6) = +8.223 × 10⁻⁵ ± 1.158 × 10⁻³ (1 SE),
> t = 0.071.**
>
> **49.3× smaller than the published turn, and of the OPPOSITE SIGN.**
> Indistinguishable from zero.

**And it is not even resolvable to that.** The rung-7 draws average 438 926 cells
against the 441 057 reference (−0.48%). Priced against the family's own
refinement rate (≈4 × 10⁻³ of Cd per ≈33% of cells), that residual mismatch is
worth ≈1.8 × 10⁻⁴ — **more than twice the mean difference itself**. The increment
between these two rungs is smaller than the bias from not matching their
resolutions exactly.

**Why this and the INDETERMINATE verdict are not in conflict.** They ask
different questions. `T` asks *"is the published turn larger than draw noise?"*
and answers *"not by 3σ, and we cannot say more."* The difference of means asks
*"what IS the increment?"* and answers *"zero, to within a bias larger than the
answer."* Both are true; the second is the one that matters for the corpus.

## 3. What this settles, and what it does not

**Settles.** The audit's Tier-1 withdrawals are supported on evidence:
`T_hi = 2.445 < 3` excludes signal, and the eight-draw increment is consistent
with zero. *"The swings get wider"*, *"the ladder oscillates"*, and *"two of two
ladders both turn"* have nothing underneath them at this recipe and these rungs.

**Does not settle.** Whether the turn is *pure noise* or *marginal*. The chief's
approved arm was sized to separate those, and §4 shows why it could not — and why
spending more to try would be the wrong call.

**Not claimed** (per pre-registration §7): no ladder verdict, band or order
changes; the B-52's Cd values are not wrong, only the shape read from their
differences; a signal branch would not have reinstated the *mechanism*; and σ
here is **conditional on the G1 ±2% delivered-cell gate** (§5) and is not the
unrestricted draw-space scatter.

## 4. My own extension ask is WITHDRAWN — it would not have worked

The pre-registration asked, on the record and unspent, for **+1 draw at each rung
(≈20.2 core-min)** on the arithmetic that at T̂ ≈ 2.0 it converts an indeterminate
into a MARGINAL verdict. **T̂ came in at 1.671, not 2.0, and at the measured `s`
that extension does not reach a verdict:**

| n₆ | n₇ | ν | 90% CI at T̂ = 1.671 | outcome | extra core-min |
| --- | --- | --- | --- | --- | --- |
| **5** | **3** | 5.61 | **[0.846, 2.445]** | **indeterminate (this arm)** | — |
| 6 | 4 | 7.16 | [0.938, 2.362] | **still indeterminate** ← *my ask* | +18.8 |
| 7 | 4 | 8.41 | [0.994, 2.312] | still indeterminate (by 0.006) | +27.4 |
| **8** | **5** | 9.97 | **[1.048, 2.262]** | **MARGINAL — a verdict** | **+46.2** |
| 10 | 6 | 12.78 | [1.120, 2.196] | verdict, tighter | +73.6 |

**And NOISE is now unreachable at any n**, because the CI's upper bound can never
fall below the point estimate, and the point estimate is 1.671. The only verdict
still purchasable is MARGINAL, at **+46.2 core-min**.

> **My recommendation is: do not spend it.** MARGINAL and INDETERMINATE have
> **identical consequences for every one of the 22 amendments and 4
> withdrawals** — signal is already excluded, and §2 already shows the increment
> is consistent with zero by a far more direct route. Buying the label
> "marginal" for 46 core-min would be paying to classify one particular
> draw-pairing of a quantity we can now estimate directly at ≈0. **The arm the
> chief approved has delivered what the corpus needed; the arm I asked for on top
> of it would not have, and I am withdrawing the ask rather than letting it stand
> now that its own arithmetic has turned against it.**

## 5. Gates and machinery

- **G1 — delivered cell count.** All three new draws admitted **on attempt 1**:
  6d (50 45 77) → 328 453 (−0.75%), 6e (53 45 73) → 327 996 (−0.89%), 7c
  (54 49 84) → 434 641 (−1.45%). No re-draws were needed, which is itself a
  small vindication of `B52_RECIPE_NOTE_BACKGROUND_PRODUCT.md`'s rule: all three
  held `ny` at the value the note identified as controlling.
- **G2 — birth certificates.** Written at creation, admitted by hash at entry.
  All three `clean` (max skewness 3.96–3.98, max non-orthogonality 55–65).
- **G3 — settle.** All three pass with margin: 2σ at 0.021–0.024% of |Cd| against
  a 5% ceiling.
- **G4 — lever echo**, in its amended form (lever dictionaries and pre-solve
  `0.orig` only, after the original wording failed on `potentialFoam` outputs).
- **L-42 guard** active: the driver refuses to re-stage over a case already
  holding an admitted certified mesh.

## 6. Cost

| item | measured | core-min |
| --- | --- | --- |
| three meshes (63.9 + 65.8 + 81.4 s, 1 core) | 211.1 s | 3.52 |
| potentialFoam + decomposePar ×3 | ~30 s | 0.50 |
| 6d, 6e, 7c simpleFoam (171 + 175 + 245 s clock, 2 ranks) | | **19.70** |
| **total** | wall 17:01:06 → 17:14:55 (829 s) | **23.7** |

**23.7 against the pre-registered 27.4 and the chief's ≈31 — 13% and 24% under
respectively**, and under for a stated reason: no draw was refused, so the
budgeted re-draw allowance went unspent, and the box was quieter than the
replicate arm's.

## 7. Consequences for the audit

No claim is amended or withdrawn by this document — that remains the chief's to
rule. What changes is the **evidential basis** the audit's grades rest on:

| audit statement | before | now |
| --- | --- | --- |
| σ | a bracket spanning ×2.6, from three mismatched estimators at n = 2, 2, 3 | **s₆ = 2.158 × 10⁻³ (n = 5), s₇ = 1.109 × 10⁻³ (n = 3)**, measured separately |
| the turn's standing | *"0.91–2.38× its own uncertainty"* | **T̂ = 1.671, 90% CI [0.846, 2.445] — signal excluded** |
| the increment itself | never estimated | **+8.2 × 10⁻⁵ ± 1.2 × 10⁻³, consistent with zero, opposite in sign to the published turn** |

`models/curriculum/uq-studies/b52.json`'s `mesh_draw_scatter` block, added this
morning under chief ruling 4, carries the superseded n = 3 numbers and should be
updated to these on the chief's word.
