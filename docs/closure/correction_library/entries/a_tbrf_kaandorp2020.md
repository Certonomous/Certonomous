---
id: a_tbrf_kaandorp2020
family:
  - a
  - e
flow_class:
  - square_duct_secondary_flow
  - separation_2d
  - geometry_transfer_fixed_Re
validation_cases:
  - PH_Breuer
  - CBFS:CBFS13700
  - DUCT
equation_form: >-
  TBRF predicts the Reynolds-stress ANISOTROPY TENSOR directly from the local mean flow,
  on Pope's (1975) integrity basis, and the predicted anisotropy is then used as the
  turbulence model inside a RANS solve. Transcribed from
  docs/papers/closure/Kaandorp2020_random_forests.pdf.

  (1) THE TENSOR-BASIS REPRESENTATION -- Eq. (8), printed p. 15:
      b = h(S, R) = SUM_{m=1..10} T^(m)(S, R) * g^(m)( theta_1, ..., theta_5 )
  verbatim from p. 15: "where g^(m) are scalar functions of the invariants theta_i. The
  basis tensors derived from S and R are (Pope, 1975)", with T^(1) = S,
  T^(2) = SR - RS, ..., T^(6) = R^2 S + S R^2 - (2/3) I * trace(S R^2), ... S is the
  normalised mean strain-rate tensor and R the normalised mean rotation-rate tensor.

  (2) WHAT IS LEARNED. The g^(m) are NOT a closed-form expression: they are the output
  of a Tensor Basis Random Forest -- an ensemble of tensor-basis decision trees, each
  leaf holding constant values for the ten coefficients (printed p. 18 region:
  "For the TBDT, constant values are chosen for the tensor basis coefficients"),
  obtained by "setting the derivative of J with respect to g^(m) in each bin to zero"
  for "the optimum value for the 10 tensor basis coefficients" (printed p. 19 region).
  The prediction combines trees by a median rather than a mean over the forest (p. 21
  region: "Instead of taking the mean over all the tensor basis decision trees, it ...").

  (3) INPUT FEATURES. The five invariants theta = (theta_1, ..., theta_5) of the tensor
  basis (Pope 1975), extended in the paper with "invariants based on grad(u_bar),
  grad(k), and grad(p)" (printed p. 16 region: "This is the system we use in the ...").

  (4) SOLVER-SIDE REQUIREMENT, from the abstract, printed p. 1, verbatim: "The resulting
  predictions of turbulence anisotropy are used as a turbulence model within a custom
  RANS solver. Stabilization of this solver is necessary, and is achieved by a
  continuation method and a modified k-equation."

  UNVERIFIED -- needs equation-level read: the full ten-term basis T^(1)..T^(10), the
  explicit definitions of theta_1..theta_5, the objective J, the continuation method and
  the exact form of the modified k-equation were NOT transcribed by this lane. Only the
  representation (Eq. 8) and the structural facts above were read. There is no closed-form
  equation to transcribe for g^(m) BY CONSTRUCTION -- the model is a trained forest, and
  that is a property of the method, not a gap in this reading.
provenance:
  path: docs/papers/closure/Kaandorp2020_random_forests.pdf
  title_page_verified: "yes"
  title_page_quote: >-
    "arXiv:1810.08794v2 [physics.flu-dyn] 17 Mar 2020 / Data-Driven Modelling of the
    Reynolds Stress Tensor using Random Forests with Invariance / Mikael L.A.
    Kaandorp(a,b), Richard P. Dwight(a) / (a) Aerodynamics, Faculty of Aerospace, Delft
    University of Technology, 2629 HS, Delft, The Netherlands / (b) Institute for Marine
    and Atmospheric research Utrecht (IMAU), Utrecht University, 3584 CC, Utrecht, The
    Netherlands ... Preprint submitted to Computers and Fluids -- March 18, 2020" --
    verbatim from page 1, read by closure lab-lane (laneC) on 2026-09-04 via
    `pdftotext -f 1 -l 1`. FILENAME CORRECTION: the tasking brief named this file
    `Kaandorp2020_TBRF.pdf`, which DOES NOT EXIST. The file on disk is
    `Kaandorp2020_random_forests.pdf`, as INGEST_PLAN records. The title page, not the
    filename, is what verifies it (L-144).
  equations: >-
    Eq. (8), printed p. 15, of Kaandorp2020_random_forests.pdf (confirmed by extracting
    single PDF pages: the equation appears on PDF page 15 and nowhere on 14 or 16).
    Supporting structural statements: abstract, printed p. 1; §2 tensor-basis material,
    printed pp. 15-21; case list, printed p. 27 region; TBRF-vs-TBNN discussion,
    printed p. 34 region.
