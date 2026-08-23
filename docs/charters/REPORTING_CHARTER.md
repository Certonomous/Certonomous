# Certonomous Reporting Charter

Version 2.1, dated 2026-08-17. Freezes the morning report. It is the one
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
