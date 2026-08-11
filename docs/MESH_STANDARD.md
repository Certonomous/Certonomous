# Grid-Convergence Practice — Inherited from DPW-8/AePW-4 (D8)

**Date:** 2026-07-29
**Status:** House practice for how a grid FAMILY is built and how its results are reported —
distinct from `docs/standards/MESH_STANDARD.md` (v1.0, 2026-07-25), which governs single-mesh
QUALITY gates (non-orthogonality, skewness, aspect ratio). That document says whether one mesh is
admissible; this one says how a *sequence* of meshes should be sized relative to each other and how
disagreement across a family (or across codes) should be reported. **Naming collision flagged, not
hidden** — the two files govern different questions and are cross-referenced from each other.

**Source:** `demo-output/website/campaign/DPW8_AEPW4_SCOPING.md` (commit `e7bd737`) located and
verified the DPW-8/AePW-4 joint-workshop gridding guidelines as openly downloadable, no registration
wall. This document re-derives (a)–(c) below **directly from that source PDF**, fetched and
text-extracted in this pass (`pdftotext -layout`) rather than trusted secondhand — the earlier
scoping report paraphrased the formula; this document quotes the underlying numbers.

**Primary source:** [`gridding_guidelines_v3_07012024.pdf`](https://www.aiaa-dpw.org/ref/gridding_guidelines_v3_07012024.pdf),
Version 3, July 1, 2024, B. Pomeroy (NASA) / B. Rider (Boeing). 8 slides. Consistent with DPW-7's own
baseline grid family plan (cited on the source slide).

---

## (a) Grid-family growth formula

The guidelines define a **6-level family**, indexed by Grid Level `L` (1 ≤ L ≤ 6):

| L | Name | Abbrev |
|---|---|---|
| 1 | Tiny | T |
| 2 | Coarse | C |
| 3 | Medium | M |
| 4 | Fine | F |
| 5 | Extra Fine | X |
| 6 | Ultra Fine | U |

Two related, but distinct, growth rules — **do not conflate them**, since our own Joukowski salvage
(Part 1 of this directive) shows how easy that is to do by accident:

1. **Overall grid size (cell count) growth between levels:**

   > "Grow next-finer grid in family by approximately **`[(L+2)/(L+1)]³`** in size"

   This is a *diminishing* ratio as L increases — not a constant doubling:

   | Step | Ratio |
   |---|---|
   | L1→L2 | (3/2)³ = 3.375× |
   | L2→L3 | (4/3)³ = 2.37× |
   | L3→L4 | (5/4)³ = 1.95× |
   | L4→L5 | (6/5)³ = 1.73× |
   | L5→L6 | (7/6)³ = 1.59× |

2. **Linear dimension scaling between levels** (surface spacing, spanwise/chordwise cell sizes):

   > "Scale dimensions in all three dimensions by approximately **`[(L+2)/(L+1)]`**" (the cube root
   > of the cell-count ratio above — consistent, since scaling 3 dimensions by the same linear
   > factor multiplies volume/cell-count by its cube).

3. **Wall-normal (Δy1) spacing does NOT follow the same `[(L+2)/(L+1)]` ratio** — it follows its own,
   separately-tabulated schedule (§b below), because it is additionally constrained to hit a target
   y+ at each level under a bounded stretching rate. The underlying closed-form equation relating Δy1
   to L, Re, and skin-friction coefficient is present on the source slide but its typeset (subscripts/
   superscripts) did not survive PDF text-extraction cleanly in this pass; **the tabulated per-level
   output values in §b are quoted directly and are unambiguous** — the equation itself is marked
   unestablished rather than reconstructed by guesswork.

**Companion surface-spacing rules** (same source slide, "Surface Spacing" — quoted, not paraphrased):

- Wing/airfoil chordwise spacing at LE & TE: **< 0.1% of local chord**.
- Wing spanwise spacing at root & tip (3-D cases): **< 0.1% × semispan**.
- Full-span 2-D-airfoil-with-span cases (e.g. ONERA OAT15A): spanwise cell size ≈ **Cref/112.5**
  (≈2.04mm at the 230mm reference chord used for that case).
- Trailing-edge base: **≫ 8 cells**.
- Fuselage nose / body-end spacing: **< 1% × Cref**.
- Farfield boundary: **> 100 chord lengths** (2-D) / **> 100 semispan lengths** (3-D, CRM case:
  1156.75 inches at full scale).

---

## (b) y+-anchored wall-normal spacing tables

Two regimes are tabulated, both for the CRM at full scale (`cref = 275.8 in`; "scale linearly" for
2-D cases such as ONERA OAT15A). **Quoted verbatim from the source PDF, both Re tables:**

### Re_c = 5×10⁶

| Level (L) | Name | Δy1 (inches) | Factor (vs. prior level) | y+ (target) | Min. #Δy1 constant-spacing wall cells | Viscous growth rate |
|---|---|---|---|---|---|---|
| 1 | Tiny (T) | 0.0011922 | 1.0000 | ~1.00 | 2 | 1.160000 |
| 2 | Coarse (C) | 0.0007950 | 0.6668 | ~0.67 | 3 | 1.104007 |
| 3 | Medium (M) | 0.0005961 | 0.7498 | ~0.50 | 4 | 1.068189 |
| 4 | Fine (F) | 0.0004770 | 0.8002 | ~0.40 | 5 | 1.044958 |
| 5 | Extra Fine (X) | 0.0003972 | 0.8328 | ~0.33 | 6 | 1.029752 |
| 6 | Ultra Fine (U) | 0.0003405 | 0.8571 | ~0.29 | 7 | 1.019737 |

### Re_c = 3×10⁷

| Level (L) | Name | Δy1 (inches) | Factor (vs. prior level) | y+ (target) | Min. #Δy1 constant-spacing wall cells | Viscous growth rate |
|---|---|---|---|---|---|---|
| 1 | Tiny (T) | 0.0002332 | 1.0000 | ~1.00 | 2 | 1.160000 |
| 2 | Coarse (C) | 0.0001555 | 0.6668 | ~0.67 | 3 | 1.104007 |
| 3 | Medium (M) | 0.0001166 | 0.7498 | ~0.50 | 4 | 1.068189 |
| 4 | Fine (F) | 0.0000933 | 0.8002 | ~0.40 | 5 | 1.044958 |
| 5 | Extra Fine (X) | 0.0000777 | 0.8328 | ~0.33 | 6 | 1.029752 |
| 6 | Ultra Fine (U) | 0.0000666 | 0.8571 | ~0.29 | 7 | 1.019737 |

"Factor" is the ratio of that level's Δy1 to the *previous* level's Δy1 (cross-checked by direct
division of the table's own inch values: e.g. Medium/Coarse at Re=5e6 = 0.0005961/0.0007950 = 0.7498,
matches to the digit).

**Two additional numeric rules from the same source slide, held as hard constraints:**

- **Growth-rate ceiling: < 1.2× normal to viscous walls.** All six tabulated per-level growth rates
  (1.160 down to 1.020) satisfy this by construction — the ceiling is never approached, let alone hit.
- **Minimum wall-normal constant-spacing cells: at least 2**, growing to 7 at the Ultra Fine level
  (one additional constant-spacing cell per level, per the `#Δy1s` column above).

---

## (c) Scatter-reporting conventions

The DPW family's convention for presenting disagreement (across codes, grids, or meshes) is a
**band, not a point estimate**, reported two ways simultaneously:

- **Interquartile range (IQR)** across participant submissions.
- **Standard deviation** across the same submissions.

**Precedent number, correctly attributed by workshop generation** (this is DPW-VI's 2016 result, the
most recent DPW generation with full published statistical detail — **DPW-8's own post-workshop
results are not yet published** as of this report, per `DPW8_AEPW4_SCOPING.md` §1, so the following
is inherited as "this is how the DPW family reports scatter," not asserted as a DPW-8-specific number):

- DPW-VI Wing-Body Case 2A, coarse-grid median Cd = 257 counts.
- **IQR: ±4–5 counts (band 252–262 counts).**
- **Standard deviation: 3.7–5.1 counts** (varies by grid level/configuration).
- Source: `docs/DPW-CRM-SCOPING.md` §2, citing the DPW-VI statistical analysis
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC7816761/).

