# Certonomous Lab Paper Library

An organized index of the lab's computational fluid dynamics, turbulence modeling, and related research papers. Papers are organized by research topic and include metadata for discovery and reference.

**Last updated:** 2026-08-18  
**Total papers:** 56 PDFs with 45 extracted text sidecars  
**Scope:** Turbulence closure modeling, uncertainty quantification, data-driven methods, adjoint optimization, natural and mixed convection, data center airflow, benchmark validation studies

---

## Organization by Topic

### Uncertainty Quantification (8 papers)

Papers addressing quantification and propagation of uncertainties in turbulence models and CFD simulations.

| Title | Authors | Year | File Path | Notes |
|-------|---------|------|-----------|-------|
| Uncertainty Quantification and Sensitivity Analysis of Spalart Allmaras and Menter Shear Stress Model Coefficients for NACA0012 Airfoil | Sahni, Rezaeiravesh | 2026 | `uncertainty_quantification/sahni_rezaeiravesh_2026_uq_spalart.pdf` | AIAA SciTech Forum |
| Uncertainty Quantification and Sensitivity Analysis of SA Turbulence Model Coefficients in Two and Three Dimensions | Schaefer, Cary, Mani, Spalart | 2017 | `uncertainty_quantification/schaefer_2017_uq_sa_model.pdf` | AIAA SciTech Forum 2017 |
| Uncertainty Quantification of Turbulence Model Closure Coefficients for Transonic Wall-Bounded Flows | Schaefer, Hosder, West, Rumsey, Carlson, Kleb | 2017 | `uncertainty_quantification/schaefer_2017_uq_closure_transonic.pdf` | AIAA Journal 55(1) |
| Quantification of Structural Uncertainties in RANS Turbulence Models | Dow | 2011 | `uncertainty_quantification/dow_mit_sm2011_structural_uncertainties_rans.pdf` | MIT Master's thesis |
| Quantification of Structural Uncertainties in the k-ω Turbulence Model | Dow, Wang | 2011 | `uncertainty_quantification/dow_wang_aiaa2011_1762_komega_structural_uncertainty.pdf` | AIAA 2011-1762 |
| A Random Matrix Approach for Quantifying Model-Form Uncertainties in Turbulence Modeling | Xiao, Wang, Ghanem | 2016 | `uncertainty_quantification/xiao_wang_ghanem_1603.09656.pdf` | arXiv:1603.09656 |
| Dynamically orthogonal field equations for stochastic fluid flows and particle dynamics | Sapsis | 2011 | `uncertainty_quantification/sapsis_mit_phd2011_dynamically_orthogonal.pdf` | MIT PhD thesis |
| UQit: A Python package for uncertainty quantification (UQ) in computational fluid dynamics (CFD) | Rezaeiravesh, Vinuesa, Schlatter | 2021 | `uncertainty_quantification/rezaeiravesh_2021_uqit.pdf` | Journal of Open Source Software |

---

### Data-Driven RANS and Machine Learning Turbulence Models (12 papers)

Papers employing data-driven methods, neural networks, symbolic regression, and machine learning to develop or improve RANS turbulence closures.

