# F6d random-matrix ensemble — convergence audit

**Date:** 2026-08-11 · **Status:** forensic audit, read-only. No case file, run
tree, or published record was modified. **The remedy is a decision for the F6d
owners, not an edit, and none was made.**

**Scope.** An agent pricing an unrelated proposal reported three numbers about
`demo-output/website/dafoam/f6d_random_matrix_uq`. This audit re-measured all
three from the run tree with independent instruments, then asked the question
that actually matters: **what published claims rest on them, and which of those
claims survive.**

---

## 0. Frame, stated before any count

Every count below is over the **84 directories under
`f6d_random_matrix_uq/ens/`**, each of which holds one `system/fvSolution` and
one `log.simpleFoam`. That set is:

| group | n | what it is |
| --- | --- | --- |
| `d0.2_s000…s039` | 40 | random-matrix members, δ = 0.2 (paper Case 1) |
| `d0.6_s000…s039` | 40 | random-matrix members, δ = 0.6 (paper Case 2) |
| `corner_oneC/twoC/threeC` | 3 | eigenspace corner union — the **comparator** |
| `null` | 1 | control, `R_sample = R_bar` |
| **total** | **84** | |

**This frame matters and the reported "84 members" slightly overstates the
published band.** The published bands are computed over **80** members (40 + 40);
the other 4 are the comparator and the control. Statements below say which set
they apply to.

All 84 share **byte-identical** `system/fvSolution` and `system/controlDict`
(`md5sum` over all 84 returns exactly one hash for each file). So this is one
configuration applied 84 times, not 84 independent choices.

---

## 1. The three reported numbers, re-measured

### 1.1 — `residualControl { p 1e-15; }` unreachable in 84 of 84 — **CONFIRMED**

Measured with a purpose-built `fvSolution` dict parser rather than a text
grep, because the discriminating test is a **relation the case states about
itself**: a `residualControl` target at or below *its own field's* linear-solver
`tolerance` can never be reached, and both numbers live in the same file. No
external constant is involved.

```
solvers { p { solver GAMG; tolerance 1e-12; … } }   ← what the linear solve reaches
SIMPLE  { residualControl { p 1e-15; } }            ← what SIMPLE waits for
```

**Result: 84 of 84, every one the same shape — target `1e-15` against its own
solver tolerance `1e-12`.** Zero cases in the ensemble are reachable, zero are
undecidable.

**Parser controls** (synthetic files with known answers, all passed):

| control | expected | got |
| --- | --- | --- |
| A — target 1e-15, tol 1e-12 | UNREACHABLE | UNREACHABLE |
| B — target 1e-4, tol 1e-8/1e-9 | **must not fire** | reachable, reachable |
| C — no `residualControl` block | **must not fire** | no findings |
| D — target *equal* to tol | UNREACHABLE (boundary) | UNREACHABLE |
| E — regex keys `"(k\|omega)"` on both sides | k, omega unreachable; p, U reachable | exactly that |

B and C are the negative controls: the instrument is capable of returning
"reachable", so "84 of 84 unreachable" is a finding and not a stuck needle.

### 1.2 — 0 of 84 print a convergence sentence — **CONFIRMED, with a positive control, and one refinement that matters**

`SIMPLE solution converged in N iterations` appears **0 times** across all 84
logs. Also 0 for a case-insensitive search on the bare word `converged`. No
compressed logs exist anywhere under `f6d_random_matrix_uq` (`find` for
`*.gz`/`*.bz2`/`*.xz` returns nothing), so nothing is hiding from the reader.

**Positive controls — this is exactly the shape of failure where a zero must be
defended, so it carries two:**

1. **Version-matched corpus control.** The same sentence appears in **75 other
   logs in this repo**, of which **65 are the identical `OPENFOAM=2606` build**
   that ran this ensemble. The sentence is printable by this solver.
2. **Spliced control — same instrument, same invocation.** Concatenating all 84
   ensemble logs *plus one known-converged log* and running the identical
   `grep -c` returns **1**. The same command that returns 0 on the 84 returns 1
   the moment a converging run is added. The zero is real, not blindness.

