---
id: b_qcr2000_spalart2000
family: b
flow_class:
  - square_duct_secondary_flow
validation_cases:
  - DUCT
paper_validation_cases: >-
  Spalart's own demonstration is a SQUARE DUCT, compared against Gessner et al. (1991),
  printed p. 253, and referred to Fig. 1. The coefficient itself was calibrated on a
  different flow: "the outer region of a simple boundary layer, by requiring a fair
  level of anisotropy u'^2 > w'^2 > v'^2" (p. 253). ⚠ CRITICAL AND RECORDED HERE RATHER
  THAN BURIED: the demonstration uses the SPALART-ALLMARAS model as its base -- "The S-A
  model (see Appendix A) was used with the following constitutive relation" (p. 253) --
  NOT k-omega SST. The install path available on this box is SST-based. The paper's own
  validation case is therefore NOT reproducible with the model this entry installs
  without either building an SA-QCR or redefining the reproduction target. See
  `what_it_cannot_see`.
equation_form: >-
  READ OFF THE RENDERED PAGE at 300 dpi by closure-supervisor, 2026-09-06 (L-489: never
  transcribe an equation from pdftotext output). Spalart 2000, IJHFF 21(3):252-263,
  UNNUMBERED displayed equation, printed p. 253, verbatim structure:

      tau_ij = taubar_ij - c_nl1 [ O_ik taubar_jk + O_jk taubar_ik ] ,

  where

      O_ik  =  ( d_k U_i - d_i U_k ) / sqrt( d_n U_m d_n U_m )

  which the paper calls "the normalised rotation tensor", and taubar_ij is "the Reynolds
  stress given by the linear model" (p. 253). The constant is c_nl1 = 0.3.

  This equation carries NO equation number in the source -- it is a displayed equation in
  running text in §2.2. The page is cited instead, and the absence of a number is stated
  rather than a number invented.

  THE CORRECTION IS TRACELESS, AND THAT IS DERIVABLE RATHER THAN ASSERTED. Setting i = j
  contracts the antisymmetric O with the symmetric taubar, and O_ik taubar_ik = 0 for an
  antisymmetric O and symmetric taubar. So the trace of the correction vanishes: this
  term redistributes the stress ANISOTROPY and leaves k UNCHANGED. That is the basis for
  `band_interaction: does_not` below, and it is checkable by anyone who doubts it.
provenance:
  path: docs/papers/closure/Spalart2000_strategies_turbulence_modelling.pdf
  title_page_verified: "yes"
  title_page_quote: >-
    Read by closure-supervisor 2026-09-06, page 1, with a NEGATIVE CONTROL (the same
    reader on Pope1975 returned the JFM title page, not this one): "International Journal
    of Heat and Fluid Flow 21 (2000) 252-263 / Strategies for turbulence modelling and
    simulations / P.R. Spalart / Boeing Commercial Airplanes, P.O. Box 3707, Seattle, WA
    98124, USA / Received 7 September 1999; accepted 19 February 2000".
  equations: >-
    Unnumbered displayed equation and its definition of O_ik, both printed p. 253, §2.2
    "Simple RANS models". Rendered at 300 dpi from PDF page 2 and read as an image.
claimed_effect: >-
  Spalart's own claim, quoted, p. 253: "The result in the square duct is quite positive:
  flow is induced towards the corners, and the skin friction is much closer to experiment
  (Gessner et al., 1991)." He frames the point as a demonstration of principle: "it is of
  interest to show that even a one-equation model can be made to predict this secondary
  flow." ⚠ NO NUMERIC ERROR METRIC IS GIVEN for the duct result -- "much closer to
  experiment" is the whole of it, and the comparison lives in Fig. 1. Any reproduction
  therefore has NO published number to hit, and its gate must be pre-registered against
  the reference data this lab holds, not against a figure of the paper's.
install_class: compiled-library
install_stanza: |
  RAS
  {
      RASModel        kOmegaSSTQCR;
      turbulence      on;
      printCoeffs     on;
      kOmegaSSTQCRCoeffs
      {
          Ccr1        0.3;   // Spalart 2000 p. 253, untrained
      }
  }
model_type_name: kOmegaSSTQCR
libs_required:
  - libkOmegaSSTQCRTurbulenceModels.so
libs_route: ensure_libs
libs_route_justification: "none"
failure_mode: loud
contraindications: >-
  ALL FOUR ARE SPALART'S OWN, QUOTED, from p. 253 -- this is what a contraindication
  looks like when the author supplies it.
  (1) NEGATIVE RESULTS ON ANOTHER FLOW CLASS: "other flows such as 3D wall jets have led
  to negative results (A.N. Secundov, personal communication, 1999)."
  (2) THE AUTHOR CALLS IT PRELIMINARY: "The c_nl1 term must also be considered as very
  preliminary, in the sense that it uses only one of the many quadratic combinations of
  strain and vorticity."
  (3) IT IS EMPIRICAL, NOT DERIVED: "it is fully empirical, instead of being derived from
  a more complex model; we simply selected the most intuitively attractive combination."
  (4) UNOPTIMISED: "A systematic optimisation has not been performed."
  (5) THIS LAB'S OWN, NOT THE PAPER'S: the coefficient was calibrated in a BOUNDARY LAYER
  and the flow class this entry targets is a DUCT. c_nl1 = 0.3 therefore arrives at the
  duct as a transferred calibration, which is precisely the condition charter §22.4 item 4
  and L-219 require to be stated beside any literature magnitude.
  ⚠ A MISREAD I CHECKED AND AVOIDED, recorded so a successor does not make it: p. 253
  ends "...but we have found the effect too weak to justify a widespread modification of
  codes and testing campaign." THAT SENTENCE IS ABOUT REALISABLE VERSIONS OF SIMPLE
  MODELS, NOT ABOUT THE QCR TERM -- it follows "Similarly, realisable versions of simple
  models can be created". Attributing it to QCR would invert this entry's whole case, and
  it is the same fragment-of-a-conditional-sentence error already caught once in the
  SpaRTA entry.
