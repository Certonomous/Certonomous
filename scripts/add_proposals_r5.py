#!/usr/bin/env python3
"""Proposals r5 — drawn from today's measurements, not from speculation.

Each cites a number this lab measured today and names what would falsify it.
"""
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
NOW = "2026-07-29T22:15:00Z"

NEW = [
    {
        "id": "r5-convergence-wall-not-memory",
        "objective": (
            "Determine whether the adjoint's breakdown at around 80,000 cells is a "
            "conditioning failure that can be fixed numerically, by testing scaling, "
            "equilibration and alternative Krylov methods at the exact mesh size where "
            "breakdown first appears"
        ),
        "rationale": (
            "This supersedes the hardware question and reverses its answer. Measurement "
            "today: the adjoint completes at 63,920 cells, and at 79,560 cells it "
            "returns a breakdown from the linear solver with over 4 GB of memory "
            "headroom still unused. At 99,840 cells it breaks down the same way. So in "
            "this range the CONVERGENCE limit binds before the MEMORY limit, and buying "
            "a larger machine would not buy a larger mesh -- the opposite of what the "
            "envelope was assumed to show. That makes conditioning, not capacity, the "
            "lever. Three things make this tractable rather than speculative: the "
            "breakdown reason is reported explicitly by the linear solver rather than "
            "inferred; an earlier measurement already showed that sparsifying the "
            "preconditioner matrix and raising its lower bounds cut memory by 29.6 "
            "percent while returning a bit-identical answer, which proves this operator "
            "tolerates being reformulated; and the residual collapses to denormal range "
            "at breakdown, which is a scaling signature rather than a physics one. "
            "Falsified if breakdown survives scaling, equilibration and a restarted or "
            "flexible Krylov variant at the same mesh -- in which case the wall is "
            "structural and the hardware question returns, on a firmer basis."
        ),
        "citations": [
            "Certonomous adjoint memory envelope, Options 2 and 4 measurements, 2026-07-29",
            "Saad, Iterative Methods for Sparse Linear Systems, on breakdown and equilibration",
        ],
        "est_core_min": 150.0,
        "cost_basis": "measured, from the 960-second 79,560-cell run repeated across variants",
        "expected_knowledge_gain": (
            "Decides whether four blocked cases need a purchase or a setting. This is now "
            "the highest-leverage open question in the lab, and it replaced the question "
            "it came from because the measurement inverted the answer."
        ),
        "source_kind": "measurement",
        "status": "proposed",
        "created_at": NOW, "decided_at": None, "decision_note": None,
    },
    {
        "id": "r5-a5-second-gradient-defect",
        "objective": (
            "Identify the cause of the U-bend case's gradient failure, now known not to "
            "share the mesh-warp defect found on the airfoil, by isolating each remaining "
            "link of its derivative chain against a finite difference of that link"
        ),
        "rationale": (
            "The airfoil's shape-derivative defect was resolved today and traced to the "
            "mesh warp's own linearisation. The U-bend was then tested against the same "
            "mechanism and CLEARED: its design variables are all single-point, and its "
            "two sign-flipped components agree with a finite difference of the warp to "
            "0.32 to 1.30 percent. Yet its real verification still fails badly, at 46.6 "
            "percent aggregate with only 5 of 27 components in band, and it carries the "
            "same immunities that misled the airfoil investigation for months: a "
            "step-size sweep excludes truncation error, and tightening the primal made it "
            "worse rather than better, taking two sign flips to three. So this is a "
            "second, independent defect and nothing is known about it. The link-by-link "
            "isolation strategy is what finally worked on the airfoil after six wrong "
            "mechanisms, and it should be applied here rather than guessing again. Three "
            "features distinguish this case and are the natural first suspects: an "
            "internal duct flow rather than external aerodynamics, an objective that is a "
            "pressure difference between two patches rather than an integrated force, and "
            "a half model with a symmetry plane. A two-patch difference objective and a "
            "symmetry plane are both constructions that can carry a sign error."
        ),
        "citations": [
            "Certonomous shape-derivative root-cause study, the resolved airfoil case and the U-bend scope test, 2026-07-29",
            "Certonomous DAFoam case survey, U-bend verification record",
        ],
        "est_core_min": 60.0,
        "cost_basis": "estimate, from the U-bend's own measured 26 core-minutes per full verification cycle",
        "expected_knowledge_gain": (
            "The lab's last unexplained gradient failure. Resolving it would mean every "
            "shape derivative here is either verified or has a named, understood defect, "
            "which is the precondition for trusting any optimisation result built on them."
        ),
        "source_kind": "gate",
        "status": "proposed",
        "created_at": NOW, "decided_at": None, "decision_note": None,
    },
    {
        "id": "r5-warp-linearisation-workaround",
        "objective": (
            "Establish whether the mesh-warp linearisation defect can be avoided in "
            "practice by expressing an opposing-direction combination design variable as "
            "a weighted set of single-point variables, and whether the resulting gradient "
            "then verifies"
        ),
        "rationale": (
            "The defect is now understood in two parts, both measured: the warp's "
            "linearisation is wrong for opposing-direction combination modes wherever they "
            "occur, and whether that reaches a real gradient depends on whether the error "
            "overlaps the objective's own sensitivity field. Single-point variables never "
            "show it -- confirmed across three cases. That suggests a workaround available "
            "today, without waiting on an upstream fix: a combination mode is a linear "
            "combination of point motions, so the same shape freedom can be expressed as "
            "several single-point variables and combined afterwards, where the chain rule "
            "is ours rather than the library's. If the reconstructed gradient then agrees "
            "with a finite difference, every blocked optimisation using combination modes "
            "becomes runnable now. Falsified if the reconstruction disagrees too, which "
            "would locate the defect deeper than the mode construction and be worth "
            "knowing for the same reason."
        ),
        "citations": [
            "Certonomous mesh-warp linearisation study, necessary and sufficient conditions measured, 2026-07-29",
            "Certonomous upstream defect report on the mesh-warp derivative",
        ],
        "est_core_min": 45.0,
        "cost_basis": "measured, from the airfoil's 3.5 core-minute verification cycle across several variable constructions",
        "expected_knowledge_gain": (
            "Turns a documented upstream defect from a blocker into a known workaround, on "
            "our own schedule rather than someone else's release cycle."
        ),
        "source_kind": "capability",
        "status": "proposed",
        "created_at": NOW, "decided_at": None, "decision_note": None,
    },
    {
        "id": "r5-perturbation-destroys-its-own-measurand",
        "objective": (
            "Test whether the anisotropy-perturbation uncertainty method destroys the very "
            "quantity it is built to bound, by establishing at what perturbation magnitude "
            "the separation bubble stops being a single closing structure and whether a "
            "converged solution exists beyond that point at all"
        ),
        "rationale": (
            "Today's sweep produced a result more interesting than the curve it was meant "
            "to produce. Only two perturbation magnitudes met their convergence gate, and "
            "the larger of the two moved the reattachment point AWAY from the experiment "
            "rather than toward it. Every magnitude that moves toward the experimental "
            "value failed to converge, with severity rising in step, and the flow "
            "fragments into multiple separation and reattachment events from a magnitude "
            "of 0.10 onward. So the scalar the band is built on stops being well defined "
            "in exactly the range where the band would have to be tightened. If "
            "non-convergence and fragmentation are the same phenomenon, then tightening is "
            "not merely circular, it is unreachable, and that is a genuine intrinsic limit "
            "of the method rather than a failure of this attempt. Separation position "
            "stayed single-valued and smooth throughout, which extends the known "
            "separation-is-easy-reattachment-is-hard asymmetry from accuracy into "
            "numerical well-posedness. Distinguishing an intrinsic limit from a "
            "mesh-and-scheme artefact is the crux, because only the second is fixable."
        ),
        "citations": [
            "Certonomous hump band-tightening sweep, gate-checked points, 2026-07-29",
            "Emory, Iaccarino et al., eigenvalue perturbation and the barycentric map",
            "NASA Turbulence Modeling Resource, wall-mounted hump experiment",
        ],
        "est_core_min": 250.0,
        "cost_basis": "estimate, several hump solves at the measured case cost plus one refined-mesh variant",
        "expected_knowledge_gain": (
            "A stated limit of the uncertainty machinery, established by us before anyone "
            "else finds it. A method that cannot be tightened past the point where its own "
            "measurand dissolves is a bounded tool, and saying so is worth more than an "
            "unfalsifiable claim of generality."
        ),
        "source_kind": "challenge",
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
    for i, v in bad:
        print(f"  RULE VIOLATION {i}: {v}")
    raise SystemExit("refusing to add proposals that break the lab's own text rules")
d["proposals"].extend(added)
d["generated_at"] = NOW
DOCKET.write_text(json.dumps(d, indent=1) + "\n")
for p in added:
    print(f"  + {p['id']:40s} {p['est_core_min']:6.0f} core-min")
print(f"\n  docket now holds {len(d['proposals'])} proposals, all passing the text rules")
