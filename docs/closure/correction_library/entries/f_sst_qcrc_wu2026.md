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
paper_validation_cases: >-
  Field inversion and training: the curved backward-facing step (CBFS), printed p. 1-2;
  the beta_CND data is reused from Ref. [3]'s conditioned field inversion. The paper's
  own GENERALISATION GUARD is not a separate case but the shielding function f_d, which
  "is 0 in the boundary layer and is 1 elsewhere" and exists "to preserve the baseline
  SST model's accuracy in simple wall-attached flows" (p. 1) -- i.e. the guard is built
  into the model form rather than demonstrated on a held-out attached-flow case in this
  document. Recorded here rather than dropped: an entry whose guard is a claim in the
  formulation, not a measured case, is weaker evidence than one with a demonstrated
  attached-flow result, and the difference must be visible.
equation_form: >-
  BOTH equations READ DIRECTLY OFF THE PRINTED PAGE by closure-supervisor, 2026-09-04,
  by rendering page 1 at 200 dpi (pdftoppm) and reading the image. This SUPERSEDES the
  earlier reconstruction of Eq. (1) from Spalart 2000: the paper's own form is now
  transcribed and is the authority here.


  (1) NONLINEAR QUADRATIC CORRECTION TO THE REYNOLDS STRESS -- Wu & Zhang Eq. (1),
  printed p. 1, verbatim structure:
      tau_ij   = tau^l_ij - c_r ( O_ik tau^l_kj - tau^l_ik O_kj )
      tau^l_ij = 2 nu_T S_ij - (2/3) k delta_ij
      O_ij     = ( d_j U_i - d_i U_j ) / sqrt( d_n U_m d_n U_m )
      c_r      = 0.3
  The paper states c_r "is directly adopted from Ref. [2]" (Spalart 2000) and that
  "No data-driven techniques are used to train the parameters of the correction term."
  NOTE the index arrangement is the paper's own and differs in presentation from the
  Spalart form previously recorded here; the antisymmetric structure is the same.


  (2) CORRECTION TO THE DESTRUCTION TERM OF THE OMEGA EQUATION -- Wu & Zhang Eq. (2),
  printed p. 1, verbatim structure:
      Dw/Dt = (gamma/nu_T) tau_ij d_j U_i - beta theta w^2
              + d_j[ ( nu + sigma_w nu_T ) d_j w ] + 2 (1 - F_1) (sigma_w2 / w) d_j k d_j w
      beta  = [ ( beta_CND - 1 ) f_d + 1 ]
      f_d   = 1 - tanh[ ( 8 r_d )^3 ]
      r_d   = ( nu + nu_T ) / ( kappa^2 d^2 sqrt( d_n U_m d_n U_m ) )
  beta_CND is "a spatially varying field that quantifies the error in the omega's
  equation". f_d "is a shielding function that is 0 in the boundary layer and is 1
  elsewhere", used "to deactivate the correction term beta_CND in the boundary layer to
  preserve the baseline SST model's accuracy in simple wall-attached flows". The spatial
  distribution of beta_CND "is determined by field inversion method proposed by Singh et
  al. [4]". The paper states this formulation "is identical to the formulation used in
  the work of Wu et al. [3]".


  CONSEQUENCE FOR ANY CONTROL ON THIS ENTRY, derived from Eq. (2) itself: the NULL VALUE
  OF beta_CND IS 1, NOT 0. Substituting beta_CND = 1 gives beta = [(1-1) f_d + 1] = 1,
  which recovers baseline SST exactly. A planted-zero control that plants or checks for
  ZERO would therefore be testing the WRONG NULL, and a field defaulting to 0 does not
  degrade quietly -- it drives beta -> 1 - f_d, which vanishes in the freestream. Any
  field-input control for this entry plants a DEPARTURE FROM 1.


  ONE SYMBOL READ BUT NOT RESOLVED: the destruction term prints as "beta theta w^2".
  "theta" is NOT defined anywhere on the page that carries Eq. (2). Transcribed as
  printed rather than silently normalised to the standard SST "beta w^2".
  (3) THE SYMBOLIC-REGRESSION EXPRESSION FOR beta_CND -- Wu & Zhang Eq. (3), printed
  p. 2, READ OFF THE RENDERED PAGE by closure-supervisor 2026-09-05 (200 dpi):
      beta_CND = max( -0.1157 , 0.0058525 * lambda_2 ) * lambda_2
  bounded ABOVE by 4 "to keep the computation stable", the paper stating that upper
  bound "is consistent with the upper bound used in the conditioned field inversion
  process" (p. 2). NO LOWER BOUND IS STATED.

  THE FEATURE IS IDENTIFIED. The paper offers THREE candidate features -- "We only
  chose 3 features as the input features: lambda_1, lambda_2, P_k/epsilon" (p. 2) --
  and THE FINAL EXPRESSION USES ONLY lambda_2. lambda_1 and P_k/epsilon are offered to
  the regression and DROPPED. Figure 2 (p. 2) prints the PySR hall of fame: complexity
  15 (chosen) at loss 4.845e-01, and complexity 16 at the SAME loss 4.845e-01 with a
  score of 2.253e-05 -- the paper selects 15 on simplicity, and says so.

  THE PAPER'S OWN PHYSICAL READING, p. 2 verbatim: "Eq. (3) implies that we choose to
  increase the destruction of omega in the regions with strong shear. This means that
  the eddy viscosity would be increased in the region of strong shear, since
  nu_T ~ k/omega. This is consistent with the 'slingshot effect' [7]". Figure 1 (p. 2)
  shows the field-inverted beta_CND on CBFS spanning roughly 1.2 to 4.8, concentrated
  in the separated shear layer.

  SUPERVISOR'S READING OF THE TWO EQUATIONS TOGETHER -- MARKED AS INFERENCE, NOT THE
  PAPER'S STATEMENT, AND NOT TESTED HERE. Eq. (3) drives beta_CND -> 0 as lambda_2 -> 0.
  Substituted into Eq. (2) that would give beta = [(0-1) f_d + 1] = 1 - f_d, i.e. the
  omega DESTRUCTION TERM WOULD VANISH wherever f_d were near 1 with the flow near
  irrotational. It does not bite, and the reason is in r_d: r_d = (nu+nu_T) /
  (kappa^2 d^2 sqrt(d_n U_m d_n U_m)) is INVERSELY proportional to the velocity
  gradient, so as grad(U) -> 0, r_d -> infinity, tanh -> 1 and f_d -> 0, returning
  beta -> 1, i.e. BASELINE. So the paper's prose that f_d "is 0 in the boundary layer
  and is 1 elsewhere" UNDERSTATES its own shielding function: f_d also goes to 0
  wherever the velocity gradient vanishes, and that second role is what keeps
  beta_CND -> 0 from switching off omega destruction in an irrotational freestream.
  Recorded because an implementer reading only the prose would not know the far-field
  behaviour is protected, and might add a lower clip that the model does not need.
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

