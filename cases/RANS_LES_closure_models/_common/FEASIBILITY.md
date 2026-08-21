# Feasibility matrix: which data-driven closure papers can be reproduced here

Phase 2b of the closure-modelling charter. One row per ML / DL / UQ paper the
charter names. For each: the paper's own headline case and number, **taken only
from a PDF whose printed title page I checked**, where in the paper that number
lives, what data a reproduction needs and whether we have it, the size of the
model, a core-hour estimate on this machine, and a verdict.

**Machine:** 16 cores, 30 GB RAM, no GPU. `python` =
`/home/ubuntu/closure-venv/bin/python` (numpy 2.5.1, scipy 1.18, scikit-learn
1.9.0, matplotlib; `Ofpp`; the `closure_challenge` scorer as an editable install).
`torch` **2.13.0+cpu is now installed** (added during this session from
`https://download.pytorch.org/whl/cpu`); it was absent when this matrix was
started, and several verdicts below were written before it arrived.
**OpenFOAM v2606 is installed** at `/usr/lib/openfoam/openfoam2606` and
`simpleFoam` runs, so a-posteriori (re-solved) propagation is available, not just
a-priori scoring. That is the single most important capability finding in this
file: several of these papers are only meaningful a-posteriori.

**Data on disk:** the Closure Challenge benchmark clone at
`/home/ubuntu/closure-challenge-benchmark`, commit
`deb91557184af3cb95f5190494ec52d8f2c6a0d1` - 29 parametric periodic hills
(`Re_H` 5600), the Breuer periodic hill at `Re_H` 10595, a curved backward-facing
step at `Re_H` 13700, the NASA 2-D wall-mounted hump at `Re_c` 936000, and 8
square/rectangular ducts at `Re_tau` 164-342, with interpolated LES/DNS truth on
every RANS mesh. Full inventory and the k-omega SST baseline errors:
`BASELINES.md`. Downloaded data lives **outside** the repo, in
`/home/ubuntu/closure-data/`, with source URL and sha256 recorded in the
reproduction's own `RESULTS.md`.

## 0. Source-status legend

| Tag | Meaning |
|---|---|
| **VERIFIED-PDF** | the PDF is in `docs/papers/closure/`, its **printed title page** matches the paper, and the number quoted below was read off the page named |
| **BLOCKED-ON-SOURCE** | no verified PDF on this machine. The paper's number is deliberately **not** stated, because stating a number from memory is how the corpus defect of 2026-08-20 happened. Retrieval attempted; result recorded |

Of the 29 papers the charter lists, **18 are VERIFIED-PDF** and **11 are
BLOCKED-ON-SOURCE** as of this writing (a background open-access retrieval for
most of the 11 was still running, and Guan 2022 landed mid-session). Nothing
below states a paper's headline number unless it came from a verified page.

**One paper not on the charter list arrived and is worth adding**: Wu, Xiao,
Sun & Wang, *RANS Equations with Explicit Data-Driven Reynolds Stress Closure
Can Be Ill-Conditioned*, arXiv:1803.05581v3 (JFM 869:553-586, 2019),
`docs/papers/closure/Wu2018_rans_explicit_closure_ill_conditioned.pdf`,
**VERIFIED-PDF**. It is the companion that states quantitatively why an
a-priori improvement in `b_ij` need not survive being re-solved, and it is the
paper every a-posteriori verdict in this programme should be read against.

## 1. The matrix

### 1.1 RANS anisotropy learning (tensor-basis family)

