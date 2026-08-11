#!/usr/bin/env python3
"""
check_convergence_sweep.py -- run check_convergence.py over every log in
scripts/../demo-output/website/solve_registry/ (and optionally other
directories passed on the command line), and report anything that is not
CONVERGED, sorted so NOT_CONVERGED comes first.

This is the deliberate, one-time sweep this project had never run before
2026-07-30: every previous catch of an unconverged-but-quoted number (L-14,
L-15, the hump corners, A4, the TMR bump, the wall.json credentials) was
found by someone looking at something else. This script looks at everything,
on purpose.

Usage:
    check_convergence_sweep.py [DIR ...]        # defaults to solve_registry
    check_convergence_sweep.py --json > sweep.json

THIS GATE FAILS CLOSED, AND ITS FINDINGS NOW REACH ITS EXIT CODE.

It had no non-zero return anywhere in the file. Two different failures wore the
same green: a sweep that matched zero logs because the directory was empty or
misspelt printed `Swept 0 logs` and exited 0, and a sweep of 152 real logs
holding 73 NOT_CONVERGED and 56 CANNOT_TELL exited 0 as well. A gate that
cannot fail is not a gate, and this one is cited as gating L-14 closure.

So: an empty corpus prints RED and exits 2 with no verdict of any kind, in
--json mode too, because an instrument that read nothing has nothing to
serialize. And a log that is not CONVERGED now costs exit 1 -- unless it is in
the dated register below.

WHY A REGISTER RATHER THAN A BARE `exit 1`. 129 of these 152 logs are already
not passing, and most are deliberately preserved crash logs. Reddening on all
of them would make this gate permanently non-zero, which is an alarm that is
always on: people learn to route around it, exactly as they routed around the
reach line this script already printed and nobody acted on. The register is
lifted from `sdk/chief_engineer/exec_bits.py`, which faced this precisely and
wrote down why: the register does not mass-correct anything and does not bless
anything, it makes the existing gap countable and stops it GROWING. A NEW log
that is not converged, or a registered log whose status gets WORSE, fails this
check. The 129 below are a dated snapshot of a known state, not an approval.

It is a register of log basenames rather than a pointer at
campaign/NOT_PASSING_REGISTER.md because that document is prose for humans, not
a machine-readable list, and no gate should depend on parsing English.

Exit codes:  0 = swept >=1 log, nothing unregistered failing
             1 = a log not converged and not registered, or worse than registered
             2 = no logs found at all           (RED -- verdict withheld)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_convergence import classify  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
DEFAULT_DIR = REPO / "demo-output" / "website" / "solve_registry"

#: Dated snapshot of what was ALREADY not passing when the exit code was wired.
#: Basename -> the status recorded that day. Not an approval; a baseline that
#: makes the gap countable and stops it growing. Trim entries as cases are
#: fixed -- a registered log that now CONVERGES is reported as drift so this
#: list cannot quietly rot into a blanket amnesty.
REGISTER_DATED = "2026-08-11"
KNOWN_NOT_PASSING = {
    "F9_lowalpha_ext_20260730T150516Z.log": "CANNOT_TELL",
    "F9_mesh_coarse_q100_20260730T150516Z.log": "CANNOT_TELL",
    "F9_mesh_fine_q100_20260730T150516Z.log": "CANNOT_TELL",
    "F9_mesh_med_q100_20260730T151129Z.log": "CANNOT_TELL",
    "F9_physio_dt_half_20260730T150516Z.log": "CANNOT_TELL",
    "F9_pulsatile_fine_20260730T150516Z.log": "CANNOT_TELL",
    "F9_pulsatile_lowalpha_20260729T040223Z.log": "NOT_CONVERGED",
    "F9_pulsatile_lowalpha_20260729T040455Z.log": "CANNOT_TELL",
    "F9_pulsatile_physio_20260729T040223Z.log": "NOT_CONVERGED",
    "F9_pulsatile_physio_20260729T040454Z.log": "CANNOT_TELL",
    "F9_steady_beta50_20260730T041820Z.log": "CANNOT_TELL",
    "F9_steady_beta55_20260730T041820Z.log": "CANNOT_TELL",
    "F9_steady_q100_20260729T040133Z.log": "CANNOT_TELL",
    "F9_steady_q25_20260729T040133Z.log": "CANNOT_TELL",
    "F9_steady_q50_20260729T040133Z.log": "CANNOT_TELL",
    "F9_steady_q75_20260729T040133Z.log": "CANNOT_TELL",
    "F9_womersley_probe_check_20260730T041340Z.log": "CANNOT_TELL",
    "a1_realseed_idx01_20260729T235117Z.log": "CANNOT_TELL",
    "a5_chainlinks_20260729T221339Z.log": "CANNOT_TELL",
    "a5_corrected_composite_20260730T041501Z.log": "CANNOT_TELL",
    "a5_tight_adjoint_20260730T001025Z.log": "CANNOT_TELL",
    "adjwall_phase3_20260730T190749Z.log": "CANNOT_TELL",
    "b3_diag_frozen2_20260729T203706Z.log": "NOT_CONVERGED",
    "b3_diag_frozen3_20260729T220421Z.log": "NOT_CONVERGED",
    "b3_diag_frozen4_20260729T221805Z.log": "NOT_CONVERGED",
    "b3_diag_frozen5_20260729T224035Z.log": "NOT_CONVERGED",
    "b3_diag_frozen_20260729T203110Z.log": "NOT_CONVERGED",
    "d3_coloring_off_A1_20260729T023513Z.log": "CANNOT_TELL",
    "d3_coloring_off_A1_v2_20260729T024259Z.log": "CANNOT_TELL",
    "d3_coloring_off_A1_v3_20260729T024459Z.log": "CANNOT_TELL",
    "d3_opt4_probe80k_20260729T203735Z.log": "CANNOT_TELL",
    "d3_opt5_onera_n15_21840_20260729T223429Z.log": "CANNOT_TELL",
    "d3_opt5_onera_n28_42120_20260729T224308Z.log": "CANNOT_TELL",
    "d3_opt5_onera_n8_10920_20260729T223129Z.log": "CANNOT_TELL",
    "d3_opt5_sail_coarse_uncap_20260729T220737Z.log": "CANNOT_TELL",
    "d3_ranks8_A3coarse_20260729T035114Z.log": "CANNOT_TELL",
    "d3_sparsify_A1_20260729T024828Z.log": "CANNOT_TELL",
    "d3_sparsify_A3coarse_20260729T025029Z.log": "CANNOT_TELL",
    "d3_sparsify_fill1_A3coarse_20260729T030046Z.log": "CANNOT_TELL",
    "d5_EBRSM_20260729T022019Z.log": "NOT_CONVERGED",
    "d5_LRR_20260729T022019Z.log": "NOT_CONVERGED",
    "d5_SSG_20260729T022019Z.log": "NOT_CONVERGED",
    "d5b_EBRSM_20260729T022123Z.log": "NOT_CONVERGED",
    "d5b_LRR_20260729T022123Z.log": "NOT_CONVERGED",
    "d5b_SSG_20260729T022123Z.log": "NOT_CONVERGED",
    "d5c_EBRSM_20260729T022227Z.log": "NOT_CONVERGED",
    "d5d_EBRSM_20260729T022917Z.log": "NOT_CONVERGED",
    "d5e_EBRSM_20260729T023416Z.log": "NOT_CONVERGED",
    "d5f_EBRSM_20260729T023903Z.log": "NOT_CONVERGED",
    "d5g_EBRSM_20260729T023927Z.log": "NOT_CONVERGED",
    "dmr_res120_20260807T224408Z.log": "CANNOT_TELL",
    "dmr_res60_20260807T224510Z.log": "CANNOT_TELL",
    "dpw8_v2_L4_gate_20260729T231306Z.log": "CANNOT_TELL",
    "dpw8_v2_L4_gate_20260729T231415Z.log": "NOT_CONVERGED",
    "f11_re100_n128_20260730T041833Z.log": "NOT_CONVERGED",
    "f4_swbli_warmup20_20260730T004453Z.log": "CANNOT_TELL",
    "f5a_re1000_3d_pilot_20260729T215854Z.log": "CANNOT_TELL",
    "f5a_re2000_20260729T021614Z.log": "NOT_CONVERGED",
    "f5a_re2000_20260729T021645Z.log": "CANNOT_TELL",
    "f5a_re3900_20260729T203008Z.log": "CANNOT_TELL",
    "f5a_re3900_correctedspacing_20260729T233514Z.log": "CANNOT_TELL",
    "f5a_re3900_correctedspacing_20260729T233553Z.log": "CANNOT_TELL",
    "f5c_extended_simplec20k_20260730T042423Z.log": "NOT_CONVERGED",
    "f6a_diff_EBRSM_20260801T004539Z.log": "NOT_CONVERGED",
    "f6a_diff_EBRSM_v2_20260801T020424Z.log": "NOT_CONVERGED",
    "f6a_diff_LRR_20260801T003703Z.log": "NOT_CONVERGED",
    "f6a_diff_LRR_v2_20260801T003919Z.log": "NOT_CONVERGED",
    "f6a_diff_LRR_v3_20260801T004027Z.log": "CANNOT_TELL",
    "f6a_diff_LRR_v3b_20260801T004053Z.log": "NOT_CONVERGED",
    "f6a_diff_LRR_v4_20260801T004731Z.log": "NOT_CONVERGED",
    "f6a_diff_SST_a1_025_20260801T001506Z.log": "NOT_CONVERGED",
    "f6b2_fine_20260805T171046Z.log": "NOT_CONVERGED",
    "f6b2_veryfine_20260805T171046Z.log": "NOT_CONVERGED",
    "f6b3_relaxPC_20260811T011859Z.log": "NOT_CONVERGED",
    "f6b_feasibility2_20260729T035612Z.log": "NOT_CONVERGED",
    "f6b_feasibility_20260729T035528Z.log": "NOT_CONVERGED",
    "f6b_gate_20260729T035745Z.log": "NOT_CONVERGED",
    "f6b_physics_20260729T035647Z.log": "NOT_CONVERGED",
    "f7a_calpha0_test2_20260730T041759Z.log": "CANNOT_TELL",
    "f7a_calpha0_test_20260730T041650Z.log": "CANNOT_TELL",
    "f7a_paperdomain_test_20260730T041056Z.log": "CANNOT_TELL",
    "f8_genmesh_20260729T035945Z.log": "CANNOT_TELL",
    "f8_genmesh_v2_20260729T040846Z.log": "CANNOT_TELL",
    "f8_solve_7ms_20260729T041020Z.log": "CANNOT_TELL",
    "f8_solve_7ms_v2_20260729T041211Z.log": "CANNOT_TELL",
    "f8_solve_7ms_v3_20260729T041431Z.log": "CANNOT_TELL",
    "f8_uae_phase6_mrf_extend_20260730T000056Z.log": "NOT_CONVERGED",
    "hump_SA_resume2_20260729T204648Z.log": "NOT_CONVERGED",
    "hump_SA_resume_20260729T204118Z.log": "NOT_CONVERGED",
    "hump_SpalartAllmaras_20260729T023234Z.log": "NOT_CONVERGED",
    "hump_kEpsilon_20260729T035037Z.log": "NOT_CONVERGED",
    "hump_kEpsilon_relaxfix_20260729T202237Z.log": "NOT_CONVERGED",
    "hump_kOmega_resume_20260729T202024Z.log": "NOT_CONVERGED",
    "hump_realizableKE_20260729T035037Z.log": "NOT_CONVERGED",
    "hump_realizableKE_reinit2_20260729T203444Z.log": "NOT_CONVERGED",
    "hump_realizableKE_reinit_20260729T202957Z.log": "NOT_CONVERGED",
    "hump_realizableKE_relaxfix_20260729T202237Z.log": "NOT_CONVERGED",
    "r4-ahmed-c4_20260801T123350Z.log": "CANNOT_TELL",
    "r4-ahmed-c4b_20260801T131030Z.log": "CANNOT_TELL",
    "r4-ahmed-c5_20260801T124353Z.log": "CANNOT_TELL",
    "r4-ahmed-ladder_20260801T123000Z.log": "CANNOT_TELL",
    "r4_oneC_d0.10_20260729T205643Z.log": "NOT_CONVERGED",
    "r4_oneC_d0.15_20260729T205644Z.log": "NOT_CONVERGED",
    "r4_oneC_d0.175_20260729T220902Z.log": "NOT_CONVERGED",
    "r4_oneC_d0.20_20260729T220902Z.log": "NOT_CONVERGED",
    "r4_oneC_d0.225_20260729T220902Z.log": "NOT_CONVERGED",
    "r4_oneC_d0.25_20260729T204313Z.log": "NOT_CONVERGED",
    "r4_oneC_d0.25_boundedU_20260729T223716Z.log": "NOT_CONVERGED",
    "r4_oneC_d0.25_finemesh_20260729T223717Z.log": "NOT_CONVERGED",
    "r4_oneC_d0.25_finemesh_20260729T223847Z.log": "NOT_CONVERGED",
    "r4_oneC_d0.50_20260729T205644Z.log": "NOT_CONVERGED",
    "r4_oneC_d0.75_20260729T204313Z.log": "NOT_CONVERGED",
    "r4_oneC_d1.00_initFromBaseline_20260730T041127Z.log": "NOT_CONVERGED",
    "r4_oneC_d1.00_ramp_20260730T041242Z.log": "NOT_CONVERGED",
    "r4_twoC_d1.00_initFromBaseline_20260730T041127Z.log": "NOT_CONVERGED",
    "r5_measure_scaling_n15_20260729T231124Z.log": "NOT_CONVERGED",
    "r5_noresnorm_bigbudget_n15_20260729T232625Z.log": "NOT_CONVERGED",
    "r5_noresnorm_cl_only_n15_20260730T001135Z.log": "NOT_CONVERGED",
    "r5_noresnorm_fill1_n15_20260729T234853Z.log": "NOT_CONVERGED",
    "r5_noresnorm_mgso_n15_20260730T000213Z.log": "NOT_CONVERGED",
    "r5_noresnorm_n15_20260729T231834Z.log": "NOT_CONVERGED",
    "r5_noresnorm_richardson_n15_20260730T040153Z.log": "NOT_CONVERGED",
    "uq_oneC_20260729T023701Z.log": "NOT_CONVERGED",
    "uq_oneC_feas3_20260729T023512Z.log": "NOT_CONVERGED",
    "uq_twoC_20260729T023709Z.log": "NOT_CONVERGED",
    "w1hump_a1_028_20260808T020440Z.log": "NOT_CONVERGED",
    "w3-4412-layered-rep-AB_20260802T082430Z.log": "CANNOT_TELL",
    "w3-4412-layered-rep-CD_20260802T082436Z.log": "NOT_CONVERGED",
    "w3-4412-layered-rep-E_20260802T083414Z.log": "CANNOT_TELL",
}


def case_for_log(log_path: Path) -> str | None:
    """Best-effort: find the matching .done file (same stem) and pull its
    'case:' line, so the residualControl enrichment has somewhere to look."""
    done = log_path.with_suffix(".done")
    if not done.exists():
        return None
    try:
        for line in done.read_text(errors="replace").splitlines():
            m = re.match(r"case:\s*(\S.*)$", line)
            if m:
                case = m.group(1).strip()
                p = Path(case)
                if not p.is_absolute():
                    p = REPO / case
                return str(p) if p.exists() else None
    except OSError:
        return None
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="*", default=[str(DEFAULT_DIR)])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    logs: list[Path] = []
    for d in args.dirs:
        logs.extend(sorted(Path(d).glob("*.log")))
        logs.extend(sorted(Path(d).rglob("log.*")))  # OpenFOAM-style log.simpleFoam etc.

    logs = sorted(set(logs))

    # --- fail closed --------------------------------------------------------
    # Counted before anything is judged, and before --json gets to serialize
    # an empty list that a reader would take for a clean sweep. Nothing is
    # printed on stdout here: an instrument that read nothing has no verdict
    # to emit, in text or in JSON.
    if not logs:
        print("  RED: this sweep matched no logs at all.", file=sys.stderr)
        print(f"       Looked for */*.log and */log.* under {args.dirs}",
              file=sys.stderr)
        for d in args.dirs:
            state = "exists" if Path(d).is_dir() else "DOES NOT EXIST"
            print(f"         {d} -- {state}", file=sys.stderr)
        print("  No verdict. 0 logs swept, so nothing is claimed about "
              "convergence.", file=sys.stderr)
        return 2

    results = []
    for log in logs:
        case = case_for_log(log)
        r = classify(str(log), case)
        r["case_used"] = case
        results.append(r)

    order = {"NOT_CONVERGED": 0, "CANNOT_TELL": 1, "CONVERGED": 2}
    results.sort(key=lambda r: (order.get(r["status"], 9), r["log"]))

    # --- let the findings reach the exit code -------------------------------
    # Ranked worse-than-registered first. A status that got worse than its
    # recorded one counts as new: NOT_CONVERGED under a CANNOT_TELL register
    # entry is a fresh finding, not a known one.
    rank = {"CONVERGED": 2, "CANNOT_TELL": 1, "NOT_CONVERGED": 0}
    unregistered = []
    for r in results:
        if r["status"] == "CONVERGED":
            continue
        was = KNOWN_NOT_PASSING.get(Path(r["log"]).name)
        if was is None or rank[r["status"]] < rank.get(was, 2):
            r["register"] = "NEW" if was is None else f"WORSE than {was}"
            unregistered.append(r)

    # Drift in the other direction is reported, never reddened: a registered
    # log that now converges is good news and a line to delete, not an alarm.
    # Saying it out loud is what stops the register rotting into an amnesty.
    # Drift is only answerable when the sweep actually covered the directory
    # the register was taken over. On a partial sweep every registered log is
    # trivially "not seen", which is noise that would bury the finding the
    # reader came for -- the same drowning-in-its-own-output failure the camera
    # audit's rendered() comment warns about.
    seen = {Path(r["log"]).name: r["status"] for r in results}
    swept_default = any(Path(d).resolve() == DEFAULT_DIR.resolve()
                        for d in args.dirs if Path(d).exists())
    if swept_default:
        healed = sorted(n for n, s in KNOWN_NOT_PASSING.items()
                        if seen.get(n) == "CONVERGED")
        vanished = sorted(n for n in KNOWN_NOT_PASSING if n not in seen)
    else:
        healed = vanished = []

    if args.json:
        print(json.dumps(results, indent=2, default=str))
        return 1 if unregistered else 0

    counts = {"CONVERGED": 0, "NOT_CONVERGED": 0, "CANNOT_TELL": 0}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    print(f"Swept {len(results)} logs under {args.dirs}")
    print(f"  CONVERGED:     {counts['CONVERGED']}")
    print(f"  NOT_CONVERGED: {counts['NOT_CONVERGED']}")
    print(f"  CANNOT_TELL:   {counts['CANNOT_TELL']}")
    print()

    for status in ("NOT_CONVERGED", "CANNOT_TELL"):
        rows = [r for r in results if r["status"] == status]
        if not rows:
            continue
        print(f"=== {status} ({len(rows)}) ===")
        for r in rows:
            print(f"  {Path(r['log']).name}")
            print(f"      type:   {r.get('solver_type')}")
            print(f"      reason: {r.get('reason')}")
        print()

    # The verdict states its own reach and what the exit code was computed
    # against, so "0 new" can never be read without the 152 and the 129 that
    # give it meaning.
    print("-" * 71)
    print(f"  Reach: {len(results)} log(s) swept under {args.dirs}, "
          f"one classifier each.")
    print(f"  Baseline: {len(KNOWN_NOT_PASSING)} log(s) registered "
          f"not-passing as of {REGISTER_DATED}.")
    if unregistered:
        print(f"  {len(unregistered)} NOT in that register -- these are what "
              f"make this run fail:")
        for r in unregistered:
            print(f"    [{r['register']}] {Path(r['log']).name} "
                  f"-- {r['status']}")
    else:
        print("  0 unregistered failures: every log that is not converged was "
              "already known to be.")
    def _some(names: list[str], keep: int = 8) -> str:
        head = ", ".join(names[:keep])
        return head if len(names) <= keep else f"{head}, ... {len(names)-keep} more"

    if not swept_default:
        print(f"  drift against the register NOT evaluated: this is a partial "
              f"sweep, not {DEFAULT_DIR.name}/.")
    if healed:
        print(f"  drift: {len(healed)} registered log(s) now CONVERGE -- "
              f"delete them from the register: {_some(healed)}")
    if vanished:
        print(f"  drift: {len(vanished)} registered log(s) were not seen in "
              f"this sweep: {_some(vanished)}")

    return 1 if unregistered else 0


if __name__ == "__main__":
    sys.exit(main())
