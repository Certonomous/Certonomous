# Ahmed 25° c3 — two more draws (n = 4): pre-registration

**Written 2026-08-10, before any new mesh exists.** Chief-approved at ~10–14
core-min on the leg-1 report; the c4 CI leg is explicitly **not** taken, upheld
for the reason given — refining an interval around a badly-estimated centre buys
precision about the wrong thing.

Leg 1: `R4_AHMED_TURN_DRAW_SCATTER_RESULTS.md` (`f534760f`), pre-registration
`e543bc5e`. Model rule per SUPERVISION_CHARTER §5: session default.

---

## 1. What is already forced, before anything is run

`c3` = 0.073992743 and `c3b` = 0.079827008 differ by **5.834 × 10⁻³**. Any
four-draw sample containing both has a range of at least that, so with
`E[range/s] = 2.059` at n = 4, **`s_c3` will land at or above ≈2.8 × 10⁻³ —
already 3.1× the c3 → c4 increment of 8.895 × 10⁻⁴.**

> **This arm CANNOT return "the scatter is small."** That outcome is arithmetically
> unavailable. It can only say **which structure** the scatter has. Stated here so
> no reader, including me, expects a reassuring branch that cannot appear.

## 2. The discriminating statement — outlier vs broad scatter, and WHICH draw

The chief's question: *if the scatter is large but the ORIGINAL draw is the
outlier rather than the redraw, that asymmetry matters for whether the published
number or the recipe is at fault.*

**Statistic:** `R = s(the three draws excluding the most extreme) / s(all four)`.
A single aberrant draw inflates `s` and collapses it on removal; broad scatter
does not.

**The bar is calibrated by simulation, not chosen.** 200 000 samples of n = 4
from a normal (i.e. **no** outlier present) give this distribution of `R`:

| percentile | 5th | 10th | 25th | 50th | 75th | mean |
| --- | --- | --- | --- | --- | --- | --- |
| `R` | 0.206 | **0.277** | 0.436 | 0.608 | 0.717 | 0.577 |

> **OUTLIER-DOMINATED if `R ≤ 0.28`** — the 10th percentile, so under pure
> scatter this fires wrongly 10% of the time, by construction and stated in
> advance. **BROAD SCATTER otherwise.**

**Then, and only if OUTLIER-DOMINATED fires, the identity of the extreme draw
selects the branch:**

| branch | condition | **what is at fault** |
| --- | --- | --- |
| **B1** | outlier-dominated, and the extreme draw is **the original `c3`** | **the PUBLISHED NUMBER.** The recipe is not especially draw-sensitive; the ladder's c3 entry is an unlucky draw. c3 should be restated as the draw mean and the increment recomputed — which, since every other draw so far sits above c3, would shrink or invert the turn |
| **B2** | outlier-dominated, and the extreme draw is **`c3b` or a new draw** | **the RECIPE.** The published c3 is representative and the excursion is a rare state the recipe occasionally lands in. The turn as published may stand, but the ladder carries a **bimodality that must travel on its face** |
| **B3** | **broad scatter** (`R > 0.28`) | **both.** No single draw at this rung is trustworthy, the increment cannot be read from single draws at all, and the turn is unreadable at n = 1 per rung — the standing that ended the B-52's |

**Pre-refused, by name:** (a) reading the branch off which draw *looks* odd rather
than off `R`; (b) dropping any draw from `s_c3` — no draw is excluded for its Cd,
G1 excludes on delivered cell count alone and only before any solve; (c) treating
B2 as an exoneration — a recipe that occasionally changes flow state is a worse
finding for a ladder than a single bad number, not a better one.

## 3. Carried forward from leg 1 — the increment-movement test at n = 4

Re-estimated increment = `mean(c4, c4b) − mean(c3 draws)`, same bar as leg 1:
**SURVIVES** within 25% of +8.895 × 10⁻⁴ and same sign; **DISSOLVES** below 50%
or sign flips; **PARTIAL** between. At n = 2 it fired DISSOLVES (−1.979 × 10⁻³).
Reported at n = 4 whatever it does; **a branch flip from leg 1 is a legitimate
outcome and would say the n = 2 reading was premature** — which is what n = 2
readings are for.

## 4. The draws, and a design change that buys admission cheaply

**Leg 1 spent a third of its budget on meshes G1 then refused**, because on this
recipe the delivered cell count is locally *anti-correlated* with the background
product and the published draw sits at a local maximum (leg-1 §4). Meshing is
≈0.8 core-min; solving is ≈3.1. So:

> **Mesh first, screen on delivered cells, then solve only the admitted draws.**
> Up to **five** candidates are meshed; those inside G1's ±2.0% band
> (249 813–260 009 cells) are admitted; **the two admitted draws whose cell
> counts are closest to c3's 254 911 are solved.**

Selection is on **delivered cell count only, decided before any Cd exists** —
the rung-7 attempt-1/attempt-2 precedent. No draw is ever selected or dropped on
its force coefficient.

| order | divisions | rationale |
| --- | --- | --- |
| 1 | **(99 21 59)** | one step in nx from the observed maximum |
| 2 | **(98 21 60)** | one step in nz from it |
| 3 | (97 21 59) | one step down in nx |
| 4 | (99 21 60) | up in both |
| 5 | (100 21 59) | two up in nx |

`ny` held at 21 throughout: it is the division that steps delivered count, so the
σ measured is **draw scatter at fixed delivered resolution**, conditional on G1.
**If fewer than two candidates are admitted, the arm reports n < 4 and the
shortfall as its result** — the allowance is not extended, exactly as in leg 1.

**Gates unchanged:** G1 (above), G2 birth certificate written at creation and
`certificate_admits` before launch, G3 the rung must reach `residualControl`,
G4 lever echo. **4 MPI ranks scotch on every draw**, fixed across this family.

## 5. Cost, from leg 1's own measurements

| | basis | core-min |
| --- | --- | --- |
| five meshes | leg 1 measured 39.0–60.1 s each, 1 core → ≈0.8 | **4.0** |
| two solves | leg 1 measured c3b at ClockTime 47 s × 4 ranks | **6.2** |
| potentialFoam + decomposePar + reconstructPar ×2 | leg 1 | **0.5** |
| **total** | | **≈10.7** |

Inside the approved 10–14. If more than two candidates are admitted the extras
are **not** solved — the arm stops at n = 4 as approved rather than spending the
headroom.

## 6. What will NOT be claimed

- **No SIGNAL/NOISE verdict on the Ahmed turn.** That needs the c4 leg, which is
  deliberately not taken; `T` is not computed here.
- No change to `ahmed_25.json`'s band, order or verdict.
- No amendment to `R4_ASYMPTOTIC_RESULTS.md`'s *"not one unlucky mesh"* headline —
  the chief has ruled that n = 2 moves a caveat, not a headline, and n = 4 is
  reported to him rather than applied to it by me.
- The slant-bistability hypothesis is **not** tested here. Distinguishing a flow
  state change from a resolution effect needs field inspection, not more draws.
- Nothing about `ahmed_35`, or any other body, is inferred.

*Nothing below this line existed when this document was committed.*
