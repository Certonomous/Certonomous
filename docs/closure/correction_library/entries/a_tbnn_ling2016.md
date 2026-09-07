---
id: a_tbnn_ling2016
family:
  - a
  - e
flow_class:
  - square_duct_secondary_flow
  - separation_2d
  - Re_extrapolation
validation_cases:
  - DUCT
equation_form: >-
  TBNN (Tensor Basis Neural Network) predicts the Reynolds-stress ANISOTROPY TENSOR b
  directly from the local mean flow, on Pope's (1975) integrity basis, using a deep neural
  network whose architecture is BUILT to lie on that basis so that Galilean invariance is
  guaranteed by construction. The predicted anisotropy is then propagated into a custom RANS
  solver. Transcribed from docs/papers/closure/Ling2016_tbnn_embedded_invariance.pdf
  (SAND2016-7345J preprint; the JFM 807(2016):155 version). READER DISCLOSURE: every equation
  below was read off a 200-dpi PNG render of the named printed page, produced with
  `pdftoppm -r 200 -f <page> -l <page> -png`; `pdftotext`/`/bin/grep` over the explicit
  sidecar path were used ONLY to locate pages (L-486). PDF page number equals printed page
  number throughout this 17-page file, confirmed by reading the printed footer on each
  rendered page (7, 8, 9, 11, 12, 13 all match).

  (1) THE NORMALISED ANISOTROPY TARGET -- printed p. 4, an inline UNNUMBERED definition:
      b_ij = ( u'_i u'_j ) / (2 k)  -  (1/3) delta_ij
  and, same page, verbatim: "The inputs to the neural networks were based on the mean strain
  rate tensor S and the mean rotation rate tensor R, non-dimensionalized using the turbulent
  kinetic energy k and the turbulent dissipation rate [eps] as suggested by Pope [5]." So the
  normalisation timescale is k/eps, and the RANS inputs are the k-eps LEVM fields (printed
  p. 8, verbatim: "The RANS data, obtained using the k - [eps] model with a Linear Eddy
  Viscosity Model for the Reynolds stresses, were used as the inputs to the neural networks").

  (2) THE TENSOR-BASIS (INTEGRITY-BASIS) REPRESENTATION -- Eq. (1), printed p. 7:
      b = SUM_{n=1..10} g^(n)( lambda_1, ..., lambda_5 ) T^(n)
  printed p. 7, verbatim: "Pope proved that in the most general case, an eddy viscosity model
  for incompressible flow that is a function of only S and R can be expressed as a linear
  combination of 10 isotropic basis tensors:" ... "Any tensor b which satisfies this
  condition will automatically satisfy Galilean invariance." The finiteness is by
  Cayley-Hamilton (printed p. 7, spelled "Caley-Hamilton" in the source).

  (3) THE TEN BASIS TENSORS AND THE FIVE INVARIANTS IN FULL -- Eq. (2), printed p. 7. UNLIKE
  the Kaandorp TBRF entry, where the basis carried NO equation number, here BOTH the ten
  tensors AND the five invariants are displayed together and labelled Eq. (2):
      T^(1)  = S                                 T^(6)  = R^2 S + S R^2 - (2/3) I . Tr(S R^2)
      T^(2)  = S R - R S                         T^(7)  = R S R^2 - R^2 S R
      T^(3)  = S^2 - (1/3) I . Tr(S^2)           T^(8)  = S R S^2 - S^2 R S
      T^(4)  = R^2 - (1/3) I . Tr(R^2)           T^(9)  = R^2 S^2 + S^2 R^2 - (2/3) I . Tr(S^2 R^2)
      T^(5)  = R S^2 - S^2 R                     T^(10) = R S^2 R^2 - R^2 S^2 R
      lambda_1 = Tr(S^2) ,  lambda_2 = Tr(R^2) ,  lambda_3 = Tr(S^3) ,
      lambda_4 = Tr(R^2 S) ,  lambda_5 = Tr(R^2 S^2)
  This is the SAME Pope (1975) basis Kaandorp's TBRF uses, but Ling's TBNN feeds the network
  ONLY these five invariants lambda_1..lambda_5 (see (4)) -- it does NOT add grad(k), grad(p)
  or wall-distance features, which is the input-set difference that separates this entry from
  the TBRF entry and matters for the duct (see contraindications (4) and what_it_cannot_see).

  (4) THE NOVELTY -- THE TBNN ARCHITECTURE AND THE MULTIPLICATIVE MERGE LAYER, printed p. 8,
  described in prose and in Fig. 3 (printed p. 6) with NO equation number of its own (it is a
  network that REALISES Eq. (1); quoting an equation number for it would be inventing one).
  Verbatim, printed p. 8: "As Fig. 3 shows, the network architecture was designed to match
  Eq. 1. There are two input layers: an Invariant Input Layer and a Tensor Input Layer. The
  Invariant Input Layer takes in the 5 invariants lambda_1, ..., lambda_5, and is followed by
  a series of hidden layers. The Final Hidden Layer has 10 elements and represents g^(n) for
  n = 1, ..., 10. The output from these 10 nodes is then multiplied by the Tensor Input Layer,
  which also has 10 nodes. These 10 nodes represent the 10 tensors T^(n) for n = 1, ..., 10.
  The Merge Output Layer performs element-wise multiplication between the outputs of the Final
  Hidden Layer and the Tensor Input Layer and then sums the result to give the final
  prediction for b. This innovative architecture ensures that Eq. 1 is satisfied, thereby
  guaranteeing the Galilean invariance of the network predictions." THIS multiplicative merge
  layer -- g^(n)(lambda) computed by the deep net, then multiplied against the fixed tensor
  basis T^(n) and summed -- is exactly how invariance is EMBEDDED, and it is the paper's
  central contribution. The TBNN was trained with STOCHASTIC gradient descent (printed p. 8:
  "Because of this final multiplicative layer, stochastic gradient descent was used ... more
  convenient to implement given the added complexity of back-propagation through a
  multiplicative layer"), 8 hidden layers, 30 nodes per hidden layer, learning rate 2.5e-7,
  hyper-parameters chosen by Bayesian optimisation (Spearmint), printed p. 8.

  THE GENERIC MLP BASELINE IT BEATS -- printed pp. 5-6, so the novelty is legible by contrast.
  The MLP is a densely-connected feed-forward net whose inputs are, verbatim (printed p. 5),
  "the 9 distinct components of the non-dimensionalized strain rate and rotation rate tensors,
  S and R, at a given point": 10 hidden layers, 10 nodes each, learning rate 2.5e-6 (printed
  p. 6). The MLP has NO embedded invariance, and the paper's central a-priori finding is that
  the TBNN beats it (Table I; the MLP RMSE is 0.33 on the duct, WORSE than the LEVM's 0.23).

  (5) THE BASELINE RANS CLOSURES the paper compares against, printed p. 9:
      LEVM (inline, UNNUMBERED, printed p. 9):  b = - (nu_t / k) S
      QEVM (Craft's non-linear EVM), Eq. (3), printed p. 9:
        b_ij = - (nu_t S_ij)/k
               + C1 (nu_t / eps~)( 2 S_ik S_kj - (2/3) S_kl S_kl delta_ij )
               + C2 (nu_t / eps~)( 2 R_ik S_kj + 2 R_jk S_ki )
               + C3 (nu_t / eps~)( 2 R_ik R_jk - (2/3) R_kl R_kl delta_ij )
      with C1 = -0.1, C2 = 0.1, C3 = 0.26 (printed p. 9).

  (6) PROPAGATION INTO THE VELOCITY FIELD -- the paper's a-posteriori path, printed p. 12,
  and it is DECISIVE for band_interaction. Verbatim: "the Reynolds stress anisotropy tensor
  predicted by the TBNN was implemented in an in-house RANS solver, SIERRA Fuego [30], in the
  momentum equations AND in the turbulent kinetic energy production term." (emphasis added).
  There is NO displayed propagation equation; the statement is prose. The DNS-b comparison
  model (printed p. 12) implements the true DNS anisotropy the same way and is called, verbatim,
  "the upper performance limit of an improved Reynolds stress anisotropy model" -- i.e. the
  published TBNN a-posteriori result must be read against DNS-b, not against DNS directly.

  BAND_INTERACTION READING, RECORDED FOR THE SUPERVISOR AND NOT SILENTLY RESOLVED. Ling's own
  propagation (printed p. 12) puts the TBNN anisotropy into BOTH the momentum equations AND
  the turbulent-kinetic-energy PRODUCTION term. Putting b into the k-production term makes the
  k MAGNITUDE an explicit function of the learned anisotropy, not only the stress SHAPE -- the
  SAME axis Kaandorp's modified k-equation acts on (the TBRF entry's supervisor ruling,
  `acts_on_k_magnitude`). On the paper's own words this entry's `band_interaction` reads
  toward `acts_on_k_magnitude`. `band_interaction` is a declared machine field OUTSIDE this
  lane's brief; it is left `unknown` here and flagged SUPERVISOR TO RULE (see the prose
  section "band_interaction: unknown -- SUPERVISOR TO RULE" below).

  WHAT IS DELIBERATELY NOT TRANSCRIBED, NAMED EXACTLY. There is NO closed-form g^(n) to
  transcribe, BY CONSTRUCTION: the model is a trained deep network (8 layers x 30 nodes,
  printed p. 8), and reproducing it needs the serialised weights, not an equation -- a
  property of the method, not a gap in this reading. The SIERRA Fuego solver internals and the
  back-propagation-through-the-merge-layer gradient are not given in the paper and are not
  transcribed. Everything the paper prints at equation level -- Eq. (1), the ten tensors and
  five invariants Eq. (2), the LEVM/QEVM baselines Eq. (3), and the prose propagation -- is
  above with its printed page.
provenance:
  path: docs/papers/closure/Ling2016_tbnn_embedded_invariance.pdf
  title_page_verified: "yes"
  title_page_quote: >-
    "Reynolds Averaged Turbulence Modeling using Deep Neural Networks with Embedded Invariance
    / Julia Ling, Jeremy Templeton (Sandia National Laboratories, Thermal/Fluid Sciences and
    Engineering Department, Livermore, CA) and Andrew Kurzawski (University of Texas at Austin,
    Mechanical Engineering Department, Austin, TX) / (Dated: July 24, 2016) / SAND2016-7345J" --
    read off page 1 by closure-supervisor on 2026-09-07 (CLAUDE.md rule 15, done personally by
    the supervisor and not re-attributed by this lane). CORRECT-PAPER NOTE: this is the TBNN
    paper, distinguished from the sibling `_WRONG_RETRIEVALS/Ling2016_reynolds_neural_nets.pdf`
    by reading the title page, not the filename (L-144).
  equations: >-
    Of Ling2016_tbnn_embedded_invariance.pdf, all read as 200-dpi page images and all confirmed
    against the printed footer of the page (PDF page number equals printed page number
    throughout this 17-page file): the inline b_ij definition and the k/eps normalisation on
    printed p. 4 (UNNUMBERED); Eq. (1), the tensor-basis representation, on printed p. 7;
    Eq. (2), the ten basis tensors T^(1)..T^(10) AND the five invariants lambda_1..lambda_5
    (displayed together under one equation number), on printed p. 7; the TBNN architecture and
    multiplicative Merge Output Layer on printed p. 8 (UNNUMBERED -- a network realising Eq. 1,
    schematic Fig. 3 on printed p. 6); the generic MLP baseline inputs/architecture on printed
    pp. 5-6; the LEVM inline closure (UNNUMBERED) and the QEVM Eq. (3) on printed p. 9; the
    a-posteriori propagation statement (momentum equations AND TKE production term; SIERRA
    Fuego) on printed p. 12 (prose, UNNUMBERED). Supporting non-equation material: abstract,
    printed p. 1; database of 9 flows and the 6 train / 1 validation / 2 test split, printed
    p. 8; a-priori RMSE Table I, printed p. 11; a-priori percentage claims, printed pp. 11-12;
    a-posteriori duct secondary flow (Fig. 6) and wavy-wall separation (Fig. 7), printed p. 13.
claimed_effect: >-
  The paper's own claims, quoted. Abstract, printed p. 1: "A novel neural network architecture
  is proposed which uses a multiplicative layer with an invariant tensor basis to embed
  Galilean invariance into the predicted anisotropy tensor. It is demonstrated that this neural
  network architecture provides improved prediction accuracy compared to a generic neural
  network architecture which does not embed this invariance property. ... For both test cases,
  significant improvement versus baseline RANS linear eddy viscosity and non-linear eddy
  viscosity models is demonstrated."

  A-PRIORI (RMSE of the predicted normalised anisotropy b against DNS), Table I, printed p. 11.
  The two test cases are turbulent DUCT flow at Re_b = 2000 and periodic flow over a WAVY WALL
  at Re = 6850 (printed p. 8). RMSE values, verbatim from Table I:
      Model   Duct Flow   Wavy Wall
      LEVM    0.23        0.18
      QEVM    0.18        0.11
      TBNN    0.13        0.08
      MLP     0.33        0.09
  DUCT, printed p. 11, verbatim: the TBNN "provides by far the most accurate predictions in
  this case: 43% more accurate than the LEVM and 28% more accurate than the QEVM" (i.e.
  (0.23-0.13)/0.23 = 43%, (0.18-0.13)/0.18 = 28%). WAVY WALL, printed p. 12, verbatim: "giving
  a 56% reduction in error with respect to LEVM and a 27% reduction in error with respect to
  QEVM" ((0.18-0.08)/0.18 = 56%, (0.11-0.08)/0.11 = 27%). Note the MLP RMSE on the duct is
  0.33 -- WORSE than the LEVM baseline (0.23) -- which is the quantitative form of the paper's
  headline: embedding invariance (TBNN) beats a generic net (MLP), printed p. 12.

  A-POSTERIORI (mean-velocity fields from propagating b through SIERRA Fuego). THERE IS NO
  PUBLISHED SCALAR NUMBER FOR EITHER TEST CASE -- both are reported qualitatively from figures,
  exactly as the Kaandorp TBRF entry records for its own duct case. DUCT, Fig. 6, printed p. 13:
  verbatim, "the LEVM does not predict any secondary flows at all. The QEVM predicts corner
  vortices, but significantly under-predicts their strength. The TBNN, on the other hand,
  over-predicts the strength of these vortices, with incorrect counter-rotating vortices forming
  near the center of the channel." And, printed p. 13: "while the TBNN provides improved
  secondary flow predictions, it is still not able to correctly capture the strength and shape
  of the corner vortices." WAVY WALL, Fig. 7, printed p. 13: verbatim, "The RANS LEVM and QEVM
  both fail to predict flow separation downstream of the bump. The DNS-b correctly predicts the
  size and shape of the separated region. TBNN predicts flow separation, though in a smaller
  region than the DNS." REFERENCE DATA: DNS for both cases (duct DNS Pinelli et al. 2010 class;
  wavy wall DNS), and DNS-b (the true DNS anisotropy propagated through the same solver) as the
  published UPPER BOUND (printed p. 12). A reproduction may compare a-posteriori PROFILES/FIELDS
  but may NOT quote a numeric a-posteriori improvement, because the paper publishes none, and
  must quote any a-posteriori result against DNS-b, not DNS.
