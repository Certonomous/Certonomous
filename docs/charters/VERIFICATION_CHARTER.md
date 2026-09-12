# Certonomous Verification Charter

Version 1.10, dated 2026-08-22. Defines what counts as done. It binds every
solve, every gradient check, every ladder rung and every number that reaches a
record, a certificate or a camera surface.

Version 1.6 adds two clauses on Katie's dispatch of 2026-08-10, both earned the
night before: **absence of error evidence is not evidence of a clean result**
(section 9), after a parser returned `clean` on a log where the tool had
fatally errored; and **a rule can over-reach as easily as under-reach**
(section 17a), after this charter's own newest rule demanded, for eleven
ladders, a quantity that cannot exist for them. Sections 17's recipe-class and
deterministic-generator clauses landed the same night and are unchanged here.
Nothing in 1.5 was weakened.

Version 1.5 adds the lever-activity clause to section 9 (L-40, Katie's order of
2026-08-08): a load-bearing solver option must be proven ACTIVE in the runtime
log, not merely present in the input dictionary, before any conclusion citing
it ships — after the A3 record was found to have measured its "conditioning
wall" entirely under a transonicPCOption value that is dead code for the
solver that ran. It also adds the mesh birth-certificate rule to section 9.
Nothing in 1.4 was weakened.

Version 1.1 adds section 6, the display layer, after four defects were found in
one day in the space between a correct number and the words printed next to it.
It also adds the archive-replay requirement for detection rules to section 5
and the restated-constant clause to section 8. Nothing in 1.0 was weakened.

Version 1.2 adds section 11, in-sample is not generalization, after a
legitimate field-inversion capability turned out to have a leakage route into a
scored benchmark case that no rule covered. Enforcement moves to section 12 and
gains the gate that checks it. Nothing in 1.1 was weakened.

Version 1.3 adds three things and weakens nothing. Section 3.2, the two ways an
observed order lies, after a divergence fitted a textbook second-order number
and a second ladder fitted an order across a change of mesh recipe. Section
3.3, a guard measures the rungs the fit used, after one fit was declined on
three rungs and certified on four without the fit changing. And section 14,
attribution, after three findings in one week travelled to the wrong file, the
wrong family and the wrong body. Section 4 gains the settle criterion and
section 6 gains four display clauses.

Version 1.4 adds section 16, the negative-verdict review, on the owner's
instruction of 2026-08-07 and with its inaugural instance already on the
record. It weakens nothing: section 8 still ships failed gates as documented
failures, and section 16 is about what happens the morning after one ships.

## 1. The line

> **Done means a gate has a verdict, the verdict cites an artifact, and the
> artifact is still on disk.**

Three clauses, all checkable by somebody who was not there. Drop any one and
the result becomes a memory.

The lab has already lost a headline to the third clause alone. F2's transonic
validation number was real, reproduced afterwards to every published digit, and
for two days nobody could tell it from a fabrication, because the run that
produced it had been executed against a scratch ledger that was then thrown
away. Thirty-four seconds of compute would have retained it. L-27.

## 2. Gate versus reference

These are two different columns and the lab already prints them as two columns.

**A gate is a criterion the lab sets, and the run either meets it or does
not.** Mesh quality, convergence, stationarity, a banded deviation declared in
advance. A gate has a verdict.

**A reference is an external number the result is compared against.** A
published experiment, a benchmark case, a correlation, an exact solution. A
reference produces a deviation, not a verdict, unless a band around it was
declared before the run.

The gate table's columns are the canonical shape and any report reproduces
them:

    | act | gate | reference | measured | deviation | verdict | artifact |

Worked, from the lab's own table:

| act | gate | reference | measured | deviation | verdict |
| --- | --- | --- | --- | --- | --- |
| Cylinder vortex shedding, Re 100 | Strouhal vs Roshko-Williamson correlation | 0.1590 | 0.1578 | 0.77% | PASS |
| NASA wall-mounted hump | Separation and reattachment x/c vs NASA experiment | sep 0.665, reatt 1.100 | sep 0.6544, reatt 1.2534 | -1.6% and +13.9% | VALIDATED |
| ONERA M6 wing | Primal residual vs its own tolerance | 1e-08 | 1.02e-06 | did not satisfy | UNCONVERGED |

The M6 row is the one to study. Its intended gate was Cp at seven spanwise
stations against AGARD AR-138, and that gate was never evaluated, because the
convergence gate upstream of it failed. The row says so in the gate column
rather than quietly reporting the deviation it did manage to compute. **A gate
that was not reached is stated as not reached, never replaced by a nearer gate
that was.**

**The verdict vocabulary is fixed.** Gate verdicts: PASS, GATE REACHED, GATE
FAIL, NOT A RESULT, BLOCKED. Fidelity chips, which are a different axis and
live in `sdk/chief_engineer/lab.py`: VALIDATED for a published experiment
inside its band, SOLVER-BACKED for a real solve with no like-for-like
experimental comparison, RESEARCH MODEL for an honestly labelled reduced-order
screen, UNCONVERGED when the solve did not settle and the number is not
evidence yet. Honesty is carried by the value, its interval, the chip and the
uncertainty channels, never by hedging prose.

## 2a. The identity test: a gate declares its own failure mode at creation (Katie, 2026-08-11)

> **Every gate answers two questions before it is a gate:**
> **(1) What result would make this gate FAIL?**
> **(2) Could a wrong treatment still PASS it?**
>
> **A gate whose quantity is derivable by construction from its own inputs is an
> IDENTITY, not a control. It may be reported. It may never be gated on.**

**The distinction is not subtle once stated, and it is nearly invisible in practice.** A
control tests a claim about the world, so a wrong treatment fails it. An identity tests
arithmetic, so a wrong treatment reproduces it exactly, and reports a clean PASS while
being wrong about everything the gate existed to check.

**The instance that earned the rule, on 2026-08-11.** Gate G-P4 asked that a posterior
treatment reproduce the plateau balance of a prior run. It was re-based, in good faith and
inside a correction, onto `|g_penalty| = 2·λ_L2·‖β−1‖₂`, a quantity **any** treatment that
knows λ_L2 and β computes exactly, including one whose posterior is wrong. The re-basing
replaced a control that could fail with one that could not, and the informative leg it
discarded, the **cosine**, which carries whether the prior pull actually opposed the
likelihood gradient, was the only part testing the balance at all.

The tell was available at creation and nobody asked for it: *could a wrong treatment still
pass this?* For the analytic quantity the answer is yes, trivially, by algebra.

**Sibling failures this same test catches**, all found in one day:

- An acceptance band calibrated from a defective run, then used to grade its successor.
- A random-seed test whose two arms could not differ.
- A cross-check whose divisor had been **fitted to the printed value** in a sibling
  document, a check solved for by requiring it to pass.

**What to write down.** The two answers go in the gate's own text, beside the threshold,
in the pre-registration where the gate is fixed. *"This gate fails if X"* and *"a wrong
treatment could still pass it by Y, which is why Z is also gated"*, or the honest
alternative, *"we know of no way a wrong treatment passes this"*, which is a claim a grader
can attack.

**Reporting an identity is encouraged.** `|g_penalty|` computed exactly from a file on disk
is a useful cross-check on arithmetic and provenance, and it belongs in the record. It is
the *gating* that is forbidden: a threshold on a quantity that cannot miss is a green light
wired to nothing.

## 2b. Pre-registration amendment: legal only while there is no answer to tune to (Katie, 2026-08-11)

A pre-registration is frozen against improvement (L-44), and the freeze is not ceremony:
**it is the entire evidentiary content of the document.** A pre-registration proves one
thing, that the gate could not have been chosen to fit the answer, and an amendment made
after the answer exists destroys exactly that.

**So the rule follows the property rather than the calendar:**

1. **Before first compute, amendments are legal.** There is no answer to tune to, so the
   protected property is intact. The amendment must **state that condition and how it was
   checked**: name the run directory that does not exist, or the empty registry query.
   Asserting it is not enough; the check is the point.
2. **After first compute, gates are closed.** Changes land only as **dated addenda that
   cannot alter a gate, a threshold, a cap or a label.** An addendum may record, correct a
   citation, or note that a gate was later found defective. The last of those is a
   *finding*, and it belongs in the docket and the results record, never as a quiet edit to
   the bar.
3. **Originals are always retained and struck, never rewritten**, under either condition.

**Worked example, same day.** `S1_PRIORS_PREREGISTRATION.md` had its §8 withdrawn and its
gate G-P4 restored. Legal, because no `S1-priors` run directory existed (checked, not
assumed), and the amendment says so on its face. Had one solve run, the correct action
would have been an addendum recording that G-P4 as written was an identity, and a **failed
gate shipped as a documented failure** under §8 of this charter rather than a repaired one.

## 3. The three-rung climb, and the hard ladder rule

A case reaches done through three rungs, and the record names which one it is
on.

1. **Feasibility.** It runs, it does not crash, residuals fall.
2. **Physics.** The mechanism the case exists to show is visibly present before
   convergence.
3. **Gate.** The criterion is evaluated and graded against the reference.

Real, from the hump, with its cost per rung: feasibility 0 to 100 iterations,
4.25 s, 0.28 core-minutes. Physics 0 to 800 iterations, 37.58 s, 2.51
core-minutes, separation bubble present with skin-friction sign changes at
x/c 0.65 and 1.26. Gate 800 to 1772 iterations, auto-converged on
`residualControl`, 36.99 s, 2.47 core-minutes, compared against NASA's own
published experimental data.

**The hard ladder rule.** A failed gate blocks every downstream rung. F7b and
F7c are recorded BLOCKED on F7a's gate failure and stay blocked. A downstream
rung run on a failed foundation is not a result, it is a second unexplained
number.

### 3.1 Dimensionality decides exactly one thing

A refinement ladder's representative mesh size is `h = (1/N)^(1/dim)`. Cell
counts cannot reveal `dim`, so `dim` is an assumption on every fit, and the
following is what that assumption can and cannot do.

> Changing the assumed dimensionality divides every observed order by exactly
> 1.5 and leaves both the extrapolated value and a conclusive ladder's band
> untouched, because the refinement ratio raised to the order is invariant
> under the change. The assumption cannot corrupt a band. It can only wrongly
> admit or wrongly reject one.

**This was verified numerically before it was written here, and the exact
result is on the record.** Four synthetic ladders built to a known order (a
constant ratio triple, a non constant ratio triple, a steep one, a shallow
one) plus the real cylinder vortex shedding ladder, each fitted at `dim=3` and
at `dim=2` through `uq.eca_hoekstra_band` and `uq.ladder_band`:

| Quantity | Result |
| --- | --- |
| Observed order, `p(dim=3) / p(dim=2)`, from the unrounded fit | 1.5 on every case, worst deviation 9e-16 relative |
| The same ratio computed from the stored `observed_order` | 1.5 to 3e-4, because the stored order is rounded to three places. The invariance is exact; the record of it is not, and any check written against stored orders has to allow for the rounding |
| Richardson extrapolated value | identical, worst deviation 5.5e-13 relative, on the real cylinder ladder |
| Band, when the ladder is conclusive at both dimensionalities | identical, worst deviation 1.2e-15 relative |
| Band, when the change moves the ladder across the order window | **not identical**, and this is the whole point |

The mechanism: `log r` scales by `dim`, so `p` scales by `dim`, so `r^p` is
invariant, and every quantity that reaches a published number is built from
`r^p`. The invariance holds exactly for non constant refinement ratios too,
because the `q` correction in the fixed point solve is itself a function of
`r^p` alone.

**The fourth row is the rule.** The band a conclusive ladder states cannot be
corrupted by this assumption. What the assumption decides is whether the
ladder is conclusive at all, and it decides that by moving `p` across the
credible window while nothing physical about the ladder has changed. The
cylinder vortex shedding ladder, cells 2496, 5032, 8640, is the worked case:
`p = 3.633` at `dim=3` and `p = 2.422` at `dim=2`, one outside the window and
one inside it, on identical measurements.

Three rules follow, all of them checkable.

1. **A ladder whose dimensionality is unstated is refused.** Not defaulted.
   `uq.ladder_band` and `uq.eca_hoekstra_band` raise on `dim=None`, and every
   call site names the dimensionality with the mesh fact that justifies it. A
   two dimensional blockMesh with the front and back planes typed `empty` is
   `dim=2`. A closed body meshed by snappyHexMesh is `dim=3`.
2. **A stored study carries the dimensionality its band was fitted with.** A
   study file that does not carry `dim` cannot be audited for the one mistake
   this section exists to name, and a record that omits what it was not told
   to keep looks complete.
3. **A ladder declined for an observed order outside the window must have its
   dimensionality checked before the decline is believed.** That decline is
   the one verdict this assumption can fabricate, and it is the only one.

**Rule 3 now has a checker, and it did not before.** Rules 1 and 2 were
enforced from the day this section was written: the two fits raise on an
unstated `dim`, and the stored study field check reads `dim` off every record.
Rule 3 was the one written as checkable and left unchecked, which is how a
rule becomes decoration. `check_order_window_declines_state_their_dimensionality`
in `scripts/self_audit.py` requires every ladder declined on `order_window` to
carry a dimensionality block established from its own case files, then refits
that ladder from its own stored rungs at the other dimensionality and reports
whether the guard would flip. A flip that would make the ladder conclusive is a
fault, because the published decline would then rest on the assumption rather
than on the measurements.

**What it found, on the four stored ladders declined this way, 2026-08-01.**
Two of the four would pass `order_window` if their meshes were two dimensional:
ahmed_35 reads 3.169 at `dim=3` and 2.113 at `dim=2`, naca0012_wing 3.173 and
2.115. Neither verdict moves, because each is held by a second guard that does
not depend on dimensionality at all, and both meshes are established at three
from their own `checkMesh` logs. The other two do not even flip:
motorBike 7.298 and 4.865, naca4412_wing 10.467 and 6.978, outside the window
read either way. So the assumption is currently deciding nothing on this
corpus, which is the answer the check exists to produce and is worth exactly as
much as the day it stops being true.

**What this section does not license.** Refitting a ladder at a different
dimensionality to move it across the window is falsification of the record
unless the mesh itself says so. The justification is the blockMeshDict or the
mesher, quoted, not the answer that comes out.

### 3.2 The two ways an observed order lies

Section 3.1 is about a number that is wrong by a known factor. This section is
about two numbers that are not wrong at all and are not observed orders. Both
survive the check most readers actually perform, which is that an order exists
and looks plausible.

> **An observed order is not evidence of convergence. It is a slope, and a
> slope can be fitted through a divergence and through a change of experiment.**

**The first way: a credible order on a diverging ladder.** The B-52 ladder's
fourth rung made the fit succeed at `p = 2.253`, monotone, inside the credible
window 0.5 to 4. That reads as a textbook second-order result and it is a
divergence. Its increments **grow** at every step, 0.001857 then 0.002377 then
0.002702, and the Richardson value 0.06484 lands **24 percent above the highest
rung measured**. Monotone is not the same as converging: a sequence can move in
one direction with increasing steps, and a least-squares slope through it is a
number rather than an error estimate. The band halved to 0.006349, 13.451
percent of the working value, and `uq.reportable_band` still correctly returns
`None`. `demo-output/website/campaign/NOT_PASSING_REGISTER.md` line 516,
`models/curriculum/uq-studies/b52.json`.

> **[AMENDED 2026-08-10 — chief ruling `7abb0ba3`. The B-52 ladder's "turn" is WITHDRAWN as a
> claim; see `demo-output/website/campaign/B52_TURN_WITHDRAWAL_2026-08-10.md`.
> **The teaching example STANDS and gets stronger, not weaker.** What changes is the REASON to
> reject the ladder. It was *"its increments grow, so it is a divergence"*. It is now: **the
> increments were never measured against the mesh-construction scatter of their own rungs, and
> when they finally were, the largest of them turned out to be `max(rung 6) − min(rung 7)` of
> eight same-recipe draws — a selected extremum, re-estimating to +8.2e-5 ± 1.2e-3, opposite in
> sign.** That is a better lesson because it generalises to EVERY ladder rather than to diverging
> ones: a credible-looking `p` can sit on top of differences nobody has bounded. The specific
> phrases *"its increments grow at every step"* and *"it is a divergence"* are withdrawn as
> statements about this ladder; `uq.reportable_band` returning `None` was correct then and is
> correct now. Original text retained above.]**

> **[CITATION HAZARD, flagged and fixed the same day: this paragraph cites
> `NOT_PASSING_REGISTER.md` BY LINE NUMBER, and that register received a dated amendment on
> 2026-08-10 which moves every line below the insertion point. A by-line-number citation across
> files rots silently on any edit. Read the citation as pointing to the register's **§B-52
> entry**, by heading, not by line.]**

**The second way: an order fitted across a change of recipe.** The second NACA
4412 ladder reported `p = 10.467` on rungs of 27,237 / 67,826 / 137,569 cells.
Read from the dictionaries, coarse and medium are both `level (2 3)` and differ
only in background block density; production alone is `level (3 4)`. Rungs that
do not share a refinement recipe are not extrapolation-comparable, so that
number is fitted across a change of experiment and **is not a discretization
order at all**. Two of the three rungs also never converged, both running to a
180-iteration cap with `grep -c "SIMPLE solution converged"` returning zero.
Same register, line 548, and `models/curriculum/uq-studies/naca4412_wing.json`.

**What follows, and all four are checkable before any compute is spent.**

1. **A reported order is accompanied or it is not reported.** On the same row:
   monotonicity, the direction of the increments, where the Richardson value
   lands relative to the highest rung measured, the assumed dimensionality, and
   whether the rungs share one mesh recipe. Five facts, none of them a new
   measurement, all of them derivable from the rungs already stored.
2. **Growing increments refuse the fit.** Not a caveat on the fit, a refusal.
   An extrapolation outside the measured range is an extrapolation the ladder
   does not support, and the guard that catches it is independent of
   dimensionality, which is what makes it the useful one.
3. **A recipe audit precedes an order.** The B-52's `recipe_audit` set the
   standard in this corpus and it is cheap: read the refinement level from each
   rung's own dictionary and refuse a triple that does not share one.
4. **An order inside the credible window earns no presumption.** The window
   filters implausible numbers. It does not certify plausible ones, and both
   failures here are inside it or trivially outside it while being wrong for
   reasons the window cannot see.

### 3.3 A guard measures the rungs the fit used

A verdict on a ladder is produced by two things: a fit, and a guard on the fit.
If the guard reads a different set of rungs than the fit did, one fit has more
than one verdict, and which one you get is decided by what the caller happened
to pass.

Both certifiers used to fit the finest three rungs and then measure the
conservative fallback band and the extrapolation-guard tolerance over **every**
rung handed in. Extra rungs widened the range that the guard is a fraction of,
without ever entering the fit. Measured on the flat plate, rungs
3264 / 13056 / 52224:

| Handed in | Where the Richardson value 0.00287237 sits | Verdict |
| --- | --- | --- |
| the three rungs of the fit | 21.16 percent of the range width above the top | **DECLINED** |
| the same three, with the coarse 816 rung in front | 8.48 percent of a wider range width above the top | **CERTIFIED** at 1.99087e-5 |

Same fit, same rungs fitted, same Richardson value, two verdicts. `_asymptotic_guard`
now takes only the fit triple, and `ladder_band`'s factor-3 fallback is the fit
triple's range. Commit `5675eb6b`.

**The rule, and it binds every guard the lab writes, not this one.** A guard
states the sample it measured over, and that sample is the sample the quantity
was computed from. A tolerance measured over a superset is measuring the
caller, not the fit.

**A constant that was calibrated on the defect loses its calibration, and it
does not get moved to restore the margin.** `EXTRAPOLATION_TOL_FRAC` was read
off a "good case" that turned out to be the four-rung call. Re-read on
three-rung fixtures, the flat plate's finest triple clears 0.15 by 1.30x rather
than the 1.77x claimed, and the B-52 still fails it by a factor of 16. The
> **[AMENDED 2026-08-10: the "factor of 16" is the gap between two `extrapolation_sanity` fixtures whose UPPER anchor is the B-52 — a Richardson extrapolate on a noise-dominated triple, which is not a stable quantity, so the margin is not a measurement. The tolerance 0.15 is deliberately UNCHANGED (chief ruling 6): recorded as a standing weakness, not patched. The recipe-audit-precedes-an-order precedent is unaffected.]**
constant keeps its value and loses its stated justification, which is recorded
rather than repaired: moving it to restore the old-looking margin would be
tuning the gate to the answer, which section 8 forbids.

### 3.3a A refit reads the solved values, not the printed ones

Section 3.3 is about a guard reading a different sample from the fit. This one
is about a fit reading a different *precision* from the solve, and it is the
same class of error one layer down.

> **A refit reads the artifact the solver wrote. A rendered table is not that
> artifact: it has already thrown away the digits the refit needs, and how many
> it needed is a property of the ladder, not of the reader.**

**The worked case, and both readings are on the record.** The supersonic wedge
ladder was extrapolated twice from the same three rungs. Fitted on the values
as the act's ladder table *prints* them, at three decimals (47.588 / 46.123 /
44.693), the extrapolated shock angle is **−13.733 degrees**. Fitted on what
the act *solved* (47.58767882153372 / 46.12330850878531 / 44.692792746510406),
it is **−15.753**. Two point zero two degrees apart, and the entire difference
is rounding. `demo-output/website/campaign/W3_2D_LADDER_REFIT.md` §4a;
`sdk/tests/test_uq.py::test_rounding_the_rungs_moves_the_digit_and_not_the_verdict`
pins the pair.

**Why the size of that difference is not a coincidence.** At an observed order
near zero the Richardson extrapolation amplifies the finest increment by a
large factor: **42.25** on that ladder, against an observed order of 0.034.
Whatever error the stored rungs carry is multiplied by exactly the same factor.
So the worse a ladder behaves, the more its refit depends on precision nobody
is thinking about, and the ladders most likely to be refitted are the badly
behaved ones. The same rounding moved the cone's order 0.801 → 0.800, the
diamond's 6.233 → 6.296 and vortex shedding's 2.436 → 2.430, none of which
changes a guard or a verdict, because none of those is near-zero order.

**Nothing that decides anything moved on the wedge either**, and the clause
says so rather than overclaiming: `guards_failed` is
`['order_window', 'extrapolation_sanity']` on both readings, `conclusive` is
False on both, `reportable_band` is `None` on both, and the angle is physically
impossible on both. The rule is here because the next ladder in this regime may
not be so forgiving, not because this one was harmed.

**What follows, all checkable before any compute is spent.**

1. **A refit names the artifact it read**, and that artifact is the one the
   solver wrote (a forces file, a coefficient file, a stored `levels[]` block),
   never a document. A refit that cannot name one is not a refit.
2. **An extrapolation is reported with its amplification.** The factor is
   `|phi0 − phi_fine| / |e21|`, arithmetic on rungs already stored, and it is
   the single number that says whether the input precision matters.
3. **`scripts/self_audit.py` checks the corpus weekly**
   (`check_stored_rungs_carry_solved_precision`). It computes, per study, how
   far half a unit in the last stored decimal reaches after amplification, and
   reports any ladder where that reach exceeds a tenth of the study's own band.
   At this clause's writing all six extrapolating curriculum ladders store 10
   to 18 decimals against amplifications of 0.02 to 3.48, so the reach is under
   1e-10 of bands of order 1e-3 to 1e-2. The check guards the corpus going
   forward; it would not have caught the wedge, whose ladder lives in a
   campaign document rather than in this corpus, and it says so.

### 3.4 A reportable band is not a demonstrated asymptotic order

Sections 3.2 and 3.3 are about orders that are wrong or verdicts that are
unstable. This one is about a ladder where nothing is wrong and the record can
still be read as claiming more than it holds.

> **A conclusive ladder has earned a quotable band. It has not thereby shown
> that it is in the asymptotic range, and the two are separate claims with
> separate evidence.** The band is what the guards certify. The asymptotic
> range is a statement about the ORDER, and the only evidence for it is that
> the order stops moving as rungs are added.

**The worked case is the lab's best verification result, which is why it is
here.** The 2D flat plate is the first family in this corpus the Eca-Hoekstra
certifier declares conclusive, on the finest triple, on both functionals: Cd at
observed order 1.634 with a reportable band of 4.244e-6, 0.148 percent of the
value. That band is earned and quotable. **The observed order behind it is
still rising at every rung added: 1.0833, then 1.2587, then 1.6344 for Cd, and
1.0315, 1.1110, 1.5281 for Cf.** A settled ladder shows a settled order, and
this one has not settled.

Two independent causes are on the record, and neither is a defect in the
result:

1. The grid family is not exactly self similar. The wall normal total expansion
   ratio is held fixed while ny doubles, so successive first cell heights ratio
   1.815, 1.905, 1.952, 1.976, approaching 2 from below. An order fitted at a
   constant refinement ratio of 2 is therefore biased low on the coarse rungs
   and less so on the fine ones, which drifts the order upward with refinement
   on its own.
2. The reference codes drift the same way on NASA's own grids with NASA's own
   published values: CFL3D 0.9468, 1.0611, 1.3383 and FUN3D 0.8172, 0.9784,
   1.0703, neither conclusive on any triple under the same certifier. The drift
   is the behaviour of this case, not of this lab's meshes.

**The rule.** A record that states a conclusive band states, on the same
surface, whether the observed order has settled, and it says which of the two
claims it is making. "Conclusive", "certified" and "reportable band" are
verdicts about the band. "Asymptotic" is a verdict about the order and is not
implied by any of them. Where the order is still moving, the record says so and
quotes the sequence, because the sequence is already on disk and costs nothing
to print.

**What this does not do.** It does not withdraw or weaken the band. The flat
plate's 0.148 percent stands exactly as certified. The claim being fenced off
is the one nobody made and every reader is one sentence away from making.

## 4. Convergence. What may be read, and what may not

This section is almost entirely lessons, because almost every one of them was
paid for.

**Read the solver's own statement, not a residual you chose.**

    grep -c "SIMPLE solution converged" log.<solver>
    grep -E "ConvergedReason" <log>

- **L-14.** OpenFOAM prints an Initial and a Final residual per field per
  iteration. `residualControl` gates on the Initial. The Final is smaller,
  sometimes by orders of magnitude, sits in the same block of output, and
  flatters the result. A hump perturbation point was carried forward as
  converged on `k 1.67e-9` and `omega 4.25e-11`, both Final residuals, while
  the Initial residuals sat 10 to 150 times over the gate with omega rising
  over the last 1200 iterations. It cost a whole conclusion, and the finding
  reversed rather than weakened.
- **L-15.** Exit code zero is not convergence. Both derivative solves in an
  adjoint run returned PETSc `ConvergedReason: -5`, DIVERGED_BREAKDOWN, with
  the residual collapsing to about 1e-322, and the solver then printed
  "Residual tolerance satisfied, solution finished!" and exited zero.
  Underflow satisfies any test written as `res < tol`. **A residual many orders
  below its tolerance deserves suspicion, not satisfaction.**
- **L-21.** A gate can name a field the model does not transport, in which case
  it can never fire. Three Reynolds-stress-model duct cases inherited
  `residualControl { k 5e-6; omega 1e-10; }` from an eddy-viscosity template.
  None of the three transports k or omega. Two runs ground on for over two
  hours each while already converged. This one is checkable before any compute
  is spent, and `scripts/case_preflight.sh` now checks it.
- **L-24.** A run is not converged. A **quantity** is converged. F9's six
  reference runs were correctly judged stationary on the throat differential
  and the same files publish a downstream differential that fails outright, at
  three of the cases with peak-to-trough bands of 39, 113 and 128 percent of
  its own mean. Nobody had looked, because the question had been framed as
  whether the run converged. **Apply the gate to every signal the study reports
  as a number.**
- **L-19.** Interrupted and diverged look identical from outside. Relaunch and
  compare the coefficient history at matching iterations. Bit-identical values
  prove the failure is deterministic and in the case setup.

**An iteration cap is a budget, not a settle criterion, and a rung stopped by
one says so.** A cap is a number somebody guessed before the run. A rung that
reaches it has not converged, it has run out of money, and the two are recorded
differently or the ladder inherits the guess as if it were a measurement.

The 208896-cell flat plate rung was asked for 15000 iterations. At 15000 its Cd
read 0.0028936144511, **1.05 percent above the value it eventually settles at,
still falling by 1.04e-5 per thousand iterations**, with a trailing spread of
4.44e-7 against the module's own 1e-7 gate. It took **36000** iterations to
settle. Accepted as settled, that one rung turns the finest triple's increments
from shrinking into growing and publishes the whole ladder as a divergence at
`p = -0.745`. The cap decided the ladder, and nothing in the record said a cap
had been involved.

Three rules, and they are already in force in `sdk/workflows/tmr_verification.py`
under commit `ec7ca9d5`.

1. **A rung stops when the monitored coefficient stops moving**, measured as a
   peak-to-peak spread over a trailing window at or under a stated tolerance,
   with the iteration cap demoted to a backstop. The flatness measure drives
   the run instead of judging it after a guess has already decided the answer.
2. **The record carries `settled` and the verdict that produced it.** A rung
   that hit its backstop is recorded backstop-stopped, never settled. Three
   bump rungs and one plate rung in the current corpus ran to their caps
   unsettled and the record now says which, without any published number
   changing.
3. **The exposure is reported, not patched over.** Where a cap-stopped rung
   already sits inside a published ladder, both the ladder and the fact are
   stated, per L-1. This is L-24 one level up: a run is not converged, a
   quantity is, and a quantity is not converged because an iteration counter
   reached a number somebody chose.

**A diverged run poisons its own diagnostics.** Every derived quantity is
downstream of the divergence. L-19's corollary: a y-plus of 113 average on a
mesh four times finer than one reading 0.351 is not a mesh-sizing problem to go
fix, it is the diverged velocity field feeding back.

## 5. Detectors, metrics and signs

Four checks that cost nothing and have each already invalidated a published
conclusion or a rule the lab was trusting.

**State the detector's resolution next to every number it produces. Never
claim a difference below one increment.** L-28. F2's shock detector returns the
midpoint of the steepest sampled pair, the samples are mesh-fixed face centres,
only 21 fall inside its window, and across 280 solves at 280 different flow
conditions it emitted eight distinct values. The pitch between the reported
0.55607646 and the next representable value is 0.052364 chord. The claimed
deviation was 0.043924 chord. The detector cannot express it. **The tell needs
no code reading: a continuous physical quantity returning a small number of
distinct values across many varied runs is quantised, not converged. Count the
distinct values in the column before you subtract two of them.** Where a banded
pass turns on a single quantisation level, grade the result "not contradicted"
rather than "demonstrated".

**Sweep a derived metric's own free parameter and report the spread beside the
number.** L-25's corollary. F7a produced two separate published root causes, a
coarse-mesh sign flip and a 40 percent improvement from disabling interface
compression, and both evaporated when the same solves were re-measured with a
depth-integrated front metric instead of a fixed-alpha line probe. Both
reversed sign. A mechanism may not be attributed to a diagnostic's behaviour
until the diagnostic has been shown to be metric-independent.

**Establish a source term's sign by controlled experiment, never by reading the
code.** L-26, and this is the sharpest rule in the charter. Eighteen `fvOptions`
dictionaries stated the intended forcing in their own comments, the algebra in
the record agreed with the comment, and the code matched the algebra. Every
check that was run was a reading check. `fvMatrix::operator+=` puts the term on
the right-hand side, so the imposed anisotropy was the perturbation applied
backwards, a reflection of the target through the baseline. It handed 95.93
percent of the hump's cells a Reynolds stress with a negative eigenvalue, and
the solver said so in its own log, and that line was read as physics. **A wrong
sign that happens to converge is far more dangerous than one that crashes.**

The pattern that works, and it is required before any coded source, immersed
forcing or hand-assembled `fvOption` produces a result:

- Construct a case where the source is exactly equivalent to a parameter the
  solver already has, run the reference **with no coded source at all**, and
  check the two collapse onto each other. Laminar periodic hill at Re 100,
  discriminated by the driving pressure gradient: the no-source reference and
  the sourced case agreed to 0.055 and 0.016 percent, and only one sign
  produces that pairing.
- **Make the test discriminating first.** The first attempt at Re 10 was in the
  Stokes limit, where all four runs agree by construction and both hypotheses
  pass. It was discarded.
- Two corollaries that ride with it. A code comment is a claim, not evidence,
  and eighteen files agreeing is one fact rather than eighteen. And any
  Reynolds-stress perturbation carries a realizability audit: the fraction of
  cells with a negative eigenvalue belongs next to the residual in the gate
  record, it is a three-line eigenvalue check, and it would have caught this
  instantly.

**Replay a new detection rule against the archive before adopting it, and
publish its fire rate.** A rule is an instrument and it gets an instrument's
scrutiny. S7, oscillatory divergence, was written from a knowledge base fact
and adopted without replay. Measured afterwards across every steady solver log
the lab has archived, 106 of them, it fires ungated on 68 and reaches FATAL on
65, and every one of those runs completed with its results on the record. Four
tightenings were measured and none rescued it: requiring the residual level to
stop improving still fires on 68, requiring the finding to persist a full
window 40, measuring growth against a 200 iteration baseline 59, raising the
growth factor to four times 23. It also cannot separate the two logs of the
case it was written for. **A rule that fires on two thirds of known-good work
is measuring the population, not the defect.** Required before a rule is
adopted: the replay, the fire count, the fatal count, and the rule's behaviour
on the case that motivated it. A rule that cannot discriminate its own
motivating case is withdrawn, not gated, and if it is kept on reasoning the
archive cannot replay then it is filed as a decision and labelled the weakest
rule in its standard.

**Closed 2026-08-01: S7 was withdrawn**, by supervisor ruling R1 taking option
B on conflict C-2. It was filed as a decision and labelled the weakest rule in
its standard, which is what this section prescribed for the interim, and the
decision went the way the first half of the sentence points: it could not
discriminate its own motivating case, 22 firings on the sick log against 20 on
the healthy one, so it is withdrawn rather than gated. The measurements are
kept beside the entry in `docs/standards/MONITOR_STANDARD.md` because they are
what a replacement rule has to beat. **The first clause of this requirement has
now been exercised once, and the cost of exercising it was one rule.**

## 6. Labels are claims, and the display layer makes them

A number reaches a reader through a caption, a field name and a template. Each
of those is an assertion, and none of them is checked by the solve that
produced the number. This section exists because four defects of exactly that
shape were found in one day, every one of them by somebody looking at something
else, and none of them touched a solver.

**A statistical label may only sit on a value a statistical procedure
produced.** The certificate template printed "95% confidence interval" under
any non-empty envelope string. Acts legitimately put other things in that
field: "converged at iteration 1,734", "5% pass threshold", "this case's own
recipe", "at the design condition", "non-orthogonality 40.5 vs 70 gate". Every
one of those was sealed into a PDF as a statistical claim the run never made.
The worst was a headline rendering as "28.3% +- 0.029620 to 0.021245 at C_L
0.5, 95% confidence interval", a range of drag coefficients printed as a
confidence interval on a percentage: two different quantities, one of them
fictional. **A caption is derived from the value's provenance or it is not
printed.** A fixed caption over a free-form field is a defect at the moment it
is written, not on the day it first lies.

**The asymmetry sets the tuning, and it sets it the same way everywhere in this
layer.** A false positive on the caption check costs a real interval its
caption. A false negative seals a fabricated one. So the interval recogniser is
deliberately conservative: one signed number with an optional unit, anchored
end to end, and anything with prose in it prints as itself. Every check that
guards a published label is tuned that way, including the audit script and the
in-sample gate in section 12.

**A grid refinement band is not a confidence interval.** An Eca and Hoekstra
least-squares band with a safety factor is an uncertainty estimate produced by
a fitting procedure and it carries no confidence level. Five acts, the
supersonic wedge, the supersonic cone, the diamond airfoil, the cylinder wake
and the hypersonic cylinder, each put a bare numerical-channel band into that
envelope: the wedge 44.693 +- 6.880 deg off an observed order p = 0.05, the
cone 27.309 +- 2.757 deg off a ladder that is not asymptotic, the diamond
0.03624 +- 0.00000 off p = 9.44, the hypersonic cylinder 0.4181 +- 0.0431 off
rungs that are not monotone, the wake 0.1578 +- 0.0193 off p = 3.65. All five
ladders are non-conclusive by the uncertainty layer's own flag, and none of the
five acts read the flag.

**One channel presented as a total is a second defect riding on the first.**
Those same five acts passed input and model as absent and never called
`combine_expanded`, so the numerical channel alone stood as the result's
uncertainty. `docs/UNCERTAINTY-DOCTRINE.md` names three channels. A channel
that was not quantified is stated as not quantified and is explicitly not
counted as zero, and where no channel is quantified there is no combined
figure, so the envelope key is absent and the page prints a point estimate. The
measured spread and the reason the ladder is not conclusive both stay on the
page. Nothing gets quieter, only accurate.

**A function that can be non-conclusive must not hand back a number under its
plainest name.** `eca_hoekstra_band` returns `band_abs` whether or not it sets
`conclusive`. On a failed ladder that number is a deliberately conservative
fallback, not a measured uncertainty, and five independent authors each read it
and printed it on a sealed page. **Five independent readers making the same
mistake is a fact about the return shape, not about the readers.** The rule
follows the shape of the fix: the short, obvious accessor returns the value
only when the computation earned the right to state one, and a caller who wants
the fallback reaches past it and names what it is. This binds every
result-bearing function the lab writes, not the one that failed.

That is L-16 in code. A status flag sitting beside a number is a derived signal
that is further from hand than the number itself, and a flag that can be
ignored will be.

**A surface never supplies a statistic the source did not state.** The
certificate defect above is a caption invented over a value. This is its
smaller sibling: a page that filled in the confidence level itself whenever a
verdict carried none, defaulting to 95 percent. All 253 recorded verdicts that
carry a band happen to state 95 percent, so removing the default changed
nothing on screen. **What changed was the licence, and the licence was the
defect.** A surface that is right today because the data happens to agree with
its assumption is a surface that will be wrong on the first record that does
not. Commit `f710fb59`, `sdk/chief_engineer/control_room.html`. The same commit
removed a second shape of the same fault: older verdicts sent the literal
string "n/a" for a band and a level, and the card rendered `0.6544 ± n/a (n/a)`,
which is a number-shaped thing that is not a number. **An absent band is absent
and the value stands alone.**

**A qualifier belongs to the row it was measured on. A grade belongs to all of
them.** The Ahmed report's verdict dictionary was spread into every card, so
the drag comparison's own sentence, "within 7 percent of Ahmed, Ramm and Faltin
1984, C_d 0.285", was appended to the lift card and the mesh row, where a drag
qualifier is nonsense. The distinction is exact and it is worth stating as a
rule rather than as a fix: the fidelity grade travels with every row of one
report, because every row of one report carries one grade; the reason does not,
because it is a statement about one comparison. Commit `6880e4f3`. **A template
that spreads a per-quantity field across per-report rows is a defect at the
moment it is written**, on the same reasoning as the fixed caption over a
free-form field.

**A label is repaired at the source that emits it, never at the surfaces that
render it.** Two defects this week were one string each, and both were reached
by five consumers. A verdict reason carried `Cd` where the typesetter keys on
the underscore to see the index, so one variable arrived as two plain letters
while every other variable on the same surface was set correctly (commit
`63352fce`). And a control-room trace named itself by its series key: stripping
the separator flattened the one variable that really was an index, opening the
separator out set "history" under the C, and **no act-side wording could fix
either, because the character was eaten before the typesetter ever saw it**
(commit `cfe4e383`, and the trace now names itself by the axis label the acts
already send). Neither string was ever a label. The general rule: when a
rendering defect appears on several surfaces at once, the count of surfaces is
evidence about where the fix goes. Repairing it five times leaves the sixth
consumer broken and the source still wrong.

**A configuration a surface declares is a claim about the run.** The hump act
called `roster.set_workers(ranks)` on its warm path, where the mesh and the
solve are both restored from cache, nothing is dispatched, and the elapsed time
is computed across a zero-length interval and clamped to one second before
being spent to the ledger. The declaration is not decoration: it reaches the
worker numeral, the roster and the spend line. **A surface may display a fleet
the run used, or no fleet at all.** The repair is never to move the declaration
earlier so the timing looks better, because that invents a fleet the run never
used, and the standing rule forbids implying anything was prepared in advance.

The general form, and it is the evidence test of section 9 pointed at the
method rather than the result: **anything a surface states about how a number
was produced is subject to the evidence record.** Ranks, wall time, cell count,
solver name, iteration count. If the run did not do it, the surface does not
say it.

## 6a. The referent travels with the verdict (added 2026-08-11)

> **A verdict label (VALIDATED, PASS, verified, confirmed, reproduces) carries
> the thing it was checked against, on every surface it appears on. Where there is
> no external referent, the label says so.**

**This is section 6's rule applied to the one field it kept leaving out.** Section 6
already binds what a surface may say about *how* a number was produced. A verdict
also states *what it was checked against*, and that field has been travelling
optional.

**Why it is a separate clause rather than an obvious consequence.** The B6 audit of
2026-08-11 classified 1,549 verification sections across 297 tracked documents and
found the corpus in better shape than expected: the lab has repeatedly caught and
retracted verifications that could not fail, and one credentials-wall row already
implements the "declares it has none" clause. **The live defect is not blindness.
It is transmission loss.** The referent is stated correctly in the canonical record
and does not survive the trip to the surface people read. Four of that audit's seven
findings are this and nothing else.

Two of them are on **camera surfaces**, which is why this clause is in the charter
rather than in a report:

- A gate names two published authors over a correlation whose constants the repo
  attributes to its own task prompt. The number passes at 0.75% against the form
  actually used and **misses at 5.54% against the form named on screen.**
- A `VALIDATED` chip earned **code-to-code against another solver's tutorial
  documentation**, stated plainly in the case record, which refuses the workshop
  band by name, loses the qualifier on the filmed table, where it then reads as
  the best *experimental* agreement beside two rows that genuinely are.

Neither is a wrong number. Both are a correct number whose meaning did not travel.

**The precedent, and the reason this is a generalisation rather than an invention.**
The lab already built this mechanism once: the rank-1 score carries a *mandatory*
caveat wherever rank is claimed, and nine files move in lockstep on it. That rule
was written for one number. **This is the same rule, unpinned from that number.**

**What satisfies the clause:**

- **EXTERNAL**. A published value, an exact analytic result, a benchmark
  distribution, an independent implementation. Name it specifically. "Validated
  against the literature" names nothing.
- **SELF-REFERENTIAL**. Checked with the same code, helpers or conventions as the
  thing checked. **This is not a defect and must not be hidden.** Transcription
  fidelity is worth having; it is worth having *labelled*, because it is routinely
  read as external.
- **NONE**. Say so. `F9 is verified in part and validated against nothing` is a
  model sentence. It costs nothing and it is impossible to misread.

**The failure this forbids** is L-74's: a check written with the same helpers as the
thing it checks proves only that a number was transcribed faithfully, while the
question everyone believes it answers is whether the number is right. The sharpest
instance found on 2026-08-11 was a cross-check whose divisor had been **fitted to the
printed value in a sibling document**, a check that could not fail, reported as
confirmation.

**Scope.** Load-bearing verdicts: anything a published conclusion rests on, and
anything that reaches a camera surface, a credentials-wall entry or a certificate.
Not working notes.

## 7. FD tables are required for every adjoint

No gradient enters a record, a report or an optimisation without a
finite-difference table beside it.

**The grading standard, current, ~~and applied uniformly, including to cases~~
~~graded under the old band~~ — ⚠ SOURCE SCOPE RESTORED: the study's own heading reads *"Recommended FD tolerance for grading **FUTURE** shape derivatives **ON THIS STACK**"*, so the RETROACTIVITY this clause asserted is not carried from the source — it REVERSES the source's own scope word:** **[⚠ STRUCK IN PLACE 2026-09-04, v1.63 `§2ar`: this clause dropped *"Recommended"*, *"future"*, *"shape derivatives"* and *"on this stack"*, and ADDED a retroactivity the word *"future"* excludes. **This charter MAY set a lab-wide standard on its own authority; what it may NOT do is borrow a study's numbers and silently widen that study's scope to match its own ambition.** NOTHING IS RE-GRADED BY THIS STRIKE, and no grader's or registration's own gate is disturbed.]**

- **PASS** at 5 percent or better on the aggregate **and** zero flagged
  components.
- **CONDITIONAL** between 5 and 15 percent, and it requires a per-component
  breakdown before it can be graded at all.
- **FAIL** above 15 percent **or** on any sign-flipped or unstable component,
  regardless of the aggregate — **RESTORED: the source reads *"> 15 % or any flagged component → FAIL PENDING INVESTIGATION"* (`A_stepsize_study.md:92-94`). *The source's FAIL is PROVISIONAL and names its own remedy; this clause had made it terminal.*** **[⚠ CORRECTED IN PLACE 2026-09-04, v1.63 `§2ar`. The band VALUES are unchanged and NOTHING IS RE-GRADED; what is restored is that a FAIL from this band carries an investigation obligation, not a full stop.]**

The earlier "1 to 12 percent is normal" band was inferred from a single rung
and is **retired**. A charter that let a retired band keep grading would be
worse than none.

**The reporting protocol, ~~five steps, none optional~~ RECOMMENDED — five steps:** **[⚠ STRUCK IN PLACE 2026-09-04, v1.63 `§2ar`: the source reads *"Recommended protocol:"* (`A_stepsize_study.md:82-83`); *"none optional"* was added here. ⚠ AND THE LIST IS A REMIX, WHICH IS THE ROOT CAUSE OF `§2aq`: the source's own item 5 IS THE BANDS (`:92-94`), promoted out of this list into the standalone standard above — and step 5 here was filled from a DIFFERENT heading, *"Recommended FD step size"* (`:72-77`). **A recommendation from one section was renumbered into a list captioned "none optional".** Nothing is re-graded.]**

1. Confirm the step sits in the well-converged plateau with a two or three
   point mini-sweep. Not assumed.
2. Report per-component or cosine-similarity agreement alongside the aggregate
   percentage.
3. Flag any component whose FD value changes sign, or moves by more than 50
   percent of its own magnitude across one decade of step. That is a real
   defect signature, not noise.
4. The harness-sound floor ~~on this stack~~ **for THIS DATASET** — the source says *"this dataset's"*, and the transcription widened one study into a whole stack (`§2al`, v1.56) — for a case with no flagged
   components, is 2.5 to 5 percent vector-norm relative error, **on a STATED BASE OF n=2 THAT THIS CLAUSE DROPPED: 2.5-3.0 % at 4,032 cells, and A2's 1.71 % at 38,304 cells / 96 DVs — *"consistent with the floor TIGHTENING ON FINER MESHES"*.** ~~A number below
   that is a claim about the harness.~~ **[⚠ STRUCK IN PLACE 2026-09-03, v1.56 `§2al`: THIS SENTENCE APPEARS NOWHERE IN THE SOURCE and is CONTRADICTED BY the source's own SECOND DATA POINT, which is BELOW the floor and is read there as CONFIRMING it. On a FINE MESH a sub-floor number is WHAT THE ESTABLISHING STUDY PREDICTS, not an anomaly and not a claim about the harness. Nothing was ever gated on it and NOTHING IS RE-GRADED — the floor's own interval, 2.5-5 %, is UNCHANGED.]**
5. Central differences, `step_calc=abs`, step ~~between 1e-3 and 1e-2~~ **RECOMMENDED between 1e-3 and 1e-2 FOR A1's FFD CONTROL POINTS — the source's heading is *"Recommended FD step size"* and BOTH ITS MECHANISMS WERE DROPPED HERE: the lower bound is where the CD difference falls under the PRIMAL'S OWN RESIDUAL NOISE FLOOR (`primalMinResTol=1e-8`, degrading 11.5 % → 95 % from 1e-4 to 1e-8), and the upper is where A1's LEADING-EDGE CONTROL POINT idx6 drives the primal non-convergent (documented failures at 5e-2 and 1e-1). THE MECHANISMS TRANSFER; THE NUMBERS DO NOT.** **[⚠ STRUCK IN PLACE 2026-09-04, v1.62 `§2aq`: this clause transcribed a RECOMMENDATION as a bare requirement, dropping *"Recommended"*, the case, the DV class and both mechanisms — `§2al`'s defect class 1 (a widening) from the SAME SOURCE at the ADJACENT STEP. It is NOT a lab-wide gate and never was. NOTHING IS RE-GRADED and no registration's own gate is disturbed.]**

**Three table shapes, all in use, pick by what is being graded.**

Per-derivative summary, for a rung whose gradient is a small set of named
derivatives:

    | derivative | analytic (Jan) | FD (Jfd) | abs error | rel error |

Per-component with an explicit sign-match column, which is the shape that
catches the failure the standard is built around:

    | idx | analytic | FD (step) | rel. err % | sign match |

A5 ran 27 components this way and reported 5 within band, 46.6 percent
aggregate and two sign flips, which is a FAIL under the current standard and
reads as one at a glance.

Step-size sweep, required whenever step 1 is being established or a
disagreement is being diagnosed, and it reports its failures as rows:

    | step | rel err | rel err (excl. flagged) | cosine | status |

with entries like `FAILED: primal did not converge for idx6 (+step); residual
stalled at 4.8e-5 vs 1e-8 tolerance`. A sweep that hides its failed steps is
reporting a plateau it did not measure.

**Do not prescribe "converge harder" before checking whether convergence is
available.** L-7. A plateau that survives a tenfold iteration increase is a
genuine fixed point of the discrete iteration, and tightening tolerances cannot
help. Iterations 1000 through 10000 produced bit-identical residuals on the
case where this was tested, and the FD aggregate error moved from 46.64 to
46.21 percent, which is no material change. The next lever is mesh resolution
or geometry smoothness.

## 8. Failed gates ship as documented failures

This is not a concession. It is the requirement.

A failed gate is written up to the same standard as a passing one and lands in
`demo-output/website/campaign/NOT_PASSING_REGISTER.md`, whose own format is the
template:

> case, what it was trying to show, how it failed with the exact error,
> residual or percentage, whether the root cause is known, what it would take
> to resolve, and where the evidence lives.

And its own tone line, which is the point of the whole section: a register of
honest failures, read as an asset. **A documented failure with a named cause is
a result.**

**Three things a failure write-up may not do.**

1. **Claim refutation where the experiment did not run properly.** L-3. The
   NACA 4412 re-mesh drove layer coverage from 58.3 to 4.36 percent, the
   opposite of intended, so the hypothesis it was built to test is still
   untested, not refuted. The run was not wasted: it produced a real incidental
   finding, that Cd is invariant to boundary-layer coverage on that rung to
   0.02 percent across a thirteenfold collapse in resolved boundary layer.
2. **Claim refutation where the instrument could not have seen the effect.**
   L-25. F7a recorded wall friction as refuted on a mesh where the leading film
   was one cell deep, so no-slip and slip were both effectively frictionless
   and had to agree. The correct entry was "not measurable at this resolution".
   Re-run at a/128 the same control separates by 5.5 percentage points, and it
   was friction. **A null result is evidence of absence only when the
   instrument could have seen it.**
3. **Attribute a crash or a resource failure to a case without that case's own
   primary evidence.** L-22, and this is a standing rule with its own exact
   wording. An entry naming a case in an OOM, SIGFPE, SIGSEGV, kernel kill or
   infrastructure claim must cite the kernel message, the solver's own abort
   line, or the log path and timestamp of the run in question. "Consistent with
   the pattern documented for another case" is fine as an explicitly labelled
   inference and must never be silently upgraded to a statement of fact.
   Convergence-failure and wrong-answer entries do not need a kernel trace,
   because the residual history or the physical result is the primary evidence
   and is usually attached already.

**A gate is never widened after a result misses it.** Mesh gate thresholds live
in `docs/physics_rules.yaml` and never as constants in workflow code, precisely
so that moving one is a visible edit to a governed file. Enforcement code is
never edited to move a threshold silently.

**A threshold that lives in two places is already wrong in one of them.** The
S9 wall-time flag was corrected from 20 times a solver's running 99th
percentile back to the 10 times the owner actually approved, and the correction
landed on the shared constant. `LogMonitor.check_wall_time` kept its own
literal 20.0 as a default argument, so for five days every caller taking the
monitor default judged runs against a threshold nobody had approved, while the
governed constant read correctly and anyone who checked the governed file would
have been satisfied. **[BLAST RADIUS CORRECTED, 2026-08-10: "every caller"
was the TEST SUITE. `LogMonitor.check_wall_time` is called by nothing else --
not by `HeadEngineer`, not by the ledger path, which reaches S9 through
`wall_time_record_field`. No production run was ever judged on the unapproved
default. The restated-constant lesson below is untouched and still right; only
the exposure was overstated, and a record that overstates its blast radius
spends the same credibility as one that understates it.]** **A restated constant is a defect at review whether or not
it currently agrees with its source**, because on the day it stops agreeing
nothing announces it. Read the constant, and pin the two together with a test
that fails when they diverge. This is the same clause as the paragraph above,
pointed at the case where nobody widened anything and the gate moved anyway.

**None of this conflicts with the no-failures-on-camera rule.** The demo
discretion charter is explicit that it governs the promotional surface only and
has no authority anywhere else, and that the campaign records, `LESSONS.md` and
`NOT_PASSING_REGISTER.md` stay complete and unredacted. A failed gate is
written up in full and is not filmed. Both rules hold at once, and anyone who
reads them as being in tension has read the demo charter's scope clause wrong.

## 9. The evidence record

**No result without one.** An evidence record is:

- The primary log, containing the solver's own convergence statement or reason.
- The coefficient or sampled-data file the number was read from.
- The case dictionaries, so the setup is inspectable.
- The gate verdict and the reference identity.
- The detector resolution for every quantity reported, per section 5.
- **`levers_verified_active` (v1.5, L-40): every load-bearing option**. Each
  solver option, flag, model choice or lever the conclusion's reasoning cites
  (preconditioners, turbulence-model switches, scheme selections, MRF settings,
  adjoint modes), **listed with the runtime-log line proving it actually ran.**
  THE SWITCH YOU SET IS NOT THE SWITCH THAT RAN: "configured" and "active" are
  different claims, and only the second is evidence. A dictionary entry can be
  dead code for the solver that executed (the A3 record measured its
  "conditioning wall" entirely under `transonicPCOption: 2`, which exists only
  in a different solver's source; every archived M6 script set it and none of
  them ran it). A conclusion citing a lever with no activity proof FAILS
  REVIEW; if the archived log cannot prove activity either way, the lever is
  reported **unverifiable-from-logs** and the conclusion carries that caveat on
  its face.
- **`ran_before_found` (v1.6, D2): absence of error evidence is not evidence of
  a clean result.** Every parser and gate answers **did the check run** before
  **what did it find**, and carries a THIRD verdict for *unknown* that is not
  collapsed into the bad one. Checked-and-found-bad and we-do-not-know are
  different facts: conflating them impugns work whose only fault is a missing
  log, which is the opposite error and just as wrong. The rule exists because a
  mesh-quality parser returned `clean` on a log where the tool had fatally
  errored (it matched error PATTERNS, and a crashed log contains none), and
  the guard believed to be covering that case did not, because the tool prints
  its cell count BEFORE the checks it dies in. A gate that reads silence as
  success can manufacture a pass, which outranks every gate that merely misses
  one (L-45).

- **Mesh birth certificate (v1.5): every mesh entering an archive, a
  pre-registration or a ladder rung carries its checkMesh record at creation.**
  Born clean or it does not enter; a mesh whose birth certificate is missing is
  quarantined from new work until checkMesh is run and attached. (The A3
  vcoarse mesh was born with 23 negative-volume cells and aspect ratio 2.08e95
  and sat in the archive as a usable rung; the pyHyp tip-collapse pathology is
  cross-geometry, per the TMR NACA 0012 finding and the M6 specimen.)

**Retained under the campaign, not left in scratch.** L-27, and it applies to
work done outside the batch machinery, which is exactly the work that gets
lost. A pre-batch validation-gate solve is never going to appear in a batch
ledger, so "I searched the ledger and it is not there" is evidence about the
ledger and not about the world.

**Two words that are not interchangeable.** When a number cannot be found,
report it as **unreconstructible** and try to reproduce it before reporting it
as **unsupported**. Deterministic cases are usually cheap, and a reproduction
converts an accusation into evidence either way. The same audit that called F2
fabricated also reported that our record described the case as transonic
RAE2822 when every record in the repo titles it NACA0012 and openly documents
why RAE2822 was not used. It read a disclosure as a claim.

**Provenance is by artifact, not by proximity.** The gate table's own rule:
each act writes a transcript when it runs and that transcript is what the
camera records, while the campaign records are a different set of runs. Mostly
they agree, and not always. A row whose act has not run prints PENDING and is
never filled in from a neighbouring run that happens to be close. Citing the
campaign record for a row the viewer watched an act produce would make the
provenance decorative.

## 10. Before believing any of it, check the primary source

L-16 names the standing pattern behind L-14, L-15 and L-19: a derived,
annotated or summarised signal sits closer to hand than the primary evidence,
and it agrees with what was expected.

| the claim | the primary artifact |
| --- | --- |
| it converged | the solver's own convergence statement or reason |
| what the code does | the source line that does it, not a wrapper's comment on it |
| a measured quantity | the raw log or data file, not a collector summary |
| which case a log belongs to | the log's own path and timestamp |
| a column's meaning | the file's own `#` header line, read every time |

The last row cost the most on its own. A salvage report described lift swinging
between plus 0.40 and minus 0.43 as a convergence wobble. Those were columns 8
and 9 of `coefficient.dat`. Lift is column 5 and its value there was minus
40.30. Reading the wrong column turned a two-order-of-magnitude divergence into
a mild wobble.

**Treat agreement with expectation as a reason for more scrutiny, not less.**
All three of L-16's instances confirmed something already believed, which is
exactly why none of them got checked.

## 11. In-sample is not generalization

A benchmark score is a claim about cases the method had never seen. Fit the
method on one of those cases, by any route, and the score stops measuring that
and starts measuring memory, while looking exactly the same on the leaderboard.

> **Nothing this lab fits, inverts, calibrates or tunes on may be a scored case
> of a benchmark it reports a score against. A score obtained on data the
> method saw is reported as in-sample, never as generalization, and the
> intersection is stated in the record before the score is.**

**The route that arrived while nobody was watching.** `NASA_2DWMH` is one of
the closure challenge's eight scored test cases. It also has published
experimental skin friction, which makes it an obvious field-inversion target:
invert a correction field against the measured Cf, and the inversion is
textbook and legitimate. The benchmark score that follows is not. The case is
in-sample by construction, and the challenge's own README says training or
validating on a test case withdraws the submission and puts a note on the
leaderboard. The clean FIML workflow is the one the field already uses: invert
on a training case, learn the correction as a function of local features, apply
it forward.

**This is the same shape as the shortcut the lab already refused, and that is
the point.** The refusal held the first time because the shortcut arrived
labelled as a shortcut. This one arrives labelled as a capability, from a
direction nobody was watching, and every individual step in it is sound. A rule
that only recognises the first shape is a rule about that shape, not about
leakage.

**Reading ground truth is not the offence; fitting to it is.** Round 1's own
scripts read `U_LES` for the 21 training and 4 validation cases, which is how a
regression target gets built, and say so. The line is whether a scored case's
data reached anything that was fitted, selected, thresholded or stopped early.
Selection counts. So does a threshold chosen after looking.

**What a record has to say.** Any result carrying a benchmark score states the
case list it fitted on, the case list it scored on, and that the two are
disjoint, in the artifact itself rather than in a covering note. Round 1's
entry already does this (`train_val_test_disjoint`,
`train_validation_test_leakage`), which is why the check below can be written
at all: a claim that is machine-readable can be machine-checked.

**Caught by an aside, not by a rule.** This clause exists because
`demo-output/website/dafoam/ladder-b/S1_FIML_FIELD_INVERSION.md` section 7
recorded the leakage risk voluntarily, as a note to whoever ran the inversion
next. That worked once. L-22's point applies: a register whose entries depend
on somebody choosing to write them is not a register.

## 12. Enforcement

- `sdk/scripts/closure_in_sample_gate.py` derives the benchmark's scored-case
  list twice, from the clone's own README split table and from the repo's
  round-1 case lists, refuses to proceed if the two disagree, and then reads
  every training, fitting, inversion and calibration set declared in the repo's
  JSON records and Python case lists for a scored case. A case name as a whole
  value or as a key under such a declaration FAILs; a case name inside longer
  text, or in a prose line that says trained or inverted on, is reported for
  review with expected false positives, exactly as
  `scripts/audit_camera_discretion.sh` is. Section 6's asymmetry sets that
  tuning.
- `scripts/case_preflight.sh` runs before any launch and refuses cases whose
  fields do not match the named model, whose decomposition is stale, or whose
  `residualControl` names only fields the model does not transport.
- `scripts/launch_solve.sh` is the only sanctioned way to start a long solve.
  It runs preflight and refuses on failure, captures the real PID rather than a
  wrapper shell, arms the collector at launch so it outlives the caller's turn,
  and flags a job that exits without producing its expected artifact, which is
  the case that previously looked identical to success. D12 moved this out of
  discipline and into the harness after the rule was written down and the
  failure rate did not change.
- `scripts/gate_table.py` regenerates the gate table from act transcripts.
- `docs/standards/MONITOR_STANDARD.md` carries the log signatures, their
  severities and their prescribed actions.
- `HeadEngineer.stage_case` and `DockerDAFoamEngineer.stage_case` enforce
  section 13. Both scan the case as staged and refuse it if it carries
  executable directives and its template is not named in
  `chief_engineer.head_engineer.VETTED_SYSTEM_OPERATION_CASES`.

**~~A live defect, recorded here rather than quietly fixed.~~ ⚠ THIS NOTE IS STALE IN BOTH HALVES AND IS STRUCK 2026-09-05, v1.64 `§2as`.** ~~The consolidated FD
table in `demo-output/website/ACTIVE_RESEARCH.md` still shows A4's 10.04 percent
as PASS within the calibrated band.~~ **MEASURED: that row was CORRECTED 2026-08-14 (`ACTIVE_RESEARCH.md:167`), so the stale artifact this note reports is no longer stale.** ~~That band is the retired one. Under the
current standard in section 7 the same number grades CONDITIONAL, and two other
records already say so.~~ **AND A4's VERDICT OF RECORD HAS MOVED AGAIN, past the number this note argues about: `PASS` on a DIFFERENT CONFIGURATION — np=1 stock, **1.10 %** (`a4_np1_stock.log`, supervisor sweep `27d25762`) — after the step-sweep the source demanded WAS RUN (2026-08-02, W4, nine steps, `PROOF.md:2805` §25.4).** ~~L-1 applies: report both and say which artifact each
figure came from, then correct the stale one.~~ **L-1 still applies and is now discharged: both are reported here, each with its artifact.** **NOTHING IS RE-GRADED BY THIS STRIKE — A4's `PASS` is dafoam's, on their own record, and is not disturbed.**

## 13. A case from outside does not run with system operations enabled

**The rule.** A case file the lab did not author must not be run on a host
configured with `allowSystemOperations 1`. Either the switch is off for that
run, or the solve is sandboxed, or the case does not run. This is standing, not
a response to one incident.

**Why it is a verification rule and not only a security one.** An OpenFOAM case
is not inert data. With that switch on, four dictionary entries compile and
execute C++ inside the solver process, with the running user's rights:
`#codeStream`, `#calc`, any `coded*` boundary condition or function object, and
the `systemCall` function object (`dynamicCode::checkSecurity`, called from
`codeStream.C:268`, `calcEntry.C:75`, `codedBase.C:302`, `systemCall.C:131`).
So "we read the case dictionaries and the setup is inspectable", which is
section 9's evidence record, is a claim about a program, not about a table of numbers. A
case that can rewrite its own inputs at run time can also rewrite the evidence
record that is supposed to check it.

**Where the switch comes from here.** Nowhere in this repository. The
`openfoam2606` Debian package ships
`/usr/lib/openfoam/openfoam2606/etc/controlDict` line 75 as
`allowSystemOperations 1`; OpenFOAM's own compiled default is `0`
(`dynamicCode.C:44`), and `dpkg --verify openfoam2606-common` reports that file
unmodified. The DAFoam container ships the switch on too (OpenFOAM v2506,
`etc/controlDict` line 75).

**Which of the two paths is actually open, measured rather than assumed.** The
host path is open: it runs as `ubuntu`, uid 1000, and a `#calc` entry compiles
and evaluates. The container path is closed, but not by configuration: it runs
as root, and `checkSecurity` refuses `isAdministrator()` at `dynamicCode.C:73`
before it ever reads the switch. Measured in the container 2026-07-31: a
`#calc` entry fails with "This code should not be executed by someone with
administrator rights". So the container is safe today by accident of the
ownership decision in `docker_dafoam.run`, and the staging check is what keeps
it safe if that decision is ever revisited.

**How to turn it off, when a case does not need it.** Merge an override at the
user tier, which wins over the package file (`etcFiles.C` returns
user → group → project and `debug.C:161` merges in reverse):

```
~/.OpenFOAM/2606/controlDict
    InfoSwitches { allowSystemOperations 0; }
```

Every OpenFOAM run then prints `allowSystemOperations : Disallowing
user-supplied system call operations`, which is the receipt.

**What is exempt, and it is a list of one.** Act 7, the NASA wall-mounted hump.
Its case is the closure-challenge benchmark's own shipped `NASA_2DWMH`
OpenFOAM case; `caseDef` derives `Uinf`, `nu`, `kRef` and `omegaRef` with
`#calc`, and `system/convergenceProbes` plus the seven `system/singleGraph_*`
dictionaries place their probes with `#calc`. Nine files in all. Measured
2026-07-31: with the switch off, `foamDictionary caseDef -entry Uinf` exits 1
at `dynamicCode.C:83`, so the act cannot run. The exemption is recorded in
`VETTED_SYSTEM_OPERATION_CASES` with that reason, and note what it means, that the
one case that needs the capability is itself a case from outside. That is the
argument for the rule, not against it.

**An exemption is a debt, not a permission.** `#eval` is evaluated by the
expression parser and is not gated by the switch, so the hump's `#calc` entries
have a route out. Measured on `caseDef`, `#eval` reproduces six of the eight
derived constants bit-for-bit and the other two (`nu`, `kRef`) to within four
units in the last place, a floating-point association-order difference of about
3e-16 relative. Adopting it needs one act-7 rerun to confirm the published
separation and reattachment stations are unchanged, and that rerun is the price
of closing the exemption.

**No entry without a reason.** An entry in the vetted list names the act, the
files, and what those files use the capability for. "It broke without it" is
not a reason; it is the symptom that starts the review.

## 14. A finding is attributed to what somebody opened

L-22 already says a failure attributed to a case must be checked against that
case's own logs. Three findings in one week travelled anyway, and none of them
was a crash or a resource failure, which is why L-22's wording did not catch
them. All three are the same shape: a true statement about one artifact
restated as a statement about a different one, because the two were adjacent in
somebody's head.

> **An attribution is a claim, and it is a claim about a file. Name the file,
> and open it before the finding leaves the room.**

**The file nobody opened.** A dimensionality defect found in the shared
uncertainty module was attributed to the flat-plate verification card. The card
never had it: it has always fitted at the dimensionality its own mesh has, it
reproduces its published order, and it follows the reference convention. The
two were conflated because both compute an observed order and only one of them
was read. **The wrong attribution reached a proposal and a briefing before
anybody checked.** `demo-output/website/tmr/flatplate_sst.json`,
`sdk/chief_engineer/uq.py`, docket `w8-an-audit-attribution-is-a-claim`.

**The family that does not use the thing.** A generator finding measured max
aspect ratio worsening under refinement, 97.87 to 167.50, on a pyHyp extrusion.
That was carried to the NACA 4412 as the likely cause of its ladder trouble,
and it is wrong twice over: the 4412 is snappyHexMesh throughout, and its
aspect ratio **improves** under refinement, 53.5 to 26.8 to 13.4. The metric
moves the opposite way. The real degradation on that family is non-orthogonality
reaching 74.96 against a 70 gate and layer coverage falling to 58.3 percent, so
the borrowed cause also displaced the true one.
`demo-output/website/dafoam/GENERATOR_FINDING_pyhyp_aspect_ratio.md`,
`models/curriculum/results/naca4412_wing.json`.

**The body the number did not come from.** A polar was published under the name
of a surface it was not computed from. A NACA 0012 arrived, the act took only
its **span**, both lanes solved the act's own parametric anchor at camber 0.04
at 0.4 chord, and the curve went on screen labelled NACA 0012 with lift-to-drag
peaking at zero incidence. A symmetric section has no circulation at zero
incidence, so that curve could never have been its. Measured rather than
reasoned from the name: the received `naca0012_wing.stl` reads 0.00 percent
camber, 12.00 percent thickness and 0.00 degrees built-in incidence, while the
`wing.stl` the solver wrote reads 3.98 percent camber at 0.38 chord. **The
surface was right and the label was wrong.** Commit `3db36388`, and the fix
spells the name from the three section parameters the solver is handed, so a
label can no longer drift from the section that was solved.

**Four rules.**

1. **A finding names the file and the line it was read from**, and a second
   reader opens that file before the finding is filed. This is the literature
   charter's provenance tier pointed at the lab's own artifacts: a finding
   carried from another of our documents without re-opening the original is the
   same act as a citation copied without re-checking it.
2. **A defect attributed to a tool, a generator or a template names the case
   files showing that case uses it.** One line of evidence, and it is free.
3. **A result is named for what produced it, not for what was handed in.** An
   input that contributes a span contributes a span; the record says which
   properties came from the received artifact and which the run chose. This is
   section 6's evidence test applied to the subject line rather than the value.
4. **A cheap prior that contradicts the name is worth writing down.** The polar
   was caught by the observation that a symmetric section cannot lift at zero
   incidence, which costs nothing and is now an armed check on the alpha equal
   to zero anchor. P1 applies: run the cheapest control before publishing the
   attribution, not after.

## 15. A tool-forensics line is closed by repair, not by correlation

Sections 1 to 14 are about not believing a number. This one is about when to
stop, which is the opposite failure and the more expensive one: a forensics
line with no definition of done stops when the people on it get tired, and what
is on the record then is a suspect rather than a cause.

> **A root-cause claim about a tool is closed when the named line is changed,
> every reproducer collapses, the controls that should not move do not move,
> and something that should still be broken still is. Correlation, however
> strong, closes nothing.**

**Four conditions, and all four are load-bearing.**

1. **The named line is repaired and the errors collapse.** Not improve.
   Collapse, against pre-stated acceptance tests written before the patch ran.
   A repair that halves an error is consistent with the named line being one of
   several causes, which is not the claim being closed.
2. **Invariance controls stay bit-identical.** The paths the fix does not
   touch produce the same bytes they produced before. Without this a collapse
   is indistinguishable from a change that quietly moved everything.
3. **The primal is proven untouched, by checksum rather than by argument.**
   A derivative fix that also moves the solution is not a derivative fix.
4. **At least one thing that should NOT be fixed is checked and is still
   broken.** This is the condition that separates a cause from a fix that
   zeroes the comparison. A patch that repaired everything, including the
   failures the diagnosis says have a different mechanism, would refute the
   diagnosis while looking like the strongest possible confirmation of it.

**The worked example: the mesh-warp derivative arc, sections 15 to 24 of
`demo-output/website/dafoam/PROOF.md`.** Nine sessions narrowed a wrong adjoint
gradient to one discarded term in one degenerate branch of a generated reverse
routine. The derivation went on the record before any code was written, the
patch is four assignments in a scratch clone with no installed package touched,
and all four conditions were then met on the same day:

* **Collapse, against five acceptance tests stated in advance.** Upstream
  issue 57's `inflate_cube` went 210.16 percent and 212.62 percent to
  **8.6e-06 and 3.4e-05 percent**. A1's real seed went 634 percent with a sign
  flip, 1.74, 11.9 and 11.6 percent to **5.5e-04, 1.3e-06, 1.2e-05 and
  1.3e-05 percent**. The A5 pressure-loss seed's two sign flips, 207.0 and
  121.6 percent, came back at **3.0e-06 and 7.0e-06 with the signs agreeing**.
  The worst of A5's 27 stock modes went 80.79 percent to **0.0000, all 27**.
* **Controls bit-identical.** The shear regression set logs the same bytes
  patched and unpatched; the live branch was never entered.
* **Primal untouched, by checksum.** The full 310,284-coordinate warped grid is
  md5-identical patched against unpatched, `max|diff| = 0.0`.
* **Something still broken, on purpose.** The ONERA M6 second-regime error of
  1.26 percent **survives the patch unchanged**, which is what a
  degenerate-branch-only fix predicts and what a fix that merely zeroed the
  comparison could not have produced. In the same pass the half-failed
  rigid-translation control of section 23 collapsed from 1.7 and 2.8 percent to
  **4e-09 and 6e-09**, which turns its patch-junction attribution from an
  argument into a result.

`demo-output/website/dafoam/PATCH_getRotationMatrix3d.md` carries the
derivation, two independent hand sign checks and a standalone controlled
experiment with a known answer.

**What this clause does not license.** A repair proves a cause; it does not
license reporting the repaired numbers as the lab's own results. The patch
above lives in a scratch clone, nothing upstream has been filed, and every
figure in this section is labelled as a patched-versus-unpatched comparison
rather than as a validated gradient. Section 8 still governs what may be
claimed from any of it.

## 16. A negative verdict triggers a supervisor review

Section 8 makes a failed gate a result. This section is about the day after:
a negative verdict closes a question, and left alone it quietly closes the
diagnostics behind it too, because nothing in the lab's machinery ever asks a
FAIL what should be measured next.

> **Every negative verdict (a gate FAIL, a NO-GO, a no-verdict, a refuted
> prediction) triggers a supervisor review that proposes new diagnostics,
> and the review is recorded.** Owner's instruction, 2026-08-07.

**The inaugural instance is the pattern, and it is cited rather than
paraphrased:** `demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`,
written personally by the chief supervisor, covering every standing negative
verdict on the record in one pass, ten of them, from the periodic hills'
physics FAIL to the TMR aspect-ratio pathology. Its eleven filed diagnostics
set the bar for what a review proposes. Precisely: the review marks thirteen
diagnostics `[FILE]`, of which two ride existing approved runs (the standing
model-form batch gains the hills, the approved hump run gains a QCR arm) and
eleven are standalone filings to the docket. Every one is falsifiable,
costed, carries its hardness or source rationale, and names which way each
outcome moves the record. None requires a scoring call.

**What a review contains, per entry.** The verdict as it stands, what it
actually taught, and the new diagnostics proposed, each costed. A review
entry that proposes nothing says why nothing is proposable, which is itself a
finding.

**What a review is not.**

1. **It is not an appeal.** The verdict stands as graded; section 8 still
   forbids widening a gate after a result misses it, and a review that
   softens a verdict has become the thing this charter exists to prevent.
2. **It is not a bypass of intake.** Every diagnostic the review files is a
   proposal like any other and clears charter 1's disqualifiers on its own:
   prediction first, a stated cost, a hardness answer, an archive replay if
   it adds a rule.
3. **It is not delegable below supervisor level.** The judgments are the
   supervisor's; only the filing mechanics may be dispatched. The inaugural
   review says exactly this in its own header, and the supervision charter's
   section 4 keeps the review on the chief's retained list.

**Enforcement.** A negative verdict on the record with no review citing it is
a findable gap: the verdict vocabulary of section 2 is fixed, so the set of
FAILs, NO-GOs and refuted predictions is enumerable, and each is matched
against a review artifact or it is a violation. That matching is a review
discipline today, stated honestly; the artifact-per-instance convention
exists so a checker can be written against it.

## 17a. A rule can over-reach as easily as under-reach

**And only over-reach looks like rigour while it is happening.** A rule that
demands evidence which cannot exist does not make the record stronger; it makes
it wrong in a new direction, while wearing the costume of care. Section 17 was
adopted on a Monday evening and by that night its own first application had
found that **eleven of the ladders it annotated use deterministic generators,
where the quantity it demands is identically zero**, so the annotation was
false on every one of them.

Therefore, before any rule in this charter is applied to a record:

1. **Ask whether the demanded quantity can exist for that case at all.** If it
   cannot, the rule is satisfied by SAYING so, and demanding a number is the
   failure.
2. **Ask which quantity the record actually means.** The same word names
   different measurables. The case that triggered this had measured its
   *temporal* scatter carefully, per rung, and was annotated for lacking a
   *mesh-draw* scatter it could never have had.
3. **State the scope of the rule's applicability in the rule itself**, so the
   next reader does not have to re-derive it by spending.

Under-reach leaves a gap, which invites a fix. Over-reach writes a false
constraint, which forbids one (L-48), and a rule applied where it cannot hold
manufactures verdicts, which is the failure mode every other section here
exists to prevent.

## 17. A ladder increment is not published as a FEATURE without draw-scatter evidence

**Adopted 2026-08-10** on the archive replay in
`demo-output/website/campaign/W3_DRAW_SCATTER_RULE_REPLAY_RESULTS.md`
(pre-registration `6f196082`, results `dd3cac8d`), proposal
`w3-no-ladder-feature-without-draw-scatter`.

> **A ladder increment may not be published as a FEATURE without draw-scatter
> evidence at the rung it turns on, or with the absence of that evidence stated
> on its face.**

**A "feature" is a claim about the SHAPE of a sequence of grid-refinement
increments**: a turn, an oscillation, a divergence, a trend in increment
magnitudes, or monotonicity used as an argument. Reporting rung values, a band,
an order, or a `conclusive: false` verdict is **not** a feature and this rule
does not reach it. *"The fit returns p = 2.25 and we reject it"* does not fire;
*"its increments grow with refinement"* does.

**The remedy is RESTATEMENT, not withdrawal.** A feature whose scatter has never
been measured is not thereby false. It is unchecked, and the rule is satisfied
by saying so where the feature is stated. Withdrawal is only for features that
have been measured against draw scatter and did not survive.

**Why it was adopted: the evidence, not the argument.** Every replicate family
this lab has ever measured has returned a material finding. **Four for four:**

| family | what the replicates found |
| --- | --- |
| B-52 | the published turn was `max(rung 6) − min(rung 7)` of eight draws; **withdrawn** |
| NACA 0012 | the published mesh is the family **maximum** at +1.35σ |
| NACA 4412 | construction scatter 5.82 / 12.74 / 4.20% of the mean, worst at the graded rung |
| Ahmed 25° | the increment **inverts or halves** depending on which draw is excluded; **withdrawn** |

**The check has never once come back clean.** A check with that hit rate across
four independent families is not a precaution; it is a measurement everyone had
been skipping. `uq.eca_hoekstra_band` cannot infer draw scatter from a cell-count
and value series, so a ladder can be fitted, banded and quoted without anyone
ever asking whether its increments exceed the scatter of the meshes they are
differences of.

**The archive replay that carried it** (the entry condition: a rule firing on
every record or on none is not adopted). Of **151** campaign and website records,
**32** assert a ladder feature, neither all nor none:

| disposition | count |
| --- | --- |
| withdrawn (both applied 2026-08-10, none new) | 5 |
| already carry draw-scatter evidence at the deciding rung | 8 |
| already state the absence themselves | 2 |
| **RESTATE** | **17** |

**77% of the records the rule acts on need restatement, not withdrawal**, the
number that decided adoption. **The replay's first pass got this wrong** (16
records, 5 restatements, 50%) because its search vocabulary came from the two
families already under investigation; an independent second route of a different
kind found nine further bodies. That correction is L-49 and §7a of the Cases
family guidelines, and the counts above are the reconciled ones.

**Scope of the priced retrofit, stated honestly.** The approved retrofit, at
**12.8 to 21.7 core-min** for two further draws at the turn rung of each unchecked
ladder, covers **only the five ladders stored in
`models/curriculum/uq-studies/`**: `ahmed_25`, `ahmed_35`, `motorBike`, `cube`,
`naca0015_sail`. **It does not cover bodies whose ladders live only in campaign
records**: F3 wedge, F4 hypersonic, F7 dam-break, F6b ERCOFTAC, TMR bump,
lid-driven cavity, DPW8. Those need their own measured per-body solve costs and
are **flagged, not guessed**. For scale: the whole curriculum retrofit costs less
than checking the B-52 alone cost (40.9 core-min), and that one ended in a
withdrawal.


**CORRECTION, 2026-08-10, same day as adoption — the statistic named above cannot
decide at the sample size this rule affords, and the correction belongs here
rather than in a report.**

The retrofit buys **n = 3** at the deciding rung (one published draw plus two
new). Calibrated against the pure-scatter null by `scatter_bar.calibrate`:

| n | bar (10th percentile) | null median |
| --- | --- | --- |
| **3** | **0.0754** | 0.365 |
| 4 | 0.2722 | 0.594 |
| 5 | 0.4142 | 0.686 |

**At n = 3 the ratio `R = s(without the most extreme)/s(all)` has essentially no
power** — declaring "outlier-dominated" would require the two surviving draws to
be nearly identical. **A rule that specifies a statistic which cannot decide at
the sample size it affords is a trap for whoever runs it next.**

> **The deciding statistic is the INCREMENT-MOVEMENT test**, which is what
> actually decided both the B-52 and the Ahmed 25°: replace the rung's single
> published draw with the mean of its draws, recompute the increment, and grade
> **SURVIVES** (within 25% and same sign) / **DISSOLVES** (below 50%, or the sign
> flips) / **PARTIAL**. `R` is computed and reported; **at n = 3 it is not
> graded on**, and the bar's calibrated value is reported so a reader can see
> why.

Where the published draw sits in its own distribution is reported and **never
graded**: at n = 3 a draw is an extremum with prior probability 2/3 under no
selection at all.

**SCOPE. The rule applies only where a DRAW EXISTS. Added 2026-08-10 the same
day, on finding that it did not.**

**Mesh-draw scatter is a property of a NONDETERMINISTIC generator.**
snappyHexMesh's castellation is nonlinear in the background lattice, so two
meshes built to one recipe genuinely differ, and that is what makes a *draw* a
sample of anything. **A deterministic structured `blockMesh` generator produces a
byte-identical mesh from the same parameters. There is no second draw to take,
and the scatter this rule asks for is identically zero by construction.**

> **On a deterministic generator the rule is satisfied by STATING that, not by
> measuring.** Demanding a measurement there would be demanding a number that
> cannot exist.

**This was found by pre-flighting an approved run rather than by running it.**
All 11 campaign-record ladders restated as *"clean, no scatter measured"* (F3,
F4, F6b, F7, TMR bump, the NASA bump grids, the lid-driven cavity, DPW8) turned
out to use deterministic structured generators. **The ≈7.5 core-min approved for
F4 was declined because there was nothing for it to measure**, and the
restatements on all 11 were corrected. Only the snappyHexMesh bodies (B-52,
Ahmed, the NACA wings, motorBike, cube, the sail) have a draw distribution at
all.

**A related trap, from the same finding.** F4's record says *"scatter does not
fully explain it"*, and the scatter it means is **temporal snapshot scatter,
which it measured per rung**. A restatement that reads "scatter" as *mesh-draw*
scatter mis-describes the claim it is annotating. **Check which scatter a record
means before annotating it for lacking one.**

**FORM OF A RESTATEMENT. A restatement names the recipe class, because the class
determines what the absence means.** Added 2026-08-10 on the chief's ruling.
*"No scatter measured here"* means two different things:

| class | what the absence means |
| --- | --- |
| **CLEAN** (one knob moves per rung) | the feature is **one measurement away from real**, and its increments are genuine discretization increments |
| **CONFOUNDED** (more than one knob moves) | the feature is **unsupported twice over**, and its increments were never discretization increments, so the missing scatter is the lesser problem |
| **UNDETERMINABLE** (rung cases no longer exist) | **neither** the recipe nor the scatter can now be established at all |

A reader who cannot tell those apart would draw the wrong conclusion from an
honest sentence. **Every restatement states the class**, sourced from a recipe
audit (`campaign/LADDER_RECIPE_CONSISTENCY_SWEEP_2026-08-10.md` is the corpus-wide
one).

**THE CORPUS'S END STATE, 2026-08-10 — measured, not asserted.**

After three sweeps that each corrected the one before, the standing answer for
this lab is:

> **There are currently ZERO ladders in this lab where a draw-scatter
> measurement would be both possible and meaningful.**

| | |
| --- | --- |
| ladders where a draw **exists** (snappyHexMesh generation) | **6** |
| of those, **CONFOUNDED** — measuring them would be precise measurement of the wrong quantity | **4** |
| of those, **UNDETERMINABLE** — the rung cases no longer exist | **2** |
| ladders on **deterministic** generators, where the quantity is identically zero | **11** |

**This is the honest end state, not a shrug.** It says the rule has no unspent
work, and it says so because the work was looked for three times and the search
corrected itself each time: a text sweep corrected by a structural one, the
structural one corrected on its sampling frame, and the whole set corrected again
when a pre-flight found the quantity undefined for most of them.

**A reader arriving later should not re-derive this by spending.** If a new
ladder is built, the rule applies to it from §17's scope test (*does a draw
exist for this generator?*) and not from this table, which is a statement about
the corpus as it stood, not a permanent property of it.

**Calibration convention, binding on every retrofit verdict.** The bar separating
"the scatter is structured" from "the scatter is broad" is **calibrated by
simulation against the null before the draws exist**, never chosen after, so
every verdict arrives with its false-positive rate stated. The Ahmed 25° arm is
the worked precedent (`R4_AHMED_C3_LEG2_PREREGISTRATION.md`): the bar was the
10th percentile of the pure-scatter null, it was missed by 0.044, and the near
miss was **reported rather than resolved**. A bar that moves after the number is
not a bar.

## Related

- `docs/charters/RESULT_PRIORITY_CHARTER.md`. Which quantity wins when two
  methods verify different ones.
- `docs/charters/REPORTING_CHARTER.md`. Where gate tables and FD tables land,
  and section 10 there is the reporting side of sections 3.2, 3.3 and 14 here.
- `docs/standards/MESH_STANDARD.md`. The pre-solve mesh gate.
- `docs/charters/LITERATURE_CHARTER.md`. Section 7 carries the intake side of
  section 11: a reading is where a scored case gets proposed as a training case.
- `docs/UNCERTAINTY-DOCTRINE.md`. The three channels every result carries.
- `docs/charters/SUPERVISION_CHARTER.md`. Who conducts the section 16 review,
  and the four checks a supervisor performs personally.
- `LESSONS.md` L-3, L-7, L-14, L-15, L-16, L-19, L-21, L-22, L-24, L-25, L-26,
  L-27, L-28, P1, P3, D12.

## Amendment record

**Version 1.9, dated 2026-08-17. A style amendment, measured at frame `101079fd`.**
The sections above were brought to the owner's standard for a durable
record: em dashes and en dashes replaced by ordinary punctuation, and the
result of each replacement read back against the clause it sits in.

| what the amendment did | figure |
| --- | --- |
| em dashes replaced in the live sections | 62 |
| en dashes replaced in the live sections | 1 |
| em dashes left standing inside dated records | 9 |
| en dashes left standing inside dated records | 0 |
| clauses opened and declined, listed below | 4 |
| lines whose number changed above this section | 0 |

**No clause was added, removed, widened or narrowed, and no modal, scope or
tense inside a clause was altered.** Both the counts above and the gates were
taken in a detached worktree held at frame `101079fd`, so that a peer's
concurrent commit could not be read as part of this batch. The gates run either
side of the edit were `scripts/check_verdict_cells.py` with and without
`--selftest`, `scripts/check_absolutes.py`,
`scripts/check_normative_clauses.py`, `scripts/withdrawal_sweep.py`,
`scripts/self_audit.py` and `scripts/lab_check.py --no-tests`; the `sdk/tests`
suite was run either side in the live checkout. No gate moved its verdict. `check_absolutes.py` moved its verdict
COUNTS and not its verdict, and the movement was traced to the
sentences of this record rather than to the sections above.

**The line numbering above this section was held fixed on purpose.** Other
records cite this directory by line, and one of those citations sits inside an
executable check. An amendment that inserted its own changelog at the head of
the file would have moved the cited lines below it, so this record was appended
at the foot instead. The version-history entries above stand unedited, because their
figures describe the versions and the dates they name.

**What was opened and left alone.**
1. §1's verdict vocabulary reads GATE FAIL while the rung cells in the Ladder V ledger read bare FAIL; `scripts/check_verdict_cells.py --strict-fail` counted 4 such cells at frame `101079fd`. Both readings are defensible, neither side was touched, and the question is referred for a ruling.
2. §2a and §2b name the principal in their headings, which is what marks them as recorded instructions rather than lab-written proposals. The names were left in place; only the heading punctuation was changed.
3. §17's CORRECTION block of 2026-08-10 and its end-state table of the same date carry figures that describe the corpus at that date. They were left byte-identical, dashes included.
4. The three AMENDED blocks in §3.2 and §3.3 were left byte-identical.

---

## 6b. A reference that was never obtained is recorded in one vocabulary (added 2026-08-18)

**Placed at the foot, and numbered 6b for where it belongs.** Version 1.9's own
note above states the reason: other records cite this file by line and one of
those citations sits inside an executable check, so an amendment that inserted
itself next to section 6a would have moved every cited line below it. **Lines
whose number changed above this section: 0.** This clause is read with section
6a and is filed beside it in every index.

> **A gate row whose reference was never obtained says `NOT OBTAINED`, in those
> two words, and carries four fields: what is missing, which rung or row it
> blocks, why it was not obtained with the availability check named and dated,
> and the acquisition path with its price. `NOT OBTAINED` is a statement about
> a document, never about a verdict, and it changes no tier by itself.**

**This is section 6a's rule applied to the case where the referent is absent
rather than merely untransmitted.** 6a says a verdict carries what it was
checked against and, where there is no external referent, says so. It does not
say in which words, and the corpus answered that question five different times.

**Why a vocabulary is a charter matter and not a style note.** Docket **D382**
measured the state: `NOT OBTAINED` is campaign F14's local dialect, and the same
condition is recorded elsewhere in prose that no sweep can match. The
consequence is not untidiness. **The lab cannot count its own missing
references**, which is why `docs/VALIDATION_INVENTORY.md` section 6 had to
assemble that list by hand from two different kinds of record, and says so per
row. A rule that cannot be counted cannot be audited, and an honesty convention
that cannot be audited decays in one direction only.

**The token adopted is F14's, because it is the only one already carrying the
four fields.** `docs/campaigns/F14-cooling-ladder/K2c_RACK_ROW_VALIDATION_SEARCH.md`
is the worked example: candidate, what its record offers, availability checked
and dated against a named instrument, verdict. The four fields are what make the
token actionable rather than decorative, and a bare `NOT OBTAINED` with no
acquisition path is half a record.

**Nothing is renamed.** Every instance below is in a published record, several
of them frozen, and rewriting a record's own words to match a token adopted
afterwards is the edit this charter forbids everywhere else. **The mapping is
the instrument, not the rename.** A sweep reads the mapping; a reader reads the
record in the words its author chose. The obligation this clause creates runs
forward: **a row written from today says `NOT OBTAINED`.**

**The mapping, re-derived at HEAD on 2026-08-18 rather than copied from D382**
(the counts moved after D382 was filed, because `docs/VALIDATION_INVENTORY.md`
itself added fourteen occurrences of the token):

| Dialect as the record states it | Where, at HEAD | What it is |
| --- | --- | --- |
| `NOT OBTAINED` | `docs/campaigns/F14-cooling-ladder/K2c_RACK_ROW_VALIDATION_SEARCH.md` (15), `docs/VALIDATION_INVENTORY.md` (14), F14 `README.md` (5), `K0cT_runs/analyse_k0ct.py` (5), `K0c_runs/gate_k0c.json` (4), and eleven further files at one to three each | **The canonical form.** It is the only one of the six that a `git grep` can count |
| *"the reference is a literature-recalled `x/c ~ 0.60`, stated to two significant figures with no retained citation"* | `demo-output/website/campaign/F2_transonic_naca0012.md:186-189` | `NOT OBTAINED`. Field 3 is *no citable digitized dataset was retained*; **field 4 is empty, and the empty field is the finding** |
| *"No paper was found, despite a genuine search ... that reports a point value of Cd or St at exactly Re=2000"*, followed by a fallback to a secondary reproduced as a figure in a 2014 thesis | `demo-output/website/campaign/F5a_cylinder_reynolds_ladder.md:562-571` | `NOT OBTAINED` **as a primary**. What is held is SECONDARY, and the row is graded BANDED and LOWER CONFIDENCE, which is the right handling of the state under a different name |
| *"No tabulated numeric data for Martin & Moyce (1952) could be located"*, followed by a 600 dpi digitisation of a 2021 figure | `demo-output/website/campaign/F7_marine_free_surface.md:62-64` | `NOT OBTAINED` **as a primary**. The digitisation is the held artifact; its stated provenance and increment are field 4, and the record already supplies them |
| *"the exact form given in this task's gate"* | `cases/mega-batch/PHYSICS_FAMILIES.md:73-74` | `NOT OBTAINED`, **and the hardest of the five**, because this dialect does not read as a missing reference at all. It reads as a specification. A reader meets a correlation warranted by the prompt that asked for it |
| **nothing at all** | the nine-act gate table, `demo-output/website/campaign/NINE_ACT_GATE_TABLE.md`, until 2026-08-18 | The sixth state, and the one D382 named as uncountable by construction: a row with an unobtained reference that says nothing about it. **Repaired on that surface on 2026-08-18** by the referent and band columns, which state the class of every row's referent and, on act 1, that the form in the reference cell is in no cited source |

**What this clause does not do.** It does not convert a `NOT OBTAINED` into a
verdict, it does not license writing a gate row against a reference that is
absent, and it does not permit the reverse move of deleting a row because its
reference was never found. Section 2's rule still governs: a gate not reached is
stated as not reached. **`NOT OBTAINED` is how that sentence is spelled when the
reason is a document.**

---

## 2c. The discrimination test: a row that grades a hypothesis separates it from that hypothesis being absent (added 2026-08-18)

**Placed at the foot, and numbered 2c for where it belongs.** Section 6b's note
above states the reason and this clause inherits it: other records cite this
file by line and one of those citations sits inside an executable check, so an
amendment that inserted itself next to section 2a would have moved every cited
line below it. **Lines whose number changed above this section: 0.** This clause
is read with section 2a and is filed beside it in every index.

> **A gate row whose verdict is counted as evidence about a hypothesis is
> DISCRIMINATING or it is not evidence. A row that returns the same verdict for
> the hypothesis and for a registered trivial baseline of that hypothesis may be
> reported. It may not be counted toward the hypothesis's verdict.**
>
> **The rule reaches GRADE rows only. A GUARD row is exempt, and the exemption
> holds only while the row is counted toward no verdict.**

**This is section 2a's rule reached by the other road.** 2a catches a row whose
value is fixed by ALGEBRA: derivable by construction from its own inputs, so a
wrong treatment reproduces it exactly. 2c catches a row whose value is fixed by
nothing THE HYPOTHESIS CONTROLS: geometry, mesh, boundary conditions, anything
but the thing under test. Both are rows that cannot come out differently. Both
read exactly like a row that passed on merit.

**The instance that earned the rule, on 2026-08-18.** The K0cS square-cavity
rung graded three turbulence closures against Ampofo and Karayiannis (2003), and
ran a RECOGNITION control, C1, registered before the run with the turbulence
model switched off. **C1 passed four rows. kOmegaSST passed two. The set of rows
kOmegaSST passed that no turbulence model at all did not pass was EMPTY.** On
one of the two, local Nusselt at mid-height, the closure and its absence sat
0.0055 percent of the reference apart on the same mesh. Docket **D411**.

### The boundary, and it is the load-bearing half

**A row that GRADES a hypothesis is not the same object as a row that GUARDS a
run,** and the naive form of this rule -- every row must discriminate -- is
section 17a's over-reach, which looks like rigour while it is happening.

| | GRADE row | GUARD row |
| --- | --- | --- |
| Its verdict is evidence about | the **hypothesis** | the **run** |
| Its referent is | outside the run: an experiment, exact theory, a benchmark | an invariant every valid run of any hypothesis satisfies: conservation, convergence, a boundary condition applied, a marker written |
| A FAIL withdraws | the **hypothesis** | the **run**. The numbers are not evidence yet and it is re-run |
| It is counted in the rung's "N of M rows" tally | **yes** | **never** |
| It must discriminate | **yes** | **no, and it is supposed not to** |

**The question that separates them is asked at creation, beside section 2a's
two:** *if this row fails, what is withdrawn -- the hypothesis, or the run?*

A guard MAY discriminate and is simply never required to. K0cS's heat-balance
closure did, because its laminar arm was unsteady; K0cS's centre-cavity
temperature did not, correctly, because Boussinesq symmetry fixes it at 0.5 and
the row measures the non-Boussinesq defect rather than any closure.

**The exemption has teeth or it is a loophole.** A row declared GUARD and then
counted in a graded tally is the smuggling path, and it was found on real data
the day this clause was written: `gate_k0c.json` carried all four
energy-balance rows -- a demonstrated identity in
`docs/VALIDATION_INVENTORY.md` section 7.1, excluded from the rung's evidence in
its own prose -- inside `gate_rows`, its graded tally, with `passed: true`.

### Where this rule does not reach, stated so nobody re-derives it by spending

1. **A hypothesis with no runnable null.** "Does this solver solve the
   equations" has no no-solver arm. The rule is then UNMEASURABLE, **not
   satisfied**, and the row is recorded as unmeasured. A check reporting no
   violations over a population it could not evaluate has not passed; it has not
   run.
2. **A rung that IS an A/B by construction.** Where every row is already a
   difference between a treatment and its null on identical geometry -- F14's
   K2e sweeps Boussinesq against variable density this way -- the discrimination
   IS the measurement, and a discrimination test on top of it restates its own
   input.
3. **What counts as the trivial baseline is a judgement, not a datum.** For a
   turbulence closure it is the model switched off; for a correction, the
   uncorrected run; for a mesh claim, the coarser mesh. **The null arm is
   registered before its own run, with the record that registered it, and a null
   chosen after the numbers were read makes the instrument the thing it exists
   to detect.**
4. **A FAIL that both arms share is not automatically hollow.** Where the two
   arms are separated by a band or more the row grades and both arms are simply
   outside it. The hollow case is the one where they are not separated: the row
   then fails for a reason the hypothesis does not control, and the FAIL is not
   evidence against the hypothesis either.
5. **This is not the mutation control and does not replace it.** A mutation
   control perturbs the MEASURED NUMBER and asks whether the verdict can move; a
   discrimination test perturbs the HYPOTHESIS and asks whether it does. K0cS's
   mutation control stamped `every_row_reachable_both_ways: true` over twenty
   graded rows, correctly, and eight of the twenty carried evidence under this
   clause. **Both are required and neither implies the other.**

### Enforcement

`scripts/check_row_discrimination.py`, rules D1-HOLLOW-PASS, D2-INERT-ROW and
D3-GUARD-GRADED, with `--selftest` planting five shapes that must fire and nine
that must survive. The negative controls include a guard row displaying the
exact hollow-pass signature on real data, because a check that condemns the
whole inventory is scrolled past and has become the decoration it was built to
detect.

**What this clause does not do.** It withdraws no verdict already published, it
does not license deleting a row whose null arm was never run, and it does not
convert a discriminating row into a validated one. Section 2's rule still
governs: a gate not reached is stated as not reached.

---

## 2d. The comparator is frozen before its cases can answer it (added 2026-08-19)

**Placed at the foot, numbered 2d for where it belongs, and read with 2b.**
Other records cite this file by line and one of those citations sits inside an
executable check. **Lines whose number changed above this section: 0.**

> **The grading path of a comparator — every band, every reference, every row
> definition, every verdict rule, the discrimination test and the mutation
> control — is fixed at the pre-registration commit and does not change once
> the first graded solve has started. Instrumentation that is NOT on the
> grading path may be added later, and when it is, the record carries a dated
> disclosure naming what was added, when, what was readable at that moment, and
> which findings rest on it and which do not.**

**This is 2b's rule moved one step downstream.** 2b freezes the *prediction*
while there is no answer to tune it to. **A comparator is where the prediction
is cashed**, and freezing the prediction while leaving the instrument that
evaluates it editable protects only half the distance.

### Why this is a charter matter and not a practice note

**Because the lab has now done it both ways in one day and the difference is
recorded.**

`K0cX_RESULTS.md` §11 discloses a comparator extended at 18:58-18:59Z, after the
first graded solve at 18:43:23Z and after **six completion markers already
existed**. The edit was **purely additive** — 55 lines added, 2 removed and both
re-added extended, no band, reference, row definition, verdict rule,
discrimination test or mutation control touched, verified by inspecting every
removed line and by confirming the two newly parsed references are read by
nothing. **Every verdict in that rung rests on instrumentation that predates its
first solve.** The rung is sound and its own record says why.

**And it still cost something.** Two of its readings — the `fMu` first-cell trap
and the `Re_t` figure — rest on diagnostics chosen while some answers were
visible, which is the condition under which a diagnostic gets chosen *because it
will say something*. That rung had to spend a section of its own record
establishing what would otherwise have been assumed.

`K0cQ_RESULTS.md` §6 and `K0cR` did it the other way: comparator committed while
every case was mid-solve and **no case had written a marker**, then verified
byte-identical at analysis time. **K0cQ's finding is a null**, and a null is the
result most easily produced by an instrument that was not looking properly, so
the freeze is what makes it readable at all.

### The test, which is why this rule can be enforced rather than merely urged

**Compare the comparator's commit timestamp against the earliest completion
marker in its own run tree.** Both are on disk, neither is written by the person
being audited, and the comparison is one command. A comparator committed before
the first marker is frozen by construction; one committed after is not, and owes
the disclosure.

**Verify the frozen file is the file that ran.** Hash the comparator at analysis
time against the committed blob. A freeze that is claimed and not checked is a
claim about intent.

### What this rule does NOT reach (2c's boundary, applied to itself)

Per §17a, a rule over-reaches as easily as it under-reaches.

1. **A comparator that cannot run at all.** D419 found `analyse_k0c.py`
   unrunnable at HEAD because a documentation move left its specification path
   dangling. Repairing a path constant so the instrument executes is not tuning
   an instrument to an answer, and this clause does not forbid it. **The test is
   whether the repair can change a number**; a path either resolves or refuses.
2. **Additive instrumentation, disclosed.** The clause requires the disclosure,
   not abstention. A lab that may not add a diagnostic after seeing a partial
   result will under-instrument its most interesting runs.
3. **A rung whose defect is found after it reports.** D420 moved 18 rows out of
   a graded tally after the rung had published. That is a correction to a
   *published* record under W-4, made with every measurement shown byte-identical
   across the re-run, and it is governed by the amendment rules and not by this
   one.

**The boundary in one question, asked at the moment of the edit:** *could this
change move a number that a verdict depends on?* If yes, it belongs before the
first solve. If no, it belongs in the record with a date on it.

---

## 2d.1 Amendment to 2d: the repair exception, forced by the first case the rule was run against (added 2026-08-19)

**Lines whose number changed above this section: 0.**

**2d was written, an instrument was built to enforce it, and the instrument's
first pass over the lab found a case the rule got wrong.** That sequence is
recorded rather than tidied, because §17a says a rule over-reaches as easily as
it under-reaches and this is what the over-reach looked like.

`scripts/check_comparator_freeze.py` classed
`K0cS_runs/analyse_k0cs.py` as **UNFROZEN**: first committed 17:36:53Z against a
first completion marker at 17:28:48Z. The change it made after that marker was
**on the grading path** — `wall_nu` went from an **arithmetic** mean of the local
Nusselt over wall faces to an **area-weighted** one.

**2d as written forbids that change. The change was correct and necessary.**
The mesh is graded 117:1 and Ampofo's average Nusselt is an area average, so the
arithmetic mean weighted the corner cells — where local Nu runs from 136 to 17 —
about a hundredfold too heavily. **Every Nusselt number in the rung was wrong by
10-27 percent before the fix** (`K0cS_RESULTS.md` §10). Obeying 2d would have
meant publishing a knowingly wrong wall integral.

> **A change on the grading path made after the first graded solve is permitted
> when, and only when, all four hold: (1) it repairs a DEMONSTRABLE ERROR rather
> than a preference; (2) the error was established by an instrument INDEPENDENT
> OF THE HYPOTHESIS — one that grades nothing, such as a near-identity, a guard
> or a control; (3) the record discloses it, names that instrument, and
> QUANTIFIES WHAT MOVED; and (4) the pre-repair values are recorded beside the
> published ones. Failing any of the four, 2d stands.**

**Condition (2) is the load-bearing one and the other three are hygiene.** An
error found by something that grades nothing **cannot have been selected to move
a verdict in a wanted direction**, because the thing that found it does not know
which direction that is. K0cS's repair was found by the **heat balance** — a
near-identity on a sealed cavity, reported and never gated — whose closure sat
at 2.5-8.4 percent before the fix and **0.0000 percent** after on the fully
converged cases. That is the shape the exception is cut to fit.

**What the exception still does not permit**, and the contrast is the whole
point: *the numbers looked wrong, so the band was widened.* A band is not an
instrument; it is the hypothesis's own scoring rule. **Nothing a verdict depends
on may be repaired on the authority of the verdict it produces.**

### The instrument's other three findings, since a rule amended by one case should say what the rest looked like

- `K0cX_runs/analyse_k0cx.py`: **UNFROZEN**, first commit 50 seconds after its
  first marker. Its §11 already discloses the edit and establishes it as
  additive only, so it is 2d-compliant on the disclosure limb rather than on the
  freeze limb.
- `K0b_D403_rerun` and `K0b_D406_repair`: **AMENDED_AFTER** — first committed a
  day before their runs and touched again afterwards. 2d's boundary clause
  places W-4 corrections outside this rule, and the check reports that state
  separately rather than as a violation.
- `K0cQ_runs` and `K0cR_runs`: **FROZEN**, by +237 s and +422 s.

**Two of six frozen is the honest baseline this rule starts from**, and it is
recorded here so that later compliance is measured against a number rather than
an impression.

---

## 2e. Bands from a perturbation envelope (eigenspace, shelf D) — what such a band may and may not contain (added 2026-08-22, Sanaa's directive H-7)

**Placed at the foot, and numbered 2e for where it belongs.** Section 6b's note
above states the reason and this clause inherits it, as 2c, 2d and 2d.1 did:
other records cite this file by line and one of those citations sits inside an
executable check, so an amendment that inserted itself next to section 2d would
have moved every cited line below it. **Lines whose number changed above this
section: 0.** This clause is read with sections 2d and 6a and is filed beside
them in every index.

> **A band derived from an eigenspace/barycentric perturbation envelope may be
> armed on a graded row only if the pre-registration states, per row, whether
> the row's quantity is a Reynolds-stress SHAPE quantity or a FORCING/production-class
> quantity, and cites the measured containment fraction for that class; an
> envelope that perturbs eigenvalues only never perturbs `k` magnitude and may
> not be used to band a quantity that depends on `k` magnitude.**

**The caveat this clause institutionalises, quoted verbatim from
`docs/LESSONS.md` rather than restated.** Sanaa's directive H-7 of 2026-08-22
required the bands-vs-corrections caveat to enter the charters *verbatim*, and
that is why the two lessons are reproduced here in full rather than summarised:
a paraphrase of a containment fraction is a new number, and this charter forbids
new numbers in a clause that governs bands.

**L-219:**

> Emory, Larsson & Iaccarino deduce the perturbation magnitude `B` from DNS by
> minimising the barycentric distance to the perturbed state, and the values they
> work with are O(0.5). Measured here as the per-cell **minimum `delta_B` that
> contains the truth**, the eight training cases split into two families that do not
> overlap:
>
> | family | median `delta_B` required |
> |---|---|
> | 2-D separated flows — five hills and the curved step | **0.31 to 0.54** |
> | square and rectangular ducts | **0.95 to 0.98** |
>
> The hills sit exactly where the literature says. The ducts need essentially the
> whole way to a corner of the triangle. The reason is not that the duct is harder
> in degree: a linear eddy-viscosity model in a duct produces `b_23` and
> `b_22 − b_33` **identically zero**, so its barycentric point is not displaced from
> the truth, it is near the wrong vertex. The perturbation magnitude has nowhere to
> go but 1.
>
> **An uncertainty magnitude is a calibration, and it inherits the flow class it was
> calibrated on.** Quoting O(0.5) on a flow where the closure is structurally rather
> than quantitatively wrong understates the band by a factor of two, and the
> diagnostic that catches it — the required magnitude, per cell, in closed form — is
> one line of algebra and no solves.

**L-220:**

> The eigenspace method parameterises the **shape and orientation** of the Reynolds
> stress. Emory's eq. (4) keeps `k` outside the bracket, so magnitude is untouched
> by construction. Both papers say so. What the measurement adds is which cases pay
> for it, and the answer is an inversion:
>
> * **Shape** containment at `delta_B` = 1 is essentially complete everywhere
>   (0.9949–1.0000) — but on the ducts it costs the whole triangle (D2).
> * **Production** `P_k = -R_ij dU_i/dx_j` — the term through which the stress
>   actually forces momentum — is contained in only **0.9279 to 0.9433 of cells on
>   every hill and on the curved step**, while the two ducts clear 0.9998.
>
> So the cases whose *shape* is cheap to contain are the ones whose *forcing*
> escapes, and vice versa. A single "does the envelope contain the truth?" answered
> on `b` alone would have reported the hills as the easy family and been wrong about
> the thing that matters to the solution.
>
> **Report envelope coverage on the forcing term as well as on the parameterised
> quantity, and expect them to fail on different cases.** This also closes the loop
> L-157 opened: Xiao's space excludes the truth because it never perturbs
> orientation; the eigenspace envelope perturbs orientation and still misses the
> truth's forcing in 2–7 % of cells because it never perturbs magnitude. **Neither
> framework contains what it is meant to bound, and they fail on different axes.**
>

**What the two lessons jointly forbid, in the terms of the bright line above.**
L-220 establishes that the envelope's own construction leaves `k` magnitude
untouched — *"Emory's eq. (4) keeps `k` outside the bracket, so magnitude is
untouched by construction"* — so containment measured on shape is not evidence
of containment on forcing, and the measured fractions differ per class and per
case family. L-219 establishes that the magnitude `B` is a **calibration** that
inherits its flow class, so a band armed at a magnitude quoted from a different
flow class is not a band at that confidence. **A row that cites neither its
class nor its measured containment fraction has not armed a band; it has quoted
one.**

**What this clause does not do.** It does not forbid reporting an envelope's
coverage on any quantity — reporting is always available under section 3.3. It
does not convert a wide band into a pass, and it does not license widening a
band because a row missed: section 2d.1's closing sentence still governs —
**nothing a verdict depends on may be repaired on the authority of the verdict
it produces.** And it says nothing about *corrections*: a data-driven correction
and an uncertainty envelope are different objects, and the caveat is precisely
that a band is not a correction and a correction is not a band.

**First application: T4 impinging jet (H-5), where the registered question is
whether eigenspace bands contain the documented stagnation-Nu bias; the
pre-registration must classify `Nu_stag` as forcing-class.**

**Lines whose number changed above this section: 0.**

---

## Amendment record, continued: version 1.10 (2026-08-22)

**Appended here rather than inserted into the "Amendment record" section above,
for the reason that section itself gives.** Inserting a row at line 1618 would
have moved every line of sections 6b, 2c, 2d and 2d.1 below it, and each of
those clauses carries the sentence *"Lines whose number changed above this
section: 0"* — a sentence this amendment would have falsified for clause 2e in
the same stroke. The entry is therefore recorded at the foot, and the version
history above stands unedited.

| version | date | what the amendment did | existing clauses altered | lines whose number changed above clause 2e |
| --- | --- | --- | --- | --- |
| **1.10** | **2026-08-22** | **Clause 2e added at the foot** — bands from an eigenspace/barycentric perturbation envelope, with the L-219 and L-220 caveat quoted verbatim, on Sanaa's directive H-7 | **none** | **0** |

**Line 3 of this file is the only line above clause 2e whose CONTENT changed**,
carrying the version and date from *1.9, dated 2026-08-17* to *1.10, dated
2026-08-22*. Its line NUMBER is unchanged, no line was inserted or removed above
the clause, and the line number of every `##` heading in the file is unchanged;
both were verified by `diff` and by comparing `grep -n "^## "` either side of the
edit.

## Amendment record, continued: silent-background convention (2026-08-23)

**Dated addendum, 2026-08-23, appended at the foot; append-only. One standing
convention added on the owner's directive. No clause above is altered, widened
or narrowed; no line above this section changed number; the header's version
line is deliberately left untouched, because this addendum inserts nothing and
edits nothing above itself.**

Sanaa's directive, verbatim (2026-08-23): "There needs to be added to all
the .md convention files that all agents must always act in a silent way on
the background without showing bash or ssh on the screen, the screen must
always remain clean with only discussion and results."

In force for every agent this charter binds, and recorded lab-wide as
`CLAUDE.md` rule 16: all heavy work (bash, ssh, compute, file surgery) runs
inside background lanes or subagents, never as top-level tool calls in the
user-facing session when avoidable; user-facing reports carry discussion,
numbers and verdicts only, never pasted terminal output, raw logs or command
transcripts (quote the specific value with its artifact path, not the dump it
came from); supervisors enforce this on their lanes, condensing a transcript
before relay rather than forwarding it raw. Honest caveat: the Claude Code UI
renders whatever tool calls the top-level session makes, so the convention is
kept by pushing work into background agents; that delegation, not a display
setting, is what keeps the screen clean.

| what the amendment did | figure |
| --- | --- |
| standing conventions added | 1 |
| clauses altered, widened or narrowed | 0 |
| lines whose number changed above this section | 0 |

---

## Amendment — v1.11, 2026-08-27 — the NON-CONVERGENCE LADDER is lab law and lives in its own standard

**Nothing above is edited, struck, widened or narrowed. This amendment ADDS a cross-citation and
creates no clause of its own.**

Sanaa issued the **L0–L7 non-convergence ladder with an absolute anti-gaming clause** on
2026-08-27T16:54Z as §3 of her standing directives, captured verbatim at
`etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md` and boarded at `55b95ba9`. **It is
lab law and binds every team.**

**The standard text is `docs/standards/NONCONVERGENCE_STANDARD.md`** — her ladder verbatim in its
§1, this team's operationalisation `[lab-attributed]` in its §2, and F23 as the recorded L3
withdrawal precedent in its §2.2. **This charter does not restate the ladder**, because a clause
restated in two files diverges (`L-185`/`L-205`); it cites it.

**Four points of contact with clauses already in this charter, none of them changed:**

1. **§2b/§2d are untouched by the ladder.** Every level's arm is a run: frozen by sha before it
   starts, with its own cap. **No level of the ladder is a repair exception**, and §2d.1's
   four-condition exception remains the only route to a frozen comparator — reaching the
   comparator, never the gate, the threshold, the cap or the label. Sanaa's own clause says it:
   *"Frozen gates never edited post-compute."*
2. **§2c (discrimination) is what an arm changing two dials fails.** Her *"one change per run"* is
   a discrimination requirement, not a tidiness preference.
3. **The Roache ladder (standing rule 5) constrains L4.** A mesh repair applied to one level of a
   graded refinement family makes the three values incommensurable; the standard's §2.1 L4 clause
   requires the whole ladder to be re-registered rather than patched.
4. **§16 (negative verdicts) is where converged-but-wrong lands.** Her *"Converged-but-wrong = NOT
   HELD with diagnosis, never a parameter hunt"* is reported under this charter's existing
   negative-verdict discipline; the gate verdict is `GATE FAIL` and `NOT HELD` is its coverage
   tier. **No new verdict word is created** — standing rule 1's vocabulary is unchanged.

**Three desk rulings APPROVED by Sanaa in the same directive** (her §0, verbatim in the capture
file), recorded here because two of them are this charter's business:

- **R-RC — APPROVED.** *"rc value is physics, rc record is infrastructure; absent record -> NOT
  MEASURED only when the other four rule-4 conditions hold."* The ruling as issued is
  `docs/L342_GRADER_AUDIT.md` §2, including limb R-RC-4 (a grader inferring rc must also refuse on
  a `FOAM FATAL` / signal token).
- **D534 — APPROVED.** *"REPORTED is a row class, not a verdict; excluded from censuses."*
- **R-1D — APPROVED.** *"1-D cases count as CAVEATS in the 2D row."*

**One standing citation obligation, from her §0 and binding until the text lands:** ASME V&V 20's
own text is **not on the box**; the lab holds only `docs/papers/verification_validation/
dowding_2016_asme_vv.{pdf,txt}`. Her words: *"until it lands, every V&V-20 practice cites Dowding
2016 as secondary, stated as such."* **`docs/NUMERICS_KNOWLEDGE.md:118` is HERS to correct and no
agent touches it** — she stated she would correct it today.

| amendment record | v1.11 |
|---|---|
| clauses added | 0 |
| cross-citations added | 1 (`docs/standards/NONCONVERGENCE_STANDARD.md`) |
| desk rulings recorded as APPROVED | 3 (R-RC, D534, R-1D) |
| clauses altered, widened or narrowed | 0 |
| lines whose number changed above this section | 0 |

---

## Amendment — v1.12, 2026-08-27 — §2b: A FREEZE SHA IS NEVER DERIVED FROM A COMMIT SUBJECT

**Appended at the foot; nothing above edited, struck, widened or narrowed. `lines whose number
changed above this section: 0`.** Adopted by the chief `[lab-attributed]`; **on Sanaa's desk to
overrule.** Recorded in §2b's territory rather than in `USING_THIS_LAB` §8.5 because this is not a
commit-mechanics rule — **it protects the evidentiary content of the freeze itself**, which §2b
defines. It is stated **once**, here, and cross-referenced rather than restated elsewhere
(`L-185`/`L-205`).

### The clause

> **A pre-registration's freeze sha is resolved from the TREE, never from a commit subject line.
> The standard primitive is `git log --diff-filter=A -- <prereg path>` to find the commit that
> ADDED the document, followed by `git cat-file -e <sha>:<prereg path>` to prove the document
> exists AT that sha. A sha with no document at it is not a freeze.**

### Why a subject line cannot carry this weight — measured, not argued

Verified at source by this supervisor before recording. Two commits in dafoam's history carry
**byte-identical subjects**, both reading `dafoam curriculum_AV1R FROZEN -- the SUCCESSOR to AV-1
…`, **52 seconds apart**:

| commit | committed | paths touched | tree |
|---|---|---|---|
| `5e45a5a9` | 17:20:23Z | **0** | **byte-identical to its parent** — an EMPTY commit |
| `0c019d92` | 17:21:15Z | **19** | the real freeze |

**The primitive resolves it unambiguously and was executed here, not quoted:**
`git log --diff-filter=A -- cases/dafoam/ladder-a/A1/curriculum_AV1R/PREREGISTRATION.md` returns
**`0c019d92`**; `git cat-file -e 5e45a5a9:<that path>` **fails** — *"exists on disk, but not in
'5e45a5a9'"* — while `git cat-file -e 0c019d92:<that path>` **succeeds**.

**Anyone citing the freeze by grepping the subject had a 50 % chance of citing a commit that does
not contain the pre-registration at all** — which would make the freeze unverifiable while looking
perfectly well-cited. This is the same object-class error this team published against itself in
`docs/L342_GRADER_AUDIT.md` Addendum 3.

### The instrument already exists and is not new law

`scripts/queue_entry_check.py:250-256` already refuses exactly this, and its message is the clause
in operational form:

> `PREREG-AT-COMMIT: {path!r} does not exist at commit {sha}. A sha with no document at it is not a
> pre-registration freeze.`

**This amendment names the practice that check enforces so that records written by hand are held to
the standard the machine already applies.** It adds no gate and changes no threshold.

| amendment record | v1.12 |
|---|---|
| clauses added | 1 (a resolution primitive for §2b's existing "frozen by sha") |
| gates, thresholds, caps or labels changed | 0 |
| lines whose number changed above this section | 0 |

---

## Amendment — v1.13, 2026-08-27 — cfd's SWEEP PRECONDITION is **ADOPTED**, with one narrowing, two additions, and the boundary of what a lab agent may adopt stated on the face of it

**Ruling on `docs/standards/SWEEP_PRECONDITION_PROPOSAL.md` (`f35a276f`, cfd-supervisor,
drafted by cfd lane G3), referred by the chief to this team as standards owner. Appended at
the foot; nothing above edited. `lines whose number changed above this section: 0`, proved by
a byte-prefix check against the HEAD blob in the same invocation that wrote this section.**

### 1. WHAT IS ADOPTED, AND WHAT NO AGENT MAY DO WITH IT

**ADOPTED as a clause of this charter**, binding every team including this one:

> Any guard or comparator that carries a **measured false-positive rate** must have that rate
> **re-measured under the amended code before an amendment ships**, with the before/after rows
> recorded in the amendment, including the **per-clause split** and an **explicit statement of
> which outcomes moved and which did not**. Both rows are produced from **committed blobs**,
> over the **same** frozen sample, **in one process** — never from a worktree. **The
> instrument is filed in the repository, never in scratch.**

**Both riders are adopted as written:** the precondition is about the **delta**, not about
hitting a rate — no threshold is implied, and an amendment may legitimately raise a refusal
rate, it may only not ship without knowing what it did; and the sweep is **a floor, not a
ceiling** — a fixed sample cannot see forward exposure, which is where AMENDMENT 1 actually
acted.

**AND THE BOUNDARY, STATED SO IT CANNOT BE READ PAST.** This is a **documentation obligation
on amenders**. **No executable check may be made to refuse on it, by any agent, at any level.**
This team's own standing ruling (D539, on `check_threshold_resolution.py` and re-affirmed on
the commit-size guard) is that *a checker which refuses is a gate on lab process, and ADDING
a gate is reserved to Sanaa exactly as retiring one is.* A clause saying what an amendment
must **contain** is charter text and is this team's to adopt; a program that **refuses** an
amendment lacking it is a new gate and is hers. **Anyone who reads this adoption as authority
to write that check has laundered a permission (rule 9).**

### 2. THE ONE NARROWING — cfd's own caveat is DISSOLVED rather than carved around

cfd notes, correctly, that *an amendment which changes no guard behaviour cannot literally
satisfy the clause*, and proposes to solve it in the wording (*"any amendment that changes
guard behaviour"*). **That exemption is DECLINED, and the opposite rule is adopted:**

> **There is no "no behaviour change" exemption. The sweep is run anyway.**

**Ground: the exemption costs more than the work it saves.** cfd measured the work at **two
commands and under one core-minute** with the instrument filed. An exemption keyed on
"changed behaviour" requires the amender to **adjudicate** whether their own change moved
anything — which is a judgement, made by the interested party, about the exact question the
sweep answers **mechanically and for free**. **A claim of "this changed nothing" is cheaper to
PROVE than to argue**, and cfd's own AMENDMENT 1 is the proof: **its before/after rows were
identical and its real effect was large** (forward exposure 64 tracked paths → 14). **An
amender who had been permitted to assert "no behaviour change" on AMENDMENT 1 would have been
sincere, and wrong.**

Where the sweep genuinely cannot apply — a typo, a citation, a strike-in-place — the
amendment records **the rows it did produce and their identity**, which is a measurement, not
an assertion. **The identical row IS the compliance.**

### 3. ADDITION ONE, AND IT IS THE LOAD-BEARING ONE: THE HARNESS CARRIES A PLANTED CONTROL

**The proposal requires the rate to be re-measured. It does not require the instrument that
re-measures it to be shown able to return a DIFFERENT answer.** Without that, **a harness that
returns identical before/after rows because it is BROKEN is indistinguishable from one that
returns them because nothing moved** — and under §2 above, identical rows are now the
*expected* outcome of most amendments, which is precisely when a broken harness is least
likely to be noticed. **Adopting the clause without this would institutionalise the false zero
at lab scale.** Therefore:

> **The re-measurement harness ships with a planted control, executed in the same invocation
> as the sweep and recorded beside its rows: a deliberate mutation of the instrument under
> test must MOVE the reported rows. A harness that has not been shown able to report a change
> has not measured that nothing changed.**

This is `CLAUDE.md` standing rule 3 — *a zero from a reader not shown able to see a non-zero
is not evidence* — applied to a **rate delta** rather than to a comparator's output. **The
precedent is cfd's own:** `d12y_w3_fatal_scan_control.sh` extracts its pattern list **from the
launcher** rather than carrying a copy, on the stated ground that *"a control that carries its
own copy of the thing it is testing tests the copy."*

**Disclosed, because this team is the live instance and it is four commits old.** In
`58b68393` this supervisor reported two counts as *"RE-VERIFIED BY EXECUTION"*. The execution
was real; the check was worthless, because the grep patterns were **copied from the claim**
and the tokens had never existed in the file at any blob — **a zero from a reader that could
not have returned anything else** (`docs/L342_GRADER_AUDIT.md` Addendum 6, `b452e889`).
**This clause is written by the team that just failed it, against itself first.**

### 4. ADDITION TWO — THE SAMPLE IS PART OF THE ROW, and objection 2 is answered not dismissed

cfd's objection 2 is right that a frozen window decays, and its handling — the harness
**refuses** when its window stops resolving rather than silently sweeping a different sample —
is adopted as sufficient for the refusal case. It does not cover the **comparison** case:

> **Every recorded rate carries its sample's DEFINITION — the commit range and the count —
> beside the number. Two rates over different samples are not a before and an after, and a
> reader who cannot tell them apart will subtract them.**

### 5. OBJECTION 1 IS THE REAL WEAKNESS, AND IT IS FLAGGED, NOT SILENTLY FIXED

cfd asks whether exempting instruments that carry **no** published rate is *"clean, or an
invitation to publish no rate."* **This team's reading: as written, the clause's burden falls
ONLY on instruments whose owners chose to measure — so it taxes measuring and exempts
silence.** That is a real perverse incentive and it is not a small one.

**It is NOT fixed here, and the reason is a rule this team enforces on others.** The repair —
attaching the obligation to *any amendment that changes what an instrument refuses*, whether
or not a rate was ever published — is a **materially wider** obligation than the one cfd
proposed and the chief relayed. **Widening an obligation lab-wide under cover of adopting a
narrower one is exactly the permission-laundering shape (rule 9): approval of an item is
approval of ITS scope, not a new ceiling.** **So it goes on Sanaa's desk as a named, separate
question, with this team's recommendation that she take it** — and until she rules, an
instrument carrying no measured rate incurs **one sentence**: that it carries none and none
was re-measured. **A disclosure is not a measurement and costs nothing, and it removes the
incentive to stay silent without widening the obligation.**

### 6. OBJECTION 3, ANSWERED

cfd notes it proposed a rule that binds cfd most. **On adoption that is no longer true: it
binds every team, and it bit this one first** — §3's disclosure is a verification failure, not
a cfd one. **A rule proposed by the team it would most constrain, adopted by the team it
immediately convicts, is about as well-tested for self-interest as this lab can manage.**

### 7. STATUS OF THE PROPOSAL FILE

`docs/standards/SWEEP_PRECONDITION_PROPOSAL.md` **keeps its `STATUS: PROPOSAL. NOT ADOPTED.`
header and is NOT edited by this team** — it is cfd's file and its record of what was
proposed. **What is adopted is the text in §1 of this amendment, as amended by §§2–4; where
the two differ, this charter governs.** `COMMIT_SIZE_GUARD.md` v1.4 already binds cfd's own
guard and is unaffected. **Nothing is sent anywhere (rule 7).**

| amendment record | v1.13 |
|---|---|
| clauses added | 1 adopted (cfd's), with 1 narrowing and 2 additions by this team |
| gates, thresholds, caps or labels changed | 0 |
| executable checks made to refuse | **0 — and none may be, see §1** |
| questions placed on Sanaa's desk | 1 (the objection-1 widening) |
| lines whose number changed above this section | 0 |

---

## Amendment — v1.14, 2026-08-27 — **§2f: A REGISTRATION THAT DECLARES NO ROACHE TRIPLE.** Rule 5 is **UNREACHABLE, NOT WAIVED**; the cap attaches to what a LIMB CLAIMS, not to the registration; and the election is frozen pre-compute

**Ruled on ansys-verification's VMFLGPU007 wording call, routed by the chief. Appended at the
foot; nothing above edited. `lines whose number changed above this section: 0`, proved by a
byte-prefix check against the HEAD blob in the same invocation. This clause is `§2f` and
ansys should cite it by that number. It does not block their freeze and it ratifies their
registered design in every particular — with one distinction added and one loophole closed.**

### §2f.1 The answer to the question asked: YES, it needs a clause

A registration with no triple is the only shape in this lab that can **avoid rule 5 without
failing it**. Left unwritten, the reasoning *"we registered no triple, so the triple gate does
not apply"* is available to any rung whose triple would have come back `DIVERGENT` — and it
converts a `NOT A RESULT` into a `GATE REACHED` **by a wording choice**. It is written down
here so it is a narrow, evidenced election rather than a phrase a future team reaches for.

### §2f.2 RULE 5'S WORDING — the operative sentence

> **Standing rule 5 does not FIRE on a registration that declares no grid triple, and is not
> thereby SATISFIED. A row that cannot reach rule 5's gate has not passed it.** The absence of
> a triple is a **LIMITATION on what the row may claim**, never an exemption from the standard
> the row is measured against, and it is recorded on the face of the registration in those
> terms.

**And the half of rule 5 that still fires, which matters more than the half that does not:**

> **Rule 5's limb (1) — a level not iteratively converged, or not plateaued, is `NOT A RESULT`
> — is UNAFFECTED and applies in full.** Only limb (2), the triple-state gate, is unreachable.
> **"No triple" never means "no rule 5."**

### §2f.3 THE CAP ATTACHES TO WHAT A LIMB CLAIMS — not to the registration

The proposed wording *"cap every physics limb at `GATE REACHED`"* is **adopted for continuum
claims and DECLINED as a blanket**, because a blanket cap is wrong about a whole class of
legitimate limb and would make this clause punitive rather than accurate.

| limb class | what it claims | ceiling without a triple |
|---|---|---|
| **CONTINUUM** — value vs experiment, correlation, exact or manufactured solution | a property of **the continuum solution**, from which discretisation error is not separable without a triple | **`GATE REACHED` maximum. `PASS` is unavailable.** |
| **SAME-DISCRETE-PROBLEM IDENTITY** — GPU vs CPU, solver vs solver, restart vs cold, np-invariance, determinism | that **two computations of the SAME discrete problem agree** | **`PASS` available.** A triple is **irrelevant** to it: both sides carry the *same* discretisation error on the *same* mesh, it cancels exactly, and the claim is **identity, not accuracy**. |

**So VMFLGPU007's registered design is correct as ansys wrote it, and the ground is now
stated:** limb B (GPU vs CPU at identical mesh) is `PASS`-capable **not by concession but
because it makes no continuum claim**; limb C (physics vs Vogel & Eaton) is capped at
`GATE REACHED` **because it does**. A limb is classified in the registration, before compute,
and **a limb that cannot be classified is CONTINUUM by default.**

### §2f.4 THE INADMISSIBILITY MUST BE A MODEL-FORM FACT, NOT A CAPABILITY STATEMENT

*"Name why systematic refinement is inadmissible"* is adopted **with a test attached**, because
naming a reason is not evidence and any team can write a sentence.

> The reason must be a **property of the REGISTERED MODEL OR CASE that another reader can
> check**, and it must be **entailed by a choice already frozen** in the registration.

- **QUALIFIES** (VMFLGPU007's own): standard k-ε with standard wall functions requires `y+` in
  the log layer, so refining the first cell **violates the turbulence model's own validity**.
  The inadmissibility follows from the registered model. A reader can verify it without
  running anything. **The honest corollary is stated too: a systematic triple IS available on
  this geometry — at `y+ ≈ 1` with a low-Re model — and it is A DIFFERENT CASE, not this one
  refined.** Saying which case *would* carry a triple is part of the election.
- **DOES NOT QUALIFY:** "the mesher could not build it", "we lacked the core-minutes", "the
  finer level diverged", "no reference exists at finer resolution". Those are **capability,
  budget or outcome** statements. **The last is the loophole itself.**

### §2f.5 THE ELECTION IS FROZEN PRE-COMPUTE, AND A PRIOR TRIPLE IS DISCLOSED

This is the clause the loophole actually needs.

> **The no-triple election is registered BEFORE first compute**, like every other gate
> (§2d). **If a Roache triple was ever run on the same case, its result is DISCLOSED in the
> no-triple registration** — the levels, the state and the observed order — whatever it said.

**Electing "no triple" after a triple returned `DIVERGENT` is selection by outcome**, and it is
prohibited by the same clause of Sanaa's §3 anti-gaming rule that prohibits picking a model by
agreement with the reference. **The tell is identical: the discarded arm is missing from the
record.** A registration that is silent about whether a triple was attempted is **not
compliant** — silence is the signature, so silence is what the clause forbids.

### §2f.6 THE MESH-SENSITIVITY SPREAD IS A BOUND, AND IT IS NOT A GCI

Adopted, with the naming discipline made explicit:

> The spread across the sensitivity family is reported **beside** the value as an uncertainty
> channel, **as a BOUND on observed variation over the meshes actually built — never as an
> error estimate, never extrapolated, and NEVER called a GCI or an observed order.**

**Ground:** Richardson extrapolation and the GCI both presuppose systematic refinement. A
family built to hold the first-cell height fixed is **deliberately not systematic**, so the
quantity has no asymptotic interpretation at all. The lab's existing discipline already
forbids quoting a GCI off a non-monotone triple; **this forbids quoting one off no triple**,
which is the stronger case.

### §2f.7 RATIFIED, AND NOT NEW LAW — ansys's §10.x

ansys's rule that ***"ran to `endTime`" is not convergence where no `residualControl` exists —
plateau must be established by a registered channel*** is **correct and is ratified.** It is
**not** a new standard: it is **rule 5's limb (1) in operational form**, and standing rule 4's
completion conditions are about *whether the run finished*, never about *whether the solution
stopped moving*. **A solver that ran every registered iteration and was still moving at the
last one has completed and has not converged, and the two are different findings.** Where the
solver offers no residual signal the registration **names the channel** — a monitored quantity,
its window, and its plateau criterion — **before compute**, or limb (1) is unevaluated and the
row is `NOT A RESULT`. **This clause is where §2f bites hardest: a no-triple family has already
given up limb (2), so limb (1) is the only convergence gate it has left, and it is not
optional.**

| amendment record | v1.14 |
|---|---|
| clauses added | 1 (§2f, seven sub-clauses) |
| gates, thresholds, caps or labels changed | 0 — the ceiling is stated, not moved |
| exemptions from rule 5 created | **0 — §2f.2 makes it unreachable, not waived, and limb (1) still fires** |
| executable checks made to refuse | **0** (D539: a checker that refuses is Sanaa's) |
| lines whose number changed above this section | 0 |

---

## Amendment — v1.15, 2026-08-27 — §2b: **A CITATION NAMES ITS OBJECT CLASS.** v1.12 governs how a sha is RESOLVED and never said how one is WRITTEN — and the classes are **THREE**, not two

**Ruling on closure's D546 (`617eb2ca`), routed by the chief with the question *"consider a
one-line clarification under v1.12 if the text does not already say so."* **It does not say so —
checked before answering.** Appended at the foot; nothing above edited. `lines whose number
changed above this section: 0`, proved by a byte-prefix check against the HEAD blob in the same
invocation. **No gate is created; a citation form refuses nothing.**

### 1. v1.12 DOES NOT ALREADY SAY IT

v1.12's clause is *"a pre-registration's freeze sha is resolved from the TREE, never from a commit
subject line."* **That governs how a sha is RESOLVED. It says nothing about how a sha is
WRITTEN**, and its "why" section only mentions the object-class error in passing. **The gap D546
identifies is real and the clause below is new.**

### 2. D546 IS RIGHT AND UNDERSTATES IT — THERE ARE THREE OBJECTS, NOT TWO

Measured on the very file D546 uses, `docs/standards/NONCONVERGENCE_STANDARD.md`:

| class | value | what resolves it |
|---|---|---|
| **commit** | `7ffd6c73` | `git cat-file -t` → `commit` |
| **blob** | `d553b963b4a727b8…` | `git rev-parse <commit>:<path>` |
| **sha256** | `14d72954cbe853ae…` | `git show <commit>:<path> \| sha256sum` |

**Three different valid digests of the same bytes, and the phrase "the sha" names none of them.**
**A clause worded as "commit or blob" would leave the blob/sha256 pair still ambiguous** — and
this team put `sha256:` into live use *today*, in `docs/L342_GRADER_AUDIT.md` Addendum 6, for
untracked artefacts that have no blob. **All three forms are now in circulation, so all three
must be nameable.**

### 3. THE CLAUSE

> **Every sha-bearing citation names its object class on the face of the citation**, as
> `commit:<sha>`, `blob:<sha>` or `sha256:<digest>`. **A bare hex string is not a citation**, and
> **the construction `<path> at <sha>` is specifically prohibited**: it places a path adjacent to
> a number and lets the reader supply the relationship, which is how the error in D546 travelled.
> The existing forms stay valid and are read as `commit` unless marked: `sha:path:line`
> (Addendum 4) and `path:line @ sha256:<digest>` (Addendum 6).

**The damage is pedagogical, not evidentiary, and the clause is written for that.** A commit id
used where file content is meant **fails loudly** — `git cat-file -p 7ffd6c73` returns a commit
object, not the file — so **nothing can be silently verified against the wrong object.** *(That
"nothing was verified against the wrong object" is the chief's finding and closure's; this team
confirms only the mechanism that makes it so.)* **What propagates is the FORM, into frozen commit
messages that cannot be edited** — which is precisely why a citation convention, not a checker, is
the right instrument.

### 4. THE ORIGIN IS THIS TEAM, MEASURED RATHER THAN INFERRED

`docs/LAB_STATE.md:11986`, written by **this team** at 17:03:32Z, reads:

> *"`docs/standards/NONCONVERGENCE_STANDARD.md` **at** `7ffd6c73`"*

closure's frozen `e6961d48` then reads:

> *"docs/standards/NONCONVERGENCE_STANDARD.md **sha** `7ffd6c73`"*

**The board wrote a path adjacent to a commit id and let "at" carry the relationship; the next
reader supplied the wrong one and froze it.** dafoam's `dae3dc9d` carries the same id in the
milder form *"NONCONVERGENCE_STANDARD (`7ffd6c73`) CARRIED BY NAME"*. **The prohibition on
`<path> at <sha>` in §3 is written against this team's own sentence.**

**Also on the record: the correct disambiguation already existed elsewhere on the board** —
`docs/LAB_STATE.md:1375` reads *"landed at COMMIT `7ffd6c73`; the FILE's sha256 is …"*. **One
board carried both the right form and the wrong one, and the wrong one is the one that
travelled.** A convention that exists in one place and not in the neighbouring paragraph is not a
convention yet, which is why this is charter text.

### 5. WHAT THIS DOES NOT DO

- **It creates no gate and no checker.** Adding a gate on lab process is Sanaa's (this team's
  D539); a citation form binds writers, refuses nothing, and blocks no commit.
- **It does not retro-fit existing citations.** Frozen commit messages **cannot** be edited, and
  the two named ones stay as they are — **the record of how the form travelled is worth more than
  a tidy corpus.** Existing bare shas in tracked documents are read as `commit` per §3 and are
  re-derived by content before they are relied on, exactly as Addendum 4 already requires.
- **It settles nothing about `7ffd6c73`'s content.** `NONCONVERGENCE_STANDARD.md` and its §1/§2
  two-voice structure are unaffected; only how the file is cited changes.

| amendment record | v1.15 |
|---|---|
| clauses added | 1 (citation object-class, three classes) |
| gates, thresholds, caps or labels changed | 0 |
| executable checks made to refuse | **0** |
| existing citations retro-fitted | **0** |
| lines whose number changed above this section | 0 |

---

## Amendment — v1.16, 2026-08-27 — **§2g: A PRE-REGISTRATION CANNOT EXCEPT A STANDING RULE.** W1b R1's floor exception is REFUSED — and the remedy is a different instrument, not a refusal

**Ruling on heat-transfer's referred-and-unruled W1b R1 item. Appended at the foot; nothing above
edited. `lines whose number changed above this section: 0`, proved by a byte-prefix check against
the HEAD blob in the same invocation. The clause is `§2g`.**

### §2g.1 THE QUESTION

W1b R1's triple measures **`EXACT`** (`e21` −2.842e-13, `e32` 3.240e-12); its deviation is
**2.899e-12 K against a registered 1e-06 K floor**. Standing rule 5 branch (2) makes an `EXACT`
triple **`NOT A RESULT`**. The row is recorded **`PASS`**, standing on a **floor exception frozen
in the pre-registration before compute** (`commit:3c39d08d`, 2026-08-26T21:18Z, against first
compute 2026-08-27T08:54:19Z — **rule 2 is clean and is not in question**).

### §2g.2 THE RULING: REFUSED, ON RULE 5's OWN SENTENCE

> **A pre-registration fixes the gate, threshold, cap and label FOR ITS CASE. It has no power to
> disapply a standing rule, and an exception to one is void however early it was frozen.**

**Three grounds, and the first is decisive on its own:**

1. **Rule 5 says the gate is ONE-WAY, in its own text:** *"The gate can only turn a `PASS` or
   `GATE FAIL` **into** `NOT A RESULT`, never the reverse."* **An exception that yields `PASS`
   where rule 5 yields `NOT A RESULT` runs the gate backwards.** It is not a gap in the rule; it
   is the thing the rule's last sentence exists to forbid.
2. **Scope.** A pre-registration binds a **case**; a standing rule binds the **lab**. **A
   case-level document cannot amend a lab-level rule** — that is Sanaa's, exactly as adding or
   retiring a gate threshold is (this team's D539).
3. **The consequence if it were allowed:** any rung could pre-register its way out of any standing
   rule, disclosed and in advance, and **rule 5 would become optional at the author's election.**
   Pre-registration's power is that it fixes what the author may claim *before* they know the
   answer; it was never a power to choose which rules apply.

**Rule 2 being clean does not save it.** Freezing early proves the exception was not chosen to fit
the answer. **It does not confer the authority to write the exception.**

### §2g.3 BUT THE PHYSICS IS RIGHT, AND THE REMEDY IS A DIFFERENT INSTRUMENT — NOT A REFUSAL

**Heat-transfer's substantive point stands and this ruling does not dismiss it.** A triple whose
three levels agree to 1e-13, whose deviation sits **six orders inside its floor**, and which is
**900× tighter than the band it replaces**, is **not the pathology rule 5 exists to catch.**

**Why rule 5 refuses an `EXACT` triple, stated precisely, because it decides the remedy:**
`p = ln|e32/e21| / ln r` on two differences that are both round-off is **noise divided by noise**.
**Rule 5 refuses to compute an ORDER from nothing. It does not say the VALUE is worthless.**

> **THE DIAGNOSIS: the wrong instrument was registered.** Where the discretisation error is below
> the registered floor **at every level**, a Roache triple **has nothing to measure** — there is
> no order to observe and no GCI to quote. Registering a triple and then excepting the triple gate
> is **registering the wrong instrument and patching it.**

**THE REMEDY, which loses nothing:**

- The row reads **`NOT A RESULT` on its Roache limb** — rule 5 unexcepted.
- **The measurement is REPORTED beside it, not discarded**: 2.899e-12 K against a 1e-06 K floor,
  the three levels' agreement, and the 900× improvement on the band it replaces. **D534 already
  established `REPORTED` as a row class** for exactly this — a quantity the record carries and no
  gate scores.
- **The successor registers a FLOOR DEMONSTRATION with its own gate** — *the discretisation error
  is below X at the coarsest level, so the answer does not depend on the mesh at the resolution
  that matters* — **and that gate CAN `PASS`**, on its own pre-registered band, without touching
  rule 5. **A floor demonstration is a weaker claim than grid convergence and it is the claim the
  evidence actually supports.**

**Nothing is re-graded by this team.** The row is heat-transfer's; this rules the standard.

### §2g.4 AND THE T13 `exact_class` FLAG IS WIDER THAN THE ARGUMENT FOR IT — verified at source

`verification/runs/T-family/T13_runs/analyse_t13.py:405` reads:

    if not exact_class and tr["state"] != "CONVERGING":

**Read by this supervisor at source: the flag short-circuits the WHOLE of branch (2)** — not the
`EXACT` state its docstring argues for, but `DIVERGENT`, `STAGNANT` and `OSCILLATORY` with it. The
flag is a **hard-coded per-row constant** in the spec tuples at `:488`. **G2 and G3 read
`OSCILLATORY` and `DIVERGENT` (p −0.8931) and are recorded `PASS`.**

**This is the T1b shape** (`analyse_t1b.py:193`, ruled at `docs/L342_GRADER_AUDIT.md` Addendum 5):
**a gate condition that is computed, recorded, and never reaches the verdict.** Here it is worse in
one respect and better in another — **worse**, because a constant *actively* disables the test
rather than the test merely being absent; **better**, because heat-transfer found it, boarded it
(D545), disclosed the width itself, and marked the comparator **NOT-FOR-REUSE**.

**This team accepts that no retrofit is owed**, on heat-transfer's own evidence and not on its
assurance: the band verdict is computed first, the gate is one-way, the graded fine values sit
**4.20 and 6.00 orders below their floors**, and **all five planted-zero controls PASS at a
demonstrated detection floor of 1e-07 — an order below G2's band — so a band violation would have
been visible.** **The verdicts are substantively right and the instrument is not. Both are true
and the record should say both.**

### §2g.5 THE DEFECT CLASS, ADOPTED — and its contrast pattern is in the same family

Heat-transfer's generalisation is adopted as this charter's:

> **A PROPERTY DECLARED BY CONSTRUCTION AND NEVER TESTED AGAINST THE MEASUREMENT.** The
> declaration then reads as licence to skip the check that would have falsified it. **In T13 the
> measurement happened to vindicate the premise; nothing in the code required that.**

**The contrast is `verification/runs/T-family/T9aR1b_runs/analyse_t9aR1b.py:217-225`, which
DERIVES the state from the numbers** — `if max(abs(e21), abs(e32)) < roundoff_K: state="EXACT"` —
**and carries both `e`'s in the record either way.** **A property MEASURED can be wrong and be
caught; a property DECLARED cannot.** That file is the lab's pattern of record for this, and the
sweep contrast to look for is a **constant** where `analyse_t9aR1b` has a **comparison**.

| amendment record | v1.16 |
|---|---|
| clauses added | 1 (§2g) |
| exceptions to standing rules permitted | **0** |
| gates, thresholds, caps or labels changed | 0 |
| rows re-graded by this team | **0** |
| executable checks made to refuse | 0 |
| lines whose number changed above this section | 0 |

## Amendment — v1.17, 2026-08-27 — **§2h: A FLOOR DEMONSTRATION IS NOT A CONTINUUM CLAIM.** §2f.3 does not cap it, the two clauses do not conflict — and the ambiguity that made them look like they do is MINE

**Appended, append-only; no line above changed number. Raised by heat-transfer as a
blocking referral with its launch HELD; ruled here. Nothing of heat-transfer's is
edited and no row is re-graded.**

### §2h.1 THE REFERRAL, STATED FAIRLY

§2g.3 says the floor-demonstration successor's gate **CAN `PASS`**. §2f.3's
**CONTINUUM** row names *"value vs experiment, correlation, exact or manufactured
solution"* and caps such a limb at **`GATE REACHED`**. T9a-R1c's limb compares a
computed interface temperature against an **exact series-resistance solution**, so
read literally it is a §2f.3 CONTINUUM row. **Both cannot govern the same row.**

**Heat-transfer registered `PASS` on §2g.3's express authority, argued that §2f.3's
STATED GROUND does not obtain, and then referred rather than proceeded.** That is
the correct handling and it is noted.

### §2h.2 THE RULING: §2f.3 DOES NOT REACH THIS LIMB

**§2f.3's own heading decides it: *"THE CAP ATTACHES TO WHAT A LIMB CLAIMS."*** Apply
that principle to what this limb actually claims.

**A floor demonstration does not claim a property of the continuum solution. It
claims a property of THE DISCRETISATION** — *the discretisation error is below X*.

**§2f.3's ground is not merely absent here; it is INVERTED.** That clause caps a
limb because *"discretisation error is not separable"* from the claim. **A floor
demonstration's claim IS the discretisation error.** There is nothing to separate
it from — **the quantity §2f.3 protects against is the quantity being reported.**

**And the DEFAULT does not catch it either.** §2f.3 ends *"a limb that cannot be
classified is CONTINUUM by default."* **That default is RESIDUAL — it governs
UNCLASSIFIED limbs.** §2g.3 classifies this limb **expressly**, and an express
classification beats a residual default. **So the clauses are not in conflict: one
is specific and one is residual, and they never both applied.**

### §2h.3 BUT THE AMBIGUITY IS REAL AND IT IS MINE

**§2f.3's CONTINUUM row groups FOUR referents under ONE ground, and the ground holds
for only two of them:**

| referent | does the residual contain MODEL-FORM error? | is the residual discretisation error? |
| --- | --- | --- |
| experiment | **YES** | no — inseparable without a triple |
| correlation | **YES** | no — inseparable without a triple |
| **exact solution OF THE SAME CONTINUUM MODEL** | **NO, by construction** | **YES** |
| **manufactured solution OF THE SAME MODEL** | **NO, by construction** | **YES** |

**My own table row put all four in one class under a ground that distinguishes
them.** A reader applying §2f.3 literally reaches the wrong answer on the bottom two
rows, which is exactly what happened. **The defect is in the drafting, not in
heat-transfer's reading — their reading of the words was correct.**

**§2f.3's row is NOT amended here.** Narrowing a cap makes a gate weaker, and
**weakening a charter clause is Sanaa's, exactly as retiring one is (D539).**
**REFERRED, WITH RECOMMENDED WORDING: split the CONTINUUM row so that *exact or
manufactured solution of the same continuum model* is named separately and is
`PASS`-capable when §2h.4's conditions are met.** Until she rules, **§2h governs by
express classification and §2f.3's cap stands untouched for everything else.**

### §2h.4 THE CONDITIONS, WHICH ARE THE WHOLE RULING — a floor demonstration may `PASS` ONLY where ALL FIVE hold, declared in the registration BEFORE compute

1. **THE REFERENCE IS THE EXACT OR MANUFACTURED SOLUTION OF THE SAME CONTINUUM MODEL
   THE SOLVER DISCRETISES.** Not an experiment, not a correlation, not a different
   model. **This is the load-bearing condition:** it is what makes model-form error
   **zero by construction** and the residual **discretisation error**. If the
   reference is anything else, **§2f.3's CONTINUUM cap applies in full** and this
   clause does not fire.
2. **ITERATIVE ERROR IS SEPARATELY GATED BY RULE 5 LIMB (1), ONE-WAY.** A level not
   iteratively converged or not plateaued is `NOT A RESULT` **regardless of the floor
   result**, and no verdict-writing path may turn that into a `PASS`. **"No triple"
   never means "no rule 5" (§2f.2).**
3. **ROUND-OFF IS STATED WITH ITS MAGNITUDE AND SHOWN NEGLIGIBLE AGAINST THE BAND** —
   a number in the registration, not an assurance.
4. **THE LIMB'S WORDING MAKES NO CONTINUUM CLAIM.** It reads *"the discretisation
   error is below X at N cells"*, **never** *"the solution is correct to X"*. **A
   floor demonstration WORDED as a continuum claim IS a continuum claim and §2f.3
   catches it.** The registration's own sentence is the test.
5. **THE CLAIM IS BOUNDED BY THE LEVELS ACTUALLY RUN.** *"Below X at every level
   run"* is measured; *"so the answer does not depend on the mesh"* is a claim about
   meshes **not** run and is not supported by this instrument. **§2g.3's phrase *"so
   the answer does not depend on the mesh at the resolution that matters"* OVERREACHES
   and is NARROWED here, against this team's own drafting** — a floor demonstration
   establishes the error at the meshes measured and nothing about finer ones, because
   establishing behaviour across meshes is what a triple is for **and this instrument
   deliberately has none.**

### §2h.5 T9a-R1c ON THESE CONDITIONS — the ruling heat-transfer is holding for

**On the design as reported, conditions 1, 2 and 5 are met** — an exact
series-resistance referent; limb (1) applied in full and one-way with a single
verdict-writing function that cannot turn `NOT A RESULT` into `PASS`; and three
levels run. **Condition 3 is OWED: state the round-off magnitude against the
1.0e-04 K band as a number.** **Condition 4 is OWED as a WORDING CHECK: the
registered sentence must read as a discretisation-error claim.**

**RULING: `PASS` IS AVAILABLE TO T9a-R1c's FLOOR LIMB**, on §2g.3's express
authority as narrowed by §2h.4, **once conditions 3 and 4 are discharged in the
pre-compute registration.** Both are one-field, pre-compute, and reversible before
launch. **The AST guard over a forbidden-name list, with a planted `gci_unequal()`
control proving the guard can see one, is the right instrument for condition 4's
machine half** and is noted approvingly — **but it proves the ABSENCE OF A TRIPLE,
not the wording of the claim, and condition 4 is about the wording.**

**NOT RULED, and named so it is not read in:** nothing here touches W1b's refused
exception, which stands refused; **nothing licenses a `PASS` on any limb whose
reference is experimental or correlative**; and **whether §2f.3's row should be
split is Sanaa's, not settled by this.**

## Amendment — v1.18, 2026-08-27 — **§2i: THE FREEZE BITES WHEN COMPUTE BEGINS.** The first-compute stamp is the EARLIEST `started_utc` under the registration, and a stamp cited late opens a window in which an illegal amendment looks legal

**Appended, append-only; no line above changed number. Raised by heat-transfer from
its own T16 records; verified here at source. Zero compute.**

### §2i.1 THE CLAUSE

> **A registration's first-compute moment is the EARLIEST `started_utc` of any case
> under that registration.** Not an `ended_utc`. Not the latest `started_utc`. Not a
> commit time, a file mtime, or the moment a launcher was invoked. **Where the
> earliest `started_utc` cannot be established, the first-compute moment is
> `NOT MEASURED` and every amendment after the earliest evidence of compute is
> treated as post-compute** — the conservative direction, because the alternative
> lets an unestablished stamp license an amendment.

**The stamp is RECORDED IN THE REGISTRATION with the path of the STATUS file it was
read from**, so a third party can check it in one command. A stamp without its
source is an assertion (`R-CAP.8` §8.7, applied to a different quantity).

### §2i.2 WHY THIS IS A RULE-2 QUESTION AND NOT BOOKKEEPING

Standing rule 2: *"Before first compute, amendments are legal … After first compute
gates are closed."* **The whole legality of an amendment turns on one timestamp.**

> **A first-compute stamp cited LATE opens a WINDOW — an interval in which an
> amendment that is in fact ILLEGAL reads as legal against the record.** The stamp
> is not a description of the run; **it is the boundary of the lab's central
> evidentiary rule.**

**And the error has a DIRECTION.** `ended_utc` is always ≥ `started_utc`, so citing
it is **always late and never early**. **The defect is therefore systematically
biased toward permitting amendments, never toward refusing them** — it can only ever
enlarge the legal window, never shrink it. **A mistake that errs in only one
direction is not a mistake, it is a leak.**

### §2i.3 THE SPECIMEN, VERIFIED AT SOURCE

`verification/runs/T-family/T16_runs/STATUS.T16_MC_c` carries
**`started_utc=2026-08-27T17:30:06Z`** and **`ended_utc=2026-08-27T17:42:30Z`**. The
sibling `STATUS.T16_MC_m` carries `started_utc=2026-08-27T17:42:55Z`.

**Citing `ended_utc` as first compute puts the boundary 12 minutes 24 seconds late,
and the earliest `started_utc` under the registration is 17:30:06Z.** **Found and
reported by heat-transfer against its own records.**

**Note the second trap the sibling exposes:** the *latest* `started_utc` is
**17:42:55Z**, which is **within 25 seconds of the wrong answer** — so a reader who
correctly rejects `ended_utc` and then takes the wrong `started_utc` lands almost
exactly where they started. **EARLIEST, across ALL cases, is the operative word.**

### §2i.4 SCOPE, AND WHAT IS **NOT** RULED

**This clause is PROSPECTIVE on its face and REMEDIAL only where a sweep shows an
amendment actually fell inside a window.** A late-cited stamp with **no amendment in
its window** is a **citation defect and nothing turns on it** — it is corrected by a
dated addendum and **no gate moves, no row is re-graded.** Those two outcomes are
counted **separately** and must never be reported as one number.

**A sweep of the corpus is in flight and its findings are NOT anticipated here.**
**No amendment anywhere is declared illegal by this clause**; the clause states the
test, and any application of it to a specific record is a separate ruling on
evidence, made case by case with the owning team. **`L-380`: a framing is not a
finding, and this section refuses to convict on a rule it has just written.**

## Amendment — v1.19, 2026-08-27 — **§2h.6: §2h IS NOT RETROACTIVE, AND A LANE WAS RIGHT TO REFUSE AN ORDER TO CITE IT.** Plus a narrowing of §2g.4 that runs against this team's own wording

**Appended, append-only; no line above changed number. Zero compute. No verdict
moves anywhere in this amendment.**

### §2h.6 NON-RETROACTIVITY — write it down so nobody reaches for a path that does not exist

**§2h.4's chapeau already decides this and it is being made explicit because a
near-miss proved the implication is not obvious:** the five conditions must be
**"declared in the registration BEFORE compute."**

> **A rung frozen before §2h landed cannot have declared them, so §2h CANNOT BE
> CITED FOR ANY ALREADY-FROZEN RUNG, IN ANY FAMILY, EVER.** Every §2h benefit
> requires a **NEW registration**, frozen after §2h, carrying the five conditions on
> its face. There is no citation path, no addendum route and no supervisory
> instruction that creates one.

**THE SYMMETRIC GROUND, and stating it makes both halves harder to forget.** §2g
holds that **a pre-registration cannot EXCEPT a standing rule.** §2h.6 holds that a
pre-registration **cannot retroactively CLAIM THE BENEFIT of a later one.** **A
registration is fixed at its freeze and reaches neither around a rule that bound it
nor forward to a rule that did not.** Both follow from rule 2's single evidentiary
claim — *the freeze proves the gate could not have been chosen to fit the answer* —
and **a rung citing a clause that did not exist when it froze is choosing its gate
after seeing its answer, with extra steps.**

**THE NEAR-MISS, recorded because the refusal is the finding.** T13's two
floor-demonstration `PASS` rows were frozen at **`commit:0d2dc150`,
2026-08-26T20:55:45Z**; **§2h landed at `commit:9fdb1d9f`, 2026-08-27T22:01:24Z** —
**25 hours and 6 minutes later.** A "§2h citation" to legitimise those rows was
**ordered by the chief and endorsed by heat-transfer**, and **the lane REFUSED on
§2h.4's chapeau.**

**The lane was right and both supervisors were wrong, this team included — §2h is
mine and I did not spell out its own non-retroactivity.** **A lane refusing a
supervisory instruction on charter grounds is not insubordination; it is the control
working, and it is the only one of these barriers that operated on the day.**
Rule 9's permission-laundering clause has a mirror image here: **no instruction from
any supervisor, or from the chief, converts a rung's frozen registration into one
that declared what it did not declare.**

**W1c is the only rung that can invoke §2h**, having been frozen after it with the
five conditions declared. **Nothing about T13 is re-graded by this section:** its
rows stand as they were registered, on the grounds registered, and **§2h neither
helps nor harms them.**

### §2h.7 A NARROWING OF §2g.4, AGAINST THIS TEAM'S OWN WORDING

§2g.4 reported T13's `exact_class` flag as short-circuiting branch (2), and this
team's relay of it later described the flag more loosely as bypassing **rule 5**.
**That looser phrasing is TOO WIDE and is withdrawn.**

**Verified at source in `analyse_t13.py`:** `if not gate1_ok: return "NOT A RESULT",
…` is evaluated **BEFORE** `if not exact_class and tr["state"] != "CONVERGING"`.
**So limb (1) — not iteratively converged or not plateaued → `NOT A RESULT` — is
CLEAN, ONE-WAY AND UNAFFECTED BY THE FLAG.** The flag reaches **gate (2) only.**

**The correction narrows the defect and narrows it in heat-transfer's favour, which
is why it is worth making carefully:** the instrument is less broken than this team
said. **§2g.4's substantive finding is undisturbed** — a per-row hard-coded constant
still disables the triple-state test, and the defect class *"a property declared by
construction and never tested against the measurement"* (§2g.5) still stands.
**T13 G2/G3 remain `PASS` on the registered floor with the defect disclosed; no
verdict moves.**

## Amendment — v1.20, 2026-08-27 — **§2i.5–§2i.8: THE SWEEP IS IN. Three LATE citations and NOTHING TURNS ON THEM; T4 AMENDMENT 2 IS LEGAL AND §2i DOES NOT REACH IT; and the clause is NARROWED three ways prospectively**

**Appended, append-only; no line above changed number. Zero compute. No row re-graded, no amendment declared illegal.**

### §2i.5 THE SWEEP RESULT — the two outcomes counted separately, as §2i.4 required

**15 records assert a timestamp AS first compute**, out of 1,271 phrase-bearing files
(16,624 tracked at HEAD). **3 LATE · 6 CORRECT · 6 UNDECIDABLE.**

**All three LATE citations are T16 and all three cite the same stamp** —
`T16_PREREGISTRATION.md:489` and two `LAB_STATE` sites — and **the window is EMPTY.**
The T16 window is `[17:30:06Z, 17:42:30Z]`, **744 s**; every commit touching that
registration or run tree sits **1,073 s before it** (the freeze `ae20d137`) **or
after it**, and Amendment A1 **self-declares POST-COMPUTE on its face**, so it never
rested on the late stamp.

> **CITATION WRONG, NOTHING TURNS ON IT: 3. AMENDMENT INSIDE A WINDOW: 0.** A dated
> addendum on each of the three is owed. **No gate moves, no row is re-graded, and
> the two figures are never to be reported as one number.**

### §2i.6 T4 AMENDMENT 2 — RULED **LEGAL**, AND §2i DOES NOT REACH IT

`verification/runs/T-family/T4_runs/STATUS.T4_IJ_c.CRASH_pre_amendment2` carries
`started_utc=2026-08-26T03:47:47Z`, **`rc=1`**, `ended_utc` **equal to**
`started_utc`. **T4 Amendment 2 (`commit:399dc213`) is at 03:56:37Z — 530 s later**,
and it registers **physics** (`kLowReWallFunction`, `nutLowReWallFunction`,
`alphat = calculated`) on a Nusselt-class rung while claiming rule 2's **pre-compute**
clause.

**Under §2i as literally worded it is post-compute. IT IS NEVERTHELESS LEGAL, ON A
GROUND THAT HAS NOTHING TO DO WITH CRASHES.**

> **§2h.6 holds that a registration cannot claim the BENEFIT of a clause that did
> not exist when it froze. THE SYMMETRIC PROPOSITION IS THAT A LATER CLAUSE CANNOT
> RETROACTIVELY CONVICT ONE EITHER.** §2i landed **2026-08-27T22:19Z**; T4's
> amendment was made **2026-08-26T03:56:37Z — over a day earlier.** **A rule written
> after the act does not reach the act.** T4 Amendment 2 is judged on the rules in
> force when it was made, and **§2i is not among them.**

**Recorded because the symmetry is the whole point: this team wrote the
non-retroactivity clause four hours ago in the direction that RESTRAINED a team, and
it applies here in the direction that PROTECTS one. A principle that only ever runs
one way is not a principle.**

**AND ON THE MERITS, prospectively and without deciding this case:** the amendment's
own stated ground — **rc=1, zero iterations, no `Time = 1`, no time directory, no
field written, 0.034 core-min** — **is the correct criterion, and §2i.7 adopts it.**

### §2i.7 NARROWING 1 — FIRST COMPUTE REQUIRES A RESULT-BEARING ARTEFACT

> **The first-compute moment is the earliest `started_utc` of any case UNDER THE
> REGISTRATION THAT PRODUCED A RESULT-BEARING ARTEFACT: a time directory, a written
> field, or at least one `Time = ` iteration line in a solver log.** A launch that
> produced **none** of these did not close the gates.

**THE GROUND IS RULE 2'S OWN EVIDENTIARY CLAIM, NOT LENIENCY.** The freeze proves the
gate **could not have been chosen to fit the answer**. **A run that produced no
iteration and no field produced NO ANSWER TO FIT TO.** Nothing was visible, so
nothing could be fitted. **`started_utc` is a PROXY for "compute that could have
produced information", and where the proxy and the thing diverge, the thing governs.**

**AND THE LOOPHOLE IS CLOSED BY PUTTING THE BURDEN ON THE REGISTRATION, NOT ON
HINDSIGHT:** the amendment must **state the absence at its own timestamp, naming the
checks** — no time directory, no field, no `Time =` line, and the `rc`. **"Nothing
useful happened" judged after the fact by the party who benefits is not admissible;
a named, checkable absence recorded at the time is.** **Spend does NOT close gates
— 0.034 core-min is a rule-12 question and rule 2 is about evidence.**

### §2i.8 NARROWING 2 — WHICH CONVENTION GOVERNS WHEN THE MESH IS COMPUTE

Two conventions are live and **they disagree by ~23 minutes on T16**: `started_utc`
is set **after** the case build and `checkMesh` (`run_one_t16.sh:178` vs `:169`) —
measured, `log.blockMesh` mtime **17:07:20Z** against `started_utc` **17:30:06Z**,
**1,366 s of meshing outside the stamp** — while
`docs/CROSS_TEAM_GATE_AUDIT.md:617` uses *"the `blockMesh` banner"* outright.

> **THE TEST IS WHETHER THE MESH IS INSIDE THE FREEZE.** Where the built mesh is
> **committed in the freeze commit**, it is part of the registration and **compute
> means the SOLVER**. Where the mesh is **generated after the freeze**, **MESHING IS
> COMPUTE**, because a mesh made after the freeze is a result-bearing artefact the
> registration did not fix — and a gate could be fitted to it.

**T16 is internally consistent under this test and needs no correction:** its freeze
`ae20d137` **deliberately commits `log.blockMesh` and `log.checkMesh.build`.**

### §2i.9 NARROWING 3 — SCOPE, STATED HONESTLY

**The rule is MOSTLY PROSPECTIVE and the corpus is largely immune by construction.**
The dominant convention is the **opposite** one — an amendment carrying its own
timestamp plus a **run-root-ABSENCE** check — which cannot exhibit this defect.

**`started_utc` exists in only 8 tracked run directories, ALL heat-transfer
T-family.** **No closure, dafoam, cfd or ansys registration carries the field**, and
K0f's base STATUS files lack it. **So 6 of the 15 sites are UNDECIDABLE because there
is no `started_utc` to read**, and they derive first compute from mtimes or banners.
**Where no `started_utc` exists the clause does not bind; the record states its
criterion and its evidence, and `NOT MEASURED` remains available.**

### §2i.10 NOT CLAIMED, AND ONE READER FAILED

**The single most consequential candidate lived ONLY IN THE DISK FRAME** — T4's crash
STATUS files are **untracked**. **A HEAD-scoped search returned the identical null for
"no such record" and "not committed yet", and here that difference hid the finding
completely** (`L-386`, now with its worked example).

**A phrase-based reader MISSED the planted control** — a first-compute assertion in a
phrasing outside the enumerated vocabulary — **and is reported as failed rather than
quietly dropped**; the conclusions rest on a **value-based** reader that flagged the
plant and did not flag its correct-citing twin. **Both limbs fired on the reader
that is relied upon.**

**`T1_runs` may be one registration or two** (`NOT MEASURED`); if two, one CORRECT
classification needs re-reading. **K0f's true first compute is UNDECIDABLE.** **The
three crash STATUS files are evidenced by mtime, a weaker class than a committed
field.** **No amendment anywhere is declared illegal by this amendment.**

## Amendment — v1.21, 2026-08-28 — **§2j: THE BIRTH REQUIREMENT.** Standing rule 3's question is now a PRECONDITION OF GRADING, not a property a comparator may acquire later — **canonized by Sanaa, 2026-08-28**

Appended at the foot; nothing above edited. `lines whose number changed above this section: 0`,
proved by a byte-prefix check against the pre-amendment file: the first **184349** bytes
of this file are byte-identical to the version before this section, whose sha256 begins
`57ba9adb73053ccf` and which carried **3056** lines. The assertion is machine-checked in the
commit that lands this amendment, not asserted in prose.

### §2j — THE BIRTH REQUIREMENT OF EVERY READER AND COMPARATOR

**Canonized on Sanaa's instruction, 2026-08-28, verbatim:**

> Companion rule canonized: rule 3's question — "was this reader ever shown able to see a
> non-zero through the real code path?" — is now the birth requirement for every
> reader/comparator: no instrument grades anything until that answer is yes, demonstrated.

**§2j.1 — WHAT CHANGES.** Standing rule 3 already required a planted control. It was read, in
practice, as a property a comparator could be shown to have **when someone got round to
checking** — often after it had already produced numbers. **§2j makes it a PRECONDITION.** An
instrument that has not answered the question **does not grade**; anything it has already emitted
is **`NOT A RESULT`** until the answer is demonstrated. **The burden sits on the instrument's
author at birth, not on a later auditor.**

**§2j.2 — "THROUGH THE REAL CODE PATH" IS THE OPERATIVE PHRASE, AND IT IS WHERE EVERY FAILURE
THIS LAB HAS FOUND ACTUALLY LIVES.** The demonstration must use **bytes written by the real
producer's code**, read by **the real reader**, in **the form reality delivers**. Per `L-402`:
**ask who WROTE the bytes the control reads.** If the answer is *the control itself* or *the test
harness* rather than the real producer, **the birth requirement is NOT met**, however green the
selftest.

**Three specimens, all found in this lab within one week, all of which pass a naive reading of
rule 3 and fail §2j:**

| instrument | its control | why it fails §2j |
|---|---|---|
| `grade_vmflgpu007.py` A4 | fixture shapes the reader matches | **no smoke has ever produced a real PETSc `-log_view` table**; exercised only on its absent-table path (`DEAD_LEVER_AUDIT` §5) |
| `queue_runner.py` GPU clause | `--selftest` **injects** entries setting `gpu: exclusive` | **zero real entries set that field**, including both queued GPU cases (§8) |
| `check_record_reconciliation.py` | plants period-form headings | **89 live headings use the em dash**; the D549 regression left the selftest at `rc 0` (`L-401`) |

**§2j.3 — THE DEMONSTRATION IS AN ARTEFACT, NOT A CLAIM.** *"I tested it, it's fine"* from the
author is evidence, never the demonstration (`SUPERVISION_CHARTER` §3). What satisfies §2j is a
**driven control whose output is on disk or in the record**, naming the producer that wrote the
bytes, and carrying **both limbs**: the reader **sees** the planted non-zero, **and** stays
**silent** on the negative. **A control with only a positive limb is a detector that fires on
everything.**

**§2j.4 — WHAT §2j DOES NOT DO.** It is **NOT RETROACTIVE** (§2h.6's principle, applied here
against this team's own interest): a comparator frozen and run before 2026-08-28 is **not
retrospectively void** for want of a birth demonstration. It is **flagged as UNDEMONSTRATED**,
and the honest disposition of anything resting on it is decided case by case — which is exactly
the re-grade sweep Sanaa ordered the same day for dafoam's seven defective readers. **A rule that
convicted every instrument written before it was announced would be the retroactivity this
charter refused three times this week.**

**§2j.5 — AND IT BINDS THIS TEAM FIRST.** The three specimens above include **two instruments in
this team's own territory** and one this team **wrote and owns**. §2j is written by the team it
most immediately indicts, and that is the reason it is admissible rather than a reason to soften
it.

---

## Amendment — v1.22, 2026-08-31 — **§2k: EVERY NUMBER CARRIES ITS PROVENANCE. A DERIVED QUANTITY RELAYED AS AN OBSERVATION IS A FALSE EVIDENCE CLAIM EVEN WHEN THE NUMBER IS RIGHT**

**Lines whose number changed above this section: 0.**

**Occasion.** An ansys lane relayed a **derived** quantity upward with its provenance stripped — a
**fitted extrapolation reported as an observation**. **The number was right.** The team caught it
themselves and corrected it unprompted, which is why this is a clause and not an incident.

**THIS IS NOT A NEW IDEA AND IT IS IMPORTANT THAT IT IS NOT.** `CLAUDE.md` rule 12 already carries
the two-value form for **one** quantity: a cost is **`reported-by-owner, not measured`** because
the box cannot read its own billing, and dollars are **`derived, not measured`** from
core-minutes. **§2k generalises that existing discipline from costs to every number**, because
nothing about the hazard was ever specific to money.

### §2k.1 THE VOCABULARY — five tags, and they are not verdict words

| tag | means | the question it answers |
|---|---|---|
| **MEASURED** | read from an artifact that a real producer wrote, still on disk | *what happened?* |
| **DERIVED** | computed from measured values by a stated rule | *what follows arithmetically?* |
| **EXTRAPOLATED** | obtained by extending a fit or model **beyond** the data | *what would follow if the model holds?* |
| **REGISTERED** | frozen in a pre-registration or a dict — **an intention** | *what did we ask for?* |
| **REPORTED-BY-OWNER** | stated by a person or a system this box cannot verify | *what were we told?* |

**A number relayed upward without a tag is NOT REPORTABLE.** Not "discouraged" — a reader cannot
tell which of five different things they are holding, and four of them are not observations.

**⚠ THESE TAGS ARE NOT VERDICTS AND MAY NEVER BE WRITTEN WHERE A VERDICT BELONGS.** Standing rule
1's vocabulary — `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` —
is **untouched and remains closed.** A provenance tag qualifies a **number**; a verdict grades a
**gate**. **`EXTRAPOLATED` is not a verdict, and a row whose verdict cell reads `DERIVED` has lost
its verdict.** This clause adds a field beside the value; it does not add a word to rule 1.

### §2k.2 THE DECISIVE TEST, and it is one question

> **NAME THE ARTIFACT THAT WOULD HAVE TO EXIST FOR THIS NUMBER TO BE `MEASURED`, THEN CHECK
> WHETHER IT EXISTS.**

If you can name the file and it is on disk, the number is **MEASURED** and the record cites the
path. If you can name it and it does **not** exist, the number is **DERIVED**, **EXTRAPOLATED** or
**REGISTERED**, and **which one is decided by what you did instead of reading it.** If you cannot
name the artifact at all, the number is **REPORTED-BY-OWNER** at best.

**The failure mode this catches is not lying. It is the honest author who computed something
correctly and then described it in the vocabulary of observation** — *"the Courant number is 0.9"*
when what is true is *"we asked for at most 0.9"*.

### §2k.3 THE WORKED EXAMPLE, MEASURED ON THIS BOX, AND IT SPANS NINE ORDERS OF MAGNITUDE

ansys ruled, correctly, that **a declared `maxCo` records an INTENTION and only the log records
what happened.** Verified independently here on the two run roots:

| | `adjustTimeStep` | **REGISTERED** `maxCo` | **MEASURED** max Courant, from the solver's own log |
|---|---|---|---|
| `VMFL069` (R1) | **`no`** | declared | **2 869 282 454** |
| `VMFL069-R2` | **`yes`** | declared | **1.175** (mean ≈ 0.605, over 53 699 Courant lines) |

**With `adjustTimeStep no` the `maxCo` entry limited NOTHING** — R2's own `controlDict` says so in
its header — **so R1 ran at a Courant number of 2.87 × 10⁹ while its dict declared a bound.**
**The REGISTERED value and the MEASURED value differ by nine orders of magnitude on the same case
family**, and every word in the dict was true: it recorded what was asked for. **Nothing but the
log could have told anyone what happened.**

**This is §2k's whole argument in one case: `REGISTERED` and `MEASURED` are different tags because
they are different facts, and the gap between them is not bounded by anyone's good intentions.**

### §2k.4 THE CONSEQUENCE FOR GATES — and it is a gate change, so it is prospective only

**A gate on a quantity that a dict merely DECLARES is not a gate on that quantity.** A transient
registration that intends to bound the Courant number **gates on the REALISED Courant read from
the log**, never on the declared `maxCo`, and states which it used.

**PROSPECTIVE ONLY, and this is not a courtesy.** Changing what a gate reads is a **gate change**,
barred after first compute by standing rule 2. **ansys landed this on the running `VMFL069-R2` as
DISCLOSURE, NOT AS A GATE, and that is correct** — the run's gates closed when compute began, and
a disclosure that alters no threshold is exactly what rule 2 leaves available. **§2k.4 binds the
NEXT transient registration and re-grades nothing.** (§2j.4's principle, applied again.)

### §2k.5 WHAT THIS SECTION BINDS, AND WHAT IT ONLY PROPOSES — stated plainly rather than assumed

**BINDING NOW, on this team's own authority:** every number **this team** relays upward, and every
number **this team accepts in a cross-team gate audit**, carries a tag. **An audited claim whose
numbers are untagged is `NOT MEASURED` until the owning team supplies the tags** — this team's
audit mandate reaches other teams' evidence, and this is the standard that evidence is read
against.

**PROPOSED, NOT ENACTED, AND ON SANAA'S DESK:** elevating §2k into `REPORTING_CHARTER` as a
**lab-wide obligation on all six teams' upward reports.** **`REPORTING_CHARTER` is not in this
team's folder scope**, and a clause binding how five other teams report is not this supervisor's
to impose merely because the reasoning is sound. **The draft is §2k.1–§2k.2 verbatim; the decision
is Sanaa's.** Meanwhile ansys has amended its own charter (Amendment 1.6) and any team may adopt
§2k in its own — **which is the route Sanaa's 2026-08-30 directive already opens** (*"each teams
updates their own charters and standards"*).

**NOT CLAIMED:** that tagging makes a number correct. **A tag records how a number was obtained,
not whether it is right**, and a correctly-tagged `EXTRAPOLATED` value can still be wrong. §2k
closes one specific hole — **a reader unable to tell an observation from a projection** — and
closes nothing else.

| amendment record | **v1.22** |
|---|---|
| clauses added | **1** (§2k) |
| existing clauses altered, widened or narrowed | **0** |
| gate values changed | **0** |
| verdict vocabulary changed | **0** — rule 1 is closed and untouched; tags are not verdicts |
| retroactive re-grades authorised | **0** — §2k.4 is prospective |
| items placed on Sanaa's desk | **1** (the `REPORTING_CHARTER` elevation) |
| **lines whose number changed above this section** | **0** |


---

## Amendment — v1.23, 2026-08-31 — **§2k.6: THE SIXTH STATE IS A REFUSAL, NOT A TAG. A NUMBER THAT CANNOT HONESTLY TAKE ONE OF THE FIVE IS NOT REPORTABLE AT ALL**

**Lines whose number changed above this section: 0.** **Added on cfd's referral, BEFORE §2k had
been applied to anything**, and disclosed as a separate amendment rather than folded silently into
v1.22 — **an appended block is append-only even when it is minutes old and even when it is mine.**

**cfd concurred with §2k, adopted it as practice, referred the charter home here, and proposed the
clause below. It is a real improvement and I adopt it.**

### §2k.6 THE HOLE IN v1.22, NAMED BY ITS FIRST READER

§2k.1 says an untagged number is not reportable. **It did not say what happens when a number
resists ALL FIVE tags** — and the tempting move is to invent a sixth tag (`INFERRED`, `ASSUMED`,
`APPARENT`) and pass the number on wearing it. **That move is refused.**

> **A number that cannot honestly take one of the five tags IS NOT REPORTABLE. The correct action
> is to STOP AND ESTABLISH ITS PROVENANCE, never to widen the vocabulary until the number fits.**

**THE VOCABULARY IS CLOSED FOR THE SAME REASON RULE 1's IS.** A tag set that grows to accommodate
whatever needs reporting stops discriminating; the sixth tag becomes the drawer everything
awkward goes into, and the clause quietly becomes decoration.

### §2k.7 WHY THIS IS THE LOAD-BEARING HALF — the moment of failed classification IS the catch

cfd's ground, and it is better than the clause it improves: **the worst error of the night —
*"a peer has appended since"*, invented on the spot to explain a discrepancy — FITS NO TAG.** It
was not measured, not derived from anything, not extrapolated from a fit, not registered anywhere,
and nobody reported it. **It was manufactured to make a disagreement go away.**

**So the failure to classify is not an inconvenience on the way to reporting — IT IS THE DETECTION
EVENT.** A number that resists all five tags is, in that moment, **announcing that nobody knows
where it came from**, and that is exactly when it is cheap to catch. **Reaching for a sixth tag
converts the lab's best available alarm into a formatting decision.**

**The operational form:** when no tag fits, the number does not go upward. What goes upward is the
**absence** — *"this figure has no provenance and is withheld"* — which is reportable, honest, and
actionable, where the number itself was none of those.

### §2k.8 SCOPE, and one document explicitly NOT touched

**§2k.6 binds exactly what §2k.5 binds and no more:** this team's own upward numbers and the
numbers this team accepts in a cross-team gate audit. **The `REPORTING_CHARTER` elevation remains
PROPOSED and on Sanaa's desk**; cfd has adopted §2k as practice in its own territory, which is the
route Sanaa's 2026-08-30 directive opens.

**`RESULT_PRIORITY_CHARTER.md` IS NOT TOUCHED BY THIS AMENDMENT AND MUST NOT BE.** It stands at
**v0.5 carrying Sanaa's own header — *"still need to think abt this"*** — so its orderings are
**proposals, not law**, and **anything reaching into it is DRAFTED FOR HER RATIFICATION, never
landed.** Noted here because §2k concerns how evidence is qualified, which sits adjacent to how
results are ranked, and **adjacency is not authority.**

| amendment record | **v1.23** |
|---|---|
| clauses added | **1** (§2k.6–§2k.8) |
| tags added to §2k.1's vocabulary | **0 — the set is CLOSED at five, deliberately** |
| existing clauses altered, widened or narrowed | **0** |
| verdict vocabulary changed | **0** — rule 1 untouched |
| documents drafted-for-ratification rather than landed | **1** (`RESULT_PRIORITY_CHARTER`, untouched) |
| **lines whose number changed above this section** | **0** |


---

## Amendment — v1.24, 2026-08-31 — **§2l: REMOVE THE POSSIBILITY, NOT THE INSTANCE. Three repairs landed on one night in three teams' territory turned out to be one move, and it is worth naming rather than rediscovering a fourth time**

**Lines whose number changed above this section: 0.**

**Occasion.** Three repairs landed on 2026-08-30/31, by three different teams, against three
unrelated defects. **Reading them side by side they are the same move**, and none of them fixes
the thing that broke.

### §2l.1 THE THREE SPECIMENS, each cited to its own record

| | the defect | the ORDINARY fix nobody took | what was done instead |
|---|---|---|---|
| **DERIVE, DON'T MAINTAIN** | `NUMERICS_KNOWLEDGE`'s FAMILY INDEX had drifted **8 entries** — `N-C` listed `N-C1` alone against an actual `N-C7`. **Five of seven families were correct, and the only two stale were the two that had GROWN.** | *update the index; assign someone to keep it fresh* | the index is **generated from the tail** by `scripts/check_numerics_index.py`, and `check_harness [5/5]` asserts it. **A hand-maintained derived value does not drift less when watched more.** (`DEAD_LEVER_AUDIT` §19) |
| **MOVE THE SAFETY INTO THE PATH** | An **unquoted heredoc** command-substituted prose. **Three teams lost bytes to it in ONE AFTERNOON**, including the lab's only handoff channel, **each team already knowing the rule.** | *be careful with heredocs* | `scripts/append_block.py` reads the body **from a FILE as BYTES, so no shell ever sees it**, asserts every substitution, and reverts on any byte difference. (`L-403`, `L-405`) |
| **MAKE THE BAD STATE UNREPRESENTABLE** | The queue runner's round-robin cursor lived in **two unit systems** — written as an index into the 6-tuple `TEAMS`, read modulo the *filtered* list. **Not a bias: an ABSORBING STATE. 12 of 12 launches went to one team while the log looked healthy.** | *correct the modulus* | state is the **last-launched TEAM NAME**, which **has no unit system and cannot be taken modulo the wrong length**. cfd's own words: *"the defect is not fixed, it is UNREPRESENTABLE."* (`bec46169`) |

**In none of the three was the ordinary fix wrong.** Each would have worked, that day, on that
instance. **Each also leaves the defect one plausible edit away from returning**, and in two of the
three it already had returned before anyone acted.

### §2l.2 THE TEST — one question, and it is answerable

> **AFTER THIS REPAIR, WHAT WOULD IT TAKE TO REINTRODUCE THE DEFECT?**
>
> If the answer is *"an edit a careful person could plausibly make"* — **the possibility is still
> there and only the instance was removed.**
> If the answer is *"you would have to reinstate the mechanism itself"* — **the possibility is
> gone.**

A corrected modulus is one keystroke from being wrong again, and **the original was invisible
precisely because both expressions were individually reasonable**. A team name cannot be taken
modulo anything. **That difference is the whole clause.**

### §2l.3 WHEN TO REACH FOR IT — because "always" is wrong and would be expensive

**Two triggers, either sufficient:**

1. **RECURRENCE.** The same defect has landed more than once, anywhere in the lab. Twice is a
   pattern; a third occurrence is a statement about the mechanism rather than about the people.
2. **EFFORT ASYMMETRY — the safe path is HARDER than the unsafe one.** `L-405`'s evidence is the
   canonical form: **three careful teams hitting one defect in one afternoon is not three lapses,
   it is evidence that the safe path cost more than the unsafe one.** Where that is true, no
   amount of discipline is load-bearing, because discipline is exactly the thing being taxed.

**A first occurrence with no asymmetry gets the ORDINARY FIX.** Reaching for this move on a
one-off is over-engineering, and this clause does not license it.

### §2l.4 THE HONEST LIMIT, AND IT HAS A WORKED COUNTER-EXAMPLE FROM THE SAME NIGHT

**Not every defect has a possibility that can be removed, and pretending otherwise produces
elaborate machinery around a judgement that still has to be made.**

**`T16`/`C_ORDER` is the counter-example** (`DEAD_LEVER_AUDIT` §18). A guard hunting a **−1.0**
transposed-ordering signal carried a **1e-06** tolerance and fired on **−7.4e-05** of real physics.
**There is no way to make "a tolerance mis-sized for the defect it hunts" unrepresentable.** The
remedy there was **split the clause and size each tolerance to its own signal** — a judgement about
what the guard is *for*, which no construction can take over. **§2l does not reach it, and a lane
citing §2l to avoid making that judgement has misread this section.**

**AND THE FAILURE MODE OF THE PRINCIPLE ITSELF, named so it can be caught:** claiming a state is
*unrepresentable* when it has merely become **inconvenient**. The claim is checkable by §2l.2's
question, asked honestly and in writing. **"It would be weird to write that now" is not
unrepresentability.**

### §2l.5 SCOPE

**Binding on this team's own repairs, and it is the standard this team's cross-team gate audits
read a repair against** — an audited repair that fixes an instance where the possibility was
removable is **not thereby refused**, but the record says which was done and why. **§2l changes no
gate, retires nothing, and creates no verdict.**

**Elevation to `docs/standards/INNOVATION_STANDARD.md` — where a principle about how the lab
BUILDS things arguably belongs — is PROPOSED, NOT TAKEN.** That file is not in this team's folder
scope. **Drafted here, in this team's own charter, for Sanaa to elevate if she wants it lab-wide**;
any team may adopt §2l in its own charter meanwhile, which is the route her 2026-08-30 directive
opens.

| amendment record | **v1.24** |
|---|---|
| clauses added | **1** (§2l) |
| existing clauses altered, widened or narrowed | **0** |
| gate values changed | **0** |
| verdict vocabulary changed | **0** |
| specimens cited, each to its own record | **3** |
| worked counter-examples shipped | **1** (`T16`/`C_ORDER`) |
| **lines whose number changed above this section** | **0** |


---

## Amendment — v1.25, 2026-08-31 — **§2k.9: MY OWN §2k.1 WAS INCOMPLETE AND heat-transfer FALSIFIED IT WITH A SPECIMEN. THE SET IS NOW EIGHT, STILL CLOSED, AND LAB-WIDE — because team-local was the one option guaranteed to produce six dialects**

**Lines whose number changed above this section: 0.**

**§2k.1 published five tags and §2k.6 called the set CLOSED. The closure principle was right. THE
COUNT WAS WRONG, and heat-transfer showed it with a case rather than an argument.** Their proposal
is `docs/campaigns/T-family/PROVENANCE_TAGGING_PROPOSAL_2026-08-31.md`, adopted team-locally and
**deliberately not imposed lab-wide** — the correct routing, and it is why this ruling is clean.

### §2k.9.1 THE FALSIFICATION, AND I ADOPT THEIR ARGUMENT OVER MY OWN FIRST INSTINCT

Their **§R-P.4**: ***"`BORROWED` MAY NOT HIDE INSIDE `DERIVED`."*** A value measured on a
**different object** and asserted to apply here is:

- **not `MEASURED`** — not on this object;
- **not `DERIVED`** — there is no rule taking it from *this* object's own data;
- **not `EXTRAPOLATED`** — nothing is being extended along a fit;
- **not `REGISTERED`** — registration says a value is *frozen*, not where it came from; a
  registered value may be measured **or** borrowed, so the tag is **orthogonal**, not a home;
- **not `REPORTED-BY-OWNER`** — the box **can** verify it; the source rung is on this disk.

**My own first instinct was to map `BORROWED` onto `MEASURED` with an origin field. That is wrong
and their clause says why: it would assert an observation of an object nobody observed.** I adopt
their reading.

**The same test applied to the other two:** `ASSUMED` — *chosen by judgement, with **no measurement
anywhere behind it*** — is a claim about the **absence of a measurement at the root of the chain**,
which no other tag makes. `TRANSCRIBED` — *copied from another record rather than re-derived from
the artifact* — is a **fidelity claim about a copy step**, and their specimen shows it earning its
keep: a `1.528×` transposed into a heat-transfer census **belongs to `F22_LAMB_OSEEN`, a cfd rung**
(`COST_CALIBRATION.md:229`, `C-153`). **A cross-team mis-attribution that no other tag would have
surfaced.**

### §2k.9.2 THE SPECIMEN THAT DECIDES IT — a two-hop borrow, and the miss compounds

    T20 rate 2.80e-07  ←  borrowed from T17's reading
    T17 registered 1.64e-07  ←  borrowed from T14
    2.80e-07 / 1.64e-07 = 1.707

**T20's rate is the T14 borrow multiplied by T17's measured miss OF THAT SAME BORROW.** The error
did not merely propagate — **it compounded, and nothing in the number shows it.**

**AND THEY EXCLUDED THE INNOCENT EXPLANATION BEFORE CLAIMING THE GUILTY ONE, which is why I accept
the attribution.** T17's registered `0.137` core-min against an actual `0.233` is **1.7007×**, and
`T17_CY_c` **ran ALONE** — `02:25:17Z` to `02:25:31Z`, the next T17 case starting `16:15:56Z`, a
gap of **49,825 s (13 h 50 m)**. **So the miss is the BORROWING, not contention.** That is the
control this team demands of others, done unprompted against their own registration.

### §2k.9.3 THE RULING

**THE SET IS EIGHT AND REMAINS CLOSED:** `MEASURED` · `DERIVED` · `EXTRAPOLATED` · `REGISTERED` ·
`REPORTED-BY-OWNER` · **`BORROWED`** · **`ASSUMED`** · **`TRANSCRIBED`**.

**§2k.6 IS UPHELD, NOT WEAKENED.** A number that fits none of the eight is still **NOT REPORTABLE**,
and the sixth-state refusal stands verbatim. **What changed is the count, once, on evidence** — and
**the bar for any future change is now stated so this cannot become a drifting vocabulary:**

> **A NEW TAG IS ADMITTED ONLY ON A SPECIMEN SHOWING THAT AN EXISTING TAG WOULD BE *FALSE*, NOT
> MERELY COARSE.** *"The existing tag loses detail"* is not sufficient — that is what the mandatory
> fields below are for. **`BORROWED` cleared this bar; a ninth tag must clear it too.**

**LAB-WIDE, NOT TEAM-LOCAL, AND THE REASONING IS NOT A PREFERENCE:**

1. **The three already exist VERBATIM in FROZEN records** — `T17_registered.json`
   (`cost.rate_provenance`), `T20_PREREGISTRATION.md:999-1001`, `T17_CY_f.json:21`. **Rule 6 forbids
   rewriting them**, so ruling the words team-local would not remove them from the lab's records; it
   would only make them unreadable outside one team.
2. **Team-local is the one option that GUARANTEES the dialect problem** it was meant to avoid: six
   teams meeting the same gap independently mint six words for it. **A shared vocabulary of eight
   beats a private vocabulary of three plus five unwritten ones.**
3. **heat-transfer did not impose it, and that restraint should not cost them the ruling.**

### §2k.9.4 MANDATORY FIELDS — the reason each tag exists is a field, not the word

| tag | MUST also carry |
|---|---|
| **`BORROWED`** | **the object the value was measured on**, and where that source is itself borrowed, **the chain stated to its MEASURED ROOT, with its depth.** A borrow of a borrow is disclosed as such. |
| **`ASSUMED`** | that **no measurement lies behind it**, and **what would falsify it** |
| **`TRANSCRIBED`** | **the record it was copied from**, by path and line |

**The chain-depth clause is the whole point of `BORROWED` and is not optional.** §2k.9.2's specimen
is a **depth-2** borrow whose compounding is invisible in the value; **a depth-1 disclosure would
have hidden exactly the thing that mattered.** A borrowed value at depth *n* has had *n*
opportunities to stop applying, and **none of them is visible in the number.**

### §2k.9.5 WHAT THIS DOES NOT DO

**It does not make a tagged number correct** (§2k's own limit, restated). It **adds no verdict
word** — rule 1 is closed and untouched, and none of the eight may sit where a verdict belongs. It
**re-grades nothing**: registrations already carrying these words in frozen text are **compliant as
written**, and this amendment is what makes them readable lab-wide rather than a defect to repair.

**The `REPORTING_CHARTER` elevation of §2k remains PROPOSED and on Sanaa's desk, now covering
eight tags rather than five.**

| amendment record | **v1.25** |
|---|---|
| tags in the closed set | **5 → 8**, once, on a specimen |
| §2k.6's refusal-not-a-tag principle | **UPHELD verbatim** |
| bar for a ninth tag | **stated** — an existing tag must be shown FALSE, not coarse |
| existing clauses altered, widened or narrowed | **0** |
| gate values changed | **0** · verdict vocabulary changed | **0** |
| re-grades authorised | **0** |
| **lines whose number changed above this section** | **0** |


## Amendment — v1.26, 2026-08-31 — **[SANAA-DIRECT] §2m: THE FREEZE CLOCK. A FEASIBILITY RUNG HAS NO GATE TO FREEZE, SO RULE 2 NEVER REACHED IT — AND A DRAFT MAY NOT BE POLISHED PAST FOUR HOURS**

**Lines whose number changed above this section: 0.**

**Sanaa's words, verbatim, 2026-08-31** (captured at
`etc/sessions/2026-08-31T1513Z_sanaa_freeze_clock_and_so3_ruling.md`, commit `927924f1`; that
session file is not edited — this section is the amendment):

> Effective immediately, cfd and heta transfer teams: start the L1 feasibility solves on Cases 1
> and 2 NOW — no freeze required for feasibility/physics rungs, never was. Freeze in 10-line
> template form within 4 hours; anything a draft still "needs" after that becomes a W-3 amendment
> after first fields exist. New standing rule — FREEZE CLOCK: a prereg draft older than 4 hours
> without a freeze auto-escalates to the supervisor, who freezes the template version on the spot.
> First report on any new case must contain a converged coarse field, or one line saying why not —
> not a document status.

### §2m.1 WHY "NEVER WAS" IS LITERALLY TRUE, AND WHY THAT MATTERS MORE THAN AN EXCEPTION WOULD

**Rule 2's freeze attaches to the GATE.** Its entire evidentiary content is that *the gate could
not have been chosen to fit the answer* — so its object is a gate, a threshold, a cap and a label.
**A rung that declares none of those has nothing for rule 2 to bite on.** This is therefore **not
an exception to rule 2 and not a widening of it**: it is the observation that rule 2's object is
**absent**, which is exactly what "never was" asserts. **Recording it as an exception would have
been the more dangerous drafting**, because an exception invites the question *what else qualifies*
— and the answer here is structural, not discretionary.

**THE CONSEQUENCE IS IMMEDIATE AND IT IS THE POINT: the moment a gate exists, the freeze is back,
with nothing weakened.** §2m does not move the freeze later for any gated run; it identifies runs
that never had one to move.

### §2m.2 WHAT A FEASIBILITY/PHYSICS RUNG IS — and the boundary is SELF-POLICING, not a judgement call

A rung is **feasibility/physics** when it declares **no gate, no threshold, no band and no
pre-registered label**, and asks only: *does this run at all, and what does the physics look like?*

> **THE PRICE, AND IT IS WHAT KEEPS THE CLASSIFICATION HONEST: A FEASIBILITY RUNG'S OUTPUT IS NOT
> A VERDICT AND MAY NOT BE REPORTED AS ONE.** It may emit **no** word from the fixed vocabulary —
> not `PASS`, not `GATE REACHED`, not `GATE FAIL`. Its numbers are reportable as **observations**,
> tagged per `REPORTING_CHARTER`'s eight-tag rule, and **nothing may be cited from it as a
> result.**

**This is the whole anti-abuse mechanism and it needs no policing instrument.** The tempting
misuse — reclassify gated work as "feasibility" to skip the freeze — **costs the reclassifier the
ability to claim anything**. A team that wants a verdict must freeze; a team that freezes nothing
gets no verdict. **The two cannot be had together, and no auditor has to adjudicate intent.**

**A feasibility rung that later wants a verdict does not get one retroactively.** It freezes a
registration and **runs again**. Fields already on disk are evidence about the physics and may
inform the registration; they are **not** the registration's answer, because they existed before
the gate did — which is `§2d` in its original form.

### §2m.3 THE FREEZE CLOCK — and the clock's START is defined here, because an undefined clock is unenforceable

- **A pre-registration draft reaches four hours old without a freeze → it AUTO-ESCALATES to its
  supervisor, who freezes the TEMPLATE version ON THE SPOT.** The supervisor does not first
  improve it.
- **THE CLOCK STARTS AT THE EARLIER OF: the draft's first commit, or its file mtime on disk** —
  the **earlier**, deliberately, so that **touching, moving, renaming or re-writing the file cannot
  reset it.** A clock a draft can restart by being edited is a clock that rewards polishing, which
  is the exact behaviour this rule exists to end.
- **Ten lines is a FLOOR, not a target**, and the template version is a **complete** freeze: gate,
  threshold, cap, label, grading path. A freeze missing any of those is not a short freeze, it is
  **not a freeze**, and §2m does not license one.
- **Everything a draft still "needs" after the freeze becomes a W-3 amendment AFTER first fields
  exist** — never a pre-freeze delay. Post-compute, `§2b` and `§2d`/`§2d.1` govern what such an
  amendment may touch, **and §2m changes neither.**

**THIS IS A STANDING SUPERVISOR DUTY.** It joins the four non-delegable checks in practice though
not in `SUPERVISION_CHARTER` §3's enumeration: **a supervisor who lets a draft pass four hours has
failed the rule, not the draft's author.**

### §2m.4 WHAT §2m DOES **NOT** DO — stated as flatly as possible, because this is the clause most easily misread

1. **It does not permit ANY gated solve to run unfrozen.** Rule 2 is untouched, in full force, and
   the freeze still **precedes** the first gated run.
2. **It does not shorten, weaken or waive any freeze requirement** — it removes **draft-polishing
   time**, not pre-registration.
3. **It creates no new verdict, retires no gate, and re-grades nothing.**
4. **It does not make a feasibility rung's numbers citable.** See §2m.2.
5. **It does not reach `§2j`'s birth requirement:** an instrument that grades anything still owes
   its planted control **before** it grades, feasibility rung or not, because §2j attaches to the
   INSTRUMENT rather than to the rung.

### §2m.5 THE REPORTING LIMB

> **The first report on any new case carries a CONVERGED COARSE FIELD, or ONE LINE saying why not —
> never a document status.**

*"Pre-registration drafted"*, *"template under review"*, *"awaiting freeze"* are **not reportable
first-report content.** The unit of progress on a new case is **a field on disk**, and where there
is none the report owes the **reason**, in one line, not the paperwork's state. This limb is a
reporting rule and is cross-referenced into `REPORTING_CHARTER`; **where the two are read together
the requirement is the same one, not two.**

### §2m.6 SCOPE

Lab-wide standing rule, effective 2026-08-31, **prospective**. Drafts already older than four hours
at this date are escalated **on their next touch or their team's next report**, not retroactively
declared in breach — the same non-retroactivity `§2h.6`, `§2i.4` and `§2j.4` applied against this
team's own interest.

| | |
|---|---|
| amendment record | **v1.26** |
| clause added | **§2m** (freeze clock; feasibility rungs) |
| rule 2 weakened, narrowed or excepted | **0 — its object is absent, not waived** |
| gated solves permitted to run unfrozen | **0** |
| existing clauses altered | **0** · gate values changed | **0** |
| verdict vocabulary changed | **0** · re-grades authorised | **0** |
| new duty created | **1** — the four-hour clock, on supervisors |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.27, 2026-08-31 — **[SANAA-DIRECT] §2h.6: THE EXACT-PDE RULE. THE CONTINUUM ROW SPLITS, AND THE TEST IS SAMENESS OF MODEL — NEVER EXACTNESS OF ALGEBRA**

**Lines whose number changed above this section: 0.**

**Sanaa ruled, and I read her words at source before writing law from them** rather than
from the relay that carried them (rule 9 — no agent message is her consent). Captured
verbatim at `5dd94f4f`, `etc/sessions/2026-08-31T2016Z_sanaa_three_rulings_runner_2h3_f28floor.md`:

> **`"§2h.3": exact-PDE rule`**

**Her wording is terse, so the substance is the referral she answered**, and §2h.3 is where it
sits. §2h.3 referred **with recommended wording**: *"split the CONTINUUM row so that exact or
manufactured solution of the same continuum model is named separately and is `PASS`-capable
when §2h.4's conditions are met."* **She confirmed it. It is now law rather than an interim
classification.**

### §2h.6.1 THE RULE

> **A reference that is the EXACT (or manufactured) SOLUTION OF THE SAME CONTINUUM PDE THE
> SOLVER DISCRETISES is `PASS`-capable, when §2h.4's five conditions are met and declared in
> the registration before compute.**
>
> **A reference drawn from a DIFFERENT MODEL — nozzle relations, shock tables, lumped or
> series-resistance paths, correlations, experiment — CAPS AT `GATE REACHED`, HOWEVER EXACT
> ITS OWN ALGEBRA.**

### §2h.6.2 THE TEST IS SAMENESS OF MODEL, AND THE FAILURE MODE IS READING IT AS EXACTNESS

**The discriminating question is not *how exact is this reference?* but *is this the solution
of the equations my solver is discretising?*** Those come apart, and the place they come apart
is exactly where the cap is needed:

- **A closed-form isentropic nozzle relation is EXACT ALGEBRA and a DIFFERENT MODEL.** It
  solves quasi-1D isentropic flow; the solver discretises 2D/3D RANS. The residual between
  them contains **model-form error**, and no amount of algebraic exactness removes it.
- **A shock table is exact for the Rankine–Hugoniot jump conditions**, which is not the
  system a shock-capturing scheme integrates across a smeared numerical shock.
- **A lumped or series-resistance path is exact for the lumped model**, which is a *reduction*
  of the field equations, not the field equations.

**In every one of those the algebra is unimpeachable and the referent is still the wrong
object.** `§2f.3`'s cap exists for precisely that residual, and this amendment does not weaken
it — **it names the one case where the residual is discretisation error by construction, and
leaves every other case where it was.**

### §2h.6.3 WHAT IT CONFIRMS RATHER THAN INVENTS

**§2h.4 condition 1 already said this and already called itself load-bearing:** *"the reference
is the exact or manufactured solution of the same continuum model the solver discretises… this
is what makes model-form error zero by construction and the residual discretisation error."*
**What was interim was its AUTHORITY, not its content** — §2h.3 held that **narrowing a cap is
Sanaa's alone, exactly as retiring a clause is (D539)**, and refused to take it. **She has now
taken it.** §2h.4's five conditions are **unchanged and all five still bind**; condition 2's
one-way rule-5 limb is untouched, and **"no triple" still never means "no rule 5" (§2f.2)**.

**§2f.3's CONTINUUM row is hereby SPLIT** — *exact or manufactured solution of the same
continuum model* becomes its own row, `PASS`-capable under §2h.4; **experiment, correlation and
every different-model reference remain capped at `GATE REACHED`.** §2h.3's own four-row table
already carries the ground for the split and is the reference for it.

### §2h.6.4 IT IS PROSPECTIVE, AND GRADED ROWS STAND

**A rule cannot re-grade a closed gate.** Gates close at first compute (rule 2, §2d), and a
verdict already earned under the classification in force when it was frozen is not disturbed by
this amendment. **Sanaa confirmed the instance directly: `VMFL038-R2`'s limb A STANDS AS
GRADED**, and its `PASS`-capability is **permanent law rather than interim classification.**
ansys-verification is to be told that its row's standing no longer depends on a pending ruling.

**Equally, this amendment creates no retrospective `PASS`.** A row capped at `GATE REACHED`
under §2f.3 before today is not promoted by it; the availability of `PASS` is a property of a
registration frozen **after** this rule, declaring §2h.4's conditions before compute.

### §2h.6.5 ⚠ AN OPEN QUESTION THIS RULING CREATES, FLAGGED RATHER THAN GUESSED

**§2h.5 ruled `PASS` available to `T9a-R1c`'s floor limb on what it calls *"an exact
series-resistance referent."*** **Under §2h.6.1, a series-resistance path is named among the
different-model references that cap at `GATE REACHED`** — *unless* the solver is discretising
that same one-dimensional conduction problem, in which case series resistance **is** the exact
solution of the same continuum model and condition 1 is met.

**Which of those `T9a-R1c` is, this amendment DOES NOT DECIDE, and I will not guess it into
law.** It is a question about that rung's own registration and it belongs to **heat-transfer**
to answer against §2h.4 condition 1: *is the referent the exact solution of the equations the
solver discretises, or a reduction of them?* **If the latter, §2h.5's `PASS` availability falls
to `GATE REACHED` prospectively — and if the rung is already graded, §2h.6.4 protects the row
and the correction is to the classification, not to the verdict.** **Raised here because a new
rule that silently contradicts an old ruling is worse than one that names the contradiction.**

### §2h.6.6 WHAT THIS AMENDMENT DOES NOT DO

**It does not touch §2f.3's cap for anything but the split row.** **It does not weaken rule 5**
— a level not iteratively converged or not plateaued is `NOT A RESULT` whatever the referent,
and the one-way conversion is unchanged. **It does not make a floor demonstration into a
triple:** §2h.4 condition 5 still bounds the claim to the levels actually run, and §2g.3's
overreaching phrase stays narrowed. **And it does not license a continuum claim** — condition 4
still tests the registration's own sentence, so a floor demonstration **worded** as a continuum
claim is still caught by §2f.3 however impeccable its referent.

| field | value |
| --- | --- |
| authority | **Sanaa, `5dd94f4f`, verbatim, read at source** |
| ruled | `§2h.3`'s referral CONFIRMED — the exact-PDE rule |
| clauses added | `§2h.6.1`–`§2h.6.6` |
| clauses unchanged | `§2h.4` all five conditions; `§2f.2`; rule 5's one-way limb; `§2g.3` as narrowed |
| instance confirmed | `VMFL038-R2` limb A **stands as graded**; `PASS`-capability permanent |
| open, referred to heat-transfer | `§2h.5` / `T9a-R1c`'s series-resistance referent under `§2h.6.1` |
| retrospective effect | **none** — prospective only; no row promoted, no row demoted |
| amendment record | **v1.27** |

---

## Amendment — v1.28, 2026-08-31 — **§2h.8: A LABEL REPAIR, NOT A RULE CHANGE. `§2h.6` NAMED TWO RULES AT ONCE — MINE, ONE COMMIT OLD — AND THE EXACT-PDE RULE TAKES THE FREE NUMBER**

**Lines whose number changed above this section: 0.**

**Nothing in this amendment moves a gate, a band, a threshold, a cap, a label or a
verdict. It moves a NUMBER ON A CLAUSE.** Read it as bookkeeping and it is bookkeeping —
but it is bookkeeping that decides whether a `PASS`-capable registration can cite its
own ground, which is why it lands as law rather than as a note.

### §2h.8.0 THE DEFECT, AND WHO FOUND IT

**`§2h.6` is occupied twice in this document, and I wrote the second one.**

- **v1.19, 2026-08-27, line 2882** — `§2h.6 NON-RETROACTIVITY`.
- **v1.27, 2026-08-31, line 3604ff** — `§2h.6.1`–`§2h.6.6`, the exact-PDE rule.

**Four live citations already point at the older meaning** — lines `2895`, `2974`, `3104`
and `3588` — and **the sharp edge is inside my own new amendment**: `§2h.6.4` is headed
*"IT IS PROSPECTIVE"*, which **is** the old `§2h.6`'s doctrine. One amendment used one
label both for the rule it states and for the rule that bounds it.

**FOUND BY `ansys-verification`, and found in the one way that works.** They were told
by a peer that Sanaa had ruled; under standing rule 9 they **did not take the peer's
word**, went to `27a49bda` and read the bytes — and the collision fell out of that read.
They **reported it and repaired nothing**: my file untouched, no number proposed, the
finding routed rather than acted on. **That is the correct handling of a defect in
another team's territory, and it is recorded here as such.** They then banned a bare
`§2h.6` in their own territory (`ANSYS_VERIFICATION_CHARTER` §12.3) rather than wait for
me. **A team that protects itself from another team's defect while declining to edit
that team's file is doing exactly what the cross-team audit mandate asks of it.**

**I record the ugly half plainly: this team audits other teams for exactly this, and
`879d7726`'s subject line — a charter label naming two rules at once — was written about
MY document, sixteen minutes after I committed the collision.**

### §2h.8.1 THE RULING — THE EXACT-PDE RULE IS `§2h.8`, AND `§2h.6` IS NON-RETROACTIVITY ALONE

> **`§2h.6` denotes NON-RETROACTIVITY (v1.19) and nothing else.** The four existing
> citations at lines `2895`, `2974`, `3104` and `3588` resolve to it correctly and are
> **undisturbed**.
>
> **The EXACT-PDE RULE is `§2h.8`.** Its six subclauses map ONE-TO-ONE and in order onto
> the v1.27 text: `§2h.6.1` → **`§2h.8.1`**, `§2h.6.2` → **`§2h.8.2`**, `§2h.6.3` →
> **`§2h.8.3`**, `§2h.6.4` → **`§2h.8.4`**, `§2h.6.5` → **`§2h.8.5`**, `§2h.6.6` →
> **`§2h.8.6`**. **The words of each are unchanged.** `§2h.7` is not free — v1.19 gave it
> to the `§2g.4` narrowing — so the exact-PDE rule takes the next free number, `§2h.8`.

**`§2h.8.1` therefore reads, verbatim as v1.27 wrote it:** a reference that is the
**exact or manufactured solution of the same continuum PDE the solver discretises** is
`PASS`-capable under `§2h.4`'s five conditions declared before compute; a reference from
a **different model** — nozzle relations, shock tables, lumped or series-resistance
paths, correlations, experiment — **caps at `GATE REACHED`, however exact its own
algebra.** The test is **sameness of model, never exactness of algebra.**

### §2h.8.2 THE v1.27 BLOCK IS NOT EDITED, AND WHY THAT IS THE WHOLE POINT

**Standing rule 6: frozen files are never edited.** The v1.27 amendment **stands on the
page exactly as committed at `27a49bda`**, including its own `§2h.6.x` numbering and
including `§2h.6.4`'s heading. **I did not go back and renumber it, and the temptation to
do so is precisely the failure this rule exists to stop** — a document whose history is
tidied is a document whose citations cannot be checked against what was actually frozen.

**So this amendment is a MAPPING, not a rewrite.** A reader who meets `§2h.6.1` in the
v1.27 block, or in a record frozen between `27a49bda` and now, reads it through
`§2h.8.1`. **The substance is identical; only the address changed.**

### §2h.8.3 A BARE `§2h.6` IS NON-CONFORMING LAB-WIDE FROM TODAY

**`ansys-verification` banned it in their territory. I adopt the ban for the lab**, in
their form, because the reasoning is theirs and it is right: a `PASS`-capable
registration must cite its ground on a document that is then **FROZEN**, and a frozen
document cannot be repaired afterwards. **A bare `§2h.6` in such a registration would
name two rules, one of which — non-retroactivity — DEFEATS the claim the citation is
offered to support.** The citation must be unambiguous **at the freeze** or not at all.

> **THE CITATION FORM, lab-wide:** subclause **+ version + date + name**. For the
> exact-PDE rule: **`VERIFICATION_CHARTER §2h.8.1 (v1.28, 2026-08-31, the exact-PDE
> rule)`**. For non-retroactivity: **`VERIFICATION_CHARTER §2h.6 (v1.19, 2026-08-27,
> non-retroactivity)`**. **A bare `§2h.6` is non-conforming and a grader may refuse it.**

### §2h.8.4 THIS AMENDMENT IS NOT A SUBSTANTIVE CHANGE, AND NON-RETROACTIVITY DOES NOT BITE

**A registration frozen between `27a49bda` and this amendment that cites `§2h.6.1` for
the exact-PDE rule IS VALID and stays valid.** Non-retroactivity (`§2h.6`, v1.19) bars a
registration from claiming the **benefit of a clause that did not exist**. The clause
existed — Sanaa ruled it, it was law from `27a49bda` — and **only its number moves here.**
A rule against back-dated SUBSTANCE is not a rule against correcting an address, and
stretching it that far would convert a protection into a trap.

**Equally, and for the same reason, this amendment creates no `PASS` and destroys none.**
`VMFL038-R2` limb A **stands as graded** (`§2h.8.4`, formerly `§2h.6.4`) and its
`PASS`-capability is **permanent law, not interim classification** — that was Sanaa's
ruling and nothing here touches it. **`ansys-verification` has already read that at
source for itself**, so it is confirmed to them rather than announced.

### §2h.8.5 THE OPEN REFERRAL SURVIVES THE RENUMBER, UNCHANGED

**`§2h.5` / `T9a-R1c`'s series-resistance referent remains open and remains
heat-transfer's to answer**, now against **`§2h.8.1`**. The question is unchanged: *is
the referent the exact solution of the equations the solver discretises, or a reduction
of them?* If a reduction, `§2h.5`'s `PASS` availability falls to `GATE REACHED`
**prospectively**; if the rung is already graded, `§2h.8.4` protects the row and the
correction is to the **classification**, not to the verdict. **I still do not decide it.**

### §2h.8.6 THE LESSON I AM WILLING TO STATE AGAINST MYSELF

**A clause number is an instrument.** This team requires every other team to cite its
ground precisely, refuses gates whose comparator was not frozen, and audits labels for a
living — and it minted a duplicate address in its own constitution because it appended a
new subclause to a family without re-deriving which numbers in that family were already
taken. **That is `CLAUDE.md` rule 11's own defect class — a number assigned from the
shape of the thing rather than from the maximum actually present — committed in the
document that teaches it.** The re-derivation is one `grep`; it was not run.

| field | value |
| --- | --- |
| defect | `§2h.6` occupied twice — v1.19 non-retroactivity, v1.27 exact-PDE |
| found by | **`ansys-verification`**, by reading `27a49bda` at source under rule 9; reported, **not repaired** |
| ruled | exact-PDE rule is **`§2h.8`**; `§2h.6` is **non-retroactivity alone** |
| clauses renumbered | `§2h.6.1`–`§2h.6.6` → **`§2h.8.1`–`§2h.8.6`**, one-to-one, **words unchanged** |
| v1.27 block | **NOT EDITED** — stands as frozen (rule 6) |
| gate values changed | **0** · bands | **0** · caps | **0** · labels | **0** · verdicts | **0** |
| rows re-graded | **0** — `VMFL038-R2` limb A stands as graded |
| new duty created | **1** — the citation form; a bare `§2h.6` is non-conforming lab-wide |
| open, still referred | `§2h.5` / `T9a-R1c` → heat-transfer, now against `§2h.8.1` |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.29, 2026-08-31 — **[SANAA-DIRECT] §2n: THE CAUSE CLASS. EVERY NON-`PASS` VERDICT NAMES WHY, FROM A CLOSED SET OF EIGHT — AND THE PRECEDENCE THAT DECIDES A ROW FITTING TWO IS FAIL-CLOSED AWAY FROM PHYSICS**

**Lines whose number changed above this section: 0.**

**Sanaa's GRADING TRANSPARENCY ORDER, 2026-08-31**, captured verbatim by the chief at
`4116024a` (`etc/sessions/2026-08-31T2055Z_sanaa_grading_transparency_order.md`). **Read at
source before this was written** (standing rule 9 — no agent message is her consent,
including the one that carried this). **Her order passes her own 14-day rule freeze by its
own terms:** rules spawn only with her approval, and this **is** her approval.

**Her stated purpose, in her words, is the thing this amendment must serve:** *"This is
mostly for me to start separating what breaks due t physics/ numerics without a plausible
explanation vs what breaks according to the theory vs what breaks bc of bookeeping etc."*
And: ***"referee trouble never again wears a physics costume in any report I read."***
Every mechanic below is chosen to make that sentence true, and where a choice was
available I took the one that makes a physics claim **harder**, never easier.

### §2n.1 THE CLOSED SET OF EIGHT — HER TEXT, NOT A PARAPHRASE

Every non-`PASS` verdict carries **exactly one** of these. **No free text, no ninth class,
no synonyms** — the same discipline §2 already imposes on the verdict vocabulary itself.

| # | class | her definition, verbatim | her anchor |
| --- | --- | --- | --- |
| 1 | **`BUDGET/KILL`** | *"cap hit or external death (meter, box)"* | JF1's pending item |
| 2 | **`NAMING/PLUMBING`** | *"paths, ids, directories, collisions"* | SO3aR's shared run dir |
| 3 | **`BOOKKEEPING`** | *"record/STATUS/rc/ledger failure; solve fine, stamp impossible"* | arm O, K0d |
| 4 | **`INSTRUMENT`** | *"comparator/reader/guard defect; physics unjudged"* | banner-match, blind readers |
| 5 | **`GATE-DESIGN`** | *"the gate itself was defective or ungradeable as registered"* | τ_w conservation identity, F28's no-floor criterion |
| 6 | **`REFERENT-CEILING`** | *"result fine; the reference caps the tier … or isn't obtainable"* | T18, T16 |
| 7 | **`MODEL-LIMIT`** | *"physics missed where the literature says this model class misses. Expected failure, correctly measured."* | SST hump +13.9 %, turbulent cavities |
| 8 | **`PHYSICS-FAIL`** | *"proven instrument, band genuinely missed. The solver's answer is wrong vs reality."* | dam break +11 % |

**Only classes 7 and 8 say anything about the lab's ability to do physics.** Her rule,
unaltered: *"Only the first two say anything about the lab's ability to do physics."*
(She numbers them first in her list; they are 7 and 8 in the precedence order below, and
**the set is identical** — the renumbering is precedence, not a change of membership.)

### §2n.2 THE CLASS IS ASSIGNED BY THE GRADING RECORD AND CITED LIKE ANY CLAIM

Her rule: *"the class is assigned by the grading record, cited like any claim."* Operationally:

> A cause-class cell carries **the class AND a citation that resolves at `HEAD`** to the
> grading record that assigns it — a path with a line number, or a commit sha. **A class
> with no resolving citation is not a class**, exactly as a number with no artifact is not
> a measurement (§2k).

**A supervisor may not assign a class from recollection, from a case's reputation, or from
the shape of the failure.** If the grading record does not support a class, the row is
`UNCLASSED` (§2n.4) and that is a **finding**, not a formatting gap.

### §2n.3 ⚠ THE PRECEDENCE ORDER — THE MECHANIC THAT ACTUALLY DECIDES THINGS

**A real row commonly fits two classes, and her order does not say which wins.** This is
the gap that would otherwise generate a referral per case, so it is ruled here.

> **Assign the LOWEST-NUMBERED class in §2n.1's table that the grading record supports.**
> `1` is most disqualifying, `8` least. **A verdict carries exactly ONE class**; where more
> than one cause is present, the grading record narrates the rest **in prose** and the
> column still carries one.

**THE ORDER IS NOT INVENTED — IT IS READ OFF HER OWN DEFINITIONS.** `PHYSICS-FAIL` is
defined by her as *"**proven instrument**, band genuinely missed"*, and `INSTRUMENT` as
*"comparator/reader/guard defect; **physics unjudged**"*. **A row cannot be a physics
failure while its instrument is unproven — her two definitions are already mutually
exclusive in that direction.** The precedence generalises that one relation to all eight:
**you may not claim a physics cause until every referee cause is excluded.** That is
exactly *"referee trouble never again wears a physics costume."*

**THE RATIONALE FOR EACH STEP DOWN, stated so it can be overruled rather than rediscovered:**

- **`BUDGET/KILL` first** — the run did not finish, so **no answer was produced to be wrong**.
- **`NAMING/PLUMBING` second** — a path/id/collision defect puts **the identity of the graded
  object in doubt**; you may have measured the wrong artifact correctly.
- **`BOOKKEEPING` third** — the answer exists and the record cannot carry it, so the verdict
  is about the stamp, not the solve. Her own gloss: *"solve fine, stamp impossible."*
- **`INSTRUMENT` fourth** — her words are decisive: **physics unjudged**. No number arrived.
- **`GATE-DESIGN` fifth, BELOW `INSTRUMENT`, and this is the one genuinely close call.** With
  a blind reader you never obtained the number the gate would have judged, so **you cannot
  demonstrate on data that the gate was ungradeable** — the instrument defect is the nearer
  cause. **Recorded as a ruling with its reasoning exposed, because it is arguable.**
- **`REFERENT-CEILING` sixth** — *"result fine"* by her own definition; the limit is external.
- **`MODEL-LIMIT` seventh, ABOVE `PHYSICS-FAIL` — and this placement is load-bearing.** A
  known, literature-documented model-class miss must **never** be reported as the lab's
  solver being wrong about reality. It is an **expected failure, correctly measured**, and
  ranking it above `PHYSICS-FAIL` is what stops the lab flattering itself in the other
  direction — by claiming a genuine discovery where the textbook already said so.
- **`PHYSICS-FAIL` last** — reachable **only** when everything else is excluded, which is
  what makes it worth something when it is claimed.

**VALIDATION, RUN BEFORE THIS ORDER WAS ADOPTED: all eight of her own anchors were graded
under it, and every one lands in the class she put it in.** Dam break → 8; SST hump →
7; T18/T16 → 6; τ_w identity and F28's no-floor → 5; banner-match and blind readers → 4;
arm O and K0d → 3; SO3aR's run dir → 2; JF1's pending → 1. **An order that moved any of her
anchors would have been wrong by construction, and this one moves none.**

### §2n.4 `UNCLASSED` IS FAIL-CLOSED, AND IT IS NOT A NINTH CLASS

> A non-`PASS` row whose grading record does not support any class is **`UNCLASSED`**.
> **`UNCLASSED` is the ABSENCE of a class, never a value of it**, and it reads with the
> force of the **most** disqualifying class: an `UNCLASSED` row **may not be counted toward
> any capability claim** (§2n.6) and **may not be reported in the physics-adverse half of a
> headline** (§2n.5).

**Why this direction.** The alternative — treating an unclassed row as harmless until
someone objects — is the fail-open this team audits for a living. **A row nobody has
explained is not evidence that nothing is wrong with it.** An `UNCLASSED` count is
therefore **published, not hidden**, and a rising one is a finding about the lab's records.

### §2n.5 THE HEADLINE SPLIT

Her rule, unaltered: every report headline carries
**`N physics-adverse (list) / M non-physics (by class)`**.

- **physics-adverse** = classes **7 `MODEL-LIMIT`** and **8 `PHYSICS-FAIL`** only, listed individually.
- **non-physics** = classes **1–6**, broken out **by class** rather than totalled.
- **`UNCLASSED` is reported as its own third figure** and is **never** silently folded into
  either half. Folding it into "non-physics" would assert something nobody has established.

### §2n.6 THE STANDING CAPABILITY DEFINITION

Her rule, so the question never needs asking again:

> **"Can the lab run and post-process X?"** is answered **`YES`** exactly when X has a row
> at **`SURVEYED`-or-better** whose cause classes **exclude `INSTRUMENT`, `BOOKKEEPING` and
> `NAMING/PLUMBING`** (classes 4, 3 and 2). **Everything else is referee trouble**, and
> referee trouble is never reported as a physics limitation.

**Three notes this team adds, none of which narrows her rule:**

1. **`UNCLASSED` rows do not answer `YES`** (§2n.4). An unexplained row cannot demonstrate a capability.
2. **`BUDGET/KILL` (1) and `GATE-DESIGN` (5) are NOT in her exclusion list**, and this
   amendment **does not add them**. Her list is exactly three and it is hers to widen.
   **Recorded as an observation, not a change:** a `GATE-DESIGN` row arguably also fails to
   demonstrate a capability. **Referred to her; not acted on.**
3. This definition **merges into the capability and coverage documents** as a dated
   amendment citing `4116024a`, per her bullet 3 — it is not confined to this charter.

### §2n.7 BACKFILL — CHEAP, NO RE-RUNS, AND IT MAY NOT INVENT

Her rule: *"backfilled from existing records — cheap, no re-runs."*

- **Each team backfills its OWN rows.** Verification designs the column and audits it; it
  does not class another team's verdicts, exactly as it does not delete another team's rows.
- **No solve is re-run for a backfill, ever.** A class that would require new compute to
  establish is a class the record does not support — so the row is **`UNCLASSED`** (§2n.4).
- **⚠ THE BACKFILL'S OWN FAILURE MODE, NAMED IN ADVANCE:** the pressure on a backfilling
  supervisor is to reach for the class that **reads best** for their team, from memory,
  because the row is old and the record is thin. **§2n.2 is what forbids it:** the class
  needs a citation resolving at `HEAD`. **A backfill that produces zero `UNCLASSED` rows
  across a large register should be disbelieved and audited** — this team will audit it —
  because it is far likelier that recollection filled the gaps than that every historical
  record happened to name its cause.

### §2n.8 WHAT THIS AMENDMENT DOES NOT DO

**It does not touch the verdict vocabulary** (§2): a cause class is an **attribute of a
non-`PASS` verdict**, never a verdict, never a softener, and it **cannot convert one verdict
into another**. **It does not weaken rule 5** — a row whose triple is not `CONVERGING` is
`NOT A RESULT` whatever its class. **It does not re-grade anything:** no row's verdict moves
because a class was added to it. **And it creates no `PASS`** — a `PASS` carries no cause
class at all, because there is nothing to explain.

| field | value |
| --- | --- |
| authority | **Sanaa, `4116024a`, verbatim, read at source** |
| clause added | **§2n** (`§2n.1`–`§2n.8`) |
| classes | **8, closed set, her text** · precedence **ruled** (`§2n.3`) · `UNCLASSED` **fail-closed** (`§2n.4`) |
| anchors reproduced | **8 of 8** — the order moves none of her examples |
| verdict vocabulary changed | **0** · gates | **0** · bands | **0** · caps | **0** · re-grades | **0** |
| new duty created | **3** — class every non-`PASS`; headline split; backfill own rows |
| referred to Sanaa | whether `GATE-DESIGN` (and `BUDGET/KILL`) join her three capability exclusions |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.30, 2026-08-31 — **§2n.9–§2n.13: THE CAUSE CLASS MEETS THE REAL FILES, AND THREE OF ITS FOUR MECHANICS HAD TO CHANGE. A COLUMN CANNOT BE ADDED TO AN APPEND-ONLY REGISTER, AND `SURVEYED-OR-BETTER` PRESUPPOSED AN ORDERING NOBODY HAD WRITTEN DOWN**

**Lines whose number changed above this section: 0.**

**v1.29 designed §2n against Sanaa's order. This amendment is what a survey of the actual
files did to that design** — four findings, three of which forced a mechanic to change.
**Recorded as a correction to my own amendment of ninety minutes ago**, because the
alternative is a rule that cannot be executed against the files it names.

### §2n.9 ⚠ `SURVEYED-OR-BETTER` PRESUPPOSED A TIER ORDERING THAT IS WRITTEN DOWN NOWHERE

**MEASURED:** the five tiers — `HOLDS` / `GATE REACHED` / `SURVEYED` / `NOT HELD` /
`NEVER RUN` — are defined at `docs/COVERAGE_MATRIX.md:50-58` and operatively re-stated at
`:200-209`, **and no file in this repository states an ORDINAL RANKING of them.** Sanaa's
standing definition (§2n.6) says *"`SURVEYED`-or-better"*, which **cannot be evaluated
without one.** A `grep` for a tier ordering across `docs/` returns only two teams' own
`GRADING_CHAIN.md` files quoting her phrase back.

**This is a gap, not a formatting problem, and her bullet 1 says to call it what it is.**

> **RULING `[lab-attributed]`, and overrulable by her:** the ordering is
> **`HOLDS` > `GATE REACHED` > `SURVEYED` > { `NOT HELD` , `NEVER RUN` }**, and therefore
> **`SURVEYED`-or-better = { `SURVEYED` , `GATE REACHED` , `HOLDS` }.**

**THE GROUND, so this is derived rather than asserted.** Ruling 1's final form
(`:200-209`) assigns the top three by **counting green V/G/P columns** — `HOLDS` 3,
`GATE REACHED` 1–2, `SURVEYED` 0 — so those three are **already totally ordered by a
monotone quantity in the matrix's own rubric**. The remaining two are assigned by a
**different predicate** and neither can be "better" than `SURVEYED`: `NOT HELD` is *"an
honest FAIL, or a blocker"* — a gate that **returned FAIL** — and `NEVER RUN` is *"no
solver has run in this class"*. **A row that failed and a row that never ran cannot
outrank a row carrying breadth evidence**, so both sit below, and this ruling does not
order them against each other because nothing turns on it.

**⚠ THE STANDING I AM CLAIMING FOR THIS, STATED HONESTLY:** `docs/COVERAGE_MATRIX.md:26-41`
discloses that the rubric and the five tier words are **the CHIEF'S reconstruction** and
that ***"Sanaa has not ruled on the rubric."*** So this ordering is `[lab-attributed]`,
made because her definition is **inoperative without it**, and it is the first thing to
fall if she rules otherwise.

### §2n.10 ⚠ THE REGISTER CANNOT TAKE A COLUMN — AND IT HAS ALREADY SOLVED THIS ONCE

**MEASURED, and it defeats v1.29's wording.** `ANSYS_VALIDATION_REGISTER.md:5-7` is
explicit: ***"a row is never edited after it lands; a correction or a re-run is a new row
citing the old one."*** The register's main table (`:22`) carries **13 columns and 51
landed rows, 41 of them non-`PASS`**. **Adding a 14th column edits every one of those 51
rows** — forbidden by the register's own law and by standing rule 6.

**Sanaa's order says the register "gets a cause-class column". Her SUBSTANCE is that the
register must carry the classification; "column" is the shape she reached for, and the
shape is the one thing the file forbids.** Serving the substance and breaking the file
would be obeying an instruction rather than answering it (rule 9).

> **RULING: the cause class lands as an APPENDED, DATED COMPANION BLOCK keyed by row id,
> never as a column edit.** Schema, fixed:
> `| row | case | verdict (rule 1, unchanged) | CAUSE CLASS | citation resolving at HEAD |`

**THIS IS PRECEDENT, NOT INVENTION, AND I VERIFIED IT PERSONALLY AT SOURCE.** The register
has **already added an entire new classification dimension to landed rows this way**: the
**tier** addendum at `:185-196` carries exactly this shape —
`| row | case | verdict (rule 1, unchanged) | tier | the reason, as ruled |` — with four
rows whose `#1`–`#4` are **references into the main table, not new rows**. Its own scoping
line names the tier vocabulary, and its rows are marked *"the
`ansys-verification-supervisor`'s rulings, recorded as such and **overrulable**."* **The
file solved this problem once already and the cause class simply uses the same door.**

**Two consequences, both deliberate.** The companion block's row ids are **references**, so
they are **never double-counted** in any census. And a later re-classification is **a new
dated block citing the old**, exactly as a re-run is a new row — **never an edit**.

### §2n.11 THE MATRIX HAS NO SHARED ROW SCHEMA TO ADD A COLUMN TO EITHER

**MEASURED:** `docs/COVERAGE_MATRIX.md` is the matrix (`docs/LAB_STATE.md:144,175` name it
as verification's §1 product), its authoritative count is **153 rows** (`:965`, census at
`:967-974` — dafoam 58 / closure 6 / heat-transfer 37 / cfd 48 / ansys 4), **and those 153
rows are not enumerated in it.** `:828` says so: *"Full table in the audit record."* They
live in **five family files with five different table shapes** — compare §3.3's 6-column
closure header against §3.6's 5-column ansys header.

> **RULING: each family appends its own cause-class block to its OWN contribution file, in
> the SINGLE schema of §2n.10**, and `COVERAGE_MATRIX.md` carries **the census only** — a
> per-class, per-family count plus the `UNCLASSED` figure. The five contribution files are
> `cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md`,
> `cases/dafoam/MATRIX_CONTRIBUTION.md`,
> `docs/campaigns/T-family/MATRIX_CONTRIBUTION.md`,
> `verification/campaign/MATRIX_CONTRIBUTION.md` (cfd's, filed there because cfd has no
> single case root) and `docs/ansys_verification/COVERAGE_ROWS.md`.

**A matrix tier is not a verdict** (`COVERAGE_MATRIX.md:60-79`; `LAB_STATE.md:165-171`),
so **a cause class attaches to the row's VERDICT, never to its tier.** A row with a tier
and no verdict takes **no** class — and is not thereby capable (§2n.4).

### §2n.12 `docs/CAPABILITY_GRID.md` IS GENERATED — A HAND EDIT THERE IS OVERWRITTEN

**MEASURED:** `docs/CAPABILITY_GRID.md:1` states it is *"assembled from the family tables
at HEAD"*, `:3` names `scripts/assemble_capability_grid.py`. **Text merged into it by hand
is destroyed on the next assembly** — a silent loss, and exactly the dead-lever shape this
team audits.

**And a second measured surprise: `SURVEYED` IS NOT IN THE CAPABILITY GRID'S VOCABULARY AT
ALL.** The grid runs on **Sanaa's own three words** — `CAN DO` / `CAN DO, CAVEATS` /
`CAN NOT DO` (`docs/CAPABILITY_GRID.md:5`). `SURVEYED` occurs there **zero times**; it is a
**matrix** tier. **So her standing definition answers a CAPABILITY question in MATRIX
vocabulary**, and the two documents do not share a word.

> **RULING: the standing definition's home is `docs/COVERAGE_MATRIX.md`** — the file that
> **defines** `SURVEYED` (`:50-58`) and **holds the rubric** (`:42-58`, the only rubric in
> the lab; `VERIFICATION_CHARTER` has none, checked). The capability grid **cross-references
> it** rather than restating it, and any text that must appear in the assembled grid goes
> **through the family sources or the assembler**, never by hand-editing the output.

### §2n.13 ⚠ A HAZARD IN ANOTHER TEAM'S FILE, FOUND IN PASSING — REPORTED, NOT TOUCHED

**`docs/capability/heat-transfer_GRID.md`: the worktree copy is BEHIND `HEAD` and is NOT a
byte-prefix of it.** HEAD blob 51,081 B; disk 44,728 B; **first divergence at byte 8,944**,
inside the `conduction · laminar (no flow) · 2D` cell, where HEAD carries three
strikethrough corrections and disk carries one.

**Because the divergence is MID-FILE, the strict byte-prefix restoration proof this lab
relies on does not apply** — and **an append to the disk copy followed by a commit would
revert about 6.3 KB of committed heat-transfer corrections.** Anyone amending that file
must build from `git show HEAD:docs/capability/heat-transfer_GRID.md`, **never** the
worktree copy. **Inspected, never reverted** (rule 10); it is heat-transfer's file and
heat-transfer's call.

| field | value |
| --- | --- |
| authority | Sanaa `4116024a` for §2n; **`[lab-attributed]`** for §2n.9's ordering |
| corrects | **v1.29's own mechanics** — "column" was unexecutable against two of its targets |
| clauses added | `§2n.9`–`§2n.13` |
| verdict vocabulary changed | **0** · gates | **0** · caps | **0** · re-grades | **0** · rows edited | **0** |
| referred to Sanaa | the tier **ordering** (§2n.9); the capability-exclusion list (§2n.6 note 2) |
| routed to heat-transfer | the `heat-transfer_GRID.md` worktree divergence (§2n.13) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.31, 2026-08-31 — **[SANAA-RULED] §2n.14–§2n.15: BOTH REFERRALS CLOSE. THE TIER ORDERING IS RATIFIED AND STOPS BEING THIS TEAM'S ASSUMPTION, AND THE CAPABILITY-EXCLUSION LIST BECOMES FOUR**

**Lines whose number changed above this section: 0.**

**Sanaa ruled, 2026-08-31, captured verbatim at `6fcc7fb6`** (`etc/sessions/2026-08-31T2110Z_sanaa_tier_order_gatedesign.md`), **read at source before this was written** (standing rule 9 — no agent message is her consent, including the one that carried this):

> **"Tier order confirmed as assumed; yes, GATE-DESIGN joins the excluded classes."**

**Both of the referrals this team put on her desk tonight are hereby CLOSED.** Neither was decided locally, and that was the right call in both directions — she confirmed one and changed the other.

### §2n.14 THE TIER ORDERING IS RATIFIED — THE TAG LIFTS, THE WORDS DO NOT MOVE

**`§2n.9` and `COVERAGE_MATRIX.md`'s dated section of tonight both ruled the ordering `[lab-attributed]`, and both said in terms that it was *"the first thing to fall if she rules otherwise."* She has ruled that it stands.**

> **`HOLDS` > `GATE REACHED` > `SURVEYED` > { `NOT HELD` , `NEVER RUN` }**, and therefore
> **`SURVEYED`-or-better = { `SURVEYED` , `GATE REACHED` , `HOLDS` }** — **`[SANAA-RULED]`, `6fcc7fb6`.**

**What changes is the AUTHORITY, not the content.** `§2n.9`'s reasoning from Ruling 1's green-column monotonicity is unaltered and remains the ground; what it no longer needs is the caveat that Sanaa had not ruled the rubric. **The clause is NOT edited** (standing rule 6) — `§2n.9` stands on the page with its `[lab-attributed]` tag and its own invitation to be overruled, **and this addendum is the record that the invitation was answered.** A reader meeting `§2n.9` reads its tag through this section.

**Her word *"as assumed"* is doing real work and is recorded as such:** she ratified **the ordering this team had already written down and acted on**, rather than supplying a different one. The gap `§2n.9` named — that no file in the repository ordered the five tiers — **was a real gap in the lab's records, and it is now closed by her ruling rather than by our assumption.**

### §2n.15 THE CAPABILITY-EXCLUSION LIST IS NOW FOUR

`§2n.6` is amended, on her authority:

> **"Can the lab run and post-process X?"** is answered **`YES`** exactly when X has a row at **`SURVEYED`-or-better** whose cause classes exclude **`INSTRUMENT`**, **`BOOKKEEPING`**, **`NAMING/PLUMBING`** and — **new, `6fcc7fb6`** — **`GATE-DESIGN`**. `UNCLASSED` rows continue to answer **no** (`§2n.4`).

**SHE WAS ASKED ABOUT TWO CLASSES AND ADDED ONE, AND THAT DISCRIMINATION IS DELIBERATE.** `§2n.6` note 2 referred **both** `BUDGET/KILL` (class 1) and `GATE-DESIGN` (class 5). She took `GATE-DESIGN` and left `BUDGET/KILL` where it was. **That is a decision, not an oversight, because the referral named both** — and this team will not re-raise it.

**THE PRINCIPLE HER FOUR-ITEM LIST MAKES EXACT, stated because it is now derivable rather than assumed.** Every one of the four excluded classes is a defect in **the lab's own refereeing apparatus** — a blind reader (`INSTRUMENT`), a record that cannot stamp (`BOOKKEEPING`), a path or id collision (`NAMING/PLUMBING`), a gate defective as registered (`GATE-DESIGN`). **`BUDGET/KILL` is not:** a cap hit or a box death is **external**, and a row that nonetheless reached `SURVEYED`-or-better **did demonstrate that the lab can run and post-process X** before the meter stopped it. **Her list is exactly the set of ways the lab's own instruments can be at fault**, which is precisely *"referee trouble never again wears a physics costume."*

**Consequence, for the record:** the excluded set is now classes **2, 3, 4 and 5** — contiguous in `§2n.3`'s precedence order — and the classes that still permit a capability `YES` are **1 `BUDGET/KILL`, 6 `REFERENT-CEILING`, 7 `MODEL-LIMIT`, 8 `PHYSICS-FAIL`**. **`§2n.3`'s precedence order is untouched:** `GATE-DESIGN` remains class 5 for assignment; only its capability effect changed.

### §2n.16 THIS WIDENING COSTS NO RE-WORK, AND THE REASON IS TIMING — SAID SO IT IS NOT MISTAKEN FOR DESIGN

**Narrowing a capability definition would normally raise a retroactivity question:** a claim published under the three-item list might not survive the four-item one. **It does not arise here, and the reason is luck of sequencing rather than foresight.** The census published tonight is **153 rows, 0 classed, `UNCLASSED` 153** — **no capability `YES` has yet been asserted under the three-item list by anyone**, so there is nothing to re-evaluate and no row's answer moves.

**Had the backfill run first, this widening would have required re-reading every `YES`.** Recorded so a future widening is understood to be expensive by default.

**And nothing here re-grades:** no verdict moves, no tier moves, no gate, band, cap or label moves. A cause class remains an **attribute** of a non-`PASS` verdict.

| field | value |
| --- | --- |
| authority | **Sanaa, `6fcc7fb6`, verbatim, read at source** |
| referrals closed | **2 of 2** — tier ordering (ratified); exclusion list (widened) |
| `§2n.9` | **tag lifts to `[SANAA-RULED]`; words unchanged; clause NOT edited** (rule 6) |
| `§2n.6` | exclusion list **3 → 4**, adding `GATE-DESIGN` |
| `BUDGET/KILL` | **referred and NOT added — her deliberate discrimination; not re-raised** |
| precedence order | **unchanged** — `GATE-DESIGN` is still class 5 |
| verdict vocabulary | **0** · gates **0** · bands **0** · caps **0** · re-grades **0** · rows edited **0** |
| rows requiring re-evaluation | **0** — census is 0 classed / 153 `UNCLASSED` (`§2n.16`) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.32, 2026-08-31 — **§2d.2: RULE 2 GOVERNS AND MY OWN §2d IS THE OUTLIER — GATES CLOSE AT FIRST COMPUTE, NOT AT THE FIRST GRADED SOLVE. Plus §2n.17, a backfill trap another team measured, and a referral I will not spawn as a rule**

**Lines whose number changed above this section: 0.**

### §2d.2 THE RULING F28's A1.8 REFERRED, AND IT GOES AGAINST THIS CHARTER'S OWN WORDING

**THE TENSION, STATED FAIRLY.** `CLAUDE.md` rule 2 closes gates ***"after first compute."*** **My `§2d` closes them at ***"the first graded solve."*** F28 has **feasibility compute** (`verification/runs/F28_runs/FEAS_*`) and **zero graded solves**, so the two texts give opposite answers, and the registration's own **A1.8 referred exactly this and left it UNRULED**.

> **RULING: `CLAUDE.md` RULE 2 GOVERNS. Gates close at the FIRST COMPUTE under the registration — feasibility compute included — and `§2d`'s narrower wording is a DEFECT IN THIS CHARTER, corrected here prospectively.**

**THE GROUND, AND IT IS THIS CHARTER'S OWN §2g.** v1.16 holds that **a pre-registration cannot EXCEPT a standing rule.** The identical logic binds *a fortiori* on **me**: `CLAUDE.md` is Sanaa's and this charter is mine, so **a charter clause cannot except a standing rule either.** `§2d`'s *"first graded solve"* is **strictly narrower** than rule 2's *"first compute"* — it would hold gates open through compute that rule 2 has already closed them after. **A narrower charter clause does not get to shrink a standing rule; it gets corrected.**

**AND THIS CHARTER ALREADY AGREES WITH RULE 2 ELSEWHERE — §2d IS THE ODD ONE OUT.** `§2i` (v1.18) states that **the freeze BITES WHEN COMPUTE BEGINS** and fixes the stamp as **the EARLIEST `started_utc` under the registration**, with no graded-solve qualifier anywhere in it. **So the conflict was never between me and Sanaa; it was between §2d and §2i, and §2i is the one that is right.**

**§2m DOES NOT RESCUE F28, and I checked rather than assumed.** v1.26's `[SANAA-DIRECT]` `§2m` holds that **a FEASIBILITY RUNG has no gate to freeze, so rule 2 never reached it.** Its object is a rung **with no gate at all**. F28 **has** a gate, and feasibility compute **under a gated registration** is compute under that registration. **§2m is about the absence of a gate, not the character of the run.**

**THE CONSEQUENCE FOR F28, AND THE OUTCOME SURVIVES.** The gates closed at the **earliest `started_utc` of the feasibility runs**, so **the pre-compute amendment limb did NOT apply and the lane's stated ground was wrong.** But **the lane checked all four `§2d.1` repair conditions anyway** — and those are the **post-compute** limb. **The amendment is therefore LEGAL, on the exception rather than on the limb it invoked: the result stands and only its ground moves.** **The lane's belt-and-braces caution is the only reason there is anything to save, and it is commended rather than merely noted** — a lane that satisfies the stricter test it does not believe it needs is the reason a supervisor's ruling can go against it without destroying its work.

**PROSPECTIVE ONLY** (`§2h.6`, v1.19, non-retroactivity): no verdict already earned is disturbed, and no registration is retroactively in breach for having relied on `§2d`'s wording while it stood.

### §2n.17 ⚠ A BACKFILL TRAP, MEASURED BY heat-transfer BEFORE ANYONE HIT IT

**Folded into `§2n`'s backfill mechanics so every team inherits the warning.** Measured by a heat-transfer backfill lane, **`98d8733a`**:

> **The obvious vocabulary tidy — "correct every bare `FAIL` string to `GATE FAIL` in the run trees" — would SILENTLY DISARM 74 REGISTERED CONTROLS ACROSS THREE RUNGS.** `.controls[].must = "FAIL"` is **a registered statement that a control MUST RETURN `FAIL`** — an assertion, **not a verdict cell**. Flipping it does not tidy a label; **it disarms the control.**
>
> **THE SAFE MEASURE IS `graded_rows[].verdict` ONLY.** A backfill or a vocabulary sweep touches **verdict cells** and **never** a control's `must` field.

**This is `CLAUDE.md` rule 3's failure mode wearing a tidy-up's clothes** — a guard silently switched off by a change that looks like housekeeping — and it is the same class as `§2n.7`'s named backfill hazard, arriving from a direction `§2n.7` did not anticipate. **The lane also bounded the reported never-graded defect to two of three K0c rungs by sweeping the third and finding it clean**, which is the right shape: a defect is bounded by measurement, not by assumption.

### §2n.18 REFERRED TO SANAA, NOT SPAWNED — CHECK 1 IS NECESSARY AND NOT SUFFICIENT

**Tonight two independent supervisors performed full, personal, non-delegable check-1 reads of `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py` and BOTH certified a guard that cannot fail.** `read_fvoptions_source`'s first-match regex hits a **banner comment** and reports `volumeMode specific` **even when the live entry says `absolute` and even when it is deleted entirely** — measured by driving it, and recorded at `verification/credibility/CHECK1_ANALYSE_F28_VERIFICATION.md`. **cfd found it by RUNNING the file. Neither of us found it by reading it.**

> **CANDIDATE STANDING RULE, referred and NOT enacted:** *a measurement script's guards are not believed until they have been **exercised** against the artifacts they guard — driven to their refusal by a mutation, as `CLAUDE.md` rule 3 already requires of a reader. A supervisor's read is necessary and not sufficient.*

**It is NOT spawned as a rule here.** Rules spawn only with Sanaa's approval under the 14-day freeze, and **this team does not get to except that because the finding is embarrassing to it.** Recorded, referred, and left for her.

| field | value |
| --- | --- |
| clause added | `§2d.2`, `§2n.17`, `§2n.18` |
| ruled | **rule 2 governs**; `§2d`'s *"first graded solve"* is corrected to **first compute** |
| conflict resolved | `§2d` vs `§2i` — **`§2i` was already right** |
| F28 | amendment **LEGAL on `§2d.1`'s post-compute exception**, not on the limb it invoked; **outcome stands, ground moves** |
| retrospective effect | **none** — prospective only (`§2h.6`) |
| verdict vocabulary | **0** · gates **0** · bands **0** · caps **0** · re-grades **0** |
| referred to Sanaa | the exercise-the-guard rule (`§2n.18`) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.33, 2026-08-31 — **§2n.18 EVIDENCE UPDATE: THE REFERRAL NOW STANDS ON THREE SPECIMENS AND ALL THREE ARE THIS SUPERVISOR**

**Lines whose number changed above this section: 0.** **No rule is spawned here.** `§2n.18` remains a **referral** on Sanaa's desk; this records only that its evidentiary basis grew, and it grew against this team.

**`§2n.18` was referred an hour ago on one specimen: two supervisors certifying a `volumeMode` guard that cannot fail. It now stands on THREE, and I am the author of all three.**

1. **I certified the guard as working** in the check-1 record at `3fb0d0a3` — a full, personal, 763-line read. **Falsified by cfd, who ran it.**
2. **I then explained the sibling guards' survival by a mechanism I had not executed** — *"saved by a backtick."* **Measured false:** a backticked verbatim quote blinds these guards exactly as well as an unbackticked one, and the comment that blinds `volumeMode` **is itself backticked**. **Falsified by cfd, who ran it.**
3. **The conclusion in (2) — "right by luck, not by design" — was nonetheless correct**, which is the most instructive failure of the three: **a right answer resting on a wrong mechanism reads as knowledge and is not.** A record carrying it teaches the next reader to defend against the wrong thing.

**THE COMMON SPECIES, AND IT IS NOT CARELESSNESS:** each time I reasoned about a regular expression **from its shape** rather than **executing it against the bytes it runs on**. That is the same defect this charter names elsewhere in other teams' work — `§2k` (a derived quantity relayed as an observation) and `CLAUDE.md` rule 3 (a zero from a reader not shown able to see a non-zero) — **arriving in this team's own reasoning about code rather than in its numbers.**

**THE CORRECTED RULE THIS TEAM NOW CARRIES IN ITS OWN PRACTICE, pending her ruling:** a guard's behaviour is **measured**, never inferred from its source; and the measurement is a **mutation driven to refusal**, not a reading. **Until she rules, this binds this supervisor's own reviews as practice, and is asserted against no other team.**

**cfd's structural fix is endorsed and is `§2l` in practice** — strip comments before parsing, refuse on multiplicity, refuse on absence, with a planted verbatim-quoting-comment limb: it **removes the possibility** across all three guards rather than patching the one that fired.

| field | value |
| --- | --- |
| rules spawned | **0** — `§2n.18` stays a referral (freeze; rules are Sanaa's) |
| specimens supporting `§2n.18` | **1 → 3**, all authored by this supervisor |
| verdict vocabulary | **0** · gates **0** · bands **0** · caps **0** · re-grades **0** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.34, 2026-08-31 — **§2n.17 IS NARROWED ON heat-transfer's RE-MEASUREMENT — I MISCHARACTERISED THE HAZARD AND THE 74 — AND THEIR METHOD FINDING FALSIFIES §2n.2's OWN CITATION FORM**

**Lines whose number changed above this section: 0.** Raised by **heat-transfer**, `fd4fac0d`. **Every figure below was re-derived here before acceptance, not relayed** — and all of theirs reproduce exactly.

### §2n.17a THE HAZARD IS NOT WHAT I SAID IT WAS

**v1.32's `§2n.17` framed the danger as inherent to the vocabulary tidy itself. That is wrong, and the correction is more useful than the warning was.**

**MEASURED HERE, reproducing their result:** `scripts/check_verdict_cells.py` — D-5's own instrument — **globs `*.md` and nothing else.** Its single corpus statement is at **`:270`**, `for p in sorted(CAMPAIGN.glob("*.md")):`, and the string `gate_*.json` occurs in that file **zero times**. **A correctly scoped D-5 sweep therefore touches ZERO of the 91 bare-`FAIL` strings in the run trees — 74 : 0 within its actual corpus.**

> **THE HAZARD RESTATED:** it is **not** that D-5 work is dangerous. It is **a sweep written from the PHRASE — *"correct every bare `FAIL`"* — rather than from THE INSTRUMENT'S OWN CORPUS DEFINITION.** The phrase has no scope; the instrument does. **Scope a sweep from the code that reads the files, never from the sentence that commissioned it.**

### §2n.17b AND THE 74 IS NOT 74 OF ONE THING

**My clause called all 74 `.controls[].must` assertions. Measured, they are two populations:**

| key | count | what it is |
| --- | --- | --- |
| `required` 20 + `must` 18 | **38** | **literal expectations** — a registered statement that a control MUST RETURN `FAIL` |
| `regraded_verdict` 20 + `base_verdict` 16 | **36** | **recorded observations** — what a run actually returned |
| **74** | | **the damage figure, and it stands** |
| `verdict` 8 · `criterion_*` 7 · `*_row_verdict` 2 | 17 | the balance to **91** total |

**Both populations are corrupted by a blind edit — an expectation flipped is a disarmed control, an observation flipped is a falsified record — so 74 remains the damage figure and only its DESCRIPTION changes.** But the two are different injuries and a repair that understands only one of them will be written wrong. **The sweep would have disarmed or falsified 74 to correct the 8 bare `verdict` strings that D-5's instrument never reads anyway.**

**The safe measure is unchanged: `graded_rows[].verdict` only.**

### §2n.17c ⚠ THEIR METHOD FINDING FALSIFIES `§2n.2`'s OWN CITATION FORM — AND `§2n.2` IS MINE

heat-transfer report that **four of five pointers in the earlier list had ROTTED**, and that a mechanical actor following them **would have edited three innocent lines and missed three real ones.**

**That lands on this team, not on them.** `§2n.2` (v1.29) specified a cause-class citation as *"a path with a line number, or a commit sha."* **A bare line number into a shared, concurrently-appended board is exactly the pointer class they measured rotting at 4-in-5** — and `§2n.2` is the clause that will be executed 153 times during the backfill. **I specified a resolver that decays under the very concurrency this lab runs on.**

> **`§2n.2` IS AMENDED.** A cause-class citation resolves by **(a) the record's SECTION heading and (b) QUOTED TEXT from the assigning sentence** — with a **commit sha** where one exists. **A line number may accompany a citation as a convenience and is NEVER the thing that resolves it.** A citation that resolves only by line number **is not a citation** for `§2n.2`'s purposes.

**This is `§2l` again — remove the possibility, not the instance.** Re-pointing the rotted four would have fixed four pointers; changing the citation form removes the rot.

**And it is the third time tonight this team's own text has been corrected by a team measuring something I asserted** — cfd twice on `analyse_f28.py`, heat-transfer here. **Recorded in that spirit: the audit mandate is working in the direction that costs this team, which is the only direction that proves it works.**

| field | value |
| --- | --- |
| authority | **heat-transfer, `fd4fac0d`** — re-derived here, reproduces exactly |
| `§2n.17` | hazard **narrowed**: not D-5 work, but a sweep scoped from a PHRASE not a CORPUS |
| the 74 | re-characterised: **38 expectations + 36 observations**; damage figure **unchanged at 74** of **91** |
| `§2n.2` | citation form **amended** — section + quoted text (+ sha); **line numbers never resolve** |
| verdict vocabulary | **0** · gates **0** · bands **0** · caps **0** · re-grades **0** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.35, 2026-08-31 — **§2n.19: OVER-CORRECTION IS A RECORD DEFECT. THIS TEAM WITHDREW A TRUE SENTENCE AGAINST DATA IT HAD ALREADY GENERATED**

**Lines whose number changed above this section: 0.** **No rule is spawned; `§2n.18` remains a referral.** This records a **fourth specimen of a different species**, because the first three pointed one way and this one points the other.

**MEASURED (three-way positional test, F28 repair lane, re-run here):** a backtick before the **KEYWORD** blocks nothing — `` `cellZone disk;` `` yields `disk`; a backtick before the **VALUE** — `cellZone` ⏎ `` `disk`. `` — **blocks**. **Both earlier accounts were right about different positions.** This team's *original* sentence named the **value** position and was **true**; only the generalisation *"backticks block"* was false.

**AND THIS TEAM STRUCK THE TRUE SENTENCE ANYWAY.** The test executed immediately before that withdrawal printed the exonerating line. **The data was on the screen and the sentence was withdrawn regardless.**

> **`§2n.19` — OVER-CORRECTION IS A RECORD DEFECT AND IS AUDITED LIKE ANY OTHER.** Withdrawing a true statement damages a record exactly as asserting a false one does, **and is harder to catch, because a concession reads as humility and nobody audits it.** When a peer's counter-example arrives, the question is **"does it address MY sentence, or a GENERALISATION of it?"** — and it is answered **against data**, before the concession, never after.

**`§2n.18` is not weakened; it is completed.** Exercising the instrument is necessary when making a claim **and equally when accepting a correction** — **a concession is a claim about your own record.**

**The honest tally for tonight, since this team has been auditing everyone else's:** four errors by this supervisor on one 40-line function — **three from reasoning about code instead of running it, one from conceding against evidence it had already produced.** Peers caught all four. **That is the cross-team mandate working, and the count is recorded rather than rounded.**

| field | value |
| --- | --- |
| rules spawned | **0** — `§2n.18` stays a referral (freeze; rules are Sanaa's) |
| clause added | `§2n.19` — over-correction is a record defect |
| restored | the value-position sentence in `verification/credibility/CHECK1_ANALYSE_F28_VERIFICATION.md` |
| still struck | only the generalisation *"backticks block"* |
| verdict vocabulary | **0** · gates **0** · caps **0** · re-grades **0** — F28 verdict unchanged |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.36, 2026-08-31 — **§2d.3: T20's §2d.1 REFERRAL IS GRANTED. AND THE INTERESTING PART IS CONDITIONS (3) AND (4), WHICH PRESUPPOSE PUBLISHED NUMBERS THAT DO NOT EXIST HERE — SO THE RULING NARROWS THEM RATHER THAN WAIVING THEM**

**Lines whose number changed above this section: 0.** heat-transfer's referral, `3efb92b8`. **Every fact below was MEASURED by me, not relayed** — the referral's framing was checked, not accepted (`§2n.19`).

### §2d.3.1 WHAT I VERIFIED MYSELF, BEFORE RULING ON ANY OF IT

| claim | how I checked it | result |
| --- | --- | --- |
| gates closed at first compute | `log.solve` present under `T20_runs/` | **six `T20_LC_*` cases ran — TRUE**, so `§2d.2` applies and the **pre-compute limb does NOT** |
| `q_volumetric` is rung-global | parsed `T20_registered.json` | **`physics.q_volumetric = 5000.0`** — a single value |
| the case schema cannot carry it | enumerated the per-case keys | **19 keys, none is `q_volumetric`**; `any case carries it? **False**` |
| no `T20_LC_P10` exists | disk **and** `HEAD` | **zero hits on both** |
| the repair is committed and unauthorised | `git ls-tree HEAD` | `build_t20c.py` **tracked**, commit says **NOT YET AUTHORISED TO RUN** |
| condition (2)'s instrument is real | **I RAN IT** | `mutation_controls_t20c.py` → **12 controls, 0 misbehaved, rc 0** |

**The inexpressibility claim is therefore TRUE AND MEASURED, not argued:** a per-case planted `q` cannot be stated through the registered interface, because the registration puts `q_volumetric` in `physics` and the per-case schema has no slot for it. **The V5 planted arm is unbuildable as registered** — and under `§2j` an instrument that cannot answer rule 3's question **does not grade**. So without the repair, **T20's V5 arm is a dead lever by construction, not by neglect.**

### §2d.3.2 THE FOUR CONDITIONS, RULED

1. **DEMONSTRABLE ERROR, NOT A PREFERENCE — HOLDS.** A *registered* control that **cannot be built through the registered interface** is a defect, and it is demonstrated by the schema itself rather than by anyone's judgement of it.
2. **INDEPENDENT INSTRUMENT THAT GRADES NOTHING — HOLDS, AND THIS IS THE LOAD-BEARING ONE.** `mutation_controls_t20c.py` is a **mutation harness**: it plants defects and requires limbs to go red. **It grades nothing and cannot know which direction a verdict wants**, which is exactly the property `§2d.1` is cut around. **I drove it rather than trusting its commit message: 12 of 12, 0 misbehaved.**
3. **DISCLOSE, NAME THE INSTRUMENT, QUANTIFY WHAT MOVED — HOLDS, at ZERO.** See the narrowing below.
4. **PRE-REPAIR VALUES BESIDE THE PUBLISHED ONES — HOLDS VACUOUSLY.** See the narrowing below.

> **RULED: the `§2d.1` exception is GRANTED for T20's V5 planted arm. `build_t20c.py` is legal.**

### §2d.3.3 ⚠ THE NARROWING, WHICH IS THE REAL CONTENT OF THIS RULING

**Conditions (3) and (4) PRESUPPOSE PUBLISHED NUMBERS.** `§2d.1` was cut for `K0cS`, where a wall integral had been **published and was wrong by 10–27 %**; "quantify what moved" and "record the pre-repair values" both assume values exist. **T20 has NONE — zero graded solves, no `T20_LC_P10`, nothing published.**

**Read carelessly, that makes (3) and (4) free, and "nothing moved" becomes a phrase any team can write.** It is not free:

> **A `§2d.1` repair may satisfy conditions (3) and (4) by DISCLOSING AN ABSENCE — but the absence must be MEASURED AND NAMED, never asserted.** The record states **the count of graded solves under the registration (zero)** and **names the artifacts that do not exist**, resolvably. **This is rule 2's own pre-compute test — *name the run directory that does not exist* — reused, and it is the same evidentiary standard, not a weaker one.**
>
> **AND IT IS AVAILABLE ONLY WHILE THAT COUNT IS ZERO.** The moment one graded solve exists under the registration, **(3) and (4) bite in full** and a repair must quantify what moved and record the pre-repair values. **This clause creates no path for repairing a rung that has produced numbers.**

**T20 meets it:** zero graded solves, `T20_LC_P10` absent on disk and at `HEAD`, both measured above.

### §2d.3.4 CONSISTENT WITH THE F28 PRECEDENT, AND I SAY SO RATHER THAN LET IT BE NOTICED

This is **the same shape I ruled hours ago** for F28's Addendum 3: a defect found by an instrument that grades nothing, **before any graded solve**, a repair that **restores a control's ability to fire**, and **no gate value moving**. **Two teams, two rungs, one rule, the same answer** — which is what a charter is for. **Had I ruled T20 differently I would have been wrong about one of them.**

### §2d.3.5 THE SCOPE OF THIS GRANT, STATED NARROWLY

**I rule the REPAIR LEGAL. I do not authorise COMPUTE.** Whether `T20_LC_P10` launches, under what cap and against what pre-registration, is **heat-transfer's**, subject to rule 2 (its own gate frozen before it runs), rule 12 (costed in its pre-registration) and the completion rule. **A `§2d.1` grant removes a legal obstacle; it is not a budget, not a launch order, and not a verdict.**

**No gate value, band, threshold, cap or label moves anywhere in T20. No row is re-graded.**

| field | value |
| --- | --- |
| referral | heat-transfer, `3efb92b8` — **GRANTED** |
| conditions | **4 of 4 hold**; (2) verified by **driving** the instrument, 12/12, rc 0 |
| narrowing created | (3) and (4) satisfiable by a **measured, named absence** — **only while graded solves = 0** |
| scope | **repair legal; compute NOT authorised** |
| gates **0** · bands **0** · caps **0** · labels **0** · re-grades **0** | |
| **lines whose number changed above this section** | **0** |

## Amendment — v1.37, 2026-09-02 — **§2d.4: T23G2's PETITION — THE FRAMEWORK IS RULED AND IT CUTS AGAINST THE PETITION ON A POINT NOBODY RAISED. §2d.3.3's SHORTCUT IS DENIED, BECAUSE "NO GRADED SOLVE" IS NOT "NO NUMBERS". THE PER-ITEM GRANTS ARE HELD, NOT REFUSED.**

**Lines whose number changed above this section: 0.** heat-transfer's petition, `docs/campaigns/T-family/T23G2_GRADING_PATH_REPAIR_PETITION.md`, §9, six items, **per-item ruling sought and a bundle ruling expressly not sought.** **Zero solver compute; 0 core-min; $0.00.** **This amendment creates, moves and retires NO gate, threshold, band, cap or label, and re-grades nothing.**

### §2d.4.1 WHAT I RULE NOW, AND WHY IT IS NOT THE PART ANYONE ASKED ABOUT

**§2d.3.3's absence-disclosure shortcut is DENIED to T23G2.** This is the load-bearing ruling and **it makes the petition harder, not easier.**

My own `§2d.3.3` — written eighteen hours ago for T20 — permits conditions (3) and (4) to be satisfied by **disclosing a measured absence**, and says in terms: *"AVAILABLE ONLY WHILE THAT COUNT IS ZERO… This clause creates no path for repairing a rung that has produced numbers."*

**T20 had no solves. T23G2 has three.** `[MEASURED: `verification/runs/T-family/T23G2_runs/` EXISTS; the petitioner reports rule-4 completion on all three levels and the chief's routing confirms it.]` **What T23G2 lacks is a VERDICT, not NUMBERS** — and (3) *"quantifies what moved"* and (4) *"pre-repair values recorded beside the published ones"* key on **values**, not on verdicts.

> **RULED — `§2d.4`, and it narrows `§2d.3.3` rather than extending it: the absence-disclosure shortcut keys on the absence of NUMBERS, never on the absence of a VERDICT. A rung whose solves have COMPLETED has numbers, whether or not a comparator has consented to grade them. For such a rung, conditions (3) and (4) BITE IN FULL.**

**This costs heat-transfer nothing but work, and no solver compute.** The fields are on disk; every repair's effect is measurable by **running the comparator over the same data before and after the repair and publishing both**. That is a **stronger** discharge of (3) and (4) than any disclosure of absence, and it is available here precisely because the runs completed. **Requiring it is therefore not an obstacle; it is the better evidence, and it is affordable.**

**Why I rule this against the grain of a petition I am otherwise sympathetic to:** `§2d.3.3` was cut for a rung with nothing on disk, and **read loosely it would let any ungraded rung call itself value-free.** A comparator that refuses to run is then a *qualification* for the shortcut — **the instrument's own failure becoming the ground for relaxing the rule that governs repairing it.** That is circular, and it is the shape `§2d.1`'s closing sentence forbids: *"Nothing a verdict depends on may be repaired on the authority of the verdict it produces."*

### §2d.4.2 THE LOCATION DISCREPANCY — RULED NOW, BECAUSE THE DANGER IS SOMEBODY BEING HELPFUL

The registration's §7 (`:662-663`) registers the comparator at `verification/runs/T-family/T23G2_runs/`; it lives at `docs/campaigns/T-family/analyse_t23g2.py`. **`verification/runs/T-family/T23G2_runs/` EXISTS** `[MEASURED]`, so the registered destination is real and a move is physically trivial — **which is exactly why this needs ruling before someone tidies it.**

> **RULED: THE FILE DOES NOT MOVE. No agent may relocate `analyse_t23g2.py` — not to the registered path, not anywhere — while T23G2 is ungraded.** The discrepancy is disclosed in a dated addendum and **left standing**.

**The reason is rule 2's verification step, not tidiness.** The freeze is verified by *"hashing the frozen file against the committed blob"* at the **registered grading path**. Moving the file post-compute rewrites the very fact the freeze check reads. **A path discrepancy is a disclosed, inert defect; a post-compute move is an undisclosed change to the object of verification, and it destroys the ability to tell the two apart afterwards.** **heat-transfer requested no move and disclosed the discrepancy instead. That was correct and I record it as correct** — the petition's conduct on this point is better than the ruling it asked for.

### §2d.4.3 R2's LEGAL CHARACTER, AND THE RECURSION IN IT THAT THE PETITION DOES NOT NAME

`R2` adds the sha recorder that the frozen registration (`:671`) says the comparator *"will record its own grading-path shas on the artifact's face."* **This is not a DEPARTURE from the registered path; it is a REGISTERED FEATURE THAT WAS NEVER BUILT** — a different legal object, and condition (1)'s *"demonstrable error, not a preference"* is satisfied **by reading the frozen text against the code**, with no judgement call.

**⚠ BUT THE REPAIR CANNOT DELIVER WHAT THE REGISTRATION ASKED FOR, AND THE RECORD MUST SAY SO.** The recorder records **the comparator's own sha** — and **adding the recorder changes that sha.** The registration contemplated provenance present **from the first graded solve**; what `R2` can produce is provenance **from the repair forward**, carrying a **post-repair** sha that is **not** the blob frozen at pre-registration.

> **RULED: `R2` may not be recorded as restoring the registered provenance. If granted, the artifact's face must carry BOTH the post-repair comparator sha AND the pre-registration blob sha, labelled as two different objects, with a line stating that no graded solve was ever produced under a comparator carrying the recorder.** **The registration's intent here is UNRECOVERABLE; only its forward half is available, and calling that "as registered" would be a claim wider than its instrument.**

### §2d.4.4 WHAT IS HELD, AND WHAT HELD MEANS

**R1, R3, R4, R5 and R6 are HELD pending measurement I have commissioned. HELD IS NOT REFUSED, and none of the six is denied.** The direction analysis I will apply is stated now so heat-transfer can prepare rather than wait:

| item | direction if granted | scrutiny |
|---|---|---|
| **R1** `mark_done_t23.py` `CASES` | **PERMISSIVE** — turns a refusal into a gradeable case | **highest.** A shared completion instrument, fail-closed **by design**; the petitioner itself flags blast radius beyond T23G2. **Which other campaigns share it is being measured** |
| **R2** sha recorder | **NON-PERMISSIVE** — adds a record, cannot move a verdict | ruled in character above (§2d.4.3) |
| **R3** `p(Q4)` vs `ORDER_BAND`, folded into rollup | **adds a gate** — can only worsen or hold | check the band is **registered**, not invented |
| **R4** `Q6` reported-only, excluded from rollup | **⚠ PERMISSIVE — the sharpest of the six.** Removing a quantity from a rollup can turn a fail into a pass | **`§2d.1`'s named prohibition is exactly this shape.** And the petitioner **retracted its own `Q6` claim**, having found `:449-451` registers more of `Q6`'s role than `:455` alone — **a retraction that appears to cut AGAINST `R4`. Being verified** |
| **R5** 18 controls for 5; live plant-and-read-back | **NON-PERMISSIVE** — strengthens controls; standing rule 3 | easy on direction; (3)/(4) still bite |
| **R6** absent primary y+ log refuses | **NON-PERMISSIVE** — strictly stricter; closes a fail-open | easy on direction; (3)/(4) still bite |

**AND THE QUESTION THAT MAY MOOT MOST OF THIS, WHICH I PUT FIRST TO MY OWN LANE:** the petitioner discloses that `G-YPLUS` is a **`GATE FAIL`** on `centrebody_up` max y+ and **petitions anyway**. **If T23G2 is `GATE FAIL` regardless of all six repairs, then the repairs decide the quality of the record and not the verdict** — which changes what is at stake in every row above, and is the first thing being re-derived independently.

**Two facts about the petition's conduct, recorded because they bear on its reliability in both directions:** it **retracts part of its own `Q6` claim**, and it **petitions while conceding a `GATE FAIL`.** **Neither buys a grant.** Both are evidence that the petition is not shaped to a wanted answer, and I weigh them as such and no further.

### §2d.4.5 SCOPE, STATED NARROWLY

**I rule FRAMEWORK, not the six items.** No repair is authorised by this amendment; **no edit to `analyse_t23g2.py` or `mark_done_t23.py` is legal on the strength of it.** **No compute is authorised.** **T23G2 remains `PENDING`, grading `BLOCKED`,** and the block is now on **measurement I have commissioned**, not on a decision nobody has taken.

| item | outcome |
|---|---|
| `§2d.3.3` shortcut for T23G2 | **DENIED** — (3) and (4) bite in full; discharge by before/after over existing data, **0 core-min** |
| the narrowing created | the shortcut keys on **absent NUMBERS**, never on an **absent VERDICT** |
| comparator relocation | **FORBIDDEN while ungraded** — no agent may move it |
| `R2` character | **a registered feature never built**, not a departure — **and its registered intent is unrecoverable** |
| `R1`–`R6` grants | **HELD, none refused**; directions published in advance |
| gates · bands · caps · labels · re-grades | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

## Amendment — v1.38, 2026-09-02 — **§2d.5–§2d.8: T23G2's SIX ITEMS RULED — FOUR GRANTED (TWO OF THEM WIDENED BEYOND WHAT WAS ASKED), ONE SPLIT AND HALF-REFUSED, ONE REFUSED AS THE WRONG INSTRUMENT. AND THE RUNG CANNOT PASS ON ANY OF THEM: IT IS `NOT A RESULT` OVER A `GATE FAIL` THE PETITION NEVER MENTIONS.**

**Lines whose number changed above this section: 0.** **Zero solver compute; 0 core-min; $0.00.** **This amendment creates, moves and retires NO gate, threshold, band, cap or label.** It **grades nothing** — grading T23G2 is heat-transfer's act with its own comparator. Every number below was **re-derived by me at source, or measured by a lane and then spot-checked by me at source**; the two the disposition turns on I read myself.

### §2d.5 THE CHARTER RULING, AND IT IS THE ONE WITH REACH BEYOND T23G2

Five of the six items were found **by reading the frozen registration against the code**, and condition (2) demands *"an instrument INDEPENDENT OF THE HYPOTHESIS — one that grades nothing, such as a near-identity, a guard or a control."* All of §2d.1's examples are **executable**. The petition names no instrument, and none exists. **Read literally, five of six fail condition (2) and `§2d` stands on all of them.** That reading would be wrong, and here is why.

**Condition (2)'s stated PURPOSE is at lines 1944-1947**, and it is not about executability: *"An error found by something that grades nothing **cannot have been selected to move a verdict in a wanted direction**, because the thing that found it **does not know which direction that is**."*

**A sha-frozen pre-registration is the paradigm case of that property.** It was written **before the answers existed**, it is **frozen by sha**, it **grades nothing**, and it **cannot know which direction any verdict wants** — that unselectability is *the freeze's entire evidentiary content* (rule 2). It satisfies condition (2)'s purpose **more completely than a near-identity does**, because a near-identity is at least chosen after the fact and a frozen registration cannot be.

> **RULED — `§2d.5`: THE FROZEN PRE-REGISTRATION IS AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS FOR CONDITION (2), WHEN AND ONLY WHEN THE DEFECT IS A DEMONSTRABLE DEPARTURE FROM ITS TEXT — a registered feature absent from the code, a registered gate never implemented, a registered count the code does not meet, a band the registration does not carry. The departure must be exhibited by quotation and by measurement, both.**
>
> **AND IT IS NOT AN INSTRUMENT WHERE THE REGISTRATION IS SILENT. Silence cannot be departed from. An inference from silence is precisely the PREFERENCE that condition (1) excludes, and dressing it as a departure is how condition (2) would be hollowed out.**

**This clause narrows as much as it opens, and I state the narrowing first:** it gives a team **no** route to repair anything the registration did not address, and it makes the **quotation** load-bearing — a citation that does not check out is not a departure, it is an assertion. **The petition's own citation record bears on this:** three of its line references are **materially wrong** and five drift by 1–3 lines `[MEASURED]`. **The substance survived every check; the locations frequently did not.** Under `§2d.5` that is not cosmetic — **the quoted text IS the instrument** — so every grant below is pinned to the **corrected** line, never to the petition's.

### §2d.6 WHEN T23G2's GATES CLOSED — MY OWN V-52 AND §2i.8 GAVE DIFFERENT ANSWERS, AND I RESOLVE IT WITHOUT OVERRULING EITHER

The lane surfaced a live inconsistency I had not seen. **§2i.8** (charter `:3010-3026`): where the mesh is *generated after the freeze*, **meshing IS compute** — which puts first compute at **18:39:59.8Z**, **17 min 40 s BEFORE** the comparator was committed (`976776f4`, 18:57:39Z), so the comparator would have been committed **after gates closed**. **My own V-52** (`25231651`, 19:03:25Z) held the opposite on these very facts: *"the meshes exist and nothing has solved… the FREE pre-compute limb governs"* — putting first compute at the first solver line, **19:07:26Z**, **9 min 47 s AFTER** the comparator froze.

**§2i.8's own condition decides it, and it is not met here.** §2i.8 reaches a post-freeze mesh because it is *"a result-bearing artefact **the registration did not fix**."* **T23G2's registration DID fix it:** §2.1 registers the cell counts **40320 / 90720 / 204120**, `gate_meshsim` **refuses on a mismatch**, and the built meshes match **exactly** `[MEASURED]`. §2i.7's own narrowing (`:2991`) defines a result-bearing artefact as *"a time directory, a written field, or at least one `Time = ` iteration line in a solver log"* — **a `polyMesh` is none of the three.**

> **RULED — `§2d.6`: §2i.8 does not reach T23G2, because its condition — a mesh the registration did not fix — is FALSE here. A mesh fixed by REGISTERED, GATED CELL COUNT is part of the registration in substance even when it is not in the freeze commit in bytes. First compute for T23G2 is the first solver line, 19:07:26Z. V-52 stands, and §2i.8 is neither narrowed nor overruled — it simply has no object here.**

**⚠ AND THIS CHANGES NOTHING ABOUT THE SIX ITEMS, WHICH I SAY BEFORE ANYONE INFERS OTHERWISE.** It establishes that the comparator's **original** commit was clean. **The petitioned repairs are being made TODAY, after all three levels solved — they are post-compute beyond argument, and `§2d.1` governs every one of them.**

### §2d.7 THE SIX ITEMS, RULED SEPARATELY AS ASKED

| item | ruling |
|---|---|
| **R1** completion allow-list | **GRANTED** |
| **R2** sha recorder | **GRANTED AND WIDENED** — a fifth file is required |
| **R3** implement `G-ORDER` | **GRANTED** — and measured inert |
| **R4** `Q6` band + rollup exclusion | **SPLIT: band limb GRANTED AND WIDENED to `Q4`; ROLLUP-EXCLUSION LIMB REFUSED** |
| **R5** 18 controls + live y+ plant | **GRANTED — and it is the most important of the six** |
| **R6** absent y+ log refuses | **REFUSED as a `§2d.1` repair; REFERRED prospectively** |

**R1 — GRANTED.** The only item with a **real, drivable, grading-nothing instrument**: the completion tool's own allow-list guard refuses `T23G2_L1` with **rc 2** before reading a field, against `:539-541` which registers completion as **delegated to that very tool**. Conditions (1) and (2) **MET on the strongest evidence in the petition**. **Blast radius measured and narrower than "shared instrument" implies:** T23 does not call it at runtime (`analyse_t23.py:88` carries its own `CASES`); CASE3 inherits T23's position; **T24 does not use it at all** — its reference is a docstring. **T23G is the only rung whose record diverges, and only in provenance** — its recorded sha is **written, never asserted**, so no re-run breaks. **V-52 already ruled those fossils untouchable and that ruling is undisturbed: the divergence is a detection doing its job and must not be suppressed.** *(Precedent the petition cites neither: `DEAD_LEVER_AUDIT` §27.3/§27.4, `af6af856`, granted this same widening for the three `T23G` names.)*

**R2 — GRANTED, AND WIDENED BEYOND WHAT WAS ASKED.** A registered feature never built (`:671`), with **zero** occurrences of `grading_path`/`shas`/`hash-object`/`hashlib`/`sha256`/`sha1` in 653 lines. Condition (2) **MET under §2d.5**. **⚠ THE SCOPE AS PETITIONED IS INCOMPLETE AND I WILL NOT GRANT IT AS ASKED:** `analyse_t23g2.py:46` imports `t23g_readonly_diagnosis` and uses it in `yplus_from_fields`, `_first_cell_heights`, `gate_meshsim` and `_u_maxima` — **it is on the grading path for `G-YPLUS`, `G-MESHSIM` and `G-CONV`, and it appears in neither the freeze table nor R2's four-file list.** **A sha recorder that leaves a grading-path member silent is the defect it was built to cure.** **REQUIRED: five files, not four.** **And `§2d.4.3`'s dual-sha condition stands** — post-repair sha **and** pre-registration blob sha, labelled as two objects, with a line stating no graded solve ever ran under a recorder-carrying comparator.

**R3 — GRANTED, AND MEASURED INERT.** `ORDER_BAND = (0.5, 1.5)` is frozen **pre-compute** at `:833-834` and is not proposed for change; `ORDER_BAND`/`ORDER_QUANTITY` occur **twice each**, both second occurrences inside a single `note()` — **`G-ORDER` cannot return `GATE FAIL` under any value of `p`**, verified in code, and `RT.grade_ladder`'s signature carries **no order-band parameter**. A registered gate unreachable in code is a departure; condition (2) **MET under §2d.5**. **Direction: restrictive — it can only ADD a `GATE FAIL`.** **On this data it adds none: p(Q4) = 0.6111 ∈ [0.5, 1.5] → PASS.** *The petition's "strictly tightens" argument is sound in principle and empty in effect, and I grant it on the principle while recording that it moves nothing.*

**R4 — SPLIT, AND HALF OF IT IS REFUSED. This is the sharpest ruling of the six.**

- **The band limb is GRANTED, and WIDENED.** `:455` gives `Q6`'s entire registered role with **no band**; `:581` passes it `BAND_Q1`. A departure; condition (2) **MET under §2d.5**. **⚠ AND THE PETITION UNDER-REPORTS ITS OWN DEFECT: `Q4` receives `BAND_Q1` at the same line and is registered at `:450` as the primary order quantity with NO fine-value band.** The unregistered band reaches **two** quantities, not one. **The repair must cover both, or it leaves half the defect standing while reporting it repaired.** *(Both currently PASS that band — `Q6` 50.847, `Q4` 53.195, band [46,56] — so removal takes away a PASS, not a `GATE FAIL`: non-permissive on this data.)*
- **⚠⚠ THE ROLLUP-EXCLUSION LIMB IS REFUSED, ON CONDITIONS (1) AND (2) AND ON DIRECTION.** **No registration text excludes a reported-only quantity's verdict from the rollup**, and the petition cites none — it is an **inference from silence**, which `§2d.5` names as the preference condition (1) excludes. **And the petition MISSTATES the direction.** It writes that removing `Q6` *"could remove either a `PASS` or a `GATE FAIL`."* **Measured, it removes neither: `Q6`'s row verdict is `NOT A RESULT`, and the rollup tests `"NOT A RESULT" in verdicts` FIRST.** The one case the petition's disjunction omits is **the case that obtains**, and it is **the strictly permissive one**.

> **RULED — a general property, registered here because it is not T23G2's alone: REMOVING A ROW FROM A ROLLUP CAN ONLY WEAKEN THE ROLLUP OR LEAVE IT EQUAL. IT CAN NEVER STRENGTHEN IT. A rollup exclusion is therefore ALWAYS a permissive change and requires REGISTERED TEXT, never an inference — whatever the excluded row's verdict happens to be on the day.**

**R5 — GRANTED, AND IT IS THE MOST IMPORTANT OF THE SIX.** `:624-625` registers *"Six quantities × three levels = **18 controls**, plus the two y+ readers = **20**"*; the code calls `plant_control_for` at **one line**, at the finest level only, for **five** quantities. §5.4 (`:601-602`) registers that the y+ reader *"**must plant a known perturbation and read it back, and refuse if it cannot see it** (rule 3)"*; `yplus_from_fields` contains **no plant** and argues its validity **documentarily**. Departures on both counts; condition (2) **MET under §2d.5**. **⚠ AND IT IS LOAD-BEARING RIGHT NOW, WHICH THE PETITION DOES NOT SAY: `G-RATIO` passes on all six quantities ONLY because the measured iterative change is exactly `0.0`** — `g_ratio` returns PASS with ratio ∞ on a zero, and the series is genuinely bit-identical (`3.411950435137e+02` at every sample, 13 significant digits). **Six exact zeros are carrying six `G-RATIO` passes while thirteen of the eighteen registered controls that would license them do not exist. That is standing rule 3's exact shape — a zero from a reader not shown able to see a non-zero — and it means even T23G2's PASSING gates are currently unlicensed.**

**R6 — REFUSED as a `§2d.1` repair, and referred rather than dismissed.** §5.4 registers two instruments and a 2 % agreement check, and registers that a **disagreement** is a refusal. **A MISSING instrument is neither agreement nor disagreement — the registration does not name the case, and the petition says so itself.** Under `§2d.5` **silence is not a departure**, so condition (2) has **no object** and `§2d` stands. **This is a refusal on the instrument, not on the merits: R6 is a good change.** It is strictly stricter and **measured inert** (all three `log.yPlus.fluid` present, parsed, four patches each; the branch is never taken). **REFERRED: register the refusal PROSPECTIVELY in the next rung's pre-registration, where it costs nothing and needs no exception. A gap in a registration is closed by the next registration, not by repairing the rung that revealed it.**

### §2d.8 THE DISPOSITION — AND NO REPAIR REACHES IT

**Verified by me at source, both numbers the disposition turns on:**

| gate | measured | registered | verdict |
|---|---|---|---|
| **`G-CONV`** | `T23G2_L2` last `p_rgh` initial residual **`1.04122627289e-08`** (L1 `9.1885e-09`, L3 `9.0751e-09`) | `≤ 1e-8` (`:561`) | **`GATE FAIL`** — 4.1 % over, on one level |
| **`G-YPLUS`** | `centrebody_up` max y+ **`1.8246 / 1.3540 / 1.0048`** | A2.2 `:1117-1118`, **`≤ 1.0` on EVERY wall patch, EVERY level** | **`GATE FAIL` on all three, the finest included** |
| `Q3` fine ΔT | **56.708 K** | A1.2 band **[46.0, 56.0]** | **`GATE FAIL`** |
| rollup | `G-CONV`'s failure propagates through **rule 5 step (a)** — no grid claim from any triple | — | **`NOT A RESULT`** |

**The graded triples are `CONVERGING`** (orders 0.610–0.615, GCI 5.27–5.85 %) **and it does not save the rows**: rule 5 step (a) fires first because `T23G2_L2` is not iteratively converged. `Q5` is `DIVERGENT` and is registered **reported, never gated**, with `DIVERGENT` pre-registered as expected under P4 — **so `Q5` does not make the rows `NOT A RESULT`; `G-CONV` does.**

> **NO COMBINATION OF R1–R6 CAN PRODUCE `PASS` OR `GATE REACHED` FOR T23G2. Measured, not argued. R1 makes the verdict REACHABLE; R2–R6 change the outcome by nothing measurable. The repairs decide the QUALITY OF THE RECORD, not the verdict.** **Rule 5's direction is respected throughout: every ruling above can only turn a verdict worse or leave it equal, and the one that could have gone the other way — R4's rollup exclusion — is the one I refused.**

**⚠ AND A2.2's REGISTERED PREDICTION IS NOT BORNE OUT, WHICH BELONGS IN THE RECORD BECAUSE THE REGISTRATION VOLUNTEERED IT.** A2.2 predicted maxima on `duct_wall` and `fluid_to_housing` — **both met**. **It registered no prediction for `centrebody_up`, the one patch that fails**, and closed with *"This costs nothing, because the design already meets it."* **The run falsifies that sentence.** A prediction that covers only the patches that pass is not a prediction; **the gate was still honestly registered as "every wall patch", and it is the gate that binds, not the forecast.**

**Also recorded, not ruled:** rule 4 holds on **all three levels, all six limbs including the age guard**, independently re-derived. Campaign spend **536.77 core-min** against a registered point of 579.2 and cap 1365 — **ratio 0.93, `capped=0`** — with **`$0.4589` DERIVED, never measured.** **No `COST_CALIBRATION.md` row exists for T23G2**; whether a rung that cannot be graded has "completed" for rule 12's purposes is **heat-transfer's to state and mine only if referred.**

**⚠ AGAINST MY OWN §2d.4.1, AND IT SURVIVES.** I denied the absence-disclosure shortcut on the ground that T23G2 **has numbers even though it has no verdict**. The lane then **produced a complete grading from the existing data, read-only, at zero solver compute, in one session.** **That is the discharge of conditions (3) and (4) I said was available, demonstrated rather than asserted** — and it confirms the distinction: **the graded-solve count is indeed zero, and the numbers exist anyway.** Heat-transfer may discharge (3) and (4) by publishing that before/after table.

| item | outcome |
|---|---|
| granted | **R1, R2 (widened), R3, R5** |
| split | **R4** — band limb granted **and widened to `Q4`**; **rollup exclusion REFUSED** |
| refused | **R4 rollup limb** (silence is not a departure; permissive) · **R6** (no object; referred prospectively) |
| new charter clauses | **§2d.5** frozen registration as condition (2) instrument, **for departures only** · **§2d.6** §2i.8 has no object where the registration fixed the mesh · **§2d.7** rollup removal is always permissive |
| T23G2 disposition | **`NOT A RESULT`**, over **`GATE FAIL`** on `G-CONV`, `G-YPLUS` and `Q3`'s band — **unreachable by any repair** |
| gates · thresholds · bands · caps · labels created/moved/retired | **0 · 0 · 0 · 0 · 0** |
| compute authorised | **NONE** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

## Amendment — v1.39, 2026-09-02 — **§2o: A NULL IS A CLAIM AND NEEDS ITS OWN PLANTED CONTROL. ansys's METHOD IS ADOPTED LAB-WIDE, AND SHARPENED — THEIR OWN RECOVERY NUMBERS ARE BIASED IN THE PERMISSIVE DIRECTION, WHICH DECIDES HOW BIG THE PLANT MAY BE.**

**Lines whose number changed above this section: 0.** **Zero solver compute; 0 core-min; $0.00.** **This amendment creates no gate, threshold, band, cap or label, and re-grades nothing.** It states **how a negative finding must be evidenced** before any existing gate may rest on one. Source: `ANSYS_VERIFICATION_CHARTER.md` §16.4, v1.11, commit `172f6378`, **read at source by me and not on relay.**

### §2o.1 THE PRINCIPLE, AND WHY IT IS NOT ALREADY COVERED

Standing rule 3 says a **zero** from a reader not shown able to see a **non-zero** is not evidence. **It names the zero case.** The ansys team read it as covering every negative finding, and **they are right, but their reading is a team's reading and a gate is not bound by one.** A null is the same object wearing different arithmetic:

- *"it does not decay"* — from a fit that cannot detect decay
- *"there is no trend"* — from a regression underpowered against the trend that matters
- *"the spread is zero"* — from a reader that would report zero on any input
- *"nothing moved"* — from a comparison that cannot see movement
- *"no arm fired"* — from a suite whose arms assert a code and never a value

**In every one, the finding's evidential content is exactly the reader's demonstrated ability to have found otherwise, and nothing else.** A reader that cannot fail to return the null returns it for free.

> **RULED — `§2o`: A ZERO, A NULL, A "NO TREND", A "NO DECAY", A "NOTHING MOVED" OR ANY OTHER NEGATIVE FINDING IS ADMISSIBLE AS EVIDENCE ONLY FROM A READER SHOWN, IN THE SAME RUN, ABLE TO SEE THE ALTERNATIVE. The demonstration plants the alternative into the REAL series, recovers it, and REFUSES if it cannot. A negative finding presented without it is `NOT A RESULT` — not a `GATE FAIL`, because nothing was measured.**

### §2o.2 THE EVIDENCE, AND THE SHARPENING THEIR OWN NUMBERS FORCE

ansys's lane planted known exponential decays into the real series and re-ran the same fit `[MEASURED, their §16.4]`:

| planted half-life | recovered | r² | error |
|---|---|---|---|
| 20 000 iterations | **20 967** | 0.992 | **+4.8 %** |
| 60 000 iterations | **64 472** | 0.990 | **+7.5 %** |

**The control fires, and I adopt it. But look at the direction of the residual: BOTH recoveries are BIASED HIGH, and consistently.** A half-life recovered **longer** than the truth is a decay reported as **slower** than it is — **and "slower decay" is the direction that shades toward "no decay at all."** **The instrument's residual error runs the SAME WAY as the null it is being used to license.**

**That is not a defect in their work — it is a property of exponential fits on truncated series, and they disclosed the numbers that reveal it rather than rounding them away.** But it decides the one thing a lab-wide clause must fix, which their team clause leaves open: **how big may the plant be?**

> **`§2o.2` — THE PLANT'S MAGNITUDE IS NOT FREE. The planted alternative must be AT OR BELOW the smallest departure that would change the verdict. A plant large enough to be easy is a control that proves the reader can see what nobody was worried about.**

**A generously large plant is the null-shaped version of the fail-open I booked twice today** — an arm that passes on a case the gate was never at risk from. `§2o.1`'s demonstration is only worth the margin it was run at, **and the margin must be the verdict's margin, not the planter's convenience.**

### §2o.3 WHAT THIS CLAUSE DOES NOT DO

It **does not require a plant on every reported number** — only where **a NEGATIVE finding is load-bearing for a gate**. A null reported beside a verdict it does not carry is prose, and prose is governed by `§2k`'s provenance tags.

It **does not amend `CLAUDE.md` rule 3**, which is constitutional and **not mine**. Rule 3's zero case stands exactly as written. **`§2o` binds GATING — which is this charter's subject — and the question of generalising rule 3 itself at the constitutional level is REFERRED to the chief and to Sanaa.** Where the two overlap, rule 3 governs and `§2o` adds nothing; where a null is not a zero, `§2o` reaches and rule 3's literal text does not.

**And it takes effect PROSPECTIVELY.** It does not retroactively void a recorded verdict. **It does mean that a null-carrying gate re-read from today forward must show its control**, and it names the specimens already on the books rather than leaving them to be discovered.

### §2o.4 ⚠ THE SPECIMEN THIS CLAUSE WAS ALREADY NEEDED FOR, AND I FOUND IT FOUR COMMITS AGO WITHOUT HAVING THE CLAUSE

**T23G2's `G-RATIO` passes on all six quantities ONLY because the measured iterative change is exactly `0.0`** (v1.38 `§2d.8`). `g_ratio` returns `PASS` with ratio ∞ on a zero. The series is genuinely bit-identical — `3.411950435137e+02` at every sample, 13 significant digits — so it is **not** a precision artefact. **And thirteen of the eighteen registered planted-zero controls that would license those readings do not exist.**

**That is `§2o` exactly: six gate passes resting on six nulls from readers not shown able to see the alternative.** Two teams reached the same species on the same day from opposite ends — **ansys found the cure while auditing a fit; I found the disease while ruling a petition.** **Neither of us would have named it a class alone**, and I record that the convergence is what makes it one.

**A third specimen, same day, same shape, booked in `FAIL_OPEN_GATE_AUDIT` §26:** a limb whose green means *"two phrases were found somewhere on the wire"* and which returns that green on a table attributing every quantity to the wrong party. **A null — "no violation found" — from a limb that never read the table.**

| item | outcome |
|---|---|
| ansys `§16.4` | **ADOPTED lab-wide as `§2o`**, verified at source, not on relay |
| the sharpening added | **the plant must be ≤ the smallest verdict-changing departure** — forced by their own permissive-direction bias |
| specimens on the books | **3** — T23G2's six `G-RATIO` zeros; `check_demo_acts.py`'s split limb; the class ansys found |
| `CLAUDE.md` rule 3 | **NOT amended — not mine.** Constitutional generalisation **REFERRED** to the chief and Sanaa |
| effect | **prospective**; no recorded verdict retroactively voided |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

## Amendment — v1.40, 2026-09-02 — **§2p: A PASS MUST BE ATTRIBUTABLE. THE THREE INSTRUMENT DEFECTS THIS LAB FOUND IN ONE DAY ARE ONE DEFECT, AND THE TEST THAT GENERATES ALL THREE COSTS NOTHING: FEED THE GUARD NOTHING AND SEE WHAT IT SAYS.**

**Lines whose number changed above this section: 0.** **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label created, moved or retired; nothing re-graded.** Sources: `L-436` + addendum `5ef3bcda` (ansys), `ANSYS_VERIFICATION_CHARTER.md` §16.4 (adopted here as `§2o`), and this team's own `FAIL_OPEN_GATE_AUDIT` §§24–27. **Every mechanism below was driven by me, not read.**

### §2p.1 THE THREE ARE ONE, AND NAMING THE ONE IS WORTH MORE THAN THE THREE

Three instrument defects surfaced across three teams in a single day. They look unrelated and are not:

| specimen | the instrument said | the reason it said it |
|---|---|---|
| a decay fit reporting **"it does not decay"** | no decay | **the fit could not have detected decay** |
| a before/after **`md5` guard** reporting **"unchanged"** | unchanged | **both operands collapsed to the empty digest** |
| a `sorted(dirs)[-1]` reader reporting **"the latest directory"** | latest | **lexicographic order coincided with — or contradicted — time order** |

**In every one the instrument returned the reassuring answer, and the reason it returned it is not the reason it claims.** The pass is genuine **as an output** and vacuous **as evidence**.

> **RULED — `§2p`: A PASS IS EVIDENCE ONLY IF THE RUN ALSO SHOWS THE PASS COULD NOT HAVE ARISEN FROM A DEGENERATE PATH. An instrument that returns the passing value when its input is absent, destroyed, or outside its competence has not passed — it has failed to notice, and the two are indistinguishable from the verdict alone.**

### §2p.2 THE TEST THAT GENERATES THE WHOLE CLASS, AND IT IS FREE

I do not want a lab enumerating failure modes; enumeration always ends one specimen short. **There is a single test that finds all three and is cheaper than any of them:**

> **THE EMPTY-INPUT TEST — feed the guard NOTHING and see what it says. If it says PASS, IT IS NOT A GUARD.**

**No knowledge of the failure mode is required, and that is the point.** The decay fit on a flat series, the digest guard on a destroyed file, the directory reader on an empty tree — **each returns its passing value, and each does so for a reason its author never enumerated.** A guard that cannot be made to refuse by being given nothing is not measuring its subject.

### §2p.3 THE THREE REQUIRED LIMBS, EACH TIED TO ITS DEGENERATE PATH

**(a) INSENSITIVITY — the reader cannot see the alternative.** Cured by **`§2o`** (v1.39): plant the alternative into the real series, recover it, refuse if you cannot; and **`§2o.2`** — the plant must be **at or below the smallest verdict-changing departure**.

**(b) COMMON-MODE COLLAPSE — a relative comparison whose two operands share a failure that moves both together.** This is `L-436`'s discovery and it is the sharpest of the three, because **the guard is not weak, it is STRUCTURALLY UNABLE TO FIRE.**

> **RULED: EVERY DIFFERENTIAL GUARD CARRIES AN ABSOLUTE LIMB BESIDE IT. A comparison of two derived values can NEVER detect a failure that collapses both derivations together, and no amount of care in the comparison repairs that — the defect is in the SHAPE, not the coding.**

**Driven by me `[MEASURED]`, and it is worse than the referral states:** `head -n 5` on a **zero-length** file returns **`rc 0`**, empty output, digest **`d41d8cd98f00b204e9800998ecf8427e`**. `head` returns **`rc 1` only on a MISSING file, never on a DESTROYED one** — **so checking `rc` does not save you**, which is the assumption that makes this defect survive review. Before and after both read `d41d8cd9…`; **the guard reports UNCHANGED, PASS, on a file with no content at all.**

**⚠ AND THE TWO PROPOSED LIMBS ARE NOT INTERCHANGEABLE, WHICH THE REFERRAL'S WORDING WOULD LET A READER BELIEVE.** *"Either limb alone catches total loss"* is **true and incomplete.** Measured across three input states:

| input | empty-digest limb | **line-count limb** |
|---|---|---|
| healthy, 5 lines | miss *(correct)* | miss *(correct)* |
| **partially truncated, 3 lines** | **MISSES** | **FIRES** |
| destroyed, 0 lines | FIRES | FIRES |

**The count limb STRICTLY DOMINATES.** Partial truncation yields a perfectly ordinary non-empty digest (`40c53c58…`), identical before and after, and **the empty-digest limb is blind to it** — while the count limb catches both. **REQUIRED: assert that the prefix actually contains the N lines being hashed. The empty-digest check is retained as a cheap independent cross-check with a different failure mode, and MUST NOT be offered as an alternative to the count.** *Total loss is the easy case; partial loss is the one that ships.*

**(c) PROXY KEYING — ordering or selecting by a RENDERING of the quantity instead of the quantity.** A `sorted()` over numeric directory **names** sorts strings. **Driven by me:** `sorted(['0','10000','30000','5000'])[-1]` returns **`'5000'` where the true latest is `'30000'`**, while `[0]` returns `'0'`, which is **coincidentally correct**.

> **RULED: SELECTION AND ORDERING ARE KEYED ON THE QUANTITY, NEVER ON ITS TEXTUAL FORM. `sorted(..., key=int)` or equivalent; a bare `sorted()` over numeric names is a defect whichever end is taken.**

**⚠ AND THE NAIVE FIX IS MORE DANGEROUS THAN THE DEFECT, which is why this clause forbids the patch as well as the defect.** `sorted(dirs)[0]` is **coincidentally correct whenever `'0'` is present — the common case in an OpenFOAM tree.** **A team told "take `[-1]` instead" converts a read a coincidence was protecting into one that is reliably wrong.** *A repair that changes which coincidence you depend on is not a repair.* **Scope pending: a sweep of every grading-path reader is in flight; its LIVE-versus-LATENT counts are NOT YET ESTABLISHED and this clause is stated on mechanism, not on incidence.**

### §2p.4 WHAT THIS DOES NOT DO, AND ONE THING IT COSTS

It **does not amend `CLAUDE.md` rule 3** — constitutional, not mine; `§2p` binds **gating**, and the constitutional generalisation stays **referred** to the chief and Sanaa. It **takes effect prospectively** and **voids no recorded verdict**. It **adds no gate** — it states what an existing gate's PASS must be able to show.

**And it costs something real, which I state rather than let a team discover:** every limb above is **work on instruments that are already green**, and the return is **entirely invisible** — nothing to publish, no rung advanced, and the only evidence of success is a refusal that never had to happen. **A lab that measures itself by rungs closed will not do this, and this clause exists because we have now paid for the alternative three times in one day.**

**⚠ AGAINST MYSELF, AND IT IS THE FOURTH SPECIMEN OF `§2p` TODAY AND THE ONE I OWN.** `FAIL_OPEN_GATE_AUDIT` §27.6: I built a foreign-content assert, **it fired**, it printed `foreign:PRESENT` in the same invocation immediately before the commit — **and the commit proceeded, because I wrote `echo` and never wrote `|| exit 1`.** **A guard that reports and does not refuse is `§2p`'s exact shape**, and I shipped it **inside the audit file that names the class**. **The empty-input test would have caught it in one line.**

| item | outcome |
|---|---|
| the unifying clause | **`§2p` — a pass must be attributable; a pass from a degenerate path is not evidence** |
| the generator | **THE EMPTY-INPUT TEST — feed the guard nothing; if it passes, it is not a guard** |
| limb (a) insensitivity | `§2o`, already landed v1.39 |
| limb (b) common-mode collapse | **absolute limb REQUIRED beside every differential guard** |
| **correction to the referral** | **the limbs are NOT interchangeable — the COUNT limb strictly dominates; the empty-digest limb is blind to partial truncation** `[MEASURED]` |
| limb (c) proxy keying | **key on the quantity, never its textual form**; the naive `[0]→[-1]` patch is **forbidden**, not merely insufficient |
| specimens of `§2p` in one day | **4** — the decay fit, the digest guard, the directory sort, **and my own non-gating assert** |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

### §2p.5 — **LIMB (c) CLOSED ON MEASUREMENT: INCIDENCE IS ZERO, THE PREMISE THAT JUSTIFIED THE SWEEP WAS FALSE, AND THE RIGHT CURE IS NOT THE ONE I WROTE**

**Appended 2026-09-02. Lines whose number changed above this section: 0.** `§2p.3(c)` was stated on mechanism with incidence marked NOT YET ESTABLISHED. The sweep has reported and **every correction below runs against my own clause.**

**INCIDENCE: `LIVE 0`, `LATENT 25`, `NOT DETERMINABLE 0`** `[MEASURED, 2,114 `.py` files; 4,503 directories holding ≥2 numeric-named subdirs]`. **Every function-object directory read by a confirmed string-sorted grading-path reader holds exactly ONE subdirectory on disk.** 22 genuine time-directory selections were hand-verified out of 41 unguarded-lexicographic candidates. **The mechanism is real and its current exploitation is nil** — and the honest reading is that the class is **latent, not live**, which is a weaker statement than the referral's and I make it anyway.

**⚠ THE PREMISE THAT JUSTIFIED THE SWEEP IS FALSE. It was ONE specimen, not two.** VMFL054's comparator is **REFUTED as a defect, verified by me at source**: `grade_vmfl054.py` has **one commit in its entire history**, and that single committed version already carries `if len(subs) > 1: refuse("…a restart wrote more than one; REFUSING rather than guessing which is current")` **immediately above** the `subs[0]`. **The index is reached only when the list has exactly one member. There is no repair diff in the repository because there was nothing to repair.** `analyse_L3_plateau.py:112,158` **is** genuine and **unrepaired at HEAD**. **So "twice in one day, a pattern not an accident" — the sentence that motivated a lab-wide sweep — does not survive.** *The sweep was still right to run, because the MECHANISM was verified independently and does not depend on the count. But a class propagated on a miscount is how a lab acquires rules nobody can later justify, and this one came within one unchecked citation of that.*

**⚠ AND THE DISCRIMINATOR IS NOT THE INDEX — IT IS WHETHER THE SITE IS GUARDED.** Under a `refuse-unless-exactly-one` guard, `[0]`, `[-1]` and integer-keyed selection are **identical**, and most sites reached that way are sound. Of 205 time-like candidates: **96 unguarded, 69 named, 26 guarded, 13 guarded+named.**

> **`§2p.5` REVISES `§2p.3(c)`: ANCHORING BEATS ORDERING, AND REFUSAL BEATS BOTH. A reader that knows which time it needs SELECTS BY THAT TIME and REFUSES if it is not uniquely present. Ordering — numeric, never lexicographic — is the FALLBACK for when the target genuinely is "whatever is latest". A `refuse-unless-exactly-one` guard is a sufficient alternative to integer keying and is STRONGER, because it declines rather than chooses.**

**The lab had already converged on this twice and I should have looked before writing a rule.** `VMFLGPU003/grade_vmflgpu003.py:364-400` is **named AND integer-keyed AND refusing**, and says why in its own words: *"Never `the last directory`: a truncated or restarted run leaves a perfectly well-formed profile for the wrong iteration, and that number is indistinguishable from the right one once it is out of context"* — *"the gate is read AT endTime or it is not read."* **It is also the reader for the one directory on disk where a string sort actually disagrees, and it is immune.**

**MEASURED AND REASSURING, stated because a null belongs on the record as much as a hit (`§2o`): NO grader anywhere selects a CASE TIME DIRECTORY by string sort** — every one uses `key=float` or equivalent. **That closes the highest-consequence variant, and it matters because case time dirs hold 490 of the 527 "naive-fix-breaks" directories.** For case time dirs `[0]` disagrees in **2 of 3,741 (0.1 %)** — the `'0'`-sorts-first coincidence holding — while for `postProcessing` dirs the coincidence does **not** hold: `[0]` disagrees in **60.2 %**.

**THE AGE-GUARD CROSS-CHECK IS CONFIRMED AND THE HAZARD IS AS LARGE AS IT LOOKS.** Both canonical implementations stat **only case time-dir fields against `0/`** and **nothing under `postProcessing/`**. A reader that picks the wrong function-object directory reads a file **the age guard never opens**.

**⚠ A REFINEMENT TO "GRADING PATH" THAT THIS FOUND, AND IT IS NOT COSMETIC.** `analyse_L3_plateau.py`'s own docstring says *"THIS SCRIPT PRODUCES MEASURED NUMBERS. It grades nothing, issues no verdict"* — so by a literal reading it is diagnostic and not urgent. **But its numbers are cited in `docs/NUMERICS_KNOWLEDGE.md` and `docs/charters/ANSYS_VERIFICATION_CHARTER.md`** `[MEASURED, 2 citations each]`. **A script that grades nothing but whose outputs become RECORDED LAB FACTS is on the RECORD path, and the record path deserves the grading path's hygiene.** *"It issues no verdict" is not a discharge when a charter quotes its number.*

**COUNTS ARE LOWER BOUNDS, DISCLOSED BY THE LANE AGAINST ITS OWN WORK.** Its guard-detector marks a site GUARDED whenever the **enclosing function** contains any `len()` check, which falsely absolved `analyse_t15.py:693` — unguarded and lexicographic, caught only by hand. **Any unguarded site inside a large function that guards something else was silently absolved, so the 22 may be incomplete.** Closing it needs control-flow reachability, not an enclosing-function heuristic. **Non-Python readers were not swept.** And **LIVE/LATENT is a snapshot: a latent case becomes live the moment it is restarted, which is exactly how these directories multiply.**

**THE SCANNER IS NOT LANDED, and the reason is `§2p` itself:** it carries **two known defects**, one of which produces **false GREENs**. **Landing an instrument that absolves sites it did not check would be the fail-open this clause exists to forbid.** If it is wanted as a standing instrument it is repaired first, with the empty-input test and a planted control on the false-GUARDED shape.

| item | outcome |
|---|---|
| incidence | **LIVE 0 · LATENT 25** — mechanism real, exploitation nil |
| the referral's premise | **FALSE — one specimen, not two.** VMFL054 **REFUTED** at source; `analyse_L3_plateau.py` **CONFIRMED**, unrepaired |
| `§2p.3(c)` as I wrote it | **REVISED — anchoring beats ordering; refuse-unless-exactly-one beats both** |
| case time directories | **CLEAN lab-wide** — the highest-consequence variant is closed |
| age guard | **CONFIRMED BLIND** to this class |
| "grading path" | **widened to the RECORD path** — a diagnostic quoted by a charter is not diagnostic |
| counts | **LOWER BOUNDS**, by the lane's own disclosed defect |
| repairs mandated | **0** — referred; `analyse_L3_plateau.py` is ansys's file |
| solver compute | **0 core-min, $0.00**; the sweep itself ~15 core-min of static analysis, **not a pre-registered run** |

### §2p.6 — **MY §2p.5 REFUTATION IS ITSELF REFUTED, AND CORRECTLY. A SWEEP THAT READS ONLY COMMITTED HISTORY RETURNS "CLEAN" WHETHER NOTHING WAS WRONG OR EVERYTHING WAS CAUGHT PRE-FREEZE — WHICH IS §2p's OWN DEFINITION, IN MY OWN AUDIT.**

**Appended 2026-09-02. Lines whose number changed above this section: 0.** `§2p.5` is **struck in one sentence and stands in the rest**; per rule 6 it is corrected here, not edited above. Source: ansys charter v1.14, `45b36f4d`. **Verified by me at source before acceptance — the same check I would run on a correction that favoured me.**

**WHAT I GOT RIGHT AND WHAT I OVERSTATED.** `§2p.5` said VMFL054 was *"REFUTED as a defect"* and — the overreach — *"there was no repair diff in the repository because there was nothing to repair."* **The first half is supportable; the second is not, and it is mine.** The freeze commit `05ec949e`'s **own message** records the defect verbatim `[MEASURED, read by me at source]`:

> `COMPARATOR DEFECTS D1-D4, found in my §3 check-1 diff read, all fixed with every gate`
> `D3 a silent-wrong-answer path: the gate reader hardcoded centreProbe/0/U, so a …`

**The hardcoded path existed in the UNCOMMITTED draft and was repaired by the author's own pre-freeze check-1 diff read.** The single clean commit in that file's history is **the RESULT of a guard firing**, not evidence that nothing was wrong. **The supervisor's §3 check-1 duty is not decoration — here it caught a silent-wrong-answer path before any compute, and my sweep then read its success as the absence of a problem.**

> **THE SUPPORTED FORM, replacing `§2p.5`'s sentence: "ONE specimen in COMMITTED HISTORY; the second existed PRE-FREEZE per the freeze commit's own message and was caught by the author's own check-1 read."**

### §2p.6.1 THE METHODOLOGICAL CLAUSE, ADOPTED LAB-WIDE — AND IT IS §2p's FIFTH SPECIMEN, MINE

> **RULED: COMMIT HISTORY IS NOT THE RECORD. A sweep that reads only committed history is STRUCTURALLY BLIND to every defect a pre-freeze check catches: it returns "clean" when nothing was wrong AND when everything was caught early, and THE TWO ARE INDISTINGUISHABLE FROM ITS OUTPUT ALONE. Absence from git history is not absence from the record — COMMIT MESSAGES, pre-registrations and check records are where that work leaves its trace, and a sweep that does not read them has not looked.**

**Apply `§2p.2`'s own empty-input test to my sweep and it fails in one line: feed it a repository in which EVERY defect was repaired before commit, and it reports ALL CLEAN.** A guard that cannot be made to refuse by being given a perfect input is not measuring what it claims. **My history sweep is exactly that**, and I built it two commits after writing the test that finds it.

**⚠ AND THE SYMMETRY IS THE INSTRUCTIVE PART, SO I STATE IT AGAINST MYSELF FIRST.** `§2p.5` corrected the referral **for propagating a class on a miscount**. My correction was **itself an overreach, on an instrument whose blind spot I had not checked.** **Both parties were right about the other's error and wrong in the same way** — each trusted a count without asking what the counting instrument could not see. *That is not two mistakes; it is one mistake made twice, and it is why `§2p` is a standard and not a note.*

**Specimen count for `§2p` in one day: FIVE. Three are mine** — the non-gating assert (`FAIL_OPEN_GATE_AUDIT` §27.6), the history-blind sweep (here), and the §2p.5 overreach they produced together.

### §2p.6.2 WHAT ansys DID WITH THE RULINGS, RECORDED BECAUSE IT IS THE STANDARD FOR A REPAIR

They **adopted `§2p.5`'s guarded-versus-unguarded discriminator in place of their own integer-sort rule**, and **adopted the record-path hygiene rule** (`§2p.5`: a script that grades nothing but whose numbers a charter quotes is on the record path). **`analyse_L3_plateau.py` now refuses on ambiguity, the repair was verified BY PLANT, and its outputs are BYTE-IDENTICAL so no recorded number moved.**

**That is the shape a repair should have and I record it as the reference:** the fix **refuses** rather than choosing; the refusal is **demonstrated by a plant** rather than asserted (`§2o`); and the **no-change claim is verified byte-wise** rather than reasoned, so `§2d.1`'s conditions (3) and (4) are discharged at zero. **A repair that cannot show what it did not move is not finished.**

| item | outcome |
|---|---|
| `§2p.5`'s *"nothing to repair"* | **STRUCK — my overreach**, corrected to the supported form |
| `§2p.5`'s rest, incl. LIVE 0 / LATENT 25 | **STANDS** |
| new clause `§2p.6.1` | **commit history is not the record**; a history-only sweep is blind to pre-freeze repairs |
| `§2p` specimens in one day | **5 — three of them mine** |
| ansys's repair | **the reference shape** — refuses, plant-verified, byte-identical outputs |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |

## Amendment — v1.41, 2026-09-02 — **§2d.9 + §2p.7: R7 IS GRANTED — IT REPAIRS A RULE-5 VIOLATION INSIDE A REPAIR I GRANTED THIS AFTERNOON, AND I MEASURED THE VALUE THAT PRODUCED IT WITHOUT ASKING WHETHER THE VERDICT WAS LEGAL. AND THE MISFILED-COMPARATOR REFUSAL BECOMES PERMANENT.**

**Lines whose number changed above this section: 0.** **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label created, moved or retired; nothing re-graded by this amendment.**

### §2d.9.0 A ROUTING CORRECTION FIRST, BECAUSE I ALMOST RULED ON THE WRONG ITEM

`R7` was relayed to me as *"the misfiled comparator … a POST-COMPUTE grading-path relocation."* **It is not.** `docs/campaigns/T-family/T23G2_R7_ORDER_GATE_PETITION.md` is a **`§2d.1` petition to repair `gate_order`**, and its subject line reads *"a defect in `R3` — a **granted** repair — found after the grant, in its delivered code."* **The relocation is §8 item 1 of the EARLIER petition and I ruled it in `§2d.4.2`.** *I read the document rather than the summary, which is the only reason this ruling is about the right thing — the fourth time today a relay has differed from its source in a way that mattered.*

### §2d.9.1 R7 — GRANTED, AND IT FINDS A DEFECT I SHIPPED

**What is asked:** `gate_order` must return **`NOT A RESULT`** when any level's iterative-convergence or plateau state would void the grid claim, **instead of returning `PASS` or `GATE FAIL` on an order belonging to a voided claim.**

**That is standing rule 5, verbatim and unambiguous:** *"A row whose grid triple is not `CONVERGING` is `NOT A RESULT`, whatever its value… The gate can only turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse."* **A `gate_order` that emits `PASS` on a voided claim does the reverse.**

**⚠ AND I GRANTED THE REPAIR THAT SHIPPED IT, THIS AFTERNOON.** `§2d.7` ruled `R3` *"GRANTED and MEASURED INERT — p(Q4) = 0.6111 ∈ [0.5, 1.5] → PASS."* **I measured the value, confirmed it fell in the registered band, and never asked whether a `PASS` was LEGAL on a claim rule 5 had already voided.** `T23G2_L2` is not iteratively converged; every row is `NOT A RESULT` at rule 5 step (a); **and I authorised a gate that would have printed `PASS` beside them.** *The number was right. The verdict it produced was not permitted, and checking the number felt like checking the gate.*

**The four conditions:**

1. **DEMONSTRABLE ERROR — MET.** A violation of standing rule 5, exhibited from the rule's text against the delivered code. Not a preference.
2. **INDEPENDENT INSTRUMENT — MET, and `§2d.5` extends A FORTIORI.** `§2d.5` ruled a sha-frozen pre-registration qualifies because it cannot have been selected to move a verdict. **A STANDING RULE IN `CLAUDE.md` satisfies that MORE completely still: it is lab-constitutional, predates every rung, grades nothing, and cannot know which direction any verdict wants.** **RULED: a standing rule is an instrument independent of the hypothesis for condition (2), on the same ground and with more force than a frozen registration.**
3. **and 4. BITE IN FULL, and are DISCHARGEABLE AT ZERO.** T23G2 now carries a **published, final verdict**, so `§2d.4.1` applies exactly as I wrote it. **REQUIRED: publish the pre-repair `G-ORDER` cell (`PASS`) beside the post-repair cell (`NOT A RESULT`), and state that the RUNG verdict is UNCHANGED** — the rollup already carries `NOT A RESULT` from three independent grounds, so **the repair moves a CELL and not the rung.** That distinction must appear in the record, not be left for a reader to infer.

**DIRECTION: STRICTLY RESTRICTIVE — it can only turn `PASS` or `GATE FAIL` INTO `NOT A RESULT`, which is the sole direction rule 5 permits.** *This is the easiest grant of the seven and it is the one that mattered most, because it repairs the only item among them that could have put an illegal verdict into a record.*

> **RULED: `R7` GRANTED, on all four conditions, with the cell-level before/after published.**

### §2d.9.2 THE MISFILED COMPARATOR — `§2d.4.2`'s CONDITION IS DISCHARGED, AND THE REFUSAL NOW BECOMES PERMANENT

`§2d.4.2` forbade relocation *"while T23G2 is ungraded."* **`T23G2_RESULTS.md` now reads `## RUNG VERDICT: NOT A RESULT`** `[MEASURED]` — **the condition is spent, and the question is properly open again.** I close it the other way, and more firmly.

**The comparator is at `docs/campaigns/T-family/analyse_t23g2.py`, 56,884 bytes; `verification/runs/T-family/T23G2_runs/analyse_t23g2.py` DOES NOT EXIST** `[MEASURED]`. §7 registers the latter — **and §7's own next words are *"It does not exist yet"***, so §7 was a **statement of intent about a file not yet written**, not a description of where the comparator lived while it graded.

> **RULED — PERMANENTLY, not conditionally: THE COMPARATOR DOES NOT MOVE. MOVING IT WOULD NOT MAKE THE REGISTRATION TRUE — IT WOULD MAKE THE RECORD FALSE.** The registration would then appear to describe where the comparator sat during grading, and it never sat there. **A post-hoc relocation converts a DISCLOSED discrepancy into a CONCEALED one, and produces a tree that lies about its own history.**

**AND THE REPAIR §2d.5 ACTUALLY LICENSES POINTS THE OTHER WAY.** The demonstrable error is in the **registration's §7 text**, which names a path the file never occupied. **`§2d.1` permits repairing the error — and the error is in the RECORD, not in the file's location.** **REQUIRED, if heat-transfer wants it closed: a dated addendum correcting §7 to state the ACTUAL path, altering no gate. You repair the record to match reality, never reality to match the record.**

### §2p.7 LIMB (d) — **THE TEST EXERCISES A COPY, NOT THE ORIGINAL. AND THE EMPTY-INPUT TEST DOES NOT CATCH IT.**

`L-437`: a selftest green produced by a **DUPLICATE CONJUNCT on a forged branch**, while **production takes the unguarded path.** The green is real; **it comes from code the production path does not execute.**

> **RULED — `§2p.3(d)`: A TEST THAT EXERCISES A REDUNDANT COPY OF THE GUARDED LOGIC TESTS NOTHING. A pass is attributable only if the code that produced it is the code that runs.**

**⚠ AND THIS IS THE LIMB THAT BREAKS MY OWN GENERATOR, WHICH I SAY BEFORE ANYONE ELSE NOTICES.** `§2p.2` offered the **empty-input test** as the free test that finds the whole class. **It does not find this one:** feed the duplicate nothing and it refuses correctly, because *the duplicate is fine* — the defect is that **it is not the code under test.** **`§2p.2` is therefore NECESSARY AND NOT SUFFICIENT, and I amend my own claim rather than leave it standing wider than its instrument.**

> **THE TEST FOR LIMB (d) IS MUTATION OF THE PRODUCTION PATH SPECIFICALLY: mutate the line that RUNS and require the suite to fail. A suite that survives a mutation of production code is not testing production code.**

**heat-transfer supplied exactly that instrument and its number: guard kill-rate `36/46 = 78 %`.** **I read that as `10 OF 46 MUTATIONS SURVIVED`, and I state it that way** — 78 % is not a pass mark, it is **ten measured blind spots in a suite that now knows where they are**, which is strictly better than any suite that has never been mutated. **This also discharges my own `§2n.18` referral, which my T23G2 ruling flagged as NOT satisfied: the guards have now been exercised.**

| item | outcome |
|---|---|
| routing | **CORRECTED — R7 is the `gate_order` repair, not the relocation** |
| **R7** | **GRANTED** — repairs a **rule-5 violation** inside a repair I granted hours earlier |
| against myself | **I measured p(Q4) in band and never asked whether the `PASS` was LEGAL on a voided claim** |
| `§2d.5` extended | **a standing rule is condition (2)'s instrument a fortiori** |
| conditions (3)/(4) | **bite in full** — cell-level before/after required; **the rung verdict does not move** |
| relocation | **REFUSED PERMANENTLY** — it would make the record false, not the registration true |
| the repair actually licensed | **an addendum correcting §7's text** — repair the record to match reality |
| `§2p` limb (d) | **a test exercising a copy tests nothing** |
| **`§2p.2` amended against myself** | the empty-input test is **necessary, NOT sufficient** — limb (d) needs **production-path mutation** |
| kill-rate | **36/46 — i.e. TEN MUTATIONS SURVIVED**; `§2n.18` discharged |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |

## Amendment — v1.42, 2026-09-02 — **§2d.10 + §2p.8 + §2q: THE `G-RATIO` QUESTION IS RULED AND THE PASS FAILS ON TWO INDEPENDENT GROUNDS, ONE OF WHICH THE PETITION DID NOT RAISE. A RESTRICTIVE REPAIR IS NOT SELF-CERTIFYING — WHICH CORRECTS THREE GRANTS I MADE TODAY. AND THE LAB'S RULE-2 ENFORCEMENT INSTRUMENT IS BLIND TO THE COMPARATOR I JUST ORDERED TO STAY WHERE IT IS.** **[⚠ TWO, NOT THREE — `R6` WAS REFUSED; see `§2p.9` v1.50 and `§2p.11` v1.55]**

**Lines whose number changed above this section: 0.** **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label created, moved or retired; nothing re-graded.** The `§6` question is **ruled on its own merits, not inferred from `R7`'s grant** — quoted at source, as asked.

### §2d.10 THE LICENSING-GATE CLAUSE, AND WHY IT IS BROADER THAN `G-RATIO`

heat-transfer's `§6` is put as **a question, not a claim** — *"We do not assert that `G-RATIO` has the same defect. We ask"* — and it states the mechanism precisely `[verified by me at source]`: the **numerator** is `min(abs(d) for d in level_diffs)` at `:294`, drawn from the L1/L2/L3 ladder so **every difference involves `T23G2_L2`**, the non-converged level; the **denominator** is `L3`'s own plateau spread, **`0.0` exactly**, so the zero-branch at `:295-304` returns `PASS` with ratio ∞. **They correctly locate the contamination in the numerator and correctly exempt the denominator**, which is measured on `L3` alone and *is* converged.

`G-RATIO`'s own stated purpose, `:281`: *"otherwise the observed order is noise, not discretisation."* **It exists to LICENSE the observed order.**

> **RULED — `§2d.10`, and stated generally because `G-RATIO` is only the instance: A GATE WHOSE PURPOSE IS TO LICENSE ANOTHER QUANTITY MUST RETURN `NOT A RESULT` WHENEVER THAT QUANTITY IS ITSELF `NOT A RESULT`. A licence issued for a voided claim is not a verdict — it is a CATEGORY ERROR, an assurance about an object that does not exist.** Rule 5 step (a) has already voided the observed order; **there is no order for `G-RATIO` to license.** Direction is rule 5's only permitted one: `PASS` → `NOT A RESULT`.

**⚠ AND THERE IS A SECOND, INDEPENDENT GROUND THE PETITION DID NOT RAISE, WHICH I ADD RATHER THAN LET IT SIT.** With `iter_change` **exactly `0.0`**, the zero-branch returns ∞ **regardless of the numerator entirely.** **The `PASS` is attributable to the denominator being zero and to NO property of the ladder** — it would have returned ∞ and `PASS` for **any** numerator, contaminated or pristine. **That is `§2p` in its own right: a pass from a degenerate path.** So `G-RATIO`'s `PASS` fails **twice over and for unrelated reasons** — it licenses a voided claim, *and* it is not attributable to the thing it claims to measure. **Either alone is sufficient.** *The petition asked whether the numerator was contaminated. The sharper answer is that on this data the numerator was never consulted.*

**And the honest qualification, because "contaminated" overstates it:** the ratio is not *meaningless* — it is **UNINTERPRETABLE**. A large value could mean *"grid differences dominate iterative error"* (the intended reading) or *"L2's iterative error is inflating the inter-level differences"* (the contaminated one). **The instrument cannot distinguish them, and not having to is precisely what rule 5 step (a) is for.**

**NOT A PETITION, AND I TREAT IT AS THEY ASKED.** They explicitly requested no repair to `G-RATIO`. **This ruling states the LAW; whether and when `analyse_t23g2.py` is changed is heat-transfer's, subject to `§2d.1` and to `§2d.4.1`'s full-force (3) and (4).** T23G2's rung verdict is `NOT A RESULT` and **this moves a cell, not the rung.**

### §2p.8 A RESTRICTIVE REPAIR IS NOT SELF-CERTIFYING — AND THIS CORRECTS THREE GRANTS I MADE TODAY **[⚠ TWO, NOT THREE — `R6` WAS REFUSED; see `§2p.9` v1.50 and `§2p.11` v1.55]**

heat-transfer's lane invented the control and it is the one I was missing: **drive the PRODUCTION gate over PLANTED inputs and prove the restrictive repair RESTRICTED rather than DISABLED it — 5/5, including a `PASS` returned on an all-`CONVERGED` plant.**

> **RULED — `§2p.3(e)`: EVERY RESTRICTIVE REPAIR CARRIES A POSITIVE CONTROL. It is not enough to show the gate now refuses what it should refuse; the same run must show it STILL PASSES WHAT IT SHOULD PASS, driven through the PRODUCTION path over a planted input constructed to deserve a pass. A repair that refuses everything is "restrictive" in the trivial sense and is indistinguishable, from its verdicts alone, from a correct one.**

**⚠ AND IT RUNS AGAINST MY OWN REASONING THIS AFTERNOON, ~~THREE TIMES~~ TWICE.** **[⚠ STRUCK IN PLACE 2026-09-03, v1.55 `§2p.11` — this paragraph named a grant that was REFUSED.]** I granted **`R3`, `R5` and ~~`R6`~~** — **`R6` WAS REFUSED, at `:4523`, `:4540` and `:4567`; it was never granted, and the error is corrected at `§2p.9` (v1.50)** — with the direction analysis *"restrictive → easy grant on direction"* (`§2d.7`). **That reasoning is incomplete: a repair can be restrictive BY BEING BROKEN, and I treated the direction as self-certifying in ~~all three~~ both.** The grants stand — nothing in them is shown wrong — **but each now owes `§2p.3(e)`'s positive control before its output is believed** **[DISCHARGED for `R3` and `R5` through the production path, v1.50 `§2p.10`; `R6` owes nothing because it was never granted]**, and I record that as a debt against my own rulings rather than waiting to be asked. **heat-transfer has already adopted the control as mandatory on their team; I make it lab law and note that they got there first.**

### §2q THE RULE-2 ENFORCEMENT INSTRUMENT IS BLIND TO THE FILE I JUST ORDERED TO STAY PUT

**MEASURED:** `scripts/check_comparator_freeze.py:131` — `POPULATION_ROOTS = ("verification", "cases")`. **`docs/campaigns` appears ZERO times in the file.** **T23G2's comparator, at `docs/campaigns/T-family/analyse_t23g2.py`, is outside the walk entirely: ZERO freeze coverage.**

**This is `§2p` in the lab's own constitutional enforcement instrument** — `CLAUDE.md` rule 2 names this script as what enforces the comparator freeze. **Apply `§2p.2`'s empty-input test: give it a repository whose every comparator lives outside its walk roots and it reports ALL CLEAN.** **It is the same shape as my own history-blind sweep (`§2p.6.1`), and it is worse, because mine was an audit and this one is the enforcement.**

**⚠ AND `§2d.9.2` — MY OWN RULING, HOURS OLD — IS WHAT MAKES IT PERMANENT.** I forbade the relocation, correctly: moving the file would make the record false. **But that ruling guarantees the comparator stays outside the walk, so nothing within heat-transfer's authority can ever fix this.** *A correct ruling created a permanent coverage hole, and naming that is part of making the ruling.*

**I SPEC IT; I DO NOT AMEND IT — and I hold that line against a routing that offered me the choice.** `scripts/` is outside this team's folder scope. I have refused to repair cross-team instruments twice today on exactly this ground (`check_demo_acts.py`, and previously `check_grader_self_blindness.py`), and **being told the call is mine does not widen my scope — only Sanaa's own words or the permission system do (rule 9).** *Consistency is worth more here than the half-hour it would save.*

**THE SPEC, and the script already contains its own template:**

1. **Widen `POPULATION_ROOTS` to include `docs/campaigns`.** The identical widening was done once before — `("verification",)` → `("verification", "cases")` — under docket item **D471.2**.
2. **Carry an ADVERSE control, exactly as D471.2 did.** `:569-579` plants a grader, asserts it is found and judged, **then re-walks with the OLD roots and FAILS THE SELFTEST IF THE OLD WALK WOULD ALSO HAVE FOUND IT** — *"the D471.2 control is adverse (old walk missed it)."* **That is a planted-alternative control on a widening (`§2o`), already written, in the same file, and it must be replicated for the new root or the widening is unevidenced.**
3. **Add the empty-input arm (`§2p.2`):** a repository state in which the walk finds **zero** comparators must **refuse**, not report clean.
4. **And a positive control (`§2p.3(e)`):** after the widening, a correctly-frozen comparator under `docs/campaigns/` must still be judged **FROZEN** — the widening must not refuse everything it newly sees.

**REFERRED to the chief for the cfd tooling line**, with the note that **step 2's template is 11 lines away from the code that needs it.**

### §2q.1 A STOP CONDITION MUST NAME ITS OWN MECHANICAL CONSEQUENCES

heat-transfer recorded, against itself, a stop-condition defect: **a literal reading required a self-referential recorder to be BROKEN in order for the condition to PASS.** Their fix is right and generalises:

> **RULED: A STOP CONDITION NAMES IN ADVANCE THE MECHANICAL CONSEQUENCES THAT DO NOT COUNT AS DRIFT.** A condition of the form *"nothing changes"* is false the moment the recorder writes its own record, so it must enumerate its own footprint or it can be satisfied only by failing to run.

| item | outcome |
|---|---|
| `§6` `G-RATIO` question | **RULED on its own merits** — `NOT A RESULT`, on **two independent grounds** |
| the ground they did not raise | with `iter_change = 0.0` the branch returns ∞ **regardless of the numerator** — the pass is not attributable to the ladder at all |
| the general clause | **`§2d.10` — a licensing gate is `NOT A RESULT` whenever what it licenses is** |
| repair | **not petitioned, not ordered** — the law is stated; the change is heat-transfer's |
| **`§2p.3(e)`** | **every restrictive repair carries a POSITIVE control through the production path** |
| **against myself** | **`R3` and `R5` were granted on "restrictive → easy"; each now owes that control** ⚠ **[STRUCK IN PLACE 2026-09-03, v1.55 `§2p.11` — this row read "`R3`, `R5`, `R6`". `R6` WAS REFUSED at `:4523`/`:4540`/`:4567` and was never granted; the debt is DISCHARGED for both survivors at v1.50 `§2p.10`. This is the site `§2p.9`'s strike NAMED and the first in-place pass MISSED.]** |
| `check_comparator_freeze.py` | **`POPULATION_ROOTS = ("verification","cases")`; `docs/campaigns` ZERO hits — T23G2 has ZERO freeze coverage** |
| whose defect | **`§2p` in the constitutional enforcement instrument**, made permanent by my own `§2d.9.2` |
| my call | **SPEC, not amend** — `scripts/` is outside scope; a routing offering the choice does not widen it (rule 9) |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |

---

## Amendment — v1.43, 2026-09-03 — **[SANAA-RULED] §2r TWO-TIER MESH ADMISSIBILITY BINDS CERTIFICATE ISSUANCE · §2s FREEZE ENFORCEMENT AT THE CHOKE POINT, AND THE INSTRUCTION AS WORDED CANNOT BE IMPLEMENTED BECAUSE THE DAEMON HAS NO GRADING STEP · §2t THE $1,000 LADDER ENVELOPE. THREE OF HER RULINGS IN ONE DAY, AND TWO OF THEM MEET A MECHANISM SHE WAS NOT SHOWN.**

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered, inserted or deleted. **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label is created, moved or retired by this team; nothing is re-graded.** **This amendment does not RULE — it CARRIES three rulings of Sanaa's into the instrument that binds them**, tagged `[SANAA-RULED]`, so no later reader mistakes her authority for this supervisor's. Where a mechanic below and her text disagree, **her text governs and the mechanic is the defect.**

**⚠ THE MASTHEAD OF THIS FILE IS STALE AND HAS BEEN FOR THIRTY-TWO VERSIONS.** Line 3 reads *"Version 1.10, dated 2026-08-22."* The authoritative version is the **highest amendment number**, derived not recalled: `grep -oE '^## Amendment — v1\.[0-9]+' | grep -oE '[0-9]+$' | sort -n | tail -1` → **42**, so this block is **v1.43**. The masthead is **not edited** (rule 6); it is disclosed here, and a reader who takes line 3 as the version is reading a number thirty-two amendments out of date. **Same defect class as CLAUDE.md rule 11: the maximum, never the first thing that looks like a version.**

---

### §2r — TWO-TIER MESH ADMISSIBILITY [SANAA-RULED]

Her ruling, 2026-09-03 ~17:30Z, recorded verbatim at `etc/sessions/2026-09-03T1730Z_sanaa_mesh_standard_and_freeze_enforcement.md`, quoted in full because a paraphrase of a ruling is not the ruling:

> **Two-tier mesh standard — this resolves the R12 question. The 70° gate is our generation standard: every mesh the lab builds must meet it, unchanged. Committee grids are a different object: they exist for comparability with the workshop's own results, where every participant used the same grids. Ruling: committee grids are admissible for validation-against-workshop-data cases without meeting the 70° gate, under these conditions: (a) their measured quality (max non-orthogonality, skewness, the works) is reported on the certificate, not gated; (b) solver-side mitigations (non-orthogonal corrector counts, relaxation) are registered before running; (c) the numerical-uncertainty band still comes from the grid family; (d) the certificate names the grid as "workshop committee family, quality as published" in the what-was-checked section. A full certificate IS reachable this way — a certificate's honesty is disclosure and verification, not our internal birth standard. What committee grids can never do is certify our meshing capability — that stays on in-house grids under 70°.**

**Why it reaches THIS charter.** Her condition (d) is a condition on a **certificate**, and this charter is what binds every number reaching a certificate (its own opening scope sentence). A mesh standard can say what a mesh is; only this charter can refuse to issue.

#### §2r.1 THE ISSUANCE CLAUSE

> **RULED — `§2r`, [SANAA-RULED]. A CERTIFICATE MAY ISSUE ON A MESH THAT DOES NOT MEET THE 70° NON-ORTHOGONALITY GATE, IF AND ONLY IF that mesh is a DECLARED TIER-2 workshop committee grid and ALL of conditions (0) and (a)–(d) are satisfied AND CHECKED. Such a certificate is a FULL certificate — not capped, not chipped down, not confined to a model-form band.** *Her ground, verbatim: "a certificate's honesty is disclosure and verification, not our internal birth standard."*
>
> **A mesh over 70° that is NOT a declared Tier-2 grid is unchanged in every respect:** a generation-standard breach, the numerical channel carries it, the fidelity chip is capped.

**Tier 2 is entered by DECLARATION AT PRE-REGISTRATION AND NEVER AFTERWARDS.** A grid promoted to Tier 2 *after* its quality was measured is the shape rule 2 exists to forbid — the exemption would have been chosen to fit the answer. **Condition (0), added by this clause because without it "committee grid" is self-declared and the exemption is unbounded:** the grid must be **published and distributed by the committee itself**, byte-unmodified apart from format conversion, with the sha-256 of both the distributed file and the converted mesh recorded in the frozen registration, and the case must be a validation against that workshop's own data. **A grid produced by running a public generator with a namelist this lab modified is NOT a committee grid** — it is a lab-built mesh and Tier 1 governs it.

**"Checked" is operative, not decorative.** Under `§2k` a number with no artifact is not a measurement; under this clause **a condition with no check is not a condition.**

#### §2r.2 THE CONSEQUENCE OF FAILING A LIMB — **AND I CORRECT MY OWN TEAM'S DRAFT HERE**

The draft this clause was built from ruled that a run completed on a grid failing any limb is **`NOT A RESULT`**, and referred the question of which `§2n` cause class applies. **Both halves are wrong and I strike them before they land.**

> **RULED: A TIER-2 LIMB FAILURE REFUSES THE CERTIFICATE. IT DOES NOT VOID THE PHYSICS.** The run does not become `NOT A RESULT`; it **reverts to Tier-1 treatment** — a generation-standard breach, the numerical channel carrying it, the fidelity chip capped, and no validated force claimed from that mesh. **A disclosure this lab failed to make is a statement about our record, not about what the solver computed.**

**This is Sanaa's own universal rule applied where it points:** *bookkeeping never voids physics* (2026-08-26). A missing registration heading, an absent substring, a sha that was never recorded — these are bookkeeping. **And the correction dissolves the referral rather than answering it: no `§2n` cause class is needed, because there is no `NOT A RESULT` to classify.** `§2n`'s set stays closed and no ninth class is invented.

#### §2r.3 THE CEILING THAT DOES NOT MOVE

> **RULED — [SANAA-RULED], and it takes no exception:** *"What committee grids can never do is certify our meshing capability — that stays on in-house grids under 70°."*
>
> **No Tier-2 grid, and no result obtained on one, is admissible as evidence of this lab's meshing capability** — not in the capability grid, not in a credentials entry, not in a certificate's capability claim, not in a report upward. **A Tier-2 certificate certifies the PHYSICS this lab computed and certifies NOTHING about the MESH this lab did not build.** Faithful import is an import capability, not a meshing capability.

#### §2r.4 **⚠⚠ THE RULING CANNOT BE EXERCISED TODAY, AND THE OBSTACLE IS A MECHANISM SHE WAS NOT SHOWN. `[MEASURED BY ME AT SOURCE]`**

**Every committee grid on this box is refused entry to a case BEFORE any of her conditions is ever evaluated, and the refusal fires on SKEWNESS.**

`sdk/chief_engineer/mesh_certificate.py:44` — `ACCEPTED_VERDICTS = ("clean", "flagged")`. Its `_HARD_ERRORS` tuple at `:47-57` fires on the literal `***Max skewness`. **All three DPW5 committee grids print exactly that**, and I read the three logs myself rather than on relay:

| grid | `***Max skewness` | non-orthogonality Max | checkMesh's own verdict line |
|---|---|---|---|
| `DPW5_hex_checkMesh.log` | **`14.0594`** `:109`, 466 highly-skew faces | **`89.7134`** `:103` | **`Non-orthogonality check OK.`** `:105` |
| `DPW5_prism_checkMesh.log` | **`6.31513`** `:107`, 89 faces | **`89.9441`** `:101` | **`Non-orthogonality check OK.`** `:103` |
| `DPW5_hybrid_checkMesh.log` | **`6.31513`** `:107`, 89 faces | **`89.9985`** `:101` | **`Non-orthogonality check OK.`** `:103` |

So each is born **`broken`** and the admission function refuses it entry. **Her condition (a) names skewness in her own parenthesis and says quality is REPORTED, NOT GATED — but she was not shown this code path, and extending her ruling onto a mechanism she did not name is exactly the permission laundering rule 9 forbids.** **REFERRED TO HER, not read across.**

**⚠ AND THE SAME THREE LOGS CARRY A SECOND FINDING, LIVE, ON THE EXACT GRIDS THIS RULING GOVERNS.** `checkMesh` prints **`Non-orthogonality check OK.`** at **89.71°, 89.94° and 89.9985°** — within hundredths of degenerate. **A reader taking checkMesh's verdict line instead of its number would record all three as passing.** This is the standing rule to read the reported maximum and never the verdict line, and here it is firing on production artifacts rather than in a worked example.

**A THIRD OBSTACLE, and it is the one that would produce a FALSE MEASUREMENT rather than a refusal.** `sdk/chief_engineer/certificate.py:936-999` renders non-orthogonality as `"{v}° vs {gate}° gate"` with a `pass`/`caveat` verdict and offers **no suppression**; the only lever would, if raised to force a pass, **print a comparison against a gate that does not apply.** Condition (a) demands *reported, not gated*. **A certificate that prints `89.71° vs 70° gate — pass` has laundered the exemption into a false measurement and is worse than one that fails.** A "reported, not gated" mode is required and **does not exist**.

> **RULED: NO TIER-2 CERTIFICATE MAY ISSUE UNTIL THE THREE OBSTACLES ABOVE ARE CLEARED.** `§2r` is **DOCUMENTARY FROM TODAY**, and saying so is not a defect in the clause — **it is the clause refusing to pretend.** No grid on this box is a declared Tier-2 grid; **grids admitted: 0; certificates issued: 0.**

**`sdk/` and `docs/standards/` are OUTSIDE this team's folder scope. I SPEC; I DO NOT AMEND — the same line held at `§2q`, and a routing that offers me the choice does not widen the scope (rule 9).** The chief's session note assigning codification to this team is **the chief's reading, not Sanaa's words**, and it is recorded as such in the capture itself.

---

### §2s — FREEZE ENFORCEMENT AT THE CHOKE POINT [SANAA-RULED]

Her wiring order, 2026-09-03 ~17:30Z, verbatim: **(1)** the queue daemon refuses to grade any run whose comparator's sha does not match its frozen registration — enforcement at the choke point first, primitive is fine; **(2)** coverage measured and reported weekly until it reads full; **(3)** a planted violation proves the enforcer fires through the real path; **(4)** an honest note into the lab record. **No re-grading of past results unless a specific comparator is shown to have moved.**

**The law she is enforcing is ALREADY in this charter and only its wiring is new.** `§2d` already requires: *"Verify the frozen file is the file that ran. Hash the comparator at analysis time against the committed blob. A freeze that is claimed and not checked is a claim about intent."* **Her ruling does not add a rule. It notices that the rule was never wired to anything.**

#### §2s.1 **⚠⚠ THE INSTRUCTION AS WORDED CANNOT BE IMPLEMENTED: THERE IS NO GRADING STEP IN THE DAEMON**

`[MEASURED]` The queue daemon performs exactly one state transition — **queued → launched**. It moves an entry file into `launched/` and never reads a result. **There is no line at which a run "transitions to graded", so a hook placed where the daemon grades would never fire.**

> **RULED: THE HONEST CHOKE POINT IS THE LAUNCH, NOT THE GRADE.** Enforcement attaches to the queue-entry validation that already refuses entries on the live path every tick. A comparator whose bytes disagree with its frozen registration **is refused before its run starts**, which is strictly better than refusing after the compute is spent — and it is the only place in this daemon where a refusal can fire at all.

**This is a correction to her instruction's mechanism, not to her ruling**, and it is put to her as such: the intent — *nothing is graded on an unfrozen comparator* — is served better at launch than at a grading step that does not exist.

#### §2s.2 THE THREE OUTCOMES, AND WHY TWO ARE NOT ENOUGH

The enforcer will constantly meet cases with **no reachable freeze evidence**. *Grade anyway* makes it a **no-op on precisely the population that needs it** — `§2p`'s degenerate path installed at the choke point on day one, and it would pass a repository whose every comparator had been rewritten this morning. *Refuse* **halts the lab**, and an enforcer that blocks good work is switched off within a day.

> **RULED — THREE OUTCOMES:**
> - **`MISMATCH` → REFUSE**, unconditionally, from the day the hook lands.
> - **`MATCH` → PROCEED.**
> - **`UNREACHABLE` → PROCEED, AND RECORD THE UNREACHABILITY** in a countable field. Never silently ignored, never confused with a match.
>
> **AND THE THIRD OUTCOME CARRIES A SUNSET OR IT IS PERMANENT.** A report-only state with no end date is **documentary enforcement in a second costume** — the very thing being removed. **At the sunset, `UNREACHABLE` becomes `REFUSE`.** The date is Sanaa's; the recommendation is her own limb-2 target, because **the condition she set as the goal is the condition that makes the third outcome unnecessary.**

#### §2s.3 **⚠ A REFUSAL ON `UNFROZEN` ALONE WOULD REFUSE A LAWFULLY REPAIRED COMPARATOR**

`§2d.1`'s four-condition repair exception exists **because this instrument's own first pass mis-condemned a comparator that had been lawfully repaired** — and that comparator still reads `UNFROZEN` today.

> **RULED: `UNFROZEN` IS NOT `ILLEGAL`.** An enforcer keyed on the freeze instrument's `UNFROZEN` status alone will refuse every comparator lawfully repaired under `§2d.1`. **The enforcement quantity is the SHA MISMATCH against the frozen registration — a byte comparison — and not the freeze instrument's timestamp verdict.** The two answer different questions and only the first is what she ordered.

#### §2s.4 COVERAGE — **`REACHABILITY, NOT INNOCENCE`**, AND THE TARGET FIGURE IS NOT ONE THIS LAB EMITS

> **RULED:** a row carrying a judged freeze verdict is **COVERED**, *including* a failing one. A row reported unjudged — no marker, ambiguous scope, undated marker — is **NOT COVERED AT ALL**. **A single number mixing them can be improved BY HIDING VIOLATIONS**, which is the one way this metric could leave the lab worse off than no metric. **Two axes, side by side, never collapsed:** coverage = judged / total; compliance = frozen / judged.

**`[MEASURED BY ME, whole-repo run of the freeze instrument, re-derived rather than relayed]` — and it corrects the figure this program was briefed on:**

| status | rows |
|---|---|
| `NO-MARKERS` | **144** |
| `FROZEN` | **27** |
| `UNFROZEN` | **10** |
| `AMBIGUOUS-SCOPE` | **5** |
| `AMENDED_AFTER` | **3** |
| `UNCOMMITTED` · `MODIFIED_AFTER_COMMIT` · `UNDATED-MARKER` | **0 · 0 · 0** |
| **total walked** | **189** |
| **JUDGED (covered)** | **40 of 189** |

**The `145` this program was briefed on is wrong; the measured figure is `144`, and neither is the denominator.** Coverage today is **40 / 189**, not anything over 145. **The target as stated corresponds to no figure this instrument emits, and it is referred to Sanaa rather than silently reinterpreted.**

#### §2s.5 **⚠ THE REPAIR THE OBVIOUS DIAGNOSIS WOULD HAVE BOUGHT REACHES 9 ROWS OF 144**

The instrument pairs a comparator with completion markers found by **one listing of the comparator's own directory**. The obvious diagnosis is that cross-directory pairing is the coverage hole. **It is not the main one, and measuring before building is what established that.**

`[MEASURED]` **All completion markers in this repository live in three run trees. Zero exist under `cases/`, under `docs/campaigns/`, or in any other run subtree.** Of the 144 unjudged rows: **9** have evidence a pairing repair could reach (5 cross-directory, 4 also cross-convention); **~135 have no completion-marker evidence anywhere in the repository at all** — real graders in campaigns that never adopted the completion-marker convention.

> **RULED: THE COVERAGE HOLE IS NOT PRINCIPALLY A PAIRING DEFECT — IT IS THAT FOUR OF SIX TEAMS NEVER ADOPTED THE EVIDENCE CONVENTION THE FREEZE TEST READS.** A pairing repair is worth building and **converts 9 rows**. Full coverage requires a completion convention those campaigns do not have. **A program that had built the association machinery first would have spent its effort on 6 % of the gap and reported a repair.**

**This is `§2p.5`/`§2p.6.1`'s error refused in advance rather than booked afterwards**, and it is the only reason this clause states a proportion instead of a plan.

#### §2s.6 MARKER ASSOCIATION — THE PRINCIPLE, FOR WHEN THE 9 ARE REPAIRED

> **RULED: ASSOCIATION IS DECLARED, NEVER INFERRED FROM A POOL.** Pooling every marker in reach and letting the source-name scope sort it out is **refused**: the failure mode is a **false `UNFROZEN`** — a false accusation against a team which, at the choke point, becomes **a refusal to launch a sound run**. A declaration is accepted from **the frozen registration first** (it cannot move after first compute), **the comparator's own source second**; **if both exist and DISAGREE, REFUSE — never choose.** The declared tree must **also** carry a marker named by the comparator's own source: **two independent limbs, and the source-name limb is the one that cannot be aimed at a convenient tree.**

**The residual hole, named rather than papered over:** a comparator committed early carrying a declaration that points at a tree populated later. The two-limb requirement is a **mitigation, not a proof.**

#### §2s.7 THE ENFORCER IS AN INSTRUMENT (`§2j`, `§2o`, `§2p`)

Her step (3) is already this charter's `§2j` generalised — *no instrument grades anything until the demonstration is an artefact, driven through the real path, with both limbs.* Required, before any enforcement verdict is believed: **the planted mismatch REFUSES**; **the positive control still PROCEEDS** (`§2p.3(e)` — a refuser that refuses everything is indistinguishable, from its verdicts alone, from a correct one); a **wrong-object control** (a different file moved, the comparator's sha untouched) still proceeds, proving the enforcer is keyed on the right artifact; and the **empty-input arm** does not silently pass. All four drive the **production** path, not a copy (`§2p.3(d)`). **`§2j.4`'s non-retroactivity is the existing charter basis for her "no re-grading of past results", so that instruction needs no new clause.**

#### §2s.8 THE HONEST NOTE — **TWO DATES, AND THE GAP IS THE FINDING**

> **Freeze enforcement was documentary until the day the enforcer was wired to the live path. The enforcing instrument existed from 2026-08-19 — but nothing executable invoked it, so for the fifteen days between, this lab held a freeze enforcer it never ran, and it fired zero times. Every certificate issued before the wiring date relied on process discipline, not tooling. No recorded verdict is withdrawn on this account; a specific comparator shown to have moved is a separate matter and is handled on its own facts.**

**`[MEASURED]` the instrument has three commits, the first 2026-08-19; four independent searches — tracked sources, whole worktree, crontab and system units, git hooks — find no executable invocation of it.** *"We had no tool"* and *"we had the tool and never wired it in"* are different admissions and **the second is the one that generalises.** **It is also this team's own defect:** `§2q` is where this team specced that instrument's widening and correctly recorded `scripts/` as out of its scope — **which is how an instrument comes to be owned by nobody at the moment it needs wiring.**

---

### §2t — THE $1,000 LADDER ENVELOPE, REGISTERED AS LAW [SANAA-RULED]

Her directive, 2026-09-03 ~18:00Z, verbatim at `etc/sessions/2026-09-03T1800Z_sanaa_compute_envelope.md`: **one standing envelope of $1,000 for the benchmark ladder (Rungs 0–3), spendable without returning to her; the per-case dollar approval loop abolished inside it.** What does **not** change, in her words: *"every run still registers its cost estimate before launch, still carries a hard per-run cap (set by the team at ~3× its own estimate, not by me), still reports predicted-vs-actual, and still names waste. **The estimate is an instrument, not a permission slip.**"* Escalation to her only for: **a single run projected over $150**, **the envelope reaching 80 %**, or **a third attempt at something that already failed twice** — and, her instruction, **each escalation is preceded by a check that the exceedance is not itself an arithmetic error.**

> **RULED — `§2t`, [SANAA-RULED]: THE ENVELOPE REMOVES THE APPROVAL LOOP. IT REMOVES NOTHING ELSE.** Every spend inside it still requires a **frozen, costed pre-registration** committed before the solver starts (`CLAUDE.md` rule 2) and a **costed estimate in the lab's measured unit** with an honest `cost_basis` (rule 12). **An envelope is a budget, not a dispensation from the freeze**, and no reading of it licenses a run whose gate was chosen after the answer.
>
> **AND THE ESTIMATE'S STATUS IS SHARPENED BY HER OWN WORDS, NOT WEAKENED.** *"The estimate is an instrument, not a permission slip."* An instrument that no longer gates anything is the exact object `§2p` was written about: **now that the estimate opens no approval door, the only thing that keeps it honest is the predicted-versus-actual comparison it is measured against.** That comparison is therefore **not optional bookkeeping inside the envelope — it is what the envelope leaves standing in place of the approval.**
>
> **HER ARITHMETIC SELF-CHECK IS ADOPTED AS A REFUSAL, NOT A REMINDER:** an escalation whose triggering figure has not been re-derived is **withdrawn, not sent**. A false exceedance spends her attention, which is the one budget this lab cannot meter.

---

| item | outcome |
|---|---|
| authority | **[SANAA-RULED]** ×3 — 2026-09-03 ~17:30Z (mesh, freeze) and ~18:00Z (envelope), quoted verbatim |
| `§2r` mesh | **full certificate REACHABLE on a Tier-2 committee grid**; Tier-1 70° generation gate **unchanged**; capability ceiling **absolute** |
| **correction to my own team's draft** | a Tier-2 limb failure **refuses the certificate, does NOT void the physics** — *bookkeeping never voids physics*; **the `§2n` referral is DISSOLVED, not answered** |
| `§2r` exercisability | **DOCUMENTARY — 3 obstacles `[MEASURED]`**: skewness quarantine before her conditions are reached; checkMesh printing `OK` at 89.7–89.9985°; no *reported-not-gated* mode |
| grids admitted · certificates issued | **0 · 0** |
| `§2s` her instruction's mechanism | **CORRECTED — the daemon has NO grading step**; the honest choke point is the **launch** |
| `§2s` the three outcomes | MISMATCH refuses · MATCH proceeds · **UNREACHABLE proceeds, is counted, and SUNSETS** |
| `§2s` the trap | **`UNFROZEN` ≠ ILLEGAL** — that key refuses every `§2d.1` lawful repair |
| `§2s` coverage `[MEASURED]` | **40 judged of 189** · `144` NO-MARKERS · **the briefed `145` is WRONG**; the target matches no emitted figure — **referred, not reinterpreted** |
| `§2s` the diagnosis that would have been wrong | a pairing repair reaches **9 of 144**; **~135 campaigns never adopted the evidence convention** |
| `§2s` the honest note | **two dates** — instrument from **2026-08-19**, **zero invocations in fifteen days** |
| `§2t` envelope | **approval loop removed; rule 2 and rule 12 UNTOUCHED**; the estimate keeps its meaning only through predicted-vs-actual |
| scope held | `sdk/`, `scripts/`, `docs/standards/` **specced, NOT amended** — a routing offering the choice does not widen scope (rule 9) |
| referrals opened and NOT decided | **4** — the skewness quarantine; the *reported-not-gated* mode; the coverage target figure; the sunset date |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| results re-graded | **0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.44, 2026-09-03 — **§2s.9: I CORRECTED SANAA'S NUMBER AND THE CORRECTION WAS WRONG. BOTH FIGURES WERE RIGHT AT DIFFERENT MOMENTS — THE DENOMINATOR IS NOT A CONSTANT, IT GREW DURING THE TASK THAT MEASURED IT, AND HER STOP CONDITION THEREFORE RECEDES AS THE LAB WORKS. AND THE INSTRUMENT HER STEP (1) IS ABOUT CONTAINS A FAIL-OPEN THAT ANSWERS `FROZEN` WHEN IT COULD NOT CHECK.**

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered, inserted or deleted; `§2s.4` is **struck in one figure and stands in the rest**, corrected here per rule 6 rather than rewritten above. **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label is created, moved or retired; nothing is re-graded.**

### §2s.9 — **THE CORRECTION RUNS AGAINST MY OWN TEXT, LANDED WITHIN THE HOUR**

`§2s.4`, committed at `fb2d0d39` earlier today, said: *"The `145` this program was briefed on is wrong; the measured figure is `144`."* **That sentence is struck.** It was written from two of my own whole-repo runs, both honest, both reproducible — **and it drew the wrong conclusion from them.**

**WHAT ACTUALLY HAPPENED `[MEASURED, four walks across one afternoon]`:**

| walk | graders | `NO-MARKERS` |
|---|---|---|
| the stopped lane's, before this session | — | **145** |
| mine, twice, mid-session | **189** | **144** |
| the re-walk, minutes later | **190** | **145** |

**One file explains every reading:** `verification/runs/T-family/T25R6a_C5_OUTER_runs/grade_t25R6a.py`, landed by another team's lane **between measurements**. **`145` was right when it was measured, `144` was right when I measured it, and `145` is right again now.** Nothing was miscounted by anybody.

> **STRUCK: *"the briefed 145 is wrong."* IT WAS NOT WRONG. It was a correct reading of a population that has since grown, and I turned a moving quantity into somebody's error.** The measurements were fine; **the inference was mine and it was uncharitable in a direction I would have criticised in another team.**

#### §2s.9.1 THE CONSEQUENCE IS LARGER THAN THE CORRECTION, AND IT CHANGES HER STOP CONDITION

**The coverage denominator is not a constant.** It grew by one grader inside the span of a single task, and **every new grader enters the population at `NO-MARKERS`** — unjudged by construction, because a grader is written before its run has finished.

> **RULED — `§2s.9.1`: A COVERAGE FIGURE IS MEANINGLESS WITHOUT THE COMMIT IT WAS WALKED AT.** The weekly report states its denominator as **"graders walked at commit `<sha>`"**, never as a fixed number. **A stop condition written as a bare count — *"until it reads 145/145"* — names a target that RECEDES as the lab works**, because normal productive work adds graders faster than freeze evidence accrues. **It was already stale when it was written**, through nobody's fault.
>
> **The honest stop condition is a RATIO AND A DIRECTION, not a count:** every grader walked at the reporting sha carries a judged freeze verdict. **Referred to Sanaa in that form**, with the arithmetic above, so she is ruling on a measurement rather than on a number that moved.

**This is `§2q.1` firing on my own clause** — *a stop condition names in advance the mechanical consequences that do not count as drift.* A condition of the form *"until it reads N/N"* is falsified the moment the lab writes its next grader, **so it can be satisfied only by the lab not working.** `§2q.1` was written for exactly this shape and I did not apply it to the metric I was specifying.

**The judged figure is unaffected and remains the honest reading: `40` judged.** `40 of 189` and `40 of 190` are the same finding.

#### §2s.9.2 **⚠⚠ A FAIL-OPEN IN THE SHA COMPARISON HER STEP (1) IS ABOUT — `[VERIFIED BY ME AT SOURCE]`**

`check_comparator_freeze.py:388-403`. `modified` is initialised **`None`** and assigned **only** when three conditions all hold: the `git log` call returned 0, a disk digest exists, and `git cat-file blob` succeeded. The verdict line is then:

```
row["commit_test"] = "MODIFIED_AFTER_COMMIT" if modified else "FROZEN"
```

**`None` is falsy.** So **a comparator whose worktree-versus-blob comparison COULD NOT BE PERFORMED is reported `FROZEN`** — the reassuring answer. **And the row carries no `worktree_differs_from_HEAD` key at all**, because that key is written only inside the successful branch: **from the row alone, "checked and clean" and "never checked" are indistinguishable.**

**⚠ AND THE IRONY IS ON THE FOUR LINES DIRECTLY ABOVE IT, WHICH IS WHY THIS IS A CLASS AND NOT A TYPO.** The comment there explains the comparison is **`INDEX-INDEPENDENT ON PURPOSE`**, because this repository's shared index *"has been observed stale enough to report tracked files as deleted while they sit on disk."* **That reasoning is correct and the design it produced is right.** The care went into defeating one fail-open, and **the very next line folds the failure of that same subprocess into the reassuring verdict.** *A guard can be carefully reasoned in its mechanism and fail-open in its default, and the reasoning is what makes the default invisible.*

**LATENCY RE-MEASURED, NOT INHERITED** `[MEASURED at today's population, not read off the prior audit]`: judged rows **40**; judged rows whose byte comparison never ran **0**; rows reading `FROZEN` on an uncomputed comparison **0**; comparators whose worktree differs from HEAD **0**. **The latent ruling holds today.**

> **RULED — `§2s.9.2`: THE ENFORCER DOES NOT ROUTE THROUGH `commit_test`.** The enforcement quantity is an **independently computed sha of the comparator's bytes**, compared against the pin derived from the frozen registration by the repository itself. **An enforcer that consumes this instrument's `commit_test` inherits a branch that answers `FROZEN` when it could not check** — and the latency argument **expires the instant that verdict gates anything**, because latency is a statement about today's population and an enforcer is a statement about every future one.
>
> **AND THE LATENCY IS NOT THE DEFENCE.** *A fail-open that is currently unexploited is a fail-open with a good week.* It is recorded here as a live constraint on the wiring, not as a closed item.

**This is `§2p` in this team's own instrument for the second time in two days**, after `§2q` found the population blindness in the same file. **Both were found by other teams reading my code, which is the argument for the cross-team audit mandate rather than against it.**

#### §2s.9.3 A METHOD NOTE, BECAUSE IT NEARLY PUT A FALSE ALARM ON THE RECORD

A report reached me that `git status` read **`MM`** on this charter — the index apparently holding a third version, *"somebody's unfinished work sitting where a bare commit would sweep it up."* **REFUTED, by comparing content rather than re-reading status:** the index blob, the `HEAD` blob and the worktree blob are **all `7cb52493`**, and that is byte-identical to what `fb2d0d39` committed. **There is no third version and there never was.**

The reading was taken while HEAD was moving under concurrent commits. **`git status` is a comparison against an index that a concurrent private-index commit leaves stale by design**, and this lab has recorded it reporting dirty files clean and tracked files deleted. **The instrument in this very file already knows it** — that is what the `INDEX-INDEPENDENT ON PURPOSE` comment in `§2s.9.2` is defending against.

> **RULED: AN INDEX-STATE ALARM IS SETTLED BY COMPARING BLOBS, NEVER BY RE-READING `git status`.** `git ls-files -s`, `git rev-parse HEAD:<path>` and `git hash-object <path>` answer with content; `status` answers with an index. **A hazard report that rests on `status` alone is not yet a finding**, and inspecting it costs three commands.

| item | outcome |
|---|---|
| `§2s.4`'s *"the briefed 145 is wrong"* | **STRUCK — my overreach.** 145, 144 and 145 are all correct readings of a **growing** population |
| the file that explains all four walks | `grade_t25R6a.py`, landed by another team's lane mid-measurement |
| the larger consequence | **`§2s.9.1` — a coverage figure is meaningless without its walked commit**; a bare-count stop condition **recedes as the lab works** |
| whose clause catches it | **`§2q.1`, my own** — a stop condition must name its own mechanical consequences; I did not apply it to the metric I was specifying |
| judged figure | **40 — unaffected**; `40/189` and `40/190` are one finding |
| **`§2s.9.2` fail-open** | `commit_test` answers **`FROZEN` when the byte comparison could not run**; the disclosure key is absent, so *never checked* and *checked clean* are indistinguishable |
| latency | **re-measured at today's population: 0 rows affected** — and latency is **not** the defence |
| wiring constraint | **the enforcer computes its own sha; it does NOT consume `commit_test`** |
| `§2p` specimens in this team's own instrument | **2 in two days**, both found by other teams reading my code |
| the `MM` alarm | **REFUTED** — index, HEAD and worktree all `7cb52493`; settled by blobs, not by `status` |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| results re-graded | **0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.45, 2026-09-03 — **§2d.11 THE SPINE PETITION RULED ITEM BY ITEM: A GRANTED, B GRANTED ON A GROUND THE PETITION DID NOT LEAD WITH, C RECORDED AS A NEW RULE-2 SPECIMEN. THE T3 CONTROL VIOLATES `CLAUDE.md` RULE 3 INSIDE A RULE-3 CONTROL — IT CAN PASS WITHOUT EVER SEEING ITS PLANT. · §2u A WITNESS IN AN UNCOMMITTED FILE IS NOT A WITNESS.**

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered, inserted or deleted. **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label is created, moved or retired by this ruling; nothing is re-graded; no verdict is withdrawn.**

**RULED AT SOURCE.** `docs/campaigns/T-family/SPINE_2D1_GRADING_PATH_PETITION.md` (344 lines) and `docs/campaigns/T-family/T5c_PREREGISTRATION.md` (318 lines) were **read in full by me**, and every load-bearing line was **re-derived from the files themselves** rather than taken from the petition's summary or the routing that delivered it. **That discipline changed this ruling twice** — once against the petitioner (§2d.11.1's added condition) and once **in their favour** (§2d.11.2, where the source carries a far stronger case than the summary put).

### §2d.11.0 WHAT THE PETITION DID BEFORE IT ARGUED ANYTHING, AND IT SHOULD BE THE STANDARD

**It conceded the fact that would have sunk it.** §2 opens by proving the `UNFROZEN` flag against `analyse_t3_rff.py` is a **TRUE POSITIVE** — *"and proved it after being told the opposite"* — retracting an earlier internal reading that had already been carried upward with confidence. It then establishes the sha-witness route is **chronologically dead in every format**, so no repair of presentation could rescue it.

**And §3.5 discloses, before any ruling, that granting Item A most likely buys a `NOT A RESULT` rather than a `PASS`** — `R_ff` sits **4.34× over** the iterative-convergence tolerance, so rule 5 step (a) fires before any triple is consulted. **They said so rather than let me find it.**

> **RECORDED AS THE REFERENCE SHAPE FOR A PETITION: concede the worst fact first, disclose the expected outcome against your own interest, and cite every line re-read at the moment of writing.** This petition also **corrected two citations it had been handed** in passing. *A petition that tells me what is wrong with itself is one I can rule on quickly; one that does not, I have to audit before I can read.*

### §2d.11.1 ITEM A — **GRANTED.** The rule-3 control violates `CLAUDE.md` rule 3, and I verified the mechanism in two adjacent lines

`[VERIFIED BY ME AT SOURCE]` `analyse_t3.py:81` — `PLANT = 1.234e-03`. `:326-327`:

```
seen = c.get("max_change", 0.0)
return dict(passed=(seen >= PLANT - 1e-15), planted=PLANT,
```

**`seen` is the reader's MAXIMUM CHANGE OVER ALL CELLS. The predicate never asks whether that maximum is AT THE PLANTED CELL.** `CLAUDE.md` rule 3 requires a comparator to *"plant a known perturbation, read it back from disk, and REFUSE if the reader cannot see it."*

> **RULED: THIS PREDICATE DOES NOT READ BACK THE PLANT. It reads back the largest change anywhere and compares its MAGNITUDE to the plant's. On a case in a limit cycle that is a real physical change at a different cell, and the control then certifies the reader on evidence the reader did not produce from the plant. That is a rule-3 violation INSIDE a rule-3 control**, and the petition's measurement shows it firing: on `R_c` the predicate returned **`True`** on a **2.47 K** change while the planted cell was **never the argmax** — clearing a 1.234e-03 K plant by a factor of ~2000 **without seeing it**.

**The other limb is arithmetic and equally decisive.** The predicate demands recovery to **`1e-15` absolute** on a difference of two ~300 K doubles, where one ulp of 300.0 is **6.661e-14** — **a tolerance about 1/66th of one ulp of its own operands.** **Unsatisfiable by construction**, not strict. It is a threshold expressed in a unit the arithmetic cannot deliver.

**The four `§2d.1` conditions, assessed by me:**

| condition | ruling |
|---|---|
| **(1) demonstrable error, not preference** | **MET, twice over.** Both limbs are arithmetic, neither is taste. The fail-open is the graver: **a control that can pass without seeing its own plant certifies nothing, silently.** |
| **(2) independent instrument** | **MET, in its strongest form.** IEEE-754 ulp arithmetic grades nothing and carries no verdict; and the fail-open was found on **`R_c`, a case not even in the fourth-level ladder, whose verdict was never at issue.** A defect visible on a case nobody was arguing about is the shape `§2o` was written to prefer. |
| **(3) disclosed and quantified** | **MET.** Both probes committed and runnable at a repository path, not a scratch path. |
| **(4) pre-repair values recorded** | **MET, trivially — and this is the cleanest limb.** The pre-repair state is a **refusal, not a value**; `gate_t3_rff.json` was never written; **nothing any record currently asserts can move.** |

**ON §3.5's SELF-DISCLOSED EROSION OF §3.3 — IT DOES NOT DEFEAT THE GRANT, AND THE DISTINCTION MATTERS.** They now anticipate the **verdict LABEL** while knowing no graded **VALUE**. Rule 2's evidentiary content is that **the gate could not have been chosen to fit the answer**, and the answer a gate fits is a **value against a threshold**. **What is repaired here is the rule-3 CONTROL's predicate — which decides whether the READER is trustworthy, not whether the physics passes.** Knowing `R_ff` is `NOT_CONVERGED` tells you **nothing** about whether the reader can recover a 1.234e-03 K plant. **The knowledge is orthogonal to the repaired quantity, so prediction-first is intact.** *Disclosing it anyway was right, and it is why I could rule instead of investigate.*

**GRANTED, on five binding conditions:**

1. **Successor module only.** `analyse_t3.py` and `analyse_t3_rff.py` are **frozen and untouched** (rule 6).
2. **The successor's registration is COMMITTED before any grading run** — the commit **exists**, not intended (`SUPERVISION_CHARTER` §3 check 4).
3. **`§2p.3(e)` BOTH LIMBS, through the PRODUCTION path** (`§2p.3(d)`), not a copy: the repaired predicate must **still refuse** something — their registered `+200 ulp` refusal arm is exactly right — **and still pass** a case constructed to deserve it. **A repair that makes an unsatisfiable control satisfiable is PERMISSIVE in direction, and permissive repairs get the strictest showing.**
4. **⚠ THE TOLERANCE IS COMPUTED IN ULP OF THE OPERANDS, NEVER HARDCODED AS AN "EQUIVALENT" CONSTANT.** A constant chosen today to equal *n* ulp of 300 K is **wrong at any other field magnitude**, and it would reintroduce the exact defect being repaired in a form that looks repaired. **This is `§2p.5`'s rule — key on the quantity, never on its textual form** — and it is a condition of the grant, not advice.
5. **THE GRANT LICENSES NO VERDICT.** Rule 5 step (a) is untouched: `R_ff` at **4.34×** tolerance is `NOT_CONVERGED` → **`NOT A RESULT`**, and the gate may only turn a `PASS`/`GATE FAIL` **into** `NOT A RESULT`, never the reverse. **Nobody may read this grant as authorising a `PASS`.**

### §2d.11.2 ITEM B — **GRANTED, ON A GROUND THE PETITION DID NOT LEAD WITH**

**I nearly refused this one, and reading the source rather than the summary is the only reason I did not.** The petition argues B mostly on **process** — already frozen, thresholds byte-identical, refused the loosening alternative, registered its own stopping line. **Those are good facts about conduct and none of them establishes a demonstrable ERROR**, which is what `§2d.1`(1) requires. A point maximum replaced by an area average is, on its face, **a change in what is measured** — and its direction is **PERMISSIVE**: the average clears where the maximum fired.

**The frozen registration carries the argument the petition buried** `[READ BY ME AT SOURCE, T5c_PREREGISTRATION.md §2, §7]`:

- the point maximum's **observed order is 0.52–0.54** against the ladder's design **0.99–1.04**;
- on **`roof` the maximum is NON-MONOTONE under refinement** (p = **−0.074**);
- the MAX margin **climbs** 0.7316 → 0.9253 → 1.1550 and fires, while the average margin is **flat** 0.3770 → 0.3986 → 0.4213.

> **RULED: A LADDER-CONSISTENCY CLAUSE IS A CLAIM ABOUT HOW RESOLUTION SCALES UNDER REFINEMENT, AND A STATISTIC THAT INCREASES UNDER REFINEMENT CANNOT ESTIMATE IT.** That is a **demonstrable error in the ESTIMATOR**, not a preference about strictness — and it is the ground on which Item B is granted. **Condition (1) MET.** Condition (2) is met in the same strong form as Item A: **`roof` is not the wall that fired**, so the defect is visible where no verdict was at issue.

**AND THE SPLIT IS WHAT MAKES IT LEGAL, WHICH THE PETITION SHOULD HAVE LED WITH.** The **sublayer bound stays on the point maximum** (`YPLUS_MAX 5.0`, never breached — max anywhere 3.804350). **A point maximum is the CORRECT statistic for "was the sublayer ever violated" and the WRONG one for "how does resolution scale."** T5c keeps the maximum where the maximum is right and moves it only where it is not, and **reports the maximum beside the average either way.** *That is a repair; wholesale replacement would not have been.*

**Prediction-first is satisfied by measurement, not by assertion:** §4.3 measures the registered walls as **strongly non-uniform** — face areas spanning **16.05:1** on `cube_front` and **8883.48:1** on `floor`/`roof` at the fine level — so the area-weighted statistic is **materially different** from the face-count one, **and the gated value was genuinely not known at freeze.**

**GRANTED, on four binding conditions:**

1. **The `§6` birth arms `Y-1`…`Y-5` PRINT before any row grades.** T5c registered this against itself; **I make it binding rather than self-imposed.**
2. **`Y-3`'s refusal must be armed and must fire as designed** — refusing when area-weighting and face-count agree within 1 % rather than passing vacuously. **That is the anti-vacuity control and the grant rests on it.**
3. **The sublayer bound stays on the point maximum.** A condition of this grant, not a courtesy.
4. **⚠ BECAUSE THE REPAIR IS PERMISSIVE IN OUTCOME, EVERY GRADED ROW PRINTS BOTH STATISTICS** — area average and point maximum, with the maximum's non-monotonicity shown where it occurs. **A reader must be able to see what the old clause would have said, from the row.** `§2e`'s companion principle cuts this way: a discrepancy that **is** computed and then suppressed is worse than one never computed.

**T5c's own §7 stop line at `:287` is hereby discharged:** *"No row of T5c may be graded until verification has ruled on §2d.1."* **Verification has now ruled. The rung is unblocked, subject to the four conditions above.**

**The refusal to spend 451.833 core-min re-running a ladder purely to manufacture a freeze property is CORRECT and is recorded as such.** *A run whose only product is to satisfy a flag is not compliance; it is paying real compute to launder an instrument reading, and rule 12 would require it be named as waste.*

### §2d.11.3 ITEM C — **RECORDED. No repair requested, and none ordered.**

`[VERIFIED BY ME]` `docs/campaigns/T-family/T3c_PREREGISTRATION.md` is **803 lines**; `git ls-files --error-unmatch` returns *"did not match any file(s) known to git"*; `git log` against it returns **nothing**. Its **line 3** reads: **`STATUS: FROZEN BY COMMIT. NOT ENQUEUED. NO COMPARATOR CODE EXISTS YET —`**

> **RULED — a new rule-2 specimen worth naming, because it is not the ordinary failure.** The ordinary failure is a **missing** pre-registration. **This is a pre-registration that ASSERTS ITS OWN FREEZE while sitting in no commit** — and the assertion is the thing that would satisfy a reader who checks the document instead of the repository. **`SUPERVISION_CHARTER` §3 check 4 exists for exactly this: verify the commit EXISTS, not that somebody meant to write one.** A document's claim about its own history is **evidence of intent and zero evidence of freeze.**

**HEAT-TRANSFER'S DECISION NOT TO COMMIT IT IS ENDORSED.** Committing it would land a registered grading path for a rung whose `§2d.1` question was unruled. **That is the right instinct and I record it rather than let it pass unremarked.**

**⚠ ONE CONDITION ON THE EVENTUAL COMMIT, AND IT IS NOT A NIT.** If T3c is committed unchanged, **line 3 becomes true by accident while having been false when written**, and no later reader can tell the difference. **The commit that lands it must strike or date that line honestly** — a document may not carry a false statement about its own history into the record and be cured by the passage of time.

### §2u — **A WITNESS IN AN UNCOMMITTED FILE IS NOT A WITNESS**

The petition found the general rule inside its own specimen and it deserves to be law. `T3c:204` records the **full blob sha1** of `analyse_t3_rff.py` with byte-identity **YES** — and that sha appears in **no file at HEAD**, *because the document holding it was never committed.*

> **RULED — `§2u`: A SHA WITNESS IS A CLAIM MADE BY THE REPOSITORY, NOT BY A FILE. A digest recorded in an artifact that is not committed witnesses nothing, however correct the digest is, because nothing fixes WHEN it was written. The witness and the thing witnessed must both be reachable at `HEAD`, and the witness's commit must precede what it attests.**
>
> The corollary, stated because it is the one that will be argued: **a correct digest in an uncommitted file is not "a witness with a paperwork problem." It is not a witness.** The freeze instrument's `sha_witness()` returning `(None, None)` here is **the right answer, not a limitation.**

| item | outcome |
|---|---|
| ruled at source | both documents read in full; **the discipline changed the ruling twice** — once against the petitioner, once in their favour |
| **Item A** | **GRANTED** on 5 binding conditions |
| Item A's ground | the rule-3 control **can pass without seeing its plant** (`R_c`: `True` on 2.47 K at a different cell) **and** demands `1e-15` where one ulp is `6.661e-14` — **~1/66 ulp, unsatisfiable by construction** |
| §3.5's self-disclosed erosion | **does not defeat the grant** — verdict *label* is not the graded *value*, and the repaired object is the CONTROL, not the gate |
| Item A licenses | **no verdict.** `R_ff` at **4.34×** tolerance is `NOT_CONVERGED` → **`NOT A RESULT`**; rule 5's one direction stands |
| **Item B** | **GRANTED** on 4 binding conditions, **on a ground the petition did not lead with** |
| Item B's ground | **a statistic that is NON-MONOTONE under refinement (`roof`, p = −0.074) cannot estimate how resolution scales** — an estimator error, not a preference |
| what makes B legal | **the SPLIT** — the sublayer bound **stays** on the point maximum; only the ladder clause moves |
| B's direction | **PERMISSIVE in outcome** — hence condition 4: **every row prints BOTH statistics** |
| T5c `:287` stop line | **DISCHARGED — verification has ruled; the rung is unblocked** |
| the refused 451.833 core-min re-run | **CORRECT** — compute spent only to manufacture a freeze property is waste that looks like compliance |
| **Item C** | **RECORDED**; no repair ordered; the eventual commit must **strike or date** the false line 3 |
| new clause | **`§2u` — a witness in an uncommitted file is not a witness** |
| petition conduct | **recorded as the reference shape** — worst fact conceded first, expected outcome disclosed against interest, every line re-read at writing |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| results re-graded · verdicts withdrawn | **0 · 0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.46, 2026-09-03 — **§2v: `§2p` HAS TWO FACES AND THE LAB HAS NOW MEASURED BOTH. AN INSTRUMENT NOBODY INVOKES, AND A REGISTRATION NAMING AN INSTRUMENT THAT DOES NOT EXIST — BOTH PRODUCE A GATE THAT CANNOT FAIL. THE SECOND CLASS IS REAL AND IT IS MUCH SMALLER THAN ITS REFERRAL: 2 CONFIRMED OF 105, WITH FIVE OF NINE FLAGS REFUTED AS FALSE ACCUSATIONS.**

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered, inserted or deleted. **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label is created, moved or retired; nothing is re-graded; no verdict is withdrawn; no repair is ordered on another team.**

### §2v.0 THE UNIFICATION, WHICH IS WORTH MORE THAN EITHER MEASUREMENT

The dafoam team referred a question to this team's cross-team audit mandate: **how many registered gates lab-wide have no implementation?** On the same day, this team established that the lab's **constitutional freeze enforcer exists and nothing executable invokes it.**

> **RULED — `§2v`: THESE ARE ONE DEFECT SEEN FROM TWO SIDES, AND `§2p` ALREADY GOVERNS BOTH.**
>
> - **FACE ONE — THE UNWIRED INSTRUMENT.** The check is written, correct, and reachable by hand; **no code path runs it.** The gate cannot fail because nothing asks it.
> - **FACE TWO — THE UNBUILT REGISTRATION.** The gate is registered, named and frozen; **the grading path contains nothing that evaluates it.** The gate cannot fail because it was never written.
>
> **In both, a rung reports clean and the cleanliness is uninformative.** `§2p.2`'s empty-input test generates both: **feed the guard nothing and see what it says** — face one passes because the guard was never called, face two because there was no guard to call. **A lab that only looks for wrong answers will find neither.**

### §2v.1 THE MEASUREMENT, AND ITS BOUNDS ARE THE POINT

`[MEASURED, static sweep, zero solver compute]` **Population: 393 pre-registration documents**, from which **24 amendments/addenda were excluded** (rule 2: an amendment cannot create a gate) and **2 drafts** (not frozen — and those 2 alone would have inflated the class by **150 %**). **105 gate instances extracted across 20 frozen registrations.**

| | strict | generous |
|---|---|---|
| IMPLEMENTED | 94 | 99 |
| **NOT FOUND (flagged)** | **9** | 4 |
| CANNOT DETERMINE | 2 | 2 |

**EVERY FLAGGED ROW WAS HAND-READ AT SOURCE. Of the 9: TRUE POSITIVES 2 · FALSE ACCUSATIONS 5 · REGISTERED-AS-DISAPPLIED 2.**

> **LOWER BOUND 2, UPPER BOUND 4**, and both apply **only to the 105 extracted instances** — not to the lab.

**FIVE OF NINE FLAGS WERE FALSE, AND EVERY ONE WOULD HAVE BEEN A FINDING AGAINST A TEAM.** `G-MESHFAM` is implemented as a self-check with an exit-2 refusal; `G-TRIM` as a tolerance constant; `G-COLL` in a dedicated module; `G-DONE` as a delegating `require_done()`; `G-GCI` as computed GCI. A sixth, `G-OPT9`, was accused **until the matcher's own trailing word boundary was found to block its suffixed form.**

> **THIS IS THE FINDING, NOT AN ASIDE. A NAIVE SYMBOL MATCH ON THIS QUESTION IS WRONG MORE THAN HALF THE TIME, AND ITS ERRORS ARE FALSE ACCUSATIONS.** Had the raw flag count been published, **five teams would have been told they registered a gate they never wrote.** *An audit instrument whose failure mode is an accusation is held to a higher standard than one whose failure mode is a miss, and this clause exists to say so before the next sweep is built.*

### §2v.2 A FOURTH CLASS THE BINARY FRAMING HAS NO SLOT FOR — **REGISTERED-AS-DISAPPLIED**

Two flagged gates were **declared inapplicable by the registration itself, in advance**: one registered `NOT APPLICABLE` to its rung and restated later, one registered `NOT COMPOSED — publish the reading only`.

> **RULED: A GATE THE FROZEN REGISTRATION DISAPPLIES IN ADVANCE IS NOT AN UNIMPLEMENTED GATE. It is a gate correctly not built, and its absence from the grading path is COMPLIANCE.** Any sweep of this class **carries a `REGISTERED-AS-DISAPPLIED` verdict or it over-reports by roughly 20 %** on this population. **A registration that disapplies a gate before compute is doing exactly what rule 2 asks** — deciding in advance — and an audit that scores it as a defect punishes the discipline it is meant to enforce.

### §2v.3 THE THREE REFERRED SPECIMENS, RULED SEPARATELY — **ONE DOES NOT SURVIVE**

| specimen | verdict |
|---|---|
| **`G-COMPLETE`** — registered with rule 4's clauses and *"refuse (exit 2) rather than degrade"*, **zero occurrences in its reader** | **CONFIRMED** |
| **`G-CAPS`** — *"appears as one prose line computing no arithmetic"* | **⚠ DOES NOT SURVIVE AS STATED — NOT CARRIED FORWARD** |
| **MAAOA's pre-compute selftest** — §4 asserts controls *"driven PASS before this freeze"* | **CONFIRMED** — the only selftest artifact postdates the freeze **and records the first control as `FAIL`** |

**WHY `G-CAPS` IS REFUTED, stated at length because refusing a specimen matters more than adding one.** Its only appearance **in the reader** is indeed prose. But **its registered subject — every stage within its cap, cap-stop ⇒ `NOT A RESULT` — is implemented with real arithmetic in the chain driver**, which **the registration's own freeze table lists as a frozen instrument**: caps as constants, spend accumulation, an actual cap comparison, the cap-stop branch emitting the registered `NOT A RESULT` wording, and a `timeout` enforcing it inside the container.

> **RULED: A RUNTIME CAP CAN ONLY BE ENFORCED AT RUNTIME, AND A GATE IS IMPLEMENTED WHERE IT MUST BE, NOT WHERE THE READER IS.** Judging implementation **from the reader alone** is the single largest source of over-flagging in this class — **the surviving claim is "not implemented IN THE READER", which is not a `§2p` defect at all.** *The grading path is every frozen instrument the registration names, not the one file with `analyse_` in its name.*

**AND THE ONE GENUINELY NEW MEMBER IS THE CHEAPEST TO FIX.** `G-RLX-0` registers a bit-for-bit reproduction against a literal that **appears in no executable in the repository**, and its corrected grading path contains no series comparator. **It is PRE-COMPUTE AND NOT LAUNCHED — so it is repairable by a lawful pre-compute amendment under rule 2's own terms**, which is the whole of what this team recommends on it. **Referred to dafoam as actionable; no repair ordered from here.**

### §2v.4 WHAT THE REFERRAL TURNED OUT TO BE, AND IT CHANGES THE READING

**All three referred specimens are the referring team's OWN PUBLISHED SELF-DISCLOSURES** — already in their results records and addenda before this team saw them. One of them makes the missing evidence its **first binding requirement**, *"because it is the one MAAOA cannot now evidence."*

> **RECORDED: this was not a concealment audit. It was a team asking whether its own disclosed defects GENERALISE — and the measured answer is MOSTLY NO.** *A team that refers its own disclosed defects outward for measurement is doing the thing this charter exists to make normal, and the finding that the class is small is a finding in their favour, not a let-off.*

### §2v.5 THE STRUCTURAL CURE ALREADY EXISTS IN THIS LAB, ON DISK

One registration family **registers its gates AS NAMED CODE BLOCKS of its grader, AST-extracted and diffed.**

> **RECORDED AS THE REFERENCE SHAPE: where the registration's gate IS the implementation, face two of `§2v` is STRUCTURALLY UNAVAILABLE.** The gate cannot be registered without existing, because the registration *is* an extract of it. **That is a stronger cure than any sweep**, and it is already practised here. **Not mandated** — it constrains how a team writes a registration, which is not this team's to impose — **but named, so the next team choosing a convention knows one of the options forecloses the defect entirely.**

### §2v.6 THE `L-435` SECOND SPECIMEN — **TWO OF THE SHAPE, ONE OF THE HARM. NOT A CLASS.**

The cited reader **does** select its control fixture from a live artifact of the graded run, and under the referring team's **own** adopted rule — *a control's input may never be a function of the run being graded* — **the site is in breach. CONFIRMED as a structural instance.**

**But the harm is not reproduced, and I will not let that be elided.** The original defect died because a control **assumed** its live fixture had a property the run falsified. This reader **verifies the premise at selection time** and **falls back to a static in-file fixture** when no qualifying segment exists — so a wholly-failed run does not take it down.

> **RULED: TWO SPECIMENS OF THE SHAPE AND ONE OF THE HARM IS NOT A CLASS, AND THIS TEAM WILL NOT NAME ONE.** `§2p.5` is the precedent and it was paid for: *"a class propagated on a miscount is how a lab acquires rules nobody can later justify."* **A pattern worth watching is recorded as a pattern worth watching.**
>
> **The residual defect IS real and is named precisely rather than by analogy: WHAT THE SELFTEST PROVES VARIES WITH THE RUN**, because the controls exercise whichever qualifying point happens to be first. **The reader's verdict is not reproducible from the reader alone.** That is a weaker and truer statement than the class it was offered as.

### §2v.7 THE INSTRUMENT IS **NOT** LANDED, AND THE REASON IS `§2p` ITSELF

The sweep carries **two disclosed defects found by its own controls**: its generous arm **absolves the confirmed specimen** by matching a shell status string in a file that is not the reader; and relaxing a word boundary made it match a gate id **inside an ordinary English word**, which its own mutation arm caught.

> **CONSISTENT WITH `§2p.5`'s ruling on the previous scanner: AN INSTRUMENT THAT ABSOLVES WHAT IT DID NOT CHECK IS NOT LANDED AS A STANDING INSTRUMENT.** Landing it would be the fail-open this charter exists to forbid. **If it is wanted, it is repaired first and carries the `REGISTERED-AS-DISAPPLIED` verdict of `§2v.2`.** Its artifacts are in scratch, which **`L-186` forbids as a handoff channel** — so **this clause, not the code, is the durable record of the measurement.**

**⚠ AND THE DOMINANT BLIND SPOT IS STATED SO THE BOUNDS ARE NOT OVERREAD: 371 OF 393 REGISTRATIONS USE CONVENTIONS THE EXTRACTOR CANNOT READ** — principally gates registered by **quantity and band with no id at all**. **The lab-wide number could be materially larger and this team has NO BASIS TO BOUND IT.** The measured bounds describe **one naming convention in two families**, and **they must never be quoted as a lab-wide figure.**

| item | outcome |
|---|---|
| the unification | **`§2v` — `§2p` has two faces: the unwired instrument and the unbuilt registration; both yield a gate that cannot fail** |
| measured class size | **LOWER 2 · UPPER 4**, of **105** extracted instances in **20** frozen registrations |
| flags that were **false accusations** | **5 of 9** — a naive symbol match is wrong **more than half the time**, and its errors accuse teams |
| new verdict class | **`REGISTERED-AS-DISAPPLIED`** — without it a sweep over-reports by ~20 % |
| specimen (a) `G-COMPLETE` | **CONFIRMED** |
| specimen (b) `G-CAPS` | **REFUTED as stated — NOT carried forward.** A runtime cap is enforced at runtime; the grading path is every frozen instrument the registration names |
| specimen (c) MAAOA selftest | **CONFIRMED** — sole artifact postdates the freeze and records a `FAIL` |
| genuinely new member | **`G-RLX-0` — pre-compute, not launched, repairable by a lawful amendment.** Referred to dafoam; **no repair ordered** |
| what the referral was | **a team measuring whether its OWN disclosed defects generalise** — and mostly they do not |
| structural cure, already on disk | **register the gate AS the code block** — face two becomes structurally unavailable |
| `L-435` second specimen | **shape CONFIRMED, harm NOT reproduced — NOT a class.** Residual named: *what the selftest proves varies with the run* |
| the sweep instrument | **NOT LANDED** — it absolves what it did not check (`§2p.5`'s own ruling, applied to this team) |
| blind spot | **371 of 393 registrations unreadable by the extractor — the bounds are NOT a lab-wide figure** |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| repairs ordered on other teams · results re-graded | **0 · 0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.47, 2026-09-03 — **§2d.11.4 T3c's P-2 IS INSIDE THE GRANT AND P-1 NEVER WAS — THE GRANT IS SCOPED BY THE PROPERTIES I NAMED, NOT BY WHICHEVER CODE WAS WRITTEN FIRST · §2v.8 MY `G-RLX-0` PREMISE WAS FALSE AND THE TRUTH IS WORSE · §2w A LANDED VERDICT WHOSE LOAD-BEARING GATE WAS NEVER IMPLEMENTED IS `NOT A RESULT` · §2x "BIT-FOR-BIT" IS NOT A COMPARISON SPECIFICATION.**

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered, inserted or deleted. **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label is created, moved or retired; no verdict is withdrawn by this team.**

---

### §2d.11.4 — **T3c: CONFIRMED INSIDE THE GRANT. Heat-transfer is unblocked.**

**The question put to me:** does replacing the registered predicate **P-1** with **P-2** sit inside `§2d.11.1`'s grant, or does it need a fresh one?

**CONFIRMED INSIDE. And the reason matters more than the answer.**

`§2d.11.1` granted a successor whose rule-3 predicate is **two-sided, ASSERTING THE PLANT IS THE ARGMAX, with its tolerance quoted in ulp of the operands.** That grant named **properties**, not code.

> **RULED: A `§2d.1` GRANT IS SCOPED BY THE PROPERTIES IT NAMES, NOT BY WHICHEVER IMPLEMENTATION WAS WRITTEN FIRST.** **P-1 lacked the location limb** and therefore **never satisfied the grant** — it *"still passes `R_c` vacuously, `got == rec` to the last digit"*, which is **the exact defect the grant was given to repair.** **P-2 adds the LOCATION-identity limb and the ulp-magnitude limb, which is what the grant describes.**
>
> **So P-1 → P-2 is NOT an expansion of the grant. It is the FIRST attempt at compliance with it**, and no fresh grant is required.

**`[VERIFIED BY ME AT SOURCE, `c8dce56f`]` — CONDITION 4 IS SATISFIED, and I checked the thing most likely to be wrong.** The predicate reads `abs(got_max - PLANT) <= N_ULP * math.ulp(operand)`. **`N_ULP = 32` is a DIMENSIONLESS ULP COUNT multiplied by `math.ulp` of the ACTUAL OPERAND at runtime** — **not** an absolute tolerance in Kelvin chosen to equal *n* ulp at one field magnitude. **That distinction IS condition 4**, and it is the difference between a repair and the same defect wearing a computation.

> **BOUND, stated so it cannot drift later: the ulp must be taken from the OPERAND ENCOUNTERED AT RUNTIME. `math.ulp(300.0)` evaluated once and reused is the forbidden constant with an extra step**, and it would reintroduce the original defect at any other field magnitude.

**The window derivation is transparent and I re-read it:** `N_ULP >= 21` (the **frozen** S-2 arm), `>= 6.81` (real `R_f`), `>= 5.81` (real `R_ff`), `< 200` (the frozen S-2 negative limb) — so `21 <= N < 200`, **forced by T3c's own frozen arms rather than chosen**, with the smallest admissible power of two adopted on a registered principle. **The lane's self-correction — that its "unique" claim was false, three powers of two being admissible — is recorded as the right conduct**: a derivation that overstates its own uniqueness is a claim nobody can later audit.

**`§2p.3(e)` FIRED PRODUCTIVELY AND THAT IS THE PART WORTH KEEPING.** The first mutation showed **`R_c` never exercised the new limb at all** — so arm **S-9**, a **decoy cell inside the magnitude window but OFF the planted cell**, was registered and kills the mutant. **S-9 is what proves the LOCATION limb discriminates rather than the magnitude limb doing all the work.** *A positive control that passes without exercising the thing it certifies is the defect this whole grant exists to repair, and they caught it in their own repair before it shipped.*

**`§2d.11.3`'S BINDING CONDITION WAS HONOURED, AND HONOURED THE RIGHT WAY.** `[VERIFIED BY ME]` T3c's line 3 is **struck with strikethrough and LEFT LEGIBLE**, citing this charter as the reason: *"the striking is a condition of landing this document"*, *"the struck line is left legible rather than deleted."* **Struck, never rewritten. That is rule 2's own discipline applied to a document's claim about itself.**

**Conditions 1, 2, 3 and 5 of `§2d.11.1` CONTINUE UNCHANGED.** In particular **condition 5: THIS CONFIRMATION LICENSES NO VERDICT.** `R_ff` at **4.34×** the iterative-convergence tolerance is `NOT_CONVERGED` → **`NOT A RESULT`**, and that remains the expected honest outcome. **Nobody may read this as authorising a `PASS`.**

**AND THE POINT OF ORDER IS CORRECT AND I ADOPT IT VERBATIM.** Heat-transfer's supervisor authorised the build and **explicitly declined to treat that authorisation as my ruling**: *"a supervisor's authorisation is not a charter owner's ruling on the scope of that charter owner's own grant, and treating it as one is the laundering rule 9 forbids."* **That is exactly right, it is now on this record, and it is the cleanest statement of rule 9 any team has produced.**

---

### §2v.8 — **MY OWN `§2v.3` CARRIED A FALSE PREMISE. THE CORRECTION MAKES THE FINDING WORSE.**

`§2v.3`, committed hours ago, said `G-RLX-0` *"is PRE-COMPUTE AND NOT LAUNCHED — so it is repairable by a lawful pre-compute amendment, which is the whole of what this team recommends on it."*

**THAT IS FALSE, and `[VERIFIED BY ME AT SOURCE]` rather than accepted on the referral's word:**

- `cases/dafoam/D12RLX_RESULTS.md:1` — **`GATE REACHED`**, a **landed verdict**;
- `docs/COST_CALIBRATION.md:361` — a **landed calibration row**, **92.9672 core-min actual** against 111.03 predicted, **ratio 0.837**;
- the registered literal appears in **ZERO executables** (my own sweep);
- the frozen grader contains **ZERO occurrences of `rlx`**.

**The compute ran. The verdict landed. My recommended remedy — a lawful pre-compute amendment — DOES NOT EXIST for this item, because rule 2 closed those gates at first compute.**

**HOW I GOT IT WRONG, because the mechanism is the lesson:** I carried a lane's characterisation of launch status into a **charter clause** without verifying it personally. **That is `SUPERVISION_CHARTER` §3 check 3 — big-claim verification before belief — and I skipped it on the one figure in `§2v` that determined the recommended remedy.** I verified five other things at source that day and not this one. *A supervisor who verifies the interesting claims and relays the boring ones has not verified anything.*

**AND THE TRUTH IS WORSE THAN THE REFERRAL LABELLED IT, in a way I found by reading the records myself.** `D12RLX_RESULTS.md:3-4` shows the item verdict came from **§7's registered mapping, whose THIRD ROW OPENS `"G-RLX-0 reproduces"`** — **the unimplemented gate is the FIRST CLAUSE of the mapping that produced the verdict.** And `COST_CALIBRATION.md:361` **asserts the gate passed**: *"`G-RLX-0` reproduction PASS bit-exact incl. the adjoint gradient."*

> **⚠ THE FALSE CLAIM PROPAGATED INTO A SECOND RECORD THAT NOBODY WOULD THINK TO AUDIT FOR GATE IMPLEMENTATION.** The cost-calibration ledger is read for **core-minutes**, and it is now carrying a **verdict assertion about a gate that no code ever evaluated.**

**THE SWEEP DISCIPLINE BEHIND THE CORRECTION IS ADOPTED AS LAW**, because it is `CLAUDE.md` rule 3 generalised from comparators to search instruments: dafoam's **first sweep false-zeroed on its own control** and was **re-run with known-present literals**.

> **RULED: A ZERO FROM A SEARCH INSTRUMENT IS NOT EVIDENCE UNTIL THAT INSTRUMENT IS SHOWN ABLE TO FIND A KNOWN-PRESENT INSTANCE, in the same invocation.** *A grep that finds nothing and a grep that is pointed at the wrong tree print the same thing.*

---

### §2w — **WHAT HAPPENS TO A LANDED VERDICT WHOSE LOAD-BEARING GATE WAS NEVER IMPLEMENTED**

> **RULED — `§2w`: THE VERDICT IS `NOT A RESULT`.**
>
> A gate that **licenses** whether a quantity may be read is **a step in the measurement chain**, not a statement about the record. **Where it was never evaluated, the licensed quantity was never licensed**, and every verdict resting on it is `NOT A RESULT` **whatever its value**. `§2d.10` already holds that a licensing gate is `NOT A RESULT` whenever what it licenses is; **a gate that does not exist is a fortiori not `CONVERGING`, not `PASS`, and not anything else.**
>
> **The direction is the permitted one.** Rule 5 allows a substantive verdict to be turned **INTO** `NOT A RESULT` and never the reverse. **`GATE REACHED` → `NOT A RESULT` is lawful; the converse would not be.**

#### §2w.1 THE DISTINCTION FROM `§2r.2`, DRAWN EXPLICITLY BEFORE ANYONE CALLS THIS INCONSISTENT

Hours ago I ruled the opposite-looking thing: a Tier-2 mesh limb failure **refuses the certificate and does NOT void the physics** — *bookkeeping never voids physics*. **These are not in tension and the line between them is sharp:**

| `§2r.2` — bookkeeping | `§2w` — a missing measurement step |
|---|---|
| The failure is in **what the record DISCLOSES** — a heading, a substring, a digest nobody wrote down. | The failure is in **whether the number was ever ENTITLED TO BE READ**. |
| The physics was computed and is unaffected. | The physics was computed **and remains on disk** — but the **verdict** rests on a precondition **that was never checked**. |
| Certificate refused; run reverts to its ordinary treatment. | **Verdict demoted to `NOT A RESULT`.** |

> **THE TEST: does the missing thing describe the record, or does it stand between the run and the reading?** *A missing disclosure is a debt against the record. A missing licensing gate is a hole in the measurement.*

#### §2w.2 HOW IT IS CORRECTED — **SUPERSESSION, NEVER DELETION**

1. **The original verdict is STRUCK AND LEFT LEGIBLE**, with the demotion and its cause beside it (rule 6; and T3c's line 3, struck this same day, is the reference execution). **A reader who finds only `NOT A RESULT` learns less than one who sees a `GATE REACHED` demoted and why.**
2. **THE COMPUTE IS NOT WASTE.** The run ran, the artifacts are on disk, and **a future implementation of the gate can still grade them.** Same disposition this charter gave T3's 26,757 core-min.
3. **⚠ THE CALIBRATION ROW STANDS AS A RECORD OF SPEND; ITS VERDICT ASSERTION DOES NOT.** The core-minutes are a **measured fact about the run** and are true whatever the verdict — *physics never voids bookkeeping either.* But a calibration row that **asserts a gate passed** carries a claim outside its own subject, and **where that claim is false it is corrected on the same terms as any other record.**
4. **THE OWNING TEAM DEMOTES ITS OWN VERDICT. This team rules the CLASS, not the item.** Dafoam has already declined to treat the `GATE REACHED` as supported and referred rather than withdrawn — **which is the correct order of operations and is recorded as such.**

#### §2w.3 **THE DISCRIMINATOR THAT MAKES `§2v`'s MEASUREMENT ACTIONABLE**

The two confirmed members of `§2v`'s class are **not equivalent**, and the difference is the whole of what to do about them:

- **`G-COMPLETE`** — the item's completeness is recorded **UNADJUDICATED**; the team **declined to hand-compute the missing verdict**. **A DISCLOSED HOLE.**
- **`G-RLX-0`** — a **verdict LANDED** on the strength of the unimplemented gate, and a second record asserts that gate passed. **A FALSE RECORD.**

> **RULED: THE QUESTION IS NOT "IS A GATE UNIMPLEMENTED" — IT IS "DID A VERDICT LAND ON ITS STRENGTH."** An unimplemented gate whose item is recorded unadjudicated is **a hole its team already disclosed**. An unimplemented gate carrying a published verdict is **a false record and is corrected under `§2w.2`**. *Only the second is urgent, and conflating them would have this lab chasing disclosures instead of errors.*

**NO LAB-WIDE SWEEP IS ORDERED.** `§2v.1` measured this class at **2 confirmed of 105** with **five of nine naive flags false**, and **371 of 393 registrations unreadable by that extractor**. **A sweep whose false-positive rate exceeds half, aimed at a class of two, would produce more false accusations than findings.** The two confirmed members are handled **on their own facts, by their own team.**

**⚠ AND I WILL NOT BORROW SANAA'S NO-RE-GRADING INSTRUCTION AS COVER.** Her *"no re-grading of past results unless a specific comparator is shown to have moved"* is about the **FREEZE**. Here **no comparator moved — a gate never existed.** **That is a different condition and her instruction neither authorises nor forbids it.** *Reading an instruction onto a case it does not address is the laundering rule 9 forbids, and it is just as wrong when it would save me work.*

#### §2w.4 WHAT IS **NOT** RULED HERE

**The RESULT-PRIORITY consequences are NOT ruled**: whether a demoted item still counts toward a ladder, how it orders against live rungs, and what it does to a capability claim. **`RESULT_PRIORITY_CHARTER.md` is a DRAFT at v0.5 awaiting Sanaa — its orderings are proposals and only the bright line is settled**, and this team will not settle by amendment what is on her desk for ratification. **Referred, with `§2w` as the verification-side input.**

---

### §2x — **"BIT-FOR-BIT" IS NOT A COMPARISON SPECIFICATION**

The sharpest finding in the referral, and it generalises past its specimen: **the registered `h_min` and the achieved value DIFFER AS STRINGS and are EQUAL AS `float64`** — and **no code ever decided which comparison *"bit-for-bit"* meant.**

> **RULED — `§2x`: A REGISTERED COMPARISON NAMES ITS OPERATOR AND ITS TYPE.** *"Bit-for-bit"*, *"exact"*, *"identical"*, *"unchanged"* and *"reproduces"* are **English words, not comparison specifications.** Each resolves **differently** over decimal strings, over `float64`, and over rendered output, and **the three disagree on real values** — as this specimen proves, where the same quantity is simultaneously unequal and equal depending on a choice nobody made.
>
> **A registration that says "bit-for-bit" without naming the type has registered a gate whose meaning is decided by whoever implements it — and WHERE NO CODE EVER MADE THE CHOICE, THE GATE WAS NEVER SPECIFIED, LET ALONE IMPLEMENTED.**
>
> **Required in the registration: the operator (`==`, `abs(a-b) <= tol`, string identity), the TYPE the comparison is performed in, and — for any float comparison — the TOLERANCE AND ITS UNIT** (`§2d.11.4`'s ulp-count-times-runtime-ulp is the reference form).

**⚠ AND THE FAILURE MODE IS THE DANGEROUS ONE: this reads as MORE precise than a stated tolerance, not less.** *"Bit-for-bit" sounds like the strictest thing a registration can say.* **It is in fact the least specified**, and a reviewer's eye slides over it precisely because it sounds rigorous. **A phrase that buys credibility without buying meaning is worse in a registration than an admitted approximation.**

### §2y — **SANAA'S GOVERNANCE REFORM APPLIED TO THIS TEAM'S OWN CLAUSES, INCLUDING TWO I COMMITTED TODAY**

`[SANAA-DIRECT, 2026-09-03 ~20:00Z, `etc/sessions/2026-09-03T2000Z_sanaa_governance_reform.md`, read verbatim before this amendment was committed.]` **This team is the most affected by it, and the first thing it does is cut two of my own clauses down.**

#### §2y.1 THE BLOCKED RESULTS THIS AMENDMENT NAMES, as her new bar requires

> *"Petitions, rulings, and charter amendments require a blocked result to name. No result blocked → no petition."*

- **`§2d.11.4` — BLOCKED RESULT: T3's `R_ff` grading.** 26,757 core-min already spent, a complete field tree on disk, and **not one row graded** pending this confirmation.
- **`§2w` / `§2v.8` — BLOCKED RESULT: D12RLX's verdict integrity.** A landed `GATE REACHED` whose supporting record its own team declines to treat as supported.

**Both name a blocked result and both clear the bar.** `§2x` does **not** stand alone under it and is landed **only** as the specification `§2w` needs to be applicable — **not as a free-standing rule**, and it opens no work for any team.

#### §2y.2 CLASSIFICATION — **GATING vs REPORTING, for every clause in this amendment**

> *"Gating requires a stated reason of the form 'without this, the verdict on result X cannot be trusted.' Anything without that reason is reporting."*

| clause | mode | the stated reason, or why not |
|---|---|---|
| **`§2w`** | **GATING** | *Without the licensing gate having been evaluated, the verdict on D12RLX cannot be trusted* — the number was never entitled to be read. This is the required form exactly. |
| **`§2x`** | **GATING only where the comparison it governs is itself gating; REPORTING everywhere else** | An unspecified comparison in a **reporting** check misleads a reader; an unspecified comparison in a **gating** check means the gate was never specified. **Only the second can void a verdict**, so only the second gates. |
| **`§2d.11.4`** | **neither — a scope confirmation** | It creates no check. It confirms which implementations an existing grant already covers. |
| **`§2v.8`** | **neither — a correction of record** | It withdraws a false statement of mine. |

#### §2y.3 **HER RULINGS CUT TWO CLAUSES I COMMITTED TODAY, AND I RECORD THAT PLAINLY**

- **`§2r.4`'s FIRST OBSTACLE IS DISSOLVED BY HER, not by me.** I ruled Tier-2 certificates **documentary** partly because the birth machinery quarantines every committee grid on **skewness**. She has **reclassified the skewness quarantine to REPORTING**. **A reporting check never blocks.** So **obstacle 1 no longer blocks a Tier-2 certificate**; obstacles 2 and 3 (checkMesh's false `OK` line, and the missing *reported-not-gated* rendering mode) **stand**, and the second of those is now **the standard's default mode by her order**, so it is a build item rather than a question.
- **`§2s.2`'s SUNSET IS SUPERSEDED BY HER CONDITION.** I recommended `UNREACHABLE → REFUSE` when coverage first reads full. **She ruled it fires only after the fleet monitor has run ONE FULL SWEEP fleet-wide.** **Her condition governs; my recommendation is struck.** It is also the better condition — it turns on **demonstrated fleet-wide observability**, not on a ratio I had already shown recedes as the lab works.

#### §2y.4 **LIMB (2) IS SUSPENDED, AND HER RULE 2 IS WHY — IT CATCHES MY OWN METRIC**

> *"No instrument is built to measure another instrument's reach unless the first instrument has already changed a verdict at least once."*

**The coverage metric is exactly that: an instrument measuring the freeze enforcer's reach.** `[MEASURED]` **the enforcer has changed ZERO verdicts** — its census reads **1 PINNED of 289 eligible**, and because the gate fires **at launch** while **every eligible row has already launched**, it has refused nothing and can refuse nothing historical.

> **RULED AGAINST MY OWN PROGRAM: LIMB (2)'s COVERAGE REPORTING IS SUSPENDED.** Her separate application — *"coverage ratios forward-only, unreported"* — points the same way. **The weekly coverage report does not start.** It starts when the enforcer has refused something real. **I built a measuring instrument for a thing that had not yet measured anything, which is her rule's exact target, and it is mine.**

#### §2y.5 WHAT THIS TEAM OWES UNDER THE REFORM, AND THE HONEST DIGEST LINE

- **THE ONE-PASS RECLASSIFICATION IS OWED BY ME** for every check this charter defines: each is marked **gating with its stated reason**, or **drops to reporting**. **Anything that cannot produce the reason drops.** One pass, inside the governance budget, **not a new cycle.**
- **`§2w.3` ALREADY CONFORMS TO HER COST RULE** — it orders **no sweep, no backfill and no migration**, and the two confirmed members are handled by their own team on their own facts.
- **THE DIGEST LINE, STATED AS SHE REQUIRES IT: `no physics result this cycle`.** Zero solver compute, zero rungs graded. **The honest counterweight, offered as fact and not as excuse: two rungs that were blocked are now unblocked** — T3's `R_ff` and T5c — **and this team's output is properly measured in other teams' results, not in its own.** **Her warning is nevertheless taken: repeated no-result cycles are the signal, and this team will be the last to notice its own.**

---

| item | outcome |
|---|---|
| **T3c `P-1` → `P-2`** | **CONFIRMED INSIDE `§2d.11.1`** — no fresh grant needed; **heat-transfer unblocked** |
| why | **a `§2d.1` grant is scoped by the PROPERTIES it names**, not by whichever code was written first; **P-1 never satisfied it** |
| condition 4 | **SATISFIED** — `N_ULP` × `math.ulp(operand)` is a dimensionless count against a **runtime** ulp; **bound added: never a pre-evaluated `ulp(300.0)`** |
| `§2d.11.3` condition | **HONOURED** — line 3 **struck and left legible**, citing this charter |
| verdict licensed by the confirmation | **NONE.** `R_ff` at **4.34×** remains `NOT A RESULT` |
| **`§2v.3`'s premise** | **FALSE — MINE.** `G-RLX-0` is **post-compute**: `GATE REACHED` landed, **92.9672 core-min**, calibration row landed |
| how I erred | **carried a lane's characterisation into a charter clause without check 3** — on the one figure that decided the remedy |
| worse than labelled | the unimplemented gate is **the FIRST clause of the mapping that produced the verdict**, and the **calibration ledger asserts it PASSED** |
| **`§2w`** | **a landed verdict whose load-bearing gate was never implemented is `NOT A RESULT`** — the permitted direction |
| `§2w.1` | the line against `§2r.2`: **does the missing thing describe the record, or stand between the run and the reading?** |
| `§2w.2` | **supersession, never deletion**; compute is **not waste**; **the calibration row's SPEND stands, its VERDICT ASSERTION does not** |
| `§2w.3` | **the discriminator: did a verdict LAND on its strength?** Disclosed hole vs **false record** — only the second is urgent |
| sweep ordered | **NONE** — false-positive rate >50 % against a class of 2 |
| Sanaa's no-re-grading instruction | **NOT borrowed as cover** — it addresses the freeze; **no comparator moved here** |
| new law | **`§2x` — "bit-for-bit" is not a comparison specification**; name the operator, the type, and the tolerance with its unit |
| adopted from the referral | **a zero from a search instrument is not evidence until it is shown able to find a known-present instance** |
| result-priority consequences | **NOT RULED — `RESULT_PRIORITY_CHARTER` is a v0.5 draft on Sanaa's desk** |
| **`§2y` blocked results named** | **`R_ff`'s grading** and **D12RLX's verdict integrity** — both clear Sanaa's new petition bar |
| `§2y.2` classification | `§2w` **GATING** with her required reason; `§2x` **gating only where the comparison it governs gates**, reporting otherwise |
| **`§2r.4` obstacle 1** | **DISSOLVED BY HER** — the skewness quarantine is reclassified **REPORTING**, and a reporting check never blocks |
| **`§2s.2` sunset** | **MY RECOMMENDATION STRUCK** — her condition governs: after ONE full fleet-wide monitor sweep |
| **limb (2) coverage** | **SUSPENDED — her meta-instrument rule catches MY OWN metric.** The enforcer has changed **0 verdicts** (1 PINNED of 289, and it fires at launch on already-launched rows) |
| owed by me | the **one-pass reclassification** of every check this charter defines — gating with its reason, or it drops to reporting |
| **digest line, as she requires it** | **`no physics result this cycle`** — 0 core-min, 0 rungs graded; **two rungs UNBLOCKED** (`R_ff`, T5c), which is where this team's output properly shows |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| verdicts withdrawn by this team | **0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.48, 2026-09-03 — **§2s.10: D6 RULED ON THE RECORD — A DECLARED-BUT-ABSENT COMPARATOR IS A DECLARATION DEFECT AND REFUSES NOW. A RULING THAT LIVES ONLY IN AN INTER-AGENT MESSAGE IS NOT ON THE RECORD, AND ANOTHER TEAM'S CODE WAS STANDING ON ONE OF MINE. · §2z TWO MEASURED INPUTS RECORDED, NOT RULED.**

**Lines whose number changed above this section: 0.** **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label is created, moved or retired.**

**BLOCKED RESULT NAMED (Sanaa's petition bar):** rows **refusing at launch today** on a behaviour my `§2s.2` did not license. **THIS IS THIS TEAM'S LAST GOVERNANCE COMMIT OF THE CYCLE** — 22 governance commits today against **zero** physics, which is far outside her ~1-in-5 budget, and it is recorded here rather than left for her to notice.

### §2s.10 — **DECLARED-BUT-ABSENT IS A DECLARATION DEFECT. REFUSE NOW.**

`§2s.2` assigned unconditional refusal to **`MISMATCH` alone** and routed no-reachable-sha to **proceed-and-count until the sunset**. cfd's enforcer refuses **two further states** — `ABSENT-AT-FREEZE` and `ABSENT-ON-DISK` — **stricter than my ruling licensed.** They refused to pick on their own authority (rule 9), disclosed it, and left the behaviour stands-as-built.

> **RULED: THEIR STRICTER READING IS UPHELD. `§2s.2` WAS UNDERSPECIFIED; THEIR CODE WAS NOT WRONG.**
>
> **`§2s.2`'s third outcome was written for rows where the FREEZE EVIDENCE is absent. These are rows where the ARTIFACT is absent — a different and worse condition.** A row that **declared** a comparator not present **at its own freeze commit** has **registered nothing**: it is nearer **self-contradiction** than unreachability. And a comparator **absent on disk cannot grade at all.**
>
> **GATING REASON, in the form Sanaa's reform requires:** *without a comparator present at freeze and present on disk, the verdict on that run cannot be trusted, because nothing computed it.*
>
> **AND THE DECISIVE ARGUMENT IS THEIRS, NOT MINE:** treating declared-but-absent as outcome three **lets a row BUY proceed-and-count by naming a path that never existed.** *An outcome reserved for rows with no evidence must not become an outcome reachable by asserting nothing.*

**⚠ THE PROCEDURAL FAILURE IS MINE AND IT IS THE POINT OF THIS AMENDMENT.** I ruled D6 **in an inter-agent message** hours before this clause. **Another team's enforcement code was standing on a ruling that existed nowhere in the repository.** **`L-186`'s principle is not about the scratchpad specifically — it is that a channel which does not survive the session is not a record.** **A message is exactly that channel**, and I used one for a ruling **the same day I committed two files to stop doing it with drafts.**

> **RULED: A RULING IS NOT IN FORCE UNTIL IT IS COMMITTED. An inter-agent message may CONVEY a ruling and may unblock work provisionally, but the ruling is landed in the charter in the same cycle or it is withdrawn.** *A team should never have to cite my mail to justify its gate.*

### §2z — **TWO MEASURED INPUTS FROM cfd, RECORDED AND NOT RULED**

Both are **physics findings** under Sanaa's taxonomy — *reported, not gated*, and **they trigger no rule change on their own.** Recorded because each bears on an instrument this charter governs, and **neither is mine to act on.**

**§2z.1 — A PLATEAU CLASSIFIER BUILT ON ENDPOINT DELTAS WILL CALL THINGS CONVERGED THAT ARE NOT.** `[MEASURED, cfd, `N-C10`]` the endpoint-to-endpoint `C_D` difference **understates the functional's wander by ~3.8×** — full spread across 31 recorded iterations **1.082e-05** against an endpoint reading of **2.840e-06**. **Sanaa's fleet monitor classifies *plateaued-or-oscillating* at a deadline**, and a classifier reading endpoints **will mislabel a wandering functional as plateaued.** **It has to read spread-over-window.** **Relayed upward as an input to the monitor's design, not adopted here** — the monitor is not this team's instrument.

**§2z.2 — TIER 1 IS NOT CURRENTLY REACHABLE FOR M6 BY ANY IN-HOUSE ROUTE THIS LAB HAS.** `[MEASURED]` `R1-M0` reads **88.88926674°** with **206 severe faces** on a pyHyp wall-resolved in-house M6; M6I reads **87.66–87.75°**. **Two INDEPENDENT in-house topologies now fail the 70° generation gate**, which converts what was explicitly labelled **inference** — that ≈87° flat across a **64× cell increase** is a property of the **topology, not the resolution** — into **measurement.**

> **RECORDED, and it changes the standing of `§2r` without changing its text: the Tier-2 admission path is not a convenience. On present evidence it is the ONLY path to a certificate on M6**, which is why the missing *reported-not-gated* rendering mode is now correctly treated as a **blocking physics fix** rather than a governance item. **`§2r`'s obstacle 3 is therefore the live one**, obstacle 1 having been dissolved by Sanaa's reclassification.

### §2z.3 — **THE `§2w` AUDIT IS THE OWNING TEAM'S, AND I DECLINE TO TAKE IT OVER**

cfd has opened a `§2w` audit **on itself, unprompted** — F17–F27 headline verdicts read from RESULTS records with **no comparator re-run and no GCI re-derived**, and **7 JF1 rows with no grading script anywhere in the repository** — and offered to hand it to this team.

> **DECLINED, and the reason is `§2w.3`'s own discriminator: the owning team demotes its own verdicts; this team rules the CLASS.** Taking it over would duplicate work, and it would make a team's self-correction into an external finding — **which is the surest way to stop teams opening audits on themselves.**
>
> **THE STANDARD IT MUST MEET, so the result is auditable when it lands:** each item states **whether a verdict LANDED on the unimplemented gate's strength** (`§2w.3`); a **disclosed hole is not a false record**; demotions are **struck and left legible, never deleted** (`§2w.2`); and **the compute is not waste.** **This team will audit the RESULT, not the work.**

**And a second instance of a pattern `§2w.2` already names:** `JF1_P1_L1_CMESH_PHYSICS` is asserted `NOT A RESULT` **only inside a cost-calibration row** — a verdict living in an instrument built to record spend, which is the same shape as D12RLX's calibration row asserting a gate passed. **Two instances is a pattern worth watching and NOT a class** (`§2p.5`), and no sweep is ordered; **the scope rule is already law at `§2w.2` and needs no new clause.**

| item | outcome |
|---|---|
| **D6** | **cfd's stricter reading UPHELD** — declared-but-absent is a **declaration defect**, refuses now |
| why | the third outcome is for **absent EVIDENCE**, not an **absent ARTIFACT**; otherwise a row **buys proceed-and-count by naming a path that never existed** |
| **the procedural failure** | **MINE** — I ruled D6 **in a message**; another team's gate stood on a ruling **in no commit** |
| new law | **a ruling is not in force until it is committed**; a message may unblock provisionally, never permanently |
| `§2z.1` | **endpoint deltas understate wander ~3.8×** — a plateau classifier must read **spread-over-window**; relayed to the monitor, **not adopted here** |
| `§2z.2` | **two independent in-house topologies fail the 70° gate** — Tier 2 is, on present evidence, **the only path to an M6 certificate**; `§2r` obstacle 3 is the live one |
| `§2w` audit | **DECLINED — the owning team's.** Standard stated; **this team audits the RESULT, not the work** |
| verdicts in calibration rows | **2 instances — a pattern, NOT a class**; already covered by `§2w.2`; **no sweep** |
| governance budget | **22 governance commits today against 0 physics — far outside her ~1-in-5. THIS IS THE LAST OF THE CYCLE.** |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.49, 2026-09-03 — **§2s.11: THE LAUNCH/GRADE SPLIT, STATED SO NOBODY RE-DERIVES MY WRONG READING. SANAA REVERSES MY "CHOKE POINT IS THE LAUNCH" CORRECTION AND STRIKES MY D6 RULING OF TWENTY MINUTES AGO — BOTH CORRECTLY. I FOUND A TRUE FACT AND DREW A FALSE CONCLUSION FROM IT.**

**Lines whose number changed above this section: 0.** **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label is created, moved or retired; the frozen grader is untouched.**

**BLOCKED RESULT NAMED:** **runs that are being refused at launch right now** by an enforcement reading this amendment withdraws. **THIS AMENDMENT IS HER DIRECTIVE, NOT THIS TEAM'S INITIATIVE** — v1.48 stated it was the cycle's last governance commit, and that stands as this team's own budget discipline; **`[SANAA-DIRECT, 2026-09-03 ~21:00Z]` explicitly orders this reconciliation "within your governance budget."**

### §2s.11 — **PRE-REGISTRATION PREDICTS · THE MONITOR WATCHES · THE GRADER JUDGES AFTERWARD**

Her rule, verbatim: **"A pre-registration mismatch never prevents a launch. It's recorded as a prediction, the run launches under the monitor, and the outcome is compared to the prediction on the certificate."** And the sentence that decides it: **"Refusing to widen the gate was right; refusing to launch was the expensive part."**

> **RULED — `§2s.11`, [SANAA-RULED]. THE REFUSAL LIVES AT GRADING. IT DOES NOT LIVE AT LAUNCH.**
>
> - **At LAUNCH:** a comparator `MISMATCH` — and every other pre-registration mismatch — is **RECORDED AS A PREDICTION**. The run **launches, under the monitor**. **Nothing about a frozen-comparator disagreement blocks a solve from starting.**
> - **At GRADING:** the **frozen grader, UNCHANGED**, applies every gate **after the fact, on evidence**. A run whose comparator moved still gets that refusal **on its certificate**.
> - **The rule changes WHEN the gate applies, never WHETHER it applies.**

**`§2s.10` IS STRUCK.** D6's two states — `ABSENT-AT-FREEZE` and `ABSENT-ON-DISK` — **take the same disposition: RECORD, LAUNCH, JUDGED AFTER.** My ruling that they are a declaration defect refusing *now* was **twenty minutes old and is withdrawn.** The *reasoning* in `§2s.10` — that an absent artifact is a worse condition than absent evidence — **survives as a grading-time distinction**; what does not survive is the launch-side refusal it licensed.

**WHAT DOES NOT CHANGE, stated because a reader will ask:** **rule 2's freeze-before-compute is untouched** — registrations still freeze before compute, because **they are the predictions being tested**; **the grader's gates are untouched**; and **two classes still stop a run before it starts** — a **physically ill-posed setup** (no outlet, inconsistent BCs, leaking geometry) is a **blocking physics fix, not a pre-registration mismatch**, and **resource limits QUEUE rather than block**, which is not blocking because the run stays scheduled.

**THE ONE HARD STRUCTURAL STOP, recorded and NOT this team's instrument:** a fleet-wide safety ceiling at **min(3× the registered cost cap, the box's remaining budget)**, monitor-enforced, **graceful stop regardless of residual trend.** Her justification is the T12 lesson — *the launcher's own flag never fired, so something must be structurally guaranteed to stop a run* — **but the ceiling sits far above the estimate, because the estimate is a prediction to be tested and the ceiling is protection against the box being eaten.**

### §2s.11.1 — **MY ERROR, NAMED, BECAUSE THE SHAPE OF IT IS THE LESSON**

`§2s.1` and the spec's `§7.2` ruled: *"the daemon has no grading step, so the honest choke point is the LAUNCH"* — and I went further and claimed it **"serves her intent better, because the run is refused before the compute is spent."**

> **THE FACT WAS TRUE AND THE CONCLUSION WAS FALSE.** The daemon genuinely has no grading step. **The correct inference was that THE GRADING STEP IS WHAT MUST BE BUILT — not that the refusal should move earlier to somewhere convenient.** I mistook *"where can a refusal most easily be attached"* for *"where does the refusal belong."*
>
> **AND THE WORSE HALF IS THE CLAIM ABOUT HER INTENT.** I asserted my mechanism served her purpose better than her own wording did. **It did the opposite: refusing before the compute is spent is precisely the expense she was eliminating** — a refused launch buys no evidence, teaches nothing, and forecloses the comparison that makes the standard improvable. **Reasoning about an owner's intent and getting it backwards is worse than being wrong about a mechanism, because a mechanism error is visible in the code and an intent error hides inside a justification.**

**MY UNDERLYING CONCERN WAS RIGHT AND MY MECHANISM WAS CLUMSY, which I record so the concern is not thrown out with the error.** `§2s.2`'s three outcomes existed to stop the enforcer halting the lab and being switched off within a day. **Her rule achieves that protection more cleanly — nothing halts, everything launches — AND buys a calibration dataset my design could not.** *The problem I identified was real; she solved it in the direction I did not consider.*

### §2s.11.2 — **THE PAYOFF BECOMES THIS TEAM'S CALIBRATION LINE**

> *"What you gain: a calibration dataset for every pre-registration standard. If runs flagged 'will exceed cap' routinely come in under it, the caps are too tight; if y+ predictions never miss, the quality gate can drop to reporting. The standards get corrected by data instead of by petition."*

**RECORDED AS THIS TEAM'S GOVERNING PRINCIPLE GOING FORWARD, and it is the answer to a problem this charter has been solving the expensive way all day.** Every gate, band and cap in this charter has been set, widened or defended **by argument**. **Under this rule each one accrues a predicted-versus-actual record on every certificate**, and **a standard that is never missed is a standard that should drop to reporting** — which is her governance reform's default arriving with the evidence to apply it.

**⚠ AND IT SHARPENS, RATHER THAN LIFTS, `§2y.4`'s SUSPENSION OF LIMB (2).** The coverage metric stays suspended. **But its SUBJECT changes: the useful measurement is no longer "how many rows were refused" — under this rule none are — it is PREDICTED VERSUS ACTUAL.** *A refusal count would now measure only how often the lab declined to learn something.*

| item | outcome |
|---|---|
| **the split** | **launch RECORDS a mismatch as a prediction; GRADING refuses.** The rule changes **when** a gate applies, never **whether** |
| **`§2s.10` (D6)** | **STRUCK, twenty minutes after landing.** Both states: **record, launch, judged after.** Its artifact-vs-evidence reasoning survives **at grading time** |
| **`§2s.1` / spec `§7.2`** | **REVERSED — mine.** True fact, false conclusion: the grading step must be **built**, not bypassed by refusing earlier |
| **the worse half** | I claimed my mechanism **served her intent better**. It did the opposite — **a refused launch buys no evidence** |
| unchanged | **rule 2's freeze-before-compute; the frozen grader; every gate it applies** |
| still stops a run | **ill-posed setup** (blocking physics fix) · **resource limits QUEUE, which is not blocking** |
| one hard ceiling | **min(3× registered cap, remaining box budget)**, monitor-enforced, graceful — **not this team's instrument** |
| limb (2) | **still suspended, and its SUBJECT changes** to predicted-vs-actual |
| this amendment's authority | **[SANAA-DIRECT]** — ordered by her; v1.48's "last of the cycle" stands as this team's own discipline |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.50, 2026-09-03 — **§2p.9 MY OWN `§2p.8` NAMES A GRANT THAT WAS REFUSED, AND THE DEBT IS ON TWO ITEMS NOT THREE · §2p.10 `§2p.3(e)` DISCHARGED FOR `R3` AND `R5` THROUGH THE PRODUCTION PATH · §2ab AN UNREACHABLE VERDICT IS A DEFECT ONLY WHEN NOTHING REACHES IT — WHEN SOMETHING STRICTER PREEMPTS IT, IT IS A PROPERTY. VR3-R2 IS `GATE FAIL`.**

**Lines whose number changed above this section: 0.** Pure append; the file's pre-append
digest is `971bdad34f566febad9fc5c790b1c9a1` at 5,699 lines and every prior line keeps its
number. **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label
created, moved or retired; nothing re-graded.** `§2p.8` is **STRUCK IN ONE CLAUSE AND LEFT
LEGIBLE WHERE IT WAS WRITTEN** — the discipline I have required of three other teams this week.

### §2p.9 ⚠⚠ `§2p.8` ASSERTS A GRANT THAT DOES NOT EXIST. THE ERROR IS MINE, IT IS IN A CHARTER, AND IT IS THE CLASS I RULED URGENT THIS MORNING

`§2p.8` at `:4872` reads *"I granted **`R3`, `R5` and `R6`** with the direction analysis
'restrictive → easy grant on direction'"*, and its outcome table at `:4906` repeats it.
**`[VERIFIED BY ME AT SOURCE, THREE INDEPENDENT LINES OF MY OWN CHARTER]`:**

| line | what it says |
|---|---|
| `:4523` | `§2d.7`'s disposition table — **`R6` — "REFUSED as a `§2d.1` repair; REFERRED prospectively"** |
| `:4540` | the reasoned refusal — silence is not a departure, **condition (2) has NO OBJECT**, `§2d` stands |
| `:4567` | `§2d.8`'s outcome table — **refused: "`R6` (no object; referred prospectively)"** |

**`R6` WAS NEVER GRANTED. Zero occurrences of a grant of it anywhere in 5,699 lines**, and
heat-transfer's own record says the same independently at `T23G2_RESULTS.md:447`, `:471`,
`:802`.

**THE MECHANISM IS VISIBLE IN MY OWN TEXT AND IS WORTH MORE THAN THE CORRECTION.** The
**direction analysis** at `:4462-4465` was published in advance for `R3`, `R5` **and** `R6` —
all three carry *"easy on direction"*. `§2p.8` correctly identified the flaw in **that
reasoning** and then attached it to *"the grants I made"*. **`R6` had a direction analysis and
never a grant.** *I generalised from the set I had ANALYSED to the set I had GRANTED, and those
were different sets. The defect §2p.8 identifies is real and does cover all three analyses;
the word "granted" is what is false.*

> **STRUCK — `§2p.8`'s "`R3`, `R5` and `R6`" and its table row `:4906`. THE `§2p.3(e)` DEBT IS
> OWED BY `R3` AND `R5` AND BY NOTHING ELSE.** `R6` has **no grant, therefore no output,
> therefore nothing to disbelieve**; its `§2p.3(e)` obligation is a **CONDITION on the repair
> if and when it lands**, in the successor rung's pre-registration where `§2d.7` referred it.
> **The original sentence is not rewritten and stays legible at `:4872`.**

**AND THE SHAPE IS THE ONE I NAMED URGENT AT `§2w.3` THIS MORNING: A FALSE RECORD, NOT A
DISCLOSED HOLE.** A charter asserting that a refused item was granted is exactly *"a false
claim propagated into a second record nobody would think to audit"* — and this time the second
record is the constitution. **A lane found it because I asked it to check the clause against
its own table before acting on it.**

### §2p.10 `§2p.3(e)` IS DISCHARGED FOR `R3` AND `R5`, DRIVEN THROUGH THE PRODUCTION PATH

`analyse_t23g2.py` was **not edited**; only inputs were constructed (`§2p.3(d)`). Positive and
negative limbs ran in the **same invocation**. Both repairs are confirmed **SHIPPED** at HEAD —
`R3` at `:997`/`:1085`/`:1269` (`c2ce64a5`, amended by `73f2e51a`), `R5` at `:910-926` and
`:413`/`:529`/`:555` (`91bb04f8`).

- **`R3` / `G-ORDER` — 3 positive limbs `PASS`, 5 negative limbs refuse or void.** The
  positives include **both band edges at the minimum verdict-changing margin** — p = 0.500001
  and p = 1.499999 → `PASS`; p = 1.5001 → `GATE FAIL`; non-monotone ladder → `NOT A RESULT`,
  `OSCILLATORY`; two empty-input arms **REFUSED**.
- **`R5` — 18/18 registered controls `PASS`** (six quantities × three levels) on the real,
  untouched artifacts, **plus the live y+ plant**: 181,694 vectors planted, expected ratio
  `1.000616810` = √(1+PLANT), **worst relative miss `2.219e-16`** across all four wall patches.
  The negative limbs are genuine: a **blind reader** built by setting a value to `1e20` so that
  `float(v) + PLANT == float(v)` was **REFUSED**; a **stale unplanted copy** through the real
  reader returned ratio **exactly 1.0**, proving the discriminator carries signal. The run tree
  is clean afterwards — **0 `.plant` files** remain.

**THE HONEST GAP, RECORDED BECAUSE A DISCHARGE THAT HIDES ITS LIMIT IS NOT A DISCHARGE:** the
y+ control's **refusal** path is demonstrated at the `_plant_u_file` layer, **not end to end** —
driving `control_yplus_field_reader` itself to refusal would have required editing production
code or corrupting the real case's `U`, and neither is permitted. **That limb remains
undemonstrated and is named rather than counted.**

### §2aa `G-ORDER`'s `GATE FAIL` IS REACHABLE ON ONE SIDE ONLY, AND NO RECORD SAYS SO

**`[MEASURED, AND VERIFIED BY ME AT BOTH SOURCES]`:** `analyse_t23g2.py:65` sets
`ORDER_BAND = (0.5, 1.5)`; `scripts/roache_triple.py:170` sets `STAGNANT_FLOOR = 0.5`.
**The band's lower edge and the triple's stagnation floor are the same number.**

| p | triple state | `G-ORDER` |
|---|---|---|
| ≤ 0.04 | DEGENERATE | `NOT A RESULT` |
| 0.10 – 0.499999 | **STAGNANT** | **`NOT A RESULT`** |
| 0.500001 – 1.5 | CONVERGING | **`PASS`** |
| > 1.5 | CONVERGING | **`GATE FAIL`** |

> **There is NO value of `p` that produces a low-side `GATE FAIL`: every `p` below the band is
> `STAGNANT` or `DEGENERATE` and rule 5 voids the row first. The registered clause "CONVERGING
> but outside the band → `GATE FAIL`" HAS AN EMPTY LOWER HALF.**

**THIS IS NOT A DEFECT AND I WILL NOT CALL IT ONE.** `NOT A RESULT` is **strictly stricter**
than `GATE FAIL`, and rule 5 permits exactly that direction. **`R3` is sound.** But `§2d.7`
recorded `R3`'s direction as *"restrictive — it can only ADD a `GATE FAIL`"*, and **on half its
domain it adds a `NOT A RESULT` instead.** A future reader who tries to demonstrate
`G-ORDER`'s failure branch on the low side **will fail to and will not know why.**
**Reported, not gated** (her ~20:00Z default): a **physics finding about the instrument**, not
a rule change.

### §2ab ⚠⚠ THE DISCRIMINATOR THIS FORCES ME TO STATE, BECAUSE IT BEARS ON A RULING I MADE THIS MORNING

This morning I withdrew `VR3`'s `PASS` to `NOT A RESULT` partly because its `GATE FAIL` was
**unreachable in the implementation**. Hours later I record that `G-ORDER`'s `GATE FAIL` is
**also unreachable on half its domain** — and call `G-ORDER` sound. **Those two must be
reconciled or one of them is wrong.**

> **RULED — `§2ab`: AN UNREACHABLE VERDICT BRANCH IS A DEFECT WHEN NOTHING REACHES IT, AND A
> PROPERTY WHEN A STRICTER VERDICT PREEMPTS IT. The test is not "can this branch fire" but
> "IS THERE AN INPUT THE GATE ANSWERS WRONGLY BECAUSE THE BRANCH DID NOT FIRE."**
> - **`VR3`:** the only non-`PASS` return was both-totals-zero. **Nothing preempted `GATE
>   FAIL`; the gate simply could not fail**, so its `PASS` was **uninformative — it could not
>   have come out any other way.** Defect.
> - **`G-ORDER`:** every input that would have taken the low-side `GATE FAIL` **takes `NOT A
>   RESULT` instead, from a gate that DOES fire, in rule 5's one permitted direction.** No
>   input is answered wrongly. **Property.**

*The discriminator strengthens this morning's ruling rather than weakening it: had `VR3`'s
unreachable branch been preempted by anything at all, I would have had to rule the other way.
It was preempted by nothing.*

### §2ab.1 AND THE `VR3` REGISTRATION'S OWN ARITHMETIC WAS WRONG — 11 HAS NO SUPPORT

`VR3_PREREGISTRATION.md:19` registers *"the **11** sites"*, assuming **one** removal for
`grade_vmfl076`. **There are TWO such files** — `VMFL076/` and `VMFL076-R2/`, each contributing
one site at `:677`. **The number 11 has no support anywhere; it is 12.** `VR3-R2` registers
**N = 12** with that arithmetic on its face.

**`VR3-R2` IS `GATE FAIL`** (`8515ea51` frozen; `7c14d198` graded): **12 of 12 sites
classified, UNGUARDED = 4, GUARDED = 8**, and the four are **one function — `probe_series` —
replicated into four graders**, each a `LEXICAL sorted(glob.glob(...))` over
`postProcessing/*/U/gateProbes` with **no `len()` guard in that function**. **It widens a
CANDIDATE set 19 → 23 and MOVES NO VERDICT** — `DEAD_LEVER_AUDIT` §7.3's standing measurement
that every hazard case produced exactly one start-time directory still holds.

| item | outcome |
|---|---|
| `§2p.8`'s "`R3`, `R5` and `R6`" | **STRUCK — `R6` was REFUSED at `:4523`/`:4540`/`:4567`** |
| the `§2p.3(e)` debt | **two items, not three** |
| `R3` / `R5` | **`§2p.3(e)` DISCHARGED** through the production path, both limbs, same run |
| `R6` | **prospective — no grant, no output, nothing to disbelieve** |
| the y+ refusal limb | **NOT demonstrated end to end — named, not counted** |
| `G-ORDER`'s low-side `GATE FAIL` | **EMPTY — `ORDER_BAND[0]` == `STAGNANT_FLOOR` == 0.5.** Reported, not gated |
| **`§2ab`** | **unreachable + nothing preempts = DEFECT; unreachable + stricter preempts = PROPERTY** |
| `VR3`'s "11" | **no support — it is 12** |
| **`VR3-R2`** | **`GATE FAIL` — 4 of 12 UNGUARDED, one function replicated four times** |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |

---

## Amendment — v1.51, 2026-09-03 — **§2ac THE D12RLX CLASS IS RULED ON ITS SECOND SPECIMEN: A LANDED VERDICT WHOSE LOAD-BEARING PREMISE IS MEASURED FALSE IS `NOT A RESULT`, AND A GATE THAT FIRED AND RETURNED A FALSE VALUE IS WORSE THAN ONE NEVER WRITTEN · §2ad DEMOTING YOUR OWN `GATE FAIL` IS PERMITTED AND CARRIES A DISCLOSURE BURDEN THAT DEMOTING YOUR OWN `PASS` DOES NOT · §2ae "A CORRECTION FILED ONLY AT THE FOOT DOES NOT REACH THE READER OF THE CLAUSE" IS RIGHT, AND THE FIX IS NOT TO ANNOTATE FROZEN BYTES**

**Lines whose number changed above this section: 0.** Pure append; pre-append digest
`9a0e4573f746fc297c1e85b5b272ad8d` at 5,844 lines. **Zero solver compute; 0 core-min; $0.00.**
**Nothing is re-graded by this amendment — it states the law; the demotion is
ansys-verification's to take** (`§2z.3`: the owning team demotes its own verdicts; this team
rules the class).

### §2ac THE SECOND SPECIMEN, AND IT SHARPENS `§2w` RATHER THAN REPEATING IT

`§2w` ruled the first limb: *a landed verdict whose load-bearing gate was NEVER IMPLEMENTED is
`NOT A RESULT`.* **The ansys specimen is a different and worse shape: the gate WAS implemented,
DID fire, and returned a FALSE VALUE.**

**`[VERIFIED BY ME AT SOURCE, ansys-verification's own record]`:** *"L3 excursion 1.2037e-01 m
= **192.60 % of the band**, final-window **3.722 %**, while its **plateau limb read
4.332e-10** and row #54 records **'plateau MET at every level'**."*

> **THE NUMBER THAT DECIDES THIS IS `4.332e-10`.** The plateau limb did not report a marginal
> pass. **It reported a near-exact ZERO for a quantity that was moving by 192.60 % of its own
> band** — because it watched an **upstream supersonic station that causally cannot see the
> shock**. **That is `CLAUDE.md` rule 3's shape in a graded gate: a zero from a reader not
> shown able to see a non-zero.** Three guards, one geometry, **all defeated identically** —
> which is not three failures but **one blind station wearing three coats**.

> **RULED — `§2ac`: A LANDED VERDICT WHOSE LOAD-BEARING PREMISE IS ASSERTED TRUE IN ITS OWN
> RECORD AND IS MEASURED FALSE IS `NOT A RESULT`, WHATEVER ITS PRINTED LABEL WAS.** Rule 5's
> one permitted direction applies: `PASS` → `NOT A RESULT` and `GATE FAIL` → `NOT A RESULT`
> are both legal; **the reverse is not, ever.**
>
> **AND THE THREE CASES RANK, WHICH `§2w.1` DID NOT YET SAY:**
> 1. **a gate never implemented** — *silent*; produces no verdict (`§2w`);
> 2. **a gate implemented and unreached** — *inert*; produces no verdict on that branch, and if
>    a **stricter** verdict preempts it, that is a **PROPERTY**, not a defect (`§2ab`, today);
> 3. **⚠ a gate implemented, FIRED, and FALSE** — ***asserts***. **It manufactures a positive
>    claim of soundness, and a false assurance is indistinguishable from a true one at the
>    point of reading.** **This is the worst of the three and it is the only one that
>    propagates**, because downstream records quote the assurance rather than re-deriving it —
>    exactly as `COST_CALIBRATION.md:361` quoted `G-RLX-0`'s non-existent pass in the first
>    specimen.

### §2ac.1 PARTIAL SCOPE IS CORRECT, AND ansys STATED IT BEFORE BEING ASKED

**A SURVIVING FINDING IS NOT A SURVIVING VERDICT, and the two must not be traded for each
other.** The row's **graded verdict** is `NOT A RESULT` — rule 5 step (1) voids the row the
moment any level is not plateaued, and the finest level is not. **But the flagship finding
—** *the shock moves AWAY from the reference under refinement* **— rests on `L1 → L2`
(+1.73 % → −4.06 %), movement between two SETTLED levels, and SURVIVES** as a **physics
finding, reported not gated** (Sanaa's ~20:00Z taxonomy). **The `L3` point and the −12.92 %
Richardson extrapolation are CONTAMINATED and do not survive**, because the extrapolation
consumes the non-converged level — and rule 5 forbids quoting a GCI over values that are not
monotone for the same reason.

> **RULED: a `NOT A RESULT` voids the ROW's VERDICT, never the team's MEASUREMENTS. Findings
> resting wholly on settled levels are preserved, labelled as findings, and may not be
> re-described as verdicts; anything consuming the voided level goes with it.** *Ansys drew
> this line itself, correctly, before any ruling reached them.*

### §2ad ⚠⚠ THE ASYMMETRY THE CHIEF CORRECTLY FLAGGED, AND IT IS THE HARD PART

Row #55 was **`PASS` → `NOT A RESULT`**: **self-adverse** — it cost the team a credential.
Row #54 is **`GATE FAIL` → `NOT A RESULT`**: **rule 5 permits it identically**, but it
**RELIEVES the demoting team of a recorded failure.** *Same direction under the rule, opposite
incentive.* **A rule blind to that difference would let any team launder every failure into
"we do not know."**

> **RULED — `§2ad`: RULE 5'S PERMISSION IS SYMMETRIC AND THE EVIDENTIARY BAR IS IDENTICAL. WHAT
> DIFFERS IS THE DISCLOSURE BURDEN. A demotion that relieves the demoting team of a recorded
> failure must, on the face of the demotion:**
> 1. **state that it does so** — *"this demotion vacates a `GATE FAIL` against this team"*;
> 2. **preserve every finding of the vacated `GATE FAIL` that rests on settled levels**, so the
>    adverse content is not lost with the label;
> 3. **name what would have to be true for the `GATE FAIL` to be REINSTATED** — the condition,
>    stated in advance, so a later re-run can settle it rather than re-argue it.
>
> **No such burden attaches to demoting one's own `PASS`: the act is already against interest,
> and requiring extra ceremony of it would tax exactly the behaviour this lab wants.**

**AND THE PRECEDENT THE CHIEF IDENTIFIED IS WHY THIS CLAUSE CAN BE PERMISSIVE RATHER THAN
SUSPICIOUS.** Ansys ran **the unfavourable one first, with zero discretion** — demoting the
frozen comparator's **own printed `PASS`** on measured evidence, losing a credential by it.
**A team that has already demoted its own `PASS` on this evidence has earned the presumption
of good faith when it demotes its own `GATE FAIL` on the same evidence.** *The precedent is not
the rule and cannot be — the disclosure burden binds a team with no such record just the same —
but it is the reason the rule is written as a duty to disclose rather than as a permission to
withhold.*

### §2ae THE REPAIR FORM — ansys `§30` IS RIGHT AND THE OBVIOUS FIX IS THE WRONG ONE

Their `§30`: ***"a correction filed only at the foot does not reach the reader of the
clause."*** **Correct, and it names a real gap in rule 6**, which requires the dated amendment
at the foot and says nothing about the reader who never scrolls there. *I created an instance of
it myself today: `§2p.8`'s false sentence is struck at v1.50 and a reader of `:4872` still sees
no mark.*

**THE OBVIOUS FIX IS FORBIDDEN AND MUST BE NAMED AS FORBIDDEN**, because it is what a
well-meaning successor will reach for: **annotating the frozen artifact at the site.** For an
**executable comparator** that breaks the sha, and rule 2 fixes the grading path **by sha** —
so an in-place marker would destroy the very property that makes the freeze evidence. **Never
annotate frozen bytes.**

> **RULED — `§2ae`: THE CORRECTION MUST BE REACHABLE FROM WHERE THE NUMBER IS READ, NOT FROM
> WHERE IT WAS WRITTEN.** A reader about to believe a verdict consults the **REGISTER ROW** and
> the **RESULTS record** — never the comparator's source. **So the obligation lands there: a
> demoted verdict's REGISTER ROW carries the demotion IN ITS VERDICT CELL**, and the results
> record carries it **at the head of its section**, not in an addendum at the foot of a
> different document. **The amendment at the foot remains required and remains insufficient by
> itself.** *This renumbers nothing, edits no frozen byte, breaks no sha, and costs one cell.*

### §2af CLASS SIZE — AND I APPLY MY OWN `§2p.5` AGAINST MY OWN CLAUSE

D12RLX is one specimen. **Rows #54 and #55 are ONE specimen with two rows** — the same
unconverged finest level, one geometry, three guards defeated identically. **That is TWO
instances, and `§2p.5` says two instances is a PATTERN AND NOT A CLASS.**

> **NO SWEEP IS ORDERED.** I have refused a sweep on a two-member population twice today and I
> refuse my own here. **`§2ac` is stated forward-only**, and under Sanaa's clause 2 it
> **schedules no backfill**: it creates no migration work for any team, and it applies to
> verdicts as they are taken. *A supervisor who applies a threshold only to other teams' classes
> has no threshold.*

**BLOCKED RESULT NAMED, per her governance bar:** ansys-verification's **row #54 verdict**, held
by them pending this ruling precisely because they would not re-grade a landed verdict
unilaterally. **This ruling unblocks it.** The action is theirs; this team audits the RESULT,
not the work.

| item | outcome |
|---|---|
| the class | **RULED — premise measured false ⇒ `NOT A RESULT`, whatever the printed label** |
| the three cases, ranked | **silent (never implemented) < inert (unreached) < ⚠ ASSERTS (fired and false)** |
| why the third is worst | it **manufactures a positive claim of soundness** and **propagates** into records that quote it |
| the deciding number | **plateau limb `4.332e-10`** against **192.60 % of band** — rule 3's false zero, inside a graded gate |
| partial scope | **UPHELD** — `L1→L2` finding survives as a FINDING; `L3` and the −12.92 % Richardson go with the voided level |
| `GATE FAIL` → `NOT A RESULT` | **PERMITTED**, identical evidentiary bar, **plus a three-limb disclosure burden** |
| `PASS` → `NOT A RESULT` | **no added burden** — already against interest |
| ansys's precedent | **the unfavourable demotion ran first, with zero discretion** — the reason `§2ad` is a duty to disclose, not a licence to withhold |
| **`§30`'s complaint** | **UPHELD** — and the fix is the **register row's verdict cell**, never an annotation on frozen bytes |
| sweep | **REFUSED — two instances is a pattern, `§2p.5`, applied against my own clause** |
| who acts | **ansys-verification.** This amendment states the law and re-grades nothing |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |

---

## Amendment — v1.52, 2026-09-03 — **§2ag RUNG 0's `§2d.1` PETITION IS REFUSED ON THE INSTRUMENT, BECAUSE THERE IS NO DEPARTURE TO REPAIR — THE COMPARATOR IMPLEMENTS ITS REGISTRATION FAITHFULLY AND IS THE MOST HONEST ARTIFACT IN THE REFERRAL. THE REGISTERED STRIKE PATH IS REFUSED BY NAME. THE ROUTE IS A SUCCESSOR, AND cfd's ORDERED CONTROL PROGRAMME SHRINKS TO ONE LIMB.**

**Lines whose number changed above this section: 0.** Pure append; pre-append digest
`e8f25af23567534b3382ac6153000512` at 5988 lines. **Zero solver compute; 0 core-min; $0.00.**
**No gate, threshold, band, cap or label created, moved or retired; nothing re-graded.**

### §2ag ⚠⚠ FIRST, A CORRECTION TO THE REFERRAL'S FRAMING, AND IT RUNS IN cfd's FAVOUR

The referral reached me as *"the frozen comparator hardcodes `PENDING`, omits the gate from the
conjunction, and **HAS NO PASS BRANCH AT ALL** — for grid or rung."* **Every clause of that is
literally true and together they read as an indictment. READ AT SOURCE, THE COMPARATOR IS THE
MOST HONEST ARTIFACT IN THIS REFERRAL.**

`[VERIFIED BY ME AT SOURCE]` `analyse_rung0.py` **does** carry `PASS` branches — `R0_G1` at
`:448`, `R0_G2a` at `:462`, `R0_G3` at `:492`, `R0_G4` at `:505`. What it withholds is the
**grid and rung** `PASS`, **deliberately, with its reason printed at `:513-518`**:

> *"RUNNABLE GATES ALL HELD. That is NOT the rung's `PASS` — R0-G2b is unbuilt… §4 defines
> `PASS` as the conjunction INCLUDING R0-G2b, which cannot run. **Reporting `PASS` here would
> be reporting a conjunction one of whose conjuncts was never evaluated.**"*

And its docstring **anticipates rule 1's prohibition and disclaims it in advance** (`:21-24`):
*"`PENDING` — the display/queue state meaning NOT YET RUN. It is NEVER [used to soften]… What
`PENDING` covers is the one conjunct nobody has built yet."*

**`[VERIFIED]` the registration agrees at `:228`: `PASS` = R0-G1, R0-G2a, R0-G2b hold on all
four grids.** **THE COMPARATOR AND THE REGISTRATION DO NOT DIVERGE. THEY AGREE.**

> **RULED — `§2ag`: THE `§2d.1` PETITION IS REFUSED ON THE INSTRUMENT, NOT ON THE MERITS.
> `§2d.1` repairs a DEPARTURE of the comparator from its frozen registration. HERE THERE IS
> NO DEPARTURE — not even the silence `§2d.5` excludes. Condition (2) has NO OBJECT, exactly
> as it had none for `R6`.** *This is `V-52`'s shape a second time: I decline a grant because
> none is needed, and recording one would falsely assert that something was wrong with a
> comparator that behaved correctly.*

### §2ag.1 ⚠⚠ AND THE REGISTERED ESCAPE HATCH IS REFUSED BY NAME, BECAUSE ITS TRIGGER IS NOT WHAT HAPPENED

The registration **pre-registered its own amendment path** (`:114-116`, `:508`): *"if only the
comparison limb is meant, say so and **R0-G2b is struck by addendum** and nothing else moves."*
**That is registered text, so a strike would not be an inference from silence** — which is
precisely what `§2d.7` requires of a rollup exclusion.

**BUT ITS TRIGGER CONDITION IS A READING QUESTION — *"if only the comparison limb is meant"* —
AND WHAT ACTUALLY HAPPENED IS A RUNNABILITY EVENT.** `cases/committee-grids/foam_to_ugrid.py`
**now EXISTS** — 53,741 bytes, tracked at HEAD, added by `d1c5aa5d` — and R0-G2b has been
**MEASURED to hold on all four grids**.

> **REFUSED BY NAME: R0-G2b MAY NOT BE STRUCK NOW. A limb becoming RUNNABLE is not evidence
> that it was never MEANT.** Striking it at the moment it became runnable **and passed** would
> convert *"we cannot run this"* into *"we do not need this"* **on the strength of the very
> measurement that removed the excuse.** By `§2d.7`'s ruling a rollup exclusion is **ALWAYS
> permissive**; here it would also be **self-serving and perfectly timed**, which is the worst
> available combination. *The hatch was registered for an unrunnable limb. The limb runs.*

### §2ag.2 THE ROUTE, AND IT IS CHEAPER THAN WHAT WAS ABOUT TO BE BUILT

**A SUCCESSOR REGISTRATION.** It registers R0-G2b as **runnable**, brings the now-existing
instrument **INSIDE the grading path** (rule 2 — the path is fixed at the pre-registration
commit, and an instrument outside it can produce a **measurement** but never a **verdict**), and
grades the conjunction §4 always demanded. **The work is a mesh round-trip: no solver, and the
registration itself prices the second limb at *"under two core-minutes."***

**This is `R6`'s disposition applied to a better-placed case: a gap in a registration is closed
by THE NEXT REGISTRATION, not by repairing the rung that revealed it.** Nothing is struck,
nothing is excused, and the conjunction is graded as written.

> **UNTIL THE FROZEN GRADING PATH EMITS IT, R0-G2b's `PASS` IS A MEASUREMENT AND NOT A VERDICT
> — reported, not gated.** 21 controls and refusal-verified under `-O` make it a **good**
> measurement. They do not make it a graded one. **cfd must not report Rung 0 or any grid as
> `PASS` on its strength**, and to their credit they have not.

### §2ag.3 cfd's ORDERED CONTROL: LIMB (i) IS KEPT AND REPURPOSED; THE REST IS NOT NEEDED

Their supervisor ordered a two-limb instrument to satisfy condition (2). **Condition (2) has no
object, so the programme built to satisfy it is not owed.** But **limb (i) survives for a
better reason than the one it was ordered for:**

> **KEEP: the UNMODIFIED frozen comparator over a synthetic all-gates-hold case must still emit
> `PENDING`. NOT as a licence for a repair — as A FALSIFIER OF THE READING I JUST MADE.** I
> have certified the comparator faithful **from its source**. If that case returns `PASS`, my
> `§2ag` is wrong and the petition reopens. **My own check-3 discipline forbids me to certify
> an instrument by inference when driving it is nearly free.**
>
> **NOT OWED: the mirror mutation, and the repair programme it belonged to.** *(Recorded, because
> it is the right instinct and will be owed the first time a genuinely PERMISSIVE repair is
> granted: `§2p.3(e)` requires a POSITIVE control of a RESTRICTIVE repair, and its mirror — a
> permissive repair must show a case that DESERVES the failing verdict STILL RECEIVES IT — has
> no clause yet. Their pair proves the UNREPAIRED comparator can fail; it would not have proved
> the REPAIRED one still could. **No result is blocked, so under Sanaa's bar this is reasoning
> on the record and NOT a clause** — it is earned the day a permissive repair is actually
> granted.)*

### §2ag.4 THE STRING LIMB IS ANSWERED BY `§2ae`, RULED ONE HOUR AGO

`analyse_rung0.py:467` states `foam_to_ugrid.py` **"DOES NOT EXIST"** and the file is
**measurably on disk and tracked**. Their demonstrable-error near-identity reading is sound —
**but it must not be exercised on the frozen bytes.** `§2ae`: **never annotate a frozen
artifact**; the correction goes **where the number is READ** — the **results record's section
head**, and the successor registration, which states it truly from birth. **The frozen file
keeps its false sentence and its sha, and no reader meets the sentence without meeting the
correction.**

**And the general test for any demonstrable-error repair, stated because it is what makes the
class safe: a demonstrable error is one whose correction CHANGES NO GATE OUTCOME. If correcting
the string would move a verdict, it is not a typo — it is a gate change wearing a typo's
clothes.** Here the string is read by no gate, so the class holds.

### §2ag.5 THE SUPERVISOR'S REFUSAL TO SELF-AUTHORIZE IS UPHELD, AND IT IS THE MODEL

His words: *"nothing a verdict depends on may be repaired on the authority of the verdict it
produces… I supervise this rung; the repair runs toward my own rung's success — **the worst
possible configuration**."*

> **UPHELD IN FULL, AND ADOPTED AS THE OPERATIVE STATEMENT OF WHY `§2d.1` GRANTS ARE ROUTED
> OUTWARD.** He identified the conflict **before anyone raised it**, refused the authority he
> could have taken silently, **and ordered the instrument against his own preferred outcome.**
> *He also happened to be petitioning for a repair he did not need — and that is a far better
> failure than the one he refused to commit.*

### §2ag.6 THE POPULATION-BLINDNESS SPECIMEN — RECORDED, NO CLASS DECLARED, NO SWEEP

**A single pyramid in ONE of four grids caught dead-code copying that the other three would
have shipped** — the rung's **THIRD** population-lacking-the-failure-mode bite. **A clean
`§2p`-family specimen and it is filed as one.**

**The general shape, stated and not legislated: WHERE A CHECK'S POPULATION IS DRAWN FROM REAL
DATA, ITS COVERAGE OF FAILURE MODES IS ACCIDENTAL. Three times in one rung the real grid caught
what the population would have missed — and the third time it turned on ONE cell of one type in
one of four grids. THAT IS LUCK, AND LUCK IS NOT A CONTROL.** The cure is not a bigger
population; it is a **PLANTED** one.

**NO CLASS IS DECLARED AND NO SWEEP IS ORDERED.** Three bites of one failure mode **inside one
rung** is evidence about **that rung's population discipline**, not three independent
instances — and **no result is blocked**, since all three were caught. **Under Sanaa's bar that
makes it a specimen and a lesson, not a clause.** *If a fourth lands where the population DID
ship the defect, that is a blocked result and the clause is earned that day.*

| item | outcome |
|---|---|
| the referral's *"no `PASS` branch at all"* | **CORRECTED — four gate-level `PASS` branches exist; the grid/rung `PASS` is withheld DELIBERATELY, with its reason printed** |
| `§2d.1` petition | **REFUSED ON THE INSTRUMENT — no departure; condition (2) has no object** |
| the registered strike of R0-G2b | **REFUSED BY NAME — a limb becoming RUNNABLE is not evidence it was never MEANT** |
| the route | **SUCCESSOR REGISTRATION** — instrument inside the grading path, conjunction graded as written, under two core-minutes |
| R0-G2b's measured `PASS` | **a MEASUREMENT, not a verdict** — reported, not gated, until the frozen path emits it |
| cfd's control programme | **shrinks to ONE limb, repurposed as a falsifier of MY reading** |
| the permissive-repair mirror control | **reasoning on the record, NOT a clause** — nothing blocked |
| the string limb | **legal, but never on frozen bytes — `§2ae`: the results record and the successor** |
| the supervisor's refusal | **UPHELD and adopted as the model** |
| population blindness | **specimen filed; NO class, NO sweep** |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |

---

## Amendment — v1.53, 2026-09-03 — **§2ah THE THRESHOLD QUESTION IS RULED IN THE PETITIONER'S FAVOUR AND AGAINST ITS OWN FILING: `§2d.1` DOES NOT REACH AN OFF-GRADING-PATH CHANGE, SO NO PETITION WAS NEEDED — BUT `§2d` ALREADY IMPOSES A FOUR-PART DISCLOSURE THERE, AND "OFF-PATH" IS THE ONE CLAIM A TEAM HAS AN INTEREST IN, SO IT IS MEASURED AND NEVER ASSERTED · §2ai T25R6a's EQUIVALENCE PREDICATE IS TAUTOLOGICAL AND THE REPAIR IS GRANTED IN THE SUPERVISOR'S STRENGTHENED FORM, WITH FIVE CONDITIONS AND A NARROWING THE PETITION DID NOT RAISE: THIS GRANT WOULD NOT BE AVAILABLE IF IT LANDED ON A `PASS` · §2aj A SELFTEST THAT NEVER REACHES ITS EMISSION PATH — THE THIRD QUESTION, AND THE LAB HAD BUILT CONTROLS FOR ONLY THE FIRST TWO**

**Lines whose number changed above this section: 0.** Pure append; pre-append digest
`5e5e813772a36bd4fdbe19c5f0955989` at 6142 lines. **Zero solver compute; 0 core-min; $0.00.**
**No gate, threshold, band, cap or label is created, moved or retired by this amendment, and
nothing is re-graded by it.** One **registration-time expectation** is created at `§2aj`,
forward-only, with **no backfill and no sweep**.

**Two petitions from heat-transfer, ruled one by one against their own `§10`/`§8` lists as they
asked.** Every fact this ruling turns on was **re-derived by me at source**, not taken from
either document; where I checked something that could have refuted a petition, I say so and give
the number.

---

### §2ah — **THE THRESHOLD RULING. `§2d.1` DOES NOT GOVERN AN OFF-GRADING-PATH CHANGE, AND `§2d` SAYS WHAT DOES — IN A SENTENCE THAT HAS BEEN IN THIS CHARTER SINCE 2026-08-19**

`T25R6cR2_2D1_RECORD_EMISSION_PETITION.md` `§0` asks the question first because it may dispose of
everything below it: *"Does §2d.1 govern a post-compute repair that is NOT on the grading path —
and if it does not, what does?"* It offers three readings and **declines to choose between them**,
petitioning under the narrower one *"so that a narrower rule is applied rather than a broader one,
which is the direction that cannot go wrong."*

**Its reading (a) is correct, and the answer was already written.** `§2d.1`'s grant opens *"A
change **on the grading path** made after the first graded solve…"* (`:1936`). A change that is
not on the grading path is not inside the clause and needs no exception from it.

**But (a) is stated one degree too weakly, and the correction matters more than the ruling.** The
petition reads (a) as *"nothing forbids the repair and no petition was needed."* `§2d` does not
merely fail to forbid it. **It affirmatively permits it AND imposes a duty**, at `:1842-1845`:

> *"**Instrumentation that is NOT on the grading path may be added later, and when it is, the
> record carries a dated disclosure naming what was added, when, what was readable at that
> moment, and which findings rest on it and which do not.**"*

And `§2d`'s own boundary test, at `:1908-1910`, is the discriminator:

> *"**The boundary in one question, asked at the moment of the edit: could this change move a
> number that a verdict depends on?** If yes, it belongs before the first solve. **If no, it
> belongs in the record with a date on it.**"*

> **RULED — `§2ah`: A POST-COMPUTE CHANGE THAT IS OFF THE GRADING PATH NEEDS NO `§2d.1`
> EXCEPTION, NO PETITION AND NO RULING. `CLAUDE.md` RULE 6 SUPPLIES THE FORM — dated amendment
> at the foot, version bump, `lines whose number changed above this section: 0`, original struck
> and never rewritten. `§2d:1842-1845` SUPPLIES THE CONTENT — a dated disclosure naming (i) what
> changed, (ii) when, (iii) what was readable at that moment, and (iv) which findings rest on it
> and which do not. Reading (c) and reading (a) are not rivals: (c) is the form and (a) is the
> jurisdiction, and both are owed.**
>
> **"NO PETITION WAS NEEDED" IS NOT "NOTHING WAS OWED", and a team that reads it as the second
> has taken the wrong half of this ruling.**

#### §2ah.1 ⚠ **THE NARROWING THAT KEEPS THIS FROM BECOMING A LOOPHOLE, AND IT IS THE WHOLE PRICE OF THE ROUTE**

**"This change is off the grading path" is the single claim a team has an interest in making**,
because it is the claim that dissolves the entire freeze. `§2d.1`'s condition (2) exists for
exactly this reason — an error found by something that grades nothing *"cannot have been selected
to move a verdict in a wanted direction, because the thing that found it does not know which
direction that is"* (`:1944-1947`). The off-path route must not become the way around that.

> **RULED — `§2ah.1`: OFF-PATH STATUS IS MEASURED, NEVER ASSERTED. A change taken through `§2ah`
> rather than through `§2d.1` carries a demonstration on the record that the change moves no
> graded number. WHAT THE OFF-PATH ROUTE SAVES IS THE RULING, NOT THE EVIDENCE: the measurement
> `§2ah` requires is the same measurement `§2d.1`(3) would have demanded, so the cheap route is
> cheap in governance and not in rigour.**

**THE STANDARD DEMONSTRATION, AND I NAME IT AFTER THE CONDUCT THAT PRODUCED IT — THE `T25R6cR2`
PROBE.** Heat-transfer did this before asking, unprompted, and it is the reference form:

1. **Copy the frozen instrument.** The frozen file is not touched. Its blob is re-verified
   afterwards — here `eb363769bb18dd0550b551e6fa5ba457f002cfb9`, identical at the freeze commit
   `f67ade8d` and at HEAD.
2. **Apply the one change to the copy, and nothing else.**
3. **Drive the copy through the PRODUCTION path against the REAL case directory** — not against
   a fixture, because a fixture cannot show what the real gates print.
4. **`diff` EVERY printed gate line against the frozen run's landed output.** Byte-identical
   ⇒ the change is off the grading path, **measured**. One differing digit ⇒ it is on the path,
   and `§2d.1` governs after all.

*Their probe returned byte-identical output across the planted-zero lines, the rule-4 line,
`C-R2-1`, both plateau halves and their two normalisations, the graded statistic, `rho`, `R-R2-1`,
`R-R2-4` and the predicted-vs-actual line. **What moved: nothing. Not one digit of one gate.***

#### §2ah.2 — **ITEM B: THE BLOCKED-RESULT BAR IS NOT MET, AND ITEM C THEREFORE NEEDS NO GRANT**

The petition **led with the evidence against itself**, which is the standard `§2d.11.0` set and
which I record again because it keeps being the reason these documents are rulable. Its sweep of
`scripts/`, `sdk/` and `verification/` finds **no consumer of any `*_VERDICT.json` but the graders
that write them**; `scripts/check_comparator_freeze.py` dates freezes against `DONE.<CASE>`
markers, not verdicts; `scripts/queue_runner.py` reads no grader exit code. And the rung's verdict
— **`GATE FAIL`, `rho = 1.103859`** — is landed at `286276a1` as the frozen grader's own stdout
**with the traceback intact**, under Sanaa's 2026-08-26 universal rule that bookkeeping never
voids physics.

> **RULED — item B: THE BAR IS NOT MET. No result is blocked by Defect A.** Under Sanaa's
> 2026-09-03 ~20:00Z reform the team decides locally and records the decision as a lesson — and
> **`L-470` already exists at `b672601f`**, so the disposition costs nothing and is already paid.
>
> **RULED — item C: NO GRANT IS GIVEN, BECAUSE GIVING ONE WOULD MISSTATE THE LAW.** The
> one-character repair is heat-transfer's to apply under `§2ah`, on the probe it has already run,
> with `§2d:1842-1845`'s four-part disclosure and rule 6's form. **A supervisor who grants an
> exception that was not needed has taught every future reader that it was.**

**⚠ AND "NOT BLOCKED" DOES NOT MEAN "NOTHING OWED", WHICH IS WHERE THIS RULING EARNS ITS KEEP.**
`T25R6cR2_PREREGISTRATION.md:532` registers, inside `GRADING_FREEZE`, that the grader *"recomputes
and reports BOTH its git blob sha1 and the FULL sha256 of its disk bytes (L-450) into
`T25R6cR2_VERDICT.json` at grade time."* **That artifact is unreachable through the frozen path.**
It is `CLAUDE.md` rule 2's own closing sentence — *verify the frozen file is the file that ran by
hashing it against the committed blob* — and the rung satisfied it **on a different path**, by
hand, against `f67ade8d` and HEAD.

> **REQUIRED, AND IT IS ONE SENTENCE: the rung's record states that its rule-2 freeze
> verification was satisfied by hand and NOT by the registered path, and names the blob.** A
> reader must not be left to assume the registered path produced it. This alters no gate; it
> forbids one silent inference.

**ONE CONDITION ON THE LOCAL REPAIR, and it is not a formality.** The defect is that a registered
artifact could not be emitted. **The repair is not finished when the character changes; it is
finished when the file EXISTS and PARSES.** The repaired grader is re-run through the production
path and the verdict artifact is shown on disk, with its gate lines byte-identical to the landed
stdout. That costs seconds and no solver.

#### §2ah.3 ⚠⚠ **A MEASUREMENT MY OWN LANE MADE THAT CUTS AGAINST THE RULING ABOVE, AND IT FORCES A FIFTH DISCLOSURE CONTENT**

**I nearly ruled item A on the petition's own framing, and a call-chain measurement I ordered
against it changed the clause.** Recording that, because a supervisor who only publishes the
measurements that confirmed him is running a different instrument than he says.

`[MEASURED BY MY LANE AT SOURCE, STRUCTURE RE-READ BY ME]` **The gate-determination claim holds
and is structural, not contingent:** every `out["verdict"]` assignment in `grade_t25R6cR2.py` is
at `:551`, `:583`, `:702`, `:800`, `:808` — **all inside `grade()`, all above the `finish()` call
at `:826`** — and `rho` is computed at `:719`. `finish()` (def `:829`) opens by *storing* the `rc`
it was handed (`:830`). **Nothing at or after `:829` computes a gate value**, so no gate line
*can* move. The petition is right about the gates.

**BUT THE CRASH MOVED A REGISTERED NUMBER, AND THE PETITION DOES NOT CLAIM OTHERWISE BECAUSE IT
FILED THAT FACT AS A SEPARATE DEFECT.** `grade()` computed `rc = EXIT_GATE_FAIL = 3` — one of the
four codes registered at `:117-120`. The raise inside `finish()` and the unguarded `__main__`
turned it into **`1`, a value outside the registered vocabulary.** So `§2d`'s own boundary
question — *could this change move a number that a verdict depends on?* — **does not answer
cleanly "no" on the whole artifact.** It answers "no" on the **gate values** and "**yes**" on a
**registered output channel**.

**Two corrections to the petition's own citations, pinned per `§2d.5` because the quoted text IS
the instrument:** the crashing literal is at **`:863`**, not `:857` (the assignment opens at
`:856`; CPython attributes the frame to the first physical line of the implicit concatenation),
and `json.dump` is at **`:870`**, not `:869`. **Nothing substantive turns on either**, and the
ruling is pinned to the corrected lines.

> **RULED — `§2ah.3`: A CHANGE OFF THE GATE-DETERMINATION PATH BUT ON A REGISTERED OUTPUT CHANNEL
> IS STILL OUTSIDE `§2d.1`** — `§2d:1839-1841` defines the grading path as *"every band, every
> reference, every row definition, every verdict rule, the discrimination test and the mutation
> control"*, and an output channel is none of the six. **BUT `§2d:1842-1845`'s disclosure GAINS A
> FIFTH CONTENT THERE: name the registered channel that moved, and state its pre- and
> post-repair value.** Here: **the process exit code, `3` registered → `1` actual → `3` after
> repair**, and **the verdict artifact, registered at `PREREGISTRATION.md:532`, absent → present.**
>
> **⚠ AND THE NARROWING THAT MATTERS MORE THAN THE CLAUSE: "no verdict depends on this number"
> was TRUE HERE BY A FACT ABOUT TODAY'S CONSUMERS, NOT BY A PROPERTY OF THE CODE.** My lane
> verified `scripts/queue_runner.py` invokes no grader and reads no grader rc. **That is a
> consumer census, and a consumer census expires the moment somebody writes a consumer.** An
> off-path claim resting on *"nothing reads it"* is **strictly weaker** than one resting on
> *"nothing downstream computes it"*, and a record taking `§2ah` must **say which of the two it
> is standing on.**

---

### §2ai — **T25R6a ITEM 1: THE PREDICATE IS TAUTOLOGICAL. GRANTED, IN THE `§7` FORM, WITH FIVE CONDITIONS**

#### §2ai.0 WHAT I VERIFIED MYSELF, INCLUDING THE ONE FACT THAT COULD HAVE REFUTED THE PETITION

`[VERIFIED BY ME AT SOURCE]` `grade_t25R6a.py:437` reads `if r is not True and r != 0:`.
`compare()` is defined at `compare_arms_t25R5.py:253`; **`selftest()` is defined at `:295`**, so
`compare()` spans `:253-:294` and **its only `return` is `:292`, `return res`** — a dict.
A dict is never the `True` singleton and never compares equal to `0`. **The predicate is
tautologically true for every value the delegated frozen contract can return, so `equiv_ok` is set
`False` unconditionally and no run of any quality could ever have satisfied it.**

**THE CHECK THAT COULD HAVE KILLED THIS PETITION, AND I RAN IT FIRST.** The file carries
`return 0 if not fails[0] else 1` at `:319`. **Had that line been inside `compare()`, `r` could be
the integer `0`, `r != 0` would be FALSE, and the predicate would NOT be tautological — the
petition would fail on its central claim.** It is inside `selftest()`, which begins at `:295`.
*The petition asserted "exactly one `return`, at `:292`" and it is right; I checked it because a
citation that does not check out is not a departure but an assertion (`§2d.5`).*

`[VERIFIED BY ME AT SOURCE]` `T25R6a_VERDICT.json` on disk: `"verdict": "NOT A RESULT"`,
`"ground": "the equivalence control FIRED (prereg 6.4)"`, and `'fired': []` **at both levels in
the same file**. Its only `cap`-bearing keys are `rung_cap_core_min` and `what_sigma_cap_is_not` —
**`Σ CAP(C5)` was never computed**, exactly as claimed. Citations spot-checked in
`T25R6a_C5_REGRADE_RECORD.md` — `:157` the interval, `:121` `10.651858`, `:123` `7.059383`,
`:138` the `20,006.80` sum — **all four check out at the quoted line.**

#### §2ai.1 THE FOUR CONDITIONS

**(1) DEMONSTRABLE ERROR — MET, and it is arithmetic rather than judgement.** A gate no run can
pass is not a strict gate; it is a broken one. **This is `§2p.8`'s own shape, in its purest form:
a repair — or here a predicate — that is "restrictive" BY BEING BROKEN.** Rule 5's permitted
direction does not launder it: a `NOT A RESULT` produced by a predicate that cannot be satisfied
is not strictness, it is an instrument that cannot speak.

**(2) INDEPENDENT INSTRUMENT — MET ON TWO GROUNDS, AND THE FIRST IS `§2d.5`'s.** The registration
(`T25R6a_PREREGISTRATION.md` §6.4, carried from T25R5 §4) registers the `fired` channel and its
disqualifying thresholds as what gates the equivalence limb; **the code reads neither.** That is a
registered feature absent from the code — squarely the departure `§2d.5` admits, exhibited by
quotation and by measurement, both. Independently, the petition names two executable instruments
that grade nothing: the `fired` list, which `grade_t25R6a.py:436` serialises into the artifact and
`:437` then **discards**; and the rule-3 planted-zero control, **`PLANT = 1.234e-03` K placed
ABOVE the `E1` disqualifying threshold `1.000e-03` K on purpose**, 16/16 SEEN, so the control
proves the gate **can fire** and not merely that the reader can read. *Neither knows anything
about `Σ CAP`, the six ladder runs or the 20,000 ceiling.*

**(3) DISCLOSED, INSTRUMENT NAMED, WHAT MOVED QUANTIFIED — MET.** `T25R6a_C5_REGRADE_RECORD.md`
§4: `Σ CAP(C5)` never-computed → **20,006.80** core-min; `f_C5(L1)` = **10.651858**;
`f_C5(L3)` = **7.059383**; `P-1..P-3` never-evaluated → WINS/WINS/WINS.

**(4) PRE-REPAIR VALUES BESIDE THE PUBLISHED ONES — MET.** `T25R6a_VERDICT.json` stands unaltered
and is struck by the record, never rewritten.

#### §2ai.2 ⚠⚠ **THE NARROWING THE PETITION DID NOT RAISE, AND IT IS THE HARD PART OF THIS GRANT**

**This repair moves a landed verdict FROM `NOT A RESULT` TO a graded one.** `CLAUDE.md` rule 5's
ordering — *"the gate can only turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the
reverse"* — is written for the Roache triple and is not literally engaged here, since the
pre-repair `NOT A RESULT` came from a step-`[5]` control and not from a grid triple. **But its
reason is engaged, and a supervisor who answers only the letter has answered nothing.** `NOT A
RESULT` is the safe label; moving off it is moving toward a claim.

> **RULED — `§2ai.2`: A `§2d.1` REPAIR MAY CONVERT A LANDED `NOT A RESULT` INTO A GRADED VERDICT
> ONLY WHEN THE DIRECTION IS NOT THE PETITIONER'S. Two grounds, and either suffices: (i) the
> graded verdict it lands on is AGAINST the petitioner's interest, or (ii) the defect was
> established by an instrument that cannot know which direction is wanted (`§2d.1`(2), on its
> stated purpose rather than its examples).**
>
> **BOTH HOLD HERE.** The repair lands on **`GATE FAIL`**, and the defect is type arithmetic over
> two frozen contracts plus a `fired` list that gates nothing.
>
> **⚠ AND THE PRECEDENT IS EXPLICITLY NOT AVAILABLE THE OTHER WAY. Had the repaired predicate
> landed on a `PASS`, THIS GRANT WOULD NOT HAVE BEEN GIVEN**, and no reader may cite `§2ai` for
> resurrecting a `NOT A RESULT` into a `PASS`. *Heat-transfer put the direction row first, before
> any argument, and said "if verification wishes to test this petition's motive, that row is the
> test." It is the test, and it is the reason this clause can be written narrowly instead of
> refused.*

#### §2ai.3 **ITEM 1 — GRANTED. ITEM 2 — FIVE CONDITIONS, ASKED FOR EXPLICITLY AND GIVEN**

> **GRANTED: heat-transfer may apply to `grade_t25R6a.py` the `§7` predicate repair.**

| # | condition |
|---|---|
| **C1** | **The `§7` form ONLY. The `§6` form is REFUSED BY NAME.** Its `r["fired"]` is a direct key access behind an `isinstance` guard that covers the type and leaves the key unguarded; a `compare()` returning a dict without `fired` raises `KeyError`, and **a traceback is a DEGRADE where this lab's comparators REFUSE** (rule 4). *The petitioning supervisor found this in his own lane's diff and disclosed it rather than substituting quietly. The grant is pinned to the form he caught.* |
| **C2** | **`refuse()` on both new limbs, verified at source: `grade_t25R6a.py:134-136`, `sys.exit(EXIT_REFUSE)`, `EXIT_REFUSE = 2` at `:55`.** Both limbs distinguishable in the log by message. |
| **C3** | **⚠ THE LOAD-BEARING ONE, AND IT IS `§2p.8` APPLIED TO THIS GRANT: A RESTRICTIVE REPAIR IS NOT SELF-CERTIFYING.** The repair can only ADD refusals, and the petition itself discloses that **both new limbs are dead code on today's data — "it is not load-bearing; it is insurance."** So `§2p.3(e)`'s positive control is **not optional and not cheap talk**: drive the repaired grader **through the production path** over planted inputs — one constructed to DESERVE a pass on the equivalence limb (dict present, `fired == []`), and one each for the three refusal limbs (non-dict return; dict without `fired`; non-empty `fired`) — and show that it **still passes what it should pass**. **A repair whose new limbs cannot be shown to fire is indistinguishable, from its verdicts alone, from one that does nothing.** |
| **C4** | **`T25R6a_VERDICT.json` is not overwritten.** The regraded verdict lands beside it; the pre-repair file is struck by the record, never rewritten (rule 6). |
| **C5** | **⚠ ADDED AGAINST THE PETITIONER. The post-repair `GATE FAIL` carries its own resolution in its verdict cell.** `Σ CAP(C5) = 20,006.80` against a ceiling of 20,000 is a breach of **+6.80 core-min, ×1.00034**, while the registered interval **`[18,801.4 , 21,480.1]`** (`T25R6a_C5_REGRADE_RECORD.md:157`) **STRADDLES the ceiling** — the verdict is decided at a resolution the measurement does not have. **Under `§2ae` that disclosure belongs in the REGISTER ROW'S VERDICT CELL and at the head of the results record, not in an addendum a reader of the number never reaches.** *I do not re-grade and I do not widen: the gate is `Σ CAP ≤ 20,000` as registered, the ceiling question is already on Sanaa's desk, and this team unblocks a READING, not a NUMBER.* |

#### §2ai.4 **ITEM 3 — RECORDED, AND IT IS WORTH MORE THAN THE REPAIR: AN ARTIFACT THAT CARRIED ITS OWN REFUTATION AND WAS BELIEVED ANYWAY**

No repair was requested and none is ordered; the file stands unaltered under rule 6.

`T25R6a_VERDICT.json` asserts `"ground": "the equivalence control FIRED (prereg 6.4)"` while
carrying `'fired': []` at **both** levels **in the same file** `[VERIFIED BY ME AT SOURCE]`. The
measured channels sit **three to six orders inside every registered disqualifying threshold** on
both levels.

**Under `§2ac` this is the ASSERTS rank — the worst of the three** — because it does not merely
fail to check something; **it manufactures a positive claim of soundness that propagates into
every record quoting it.**

**AND IT HAS A PROPERTY NO PREVIOUS SPECIMEN OF THAT RANK HAD, which is why it is filed rather
than merely counted:** the refuting evidence was **serialised into the artifact by `:436` and
discarded by `:437` — the very next line.** The file carries its own falsifier, in its own body,
beside the claim it falsifies.

> **RECORDED — `§2ai.4`: A RECORD CAN CARRY ITS OWN REFUTATION AND STILL BE BELIEVED, BECAUSE
> CONSUMERS READ THE VERDICT FIELD AND NOT THE EVIDENCE FIELD BESIDE IT.** The discriminating
> test, which costs one question: ***does any consumer read the evidence field this record
> serialises, or only its verdict field?*** **Reported, not gated. No sweep is ordered and no
> class is declared** — one specimen. It is filed as a mechanism in `FAIL_OPEN_GATE_AUDIT`.
>
> **The GROUND is struck in the record** (`§2ae`: at the head of the results record and in the
> register row's verdict cell), **not in the file.** The rung's verdict is already `NOT A RESULT`,
> so no demotion is available and none is performed.

---

### §2aj — **ITEM E: A SELFTEST THAT NEVER REACHES ITS EMISSION PATH. ADOPTED, FORWARD-ONLY, AND IT IS NOT NEW LAW**

`grade_t25R6cR2.py --selftest` reports **`PASS (0 failed)` over 39 checks** — exercising every
gate, every control and five planted mutations, **including a blind reader failing the planted-zero
control and a smeared plant failing to read back at its step** — and **never calls `finish()`.**

**A comparator structurally unable to emit a verdict certified itself healthy over 39 checks.**

**THE BLOCKED RESULT, NAMED, because Sanaa's bar requires one and I will not adopt a requirement
without it:** T25R6cR2's registered artifact (`PREREGISTRATION.md:532`) was **unreachable through
its frozen path**, and **the instrument's own certification did not see it.** That is a registered
deliverable no run could produce, invisible to the only instrument that was supposed to notice.

**AND THIS IS NOT A NEW PRINCIPLE — IT IS THE THIRD QUESTION IN A SERIES THE LAB HAD ALREADY
STARTED**, which is the ground on which it costs nothing to adopt:

| | the question | where it was already law |
|---|---|---|
| 1 | **"Can this reader see a non-zero?"** | `CLAUDE.md` rule 3 — the planted-zero control |
| 2 | **"Did this reader run at all?"** | `FAIL_OPEN_GATE_AUDIT §28.4` — *plant the RUN, not only the VALUE* |
| 3 | **"Can this instrument SAY what it saw?"** | **nowhere. This clause.** |

> **RULED — `§2aj`: A COMPARATOR REGISTERED AFTER 2026-09-03 WHOSE SELFTEST DOES NOT DRIVE
> `grade()` END TO END THROUGH ITS EMISSION PATH — against a synthetic case root, asserting the
> verdict artifact EXISTS and PARSES — IS REGISTERED INCOMPLETE.** One added check per comparator,
> no compute, and it would have caught this before the rung ran.
>
> **NO BACKFILL. NO SWEEP. NO NEW INSTRUMENT.** Existing comparators are untouched and
> non-conformance in them is **not** a defect. **No instrument is built to measure this**, per
> Sanaa's reform — a registration-time expectation is checked by the supervisor registering it,
> which is a person and not a sweep.

**AND THE DOMAIN GAP HEAT-TRANSFER ASKS THIS TEAM TO CARRY IS ACCEPTED AS A FINDING, NOT AS A
CLAUSE**, in their own words: ***"the lab plants rigorously into comparators reading solver logs,
and into no git assertion, no shell glob, and no selftest's own coverage."*** With six guard
instances in one session behind it, **that is a domain gap in rule 3's application, not three
coincidences** — and I record it **REPORTED, NOT GATED**, because no result is blocked by the gap
as such. *It is filed as a mechanism family in `FAIL_OPEN_GATE_AUDIT`, where a measurement can
accumulate against it without any team owing migration work today.*

**Item D of that petition — the exit-code contract — is NOT ruled here.** It is a lab-wide
contract question and it is being ruled on its own measured census of every comparator's exit
codes, not on one grader's. **`PENDING`, in its display sense, and named so it is not mistaken for
silence.**

---

| item | outcome |
|---|---|
| **T25R6cR2 A — threshold** | **`§2d.1` DOES NOT REACH IT. No petition was needed** — rule 6 supplies the form, **`§2d:1842-1845` supplies a four-part disclosure that IS owed** |
| **the loophole guard** | **off-path status is MEASURED, never asserted — the `T25R6cR2` PROBE, named after the conduct that produced it** |
| **T25R6cR2 B — the bar** | **NOT MET. No result blocked; `L-470` already carries the local decision** |
| **T25R6cR2 C — the one-character repair** | **NO GRANT GIVEN, because granting an unneeded exception teaches that it was needed.** Local, under `§2ah`, one condition: the artifact must EXIST and PARSE |
| **the unreachable registered artifact** | **one sentence owed: rule 2's freeze verification was satisfied BY HAND, not by the registered path** |
| **⚠ the measurement against my own draft** | **the crash MOVED a registered channel: rc `3` → `1`. Off-gate-path holds; "off-path" gains a FIFTH disclosure content** |
| **the weaker vs stronger off-path claim** | *"nothing READS it"* is a consumer census that expires; *"nothing DOWNSTREAM COMPUTES it"* is structural. A record must say which it stands on |
| **T25R6a 1 — the predicate** | **GRANTED in the `§7` form.** Tautological, verified by me at source; `compare()` spans `:253-:294`, one return, a dict |
| **the check that could have refuted it** | **`:319` is inside `selftest()` (`:295`), not `compare()`** — had it been inside, `r != 0` could be false and the petition fails |
| **T25R6a 2 — conditions** | **FIVE. C1 form, C2 refusal, C3 `§2p.3(e)` positive control, C4 no overwrite, C5 the straddling interval in the verdict cell** |
| **the narrowing** | **`NOT A RESULT` → graded is permitted only when the direction is NOT the petitioner's. Had it landed on a `PASS`, REFUSED** |
| **T25R6a 3 — the artifact** | **RECORDED. `§2ac` ASSERTS rank, with a new property: it serialised its own falsifier at `:436` and discarded it at `:437`** |
| **T25R6cR2 E — the selftest** | **ADOPTED FORWARD-ONLY.** The third question; no backfill, no sweep, no instrument |
| **T25R6cR2 D — exit codes** | **`PENDING` — ruled separately on a measured census, not on one grader** |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| registration-time expectations | **1, forward-only (`§2aj`)** |
| solver compute | **0 core-min, $0.00** |

---

## Amendment — v1.54, 2026-09-03 — **§2ak THE COMPARATOR EXIT-CODE CONTRACT, RULED ON A CENSUS OF ALL 238 COMPARATORS RATHER THAN ON THE ONE GRADER THAT ASKED. THE PROPOSED FIX IS REFUSED TWICE — ONCE ON PRINCIPLE, BECAUSE A CRASH DRESSED AS A REFUSAL IS `§28`'s TELL DESIGNED IN BY CHARTER, AND ONCE ON MEASUREMENT, BECAUSE `EXIT_REFUSE` IS NOT ONE VALUE. AND THE LAB'S OWN RULE-3 PLANTED-CONTROL REFUSAL CURRENTLY RETURNS THE CRASH CODE.**

**Lines whose number changed above this section: 0.** Pure append; pre-append digest
`fb45084f0e13d4564835f9954f24a4cd` at 6496 lines. **Zero solver compute; 0 core-min; $0.00.**
**No gate, threshold, band, cap or label is created, moved or retired. Nothing is re-graded. No
sweep is ordered, no backfill is scheduled, and NO INSTRUMENT IS BUILT.**

**THE BAR, STATED BEFORE THE RULING AND NOT AFTER IT.** Sanaa's 2026-09-03 ~20:00Z reform
requires a blocked result to name. **NO RESULT IS BLOCKED — I measured for one and did not find
it, and I say so rather than manufacture one.** What is blocked is **one team's parked repair and
a question they formally put to this team**: `T25R6cR2_2D1_RECORD_EMISSION_PETITION.md` `§3.2`
declines to propose a fix because *"the right shape … is a comparator-contract question for
verification, not a lane's patch."* **Under her bar that earns an ANSWER, and the answer is
mostly a REFUSAL — which is the cheapest thing this charter can contain.** Two teams reached this
hole independently in one session; neither is waiting on a solve.

---

### §2ak.0 — **THE PROPOSED FIX IS REFUSED, AND ON TWO INDEPENDENT GROUNDS**

The petition's proposed shape: *"a top-level handler mapping any unexpected exception onto
`EXIT_REFUSE`, so that a comparator that cannot record REFUSES rather than returns an unregistered
code."*

**REFUSAL 1 — ON PRINCIPLE, AND IT IS THE WHOLE OF THIS CLAUSE.**

> **A REFUSAL IS A STATEMENT ABOUT THE RUN, MADE BY A WORKING INSTRUMENT. A CRASH IS A STATEMENT
> ABOUT THE INSTRUMENT, MADE BY NOBODY.**

| | a REFUSAL | a CRASH |
|---|---|---|
| what it is a statement about | **the RUN** | **the INSTRUMENT** |
| who made it | a working instrument, deliberately | nobody |
| what it says | *"I am not permitted to grade this"* | *"I could not answer"* |
| the verdict for the **run** | `NOT A RESULT` | `NOT A RESULT` |
| the verdict for the **instrument** | **none — it worked** | **a DEFECT FINDING** |
| can be made to go away by re-running | **no** — the condition must change | **yes** — and that is the hazard |

**The last row is why they may never share a value.** Mapping a crash onto `EXIT_REFUSE` makes
every instrument defect present as a well-behaved refusal, and **the lab permanently loses the
ability to count its own instrument failure rate.** *That is `FAIL_OPEN_GATE_AUDIT §28`'s tell —
the absence of an answer read as the presence of a considered one — except designed in, by
charter, rather than stumbled into.* **A refusal is a measurement. A crash is the absence of one.**

**REFUSAL 2 — ON MEASUREMENT, AND IT IS FATAL TO THE PROPOSAL AS WORDED.**

> **`EXIT_REFUSE` IS NOT ONE VALUE.** `[VERIFIED BY ME AT SOURCE]` **51 definitions say `2`; two
> say `3`** — `verification/runs/T-family/T25R4_MODULE_runs/ladder_gate_t25R4.py:25` and
> `verification/runs/T-family/T23G2_runs/preflight_gate_t23g2.py:49`. And `3` is `EXIT_GATE_FAIL`
> in three other graders. **A rule reading "return `EXIT_REFUSE`" would emit a `2` in 51 files, a
> `3` in two, and would silently mean GATE FAIL in the second pair.**
>
> **A CONTRACT IS WRITTEN ON A VALUE, NEVER ON A NAME.** The petitioner could not have known this;
> it is exactly what a census is for.

**Two further name collisions, measured, because the first is not an outlier:**
`EXIT_NOT_A_RESULT` is `4` in three files and **`1` in `scripts/recipe_audit.py:231`
`[VERIFIED BY ME AT SOURCE]`** — *in that instrument a `NOT A RESULT` and a crash are byte-identical
by design.* `EXIT_UNKNOWN` is `3` in six files and `4` in `scripts/append_record.py:378`.

---

### §2ak.1 — **THE MEASURED STATE, BECAUSE I WILL NOT LEGISLATE OVER A POPULATION I HAVE NOT COUNTED**

**Population: 238** — every `analyse_*.py`, `grade_*.py`, `mark_done_*.py`, `compare_*.py` under
`verification/runs/**`, `cases/**`, `scripts/**`. **Eleven distinct exit values in use:
`0,1,2,3,4,5,6,7,8,9,64`.**

- **`[MEASURED]` 236 OF 238 RETURN `1` ON AN INTERNAL CRASH.** Only two have a guard wired to the
  grading entry point: `analyse_t25R2.py:2729-2751` (wired `:2759`) and `mark_done_t25R2.py:551`
  (wired `:562`).
- **⚠ `[MEASURED]` 37 REFUSAL CALL SITES IN 8 COMPARATORS ALREADY EXIT `1`.** They pass a *string*
  to `sys.exit()` / `SystemExit`. `[VERIFIED BY ME ON THIS BOX]` `raise SystemExit("REFUSE: demo")`
  → **rc 1**; `raise ValueError("boom")` → **rc 1**. **Identical.** The files:
  `analyse_k0c.py` (9), `analyse_k2e.py` (6), `analyse_t25.py` (5),
  `K0b_D403_rerun` / `K0b_D406_repair` / `analyse_k0b_mesh.py` (5 each), `analyse_k2b.py` (1),
  `analyse_L3_plateau.py` (1).

> **⚠⚠ THE CONFLATION THIS CLAUSE FORBIDS ALREADY EXISTS 37 TIMES, MEASURED, BEFORE ANY RULE WAS
> WRITTEN. In those eight comparators a refusal and a crash are the same value TODAY.**

- **⚠⚠⚠ AND THE WORST SINGLE INSTANCE IS `CLAUDE.md` RULE 3's OWN CONTROL.**
  `[VERIFIED BY ME AT SOURCE]` `verification/runs/T-family/T25_MODULE_runs/analyse_t25.py:363-365`:

      if not ok:
          sys.exit("REFUSE: planted control failed; this reader's numbers are "
                   "not admissible")

  **That returns `1`.** So **the lab's planted-zero refusal is indistinguishable, by exit code,
  from the reader having died before the control ever ran.** *Rule 3 exists to make exactly that
  distinction — "a zero from a reader not shown able to see a non-zero is not evidence" — and its
  transmission channel cannot carry it.* **The reading is not wrong. The reader may never have
  run, and the value says the same thing either way** (`L-466`, one level down).

- **One composition hazard, recorded not ruled:** `mark_done_t25R6a.py:110-114` accumulates
  `rc |= mark(...)` across cases and exits the OR. **`2 | 4 = 6`**, which is a defined code with
  a different meaning elsewhere in the lab. *An exit code is not a set and does not compose.*

---

### §2ak.2 — **THE CONTRACT**

> **RULED — `§2ak`: A COMPARATOR'S INTERNAL ERROR HAS ITS OWN EXIT VALUE, AND IT IS NOT A REFUSAL.
> THE VALUE IS `70`.**
>
> **`EXIT_INSTRUMENT_ERROR = 70`** — `EX_SOFTWARE` from BSD `sysexits.h`, *"an internal software
> error has been detected"*. **Chosen from outside this lab and not invented here**, and it is the
> value the census actually permits:
> - it **collides with none** of the eleven values in use (`0-9`, `64`);
> - it **cannot be produced accidentally** — an unhandled Python exception returns `1`, and no
>   comparator in the population returns `70`;
> - it is **outside the shell's reserved band** (`126`, `127`, `128+N`);
> - it is **defined by a name outside this repository**, so it cannot drift the way `EXIT_REFUSE`
>   drifted to two values inside it.
>
> **The contract binds the VALUE. `EXIT_INSTRUMENT_ERROR` is its name here, and a file defining
> that name to another value is non-conforming BY DEFINITION, not by opinion.** Where a comparator
> encodes verdicts in its exit codes — several do, and their registrations name them — `70` is
> reserved out of that space and no verdict may occupy it.

**AND THE PART THAT MATTERS MORE THAN THE NUMBER — THE EMISSION DUTY.**

> **On internal error the comparator EMITS ITS RECORD ANYWAY**, from a top-level handler that runs
> **no grading logic**: verdict `NOT A RESULT`, plus an `instrument_error` block carrying the
> **exception type**, its **message**, the **file and line of the raise**, and the **comparator's
> own blob sha**. Then exit `70`.
>
> **THE FLOOR, STATED HONESTLY BECAUSE THE OBVIOUS OBJECTION IS CORRECT: THE HANDLER CAN ITSELF
> FAIL.** A crash in the writer is precisely the case where a writer cannot write. **Then the
> floor is the traceback on stderr and exit `70`, and nothing else is promised.** *A contract that
> pretends otherwise is the same species of false assurance it exists to prevent.*
>
> **THEREFORE THE CALLER'S DUTY, WHICH IS THE HALF THAT WOULD ACTUALLY HAVE CAUGHT THIS ONE:
> A MISSING VERDICT ARTIFACT IS NEVER READ AS "NO VERDICT WAS DUE." Absence of the artifact is
> itself `NOT A RESULT`.** That is `§28`'s caller side, and **it would have caught T25R6cR2 with
> no exit code at all.**

**THE TWO VERDICTS A CRASH PRODUCES, AND THEY ARE TWO:**

> - **THE RUN IS `NOT A RESULT`.** Not `BLOCKED` — nothing external prevented the work and the
>   data exists; the instrument failed to judge it. And never a silent absence.
> - **THE INSTRUMENT IS A DEFECT FINDING** — docketed, **never silent**.
>   **⚠ A CRASH THAT IS REPAIRED AND RE-RUN TO SUCCESS, WITH NO RECORD THAT IT HAPPENED, HAS
>   DESTROYED A MEASUREMENT OF THE INSTRUMENT'S OWN RELIABILITY.** *This is the whole reason the
>   two codes must differ: a crash can be made to go away by re-running, and a refusal cannot.*

**RE-GRADING AFTER THE REPAIR is governed by `§2d`/`§2ah`, not by this clause** — and a crash
repair takes **`§2ah.3`'s fifth disclosure content**, because **a crash MOVES THE EXIT CODE, which
is a registered channel.** *That is not a coincidence. The exit code is precisely the registered
channel a crash falsifies, which is why `§2ah.3` and this clause were forced by the same rung on
the same afternoon.*

---

### §2ak.3 — **THE REFERENCE IMPLEMENTATION IS ALREADY ON THIS LAB'S DISK, AND IT IS THE PETITIONER'S OWN**

`§2v.5`'s pattern again, and this instance is the sharpest yet.

`verification/runs/T-family/T25R2_MODULE_runs/analyse_t25R2.py:2729-2751` **already implements a
guarded grading entry point**, wired at `:2759` as `sys.exit(_guarded(sys.argv[1:]))`. Its own
docstring states this defect better than the petition did, **weeks earlier**:

> *"An instrument with no `except` clause lets an uncaught traceback leave the interpreter with
> exit status 1 — which in this file's exit vocabulary is 'a gate failed or a row is `NOT A
> RESULT`', i.e. a **GRADED outcome**. A crash would then be **INDISTINGUISHABLE FROM A
> MEASUREMENT**."*

> **RECORDED: HEAT-TRANSFER DIAGNOSED THIS DEFECT IN WRITING, IN ITS OWN FILE, BEFORE PETITIONING
> THIS TEAM FOR A RULE ABOUT IT — AND THE PETITION DOES NOT CITE IT.** No criticism attaches: it
> is a large team, a large repository, and the petition is one of the best-argued documents this
> charter has ruled on. **But the lab's best answer to a question was on its own disk while a team
> was asking for one, and that is a finding about the lab's memory, not about the team.** *It is
> the same shape as `§2v.5` and as `L-186`: what is not on a board is lost, and what is not
> indexed is not found.*
>
> **`analyse_t25R2.py:2729-2751` IS NAMED AS THE REFERENCE FORM so nobody invents a second one.**

---

### §2ak.4 — **SCOPE, HONESTLY, AND IT IS DELIBERATELY SMALL**

- **REPORTED, NOT GATED. NO RESULT IS BLOCKED** by the 37 conflated refusals or by the 236
  unguarded crash paths. `[MEASURED]` **No automated consumer reads a grader's exit code:**
  `scripts/queue_runner.py` invokes no grader and reads none; the four
  `[ $? -eq 2 ]` checks in `run_f17.sh`, `run_f17c.sh`, `run_f17b`'s and `run_f18.sh` are
  **pre-launch instrument checks that abort in the safe direction**; and `dafoam`'s
  `so3_chain_driver.sh:310` has **already ruled the exit status non-load-bearing in a live
  driver** (`note=comparator-exit-status-NOT-the-verdict`). **Every refusal to date was caught by
  a human reading stdout.**
  - *One honest caveat on that list: `run_f17c.sh:105` prints* "the `-O` refusal is not armed"
    *on any rc ≠ 2 — so it cannot distinguish an unarmed refusal from a crashed grader, and it
    prints the first diagnosis either way. It aborts, so nothing is graded wrongly; but its
    MESSAGE is false half the time.*
- **NO SWEEP. NO BACKFILL. NO NEW INSTRUMENT.** Per Sanaa's standing rule that **no instrument
  measures another instrument until the first changed a verdict**, **I do not build an exit-code
  conformance checker, and one may not be built on this clause's authority.**
- **FORWARD-ONLY.** A comparator **registered after 2026-09-03** conforms. **Existing comparators
  are non-conforming and that is NOT a defect** until one of them misleads a consumer — on which
  day it is a blocked result and the enforcement is earned.
- **ONE ITEM NAMED AND NOT ORDERED:** `analyse_t25.py:363-365`, rule 3's own control refusing at
  the crash code. **Its owner is heat-transfer and the decision is theirs.** *I name it because it
  is `CLAUDE.md` rule 3's binding artifact and a charter that knows this and stays silent is worse
  than one that never measured.*

| item | outcome |
|---|---|
| the proposed *"map internal raise onto `EXIT_REFUSE`"* | **REFUSED TWICE — on principle, and on the measurement that `EXIT_REFUSE` is 2 in 51 files and 3 in two** |
| refusal vs crash | **statement about the RUN vs statement about the INSTRUMENT. Never the same value** |
| why never the same | **a crash can be made to go away by re-running; a refusal cannot** |
| the value | **`EXIT_INSTRUMENT_ERROR = 70`**, `EX_SOFTWARE`, chosen from outside this lab, colliding with none of the 11 in use |
| the emission duty | **emit `NOT A RESULT` + an `instrument_error` block from a handler that grades nothing; floor is traceback + 70** |
| the caller's duty | **a MISSING artifact is `NOT A RESULT`, never "no verdict was due"** — and this alone would have caught T25R6cR2 |
| the two verdicts | **RUN → `NOT A RESULT`; INSTRUMENT → a docketed DEFECT FINDING, never silent** |
| **measured, 238 comparators** | **236 return 1 on a crash · 37 refusal sites in 8 files ALREADY return 1 · 11 distinct values in use** |
| ⚠ **rule 3's own control** | **`analyse_t25.py:363-365` refuses at rc 1 — the crash code. Named, not ordered; heat-transfer's** |
| the reference form | **`analyse_t25R2.py:2729-2751`, already on disk, by the petitioning team, weeks earlier, uncited** |
| blocked result | **NONE. Measured for, not found, and said rather than manufactured** |
| sweep · backfill · new instrument | **0 · 0 · 0 — and an exit-code conformance checker is FORBIDDEN on this clause's authority** |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |

---

## Amendment — v1.55, 2026-09-03 — **§2p.11 `§2ae` IS APPLIED TO MY OWN CHARTER FOR THE FIRST TIME, AND THE FIRST PASS REACHED THREE READING SITES OUT OF FOUR — DROPPING THE ONE SITE THE STRIKE ITSELF NAMED, WHILE ADDING TWO IT DID NOT. AN IN-PLACE CORRECTION DRIVEN FROM RECALL RATHER THAN FROM ITS OWN ENUMERATION BOTH OVER- AND UNDER-COVERS.**

**Lines whose number changed above this section: 0.** Pure append; pre-append digest
`a0090ce473fc8e417141f42b329cb0ce` at **6,719 lines**, the same 6,719 the file carried at
`HEAD` `5577cec9`, and every prior line keeps its number. **⚠ FOUR LINES ABOVE THIS SECTION
CHANGED CONTENT WITHOUT CHANGING NUMBER — `:4848`, `:4866`, `:4872`, `:4906` — and that is
what this amendment is about**, so it is stated here rather than left for a reader to
discover. Legal under `§2ae` (v1.51), which permits an in-place correction in a **record**
and forbids it absolutely on **frozen executable bytes**, where it would break the sha that
rule 2 fixes the grading path by. **This charter is a record. No comparator, no
registration, no frozen artifact was touched.** **Zero solver compute; 0 core-min; $0.00.**
**No gate, threshold, band, cap or label created, moved or retired; nothing re-graded.**

### §2p.11 THE `§2ae` REMEDY WAS APPLIED INCOMPLETELY, AND IT MISSED EXACTLY THE SITE `§2ae` EXISTS TO PROTECT

`§2ae` was ruled at v1.51 on ansys-verification's `§30`, whose finding I accepted in full:
***"a correction filed only at the foot does not reach the reader of the clause."*** The
remedy I ruled is that the correction must be reachable **from where the number is READ**,
not from where it was written.

**`§2p.9` (v1.50) is the test case, and it is mine.** Its strike reads, at `:5735-5736`:

> **STRUCK — `§2p.8`'s "`R3`, `R5` and `R6`" and its table row `:4906`. THE `§2p.3(e)` DEBT IS
> OWED BY `R3` AND `R5` AND BY NOTHING ELSE.**

**That strike NAMES TWO SITES.** A first in-place pass, in flight when this session's
predecessor was killed at ~20:00Z and recovered from the working tree, marked **three**:

| site | what it is | named by the strike? | marked by the first pass? |
|---|---|---|---|
| `:4872` | the prose sentence *"I granted `R3`, `R5` and `R6`"* | **YES** | **YES** |
| `:4906` | **the v1.42 outcome-table row** *"`R3`, `R5`, `R6` were granted"* | **YES** | ⚠ **NO** |
| `:4848` | the v1.42 amendment heading — *"THREE GRANTS I MADE TODAY"* | no | yes |
| `:4866` | the `§2p.8` section heading — *"THREE GRANTS I MADE TODAY"* | no | yes |

**THE PASS ADDED TWO SITES OUTSIDE ITS ENUMERATION AND DROPPED ONE INSIDE IT.** The two it
added are correct and belong — a heading asserting *"THREE GRANTS"* is a reading site by any
standard, and the strike under-enumerated. **The one it dropped is the worse half of the
trade, and not by a little: `:4906` is a SUMMARY TABLE ROW.** A reader who skims an
amendment reads its outcome table **instead of** its prose, not in addition to it. The first
pass therefore left the false claim standing at the site with the **highest** probability of
being read, inside a correction whose entire purpose was to reach the reader.

**⚠ AND HAD I COMMITTED THE WORKING TREE AS I FOUND IT, NOTHING IN THE ARTIFACT WOULD HAVE
SAID SO.** Three marked sites read as a completed correction. The fourth row carries no mark
and no reader could tell it was owed one. *That is `§28`'s tell — the absence of a mark read
as the absence of an error — arriving in the remedy for a different fault.*

> **RULED — `§2p.11`: AN IN-PLACE CORRECTION UNDER `§2ae` IS DRIVEN FROM AN ENUMERATION OF
> READING SITES, AND THE ENUMERATION IS DERIVED BY SEARCH AT CORRECTION TIME — NEVER FROM
> THE AUTHOR'S RECALL, AND NEVER FROM THE FOOT STRIKE ALONE. The foot strike is a
> STARTING POINT, not a work list: it is written by the same author, on the same day, from
> the same recall, and `§2p.9` proves it can under-enumerate. The correction is complete
> when a search for the corrected claim's own text returns no unmarked hit.**

**THE DISCRIMINATING TEST, and it costs one command.** After the pass, grep the file for the
**false claim's own distinguishing string** — here `R3.*R5.*R6` and *"three grants"* — and
read every hit. **An unmarked hit is an incomplete correction.** This is the test that found
`:4906`, and it is the test the first pass did not run. *It is the same discipline this team
has required of five other teams this week: do not certify an instrument by inference when
driving it is nearly free.*

**SCOPE, STATED AGAINST MY OWN INTEREST.** I do not know whether the first pass **missed**
`:4906` or had simply **not yet reached** it when the session died. **The distinction does
not survive contact with the artifact**, which is the point: a correction interrupted at
three-of-four and a correction completed wrongly at three-of-four are byte-identical, and
neither carries a mark saying which it is. **So the rule is written to hold under both** —
the completeness test is run at the end of the pass, by the author, and its result is stated
in the amendment. **It is stated in this one, and stated as a partition rather than as a
count, because a bare count is what let the first pass believe it was done.** The grep
`R3`…`R5`…`R6` ∪ *"THREE GRANTS"* returns **10 hits above this section**:

| class | lines | status |
|---|---|---|
| **assertion sites** — the text claims the grant | `:4848`, `:4866`, `:4872`, `:4906` | **4 of 4 MARKED** |
| **quotation inside `§2p.9`'s own correction** | `:5713`, `:5728`, `:5735`, `:5736`, `:5834` | **correct as written; a correction must quote what it corrects** |
| **a true statement naming all six petitions** | `:4456` — *"R1, R3, R4, R5 and R6 are HELD"* | **asserts no grant; nothing owed** |

**The partition is the deliverable, not the number.** *10 hits with 4 marked is
indistinguishable, from the count alone, from 10 hits with 4 missed.*

**NO NEW INSTRUMENT, AND I NAME THE ONE I DECLINED TO BUILD.** An in-place-correction
completeness checker over the charter corpus is buildable in an afternoon and would be
`§28`'s fifth face wearing a helpful face: a lab-wide enforcement instrument for a class
whose measured incidence is **one**. **Sanaa's governance budget forbids it and she is
right.** `§2p.5` says two instances is a **pattern**, not a class; **this is one.** The rule
above is a discipline for the author, not a gate, and **nothing in this amendment blocks or
unblocks any result.**

**WHAT IS NOT CLAIMED.** `§2p.9`'s substance was correct on the day it landed and is
unchanged here: **`R6` was REFUSED, never granted; the `§2p.3(e)` debt was owed by `R3` and
`R5` and is DISCHARGED for both** through the production path at `§2p.10`. **No verdict
moves. No grant is revisited.** This amendment corrects the REACH of a correction, not its
content — and it is the third consecutive session in which the error I have had to record in
this charter is my own.

| item | outcome |
|---|---|
| reading sites named by `§2p.9`'s strike | **2** — `:4872` and `:4906` |
| reading sites found by search at correction time | **4** — the two above, plus headings `:4848`, `:4866` |
| marked by the first, interrupted pass | **3 — and the ONE it dropped was the summary table row** |
| marked now | **4 of 4. The grep returns 10 hits, PARTITIONED: 4 assertion sites (marked), 5 quotations inside `§2p.9`'s correction, 1 true HELD statement** |
| why a partition and not a count | **10-with-4-marked and 10-with-4-missed are the same NUMBER** |
| why the dropped one is the worst | **a summary table is read INSTEAD OF the prose, not in addition to it** |
| the rule | **enumerate by SEARCH at correction time; the foot strike is a starting point, not a work list** |
| the test | **grep the false claim's own distinguishing string; an unmarked hit is an incomplete correction** |
| honesty on cause | **missed vs not-yet-reached is UNDECIDABLE from the artifact — the rule holds under both** |
| `§2ae` legality | **a RECORD, corrected in place. NO frozen bytes, NO comparator, NO sha broken** |
| lines renumbered · content-changed above | **0 · 4, all four named** |
| blocked result | **NONE — measured for, not found, and said rather than manufactured** |
| sweep · backfill · new instrument | **0 · 0 · 0 — a completeness checker is FORBIDDEN on this clause's authority** |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |

---

## Amendment — v1.56, 2026-09-03 — **§2al THE HARNESS-SOUND FLOOR'S PROVENANCE IS RESTORED, AND THE REFERRAL UNDERSTATED IT: THERE ARE THREE TRANSCRIPTION DROPS AND ONE INVENTION. THE INVENTED SENTENCE IS THE LOAD-BEARING ONE, IT IS CONTRADICTED BY THE SOURCE'S OWN SECOND DATA POINT, AND IT HAS PROPAGATED INTO FROZEN PRE-REGISTRATIONS AND A GRADER'S STATUS STRING. NO VERDICT MOVES, BECAUSE EVERY TEAM THAT CONSUMED IT REFUSED TO GATE ON IT.**

**Lines whose number changed above this section: 0.** Pure append. **⚠ THREE LINES ABOVE THIS
SECTION CHANGED CONTENT WITHOUT CHANGING NUMBER — `§7` step 4's three lines — and that is
what this amendment is about**, so it is stated here rather than left to be discovered.
Legal under `§2ae` (v1.51): **this charter is a RECORD.** **No frozen byte, no comparator, no
registration and no capture was touched; no sha that fixes a grading path is broken.** **Zero
solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or label created, moved
or retired. NOTHING RE-GRADED. The floor's interval — 2.5 to 5 % — is UNCHANGED.**

### §2al.1 THE REFERRAL IS GRANTED AND IT UNDERSTATED ITS OWN CASE

It reached me from a dafoam lane's bright-line investigation, asking for two restorations: the
mesh qualifier and the floor's stated base. **`[VERIFIED BY ME AT SOURCE, NOT RELAYED]`
`cases/dafoam/ladder-a/A_stepsize_study.md:89-90`, md5 `b6fcde0f55e9b357d43140f591db399b` —
the referral's prefix confirmed.** The source reads:

> *"For a case with **no flagged components**, **this dataset's** harness-sound floor is
> **2.5-5%** vector-norm relative error (2.5-3.0% here at 4032 cells; A2 independently
> achieved 1.71% at 38304 cells / 96 DVs — **consistent with the floor tightening on finer
> meshes**)."*

**`§7` step 4 carried, until this amendment:**

> *"The harness-sound floor **on this stack**, for a case with no flagged components, is 2.5
> to 5 percent vector-norm relative error. **A number below that is a claim about the
> harness.**"*

**FOUR DEFECTS, NOT TWO. Three are drops; the fourth is not a drop at all.**

| # | defect | class |
|---|---|---|
| 1 | *"**this dataset's**"* → *"**on this stack**"* | ⚠ **A WIDENING — one dataset became a whole stack. The referral did not name this and it is the broadest of the four** |
| 2 | the base **n=2** — 2.5-3.0 % at **4,032** cells; A2's **1.71 %** at **38,304** cells / 96 DVs | dropped |
| 3 | *"consistent with the floor **tightening on finer meshes**"* | dropped |
| 4 | **"A number below that is a claim about the harness."** | ⚠⚠ **NOT A TRANSCRIPTION AT ALL. IT APPEARS NOWHERE IN THE SOURCE** |

### §2al.2 ⚠⚠ THE INVENTED SENTENCE IS CONTRADICTED BY THE VERY STUDY IT CLAIMS TO SUMMARISE

**The source's SECOND DATA POINT — A2's 1.71 % — IS ITSELF BELOW THE FLOOR.** The source does
not treat it as a claim about the harness. **It treats it as CONFIRMATION**, and says so in
the same parenthesis: *"consistent with the floor tightening on finer meshes."*

> **So the charter took a study whose own finer-mesh result sat below the floor and was read
> as SUPPORTING the floor's shape, and turned "below the floor" into a standing accusation
> against the harness.** ***The clause inverted the polarity of its source's second data
> point.***

**This is `§2ac`'s worst class and it is mine.** A gate never implemented is **SILENT**; one
implemented-and-unreached is **INERT**; one **implemented, fired and FALSE ⚠ ASSERTS** — and
it is **the only one that PROPAGATES**, because downstream records quote the assurance rather
than re-derive it. **MEASURED PROPAGATION, all `[VERIFIED BY ME AT SOURCE]`:**

- **FROZEN pre-registrations quote it VERBATIM** — `curriculum_SO3/PREREGISTRATION.md:79` and
  `curriculum_D19O/PREREGISTRATION.md:188`.
- **It is compiled into a grader's STATUS STRING** — `so3_grade.py:290`: *"BELOW_HARNESS_FLOOR
  -- a number below 2.5 % on this stack is a claim about the harness (VERIFICATION section 7
  step 4)"*.
- **It is quoted in at least five RESULTS records** — SO3, D19M, D19O, D4, D10.

### §2al.3 ⚡ AND NOTHING IS RE-GRADED, BECAUSE EVERY TEAM THAT CONSUMED IT REFUSED TO GATE ON IT

**`[VERIFIED BY ME AT SOURCE]` `so3_grade.py:281-299`, `floor_margin()` — its docstring reads
`REPORTED, NEVER GATED` and it returns a margin and a label. IT RETURNS NO VERDICT.** The
records agree on their own faces: D19M — *"The floor is REPORTED, NEVER GATED, as
registered"*; SO3's artefact carries `gated: false`; and **`D19O/PREREGISTRATION.md:188` states
the principle better than the clause did**:

> *"Turning it into a gate would convert an honest caveat into a `GATE FAIL` the charter does
> not authorise."*

**THE FIELD PRACTICE WAS RIGHT WHERE THE CLAUSE WAS WRONG, AND THAT IS WHY NO VERDICT MOVES.**
*It is `§2ag`'s shape again: the comparator and the registrations were more honest than the
charter they were obeying, and the defect was in the instrument of governance rather than in
the work it governed.* **Every sub-floor row named in the referral's census — D19M, D19O, D8,
SO-3aR2 — carried the caveat on the artefact's face and gated nothing** *(that census is
dafoam's and is recorded as **REPORTED**; I re-derived D19M, D19O and SO3 and did not open D8
or SO-3aR2)*.

### §2al.4 THE CLAUSE'S OWN STANDARD, APPLIED TO THE CLAUSE

The referral notes that this clause **retired its predecessor for resting on a single rung**,
and itself rests on **n=2**. **That is one more rung, not a different kind of evidence.**
`§2p.5` — this team's own rule, invoked twice today to refuse my own sweeps — says **two
instances is a PATTERN, not a class.**

> **RULED — `§2al`: A FLOOR ESTABLISHED ON n=2 IS A PATTERN AND IS STATED AS ONE. It keeps
> its interval and it carries its base and its trend qualifier ON ITS FACE, so that a reader
> can see what it rests on without opening the study.** **A number below a floor whose own
> establishing study says the floor TIGHTENS ON FINER MESHES is, on a finer mesh, WHAT THAT
> STUDY PREDICTS** — reported beside the aggregate, exactly as the field has been doing, and
> **never an anomaly, never a `GATE FAIL`, and never a standing accusation against the
> harness.**

**WHAT IS NOT RULED, AND I NAME IT RATHER THAN LET SILENCE READ AS COVERAGE:** whether the
floor's *interval* is right at all on a fine mesh is **UNMEASURED** and is not touched here.
`n=2` cannot answer it. **Restoring provenance is not validating the number** — this amendment
makes the clause say what its source says, and its source's base is two rungs.

### §2al.5 THE FROZEN QUOTATIONS ARE DELIBERATELY NOT ANNOTATED

`curriculum_SO3/PREREGISTRATION.md:79` and `curriculum_D19O/PREREGISTRATION.md:188` quote the
struck sentence **verbatim inside FROZEN pre-registrations**, and `so3_grade.py:290` carries
it in a **frozen comparator's** status string. **`§2ae` is absolute here: NEVER ANNOTATE
FROZEN BYTES** — for a comparator it breaks the sha that rule 2 fixes the grading path by, and
for a pre-registration it destroys the freeze that is its entire evidentiary content.

**THE CORRECTION REACHES THEM ANYWAY, AND BY THE ONE ROUTE THAT IS LEGAL: THEY CITE `§7` STEP
4 BY NAME, AND `§7` STEP 4 IS NOW CORRECTED AT THE POINT OF READING.** *A citation is a live
link, not a copy: correcting the cited clause is how a frozen quotation is reached without
touching a frozen byte.* **Any successor registration quoting this clause quotes the corrected
form. No existing registration is reopened and no rung is re-graded.**

| item | outcome |
|---|---|
| referral | **GRANTED, and enlarged — it asked for 2 restorations; there are 3 drops and 1 invention** |
| the invention | **"A number below that is a claim about the harness" — NOWHERE IN THE SOURCE, and CONTRADICTED by the source's own second data point** |
| the widening the referral missed | **"this dataset's" → "on this stack"** |
| source | `A_stepsize_study.md:89-90`, md5 **`b6fcde0f55e9b357d43140f591db399b`**, verified by me |
| the floor's base | **n=2 — 2.5-3.0 % at 4,032 cells; 1.71 % at 38,304 cells / 96 DVs. A PATTERN, per `§2p.5`** |
| the interval | **2.5-5 % — UNCHANGED. Not revisited, not validated** |
| propagation | **2 FROZEN pre-registrations, 1 grader status string, ≥5 results records** |
| ⚡ verdicts moved | **ZERO — `floor_margin()` is `REPORTED, NEVER GATED` and returns no verdict** |
| who was right | **THE FIELD. `D19O:188` refused to gate on it before any ruling reached them** |
| frozen bytes touched · shas broken | **0 · 0** — reached by citation, which is the only legal route |
| lines renumbered · content-changed above | **0 · 3, all three named** |
| sweep · backfill · new instrument | **0 · 0 · 0** — forward-only, as the referral itself proposed |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |

---

## Amendment — v1.57, 2026-09-03 — **§2am ansys `§31`'s REINSTATEMENT CONDITION IS **RESOLVABLE**, AND THE DOCUMENT THAT CARRIES IT ALREADY NAMED ITS READER TWENTY LINES ABOVE. THE SUSPENSION IS LIFTED. ⚠ THE RULING LANDS IN THE PETITIONING TEAM'S FAVOUR AND I SAY SO AT THE TOP, THEN SHOW EVERY GROUND IS OUTCOME-INDEPENDENT.**

**Zero solver compute; 0 core-min; $0.00.** **Lines whose number changed above this section: 0.** Pure append; **no line of any charter, register, comparator or capture is edited — this rules on ansys's clause and touches none of their bytes.** **No gate, threshold, band, cap or label created, moved or retired. Row #54's demotion is UNTOUCHED and stands.**

### §2am.1 THE QUESTION, AND WHY IT CAME TO ME

`ANSYS_VERIFICATION_CHARTER §31` freezes a reinstatement condition — **finest-level shock final-window drift ≤ 6.25e-04 m** over the last **W = 500** iterations, *"measured on the shock location itself and not on any upstream station"* — and **names no reader.** Two readers exist on disk and they straddle it:

| reader | on the real L3 final window | against the condition |
|---|---|---|
| `grade_vmfl046.py:251-254` — largest adjacent-pair Mach drop, **snapped to a sample node** | **exactly 0.0000e+00 m** | **SATISFIES** |
| `diagnostic_shock_steadiness.py:82-95` — last downward `M=1` crossing, **linearly interpolated** | **2.3265e-03 m** | **FAILS by 3.72×** |

**ansys ESCALATED RATHER THAN SELF-APPLIED AND DISCLOSED THAT THEIR INCENTIVE RUNS TOWARD *"UNRESOLVABLE"***, in their own words: *"choosing one now, knowing which answer each gives, is precisely the gate-fitting this charter has refused four times."* **That disclosure is why this gets a ruling instead of a deferral, and it is the `§2ag.5` model: they named the conflict before anyone raised it and refused authority they could have taken silently.**

### §2am.2 ⚠ THE OUTCOME FAVOURS THEM, STATED BEFORE THE REASONING SO IT CANNOT LOOK LIKE A CONCLUSION I BACKED INTO

**Under the SNAPPING reader**: drift 0.0 → admissible → the second limb fires on existing data → settled `x_shock` **1.152576** vs analytical **1.250** = **7.79 % deviation > 5 %** → **the `GATE FAIL` IS REINSTATED against ansys.**
**Under the INTERPOLATING reader**: drift 2.3265e-03 > 6.25e-04 → **not admissible** → no reinstatement; row #54 stays `NOT A RESULT`.

> **I RULE FOR THE INTERPOLATING READER. THAT IS THE OUTCOME FAVOURABLE TO THE TEAM THAT REFERRED THE QUESTION, AND IT IS THE SAME OUTCOME THEIR DECLARED "UNRESOLVABLE" WOULD HAVE PRODUCED.** *I therefore tested every ground below against the question "would this argument still convince me if it pointed the other way," and I state the one place where the answer is uncomfortable (`§2am.5`).*

### §2am.3 GROUND ONE, AND IT IS SUFFICIENT ON ITS OWN: THE DOCUMENT DEFINES THE TERM TWENTY LINES ABOVE, BY NAME

The condition lives in the dated demotion note at the foot of `ANSYS_VALIDATION_REGISTER.md` (`:881`). **That same note, at `:855`, twenty-six lines earlier, reads: *"Measured against the same run root by `verification/runs/ansys_verification/diagnostic_shock_steadiness.py`"*, and introduces the table at `:857-861` whose column header is *"final-window drift"* — THE IDENTICAL PHRASE THE CONDITION USES — with the L3 cell reading 2.3265e-03 m = 3.722 %.**

**The condition is then written in that table's own normalisation**: *"≤ 1 % of the 0.0625 m band"*, against a table quoting **3.722 % of band**.

> **A term of art defined by name earlier in a document is defined for the sentence below it, unless that sentence redefines it. `§31` does not redefine it.** *"Final-window shock drift" has exactly one prior definition in the document that carries the condition, and that definition is attributed, by filename, to the interpolating script.*

**THIS GROUND IS PURELY TEXTUAL AND WOULD READ IDENTICALLY IF THE NUMBERS WERE REVERSED.**

### §2am.4 GROUND TWO: THE FROZEN COMPARATOR COMPUTES NO DRIFT AT ALL, SO IT WAS NEVER AN AVAILABLE READING

`grade_vmfl046.py` calls `shock_location` at **exactly one** site (`:161`), on the **single final** centreline sample. **There is no `final_window`, no `drift`, and no differencing of `xshock` across iterations anywhere in the file.** Its only convergence limb is the `M(0.900)` plateau — *the very limb whose false zero (`4.332e-10`) grounded the demotion.*

> **A condition cannot mean a reader that has never computed the condition's quantity.** *"Use the frozen comparator" is not a selection between two existing readings; it is a request for code that does not exist. The two options were never symmetric: one is written and unfrozen, the other is frozen and unwritten.*

**And the siting constraint points the same way**: *"measured on the shock location itself and **not on any upstream station**"* is a **correction of the frozen comparator's own plateau limb.** A condition drafted to exclude an instrument's convergence limb is poor evidence that it meant that instrument.

### §2am.5 GROUND THREE, THE DECISIVE ONE: UNDER THE SNAPPING READER THE NUMBER `6.25e-04` DOES NO WORK, SO THE FREEZE WOULD HAVE RECORDED NOTHING

**`[VERIFIED, DERIVED FROM CODE AND MESH, NOT ASSERTED]`** the centreline sampler is `nPoints 400` over `x ∈ [0.002, 1.998]` at **every** level, so **Δ = 5.0025062657e-03 m**, and **Δ / 6.25e-04 = 8.004**. The snapping reader returns a node coordinate, so the **complete set** of drifts it can produce is

**{ 0 } ∪ { k · 5.0025e-03 : k = 1, 2, 3, … }**

> ⚡ **THERE IS NO OUTPUT IN THE INTERVAL `(0, 6.25e-04]`. The reader is a BINARY INDICATOR: the condition is satisfied iff the node index did not change, and the MAGNITUDE OF THE DRIFT PLAYS NO PART.** **Every threshold in `(0, 5.0025e-03)` produces byte-identical verdicts.**

**Therefore, under the snapping reader, the specific value `6.25e-04` carries NO INFORMATION.** Rule 2's entire evidentiary content is that a frozen number **could not have been chosen to fit the answer** — but a number that could be replaced by any other number in a 4,000-fold range **without changing a single verdict was not chosen for its value at all.**

> **RULED — `§2am`: A FROZEN THRESHOLD IS READ AS MEANING THE READER UNDER WHICH ITS SPECIFIC VALUE IS OPERATIVE. Where one candidate reader makes the number load-bearing and another makes it arbitrary, the freeze names the first — because on the second reading the freeze recorded no information, and rule 2 does not permit a frozen number to be construed as having recorded nothing.**

**AND THIS GROUND IS THE MOST OUTCOME-INDEPENDENT OF THE THREE:** it is arithmetic over a mesh spacing and a threshold, and it would select the interpolating reader **whatever** either reader happened to return.

### §2am.6 A FOURTH GROUND, WHICH IS THE DOCUMENT REFUTING THE ALTERNATIVE OUT OF ITS OWN MOUTH

**Burden 2's PRESERVED flagship finding — *"the shock moves AWAY from the reference under refinement, L1 → L2 = +1.7288 % → −4.0612 %"* — is justified at `:873` by *"both levels are settled (final-window drift 0.0000e+00 and 2.06e-04 m)"*. Those are INTERPOLATING-reader values.**

> **Under the snapping reader ALL THREE levels read exactly 0.0000e+00 at the final window. It could not have made the settled/unsettled distinction the demotion's surviving finding rests on.** *The note's own reasoning is unavailable under the reader it is now suggested the note meant.*

### §2am.7 ⚠⚠ THE FREEZE ORDERING, WHICH LOOKS BAD AND WHICH I RULE DOES NOT DEFEAT THE CONDITION

| when (UTC) | what |
|---|---|
| 2026-09-02 23:51–23:52 | **the L3 samples both readings consume are written** |
| 2026-09-03 18:15:25 | **the audit artifact printing the interpolated drift, 3.722 % of band** |
| 2026-09-03 **18:28:58** | **`c53a1a67` — the condition frozen at 1 % of band** |

**The condition was frozen 18 h 36 min after the data existed and 13 min 33 s after the artifact printing that data's answer.** The register's own claim — *"frozen here … before any such run exists"* — is **true as stated** (no re-run root exists) **and is a narrower claim than "before the data that could answer it".** *That distinction is real and the lane was right to name it.*

**I RULE IT DOES NOT DEFEAT THE CONDITION, ON THE DIRECTION ANALYSIS `§2d.7` REQUIRES.** `6.25e-04` is **1 % of the 0.0625 m band** — a principled round fraction, not a value reverse-engineered from 3.722 %. **And its direction is ADVERSE-then-protective in a way no fitter would choose:** a *stricter* admissibility bar blocks **both** limbs — it prevents the `GATE FAIL` returning **and** prevents the case ever becoming a live `PASS` candidate. **A team fitting a gate to its own advantage sets the admissibility bar LOOSE and then argues the second limb; setting it at 1 % forecloses their own best outcome as thoroughly as their worst.**

> ⚠ **BUT THE HAZARD IS REAL AND IS NAMED RATHER THAN DISMISSED: a threshold frozen after its data existed carries less evidentiary weight than one frozen before, and `§31`'s wording invites a reader to think otherwise.** *Recorded as a finding against the clause's framing, not as a defect in the number.*

### §2am.8 WHAT THIS RULING IS NOT: INTERPRETING A CONDITION IS NOT ALTERING IT

ansys escalated because *"naming the reader alters a frozen condition, which `ESCALATION_CHARTER` reserves."* **They were right to escalate and they are wrong that this alters it.**

> **RULED: naming the reader THE DOCUMENT ITSELF ALREADY USED, for a term THE DOCUMENT ITSELF ALREADY DEFINED, is INTERPRETATION and is available to a cross-team auditor. SELECTING A READER THE DOCUMENT NEVER USED WOULD BE ALTERATION and would go to Sanaa.** *The whole of `§2am.3`–`§2am.6` is derived from inside the document carrying the condition. I have imported nothing.*

### §2am.9 DISPOSITION

| item | outcome |
|---|---|
| **the reader `§31`'s condition means** | **the INTERPOLATING reader — `diagnostic_shock_steadiness.py:82-95`, by the document's own definition at `:855`** |
| **`§35.1`'s suspension** | **LIFTED. Reinstatement may be claimed under `§31`, under the named reader** |
| **the condition applied to existing L3 data** | drift **2.3265e-03 m > 6.25e-04 m** → **ADMISSIBILITY NOT MET. NO REINSTATEMENT TODAY** |
| **row #54** | **`NOT A RESULT`, UNTOUCHED. Its demotion rests on the `M(0.900)` false zero and on a 192.60 %-of-band excursion BOTH readers resolve** |
| ⚡ **the case is NOT CLOSED** | **it is PENDING A RUN.** The condition is live and reachable: a re-run driven to a measured plateau can meet it |
| **who was right** | **ansys, on both the finding and the refusal to self-apply.** Their `§35.1` general rule is **ENDORSED for their territory** |
| **lab-wide generalisation of `§35.1`** | **DECLINED — `§28.6.6`'s reasoning: nothing is blocked once this ruling lands, and a met precondition permits a clause, it does not compel one** |
| frozen bytes touched · shas broken | **0 · 0** |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** — the condition is UNCHANGED; only its reader is named |
| solver compute | **0 core-min, $0.00** |

### §2am.10 ⚠ THE ANTI-SHELTER CLAUSE, BECAUSE MY OWN RULING CREATES THE RISK

**This ruling leaves row #54 unresolved and unresolvable-today, which is the outcome that suits the team it concerns.** *I decline to leave that comfortable.*

> **RULED: A CASE THAT CANNOT BE RESOLVED TODAY IS NOT A CASE THAT IS CLOSED. `NOT A RESULT` is a statement that the question is OPEN, never that it is settled, and it may not be cited as an absence of failure (`FAIL_OPEN_GATE_AUDIT §28.4`).** **The obligation to re-run VMFL046 under a registration whose finest level reaches a measured plateau SURVIVES this ruling and is owed by ansys-verification.** *A demotion that relieves a team of a recorded failure carries `§2ad`'s disclosure burden; a ruling that leaves the failure unreachable carries the mirror of it, and this clause is that mirror.*

**AND THE ONE THING THAT WOULD REOPEN THIS RULING, STATED IN ADVANCE SO IT CANNOT BE FITTED LATER: if a drift-computing reader is ever brought INSIDE a frozen grading path for this family, `§2am.3`'s textual ground yields to it** — rule 2 prefers an instrument inside the grading path to one outside it, and today there is no such instrument to prefer.

---

## Amendment — v1.58, 2026-09-04 — **§2an A MODEL-FORM `GATE FAIL` IS A ROUTING SIGNAL, NOT A TERMINUS: IT ESCALATES INTO SANAA'S FOUR-RUNG CLOSURE LADDER, EACH RUNG GATED AGAINST THE SAME REFERENCE. ⚠ AND THE LADDER COLLIDES WITH HER OWN `(ABSOLUTE)` ANTI-GAMING CLAUSE UNLESS THREE CONDITIONS HOLD — THEY ARE NAMED HERE AND MADE BINDING. THE EXHAUSTED-LADDER RESULT IS A CERTIFIED PRODUCT, AND ITS CERTIFICATION RESTS ON THE CLOSURES *NOT* TRIED**

**Appended 2026-09-04 by `verification-supervisor`. Lines whose number changed above this section: 0.**
**No gate, threshold, band, cap or label is moved by this amendment. Nothing is re-graded. Rule 1's
vocabulary is unchanged; rule 5's ordering is unchanged; §2's freeze law is unchanged; the
no-gate-widening boundary is unchanged.** This amendment answers, and supersedes, the question this
team placed on Sanaa's desk on 2026-09-04 (*"does a measured, defect-exhausted, model-form `GATE
FAIL` discharge the mandatory-completion order"*). **Her ruling supersedes the question's framing
rather than answering it as posed, and that is recorded as the disposition.**

### §2an.1 SANAA'S TEXT, VERBATIM — THE AUTHORITY

Captured at `etc/sessions/2026-09-04T1510Z_sanaa_model_form_closure_ladder.md`, commit `0910b664`;
her own header, *"Corrected ruling, paste-ready."* **Quoted, not styled; where the operationalisation
below appears to add a requirement her text does not state, HER TEXT GOVERNS.**

> [SANAA-DIRECT] Model-form GATE FAIL is a routing signal, not a terminus.
> When stock closures fail a gate, the case escalates into the closure ladder,
> in order, each rung gated against the same reference: (1) exhaust all stock
> RANS closures, register if none land; (2) rule out numerical cause per §0;
> (3) apply literature closure corrections — analytical terms,
> functional/nonlinear and algebraic-stress models, curvature/rotation and
> separation-specific corrections — each carried in the lab docs with its
> paper provenance and known-good flow class, applied and gated individually;
> (4) the lab's own research closures (GP-based) as the top rung. A
> model-form failure ships as a documented failure ONLY when the closure
> ladder is genuinely exhausted — and even then it ships with the full ladder
> recorded (which closures and corrections were tried, each deviation),
> because "all known closures fail this flow at these numbers" is itself a
> rare and valuable certified result. Process-class failures still halt as
> before; this ladder is for model-form only.

*(Her standing task in the same directive — build the provenance-tagged closure-correction library —
is a capability assignment carried by the closure line, not verdict law, and is not restated here.)*

### §2an.2 WHAT CHANGES IN VERDICT LAW, AND WHAT DOES NOT `[lab-attributed]`

**CHANGES:** a `GATE FAIL` whose cause is established as **model-form** no longer terminates a case,
and no longer travels to Sanaa's desk case by case. **It routes into the four-rung ladder**, each
rung executed through the ordinary registered path.

**DOES NOT CHANGE — and each is restated because a routing law is exactly where they would be
quietly lost:**

- **The failing rung keeps its verdict.** `GATE FAIL` on rung 1 is a **`GATE FAIL` on the record,
  permanently.** A later rung that passes **does not withdraw, overwrite or supersede it** — this is
  `NONCONVERGENCE_STANDARD` §2.1's L6 rule and §4.4, and it applies unchanged. **The disposition of
  an escalated case is the SEQUENCE of rung verdicts, never a single word.**
- **Rule 5's ordering is untouched and still runs FIRST.** A rung whose triple is not `CONVERGING`
  is `NOT A RESULT` whatever its value, and the gate can only turn a `PASS` or `GATE FAIL` **into**
  `NOT A RESULT`, never the reverse. **A ladder rung is a rung of the Roache ladder before it is a
  rung of the closure ladder.**
- **Rule 2's freeze law is untouched.** **Each rung is its own registered, frozen, costed act.** The
  ladder creates **no fast path**: rung *N*'s gate, threshold, cap and label are committed before
  rung *N*'s solver starts.
- **The no-gate-widening boundary is untouched and is the whole point.** See §2an.3.
- **Process-class failures halt and triage as before.** Her sentence is explicit; §2an.5 makes the
  discriminator operational.

### §2an.3 ⚡ THE KEYSTONE: THE LADDER MOVES THE **MODEL** AGAINST A FIXED GATE AND A FIXED REFERENCE

Her binding phrase is ***"each rung gated against the same reference."*** It is not decoration and it
is the clause that makes the whole ladder lawful.

> **RULED — `§2an.3`: ON AN ESCALATED CASE, THE REFERENCE AND THE GATE ARE INVARIANTS OF THE ENTIRE
> LADDER. Only the CLOSURE moves.** Every rung is graded against **the same reference value, the same
> band, the same acceptance criterion** as the rung that failed. **A rung graded against a different
> reference, a re-derived band, a re-normalised criterion, or a second reference "more appropriate to
> this closure" IS NOT A RUNG OF THIS LADDER** — it is a new case, and it inherits none of the
> ladder's standing.

***This is the exact mirror of the act the anti-gaming clause forbids.*** Gate-widening holds the
model fixed and moves the gate until the answer fits. **The closure ladder holds the gate AND the
reference fixed and moves the model.** *They are opposites, and that is precisely why one is lawful
and the other never is.* **A team that finds itself adjusting the reference to make a rung land has
left the ladder and re-entered the manoeuvre the ladder exists to replace.**

### §2an.4 ⚠⚠ THE COLLISION WITH HER OWN `(ABSOLUTE)` ANTI-GAMING CLAUSE — NAMED, AND RESOLVED BY THREE BINDING CONDITIONS

Her 2026-08-27 anti-gaming clause, still in force, `(absolute)`:

> *"Answer-changing choices (model, scheme class, formulation) are never selected by agreement with
> the reference."*

**The closure ladder SELECTS A MODEL AND STOPS WHEN A MODEL AGREES WITH THE REFERENCE. Read naively,
that is the forbidden act performed as policy, and this amendment will not pretend otherwise.**

**RESOLVED — and the resolution is in the anti-gaming clause's own stated tell.** What that clause
prohibits is **UNDISCLOSED** selection: *"trying several and keeping the one nearest the reference"*,
where ***"the tell is that the discarded arms are not in the record"*** and *"a single reported arm
out of several run is the signature this clause exists to catch."* **Her closure ladder mandates the
opposite — *"it ships with the full ladder recorded (which closures and corrections were tried, each
deviation)."*** ***The ladder does not evade the anti-gaming clause; it performs the clause's own
cure, as policy, and makes the disclosure the deliverable.***

**⚠ BUT THAT HOLDS ONLY UNDER THREE CONDITIONS, AND WITHOUT ALL THREE THE LADDER DEGENERATES INTO
MODEL-SHOPPING WITH A LADDER'S VOCABULARY BOLTED ON. THEY ARE BINDING:**

1. **THE ORDER IS FIXED AND IS HERS.** Rungs are climbed **in her stated order** — stock exhaustion,
   numerical rule-out, literature corrections, lab research closures. **A rung is not reached until
   the rung below it is exhausted and registered.** *Choosing which rung to try is choosing by
   expected agreement; her order removes the choice.*
2. **EACH RUNG IS REGISTERED AND GATED BEFORE IT RUNS.** Rule 2, without exception. ***The gate a
   rung will be judged by is frozen before that rung's result exists*** — which is what makes
   "this rung passed" a finding rather than a selection.
3. **EVERY RUNG ATTEMPTED IS IN THE RECORD, WITH ITS DEVIATION, INCLUDING THE ONES THAT WENT THE
   WRONG WAY.** No rung is dropped for being uninformative, embarrassing, or superseded.

**A ladder satisfying all three is a measurement. A ladder missing any one of them is a parameter
hunt over models, and this charter grades it `NOT A RESULT` under §2c for the same reason a
multi-dial arm is: it cannot discriminate.**

### §2an.5 THE DISCRIMINATOR — MODEL-FORM IS A **RESIDUAL**, ESTABLISHED BY ELIMINATION, NEVER BY INSPECTION `[lab-attributed]`

Her ladder is *"for model-form only"*, so the classification decides whether a case may enter it.
**The lab's incentive now runs toward an early model-form finding — it opens the interesting work —
so the discipline must run the other way.**

> **RULED — `§2an.5`: `MODEL-FORM` IS THE LAST CLASSIFICATION A CASE IS PERMITTED TO REACH, NOT THE
> FIRST. It is never asserted from the look of a result. It is what REMAINS after every
> process class below has been cleared AT SOURCE.**

**PROCESS-CLASS — checked first, in this order; any hit stops the case here and it does NOT enter
the ladder:**

1. **Completion.** The run fails the strict completion rule (rule 4) — `rc ≠ 0`, no `End` line, last
   time ≠ `endTime`, missing fields, `ExecutionTime` mismatch, or an age-guard failure. **The answer
   was never produced.**
2. **Convergence and grid.** Any level not iteratively converged or not plateaued; the triple
   `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` (rule 5). → `NOT A RESULT`.
3. **Crash, divergence or refused solve**, not yet triaged (`SUPERVISION` §3 check 2) — **a finding
   about the case, the method or the toolchain until triage says otherwise.**
4. **Instrument.** The comparator, reader or grading path is shown wrong; a planted-zero control
   refuses (rule 3); an exit code is a crash wearing a refusal's clothes (`§2ak`).
5. **Referent.** The reference value, its band or its provenance is itself in question (`§2al`,
   `§2am`). ***A disagreement with a reference that is wrong is not a model-form failure.***

**MODEL-FORM — reached only when ALL FIVE are cleared and ALL of the following hold, each verified
at source and not relayed:** the run satisfies rule 4 in every limb; its triple is `CONVERGING` with
its GCI quoted at `Fs = 1.25`; the comparator's planted control fired; the reference and its band are
sound; **and the measured deviation exceeds the pre-registered band.** ***In one line: the numerics
are demonstrably right and the answer is demonstrably wrong.***

**⚡ AND HER RUNG 2 IS THE DISCRIMINATOR'S OWN AUDIT, PLACED INSIDE THE LADDER.** *"Rule out numerical
cause"* sits at rung 2 **after** stock exhaustion — which means **the initial model-form
classification is PROVISIONAL until rung 2 confirms it.** **A case that finds a numerical cause at
rung 2 EXITS the ladder entirely and returns to process class**, and its rung-1 record stands as what
it was. *That exit is the ladder's safety valve and it is not optional.*

### §2an.6 ⚡⚡ THE LADDER RECORD'S REGISTERED FORM — AND THE **NOT-TRIED** SET IS THE HALF THAT CERTIFIES IT

Her product claim is precise: *"all known closures fail this flow at these numbers"* is *"itself a
rare and valuable certified result."* **This team's contribution is to say what that claim requires,
before the first F6-era case improvises it.**

> **⚠ RULED — `§2an.6`: "ALL KNOWN CLOSURES FAIL" IS A CLAIM ABOUT THE CLOSURES **NOT TRIED** AT
> LEAST AS MUCH AS THOSE TRIED. IT CANNOT BE CERTIFIED FROM A RECORD THAT LISTS ONLY WHAT WAS RUN.**
> ***A ladder record enumerating only its attempts is consistent with a faithful exhaustion AND with
> a lucky early stop — it therefore discriminates neither*** (`FAIL_OPEN_GATE_AUDIT` §28.11, the
> likelihood-ratio-1 form). **The record must make the difference visible.**

**A ladder record is admissible for an exhaustion claim only if it carries, as a registered
artifact beside the case:**

- **THE ADMISSIBLE SET, ENUMERATED UP FRONT** — every stock closure and every catalogued literature
  correction whose declared flow class covers this case, listed **before** climbing;
- **PER MEMBER, `TRIED` OR `NOT TRIED`**, and for every `NOT TRIED` a **reason from a closed set** —
  not implemented in this solver / outside its declared flow class / superseded by a listed member /
  not yet ingested into the library. ***"Not tried" with no reason voids the exhaustion claim,
  though it does not void the rung verdicts already earned;***
- **PER ATTEMPT:** rung number; the closure or correction named; **its paper provenance** (her
  requirement — author, year, and the `docs/papers/` path) and **the flow class the source claims
  for it**, with a statement of whether THIS case is inside that class; **the sha of that rung's own
  frozen pre-registration**; **the reference and gate asserted IDENTICAL to rung 1's, BY VALUE**
  (§2an.3, asserted not claimed); the measured deviation with its uncertainty channels; the rule-1
  verdict; and the cost in core-minutes;
- **THE ORDER ACTUALLY CLIMBED**, so that §2an.4's condition 1 is checkable rather than asserted.

**Until a rung's admissible set is enumerated, the case may still climb and still earn rung verdicts
— it simply may not claim EXHAUSTION.** *The verdicts and the exhaustion claim are separable, and
this amendment separates them deliberately so that record-keeping never blocks physics
(Sanaa's bookkeeping rule).*

### §2an.7 ⚠ THE `§0` REFERENT IS FLAGGED, NOT GUESSED

Her rung 2 reads *"rule out numerical cause per §0."* **`[MEASURED]` No document in this repository
defines a `§0` governing numerical rule-out**; the only `§0` on record is her own 2026-08-27 desk-rulings
section, which concerns other matters. **Applying `§2am`'s discipline to her text as I applied it to
ansys's: I identify the reader a document already uses, or I flag it — I do not select one.**

**RULED: the CROSS-REFERENCE is unresolved; the OBLIGATION is not ambiguous and nothing is blocked.**
Rung 2's substance — *rule out numerical cause* — is fully executable today through instruments
already binding: **rule 4's completion rule, rule 5's Roache triple and GCI, and the
`NONCONVERGENCE_STANDARD`'s L0–L4.** A rung-2 record discharging those discharges rung 2. **If Sanaa
names a different `§0`, that reading governs and this paragraph yields to it.**

### §2an.8 WHAT THIS AMENDMENT DOES NOT DO

- **It creates no verdict word.** Rule 1's vocabulary is unchanged; an escalated case's rungs each
  take a verdict from it.
- **It grants no compute and lifts no cap.** Every rung is costed and capped under rule 12.
- **It re-grades nothing and reopens no frozen document.**
- **It does not lift closure's stand-down.** Sanaa's directive reframes that line as the ladder's top
  rung and library owner; **whether and when it resumes is hers, and this charter does not decide it.**
- **It does not itself build the closure-correction library**, which is a capability assignment to
  another team, not verdict law.

---

## Amendment — v1.59, 2026-09-04 — **§2ao THE T3d `DONE.R_fx` PETITION IS **REFUSED AS UNNECESSARY** AND THE BLOCKED RESULT IS **UNBLOCKED ANYWAY**, BY A ROUTE STRICTLY BETTER THAN THE ONE PETITIONED FOR — WHICH THE PETITIONER FOUND AND DISCLOSED AGAINST ITS OWN INTEREST. AND THE DISTINCTION THAT DECIDES IT GENERALISES: AN **ATTESTATION** OF INDEPENDENTLY-CHECKABLE FACTS IS NOT A **COMPARATOR**.**

**Appended 2026-09-04 by `verification-supervisor`. Lines whose number changed above this section: 0.**
**No gate, threshold, band, cap or label is moved. Nothing is re-graded. No verdict is pre-judged.**
Petition: `docs/campaigns/T-family/T3d_DONE_MARKER_2D1_PETITION.md`, from heat-transfer.

### §2ao.1 THE RULING, LED WITH, BECAUSE A BLOCKED MANDATORY COMPLETION SHOULD NOT HAVE TO READ TO THE END

> **1. THE ASK IS REFUSED.** No new completion-marker producer is added to T3d's grading path after
> first compute. **§2d stands, because no exception is needed** — §2d.1 is not reached at all.
> **2. THE RESULT IS UNBLOCKED, TODAY.** `python3 mark_done_t3.py --root <T3_runs> R_fx` — a file
> **frozen 2026-08-21, before `R_fx` existed** — **applies** rule 4's six clauses to `R_fx` and
> writes `DONE.R_fx` if and only if they hold. **No new file. No registered sha changes. The
> comparator is byte-untouched.**
> **3. IT IS HEAT-TRANSFER'S HAND, NOT MINE.** The marker lands in their run tree; this team
> authorises and does not execute.

### §2ao.2 VERIFIED BY ME AT SOURCE, NOT RELAYED — THE PETITIONER'S OWN §8.2 IS CORRECT

**I read `mark_done_t3.py` end to end rather than accept the claim, because the whole ruling rests
on it.**

- **`:105` — `ap.add_argument("cases", nargs="*", default=CASES)`.** ***`CASES` is a DEFAULT, not a
  domain.*** `check(root, c)` is called with whatever name is given and **validates it against
  nothing.**
- **`check()` is GENERIC BY CONSTRUCTION.** Every criterion resolves from **the case's own
  artifacts**: `root/<case>` for the directory, `STATUS.<case>`, `<case>/log.solve`, `endTime` from
  **the case's own `system/controlDict`**, RAS-or-not from **the case's own
  `constant/turbulenceProperties`**, and the age datum from **the case's own `0/T`**. **There is no
  hardcoded case name in the checking logic at all.**
- **It refuses safely in every degenerate direction** — no case directory, no `STATUS`, no
  `log.solve`, no time directory beyond 0, missing fields, or no `0/T` (*"so the run's start cannot
  be dated"*) each produce a failure, not a pass. **`main()` returns 1 if any case is not done, and
  the script never retracts an existing marker.**

**⚡ AND IT IS STRICTER THAN THE CONSTITUTION, WHICH IS THE FACT THAT DISPOSES OF THE SAFETY
QUESTION.** `:34` — `NEEDED = ("T", "U", "p_rgh", "alphat", "phi")`, plus `("nut","k","omega")` when
RAS. **`CLAUDE.md` rule 4's thermal list is `T U p_rgh alphat nut k omega` — the same set MINUS
`phi`.** ***The frozen instrument therefore requires strictly more than rule 4 does, so it cannot
pass a case that rule 4's field limb would fail.*** *(The `phi` divergence between the constitution
and its enforcing instrument is a real recorded discrepancy; nothing turns on it here because it
runs in the safe direction, and any `CLAUDE.md` line is Sanaa's alone.)*

### §2ao.3 WHY §2d.1 IS NOT REACHED — AND THE DISTINCTION THAT GENERALISES

§2d governs **a change on the grading path made after the first graded solve.** **Running an
already-frozen instrument through its own registered interface is not a change to anything.** No
file is added, no registered sha256 moves, `analyse_t3d.py` is byte-identical to its registration.
**A rule that forbids *using* a frozen instrument would forbid grading itself.**

The petition's §3.2 establishes the real shape of the defect, and I adopt it: **T3d's registration
NAMES the `DONE.R_fx` artifact, REGISTERS the comparator's refusal without it, and REGISTERS NO
PRODUCER FOR IT.** ***A frozen registration that requires an artifact and registers no way to make
it has not registered a gate; it has registered a deadlock.*** Rule 2 exists so a gate cannot be
fitted to an answer — **it was never meant to make a completed run permanently ungradable because
the registration omitted to say who writes the marker.**

> **⚡ RULED — `§2ao.3`, AND IT REACHES BEYOND THIS CASE: AN **ATTESTATION** IS NOT A
> **COMPARATOR**, AND THE FREEZE DISCIPLINE BINDS THEM DIFFERENTLY.**
> **A comparator's freeze is load-bearing because its output is a NUMBER NOBODY ELSE CAN
> RE-DERIVE** — its identity is the evidence. **A completion marker attests facts that ANY reader
> can re-derive from disk**: an `rc`, an `End` line, a last time directory, a field list, a line
> count, a set of mtimes. ***Its correctness is auditable independently of who produced it, so the
> producer's identity is not evidentially load-bearing.*** **What IS load-bearing, with full force,
> is that the clauses be APPLIED and not ASSERTED.**

**This is why the petition's own §8.1 was right to refuse hand-writing the marker**, and why
heat-transfer's disclosure — *"a check that would have passed is still not a check performed"*,
offered against their own interest on `reconstructpar_rc=0` — **is the correct principle and earns
them nothing here.** It does not need to: **the route granted PERFORMS the checks.**

### §2ao.4 THE STOPPING POINT, STATED BECAUSE §7.3 ASKED FOR ONE I COULD LIVE WITH OR ELSE A REFUSAL

**A frozen, pre-first-compute instrument may be applied to a case outside its default list when ALL
THREE hold, and this is the whole of the permission:**

1. **IT TAKES THE CASE THROUGH ITS OWN REGISTERED INTERFACE** — a documented parameter, not an edit,
   not a wrapper, not a copy. *If reaching the case requires changing a byte, this clause fails and
   §2d applies in full.*
2. **EVERY CRITERION DERIVES FROM THE CASE'S OWN ARTIFACTS** — not from constants tied to the cases
   it was written for. *An instrument carrying another case's `endTime`, field list or geometry is
   measuring that case, not this one.*
3. **ITS CRITERIA ARE AT LEAST AS STRICT AS THE GOVERNING RULE FOR THE NEW CASE**, measured and
   stated, not assumed.

**All three are measured as holding here. Failing any one, §2d stands and a petition is required.**
**This permission reaches ATTESTATIONS only. It does NOT reach comparators, graders, scorers or any
instrument that produces a value a gate is compared against** — for those the registered identity
IS the evidence and nothing in this amendment touches them.

### §2ao.5 WHAT THIS RULING DOES **NOT** DO, INCLUDING WHERE IT LEAVES THE PETITIONER WORSE OFF

- **IT DOES NOT PRE-JUDGE THE VERDICT.** The marker unblocks **grading**, not a `PASS`. `R_fx` may
  grade `PASS`, `GATE FAIL` or `NOT A RESULT`, and the registration's own §3 predicts against a
  `PASS`. **Under `§2an` and `NONCONVERGENCE_STANDARD` §4 a `GATE FAIL` here is an honest waypoint,
  not a failure of the mandatory-completion order.** *If the marker script REFUSES, that refusal is
  the finding and the run is not done — that outcome is equally admissible and must not be worked
  around.*
- **IT DOES NOT EXCUSE THE REGISTRATION DEFECT. §7.2 IS CONCEDED BY THE PETITIONER IN FULL AND I
  LEAVE THE CONCESSION STANDING**: the same team registered a marker producer for `R_ff` eight days
  earlier under a `PRE-FIRST-COMPUTE` heading and did not do so for `R_fx`. **That belongs on
  heat-transfer's record whatever the ruling**, and the correct repair for the NEXT rung is to
  register the producer in the pre-registration, before compute, as they already know how to do.
- **IT REQUIRES THE RUN TO BE RECORDED.** The invocation, its full output — which cases met the
  clauses and which failed and why — and the resulting marker are filed beside the case. ***An
  attestation whose application left no record is back to being an assertion.***
- **IT SETTLES NOTHING ABOUT `mark_done_t3_rff.py`**, whose `CASE = "R_ff"` module constant admits
  no override (petition §3.4, verified) — **that script cannot reach `R_fx` and this ruling does not
  make it able to.**

---

## Amendment — v1.60, 2026-09-04 — **§2ap THE PAIRED-PIN REHEARSAL: A REGISTRATION THAT PINS BOTH A PRODUCER AND A CONSUMER OF AN ARTIFACT FREEZES ONLY AFTER THE PRODUCER'S REAL OUTPUT HAS BEEN DRIVEN THROUGH THE CONSUMER — ONE SUCCESS LEG AND ONE CORRUPTION LEG, RECORDED IN THE REGISTRATION. THIS TEAM REFUSED FIVE INSTRUMENTS TODAY AND GRANTS THIS ONE; THE DIFFERENCE IS STATED SO THE GRANT CANNOT BE CITED FOR THE NEXT ONE.**

**Appended 2026-09-04 by `verification-supervisor`. Lines whose number changed above this section: 0.**
**FORWARD-ONLY. NO BACKFILL. No frozen registration is reopened, no verdict moves, nothing is
re-graded, and no existing rung acquires a defect it did not have this morning.**

### §2ap.1 THE MEASUREMENT THAT EARNED IT — VERIFIED BY ME AT SOURCE

**T3d.** `build_t3d.py:89` writes `CASE.txt` as **six lines of prose containing no key-value pairs of
any kind**. `analyse_t3.py:461-468` reads **seven numeric keys** from that same file — `H`, `nu`,
`Pr`, `Prt`, `dTdn_wall`, `T_in`, `U_in`, ~~`endTime`~~ — and refuses on the first it cannot find. **[⚠ STRUCK IN PLACE 2026-09-04, v1.61 `§2ap.6`: `endTime` IS SATISFIABLE and does not belong in the failing list — the prose line begins `endTime 24000 = ADDITIONAL iterations`, so `line.startswith("endTime ")` matches and `.split()[0]` parses as `24000.0`. VERIFIED BY ME against the real `R_fx/CASE.txt`. The COUNT of seven was right and the LIST was wrong by one; `H` is the key that refuses first. Nothing else in `§2ap` changes.]**
**Both are sha-pinned in the SAME frozen registration (`T3d_PREREGISTRATION.md` §6) and both are
byte-identical to their pins.** ***Nothing drifted. The pinned builder and the pinned grader could
never have satisfied each other, and that was true at the moment of freezing.***

**COST: 4,723.200 core-minutes, MEASURED**, on a run **no outcome of which could have been graded**.
The rung closed `NOT A RESULT`. **The three sibling levels carry the structured block because a
DIFFERENT builder wrote them; only the level T3d itself adds was built by the pinned builder** —
which is why the defect could not be inferred from the family's other cases.

**⚡ AND THE DEFECT WAS MASKED BEHIND ANOTHER ONE.** The missing `DONE.R_fx` producer (`§2ao`)
refused *first*. **The incompatibility was not discoverable until that blocker was cleared — which
took a charter ruling.** ***A registration can carry two independent fatal defects, and the outer one
hides the inner one until it is resolved. Clearing a blocker is not evidence that a case is
gradeable.***

**THE CLASS HAS NOW COST THE LAB THREE ITEMS — T19, T3d, T5b, each a DIFFERENT mutual
incompatibility between separately-pinned components — and ~4,752 core-minutes.**

### §2ap.2 THE CLAUSE

> **RULED — `§2ap`: WHERE A REGISTRATION PINS BOTH A PRODUCER AND A CONSUMER OF THE SAME ARTIFACT,
> THE FREEZE IS NOT VALID UNTIL AN END-TO-END REHEARSAL HAS BEEN RUN AND RECORDED IN THE
> REGISTRATION ITSELF. The rehearsal has TWO legs and both are required:**
>
> **(a) THE SUCCESS LEG — the PINNED producer's REAL OUTPUT, driven through the PINNED consumer,
> accepted.** *Real output, not a hand-made fixture: a fixture is a third artifact nobody pinned,
> and agreeing with it proves only that the fixture's author guessed the format.*
>
> **(b) THE CORRUPTION LEG — the artifact perturbed, and the consumer REFUSES.** *Mandatory, and it
> is `§28.8`'s cure: a success leg alone is satisfiable by a consumer that accepts everything, and
> such a consumer passes on the day the defect ships.* **The leg that can fail is the leg that
> carries the evidence.**
>
> **Both legs and their outputs are recorded IN the registration, BEFORE the freeze.**

**SCOPE, DELIBERATELY NARROW: it bites only where BOTH components are pinned in the SAME
registration.** Where only one is pinned, or the consumer reads an artifact no pinned producer
writes, **`§2ap` does not apply** and rule 2 stands unchanged.

**WHAT IT DOES NOT REQUIRE: a solve.** The rehearsal needs the producer's real output on a minimal or
scratch case — **seconds of compute, and that is the entire point: the defect that cost 4,723
core-minutes was determinable before a single iteration ran.**

### §2ap.3 WHY THIS ONE IS GRANTED WHEN FIVE WERE REFUSED TODAY — THE DIFFERENCE, STATED SO THE GRANT CANNOT BE CITED FOR THE NEXT PROPOSAL

**This team refused five instruments today** (`§28.9`, `§28.10`, `§28.11`, `§28.12`, `§28.13`,
`§28.14`), **two of them against its own findings.** The grounds for refusal were: a population of
one; a defect already fixed at source; a detector that would fire on lawful work; and a hazard whose
measurable class was empty. **None of those applies here, and each is answered:**

| refusal ground | why it does not apply |
|---|---|
| **population of one** | **THREE instances, three rungs, each a DIFFERENT incompatibility** — `§2p.5`'s pattern bar is passed on distinct mechanisms, not repetitions |
| **already fixed at source** | **not fixed anywhere; it recurs by construction** whenever two components are pinned without being introduced to each other |
| **would fire on lawful work** | **it cannot.** ***Performing the rehearsal IS the lawful work.*** The check is binary and auditable: the record exists or it does not. **No false-alarm stream, so `§28.10`'s pathology is not created** |
| **empty measurable class** | **4,752 core-minutes, MEASURED**, and a rung closed `NOT A RESULT` |

**AND THE TWO GROUNDS THAT ARE AFFIRMATIVE RATHER THAN MERELY NOT-DISQUALIFYING:**

1. **IT WOULD HAVE CHANGED A VERDICT'S FATE, WHICH IS THE BAR THIS TEAM SET FOR MINTING A CHECK
   RATHER THAN RECORDING A NOTE.** T3d did not lose a record; **it lost the possibility of any
   verdict at all**, after the compute was spent.
2. **⚡ TWO TEAMS INDEPENDENTLY IMPOSED THE CURE ON THEMSELVES BEFORE ANY CLAUSE EXISTED** —
   heat-transfer on `T3e` (freeze follows a rehearsal, plus a corruption clause proving the checks
   live) and dafoam via `A1WRT2 §1` (the no-verdict state forbidden by construction). ***A cure two
   teams reach separately, unprompted, is one the lab already believed in and had not written
   down*** — the same signal `§28.8` recorded. **This clause makes uniform what the lab converged
   on; it does not impose a practice nobody wanted.**

**`§28.6.6` still governs and is satisfied deliberately, not bypassed: a met precondition PERMITS a
gate, it does not COMPEL one. I am deciding affirmatively, and the reason is the row above.**

### §2ap.4 KEPT APART FROM ITS NEIGHBOURS, AS EVERY MECHANISM THIS WEEK HAS BEEN

- **`§28.14.2` (the unrehearsed success path)** asks whether **ONE instrument can EMIT a verdict at
  all** — the output side of a single component.
- **`§2ap`** asks whether **TWO pinned components can TALK** — the interface between them.
  ***An instrument can emit verdicts perfectly and still be unable to read what its own registered
  producer writes; that is exactly T3d.*** **Different failure, different cure, two entries.**
- **`§2p.3(e)`** demands a positive control for a **restrictive repair**; `§2ap` demands a rehearsal
  for a **freeze**. **Neither subsumes the other.**

### §2ap.5 WHAT THIS CLAUSE DOES NOT CATCH, STATED SO IT IS NOT OVER-TRUSTED

- **A rehearsal exercises ONE output.** A producer whose output varies with the case may emit
  something the consumer rejects on a later run. ***`§2ap` proves the pair CAN agree; it does not
  prove they ALWAYS will.*** A team that treats a passed rehearsal as a guarantee has over-read it.
- **It does not reach unpinned components**, by design (`§2ap.2`).
- **It is not enforced by any instrument today, and none is built by this amendment.** It is
  auditable by reading the registration, which is where a reviewer already looks. **If it is found
  being skipped, that is the evidence for building an enforcer — and not before.**
- **NO BACKFILL.** Registrations frozen before today are governed by rule 2 as it stood. **A sweep of
  not-yet-run frozen registrations for this class is COMPUTE-PROTECTIVE and is separately
  commissioned; it grades nothing and reopens nothing.**

---

## Amendment — v1.61, 2026-09-04 — **§2ap.6 THE `§2ap` SWEEP RETURNS **NO NEW MISMATCH** ON THE POPULATION IT CAN SEE — AND THE POPULATION IT CAN SEE IS **29 OF 393**. THE SWEEP ALSO CORRECTED `§2ap.1`'s OWN KEY LIST, AND FOUND THE CLASS IS WIDER THAN KEYS. `§2ap` IS NOT WIDENED TONIGHT AND THE REASON IS STATED.**

**Appended 2026-09-04 by `verification-supervisor`. Lines whose number changed above this section: 0**
— `§2ap.1`'s correction is a STRIKE IN PLACE on its existing line, adding no line. **No gate,
threshold, band, cap or label moves. Nothing re-graded. `§2ap` itself is UNCHANGED in scope,
requirement and effect.**

### §2ap.6.1 THE CORRECTION TO MY OWN CLAUSE, FOUND BY THE LANE I SENT TO ENFORCE IT

**`§2ap.1` listed EIGHT keys under the label "seven".** `endTime` does not belong in the failing
list: `build_t3d.py`'s prose line begins `endTime 24000 = ADDITIONAL iterations`, so
`line.startswith("endTime ")` matches and `.split()[0]` parses as `24000.0`.

**`[VERIFIED BY ME AT SOURCE against the real `R_fx/CASE.txt`, not against the lane's report]`:
`endTime` → FOUND, parses `24000.0`. `H` → ABSENT, refuses.** **The COUNT of seven was right; the
LIST was wrong by one, and `H` is the key that refuses first.** *Struck in place at `§2ap.1`.*
***This sharpens the finding rather than weakening it: seven of eight required keys are unobtainable
from the pinned producer's output.***

### §2ap.6.2 THE SWEEP — AND ITS COVERAGE IS THE HEADLINE, NOT ITS ZERO

**Strict population 29 registrations pinning both a producer and a consumer.
RESULT: ONE MISMATCH, AND IT IS THE KNOWN POSITIVE (T3d). NO NEW MISMATCH.**

| class | n | result |
|---|---|---|
| `CASE.txt` keyed contract | 9 | **1 MISMATCH (T3d) · 8 COMPATIBLE** |
| `birth_certificate.json` key contract | 3 | COMPATIBLE |
| existence / bare-`rc` contract | 4 | COMPATIBLE |
| no shared on-disk artifact between the pinned pair | 13 | out of class |

**⚠ AND THE COVERAGE IS 29 OF 393.** Of 393 registrations, **95 mention both a producer- and a
consumer-shaped script and only 29–31 PIN both adjacently to a sha. 37 sha-bearing documents that
mention both were NOT CLASSIFIED — that is the largest remaining exposure and it is named, not
buried.** ***A zero on 7 % of the population is not a zero on the population, and this team will not
report it as one.***

**THE EIGHT COMPATIBLEs CARRY EVIDENCE, NOT ABSENCE OF IT — three distinct on-disk dialects coexist
and each pair matches its own**: `key=value` written and regex-read (T14, T17, T18, T9aR1b);
`key<spaces>value` written and whitespace-split (T15); and two graded empirically (T13, T16).
***T3d is prose written against a whitespace-split reader — a DIALECT mismatch, not a typo.*** The
cross-dialect case was hunted specifically: **zero found outside T3d.**

**THE DETECTOR NEEDED THREE GENERATIONS TO SEE THE KNOWN POSITIVE, AND THAT IS RECORDED BECAUSE THE
FAILURES CHARACTERISE THE BLINDNESS:** gen 1 was blind (the pinned consumer delegates via `import
analyse_t3 as A`); gen 2 **false-positived on the negative control** (keys from a library import
never called on that family); gen 3, call-graph reachability from the pinned entry points, passes
both legs. ***A detector that had not been driven against a known positive would have reported the
same zero and meant nothing by it.***

### §2ap.6.3 ⚡ THE CLASS IS WIDER THAN KEYS, AND `§2ap`'s NARROW SCOPE HAS A COST I STATE RATHER THAN HIDE

- **THE PATCH-NAME DIMENSION, self-documented in this repository and never counted:**
  `build_t5b.py:198-206` records that *"`cube_side_s` does NOT exist on the half domain; T5's
  comparator named it and fired NOT A RESULT by construction."* **A pinned comparator naming a patch
  the pinned builder never creates is the same class in a dimension no key-detector covers.**
- **THE UNPINNED-PRODUCER GAP, and it is a cost of MY OWN wording:** `analyse_m6sr.py:1205` requires
  `SOLVER_RC`, written by `run_m6sr_b5.sh`, **which `M6SR_PREREGISTRATION.md` does not pin.**
  **`§2ap` deliberately reaches only pairs where BOTH are pinned, so it does not bite here** —
  correct by the clause as written, **and a real hole.** *A narrow scope is not a free scope, and
  pretending otherwise is how a clause gets over-trusted.*

**`§2ap` IS NOT WIDENED TONIGHT.** Widening it to unpinned producers or to patch names on **zero new
measured instances** is exactly the move this team refused five times today. **`§28.6.6`: a met
precondition permits a gate, it does not compel one — and here the precondition is not met.**
**Recorded so the next instance is RECOGNISED rather than rediscovered.**

### §2ap.6.4 THE OPERATIONALLY URGENT FINDING, WHICH IS NOT A MISMATCH AT ALL

**EIGHT registrations are RAN-BUT-UNGRADED: `K0e`, `K0eR2`, `K0eR3`, `T10aVF`, `T19`, `F21`, `F22`,
`F24`.** ***The compute is already spent and the grader has never been driven — which is precisely
T3d's failure shape, eight times over.*** **A paired-pin defect in any of them surfaces only at
grading, after the core-minutes are gone.** **`T19` is already a named member of this class.**
**`T10aVF` could NOT be classified statically** (`CASE.json`, unresolvable key subscripts) —
**CANNOT DETERMINE, and said so rather than counted as clean.**

**RELAYED TO THE OWNING TEAMS, NOT ORDERED BY ME: drive the grader on what is already on disk.** It
costs no solver time and it is the only way to learn whether the money already spent bought a
gradeable artifact. **This is a recommendation about their own rungs, not a verdict on them.**

**AND ONE PRACTICE ALREADY ANTICIPATED `§2ap` BEFORE IT EXISTED, WHICH IS WORTH MORE THAN THE
CLAUSE: `run_f23b.sh:490` asserts `[ -f "$CD/MESH_LINE.txt" ]` immediately after the build and aborts
at ZERO SOLVER COST if it is absent** — an in-launcher producer→consumer rehearsal, written by cfd
with no clause requiring it. **F23b is UNRUN with a 313.0 core-min rung cap and its pinned pair is
COMPATIBLE, verified at source. That is the third team to reach this rule unprompted.**

---

## Amendment — v1.62, 2026-09-04 — **§2aq THE FD STEP RANGE AT `:864` IS A **RECOMMENDATION FOR A1's FFD CONTROL POINTS**, NOT A LAB-WIDE GATE — `§2al`'s DEFECT CLASS 1 FROM THE **SAME SOURCE** AT THE **ADJACENT STEP**. AND THE DROPPED MECHANISMS INVERTED A FAMILY'S RISK ORDERING: A STEP THE SOURCE CALLS SAFE WAS EXCLUDED AS "BELOW SANCTIONED" WHILE THE SOURCE'S OWN FAILURE BOUNDARY WAS ADOPTED.**

**Appended 2026-09-04 by `verification-supervisor`. Lines whose number changed above this section: 0**
— `:864`'s correction is a STRIKE IN PLACE adding no line. **NOTHING IS RE-GRADED. NO VERDICT MOVES.
NO REGISTRATION'S OWN GATE IS DISTURBED.** Referred by dafoam, whose framing is preserved: *"referred,
not charged — we ask for a reading, assert no defect, move no verdict."* **The referral is correct in
full, and it understated itself; see `§2aq.3`.**

### §2aq.1 THE TRANSCRIPTION, BOTH SIDES READ BY ME AT SOURCE

**`[VERIFIED BY ME, NOT RELAYED]`** — `cases/dafoam/ladder-a/A_stepsize_study.md`, under the heading
***"## Recommended FD step size"***:

> **1e-3 to 1e-2**, central, `step_calc=abs`. Below ~1e-4 the CD difference falls below the primal's
> residual noise floor (`primalMinResTol=1e-8`) and FD degrades severely (11.5 % → 95 % from 1e-4 to
> 1e-8). Above ~3e-2 the leading-edge control point (idx6) pushes the primal solver into
> non-convergence (documented failures at 5e-2 and 1e-1). **A1's original 1e-3 was already inside
> this safe window.**

**`:864` carried it as: *"Central differences, `step_calc=abs`, step between 1e-3 and 1e-2."***

**FIVE THINGS WERE DROPPED: the word *"Recommended"*; the case (A1); the DV class (FFD control
points); and BOTH MECHANISMS.** **And `step_calc=abs` makes the bounds necessarily DIMENSIONAL**, so
a bare interval with no DV class and no case **is not a quantity another team can even evaluate.**

> **RULED — `§2aq`: `:864`'s interval is a RECOMMENDATION, carried from a study of A1's FFD control
> points, and it is NOT a lab-wide admissible range and NOT a gate.** ***THE MECHANISMS TRANSFER; THE
> NUMBERS DO NOT.*** **A team on another case re-derives from the mechanisms: what step falls under
> MY primal's noise floor, and what step drives MY geometry's worst control point non-convergent.**

### §2aq.2 CONSEQUENCES, STATED NARROWLY

- **THE NINE ITEM FAMILIES USING STEPS OUTSIDE THE INTERVAL ARE NOT IN VIOLATION OF ANYTHING**
  (A1, A3, A4, A5, A6, B3, S1, W4; `h=0.05` family-wide). ***A recommendation cannot be violated,
  and this charter never gated it.*** **Nothing is re-graded.**
- **⚠ AND FROZEN REGISTRATIONS THAT GATE ON IT KEEP THEIR GATES, UNTOUCHED.** `G19-1b` restricts its
  graded candidates to the interval; **that is `G19-1b`'s OWN frozen gate, adopted in its own
  registration, and it stands whether or not this charter compelled it.** ***A registration may
  adopt a recommendation as its own gate; this ruling says only that the charter did not COMPEL
  it.*** **Nothing in `§2aq` moves a gate, and rule 2 is untouched.**
- **`D19R`'s internal inconsistency is dafoam's to reconcile in their own record, not mine to
  repair** — noted at `§2aq.3` as evidence, not as an order.

### §2aq.3 ⚡ THE REFERRAL UNDERSTATED ITSELF: THE DROPPED MECHANISMS INVERTED A RISK ORDERING

**The source carries TWO different intervals and the transcription collapsed them into one.** The
**failure bounds** are `~1e-4` (noise floor) and `~3e-2` (idx6 non-convergence). The **recommended
window**, `1e-3` to `1e-2`, sits conservatively INSIDE them with margin. ***`:864` transcribed the
conservative recommendation as though it were the admissible boundary.***

**The measurable consequence, in one registration's single sentence:** `D19R` excludes `1e-4`/`3e-4`
as *"below the sanctioned range"* **and in the same sentence sets `patchV` to `{1e-2, 3e-2}`.**

- **`3e-4` is ABOVE the source's `~1e-4` noise-floor threshold — it is in the region the source's own
  mechanism calls sound**, and it was excluded.
- **`3e-2` IS the source's upper failure threshold** — the edge at which idx6 is documented to drive
  non-convergence — **and it was adopted.**

> ***STRIPPED OF ITS MECHANISMS, THE INTERVAL CAUSED A FAMILY TO EXCLUDE A MECHANICALLY-SAFE STEP AND
> ADOPT THE SOURCE'S OWN BOUNDARY. THAT IS NOT A DOCUMENTATION BLEMISH; IT IS A RISK ORDERING
> INVERTED BY A TRANSCRIPTION.*** *`§2al` said a widening propagates into frozen pre-registrations
> and a grader's status string. Here it propagated into a CHOICE OF STEP.*

**No verdict is moved by this observation and no repair is ordered.** *It belongs to dafoam's record
and is stated so they need not re-derive it.*

### §2aq.4 ⚠ TWO DEFECTS FROM ONE SOURCE AT ADJACENT STEPS IS A PATTERN — AND THE RESPONSE IS AN ENUMERATION, NOT A THIRD RULING

**`§2al` (v1.56) corrected step 4 from `A_stepsize_study.md`. `§2aq` corrects step 5 from the same
source. `§2p.5`: two instances is a PATTERN.**

> **THE POPULATION IS NOT "STEP 5". IT IS *EVERY CLAUSE IN THIS CHARTER TRANSCRIBED FROM
> `A_stepsize_study.md`*, and fixing them one referral at a time cannot terminate** — ***which is the
> finding this team recorded at `V-90` today: a census keyed on what a defect is CALLED finds only
> the instances that name themselves.*** **The enumeration is OWED BY ME**: every clause sourced from
> that study, each marked FAITHFUL / WIDENED / NARROWED against the source text, **so a third
> referral is unnecessary rather than merely unwelcome.** **Owed, not done tonight, and recorded as
> owed rather than left to be discovered.**

### §2aq.5 ON THE REFERRAL ITSELF

**dafoam were right to refer and right on the finding, and their closing line — *"a family whose own
charter reading was corrected today, in its own §20, should be slow to correct somebody else's"* —
is the right instinct and was not needed here.** ***A team that finds a defect in another team's
charter and refers it as a question rather than a correction has done exactly what `§2ae` asks.***
**The defect is mine, in a clause I own, and the correction is mine to make.**

---

## Amendment — v1.63, 2026-09-04 — **§2ar THE ENUMERATION `§2aq.4` OWED IS DISCHARGED, AND IT TERMINATES: 14 CLAIMS, 9 FAITHFUL, 5 WIDENED, 0 INVENTED POST-STRIKE. THE TWO RULED DEFECTS WERE THE TWO *NUMBER-BEARING* MEMBERS OF A LIST WHOSE **CAPTION** AND WHOSE **BAND CLAUSE** CARRY THE SAME WIDENING UNSTRUCK — AND THE BAND CLAUSE IS THE ONE MEMBER COMPILED INTO CODE.**

**Appended 2026-09-04 by `verification-supervisor`. Lines whose number changed above this section: 0**
— all three corrections are STRIKES IN PLACE, each preserving its own line count, asserted before the
write (file line count unchanged at 7,678). **NOTHING IS RE-GRADED. NO VERDICT MOVES. NO GRADER'S OR
REGISTRATION'S OWN GATE IS DISTURBED, AND NO SDK CONSTANT IS TOUCHED BY A CHARTER EDIT.**

### §2ar.1 THE ENUMERATION, AND THE GOOD NEWS FIRST

**`§2aq.4` predicted the population was not "step 5". It was right, AND IT TERMINATES:** the
transcription is confined to **`§7` (`:833-897`)** plus one downstream application at `:1139-1144`.
**14 transcribed claims: FAITHFUL 9 · WIDENED 5 · NARROWED 0 · INVENTED 0 post-strike** (one
pre-strike, already struck by `§2al`). ***Most of this transcription is faithful and one clause is
verbatim*** — `:887-888` reproduces the source's failure entry word for word. **Stated plainly
because a report of an audit that lists only its hits is the defect this charter keeps naming.**

### §2ar.2 THE TWO GATED WIDENINGS — AND THE FIRST IS A REVERSAL, NOT A DROP

**(a) `:838-839`, THE RETROACTIVITY.** Charter: *"applied uniformly, **including to cases graded
under the old band**"*. Source heading `:79`: *"Recommended FD tolerance for grading **future** shape
derivatives **on this stack**"*. **`[VERIFIED BY ME AT SOURCE, BOTH SIDES]`**

> ***~~THIS IS NOT A DROPPED QUALIFIER. IT IS THE REVERSAL OF ONE.~~*** **[⚠ STRUCK IN PLACE 2026-09-05, v1.64 `§2as` — I OVERSTATED THIS AND THE MEASUREMENT CORRECTED ME: the source is NOT purely forward-looking. `A_stepsize_study.md:100-111` carries its OWN dedicated section, *"Should A4's 10.04 % still read as a PASS?"* → *"No — downgrade to CONDITIONAL / UNVERIFIED, not FAIL"*, RE-GRADING ONE NAMED PRIOR CASE. **The widening is real but NARROWER than I said: the source retroactively re-graded ONE NAMED CASE WITH REASONS; this charter generalised that into a STANDING RULE over EVERY case graded under the old band. Instance → class, not absence → presence.**]** `§2al` and `§2aq` were widenings
> by omission; **this clause ASSERTS RETROACTIVITY WHERE THE SOURCE'S OWN WORD IS "FUTURE".**

**(b) `:845-846`, THE PROVISIONAL FAIL.** Source `:92-94`: *"`>15%` or any flagged component → **FAIL
pending investigation**"*. The charter dropped *"pending investigation"*. ***The source's FAIL names
its own remedy; the charter's was a full stop.*** **The band VALUES are unchanged; what was lost is
that this FAIL carries an investigation obligation.**

**⚠ AND THESE TWO ARE COMPILED.** `sdk/workflows/adjoint_optimization.py:449-456` reproduces the
widened framing — *"applied uniformly across the whole ladder"* — beside `GATE_PASS_PCT = 5.0` and
`GATE_CONDITIONAL_PCT = 15.0`; `BAND_CONDITIONAL = 0.15` sits in four `d12*` graders; and
`d10f_grade.py:95` maps **CONDITIONAL → GATE FAIL**. ***`§2al` measured a widening propagating into
frozen registrations and a status string. This one propagated into a shipped SDK constant and a
verdict mapping.***

> **⚠⚠ WHETHER ANY VERDICT ACTUALLY RESTS ON EITHER WIDENING IS *NOT ESTABLISHED*, IS BEING MEASURED,
> AND I ASSERT IT IN NEITHER DIRECTION.** **A charter edit does not change code and does not re-grade
> a row.** *If a case was re-graded under (a)'s retroactivity, or carries a terminal FAIL the source
> would have made provisional, that is a matter for the owning team and possibly for Sanaa — and it
> will be reported when measured, not guessed at now.*

### §2ar.3 THE ROOT CAUSE, AND IT EXPLAINS `§2aq`

**(c) `:852`** read *"five steps, **none optional**"*; the source reads *"**Recommended** protocol:"*.
**Same dropped word as `§2aq`, one level up — governing the whole list rather than one member.**

**AND THE LIST IS A REMIX.** The source's own **item 5 IS THE BANDS** (`:92-94`), promoted out of the
list into the standalone standard above — **and charter step 5 was filled with material from a
DIFFERENT HEADING**, *"Recommended FD step size"* (`:72-77`).

> ***THAT REMIX IS THE MECHANISM THAT MADE `§2aq` POSSIBLE: a RECOMMENDATION from one section was
> renumbered into a list captioned "none optional."*** **The defect `§2aq` ruled was not a careless
> sentence; it was the predictable consequence of a structural rearrangement nobody recorded.**

### §2ar.4 THE GENERAL FORM, WHICH IS WHAT THESE THREE AMENDMENTS ARE REALLY ABOUT

> **RULED — `§2ar`: THIS CHARTER MAY SET A LAB-WIDE STANDARD ON ITS OWN AUTHORITY. WHAT IT MAY NOT DO
> IS BORROW A STUDY'S NUMBERS AND SILENTLY WIDEN THAT STUDY'S SCOPE TO MATCH ITS OWN AMBITION.**
> ***The numbers came from one stack; the ambition is the lab's. Presenting them as one thing is the
> defect — in `§2al`, in `§2aq`, and here.***

**A borrowed number must carry the scope it was measured in.** *If this charter wants it wider, it
must say so in its own voice and own the extrapolation — which is a claim a reader can then check.*

### §2ar.5 TWO JUDGEMENT CALLS I WAS OFFERED AND ONE THIRD CATEGORY I AM NAMING

Two clauses classified FAITHFUL carry named abridgements — `:848-850` drops the source's *reason* for
retiring the old band, and the *"do not grade on the aggregate alone"* carriage drops its
justification. **The lane judged neither widens the assertion and offered them for overrule. I AGREE
AND DO NOT OVERRULE — but they are not simply FAITHFUL either, and forcing them into that box loses
the thing `§2aq` proved harmful:**

> **A THIRD CATEGORY, NAMED: `MECHANISM-DROPPED, ASSERTION-FAITHFUL`. The claim is unchanged and
> nothing is widened — but the reader cannot RE-DERIVE it or know WHERE IT TRANSFERS.** ***That is
> exactly the state `:864` was in before `§2aq`: faithful in its numbers, unusable outside its
> case.*** **It is not a defect. It is the precursor to one, and it is worth a name so the next
> transcription notices.**

### §2ar.6 REMAINING, AND OWED

- **`:858-860`** drops *"the idx6 signature"* — mechanism-dropped, not gated, **left standing** and
  recorded.
- **`:1139-1144`** (A4's 10.04 %) drops *"UNVERIFIED"*, the non-refutation caveat, and the source's
  required next action (*"run this identical step-sweep protocol on A4 before re-confirming or
  reversing its verdict"*). **NOT struck tonight: it is the one place (a)'s retroactivity lands on a
  specific number, and whether A4's verdict moved — and whether that sweep was ever run — is under
  measurement. It will be corrected when I know which correction it needs.**
- **`:835-836`** (*"No gradient enters a record… without a finite-difference table beside it"*)
  **appears nowhere in the source and is NOT an invented transcription — it is this charter's OWN
  rule.** ***But it is the scope frame that (a) widened through: the source governs shape derivatives
  on one stack; `§7` governs every adjoint in the lab.*** **Left standing as the charter's own, and
  named so no future reader mistakes it for carried material.**

---

## Amendment — v1.64, 2026-09-05 — **§2as THE `§2ar` VERDICT-RISK QUESTION IS ANSWERED AND THE ANSWER IS **NO VERDICT RESTS ON EITHER WIDENING**. THE ONE VERDICT THAT MOVED WAS RE-GRADED BY THE SOURCE ITSELF, BY NAME, TWO DAYS BEFORE MY CLAUSE EXISTED — WHICH ALSO CORRECTS `§2ar`'s OWN CHARACTERISATION AGAINST ME. AND THE OBLIGATION I DROPPED HAD SURVIVED DOWNSTREAM ALL ALONG.**

**Appended 2026-09-05 by `verification-supervisor`. Lines whose number changed above this section: 0**
— both corrections are STRIKES IN PLACE preserving their line counts (file unchanged at 7,775 lines
before this append), asserted before the write. **NOTHING IS RE-GRADED. NO VERDICT MOVES.**
**`§2ar`'s corrections to `§7` STAND; what is corrected here is `§2ar`'s own account of WHY.**

### §2as.1 THE ANSWER: NO VERDICT RESTS ON EITHER WIDENING

**I said at `§2ar.2` that this was *"not established, being measured, and I assert it in neither
direction."* It is now measured.**

| channel | result |
|---|---|
| **retroactivity (`:838-839`)** | **one verdict moved — and it does NOT rest on this clause.** See `§2as.2` |
| **dropped *"pending investigation"* (`:845-846`)** | **ZERO abandoned terminal FAILs.** See `§2as.3` |
| **the code path** | **ZERO verdicts produced by either constant.** See `§2as.4` |

> **RULED: `§2ar` is a TEXT REPAIR. It does not go to Sanaa, no team owes a re-grade, and no row on
> the record was decided by a widened transcription.** *Stated as the disposition because I said in
> advance it would depend on this measurement, and it did.*

### §2as.2 ⚠ AND THE MEASUREMENT CORRECTS `§2ar` AGAINST ME — THE SOURCE IS NOT PURELY FORWARD-LOOKING

**A4's Ahmed-body gradient did move `PASS` → `CONDITIONAL`** (`cases/dafoam/DAFOAM_CASE_STATUS.md:88`,
`W5_GRADIENT_REGRADE.md:155-166`). **THE CHRONOLOGY EXONERATES THE CLAUSE, `[VERIFIED by git show]`:**

- **2026-07-28, `fb88d1f5`** — `A_stepsize_study.md` authored, carrying **both** its *"future … on this
  stack"* heading **AND its own dedicated section `## Should A4's 10.04% still read as a PASS?` →
  *"No — downgrade to CONDITIONAL / UNVERIFIED, not FAIL."***
- **2026-07-30, `ea53c110`** — this charter transcribes it and **adds** the retroactivity clause.
- **2026-08-01/02** — A4 recorded `CONDITIONAL`; **every record carrying the downgrade cites the
  STUDY or A4's own record. NOT ONE CITES THE CHARTER.**

> ***THE SOURCE RETROACTIVELY RE-GRADED A4 ITSELF, BY NAME, TWO DAYS BEFORE MY CLAUSE EXISTED.***
> **So `§2ar.2`'s claim — *"this is not a dropped qualifier, it is the reversal of one"* — IS
> OVERSTATED AND IS STRUCK.** **The widening is REAL but NARROWER: the source re-graded ONE NAMED
> CASE WITH REASONS; this charter generalised that into a STANDING RULE over every case graded under
> the old band.** ***Instance → class, not absence → presence.***

**AND NO OTHER CASE MOVED BY BAND APPLICATION**: A2 and the naca0015 sail are `≤ 5 %` `PASS` under
both bands; A1 and A5 are graded on the flagged-component and `>15 %` clauses, **both present in the
source**. **A4 is the only case where the old and new bands disagree at all.**

### §2as.3 THE OBLIGATION I DROPPED HAD SURVIVED DOWNSTREAM ALL ALONG

**Zero abandoned terminal FAILs. All three families carry an investigation:** A1 and A5 have a root
cause **identified and confirmed by repair** (IDWarp 2.6.2's degenerate branch,
`vectorUtils.f90:58`), their register entries deliberately open because the shipped toolchain still
fails; **A6 N=16 has a SUCCESSOR that resolved it** — row `G-30`, aggregate **1.0432 %**, zero sign
flips, `PASS` on 8 of 9, **an FD-reference artefact and not an adjoint defect.**

> **⚡ AND THE FINDING I DID NOT EXPECT: dafoam's own rung records transcribe the source's FULL
> wording — *"> 15 % or any flagged component → FAIL PENDING INVESTIGATION"* — at
> `A2/grading_confirmation/RESULTS.md:9` and `A2/per_component_table/RESULTS.md:52`.**
> ***THE PROVISIONAL-FAIL CLAUSE SURVIVED INTACT AT THE LEVEL WHERE GRADING ACTUALLY HAPPENS. IT WENT
> MISSING ONLY IN MY TRANSCRIPTION.*** **The lab was more faithful to the source than its own
> charter, and that is worth recording in the charter's own voice.**

### §2as.4 THE CODE PATH PRODUCED NOTHING

- **`d10f_grade.py`** cites **`DAFOAM_CHARTER.md` §2, NOT this charter's `§7`.** Its only verdict ever
  produced is **`PASS` at 4.401007e-08 relative**, via the `err ≤ 5 %` branch. **The CONDITIONAL
  branch has never executed on a real row.**
- **`BAND_CONDITIONAL = 0.15`** in the four `d12*` graders is used at one site each, inside
  `g6_bright_line` — **gate `G12R-6`, WHICH HAS NEVER RUN.** All three D12 items die at the
  *preceding* step-sizing gate. **11 D12 run roots, 665,644 files, ZERO carrying `charter_band`.**
- **The band's only exercise is a unit-test fixture**, whose own defect entry says *"until this
  repair the CONDITIONAL band had never been exercised by a passing unit."*
- **The SDK string is narrative, not a branch:** `GATE_CONDITIONAL_PCT` has **exactly one use site in
  the file — that string.** *So `§2ar.2`'s alarm that the widening "reached a shipped SDK constant
  and a verdict mapping" is true of the TEXT and false of any EXECUTED PATH, and I say so.*

### §2as.5 `:1139-1144` IS STRUCK — I NOW KNOW WHICH CORRECTION IT NEEDED

**`§2ar.6` deliberately left it standing until measured. It is stale in BOTH halves:** the
`ACTIVE_RESEARCH` row it reports as stale **was corrected 2026-08-14**; and **A4's verdict of record
has moved past the number entirely — `PASS` on a different configuration, np=1 stock, 1.10 %** —
**after the step-sweep the source demanded WAS RUN** (2026-08-02, W4, nine steps). **Struck in place.
Nothing re-graded; A4's `PASS` is dafoam's and is untouched.**

**ONE RESIDUE, REPORTED AND NOT RULED: the source asked for *"a large-step check around 3e-2"* and no
3e-2 A4 arm exists** — three of its four named checks ran. ***That is dafoam's to weigh on their own
rung; it is not a defect this charter may declare, and I do not.***

---

## Amendment — v1.65, 2026-09-06 — **§2at THE ESCALATED CHARTER QUESTION IS RULED, AND IT IS A **FALSE DICHOTOMY**: RULE 2 CONTAINS **TWO DIFFERENT POST-COMPUTE PROVISIONS GOVERNING TWO DIFFERENT OBJECTS**, AND BOTH INSTANCES APPLIED THE REGISTRATION'S RULE TO THE GRADING PATH. THE GRADING PATH'S TEST IS **HASH IDENTITY**, WHICH ADMITS NO "HARMLESS EDIT" CATEGORY AT ALL.**

**Appended 2026-09-06 by `verification-supervisor`. Lines whose number changed above this section: 0.**
**`CLAUDE.md` IS NOT TOUCHED AND IS NOT MINE TO TOUCH.** This ruling READS rule 2's own three
bullets; it amends nothing in the constitution. **Nothing re-graded. No verdict moves. No frozen
comparator is edited by this amendment, and none is authorised to be.**

### §2at.1 THE QUESTION AS ESCALATED

Twice in one day, from different directions (cfd's `JF1G` §7.1 and `M6SR` §33.5):

> ***"Does rule 2's post-compute clause protect the four named things, or everything that determines
> the answer?"***

**RULED: NEITHER. THE QUESTION IS A FALSE DICHOTOMY, AND THE ANSWER DEPENDS ON WHICH OBJECT IS BEING
EDITED.**

### §2at.2 RULE 2 HAS THREE BULLETS AND THE SECOND AND THIRD GOVERN DIFFERENT OBJECTS

**`[VERIFIED BY ME AT SOURCE, `CLAUDE.md:32-37`]`:**

> - *"After first compute gates are closed; **changes land only as dated addenda** that cannot alter a
>   gate, threshold, cap or label. **Originals are struck, never rewritten.**"*
> - *"**The grading path is fixed** at the pre-registration commit; verify **the frozen file IS the
>   file that ran** by hashing it against the committed blob."*

**THESE ARE NOT TWO STATEMENTS OF ONE RULE. THEY ARE TWO RULES OVER TWO OBJECTS:**

| object | post-compute test | what it permits |
|---|---|---|
| **THE REGISTRATION DOCUMENT** | *may not alter a gate, threshold, cap or label* | **dated addenda**; originals struck, never rewritten |
| **THE GRADING PATH** (comparator, grader, reader) | ***hash identity* — the frozen file IS the file that ran** | ***NOTHING.*** A hash admits no harmless category |

> **⚡ RULED — `§2at`: THE FOUR-NAMED-THINGS TEST IS THE WRONG TEST TO APPLY TO A COMPARATOR. It
> governs ADDENDA TO A DOCUMENT. A GRADING PATH IS PROTECTED BY BYTE IDENTITY, AND BYTE IDENTITY HAS
> NO CONCEPT OF CONSEQUENCE — a display-only edit breaks it exactly as completely as a threshold
> edit.** ***"It alters none of the four named things" is not a defence for touching a comparator,
> because the four named things were never what protected it.***

**AND THIS EXPLAINS THE ARCHITECTURE RATHER THAN INVENTING ANYTHING: it is precisely WHY `§2d.1`'s
four-condition exception exists and why it reaches the COMPARATOR.** *If a comparator were governed
by the four-named-things test, every display-only repair would be self-authorising and `§2d.1` would
have been unnecessary for exactly the cases it was written for.* **The exception exists because the
comparator's rule is absolute.**

### §2at.3 APPLIED TO `JF1G`: THE INSTINCT WAS RIGHT, THE READING WAS WRONG, AND THE OUTCOME IS UNCHANGED

**cfd HELD, did not edit, characterised both defects, and measured on two independent counts that
neither can move the verdict. That disposition is CORRECT and is endorsed.** Their reasoning —
*"on the LETTER of rule 2's post-compute clause it is permitted … BUT it moves the blob and breaks
the freeze"* — **reached the right answer through the wrong clause: on the letter of the clause that
actually governs a grading path, it was never permitted.** *There is no tension to resolve.*

> **⚡ AND THE POINT THAT MATTERS MORE THAN THE RULING: A DEFECT THAT PROVABLY CANNOT MOVE A VERDICT
> DOES NOT NEED REPAIRING IN THE FROZEN FILE AT ALL.** ***The record IS the repair.*** **The
> characterisation stands beside the case; the SUCCESSOR registration gets the corrected comparator.**
> **`§2d.1` is for a defect that MOVED A VALUE — not for one measured to be incapable of moving one.**
> *Invoking a repair exception for a harmless defect spends the exception's credibility on nothing.*

**The two `JF1G` defects — an aggregation that discards a correct per-level `NOT A RESULT`, and a
`[:60]` truncation printing `endTime 3000` for `30000` with no ellipsis — are REAL, are RECORDED, and
are REPAIRED IN THE SUCCESSOR, NOT IN THE FROZEN FILE.** ***The truncation is the sharper of the two:
a reader sees a number wrong by an order of magnitude that is RIGHT IN MEMORY*** — the silent-
corruption family in a display rather than in a graded artifact, and it belongs in that collection.

### §2at.4 ⚠ `M6SR` §33.5 IS **NOT** RULED HERE, AND THE REASON IS THE RULING ITSELF

**The two instances are NOT the same object, which is exactly what `§2at.2` predicts, so I decline to
dispose of both with one stroke.** **Relaxation factors are not a display and may not be a grading
path at all** — *if they live in the CASE SETUP they are part of the RUN, and changing them
post-compute does not produce an amended registration, it produces A DIFFERENT RUN, which is a NEW
REGISTRATION and not an addendum question.* **HELD for its own reading against this framework. I have
not read it and I assert nothing about it.** ***Two instances arriving together is a reason to check
whether they are one class, not a licence to assume it.***

### §2at.5 WHY THIS IS MINE TO RULE, STATED SO IT IS NOT MISTAKEN FOR OVERREACH

**`CLAUDE.md` is Sanaa's alone and is untouched.** **What I have done is READ ITS THREE BULLETS AND
NAMED WHICH OBJECT EACH GOVERNS** — the `§2am` distinction: *naming the reader a document already
uses is INTERPRETATION; selecting a reader it never used would be ALTERATION and goes to her.*
**Rule 2's own provenance line names `VERIFICATION_CHARTER` §2b/§2d/§2d.1 as its operationalisation,
which is this charter's to hold.** **If Sanaa reads rule 2 differently, her reading governs and this
section yields to it without argument.**

**AND THE ESCALATION WAS RIGHT EVEN THOUGH THE GAP WAS NOT REAL.** *Two teams, from different
directions, hit the same sentence and neither invented a permission for itself; both HELD and asked.*
***A question that turns out to have an answer already in the text is not a wasted escalation — it is
the system working, and the answer is now written down where the third instance will find it.***

---

## Amendment — v1.66, 2026-09-06 — **§2au THE MACHINE-READABLE FREEZE PIN, APPROVED BY SANAA AND LANDED — WITH TWO DISCLOSURES SHE IS ENTITLED TO: I HAD **WITHDRAWN** THIS PROPOSAL, AND THE FORM AS ENUMERATED IS **IMPOSSIBLE**. THE PIN LIVES IN THE FREEZE COMMIT'S MESSAGE, NOT IN THE FROZEN DOCUMENT, AND IT IS **NOT** THE RULE-2 ANCHOR.**

**Appended 2026-09-06 by `verification-supervisor` on Sanaa's approval, `etc/sessions/2026-09-06T0230Z_sanaa_everything_approved.md`, capture `b7c56371`, her verbatim word *"everything approved"* over an enumerated list whose item 4 is this pin. `[CAPTURE READ BY ME AT SOURCE, not taken from the relay — rule 9.]`**
**FORWARD-ONLY. NO BACKFILL. No existing registration acquires a defect, nothing is re-graded, and no frozen document is reopened to add a pin.**

### §2au.1 ⚠ DISCLOSURE ONE: I WITHDREW THIS PROPOSAL, AND SHE MAY NOT HAVE KNOWN

**`§28.13.5` (commit `0a8aa9f7`, 2026-09-04) reads: *"SANAA'S DESK ITEM #2 — THE MACHINE-READABLE
FREEZE PIN — IS WITHDRAWN BY THIS TEAM."*** I withdrew it because I had proposed it as **rule 2's
anchor**, and then measured that ***rule 2 turns on FIRST COMPUTE, not on the freeze*** (`§28.13.1`,
and now `§2at`) — so a freeze pin obtains a timestamp rule 2 does not use.

**Her approval was given over a list that presented it as live. I record the withdrawal here rather
than accept an approval she may have granted without it.**

> **AND I LAND IT ANYWAY, FOR A REASON THAT SURVIVES THE WITHDRAWAL: my withdrawal disposed of the
> RULE-2 purpose, not of the PROVENANCE one — and `§28.12` MEASURED that the freeze is currently
> unrecoverable from prose.** `FROZEN` matches inside `UNFROZEN`; *"NOT THE FREEZE COMMIT"* scores as
> a freeze; **F28's DESCRIPTIVE subject beat its DECLARATIVE one**; and **147 of 415 registrations
> carry no freeze-matching subject at all.** ***That is a real, measured defect, and the pin fixes
> exactly it.*** **If she intended the rule-2 purpose, this clause does not deliver it and she should
> overrule me.**

### §2au.2 ⚠⚠ DISCLOSURE TWO: THE FORM AS ENUMERATED IS IMPOSSIBLE, AND I SAY SO RATHER THAN SHIP SOMETHING THAT CANNOT WORK

The enumeration reads: *"each pre-registration records its own freeze sha in a fixed field at freeze
time."*

> ***A DOCUMENT CANNOT CONTAIN THE SHA OF THE COMMIT THAT COMMITS IT.*** **A git sha is computed OVER
> the content; writing the sha into the document CHANGES the content and therefore the sha.** **The
> literal form is not merely awkward — it has no fixed point.** *And every workaround that writes the
> sha in afterwards MUTATES A FROZEN DOCUMENT, which is the one thing the freeze exists to prevent.*

**Her verbatim word is *"everything approved"*; the field-in-document wording is the enumeration's
rendering of MY OWN earlier proposal, and the impossibility is therefore MY error being faithfully
relayed.** **I implement the INTENT — *the freeze is machine-identifiable* — and state the departure
so she can overrule the form.**

### §2au.3 THE CONVENTION

> **RULED — `§2au`: AT FREEZE TIME, THE FREEZING COMMIT'S MESSAGE CARRIES, ON ITS OWN LINE:**
>
> ```
> FREEZE-PIN: <repo-relative path of the registration>
> ```
>
> **One such line per registration frozen by that commit. The FREEZE COMMIT IS THE PIN; the token
> makes it FINDABLE.**

**WHY THE COMMIT MESSAGE AND NOT THE DOCUMENT:** it has **no fixed-point problem**, it **mutates no
frozen file**, there is **no sidecar to drift out of sync**, and **the pin is written by the very act
it records** — *a freeze that forgot its pin is a freeze that did not happen in the machine-readable
sense, which is the correct failure mode.*

**HOW IT IS READ:** `git log --grep='^FREEZE-PIN: <path>$'` returns the freeze commit, exactly, with
**no prose regex and no `FROZEN`-inside-`UNFROZEN` hazard.**

**AND THE READER OF THE DOCUMENT IS NOT LEFT OUT:** a frozen registration carries one line —
**`**FROZEN.** Freeze pin: this document's freezing commit carries `FREEZE-PIN: <its own path>`.`** —
so **a reader who has the document but not the history knows the pin exists and where to look.**
*That line is written at freeze time, is not a sha, and creates no fixed point.*

### §2au.4 WHAT THIS PIN IS **NOT**

- **IT IS NOT THE RULE-2 ANCHOR.** ***Rule 2's post-compute clause turns on FIRST COMPUTE*** — edits
  between freeze and first compute are **expressly lawful** (`§28.13`, `§2at`). **Nobody may cite
  `§2au` to date a rule-2 question.** *Stated in the clause because the wrong use is the likely one.*
- **IT IS NOT A GATE AND REFUSES NOTHING.** No verdict depends on it; a missing pin is a **provenance
  gap**, not a defect in a result.
- **IT DOES NOT REACH BACKWARD.** **NO BACKFILL** — the 147 unpinnable registrations stay unpinnable,
  and `§28.12`'s prose-anchor caveats continue to govern everything frozen before today.
- **NO INSTRUMENT IS BUILT BY THIS AMENDMENT.** *It is auditable with one `git log --grep`, and
  `§28.18`'s regress property applies: a guard is code and adds surface — this convention deliberately
  adds none.*

### §2au.5 ITS OWN ORIGIN STORY, RECORDED AS SHE ASKED

**Proposed 2026-09-04, the morning the F28 transcription work found this lab's freeze instruments
GUESSING SHAS FROM COMMIT PROSE.** **DECLINED BY ME the same day** — *not on its merits, but because
it required a convention across six teams and I would not impose one unasked* (`§28.12.5`).
**WITHDRAWN BY ME a few hours later**, when the measurement showed I had aimed it at the wrong event.
**APPROVED BY SANAA 2026-09-06 and landed here, in a corrected form, for the purpose that survived.**

> ***A proposal declined for needing permission, withdrawn for being aimed wrong, and landed on her
> word for the one purpose that outlived both objections. The record is kept because a clause whose
> history is invisible looks like it was always obvious.***

---

## Amendment — v1.67, 2026-09-06 — **§2av THE `VMFL046-R4` `§2d.1` PETITION IS **GRANTED**, NARROWLY, AND ON A TEST THIS CHARTER HAS NOT STATED BEFORE: FOR A **CRASH** REPAIR THE ANTI-GAMING QUESTION IS NOT ONLY *WHO FOUND IT* BUT ***HOW MANY WAYS COULD IT BE FIXED*** — AND A DEFECT WITH EXACTLY ONE CORRECT REPAIR CANNOT BE AIMED AT AN ANSWER.**

**Appended 2026-09-06 by `verification-supervisor`. Lines whose number changed above this section: 0.**
**Petitioned by ansys-verification at `00cb4530`, REFERRED rather than self-granted. Nothing is
re-graded by this amendment; it authorises ONE narrow repair and grades nothing.**

### §2av.1 THE FACTS, AND THE ONE I VERIFIED MYSELF

`[RELAYED]` All three `VMFL046-R4` levels completed **rc = 0 at `endTime` exactly**, inside estimate
(**488.74 / 536 core-min, 0.912×**). The **frozen comparator then CRASHED pre-verdict** — a
`TypeError`, **three of four plant call sites passing `pl["A"]`, a float, to functions whose
signatures take a window/series**; only `plant_gate_reader` called correctly. **59 selftest arms
passed without one exercising the call site.**

**`[VERIFIED BY ME AT SOURCE, NOT RELAYED — because conditions (3) and (4) turn on it]`: NO PUBLISHED
VERDICT FOR `VMFL046-R4` EXISTS.** A search across `docs/` and `verification/` for any rule-1 verdict
token bound to `R4` returns **nothing**. *The petition's factual predicate holds.*

### §2av.2 THE EASY EXIT, DECLINED

**`§2d.1`'s permission clause opens *"A change on the grading path made after the first GRADED
solve…"* — and NO SOLVE WAS EVER GRADED here.** On the letter, the clause is not engaged and the
petition needs no exception at all.

> **I DECLINE THAT EXIT AND RULE THE FOUR CONDITIONS ANYWAY.** **`§2d`'s protection runs from the
> FREEZE, not from first grading, and the DATA EXISTS** — so the hazard `§2d` guards, *seeing the
> data and then adjusting the reader*, **IS LIVE.** ***A grant that rested on a trigger technicality
> would be the weakest kind, and the next petitioner would cite it.***

### §2av.3 THE FOUR CONDITIONS, READ BY ME

**(1) A DEMONSTRABLE ERROR RATHER THAN A PREFERENCE — MET.** Passing a float where the function's own
signature takes a window/series is **wrong by the file's own declarations**. *Not a preference; the
code contradicts itself.*

**(2) AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS — MET AT THE LIMITING CASE.** The error was
established **not by an instrument but by the LANGUAGE RUNTIME.** `§2d.1`'s own reasoning is that
*"an error found by something that grades nothing cannot have been selected to move a verdict in a
wanted direction, because the thing that found it does not know which direction that is."*
***A type system is the purest possible satisfaction of that: it grades nothing, and it cannot even
represent the verdict.***

**(3) THE RECORD DISCLOSES IT, NAMES THE INSTRUMENT, QUANTIFIES WHAT MOVED — and (4) PRE-REPAIR
VALUES BESIDE THE PUBLISHED ONES — MET, AND I RULE *WHY*, BECAUSE "VACUOUSLY SATISFIED" IS A PHRASE
THIS CHARTER HAS SPENT A WEEK CONVICTING.**

> ***A VACUOUSLY SATISFIED CONDITION IS A DEFECT WHEN ITS PURPOSE IS UNMET; IT IS SOUND WHEN THE
> HAZARD IT GUARDS DOES NOT EXIST.*** **Conditions (3) and (4) guard against UNDISCLOSED MOVEMENT OF
> PUBLISHED VALUES. With no published values, there is no movement to disclose — the guard has
> nothing to guard, and that is a FACT ABOUT THE CASE, not a gap in the evidence.** **This holds ONLY
> because the absence was VERIFIED (`§2av.1`) rather than asserted; had one cell been published,
> both conditions would bite in full.**

### §2av.4 ⚡⚡ THE TEST THIS CHARTER HAS NOT STATED BEFORE, AND IT IS WHY THE LIVE DATA DOES NOT CONTAMINATE THE GRANT

**The petitioners hold the data. On `§2d`'s own logic that is exactly when a reader must not be
adjusted. So the grant needs more than condition (2), and here is what supplies it:**

> **RULED — `§2av`: FOR A **CRASH** REPAIR, THE ANTI-GAMING QUESTION IS NOT ONLY *WHO FOUND THE
> ERROR* BUT ***HOW MANY WAYS COULD IT BE FIXED?*** **A repair whose correct form is FORCED — by a
> signature, a type, an interface — HAS NO DEGREES OF FREEDOM POINTING AT THE ANSWER, and therefore
> CANNOT BE AIMED, however much the repairer knows about the data.***
>
> **Here the correct call is determined by the function's own signature. There is exactly one right
> repair, and the repairer cannot choose among alternatives to tilt a reading.** ***A defect with
> exactly one correct repair cannot be selected to fit an answer.***

**AND THE CONVERSE IS THE LIMIT OF THIS RULING, stated so it is not read wider: WHERE A CRASH ADMITS
SEVERAL CORRECT-LOOKING REPAIRS THAT WOULD READ THE DATA DIFFERENTLY, THIS TEST FAILS AND `§2d.1`'s
ordinary burden returns IN FULL.** *`§2av` is not a general licence to repair crashes; it is a
licence to repair crashes whose fix is forced.*

### §2av.5 THE GRANT, AND ITS SCOPE

> **GRANTED: the three miscalled plant call sites in `VMFL046-R4`'s frozen comparator may be
> repaired to pass the arguments their signatures require, and the existing run data may then be
> graded through the repaired path.**

**REQUIRED WITH IT, and the last of these is not optional:**

1. **The pre-repair sha, the post-repair sha, and the diff recorded in the case record.**
2. **The crash REPRODUCED and recorded** — the `TypeError` shown, not described.
3. **The repair confined to the argument passed at those three sites.** *Any change to what is
   computed, compared or thresholded is outside this grant and void under it.*
4. **⚡ A DRIVEN CONTROL THAT EXERCISES THE PREVIOUSLY-UNEXERCISED CALL SITE.** **59 arms passed
   while the defect shipped through them — `§2p.3(d)`'s exact class — and shipping the repair without
   covering the site REPEATS THE DEFECT WITH A SMALLER AUDIENCE.** ***`§28.19` applies directly: the
   59 arms did not measure the comparator, they measured their own coverage, and that measurement is
   the free product of this crash.***

**NOT COVERED: the exit-1-where-the-convention-is-refuse-at-2 defect (`§36.5`'s class).** It was
REPORTED, not petitioned, and I rule what is before me. **⚠ BUT a second touch of a frozen file is
itself a cost, so if ansys want it repaired they should AMEND THIS PETITION NOW and I will rule it
under the same grant rather than force two intrusions.** *I will not fold it in unilaterally —
folding an unpetitioned repair into an authorised one is how a narrow grant becomes a wide one.*

### §2av.6 THE PRICE IS NOT A GROUND, AND I HONOUR THEIR OWN STIPULATION

**ansys wrote that *"the price is not an argument for the grant."* They are right, and the grant
above rests on the conditions alone.** **I note the cost only to record what refusal would actually
buy:** *a ~489 core-min re-run REGENERATES DATA THAT IS NOT IN QUESTION AND LEAVES THE CRASHING
COMPARATOR UNTOUCHED.* ***Re-running the solve does not repair a reader.*** **Refusal's real
alternative is a NEW REGISTRATION with a corrected comparator — lawful, and it spends 489 core-min to
obtain data already on disk.** *That is a fact about the alternative, not a reason for the grant.*

### §2av.7 ON THE PETITION ITSELF

**They REFERRED rather than self-granted, on the reasoning that *"a supervisor who would gain from a
repair is the wrong party to rule it lawful."* That is exactly right and it is why this exception has
a referee at all.** **They also convicted themselves of OVER-CLAIMING — one mutated line generalised
to a file — against their own interest in a document seeking a grant.**

**⚠ AND A SECOND INSTANCE FOR THE RECORD: dafoam's 53 controls missed a truncation (`§28.19`);
ansys's 59 arms missed this call site. TWO INDEPENDENT INSTANCES IN TWO DAYS of a large control suite
passing while the defect shipped straight through it.** ***`§28.19.2`'s inversion now has its second
instance: a big green suite is a coverage measurement waiting to be read.***

---

## Amendment — v1.68, 2026-09-06 — **§2aw THE W1 AUDIT-SCOPE PETITION IS **GRANTED AT REPAIR (c)**, AND IT FALLS IN A GAP `§2av` DID NOT NAME: A REPAIR WHOSE FREEDOM IS **ORTHOGONAL TO THE VALUE** BUT NOT TO **WHETHER A VALUE IS PUBLISHED**. WHAT DISPOSES OF IT IS THAT THEY REFERRED THE **CHOICE**, NOT MERELY THE PERMISSION.**

**Appended 2026-09-06 by `verification-supervisor`. Lines whose number changed above this section: 0.**
**Petition read by me at source: `docs/ansys_verification/PETITION_VMFL046_R4_W1_AUDIT_SCOPE.md`.
Nothing re-graded. Row #61 stands `NOT A RESULT` until the repaired path is driven.**

### §2aw.1 MY OWN CONVERSE DOES NOT STRICTLY BITE, AND I SAY SO BEFORE USING IT

**They cite `§2av.4`'s converse against themselves — *"where a crash admits SEVERAL correct-looking
repairs THAT WOULD READ THE DATA DIFFERENTLY."*** **On my own wording the trigger is NOT met.** Their
`§5.1`, stated against their own interest and in their favour, is correct and I verify the claim's
shape: **none of (b), (c) or (d) touches `shock_series`, `plateau`, the gate (`1.250 m ± 5 %`) or
`DELTA_X = 6.250e-04 m`.** ***Whichever is chosen, `x_shock` and the plateau statistic are computed
byte-identically.*** **These repairs do not read the data differently.**

### §2aw.2 ⚡⚡ THE THIRD CATEGORY, WHICH `§2av` DID NOT NAME — AND IT IS NOT SAFE MERELY BECAUSE THE NUMBER IS INVARIANT

> **RULED — `§2aw`: BETWEEN A *FORCED* REPAIR AND ONE THAT WOULD MOVE THE NUMBER LIES A THIRD CASE —
> A REPAIR WHOSE DEGREES OF FREEDOM ARE **ORTHOGONAL TO THE VALUE** BUT DETERMINE **WHETHER THE
> COMPARATOR REFUSES OR PROCEEDS**.**
>
> **⚠ AND THAT FREEDOM IS GAMEABLE, WHICH THE PETITION DOES NOT QUITE SAY: *choosing to refuse rather
> than publish an unwelcome number is itself a form of selection.*** **A repairer who knew the value
> would be a `GATE FAIL` could prefer the repair that keeps refusing.** ***Value-invariance is
> therefore NOT sufficient to make such a repair self-authorising, and `§2av`'s narrowness is not
> relaxed by it.***

### §2aw.3 WHAT ACTUALLY DISPOSES OF IT: THEY REFERRED THE **CHOICE**, NOT THE PERMISSION

**The degree of freedom `§2av` exists to deny is THE PETITIONER'S. Here the petitioner has surrendered
it:** their `§6.1` asks for *"a ruling on which of (b), (c) or (d) … made by the referee and not by
this team."*

> ***A FREEDOM SURRENDERED TO A REFEREE WHO DOES NOT KNOW THE ANSWER IS NOT A DEGREE OF FREEDOM
> POINTING AT THE ANSWER.*** **I do not know what `VMFL046-R4` returns either, and I choose below on
> grounds stated ENTIRELY WITHOUT REFERENCE TO ANY VALUE — which is the test that the choice is not
> aimed, and it is a test the reader can apply to my reasoning rather than take on my word.**

### §2aw.4 THE CHOICE: **(c)**, AND WHY (b) AND (d) ARE REJECTED FOR REASONS RATHER THAN BY ELIMINATION

**(a)** is eliminated by the file's own `:1354` arm — an empty audit refuses. **Their elimination is
correct and is not mine to re-make.**

**(b) — REJECTED. Arming the audit after the plants collapses coverage from 33 real reads to ONE.**
***A guard that audits one read instead of thirty-three has not been narrowed, it has been
hollowed*** — and the 33 that go unaudited are precisely the reads that produce the value. **That is
this collection's vacuous-predicate family (`§28.8`) being installed deliberately as a repair.**

**(d) — REJECTED FOR A REASON, NOT BY TIE-BREAK. Snapshot-and-restore yields the same set as (c)
*here*, and that equivalence is COINCIDENTAL TO THIS CASE.** ***It would also mask a plant that read
a REAL out-of-window sample*** — **a hazard W1 exists to catch.** **A repair that is equivalent today
and blind tomorrow is strictly worse than one that is correct for a stated reason.**

> **GRANTED AT (c): AUDIT ONLY PATHS INSIDE THE RUN ROOT — keeping all 33 real reads and excluding
> the 19 synthetic.** **THE GROUND IS SEMANTIC AND VALUE-FREE: *W1 asks whether the comparator
> consumed RUN DATA outside its registered window, and a `/tmp` scratch file created by the
> comparator's own plant machinery is not run data.*** ***An audit's subject is the case's data; the
> auditor's own artifacts were never in scope, and excluding them narrows nothing that W1 was ever
> measuring.*** **Their own recommendation was (c); I reach it independently and record that the
> agreement is not the reason.**

### §2aw.5 `§2d.1`'s FOUR CONDITIONS, ON THE FULL BURDEN

**(1) MET** — the error is **measured, not preferred**: the 33 pre-plant reads are **exactly** the 33
registered-window samples, and the 19 are the comparator's own `/tmp` scratch. *A scope that counts
the auditor's artifacts as the audited subject is demonstrably wrong, whatever the right boundary
elsewhere.*

**(2) MET** — established by **W1's own read-audit measured against the registered window list**, an
identity check that **grades nothing and knows nothing about `x_shock`**. `§2d.1` names *"a guard"*
explicitly, and this is one.

**(3) HAS REAL CONTENT THIS TIME, UNLIKE `§2av`, AND IS REQUIRED IN FULL.** Something *can* move here
— **whether the comparator refuses or proceeds.** **The record must state that before the repair W1
REFUSED, that after it W1 passes with 33 audited reads and 19 excluded, and must NAME the 19.**

**(4) MET AS TO PUBLISHED VALUES (none exist; row #61 is `NOT A RESULT`) — AND CONVERTED FORWARD:
the pre-repair state, `REFUSED AT W1`, is recorded BESIDE whatever verdict now lands.** *`§2av`'s
condition-4 reasoning applies, but this time a value WILL be published, so the pre-repair state must
travel with it.*

**REQUIREMENTS, as they themselves proposed:** shas and diff · the refusal **reproduced** · the repair
**confined to the audit's path-selection** — *any change to `shock_series`, `plateau`, the gate or
`DELTA_X` is outside this grant and void under it* · **and a driven control exercising the
plants-then-audit ORDERING**, which is the coverage gap that produced both defects.

### §2aw.6 ⚠ THEIR RESTRAINT IS ADMIRABLE AND I DECLINE TO MAKE IT A CONDITION

**They did not look at the answer. `pl["x_level"]` was computed at `:1045` and sat in memory when the
comparator refused at `:1069`; one line would have printed it; it was not added.** **They also
declined my `§2av.5` fold-in offer on the exit-code defect as unforced widening, and they made TWO
substitutions rather than three because repairing the third site would have exceeded the grant.**
***That is the conduct this exception depends on and it deserves saying.***

> **AND IT IS NOT A CONDITION, DELIBERATELY. `§2d.1`'s conditions are constructed so THE REFEREE NEED
> NOT TRUST THE PETITIONER.** ***"I did not look" is not checkable by a referee, and a grant that
> rested on it would teach the next petitioner that the assurance is the price of admission.*** **I
> weigh it as conduct, I grant on the conditions, and I record the distinction so it is not lost:
> `§2aw.3`'s surrender of the CHOICE is checkable — the petition asks me to choose, in writing — and
> that, not their self-report, is what carries the grant.**

### §2aw.7 THEIR LARGER QUESTION — RECORDED, ONE HALF RULED, THE OTHER NOT MINTED TONIGHT

They ask whether a comparator selftest that **never drives `grade()` end-to-end on a synthetic run
root** should continue to count as a freeze qualification.

- **⚡ THE HALF I RULE NOW, because it is a false-coverage declaration and those are this audit's
  subject: `check_freeze_ready.py`'s C3 DECLARES that it checks the comparator AND DOES NOT CHECK THE
  COMPARATOR'S PRODUCTION ORDERING.** ***A check whose declaration is wider than its coverage is worse
  than an absent check, because the declaration is what a reader relies on.*** **RECORDED as a
  finding; the repair is its owner's.**
- **THE HALF I DO NOT MINT: end-to-end drive as a freeze qualification.** **Two defects in one day is
  striking — and they are TWO DEFECTS IN ONE FILE, which is one population member, not two
  (`§2p.5`).** **And `§28.18`'s regress applies: a fourth layer of guard is a fourth surface.**
  **ENDORSED AS PRACTICE; NOT MINTED. `§2ap` already requires the producer's real output through the
  pinned consumer, and this would extend it to the consumer's own ordering.**
  **⚠ WHAT WOULD MOVE ME, STATED IN ADVANCE: the same class in a SECOND FILE, or one instance where
  the missing end-to-end drive let a WRONG VERDICT PUBLISH rather than merely blocking one.**

---

## Amendment — v1.69, 2026-09-06 — **§2ax "FIRST COMPUTE" AT ITS LOWER EDGE: A CONTAINER THAT STARTS AND ABORTS WITH **NO TIME DIRECTORY BEYOND 0** HAS NOT REACHED FIRST COMPUTE FOR RULE 2's PURPOSES. THE ANCHOR IS RULE 2's AND RULE 4's OWN OPERATIONAL TESTS — I INTERPRET, I DO NOT DEFINE. AND THE LINE IS "GRADEABLE STATE PRODUCED", NOT "CONTAINER EXITED CLEANLY".**

**Appended 2026-09-06 by `verification-supervisor`. Lines whose number changed above this section: 0.**
**Referred by dafoam because it gates a repair a supervisor cannot self-grant, and because it RECURS
— tonight produced several no-solve aborts. Nothing re-graded. No frozen document reopened.**

### §2ax.1 THE ESCALATION SELF-CHECK, DONE FIRST BECAUSE IT DECIDES WHO RULES

**dafoam asked me to escalate to Sanaa in one line if this is a constitutional reading of rule 2
itself, and to rule it if it is interpretation within the referee's scope. I judge it
INTERPRETATION, and I state the test I applied so the judgement is checkable, not asserted.**

**`§2am`'s distinction governs: naming the reader a document ALREADY USES is interpretation; SELECTING
a reader it never used is alteration and goes to her.** ***Rule 2 and rule 4 already carry two
operational tests for "did compute happen", and I am naming them, not choosing a meaning the
constitution never had:***

- **Rule 2 bullet 1 `[VERIFIED, `CLAUDE.md:31-32`]`: an amendment is pre-compute when it can *"name
  the run directory that does not exist."*** ***The constitution's own pre-compute test is the
  ABSENCE OF THE RUN DIRECTORY.***
- **Rule 4 `[VERIFIED, `CLAUDE.md:49-55`]`: a run is dated by *"every field at `endTime` NEWER than
  the case's own `0/T`"*, the age guard, because a produced answer lives in a time directory the
  solver wrote.** ***The constitution's own test for "the run produced something" is a TIME DIRECTORY
  the solver wrote.***

**Both point one way, and I am reading them, not overriding them. If Sanaa reads "first compute"
differently, HER READING GOVERNS AND THIS SECTION YIELDS WITHOUT ARGUMENT** — the same deference
`§2at` and `§2au` carry. **`CLAUDE.md` is untouched and is not mine to touch.**

### §2ax.2 THE RULING

> **RULED — `§2ax`: A CONTAINER THAT STARTS AND REFUSES OR CRASHES WITHOUT WRITING ANY TIME DIRECTORY
> BEYOND `0` — zero solver iterations, no gradeable artefact — HAS NOT REACHED "FIRST COMPUTE" FOR
> RULE 2's PURPOSES. THE REGISTRATION'S GATES REMAIN OPEN, AND A PRE-COMPUTE AMENDMENT MAY BE
> SELF-APPLIED BY THE SUPERVISOR UNDER RULE 2 BULLET 1.**

**The reason is rule 2's own stated purpose, not a convenience: *"the freeze proves the gate could not
have been chosen to fit the answer."*** ***An answer that does not exist cannot have been fitted to.***
A no-solve abort produced **nothing rule 2 protects** — no `x_shock`, no plateau, no field at
`endTime`, no number a gate could be bent toward. **The freeze has nothing to prove because there is
nothing it could have been chosen against.**

### §2ax.3 ⚠ THE LINE IS "GRADEABLE STATE PRODUCED", NOT "CONTAINER EXITED CLEANLY" — AND THIS IS THE HALF THAT KEEPS THE RULING FROM OVER-REACHING

**A crash is NOT automatically pre-compute, and reading `§2ax` that way would be a serious error I
foreclose here:**

| what happened | time dir beyond 0? | disposition |
|---|---|---|
| container aborts at startup / staging / a stale-pin read | **NO** | **pre-compute** (`§2ax`) — gates open, amend and self-apply |
| solver ran, wrote time dirs, THEN crashed or diverged | **YES** | **post-compute** — the run happened and FAILED completion; **rule 4 → `NOT A RESULT`**, gates CLOSED, repairs go through `§2d.1` |

> ***THE DISCRIMINATOR IS WHETHER THE SOLVER PRODUCED A STATE A GATE COULD READ — not the exit code,
> not whether the crash was clean.*** **A run that computed 12,000 iterations and then died has
> reached first compute as fully as one that finished; its gates are closed. `§2ax` reaches ONLY the
> container that never produced a gradeable state at all.**

**⚠ AND A TRAP I HIT WHILE VERIFYING AND NAME SO THE NEXT READER DOES NOT: a bare `0/` DIRECTORY IS
NOT A TIME DIRECTORY IN THIS SENSE.** `[MEASURED — D6RF4's run root holds `P_conv/0`, `base/0`, etc.,
and NO directory beyond `0`.]` **`0/` is STAGING — the initial field, written before the solver
runs; it is the age-guard's DATUM, not its subject.** ***The test is a time directory the solver
WROTE, i.e. one BEYOND `0`.*** A reader who counts `0/` as compute will call every staged-but-unrun
case post-compute and close gates that never opened.

### §2ax.4 APPLIED TO D6RF4, AND WHAT IT DOES NOT DECIDE

**`[VERIFIED BY ME AT SOURCE]`: D6RF4's authoritative run root
(`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe`) holds `0/` staging and
NO time directory beyond `0`; the four launches record `launcher_rc=2 … NOT-the-solver-rc`.**
***No solve occurred. By `§2ax` this is pre-compute, its gates are open, and the stale-pin repair
(`MD5_EXTRACT` at `endpoint_physical.py:95`) is a LAWFUL PRE-COMPUTE AMENDMENT the supervisor
self-applies under rule 2 bullet 1 — NO `§2d.1` PETITION IS REQUIRED.***

**WHAT `§2ax` DOES NOT DECIDE, stated so the grant is not read wider than it is:**

- **It does not certify the repair.** *That the manoeuvre is pre-compute means the SUPERVISOR rules
  it, under rule 2's pre-compute discipline — the amendment must still state the condition and how it
  was checked (rule 2 bullet 1), and the stale md5 must be demonstrated, as dafoam say it is (sole
  outlier of 22 pins, three ways). I authorise the PROCEDURE, not the pin.*
- **It grants nothing retroactive.** No prior verdict rests on D6RF4; none exists.
- **It changes no gate, threshold, cap or label**, and a repair that touched any of those would be
  outside rule 2 bullet 1 whether or not compute had occurred.

### §2ax.5 WHY A CLASS RULING RATHER THAN A CASE ONE — AND THE ANTI-SHELTER CLAUSE

**dafoam is right that this recurs, and `§28`'s own lesson is that a no-solve abort is common: the box
restarts, a stale pin, a staging error, a refused launch all produce this exact state.** **A
case-by-case ruling would route every one of them through a `§2d.1` petition that has nothing to
grade.** **So `§2ax` settles the class.**

**⚠ BUT A CLASS RULING IS A WIDER SURFACE, so it carries its own guard, stated in advance so it cannot
be fitted later:**

> **`§2ax` IS AVAILABLE ONLY WHERE THE ABSENCE OF A TIME DIRECTORY BEYOND `0` IS *VERIFIED AT SOURCE
> IN THE AUTHORITATIVE RUN ROOT*, NOT ASSERTED FROM A STATUS FILE.** **`§28.15` measured a
> `launcher_rc` that lied about a solver rc, and `§28.13.4` measured a refused launch writing a false
> `rc=0` — SO A STATUS FIELD IS NOT EVIDENCE THAT NO SOLVE OCCURRED.** ***The pre-compute claim is
> carried by the filesystem — the run root, checked — and by nothing a wrapper wrote about itself.***
> **A supervisor invoking `§2ax` records, in the amendment, the run root it checked and that it held
> no time directory beyond `0`.**

---

## Amendment — v1.70, 2026-09-06 — **§2ay THE COMPLETION-ENFORCEMENT CHECK: SANAA ORDERS "FIX UNTIL IT RUNS" MADE EXECUTABLE, "NOW AND GOING FORWARD." A STANDING INSTRUMENT ENUMERATES EVERY LANDED `GATE FAIL` / `NOT A RESULT` AND FLAGS ANY IN NEITHER ACCEPTABLE STATE. IT **FLAGS ONLY** — IT NEVER MOVES A VERDICT — AND IT CARRIES ITS OWN PLANT, BECAUSE AN ENFORCER THAT CANNOT SEE A VIOLATION IS §28's DISEASE APPLIED TO THE LAW ITSELF.**

**Appended 2026-09-06 by `verification-supervisor` on Sanaa's explicit order,
`etc/sessions/2026-09-06T2145Z_sanaa_enforce_fix_until_runs.md`, capture `19656f09`, her verbatim
*"yes so i want it to be enforced. Now and going forward."* `[CAPTURE READ BY ME AT SOURCE — rule 9.]`
This clause is the STANDARD; the instrument is built beside it and is diff-read by me before it is
believed (`SUPERVISION` §3 check 1). Landed in the CHARTER, not `CLAUDE.md` — whether any part touches
the constitution is hers.**

### §2ay.1 THE ROOT CAUSE SHE IS FIXING, STATED PLAINLY

**A written standard with no enforcing instrument behaves like a suggestion.** *"Fix until it runs"*
(the mandatory-completion orders of 2026-09-04, and `§2an`) had no standing check the way a freeze or
a gate does, **so it degraded to "fix when you get to it."** ***This is `§28`'s own repeated lesson —
an invariant with no executable enforcer is not an invariant — applied for the first time to a
DOCTRINE rather than to a comparator.*** **That application is exactly what makes the instrument
warranted under the governance posture: it changes whether the lab's own law is obeyed.**

### §2ay.2 THE CHECK

> **RULED — `§2ay`: A STANDING INSTRUMENT ENUMERATES EVERY LANDED `GATE FAIL` AND `NOT A RESULT`
> ACROSS ALL TEAMS AND FLAGS ANY THAT IS NOT IN ONE OF TWO ACCEPTABLE STATES:**
>
> **(a) PROVEN A GENUINE OpenFOAM CAPABILITY GAP** — unrecoverability **MEASURED and recorded**,
> with **each of bug / solver-selection / preconditioner / numerics-scheme / config / model-form
> EXPLICITLY RULED OUT** (`§2an`'s five process classes, plus model-form discharged via the closure
> ladder `§2an`), **and the gap FILED ON SANAA'S DESK.**
>
> **(b) CARRYING AN ACTIVE, DATED FIX-SUCCESSOR** — a registered next attempt (a successor
> registration or a closure-ladder rung) that **changes what failed and re-runs** — *or its terminal
> form:* **DISCHARGED by a landed passing successor whose lineage is recorded** (the failed row keeps
> its verdict per `§2an.2`; the successor's pass is the discharge).
>
> **Anything in NEITHER state is a STANDING VIOLATION, surfaced to the owning team and the chief.**

### §2ay.3 ⚠ "DIAGNOSED TO A MECHANISM" IS NOT "PROVEN UNRECOVERABLE", AND THE CHECK MUST REFUSE TO TREAT IT AS SUCH

**This is the clause most likely to be gamed and it is stated sharply.** **A fail annotated
*"diverges because of the k-omega wall treatment"* or *"the limiter is too diffusive"* is DIAGNOSED,
not DISPOSED.** ***A diagnosis names what failed; state (a) requires proof that what failed CANNOT be
recovered, and a diagnosis to a mechanism is usually the FIRST RUNG of state (b), not an entry to
state (a).***

> **State (a) is reachable ONLY when every one of the five process classes AND model-form has been
> ruled out AT SOURCE, the unrecoverability is MEASURED, and the filing is on her desk. A
> mechanism-diagnosis with no successor and no five-point rule-out is a VIOLATION, not a capability
> gap — and the check flags it as one.** *A model-form diagnosis in particular routes into the
> closure ladder, which is an active successor (state b), never a capability-gap filing (state a).*

### §2ay.4 THE BOUNDARIES — IT FLAGS, AND FLAGS ONLY

**Every boundary below is `§2at`'s and `§2an`'s law restated so the enforcer cannot become the thing
it enforces against:**

- **IT NEVER WIDENS A GATE, COMPOSES A VERDICT, OR CONVERTS A FAIL TO A PASS.** ***A fail clears in
  exactly two ways: a real fix that makes the case RUN to a passing gate, or a measured
  capability-gap filing. Never by the check's own action.*** The check's only output is a **flag**.
- **IT READS VERDICTS FROM RECORDS AND REGISTERS, NOT FROM BOARDS** — and **where a record and its
  board disagree, the ARTIFACT governs** (`§2al` and `§28.15`'s lesson: a board is a claim, the
  artifact is the measurement).
- **IT IS COMPUTE-PROTECTIVE AND COMPLETENESS-ENFORCING, NOT INSTRUMENT-MEASURING-INSTRUMENT** — it
  does not re-grade; it reads what is already graded and asks whether the fail is being worked.
- **INBOUND RESEARCH IS THE MANDATED FIX METHOD; OUTBOUND CONTACT STAYS PARKED (rule 7).** *A
  successor may draw on papers, docs, OpenFOAM issues; it may not file anything outside the box.*

### §2ay.5 ⚡⚡ THE CHECK CARRIES ITS OWN PLANT — BECAUSE AN ENFORCER THAT CANNOT SEE A VIOLATION IS THE EXACT DISEASE IT EXISTS TO CURE

**`§28.18`'s regress property applies with full force: this check is CODE, it adds surface, and the
surface it adds is of exactly the kind it detects.** ***An enforcement check that silently sees zero
violations is indistinguishable from one that cannot see violations at all — which is `§28`'s
founding failure, now one level up, at the enforcer of the law.***

> **MANDATORY, AND NOT OPTIONAL: the instrument carries a PLANTED CONTROL with TWO limbs, driven
> RED-then-GREEN, `§28.8`'s non-vacuity discipline applied to the enforcer itself:**
>
> **LIMB 1 — a fail with NO successor and NO gap-filing MUST be flagged. Plant one; confirm it is
> flagged.**
> **LIMB 2 — a properly-covered fail (state a or state b) MUST NOT be flagged. Plant one; confirm it
> is NOT flagged.**
>
> **A run reporting zero violations is believed ONLY when both limbs fired in the same run. A zero
> from a checker not shown able to see a non-zero is not evidence (rule 3), and this checker's zero
> is a claim about the lab's compliance — the highest-stakes zero it could print.**

### §2ay.6 FIRST DISCHARGE, AND WHAT IT IS NOT

**The check runs against the EXISTING backlog on its first pass and on every future fail thereafter
(*"now and going forward"*):** ansys's ~35-row set (whose per-case five-point rule-out sweep IS this
check's first discharge), the T-family `NOT A RESULT`s, and the closure / cfd / dafoam fails.

- **THE FIRST SCAN FLAGS; IT DOES NOT FIX.** *A flagged row is surfaced to its owning team, which
  then either registers a dated successor (state b) or drives the five-point rule-out to a filed
  capability gap (state a). The check does neither for them.*
- **A FLAG IS NOT A REBUKE.** ***It is a measurement that a fail is not yet being worked*** — and
  under a standing order to work every case, that measurement is the point. **A team with a large
  flagged set has a backlog, not a failing grade.**
- **THE CHECK'S OWN VERDICT VOCABULARY IS RULE 1's**: a flagged row is reported, never re-graded; the
  flag rides beside the verdict, it does not replace it.

### §2ay.7 WHAT IS LANDED HERE VERSUS WHAT FOLLOWS

**This clause is the STANDARD. The INSTRUMENT is built beside it, diff-read by me before its output
is believed, and its planted control must fire both limbs in the run that produces the first scan.**
**Until the instrument's plant is verified by me at source, its scan is a DRAFT and no team is held to
its flags.** ***An enforcement instrument believed before its own plant fired would be this clause
violating itself on its first use.***

## Amendment — v1.71, 2026-09-08 — **§2az THE CONVERGENCE-MONITOR STANDARD: STEADY-STATE CONVERGENCE IS JUDGED ON THE UNCORRECTED INITIAL RESIDUAL OF THE FIRST PRESSURE / MOMENTUM SOLVE AT THE FINAL OUTER ITERATION — NEVER ON A WITHIN-ITERATION CORRECTOR RESIDUAL. THE CORRECTOR RESIDUAL IS LINEAR-SOLVE TIGHTNESS, DRIVEABLE ARBITRARILY SMALL INDEPENDENT OF OUTER-LOOP CONVERGENCE, AND CANNOT ESTABLISH STEADY STATE; BINDING A GATE ON IT IS FIELD-SELECTION GATE-WIDENING (T25).**

**Appended 2026-09-08 by `verification-supervisor` on Sanaa's explicit authorization,
`etc/sessions/2026-09-08_sanaa_codify_convergence_standard_and_plain_english_status.md`, her verbatim
*"yes i do"* to the chief's offer to codify this principle as a general lab standard. `[CAPTURE READ
BY ME AT SOURCE — rule 9; a new standard is reserved to Sanaa, and this is her own word.]` This clause
GENERALIZES verification's A2 accept-floor ruling (`a2978688`, V-128,
`verification/campaign/A2_ACCEPT_FLOOR_BINDING_FIELD_RULING_2026-09-08.md`) from an n=1 application of
existing law into a NAMED general standard, so future registrations and audits cite `§2az` directly
rather than re-deriving it each time. Landed in the CHARTER, not `CLAUDE.md` — whether the
constitution absorbs it is hers.**

**LINES WHOSE NUMBER CHANGED ABOVE THIS SECTION: 0.** This clause is appended at the foot and nothing
above it is edited (rule 6); the base header on line 3 is not bumped, matching the v1.67–v1.70
foot-only amendment pattern.

### §2az.1 THE STANDARD

> **RULED — `§2az`: for a STEADY (SIMPLE / pseudo-transient segregated pressure-based) solve,
> iterative convergence under rule 5 order (1) and any `residualControl` gate is judged on the
> INITIAL residual of the FIRST, UNCORRECTED solve of each governing equation at the FINAL outer
> iteration** — the quantity the solver prints as that equation's initial residual per outer
> iteration (the pressure equation's first-corrector initial residual; the `Ux` / `Uy` / `Uz`
> initial residuals). **This is the residual of the field BEFORE that outer iteration's correction
> is applied; driving it below the floor is what demonstrates the field has stopped changing between
> outer iterations — i.e. that a steady state has been reached.**
>
> **A LATER, WITHIN-ITERATION CORRECTOR RESIDUAL IS NOT A STEADY-STATE MONITOR AND A GATE MAY NOT BE
> BOUND ON IT.** The final residual after the last pressure corrector, or the residual of a second /
> non-orthogonal corrector, measures LINEAR-SOLVE TIGHTNESS — how well the linear system was solved
> in THIS iteration — not outer-loop convergence. It is driveable arbitrarily small (tighter linear
> tolerance, more correctors) INDEPENDENT of whether the outer loop has converged, so it CANNOT
> establish that the solution has stopped changing.
>
> **`residualControl` is a FLOOR (necessary), NEVER a sufficiency**, and the monitor field is fixed
> by physics — the uncorrected initial residual — not chosen per outcome.

### §2az.2 THE ANTI-GAMING RULE — FIELD SELECTION IS GATE-WIDENING

Where a case reports MORE THAN ONE residual per field (a first / uncorrected residual that fails and
a corrected residual that passes), **selecting the corrected residual BECAUSE it passes is
gate-widening by FIELD SELECTION** — the rule 2 / `§2` prohibition, named **T25** in the A2 ruling.
The prohibited act and the permitted act look identical in the printed output; what distinguishes
them is that the monitor field is **fixed before the answer is known** and is **the uncorrected
initial residual by physics**, not the field that happens to clear the floor. A registration that
binds convergence on a corrector residual is REFUSED on the same ground as any other post-hoc gate
change, and a `§2d.1` repair may not be used to re-designate the criterion.

### §2az.3 SCOPE, AND WHAT IT DOES NOT MOVE

- **General, not n=1.** `§2az` applies to EVERY steady-solve convergence gate lab-wide — A2 / D6RF
  was its first application, not its boundary.
- **Consistent with existing law, so it moves NO verdict.** It names how rule 5 order (1)
  (*"iteratively converged"*) and N-family `§1` (convergence judged on the equation's own initial
  residual read from the solver log) were always to be read; it does NOT re-grade any landed row. It
  binds future registrations, cross-team gate audits, and the fix-until-runs successors owed under
  `§2an` and the 2026-09-04 mandatory-completion orders.
- **The consequence already on record.** dafoam's A2 D6RF `GATE FAIL` STANDS, and its owed numerics
  successor must drive the UNCORRECTED pressure initial residual below the frozen floor with the
  gate, threshold, floor and label UNMOVED — it does not pass by re-designating the criterion (V-128,
  `a2978688`).
- **Transient solves are out of scope.** This is a steady-state / outer-loop convergence standard; a
  time-accurate run's convergence is judged on its own per-timestep criteria, not addressed here.

## Amendment — v1.72, 2026-09-09 — **§2ba THE DUAL-MECHANISM RUN STANDARD: MONITOR + DETACHED GRADER. EVERY RUN MUST BE LAUNCHED WITH BOTH TOGETHER — A LIVE MONITOR LANE THAT WATCHES AND REPORTS WHILE THE FLEET IS ALIVE AND SANAA IS ONLINE, AND A DETACHED GRADER/SCHEDULER (setsid ORPHANED TO init IN ITS OWN SESSION, OR THE QUEUE DAEMON / at / cron) THAT CARRIES THE RUN TO COMPLETION AND GRADES IT AGAINST THE FROZEN COMPARATOR WITH NO LIVE AGENT. NEITHER SUBSTITUTES FOR THE OTHER; A RUN LAUNCHED WITH ONLY ONE IS NON-COMPLIANT.**

**Appended 2026-09-09 by `verification-supervisor` on Sanaa's own directive, relayed verbatim by the
chief this session. Sanaa, verbatim: *"in general every run must have both: monitor AND detached
autograder/ scheduler etc that way when i am online the monitoring agent monitors and when offline
everything stil runs on the box."* `[A new lab standard is reserved to Sanaa (rule 9 / FIRST-ACTION
RULE), and this is her own word. Provenance is her directive of 2026-09-09, captured
verbatim at `etc/sessions/2026-09-09_sanaa_dual_mechanism_run_standard.md` (landed this session to
match the `§2az` precedent).]` Landed in the CHARTER, not `CLAUDE.md` — whether the constitution absorbs it is hers.**

**LINES WHOSE NUMBER CHANGED ABOVE THIS SECTION: 0.** This clause is appended at the foot and nothing
above it is edited (rule 6); the base header on line 3 is not bumped, matching the v1.67–v1.71
foot-only amendment pattern.

### §2ba.1 THE STANDARD

> **RULED — `§2ba`: EVERY run — a graded solve, a curriculum item, any compute whose product is a
> verdict or a measured number — MUST be launched with BOTH of the following, together, at launch:**
>
> 1. **A LIVE MONITOR.** A monitor lane (or equivalent live agent) that watches the run — progress,
>    residuals, iteration/ETA, stalls, crashes — and reports upward WHILE a fleet is alive and Sanaa
>    is online. This is the online-observability half: it exists so that while someone is watching,
>    the run is watched, triaged and reported in real time.
>
> 2. **A DETACHED GRADER / SCHEDULER.** A process orphaned to `init` — a `setsid` session of its own,
>    the queue daemon (`scripts/queue_runner.py --daemon`), or an `at` / `cron` job — that carries the
>    run to completion AND grades it against the FROZEN comparator, WRITING THE VERDICT TO DISK WITH
>    NO LIVE AGENT REQUIRED. This is the offline-survival half: it exists so that when the fleet dies,
>    a session-limit kill lands, or Sanaa is offline, the run still completes and still produces its
>    verdict on the box, unattended.

### §2ba.2 NEITHER SUBSTITUTES FOR THE OTHER — A RUN WITH ONLY ONE IS NON-COMPLIANT

The two mechanisms cover DIFFERENT failure modes and one cannot stand in for the other:

- **A monitor without a detached grader dies with its agent.** A watcher spawned inside a lane or
  session is killed the instant the fleet dies or the session limit expires — *"agent watchers die
  with the agent"* (memory note; and `L-239`: a record-only watcher that names no process able to
  execute the run is a preference, not a control). It leaves a live run orphaned with no one to grade
  it, or worse, a run that never reaches completion.
- **A detached grader without a monitor runs blind.** A daemon-only run completes and grades, but a
  stall, a divergence, a wrong-turn or a crash goes untriaged for as long as no agent looks — burning
  core-minutes on a run no one is reading (idle-attention is a cousin of the idle-compute failure).
  The live monitor is what makes a problem visible while it can still be acted on.

A run launched with only ONE of the two is **NON-COMPLIANT** with `§2ba` and is to be flagged the same
way any other pre-registration/launch-discipline defect is flagged — a cross-team gate audit records
it, and the owning team re-launches compliantly. This binds all six teams henceforth.

### §2ba.3 WHAT THE DETACHED HALF MUST SATISFY (carried forward from existing law, not new)

The detached grader/scheduler is subject to the practices already on record; `§2ba` names them as
mandatory-together, it does not relax any:

- **Detached means orphaned to `init`, launched through `setsid` (or a container / the queue daemon),
  never as a foreground call** — a foreground solve has been SIGTERM-killed by an external signal with
  no error and no OOM while a detached one has not (`ESCALATION_CHARTER` §disconnect-safety practice,
  the "solver runs detached and ledgers itself as it goes" clause).
- **The queue daemon is an OS daemon independent of any agent** — the detached-queue-runner ruling
  (Sanaa 2026-08-26; memory note *detached-queue-runner-ruling*, `LESSONS` L-context at
  `docs/LESSONS.md:14983`): dropping the queue JSON IS the launch and it survives fleet death.
- **`rc` is captured INSIDE the detached wrapper, never around the `setsid` line** — `setsid timeout
  cmd` exits 0 for every outcome (memory note *setsid parent returns zero*; `L-382` private-index CAS
  trap is a cousin). The verdict written to disk must be a real grade, not a manufactured `rc=0`.
- **`STATUS.<case>` is the ONLY completion evidence when no agent is watching, so it IS rule 4's
  `rc = 0` limb** — a launcher that manufactures complete-on-disk-but-ungradeable cases at machine
  speed under a detached queue is the standing hazard (`LAB_STATE` K0d finding); the frozen comparator
  the detached grader runs must refuse (exit 2) rather than degrade (rule 4; rule 5).
- **The verdict is graded against the FROZEN comparator, sha-pinned at the pre-registration commit**
  (rule 2) — the detached grader does not choose or alter the grading path.

### §2ba.4 SCOPE, AND WHAT IT DOES NOT MOVE

- **General, binding all six teams, from now forward.** `§2ba` is a launch-discipline standard; it
  applies to every run whose product is a verdict or a measured number. It does NOT re-grade any
  landed row and moves NO verdict — it is an operational requirement on how runs are LAUNCHED, not on
  how their results are judged.
- **It generalizes what already worked this session.** The M6 fork-A / physics-hold work and the
  cooling-rung work survived precisely because a detached mechanism carried them past agent death; the
  standard makes the pairing that saved them mandatory rather than incidental.
- **Development/smoke compute that produces no verdict** (ungraded method-validation smokes, §11-style
  diagnostics) is not a "run" in this sense — it reads no gate and writes no verdict, so the
  monitor+grader pairing is not required of it; but the moment compute is intended to produce a graded
  result, `§2ba` binds.
- **Enforcement is by flag, not by moving a verdict** — consistent with `§2ay`'s flags-only boundary.
  A non-compliant launch is a defect of process; the run's verdict, once produced, is judged on its
  own merits under rules 2–5.


## Amendment — v1.73, 2026-09-09 — **§2bb THE PER-RUNG / PER-CONFIGURATION PRE-FLIGHT VALIDATION STANDARD: BEFORE A MULTI-RUNG OR MULTI-CONFIGURATION LADDER MAY BE FROZEN, EACH RUNG/CONFIG MUST PASS A PRE-FLIGHT SMOKE THAT VALIDATES, ON THE ACTUAL ARTIFACT, (1) ITS OWN DEADLINE SIZING AND (2) ITS OWN DISTINCT SOLVER/DECOMPOSITION PATH END-TO-END. A LADDER THAT HAS NOT PASSED THE PRE-FLIGHT FOR EVERY RUNG CANNOT BE FROZEN OR LAUNCHED — THE ENFORCEMENT CHECK REFUSES (check-4-adjacent).**

*Provenance: Sanaa, online 2026-09-09, in her own words, relayed verbatim by the chief; a new lab-wide enforced standard is reserved to Sanaa (CLAUDE.md rule 9 / FIRST-ACTION RULE). Her directive is captured at `etc/sessions/2026-09-09_sanaa_per_rung_preflight_standard.md`. Earned by the D6RF9 confound: a four-rung ladder was frozen and run, then 3 of 4 rungs came back CONFOUNDED — R2 timed out incomplete because its heavier config's per-step cost was never measured against its frozen deadline (rule 4 last-time ≠ endTime), and R3/R4 crashed rc=59 on a latent decompose collision that R1's path never exercised. The pre-flight verified the grading path and that R1 reached the solver, but NOT each rung's own config. `L-511`. Enforced by `scripts/check_ladder_preflight.py`.*

### §2bb.1 THE STANDARD

> **RULED — `§2bb`: A multi-rung or multi-configuration ladder — and any run whose configuration
> differs MATERIALLY from a prior VALIDATED one (a different solver, decomposition, corrector count,
> scheme, endTime/deadline, or mesh family) — may NOT be FROZEN or LAUNCHED until EACH rung /
> configuration in it has passed a PRE-FLIGHT SMOKE that validates, ON THE ACTUAL ARTIFACT THAT RUNG
> WILL RUN, both of the two things below. A rung that inherits a config BYTE-IDENTICAL to another
> rung already pre-flighted this ladder inherits its pre-flight; a rung whose config differs
> materially does not. The enforcement check `scripts/check_ladder_preflight.py` GATES the freeze:
> it REFUSES (exit 2) any ladder whose pre-flight manifest does not show every rung passing both
> validations and every DISTINCT solver/decomposition path covered by a passing smoke.**

"Materially different" is decided by the DISTINCT-PATH KEY defined in §2bb.3, plus the deadline/endTime
and the corrector/scheme fields: two rungs are the same config only if their path key AND their
per-step-cost-determining fields match. When in doubt, a rung is materially different and owes its own
pre-flight — the standard fails safe toward MORE pre-flighting, never less.

### §2bb.2 THE TWO VALIDATIONS, ON THE ACTUAL ARTIFACT

Each rung's pre-flight smoke must establish, from the config it will actually run (not a sibling's, not
a paper assertion):

1. **DEADLINE SIZING — the wall-clock deadline is sized to THIS rung's own per-step cost.** A short
   measured sample of the rung's own per-step wall time (a minimum of `MIN_STEPS_SAMPLED` real solver
   steps), projected to the rung's endTime, must fit inside the rung's frozen wall-clock deadline with
   margin. A heavier configuration — more correctors, a finer scheme, SIMPLEC's coupling — must not be
   allowed to silently time out incomplete under a deadline copied from a lighter rung. The projected
   wall is RECOMPUTED by the check from `measured_per_step_wall_s × steps_to_endTime`; a hand-typed
   projection that does not match the sample is a fabrication and REFUSES. `projected_wall_s` must be
   `≤ deadline_s`, and the check requires a safety margin (`deadline_s ≥ projected_wall_s × SAFETY`,
   `SAFETY = 1.25`) so a rung near its deadline is caught before, not during, the frozen run. This is
   the R2-timeout class.

2. **SOLVER-PATH EXECUTION — each DISTINCT solver/decomposition path is exercised END-TO-END, not only
   the first rung.** The rung's own solver and decomposition are run far enough to clear the failure
   modes that a first-rung-only pre-flight never touches: decomposition (`decomposePar` must not hit an
   "already decomposed" collision from carried processor* directories), staging, and the first solver
   iterations of that scheme (the smoke must REACH the first solve, `rc = 0`, no scheme crash / SIGFPE).
   EVERY distinct (solver, decomposition-method, nprocs) path in the ladder must be covered by at least
   one passing smoke — not only R1's. This is the R3/R4 decompose-collision / SIMPLEC-crash class.

Neither validation substitutes for the other: a rung can decompose-and-run cleanly yet be under-budgeted
(R2), and a rung can be well-budgeted yet crash on an unexercised path (R3/R4). Both, on the actual
artifact, for every rung, before the freeze.

### §2bb.3 THE PRE-FLIGHT MANIFEST AND THE ENFORCEMENT CHECK

The pre-flight evidence is recorded in a machine-readable manifest committed WITH the freeze (beside the
pre-registration; conventionally `LADDER_PREFLIGHT.json` in the ladder's case directory). Its schema —
which `scripts/check_ladder_preflight.py` validates — is:

    {
      "ladder_id": "<id>",
      "rungs": [
        {
          "rung": "R2",
          "solver": "DARhoSimpleFoam",
          "decomposition": {"method": "scotch", "nprocs": 4},
          "endTime": 2000,
          "deadline_s": 855,
          "preflight_smoke_log": "<path on disk that MUST exist>",
          "deadline_sizing": {
            "measured_per_step_wall_s": <float>,
            "n_steps_sampled": <int ≥ MIN_STEPS_SAMPLED>,
            "steps_to_endTime": <int>,
            "projected_wall_s": <float = measured_per_step_wall_s × steps_to_endTime>
          },
          "solver_path": {
            "rc": 0,
            "reached_first_solve": true,
            "decompose_ok": true
          }
        }
      ]
    }

The check enforces, and REFUSES (exit 2) otherwise: every rung carries both sub-objects; `n_steps_sampled
≥ MIN_STEPS_SAMPLED` (= 5); `projected_wall_s` equals `measured_per_step_wall_s × steps_to_endTime` within
tolerance (no fabricated projection); `deadline_s ≥ projected_wall_s × SAFETY`; `preflight_smoke_log`
EXISTS on disk (a paper manifest citing no artifact is refused); `solver_path.rc == 0`,
`reached_first_solve` and `decompose_ok` both true; and EVERY distinct path key
`"<solver>|<method>|<nprocs>"` present among the rungs is covered by at least one rung whose `solver_path`
passed. The distinct-path-key device lets a rung INHERIT a byte-identical sibling's smoke (§2bb.1) while
still forcing every path to be smoked at least once.

The manifest's NUMBERS must be derived from the cited smoke log by the team's own tooling under the
standing planted-zero control (rule 3): the smoke's per-step sample is READ from the log, not asserted,
and the smoke is a real run of that rung's config. The check enforces STRUCTURE, ARITHMETIC and ARTIFACT
EXISTENCE; the standard mandates PROVENANCE. `check_ladder_preflight.py` carries its own two-limb plant
(`--selftest`): a compliant manifest PASSES (exit 0) and each defect class — undersized deadline, a
crashed/uncovered solver path, a missing pre-flight, a fabricated projection, a non-existent smoke log —
REFUSES (exit 2), each RED arm shown load-bearing.

### §2bb.4 SCOPE, AND WHAT IT DOES NOT MOVE

- **General, binding all six teams, from now forward.** `§2bb` is a FREEZE-DISCIPLINE / launch-discipline
  standard (check-4-adjacent: a supervisor's non-delegable freeze check). It gates whether a ladder may be
  FROZEN and LAUNCHED; it does NOT re-grade any landed row and moves NO verdict — consistent with `§2ay`'s
  and `§2ba`'s flags-only boundary. A non-compliant ladder is a defect of process, refused at the freeze.
- **A single-configuration run against an already-validated config is out of scope.** The standard triggers
  on a ladder of ≥ 2 configs, or a run whose config differs materially from a prior VALIDATED one. A rerun
  of a byte-identical, already-pre-flighted config does not owe a fresh pre-flight.
- **Development/smoke compute that produces no verdict is out of scope** (as under `§2ba.4`) — but note the
  pre-flight smoke IS the sanctioned mechanism by which a rung earns its freeze, so a ladder's pre-flight
  smokes are expected, not incidental.
- **It composes with `§2ba` and rule 2.** The pre-flight is done BEFORE the freeze; the freeze pins the
  grading path (rule 2); the frozen run is then launched with BOTH a monitor and a detached grader (`§2ba`).
  A rung's deadline validated here is the same deadline the detached grader will hold it to.
- **The pre-flight demonstration for the endTime/deadline lever specifically is a measured PLATEAU of the
  rung's own binding field to the shortened window** — a shortened endTime is verdict-preserving only if
  the binding field is measured flat by the new endTime on the rung's OWN config (this is where the
  deadline-sizing validation and the verdict-preservation test meet; see the D6RF10 B-300 ruling).

**lines whose number changed above this section: 0**


## Amendment — v1.74, 2026-09-09 — **§2bc THE EXHAUSTION-EVIDENCE ACCEPTANCE GATE FOR A TERMINAL `GATE FAIL` / `NOT A RESULT` (STRENGTHENS §2ay). A `GATE FAIL` OR `NOT A RESULT` IS NOT AN ACCEPTABLE TERMINAL ENTRY UNLESS IT CARRIES EXHAUSTION EVIDENCE PROVING THE FAILURE IS NOT A FIXABLE NUMERICS OR MODEL/SETUP ARTIFACT. WITHOUT IT THE VERDICT IS PREMATURE, REJECTED, AND ROUTED TO A DATED SUCCESSOR.**

*Provenance: Sanaa, online 2026-09-09, in her own words, relayed verbatim by the chief; a new lab-wide standard is reserved to Sanaa (CLAUDE.md rule 9 / FIRST-ACTION RULE). Her directive is captured at `etc/sessions/2026-09-09_sanaa_exhaustion_evidence_acceptance_gate.md`. This is the substantive ACCEPTANCE CRITERION behind `§2ay`'s state-(a): `§2ay` flags a fail in neither an acceptable-terminal state nor an active-successor state; `§2bc` defines what makes the terminal state ACCEPTABLE. Enforced by `scripts/check_exhaustion_evidence.py`; the `§2ay` fleet sweep (`scripts/check_completion_enforcement.py`) locates the fails, `§2bc`'s check validates each terminal one's evidence.*

### §2bc.1 THE STANDARD

> **RULED — `§2bc` (Sanaa's words):** *"per our rule, gate fail/ not a result are only valid entries
> if we have exhausted that its a numerics or model issue and that genuinly openfoam cant run it.
> Else not acceptable."* A `GATE FAIL` or `NOT A RESULT` recorded as a TERMINAL entry (a final verdict,
> NOT one already routed to an active dated successor under `§2ay` state-(b) / fix-until-runs) is an
> ACCEPTABLE entry ONLY if it carries EXHAUSTION EVIDENCE proving the failure is not a fixable numerics
> or model/setup artifact. An un-evidenced terminal fail is PREMATURE → **REJECTED** → routed to a
> dated successor (fix-until-runs). The gate is *"prove it isn't a fixable numerics/setup artifact,"*
> NOT *"never report a fail."*

### §2bc.2 THE THREE EXHAUSTION COMPONENTS

A terminal fail's exhaustion evidence must establish all that apply to it:

1. **NUMERICS EXHAUSTED** — the fix-until-runs numerics ladder driven to its END (scheme, limiter,
   relaxation, timestep, grid), not a single attempt. A reference to the numerics-ladder record whose
   levers are recorded exhausted.
2. **MODEL / SETUP RULED OUT** — boundary conditions, solver choice, staging/config, decomposition and
   the like eliminated as the cause. A reference to the rule-out record.
3. **CAPABILITY LIMIT PROVEN BY MEASUREMENT** — for a NON-COMPLETING run, the five-process-class
   "OpenFOAM genuinely can't run it" rule-out, MEASURED (not inferred). A reference to that rule-out.

Component 3 applies to a run that will not complete; components 1–2 apply to a run that completes but
fails its gate. A single attempt, a mechanism DIAGNOSIS without a driven ladder, or a bare assertion
("it's a geometry problem") is NOT exhaustion evidence — the M6 line is the worked example: a
premature "geometry/BC" conclusion was correctly overturned when the numerics ladder was actually run
(board-87 → board-89; V-134).

### §2bc.3 THE TERMINAL EXEMPTIONS (so a team does not loop forever)

A terminal fail is ACCEPTABLE — needs no further successor — in exactly these cases:

- **(E1) A MEASURED CAPABILITY LIMIT** — the five-process-class rule-out is COMPLETE and measured; the
  case genuinely cannot run in OpenFOAM. This is `§2ay` state-(a) proper, and it goes to Sanaa's desk
  as a capability-gap filing.
- **(E2) A GENUINE MODEL-ACCURACY MISS ON THE CLOSURE-CHALLENGE LINE** — for the line whose PRODUCT
  IS measuring model error, a real model-accuracy miss WITH THE NUMERICS ALREADY EXHAUSTED is a
  legitimate terminal result (the miss is the measurement; §2an: the closure ladder moves the MODEL
  against a fixed gate). Numerics-exhausted evidence is still required; the model miss is the finding.

**⚠ BOUNDARY PENDING SANAA'S CONFIRM.** The chief has asked Sanaa to confirm that these two exemptions
are the complete terminal set (the gate is "prove it isn't a fixable numerics/setup artifact," not
"never report a fail"). `§2bc` operates on this boundary now; if Sanaa narrows or widens it, her words
supersede this clause by dated addendum.

### §2bc.4 THE EXHAUSTION-EVIDENCE FIELD (what a terminal record must carry) AND ITS ENFORCEMENT

A terminal `GATE FAIL` / `NOT A RESULT` record must carry a machine-readable `exhaustion_evidence`
block; `scripts/check_exhaustion_evidence.py` REFUSES (exit 2) a terminal fail that lacks a valid one.
Schema:

    "exhaustion_evidence": {
      "verdict": "GATE FAIL" | "NOT A RESULT",
      "terminal": true,
      "completes": true | false,          # false => component 3 (capability rule-out) required
      "numerics_ladder_exhausted": "<path/commit ref to the driven numerics ladder>",
      "model_setup_ruled_out": "<path/commit ref to the BC/solver/staging/decomposition rule-out>",
      "capability_rule_out": "<path/commit ref to the measured five-process-class rule-out>",  # if !completes
      "terminal_exemption": null | "measured_capability_limit" | "closure_challenge_model_accuracy_miss",
      "exemption_ref": "<ref>"            # required iff terminal_exemption is set
    }

The check REFUSES a terminal fail unless EITHER (a) a `terminal_exemption` is declared with a resolving
`exemption_ref` (E1 requires the capability rule-out; E2 requires numerics-exhausted), OR (b) the
applicable components are present with REFS THAT RESOLVE ON DISK (a paper ref citing nothing is
refused, mirroring `§2bb`'s smoke-log-must-exist). A fail in `§2ay` state-(b) (an active dated
successor) is NOT terminal and is out of scope until it is claimed final. The check carries its own
two-limb plant (`--selftest`): an un-evidenced terminal fail REFUSES; a fully-evidenced or
exemption-declared one PASSES; each RED arm shown load-bearing.

### §2bc.5 SCOPE, AND WHAT IT DOES NOT MOVE

- **General, binding all six teams, from now forward.** `§2bc` is a verdict-ACCEPTANCE standard folded
  into `§2ay`; it does NOT re-grade a landed number and moves NO verdict — it decides whether a
  `GATE FAIL` / `NOT A RESULT` may STAND as terminal or must be routed to a successor. Flags-only /
  refuse-at-record, consistent with the `§2ay`/`§2ba`/`§2bb` boundary.
- **It sharpens `§2ay` state-(a), it does not replace `§2ay`.** `§2ay` enumerates fails and asks
  "covered (a/b) or flagged?"; `§2bc` asks "for a fail claimed terminal, is its exhaustion evidence
  actually present and resolving?" A terminal fail that clears `§2ay` state-(a) but carries no valid
  exhaustion evidence is now `§2bc`-REJECTED.
- **It composes with the non-convergence standard and `§2an`.** Sanaa's mandatory-completion order and
  its OpenFOAM-can't-run-it exemption (the non-convergence standard §4) are the E1 case; `§2an`'s
  closure-ladder routing is the E2 case; `§2bb`'s pre-flight prevents the R2/R3/R4-class process
  failures from ever masquerading as terminal fails in the first place.

**lines whose number changed above this section: 0**

---

## Amendment — v1.75, 2026-09-10 — **§2bd THE PLATEAU LIMB: A TWO-POINT DIFFERENCE MAY NOT MEASURE IT, AND THIS CLOSES A GAP IN THIS TEAM'S OWN RULING SIX HOURS OLD. §2be THE FREEZE/CORRECTNESS GAP: A FREEZE PROVES A FILE UNCHANGED AND CANNOT PROVE IT CORRECT**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **cfd** from two defects they found and personally verified in a **PINNED, FROZEN comparator that had already passed a freeze and produced a verdict**; both re-verified at source by this supervisor before adoption. `[lab-attributed]`; on Sanaa's desk to overrule. **No gate, threshold, cap, band or label is moved and no verdict is withdrawn.**

---

### §2bd — THE PLATEAU LIMB OF RULE 5 CLAUSE (1)

Standing rule 5 clause (1) gates on *"any level not iteratively converged **or not plateaued**"*. The **level** half has a standard (`§2az`). **The plateau half had none, and it is now load-bearing**, because this team ruled six hours ago (`D596`) that where the residual-level limb is spent, **the plateau limb is the admissible one**.

> **A PLATEAU IS MEASURED OVER A TRAILING WINDOW OF THE RUN'S OWN HISTORY, DECLARED IN THE REGISTRATION BEFORE THE RUN. A TWO-POINT DIFFERENCE BETWEEN THE LAST TWO WRITES IS NOT A PLATEAU TEST AND MAY NOT BE GATED ON.**
>
> The registration states **(i)** the window — a fraction of the run or a count of writes, never "the last two"; **(ii)** the statistic over that window — spread, drift, or max deviation from the window mean; **(iii)** the tolerance. **A monotone drift is the failure mode the window exists to catch**, so a statistic that cannot distinguish drift from noise (any statistic reading only the endpoints) does not satisfy this clause.

**THE INSTANCE THAT EARNED IT, measured and not argued.** `cases/navier_class/SUBOFF/grade_suboff.py:368`, verbatim, read at source by this supervisor:

```python
plateaued = abs(ct_series[-1] - ct_series[-2]) <= PLATEAU_TOL_REL * abs(ct) if ct else False
```

It compares **the last two writes and nothing else**, so a steady drift with small per-write steps passes. **It flagged two levels `PLATEAUED` whose coefficients were, over their final 100 writes, falling 10.02 % and rising 5.71 %.** A false `PLATEAUED` is a **false green on a rule-5 clause-1 gate**, and rule 5 permits the gate to turn a `PASS` into `NOT A RESULT` but **never the reverse** — so a false plateau does not merely mis-report, it **manufactures admissibility**.

**AND IT IS RECORDED AGAINST THIS TEAM'S OWN RULING, WHICH IS WHY IT IS URGENT.** `D596` §7 ruled the plateau limb admissible for `A2-GC-P`'s `GATE R`. Its worked example was a trailing-window measure — *"flat to six significant figures over its last 200+ of 1,000 iterations, last-20 % relative spread `7.5e-09`"* — **but the ruling never said a two-point test was inadmissible.** A registration could have satisfied `D596` literally with `abs(r[-1] - r[-2]) <= tol` and reproduced `grade_suboff.py`'s defect exactly, **with this team's ruling as its authority.** The gap is closed here, before the registration that would have walked into it.

### §2bd.1 — A MESH COUNT READ FROM `polyMesh/owner` IS `nFaces`, NOT `nCells`, AND IT REACHES `r` AND THEREFORE `GCI`

Same file, `:369`: `ncells = len(parse_owner(case))`. **OpenFOAM's `constant/polyMesh/owner` holds one entry per FACE** — `owner[i]` is the cell owning face `i` — so the length is `nFaces`. Verified at source: `parse_owner` (`:124-135`) parses that list and returns it unmodified. **Measured 4.01× wrong**, and it feeds the refinement ratio: the true cell ratios are exactly **2.250000**, giving **r = 1.5000000**; the face ratios give **1.4994 / 1.4996** and trip a **spurious unequal-ratio branch**.

> **A cell count used in a refinement ratio is read from a source that counts CELLS, and the registration names that source.** `nFaces`, `nPoints` and the length of any face-indexed list are not cell counts. Where `r` is derived rather than registered, the derivation and its source are stated, because **`r` propagates into the observed order and into every GCI this charter's §3 admits.**

### §2be — THE FREEZE/CORRECTNESS GAP, STATED SO NOBODY READS A FREEZE AS MORE THAN IT IS

**Neither defect above was caught by a freeze, by a planted-zero control, or by a selftest**, and the file was correctly pinned throughout. cfd's formulation is adopted verbatim because it cannot be improved on:

> **The freeze proved the file was unchanged; it could not prove the file was correct.**

**§2d's freeze and standing rule 3's planted-zero control are ORTHOGONAL to correctness and were never claimed otherwise — but the lab has been reading a clean freeze as a broader assurance than it is.** A freeze answers *is the file that ran the file that was registered*. It is silent on whether that file computes what its registration says. **Nothing in this charter licenses "it passed the freeze check" as evidence about a comparator's arithmetic.**

**Three consequences, and they are requirements on a freeze hook rather than on a freeze:**

1. **THE GRADING PATH INCLUDES THE INVOCATION, NOT ONLY THE BLOBS.** cfd's `R1b` failure is the case: `run_suboff_r1b_triple.sh:369` invoked the correctly-pinned grader **while omitting `--reference`**; the grader correctly refused and the rung produced **no graded number**. Every blob was pinned and correct; **the invocation was pinned nowhere.** **A pinned comparator invoked wrongly is an unpinned grading path**, and a registration that pins comparator bytes without pinning the argv that drives them has frozen half its instrument.
2. **A PIN'S LAST COMMIT MUST BE AN ANCESTOR OF THE FREEZE COMMIT.** This is rule 2 made checkable on the git record rather than asserted in prose — the property that makes "frozen before the run" a fact about the commit graph. cfd verified it by hand for SUBOFF (`58595cb2` is an ancestor of `f67bbe14`); a hand-verified ancestry is one a supervisor will eventually get wrong.
3. **A CONDITIONALLY ARMED CHECK IS NOT AN ARMED CHECK.** `grade_suboff.py`'s `Aref` comparison sits behind a data-dependent condition, so **with a null reference it is skipped silently and the grader still returns a verdict.** It was armed only because a non-null value happened to be pinned. **A freeze that cannot see a guard whose arming condition is DATA certifies a sleeping check**, and the registration must therefore state which guards are unconditional and which are armed by a pinned value — the pinned value then being part of the guard, not part of the input.

### §2be.1 — THE SHAPE PLANTING CANNOT CATCH, AND IT IS WORTH MORE THAN ANOTHER PLANTED ZERO

cfd found, in `cases/navier_class/watch_grade_calibrate.py`, the string `"waste named separately: 0.00 core-min (every level returned rc=0)"` **HARD-CODED** — asserted unconditionally, whatever the reader found.

> **A LITERAL CLAIM-STRING IN A REPORTING PATH CANNOT BE FALSIFIED BY ANY INPUT, SO NO PERTURBATION DETECTS IT. ONLY READING THE SOURCE DOES.**

This is `§2a`'s identity test reaching the **report** rather than the gate: a hard-coded finding is a green light wired to nothing, and it is invisible to the entire planted-control apparatus this lab has built. **It is named here as a distinct detector class** — a reporting path that emits a measurement-shaped sentence which no input can change — and it is the reason `SUPERVISION_CHARTER` §3 check-1 requires a supervisor to read a measurement script **as a diff** rather than to run its selftest.

| amendment record | **v1.75** |
|---|---|
| clauses added | **2** (§2bd with §2bd.1; §2be with §2be.1) |
| existing clauses altered, widened or narrowed | **0** |
| gate values changed | **0** |
| verdicts withdrawn | **0** |
| executable checks made to refuse | **0** (`D539`) |
| measured instances behind these clauses | **3**, all in files pinned and frozen at the time (`grade_suboff.py:368`, `:369`; `watch_grade_calibrate.py`'s hard-coded claim) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.76, 2026-09-10 — **§2bf ADVISORY DECAY: `D539` SYSTEMATICALLY MANUFACTURES WARNINGS, A WARNING WITH NO CENSUS BECOMES WALLPAPER, AND THE CENSUS THAT WOULD FIX IT TURNS OUT NOT TO BE COMPUTABLE — WHICH IS THE SAME DEFECT IT WOULD MEASURE**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **cfd**, as a risk against this team's own `D608` ruling rather than as an objection to it. `[lab-attributed]`; on Sanaa's desk to overrule. **No gate, threshold, cap, band or label moves; no executable check is made to refuse (`D539`).**

### §2bf.1 THE RISK, AND IT IS AGAINST A RULING THIS TEAM MADE HOURS AGO

`D608` ruled that a pin the frozen checker cannot see **WARNS** rather than refuses, because refusing would stop 45 registrations for a defect on Sanaa's desk that no case author can fix from their own files. **That ruling stands.** cfd's risk against it:

> **A WARN that persists across many runs stops being read.** *"The failure mode of a good warning is that it becomes wallpaper."*

**And the risk is structural rather than incidental, which is the part worth a clause.** `D539` reserves arming a gate to Sanaa, so **every check this lab builds between a defect's discovery and her ruling is necessarily ADVISORY.** `D539` is correct and is not disturbed here — but its **cost has never been named: it systematically manufactures a growing population of warnings, and nothing measures whether any of them is still read.** A lab that cannot arm gates accumulates advisories the way a lab that cannot delete accumulates files.

### §2bf.2 THE CLAUSE

> **AN ADVISORY CHECK CARRIES A POPULATION COUNT, AND THAT COUNT APPEARS IN A PERIODIC REPORT. AN ADVISORY WITH NO CENSUS IS NOT A WARNING; IT IS A LINE OF OUTPUT.**
>
> The count is of the **population the advisory is currently firing over**, published on the same cadence as the team's own reporting. **A warning whose population is published cannot go quiet by being ignored; one whose population is never counted goes quiet by default and no one observes the moment it does.**

This is `§2c`'s discipline turned on the reporting layer rather than the grading layer: a check reporting over a population nobody counts has not been read, whatever it printed.

### §2bf.3 **THE REMEDY cfd PROPOSED IS NOT COMPUTABLE TODAY, AND THE REASON IS THE DEFECT IT WOULD MEASURE**

cfd proposed a **sixth weekly number** — corpus-wide `pins_unseen` — beside the CASE PROTOCOL's five. **This supervisor tried to compute it and could not, and the failure is the finding.**

| recogniser | registrations flagged | unseen pins |
|---|---|---|
| first attempt, suffix `[A-Za-z0-9_+-]{1,12}` | 93 | **554** |
| bounded to real file classes | 55 | **323** |
| …of which **one file**, `docs/COST_CALIBRATION.md`, contributes | — | **228** |

**`docs/COST_CALIBRATION.md` IS NOT A REGISTRATION.** It is the cost ledger, and its rows cite run artifacts — `COST.txt`, `RUN_RC.txt`, `CONTENTION.txt` — beside shas. Those are the **CLASS B outputs** `D597` measured at **102 of 138**, which **may never be pinned at all**, because `IDENTITY` demands worktree == HEAD blob and an output changes when the run runs.

**So a corpus-wide census cannot be computed without first deciding WHICH FILES ARE REGISTRATIONS AND WHICH ROWS ARE PIN CLAIMS — and that is precisely the question `D597` identified as the real defect and put on Sanaa's desk.** The proposed measurement is blocked by the thing it was proposed to measure. **That strengthens the case for the repair rather than weakening it, and it means no corpus figure is published here**, because a number this supervisor cannot defend is worse than none.

**WHAT IS COMPUTABLE, AND IS THEREFORE WHAT THE CLAUSE REQUIRES: `pins_unseen` PER CASE, AGGREGATED OVER CASES THAT ACTUALLY RAN STAGE 1.** It is well defined there because **the case names its own registration**; it is undefined corpus-wide because *"which `.md` is a registration"* is undecided. This gives the warning a floor without requiring the undecided question to be answered first, and the aggregate rises as cases enter the protocol rather than being a one-off scan nobody repeats.

### §2bf.4 AND THIS SUPERVISOR COMMITTED THE ERROR THE CLAUSE IS ABOUT, TWICE, WHILE WRITING IT

**The first recogniser above matched `` `0.000` ``, `` `0.40` ``, `` `0.orig` ``, `` `C1.3` `` — numbers and version strings in backticks, counted as pinned paths.** That is `§17a`'s over-reach, *"which looks like rigour while it is happening"*, and this team warned against exactly it in `D597` one commit earlier. **The second attempt was still dominated 228-to-95 by a file that is not a registration.**

**The cause is not carelessness and is worth naming because another supervisor confessed the identical pattern today:** *I reached for a detector I could write in one line instead of using the instrument that already existed.* The instrument existed — `case_protocol_freeze_hook.py`'s recogniser, which differs from the frozen `PIN_PATH` in exactly one dimension and had already returned a defensible **45**. **Both wrong numbers came from a one-line regex written in preference to a tool built four hours earlier by this team's own lane.** Recorded so the next census starts from the instrument.

| amendment record | **v1.76** |
|---|---|
| clauses added | **1** (§2bf) |
| existing clauses altered, widened or narrowed | **0** |
| gate values changed | **0** — `D608`'s WARN default is unchanged and the pre-registered flip still ties to the `PIN_PATH` repair |
| executable checks made to refuse | **0** (`D539`) |
| corpus figures published | **0**, deliberately — the census is blocked by the defect it would measure |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.77, 2026-09-10 — **§2bf GAINS ITS MEASURED BODY AND A SHARPER DANGER (an advisory and an enforcement are INDISTINGUISHABLE FROM THE ARTIFACT), AND §2bg: A HEADLINE TRAVELS ALONE**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Both raised by **cfd**; both verified at source by this supervisor before adoption. `[lab-attributed]`. **No gate, threshold, cap, band or label moves; no executable check is made to refuse (`D539`).**

### §2bf.5 — `D539`'s COST IS NO LONGER HYPOTHETICAL. IT HAS A BODY, IN A LIVE CASE, TODAY

`§2bf` argued that `D539` *"systematically manufactures a growing population of warnings"* and that its cost had never been named. **cfd supplied the instance and it is on disk.** `cases/navier_class/SUBOFF/CAP_OVERRUN.txt`, written by the runner at `2026-09-10T07:21:03Z`, quoted verbatim and read at source:

> *"CAP OVERRUN REPORTED, NOT ENFORCED: case `SUBOFF-R1-TRIPLE` … elapsed **9022 s > 1.00 x registered CAP 9000 s** … **The run was NOT killed. THAT IS A PROPERTY OF THIS RUNNER AS BUILT, NOT A PERMISSION ANY CHARTER GRANTS:** `COMPUTE_BUDGET_CHARTER.md:197` says the OPPOSITE — 'A budget overrun stops the run. It does not get a new budget.' — and `CLAUDE.md` rule 12 repeats it. No clause of that charter carves out a report-only cap. Runner-side cap enforcement is pre-registered at `docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md` (`D539`) and is **ADVISORY, INERT and OFF**; switching it on is Sanaa's alone."*

**So the advisory-by-necessity structure has already produced one unenforced cap in a live case, with the charter clause it violated quoted in the runner's own output.** `RUNNER_CAP_ENFORCEMENT_CLAUSE.md:3` confirms the status: *"**Status: ADVISORY. INERT. OFF.** Not switched on, and no agent may switch it on."* **Nothing here criticises `D539`, which is correct and undisturbed** — it names the price, which `§2bf` said had never been named.

### §2bf.6 — THE SHARPER DANGER, AND IT REPLACES THE DECAY FRAMING AS THE PRIMARY ONE

`§2bf` framed the hazard as **attention decay** — a warning becoming wallpaper. cfd's framing is better and is adopted as primary:

> **THE DANGER IS NOT THAT AN ADVISORY IS IGNORED. IT IS THAT AN ADVISORY AND AN ENFORCEMENT ARE INDISTINGUISHABLE FROM THE ARTIFACT.**

A reader of the record cannot tell **a cap that was enforced and not breached** from **a cap that was never enforced and was breached** — both leave a run that finished and a log that does not mention a kill. Decay is a property of readers; **indistinguishability is a property of the evidence**, and it survives a perfectly attentive reader. It is the same sentence as *"an instrument that could not act and an instrument that had no cause to act produce identical silence"*, and as `D593`'s *"a check reporting no violations over a population it could not evaluate."*

**AND THE RECURSION IS THE PART WORTH KEEPING.** `RUNNER_CAP_ENFORCEMENT_CLAUSE.md:257-260` **already identified this danger and already mechanised it**, as mandatory mutant **P2**, verbatim:

> *"**P2 (MANDATORY) — force `enforce=True` → control 8 must FAIL.** Without P2, control 8 passing proves nothing: a wrapper that happens to exit, or a clause that happens not to fire, **looks identical to an off switch**. **The off-state must be shown to be what held the run, not an accident.**"*

**That control lives inside a clause that is ADVISORY, INERT and OFF.** So the mutant that would prove the off-state is deliberate **never runs, because the thing it controls is off.** **A control that can only run when the guard is armed says nothing about the period when the guard is off — and that period is the entire period.** This is not a defect in cfd's clause, whose author saw the hazard clearly enough to mechanise it; it is what `D539`'s reservation costs, stated at the only level where it is visible.

### §2bg — **A HEADLINE TRAVELS ALONE, SO IT MUST BE TRUE ALONE**

Raised by cfd against **this team's own reporting of a finding about standing rule 3**, and the correction is accepted.

The finding: `CLAUDE.md` rule 3 names `analyse_t3.py` and `analyse_t10a.py` as its reference implementations, and **both plant into a copy and call the reader in-process rather than through its CLI.**

**Stated as *"the exemplars demonstrate a NARROWER property than the rule states"* it is true and useful.** They prove the field-reading **function** can see a plant; they do not prove that bytes on disk propagate through the real path to a changed verdict. **Stated as *"rule 3's controls are broken"* it would be FALSE and damaging** — neither manufactures a favourable world-state, and T10a's exact-equality on the float-representable delta is **tighter** than the new check's.

> **A FINDING'S HEADLINE IS WRITTEN TO SURVIVE SEPARATION FROM ITS BODY, BECAUSE IT WILL BE SEPARATED. Where the careful statement and the arresting one differ, the headline carries the careful one, and the caveat that makes it true goes ABOVE the fold, not below it.**

**This is the headline-versus-substance defect this team named against its OWN board today** — three standing audits whose "standing" was asserted in a summary phrase that no section re-measured — and against `check_comparator_freeze.py`, whose *"N of N pinned executable(s)"* is **word-for-word true and misleads anyway** because the count is what gets read. **`§2be.1`'s hard-coded claim-string, that coverage line, and a finding's own headline are one family: a sentence whose narrower truth is disclosed somewhere the reader does not go.**

**Applied immediately to this team's own record:** `D610`'s body states the rule-3 finding carefully, and its **commit subject does not**. That subject cannot be edited and is disclosed here instead, as `V-152` and `§A8.3` were.

| amendment record | **v1.77** |
|---|---|
| clauses added | **1** (§2bg); §2bf gains two dated sub-sections (§2bf.5, §2bf.6) |
| existing clauses altered, widened or narrowed | **0** — §2bf's decay framing is retained and demoted, not struck |
| gate values changed | **0** |
| executable checks made to refuse | **0** (`D539`) |
| measured instances behind these clauses | **1** (`SUBOFF-R1-TRIPLE`, 9,022 s past a 9,000 s cap, not killed) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.78, 2026-09-10 — **§2bf.7: THE CONTROL'S UNREACHABILITY HAS ALREADY BEEN LOAD-BEARING IN A LIVE CASE, AND WHAT STOOD IN ITS PLACE WAS THE INSTRUMENT'S OWN CANDOUR. §2bf.6's DISPOSITION IS CORRECTED: THE TWO FRAMINGS ARE ORTHOGONAL, NOT RANKED**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **cfd** against **their own clause** — `RUNNER_CAP_ENFORCEMENT_CLAUSE.md:5` reads `**Owner:** cfd-supervisor`, and they asked that it be recorded as their team's finding rather than as this team's about theirs. **That attribution is honoured.** `[lab-attributed]`. **No gate, threshold, cap, band or label moves; nothing is made to refuse (`D539`).**

### §2bf.7 — THE LAYER BELOW THE RECURSION, AND IT IS THE WORST ONE

`§2bf.6` recorded that mutant **P2** — the control written to prove an off-state was *deliberate* — is reachable only when the clause is armed, and the clause has never been armed. **cfd's addition is that this has already cost something, in the one case where it mattered.**

**`SUBOFF-R1-TRIPLE`'s overrun happened *in* the off-state.** So when the runner reported 9,022 s past a 9,000 s cap and did not kill:

> **The ONLY artifact distinguishing *"the clause was deliberately off"* from *"the clause was armed and silently failed to fire"* is `CAP_OVERRUN.txt` — a SELF-REPORT written by the very instrument in question.**

Verified by this supervisor: `cases/navier_class/SUBOFF/` contains **`CAP_OVERRUN.txt` and no `CAP_STOPPED.txt`** — the enforcement artifact is absent, so the self-report genuinely stands alone.

**P2 exists precisely to replace that self-report with a control, and P2 cannot run.** So **the one case where the distinction mattered is the one case where only the instrument's own word is available.** A self-report from the subject is what a control exists to replace; here the control's unreachability leaves the self-report standing alone — **and it happens to be honest.**

> **WE ARE RELYING ON THE CANDOUR OF AN INSTRUMENT RATHER THAN ON EVIDENCE ABOUT IT, AND CANDOUR IS NOT A PROPERTY YOU CAN AUDIT.**

**This converts the finding from *a control is unreachable* into *a control's unreachability has already been load-bearing*, which is a different and larger claim.** And the saving grace is real and is stated beside it rather than instead of it: **the runner wrote that note unprompted, quoting the charter clause it was violating.** `§2be.1`'s hard-coded claim-string is the same instrument class behaving in the opposite direction — **a less candid instrument would have produced identical silence, and nothing in the system would have known.**

### §2bf.8 — CORRECTION TO §2bf.6's DISPOSITION: THE TWO FRAMINGS ARE **ORTHOGONAL**, NOT RANKED, AND EACH HAS ITS OWN REMEDY

`§2bf.6` adopted cfd's indistinguishability framing **as primary** and demoted this team's decay framing. **cfd objected to their own promotion, and they are right.** The correction:

| failure | what it is | **remedy** |
|---|---|---|
| **DECAY** | a warning that is still legible but no longer read | **A CENSUS.** Publish the population the advisory fires over — `§2bf`'s population count |
| **INDISTINGUISHABILITY** | two states that leave the same evidence, so an attentive reader still cannot separate them | **NOT COUNTING — DIFFERENTIAL ARTIFACTS.** Make the two states write different files. **That is exactly what P2 was for** |

**Counting does not touch indistinguishability, and differential artifacts do not touch decay.** cfd's words, adopted: *"a clause that only carried my framing would tell a reader what is wrong without telling them that counting helps."*

**`§2bf.6`'s "retained and demoted" is therefore corrected to RETAINED AND CO-EQUAL.** Neither framing supersedes the other; a reader of `§2bf` must leave with **both failures and both remedies**, because a check that has a census but no differential artifact is as incomplete as one with the reverse. **The clause's substance is unchanged and nothing above is struck** — this corrects a ranking this supervisor imposed on it, on the objection of the person it favoured.

| amendment record | **v1.78** |
|---|---|
| clauses added | **0** — two dated sub-sections on §2bf (§2bf.7, §2bf.8) |
| existing clauses altered, widened or narrowed | **0**; one **disposition** corrected (§2bf.6's ranking → co-equal) |
| gate values changed | **0** |
| executable checks made to refuse | **0** (`D539`) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.79, 2026-09-10 — **§2bh: A GATE SET AT THE SOLVER'S OWN ACCEPTANCE IS AN IDENTITY AND A TOLERANCE-ORDERING VIOLATION AT THE SAME TIME. `D596` §5 AND THE T23G2Rn2 RULE ARE ONE RULE SEEN FROM TWO ENDS**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **dafoam** (`719640ce`) as a forward-binding finding against their own successors. `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`).**

dafoam recorded that `D6RF10`'s **`CONV_BAR` = `primalMinResTol × primalMinResTolDiff`** — a gate set **equal to the solver's own acceptance product** — is the **T23G2Rn2 rule in DAFoam form**, and that **no `D6` successor may register it again.** The generalisation is worth stating once, here, because **this team reached the same conclusion from the opposite direction six hours earlier and did not notice they were the same rule.**

> **A GATE SET AT OR LOOSER THAN THE SOLVER'S OWN ACCEPTANCE CRITERION CANNOT FAIL, BECAUSE THE SOLVER REFUSES TO PRODUCE ANYTHING THAT WOULD FAIL IT. IT IS AN `§2a` IDENTITY — REPORTABLE, NEVER GATEABLE — AND IT IS THE SAME FACT AS THE TOLERANCE-ORDERING REQUIREMENT THAT THE SOLVER TOLERANCE BE STRICTLY TIGHTER THAN ANY GATE.**

**The two ends:**

- **`D596` §5 (this team, 2026-09-10)** refused `A2-GC-P`'s `GATE R` at the accept floor under **`§2a` question (2)** — *could a wrong treatment still pass?* — because any level reaching a grader **has already cleared the floor by construction**, the solver having aborted everything above it (`mphys_dafoam.py:344-345`).
- **The T23G2Rn2 rule (stage 1)** requires the **solver tolerance strictly tighter than any gate**, stated as an ordering constraint on registration.

**They are the same constraint.** The ordering rule is the *prospective* form — set the tolerance tighter and the gate can bite. The identity test is the *retrospective* form — a gate that cannot bite is not a gate. **A registration satisfying the ordering rule cannot produce this identity, and a registration producing this identity has violated the ordering rule.** Naming them as one closes the gap through which a case could satisfy the letter of one while failing the other.

**Recorded as a cross-reference, not as new law:** `§2a` and the T23G2Rn2 rule both already existed and neither is widened. **dafoam's forward binding on `D6` successors is theirs and stands as they wrote it**; the numerics-record append is dafoam's to make, and this team does not reach into another team's record to make it.

---

## Amendment — v1.80, 2026-09-10 — **§2be.2 NARROWS `§2be.1`'s FAMILY, WHICH WAS PARTLY REFUTED BY MEASUREMENT WITHIN THE HOUR. §2bd.2 CORRECTS `§2bd.1`'s CONSEQUENCE CLAIM. §2bi: `hits[-1]` REACHES THE CORRECTOR SOLVE, WHICH IS THE FIELD THIS TEAM'S OWN 2026-09-08 RULING SAID CANNOT BIND. §2bj: `INSTRUMENT REFUSAL` IS A CAUSE CLASS, NOT A VERDICT**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **cfd** (`611aed5a`) from four plants driven through the real path; the load-bearing items re-verified at source by this supervisor. `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`); standing rule 1's vocabulary is UNTOUCHED.**

### §2be.2 — **`§2be.1`'s FAMILY WAS TOO WIDE AND IS NARROWED. THE OPERATIVE DISTINCTION IS PLANT SHAPE AND JUDGMENT CRITERION, NOT "COMPUTATION DEFECTS ARE UNREACHABLE BY PLANTING"**

This supervisor told cfd that a planting harness could not reach either of their comparator defects, and put the reasoning behind `§2be.1`. **cfd measured it and the claim is half wrong.** Four plants, decision field read rather than output bytes:

| plant | role | result |
|---|---|---|
| P1 offset on last row | positive control | **DETECTED** — `CT` 4.732714 → 4.733949 |
| **P2 drift over the trailing window** | defect probe | **NOT-DETECTED** — `iteratively_plateaued` stayed `True` |
| **P3 residual, FIRST occurrence** | defect probe | **NOT-DETECTED** — `p` residual stayed 3.8976e-04 |
| P4 residual, LAST occurrence | positive control | **DETECTED** — 3.8976e-04 → 0.99 |

**P2 plants +20 % drift over the final 100 writes — 40× `PLATEAU_TOL_REL` — with the final step held at 0.05 %.** A trailing-window statistic sees it; an endpoint difference cannot. **`NOT-DETECTED` IS THE DEFECT BEING CAUGHT BY PLANTING**, not planting failing.

> **THE CORRECTED RULE: planting cannot reach a computation defect when the plant is shaped like a GENERIC PERTURBATION and detection is judged on WHETHER THE OUTPUT CHANGED. A plant shaped like the FAILURE MODE, judged on the DECISION FIELD, does reach it.**

**What stays in `§2be.1`'s family:** `:369`'s wrong-file defect — it reads *a* file faithfully, so **only a cross-reader or a source read distinguishes faces from cells** — and hard-coded claim-strings, which **no input can touch**. **What comes OUT: the two-point plateau test.** Stated as *"planting cannot detect these"* the family was wrong about `:368`; stated as the distinction above it is right about all three.

**Consequence for the stage-2 harness, and it is a design requirement not a note:** a `NOT-DETECTED` is **evidence only when the plant was shaped like the hypothesised failure and the reader's DECISION FIELD was read.** A generic perturbation judged on output bytes yields a `DETECTED` that is **true and uninformative** — which is what this supervisor predicted — but that is a limit of *that* plant, not of planting.

### §2bd.2 — CORRECTION TO `§2bd.1`'s CONSEQUENCE CLAIM

`§2bd.1` is headed *"…AND IT REACHES `r` AND THEREFORE `GCI`"*. **cfd has corrected their own report and the correction is against this team's clause: the `nFaces`/`nCells` error is very nearly a COMMON FACTOR across levels, so `r` comes out 1.49937 / 1.49958 against 1.50000 — off by 0.042 % and 0.028 %, which is immaterial.** **The heading overstates and is corrected here rather than edited above.**

**The defect stands and its real damage is restated:** a **published mesh size 4.01× wrong**, and a **spurious unequal-ratio branch**. **The clause's requirement is unchanged** — a cell count used in a refinement ratio is read from a source that counts cells — because a defect that happens to cancel is still a defect and the cancellation is a property of this mesh family, not of the method.

### §2bi — `hits[-1]` REACHES THE CORRECTOR SOLVE, AND THAT IS THE FIELD THIS TEAM ALREADY RULED CANNOT BIND

cfd's P3 caught a **third** gate-affecting defect neither team had flagged. `grade_suboff.py:197-199`, verified at source by this supervisor:

```python
hits = re.findall(rf"Solving for {f},\s*Initial residual\s*=\s*([-\d.eE+]+)", logtxt)
if hits:
    finals[f] = float(hits[-1])
```

**`hits[-1]` is the LAST `Solving for p` line — the non-orthogonal CORRECTOR solve — not the solve OpenFOAM's own convergence test reads.** Measured on the fine level's final iteration: first-solve **0.01208393174399553** against last-solve **0.0003897631590649481**, a factor of **31.0**, and **24.4× / 23.4× / 31.0×** across the three levels.

**THIS IS EXACTLY THE FIELD THIS TEAM REFUSED ON 2026-09-08**, in `A2_ACCEPT_FLOOR_BINDING_FIELD_RULING`: *"`p_corrected` measures the wrong thing for outer-loop convergence … It can be driven arbitrarily small regardless of whether the outer loop has converged, so it CANNOT establish steady-state iterative convergence."* **And the finding generalises that ruling in the way that matters: there it was a proposed SWITCH, refused as gate-widening by field selection. Here nobody chose it — `hits[-1]` produces it BY DEFAULT.** So the ruling is not a guard against a temptation; **it is a guard against the natural output of the obvious regex**, in a second instrument, in a different team, reached independently.

**It flips no R1b verdict and the record stands. It is a LATENT FALSE-GREEN:** any run whose true `p` residual is 1.2e-02 grades `CONVERGED` whenever the corrector solve lands under `RES_TOL`. **cfd's blocker on any SUBOFF `PASS` is now three defects, not two.**

**And cfd's pattern across all three is adopted, because it is a better organising statement than this charter had:** **each reads a real artifact faithfully and asks it the wrong question** — `:368` the wrong **statistic**, `:369` the wrong **file**, `:197-199` the wrong **line of the right file**. **The third is the most dangerous shape because it is the one that looks most like correct code.**

### §2bj — **`INSTRUMENT REFUSAL` IS A CAUSE CLASS, NOT A VERDICT, AND STANDING RULE 1 IS UNTOUCHED**

Two of cfd's lanes independently hit the same gap: a grading stage that **refuses** has no stop taxonomy and no ladder, so a refusal gets driven up a ladder built for a different failure.

**The vocabulary is not extended.** Standing rule 1 fixes `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and **no new verdict word is created here.** `INSTRUMENT REFUSAL` is a **CAUSE CLASS attached to a `NOT A RESULT`** — the same shape the protocol already asks for when it requires a verdict *"plus cause class"*, and the same relation `NOT HELD` bears to `GATE FAIL` under `§16`.

> **`INSTRUMENT REFUSAL`: a `NOT A RESULT` whose cause is that the GRADING PATH could not reach a verdict, not that the RUN failed. Its distinguishing property, and the reason it needs naming: ITS REGISTERED ACTION IS NEVER MESH, NUMERICS OR MODEL — because the run is not what failed.**

**Why the naming earns its place:** without it, a refusal is triaged up a ladder aimed at the solve, and **every rung of that ladder acts on something that was not the problem** — spending compute to repair a mesh that is fine, in response to a reader that could not parse. It is the reporting-layer twin of `§2c`'s *"a check that did not reach its subject has not passed; it has not run."*

**NOT ADOPTED HERE, and referred rather than legislated:** cfd also reports that the **stage-3 and stage-4 ladders are different** — §4 being *"continuation from a converged neighbor, relaxation reduction, pseudo-transient, then transient re-registration"* against §3's mesh → numerics → model — and that conflating them **acts against a mesh that is not what stopped**, all three SUBOFF levels clearing their quality gates. **That is CASE PROTOCOL territory, that charter is Sanaa's and is still ABSENT at HEAD, and this team does not legislate another document's ladder.** Recorded for her weekly.

| amendment record | **v1.80** |
|---|---|
| clauses added | **1** (§2bj, a cause class — **not** a verdict) |
| existing clauses **narrowed** | **1** (§2be.1's family, on measurement that partly refuted it) |
| existing clauses **corrected in consequence, not in requirement** | **1** (§2bd.1) |
| standing rule 1 vocabulary changes | **0** |
| gate values changed | **0** · executable checks made to refuse | **0** (`D539`) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.81, 2026-09-10 — **§2bk: A FACT WITHOUT A GUARD IS A FACT REMEMBERED. I RE-DERIVED THE GUARDED FACT IN EVERY COMMIT AND CARRIED THE UNGUARDED ONE FROM MEMORY INTO THE SAME COMMITS, THREE TIMES AFTER IT HAD GONE FALSE**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **cfd**, against a premise this supervisor repeated in five commit messages. `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`).**

### §2bk.1 THE MEASUREMENT, AND IT IS THE WORSE OF THE TWO EXPLANATIONS ON OFFER

cfd asked which of two things happened: a path that exists resolving to a path that does not — **the third `check_comparator_freeze.py` defect, live in this team's own hands** — or ordinary staleness. **Measured, and it is neither flattering nor a tooling bug:**

| event | sha | time |
|---|---|---|
| `CASE_PROTOCOL_CHARTER.md` **added** | `e24953a6b` | **16:52:41Z** |
| this team's check returned ABSENT, HEAD then | `477ce19b` | **16:48:29Z** |

**The check was CORRECT when it ran — 4 min 12 s before the file existed. No path resolved wrongly.** But the claim was then repeated in **three commits after it had gone false**: `f49d3e42` (**+87 seconds**), `5d56de90` (**+7.5 min**), `948531e1` (**+37.7 min**).

### §2bk.2 THE PART THAT IS A STANDARD AND NOT AN APOLOGY

**In every one of those commits this supervisor RE-DERIVED the docket id at commit time, in the same invocation, behind a guard — and that guard FIRED**, catching peers' rows and moving the id from `D604` to `D608`. **So the same commit carried one fact re-derived by machine and another carried from memory, and the difference between them was not importance. It was whether a guard existed.**

> **A FACT WITHOUT A GUARD IS A FACT REMEMBERED. Rule 11's "re-derive at commit time" is not a rule about docket numbers; it is a rule about EVERY CHECKABLE CLAIM IN THE MESSAGE. A claim that was verified once and is asserted again has been REMEMBERED, not verified, and the interval is exactly as long as nobody re-ran it.**

**The operative statement was true throughout and remains true:** these commits *"cite no authority I have not read"* — the charter was never cited. **But its stated JUSTIFICATION went false 87 seconds into the first commit that gave it.** A true conclusion resting on a false premise is `§A8.3`'s *"a true answer resting on a false attribution"* and `§2bg`'s headline problem, arriving this time **in the reasoning of the commit messages that were naming those very shapes in other people's work.**

### §2bk.3 THE CHARTER'S ACTUAL TEXT, NOW READ — AND IT VINDICATES THE RELAYED SPEC

85 lines, read at HEAD (blob `b9863286`). **Nothing this team built to the relayed spec conflicts with it**, and three lines bear directly:

- **`:26`** — *"Nothing below is run until the freeze check passes."* The freeze hook's authority, verbatim as relayed, so **`D608`'s reading that Sanaa added that gate herself is confirmed against her own text** rather than against a summary of it.
- **`:35`** — *"every reader that will grade this case detects a planted perturbation **through the real path**; a reader that cannot see its plant **fails the case closed**."*
- **`:58`** — *"verdict written as one of `PASS`, `GATE FAIL`, `NOT A RESULT`, **with the cause class for any non-pass**."* **This independently confirms `§2bj`: `INSTRUMENT REFUSAL` as a CAUSE CLASS is the shape her charter asks for, and a seventh verdict word would have CONTRADICTED HER TEXT** — a thing this team would have discovered by reading the file it was asserting to be absent.

### §2bk.4 cfd's REFERRAL IS RE-CHARACTERISED, AT THEIR REQUEST AND CORRECTLY

`v1.80` recorded the stage-3/stage-4 ladder item as *"CASE PROTOCOL territory, that charter is Sanaa's and is still ABSENT at HEAD"*. **It is not a proposal about an absent charter. It is a READING OF A PRESENT AND CLEAR ONE:** §4's ladder sits at **line 53**, *"continuation from a converged neighbor, relaxation reduction, pseudo-transient, then transient re-registration"*, against §3's mesh → numerics → model — **unambiguous on the face of the document.**

**The conflict cfd reported was their own brief's error, not an ambiguity in her text**, and cfd asked that it reach her weekly in that form. **It is recorded that way, because it makes her charter look clear — which it is — rather than contested.** `v1.80`'s conclusion (*"this team does not legislate another document's ladder"*) is unaffected and stands on its own; **only its premise was wrong.**

| amendment record | **v1.81** |
|---|---|
| clauses added | **1** (§2bk) |
| existing clauses altered, widened or narrowed | **0**; one **premise** corrected in `v1.80` (§2bk.4), its conclusion unaffected |
| gate values changed | **0** · checks made to refuse | **0** (`D539`) |
| commit messages carrying a claim false at their own commit time | **3** — `f49d3e42`, `5d56de90`, `948531e1`; **they cannot be edited and are disclosed here** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.82, 2026-09-10 — **§2bk.5 THE OPERATIONAL FORM §2bk LACKED, FROM A SECOND MEASURED INSTANCE INSIDE THE HOUR. §2bl AN ABSENT CHECK IS NEITHER PASSED NOR FAILED — CLAUSE 7 IS FAMILY-WIDE DEAD AND CONSEQUENCE-FREE FOR EVERYTHING GRADED. §2bm THE UNREVIEWED INSTRUMENT: WE REVIEW WHAT WE COMMIT AND BELIEVE WHAT WE TYPE**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **cfd** (§2bk.5) and **heat-transfer** (§2bl, §2bm), each against their own work; census and exculpation re-verified at source by this supervisor. `[lab-attributed]`. **No gate value moves; no verdict is withdrawn; nothing is made to refuse (`D539`).**

### §2bk.5 — A SECOND INSTANCE WITHIN THE HOUR, AND THE OPERATIONAL FORM THE CLAUSE WAS MISSING

`§2bk` stated the principle and gave **no operational form**. cfd supplied both a second instance and the remedy, against themselves: they asserted *"the box is at load 45.85 on 16 vCPU"* in **four consecutive reports** and used it as the stated reason for a decision — refusing to launch a sixth solver. **Re-derived at 17:40:17Z: load average 3.96.** The box had drained.

**The structure is identical to this team's, including the part that makes it a standard rather than an anecdote:** in those same reports cfd re-derived HEAD, the commit sha and the numstat **every time, because a machine handed them over**, while the load figure came from memory **because only a human could have re-run it**. **Same report, one fact verified by machine and another remembered, and the difference was not importance but whether a guard existed.**

**And it was load-bearing, which is worse than a stale number:** the decision it justified — M6 not launching — was real and had a cost. It was right when made and is now moot, but **the justification decayed before the conclusion did**, which is `§A8.3`'s shape a second time in one hour, in a second team.

> **THE OPERATIONAL FORM, adopted from cfd verbatim: ANY FIGURE IN A REPORT THAT A READER COULD ACT ON IS EITHER RE-DERIVED IN THE INVOCATION THAT REPORTS IT, OR STAMPED WITH THE TIME IT WAS MEASURED. NEITHER IS OPTIONAL.**
>
> The class that needs it is the one nothing breaks over: **a load average, a `MemAvailable`, a "no solver is running", a file's presence.** Unlike a docket id, **nothing fails when these are stale** — which is exactly why they go false silently and why nobody re-runs them.

**One correction cfd offered against this team's own framing, and it is accepted because it is more useful than the compliment it replaces.** This supervisor wrote that two clauses existed because cfd *"read my work more carefully than I did."* cfd's account: both times they held a **cheap measurement** and took it **only because the claim was stated precisely enough to be checkable**. **A vague claim cannot be refuted in thirty seconds.** So the reproducible mechanism is **falsifiable writing**, not attentive reading — and the lesson transfers to anyone, where a compliment does not.

### §2bl — **AN ABSENT CHECK IS NOT A FAILED CHECK, AND IT IS NOT A PASSED ONE EITHER**

heat-transfer's framing, adopted verbatim as the clause name, on their own family-wide finding: **rule 4's clause 7 is defined in the `mark_done_*` instruments and was called by NO launcher anywhere in the lab.**

**Census re-run by this supervisor over tracked paths:** **six** instruments define `launch_guard` — `mark_done_k0d/k0f/k0g/k0h.py`, `mark_done_adaptive.py`, `cases/navier_class/PRD/mark_done_prd.py` — and **exactly two call sites exist, `scripts/launch_k0h.sh` and `scripts/launch_k0h_selftest.sh`, both created by heat-transfer's repair today.** Before it, **zero, lab-wide.** *(One discrepancy named rather than reconciled silently: heat-transfer reports **seven**, including `K2b_runs/mark_done_k2bU3R3.py`, which this team's tracked-path census did not return — it is either untracked, which `D593` makes a live possibility, or it defines the guard in another form. Named, not resolved.)*

**The structural cause is adopted from heat-transfer and it exonerates every author:** the builder creates `0/` **itself**, so clause 7 invoked **after** the build refuses every case and invoked **before** it has nothing to judge. **Nobody forgot to call it. It could not be called.**

**THE EXCULPATION IS VERIFIED, NOT RELAYED, because it is the load-bearing half.** `K0f_RESULTS.md` read at source: **`TALLY 0 of 10, RUNG VERDICT GATE REACHED`**, with `NOT A RESULT` on every graded row — the ordered gate stopped at limb (1) on all ten because no level is iteratively converged, **so no band was ever read.** K0g carries `DONE.M1_c` and `DONE.M2_c`, and this team's own `§10` independently verified **clause 6 holding on both arms, fields post-dating `0/T` by about 2.6 hours.**

> **RULED: no verdict is withdrawn, and no case is alleged dirty. What the gap means is narrower and is stated exactly — those verdicts rest on CLAUSE 6 ALONE for the stray-write question: on the age guard HAVING PASSED, not on clause 7 HAVING BEEN CHECKED.**

**AND THE BUILDER REPAIR IS NOT ORDERED FOR K0f OR K0g.** Re-sequencing a builder on a graded path touches an instrument on that path — **K0g's are frozen under rule 6** — to close a gap that is **consequence-free for everything graded in the family.** The cost of the repair exceeds the risk it retires. **What IS owed is disclosure: each affected registration states on its face that clause 7 was never reachable, so a future reader does not take it as having been checked.** `mark_done_prd.py` is **navier-class territory and is referred, not touched.**

**heat-transfer's two self-corrections are recorded because they are the behaviour this charter wants and rarely gets:** they withdrew a credit claim (*"a fourth ground … and it is MINE"* — the finding arrived in this team's `§8` and the `0.orig` repair was prescribed in `§7.4`), and they **reduced their own blocker count from five to three**, on the ground that *"inflating a blocker count is as dishonest as deflating one."*

### §2bm — **THE UNREVIEWED INSTRUMENT: WE REVIEW WHAT WE COMMIT AND BELIEVE WHAT WE TYPE**

heat-transfer counted, across their lanes and themselves in one session, **roughly seven false zeros from ad-hoc filters** — a `ugrep` flag rejection swallowed by `2>/dev/null` reporting *"no implementation exists"* about a fully-implemented guard; a `grep -v` that deleted every line because they carried a two-space indent; a case-survey glob undercounting 3D candidates **threefold**; a `STATUS` file sought in the wrong directory. **This supervisor contributed two more in the same session** — a recogniser counting `` `0.000` `` and `` `0.orig` `` as pinned paths, and its bounded successor dominated 228-to-95 by a file that is not a registration.

**heat-transfer's diagnosis is exact and is the clause:**

> **THE INSTRUMENTS WE COMMIT ARE REVIEWED. THE FILTERS WE TYPE AT A PROMPT ARE NOT.**

A committed comparator gets `SUPERVISION_CHARTER` §3 check-1 as a diff, a selftest, planted controls and a supervisor's read. **A `grep`, a glob or a regex typed at a prompt gets none of these, and its output is believed immediately — because it is convenient and because nothing in the system knows it ran.**

> **CLAUSE: an ad-hoc filter IS an instrument, and standing rule 3 reaches it. A ZERO from a filter typed at a prompt is NOT A MEASUREMENT until that filter has been shown able to return NON-ZERO on the same corpus. This creates no new law — it is rule 3, applied to the one instrument class the lab has never applied it to.**

**The cheapest sufficient form is a positive control on the same command:** a pattern known to be present, in the same shape as the target, run through the identical filter. **Every one of the nine instances above would have been caught by it**, and none of them was caught by luck — each was caught by somebody declining to believe a convenient empty result, which is a disposition and not a control.

| amendment record | **v1.82** |
|---|---|
| clauses added | **2** (§2bl, §2bm); §2bk gains its operational form (§2bk.5) |
| existing clauses altered, widened or narrowed | **0** |
| gate values changed | **0** · verdicts withdrawn | **0** · checks made to refuse | **0** (`D539`) |
| new law created by §2bm | **0** — it is standing rule 3 applied to a class it never reached |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.83, 2026-09-10 — **§2bn A CENSUS BY IDENTIFIER MEASURES THE IDENTIFIER, NOT THE PROPERTY — AND IT CORRECTS `§2bl`'s LOAD-BEARING HALF, WHICH WOULD HAVE LIBELLED THE BEST-GUARDED CASE IN THE LAB THE DAY BEFORE IT IS FILMED. §2bo A DIMENSIONALITY CLAIM IS READ FROM `checkMesh`, NEVER INFERRED FROM A CELL COUNT**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** §2bn raised by **heat-transfer** against their own finding of six hours ago; §2bo raised by **closure** against three of their own families, on the way into a stand-down. Both **verified at source by this supervisor before adoption**, not relayed. `[lab-attributed]`. **No gate value moves; no verdict is withdrawn; nothing is made to refuse (`D539`).**

### §2bn — **`§2bl` IS CORRECTED ON THE HALF THAT MATTERED, AND THE CORRECTION RUNS IN THE DANGEROUS DIRECTION**

`§2bl` (v1.82, six hours old) ruled that rule 4's **clause 7** — refuse a case where `0/` or a numeric time directory already exists — is **family-wide dead**, on a census returning **six** `launch_guard` definers and **zero** call sites lab-wide before heat-transfer's repair of the same day. It named one unresolved discrepancy: heat-transfer reported **seven**.

**Both halves of that discrepancy are now measured, and they fail in opposite directions.**

**(1) The seventh definer was UNTRACKED.** `verification/runs/F14-cooling-ladder/K2b_runs/mark_done_k2bU3R3.py` was invisible to a `git grep` census. It is **TRACKED as of `0e3d2f2f9`** (heat-transfer, today). Re-censused by this supervisor **on the disk, with `find`, not with `git grep`**, at 2026-09-10T18:58:35Z: **seven definers, all seven now tracked.** This half is the already-ruled tracked-path blindness class and adds nothing new.

**(2) THE HALF THAT IS NEW, AND IT IS AGAINST THIS TEAM'S OWN CLAUSE. "Zero call sites lab-wide" is TRUE OF THE FUNCTION NAME AND FALSE OF THE CHECK.**

`K2bU3R3` enforces clause 7 — all of it — **inline in its builder, under no such name.** Verified by this supervisor at source, reading `verification/runs/F14-cooling-ladder/K2b_runs/build_k2bU3R3.py` (**TRACKED**) at 19:08:38Z, not taken from the referral:

- `:149-151` — `if os.path.isdir(os.path.join(case, "0")): sys.exit("REFUSE (exit 2): … the age guard refuses a case that already carries a 0/ (rule 4).")`
- `:152-155` — `tds = _numeric_time_dirs(case)`; non-empty ⇒ `REFUSE (exit 2)`, naming rule 4.
- `:156-158` — a **stronger** limb this charter never asked for: a prior `log`/`COST.txt` also refuses, so an existing run's *record* cannot be overwritten either.
- `:161` — `if not os.path.isdir(case + "/0.orig"): REFUSE`, and only then, at `:164`, `copytree(0.orig → 0)` **at launch, with `0/T` touched last so it dates the run.**

**All four refusals precede the arming copy.** That is `T1b_L4_AMENDMENT` §7's prescription executed exactly, and it is the structure `§2bl` said *could not exist* — because `§2bl` reasoned that the builder creates `0/` itself, so a guard after the build refuses everything and a guard before it has nothing to judge. **The reasoning was sound and the conclusion was false: the resolution is to put the guard in the builder, before the builder's own arming step.** `K2bU3R3` had solved it before this team ruled it unsolvable.

> **RULED, and this team states the correction against itself first: `§2bl`'s clause NAME — "an absent check is neither passed nor failed" — stands and is untouched. `§2bl`'s FINDING that clause 7 was dead lab-wide is NARROWED: it is dead in the `K0` family, where the exculpation of v1.82 §2bl stands verified and unamended, and it was NEVER dead in `K2bU3R3`, which is the one rung in the lab where clause 7 genuinely ran.**

**WHY THIS IS THE DANGEROUS DIRECTION, and it is the whole reason the clause exists.** Every blindness class this lab has ruled so far — the fail-open gate (`§2v`), the unreachable selftest (`§2aj`), the false zero (`§2bm`) — fails **permissively**: it lets something through. **An identifier census fails ACCUSATORILY: it under-reports compliance, and it therefore manufactures a false charge against precisely the cases that implemented the property WELL ENOUGH TO NOT NEED THE STANDARD LIBRARY.** A case that copied the blessed function name is scored compliant; a case that implemented the property better, inline, under its own name, is scored delinquent. **The census rewards the copy and punishes the improvement.**

**AND IT WAS ABOUT TO BE LOAD-BEARING ON CAMERA.** `K2bU3R3` sits behind `DONE.K2bU3R3_D59`, one of only two presentable 3D `GATE REACHED` verdicts in its family — demo material, on the day the owner's stated priority is hard 3D demos. A "seventh dead lever" line, carried unchecked from a name-based census into a demo-adjacent claim, would have been a **false accusation against the best-guarded case in the family**, published in this team's own charter, by this team.

> **CLAUSE §2bn: A CENSUS THAT SEARCHES FOR AN IDENTIFIER MEASURES THE PRESENCE OF THAT IDENTIFIER AND NOTHING ELSE. IT MAY NEVER BE REPORTED AS A CENSUS OF THE PROPERTY THE IDENTIFIER USUALLY IMPLEMENTS.**
>
> Operationally, and this is the cheap form:
> 1. **A negative finding from an identifier census is a HYPOTHESIS, not a finding.** Before it may be written into a record as a defect, each named case is opened and the **property** is looked for **in whatever form it takes there** — inline, renamed, in a builder, in a launcher, in a wrapper.
> 2. **The count of cases opened is stated beside the census count.** "Six by name, seven on disk, seven opened, one enforces it inline" is a measurement. "Zero call sites" is a grep.
> 3. **A census may be reported as a bound, never as a total, when step 1 was not done** — and it is named as such in the sentence that carries it: *"no case implements it UNDER THIS NAME"*, never *"no case implements it"*.
> 4. **`§2bm`'s positive control applies unchanged** and is not sufficient on its own here: a positive control proves the filter can see the identifier. **It cannot prove the identifier is the property.** These are two different failures and the second needs step 1.

**This clause creates no new law about clause 7 and no verdict moves.** `K0f`'s exculpation (`TALLY 0 of 10`, every row `NOT A RESULT`, no band ever read) and `K0g`'s reliance on clause 6 are **re-affirmed exactly as v1.82 verified them**. The disclosure `§2bl` ordered on the `K0`-family registrations is **unchanged and still owed**. `K2bU3R3` is **removed from that disclosure's scope**: it owes no clause-7 disclosure, because its clause 7 fired. `cases/navier_class/PRD/mark_done_prd.py` remains navier-class territory, **referred and untouched**.

**Two acknowledgements this team owes and pays.** heat-transfer found this **against their own finding of the same day**, on a case that would have made their own report look worse rather than better, and said so in the commit subject. And their statement of the limit is adopted verbatim because it is the part most likely to be over-read: *"a blob recorded today pins forward from today and reaches nothing behind it. `DONE.K2bU3R3_D59` was certified on 2026-09-09 by bytes no committed document names."* **Committing the instrument today does not retro-pin the verdict, and `K2bU3R3_PREREGISTRATION.md:226` names no `mark_done` sha to compare against — that gap is real, is separate from clause 7, and is NOT closed by this amendment.**

### §2bo — **A DIMENSIONALITY CLAIM IS READ FROM THE MESH, NEVER INFERRED FROM A CELL COUNT**

closure, on the way into their stand-down, reported against three of their own families: **all three were boarded as 3D and all three were one cell thick.** Their diagnosis, adopted: **the cell counts were right; the dimensionality was inferred from them and never read.** In one family a **commented-out `blockMeshDict` line masqueraded as the live mesh.**

**The instrument already exists in every case that has ever been meshed, and this supervisor verified that before ruling** — sampled at 19:09:18Z across `verification/runs/` and `cases/`: **1,112 `log.checkMesh` files on disk**, and the line is present and discriminating in every one sampled:

- `verification/runs/F2_runs/primary_M0.8_a1.25_Re6e6/log.checkMesh` — `Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)`
- `verification/runs/F24_PRANDTL_MEYER_runs/coarse/log.checkMesh` — `Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)`
- `verification/runs/F27_NUMERICS_SUCCESSOR_R3_runs/{coarse,medium,fine}/log.checkMesh` — `Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)`

**A one-cell-thick extrusion reads `2 … (1 1 0)`. There is no ambiguity to resolve and no new instrument to build.**

> **CLAUSE §2bo: ANY CLAIM THAT A CASE IS 3D — in a registration, a board line, a certificate, a docket row, a report to the owner, or a demo caption — CITES `log.checkMesh`'s `N geometric (non-empty/wedge) directions` LINE, PER MESH LEVEL, WITH THE PATH IT WAS READ FROM. A CELL COUNT IS NOT EVIDENCE OF DIMENSIONALITY. NEITHER IS A `blockMeshDict`, WHICH CAN CARRY THE CLAIM ON A COMMENTED-OUT LINE.**
>
> - **Per level, not per case.** A family may be 3D at one level and extruded at another; the claim is made where it is measured.
> - **`3 geometric` is necessary and not sufficient for the word "3D" in a demo caption.** A wedge, a symmetry-plane sector or a single-cell-in-θ axisymmetric mesh can read `3` while being a 2D problem; the `(1 1 1)` triple and the **patch types** (`empty`, `wedge`, `symmetry`) are cited together. *(This limb is stated as the reading rule; `docs/standards/MESH_STANDARD.md` is **cfd's** territory and any gate text there is **theirs to write** — this charter binds the CLAIM, not their mesh gates.)*
> - **This is `§2bn` applied one level up, and the two clauses are one rule seen from two ends:** clause 7 was audited by the name of its function instead of by the property; a mesh was called 3D by its cell count instead of by its directions. **In both cases a cheap proxy stood in for the artifact that carries the property, and in both cases the proxy was wrong about a case that is about to be filmed.**

**Referred, not ruled here:** closure's two open items — that **"Navier-class" is undefined in `CASE_PROTOCOL_CHARTER`** (the charter's §0 scope line names it and no definition exists; that scope word governs which cases the protocol binds, so it is a real gap and it is **docketed**, not invented by this team), and that **L-525 / L-529 / L-530 owe executable checks.** Both are recorded at `D617`; neither is closed today.

### §2bp — **A THIRD MEASURED INSTANCE OF `§2bk.5`, AND IT ARRIVED INSIDE THIS TEAM'S OWN TASKING**

Recorded because the instance is unusually clean and because it cost nothing only by luck. This supervisor's brief for this session carried, as a measured live reading at 18:4xZ, *"`scripts/check_harness.py`: **FAIL: 2 problems** … `N-AV17` (ansys) and `N-D44` (dafoam) … missing from the index"*, and instructed: **route the two FAILs to their owners.**

**Re-derived by a lane in this session, run started 18:58:38Z: `PASS with 12 warning(s)`, rc 0, ZERO FAILs.** Cleared by **`d223a464c`, 2026-09-10T18:56:52Z** (dafoam), which appended a superseding `FAMILY INDEX` block — `44 insertions, 0 deletions`, `@@ -6796,3 +6796,47 @@`, **zero lines renumbered**, so nothing any frozen document cites by line moved.

**The figure was true when measured and false ~14 minutes later.** It is `§2bk.5`'s class exactly: a state reading, correctly taken, correctly reported, acted on after it decayed. **The cost it nearly incurred is the part worth recording: the routing would have woken the ansys team — stood down by the owner at 18:55Z — to fix an index row that a peer had already fixed three minutes earlier.** `§2bk.5`'s operational form held: the lane re-derived in the invocation that reported, and the stale instruction died there instead of in another team's inbox.

**And the lane's own planted-zero discipline is recorded as the model form of `§2bm`:** it reported `grep -c '^  FAIL '` = 0 **with** its positive controls on the identical corpus (`'^  WARN '` = 12, `'^  ok '` = 93), and named the trap it avoided — a naive `grep FAIL` returns **6** lines on that output, every one of them an `ok` or `WARN` row whose *document title* contains the word (`docs/FAIL_OPEN_GATE_AUDIT.md`). **A filter that matches the subject matter instead of the verdict is the false-zero's mirror image: a false NON-zero, and it would have manufactured four FAILs that do not exist.**

| amendment record | **v1.83** |
|---|---|
| clauses added | **3** (§2bn, §2bo, §2bp) |
| existing clauses **corrected** | **1** — `§2bl`'s finding is NARROWED (its clause name and its `K0` exculpation stand; its "dead lab-wide" reach does not) |
| gate values changed | **0** · verdicts withdrawn | **0** · verdicts newly alleged dirty | **0** · checks made to refuse | **0** (`D539`) |
| cases removed from a disclosure obligation | **1** (`K2bU3R3`, on measurement) |
| new instruments required by §2bo | **0** — `log.checkMesh` already exists in 1,112 places |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.84, 2026-09-10 — **§2bo.1 MY OWN CLAUSE OF TWELVE MINUTES AGO IS FACTUALLY INVERTED AND IS CORRECTED ON MEASUREMENT: A WEDGE READS `2 geometric` AND `3 solution`, NOT `3 geometric`. §2bo.2 THE CELL-COUNT RATIO FALSIFIES A 3D CLAIM FROM BOARD INTEGERS ALONE. §2bo.3 THE TWO NAMED PROTOCOL FRONTS ARE AXISYMMETRIC WEDGES**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **heat-transfer** against `§2bo` within twelve minutes of its commit (`a27b35511`); **re-measured at source by this supervisor before adoption**, and the measurement is against this team. `[lab-attributed]`. **No gate value moves; no verdict is withdrawn; nothing is made to refuse (`D539`).**

### §2bo.1 — **THE CORRECTION, STATED BEFORE ANYTHING ELSE, BECAUSE THE CLAUSE AS WRITTEN WOULD HAVE CERTIFIED A WEDGE AS 3D**

`§2bo` (v1.84's immediate predecessor, committed `a27b35511` at 19:14Z) wrote:

> *"`3 geometric` is necessary and not sufficient for the word '3D' in a demo caption. A wedge, a symmetry-plane sector or a single-cell-in-θ axisymmetric mesh **can read `3`** while being a 2D problem…"*

**MEASURED AT 19:21:11Z, on four independent wedge cases, each confirmed to carry `2` patches of `type wedge;` in `constant/polyMesh/boundary` — THAT SENTENCE IS BACKWARDS:**

| case | wedge patches | `geometric (non-empty/wedge)` | `solution (non-empty)` |
|---|---|---|---|
| `verification/runs/F23_HP_WEDGE_runs/fine` | 2 | **`2 … (1 1 0)`** | **`3 … (1 1 1)`** |
| `verification/runs/F28_runs/mesh_L2` | 2 | **`2 … (1 1 0)`** | **`3 … (1 1 1)`** |
| `verification/runs/T-family/T4e_runs/T4e_IJ_f` | 2 | **`2 … (1 1 0)`** | **`3 … (1 1 1)`** |
| `verification/runs/navier_class/SUBOFF/{reg_coarse,diag_medium_wp16}` | 2 | **`2 … (1 1 0)`** | **`3 … (1 1 1)`** |

**A wedge reads `2` on the `geometric` line and `3` on the `solution` line.** The `geometric` line is therefore not merely *preferred* — **it is the only one of the two that is correct about a wedge**, and the `solution` line, printed **one line away**, is the one that says `3` about an axisymmetric 2D problem.

> **§2bo IS CORRECTED, NOT NARROWED — the sufficiency sentence was FALSE and is REPLACED:**
>
> **THE LINE CITED IS `Mesh has N geometric (non-empty/wedge) directions`, BY THAT EXACT NAME, WITH ITS `(i j k)` TRIPLE. `N geometric == 3` WITH TRIPLE `(1 1 1)` IS THE TEST. THE `Mesh has N solution (non-empty) directions` LINE IS NOT THE TEST AND MAY NEVER BE QUOTED FOR A DIMENSIONALITY CLAIM: IT READS `3 … (1 1 1)` FOR AN AXISYMMETRIC WEDGE.**
>
> `§2bo`'s **core clause is unaffected and stands**: a dimensionality claim is READ from `checkMesh`, per mesh level, with its path; a cell count is not evidence; a `blockMeshDict` is not evidence. Only the sufficiency limb — which named the wrong line and the wrong number — is replaced. **The patch-type citation stands and is now doubly earned**: `2` patches of `type wedge;` is what distinguishes these four cases, and it is read from `constant/polyMesh/boundary`.

**AND THE FAILURE IS THIS TEAM'S OWN, IN THE EXACT SHAPE IT RULED AGAINST IN THE SAME COMMIT.** `§2bn`, twelve minutes old, says a proxy is not the property and a negative census is a hypothesis until each case is **opened**. `§2bo`'s sufficiency sentence was **reasoned from the parenthetical `(non-empty/wedge)`** — I read the words "wedge" inside the `geometric` line's own label and concluded that a wedge must therefore count as geometric. **The label describes what the line EXCLUDES, not what it counts.** I had six non-wedge logs in front of me and **zero wedge logs**, and I wrote the wedge sentence anyway.

**Worse, and recorded because it is the cleanest `§2bm` specimen this team has produced against itself:** the filter I used to look for a wedge case was `grep -q 'wedge' log.checkMesh`. It returned **399 of 400** logs — because **the standard `geometric (non-empty/wedge)` line contains the word `wedge` in every mesh OpenFOAM has ever checked.** My "wedge sample" was four non-wedge cases. **This is `§2bp`'s mirror-trap — a false NON-zero from a filter matching the subject matter instead of the property — committed by the supervisor who wrote `§2bp` in the same commit, forty minutes earlier.** The measurement that fixed it took one minute: census `type wedge;` in `constant/polyMesh/boundary`, which is **the artifact that carries the property**, and is what `§2bn` step 1 tells you to open.

### §2bo.2 — **THE FREE CROSS-CHECK: A REFINEMENT RATIO FALSIFIES A 3D CLAIM FROM BOARD INTEGERS ALONE**

Adopted from heat-transfer. It is arithmetic, not a measurement, and it needs no file:

> **A uniformly refined family at ratio `r` multiplies cells by `r³` in 3D and `r²` in 2D. At `r = 2`: 3D ×8, 2D ×4. At `r = 1.5`: 3D ×3.375, 2D ×2.25.**
>
> **A three-level family whose published cell counts step by ~4× or ~2.25× is NOT three-dimensionally refined, whatever the case is called** — and this is checkable from a board line, a docket row or a table in a report, with no access to the case. It is a **falsifier, not a certifier**: ~8× is consistent with 3D and does not establish it (a 2D family refined in one direction only, or a family refined anisotropically, can hit any ratio). **`§2bo.1`'s `geometric` line remains the test; this is the cheap screen that catches the claim before anyone opens a case.**

### §2bo.3 — **THE FINDING THIS PRODUCED, RECORDED PLAINLY BECAUSE IT BEARS ON WHAT IS FILMED**

**Both cases named as protocol fronts in `CASE_PROTOCOL_CHARTER` §7 are axisymmetric wedges. Measured by this supervisor at 19:21:11Z, not relayed:**

- **`T4e`** — heat-transfer's named front — `verification/runs/T-family/T4e_runs/T4e_IJ_f/`: **2 wedge patches**, `Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)`.
- **`SUBOFF`** — cfd's named front — `verification/runs/navier_class/SUBOFF/reg_coarse/` and `…/diag_medium_wp16/`: **2 wedge patches**, `Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)`.

**This team states what that does and does not mean, because the distinction is the whole value of the clause:**

- **It does NOT invalidate anything.** An axisymmetric wedge is a legitimate, standard, often *correct* discretisation, and every verdict on these cases stands exactly as graded. **No verdict is withdrawn and no case is alleged dirty** — this is `§2bl`'s discipline applied to a second finding in one day.
- **What it forbids is one sentence**: neither case may be described as a 3D case — in a caption, a board line, a report to the owner, or a demo — because `2 geometric (1 1 0)` is what its own mesh says. **`§2bo` binds the CLAIM.**
- **The routing is the chief's and is already in motion**; this clause exists so the wording is decided by measurement rather than by whoever writes the caption. `M6` has not solved. The 3D cases that DO read `3 geometric` are a separate list and each one owes its own citation under `§2bo` before it is captioned.

### §2bo.4 — **REFERRED UNDER `§2bn`, NOT ALLEGED: A `PASS` WHOSE GRADER A NAME CENSUS COULD NOT FIND**

A lane reports that **NASA CRM / DPW5**, carried on cfd's board as `PASS` on 4 gates at `verification/runs/RUNG2_CRM_runs/M2_snapshot_admission/B1`, has **no file matching `analyse_*.py` / `grade_*.py` / `score_*.py` anywhere under its run tree** — 0 of 3,675 files, with the directory proven readable by the same `find`.

**Under `§2bn`, decided forty minutes ago, THAT IS A HYPOTHESIS AND NOT A FINDING, and this team will not write it as one.** The census searched three **name patterns**; a grader under a fourth name satisfies the property and defeats the census — which is precisely the failure `§2bn` exists to prevent, and it would land here on another team's flagship filming case. **It is also, if true, exactly `§2w`'s class** (a landed verdict whose load-bearing gate was never implemented), which is why it may not be left unasked.

> **REFERRED TO cfd, as a question with a one-artifact answer: NAME THE ARTIFACT THAT ISSUED THE CRM `PASS`, by path.** Any answer closes it — a grader under an unmatched name (in which case `check_comparator_freeze.py`'s population, which keys on those three prefixes, **cannot see it and it has never been freeze-judged** — a real and separate defect), a shared module, or a hand-issued verdict. **This team asserts nothing about which.**

| amendment record | **v1.84** |
|---|---|
| clauses added | **2** (§2bo.2, §2bo.3) · referrals opened | **1** (§2bo.4) |
| existing clauses **corrected** | **1** — `§2bo`'s sufficiency limb was **FALSE** and is REPLACED (`§2bo.1`); its core clause stands |
| gate values changed | **0** · verdicts withdrawn | **0** · verdicts newly alleged dirty | **0** · checks made to refuse | **0** (`D539`) |
| cases whose DESCRIPTION is corrected | **2** (`T4e`, `SUBOFF` — wedges, not 3D) · cases whose VERDICT moves | **0** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.85, 2026-09-10 — **§2bq `Mesh OK.` FROM BARE `checkMesh` IS NOT A MESH VERDICT — THE TWO MOST DIAGNOSTIC CHECKS DO NOT RUN AT ALL. §2br A SCALE-INVARIANT GEOMETRIC DEFECT IS A MESH-*CONVERGENCE* DEFECT, AND IT IS THE ONE THAT WASTES A LADDER. §2bs M6CP1's EXHAUSTION EVIDENCE AND ITS NEWLY-FOUND CAUSE POINT IN OPPOSITE DIRECTIONS**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **cfd** from their M6 adjudication (5.38 core-min), against their own case and their own park. **The lab-wide mechanism was re-verified at source by this supervisor on an independent specimen before adoption**; cfd's case-specific integers are relayed and labelled as such. `[lab-attributed]`. **No gate value moves; no verdict is withdrawn; nothing is made to refuse (`D539`).**

### §2bq — **THE MOST-INVOKED GATE IN THE LAB REPORTS `Mesh OK.` WITHOUT RUNNING ITS TWO MOST DIAGNOSTIC CHECKS**

cfd's finding: bare `checkMesh` prints `Mesh OK.` where `checkMesh -allGeometry -allTopology` on the same mesh reports `Failed 2 mesh checks` — **the face-tet quality and cell-determinant (wellposedness) checks only execute under the flags.**

**RE-VERIFIED BY THIS SUPERVISOR ON AN INDEPENDENT SPECIMEN, 19:52:18Z, because a lab-wide clause may not rest on one team's case:**

- **Flagged** — `verification/runs/GEN_ALT_runs/alt_coarse/log.checkMesh`, run with `-allGeometry`: prints `Face tets OK.`, prints `Cell determinant (wellposedness) : minimum: 2.17584e-05`, finds `***Cells with small determinant (< 0.001) found, number of cells: 56`, and concludes **`Failed 1 mesh checks.`**
- **Bare** — `verification/runs/F27_NUMERICS_SUCCESSOR_R3_runs/coarse/log.checkMesh`: contains **neither** a `Face tets` line **nor** a `Cell determinant` line — the checks did not run — and concludes **`Mesh OK.`**

**The bare invocation does not FAIL the wellposedness test. It never TAKES it.** And `F27_NUMERICS_SUCCESSOR_R3` is a **three-level refinement family** — a mesh-convergence ladder — every level of which was admitted by a check that never ran.

**cfd's case-specific integers, RELAYED not re-measured (`§2bk`): M6CP1 L0 carries 332 low-quality tet faces and 656,877 under-determined cells behind a `mesh_ok: true` record.**

> **CLAUSE §2bq: `Mesh OK.` IS NOT A MESH-ADMISSIBILITY VERDICT. IT IS THE STATEMENT THAT THE SUBSET OF CHECKS THIS PARTICULAR INVOCATION RAN FOUND NOTHING — AND THE TWO MOST DIAGNOSTIC GEOMETRIC CHECKS ARE NOT IN THE DEFAULT SUBSET.**
>
> 1. **A mesh-admissibility claim CITES THE ARGV THAT PRODUCED IT**, exactly as `§2bo` makes a dimensionality claim cite the line it was read from. `checkMesh` is not one instrument; it is a family selected by flags, and naming the tool does not name the check.
> 2. **THE FREE DISCRIMINATOR, which needs no code and no re-run:** a `log.checkMesh` containing **no `Cell determinant` line** is a log in which the wellposedness check **did not execute**. Its `Mesh OK.` carries no information about determinant or face-tet quality. This is the same shape as the `worktree_differs_from_HEAD` discriminator ruled earlier today: **the absence of the line proves the absence of the check**, and it costs one `grep` on a file already on disk.
> 3. **cfd is landing the flags lab-wide and a feature-cells / wall-face-area-ratio limb; the mesh GATES are theirs and this clause does not write them.** Consistent with `§2bo`, this charter binds **the CLAIM** — what may be asserted, and on what evidence — and `docs/standards/MESH_STANDARD.md` remains cfd's to author. **The chief routed the standard's wording here; this team declines the wider half of that routing rather than take territory it published as cfd's four hours ago.**
> 4. **AND THIS IS THE THIRD INSTANCE OF ONE CLASS IN ONE DAY.** `§2bn`: a census measured the function NAME, not the property. `§2bo.1`: this supervisor quoted the WRONG LINE of `checkMesh` output. Now: the gate invoked the WRONG FORM of the right tool. **In all three the instrument ran, the token came back clean, and the check never happened. A PROXY IS NOT THE PROPERTY — and today the lab has paid for that sentence three times.**

### §2br — **A SCALE-INVARIANT GEOMETRIC DEFECT IS A MESH-*CONVERGENCE* DEFECT, AND THIS IS THE CLAUSE THAT SERVES THE LAB'S CURRENT PRIORITY**

cfd's second finding is the deeper one, and it is not about a flag: **a cusped trailing edge — 60.9° half-angle, ZERO CELLS ACROSS, scale-invariant under refinement — passes BOTH check sets.** (Geometry integers relayed from cfd, not re-measured here.) **So the gate is INSUFFICIENT as well as mis-invoked**, and no flag repairs that half.

**Why this belongs in the V&V charter and not only in a mesh standard.** The owner's stated priority, her words ~19:45Z today, is *"all these complicated cases run and complete, and wit their mes convergence ASAAAP … More than anything else."* **A feature with zero cells across it is resolved IDENTICALLY at every level of a refinement family.** Its contribution to the discretisation error **does not reduce as `h → 0`**. The level-to-level differences `e21` and `e32` are then contaminated by a term that is **constant across the ladder**, and the observed order fitted from them is **not an order of accuracy at all** — it is an artifact of a defect the refinement never touched.

**This is a direct, mechanical cause of `NOT A RESULT` under rule 5**, and it is the expensive kind: it consumes a full three-level ladder, produces a `STAGNANT`, `DEGENERATE` or `OSCILLATORY` triple, and **presents as a numerics problem while being a geometry problem.** A team reading only the triple's verdict will spend its escalation ladder on relaxation, schemes and pseudo-transient continuation, and none of them can move it.

> **CLAUSE §2br: A REFINEMENT FAMILY MUST BE SHOWN TO RESOLVE ITS NAMED GEOMETRIC FEATURES *BETTER* AT EACH LEVEL, AND THE EVIDENCE IS CELLS-ACROSS-THE-FEATURE PER LEVEL, CITED BESIDE THE CELL TOTALS.**
>
> - **A triple whose feature resolution is CONSTANT ACROSS LEVELS IS NOT A REFINEMENT FAMILY**, whatever its total cell counts do, and an observed order fitted on it may not be quoted.
> - **The check is pre-compute and nearly free**, and it belongs at protocol §1/§2, not at grading: for each feature the registration names (trailing edge, gap, fillet, boundary layer, wake), state the cells across it at L1/L2/L3. **A feature reading `0, 0, 0` — or `n, n, n` — disqualifies the ladder before a single core-minute is spent.**
> - **It composes with `§2bo.2`'s falsifier and answers a question that one cannot.** `§2bo.2` catches a family whose *totals* step wrong (~4× instead of ~8×). **This catches the family whose totals step perfectly and whose defect never shrinks** — the case that looks correct in every board integer and still cannot converge.
> - **Stated as guidance because it is what teams will actually hit tonight:** a low observed order is usually the instrument reporting that **you are not in the asymptotic range**. Before treating that as a numerics failure, check whether a named feature is scale-invariant. **If it is, the finer level is not finer where it matters.**

### §2bs — **M6CP1: THE EXHAUSTION EVIDENCE AND THE NEWLY-FOUND CAUSE POINT IN OPPOSITE DIRECTIONS, AND cfd FOUND THE DISQUALIFYING EVIDENCE THEMSELVES**

cfd's disposition, relayed: **M6CP1 `NOT A RESULT`, cause `ENERGY_RUNAWAY_TRAILING_EDGE`, three strikes under `CASE_PROTOCOL_CHARTER` §3.** Protocol §3 authorises exactly that — *"Three failures on the same cause: the case is parked as NOT A RESULT with the cause class and the three actions tried, the lesson is written, and the supervisor moves to the next case."* **The verdict is in the vocabulary, the cause class is named, and the park is procedurally correct on its face.**

**But `§2bc` (v1.74) governs a TERMINAL `NOT A RESULT` and it asks a different question:** such a verdict *"is not an acceptable terminal entry unless it carries exhaustion evidence proving the failure is not a fixable numerics or model/setup artifact."*

> **RULED: three strikes under §3 is exhaustion of the NUMERICS ladder. It is NOT exhaustion under `§2bc`, because cfd's own adjudication — in the same 5.38 core-min — produced AFFIRMATIVE EVIDENCE OF A FIXABLE SETUP ARTIFACT: zero cells across the trailing edge, at the exact feature the cause class names.**
>
> **This team asserts NO causal claim** — that the cusp *causes* the energy runaway is a hypothesis, and `§2bn` forbids this team from writing a hypothesis as a finding. **`§2bc` does not require causation. It requires that the failure be shown NOT to be a fixable setup artifact, and a feature the cause class names, carrying zero cells across it, is evidence in the opposite direction.**
>
> **THE PARK IS THEREFORE PREMATURE AND THE VERDICT IS ROUTED TO A DATED SUCCESSOR** (`§2bc`'s own remedy), **not withdrawn and not overturned.** The successor is a mesh with cells across the trailing edge. **M6 is not dead, and no one should report it as dead.**

**Said plainly because it is the part that generalises:** cfd ran the audit that disqualified their own park, disclosed it in the same report, and did so on the case the owner has asked for by name. **A team that hands its supervisor the evidence against its own terminus is the reason this charter can be strict without being adversarial.** The three strikes were spent on the numerics ladder while the mesh audit was still running; **that is a sequencing lesson, not a fault** — and `§2br` exists so the next ladder runs its feature-resolution check *before* its escalation ladder rather than beside it.

| amendment record | **v1.85** |
|---|---|
| clauses added | **3** (§2bq, §2br, §2bs) |
| existing clauses altered, widened or narrowed | **0** |
| gate values changed | **0** · verdicts withdrawn | **0** · verdicts overturned | **0** · checks made to refuse | **0** (`D539`) |
| verdicts ROUTED TO A DATED SUCCESSOR under `§2bc` | **1** (`M6CP1`) |
| mesh GATE text written by this charter | **0** — `MESH_STANDARD.md` remains cfd's |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.86, 2026-09-10 — **§2bt THE FOURTH INSTANCE OF ONE CLASS IN ONE DAY, AND THE MOST EXPENSIVE: THE FREEZE ENFORCER RECOGNISES A NOTATION, NOT A PROPERTY — 441 OF 515 REGISTRATIONS (85.6%) PIN ZERO BY ITS RECKONING, AND A HARD-WIRED GATE WOULD HAVE REFUSED THEM ALL TONIGHT. §2bu A PASS THAT DOES NOT DEPEND ON THE CASE IS NOT A PASS ABOUT THE CASE. §2bv THE `§2s.9.2` FAIL-OPEN FIRES AND DOES NOT PROPAGATE — THE WRAPPER IS STRICTLY SAFER THAN THE INSTRUMENT IT WRAPS**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Measured by a verification lane driving the instruments against live cases and against constructed negative controls; **≈9 core-min, single-rank, NON-SOLVER, $0.0077 derived** at $0.0513/core-h (derived from wall stamps, not read from a scheduler record — `COMPUTE_BUDGET_CHARTER` §5). `[lab-attributed]`. **No gate value moves; no verdict is withdrawn; NOTHING IS MADE TO REFUSE (`D539`), and this amendment's central holding is a REFUSAL TO WIRE ONE.**

### §2bt — **441 OF 515: THE RECOGNISER MEASURES A MARKDOWN NOTATION AND THE HOOK REPORTS IT AS "PINS ZERO EXECUTABLES"**

`scripts/check_comparator_freeze.py:261-262`, read as source:

```
PIN_PATH = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./+-]*\.(?:py|sh))`")
PIN_BLOB = re.compile(r"\b[0-9a-f]{40}\b")
```

`registered_pins()` (`:384`) requires **both, inside one markdown table row beginning `|`**. A registration that pins its comparator by **sha256** (64 hex — no word-boundary 40-hex substring), or names it in **prose** rather than a table row, yields **zero pins**; zero pins is `refuse()` at `:268`, relayed by the stage-1 hook at `:302` as exit 2.

**MEASURED corpus-wide, by importing the frozen module's own `registered_pins()` in-process — not by re-implementing it:**

| | |
|---|---|
| pre-registrations on disk | **515** |
| pin ≥1 executable by 40-hex git blob (the hook can pass them) | **74** |
| **pin ZERO → frozen check exits 2 → HOOK REFUSES** | **441 (85.6%)** |

By territory of the 441: **`cases/dafoam` 152**, `verification/campaign` 122, `cases/ansys_verification` 64, `docs/campaigns` 62, `cases/RANS_LES_closure_models` 35. Positive control that the recogniser is not simply returning empty on everything: the same call returns **18** for `K0h_PREREGISTRATION.md`, **10** for `M6SR`, **7** for `M6CP1`.

**The worked instance shows the notation is the whole difference, not the diligence.** `cases/dafoam/A2_B2R_INDEPENDENT_TRIM_PREREGISTRATION.md` **names its comparator** (`:56`, `cases/dafoam/grade_a2b2r.py:52`) **and carries hashes** (`:133` a sha256; `:366` a table row pinning the instrument by md5 **and** sha256, path absolute and outside the repo). **It is pinned by content, carefully, and the recogniser cannot see any of it.**

> **RULED — §2bt, and it is the FOURTH instance today of the class `§2bn` names: `§2bn` a census read a function NAME; `§2bo.1` this supervisor read the WRONG LINE; `§2bq` the gate ran the WRONG FORM of the right tool; and now THE FREEZE ENFORCER READS A MARKDOWN NOTATION AND REPORTS IT AS A FREEZE PROPERTY.**
>
> 1. **`pins ZERO executables` MEANS "NO PIN IN THE RECOGNISED NOTATION". IT DOES NOT MEAN "NOT FROZEN", AND IT MAY NOT BE WRITTEN, RELAYED OR BOARDED AS THOUGH IT DID.** That is `§2bn` step 3 exactly: an un-opened census is reported as a **bound**, in the sentence that carries it. **441 is a count of registrations the instrument CANNOT SEE. It is not a count of defects, and anyone converting it into one is manufacturing 441 false accusations.**
> 2. **`PIN_PATH` IS NOT WIDENED.** `check_comparator_freeze.py` is frozen, and widening what a gate accepts is a **gate change reserved to Sanaa** (`D539`, rule 9). The regex stays.
> 3. **THE FIX IS ON THE REGISTRATION SIDE AND IS FREE: new registrations pin their comparators in the recognised form** — a markdown table row carrying a backticked `*.py`/`*.sh` path **and** its 40-hex **git blob** sha. A sha256 of file content is a fine hash and is **not** a git blob; the instrument compares against `git rev-parse HEAD:<path>` and can only use the latter. **No existing registration is required to be rewritten, and none is alleged defective.**
> 4. **AND THE OPERATIONAL HOLDING THAT MATTERS TONIGHT: THE STAGE-1 HOOK IS NOT WIRED INTO ANY LAUNCH OR QUEUE PATH, AND THIS TEAM WILL NOT WIRE IT AS A HARD STOP.** Hard-wiring it unchanged **refuses 441 of 515 registrations**, with dafoam worst hit at 152. **That is not enforcement, it is a lab-wide outage** — on the night the owner's words are *"For now i want the RUNS"* and *"mes convergence ASAAAP … More than anything else"*. It would also violate `§2s.11` `[SANAA-RULED]` — *"A pre-registration mismatch never prevents a launch … Refusing to widen the gate was right; refusing to launch was the expensive part"* — and repeat `§2s.11.1`, this team's own recorded error of attaching a refusal where it was convenient rather than where it belongs.
> 5. **What the hook IS, and how it is used: an ON-DEMAND stage-1 exit check a team runs before it freezes.** Its verdicts on every live front driven tonight were **correct** — `M6CP1` PASS (7 pins judged, 0 unseen, reproducing the rc 0 cfd already had), `SUBOFF_R1b` and `SUBOFF_R1` PASS (3 judged, **1 unseen**, which is the positive control proving `pins_unseen` can be non-zero), `RUNG2_CRM_M2` PASS (3/0), and **TRUE REFUSALS on `T26`, `MRF_R1` and `A2_B2R`**, each of which genuinely carries no pin in the recognised form and two of which say so on their own face.

### §2bu — **A PASS THAT DOES NOT DEPEND ON THE CASE IS NOT A PASS ABOUT THE CASE**

`case_protocol_freeze_hook.py` uses `--case` at exactly three places: `:198` (basename → the printed label), `:202` (isdir), `:206` (repo discovery). **It is never compared against the registration.** Measured, both at 19:53Z:

```
--case cases/navier_class/SUBOFF --registration verification/campaign/M6CP1_PREREGISTRATION.md
   -> STAGE1 FREEZE PASS case=SUBOFF   pins_judged=7 pins_unseen=0 rc=0 reason=freeze-proven   exit 0
--case docs                     --registration verification/campaign/M6CP1_PREREGISTRATION.md
   -> STAGE1 FREEZE PASS case=docs     pins_judged=7 pins_unseen=0 rc=0 reason=freeze-proven   exit 0
```

**`docs/` is not a case at all.** The gate certifies *"M6CP1's registration is clean"* and prints it under whatever `case=` label it is handed. **No malice is required — a copy-pasted command line does it**, and a team whose own registration refuses can satisfy the gate by naming someone else's.

> **RULED — §2bu: this is `§2p`'s class ("a pass is evidence only if the run shows the pass could not have arisen from a degenerate path"), reached by a route `§2p` did not enumerate — not an instrument insensitive to its input, but an instrument whose PASS IS INDEPENDENT OF THE INPUT THE LABEL CLAIMS IT IS ABOUT. `§2p`'s free generator finds it in one line: hand the guard the WRONG case and see whether it notices.**
>
> **The remedy is a WARNING and explicitly NOT a refusal:** binding a registration to a case is a **new gate criterion**, and adding one is Sanaa's alone (`D539`). **Until then a `PASS` from this hook is admissible ONLY when the registration it names is the case's own, and that correspondence is asserted by the READER, not by the instrument.** Any record citing a stage-1 hook PASS states the registration path it was run against.

### §2bv — **THE `§2s.9.2` FAIL-OPEN FIRES, AND IT DOES NOT PROPAGATE — WHICH REVERSES THE ADVICE I GAVE FOUR HOURS AGO**

`§2s.9.2` and this team's own reading this afternoon held that `check_comparator_freeze.py:585` answers `FROZEN` when it could not check (`modified` stays `None` when `git cat-file blob` fails). **Constructed and driven on a throwaway repo — not on any repo case:**

| arm | condition | `commit_test` | pin limb | frozen rc | hook |
|---|---|---|---|---|---|
| E3a | clean | `FROZEN` | `PIN-OK` | 0 | **PASS** |
| E3b | worktree drifted | `MODIFIED_AFTER_COMMIT` | `PIN-DRIFT` | 3 | **REFUSE** |
| E3c | drifted **and HEAD blob object deleted** | **`FROZEN`** ← the fail-open fires | `PIN-DRIFT` | 3 | **REFUSE** |

**The fail-open is REAL and was made to fire on a genuinely drifted file. It cannot reach a hook PASS.** The hook hard-wires `--registration` and `--restrict-to-registration` (`:230-232`), so the population **is** the pinned set, and every row also gets a `pin_rows()` verdict (`:411-435`) whose identity test uses `git hash-object` and `git rev-parse HEAD:<rel>` — **neither touches `cat-file`**, so the pin limb is immune to the same failure and drift lands `PIN-DRIFT` → exit 3.

> **RULED, and it CORRECTS the reading rule this supervisor published earlier today: THE WRAPPER IS STRICTLY SAFER THAN THE INSTRUMENT IT WRAPS, AND THE EXPOSURE IS IN THE HAND-TYPED FORM.** Run `check_comparator_freeze.py` **by hand without `--registration`** and there are no pin rows at all — `:585` is then **the only identity test** and the fail-open is **fully live**. **So: invoke the freeze check THROUGH the hook, or with `--registration --restrict-to-registration`. A bare hand-run of the frozen checker is the exposed path.** The `worktree_differs_from_HEAD` discriminator published earlier stands and is now scoped: it is the tell for **that** hand-run form.
>
> **This is an argument for the hook's existence and NOT for wiring it as a stop** — `§2bt.4` governs that, unchanged.

**Two message defects recorded, both repairs designed and NEITHER MADE tonight** (a measurement-script change on the night three teams freeze is a risk this team declines to take at 20:00Z; both are additions to the *message* and *warning* streams and change no verdict): **(a)** `:245` prints the child's actionable `REFUSE:` line only under `--show-check-output`, so a refusal otherwise names no file and no reason — contrary to `CASE_PROTOCOL` §2's *"the failing check, the file, and the line are written to the record"*; **until repaired, `--show-check-output` is MANDATORY in every documented invocation.** **(b)** the `§2bu` warning. **`PIN_PATH` is NOT to be touched by anyone (`§2bt.2`).**

**One open shape this team could not close and will not paper over:** `PIN-ABSENT` is **not** in `PIN_VIOLATING` (`:263`). A registration pinning **two** files, one present and one absent, might escape the empty-population refusal while `PIN-ABSENT` stays non-violating. **That mixed case was NOT constructed. It is the one shape that could still pass vacuously, and it is named as unmeasured rather than assumed safe.**

| amendment record | **v1.86** |
|---|---|
| clauses added | **3** (§2bt, §2bu, §2bv) |
| existing readings **corrected** | **1** — this team's own fail-open advice of today is scoped to the hand-run form (`§2bv`) |
| gate values changed | **0** · gates wired | **0** · verdicts withdrawn | **0** · checks made to refuse | **0** (`D539`) |
| registrations alleged defective | **0** — the 441 is a bound on what the instrument can SEE |
| instrument edits made tonight | **0** (two designed, both deferred) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.87, 2026-09-10 — **§2bw RUN THE PLANT CHECK WITH NOTHING PLANTED; IF IT STILL SAYS GREEN IT IS NOT A PLANT CHECK — THE FIFTH INSTANCE TODAY, AND IT IS INSIDE THE RULE-3 INSTRUMENT ITSELF. §2bx M6CP1's STAGE-2 INSTRUMENT ARM IS `NOT A RESULT`; THE CANONICAL STAGE-2 CHECK IS NAMED. §2by CANONICAL IS NOT THE SAME AS MANDATORY, AND THE PLANT VOCABULARY DOES NOT FIT THIS LAB'S ARTIFACTS**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Measured by a verification lane driving all three stage-2 implementations against real graders, a purpose-built blind grader and a purpose-built sighted twin; **≈13 core-min single-rank NON-SOLVER, $0.011 derived** at $0.0513/core-h (derived, not measured — `COMPUTE_BUDGET_CHARTER` §5). `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`). ONE VERDICT COMPONENT IS DEMOTED, and it is named in full below.**

### §2bw — **THE CONTROL'S OWN CONTROL: A DETECTION PREDICATE MUST BE SHOWN ABLE TO RETURN RED ON A GRADER THAT IS PASSING**

`scripts/case_protocol_stage2_bugcheck.py:405-406` is the stage-2 instrument arm that **actually ran** in this lab. Read as source:

```
seen = (f"{PLANT:.3e}"[:5] in out) or ("PLANT" in out.upper())
```

and the `out` it tests comes from `[sys.executable, comparator, "--selftest"]` (`:405`) — **the comparator is run in its SELFTEST mode and is never handed the planted path.**

**MEASURED with NO PLANT ON DISK ANYWHERE, 19:55Z:**

| grader, run `--selftest`, nothing planted | `seen` |
|---|---|
| `cases/navier_class/SUBOFF/grade_suboff.py` | **True** |
| `cases/navier_class/MRF/grade_mrf_np.py` | **True** |
| `cases/F25_DUCT3D/grade_f25.py` | **True** |

**The predicate is not broken in the sense of never returning False** — control on the predicate itself: `"planted-zero control PASSED"` → True, `"value 1.2345 read"` → True, `"all gates green, nothing to report"` → **False**. **It can return red. It simply never does on a lab grader, because every lab grader's selftest banner prints the word "planted".**

> **RULED — §2bw: A PLANT CHECK IS VALID ONLY IF IT HAS BEEN RUN WITH NOTHING PLANTED AND RETURNED RED. That run is the control's own control, it costs one invocation, and it is now required of every detection predicate this lab writes or cites.**
>
> `CLAUDE.md` rule 3 says a zero from a reader not shown able to see a non-zero is not evidence. `§2bm` extended it to filters typed at a prompt. **This extends it to the DETECTOR: the positive control for a plant check is not "the plant landed on disk" — the instrument can verify that and still be measuring nothing. The control is "with no plant, the answer is NO."**
>
> **This is the FIFTH instance in one day of the class `§2bn` names, and the most pointed: `§2bn` a census read a function NAME; `§2bo.1` this supervisor read the WRONG LINE; `§2bq` the gate ran the WRONG FORM of the tool; `§2bt` the enforcer read a NOTATION; and now the rule-3 instrument reads THE WORD "PLANTED" IN A BANNER. Every time, the instrument ran, a token came back clean, and the check never happened.** It is also `§2p.3(d)` exactly — *a test that exercises a redundant copy of the guarded logic tests nothing* — reached here by running the guarded logic's **selftest** instead of the guarded logic.

### §2bx — **M6CP1's STAGE-2 INSTRUMENT ARM IS `NOT A RESULT`, AND THE CANONICAL STAGE-2 CHECK IS NAMED**

`verification/runs/M6CP1_runs/STAGE2_RECORD.json` carries three `instrument_perturbation_arm` rows, `green: true`, `comparator_saw_plant: true`, `planted_into: verification/runs/M6CP1_runs/L{0,1,2}/case/0/p`. The comparator was `verification/runs/M6_OWN_FAMILY_runs/analyse_m6_own_family.py`, which **contains the string `M6CP1` zero times** (positive control on the same file, same grep: `selftest` → 4), derives its own root from `_THIS` at `:81`, and **was handed no case path**. Run with nothing planted anywhere at 19:57Z, its `--selftest` prints `CONTROL C3 FIRED : planted 88.889 deg…` and `CONTROL C10 FIRED : planted 0.1234…`.

> **RULED: those three GREENs are evidence that a selftest banner contains the word "planted". They are NOT evidence that any reader saw the plant. Under `CLAUDE.md` rule 3 and `§2bw`, M6CP1's STAGE-2 INSTRUMENT ARM IS `NOT A RESULT` and must be re-run before that case's record is cited as §2-complete.**
>
> **STATED PRECISELY, BECAUSE THE SCOPE MATTERS AND OVER-READING IT WOULD BE ITS OWN DEFECT: M6CP1 IS NOT THEREBY UNSOUND. No gate value moves, no graded verdict is withdrawn, and the case is not alleged dirty.** What is demoted is **one arm of one stage-2 record** — the arm asserting a reader was shown able to see a perturbation. That assertion was never measured. It is `NOT A RESULT` in the strict sense: **nothing was measured, so there is nothing to fail.** M6CP1's separate disposition under `§2bs` — park premature, routed to a dated successor over the trailing edge — is unchanged, and **the successor now owes a real stage-2 as well as a resolved mesh.**

**CANONICITY, ruled on the measured difference and not on design preference:**

- **`scripts/check_instrument_detects_plant.py` IS THE CANONICAL STAGE-2 INSTRUMENT CHECK.** It invokes the reader through its **real production argv as a subprocess** (`:130-146`), plants into the caller's named artifact, judges on the reader's own `(rc, stdout, stderr)` changing (`:420`), keeps **four outcomes unmerged** (`DETECTED 0 / NOT-DETECTED 1 / COULD-NOT-RUN 2 / RESTORE-FAILED 3`), runs a **two-clean-run stability control** that routes drift to COULD-NOT-RUN (`:349-371`), restores bytes **and** mtime and verifies both (`:434-450`), and carries its own `--selftest` at 44/44. **It passes its own §2bw control by construction and by measurement:** a purpose-built blind grader scored **NOT-DETECTED (1)**, its honest twin **DETECTED (0)**.
- **`case_protocol_stage2_bugcheck.py`'s instrument arm (`:355`) MAY NOT BE CITED as a stage-2 instrument check** until its predicate is repaired. **Its `check_instrument_source` arm (`:313-354`) is a genuine capability the canonical instrument LACKS, is retained, and is called SEPARATELY — never merged into the plant verdict.** A source-defect scan and a plant check answer different questions and must not share a `green`.
- **`case_protocol_lib.py:907 planted_control` is dead code — 0 callers, and it demands four callables including the detection predicate from the caller.** It is not a third path.
- **A defect recorded against `(B)` beyond its predicate: COULD-NOT-RUN and NOT-DETECTED are MERGED.** "Comparator absent" (`:376`) and "no time dir carrying `p`" (`:388`) both emit `green: False`, the same machine-readable field a genuine blindness produces, and the roll-up at `:552` keys on exactly that field. **`§2bj` already ruled `INSTRUMENT REFUSAL` a cause class and not a verdict; this merges the two ends of that distinction back together.**

### §2by — **CANONICAL IS NOT MANDATORY: THE PLANT VOCABULARY DOES NOT FIT THIS LAB'S ARTIFACTS, AND SAYING SO IS THE HONEST ORDER OF OPERATIONS**

`plant_numeric` (`:213-247`) requires **a whole line that is one bare float** (`:197-211`: `float(ln.strip())` on the entire stripped line). **No OpenFOAM `postProcessing` `.dat` and no solver log has one**, so `--plant-mode auto` always falls through to `plant_append`, which adds a `PLANTED_PERTURBATION <v>` marker line. **Three real graders, three different consequences, all measured:**

| grader | outcome | mechanism |
|---|---|---|
| `grade_suboff.py` | **DETECTED (0)** | the marker parsed as a data row — **right answer, accidental mechanism** |
| `grade_mrf_np.py` | **DETECTED (0)** | the marker **crashed the tokeniser** — `ValueError: could not convert string to float: 'PLANTED_PERTURBATION'`. **A crash and a detection are indistinguishable to `fp != f1`** |
| `analyse_k2bU3.py` | **NOT-DETECTED (1)** | the marker matched no regex — **a FALSE NEGATIVE on a reader that is not blind** |

**The K2bU3 false negative was proven false by an in-format sweep on the same scratch log**: at plant `0.001234` the grader printed an identical line; at `0.01` it moved; at `1.0` and `5.0` it tracked exactly. **So a second, independent defect: the default plant `1.234e-03` is BELOW some readers' printed precision and is invisible even when planted correctly.** The instrument already guards this on the **input** side (`:243`, `PlantError("plant is swallowed at value…")`) and has **no equivalent guard on the output side**.

> **RULED — §2by:**
> 1. **A `DETECTED` obtained through `plant_append` on a multi-column `.dat` IS NOT A VALID STAGE-2 GREEN and may not be recorded as one.** Its mechanism is that the reader choked on, or coincidentally parsed, a foreign line. **Where no correct invocation exists, the case record states the §2 gap in words. It does not paste a green.** A convenient green is the thing this whole charter exists to refuse.
> 2. **`NOT-DETECTED` from `plant_append` is a HYPOTHESIS, not a finding** (`§2bn` again): before a reader is called blind, the plant is retried **in the artifact's own format and at a magnitude the reader can print.**
> 3. **THREE REPAIRS ARE SPECIFIED AND NONE IS MADE TONIGHT** — a measurement-script edit on the night three teams freeze is a risk this team declines at 20:10Z, and each is additive: **(a)** a `--plant-column N [--plant-row last]` mode adding the plant to whitespace-column N of the last non-comment row and verifying read-back — the shape `grade_suboff.coefficient_plant_control` (`:303-324`) and `grade_mrf_np._plant_into_moment_dat` (`:170-197`) **already implement independently**, so it is consolidation and not invention; **(b)** an **output-resolution guard**, the twin of `:243`, refusing COULD-NOT-RUN when the graded value's printed precision cannot represent the plant; **(c)** `--clean-rc auto`, taking the datum from the first clean run and requiring only that the two clean runs agree — **`--clean-rc` is currently the ONE argument that cannot be supplied without reading the grader's internals**, and there is no lab convention (`grade_suboff` returns 0 on a GATE FAIL, `grade_mrf_np` 3 on NOT A RESULT and 2 on a refusal, `analyse_k2bU3` always 0).
> 4. **Documentation defect, blocking and free to state:** argparse consumes a flag-shaped value, so **every flag-shaped reader argument must be written `--reader-arg=--coarse`**. Nothing in `--help` says so.
> 5. **Scope limits named rather than assumed away:** the canonical instrument grades a **`(reader, argv, artifact)` triple, not a reader** — the same grader measured `DETECTED` under one argv and `NOT-DETECTED` under another that never reached the artifact. It also has **no multi-artifact mode**, so a graded value reduced over many files can only be checked one file at a time. And it runs the reader **three times**, which on `F25` is a **>30-minute** stage-2 against `CASE_PROTOCOL` §2's *"under one minute"* — the `F25` verdict under the canonical instrument is **`PENDING`**, measured at 631 s for a single pass and killed before completion, **not** claimed either way.

| amendment record | **v1.87** |
|---|---|
| clauses added | **3** (§2bw, §2bx, §2by) |
| gate values changed | **0** · graded verdicts withdrawn | **0** · cases alleged dirty | **0** · checks made to refuse | **0** (`D539`) |
| **verdict COMPONENTS demoted to `NOT A RESULT`** | **1** — M6CP1's stage-2 instrument arm (3 rows), NOT the case |
| canonical instrument named | **1** · implementations retired | **1** (`planted_control`, 0 callers) · arms retained separately | **1** (`check_instrument_source`) |
| instrument edits made tonight | **0** (four specified, all deferred) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.88, 2026-09-10 — **§2bz THE LAB'S 3D PROBLEM IS NOT MESH CONVERGENCE: NOT ONE 3D TRIPLE HAS EVER FAILED ON THE GRID STATE. §2ca PRD — 1,107.7 CORE-MIN OF FINISHED 3D COMPUTE IS UNGRADED BECAUSE A PLATEAU TOLERANCE SITS BELOW ITS OWN MONITOR'S NOISE FLOOR. §2cb THREE INSTRUMENT FINDINGS, REPORTED AND NOT CHANGED**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Measured by a verification lane over 4,164 JSON artifacts, 139 structurally-detected level families and 128 graded triple rows, with three independent censuses (by identifier, by content, by property) each carrying its positive control; **≈8 core-min single-rank NON-SOLVER, $0.0068 derived**, no solver launched, no repo file written. `[lab-attributed]`. **No gate value moves; no verdict is withdrawn; nothing is made to refuse (`D539`).**

### §2bz — **THE DIAGNOSIS, AND IT REDIRECTS THE LAB'S CURRENT PRIORITY**

The owner's words ~19:45Z: *"all these complicated cases run and complete, and wit their mes convergence ASAAAP … More than anything else."* **The measurement says the obstacle is not where the phrase points.**

Aggregate over 128 graded triple rows: **CONVERGING→PASS 41 · CONVERGING→GATE FAIL 12 · limb (1) 21 · DIVERGENT 6 · STAGNANT 4 · OSCILLATORY 3 · DEGENERATE 1 · state unprinted 5.** Failed triples 40; **limb (1) = 21 (52%)**, limb (2) = 19 (48%).

**Restricted to 3D / Navier-class the picture is absolute:**

| bucket | 3D instances |
|---|---|
| CONVERGING | 6 (F25 ×2, F27-R3 ×2, F27-R2 ×2) |
| **limb (1) — iterative/plateau kill** | **8** (F27_WOMERSLEY ×2, SUBOFF-R1b, **PRD ×5**) |
| level never completed | 2 (VMFL072-R3 `rc=136` SIGFPE at L3; M6_OWN_FAMILY L2 failed all 7 rule-4 clauses, L3 never built) |
| never solved, stopped at mesh | 5 (M6I, M6SR, RUNG1_M6_R2, A1WR, DRIVAER) |
| **limb (2) alone, 3D** | **ZERO** |

> **RULED — §2bz: NOT ONE 3D TRIPLE IN THIS LAB HAS EVER BEEN KILLED BY ITS GRID STATE. Every 3D triple that failed, failed at limb (1) or earlier — a level that did not iteratively converge, did not plateau, crashed, or was never solved. THE BOTTLENECK IS THAT A LEVEL IS NEVER ALLOWED TO FINISH, AND WORK AIMED AT MESHES IS AIMED PAST THE PROBLEM.**

**AND THE `F25`-IS-THE-ONLY-ONE CLAIM IS REFUTED.** `docs/LAB_STATE.md:31544` and `:31565` read *"the lab's ONLY CONVERGING 3D triple"*. **Measured: three cases, six triples** — `F25_DUCT3D` (p = 1.9529 / 1.9698, PASS ×2), `F27_NUMERICS_SUCCESSOR_R3` (2.0327 / 2.2738, PASS ×2), `F27_NUMERICS_SUCCESSOR_R2` (2.0671 PASS / 1.2718 GATE FAIL). Both F27 roots are genuinely 3D **checked from the mesh, not the label** (`§2bn`): `constant/polyMesh/boundary` carries 2 × `cyclic` + 1 × `wall`, **no `empty`, no `wedge`** — identical topology to F25's.

> **THE HONEST HEADLINE, AND IT IS THE SENTENCE THAT SHOULD REACH THE OWNER: the lab holds THREE converging 3D grid triples, and ALL THREE ARE STREAMWISE-CYCLIC LAMINAR / ANALYTIC CODE-VERIFICATION CASES AT r = 2. THE LAB HOLDS ZERO CONVERGING 3D TRIPLES ON A TURBULENT OR EXTERNAL-AERODYNAMIC CASE.** Correcting "one" to "three" without that second sentence would be a truer number and a worse report.

**Two caveats carried up rather than buried:** F25 row 0 reports **GCI = 129.33 %**, F27-R3 row 0 **109.88 %**, F27-R2 row 0 **71.70 %**. These pass their pre-registered bands — the band is on the fine value and `GCI_pct` divides by `f_fine ≈ 7e-4`, so `GCI_abs` (9.60e-4 / 5.87e-4 / 5.22e-4) is the honest figure. **Not a defect, and "PASS with 129 % GCI" is what a reviewer sees**, so it is said here first.

### §2ca — **PRD: FIVE 3D TRIPLES, FIFTEEN COMPLETED SOLVES, 1,107.7 CORE-MIN SPENT, AND NO GATE HAS EVER BEEN EMITTED**

`verification/runs/navier_class/PRD/_scheduler.log` final line: `ALL 15 solves FINISHED; core_min=1107.7; scheduler EXIT; … autograder grades when all plateaued -> …/gate_prd_e1.json`. **That file does not exist.** `autograde_prd.watch.log` was still spinning at 19:47Z — `cases=15 ready=False`, 9 of 15 levels `NOT_PLATEAUED`. **The autograder has been polling a finished job for fourteen hours.**

**All fifteen solves ran their full 3,000 iterations, wrote `End`, and reached final initial residuals of order 1e-7** (e.g. `us4.00_L1/log.simpleFoam`: `Solving for k, Initial residual = 2.2959527e-06 … ExecutionTime = 168.59 s … End`). `iterative_state` is `CONVERGED` everywhere. **The block is the plateau limb alone**, and the failing levels miss `PLATEAU_REL_TOL = 1.0e-4` by factors of **1.8× to 23×** — recomputed from the raw `surfaceFieldValue.dat` monitors by re-implementing the grader's own `plateau_state` exactly, not by re-reading its output.

> **RULED — §2ca.1: A PLATEAU CRITERION WHOSE TOLERANCE IS TIGHTER THAN ITS OWN MONITOR'S CONVERGED RIPPLE IS NOT A CONVERGENCE TEST — IT IS A TEST THAT NO CONVERGED RUN CAN PASS.** The area-averaged inlet Δp carries a bounded ~0.1–0.2 % oscillation the residual norm does not see. **The remedy is a pre-registration amendment (a windowed MEAN rather than a max-deviation, a tolerance defensible from the measured ripple amplitude, or a monitor with a lower noise floor) — and the compute is ALREADY SPENT, so RE-GRADING IS FREE AND RE-RUNNING IS NOT.** This is cfd's registration and cfd's amendment to make; this team rules the principle, not their threshold.

> **§2ca.2 — THE HARDER FINDING UNDERNEATH, AND IT GENERALISES TO EVERY LOW-MACH INTERNAL-FLOW INTEGRAL THIS LAB GRADES. PRD's level-to-level spread is 0.03–0.2 % — THE SAME ORDER AS THE ITERATION RIPPLE THAT IS BLOCKING THE PLATEAU TEST. THE GRID SIGNAL HAS FALLEN BELOW THE ITERATIVE NOISE FLOOR.** Even with the plateau limb repaired, **at best 1 of 5 PRD triples would read CONVERGING** *(INFERRED — the lane's own Roache arithmetic on the last monitor write; `analyse_prd.py` may reduce the series differently. **VERIFY before this figure is quoted upward.**)*
>
> **The rule that follows is general and is not about PRD: A REFINEMENT FAMILY WHOSE LEVEL-TO-LEVEL DIFFERENCE IS THE SAME ORDER AS ITS OWN ITERATIVE RIPPLE CANNOT PRODUCE AN OBSERVED ORDER, AND NO PLATEAU TOLERANCE REPAIRS THAT.** `CASE_PROTOCOL` §5 already asks that *"iterative error is verified at least ten times smaller than the level-to-level difference"* — **that ratio is the test, it is computable BEFORE the ladder is graded, and PRD fails it.** Where it fails, the ladder needs a coarser base or a quantity with more grid sensitivity, not a looser gate.

### §2cb — **THREE FINDINGS IN THE SHARED INSTRUMENT. REPORTED. NOT CHANGED.**

`scripts/roache_triple.py` is sound in its guarded core — a reversed ladder REFUSES (`r <= 1.0`), no `ast.Assert` survives, `main` refuses under `python3 -O`, `_seal` structurally re-checks that no GCI escapes beside a non-monotone or non-CONVERGING row, and `band_verdict` grades the **fine value** and never the extrapolate. Three findings stand against it, and **none is repaired here, because two are thresholds and a threshold change escalates to Sanaa.**

1. **`STAGNANT_FLOOR = 0.5` IS A HARD CLIFF AND THE LAB IS SITTING ON IT.** Measured live specimens straddling it: **failing** — `T23G` p = 0.3744 / 0.3766 / 0.3796; `gate_t1b_L4` p = 0.3790 … 0.4350 (seven rows); `gate_t9aD` p = 0.1305; K0cX `Nu_avg` p = 0.1065. **Passing** — `gate_t3c` p = **0.5100**, clearing the floor **by 0.010**, and `gate_t3g` p = 0.5100. **A constant taking its provenance from `T1c:321` is deciding live verdicts by 1 % margins.** That is not a bug and it is more work than the provenance can carry. **Recorded for Sanaa's desk as a threshold question; NOT adjusted, and no verdict moves on it today.**
2. **THE `OSCILLATORY` TEST PRECEDES THE `DEGENERATE` GUARD, SO "FLAT TO ROUNDOFF" IS REPORTED AS "NOT MONOTONE".** Order is `EXACT` → `e32/e21 < 0 → OSCILLATORY` → `|p| < P_MIN → DEGENERATE`. The docstring's item 5 guards the **same-sign** roundoff case; the **opposite-sign** case never reaches it. **Both land `NOT A RESULT`, so NO VERDICT FLIPS** — but the emitted `why` says *"the three values are not monotone"* when the truth is *"the three values are identical to within noise"*, **and a team reading `OSCILLATORY` will go hunting a physical oscillation that does not exist.** PRD `us1.00` and `us4.00` are exactly this shape (spread 0.085 % and 0.15 %, sign chosen by ripple). **A diagnosis that sends a team after a phantom is a real cost even when the verdict is right.** Referred as a `why`-string repair, which changes no state and no exit code.
3. **`p` IS PROPORTIONAL TO `dim`, AND NOTHING CROSS-CHECKS A GRADER'S DECLARED `dim` AGAINST ITS MESH.** Since `r = (N_f/N_c)^(1/dim)`, `p = dim · ln|e32/e21| / ln(N_f/N_c)`. **Declaring a 3D case `dim = 2` multiplies the reported order by 2/3 — enough to drive a genuine p = 0.72 to 0.48 and turn `CONVERGING` into `STAGNANT` against finding 1's cliff.** The module refuses a **missing** `dim`; it cannot verify a **wrong** one. **This is `§2bo`'s clause with teeth: the mesh already states its own dimensionality in `log.checkMesh`'s `geometric (non-empty/wedge)` line, and a cheap instrument could compare it to every grader's declared `dim`. THIS TEAM OWNS THAT INSTRUMENT AND IT IS THE NEXT THING THIS TEAM BUILDS** — it is a `§2bo` reader, not a new gate, and it refuses nothing.

**Three items referred, none ruled here:**
- **`MRF` IS SOLVING RIGHT NOW AGAINST AN EXPLICITLY UNFROZEN PRE-REGISTRATION.** `verification/campaign/MRF_R1_PREREGISTRATION.md:3` reads `**STATUS: DRAFT / UNFROZEN. NO COMPUTE HAS RUN. NOT A GATE YET.**` while `fine/` carried an mtime of 19:49Z. **That is a standing-rule-2 exposure (freeze before compute) and it is cfd-supervisor's check 4. Referred, not acted on** — and named plainly because rule 2's freeze is the entire evidentiary content of a pre-registration.
- **`SUBOFF` R1b carries TWO contradictory verdict artifacts on disk, unreconciled by any record found**: `VERDICT.R1b_triple.txt` = `NOT A RESULT / grade_suboff.py REFUSED (exit 2)` because **the launcher invoked the grader with no arguments**, and `grade.R1b_triple.REPAIRED.out` = `NOT A RESULT` on limb (1). Same verdict, two entirely different reasons. **Referred to cfd to reconcile.** (Its underlying physics is not a grid question at all: CT = 0.011283 → 0.339200 → **4.732715** against a reference of 0.0036 — the fine level is **1,315×** the reference and residuals **rise** with refinement, on a clean r = 1.5 family. **The meshes are innocent.**)
- **Two live 3D families are built on a 2D refinement step** — `VMFL072-R2/R3` and `M6SR`, both stepping **4.000 / 4.000** on 3D meshes (implied 3D r = 1.587), so `§2bo.2`'s falsifier fires and **no observed order from either family is interpretable**. And `A1WR` is **not 3D at all**: `STAGE0.log` records `symmetry1 nFaces=130304` with 130,304 cells — **nFaces == nCells, one cell thick**, classified 3D only because it uses `symmetry` rather than `empty` patches. **A structural detector called it 3D and was wrong; opening it corrected that — `§2bn` step 1, working as intended.**

| amendment record | **v1.88** |
|---|---|
| clauses added | **3** (§2bz, §2ca, §2cb) · referrals opened | **3** |
| gate values changed | **0** · thresholds adjusted | **0** (one recorded for Sanaa) · verdicts withdrawn | **0** · checks made to refuse | **0** (`D539`) |
| board claims REFUTED | **1** (`F25` "only converging 3D triple" — three cases, six triples) |
| instruments this team commits to BUILD next | **1** (declared-`dim` vs `checkMesh` cross-check) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.89, 2026-09-10 — **§2cc THE CORPUS IS THE OTHER HALF OF A CENSUS, AND IT IS THE HALF NOBODY STATES. §2cd THE CRM REFERRAL IS CLOSED AND MY OWN CONDITIONAL WAS WRONG — THE INSTRUMENT IS EXONERATED. §2ce THE `motorBike`: A CORRECTION THAT MAY HAVE WITHDRAWN A TRUE SENTENCE, AND THE HONEST ANSWER TO A CASE THE OWNER ASKED FOR BY NAME**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **cfd**, three items, two against themselves. **Every load-bearing claim re-measured at source by this supervisor**, and one of them does not survive. `[lab-attributed]`. **No gate value moves; no verdict is withdrawn; nothing is made to refuse (`D539`).**

### §2cc — **`§2bn` HAS A SECOND AXIS: THE FILTER CAN BE PERFECT AND THE CORPUS STILL WRONG**

`§2bn` ruled that a census by identifier measures the identifier. **Today produced a second, distinct mechanism with the same signature: a correct filter run over the wrong roots.** The output is indistinguishable — a confident zero that reads as a finding — and the remedy is different, so it needs its own statement.

**Measured instances, today:**

1. **The CRM "missing grader"** (`§2bo.4`, opened by this team four hours ago): the census walked the **run tree**; the grader lives under **`cases/`**. Filter correct, corpus wrong.
2. **DrivAer, CONFIRMED at source by this supervisor at 20:20:15Z:** `/home/ubuntu/certonomous-runs/navier_class/DRIVAER/drivaerml_r7a5c094/run_466/drivaer_466.stl`, **136 MB**, present — and rowed as *"no STL on disk"*. The tree is **enumerated in `docs/LOCATIONS.md`**; it is simply **outside git**, so a tracked-path census cannot see it.
3. **This supervisor, twice more, in the last ten minutes.** Searching for the motorbike I ran `find … -path '*otorbike*'` — **case-sensitive** — and got zero. The case is **`motorBike`**, capital B. `-iname` found it instantly. **That is my third false zero today, and it came twenty minutes after I ruled on the class.**

> **CLAUSE §2cc: A CENSUS IS DEFINED BY ITS CORPUS AS MUCH AS BY ITS FILTER, AND THE CORPUS IS THE HALF NOBODY WRITES DOWN.**
>
> 1. **EVERY NEGATIVE CENSUS STATES THE ROOTS IT WALKED**, in the sentence that carries its zero. "No grader exists" is not a finding; "no file matching `grade_*` exists **under `verification/runs/<case>/`**" is.
> 2. **THE ROOTS ARE CHECKED AGAINST `docs/LOCATIONS.md` BEFORE THE ZERO IS BELIEVED.** That file exists precisely because data too large for git lives outside it, and it **enumerates those trees**. A census that has not consulted it has not established its own scope. **Nothing is invisible merely because it is big — and nothing is absent merely because it is untracked.**
> 3. **CASE-SENSITIVITY IS PART OF THE FILTER.** `-path` and `grep` are case-sensitive; `-iname` and `grep -i` are not. **A zero from a case-sensitive filter over lab paths is not a measurement**, because this lab's directories carry mixed case (`motorBike`, `K0cX`, `T4e_IJ_m`).
> 4. **`§2bm`'s positive control does not catch this and must not be trusted to.** A positive control proves the filter can return non-zero **within the corpus it was pointed at**. It says nothing about a corpus that was never walked. **These are two independent failures and each needs its own check.**

### §2cd — **THE CRM REFERRAL IS CLOSED, THE HYPOTHESIS IS DISCONFIRMED, AND THE CONDITIONAL I ATTACHED TO IT WAS FALSE**

cfd's answer: the grader is **`cases/committee-grids/grade_r2_m2.py`** at `a2996ed07`; its name **matches `grade_*`**; its **sha256 and blob match the pre-registration pins**. **The referral is answered by exactly the one-artifact answer it asked for, and `§2bn`'s discipline is vindicated: this team wrote it as a hypothesis, and the hypothesis was wrong.**

**AND THE CORRECTION THIS TEAM OWES RUNS AGAINST ITSELF.** `§2bo.4` attached a conditional: *"if it is a grader under an unmatched name, `check_comparator_freeze.py`'s population keys on those three prefixes and cannot see it — a real and separate defect."* **Read at source at 20:20:15Z, `scripts/check_comparator_freeze.py:55-70`, verbatim: `"verification/, cases/ and docs/campaigns/ are walked, and the grader name patterns are analyse_*.py, grade_*.py and score_*.py."`**

> **The name matches AND the location is inside the walked population. THERE IS NO SEPARATE DEFECT, the instrument is EXONERATED, and my conditional would have libelled it.** Those same lines record that the `cases/` root was added **because** walking `verification/` alone left eleven graders uncovered — **the instrument had already been repaired for exactly this class before I speculated about it.** *(One nuance preserved rather than smoothed: cfd cite those lines as documenting a live gap; read in full they document a gap that was **closed**. The distinction matters, because a closed gap cited as open becomes a defect nobody can fix.)*

**The one real finding inside cfd's answer stands, and it is a recording defect, not a gate defect:** *"PASS on four gates"* is an artifact — **G4 runs and passes, but is printed only on the selftest branch and never persisted to `STATUS`**; 15/15 controls re-derived.

> **RULED: a gate that fires, passes, and is NEVER PERSISTED did not happen for the record's purposes, even though it happened in the process.** The record is what a future reader has. **This is the mirror of `§2aj`** — that clause caught a selftest that never reaches the emission path; **this is an emission that exists ONLY on the selftest path.** No verdict moves: the gate genuinely passed. **What is owed is that the record say four gates ran and three were persisted, or that G4's result be written where the other three are.** cfd's to land.

### §2ce — **THE `motorBike`: I RE-MEASURED cfd's CORRECTION AND IT DOES NOT SURVIVE — WHICH IS WHY I STATE IT AS A HYPOTHESIS AND NOT A CHARGE**

cfd's item (2) pairs DrivAer with a second instance: the motorbike *"rowed as 'no solve log' (log.simpleFoam present)"*. **DrivAer is confirmed (§2cc.2). The motorbike half is not.**

**Measured at 20:26:51Z with a CASE-INSENSITIVE, WHOLE-TREE filter carrying its positive control** — `find /home/ubuntu/certonomous-runs -ipath '*motorbike*' -iname 'log.*'` returns **exactly three files**: `validation-scratch/motorBike/log.checkMesh`, `…/log.yPlus`, `…/log.yPlus2`. Positive control on the identical filter: `-iname 'log.checkMesh'` returns that file, so the filter sees. **`study-motorBike-f8b4a2/` carries NO `log.*` at all** (it holds `0`, `0.orig`, `300`, `VTK`, `postProcessing`, 16 `processor*` dirs, `Allrun`, `illegalFaces`). **`.solve-cache/motorBike-c353688-i300/` holds `300/`, `DONE` and `postProcessing` — results, and no log.**

> **THERE IS NO SOLVE LOG FOR THE motorBike ANYWHERE IN THAT TREE BY MY CENSUS. cfd's ORIGINAL ROW APPEARS TO HAVE BEEN CORRECT, AND THE CORRECTION APPEARS TO HAVE WITHDRAWN A TRUE SENTENCE — which is `§2n.19`'s ruled class, OVER-CORRECTION IS A RECORD DEFECT, arriving today from the other direction.**
>
> **STATED AS A HYPOTHESIS AND NOT A FINDING, BY MY OWN `§2bn` AND MY OWN `§2cc`, BECAUSE I HAVE JUST BEEN WRONG TWICE ON THIS EXACT CASE:** cfd may hold a location my roots did not cover. **The question has a one-artifact answer: name the path of the `log.simpleFoam` you found.** If it exists, my census was corpus-blind — the very defect this amendment rules on — and I will say so.

**AND THE PART THE OWNER ASKED FOR, ANSWERED HONESTLY.** She asked *"how about b-52 and motorbyke etc"*. Measured:

- **A genuinely 3D motorBike mesh exists** — `validation-scratch/motorBike/log.checkMesh`: **`Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)`, 353,688 cells.** Cited under `§2bo`, from the `geometric` line, per level, with its path.
- **Results exist** — a `300/` time directory, `postProcessing`, VTK, and a `DONE` marker in the solve cache.
- **AND IT CANNOT BE CERTIFIED.** Standing rule 4 requires `rc = 0`, an `End` line, last time == `endTime`, an `ExecutionTime` count and the age guard — **every one of which is read FROM THE SOLVE LOG.** With no log, **none of the five can be evaluated**, and the case is `NOT A RESULT` in the strict sense: **not failed — unevaluable.**
- **`study-motorBike-f8b4a2/` cannot even carry a `§2bo` dimensionality claim**, because it has no `log.checkMesh` of its own. Its boundary file shows zero `wedge`/`empty` patches, **which is a proxy and is exactly what `§2bo` forbids citing.**

> **THE HONEST LINE: the lab has a solved 3D motorBike on disk that it cannot certify, because the artifact rule 4 reads is missing. That is a recoverable position — the case is cheap and re-runnable WITH its log — and it is not a result today.** The same question should be put to the B-52 before anyone reports on it.

| amendment record | **v1.89** |
|---|---|
| clauses added | **3** (§2cc, §2cd, §2ce) · referrals CLOSED | **1** (`§2bo.4`, CRM) · hypotheses opened | **1** (the motorBike log) |
| **this team's own claims corrected** | **1** — `§2bo.4`'s conditional was FALSE; `check_comparator_freeze.py` is EXONERATED |
| this supervisor's false zeros today | **3** (two ruled on earlier; the third made AFTER the ruling) |
| gate values changed | **0** · verdicts withdrawn | **0** · cases alleged dirty | **0** · checks made to refuse | **0** (`D539`) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.90, 2026-09-10 — **§2cf A LOAD AVERAGE IS NOT A CPU MEASUREMENT, AND TONIGHT IT IS WRONG BY TWO ORDERS OF MAGNITUDE — MY OWN CENSUS DISCIPLINE IS PART OF THE CAUSE. §2cg MRF IS EXONERATED: MY RULE-2 FLAG OF THIRTY MINUTES AGO IS WITHDRAWN ON MEASUREMENT. §2ch A `DRAFT / UNFROZEN` BANNER ABOVE A FREEZE BLOCK IS A RECORD DEFECT, AND STRIKING IT IS PART OF FREEZING**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by the **chief** (§2cf) and **cfd** (§2cg, §2ch). **Measured at source by this supervisor at 20:34:42Z.** `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`). ONE ACCUSATION BY THIS TEAM IS WITHDRAWN.**

### §2cf — **LOAD 63 ON A BOX WHOSE CPU PRESSURE IS 0.93 %**

**Measured in one invocation at 20:34:42Z:**

```
/proc/pressure/cpu   some avg10=1.17  avg60=1.09  avg300=0.93   full avg300=0.00
/proc/pressure/io    some avg10=74.98 avg60=75.02 avg300=77.99  full avg300=43.24
/proc/loadavg        63.17 55.63 46.93
```

> **The box is reporting a load of 63 on 16 vCPU while CPU pressure is UNDER ONE PERCENT. `io full avg300 = 43.24` means that for 43 % of the last five minutes EVERY runnable task was stalled on IO. The load average is essentially all D-state waiters, and as a signal of CPU availability it is wrong by nearly two orders of magnitude.**

**RULED — §2cf: A LOAD AVERAGE IS NOT A MEASUREMENT OF CPU AVAILABILITY AND MAY NOT BE USED ALONE TO JUSTIFY A SCHEDULING DECISION. IT IS READ BESIDE `/proc/pressure/{cpu,io,memory}`, AND THE FIGURE THAT DECIDES WHETHER A SOLVER CAN LAUNCH IS `pressure/cpu`, NOT `loadavg`.** Linux load counts uninterruptible-sleep tasks, so **an IO-starved box misreads as CPU-contended, and the wrong action follows: launches get sequenced or refused on a box with idle CPUs.** `MONITOR_STANDARD.md`'s text is not this charter's to write; **the measurement rule is, and this is it.**

**AND THE RETROSPECTIVE MATTERS, BECAUSE IT REOPENS `§2bk.5`.** That clause recorded cfd refusing to launch a sixth solver on a stated *"load 45.85"*, later re-derived at 3.96, and ruled it a **staleness** failure. **Tonight's measurement supplies a second, independent reason the same decision was unsound: even when a high load reading is CURRENT, it may not mean what the decision assumed.** `§2bk.5` stands and gains a limb: **a figure can be fresh, correctly measured, and still not be the quantity the decision needs.** Freshness and validity are different properties and this lab has now paid for both.

**THE PART THAT IS MINE, AND I STATE IT FIRST BECAUSE IT IS UNCOMFORTABLE.** Four repo-wide `ugrep`/`find` sweeps were live at the reading. **My own lane briefs ordered disk-wide censuses in as many words** — *"census the DISK (find) as well as git"* — and `§2cc`, which I ruled forty minutes ago, makes that discipline **binding lab-wide**. **The discipline is right and its cost is real: a corpus-complete census is IO-heavy, and tonight it was taxing the solvers on the night the owner asked for runs.**

> **§2cf.1 — THE OPERATIONAL RULE THAT PAYS FOR `§2cc`: A CORPUS-COMPLETE CENSUS IS AN IO-EXPENSIVE MEASUREMENT AND IS SCHEDULED LIKE ONE.**
> - **While solvers are running: no repo-wide `grep -r` and no unbounded `find`.** Use `git grep` **with a pathspec**, or `find` with an explicit root and `-maxdepth`.
> - **Never walk `processor*/`, `VTK/`, `postProcessing/` or a time-directory tree with a text search.** They hold the overwhelming majority of the bytes and essentially none of the answers.
> - **A census that must be corpus-complete runs when the box is not solving**, and says in its report when it ran.
> - **`§2cc` is NOT relaxed** — a zero from a narrowed corpus is still a bound and still states its roots. **What changes is WHEN the wide census runs, never whether its scope is disclosed.**

### §2cg — **MRF IS EXONERATED. MY RULE-2 FLAG IS WITHDRAWN, THIRTY MINUTES AFTER I MADE IT.**

`§2cb` referred *"MRF is solving RIGHT NOW against an explicitly unfrozen pre-registration"* as a standing-rule-2 exposure. **cfd's timing, and it disposes of it: freeze `20:02:01Z`, first solver write `20:26:12Z`. The freeze preceded the compute by twenty-four minutes. THERE IS NO BREACH.**

> **WITHDRAWN. Rule 2 was satisfied — the freeze came first, which is the whole of what rule 2 requires. What I saw was a DOCUMENT that contradicted itself, and I read a contradictory document as a violated rule.** The ordering was clean; the record was not. **That is a real defect and it is `§2ch`'s, not rule 2's.**
>
> **This is the third correction this team has made against itself today and the third that runs in another team's favour** (`§2bn` restored K2bU3R3, `§2cd` exonerated `check_comparator_freeze.py`, and now MRF). **The pattern is worth naming: a supervisor auditing at speed generates false positives, and the accusatory direction is the one this charter has ruled hardest against (`§2bn`). Withdrawing them promptly and by name is the only thing that makes the audit affordable to the teams being audited.**

### §2ch — **A `DRAFT / UNFROZEN` BANNER STANDING ABOVE A FREEZE BLOCK IS A RECORD DEFECT, AND IT HAPPENED TWICE TONIGHT**

`M6CP1` at `726e3d0c` and `MRF` at `e006de9b`: a freeze block was appended while **line 3 still read `STATUS: DRAFT / UNFROZEN. NO COMPUTE HAS RUN. NOT A GATE YET.`**

**This is `§2bg`'s class — a headline travels alone.** Line 3 is the first thing any reader, any instrument and any future auditor sees, and it asserts **the exact opposite** of the freeze block below it. **I was that reader thirty minutes ago, and I filed a rule-2 accusation against a team whose ordering was clean.** The defect cost a real false positive within the hour of its creation.

> **RULED — §2ch: APPENDING A FREEZE BLOCK AND STRIKING THE `DRAFT / UNFROZEN` BANNER ARE ONE OPERATION, NOT TWO. A registration is frozen when BOTH have happened. A document carrying both states simultaneously is NOT a frozen registration with a stale header — it is a registration whose freeze status cannot be determined from the document, and no reader is obliged to guess which half is current.**
>
> **THE INSTRUMENT, and its authority is bounded exactly as everything else tonight has been:**
> - **The check is specified: a registration carrying a `DRAFT`/`UNFROZEN`/`NOT A GATE YET` token ABOVE its freeze block is flagged.** Cheap, textual, no compute.
> - **IT LANDS AS A WARNING, NOT A REFUSAL.** cfd asked for a refusal, and **the request is well-founded on the merits and is still not mine to grant**: making an instrument refuse where it previously passed is **adding a gate on lab process, and `D539` reserves that to Sanaa — "not cfd, not this team, not the chief."** I have declined to arm three checks tonight on that ground and I will not make an exception for a request I agree with.
> - **RECORDED FOR SANAA'S DESK**, with the two measured instances and the measured cost (one false rule-2 accusation, withdrawn in `§2cg`), as evidence for **her** decision. **A well-motivated gate is still her gate.**
> - **Until it is armed, the obligation is on the author and it is absolute: strike the banner in the same commit that appends the freeze block.** The private-index protocol makes that one operation trivially — both edits, one `write-tree`, one commit.

**Recorded with thanks and without softening the ledger: cfd accepted `§2ca`'s PRD ruling under `§2d.1` on the strength of the noise-floor finding — i.e. they accepted a repair that this team's own measurement says WILL NOT PRODUCE A PASS.** Accepting a correction that cannot help your own verdict is the behaviour `§2d.1` exists to make safe, and it is noted here because the ledger should carry it as prominently as it carries the defects.

| amendment record | **v1.90** |
|---|---|
| clauses added | **3** (§2cf, §2cg, §2ch) · existing clauses gaining a limb | **1** (`§2bk.5`) |
| **accusations by this team WITHDRAWN** | **1** (MRF rule-2 flag — no breach; freeze preceded compute by 24 min) |
| self-corrections today running in another team's favour | **3** (K2bU3R3, `check_comparator_freeze.py`, MRF) |
| gate values changed | **0** · gates armed | **0** · checks made to refuse | **0** (`D539`) · items recorded for Sanaa | **2** (`STAGNANT_FLOOR`, the banner refusal) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.91, 2026-09-10 — **§2ci A LAUNCH IS NOT A LAUNCH UNTIL A CHILD ARTIFACT EXISTS — `Popen` RETURNING IS NOT EVIDENCE, AND THIS IS THE WORST MEMBER OF TODAY'S CLASS BECAUSE IT IS A FALSE *ACTION*, NOT A FALSE *CHECK*. §2cj THE CENSUS: EVERY STAGE-4 LAUNCH CLAIM IN THE LAB IS FALSE — ONE OF ONE. §2ck A WRAPPER THAT ERASES ITS OWN ERROR CONVERTS A LOUD FAILURE INTO A SILENT SUCCESS**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **cfd** against their own instrument and their own first-ever `--go`. **Census run and every claim re-verified at source by this supervisor at 21:15–21:17Z**, bounded per `§2cf.1` (named-path `find`, `-maxdepth`, no `VTK`/`processor*` walk). `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`).**

### §2ci — **THE SIXTH INSTANCE TODAY, AND THE FIRST THAT IS A FALSE ACTION RATHER THAN A FALSE CHECK**

`scripts/case_protocol_stage4_run.py:365-373` does `Popen(setsid nohup …)`, `sleep 2`, then writes `manifest["launched"] = True` and prints `LAUNCHED` — **without ever checking the child is alive.** The comment **eight lines above names exactly that trap.** The generated wrapper does `set -u` and then sources OpenFOAM's `etc/bashrc`; `WM_PROJECT_DIR` is unset, so the wrapper **aborts before the `cd`, the `touch` and the solver** — and the error is erased by `>/dev/null 2>&1`.

**Every previous member of today's class was a false CHECK: a census that read a name (`§2bn`), a line misread (`§2bo.1`), a gate run in the wrong form (`§2bq`), an enforcer reading a notation (`§2bt`), a detector reading the word "planted" in a banner (`§2bw`). Each produced a wrong belief about work that HAD happened.**

> **THIS ONE PRODUCES A WRONG BELIEF THAT WORK IS HAPPENING WHEN THE BOX IS IDLE. On the night the owner's words are "For now i want the RUNS", a launcher that reports `LAUNCHED` and starts nothing is the single most expensive defect the lab can hold — it does not corrupt a result, it silently removes the run that would have produced one.** It also compounds directly with two things measured tonight: **the pending queue at 0 across all six teams**, and **`/proc/pressure/cpu` at 0.93 %**. A lab that believes it is running and is idle will read both of those as somebody else's problem.

**AND THE LESSON IT DEFEATS WAS ALREADY ON THE BOOKS, APPLIED TO THE WRONG HALF.** This lab already knows that **`setsid timeout cmd` exits 0 for every outcome** and that rc must be captured **inside** the detached wrapper, never around the `setsid` line. **That lesson was applied to the RETURN CODE and never to the LAUNCH.** `Popen` returning a handle proves a process was forked; **it proves nothing whatever about whether the thing you wanted to run is running.**

> **CLAUSE §2ci: A LAUNCHER MAY NOT RECORD `launched: true` — OR PRINT `LAUNCHED`, OR WRITE ANY LAUNCH MARKER — ON THE STRENGTH OF `Popen` RETURNING, A `sleep`, OR THE PARENT'S EXIT CODE. THE CLAIM IS ASSERTED FROM THE CHILD, BY ONE OF EXACTLY TWO WITNESSES:**
> 1. **LIVENESS OF THE SOLVER ITSELF** — `kill -0` on the **solver's** pid, read from inside the wrapper, **never the `setsid`/`nohup` parent's pid**, which is alive in every outcome; or
> 2. **A FIRST ARTIFACT THE CHILD PRODUCED** — the first line appearing in the solver log, or the case's `0/T` mtime advancing past its staging time.
>
> **A launcher that cannot obtain either witness records `launched: false` and says why. `PENDING` is the honest display state; a launch marker is not a hope.**
>
> **Witness 2 costs nothing and the lab already owns it.** `0/T` is touched last at launch precisely so it **dates the run** — that is rule 4's clause-6 age guard. **The same mtime, UNCHANGED, is proof the run never started.** One artifact, two uses, and the second was free the whole time.

### §2cj — **THE CENSUS: TWO STAGE-4 MANIFESTS IN THE LAB, ONE CLAIMS A LAUNCH, AND THERE IS NO SOLVER BEHIND IT**

Bounded named-path census across `verification/runs` and `cases`, disk **and** tracked (`§2cc`'s corpus rule), 21:15:21Z; positive controls on both filters (`FREEZE_MANIFEST*` → 1 on disk; `STAGE2_RECORD` → 1 tracked).

| manifest | `launched` | solver | evidence behind it |
|---|---|---|---|
| `verification/runs/M6CP1_runs/STAGE4_MANIFEST_L0.json` | **False** | `rhoPimpleFoam` | correctly negative |
| `verification/runs/M6CP1_runs/STAGE4_MANIFEST_L2.json` | **True** | `rhoPimpleFoam` | **NONE** |

**Verified at source, 21:16:56Z:** `L2/case/` contains **only** `0`, `constant`, `launch_stage4.sh`, `system` — **no solver log, and no time directory beyond `0`.** And the decisive one, using witness 2 above: **`L2/case/0/T` has mtime `Sep 9 01:03`** — its staging time, **untouched**. The three `log.rhoPimpleFoam` files that do exist under `M6CP1_runs` are in `L2/smoke_M0_baseline/`, `L1/smoke/` and `L2_N1/smoke/` — **smoke runs, not this launch**, and a name-only census would have counted them as the missing evidence.

> **RESULT: ONE OF ONE. Every stage-4 launch claim in this lab is false, and the population is small enough to say so exhaustively rather than as a rate.** `L0`'s honest `false` is the positive control that the manifest field can carry both values.
>
> **NO VERDICT MOVES AND NO CASE IS DIRTY — because nothing ran, nothing was graded from it.** `M6CP1` `L2` is `PENDING`, not `NOT A RESULT`: **there is no measurement to demote.** This also **explains rather than excuses** `§2bx`: M6CP1's stage-2 arm was measuring nothing and its stage 4 never started. **The case is not damaged; it is un-begun, and that is a far cheaper position to be in at 21:17Z than the alternative.**

### §2ck — **`set -u` OVER A SOURCED THIRD-PARTY `bashrc`, TWICE TONIGHT — AND THE ERASURE IS THE MULTIPLIER**

Two independent instances: the stage-4 wrapper, and the **MRF wrapper at 20:17Z**. The mechanism is generic and will recur: **OpenFOAM's `etc/bashrc` legitimately reads variables that are unset on first entry; `set -u` turns each into a fatal abort.**

**But `set -u` alone would have been a LOUD failure.** What made it invisible is `>/dev/null 2>&1` on the wrapper invocation: **the diagnosis was generated, correctly, and then discarded** — and the caller, asserting nothing about the child, reported success.

> **CLAUSE §2ck: A WRAPPER'S OWN STDERR IS EVIDENCE AND IS NEVER DISCARDED. It is redirected to a file beside the run, never to `/dev/null`. A launcher that both silences its child and declines to check it has converted a loud, immediate, one-line failure into a silent false success — and the two defects are individually survivable and jointly fatal.**
>
> **Operationally:** do not wrap `set -u` around a sourced third-party profile — source it first, then `set -u`, or set the variables the profile needs before entering strict mode. **This is a WRAPPER defect and not an OpenFOAM defect**, so it is repaired here and nothing goes upstream. cfd repairs both under `§2d.1` with their own diff-read, and the exception is properly available: **no result existed, so no gate can have been aimed at an answer.**

### §2cl — **THE CAP RELEASE IS RECORDED, AND THIS TEAM DECLINES THE HEADROOM TONIGHT**

Sanaa's own words: *"any cap increase needed to reach our goal is pre approved by me already. Im giving the team full freedom for this."* **Recorded as authorisation — hers, in her words, so rule 9 is satisfied and no agent's relay is doing the authorising.** `SUPERVISION_CHARTER` §8's lane cap of 3 is lifted for the push.

> **AND THIS TEAM IS NOT SPAWNING MORE LANES TONIGHT, ON MEASUREMENT AND NOT ON CAUTION. `§2cf` measured `/proc/pressure/io full avg300 = 43.24 %` against `/proc/pressure/cpu some avg300 = 0.93 %` — the box is IO-saturated with idle CPUs, and my own lanes' censuses are part of the cause. Adding lanes would consume the very throughput the cap release exists to buy.**
>
> **A pre-approved cap increase is PERMISSION, NOT AN INSTRUCTION.** The headroom is real and stays available the moment the IO pressure falls; **using it now would spend Sanaa's grant against her stated goal.** `[lab-attributed]`, recorded so the decision is auditable rather than assumed.

| amendment record | **v1.91** |
|---|---|
| clauses added | **4** (§2ci, §2cj, §2ck, §2cl) |
| **launch claims audited** | **2** · **false** | **1** · population exhaustive | **yes** |
| gate values changed | **0** · verdicts withdrawn | **0** · verdicts DEMOTED | **0** (`M6CP1 L2` is `PENDING` — nothing ran, so nothing to demote) |
| cases alleged dirty | **0** · checks made to refuse | **0** (`D539`) |
| authorisations recorded | **1** (cap release, Sanaa's own words) · **declined tonight on measurement** | **1** |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.92, 2026-09-10 — **§2cm THE WITNESS I PRESCRIBED FORTY MINUTES AGO IS ITSELF A PROXY: `Time =` FIRES ON `decomposePar`, 583 LINES BEFORE ANY SOLVER STEP. §2cn A NORMALISED RESIDUAL IS A RATIO, AND A DIVERGING FIELD DRIVES ITS OWN RESIDUAL TOWARD ZERO. §2co MY CANONICITY RULING AND ITS OPERATING CAVEAT SIT 21 LINES AND ONE CLAUSE APART**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **dafoam** (§2cm, §2cn) and by a **verification lane reading my own charter as a user would** (§2co). **The one instrument edit this team has made today is recorded in §2co with its diff-read and its selftest.** `[lab-attributed]`. **No gate value moves; no verdict is withdrawn; nothing is made to refuse (`D539`).**

### §2cm — **THE SEVENTH INSTANCE TODAY, AND IT IS INSIDE THE CLAUSE I WROTE TO CURE THE SIXTH**

`§2ci` (v1.91, forty minutes old) ruled that `launched: true` must be asserted from the child by one of two witnesses, and named the second as *"the first line appearing in the solver log, or the case's `0/T` mtime advancing past its staging time."*

**dafoam measured the failure mode: `Time =` — the obvious implementation of "the first line in the solver log" — fires on `decomposePar`'s OWN `Time =` line, 583 lines before any solver step. A launcher waiting on it declares `LAUNCHED` on `decomposePar`.**

> **This is the day's own finding turned on its author: `Time =` is a TOKEN THAT USUALLY ACCOMPANIES A SOLVER STEP, and the launcher would be reading the token instead of the property. A PROXY IS NOT THE PROPERTY — and I wrote a proxy into the remedy for the previous proxy, in the same hour.**

> **`§2ci` WITNESS 2 IS CORRECTED AND NARROWED, and the correction is the whole of the change — witness 1 (liveness of the SOLVER's own pid, never the `setsid`/`nohup` parent's) stands untouched:**
>
> **WITNESS 2 IS ONE OF EXACTLY TWO ARTIFACTS, AND `Time =` IS NEITHER:**
> - **the solver's first `ExecutionTime` line** — emitted by the solver's own time loop and **not by `decomposePar`**; or
> - **`0/T`'s mtime advancing past its staging time** — the artifact rule 4's clause-6 age guard already relies on to date a run.
>
> **A pre-processing utility writes into the same log and its output is not evidence that the solver started.** The general form, and it is the transferable half: **a launch witness must be an artifact ONLY THE PROCESS YOU ARE WAITING FOR CAN PRODUCE. Anything a predecessor in the same pipeline also emits is a proxy, however specific it looks.**

### §2cn — **A DIVERGING FIELD DRIVES ITS OWN NORMALISED RESIDUAL TOWARD ZERO, SO A RESIDUAL-ONLY GATE REPORTS ITS BEST NUMBER WHEN THE SOLUTION IS WORST**

dafoam's `N-D45` (`5d5dae408`), measured: **`omega` initial residual `5.87e-31` with `nIters 0`, while that same field's `Norm2` read `1.13e+35` and bounding had fired.** The run **passed DAFoam's acceptance by 17,000×.**

**The mechanism is arithmetic, not a bug: a normalised residual carries the field norm in its DENOMINATOR. A field going to `1e+35` makes any residual look perfect. The gate was reading a ratio and calling it a convergence.**

> **RULED — §2cn: NO GATE READS A RESIDUAL WITHOUT A FIELD-BOUNDEDNESS LIMB BESIDE IT. A normalised residual is a RATIO, and a gate on a ratio is a gate on BOTH ITS TERMS — it is admissible as evidence of convergence only when the denominator is independently shown to be bounded.**
>
> **THIS CREATES NO NEW LAW. It is `§2p.3(b)` — "EVERY DIFFERENTIAL GUARD CARRIES AN ABSOLUTE LIMB BESIDE IT" — reaching a class it had not been applied to: the differential guard whose normalisation hides the divergence.** The absolute limb here is field boundedness (`Norm2`, `max`/`min` against physical bounds, or the solver's own bounding warnings), and **a fired bounding warning is a positive finding, not log noise.**
>
> **It also composes with `§2az`, and the two answer different questions.** `§2az` fixed **WHICH** residual may bind a gate — the uncorrected initial residual of the first pressure/momentum solve at the final outer iteration, never a within-iteration corrector. **`§2cn` fixes WHETHER A RESIDUAL ALONE MAY BIND ONE AT ALL. Passing `§2az` and failing `§2cn` is exactly what `N-D45` did.**
>
> **AND IT IS THE THIRD NORMALISATION ARTIFACT THIS TEAM HAS MEASURED TODAY**, which is why it earns a clause rather than a docket row: `§2bz`'s caveat — `GCI_pct = 129.33 %` on a PASS, because `f_fine ≈ 7e-4` sits in the denominator; `§2ca`'s plateau tolerance, relative to a monitor whose own ripple is the same order; and now `N-D45`. **A NORMALISED QUANTITY STOPS MEANING WHAT ITS NAME SAYS THE MOMENT ITS DENOMINATOR MOVES, AND ITS NAME NEVER WARNS YOU.** Report the absolute beside the relative, always; where only one may be quoted, **quote the absolute.**

### §2co — **MY CANONICITY RULING AND ITS OPERATING CAVEAT ARE 21 LINES AND ONE CLAUSE APART, AND A READER FOUND THAT BY BEING THE READER I DESIGNED FOR**

A lane reported the canonical stage-2 instrument as unusable tonight, because *"the charter's prose does not warn"* about argparse consuming a flag-shaped value. **It does warn — `§2by` point 4, at `:9628`. The lane flagged VERIFY on exactly this point and was right to.** But **the canonicity ruling is at `:9607`, in `§2bx`** — **21 lines and a clause boundary away.** The lane read the sentence that answered its question and stopped, which is what readers do.

> **THIS IS `§2bg` ("A HEADLINE TRAVELS ALONE") AND `§2ae` ("A CORRECTION FILED ONLY AT THE FOOT DOES NOT REACH THE READER OF THE CLAUSE") — MY OWN TWO CLAUSES, IN MY OWN CHARTER, INSIDE A SINGLE COMMIT.** The designation travels; the caveat does not. **RULED: A DESIGNATION OF AN INSTRUMENT AS CANONICAL CARRIES ITS OPERATING CAVEATS IN THE SAME SENTENCE OR THE SAME PARAGRAPH — never in a later clause — because the designation is the part that gets quoted.**
>
> **Restated here so the two travel together, and this paragraph is the citable one: `scripts/check_instrument_detects_plant.py` IS THE CANONICAL STAGE-2 INSTRUMENT CHECK, AND IT IS NOT YET MANDATORY. Two caveats bind every use: (i) FLAG-SHAPED READER ARGUMENTS TAKE AN EQUALS SIGN — `--reader-arg=--case`, never `--reader-arg --case`, which exits 2; and (ii) ON A MULTI-COLUMN `.dat` THERE IS NO CORRECT INVOCATION YET — `plant_append`'s marker line decides the verdict by how the reader's tokeniser reacts to it, so a `DETECTED` there is NOT a valid green and the case record STATES THE §2 GAP IN WORDS (`§2by`).**

**THE ONE INSTRUMENT EDIT THIS TEAM HAS MADE TODAY, recorded in full because I have declined nine others tonight and the asymmetry needs its reason.** I edited **one `help=` string** in `check_instrument_detects_plant.py` so the tool states caveat (i) itself.

- **Safe to touch, MEASURED before touching:** the instrument is **pinned by NO registration** — zero hits across `verification/campaign`, `docs/campaigns` and `cases`; positive control on the identical filter returns **5** for a name I know is pinned. **No freeze is broken and rule 2's grading path is untouched.**
- **`SUPERVISION_CHARTER` §3 check 1 discharged personally: I read the diff.** It adds four lines inside one `add_argument(help=…)` kwarg. **No logic, no constant, no threshold, no exit code, no emitted value.**
- **Proof nothing moved: `--selftest` re-run at 22:06:21Z — `44 checks, 0 failed / SELFTEST PASS`, rc 0, `ast.Assert node count == 0` still holding.** Identical to the pre-edit figure.
- **Why this one and not the other nine:** every deferred repair changes **what an instrument DECIDES**. This changes **what it SAYS about how to call it**. **A help string cannot produce, grade or aggregate a measured number, and a lane hitting exit 2 at 02:00 with no explanation is a cost I can retire tonight for zero risk.**

| amendment record | **v1.92** |
|---|---|
| clauses added | **3** (§2cm, §2cn, §2co) · existing clauses **CORRECTED** | **1** (`§2ci` witness 2 narrowed; witness 1 untouched) |
| new law created by §2cn | **0** — `§2p.3(b)` reaching the normalised class |
| **instrument edits made** | **1** (a `help=` string; diff read personally, selftest 44/44 rc 0, pinned by nothing) · **still deferred** | **9** |
| gate values changed | **0** · verdicts withdrawn | **0** · checks made to refuse | **0** (`D539`) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.93, 2026-09-10 — **§2cp "THE MESHES ARE INNOCENT" IS REFUTED, AND BY MY OWN `§2br`: A QUALITY INVARIANT IDENTICAL ACROSS LEVELS IS SCALE-INVARIANT. §2cq THE WALL-TREATMENT INVERSION — A FAMILY CAN REFINE ITSELF OUT OF ITS OWN MODEL'S VALIDITY BAND. §2cr A GATE UNFREEZABLY BROKEN BY ITS *REFERENCE*, WHICH NO FREEZE CHECK ASKS ABOUT. §2cs M6CP1's CUSP WAS AN UNREGISTERED DEPARTURE FROM A REFERENCE THE LAB HAS HELD SINCE 3 SEPTEMBER**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **cfd**, and `§2cp` refutes this team's own finding of three hours ago. **The M6 reference coordinate is verified at source by this supervisor; the SUBOFF quality figures are cfd's and are explicitly NOT re-derived here — see the corpus disclosure in `§2cp`.** `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`).**

### §2cp — **I WROTE "THE MESHES ARE INNOCENT" AND MY OWN CLAUSE OF THREE HOURS EARLIER SAYS THEY ARE NOT**

`§2cb` referred SUBOFF with the line *"its physics is not a grid question at all … on a clean r = 1.5 family. **THE MESHES ARE INNOCENT.**"* **I reached that from the REFINEMENT RATIO alone** — r21 = 1.49958, r32 = 1.49937, a textbook family — **and never looked at a single quality invariant.**

cfd's measurement: **min cell determinant `3.526225e-05` identical to seven figures at all three levels; max aspect ratio `236.15` likewise; bad cells multiplying `1,531 → 3,240 → 7,125` with refinement while the worst never improves.**

> **A CLEAN REFINEMENT RATIO IS NOT AN INNOCENT MESH, AND `§2br` ALREADY SAID SO IN THE ONLY WORDS THAT MATTER: a defect identical at every level is SCALE-INVARIANT, its error does not reduce as `h → 0`, and it contaminates `e21` and `e32` with a term constant across the ladder. I wrote that clause at 19:55Z and contradicted it at 20:17Z on the very case it describes.**

> **RULED — §2cp: `§2br` IS GENERALISED FROM FEATURE RESOLUTION TO ANY QUALITY INVARIANT. A refinement family must be shown to IMPROVE — not merely to grow — and the evidence is `checkMesh`'s quality metrics COMPARED ACROSS LEVELS, cited beside the cell counts. A minimum determinant, a maximum aspect ratio or a maximum non-orthogonality that is IDENTICAL ACROSS LEVELS (to the digits printed) is proof the ladder is not refining where it is worst, and it disqualifies an observed order exactly as a zero-cell feature does.**
>
> **The check is free and comparative: the numbers are already in every `log.checkMesh`; nobody had put three of them side by side.** And note it composes with `§2bq`: **those metrics must come from the `-allGeometry -allTopology` invocation, or the determinant limb is not in the log to compare.**

**THE CORPUS DISCLOSURE THIS TEAM OWES, because it is `§2cc` against me a fourth time.** I attempted to re-derive cfd's figures and **could not, for two reasons that are both mine:** I first sampled `reg_coarse` and `diag_medium_wp16` — **diagnostic directories, not the graded triple** — and got `236.1509113697265` and `70.845`, non-identical, which would have read as a refutation of a true claim. And my determinant filter returned **zero on `reg_coarse`**, because that log has **no `minimum:` line at all** — a bare `checkMesh`, which is **`§2bq`'s own finding.**

> **cfd's figures are RECORDED AS THEIRS AND NOT RE-DERIVED. My failure to reproduce them is a statement about MY corpus and MY filter, not about their measurement** — the exact discipline `§2bn` and `§2cc` exist to enforce, applied against my own instinct to report a non-reproduction as a finding.
>
> **AND THE ATTEMPT PRODUCED A REAL SUB-FINDING: the three GRADED levels — `r1b_coarse`, `r1b_medium`, `r1b_fine` — carry NO `log.checkMesh` AT ALL.** Seven such logs exist under SUBOFF and **not one of them is in a graded directory.** So under `§2bq` the graded triple **cannot cite the argv that admitted its meshes**, because there is no log in the graded levels to cite. **Referred to cfd; not ruled.**

**Two corrections cfd supplies that this team accepts and records against its own earlier framing:** the lab's SUBOFF wedge **IS Groves 1989 Configuration 1, the source's own axisymmetric baseline** — so it was **never wrong to be a wedge**, and a 3D SUBOFF is a *different configuration*, not a better one. `§2bo.3` said the wedge invalidates nothing and forbids only the word "3D"; **that scoping was right and is now confirmed from the source.** And the appendage trailing edges **close to a point by design** (Table 3's polynomial sums to 0 at ξ = 1), so **the reference geometry itself carries the M6CP1 pathology** — which makes `§2br` a reference-level problem, not only a meshing one.

### §2cq — **A REFINEMENT FAMILY CAN REFINE ITSELF OUT OF ITS OWN MODEL'S VALIDITY BAND, AND THE FINEST LEVEL IS THEN THE LEAST TRUSTWORTHY**

cfd's candidate mechanism for SUBOFF: **`nutkWallFunction` requires y+ ≳ 30; the coarse level measures y+ 25.3; `y1` falls 2.25× across the family.** So the family **starts marginally outside its wall treatment's validity and moves further out with every refinement** — in the same order as the CT blow-up.

**cfd's own caveat is adopted verbatim and is the honest half: fine's y+ 694 is POST-DIVERGENCE, so cause and effect are not separable. This is a STRONG CANDIDATE, NOT A DIAGNOSIS**, and this charter will not write it as one (`§2bn`).

> **But the CLASS is rulable independently of whether it is SUBOFF's cause, and it is general and unguarded: REFINEMENT IS NOT MONOTONE IN VALIDITY. Every wall function, every low-Re model, every wall-distance-based closure has a validity BAND in y+, and `h`-refinement moves a family THROUGH that band and out the far side. The finest level — the one Roache weights most heavily and the one `f_fine` is read from — can be the LEAST physically admissible member of its own ladder.**
>
> **RULED — §2cq: A REFINEMENT FAMILY MUST HOLD ITS MODEL'S VALIDITY CONDITIONS AT EVERY LEVEL, AND THE CONDITION IS STATED AND MEASURED PER LEVEL IN THE REGISTRATION — for a wall-function closure that means the y+ band, measured, at L1/L2/L3, beside the cell counts. A family that leaves the band at any level has no admissible observed order over that range, and the remedy is a model appropriate to the resolution (a low-Re treatment), NOT a looser gate and NOT a coarser mesh chosen to keep a wall function happy.**
>
> **This is a THIRD independent disqualifier of a ladder, and the three are orthogonal — `§2bo.2` catches a family whose TOTALS step wrong; `§2br`/`§2cp` catch one whose DEFECTS do not shrink; `§2cq` catches one whose PHYSICS MODEL stops applying. A family can pass all three checks and still fail, but a family failing any one of them cannot produce an observed order, and ALL THREE ARE COMPUTABLE BEFORE THE LADDER IS GRADED.**

### §2cr — **A GATE BROKEN BY ITS *REFERENCE*: THE FREEZE PINS THE COMPARATOR AND NEVER ASKS WHETHER THE THING IT COMPARES AGAINST EXISTS**

M6CP1 §5 **Gate P** — Cp at seven stations, ±0.02 — **had no machine-readable reference from the moment it was frozen.** The lab's AGARD AR-138 is a **2007 paper-capture whose numeric tables never OCR'd**; the Cp tables **exist only as captions.**

> **This is a genuinely new class and it sits in a hole this team's own doctrine left open. Rule 2, `§2s` and `check_comparator_freeze.py` all pin THE COMPARATOR — its blob, its sha, its commit time. NOTHING ANYWHERE ASKS WHETHER THE REFERENCE THE COMPARATOR READS RESOLVES TO A NUMBER.** A gate can therefore be **perfectly frozen and permanently ungradeable**, and every freeze instrument reports it green.
>
> **It is `§2v`'s family — a gate that cannot fail — reached by a route `§2v` did not enumerate: not an unimplemented gate, and not an unreachable one, but a fully implemented gate with NOTHING ON THE OTHER SIDE OF THE COMPARISON.**
>
> **RULED — §2cr: A REGISTRATION THAT NAMES A QUANTITATIVE REFERENCE MUST NAME THE ARTIFACT THE NUMBER IS READ FROM — a path and a locator, not a citation — AND THAT ARTIFACT MUST RESOLVE TO A MACHINE-READABLE VALUE AT FREEZE TIME. A bibliographic citation is provenance; it is not a reference. Where the number exists only in a scanned caption, the registration says so ON ITS FACE and the gate is registered as `PENDING` pending transcription — never frozen as if gradeable.**
>
> **THE INSTRUMENT, and its authority is bounded as everything else tonight: a reference-resolvability READER — for each registered gate, does its named reference artifact exist and parse? It REFUSES NOTHING and it is mine to build, alongside the declared-`dim` cross-check `§2cb` already committed me to. Arming either as a refusal is `D539` and Sanaa's.** **Gate P is `NOT A RESULT` in the strict sense — nothing was measured, because nothing could be — and that is a disclosure M6CP1's record owes on its face, not a demotion of anything that ran.**

### §2cs — **M6CP1's CUSP WAS AN UNREGISTERED DEPARTURE FROM THE REFERENCE GEOMETRY, AND THE REFERENCE HAS BEEN ON DISK SINCE 3 SEPTEMBER**

**VERIFIED AT SOURCE by this supervisor at 22:18:08Z.** `models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat` (1,512 B, mtime **2026-09-03 23:02**) — its final data line, verbatim:

```
1.0000000  0.0007052
```

**At x/c = 1.0 the reference half-thickness is z/c = 7.052e-4. THE ONERA M6 TRAILING EDGE IS BLUNT** — cfd's reading: 0.141 % chord, a 14.8° included angle, **7.6× the fabrication tolerance.** The case built a **cusp**.

> **RULED — §2cs, and it STRENGTHENS `§2bs` rather than replacing it. `§2bs` held M6CP1's park premature because zero cells across the trailing edge was affirmative evidence of a fixable SETUP artifact. The evidence is now stronger and more specific: THE GEOMETRY ITSELF DEPARTED FROM THE REFERENCE, THE DEPARTURE WAS NEVER REGISTERED, AND THE CORRECT COORDINATE WAS SITTING IN THE REPOSITORY SEVEN DAYS BEFORE THE CASE FROZE.**
>
> **THE SUCCESSOR IS NOW SPECIFIED RATHER THAN GESTURED AT: the M6 successor is built on the AGARD AR-138 Table B1-1 section coordinates AS THEY STAND — blunt trailing edge, `z/c = 7.052e-4` at `x/c = 1.0` — with cells resolved across that finite thickness, and the registration states the TE treatment explicitly. `§2br`'s feature-cells table is then a real check rather than a vacuous one, because THERE IS A FEATURE TO PUT CELLS ACROSS.**
>
> **AND THE GENERAL RULE THIS EARNS: A GEOMETRY IS PART OF THE REGISTRATION. A departure from the reference geometry — a closed trailing edge, a removed fillet, a simplified junction — IS A REGISTERED CHOICE WITH A STATED REASON, OR IT IS AN UNDISCLOSED CHANGE TO THE CASE BEING VALIDATED.** M6CP1's cusp was neither malicious nor careless; **it was invisible, because no instrument in this lab compares a built geometry against its reference, and no clause required anyone to say.** *(cfd's SUBOFF note cuts the other way and is recorded beside it: there, the appendages close to a point BY DESIGN in the source's own polynomial — so the same pathology can be FAITHFUL. Which is exactly why it must be REGISTERED rather than assumed either way.)*

| amendment record | **v1.93** |
|---|---|
| clauses added | **4** (§2cp, §2cq, §2cr, §2cs) · existing clauses GENERALISED | **1** (`§2br` → any quality invariant) · STRENGTHENED | **1** (`§2bs`) |
| **this team's own findings REFUTED** | **1** ("the meshes are innocent" — by my own `§2br`) · corpus failures disclosed | **1** (`§2cc`, fourth time) |
| instruments this team now owes | **2** (declared-`dim` cross-check; reference-resolvability reader) — **both READERS, neither refuses** |
| gate values changed | **0** · verdicts withdrawn | **0** · checks made to refuse | **0** (`D539`) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.94, 2026-09-10 — **§2ct AN EXIT CODE IS A CHANNEL WHOSE CONTRACT YOU DID NOT WRITE: `checkMesh` RETURNS 0 WHILE PRINTING `Failed 3 mesh checks.` §2cu "ARMED BY DATA" — ONE NULL IN A JSON SILENTLY REMOVES THE GATE, ITS CONTROL, AND THE REFUSAL, BECAUSE ALL THREE SHARE ONE PREDICATE. §2cv WHEN A TOOL'S SELF-REPORT IS THE THING IN QUESTION, THE CONFIRMING READER MUST NOT SHARE ITS CODE PATH**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by **cfd** from their DrivAer build. **§2cu's guard read at source by this supervisor at 23:12:38Z; §2ct's and §2cv's figures are cfd's and are recorded as theirs.** `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`).**

### §2ct — **`§2bq` IS SHARPENED, AND THE PART I LEFT OPEN IS THE PART A READER WOULD HAVE USED**

`§2bq` ruled that a mesh-admissibility claim cites the argv, and gave the missing-`Cell determinant`-line discriminator. **It did not say what to read INSTEAD, and the obvious answer — the exit code — is measured wrong in both directions.**

cfd's measurement: **`rc = 1` on a broken mesh, and `rc = 0` on three delivered levels each printing `Failed 3 mesh checks.`** And, compounding it, **plain `checkMesh` reports 1 failure where `-allGeometry -allTopology` reports 3** (small determinant and concave cells are the two it cannot see).

> **RULED — §2ct: THE MESH VERDICT IS THE `Failed N mesh checks` LINE, PARSED, UNDER THE FULL FLAG SET. THE RETURN CODE IS NOT THE VERDICT AND MAY NOT BE GATED ON.** A `Mesh OK.` line with no `Failed` line is the pass; anything else is read from the text.
>
> **AND THE FAMILY IS NOW LARGE ENOUGH TO NAME, BECAUSE THIS LAB HAS PAID FOR IT FOUR TIMES: `setsid` returns 0 for every outcome; `Popen` returning proves only a fork (`§2ci`); `§2ak` had to rule the comparator exit-code contract on a census of 238 comparators; and now `checkMesh` returns 0 while printing three failures. AN EXIT CODE IS A CHANNEL WHOSE CONTRACT SOMEBODY ELSE WROTE, AND USUALLY DID NOT DOCUMENT. Where a tool emits a verdict in its OUTPUT, the output is the verdict and the rc is a hint.** *(This does not touch `§2ak`, which governs the exit codes of comparators **this lab writes** — there the contract is ours and it binds.)*

### §2cu — **"ARMED BY DATA": THE GATE, ITS PLANTED CONTROL, AND THE REFUSAL ALL HANG ON ONE `is not None`**

Read at source, `cases/navier_class/DRIVAER/grade_drivaer.py`, verbatim:

```
350:    cd_ref, cl_ref = ref["Cd"], ref.get("Cl")
363:    ctrl_cl = coefficient_plant_control(args.fine, "Cl") if cl_ref is not None else None
364:    if ctrl_cl is not None and not ctrl_cl["passed"]:
378:    if cl_ref is not None:
380:        band_cl = (cl_ref - CL_BAND_ABS, cl_ref + CL_BAND_ABS)
```

**The reference JSON carries `Cl: null`. Trace what that one null does: `:363` the PLANTED CONTROL is never built; `:364` the refusal is doubly gated and cannot fire on a control that does not exist; `:378` the GATE is skipped. Three independent safety layers, ONE predicate, and the grader exits normally having silently graded nothing about lift.**

> **THE KILLER, AND IT IS THE GENERAL FORM: THE CONTROL IS GUARDED BY THE VERY CONDITION IT EXISTS TO CATCH. A planted control disarmed by the same predicate as its gate cannot guard that gate — it can only confirm the gate when the gate was already going to run. Standing rule 3 buys nothing here, and `§2bw`'s null-plant test would pass, because with `Cl: null` there is no plant to run and no claim to test.**

**AND LINE 350 IS THE TEACHING ARTIFACT, because both behaviours sit in one statement:** `ref["Cd"]` is a **subscript** — a missing `Cd` raises `KeyError` and the grader dies loudly. `ref.get("Cl")` is **`.get()`** — a missing or null `Cl` returns `None` and the grader continues. **The author knew how to fail loud; the silent form was chosen for the reference deemed optional, and "optional" then propagated into the control and the refusal without anyone deciding it should.**

> **RULED — §2cu, two limbs:**
> 1. **A GATE'S ARMING MAY NEVER DEPEND ON THE PRESENCE OF THE DATA IT READS. An absent or null reference is a REFUSAL (exit 2), never a skip.** If a quantity is genuinely optional for a case, **that is a registration decision recorded in the registration** — not an emergent property of a `.get()`.
> 2. **A CONTROL'S ARMING CONDITION MUST BE INDEPENDENT OF ITS GATE'S.** A control that shares the gate's predicate is not a control; **it is a second copy of the gate's assumptions.** Where they must share a condition, the control's failure to arm is itself reported as `COULD-NOT-RUN`, never as silence.
>
> **This is `§2p`'s family reached from a new side — not an instrument insensitive to its input (`§2p.3(a)`), not one whose pass is independent of the input (`§2bu`), but one that DOES NOT RUN AT ALL and says nothing about it. And it composes with `§2cr` from an hour ago: `§2cr` is the reference that does not EXIST; `§2cu` is the reference that exists and is NULL. The first left the gate frozen-and-ungradeable; the second lets the grader exit 0 with a verdict that is silently about fewer quantities than it claims.**
>
> **NO VERDICT IS MOVED BY THIS CLAUSE TONIGHT** — DrivAer has not been graded to a landed verdict, so there is nothing to demote. **What is owed is a sweep: any landed verdict whose grader carries a `.get()`-guarded reference must state which gates actually armed.** cfd's to run on their own graders; **I will run it on the T-family and the certificates when the box is not IO-bound (`§2cf.1`).** *(cfd cite the same shape as SUBOFF's `armed: by_data`; I grepped `grade_suboff.py` for `armed` and got zero, but I searched ONE FILE and that zero is a bound, not a finding — `§2cc`.)*

### §2cv — **INDEPENDENT INSTRUMENTATION: THE CONFIRMING READER MUST NOT SHARE THE CODE PATH OF THE TOOL WHOSE SELF-REPORT IS IN QUESTION**

cfd, on DrivAer: **`snappyHexMesh` layer addition produced 52,165 negative-volume cells of 128,230 — 40.7 % of the mesh — while printing all-zeros on its own final check and `"Finished meshing without any errors"`. Reproduced across snap settings, and CONFIRMED BY A NON-OpenFOAM READER CARRYING A PLANTED CONTROL.**

**The finding is theirs and the methodology is the clause.** Today's entire ledger is one disease — a token from a tool believed in place of the property (`§2bn`, `§2bo.1`, `§2bq`, `§2bt`, `§2bw`, `§2ci`, `§2cm`, `§2ct`). **Every one of those was caught, eventually, by reading a DIFFERENT artifact than the one the tool volunteered. cfd did that deliberately and in advance, and it is the first time today a defect of this class was caught BEFORE it cost something.**

> **RULED — §2cv: WHERE A TOOL'S OWN SELF-REPORT IS THE PROPOSITION UNDER TEST, THE CONFIRMING MEASUREMENT MUST BE MADE BY A READER THAT DOES NOT SHARE THE TOOL'S CODE PATH — a different implementation, a different library, or a direct read of the artifact's bytes — AND THAT READER CARRIES ITS OWN PLANTED CONTROL (rule 3, `§2bw`). A second opinion from the same codebase is one opinion stated twice.**
>
> **This is the constructive half of the day, and it is the one clause here that tells an agent what TO DO rather than what to distrust.** It is also why `§2bw`'s null-plant test and this clause are complementary: **§2bw asks whether your detector can say no; §2cv asks whether your detector is independent of the thing it is judging.**

**RULE 7 COMPLIANCE RECORDED, because it is exactly right and should be visible:** the `snappyHexMesh` defect is **an OpenFOAM issue**, and the owner's standing directive is that OpenFOAM issues are **surfaced, not worked around**. cfd has drafted it and it is **`NOT FILED` and PARKED**. **Nothing is sent, by anyone, ever, except by Sanaa.** The draft stays current — *parked is not cancelled* — and no reading of this clause converts readiness into sending.

| amendment record | **v1.94** |
|---|---|
| clauses added | **3** (§2ct, §2cu, §2cv) · existing clauses SHARPENED | **1** (`§2bq` — read the `Failed N` line, never the rc) |
| gate values changed | **0** · verdicts withdrawn | **0** · verdicts demoted | **0** (DrivAer has no landed verdict to demote) · checks made to refuse | **0** (`D539`) |
| sweeps owed | **1** (landed verdicts whose graders carry `.get()`-guarded references — cfd's graders theirs, T-family and certificates mine, deferred under `§2cf.1`) |
| upstream reports filed | **0** — `NOT FILED`, parked (rule 7) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.95, 2026-09-10 — **§2cw THE TWO CENSUS FILTERS ARE BLIND IN OPPOSITE DIRECTIONS, AND A POSITIVE CONTROL IS ONLY AS GOOD AS THE BLINDNESS IT WAS CHOSEN TO EXPOSE. §2cx THE ARMING DEFECT UNIFIED ON THREE MEASURED INSTANCES — EVERY GATE REPORTS `armed_by`, AND EVERY GATE SHIPS A CONTROL FOR ITS *ARMING*, NOT ONLY ITS *READING***

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** `§2cw` from a verification lane closing its own last open arm; `§2cx` is **cfd's proposal**, adopted with its refusing limbs split off to Sanaa. `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`).**

### §2cw — **`§2cc` GAINS ITS OPERATIONAL FORM, AND IT IS SHARPER THAN THE CLAUSE I WROTE**

`§2cc` ruled that a census is its corpus as much as its filter, and that roots must be stated. **It did not say the thing that actually bites, and a lane found it by auditing its own method rather than its subject:**

> **`grep -r` (ugrep — SKIPS GITIGNORED) and `git ls-files` (TRACKED ONLY) are blind in OPPOSITE directions. An agent who learns about the first trap and switches to the second has traded one blind spot for its mirror, and feels safer.**

**And the deeper half, which corrects `§2bm` as much as `§2cc`: A POSITIVE CONTROL DRAWN FROM THE POPULATION THE FILTER CAN ALREADY SEE IS A TAUTOLOGY.** The lane's own control initially exercised only the ugrep arm; it declined to report the tracked-arm zero until it had a control **chosen to exercise that specific blindness** — token `materialise_case`, living in `scripts/demo3d_render_common.py`, **a file on disk that git does not track**:

| filter | result on the control token |
|---|---|
| `git ls-files \| xargs grep -ln` | **0 — blind, as suspected** |
| `find … -name '*.py' \| xargs grep -ln` | **2** (`demo3d_render_common.py`, `selftest_demo3d_render.py`) |

> **CLAUSE §2cw: A POSITIVE CONTROL IS ONLY AS GOOD AS THE FAILURE MODE IT WAS CHOSEN TO EXPOSE. The control token is selected to live in the class the filter is SUSPECTED OF MISSING — untracked when the filter is `git ls-files`, gitignored when it is `grep -r`, mixed-case when the match is case-sensitive, outside the repo when the roots are inside it. A control that merely proves "the filter returns something" proves the filter is not broken; it does not prove the CORPUS IS WHOLE.**
>
> **AND A CALL-SITE ZERO NEEDS BOTH ARMS.** Neither filter alone can establish one. This is `§2bm` at its second remove: rule 3 said a reader must be shown able to see a non-zero; `§2bm` extended it to prompt-typed filters; **`§2cw` says the demonstration must be aimed at the specific way THIS filter can be wrong.**

**THE MEASUREMENT THIS UNLOCKS, and it is the claim my own canonical designation rests on.** With both arms and a properly aimed control: **`scripts/check_instrument_detects_plant.py` has ZERO EXECUTABLE CALL SITES ANYWHERE ON THIS BOX** — repo tracked and untracked, the out-of-repo run trees, `/home/ubuntu/harness-state`, `/home/ubuntu/notes`, `/etc/systemd/system`, and **cron (0 of 4 entries, with `crontab -l` proven readable by a control that returns real content)**. Its only three references are prose, **one of which is the charter clause that made it canonical 91 minutes earlier.** **Previously "zero tracked call sites" and inferred; now measured.**

### §2cx — **cfd's UNIFICATION IS ADOPTED: THREE INSTANCES TONIGHT ARE ONE DEFECT**

cfd's framing, adopted as the clause name: **SUBOFF's `armed: by_data`, DrivAer's null `Cl` reference disarming a gate AND its control, and M6CP1's stage-2 gate evaluated by an instrument that could not see the failing check are ONE DEFECT — A GATE WHOSE ARMING IS CONTINGENT ON SOMETHING OTHER THAN THE GATE'S OWN DEFINITION.**

**That is a better generalisation than `§2cu`'s, which reached only the data-presence route.** The three instances differ in what the arming became contingent on — **the reference's presence, the reference's nullity, the instrument's capability** — and are identical in consequence: **the gate did not run, and nothing said so.**

> **RULED — §2cx, DISCLOSURE LIMBS, BINDING NOW, because none of them makes anything refuse:**
> 1. **EVERY GATE REPORTS `armed_by`** — the condition that caused it to evaluate, named, in the emitted verdict artifact. A gate that cannot state why it armed has not established that it did.
> 2. **AN UNARMED GATE IS REPORTED AS `NOT-ARMED` AND IS NEVER SILENT, AND IT MAY NEVER BE COUNTED IN A PASS TALLY.** A rung verdict states how many of its gates armed beside how many passed. **"4 gates PASS" where one never armed is a false headline (`§2bg`), and this is the field that prevents it.**
> 3. **EVERY GATE SHIPS A CONTROL FOR ITS *ARMING*, NOT ONLY ITS *READING* — and this is the limb the lab does not have at all.** Every planted control in this repository tests the **read path**: can the reader see a perturbation. **NONE tests the arming path: does this gate actually evaluate when it should, and does it announce itself when it cannot.** The arming control is two cheap arms — **fire the gate on a planted WRONG value and require it to notice; present it an ABSENT or NULL reference and require it to say `NOT-ARMED`** — and `§2cu` measured why it is needed: **DrivAer's reading control was disarmed by the same predicate as its gate, so a reading control cannot detect this class by construction.**
>
> **THE REFUSING LIMBS ARE NOT MINE AND GO TO HER DESK.** cfd propose that an unarmed gate and an absent reference **REFUSE**. **I agree with both on the merits and may not arm either: making an instrument refuse where it previously passed is adding a gate on lab process, and `D539` reserves that to Sanaa — "not cfd, not this team, not the chief."** They are recorded for her with **three measured instances and their cost**, alongside the two items already on her desk tonight. **That is now five declined refusals today, one of them proposed by the team it would constrain.**
>
> **`§2cu` is not superseded — it is the data-presence special case of `§2cx`, and its second limb (a control's arming condition must be INDEPENDENT of its gate's) is what makes limb 3 above implementable rather than circular.**

**NO VERDICT MOVES TONIGHT, and the sweep this implies is named rather than performed:** every landed verdict whose grader can skip a gate must state which gates armed. **cfd's graders are theirs; the T-family and `verification/certificates/` are mine, and both are deferred under `§2cf.1` until the box is not IO-bound** — a full-corpus sweep is exactly the IO-expensive census that clause exists to schedule.

| amendment record | **v1.95** |
|---|---|
| clauses added | **2** (§2cw, §2cx) · existing clauses gaining an operational form | **1** (`§2cc`) · subsumed as a special case | **1** (`§2cu`) |
| gate values changed | **0** · verdicts withdrawn | **0** · checks made to refuse | **0** (`D539`) |
| **refusing limbs DECLINED and sent to Sanaa** | **2** (unarmed gate; absent reference) — **five declined today** |
| claims upgraded from INFERRED to MEASURED | **1** (zero call sites, box-wide) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.96, 2026-09-10 — **§2cf.2 RULING A CLASS DOES NOT STOP THE INSTANCES ALREADY RUNNING — MY OWN UNBOUNDED CENSUS RAN 4h17m, BOUGHT TWO FILES OF INFORMATION OVER A TWO-SECOND `git grep`, AND WAS STILL RUNNING TWO HOURS AFTER I RULED AGAINST IT**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Self-reported; measured at 23:36:55Z. `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`).**

**THE FACTS, AGAINST THIS SUPERVISOR.** At **19:05Z** I launched an unbounded whole-disk `find … | xargs grep -ln launch_guard`. **It completed at 23:22Z — 4 hours 17 minutes.** At **20:27Z** the chief measured the box IO-starved and named a running `grep -ln launch_guard` as *"one of yours"*. At **20:39Z** I ruled `§2cf.1`: *"while solvers run, no repo-wide `grep -r` and no unbounded `find`."* **I then left my own violating process running for another 2 hours 43 minutes.** It was invisible to me because it was detached and its output was empty until it finished — **L-540's shape exactly, landed by another team tonight.**

**AND THE COST/BENEFIT IS THE PART WORTH KEEPING.** The 4h17m census returned **27 files**. A `git grep` I ran in the same minute, in about two seconds, returned **25**. **Four hours and seventeen minutes of IO, on a box whose solvers were stalling, bought TWO FILES** — and both were untracked files a bounded `find` over the three known instrument directories would have returned instantly.

> **CLAUSE §2cf.2: A NEW RULE BINDS FUTURE ACTIONS AND STOPS NOTHING THAT IS ALREADY RUNNING. Ruling a class obliges the ruler to SWEEP THE PROCESS TABLE FOR LIVE INSTANCES OF IT, in the same invocation as the ruling. `ps` for the pattern you just forbade, and stop your own — by explicit pid, never `pkill`, which matches its own invoking shell.**
>
> **And the operational sizing, measured rather than asserted: BOUND THE CENSUS FIRST AND WIDEN ONLY IF THE BOUNDED ARM COMES BACK EMPTY. `git grep` and a `-maxdepth`-bounded `find` over named directories answer the overwhelming majority of census questions in seconds; the unbounded disk walk is a LAST arm, run knowingly, and never while solvers are stalling.** `§2cw` requires both filter arms for a call-site zero — **that is an argument for aiming the second arm, not for pointing it at the whole disk.**

**STATE AT CLOSE, measured 23:36:55Z:** no sweep of mine is alive; `/proc/pressure/io full avg10 = 1.88` (was **43.24** at 20:34Z), load **3.28** (was **63.17**). **The box has drained. AND MY DEFERRED SWEEPS STAY DEFERRED: `§2cf.1` keys on SOLVERS RUNNING, not on pressure, and ansys, heat-transfer and MRF are still solving. A rule I wrote two hours ago does not become optional because the number it was written about improved.**

| amendment record | **v1.96** |
|---|---|
| clauses added | **1** (§2cf.2) · gate values changed | **0** · verdicts withdrawn | **0** · checks made to refuse | **0** (`D539`) |
| **self-reported violations of this team's own clause** | **1** (2h43m, after ruling) |
| deferred sweeps released tonight | **0** — the rule keys on solvers, not on pressure |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.97, 2026-09-11 — **§2cy `§2cf.1`'s TRIGGER IS A PROXY AND IT HAS NEVER DISCRIMINATED: THE RUNNING SOLVERS SUPPLY 0.0018 % OF THIS BOX'S BLOCK IO AND ZERO OF ITS READS, WHILE MY OWN LANES SUPPLY 459 MB/s. §2cz `§2cf.2` ORDERS AN ACTION THIS TEAM CANNOT PERFORM — A PARTIAL DEAD LEVER, FOUND BY TRYING TO OBEY IT. §2cf.3 A DISCIPLINE THAT LIVES IN THE CHARTER AND NOT IN THE BRIEF IS NOT IN FORCE ON THE LANE**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** All three raised by **this supervisor against this supervisor's own clauses of yesterday**, on measurement taken at 15:26–15:32Z today. `[lab-attributed]`. **No gate value moves; no verdict moves; nothing is made to refuse (`D539`).** **One clause of mine is REFUTED in its trigger, one is declared a PARTIAL DEAD LEVER, and the third repairs the reason all three of my lanes were violating the first within ten minutes of dispatch.**

### §2cy — **THE SOLVERS ARE NOT THE IO. MEASURED, NOT ARGUED.**

`§2cf.1` defers a corpus-complete census **"while solvers are running"** and says such a census **"runs when the box is not solving."** I wrote that yesterday at 20:39Z. Today I measured what the running solvers actually cost.

**THE WINDOW, 15:28:11Z → 15:29:41Z (90 s), `/proc/diskstats` on `nvme0n1` beside `/proc/<pid>/io` for both live solvers:**

| | read | written |
|---|---|---|
| **whole box** | 22,982,080 sectors = **11.77 GB** (130.7 MB/s) | 79,880 sectors = **40.9 MB** (0.45 MB/s) |
| `rhoCentralFoam` pid 316601 (ansys VMFL017-R3/L3) | **0 bytes** | 217,088 B |
| `buoyantBoussinesqSimpleFoam` pid 1233987 (heat-transfer T4e_IJ_f) | **0 bytes** | 139,264 B |
| **both solvers together** | **0 bytes — not rounded, zero** | **348 KB** |

**Solver share of the box's block IO in that window: 0.0029 %. Solver share of its READS: 0.000 %.**

**AND THE LIFETIME FIGURE, which no windowing objection can reach** — a 90 s window may fall between writeIntervals, so here is each solver's whole life: pid 316601 has run **3d 03h 07m 34s** and moved **589.9 MB** total → **2.18 KB/s**. pid 1233987 has run **23h 42m 54s** and moved **520.3 MB** → **6.09 KB/s**. **Together, 8.27 KB/s, averaged over every second they have existed.**

**WHAT THE IO ACTUALLY WAS.** A 15 s attribution sweep at ~15:31Z over every `/proc/<pid>/io`: `claude` pid 1982218 read **5.27 GB** (351 MB/s); a `ugrep -rn launch_k2d.sh … .` read **1.46 GB**; a `grep -rn 'geometric (non-empty' … verification/runs cases` read **145 MB**. **Top three ≈ 6.88 GB in 15 s ≈ 459 MB/s — the agent fleet, and one of those three is a search my own brief commissioned twenty minutes earlier.** `/proc/pressure/cpu full avg10 = 0.00` throughout: the box has idle CPUs and is read-starved, `§2cf` exactly.

**8.27 KB/s against 459 MB/s is 0.0018 %.**

> **RULED — §2cy: "SOLVERS ARE RUNNING" IS A PROXY FOR IO CONTENTION AND IT IS NOT THE PROPERTY. A CENSUS MAY BE DEFERRED FOR IO, AND THE DEFERRAL MUST CITE (a) THE MEASURED `/proc/pressure/io full avg60` AND (b) THE RUNNING SOLVERS' MEASURED SHARE OF BLOCK IO OVER A STATED WINDOW. THE EXISTENCE OF A SOLVER IS NO LONGER A GROUND ON ITS OWN.** Each deferral is a **fresh measurement**; a census deferred for IO is **re-tested, never re-deferred by recall**.
>
> **I SET NO THRESHOLD AND THAT IS DELIBERATE.** `§2cb` finding 1 is my own criticism of `STAGNANT_FLOOR = 0.5` — a constant whose provenance is thinner than the work it does, deciding live verdicts by 1 % margins. **Inventing a pressure threshold this afternoon would be the identical error committed knowingly.** The clause is therefore a **disclosure** rule, which needs no number, and **the threshold goes to Sanaa's desk** beside `STAGNANT_FLOOR`.
>
> **`§2cf.1`'s SUBSTANTIVE LIMBS ARE NOT WEAKENED — THEY ARE VINDICATED AND MADE UNCONDITIONAL.** Today's measurement is the best evidence the lab has ever had that unbounded searches saturate this box: three of them took 459 MB/s. **So "no repo-wide `grep -r`, no unbounded `find`, never walk `processor*/`, `VTK/`, `postProcessing/` or a time-directory tree" ceases to be conditioned on solving and applies ALWAYS** — because the contention it guards against is **agent-versus-agent**, which is what the numbers say, and not agent-versus-solver, which is what the clause assumed. **This is strictly MORE discipline in the common case and less in none.**

**WHY THIS IS A DISCRIMINATION FAILURE AND NOT A TUNING QUESTION (`§2c`).** The clause has now been evaluated in the two extreme states of its own domain:

| when | measured `io full` | solvers running | clause output |
|---|---|---|---|
| **2026-09-10 23:36:55Z** (my own board) | **1.88** — drained | three | **DEFER** |
| **2026-09-11 15:29:41Z** (today) | **75.20** — saturated | two | **DEFER** |

**A factor of forty apart, spanning the whole range the clause is about, and it returns the same answer both times. It has never once discriminated.** Ask `§2a`'s question of it — *what reading would make this clause say GO?* — and the honest answer yesterday was *none, while any solver exists*, which on a box that is essentially always solving is a permanent stop wearing a scheduler's name. **My deferred sweeps were not scheduled. They were parked, by a test that cannot return the other answer.**

**AND THE CAUSALITY IS INVERTED, WHICH IS THE PART I MISSED.** `§2cf.1` defers *this team's* census to protect *the solvers* from IO contention. Measured: the solvers read **nothing**, and the entire read storm is **the censuses themselves, competing with each other**. **The clause was protecting the one party on the box that was not in the contest.**

**OPERATIONAL CONSEQUENCE TODAY, and it cuts against me both ways.** The deferred `§2cx` arming sweep over the T-family and `verification/certificates/` is **released from the solver condition** — and **stays deferred anyway**, now for a reason that is measured and true: `io full avg60 = 75.20`, and **the cause is my own three lanes.** The right answer was never "wait for the solvers to stop." It was **"stop over-subscribing the disk with my own agents,"** which is a different action entirely, and one I could have taken yesterday.

### §2cz — **`§2cf.2` ORDERS AN ACTION THIS TEAM CANNOT TAKE. I FOUND OUT BY TRYING TO OBEY IT.**

`§2cf.2`, mine, yesterday: *"Ruling a class obliges the ruler to SWEEP THE PROCESS TABLE FOR LIVE INSTANCES OF IT, in the same invocation as the ruling. `ps` for the pattern you just forbade, and stop your own — by explicit pid, never `pkill`, which matches its own invoking shell."*

**I ran the sweep before writing `§2cy`. IT WORKED, AND THAT HALF IS ALIVE:** within ten minutes of my dispatching three lanes it found **three live violations** — a `bfs … / -name layerParameters.C` (an **unbounded whole-disk find**, the exact 4h17m shape `§2cf.2` was written about), a repo-wide `ugrep -rn … .`, and a two-root `grep -rn` that walks `processor*/` and time directories in breach of `§2cf.1`'s second limb.

**THEN THE SECOND HALF FAILED, TWICE, FOR TWO INDEPENDENT REASONS.**

1. **"YOUR OWN" IS NOT RECOVERABLE FROM THE PROCESS TABLE.** Every agent in this fleet — six supervisors, every lane — is a child of **one** `claude` pid (1982218). Each search's ancestry is `claude → bash -c <shell-snapshot> → the search`. **There is no agent id, team name or lane id anywhere in `ps`.** I could attribute exactly **one** of the three, and only by recognising a string my own brief had commissioned (`geometric (non-empty`). The other two I attributed by **guessing from content** — `launch_k2d.sh` looks like heat-transfer's K2d, `layerParameters.C` looks like cfd's snappyHexMesh work — **and a content guess is not attribution.** Under `§2cf.2` as written I would have had to either stop processes that may be another team's mid-flight work, or stop none.
2. **AND FOR THE ONE I DID OWN, THE ACTION WAS DENIED.** `kill -TERM 1989031`, explicit pid, no `pkill`, was **refused by this session's permission classifier** (*Interfere With Workloads*). **I did not route around it and I am not asking a peer to do it for me** — that is permission laundering across sessions (rule 9), and the denial is the user's decision, not an obstacle. **So the clause's mandated verb is unavailable to this team in this session, for its own processes, with correct syntax.**

> **RULED — §2cz: `§2cf.2`'s SWEEP LIMB STANDS; ITS *STOP* LIMB IS A PARTIAL DEAD LEVER AND IS REPLACED BY A VERB THAT IS ALWAYS PERFORMABLE. The obligation is SWEEP, then STOP WHERE YOU CAN, AND OTHERWISE DISCLOSE — by pid, with its command line, its measured IO cost and its elapsed time, to the chief and to the supervisor whose content it appears to be, naming the attribution as a GUESS where it is one.** **Disclosure can always be executed; termination cannot, and a clause whose only verb is the one you may be unable to perform silently converts into no obligation at all.** Filed to `docs/DEAD_LEVER_AUDIT.md` as a **PARTIAL** dead lever — the rarer and more dangerous kind, because the half that works produces the feeling that the clause is working.
>
> **AND A SECOND-ORDER CONSEQUENCE I AM NOT AUTHORISED TO FIX:** an agent fleet that is unattributable in the process table cannot be governed by any per-agent process rule, not just this one. **Making lane provenance visible in `ps` is a harness change and `harness/` is not mine to edit (rule 9). It goes on Sanaa's desk** as the enabling condition for every clause of this shape.

**THE THREE VIOLATIONS ARE DISCLOSED HERE UNDER THE VERB THIS CLAUSE INSTALLS**, attribution labelled: pid **1989031**, `grep -rn 'geometric (non-empty' … verification/runs cases`, 145 MB in 15 s — **MINE**, commissioned by my own brief. pid **1988579**, `ugrep -rn launch_k2d.sh … .` (repo-wide), **20.95 GB read cumulatively** — **GUESS: heat-transfer**. pid **1994631**, `bfs … / -name layerParameters.C` (whole disk from `/`), **GUESS: cfd**. **Neither guess is acted on by me.**

### §2cf.3 — **WHY ALL THREE OF MY LANES WERE VIOLATING `§2cf.1` TEN MINUTES AFTER DISPATCH**

Not defiance, and not ignorance on their part. **I wrote three lane briefs this afternoon and `§2cf.1` appears in none of them.** I told one lane to census the corpus and warned it about load in general terms; I never gave it the bounded-search form, the forbidden roots, or the clause's name. It then did exactly what an unbriefed competent agent does.

> **RULED — §2cf.3: A SEARCH-DISCIPLINE CLAUSE BINDS THE LANE ONLY IF IT IS IN THE LANE'S BRIEF. A supervisor dispatching work that will read the corpus states the bounded form IN THE BRIEF — the explicit roots, the `-maxdepth`, `git grep` with a pathspec, and the absolute exclusion of `processor*/`, `VTK/`, `postProcessing/` and time-directory trees — and does not rely on the lane having read this charter.** Lanes are not issued this document. **A rule the worker never sees is not a rule; it is a grievance waiting to be filed against someone who could not have complied.** This is the dispatch-side twin of `§2bl`: an absent check is neither passed nor failed, and an untransmitted rule is neither obeyed nor broken.

| amendment record | **v1.97** |
|---|---|
| clauses added | **3** (§2cy, §2cz, §2cf.3) · existing clause REFUTED IN ITS TRIGGER | **1** (`§2cf.1`) · existing clause made UNCONDITIONAL and thereby STRENGTHENED | **1** (`§2cf.1`'s substantive limbs) · existing clause declared a PARTIAL DEAD LEVER | **1** (`§2cf.2`'s stop limb) |
| gate values changed | **0** · thresholds adjusted | **0** (one more recorded for Sanaa) · verdicts withdrawn | **0** · checks made to refuse | **0** (`D539`) |
| clauses of mine refuted by me | **2** · sweeps RELEASED from a condition that never discriminated | **1** (`§2cx`'s arming sweep) · sweeps still deferred on a MEASURED ground | **1** (the same one) |
| desk items opened for Sanaa | **2** (an IO-pressure threshold; lane provenance in the process table) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.98, 2026-09-11 — **§2da AN OpenFOAM *CAPABILITY GAP* STOPS THE WORK; AN OpenFOAM *DEFECT* IS A BREAKAGE THE SUPERVISOR FIXES — AND THIS CHARTER'S `§2cv` PARAGRAPH PUT `snappyHexMesh`'s NEGATIVE-VOLUME DEFECT ON THE WRONG SIDE OF THAT LINE**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Occasioned by an owner directive relayed through the chief. **This clause RELEASES work; it makes nothing refuse (`D539`) and moves no gate, threshold or verdict.** `[lab-attributed]` as to the reading; the directive itself is `[SANAA-DIRECT]`.

### §2da — **THE DISTINCTION, IN HER OWN WORDS**

Sanaa, 2026-09-11 ~16:00Z, byte-exact:

> **no when i said openfoam issue i meant openfoam capabilties. The team can proceed to fix with what its supervisor decides the fix is.**

This reads back onto her 2026-09-10 16:15Z directive — *"Per usual the fixes continue UNLESS It's an openfoam issue. Else I want to see the runs."* **The carve-out was never about OpenFOAM code being broken. It is about OpenFOAM not being ABLE to do the thing.**

> **RULED — §2da, the test, and it is one question:** *could OpenFOAM do this if it were working correctly?*
> - **NO — a CAPABILITY GAP.** The solver, library or utility does not implement it, or cannot represent the physics asked of it. **This stops the work.** It is surfaced to her as a run and its evidence; no workaround is invented; no agent decides to route around a missing capability.
> - **YES — a DEFECT, CRASH OR BREAKAGE.** A wrong answer, a silent corruption, an exception, a tooling or build failure. **This is ordinary breakage: the OWNING SUPERVISOR decides the fix and proceeds**, `[lab-attributed]`, frozen, costed, queued, and **surfaced on the board either way.**
>
> **SURFACING IS UNIVERSAL AND IS NOT THE THING THAT WAS EVER CONDITIONAL. Only the STOP belongs to the capability gap.** The 16:15Z phrase *"surfaced, not worked around"* was carrying both duties at once, and that conflation is what this clause ends: **everything is surfaced; only a missing capability halts.**

### §2da.1 — **THE CORRECTION THIS CHARTER OWES AGAINST ITSELF**

`§2cv`'s closing paragraph (v1.94, at line **10078**) reads: *"the `snappyHexMesh` defect is **an OpenFOAM issue**, and the owner's standing directive is that OpenFOAM issues are **surfaced, not worked around**."*

**Under §2da that classification is WRONG, and it is wrong in the direction that costs a team its work.** The defect `§2cv` records is `snappyHexMesh` **producing 52,165 negative-volume cells of 128,230 — 40.7 % of the mesh — while printing all-zeros on its own final check and `"Finished meshing without any errors"`.** A mesher that silently emits invalid cells and reports success is **not OpenFOAM declining to do something it cannot do. It is OpenFOAM doing it wrong.** That is a defect, therefore a breakage, therefore **cfd's supervisor decides the fix and proceeds.**

**cfd IS UNBLOCKED ON THIS ITEM BY THIS CLAUSE**, and the unblocking is the point of writing it the same hour the directive landed. **The choice of fix is cfd's, not mine** — I classify, I do not prescribe their mesh route.

**AND WHAT IS NOT TOUCHED, stated so nobody reads a release where there is none: RULE 7 IS UNCHANGED.** The drafted upstream defect report stays **`NOT FILED` and PARKED**. **Fixing is not sending.** The lab repairing its own mesh has no bearing whatever on whether a report leaves this box, and **nothing leaves the box except by Sanaa** (rules 7, 8). *Parked is not cancelled*, and no reading of `§2da` converts a proceeding fix into a filed report.

**MEASURED, NOT ASSUMED, ON THE OTHER TWO CHARTERS I WAS ASKED ABOUT:** `docs/charters/CASE_PROTOCOL_CHARTER.md` contains **no occurrence of the token `openfoam`, case-insensitive** — it does not carry the 16:15Z clause in any form, so there is nothing there to append, and it is **Sanaa's byte-exact text and not mine to amend** regardless. `docs/charters/RESULT_PRIORITY_CHARTER.md`: **likewise zero occurrences.** **This charter was the only one of the three carrying it, and it carried it wrongly.**

| amendment record | **v1.98** |
|---|---|
| clauses added | **2** (§2da, §2da.1) · existing clause CORRECTED IN ITS CLASSIFICATION | **1** (`§2cv`'s closing paragraph, by appended addendum — the line is NOT edited, rule 6) |
| gate values changed | **0** · thresholds adjusted | **0** · verdicts withdrawn | **0** · checks made to refuse | **0** (`D539`) |
| teams UNBLOCKED | **1** (cfd, on the `snappyHexMesh` negative-volume defect) · standing rules relaxed | **0** (rule 7 expressly reaffirmed) |
| **lines whose number changed above this section** | **0** |

---

## Amendment — v1.99, 2026-09-11 — **§2db THE `§2d.1` GRANT FOR `roache_triple.py`: A GATE THAT DECIDES CORRECTLY AND EXPLAINS FALSELY, IN THREE OF SIX STATES, 100 % OF THE TIME — AND THE SUITE THAT NEVER LOOKED. §2dc THE RENDER FIELD IS A LIGHT CONVENTION, AND THE TRIGGER AS PHRASED WOULD RENDER A `NOT A RESULT`**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`).**

### §2db — THE GRANT

**THE DEFECT.** `scripts/roache_triple.py` at `:629-632`, on the `NOT A RESULT`
branch, appends to the delivered `row["why"]`:

> *"...NO GCI is quoted because the three values are not monotone"*

as the **`else` of a two-way branch over a SIX-state vocabulary**
(`NOT_A_RESULT_STATES` at `:182`: `DIVERGENT`, `STAGNANT`, `OSCILLATORY`,
`EXACT`, `DEGENERATE`, `NO_ORDER`). Everything that is not `DEGENERATE` is told
the reader it was non-monotone — **without ever consulting `row["monotone"]`,
which the same function computed at `:599` and carries in the same row.**

**IT IS UNCONDITIONAL, NOT OCCASIONAL, AND THAT WAS MEASURED RATHER THAN
ARGUED.** A sweep of both classifiers over 828k+ triples, with a planted control
on the sweep predicate itself, finds the state/monotone relation **structural,
with zero counterexamples**:

| state | `monotone` | n | stated reason |
|---|---|---|---|
| `DIVERGENT` | **always True** | 135,306 | **FALSE** |
| `STAGNANT` | **always True** | 20,932 | **FALSE** |
| `NO_ORDER` | **always True** | 4,571 | **FALSE** |
| `DEGENERATE` | always True | 6,737 | correct |
| `OSCILLATORY` | always False | 559,130 | **correct BY ACCIDENT** |
| `EXACT` | always False | 2,560 | **correct BY ACCIDENT** |

**Three of six states carry a false stated reason 100 % of the time.** The two
it gets right, it gets right without ever having asked — `OSCILLATORY` and
`EXACT` are classified on `ratio < 0` and `e21 == 0` before any other branch is
reachable. **A reason that is right only because the two branches happen to
coincide is not a reason; it is a coincidence that has not failed yet.**

**A PARTIAL REPAIR THAT STOPPED, AND THE HISTORY MATTERS.** The defect dates to
the instrument's first commit `9c69a79a9`, where the sentence was an
unconditional string and **all six states** were told "not monotone". The
`DEGENERATE` branch added at blob `78e56a3b` **was itself a repair of this exact
defect — it fixed one state of six and left five standing.** This amendment
finishes it.

**THE SAFETY BEHAVIOUR IS SOUND AND IS NOT TOUCHED.** `_seal` at `:664-667`
independently refuses any GCI beside a non-monotone or non-`CONVERGING` triple.
**No GCI leaked anywhere, in any affected row.** The gate DECIDES correctly. It
EXPLAINS falsely. **That distinction is the whole of this ruling, and it is a
distinction this charter has not previously had to draw.**

**I ALSO RECORD THAT I GOT PART OF THIS WRONG.** I briefed the censusing lane
that the human-readable path was clean — that `format_row` at `:700-705`
branches on `monotone` first and is therefore correct. **It is not clean.** For
monotone `DIVERGENT`/`STAGNANT`/`NO_ORDER` **both** of its branches miss, so
**no "GCI NOT QUOTED" line is emitted at all**, and `:708` then prints
`row["why"]` verbatim — **so the printed row carries the false sentence too.**
The blast radius is every printed grading output, not only the JSON. The lane
checked instead of believing me. **That is the behaviour this lab wants from a
lane and it is recorded as such.**

**SIX DELIVERED ROWS, FOUR FILES, THREE TEAMS.** `MRF_R1_GRADED_ROW.json`
(`DIVERGENT`, `monotone: true`, p = −5.2311); `MRF_R2_TRIPLE_AT_4000.json`
(p = −5.7784); `GRADE_F4S.json` (p = −0.3326); and **`T23G_GRADED.json`**, three
quantities, `STAGNANT`, `monotone: true`. **14 pre-registrations pin this
instrument by sha; five are already graded to landed verdicts.**

#### §2db.1 THE FOUR CONDITIONS, RULED

1. **DEMONSTRABLE ERROR — MET.** A row asserts "the three values are not
   monotone" while **the same row reports `monotone: true`**. This is not a
   preference and not a reading: it is **a self-contradiction inside one
   delivered artifact**, exhibited from the delivered code against its own
   delivered data.
2. **INDEPENDENT INSTRUMENT — MET, IN THE STRONGEST FORM THIS CLAUSE HAS SEEN.**
   `§2d.5` ruled a sha-frozen pre-registration qualifies because it cannot have
   been selected to move a verdict; `§2d.3.2` extended that to a standing
   `CLAUDE.md` rule. **Here the witness is narrower still and therefore stronger:
   the module's OWN `monotone()` at `:599`, which grades no reason string,
   reaches no verdict, and cannot know which direction any verdict wants.
   THE DELIVERED ROW IS ITS OWN WITNESS.** No external instrument is required,
   and none was consulted to establish the error.
3. **and 4. BITE IN FULL.** Six delivered rows carry published text, so
   `§2d.4.1` applies exactly. **REQUIRED: for each affected row, publish the
   pre-repair sentence verbatim beside the post-repair sentence, AND state
   explicitly that the VERDICT IS UNCHANGED — `NOT A RESULT` before and after,
   with no GCI ever quoted because `_seal` held.** That statement must appear in
   the record and must not be left for a reader to infer.

**DIRECTION — SATISFIED *A FORTIORI*, AND THIS IS THE CLEANEST DIRECTION TEST IN
THE SERIES.** `§2d.1` permits a repair to move a verdict in one direction only:
`PASS` or `GATE FAIL` **into** `NOT A RESULT`. **This repair moves no verdict in
any direction whatsoever.** Measured across **2,395 graded ladders**, patched
against unpatched agree on **every field except `why`** — verdict, band verdict,
`monotone`, states, orders and GCI presence all identical. **A repair that
cannot move a verdict at all is strictly weaker than one that may move it in the
permitted direction**, and so passes the direction test without needing its
indulgence.

> **RULED: the `§2d.1` exception is GRANTED for `scripts/roache_triple.py`, on
> all four conditions, with the row-level before/after published. The repair is
> LEGAL. The landed verdicts STAND — every one of them, unchanged.**

**WHAT THE GRANT DOES NOT DO.** It does not edit a landed record (rule 6): the
six rows receive a **dated correction** stating the false sentence and the
unchanged verdict, drafted by verification and **landed by their owning teams**,
cfd and heat-transfer. It does not re-grade anything. It is not a budget and not
a launch order.

#### §2db.2 THE REAL FINDING: A SUITE THAT TESTS WHETHER THE GATE *DECIDES* AND NEVER WHETHER IT *EXPLAINS*

**`row["why"]` HAS ZERO TEST COVERAGE.** It is written at `:615`, `:623` and
`:642`, read at `:708`, and **not one `check()` in the entire selftest
references it.** The field that lands **verbatim in delivered JSON verdicts** is
the module's only wholly untested output.

**AND THE FIXTURES ALREADY CONTAINED THE BUG.** Limb `(vi)` at `:953-956`
already drives `DIVERGENT (1.00, 1.02, 1.05)` and `STAGNANT (1.0, 1.03375,
1.06375)` — **both monotone, both emitting the false sentence on every run since
the instrument was written.** The limb asserted the verdict, the band verdict,
the absence of `GCI_pct`, and that the triples are printed. **It never read the
sentence those very rows carry.**

**THE SHARPEST EVIDENCE, AND THE ONE TO REMEMBER: the patched module scores
60/60 on the existing selftest, exactly as the unpatched module does.** A change
that corrects delivered verdict text for three of six states **moves not a
single existing check.**

> **§2db.2 RULED, AND IT BINDS BEYOND THIS INSTRUMENT: A FIELD THAT REACHES A
> DELIVERED VERDICT IS A GRADED OUTPUT AND CARRIES A CONTROL, WHETHER OR NOT A
> GATE READS IT.** A green suite over a field nobody asserts is not evidence
> about that field — it is silence about it. **Prose inside a verdict is part of
> the verdict.** Rule 1 already says honesty is carried by the value, the
> interval, the chip and the uncertainty channels and never by adjectives; this
> clause adds the converse — **where the lab does ship an explanatory sentence,
> that sentence is graded output and must be shown capable of being wrong.**

**OWED, AND NAMED AS OWED:** a bounded sweep for affected rows deeper than
`maxdepth 4` or in non-`.md`/`.json` artifacts (a `GRADING_OUTPUT.txt` is cited
by `VMFL076/RESULTS.md`), and the four campaigns pinned at the older
`8dee0d31` blob, **where all six states carry the false reason**. Both deferred
under `§2cf.1`; **both are bounds, not findings** (`§2cc`).

### §2dc — THE RENDER FIELD, AND A TRAP IN THE TRIGGER

Sanaa, 2026-09-11, byte-exact: *"whenever a case finishes and completes (i.e run
converged or is within bands of a known reference/ solution), an agent from the
designated team needs to render the stl file (3D geometry) then the mesh
paraview, better to do this as we go since well use them in the demos, instead
of us waiting for the day we shoot. (But only whenever a case is done and
checked)."*

**MY TERRITORY HERE IS NARROW AND I KEEP IT NARROW.** The rendering itself,
its tooling and its scheduling belong to the owning teams. One question was
routed to me — whether the Case Protocol per-case state file (`§6`) should carry
a `render` field — and one hazard is mine to raise because it is a verdict
question wearing a rendering costume.

**RULED: YES, a `render` field, as a LIGHT CONVENTION AND NOT A GATE.**
It records the paths of the STL and mesh renders for a done-and-checked case so
the rollup can show which ones have them. **It arms nothing, refuses nothing,
and gates nothing (`D539`).** **Nothing in the grading path may READ it** — it is
write-only with respect to every verdict, and a case with no render is not
thereby anything other than what its verdict says it is.

#### §2dc.1 THE TRAP: "PASS IN BAND" IS NOT A VERDICT, AND READING IT AS ONE WOULD RENDER A `NOT A RESULT`

The chief's reading — offered as correctable — gives the trigger as rule-4
complete **and** graded converged *"or `PASS` in band"*. **That phrase is
ambiguous and the ambiguity has a live example sitting in the repository.**

**`MRF_R1` carries `band_verdict: PASS` and delivered verdict `NOT A RESULT`.**
Its own record says so: *"Band verdict computed first and unconditionally: PASS
(4.453 in [4.0,6.0]) — turned to `NOT A RESULT` by the one-way gate."* That is
rule 5 working exactly as designed: the band is computed unconditionally so the
gate can only ever restrict it.

**So a lane reading "PASS in band" as `band_verdict == PASS` would render
`MRF_R1` — a `NOT A RESULT` — as a done-and-checked case.** And a render is
destined for a DEMO, where a picture of a case reads as a validated case to
every viewer who never opens the JSON.

> **RULED, INSIDE MY TERRITORY: THE RENDER TRIGGER READS THE *DELIVERED
> VERDICT*, NEVER THE BAND VERDICT.** A case is eligible when it is rule-4
> complete **and its DELIVERED verdict is `PASS`** (or a `CONVERGING` triple
> where a triple is claimed). **`NOT A RESULT`, `GATE FAIL`, `BLOCKED` and
> `PENDING` are not rendered — and a `NOT A RESULT` whose band would have passed
> is STILL NOT RENDERED.** The one-way gate exists precisely so that a
> restricted verdict cannot be read back out through its own unrestricted
> intermediate; **a renderer that reads `band_verdict` would be doing exactly
> that, and would be the first thing in this lab to defeat rule 5's one-way
> property — through a picture rather than through a number.**

**This is a clarification of the chief's reading, not a contradiction of it** —
the chief labelled the reading correctable and this is the correction. **Sanaa's
own words are satisfied either way**: *"only whenever a case is done and
checked"*, and a `NOT A RESULT` is precisely a case the lab has checked and
declined to stand behind.

**RULE 7 UNCHANGED.** Renders are demo artifacts and **stay in the box** like
everything else. Producing them is not sending them.

---

## Amendment — v2.00, 2026-09-11 — **§2dd `§2dc.1` IS SUPERSEDED BY THE OWNER, ON THE EXACT CASE I USED TO ARGUE IT. WHAT SURVIVES IS NOT THE TRIGGER BUT THE CAPTION. §2de ACTION OVER PLUMBING: SIX ITEMS OF MINE STAND DOWN**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** `[lab-attributed]` except where Sanaa is quoted. **No gate value moves; nothing is made to refuse (`D539`).**

### §2dd — I WAS OVERRULED, AND I SAY SO PLAINLY RATHER THAN READING MY CLAUSE NARROWLY UNTIL IT SURVIVES

**Hours ago I ruled `§2dc.1`:** the render trigger reads the **delivered verdict**, never `band_verdict`; a `NOT A RESULT` whose band would have passed is **still not rendered**. I built the argument on `MRF_R1` — `band_verdict: PASS`, `verdict: NOT A RESULT`.

**Sanaa, 2026-09-11, byte-exact:** *"About your 'done and checked' reading : 1. done and checked i think in this case can be at bit more loose (this is for demo purpose not for us and building knowledge), so whta i mean is ran on a fine mesh,with results within the tolerance band of a verification number, and if not, with a converged mesh. if converged trio exists the one i was to see on paraviw is the finest."*

**THAT IS THE BAND CRITERION, AND IT IS EXACTLY WHAT I RULED AGAINST.** Under her trigger `MRF_R1` — fine mesh, `Np` 4.453 inside `[4.0, 6.0]`, the band of a verification number — **IS renderable.** The one case I chose to make my argument is the case she has decided the other way.

> **RULED: `§2dc.1`'s TRIGGER IS SUPERSEDED. The render trigger is Sanaa's:
> a FINE MESH with results INSIDE THE TOLERANCE BAND of a verification number;
> failing that, a CONVERGED MESH; and where a converged trio exists, THE FINEST
> LEVEL is the one rendered.** No verdict is required for a render and **no
> verdict is conferred by one.**

**I DO NOT GET TO RESCUE THE CLAUSE BY READING IT NARROWLY.** She gave the ground herself — *"this is for demo purpose not for us and building knowledge"* — and **selecting demo footage is hers, not a verification gate.** A supervisor whose clause meets the owner's instruction head-on amends it; he does not reinterpret it until it survives.

#### §2dd.1 WHAT ACTUALLY SURVIVES, AND IT IS THE HALF THAT WAS ALWAYS MINE

My concern was never *which* cases get photographed. It was that **a picture reads as a validated case to every viewer who never opens the JSON.** That concern does not live in the trigger. It lives in the **caption**, and the caption is still governed by rule 1.

> **THE SELECTION IS LOOSENED; THE VOCABULARY IS NOT.** A case rendered under the
> demo trigger **may be shown**, and **may not be captioned, labelled, listed or
> narrated as `PASS`, as verified, or as validated when its delivered verdict is
> `NOT A RESULT`, `GATE FAIL`, `BLOCKED` or `PENDING`.** Where a rendered case
> carries a delivered verdict, **the render cites that verdict as it stands.**
> Rule 1 fixes the vocabulary for what the lab *says*; Sanaa fixes what the lab
> *films*. **These never conflicted, and `§2dc.1` confused them.**

**`§2dc` ITSELF STANDS UNCHANGED:** the `render` field is a light convention, not a gate; it arms nothing, refuses nothing (`D539`), and **nothing in the grading path may read it.** A render moves no verdict, and heat-transfer's separate hazard — **a renderer with write access to a graded tree** — is untouched by this amendment and still stands on its own.

**THE HONEST RESIDUE, NAMED RATHER THAN BURIED:** "within the tolerance band of a verification number" and "a converged mesh" are **the owner's words and are looser than this charter's `CONVERGING`/`PASS`**. I am not tightening them into my vocabulary by the back door — **the trigger is hers as stated.** Where a lane cannot tell whether a mesh is "converged" in her sense, it asks her rather than substituting `§2`'s definition and reporting that it followed orders.

### §2de — ACTION OVER PLUMBING: WHAT THIS TEAM STOPS DOING

**Sanaa, byte-exact:** *"I am re insisting what i said yesterday, i want as much actiona dn reaction as possible instad of plumbing, I want all th 3D cases i asked for and the multipoin tcompressible/ incompressible optimizations. When we finish these well run more stuff."*

**Her three named items for this team are LANDED as of this amendment**, and each unblocked a run or a grade:

| item | commit | what it unblocked |
|---|---|---|
| the calibration-append register repair | `bc5588bc7` | **every team's** rule-12 row |
| the freeze hook `:245` landing | `c185d7508` | her own named priority |
| `roache_triple.py:632` wording | `a7b3846d8` | three teams' delivered verdicts |

> **STOOD DOWN until a RUN or a GRADE depends on them:** the `§2cr` and `§2cx`
> instruments, `COMMIT_INTEGRITY_STANDARD` clause 6, the `§2cx` arming sweep,
> the six-brief audit, and the L-544 execution-witness machinery — **ruled in
> `§2db`/V-179 and deliberately LEFT UNBUILT.** **V-119 proceeds only as far as
> it takes to stop the shared-board sweeps**, which cost three teams work today;
> not one step further.

**THIS CLAUSE IS A PRIORITY RULING, NOT A RETIREMENT.** Nothing above is
withdrawn, no gate is loosened and no owed item is discharged by being deferred
— **`§2cc` applies to a lab's own backlog as much as to a corpus: a deferred
item that stops being written down has not been deprioritised, it has been
lost.** Each stands recorded here as OWED.

---

## Amendment — v2.01, 2026-09-11 — **§2df THE BOARD WRITE PATH: MY OWN V-175 RULING SENT FIVE TEAMS PAST TWO WORKING GUARDS, AND THE CURE WAS ALREADY ON DISK, SELFTEST-GREEN, UNUSED**

**Appended at the foot; nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** `[lab-attributed]`. **No gate value moves; nothing is made to refuse (`D539`).** This is the whole of what `§2de` permits V-119 to do: **stop the shared-board sweeps, and not one step further.**

### §2df — THE FINDING: THIS WAS NEVER A MISSING INSTRUMENT

Four shared-board sweeps in twenty-four hours — heat-transfer, dafoam, cfd, and cfd again at `c79d6d75a`, which **reverted 73 lines of two peers' board work.** I have been treating that as a gap to be filled by V-119. **It is not a gap. Both cures already exist, both are green, and nobody was using them — because I told them not to.**

**MEASURED THIS SESSION, ON DISK, BY ME:**

| instrument | state | what it does |
|---|---|---|
| `scripts/lab_state_section.py` | **`--selftest` PASS** | rebuilds ONE team's section **from the COMMITTED blob**; **round-trip proved BYTE-IDENTICAL** (`a4c71c33…` rebuilt == `a4c71c33…` at HEAD) |
| its planted controls | **both fire** | a foreign edit outside the section → **DROPPED**; a stray `## ` heading inside → **REFUSED** (exit 2) |
| `cases/RANS_LES_closure_models/_common/commit_private.sh` | live | **BOARD-CLOBBER GUARD** — refuses any commit that reduces the board's section or block count versus the parent |

**A foreign edit outside your section is DROPPED. That is the sweep, and the helper already deletes it.** The instrument was never wrong; **nobody was pointed at it.**

#### §2df.1 I POINTED THEM THE OTHER WAY, AND I SAY SO

**V-175 — my own ruling — mandated the RAW `git hash-object -w` + `git update-index --cacheinfo` splice on the shared board.** It solved the problem I was looking at (never re-read the 8.8 MB worktree copy) and **walked straight past both guards above**, because the raw form:

- **bypasses the BOARD-CLOBBER GUARD entirely** — nothing counts sections or blocks;
- **cannot drop a peer's foreign edit**, because it never reconstructs from the committed blob — it commits whatever bytes you assembled;
- **leaves a STALE WORKTREE behind a current HEAD**, which earlier today had silently hidden the entire v1.98 amendment that unblocked cfd, and would have been reverted by the next ordinary commit;
- **and cannot add a NEW path at all.**

> **RULED: `§2df` SUPERSEDES V-175's raw-splice instruction for `docs/LAB_STATE.md`.** The raw form remains correct for an **ordinary single-team file** — that is what every other commit in this session used. **For the shared board it is retired.**

#### §2df.2 THE WRITE PATH, IN ONE INVOCATION, SAME `$H` THROUGHOUT

```
H=$(git rev-parse HEAD)                      # ONCE: for --rev, for -p, for the CAS
python3 scripts/lab_state_section.py --repo . --path docs/LAB_STATE.md \
        --team <team> --section-file <your section> --rev $H --out <SCRATCH>
B=$(git hash-object -w <SCRATCH>)
export GIT_INDEX_FILE=<scratch>/idx && rm -f $GIT_INDEX_FILE && git read-tree $H
git update-index --add --cacheinfo 100644,$B,docs/LAB_STATE.md
T=$(git write-tree); git diff-tree -r --numstat $H $T   # ASSERT: one path, deletions 0
[ "$T" != "$(git rev-parse $H^{tree})" ] || exit 1      # empty tree == the assertion failing
C=$(git commit-tree $T -p $H -F msg); git update-ref refs/heads/main $C $H
git diff HEAD~1 HEAD --stat                             # post-commit verify, NOT optional
```

**The shared worktree copy is never written.** `--out` goes to scratch; the blob is staged from there.

#### §2df.3 `--add` IS MANDATORY — cfd's FINDING, ADOPTED, WITH ONE WORD CORRECTED

**cfd (block 157) found it and the fix is theirs and is right:** `--cacheinfo` **cannot add a path not already in the tree**, so a lane landing a **new** record commits nothing. **Adopted: the form above carries `--add` unconditionally.**

**Their characterisation is wrong on one word, and the correction STRENGTHENS their finding rather than weakening it.** They called it *silent*. **Measured, in a scratch repo, all three arms:**

| arm | result |
|---|---|
| `--cacheinfo` on a **NEW** path | **rc 128**, `error: cannot add to the index - missing --add option?` — **loud, and it names the missing flag** |
| `--add --cacheinfo` on a **NEW** path | rc 0, path staged |
| `--cacheinfo` on an **EXISTING** path | rc 0, staged (which is why a dozen board commits were unaffected) |

**It is not silent. It is rc 128 with the remedy printed.** That matters, because it means **the failure is caught by any `&&`-chained sequence, by an rc check, by the empty-tree guard and by the path-count assertion** — and a path-count assertion is **exactly what caught cfd's lane.** Their guards worked. **The hazard is real and the word was wrong; both halves belong on the record.**

> **A near-miss that was caught by a guard is evidence the guard works, and must be written down as such** — not upgraded into a silent failure. Overstating a defect retires a working control, and this lab has more to lose from a guard nobody trusts than from a flag nobody remembers.

#### §2df.4 WHAT THIS AMENDMENT DELIBERATELY DOES NOT DO

**The full V-119 per-team-source cutover stays DORMANT.** `docs/lab_state/*.md` are **UNTRACKED and STALE** (2026-08-31, predating the 2026-09-07 L-499 convergence); `merge_lab_state.py` **hard-refuses every real invocation at rc 7**; the merge cron is **not installed**; and cutover requires `MERGE_LAB_STATE_CUTOVER_AUTHORIZED=1` plus `--adopt`, **after the chief sequences it**. **None of that is touched here and none of it is authorised by this clause.** Reading a stale source there has already cost one team a stall.

**This clause changes a write path and nothing else.** No gate, no threshold, no verdict, no cutover. It is the narrow step `§2de` allows, and it is landed because **four teams lost work to a sweep that two existing green instruments would have refused.**

---

## Amendment — v2.02, 2026-09-12 — **§2dg GEOMETRIC SIMILARITY IS A PRECONDITION OF THE OBSERVED ORDER, NOT OF THE TRIPLE. A FAMILY WHOSE NEAR-WALL AND BULK REFINEMENT RATIOS DISAGREE MAY STILL BE `CONVERGING`, AND MAY NOT QUOTE AN ORDER OR A GCI FROM IT**

*lines whose number changed above this section: 0*

**Raised by cfd from its SUBOFF A1 family and routed to me by the chief. [lab-attributed] — decided by this supervisor under `§2`; no owner ruling was sought and none is claimed.**

### §2dg.0 The measurement that forced it

cfd measured a SUBOFF A1 family whose **bulk (cell-count) refinement ratio is 1.4079** while its **near-wall first-cell ratio is 1.7914**, because `nSurfaceLayers` runs 5-6-7-8 down the family and every level gains a layer on top of the surface refinement. **A 27 % disagreement is not a rounding artifact.** cfd registered it as a named weakness and moved no threshold, which is the correct order of operations and is why this clause exists instead of a quiet re-grade.

**cfd also checked before generalising, and that is worth recording as much as the finding:** MRF carries `addLayers false` at **every** level, so this mechanism is **NOT** the explanation for MRF's two negative observed orders (−5.2311, −5.7784). A team that measures the negative case before extending its own claim is doing the thing `§28.11` was written about.

### §2dg.1 The ruling

Roache's observed order `p = ln((f₃−f₂)/(f₂−f₁)) / ln(r)` consumes a **single `r`**, and a single `r` asserts that the whole domain refines together. Three quantities must therefore be kept apart, and this lab has been collapsing them:

1. **The STATE (`CONVERGING`, `DIVERGENT`, `STAGNANT`, `OSCILLATORY`, `EXACT`) is a property of the THREE VALUES** — whether they are monotone and whether the differences shrink. **It does not consume `r` and it survives a non-similar family. `CONVERGING` MAY STAND.**
2. **The OBSERVED ORDER consumes `r` and does not survive.** When the near-wall and bulk ratios disagree, the effective `r` — `(N_fine/N_coarse)^(1/d)` from total cell count — is a **volume-weighted average dominated by the bulk**, while the quantity of interest (drag, moment, Nusselt) is **largely produced in the boundary layer**. The formula then divides a boundary-layer error difference by the logarithm of a bulk ratio. **That is not a wrong number. It is a number about nothing**, and it must not be reported as a measurement of the discretisation order.
3. **The GCI consumes both `r` and `p` and does not survive. NO GCI MAY BE QUOTED** from a family that is not refinement-invariant near the wall. Rule 5 already forbids quoting a GCI when the three values are not monotone; this is the same prohibition reached by the other precondition.

### §2dg.2 The generalisation — and it is the part that matters, not `nSurfaceLayers`

The governed property is **REFINEMENT-INVARIANCE OF THE NEAR-WALL TREATMENT**. It breaks in two ways and `nSurfaceLayers` is only the visible one:

- **(A) THE GRID FAMILY IS NOT SIMILAR.** Layer parameters (`nSurfaceLayers`, `expansionRatio`, `firstLayerThickness`, `finalLayerThickness`, `minThickness`) vary by level. **Visible in the dictionaries** to anyone who looks.
- **(B) THE GRID IS SIMILAR AND THE SOLUTION FAMILY IS NOT.** A high-Re wall function (`nutkWallFunction`, `nutUWallFunction`, `epsilon/omega/kqRWallFunction`) whose validity depends on `y⁺`, in a family where `y⁺` is **never measured per level**. As the grid refines `y⁺` falls, the wall function leaves its valid band, and **each level is running a DIFFERENT EFFECTIVE BOUNDARY CONDITION.** The mesh is geometrically similar; the physics is not.

**(B) IS STRICTLY THE MORE DANGEROUS OF THE TWO, because (A) is legible in a dictionary and (B) is invisible unless somebody measured `y⁺`** — and a family that never measured it cannot tell you whether it happened. This is the live MRF hypothesis and the mechanism `SUBOFF §1.2` already diagnosed for R1b's `DIVERGENT` triple. **Both are instances of one clause, and a clause written only against `nSurfaceLayers` would have missed the one that is harder to see.**

### §2dg.3 What the record must PRINT — always, not only when it is bad

Beside every observed order, a graded record carries **BOTH ratios: the bulk (cell-count) refinement ratio AND the near-wall first-cell ratio**, and for any family using a wall function, **the per-level `y⁺` at the wall (min/max/mean)**.

**ALWAYS, AND THE "ALWAYS" IS THE WHOLE CLAUSE.** A number printed only when it is unflattering teaches every reader that its **absence means it was fine**; a number printed unconditionally makes its **absence a defect on the face of the record**. This lab has already paid for the other arrangement — `§2db.2`: prose inside a delivered verdict is part of the verdict, and a field that reaches a verdict carries a control whether or not a gate reads it.

### §2dg.4 The tolerance — I REFUSE TO INVENT ONE TONIGHT

**No numeric threshold is set by this amendment, and setting one by feel would be the defect this charter exists to prevent.**

- Where a pre-registration **registered** a refinement-similarity tolerance, **that tolerance governs**, and it was frozen before the answer was known, which is the whole of its evidentiary content.
- Where **none was registered**, the two ratios are **printed** and **no GCI issues**. The absence of a registered tolerance is not a licence to assume similarity; it is the reason the claim cannot be made.
- A general constant needs a **non-local justification**, exactly as `§2cb`/`V-121` refused to let the `0.20` admissibility constant rest on one campaign's convenience. **Commissioned, not guessed.**

### §2dg.5 THE ANTI-GAMING LIMB — THIS CLAUSE RESTRICTS AND CAN NEVER PROMOTE

**§2dg MAY NOT BE CITED TO TURN A `NOT A RESULT` INTO A RESULT.** A team whose triple came back `DIVERGENT` or `STAGNANT` may **not** argue that the family was non-similar, that the order is therefore uninterpretable, and that the negative verdict should be vacated. **The direction is fixed and it is the same one-way property rule 5 already fixes:** the gate can only turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse. **A non-similar family can be prevented from claiming a result. It can never be rescued into one.** If a non-similar family's order is uninterpretable, the honest consequence is that the rung has **not been measured** and must be re-run on a similar family — not that its bad news may be discarded.

### §2dg.6 Retrospective effect — NONE on any verdict, and that is deliberate

**NO DELIVERED VERDICT MOVES BY THIS AMENDMENT.** A GCI is not what decides `PASS`/`GATE FAIL` — the pre-registered band is — so withholding one flips nothing. What is owed on an already-delivered row flagged by the standing sweep is a **dated addendum** printing both ratios and, where a GCI was quoted on a non-similar family, **striking that GCI with its ground stated** (rule 6: originals are struck, never rewritten; and I do not edit another team's records). **Where an owning team finds that a struck GCI was load-bearing for a decision, that goes to the chief and, if it would move a verdict, to Sanaa. It is not settled here.**

### §2dg.7 Where the clauses land, and what is NOT mine

- **This charter: §2dg, above.** Mine, landed.
- **`scripts/roache_triple.py`: a NEW GROUND in `gci_refusal_reason()`** — the single function landed at `a7b3846d8` that already writes the reason a GCI is withheld. **OWED, not landed here.** It must meet `§2d.1`'s four conditions, and its direction is satisfiable *a fortiori* only if it is shown **restricting-or-neutral on every delivered row** — a repair that moved a verdict in the permissive direction would violate `§2dg.5` in code. **Its `why` string carries a control (`§2db.2`) or it does not land.**
- **`docs/standards/MESH_STANDARD.md`: NOT MINE — RAISED, NOT EDITED.** A grid family's registration should state its refinement ratio for **both** the bulk and the near-wall region rather than a single number. cfd owns that file; `§15.9 item 2` in it is already an open referral this team answered elsewhere, and I am not adding a second.

### §2dg.8 What is and is not claimed

**Claimed:** that `r` is a single number in Roache's formula and a non-similar family does not have one; that a cell-count ratio is volume-weighted and bulk-dominated; that state, order and GCI have different preconditions; that (B) is less visible than (A).

**Not claimed:** that any flagged family failed to converge — **non-similarity makes the ORDER uninterpretable, not the SOLUTION wrong.** That a numeric similarity tolerance is known. That any delivered verdict in this lab is wrong; the standing sweep is a roll call and **no verdict is moved by me**. That MRF's negative orders are explained — `addLayers false` **rules this mechanism out there**, and the `y⁺` hypothesis is under test by cfd and is **not** resolved by this amendment.
