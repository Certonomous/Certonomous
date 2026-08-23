# FS6 — Comparative feature document

**Rung definition, verbatim** (`docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md`
Part 4): *"FABLE mines every paper's feature table into one comparative document
with page cites."*

**Written 2026-08-23** by a closure-team lane. **Zero compute** — document work
only; no solver run, no fit, no training. Every page cite below is a page the
author of this document read this session, from the file on disk; PDF page
numbers are used throughout (printed-page equivalents are given where the two
differ). Title pages of **all 35** distinct verified works on disk were
re-verified this session before citation — 32 by reading the `.txt` sidecar's
page 1, Emory 2013 and Iaccarino 2017 by `pdftotext` of PDF page 1 (they carry
no sidecar), Gatski 1996 by rendering PDF page 1 to PNG and reading it — per
CLAUDE.md rule 15 / L-144. Statements a paper makes are marked **[stated]**;
everything the lab concludes from reading across papers is marked
**[inferred]**.

## What was mined, and what was not

| | n | which |
|---|---|---|
| Distinct title-verified works on disk | **35** | `MANIFEST.md` §1 (33) + Addendum 3 (Emory 2013, Iaccarino 2017) |
| Examined for feature content this session | **34** | all except Gatski 1996 |
| **Excluded from text mining** | **1** | `Gatski1996_handbook_chapter6.pdf` — 300-dpi scan, **no text layer** (sidecar is empty); its EASM feature content cannot be grepped or page-cited from text. Recorded, not padded. |
| Carry an explicit input-feature set for a learned/regressed closure | **9** | §2.1 below |
| Define field/stencil NN inputs (LES / learned wall models) | **10** | §2.2–§2.3 |
| Carry **no** feature table or ML input set — recorded as such | **15** | §2.4–§2.7 |

Not on disk and therefore **not mined**: the 16 PENDING-MIT titles of
`MANIFEST.md` §4. The single most consequential absence for this document is
**Ling & Templeton 2015** (§4 row 6) — the printed origin of the scalar-marker
feature set that four on-disk papers use at second hand, and (see §3.5) the
apparent true origin of two features in our own FS1 library whose on-disk
citation does not survive checking. No number from any PENDING-MIT paper
appears below.

A note on nomenclature to prevent a real confusion: **Kaandorp & Dwight 2020
name their three feature sets "FS1", "FS2", "FS3"** (their Table 1, arXiv
preprint p. 25). Those are *their* labels for feature groups and have nothing
to do with this lab's FS1–FS6 ladder rungs. In this document "FS1 library"
always means the lab's 110-feature library
(`cases/RANS_LES_closure_models/_common/features/FEATURE_LIBRARY.md`);
Kaandorp's sets are always written "Kaandorp-FS1/2/3".

---

## 2. Paper-by-paper feature inventory

### 2.1 RANS data-driven closures with explicit input-feature sets (9)

**Pope 1975** (*JFM* 72(2):331–340, publisher PDF; printed = PDF + 330).
The foundational feature set: the effective-viscosity hypothesis is closed with
a **10-tensor integrity basis and 5 scalar invariants** of the normalised
strain and rotation tensors (s, r), printed pp. 334–335 (PDF pp. 4–5); the
invariants and basis tensors are on printed **p. 335**. Normalisation is by the
turbulent timescale — s and r are dimensionless by construction. Invariance is
the paper's entire premise: any isotropic tensor function of (s, r) is
expressible in this basis **[stated]**. Every invariant-input paper below is
downstream of this page **[inferred]**.

**Ling, Kurzawski & Templeton 2016** (SAND2016-7345J preprint on disk, 17 pp).
TBNN inputs: **the 5 Pope invariants λ1…λ5 of S and R** (pp. 7–8), fed to an
"Invariant Input Layer", with the 10 Pope tensors in a separate "Tensor Input
Layer" whose combination embeds rotational/Galilean invariance of the output
(p. 8). S and R are non-dimensionalised "using the turbulent kinetic energy k
and the turbulent dissipation rate ε as suggested by Pope" (p. 4). The baseline
MLP instead takes **the 9 distinct components of the non-dimensionalised S and
R tensors** directly (p. 5) and is *not* rotationally invariant — the paper's
comparison point (p. 3). No wall-distance, pressure-gradient or TKE-gradient
feature of any kind **[stated by omission — the input list is exactly λ1…λ5]**.