**Other scatter-reduction conventions carried into this standard** (from
`DPW8_AEPW4_SCOPING.md` §2, §5, verified against the workshop's own case-matrix and working-group
material):

- **Drag-increment vs. absolute-drag distinction.** A predicted *increment* (e.g. wing-body vs.
  wing-body-nacelle-pylon) scatters roughly **3× less** than an absolute drag value (order 1–2 counts
  vs. 4–5 counts). Where a comparative claim is the actual point (does change X help or hurt), report
  the increment and its own band — do not launder it through two noisy absolute numbers.
- **Fully-qualified model naming as a scatter-reduction lever.** DPW-8's own "Source of Scatter"
  working group treats ambiguous turbulence-model specification as a measured source of code-to-code
  disagreement — e.g. "French Vanilla SA-(neg) (All-terms)" names a specific SA variant, not generic
  "SA." Any Certonomous report comparing runs across models must name the exact variant and closure
  constants, not a family name.
- **Machine-precision convergence (~1e-10)** is specified for DPW-8's dedicated scatter-reduction
  case, roughly 4–5 orders tighter than this lab's production bar (p≤1e-5/U≤1e-6). Adopted here as an
  **aspirational ceiling for scatter-focused campaigns, not a blanket requirement** — most production
  work does not need it, but a campaign specifically trying to isolate grid/model scatter from
  iterative-convergence noise should tighten toward it before reporting a band.

