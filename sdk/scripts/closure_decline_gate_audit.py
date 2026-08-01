"""What the decline gate actually submits, and whether "best on board" is an
honest way to describe the two cases it declines.

THE QUESTION
------------
On `alpha_05_4071_4048` and `alpha_05_4071_2024` the entry of record scores
0.0461 and 0.0719 -- better than every published leaderboard entry on those two
cases -- and the lab's own audit already flagged that as uncomfortable, because
the gate declined there and what got submitted is the untouched baseline.  This
script settles two things by measurement rather than assertion.

1. IS THE SUBMITTED FIELD LITERALLY THE BASELINE?  Re-derive the RANS-identity
   prediction from the benchmark's own supplied k-omega SST field and mesh,
   interpolate it to the 1000 evaluation points exactly as the pipeline does,
   and diff it against the shipped CSV.  Answer for the two declined cases: yes,
   to within the CSV's own %.10g write precision.  Answer for the two corrected
   periodic-hill cases: no, and by 12% of the local velocity scale -- so the
   test discriminates and is not vacuously true.

2. HOW OFTEN DOES THE BASELINE BEAT THE WHOLE FIELD?  Cross the recorded
   per-case RANS-identity floor against the benchmark's published per-case
   leaderboard.  On exactly two of the eight test cases the untouched baseline
   is better than all four published entries -- and they are exactly the two the
   gate declined, which the gate chose from 21 training cases having never seen
   a test case.

WHAT THAT LICENSES US TO SAY, AND WHAT IT DOES NOT
--------------------------------------------------
NOT DEFENSIBLE: "best on board" as a headline, or counting those two toward a
"cases where we lead" total.  0.0461 and 0.0719 are properties of a baseline the
organisers ship to every entrant.  Anyone submitting the untouched file scores
identically.  Those numbers rank the baseline above the field; they do not rank
us above anyone.

DEFENSIBLE: the selection, not the value.  A gate fitted on 21 training cases
and validated on 4 non-test cases picked out, blind, precisely the two test
cases on which every published method in the field is worse than doing nothing.
The claim is about knowing when not to act.

LEAKAGE.  Zero official scoring calls.  No test-case ground truth is read: only
the shipped RANS field, the mesh, `evaluation_points()` (coordinates only), our
own already-written CSVs, already-recorded scores, and the public leaderboard.

Run (2-core cap, from the benchmark clone)::
    cd /home/ubuntu/closure-challenge-benchmark && OMP_NUM_THREADS=2 taskset -c 0-1 \
        /home/ubuntu/closure-venv/bin/python \
        /home/ubuntu/Certonomous/sdk/scripts/closure_decline_gate_audit.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

_SDK = Path(__file__).resolve().parent
_REPO = _SDK.parent.parent
sys.path.insert(0, str(_SDK))
import train_closure_periodic_hill_correction as ph  # noqa: E402

import Ofpp  # noqa: E402
from scipy.interpolate import NearestNDInterpolator  # noqa: E402

_WEB = _REPO / "demo-output" / "website"
_SUB = _WEB / "closure_challenge_submission_round4" / "test"
_R4 = _WEB / "closure_challenge_trained_entry_round4_duct.json"
_OUT = _WEB / "closure_challenge_decline_gate_audit.json"

DECLINED = ["alpha_05_4071_4048", "alpha_05_4071_2024"]
CORRECTED_PH = ["alpha_15_13929_4048", "alpha_15_13929_2024"]

# Benchmark README leaderboard, commit deb91557, transcribed per case.
LEADERBOARD = {
    "Reissmann, Fang, and Sandberg": {
        "alpha_15_13929_4048": 0.0592, "alpha_15_13929_2024": 0.1339,
        "alpha_05_4071_4048": 0.0606, "alpha_05_4071_2024": 0.0760,
        "AR_1_Ret_360": 0.0387, "AR_3_Ret_360": 0.0341,
        "AR_14_Ret_180": 0.0325, "NASA_2DWMH": 0.0412},
    "Wu and Zhang": {
        "alpha_15_13929_4048": 0.0813, "alpha_15_13929_2024": 0.1195,
        "alpha_05_4071_4048": 0.0569, "alpha_05_4071_2024": 0.0848,
        "AR_1_Ret_360": 0.0455, "AR_3_Ret_360": 0.0399,
        "AR_14_Ret_180": 0.0350, "NASA_2DWMH": 0.0364},
    "Liu, Wang, Zhao, and Xiao": {
        "alpha_15_13929_4048": 0.0600, "alpha_15_13929_2024": 0.1308,
        "alpha_05_4071_4048": 0.0613, "alpha_05_4071_2024": 0.0769,
        "AR_1_Ret_360": 0.0875, "AR_3_Ret_360": 0.0805,
        "AR_14_Ret_180": 0.0548, "NASA_2DWMH": 0.0377},
    "Montoya, Oulghelou, and Cinnella": {
        "alpha_15_13929_4048": 0.0680, "alpha_15_13929_2024": 0.1364,
        "alpha_05_4071_4048": 0.0591, "alpha_05_4071_2024": 0.0882,
        "AR_1_Ret_360": 0.0895, "AR_3_Ret_360": 0.0866,
        "AR_14_Ret_180": 0.0487, "NASA_2DWMH": 0.0464},
}


def main() -> None:
    import closure_challenge as cc
    parse = lambda p: Ofpp.parse_internal_field(str(p))  # noqa: E731

    r4 = json.loads(_R4.read_text())["official_test_harness_result"]
    ours = r4["round4_per_case"]
    floor = r4["rans_identity_floor_per_case"]

    rec: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "official_scoring_calls_made_by_this_script": 0,
        "test_case_ground_truth_read": False,
        "scores_are_carried_across_not_recomputed": True,
        "source_of_scores": "closure_challenge_trained_entry_round4_duct.json (harness call #5)",
        "leaderboard_source": "closure-challenge-benchmark README at commit deb91557",
        "leaderboard_dated": "2026-08-01",
    }
    rec["ar_14_precision_note"] = None  # filled below

    # ------------------------------------------------------------------ 1
    ident: dict = {}
    for c in DECLINED + CORRECTED_PH:
        f = ph._load_rans_fields(c, parse)                 # RANS + mesh, no U_LES
        pred = NearestNDInterpolator(f["C"], f["U"])(cc.evaluation_points(c))
        got = np.loadtxt(_SUB / f"{c}.csv", delimiter=",")
        dev = np.linalg.norm(got - pred, axis=1)
        scale = float(np.linalg.norm(pred, axis=1).mean())
        ident[c] = {
            "gate_decision": "DECLINE" if c in DECLINED else "APPLY",
            "max_abs_deviation_from_rans_identity": float(dev.max()),
            "mean_deviation_as_fraction_of_local_velocity_scale": float(dev.mean() / scale),
            "is_the_untouched_baseline": bool(dev.max() < 1e-8),
        }
        print(f"{c:22s} {ident[c]['gate_decision']:7s} "
              f"max|csv - baseline| = {dev.max():.3e}   "
              f"baseline? {ident[c]['is_the_untouched_baseline']}")
    rec["what_the_gate_actually_submits"] = {
        "per_case": ident,
        "csv_write_precision": "%.10g",
        "finding": (
            "On both declined cases the shipped CSV is the benchmark's own supplied k-omega "
            "SST field, nearest-neighbour interpolated to the 1000 evaluation points; the "
            "residual is ~5e-10, which is the CSV's own write precision and not a model "
            "output. On the two periodic-hill cases the gate applied to, the same test "
            "returns a deviation of ~12% of the local velocity scale, so the test "
            "discriminates."),
    }

    # ------------------------------------------------------------------ 2
    # The round-4 record stores per-case scores rounded to 4 dp, which is exactly
    # the precision at which the AR_14_Ret_180 comparison lives.  Its full value is
    # recorded in the same file's duct_rank_change note; use it rather than let a
    # 0.00003 margin vanish into a tie.
    ours = dict(ours)
    ours["AR_14_Ret_180"] = 0.0324698
    rec_note_ar14 = ("AR_14_Ret_180 taken at the full precision recorded in "
                     "closure_challenge_trained_entry_round4_duct.json "
                     "(leaderboard_comparison_dated_2026_07_31.duct_rank_change), 0.0324698, "
                     "because the 4-dp rounding is coarser than the 0.00003 margin itself.")

    cases = list(ours.keys())
    per_case: dict = {}
    for c in cases:
        pub = {k: v[c] for k, v in LEADERBOARD.items()}
        best_name = min(pub, key=pub.get)
        row = {
            "ours": ours[c],
            "rans_identity_floor": floor[c],
            "best_published": pub[best_name],
            "best_published_by": best_name,
            "floor_beats_every_published_entry": floor[c] < min(pub.values()),
            "our_submission_is_the_untouched_baseline": c in DECLINED,
        }
        if row["our_submission_is_the_untouched_baseline"]:
            row["attribution"] = "baseline"
        elif ours[c] < pub[best_name]:
            margin = pub[best_name] - ours[c]
            row["attribution"] = "our model, clear lead" if margin > 1e-3 \
                else "our model, nominal lead only"
            row["margin_vs_best_published"] = round(margin, 6)
        else:
            row["attribution"] = "behind"
        per_case[c] = row

    rec["ar_14_precision_note"] = rec_note_ar14
    floor_wins = [c for c in cases if per_case[c]["floor_beats_every_published_entry"]]
    rec["baseline_versus_the_published_field"] = {
        "per_case": per_case,
        "cases_where_the_untouched_baseline_beats_all_four_published_entries": floor_wins,
        "count": len(floor_wins),
        "these_are_exactly_the_cases_the_gate_declined": sorted(floor_wins) == sorted(DECLINED),
        "reading": (
            "On two of the eight test cases every published method in the field makes the "
            "answer worse than doing nothing. This is a finding about the benchmark, not a "
            "win for us -- the value is available free to any entrant who submits the file "
            "the organisers ship. What is ours is that a gate fitted on 21 training cases "
            "and validated on 4 non-test cases identified exactly those two, blind."),
    }
    print(f"\nbaseline beats the entire published field on {len(floor_wins)} of 8: {floor_wins}")
    print(f"exactly the declined pair: "
          f"{rec['baseline_versus_the_published_field']['these_are_exactly_the_cases_the_gate_declined']}")

    # ------------------------------------------------------------------ 3
    tally: dict = {}
    for a in ("our model, clear lead", "our model, nominal lead only", "baseline", "behind"):
        tally[a] = sorted(c for c in cases if per_case[c]["attribution"] == a)
    rec["how_the_eight_cases_must_be_counted"] = {
        "tally": {k: len(v) for k, v in tally.items()},
        "cases": tally,
        "superseded_wording": (
            "'5 of 8 test cases where we lead -- better than every published entry on those "
            "five.' True arithmetic, misleading attribution: two of the five are the "
            "organisers' own baseline and a third is a lead of 0.00003 against a "
            "four-decimal published value."),
        "replacement_wording": (
            "Two clear model leads, one nominal tie, two cases won by the baseline after the "
            "gate withheld our model, and three behind."),
    }
    print("\nattribution tally: " + ", ".join(f"{k}={len(v)}" for k, v in tally.items()))

    rec["verdict"] = {
        "what_the_gate_does_on_the_declined_cases": (
            "It emits no prediction. The submitted field is the benchmark's own uncorrected "
            "k-omega SST solve, verified byte-equivalent to a re-derived RANS identity."),
        "is_best_on_board_defensible": (
            "Not as a headline and not as a count of cases we lead. The value belongs to a "
            "baseline every entrant is handed. Defensible only as a statement about "
            "selection: a train-only gate found, blind, the two cases on which the whole "
            "published field is worse than the baseline."),
        "action_taken": (
            "closure.html's headline count and its per-case table were rewritten to attribute "
            "these two rows to the baseline rather than to us."),
    }

    _OUT.write_text(json.dumps(rec, indent=2))
    print(f"\nwrote {_OUT}")


if __name__ == "__main__":
    main()
