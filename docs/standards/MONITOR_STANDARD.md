# Certonomous Monitor Standard

Version 1.12, dated 2026-08-18. **Adds no new rule. It changes what S13's
percentage is a percentage OF, and corrects a false positive v1.11 introduced
hours earlier.** S13 normalised the peak-to-peak spread by the quantity's
ABSOLUTE MEAN, so on a quantity carrying a large offset it measured the offset:
K2b's rack-inlet temperature has a mean of 289 K and a range of 0.086 K, a
factor of 3,343. The spread is now referred to **the range the quantity spanned
over the run** (D389). The same change repairs v1.11, whose null-variation
clause tested the WINDOW SPREAD against the print resolution and so could not
tell "never moved" from "converged to the last bit" — it refused four committed
K2e cases that print sixteen significant figures bit-identically after
travelling 0.53. Re-graded over **all 49** committed cases, **two verdicts
change against the original criterion**, both K2b's, and K0c's eleven and K2e's
thirty are all unchanged. The 1.11 note follows.

Version 1.11, dated 2026-08-18. **Adds no new rule. It repairs S13, which until
now returned its BEST POSSIBLE SCORE on a quantity that had never moved** — the
identity defect this standard already documents for the sealed-case heat balance
(S14), arriving in the convergence criterion. Measured at rung K2b: a graded
rack-inlet temperature pinned at the supply temperature scored **0.00000 %**
against a 0.02 % band while the same case's heat balance was 2.6632 % out. S13
now REFUSES an unresolved spread instead of passing it. Re-graded over all
fourteen cases graded under the old reading, **exactly one verdict changes**.
The 1.10 note follows.

Version 1.10, dated 2026-08-17. **Adds exactly one rule, S16, and gives S14 the
branch its own detection clause had always implied and never answered.** S14
detects on a conjunction — no non-wall patch **and** no constructed source — and
until now the negation of that conjunction was simply silent. It was worse than
silent in the instrument: `scripts/heat_balance.py` printed "NOT of the identity
class, so the balance is a genuine constraint here" on open cases while never
computing the advective enthalpy flux that claim rested on. Rung KV1 implemented
and validated that term, so the open case now has an answer of its own, and it
is not S14's: measured on one heated duct at eleven iteration counts, the
open-case closure reads **20.881% at iteration 20 and 0.000000% at 201**,
tracking the T residual across nine decades and crossing the governed 0.5% band
between iteration 80 and 100. It is a measurement. **S16 is the rule that stops
that measurement from being read as more than it is:** an open-case closure
establishes nothing about circulation, a solve with the flow structure entirely
wrong closes perfectly once converged, and S16 is adopted with a corpus of
**zero cases** — before K2b produces the population it governs — because a rule
written after the first closure figure is quoted arrives too late.

Version 1.9, dated 2026-08-17. **Three thermal signatures adopted at rung K1a
of F14, and the first of them is the one that would have changed a published
result.** S13 fires when a steady buoyant run meets its own `residualControl`
while the quantity the rung is graded on is still moving: measured at K0c on
four mesh pairs, where every fine mesh met its residual target and missed the
graded criterion by two to three orders of magnitude, and where grading on
residuals would have reported a FINE mesh further from the benchmark than its
own COARSE mesh. S14 fires on the opposite error — a heat-balance closure
number quoted as evidence on a sealed impermeable case, where it is very nearly
an identity and K0b measured 0.013% against its own prediction of over 20%.
S15 fires when a planted source is witnessed in a dictionary and not in the
solver's log, or when a case's logs disagree about it; **it caught this rung's
own no-source control**, which had inherited two foreign stage logs from the
case it was copied from and would otherwise have read as planted. All three are
WIRED, in `scripts/check_convergence.py` and `scripts/heat_balance.py`, and
their thresholds are governed from `docs/physics_rules.yaml` block `thermal`
rather than held in the checkers. Replay lines and corpus reach are stated with
each; the corpus is small and the rules say so.

Version 1.8, dated 2026-08-11. **S6's arming parser could not read OpenFOAM
regex-group field keys, and the six "tolerance unreadable" cases were that
parser, not those cases.** A `residualControl` target and its field's
linear-solver `tolerance` may each be declared under a quoted regex key
covering several fields; the helper compared the declared KEYS to each other
by string equality, so the pair never met and the gate fell through to
fail-open on cases that state both numbers plainly. Repaired to resolve both
**per field** using OpenFOAM's own lookup order (literal keys before pattern
keys; among patterns the last-declared match wins). Re-scored on the same 222
gated logs: **135 excluded (unchanged, still 135 of 135 sentinels and nothing
else), 87 gated at 47%, 0 fail-open**, family spread **94 / 51 / 20**. No case
moves between sentinel and non-sentinel and no refutation condition fires. The
relation now reproduces the bare-`1e-15` partition of v1.6 exactly. **And v1.7
above overstates its own verification**: three of its eight "met" rows are
measurements restated from the pre-registration's own validation table rather
than predictions, and its primary prediction -- the post-wiring fire rate on
`HeadEngineer` runs -- was never scored, because that run cost zero
core-minutes. Both are labelled in place in
`campaign/S6_WIRING_PREREGISTRATION.md`, which is otherwise unaltered.

Version 1.7, dated 2026-08-10. **S6 is wired and now fires on production
runs**, armed at staging from the case's own `residualControl`, with the
sentinel class excluded by construction (a target at or below its field's own
linear-solver tolerance is unreachable in principle). Pre-registered before
the code existed and every prediction met, including the family spread
(92/48/20). S8 stays unwired. Section 3.1 gains the reach requirement a
corpus owes.

Version 1.6, dated 2026-08-10. **Corrects a warrant, a corpus, and a claim --
no rule changes.** S1's warrant ("every OpenFOAM log prints a trapping
banner") is false: 39 of 149 registry logs carry none, across eight family
prefixes. **And the corpus behind six adopted rules was selected by a filename
accident** -- the replay globbed `*.log` while OpenFOAM writes `log.<app>`, so
section 3.1's adoption gate was discharged over 449 files against 1,375 real
run logs. Re-run on a content-derived corpus, S6's fire rate on REAL targets
is 47%, and a published line about declared targets is refuted by 70 logs the
glob could not see.

Version 1.5, dated 2026-08-10. **Withdraws a claim rather than a rule.** The
2026-07-30 adoption note said "the whole of both approved monitor proposals is
in force"; it was false the day it was written. **S6 and S8 cannot fire on any
production run** -- `HeadEngineer` has no parameter by which their gates could
be supplied -- and S9's `check_wall_time` entry point has no caller outside
the tests. The false sentence is retained with its correction beside it, the
five-day-threshold defect's blast radius is corrected ("every caller" was the
test suite), and the honest coverage table plus the wiring decision are at the
end of this document. Nothing about any rule's correctness changes.

Version 1.4, dated 2026-08-08. **Adds exactly one rule, S10d magnitude
explosion, as a fourth branch of S10, and widens the archive-replay rail's
corpus to forces-object histories. Withdraws nothing.** The amendment exists
because the archive-replay discipline did its job on the standard itself: the
F8 divergence specimen — a blade moment at −2.5e99 N·m behind a 1.4e-8
momentum residual, the second real member of S10's own class — was replayed
through every clause on 2026-08-08 and caught by none, for measured,
structural reasons recorded in the S10d entry. The rule was adopted through
the innovation path with its replay line attached (974 histories, 5 fires,
all on runs the record already names diverged, zero completed-run false
positives), chief-endorsed in the negative-verdict review of 2026-08-07 entry
3, and the replay was rerun by the adopting family supervisor's own hands
before this version was written. Nothing else in 1.3 is changed.

Version 1.3, dated 2026-08-02. **Adds exactly one rule, S12 unsettled stop, and
withdraws nothing.** S12 closes both of the failure modes section 3.4 recorded
as having no rule at all — item 2, a rung stopped and recorded as settled, and
item 3, a monitored quantity that is not a residual — and it is the first rule
in this standard that reads a coefficient history instead of the residual block.
Its thresholds are bracketed by one archived case against itself rather than
chosen off a distribution, which is the shape section 3.3 asks for. Nothing else
in 1.2 is changed.

Version 1.2, dated 2026-08-01. **Version 1.2 withdraws exactly one rule, S7
oscillatory divergence, and adds nothing.** It is the first version of this
standard to remove a rule rather than add one. The entry stays in place, marked
withdrawn, with the five measurements that justify removing it kept beside it,
because the reason a rule failed is what a replacement needs. S10 stands. The
rest of 1.1 is unchanged and is described below as it was written.

Version 1.1, dated 2026-07-31. Produced by the overnight reading program (R1).
Names every solver-log signature the lab's monitor recognizes or should
recognize, with a detection rule, a severity, and a prescribed action. Derived
from the lab's own logs: the mega-batch ledger
(`demo-output/website/mega-batch/ledger.jsonl`, 39442 rows examined), the
mission logs and learned lessons under
`sdk/chief-engineer-runs/mission-state/`, the TMR and motorcycle run logs, and
the monitor implementation in `sdk/chief_engineer/head_engineer.py`
(`LogMonitor`).

Version 1.1 adds section 3, the set reviewed as a set: which rules have been
replayed against the archive and which are still hypotheses, which one fires
too often to be useful, why a rule that fires on every run is sometimes right,
and the four failure modes seen this week that no rule covers. Standing rules 6
and 7 follow from it. No rule's detection, severity or action was changed.

Severities: FATAL (stop and investigate, the run is not evidence), FLAG
(continue, mark the record, cap trust until resolved), WATCH (continue,
count, report in the debrief).

One severity sits outside that ladder: CONFIGURATION RISK (the numbers are
untouched and stand; the machine they were computed on is the finding). It is
never FATAL, because calling a sound solve unsound would be false, and it is
never folded into "nothing fatal", because "nothing fatal" is a verdict on the
arithmetic and this is a statement about the host. A run can be numerically
spotless and carry one, and both facts are reported.

## 1. Signatures the monitor already catches

### S1. Floating point exception

