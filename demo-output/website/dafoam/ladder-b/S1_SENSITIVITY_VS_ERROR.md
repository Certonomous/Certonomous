# S1 — does the correction land where the model is wrong, or where the objective is sensitive?

**Research direction R1**, filed in `demo-output/website/campaign/RESEARCH_DIRECTIONS_2026-08.md`
at commit `6773c36f` as
`s1-does-the-correction-land-where-the-error-is-or-where-the-sensitivity-is`.
Executed 2026-08-11T21:52Z–21:59Z. **Zero solver compute**: every number below is arithmetic
over arrays written before this document was opened. No solver, no inversion, no container
was launched.

---

## 0. The null model first, and whether the result clears it

**It does not. The headline correlation is reported as INCONCLUSIVE, not as a verdict.**

R1's own §2a hazard was that a barely-moved inversion satisfies the correlation by
construction. The null model is β exactly one projected gradient step from 1:

```
beta_null = clip(1 - alpha * g(beta=1), 0.2, 4.0)
```

**Under that null the test statistic is pinned at its ceiling by arithmetic, not by fit.**
`|beta_null - 1| = alpha * |g|` is a strictly increasing function of `|g|`, so

| quantity | NULL value | how obtained |
| --- | --- | --- |
| Spearman ρ(\|β−1\|, \|g(β=1)\|) | **+1.0000** | identity — monotone map, no α to fit |
| top-decile overlap | **100.0%** | identity |
| Pearson r | +0.9827 (α from least squares) / +0.5639 (α from projected best fit) | α-dependent, bound clipping only |

**The null is not hypothetical here — this run's own first accepted iterate is exactly it.**
`beta_accept_iter001.npy` satisfies `beta_it1 = 1 − 1.0·g_total(β=1)` to a maximum absolute
residual of **1.110e-16** over all 21,000 cells, with the step length measured (not fitted) at
α = 1.000000. Scored against `|g(β=1)|` it returns Spearman **+1.0000**, Pearson **+1.0000**,
top-decile overlap **100.0%**. That is a positive control with nothing fitted in it.

**Measured, on the final field: Spearman ρ = +0.9742.**

R1 pre-declared the abort: *"If the measured field and the fitted first step agree beyond
ρ = 0.9, the run is declared TOO CLOSE TO ITS FIRST STEP and the comparison is inconclusive,
not a verdict."* Agreement between `|β_final − 1|` and `|β_null − 1|` is **+0.9742**.
**The abort fires.** It fires at the same time as the SENSITIVITY-DRIVEN verdict thresholds
(ρ ≥ 0.6 and overlap ≥ 40%, both met), and per R1's own text the abort dominates.

**So the correlation is not the finding, and this document does not present it as one.**
Section 3 answers R1's question by a route that has no null of this shape: the geography of the
sensitivity field measured **on its own**, with no reference to β at all. A barely-moved
inversion cannot manufacture that.

**One honest complication in the other direction.** The abort's premise — that the field has
barely moved — is measurably false. Section 2 records that `β_final` sits at cosine **+0.2125**
to `−g(β=1)`, has travelled **101.86×** the length of the first step, and has a per-cell gain
`|β−1|/|g|` spanning **73.7×** between its 10th and 90th percentiles where the null requires a
constant. The field is emphatically not its own first step. What survives the first step almost
intact is specifically the **rank ordering of correction magnitude**, and that is exactly the
quantity the test statistic uses. That coincidence is why the statistic cannot separate the two
readings and why sections 3–5 exist.

---

## 1. Provenance, and which evaluation every array comes from

Nine gradient arrays survive in the whole archive, as R1 recorded
(`invert_lbfgsb.py:97`: `if neval > 1 and neval % 10 != 0: os.remove(gpath)`). Enumerated by
`find`, executed 2026-08-11: `S1-cbfs-inversion/cbfs_inv/{grad_eval001, grad_eval010}`,
`S1-cbfs-reinversion/cbfs_inv/{grad_eval001, grad_eval010, grad_anchor, grad_anchor8}`,
`S1-cbfs-weighted-arm/cbfs_inv/{grad_eval001, grad_ext001, grad_anchorw}` — **nine, confirmed.**

**Every array used, with its evaluation named** (a mismatched-evaluation pairing produced a
spurious 1.684× discrepancy on this same run earlier the same day):

