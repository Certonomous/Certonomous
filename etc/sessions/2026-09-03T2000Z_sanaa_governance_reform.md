# SANAA-DIRECT — governance reform: reported-not-gated default, budgeted governance, deadline monitor, physics taxonomy (2026-09-03, ~20:00Z)

## Sanaa's words, verbatim

> effective immediately: Default is "reported, not gated"
> Every standard, lesson, and grader check is classified as gating or
> reporting. Gating requires a stated reason of the form "without this, the
> verdict on result X cannot be trusted." Anything without that reason is
> reporting.
> Reporting checks run, log, and attach to the certificate; they never
> block a solve from starting, a mesh from being used, or a hand-off from
> happening.
> Existing rules are re-classified once, by their owning team, with the
> reason recorded. Anything that can't produce the reason drops to
> reporting. This is a one-pass audit, not a new cycle.
> 2. Rules cannot create work for other teams without a cost
> A rule that requires a backfill, migration, or re-registration must state
> its compute/effort cost and the result it protects before it's adopted.
> If the protected result isn't on any team's current line, the rule is
> adopted as "forward-only" (applies to new entries) and the backfill is
> not scheduled.
> No instrument is built to measure another instrument's reach unless the
> first instrument has already changed a verdict at least once.
> 3. Governance is budgeted, not free
> Each team gets a fixed share of its cycle for rules, lessons, standards,
> and grader work (e.g. one commit in five, or one slot per cycle). Beyond
> that, governance items queue behind physics work.
> Digests lead with a physics result or the sentence "no physics result
> this cycle." Governance goes below, count-only. Repeated "no result"
> cycles from a team are the signal, not a report of how many rules landed.
> Petitions, rulings, and charter amendments require a blocked result to
> name. No result blocked → no petition; the team decides locally and
> records the decision as a lesson. 2. When something is blocked bc its
> waiting for my approval, and i dont answer, take that as a yes and
> proceed.Auto-stop / monitor as a general fleet capability, all solver
> modes, all runs including detached: at deadline, classify the
> max-over-equations residual as descending / plateaued-or-oscillating /
> diverging; extend bounded and booked, stop gracefully as
> "non-convergent, reported not gated," or kill, respectively. Sidecar
> attached to the log, not the process. Same values everywhere unless a
> team states why its solver needs different ones.
> Justification for classifying rather than killing: a deadline is a cost
> estimate, and an estimate that turns out wrong is information about cost;
> killing discards exactly the data (residual trajectory) that tells you
> whether the estimate or the solver was the problem.
> 7. Immediate applications, in this order: board migration approved and
> shared-index deletions frozen until it lands; skewness quarantine
> reclassified to reporting; "reported, not gated" adopted as the
> standard's default mode; coverage ratios forward-only, unreported;
> UNREACHABLE → REFUSE only after the monitor has run one full sweep
> fleet-wide; pin backfill forward-only; scripts to the team that built
> the enforcer.. In general governance is importance, but so is running.
> Running cases cannot be blocked bc of governance.Classify physics items
> into three kinds, each with its own path:
> Blocking physics fixes — a result can't be produced or trusted without
> them (wrong patch identity on a mesh, a residual print that isn't the
> max over equations, a boundary condition set wrong, a linear solver
> failing). These jump every queue, need no petition, and the team fixes
> them and records a lesson afterward, not before.
> Physics findings — a measured fact about the problem, not a defect (an
> arm that plateaus at a tolerance, a y+ commitment that fails, a
> model-form band that has to widen). These are reported with the evidence
> and land as "reported, not gated" on the certificate. They open a
> follow-up question; they never trigger a rule change on their own.

## Context (chief's reading, not her words)

- Answers the pending desk items in one stroke: board migration APPROVED
  (shared-index deletions frozen as a hazard class until it lands);
  skewness quarantine → reporting; reported-not-gated is the standard's
  default mode; coverage ratios forward-only and unreported;
  UNREACHABLE→REFUSE waits for one full fleet-wide monitor sweep; pin
  backfill forward-only; the board scripts go to cfd (the enforcer team).
- Silence-is-yes GENERALIZED by her: items blocked awaiting her approval
  proceed if she does not answer. (Rule 7 SUBMISSIONS PARKED and rule 8
  privacy are not approval-blocked items and are untouched.)
- The auto-stop patch's scope grows into the fleet monitor capability:
  at-deadline residual-trajectory classification (descending → extend
  bounded and booked; plateaued/oscillating → stop gracefully as
  non-convergent, reported not gated; diverging → kill), sidecar on the
  log, one value set fleet-wide unless a solver-specific reason is stated.
- Physics taxonomy: BLOCKING PHYSICS FIXES (e.g. the symmetry→empty patch
  defect, the residual-print-not-max defect) jump every queue, no
  petition, lesson AFTER the fix; PHYSICS FINDINGS are
  reported-not-gated and never trigger rule changes alone.
- Verdict integrity unchanged: gating survives wherever its owner states
  the "without this, the verdict on X cannot be trusted" reason —
  rule 2/4/5 gates on graded verdicts are exactly such reasons.
