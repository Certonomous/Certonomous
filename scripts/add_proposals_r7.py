import json, pathlib, sys
sys.path.insert(0, "sdk")
from chief_engineer import agenda

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
NOW = "2026-07-30T03:40:00Z"
NEW = [{
    "id": "r7-strouhal-mesh-sensitivity-across-the-ladder",
    "objective": (
        "Establish whether the cylinder ladder's Strouhal gates are sensitive to "
        "near-wall spacing at every rung or only at the highest one, by running a "
        "matched-spacing twin at the ladder's best-gated low-Reynolds rung and comparing "
        "the shift against the one already measured at the top"
    ),
    "rationale": (
        "A matched pair at the ladder's top rung, differing only in first-cell height by "
        "55 percent, moved drag by 7.1 percent, base suction by 6.9 percent and "
        "fluctuation amplitude by 3.3 percent , all small against the 50 to 100 percent "
        "deviations those quantities carry versus the three-dimensional reference. "
        "Strouhal moved 35.1 percent, from 0.2409 to 0.1564, and that is large enough to "
        "flip which side of the reference band the run lands on, over-predicting in one "
        "member and under-predicting in the other. An independent windowed transform "
        "confirmed two genuinely distinct frequency bands rather than a period-detector "
        "artifact. So at that rung the Strouhal gate is not a solid measurement. "
        "Nothing is known about the lower rungs, which have no twins, and the ladder "
        "reports a Strouhal trend ACROSS rungs, and that is a trend whose sensitivity is therefore unquantified at every point but one. The best-supported reading is that the "
        "sensitivity belongs to a chaotic-dynamics regime in which a finite window no "
        "longer contains one robust dominant frequency, which is consistent with "
        "published evidence that two-dimensional confined cylinder wakes are fully "
        "chaotic well below this Reynolds number. That reading predicts the low rung "
        "will be ROBUST. Falsifiable either way: if the low rung's Strouhal moves "
        "comparably under the same spacing change, the sensitivity is not regime-related "
        "and every Strouhal gate on this ladder is soft; if it holds within a few "
        "percent, the sensitivity has an onset and the lower gates stand."
    ),
    "citations": [
        "Certonomous cylinder ladder, matched-spacing pair at the top rung, 2026-07-30",
        "Certonomous literature reproduction review, on two-dimensional wake chaos "
        "below this Reynolds number",
    ],
    "est_core_min": 45.0,
    "cost_basis": (
        "measured, from the low rung's own 2,417-second single-core solve, which a twin "
        "reproduces at the same cost"
    ),
    "expected_knowledge_gain": (
        "Tells us whether one of this ladder's four gated quantities can be trusted at "
        "all. A gate that moves 35 percent under a mesh parameter nobody varied is not a gate, and we currently cannot say whether that applies to one rung or to every "
        "rung. It also tests the chaotic-regime explanation on a prediction it makes "
        "rather than on the observation that motivated it."
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
    for i, v in bad: print(f"  VIOLATION {i}: {v}")
    raise SystemExit(1)
d["proposals"].extend(added); d["generated_at"] = NOW
DOCKET.write_text(json.dumps(d, indent=1) + "\n")
for p in added: print(f"  + {p['id']}  {p['est_core_min']:.0f} core-min")
print(f"  docket now {len(d['proposals'])}, all passing text rules")
