# The evaluation protocol the Closure Challenge does not have: a census of what this field actually measures, and a battery that measures it

Date: 2026-08-05 (UTC). **TEST-BLIND throughout.** Zero scoring calls, zero
test-case ground-truth reads. Every figure and number below comes from
training or validation cases, where reading truth is legal under the
benchmark's own split, or from records earlier guarded runs already wrote.

**Why this document exists.** The Closure Challenge reduces a submission to
one number per case. Section 1 shows, from the benchmark's own preprint,
that this is the *only* thing it measures and that the preprint never states
a limitation of it. Section 2 is a census of what the field's own literature
measures instead — ten papers read in full, every evaluation metric
inventoried with a verbatim convention quote. Section 3 states the protocol
this lab will use. Section 4 reports what the implemented battery found on
our own entry, including the parts that go against us.

Companion artifacts:

| Artifact | What it is |
| --- | --- |
| `demo-output/website/closure_eval/closure_eval_master_table.md` | every number, in one table, sourced per row |
| `demo-output/website/closure_eval/{ph,duct}_battery.json` | the battery's own records |
| `demo-output/website/closure_eval/*.png` | 20 figures |
| `sdk/scripts/closure_eval_battery/` | the implementation (4 files) |

---

## 1. What the challenge measures, and what its own paper says about that

Source: `docs/papers/mcconkey_et_al_closure_challenge_2603.28884.{pdf,txt}`
— McConkey, Buchanan, Smidt, Bodner, Dwight, Cinnella, "The Closure
Challenge: a benchmark task for machine learning in turbulence modelling",
arXiv:2603.28884v1, 30 Mar 2026, **read in full (6 pages)**.

**The metric, Eq. (1), §2.3.** (The `.txt` extraction drops the equation's
norm bars and the overbar on `|U|_c`; the form below was read off the
rendered PDF page 3, and that reading is recorded as such.)

> Score = (1/N_cases) · Σ_c [ 1 / (N_c · ‾|U|_c) ] · Σ_{i=1..N_c}
> |Ũ_i − U_true,i| , with ‾|U|_c = (1/N_c) Σ_i |U_true,i|

Verbatim definitions (lines 125–131): *"| · | denotes the Euclidean vector
magnitude, Ũi is the predicted velocity vector at point i, Utrue,i is the
reference (DNS/LES) velocity vector"*; *"The scaling by |U|c ensures that
each test case contributes on a comparable scale regardless of its
characteristic velocity."* Interpretation, verbatim: *"average fractional
velocity error across all test cases; for example, a score of 0.05 indicates
that predictions are off by approximately 5% of the mean velocity magnitude
on average. A lower score indicates better agreement"*.

**Three facts about the paper, each checked rather than assumed:**

1. **There are no results plots of any kind.** `pdfimages -list` finds
   exactly one embedded image in the whole 6-page PDF. That image is
   Figure 1, a *case-selection* diagram (the 29 parametric hill geometries
   with red boxes on the four test cases), captioned *"Cases for the
   periodic hills dataset (reproduced from [6] with red boxes added)."*
   Table 1 is the leaderboard: rank, authors, one scalar. That is the
   complete inventory. No profiles, no contours, no C_f, no C_p, no
   per-case physics.
2. **The paper never states a limitation of the metric.** A keyword sweep
   over the full text returns zero hits for `limitation`, `does not`,
   `pressure`, `Reynolds stress`, `anisotrop*`, `Lumley`, `barycentric`,
   `reattach`, `skin friction`, `Cp`, `RMSE`, `L2`, `weight`, `per-case`.
   The only hedge is temporal: the phrase *"As of March 2026"* appears four
   times, once attached to the score itself.
3. **The train/validation confound is acknowledged and left open.** The
   paper *would prefer* a standard training set *"in order to separate the
   performance of a modelling technique from the data it was trained on"*
   but states *"we only standardize the test dataset. You are free to use
   your own training and validation data."* Leaderboard position therefore
   mixes method quality with data quality, by the organisers' own account.