| symbol | file | run | evaluation | order |
| --- | --- | --- | --- | --- |
| `β_final` | `cbfs_inv/beta_final.npy` | S1-cbfs-**reinversion** | final accepted iterate = L-BFGS-B **iteration 11**, reached at **evaluation 16 of 16**; bitwise identical to `beta_accept_iter011.npy` (max diff 0.000e+00) | DV |
| `g(β=1)` | `cbfs_inv/grad_eval001.npy` | S1-cbfs-**reinversion** | **evaluation 1** | DV |
| `β_it1` | `cbfs_inv/beta_accept_iter001.npy` | S1-cbfs-**reinversion** | L-BFGS-B iteration 1 | DV |
| `g(eval10)` | `cbfs_inv/grad_eval010.npy` | S1-cbfs-**reinversion** | **evaluation 10** — auxiliary only, never mixed into a headline | DV |
| cell centres | `cbfs_inv/2500/C` | S1-cbfs-**reinversion** | final write-out (mesh is static) | serial |
| baseline `U`, LES `UData` | `cbfs_inv/0/{U,UData}` | S1-cbfs-**reinversion** | β = 1 baseline | serial |
| second arm | `cbfs_inv/{beta_final, grad_eval001}.npy` | S1-cbfs-**inversion** | evaluation 17 final / **evaluation 1** | DV |

**Eval 1 is the unperturbed state — confirmed, not assumed.** `J_history_main.csv` row 1 records
`penalty = LL2·Σ(β−1)² = 0.0000000000000000e+00` and `beta_min = beta_max = 1.000000`, which is
β ≡ 1 exactly. Independently, `grad_eval001.npy` is **bitwise identical** to the separately
measured `grad_anchor8.npy` (recomputed here: max abs diff **0.000e+00**), and
`‖g_total(eval 1)‖ = 1.9864e-01` against the driver's printed `1.986e-01`. The L2 leg of the
gradient, `2·LL2·(β−1)`, is identically zero at β = 1, so `g_total(β=1) = LQOI · g_varU`, and
both correlations are invariant to that positive scalar.

`grad_eval001` and `grad_eval010` differ by max **4.211e-05** — they are distinct evaluations,
not the same array under two names.

### 1a. The kill switch: permute-invert-assert

The gradient is in design-variable order and the fields are in serial cell order. R1 made this
step one and said the comparison stops here if it fails.

- `dv_to_serial_perm.npy` is a bijection on [0, 21000): **True**.
- `perm[inv] == arange` and `inv[perm] == arange`: **True, True**.
- `|beta_serial[perm] − beta_dv|max = 5.107e-15` — matching the record's 5.1e-15 control.
- `|beta_serial − beta_dv|max = 3.0000e+00` **unpermuted**, which is the evidence that the two
  orders genuinely differ and that the control is not vacuous.

**Control passes.** The map is `serial[perm[i]] = dv[i]`; cell centres for DV index *i* are
`C_serial[perm[i]]`. The same permutation transfers to the first inversion (same mesh, same
4-rank decomposition): `|fields_beta[perm] − beta_final_dv|max = 5.107e-15`.

### 1b. Both published gate values reproduce exactly

| arm | published G2 | reproduced here |
| --- | --- | --- |
| S1-cbfs-reinversion (after objective repair) | 26.8571% | **26.8571%** |
| S1-cbfs-inversion (before) | 29.0476% | **29.0476%** |

Top-decile split of `|β_final − 1|` for the reinversion: **39.6% upstream (x<0), 31.5% above the
shear layer (y>2), 26.9% in-window, 14.6% downstream** — the published split, recovered.
Window base rate 8.4429% of cells. 223 cells pinned at the lower bound, 1 at the upper.

**The four regions are not a partition.** `x<0` and `y>2` overlap: 4,995 of 21,000 cells sit in
two regions, so the top-decile shares sum above 100%. The published figures have the same
property and this document keeps the same definitions so the numbers are comparable.

---

## 2. The measurement, and every way the field departs from the null

**Whole domain, 21,000 cells — `|β_final − 1|` (eval 16) vs `|g(β=1)|` (eval 1):**

| statistic | measured | NULL | chance |
| --- | --- | --- | --- |
| **Spearman** | **+0.9742** | +1.0000 | −0.0003 ± 0.0071 |
| Pearson | +0.4899 | +0.5639 | — |
| Pearson on log₁₀ of both | +0.2946 | — | — |
| top-decile overlap | 71.90% | 100.0% | 10% |

