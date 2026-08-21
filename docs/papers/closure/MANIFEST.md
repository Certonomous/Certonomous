# Paper Retrieval Manifest — TITLE-PAGE VERIFIED

**Regenerated 2026-08-20 from the folder as it stands, by script, after the retrieval
agents exited. The corpus is FINAL: nothing else writes to `docs/papers/closure/`.**
Supersedes the 2026-08-20 20:25 rebuild and `MANIFEST_OLD_UNVERIFIED.md`, which was written
without ever opening a title page and was ~64% wrong.

## VERIFICATION RULE

> **A retrieval is RETRIEVED-VERIFIED only if the PRINTED TITLE PAGE of the file on disk
> matches the intended paper.** File type (`%PDF` magic), file size, non-zero page count
> and sha256 prove *integrity* — that the bytes are a readable PDF and have not changed —
> and prove **nothing whatsoever about identity**. Every WRONG-QUARANTINED row below was a
> valid, well-formed, hash-stable PDF of a completely unrelated paper. An arXiv ID that
> was *guessed* from a title, rather than resolved from a listing, resolves to an unrelated
> paper roughly two times in three.

**Second rule, added 2026-08-20 (lesson L-145):** identity is not multiplicity. Title-page
verification cannot detect that two correctly-identified files are **the same document**.
**Duplicates are found by grouping the verified files by sha256**, and the manifest emits
**one row per hash**, never one row per filename. Six such files were found and are listed
in §2; a manifest with two rows for one document is eventually read as two independent
sources agreeing on a number.

Method: `pdftotext -f 1 -l 1 -layout` on page 1 of every file under `docs/papers/closure/`
(top level, `_DUPLICATES/`, `_WRONG_RETRIEVALS/`); printed title read off the extracted
page-1 text; sha256 over the whole file; page count from `pdfinfo`; arXiv ID taken only from
the stamp printed in the left margin by arXiv itself. Scanned files with no text layer are
verified by rendering page 1 to PNG and reading it. **Hashes and page counts in this file are
script-generated and were not hand-edited.**

## STATUS COUNTS

| status | n |
|---|---|
| **RETRIEVED-VERIFIED (canonical, distinct works)** | **33** |
| DUPLICATE (byte-identical second copy, quarantined) | 6 |
| WRONG-QUARANTINED (unrelated paper, kept as evidence) | 30 |
| **PENDING-MIT (not retrievable from open sources)** | **16** |

PDFs on disk: **33 canonical + 6 duplicates + 30 wrong = 69**. `_WRONG_DOWNLOADS/` is empty.

---

# 1. CANONICAL CORPUS — 33 distinct title-verified works

Shelf codes: **A** foundational analytical · **B** data-driven RANS · **C** field inversion + ML ·
**D** model-form UQ · **E** LES subgrid-scale · **F** wall-modelled LES ·
**G** differentiable / solver-in-the-loop · **H** aggregation · **R** reviews · **X** feature selection.

**Version column**: where the file is an arXiv preprint, cite it as *arXiv preprint p./eq./Table* —
preprint pagination and equation numbers do not generally match the journal version.

