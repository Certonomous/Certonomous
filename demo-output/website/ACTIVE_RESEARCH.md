# Active Research board

Live status per ladder, with measured numbers only. Every figure here is copied
from a solver output, a scored artifact, or a published leaderboard. Nothing is
estimated unless the row says so.

Created 2026-07-28 because no board of this name existed in the repository. If
an external board was intended instead, this file should be pointed at it — the
question is logged in the blockers list, and work did not wait on the answer.

Last updated: 2026-07-28 00:5x UTC.

---

## Ladder A — DAFoam verification and reproduction

| Rung | Case | Status | Headline measured result |
| --- | --- | --- | --- |
| A1 | NACA0012 incompressible, official tutorial | **COMPLETE, FD-verified** | CD 0.0209105, CL 0.4987653, 4,032 cells, 3.51 core-min |
| A2 | MACH tutorial wing (3D) | **COMPLETE, FD-verified, optimization run** | CD 0.02772949, CL 0.47759, 38,304 cells; **28.28% drag reduction** at matched CL, time-boxed; 692.5 core-min |
| A3 | ONERA M6 transonic | **primal + Cp validated; adjoint blocked** | CD 0.02299556, CL 0.31311589, 399,360 cells, 127.5 core-min |
| A4 | Ahmed body 25 deg | **COMPLETE, FD-verified** | CD 0.06998 on 45,760 cells; gradient FD-verified at 10.04% on a 2,777-cell mesh; 10.9 core-min |
| A5 | U-bend internal flow | running | — |
| A6 | CRM / DPW-class wing-body | queued, time-boxed, converged primal counts as success | — |

### Consolidated FD verification table (every adjoint rung)

| Rung | derivative | analytic vs FD, relative error |
| --- | --- | --- |
| A1 | geometric constraints wrt shape | **4.4e-14 to 1.4e-10** |
| A1 | CD wrt flow parameter | **0.232%** |
| A1 | CL wrt flow parameter | **0.232%** |
| A1 | CL wrt shape | **1.67%** |
| A1 | CD wrt shape | **11.43%** on the difference-vector norm, but the two gradient magnitudes agree to **0.451%** |

| A4 | CD wrt rear-slant shape | **10.04%** — adjoint 0.21821, FD 0.24258. **PASS** within the calibrated band |
| A5 | objective wrt shape, 27 components | **46.6%** aggregate; only 5 of 27 within the 12% band; **2 sign flips** |

### A4 found a silent solver mismatch that affects the credentials wall

The Ahmed primal landed **22.05% away from our own validated OpenFOAM baseline**
on the same mesh, boundary conditions and turbulence model. The cause is not
tolerance and not mesh: our baseline sets `consistent yes` in its `SIMPLE` block
— **verified directly in the case file** — which selects the consistent pressure
correction. `DASimpleFoam` does not implement it and silently runs the plain
variant instead.

On the 25 degree slant this is not a small numerical difference. That geometry
has a **documented bistable wake**, so the two algorithms settle on *different
branches of the solution*. Neither number is wrong on its own terms, and both
sit within the experimental band once rebased to frontal area — ours 0.2510 and
the baseline 0.3219 against the measured 0.285, at 11.93% and 12.95%.

**Any credential or comparison that places the two solvers side by side inherits
this**, and an audit is now queued.

**A4 also validated the memory-wall constraint as actionable:** the primal ran
at 45,760 cells and the adjoint was deliberately coarsened to 2,777, which made
it tractable and produced the first passing FD verification since A1. Coarsening
for the gradient stage while comparing the primal on the fine mesh is legitimate
precisely because it was disclosed.

### Cross-rung finding: the adjoint has a memory wall on this host, between 10^4 and 10^5 cells

This one held up, and it constrains the whole ladder.

| rung | cells | adjoint outcome |
| --- | --- | --- |
| A1 NACA0012 | 4,032 | works, FD verified |
| A5 U-bend | 4,800 | works, GMRES converged in 86 iterations |
| A3 ONERA M6 | 399,360 | **OOM** in the mesh-sized residual/volume-coordinate Jacobian assembly |
| A3 coarsened | 99,840 | **still OOM** |

Eight independent mitigations were tried on A3 and ruled out: 12 GB and 18 GB
container caps, 4-rank and 2-rank decomposition, GMRES restart 1000 to 200, and
preconditioner fill level 1 to 0. The 2-rank attempt drove the host to 1.77 GB
free and was killed manually rather than left to run — the right call, given
this box has been taken down twice in two nights by memory exhaustion.

