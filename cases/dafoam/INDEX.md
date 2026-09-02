# `cases/dafoam/` — INDEX

**Written 2026-08-21 by DAFoam team Lane B. Nothing was moved, renamed, deleted or
edited to produce this file.** It is a read-only map: it states what each logical case
is, where its record / config / logs / work directory actually live today, and what the
directory would be called if the lab's `cases/<family>/<case>/PREREGISTRATION.md +
RESULTS.md` convention were applied. **The proposed names in §7 are proposals only; the
supervisor confirms them before any new directory is created.**

Tree size at writing: **6.7 GB** total (`du -sh`, 2026-08-21). 78 loose `*.log` files at
the top level, 3.3 MB combined.

## 0. The convention gap, stated plainly

The lab's other case family that follows a preregistration convention is the closure
team's, and its actual on-disk shape is **not** `cases/closure/<ladder>/<case>/`:

- `cases/closure/` **does not exist** (`ls`, 2026-08-21).
- The closure team's cases live at
  `cases/RANS_LES_closure_models/<PaperKey>/{PREREGISTRATION.md, RESULTS.md}` — a flat,
  paper-keyed layout with a shared `_common/` (four cases: `Kaandorp2020_TBRF`,
  `Wu2018_PIML_RF`, `Ling2016_TBNN`, `Schmelzer2020_SpaRTA`; `_common/` holds
  `BASELINES.md`, `FEASIBILITY.md`, the scorer and dataset builders).
- Those eight files are the **only** `PREREGISTRATION.md`/`RESULTS.md` pair-files
  anywhere under `cases/` (`find cases -name PREREGISTRATION.md -o -name RESULTS.md`).

`cases/dafoam/` follows a different, older shape that grew by ladder rung and by well
(W4/W5) rather than by case:

| shape | where it is used here |
|---|---|
| `<RUNG>_<name>.md` + `<RUNG>_<name>.json` beside each other | `ladder-a/A1..A6`, `ladder-a/A_stepsize_study`, `ladder-b/B2`, `ladder-b/B3` |
| `<ITEM>_PREREGISTRATION.md` + `<ITEM>_RESULT.md` as two top-level files | `ladder-b/S1_CBFS_{INVERSION,REINVERSION,WEIGHTED_ARM}_*`, `A3_*_PREREGISTRATION/RESULT` |
| one `.md` with pre-registration and results in dated parts | `ladder-b/S1_CBFS_WEIGHTED_LOSS_VARIANT.md`, `ladder-b/W4_ADJOINT_PC_UNBLOCK.md` |
| a `PREDICTION*.md` written before the run, never edited after | `f6a_epistemic_band/PREDICTION.md`, `f6b_periodic_hills/PREDICTION_before_run.md` |
| `*_work/` or `<case>/` sibling holding the OpenFOAM case, scripts and logs | `ladder-b/B3_work`, `ladder-b/S1_work`, `ladder-a/A5_work`, `f6a_nasa_hump/case` |
| bare `logs_<RUNG>/` directories | `ladder-a/logs`, `logs_A1_stepsize`, `logs_A3`, `logs_A4`, `logs_A6` |
| loose top-level `*.log` with no case directory at all | the 78 files in §6 |

**Do not move anything to close this gap.** Several records cite paths inside these trees
by name (e.g. `B3_duct_field_inversion.md` "Evidence files"; `WARMSTART_AUDIT.md` row 1
cites `B3_work/fixA_kbounds/stage2_serial_run3.log:471`), and the family's own record
hygiene rule is that a satellite citing a path its case file contradicts is a defect
(`FAMILY_SUPERVISION_GUIDELINES.md` §7). This index is the mapping layer instead.

**A path caveat that bites every reader:** most records were written when this tree lived
at `demo-output/website/dafoam/`, and their "Evidence files" sections still say so
(e.g. `ladder-b/B2_duct_baseline.md:214-221`, `ladder-b/B3_duct_field_inversion.md:347-358`,
`f6c_duct_dns/F6c_duct_vs_dns.md:89-95`). Read `demo-output/website/dafoam/` as
`cases/dafoam/` throughout. Run trees under `/home/ubuntu/certonomous-runs/` are **outside
this repo** and are not indexed here.

---

## 1. Ladder A — DAFoam verification / reproduction ladder

Root: `cases/dafoam/ladder-a/` (15 MB). Convention name would be
`cases/dafoam/ladder-a/<RUNG>/`.

| convention name | record (.md) | config (.json) | logs | work dir | size |
|---|---|---|---|---|---|
| `ladder-a/A1/` | `ladder-a/A1_naca0012_incompressible.md` (12K) | `ladder-a/A1_naca0012_incompressible.json` (12K) | `ladder-a/logs/{check_totals_run1,check_totals_run2,compute_totals_run1}.log`, `logMeshGeneration.txt`, `preproc_stdout.log`; plus 60 loose top-level logs (§6) | `work/NACA0012_Airfoil_Incompressible/` (13M), `work_refined/NACA0012_Airfoil_Incompressible{,_probe,_refined}/` (18M) | 31M |
| `ladder-a/A_stepsize/` | `ladder-a/A_stepsize_study.md` (12K) | `ladder-a/A_stepsize_study.json` (20K) | `ladder-a/logs_A1_stepsize/` (1.3M, 14 entries: `fdStepSweep.py` + `fdsweep_1e-1..1e-8*.log`) | shares A1's `work/` | 1.3M |
| `ladder-a/A2/` | `ladder-a/A2_mach_tutorial_wing.md` (12K) | `ladder-a/A2_mach_tutorial_wing.json` (16K), `A2_optimization_history.json` (16K), `A2_shape_frames.json` (1.5M) | in `w5_regrade/a2_*.tail.log` (4 files) | none in-tree | 1.5M |
| `ladder-a/A3/` | `ladder-a/A3_onera_m6.md` (16K) + 13 top-level `A3_*_PREREGISTRATION.md` / `A3_*_RESULT.md` (§5) | `ladder-a/A3_onera_m6.json` (20K) | `ladder-a/logs_A3/` (628K, 20 entries incl. `check_totals_{vcoarse,coarse_run1..3,fine_12g,fine_18g}*.log`, `case_2308.dat`, `compare_cp.py`) | none in-tree | 660K |
| `ladder-a/A4/` | `ladder-a/A4_ahmed_body.md` (24K); mechanism work in `DISCRIMINATORS_A4_decomposition_mechanism.md` (20K), `A4_SIMPLEC_ACTIVITY_PROOF_PREREGISTRATION.md` (8K) | `ladder-a/A4_ahmed_body.json` (16K) | `ladder-a/logs_A4/` (2.5M, 10 entries incl. `A4_check_totals_run1.log`, `A4_fine_primal_par4.log`, snappyHexMesh/checkMesh logs, `A4_ahmedFFD.xyz`) | none in-tree | 2.5M |
| `ladder-a/A5/` | `ladder-a/A5_ubend_internal.md` (88K) | `ladder-a/A5_ubend_internal.json` (24K) | `ladder-a/logs/A5_*.log` (11 files); plus 11 loose top-level `a5_*`/`probewarpderiv_a5_*` logs (§6) | `ladder-a/A5_work/UBend_Channel_pressureloss/` (4.7M) | 4.8M |
| `ladder-a/A6/` | `ladder-a/A6_crm_wingbody.md` (16K) | `ladder-a/A6_crm_wingbody.json` (16K) | `ladder-a/logs_A6/` (104K, 6 entries: `decomposePar.log`, `run_model_accepted_t0_to_t1000.log`, `run_model_attempt2_corrupted_checkpoint_read.log`, `runScript.py`, mesh logs) | none in-tree | 104K |

**Pre-ladder cases (predate the ladder; no A-rung name).** `work_sail/` (221M:
`naca0015_sail_{coarse,medium,full}`, `naca4412_wing_check`) and `work_wing/` (211M:
`naca4412_wing_coarse`). Verdicts live in `DAFOAM_CASE_STATUS.md:142-173`, not in a
ladder record. Convention name would be `cases/dafoam/pre-ladder/<case>/`.

---

## 2. Ladder B — closure-literature reproduction via DAFoam adjoint field inversion

Root: `cases/dafoam/ladder-b/` (177M).

| convention name | record (.md) | config (.json) | logs / work dir | size |
|---|---|---|---|---|
| `ladder-b/B1/` | `ladder-b/B1_reproduction_plans.md` (28K) | none | none — research only, zero compute | 28K |
| `ladder-b/B2/` | `ladder-b/B2_duct_baseline.md` (16K) | `ladder-b/B2_duct_baseline.json` (20K, amended 2026-08-17: eval-package commit pin) | `ladder-b/duct_baseline/` (28M): `AR_1_Ret_360/` (2.5M, `0/`, `456/`, `log.run` 462K, `caseDef`, `fieldDef`, `secondary_flow_gate.json`), `AR_3_Ret_360/` (5.6M, `1700/`), `CBFS/` (20M, `0/`, `30000/`, `log.run.gz` 5.4M) | 28M |
| `ladder-b/B3/` | `ladder-b/B3_duct_field_inversion.md` (24K) + `ladder-b/B3_supervisor_debug.md` (16K) | `ladder-b/B3_duct_field_inversion.json` (12K) | `ladder-b/B3_work/` (147M): `CBFS/` (39M — `runScript{,_stage2,_diag_force,_diag_frozen}.py`, `adjoint_pilot_run1..6.log`, `stage2_{serial,warm,smoke}_run*.log`, `diag_force_run{1,2}.log`, `decomp_test{,2,3}.log`, `dRdWColoring_{1,4}.bin`, times `0/1000/1500/1584/500`), `fixA_kbounds/` (49M), `fixB_SA/` (30M), `fixC_empty/` (30M) — the three supervisor-debug rungs | 147M |
| `ladder-b/S1-cbfs-inversion/` | `ladder-b/S1_CBFS_INVERSION_PREREGISTRATION.md` (20K, + Amendment 1) and `ladder-b/S1_CBFS_INVERSION_RESULT.md` (16K) | none | run tree **outside repo**: `/home/ubuntu/certonomous-runs/S1-cbfs-inversion/` | 36K |
| `ladder-b/S1-cbfs-reinversion/` | `ladder-b/S1_CBFS_REINVERSION_PREREGISTRATION.md` (16K, + Amendment 1) and `ladder-b/S1_CBFS_REINVERSION_RESULT.md` (16K) | none | `/home/ubuntu/certonomous-runs/S1-cbfs-reinversion/` (outside repo) | 32K |
| `ladder-b/S1-cbfs-weighted-loss-offline/` | `ladder-b/S1_CBFS_WEIGHTED_LOSS_VARIANT.md` (12K — Part I prereg + Part II results in one file) | none | zero solver compute; host-side arithmetic on written fields | 12K |
| `ladder-b/S1-cbfs-weighted-arm/` | `ladder-b/S1_CBFS_WEIGHTED_ARM_PREREGISTRATION.md` (12K, Parts A/B/C + Budget Amendment 1) and `ladder-b/S1_CBFS_WEIGHTED_ARM_RESULT.md` (12K, + eval-8 addendum) | none | `/home/ubuntu/certonomous-runs/S1-cbfs-weighted-arm/` (outside repo) | 24K |
| `ladder-b/S1-fiml/` | `ladder-b/S1_FIML_FIELD_INVERSION.md` (40K, 599 lines) | none | `ladder-b/S1_work/` (2.5M): `logs/` (2.4M — `hump_{adjoint,wf,nrn,nat,nofvopt}_run1.log`, `hump_mem_run1.log`, `fd_sweep_run1.log`, `fd_clip_audit_run1.log`, `fd_points/`, `r1_*.out`, `s1_e{1,2}*.json`) and `scripts/` (104K — `runScript_S1.py`, `runScript_hump{,_nat,_nrn,_wf}.py`, `analyze_fd.py`, `build_ref.py`, `make_fd_points.py`, `r1_*.py`) | 2.5M |
| `ladder-b/S1-sensitivity-vs-error/` (R1) | `ladder-b/S1_SENSITIVITY_VS_ERROR.md` (28K) | none | scripts/outputs archived inside `ladder-b/S1_work/{scripts,logs}` (`r1_sens_vs_error.py`, `r1_geography.py`, `r1_confounds.py`, `r1_final.py` + four `.out`) | shared |
| `ladder-b/S1-priors/` (unrun) | `ladder-b/S1_PRIORS_PREREGISTRATION.md` (44K, **canonical**) and `ladder-b/S1_WITH_PRIORS_PREREGISTRATION.md` (40K, **superseded duplicate**, retained) | proposal JSON in `agenda/proposals/` (not in this tree) | **no run directory exists** — that absence is itself the W-3 legality evidence (`S1_PRIORS_PREREGISTRATION.md` §4a) | 84K |
| `ladder-b/W4-adjoint-pc-unblock/` | `ladder-b/W4_ADJOINT_PC_UNBLOCK.md` (32K, 417 lines) | none | patch at `subpclu_patch/DALinearEqn_subpclu.patch` (8K); runs at `/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/` (outside repo) | 40K |

---

## 3. F6 series and the RANS model comparison

These are **campaign** cases (family F6, "Certonomous hard-case campaign"), not DAFoam
ladder rungs — every one is a **plain OpenFOAM `simpleFoam`** solve; no DAFoam adjoint
runs anywhere in F6a–F6d or `rans_model_comparison`. They sit under `cases/dafoam/` for
historical reasons; **their analysis records live in a different tree entirely**, at
`verification/campaign/` (the records cite it as `campaign/`): `F6_closure_aligned_flows.md`,
`F6a_epistemic_band.md`, `F6a_epistemic_propagation.md`, `F6a_EPISTEMIC_CASE.md`,
`F6a_DIFFUSION_{PREREGISTRATION,RESULTS}.md`, `F6b_ERCOFTAC_{PREREGISTRATION,RESULTS}.md`,
`F6b_QCR_{PREREGISTRATION,RESULTS}.md`, `F6b_RELAXATION_INVARIANCE_{PREREGISTRATION,RESULTS}.md`,
`F6d_random_matrix_uq.{md,json}`, `F6D_OPTION_A_{PREREGISTRATION,RESULT}.md`,
`F6D_COLLISION_INDEPENDENCE_CHECK.md`, `F6D_ENSEMBLE_CONVERGENCE_AUDIT.md`, plus
`verification/runs/F6b_runs/`. **A reader who looks only in `cases/dafoam/` will conclude
F6a-band and F6d have no records; they have many, in the other tree.** Convention name
would be `cases/f6/<sub>/`.

| convention name | record | config | case/logs | size |
|---|---|---|---|---|
| `f6/F6a-nasa-hump/` | `f6a_nasa_hump/F6a_nasa_hump.md` | `f6a_nasa_hump/F6a_nasa_hump.json` | `case/` (`0/`, `800/`, `1772/`, `postProcessing/`, `log.rung1_feasibility`, `log.rung2_physics`, `log.rung3_gate`, `gate_result_1772.json`, `cf_xc_1772.csv`, `cp_xc_1772.csv`), `case_template/`, `nasa_experimental_reference/{noflow_cp.exp.dat,noflow_cf.exp.dat}`, `score_our_baseline.py` | **37M** |
| `f6/F6a-epistemic-band/` | `f6a_epistemic_band/PREDICTION.md` only (results record is under `docs/`, cited as `campaign/`) | none in-tree | `channel1_rans_sweep/{SpalartAllmaras,kEpsilon,kOmega,realizableKE}` (248M); `channel3_eigenvalue_perturbation/{oneC,twoC,threeC}` (169M); `r4_band_tightening_hump/` (880M, 15 delta arms `oneC_delta0.00 … 1.00_ramp`, `twoC_delta1.00_initFromBaseline`) | **1.3G** |
| `f6/F6b-periodic-hills/` | `f6b_periodic_hills/F6b_periodic_hills.md` + `PREDICTION_before_run.md` | `f6b_periodic_hills/F6b_periodic_hills.json` (written 2026-07-30, after the fact — disclosed at `F6b_periodic_hills.md:198-206`) | `case_breuer_re10595/` (71M: `0/`, `10000/`, `processor0..3/`, `postProcessing/`, `gate_analysis.py`, `foam_io.py`, `gate_result.json`) | **71M** |
| `f6/F6c-duct-vs-dns/` | `f6c_duct_dns/F6c_duct_vs_dns.md` | `f6c_duct_dns/F6c_duct_vs_dns.json`, `{AR_1_Ret_360,AR_3_Ret_360}_secondary_flow_gate.json` | `secondary_flow_gate.py`; **no case dir** — zero new CFD, post-processing of B2's fields | **28K** |
| `f6/F6d-random-matrix-uq/` | no `.md` in-tree; `f6d_random_matrix_uq/f6d_option_a/d0.2_s000/PROVENANCE_7500_CONTAMINATED.md` is the only markdown | `option_a_result.json` (24K), `aggregate_result.json` (48K), `cost.json`, `barycentric_reach.json`, `realizability_of_flipped_corner.json`, `verify_sampler_result.json` | `ens/` (2.7G, 80 members `d0.2_s000..039`, `d0.6_s000..039` + `corner_{oneC,twoC,threeC}` + `null`); `f6d_option_a/` (1.7G, 15 continued members + `null`); `f6a_recheck/` (195M); `signdemo/` (157M); `signcheck/` (60M); drivers `run_campaign.sh`, `run_option_a_queue.sh`, `rmt_sampler.py`, `aggregate.py`, `analyse{,_option_a}.py`, `plot_band.py`, `F6d_band.png` | **4.7G** — the single largest item in this tree |
| `f6/rans-model-comparison/` | none in-tree | `rans_model_comparison/sweep_results.json` | `{SpalartAllmaras,kEpsilon,kOmega,realizableKE,LienCubicKE}/` each with `0/`, converged time dir (354 / 597 / 274 / 2921 / 4780) and `log.run`; `collect_results.py` | **20M** |

---

## 4. Patches, reproducers and defect-campaign directories

| convention name | what it is | contents | size |
|---|---|---|---|
| `patches/subpclu/` | the W4 sub-LU patch (image `dafoam-subpclu:v1`) | `subpclu_patch/DALinearEqn_subpclu.patch` — one hunk at `DALinearEqn.C:266`, regenerated 2026-08-07 with `a/`/`b/` headers so `git apply --check` passes | 8.0K |
| `patches/kspopts/` | the KSP-options escape-hatch patch | `kspopts_patch/DALinearEqn_kspopts.patch` | 8.0K |
| `patches/idwarp-rotation/` | the IDWarp rotation-guard patch and its whole evidence branch | `rotation_branch/` — `idwarp_v2.6.2_degenerate_branch_fix.patch`, `repro_geometries.py`, `repro_issue57_inflate_cube.py`, `diag_rotation_ubend.py`, 20 `.txt` result files (`D1a..D6`, `geom_*`, `issue57_rot_{on,off}`), subdirs `patched/`, `patch_unittest/`, `independent_check/`, `supervisor_sweep/` | 424K |
| `upstream_repro/` | self-contained reproducer bundle for the `warpDeriv` report, built from a fresh upstream clone | `README.md` (environment pinned: image digest `sha256:9d45679d…`, OpenFOAM v2506, dafoam 5.0.0, idwarp 2.6.2, pygeo 1.13.0, petsc4py 3.15.5), `run_repro.sh`, `repro_warpderiv_{ubend,airfoil}.py`, 4 `repro_ubend_*_np4.log` | 184K |
| `w4_idx16/` | the W4 idx16 reference-remeasurement arm (L-31) | `run.sh` + 8 `probe_*.tail.log` (`probe_base`, `probe_idx16_{±1e-3,±1e-4}`, `probe_seq_idx16`, `probe_warm_idx{15,16}_1e-4`) | 172K |
| `w5_regrade/` | the W5 stock-vs-patched regrade sweep | 13 `*.tail.log`: `a1_{unpatched_stock,patched_patched}`, `a2_{twist_stock,twist_patched,rebuilt_runmodel,preserved_case_FAILED}`, `a4_{stock,patched}_checktotals`, `a5pl_{stock,patched}`, `a5_stock_OTHER_OBJECTIVE`, `sail_{stock,patched}` | 92K |
| `S1_gp4_replacement_2026-08-14/` | zero-compute gate-replacement analysis | `scripts/gp4_replacement.py`, `logs/gp4_replacement.out` | 48K |
| `S1_zerocompute_2026-08-14/` | zero-compute triage (D67/D68/D69/D70) | `scripts/s1_zerocompute.py`, `logs/s1_zerocompute.out` | 60K |

---

## 5. Top-level records with no case directory of their own

These are family-level `.md` files, not cases. Listed so the index is complete; verdicts
and rulings are summarised in `docs/dafoam/PRIOR_WORK_INVENTORY_PART_B.md` §1–§3.

- **Central status:** `DAFOAM_CASE_STATUS.md` (83K, the family's record of record),
  `PROOF.md` (222K, §15–§25 root-cause chain), `ADJOINT_MEMORY_ENVELOPE.md` (39K) +
  `.json` (12K).
- **Defect campaigns:** `DEFECT_ROBUSTNESS_mesh_and_setup.md` (66K),
  `DEFECT_REACH_decomposition_cases.md` (42K),
  `DISCRIMINATORS_A4_decomposition_mechanism.md` (19K),
  `DEFECT_CANDIDATE_ksp_options_override.md` (12K, FILING-READY / NOT FILED),
  `ROOTCAUSE_getRotationMatrix3d.md` (46K), `PATCH_getRotationMatrix3d.md` (15K),
  `GENERATOR_FINDING_pyhyp_aspect_ratio.md` (11K).
- **Unfiled upstream drafts:** `UPSTREAM_BUG_REPORT_decomposition_adjoint.md` (39K),
  `UPSTREAM_BUG_REPORT_mesh_warpDeriv.md` (49K). Both carry
  **"Status: NOT FILED ANYWHERE"** at line 3.
- **Verification sweeps (7):** `VERIFICATION_A1_serial_limiter_supervisor_sweep.md`,
  `VERIFICATION_A4_decomposition_supervisor_sweep.md`,
  `VERIFICATION_A4_mechanism_supervisor_sweep.md`,
  `VERIFICATION_cbfs_unblock_supervisor_sweep.md`,
  `VERIFICATION_defect_robustness_supervisor_sweep.md`,
  `VERIFICATION_reach_matrix_supervisor_sweep.md`,
  `VERIFICATION_rotation_patch_supervisor_sweep.md`.
- **Supervision / family:** `FAMILY_SUPERVISION_GUIDELINES.md` (20K),
  `SUPERVISOR_FAMILY_REVIEW_2026-08-07.md` (23K), `WARMSTART_AUDIT.md` (8.7K),
  `S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md` (39K),
  `S1_GP4_REPLACEMENT_2026-08-14.md` (18K),
  `S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` (45K), `A1_A5_A6_DIAGNOSIS.md` (50K).
- **Research / liaison:** `R5_ADJOINT_CONDITIONING.md` (25K),
  `LIAISON_RESEARCH_adjoint_conditioning.md` (18K),
  `LIAISON_NOVELTY_SWEEP_decomposition_defect.md` (24K),
  `DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` (13K).
- **A3 / W4 / W5 rung files (top level, belong to `ladder-a/A3` and the wells):**
  `A3_FD3_PREREGISTRATION.md`, `A3_KSPOPTS_PATCH_PREREGISTRATION.md`,
  `A3_NONNORMALITY_DIAGNOSTIC_PREREGISTRATION.md`,
  `A3_RUNG2_N28_{PREREGISTRATION,RESULT}.md`,
  `A3_RUNG3_{N52_PREREGISTRATION,N52_RESULT,FILL1_ENGINEERING_PREREGISTRATION,RESTART_CHALLENGE_PREREGISTRATION}.md`,
  `A3_SAAD_DELIBERATE_CONDITIONING_PREREGISTRATION.md`,
  `A3_STAGE2_UNREACHABLE_CLASS_PREREGISTRATION.md`,
  `A3_SUBLU_{PREREGISTRATION,RESULT,SWEEP_PREREGISTRATION}.md`,
  `A3_TPC1_{ARM,CONTROL}_PREREGISTRATION.md`, `A3_TRIAGE_LEVERS_PREREGISTRATION.md`,
  `A4_SIMPLEC_ACTIVITY_PROOF_PREREGISTRATION.md`,
  `D3_VARIANT_COLD_RERUN_PREREGISTRATION.md`, `W4_CARRY_TO_BLOCKED_RUNGS.md`,
  `W4_IDX16_IS_THE_REFERENCE.md`, `W5_COMMUNITY_REPORTS_TESTED.md`,
  `W5_GRADIENT_REGRADE.md`.

---

## 6. Loose top-level `*.log` files (78 files, 3.3 MB)

Attribution below is from each log's own content (cell counts, patch names, PROBE lines,
`Case :` headers), not from the filename. **Every attributable file belongs to Ladder A —
A1 (NACA0012) or A5 (U-bend). None belongs to Ladder B.** They are the raw evidence
behind `PROOF.md` §15–§24 and `A1_A5_A6_DIAGNOSIS.md`. Convention placement would be
`cases/dafoam/ladder-a/A1/logs/` and `.../A5/logs/`.

| group | files (count) | size | belongs to | basis for attribution |
|---|---|---|---|---|
| `a5_dobjdxv_np1_run1`, `a5_dobjdxv_reset_np1_run1`, `a5_noisefloor_np1_run1`, `a5_realseed_np4_run1` (4) | 504K | **A5** U-bend | `ubend` / `UBend_Channel` strings in-log |
| `probewarpderiv_a5_idx{2,8,17,26}_seed{42,2026}_np{1,4}_run1` (7) | 136K | **A5** U-bend | same |
| `probewarpderiv_idx{4,6,7}_np{1,4}_seed{42,2026}_h1e-{4,5}_run1` (10), `probewarpderiv_realseed_idx4_idx6_idx7_np4_run1` (1) | 220K | **A1** NACA0012 coarse | 4 ranks × 1008 cells = 4,032 cells in-log |
| `stepstudy_run1`, `stepstudy2_run1` (2) | 476K | **A1** coarse | `NACA0012_Airfoil_Incompressible` in-log |
| `stepstudy_refined_run1`, `checkall8refined_run{1,2}` (3) | 532K | **A1 refined** (14,720 cells) | `NACA0012_Airfoil_Incompressible_refined` in-log |
| `check_totals_run1`, `compute_totals_run1` (2) | 200K | **A1** coarse | same |
| `diagnose_run1`, `diagnose_chain_run1`, `diagnose_chain2_run1`, `diagnose_frozen_run1`, `diagnose_frozen_serial_run1`, `diagnose_partials_run1`, `diagnose_warp_run1`, `diagnose_warp_exact_run1` (8) | 176K | **A1** coarse | same |
| `handcomp_idx{0,1,4}_run1` (3) | 72K | **A1** coarse | same (PROOF §21 hand-composition) |
| `probedcddxv_idx{0,1}_h{1e-4,5e-5}_run1`, `probedcddxv_idx4_h1e-4_run1` (5) | 144K | **A1** coarse | same (PROOF §20) |
| `probewallbranch_*` (11: `baseline`, `baseline_idx01`, `idx{0,1,4,6}_{plus,minus}`) | 288K | **A1** coarse | in-log `PROBE tag=baseline … CD=2.091051001294601e-02 CL=4.987652641220148e-01 bcType=nutUSpaldingWallFunction nWingFaces=126` — the `wing` patch of the naca0012 case |
| `probemeshquality_{baseline,idx4_plus,idx4_minus,idx6_plus,idx6_minus}_run1` (5) | 140K | **A1** coarse | in-log `Max aspect ratio = 97.87218721638284`, the coarse-mesh value of `GENERATOR_FINDING_pyhyp_aspect_ratio.md` |
| `probemeshmetricrefinement_run1` (1) | 4.0K | **A1 coarse vs refined** | its own first line: "A1 coarse (4032 cells) vs refined (14720 cells)" |
| `probe_baseline_run1`, `probe_baseline_pcheck_run1`, `probe_idx{0,1,4,6}_{1e-4,neg1e-4}_run1`, `probe_idx0_LARGE_run1`, `probe_idx0_LARGE_pcheck_run1` (12) | 428K | **A1** coarse (probably; `idx0..idx6` FFD set matches A1's 8 shape DVs) — in-log cell count reads 3,648/3,712, which is **not** 4,032, so the exact mesh variant is **NOT SETTLED** | `cells: 3648` / `3712` lines; container mounts the case at `/home/dafoamuser/mount`, so the host path is not recoverable from the log |
| `run_all_probes.log` (1) | 576 B | driver for the `probe_*` set above | its own body lists `idx0_neg1e-4`, `idx1_1e-4`, … |
| `preproc_stdout.log`, `preproc_refined_stdout.log` (2) | 84 B | **A1** coarse / refined mesh generation | body is `Generating mesh.. Done!` only |
| `pull.log` (1) | 311 B | **toolchain, not a case** | `docker pull dafoam/opt-packages`, digest `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` — the same digest `upstream_repro/README.md` pins |
| `pcheck_wrapper.log` (1) | **0 bytes** | **UNATTRIBUTED** — empty file, no content to attribute | — |

---

## 7. Where NEW work goes — proposed directory names (supervisor confirms)

Proposal: adopt the closure team's file-pair convention (`PREREGISTRATION.md` +
`RESULTS.md` inside a per-case directory) for **new** cases only, keeping the existing
ladder-a/ladder-b roots so no citation breaks.

| new work | proposed path | pair files |
|---|---|---|
| Ladder A rungs not yet run, or re-runs | `cases/dafoam/ladder-a/A4/`, `.../A6/` (etc., one dir per rung) | `PREREGISTRATION.md`, `RESULTS.md`, `config.json`, `logs/`, `work/` |
| A3 well continuations | `cases/dafoam/ladder-a/A3/<arm>/` e.g. `A3/rung4_n80/` | same |
| Ladder B — B3 Stage 4 (the field inversion that never ran) | `cases/dafoam/ladder-b/B3_stage4/` | same |
| S1 CBFS follow-ons | `cases/dafoam/ladder-b/S1-cbfs-w1-only-arm/`, `.../S1-cbfs-continuation-arm/`, `.../S1-priors/` | same (the last one's prereg already exists as `S1_PRIORS_PREREGISTRATION.md` and should be **moved only with the supervisor's word**, since `S1_GP4_REPLACEMENT_2026-08-14.md` §5 cites it by name) |
| The destruction-term model patch (`w3-beta-on-omega-destruction-model-patch`) | `cases/dafoam/ladder-b/w3-destruction-term/` | same, plus `patches/` |
| Hump adjoint characterisation (W4 §5b.1 items M1–M6) | `cases/dafoam/ladder-b/hump-adjoint-characterisation/` | same |
| New toolchain patches | `cases/dafoam/patches/<name>/` (mirroring the existing `subpclu_patch`/`kspopts_patch`) | `README.md` + `.patch` |
| New upstream reproducers | `cases/dafoam/upstream_repro/<name>/` | `README.md` + driver |
| Family entry point | `docs/dafoam/README.md` (to be written, mirroring `docs/closure/README.md`) | — |

**Two things this index deliberately does not do:** it does not propose moving any
existing directory, and it does not rename any file. Both are supervisor calls, and the
family's own §7 hygiene rule makes a half-applied rename worse than none.

---

## Addendum 2026-08-22 (supervisor) — directories created today, confirmed under the `<RUNG>/<run-slug>/` pair-file form

| new directory | pair files | run tree (outside the repo) |
|---|---|---|
| `ladder-a/A3/rung2_patched_idwarp_np4/` | `PREREGISTRATION.md` (+ pre-compute Amendment 1 → np=1 twins) | `/home/ubuntu/certonomous-runs/P3-a3-rung2-patched/` |
| `ladder-a/A6/rung_n16_fixed_reference/` | `PREREGISTRATION.md` | `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/` |
| `ladder-a/A4/shipped_optimisation_np1/` | `PREREGISTRATION.md`, `RESULTS.md` | `/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/` |
| `ladder-a/A2/per_component_table/` | `RESULTS.md` (zero compute, no prereg) | `/home/ubuntu/certonomous-runs/P3-a2-percomponent/` |

---

## Addendum 2026-08-31 (dafoam lane) — the SO-series backfill: 12 directories that existed on disk and had NO index row

**Why this addendum exists.** `docs/dafoam/GRADING_CHAIN.md` bullet 9 is a finding, not a
formatting note: *"Nothing links a graded verdict to `docs/dafoam/README.md` §3 or to
`cases/dafoam/INDEX.md` … `INDEX.md` was last touched 2026-08-22 and carries **zero** entries for
SO-2M, SO-3a or SO-3aR — the whole SO-series is unindexed."* This addendum closes that gap for the
SO series by hand, which is exactly the point bullet 9 makes: **this hop is a person reading a
page, and nothing automates it.**

**Nothing above this line was edited.** No existing row, table, column or section was altered, moved
or renamed; the 2026-08-22 addendum's three columns are reproduced here unchanged and in order, with
two columns appended that apply to this addendum's rows only. **No frozen `PREREGISTRATION.md` or
`RESULTS.md` was touched by this backfill, and zero compute was spent.**

**The verdict column is a citation, never a summary.** Every verdict is the word the artefact
carries, read from that artefact; where an item has no verdict this table says so rather than
supplying one. **Where an item's ORIGINAL grader refused and a SUCCESSOR later produced a verdict,
both are stated** — the family's convention (`curriculum_SO1a/RESULTS.md` §1,
`curriculum_AV1R/RESULTS.md` §1) is that the original is struck as superseded *for the run* and is
NOT struck as a fact about the item's own frozen path.

**The CAUSE CLASS column** is Sanaa's GRADING TRANSPARENCY ORDER of 2026-08-31
(`etc/sessions/2026-08-31T2055Z_sanaa_grading_transparency_order.md`, committed `4116024a`): every
non-`PASS` verdict carries one of exactly eight classes, **assigned by the grading record and cited
like any claim**. A `PASS` carries none. Only `PHYSICS-FAIL` and `MODEL-LIMIT` say anything about the
lab's ability to do physics. Classes already fixed by `docs/dafoam/GRADING_CHAIN.md` are **carried
from it, not re-derived**; the one class this table assigns that GRADING_CHAIN does not carry
(SO-1b) is marked `[NEW]` and is the supervisor's to ratify, since that page is theirs.

| new directory | pair files | run tree (outside the repo) | verdict of record, with the artefact it is read from | CAUSE CLASS |
|---|---|---|---|---|
| `ladder-a/A1/curriculum_SO1a/` | `PREREGISTRATION.md`, `RESULTS.md` | `/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/` | ORIGINAL ~~`NOT A RESULT`~~ (struck as superseded for the run), G1 refusal on the bare substring `Floating point exception` in `checkMesh.log` — `SO1a_grade_20260828T023132Z.json` → `verdict`, `refusal`. CURRENT **`GATE FAIL`** by successor SO-1aR, SHIPPED `GATE FAIL` / PATCHED `PASS` — `curriculum_SO1a/RESULTS.md` §1 | **PHYSICS-FAIL — against the SHIPPED TOOLCHAIN** (`GRADING_CHAIN.md`, row "SO-1aR shipped row") |
| `ladder-a/A1/curriculum_SO1aR/` | `PREREGISTRATION.md`, `RESULTS.md` | re-grade of SO-1a's preserved root — same tree, no root of its own | **`GATE FAIL`**, rows `{"SHIPPED": "GATE FAIL", "PATCHED": "PASS"}` — `.../CURRICULUM-SO1a-.../SO1aR_grade_20260828T171830Z.json` → `verdict`, `rows`; `curriculum_SO1aR/RESULTS.md` §3. Worst component `shape[6]` **637.7570 %** with a sign flip | **PHYSICS-FAIL — against the SHIPPED TOOLCHAIN** (`GRADING_CHAIN.md`, same row) |
| `ladder-a/A1/curriculum_SO1b/` | `PREREGISTRATION.md`; **no `RESULTS.md`** | **none — nothing was ever launched** | **`BLOCKED`** on this item's OWN registered no-launch branch (`PREREGISTRATION.md` §1a), **zero core-minutes spent**. Verbatim from `curriculum_SO1b/G_SO1A.20260828T023149Z.txt` and `LAUNCH.SO1b_chain_wait.20260828T021949Z_1712764.out` (both in-git, in the case directory): *"ABORT G-SO1A the SO-1a PATCHED row is not PASS on BOTH G5 (dCD/dx) and G5c (dCL/dx) … the SO-1b item verdict is BLOCKED"*, `reading: REFUSE no_gates.G5_PATCHED in=SO1a_grade_20260828T023132Z.json` | **INSTRUMENT** `[NEW]` — the gate read a REFUSAL, not a failing gradient: SO-1a's grader had evaluated **zero** gates on a false positive (`so1a_grade.py:122-125` bare substring, `:420` appending `checkMesh.log`, whose line 18 is OpenFOAM's `trapFpe:` **enablement banner** — `docs/COST_CALIBRATION.md` C-205). The successor pair settles it: SO-1aR's PATCHED row is `PASS` and SO-1bR then ran to `PASS`. Physics was never what stopped this item |
| `ladder-a/A1/curriculum_SO1bR/` | `PREREGISTRATION.md`; **⚠ no `RESULTS.md` — SEE THE FLAG BELOW** | `/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt/` | **`PASS`**, rows `{"SHIPPED": "PASS", "PATCHED": "PASS"}` — `SO1bR_grade_20260831T160245Z.json` → `verdict`, `grade.rows`, `refusal: null`. The same artefact's `verdict_line` carries the qualification and it travels with the `PASS`: *"RESTS ON THE PATCHED ROW OF CURRICULUM-SO1aR, WHOSE ITEM VERDICT IS GATE FAIL AND WHOSE SHIPPED ROW IS GATE FAIL … THE SHIPPED TOOLCHAIN FAILED THE GRADIENT THIS RESULT RESTS ON"* | — (`PASS` carries no class) |
| `ladder-a/A1/curriculum_SO1c/` | `PREREGISTRATION.md`; no `RESULTS.md` | `/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv/` | **`NOT A RESULT`** — `SO1c_grade_20260831T171139Z.json` → `verdict`, `refusal`: `{"REFUSE": "G1", "detail": {"arm_absent_from_ledger": "Ns-P", …}}` | **INSTRUMENT** (`GRADING_CHAIN.md`, row SO-1c: *"Row-label break in call sites the R8 repair never swept"* — the break is why the arm is absent from the ledger under the label the grader looks for) |
| `ladder-a/A1/curriculum_SO1cR/` | `PREREGISTRATION.md`; no `RESULTS.md` | `/home/ubuntu/certonomous-runs/CURRICULUM-SO1cR-a1-naca0012-dragmin-npinv/` | **`PASS`**, rows `{"SHIPPED": "PASS", "PATCHED": "PASS"}` — `SO1cR_grade_20260831T175758Z.json` → `verdict`, `rows`. Its trivial baseline is one of this family's two live controls: it failed **5 of 5** components with two sign flips (`GRADING_CHAIN.md` bullet 6) | — (`PASS` carries no class) |
| `ladder-a/A1/curriculum_SO2M/` | `PREREGISTRATION.md`; no `RESULTS.md` | `/home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient/` | **`NOT A RESULT`** — `SO2M_grade_20260831T195531Z.json` → `verdict`, `refusal`: `{"REFUSE": "CONTROL", "detail": {"G5m_did_NOT_flip_to_GATE_FAIL_under_the_planted_copy": {…"plant": 0.001234, "flipped": false, "live_verdict": "PASS"…}}}`. **Every arm `rc=0` and the physics is clean; the comparator refused rather than degrade** | **GATE-DESIGN** (`GRADING_CHAIN.md`, row SO-2M: the **registered plant** was too small to cross its own band — `1.234e-03` is 2.48 % of `CMZ`'s reference against a 5 % band D. The comparator was correct; the gate as registered was defective) |
| `ladder-a/A1/curriculum_SO2MR/` | **none — scripts only; NO `PREREGISTRATION.md` and NOT TRACKED at HEAD** (`git ls-files` returns nothing) | none | **no verdict, and none is claimed.** Nothing is registered and nothing has run. Listed only so the census is complete and so no reader mistakes the directory for a case; **it is a peer's live, unfinished work and this addendum did not touch it** | — (no verdict exists) |
| `ladder-a/A1/curriculum_SO2a/` | `PREREGISTRATION.md`; no `RESULTS.md` | `/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient/` | **`PASS`**, rows `{"SHIPPED": "PASS", "PATCHED": "PASS"}` — `SO2a_grade_20260831T002529Z.json` → `verdict`, `rows` | — (`PASS` carries no class) |
| `ladder-a/A1/curriculum_SO3a/` | `PREREGISTRATION.md`; no `RESULTS.md` | `/home/ubuntu/certonomous-runs/CURRICULUM-SO3a-a1-naca0012-alpha-multipoint-gradient/` | **`NOT A RESULT`** — `SO3a_grade_20260831T184321Z.out` (**there is no `.json` for this item; the `.out` is the only grade artefact on disk**), last two lines: *"NOT A RESULT -- the comparator REFUSED"* then `{"REFUSE": "G1", "detail": {"C3_artefact_absent": ".../X-S/so3a_X.json", "arm": "X-S"}}` | **INSTRUMENT** (`GRADING_CHAIN.md`, row SO-3a: unfilled fail-closed producer pin, `so3a_xf.py:111`; the extractor refused before any physics was read) |
| `ladder-a/A1/curriculum_SO3aR/` | `PREREGISTRATION.md`, `RESULTS.md` | `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/` | **`NOT A RESULT`** — `curriculum_SO3aR/RESULTS.md` §1, on two independent grounds on disk; grade artefact `SO3aR_grade_20260831T202215Z.out` (**`.out` only, no `.json`**): `{"REFUSE": "G1", "detail": {"C3_artefact_absent": ".../X-S/so3ar_X.json", "arm": "X-S"}}`. **The stop marker's `"verdict": "PENDING"` is NOT the item verdict** and that record says so in the same breath, quoting its own `"verdict_source": "NO READABLE COMPARATOR VERDICT AT THIS ADDRESS"` | **NAMING/PLUMBING** (`GRADING_CHAIN.md`, row SO-3aR: one shared run directory, three scenarios, no per-point `run_directory`, all renaming to `0.0001`) |
| `ladder-a/A1/feasibility_SO3a_alpha/` (SO-3aF) | `FEASIBILITY_NOTE.md`, `COST_ROW_OWED.md` — **deliberately not a pre-registration** | `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility/` | **No verdict, and none is possible.** The note's own opening line: *"THIS IS NOT A PRE-REGISTRATION AND ITS OUTPUTS ARE NEVER GRADEABLE AS VERDICTS."* It files with `prereg_commit = "FEASIBILITY"` under Sanaa's ruling of 2026-08-31 (`etc/sessions/2026-08-31T1513Z_sanaa_freeze_clock_and_so3_ruling.md:5`), encoded lab-wide at `scripts/queue_entry_check.py:114`. **Writing `PENDING` or `NOT A RESULT` here would be a category error**, so neither is written | — (not gradeable by construction) |

### ⚠ TWO GAPS THIS BACKFILL FOUND AND DID NOT PAPER OVER

**1. SO-1bR's verdict of record exists ONLY outside git.** `SO1bR_grade_20260831T160245Z.json`
carries `PASS` on both rows in the preserved run root, and **no `RESULTS.md` exists for the item —
neither on disk nor at HEAD.** The row above is written from the grade artefact, which is the
authority; **no `RESULTS.md` was manufactured for it**, because writing a first results record for an
item this lane did not grade is a supervisor's call and not a lane's (the precedent is
`curriculum_AVWC/RESULTS.md` §10, which refused the same step for AV-1R and was later executed on the
supervisor's own instruction). This is `GRADING_CHAIN.md` bullet 8 in the live: **between the
comparator writing a verdict and a `RESULTS.md` landing, the verdict of record exists only on disk,
outside version control.** SO-1c, SO-1cR, SO-2M, SO-2a and SO-3a are in the same state — a graded
verdict and no in-git record — and are listed here so the count is known: **six items, one addendum
row each, zero `RESULTS.md` between them.**

**2. SO-3a and SO-3aR have `.out` grade artefacts and NO `.json`.** Every other SO item in this
table has both. The `.out` carries the refusal string verbatim and is cited above as the artefact of
record; a reader who expects the machine-readable payload will not find one, and that absence is
stated rather than left to be discovered.

**What this addendum does not do.** It moves no gate, band, threshold, cap or label; it re-grades
nothing; it adds no number that was not already written in a cited artefact; it does not edit
`docs/dafoam/GRADING_CHAIN.md` (that page is the supervisor's), `docs/dafoam/README.md` §3, or any
frozen document. **Zero solver core-minutes.**

---

## Addendum 2026-08-31 (dafoam lane, later the same day) — ONE ROW ABOVE HAS BEEN OVERTAKEN BY EVENTS: SO-2MR IS NOW A FROZEN ITEM

**Nothing above this line was edited.** The SO-2MR row in the addendum above is left standing
**exactly as written**, because it was a true reading of the disk when it was taken — the directory
then held scripts only, carried no `PREREGISTRATION.md`, and `git ls-files` on it returned nothing.
This note supersedes that row rather than rewriting it, which is this file's own convention.

| item | what changed | the reading now |
|---|---|---|
| `ladder-a/A1/curriculum_SO2MR/` | **FROZEN and TRACKED**, commit `c0eff9ca9330dd310fcfbe7a77f13e2ec1ec8cca` | pair files: `PREREGISTRATION.md` (Stages 1 **and** 2 in one freeze) + `QUEUE_ENTRY_DRAFT.json`; **no `RESULTS.md`, because nothing has run.** Run tree: **none — the run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO2MR-a1-naca0012-moment-gradient` is ABSENT**, read at 2026-08-31T22:15:13Z beside a known positive on SO-2M's existing root. **Verdict: none, and none is claimed** — zero containers, zero core-minutes, no queue entry filed. Arming is the supervisor's check-4 decision, not a lane's |