---

## How this changes our practice — concretely

Our current grid work is ad hoc. Two live examples, and what MESH_STANDARD would have required
differently in each:

### NACA 4412 wing ladder ("Ladder C3", `demo-output/website/OTHER_WORK_STATUS.md`)

**What happened:** the ladder was never a systematic grid family. Its two rungs differ not by a
stated, constant refinement ratio but by *which single `addLayersControls` knob was toggled*:
Attempt 1 relaxed nine layer-control settings at once and boundary-layer coverage **collapsed**
58.3%→4.36% (the opposite of the intended effect); Attempt 2 changed only `nGrow` (held at 0),
coverage improved to 77.00%, cell count rose to 2,091,678 (~37.4 core-min). No cell-count ratio
between rungs was ever stated as a design target — it fell out of whichever knob got turned. The
ladder is explicitly non-asymptotic: "Better coverage closes only ~26.5% of the Cl gap to fine rung;
ladder remains non-asymptotic." Worse, the acceptance band was **self-referential** — anchored on the
solve's *own* Cl — so a 25.0% Cl over-prediction on one rung inflated induced drag 56.2% and widened
the band until the **worst-resolved rung (4.36% coverage) passed** and the **two best-resolved rungs
(94%+) failed**. Verdict on record: **NOT VALIDATED**.

**What MESH_STANDARD requires instead:**
1. A stated Level index `L` with the **same refinement rule applied at every step** — e.g. our own
   4× cell-count doubling convention (used in the Joukowski V2 salvage, Part 1 of this directive) or
   the DPW `[(L+2)/(L+1)]³` formula — not qualitatively different meshing strategies (different layer
   controls) between rungs. Refine the same way each step; change only the resolution parameter.
2. A y+-anchored Δy1 table with the stated **<1.2× growth-rate ceiling** and the **minimum
   constant-spacing-wall-cells rule** (§b), so boundary-layer coverage (58%→77%→94%…) is a *byproduct*
   of hitting a y+ target at each level, not something separately hand-tuned per rung.
3. **IQR/std reporting across the family**, not a band anchored on one rung's own uncertain Cl. This
   is the specific failure this ladder hit — a band that widens until the least-resolved point passes
   is structurally impossible if the band is computed the DPW way, from the spread of *independent,
   systematically-refined* rungs, not from one rung's own noise.

### TMR flat-plate ladder (`demo-output/website/tmr/flatplate_sst.json`)

