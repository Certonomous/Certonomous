# F6b prediction, written BEFORE any solve (P1)

Date: 2026-07-29. Case chosen: `PH_Breuer` from the benchmark clone
(`/home/ubuntu/closure-challenge-benchmark/data/PH_Breuer/`), confirmed by
inspection to be the classic ERCOFTAC/Breuer periodic-hill geometry:
domain `Lx=9h`, `Ly=3.035h` (h=1 nondimensional hill height), cyclic
streamwise BC, `nu=9.438414346389807e-05` with an explicit code comment
`Re_H=10595`, `Ubar=0.72` enforced via a `meanVelocityForce` fvOption. This
matches Breuer, Peller, Rapp & Manhart (2009), the standard high-Re
periodic-hill case in the Fröhlich/Breuer lineage that ERCOFTAC and NASA TMR
both host. Sampling stations `x0..x8` at `x/h = 0,1,2,...,8` are the
standard stations used in that literature.

Turbulence model: shipped case declares `kOmegaSST` — no custom library
substitution needed this time (unlike F6a/F6c, no `AugmentedkOmegaSST`).
`controlDict` still requests `libfrozenIncompressibleTurbulenceModels.so`,
not present on this box; expect this is only needed for a frozen/`tauij`
post-processing utility, not the forward `kOmegaSST` solve itself — to be
confirmed at preflight, and dropped if simpleFoam does not need it.

## Prediction, before running anything

- **Feasibility**: expect the case to run clean on stock `kOmegaSST` — the
  mesh, BCs and fvOptions are already a complete, previously-converged
  OpenFOAM v7 case (shipped `log.run` shows a full 10000-iteration run to
  completion), so no structural setup problem is expected on this
  well-formed case.
- **Physics**: expect a separation bubble immediately downstream of the
  hill crest (near `x/h≈0-1`) and reattachment before the next hill
  (somewhere in `x/h≈4-6`), i.e. a single recirculation zone spanning
  roughly half the domain — this is the textbook periodic-hill flow
  topology at this Reynolds number.
- **Gate, expected DIRECTION of model-form error (to be checked against a
  citable source, not asserted from memory)**: general RANS/periodic-hill
  literature (Fröhlich et al. 2005; Temmerman et al. 2003) documents that
  linear-eddy-viscosity models (standard k-epsilon particularly, k-omega
  SST to a lesser degree) tend to UNDER-predict the recirculation length
  on periodic hills relative to LES/DNS — i.e. reattach TOO EARLY — which
  would be the OPPOSITE sign of F6a's NASA-hump result (where SST
  over-predicted the bubble by +14%). This is a recollection, not a
  citation; the gate report must fetch and cite an actual published number
  (Breuer LES, and if available a published RANS/SST periodic-hill result)
  before asserting a sign or magnitude. If the fetched literature
  disagrees with this recollection, the fetched literature wins and this
  paragraph is superseded, not edited after the fact.

This file is written before any preflight or solve command below. It will
not be edited after results are known; deviations from it will be reported
in the final `.md`, not hidden.
