# Lesson drafts — Kaandorp2020_TBRF lane (a-priori + a-posteriori)

Placeholders `L-TBD-K*` per the supervisor's numbering instruction; numbers are
assigned at commit from the tail of `docs/LESSONS.md`.

**Section A was previously drafted in the scratchpad as `lessons_B.md` L-183/184/185
and the scratchpad has since been cleared. Rewritten here from context. If those
three were already appended to `docs/LESSONS.md`, drop section A rather than
duplicating it.** Section B is new (this a-posteriori lane).

---

# SECTION A — from the a-priori reproduction (`../RESULTS.md`)

## L-TBD-K1. A second moment is not a verdict: the same closure prediction was 156x worse than the baseline and better than it, depending on which statistic of the same error field was reported

The TBRF reproduction preregistered `b_rms_F = sqrt(mean ||b_pred - b_LES||_F^2)`,
because that is the convention `_common/BASELINES.md` uses for the k-omega SST
comparator and the comparison had to be apples to apples. On the curved
backward-facing step the 16-feature forest returned **47.68 ± 46.40** (5 seeds)
against an SST baseline of **0.3051**. Read as a verdict that is a rout.

The error field says something else. Its **median is 0.170** — better than SST's
own `b_rms` of 0.319. Its p90 is 3.40 and its p99 is 153.9. The RMS is a report on
the tail, and the tail is **15.0 % of cells** whose predicted anisotropy violates
`||b||_F <= sqrt(2/3)`, a bound no realisable Reynolds stress can violate at all.
Projecting exactly those cells onto the bound — a rescaling that adds no
information — takes the RMS from 47.68 to **0.567**.

Neither number is wrong. "156x worse than the baseline" and "beats the baseline in
the median cell and is unbounded in a seventh of them" are both true, and only the
second tells you what to fix: retrain versus constrain.

**Standing rule: report the median, p90, p99 and max of the error field beside any
RMS, and beside them the fraction of predictions violating a hard physical bound.**
Where a physical bound exists — and for the anisotropy tensor one does — the
violating fraction is the first number, because it is the one that predicts what
happens in a solver. The preregistered verdict still stands on the preregistered
metric; the distribution goes next to it, never in place of it.

## L-TBD-K2. The stabiliser inherited from a sibling pipeline was the destabiliser, and the preregistration is what made that finding legible instead of embarrassing

`_common/tensor_basis.py` bounds the turbulent time scale below by Durbin's
`6 sqrt(nu/eps)`. It was written for the sibling TBNN reproduction, it is a
standard guard against `T -> 0` at a wall, and this reproduction inherited it and
**disclosed it as departure D2 with the stated reason "`k/eps` is unbounded in the
low-`k` freestream"**.

That reason was wrong, and the departure was the largest single error source in the
run. `k/eps = 1/(0.09 omega)` is bounded wherever `omega` is; it is
`6 sqrt(nu/eps)` that diverges when `k` and `eps` vanish together. Worse, `k/eps`
is Reynolds-similar and `6 sqrt(nu/eps)` is not — it carries `nu` explicitly, so it
means something different on a non-dimensional hill (`H` = 1) than on a duct meshed
in millimetres. The bound was the active branch in **71.8 % of duct cells and
46.0 % of step cells** against 8.9-11.3 % of training hills, inflating the time
scale by up to **2500x**. Removing it moved the held-out duct from
`b_rms_F` = 6.382 ± 2.110 to **0.3160 ± 0.0080**.

What made this recoverable rather than a silent bias: the departure was **written
down before the run with its rationale**, so when results came back wrong the
rationale could be checked and found false; the rationale was **falsifiable in four
minutes** (measure which branch of the `max` is active, per case); and the fix ran
as a **labelled post-hoc diagnostic**, not swapped into the headline.

**A numerical guard copied from a neighbouring case is an untested assumption about
the new case**, and guards that mention a material property (`nu`, `rho`, a length)
rather than only the flow's own quantities are the ones that break similarity
between cases. Check which branch of every `max`/`min`/clip is actually active,
per case, and report the fraction.

## L-TBD-K3. Reproducing a paper's headline contrast means reproducing its confound too, and the honest move is to run both arms

Kaandorp & Dwight's Table 3 is the evidence for the claim flagged as F18 — feature
set matters more than model class. Their case C3 (5 features) and C4 (17 features)
are the two arms. But the same paragraph states that C3 also used **fully grown
trees and all features per split** while C4 used **9 samples per leaf and 11 of
17 features**. The two arms differ in the feature set *and* the tree depth *and*
the split randomisation.

A reproduction has two defensible choices answering different questions: run the
paper's exact pair and reproduce a confounded contrast, or hold everything but the
feature set fixed and test the claim the contrast supports. We preregistered the
second as headline and the first as secondary, said so before running, and got
numbers that differ — the paper-faithful fully-grown 5-feature configuration beat
the depth-matched one on every held-out case. Run only one arm and you report "the
claim reproduces" or "it does not" with equal confidence and no way to tell which
effect you measured. Both arms cost under two core-hours.

---

# SECTION B — from the a-posteriori lane (`RESULTS.md` in this directory)

