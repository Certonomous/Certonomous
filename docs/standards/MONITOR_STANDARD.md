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

### S7. Oscillatory divergence (same proposal)

- Evidence: the same past-regime family, oscillation amplitude growing rather
  than decaying around a stalled residual.
- Detection rule: alternating-sign residual changes with growing envelope
  over the last 50 iterations.
- Severity: FLAG, escalating to FATAL when the envelope doubles. Action: stop
  the steady solve; the prescribed fix is the unsteady track, not more
  iterations.

### S8. Courant excursion (same proposal, forward-looking)

- Evidence: no transient excursion exists in the ledger yet because the fleet
  runs steady solves; the rule is written before the unsteady track lands so
  the first transient run is born monitored.
- Detection rule: `Courant Number max` exceeding the case limit, or growing
  monotonically across 20 consecutive time steps.
- Severity: FLAG at the limit, FATAL on monotonic growth with the time step
  fixed. Action: reduce the time step or enable adaptive stepping; a transient
  result computed above its Courant limit is not evidence.

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
