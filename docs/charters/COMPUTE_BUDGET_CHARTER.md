# Certonomous Compute Budget Charter

Version 1.2, dated 2026-08-05. Governs what the lab is allowed to spend, how it
counts what it spent, and the contract between the lab and the machine it runs
on.

Version 1.1 adds the gross-versus-cleaned clause to section 2, after the audit
measured 11.3 percent of the published solver core-hours to be host stalls that
re-derive perfectly from the ledger and are still not solver cost.

Version 1.2 defines the two terms once, precisely, in section 2, and records
that the reporting half is now carried out on the morning-report path: every
core-minute figure the spend section prints carries `basis: gross` or
`basis: cleaned` inline. The credentials wall still publishes its gross figure
alone; changing the wall is curation and stays hers.

## 1. The line

> **Every budget is measured, and every hold on the box expires by itself.**

Two clauses because the charter guards two different failures. The first is a
spend number that was estimated and then quoted as though counted. The second
is a machine that runs for a month because somebody switched off the thing that
stops it and went home.

## 2. The unit, and the honesty rule attached to it

**Core-minutes.** Wall seconds times MPI ranks divided by 60. That is the unit
in the docket, in every campaign record, and in the spend footer. It is not
wall time and it is not a dollar figure.

The cost-honesty rule is already in force in `sdk/chief_engineer/agenda.py` and
this charter restates it because it is the whole basis of the first clause of
section 1:

> `est_core_min` is either derived from measured history, meaning the ledger's
> wall seconds for the same evaluation family or a prior graded solve of the
> same body, with the derivation quoted in `cost_basis`, or it is a default
> that `cost_basis` plainly labels an estimate. **No cost is ever presented as
> measured unless a record backs it.**

Real `cost_basis` strings, both kinds, so the difference is visible:

- Measured: "measured, the tutorial rung cost 3.51 core minutes so a sweep of
  eight step sizes plus reruns is bounded".
- Measured, with a derived exponent: "measured, using the cost exponent of
  1.514 derived from this ladder's own two most recent rungs rather than the
  shallower 0.714 assumed earlier".
- Estimate, labelled: "estimate; the finest rung holds 337,334 cells and the
  next roughly doubles it".
- Estimate, labelled and flagged: "estimate from the paper's stated iteration
  count combined with our own measured per solve adjoint cost; flagged as
  needing a timed pilot before it is trusted".

The last one is the model. An estimate that names what would upgrade it is
worth more than a confident number.

**A cost basis may not cite a run the lab has since superseded, withdrawn or
graded out of band.** This clause exists because the clause above had a hole
in it and the lab fell through twice. "A prior graded solve of the same body"
is measured history right up until the proposal exists to *replace* that
solve, and then it is not history, it is the defect. A repair is a different
job from the run it repairs, and a run that stopped being right early is
cheap partly because it stopped being right early, so the error has no known
direction to be conservative in.

Both instances are on the record and both were under:

| priced at | from | the measured job | factor |
| --- | --- | --- | --- |
| 3.04 core-min | the NACA 0012 graded solve's own wall time, the solve the repair replaces | 180 to 240, measured on the NACA 4412 precedent that repaired the same layerless mesh | ~15x |
| 4.64 core-min | the NACA 4412 credential record's `wall_minutes`, which belongs to a superseded refinement-2 act and not to the ladder that produced the graded drag | one rung of that ladder alone measured 1,574.2 s of meshing plus 278.6 s of solve at 4 ranks | not yet re-priced |

Naming a superseded run in order to disclose it is the opposite of pricing
from it and stays allowed. `cost_basis_violations` in
`sdk/chief_engineer/agenda.py` refuses the priced form at intake and names the
run; the drafter that emitted the first instance now reports the prior wall
time as a floor on the repair and prices at the labelled default instead.

**A measured total that includes infrastructure stalls is not measured solver
cost.** Measured is not the same as clean. The published `solver_core_hours`
counter on the credentials wall re-derives exactly from the ledger, which is
the check that matters and it passes, and it still carries 26.98 core-hours of
host stall inside a 239.259 core-hour headline, 11.3 percent of it. The
evidence that these are stalls rather than solver cost is not a judgement
call: six rows near 16,300 seconds land in two tight wall-clock clusters and
are shared across two independent solver families, which no per-solver cost
mechanism can produce, against a cylinder median of 2.4 seconds. **A spend
figure states whether it is gross or cleaned, and names the cleaning rule.**

**The two terms, defined once. Every other document points here rather than
redefining them.**

- **Gross**: the sum of core-minutes over every ledger row whose timestamp
  falls in the stated window, with no row excluded for any reason. A gross
  figure re-derives from the ledger by summation alone, which is its virtue:
  it can be checked by anyone with the file and no judgement.