**What Eq. (1) structurally cannot see** (our analysis, not the paper's
claim): pressure, Reynolds stresses, k, ω, anisotropy, skin friction,
separation and reattachment location, any wall quantity, and any
conservation property of the submitted field. It weights every evaluation
point equally, so large quiescent regions outvote thin shear layers and
recirculation zones. Section 4 shows this is not hypothetical for our own
entry.

---

## 2. The census: what this field's literature actually measures

Ten papers read in full, PDF + `pdftotext` pairs held in `docs/papers/`.
Every quote below was `grep`-verified against the extraction; where
`pdftotext` mangled the source, the mangled form is quoted and flagged.

**Dimensions of the census: 10 papers · 8 flow families · 24 distinct
evaluation metrics · 6 convention classes.**

### 2.1 The corpus

| # | Paper | Role | File stem |
| --- | --- | --- | --- |
| 1 | McConkey, Buchanan, Smidt, Bodner, Dwight, Cinnella, arXiv:2603.28884 (2026) | **the benchmark itself** | `mcconkey_et_al_closure_challenge_2603.28884` |
| 2 | Wu & Zhang, "The Training of the SST-QCRC Model" | leaderboard rank 2 — entrant description document | `wu_zhang_sst_qcrc_challenge_description` |
| 3 | Wu, Zhang, Zhang, arXiv:2402.16355 | rank 2's method paper | `wu_zhang_zhang_2402.16355` |
| 4 | Liu, Wang, Zhao, Xiao, arXiv:2509.17189 (70 pp.) | leaderboard rank 3's method paper | `liu_wang_zhao_xiao_2509.17189` |
| 5 | Oulghelou, Cherroud, Merle, Cinnella, FTaC 2025 / arXiv:2410.14431 | the paper linked from leaderboard rank 4 | `oulghelou_cherroud_merle_cinnella_ftac2025_2410.14431` |
| 6 | Reissmann, Fang, Ooi, Sandberg, GPEM 2025 / arXiv:2409.07369 | rank 1's cited SR-machinery paper | `reissmann_fang_ooi_sandberg_gpem2025_2409.07369` |
| 7 | Zhao, Akolekar, Weatheritt, Michelassi, Sandberg, arXiv:1902.09075 | rank 1's turbulence lineage (GEP) | `zhao_akolekar_weatheritt_michelassi_sandberg_1902.09075` |
| 8 | Xiao, Wang, Ghanem, arXiv:1603.09656 | the periodic-hill para-database lineage | `xiao_wang_ghanem_1603.09656` |
| 9 | Schmelzer, Dwight, Cinnella, FTaC 2020 | SpaRTA — rank 4's lineage | `schmelzer_dwight_cinnella_ftac2020_s10494-019-00089-x` |
| 10 | Ling, Kurzawski, Templeton, JFM 2016 | TBNN — the duct/secondary-flow reference | `ling_kurzawski_templeton_jfm2016_osti1333570` |

Geometry- and convention-canon references fetched alongside, each PDF +
extraction: Breuer, Peller, Rapp, Manhart, C&F 38 (2009) 433–457 (periodic
hills); Vinuesa et al., J. Turbulence 15 (2014) and Pinelli, Uhlmann,
Sekimoto, Kawahara, JFM 644 (2010) (ducts); Greenblatt et al., AIAA-2004-2220
(the CFDVAL2004 hump experiment) plus captured NASA turbmodels pages for the
hill and hump validation cases; Emory & Iaccarino, CTR Annual Research Briefs
2014 (barycentric/componentality display).

**Availability failures, recorded rather than papered over** (charter §2:
attempts are reported, never assumed):

- **Weatheritt & Sandberg, J. Comput. Phys. 325 (2016) 22–37** (the GEP
  paper McConkey co-cites for the rank-1 entrant, DOI
  `10.1016/j.jcp.2016.08.015`): **not obtained.** Unpaywall `is_oa: false`;
  OpenAlex `oa_status: closed`, `any_repository_has_fulltext: false`;
  Semantic Scholar `CLOSED`; not deposited in Southampton ePrints or
  Melbourne Minerva Access. Nothing is asserted from it. *(The DOI given in
  the entrant's own info file, `10.1016/j.jcp.2016.05.022`, resolves via
  Crossref to a different paper entirely — an atmospheric-model paper by
  Allen & Zerroukat. The PII in that same link is correct; the DOI is not.)*