| Title | Authors | Year | File Path | Notes |
|-------|---------|------|-----------|-------|
| Reynolds Averaged Turbulence Modeling using Deep Neural Networks with Embedded Invariance | Ling, Kurzawski, Templeton | 2016 | `data_driven_rans/ling_kurzawski_templeton_jfm2016_osti1333570.pdf` | SAND2016-7345J |
| Toward a unified data-driven turbulence model through multi-objective learning | Liu, Wang, Zhao, Xiao | 2026 | `data_driven_rans/liu_wang_zhao_xiao_2509.17189.pdf` | arXiv:2509.17189 |
| Machine Learning-augmented Predictive Modeling of Turbulent Separated Flows over Airfoils | Singh, Medida, Duraisamy | 2016 | `data_driven_rans/singh_medida_duraisamy_1608.03990.pdf` | arXiv:1608.03990 |
| Discovery of Algebraic Reynolds-Stress Models Using Sparse Symbolic Regression | Schmelzer, Dwight, Cinnella | 2020 | `data_driven_rans/schmelzer_dwight_cinnella_ftac2020_s10494-019-00089-x.pdf` | Flow, Turbulence and Combustion 104:579-603 |
| Data-Driven Optimization Approach for Inverse Problems: Application to Turbulent Mixed-Convection Flows | Oulghelou, Beghein, Allery | 2020 | `data_driven_rans/oulghelou_beghein_allery_2020_2009.06724.pdf` | arXiv:2009.06724 |
| Machine-learning-assisted Blending of Data-Driven Turbulence Models | Oulghelou, Cherroud, Merle, Cinnella | 2025 | `data_driven_rans/oulghelou_cherroud_merle_cinnella_ftac2025_2410.14431.pdf` | arXiv:2410.14431 |
| Constraining Genetic Symbolic Regression via Semantic Backpropagation | Reissmann, Fang, Ooi, Sandberg | 2025 | `data_driven_rans/reissmann_fang_ooi_sandberg_gpem2025_2409.07369.pdf` | arXiv:2409.07369 |
| Development of a Generalizable Data-driven Turbulence Model: Conditioned Field Inversion and Symbolic Regression | Wu, Zhang, Zhang | 2026 | `data_driven_rans/wu_zhang_zhang_2402.16355.pdf` | arXiv:2402.16355 |
| Coarse-Grid Computational Fluid Dynamic (CG-CFD) Error Prediction using Machine Learning | Hanna, Dinh, Youngblood, Bolotnov | 2018 | `data_driven_rans/hanna_dinh_youngblood_bolotnov_1710.09105.pdf` | Journal of Fluids Engineering |
| The Closure Challenge: a benchmark task for machine learning in turbulence modelling | McConkey, Buchanan, Smidt, Bodner, Dwight, Cinnella | 2026 | `data_driven_rans/mcconkey_et_al_closure_challenge_2603.28884.pdf` | arXiv:2603.28884 |
| The Training of the SST-QCRC Model | Wu, Zhang | 2022 | `data_driven_rans/wu_zhang_sst_qcrc_challenge_description.pdf` | Tsinghua University |
| RANS Turbulence Model Development using CFD-Driven Machine Learning | Zhao, Akolekar, Weatheritt, Michelassi, Sandberg | 2020 | `data_driven_rans/zhao_akolekar_weatheritt_michelassi_sandberg_1902.09075.pdf` | Journal of Computational Physics |

---

### Adjoint Methods and Design Optimization (DAFoam) (3 papers)

Papers on adjoint-based sensitivity analysis and gradient-based aerodynamic design optimization.

| Title | Authors | Year | File Path | Notes |
|-------|---------|------|-----------|-------|
| DAFoam: An Open-Source Adjoint Framework for Multidisciplinary Design Optimization with OpenFOAM | He, Mader, Martins, Maki | 2020 | `adjoint_and_optimization/he_mader_martins_maki_aiaaj2020_dafoam_J058853.pdf` | AIAA Journal |
| An Aerodynamic Design Optimization Framework Using a Discrete Adjoint Approach with OpenFOAM | He, Mader, Martins, Maki | 2018 | `adjoint_and_optimization/he_mader_martins_maki_caf2018_discrete_adjoint_openfoam.pdf` | Computers & Fluids 168:285-303 |
| Effective Adjoint Approaches for Computational Fluid Dynamics | Kenway, Mader, He, Martins | 2019 | `adjoint_and_optimization/kenway_mader_he_martins_pas2019_effective_adjoint_100542.pdf` | Progress in Aerospace Sciences |

---

### Gaussian Processes and Reduced-Order Models (5 papers)

Papers applying Gaussian process regression and reduced-order modeling techniques to fluid dynamics problems.