## L-TBD-K4. The truth-injection ceiling is the cheapest experiment in a closure lane and it is the one that fires

The lane preregistered a gate before grading any model: inject the **true** LES
anisotropy into the solved momentum equation and require it to cut the velocity
error by at least 30 %; if it does not, the propagation path is broken and every
model number downstream is NOT A RESULT.

It fired. On the held-out square duct, injecting the true anisotropy took `U_rms`
from the SST baseline's **0.1985** to **0.3215** — a 62 % *increase*. The
machine-learned correction, on the same path, gave **0.2594 ± 0.0007**: worse than
the baseline, but **better than injecting the truth**. Without the ceiling
configuration that pair of numbers is unreadable, and the temptation is to report
"the ML correction degrades `U` by 31 %" as a fact about the model. It is a fact
about the propagation.

The ceiling cost **8.5 seconds of CPU**. It is one extra configuration in a lane
that ran nineteen. **Any lane that propagates a learned correction should run the
truth injection first and grade nothing until it passes.**

## L-TBD-K5. An omitted correction term is not a neutral simplification: dropping R collapsed k by 67 % and inverted the ceiling

Why the ceiling failed was registered in advance as a risk and then measured. The
TBRF predicts `b` and nothing else, so the k-equation correction `R` was set to
zero — a registered choice with the registered consequence "our ceiling is a
b-only ceiling and is necessarily weaker than Schmelzer's".

"Weaker" turned out to be "inverted", and the mechanism is one number.
Injecting `b^Delta` changes the k-production term by
`Gextra = -2 k (b^Delta : grad U)`, which on this flow is strongly negative. With
no `R` to balance it, `k` collapses: mean `k` fell from the SST field's **26.68**
to **8.74** under truth injection and to **0.128** under the train-mean injection,
against an LES truth of **43.42**. `nu_t` follows `k`, the effective viscosity
collapses with it, and the momentum correction `2 k b^Delta` shrinks toward zero
at the same time. Schmelzer's `b^Delta` and `R` are not two independent
corrections you can take one of.

**Registering the omission was necessary and was not sufficient.** The registration
predicted a weaker ceiling; it did not predict a sign change. The lesson is to
measure the quantity the omitted term controls — here `k` — in the truth
configuration, and to treat a 3-to-200-fold departure in it as a stop condition,
not as context.

## L-TBD-K6. A convergence criterion has to be checked against the flow it will be applied to, and a periodic duct will break the obvious one

The lane registered "converged iff the initial residuals of `p` and `Ux` are both
below 1e-6, sustained 100 iterations". On the streamwise-periodic square duct with
a `meanVelocityForce`, that criterion **cannot be satisfied by a perfectly
converged field**: the cross-plane pressure is nearly uniform, so OpenFOAM's
residual normalisation divides by a near-zero scale and the `p` initial residual
sits at **0.14 after 30,000 iterations** on the zero-correction control — whose
`Ux` residual is **8.4e-16** and whose RMS `div(U)` is **6.1e-18**. The field has
not moved; the residual is an artefact of the normaliser.

Two further traps in the same family, both hit: the duct's baseline has
`Uy, Uz ~ 0`, so their initial residuals are **O(0.3) at restart even with zero
corrections** (this one *was* caught before registering and the components were
excluded); and a solver that stops at first satisfaction of its own
`residualControl` can never demonstrate a criterion phrased as "sustained for 100
iterations", so the registered criterion and the stopping mechanism were mutually
unsatisfiable.

**Before registering a residual-based convergence criterion, run the
zero-correction control and read its residuals.** Register the field-movement
fallback as primary for any flow whose driving pressure gradient is a source term
rather than a boundary condition.

## L-TBD-K7. Register a threshold only after measuring what the instrument can resolve, on a field you already trust

The lane registered "RMS `div(U)` normalised by the field's own gradient scale
below 1e-3 for every re-solved configuration", against this lab's published
post-hoc figures of 10.5 % and 9.7 %. On the two ducts it held with room to spare
(6.1e-18 for the zero-correction control, 3.8e-4 for the worst injected case).

On the curved backward-facing step it is **unmeasurable**. The divergence is
computed from a curvilinear chain-rule gradient, and on that mesh the estimator
returns **5.2e-3 for the shipped converged SST field and 4.3e-3 for the LES
truth**. Both of those fields are divergence-free to the precision of the solver
and the experiment respectively; the number is the estimator's floor, not the
field's continuity error. **A threshold of 1e-3 on that mesh cannot be met by any
field, including the two references.**

The calibration cost one script and no solves: *run the estimator on fields whose
answer you already know*. The shipped baseline and the LES truth were both sitting
in the case directory the whole time. Do that before writing the number into a
preregistration, and register the threshold per case — the same instrument was
exact to round-off on the ducts, because a fully-developed flow has no streamwise
derivative to discretise, and three decades short on the step.

The consequence for the record is small and specific: H5 is graded on the ducts
and reported as **NOT MEASURABLE** on the step. The consequence for the next
preregistration is that every registered tolerance now needs a line saying what
was measured to justify it.
