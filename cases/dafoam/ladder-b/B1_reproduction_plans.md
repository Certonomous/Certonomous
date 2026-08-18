# Ladder B1 — FIML-lineage reproduction plans for the closure challenge

Date: 2026-07-28. **Research and planning only — no solver runs, no compute launched
in this rung.** Every number below is either quoted from a paper/repo I fetched, or
measured directly from files already on this box (marked **[measured, this box]**);
every cost figure is marked **[estimate]** with its basis stated. No citation, DOI,
URL, or number below was invented; where I could not verify something I say so.

## What "our stack" and "our cases" mean here

- OpenFOAM v2506/2606 + DAFoam (`dafoam/opt-packages` Docker image), incompressible
  RANS, SA and k-omega SST, discrete adjoint via `DAFoam`/PETSc.
- Our closure-challenge entry (`demo-output/website/closure_challenge_trained_entry_round2.json`)
  scores **0.0741** against a RANS-identity floor of **0.1036**
  (`demo-output/website/closure_challenge_rans_floor.json`) and a docket-recorded
  rank-4 target of **0.0779** (Montoya, Oulghelou, Cinnella).
- The benchmark is **McConkey, Buchanan, Smidt, Bodner, Dwight, Cinnella, "The Closure
  Challenge: a benchmark task for machine learning in turbulence modelling,"
  arXiv:2603.28884** — repo `github.com/rmcconke/closure-challenge-benchmark`
  (commit `deb91557184af3cb95f5190494ec52d8f2c6a0d1`, the same commit our own
  provenance record used), eval package `github.com/rmcconke/closure-challenge`.
  The 8 test cases: 4 periodic-hill (`alpha_15_13929_4048`, `alpha_15_13929_2024`,
  `alpha_05_4071_4048`, `alpha_05_4071_2024`), 3 square-duct
  (`AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180`), and `NASA_2DWMH`.
- **The benchmark's own scratch clone is still present on this box**, at
  `/home/ubuntu/closure-challenge-benchmark/` (used earlier by
  `sdk/scripts/run_closure_challenge_evidence.py`). I read its `README.md`,
  `data/`, and `submissions/` directly rather than relying only on web search —
  this is the single most load-bearing source in this report and is cited
  throughout as **[local clone]**.

## Headline finding before the ranked picks

**The benchmark's own public leaderboard already contains a FIML-lineage entry,
scored on our exact 8 test cases, that outperforms our current entry.** Rank 2,
"Wu and Zhang," scores **overall 0.0624** — better than both our 0.0741 and the
docket's rank-4 target of 0.0779 — using a DAFoam-adjoint field-inversion method.
This is Pick 1 below, and it changes what "reproduction" means for this pick: we
are not inferring overlap from a paper written for a different benchmark, we are
looking at a submission scored by the benchmark's own steward on the same ground
truth we are scored against.

Leaderboard (`/home/ubuntu/closure-challenge-benchmark/README.md`, **[local clone]**):

| Rank | Authors | Overall | Method (from submission materials) |
|---|---|---|---|
| 1 | Reissmann & Fang | 0.0595 | Differential evolution + gene-expression-programming symbolic regression for anisotropic stress + k-omega coefficients. **Not FIML** (gradient-free, no field inversion) — checked directly, see Rejected candidates. |
| **2** | **Wu and Zhang** | **0.0624** | **DAFoam discrete-adjoint field inversion + symbolic regression (SST-QCRC). FIML lineage, our stack. Pick 1.** |
| 3 | Liu, Wang, Zhao, Xiao (arXiv:2509.17189) | 0.0737 | Multi-objective ML learning framework. **Not confirmed field-inversion/adjoint** — checked directly, see Rejected candidates. |
| 4 | Montoya, Oulghelou, Cinnella | 0.0779 | Already our docket's recorded external target; not re-researched here. |

---

## Pick 1 (highest overlap — RANK THIS FIRST): Wu, Zhang & Zhang, DAFoam field inversion

**Method paper citation:** Wu, C., Zhang, S., Zhang, Y. "Development of a
Generalizable Data-Driven Turbulence Model: Conditioned Field Inversion and
Symbolic Regression." *AIAA Journal* 63(2), 2025, pp. 687–706.
DOI: `10.2514/1.J064416`. Open preprint: **arXiv:2402.16355**
(https://arxiv.org/abs/2402.16355, resolves — fetched full text via the arXiv PDF,
extracted with `pypdf`, 48 pp., saved locally during this research).

