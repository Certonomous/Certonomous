# Model-form band — converged cells only

Generated 2026-08-07T20:07:46Z by `sdk/scripts/model_form_batch.py --band`. Design and pre-registration: `MODEL_FORM_BATCH_DESIGN.md`.

20 of 32 designed cells have run, 17.43 core-min spent.

The band is the min/max across CONVERGED members of a group. An unconverged cell is excluded and named -- the NASA hump lesson: the band that failed to contain the experiment was the band that still had an unconverged member in it.

## B_re1p2e7 (0 converged, 4 excluded, 2.35 core-min)


Excluded from the band:
  - SpalartAllmaras: residualControl not met (stopped on the backstop)
  - kEpsilon: solver exit code -8; S1 floating point exception; residualControl not met (stopped on the backstop); QoI missing from the coefficient history
  - kOmegaSST: solver exit code -8; S1 floating point exception; residualControl not met (stopped on the backstop); QoI missing from the coefficient history
  - realizableKE: solver exit code -8; S1 floating point exception; residualControl not met (stopped on the backstop); QoI missing from the coefficient history

## B_re3e6 (0 converged, 4 excluded, 9.19 core-min)


Excluded from the band:
  - SpalartAllmaras: residualControl not met (stopped on the backstop)
  - kEpsilon: residualControl not met (stopped on the backstop)
  - kOmegaSST: residualControl not met (stopped on the backstop)
  - realizableKE: residualControl not met (stopped on the backstop)

## P_re1e6 (4 converged, 0 excluded, 1.04 core-min)

- **Cd: 0.000935082 to 0.006846** (spread 0.005911, 156.46% of the mean; low realizableKE, high kEpsilon)
  - SpalartAllmaras: 0.00368046
  - kEpsilon: 0.006846
  - kOmegaSST: 0.00364991
  - realizableKE: 0.000935082

## P_re2e7 (2 converged, 2 excluded, 3.19 core-min)

- **Cd: 0.00220088 to 0.00385085** (spread 0.00165, 54.53% of the mean; low kOmegaSST, high kEpsilon)
  - kEpsilon: 0.00385085
  - kOmegaSST: 0.00220088

Excluded from the band:
  - SpalartAllmaras: residualControl not met (stopped on the backstop)
  - realizableKE: residualControl not met (stopped on the backstop)

## P_re5e6 (3 converged, 1 excluded, 1.65 core-min)

- **Cd: 0.00278117 to 0.00500082** (spread 0.00222, 62.42% of the mean; low kOmegaSST, high kEpsilon)
  - SpalartAllmaras: 0.00288529
  - kEpsilon: 0.00500082
  - kOmegaSST: 0.00278117
  - reference CFL3D SST-V (3264 cells): 0.00278507 — **CONTAINED** by this band
  - reference FUN3D SST-V (3264 cells): 0.00267868 — **NOT contained** by this band

Excluded from the band:
  - realizableKE: residualControl not met (stopped on the backstop)