**Why the successor exists, in one line, since the table above records SO-2M's cause class as
GATE-DESIGN and stops there:** SO-2M's registered direction-B plant was a **bare absolute**
`1.234e-03`, which is **2.479781 %** of `CMZ`'s reference `|d_ref| = 0.049762462207060022` against a
5.0 % band — it could not cross, so the comparator refused rather than report a `PASS` from a gate it
had not shown able to `GATE FAIL`. SO-2MR registers the plant as a **rule relative to the quantity it
perturbs**, `P = K · (band_D/100) · |d_ref|` with **`K = 2.0` fixed at freeze**, which crosses the
band by construction with 100 % margin at any functional scale. **No gate, threshold, band, cap or
label moved with it**, and SO-2M's `NOT A RESULT` stands unaltered.

**QUEUE ENTRIES, since this index has never carried them and the SO series is the family's densest
user of them.** Every path below was confirmed present on disk when this note was written:
`verification/queue/dafoam/launched/` holds `SO1a_chain.json`, `SO1b_chain_wait.json`, `SO1bR.json`,
`SO1bR_r2.json`, `SO1c_chain.json`, `SO1cR_chain_wait.json`, **`SO2M_chain.json`** (`prereg_commit`
`f1a723ac3a0d8da5c9e54ab7a0a80127ab366f26`, `cost_core_min_estimate` 11.0, `cap_core_min_registered`
79.0), `SO2a_chain.json` and `SO2a_chain.2026-08-30T231326Z.json`; `verification/queue/dafoam/refused/`
holds `SO3AF.json` with its `SO3AF.REFUSED.txt`. **There is no queue entry for SO-3a, SO-3aR or
SO-2MR, and none is invented here** — SO-2MR's is a `QUEUE_ENTRY_DRAFT.json` sitting in its case
directory, deliberately **not filed**.