- **Banerjee, Krahl, Durst, Zenger, J. Turbulence 8 (2007) N32** (the
  barycentric map's source): **not obtained** — Taylor & Francis 403,
  Unpaywall `is_oa: false`, OpenAlex closed, no repository copy. The
  convention is instead cited from Emory & Iaccarino (CTR 2014), which
  presents the same construction and credits Banerjee et al.
- **NASA turbmodels caveat, found the hard way:**
  `turbmodels.larc.nasa.gov` now 301-redirects every deep link to a generic
  NASA landing page, so a plain `curl` of a validation-case URL silently
  returns the wrong document. Caught because two different fetches came back
  byte-identical. The live mirror is `https://tmbwg.github.io/turbmodels/`,
  and that is what the captured pages record.

### 2.2 Two corrections to what the leaderboard implies

Both matter for any claim we make about rank, so both are on the record.

1. **The board and the paper disagree on how many entrants there are.** The
   challenge preprint's Table 1 lists **three** entrants (Reissmann 0.0595,
   Wu & Zhang 0.0624, Montoya/Oulghelou/Cinnella 0.0779). The benchmark
   repo's `README.md` lists **four**, inserting Liu, Wang, Zhao & Xiao at
   0.0737 as rank 3. The README declares itself *"the main source of
   up-to-date information"*, so the master table transcribes the README —
   and records the discrepancy.
2. **Two of the linked entrant papers do not demonstrate the method on the
   challenge.** Reissmann et al. (arXiv:2409.07369), linked as rank 1's
   reference, contains **zero turbulence or CFD content** — word-boundary
   grep gives `RANS` = 0, `duct` = 0, `turbulen*` = 0, `Reynolds` = 0; it is
   a symbolic-regression methods paper, and the turbulence content lives in
   the co-cited (and unobtainable) Weatheritt & Sandberg. Oulghelou et al.
   contains **no square duct at all** — yet ducts are 3 of the 8 test cases.

### 2.3 The metric census, by convention class

#### Class 1 — Station velocity profiles (7 of 10 papers)

The universal mean-flow metric. **The only fully specified periodic-hill
convention in the corpus is Xiao, Wang & Ghanem's**, and it is the one this
lab adopts because the challenge's own hill cases come from that database.

| Paper | Convention, verbatim | Where |
| --- | --- | --- |
| Xiao et al. | axis label *"x/H; 2Ux /Ub + x/H"*; *"eight streamwise locations x/H = 1, · · · , 8, compared to the baseline results and the benchmark results obtained by direct numerical simulation"*; stresses at *"20R12/Ub2"*, TKE at *"20k/Ub2"*; legend *"Samples Baseline Benchmark (Breuer et al. 2009)"* | Figs. 7–10 |
| Xiao et al. | normalisation: *"Re is based on the crest height H and bulk velocity Ub at the crest"*; *"All dimensions are normalized by H with Lx /H = 9 and Ly /H = 3.036"* | §3, Fig. 2 |
| Liu et al. | hills, **wall-normal** velocity not streamwise: `10 Uy /Ub + x/hp` vs `y/hp`; ducts as offset `Uy` stacks — *"Each panel plots Uy at multiple wall-normal locations z/hs , where hs denotes half the duct height; horizontal offsets of +10.0 Uy are applied for visualization."* | Figs. S26–S29 |
| Oulghelou et al. | offset stacks with **per-figure undocumented scale factors** (jet `x/Djet + 5Ux/Uxref`, hills `x/L + Ux/Uxref`, hump `x/L + Ux/(10 Uxref)`); PH stations `x/L ∈ {0,…,9}`; CD stations `{5.5, 6.2, 6.8, 7.6, 8.5, 9.5, 10.3, 11.1, 11.8}` | Figs. 7, 9, 12 |
| Wu et al. | *"Velocity profiles at different 𝑥 standpoints"* — station values figure-only, never enumerated | Figs. 6, 11, 16, 20 |
| Schmelzer et al. | *"Predicted stream-wise velocity"*; stations figure-only | Figs. 2, 7, 13 |
| Zhao et al. | turbomachinery analogue: pitchwise wake loss *"ω(y) = (pit − pt (y))/(pit − po)"* at *"20% axial chord downstream of blade trailing edge"* | Fig. 4a, Fig. 8 |
| NASA hump page | station list for the hump class: `x/c = -2.14, 0.65, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3` | captured page |