| # | shelf | file on disk | intended citation | version on disk | pp | VERIFIED PRINTED TITLE (verbatim, from page 1) |
|---|---|---|---|---|---|---|
| 1 | A | `Pope1975_effective_viscosity_hypothesis.pdf` | Pope, S.B. (1975), A more general effective-viscosity hypothesis, *J. Fluid Mech.* 72(2):331-340 | publisher PDF | 10 | J . Pluid Mech. (1975), vol. 72, part 2, pp. 331-340 331 Printed i n Great B r i t a i n A more  |
| 2 | A | `Spalart2000_strategies_turbulence_modelling.pdf` | Spalart, P.R. (2000), Strategies for turbulence modelling and simulations, *Int. J. Heat Fluid Flow* 21:252-263 | publisher PDF | 12 | International Journal of Heat and Fluid Flow 21 (2000) 252±263 www.elsevier.com/locate/ijh Stra |
| 3 | A | `Menter1994_sst_two_equation.pdf` | Menter, F.R. (1994), Two-equation eddy-viscosity turbulence models for engineering applications, *AIAA J.* 32(8):1598-1605 | publisher PDF | 8 | AIAA JOURNAL Vol. 32, No. 8, August 1994 Two-Equation Eddy-Viscosity Turbulence Models for Engin |
| 4 | A | `Gatski1996_handbook_chapter6.pdf` | [SUBSTITUTE ON SHELF] Gatski, T.B. (1996), Turbulent flows: model equations and solution methodology, ch. 6 in *Handbook of Computational Fluid Mechanics*, Academic Press, pp. 339-414 | uploaded scan | 77 | *[no text layer — identity read from rendered page 1]* |
| 5 | E | `Smagorinsky1963_general_circulation.pdf` | Smagorinsky, J. (1963), General circulation experiments with the primitive equations: I. The basic experiment, *Mon. Weather Rev.* 91(3):99-164 | publisher PDF (NOAA open access) | 66 | DEPARTMENT OF COMMERCE WEATHER BUREAU LUTHER H. HODGES, Secretary F, W. REICHELDERFER, Chief MON |
| 6 | E | `Nicoud1999_WALE_sgs.pdf` | Nicoud, F. & Ducros, F. (1999), Subgrid-scale stress modelling based on the square of the velocity gradient tensor, *Flow Turb. Combust.* 62:183-200 | publisher PDF | 18 | Flow, Turbulence and Combustion 62: 183–200, 1999. 183 © 1999 Kluwer Academic Publishers. Printe |
| 7 | F | `Piomelli2002_wall_layer_models_les.pdf` | Piomelli, U. & Balaras, E. (2002), Wall-layer models for large-eddy simulations, *Annu. Rev. Fluid Mech.* 34:349-374 | publisher PDF | 29 | 5 Nov 2001 12:13 AR AR151-14.tex AR151-14.SGM ARv2(2001/05/10) P1: GJC Annu. Rev. Fluid Mech. 20 |
| 8 | F | `Larsson2016_wall_stress.pdf` | Larsson, J., Kawai, S., Bodart, J. & Bermejo-Moreno, I. (2016), Large eddy simulation with modeled wall-stress: recent progress and future directions, *Mech. Eng. Rev.* 3(1):15-00418 | J-STAGE open access | 23 | Bulletin of the JSME Vol.3, No.1, 2016 Mechanical Engineering Reviews Large eddy simulation with |
| 9 | X | `Guyon2003_feature_selection.pdf` | Guyon, I. & Elisseeff, A. (2003), An introduction to variable and feature selection, *J. Mach. Learn. Res.* 3:1157-1182 | JMLR open access | 26 | Journal of Machine Learning Research 3 (2003) 1157-1182 Submitted 11/02; Published 3/03 An Intro |
| 10 | B | `Ling2016_tbnn_embedded_invariance.pdf` | Ling, J., Kurzawski, A. & Templeton, J. (2016), Reynolds averaged turbulence modelling using deep neural networks with embedded invariance, *J. Fluid Mech.* 807:155-166 | Sandia SAND2016-7345J | 17 | SAND2016-7345J Reynolds Averaged Turbulence Modeling using Deep Neural Networks with Embedded In |
| 11 | B | `Wang_Wu_Xiao2017_pinn_reynolds_stress.pdf` | Wang, J.-X., Wu, J.-L. & Xiao, H. (2017), A physics-informed machine learning approach for reconstructing Reynolds stress modeling discrepancies, *Phys. Rev. Fluids* 2:034603 | arXiv:1606.07987v2 | 36 | A Physics Informed Machine Learning Approach for Reconstructing Reynolds Stress Modeling Discrep |
| 12 | B | `Wu2018_physics_augmenting.pdf` | Wu, J.-L., Xiao, H. & Paterson, E. (2018), Physics-informed machine learning approach for augmenting turbulence models: a comprehensive framework, *Phys. Rev. Fluids* 3:074602 | arXiv:1801.02762v4 | 42 | Physics-Informed Machine Learning Approach for Augmenting Turbulence Models: A Comprehensive Fra |
| 13 | B | `Schmelzer2020_algebraic_reynolds.pdf` | Schmelzer, M., Dwight, R.P. & Cinnella, P. (2020), Discovery of algebraic Reynolds-stress models using sparse symbolic regression, *Flow Turb. Combust.* 104:579-603 | arXiv:1905.07510v2 | 29 | Discovery of Algebraic Reynolds-Stress Models Using Sparse Symbolic Regression. Martin Schmelzer |
| 14 | B | `Kaandorp2020_random_forests.pdf` | Kaandorp, M.L.A. & Dwight, R.P. (2020), Data-driven modelling of the Reynolds stress tensor using random forests with invariance, *Computers & Fluids* 202:104497 | arXiv:1810.08794v2 | 58 | Data-Driven Modelling of the Reynolds Stress Tensor using Random Forests with Invariance Mikael  |
| 15 | C | `Singh2017_ml_airfoils.pdf` | Singh, A.P., Medida, S. & Duraisamy, K. (2017), Machine-learning-augmented predictive modeling of turbulent separated flows over airfoils, *AIAA J.* 55(7):2215-2227 | arXiv:1608.03990v3 | 32 | Machine Learning-augmented Predictive Modeling of Turbulent Separated Flows over Airfoils Anand  |
| 16 | D | `Xiao2016_model_uncertainties.pdf` | Xiao, H., Wu, J.-L., Wang, J.-X., Sun, R. & Roy, C.J. (2016), Quantifying and reducing model-form uncertainties in RANS simulations: a data-driven, physics-informed Bayesian approach, *J. Comput. Phys.* 324:115-136 | arXiv:1508.06315v3 | 54 | Quantifying and Reducing Model-Form Uncertainties in Reynolds-Averaged Navier–Stokes Simulations |
| 17 | D | `Wu2018_rans_explicit_closure_ill_conditioned.pdf` | Wu, J.-L., Xiao, H., Sun, R. & Wang, Q. (2019), RANS equations with explicit data-driven Reynolds stress closure can be ill-conditioned, *J. Fluid Mech.* 869:553-586 | arXiv:1803.05581v3 | 34 | This draft was prepared using the LaTeX style file belonging to the Journal of Fluid Mechanics 1 |
| 18 | E | `Maulik_San2017_neural_deconvolution.pdf` | Maulik, R. & San, O. (2017), A neural network approach for the blind deconvolution of turbulent flows, *J. Fluid Mech.* 831:151-181 | arXiv:1706.00912v2 | 31 | Under consideration for publication in J. Fluid Mech. 1 A neural network approach for the blind  |
| 19 | E | `Maulik2019_subgrid_2d_nn.pdf` | Maulik, R., San, O., Rasheed, A. & Vedula, P. (2019), Subgrid modelling for two-dimensional turbulence using neural networks, *J. Fluid Mech.* 858:122-144 | arXiv:1808.02983v1 | 22 | This draft was prepared using the LaTeX style file belonging to the Journal of Fluid Mechanics 1 |
| 20 | E | `Beck2019_deep_neural_les.pdf` | Beck, A., Flad, D. & Munz, C.-D. (2019), Deep neural networks for data-driven LES closure models, *J. Comput. Phys.* 398:108910 | arXiv:1806.04482v3 | 27 | This draft was prepared using the LaTeX style file belonging to the Journal of Fluid Mechanics 1 |
| 21 | E | `Sirignano2020_dpm_les.pdf` | Sirignano, J., MacArt, J.F. & Freund, J.B. (2020), DPM: a deep learning PDE augmentation method with application to large-eddy simulation, *J. Comput. Phys.* 423:109811 | arXiv:1911.09145v1 | 28 | DPM: A deep learning PDE augmentation method (with application to large-eddy simulation) Jonatha |
| 22 | E | `Guan2022_stable_aposteriori_les_cnn.pdf` | Guan, Y., Chattopadhyay, A., Subel, A. & Hassanzadeh, P. (2022), Stable a posteriori LES of 2D turbulence using convolutional neural networks, *J. Comput. Phys.* 458:111090 | arXiv:2102.11400v1 | 30 | Stable a posteriori LES of 2D turbulence using convolutional neural networks: Backscattering ana |
| 23 | F | `Bae2022_marl_wall_model.pdf` | Bae, H.J. & Koumoutsakos, P. (2022), Scientific multi-agent reinforcement learning for wall-models of turbulent flows, *Nature Commun.* 13:1443 | arXiv:2106.11144v2 | 22 | Springer Nature 2021 LATEX template Scientific multi-agent reinforcement learning for wall-model |
| 24 | F | `LozanoDuran2023_wall_model.pdf` | Lozano-Duran, A. & Bae, H.J. (2023), Machine learning building-block-flow wall model for large-eddy simulation, *J. Fluid Mech.* 963:A35 | arXiv:2211.07879v3 | 35 | This draft was prepared using the LaTeX style file belonging to the Journal of Fluid Mechanics 1 |
| 25 | G | `Strofer2021_differentiable.pdf` | Michelen Strofer, C.A. & Xiao, H. (2021), End-to-end differentiable learning of turbulence models from indirect observations, *Theor. Appl. Mech. Lett.* 11:100280 | arXiv:2104.04821v1 | 10 | This draft was prepared using the LaTeX style file belonging to the Journal of Fluid Mechanics 1 |
| 26 | G | `Um2020_solver_loop.pdf` | Um, K., Brand, R., Fei, Y., Holl, P. & Thuerey, N. (2020), Solver-in-the-loop: learning from differentiable physics to interact with iterative PDE-solvers, *NeurIPS 2020* | arXiv:2007.00016v2 | 37 | Solver-in-the-Loop: Learning from Differentiable Physics to Interact with Iterative PDE-Solvers  |
| 27 | G | `Kochkov2021_ml_accelerated_cfd.pdf` | Kochkov, D., Smith, J.A., Alieva, A., Wang, Q., Brenner, M.P. & Hoyer, S. (2021), Machine learning-accelerated computational fluid dynamics, *PNAS* 118(21):e2101784118 | arXiv:2102.01010v1 | 13 | Machine learning accelerated computational fluid dynamics Dmitrii Kochkov,1, ∗ Jamie A. Smith,1, |
| 28 | G | `List2022_learned_turbulence.pdf` | List, B., Chen, L.-W. & Thuerey, N. (2022), Learned turbulence modelling with differentiable fluid solvers: physics-based loss functions and optimisation horizons, *J. Fluid Mech.* 949:A25 | arXiv:2202.06988v2 | 40 | Learned Turbulence Modelling with Differentiable Fluid Solvers: Physics-based Loss-functions and |
| 29 | H | `deZordoBanliat2023_space_dependent_aggregation.pdf` | de Zordo-Banliat, M., Dergham, G., Merle, X. & Cinnella, P. (2023), Space-dependent turbulence model aggregation using machine learning, *J. Comput. Phys.* 485:112114 | arXiv:2301.09013v1 | 27 | Space-dependent turbulence model aggregation using machine learning M. de Zordo-Banliat(1,2) , G |
| 30 | R | `Duraisamy2019_turbulence_age_data.pdf` | Duraisamy, K., Iaccarino, G. & Xiao, H. (2019), Turbulence modeling in the age of data, *Annu. Rev. Fluid Mech.* 51:357-377 | arXiv:1804.00183v3 | 23 | Turbulence Modeling in the Age of Data Karthik Duraisamy1,? , Gianluca Iaccarino2,? , and Heng X |
| 31 | R | `Duraisamy2021_perspectives_ml.pdf` | Duraisamy, K. (2021), Perspectives on machine learning-augmented RANS and LES models of turbulence, *Phys. Rev. Fluids* 6:050504 | arXiv:2009.10675v3 | 25 | Perspectives on Machine Learning-augmented Reynolds-averaged and Large Eddy Simulation Models of |
| 32 | R | `Beck2021_perspective_ml.pdf` | Beck, A. & Kurz, M. (2021), A perspective on machine learning methods in turbulence modeling, *GAMM-Mitteilungen* 44:e202100002 | arXiv:2010.12226v1 | 37 | A Perspective on Machine Learning Methods in Turbulence Modelling Andrea Beck, Marius Kurz Lab.  |
| 33 | R | `Sanderse2024_ML_closure_models.pdf` | Sanderse, B., Stinis, P., Maulik, R. & Ahmed, S.E. (2024), Scientific machine learning for closure models in multiscale problems: a review, *arXiv:2403.02913* | arXiv:2403.02913v2 | 32 | SCIENTIFIC MACHINE LEARNING FOR CLOSURE MODELS IN MULTISCALE PROBLEMS: A REVIEW B. SANDERSE, P.  |