- Detection: `Foam::sigFpe::sigHandler` or a line starting `Floating point
  exception`. Never the log banner: every OpenFOAM log prints a trapping
  banner (`trapFpe: Floating point exception trapping enabled`), and matching
  it reads every healthy run as fatal. The monitor matches the handler, not
  the banner. Evidence: motorcycle benchmark logs, knowledge base fact 7.

  > **WARRANT CORRECTED, 2026-08-10 — THE RULE IS UNCHANGED AND STILL RIGHT.**
  > Only the sentence justifying it moved; S1's detection is untouched, and
  > nothing about what it matches or when it fires is affected.
  >
  > *"Every OpenFOAM log prints a trapping banner"* is **false**. Measured
  > over the solve registry: **39 of 149 logs carry no `trapFpe` line**, and
  > they are not one family — the prefixes span `d*`, `f*`, `b*`, `r*`, `a*`,
  > `w*`, `dpw*` and `adjwall*`. The banner appears only when `FOAM_SIGFPE` is
  > set in the environment, so it is a fact about how a run was launched, not
  > a property of OpenFOAM. The second half of the citation is stale at its
  > own end: `knowledge base fact 7` describes a mesh **this lab's own
  > skewness gate now rejects** (reported by the 2026-08-10 audit; the
  > registry measurement above is this family's own).
  >
  > **Why the rule survives its warrant, and this is the point.** S1 keys on
  > the SIGNAL — the handler line — not on the banner. That is strictly safer
  > **whether or not the banner is universal**, and the measurement makes the
  > design look better rather than worse: a banner-keyed detector would have
  > been blind on those 39 logs *and* would have read the other 110 healthy
  > runs as fatal. The original reasoning reached the right rule through a
  > claim that was not true.
  >
  > A correction that blurred these two would spend credibility for nothing.
  > **The warrant moved. The rule did not.**
- Severity: FATAL. Action: stop and investigate; nothing downstream of an FPE
  is evidence.

### S2. NaN in solver output

- Detection: `nan` in a solving or field line. Severity: FATAL. Action: stop
  and investigate; check boundary conditions and time step before rerunning.

### S3. Residual spike

- Detection: initial residual above 25 times the rolling median of the last
  25 iterations, and rising over the last three. The comparison is against a
  rolling median, never the all-time minimum: the deeper a run converges, the
  larger every ordinary wobble looks as a multiple of the minimum, and a
  healthy run would drown the log in alerts.
- Severity: FLAG. Action: continue, mark the record; repeated spikes in one
  step escalate to stop when paired with S5 oscillation.

### S4. Bounding warnings

- Detection: lines starting `bounding <field>,`. A clipped variable was held
  physical by force.
- Severity: WATCH during the first ten percent of iterations (startup
  transients bound routinely), FLAG when persistent past startup: sustained
  bounding means the discretization or the turbulence initialization is
  fighting the physics.

### S5. First-seen warning on an unfamiliar case

- Detection: any `FOAM Warning` pattern not seen before on a body the lab has
  not solved before (novel mode). Severity: WATCH. Action: capture as
  candidate knowledge for the debrief.

### S11. System operations allowed (configuration risk)

- Detection: `allowSystemOperations\s*:\s*Allowing`, on every run, in every
  mode. `detect_system_operations` in `sdk/chief_engineer/log_signatures.py`.
- Severity: **CONFIGURATION RISK**. Not FLAG, not FATAL, and specifically not
  "nothing fatal".
- Action: no number is in doubt; the host is. The run just executed with
  `#codeStream`, `#calc`, `coded*` boundary conditions and the `systemCall`
  function object enabled, which means a case file can compile and run
  arbitrary code on the machine. Required for a named, vetted case; never for
  one that arrived from outside. The standing rule is Verification Charter
  section 13, enforced at staging.

Three things about this rule are deliberate and are the reason it is not a
special case of S5.

1. **It is not banner text, so rule 3 below permits it.** `argList` prints the
   line only inside `if (dynamicCode::allowSystemOperations)`
   (`argList.C:2241`). The line exists because the switch is on. With the
   switch off the same code prints `Disallowing` and the detector returns
   nothing, the same distinction that separates the FPE *handler* from the
   FPE *trapping banner* in S1.
2. **It cannot ride on S5, because in the container it is not a warning.**
   OpenFOAM v2606 on the host prints `--> FOAM Warning : allowSystemOperations
   : Allowing user-supplied system call operations.`; the older build inside
   the DAFoam container prints `allowSystemOperations : Allowing user-supplied
   system call operations` bare, with no warning prefix
   (`demo-output/website/dafoam/probe_baseline_run1.log` line 33). S5 matches
   on `FOAM Warning` and would miss every containerized run, which is exactly
   the run that executes as root on a bind mount.
3. **It is recorded on every run, not only in novel mode.** A machine that
   executes case-supplied code does so whether or not the body is new to the
   lab. S5's novel-mode gate is about knowledge capture; this is about the
   host, so it is unconditional. It is reported under its own
   `configuration_risk` key next to `fatal`, and it never moves the anomaly
   count, the by-kind table, or the fatal verdict.

## 2. Signatures the logs show the monitor misses

Each of these is filed as a proposal in the agenda inbox; the monitor code is
owned elsewhere and is not edited by this program.

Adoption note, 2026-07-25: the owner approved the agenda proposals, and S6,
S7, and S9 are implemented as pure detection functions in
`sdk/chief_engineer/log_signatures.py`, wired into `LogMonitor` in
`sdk/chief_engineer/head_engineer.py` (series hooks for S6/S7, a
`check_wall_time` hook for S9). Each signature below carries a Status line.

Withdrawal note, 2026-08-01: **S7 is withdrawn** and is no longer implemented.
Its entry below is kept, marked, and carries the measurements that justify
removing it. Every adoption note above it that mentions S7 is left as written,
because an adoption note is a record of what was decided on a date and editing
it would erase the fact that the rule was once in force.

Adoption note, 2026-07-30: S8 is now implemented too, so the whole of both
approved monitor proposals is in force.

> **CORRECTION, 2026-08-10 -- THE SENTENCE ABOVE IS FALSE, and it is retained
> so the correction has something to point at.** "In force" was read off the
> implementations. **S6 (residual stall) and S8 (Courant excursion) cannot
> fire on any production run**, and could not on the day it was written. Both
> return early unless `LogMonitor` was constructed with `residual_target` /
> `courant_limit` respectively -- and `HeadEngineer.__init__` takes
> `case_name, out_root, *, novel, on_event`, so **no parameter exists by which
> either gate could be supplied.** It builds
> `LogMonitor(novel=novel, on_anomaly=...)` at `head_engineer.py:830`. Three
> construction sites exist repo-wide: that one, the offline replay at
> `sdk/scripts/replay_monitor_rules.py:134` (which does pass
> `residual_target`), and the test suite.
>
> **Unreachable on: every HeadEngineer path** -- the geometry studies, the
> Ahmed act, the NASA hump act, the UQ studies. **Reachable on: offline replay
> and the tests, only.**
>
> **S9 (wall-time excursion) is live, but through a different door.** Its rule
> runs on the mega-batch ledger via `wall_time_record_field`
> (`mega_batch.py:810`) and is correct there. The `LogMonitor.check_wall_time`
> entry point is called by nothing but tests, so S9 too covers no HeadEngineer
> run.
>
> **Where this hid, and it is the transferable part.** Every per-rule Status
> line in this document is scrupulously honest -- they say a rule fires *"when
> constructed with residual_target"*, and each is true. The summary sentence
> is false and is built from nothing but true ones: a summary drops the
> conditionals, because that is what summaries do, and the honest clause
> upstream makes the summary feel audited. **When a capability is claimed IN
> FORCE, find its production CALL SITE** -- not its definition, not its test,
> not the conditional prose that is true about the definition. Three things changed with it, each on
measured evidence and each recorded in the relevant section below: S8 carries a
tolerance because a strict comparison would have called every healthy transient
run in the lab an excursion; S6 and S7 are scoped to steady solves because they
fired on every healthy transient run; and the S9 flag threshold was corrected
from 20x back to the 10x the owner actually approved.

Adoption note, 2026-07-31: closing out both monitor proposals against a real
failure rather than against the archive alone. S10 is added, designed on the
Ahmed body primal whose drag was published and withdrawn this week, and it is
the branch that catches a run whose field diverged while its residual read as
converged. Two older things were corrected on the way: the S9 flag threshold
correction had landed on the shared constant but not on the monitor entry
point, which kept its own literal 20x, and S7 turns out to fire on two thirds
of the lab's archived steady runs and now carries a gate and a recorded
weakness. Both are written up in their own sections.

### S6. Residual stall (proposal r1-monitor-stall-rule)

- Evidence: the Re 200 cylinder case stalls at residual near 1e-3 with Cd
  oscillation near 1e-2 at the iteration cap (knowledge base fact 4). A
  steady solver applied past its regime degrades measurably but never spikes,
  so the spike rule stays silent and the run exits on the cap looking calm.
- Detection rule: residual plateau, rolling median improving by less than a
  factor of 2 over the last 200 iterations while still above the
  residualControl target, with the iteration cap approaching.
- Severity: FLAG. Action: the result is UNCONVERGED regardless of how smooth
  the tail looks; prescribe the regime check (steady versus unsteady) before
  any rerun buys more iterations.
- Scope: steady solves only. The scoping note is kept under the withdrawn S7
  entry, where it was written; it now binds S6 alone.
- Status: implemented (`detect_residual_stall` in
  `sdk/chief_engineer/log_signatures.py`; raised once per field per episode
  by `LogMonitor` when constructed with `residual_target`, and gated on the
  iteration cap approaching when `iteration_cap` is given).

### S7. Oscillatory divergence — **WITHDRAWN 2026-08-01**

**Withdrawn by supervisor ruling R1** (`docs/charters/SUPERVISOR_RULINGS.md`),
answering conflict C-2 in `docs/charters/PROPOSALS_OPEN.md` with option B. The
rule is gone from the standard and gone from the monitor: there is no
`oscillatory-divergence` detector and no `oscillatory-divergence` anomaly kind.
Nothing replaces it, and the failure family it aimed at is left uncovered and
named as uncovered in 3.2.

**The measurements that justify the withdrawal are kept below rather than
deleted with the rule**, because the reason a rule was withdrawn is the part a
future proposal needs, and a rule that leaves no trace gets reinvented.

**Why, in one line: it fires on two thirds of the lab's completed steady work,
and it cannot separate the two logs of the case it was written for.** The
second fact is the decisive one. A detector that cannot tell the sick run from
the healthy run in the one case it was designed around has not been shown to
detect anything, and everything else is a question of where to put a threshold.

The rule as it stood when it was withdrawn, recorded so the measurements below
have something to attach to:

- Evidence it was written from: the same past-regime family as S6, oscillation
  amplitude growing rather than decaying around a stalled residual. A knowledge
  base fact, not a run.
- Detection rule: alternating-sign residual changes with growing envelope
  over the last 50 iterations.
- Severity: FLAG, escalating to FATAL when the envelope doubles. Action: stop
  the steady solve; the prescribed fix is the unsteady track, not more
  iterations.

**Measurement 1, the fire rate. Over every steady solver log the lab has
archived, 106 of them: ungated, S7 fires on 68 and reaches FATAL on 65.** Every
one of those runs completed and its results are on the record, so on this
corpus the rule was calling roughly two thirds of the lab's healthy work
divergent.

**Measurement 2, four tightenings, none of which rescued it.** Requiring the
residual level to stop improving: still 68 logs. Requiring the finding to
persist a full window: 40. Measuring growth against a 200 iteration baseline:
59. Raising the growth factor to four times: 23.

**Measurement 3, and the one that decided it: it cannot discriminate its own
motivating case.** 22 firings on the sick log, 20 on the healthy one. The two
counts are the same number to within the noise of the rule.

**Measurement 4, why no threshold saves it.** A converged field sits flat with
small noise, and the ratio of one noise envelope to the next is close to a coin
toss. A run of thousands of iterations wins that toss somewhere, so the fire
rate is a function of run length rather than of run health.

**Measurement 5, transient runs, taken 2026-07-30.** On the lab's four archived
transient runs S7 fired 5, 5, 6 and 9 times on runs that all completed
healthily, every one a false positive. This was the reason for the steady-solve
scoping described below; it is now the reason for nothing, and is kept because
it is a measurement.

**What the withdrawn gate was, and why it was not enough.** The shipped rule
required a `residual_target` and stayed silent on any field that had already
reached it, reasoning from the proposal's own words that the rule is about
oscillation "around a stalled residual". That gate was never a measurement: the
archived logs do not record the residual target each run was aiming for, so the
corpus could not be replayed with the gate in place, and its false-positive
rate was unmeasured and unmeasurable with the data the lab holds. **A detection
rule nobody can validate is worse than no rule, because it is trusted.**

S10, which names exactly one log out of 383, stands, and is the shape a
detection rule in this standard is expected to have.

The scoping note the withdrawn rule carried, kept because S6 still depends on
it and refers to it:

  rule and is switched off for the rest of a run as soon as the monitor sees a
  `Courant Number` line, which is a transient solver's signature. In a
  transient run the residual series restarts at every time step and the outer
  correctors drive it high and low in turn, so alternation with a moving
  envelope is the time stepping itself, not divergence. The transient
  equivalent is S8, and it now exists. This scoping was written for S6 and S7
  together; with S7 withdrawn it binds S6 alone, and S6's own evidence for it
  is under S6.
- Status: **withdrawn, and absent from the code.**
  `detect_oscillatory_divergence` is removed from
  `sdk/chief_engineer/log_signatures.py`, its wiring and its
  `residual_target` gate are removed from `LogMonitor` in
  `sdk/chief_engineer/head_engineer.py`, and `oscillatory-divergence` is no
  longer a value the `Anomaly.kind` field can take. A test asserts the monitor
  raises no anomaly of that kind on a series that used to trigger it, so the
  withdrawal cannot be undone by accident.
- **What is now uncovered.** Graceful degradation of a steady solve applied
  past its regime loses its dedicated detector. S6, residual stall, still
  covers the stalled-residual half of that family, and S6 is gated the same way
  S7 was but does not false-positive. The growing-oscillation half has no rule.
  A replacement is welcome and starts from the standing rules in section 4:
  replay it against the archive first, publish the fire count and the fatal
  count, and show it separating the two logs of the case it is written for.
  Measurement 3 above is the bar.

### S8. Courant excursion (same proposal)

- Evidence: when the rule was first written no transient run existed in the
  ledger and it was drafted forward-looking. The unsteady track has since
  landed, so the rule was measured before adoption against real data: 417
  unsteady cylinder rows in the ledger and four archived `pimpleFoam` logs
  holding 13308 time steps at a requested maximum Courant number of 1.5.
- Detection rule: `Courant Number max` exceeding the case limit by more than
  the tolerance an adaptive time step explains, or growing monotonically
  across 20 consecutive time steps while the time step is held fixed.
- **Why the rule carries a tolerance, measured rather than assumed.** An
  adaptive stepper sets the next step from the *previous* step's Courant
  number, so the reported maximum sits a little above the requested limit by
  construction. In those four healthy archived runs, between 27 and 43 percent
  of all time steps are strictly above the limit, and the rule as first drafted
  (a strict comparison) would therefore have called every healthy transient run
  in the lab an excursion. The largest overshoot anywhere in the archive is
  0.403 percent. The adopted tolerance is 2 percent, five times that, so
  ordinary adaptive stepping never trips it while a real excursion still does.
- **Why the monotone branch requires a fixed time step.** An adaptive stepper
  raising the Courant number back toward its own target is the stepper working.
  The longest monotone rising run in the healthy archive is 17 consecutive
  steps, below the window of 20, and none of those runs held its step fixed.
- Severity: FLAG at the limit, FATAL on monotonic growth with the time step
  fixed. Action: reduce the time step or enable adaptive stepping; a transient
  result computed above its Courant limit is not evidence.
- Status: implemented (`detect_courant_excursion` in
  `sdk/chief_engineer/log_signatures.py`, wired into `LogMonitor` when
  constructed with `courant_limit`; raised once per episode and again only on
  escalation to FATAL). Tests assert that no healthy archived run is called an
  excursion, that a strict comparison would have flagged every one of them, and
  that an injected over-limit step is still caught.

### S9. Wall-time excursion (proposal r1-monitor-walltime-rule)

- Evidence, mined from the mega-batch ledger: solver wall times are tightly
  banded (cylinder median 3.7 s, 99th percentile 19.7 s; wing median 5.8 s,
  99th percentile 8.6 s), yet three runs per solver recorded wall times near
  16300 s, over 800 times the 99th percentile, and every one was recorded
  ok with no flag anywhere. A hung or starved run that eventually returns a
  plausible number is invisible to every current check.
- Detection rule: wall time above 10 times the running 99th percentile for
  that solver and case class is FLAG; above 100 times is stop-and-investigate
  with the host state captured.
- Severity: FLAG, then FATAL as above. Action: the record keeps the excursion
  as a named field so fleet learning can separate solver cost from
  infrastructure stalls.
- Status: implemented (`wall_time_percentiles` and `classify_wall_time` in
  `sdk/chief_engineer/log_signatures.py`, exposed as
  `LogMonitor.check_wall_time`, and stamped onto the record by
  `wall_time_record_field`). The envelope is learned lazily from the
  mega-batch ledger percentiles and memoized per file version.
- **Thresholds.** FLAG above 10 times the learned p99, FATAL above 100 times;
  both carry the stop-and-investigate action, and both are configurable.
  CORRECTION, 2026-07-30: this section previously recorded the flag threshold
  as 20 times and attributed that to the approved proposal. The proposal says
  10 times. The code has been brought back to what was approved, and the
  choice costs almost nothing in noise: measured over the full 208193-row
  ledger, 10x names 30 rows and 20x names 27, and the three extra are
  reduced-order rows of 0.05 to 0.43 s.
  SECOND CORRECTION, 2026-07-31: the correction above landed on the shared
  constant but not on `LogMonitor.check_wall_time`, which kept its own literal
  default of 20.0. For five days every caller that took the monitor default
  judged on a threshold nobody approved, and the gap between the two rows the
  ledger holds in that band was invisible to it.
  BLAST RADIUS CORRECTED, 2026-08-10: **"every caller" was the test
  suite.** `LogMonitor.check_wall_time` is called by nothing else --
  not by `HeadEngineer`, not by the ledger path, which reaches S9
  through `wall_time_record_field` and read the governed constant
  correctly throughout. No production run was ever judged on the
  unapproved 20x default. The defect in the code was real and the fix
  was right; the exposure stated above was not. A record that
  overstates its blast radius spends the same credibility as one that
  understates it. The entry point now takes its
  default from the constant, and a test pins the two together so they cannot
  drift apart again.
- **The named field.** `run_task` in `sdk/workflows/mega_batch.py` stamps
  `wall_time_excursion` onto a row as it is written, carrying the severity,
  the multiple, and the p99 and sample count it was judged against. An
  ordinary row carries no such field. This is what makes the rule's finding
  survive into fleet learning rather than living only in a log.
- **Envelope, measured 2026-07-30 over 208193 ledger rows:** openfoam-cylinder
  p50 2.396 s, p99 15.23 s (69288 runs); vspaero-wing p50 5.23 s, p99 7.365 s
  (69149 runs); reduced-order p50 0.000 s, p99 0.003 s (69007 runs);
  openfoam-cylinder-unsteady p50 395.5 s, p99 445.7 s (417 runs);
  rhosimplefoam-naca0012-transonic p50 29.63 s, p99 69.91 s (280 runs);
  simplefoam-ahmed-3d-viscous p50 34.57 s, p99 44.59 s (52 runs).
- **Retrospective assessment.** `sdk/scripts/assess_ledger_wall_times.py`
  applies the rule backwards over the ledger and writes
  `demo-output/website/mega-batch/wall_time_assessment.json`. It labels every
  entry an assessment and states that the monitor flagged nothing at the time,
  because it changes no record and must never be read as monitor history. It
  confirms the proposal's evidence: the six ~16300 s runs (three cylinder,
  three wing), every one recorded ok, land at 1070x and 2214x their p99 and
  are FATAL under the rule.
  The artifact was generated for the first time on 2026-07-31, over 208193
  ledger rows: 19 rows would have been FLAG and 11 FATAL, none of them flagged
  by anything at the time. Until then the script existed and its output did
  not, so the finding lived only in this paragraph.