**Refinement, and it cuts both ways.** The absent sentence is a **true**
negative for 83 of the 84 and a **false** negative for exactly one — the `null`
control, which *is* converged (final Ux initial residual **1.57e-5**, and it
reproduces the baseline reattachment to 5 significant figures, 7.643814 vs
7.643915). So the "known false negative" reasoning inherited from F6b is sound
for the control and **unsound for the 80 members the bands are built from**.
This is the crux of §3.

### 1.3 — momentum residual rising over the second half in 76 of 84 — **CONFIRMED, and reproduced to three digits**

Definition that reproduces the reported number: for the **Ux initial-residual**
series, ratio = (value at final iteration) ÷ (value at the midpoint iteration);
"rising" is ratio > 1.

**Result: 76 of 84 rising, worst 9.938× — matching the reported 76 and 9.94×.**
The worst is `d0.6_s011`.

Robustness across alternative definitions (the conclusion does not depend on the
choice):

| definition | field | rising | worst |
| --- | --- | --- | --- |
| endpoint ÷ midpoint | **Ux** | **76 / 84** | **9.938** (`d0.6_s011`) |
| median of last decile ÷ first decile of 2nd half | Ux | 73 / 84 | 8.875 |
| endpoint ÷ midpoint | Uy | 66 / 84 | 4.247 |
| max over 2nd half ÷ midpoint | Ux | 84 / 84 | 10.993 |

**All three reported numbers stand. None is overstated. The only correction is
the frame in §0 and the one-member refinement in §1.2.**

---

## 2. Mechanism — were they capped, and were they near converged?

**Capped: yes, by construction.** `controlDict` is `stopAt endTime; endTime
4000;` and 82 of 84 logs end at exactly `Time = 4000`. The remaining two
(`d0.2_s038`, `d0.2_s039`) have logs truncated at iteration 2543 and 2095 while
their field output carries `index 4000` — the solver ran on, the log capture
stopped. **Consequence: the residuals recorded for those two members are the
residuals at iteration 2543 and 2095, not at 4000, and both were admitted
through the 1e-3 residual gate on that stale evidence** (2.54e-4 and 4.69e-4).
Two of the 28 gated δ = 0.2 members rest on truncated logs.

**Near a converged state: no — and this is measured, not assumed.**

A rising residual is suggestive but not decisive, because a run can be
unconverged in a residual sense while its *integrated* outputs are stable. That
distinction decides recoverability, so it was tested directly. `writeInterval`
equals `endTime`, so **only one field snapshot exists per member (t = 4000) and
no intermediate field output exists anywhere in the tree** — the QoI itself
cannot be trended. The one integrated quantity printed every iteration is the
**`meanVelocityForce` driving pressure gradient**, the global forcing required
to hold `Ubar = 0.72`. On a settled steady state it goes constant.

Measured as the peak-to-peak swing of that pressure gradient over the **final
500 iterations**, normalised by the median |pg| over the second half (a robust
scale — normalising by the mean is unusable because several members' pg passes
through zero):

| | value |
| --- | --- |
| `null` control | **0.0008** — settled to 0.08 % |
| median of the 84 | **0.862** — still swinging by ~86 % of its own level |
| worst (`d0.6_s011`) | **5.18** |
| members settled to < 5 % | **2 of 84** |
| **members whose driving pressure gradient changes _sign_ within the last 500 iterations** | **23 of 84** |

The `null` control is the positive control for this instrument too: it *can*
register "settled", and does, at 0.0008. The perturbed members do not.

A second, independent instrument agrees: the F6b baseline of this same case
converged to Ux initial residual **3.6e-9**, and the `null` sits at **1.57e-5**,
while the members' median final Ux residual is **1.29e-3** and median final p
residual is **3.5e-2** — five to six orders of magnitude above the converged
state of the very same case.