**This note moves no gate, re-grades nothing, and spent zero solver core-minutes.**

---

## Addendum 2026-09-01 (dafoam lane) — `curriculum_D19M` is indexed, and the rest of the D19 family is named as still missing

**Nothing above this line was edited.** No existing row, table, column or section was altered, moved or renamed. **No frozen `PREREGISTRATION.md` was touched and zero compute was spent** — every figure below is read from an artefact already on disk.

**This addendum indexes ONE item**, the one this lane was dispatched to land. The verdict column is a **citation, never a summary**.

| new directory | pair files | run tree (outside the repo) | verdict of record, with the artefact it is read from | CAUSE CLASS |
|---|---|---|---|---|
| `ladder-a/A1/curriculum_D19M/` | `PREREGISTRATION.md` (frozen `c7d7bf10`, through Amendment 3), `RESULTS.md`, `QUEUE_ENTRY_DRAFT.json` | `/home/ubuntu/certonomous-runs/CURRICULUM-D19M-a1-naca0012-subsonic-multipoint/` | **`GATE REACHED`**, rows `{"SHIPPED": "GATE REACHED", "PATCHED": "GATE REACHED"}`, both `verdict_before_ceiling: "PASS"` and `capped_by_ceiling: true` — `D19M_grade_20260901T083034Z.json` → `verdict`, `rows`, `rows_capped_by_ceiling`. Chain `COMPLETE`, `chain_rc=0`, `declared=7 executed=7`. **35.166 core-min**, \$0.030067 **derived, not measured** | **CEILING** — the item was **capped, not failed**: every gate returned `PASS`, and the registered `VERDICT_CEILING` binds because the compressible gradient it spends has **no graded verdict** and D19R's plateau never closed. **Nothing in this item is a `GATE FAIL`, and no `PHYSICS-FAIL` or `MODEL-LIMIT` class applies** |