## 1.1 Version authority and per-file notes

| file | authority / note |
|---|---|
| `Pope1975_effective_viscosity_hypothesis.pdf` | **journal of record** (doi:10.1017/S0022112075003382) |
| `Spalart2000_strategies_turbulence_modelling.pdf` | **journal of record** (doi:10.1016/S0142-727X(00)00007-2) |
| `Menter1994_sst_two_equation.pdf` | **journal of record** (doi:10.2514/3.12149) |
| `Gatski1996_handbook_chapter6.pdf` | **book of record**, ISBN 0-12-553010-2. **SCANNED, NO TEXT LAYER** |
| `Smagorinsky1963_general_circulation.pdf` | **journal of record** (doi:10.1175/1520-0493(1963)091<0099:GCEWTP>2.3.CO;2) |
| `Nicoud1999_WALE_sgs.pdf` | **journal of record** (doi:10.1023/A:1009995426001) |
| `Piomelli2002_wall_layer_models_les.pdf` | **journal of record** (doi:10.1146/annurev.fluid.34.082901.144919) |
| `Larsson2016_wall_stress.pdf` | **journal of record** (doi:10.1299/mer.15-00418). Printed folios extract with a spurious '2' prefix; cite PDF page numbers |
| `Guyon2003_feature_selection.pdf` | **journal of record** |
| `Ling2016_tbnn_embedded_invariance.pdf` | **preprint** (journal doi:10.1017/jfm.2016.615). Architecture differs from Kaandorp 2020's description of it - see NOTES |
| `Wang_Wu_Xiao2017_pinn_reynolds_stress.pdf` | **preprint** (journal doi:10.1103/PhysRevFluids.2.034603) |
| `Wu2018_physics_augmenting.pdf` | **preprint** (journal doi:10.1103/PhysRevFluids.3.074602) |
| `Schmelzer2020_algebraic_reynolds.pdf` | **preprint** (journal doi:10.1007/s10494-019-00089-x) |
| `Kaandorp2020_random_forests.pdf` | **preprint** (journal doi:10.1016/j.compfluid.2020.104497) |
| `Singh2017_ml_airfoils.pdf` | **preprint** (journal doi:10.2514/1.J055595) |
| `Xiao2016_model_uncertainties.pdf` | **preprint** (journal doi:10.1016/j.jcp.2016.07.038) |
| `Wu2018_rans_explicit_closure_ill_conditioned.pdf` | **preprint** (journal doi:10.1017/jfm.2019.205). Retrieved 2026-08-20; closes VERIFICATION_FLAGS F16 |
| `Maulik_San2017_neural_deconvolution.pdf` | **preprint** (journal doi:10.1017/jfm.2017.637) |
| `Maulik2019_subgrid_2d_nn.pdf` | **preprint** (journal doi:10.1017/jfm.2018.770) |
| `Beck2019_deep_neural_les.pdf` | **preprint** (journal doi:10.1016/j.jcp.2019.108910). **Preprint title differs from the journal title** |
| `Sirignano2020_dpm_les.pdf` | **preprint** (journal doi:10.1016/j.jcp.2020.109811). **Preprint author order is Freund, MacArt, Sirignano** |
| `Guan2022_stable_aposteriori_les_cnn.pdf` | **preprint** (journal doi:10.1016/j.jcp.2022.111090). Retrieved 2026-08-20 |
| `Bae2022_marl_wall_model.pdf` | **preprint** (journal doi:10.1038/s41467-022-28957-7) |
| `LozanoDuran2023_wall_model.pdf` | **preprint** (journal doi:10.1017/jfm.2023.331) |
| `Strofer2021_differentiable.pdf` | **preprint v1** (journal doi:10.1016/j.taml.2021.100280). **v1 contains no ensemble-Kalman content** - see NOTES |
| `Um2020_solver_loop.pdf` | **preprint** (NeurIPS 2020 proceedings) |
| `Kochkov2021_ml_accelerated_cfd.pdf` | **preprint** (journal doi:10.1073/pnas.2101784118) |
| `List2022_learned_turbulence.pdf` | **preprint** (journal doi:10.1017/jfm.2022.738) |
| `deZordoBanliat2023_space_dependent_aggregation.pdf` | **preprint** (journal doi:10.1016/j.jcp.2023.112114) |
| `Duraisamy2019_turbulence_age_data.pdf` | **preprint** (journal doi:10.1146/annurev-fluid-010518-040547) |
| `Duraisamy2021_perspectives_ml.pdf` | **preprint** (journal doi:10.1103/PhysRevFluids.6.050504) |
| `Beck2021_perspective_ml.pdf` | **preprint** (journal doi:10.1002/gamm.202100002) |
| `Sanderse2024_ML_closure_models.pdf` | **preprint; no journal version recorded** |

