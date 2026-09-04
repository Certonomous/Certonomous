---
id: f_sst_qcrc_wu2026
family:
  - f
  - b
flow_class:
  - square_duct_secondary_flow
  - separation_2d
validation_cases:
  - CBFS
equation_form: >-
  TWO modifications to Menter's k-omega SST, both transcribed from the source PDF.

  (1) NONLINEAR QUADRATIC CORRECTION TO THE REYNOLDS STRESS. Wu & Zhang Eq. (1),
  printed p. 1: "a nonlinear quadratic correction term is added to the Reynolds
  stress's expression. The correction term (for incompressible flow) is like the QCR
  term used in the SA-QCR2000 [2] model", with the constant "directly adopted from
  Ref. [2], which is = 0.3". The symbol glyphs of Eq. (1) DO NOT extract from this
  PDF (its math font does not map through pdftotext), so the explicit tensor form is
  taken from the paper's own cited source, which this lane title-page verified and
  read: Spalart 2000, IJHFF 21(3):252-263, UNNUMBERED displayed equation, printed
  p. 253 --
      s_ij(nonlinear) = s_ij - c_nl1 * ( O_ik s_jk + O_jk s_ik )
      O_ik = ( d_k U_i - d_i U_k ) / sqrt( d_n U_m d_n U_m )
      c_nl1 = 0.3
  where s_ij is "the Reynolds stress given by the linear model" and O_ik "the
  normalised rotation tensor" (Spalart 2000, p. 253, verbatim).

  (2) CORRECTION TO THE DESTRUCTION TERM OF THE OMEGA EQUATION. Wu & Zhang Eq. (2),
  printed p. 1: the destruction term is multiplied by a bracket of the form
  [(beta_correction - 1) * f_shield + 1], with a shielding function
  f = 1 - tanh[(8 d)^n] that "is 0 in the boundary layer and is 1 elsewhere" and is
  "used to deactivate the correction term in the boundary layer to preserve the
  baseline SST model's accuracy in simple wall-attached flows". The spatially varying
  correction field is obtained by field inversion (Singh et al.) and then distilled by
  symbolic regression (PySR) into Eq. (3), printed p. 2:
      beta_correction = max( -0.1157 , 0.0058525 * <feature> )
  bounded above by 4 for stability (p. 2). UNVERIFIED -- needs equation-level read:
  the SUBSCRIPTED SYMBOL NAMES of Eqs. (1)-(3) and the identity of the single feature
  in Eq. (3) do not extract from this PDF's math font. The paper states only that
  three input features were used and that "the definition of the features can be found
  in Ref. [3]" (Wu, Zhang & Zhang, AIAA J. 63(2):687-706, 2025), which is held on this
  box as docs/papers/data_driven_rans/wu_zhang_zhang_2402.16355.pdf but was NOT read
  by this lane. A rendered (page-image) read of pp. 1-2, or a read of Ref. [3],
  resolves it.
