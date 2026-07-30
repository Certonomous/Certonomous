# Certonomous Verification Charter

Version 1.0, dated 2026-07-30. Defines what counts as done. It binds every
solve, every gradient check, every ladder rung and every number that reaches a
record, a certificate or a camera surface.

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

**A diverged run poisons its own diagnostics.** Every derived quantity is
downstream of the divergence. L-19's corollary: a y-plus of 113 average on a
mesh four times finer than one reading 0.351 is not a mesh-sizing problem to go
fix, it is the diverged velocity field feeding back.

## 5. Detectors, metrics and signs

Three checks that cost nothing and have each already invalidated a published
conclusion.

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

## 6. FD tables are required for every adjoint

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

## 7. Failed gates ship as documented failures

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

**None of this conflicts with the no-failures-on-camera rule.** The demo
discretion charter is explicit that it governs the promotional surface only and
has no authority anywhere else, and that the campaign records, `LESSONS.md` and
`NOT_PASSING_REGISTER.md` stay complete and unredacted. A failed gate is
written up in full and is not filmed. Both rules hold at once, and anyone who
reads them as being in tension has read the demo charter's scope clause wrong.

## 8. The evidence record

**No result without one.** An evidence record is:

- The primary log, containing the solver's own convergence statement or reason.
- The coefficient or sampled-data file the number was read from.
- The case dictionaries, so the setup is inspectable.
- The gate verdict and the reference identity.
- The detector resolution for every quantity reported, per section 5.

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

## 9. Before believing any of it, check the primary source

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

## 10. Enforcement

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

**A live defect, recorded here rather than quietly fixed.** The consolidated FD
table in `demo-output/website/ACTIVE_RESEARCH.md` still shows A4's 10.04 percent
as PASS within the calibrated band. That band is the retired one. Under the
current standard in section 6 the same number grades CONDITIONAL, and two other
records already say so. L-1 applies: report both and say which artifact each
figure came from, then correct the stale one.

## Related

- `docs/charters/RESULT_PRIORITY_CHARTER.md`. Which quantity wins when two
  methods verify different ones.
- `docs/charters/REPORTING_CHARTER.md`. Where gate tables and FD tables land.
- `docs/standards/MESH_STANDARD.md`. The pre-solve mesh gate.
- `docs/UNCERTAINTY-DOCTRINE.md`. The three channels every result carries.
- `LESSONS.md` L-3, L-7, L-14, L-15, L-16, L-19, L-21, L-22, L-24, L-25, L-26,
  L-27, L-28, P1, P3, D12.
