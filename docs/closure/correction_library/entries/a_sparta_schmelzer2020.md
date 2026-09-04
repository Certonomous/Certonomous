---
id: a_sparta_schmelzer2020
family:
  - a
  - e
flow_class:
  - separation_2d
  - Re_extrapolation
  - geometry_transfer_fixed_Re
validation_cases:
  - PH_Breuer:PHLL10595
  - CBFS:CBFS13700
equation_form: >-
  SpaRTA adds TWO additive model-form corrections to k-omega SST, both discovered by
  sparse symbolic regression. Transcribed from
  docs/papers/closure/Schmelzer2020_algebraic_reynolds.pdf.

  (1) AUGMENTED CONSTITUTIVE RELATION -- Eq. (3), printed p. 5:
      b_ij = -(nu_t / k) S_ij + b_ij^Delta
  where, from Eq. (2), printed p. 5, tau_ij = 2k ( b_ij + (1/3) delta_ij ), and the
  baseline is the linear relation b_ij^o = -(nu_t / k) S_ij. b_ij^Delta is the residual
  of the baseline constitutive relation given high-fidelity data -- the paper's
  "model-form error" -- and is the term SpaRTA regresses.

  (2) AUGMENTED k AND omega TRANSPORT -- Eqs. (4) and (5), printed p. 5:
      d_t k   + U_j d_j k   = P_k + R - beta* omega k + d_j[ (nu + sigma_k nu_t) d_j k ]
      d_t om  + U_j d_j om  = (gamma / nu_t)(P_k + R) - beta om^2
                              + d_j[ (nu + sigma_om nu_t) d_j om ] + CD_kom
  with the production itself augmented by b^Delta (printed p. 5, verbatim):
      P_k = 2k ( b_ij^o + b_ij^Delta ) d_j U_i ,   nu_t = a_1 k / max(a_1 omega, S F_2)
  R is the residual of the k equation, extracted by the paper's own
  "k-corrective-frozen-RANS" procedure (printed p. 5).

  (3) THE ANSATZ THE REGRESSION SEARCHES -- Eq. (8), printed p. 6, the Pope (1975)
  integrity basis:
      b_ij(S_ij, Omega_ij) = SUM_{n=1..N} T_ij^(n) alpha_n( I_1, ..., I_5 )
  with S_ij = tau (1/2)( d_j U_i + d_i U_j ), Omega_ij = tau (1/2)( d_j U_i - d_i U_j ),
  timescale tau = 1/omega, and alpha_n the scalar coefficient functions that elastic-net
  symbolic regression makes sparse (printed p. 6, verbatim: "The Cayley-Hamilton theorem
  then dictates that the most general form of the anisotropic part of the Reynolds-stress
  can be expressed as").

  UNVERIFIED -- needs equation-level read: the SPECIFIC discovered expressions for
  b_ij^Delta and R published by Schmelzer et al. (their per-case model table, later in
  the paper) were not transcribed by this lane. Only the model FORM above was read. The
  numbers currently on this box are the LAB'S OWN discovered coefficients, not
  Schmelzer's -- see contraindications (1).
provenance:
  path: docs/papers/closure/Schmelzer2020_algebraic_reynolds.pdf
  title_page_verified: "yes"
  title_page_quote: >-
    "arXiv:1905.07510v2 [physics.comp-ph] 28 Feb 2020 / Discovery of Algebraic
    Reynolds-Stress Models Using Sparse Symbolic Regression. / Martin Schmelzer /
    Richard P. Dwight / Paola Cinnella" -- verbatim from page 1, read by closure
    lab-lane (laneC) on 2026-09-04 via `pdftotext -f 1 -l 1`. Page 1 also carries the
    author-supplied publication pointer: "Flow Turbulence Combustion 104, 579603 (2020).
    https://doi.org/10.1007/s10494-019-00089-x". NOTE: a SECOND copy of this paper is
    held at docs/papers/data_driven_rans/schmelzer_dwight_cinnella_ftac2020_s10494-019-00089-x.pdf;
    this entry cites the docs/papers/closure/ copy, which is the one this lane read.
  equations: >-
    Eqs. (2), (3), (4), (5) on printed p. 5 and Eq. (8) on printed p. 6 of
    Schmelzer2020_algebraic_reynolds.pdf. Printed page numbers were confirmed by
    extracting single PDF pages and reading the page footers, not inferred.
claimed_effect: >-
  The paper's own claim, quoted from the abstract, printed p. 1: "The predictions of the
  discovered models are significantly improved over the k-omega SST also for a true
  prediction of the flow over periodic hills at Re=37000." And, from the results
  discussion (printed p. 22 region, §4): "Most of the models show a good or even
  substantial improvement over the baseline. But, for the set of models, only providing
  a correction for b_ij^Delta, most but not all lead to an improvement of the resulting
  velocity field. In contrast to that, if only a correction for R is deployed, the
  result is a consistent, substantial improvement across all test cases." Model
  discovery and cross-validation were performed on "three cases of separating flows,
  i.e. periodic hills (Re=10595), converging-diverging channel (Re=12600) and curved
  backward-facing step (Re=13700)" (abstract, p. 1). NOTE: the paper's claims here are
  QUALITATIVE ("significantly improved", "substantial"); this lane did not extract a
  numeric error reduction, and none should be quoted until it does.
install_class: compiled-library
install_stanza: |
  RAS
  {
      RASModel        kOmegaSSTSparta;
      turbulence      on;
      printCoeffs     on;
  }
model_type_name: none
# SUPERVISOR CORRECTION 2026-09-04 (SCHEMA Addendum 2, v1.2): was `kOmegaSSTSparta`.
# That model IS built here, but carries the LAB'S OWN R4-discovered coefficients
# (R4_sparta_build/MODEL.json, frozen 2026-08-22), NOT Schmelzer's published ones.
# The entry's contraindications said so in PROSE while this MACHINE field still read
# "run kOmegaSSTSparta" -- and a rung-3 filter reads library.json, not the prose.
# `model_type_name` names the model implementing THIS ENTRY'S PAPER or it is `none`.
near_miss_built_model: kOmegaSSTSparta
libs_required:
  - libspartaTurbulenceModels.so
libs_route: ensure_libs
libs_route_justification: none
failure_mode: loud
contraindications: >-
  FOUR, three of them stated by the paper itself.

  (1) THE BUILT LIBRARY CARRIES THE LAB'S COEFFICIENTS, NOT SCHMELZER'S. `kOmegaSSTSparta`
  is built and registered (`nm -DC libspartaTurbulenceModels.so` shows
  `RASModels::kOmegaSSTSparta`, read by this lane 2026-09-04), but the discovered model
  it is paired with on this box is the LAB'S OWN, frozen at
  cases/RANS_LES_closure_models/R4_sparta_build/MODEL.json (frozen_at 2026-08-22,
  preregistration_sha256 058444309f87a9e1f6faccca2086bf16364df7a06bb7702d155c35b1fcacbbe8),
  whose R model is {T1, I1*T1, I2*T1, I2^2*T1} and whose bDelta model is {T2, I2*T2, T3}.
  Those are not Schmelzer's published expressions. A run of `kOmegaSSTSparta` as it
  stands therefore tests the LAB'S model, not this entry's paper, and cannot advance this
  entry towards REPRODUCED. Reaching REPRODUCED requires installing Schmelzer's OWN
  published coefficients on Schmelzer's OWN case against Schmelzer's OWN reference.

  (2) b^Delta MAY NEED SCALING TO CONVERGE AT ALL. The paper, verbatim: "b_ij^Delta needs
  to be scaled with xi = 0.1 to achieve convergence, see Section 3.3". A correction that
  must be damped by a factor of ten to run is a stability contraindication, and any
  reproduction must report the xi actually used.

  (3) THE b^Delta CORRECTION ALONE OFTEN DOES NOT HELP. Verbatim: "for the set of
  models, only providing a correction for b_ij^Delta, most but not all lead to an
  improvement of the resulting velocity field."

  (4) COMBINING BOTH CORRECTIONS IS NOT UNIFORMLY BETTER. Verbatim: "Using both a model
  for b_ij^Delta and R leads to a further improvement, except for test case CBFS13700."
  And the paper reports its own selection surprise: "Surprisingly, the best model per
  test case is not always identified on the associated training data."
what_it_cannot_see: >-
  The ansatz (Eq. 8) is a LOCAL algebraic function of S_ij, Omega_ij and their five
  invariants, so it is blind to everything not encoded in the local mean-velocity
  gradient: history, upstream separation state, and non-local pressure effects. Eq. (8)
  as written takes no wall distance and no pressure-gradient input, so it cannot
  distinguish a shear layer from a boundary layer with the same local invariants. Its
  training set is three 2-D separating flows -- it has never seen a square duct, which
  is where this library's first ladder target sits, and secondary flow of the second
  kind depends on normal-stress anisotropy in a corner geometry absent from all three
  training cases. Finally, `R` is fitted as a residual of the k equation: it absorbs
  whatever the baseline got wrong, including numerical and data error, and cannot
  distinguish those from a genuine model-form deficiency.
band_interaction: acts_on_k_magnitude
status: REGISTERED
cost_estimate_core_min: none
structural:
  modifies_anisotropy_tensor: "yes"
  is_uncertainty_band: "no"
  is_post_hoc_field_correction: "no"
  is_per_case_switching: "no"
  planted_zero_verdict: none
---

# SpaRTA (Schmelzer, Dwight & Cinnella 2020) — sparse symbolic regression for algebraic Reynolds-stress models

**Status REGISTERED. Nothing here has been run. ZERO COMPUTE.**

## Why `install_class: compiled-library`

Eq. (3) adds `b_ij^Delta` directly to the anisotropy tensor, so
`structural.modifies_anisotropy_tensor: yes`, and SCHEMA §4 refuses `fvOptions-source`
for this entry — `fvOptions` cannot modify the momentum equation's Reynolds-stress
term. ARCHITECTURE §2.2 names SpaRTA explicitly as the shape that forces
`compiled-library`. The `R` correction *alone* (Eqs. 4–5, a source in the k and omega
transport equations) would be legal as `fvOptions-source`; `b^Delta` is not, and the
model is both.

## `band_interaction: acts_on_k_magnitude`

`R` is an additive source in the k equation (Eq. 4) and enters the omega equation
through `(gamma/nu_t)(P_k + R)` (Eq. 5). It moves the k magnitude directly. That is
precisely the axis a shelf-D eigenspace band does *not* perturb, so a band and this
correction shown together must state the overlap in what neither sees
(CLOSURE_MODELLING_CHARTER §22.4 item 2).

## `failure_mode: loud`, and why `ensure_libs` anyway

`kOmegaSSTSparta` is a custom `RASModel` name registered only by
`libspartaTurbulenceModels.so`. If that library does not load, OpenFOAM cannot resolve
the name and aborts with an unknown-RASModel fatal error — a **loud** failure, which is
ARCHITECTURE §2.5's principled `assert_only` exception (sweep site #8). This entry
nevertheless declares `ensure_libs`, the default: `assert_only` is *permitted* for a
loud failure, not *preferable*, and a bare `grep -q '<lib>'` cannot see a second
top-level `libs` entry — a duplicate dictionary key, not a longer list — which
`scripts/foam_libs.py`'s `ensure_libs` refuses on (SCHEMA §5, L-221/L-222,
CLAUDE.md rule 14).

## The gap between this entry and a licensed result

This is a `REGISTERED` entry: it may be **tried**, and a negative result from it is
**not** evidence about SpaRTA — only about our implementation (ARCHITECTURE §0). The
specific obstacle is named in contraindication (1) and is not a formality: the built
library and the lab's `MODEL.json` are a SpaRTA-*class* model, and running them proves
nothing about *this paper's* claim. The reproduction gate for this entry is
Schmelzer's own coefficients, on `PHLL10595` or `CBFS13700`, against the paper's own
reference data.

## Readers used

Page 1 by `pdftotext -f 1 -l 1` (L-144, never by filename or hash — and see the
sibling entry's note on `Weatheritt2016_evolutionary_rans.pdf`, a file in this corpus
whose *name* is right and whose *contents* are a different paper entirely). All sidecar
content searches used **`/bin/grep` over explicit globs**, because the closure corpus
sidecars are invisible to this box's default `grep` (.gitignore + ugrep) — L-486.
Printed page numbers were confirmed by extracting single PDF pages and reading their
footers.
