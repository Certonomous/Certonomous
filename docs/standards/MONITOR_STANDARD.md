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
   nothing — the same distinction that separates the FPE *handler* from the
   FPE *trapping banner* in S1.
2. **It cannot ride on S5, because in the container it is not a warning.**
   OpenFOAM v2606 on the host prints `--> FOAM Warning : allowSystemOperations
   : Allowing user-supplied system call operations.`; the older build inside
   the DAFoam container prints `allowSystemOperations : Allowing user-supplied
   system call operations` bare, with no warning prefix
   (`demo-output/website/dafoam/probe_baseline_run1.log` line 33). S5 matches
   on `FOAM Warning` and would miss every containerized run — which is exactly
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

Adoption note, 2026-07-30: S8 is now implemented too, so the whole of both
approved monitor proposals is in force. Three things changed with it, each on
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
- Scope, added 2026-07-31 on measured evidence: S7 needs a `residual_target`
  and stays silent on any field that has already reached it. **Measured over
  every steady solver log the lab has archived, 106 of them: ungated, S7 fires
  on 68 and reaches FATAL on 65.** Every one of those runs completed and its
  results are on the record, so on this corpus the rule is calling roughly two
  thirds of the lab's healthy work divergent. Four tightenings were measured
  and none rescued it: requiring the residual level to stop improving (68 logs
  still fire), requiring the finding to persist a full window (40), measuring
  growth against a 200 iteration baseline (59), and raising the growth factor
  to four times (23). The cause is that a converged field sits flat with small
  noise, and the ratio of one noise envelope to the next is a coin toss that a
  run of thousands of iterations wins somewhere. The gate comes from the
  proposal's own words, which say the rule is about oscillation "around a
  stalled residual": a field below its target has converged, and its noise is
  not the subject. S6 has always been gated this way and does not
  false-positive.
- **Recorded weakness, not hidden.** The gate is reasoning from the proposal's
  wording plus S6's measured behaviour; it is not a measurement of its own,
  because the archived logs do not record the residual target each run was
  aiming for and the corpus cannot be replayed with the gate in place. S7 is
  the weakest rule in this standard. It is filed for the owner as a decision
  rather than quietly kept: the alternative is to withdraw the branch outright,
  and the evidence for keeping it is a knowledge base fact rather than a run.
- Status: implemented (`detect_oscillatory_divergence` in
  `sdk/chief_engineer/log_signatures.py`; runs on every residual line of a
  steady run in `LogMonitor` once a `residual_target` is given and while the
  field is above it, raised once per episode and again only on escalation to
  FATAL).

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
  ledger holds in that band was invisible to it. The entry point now takes its
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

## 3. Standing rules for any monitor rule

1. A rule states its detection pattern, severity, and action before it ships;
   a rule that only prints is not a rule.
2. Repeated conditions are one finding, not hundreds: report a few instances
   per step, count the rest silently (the suppression discipline already in
   `LogMonitor`).
3. Banner text is never matched; only handlers and measured values are. A line
   the solver prints only when a condition holds is a measured value, not a
   banner — that is the test S11 passes and the FPE trapping banner fails.
4. New rules enter through the innovation path (see
   `docs/standards/INNOVATION_STANDARD.md`): proposal, offline evidence
   against archived logs, then adoption.
5. A severity that is not about the numbers says so. It does not borrow FLAG
   or FATAL to be noticed, and it is not allowed to disappear into "nothing
   fatal" for being unable to. S11 is the first of these.

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
- Signature detectors for S6, S7, and S9,
  `sdk/chief_engineer/log_signatures.py`, with tests in
  `sdk/tests/test_log_signatures.py` (including an integration test against
  a fixture slice of real ledger rows,
  `sdk/tests/fixtures/ledger_slice.jsonl`).