**Spearman is the leg to trust and Pearson is reported because R1 asked for it.** `|β−1|` has
max/median = 2.68e+04 and `|g|` has max/median = 2.05e+06. A Pearson coefficient over
distributions with that dynamic range is a statement about a few hundred extreme cells, not
about the field; it moves from +0.49 to +0.97 across regions purely with the tail shape.

**By region** (Spearman / Pearson, with the null under the identical restriction):

| region | n | Spearman | Pearson | NULL Spearman |
| --- | --- | --- | --- | --- |
| in-window 0≤x≤6, 0≤y≤2 | 1,773 | +0.9400 | +0.5436 | +0.9994 |
| upstream x<0 | 6,750 | +0.9737 | +0.3688 | +1.0000 |
| above shear layer y>2 | 14,616 | +0.9674 | +0.8343 | +1.0000 |
| downstream x>6 & y≤2 | 2,856 | +0.9737 | +0.9693 | +1.0000 |

**No region behaves differently from the whole domain on the Spearman leg.** That was the
specific risk R1 named — a single whole-domain number hiding opposite behaviour — and it is not
realised. Pearson does swing hard by region, which is the second reason to distrust it here.

### 2a. Where the field is NOT its first step

| quantity | measured | NULL requires |
| --- | --- | --- |
| cosine(β_final − 1, −g(β=1)) | **+0.2125** | +1.0000 |
| ‖β_final − 1‖ / ‖β_it1 − 1‖ | **101.86** | 1.00 |
| Spearman(β_final, β_it1) as signed fields | +0.6949 | +1.0000 |
| Pearson(β_final, β_it1) as signed fields | +0.1957 | +1.0000 |
| per-cell gain `r = |β−1|/|g|`, p90/p10 | **73.7×** | 1.0 (constant) |
| sign(β_final−1) = sign(−g) | 71.84% (95.95% within the top decile) | 100% |
| ‖g‖ over the run | 1.9864e-01 → 1.5959e-02 (eval 1 → eval 10) | — |

**The run moved.** What did not move is the rank ordering of correction magnitude.

### 2b. Restricted range — the comparison that hurts the correlation most

Restricting to the cells that actually matter attenuates any correlation, so the **null is
subjected to the identical restriction**. The null barely moves, because it is an identity;
the measurement collapses.

| subset | n | MEASURED ρ | NULL ρ |
| --- | --- | --- | --- |
| all cells | 21,000 | +0.9742 | +1.0000 |
| **top decile of \|β−1\| — the 2,100 cells G2 actually scores** | 2,100 | **+0.4774** | +0.9991 |
| top decile of \|g\| | 2,100 | +0.6239 | +0.9991 |
| union of the two top deciles | 2,690 | +0.3814 | +0.9996 |
| intersection of the two top deciles | 1,510 | +0.5539 | +0.9976 |

