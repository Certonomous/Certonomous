# W2 reading — Zhao et al., CFD-driven training: the paper that prices the expensive step

Date: 2026-08-02 (UTC). **Zero compute** for the reading itself; the one cost
cross-check below reuses an iteration rate measured tonight on a rung that was
already running for another item.

Lead 3 on the seed list `W2_TBNN_SPARTA_READING.md` left behind, and the reason
it was named there was exactly this: SpaRTA cites it as the approach that puts
CFD *inside* the model search, which *"increases the costs of the model search
drastically"*. The lab's standing complaint about both closure papers read so
far is that they **price the cheap step and hide the expensive one**. This paper
is the counter-example, and that is the headline.

---

## 0. The artifact

**Y. Zhao, H. D. Akolekar, J. Weatheritt, V. Michelassi & R. D. Sandberg, "RANS
Turbulence Model Development using CFD-Driven Machine Learning", *Journal of
Computational Physics* (2020).** arXiv `1902.09075v2`, dated 24 March 2020.

**Tier: READ IN FULL.** Fetched 2026-08-02 from `https://arxiv.org/pdf/1902.09075`,
HTTP 200, no library access needed and none attempted — the arXiv identifier was
on the seed list and it resolved. Held at
`docs/papers/zhao_akolekar_weatheritt_michelassi_sandberg_1902.09075.pdf` with a
text extraction alongside. The version read is the arXiv v2, which carries the
JCP (2020) header; it is labelled here as that version and not as the publisher's
version of record.

---

## 1. Claim / source / where-it-applies

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| **The cost of the CFD-in-the-loop search is stated, in the paper, in the unit that matters**: *"the CFD-driven training in the present study typically requires O(10³) CPU hours which is more computationally expensive than the frozen training."* | Zhao et al. 2020, §3.2, READ IN FULL. | Any comparison of model-search methods on cost. **This is the disclosure the other two closure papers do not make**, and it is one sentence long. | It is an order of magnitude, not a measurement with a machine attached: no core count, no wall clock, no per-evaluation figure. §3 below turns it into something this lab can act on. |
| The cost mechanism is named, not buried: *"the candidate models in GEP need to iterate through hundreds or thousands of generations to get the desired models, and for each generation the CFD calculations have to be performed. Therefore, it is essential that the integrated CFD solver is highly efficient."* | Same, §4.2, READ IN FULL. | Reading any "our model selection takes a minute on a laptop" claim. The generations are the cost and the solver is the multiplier. | The paper does not state the population size used for the CFD-driven runs specifically. §2.2 gives a GEP population of 1000, in the general description; whether the CFD-driven search used that number is not said. |
| **The Hi-Fi data requirement is sparse, and that is the methodological point.** The cost function needs only the kinetic loss profile `ω(y)` at **two axial locations**, `x₁ = 1.15 Cax` and `x₂ = 1.25 Cax`: *"the Hi-Fi data needed for the computation of the CFD-driven cost function J_CFD only needs to include the kinetic loss profiles ω_HiFi(y) at these two locations."* | Same, §3.2 and Eqn. 13, READ IN FULL. | **This is the property that matters most to this lab.** Frozen/TBNN-style training needs dense per-cell Reynolds-stress fields; this needs a mean-flow profile at two stations. A lab with sparse experimental data and a working solver can run this shape of search where it cannot run the other. | It buys flexibility, not free lunch: the sparse data is compensated for by running the solver thousands of times, which is where the O(10³) CPU hours went. |
| The trained model is **simpler** than the frozen-trained model on the same data. CFD-driven: coefficients `(−2.57 + I₁)`, `4.0`, `(−0.11 + 0.09I₁I₂ + I₁I₂²)`. Frozen, same Hi-Fi data: polynomials with coefficients to `304.979` and `−184.519`. | Same, Eqn. 14, READ IN FULL. | An argument that optimising in the environment the model will live in produces a better-conditioned model than fitting it outside that environment. | It is one comparison on one case, and the paper presents it as an observation, not as a proved property of the method. |
| **The basis is three tensors and two invariants** — `V¹, V², V³` with `I₁, I₂`. | Same, Eqn. 14, READ IN FULL. | It is Pope's two-dimensional reduction, the same three-tensor set SpaRTA restricts itself to. A third paper on the same foundation this lab read on 2026-08-02. | Consistent with the flows: turbine cascades treated as two-dimensional. Nothing here exercises the higher tensors, so nothing here bears on the ten-coefficient identifiability question in `W2_POPE_1975_INTEGRITY_BASIS.md` §2.2. |
| **The model is zonal and the authors say so plainly**: it is applied only inside a wake mask (`k > 5% k_max` and `x > 1.05`), with `k−ω SST` + `γ−Re_θ` everywhere else. *"we should not expect a model with a unified set of parameters to show good performance for different kinds of flow phenomena."* | Same, §3.2 and §4.2, READ IN FULL. | The fourth column, written by the authors themselves. A wake-mixing model, in wake regions of turbomachinery flows. | Explicitly **not** claimed for the whole domain, for boundary layers, separation or transition. Any citation of this as a general closure would be citing something the paper refuses to say. |
| Applying the trained model costs **~5%** over the baseline linear model in the RANS calculations. | Same, §3.2, READ IN FULL. | The deployment cost, as distinct from the training cost. The expensive step is the search, not the model. | "for the present cases". |
| Each candidate's CFD run is **200 steps, initialised from a baseline flow field**, converged to RMS continuity residual below 1e−7. | Same, §3.2, READ IN FULL. | Reconstructing the cost, and the reason the search is affordable at all: the seed skips the transient. | See §3 — this lab measured tonight that a seed of exactly this kind saves 8.7% of iterations, not a factor, on its own bump case. The 200-step budget is a claim about the authors' solver and case, not a transferable number. |

