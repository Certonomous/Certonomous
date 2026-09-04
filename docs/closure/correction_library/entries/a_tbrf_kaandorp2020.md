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
  on Pope's (1975) integrity basis, and the predicted anisotropy is then blended into the
  momentum equation and into a modified k-equation inside a RANS solve. Transcribed from
  docs/papers/closure/Kaandorp2020_random_forests.pdf. READER DISCLOSURE: every equation
  below was read off a 200-dpi PNG render of the named printed page, produced with
  `pdftoppm -r 200 -f <page> -l <page> -png`; `pdftotext` was used only to locate pages.
  PDF page number equals printed page number throughout this file, confirmed by reading
  the footer on each rendered page.

  (1) NORMALISED STRAIN AND ROTATION -- Eq. (7), printed p. 15:
      S = (1/2)(k/eps)( grad u + grad u^T ) ,   R = (1/2)(k/eps)( grad u - grad u^T )
  i.e. the normalisation timescale is k/eps, NOT 1/omega, even though the RANS
  simulations themselves use k-omega (printed p. 24).

  (2) THE TENSOR-BASIS REPRESENTATION -- Eq. (8), printed p. 15:
      b = h(S, R) = SUM_{m=1..10} T^(m)(S, R) * g^(m)( theta_1, ..., theta_5 )
  printed p. 15, verbatim: "In this case (Pope, 1975) there are 10 integrity basis
  tensors T^(m), making the most general expression for b:" ... "where g^(m) are scalar
  functions of the invariants theta_i."

  (3) THE TEN-TERM BASIS IN FULL -- printed p. 16. PAGE AND NUMBER CORRECTION: an earlier
  revision of this entry placed the basis on p. 15; it is on p. 16, and IT CARRIES NO
  EQUATION NUMBER. It is a displayed two-column array between Eq. (8) (p. 15) and Eq. (9)
  (p. 18), introduced by "The basis tensors derived from S and R are (Pope, 1975):".
  Quoting an equation number for it would be inventing one.
      T^(1) = S                                  T^(6)  = R^2 S + S R^2
                                                          - (2/3) I . trace(S R^2)
      T^(2) = S R - R S                          T^(7)  = R S R^2 - R^2 S R
      T^(3) = S^2 - (1/3) I . trace(S^2)         T^(8)  = S R S^2 - S^2 R S
      T^(4) = R^2 - (1/3) I . trace(R^2)         T^(9)  = R^2 S^2 + S^2 R^2
                                                          - (2/3) I . trace(S^2 R^2)
      T^(5) = R S^2 - S^2 R                      T^(10) = R S^2 R^2 - R^2 S^2 R

  (4) THE FIVE INVARIANTS IN FULL -- printed p. 16, ALSO UNNUMBERED, introduced by "with
  invariants":
      theta_1 = trace(S^2) ,  theta_2 = trace(R^2) ,  theta_3 = trace(S^3) ,
      theta_4 = trace(R^2 S) ,  theta_5 = trace(R^2 S^2)

  (5) BUT theta_1..theta_5 ARE NOT THE FEATURE SET ACTUALLY USED. Printed p. 16,
  verbatim: "In Wang et al. (2017) this approach is extended to derive a set of 47
  invariants based on grad(u_bar), grad(k), and grad(p). This is the system we use in
  the following; the full feature-set will be shown in Section 2.6." Printed p. 23,
  verbatim: "Therefore here we will use the full set of invariants derived from S, R,
  and grad(k) from Wang et al. (2017)", with grad(k) first normalised by sqrt(k)/eps and
  turned into an antisymmetric tensor, Eq. (13), printed p. 23:
      A_k = - I x grad(k)
  Same page, verbatim: "Furthermore nine extra scalar features which are more physically
  interpretable, such as the wall-distance based Reynolds number are used, which were
  obtained from Wu et al. (2016)". The features actually used are Table 1, printed p. 25,
  in three sets:
      FS1 -- traces of S^2, S^3, R^2, R^2 S, R^2 S^2, R^2 S R S^2. No normalisation
             column. "Invariant set based on S and R".
      FS2 -- adds ten invariants built with A_k: A_k^2, A_k^2 S, A_k^2 S^2,
             A_k^2 S A_k S^2, R A_k, R A_k S, R A_k S^2, R^2 A_k S*, R^2 A_k S^2*,
             R^2 S A_k S^2*  (the * means all cyclic permutations of anti-symmetric
             tensor labels are taken; FS1 and FS2 take the trace of each quantity).
      FS3 -- nine scalar features with explicit normalisations, each with the paper's own
             one-line meaning: (1/2)(||R||^2 - ||S||^2) over ||S||^2, "Ratio of excess
             rotation rate to strain rate"; k over (1/2) u_i u_i, "Turbulence intensity";
             min( sqrt(k) d / (50 nu), 2 ), unnormalised, "Wall-distance based Reynolds
             number"; u_k dp/dx_k over sqrt( (dp/dx_j)(dp/dx_j) u_i u_i ), "Pressure
             gradient along streamline"; (k/eps) over (1/||S||), "Ratio of turbulent time
             scale to mean strain time scale"; sqrt( (dp/dx_i)(dp/dx_i) ) over
             (1/2) rho (d/dx_k) u_k^2, "Ratio of pressure normal stresses to shear
             stresses"; u_i dk/dx_i over |u'_j u'_k S_jk|, "Ratio of convection to
             production of TKE"; ||u'_i u'_j|| over k, "Ratio of total to normal Reynolds
             stresses"; | u_i u_j du_i/dx_j | over sqrt( u_l u_l u_i du_i/dx_j u_k
             du_k/dx_j ), "Non-orthogonality between velocity and its gradient".
  Table 1's own caption, printed p. 25: features marked with a dagger are "rotationally
  invariant but not Galilean invariant" -- k, u_k dp/dx_k, u_i dk/dx_i and the
  non-orthogonality feature carry that dagger. In the reported runs 17 features survived
  a low-variance filter (Table 2, printed p. 31; features with variance < 1e-4 were
  discarded, printed p. 30).

  (6) WHAT IS LEARNED -- and there is NO closed form, BY CONSTRUCTION. The g^(m) are the
  output of a Tensor Basis Random Forest: an ensemble of tensor-basis decision trees,
  each leaf holding ten constant coefficients. The split rule is Eq. (9), printed p. 18:
      R_L(j,s) = { X | [X]_j <= s } ,   R_R(j,s) = { X | [X]_j > s }
  printed p. 18, verbatim: "For the TBDT, constant values are chosen for the tensor basis
  coefficients". The split objective is Eq. (10), printed p. 19, a Frobenius-norm cost
  summed over both bins:
      J = SUM_{x_i in R_L} || SUM_{m=1..10} T_i^(m) g_L^(m) - b_i ||_F^2
        + SUM_{x_i in R_R} || SUM_{m=1..10} T_i^(m) g_R^(m) - b_i ||_F^2
  and, printed p. 19, verbatim: "It can be shown by setting the derivative of J with
  respect to g^(m) in each bin to zero, the optimum value for the 10 tensor basis
  coefficients in each bin is found using" -- Eq. (11), printed p. 19:
      g = ( SUM_{i=1..N} That_i^T That_i )^-1 ( SUM_{i=1..N} That_i^T bhat_i )
  where That_i (9 x 10) and bhat_i (9 x 1) are the flattened basis tensors and reference
  anisotropy, Eq. (12), printed p. 19. Eq. (11) can be ill-posed (printed p. 20), and the
  Appendix, printed p. 54 ("Appendix: TBRF implementation details"), restates the same
  solve with ridge regularisation, Eq. (23), printed p. 56:
      g = ( SUM That_i^T That_i + Gamma I )^-1 ( SUM That_i^T bhat_i )
  with Gamma = 1e-12 in the reported runs (printed p. 30). The forest prediction is a
  MEDIAN, not a mean -- printed p. 21, verbatim: "Instead of taking the mean over all the
  tensor basis decision trees, it proved to be more successful to take the median of the
  trees in the random forest."

  (7) PROPAGATION INTO THE MOMENTUM EQUATION, and the RELAXATION -- Section 2.7, printed
  p. 24. Eq. (14), printed p. 24, is the RANS momentum equation:
      d(u_bar)/dt + u_bar . grad(u_bar) = div[ -p_bar + nu Shat - tau ]
  and Eq. (15), printed p. 24, is how the ML prediction enters it:
      tau  ~=  tau_ML(gamma) := (2/3) k I + 2k[ (1 - gamma) b_B + gamma b_ML ]
  with b_B := nu_t Shat the Boussinesq anisotropy and gamma in [0,1] a relaxation
  parameter. Printed p. 24, verbatim: "Simply setting the prediction of the anisotropy
  tensor b_ML in the momentum equation adversely affects the numerical stability of the
  solver."

  (8) THE CONTINUATION METHOD, printed p. 26, an UNNUMBERED displayed equation -- a
  linear ramp on gamma against the SIMPLE iteration count n:
      gamma_n = gamma_max min{ 1 , n / n_max }
  Printed p. 26, verbatim: "The blending parameter gamma starts at 0 and is gradually
  increased during the simulation, i.e. a continuation method"; "gamma_max >= 0.8 is
  achieved in all test-cases presented here, and n_max is the iteration count, after
  which gamma is fixed"; "gamma_max was incremented in steps of 0.1 until the solver
  became unstable, yielding a value of gamma_max = 0.8. As this choice is ad hoc, further
  work related to this topic is necessary." Note gamma_max = 0.8 means the CONVERGED
  solution is 20 percent Boussinesq by construction, and the paper says so: "A lower
  value for gamma means that the linear eddy viscosity assumption becomes more dominant,
  resulting in a more stable solution, but impairing the accuracy of the solved mean
  velocity."

  (9) THE MODIFIED k-EQUATION, printed p. 26. The k-omega k-equation is retained but its
  PRODUCTION term is recomputed from the ML stress. Eq. (16), printed p. 26, is the exact
  production
      P = - tau : grad(u_bar)
  and, printed p. 26, verbatim: "is approximated in the k-omega model by replacing tau
  with its Boussinesq approximation (Wilcox, 2008). Here we use the model tau_ML from
  (15) instead, including the blending with gamma." So the modification is exactly:
  substitute tau_ML(gamma) of Eq. (15) for the Boussinesq stress in P, leaving the rest
  of the k-omega k-equation alone. Printed p. 26, verbatim on why: "the production term
  is modified to be consistent with the predicted Reynolds stress in the momentum
  equation." Printed p. 27: "With these modifications, the solver converges for b-tensors
  originating from DNS, TBNN and TBRF."

  READING THAT CONTRADICTS THIS ENTRY'S OWN `band_interaction: does_not`, FLAGGED AND NOT
  SILENTLY RESOLVED. Eq. (16) with tau -> tau_ML makes the k PRODUCTION an explicit
  function of b_ML. The ML anisotropy therefore moves the k MAGNITUDE through the
  k-equation, not only the stress SHAPE, and the paper's own justification for the change
  is consistency, not stability alone. `band_interaction` is a declared machine field
  outside this lane's brief and has NOT been changed here; the reading is recorded so the
  supervisor can rule on it. See the prose section "band_interaction: does_not" below,
  which anticipated exactly this and set the condition for revision.

  (10) SOLVER-SIDE REQUIREMENT, from the abstract, printed p. 1, verbatim: "The resulting
  predictions of turbulence anisotropy are used as a turbulence model within a custom
  RANS solver. Stabilization of this solver is necessary, and is achieved by a
  continuation method and a modified k-equation."

  WHAT IS STILL NOT READ, NAMED EXACTLY. The equation-level gap this entry carried until
  2026-09-04 is CLOSED: the ten-term basis, the five invariants, the full feature table,
  the continuation method and the modified k-equation are all transcribed above with
  their printed page, and with an explicit note wherever the paper gives NO equation
  number. Two things were deliberately not transcribed: (a) Eqs. (17)-(22), printed
  pp. 54-56, the Appendix restatement of the CART split and of Eqs. (10)-(12) -- read as
  a restatement, so only Eq. (23), the one that adds Gamma, is quoted above; and (b) the
  numerical CONTENT of the trained forest. There is no closed-form g^(m) to transcribe BY
  CONSTRUCTION: the model is 100 trained trees (printed p. 30), and reproducing it needs
  the serialised forest, not an equation. That is a property of the method, not a gap in
  this reading.
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
    Of Kaandorp2020_random_forests.pdf, all read as 200-dpi page images and all confirmed
    against the printed footer of the page (PDF page number equals printed page number
    throughout this file): Eqs. (7) and (8) on printed p. 15; the ten-term basis and the
    five invariants theta_1..theta_5 on printed p. 16, BOTH UNNUMBERED in the paper;
    Eq. (9) on printed p. 18; Eqs. (10), (11) and (12) on printed p. 19; the median-
    over-trees statement on printed p. 21; Eq. (13) on printed p. 23; Eqs. (14) and (15)
    on printed p. 24; the feature table (Table 1) on printed p. 25; the continuation ramp
    (UNNUMBERED) and Eq. (16), the modified k-equation production, on printed p. 26;
    Eq. (23), the ridge-regularised leaf solve, on printed p. 56 of the Appendix that
    opens on printed p. 54. Supporting non-equation material: abstract, printed p. 1;
    flow-case list, printed pp. 27-28; run settings, printed p. 30; training/prediction
    split (Table 2), printed p. 31; square-duct anisotropy RMSE (Table 3), printed p. 37;
    backward-facing-step reattachment (Table 4), printed p. 41.
    PAGE CORRECTIONS made 2026-09-04 against an earlier revision of this entry: the
    ten-term basis is on p. 16, not p. 15; Table 2 (training/test split) is on p. 31, not
    "p. 28 region"; and the realizability and shear-layer passages are on p. 35, not
    "p. 34".