- **Cleaned**: the gross figure minus the rows the stall rule matches. The
  stall rule is the one in `scripts/self_audit.py` and there is exactly one:
  **a ledger row over 3600 wall seconds is an infrastructure stall, not
  solver cost.** The threshold's justification is the measured clustering
  above, not an assumption, and a cleaned figure names this rule, because a
  cleaned figure with an unnamed cleaning rule is a judgement wearing a
  number's clothes.

A figure that is neither, or that does not say which it is, is not published.
Waste (a failed run that really did burn solver time) stays INSIDE both
figures and is reported by the waste split in section 6; cleaning removes
what was never solver cost, the waste split labels solver cost that bought
nothing, and conflating the two would launder waste as stall.

**Carried out on the reporting path, 2026-08-05, under the standing
charter-iteration directive (P-6.2; her ruling on it stands open and one word
reverts it).** The morning report's spend section, the one published spend
surface assembled by machine (`scripts/morning_report.py`), prints
`basis: gross` or `basis: cleaned` inline on every core-minute figure it
emits, prints both the gross and the cleaned night figure, and names the
3600 second rule in the section body. A figure line without a basis label is
a tested failure, not a style slip. **The credentials wall is the remaining
half and it is hers**: it still publishes its gross headline alone, the audit
reports the contamination weekly, and whether the wall carries both numbers
is a curation decision this charter does not make.

This is also why the wall-time monitor exists and why its threshold is
governed. Every one of those six rows was recorded ok at the time, at 1070 and
2214 times its own solver's 99th percentile.

## 3. Per-rung budgets

**Every proposal carries `est_core_min` before it is queued.** A proposal with
no cost is disqualified under charter 1.

The standing defaults, which apply only when nothing measured is available and
which `cost_basis` must label as defaults:

| Kind | Default core-minutes |
| --- | --- |
| A new capability | 60 |
| A written report | 20 |
| One ladder rung | 20 |
| A benchmark-resource bump | 30 |

**A rung estimate states the iteration count it assumes, and the evidence for
it.** The default above prices one rung. It does not say how long that rung
takes to settle, and settling is the half that overruns.

The flat plate's finest rung came in at **483.6 core-minutes against 327, a
factor of 1.48**, and the whole overrun was iterations: it was asked for 15,000,
read 1.05 percent above its settled value with the coefficient still falling by
1.04e-5 per thousand, and took 36,000 to settle. Its cells were estimated
correctly. Nothing in the estimate asked about the settling, and 202.7 of those
483.6 core-minutes went on a first pass the module then refused.

**This is measured, not a caution.** Fitted from the mega-batch ledger,
`demo-output/website/mega-batch/COST_SCALING.md`: wall time carries an exponent
of essentially one on iterations in both families that record them, 1.156 on
time steps and 1.026 on SIMPLE iterations, while the within-family cell
exponents are small because cells barely vary inside a family. **The term that
overruns is the term nobody was writing down.**

Three consequences, all checkable before compute is spent:

1. **A rung estimate names its assumed iteration count and where the number
   comes from**: the settling curve of the rung below, the solver's own
   `residualControl` history, or the configured cap, and which of the three.
2. **A ladder that stores no iterations per rung says so in its cost basis.**
   The docket drafter for a refinement rung writes that sentence itself, because
   a stored study records cells per rung and no iterations at all, so the
   drafter can price the grid and nothing else. An omission stated is a question
   somebody can answer before the rung is queued.
3. **`scripts/self_audit.py` counts the gap weekly**
   (`check_rung_estimates_state_their_iterations`). At this clause's writing,
   **32 of 37 rung-shaped compute proposals on the docket name no iteration
   count and 26 of those are still unstarted**, the largest at 400
   core-minutes.

**Session budgets are stated as three numbers, not one.** Core-minutes, cores,
and memory. The real form, from the record: a 40 core-minute budget at 3 cores
and 4 GB. Container-enforced where the work runs in one, with explicit `--cpus`
and `--memory` caps and a serial rank count, so the cap is a property of the
run rather than of the agent's intentions.

**The machine.** 16 vCPU and 32 GiB, which is 2 GB per core. Memory is the
binding constraint more often than cores, and L-15 is the reason that sentence
is here rather than the opposite one: an adjoint that works at 63,920 cells and
breaks at 79,560 with over 4 GB of headroom unused is bound by convergence, not
by RAM, and a hardware recommendation was once made in the wrong direction on
exactly that confusion.

**Capacity is audited before launch, not after.** `compute_audit` reserves 2
cores and budgets memory per worker, and returns FITS or CONSTRAINED. A
proposal the owner approves when the machine has no room becomes
`approved-queued` rather than launching or being dropped, and the docket says
so in plain words. A refusal here is not a failure. It routes the mission to a
subset run at full fidelity with the rest covered by a reduced-order ensemble.