---

## 2. Reproduction verdict: not reproducible here, and this is the third paper with the same cause

**Nothing in this paper is reproducible in this lab, and the reason is the data
and the solver, not the method.**

- **The Hi-Fi data** is *"provided from previous DNS and high-resolution LES
  using code HiPSTAR"* — the authors' own group's simulations (their refs 24,
  25, 26). No public archive is named and the paper carries no data-availability
  statement.
- **The RANS solver is TRAF** (their ref 27), an in-house code this lab does not
  have and cannot substitute for without changing what was measured.
- **The cases are turbine cascades** — VKI LS89 HPT and T106A LPT, training on
  HPT case A at `Re = 0.57×10⁶`, `Ma_exit = 0.9`, with transition and shocks, on
  a 705×65 + 101×161 O–H mesh. This lab has no turbine cascade case, no
  transition model in the loop, and no Hi-Fi wake data.

**The pattern is now worth naming.** Of the three closure-method papers this lab
has read in full, **two fail reproduction on the same cause** — training data
that is the authors' own unarchived simulations:

| Paper | Reproducible here? | Blocker |
| --- | --- | --- |
| Ling, Kurzawski & Templeton 2016 (TBNN) | **No** | two of six training flows are internal simulations with no public archive named |
| Schmelzer, Dwight & Cinnella 2020 (SpaRTA) | **Yes, and reproduced** | none; its data is in the benchmark tree |
| Zhao et al. 2020 (CFD-driven) | **No** | HiPSTAR DNS/LES with no public archive, plus an in-house RANS solver |

That is not a complaint about any of them. It is a statement about what a lab
without those groups' archives can and cannot check, and it is the reason
SpaRTA was the one that got reproduced.

---

## 3. What the cost means on this box, which the paper cannot say and we can

The paper's `O(10³) CPU hours` is an order of magnitude with no machine
attached. Converted at this lab's own **measured** rates:

| at | 1,000 CPU-hours = 60,000 core-minutes is |
| --- | --- |
| 11.06 cores sustained under MPI | **90 wall-hours — 3.8 days of the whole box** |
| 3.02 cores, busy mean | 331 wall-hours — 13.8 days |
| 1.40 cores, long-run mean | 714 wall-hours — **29.8 days** |

And a cross-check on the per-evaluation cost, grounded in this lab's own
instrument rather than in the paper's. The turbine meshes are 705×65 + 101×161
≈ **62,000 cells**, which is 10.2% larger than the 56,320-cell bump rung this lab
had running tonight. That rung measures **0.63 s/iteration serial** at 56,320
cells/rank (`W1_runs/fine`, extension log, 2026-08-02). At that rate a 200-step
candidate evaluation is about **2.1 core-minutes**, so `O(10³)` CPU hours buys
roughly **28,000 candidate evaluations** — consistent with a few hundred
generations of a few hundred candidates, which is what §4.2 describes.

*(The mesh comparison is 62,086 against 56,320 cells — 10.2% larger, not
"comparable" by hand-wave. The rate is quoted from the coarser of the two, so
the per-evaluation figure is if anything an under-estimate.)*

**The conclusion that follows is a decision, not a complaint.** A CFD-driven
model search at the published scale is between four days and a month of this
entire box. Nothing in the approved queue is priced anywhere near that, and the
whole of tonight's W1 queue after triage is 647 core-minutes — **1.1% of one
such search**. That is the number anybody proposing this method here has to
answer, and it is now on the record before anybody proposes it.

---

## 4. Charter section 6 — which trigger fired

- **Trigger 2 (a method whose admissibility could be written as thresholds):
  FIRED.** Proposal filed, `w2-cfd-driven-search-costed-before-proposed`.
- **Trigger 1 (a number on a case we can build): did not fire.** Every number in
  the paper is on a turbine cascade with in-house Hi-Fi data. There is no case
  here to build.
- **Trigger 3 (disagrees with one of our results): did not fire.** It touches
  nothing we have measured.
- **Trigger 4 (limit case checkable at zero compute): did not fire.** The paper
  offers no correlation with a stated range and no closed-form limit.

---

## Related

- `demo-output/website/campaign/W2_TBNN_SPARTA_READING.md` — the seed list this
  came off, and the two papers it compares against.
- `demo-output/website/campaign/W2_POPE_1975_INTEGRITY_BASIS.md` — the basis all
  three papers use.
- `demo-output/website/campaign/W1_bump_nasa_grids.md` §4 — the seeding control
  and the 0.63 s/iteration rate used in §3 above.


---

## Paper-library forwarding note — appended 2026-08-18

**Nothing above this line was edited.** The `docs/papers/` paths cited above were
correct when the sentences carrying them were written. Commit `5c0d2483`
(2026-08-18) refiled the paper library into topic subdirectories and renamed most
of its files, and `4323d7e3` lowercased two of the new names afterwards. Those
citations were left exactly as they stood, because each records where a file was
at the moment its statement was made; rewriting one would have changed what this
record says happened.

Each pair below was resolved by **git blob identity** — the old path's blob hash
matched to the path carrying the identical hash — and not by name similarity, and
each destination was then confirmed against the filesystem at commit `4323d7e3`.

| as cited above | the same bytes, as of `4323d7e3` |
| --- | --- |
| `docs/papers/zhao_akolekar_weatheritt_michelassi_sandberg_1902.09075.pdf` | `docs/papers/data_driven_rans/zhao_akolekar_weatheritt_michelassi_sandberg_1902.09075.pdf` |

The whole 87-path table was appended to `docs/papers/README.md` in the same
commit. `python3 scripts/check_paper_citations.py` re-derives the rows above and
exits non-zero if any destination stops resolving.