**A NOTE ON THE `capped_by_ceiling` FIELD, because this row would otherwise be checkable against the wrong one.** The grade artefact's **top-level** `capped_by_ceiling` reads `false` while both **rows** read `true`. Both are literally true — the ceiling binds at row level and the item inherits, so item-level capping had nothing left to do. **The fields to quote are `capped_by_ceiling_anywhere: true` and `rows_capped_by_ceiling: ["SHIPPED", "PATCHED"]`**, and `curriculum_D19M/RESULTS.md` §7.1 states why.

### ⚠ THE GAP THIS ADDENDUM DOES NOT CLOSE

**Four other `curriculum_D19*` directories exist on disk and still have NO index row**: `curriculum_D19`, `curriculum_D19R`, `curriculum_D19R2` and `curriculum_D19O`. Three carry run trees (`CURRICULUM-D19-a1-naca0012-subsonic-opt`, `CURRICULUM-D19R-a1-naca0012-subsonic-plateau`, `CURRICULUM-D19O-a1-naca0012-subsonic-optimisation`). **No verdict is stated here for any of them** — this lane's brief covered D19M only, and writing an index row for an item it did not read the artefacts of is exactly the step the 2026-08-31 backfill refused for SO-1bR. **They are named so the count is known: four items, zero index rows.**