| Paper | Source status | Headline case + number + where | Data needed / have? | Model size | Core-hours (16 cores) | Verdict |
|---|---|---|---|---|---|---|
| **Ling, Kurzawski & Templeton 2016**, TBNN (SAND2016-7345J, JFM 807:155-166) | **VERIFIED-PDF** | RMSE of `b_ij` on two held-out flows, **Table I, p. 11**: duct `Re_b`=2000 - LEVM 0.23, QEVM 0.18, **TBNN 0.13**, plain MLP 0.33; wavy wall `Re`=6850 - LEVM 0.18, QEVM 0.11, **TBNN 0.08**, MLP 0.09. Stated as "43% more accurate than the LEVM" (duct) and "56% reduction ... with respect to LEVM" (wavy wall), pp. 10-11. Train: duct `Re_b`=3500, channel `Re_tau`=590, two jets in crossflow, square cylinder, converging-diverging channel (6 cases). Validation: wall-mounted cube `Re_b`=5000. Test: duct `Re_b`=2000, wavy wall `Re`=6850 (p. 8) | Their 9-flow database is **not** on disk and is not distributed as one archive. The benchmark's ducts and hills give the same *flow classes* (secondary flow; separation) at different `Re` and geometry | TBNN: 8 hidden layers x 30 nodes, 5 invariants in, 10 `g^(n)` out, multiplied by `T^(1..10)` (p. 9). Baseline MLP: 10 x 10, lr 2.5e-6 (p. 6). ~10^4 parameters | training: **< 0.5** (10^5-10^6 samples, 10^4-parameter net, CPU). Feature/basis assembly on 641k cells: ~0.2 | **FEASIBLE-AS-LABELLED-VARIANT** - the architecture reproduces exactly; the *cases* cannot, so the number 0.13 is not directly comparable. Reproduce as: TBNN on benchmark hills -> held-out ducts, scored against the SST `b_rms` rows of `BASELINES.md` |
| **Kaandorp & Dwight 2020**, TBRF (Comput. Fluids, arXiv:1810.08794v2) | **VERIFIED-PDF** | (a) RMSE of `b_ij`, square duct `Re`=3500, **Table 3, preprint p. 37**: 5 features (S,R only) TBRF **0.0995** / TBNN 0.0871; 17 features TBRF **0.0521** / TBNN 0.0681. (b) Backward-facing step `Re`=5100 reattachment, **Table 4, preprint p. 41**: RANS 5.45, **RANS+`b_TBRF` 6.32**, DNS 6.28, experiment 6.0 +/- 0.15. Train for all four cases: PH5600 + PH10595 + CD12600, `N_sample` = 21,000 (Table 2, p. 31; hyper-parameters p. 30) | **Best match in the whole list.** PH10595 (Breuer) and CBFS13700 are the *same cases* in our benchmark; PH5600 exists as the 29-hill family; square ducts exist at `Re_tau` 164-342. Missing: CD12600 (converging-diverging channel, Laval & Marquillie) and BFS5100 | 100 tensor-basis decision trees, 11 of 17 features per split, min 9 samples/leaf, regularisation `Gamma`=1e-12 (pp. 30-31). Custom TBDT: each split solves a least-squares fit of `b = sum g^(n) T^(n)` | TBDT training is the cost. 21k samples x 17 features x 10-tensor LSQ per candidate split. Estimate **2-6 core-hours** for 100 trees with `joblib` over 16 cores; bounded by capping tree depth | **FEASIBLE** - and it is the primary Phase-3 target after TBNN, because the training and test cases overlap our data almost exactly |
| **Wu, Xiao & Paterson 2018**, PIML random forest (Phys. Rev. Fluids 3:074602, arXiv:1801.02762v4) | **VERIFIED-PDF** | Framework paper. Two cases (preprint pp. 20-22): square duct - train `Re`=2200/3500 (Pinelli DNS), predict `Re`=125000 (Gessner & Emery experiment); periodic hills - train on a **steeper hill, hill width 0.8x**, predict the standard hill at `Re`=5600. Its quantitative claims are made through profile figures rather than a single error table; the two innovations it states are the integrity-basis feature set (Tables 1-2) and **separating the linear from the nonlinear part of `tau`** to avoid ill-conditioning of the RANS equations (abstract) | Excellent fit. The hill-geometry-transfer experiment is *exactly* the `alpha_05...alpha_15` axis of our 29 parametric hills, at fixed `Re`=5600. Duct `Re` extrapolation maps onto `Ret_180 -> Ret_360` | scikit-learn random forest, ~100 trees, ~47 features from the integrity basis (their sec. 2.1) | **< 0.5** core-hours (sklearn RF on 3x10^5 samples, 16 threads) | **FEASIBLE**. Its ill-conditioning point is the one to test: predict `b`, then re-solve in `simpleFoam` and check whether `U` improves or degrades |
| **Schmelzer, Dwight & Cinnella 2020**, SpaRTA (Flow Turb. Combust. 104:579-603, arXiv:1905.07510v2) | **VERIFIED-PDF** | Table 1 (ceiling, preprint p. 5): `eps(U)/eps(U_0)` = **0.00165** PH10595, **0.22703** CBFS13700. Table 2 (discovered models, p. 14): **0.22287** PH10595 (M1), **0.30413** CBFS13700 (M1). Both cases are **literally our cases**, and both are normalised by the k-omega SST baseline, so these are directly quotable targets | PH10595 and CBFS13700 both on disk | elastic net over a tensor-polynomial library; discovered models are 1-5 terms | **ALREADY SPENT: 2.7 core-hours, 2026-08-01** | **DONE — do not re-run.** See `../Schmelzer2020_SpaRTA/RESULTS.md`. Ceiling PASS (PH 0.003331 HIT its band; CBFS 0.39753 factor-2 PASS). Table 2 reproduced (discovered-on-CBFS 0.36051 HIT +/-25%; discovered-on-PH 0.14292, better than published). Form `T1` recovered exactly; PH coefficient 1.39917 vs 1.39. **Open work is the cross-validation rung only**, blocked on a form-pruning rule and CD12600 data, not on compute |
| **Weatheritt & Sandberg 2016**, GEP algebraic stress | **BLOCKED-ON-SOURCE** (open-access retrieval running; JCP paywall) | not stated - no verified page | training data would be the same hills/ducts | symbolic; population-based | GEP with population 100 x 500 generations on 10^5 samples: **10-40** core-hours, and it is embarrassingly parallel | **BLOCKED** on the source. Compute is affordable; the barrier is the paper |
| **Ling & Templeton 2015**, ML for regions of high RANS uncertainty | **BLOCKED-ON-SOURCE** | not stated | classifier labels would be derived from `BASELINES.md` per-cell errors | SVM / RF classifier | **< 0.5** | **BLOCKED** on the source |