**Mechanism verdict.** The unreachable target removed the solver's stopping
test, so every member ran to a fixed 4,000-iteration budget and stopped
wherever it happened to be. For 83 of 84 that place is **not near a steady
solution**: the flow's own global forcing is still oscillating at order-unity
relative amplitude, and for 23 members it is still reversing sign. The
perturbation drives these cases into genuinely unsteady behaviour that a steady
solver cannot settle — the `null` proves the machinery converges fine when the
perturbation is switched off. **These are not converged solutions sampled from a
distribution; they are arbitrary phases of an unsettled transient.**

---

## 3. The finding that decides the claims: the band's reach is a convergence artifact

Sorting all 80 random-matrix members by how settled they are and grouping into
quartiles:

| settledness quartile (pg swing) | n | mean reattachment x/h |
| --- | --- | --- |
| 1 — most settled (0.04 – 0.27) | 20 | **7.214** |
| 2 (0.27 – 0.86) | 20 | 6.267 |
| 3 (0.86 – 1.71) | 20 | 6.161 |
| 4 — least settled (1.71 – 5.18) | 20 | **5.249** |

Monotone. The baseline is 7.644 and the LES truth is 4.6–4.7. **The more
unsettled a member is, the further its reattachment moves from the baseline
toward the LES value.** As members settle, they return toward the baseline.

The same thing seen from the claim side — the members that *carry* the LES
coverage are the least settled in the ensemble:

| | members at or below LES upper bound 4.7 | median pg swing, those members | median pg swing, all others |
| --- | --- | --- | --- |
| δ = 0.2 | 6 of 40 | **1.513** | 0.270 |
| δ = 0.6 | 7 of 40 | **2.075** | 1.061 |

`d0.6_s011` — the single **worst-settled member of all 84** and the worst rising
residual (9.94×) — is one of the seven carrying δ = 0.6's coverage.

**The honest caveat, which cannot be resolved from existing runs.** This is
correlational, and there is a competing explanation pointing the other way: a
member with a genuinely stronger stress perturbation may *both* reattach earlier
*and* be harder to converge, in which case the correlation is physics, not
artifact. **Existing data cannot separate the two**, because no intermediate
field snapshots were written. The discriminating experiment is in §5.

---

## 4. Per-claim survival table

Graded on one question: **does the claim depend on the members having
converged?**