## 1.2 Full sha256 of the 33 canonical files

| file | pp | sha256 |
|---|---|---|
| `Pope1975_effective_viscosity_hypothesis.pdf` | 10 | `bd4ba7a38db142307aad0b0abb29ddb9d1e94d28a332d4469711a3a169cc2222` |
| `Spalart2000_strategies_turbulence_modelling.pdf` | 12 | `bf266888c9a2864f2c8552e38502b3b1cc2aa68193fd177a9b6c693b8477e720` |
| `Menter1994_sst_two_equation.pdf` | 8 | `a939bfb3b322d7a4f1978e8b21469623dc125ffcb2de6ff2e6c723e4842be896` |
| `Gatski1996_handbook_chapter6.pdf` | 77 | `c9482c522225209997e55346d10332ff32535f7cb2b1a1302d90f2ff689ecc29` |
| `Smagorinsky1963_general_circulation.pdf` | 66 | `424b802dd5b4fba15bc0de6068cfff06f09ccac2d0b2f62b6eba12350425231e` |
| `Nicoud1999_WALE_sgs.pdf` | 18 | `f87d482d0af5bdc14b8ea7d8d65a73728054a436bf13abb350a38836bd8d561e` |
| `Piomelli2002_wall_layer_models_les.pdf` | 29 | `87cbde02e3f9e5d3aff55f35d9ccea2a4863554d1b50b4d67e8803e26edbb0c4` |
| `Larsson2016_wall_stress.pdf` | 23 | `40d0e1277859a02a0401a906d44000f34d828c9af6ebb3fd5c073cbb945d859c` |
| `Guyon2003_feature_selection.pdf` | 26 | `73dba144b5bfda65fccbb74681f21e0361274f56e4a7a7ab907586beaeb19397` |
| `Ling2016_tbnn_embedded_invariance.pdf` | 17 | `4f4fc80e2373075780e990d27496af3f8450c073c533470749b02c6bce5579c3` |
| `Wang_Wu_Xiao2017_pinn_reynolds_stress.pdf` | 36 | `1c8ee1af94eb8a623756a59070f2e1893a84f0cee66d65b025cb7d47619ab864` |
| `Wu2018_physics_augmenting.pdf` | 42 | `e67b7b029a4477cf14b571fdf3ddbfaaf692ffa17327635c10f09f173e31a353` |
| `Schmelzer2020_algebraic_reynolds.pdf` | 29 | `7aca1f9a1f40dc4c67c12f83f2c05fe85cecf6527e1107129bb831b68def1208` |
| `Kaandorp2020_random_forests.pdf` | 58 | `7a04713d8f82077de94255c6f5ded637e58121fea647ba210a06d04dbc5a9ad2` |
| `Singh2017_ml_airfoils.pdf` | 32 | `6e5776281a80ca66c70adc01a87796d3b115aa2b30b47e7c6bf084af90d44133` |
| `Xiao2016_model_uncertainties.pdf` | 54 | `1577eabd0d5924146370256cbff8f37397d48953efd1e6589605b6583a40e739` |
| `Wu2018_rans_explicit_closure_ill_conditioned.pdf` | 34 | `02245ae54c949b1518606a5c22e6fefc97836d10e250a4f6186480c8626551f4` |
| `Maulik_San2017_neural_deconvolution.pdf` | 31 | `92ee9bc6830b8ee1835671b6807e937dcf82966689c8a0d699989dd2597d1847` |
| `Maulik2019_subgrid_2d_nn.pdf` | 22 | `a8bfb15f49f7cd719c42e00b956113a800d9c0a2c834ecd66bdc7b4652908596` |
| `Beck2019_deep_neural_les.pdf` | 27 | `5e871ebae97db5cd6e9f90b8773709e57dd7136ee6ad113486c1db603e63c7d9` |
| `Sirignano2020_dpm_les.pdf` | 28 | `378bc5820fba092bdf13b9aafd06e164e5677677404b04eb4407dda75983222d` |
| `Guan2022_stable_aposteriori_les_cnn.pdf` | 30 | `61462961b6643c1388f1ed3929c11558c6cb028b9b9098a7fc759c457af196a3` |
| `Bae2022_marl_wall_model.pdf` | 22 | `8962e018a8b47e3a3b7854674b8adae0f8802e6cc8e6f24a01c3434657d1e36d` |
| `LozanoDuran2023_wall_model.pdf` | 35 | `d30b8bf9f86d09b97991f76596df410fe8175e2d9f4300d3aa2613685e3fd001` |
| `Strofer2021_differentiable.pdf` | 10 | `ccb63574017d356974a6c7da113f2a7c6ac8aa393bb4aa472b7439245d2ddace` |
| `Um2020_solver_loop.pdf` | 37 | `b356d2f93af77746ee25e5ae8d414c68231f521509232176ec5535483ec8af0d` |
| `Kochkov2021_ml_accelerated_cfd.pdf` | 13 | `84cbe66efc645d4f7638b06ab088df9184bfb0dbce9978bc2ad1619bc3588477` |
| `List2022_learned_turbulence.pdf` | 40 | `2238e1c5a9790c14794c256ef88c940d223eca65acbfda85f8f49337bd4542d5` |
| `deZordoBanliat2023_space_dependent_aggregation.pdf` | 27 | `48ee9c88e4b07e4a46f056e6cde8a6cadd1c0db10576e7a0cdd4f8d392e1eabc` |
| `Duraisamy2019_turbulence_age_data.pdf` | 23 | `c57e05389c579461ea972683c6daa9656e732b900962b0b917403a94d00db3a8` |
| `Duraisamy2021_perspectives_ml.pdf` | 25 | `ccb66cf93c004ea749f29a8181e327a54950e32b59bd3869752c00c23d3bf53c` |
| `Beck2021_perspective_ml.pdf` | 37 | `11975c01abb8ae4df90e6fa7359a5e2d4e552d8d39c8b66f4c78fd9916e94024` |
| `Sanderse2024_ML_closure_models.pdf` | 32 | `942727457b7c00bed52c8e13f436320f87f4e28a2e2ecc0f859ed7e7486418ad` |