**This is the sharpest negative result in the document, and it cuts against the sensitivity
reading.** Within the 2,100 cells the geography gate scores, the ordering of `|β−1|` is only
weakly related to the ordering of `|g|` (+0.477, inside R1's own UNDECIDED band of 0.3–0.6),
while the null stays at +0.9991. The +0.9742 whole-domain figure is carried by the ~19,000
cells where both quantities are negligible and decay together.

**So the correction and the sensitivity agree strongly on *which* cells matter (71.90% top-decile
overlap against a 10% chance level) and only weakly on *how much* each of them matters.** For
R1's question — which is about geography — the set-level agreement is the operative one.

### 2c. Controls

- **Positive control 1** — the null model, a field known to be a pure gradient step:
  Spearman **+1.0000**.
- **Positive control 2** — this run's own measured first iterate, nothing fitted:
  Spearman **+1.0000**.
- **Negative control** — `|β−1|` shuffled, 200 draws: mean **−0.00027**, sd 0.00708,
  |max| 0.0201.

The instrument returns ≈1 where a relation exists and ≈0 where none does. Rank-correlation
p-values are deliberately not quoted: both fields are spatially autocorrelated, so 21,000 cells
are not 21,000 independent samples.

---

## 3. The null-free leg — the sensitivity field's own geography

**This is the measurement that answers R1, and it never touches β.** `grad_eval001.npy` is the
adjoint gradient at the unperturbed field. Scoring **the published G2 definition** — top decile
by magnitude, same 2,100 cells, same window, same cell-centre test — on that array alone:

| field scored | G2 (bar >50%) | in-window | upstream x<0 | above shear y>2 | downstream |
| --- | --- | --- | --- | --- | --- |
| base rate (all cells) | — | 8.44% | 32.14% | 69.60% | 13.60% |
| **\|g(β=1)\| — no inversion result in it at all** | **35.38%** | 35.4% | **45.8%** | 9.8% | 12.5% |
| the null field (pure gradient step) | 35.38% | 35.4% | 45.8% | 9.8% | 12.5% |
| **\|β_final − 1\| (the published FAIL)** | **26.86%** | 26.9% | **39.6%** | 31.5% | 14.6% |
| per-cell baseline loss \|U(β=1) − U_LES\|² | 32.71% | 32.7% | 8.0% | 22.0% | 44.7% |

**Read the upstream column.** The 39.6%-upstream feature that the geography failure is built on
is present in the sensitivity map at **45.8%**, in an array containing no inversion result.
And it is absent from the loss, at **8.0%**. Whatever else is true, *the upstream deposition is
not independent evidence about where the closure is wrong* — a field derived from the baseline
adjoint alone reproduces it, and a field derived from the baseline error does not.

**The loss geography, recomputed from disk** (`0/U` vs `0/UData`, β = 1 baseline;
`varianceU = 6.15101e-04` against the driver's eval-1 `6.15090e-04`, agreeing to 1.8e-5
relative — the residual is the difference between the stored starting field and the same
solve reconverged at `primalTol 1e-8`):

| region | % of cells | % of loss | loss per cell |
| --- | --- | --- | --- |
| in-window | 8.44% | **41.2%** | ×4.88 |
| upstream x<0 | 32.14% | 8.4% | ×0.26 |
| above shear layer y>2 | 69.60% | 25.6% | ×0.37 |
| downstream x>6 & y≤2 | 13.60% | 32.2% | ×2.37 |

**41.2% on 8.44%** reproduces the re-inversion pre-registration's amendment D stage-A loss audit
exactly, from a different file by a different route. The window confirmation stands.

Cross-geography rank correlations: Spearman(`|g|`, loss) = **+0.4121**;
Spearman(`|β−1|`, loss) = **+0.3788**. Top-decile overlaps with the loss: `|g|` 33.4%,
`|β−1|` 39.9%. **The correction resembles the sensitivity map (71.9% overlap) far more than it
resembles the loss (39.9%).**

**Second arm, independent.** The pre-repair inversion's own eval-1 gradient — a different
baseline, a different objective normalisation, a different L2 weight — scores G2 = **31.19%**
on its own, and Spearman(`|g_inv|`, `|g_reinv|`) = **+0.9450**. Two independently computed
baseline sensitivity maps agree on the geography, and both fail the >50% bar without any
inversion having been run.

---

## 4. Two adversarial checks that had to come back clean, and one that did not

**Check A — is `|g|` just a mesh map?** Cell-wise adjoint gradients commonly scale with cell
volume, which would make the whole geography an artefact of refinement. The mesh is one cell
thick in z (1 unique z value); a local spacing proxy `h` from the mean distance to the four
nearest cell centres spans 8.3× across the domain.

- Spearman(`|g|`, area proxy `h²`) = **−0.8372**; Spearman(`|β−1|`, `h²`) = **−0.8655**.
  Both quantities are larger in smaller cells, and mesh refinement is a genuine shared driver.
- **But normalising it out changes nothing material.** `|g|/h²` scores G2 = **33.00%**
  (vs 35.38% raw), upstream **45.4%** (vs 45.8%), and Spearman(`|β−1|`, `|g|/h²`) = **+0.9792**
  (vs +0.9742). **The confound is real and is not the explanation.**

**Check B — is the correlation an artefact of the untouched far field?** Partly yes, and this is
the check that did *not* come back clean; it is reported in full as §2b. Whole-domain +0.9742
falls to +0.4774 inside the top decile of `|β−1|`.

**Check C — does the verdict rest on one gradient array?** Pairing `|β_final − 1|` with the
**eval-10** gradient instead gives Spearman +0.9925, and Spearman(`|g(eval1)|`, `|g(eval10)|`)
= +0.9741. Reported separately and never mixed into a headline, per the mismatched-evaluation
lesson.

---

## 5. Verdict

**On R1's headline statistic: INCONCLUSIVE.** ρ = +0.9742 against a null pinned at +1.0000 by
arithmetic, with the abort threshold at 0.9. The statistic does not clear its own null and is
not reported as a finding. R1's §2a hazard was correctly identified by its author and is
realised.

**On R1's question, answered by the null-free legs:**

**Reading 2 — "the inversion deposits its correction wherever the adjoint is loudest" — is
CONFIRMED as a description of the mechanism, on evidence independent of the correlation.** The
correction's geography is present in the baseline sensitivity map on its own (G2 = 35.38%,
45.8% upstream), reproduced by a second independently computed baseline gradient (31.19%,
ρ = +0.945 between the two), and survives normalisation by cell size (33.00%, 45.4%). The
top-decile sets agree at 71.90% against a 10% chance level.