claimed_effect: >-
  The paper's own claims, quoted. Abstract, printed p. 1: "The algorithm is trained on
  several flow cases using DNS/LES data, and used to predict the Reynolds stress
  anisotropy tensor for new, unseen flows. ... Results are compared to the neural network
  approach of Ling et al. [J. Fluid Mech, 807(2016):155-...]". Abstract, printed p. 1:
  "...square duct flow case and a backward facing step flow case show good agreement with
  DNS and experimental data-sets." On realizability, printed p. 34: "In all our studies,
  we have never observed unrealizable predictions from TBRF, despite no explicit
  realizability constraint being imposed on the method" -- and, in the same passage, TBNN
  achieves its competing accuracy "at the cost of some unrealizable predictions closest
  to the wall." NOTE: these are QUALITATIVE claims ("good agreement"); this lane
  extracted NO numeric error reduction and none should be quoted until it does. The
  training/test split is the paper's Table 2, printed p. 28 region, which this lane did
  not transcribe.
install_class: compiled-library
install_stanza: |
  # NOT INSTALLABLE ON THIS BOX TODAY. No TBRF RASModel exists here.
  # The stanza a built implementation would take, recorded so the entry is checkable
  # against `nm -DC` the day it is built:
  RAS
  {
      RASModel        <tbrfModelName>;   // UNBUILT -- see contraindications (1)
      turbulence      on;
      printCoeffs     on;
  }
model_type_name: none
libs_required: []
libs_route: ensure_libs
libs_route_justification: none
failure_mode: loud
contraindications: >-
  FOUR.

  (1) NOT INSTALLABLE ON THIS BOX. No TBRF turbulence model exists here. The four user
  libraries built in FOAM_USER_LIBBIN register, by symbol table read with `nm -DC` on
  2026-09-04, only `kOmegaSSTQCR`, `kOmegaSSTCorrected`, `kOmegaSSTFrozen` and
  `kOmegaSSTSparta`. TBRF additionally needs a trained forest at run time, which is not
  a coefficient set but a serialised model artifact, and it needs the paper's custom
  solver. `model_type_name` is `none` and `libs_required` is empty for that reason, and
  this entry cannot pass IMPLEMENTED until both exist.

  (2) THE SOLVER DOES NOT CONVERGE WITHOUT DELIBERATE STABILISATION, by the paper's own
  statement. Abstract, printed p. 1, verbatim: "Stabilization of this solver is
  necessary, and is achieved by a continuation method and a modified k-equation." A
  propagated-anisotropy RANS solve is not a drop-in; any reproduction must report the
  continuation schedule and the k-equation modification actually used, and a failure to
  converge without them is expected behaviour, not a finding.

  (3) A NAMED FAILURE IN THE SHEAR LAYER, which the authors do not explain. Printed
  p. 34, verbatim: "Moving away from the wall into the shear layer TBRF erroneously heads
  too far back towards the two-component boundary at the sections closest to the step.
  The reason for this is unclear, at similar (shear-layer) locations in the training
  flows, the turbulence does not exhibit such behaviour. Furthermore TBNN is reasonably
  accurate here. Diagnostic tools are needed, and will be a focus of future research."
  This is a contraindication for near-separation shear layers specifically.

  (4) A RANDOM FOREST DOES NOT EXTRAPOLATE. INFERRED, not stated by the paper: a tree
  ensemble predicts by averaging training targets in a leaf, so outside the convex range
  of its training features it returns the boundary of what it has seen rather than a
  trend. Applying TBRF at Reynolds numbers or geometries outside its training set is
  therefore contraindicated on method grounds. Marked INFERRED and not to be cited as
  the paper's claim.