**A budget overrun stops the run. It does not get a new budget.** If the work
genuinely needs more, that is a new proposal with a corrected `cost_basis`, and
the correction is the point: the ranking in charter 1 is a ratio, and a
denominator nobody grades is a denominator that drifts.

## 4. The auto-stop contract

This section is written from the installed script, not from intent.

**What is installed.** `/usr/local/bin/auto-stop.sh`, run by root cron every
five minutes. It reads the mtime of `/tmp/last_job_activity`. If the box has
been idle for 30 minutes or more it logs "auto-stop: idle Nmin, shutting down"
and powers the instance off.

**How it decides the lab is busy.** One test, a single `pgrep -f` over solver
and mesher names plus the literal string `Certonomous/sdk`:

    simpleFoam|pimpleFoam|rhoSimpleFoam|rhoCentralFoam|interFoam|
    potentialFoam|blockMesh|snappyHexMesh|vspaero|mega_batch|
    mega_batch_keeper|dafoam|Certonomous/sdk

If any match, it touches the marker and exits. Nothing else counts.

**The contract, stated plainly.**

1. **It is deliberate and it stays.** The owner installed it for cost control.
   It is not disabled, not weakened, and not worked around. A charter that
   treats the cost control as an obstacle has the relationship backwards.
2. **The control room does not count as activity.** Verified. The two demo
   servers run as `python3 -u -m chief_engineer.server` and
   `python3 -u -m http.server 8080 --directory demo-output/website`, and
   neither matches any pattern above. The acts are in-process replays, so they
   spawn no matching process either.
3. **Therefore filming looks exactly like an idle box.** Someone typing
   prompts, running acts and talking to camera refreshes nothing. It powered
   off at 10:40 UTC on 2026-07-30 this way. A 172 second live run can also be
   cut off mid-run if the countdown is already near 30.
4. **The sanctioned hold is `scripts/filming_keepalive.sh`, and it is
   bounded.** It needs no root and works against the script that is really
   running, by holding open one process whose command line contains
   `Certonomous/sdk`, which the live `pgrep` already counts. It burns no CPU.
   It sleeps in one-minute steps and exits by itself.
5. **The hold ALWAYS expires.** Default 6 hours, maximum 24, minimum 1,
   validated as a whole number and refused otherwise. The script's own comment
   states the reasoning and it is the reasoning this charter adopts: an
   unbounded keep-alive is how a forgotten box quietly runs for a month, so the
   cost of forgetting to switch it off is bounded to the hours you asked for.
6. **`status` reports the whole truth, not its own half.** It prints whether
   the hold is on and how long is left, and separately whether the idle timer
   currently sees the lab as BUSY or IDLE, and when activity was last recorded.
   A hold script that only reported its own state would be L-2's failure: a
   verifier's self-assessment presented as evidence.

**NEVER.**

- Disable, uninstall or lengthen the 30 minute idle timer.
- Start an unbounded hold by any means, including a bare `sleep infinity` with
  a matching command line, which would work and is exactly the thing the
  expiry exists to prevent.
- Leave a hold running after the work that needed it finished. Run `off`.
- Report a hold as active without confirming the holder process is alive. The
  script re-derives its PID from the command line rather than trusting `$!`,
  because `setsid` only execs without forking when the caller is not already a
  process-group leader, and under job control `$!` would capture a short-lived
  parent so `off` would report success while the real holder survived. That is
  L-6 in the keep-alive, and it is already handled.

**Staged and not installed.** `scripts/filming_mode.sh` writes a hold file that
only the proposed auto-stop reads, and `scripts/auto-stop.sh.proposed` adds a
hold check plus mission-state mtime as an activity signal. Both need root.
Until they are installed they have no effect, and saying that clearly is the
difference between a mitigation and a comforting file.

**A long solve is safe by construction.** Any real solver, mesher or SDK python
process matches the pattern, so the timer cannot power off a running job. The
gap is entirely between jobs, which is where filming and thinking happen.

## 5. Spot versus on-demand

> **PROPOSAL, and currently blocked.** There is no spot policy, no on-demand
> policy, no dollar figure and no cost-per-hour convention anywhere in the
> repository. Writing one here would be inventing policy.

**Why it is blocked, and this is recorded rather than guessed.** The instance
cannot read its own billing. With no credentials and no instance role it cannot
call CloudWatch or Billing, so the configured alarm threshold and spend cap
cannot be reported from here. The blocker entry says so and then says the
important part: it explicitly does not report a number, because stating an
unverified spend cap would be exactly the kind of fabricated measurement the
house rules forbid. A campaign record repeats the same discipline, stating
actual core-minutes precisely and explicitly not claiming the spend was checked
against a limit.