## Training provenance, read off p. 1-2 by the supervisor — and a cross-team consequence

The paper states plainly where its correction field comes from: *"We performed field inversion on
the curved backward facing step (CBFS) case. In fact, the data obtained in Ref. [3] using the
conditioned field inversion is directly used"*, and — the line that matters operationally —
**"The code used to perform the field inversion is DAFoam, developed by He et al [5]."**

**Consequence, and it is the reason this entry is worth more than its rank-2 placing.** The field
inversion that produces `beta_CND` was done in **DAFoam**, which this lab already runs as a
standing capability (the `dafoam` team's whole territory). So the reproduction path for this
entry's *second* modification is not an unknown toolchain — it is one the lab operates. **This does
not make the reproduction cheap and it is not a claim that it will work**; DAFoam adjoint work here
has its own live defects. It means the capability gap for this entry is **narrower than for any
other family-(f) correction**, and that should be weighed when Phase 2 picks an order.

**Its training case, CBFS, is on disk** (`/home/ubuntu/closure-challenge-benchmark/data/CBFS`).
So the entry's own reproduction target and its reference data are both present.

**What that does NOT license.** `kOmegaSSTQCR` on this box implements **Eq. (1) only**. Running it
and reporting the result as SST-QCRC would report a verdict for a model missing the entire second
modification — the one the field inversion produces and the one that did the work on CBFS. That is
why `model_type_name` is `none` here, and it is the same trap SCHEMA Addendum 2 was written for.

## What still blocks IMPLEMENTED — a named table, not a vague gap

`equation_form` is now fully transcribed and `UNVERIFIED` is removed: Eqs. (1), (2) and (3) are
read off the printed pages with numbers and pages. **The remaining gap is different in kind and is
recorded so it cannot be mistaken for the old one.**

**`lambda_2` is identified but not DEFINED here.** Wu & Zhang state only *"The definition of the
features can be found in Ref. [3]"* (p. 2). Ref. [3] is **held** —
`docs/papers/data_driven_rans/wu_zhang_zhang_2402.16355.pdf`, title-page verified by the supervisor
2026-09-05 as *"Development of a Generalizable Data-driven Turbulence Model: Conditioned Field
Inversion and Symbolic Regression"* (Wu, Zhang & Zhang, Tsinghua) — and its **Table 2** carries the
feature definitions. **That table has NOT been read.** Its own math does not extract (`lambda` hits:
**0** over 83,953 extracted characters — the same font trap as L-489), so it needs a rendered read.

> **THIS GATES `IMPLEMENTED`, NOT `REGISTERED`.** The equation form is verified; you cannot *code*
> `lambda_2` without its definition. Any attempt to advance this entry past `REGISTERED` reads
> Ref. [3] Table 2 first. **Note also that Ref. [3] uses FIVE features where the challenge
> description uses THREE** — so the two papers' feature sets are not the same object, and the
> definition must be taken for the three named here.

## Runtime cost, from Ref. [3] p. 18 — a rule-12 input for Phase 2, and a warning about a sibling entry

Read off the rendered page by the supervisor, verbatim: *"the SR-CLS and the SR-CND model increase
the total runtime (of the same CFD iteration steps) by about **15% and 10%** respectively, which is
acceptable."* **So a symbolic-regression correction of this family costs roughly 1.10-1.15x baseline
runtime** — a usable first estimate for Phase 2 costing under rule 12.

**And the contrast on the same page is the one that matters for planning.** Ref. [3] cites Yin et
al. [8]: *"if a random forest model is called in every iteration of CFD, the computational time
required to converge the solution is about **30 times** the convergence time of the baseline
model."* **The TBRF entry in this library IS a random forest** (100 trees, no closed form by
construction). **A TBRF a-posteriori reproduction should therefore be costed near 30x baseline, not
near 1x** — an order-of-magnitude difference that decides whether it fits an authorisation, and one
that would otherwise have been discovered by overrunning a cap mid-run.