**Direct benchmark submission (same authors, applied to our exact 8 cases):**
Wu, C., Zhang, Y. "The Training of the SST-QCRC Model" — description document for
the `rmcconke/closure-challenge-benchmark` submission, rank 2 on the leaderboard
above. Location: `submissions/wu/description_document.pdf` in the benchmark repo
(**[local clone]**, also at
`https://github.com/rmcconke/closure-challenge-benchmark/blob/main/submissions/wu/description_document.pdf`).
I read this document directly (4 pp., extracted with `pypdf`) — it is the most
important single source in this report.

### Where the data lives

| Case family | Public source | Verified |
|---|---|---|
| NASA hump (training data for the AIAA J paper's field inversion) | Uzun, A., Malik, M.R. "Wall-resolved large-eddy simulation of flow separation over NASA wall-mounted hump." 55th AIAA Aerospace Sciences Meeting, 2017. DOI `10.2514/6.2017-0538` — full LES field **not confirmed publicly downloadable** (see caveat below) | Citation confirmed in the paper's own reference list (ref [53]) |
| NASA hump — experimental Cf/Cp/PIV data actually usable as a public field-inversion target | NASA Turbulence Modeling Resource, `https://turbmodels.larc.nasa.gov/nasahump_val.html` (redirects to `tmbwg.github.io/turbmodels/nasahump_val.html`) — `noflow_cp.exp.dat`, `noflow_cf.exp.dat`, `noflow_u_inflow.exp.dat`, `noflow_vel_and_turb.exp.dat`, `Noflow_PIV_exp.zip`, plus grids (with and without plenum). Re_c = 936,000, M = 0.1. | Fetched directly, links present |
| CBFS (curved backward-facing step, the other field-inversion training case) | Bentaleb, Y., Lardeau, S., Leschziner, M.A. "Large-Eddy Simulation of Turbulent Boundary Layer Separation from a Rounded Step." *J. Turbulence* 13, 2012, N4. DOI `10.1080/14685248.2011.637923`. Benchmark mirror: `turbmodels.larc.nasa.gov/Other_LES_Data/curvedstep.html` | Cited in paper ref [54]; benchmark README lists the LARC mirror |
| Periodic hills (cross-validation case in the AIAA J paper, and the exact family of our 4 PH test cases) | Xiao, H., Wu, J.-L., Laizet, S., Duan, L. "Flows over Periodic Hills of Parameterized Geometries: A Dataset for Data-Driven Turbulence Modeling from Direct Simulations." *Computers & Fluids* 200, 2020, 104431. DOI `10.1016/j.compfluid.2020.104431`. Data repo: `https://github.com/xiaoh/para-database-for-PIML` | Fetched repo directly; benchmark README confirms this is the **same** original-data link it uses for `Parm_PH_29` |

**Our own DUCT test cases are not covered by either the AIAA J paper or the
benchmark submission's training** — the submission scores DUCT purely by
zero-shot generalization of a model trained only on CBFS (see below). This is
disclosed plainly by the authors, not hidden.

### What the correction modifies (I read the equations directly)

Two independent modifications, both to the k-omega SST baseline (submission
doc, §1, my transcription of the extracted equations):

1. **A QCR2000-style quadratic (Boussinesq-breaking) term added to the Reynolds
   stress**, with a fixed coefficient C_cr1 = 0.3 taken directly from Spalart's
   SA-QCR2000 paper — **not trained, not part of the field inversion.**
2. **A multiplicative correction on the destruction term of the omega equation**:
   `destruction_new = destruction_omega × [(β(x) − 1)·f_d + 1]`, where `f_d` is
   Spalart et al.'s DES shielding function (0 in the boundary layer, 1 outside),
   and **β(x) is the field-inverted quantity** — this is the classic FIML
   correction factor, traced explicitly by the authors to Singh & Duraisamy
   (2016), and it is bounded `β(x) ≤ 4` in practice. β is obtained on the CBFS
   mesh by minimizing the discrepancy between RANS `Ux` and the CBFS LES
   reference at sampled points, via **PDE-constrained optimization using
   DAFoam's discrete adjoint** (submission doc, §2: "The code used to perform
   the field inversion is DAFoam, developed by He et al [5]" — He, P., Mader,
   C.A., Martins, J.R.R.A., Maki, K.J., "DAFoam: An Open-Source Adjoint
   Framework for Multidisciplinary Design Optimization with OpenFOAM," *AIAA
   Journal* 58(3), 2020, 1304–1319, DOI `10.2514/1.J058853` — **the same tool
   this lab uses**).