**The unblock is named and small.** Attach an instance role with read-only
`cloudwatch:DescribeAlarms` and `ce:GetCostAndUsage`, or paste the configured
numbers directly, in which case they are recorded as reported-by-owner rather
than measured.

**The proposed policy, for when it unblocks.** Written now so the decision is
one word rather than a design exercise.

- Interruptible work runs on spot: mega-batch sampling, parameter sweeps,
  ensemble members, anything whose loss costs only its own core-minutes.
- Work that cannot be resumed from an artifact runs on demand: a gate-deciding
  solve, a long adjoint, anything whose interruption would produce a truncated
  log indistinguishable from a divergence. L-19 is the reason. Interrupted and
  diverged look identical from outside, and paying spot prices to create that
  ambiguity is a false economy.
- A filmed session runs on demand, always.

None of this is in force. It is a draft awaiting the unblock and her call.

## 6. Spend reporting format

**The lab's convention today is a footer.** Real examples, unaltered:

> Total compute: 38.45 core-minutes across 17 CFD runs (7 wedge, 4 cone, 6
> diamond), all foreground, single-core, nothing left running.

> Total compute: 14.66 core-minutes across all 9 CFD runs (3 Mach numbers by 3
> resolutions), all foreground, single-core, nothing left running, verified
> after every stage.

> Total new compute this session: about 5.25 core-minutes, all in F6a; F6c was
> free re-analysis of already-converged fields.

Three properties worth keeping: the count of runs, the statement that nothing
was left running with how that was checked, and the explicit note when
something cost nothing because it reused existing fields.

**Waste is reported, not absorbed.** A ladder rung on the record reads 692.5
core-minutes total, 485.3 useful and 207.1 wasted on a failed attempt. That
split is the honest form and it is required. A total that silently includes a
failed attempt understates the lab's cost per result and overstates its
efficiency.

**Per-stage tables where a run has stages**, with measured times and their
timestamps, headed as measured and not estimated:

    | stage | ranks | wall time | core-minutes | result |

including the failed stages as their own rows. One real table carries a
`check_totals` run that FAILED at 0.33 core-minutes and its retry at 1.80, and
that is what makes the 3.51 total meaningful.

**The morning report moves it to the head.** Charter 8 puts spend in the
header rather than the footer, on the owner's list. The content is the same and
the position changes.

**The compute ledger records avoided spend, and only when measured.** Its own
docstring is the rule: savings are only ever recorded against a measured
alternative, the cost of the designs a surrogate covered or of the fine mesh a
validated closure stood in for. **An unmeasured saving is not recorded.**

## 7. Enforcement

- `agenda.proposal_violations` refuses a proposal with no cost, and the
  drafting scripts refuse to write a batch containing one.
- `compute_audit` gates launch on measured free cores and memory.
- `scripts/launch_solve.sh` is the only sanctioned launcher and registers the
  job so `--check` can test an agent's claim that it finished.
- `scripts/filming_keepalive.sh status` reports the idle timer's own view
  alongside its own.
- The auto-stop script itself is the backstop, and it is the one piece of this
  charter that enforces itself without anybody remembering to run it.

Not enforced mechanically: the measured-versus-estimated discipline in
`cost_basis`, the waste split, and the estimate-versus-actual grading. All
three are review disciplines.

## Related

- `docs/charters/GOALS_AND_PROPOSALS_CHARTER.md`. Where `est_core_min` enters
  the ranking.
- `docs/charters/ESCALATION_CHARTER.md`. How much may be spent without asking.
- `docs/charters/REPORTING_CHARTER.md`. The spend header.
- `LESSONS.md` L-2, L-6, L-15, L-19, D12.

## A per-cell rate borrowed across solver families is a factor wearing a basis's clothes

**Added 2026-08-11 (D5), from a repricing caught before it was quoted.** The
standing finding of this lab's calibration work is that *the predictor is the
basis, not a factor*: estimates priced from a prior measurement of the same
body have never over-run by more than 1.84x, while forecast-based estimates
have reached 13.55x. This clause closes the loophole in that rule.

A measured basis is only a basis **within its own solver family and regime**.
Two ladders were priced from the nearest measured bases available — both
steady, incompressible `simpleFoam` on snappyHexMesh bodies — and applied to a
case running **transient, explicit `rhoCentralFoam` to a fixed end time**. The
per-cell rate does not cross that gap: the honest price, read from that case's
own record, was **8.9x** the borrowed one.

The rule: **a repricing crosses solver families only from that case's own
record.** Where no such record exists, the item is reported UNPRICED rather
than given a number — an unpriced item invites the measurement that would price
it, and a wrong price is spent before anyone checks it. Naming several
candidates unpriced, rather than extending one rate across all of them, is the
correct and expected outcome.
