# Certonomous Reporting Charter

Version 2.3, dated 2026-08-17. Freezes the morning report. It is the one
document the owner reads every day, so its shape is fixed and its sections do
not get reordered, merged or skipped.

Version 1.1 added two never-clauses on labels and on declared configuration,
and named `scripts/self_audit.py` in enforcement.

**What changed in 2.0, and it is the whole point of the revision.** Version 1.1
named the six sections and said they were required. It gave nobody a way to
tell a report that skipped one from a report that had nothing to say. Section 2
is new and it is the frame: exact heading strings, exact order, a computed
section count, a required source line per section, and two reserved words.
After it, "the report omitted the gates" is a string that is either present or
absent rather than a matter of opinion. Section 10 is new and carries the
reporting obligations that eight defects found this week put on the ladder,
gate and FD rows. The never list gains four label clauses, the reserved-word
clause, and one on configuration risk.
Nothing in 1.1 was weakened, and the six sections and their order are still
hers.

## 1. The line

> **Six sections, in this order, every morning, including the mornings with
> nothing good in them.**

The order is the owner's. Spend, ladder positions, gates, FD tables, refilled
queue, waiting list. A section with nothing in it prints its heading and the
word "nothing", because an absent section is indistinguishable from a forgotten
one.

**A morning report is a status document, not a persuasion document.** Nothing
here is a camera surface, so nothing here is curated. The demo discretion
charter has no authority over this file and never had: it governs the
promotional surface only.

**Nothing in the report is written from memory.** Every section names the
artifact it was assembled from. Where the artifact and the report disagree, the
artifact wins and both are shown, per L-1.

## 2. The frame, and it is what makes an omission detectable

Section 1 states a requirement. This section states the form the requirement
takes, so that breaking it is a check rather than a judgement. Every rule below
is testable by a reader holding the file and nothing else.

The report opens with exactly this block and then exactly these six headings,
in this order, each appearing once:

    CERTONOMOUS MORNING REPORT
    Date:       YYYY-MM-DD
    Assembled:  <UTC timestamp>
    Sections:   N of 6
    Missing:    none / <section numbers>

    ## 1. SPEND
    ## 2. LADDER POSITIONS
    ## 3. GATES
    ## 4. FD TABLES
    ## 5. REFILLED QUEUE
    ## 6. WAITING LIST

**Eight rules, and each one names the failure it catches.**

1. **The six headings are fixed strings and they are matched literally.** Not
   retitled, not translated into that morning's subject, not merged, not split.
   "Gate status" is not `## 3. GATES`. A report whose third heading is anything
   else is malformed, and it is reported as malformed rather than silently read
   past. This is the rule that turns a skipped section from a stylistic slip
   into a failed match.
2. **Nothing is added at the top level.** A seventh thing goes inside the
   section it belongs to, or it goes in section 6, or it is not in the report.
   The order is hers, and a report that grows a section has stopped being the
   thing she agreed to read every morning.
3. **`Sections: N of 6` is computed by counting the headings, never typed.** A
   report claiming 6 of 6 while carrying five headings is a worse defect than
   one claiming 5 of 6, because the first lies about its own shape. Where N is
   below 6, `Missing` names the section numbers.
4. **An empty section prints the single word `nothing` on its own line.** That
   word is reserved. It means the section was assembled, its source was read,
   and there was nothing in it.
5. **An unavailable source prints `PENDING: <path>` and nothing else.** That
   token is reserved too and it means the opposite of `nothing`: the section
   could not be assembled because the artifact behind it could not be read. A
   section printing `nothing` when it means `PENDING` is a false statement about
   the lab's state, which is why the two words are different.
   `scripts/gate_table.py` already uses PENDING this way for an act that has not
   run.
6. **Every section ends with a `Source:` line naming the artifact or artifacts
   it was assembled from**, as repository-relative paths. A section carrying
   content and no `Source:` line is malformed. This is section 1's "nothing is
   written from memory" made checkable.
7. **A cited artifact that is not on disk is a finding inside the report**,
   printed in the section that cited it, not left for the weekly audit. The
   audit is the backstop; the report is the first reader.
8. **One file per morning, retained under the campaign, never overwritten.**
   Section 8's "Since" column is unverifiable once yesterday's report is gone,
   and L-27 is the standing reason artifacts are retained rather than
   regenerated on demand.

**A malformed report is reported as malformed.** The honest output when a source
cannot be read is a report with a PENDING section, not a report with five
sections and no comment. Quietly emitting five sections is the single failure
this charter exists to prevent, and after this section it is a detectable one.

## 3. What exists today, stated honestly

No single artifact combines these six sections. The pieces exist, in named
files, and the report is assembled from them:

| Section | Source of truth today |
| --- | --- |
| Spend | Campaign record footers, the compute ledger, per-stage tables |
| Ladder positions | `demo-output/website/ACTIVE_RESEARCH.md`, `dafoam/DAFOAM_CASE_STATUS.md`, `campaign/CAMPAIGN_STATUS.md` |
| Gates | `campaign/NINE_ACT_GATE_TABLE.md`, generated by `scripts/gate_table.py` |
| FD tables | `dafoam/DAFOAM_CASE_STATUS.md`, `dafoam/ladder-a/A_stepsize_study.md`, the consolidated table in `ACTIVE_RESEARCH.md` |
| Refilled queue | `demo-output/website/agenda/docket.json` |
| Waiting list | `demo-output/website/agenda/BLOCKERS.md` |

Writing that table down is half the point of this charter. The report has been
reassembled by hand each time from whichever of these somebody remembered.

**One change from existing practice, and it is the owner's.** Spend is
currently a footer, at the end of a campaign record. In the morning report it
is the header. Same content, first position.

## 4. Section 1. Spend header

The first thing on the page, above everything.

    SPEND, <date range>
    Last night:     N core-minutes across M runs
    Of which:       U useful, W wasted on <what>
    Left running:   nothing / <what, and why>
    Week to date:   N core-minutes
    Dollar spend:   not readable from this instance, see waiting list

Rules:

1. **Measured, never estimated.** Core-minutes are wall seconds times ranks
   divided by 60, read off the runs. The compute budget charter's honesty rule
   governs.
2. **The useful and wasted split is required.** A record on file reads 692.5
   core-minutes total, 485.3 useful and 207.1 wasted on a failed attempt. A
   single total hides the lab's real cost per result.
3. **"Left running" is checked, not assumed**, and the report says how. The
   campaign convention is "nothing left running, verified after every stage".
4. **The dollar line stays as written until the billing blocker clears.** The
   instance cannot read CloudWatch or Billing. Printing an unverified number
   would be a fabricated measurement, and the line as written is more useful
   than a blank because it points at the unblock.