**`docs/dafoam/README.md` §3 carried no D19-family row of any kind before today.** This lane added D19M's two rows there; **D19, D19R, D19R2 and D19O remain absent from §3**, and that is `docs/dafoam/GRADING_CHAIN.md` bullet 9 in the live again — *nothing links a graded verdict to `README.md` §3 or to this file*, and the hop is still a person reading a page.

**This note moves no gate, band, threshold, cap or label; it re-grades nothing; it adds no number that is not already written in a cited artefact; and it spent zero solver core-minutes.**

---

## Addendum 2026-09-01 (dafoam lane, later the same day) — THE GAP THE ADDENDUM ABOVE OPENED IS CLOSED: `D19`, `D19R`, `D19R2` AND `D19O` ARE INDEXED, AND **TWO OF THE FOUR CARRY NO VERDICT AT ALL**

**Nothing above this line was edited.** No existing row, table, column, heading or section was
altered, moved or renamed — the addendum above stands exactly as written, including its ⚠ gap
notice, which this addendum answers rather than rewrites (this file's own convention, established by
the SO-2MR note of 2026-08-31). **No frozen `PREREGISTRATION.md`, no `RESULTS.md`, no grader and no
`docs/capability/dafoam_GRID.md` was touched, and ZERO compute was spent** — every figure below is
read from an artefact already on disk.