- **Known weakness, recorded not hidden.** The rule is purely relative, so a
  solver whose p99 is 3 milliseconds gets a threshold of 30 milliseconds. Five
  reduced-order rows of 0.30 to 0.43 s are assessed FATAL on that basis. The
  detection is arguably right (those runs really were hundreds of times slower
  than their own baseline, which is what host contention looks like) but the
  severity is out of proportion to a third of a second. An absolute floor
  would fix it and is deliberately NOT added here, because no such floor was
  in the approved proposal and inventing a threshold is how a rule stops
  meaning what it says. Filed as an observation for the owner.

### S10. Divergence behind a converged residual (proposal r1-monitor-stall-rule)

- **The run this rule was designed against.** The Ahmed body primal on the
  45760-cell mesh (ladder rung A4) ran to its iteration cap, printed a drag
  coefficient, and that number was published and then withdrawn. Its
  turbulence field had diverged: omega was pegged against the top of its
  clipping range from iteration 100 onward, and its unnormalised residual norm
  finished at 1.13e+35 against 6.9e+03 for momentum. The number the log reports
  as the omega residual finished at 5.9e-31, which reads as converged to every
  rule S1 to S9. A normalised residual is a ratio, and when the field blows up
  the denominator blows up with it, so the ratio collapses toward zero exactly
  when the field is worst. Nothing else fired: no NaN, no exception, no spike,
  no stall (the residual is far below target, not above it), no Courant line,
  18 s of wall time.
- Detection rule, three independent branches, any one sufficient:
  - **S10a, ceiling clip.** The solver reports a field clipped at the TOP of
    its permitted range. Direction is the whole finding: a turbulence quantity
    held up off its floor is ordinary and stays the S4 watch, while an eddy
    frequency at 1e+16 has left the physical range. Severity FATAL.
  - **S10b, normalisation collapse.** A field's normalised residual has sat at
    or below 1e-20 for 100 consecutive iterations, having been above it earlier
    in the run, while another field in the same solve is still working. All
    three conditions carry weight: the floor sits twelve orders below the
    tightest target any of the lab's cases asks for, so nothing converges into
    it legitimately; "alive earlier" separates a diverged field from a
    conserved variable that reports exactly zero from first iteration to last,
    which is what five series in the archive do; a working peer is what makes
    the reading a contradiction rather than a finished solve. Severity FLAG,
    FATAL when the same field also hit its ceiling.
  - **S10c, residual norm contradiction.** Where a solver prints unnormalised
    residual norms at the end of a run, a field whose norm exceeds the momentum
    norm by more than ten orders of magnitude. That block is the honest one: it
    is not divided by anything that can blow up with the field. Severity FATAL.
- **Why ten orders and not a rounder number.** Measured over the 157 archived
  runs that print such a block: the largest healthy ratio anywhere is 3.6
  orders of magnitude, and it belongs to the healthy coarse solve of this very
  case. The withdrawn run sits at 31.2. The threshold is six orders above
  anything healthy and twenty one below the failure.
- Severity: FATAL on S10a and S10c, FLAG on S10b alone. Action: no quantity
  computed from that state is evidence, and any number already published from
  it is withdrawn. That is what happened to this one, three days late.
- **False positives, swept rather than sampled.** All three branches were run
  over every solver log the lab has archived, 383 of them, before adoption.
  Together they name exactly one: the withdrawn run. A test sweeps the whole
  archive on every run and fails if a second log is ever named.
- Status: implemented (`classify_bound_line`, `detect_ceiling_clip`,
  `detect_normalisation_collapse` and `detect_residual_norm_contradiction` in
  `sdk/chief_engineer/log_signatures.py`, wired into `LogMonitor`; each raised
  once per field per episode). Tests feed both A4 logs through the monitor line
  by line and assert that the withdrawn run is fatal on all three branches
  while the healthy coarse solve of the same case raises nothing at all.

**S10d, magnitude explosion in a monitored quantity** (added v1.4,
2026-08-08; proposal `s10d-monitored-quantity-magnitude-explosion`,
chief-endorsed in the negative-verdict review of 2026-08-07 entry 3).

- **The run this branch was designed against, and why a, b and c all miss
  it.** The F8 `phase6_mrf_pfinit` specimen: blade moment at −2.5e99 N·m
  behind a 1.4e-8 momentum residual, the class's second real member and the
  first the standard missed. The zero-compute replay of 2026-08-08 measured
  the silence clause by clause: S10a sees 692 bound lines and every one is a
  floor bound on nuTilda — wrong direction; S10b's smallest normalised
  residual is 1.86e-9, eleven orders above its 1e-20 floor; S10c's required
  unnormalised-norm block does not exist in a plain simpleFoam log; S12
  fails first on its 40-sample length floor and then, floor removed, on its
  monotone clause (0.79 against 0.90) because exponential divergence rides
  on an oscillation. The branch that was missing reads the quantity's
  magnitude, not its drift.
- **Detection.** Over the monitored-quantity history with the first tenth of
  samples excluded as startup, let m be the median magnitude of the first
  half of the remainder. Fires when the final magnitude is at least
  **1e6 · m** *and* the last **five** magnitude steps all increase. Both are
  required: the ratio names an explosion rather than a scale change, and the
  climbing tail names one in progress rather than a quantity that grew and
  settled at a new scale.
- **Replay line (standing rule 6), run before adoption and rerun by the
  adopting supervisor.** Corpus **974 monitored-quantity histories** across
  `demo-output` (194) and `/home/ubuntu/certonomous-runs` (780):
  `coefficient.dat` Cd and Cl plus forces-object `moment.dat`/`force.dat`
  total_x columns. **Fires on exactly 5, FATAL on 5, zero completed-run
  false positives across the remaining 969.** Every fire is a run the
  record already names diverged: the two F8 specimen histories at 83.3 and
  84.5 orders — caught by nothing else in this standard — and three
  dpw5-committee-probe histories at 20.9 to 29.5 orders from runs recorded
  "diverged, signal 8", an S1 overlap of the same acceptable kind S3
  carries. Reproduce with
  `demo-output/website/campaign/F8_runs/s10_replay/s10d_corpus_replay.py`.
- **The rail clause.** The same amendment widens
  `sdk/scripts/replay_s12_unsettled_stop.py`'s corpus to forces-object
  `moment.dat`/`force.dat` histories: the specimen lived in exactly such a
  file, so the coefficient-only glob meant the archive-replay rail could not
  ingest the standard's own best specimen at all.
- **What is deliberately not added.** S6 and S4 FLAG this specimen saying
  only "unconverged" — the same words they use for a mild stall — and the
  adopting review considered a separate FLAG-to-FATAL conversion clause for
  that pair. Judged unnecessary: S10d *is* the conversion rule for the class
  (the magnitude is the evidence that separates a catastrophe from a stall),
  and a stall without explosion is honestly a FLAG. If a future specimen
  stalls fatally without tripping the magnitude clause, that is a new rule's
  motivating case and it enters through the innovation path with its own
  replay line, not by escalating S6 here.
- Severity: **FATAL**. Action: no quantity computed from that state is
  evidence, whatever the residual block reads; triage as a divergence and
  withdraw any number already published from it.
- Status: implemented (`detect_magnitude_explosion` in
  `sdk/chief_engineer/log_signatures.py`, exactly as pre-registered in the
  proposal's gate field; wired beside S12 at the settle-audit collection
  point in `sdk/workflows/tmr_verification.py`, so every history read there
  records both verdicts). Tests assert the motivating specimen fires from
  its file on disk, the archive sweep names the known fires and no others,
  and the settled flat-plate histories stay silent.

### S12. Unsettled stop (proposal `w7-cap-stopped-is-a-monitor-signature`)

**Adopted 2026-08-02.** Closes section 3.4 item 2, and is the first rule in this
standard that does not read the residual block — which is section 3.4 item 3,
answered rather than merely recorded.

- **What it names.** A run that ended while the coefficient it is quoted for was
  still travelling in one direction. The residual is fine, the field is fine,
  the run completes, and S1 through S11 all stay silent, because none of them
  looks at the monitored quantity's history. L-24 one level up: a run is not
  converged, a *quantity* is.
- **Detection.** Over a trailing window (a quarter of the iterations, floored at
  20 and capped at 2000), the mean of the window's second half minus the mean of
  its first, divided by the window's mean magnitude, is the **relative drift**;
  the fraction of steps inside the window that move in the drift's own direction
  is the **monotone fraction**. Fires when relative drift is at least **1e-3**
  *and* the monotone fraction is at least **0.90**. Both are required: a settled
  history wobbles without displacement, a truncated one travels.
- **Why drift and not spread.** The Verification Charter's settle criterion
  (section 4, in force inside `sdk/workflows/tmr_verification.py`) measures
  peak-to-peak spread against `SETTLE_TOL = 3e-7` **absolute in Cd**. That is
  correct for the flat plate it was measured on and wrong as a monitor rule,
  which must grade a duct, a wing and an Ahmed body against their own scales.
  Direction is scale-free.
- **Where the thresholds come from — one case against itself, not a
  percentile.** The 208896-cell TMR flat plate is in the archive twice:

  | rung | iterations | relative drift on Cd | monotone | S12 |
  | --- | --- | --- | --- | --- |
  | capped, the rung the charter records | 15000 | **−4.131e−03** | 1.000 | **fires** |
  | the same case, after it settled | 21000 | +3.716e−07 | 0.552 | silent |

  The tolerance sits 4.13x below the firing rung and 2690x above its settled
  twin; the monotone floor sits below 1.000 and above 0.552. Accepting the first
  as settled is what published that ladder as a divergence at `p = -0.745`.