| Title | Authors | Year | File Path | Notes |
|-------|---------|------|-----------|-------|
| Solving Functional PDEs with Gaussian Processes and Applications to Functional Renormalization Group Equations | Yang, Darcy, Hudes, Alexander, Eyink, Owhadi | 2025 | `gaussian_processes_roms/yang_darcy_2025_gp_frg.pdf` | arXiv:2512.20956 |
| Sparse and Deep Gaussian Processes Closure for 2-D Fluids and Ocean Flows | Mouzahir, Lermusiaux | 2026 | `gaussian_processes_roms/mouzahir_lermusiaux_2026_osm26_closure.pdf` | OSM26 |
| Error Quantification of Gaussian Process Regression for Extracting Eulerian Velocity Fields from Ocean Drifters | Xia, Iskandarani, Gonçalves, Özgökmen | 2023 | `gaussian_processes_roms/xia_iskandarani_2023_gpr_velocity.pdf` | Journal of Marine Science and Engineering Vol. 13 |
| Sparse and Deep Gaussian Processes Closure for 2-D Fluids and Ocean Flows (Poster) | Mouzahir, Lermusiaux | 2026 | `gaussian_processes_roms/mouzahir_lermusiaux_2026_sparse_gp_poster.pdf` | Poster #DO24C1962 |
| Sparse and Deep Gaussian Processes Closure of Non-Stationary Flows (Poster) | Mouzahir, Lermusiaux | 2026 | `gaussian_processes_roms/mouzahir_lermusiaux_2026_sparse_gp_poster_pl.pdf` | Poster |

---

### Buoyant and Natural Convection (9 papers)

Experimental benchmark data, numerical studies, and modeling of natural and mixed convection in cavities and enclosures.

| Title | Authors | Year | File Path | Notes |
|-------|---------|------|-----------|-------|
| Spectral element simulations of buoyancy-driven flow | Gjesdal, Wasberg, Andreassen | 2003 | `buoyant_natural_convection/gjesdal_wasberg_andreassen_2003_physics0305049.pdf` | arXiv:physics/0305049 |
| Robust globally divergence-free weak Galerkin finite element methods for natural convection problems | Han, Xie | 2019 | `buoyant_natural_convection/han_xie_2019_1903.09506.pdf` | arXiv:1903.09506 |
| Experimental benchmark data for turbulent natural convection in an air filled square cavity | Ampofo, Karayiannis | 2003 | `buoyant_natural_convection/ampofo_karayiannis_2003_ijhmt_46.pdf` | Int. J. Heat Mass Transfer 46:3551-3572 | **GATE PRIMARY** |
| Low turbulence natural convection in an air filled square cavity Part I: the thermal and fluid flow fields | Tian, Karayiannis | 2000 | `buoyant_natural_convection/tian_karayiannis_2000_ijhmt_43.pdf` | Int. J. Heat Mass Transfer 43:849-866 | **GATE PRIMARY** |
| Experiments on turbulent natural convection in an enclosed tall cavity | Betts, Bokhari | 2000 | `buoyant_natural_convection/betts_bokhari_2000_ijhff_21.pdf` | Int. J. Heat Fluid Flow 21:675-683 | **GATE PRIMARY** |
| Benchmark solutions for the natural convective heat transfer problem in a square cavity | Vierendeels, Merci, Dick | 2002 | `buoyant_natural_convection/vierendeels_merci_dick_2002_wit_afm02.pdf` | Advances in Fluid Mechanics IV |
| Numerical modeling of particles deposition in domestic floor heating systems | Sadighi, Abbasalizadeh, Mirzaee | 2020 | `buoyant_natural_convection/sadighi_2020_particles_heating.pdf` | Int. J. Nonlinear Anal. Appl. 11(7):93-104 |
| Large eddy simulation of natural and mixed convection airflow indoors with two simple filtered dynamic subgrid scale models | Zhang, Chen | 2000 | `buoyant_natural_convection/zhang_chen_2000_les_indoor.pdf` | Numerical Heat Transfer Part A 37(5):447-463 | **GATE PRIMARY** |
| Simulation of Mixed Convection Flow in a Room with a Two-Layer Turbulence Model | Xu, Chen | 2000 | `buoyant_natural_convection/xu_chen_2000_indoor_air_two_layer.pdf` | Indoor Air 10:306-314 |

---

### Data Center and Indoor Airflow (7 papers)

CFD modeling, validation, and optimization of airflow and cooling in data centers and indoor environments.