| # | Claim (surface) | Grade | Reason |
| --- | --- | --- | --- |
| 1 | **Sampler verification: 15 checks, 0 failures** (V1–V7b, `verify_sampler_result.json`, F6d §3.2) | **SURVIVES** | Entirely offline linear algebra and Monte Carlo on the sampler. Never touches a CFD solve. Unaffected in full. |
| 2 | **Two implementation bugs found and fixed** (`hermegauss` overflow; `gammaincinv` → +inf) | **SURVIVES** | Same reason — properties of the sampler code, established without solving. |
| 3 | **Paper inconsistency found** (Appendix A step 2.4 drops a factor 2 vs Eqs. 16/24) | **SURVIVES** | A reading of the paper, verified numerically against `E{[G]} = [I]`. Solver-independent. |
| 4 | **The sign error in F6a's eigenvalue perturbation** (F6d §4) | **SURVIVES** | Established by controlled A/B runs, the OpenFOAM v2606 sources, and a realizability audit — a *relative* one-character comparison in which both arms are identically affected, and the conclusion is about which direction the code moves, not about a converged value. |
| 5 | **Null test: propagating `R_sample = R_bar` leaves the baseline where it is** (reattachment 7.643814 vs 7.643915) | **SURVIVES** | The one member that *is* settled (pg swing 0.0008, residual 1.57e-5). It is the positive control and it passes on its own evidence. |
| 6 | **The F6b baseline is real and converged** (residuals to 3.6e-9; matches shipped kOmegaSST to 5 s.f.) | **SURVIVES** | Its missing convergence sentence genuinely *is* a false negative — substantiated by a monotone four-decade residual history, which the ensemble members do not have. Note the baseline case file carries the same `p 1e-15` (§6). |
| 7 | **Baseline over-predicts recirculation by ≈ 64 %** | **SURVIVES** | Rests on the converged baseline and the LES reference only. |
| 8 | **"The δ = 0.2 band contains the LES truth"** (`covers_LES_range: true`; plotted in `F6d_band.png`) | **INVALID** | The 6 members producing the coverage are the least-settled in the group (median pg swing 1.51 vs 0.27). Restricting to better-settled subsets destroys the coverage: at a settledness cut of 0.25 the band no longer covers LES. A distribution over unsettled transients is not a distribution over solutions. |
| 9 | **"At δ = 0.6 the band is wider still and worse behaved"** | **QUALIFIED** | The *ordering* (δ = 0.6 wider than δ = 0.2) is a relative comparison at matched cap, mesh, and dictionary, and larger dispersion plausibly does widen the band. But the *magnitudes* (support 6.635 vs 5.402) are inflated by transient scatter that is itself larger at δ = 0.6 (median pg swing 1.38 vs 0.32), so the direction survives and the size does not. |
| 10 | **"The band is much wider than the corner union, not tighter"** (headline finding 2) | **QUALIFIED** | Directionally robust — 3.98/5.69 (90 %) vs 4.46 support is a large gap. But it is *not* the clean equally-affected comparison it looks like: all 3 corners also fail the residual gate (0 of 3) with pg swings 0.39–1.53, so both sides are unconverged **to different degrees**, and both widths are inflated by different amounts. The sign of the comparison survives; its magnitude is not defensible. |
| 11 | **Velocity-profile envelope contains the LES profile at 100 % of points, both δ** (`frac_LES_points_inside_envelope: 1.0`) | **INVALID at δ = 0.2, QUALIFIED at δ = 0.6** | Recomputed over the better-settled half: δ = 0.2 coverage falls **1.000 → 0.752** and mean envelope width **halves, 0.542 → 0.245**. More than half the envelope is transient scatter and the 100 % is achieved by it. At δ = 0.6 the settled half still gives 0.994 — but only because that "settled half" is itself unsettled (median swing 1.38), so it is untested rather than vindicated. |
| 12 | **Headline finding 3: "gating throws away the members closest to the truth"** (δ = 0.2: 12 gate-fail mean 5.556 vs 28 gate-pass 6.695) — presented as a *confirmed pre-registered risk* from `F6a_epistemic_propagation.md` §9.2 | **INVALID as stated** | The arithmetic is right and the pre-registration is genuine, but it has a confound it does not consider and cannot exclude. The gate-fail members are 83 % unsettled (median pg swing 1.731) against 14 % for gate-pass (0.212). The gate is not preferentially discarding *hard-but-valid* samples; it is largely discarding *unconverged* ones. "Gating biases the band" and "gating removes the unconverged members" predict the same table, and this record asserts the first without excluding the second. |
| 13 | **"At δ = 0.6 the gated subset stops containing the LES range — gating destroys the property the band was built to have"** | **INVALID as stated** | Same confound, and weaker still: the gated subset is **n = 5**. Non-coverage at n = 5 is near-uninformative about the population either way. The dramatic reading ("fatal") is not supported at that sample size. |
| 14 | **Cost record, 394.79 core-min total** (`cost.json`) | **SURVIVES** | An as-run measurement, explicitly scoped to what was executed. Convergence is irrelevant to it. |
| 15 | **`F6d_band.png`** — the published figure | **INVALID as published** | Plots `all_admitted` (n = 40) with 5–95 % bars and full support against an "LES 4.6–4.7" band, labelled only `(n = 40, bar = 5-95%)`. It is the most exposed surface and it carries **no convergence or gate caveat at all**, while the text that does carry the caveats sits in a separate document. |
| 16 | **Profile envelope beats the corner union: 100 % vs 71.6 % coverage** (`F6d_random_matrix_uq.json` `/profile_coverage`, `/live_corner_union_profile_coverage`) | **INVALID at δ = 0.2** | Same as claim 11, and worse-placed: this is the **only metric on which the random-matrix band beats the corner union**, it exists **only in JSON with no prose statement, no gated counterpart, and no residual caveat**, and its δ = 0.2 margin is manufactured by transient scatter (coverage 1.000 → 0.752, width 0.542 → 0.245 over the settled half). |
| 17 | **`RESULT_PRIORITY_CHARTER.md` §254, §565 — "4.041 against 0.797"**, cited twice as the *provenance for ranking rule D12* (coverage → width → central value) | **QUALIFIED — rule survives, citation does not** | The charter rule (prefer coverage, then width) is a methodological principle that does not depend on this ensemble being converged. But the number it cites is ungated, carries no convergence qualifier, and is additionally **stale** (4.041 was superseded by 3.979). A governance rule should not rest on a width this audit grades unsound; it should cite the *principle*, not the measurement. |
| 18 | **`GOALS_AND_PROPOSALS_CHARTER.md` §148 — "5.1 times wider … a finding the field does not have"**, justifying why a zero-scoring project was worth funding | **QUALIFIED** | The funding judgement survives on claim 10's surviving direction (the band *is* much wider). The stated multiple is ungated, unqualified, and stale (5.1 vs 5.0). Same disposition as 17: the argument holds, the number should not be quoted bare. |
| 19 | **`W3_AHMED_PREREGISTRATION.md` §143-155 — the binding "Gating-disclosure policy"**, four mandatory rules derived from F6d, including *"If gating changes the containment verdict, that fact is the headline"* | **INVALID in its premise, and this is the most consequential item in the table** | The policy is *founded* on claims 12 and 13 — that gating biases a band away from truth. This audit finds that at δ = 0.2 the gate was largely separating converged from unconverged members, not calm from hard ones. **A binding rule that says "report the ungated ensemble" institutionalises the contaminated set as primary.** Rules 1 and 4 (report every member; state the discarded count) are good practice and survive on their own merit; the *rationale* and the ungated-primary ordering do not. |
| 20 | **`W2_DOW_STRUCTURAL_UQ_PROGRAM.md` §4.3 — "Any propagation this program runs reports the ungated ensemble"**, adopting F6d's rule verbatim for a live program | **INVALID as a rule** | Same defect as 19, now load-bearing on future work rather than past work. This is the item with the largest forward cost and the cheapest fix (it is a sentence, not a solve). |
| 21 | **`w2-band-validation-on-a-held-out-case.json` gate G3 (pre-registered)** — *"the ensemble is reported ungated; a gated subset may appear beside it and never instead of it"* | **INVALID as premised** | A *pre-registered* gate inheriting the same rationale. Pre-registration is what makes it worth flagging now rather than after the run: it is currently cheap to amend and will not be later. |
| 22 | **`W2_DOW_STRUCTURAL_UQ_PROGRAM.md` cost transfer** — 135.47 / 170.35 core-min per 40 members, median member 3.23 / 4.48 core-min, 500 samples ≈ 1,615 core-min | **QUALIFIED** | The as-run timings are sound (claim 14). But they price **4,000 iterations per member**, which this audit shows is not enough to converge this case under perturbation. Any budget built on them **under-prices a converged ensemble by roughly 3–5×**. The number is right; what it is being used to buy is not. |
| 23 | **`sdk/scripts/run_mfmc_error_budget.py` — "MISSING-MEMBER (gating) bias" term**, explicitly named after "the F6d question" | **QUALIFIED** | A methodological transfer of the *question* to a different gate on different data, not a reuse of F6d's numbers. The question remains legitimate; the F6d answer cited as its motivation is claim 12. |