**The working envelope for adjoint work on this instance is order 10^3 to 10^4
cells, not 10^5.** Consequences, stated now rather than discovered later:

- **A6 (CRM / DPW-class) cannot produce a gradient here.** The queue already
  scoped it as "converged primal is success, gradient is stretch" — that
  judgement is now backed by measurement rather than caution.
- **A4 was briefed to build the smallest mesh that still resolves the 25 degree
  slant separation**, and to coarsen further for the adjoint stage specifically.
  Verifying a gradient on a coarser mesh than the primal comparison is
  legitimate as long as it is disclosed.
- A genuine matrix-free adjoint path exists (`adjUseColoring=False`) but trades
  the memory for a runtime cost that was not attempted and should not be assumed
  tractable.

### Refuted cross-rung finding: FD agreement is NOT gated by primal convergence

Neither rung could see this alone. Placed side by side:

| rung | primal state | FD shape-derivative result |
| --- | --- | --- |
| A1 | residual **9.646e-09** against tolerance 1e-08, converged | 11.43%, **no sign flips** |
| A5 | p initRes plateau **2.2576e-04**; total field residual norm2 **55.776** | 46.6%, **2 sign flips** |

Five orders of magnitude apart in primal convergence; four times the FD error,
plus sign flips. **Hypothesis: the adjoint is exact for the discrete converged
state, so if the primal sits at a residual plateau the adjoint is linearised
about a point that is not a solution, while each finite-difference perturbation
re-solves to a slightly different point on that same non-converged manifold.**
The difference between those is noise no step size can remove — which is
precisely what A5's own step-size sweep found when the FD estimate failed to
converge toward the adjoint value as the step grew.

A supporting detail from A5's record: the 55.776 total is dominated by
temperature at 41.16. That case descends from a conjugate-heat-transfer family
and still solves temperature, which is excluded from both the objective and the
adjoint yet remains in the primal state and far from converged. **The state the
adjoint linearises about is polluted by a field the adjoint cannot see.**

### The test ran. The hypothesis is **REFUTED**.

| metric | before | after tightening |
| --- | --- | --- |
| p initRes | 2.2576e-04 | 2.0568e-04 (9% better, still far from 1e-8) |
| total residual norm2 | 55.776 | 59.324 — **worse** |
| FD aggregate error | 46.64% | **46.21% — no material change** |
| components within 12% | 5 of 27 | 4 of 27 |
| sign flips | 2 | 3 |

`residualControl` at A1's 1e-8 bar, solver tolerances tightened one to two
orders of magnitude, `endTime` extended 1000 → 5000 → 10000. **Iterations 1000
through 10000 produced bit-identical residuals** — never under-iteration, but a
true fixed point of the discrete iteration, plausibly the curved duct's
secondary-flow structure which a coarse steady solve cannot resolve away. The
tightened design point differs from the original only in the 6th significant
figure (pressure loss 52.34517755 against 52.34521634), so this is the same
state, not a better-converged one.

**The mechanism I proposed was also wrong.** I argued temperature, at 41.16 of
the 55.776 total, was polluting the linearisation point. But this case carries
constant viscosity with no temperature dependence and no buoyancy, and the
objective is a pure function of pressure and velocity — temperature's adjoint
row is **analytically decoupled** from the rows the gradient depends on. It had
no channel into the result, and tightening its solve predictably did nothing.

**The rule that replaces it** (now L-7): do not assume "converge harder" fixes
gradient disagreement. Establish first, with one cheap high-iteration run,
whether convergence is even available. A plateau that survives a tenfold
iteration increase is reporting something about the physics or the mesh, and the
next lever is resolution or geometry smoothness, not solver settings.

A5's original measured numbers stand untouched in the record; this is an
appended addendum. **A1's 11.43% therefore remains unexplained**, and the
step-size study already in the proposal queue is the next probe.

### RECALIBRATION — the "1 to 12 percent is normal" band was built on n=1 and is too loose

I derived that band from A1 alone and handed it to every subsequent agent as
settled. A2 shows it is not.

| rung | cells | CD wrt shape, FD error | shape DVs |
| --- | --- | --- | --- |
| A4 Ahmed body | 2,777 | 10.04% | 1 scalar |
| A1 NACA0012 | 4,032 | 11.43% | 20 |
| A5 U-bend | 4,800 | **46.60%** | 27 |
| **A2 MACH wing** | 38,304 | **1.71%** | 96 |