5. **A zero-compute night says so.** "No solvers run, no compute launched",
   which is already the standing header convention for read-only surveys.
6. **A spend figure states whether it is gross or cleaned**, and names the
   cleaning rule when cleaned. The compute budget charter's section 2 carries
   the measurement: 26.98 core-hours of host stall inside a 239.259 core-hour
   headline, 11.3 percent of it, and the cleaning rule in
   `scripts/self_audit.py` is a ledger row over 3600 seconds. Which figure the
   wall publishes is P-6.2 and is hers. That the report says which one it is
   printing is not.

## 5. Section 2. Ladder positions

Where every live ladder stands. One row per ladder, and a ladder that did not
move says it did not move.

    | Ladder | Rung | Position | Moved last night | Next rung | Blocked by |

Rules:

1. **Name the sense of "rung" being used.** The lab runs three and they are all
   live. A lettered program track with numbered cases, A1 through A6 and the B,
   C and D tracks. The three-rung maturity climb inside a single case,
   Feasibility then Physics then Gate. And a mesh or parameter refinement
   ladder where the rungs are successive meshes or successive Reynolds numbers.
   A position that does not say which is ambiguous.
2. **A blocked rung names what blocks it.** The hard ladder rule holds: a
   failed gate blocks every downstream rung, and F7b and F7c stay recorded
   BLOCKED on F7a's gate failure until it is explained.
3. **A ladder whose methodology forked reports the fork.** L-11 and L-17.
4. **A rung that stopped at its iteration cap is reported cap-stopped, never
   settled.** Section 10 carries the measurement.
5. **A refinement ladder's row carries its observed order only in the company
   section 10 requires.** An order on a line by itself, with nothing beside it,
   is the shape that let two ladders read as clean results this week while one
   was a divergence and the other was not a discretization order at all.

## 6. Section 3. Gates

The gate table, in its canonical column order, with no columns dropped:

    | act or case | gate | reference | measured | deviation | verdict | artifact |

Rules:

1. **Gate and reference stay in separate columns.** The verification charter's
   section 2 governs. A gate is a criterion the lab set. A reference is an
   external number.
2. **The artifact column is a path and it is checked.** A row citing an
   artifact that is not on disk is a defect and gets reported as one, in the
   row, under section 2 rule 7.
3. **Provenance is by artifact, not proximity.** `gate_table.py`'s own rule: an
   act's transcript is the source of truth for a row the viewer watched that
   act produce, because the campaign records are a different set of runs and
   mostly, not always, agree. A row whose act has not run prints PENDING and is
   never filled in from a neighbouring run that happens to be close.
4. **Failures appear.** A FAIL, an UNCONVERGED or a BLOCKED row is a row. This
   is not a camera surface.
5. **The verdict vocabulary is the fixed one.** PASS, GATE REACHED, GATE FAIL,
   NOT A RESULT, BLOCKED, and the fidelity chips separately.
6. **A verdict names the guard that held it, not only the verdict.** Two guards
   can reach the same verdict for different reasons, and a row recording only
   the verdict cannot show the morning the reason changed underneath it.
   Verification charter section 3.3.

## 7. Section 4. FD tables

Every adjoint rung that moved, plus a consolidated view.

The consolidated form, one row per graded derivative:

    | Rung | derivative | analytic vs FD, relative error | grade |

The grade column is not optional and it uses the current standard: PASS at 5
percent or better with zero flagged components, CONDITIONAL from 5 to 15
percent and only after a per-component breakdown, FAIL above 15 percent or on
any sign-flipped or unstable component regardless of the aggregate. The earlier
"1 to 12 percent is normal" band is retired and no row may be graded against
it.

Rules:

1. **Any rung that moved carries its full per-component table**, with the sign
   match column, not just its aggregate. The aggregate is the summary and the
   sign column is the finding.
2. **A step-size sweep reports its failed steps as rows.** A sweep that shows
   only the steps that worked is claiming a plateau it did not measure.
3. **Grades are recomputed against the current standard every time the table is
   regenerated.** A row carrying a retired grade is a defect. `self_audit.py`
   now recomputes rather than copying forward, which is what found the
   consolidated table in `ACTIVE_RESEARCH.md` still grading A4's 10.04 percent
   PASS against the retired band while two other records graded the same number
   CONDITIONAL. That row now reads CONDITIONAL and the number never moved.

## 8. Section 5. Refilled queue

What the lab queued for itself, in rank order.

    | Rank | id | objective | source_kind | est_core_min | cost_basis kind | status |

Rules:

1. **Rank order is the ranking function's**, descending expected knowledge gain
   per core-minute, then case-folded objective, then id. Deterministic, so two
   readers get the same queue.
2. **The `cost_basis` kind column says measured or estimate.** The distinction
   is the compute charter's honesty rule and it belongs where the owner can see
   it while she is approving things.
3. **Refill totals are stated.** The existing convention is the model: six
   proposals drafted and style-validated, 755 core-minutes costed.
4. **`approved-queued` is shown as its own status**, not folded into approved.
   It means she said yes and the machine had no room, and that is a different
   fact.
5. **Report the count by status.** Proposed, approved, approved-queued,
   dismissed, done.
6. **An item approved under a standing authorization says so in the row.** A
   blanket approval is not a per-item reading of the item. A queue that renders
   both the same way hides which ones she actually looked at, and the standing
   authorization's own decision note already records the distinction: blanket,
   not per item, so the hardness floor and the cost basis still gate what runs.

## 9. Section 6. Waiting list

Everything blocked on her, assembled from `BLOCKERS.md`.

    | id | What is blocked | Verified blocked how | Unblock action | Since |

Rules:

1. **Every entry carries its unblock action**, concretely enough to act on
   without asking a follow-up question.
2. **Verified blocked, not assumed.** The column exists so the distinction
   cannot be skipped.
3. **"Since" is a date and it is allowed to be embarrassing.** An item that has
   sat for a week should look like it has sat for a week.
4. **What proceeds regardless is named**, so a blocker is not read as holding
   more than it holds.
5. **Decisions waiting on her are listed here too**, in the escalation
   charter's shape: named options, cost of each, the lab's recommendation.

## 10. What a report has to say about a measurement

Eight defects this week sat in the space between a correct number and the
sentence printed beside it. The verification charter owns the measurement
rules. This section is the reporting side: what a row has to carry so that the
defect would have been visible in a morning report rather than a week later.