paper_validation_cases: >-
  The paper trains, validates and tests on a database of NINE flows (printed p. 8, verbatim:
  "a database of 9 flows"), split 6 / 1 / 2. NOTE: the tasking brief said "~11 flows"; the
  paper itself says NINE, and that is what is recorded here.
  TRAINING (6 cases, printed p. 8): duct flow at Re_b = 3500 [Pinelli et al. 2010, ref 22];
  channel flow at Re_tau = 590 [Moser et al. 1999, ref 23]; a perpendicular jet in crossflow
  [Ruiz et al. 2015, ref 24]; an inclined jet in crossflow [Ling et al. 2015, ref 25]; flow
  around a square cylinder [refs 26, 27]; and flow through a converging-diverging channel
  [Marquillie et al. 2011, ref 28]. NO id exists for the channel, the jets, the square cylinder
  or the converging-diverging channel in SCHEMA §3 and none is coined.
  VALIDATION for hyper-parameter selection (1 case, printed p. 8): a wall-mounted cube in
  crossflow at bulk Reynolds number 5000 [Rossi et al. 2010, ref 29]. No id coined.
  TESTING (2 cases, printed p. 8) -- these are the ONLY a-priori/a-posteriori test cases:
  (a) DUCT flow at Re_b = 2000 -- a DIFFERENT Reynolds number from the training duct
  (Re_b = 3500), which the paper frames as an extrapolation test (printed p. 14, verbatim:
  "While there was also a duct flow test case in the training set, the test case was at a
  significantly different Reynolds number"). This is the case that maps to the SCHEMA §3 id
  DUCT.
  (b) WAVY WALL -- periodic flow over a wavy wall at Re = 6850, "a completely different geometry
  than any of the training cases" (printed p. 14). NO id exists for a wavy wall in SCHEMA §3;
  it is NOT the same as PH_Breuer/Parm_PH_29 (periodic hills) or NASA_2DWMH (a 2-D wall-mounted
  hump), and none is coined -- yet it is one of only two a-posteriori cases, so it must not be
  dropped (SCHEMA Addendum 1 item 3).
  The DNS-b model (true DNS anisotropy propagated through SIERRA Fuego) is the published upper
  bound for both test cases (printed p. 12), not a separate flow case.
install_class: compiled-library
install_stanza: |
  # NOT INSTALLABLE ON THIS BOX TODAY. No TBNN RASModel exists here, and none can be built
  # from an OpenFOAM dictionary: TBNN is a trained deep neural network (8 layers x 30 nodes,
  # stochastic-gradient-descent trained, printed p. 8) that must be evaluated inside the
  # momentum and k-production terms of a custom RANS solver (the paper used Sandia's
  # proprietary SIERRA Fuego, printed p. 12). The stanza a built implementation would take,
  # recorded so the entry is checkable against `nm -DC` the day it is built:
  RAS
  {
      RASModel        <tbnnModelName>;   // UNBUILT -- see contraindications (1)
      turbulence      on;
      printCoeffs     on;
  }
model_type_name: none
near_miss_built_model: none
libs_required: []
libs_route: ensure_libs
libs_route_justification: none
failure_mode: loud
contraindications: >-
  SIX.

  (1) NOT INSTALLABLE ON THIS BOX. No TBNN turbulence model exists here. The user libraries
  built in FOAM_USER_LIBBIN register, by the symbol-table read (`nm -DC`) recorded in the
  sibling TBRF entry (2026-09-04), only `kOmegaSSTQCR`, `kOmegaSSTCorrected`, `kOmegaSSTFrozen`
  and `kOmegaSSTSparta` -- NONE of them a TBNN. Beyond a compiled RASModel, TBNN needs a
  trained network artifact (serialised weights of an 8x30 deep net) AND the paper's custom
  RANS solver, which was SIERRA Fuego, a proprietary Sandia code not present here.
  `model_type_name` is `none`, `near_miss_built_model` is `none` (there is no near-miss built
  model -- unlike the QCR family, nothing on this box even resembles a TBNN), and
  `libs_required` is empty for that reason. This entry cannot pass IMPLEMENTED until a network,
  a loader and a solver-side coupling all exist.

  (2) THE A-POSTERIORI IMPROVEMENT IS PARTIAL AND THE PAPER SAYS SO, per case. On the DUCT the
  TBNN OVER-predicts corner-vortex strength and, verbatim (printed p. 13), forms "incorrect
  counter-rotating vortices ... near the center of the channel"; it "is still not able to
  correctly capture the strength and shape of the corner vortices." On the WAVY WALL it
  predicts separation but "in a smaller region than the DNS" (printed p. 13). A reproduction
  that reported "TBNN captures the secondary flow / separation" without these qualifiers would
  overstate the paper's own result.

  (3) A NEURAL NET DOES NOT EXTRAPOLATE OUTSIDE ITS TRAINING MANIFOLD. INFERRED, on method
  grounds, and marked as such -- a trained network is only constrained where it saw data;
  outside the convex hull of its training features its output is an unconstrained extrapolation.
  THE PAPER CLAIMS THE OPPOSITE, optimistically: printed p. 14, verbatim, "the TBNN learned
  about the underlying flow regimes and has the capability to extrapolate to new flow cases."
  That claim is a POSITIVE result about two specific test flows, not a guarantee; and the
  paper's own a-posteriori imperfections (item 2) are the counterweight. This is marked
  INFERRED and must NOT be cited as the paper's claim -- the paper claims extrapolation
  capability; the caution is a method-level qualifier this lab attaches.

  (4) THE FIVE POPE INVARIANTS ARE DEGENERATE IN THE SQUARE DUCT -- and the square duct is this
  library's first ladder target. LING 2016 DOES NOT STATE THIS; it is a CROSS-REFERENCED finding
  from Kaandorp2020 (the TBRF entry `a_tbrf_kaandorp2020`, which quotes it from printed p. 23 /
  p. 37 of that paper: "due to the symmetry of the case there are only two distinct 'basis
  functions' defined by theta"). It bites LING'S TBNN HARDER than it bites TBRF, because Ling's
  network is fed ONLY the five invariants lambda_1..lambda_5 of S and R (Eq. (2), printed p. 7;
  architecture, printed p. 8) -- it has NO grad(k), grad(p) or wall-distance features to escape
  the degeneracy, whereas Kaandorp's TBRF added FS2/FS3 precisely to recover the duct. Any duct
  reproduction of Ling's TBNN as published is therefore contraindicated on this ground, and the
  attribution is explicit: the mechanism is Kaandorp's finding, applied to Ling's input set by
  construction, not a claim Ling makes.

  (5) NEAR-WALL REALIZABILITY. LING 2016 NEITHER IMPOSES a realizability constraint NOR reports
  unrealizable predictions in this paper -- so no realizability claim of Ling's own can be
  quoted here. The near-wall UNREALIZABILITY of TBNN is a finding of the LATER Kaandorp2020
  benchmark (recorded verbatim in the TBRF entry, printed p. 35 of that paper: TBNN outperforms
  TBRF at three of five stations "at the cost of some unrealizable predictions closest to the
  wall"). It is recorded here as evidence ABOUT this method from a downstream comparison,
  explicitly NOT as Ling's own statement.

  (6) THE MODEL IS NON-DETERMINISTIC TO REPRODUCE AND HAS NO INSPECTABLE FORM. Training used
  stochastic gradient descent (printed p. 8) and Bayesian hyper-parameter optimisation, and the
  correction is a trained 8x30 network with no closed-form g^(n). Reproducing the paper's numbers
  needs the exact serialised weights, not equations; a re-trained network is a different model,
  and a wrong prediction cannot be traced to a term (contrast a symbolic closure like SpaRTA).
what_it_cannot_see: >-
  Eq. (1), printed p. 7, is a LOCAL pointwise map: b at a point is a function of S and R -- via
  the five invariants lambda_1..lambda_5 -- evaluated AT THAT POINT. TBNN therefore cannot see
  history, upstream separation state, or any genuinely non-local effect.

  Its input set is NARROWER than the Kaandorp TBRF entry's, and this is the sharpest thing it
  cannot see. Ling's TBNN is fed ONLY the five Pope invariants of S and R (Eq. (2)/architecture,
  printed pp. 7-8). It does NOT ingest grad(k), grad(p), or wall distance -- the FS2/FS3 features
  Kaandorp2020 added. So Ling's TBNN as published is blind to the pressure gradient, the wall
  distance and the TKE gradient, and, because of exactly this, blind to the square duct: in the
  duct the five invariants collapse to two effectively-distinct functions (the Kaandorp finding,
  contraindication (4)), so a TBNN on lambda_1..lambda_5 alone literally cannot see the
  secondary-flow structure it is meant to predict there.

  It cannot see anything outside the convex hull of its training features (contraindication (3),
  INFERRED). And unlike a symbolic model it offers no expression to inspect: a wrong prediction
  cannot be traced to a term, only to opaque trained weights. The paper's own a-posteriori
  failures -- over-predicted, wrongly counter-rotating duct vortices; under-sized wavy-wall
  separation (printed p. 13) -- are the visible face of these blindnesses.
band_interaction: acts_on_k_magnitude
# SUPERVISOR RULING 2026-09-07 (closure-supervisor). Was `unknown`, left so by the drafting
# lane. RULED `acts_on_k_magnitude`. The lane read Ling's own propagation on printed p. 12, and
# the supervisor INDEPENDENTLY verified that page (200-dpi render, 2026-09-07): the TBNN
# anisotropy is implemented, verbatim, "in the momentum equations and in the turbulent kinetic
# energy production term." A `b` in the k-PRODUCTION term makes the k MAGNITUDE an explicit
# function of the learned anisotropy, not only the stress SHAPE. This is the IDENTICAL mechanism
# on which the TBRF entry was ruled `acts_on_k_magnitude` (Kaandorp's modified k-equation puts
# tau_ML into the same production term), so the two rulings are consistent. The lane correctly
# declined to set a declared machine field outside its brief and escalated -- exactly as the
# TBRF lane did.
#
# CONSEQUENCE UNDER CHARTER 22.4 ITEM 2, which is why this field exists at all: the shelf-D
# eigenspace band perturbs shape and orientation ONLY -- Emory eq. (4) keeps k OUTSIDE the
# bracket -- so it is SILENT on the k-magnitude axis this model moves. A shelf-D band quoted
# beside a TBNN prediction is therefore an envelope silent on the axis the model moves, and
# quoting it as "the uncertainty of this model" is the error 22.4 item 2 forbids in terms. Any
# record showing both must state that overlap.
status: REGISTERED
cost_estimate_core_min: none
structural:
  modifies_anisotropy_tensor: "yes"
  is_uncertainty_band: "no"
  is_post_hoc_field_correction: "no"
  is_per_case_switching: "no"
  planted_zero_verdict: none
---

# TBNN — Tensor Basis Neural Network (Ling, Kurzawski & Templeton 2016)

**Status REGISTERED. Nothing here has been run. ZERO COMPUTE.**

## Why this entry exists — BREADTH, not novelty

This entry DUPLICATES the data-informed-anisotropy CLASS already covered by the TBRF entry
`a_tbrf_kaandorp2020` (Kaandorp & Dwight 2020). It is registered for BREADTH, as the
**founding (2016) embedded-invariance data-driven anisotropy method** — the one that TBRF
(2020) and later data-driven closure work explicitly benchmark against. TBRF's own abstract
compares its results "to the neural network approach of Ling et al. [J. Fluid Mech,
807(2016):155-...]", and TBRF's Table 3 reports TBNN's a-priori duct RMSE beside its own
(FS1-only: TBNN 0.0871 vs TBRF 0.0995; full-feature: TBNN 0.0681 vs TBRF 0.0521 — cross-ref
the TBRF entry's `claimed_effect`, printed p. 37 of Kaandorp). It is **not** registered as a
new capability: it ships NO runnable model on this box and stays REGISTERED, which by SCHEMA
§6 means it can NEVER be cited as ladder evidence and `ladder_evidence` is computed 0.

## Correct-paper check, done by reading the page

The corpus holds a look-alike, `_WRONG_RETRIEVALS/Ling2016_reynolds_neural_nets.pdf`. The
paper used here is `Ling2016_tbnn_embedded_invariance.pdf`, and page 1 was read (by
closure-supervisor, 2026-09-07, CLAUDE.md rule 15) and confirmed to be the TBNN /
embedded-invariance paper (SAND2016-7345J, the JFM 807:155 version). The title page, not the
filename, is what verifies it (L-144).

## Why `install_class: compiled-library`

TBNN predicts `b_ij` and propagates it into the momentum equations and the k-production term
(Eq. 1; propagation printed p. 12). `structural.modifies_anisotropy_tensor: yes`, so SCHEMA §4
refuses `fvOptions-source`: `fvOptions` adds sources and cannot modify the momentum equation's
Reynolds-stress term. An anisotropy correction of this shape must be `compiled-library`.

## Why this is NOT `install_class: field-input`, though a trained net looks close

A trained TBNN could tempt a field route — write a predicted `b` field into the case and read
it back, GEKO-`machineLearning`-style. It is not recorded that way, for the same two reasons the
TBRF entry gives. First, SCHEMA §7.2: **a post-hoc field correction is not a closure model** —
entries modify the solved equations and are re-solved, and Ling's `b` re-enters the momentum and
k-production terms each iteration inside SIERRA Fuego (printed p. 12), it does not decorate a
converged field. `structural.is_post_hoc_field_correction: no` is declared on that basis.
Second, if anyone later installs it by a field route, SCHEMA §4's extra duty binds: a
`field-input` correction field that is missing or misnamed **silently becomes zero and the run
completes looking like a plausible baseline** (CLAUDE.md rule 3), so a non-zero field must be
planted, read back and shown to move the solve first.

## band_interaction: acts_on_k_magnitude — SUPERVISOR RULED 2026-09-07

The drafting lane left this `unknown` and flagged it, exactly as the TBRF lane did. The
supervisor RULED `acts_on_k_magnitude` on 2026-09-07, after independently verifying printed
p. 12 (200-dpi render): Ling implements the TBNN anisotropy "in the momentum equations and in
the turbulent kinetic energy production term," and a `b` in the k-production term moves the k
**magnitude**, not only the stress **shape** — the identical mechanism on which the TBRF entry
was ruled `acts_on_k_magnitude`. The CHARTER 22.4 item 2 consequence carries over verbatim: a
shelf-D eigenspace band perturbs shape and orientation only (Emory eq. 4 keeps k outside the
bracket) and is silent on the k-magnitude axis this model moves, so quoting such a band as "the
uncertainty of this model" is the error 22.4 item 2 forbids. Any record showing both must state
that overlap.

## What separates this entry from the TBRF entry — the input set

The two share the Pope (1975) tensor basis, but the discriminating fact is the FEATURE INPUT.
Ling's TBNN is fed ONLY the five invariants λ1..λ5 of S and R (Eq. 2, architecture printed
pp. 7–8). Kaandorp's TBRF (2020) extended the feature set to 47 invariants plus nine physical
features (grad(k), grad(p), wall distance). Because the five Pope invariants collapse in the
square duct (Kaandorp's finding), TBNN-on-λ1..λ5 is more exposed on the duct than the
full-feature TBRF is — this is recorded in `contraindications` (4) and `what_it_cannot_see`, and
it is the single most useful thing this entry adds to the library beyond "the 2016 predecessor."

## Duct relevance

Like the TBRF entry, this is directly relevant to the library's square-duct ladder target:
Ling's headline a-priori and a-posteriori demonstrations are both on the duct (test at
Re_b = 2000), and reference DUCT data is on this box. It is also far from runnable here —
nothing is built, and the paper's solver is proprietary. **Flow-class relevant, capability
absent.**

## Readers used

Page 1 read by closure-supervisor (rule 15). Equation and results pages read as 200-dpi PNG
renders (`pdftoppm -r 200`), one page per image, printed footer confirmed on each (pp. 4, 5-6,
7, 8, 9, 11, 12, 13). `pdftotext`/`/bin/grep` over the explicit sidecar path
`docs/papers/closure/Ling2016_tbnn_embedded_invariance.txt` were used ONLY to locate pages
(L-486: the closure-corpus sidecars are invisible to this box's default ugrep under .gitignore).