---

# 2. DUPLICATES — `_DUPLICATES/` (6 files)

Second copies of papers already present under another filename, produced by the title-verified
re-fetch of 2026-08-20 running concurrently with another agent's re-fetch. **All six were checked
by sha256 against their canonical twin and all six are BYTE-IDENTICAL** — so the arXiv version does
*not* differ in any of the six, and each pair is one document under two names.

**None of these is a retrieval error.** Every file here is the correct paper. They are quarantined
because a manifest must emit one row per document, not one per filename (§VERIFICATION RULE, second
rule). **Cite the canonical name only.**

| duplicate file (`_DUPLICATES/`) | canonical file (cite this one) | pp | arXiv | byte-identical? | shared sha256 |
|---|---|---|---|---|---|
| `Beck2019_deep_neural_les_closure.pdf` | `Beck2019_deep_neural_les.pdf` | 27 | arXiv:1806.04482v3 | **yes** | `5e871ebae97db5cd6e9f90b8773709e5…` |
| `Duraisamy2021_perspectives_ml_rans_les.pdf` | `Duraisamy2021_perspectives_ml.pdf` | 25 | arXiv:2009.10675v3 | **yes** | `ccb66cf93c004ea749f29a8181e327a5…` |
| `Maulik2017_blind_deconvolution_neural.pdf` | `Maulik_San2017_neural_deconvolution.pdf` | 31 | arXiv:1706.00912v2 | **yes** | `92ee9bc6830b8ee1835671b6807e937d…` |
| `Schmelzer2020_sparta_sparse_symbolic_regression.pdf` | `Schmelzer2020_algebraic_reynolds.pdf` | 29 | arXiv:1905.07510v2 | **yes** | `7aca1f9a1f40dc4c67c12f83f2c05fe8…` |
| `Sirignano2020_dpm_deep_learning_pde_augmentation.pdf` | `Sirignano2020_dpm_les.pdf` | 28 | arXiv:1911.09145v1 | **yes** | `378bc5820fba092bdf13b9aafd06e164…` |
| `Xiao2016_bayesian_model_form_uncertainty.pdf` | `Xiao2016_model_uncertainties.pdf` | 54 | arXiv:1508.06315v3 | **yes** | `1577eabd0d5924146370256cbff8f373…` |

Verify at any time with:

```
sha256sum docs/papers/closure/*.pdf docs/papers/closure/_DUPLICATES/*.pdf | sort | uniq -w64 -d
```

A non-empty result is expected here and lists exactly these six pairs.

---

# 3. WRONG-RETRIEVALS AUDIT — `_WRONG_RETRIEVALS/` (30 files)

**Kept as evidence, never cited.** These are the files produced by the retrieval agent that
*guessed* arXiv identifiers from author and year. Each guessed identifier resolved to a real but
unrelated paper, so the download succeeded, the sha256 was computed over the wrong file, and the
old manifest row certified the wrong document. **The filename is what the retrieval agent believed
it had downloaded; the title column is what the file actually is.** This is the evidence behind
**LESSONS L-144**.

