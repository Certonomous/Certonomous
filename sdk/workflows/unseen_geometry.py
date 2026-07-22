"""Part 3 — the chiefs reason about a geometry nobody has run.

This beat produces **no numbers for the new geometry**, and that is the point.
The chiefs retrieve the real cases Certonomous has actually solved, state
explicitly what transfers (trends, methodology) and what does not (magnitudes),
put a confidence bound on the extrapolation, and name the single cheapest run
that would close the largest gap.

Every case cited is a real record in ``chief_engineer/case_memory.py``, backed
by runs recorded in ``docs/NUMERICS_KNOWLEDGE.md``.  No interpolated
coefficient is ever reported.

    python -m workflows.unseen_geometry
    python -m workflows.unseen_geometry --sphere
"""

from __future__ import annotations

import sys

from . import OUT_ROOT, announce_geometry, make_transcript
from chief_engineer.case_memory import retrieve

KNOWLEDGE = "docs/NUMERICS_KNOWLEDGE.md"
LESSONS_FILE = "sdk/introspection/recipe/memory/LESSONS.md"


TARGETS = {
    "airfoil": dict(
        label="a streamlined 3D wing section (NACA-type airfoil) at Re ≈ 5×10⁵",
        dimensionality="3d", body_type="streamlined", flow="steady-turbulent",
        reynolds=5.0e5, meshing="snappyHexMesh",
    ),
    "sphere": dict(
        label="a sphere at Re ≈ 200",
        dimensionality="3d", body_type="bluff", flow="unsteady",
        reynolds=200.0, meshing="snappyHexMesh",
    ),
}


def main(request: str | None = None, params: dict | None = None,
         target_key: str = "airfoil", emit=None) -> int:
    params = params or {}
    named = str(params.get("geometry") or target_key).lower()
    # Sphere-like bluff bodies get the unsteady-regime discussion; every
    # other unseen shape is treated as the streamlined case.
    target_key = named if named in TARGETS else (
        "sphere" if "sphere" in named else "airfoil")
    out = OUT_ROOT / "unseen-geometry"
    out.mkdir(parents=True, exist_ok=True)
    target = TARGETS[target_key]
    script = make_transcript(f"part 3 — unseen geometry ({target_key})", emit)

    script.system(request or
                  f"Request: what drag should I expect for {target['label']}? "
                  f"We have never run this geometry.")
    script.engineer(
        "Before I quote anything: this geometry is not in case memory. I can "
        "either run it, or tell you what our existing evidence does and does not "
        "support. Retrieving the nearest cases we have actually solved.")

    matches = retrieve(
        dimensionality=target["dimensionality"], body_type=target["body_type"],
        flow=target["flow"], reynolds=target["reynolds"],
        meshing=target["meshing"], limit=3)

    for match in matches:
        script.engineer(
            f"  · {match.case.name} (score {match.score:.2f}) — {match.case.results}",
            citations=(match.case.source,))

    nearest = matches[0]
    if nearest.case.name.startswith("motorbike"):
        announce_geometry(emit, name="motorBike.obj",
                          label="nearest solved case — motorBike")
    script.researcher(
        f"Nearest neighbour is {nearest.case.name}, and I want to be precise about "
        f"why that is weak support. Shared: {', '.join(nearest.shared) or 'little'}. "
        f"Differing: {'; '.join(nearest.differing) or 'nothing material'}.",
        citations=(nearest.case.source,))

    # ---- What transfers, what does not: stated as claims, not numbers ----
    if target["body_type"] == "streamlined":
        script.researcher(
            "What transfers: the methodology, not the magnitude. From "
            "motorbike-3d-turbulent we know our snappyHexMesh + simpleFoam chain "
            "produces a converged, envelope-bounded Cd on a 3D external-aero body "
            "at this kind of Reynolds number, and we know the mesh-quality band it "
            "lands in (non-orthogonality 65, skewness 8.94). That is process "
            "confidence.",
            citations=(f"{KNOWLEDGE} #7 (motorBike benchmark)",))
        script.researcher(
            "What does NOT transfer: the coefficient itself. Every case in memory "
            "is a bluff body — flow that separates by geometry. A streamlined "
            "section keeps its boundary layer attached over most of the chord, so "
            "its drag is dominated by skin friction rather than pressure. Our "
            "records give no basis for the magnitude; quoting a number "
            "interpolated from bluff-body data would be inventing evidence.",
            citations=(f"{KNOWLEDGE} #1 (cylinder benchmark, bluff)",))
        gap = ("attached-flow drag decomposition — we have never validated a "
               "skin-friction-dominated case")
        cheapest = ("a single 2D airfoil run at one angle of attack, meshed with "
                    "the same chain, checked against published section data")
    else:
        script.researcher(
            "What transfers: the regime warning. cylinder-2d-past-regime is the "
            "directly relevant record — above Re ≈ 47 our steady solver converged "
            "onto a branch the physical flow does not follow, giving Cd 1.181 "
            "where the physical time-average is 1.3–1.4. A sphere at Re 200 is in "
            "the same trap, one dimension up.",
            citations=(f"{KNOWLEDGE} #3, #4 (unstable branch, degradation)",))
        script.researcher(
            "What does NOT transfer: the 2D magnitudes. Three-dimensional relief "
            "changes both the separation topology and the shedding mode, and we "
            "have measured neither.",
            citations=(f"{KNOWLEDGE} #1",))
        gap = "3D unsteady wake behaviour — no unsteady solver track exists yet"
        cheapest = ("a pimpleFoam sphere run at Re 200 with time-averaged "
                    "coefficients, compared against the standard drag correlation")

    script.engineer(
        f"Then my honest position is: high confidence in the *process* (our chain "
        f"meshes, solves, and reports this class of case with measured envelopes), "
        f"low confidence in any *magnitude* I could state today, and an explicit "
        f"refusal to interpolate one. The dominant gap is {gap}.")
    script.engineer(
        f"Cheapest run that closes the most gap: {cheapest}. That is one solve, "
        f"and it converts this conversation from opinion into a case-memory "
        f"record we can cite next time — which is exactly how every entry we just "
        f"retrieved got here.",
        citations=(f"{LESSONS_FILE} L-001",))
    script.researcher(
        "Agreed. Approve that single run before any sweep is scoped: a sweep "
        "built on an unvalidated magnitude would multiply the error, not the "
        "information.")

    script.save(out / "transcript.txt")
    print("\nArtifacts in", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main("sphere" if "--sphere" in sys.argv else "airfoil"))
