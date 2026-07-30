#!/usr/bin/env python3
"""
check_convergence_validate.py -- known-answer validation suite for
check_convergence.py.

A checker that cannot reproduce the known answers is not a checker. This
file pins down every case this session independently confirmed the true
convergence status of, by direct log inspection, before check_convergence.py
was allowed anywhere near the wider estate. Run this after any change to
check_convergence.py; it must pass in full before the checker is trusted
again.

Usage: python3 scripts/check_convergence_validate.py
Exit code 0 = all pass, 1 = at least one failure.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_convergence import classify  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

# (label, expected_status, log_path, case_dir_or_None, why_this_is_the_known_answer)
CASES = [
    (
        "hump_baseline_f6a", "CONVERGED",
        "demo-output/website/dafoam/f6a_nasa_hump/case/log.rung3_gate", None,
        "Independently checked 2026-07-29: 'SIMPLE solution converged in 1772 "
        "iterations', all Initial residuals under gate. Public baseline number "
        "(reattachment 1.2534) rests on this run.",
    ),
    (
        "hump_baseline_act6", "CONVERGED",
        "mission-output/nasa-hump/act6-nasa_hump/log.simpleFoam", None,
        "Second, independent run of the same baseline (nine-act ledger): "
        "'SIMPLE solution converged in 1734 iterations', all Initial residuals "
        "under gate. Confirms the baseline is not a fluke of one run.",
    ),
    (
        "threeC_isotropic_corner", "CONVERGED",
        "demo-output/website/solve_registry/uq_threeC_20260729T023709Z.log", None,
        "'SIMPLE solution converged in 2948 iterations', all Initial residuals "
        "under gate (Ux 9.83e-9, Uz 6.29e-9, p 6.52e-9, omega 9.70e-11, k "
        "2.08e-8). Publicly quoted as the closest single check to experiment "
        "(1.1069, +0.63%) -- this one is real.",
    ),
    (
        "r4_delta0.00_control", "CONVERGED",
        "demo-output/website/solve_registry/r4_oneC_d0.00_20260729T204314Z.log", None,
        "'SIMPLE solution converged in 1795 iterations'. Control point of the "
        "band-tightening sweep; must reduce exactly to the unperturbed baseline.",
    ),
    (
        "r4_delta0.05", "CONVERGED",
        "demo-output/website/solve_registry/r4_oneC_d0.05_20260729T205644Z.log", None,
        "'SIMPLE solution converged in 2124 iterations', all Initial residuals "
        "under gate -- the only other genuinely converged point in the r4 sweep.",
    ),
    (
        "A4_ahmed_adjoint_check_totals", "CONVERGED",
        "demo-output/website/dafoam/ladder-a/logs_A4/A4_check_totals_run1.log", None,
        "PetscConvergedReason: 2 (CONVERGED_RTOL_NORMAL). The A4 adjoint itself "
        "is fine -- it used a different, healthy coarse mesh; only the fine-mesh "
        "PRIMAL (below) is compromised. Distinguishing these two is the point.",
    ),
    (
        "A4_ahmed_fine_primal", "NOT_CONVERGED",
        "demo-output/website/dafoam/ladder-a/logs_A4/A4_fine_primal_par4.log", None,
        "SIGNATURE 1. No 'SIMPLE solution converged' string. omega's per-"
        "iteration Initial residual collapses to a fixed 5.87e-31 after ~50 of "
        "500 iterations ('No Iterations 0' every step thereafter) while DAFoam's "
        "own raw 'Printing Primal Residual Statistics' block shows omega "
        "Residual Norm2 = 1.13e+35 at the same final state -- a genuine field "
        "blow-up masked by a falsely-reassuring normalised residual. The public "
        "headline CD=0.06998 was computed from this corrupted state and has "
        "since been withdrawn from the research board.",
    ),
    (
        "onera_m6_adjoint_probe80k", "NOT_CONVERGED",
        "/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-probe80k/run_opt4_probe80k.log", None,
        "SIGNATURE 2 (this is LESSONS.md L-15's own case). Both the CD and CL "
        "adjoint KSP solves report PetscConvergedReason: -5 (DIVERGED_BREAKDOWN), "
        "KSP residual collapsed to ~1e-322/~4e-320 (denormal), yet the process "
        "printed 'Residual tolerance satisfied, solution finished!' and exited "
        "zero. Exit code and the solver's own prose message both say success; "
        "only ConvergedReason says otherwise.",
    ),
    (
        "oneC_full_corner_delta1", "NOT_CONVERGED",
        "demo-output/website/solve_registry/uq_oneC_20260729T023701Z.log", None,
        "SIGNATURE 3. No 'SIMPLE solution converged' anywhere; ran to the "
        "endTime cap. At exit, Ux/Uz Initial residuals are O(0.1) (5-6 orders "
        "over gate), 63% of cells velocity-limited. This is the run the "
        "publicly-quoted band lower edge (0.5278) was extracted from -- "
        "withdrawn once checked.",
    ),
    (
        "twoC_two_component_corner", "NOT_CONVERGED",
        "demo-output/website/solve_registry/uq_twoC_20260729T023709Z.log", None,
        "SIGNATURE 3. No 'SIMPLE solution converged'; Uz/p/omega all 100-8790x "
        "over their own gate at exit. Also withdrawn from the public band.",
    ),
    (
        "r4_delta0.25_final_vs_initial", "NOT_CONVERGED",
        "demo-output/website/solve_registry/r4_oneC_d0.25_20260729T204313Z.log",
        "demo-output/website/dafoam/f6a_epistemic_band/r4_band_tightening_hump/oneC_delta0.25",
        "SIGNATURE 4. Previously reported as 'converged cleanly (k 1.67e-9, "
        "omega 4.25e-11)' -- those are the FINAL residuals. No 'SIMPLE solution "
        "converged' string exists in the log; the actual Initial residuals "
        "(p, Uz, omega) sit 10-150x over gate throughout the run's tail.",
    ),
    (
        "f8_uae_phase6_mrf", "NOT_CONVERGED",
        "demo-output/website/campaign/F8_runs/phase6_mrf/log.simpleFoam", None,
        "Already established in NOT_PASSING_REGISTER.md via the identical "
        "manual check this tool automates: 'grep -c SIMPLE solution converged' "
        "returns 0; force history still oscillating (not decaying) at endTime.",
    ),
    (
        "f5a_re2000_transient", "CANNOT_TELL",
        "demo-output/website/solve_registry/f5a_re2000_20260729T021645Z.log", None,
        "Unsteady URANS run (fractional Time progression, e.g. 0.0044802867). "
        "A steady SIMPLE-convergence gate does not apply; this checker must say "
        "so rather than force a verdict it has no basis for.",
    ),
]


def main() -> int:
    failures = []
    for label, expected, log_rel, case_rel, why in CASES:
        log_path = log_rel if log_rel.startswith("/") else str(REPO / log_rel)
        case_path = None
        if case_rel:
            case_path = case_rel if case_rel.startswith("/") else str(REPO / case_rel)
        result = classify(log_path, case_path)
        got = result["status"]
        ok = got == expected
        mark = "OK  " if ok else "FAIL"
        print(f"{mark}  {label:32s} expect={expected:14s} got={got:14s}")
        if not ok:
            print(f"      known-answer basis: {why}")
            print(f"      checker's actual reason: {result.get('reason')}")
            failures.append(label)

    print()
    if failures:
        print(f"{len(failures)} of {len(CASES)} known-answer cases FAILED: {failures}")
        print("This checker does not reproduce the known answers and must not be trusted or run wider.")
        return 1
    print(f"All {len(CASES)} known-answer cases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