## The `lambda_2` definition — READ 2026-09-06, and the gate above is CLEARED

Ref. [3] **Table 2, PDF p. 11**, rendered at 300 dpi and read by closure-supervisor. The caption is
*"The local flow features chosen to construct the expression for beta(w)"*. Verbatim definitions:

| name | definition | |
|---|---|---|
| `lambda_1` | `tr(S_hat^2)` | `S_hat = S/(beta* omega)`, nondimensional strain rate |
| **`lambda_2`** | **`tr(Omega_hat^2)`** | **`Omega_hat = Omega/(beta* omega)`, nondimensional rotation rate** |
| `lambda_5` | `tr(Omega_hat^2 . S_hat^2)` | |
| `Re_Omega` | `\|Omega\| d^2 / nu` | *"identify strong shear away from the wall"* |
| `P_k/eps` | `tau^R_ij u_i,j / (beta* k omega)` | `tau^R` from the Boussinesq hypothesis |
| `eta` | `lambda_2 lambda_5 / Re_Omega` | extracted by SR from the CBFS field inversion in [29] |

with `beta* = 0.09`, *"a model constant of the SST model"*. These are Pope's scalar invariants of
the general tensor representation of the Reynolds stress. **`lambda_2` is therefore codeable, and
the `IMPLEMENTED` gate recorded above is CLEARED** — what remains between this entry and
`IMPLEMENTED` is a demonstrated install, which is compute.

## ⚠ AND THE SAME TABLE CARRIES THE MOST CONSEQUENTIAL SENTENCE I HAVE READ IN THIS LIBRARY

Table 2, verbatim: **"The 3rd and the 4th invariances are omitted because they are zero in 2D flows
and our training set is 2D."**

**The `beta_CND` feature basis is TRUNCATED ON A 2D PREMISE.** `lambda_3` and `lambda_4` are dropped
precisely because they vanish in two dimensions — which means they are exactly the invariants that
are *non-zero only in three-dimensional flow*.

**The square duct is a three-dimensional flow.** Secondary flow of the second kind lives in the
cross-plane; it is the canonical 3D corner phenomenon. So applying the `beta_CND` correction to a
duct would apply a model whose feature basis was **constructed on the assumption the flow is 2D** to
a flow whose defining feature is 3D. That is an extrapolation of exactly the kind **FS5 — the
standing extrapolation-coverage gate — is armed for**, and it is visible here only because the
feature definitions were read rather than cited.

**THE DECOMPOSITION THIS FORCES, AND IT IS GOOD NEWS FOR THE DUCT.** SST-QCRC is two independent
modifications and they do not share this limitation:

- **Eq. (1), the QCR term — NOT data-driven.** `c_r = 0.3` is adopted from Spalart 2000 and the
  paper states flatly *"No data-driven techniques are used to train the parameters of the correction
  term."* It carries no trained feature set, no 2D training premise, and Spalart demonstrates it
  **on a square duct** (p. 253: *"flow is induced towards the corners"*). **This is the duct-relevant
  half.**
- **Eqs. (2)-(3), the `beta_CND` omega-correction — data-driven on a 2D training set** with a
  2D-truncated feature basis. **This is the half that should NOT be carried to a duct without FS5
  being answered.**

**WHAT THIS DOES NOT LICENSE.** It does not license running `kOmegaSSTQCR` and recording the result
under this entry: that library implements Eq. (1) only, and this entry is the *combined* model.
**It licenses a SEPARATE entry for the QCR2000 correction itself, sourced to Spalart 2000** — which
this lab holds, which the supervisor has title-page verified and read at equation level, and which
`kOmegaSSTQCR` genuinely does implement. **That entry does not yet exist and is the next zero-compute
item.** Writing it is how the duct-first plan gets a correction it can honestly run.
