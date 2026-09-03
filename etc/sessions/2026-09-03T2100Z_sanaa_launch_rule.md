# SANAA-DIRECT — pre-registration predicts, monitor watches, grader judges afterward (2026-09-03, ~21:00Z)

## Sanaa's words, verbatim

> additionally : Rule as I'd state it: A pre-registration mismatch never
> prevents a launch. It's recorded as a prediction, the run launches under
> the monitor, and the outcome is compared to the prediction on the
> certificate. Pre-registration predicts; the monitor watches; the grader
> judges afterward.
> What can block a run before it starts (the full list, so the rule covers
> them all):
> Cost / budget — estimated core-hours or wall time above the envelope or
> the arm's cap.
> Model admissibility — turbulence model, wall treatment, or closure not
> on the approved list for that regime (e.g. k-ω SST at a Mach where
> transonic effects aren't covered).
> Mesh quality gates — skewness, non-orthogonality, aspect ratio, y+
> commitment failing the standard.
> Grid provenance — committee or imported grids, single-patch imports,
> unregistered mesh families.
> Numerical settings — tolerance tighter than the standard allows,
> scheme/order not pre-approved, time-step or CFL outside the registered
> range.
> Geometry / setup completeness — assumed values not filled (freestream,
> AoA, reference area), surface confirmation pending, prompt-vs-geometry
> mismatch.
> Verification state — mesh-convergence ladder not done, gradient not yet
> verified for adjoint runs, baseline not qualified.
> Concurrency / resource gates — box busy, worker headroom, license or
> memory limits.
> Freeze or procedural state — registration not frozen, pin missing,
> lesson not filed.
> How each is handled under the new rule:
> Everything in the list except the last two categories: record the
> mismatch as a prediction ("cost will exceed cap by ~X," "y+ will miss
> target," "model outside validated regime — expect band widening"),
> launch, monitor, then write predicted vs actual on the certificate. That
> comparison is the payoff: it tells you whether the pre-registration
> standards are calibrated or just conservative.
> Resource gates (box busy, memory): these are real physical limits, not
> predictions — queue, don't launch. But queueing is not blocking; the run
> stays scheduled.
> Procedural / freeze state: record and launch. A missing pin or unfiled
> lesson is bookkeeping and can be completed while the solve runs.
> The one hard limit that stays: a fleet-wide safety ceiling on any single
> run (e.g. 3× its registered cost cap, or the box's remaining budget,
> whichever is smaller). Below that, the monitor manages extensions as we
> defined; at the ceiling the monitor stops the run gracefully regardless
> of residual trend. Justification: the T12 lesson is that the launcher's
> own flag never fired, so something must be structurally guaranteed to
> stop a run — but that something should be a ceiling far above the
> estimate, not the estimate itself. The estimate is a prediction to be
> tested; the ceiling is protection against the box being eaten.
> The grader is unchanged, and that matters: the frozen grader still
> judges against the pre-registration. A run that launched over its
> predicted cost and came in at 2× still gets "cost cap exceeded" on its
> certificate. The rule changes when the gate applies — after the fact, on
> evidence — not whether it applies. Refusing to widen the gate was right;
> refusing to launch was the expensive part.
> What you gain: a calibration dataset for every pre-registration
> standard. If runs flagged "will exceed cap" routinely come in under it,
> the caps are too tight; if y+ predictions never miss, the quality gate
> can drop to reporting. The standards get corrected by data instead of by
> petition.
> Exceptions where "launch anyway" is wrong: a setup that's physically
> ill-posed (no outlet, inconsistent boundary conditions, geometry with
> leaks) will diverge and teach nothing — that's a blocking physics fix,
> not a pre-registration mismatch. And a run that would exceed the box's
> tototal remaining budget for the cycle is a resource gate, not a
> prediction.

## Context (chief's reading, not her words)

- Launch discipline inverts for seven of the nine blocker categories:
  predict-launch-monitor-grade. Resource gates queue (not block); the
  ill-posed-setup class stays a blocking physics fix; the cycle budget is
  a resource gate.
- ONE hard structural stop survives: the fleet safety ceiling — min(3x
  registered cap, remaining box budget) — enforced by the monitor with a
  graceful stop regardless of trend. cfd implements in the runner/monitor.
- Rule 2 is UNCHANGED in substance: registrations still freeze before
  compute (they are the predictions being tested); what changes is that a
  mismatch is recorded and launched, never refused. The frozen grader
  still applies every gate AFTER, on evidence.
- Reconciliation required at source (verification + cfd): §2s's
  choke-point wording says the daemon "refuses to GRADE" a sha-mismatched
  run — her original wording — while the built enforcer refuses at
  LAUNCH. Under this ruling the launch-side refusal converts to
  record-as-prediction (MISMATCH recorded, run launches, grader refuses
  the GRADING afterward per the unchanged rule). The D6 referral's two
  states are resolved the same way: record and launch, judged after.
- The payoff is a standing calibration dataset; standards corrected by
  data instead of petition.