**The verdict column is a citation, never a summary, and it is not a promotion.** Two of these four
items have **no verdict of record**: their graders refused with `rc = 2` before composing anything,
and **a refusal is not a verdict**. No row here supplies one, softens one, or writes `PENDING` over
one — `PENDING` means *not yet run*, and these items ran. The columns are the 2026-08-31 backfill's
five, in its order.

**CAUSE CLASS** is Sanaa's GRADING TRANSPARENCY ORDER of 2026-08-31
(`etc/sessions/2026-08-31T2055Z_sanaa_grading_transparency_order.md`, committed `4116024a`): one of
exactly eight, assigned by the grading record and cited like any claim. `docs/dafoam/GRADING_CHAIN.md`
carries **no D19-family row at all** — `grep D19` on it returns nothing — so nothing could be carried
from it and every class below is marked `[NEW]` for the supervisor to ratify, except D19's, which its
successor's frozen pre-registration assigns in terms.

| new directory | pair files | run tree (outside the repo) | verdict of record, with the artefact it is read from | CAUSE CLASS |
|---|---|---|---|---|
| `ladder-a/A1/curriculum_D19/` | `PREREGISTRATION.md` (frozen `f032d94e`), `D15_D16_FD_STEP_TABLE.md`, phase-1 instruments (`32bd000f`); **no `RESULTS.md` — none exists on disk or at HEAD** | `/home/ubuntu/certonomous-runs/CURRICULUM-D19-a1-naca0012-subsonic-opt/` (four arms `MESH X2 S2 S1`, all `PATCHED`, all `rc=0`, `chain_rc=0`) | **NO VERDICT OF RECORD, and none is claimed.** The grader **REFUSED, `rc = 2`**, before reading a single gate: `D19_phase1_grade_20260831T215400Z.out` → `{"REFUSE": "G1", "detail": {"age_datum_moved": ".../S1/0", "recorded": 1788213189, "rederived_by_existence": 1788213232}}`. **No grade JSON was written**, though `STATUS.D19_chain` names one (`grader_rc=2 … note=comparator-exit-status-NOT-the-verdict`). The item's own landed record is `docs/COST_CALIBRATION.md` row `C-20260831T223116.831784Z-f2a2dd3d`, whose words are *"this 8.683 core-min bought NO graded verdict … the item carries no verdict and that is the honest label"* — **8.683 core-min against 8.7 registered, ratio 0.998**. Phase 2 correctly never launched. The selector *did* run and its reading is a measurement, not a verdict: `s*` level 2 (shape 1e-3 / patchV 1e-2), `s_star_score_pct` **21.629866013797557**, binding `shape[7]/CD/fine`, `all_two_sided_at_s_star` **false** | **INSTRUMENT** — assigned by `curriculum_D19R/PREREGISTRATION.md` §2.1–§2.2: *"the guard refused rather than degrading, which is correct behaviour; it was enforcing a premise that does not hold for this solver family"* (rule 4's *"`0/T` is touched last at launch"* is false for DAFoam, whose `patchV` DV rewrites `0/U` mid-run). Physics unjudged; nothing here is a `PHYSICS-FAIL` |
| `ladder-a/A1/curriculum_D19R/` | `PREREGISTRATION.md` (frozen `5a809989`, instruments driven and frozen at `7f9c5b6e`, Amendment 1 appended); **no `RESULTS.md` — none exists on disk or at HEAD**; **no `docs/COST_CALIBRATION.md` row** | `/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau/` (six arms `MESH X2 S8 N2 S1 R1`, all `PATCHED`, all `rc=0`, `chain_rc=0`, `G9` OK on every arm) | **NO VERDICT OF RECORD, and none is claimed. This is neither a `GATE FAIL` nor a `PASS`.** The grader **REFUSED, `rc = 2`**: `D19R_phase1_grade_20260831T230742Z.out` → `{"REFUSE": "G-PROV", "detail": {"verdict_outside_the_fixed_vocabulary": null}}`. **`D19R-GRADER-DEF-1`**: `d19r_grade.py:482` calls the provenance enforcer as the **first statement of `grade()`** on a literal `{}`, thirty lines before composition at `:511-524`, so `verdict` is `None`, `None` is not in the vocabulary, and it refuses — **as coded the instrument cannot emit a verdict on any input.** The verdict of record is `docs/LAB_STATE.md` update **S-23 §2**, whose own table cell reads *"no verdict — grader REFUSED, `rc=2`"* beside *"12.416 core-min vs 13.6 predicted, ratio 0.913×, every arm inside cap"* (the six ledger `core_min` rows sum to 12.416: 0.183 + 1.333 + 6.067 + 1.9 + 2.25 + 0.683). **The plateau never closed** — `d19r_selected_step.json`: `all_two_sided` **false**, `s*` level 3, `score_pct` **21.060684242435336**, binding `shape[7]/CD/fine` — and that unclosed plateau is one half of the registered ceiling holding **both** D19O and D19M below `PASS` | **INSTRUMENT** `[NEW]` — a comparator/reader/guard defect with the physics unjudged. The boarded record words it *"INFRASTRUCTURE, not physics — bookkeeping never voids physics"* (`LAB_STATE.md` S-23 §2); `INFRASTRUCTURE` is **not one of Sanaa's eight**, and `INSTRUMENT` is the eight-class token for exactly this, so the mapping is stated rather than assumed and is the supervisor's to ratify. **The arms are clean and re-gradable the moment the call site is repaired** |
| `ladder-a/A1/curriculum_D19R2/` | `PREREGISTRATION.md` (frozen `7441f392`), `RESULTS.md`, `d19r2_grade.py` | **none of its own — it re-grades D19R's preserved arms**, and its artefact sits in D19R's root: `D19R2_phase1_grade_20260901T034416Z.out` | **`NOT A RESULT`** — grading **attempt 1**, and **no later attempt exists**, on disk or at HEAD (one D19R2 grade artefact anywhere under `/home/ubuntu/certonomous-runs/`, one commit pair `7441f392`/`944e40a8`, no `D19R3` directory). `curriculum_D19R2/RESULTS.md` §1, verbatim: *"Verdict of the attempt: `NOT A RESULT`. The grader **refused**, `rc = 2`, and wrote **no grade JSON**."* → `{"REFUSE": "G19R-1h", "detail": {"age_guard": {"REFUSE": "MANIFEST_ENTRY_MUTATED", "path": "system/decomposeParDict", "on_disk_md5": "c3f5f05d…", "recorded_md5": "68ecc827…"}}, "arm": "X2"}`. **The two provenance blockers ARE repaired and the repair held** — execution reached the completion gate, thirty lines past where D19R died. **0.00096 core-min** (0.058 s × 1 rank) against a 2.0 ceiling; **ZERO solver core-min** — D19R's 12.416 stays charged to D19R. Its §7 states a `COST_CALIBRATION` row is **owed at item completion and this item is not complete**, so none was filed and none is invented here | **GATE-DESIGN** `[NEW]` — the record's own §5.1 words, *"This is a gate-design question"*. Measured, not inferred: OpenFOAM appends its own `kahipCoeffs` default block to that dictionary **six seconds after** the manifest is built, in **exactly the three np=2 arms**; **151 of 152 manifest entries across six arms are byte-identical** after five days. The comparator was correct; the gate as registered pins a path the run writes, and narrowing it would move a registered goalpost. **Route 1 is reserved to Sanaa** — `D19R` §5 reserves gate design to her in terms |
| `ladder-a/A1/curriculum_D19O/` | `PREREGISTRATION.md` (frozen `bb0c5b08`, Amendment 1; arming `239fd2ef`), `RESULTS.md` (incl. a dated §9), `QUEUE_ENTRY_DRAFT.json` — **plus four untracked `*.selftest.out` files left deliberately in the case directory, see the flag below** | `/home/ubuntu/certonomous-runs/CURRICULUM-D19O-a1-naca0012-subsonic-optimisation/` (seven arms of seven, `chain_rc=0`) | **`GATE REACHED`**, rows `{"SHIPPED": "GATE REACHED", "PATCHED": "GATE REACHED"}`, both `verdict_before_ceiling: "PASS"`, `capped_by_ceiling_anywhere: true`, `rows_capped_by_ceiling: ["SHIPPED", "PATCHED"]` — `D19O_grade_20260901T054304Z.json` → `verdict`, `rows`; `curriculum_D19O/RESULTS.md` §1. **16.184 core-min against 24.10 predicted (ratio 0.6715), \$0.013837 DERIVED, NOT MEASURED.** The item's own §6 states what it does **not** establish, first line first: *"It does not establish that the compressible adjoint is verified"* | **REFERENT-CEILING** `[NEW]` — the item was **capped, not failed**: every gate returned `PASS` and the registered ceiling binds because the compressible gradient it spends has **no graded verdict** (the two rows above) and D19R's plateau never closed. **Nothing in this item is a `GATE FAIL`, and no `PHYSICS-FAIL` or `MODEL-LIMIT` class applies.** The same situation is worded `CEILING` in the D19M row of the addendum above; that row is left exactly as it stands and this one names the eight-class token instead |

