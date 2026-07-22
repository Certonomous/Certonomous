# Epistemic uncertainty quantification

Certonomous's chief does not just report winning numbers — it reports how much it
trusts them. Every mission ends with a per-metric verdict in the chief's own
voice:

> Uncertainty assessment for c2-stab-000 from 31 evaluated designs:
> Here I am sure: L_D = 16.7 ± 0.31 (1.8%, 95% CI [16.09, 17.3], n=31).
> Here I am fairly sure: static_margin = 0.426 ± 0.017 (4.0%, …).
> Evidence is thin along wing_span, wing_taper — sampling there would
> tighten these bounds.

## What is being quantified

**Epistemic uncertainty**: what the mission's own evidence does not pin down.
Every mission evaluates an ensemble of designs with real solvers. The layer
(`sdk/chief_engineer/uncertainty.py`) treats those (design → metric) pairs as
training data for a Gaussian-process surrogate per metric and measures the
calibrated posterior spread in the neighborhood of the assessed design. Dense,
consistent evidence around the winner → small spread → "I am sure". Sparse or
far-away evidence → large spread → "I am NOT sure", with the numbers attached
either way.

This is *not* solver noise (the deterministic backends have essentially none)
and *not* model-form error of the solver itself (e.g. a vortex-lattice code's
physics limits); see the roadmap below.

## Method

1. **Evidence pool.** Every successful evaluation in the mission — across all
   stages and cycles, baseline included — contributes its design point and
   metrics. Designs are normalized to the unit box using adapter-declared
   parameter bounds (observed extents as fallback); non-varying dimensions are
   dropped and duplicate points deduplicated.
2. **GP surrogate per metric.** Squared-exponential kernel; signal variance
   from the evidence variance; lengthscale = 3× the median nearest-neighbor
   spacing, so the surrogate stays correlated across neighboring samples but
   never confidently bridges unexplored gaps.
3. **Leave-one-out calibration.** LOO residual z-scores inflate the posterior
   standard deviation when the surrogate is overconfident about its own
   evidence (inflation factor ≥ 1, computed in closed form from the Cholesky
   factor).
4. **Local probing.** The reported σ is the RMS posterior standard deviation
   over axis-aligned probes 10% of the design box away from the assessed
   design — the region the chief's claim is actually about.
5. **Verdicts.** Relative spread < 2% → `sure`; < 10% → `moderately-sure`;
   otherwise `not-sure`. Fewer than 4 distinct designs → the chief says so
   plainly (`insufficient-evidence`) instead of inventing a number.
6. **Thin directions.** Parameters where the assessed design sits at the edge
   of the sampled range, or with fewer than 3 distinct sampled values, are
   called out as under-explored.

The implementation is pure standard library (own Cholesky, ~350 lines),
deterministic, and inspectable — matching the rest of the chief kernel.

## Where it surfaces

- `MissionOutcome.uncertainty` — `UncertaintyReport` for the mission winner;
  serialized under `"uncertainty"` in `as_dict()`.
- `CycleOutcome.uncertainty` — the same assessment for each cycle's
  challenger.
- Events: `chief.uncertainty` (per cycle) and `uncertainty.assessed` (final),
  plus `uncertainty_narration` inside `mission.completed`. Any control room,
  HTTP consumer, or MCP client sees them without new endpoints.

Run `python -m unittest tests.test_uncertainty` from `sdk/` for the behavioral
contract: dense evidence reads sure, sparse-distant evidence reads not-sure,
spread grows away from evidence, tiny evidence pools refuse to quantify.

## Roadmap

- **Reference papers**: `docs/papers/` is reserved for the UQ literature this
  layer should track; the folder is currently empty — add the PDFs and the
  method notes here can be tied to them.
- **Solver model-form error**: cross-fidelity disagreement (e.g. VSPAERO
  panel-method vs higher-fidelity references) as a second uncertainty channel.
- **Acquisition**: let the chief spend its next cycle's worker budget where
  the posterior spread is largest (the thin directions already point there).
- **Control-room visualization**: confidence bands on the live metric plots,
  in the style of the VortexAI "uncertainty overlay" concept.
