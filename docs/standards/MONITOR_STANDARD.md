# Certonomous Monitor Standard

Version 1.0, dated 2026-07-25. Produced by the overnight reading program (R1).
Names every solver-log signature the lab's monitor recognizes or should
recognize, with a detection rule, a severity, and a prescribed action. Derived
from the lab's own logs: the mega-batch ledger
(`demo-output/website/mega-batch/ledger.jsonl`, 39442 rows examined), the
mission logs and learned lessons under
`sdk/chief-engineer-runs/mission-state/`, the TMR and motorcycle run logs, and
the monitor implementation in `sdk/chief_engineer/head_engineer.py`
(`LogMonitor`).

Severities: FATAL (stop and investigate, the run is not evidence), FLAG
(continue, mark the record, cap trust until resolved), WATCH (continue,
count, report in the debrief).

## 1. Signatures the monitor already catches

### S1. Floating point exception

- Detection: `Foam::sigFpe::sigHandler` or a line starting `Floating point
  exception`. Never the log banner: every OpenFOAM log prints a trapping
  banner (`trapFpe: Floating point exception trapping enabled`), and matching
  it reads every healthy run as fatal. The monitor matches the handler, not
  the banner. Evidence: motorcycle benchmark logs, knowledge base fact 7.
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

## 2. Signatures the logs show the monitor misses

Each of these is filed as a proposal in the agenda inbox; the monitor code is
owned elsewhere and is not edited by this program.

Adoption note, 2026-07-25: the owner approved the agenda proposals, and S6,
S7, and S9 are implemented as pure detection functions in
`sdk/chief_engineer/log_signatures.py`, wired into `LogMonitor` in
`sdk/chief_engineer/head_engineer.py` (series hooks for S6/S7, a
`check_wall_time` hook for S9). Each signature below carries a Status line.

Adoption note, 2026-07-30: S8 is now implemented too, so the whole of both
approved monitor proposals is in force. Three things changed with it, each on
measured evidence and each recorded in the relevant section below: S8 carries a
tolerance because a strict comparison would have called every healthy transient
run in the lab an excursion; S6 and S7 are scoped to steady solves because they
fired on every healthy transient run; and the S9 flag threshold was corrected
from 20x back to the 10x the owner actually approved.

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
- Scope: steady solves only. See the scoping note under S7.
- Status: implemented (`detect_residual_stall` in
  `sdk/chief_engineer/log_signatures.py`; raised once per field per episode
  by `LogMonitor` when constructed with `residual_target`, and gated on the
  iteration cap approaching when `iteration_cap` is given).

### S7. Oscillatory divergence (same proposal)

- Evidence: the same past-regime family, oscillation amplitude growing rather
  than decaying around a stalled residual.
- Detection rule: alternating-sign residual changes with growing envelope
  over the last 50 iterations.
- Severity: FLAG, escalating to FATAL when the envelope doubles. Action: stop
  the steady solve; the prescribed fix is the unsteady track, not more
  iterations.
- Scope, added 2026-07-30 on measured evidence: S6 and S7 are steady-solve
  rules and are switched off for the rest of a run as soon as the monitor sees
  a `Courant Number` line, which is a transient solver's signature. In a
  transient run the residual series restarts at every time step and the outer
  correctors drive it high and low in turn, so alternation with a moving
  envelope is the time stepping itself, not divergence. Measured on the lab's
  four archived transient runs: S7 fired 5, 5, 6 and 9 times on runs that all
  completed healthily, every one of them a false positive. The transient
  equivalent of these rules is S8, and it now exists.
- Status: implemented (`detect_oscillatory_divergence` in
  `sdk/chief_engineer/log_signatures.py`; runs on every residual line of a
  steady run in `LogMonitor`, raised once per episode and again only on
  escalation to FATAL).

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
- **Known weakness, recorded not hidden.** The rule is purely relative, so a
  solver whose p99 is 3 milliseconds gets a threshold of 30 milliseconds. Five
  reduced-order rows of 0.30 to 0.43 s are assessed FATAL on that basis. The
  detection is arguably right (those runs really were hundreds of times slower
  than their own baseline, which is what host contention looks like) but the
  severity is out of proportion to a third of a second. An absolute floor
  would fix it and is deliberately NOT added here, because no such floor was
  in the approved proposal and inventing a threshold is how a rule stops
  meaning what it says. Filed as an observation for the owner.

## 3. Standing rules for any monitor rule

1. A rule states its detection pattern, severity, and action before it ships;
   a rule that only prints is not a rule.
2. Repeated conditions are one finding, not hundreds: report a few instances
   per step, count the rest silently (the suppression discipline already in
   `LogMonitor`).
3. Banner text is never matched; only handlers and measured values are.
4. New rules enter through the innovation path (see
   `docs/standards/INNOVATION_STANDARD.md`): proposal, offline evidence
   against archived logs, then adoption.

## Sources

- Certonomous mega-batch ledger and runner logs, examined 2026-07-25.
- Certonomous mission lessons, `sdk/chief-engineer-runs/mission-state/lessons`.
- Certonomous Numericist knowledge base, `docs/NUMERICS_KNOWLEDGE.md`,
  validated facts 3, 4, and 7.
- LogMonitor implementation and tests, `sdk/chief_engineer/head_engineer.py`,
  `sdk/tests/test_head_engineer.py`.
- Signature detectors for S6, S7, and S9,
  `sdk/chief_engineer/log_signatures.py`, with tests in
  `sdk/tests/test_log_signatures.py` (including an integration test against
  a fixture slice of real ledger rows,
  `sdk/tests/fixtures/ledger_slice.jsonl`).