provenance:
  path: docs/papers/data_driven_rans/wu_zhang_sst_qcrc_challenge_description.pdf
  title_page_verified: "yes"
  title_page_quote: >-
    "The Training of the SST-QCRC Model / Chenyu Wu1, Yufei Zhang1 / 1. School of
    Aerospace Engineering, Tsinghua University" -- verbatim from page 1, read by
    closure lab-lane (laneC) on 2026-09-04 via `pdftotext -f 1 -l 1`. Page 1 carries
    NO printed date; the year 2026 in this entry's id is taken from the PDF
    CreationDate metadata (2026-03-05) and corroborated by McConkey et al., "Table 1:
    Leaderboard as of March 2026", which lists "Wu and Zhang [19]" at rank 2 with an
    overall score of 0.0624.
  equations: >-
    Eqs. (1) and (2), printed p. 1; Eq. (3), printed p. 2, of
    wu_zhang_sst_qcrc_challenge_description.pdf. The explicit QCR tensor form is the
    UNNUMBERED displayed equation on printed p. 253 of
    docs/papers/closure/Spalart2000_strategies_turbulence_modelling.pdf, title page
    verified by this lane on 2026-09-04 ("Strategies for turbulence modelling and
    simulations / P.R. Spalart / Boeing Commercial Airplanes ... International Journal
    of Heat and Fluid Flow 21 (2000) 252-263").
claimed_effect: >-
  The paper's own claims, quoted. On the training case: "The [Cf] distribution given by
  the SST-QCRC model fits the LES data [9] much better compared with the baseline SST
  model" (printed p. 3, curved backward-facing step). On the guard case: "The
  prediction of the SST-QCRC model is almost identical to the prediction of the SST
  model. Both models align well with the experiment data [10]. The result indicates
  that the SST-QCRC model won't affect the baseline SST model's accuracy in simple wall
  attached flows such as the ZPG flat plate" (printed p. 3). NOTE: the paper states NO
  quantitative magnitude for either claim -- "much better" and "almost identical" are
  its own words and its figures were not digitised by this lane. The only NUMBER
  attached to this correction is external to the paper: McConkey et al.'s leaderboard
  overall score 0.0624 at rank 2 (Table 1, "as of March 2026"). For the QCR half
  specifically, Spalart 2000 p. 253 claims: "The result in the square duct is quite
  positive: flow is induced towards the corners, and the skin friction is much closer
  to experiment (Gessner et al., 1991)."
install_class: compiled-library
install_stanza: |
  RAS
  {
      RASModel        kOmegaSSTQCR;   // <-- THE QCR HALF ONLY. SEE contraindications.
      turbulence      on;
      printCoeffs     on;
  }
model_type_name: none
libs_required: []
libs_route: ensure_libs
libs_route_justification: none
failure_mode: loud
contraindications: >-
  THREE, and the first is a trap this box can spring today.

  (1) SST-QCRC IS NOT INSTALLED ON THIS BOX; ONLY ITS QCR HALF IS. `kOmegaSSTQCR` is
  built and its symbol is registered (`nm -DC
  /home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/lib/libkOmegaSSTQCRTurbulenceModels.so`
  shows `RASModels::kOmegaSSTQCR`, read by this lane 2026-09-04). That library
  implements Eq. (1) -- the quadratic Reynolds-stress term -- and NOT Eqs. (2)-(3),
  the field-inversion correction to the omega destruction term, which is the half that
  carries the 'C' in QCRC and the half that produced the CBFS result. Running
  `RASModel kOmegaSSTQCR` and recording it as SST-QCRC would report a ladder result for
  a model that never ran: ARCHITECTURE §0 failure (ii) exactly. `model_type_name` is
  therefore `none` for this entry, not `kOmegaSSTQCR`.

  (2) THE QCR TERM IS CONTRAINDICATED ON 3-D WALL JETS, by its own author. Spalart
  2000, printed p. 253, verbatim: "However, other flows such as 3D wall jets have led
  to negative results (A.N. Secundov, personal communication, 1999). The cnl1 term must
  also be considered as very preliminary, in the sense that it uses only one of the
  many quadratic combinations of strain and vorticity. Also note that it is fully
  empirical, instead of being derived from a more complex model; we simply selected the
  most intuitively attractive combination. A systematic optimisation has not been
  performed."

  (3) c_nl1 = 0.3 WAS CALIBRATED ON A BOUNDARY LAYER, NOT ON A DUCT. Spalart 2000,
  p. 253: the constant "was calibrated in the outer region of a simple boundary layer,
  by requiring a fair level of anisotropy u'2 > w'2 > v'2". Wu & Zhang adopt it
  unchanged and explicitly do not retrain it ("No data-driven techniques are used to
  train the parameters of the correction term", printed p. 1). Any duct result is
  therefore an extrapolation of that calibration, not a fit to it.
what_it_cannot_see: >-
  The omega-equation correction is a LOCAL algebraic function of three flow features
  (Eq. 3), so it cannot see history, upstream state, or anything non-local: two points
  with the same local features receive the same correction whatever happened to the
  fluid before them. Its shielding function is an explicit blindness by construction --
  f is 0 in the boundary layer, so the correction cannot act there AT ALL, by design.
  The QCR half is a local algebraic function of the mean-velocity gradient alone and so
  cannot see anything the gradient does not encode. And the correction field was
  inverted on ONE case (CBFS): it has never seen a duct, which is the flow class this
  library's first ladder target sits in.
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

# SST-QCRC (Wu & Zhang, Tsinghua) — closure-challenge leaderboard rank 2

**Status REGISTERED. Nothing here has been run. ZERO COMPUTE.**

## Why `install_class: compiled-library` and not `fvOptions-source`

Eq. (1) adds a quadratic term to the Reynolds stress itself, i.e. it changes the
anisotropy the momentum equation sees. `structural.modifies_anisotropy_tensor: yes` is
declared on that basis, and SCHEMA §4 then refuses `fvOptions-source` for this entry:
`fvOptions` adds sources and cannot modify the momentum equation's Reynolds-stress
term. The omega-destruction correction (Eq. 2) *alone* would be a legal
`fvOptions-source`; the model as a whole is not.

## `band_interaction: acts_on_k_magnitude`

Eq. (2) modifies the destruction term of the omega equation, and the paper's own
reading of Eq. (3) is that it "increase[s] the destruction of [omega] in the regions
with strong shear. This means that the eddy viscosity would be increased in the region
of strong shear" (printed p. 2). Changing nu_t changes the turbulent kinetic energy
magnitude, which is the axis a shelf-D eigenspace band does not perturb. Where this
correction and such a band appear together, the overlap in what NEITHER sees must be
stated (CLOSURE_MODELLING_CHARTER §22.4 item 2).

## What was verified today, and by what reader

- Page 1 of the PDF read with `pdftotext -f 1 -l 1`; title transcribed verbatim into
  `provenance.title_page_quote` (L-144: never verify by filename or hash).
- The corpus sidecars are invisible to this box's default `grep` (.gitignore + ugrep),
  so every content search behind this entry used **`/bin/grep` over explicit globs**
  (L-486).
- The symbol table of `libkOmegaSSTQCRTurbulenceModels.so` was read with `nm -DC`;
  `RASModels::kOmegaSSTQCR` is present (ARCHITECTURE §2.3). This is a zero-compute
  assertion and it is what establishes contraindication (1): the *name* exists, the
  *model in this entry* does not.

## Open item this entry resolves for INGEST_PLAN

INGEST_PLAN §2 (Priority 3) and §5 carried an explicit prohibition: *"confirm whether
`Spalart2000_strategies_turbulence_modelling.pdf` actually contains the QCR2000
formulation — its sidecar shows 0 hits for 'quadratic constitutive' and the lane did
not read the paper. DO NOT let an entry cite it as the QCR source until someone has."*

**It has now been read, and it does.** The formulation is on printed p. 253 as an
unnumbered displayed equation, under §2.2 "Simple RANS models", with c_nl1 = 0.3, a
square-channel demonstration in Fig. 1 (p. 254), and the 3-D-wall-jet contraindication
quoted above. It never uses the acronym "QCR" — which is why the sidecar search for
"quadratic constitutive" returned zero and why that zero was not evidence of absence.
The paper's own phrase is "nonlinear constitutive relation".

This also converts INGEST_PLAN §1's reason 1 — flagged there as *"MY DOMAIN KNOWLEDGE,
NOT A MEASUREMENT ON THIS BOX"* — into a citation: Spalart 2000, p. 253, states that a
non-Boussinesq constitutive relation "can, for instance, create secondary flows of the
second kind in a square pipe (Speziale, 1987)" and reports that with it "flow is induced
towards the corners". It remains an untested premise *on this box*; it is no longer
uncited.