**The spread is 1.71% to 46.60% — a factor of 27.** A2 demonstrates that 1.71%
is achievable on a *larger* mesh with *more* design variables, which is the
opposite of what "shape derivatives are just noisy" would predict. A1's 11.43%
is therefore not a floor imposed by the method; it is specific to A1, and
`PROOF.md` already localises it to three leading-edge control points.

**Consequence I have to own: A4 was graded PASS at 10.04% against this band.**
Its measured numbers are sound and stand unchanged, but **the verdict label
rests on a threshold that no longer looks defensible** — 10.04% is 5.9 times the
best result achieved tonight. A4 should be read as "within the observed spread,
well above the best achieved", not as a clean pass.

**This is the same error I made with the primal-convergence hypothesis**:
generalising from too few points and propagating it as established. There it was
n=2; here it was n=1, and it travelled further because four agents were briefed
with it. The step-size study already in the queue is now the priority probe —
until it runs, the honest statement is that **the acceptable FD tolerance for
shape derivatives on this stack is not yet established**, and rung verdicts that
hinge on it are provisional.

**The calibration that governs every later rung.** The geometric constraints
verifying at machine precision proves the harness, the deformation chain and the
check itself are sound — so the 11.43% cannot be waved away as a broken rig.
And because the gradient *magnitudes* agree to 0.451% while the difference norm
is 11.43%, the disagreement is **directional, per-component noise, not a scale
error**. A shape-derivative gap of order 1 to 12 percent against central
differences is normal for this class.

This also settles a stale docket entry: the "3 of 8 components at 11.9 and 11.6
percent with one sign-reversed" describes the **tutorial's own** known failure
signature, not our sail case, which was separately recorded as differing from it
at 0.7 to 8.2 percent with no sign flips. **Our adjoint behaves better than the
official tutorial's.**

## Ladder B — closure literature with adjoints

| Rung | Status | Result |
| --- | --- | --- |
| B1 | **COMPLETE** | Ranked reproduction plans written; benchmark clone and public leaderboard located on this box |
| B2 | **COMPLETE, verified** | Uncorrected duct baseline reproduced to 0.16% and 0.64% |
| B3 | running | The field inversion itself |
| B4 | queued | Feed findings back into the closure track |

**Top pick:** Wu, Zhang and Zhang, AIAA Journal 63(2), 2025, 687-706. They invert
a correction field on the SST destruction term through DAFoam's own discrete
adjoint, train only on a public separated-flow case, and generalise to the ducts
without seeing them. Rejected candidates were reported with reasons rather than
padded: one leaderboard entry is gradient-free rather than field-inversion, two
foundational papers have zero case-geometry overlap, and one paper's citation
could not be pinned down and was reported as a gap instead of guessed.

### B2 — the duct baseline is reproduced, and the pipeline was validated before it was trusted

The benchmark clone turned out to ship **the paper authors' own uncorrected
case directories** — mesh, boundary conditions, `fvOptions`, and the original
run log. Re-solved as-is on this box and scored through the benchmark's own
unmodified scorer:

| case | ours | published floor | deviation | field vs field |
| --- | --- | --- | --- | --- |
| AR_1_Ret_360 | 0.1290 | 0.1288 | +0.0002 (0.16%) | 0.023% |
| AR_3_Ret_360 | 0.1251 | 0.1243 | +0.0008 (0.64%) | 0.09% |

**The sanity check is what makes these trustworthy:** scoring the benchmark's
*own* baseline field through our scorer reproduced 0.1288 and 0.1243 exactly,
confirming the scoring pipeline before any of our own numbers were believed.
30.9 core-min total.

