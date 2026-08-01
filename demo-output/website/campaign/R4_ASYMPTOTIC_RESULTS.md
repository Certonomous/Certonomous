# R4 — result: the Ahmed ladder is non-monotone, and it is not the refinement ratio

Companion to `R4_PREREGISTRATION.md`, which was committed (`6cdf8a41`) before
any solver was launched. Every gate, prediction and rank count below was fixed
in that file; nothing in it has been edited.

Docket item `r4-asymptotic-range-ladders`.

---

## 1. The measured ladder

Five rungs, one mesh recipe, the background blockMesh division triple the only
knob. **4 MPI ranks on every rung**, scotch decomposition, identical across
rungs. Cd is the lab's own convention — mean over the final 20% of the force
history (`head_engineer.envelope_statistics`).

| rung | divisions | cells | iters to `residualControl` | Cd | 2σ over its window |
| --- | --- | --- | --- | --- | --- |
| c1 | (60 13 36) | 79 439 | 158 | **0.084801801** | 9.9e-06 |
| c2 | (78 17 47) | 144 240 | 212 | **0.079359699** | 5.5e-05 |
| c3 | (98 21 59) | 254 911 | 220 | **0.073992743** | 7.6e-05 |
| c4 | (122 26 74) | 454 691 | 623 | **0.074882228** | 1.5e-05 |
| c4b *(replicate control, §4)* | (123 27 73) | 468 509 | 1668 | **0.074979080** | 2.1e-05 |
| c5 | (152 32 92) | 834 351 | *(still solving at the time of writing — §7)* | | |

Refinement ratios in h: **1.2200, 1.2090, 1.2128** — the widest pair 0.90%
apart, against the existing Ahmed ladder's 7.85%. Every mesh reports `Mesh OK`
from checkMesh with max non-orthogonality 45.0–49.4 and max skewness 1.35–3.12.

Force histories: `campaign/R4_runs/c*/postProcessing/forceCoeffs1/0/coefficient.dat`.
Solver logs: `campaign/R4_runs/c*/log.simpleFoam`. Job records:
`solve_registry/r4-ahmed-ladder_20260801T123000Z.done`,
`r4-ahmed-c4_20260801T123350Z.done`, `r4-ahmed-c5_20260801T124353Z.done`.

## 2. The gates, scored

**G1 — the experiment worked. MET.** 0.90% ratio mismatch, fixed and recorded
before solving.

**G2 — the increments are signal. MET, with margin.** The largest per-rung 2σ
is 7.6e-05; the smallest ladder increment is 8.89e-04. The noise is **1.4% to
8.6%** of the increment it would have to fake, against a 10% gate. Two further
controls, neither pre-registered and both reported because they were run:

* *Run-to-run reproducibility.* c1 returns **0.0848018** where three earlier
  independent runs of the identical setup gave 0.0848123 / 0.0848083 /
  0.0848000 (`R4_PREREGISTRATION.md` §2). The new value lands inside that
  spread. The recipe was rebuilt, not re-invented — and c1's cell count is
  79 439, the stored production rung's count to the cell.
* *Drift at the stopping point.* Comparing each rung's final-30 window against
  the 30 before it: c1 −8.3e-05, c2 +2.8e-05, c3 −8.6e-05, c4 +4.7e-06 — that
  is 0.5% to 1.6% of the increment each rung contributes, and the sign
  alternates. `residualControl` did not stop any rung mid-slide in a direction
  that could manufacture the ladder.

**G3 — the question. G3-B, and more sharply than G3-B was written.**

**G4 — the pre-registered prediction. SCORED FALSE.** It was written as three
parts and it is recorded as one prediction, failed:

| predicted | measured | |
| --- | --- | --- |
| Cd(c2), Cd(c3) both below Cd(c1) | 0.07936 and 0.07399 against 0.08480 | true |
| shrinking increments | −5.442e-03 then −5.367e-03 — 1.4% apart, not shrinking in any useful sense | technically true, materially false |
| phi0 pulled back above 0.0733 | **phi0 = −0.0845** | **false** |

The prediction stays as written. The extrapolation did not pull back towards
the data; it ran away from it into a negative drag coefficient.

## 3. What the ladder actually does