### 1.2 RANS discrepancy, inversion and Bayesian UQ

| Paper | Source status | Headline case + number + where | Data needed / have? | Model size | Core-hours | Verdict |
|---|---|---|---|---|---|---|
| **Wang, Wu & Xiao 2017**, PIML reconstruction of `tau` discrepancy (Phys. Rev. Fluids 2:034603, arXiv:1606.07987v2) | **VERIFIED-PDF** | Abstract, preprint p. 1: square duct at various `Re`; periodic hills with two training scenarios - "the same periodic hills geometry yet at a lower Reynolds number" and "a different hill geometry with a similar recirculation zone". Reports "excellent predictive performances" qualitatively; the quantities are per-profile figures | Both scenarios map onto our data directly (29 hills span geometry at fixed `Re`; ducts span `Re_tau`) | random forest on mean-flow features | **< 0.5** | **FEASIBLE**. Effectively the predecessor of Wu 2018; reproduce them together |
| **Xiao et al. 2016**, data-driven Bayesian model-form UQ (Comput. Fluids, arXiv:1508.06315v3) | **VERIFIED-PDF** | Abstract, preprint p. 1: iterative ensemble Kalman inversion of the Reynolds stress with realisability/smoothness/symmetry constraints, on periodic hills and a square duct; claim is that "even with very sparse observations, the obtained posterior mean velocities ... have significantly better agreement with the benchmark data" and "at most locations the posterior distribution adequately captures the true model error" | Needs repeated forward RANS solves inside the EnKF loop. OpenFOAM is available, so this is possible - but an ensemble of ~50 members x ~30 iterations x ~0.3 core-hours = **~450 core-hours** for one case | ensemble of ~50 | **~450 for one case** - within the 487 pre-authorised limit but only just, and only for a single case. A 20-member, 20-iteration variant is **~120** | **FEASIBLE-AS-LABELLED-VARIANT** at reduced ensemble size. Full-size on more than one case would exceed the compute authorisation and must be costed first |
| **Emory, Larsson & Iaccarino 2013**, structural uncertainty via eigenvalue perturbation | **BLOCKED-ON-SOURCE** (Phys. Fluids; retrieval running) | not stated | **no training at all**; needs only the shipped SST fields plus 5 perturbed re-solves per case (`1c`, `2c`, `3c` corners plus eigenvector permutations) | none | 5 perturbed solves x 41 cases x ~0.3 = **~60** core-hours; a 3-case demonstrator is **~5** | **BLOCKED on source, FEASIBLE the moment it arrives.** This is the cheapest high-value item in the list and needs no ML. The falsifiable question - *does the LES truth lie inside the envelope?* - can be answered a-priori on frozen fields for **< 1 core-hour**, without any solve, and that variant is not blocked on compute at all |
| **Iaccarino, Mishra & Ghili 2017**, eigenspace perturbations | **BLOCKED-ON-SOURCE** (Phys. Rev. Fluids; retrieval running) | not stated | as above, plus the eigenvector-permutation extension | none | as above | **BLOCKED on source** |
| **Singh & Duraisamy 2016**, field inversion to quantify functional errors | **BLOCKED-ON-SOURCE** (retrieval running) | not stated | needs a discrete or continuous adjoint of the RANS + turbulence model. OpenFOAM's `adjointOptimisationFoam` exists in this build but is shape-optimisation-oriented; a 1-D or quasi-1-D hand-written adjoint is the realistic route | inversion field, one scalar per cell | 1-D/2-D hand-written adjoint, 100-300 optimisation iterations: **1-10** | **BLOCKED on source.** When it arrives: FEASIBLE only as a 1-D or 2-D VARIANT with a hand-written adjoint |
| **Parish & Duraisamy 2016**, FIML paradigm (JCP 305:758-774) | **BLOCKED-ON-SOURCE** (retrieval running) | not stated | as above | as above | as above | **BLOCKED on source** |
| **Singh, Medida & Duraisamy 2017**, ML-augmented modelling of separated flow over airfoils (AIAA J. 55(7), arXiv:1608.03990v3) | **VERIFIED-PDF** | Abstract, preprint p. 1: adjoint-based full-field inversion against **experimentally measured lift coefficient** for the SA model on airfoils; the NN-augmented SA model gives "much improved predictions in lift ... for geometries and flow conditions that were not used to train the model", "predicts surface pressures extremely well", and the improvement survives being embedded in a different commercial finite-element solver | **No airfoil case is on disk.** Would need airfoil geometries, meshes, and experimental `C_l` data from an external source | NN augmentation of the SA production term | mesh + adjoint per angle of attack; **20-80** | **BLOCKED** on data (not on the paper). Reproducing it means building an airfoil case set from scratch, which is a separate project |
| **Holland, Baeder & Duraisamy 2019**, FIML with embedded neural networks | **BLOCKED-ON-SOURCE** (retrieval running) | not stated | as Singh 2016 | -- | -- | **BLOCKED on source** |
| **Edeling, Cinnella & Dwight 2014**, Bayesian model-scenario averaging | **BLOCKED-ON-SOURCE** (retrieval running) | not stated | their scenario set is boundary-layer experiments (the classic Coles-Wadcock / Clauser families), **not on disk**; open sources exist | Bayesian averaging over model instances | **< 1** once the data exist | **BLOCKED on source and on data** |
| **de Zordo-Banliat, Dergham, Merle & Cinnella 2023**, space-dependent model aggregation (arXiv:2301.09013v1) | **VERIFIED-PDF** | Abstract, preprint p. 1: per-cell convex combination of competing turbulence-model solutions, weights regressed by a random forest on local flow features, giving "an ensemble solution accompanied by estimates of predictive uncertainty due to the turbulence model choice" | Requires **several different turbulence models solved on the same case**. The benchmark ships k-omega SST only. OpenFOAM can supply `kEpsilon`, `kOmega`, `SpalartAllmaras`, `LaunderSharmaKE` on the shipped meshes | random forest on local features | 4 models x 41 cases x ~0.3 core-hours = **~50** for the solve set, plus **< 0.5** for the RF | **FEASIBLE**, and unusually attractive: it is the only paper here whose *inputs* we would have to generate, and generating them (a 4-model solve sweep on the benchmark meshes) is independently useful as an extension of `BASELINES.md` |