#### Class 2 — Skin friction C_f along the wall (5 of 10 papers)

The standard separation-fidelity metric, and the one the challenge omits
entirely. Wu & Zhang, Figs. 3(b)/4: **SST-QCRC solid line, SST dash-dot,
LES/experiment × symbols**. Schmelzer et al., Fig. 10: *"The skin friction
coefficient Cf and the associated separation and reattachment points are
better captured compared to the baseline k-ω SST for PH10595 and
CBFS13700."* Liu et al., Figs. S9b/S32b: *"Skin-friction coefficient
distributions cf , are shown along the streamwise direction x/hc .
Separation and reattachment points are marked using circles."* Oulghelou
et al., Fig. 9: *"L refers to channel half-height for CD, the step height
for CBFS and hill crest for PH."*

**Neither C_f nor C_p is given a formula by any entrant paper** — no `u_τ`
appears in Oulghelou et al. at all, and Liu et al. plot bump `cf` against an
unnormalised bare `x`.

#### Class 3 — Separation and reattachment (4 of 10 papers, no shared convention)

The symbol `x_r` appears in **none** of the four challenge-relevant papers.
Wu, Zhang & Zhang quote numbers directly (*"reattachment point given by the
SR-CND and the SR-CLS models is approximately 𝑥 = 6.0, which is much closer
to the DNS result (𝑥 ≈ 5.2)"*). Oulghelou et al. tabulate a
`(Start x/L, End x/L, Length)` triple and **never state how it was
extracted**. Liu et al. mark `cf = 0` crossings with circles and use the
`Ux = 0` isoline on maps. Xiao et al. list reattachment as an auxiliary QoI
*"obtained by post-processing the velocity fields"* and then omit the figure.

#### Class 4 — Secondary flow in ducts (2 of 10 papers)

The metric that matters for 3 of the 8 challenge test cases, and the one the
challenge score cannot express. **Ling, Kurzawski & Templeton is the
reference convention**, verbatim: *"Plot of secondary flows in duct flow
case. Reference arrows of length Ub /10 shown at the top of each plot"*
(Fig. 6), with the layout *"Only the lower left quadrant of the duct is
shown, and the streamwise flow direction is out of the page"* (Fig. 4) —
which is exactly the domain the benchmark ships. Liu et al. give the
contour+streamline form: *"cross-sectional contours of Ux /Ub overlaid with
streamlines illustrate the corner-vortex structures and secondary
circulations"* (Fig. S39b). Oulghelou et al. have **no duct at all**.

#### Class 5 — Reynolds-stress anisotropy (2 of 10 papers, and none of the entrants)

**No paper linked from the leaderboard plots a Lumley triangle or a
barycentric map** — `Lumley` and `barycentric` return zero non-bibliographic
hits in Liu et al., Oulghelou et al., Reissmann et al., and the challenge
preprint. The convention exists only in the *lineage* papers: Zhao et al.
Fig. 7 (*"the barycentric map developed by Banerjee et al. [32] is used to
examine the trained model"*, with the plane-strain `λ2 = 0` dashed line) and
Xiao et al. Figs. 3/5, which both use the identical coordinates
`C1 = λ̃1 − λ̃2`, `C2 = 2(λ̃2 − λ̃3)`, `C3 = 3λ̃3 + 1`. Ling et al. plot raw
`b_ij` component maps instead (*"Only the lower left quadrant of the duct is
shown"*), with a scalar RMSE table.

**Consequence for us:** an anisotropy display would be establishing a
convention for this benchmark, not following one. It is also not applicable
to our own entry, which predicts a velocity correction and never forms a
Reynolds stress — recorded here so the absence is a stated scope decision
rather than an oversight.

#### Class 6 — Scalar accuracy numbers

Nearly always a normalised MSE/RMSE of velocity: Schmelzer et al.'s
`ε(U)/ε(U°)` against the baseline model's error; Wu et al.'s region-split
C_f MSE ratios (*"approximately 6.7% of those of the SST model"*) and the
Ahmed-body *"Velocity profile's RMSE"* normalised by *"the freestream
velocity 𝑈∞ = 40 𝑚/𝑠"*; Ling et al.'s RMSE of `b` (duct: LEVM 0.23, QEVM
0.18, TBNN 0.13, MLP 0.33). **Two of the four entrant ranking metrics are
not reproducible**: Liu et al.'s normalised misfit `ê` never defines its
underlying `e`, and Oulghelou et al.'s `mae` is never given a formula,
averaging population, or point weighting. McConkey Eq. (1) is the only
fully specified ranking metric in the entire corpus — a genuine argument for
anchoring on it, alongside everything else.

### 2.4 Styling: there is no convention to inherit

Across all ten papers there is no consistent "truth = symbols, models =
lines" statement. Wu & Zhang state it for their own figures (LES/experiment
as `×`); Liu et al. document exactly one legend in 70 pages (the radar
chart); Oulghelou et al.'s legends survive only as empty `( )` after
extraction. **The protocol below therefore specifies its own, and states it
in every caption.**

---

## 3. The protocol

### 3.1 Scope and legality

Every diagnostic runs on **training and validation cases only**. Test cases
may be opened for RANS fields, mesh geometry, and our own model outputs —
exactly the read categories rounds 2–4 already used — but never for ground
truth. Enforcement is in code, twice over:

1. The raising-stub scoring guard (the pattern from
   `sdk/scripts/closure_divergence_audit.py`) replaces `score`,
   `score_from_csv`, `evaluate_by_case`, `evaluate_from_csv_by_case`,
   `evaluate_individual_case`, `_velocity_field`, `_ground_truth`,
   `_load_csv_predictions` and `evaluation_points` with functions that
   raise, in every namespace they are reachable from — *before* any pipeline
   work — and the guard is **proven armed** by calling `score()` and catching
   the refusal.
2. Every ground-truth loader in `battery_common.py` asserts its case against
   a train/validation whitelist **before opening a file**, so a future
   editing mistake cannot reach a test case's truth.

### 3.2 The metrics, and what each is for

| ID | Metric | Form | Convention followed | Answers what the score cannot |
| --- | --- | --- | --- | --- |
| M1 | Station velocity profiles, hills | curve | Xiao et al., `2Ux/Ub + x/H` at `x/H = 1..8` | *where* the error lives, and whether the corrected profile is smooth |
| M2 | 1:1 scatter vs truth, one panel per quantity, black 1:1 line | scatter | ours (the census has no template) | bias vs scatter; which component is being fixed |
| M3 | Pointwise `‖U_model − U_truth‖₂` maps + the integrated scalar | map | ours — the challenge metric's own integrand, made spatial | whether a good scalar is uniform accuracy or cancelled extremes |
| M4 | In-plane secondary-flow streamlines over `\|U_in-plane\|/U_b` | map | Ling et al. Fig. 4/6 layout + `U_b/10` key; Liu et al. S39b contour+streamline | whether the corner-vortex *structure* is right |
| M5 | Secondary-flow intensity, volume-weighted `\|(Uy,Uz)\|/U_b` | number | ours (a scalar summary of M4) | how much of the true secondary flow exists at all |
| M6 | Streamwise profiles at spanwise stations `z/h`, ducts | curve | ours, on the mesh's own z-lines (no interpolation) | Reynolds/AR transfer, wall by wall |
| M7 | Continuity error `‖∇·U‖ / ‖∇U‖_F` | number | pre-registered in `closure_challenge_stability_physicality_audit.md` §0.2 | whether the field obeys the equations it claims to solve |

### 3.3 Fixed styling, stated in every caption

Because the census found none to inherit: **truth = black filled circles;
RANS baseline = blue (`#0077BB`) dashed line; our corrected field = red
(`#CC3311`) solid line; magnitude maps = viridis with a shared scale per
figure.** Categorical colours were validated with the dataviz palette
validator (light surface `#FFFFFF`: lightness band pass, chroma floor pass,
CVD separation pass at worst adjacent ΔE 13.5 deutan, normal-vision floor
pass at ΔE 29.9, contrast pass). Every axes title states the population and
the averaging convention — *"all 15600 cells, no volume weighting"*, not a
bare label.

### 3.4 Normalisations, measured rather than assumed

- **Hills.** `h` is the crest height, taken as the maximum of the mesh's own
  lower-boundary curve. It is cross-checked against a second, independent
  source — the domain-height tag in the case name (`..._3036` → `Ly/h =
  3.036`, Breuer's channel height) — and the run aborts on a >2% mismatch.
  `U_b` is the crest bulk velocity, height-averaged over the crest column
  from `y = h` to the top wall, computed from the LES field so all three
  curves in a figure share one normaliser (stated in every caption).
- **Ducts.** `h` is the quadrant half-height; `U_b` is the
  **volume-weighted** mean `U_x`, with volumes from the same validated
  Green-Gauss mesh machinery the divergence audit uses.

---

## 4. What the battery found

Implementation: `sdk/scripts/closure_eval_battery/` — `battery_common.py`,
`run_ph_battery.py`, `run_duct_battery.py`, `build_master_table.py`.
**20 figures**, all under `demo-output/website/closure_eval/`. Compute: 182 s
(hills) + 51 s (ducts) on the 2-core cap. Zero scoring calls; zero test
ground-truth reads.

**Validity anchors, checked before anything below was believed.** The PH
model's pooled validation scaled MAE comes back **0.0876**, the recorded
round-1 value to four figures; variant D's `AR_7_Ret_180` comes back
**0.0135** against the pre-registered 0.01345. These are the entry of
record's own models, not lookalikes.

### 4.1 The sharpest finding: the ducts get the *amount* right and the *structure* wrong

`duct_secondary_flow_AR_1_Ret_180.png`, `..._AR_3_Ret_180.png`,
`..._AR_7_Ret_180.png`.

The RANS baseline carries in-plane flow at `2.7e-18` to `1.2e-17` of `U_b` —
machine zero, as a linear eddy-viscosity model must: it cannot produce
Prandtl's secondary flow of the second kind at all. Our correction restores
**69% to 112% of the true secondary-flow intensity** (M5), which by that
scalar looks like the physics has been recovered.

**The streamlines say otherwise.** On the square duct `AR_1_Ret_180` the
LES field has a **counter-rotating corner-vortex pair** — two distinct
centres either side of the corner bisector, the canonical structure. Our
corrected field draws **one** vortex. On `AR_7_Ret_180` the correction
reproduces the near-side-wall vortex pair convincingly (`z/h > 5.5`) but
replaces the truth's rich multi-vortex structure near the centreplane
(`z/h < 1.5`) with a single smooth sweep. The intensity scalar cannot tell
these apart; the streamline plot does at a glance. **This is the concrete
demonstration that M5-style scalars — and the challenge score, which is a
weaker scalar still — are satisfiable without the flow being right.**

This is also the measured, a-posteriori confirmation of what
`CLOSURE_CHALLENGE_STATUS.md` §0b established a-priori from a different
direction: two of the seven Pope-invariant features (`I3_S3`, `I4_W2S`) are
*provably* zero on this entire flow family, so the feature set is structurally
short of what generating the correct vortex topology would require.

### 4.2 Where a good challenge score hides a bad field

`metric_vs_physics.png` and master table §C. Continuity numbers are quoted
from `closure_challenge_stability_physicality_audit.md` §2, not recomputed.

Every arrow in that figure points **left and up**: the score improves and
the field's continuity degrades. On the two hills the correction is applied
to, the score improves by 0.082 and 0.104 while the continuity error rises
from 0.18% and 0.08% of the field's own velocity-gradient scale to **10.5%
and 9.7% — factors of 58 and 124**. On the three ducts, the RANS field is
divergence-free to machine precision (its fully-developed unidirectional
solution is exactly solenoidal cell-wise) and the corrected field is not, at
**2.3–3.4%**. Every other entrant on the board re-solves the governing
equations and gets `∇·U ≈ 0` by construction; our submitted corrected fields
do not, and **the scoring metric never sees any of it** — nothing here
changes the recorded round-4 0.0654.

> **Round-5 note, added 2026-08-11 (Ladder V rung V14, stale-surface item 8).**
> This section reports the battery's measurements of the **round-4** submission,
> which was the entry of record when it was written. Two things about it are now
> out of date and neither is edited above, because both are correct measurements
> of the fields they were taken on:
> - **`0.0654` is round 4.** Round 5 superseded it at **0.056647** on 2026-08-07
>   (`closure_challenge_round5_qcr.json`). The definite article is the only thing
>   corrected in the sentence above.
> - **The `2.3–3.4%` duct figure no longer describes the submitted duct fields.**
>   Round 5 replaced all three with an untrained QCR2000 forward solve, whose
>   measured `rms div U / rms grad U` is **8.5×10⁻⁴ (`AR_1_Ret_360`), 5.3×10⁻⁴
>   (`AR_3_Ret_360`) and 5.4×10⁻⁴ (`AR_14_Ret_180`)** — two orders of magnitude
>   better, because a forward solve satisfies continuity where an additive
>   correction does not. Source: `closure_challenge_round5_qcr_forward.json`,
>   `/arms/{case}_qcr/div_over_grad`. **`AR_7_Ret_180` (5.8×10⁻⁴) is the
>   validation duct and is NOT in the submission** — quoting its value as the
>   submission's is the error V15 recorded as finding F1, so the three submitted
>   cases are named individually here.
> - **The two hills and `NASA_2DWMH` are unchanged by round 5** — those
>   predictions ship byte-identical to round 4, so `10.5%`, `9.7%` and the
>   declined-case rows above still describe the entry of record exactly.

**The two declined cases are the only submissions that are both competitive
and clean.** The gate's "off" state ships the organisers' own solve, so it
inherits its physicality untouched (ratio 1.000 by construction) — and on
both, the raw RANS floor already beats every published entrant for that case
(0.0461 vs best-published 0.0569; 0.0719 vs 0.0760). The part of the entry
that does nothing is the part that survives a physics check.

### 4.3 The hills: the correction works, and it is visibly rough

`ph_profiles_*.png` (7 cases), `ph_scatter_{validation,train}.png`,
`ph_error_maps_{validation,train}.png`.

At Xiao et al.'s own eight stations the corrected profile moves toward the
LES through the recirculation region on the `alpha_15` cases — and does so
with **cell-to-cell jaggedness that the LES profile does not have**. That
roughness is a direct visual of the same defect the continuity number
measures: a cell-wise ML output added to a solenoidal field is not itself a
flow field. The scalar metric averages it away completely.

**Two cases where the correction is worse than doing nothing** show up
plainly in the error maps: validation case `alpha_05_10071_4048` (0.0759 →
0.0772) and, more awkwardly, **training case `alpha_05_7071_3036`
(0.0552 → 0.0589) — the model is beaten by the raw RANS field on a case it
was trained on.** This is the in-sample form of the covariate-shift finding
the C1 decline gate was built for, and it is reported here because the
battery surfaced it, not because it flatters the entry.

The maps say *how* it gets worse, which the −0.0013 does not. On
`alpha_05_10071_4048` the RANS error is a diffuse mid-channel band; the
corrected field's error is **concentrated into a bright strip along the
lower wall**, roughly doubled there. The correction has not spread its error
around — it has relocated it into the near-wall region, which is where a
downstream user would care most and where the challenge metric's
equal-weight-per-point averaging cares least. `ph_error_maps_validation.png`,
top row.

### 4.4 What was not done, and why

- **No hump-class battery.** `NASA_2DWMH` is a test case, so its truth is
  off-limits; `CBFS13700` is the legal hump-class training case and would
  support the C_f/C_p conventions of Class 2, but computing C_f for the
  corrected field requires a wall-gradient operator that does not yet exist
  in this lab's toolchain and must be validated against the shipped
  `wallShearStress` before it is trusted. Queued, not faked.
- **No anisotropy display.** §2.3 Class 5: no entrant uses one, and our
  entry never forms a Reynolds stress. Stated as a scope decision.
- **No re-scoring of other entrants.** Three of the four have prediction
  files in the benchmark repo, but re-scoring them would spend scoring calls
  on ground truth to no purpose. Their numbers in the master table are
  transcribed by machine from the benchmark's own README and labelled
  *published*.