Increments, rung to rung: **−5.442e-03, −5.367e-03, +8.895e-04.**

The first two are equal to within 1.4%. Equal increments under uniform
refinement are the signature of an observed order of **p ≈ 0** — the fit on
(c1, c2, c3) returns **p = 0.175**, outside the credible window [0.5, 2.5], and
its Richardson extrapolation is **−0.0845**, a negative drag coefficient. The
guard that holds the verdict changes from the stored ladder's
`extrapolation_sanity` to `order_window`, which is a more basic failure: there
is no credible order to extrapolate with.

Then the fourth rung **turns around.** Handed (c2, c3, c4), or all four,
`uq.eca_hoekstra_band` returns `monotone: False` and refuses an order at all —
`not_conclusive_reason`: *"the three rungs do not move one way under
refinement."*

**That answers the item.** The proposal offered two explanations for the Ahmed
body's non-asymptotic verdict: an insufficient refinement ratio, or genuinely
non-monotone grid convergence. With the ratio made constant to 0.90%, the
recipe held fixed, every rung solved at the same rank count, the increments 12×
to 70× above the measured noise floor and no rung stopped mid-drift, **the
ladder is non-monotone.** It is the second explanation, and it is now measured
rather than inferred from a ladder whose ratios were 7.85% apart and whose first
two rungs came from a different mesh family.

## 4. What it is not

* **Not iterative noise** (G2, two ways).
* **Not the wall-function regime switching.** y+ on the body averages 331.5 /
  309.0 / 294.6 / 255.1 across c1–c4 (`log.yPlus` in each rung). It falls
  monotonically and by only 23% across a 5.7× change in cell count, and stays
  inside the log-layer regime throughout. This was checked because it is the
  obvious confound for a snapped-hex ladder; it does not explain the turn.
* **Not mesh degradation at the fine end.** c4's max non-orthogonality is 48.9
  and max skewness 1.49 — better than c1's 45.0/3.12 on skewness, comparable on
  non-orthogonality, and `Mesh OK` throughout.
* **Not a decomposition artefact.** Every rung ran at 4 ranks. The stored
  production rung was solved at a different decomposition, which is exactly why
  c1 was re-solved rather than reused.
* **Not one unlucky mesh.** This one was not pre-registered — it was run because
  the turn-up is the whole finding and a single mesh should not carry it. **c4b**
  is an independent mesh at the same resolution: divisions (123 27 73) against
  c4's (122 26 74), **468 509 cells** against 454 691, built by the same recipe,
  solved at the same 4 ranks.

  | | cells | iters | Cd |
  | --- | --- | --- | --- |
  | c4 | 454 691 | 623 | 0.074882228 |
  | **c4b** | **468 509** | **1668** | **0.074979080** |

  They differ by **9.7e-05 — 0.13% of the value, and 11% of the c3→c4 increment
  the turn consists of.** Two independently generated meshes at that resolution
  both put Cd back above c3. The turn is a property of the resolution, not of a
  particular mesh. (c4b needed 2.7× the iterations to reach the same
  `residualControl`, which is worth noting and is not explained: the two meshes
  are equally clean by checkMesh — c4b max non-orthogonality 47.7, max skewness
  3.24.)

## 5. The B-52 was not re-run, and the reason is in the pre-registration

Its fitted triple already carries a constant ratio (1.0903 against 1.0962,
0.54% apart), so "re-run it with a constant ratio" is a no-op on that body. The
six-rung sequence the proposal's rationale quotes as non-monotone is two mesh
families by `b52.json`'s own `recipe_audit`. What is true of the B-52 is that
r = 1.09 amplifies its finest increment 4.65× into the extrapolation against
1.24× at r = 1.30 — and that its increments are 253× its own measured iterative
2σ, so there is real signal being amplified, not noise. **The premise was
corrected rather than built on.**

## 6. The consequence nobody asked for: the experimental agreement passes *through* the experiment

The item was scoped to grid convergence. Rebasing the same rungs onto the
frontal-area basis the Ahmed record compares on — the ratio the whole record
already uses, 0.401696 / 0.112 = 3.5865714, applied identically to every rung so
it cancels — produces this, against Ahmed, Ramm and Faltin 1984, SAE 840300,
**Cd = 0.285**:

| cells | Cd, frontal basis | vs experiment |
| --- | --- | --- |
| 45 753 — **the rung the VALIDATED tier is recorded on** | 0.3219 | **+12.95%** |
| 79 439 (c1) | 0.3041 | +6.72% |
| 144 240 (c2) | **0.2846** | **−0.13%** |
| 254 911 (c3) | 0.2654 | −6.88% |
| 454 691 (c4) | 0.2686 | −5.76% |

`models/curriculum/results/ahmed_25.json` records `"tier": "VALIDATED"` with
`"relative_error": 0.1295` and `"reason": "within 13% of Ahmed, Ramm & Faltin
1984 ... (band ±15%)"`, measured on 45 753 cells.

**That rung is the worst agreement of any mesh in this ladder.** The solution
does not converge towards the measurement; it passes through it near 144 000
cells and comes out the other side. A reader refining this case can obtain any
error between −6.9% and +13.0% and every one of them is a converged, `Mesh OK`,
residual-gated solve.

Three things follow, and the third is the one that matters:

1. The proposal's rationale states the Ahmed body is "held back from the
   validated tier specifically because its ladder was inconclusive."
   **That is false** — `results/ahmed_25.json` has tiered it VALIDATED since
   2026-07-23. Recorded here rather than worked around.
2. **The correct verdict is still not-conclusive, and this ladder makes the case
   for that stronger, not weaker.** A non-monotone ladder cannot support an
   extrapolated band, so the conservative treatment the study file already
   applies is the right one. Nothing here argues for moving Ahmed *up*. The act
   itself already says so — `campaign/NINE_ACT_GATE_TABLE.md:24-26` records the
   act's own solver-backed verdict as *"inconclusive refinement study, not
   enough to call it validated"* and instructs that it be kept. **This ladder
   sides with the act against the tier file**, and the disagreement between the
   two is now measured rather than latent.
3. **The +6.73% over-prediction that `W3_AHMED_PREREGISTRATION.md` built its
   band-containment test around is a property of the 79 439-cell mesh, not of
   the closure.** W3's test is not automatically wrong — a band wide enough to
   contain 0.285 still contains it — but "our uncertainty machinery predicted a
   known model error" reads differently when the model error changes sign under
   refinement. That is for W3's owner to weigh; it is flagged, not decided here.

**`models/curriculum/results/ahmed_25.json` and
`models/curriculum/uq-studies/ahmed_25.json` were NOT edited by this item.**
Both were already modified in the working tree by another agent when this work
started, and a tier is a judgement about what a lab is willing to stand behind,
not an arithmetic result. The numbers are on the record; the decision is not
this item's to take.

## 7. Cost, against the estimate

`est_core_min` for this item was **400.0**, and it was ruled unaffordable.

| stage | ranks | measured |
| --- | --- | --- |
| meshing, c1+c2+c3 concurrent | 1 each | 44.6 s wall, **1.21 core-min** |
| c3 re-mesh + c4 + c5 meshing | 1 each | **≈2.6 core-min** |
| c1 solve (potentialFoam + simpleFoam) | 4 | 12.6 s wall, **0.84 core-min** |
| c2 solve | 4 | 29.9 s, **2.00 core-min** |
| c3 solve | 4 | 50.8 s, **3.39 core-min** |
| c4 solve | 4 | 251.1 s, **16.74 core-min** |
| c4b solve (replicate control) | 4 | 1054.4 s, **70.30 core-min** |
| c5 solve (834 351 cells) | 4 | still running; **its wall clock is not comparable** — it shared the box with the W5 gradient runs and the load average sat near 20 on 16 cores |

Through c4 the item cost **under 27 core-minutes against an estimate of 400** —
a factor of 15. With the two unplanned extras (c4b's replicate control and c5)
it is still comfortably inside the estimate, and the two extras exist *because*
the first four rungs were that cheap: the budget bought controls instead of
buying nothing. The estimate's basis was "the B-52's own 1,267-second
and motorBike's 1,022-second rebuild times", i.e. it was priced on *mesh
generation for a different body*, and the Ahmed body meshes in 15 seconds a
rung. That is worth recording as a fact about the estimator, not only about this
item: the four items this batch came from were ranked last on estimates of this
construction.