### 1.3 LES subgrid learning

| Paper | Source status | Headline case + number + where | Data needed / have? | Model size | Core-hours | Verdict |
|---|---|---|---|---|---|---|
| **Maulik & San 2017**, blind deconvolution network (JFM 831:151-181, arXiv:1706.00912v2) | **VERIFIED-PDF** | Abstract, preprint p. 1: single-hidden-layer feed-forward network deconvolves coarse-grained fields **without knowing the filter**; a-priori tests on 2-D Kraichnan turbulence, 3-D Kolmogorov turbulence and compressible stratified turbulence | Needs DNS snapshots. **None on disk.** 2-D Kraichnan turbulence is cheap to generate here (pseudo-spectral, 1024^2, numpy/scipy) | one hidden layer | DNS generation 2-D 1024^2: **5-20**; training **< 0.5** | **FEASIBLE-AS-LABELLED-VARIANT** (2-D Kraichnan only; the 3-D cases are out of reach without a GPU) |
| **Maulik, San, Rasheed & Vedula 2019**, subgrid modelling of 2-D turbulence with NNs (JFM 858:122-144, arXiv:1808.02983v1) | **VERIFIED-PDF** | Abstract, preprint p. 1: maps stencils of vorticity and streamfunction plus two eddy-viscosity kernels to the sub-grid vorticity forcing; study is "both a-priori and a-posteriori" | as above | small MLP on stencils | as above | **FEASIBLE-AS-LABELLED-VARIANT** (2-D only) |
| **Beck, Flad & Munz 2019**, deep NNs for LES closure (JFM 870:106-120, arXiv:1806.04482v3) | **VERIFIED-PDF** | Abstract, preprint p. 1: CNNs on decaying homogeneous isotropic turbulence learn the exact closure terms with **"a cross correlation of up to 47% and even 73% for the inner elements"**, and they conclude "the current training success is data-bound"; the a-posteriori model is a "data-adaptive, pointwise eddy viscosity closure" | 3-D DNS of decaying HIT. Not on disk. 64^3-128^3 DNS is borderline feasible on 16 CPU cores | 3-D CNN - needs `torch`, and 3-D convolutions on CPU are slow | 128^3 DNS ensemble: **50-200**; CNN training on CPU: **20-100** | **BLOCKED on compute for the published configuration.** A 64^3 VARIANT is ~**20-40** core-hours and would be honest only if labelled as such. Their own "data-bound" conclusion means a scaled-down reproduction cannot test their claim |
| **Sirignano, MacArt & Freund 2020**, DPM (JCP 423:109811, arXiv:1911.09145v1) | **VERIFIED-PDF** | Abstract, preprint p. 1: adjoint-PDE-constrained training of an embedded network; on decaying isotropic turbulence the DPM "outperforms the widely-used constant-coefficient and dynamic Smagorinsky models, even for filter sizes so large that these established models become qualitatively incorrect", and "significantly outperforms a priori trained models" | 3-D DNS of decaying isotropic turbulence + a differentiable/adjoint 3-D solver | network inside the PDE; needs the adjoint solve every step | **>> 487** for the published setup on CPU | **BLOCKED on compute.** Estimate: even a 32^3 toy needs thousands of adjoint solves; a 1-D Burgers analogue is **~2** core-hours but is not this paper |
| **Park & Choi 2021**, NN LES of channel flow | **BLOCKED-ON-SOURCE** (retrieval running) | not stated | channel DNS | -- | -- | **BLOCKED on source** |
| **Guan, Chattopadhyay, Subel & Hassanzadeh 2022**, stable a-posteriori LES of 2-D turbulence with CNNs (JCP 458:111090, arXiv:2102.11400v1) | **VERIFIED-PDF** (arrived during this session) | Printed title, preprint p. 1: *Stable a posteriori LES of 2D turbulence using convolutional neural networks: **Backscattering analysis and generalization to higher Re via transfer learning***. The two testable claims are in that title: a-posteriori stability with backscatter, and `Re` generalisation by transfer learning | 2-D decaying / forced turbulence, self-generating here with a pseudo-spectral solver | CNN; needs `torch` (now installed, CPU) | 2-D DNS **5-20** + CNN training on CPU **10-40** | **FEASIBLE-AS-LABELLED-VARIANT.** Its transfer-learning claim is cheap to test at reduced resolution and is a real falsifier |
| **Zanna & Bolton 2020**, equation discovery of ocean mesoscale closures | **BLOCKED-ON-SOURCE** (retrieval running) | not stated | their QG ocean model output; not on disk | relevance-vector sparse regression | **< 1** given data | **BLOCKED on source and data** |