- **Replay line (standing rule 6).** Corpus **760 quantity-histories** from 380
  `coefficient.dat` files under `demo-output` and `/home/ubuntu/certonomous-runs`,
  718 of them long enough to grade; **36 fire** — 4.74% of the corpus, 5.01% of
  what it can grade — and **0 fatal**, the severity being FLAG. For scale, S1
  fires on 10 of 449 logs and the withdrawn S7 fired on 68 of 106. Reproduce
  with `sdk/scripts/replay_s12_unsettled_stop.py`; artifact
  `demo-output/website/monitor/replay_s12.json`.
- **The stop reason is carried, not tested.** The charter names the iteration
  cap. The archive shows the same signature behind a solver that stopped on its
  own residual criterion — **17 of the 36 fires** — and that stop is the more
  dangerous of the two, because it announces convergence. A rule keyed to the
  cap would have missed the larger half of what this one caught.
- **What it caught on adoption.** All four graded-rung (refinement 4) NACA 4412
  replicates, on lift, at monotone 1.000 — the family whose 12.74% mesh-
  construction scatter was published earlier the same day.
- Severity: **FLAG**. Action: the arithmetic is not in question and the value
  is; the run is recorded unsettled, never settled, and is either continued to
  flatness or published with its drift stated beside it.
- Status: implemented (`detect_unsettled_stop`, `unsettled_window` in
  `sdk/chief_engineer/log_signatures.py`). Tests assert the motivating pair:
  fires on the capped rung, silent on the same case once settled.

### The thermal three (S13–S15), adopted 2026-08-17 at rung K1a of F14

These three come out of one campaign and share one corpus, so their reach is
stated once, here, rather than three times in weaker words.

> **CORPUS REACH — READ THIS BEFORE QUOTING A FIRE RATE.** The corpus is the
> eleven committed K0c solver logs (`docs/campaigns/F14-cooling-ladder/K0c_runs/
> <case>/log.buoyantBoussinesqSimpleFoam[.stage2|.stage3]`) plus six control
> cases built for K1c, and nothing else. It is **one solver**
> (`buoyantBoussinesqSimpleFoam`), **one case class** (a sealed
> two-dimensional differentially heated cavity), **one mesh family** and
> **one physics regime** (laminar natural convection, Ra 1e3 to 1e6). It is
> not a sample of this lab's logs and no rate measured on it transfers to the
> registry at large. What it IS is the complete population of thermal solves
> this lab has run, which is the population these rules are for. Section 3.1's
> standing complaint — that six rules were adopted on a corpus selected by a
> filename accident — is answered here by naming the population rather than by
> pretending to a larger one.
>
> S13 and S15 are additionally **not general log rules**: S13 needs the caller
> to nominate which printed quantity the run is graded on, because no log says
> that, and S15 needs to know which of a case's logs produced the field being
> audited. Both are therefore invoked per audit rather than swept over the
> registry, and neither is claimed to have a registry-wide fire rate.

### S13. Converged residuals over a graded quantity that is still moving

- Detection: the peak-to-peak spread of a solver-printed monitored quantity,
  over a **fixed window of outer iterations**, exceeds
  `thermal.monitor_peak_to_peak_max_pct` in `docs/physics_rules.yaml` (0.02%
  over 400 iterations sampled every 50, giving 9 samples). Fewer samples than
  span the window is `CANNOT_TELL`, never a score. The solver's own
  convergence statement is **not** evidence against this signature: S13 exists
  precisely for runs that print it.
- **The normaliser (1.12, D389).** The peak-to-peak spread is a percentage of
  **the range the quantity spanned over the whole run**, `max(series) −
  min(series)`, and **not** of its absolute mean. A criterion normalised by the
  mean measures the OFFSET on any quantity that carries one. It went unnoticed
  because K0c and K2e both grade a Nusselt-like O(1) group whose mean and range
  agree within a factor of a few — measured across 49 cases the two normalisers
  differ by 0.1×–12× there, and by **51×–1.4e9** on K2b's absolute
  temperatures. The threshold NUMBER is unchanged at 0.02 %: its original
  derivation, "one fiftieth of the tightest pass band K0c gated on", was always
  a fraction of the thing being resolved, and the mean was only a proxy.
  **One verdict moves because of this and it is the finding, not the cost:**
  `K2bP_coarse` passed at 0.00101 % of its mean and fails at 3.3876 % of its
  range — agreeing with its heat balance (0.7857 % out) and with S13 read on the
  room's free boundary (0.03973 %), both of which already said the run was not
  converged. Threshold sensitivity over all 49 cases: identical verdict set for
  any value in **(0.0027 %, 0.0642 %]**, a 24× span, with 0.02 % inside it.
- **The null-variation clause (added 1.11, CORRECTED in 1.12).** A quantity that
  never resolvably MOVED is `CANNOT_TELL`, never a pass. **1.11 tested the
  window spread against the print resolution and that was wrong**: a spread of
  zero means "never started" on one case and "converged to the last bit" on
  another, and 1.11 refused both. It fired on four committed K2e cases
  (`m96_dT10_bou`, `m96_dT20_bou`, `m96_dT30_bou`, `m96_dT90_bou`) which print
  sixteen significant figures, bit-identical across the window, after travelling
  0.53 — as converged as a double-precision solve can be. **1.12 tests the RANGE
  OVER THE WHOLE RUN instead**, which is the quantity that separates the two and
  is the same quantity D389 requires as the normaliser: one repair, both faults.
  The range is compared against the precision the series is actually printed at — measured from the samples themselves, since the most precise
  sample fixes it and OpenFOAM strips trailing zeros — and a **range** below
  `thermal.monitor_min_resolved_ulp` (10) units in the last place is refused.
  **Why it is needed:** this rule asks *has the graded quantity stopped
  moving?*, and it cannot answer that on a quantity that never STARTED. At rung
  K2b the graded rack-inlet temperature of a fine-mesh case sat at exactly the
  supply temperature — printing `289.0000002` falling to `289` across the whole
  400-iteration window, a spread of 1 ulp in a ten-figure print — and **scored
  0.00000 %, the best score this criterion can return**, on a case whose heat
  balance was 2.6632 % out and whose free boundary was swinging 0.23585 %. Two
  of that rung's controls read perfectly on the same case for the same reason:
  the boundary-offset readback erred by 0.000e+00 and the mass-versus-area
  averaging comparison by −0.0001 %, both because the face was still uniform.
  **A monitor or a control is most flattering exactly where the case is least
  converged** — which is S14's identity argument, and this clause is S14's
  refusal transplanted into S13. The threshold is not load-bearing: re-graded
  over all fourteen affected cases the verdict set is identical for any floor
  from **2 to 13,161 ulp**, 3.8 orders of magnitude, breaking at 1 (too low to
  catch it) and at 13,200 (which starts refusing K0c's genuinely converged
  `Ra1e3_m32`, whose spread is 13,161 ulp).
- **What the clause does NOT do**, stated because a refusal is easy to read as
  a failure: `CANNOT_TELL` is not `NOT_CONVERGED`. It says the log cannot
  support either verdict on this quantity, and the action is to run further, to
  print more digits, or to grade a quantity that has actually responded — not
  to declare the case bad. Neither the endpoint difference over the
  same window nor the drift over the last quarter of the run is gated, and
  both are printed beside the gated number labelled NOT GATED, because a
  reader who sees only the number that gates cannot tell a choice was made.
  Endpoint differences alias against a case approaching steady state as a
  decaying oscillation whose period is near the window length; a
  fraction-of-run window silently loosens as a run is extended, so the same
  case passes by being run longer.
- Severity: **FATAL** for any number graded off that quantity. The arithmetic
  is sound and the answer is not converged, which is a different fault from
  S3 or S6 and is not covered by either: those watch the residuals, and the
  whole content of this signature is that the residuals were fine.
- Action: continue the run, or report the drift beside the number. Never both
  quote the number and omit the drift.
- Status: **wired**, `classify_monitor()` in `scripts/check_convergence.py`,
  mode `--monitor-regex`. Thresholds read from `docs/physics_rules.yaml`,
  including `thermal.monitor_min_resolved_ulp` for the null-variation clause;
  the print resolution is measured by `print_resolution()` in the same module.
- **Replay line.** Corpus: the eleven committed K0c logs. Fires on **1 of 11**
  (`C3_Ra1e5_m64_source`, peak-to-peak 0.123720% against 0.02%); silent on the
  other ten, whose spreads run 0.000219% to 0.008403%. Fatal count on the
  graded set: **0 of 8** — every graded case passes, which is what makes the
  K0c gate's pass readable. Reproduces that rung's own published convergence
  table to six decimal places on all eleven rows, from the committed logs
  alone, which is the check that it is the same criterion and not a new one
  wearing its name.
  Behaviour on the case that motivated it: the K0c fine meshes under K0b's
  relaxation factors drifted 2.19%, 3.98% and 4.67%, and the g = 0 twin
  14.65%, all with `residualControl` met. S13 fires on all four.
  **And on this rung's own controls**: all six K1c control cases stopped on
  `residualControl` at 685 to 793 iterations with peak-to-peak spreads of
  0.176% to 0.575%. S13 fired on all six. Re-run to 4000 iterations they pass
  at 0.000e+00 to 1.793e-08%, and the planted-source recovery error improved
  by **four orders of magnitude**, from -7.943e-05% to +2.388e-09%. The rule
  changed this rung's own numbers; it is not decorative.
  **Re-grade under 1.12 (2026-08-18), which supersedes the 1.11 re-grade
  below.** Corpus widened to **all 49** committed cases — K0c's eleven, K2e's
  thirty and K2b's eight. **Against the ORIGINAL criterion exactly TWO verdicts
  change, both K2b's:** `K2bP_fine` `CONVERGED` → `CANNOT_TELL` (it never
  resolvably moved) and `K2bP_coarse` `CONVERGED` → `NOT_CONVERGED` (3.3876 %
  of its range). **All eleven K0c and all thirty K2e verdicts are unchanged.**
  Against 1.11 as shipped, five change: those four K2e false positives are
  repaired, plus `K2bP_coarse`.
  **The 1.11 re-grade was UNDER-SCOPED and that is recorded rather than quietly
  fixed:** it covered fourteen cases and omitted K2e's thirty, which had been
  graded under the old reading too and were sitting in the tree at the time.
  Widening the corpus is what exposed 1.11's false positive.

  **Re-grade under the 1.11 null-variation clause (2026-08-18), superseded.**
  Corpus: the eleven committed K0c logs plus K2b's three. **Exactly one verdict
  changes** —
  K2b's fine mesh moves `CONVERGED` → `CANNOT_TELL`. All eleven K0c cases are
  untouched, four `CONVERGED` and seven `NOT_CONVERGED` as before, and the
  closest of them to the new floor is `Ra1e3_m32` at **13,161 ulp**, three
  orders clear of it. A repair that moved the K0c corpus would have been a new
  criterion wearing the old one's name; this one does not.
  **And the defect is visible in this replay line's own text, above, which
  nobody read as a defect.** The K1c controls re-run to 4000 iterations are
  recorded here as passing "at **0.000e+00** to 1.793e-08%". A spread of
  literally zero is exactly what the 1.11 clause refuses. Those six cases would
  be `CANNOT_TELL` under it — **stated and not measured**, because K1c's logs
  are not in the committed tree and the re-grade could not be run against them.
  Whoever next has those logs owes this line a number.

### S14. A closure number quoted as evidence on a sealed case

- Detection: the audited case has **no non-wall active patch** (so no advective
  enthalpy flux) **and** the solver's own log reports that no finite-volume
  option was constructed (so no volumetric source). Under those two conditions
  the boundary heat balance is very nearly an identity: `div(phi,T)` integrates
  to zero because `phi` is conservative and no wall passes mass, so the
  boundary conduction terms are forced to sum to zero at **every** iteration,
  converged or not.
- Severity: **CONFIGURATION RISK**, in the sense this standard's preamble gives
  that word — the severity that sits outside the ladder — and for the same reason — the numbers are untouched and stand; what is at fault
  is the sentence a reader is about to write about them. It is never FATAL,
  because the closure figure is not wrong, and it is never folded into
  "nothing fatal", because it is not a verdict on the arithmetic.
- Action: the report stamps `closure_is_identity_class` and prints, in words,
  that a passing number here is not evidence the physics is right. Per W-2 a
  quantity derivable by construction cannot gate anything, so the row is
  reported and never counted as evidence for a rung.
- Status: **wired**, `scripts/heat_balance.py`, keys `closure_is_identity_class`
  and `closure_identity_basis` in the JSON and a stamped block in the printed
  report. The three-valued answer is deliberate: `true`, `false`, and `null`
  for UNKNOWN when the log cannot answer.
- **Replay line.** Corpus: the six K1c control cases. Fires on **1 of 6** —
  `KC0_nosource`, the only sealed source-free case in the set — and is silent
  on the four planted cases and on the probe. Fatal count: **0**, by
  construction; the severity is not fatal.
  Behaviour on the case that motivated it: K0b pre-registered "imbalance above
  20% on an early, unconverged snapshot" and measured **0.0128%** at iteration
  10, never above 0.13% at any iteration. Re-measured at K1c on the same case
  class, the sealed no-source control closes to **0.000000005%** with a net
  leak of -5.960965e-14 W against 1.298878e-03 W of heat crossing the boundary. That number is not an achievement and S14 is what says so.
  The contrast that makes the rule readable: the same auditor's recovery of a
  **planted** source on the same mesh tracks the T residual across seven
  decades, -24.139% at iteration 100 to +2.388e-09% at 4000. One of those two
  quantities measures the solution; the other measures the discretisation.