| Title | Authors | Year | File Path | Notes |
|-------|---------|------|-----------|-------|
| Recovery Act: A Measurement - Management Technology for Improving Energy Efficiency in Data Centers and Telecommunication Facilities | Hamann, Klein | 2012 | `data_center_indoor_airflow/hamann_klein_2012_osti_1044604.pdf` | Technical Report DE-EE0002897 |
| Computational Fluid Dynamics Modeling and Validating Experiments of Airflow in a Data Center | Wibron, Ljung, Lundstrom | 2018 | `data_center_indoor_airflow/wibron_ljung_lundstrom_2018_en11030644.pdf` | Energies 11:1105 |
| Comparing Performance Metrics of Partial Aisle Containments in Hard Floor and Raised Floor Data Centers Using CFD | Wibron, Ljung, Lundstrom | 2019 | `data_center_indoor_airflow/wibron_ljung_lundstrom_2019_en12081473.pdf` | Energies 12:1473 |
| Airflow Uniformity Through Perforated Tiles in a Raised-Floor Data Center | VanGilder, Schmidt | 2005 | `data_center_indoor_airflow/vangil der_schmidt_2005_ipack.pdf` | ASME InterPACK IPACK2005-73375 | **GATE PRIMARY** |
| The IEA Annex 20 Two-Dimensional Benchmark Test for CFD Predictions | Nielsen, Rong, Olmedo | 2010 | `data_center_indoor_airflow/nielsen_rong_olmedo_2010_clima_annex20.pdf` | Clima 2010 |
| Computational fluid dynamics modeling of mixed convection flows in buildings enclosures | Kayne, Agarwal | 2013 | `data_center_indoor_airflow/kayne_agarwal_2013_mixed_convection.pdf` | Int. J. Energy Environment 4(6):911-932 | **GATE PRIMARY** |
| Comparison of STAR-CCM+ and ANSYS Fluent for Simulating Indoor Airflows | Zou, Zhao, Chen | 2018 | `data_center_indoor_airflow/zou_zhao_chen_2018_building_simulation.pdf` | Building Simulation 11(1):165-174 |

---

### Verification and Validation Methodology (3 papers)

Foundational works on verification, validation, and numerical uncertainty estimation in CFD.

| Title | Authors | Year | File Path | Notes |
|-------|---------|------|-----------|-------|
| A procedure for the estimation of the numerical uncertainty of CFD calculations based on grid refinement studies | Eça, Hoekstra | 2014 | `verification_validation/eça_hoekstra_2014_numerical_uncertainty.pdf` | Journal of Computational Physics 262:104-130 |
| Overview of ASME V&V 20-2009 Standard for Verification and Validation in Computational Fluid Mechanics and Heat Transfer | Dowding | 2016 | `verification_validation/dowding_2016_asme_vv.pdf` | Sandia Report SAND2016-5342C |
| Verification and Validation in Scientific Computing | Oberkampf, Roy | 2011 | `verification_validation/oberkampf_roy_2011_verification_validation.pdf` | Cambridge University Press |

---

### Benchmark Test Cases (4 papers)

Detailed descriptions and DNS/LES data for canonical flow geometries used for turbulence model validation.

| Title | Authors | Year | File Path | Notes |
|-------|---------|------|-----------|-------|
| Flow over periodic hills – Numerical and experimental study in a wide range of Reynolds numbers | Breuer, Peller, Rapp, Manhart | 2009 | `benchmark_test_cases/breuer_peller_rapp_manhart_caf2009_periodic_hills.pdf` | Computers & Fluids 38:433-457 |
| A Separation Control CFD Validation Test Case Part 1: Baseline & Steady Suction | Greenblatt et al. | 2004 | `benchmark_test_cases/greenblatt_et_al_cfdval2004_hump.pdf` | AIAA 2004-2220 |
| Reynolds number dependence of mean flow structure in square duct turbulence | Pinelli, Uhlmann, Sekimoto, Kawahara | 2010 | `benchmark_test_cases/pinelli_uhlmann_sekimoto_kawahara_jfm2010_square_duct.pdf` | Journal of Fluid Mechanics 644:107-122 |
| Aspect ratio effects in turbulent duct flows studied through direct numerical simulation | Vinuesa et al. | 2014 | `benchmark_test_cases/vinuesa_et_al_jot2014_duct_aspect_ratio.pdf` | Journal of Turbulence |