### 1.4 Differentiable-solver / solver-in-the-loop

| Paper | Source status | Headline case + number + where | Data needed / have? | Model size | Core-hours | Verdict |
|---|---|---|---|---|---|---|
| **Um, Brand, Fei, Holl & Thuerey 2020**, Solver-in-the-Loop (NeurIPS 2020, arXiv:2007.00016v2) | **VERIFIED-PDF** | Abstract, preprint p. 1: putting the solver inside the training loop "significantly outperform[s]" learning approaches that do not, giving "stable rollouts of several hundred recurrent evaluation steps and surpassing even tailored supervised variants", across problems "from non-linear advection-diffusion systems to three-dimensional Navier-Stokes flows". Code at `github.com/tum-pbs/Solver-in-the-Loop` | Their 1-D Burgers and 2-D advection-diffusion cases are self-generating. Needs `torch` (or their `phiflow`) | small CNN | 1-D/2-D VARIANT: **2-10**. 3-D: **>> 487** on CPU | **FEASIBLE-AS-LABELLED-VARIANT** (1-D Burgers / 2-D only) |
| **Kochkov, Smith, Alieva, Wang, Brenner & Hoyer 2021**, ML-accelerated CFD (PNAS 118:e2101784118, arXiv:2102.01010v1) | **VERIFIED-PDF** | Abstract, preprint p. 1: for 2-D turbulence, DNS and LES results "as accurate as baseline solvers with **8-10x finer resolution in each spatial dimension**, resulting in **40-80x fold computational speedups**", stable over long rollouts and generalising to unseen forcings and `Re` | 2-D Kolmogorov flow; self-generating. Their code is JAX/TPU | CNN inside a JAX solver | reproducing the *speedup* claim on CPU is meaningless (the claim is about accelerator throughput); reproducing the *accuracy* claim at 64^2 vs 512^2: **20-60** | **FEASIBLE-AS-LABELLED-VARIANT** for the accuracy claim only. The speed-up claim is **not reproducible here** and any attempt would be NOT A RESULT |
| **List, Chen & Thuerey 2022**, learned turbulence with differentiable solvers (JFM 949:A25, arXiv:2202.06988v2) | **VERIFIED-PDF** | Abstract, preprint p. 1: CNN turbulence models trained through a differentiable solver on three 2-D scenarios - decaying HIT, temporally evolving mixing layer, spatially evolving mixing layer; models "achieve significant improvements of long-term a-posteriori statistics ... without requiring these statistics to be directly included in the learning targets", and unrolling more solver steps improves stability and accuracy | 2-D, self-generating; needs `torch` + a differentiable 2-D solver | 2-D CNN | **20-80** on CPU for the shortest-horizon variant | **FEASIBLE-AS-LABELLED-VARIANT**, low priority - the interesting claim (unroll length) needs the full sweep, which is the expensive part |
| **Michelen Strofer & Xiao 2021**, end-to-end differentiable learning from indirect observations (JFM 915:A110, arXiv:2104.04821v1) | **VERIFIED-PDF** | Abstract, preprint p. 1: continuous adjoint of the RANS equations plus a NN eddy-viscosity model, trained on **indirect** (velocity/pressure) observations; recovers the true closure when one exists, from synthetic data generated by linear and nonlinear closures, and trains a linear model against DNS velocities where no true linear closure exists | Their synthetic-truth experiment is fully self-contained and needs only a RANS solver plus its adjoint. The "no true closure exists" experiment needs DNS velocities - **which we have**, on 41 cases | small NN eddy viscosity | continuous adjoint per iteration; **10-50** for one case | **FEASIBLE-AS-LABELLED-VARIANT**. Their synthetic-truth test is the single cleanest *falsifiable* experiment in this entire list: if the method cannot recover a closure that is known to exist, nothing else it reports means anything |

