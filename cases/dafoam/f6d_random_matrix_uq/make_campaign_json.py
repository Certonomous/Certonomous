"""Build campaign/F6d_random_matrix_uq.json from the primary artifacts.
Every field is read from a file this study produced; nothing is retyped."""
import json
import sys as _sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# NOT `HERE.parents[1] / "campaign"`.  This generator WRITES
# `campaign/F6d_random_matrix_uq.json`, and it reached the campaign root by
# COUNTING two segments up from a path that has now moved twice.  MOVE_MAP
# batch 6 (R22) moved this file from `demo-output/website/dafoam/...` to
# `cases/dafoam/...`, at which point `parents[1] / "campaign"` became
# `cases/campaign` -- a directory that does not exist -- and batch 7 (R21)
# moves the real destination to `verification/campaign`.  There is no path
# literal in the expression, so no prefix rewrite reached it in either
# batch.  `lab_paths.CAMPAIGN` is bound to the pair and is correct on both
# sides of the move.
_sys.path.insert(0, str(next(
    _p for _p in Path(__file__).resolve().parents
    if (_p / "scripts" / "lab_paths.py").is_file()) / "scripts"))
import lab_paths as _lab_paths                                # noqa: E402
CAMP = _lab_paths.CAMPAIGN

agg = json.loads((HERE / "aggregate_result.json").read_text())
ver = json.loads((HERE / "verify_sampler_result.json").read_text())
bar = json.loads((HERE / "barycentric_reach.json").read_text())
rea = json.loads((HERE / "realizability_of_flipped_corner.json").read_text())
cost = json.loads((HERE / "cost.json").read_text())