- **The other branch, added 2026-08-17 at rung KV1, because S14's detection is a
  two-condition conjunction and its negation was silent rather than answered.**
  When the case is **open** — a non-wall active patch, so mass crosses the
  boundary — S14 does **not** fire and the closure is a genuine measurement. It
  is convergence-sensitive, because the advective enthalpy flux depends on the
  solution rather than being forced by the discretisation. Measured at KV1 on
  one heated duct at eleven iteration counts: **20.881% at iteration 20, 0.593%
  at 80, 0.000000% at 201**, tracking the T equation's own initial residual
  across nine decades, with the exit code flipping 1 → 0 between iteration 80
  and 100 as it crosses the governed 0.5% band. The sealed case never
  approaches its gate; the open one crosses it.

  **Three things must travel with any open-case closure number and S16 below is
  the rule that enforces the third.** (i) It catches an unconverged energy
  field, a mis-set temperature offset, a flow-rate mismatch between a face
  pair, and a patch omitted from the ledger. (ii) It rests on the boundary
  conserving mass, which `scripts/heat_balance.py` now gates against the same
  `heat_balance_tol_pct`. (iii) **It establishes nothing about circulation.**

### S15. A plant witnessed in the dictionary and not in the solver's log

- Detection: read every solver log in the case for OpenFOAM's own construction
  lines — `Selecting finite volume options` against `No finite volume options
  present`. Three findings, all reported and none inferred: the logs say
  **none** while `constant/fvOptions` exists (a plant the solver never opened
  is a silent no-op that reads exactly like a clean case); the logs
  **disagree** with each other (a case holding a history it did not all run);
  or there is **no solver log** at all, which is UNKNOWN and is reported as
  UNKNOWN rather than as a `false`.
- Severity: **FATAL for the control**, never for the case. A control whose
  plant did not reach the solver has not run, and a control that has not run
  yields UNKNOWN, never PASS — this is `scripts/control_kind.py`'s rule that a
  broken instrument is not a clean bill of health, applied to a plant instead
  of to a pattern.
- Action: rebuild the case cleanly and re-run. Never adjudicate between
  disagreeing logs by taking a vote; picking either reading invents the
  history.
- Status: **wired**, `fvoptions_witness()` in `scripts/heat_balance.py`, keys
  `fvOptions_in_log.state` and `.per_log`.
- **Replay line.** Corpus: the six K1c control cases and the eleven committed
  K0c logs. Fires on **1 of 6** at first attempt — and the one it fired on was
  the **negative control**. `KC0_nosource` was copied from the committed
  `C3_Ra1e5_m64_source` case and inherited its `.stage2` and `.stage3` logs;
  the fresh solve overwrote only `log.buoyantBoussinesqSimpleFoam`, so the case
  held one log saying `none` and two saying `constructed`. Reported
  `disagreement`, identity class UNKNOWN. Without this rule the no-source
  control would have read as **planted** and the control set would have been
  quietly worthless. The cases were rebuilt with the foreign logs removed and
  all six then report a single consistent state. Fires **0 of 11** on the
  committed K0c logs, whose staged logs agree with each other by construction.
  Behaviour on the case that motivated it: K0b's C3b, where the plant was
  verified in the solver log rather than in the input file precisely because
  an `fvOptions` the solver never opened reads as a clean pass. S15 makes that
  one-off check standing.

### S16. An open-case closure number cited as evidence about a flow field

- Detection: a closure or heat-balance figure from a case with through-flow
  quoted in support of a claim about **where the energy went** — aisle flow,
  recirculation, short-circuiting, rack inlet temperatures, any θ.
- Severity: **CONFIGURATION RISK**, exactly as S14 and for exactly the same
  reason: the number is not wrong, the sentence about it is. Never FATAL.
- Why it is a separate rule and not a clause of S14. S14's whole content is
  "this number is near-identity, so it is not evidence." S16's content is the
  opposite shape: the number **is** a measurement, and is still not evidence for
  *this* claim. Folding them together would let a reader who has satisfied S14
  by opening the domain believe they had answered S16 too, and that is precisely
  the inference K2b is at risk of making.
- The statement, carried verbatim from `K2a_RACK_ROW_MODULE_SPEC.md` §8 rather
  than re-derived loosely, because it is already written correctly there:

  > A solve with the aisle flow structure entirely wrong — supply
  > short-circuiting to the return, reversed aisle recirculation — still closes
  > perfectly once converged, because closure tests conservation, not *where*
  > the energy travelled. […] Closure is therefore **necessary, never
  > sufficient**, and no K2b sentence may cite it as validation evidence;
  > validation is K2c's gate alone.

- Action: the closure figure stands and is reported. The sentence is struck or
  re-sourced to a validation gate.
- Status: **partly wired.** `scripts/heat_balance.py` prints the
  necessary-never-sufficient warning on every open-case report and carries it in
  `closure_identity_basis`, and `docs/physics_rules.yaml` holds
  `heat_balance_closure_establishes_circulation: false`. The *citation* side is
  **not** wired: nothing scans prose for an open-case closure figure supporting a
  circulation claim, and this rule is therefore enforced by reading. Said
  plainly rather than left to be assumed from "wired" appearing elsewhere on
  this page.
- **Replay line.** Corpus: **zero cases.** This lab has run exactly three
  open-domain thermal solves, all of them at KV1, all of them straight ducts
  with one inlet and one outlet — geometries with no circulation to get wrong.
  So S16 has **never fired and could not have**, and no fire rate is claimed.
  It is adopted **before** the population it governs exists, which is the
  opposite of this standard's usual practice and is deliberate: K2b is the
  campaign that will produce that population, and a rule written after the first
  closure figure is quoted arrives too late to stop the sentence it exists to
  stop. When K2b runs, this line must be replaced by a measured one.

## 3. The set as a set, reviewed 2026-07-31

Sections 1 and 2 grade each rule on its own. This section grades the standard,
which is a different question and one nobody had asked. Adding rules one at a
time produces a set whose overall behaviour nobody has measured, and the two
things that matter about a monitor are what it catches and what it says about
work that was fine.

> **A rule nobody has replayed against real logs is a hypothesis, not a check.**

### 3.1 What has actually been replayed

| Rule | Replayed against | Fires on | Status |
| --- | --- | --- | --- |
| S1 FPE | **449 archived logs** | **10, FATAL on 10** | **validated 2026-08-01.** Every one of the ten carries a `Foam::sigFpe::sigHandler` stack frame, so every fire is a run that actually died. No completed run is named. See 3.5. |
| S2 NaN | **449 archived logs** | **0** | **replayed 2026-08-01, and it fires on nothing.** No false positive and no true positive: the archive holds no NaN on a line this rule reads. Three logs carry one on a line it does not. See 3.5. |
| S3 residual spike | **449 archived logs** | **14, 298 findings, 0 fatal** | **validated 2026-08-01, with a weakness.** 6 of the 14 also carry the FPE stack trace, so the rule agrees with a run that died. 221 of the 298 findings sit on one completed run. See 3.5. |
| S4 bounding | **449 archived logs** | **158, 38923 findings, 0 fatal** | **measured 2026-08-01, and the documented rule is not the implemented rule.** The startup scoping this standard states for S4 exists nowhere in the code. See 3.5. |
| S5 first-seen warning | **449 archived logs**, read as if every run were novel | **225 logs, 237 findings, 2 distinct keys** | **replayed 2026-08-01, and the finding is the key, not the count.** Both distinct keys are artefacts of the normaliser rather than facts about the logs. See 3.5. |
| S6 residual stall | **attempted 2026-08-01 against 123 steady logs; 46 carry a recoverable target and all 46 are one family** | **not counted, and now for a specific reason** | **still unmeasurable.** The one family that archives its own `fvSolution` declares `p 1e-15`, which no run reaches, so the gate that makes S6 mean anything is vacuous exactly where it can be read. See 3.5. |
| ~~S7 oscillatory divergence~~ | **106 archived steady logs** | **68, FATAL on 65** | **WITHDRAWN 2026-08-01**, on these measurements. It is the only rule this standard has ever removed. See 3.2 and the S7 entry. |
| S8 Courant excursion | **4 archived transient logs, 13308 time steps, 417 ledger rows** | 0 healthy runs | **validated.** Tolerance measured, not assumed: largest healthy overshoot 0.403 percent against a 2 percent tolerance, longest healthy monotone run 17 steps against a window of 20. |
| S9 wall time | **208193 ledger rows** | 19 FLAG, 11 FATAL | **validated**, with a recorded weakness. The six ~16300 s runs land at 1070x and 2214x their own p99 and were all recorded ok at the time. |
| S10 divergence behind a converged residual | **383 archived solver logs**, and 157 for the norm branch | **exactly 1**, the withdrawn run | **validated, and the strongest rule here.** A test sweeps the whole archive and fails if a second log is ever named. |
| S11 system operations | every run, by design | **every run** | **outside the ladder, and correctly so.** See 3.3. |
| S12 unsettled stop | **760 quantity-histories** from 380 archived `coefficient.dat` files, 718 gradeable | **36 (4.74%), 0 fatal** | **validated 2026-08-02, on one case against itself.** Fires on the flat-plate rung stopped at 15000 (relative drift −4.131e−03, monotone 1.000) and is silent on the same case at 21000 once settled (+3.716e−07, 0.552). The first rule here that reads a coefficient history rather than the residual block. |
| S10d magnitude explosion | **974 quantity-histories** across both corpus roots: coefficient Cd/Cl plus forces-object total_x (the v1.4 rail widening) | **5, FATAL on 5** | **validated 2026-08-08, replay rerun by the adopting supervisor.** Fires on the two F8 specimen histories (83.3 and 84.5 orders, caught by nothing else here) and three dpw5 histories from runs recorded "diverged, signal 8". Zero completed-run false positives across the remaining 969. The second history-reading rule, and the first FATAL among them. |

~~**Seven of eleven rules have never been replayed against the archive.**~~
**Superseded 2026-08-01: six of the seven have now been replayed, and the
sentence is left visible because the review that wrote it was right.** Six of
those seven were the rules the monitor already shipped with before the reading
program, which is exactly why nobody thought to measure them: they were
inherited rather than proposed, so they never met the intake requirement that
`GOALS_AND_PROPOSALS_CHARTER.md` disqualifier 10 now imposes on new ones. **The
disqualifier binds new rules and the old ones were grandfathered in without
anybody deciding to grandfather them.** That was the finding of this review, and
the review priced the remedy correctly: replaying S1 through S6 cost a
zero-compute afternoon. It did not return nothing. See 3.5.

The honest reading of the table as it stood: the three rules the lab measured
before adopting were the three it could defend. The one it adopted on reasoning
alone is the one that failed. That is a small sample and it points the same way
as D12. The replay adds two more rules the lab can defend, S1 and S3, and two
it cannot describe accurately, S4 and S5.

### 3.2 The one rule that fired too often, and is now withdrawn

**Resolved 2026-08-01: S7 is withdrawn**, by supervisor ruling R1 taking option
B on conflict C-2. This section is kept in the past tense rather than deleted,
because the finding is the durable part.

S7 was the whole of this category. Ungated it fires on 68 of 106 archived
steady logs and reaches FATAL on 65, every one of them a completed run whose
results are on the record. Four tightenings were measured and none rescued it:
68, 40, 59 and 23 respectively. It also cannot separate the two logs of the
case it was written for — 22 firings on the sick one, 20 on the healthy one —
which is the sharpest statement available about a detector.

Its shipped gate was not a measurement. The archived logs do not record the
residual target each run was aiming for, so the corpus cannot be replayed with
the gate in place, and the gate was reasoning from the proposal's own wording
plus S6's measured behaviour. **S7 was the only rule in this standard whose
form had no evidence behind it.** It was filed as C-2 in `PROPOSALS_OPEN.md`
rather than quietly kept, and the ruling on C-2 removed it: a detection rule
nobody can validate is worse than no rule, because it is trusted.

**This category is now empty**, and the standard would rather it stayed empty
than filled by a rule that survives on the fact that nobody measured it.

Nothing else in the set is in this category on the evidence available. S11
fires on every run and is not a false positive, for the reason in 3.3. The
seven unreplayed rules cannot be placed in or out of this category at all,
which is the point of 3.1.

### 3.3 Why a rule that fires on everything is usually broken, and why S11 is not

The verification charter's section 5 states the test: a rule that fires on two
thirds of known-good work is measuring the population, not the defect. S11
fires on one hundred percent of runs on this host and is correct.

The test has a scope that was never written down, and this is the place to
write it: **it applies to a rule that returns a verdict on the numbers.** S7
claimed a run diverged, so its firing on 68 completed runs was 68 false claims,
and it is withdrawn.
S11 claims the host allows case files to compile and execute code, which is
true on every run because the switch is on for every run. Its fire rate is a
property of the machine, not a discrimination failure, and the day it stops
firing is the day somebody turned the switch off.

Two conditions separate the two cases, and a future severity that sits outside
the ladder has to meet both:

1. **It makes no claim about the numbers.** A configuration risk never moves
   the anomaly count, the by-kind table or the fatal verdict, and it is never
   folded into "nothing fatal".
2. **Its fire rate is a measured property of the environment**, with the
   measurement on the record. S11's is:
   `/usr/lib/openfoam/openfoam2606/etc/controlDict` line 75, shipped
   `allowSystemOperations 1` by the Debian package and reported unmodified by
   `dpkg --verify`, against OpenFOAM's compiled default of `0`.

### 3.4 Failure modes seen this week with no rule at all