**What happened:** this ladder *is* already systematic in the sense MESH_STANDARD cares about —
4 rungs, geometric, constant `refinement_ratio_each_step: 2.0`, cells `[816, 3264, 13056, 52224]`.
But it never reached its asymptotic range: adding the 4th (finest) rung *moved* the observed order
from 1.0833 to 1.2587 — "the ladder is not yet in a strict asymptotic range and the GCI should be
read as an estimate rather than a bound" (verdict, verbatim, on record). GCI dropped from 2.09% to
0.70% only once the extra rung was appended reactively.

**What MESH_STANDARD requires instead:**
1. **Provision the full 6-level family up front**, not a 3-rung ladder extended reactively when
   Richardson extrapolation fails to settle. The DPW family's whole point is that 6 levels exist
   precisely because 3 is not reliably enough to detect a moving observed order before publishing a
   GCI number as if it were settled.
2. Even with 2× refinement per step (steeper than DPW's own diminishing `[(L+2)/(L+1)]³` ratio at
   higher L — DPW's step size *shrinks* as the family gets finer, ours stayed flat at 2×), the y+
   table in §b would have set Δy1 by a stated target at each level from the start, rather than
   discovering post hoc (as this lab's own `docs/standards/MESH_STANDARD.md` calibration table shows)
   that the fine grid happens to land at y+≈0.14.
3. Report the still-unsettled 0.70% GCI as **an IQR/std-style band, not a single number claimed
   precise** — the ladder's own verdict already says to read it as "an estimate rather than a bound";
   MESH_STANDARD's scatter convention (§c) is the concrete mechanism for saying that formally instead
   of as a caveat sentence.

**The point of this inheritance is that it outlives any single case.** Neither the 4412 ladder nor
the TMR ladder needs to be re-run to benefit from this — the next grid family built in this lab, for
any case, should be sized by a stated Level-indexed formula, resolved by a stated y+-anchored Δy1
table with a stated growth-rate ceiling, and reported as a band computed the DPW way, not a point
estimate defended by whichever rung happens to pass.

---

## Sources

- `demo-output/website/campaign/DPW8_AEPW4_SCOPING.md` (commit `e7bd737`) — located, verified-open,
  and first summarized the growth formula, y+ tables, and scatter conventions.
- [`gridding_guidelines_v3_07012024.pdf`](https://www.aiaa-dpw.org/ref/gridding_guidelines_v3_07012024.pdf) —
  primary source, fetched and text-extracted directly in this pass; §a and §b above are quoted from
  its own tables, not paraphrased secondhand.
- `docs/DPW-CRM-SCOPING.md` §2 — DPW-VI IQR/std precedent numbers, with its own citation to the
  DPW-VI statistical analysis (PMC7816761).
- `demo-output/website/OTHER_WORK_STATUS.md` (NACA 4412 ladder / Ladder C3 status) and
  `demo-output/website/ACTIVE_RESEARCH.md` — non-asymptotic verdict and self-referential-band finding.
- `demo-output/website/tmr/flatplate_sst.json`, field `convergence_extended` — TMR ladder's own
  observed-order-movement verdict.
- `docs/standards/MESH_STANDARD.md` (v1.2, 2026-08-11) — companion document, single-mesh quality
  gates (distinct scope, cross-referenced above).

---

## Free-surface families: the refinement direction must be declared

**This document's growth and scatter practice applies unchanged to marine
free-surface ladders, with one addition, which lives in the companion document
so it has one home:** `docs/standards/MESH_STANDARD.md` §7.3.

The short form of why, measured on the F7a dam break: refining dx and dy
together over a 64× cell-count range moved the graded deviation by **0.7
points**, while refining **dy alone** at fixed dx over a 4× range moved it by
**3.4 points**. On a stratified free-surface problem an isotropic family spends
its cells in the direction that does not matter, and a family built by this
document's growth formula alone would have concluded the case was converged when
it was not.

§7.3 therefore requires a free-surface ladder to declare its refinement
direction before it is built, and to include at least one rung that varies the
*other* direction at the finest spacing — because pushing one direction alone
introduces a cell-aspect-ratio artifact that is otherwise indistinguishable from
genuine convergence. See that section for the numbers and the case names.