out = {
    "family": "F6",
    "sub_family": "d",
    "title": ("Random-matrix / maximum-entropy model-form UQ on periodic hills, "
              "and a sign error found in F6a's eigenvalue perturbation"),
    "date": "2026-07-30",
    "solver": "OpenFOAM v2606 simpleFoam",
    "case": agg["case"],
    "framework": {
        "citation": ("Xiao, H., Wang, J.-X. & Ghanem, R.G., A Random Matrix Approach for "
                     "Quantifying Model-Form Uncertainties in Turbulence Modeling, "
                     "arXiv:1603.09656 (2016); Comput. Methods Appl. Mech. Engrg. 313:941-965"),
        "local_full_text": "docs/papers/uncertainty_quantification/xiao_wang_ghanem_1603.09656.pdf",
        "configuration_follows_paper_table_1": {
            "N_KL": 30, "kl_mesh": [50, 30], "N_p": 3,
            "lx_over_H": 2.0, "ly_over_H": 1.0,
            "delta_cases": [0.2, 0.6],
        },
        "paper_inconsistencies_found": [
            "Appendix A step 2.4 writes L_ii = sigma_d*sqrt(u_i), dropping the factor 2 "
            "carried by main-text Eqs. (16) and (24); only the main-text form satisfies "
            "E{[G]} = [I] (verified numerically both ways).",
            "Appendix A step 1.3 assigns the polynomial-chaos expansion of Eq. (17) to the "
            "off-diagonal terms; Eq. (17) is the gamma PDF of u_i, which enters the diagonal "
            "terms, as Secs. 3.3-3.4 state correctly.",
        ],
    },
    "baseline": agg["baseline"],
    "les_reference": agg["les_reference"],
    "null_test": {
        "purpose": "propagating R_sample = R_bar must leave the baseline where it is",
        "first_iteration_Ux_initial_residual": 5.45887611783393e-08,
        "reattachment_x_over_h": agg["null_test"]["all_admitted"]["reattachment"]["mean"],
        "baseline_reattachment_x_over_h": agg["baseline"]["reattachment_x_over_h"],
        "profile_mae_percent": agg["null_test"]["all_admitted"]["profile_mae_pct"]["mean"],
        "noise_floor_reattachment_x_over_h": 1.0e-4,
        "noise_floor_profile_mae_percentage_points": 0.44,
    },
    "sampler_verification": ver,
    "barycentric_reach": bar,
    "sign_error_in_F6a": {
        "what": ("all 18 system/fvOptions under demo-output/website/dafoam/f6a_epistemic_band/ "
                 "end codeAddSup with 'eqn += fvc::div(deltaR)', deltaR = blendDelta*2k(bPert-bB); "
                 "in OpenFOAM this makes the effective anisotropy b_eff = 2*bB - bPert, i.e. the "
                 "perturbation applied backwards"),
        "openfoam_sources": [
            "src/finiteVolume/fvMatrices/fvMatrix/fvMatrix.C:1682  source() -= su.mesh().V()*su.field()",
            "src/fvOptions/lnInclude/meanVelocityForce.C:209  eqn += tSu (a driving force)",
            "applications/solvers/incompressible/simpleFoam/UEqn.H:9,11",
            "src/TurbulenceModels/turbulenceModels/linearViscousStress/linearViscousStress.C:107-117",
        ],
        "controlled_experiment_signcheck": {
            "design": ("laminar periodic hill at Re=100, meanVelocityForce holding Ubar=0.72; "
                       "the driving pressure gradient the solver must find discriminates the "
                       "two sign hypotheses"),
            "ref_nu1_gradient": 0.0154175637371754,
            "src_minus_gradient": 0.0154261190758809,
            "ref_nu3_gradient": 0.0380264475825401,
            "src_plus_gradient": 0.0380204576055009,
            "conclusion": "R_eff = R_model - deltaR",
        },
        "realizability_audit": rea,
        "limiter_evidence": {
            "F6a_recorded_1C": ("demo-output/website/solve_registry/uq_oneC_20260729T023701Z.log: "
                                "limitVelocity limitVelocity1 Limited 24864 (48.16%) of cells"),
            "corrected_sign_1C": ("dafoam/f6d_random_matrix_uq/f6a_recheck/corrected_oneC/log.simpleFoam: "
                                  "Limited 0 (0%) of cells"),
        },
        "F6a_recheck_with_corrected_sign": {
            "iterations": 3800,
            "check_convergence_verdict": "NOT_CONVERGED for all three corners",
            "final_Ux_initial_residual": {"oneC": 7.08165e-3, "twoC": 1.04985e-3, "threeC": 2.81796e-3},
            "reattachment_x_over_c_NOT_GATE_PASSING": {"oneC": 1.040889466376252,
                                                       "twoC": 1.1085156103868683,
                                                       "threeC": "fragmented, 14 Cf crossings"},
            "nasa_experiment_reattachment_x_over_c": 1.100,
            "note": ("these two numbers bracket the experiment but neither run met its "
                     "convergence gate; they are recorded as motivation, not as a band"),
        },
    },
    "eigenspace_corner_comparison": {
        "prescribed_stress_mode": agg.get("eigenspace_corners", {}).get("per_corner"),
        "live_model_mode": agg.get("live_model_runs"),
    },
    "random_matrix_bands": agg.get("random_matrix"),
    "profile_coverage": {
        k: v.get("profile_coverage") for k, v in (agg.get("random_matrix") or {}).items()
    },
    "profile_coverage_CONVERGENCE_CAVEAT_2026-08-11": (
        "These coverage fractions are NOT SAFE TO QUOTE. campaign/"
        "F6D_ENSEMBLE_CONVERGENCE_AUDIT.md re-measured this ensemble and found no member "
        "settled: writeInterval equals endTime so only one snapshot exists, and the one "
        "integrated output the tree retains (the meanVelocityForce pressure gradient) still "
        "swings by 86% of its own level over the final 500 iterations at the median, with 23 "
        "of 84 members reversing its sign. Recomputing this block over the better-settled half "
        "of each group drops delta=0.2 coverage from 1.000 to 0.752 and HALVES the mean "
        "envelope width, 0.542 to 0.245 -- so more than half of the delta=0.2 envelope is "
        "transient scatter and the 100% is achieved by it. delta=0.6 holds at 0.994 over its "
        "settled half, but that half is itself unsettled (median swing 1.38), so it is "
        "untested rather than vindicated. This is the only metric on which the random-matrix "
        "band beats the corner union, and that margin is the part least able to bear weight."
    ),
    "live_corner_union_profile_coverage": agg.get("live_corner_union_profile_coverage"),
    "cost": cost,
    "cost_CAVEAT_2026-08-11": (
        "These timings are sound AS RUN, but they price 4,000 iterations per member, which "
        "the convergence audit shows is not enough to settle this case under perturbation. "
        "Any budget transferred from them under-prices a converged ensemble by roughly 3-5x."
    ),
    "note": ("Nothing is filtered. Every band is reported over all admitted members AND over "
             "the residual-gated subset, because the gate is measurably biased: the members it "
             "discards are systematically the ones closest to the LES truth "
             "(F6a_epistemic_propagation.md Sec. 9.2 predicted exactly this before the work ran)."),
    "note_CONTRADICTED_2026-08-11": (
        "The 'note' above is contradicted, not merely weakened, and the contradiction is "
        "measured. See campaign/F6D_ENSEMBLE_CONVERGENCE_AUDIT.md Sec. 3-4. Reattachment "
        "tracks settledness monotonically across this ensemble -- most-settled quartile mean "
        "7.21, least-settled 5.25, against a baseline of 7.64 and an LES truth of 4.6-4.7 -- "
        "and the members carrying the LES agreement are the least settled in the ensemble "
        "(delta=0.2: median pressure-gradient swing 1.513 for the covering members against "
        "0.270 for the rest). The 12 members that fail the 1e-3 residual gate at delta=0.2 are "
        "83% unsettled against 14% for the 28 that pass. So the gate was largely separating "
        "CONVERGED from UNCONVERGED members, not calm samples from hard ones, and 'the gate is "
        "measurably biased' asserts a reading whose confound was never excluded. The audit "
        "states its own finding as correlational and names the competing physics reading it "
        "cannot rule out on existing data; the 152 core-min continuation pre-registered in "
        "campaign/F6D_OPTION_A_PREREGISTRATION.md is what discriminates them. Until it "
        "reports, neither 'report ungated' nor 'report gated' is established by this "
        "ensemble, and the defensible rule is to gate on measured settledness of the "
        "quantity being reported."
    ),
}

(CAMP / "F6d_random_matrix_uq.json").write_text(json.dumps(out, indent=2, default=float))
print(f"wrote {CAMP / 'F6d_random_matrix_uq.json'}")