3. **β(x) is then distilled into a closed-form expression** via symbolic
   regression (PySR) over 3 input features (non-dimensional strain/rotation-rate
   invariants and a Pk/epsilon-type ratio — the OCR extraction of the exact
   symbol names is not fully clean, flagged rather than guessed). The submission
   document's final fitted expression (its Eq. 3, transcribed as extracted,
   OCR-uncertain on the exact feature symbol):
   `β_correction = max(−0.1157, 0.0058525 × [feature])`.

**Does our DAFoam adjoint drive the same inversion?** Yes, directly — this is
literally the same code (`DAFoam`, He et al. 2020) driving the same kind of
optimization problem (minimize ‖U_RANS − U_reference‖ over a spatially varying
field entering the omega destruction term) that our stack is already set up to
run. This is the strongest "our stack can build it" answer of any pick.

### Baseline (uncorrected RANS) case setup, measured from the benchmark's own logs

The benchmark's local scratch clone ships the actual OpenFOAM case directories
used to generate its baseline k-omega SST fields, including run logs
(**[local clone]**, `/home/ubuntu/closure-challenge-benchmark/data/`):

| Case | Cells (from `polyMesh/owner` header) | Ranks | Measured baseline wall time | Measured core-minutes |
|---|---|---|---|---|
| `NASA_2DWMH` | **51,626** | 4 (`log.decomposePar`) | 89.76 s/rank, 2000 iterations | **~6.0** [measured, this box] |
| `CBFS` | **21,000** | 1 (serial `simpleFoam`, no `decomposeParDict` present) | 1015.9 s | **~16.9** [measured, this box] |
| `PH_Breuer` (the Re=10595 periodic-hill case in this benchmark's own training pool, from `turbmodels.larc.nasa.gov/Other_LES_Data/2dhill_periodic.html`) | **15,600** | 8 (`decomposeParDict: numberOfSubdomains 8`) | 447.84 s/rank | **~59.7** [measured, this box] |
| `Parm_PH_29` (our 4 PH test cases' family), e.g. `AR` duct cells for reference | not separately re-derived — mesh sizes for our 3 DUCT test cases are `AR_1_Ret_360`: 3,025 cells, `AR_3_Ret_360`: 8,748 cells, `AR_14_Ret_180`: 31,819 cells (`polyMesh/owner` headers, **[local clone][measured, this box]**) | — | — | — |

Our own stack has already run comparable meshes: ladder A1 (NACA0012, 4,032
cells, DAFoam `DASimpleFoam`, 2 ranks) took 1.30 core-minutes for
`compute_totals` (primal+adjoint+total-derivative) and 1.80 core-minutes for a
full central-difference FD verification (21 primal solves)
(`demo-output/website/dafoam/ladder-a/A1_naca0012_incompressible.json`,
**[measured, this box]**). This says our stack's per-solve overhead on small 2D
meshes is a few seconds to ~1 core-minute — consistent with, and slightly
cheaper than, the benchmark's own baseline-generation numbers above (different
solver settings, so not a strict apples-to-apples comparison).

**Can our stack build these baselines?** Yes — plain incompressible k-omega SST
`simpleFoam`/`DASimpleFoam` on 2D structured-ish meshes at these cell counts
(21k–52k) is well inside what this lab already runs routinely (naca0012 at 4k
cells, naca4412 wing at 337k cells).

### Cost estimate for the field-inversion step [ESTIMATE]

**Basis:** the AIAA J paper states the NASA-hump field inversion "achieve[s]
convergence after approximately 140 SLSQP iterations" (paper text, §3.1.2). I do
not know the per-iteration cost breakdown from the paper (it doesn't report
wall-clock time). Extrapolating from our own DAFoam evidence — a single
primal+adjoint `compute_totals` call on a 4,032-cell case costs 1.3 core-minutes,
and a warm-started re-solve should be cheaper than a cold-start primal — and from
the benchmark's own baseline costs above (CBFS ~17 core-min for a full cold
convergence at 21,000 cells; NASA_2DWMH ~6 core-min at 51,626 cells for 2000
iterations at 4 ranks):