**Reading 1 — "model-form error genuinely sits upstream" — is NOT refuted, and cannot be
refuted by this measurement.** Here is the complication R1's framing does not contain, and it
should be recorded rather than smoothed over: **the two readings are not disjoint.** The adjoint
is loud upstream *because* an upstream β perturbation propagates into the downstream loss
region — which is precisely the mechanism reading 1 posits when it says model-form error is
"set upstream by boundary-layer history and merely expressed in the bubble". A high `|g|`
upstream is partly a restatement of that physics, not an alternative to it. The loss geography
cannot arbitrate either, because loss is where error is *expressed*, not where the closure is
wrong.

**What is established, and it is narrower and firmer than either reading:**

> **The correction's geography carries essentially no information that is not already in the
> baseline sensitivity map.** A field built from `grad_eval001.npy` alone, with no inversion in
> it, reproduces the geography gate's failure and its upstream/above-shear-layer split. G2 as
> currently defined is therefore scoring the adjoint's sensitivity map, not the closure's error
> location, and **the upstream deposition may not be cited as a physical finding about where
> RANS closure fails.**

**A third result, not asked for, which falls out of the same arithmetic:**

> **G2's >50% bar sits above the ceiling that the loss itself can deliver.** The top decile of
> the **per-cell baseline loss** — a correction placed exactly where the model is wrong, the
> best case reading 1 could ever produce — lies **32.71%** in the window. No loss-following
> correction field can score above roughly that. The achieved 26.86% is **82% of that ceiling.**
> This sharpens `CLOSURE_STAGE1_AND_C2_STATUS.md`'s "41.2% loss-proportional ceiling" argument:
> the operative ceiling is the loss's own top-decile geography, 32.71%, not its total loss
> share, 41.2%.

---

## 6. What this means for R5 and R8

### R5 — the whitened re-inversion (340 core-min, filed): its enabling premise is measured FALSE

R5's §2a note states the hazard in its own words: *"Whitening by the sensitivity mechanically
pushes correction away from high-sensitivity cells; **if those cells happen to sit outside the
window**, G2 rises for a reason with nothing to do with turbulence."* R1 was filed as the
prerequisite that measures where the high-sensitivity cells are. **Measured:**

| region | base rate | share of top-decile \|g\| | enrichment |
| --- | --- | --- | --- |
| **in-window** | 8.44% | **35.4%** | **×4.19** |
| upstream x<0 | 32.14% | 45.8% | ×1.42 |
| above shear layer y>2 | 69.60% | 9.8% | ×0.14 |
| downstream x>6 & y≤2 | 13.60% | 12.5% | ×0.92 |

**The high-sensitivity cells are enriched INSIDE the window by 4.19×, the largest enrichment of
any region.** R5's "if" is false. And the cells whitening *sends* the correction to — the bottom
decile of `|g|` — are **90.0% above the shear layer and 1.8% in-window (×0.21)**.

**Directional prediction: whitening moves G2 down from 26.86%, not up toward 50%.** This is a
first-order, single-step prediction from the sensitivity map; it does not simulate a converged
bound-constrained arm, and it should not be quoted as one. Two further measurements point the
same way and do not depend on the first-order argument: the converged inversion is **already
less window-concentrated than its own sensitivity map** (26.86% vs 35.38%), and its per-cell
gain `|β−1|/|g|` is **0.582× the global median inside the window** against 1.322× downstream —
the part of the correction that is *not* explained by the gradient is being deposited away from
the window, with a mean rank shift of **−1,029 cells (−4.90% of N)** in-window.

**Recommendation: R5 should not be bought at 340 core-min in its current form.** Three separate
measurements say the whitened arm's G-W2 fails, and one says it cannot pass regardless: a
correction placed exactly on the loss scores 32.71%, so **no** regularisation choice reaches
>50% while following the loss. R5's G-W1 reproduction control is separately vindicated — both
archived G2 values reproduce here at zero compute, so that leg is already discharged.