Four, and they are listed with what each would take.

1. **A solve that never started and left a plausible directory behind.** Half
   the race design set, 88 of 176, carried no result: every log holds only a
   launcher stub, and the act reported the ensemble without saying part of it
   was missing. S6 catches a residual that stalls; nothing catches a log with no
   solver output in it at all. This is the cheapest rule in this list to write
   and the failure mode least likely to be noticed. Docket
   `w7-solver-stub-detector`.
2. **A rung stopped by its iteration cap and recorded as settled.** *Closed
   2026-08-02 by S12, which is broader than this entry asked for: the archive
   showed that 17 of its 36 fires are runs that stopped on their own residual
   criterion rather than on a cap, so the rule is keyed to the moving quantity
   and records the stop reason as evidence.* The
   208896-cell flat plate rung was asked for 15000 iterations, read 1.05 percent
   above its settled value with the coefficient still falling by 1.04e-5 per
   thousand, and took 36000 to settle. Nothing in S1 through S11 fires: the
   residual is fine, the field is fine, the run completes. The signature is
   readable from the log without any new instrumentation, because it is the
   iteration counter reaching the configured cap while the monitored coefficient
   is still moving by more than the settle tolerance. Verification charter
   section 4 now carries the criterion.
3. **A monitored quantity that is not a residual.** *Answered 2026-08-02 by
   S12, which reads a coefficient history and nothing else. The boundary this
   item drew was real: the rule that closes item 2 could not have been built
   out of anything S1 through S11 look at.* S1 through S10 all read the
   residual block or the solver's own status lines. The failure in item 2 lives
   in the coefficient history, which the monitor does not currently watch, and
   L-24's rule is that a run is not converged, a quantity is. A monitor that
   only reads residuals can only ever grade one quantity.
4. **Nothing here can see six of this week's eight defects, and that is a
   boundary rather than a gap.** The certificate caption, the defaulted
   confidence level, the trace label, the leaked drag qualifier, the
   misattributed audit finding and the mis-named polar all happened downstream
   of a correct solve, in the display and record layers, where a solver log
   signature has nothing to look at. Those belong to
   `VERIFICATION_CHARTER.md` sections 6 and 14 and to `scripts/self_audit.py`.
   Recording the boundary matters because a lab with a good monitor can come to
   believe the monitor is the check, and this week the monitor was not where the
   defects were.

### 3.5 Replaying the six grandfathered rules, 2026-08-01

Run by `sdk/scripts/replay_monitor_rules.py`, which writes
`demo-output/website/monitor/replay_s1_s6.json`. No compute: every number below
comes from a file already on disk, and the whole sweep took 156 seconds.

**The corpus.** Every `*.log` under `demo-output`, which is the same root the
S10 archive sweep uses, so the two measurements are comparable. **449 logs**
today, against the 383 S10 was measured on. 144 of them carry residual lines,
123 steady and 21 transient; 305 carry none, which is a fact about the archive
worth knowing on its own, since most of what the lab keeps is not a solve.

**S1, validated.** Ten logs, ten fatal, and every one of the ten carries a
`Foam::sigFpe::sigHandler` stack frame. Not one completed run is named. This is
the cleanest result of the six and it retires the concern the review recorded:
the handler-versus-banner distinction was reasoned from the source, and the
sweep confirms the reasoning caught only handlers.

**S2, zero fires and one boundary.** No archived log carries a NaN on a line
this rule reads, so the rule has no false positives and no true positives here.
Three logs carry a NaN on a line it does not read: the adjoint gradient
comparison prints `Relative Error (Jan - Jfd) / Jan : nan`, which is a reported
quantity rather than a residual. That is outside S2's scope as written and it
is the same boundary 3.4 item 3 names, so it is recorded rather than fixed by
widening a rule whose purpose is the residual block.

**S3, validated, with a weakness.** 14 of 449 logs, 298 findings, none fatal.
Six of the 14 also carry the FPE stack frame, so on those the rule is agreeing
with a run that died. Seven of the remaining eight end with OpenFOAM's `End`.
The weakness is distribution rather than rate: **221 of the 298 findings sit on
one completed run**, `f6a_diff_LRR_v4`. The suppression discipline in standing
rule 2 caps reports per step, and a run with thousands of steps still
accumulates.

**S4, and the documented rule is not the implemented rule.** 158 of 449 logs,
38923 findings, none fatal, and 100 of the 158 end with `End`. Section 1 states
S4's severity as "WATCH during the first ten percent of iterations, FLAG when
persistent past startup". **No part of that exists in the code.**
`LogMonitor._bound` raises one undifferentiated `bounding` anomaly with a blank
severity; there is no iteration fraction, no WATCH, and no escalation. The only
startup notion anywhere in the stack is a sentence in
`head_engineer.diagnostics()` reading "normal in startup, suspect if persisting
past ~100 iterations", which is a different threshold and is prose on a report
rather than a severity on a finding. A rule documented with a ladder it does not
have is worse than one documented plainly, because the reader grades the finding
by a severity the finding never carried.

**S5, and the finding is the key rather than the count.** Read as if every
archived run were novel, S5 raises on 225 of 449 logs, 237 findings. That number
is not a false-positive rate, because none of those runs was novel; it is an
upper bound on how often the rule can speak. What the sweep does settle is the
rule's vocabulary, and it is **two distinct keys over the whole archive**, both
of them artefacts of the normaliser:

1. OpenFOAM's ordinary multi-line spelling puts `--> FOAM Warning :` on one
   line and the message on the lines after it. S5 keys on the single line it is
   fed, so **146 logs collapse to one key that carries no information about the
   warning at all.** Every distinct warning in those runs is indistinguishable
   from every other, which is why S5's knowledge capture has never produced
   anything to capture.
2. The key normaliser is `re.sub(r"[0-9.eE+-]+", "#", ...)`, which treats the
   letters `e` and `E`, the dot and the hyphen as number characters wherever
   they appear. `allowSystemOperations` keys as `allowSyst#mOp#rations`. Two
   genuinely different warnings differing only in those characters key the same
   and the second is suppressed as already seen.

Neither is fixed here. S5's detection is being changed, not its documentation,
and standing rule 4 sends that through the innovation path with the measurement
attached, which is what this section provides.

**S6, still unmeasurable, and now for a specific reason.** The review recorded
that the archived logs do not carry the `residualControl` target S6 needs. They
do not, but 46 of the 123 steady logs sit beside the case that produced them and
that case's `system/fvSolution` does, so the corpus is not empty. **All 46 are
one family**, `demo-output/website/dafoam/ladder-b/B3_work`, and its declared
target is a single entry, `p 1e-15`, which no run reaches. The gate that makes
S6 mean anything is therefore vacuous exactly where it can be read: every field
is above target forever, so any plateau fires. Under it S6 names 37 of the 46,
and that number is a property of the degenerate target rather than a fire rate
for S6. Reporting it as a fire rate would be the same error S7 was withdrawn
for.
**What S6 needs is not a cleverer sweep, it is one archived case outside this
family that declares a target it actually reaches.**

**Found on the way, and not fixed here.** The S10 archive sweep test
(`sdk/tests/test_log_signatures.py`, `ArchiveSweepTests`) asserts that exactly
one archived log carries a ceiling clip and it now fails: five do. Four are
finite-difference probe points under `ladder-b/S1_work/logs/fd_points`, each
printing `Bounding U<1000`, and they entered the archive after the test was
written. S10a is FATAL by this standard. The test is left failing and the
question of what rests on those four points is escalated rather than answered
here.

### S10a: the escalation answered, 2026-08-01, and the rule is worse off than it looked

The four points were audited against their own primal evidence
(`demo-output/website/dafoam/ladder-b/S1_work/logs/fd_clip_audit_run1.log`;
reading in section 3 of `S1_FIML_FIELD_INVERSION.md`). The finding is not about
those four points. It is about this rule's calibration.

**DAFoam gates its `Bounding` message on `printInterval`.** The S1 campaign ran
at the default `printInterval 100`, so each of its logs reports clipping from
**1% of its iterations**. Twelve points were re-run under the identical protocol
with `printInterval: 1` as the only change. Eleven of the twelve clip. The count
is **689 clip events where the archive recorded 3**, and the runs that clip
include the **unperturbed baseline** — whose archived log shows none — and both
runs the campaign's headline FD number is computed from (144 and 203 events).
Every re-run returned a **bit-identical objective and an identical iteration
count**, which is what establishes that `printInterval` changed only printing.

Three consequences, in order of how much they cost.

1. **"A ceiling clip appears in exactly one of the lab's archived logs" was
   never a measurement of solves.** It is a measurement of what solvers printed,
   and the printing is configurable. Section 2's false-positive sweep — "all
   three branches were run over every solver log the lab has archived, 383 of
   them, and together they name exactly one" — inherits that. The sweep is a
   floor, not a rate, and this standard should stop quoting it as a rate.
2. **S10a's severity is doing work its detection cannot support.** The rule's
   stated basis is that a clipped field "has left the physical range" and
   "every quantity integrated from it afterwards inherits that". That is true of
   the withdrawn A4 run, whose `omega<1e+16` clip is present at **every** printed
   iteration including its last, so its reported state *is* the clipped state.
   It is not true of a steady solver's startup transient: all 689 S1 events fall
   in iterations **27 to 142** of runs **1815 to 3291** iterations long, every
   run is clip-free over its final **95%+**, and the bound is inactive at the
   converged state the objective is read from. S10a fires identically on both
   and cannot tell them apart.
3. **The discriminator is persistence to the final iterate, and it is cheap.**
   A clip in the last N iterations of a run, or a clip co-occurring with S10b or
   S10c, is the fatal case; a clip confined to a startup window is not. In the
   archive as it stands that separation is exact: the withdrawn run is the only
   log tripping more than one branch, and `ArchiveSweepTests` now asserts that
   directly.

**Not changed here, and deliberately.** S10a stays FATAL and its detection is
untouched. Standing rule 4 sends a detection change through the innovation path
with the measurement attached, and this section is that measurement. What did
change is the test, which now **names** the four probe points and their
signature rather than counting them, so a sixth log cannot join them unnoticed;
and `classify_bound_line`'s docstring, which carried the 379-log calibration
claim. **The S1 FD verification itself stands** — see its own record; the clip
was audited, not waved away, and the objectives are bit-identical.

## 4. Standing rules for any monitor rule

1. A rule states its detection pattern, severity, and action before it ships;
   a rule that only prints is not a rule.
2. Repeated conditions are one finding, not hundreds: report a few instances
   per step, count the rest silently (the suppression discipline already in
   `LogMonitor`).
3. Banner text is never matched; only handlers and measured values are. A line
   the solver prints only when a condition holds is a measured value, not a
   banner, and that is the test S11 passes and the FPE trapping banner fails.
4. New rules enter through the innovation path (see
   `docs/standards/INNOVATION_STANDARD.md`): proposal, offline evidence
   against archived logs, then adoption.
5. A severity that is not about the numbers says so. It does not borrow FLAG
   or FATAL to be noticed, and it is not allowed to disappear into "nothing
   fatal" for being unable to. S11 is the first of these.
6. **Every rule carries its replay line: the corpus, the fire count, the fatal
   count, and its behaviour on the case that motivated it.** A rule with no
   replay line is labelled a hypothesis in section 3.1 and stays labelled until
   somebody runs it. This is the same requirement as disqualifier 10 in
   `GOALS_AND_PROPOSALS_CHARTER.md`, applied backwards to the rules that were
   already here when the disqualifier was written.
7. **A rule's severity is reviewed against its own fire rate, not only against
   the seriousness of the thing it names.** S9 assesses five reduced-order rows
   of 0.30 to 0.43 s as FATAL because it is purely relative, and the detection
   is arguably right while the severity is out of proportion to a third of a
   second. No absolute floor is added here, because no such floor was in the
   approved proposal and inventing a threshold is how a rule stops meaning what
   it says. Filed as an observation for the owner.

## Sources

- Certonomous mega-batch ledger and runner logs, examined 2026-07-25.
- Certonomous mission lessons, `sdk/chief-engineer-runs/mission-state/lessons`.
- Certonomous Numericist knowledge base, `docs/NUMERICS_KNOWLEDGE.md`,
  validated facts 3, 4, and 7.
- LogMonitor implementation and tests, `sdk/chief_engineer/head_engineer.py`,
  `sdk/tests/test_head_engineer.py`.
- S11 measured on this host 2026-07-31: `/usr/lib/openfoam/openfoam2606/etc/
  controlDict` line 75 (`allowSystemOperations 1`, shipped by the Debian
  package and reported unmodified by `dpkg --verify openfoam2606-common`),
  against OpenFOAM's compiled default of `0` at
  `src/OpenFOAM/db/dynamicLibrary/dynamicCode/dynamicCode.C` line 44. The four
  gated entry points are `codeStream.C:268`, `calcEntry.C:75`,
  `codedBase.C:302` and `systemCall.C:131`, all calling
  `dynamicCode::checkSecurity`. The standing rule is
  `docs/charters/VERIFICATION_CHARTER.md` section 13.
