"""Fresh-clone preflight: a tracked script with a shebang and no exec bit.

WHY THIS EXISTS. `scripts/launch_solve.sh`, `scripts/lever_echo_emit.py` and
`scripts/mint_retrospective_certificates.py` were tracked mode 100644 from the
day they were created, so a fresh clone of this repository could not run the
lab's only sanctioned launcher (`59b7e7ac`). Nobody noticed for as long as they
existed, because every working copy on this box carried the bit LOCALLY while
the committed tree did not -- `git ls-tree HEAD` and `stat` disagreed, and only
the commit travels.

AND IT WAS NOT COSMETIC. `scripts/case_preflight.sh` was tracked 100644 too, and
`launch_solve.sh` gated its preflight on `[ -x "$PF" ]`. A missing mode bit
therefore SKIPPED THE ENTIRE PREFLIGHT GATE, silently, and the launcher went
ahead -- so on a fresh clone the D12 promise that the harness runs the preflight
"so the caller cannot forget" did not hold. That is the fail-false shape: silence
read as success. Both the bit and the gate are fixed; this module is what stops
the class coming back.

WHAT THIS CHECKS, AND WHAT IT DELIBERATELY DOES NOT.

`REQUIRED_EXECUTABLE` is the small set that a fresh clone must be able to
execute. It fails hard. It is small on purpose: an attempt to MEASURE which
scripts are bare-path invoked was made and is recorded as UNRELIABLE rather than
as a result. Invocation goes through indirection -- `"$PF" "$CASE"` in
`launch_solve.sh:160` and `[str(self.LAUNCHER), ...]` in
`sdk/tests/test_lever_echo.py:790` -- so a literal-path search structurally
cannot see the two call sites we already know about. Its null was void, not a
finding (LESSONS.md L-43, L-51). The gap is recorded as a gap and not written
into this module as a constraint (L-48).

`WAIVED` is the dated register of every OTHER tracked shebang-bearing file that
currently has no exec bit -- 234 of them at adoption, owned by four different
families. They are NOT mass-corrected here: changing another family's files
across a family boundary is exactly what the supervision charter forbids, and a
234-file mode sweep would land in a tree where other agents hold live work. The
register makes the gap countable and stops it growing: a NEW shebang-bearing
tracked file that is neither executable nor registered FAILS this check, and a
registered file that has since gained its bit fails it too, so the register can
never quietly drift out of date.

Grandfathered by enumeration rather than by date (the schema-rails pattern,
Infra family supervision guidelines section 1.3): the list is the migration
boundary, it is visible, and every refusal names the file it refused.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

#: Adoption date of the waiver register below.
WAIVER_REGISTER_DATED = "2026-08-10"

#: Tracked scripts a fresh clone MUST be able to execute, with the reason.
REQUIRED_EXECUTABLE = {
    "scripts/launch_solve.sh":
        "the only sanctioned way to start a long solve (LESSONS.md D12); its own "
        "usage line is `./launch_solve.sh` and sdk/tests/test_lever_echo.py:790 "
        "invokes it as a bare path",
    "scripts/case_preflight.sh":
        "launch_solve.sh runs it as the preflight gate; when the bit is absent "
        "the gate is skipped rather than failed, so this bit is load-bearing for "
        "a safety check and not for convenience",
    "scripts/lever_echo_emit.py":
        "emitted into the launched process (launch_solve.sh:251) through python3, "
        "so the bit is not strictly load-bearing -- pinned here to hold the state "
        "committed at 59b7e7ac rather than let it regress unobserved",
    "scripts/mint_retrospective_certificates.py":
        "operator-run minting tool committed executable at 59b7e7ac; pinned for "
        "the same reason",
}

#: Tracked shebang-bearing files with no exec bit, as of WAIVER_REGISTER_DATED.
#: Enumerated, not swept away. See the module docstring for why.
WAIVED_NO_EXEC_BIT = (
    "demo-output/website/campaign/B52_RUNG6_REPLICATE_runs/run_closure.py",
    "demo-output/website/campaign/B52_RUNG6_REPLICATE_runs/run_rung6_replicates.py",
    "demo-output/website/campaign/DMR_runs/dmr_locator.py",
    "demo-output/website/campaign/DMR_runs/make_case.py",
    "demo-output/website/campaign/DPW8_V2_runs/build_mesh.py",
    "demo-output/website/campaign/DPW8_V2_runs/joukowski_theory.py",
    "demo-output/website/campaign/DPW8_V2_runs/make_case.py",
    "demo-output/website/campaign/DPW8_V2_runs/run_case.py",
    "demo-output/website/campaign/DRAW_SCATTER_RETROFIT/scatter_bar.py",
    "demo-output/website/campaign/F3_runs/build_report.py",
    "demo-output/website/campaign/F3_runs/make_cone_case.py",
    "demo-output/website/campaign/F3_runs/make_diamond_case.py",
    "demo-output/website/campaign/F3_runs/make_wedge_case.py",
    "demo-output/website/campaign/F3_runs/run_cone_case.py",
    "demo-output/website/campaign/F3_runs/run_diamond_case.py",
    "demo-output/website/campaign/F3_runs/run_wedge_case.py",
    "demo-output/website/campaign/F4_runs/build_report.py",
    "demo-output/website/campaign/F4_runs/make_cylinder_case.py",
    "demo-output/website/campaign/F4_runs/make_swbli_case.py",
    "demo-output/website/campaign/F4_runs/run_cylinder_case.py",
    "demo-output/website/campaign/F5_runs/analyze_re3900.py",
    "demo-output/website/campaign/F5_runs/cylinder_ladder.py",
    "demo-output/website/campaign/F5_runs/cylinder_ladder_3d.py",
    "demo-output/website/campaign/F5_runs/run_rung.py",
    "demo-output/website/campaign/F5b_runs/run_pitch.py",
    "demo-output/website/campaign/F5c_runs/collect.py",
    "demo-output/website/campaign/F5c_runs/plot_evidence.py",
    "demo-output/website/campaign/F5c_runs/run_a4.py",
    "demo-output/website/campaign/F5c_runs/run_stage_a.py",
    "demo-output/website/campaign/F5c_runs/run_step.py",
    "demo-output/website/campaign/F5c_runs/summarise.py",
    "demo-output/website/campaign/F7_runs/extract_front.py",
    "demo-output/website/campaign/F7_runs/front_metrics.py",
    "demo-output/website/campaign/F7_runs/gate_compare.py",
    "demo-output/website/campaign/F7_runs/grade_f7a.py",
    "demo-output/website/campaign/F7_runs/integrated_front.py",
    "demo-output/website/campaign/F7_runs/make_dambreak.py",
    "demo-output/website/campaign/F7_runs/plot_f7a_R1.py",
    "demo-output/website/campaign/F7_runs/run_dambreak.sh",
    "demo-output/website/campaign/F8_runs/bem_analysis/bem_sequence_s.py",
    "demo-output/website/campaign/F8_runs/phase6_mrf/genmesh.sh",
    "demo-output/website/campaign/F8_runs/phase6_mrf/runSolve.sh",
    "demo-output/website/campaign/F8_runs/s10_replay/replay_s10_s12_pfinit.py",
    "demo-output/website/campaign/F8_runs/s10_replay/s10d_corpus_replay.py",
    "demo-output/website/campaign/F9_work/analyze_f9.py",
    "demo-output/website/campaign/F9_work/f9_criteria.py",
    "demo-output/website/campaign/F9_work/finalize_f9.py",
    "demo-output/website/campaign/F9_work/setup_f9_round3.py",
    "demo-output/website/campaign/FPE_DIAG_runs/run_fpe_diag.py",
    "demo-output/website/campaign/GEN_ALT_runs/run_gen_alt.py",
    "demo-output/website/campaign/MESH_CERT_RULINGS_2026-08-10/recheck_95.py",
    "demo-output/website/campaign/R4_runs/mesh_rung.sh",
    "demo-output/website/campaign/R4_runs/run_c3_leg2.py",
    "demo-output/website/campaign/R4_runs/run_c3_replicates.py",
    "demo-output/website/campaign/R4_runs/solve_rung.sh",
    "demo-output/website/campaign/R4_runs/yplus.sh",
    "demo-output/website/campaign/W2_sparta_runs/setup_sparta_case.sh",
    "demo-output/website/campaign/W3_runs/run.sh",
    "demo-output/website/campaign/W3_runs/setup.sh",
    "demo-output/website/committee-grids/apply_variant.py",
    "demo-output/website/committee-grids/batch1.sh",
    "demo-output/website/committee-grids/batch10.sh",
    "demo-output/website/committee-grids/batch11.sh",
    "demo-output/website/committee-grids/batch12.sh",
    "demo-output/website/committee-grids/batch5.sh",
    "demo-output/website/committee-grids/batch6.sh",
    "demo-output/website/committee-grids/batch7.sh",
    "demo-output/website/committee-grids/batch8.sh",
    "demo-output/website/committee-grids/batch9.sh",
    "demo-output/website/committee-grids/convert_and_check.sh",
    "demo-output/website/committee-grids/inspect_ugrid.py",
    "demo-output/website/committee-grids/ladder_table.py",
    "demo-output/website/committee-grids/locate_bad_faces.py",
    "demo-output/website/committee-grids/make_dpw5_case.py",
    "demo-output/website/committee-grids/run_case.sh",
    "demo-output/website/committee-grids/run_hardened_on_dpw5.sh",
    "demo-output/website/committee-grids/run_hlpw6_variant.sh",
    "demo-output/website/committee-grids/summarise_runs.py",
    "demo-output/website/committee-grids/ugrid_to_foam.py",
    "demo-output/website/dafoam/f6d_random_matrix_uq/run_campaign.sh",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/Allclean.sh",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/preProcessing.sh",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5CorrectedComposite.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5DObjDXv.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5DObjDXvReset.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5DiagRatio.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5FixedDFdW.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5FixedDRdXv.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5HandComposition.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5MatvecDrDW.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5MatvecMaxCorrected.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5NoiseFloor.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5OffDiagSingle.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5RealSeed.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeA5TwoSidedFormula.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeChainLinksA5.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeFFDGeometry.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probeWarpDerivA5.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/probe_driver.sh",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/runScript.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/runScript_meshQualityConstraint_v2.py",
    "demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/runScript_tightAdjoint.py",
    "demo-output/website/dafoam/ladder-a/logs_A1_stepsize/fdStepSweep.py",
    "demo-output/website/dafoam/ladder-a/logs_A3/compare_cp.py",
    "demo-output/website/dafoam/ladder-a/logs_A3/extract_cp.py",
    "demo-output/website/dafoam/ladder-a/logs_A3/runScript_coarse_mesh_final.py",
    "demo-output/website/dafoam/ladder-a/logs_A3/runScript_fine_mesh_final.py",
    "demo-output/website/dafoam/ladder-a/logs_A3/shock_location.py",
    "demo-output/website/dafoam/ladder-a/logs_A4/A4_runScript.py",
    "demo-output/website/dafoam/ladder-a/logs_A6/runScript.py",
    "demo-output/website/dafoam/ladder-b/B3_work/CBFS/runScript.py",
    "demo-output/website/dafoam/ladder-b/B3_work/CBFS/runScript_diag_force.py",
    "demo-output/website/dafoam/ladder-b/B3_work/CBFS/runScript_diag_frozen.py",
    "demo-output/website/dafoam/ladder-b/B3_work/CBFS/runScript_stage2.py",
    "demo-output/website/dafoam/ladder-b/B3_work/fixA_kbounds/runScript.py",
    "demo-output/website/dafoam/ladder-b/B3_work/fixA_kbounds/runScript_diag_force.py",
    "demo-output/website/dafoam/ladder-b/B3_work/fixA_kbounds/runScript_stage2.py",
    "demo-output/website/dafoam/ladder-b/B3_work/fixB_SA/runScript.py",
    "demo-output/website/dafoam/ladder-b/B3_work/fixB_SA/runScript_diag_force.py",
    "demo-output/website/dafoam/ladder-b/B3_work/fixB_SA/runScript_stage2.py",
    "demo-output/website/dafoam/ladder-b/B3_work/fixC_empty/runScript.py",
    "demo-output/website/dafoam/ladder-b/B3_work/fixC_empty/runScript_diag_force.py",
    "demo-output/website/dafoam/ladder-b/B3_work/fixC_empty/runScript_stage2.py",
    "demo-output/website/dafoam/ladder-b/S1_work/scripts/runScript_S1.py",
    "demo-output/website/dafoam/ladder-b/S1_work/scripts/runScript_hump.py",
    "demo-output/website/dafoam/ladder-b/S1_work/scripts/runScript_hump_nat.py",
    "demo-output/website/dafoam/ladder-b/S1_work/scripts/runScript_hump_nrn.py",
    "demo-output/website/dafoam/ladder-b/S1_work/scripts/runScript_hump_wf.py",
    "demo-output/website/dafoam/ladder-b/duct_baseline/macro_field_reader.py",
    "demo-output/website/dafoam/ladder-b/duct_baseline/verify_macro_reader.py",
    "demo-output/website/dafoam/rans_model_comparison/collect_results.py",
    "demo-output/website/dafoam/rotation_branch/diag_rotation_ubend.py",
    "demo-output/website/dafoam/rotation_branch/patch_unittest/build_run.sh",
    "demo-output/website/dafoam/rotation_branch/repro_geometries.py",
    "demo-output/website/dafoam/rotation_branch/repro_issue57_inflate_cube.py",
    "demo-output/website/dafoam/rotation_branch/supervisor_sweep/run_one.sh",
    "demo-output/website/dafoam/rotation_branch/supervisor_sweep/supervisor_verify_idx8.py",
    "demo-output/website/dafoam/upstream_repro/repro_warpderiv_airfoil.py",
    "demo-output/website/dafoam/upstream_repro/repro_warpderiv_ubend.py",
    "demo-output/website/dafoam/upstream_repro/run_repro.sh",
    "demo-output/website/dafoam/w4_idx16/run.sh",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/Allclean.sh",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/diagnose.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/diagnose_chain.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/diagnose_chain2.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/diagnose_frozen.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/diagnose_partials.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/diagnose_warp.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/diagnose_warp_exact.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/genAirFoilMesh.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/preProcessing.sh",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/probeDCDDXv.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/probeHandComposition.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/probeMeshMetricRefinement.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/probeWallBranch.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/probeWarpDeriv.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/probeWarpDerivRealSeed.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/runScript.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/runScript_LoD.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/runScript_Stability_Not_Working.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/runScript_vsp.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/stepStudy.py",
    "demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/stepStudy2.py",
    "demo-output/website/dafoam/work_refined/NACA0012_Airfoil_Incompressible_probe/probeFreshY.py",
    "demo-output/website/dafoam/work_refined/NACA0012_Airfoil_Incompressible_probe/run_all_probes.sh",
    "demo-output/website/dafoam/work_refined/NACA0012_Airfoil_Incompressible_refined/Allclean.sh",
    "demo-output/website/dafoam/work_refined/NACA0012_Airfoil_Incompressible_refined/checkAll8Refined.py",
    "demo-output/website/dafoam/work_refined/NACA0012_Airfoil_Incompressible_refined/genAirFoilMesh.py",
    "demo-output/website/dafoam/work_refined/NACA0012_Airfoil_Incompressible_refined/preProcessing.sh",
    "demo-output/website/dafoam/work_refined/NACA0012_Airfoil_Incompressible_refined/runScript.py",
    "demo-output/website/dafoam/work_refined/NACA0012_Airfoil_Incompressible_refined/runScript_LoD.py",
    "demo-output/website/dafoam/work_refined/NACA0012_Airfoil_Incompressible_refined/runScript_Stability_Not_Working.py",
    "demo-output/website/dafoam/work_refined/NACA0012_Airfoil_Incompressible_refined/runScript_vsp.py",
    "demo-output/website/dafoam/work_refined/NACA0012_Airfoil_Incompressible_refined/stepStudyRefined.py",
    "demo-output/website/dafoam/work_sail/naca0015_sail_coarse/Allclean.sh",
    "demo-output/website/dafoam/work_sail/naca0015_sail_coarse/preProcessing.sh",
    "demo-output/website/dafoam/work_sail/naca0015_sail_coarse/runScript.py",
    "demo-output/website/dafoam/work_sail/naca0015_sail_full/Allclean.sh",
    "demo-output/website/dafoam/work_sail/naca0015_sail_full/preProcessing.sh",
    "demo-output/website/dafoam/work_sail/naca0015_sail_full/runScript.py",
    "demo-output/website/dafoam/work_sail/naca0015_sail_medium/Allclean.sh",
    "demo-output/website/dafoam/work_sail/naca0015_sail_medium/preProcessing.sh",
    "demo-output/website/dafoam/work_sail/naca0015_sail_medium/runScript.py",
    "demo-output/website/dafoam/work_wing/naca4412_wing_coarse/Allclean.sh",
    "demo-output/website/dafoam/work_wing/naca4412_wing_coarse/preProcessing.sh",
    "demo-output/website/dafoam/work_wing/naca4412_wing_coarse/runScript.py",
    "demo-output/website/hlpw6/make_case.py",
    "demo-output/website/hlpw6/make_hlpw6_case.py",
    "demo-output/website/hlpw6/memwatch.py",
    "demo-output/website/hlpw6/rank_sweep.sh",
    "demo-output/website/hlpw6/run_ladder.sh",
    "demo-output/website/hlpw6/ugrid_to_foam.py",
    "docs/aws/provision.sh",
    "scripts/add_proposals_r5.py",
    "scripts/audit_camera_discretion.sh",
    "scripts/audit_transcripts.sh",
    "scripts/auto-stop.sh.proposed",
    "scripts/build_laptop_bundle.py",
    "scripts/check_convergence.py",
    "scripts/check_convergence_sweep.py",
    "scripts/check_convergence_validate.py",
    "scripts/coefficient_uq_plate.py",
    "scripts/coefficient_uq_plate_analysis.py",
    "scripts/contention_audit.py",
    "scripts/cost_calibration.py",
    "scripts/demo_servers.sh",
    "scripts/dispatch_queue.py",
    "scripts/filming_keepalive.sh",
    "scripts/filming_mode.sh",
    "scripts/gate_table.py",
    "scripts/kill_worker.sh",
    "scripts/laptop_bundle/replay_console.py",
    "scripts/laptop_bundle/run-demo.sh",
    "scripts/ledger_backup.py",
    "scripts/memwatch.py",
    "scripts/morning_report.py",
    "scripts/package_caches.sh",
    "scripts/self_audit.py",
    "scripts/session_keepalive.sh",
    "scripts/ugrid_to_foam.py",
    "scripts/verify_warm_replay.sh",
    "sdk/scripts/cbfs_bentaleb_forensics.py",
    "sdk/scripts/citation_tier_audit.py",
    "sdk/scripts/closure_cbfs_donor_coverage.py",
    "sdk/scripts/closure_in_sample_gate.py",
    "sdk/scripts/extract_patch_stl.py",
    "sdk/scripts/fit_cost_scaling.py",
    "sdk/scripts/is_idle.sh",
    "sdk/scripts/mega_batch_keeper.sh",
    "sdk/scripts/model_form_batch.py",
    "sdk/scripts/replay_monitor_rules.py",
    "sdk/scripts/replay_s12_unsettled_stop.py",
    "sdk/scripts/score_s6_partition.py",
    "sdk/scripts/sparta_frozen_score.py",
    "sdk/scripts/sparta_regression.py",
)

#: Which family answers for each waived path, by longest-prefix match.
OWNERS = (
    ("sdk/", "Infrastructure and Standards"),
    ("scripts/", "Infrastructure and Standards"),
    ("docs/", "Infrastructure and Standards"),
    ("demo-output/website/campaign/", "Cases"),
    ("demo-output/website/dafoam/", "DAFoam"),
    ("demo-output/website/", "Demo and website"),
)


def owner_of(path: str) -> str:
    """The family that answers for *path*. Longest prefix wins."""
    best = ""
    owner = "UNASSIGNED"
    for prefix, name in OWNERS:
        if path.startswith(prefix) and len(prefix) > len(best):
            best, owner = prefix, name
    return owner


def tracked_shebang_scripts(root: Path | None = None) -> dict[str, str]:
    """Map committed path -> mode in ``HEAD``, for files whose first two bytes
    are ``#!``.

    THE AUTHORITY IS ``HEAD``, NOT THE INDEX, AND THE DIFFERENCE IS NOT
    PEDANTIC. This function first read `git ls-files -s`, and that read the
    fix as landed while it was only STAGED: `core.filemode` is false in this
    repository, so `git commit -- <path>` takes the working tree's content
    together with HEAD's mode, and a `git update-index --chmod=+x` sitting in
    the index is silently dropped from the commit. The index said 100755, the
    new tree said 100644, and this checker said green. A clone materializes
    the COMMIT and nobody's index, so HEAD is the only mode that answers the
    question this module asks. Found by planting the specimen rather than by
    reading the code (`0462b45b`).

    ``git ls-tree`` also settles the working-tree question for free: it reports
    what was committed, so a locally-chmodded file that was never committed can
    no longer read as fixed.
    """
    root = Path(root or REPO_ROOT)
    out = subprocess.run(
        ["git", "ls-tree", "-r", "HEAD"], cwd=str(root),
        capture_output=True, text=True, check=True).stdout
    found: dict[str, str] = {}
    for line in out.splitlines():
        if not line:
            continue
        meta, path = line.split("\t", 1)
        mode, kind, _sha = meta.split(None, 2)
        if kind != "blob":
            continue
        try:
            with open(root / path, "rb") as handle:
                if handle.read(2) != b"#!":
                    continue
        except OSError:
            continue
        found[path] = mode
    return found


def audit(root: Path | None = None) -> dict[str, list]:
    """Three findings, kept apart because they are three different facts.

    ``missing_required`` -- a fresh clone cannot run something it must.
    ``unregistered``     -- a new shebang script with no bit and no waiver.
    ``stale_waivers``    -- a waived file that has since gained its bit, or that
                            no longer exists, so the register is out of date.
    """
    modes = tracked_shebang_scripts(root)
    waived = set(WAIVED_NO_EXEC_BIT)

    missing_required = sorted(
        path for path in REQUIRED_EXECUTABLE
        if modes.get(path) != "100755")

    unregistered = sorted(
        path for path, mode in modes.items()
        if mode != "100755" and path not in waived
        and path not in REQUIRED_EXECUTABLE)

    stale = sorted(
        path for path in waived
        if path not in modes or modes[path] == "100755")

    return {
        "missing_required": missing_required,
        "unregistered": unregistered,
        "stale_waivers": stale,
    }


def waived_by_owner(root: Path | None = None) -> dict[str, list[str]]:
    """The waiver register split by the family that answers for each file."""
    split: dict[str, list[str]] = {}
    for path in WAIVED_NO_EXEC_BIT:
        split.setdefault(owner_of(path), []).append(path)
    return {k: sorted(v) for k, v in sorted(split.items())}