### R8 — the physics-informed transferable prior (unpriced, not filed): condition (a) is not met

R8 requires *"(a) The correction geography is physical, not the adjoint's sensitivity map —
**R1 decides this, at zero compute**"*, and R8's proposed prior is *"β departs from 1 in the
separated shear layer and nowhere else"*.

**Both fail against the measurement.** The correction geography is reproduced by the adjoint's
sensitivity map alone, so condition (a) is not met. And the prior's proposed *shape* is
contradicted by the data it would be fitted to: neither the correction (26.9% in-window, 39.6%
upstream) nor the sensitivity (35.4% / 45.8%) concentrates in the shear layer and nowhere else.

There is a subtlety worth recording rather than hiding. R8's §2a hard constraint is that the
marker be *"computable from the baseline β = 1 solve alone, before any inversion"* — and
`|g(β=1)|` satisfies that constraint exactly. So a prior keyed to the sensitivity map would be
legal under R8's own rule. **But it would be R5's whitening with the sign of the argument
reversed, and it would encode "β departs from 1 upstream and above the step", which is not the
structure R8 proposes and is not obviously transferable to the hump.**

**Recommendation: R8 should not enter the ambition slot on this basis.** Its stated enabling
condition is measured absent. It remains blocked independently behind the uncharacterised hump
adjoint.

### What would actually separate the two readings

The correlation cannot, and this document says so rather than forcing a number. What would:

1. **A second sensitivity map from a different objective.** If `|g|` computed against a
   *different* QoI (e.g. reattachment length, or wall shear over the step face) has a different
   geography, and the correction inverted against that QoI follows the new `|g|` rather than
   staying put, the correction is sensitivity-driven with no ambiguity. If the two corrections
   land in the same place despite different sensitivity maps, that place is physical. **This is
   the discriminating experiment and it does not exist in the archive.**
2. **A second configuration.** Model-form error set by boundary-layer history should move with
   the boundary layer; an adjoint artefact should move with the objective. The hump is the
   natural second case and is blocked behind its adjoint.

---

## 7. Priced requests

**One, and it is the only thing this document asks for.**

**PR-1 — a second-QoI sensitivity map on CBFS at β = 1.** One cold primal plus one adjoint at
`primalTol 1e-8` against a second objective, writing `grad` only. The measured basis on this
exact operation, from `S1-cbfs-reinversion/ledger.csv`: the `anchor8` evaluation took
**599 s wall at 2 cores = 19.97 core-min**, and the 16 driver evaluations billed 18.77–21.37
core-min each (mean 20.0). **Priced at 25 core-min** to carry contention and one retry of the
objective definition. Basis gross, measured, same container and same tolerance.

This buys the first half of the discriminating experiment in §6 — the geography of a second
sensitivity map — without buying the inversion behind it. If the second map's geography matches
the first, reading 2 is confirmed outright and R5/R8 are closed. If it differs, the second half
(a full inversion against the second QoI, ~340 core-min on the same measured basis) becomes
worth pricing and R8's premise is back in play.

**Nothing else is requested.** No inversion, no whitened arm, no container was launched for this
document.

---

## 8. Reproduction

Four scripts, host-side, numpy 2.5.1 + scipy 1.18.0 only, ~40 s total, no solver, archived with
their full output under `S1_work/scripts/` and `S1_work/logs/`:
`r1_sens_vs_error.py` (provenance, permutation control, null model, correlations, controls,
second arm), `r1_geography.py` (loss / sensitivity / correction geographies, gain, cosine),
`r1_confounds.py` (cell-size confound, far-field restriction, pre-registered thresholds),
`r1_final.py` (restricted-range vs null, R5 prediction, the G2 ceiling).
Every input path is listed in §1 and every array is on disk outside the repo at
`/home/ubuntu/certonomous-runs/S1-cbfs-{inversion,reinversion}/`.

Frame: cell-centre coordinates in step heights, window `0 ≤ x/h ≤ 6, 0 ≤ y/h ≤ 2`.
Filter: all 21,000 cells unless a region or quantile restriction is named at the point of use.
Executed against repo commit `a8401614`; R1 as filed at `6773c36f`; the reinversion arrays as
written 2026-08-07/08 and unmodified since.