- **If each SLSQP iteration costs roughly 1–3 core-minutes** (a warm-started
  primal+adjoint pair on a 15k–52k-cell 2D mesh, scaled from our 4k-cell
  1.3-core-min data point and the benchmark's own cold-convergence figures
  above), **140 iterations ≈ 140–420 core-minutes (2.3–7 core-hours)** per
  field-inversion run (one for CBFS, one for the NASA-hump variant if we choose
  to redo both training cases rather than reusing the paper's CBFS-only route
  the submission took).
- This is an order-of-magnitude estimate, not a measurement. The dominant
  unknown is whether DAFoam re-converges the primal from a warm start in a
  handful of SIMPLE iterations per SLSQP step (cheap) or effectively restarts
  full convergence each time (expensive, closer to the 17–60 core-min baseline
  figures per step, which would push the total into the hundreds of core-hours
  and make this pick materially more expensive). **This uncertainty should be
  resolved with a short timed pilot (a handful of SLSQP iterations, timed) before
  committing to a full field-inversion budget** — that pilot is itself cheap
  (a few core-minutes) and is the natural next compute rung after this
  research-only one.

### Comparison target

The benchmark's own scorer, `closure_challenge.score()`/`evaluate_by_case()`
(the same one our `closure_challenge_rans_floor.json` and
`closure_challenge_trained_entry_round2.json` already call), against the
per-case scores in the leaderboard table above: **overall 0.0624**, with
per-case breakdown `alpha_15_13929_4048: 0.0813`, `alpha_15_13929_2024: 0.1195`,
`alpha_05_4071_4048: 0.0569`, `alpha_05_4071_2024: 0.0848`, `AR_1_Ret_360:
0.0455`, `AR_3_Ret_360: 0.0399`, `AR_14_Ret_180: 0.035`, `NASA_2DWMH: 0.0364`
(**[local clone]**, `README.md`). Secondarily, the AIAA J paper's own Figures 10
(streamline plot, LES vs. baseline SST vs. FI-CLS vs. FI-CND on the NASA hump),
11 (velocity profiles at downstream stations), and 24–27 (periodic-hill friction
coefficient and velocity-profile comparisons) are the paper-native figures to
reproduce against if we redo the field inversion ourselves rather than only
re-scoring the authors' own CSV predictions.

---

## Pick 2: Volpiani et al. (2021), data-assimilation + ML Boussinesq-correction on periodic hills

**Citation:** Volpiani, P.S., Meyer, M., Franceschini, L., Dandois, J., Renac, F.,
Martin, E., Marquet, O., Sipp, D. "Machine learning-augmented turbulence modeling
for RANS simulations of massively separated flows." *Physical Review Fluids* 6,
064607 (2021). DOI: `10.1103/PhysRevFluids.6.064607`.

**Verification method and its limit, stated plainly:** the publisher page
(`journals.aps.org`) and the HAL open-access postprint
(`hal.archives-ouvertes.fr/hal-03285669`) both returned bot-protection blocks
(403 / Anubis challenge page) to my fetch tools, so **I could not read the full
text**. What I have is verified via the Semantic Scholar API (which resolves
against CrossRef, not a search-engine summary): exact title, all 8 authors,
venue, year, and the paper's own abstract, quoted in full: *"We combine data
assimilation and machine learning to correct the RANS Spalart-Allmaras
turbulence model. The final neural-network contribution is a
Boussinesq-correction, rather than a turbulent eddy-viscosity adjustment. Flows
over periodic hills at distinct Reynolds numbers and geometries were selected to
demonstrate the potential gain of machine learning-augmented turbulence
models."* Semantic Scholar also lists the HAL postprint as **green open
access**, i.e. legitimately free, even though I could not personally retrieve it
past the bot gate.

### Where the data lives

**Not independently confirmed for this specific paper.** The abstract says
"periodic hills at distinct Reynolds numbers and geometries" — this is
consistent with either the same `Parm_PH_29` (Xiao et al. 2020) dataset Pick 1
uses, or a different multi-Reynolds periodic-hill archive (e.g. the classic
Breuer/Rapp-Manhart family). **I flag this as unresolved** rather than assume
it is the same dataset as Pick 1 — doing so would be exactly the kind of
unverified inference the task rules warn against. If it is the Xiao dataset, the
overlap with our 4 PH test cases is as strong as Pick 1's; if it is a different
periodic-hill archive, the overlap is "same case family, different specific
geometries/Re," which is weaker but still directly relevant to the closure our
entry is weakest on.

### What the correction modifies, and can our stack drive it