### ⚠ FOUR THINGS THIS BACKFILL FOUND AND DID NOT PAPER OVER

**1. TWO items have no verdict, not one.** The brief that dispatched this lane named `D19R`'s `rc=2`
refusal and left `D19`'s state open. **`D19` refused too** — at `G1`, on `age_datum_moved`, `rc=2`,
with no grade JSON — so **two of the five D19-family items have never had a verdict composed at all**,
and the family's graded count is three (D19R2 `NOT A RESULT`, D19O `GATE REACHED`, D19M
`GATE REACHED`), not four.

**2. `D19` and `D19R` have grade artefacts as `.out` ONLY, and their own `STATUS` files name a
`.json` that does not exist.** Both chain drivers wrote
`grader_rc=2 … out=<ITEM>_phase1_grade_<stamp>.json note=comparator-exit-status-NOT-the-verdict`
while the refusal precedes the emit, so **the named JSON was never created.** A reader who trusts the
`STATUS` line and goes looking for the payload will not find one. This is the same shape as SO-3a and
SO-3aR in the addendum above, arriving by a different route.

**3. The whole D19 family has ZERO filed queue entries.** `find verification/queue/dafoam -name
"*D19*"` returns nothing, in `launched/`, `refused/` or the root — while `D15_chain.json`,
`D16_chain.json`, `D17_chain.json` and `D18_chain.json` are all filed. D19O and D19M each carry a
`QUEUE_ENTRY_DRAFT.json` in their case directory, **deliberately not filed** (`CLAUDE.md` rule 7);
D19, D19R and D19R2 have neither entry nor draft. **Stated so the count is known; nothing is filed
here.**

**4. `D19O` left four untracked `*.selftest.out` files in the shared working tree, and they are
deliberately NOT swept.** `D19O-DRIVER-DEF-1` (`curriculum_D19O/RESULTS.md` §8):
`d19o_chain_driver.sh` writes its pre-launch selftest output to `$HERE` — the git case directory —
instead of the run root. The item's own record refuses to repair it (the driver is pinned and the
item has had first compute) and refuses to delete the files, because **they are the only on-disk
evidence that the four suites were driven before staging.** **This lane deleted nothing, and an
unexpected file is inspected, never reverted.** The repair landed in D19M's driver and is confirmed
in production there.

### WHAT THIS ADDENDUM DOES NOT DO

It moves no gate, band, threshold, cap or label; it re-grades nothing; it runs nothing; it adds no
number that is not already written in a cited artefact; it edits no frozen document, no grader and no
`RESULTS.md`; it files nothing outside this box. **Zero solver core-minutes; zero GPU-hours.** The
companion edit is five rows appended to `docs/dafoam/README.md` §3 — inserted **before** the D19M row,
which is untouched to the byte — closing the second half of the gap the addendum above named.

**One pre-existing drift, disclosed because this commit adds to it:** four documents cite
`docs/dafoam/README.md` by line, at `:92`, `:100`, `:153` and `:154`. The `:153`/`:154` anchor is the
IDWarp image/md5 row, which had already drifted to `:200` before today and to `:202` when D19M
landed; after these five rows it sits at **`:207`**. The drift is not created here, the anchor's
content is named so it can be re-found, and **no citing document was edited to chase it** — those are
their owners' files.

---

## Addendum 2026-09-02 (dafoam lane) — `curriculum_SO3` AND `curriculum_SO3aR2` ARE INDEXED: **A `PASS` HAD NO `RESULTS.md`, NO INDEX ROW AND NO `README.md` §3 ROW, AND A READER OF THE STANDING VERDICT TABLE WOULD HAVE CONCLUDED THE INCOMPRESSIBLE MULTIPOINT WAS NEVER DONE**

**Nothing above this line was edited.** No existing row, table, column, heading or section was
altered, moved or renamed. **No frozen `PREREGISTRATION.md`, no grade JSON, no grader and no
`docs/LAB_STATE.md` was touched, and ZERO compute was spent** — every figure below is read from an
artefact already on disk, and the verdict column is a **citation, never a summary**.

**Why this addendum exists.** `CURRICULUM-SO3` ran to the end on 2026-09-01, graded **`PASS`** on
both rows, and had a `docs/COST_CALIBRATION.md` row from 04:18Z the same morning — while
`docs/dafoam/README.md` contained **zero occurrences of `SO3` or `SO-3` anywhere**, `cases/dafoam/INDEX.md`
carried no row for it, and no `RESULTS.md` existed. That is `docs/dafoam/GRADING_CHAIN.md` bullet 9
in the live for the third time: *nothing links a graded verdict to `README.md` §3 or to this file*,
and the hop is a person reading a page. **The companion edits to this addendum are
`cases/dafoam/ladder-a/A1/curriculum_SO3/RESULTS.md` (new) and four rows appended to
`docs/dafoam/README.md` §3 after the D19M rows, which are untouched to the byte.**

**Both items are graded, and their two rows are recorded beside each other, never one in place of the
other** (`FAMILY_SUPERVISION_GUIDELINES.md` R11). The columns are the 2026-08-31 backfill's five, in
its order. **CAUSE CLASS** is Sanaa's GRADING TRANSPARENCY ORDER of 2026-08-31
(`etc/sessions/2026-08-31T2055Z_sanaa_grading_transparency_order.md`, `4116024a`): one of exactly
eight, and **a `PASS` carries none**.