**An observed order never appears alone.** A row carrying a discretization
order carries, on the same row: whether the rungs are monotone, whether the
increments are shrinking or growing, where the Richardson value lands relative
to the highest rung measured, the assumed dimensionality, and whether the rungs
share one mesh recipe. The B-52 fourth rung fitted at p = 2.253, monotone and
inside the credible window 0.5 to 4, and it is a divergence: its increments
grow, 0.001857 then 0.002377 then 0.002702, and the Richardson value 0.06484
lands 24 percent above the highest rung measured. The second NACA 4412 ladder
fitted at p = 10.467 across a mesh-recipe change, coarse and medium both
`level (2 3)` and production alone `level (3 4)`, so it was never a
discretization order at all. Both numbers pass a reader who checks that an
order exists and looks sane, which is the check most readers actually perform.
`demo-output/website/campaign/NOT_PASSING_REGISTER.md` lines 516 and 548;
`models/curriculum/uq-studies/b52.json` and `naca4412_wing.json`.

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

**A rung that stopped at its cap is reported cap-stopped, not settled.** An
iteration cap is a budget, not a convergence criterion. The 208896-cell flat
plate rung was asked for 15000 iterations; at 15000 its Cd read 0.0028936144511,
1.05 percent above where it eventually settles, still falling by 1.04e-5 per
thousand, tail spread 4.44e-7 against the module's own 1e-7 gate. It took 36000
iterations to settle. Accepted as settled, that rung turns the finest triple's
increments from shrinking into growing and publishes the ladder as a divergence
at p = -0.745. The record now carries `settled` and the verdict that produced
it, and the report reproduces both. Commit `ec7ca9d5`,
`sdk/workflows/tmr_verification.py`.

**A verdict names the guard that held it.** A right answer reached for a wrong
reason survives every check that reads only the answer. The cylinder vortex
shedding ladder was declined for an observed order outside the credible window,
and fitted at the dimensionality its mesh actually has, that order moves from
3.633 to 2.422 and is inside the window. The ladder stays declined, now on an
independent guard whose extrapolated value overshoots the measured range and
which does not depend on dimensionality at all. The verdict never moved, the
reason did, and for a day the surface told the viewer something arithmetically
wrong about why. Commit `e3bd0e2f`, verification charter section 3.1.

**A number carries the rungs it was computed from, not the rungs it was
handed.** Both certifiers used to fit the finest three rungs and then measure
their fallback band and their extrapolation guard over every rung the caller
passed, so extra rungs widened the range the guard is a fraction of without
ever entering the fit. Measured on the flat plate 3264 / 13056 / 52224: handed
as three rungs, the Richardson value 0.00287237 sits 21.16 percent of the range
width above the top and is DECLINED. Handed with the coarse 816 rung in front,
the same value sits 8.48 percent above the top of a wider range and is
CERTIFIED at 1.99087e-5. One fit, two answers, decided by rungs the fit never
used. Commit `5675eb6b`.

**Every finding names the file it was read from, and somebody opened that
file.** A dimensionality defect found in the shared uncertainty module was
attributed to the flat-plate verification card. The card never had it: it has
always fitted at the dimensionality its own mesh has, and it reproduces its
published order. The two were conflated because both compute an order and only
one was opened, and the wrong attribution reached a proposal and a briefing
before anybody checked. A row in this report that attributes a defect to a
named artifact is asserting that somebody read that artifact.
`demo-output/website/tmr/flatplate_sst.json`, `sdk/chief_engineer/uq.py`,
docket `w8-an-audit-attribution-is-a-claim`.

**A defect is attributed to a family only after that family's own files show it
uses the thing.** A generator finding recorded max aspect ratio worsening under
refinement, 97.87 to 167.50, on a pyHyp extrusion, and it was carried to the
NACA 4412 as the likely cause of its ladder trouble. The 4412 is snappyHexMesh
throughout and its aspect ratio improves under refinement, 53.5 to 26.8 to
13.4, so the metric moves the opposite way. Its real degradation is
non-orthogonality at 74.96 against a 70 gate and layer coverage down to 58.3
percent. `demo-output/website/dafoam/GENERATOR_FINDING_pyhyp_aspect_ratio.md`
and `models/curriculum/results/naca4412_wing.json`.

**A result is named for what produced it, not for what was handed in.** A polar
was published under the name of a surface it was not computed from: the act
took only the span from the received body, solved its own parametric section at
camber 0.04 at 0.4 chord, and labelled the curve NACA 0012 with lift-to-drag
peaking at zero incidence, which a symmetric section cannot produce. Measured
rather than reasoned from the name: the received `naca0012_wing.stl` reads 0.00
percent camber and 0.00 degrees incidence, while the solver's own `wing.stl`
reads 3.98 percent camber at 0.38 chord. The surface was right and the label
was wrong. Commit `3db36388`. A report row naming a body is naming the body the
number came out of.

**An uncertainty budget names its largest term.** Multifidelity fusion cut the
race estimator standard error from 0.02832 to 0.000863, a factor of 33, and the
budget it produced records `high_fidelity_model_form: null`: the solver
model-form term, never measured, had become the largest contributor and was the
one term with no number in it. Further tightening of the estimator would have
been effort spent on the term that had already stopped mattering.
`demo-output/website/mfmc_error_budget.json`. The result priority charter's
section 4.5 carries the rule; this is the row that shows it.

**A figure is printed at the precision of the derivation that produced it, and the
uncertainty of its inputs is stated as an interval where the quantity is defined — never by
deleting digits.** Digits record *what was computed*; an interval records *what is known*.
They are different statements and a figure needs both. Truncating a figure to its
input-supported precision destroys reproducibility — a reader can no longer re-derive the
subtraction — without conveying the uncertainty, because a shortened number still reads as
exact. Adopted by the chief 2026-08-15.

**This clause fixes a FORM. It names no figure and no sentence, and naming either is
prohibited.** There is no reference sentence to copy under it, and no digit string it blesses
or forbids. A normative clause that pins a number is a claim generator: it keeps producing
copies of itself after the world it described has moved, and every copy reads as
independently sourced. Three such clauses were found in this corpus in one week, one of them
*ordering* surfaces to state a figure that had already been withdrawn. The shape to copy is
`demo-output/website/CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md` §4 clause **(b-1)**
(`65659488`), which mandates a form and prohibits designating a wording; the instrument that
grades clauses of this shape is `scripts/check_normative_clauses.py`, docket **D119**.

Two rulings that tried to settle a digit count came first and both were refuted, in opposite
directions, which is why this one settles neither: docket **D127** records a chief ruling that
a derived quantity be rewritten `0.001365` → `0.001366`, refuted by execution because it took
a printing of the basis for the basis, and then that same row's successor guess that the
honestly-supported precision was *"nearer `0.0014`"*, refuted by measurement because the
propagated interval `[0.0013153, 0.0014028]` straddles `0.00135`, so even the four-decimal
rounding is undetermined and only one significant figure is stable
(`demo-output/website/campaign/MARGIN_PRECISION_INTERVAL_2026-08-15.md` §2.4, committed
`eadcd112`). A coarser single figure is not more honest than a finer one; it is a different
unsupported claim, and that is the whole reason the answer here is an interval and not a digit
count.