The abstract is explicit that the correction is **a Boussinesq-correction term**
(i.e., an addition to the Reynolds-stress tensor beyond the linear
eddy-viscosity relation) rather than a scalar multiplier on eddy viscosity —
this is architecturally different from Pick 1's destruction-term multiplier.
"Data assimilation" strongly suggests an adjoint or variational inverse problem
(this ONERA group, particularly Marquet and Sipp, is well known for adjoint and
global-stability methods), but **I did not obtain the paper's own description of
the inversion algorithm and cannot confirm it is DAFoam-drivable versus a
different in-house adjoint solver** without the full text. This should be
resolved before committing compute to this pick specifically.

### Cost and comparison target

**Not estimated** — without the full text I do not know the mesh sizes,
iteration counts, or which specific figure to reproduce against, and I would
rather report that gap than invent numbers. If this pick is pursued, the first
step is obtaining the paper (institutional access, or a direct request to the
authors, or retrying the HAL link with a real browser rather than an automated
fetch) before any cost estimate is made.

---

## Pick 3 (lowest confidence, included for completeness — flag reader accordingly): Volpiani et al. (2026), field inversion + symbolic regression on the NASA hump

**Citation, as far as verified:** Volpiani, P.S. et al., "Improving the
Spalart-Allmaras Turbulence Model for Separated Flows Using Field Inversion and
Symbolic Regression," *Physical Review Fluids*, 2026. DOI: `10.1103/dk9r-td14`,
published 16 July 2026.

**What is and is not verified.** The DOI, title, venue, and year are confirmed
via the Semantic Scholar API (CorpusId 289239506) and independently via two
separate web searches returning consistent case-list text. The contact author is
confirmed as P.S. Volpiani (ONERA) from search-engine indexing of the abstract
page. **I could not obtain the full author list, the abstract text, or the
paper's own description of the correction equations** — the publisher page
403'd, Semantic Scholar's own record shows `abstract: null` and
`openAccessPdf.status: CLOSED`, and I found no arXiv/HAL preprint. What I have
instead is consistent (appearing near-verbatim across two independent search
queries) search-engine-indexed text stating the paper uses "data assimilation
and symbolic regression... addressing local deficiencies in its production
term," with "symbolic regression... performed using assimilated data from
two-dimensional separated-flow cases including the converging-diverging
channel, bump H42, and NASA wall-mounted hump." I am reporting this as
**search-snippet-level confidence, not primary-source confidence** — it is
plausible and internally consistent (it reads as a direct successor to Pick 1's
lineage, correcting the SA production term instead of the SST destruction
term), but I have not read it myself and would not want to be quoted on its
exact equations or figures.

### Where the data lives

`NASA wall-mounted hump` — same public source as Pick 1
(`turbmodels.larc.nasa.gov/nasahump_val.html`), already verified above. "Bump
H42" and "converging-diverging channel" data sources **were not researched** in
this rung (out of scope given the low confidence already flagged, and given the
NASA-hump overlap alone was the reason for including this pick).

### Everything else

**Not estimated.** Baseline setup, correction mechanism precision, cost, and
comparison figure are all withheld pending actually reading the paper. This
pick should be treated as "worth chasing down via a real subscription/ILL
request," not as ready to plan compute against.

---

## Rejected / considered-and-set-aside candidates

**Reissmann & Fang (leaderboard rank 1, 0.0595).** Checked directly
(`/home/ubuntu/closure-challenge-benchmark/submissions/reissmann/reissmann_info.txt`
and `score_eval.ipynb`, **[local clone]**). Method: differential evolution (Storn
& Price, 1995) to fit k-omega SST coefficients, plus Gene Expression Programming
(a symbolic-regression variant, `github.com/maxreiss123/GeneExpressionProgramming.jl`)
for the anisotropic-stress correction. This is gradient-free global optimization,
not field inversion via an adjoint — **rejected as a FIML-lineage pick**, despite
being the top scorer, because it doesn't answer the question asked (does DAFoam's
adjoint drive this same inversion — there is no adjoint here to match).

**Liu, Wang, Zhao, Xiao (leaderboard rank 3, 0.0737, arXiv:2509.17189).** Fetched
directly. Title: "Toward a unified data-driven turbulence model through
multi-objective learning." Abstract describes a multi-objective ML framework
learning from "sparse, indirect observations" — plausibly related to Xiao's
ensemble-Kalman-method lineage, but **the fetched summary explicitly could not
confirm this is a field-inversion/adjoint approach**, and no correction-term
mechanism was identified. **Set aside, not confirmed FIML**, rather than
included on an assumption.