| new directory | pair files | run tree (outside the repo) | verdict of record, with the artefact it is read from | CAUSE CLASS |
|---|---|---|---|---|
| `ladder-a/A1/curriculum_SO3aR2/` | `PREREGISTRATION.md` (frozen `181fd627`, arming `ffae7724`), `QUEUE_ENTRY_DRAFT.json`, the nine instruments; **no `RESULTS.md` — none exists on disk or at HEAD** | `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient/` (five arms `MESH X-S F-S X-P F-P`, all `rc=0`, `chain=COMPLETE declared=5 executed=5`) | **`GATE FAIL`**, rows `{"SHIPPED": "GATE FAIL", "PATCHED": "PASS"}` — `SO3aR2_grade_20260831T230221Z.json` → `verdict`, `rows`; the `.out` line reads `VERDICT GATE FAIL  rows={'SHIPPED': 'GATE FAIL', 'PATCHED': 'PASS'}  declared=5 executed=5`. SHIPPED `G5J` aggregate **31.498325840045588 %** against a 5.0 % band, **2 of 4 pairs `GATE FAIL`**, worst **47.18912652536565 %** (`shape[6]`), and `G5C` `GATE FAIL` at all three scenarios (worst 36.8983 % at point0). PATCHED `G5J` `PASS`, aggregate **2.6779490823450605 %**, 4 of 4 pairs — **and that number sits INSIDE the 2.5–5 % harness-sound floor of `VERIFICATION_CHARTER.md` §7 step 4, so it may never be described as a sub-percent verification**, and it was **measured at iteration 0 only**. Worst shipped-vs-patched adjoint divergence **118.72578844249743 %**. **14.318 core-min** against **22.1** registered (ratio **0.648×**), \$0.01224 **derived, not measured** — `docs/COST_CALIBRATION.md` row `C-20260831T230621.613076Z-d360c175` | **PHYSICS-FAIL — AGAINST THE SHIPPED TOOLCHAIN.** The SHIPPED row's multipoint objective gradient missed its registered band by more than 6× on this case with every arm `rc=0`, the mesh gate `PASS`, the toolchain gate `PASS` and the trivial-baseline control `PASS` (0 of 4 in band at `h = 1e-8`) — **the instrument is shown able to go red and the failing quantity is the gradient itself.** The class matches `GRADING_CHAIN.md`'s existing shipped-row rows for this family (SO-1aR); it is stated rather than carried, since that page has no SO-3aR2 row, and is the supervisor's to ratify |
| `ladder-a/A1/curriculum_SO3/` | `PREREGISTRATION.md` (frozen `7f7d0fb1`, through Amendment 1 `b229f0e2` and Amendment 2 `573aae08`/`ab27dff7`, all **before first compute**), **`RESULTS.md` (landed by this addendum's companion commit)**, `QUEUE_ENTRY_DRAFT.json`, `reference/REFERENCE_EVIDENCE_MANIFEST.md`, the nine instruments | `/home/ubuntu/certonomous-runs/CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation/` (seven arms `MESH O-S XE-S FE-S O-P XE-P FE-P`, all `rc=0`, `chain=COMPLETE declared=7 executed=7`, `grader_rc=0`) | **`PASS`**, rows `{"SHIPPED": "PASS", "PATCHED": "PASS"}` — `SO3_grade_20260901T040709Z.json` → `verdict`, `rows`; `.out` reads `VERDICT PASS  rows={'SHIPPED': 'PASS', 'PATCHED': 'PASS'}  declared=7 executed=7`; `SO3_STOP_MARKER.json` carries the same pair with `verdict_source: "COPIED FROM THE COMPARATOR ARTEFACT"`. Both optimisers printed **`Optimal Solution Found.`** (12 majors SHIPPED, 10 PATCHED, `max_iter` 50). Endpoint FD **at the final design point**: `G5J` aggregate **0.08594454384641227 %** / **0.06890419283803313 %**, worst pair 0.18906 % / 0.25332 %, 4 of 4 `PASS` on both rows. **Weighted drag −16.155328072130235 % / −16.15513273980908 % — AND THE LIFT COLLAPSE IS INSEPARABLE FROM THOSE FIGURES: `CL` is UNCONSTRAINED by registration and went [0.31190, 0.49877, 0.66398] → [−0.05737, 0.15241, 0.36012] (SHIPPED) and → [−0.05676, 0.15320, 0.36119] (PATCHED), NEGATIVE at point 0 on both rows.** The artefact's own `forbidden_readings` bars quoting the drag reduction without the `CL` pair beside it. **28.900 core-min** against **228.59** registered (ratio **0.126×**), \$0.02471 **derived, not measured** — `docs/COST_CALIBRATION.md` row `C-20260901T041827.958337Z-26909c1d` | — (**`PASS` carries no class**). But the `PASS` is **narrower than the word**: `G-PROV` refuses to publish it without the travelling chain, and every link — `CURRICULUM-SO3aR2` and `CURRICULUM-SO1a` — is **`GATE FAIL` at item level with a `GATE FAIL` SHIPPED row**. **Both endpoint aggregates read `BELOW_HARNESS_FLOOR`** — *"a number below 2.5 % on this stack is a claim about the harness … not a tighter verification"* — reported, never gated |

### ⚠ FOUR THINGS THIS BACKFILL FOUND AND DID NOT PAPER OVER

**1. SO-3aR2 STILL HAS NO `RESULTS.md`, AND THIS LANE DID NOT MANUFACTURE ONE.** Its verdict of record
exists only in the grade artefact outside git and in the `COST_CALIBRATION` row. **This lane's brief
covered SO-3's `RESULTS.md`**; writing a first results record for an item it was not dispatched to
write up is a supervisor's call and not a lane's — the precedent is the 2026-08-31 backfill's own
refusal for SO-1bR, and `curriculum_AVWC/RESULTS.md` §10 before it. **The row above is written from
the grade artefact, which is the authority.**

**2. SO-3's registered `P6` PREDICTED THE SHIPPED ROW WOULD `GATE FAIL`, AND IT PASSED — and `P8`
MISSED ON BOTH F ARMS.** `P8` registered *"at least one evaluation fails per F arm"*; the census
measured **34 declared, 34 succeeded, 0 failed** on both. **The multipoint evaluation pathology the
registration expected did not reproduce**, and the census is shown to have been looking rather than
blind: `R5_read_F` is in the birth register as born against the real code path, and the F-plant
control read **112 planted values** back off disk at a worst residual of 1.79e-16. **Both misses are
recorded as misses in `curriculum_SO3/RESULTS.md` §8 and neither is dressed up.**

**3. A TOKEN-NAMING DEFECT IN SO-3's FROZEN COMPARATOR, DISCLOSED AND NOT REPAIRED.**
`P2_CL_at_alpha0_in_band` reads `MISS`, while the statement its name makes — *baseline `CL` at
α₀ = 5.139° lies in [0.45, 0.55]* — **is TRUE of the undeformed baseline**, which measured
**0.49876526085592926**. `so3_grade.py:2512-2519` reads the **X arm's own** scenario-1 `CL`, and in
this item the X arms run **at the optimum** by registration, where that value is 0.15320 (PATCHED) /
0.15241 (SHIPPED). **Neither reading may be quoted against the other**: nobody may say the baseline
`CL` was out of band, and nobody may say `P2` really hit. The comparator is md5-pinned and the item
has had first compute, so **this is disclosed, never repaired.** Same shape as the `P5` naming defect
the pre-registration declared about itself at §13.2.

**4. QUEUE ENTRIES: SO-3 HAS ONE, SO-3aR2 HAS NONE, AND NEITHER HAS A `GRADING_CHAIN.md` ROW.**
`verification/queue/dafoam/launched/SO3_chain.json` exists and carries `prereg_commit`
`ab27dff7542a56d47be55435c48e1e00a3eb9f09` — **the Amendment 2 commit, not the original freeze**, and
its own `_prereg_commit_WHY_NOT_THE_ADD_COMMIT` field explains why in terms: against `7f7d0fb1`'s tree
`so3_grade.py` hashes to the **struck** `d786e10d…`, so the family template's prescribed derivation
would have pinned a tree whose grader is not the grader that ran. Its `cost_core_min_estimate` is
**228.59**, matching this addendum's registered figure. **There is no queue entry for SO-3aR2**, in
`launched/`, `held/` or `refused/` — consistent with the 2026-08-31 addendum above, which recorded the
same absence for SO-3a, SO-3aR and SO-2MR. `docs/dafoam/GRADING_CHAIN.md` carries **no row for either
item** and is the supervisor's page: it was **not edited here**. **Stated so the count is known;
nothing is filed here.**

**5. FOUR UNTRACKED FILES SIT IN `curriculum_SO3/` AND WERE DELIBERATELY NOT SWEPT.**
`STATUS.queue.SO3_chain` and `launcher.queue.out` (the queue runner's own launch status and wrapper
output, written to the case directory by the entry's `_launch` block), `so3_xf_drive_evidence.txt`,
and the two `reference/*.log` files excluded by `.gitignore:270` (`cases/dafoam/**/*.log`) —
Amendment 1's residual **R8**, still open. **This lane deleted nothing and committed nothing that is
not its own**: landing another lane's uncommitted work under cover of one's own path is the L-423
failure, and the `.gitignore` question is above a lane. **An unexpected file is inspected, never
reverted.**

### WHAT THIS ADDENDUM DOES NOT DO

It moves no gate, band, threshold, cap or label; it re-grades nothing; it runs nothing; it adds no
number that is not already written in a cited artefact; it edits no frozen document, no grader, no
pre-registration and no `docs/LAB_STATE.md`; it files nothing outside this box.
**Zero solver core-minutes; zero GPU-hours.**

**Placement, disclosed rather than left to be inferred:** the four `README.md` §3 rows are appended
**after** the D19M rows, at the foot of the A1 block, keeping SO-3aR2 immediately before SO-3 in
chain order. The D19 family's own grouping is left intact and not interleaved, so **no existing row
moved**; the SO-3aR2/SO-3 pair is chronologically earlier than D19O and D19M and is placed by chain
adjacency rather than by timestamp. **Line-number drift in `docs/dafoam/README.md` continues:** the
IDWarp image/md5 row cited at `:153`/`:154` by four documents, and last recorded at `:207`, now sits
at **`:211`** — measured after this edit, not predicted from a row count. The drift is not created
here, the anchor's content is named so it can be re-found, and **no citing document was edited to
chase it** — those are their owners' files.