claimed_effect: >-
  The paper's own claims, quoted. Abstract, printed p. 1: "The algorithm is trained on
  several flow cases using DNS/LES data, and used to predict the Reynolds stress
  anisotropy tensor for new, unseen flows. ... Results are compared to the neural network
  approach of Ling et al. [J. Fluid Mech, 807(2016):155-...]". Abstract, printed p. 1:
  "...square duct flow case and a backward facing step flow case show good agreement with
  DNS and experimental data-sets."

  PAGE CORRECTION, 2026-09-04: the realizability passage below was cited by an earlier
  revision of this entry as "printed p. 34". IT IS ON PRINTED p. 35, in Section 3.2.2,
  and the case being discussed is the BACKWARD-FACING STEP (BFS5100), not a generic
  flow. The quotes are verbatim correct; the page and the case were not stated. Printed
  p. 35, verbatim: "In all our studies, we have never observed unrealizable predictions
  from TBRF, despite no explicit realizability constraint being imposed on the method" --
  and, in the same passage, TBNN outperforms TBRF at three of five stations "at the cost
  of some unrealizable predictions closest to the wall."

  THE NUMBERS, now extracted -- a previous revision said none had been.
  (a) ANISOTROPY ACCURACY ON THE SQUARE DUCT, Table 3, printed p. 37: RMSE of the [b]_ij
  prediction against DNS. Case C3 (FS1 only, 5 features): TBRF 0.0995, TBNN 0.0871.
  Case C4 (FS1+FS2+FS3, 17 features): TBRF 0.0521, TBNN 0.0681. TBRF is therefore BEATEN
  BY TBNN in the FS1-only case and beats it only once the extra feature sets are added --
  the paper's own reading, printed p. 37, is that "the introduction of extra features has
  significantly more effect than the choice of neural-networks versus random-forests"
  (printed p. 36).
  (b) A-POSTERIORI ACCURACY ON THE BACKWARD-FACING STEP, Table 4, printed p. 41,
  reattachment location x_reattach in x/h: baseline RANS 5.45; RANS + b_ij,TBRF 6.32;
  DNS (Le et al., 1997) 6.28; Experiment (Jovic and Driver, 1994) 6.0 +/- 0.15. Printed
  p. 41, verbatim: "A significant improvement is shown for the propagated velocity field
  compared to the baseline RANS simulation", and on skin friction: "The propagated flow
  field shows a very close match to the experimental data, and the majority of results
  fall within the error bounds given by the experiment (+/-0.0005 c_f)."
  (c) A-POSTERIORI ON THE SQUARE DUCT THERE IS NO NUMBER -- only profile plots, Figure
  10, printed p. 40, and a qualitative reading, printed pp. 39-40: propagating the DNS
  anisotropy "broadly reproduce[s] the DNS mean velocity"; substituting the TBRF
  prediction "causes additional errors, but theses errors are of similar magnitude to
  the errors already made in the propagation"; and TBRF "predictions are still far more
  accurate than both non-linear eddy-viscosity models" (Shih et al. 1993 quadratic and
  Lien et al. 1996 cubic). A reproduction may compare profiles for the duct but may NOT
  quote a numeric secondary-flow improvement for it, because the paper publishes none.
  THE PROPAGATION CEILING IS PUBLISHED AND MUST BE QUOTED BESIDE ANY DUCT RESULT. Printed
  p. 39: the DNS anisotropy itself was propagated through the same stabilised solver as a
  "best case scenario where the anisotropy tensor is assumed to be perfect", and it does
  NOT recover the DNS mean flow exactly -- "with the best fit near the wall (z = 1), and
  the worst near the channel centerline (z = 0)". Any TBRF duct error is measured against
  that ceiling, not against DNS.