**Wang, Wu & Xiao 2017** (arXiv:1606.07987v2, 36 pp). Feature set: **Table 1,
PDF p. 10** — ten scalar features q1…q10: Q-criterion (excess rotation:strain),
turbulence intensity, wall-distance Reynolds number `min(√k d/50ν, 2)`
(unnormalised — "already in a non-dimensional form", p. 9), pressure gradient
along streamline, turbulent-to-mean-strain timescale ratio, **ratio of pressure
normal stresses to shear stresses**, non-orthogonality between velocity and its
gradient (raw form `U_i U_j ∂U_i/∂x_j`), convection-to-production of TKE,
total-to-normal Reynolds stress ratio, and streamline curvature (normalised by
1/L_c, with L_c a *global* characteristic length — the one deliberate departure
from local normalisation, p. 9). Provenance is **stated** on pp. 7–8: the set
is Ling & Templeton 2015's twelve **minus** vortex stretching (their input 8)
**minus** the two linear/nonlinear eddy-viscosity discrepancy markers, **plus**
streamline curvature. Normalisation follows Ling & Templeton:
qβ = q̂β/(|q̂β| + |q*β|) with local normalisation factors (p. 9, caption p. 10).
Galilean invariance is argued feature-by-feature (e.g. q4 as an inner product,
p. 8) **[stated]**.

**Wu, Xiao & Paterson 2018** (arXiv:1801.02762v4, 42 pp). The FS1 library's
main source, and the corpus's maximal set. Two blocks:
(i) the **minimal integrity basis of {S, Ω, ∇p, ∇k}** — vectors mapped to
antisymmetric tensors via A = −I × v, **Eq. (B.1a,b), PDF p. 35**; the basis
itself in **Table B.4, caption on PDF p. 36** (Appendix B opens p. 35), "up to
47 invariants" (p. 11);
(ii) **three supplementary scalars** q1–q3 (wall-distance Re, turbulence
intensity, timescale ratio) in **Table 2, PDF p. 10** — *three, not the larger
q-sets of its relatives*.
Normalisation: the bounded scheme **α̂ = α/(|α| + |β|), Eq. 8, PDF p. 9**, with
per-tensor factors β in **Table 1, PDF p. 9** — ε/k for S, ‖Ω‖ for Ω,
ρ|DU/Dt| for ∇p, ε/√k for ∇k. Invariance: rotational by construction of the
integrity basis; Galilean invariance argued in Appendix C (pp. 35–36)
**[stated]** — and the paper's own Acknowledgment (PDF p. 33) records that "one
of the reviewers pointed out the lack of Galilean invariance in two of the
normalization constants", fixed in revision. See §3.3 for what the lab's FS2
measurement adds to that argument.

**Schmelzer, Dwight & Cinnella 2020** (arXiv:1905.07510v2, 29 pp). The
sparsest feature set in the corpus: S and Ω normalised by the timescale
**τ = 1/ω** (PDF p. 6), and of Pope's ten tensors and five invariants "only
the first four base tensors and the first two invariants are used in this
work" — **T(1)…T(4), I1, I2, PDF p. 8** **[stated]**. The candidate library
multiplies/squares these primitives up to polynomial degree 6 plus a constant
(PDF p. 9). No scalar markers, no wall distance, no ∇p/∇k tensors.

**Kaandorp & Dwight 2020** (arXiv:1810.08794v2, 58 pp). **Table 1, PDF
p. 25**, three nested sets: Kaandorp-FS1 = 6 invariant traces of S and R
(S², S³, R², R²S, R²S², R²SRS²); Kaandorp-FS2 adds 10 invariants involving
A_k = −I × ∇k (Eq. 13, p. 23; ∇k first normalised by √k/ε); Kaandorp-FS3 adds
**"nine extra scalar features"** (p. 23) taken from the Wang/Wu/Xiao line —
the ten of Wang's Table 1 **minus streamline curvature** (read off the table:
no curvature row exists; confirmed by full-text search — "curvature" appears
once in the paper, in prose about challenging flows). Tensors are normalised
"using k and ε"; the scalars carry per-feature normalisation factors (p. 23).
Invariance annotation, **Table 1 footnote p. 25**: "Features marked with † are
rotationally invariant but not Galilean invariant" — **four rows carry the
dagger** in the extracted table: turbulence intensity (k), pressure gradient
along streamline, convection of TKE, and non-orthogonality. **No A_p /
pressure-gradient tensor block at all** — their tensor extension uses ∇k only
**[stated]**.