| filename (as claimed) | believed to be | pp | arXiv stamp | ACTUAL PRINTED TITLE |
|---|---|---|---|---|
| `Beck2019_deep_neural_les.pdf` | Beck, Flad & Munz 2019, deep NNs for LES closure | 12 | arXiv:1810.01993v1 | Exascale Deep Learning for Climate Analytics Thorsten Kurth∗ Sean Treichler† J |
| `Beck2021_perspective_ml.pdf` | Beck & Kurz 2021, perspective on ML in turbulence modelling | 29 | arXiv:1801.01225v1 | Patterns in Khovanov link and chromatic graph homology Radmila Sazdanovic and  |
| `Bose2018_wall_modeled_les.pdf` | Bose & Park 2018, WMLES review | 67 | arXiv:1701.04413v1 | Unified Models of Neutrinos, Flavour and CP Violation S.F. King,1 1 Physics an |
| `Duraisamy2021_perspectives_ml.pdf` | Duraisamy 2021, perspectives on ML-augmented RANS/LES | 7 | — | Non-destructive visualization of short circuits in lithium-ion batteries by ma |
| `Edeling2014_predictive_rans.pdf` | Edeling, Cinnella & Dwight 2014, Bayesian model-scenario averaging | 11 | arXiv:1406.3360v2 | Local thermal observables in spatially open FRW spaces Slava Emelyanov∗ Arnold |
| `Emory2013_uncertainties.pdf` | Emory, Larsson & Iaccarino 2013, structural uncertainties | 3 | arXiv:1303.1564v1 | 4th Fermi Symposium : Monterey, CA : 28 Oct-2 Nov 2012 1 The HAWC observatory  |
| `Holland2019_field_inversion_neural.pdf` | Holland, Baeder & Duraisamy 2019, FIML with embedded NNs | 14 | arXiv:1907.10711v2 | Density contrast matters for drop fragmentation thresholds at low Ohnesorge nu |
| `Iaccarino2017_eigenspace.pdf` | Iaccarino, Mishra & Ghili 2017, eigenspace perturbations | 25 | arXiv:1705.09996v2 | Dispersive shock waves in systems with nonlocal dispersion of Benjamin-Ono typ |
| `Kaandorp2020_random_forests.pdf` | Kaandorp & Dwight 2020, TBRF | 4 | arXiv:2007.09945v2 | Gesture Recognition for Initiating Human-to-Robot Handovers Jun Kwan, Chinkye  |
| `Larsson2016_wall_stress.pdf` | Larsson et al. 2016, WMLES review | 11 | arXiv:1512.04579v1 | A numerical method to solve higher-order fractional differential equations Ric |
| `Ling2015_ml_uncertainty.pdf` | Ling & Templeton 2015, regions of high RANS uncertainty | 26 | arXiv:1509.08935v1 | Accepted for publication in The Astronomical Journal Preprint typeset using LA |
| `Ling2016_reynolds_neural_nets.pdf` | Ling, Kurzawski & Templeton 2016, TBNN | 15 | arXiv:1606.01151v4 | Using Neural Generative Models to Release Synthetic Twitter Corpora with Reduc |
| `List2022_learned_turbulence.pdf` | List, Chen & Thuerey 2022, differentiable solvers | 26 | arXiv:2001.04881v1 | Modeling Transport of Charged Species in Pore Networks: Solution of the Nernst |
| `Lozano_Duran2023_wall_model.pdf` | Lozano-Duran & Bae 2023, building-block-flow wall model | 29 | arXiv:2105.14103v2 | An Attention Free Transformer Shuangfei Zhai Walter Talbott Nitish Srivastava  |
| `Maulik2017_neural_deconvolution.pdf` | Maulik & San 2017, blind deconvolution | 29 | arXiv:1811.11285v1 | On Identities of the Rogers–Ramanujan Type Andrew V. Sills Received May 2003;  |
| `Maulik_San2017_neural.pdf` | Maulik & San 2017, blind deconvolution | 12 | arXiv:1709.05372v2 | WEAK EQUIVALENCE TO BERNOULLI SHIFTS FOR SOME ALGEBRAIC ACTIONS BEN HAYES Abst |
| `Parish2016_field_inversion_ml_paradigm.pdf` | Parish & Duraisamy 2016, FIML paradigm | 14 | — | Journal of Computational Physics 313 (2016) 233–246 Contents lists available a |
| `Park2021_neural_les.pdf` | Park & Choi 2021, NN-based LES of channel flow | 11 | arXiv:1710.07195v4 | Global performance metrics for synchronization of heterogeneously rated power  |
| `Schmelzer2020_algebraic_reynolds.pdf` | Schmelzer, Dwight & Cinnella 2020, SpaRTA | 25 | arXiv:1907.01883v3 | Numerical homogenization for nonlinear strongly monotone problems∗ Barbara Ver |
| `Singh2016_field_inversion_functional.pdf` | Singh & Duraisamy 2016, field inversion for functional errors | 7 | arXiv:1606.00678v2 | RPP: Automatic Proof of Relational Properties by Self-Composition Lionel Blatt |
| `Singh2017_ml_airfoils.pdf` | Singh, Medida & Duraisamy 2017, ML-augmented airfoils | 5 | arXiv:1611.07749v2 | Calculated g-factors of 5d double perovskites Ba2 NaOsO6 and Ba2 YOsO6 Kyo-Hoo |
| `Sirignano2020_dpm_les.pdf` | Sirignano, MacArt & Freund 2020, DPM | 29 | arXiv:1910.01155v3 | Stochastic gradient descent for hybrid quantum- classical optimization Ryan Sw |
| `Strofer2021_differentiable.pdf` | Michelen Strofer & Xiao 2021, end-to-end differentiable | 8 | arXiv:2007.13142v1 | Fractionalized Spin Excitations in the Edge Ferromagnetic State of Graphene: S |
| `Um2020_solver_loop.pdf` | Um et al. 2020, solver-in-the-loop | 15 | arXiv:2006.13022v1 | 1 Bridging the Theoretical Bound and Deep Algorithms for Open Set Domain Adapt |
| `Vreman2004_eddy_viscosity_subgrid.pdf` | Vreman 2004, eddy-viscosity SGS model | 3 | arXiv:physics/0409022v1 | Critical dimension of Spectral Triples Alejandro RIVERO ∗† November 8, 2018 Ab |
| `Weatheritt2016_evolutionary_rans.pdf` | Weatheritt & Sandberg 2016, GEP algebraic stress | 16 | arXiv:1611.08830v1 | On the Distinction of Functional and Quality Requirements in Practice Jonas Ec |
| `Wu2017_physics_ml_reconstruction.pdf` | Wang, Wu & Xiao 2017, PIML reconstruction | 18 | arXiv:1705.10090v1 | CONSTANT ANGLE SURFACES IN LORENTZIAN BERGER SPHERES IRENE I. ONNIS, APOENA PA |
| `Wu2018_physics_augmenting.pdf` | Wu, Xiao & Paterson 2018, PIML framework | 15 | arXiv:1708.08690v1 | The Bishop-Phelps-Bollobás property for numerical radius of operators on L1(µ |
| `Xiao2016_model_uncertainties.pdf` | Xiao et al. 2016, Bayesian model-form UQ | 9 | arXiv:1607.00652v1 | Fuzzy sets in ≤–hypergroupoids Niovi Kehayopulu Abstract. This paper serves as |
| `Yang2019_predictive_wall_neural.pdf` | Yang et al. 2019, PINN wall model | 12 | arXiv:1904.09208v1 | Mean Force Kinetic Theory: a Convergent Kinetic Theory for Weakly and Strongly |

---

# 4. PENDING-MIT — 16 titles for an institutional pull

**These are not retrievable from open sources.** Every one was attempted by the open-access
retrieval agents and every attempt either hit a publisher paywall or returned an unrelated paper
(§3). They are listed here for **Sanaa's institutional access**; nothing else in the lab is blocked
on anything else.

**Status of every row below: `BLOCKED-ON-SOURCE`. No number from any of these papers appears
anywhere in the lab's documents**, per the standing rule that a number is quoted only from a
title-page-verified PDF. Where a document needs one of these papers it carries a stub with no
numeric claim.

**DOI caveat.** The DOIs below are **bibliographic identifiers stated from reference knowledge, not
read off a retrieved file.** They are provided to make the institutional pull mechanical. **Each
must be title-page-verified on arrival like any other retrieval** — a DOI is an identifier, and
§VERIFICATION RULE applies to identifiers exactly as it applies to arXiv IDs.

| # | shelf | citation | DOI (unverified, bibliographic) | why it is wanted | what is blocked without it |
|---|---|---|---|---|---|
| 1 | A | Gatski, T.B. & Speziale, C.G. (1993), On explicit algebraic stress models for complex turbulent flows, *J. Fluid Mech.* 254:59-78 | `10.1017/S0022112093002034` | The EASM derivation itself, its regularisation of the singular denominator, and its validation cases | Only the **1996 handbook chapter** is on disk, and it is a **300-dpi scan with no text layer** — it cannot be grepped or machine-checked, and it prints only the 2-D quadratic reduction, not the 3-D form |
| 2 | C | Parish, E.J. & Duraisamy, K. (2016), A paradigm for data-driven predictive modeling using field inversion and machine learning, *J. Comput. Phys.* 305:758-774 | `10.1016/j.jcp.2015.11.012` | The founding FIML paper | Category C is catalogued from its *application* (Singh 2017) rather than its foundation |
| 3 | C | Singh, A.P. & Duraisamy, K. (2016), Using field inversion to quantify functional errors in turbulence closures, *Phys. Fluids* 28:045110 | `10.1063/1.4947045` | Field inversion as an error-quantification tool | — |
| 4 | C | Holland, J.R., Baeder, J.D. & Duraisamy, K. (2019), Field inversion and machine learning with embedded neural networks, *AIAA Aviation Forum* 2019-3200 | `10.2514/6.2019-3200` | The **integrated** FIML formulation (Duraisamy 2021 Eq. 9) — the only form the reviews say "ensures full consistency between the learning and prediction environments" | **The largest single hole in the corpus.** The lab can read the claim but not the method |
| 5 | B | Weatheritt, J. & Sandberg, R.D. (2016), A novel evolutionary algorithm applied to algebraic modifications of the RANS stress-strain relationship, *J. Comput. Phys.* 325:22-37 | `10.1016/j.jcp.2016.08.015` | Gene-expression programming — the population-based control against SpaRTA's deterministic elastic net | A GEP-vs-SpaRTA comparison |
| 6 | X | Ling, J. & Templeton, J. (2015), Evaluation of machine learning algorithms for prediction of regions of high RANS uncertainty, *Phys. Fluids* 27:085103 | `10.1063/1.4927765` | The **origin of the feature set** used at second hand by four on-disk papers (Wang/Wu/Xiao 2017, Wu 2018, Kaandorp 2020, de Zordo-Banliat 2023) | The lab uses this feature set in four papers without being able to read its derivation |
| 7 | D | Emory, M., Larsson, J. & Iaccarino, G. (2013), Modeling of structural uncertainties in RANS closures, *Phys. Fluids* 25:110822 | `10.1063/1.4824659` | Eigenvalue perturbation | **The cheapest high-value item in the programme**: `FEASIBILITY.md` §1.2 prices the falsifiable a-priori question — *does the LES truth lie inside the 1c/2c/3c envelope?* — at **< 1 core-hour on frozen fields, no solve, no ML** |
| 8 | D | Iaccarino, G., Mishra, A.A. & Ghili, S. (2017), Eigenspace perturbations for uncertainty estimation of single-point turbulence closures, *Phys. Rev. Fluids* 2:024605 | `10.1103/PhysRevFluids.2.024605` | **Eigenvector** perturbation | This is exactly the axis Xiao et al. 2016 declined to perturb on stability grounds, and the reason they state their posterior may not contain the truth. Neither half of that loop is readable here |
| 9 | E | Vreman, A.W. (2004), An eddy-viscosity subgrid-scale model for turbulent shear flow: algebraic theory and applications, *Phys. Fluids* 16(10):3670-3681 | `10.1063/1.1785131` | A standard SGS control | `FOUNDATIONAL_MODELS_INVENTORY.md` §11 writes the model from background knowledge and **flags four claims that must be checked against the real paper**, including whether the near-wall decay is `y^1` rather than WALE's `y^3` |
| 10 | E | Park, J. & Choi, H. (2021), Toward neural-network-based large eddy simulation: application to turbulent channel flow, *J. Fluid Mech.* 914:A16 | `10.1017/jfm.2020.931` | The **wall-bounded** learned-SGS case | **The corpus's biggest physics gap**: every learned SGS paper on disk is isotropic (Beck, Sirignano) or two-dimensional (both Mauliks, Guan). There is no wall-bounded learned SGS closure at all |
| 11 | F | Bose, S.T. & Park, G.I. (2018), Wall-modeled large-eddy simulation for complex turbulent flows, *Annu. Rev. Fluid Mech.* 50:535-561 | `10.1146/annurev-fluid-122316-045241` | WMLES review | Framing is taken instead from Larsson 2016 and Piomelli & Balaras 2002, both journal-of-record on disk |
| 12 | F | Yang, X.I.A., Zafar, S., Wang, J.-X. & Xiao, H. (2019), Predictive large-eddy-simulation wall modeling via physics-informed neural networks, *Phys. Rev. Fluids* 4:034602 | `10.1103/PhysRevFluids.4.034602` | The physics-informed middle ground between the algebraic equilibrium wall model and the fully learned models of Bae 2022 / Lozano-Duran 2023 | `FEASIBILITY.md` §1.5: its a-priori part would cost **< 1 core-hour** here once the source arrives |
| 13 | E | Zanna, L. & Bolton, T. (2020), Data-driven equation discovery of ocean mesoscale closures, *Geophys. Res. Lett.* 47:e2020GL088376 | `10.1029/2020GL088376` | Equation discovery outside aerodynamics | — |
| 14 | H | Edeling, W.N., Cinnella, P. & Dwight, R.P. (2014), Predictive RANS simulations via Bayesian model-scenario averaging, *J. Comput. Phys.* 275:65-91 | `10.1016/j.jcp.2014.06.052` | The **scenario-averaging** ancestor of de Zordo-Banliat's space-dependent aggregation | Also blocked on **data**: its scenario set is boundary-layer experiments (Coles-Wadcock / Clauser families), not on disk |
| 15 | E | Germano, M., Piomelli, U., Moin, P. & Cabot, W.H. (1991), A dynamic subgrid-scale eddy viscosity model, *Phys. Fluids A* 3(7):1760-1765 | `10.1063/1.857955` | The dynamic procedure — the control every learned SGS closure is implicitly measured against | Distilled from background knowledge in `FOUNDATIONAL_MODELS_INVENTORY.md` §9 and **tagged there as unverified** |
| 16 | E | Bardina, J., Ferziger, J.H. & Reynolds, W.C. (1980), Improved subgrid-scale models for large-eddy simulation, *AIAA Paper 80-1357* | `10.2514/6.1980-1357` | Scale similarity — the `SS` baseline that **beats the ANN on five of six stress components** in Maulik & San 2017 Table 6 | — |

**On arrival**: each file is title-page-verified, added to §1 with a script-generated sha256, removed
from this section, and the documents carrying its `BLOCKED-ON-SOURCE` stub are revisited. Two papers
already went through exactly this path on 2026-08-20 —
`Wu2018_rans_explicit_closure_ill_conditioned.pdf` and `Guan2022_stable_aposteriori_les_cnn.pdf` —
and both changed conclusions in documents already written (LESSONS L-163).

---

# 5. NOTES

- **`Gatski1996_handbook_chapter6.pdf`** (77 pp) was uploaded, and the pre-audit manifest recorded it,
  as Gatski & Speziale (1993) *JFM* 254:59-78. **It is not that paper.** Page 1 was rendered with
  `pdftoppm -png -r 90 -f 1 -l 1` and read by eye: it is **Gatski, ch. 6 "Turbulent flows: model
  equations and solution methodology", *Handbook of Computational Fluid Mechanics*, Academic Press
  1996, ISBN 0-12-553010-2, pp. 339-414**. It is a **300-dpi bitonal scan with no text layer**
  (`pdftotext` returns 77 bytes for 77 pages), so it **cannot be grepped, quoted by text search, or
  machine-checked** — every quotation from it in the catalogue was read off a rendered page image and
  carries the printed page number so it can be re-rendered (PDF page = printed page − 338). Gatski &
  Speziale 1993 remains **PENDING-MIT** (§4 row 1).
- **`_WRONG_RETRIEVALS/Parish2016_field_inversion_ml_paradigm.pdf`** was uploaded **by hand**, not by
  the retrieval agent. Its title page reads *"ALmost EXact boundary conditions for transient
  Schrodinger-Poisson system"*, Bian, Pang, Tang & Arnold, **J. Comput. Phys. 313 (2016) 233-246** —
  right journal, right year, adjacent volume, wrong article. **A journal-and-year sanity check passed
  on a wrong document.** Hand uploads are not exempt from the verification rule.
- **`Ling2016_tbnn_embedded_invariance.pdf` architecture discrepancy — RECORDED, NOT RESOLVED.** The
  SAND2016-7345J preprint on disk states the TBNN is **8 hidden layers × 30 nodes, learning rate
  2.5e-7, per-point stochastic gradient descent** (p. 8), and attributes 10 layers / lr 2.5e-6 to its
  *baseline MLP* (p. 6). Kaandorp & Dwight 2020 (arXiv preprint pp. 16-17) attribute **10 layers, lr
  2.5e-5, Adam, mini-batch 1000** to the same paper. These cannot both be right; the JFM published
  version may differ from the SAND preprint. **For any reproduction, quote the on-disk SAND numbers
  and state that Kaandorp's differ** (LESSONS L-168).
- **`Strofer2021_differentiable.pdf` is arXiv v1** and contains **no ensemble-Kalman method and no
  EnKF-vs-adjoint comparison** (`grep -ci kalman` = 0). It also reports **no numeric error metric of
  any kind**. Do not attribute either to this file.
- **`Beck2019_deep_neural_les.pdf`**: the preprint title ("Deep Neural Networks for Data-Driven
  Turbulence Models") **differs from the journal title** ("Deep neural networks for data-driven LES
  closure models"). **`Sirignano2020_dpm_les.pdf`**: the preprint author order is **Freund, MacArt &
  Sirignano**, not the Sirignano-first order of the journal version.
- **PDFs are never committed to git** (lab convention). This manifest is.

## 5.1 Regenerating this file

```
/home/ubuntu/closure-venv/bin/python \
  /tmp/.../scratchpad/regen_manifest.py > manifest_data.json     # sha256, pages, page-1 title, arXiv stamp
```

Hashes, page counts and printed titles in §§1-3 come from that pass and were **not hand-edited**.
The citation, shelf, DOI and note columns are editorial and are hand-maintained.

## Addendum 3, 2026-08-21 — Sanaa's MIT pull (origin/main c99bce64)
| Paper | Filename | Verified |
|---|---|---|
| Emory, Larsson & Iaccarino 2013, Phys. Fluids 25:110822 | Emory2013_structural_uncertainty_rans.pdf | title page below |
| Iaccarino, Mishra & Ghili 2017, PRF 2:024605 (accepted ms) | Iaccarino2017_eigenspace_perturbations.pdf | title page below |