### 1.5 Wall models

| Paper | Source status | Headline case + number + where | Data needed / have? | Model size | Core-hours | Verdict |
|---|---|---|---|---|---|---|
| **Lozano-Duran & Bae 2023**, building-block-flow wall model (JFM 963:A35, arXiv:2211.07879v3) | **VERIFIED-PDF** | Abstract, preprint p. 1: a classifier + predictor pair trained on WMLES data "optimised to reproduce the correct mean quantities"; validated on canonical flows plus the NASA Common Research Model High-lift and the NASA Juncture Flow, and "outperforms (or matches) the predictions by an equilibrium wall model". Also carries a **confidence score** flagging where it underperforms, and concludes that "further improvements in WMLES should incorporate advances in subgrid-scale modelling" | Requires running WMLES. **No LES capability configured here** and no wall-model training data on disk | two small networks | WMLES of a channel at `Re_tau` 2000 on 16 CPU cores: **50-200** per case | **BLOCKED on compute and data** for anything resembling the paper |
| **Bae & Koumoutsakos 2022**, SciMARL wall models (Nat. Commun. 13:1443, arXiv:2106.11144v2) | **VERIFIED-PDF** | Abstract, preprint p. 1: multi-agent RL discovers wall models for LES | RL needs thousands of LES episodes | policy network per agent | **>> 487** | **BLOCKED on compute** |
| **Yang, Zafar, Wang & Xiao 2019**, PINN wall model | **BLOCKED-ON-SOURCE** (retrieval running) | not stated | channel DNS | small MLP | **< 1** for the a-priori part | **BLOCKED on source**; the a-priori part would be cheap |
| **Bose & Park 2018**, WMLES review | **BLOCKED-ON-SOURCE** (Annual Reviews paywall) | not stated | -- | -- | -- | **BLOCKED**; framing is taken instead from Larsson et al. 2016 and Piomelli & Balaras 2002, both VERIFIED-PDF (see `docs/closure/FOUNDATIONAL_MODELS_INVENTORY.md` sec. 13.5) |
| **Larsson, Kawai, Bodart & Bermejo-Moreno 2016**, WMLES review | **VERIFIED-PDF** | Not an ML paper, but it sets the acceptance criterion for every wall-model reproduction: the log-layer mismatch is a **numerical** error of the first off-wall cells, its *sign* is set by the host code, and it vanishes when `h_wm` is held fixed at ~0.2 delta and the grid is refined to `Delta y <~ 0.33 h_wm`, `Delta x ~ Delta z <~ 0.8 h_wm` (p. 211). Error size cured, as they report it: "from a typical 10-20% to only 5%" (p. 211) | -- | -- | -- | **Constraint, not a reproduction.** Any wall-model comparison here that does not hold `h_wm` fixed and show grid convergence at `h_wm` measures the code, not the model |

## 2. Compute summary

| Band | Papers |
|---|---|
| **< 1 core-hour** | Ling 2016 TBNN (VARIANT), Wu 2018 RF, Wang 2017 RF, Emory/Iaccarino **frozen-field envelope check** |
| **1-20 core-hours** | Kaandorp 2020 TBRF (2-6), Emory/Iaccarino 3-case perturbed solves (~5), Um 2020 1-D/2-D VARIANT (2-10) |
| **20-120 core-hours** | de Zordo-Banliat 2023 multi-model solve sweep (~50), Emory/Iaccarino full 41-case sweep (~60), Beck 2019 at 64^3 (20-40), Kochkov 2021 accuracy-only VARIANT (20-60), Strofer 2021 single case (10-50), Xiao 2016 reduced-ensemble EnKF (~120) |
| **Approaching or over the 487-core-hour authorisation - STOP and cost first** | Xiao 2016 full EnKF (~450 for **one** case), Weatheritt 2016 GEP full sweep, Beck 2019 at published resolution, List 2022 full unroll sweep |
| **Not reproducible on this machine at any scale that would mean anything** | Sirignano 2020 DPM, Bae 2022 SciMARL, Lozano-Duran 2023 BBF-WM, Kochkov 2021 *speed-up* claim |