- Signature detectors for S6 and S9 (S7's was removed on withdrawal),
  `sdk/chief_engineer/log_signatures.py`, with tests in
  `sdk/tests/test_log_signatures.py` (including an integration test against
  a fixture slice of real ledger rows,
  `sdk/tests/fixtures/ledger_slice.jsonl`).

---

## Coverage in fact, and the wiring decision (2026-08-10)

Added by the Infrastructure/Standards family after the audit found the
adoption note above claiming coverage nothing supplies. **This table is the
honest statement of what fires where.** It is about REACHABILITY, not about
whether a rule is correct: every rule below is implemented and tested.

| rule | HeadEngineer (geometry studies, Ahmed, hump, UQ) | mega-batch ledger | offline replay | tests |
|---|---|---|---|---|
| S1-S5, S7, S10-S12 (ungated) | fires | — | fires | fires |
| **S6** residual stall | **fires on the six paths that call `stage_case`** — see the correction below; NOT on paths that stage a case another way | — | fires | fires |
| **S8** Courant excursion | **UNREACHABLE** (needs `courant_limit`) | — | — | fires |
| **S9** wall-time excursion | **UNREACHABLE** via `check_wall_time` | fires, via `wall_time_record_field` | — | fires |

`HeadEngineer.__init__` accepts `case_name, out_root, *, novel, on_event` and
builds `LogMonitor(novel=novel, on_anomaly=...)`: there is no parameter by
which S6's or S8's gate could be supplied. `LogMonitor.check_wall_time` has no
caller outside the tests.

### The decision: NOT wired, and this is a gap with a stated price -- not a limit

The lab approved these rules and never received them on its production paths,
so "leave it" would be enacting a refusal the owner never made. But wiring
them now would be an ADOPTION, and section 3.1 of this document requires a
rule to be replayed against the archive before it binds, with its fire count
stated. **That evidence does not exist for either rule**, and for S6 the thing
that looks like it is an artifact:

- **S6.** *(Superseded the same day -- see the corrected replay below. The
  original reasoning is retained because the corpus defect it uncovered is
  the finding.)* `replay_s1_s6.json` (2026-08-01) reported 37 fires over 46
  gated logs -- 80%, above the two-thirds that got S7 WITHDRAWN. Read one
  level down, **all 46 recovered targets were the same value, `p: 1e-15`**,
  a run-to-the-cap sentinel from a single case family that no solve reaches.
  The 37 was not S6's fire rate; it was one family measured against an
  unreachable number.

> **COVERAGE CORRECTED, 2026-08-10 (same day as the wiring). The gate works;
> the sentence about where it runs did not.** The v1.7 note said S6 "fires on
> production runs" against a column headed *"HeadEngineer (geometry studies,
> Ahmed, hump, UQ)"*. **The Ahmed act never arms it.**
>
> `arm_residual_gate` has exactly ONE non-test call site: inside `stage_case`
> (`head_engineer.py:986`). `ahmed_body.py` constructs a `HeadEngineer` and
> calls thirteen of its methods — `_run_step`, `collect_mesh_stats`,
> `restore_cached_mesh`, `decompose_for_parallel`, `postprocess` and more —
> **and `stage_case` is not among them.** It stages its case another way, so
> the gate is never armed and S6 cannot fire there.
>
> **Armed on exactly these call sites**, enumerated rather than named by
> family, because naming a family is precisely what went wrong:
>
> | path | line |
> |---|---|
> | `sdk/workflows/geometry_study.py` | 1819 |
> | `sdk/workflows/nasa_hump.py` | 575 |
> | `sdk/workflows/onera_m6.py` | 425 |
> | `sdk/workflows/crm_wingbody.py` | 187 |
> | `sdk/scripts/run_uq_studies.py` | 192 |
> | `sdk/chief_engineer/head_engineer.py` (own `__main__`) | 1652 |
>
> **NOT armed:** `sdk/workflows/ahmed_body.py`, and any future runner that
> stages a case without going through `stage_case`.
>
> **Why the tests could not catch this.** Every S6 test built its engineer
> with `HeadEngineer.__new__` and called `arm_residual_gate` directly. They
> prove the gate works WHEN ARMED and can say nothing about whether it GETS
> armed — a test that reaches past the constructor cannot see a constructor
> that never calls the thing. A test going through the real staging path is
> added with this correction.
>
> Nothing in the S6 pre-registration or its measured rates is affected: those
> are claims about the gate's behaviour when armed, and they stand.

### Before adopting any rule: state your corpus's reach

**Every input to a conclusion is an instrument** -- the search, the corpus,
the frame, the file list, the launch environment -- and each needs its reach
stated before anything is adopted against it. A replay is evidence about a
CORPUS before it is evidence about a rule, and a corpus assembled by a
filename convention is a filter nobody has audited.

So a replay filed under section 3.1 states, beside its fire count:

- **how the corpus was selected**, and whether that selection is a DERIVATION
  (what the artefact is) or a LIST (what it happens to be called);
- **what it could not see** -- compressed, untracked, differently-named,
  timed-out -- with a positive control proving it can see a known-present
  specimen;
- **what fraction of the plausible universe it covers**, measured, not assumed.

The cost of not doing this is on the record below: six rules adopted against
28% of the evidence, and the number that looked like a fire rate was one case
family measured against a target no solve can reach.

### The corpus behind six adopted rules was selected by a filename accident

**Corrected 2026-08-10, and this outranks the wiring question.** The replay
tool globbed `*.log` while OpenFOAM writes `log.<app>`, so the evidence that
discharges section 3.1 for S1-S6 was gathered over **449 files**. Deriving the
corpus from what a run actually WRITES -- an OpenFOAM application prints an
`Exec   :` banner line, which dictionary and field files never carry -- yields
**1,375 real run logs, a 3.06x corpus.**

**The fix is not a wider glob.** Matching `*.log` AND `log.*` together still
misses **96** of them (`logMeshCheck.txt`, `A5_logMeshGeneration.txt`,
`A4_coarse_log.checkMesh`): a list of patterns is the same defect with more
entries (L-49). Selection is now by content, with binaries excluded by a NUL
test rather than by extension, so **no naming rule participates at any point**.

**Re-run over the derived corpus** (`replay_s1_s6.json` regenerated; the
2026-08-01 artifact is retained as `superseded_<stamp>_replay_s1_s6.json`):

| | old corpus | derived corpus |
|---|---|---|
| logs swept | 449 | **1,375** |
| with residual series | 144 | 463 |
| steady | 123 | 408 |
| S6 gated logs (target recoverable) | 46 | **222** |
| families represented in S6's gate | 1 | **3** |
| distinct residual targets recovered | 1 | **8** |

Per-rule on the corrected corpus: **S1 38, S2 0, S3 44, S4 187, S5 1249**
logs fired.

**A published line in this document is refuted by the recovered files.** It
said no case outside one family reaches a declared target; **70 logs outside
that family carry real declared targets** (35 campaign, 35 mega-batch). They
were sitting in files the glob could not match.

### S6 survives its own evidence, and the honest rate is 47%

With the corpus corrected, S6 fires on 175 of 222 gated logs -- 79% -- but
that number still carries the sentinel. Separated:

| target class | logs | fire | rate |
|---|---|---|---|
| sentinel `1e-15` (unreachable by construction) | 135 | 134 | **99%** |
| **real declared targets** | 87 | 41 | **47%** |

**47% is the number section 3.1 asks for**, and it is well below the
two-thirds that withdrew S7. And it is not uniform: **dafoam 16/17 (94%),
campaign 18/35 (51%), mega-batch 7/35 (20%)** -- a spread that reads as a real
family-dependent behaviour rather than noise, and that a single global rate
would have hidden in either direction.

So the earlier refusal to wire S6 was right on the evidence then available and
is **no longer supported**: the replay section 3.1 requires now exists. What
remains before wiring is the per-case target derivation itself -- the recovery
must read each case's own `residualControl`, not whichever `fvSolution` sits
nearest, and the sentinel class must be excluded or the gate will fire on 99%
of that family. S8 is unchanged: still no replay, still needs one.
- **S8.** No replay exists at all. The archive holds 21 transient logs with
  residual series, which is the corpus a Courant replay would run over.
- **S9.** Live and correct on the ledger. `check_wall_time` is a SECOND entry
  point to the same rule with no production caller -- a one-implementation
  defect to resolve when someone wires it, not a coverage gap.

**Recorded as a gap, never as a constraint** (L-48): nothing here says these
rules cannot cover production. It says what each one needs first.

| to wire | needs | price |
|---|---|---|
| S6 | a replay over a representative corpus with REAL per-case targets, recovering `residualControl` per case rather than from whichever `fvSolution` sits nearest; then a per-case default on `HeadEngineer` | ~1 pass, 0 core-min |
| S8 | a Courant replay over the 21 transient logs; then `maxCo` from each case's `controlDict` as the per-case default | ~1 pass, 0 core-min |
| S9 | route `check_wall_time` to the governed path or delete it | folded into either of the above |

Both derivations point the same way and it is the day's standing discipline:
**the gate comes from the case's own dictionaries -- what configures the run
-- not from a caller who remembers to pass it.** A constructor argument would
reproduce the defect this correction is about, one layer up, because whoever
forgets it gets silence.

**Reach of this assessment** (L-43): the reachability claims are from reading
the three `LogMonitor` construction sites and every `check_wall_time` caller
in the repository. The S6 numbers are READ from the existing replay artifact;
this pass did not re-run the replay, and re-running it is part of the price
quoted above.


---

## S17. A RESIDUAL READ WHERE THE SOLVER DOES NOT READ IT (adopted 2026-08-25)

**Appended at the foot. Lines whose number changed above this section: 0.**

Id derived by hand from the HEAD blob (`grep -oE '^#+ S[0-9]+'`, max = 16) inside the committing
invocation, **not** from `scripts/append_record.py`, whose id regex is measured to run 14 short and
hands out colliding ids.

Adopted by the cfd supervisor, 2026-08-25, under Sanaa's desk-item disposal rule of the same date:
recommendation and reasoning attached, **ADOPTED unless she rules otherwise within one day**,
recorded `[lab-attributed]`. **Overrulable.**

### The rule

> **A residual criterion is read WHERE THE SOLVER READS IT. When a field is solved more than once
> per outer iteration, the criterion sees the FIRST solve; a tail-read of the log returns the LAST
> corrector's value. Reading the last where the solver reads the first is an INSTRUMENT DEFECT, not
> a rounding difference, and any convergence claim resting on it is withdrawn.**

### The measurement that produced it

`simpleControl` evaluates `residualControl` against the **initial residual of the first solve of
each outer iteration**. With `nNonOrthogonalCorrectors` set, pressure is solved repeatedly within
one iteration, and the *last* corrector's residual is smaller — often by orders of magnitude,
because that is the entire purpose of the corrector.

Measured on F12's closest analogue, F2 (`nNonOrthogonalCorrectors 2`, three `p` solves per
iteration), final iteration, the two readings side by side:

| field | FIRST solve — what the criterion reads | LAST solve — what a tail-read returns |
| --- | --- | --- |
| Ux | 9.6984e-07 | 9.6984e-07 |
| Uy | 1.8281e-05 | 1.8281e-05 |
| e | 7.1092e-06 | 7.1092e-06 |
| k | 9.9732e-07 | 9.9732e-07 |
| omega | 8.3760e-07 | 8.3760e-07 |
| **p** | **4.2657e-04 — ABOVE its 1e-4 threshold** | **3.2756e-06** |

**A factor of 130, on one channel, in the direction that flatters the run.**

### WHY THIS RULE IS HARD TO SEE, which is the reason it needs to be written down

**Only the corrected field is affected.** Every other channel is solved once per iteration, so its
first and last readings **coincide exactly** — as all five non-`p` rows above show. A reader
checking itself against `U`, `k`, `omega` or `e` finds perfect agreement and concludes it is
correct. **The instrument validates itself on precisely the channels that cannot expose it.**

The concrete cost here: a report stating that *"every single channel sat one to two orders of
magnitude below its own threshold"* was **struck for `p`** on this evidence. The truth was the
opposite of the claim — **iterations out of 2,000 in which every channel's first solve sat below
1e-4: ZERO.** The run never satisfied its own `residualControl` and ran to `endTime`. There was no
solver anomaly and no mechanism defect. **There was a reading defect, in this lab's own reader**,
and it had converted a run that never converged into a run reported as comfortably converged.

### What a monitor must do to satisfy S17

1. **Determine the solve multiplicity per field before reading anything** — `nNonOrthogonalCorrectors`
   and `nCorrectors` from the case's own `fvSolution`, read from disk, never assumed and never
   carried over from a sibling case. Multiplicity does not transfer between cases: F2 runs 2
   correctors and F12 runs **1**, so F2's 130x spread is **not** F12's number and may not be quoted
   as one.
2. **Extract the FIRST solve of each outer iteration** for any field whose multiplicity exceeds one.
3. **Prove the extractor discriminates, with a planted control** (standing rule 3). Plant
   distinguishable known values at a first-solve position and at a last-solve position in a copy of
   a log, and show the reader returns the **first**. A reader not shown able to tell them apart has
   not been shown to satisfy this rule, and its numbers are not evidence — **refuse rather than
   degrade.**
4. **Say which reading was taken**, on the face of any residual figure that leaves the monitor. A
   residual quoted without its solve position is incomplete.

### Standing of S17

**Not retroactive as a regrade**: closed verdicts are not reopened by this rule. It **is**
retroactive as a **disclosure** — any *live* convergence claim resting on a tail-read is withdrawn
until re-read at the first solve. S17 changes no gate and no threshold; it governs **where a number
is read**, never **what it must be**.

---

## Amendment (2026-08-27) — LIVENESS IS READ FROM FULL ARGV, AND AN ABSENCE CLAIM NEEDS A READER SHOWN ABLE TO SEE A PRESENCE

