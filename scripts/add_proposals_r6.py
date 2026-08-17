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
NOW = "2026-07-30T00:05:00Z"

NEW = [
    {
        "id": "r6-cylinder-wake-topology-onset",
        "objective": (
            "Locate the Reynolds number at which a two-dimensional cylinder wake stops "
            "producing a time-mean recirculation bubble, by running the single "
            "intermediate rung that halves the interval in which the transition is now "
            "known to lie"
        ),
        "rationale": (
            "Measured tonight across three rungs, all extracted by identical code against "
            "a definition confirmed word-for-word in the reference literature: mean "
            "recirculation length 0.397 diameters, then 0.254, then none at all. The "
            "third is a departure from the trend, not a continuation -- extrapolating the "
            "first two predicts about 0.165, and the method resolved 0.254 cleanly one "
            "rung earlier, so it would have seen 0.165. The mechanism is measured rather "
            "than assumed: reversal FREQUENCY is flat across all three rungs at 34 to 48 "
            "percent, while the amplitude of forward-going excursions grows from 0.22 to "
            "0.52 to 0.81, so the bubble is swamped in the average rather than "
            "extinguished in the flow. Meanwhile the three-dimensional bubble GROWS with "
            "Reynolds number over the same interval, so the two dimensionalities diverge "
            "rather than one merely lagging. The transition therefore sits inside a "
            "factor-of-two window and one intermediate rung halves it. A falsifiable "
            "prediction is already recorded: the intermediate rung either shows a "
            "detectable bubble near 0.16 to 0.20, supporting smooth extinction reaching "
            "zero close to the upper rung, or shows none, placing the onset lower. Either "
            "outcome is decisive, which is the property a rung should have before it is "
            "worth its compute."
        ),
        "citations": [
            "Certonomous cylinder Reynolds ladder, three gate-checked rungs, 2026-07-29",
            "Parnaudeau et al. (2008), recirculation length defined as the sign change of "
            "centreline mean streamwise velocity",
            "Jiang & Cheng (2017), matched two- and three-dimensional direct simulation of "
            "this geometry",
        ],
        "est_core_min": 110.0,
        "cost_basis": (
            "measured, using the cost exponent of 1.514 derived from this ladder's own two "
            "most recent rungs rather than the shallower 0.714 assumed earlier"
        ),
        "expected_knowledge_gain": (
            "A located transition rather than an interval, on the ladder's sharpest result. "
            "Every other quantity here says two dimensions is high by some percentage; this "
            "one says the mean wake differs in kind, which is far better evidence for a "
            "dimensionality attribution than any deviation figure."
        ),
        "source_kind": "gate",
        "status": "proposed",
        "created_at": NOW, "decided_at": None, "decision_note": None,
    },
    {
        "id": "r6-airfoil-second-gradient-mechanism",
        "objective": (
            "Identify the cause of the airfoil case's remaining shape-derivative error on "
            "its two interior leading-edge stations, which is now known not to be the "
            "mesh-warp defect and which worsens under mesh refinement"
        ),
        "rationale": (
            "The airfoil's headline defect was resolved tonight and traced to the mesh "
            "warp's own linearisation for opposing-direction combination modes. The two "
            "interior stations adjacent to the leading edge were then tested against that "
            "same mechanism and CLEARED: under the real objective seed they return 11.92 "
            "and 11.58 percent, matching their independently measured values to within "
            "0.08 points, with no sign flip. So the warp adds nothing to them and this "
            "case carries a SECOND, distinct defect. Its signature is diagnostic and "
            "unusual: the error is step-independent, and it grows under mesh refinement. "
            "Ordinary discretisation error shrinks under refinement, so whatever this is, "
            "it is not that -- and the direction of the trend is itself a strong clue, "
            "since very few mechanisms get worse with resolution. Candidates worth "
            "separating are a geometric quantity that becomes more singular as cells "
            "shrink near a high-curvature edge, and a term whose linearisation error "
            "scales with a mesh metric rather than with cell size. The link-by-link "
            "isolation approach is what finally resolved the first defect after six wrong "
            "mechanisms and should be applied here rather than guessing again."
        ),
        "citations": [
            "Certonomous shape-derivative root-cause study, the resolved first mechanism "
            "and the cleared interior stations, 2026-07-29",
            "Certonomous airfoil case survey, mesh-refinement behaviour of the interior "
            "station errors",
        ],
        "est_core_min": 40.0,
        "cost_basis": (
            "measured, from this case's own 3.5 core-minute verification cycle across "
            "several isolation probes"
        ),
        "expected_knowledge_gain": (
            "The last unexplained gradient error on the lab's most heavily verified case. "
            "An error that grows under refinement is also the more dangerous kind, because "
            "the usual response to a suspect gradient is to refine the mesh, and here that "
            "would make it worse while appearing to be the responsible thing to do."
        ),
        "source_kind": "gate",
        "status": "proposed",
        "created_at": NOW, "decided_at": None, "decision_note": None,
    },
]

d = json.loads(DOCKET.read_text())
have = {p["id"] for p in d["proposals"]}
added = [p for p in NEW if p["id"] not in have]
bad = [(p["id"], agenda.proposal_violations(p)) for p in added]
bad = [(i, v) for i, v in bad if v]
if bad:
    for i, v in bad: print(f"  RULE VIOLATION {i}: {v}")
    raise SystemExit("refusing to add rule-breaking proposals")
d["proposals"].extend(added); d["generated_at"] = NOW
DOCKET.write_text(json.dumps(d, indent=1) + "\n")
for p in added: print(f"  + {p['id']:38s} {p['est_core_min']:5.0f} core-min")
print(f"\n  docket now {len(d['proposals'])} proposals, all passing the text rules")