**GPU-blocked rows stay BLOCKED pending the AWS quota appeal filed 2026-08-21**
(Sirignano 2020, Bae 2022, Lozano-Duran 2023, Beck 2019 at published resolution,
List 2022 full unroll sweep, and the Kochkov 2021 speed-up claim). No scaled-down
substitute is to be reported in their rows; a CPU variant is a different
experiment and is labelled as one.

Solve-cost basis: a `simpleFoam` run on a 15,600-cell structured hill to a
converged steady state is ~5-20 minutes on one core; ~0.3 core-hours is used
throughout as the per-case figure, and it should be re-measured before any sweep
is launched. Every core-hour number above that has not been superseded by the
table below is an estimate and is labelled as one.

### 2.1 Measured, not estimated (added after the Phase-3 runs)

| Task | Estimate above | **Measured** |
|---|---|---|
| Pope-basis feature + label assembly, all 40 cases, 641,652 cells | 0.2 | **15 s** (`_common/build_dataset.py`) |
| 17-marker extended feature set, all 40 cases | -- | **~60 s** (`_common/build_features_ext.py`) |
| Wu 2018 random forest, 2 experiments x 5 seeds, 100 trees | < 0.5 | **245 s wall on 4 threads = 0.27 core-hours** |
| Ling 2016 TBNN + control MLP, 5 seeds each, <= 400 epochs | < 0.5 | **~1.5 s/epoch on 4 threads**; full 10-run sweep ~1 h wall |
| Kaandorp 2020 TBRF, one forest of 100 trees, 21,000 samples, depth 12 | 2-6 total | **272 s per forest**; 6 forests ~30 min wall |

**The estimates were right only after a numerics fix.** With PyTorch's default
thread count the TBNN sweep was on track for **66 hours**, not one - 16 threads
measured **49.4 s/epoch** against **0.78 s** at 4 threads on the same problem.
Any core-hour estimate for a small-model workload on this machine is meaningless
until the thread count is pinned; see `docs/NUMERICS_KNOWLEDGE.md`, closure section, N-B4.

## 2.1b BEFORE COSTING ANY ROW: check `verification/campaign/` first

**One row of this matrix was already fully reproduced before the matrix was
written**, and the estimate above ("5-15 core-hours") was quoted for work that had
cost 2.7 core-hours three weeks earlier. The prior art lives in
`verification/campaign/W2_SPARTA_*` and `verification/runs/W2_sparta_runs/`, which
nothing in `cases/RANS_LES_closure_models/` referenced. `W5_SPARTA_GATE_STATUS.md`
(2026-08-04) records that two approved docket items had already made the same
mistake, and names the cause: *nothing links a gate to the record that satisfies
it*.

**So: before spending a single core-hour on any row below, grep
`verification/campaign/` and `sdk/` for the paper's name, its method's name and
its case names.** Two minutes. Every estimate in this file is an estimate of work
that may not need doing.

## 2.2 Three measured findings that change how every row above should be read

Added after the first Phase-3 runs. All three are measurements on this benchmark,
not opinions, and all three make the "FEASIBLE" verdicts above weaker than they
look.

**F1. A single constant tensor beats k-omega SST on the anisotropy metric, on all
eight strict TEST cases.** The mean `b_LES` over the 342,014 training cells,
used as a constant prediction with no inputs at all, scores `b_rms` of
0.2258-0.4221 against SST's 0.2889-0.5972 - better on every case
(`Ling2016_TBNN/RESULTS.md` sec. 5). **"Beats the RANS baseline on `b_ij`" is
therefore a bar that a constant clears.** Every row above that promises an
a-priori anisotropy improvement should be read against that constant, not against
SST, and any reproduction here that reports only the SST comparison has not been
evaluated.

**F2. Pope's ten-tensor basis has per-cell rank 3.006-3.987 by case mean on this benchmark, never
above 5**, because every case is a statistically 2-D mean flow and the basis
collapses to three tensors in two dimensions [VERIFIED-PDF: Pope 1975, JFM 72(2),
p. 335]. Consequences: the published ridge parameter of the TBRF
(`Gamma = 1e-12`) is far too small and produces coefficients of order `1/Gamma`
along the null space; and **no result obtained on this data can test the claim
that ten tensors are what tensor-basis methods need.** Rows for Ling 2016,
Kaandorp 2020, Schmelzer 2020 and Weatheritt 2016 are all affected.

**F3. Tensor-basis models are unbounded, and they leave the realisable set.**
A trained TBNN put 6.5-15.3% of test cells outside the barycentric triangle
(against 0.79% for the truth and 0.10% for SST) and reached `||b||_F ~ 1e7` on
the NASA hump. A TBRF on the same split reached order `1e2` there. The
architecture guarantees Galilean invariance and nothing else. Any row above whose
verdict is FEASIBLE should be understood as "feasible to train", not "feasible to
put in a solver": an a-posteriori propagation of a field that is non-realisable
on a tenth of the domain will not converge.

