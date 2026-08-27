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

**The grading standard, current and applied uniformly, including to cases
graded under the old band:**

- **PASS** at 5 percent or better on the aggregate **and** zero flagged
  components.
- **CONDITIONAL** between 5 and 15 percent, and it requires a per-component
  breakdown before it can be graded at all.
- **FAIL** above 15 percent **or** on any sign-flipped or unstable component,
  regardless of the aggregate.

The earlier "1 to 12 percent is normal" band was inferred from a single rung
and is **retired**. A charter that let a retired band keep grading would be
worse than none.

**The reporting protocol, five steps, none optional:**

1. Confirm the step sits in the well-converged plateau with a two or three
   point mini-sweep. Not assumed.
2. Report per-component or cosine-similarity agreement alongside the aggregate
   percentage.
3. Flag any component whose FD value changes sign, or moves by more than 50
   percent of its own magnitude across one decade of step. That is a real
   defect signature, not noise.
4. The harness-sound floor on this stack, for a case with no flagged
   components, is 2.5 to 5 percent vector-norm relative error. A number below
   that is a claim about the harness.
5. Central differences, `step_calc=abs`, step between 1e-3 and 1e-2.

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

**A live defect, recorded here rather than quietly fixed.** The consolidated FD
table in `demo-output/website/ACTIVE_RESEARCH.md` still shows A4's 10.04 percent
as PASS within the calibrated band. That band is the retired one. Under the
current standard in section 7 the same number grades CONDITIONAL, and two other
records already say so. L-1 applies: report both and say which artifact each
figure came from, then correct the stale one.

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