Nothing already written is rewritten under this clause and it is not authority for a sweep. It
governs what is written next, and it says so on its own face. The margin family in
`demo-output/website/campaign/BOARD_RESCORE_2026-08-14.md` §3.1 stands exactly as committed:
those are correctly-rounded printings of quantities derived from the most precise inputs the
lab holds, which is what this clause asks for, and the measurement that produced the clause
changed zero instances and recorded that it had. Where a live claim quotes a figure whose
inputs carry a printing interval, the interval goes **beside** it, once, at the point where
the quantity is defined; it is not scattered across every surface that repeats the figure.

## 11. What the report never does

- **Never omits a section.** An empty section prints `nothing`, and section 2
  is what makes the omission detectable rather than arguable.
- **Never prints `nothing` where it means `PENDING`.** Those are two different
  statements about the state of the lab.
- **Never rounds a spend number to look tidy.**
- **Never curates.** Failures, wasted compute and stale rows all appear. The
  no-failures rule is a camera rule and this is not a camera surface.
- **Never quotes a number without its artifact.**
- **Never prints a label the number did not earn.** A confidence interval is a
  confidence interval, a refinement band is a refinement band, and a gate
  threshold is neither. The verification charter's section 6 governs, and it
  governs here too: the report is not a camera surface, and that makes it a
  place where a mislabelled number is more likely to be believed, not less.
- **Never supplies a confidence level the source did not state.** A page in this
  lab defaulted the level to 95 percent whenever a verdict carried none, which
  is a surface asserting a statistic on its own authority. All 253 recorded
  verdicts that carry a band happen to state 95 percent, so nothing visible
  changed when the default went. What went was the licence, and the licence was
  the defect. Commit `f710fb59`, `sdk/chief_engineer/control_room.html`.
- **Never renders an absent band as a value.** A missing band is absent and the
  value stands alone. The card that read `0.6544 ± n/a (n/a)` was printing the
  string "n/a" into a numeric slot, which is a number-shaped thing that is not
  a number. Same commit.
- **Never lets a qualifier travel off the row it was measured on.** A drag
  comparison's own sentence, "within 7 percent of Ahmed, Ramm and Faltin 1984,
  C_d 0.285", was spread into every card of one report, including the lift card
  and the mesh row, where a drag qualifier is nonsense. A grade travels with
  every row of one report, because every row of one report carries one grade. A
  reason does not, because it is a statement about one comparison. Commit
  `6880e4f3`.
- **Never repairs a label at the consumers when the source is what is wrong.**
  Two defects this week were one string each. A verdict reason reached every
  card, chip and sealed page with `Cd` where the typesetter keys on the
  underscore to see the index, so one variable was set as two plain letters
  while every other variable on the same surface was set properly. And a
  control-room trace named itself by its series key, where stripping the
  separator flattened the one variable that really was an index and opening it
  out set "history" under the C, on five acts at once, with no act-side wording
  able to fix it because the character was eaten before the typesetter saw it.
  Neither string was ever a label. The fix is at the source that emits it, once,
  not at the five surfaces that render it. Commits `63352fce` and `cfe4e383`.
- **Never states a fleet, a wall time or an iteration count the run did not
  produce.** Same section. What a report says about how a number was made is
  subject to the same evidence test as the number.
- **Never reports a run as clean when the monitor raised a configuration risk.**
  CONFIGURATION RISK sits outside the FATAL, FLAG and WATCH ladder on purpose:
  "nothing fatal" is a verdict on the arithmetic, and a configuration risk is a
  statement about the host. A run can be numerically spotless and carry one, and
  the report carries both facts. `MONITOR_STANDARD.md` S11.
- **Never resolves a disagreement silently.** Where two records disagree, both
  appear with the artifact each came from. L-1.
- **Never reports a job as finished on a monitor's say-so.** L-5 and L-6: an
  agent reporting "waiting" or "standing by" is handing off, not working, and a
  process exiting is not a job succeeding. `launch_solve.sh --check` tests the
  claim.
- **Never carries an em dash or an en dash.** The rule covers every surface and
  the report is a surface.

## 12. Enforcement

- `scripts/gate_table.py` generates section 3 from act transcripts and prints
  PENDING rather than guessing.
- `scripts/self_audit.py` re-derives published headlines from the artifacts
  they cite and reports every disagreement. It runs weekly, it names what it
  found and why, and it never edits a surface. It is a review aid with expected
  false positives, tuned that way on purpose: a false positive costs a reading,
  a false negative costs a published number nobody rechecks. Two of the three
  behaviours the old generator proposal existed for already live in it: a cited
  artifact missing from disk is a finding, and FD grades are recomputed against
  the current standard rather than copied forward.
- The agenda's style rails reject a proposal whose visible fields carry a dash,
  a raw URL, an internal path or a banned word, so section 8 inherits clean
  text.
- ~~Sections 1, 2, 4 and 6 of the report are assembled by hand today.~~
  **Superseded 2026-08-04: the emitter below assembles all six.** ~~**The
  frame in section 2 is unchecked until the checker below exists.**~~
  **Superseded 2026-08-01: it exists.** `scripts/morning_report.py --check
  <report>` reads a report somebody wrote by hand and validates it against
  section 2, naming the rule that failed rather than the fact that something
  did. Exit 0 accepted, 1 malformed, 2 the frame holds and a cited artifact is
  not on disk. Seventeen cases in `sdk/tests/test_morning_report.py`, each one
  a report a human could plausibly hand in.

  Two readings the checker had to make, recorded here because a checker that
  interprets the frame silently becomes a second unwritten rule:

  - **A `nothing` section still needs its `Source:` line.** Rule 4 defines the
    word to mean the section was assembled and its source was read, and the
    only evidence for the reading is the line naming the source.
  - **A `PENDING` section does not.** Rule 5 says the token prints nothing
    else, and the point of the token is that the source could not be read, so
    requiring a `Source:` line under it would require the thing that failed.

  What the checker cannot do is notice a section that is present, well formed
  and wrong about the lab. It reads the frame, not the content.

> **PROPOSAL, half taken.** The old generator proposal was split in two and the
> smaller half is built, above. The emitter is the larger half and can follow,
> reading the audit's JSON output for the parts that already exist rather than
> reimplementing them. P-8.1 in `PROPOSALS_OPEN.md`.
>
> **Superseded 2026-08-04: both halves exist.** The emitter is
> `scripts/morning_report.py --emit`, and it self-checks against the frame
> above before anything is written; one file per morning is retained under
> `demo-output/website/campaign/reports/`. It reads the six primary sources
> directly rather than the audit's JSON, because the audit reports
> disagreements, not sections, and that reading is recorded in P-8.1. Where a
> source carries prose rather than a field this charter asks for, the emitter
> reproduces the source's own words and says which columns it could not
> source; it never fills one by judgement. Nine cases in
> `sdk/tests/test_morning_report_emitter.py`.