**Pattern.** Everything established *without* the solver survives intact — the
sampler, the paper reading, the bug finds. Everything that is a *relative
direction* survives with a size caveat. Everything that is a *quantitative
statement about where the band sits relative to the LES truth* fails, because
that is precisely the quantity the transients move.

**And one inversion worth stating on its own.** F6d's most-propagated conclusion
— *report the ungated ensemble* — is the one this audit most directly
contradicts. It has already reached a binding pre-registration (19), a live
program rule (20), and a pre-registered proposal gate (21). The correct reading
is neither "gate" nor "don't gate": the 1e-3 Ux gate was a **weak proxy for
convergence** that happened to work in the right direction, and the defensible
fix is to gate on *settledness of the quantity being reported*, measured, rather
than to report the ungated set because the gate looked biased.

### 4.1 Independent corroboration, from an instrument that never knew about this

`demo-output/website/monitor/replay_s1_s6.json` (generated 2026-08-10) runs the
lab's own S6 residual-stall rule across a 1,375-log archive. **98 of the 175
logs it fires on are F6d ensemble members** — 56 % of every S6 firing in the
whole archive, from 6 % of the corpus. The lab's own monitor had already flagged
this ensemble at extreme concentration; the JSON records the paths and no prose
surface calls it out. It is a fully independent confirmation of §2, and it was
sitting in the repo.