Three deviations documented with cause rather than smoothed over: a custom
frozen-turbulence library whose source is not distributed anywhere in the public
clone (stock SST substituted, measured as effectively inert at under 0.1% field
agreement, but **not** verified against the library's own source); an OpenFOAM
fork mismatch between the original Foundation build and this box's ESI build,
worth 10 to 13 percent in iteration count but only 0.02 to 0.09 percent in the
converged field; and a renamed diagnostics function object, dropped with no
effect on the solved field.

**Blocker found and flagged rather than worked around:** the CBFS reference
fields use `#include`-macro'd dictionaries that the field parser silently fails
on, returning nothing at all. A silent empty read is precisely the failure that
manufactures a fake result, so it was handed to B3 as the first thing to fix.

## Ladder C — closure challenge

**Closure metric movement tonight: NONE. 0.0741, unchanged since round 2.**
Stated explicitly because the queue requires movement to be reported including
when it is zero. The reason is in C2 below: the recoverable term was located but
deliberately not taken, because taking it by inspection would have invalidated
the entry.

### Where we actually stand

| Rank | Entry | Overall |
| --- | --- | --- |
| 1 | Reissmann, Fang, and Sandberg | 0.0595 |
| 2 | Wu and Zhang | 0.0624 |
| 3 | Liu, Wang, Zhao, and Xiao | 0.0737 |
| — | **ours, unsubmitted** | **0.0741** |
| 4 | Montoya, Oulghelou, and Cinnella | 0.0779 |

**We hold the best score on the entire leaderboard on three of eight cases:**
alpha_15_13929_4048 at 0.0501 against a best-other 0.0592, alpha_15_13929_2024
at 0.1011 against 0.1195, and AR_14_Ret_180 at 0.0303 against 0.0325.

### C2 — where the deficit lives

| case | share of the gap to rank 2 |
| --- | --- |
| AR_1_Ret_360 | **31.5%** |
| AR_3_Ret_360 | **31.4%** |
| NASA_2DWMH | 18.2% |
| alpha_05_4071_4048 | 10.4% |
| alpha_05_4071_2024 | 8.5% |

The two square ducts are **62.9%** of the deficit. Separately, the correction is
worse than doing nothing on three cases against the uncorrected baseline, worth
0.0066 on the mean, which is 1.7 times our margin over rank 4. Both terms are
real; the duct term is the larger by a factor of eight.

### C1 — training line: test-blind baseline-error gate **BUILT AND VALIDATED**

A gate that predicts, from features the test cases legitimately expose, whether
the correction should be applied at all. Fitted on the 21 training cases,
checked on the 4 held-out validation cases, **never on a test case**.

| Result | Value |
| --- | --- |
| Features after screening | 3 (p90 of two Pope invariants, plus a backflow-fraction separation proxy) |
| Separation on held-out validation | **AUC 1.0** |
| Threshold set from training data alone | classified **4 of 4** validation cases correctly |
| Trivial always-apply baseline | 3 of 4 |
| Compute | ~0.06 core-min, single core, no flow solve |

**Two things make this trustworthy rather than merely good-looking.** First, the
agent's own first attempt — a 15-feature model — overfit and was reported, not
buried: training cross-validation looked strong at r +0.93 while validation
collapsed to r +0.25 with the wrong rank order and one prediction twice outside
the observed training range. Feature screening to 3 was the fix. Second, the
n=4 caveat is stated plainly: with only one positive label, an AUC of 1.0 has
roughly a 1-in-4 chance of arising by luck. **Encouraging, not established** —
the same caution C2 applied to its own n=5 finding.

**Leakage independently verified by the supervisor, not merely asserted.** The
script loads only the training and validation splits, imports the test list
solely to assert that it never intersects them, and never calls the benchmark's
scoring function. The only matches for a test-case name anywhere in the file are
in the docstring, one of which is the sentence stating it does not touch them.

**Not applied to the test set, and no scoring call made.** Producing a validated
gate is the deliverable; deciding to spend the single shot is not tonight's call.

### C3 — NACA 4412 credential: **NOT VALIDATED**

Not because a number missed, but because the grading method is self-referential:
the reference is anchored on the solve's own lift, so a 25.0 percent lift
over-prediction inflates the induced term by 56.2 percent and widens the band
with it. Graded that way, the two best-resolved rungs fail and the worst-resolved
passes.

**Knowledge entry.** At fixed refinement, across a 17.7 fold change in boundary
layer coverage (4.36 to 77.0 percent), **drag moved 0.037 percent while lift
moved 9.41 percent**. Drag agreement is not evidence of a resolved boundary
layer on a low aspect ratio wing.

## Ladder D — background

| Item | Status |
| --- | --- |
| D1 mega batch | Running, 3 workers, single-instance lock in force. Session count and 0 failures tracked in the runner log; morning count is the true count |
| D2 queue refill | **6 proposals drafted and style-validated, 755 core-min costed** |
| D3 nightly retro | Queued for end of night |

### D2 proposals drafted this session

| Proposal | Core-min |
| --- | --- |
| Anchor the NACA 4412 reference independently of the solve | 15 |
| Add a boundary layer coverage gate to drag-only credentials | 20 |
| Shape derivative step size study | 35 |
| Closure baseline error estimator gate | 45 |
| Converge lift on the NACA 4412 ladder | 220 |
| Closure duct field inversion | 420 |

## Blocked

Billing alarm and spend cap cannot be read from this instance (no role, no
credentials, no client). Ledger cannot be synced off-host by either route. Both
are recorded in the blockers list with their exact unblock actions. **No spend
figure is reported anywhere in this board, because none can be measured.**