## Related

- `docs/charters/COMPUTE_BUDGET_CHARTER.md`. The spend header's content.
- `docs/charters/VERIFICATION_CHARTER.md`. Gate columns, FD grading, verdict
  vocabulary, the label rules in section 6, the order and guard rules in
  section 3, and attribution in section 14.
- `docs/charters/RESULT_PRIORITY_CHARTER.md`. Section 4.5, the largest term.
- `docs/charters/ESCALATION_CHARTER.md`. What lands on the waiting list.
- `docs/charters/GOALS_AND_PROPOSALS_CHARTER.md`. The queue's rank order.
- `docs/standards/MONITOR_STANDARD.md`. The severities the report reproduces.
- `LESSONS.md` L-1, L-5, L-6, L-27.

## Amendment record

**Version 2.1, dated 2026-08-17. A style amendment, measured at frame `101079fd`.**
The sections above were brought to the owner's standard for a durable
record: em dashes and en dashes replaced by ordinary punctuation, and the
result of each replacement read back against the clause it sits in.

| what the amendment did | figure |
| --- | --- |
| em dashes replaced in the live sections | 3 |
| en dashes replaced in the live sections | 0 |
| em dashes left standing inside dated records | 5 |
| en dashes left standing inside dated records | 0 |
| clauses opened and declined, listed below | 2 |
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
1. §10's precision clause is quoted verbatim, and cited by line range, in a live grading record. Restyling the quoted sentence would falsify that quotation without changing what the clause requires, so the clause was left alone.
2. The three strike-in-place blocks in §12 record what earlier versions said. They were left byte-identical.

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

## Amendment record, continued: headline metrics in the opening block (2026-08-27)

**Dated addendum, 2026-08-27, appended at the foot; append-only. One reporting
requirement added on the owner's directive. No clause above is altered, widened
or narrowed; no line above this section changed number; the header's version
line is deliberately left untouched, because this addendum inserts nothing and
edits nothing above itself.**

**§1 — Sanaa's text. This is the authority.** From her standing directives of
2026-08-27T16:54Z, captured verbatim at
`etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md`, §2:

> Headline metrics every report: CPU %, GPU %, queue depth per team,
> idle-minutes per resource.

**§2 — operationalisation. `[lab-attributed]`, and overrulable without touching
§1. Where §2 appears to add a requirement §1 does not state, §1 governs.**

**Where the metrics go, and why not where a reader might first put them.** They
go **in the opening block**, beside `Date`, `Assembled`, `Sections` and
`Missing` — **not as a seventh heading.** §2 rule 2 is explicit that nothing is
added at the top level, and the six headings are hers. Metrics are a property of
the morning the report describes, not a seventh thing the report is about, so
the opening block is their home. The block becomes:

    CERTONOMOUS MORNING REPORT
    Date:       YYYY-MM-DD
    Assembled:  <UTC timestamp>
    Sections:   N of 6
    Missing:    none / <section numbers>
    CPU:        <pct> %
    GPU:        <pct> % / no GPU attached
    Queue:      <team>=<core-h> ... (one token per team, all six named)
    Idle:       <resource>=<minutes> ... (one token per resource)

**Four clauses, and each names the failure it catches.**

1. **A metric that was not measured says so, and never prints a number.** These
   four lines are subject to §10 exactly as every other figure in the report is:
   a value carries how it was obtained. A CPU % taken from another agent's relay
   rather than from this box is marked `VERIFY`, not printed bare.
2. **`GPU: 0 %` IS A FALSE ZERO AND IS BANNED.** No GPU is attached to this box;
   a GPU is a separate instance launched per run. When no instance exists there
   is nothing to measure, and the honest token is **`no GPU attached`**. A `0 %`
   in that state is a reader-visible claim that a GPU was observed idle, which
   is a different fact from no GPU existing — the standing-rule-3 doctrine
   (a zero from a reader not shown able to see a non-zero is not evidence)
   applied to a metric rather than to a comparator. The same holds for
   `Idle:` — a resource that does not exist has no idle minutes.
3. **`Queue:` names all six teams, including the ones at zero.** A queue depth
   omitted is indistinguishable from a queue depth of zero, and the two are the
   opposite of each other: zero with a live runner is a starved queue and a
   planning defect under her FREEZE-AHEAD ≥ 3; omitted means nobody looked.
   A team that owns no compute resource prints `n/a`, not `0`.
4. **Idle minutes are a measurement, and the cost derived from them is
   derived.** Idle-minutes come from the runner's own record. Any dollar figure
   attached is labelled **derived, not measured** — the box cannot read its own
   billing (`COMPUTE_BUDGET_CHARTER.md` §5), and `CLAUDE.md` rule 12 fixes the
   rate as owner-stated.

**§3 — the scope limit, stated rather than left as a silent half-measure.**
Her directive says *every report*. **This charter governs the morning report,
and that is all this amendment can reach.** The other report shape in daily use
is the supervisor-to-chief report, whose five fixed headings live in
`.claude/agents/*.md` — **generated** from `harness/teams.yaml` by
`harness/generate_agents.py`. Landing her metrics there is a `.claude/`
configuration change, and **`CLAUDE.md` rule 9 is that no agent makes such a
change on another agent's say-so.** It is therefore **on Sanaa's desk**, named
here so the gap is visible: **until she rules, supervisor reports carry the
metrics as content under their existing headings, and the generated
definitions are not edited.**

| what the amendment did | figure |
| --- | --- |
| reporting requirements added | 1 |
| clauses altered, widened or narrowed | 0 |
| lines whose number changed above this section | 0 |

## Amendment record, continued: a time stamp is a MEASUREMENT (2026-08-27)

**Dated addendum, 2026-08-27, appended at the foot; append-only. One reporting
requirement added, on the chief's referral with its own provenance. No clause
above is altered, widened or narrowed; no line above this section changed
number; the header's version line is deliberately left untouched.**

**§1 — the clause, adopted as the chief worded it.**

> **Every time stamp in a report, board block or message is read from `date -u`
> in the same invocation that writes it; a time that was not read from the clock
> is not written. The session log's own timestamps are authoritative where they
> disagree.**

