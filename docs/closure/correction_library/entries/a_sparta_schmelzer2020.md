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
  docs/papers/closure/Schmelzer2020_algebraic_reynolds.pdf. READER DISCLOSURE: every
  equation below was read off a 200-dpi (Eqs. 25-27 also 450-dpi) PNG render of the named
  printed page, produced with `pdftoppm -r 200 -f <page> -l <page> -png`. `pdftotext` was
  used only to LOCATE pages: on this file it mangles superscripts -- it renders Eq. (25)'s
  `24.94 I_1^2` as `24.94I12` -- and no symbol here was taken from it.

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
  "k-corrective-frozen-RANS" procedure (printed p. 5). The remaining k-omega SST terms
  (CD_kom, F_1, F_2, the blend Phi = F_1 Phi_1 + (1-F_1) Phi_2) are Eq. (6), printed
  p. 5, and the blended coefficients are Eq. (7), printed p. 6:
      alpha = (5/9, 0.44), beta = (3/40, 0.0828), sigma_k = (0.85, 1.0),
      sigma_om = (0.5, 0.856),  with beta* = 0.09, a_1 = 0.31, S = sqrt(2 S_ij S_ij).

  (3) THE ANSATZ THE REGRESSION SEARCHES -- Eq. (8), printed p. 6, the Pope (1975)
  integrity basis:
      b_ij(S_ij, Omega_ij) = SUM_{n=1..N} T_ij^(n) alpha_n( I_1, ..., I_5 )
  with S_ij = tau (1/2)( d_j U_i + d_i U_j ), Omega_ij = tau (1/2)( d_j U_i - d_i U_j ),
  timescale tau = 1/omega, and alpha_n the scalar coefficient functions that elastic-net
  symbolic regression makes sparse (printed p. 6, verbatim: "The Cayley-Hamilton theorem
  then dictates that the most general form of the anisotropic part of the Reynolds-stress
  can be expressed as").

  (4) THE BASIS AND INVARIANTS ACTUALLY USED -- and it is NOT the full Pope set. Printed
  p. 8, verbatim: "with ten nonlinear base tensors T_ij^(n) and five corresponding
  invariants I_m. Only the first four base tensors and the first two invariants are used
  in this work, which are" -- Eq. (9), printed p. 8:
      T_ij^(1) = S_ij
      T_ij^(2) = S_ik Omega_kj - Omega_ik S_kj
      T_ij^(3) = S_ik S_kj     - (1/3) delta_ij S_mn S_nm
      T_ij^(4) = Omega_ik Omega_kj - (1/3) delta_ij Omega_mn Omega_nm
  and Eq. (10), printed p. 8:
      I_1 = S_mn S_nm ,   I_2 = Omega_mn Omega_nm

  (5) THE MODELLING ANSATZ FOR R -- Eq. (11), printed p. 8:
      R = 2 k b_ij^R d_j U_i
  i.e. R is modelled in the same nonlinear-eddy-viscosity framework as b^Delta, through
  its own coefficient tensor b_ij^R. Printed p. 8, verbatim: "Depending on the local sign
  of R it either increases or decreases the net production P_k locally. Hence, it acts as
  an additional production or dissipation term, which can overcome the error in k."

  (6) THE CANDIDATE LIBRARY THE REGRESSION SEARCHES -- Eq. (12), printed p. 9, the raw
  feature vector (primitive features squared, then multiplied pairwise, max degree 6,
  plus a constant c), cardinality |B| = 16:
      B = [ c, I_1, I_2, I_1^2, I_2^2, I_1^2 I_2^3, I_1^4 I_2, I_1 I_2^2, I_1 I_2^3,
            I_1 I_2^4, I_1^3 I_2, I_1^2 I_2^4, I_1^2 I_2, I_1 I_2, I_1^3 I_2^2,
            I_1^2 I_2^2 ]^T
  Eq. (13), printed p. 9, multiplies each member of B by each base tensor:
      C_bDelta = [ c T_ij^(1), c T_ij^(2), ..., I_1^2 I_2^2 T_ij^(4) ]^T
  Eq. (14), printed p. 9, double-contracts each of those with the mean velocity gradient:
      C_R = [ c T_ij^(1) d_j U_i, ..., I_1^2 I_2^2 T_ij^(4) d_j U_i ]^T
  A discovered model is the dot product of the inferred coefficient vector with that
  library, Eq. (24), printed p. 13: M_Delta := C_Delta^T Theta_Delta^d.

  (7) THE PUBLISHED DISCOVERED MODELS -- Eqs. (25), (26) and (27), all printed p. 21.
  Printed p. 21, verbatim: "Given this cross-validation assessment we select models
  M^(i) = ( M_bDelta^(i), M_R^(i) )^T based on the lowest eps(U) per case".
  NOTATION, READ FROM THE PAGE AND FLAGGED: the superscript on an I is an EXPONENT --
  the paper writes exponent 1 explicitly, e.g. `2.65 I_2^1`. The paper does NOT restate
  that convention beside Eqs. (25)-(27); this lane reads it from the candidate library
  B in Eq. (12), p. 9, whose members are exactly such powers of I_1 and I_2. Read the
  superscripts as exponents on that basis, not on the paper's own say-so.
      M_bDelta^(1) = ( 24.94 I_1^2 + 2.65 I_2^1 ) T_ij^(1)  +  2.96 T_ij^(2)
                     + ( 2.49 I_2^1 + 20.05 ) T_ij^(3)
                     + ( 2.49 I_1^1 + 14.93 ) T_ij^(4)
      M_R^(1)      = 0.4 T_ij^(1)                                            [Eq. (25)]

      M_bDelta^(2) = T_ij^(1) ( 0.46 I_1^2 + 11.68 I_2^1 - 0.30 I_2^2 + 0.37 )
                     + T_ij^(2) ( -12.25 I_1^1 - 0.63 I_2^2 + 8.23 )
                     + T_ij^(3) ( -1.36 I_2^1 - 2.44 )
                     + T_ij^(4) ( -1.36 I_1^1 + 0.41 I_2^1 - 6.52 )
      M_R^(2)      = 1.4 T_ij^(1)                                            [Eq. (26)]

      M_bDelta^(3) = T_1 ( 0.11 I_1^1 I_2^1 + 0.27 I_1^1 I_2^2 - 0.13 I_1^1 I_2^3
                           + 0.07 I_1^1 I_2^4 + 17.48 I_1^1 + 0.01 I_1^2 I_2^1
                           + 1.251 I_1^2 + 3.67 I_2^1 + 7.52 I_2^2 - 0.3 )
                     + T_2 ( 0.17 I_1^1 I_2^2 - 0.16 I_1^1 I_2^3 - 36.25 I_1^1
                             - 2.39 I_1^2 + 19.22 I_2^1 + 7.04 )
                     + T_3 ( -0.22 I_1^2 + 1.8 I_2^1 + 0.07 I_2^2 + 2.65 )
                     + T_4 ( 0.2 I_1^2 - 5.23 I_2^1 - 2.93 )
      M_R^(3)      = 0.93 T_ij^(1)                                           [Eq. (27)]
  TWO THINGS READ EXACTLY AS PRINTED AND NOT TIDIED. (a) Eq. (27) writes its basis
  tensors as `T_1 ... T_4` -- subscript index, no `ij` -- while Eqs. (25) and (26) write
  `T_ij^(1) ... T_ij^(4)`. That is the paper's own inconsistency, not a transcription
  slip; they are the same four tensors of Eq. (9), p. 8. (b) In Eq. (27) the term reads
  `1.251I_1^2` on the page. The coefficient is 1.251 and the exponent is 2 -- the digit
  1 belongs to the coefficient, not to a separate `1I` -- read at 450 dpi. If a
  reproduction ever disagrees at this term, re-read the page before adjusting the model.

  R MODEL SHAPE, printed p. 15, verbatim: "We identify T_ij^(1), I_1 T_ij^(1) and
  I_2 T_ij^(1) as the relevant candidates to regress R, and models combining all three
  give the lowest error per test case." All three published M_R above are in fact single
  terms c T_ij^(1).

  WHAT IS STILL NOT READ, NAMED EXACTLY -- and none of it is a model equation. The
  equation-level gap this entry carried until 2026-09-04 is CLOSED: every equation the
  paper publishes for the MODEL (Eqs. 2-14, 24-27) is transcribed above with its number
  and its printed page. Three things were deliberately not transcribed and a reader
  should know which:
  (a) THE DISCOVERY MACHINERY, Eqs. (15)-(23), printed pp. 10-13 -- the elastic-net /
  ridge inference that PRODUCED the coefficients. Reproducing the published models
  M^(1)..M^(3) does not need them; re-deriving new SpaRTA models does. Not read.
  (b) THE HAND-SELECTED ENSEMBLE IS NOT PUBLISHED AS EQUATIONS AT ALL. The paper
  hand-selected 5 models for b^Delta and 3 for R per training case (1 for CBFS13700),
  printed p. 15, and shows that ensemble only as scatter plots with token labels in
  Figures 4, 5 and 7. Those figure labels were not transcribed. Only the three SELECTED
  models are published as equations, and they are above in full.
  (c) WHICH TRAINING CASE PRODUCED M^(1) AND M^(3) IS NOT STATED ON ANY PAGE THIS LANE
  READ. Printed p. 22 states only that M^(2) "was identified using PH10595 as training
  data". Table 2, printed p. 15, leaves one cell blank per model -- M^(1) under
  CBFS13700, M^(2) under PH10595, M^(3) under CD12600 -- which WOULD assign M^(1) to
  CBFS13700 and M^(3) to CD12600, and the M^(2) row corroborates that reading. But the
  caption does not say the blank means "training case", so that mapping is this lane's
  INFERENCE from one corroborated row and must not be quoted as the paper's statement.
  A reproduction needing the attribution must resolve it from Figure 7 or the authors'
  code, not from this entry.
  The numbers currently on this box are still the LAB'S OWN discovered coefficients, not
  Schmelzer's -- see contraindications (1). That is an implementation gap, not a reading
  gap, and it is what keeps this entry at REGISTERED.
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
    Eqs. (2)-(6) on printed p. 5; Eqs. (7) and (8) on printed p. 6; Eqs. (9), (10) and
    (11) on printed p. 8; Eqs. (12), (13) and (14) on printed p. 9; Eq. (24) and the
    xi = 0.1 statement of Section 3.3 on printed p. 13; Table 2 on printed p. 15; the
    error discussion and the "5 times better" claim on printed p. 20; Eqs. (25), (26)
    and (27) -- the published discovered models -- on printed p. 21; the Re = 37000 true
    prediction and Section 6 on printed p. 22. All of
    Schmelzer2020_algebraic_reynolds.pdf. Printed page numbers were confirmed by reading
    the page footer on each rendered page image, not inferred: PDF page number equals
    printed page number throughout this file. Reader: `pdftoppm -r 200` (Eqs. 25-27 also
    at 450 dpi) then visual read of the PNG. `pdftotext` was used for NAVIGATION ONLY --
    on this file it drops superscripts and would have turned Eq. (25) into nonsense.
claimed_effect: >-
  The paper's own claim, quoted from the abstract, printed p. 1: "The predictions of the
  discovered models are significantly improved over the k-omega SST also for a true
  prediction of the flow over periodic hills at Re=37000." Model discovery and
  cross-validation were performed on "three cases of separating flows, i.e. periodic
  hills (Re=10595), converging-diverging channel (Re=12600) and curved backward-facing
  step (Re=13700)" (abstract, p. 1).

  PAGE CORRECTION, 2026-09-04: an earlier revision of this entry attributed the
  results-discussion quote below to "printed p. 22 region, §4". IT IS ON PRINTED p. 20,
  in Section 5, and §4 is Test Cases, not Results. The quote itself is verbatim correct;
  the page and section were wrong and are corrected here. Printed p. 20, verbatim: "Most
  of the models show a good or even substantial improvement over the baseline. But, for
  the set of models, only providing a correction for b_ij^Delta, most but not all lead
  to an improvement of the resulting velocity field. In contrast to that, if only a
  correction for R is deployed, the result is a consistent, substantial improvement
  across all test cases."

  THE NUMBERS, now extracted -- a previous revision said none had been. Table 2, printed
  p. 15, gives the normalised mean-squared velocity error eps(U)/eps(U^o) of the three
  selected models, one column per test case (baseline k-omega SST is 1.0 by
  construction), with the model's cross-validation rank in brackets:
      M^(1): PH10595 (1.)  0.22287 | CD12600 (19.) 0.21146 | CBFS13700  -    0.30413
      M^(2): PH10595  -    0.38867 | CD12600 (1.)  0.20828 | CBFS13700 (26.) 0.40154
      M^(3): PH10595 (3.)  0.22744 | CD12600  -    0.22422 | CBFS13700 (1.)  0.30655
  Printed p. 20, verbatim: "It can be observered, that the best models correct the
  velocity up to 5 times better in mean-squared error than the k-omega SST baseline
  model." (the spelling "observered" is the paper's, re-read at 450 dpi to be sure it is
  not a transcription slip of this lane's.) Printed p. 21, verbatim, on the three
  selected models: "they are still within the set of well-performing models with
  eps(U)/eps(U^o) < 0.5".

  THE CEILING THE CORRECTION CANNOT BEAT is also published, and a reproduction should
  quote it beside any result. Table 1, printed p. 6, gives the error left when the
  frozen b^Delta and R fields are inserted as STATIC fields -- i.e. the best a perfectly
  regressed model could do: eps(U_i)/eps(U_i^o) = 0.00165 (PH10595), 0.0229 (CD12600),
  0.22703 (CBFS13700); eps(tau_ij)/eps(tau_ij^o) = 0.1495, 0.4781, 0.4949 respectively.
  Printed p. 20, verbatim: "This leaves still room for further improvement compared to
  the error using the frozen data sets, see Table 1."

  THE Re = 37000 EXTRAPOLATION CLAIM CARRIES NO NUMBER. Printed p. 22, verbatim: "For
  this true prediction throughout the domain the three models improve significantly
  compared to the baseline. Interestingly, the model M^(2) is delivering the best fit of
  the data and the others tend to slightly underestimate it. Thus, taking the results of
  the cross-validation on the low-Re cases into account, the models show a weak
  Re-dependence, but overall robustness between the cases." No error figure is given for
  PH37000 -- Figure 12 is the only evidence -- so a reproduction may compare profiles
  there but may NOT quote a numeric improvement for that case.
paper_validation_cases: >-
  FOUR CASES, three for discovery/cross-validation and one for the true prediction. All
  printed pp. 13-14 (Section 4) unless noted.
  (a) PH10595 -- periodic hills, Re = 10595 on bulk inlet velocity and hill height, LES
  data of Breuer et al. 2009 (reference [33]; Figure 2(a) legend, printed p. 7). Mesh
  120 x 130 cells, cyclic inlet/outlet, driven by a volume forcing to constant bulk
  velocity.
  (b) CD12600 -- converging-diverging channel with an asymmetric bump under adverse
  pressure gradient, Re = 12600 on channel half-height and maximum inlet velocity, DNS
  of reference [35]; Figure 2(b) legend, printed p. 7, cites it as "Laval and
  Marquillie, 2010". Mesh 140 x 100 cells; inlet from a channel-flow simulation at
  equivalent Re. NO id exists for this case in SCHEMA §3, and none is coined.
  (c) CBFS13700 -- curved backward-facing step, Re = 13700 on step height and
  centre-channel inlet velocity, LES of reference [36]; Figure 2(c) legend, printed p. 7,
  cites it as "Bentaleb et al., 2012". Mesh 140 x 150 cells; inlet from a fully-developed
  boundary-layer simulation.
  (d) PH37000 -- periodic hills at Re = 37000, the TRUE-PREDICTION case, printed p. 13.
  Its reference data is EXPERIMENTAL (reference [34]), not LES/DNS, and it is outside the
  training range by construction. This is the paper's generalisation guard and dropping
  it flatters the entry (SCHEMA Addendum 1 item 3). NO id exists for it in SCHEMA §3.
  The lab holds an id only for (a) and (c); `validation_cases` lists exactly those two.
  Simulation counts, printed p. 15: 35 cross-validation runs each for PH10595 and
  CD12600 and 47 for CBFS13700, including the uncorrected k-omega SST baseline.
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
  SIX, five of them stated by the paper itself.

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

  (2) b^Delta IS THE ONLY TERM THAT CAN BREAK CONVERGENCE, AND IS DAMPED BY TEN WHEN IT
  DOES. QUOTE CORRECTED 2026-09-04: an earlier revision of this entry quoted the paper as
  saying "b_ij^Delta needs to be scaled with xi = 0.1 to achieve convergence, see Section
  3.3". That fragment is cut out of a CONDITIONAL sentence on printed p. 20, whose full
  text is: "Whether the correction for b_ij^Delta needs to be scaled with xi = 0.1 to
  achieve convergence, see Section 3.3, is indicated by a black marker edge." The paper
  does not say the scaling is always needed; it says a figure marker records which models
  needed it. The governing statement is Section 3.3, printed p. 13, verbatim: "we have
  identified corrections of b_ij^Delta as the only contribution which can do harm to the
  convergence properties for the given test cases. Therefore, if a model does not
  converge, we further decrease the coefficients by a factor xi = 0.1, for the model
  correcting b_ij^Delta only. This ad-hoc intervention is sufficient to achieve
  convergence for the studied cases." The contraindication stands and is if anything
  sharper: b^Delta is named as the sole convergence hazard, the remedy is ad-hoc, and any
  reproduction must report whether xi was applied and to which model. Also printed p. 13:
  "the identified models are also not guaranteed to converge a priori for any other test
  case outside the training set."

  (3) THE b^Delta CORRECTION ALONE OFTEN DOES NOT HELP. Printed p. 20, verbatim: "for the
  set of models, only providing a correction for b_ij^Delta, most but not all lead to an
  improvement of the resulting velocity field."

  (4) COMBINING BOTH CORRECTIONS IS NOT UNIFORMLY BETTER. Printed p. 20, verbatim: "Using
  both a model for b_ij^Delta and R leads to a further improvement, except for test case
  CBFS13700." And the paper reports its own selection surprise, same page: "Surprisingly,
  the best model per test case is not always identified on the associated training data.
  While this expectation holds for the cases CBFS13700 and CD12600 it is not true for
  PH10595, for which the other two training sets deliver significantly better performing
  models."

  (5) THE PUBLISHED MODELS ARE FITTED ON ONLY TWO INVARIANTS AND FOUR BASIS TENSORS, so
  they are not the general Pope ansatz they are introduced as. Printed p. 8, verbatim:
  "Only the first four base tensors and the first two invariants are used in this work".
  Eqs. (25)-(27) contain no T^(5)..T^(10) and no I_3, I_4, I_5. A reproduction that
  implements the full ten-term basis is NOT implementing this paper's models.

  (6) M^(2) IS A DOCUMENTED FAILURE MODE OF THE FAMILY, not a spare option. Printed
  p. 22, verbatim: "Model M^(2) tends to overestimate the magnitude of the quantities U,
  k and tau_xy and therefore predicts smaller or no separation bubbles. This model was
  identified using PH10595 as training data and, ignoring the specific structure for
  b_ij^Delta, has the largest coefficient for correcting R, see (26), which leads to
  larger k compared to the others, which is the reason for the systematic
  over-prediction." Same page, on CD12600: "the model M^(2) ignores it entirely" (the
  recirculation zone). Yet on the Re = 37000 true prediction the paper reports M^(2) as
  the BEST fit -- so model rank does not transfer across Re, and a reproduction may not
  pick one of the three on another case's ranking.
what_it_cannot_see: >-
  NARROWED 2026-09-04 by reading Eqs. (9) and (10), printed p. 8: an earlier revision of
  this entry said the ansatz is a function of "S_ij, Omega_ij and their five invariants".
  IT IS NOT. The paper uses only the FIRST FOUR base tensors and the FIRST TWO invariants
  (printed p. 8, verbatim: "Only the first four base tensors and the first two invariants
  are used in this work"), and by Eq. (10) those two are I_1 = S_mn S_nm and
  I_2 = Omega_mn Omega_nm -- both squared magnitudes. So the blindness is STRICTLY WORSE
  than the earlier text claimed: with I_3, I_4 and I_5 absent, the discovered models
  carry no invariant that mixes S and Omega beyond second order, and cannot see the
  relative ORIENTATION of strain and rotation, only their separate magnitudes. The
  discovered coefficient functions in Eqs. (25)-(27) are polynomials in exactly those two
  scalars.

  Beyond that: the ansatz (Eq. 8, p. 6) is a LOCAL algebraic function of the mean
  velocity gradient, so it is blind to everything not encoded there: history, upstream
  separation state, and non-local pressure effects. Eq. (8)
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