**Singh, Medida, Duraisamy (2017), "Machine-Learning-Augmented Predictive
Modeling of Turbulent Separated Flows over Airfoils," AIAA Journal 55(7),
2215–2227, DOI `10.2514/1.J055595`, open preprint arXiv:1608.03990.** This is
genuinely foundational FIML lineage (Duraisamy group), and it is the paper Pick
1's β(x) mechanism traces back to. I fetched the full arXiv text (32 pp.) and
searched it directly for "periodic hill," "FAITH," "duct" — **zero matches on
all three.** The paper's cases are entirely S809-airfoil-based (training on a
few angles of attack, generalizing to others and to a different airfoil). **No
geometric overlap with our 8 test cases** — rejected as a pick on overlap
grounds, not a data-availability problem. (An earlier AI-generated search
summary I initially received claimed this paper tested on "periodic hills at
Reh=10595 and the 3D FAITH hill" — I checked the primary source directly and
this claim does not appear in the paper's text. I am flagging that I nearly
repeated an unverified claim and did not, per the hard rule against fabrication.)

**Singh & Duraisamy (2016), "Using field inversion to quantify functional errors
in turbulence closures," Physics of Fluids 28(4), 045110, DOI
`10.1063/1.4947045`.** The methodology paper Pick 1's submission cites as the
source of its field-inversion algorithm (submission doc ref [4]). Search-result
text (not primary-source-verified, since I did not fetch the full paper)
describes its cases as **channel flow and flat plate** — no periodic-hill,
duct, or hump overlap. Not selected as a pick for the same reason as above;
noted here as lineage context for Pick 1 only.

**An "ANN-QCR" adjoint field-inversion paper on square-duct secondary flows.**
Multiple searches turned up consistent, detailed method descriptions —
"adjoint-based field inversion optimizes a spatially varying non-linear stress
coefficient C_cr1(x) in the QCR formulation... a neural network then learns the
mapping... FIML updates ANN-QCR weights directly by the gradient-based discrete
adjoint method" — applied to square-duct secondary-flow prediction, which would
have been an excellent overlap with our 3 DUCT test cases. **I could not pin
down the authors, title, journal, or a DOI for this paper** despite several
searches; the description keeps surfacing as an uncited summary fragment
without a traceable primary source. **I am explicitly not naming it as a pick
and not guessing a citation** — this is a real gap in this report: our square
duct family (`AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180`) has no confirmed
FIML-lineage reproduction target in this rung. If it becomes worth chasing, the
next step is a proper literature-database search (Scopus/Web of Science) rather
than open web search, since it clearly exists somewhere I couldn't cleanly cite.

---

## Summary table

| Rank | Paper | Overlap with our 8 cases | Data public? | Our stack can drive it? | Cost estimate |
|---|---|---|---|---|---|
| 1 | Wu, Zhang & Zhang (AIAA J 2025 / arXiv:2402.16355) + their closure-challenge submission | **Directly scored on all 8**, via CBFS-only training + zero-shot generalization; PH family is the exact `Parm_PH_29`/Xiao dataset our 4 PH cases come from | Yes — NASA hump exp. data, CBFS LES ref., Xiao PH dataset all confirmed public | **Yes — literally uses DAFoam** | 140-iteration field inversion, [estimate] 140–420 core-min, pending a timed pilot |
| 2 | Volpiani et al. 2021, PRF 6, 064607 | Periodic hills, "distinct Re and geometries" (dataset identity not confirmed) | Partially — case family known, exact dataset unconfirmed | Not confirmed (data assimilation, adjoint plausible but unverified) | Not estimated — full text inaccessible |
| 3 | Volpiani et al. 2026, PRF, DOI 10.1103/dk9r-td14 | NASA wall-mounted hump (search-snippet confidence only) | NASA hump: yes (same source as Pick 1). Bump H42 / CD channel: not researched | Not confirmed | Not estimated — full text inaccessible, low confidence throughout |

**Bottom line for whoever picks this up next:** Pick 1 is ready to move to a
compute rung — the data sources are verified public, the correction mechanism
and tool (DAFoam) are confirmed identical to ours, real baseline mesh/cost
numbers exist from the benchmark's own logs, and there is a same-benchmark
score (0.0624) to beat/match. Picks 2 and 3 need a full-text read (library
access or a direct author request) before any compute commitment — do not plan
core-hours against them yet.