what_it_cannot_see: >-
  (a) IT SEES ONE QUADRATIC COMBINATION ONLY -- the author's words: "it uses only one of
  the many quadratic combinations of strain and vorticity". The other quadratic invariant
  combinations of S and Omega are outside the model by construction.
  (b) IT CANNOT SEE k. The correction is traceless (derived in `equation_form`), so it
  redistributes anisotropy and leaves the turbulent kinetic energy exactly as the linear
  model set it. A k-magnitude error passes through this correction untouched.
  (c) ⚠ THE BASE MODEL IS NOT THE PAPER'S. Spalart demonstrated this constitutive relation
  on SPALART-ALLMARAS; `kOmegaSSTQCR` applies it to k-omega SST. The QCR term is a
  constitutive relation and transfers between base models in principle, but the DUCT
  RESULT Spalart reports is an S-A result. Nothing in this entry establishes that SST+QCR
  reproduces S-A+QCR on that duct, and no reproduction may quietly substitute one for the
  other.
band_interaction: does_not
structural:
  modifies_anisotropy_tensor: "yes"
  is_uncertainty_band: "no"
  is_post_hoc_field_correction: "no"
  is_per_case_switching: "no"
  planted_zero_verdict: "none"
status: REGISTERED
cost_estimate_core_min: "none"
---

# QCR2000 — the quadratic constitutive relation, Spalart 2000

**Why this entry exists, and why it is the duct-first target.** The library held three corrections
and none of them could honestly be run on a square duct. TBRF was trained on no duct and its
invariants are measurably degenerate there; SST-QCRC's `beta_CND` half has a feature basis
truncated on an explicitly 2D premise; SpaRTA's built library carries this lab's own coefficients
rather than the paper's. **This correction is the one in reach that has none of those problems.**

## Why `model_type_name` is NOT `none` here — the check SCHEMA Addendum 2 demands

Every other entry in this library carries `model_type_name: none`, because in each case the
plausibly-matching built model implements something other than that entry's paper. **This entry is
the exception, and it was verified rather than assumed:**

1. **The symbol is registered.** `nm -DC` on `libkOmegaSSTQCRTurbulenceModels.so` resolves
   `RASModels::kOmegaSSTQCR` (the ARCHITECTURE §2.3 zero-compute assertion).
2. **The source implements THIS paper's equation.** `sdk/openfoam/qcr/kOmegaSSTQCR/kOmegaSSTQCR.C`
   computes `-Ccr1_*symm((O & taul) - (taul & O))` with `Ccr1` defaulting to `0.3`, and its header
   documents the coefficient as *"c_r = 0.3 (Spalart 2000, untrained)"*.
3. **The sign convention was checked, not waved through.** The header writes the term as
   `-Ccr1[O_ik tau_jk + O_jk tau_ik]` (a PLUS) while the code computes `(O & taul) - (taul & O)`
   (a MINUS). These agree: `taul` is symmetric and `O` antisymmetric, so `O_jk taubar_ik =
   -taubar_ik O_kj`, and the two forms are the same tensor. **A mismatch here would have been a
   silent sign error in the anisotropy, so it was resolved rather than assumed.**

**What this does NOT establish.** That the library still builds against v2606, and that the on-disk
source is the source which produced the `.so` — neither was checked, and checking the first is
compute. `IMPLEMENTED` requires that demonstration.

## What `REPRODUCED` would have to mean for this entry — and why it needs deciding BEFORE Phase 2

The licence state `REPRODUCED` means an entry reproduced **its own paper's claimed improvement on
its own paper's validation case**. For this entry that runs into two facts:

- **The paper's base model is S-A, not SST.** Reproducing Spalart's *own* case strictly needs an
  SA-QCR. `SpalartAllmaras` ships with this OpenFOAM; an SA-QCR does **not** exist on this box.
- **The paper publishes no number for the duct.** "Much closer to experiment" and a figure are the
  whole claim.

**So the reproduction target must be pre-registered explicitly, and there are only two honest
options:** (i) build SA-QCR and target Spalart's qualitative claim — corner-directed secondary flow
where the linear model produces none — against the duct reference data this lab holds; or
(ii) declare the target as SST+QCR against that same reference data, and record plainly that this
is **not** the paper's configuration, which caps the entry at evidence *about* QCR in this lab's
hands rather than a reproduction of Spalart. **Neither is chosen here.** Choosing it is a
pre-registration decision and belongs in Phase 2's registered path, not in a library entry.

## Retrieval item this reading surfaces

Spalart credits the origin of the idea, p. 253: non-Boussinesq constitutive relations *"can, for
instance, create secondary flows of the second kind in a square pipe (Speziale, 1987)."*
**Speziale 1987 is NOT held.** It is the primary source for the very mechanism the duct-first plan
turns on, and it belongs on the retrieval register beside Wallin & Johansson 2000.