**Rationale, in the referral's own terms: a stamp is a measurement.** An invented
one corrupts every rate, idle-minute and ETA derived from it — and Sanaa's §2
headline metrics (2026-08-27T16:54Z) make **idle-minutes per resource** a
reported quantity, so a wrong stamp is now a wrong metric, not just untidy prose.

**Provenance, recorded because a rule without its instance decays into etiquette.**
Supervisor report stamps ran ahead of the box clock: cfd's *"19:55Z"* and
*"20:00Z"* reports arrived before 19:39Z, and the chief's own messages between
16:24Z and 16:46Z carried stamps up to **13 minutes ahead**, logged as a
correction at 16:47Z. **The chief's disclosure of its own instance is what makes
this a rule rather than a reprimand.**

**§2 — where the defect IS and IS NOT, measured before this was written
`[lab-attributed]`.**

**The board is clean.** All **48** distinct `2026-08-27` timestamps in
`docs/LAB_STATE.md`, in **any** format, were compared against the box clock:
**zero are ahead of it.** **The named instances are in the REPORT and MESSAGE
channel, not on the board**, and the clause should be read as binding hardest
there — that is where nothing is committed, nothing is diffed, and nothing else
catches it.

**This team's own nine board stamps were checked against the commit that carried
each**: every one is **≤ its commit time**, most identical to the second, worst
lag **25 s**. **The practice costs nothing and is already achievable** — that is
the positive control on the clause, not a claim of virtue.

**§3 — a live ON-BOARD instance of the same class, which is not a future stamp.**

`docs/LAB_STATE.md` carries a dafoam block stamped **`2026-08-27T18:4xZ`** — a
literal `x` in the minutes field, annotated *"(`date -u` at write)"*. **It is not
ahead of the clock and it is still not a clock reading**: a stamp with a wildcard
digit is an *approximation presented in the format of a measurement*. **§1's
wording already reaches it — *"a time that was not read from the clock is not
written"*** — and it is named here so the clause is understood to cover
**rounding, redaction and approximation**, not merely invention. **For dafoam.**

**§4 — a second finding that this amendment does NOT fix, disclosed because it
defeated this team's own first scan.**

**Six teams use at least four different stamp phrasings** — `**Section
updated:**`, `**Section last written:**`, `**Section block written:**`, and a
form naming the writer as a *persona*. **This supervisor's first scan matched
only one of them and returned a clean zero across what looked like the whole
board while actually seeing ONE team.** It was caught by running a control, and
the 48-stamp figure in §2 is the re-derived one.

**That is the coverage-as-census defect this team has now published against
itself three times today** (`L342_GRADER_AUDIT` Addendum 1; Addendum 7's
anchored-scan ruling; this). **`scripts/check_harness.py` flags a section older
than its own territory, which requires PARSING these stamps — four formats is a
parser problem, not a style problem.** **A single canonical stamp line is
recommended and NOT imposed here:** the board's section format is not this
charter's to set, and prescribing one lab-wide is a convention change for the
chief to route and Sanaa to approve.

| what the amendment did | figure |
| --- | --- |
| reporting requirements added | 1 |
| clauses altered, widened or narrowed | 0 |
| board stamps found ahead of the clock (48 checked, any format) | **0** |
| on-board approximated stamps found | **1** (dafoam, `18:4xZ`) |
| distinct stamp phrasings across six teams | **4** — recommended, not imposed |
| lines whose number changed above this section | 0 |

## Amendment record, continued: THE CLOCK-STAMP CLAUSE HAS TWO CLASSES OF TIME, AND MY OWN CENSUS OF IT WAS WRONG BY 100 (2026-08-27)

**Dated addendum, 2026-08-27, appended at the foot; append-only. No clause above
is altered, widened or narrowed. One scope defect is recorded as RECOMMENDED AND
NOT ADOPTED, because permitting a class of times the clause's literal words
forbid is a WIDENING and widening a charter clause is Sanaa's, not this team's —
the same line this team drew four hours earlier on the two Roache admissibility
clauses (`docs/standards/ROACHE_ADMISSIBILITY_SPEC.md`, `commit:aaf0bed6`). The
header's version line IS bumped, 2.1 -> 2.2, discharging the rule-6 version-bump
requirement that the two preceding amendments each deliberately left undone and
disclosed as left undone; no line above this section changed NUMBER.**

**§1 — WHAT HOLDS, AND IT IS STRENGTHENED, NOT RETRACTED.**

The preceding amendment's central claim was that no board stamp runs ahead of the
box clock. **It holds on a scan far wider than the one that produced it.** Clock
read `date -u` in the measuring invocation: **2026-08-27T21:27:32Z**. Reading
`git show HEAD:docs/LAB_STATE.md` with a **form-agnostic** matcher — every
ISO-ish stamp anywhere in the file, any date, any phrasing, anchored to no
section-header wording at all — **449 dated stamps, 391 not ahead, 10 ahead.**

**ZERO WRITE-TIME STAMPS ARE AHEAD OF THE CLOCK.** All ten of the ahead readings
are the second class described in §2 and none of them is a defect.

**§2 — THE SCOPE DEFECT: A PROJECTION IS NOT A CLOCK READING AND MUST STILL BE
WRITTEN. RECOMMENDED, NOT ADOPTED.**

The clause reads *"a time that was not read from the clock is not written."*
**Read literally, that forbids every ETA and every timeout bound in the lab** —
and the reporting contract REQUIRES them: a `Runs live` line without an ETA is an
incomplete report, and Sanaa's §2 headline metrics make projected idle-minutes a
reported quantity.