paper_validation_cases: >-
  FIVE FLOW CASES in the framework, printed pp. 27-28 (Section 3.1), and FOUR
  train/predict configurations, Table 2, printed p. 31. The distinction matters and an
  earlier revision of this entry got it wrong -- see the correction at the end.
  (a) PH -- periodic hills. "Five Reynolds numbers are available in the DNS/LES data-set
  from Breuer et al. (2009), ranging from Re = 700 to Re = 10595 based on the bulk
  velocity at the inlet and the hill height" (printed p. 27).
  (b) CD -- converging-diverging channel, "DNS data ... from Laval and Marquillie (2011)
  at Re = 12600 based on the channel half-height and the maximum velocity at the inlet"
  (printed p. 27). No id exists for this case in SCHEMA §3 and none is coined.
  (c) CBFS -- curved backward-facing step, Re = 13700 on step height and centre-channel
  inlet velocity, "highly resolved LES data from Bentaleb et al. (2012)" (printed p. 28).
  (d) BFS -- backward-facing step, Re = 5100 on step height and free-stream velocity,
  "DNS simulation can be found in Le et al. (1997)" (printed p. 28). Experimental
  comparison is Jovic and Driver (1994), printed p. 41. NO id exists for BFS in SCHEMA §3
  and none is coined -- yet it is the ONLY case for which the paper publishes an
  a-posteriori NUMBER (Table 4), so dropping it flatters the entry (SCHEMA Addendum 1
  item 3).
  (e) SD -- square duct, "Data-sets at multiple Reynolds numbers are available from
  Pinelli et al. (2010), with a total of sixteen ranging from Re = 1100 to Re = 3500
  based on the duct semi-height and the bulk velocity" (printed p. 28).
  THE FOUR CONFIGURATIONS, Table 2, printed p. 31 -- read as an image; every row has the
  SAME training set:
      C1: train PH5600, PH10595, CD12600 -> predict CBFS13700. N_sample 21,000,
          N_feature 17, feature sets FS1+FS2+FS3.
      C2: train PH5600, PH10595, CD12600 -> predict BFS5100.   21,000, 17, FS1+FS2+FS3.
      C3: train PH5600, PH10595, CD12600 -> predict SD3500.    21,000,  5, FS1 only.
      C4: train PH5600, PH10595, CD12600 -> predict SD3500.    21,000, 17, FS1+FS2+FS3.
  Run settings, printed p. 30: 100 TBDTs; 11 of the 17 features drawn at random for each
  split; minimum 9 samples per leaf; Gamma = 1e-12; features with variance < 1e-4
  discarded. For C3 the trees were instead fully grown and all features used at each
  split. Hyperparameters for C1, C2 and C4 were tuned "using a validation set consisting
  of PH2800 and SD3200".
  CORRECTION, 2026-09-04, and it changes what this entry claims: an earlier revision of
  this entry described the square duct as TBRF's TRAINING data ("Its square-duct training
  data is Pinelli et al. (2010) at Re = 1100 to 3500"). IT IS NOT. Table 2 trains every
  reported configuration on periodic hills and the converging-diverging channel ONLY; the
  square duct at Re = 3500 is a PREDICTION case in C3 and C4. The only square-duct data
  that touched the fitting is SD3200 in the hyperparameter validation set. Printed p. 31,
  verbatim on C1: "which is relatively similar to the training cases"; on C2: "which
  features stronger separation than to the training cases and will therefore feature more
  extrapolation". Printed p. 36: "Note that these are challenging cases due to the
  substantial differences between the training and prediction flows."
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
  SIX.

  (1) NOT INSTALLABLE ON THIS BOX. No TBRF turbulence model exists here. The four user
  libraries built in FOAM_USER_LIBBIN register, by symbol table read with `nm -DC` on
  2026-09-04, only `kOmegaSSTQCR`, `kOmegaSSTCorrected`, `kOmegaSSTFrozen` and
  `kOmegaSSTSparta`. TBRF additionally needs a trained forest at run time, which is not
  a coefficient set but a serialised model artifact, and it needs the paper's custom
  solver. `model_type_name` is `none` and `libs_required` is empty for that reason, and
  this entry cannot pass IMPLEMENTED until both exist.

  (2) THE SOLVER DOES NOT CONVERGE WITHOUT DELIBERATE STABILISATION, by the paper's own
  statement, and the stabilisation is ad hoc and costs accuracy. Abstract, printed p. 1,
  verbatim: "Stabilization of this solver is necessary, and is achieved by a continuation
  method and a modified k-equation." Printed p. 24: "Simply setting the prediction of the
  anisotropy tensor b_ML in the momentum equation adversely affects the numerical
  stability of the solver." The schedule is now transcribed in `equation_form` (8): a
  linear ramp gamma_n = gamma_max min{1, n/n_max} with gamma_max = 0.8, which the paper
  reached by incrementing "in steps of 0.1 until the solver became unstable" and calls,
  verbatim, "ad hoc". TWO CONSEQUENCES A REPRODUCTION MUST STATE. First, at gamma_max =
  0.8 the CONVERGED field is 20 percent Boussinesq -- the published result is NOT the
  pure TBRF closure, and the paper says the cost is real: "A lower value for gamma means
  that the linear eddy viscosity assumption becomes more dominant, resulting in a more
  stable solution, but impairing the accuracy of the solved mean velocity." Second,
  gamma_max is a per-case tuned number, so a reproduction must report the gamma_max and
  n_max it actually used or its a-posteriori result is not comparable.

  (3) A NAMED FAILURE IN THE SHEAR LAYER, which the authors do not explain. PAGE AND CASE
  CORRECTED 2026-09-04: an earlier revision cited this as "printed p. 34" without naming
  the case. It is printed p. 35, Section 3.2.2, and the case is the BACKWARD-FACING STEP
  (C2, BFS5100). Verbatim: "Moving away from the wall into the shear layer TBRF
  erroneously heads too far back towards the two-component boundary at the sections
  closest to the step. The reason for this is unclear, at similar (shear-layer) locations
  in the training flows, the turbulence does not exhibit such behaviour. Furthermore TBNN
  is reasonably accurate here. Diagnostic tools are needed, and will be a focus of future
  research." This is a contraindication for near-separation shear layers specifically,
  and it is the one place the paper reports TBRF reaching a WRONG TURBULENCE STATE while
  its neural-network competitor does not.

  (4) A RANDOM FOREST DOES NOT EXTRAPOLATE. INFERRED, not stated by the paper: a tree
  ensemble predicts by averaging training targets in a leaf, so outside the convex range
  of its training features it returns the boundary of what it has seen rather than a
  trend. Applying TBRF at Reynolds numbers or geometries outside its training set is
  therefore contraindicated on method grounds. Marked INFERRED and not to be cited as
  the paper's claim. WHAT THE PAPER DOES SAY, printed p. 31, is adjacent and corroborates
  the concern without asserting the mechanism: case C2 "features stronger separation than
  to the training cases and will therefore feature more extrapolation", and printed p. 36:
  "these are challenging cases due to the substantial differences between the training
  and prediction flows."

  (5) THE FIVE POPE INVARIANTS ARE DEGENERATE IN THE SQUARE DUCT -- and the square duct is
  this library's first ladder target. This is the paper's own finding, stated twice.
  Printed p. 23, verbatim: "in the case of the square duct (see Section 3.1) it was
  observed that due to the symmetry of the case there are only two distinct 'basis
  functions' defined by theta, and these are not sufficient to accurately describe the
  DNS anisotropy tensor for this case." Printed p. 37, verbatim, on the FS1-only case C3:
  "of the 5 features, 3 are approximately scaled versions of the other 2 - effectively
  reducing the input space to two-dimensions. This explains the difficulty nonlinear
  eddy-viscosity models based on only S and R, have in reproducing the magnitude of the
  secondary flow in the square duct." CONSEQUENCE: any duct implementation built on
  theta_1..theta_5 alone is contraindicated by the paper itself, and the published duct
  result depends on FS2 and FS3 -- which bring in grad(k), grad(p) and wall distance.
  Table 3, printed p. 37, is the measurement: FS1-only TBRF RMSE 0.0995 against
  full-feature 0.0521.

  (6) TBNN BEATS TBRF WHERE THE FEATURE SET IS THIN. Table 3, printed p. 37: on the duct
  with FS1 only (C3), TBNN 0.0871 versus TBRF 0.0995. The paper's realizability advantage
  for TBRF (printed p. 35) is therefore not an accuracy advantage everywhere, and an
  entry that cited only the realizability quote would overstate the case.