---

### Turbulence Model Closure and Theory (4 papers)

Foundational theoretical work on turbulence modeling, eddy viscosity hypotheses, and closure approaches.

| Title | Authors | Year | File Path | Notes |
|-------|---------|------|-----------|-------|
| A One-Equation Turbulence Model for Aerodynamic Flows | Spalart, Allmaras | 1992 | `turbulence_models/spalart_allmaras_1992_turbulence_model.pdf` | AIAA-92-G439 |
| A more general effective-viscosity hypothesis | Pope | 1975 | `turbulence_models/pope_jfm1975_effective_viscosity_hypothesis.pdf` | Journal of Fluid Mechanics 72(2):331-340 |
| Visualizing turbulence anisotropy in the spatial domain with componentality contours | Emory, Iaccarino | 2014 | `turbulence_models/emory_iaccarino_ctr2014_componentality_contours.pdf` | Center for Turbulence Research Annual Research Briefs 2014 |
| On the Development of Turbulent Wakes from Vortex Streets | Roshko | 1954 | `turbulence_models/roshko_1954_naca_tr_1191.pdf` | NACA Report 1191 |

---

### Unsorted (1 paper + archival text files)

| File Path | Notes |
|-----------|-------|
| `unsorted/Urop_summer_2026.pdf` | UROP 2026 summer research report (incomplete metadata) |
| `unsorted/martineau_et_al_2009_inl_ext_09_15333.txt` | INL technical note (text only) |
| `unsorted/nasa_turbmodels_2dhill_periodic_page.txt` | NASA turbulence model periodic hills benchmark page (text only) |
| `unsorted/nasa_turbmodels_nasahump_val_page.txt` | NASA turbulence model NASA hump validation page (text only) |

---

## Gate Primary Papers

The following papers are marked as gate primaries and bind to gate rows in the lab's tracking system:

1. **Ampofo & Karayiannis (2003)** - Experimental benchmark data for turbulent natural convection in an air filled square cavity  
   `buoyant_natural_convection/ampofo_karayiannis_2003_ijhmt_46.pdf`

2. **Tian & Karayiannis (2000) Part I** - Low turbulence natural convection in an air filled square cavity  
   `buoyant_natural_convection/tian_karayiannis_2000_ijhmt_43.pdf`

3. **Betts & Bokhari (2000)** - Experiments on turbulent natural convection in an enclosed tall cavity  
   `buoyant_natural_convection/betts_bokhari_2000_ijhff_21.pdf`

4. **VanGilder & Schmidt (2005)** - Airflow Uniformity Through Perforated Tiles in a Raised-Floor Data Center  
   `data_center_indoor_airflow/vangil der_schmidt_2005_ipack.pdf`

5. **Zhang & Chen (2000)** - Large eddy simulation of natural and mixed convection airflow indoors  
   `buoyant_natural_convection/zhang_chen_2000_les_indoor.pdf`

---

## Statistics

| Metric | Count |
|--------|-------|
| Total papers | 56 |
| Total .txt sidecars | 45 |
| Uncertainty Quantification | 8 |
| Data-Driven RANS | 12 |
| Adjoint & Optimization | 3 |
| Gaussian Processes & ROMs | 5 |
| Buoyant & Natural Convection | 9 |
| Data Center & Indoor Airflow | 7 |
| Verification & Validation | 3 |
| Benchmark Test Cases | 4 |
| Turbulence Models | 4 |
| Unsorted/Archival | 1 |

---

## File Naming Convention

Papers follow the naming convention: `lastname_year_keywordidentifier.pdf`

Examples:
- `spalart_allmaras_1992_turbulence_model.pdf`
- `he_mader_martins_maki_aiaaj2020_dafoam_J058853.pdf`
- `ampofo_karayiannis_2003_ijhmt_46.pdf`

Each PDF has a corresponding `.txt` file containing extracted text (where available for OCR/text searching).