**All ten ahead-of-clock readings at HEAD are legitimate and each is a
projection**, verified by reading the enclosing sentence rather than the token
(`L-360`): wrapper timeout bounds `2026-08-28T05:17:47Z`, `05:30:47Z`,
`2026-08-28T05:17Z`, `05:30Z` and `2026-08-29T01:58Z` (dafoam's four W2R
wrappers and D8R's bound, nine occurrences), and one solver ETA
`~2026-08-28T04:20Z` (heat-transfer's `T15_UP_f`, one occurrence).

**So a checker built on the clause as worded returns TEN FALSE POSITIVES ON ITS
FIRST RUN — and every one of them lands on a team doing exactly the right
thing.** That is `L-362`'s shape once more: not a defective clause and not a
defective practice, but a **false positive at their intersection**.

**THE RECOMMENDED WORDING, for Sanaa, not adopted here:**

> A time stamp is of one of two classes and the class is visible in how it is
> written. A **MEASUREMENT** — when a thing happened, or when this was written —
> is read from `date -u` in the same invocation that writes it. A **PROJECTION**
> — an ETA, a timeout bound, a scheduled close — is **derived**, and is written
> with its derivation shown: the clock reading it was computed FROM and the
> interval added to it. A projection presented as a bare future time is
> indistinguishable from an invented measurement and is the thing this clause
> forbids.

**The exemplar is already on the board and it is dafoam's**: *"pids 251492
(phase4, 129,600 s from 17:16:42Z -> 2026-08-28T05:17Z)"* — base reading,
interval, derived time, all three shown. **The rule being recommended is a
practice one team already keeps; it is not a new burden invented at a desk.**

**§3 — THE CENSUS DEFECT, AND IT IS AGAINST MY OWN §3. 1 -> 111.**

The preceding amendment's own table records **`on-board approximated stamps
found | 1 (dafoam, 18:4xZ)`**.

**MEASURED AT HEAD, FORM-AGNOSTICALLY: 111, ACROSS ALL SEVEN SECTIONS OF THE
BOARD.** Split by form, because the second form is the larger half and is the one
that defeated the earlier scan:

| form | count | how it was missed |
| --- | --- | --- |
| **DATED** approximation — `2026-08-27T19:2xZ` | **48** | seen |
| **BARE-TIME** approximation, no date at all — `19:0xZ`, `06:5xZ` | **63** | **invisible to a matcher that requires a date** |
| **total** | **111** | |

By owning section: **dafoam 42, ansys-verification 27, cfd 21, heat-transfer 14,
CHIEF 5, closure 1, verification 1.** **This team's own section carries one, and
the chief's carries five.** **Measured on the board AS IT STOOD when the clause
landed (`8f55958e`, 2026-08-27T19:41:54Z): 101.** So the figure published as
**1** was, at the moment of publishing, **101 — an undercount by 100.**

**AND THE MECHANISM IS THE ONE THAT AMENDMENT ITSELF NAMED.** Its §4 disclosed
that a first scan matched one stamp phrasing, saw ONE team, and returned a clean
zero across what looked like the whole board; it then reported a **re-derived**
figure. **The re-derivation fixed the PHRASING axis and never touched the FORMAT
axis** — it still required a date, and 63 of the 111 carry no date. **A scan
corrected along one axis reads as a corrected scan.** This is the **fifth**
publication of the coverage-as-census defect by this team today, and the first
one to occur **inside the correction written to fix the fourth.**

**§4 — THE CLAUSE IS A LIVE LEVER, AND THIS IS THE MEASUREMENT THAT SHOWS IT.**

A clause with no measured effect is a dead lever and belongs in
`docs/DEAD_LEVER_AUDIT.md`. **This one is not.** Across the **21** commits
touching `docs/LAB_STATE.md` after the clause landed at **19:41:54Z**, the added
lines carry **10 approximated stamps in 8 commits**:

| team | commits carrying an approximated stamp, post-clause | tokens |
| --- | --- | --- |
| dafoam | `3ade7856` `8e2593e2` `24e8f3f7` `5c868cf2` `a2d29137` `787db192` `9782af88` | **9** |
| heat-transfer | `a6b13c90` | **1** |
| cfd, closure, verification, CHIEF | none | **0** |

**Four of six teams wrote zero approximated stamps in the two hours after the
clause landed. The whole residual is nine tokens from one team and one from
another.** **Three independent methods agree to the token**: the board census
moved **101 -> 111** (delta **10**); the per-commit sweep of added lines finds
**10**; and a negative control run on four compliant commits (`3cc7fc35`,
`8438f44e`, `458f741d`, `0762932e`) returns **empty** from the same reader.

**ONE POST-CLAUSE INSTANCE IS NOT ON THE BOARD AND IS NAMED HERE BECAUSE THE
CLAUSE COVERS MESSAGES TOO.** The chief's re-formation brief to this team at
21:2xZ carries an approximated stamp in its opening line. **It is named for the
same reason the chief named its own 13-minute instance when this clause was
referred: a rule whose first enforcement skips the referrer decays into
etiquette.** **No fault is asserted — the clause is two hours old and the
practice it replaces is months old.**

**§5 — THE PLANTED CONTROL, DERIVED FROM THE ARTEFACT AND NOT FROM THE SEARCH.**

`L-363` says do not take the verification pattern from the claim; Addendum 9 to
`L342_GRADER_AUDIT` sharpened it to **do not take the plant from the search.**
So the control here plants **three** things this scan was NOT built around: a
future stamp in a **persona phrasing** matched by no pattern in §4 of the
preceding amendment; an approximation with the wildcard in the **seconds** field
where every real instance carries it in the **minutes**; and a **negative** limb
— a bare date with no time, and a bare time with no date — which must NOT count.
**The reader found both plants (total 449 -> 451, ahead 10 -> 11, approximated 48
-> 49) and rejected the negative limb.** **Both limbs fired.**

**§6 — NOT CLAIMED.**

The preceding amendment's **48 distinct 2026-08-27 timestamps** is **NOT shown
wrong**: the same quantity measured on the board as it stood at `8f55958e` is
**58** and at HEAD is **80**, and this team has **NOT** measured what it was at
the hour that amendment was written. **The board grew; that figure is not
retracted and no claim is made about it either way.** Nothing here re-grades any
row, and no stamp anywhere is corrected by this document — **the 111 are named,
not edited**, because they sit in six other teams' sections and a stamp is its
writer's to repair.

| what this amendment did | figure |
| --- | --- |
| clauses altered, widened or narrowed | **0** |
| clauses recommended to Sanaa, NOT adopted | **1** (the measurement/projection split) |
| write-time board stamps found ahead of the clock (449 scanned, form-agnostic) | **0** |
| ahead-of-clock readings that are legitimate projections | **10 of 10** |
| on-board approximated stamps, corrected from the preceding amendment's **1** | **111** |
| of those, invisible to a matcher requiring a date | **63** |
| approximated stamps written AFTER the clause landed | **10**, in 8 of 21 commits |
| teams writing zero approximated stamps post-clause | **4 of 6** |
| version | 2.1 -> **2.2** |
| lines whose number changed above this section | **0** |

## Amendment record, continued: A COMMIT MESSAGE IS A RECORD, AND IT IS THE ONE RECORD THAT CANNOT BE CORRECTED (2026-08-27)

**Dated addendum, appended at the foot; append-only. ONE reporting requirement
WIDENED — from documents, board blocks and messages to **commit messages** — on
the chief's referral with its own provenance. No other clause is altered; no line
above this section changed number. Version 2.2 -> 2.3.**

**§1 — THE PROVENANCE, AND IT IS THE STRONGEST INSTANCE YET BECAUSE THE SAME LANE
GOT IT RIGHT AND WRONG IN ONE ACT.**

A cfd lane on F12 Arm E (`commit:6b011629`, `commit:2b7cd6eb`) wrote **every stamp
inside its pre-registration by shell substitution from `date -u`** — all correct —
and **hand-typed the stamps in both COMMIT MESSAGES**: **21:47Z against a real
21:39:54Z**, and **21:52:12Z against a real 21:48:33Z.** The second was **in the
future of the clock a minute later, which is how the lane caught itself.**

**The discipline was present and the channel was not covered.** The clause as it
stood named *"a report, board block or message"* and a commit message is none of
those three by name — **so the lane was compliant with the letter and produced two
fabricated measurements anyway.**

**§2 — WHY THE COMMIT MESSAGE IS THE STRICTEST CASE, NOT MERELY ANOTHER ONE.**

Every other record this charter governs can carry a **dated correction**. A
document gets an amendment; a board block gets a later block; a message can be
followed by another message. **A commit message cannot.** It is sealed into the
object graph by the sha that names it, and rewriting it rewrites history — which
this lab's git rules forbid outright.

> **So the one channel the clause did not name is the one channel where the error
> is PERMANENT.** A wrong stamp in a document is a defect with a remedy; a wrong
> stamp in a commit message is a defect with none.

**§3 — THE CLAUSE, WIDENED, ADOPTED AS THE CHIEF WORDED IT.**

> **A time stamp reaches a document, a board block, a message OR A COMMIT MESSAGE
> only by substitution from `date -u` in the writing invocation. A typed stamp is
> a fabricated measurement.**

**Read together with v2.2 §2's measurement/projection split, which stays
RECOMMENDED AND NOT ADOPTED**: a projection — an ETA, a timeout bound — is not a
clock reading and must still be written, with its derivation shown. **Nothing in
this widening resolves that; it is still Sanaa's.**

**§4 — THE MECHANISM, SPECIFIED, BECAUSE A RULE AGENTS MUST REMEMBER IS WEAKER
THAN ONE THE TOOL PERFORMS.**

`.git/hooks/pre-commit`, `commit_private.sh` and `append_record.py` all sit on the
commit path. **Where a helper composes or accepts a commit message it should stamp
it itself, by substitution, so the correct behaviour is the DEFAULT rather than a
thing each lane must remember.** **Specified, NOT built** — those instruments are
not in this team's folder scope, and `.git/hooks/pre-commit` is separately on
Sanaa's desk as an **untracked** file that should be a frozen instrument.

**A planted control is required of any such change and both limbs must fire:** a
message carrying a **typed** stamp must be **refused**, and a message carrying a
**substituted** stamp must **pass** — a guard shown only to reject is not shown to
discriminate.

**§5 — WHAT IS NOT CLAIMED.**

**This team did NOT re-derive the two cfd figures**; they are the lane's own
disclosure, relayed, and the mechanism is what is adopted rather than the numbers.
**No commit message anywhere is corrected by this amendment and none can be** —
§2 is the reason. **How many typed stamps exist in the lab's commit history is
`NOT MEASURED`**, and quoting a figure here would repeat the coverage-as-census
defect this team has published against itself six times today.

| what this amendment did | figure |
| --- | --- |
| reporting requirements widened | **1** — messages -> **commit messages** |
| clauses altered, narrowed or retired | **0** |
| channels the clause now names | **4** |
| channels where a wrong stamp is PERMANENT | **1 — the commit message** |
| mechanism | **specified, NOT built** |
| typed stamps in lab commit history | **NOT MEASURED** |
| version | 2.2 -> **2.3** |
| lines whose number changed above this section | **0** |

## Amendment record, continued: **[SANAA-DIRECT] FREEZE-AHEAD COUNTS REPAIR-REGISTRATIONS — "QUEUE DEPTH 0 WITH OPEN FINDINGS IS IMPOSSIBLE BY DEFINITION"** (2026-08-28)

Appended at the foot; nothing above edited. `lines whose number changed above this section: 0`,
proved by a byte-prefix check against HEAD in the commit that lands this section — the first
**59442** bytes are byte-identical, **1030** lines before.

**Sanaa's words, verbatim, 2026-08-28** (captured at
`etc/sessions/2026-08-28T1701Z_sanaa_directives_control_regrade_freezeahead.md`; **the
2026-08-27 standing-directives file carrying §2 is NOT edited** — this section is the amendment):

> Queue depth 0 is a rule violation with an honest cause — so fix the rule, not the teams: when
> the nearest candidates are blocked on findings, the finding-repairs are the queue: they're
> frozen, capped, schedulable work items like any case. Amendment: "Freeze-ahead counts
> repair-registrations; a team blocked on findings freezes the repairs and runs them — queue
> depth 0 with open findings is impossible by definition."

**What it changes for the `Queue:` heading.** Depth is no longer *"frozen case registrations
ready to launch"*. It is **frozen, capped, schedulable work items**, and a **repair-registration
counts** — a finding with a named artefact, a cap and a frozen success criterion is a queue item
in exactly the way a solve is. **A team reporting `Queue: 0` while carrying open findings is now
reporting a contradiction**, and the report is wrong before the queue is.

**⚠ AND IT CORRECTS THIS TEAM'S OWN FINDING FROM SIX HOURS EARLIER, AGAINST THIS TEAM.**
`DEAD_LEVER_AUDIT` §8.2 measured **queue-ready 0 for all five teams** and §8.3 mitigated it:
*"the empty queue is a consequence of [the fleet being killed by the weekly limit], not an
independent planning failure by any team."* **Under this amendment that mitigation is
substantially weaker and I withdraw it as written.** The fleet's death explains why **no new
CASES** were frozen. It does not explain the absence of **repair-registrations**, because the
repairs were freezable the entire time — **findings do not require a live fleet to be written
down, capped and frozen.** The honest restatement: **the fleet's death explains the case queue,
and nothing explains the repair queue.**

**AND THIS TEAM IS ITSELF IN VIOLATION, WHICH IS THE PART THAT MAKES THE CORRECTION COST
SOMETHING.** Verification closed 2026-08-28 with **more open findings than any other team** —
the `grade_f3s.py` selector defect, **9 LATENT** ordering-key sites, **78 candidate sites in 28
files**, the 11 ansys "SAFE" sites whose *reason* is `NOT MEASURED`, the host-blind `EXEC`
clause — and **a queue depth of 0.** By the amendment's own words that state is **impossible**,
so the defect is this team's before it is anyone else's. **A supervisor who measures every other
team's starved queue and not its own has built a one-way instrument** — the shape
`DEAD_LEVER_AUDIT` §7.2 already recorded against this team today.

**Operationally, for the next report from any team:** `Queue: <team> N` counts **cases +
repair-registrations**. Where `N = 0`, the report states **either** that the team has **no open
findings** — a claim, checkable against its own audit rows — **or** that it is in violation and
names the findings it has not yet frozen. **`0` on its own is no longer a reportable value.**