### 4.2 A separate defect found in passing, not part of this audit's charge

Two generations of F6d numbers are in circulation. Two members were re-run and
F6d.md §6.1 states every number was recomputed over all 40 — but six surfaces
still carry the pre-rerun values: `NOT_PASSING_REGISTER.md`,
`CAMPAIGN_STATUS.md`, `RESULT_PRIORITY_CHARTER.md` (×2),
`GOALS_AND_PROPOSALS_CHARTER.md`, `W2_DOW_STRUCTURAL_UQ_READING.md`, and
`F6a_epistemic_propagation.md` ("38 of 40 samples" vs the current 40 of 40).
The sharpest instance: `NOT_PASSING_REGISTER.md` publishes *"exactly one of 38
members beats the baseline"* — a sentence **F6d.md §6.5 explicitly retracts in
writing** as wrong on the ensemble's own data (the figure is 11 of 40). The
retraction did not reach the register that publishes it. This is orthogonal to
the convergence question and is reported so it is not lost; it is not fixed
here.

---

## 5. Is it recoverable, what would it cost

**Not recoverable from existing data.** The decisive question — does a member's
reattachment drift back toward the baseline as it settles — needs the QoI at
more than one time, and `writeInterval == endTime` means exactly one snapshot
per member exists. There is no purely-forensic path.

**No solve was launched. These are prices, not proposals.** Anchored on this
ensemble's own measured rates (`cost.json`: 194 s/member at δ = 0.2, 269 s at
δ = 0.6, both for 4,000 iterations, serial):

| option | what it buys | cost |
| --- | --- | --- |
| **0 — costs nothing, and should not wait for A** | Attach the convergence caveat to the four surfaces that currently carry none: the figure `F6d_band.png`, the `profile_coverage` JSON block, and the two charter citations (claims 15, 16, 17, 18). Put the §4 inversion in front of the owners of the three governance surfaces (19, 20, 21) **before** the W2/W3 work runs to their pre-registered rules. | **0 core-min** |
| **A — diagnostic** | Continue only the **13 members that carry the LES coverage** by +12,000 iterations, writing intermediate snapshots. Directly settles §4's confound: if their reattachment climbs back toward the baseline, claims 8/11/12/13 are confirmed artifacts; if it holds, the physics reading is vindicated and much of the record is restored. | **≈ 152 core-min** |
| **B — restore the bands** | Continue all 80 members by +12,000 iterations. | ≈ 926 core-min (**15.4 core-h**) |
| **C — clean re-run** | All 80 re-run with a *reachable* target and a 20,000 cap, so the solver's own stopping test decides. | ≈ 1,543 core-min (**25.7 core-h**) |

**Option A is the recommendation to put to the F6d owners** — it is 1.6× the
cost of a single δ = 0.6 member's original run per member, it is the only step
that discriminates between the two live explanations, and every other decision
is cheaper to make after it.

**A caution about Option C.** The `null` settles and the members do not, which
is consistent with the perturbed cases having **no steady solution to converge
to**. If so, no residual target and no iteration cap will produce one, and the
honest instrument is a time-averaged unsteady statistic, not a steady solve.
Option A also distinguishes this case, and it should be priced before C is
funded.

---

## 6. Propagation — how far the same defect reaches