**Singh, Medida & Duraisamy 2017** (arXiv:1608.03990v3, 32 pp). FIML-style
multiplicative correction β(η). Feature construction §III.A, PDF pp. 11–12:
start from the SA model's own arguments (ν, ν̂, Ω, d), reject them as
dimensional, and re-scale locally; "the set of features that were evaluated
includes **{Ω̄, χ, S/Ω, τ/τ_wall, P/D}**" (PDF p. 12) — non-dimensionalised
vorticity, viscosity ratio χ = ν̂/ν, strain-to-vorticity ratio, Reynolds-stress
to wall-stress ratio, production-to-destruction ratio. Input selection is by
validation-set SSE (p. 12). Note this is the one on-disk RANS paper whose
feature list contains **wall-stress-scaled** and **model-internal (χ)**
quantities rather than the Ling–Templeton markers **[inferred]**.

**Michelen Strofer & Xiao 2021** (arXiv:2104.04821**v1**, 10 pp). Tensor-basis
NN inputs: **the scalar invariants θ of S and Ω** (p. 3). In their 2-D cases
"there is only one independent scalar invariant with θ1 ≈ −θ2" (p. 7), so the
networks used have **one or two inputs** (pp. 6–8). The v1 on disk reports no
numeric error metric (manifest §5 note) — feature claims only.

**de Zordo-Banliat, Dergham, Merle & Cinnella 2023** (arXiv:2301.09013v1,
27 pp). Not a closure but a **space-dependent model-aggregation** (XMA): the
mixture weights are learned in feature space. §2.3 "Input features", PDF
p. 10: "we select a subset of **10 features** among those initially proposed by
Ling and Templeton", listed in **Table 1, PDF pp. 10–11**; features that need k
are "simply excluded" for models that do not carry k (p. 10) — feature
availability depends on the baseline model **[stated]**.

### 2.2 LES subgrid papers — field/stencil inputs, not invariant features (8)

None of these carries a feature table in the RANS sense; their input spaces
are raw resolved fields or local stencils, recorded here with page cites:

| paper | NN input **[stated]** | where |
|---|---|---|
| Maulik & San 2017 (arXiv:1706.00912v2) | **9-point stencil** of the filtered vorticity around the target point (3-D variant: 27 points) | PDF pp. 9–10 |
| Maulik, San, Rasheed & Vedula 2019 (arXiv:1808.02983v1) | 9-point sampling **stencils of vorticity and streamfunction** plus Smagorinsky and Leith **eddy-viscosity kernel** values | PDF pp. 1, 5 (Eq. 2.2) |
| Beck, Flad & Munz 2019 (arXiv:1806.04482v3) | element-local coarse velocity (u,v,w)ijk **plus the coarse-grid LES operator terms R(F̃(U_i))** — 6 tensors of size p³; adding the operator term "significantly improved learning" | PDF pp. 9–10 |
| Sirignano, MacArt & Freund 2020 (arXiv:1911.09145v1) | velocity components and their first and unmixed second derivatives at the grid point **and its 6 nearest neighbours**; "this selection does not strictly enforce Galilean invariance, but this was not found to be a challenge"; normalised "by the same set of constants for all cases" (global, not local) | PDF p. 16 |
| Guan, Chattopadhyay, Subel & Hassanzadeh 2022 (arXiv:2102.11400v1) | **global** (whole-domain) fields ψ̄/σψ and ω̄/σω — CNN, standard-deviation normalisation, chosen expressly for non-local effects | PDF pp. 8–9 |
| Um, Brand, Fei, Holl & Thuerey 2020 (arXiv:2007.00016v2) | the evolving discrete PDE state, seen inside the solver loop (the paper's subject is the input *distribution*, not the input *set*) | PDF pp. 1, 4, 8 |
| Kochkov, Smith, Alieva, Wang, Brenner & Hoyer 2021 (arXiv:2102.01010v1) | the discrete velocity field, through convolutional components (architectures in Fig. A1) | PDF pp. 4, 10 |
| List, Chen & Thuerey 2022 (arXiv:2202.06988v2) | discretised **velocity and pressure-gradient fields**; "the choice of network inputs is by no means trivial, but shall not be further studied here" | PDF p. 5 |

The comparative point **[inferred]**: the LES half of the corpus has
essentially *no* feature engineering — invariance, normalisation and locality,
the three axes every RANS paper argues in detail, are either delegated to the
architecture (CNNs), waived explicitly (Sirignano), or declared out of scope
(List). Guan's global-field input is the extreme anti-local pole; Wu 2018's
pointwise 47-invariant basis is the local pole.

### 2.3 Wall models (4)

**Bae & Koumoutsakos 2022** (arXiv:2106.11144v2). Multi-agent RL states,
PDF pp. 4–6: nondimensionalised "using viscosity ν and the modeled
instantaneous friction velocity u_τ^m" (pp. 4–5). VWM states: instantaneous
u*, ∂u*/∂y*, and y* at the sampling height h_m (p. 5). LLWM states: **the
local instantaneous log-law coefficients κ^m and B^m** computed from the same
information (p. 6) — deliberately y*-independent so the model extrapolates in
y* **[stated]**.

**Lozano-Durán & Bae 2023** (arXiv:2211.07879v3). The most explicitly
Buckingham-π-styled input set in the corpus: raw two-point-stencil information
{u1, u2, γ12, a1, γ̇1, k1, k_m1} (**Eq. 2.1, PDF p. 8**), fed as **six
non-dimensional groups {u1y1/ν, u2y2/ν, γ12, a1y1³/ν², γ̇1y1²/ν, k1/k_m1}**
(**Eq. 2.3, PDF p. 9**) — viscous-unit scaling, stated assumptions (iii)–(vi)
on locality and non-dimensionality, PDF pp. 4–5. Their earlier seven-point
stencil was dropped as complexity without benefit (p. 5) **[stated]**.

**Larsson, Kawai, Bodart & Bermejo-Moreno 2016** (J-STAGE, 23 pp) and
**Piomelli & Balaras 2002** (Annu. Rev., 29 pp): algebraic/ODE wall models —
input is the LES velocity (and optionally temperature) at a matching height
h_wm (Larsson PDF pp. 10–11; Piomelli PDF pp. 6–8). No feature tables; the
matching-height velocity is the entire "feature set" of the pre-ML wall-model
tradition **[inferred]**.

### 2.4 Analytical closures — single-operator precedents (5)

- **Smagorinsky 1963**: eddy viscosity from the **magnitude of the horizontal
  deformation tensor** on the grid scale (PDF pp. 6, 64–65; printed = PDF+98).
- **Nicoud & Ducros 1999** (printed = PDF + 182): the WALE operator is built
  "on the invariants of a tensor" (PDF p. 5) from the **traceless symmetric
  part of the square of the velocity-gradient tensor** (PDF p. 6), chosen for
  y³ near-wall behaviour (PDF p. 7) — an invariance-and-asymptotics argument
  fifteen years before the ML papers made the same moves **[inferred]**.
- **Menter 1994**: the SST blending functions F1, F2 take **wall-distance-based
  arguments** (functions of √k, ω, ν, y and the cross-diffusion term; PDF
  pp. 2–3, printed pp. 1599–1600) — the analytical precedent for every
  wall-distance feature in §2.1 **[inferred]**.
- **Spalart 2000**: strategy review; no feature content (0 matches for input
  features or ML in the sidecar).
- **Gatski 1996**: EXCLUDED from text mining (no text layer); its EASM content
  is catalogued elsewhere (`FOUNDATIONAL_MODELS_INVENTORY.md`) from rendered
  pages.

### 2.5 Model-form UQ (3) — no input features, and that is the finding

**Xiao, Wu, Wang, Sun & Roy 2016** (arXiv:1508.06315v3): the Reynolds-stress
discrepancy is parameterised over **physical space** — Barycentric/natural
coordinates for the projection (PDF pp. 9–11) and orthogonal basis functions
φi(**x**) over the spatial coordinate as random-field index (PDF pp. 9, 12).
**No mean-flow feature set anywhere** (0 "input feature" matches). The
feature-space move happens one paper later, in Wang/Wu/Xiao 2017 — which
frames it exactly as replacing x by q **[stated there, PDF p. 4]**.
**Emory, Larsson & Iaccarino 2013** and **Iaccarino, Mishra & Ghili 2017**:
eigenvalue/eigenspace perturbations of the anisotropy tensor; no input-feature
sets (0 matches in both, checked via pdftotext). Shelf D operates on the
*output* space of the closure, never on an input feature space **[inferred]**.

### 2.6 Feature-selection methodology (1)

**Guyon & Elisseeff 2003** (JMLR 3:1157–1182): the filter / wrapper / embedded
taxonomy (keywords p. 1157 = PDF p. 1; "variable ranking is a filter method",
PDF p. 4; wrappers and embedded methods §4, PDF pp. 2–3 check-list). No fluid
content; this is the methods authority the doctrine names for FS3, and the
lab's FS3 instruments map onto it directly: mutual information = filter,
permutation importance = wrapper-style assessment, elastic net = embedded
**[inferred]**.

### 2.7 Reviews (4) — where their feature discussions live

- **Duraisamy, Iaccarino & Xiao 2019** (arXiv:1804.00183v3): features/invariance
  discussion PDF pp. 13–17 (η feature space p. 13; invariance p. 15; Ling &
  Templeton's crafting-and-normalising scheme p. 16).
- **Duraisamy 2021** (arXiv:2009.10675v3): a dedicated **FEATURE SELECTION**
  section, PDF pp. 13–15, with four stated guidelines — local
  non-dimensionalisation, invariance of features *and* normalisers, local vs
  non-local (wall-distance and wall-stress measures "appear to be important";
  pressure-gradient features as a surrogate for non-locality), and data
  considerations. Its Fig. 3 (PDF p. 14) shows feature ranking **changing with
  the discrepancy representation** — the review-level statement of what FS3
  measured here (§3.6). Also the **feature-mismatch trap** (PDF p. 9): trained
  features come from DNS, prediction features from the model, and k_m, ε_m
  need not equal k, ε.
- **Beck & Kurz 2021** (arXiv:2010.12226v1): feature-space discussion in ML
  terms (pp. 10–11, 14, 17–18); "arbitrary input features" named as an ML
  strength (p. 14); no feature table.
- **Sanderse, Stinis, Maulik & Ahmed 2024** (arXiv:2403.02913v2): invariance
  survey pp. 10–12; restates the Pope/TBNN construction with coefficients as
  functions of λ1…λ5 (pp. 11–12); no feature table.

---

## 3. The comparison

### 3.1 Lineage — the corpus has two feature bloodlines, and one is not on disk

**[inferred from the stated provenance chains]**

```
Pope 1975 (λ1..λ5; T(1)..T(10), printed p. 335)
  ├── Ling 2016 TBNN      (all 5 λ, all 10 T)
  ├── Strofer 2021        (θ1, θ2 — 2-D collapse of the same λ)
  ├── Schmelzer 2020      (I1, I2; T(1)..T(4) only, τ = 1/ω)
  └── Kaandorp 2020 TBNN/TBRF tensor half (θ of S,R + A_k extension)

Ling & Templeton 2015 (12 scalar markers — PENDING-MIT, NOT ON DISK)
  ├── Wang/Wu/Xiao 2017   (10 = 12 − vortex stretching − 2 eddy-viscosity markers + curvature; Table 1 p. 10)
  ├── Wu/Xiao/Paterson 2018 (3 scalars q1–q3 only, Table 2 p. 10 + 47-invariant tensor basis Table B.4 pp. 35–36)
  ├── Kaandorp 2020       (9 = Wang's 10 − curvature; Table 1 p. 25)
  └── de Zordo-Banliat 2023 (10 of the L&T set; Table 1 pp. 10–11)
```

Singh 2017 sits outside both lines (SA-internal, wall-stress-scaled features);
the LES and wall-model papers use fields, stencils or wall-unit groups, not
either lineage. **Every scalar-marker paper on disk cites Ling & Templeton
2015 as origin, and that origin is PENDING-MIT** — the corpus documents the
mutations of the set but not its derivation.

### 3.2 Normalisation across the corpus

| paper | scheme | local? | carries ν? |
|---|---|---|---|
| Pope 1975 | turbulent timescale on s, r | yes | no |
| Ling 2016 | k, ε on S, R | yes | no |
| Wang 2017 | q̂/(|q̂|+|q*|), per-feature factors; L_c global for curvature | yes (one global exception) | q3 only (wall Re) |
| Wu 2018 | α/(|α|+|β|), Eq. 8 p. 9; factors Table 1 p. 9 | yes | q1 only |
| Schmelzer 2020 | τ = 1/ω on S, Ω | yes | no |
| Kaandorp 2020 | k, ε on tensors; per-feature factors on scalars | yes | wall-Re feature only |
| Singh 2017 | SA-internal ratios (χ, Ω̄, τ/τ_wall) | yes | via χ |
| Bae 2022 | ν and instantaneous modeled u_τ (wall units) | yes | yes, by design |
| Lozano-Durán 2023 | viscous units on all six groups (Eq. 2.3 p. 9) | yes | yes, by design |
| Sirignano 2020 | one global constant set | **no** | — |
| Guan 2022 | global standard deviations | **no** | — |

**[inferred]** The bounded α/(|α|+|β|) form is a Ling–Templeton invention that
only the Virginia-Tech line (Wang, Wu, and by adoption Kaandorp's scalars and
de Zordo-Banliat) uses; the Pope line normalises by a timescale alone and stays
unbounded. The FS1 library's block D (Pope λ under the Durbin-bounded scale)
inherits exactly that unboundedness — |λ3| to 1.5e11, |λ5| to 1.5e14
(`FS2_DEGENERACY_REPORT.md` §5) — so the two bloodlines' normalisation
philosophies are *both* present in the library, and the report already
records that block D dominates any unstandardised distance metric. The
wall-model papers are the only ones that normalise with ν deliberately (wall
scaling); in the RANS line ν appears only inside wall-distance Reynolds
numbers. The lab's variant-B (Durbin bound, carries ν) is a **lab addition
with no on-disk paper precedent** — no mined paper normalises S by
max(k/ε, 6√(ν/ε)); the library's own Reynolds-similarity note (L-184/D2)
already flags the consequence.

### 3.3 Invariance: claimed vs measured

| claim | where stated | what the lab measured |
|---|---|---|
| Wu 2018: features and normalisers Galilean invariant | App. C pp. 35–36; Acknowledgment p. 33 records a reviewer already caught two normalisers | FS2 §3: the argument holds for the *unsteady* DU/Dt; in a steady solve the implementable normaliser |U·∇U| shifts under a boost, so **53 A_p-containing invariants are not Galilean invariant as implemented** — a property of steady implementation, not an error in the paper |
| Kaandorp 2020: † rows rotationally but not Galilean invariant (4 rows daggered: turbulence intensity, ∂p along streamline, convection of TKE, non-orthogonality) | Table 1 footnote p. 25 | FS1 measurement flags the raw-velocity scalars exactly (q2, q4, q8, q9, q10 in library numbering); the overlap with Kaandorp's four printed daggers is exact on q2/q4/q8/q9 — see §3.5 for the q10 attribution correction |
| Ling 2016: TBNN output invariant by construction; MLP on raw components is not | pp. 3, 7–8 | not re-measured (no TBNN in the FS1 library); consistent with the library's design choice of invariant inputs |
| Sirignano 2020: Galilean invariance **not** enforced, "not found to be a challenge" | p. 16 | — recorded as the corpus's one explicit waiver |
| Wang 2017: per-feature Galilean argument (inner products) | p. 8 | same steady-DU/Dt caveat applies to its q4 normaliser family **[inferred from FS2 §3]** |

The charter's response (CLOSURE_MODELLING_CHARTER §6) — invariance is verified
**over the whole composition** by unit test, never taken from the basis — is
precisely calibrated to the two incidents above (Wu's reviewer catch; the
steady-state normaliser shift).

### 3.4 Coverage against the FS1 110-feature library

- **Features every RANS-line paper uses**: the S/Ω pair invariants — tr S² and
  tr Ω² appear in *every* invariant-input paper on disk (Pope λ1, λ2; Ling;
  Wu rows 1, 3; Schmelzer I1, I2; Kaandorp-FS1; Strofer θ1, θ2)
  **[inferred]**. They are also the two features FS5 finds most out-of-range
  on the hump (I1_trS2__A at 20.4% of cells) — the most-used features in the
  literature are the ones our extrapolation instrument flags first.
- **Features no on-disk paper uses**: the entire **variant-B block (47
  features)** — the Durbin-bounded normalisation is a lab construction (§3.2);
  and the **A_p (pressure-gradient tensor) invariants beyond Wu 2018** — Wu is
  the *only* paper on disk whose basis includes ∇p as a tensor; Kaandorp's
  extension stops at ∇k **[stated in both]**.
- **Paper features the FS1 library does not carry**: Wang 2017's **q6, ratio
  of pressure normal stresses to shear stresses** (Table 1 p. 10; also in
  Kaandorp's nine) has no library counterpart; Ling & Templeton's vortex
  stretching and the two eddy-viscosity discrepancy markers were dropped by
  Wang before the lineage reached us (p. 7) and are likewise absent. The
  library's q9_nonOrthogonality is implemented on S (`|U_i U_j S_ij|`) where
  Wang's printed raw form uses the full gradient `U_i U_j ∂U_i/∂x_j` — an
  implementation variant, recorded here, not resolved.
- **Library features whose printed source is not on disk**: q7_viscRatio
  (ν_t/(ν_t+100ν)) and q11_turbReynolds — see §3.5.

### 3.5 Citation corrections to FEATURE_LIBRARY.md, found by this mining

These are **discrepancies between the library's source column and the pages as
read this session**. The features themselves are fine; the invariance and
degeneracy *measurements* stand untouched (they are measurements, not
citations). Recorded here for a future amendment of
`make_feature_library.py` (the .md is generated); nothing was edited.

1. **q7_viscRatio and q11_turbReynolds are cited to "Kaandorp Table 1 p. 25" —
   that table does not contain them.** Kaandorp's Table 1 lists nine scalars
   (p. 23: "nine extra scalar features"); no eddy-viscosity ratio and no
   turbulent Reynolds number appear anywhere in the paper (full-text search:
   no "viscosity ratio", no "turbulent Reynolds" feature row). Their printed
   origin is Ling & Templeton 2015's twelve-marker set — **PENDING-MIT, not on
   disk** — from which Wang 2017 explicitly *dropped* the eddy-viscosity
   markers (p. 7). Until that paper arrives, these two features have **no
   on-disk printed source**.
2. **q10_streamlineCurv is cited to "Kaandorp Table 1 p. 25 (dagger)" — wrong
   paper.** Streamline curvature is **Wang, Wu & Xiao 2017 Table 1 (PDF
   p. 10)**, added by them; Kaandorp's set is Wang's ten *minus* curvature,
   and carries no such row or dagger.
3. **Dagger count**: FEATURE_LIBRARY.md ("Their daggered features are q2, q4,
   q8, q9, q10 — five") vs the table as read: **four** † rows (q2, q4, q8, q9
   equivalents), no q10 row to dagger. CLOSURE_MODELLING_CHARTER §6 already
   has it right ("marks four of nine ... with a dagger").
4. **Wu 2018 page cites are one page early** in FEATURE_LIBRARY.md and FS2:
   normalisation Table 1 is on PDF **p. 9** (cited p. 8); Table 2 is PDF
   **p. 10** (cited p. 9); Table B.4's caption is PDF **p. 36** (cited p. 35 —
   Appendix B and Eq. B.1a,b are correctly p. 35). Wu 2018's printed folios
   match PDF pages (folio "35" prints on PDF p. 35), so this is not a
   folio-offset artefact.
5. `MANIFEST.md` Addendum 3 promises "title page below" for Emory 2013 and
   Iaccarino 2017 and the file ends without them. Both title pages were
   verified this session (pdftotext page 1) and match the intended citations.

### 3.6 Where FS2 degeneracy and the FS3 disagreement bear on paper-claimed feature importance

- **The 12 pooled-dead features are all Wu Table B.4 invariants** — every one
  a triple-product of {S, Ω, A_p, A_k} that vanishes on statistically 2-D mean
  flow (FS2 §2). Wu 2018 presents the 47-invariant basis as the systematic,
  maximal input set **[stated, pp. 5, 11]**; the lab's measurement adds that on
  this benchmark class between 22 and 48 of the 110 implemented features are
  algebraically zero per family, and the duct feature matrix has rank 96/110.
  No mined paper reports a per-family rank or dead-feature audit of its
  feature matrix **[stated-by-absence: none of the nine §2.1 papers prints
  one]** — FS2 has no literature counterpart in this corpus.
- **Pope-basis truncation is corroborated, not just asserted.** Schmelzer
  keeps T(1)…T(4)/I1–I2 on 2-D grounds (p. 8); the lab's per-cell rank
  measurement (FS2 §4: mean 3.7, never above 5, of a nominal 10) is the
  quantitative version, and the R4 fs3 fits then found T4 buys nothing over
  T1–T3 even when offered (MODEL.md: 0.0158092 vs 0.0156199 LOFO MSE, with
  T4 ≈ −T3 near-2-D). Ling 2016's use of all ten tensors carries ~5 redundant
  directions on flows of this class **[inferred]**.
- **Single-method importance claims are fragile here.** The FS3 run
  (`R4_sparta_build/artefacts/fs3.json`; RESULTS.md §4.1) put three selection
  instruments on one dataset: permutation importance vs mutual information
  Spearman **0.19 / −0.28 / 0.11 / −0.12** across the four fits — near-zero to
  *anti*-correlated — while MI vs elastic-net agreed 0.60–0.88. Wang 2017
  interprets random-forest feature importance; Singh 2017 selects by
  validation SSE; each is one instrument. Duraisamy 2021's Fig. 3 (p. 14)
  makes the same point from the literature side: the ranking changes with the
  representation of the discrepancy. The lab's pre-registered reading ("three
  methods agreeing is evidence and three disagreeing is a finding") is the
  operational form of Guyon & Elisseeff's warning that filters, wrappers and
  embedded methods answer different questions **[inferred]**.
- **No mined paper plants a zero.** The R4 planted-zero regression control
  (two true-zero columns; RESULTS.md §4.3) caught the elastic-net path
  selecting a term whose held-out permutation importance (−322.2) was *below
  both planted zeros* — a GATE FAIL on the T1–T4 `R` fit. None of the nine
  feature-set papers describes a negative-control column in its selection
  procedure **[stated-by-absence, checked in the nine §2.1 papers]**. Given
  the measured near-orthogonality of the instruments above, published
  feature-importance rankings in this corpus should be read as
  method-conditional **[inferred]**.
- **FS5 coverage vs the papers' generalisation claims.** The features carrying
  the hump out-of-range mass (FS2 §6: I1_trS2, q3_timeScaleRatio,
  q11_turbReynolds, λ3…) are drawn from *both* bloodlines; Duraisamy 2021's
  feature-mismatch trap (p. 9) and Beck 2021's position-in-feature-space check
  (p. 11) are the closest literature analogues to the FS5 instrument, and
  neither mined paper in §2.1 reports a train/test feature-range audit
  **[stated-by-absence]**.

---

## 4. Gaps this document cannot close

- **Ling & Templeton 2015** (PENDING-MIT §4 row 6): the derivation of the
  scalar-marker set, the printed definitions of the two library features with
  no on-disk source (§3.5 item 1), and the original twelve-feature table. Four
  on-disk papers use this set at second hand; this document mines the
  mutations, not the origin.
- **Gatski 1996** (no text layer): EASM invariant arguments (η1, η2 line) are
  absent from this comparison.
- **Holland 2019 / Parish & Duraisamy 2016** (PENDING-MIT): the integrated
  FIML feature treatment cannot be compared; Singh 2017 stands in for the
  whole FIML-C feature practice here.
- Kaandorp's Table 1 was read from a two-column pdftotext extraction; the four
  dagger marks and nine comment rows were legible, but any marker lost by the
  extractor would not be visible. The count "four" is what the extracted page
  shows; the charter §6 reading agrees.

*End of FS6. This closes the last unstarted rung of the FS ladder as a
document rung: no verdict is claimed, no gate graded, no compute spent.*

---

## Addendum 1, 2026-08-23 — §3.5 errata verified and repaired; Ling & Templeton 2015 acquisition stays on Sanaa's desk

The §3.5 errata were independently verified by the closure supervisor (own
grep of the Kaandorp sidecar: nine features, zero hits for a viscosity ratio
or a turbulent Reynolds number) and repaired **at the generator**:
`make_feature_library.py` edited and `FEATURE_LIBRARY.md` regenerated, commit
`01430485`; docket **D467**, lesson **L-246**. The regeneration was asserted
to move only source columns and source prose — all 110 rows'
feature/definition/normaliser/G/R/dead columns byte-identical before and
after. Known knock-on recorded in D467: the per-feature table shifted +4
lines, so two pre-existing `FEATURE_LIBRARY.md:174` line cites
(`docs/LAB_STATE.md:192`, `docs/closure/R5_CONSTRAINTS_DISCHARGE_RECORD.md:301`)
now point 4 lines early; flagged to their owners, not edited here.

**Ling & Templeton 2015 remains PENDING-MIT** (`MANIFEST.md` §4 row 6). It is
the un-owned origin of the scalar-marker bloodline (§3.1) and, after this
repair, the openly declared *only* printed source of `q7_viscRatio` and
`q11_turbReynolds`. Its acquisition is an institutional-access decision that
sits with Sanaa; nothing was fetched from any gated source by this lab.

Lines whose number changed above this section: 0.
