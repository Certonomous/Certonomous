# Model-form band — converged cells only

Generated 2026-08-08T23:55:14Z by `sdk/scripts/model_form_batch.py --band`. Design and pre-registration: `MODEL_FORM_BATCH_DESIGN.md`.

36 of 36 designed cells have run, 101.50 core-min spent.

The band is the min/max across CONVERGED members of a group. An unconverged cell is excluded and named -- the NASA hump lesson: the band that failed to contain the experiment was the band that still had an unconverged member in it.

## B_re1p2e7 (0 converged, 4 excluded, 11.81 core-min)


Excluded from the band:
  - SpalartAllmaras: residualControl not met (stopped on the backstop)
  - kEpsilon: residualControl not met (stopped on the backstop)
  - kOmegaSST: residualControl not met (stopped on the backstop)
  - realizableKE: residualControl not met (stopped on the backstop)

## B_re3e6 (0 converged, 4 excluded, 9.19 core-min)


Excluded from the band:
  - SpalartAllmaras: residualControl not met (stopped on the backstop)
  - kEpsilon: residualControl not met (stopped on the backstop)
  - kOmegaSST: residualControl not met (stopped on the backstop)
  - realizableKE: residualControl not met (stopped on the backstop)

## H_re10595 (2 converged, 2 excluded, 57.03 core-min)

- **x_R_over_h: 3.57741 to 7.64724** (spread 4.07, 72.52% of the mean; low kEpsilon, high kOmegaSST)
  - kEpsilon: 3.57741
  - kOmegaSST: 7.64724
  - reference literature band midpoint 4.455 (PRIMARY containment test): 4.455 — **CONTAINED** by this band
  - reference Rapp & Manhart 2011 (exp): 4.21 — **CONTAINED** by this band
  - reference Froehlich et al. 2005 (LES, 4.6-4.7 midpoint): 4.65 — **CONTAINED** by this band
  - reference Breuer et al. 2009 (LES): 4.69 — **CONTAINED** by this band
- **x_S_over_h: 0.260358 to 0.423019** (spread 0.1627, 47.61% of the mean; low kOmegaSST, high kEpsilon)
  - kEpsilon: 0.423019
  - kOmegaSST: 0.260358

Excluded from the band:
  - SpalartAllmaras: no steady bubble: 0 skin-friction sign changes (a steady separation bubble has exactly 2, separation first)
  - realizableKE: residualControl not met (stopped on the backstop); no steady bubble: 0 skin-friction sign changes (a steady separation bubble has exactly 2, separation first)

## N_a0 (0 converged, 4 excluded, 6.68 core-min)

**Mesh-gate exemption on this group (R12):** Mesh Standard hard gate EXEMPT under R12, docs/charters/SUPERVISOR_RULINGS.md (ruled 2026-08-07): max non-orthogonality 85.70 deg vs the 70 deg hard gate, on the reference community's own grid -- NASA Langley Turbulence Modeling Resource NACA 0012 C-grid, n0012_113-33.p3dfmt as distributed (turbmodels.larc.nasa.gov, mirror tmbwg.github.io/turbmodels) -- the verification community's canonical grid family, the same family whose 897x257 member carries the published CFL3D references this batch compares against. Scope: model-form banding only; physics gates and credential verdicts still require compliant meshes and this exemption never travels to them.


Excluded from the band:
  - SpalartAllmaras: residualControl not met (stopped on the backstop); workflow settle/extraction rule fired (not this batch's gate): coarse: Cd still moving (9.79e-06 peak-to-peak over the last 50 iterations); not defensible as steady
  - kEpsilon: residualControl not met (stopped on the backstop); workflow settle/extraction rule fired (not this batch's gate): coarse: Cd still moving (2.52e-07 peak-to-peak over the last 50 iterations); not defensible as steady
  - kOmegaSST: residualControl not met (stopped on the backstop); workflow settle/extraction rule fired (not this batch's gate): coarse: Cd still moving (5.95e-05 peak-to-peak over the last 50 iterations); not defensible as steady
  - realizableKE: residualControl not met (stopped on the backstop); workflow settle/extraction rule fired (not this batch's gate): coarse: Cd still moving (0.000849 peak-to-peak over the last 50 iterations); not defensible as steady

## N_a10 (3 converged, 1 excluded, 4.89 core-min)

**Mesh-gate exemption on this group (R12):** Mesh Standard hard gate EXEMPT under R12, docs/charters/SUPERVISOR_RULINGS.md (ruled 2026-08-07): max non-orthogonality 85.70 deg vs the 70 deg hard gate, on the reference community's own grid -- NASA Langley Turbulence Modeling Resource NACA 0012 C-grid, n0012_113-33.p3dfmt as distributed (turbmodels.larc.nasa.gov, mirror tmbwg.github.io/turbmodels) -- the verification community's canonical grid family, the same family whose 897x257 member carries the published CFL3D references this batch compares against. Scope: model-form banding only; physics gates and credential verdicts still require compliant meshes and this exemption never travels to them.

- **Cd: 0.00449517 to 0.0161921** (spread 0.0117, 100.51% of the mean; low kOmegaSST, high SpalartAllmaras)
  - SpalartAllmaras: 0.0161921
  - kEpsilon: 0.0142268
  - kOmegaSST: 0.00449517
  - reference CFL3D SST (897x257): 0.0123621 — **CONTAINED** by this band
- **Cl: 1.02905 to 1.11643** (spread 0.08738, 8.13% of the mean; low SpalartAllmaras, high kOmegaSST)
  - SpalartAllmaras: 1.02905
  - kEpsilon: 1.0802
  - kOmegaSST: 1.11643
  - reference CFL3D SST (897x257): 1.07781 — **CONTAINED** by this band

Excluded from the band:
  - realizableKE: residualControl not met (stopped on the backstop); workflow settle/extraction rule fired (not this batch's gate): coarse: Cd still moving (0.13 peak-to-peak over the last 50 iterations); not defensible as steady

## N_a15 (0 converged, 4 excluded, 6.03 core-min)

**Mesh-gate exemption on this group (R12):** Mesh Standard hard gate EXEMPT under R12, docs/charters/SUPERVISOR_RULINGS.md (ruled 2026-08-07): max non-orthogonality 85.70 deg vs the 70 deg hard gate, on the reference community's own grid -- NASA Langley Turbulence Modeling Resource NACA 0012 C-grid, n0012_113-33.p3dfmt as distributed (turbmodels.larc.nasa.gov, mirror tmbwg.github.io/turbmodels) -- the verification community's canonical grid family, the same family whose 897x257 member carries the published CFL3D references this batch compares against. Scope: model-form banding only; physics gates and credential verdicts still require compliant meshes and this exemption never travels to them.


Excluded from the band:
  - SpalartAllmaras: residualControl not met (stopped on the backstop); workflow settle/extraction rule fired (not this batch's gate): coarse: Cd still moving (1.5e-05 peak-to-peak over the last 50 iterations); not defensible as steady
  - kEpsilon: residualControl not met (stopped on the backstop); workflow settle/extraction rule fired (not this batch's gate): coarse: Cd still moving (2.3e-05 peak-to-peak over the last 50 iterations); not defensible as steady
  - kOmegaSST: residualControl not met (stopped on the backstop); workflow settle/extraction rule fired (not this batch's gate): coarse: Cd still moving (8.11e-05 peak-to-peak over the last 50 iterations); not defensible as steady
  - realizableKE: residualControl not met (stopped on the backstop); workflow settle/extraction rule fired (not this batch's gate): coarse: Cd still moving (0.17 peak-to-peak over the last 50 iterations); not defensible as steady

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

