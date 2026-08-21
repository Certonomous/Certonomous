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