what_it_cannot_see: >-
  Eq. (8), printed p. 15, is a LOCAL map: b at a point is a function of S, R and scalar
  features evaluated at that point, so TBRF cannot see history, upstream separation
  state, or any genuinely non-local effect. It cannot see anything outside the convex
  hull of its training features -- see contraindication (4) -- and unlike a symbolic
  model it offers no expression to inspect, so a wrong prediction cannot be traced to a
  term. The paper reports the model reaching an incorrect turbulence state in the shear
  layer of the backward-facing step and states plainly that "The reason for this is
  unclear" (printed p. 35, page corrected 2026-09-04 from an earlier "p. 34"): the
  method's own authors could not see why.

  CORRECTION 2026-09-04, from reading Table 1, printed p. 25: an earlier revision of this
  entry described TBRF as blind to wall distance and pressure gradient. IT IS NOT. FS3
  contains, explicitly, a "wall-distance based Reynolds number" min( sqrt(k) d /
  (50 nu), 2 ), a "pressure gradient along streamline" feature, and a pressure-normal-
  stress ratio -- so d and grad(p) ARE inputs in the 17-feature configurations C1, C2 and
  C4. What it is blind to is narrower and should be stated as such: everything not
  reducible to a POINTWISE function of the mean field and its first derivatives, plus
  whatever the low-variance filter discarded (printed p. 30: features with variance
  < 1e-4 were dropped, and the paper does not name which they were on which case). Four
  of the FS3 features are also NOT Galilean invariant, by Table 1's own dagger footnote
  (printed p. 25) -- so a TBRF trained in one frame carries a frame dependence the
  underlying physics does not.

  A SECOND BLINDNESS THE PAPER NAMES ITSELF, and it is the one that matters for this
  library's duct target: in the square duct the five Pope invariants COLLAPSE. Printed
  p. 23: "due to the symmetry of the case there are only two distinct 'basis functions'
  defined by theta, and these are not sufficient to accurately describe the DNS
  anisotropy tensor for this case"; printed p. 37: "of the 5 features, 3 are
  approximately scaled versions of the other 2 - effectively reducing the input space to
  two-dimensions." A TBRF on FS1 alone literally cannot see the duct.

  FACTUAL CORRECTION, same date: an earlier revision said "its square-duct training data
  is Pinelli et al. (2010) at Re = 1100 to 3500 ... so it has not seen the aspect ratios
  or Reynolds numbers outside that range." THE SQUARE DUCT IS NOT TRAINING DATA. Table 2,
  printed p. 31, trains every reported configuration on PH5600, PH10595 and CD12600 only;
  SD3500 is a PREDICTION case, and the only duct data touching the fit is SD3200 inside
  the hyperparameter validation set (printed p. 30). So the honest statement is stronger
  than the old one: TBRF as published has never been trained on any duct at all, and its
  duct result is an out-of-distribution prediction from two-dimensional separated flows.
band_interaction: acts_on_k_magnitude
# SUPERVISOR RULING 2026-09-04. Was `does_not`. The lane found Eq. (16), printed p. 26:
# the modified k-equation replaces the Boussinesq stress in the PRODUCTION term with
# tau_ML(gamma), which contains b_ML. The learned anisotropy therefore moves the k
# MAGNITUDE, not only the stress shape. The lane declined to change a declared machine
# field outside its brief and escalated -- correctly. The entry had PRE-REGISTERED this
# exact condition for revision, so this is a registered condition being MET, not a
# post-hoc reclassification.
#
# CONSEQUENCE UNDER CHARTER 22.4 ITEM 2, which is why this field exists at all:
# the shelf-D eigenspace band perturbs shape and orientation ONLY -- Emory eq. (4) keeps
# k OUTSIDE the bracket -- so it cannot see a k-magnitude error BY CONSTRUCTION. This
# model acts on precisely that axis. A shelf-D band quoted beside a TBRF prediction is
# therefore an envelope SILENT ON THE AXIS THE MODEL MOVES, and quoting it as "the
# uncertainty of this model" is the error 22.4 item 2 forbids in terms. Any record
# showing both must state that overlap.
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
