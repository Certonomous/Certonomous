# UQ quantification track (Q1-Q5) — status

Branch `feat/uq-quantification` (worktree ct-uq). All numbers below are
measured; nothing is invented. Studies live in
`models/curriculum/uq-studies/<body>.json`; the overnight batch runs detached
(`uq_batch.log` in the worktree root; relaunch with
`python sdk/scripts/run_uq_studies.py all` — it resumes from checkpoints).

## Machinery (done, 186 tests green)

- `sdk/chief_engineer/uq.py`: setup fingerprints (Q4), 3-mesh ladder math
  (observed order + GCI Fs=1.25, Eca-Hoekstra conservative fallback with the
  mandated sentence), spread estimates (never a bound), RSS combination (Q3),
  fingerprinted study records with pending-not-stale lookup.
- `sdk/scripts/run_uq_studies.py`: the batch runner — unfamiliar-path ladders
  (refinement 1/2/3 via the real geometry-study chain, per-rung cache
  clearing), motorBike tutorial ladder (snappy levels 3-4/4-5/5-6), closure
  trios on the cached fine mesh (kOmegaSST / kEpsilon / SpalartAllmaras with
  derived epsilon/nuTilda fields), airliner anchors, valve quadrature +
  correlation family. Checkpoints per rung.
- Workflows (geometry study, aircraft, valve) pull studies via
  `uq.channels_for(body, fingerprint)`: matched studies fill the numerical and
  model channels with method labels and provenance; mismatch renders
  "study pending"; the headline CI is the RSS combined expanded uncertainty.
  Certificates inherit the same channel values (v2 renders the table).

## Studies completed (measured)

- **aortic-valve**: numerical = phase-quadrature ladder k=3/5/9, band 81 Pa
  (k=3 value 1327 Pa reproduces the act's deterministic objective); model =
  correlation-family spread 105 Pa over sharp-orifice discharge coefficients
  (ISO 5167 0.60, Idelchik 0.61, classic 0.62, upper literature 0.65),
  unmodeled-physics list retained. End-to-end verified: input 421 /
  numerical 81 / model 105 -> combined 441 Pa (95%).
- **airliner-wing**: model = "model-form vs solver anchors", 6 real VSPAERO
  finalist anchors, max |dL/D (screen - solved)| = 1.60 (members stored
  per-planform). Feeds the aircraft act's model channel + combined headline.

## In flight (overnight batch, sequenced per the orders)

- naca4412_wing ladder (rung r=1 done: 67,826 cells, Cd 0.0289, 1.7 min;
  r=2, r=3 running) then closure trio.
- motorBike tutorial ladder (3-4 / 4-5 / 5-6) then closure trio.
- B-52 ladder + closures after.

The batch checkpoints; whatever has not finished by morning resumes with the
same command and the studies land in place with no further wiring needed.

## Honesty rails (tested in sdk/tests/test_uq.py)

Method labels mandatory; inter-closure spread labeled screening estimate,
never a bound; channels cannot upgrade a chip to VALIDATED; non-monotone
ladders report "refinement study inconclusive: non-monotone convergence" with
the factor-3 fallback band.