## 3. What this matrix cannot see

* **It cannot compare our numbers to theirs where the cases differ.** Only
  Schmelzer 2020 (PH10595, CBFS13700) and Kaandorp 2020 (PH10595, CBFS13700,
  square ducts) share cases with the data on this machine. For Ling 2016 the
  flows are entirely different, so a reproduction is a reproduction of the
  *method*, and the RMSE 0.13 in their Table I is not a target we can hit or miss.
* **Twelve of the twenty-nine papers have no verified PDF here**, so their
  headline numbers are deliberately absent rather than recalled. Any of them may
  turn out, on reading, to be infeasible for reasons this table cannot anticipate.
* **Every core-hour figure is an estimate**, made without running anything.
* **The a-posteriori / a-priori distinction dominates all of it.** An a-priori
  `b_ij` regression that halves `b_rms` can still make `U` worse when re-solved.
  Because OpenFOAM is available, there is no excuse for stopping at a-priori, and
  every reproduction below `_common/` must state explicitly whether it re-solved.
* **No GPU.** Everything CNN-shaped or RL-shaped is out of reach at published
  scale, and saying so is more useful than shipping a 1/8-scale version and
  calling it a reproduction.


---

**Provenance repair, 2026-08-21.** An earlier figure of "3.24 on average, never above 5" for the per-cell rank of Pope's ten-tensor basis was quoted here from `Kaandorp2020_TBRF/train_log.json`, **which does not exist** (charter section 5(b)). It has been replaced by a live re-measurement: per-cell rank of **3.006-3.987 by case mean** (mean of case means **3.738**), **never above 5 in any cell**, source `_common/features/FS2_DEGENERACY_REPORT.md` sec. 4 and `/home/ubuntu/closure-data/features/fs2_audit.json` -> `tensor_basis_rank`. 3.24 was a pooled-sample statistic over randomly drawn training cells, which the low-rank duct family pulls down; the case-mean statistic is 3.738. They are different statistics and are not interchangeable. **The bound that carries the argument is unchanged: never above 5, against a nominal basis size of 10.**


---

**Dated note appended 2026-08-21 — the NASA hump BLOCK is liftable by equivalence gate, and the gate PASSED.**
*Appended note; nothing above this line was edited.*

The hump's shipped baseline was blocked because `constant/turbulenceProperties`
selects **`AugmentedkOmegaSST`**, whose library is absent on this machine. That
model is not a mystery: `data/NASA_2DWMH/log.run` line 153 selects it and prints
its full coefficient dictionary — `baseline true`, `usekDeficit false`,
`usebijDelta false`, `useSigma false`, `modelbijDelta false`,
`modelkDeficit false`, `modelSigma false`, with every printed coefficient the
stock Menter SST value (`alphaK1 0.85`, `alphaOmega2 0.856`, `gamma1 0.555556`,
`beta1 0.075`, `betaStar 0.09`, `a1 0.31`, `b1 1`, `c1 10`, `F3 false`). It is a
SpaRTA-style corrected SST **run with every augmentation switched off**.

A preregistered equivalence gate
(`cases/RANS_LES_closure_models/NASA_hump_gate/`) tested that behaviourally:

* **B-G0a** (two-sided, 200 identical iterations) is **BLOCKED** — the shipped
  model cannot be instantiated here at all (`Unknown RAS model type
  AugmentedkOmegaSST`), which the preregistration registered as BLOCKED rather
  than failed.
* **B-G0b** (converged NULL against the published row) **PASSES**:
  `kOmegaSSTCorrected` with `bijDelta = 0`, `kDeficit = 0`, `omegaMin 0.1` and the
  shipped `fvOptions`, restarted from the shipped `2000/` field, **converged in
  156 iterations** to `U_rms` = **0.1261769** against the published **0.1260**
  (Δ **1.77e-4**, band 5e-3) and `U_mae` = **0.0621203** against **0.0620**
  (Δ 1.2e-4). `kOmegaSSTCorrected(0,0)` is separately measured **bit-identical**
  (rel-L2 = 0.0) to stock `kOmegaSST`.

**Consequence: the hump is scorable comparably through the `kOmegaSSTCorrected`
path**, so a lane that previously recorded it as BLOCKED-on-a-missing-library may
now run it — as **UNBLOCKABLE-BY-EQUIVALENCE-GATE**, citing this note. The
limitation stands and is not erased: equivalence is **behavioural, one-sided, on
one case, from one restart**, because the shipped model could not be loaded to
compare against. Details and the full 'cannot see' list:
`cases/RANS_LES_closure_models/NASA_hump_gate/RESULTS.md`.
