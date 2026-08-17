"""Docket entries raised while extending the TMR flat-plate ladder.

Both are defects in code this session was told not to edit, so they are
recorded as proposals rather than fixed in place.
"""
import json
import pathlib
import sys

sys.path.insert(0, "sdk")
from chief_engineer import agenda                                # noqa: E402

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[1]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

DOCKET = lab_paths.AGENDA / "docket.json"
NOW = "2026-07-31T20:30:00Z"
NEW = [{
    "id": "w5-ladder-band-guard-counts-rungs-it-did-not-fit",
    "objective": (
        "Make the ladder band's extrapolation guard measure its tolerance "
        "against the three rungs it actually fitted, not against every rung "
        "the caller happened to pass"
    ),
    "rationale": (
        "The guard rejects a fit whose Richardson value lands more than 15 "
        "percent of the measured range width outside that range. It fits "
        "the last three rungs but takes the range from all values handed "
        "in, so the same fit is conclusive or not conclusive depending on "
        "how many rungs the caller passes. The flat plate is the fixture "
        "the 15 percent was calibrated on and it sits on both sides of the "
        "line: handed the four rungs 816, 3264, 13056 and 52224 its "
        "extrapolate sits 8.48 percent above the top of the range and the "
        "ladder is certified with a band of 1.99e-5, which is 0.70 percent "
        "of the drag; handed only the three rungs the fit uses it sits "
        "21.16 percent above and the same ladder is declined with the "
        "sentence that its extrapolate falls outside the range it measured. "
        "The tolerance comment records the 8.48 percent figure, so the "
        "calibration was done on a four rung call and the three rung call "
        "was never checked. Every other act calls this with exactly three "
        "rungs. Nothing here says which reading is correct, only that a "
        "certifier must not answer two ways to one fit."
    ),
    "citations": [
        "Roache, Verification and Validation in Computational Science and "
        "Engineering, on grid convergence index practice",
        "Eca and Hoekstra 2014, procedure for the estimation of "
        "discretization uncertainty",
        "Certonomous flat-plate five-rung ladder, 2026-07-31",
    ],
    "est_core_min": 5.0,
    "cost_basis": (
        "measured; the whole question is decided by re-running the existing "
        "band unit tests with both call shapes, no solver time at all"
    ),
    "expected_knowledge_gain": (
        "Whether any of the ladders this lab has declined were declined by "
        "the rung count of the call rather than by their own numbers, and a "
        "certifier that cannot give two answers to one fit"
    ),
    "source_kind": "measurement",
    "status": "proposed",
    "created_at": NOW, "decided_at": None, "decision_note": None,
}, {
    "id": "w5-tmr-iteration-caps-are-guesses-not-measurements",
    "objective": (
        "Replace the fixed per rung iteration caps in the flat-plate ladder "
        "with a cap derived from the rung's cell count, and re check the "
        "bump and airfoil ladders for the same defect"
    ),
    "rationale": (
        "The flat-plate ladder's caps were 3000, 4000, 5000, 9000 and "
        "15000 for rungs of 816, 3264, 13056, 52224 and 208896 cells. The "
        "three coarsest exited early on their residual test at 482, 966 and "
        "2846 iterations, so their caps never bound anything. The two "
        "finest ran to their caps. Measured on this hardware on 2026-07-31, "
        "the finest rung at its 15000 cap still had drag falling by 1.04e-5 "
        "per thousand iterations and a peak to peak spread of 4.44e-7 over "
        "its last fifty, which is more than four times the module's own "
        "flatness gate of 1e-7, so the module would have refused to extract "
        "the rung it had just spent an hour computing. The iteration count "
        "needed scales with cell count and not with rung index: fine to "
        "finer took 3.99 times as many iterations to reach one part in ten "
        "thousand of its own final drag, against a cell count ratio of 4. A "
        "cap chosen by hand per rung is a guess that gets worse the finer "
        "the grid, which is exactly where the ladder needs it most."
    ),
    "citations": [
        "Certonomous flat-plate finest rung, measured 2026-07-31 19:13 to "
        "20:12 UTC",
        "ASME V and V 20 on solution verification",
    ],
    "est_core_min": 20.0,
    "cost_basis": (
        "measured; the iteration to tolerance curves already exist in the "
        "four solved rungs and the fifth, so the scaling can be fitted "
        "without a new solve"
    ),
    "expected_knowledge_gain": (
        "A refinement ladder whose rungs are all stopped by the same test "
        "rather than by five different hand chosen numbers, and an answer "
        "to whether the bump and airfoil ladders carry the same defect"
    ),
    "source_kind": "measurement",
    "status": "proposed",
    "created_at": NOW, "decided_at": None, "decision_note": None,
}]

d = json.loads(DOCKET.read_text())
have = {p["id"] for p in d["proposals"]}
added = [p for p in NEW if p["id"] not in have]
bad = [(p["id"], agenda.proposal_violations(p)) for p in added]
bad = [(i, v) for i, v in bad if v]
if bad:
    for i, v in bad:
        print(f"  VIOLATION {i}: {v}")
    raise SystemExit(1)
d["proposals"].extend(added)
d["generated_at"] = NOW
DOCKET.write_text(json.dumps(d, indent=1) + "\n")
for p in added:
    print(f"  + {p['id']}  {p['est_core_min']:.0f} core-min")
print(f"  docket now {len(d['proposals'])}, all passing text rules")