what_it_cannot_see: >-
  Eq. (8) is a LOCAL map: b at a point is a function of S, R and their invariants at
  that point (extended with grad(k) and grad(p)), so TBRF cannot see history, upstream
  separation state, or any non-local effect. It cannot see anything outside the convex
  hull of its training features -- see contraindication (4) -- and unlike a symbolic
  model it offers no expression to inspect, so a wrong prediction cannot be traced to a
  term. The paper reports the model reaching an incorrect turbulence state in the shear
  layer and states plainly that "The reason for this is unclear" (printed p. 34): the
  method's own authors could not see why. Its square-duct training data is Pinelli et al.
  (2010) at Re = 1100 to 3500 on the duct semi-height (printed p. 27 region), so it has
  not seen the aspect ratios or Reynolds numbers outside that range.
band_interaction: does_not
status: REGISTERED
cost_estimate_core_min: none
structural:
  modifies_anisotropy_tensor: "yes"
  is_uncertainty_band: "no"
  is_post_hoc_field_correction: "no"
  is_per_case_switching: "no"
  planted_zero_verdict: none
---

# TBRF — Tensor Basis Random Forest (Kaandorp & Dwight 2020)

**Status REGISTERED. Nothing here has been run. ZERO COMPUTE.**

## Filename discrepancy, resolved by reading the page

The tasking brief named `docs/papers/closure/Kaandorp2020_TBRF.pdf`. **That file does
not exist.** The file on disk is `Kaandorp2020_random_forests.pdf`, exactly as
INGEST_PLAN §2 records it. Page 1 was read and it is the intended paper. This is the
benign version of L-144; the malignant version is in the same corpus and is recorded in
the sibling GPSR blocker: `_WRONG_RETRIEVALS/Weatheritt2016_evolutionary_rans.pdf` is a
software-engineering paper about requirements. A filename is not provenance in either
direction.

## Why `install_class: compiled-library`

TBRF predicts `b_ij` and that prediction is propagated into the momentum equation
(Eq. 8, plus the abstract's "used as a turbulence model within a custom RANS solver").
`structural.modifies_anisotropy_tensor: yes`, so SCHEMA §4 refuses `fvOptions-source`:
`fvOptions` adds sources and cannot modify the Reynolds-stress term. ARCHITECTURE §2.2
names the `b_ij` / nonlinear-stress shape as exactly this case.

## Why this is NOT `install_class: field-input`, though it looks close

A tempting reading is that a TBRF anisotropy field could be written into the case time
directory and read back, GEKO-`machineLearning`-style. It cannot be recorded that way
here for two reasons. First, SCHEMA §7.2: **a post-hoc field correction is not a closure
model** — an entry modifies the solved equations and is re-solved, and TBRF's anisotropy
must re-enter the momentum equation each outer iteration, not decorate a converged
field. `structural.is_post_hoc_field_correction: no` is declared on that basis. Second,
if anyone does later install it by a field route, SCHEMA §4's extra duty binds: a
`field-input` correction field that is missing or misnamed **silently becomes zero and
the run completes looking like a plausible baseline**, so a non-zero field must be
planted, read back, and shown to move the solve before any result is believed
(CLAUDE.md rule 3). The checker enforces that: a `field-input` entry cannot reach
`IMPLEMENTED` without `structural.planted_zero_verdict: PASS`.

## `band_interaction: does_not`

TBRF predicts the anisotropy `b_ij`, which is the *shape* of the Reynolds-stress tensor
at fixed `k`; the paper's own diagnostics are barycentric maps and stress *type*. The
k-magnitude enters through the modified k-equation used for stabilisation
(contraindication 2), which is a numerical device rather than the correction. Declared
`does_not` on that reading; if a reproduction shows the stabilised k-equation moving the
k magnitude materially, this field must be revised to `acts_on_k_magnitude` by amendment.

## Duct relevance

This is the entry that matters most for INGEST_PLAN §1's recommendation that the first
certified result target the **square duct**. TBRF's own validation set includes the
square duct (Pinelli et al. 2010, sixteen datasets, Re = 1100–3500 on the duct
semi-height, printed p. 27 region), and the reference DUCT data is already on this box.
It is also the entry furthest from being runnable here — nothing is built, and the
paper's own solver needs a continuation method. Those two facts together are the honest
statement of where this correction stands: **flow-class relevant, capability absent.**

## Readers used

Page 1 by `pdftotext -f 1 -l 1`. All sidecar content searches used **`/bin/grep` over
explicit globs** (L-486: the closure corpus sidecars are invisible to this box's default
`grep` under .gitignore + ugrep). Equation page located by extracting single PDF pages
and testing for the equation text on each — it is on p. 15 and on neither p. 14 nor
p. 16.