**Derived, not listed.** Every `fvSolution` in the repository was parsed and
tested against the self-relation of §1.1 — a `residualControl` target at or
below its own field's linear-solver tolerance. Frame: **all 365 `fvSolution`
files present in the working tree** (`find` for the filename; `.git` excluded,
gitignored files included, which the shell's `grep` would have missed).

| | count |
| --- | --- |
| `fvSolution` files parsed | 365 |
| with a `residualControl` block | 271 |
| with none (cannot have the defect) | 94 |
| **carrying at least one unreachable target** | **120** |
| undecidable (target field has no matching solver entry) | 3 |

Only 3 undecidable, all `D5_rsm_runs` Reynolds-stress components — none of the
`1e-15` shape. Every one of the 120 is the same shape: field `p`, target
`1e-15`, against its own solver tolerance of `1e-12` (116) or `1e-14` (4).

Where the 120 are:

| location | n | reading |
| --- | --- | --- |
| `f6d_random_matrix_uq/ens/` | 84 | this ensemble |
| `campaign/W2_sparta_runs` | 21 | **unexamined — same shape, warrants its own audit** |
| `f6d_random_matrix_uq/` other subdirs (`signdemo`, `signcheck`, `f6a_recheck`) | 9 | same family |
| `dafoam/ladder-b` | 5 | **not this defect** — inherited from the benchmark authors' shipped CBFS case, diagnosed and *deliberately preserved* with cause recorded (`B2_duct_baseline.md`; `CLOSURE_RANK1_CAMPAIGN.md` even re-prices a route around it) |
| `f6b_periodic_hills/case_breuer_re10595` | 1 | the parent baseline case — carries the target, but its convergence is separately substantiated to 3.6e-9, so claim 6 stands |

So: **120 files carry the pattern; 84 are this ensemble; 21 in `W2_sparta_runs`
are unexamined and are the recommended next audit; 5 are documented and
intentional; 1 is the parent case whose convergence is independently
established.**

**Why closing it once did not stop it.** The F6b family diagnosed this exact
defect and closed it *for itself* — `F6b_periodic_hills.md` §"Convergence — and
a gate-checker false negative, diagnosed rather than overridden" names the
1e-15, names the mechanism, and correctly rules the missing sentence a false
negative. **What propagated to F6d was the dictionary and the excuse. What did
not propagate was the evidence that made the excuse valid.** F6b earned its
"false negative" verdict with a monotone four-decade residual history ending at
3.6e-9. F6d inherited the same `fvSolution` and the same conclusion, but its
members end at 1.29e-3 and rising. A justification that is sound for one case is
not transferable to another by copying the file it was written about.

The general lesson for the ladder: **a defect closed by argument travels
further than a defect closed by construction.** F6a's hump family is the
contrast — it carries *reachable* targets (`U/p/k 5e-7`, `omega 1e-10`) and its
solver stopped itself, printing `SIMPLE solution converged in 1772 iterations`.
Nothing had to be argued.

---

## 7. What this audit did not do

- **Did not modify anything** — no case file, no `fvSolution`, no published
  record, no plot. This is another family's ensemble; the remedy is theirs.
- **Did not launch a solver.** §5 prices; it does not propose to spend.
- **Did not re-derive** the sampler mathematics, the KL/PCE machinery, or the
  F6a sign-error analysis. Those are graded SURVIVES on the basis that they are
  solver-independent, which was checked, not on the basis that they were
  re-verified here.
- **Could not settle** the §3 confound. That needs Option A.
- **Did not re-verify the stale-number generation** of §5.2 beyond confirming
  that two values are in circulation and that one of them is a retracted
  sentence. Which surfaces to correct is the owning family's call.

**Surfaces checked and found to carry no F6d-derived claim** (so their absence
from the table is a measurement, not an oversight): all website HTML/JS
(`benchmarks.html`, `closure.html`, `shoot.html` — zero F6d references; the
withdrawn 1.1069 has already been replaced by 1.1437 and the superseded row is
marked withdrawn), `demo-output/website/certificates/`,
`credibility/validation_tiers.json`, `solve_registry/`, `surfaces/`, and
`sdk/workflows/nasa_hump.py` (its `REATTACHMENT_MODEL_BAND = 0.20` is a
hard-coded literature band with no dependency on this ensemble). Several
apparent "f6d" hits elsewhere are hex-hash coincidences in git SHAs, not
references.