**Appended, append-only; no line above changed number. Raised by heat-transfer after
a near-miss; ansys hit the same trap the same morning. Verified here by execution on
the live box. Zero compute.**

### 1. THE CLAUSE

> **A liveness reading is taken from the FULL COMMAND LINE — `ps -o args` or
> `/proc/<pid>/cmdline` — never from `ps -o comm`.**
>
> **AND AN ABSENCE CLAIM CARRIES A POSITIVE CONTROL: the same reader, in the same
> invocation, shown finding a process KNOWN to be live.** A "nothing is running"
> report from a reader not demonstrated able to see something running is **not a
> finding**; it is `NOT MEASURED`.

### 2. THE MEASUREMENT, TAKEN ON THIS BOX

`comm` is the kernel's `TASK_COMM_LEN` field and is **truncated to 15 characters**.
The lab's solver is `buoyantBoussinesqSimpleFoam`; **`comm` shows
`buoyantBoussine` — exactly 15 characters, and the substring `Foam` IS GONE.**

**So a `grep "Foam"` over `comm` misses the solver entirely. Driven here, on the
live box, in one invocation:**

| reader | processes matching `Foam` |
| --- | --- |
| `ps -eo comm=` | **1** |
| `ps -eo args=` | **15** |

**Fourteen of fifteen invisible.** A supervisor grepping `comm` for `Foam` **came one
message from declaring its own two running solvers a crash.**

**AND A TRAP INSIDE THE TRAP, measured and disclosed because it defeats the obvious
defence:** the longest `comm` on this box is **36 characters**, so **`comm` is NOT
uniformly 15 wide and a reader CANNOT infer from the field's appearance whether ITS
process was truncated.** Some entries are full; the ones that matter are not.
**Truncation is per-process and unpredictable from the output — which is exactly why
the rule bans the reader rather than asking anyone to check for truncation.**

### 3. WHY THE POSITIVE CONTROL IS THE HALF THAT MATTERS

The clause's first sentence fixes **this** reader. The second sentence is what makes
the class of error detectable **next time, with a reader nobody has thought of yet.**

**This is standing rule 3 — the planted-zero control — applied to process liveness
instead of to a comparator.** A zero from a reader not shown able to see a non-zero
is not evidence, **and "no solver is running" is a zero.** `L-364` already
generalised the doctrine from a zero to a verdict; **this applies it to an
observation.**

**Two instances in one day, in two teams, on the same mechanism** — heat-transfer's
near-miss and ansys's `contention_sampler` note that `ps args` is used and never
`comm`. **Ansys had the rule and did not write it down; heat-transfer did not have
it and nearly reported a crash. A convention one team keeps is not a standard.**

### 4. THE CONSEQUENCE THAT MAKES THIS URGENT RATHER THAN TIDY

A false crash report is not a harmless error in this lab. **It invites a relaunch of
a case that is already running** — and standing rule 4's completion guard **refuses a
case where `0` or a time directory already exists**, so the relaunch either fails
noisily or, worse, lands beside a live run and corrupts the age guard that dates the
answer. **A liveness reader is therefore an instrument in the rule-4 chain, not a
convenience**, and it is held to the same standard as a comparator.

### 5. CONTROLS, BOTH LIMBS

| control | required |
| --- | --- |
| **positive** | the reader finds a **known-live pid** by full argv — run in the SAME invocation as any absence claim |
| **negative** | the reader does **not** match a pid known to be absent (a just-reaped or never-existing pid) |
| **truncation** | a process whose name exceeds 15 characters is found by the argv reader and **MISSED** by a `comm` reader — the limb that proves the rule is about the reader and not about the grep pattern |

**The truncation limb must be driven, not asserted.** A control set that omits it
demonstrates only that argv works, never that `comm` fails — **and the whole clause
is the claim that `comm` fails.**

---

## Amendment (2026-08-27) — A PROGRESS OR LIVENESS CHECK READS **ONE NAMED ARTIFACT**, NEVER A SET — AND MAKING THE SET DETERMINISTIC IS A TRAP, NOT A FIX

**Appended, append-only; no line above changed number. Zero compute. Three
independent measurements, on three different trees; verified here by execution.**

### 1. THE CLAUSE

> **A liveness or progress check reads ONE NAMED ARTIFACT — `log.solve` by name —
> never a glob, never a set.**
>
> **`--sort`, `-J1` and any other serial-ordering flag are NAMED HERE AS TRAPS, NOT
> REMEDIES.** A repair that keeps the set and orders it does not fix the check; it
> makes the wrong answer permanent.

### 2. THE DEFECT IS THE **SET**, NOT THE CONCURRENCY — and this is what makes the clause self-justifying

`type grep` on this box is a **shell function wrapping `ugrep 7.8.4`**, which
searches multiple files on parallel threads and emits per-file output in
**completion order**. That is the proximate mechanism and it is confirmed.

**But it is not the reason for the clause.**

> **THERE IS NO DEFINED "LAST FILE" IN A GLOB AT ALL.** Threading makes the choice
> **nondeterministic**; ordering makes it **arbitrary-but-fixed**. **Both are wrong
> for the same underlying reason**, and a lab that swapped `ugrep` for GNU `grep`
> tomorrow would still be wrong — **just quietly.**

**A clause resting on "which grep is installed" would expire at the next toolchain
change. A clause resting on the set has no expiry.**

### 3. ⚠⚠ THE TRAP, MEASURED, AND IT IS WHY `--sort` MUST BE NAMED IN THE CLAUSE ITSELF

On a **live, healthy** solver at `Time = 174`:

| form | result |
| --- | --- |
| plain glob `log.*` | **intermittently wrong** |
| **`-J1`** | **`Time = 0` on every trial** |
| **`--sort`** | **`Time = 0` on every trial** |
| **single named `log.solve`** | **correct on every trial** |

`log.writeCellVolumes` sorts alphabetically last and holds the zero, so ordering
selects it every time.

> **MAKING THE GLOB DETERMINISTIC CONVERTS AN INTERMITTENT LIE INTO A STABLE ONE:
> "stalled at `Time = 0`" reported unanimously about a solver running normally.**
> **AND CONSISTENCY IS WHAT READERS MISTAKE FOR CORRECTNESS.** An intermittent wrong
> answer eventually contradicts itself and invites a look; **a stable wrong answer
> never does.** It is the `DEAD_LEVER_AUDIT` §5 class — **a reading independent of
> the data it purports to report** — arrived at by *repairing* a check.

**A team that "fixed" this with `--sort` would pass its own before/after test.**

### 4. NO FAILURE RATE IS QUOTED, AND THAT IS DELIBERATE

Three independent measurements exist on three trees. **Their rates differ widely,
because the rate is a property of a SCHEDULING RACE NOBODY CONTROLS — thread count,
file sizes, page cache, what else the box is doing.**

> **THE CLAIM IS BINARY: a glob-fed last-line read CAN RETURN A VALUE FROM THE WRONG
> FILE. Quoting a percentage would attach a number to the schedule and invite a
> reader to decide the risk is small.** The failure rate is not a property of the
> defect and does not belong in the clause.

### 5. CONTROLS — and the second row is the one that is usually omitted

| control | required |
| --- | --- |
| named-artifact read on a live case | returns the **correct** value |
| **the glob form shown returning a DIFFERENT answer from the named-file read, on the same tree, in the same minute** | **REQUIRED** |
| the ordered forms (`--sort`, `-J1`) shown returning the **same wrong** value repeatedly | **REQUIRED** — or the trap is asserted rather than demonstrated |

> **A CONTROL THAT ONLY PROVES THE NAMED FORM WORKS DOES NOT PROVE THE GLOB FORM
> FAILS.** That is the planted-zero discipline (standing rule 3) applied to a
> **repair** rather than to a comparator, and it is the limb a team fixing its own
> monitor will naturally skip.

### 6. TWO FURTHER `ugrep` TRAPS ON THIS BOX, BOTH MEASURED TODAY

1. **`grep -r` honours ignore-files**, so a census built on it is **blind to exactly
   the gitignored material a census often exists to find.** Any `grep -r` whose
   completeness matters must say whether ignore-files were honoured.
2. **`--no-ignore` IS NOT A `ugrep` OPTION.** It errors to **stderr**; a pipeline
   carrying `2>/dev/null` then yields a **silent `0`** — a false zero from an
   unparsed flag. **The working flag is `--no-ignore-files`.** Found when a sweep
   reported "0 files contain `started_utc`" **after** the same field had been read
   from a file on disk.

**Both are the same shape as §1: a reader returning a confident answer to a question
it never asked.**

### 7. AUDIT STATE, WITH SCOPE LIMITS ON ITS FACE

- **heat-transfer — CLEAN, WITH A CONTROL.** Every `mark_done_*.py`, `analyse_*.py`
  and `grade_*.py` across `T-family`, `THERMAL_K0_runs` and `F14-cooling-ladder`
  locates the solver log by the **literal string `"log.solve"`**. Zero glob-fed log
  reads. **Two planted positives detected 2 of 2; a named-artifact negative control
  correctly did not fire** — so the zero is **evidence, not an absence**. **These are
  the instruments that apply rule 4, where a wrong last `Time =` would corrupt the
  *last time == endTime* conjunct — a wrong RESULT, not a wrong display. Those
  determinations are NOT corrupted.**
  **Scope stated by its author: three trees, three instrument classes, three glob
  patterns. NOT covering `run_one_*.sh`, watchers, pollers, `cases/`, or other
  teams.**
- **closure — CLEAN.** Grader reads `log.run` by name; last time taken from
  **numerically sorted time directories**.
- **Repository-wide sweep IN FLIGHT**, classifying hits by whether the value reaches
  a **verdict or a completion decision** versus a display.

---

## Amendment (2026-08-27) — A RESOURCE GATE DECLARES ITS SAMPLING DISCIPLINE, AND A FLOOR THAT THE BOX CANNOT MEET NEEDS ITS REFUSAL OUTCOME **REGISTERED**, NOT DECIDED ON THE NIGHT

**Appended, append-only; no line above changed number. Raised by dafoam via the
chief; verified here at source. Zero compute.**

### 1. THE MEASUREMENT

Two gates guard the **same resource at different levels, with different sampling
disciplines**, and neither declares which it uses:

- **`scripts/queue_runner.py:722-724`** — verified: `if mem < floor: log(…); continue`.
  **ONE sample of `MemAvailable`, then skip the entry.**
- **A driver's H5 gate** — a **45-sample / 60-second window** against a registered
  floor.

> **"`MemAvailable` is below the floor" is a DIFFERENT PROPOSITION at one sample than
> over sixty seconds.** `MemAvailable` moves as page cache is reclaimed and as peers
> allocate and free; **a single sample can hold a run on a transient that a window
> would not see, and a window can admit a run that a single sample would refuse.**
> Neither is wrong; **an undeclared choice between them is.**

### 2. THE CLAUSE

> **A resource gate DECLARES ITS SAMPLING DISCIPLINE on its face: single-sample, or
> windowed with its sample count and duration.** A gate whose discipline is
> undeclared cannot be reproduced, and its HOLD cannot be distinguished from a
> transient.
>
> **AND WHERE TWO GATES GUARD ONE RESOURCE AT DIFFERENT LEVELS, THE REGISTRATION
> NAMES WHICH GOVERNS.** Two gates that can disagree — the outer holding while the
> inner would pass — produce a contradiction **no reader of either record can see**,
> because each looks internally consistent.

### 3. ⚠ AND THE HARDER HALF: A FLOOR THE BOX CANNOT MEET

D8R registers a **18.0 GiB** floor; the box's `MemAvailable` is **16.0 GiB**. **The
gate can therefore never pass on this machine as configured.**

> **A registration whose floor sits above the box's capacity must REGISTER ITS
> REFUSAL OUTCOME — hold indefinitely, refuse as `BLOCKED`, or fail the rung — BEFORE
> COMPUTE. It must not be decided on the night.**

**THE GROUND IS RULE 2, NOT OPERATIONS.** An unregistered refusal outcome means the
*consequence* of the gate is chosen **after** its state is known, by whoever happens
to be awake. **That is precisely the defect the pre-registration freeze exists to
prevent, wearing operational clothes:** the gate was frozen and **what to do when it
fires was not.**

**AND IT IS THE `L-380` SHAPE:** faced with an unregistered outcome at 2 a.m., both
available answers — *hold and lose the night*, or *lower the floor and run* — are
defensible, **and the second silently rewrites a registered threshold after seeing
the box.** **Registering the outcome removes the choice, which is the point.**

**NOT RULED HERE: whether D8R should hold, be `BLOCKED`, or re-register a lower floor
is dafoam's, and lowering a registered floor after seeing the box would need its own
pre-compute amendment with the condition stated.** This clause says only that the
outcome must be **on the record before the gate fires.**

### 4. CONTROLS

| control | required |
| --- | --- |
| a gate declaring **single-sample** | HOLD reproduces on a re-read taken in the same second; a HOLD is **not** claimed to survive a window |
| a gate declaring a **window** | the window is **driven** — n samples over the stated duration, and a single unlucky sample must **not** decide it |
| a floor **above** the box's capacity | the registered refusal outcome is **present in the registration** and the gate's fire path **reaches it** |
| **two gates on one resource** | the record names **which governs**, and a case is driven where they **disagree** |

**The last row is the one that will be skipped.** Two gates that agree on every case
anyone tries are indistinguishable from one gate; **only the disagreeing case shows
which is in force.**
