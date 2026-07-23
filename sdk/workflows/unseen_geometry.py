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
        "• This geometry is not in case memory — no number will be quoted. "
        "• Retrieving the nearest cases we have actually solved.")

    matches = retrieve(
        dimensionality=target["dimensionality"], body_type=target["body_type"],
        flow=target["flow"], reynolds=target["reynolds"],
        meshing=target["meshing"], limit=3)

    for match in matches:
        script.engineer(
            f"• {match.case.name} (score {match.score:.2f}) — {match.case.results}",
            citations=(match.case.source,))

    nearest = matches[0]
    if nearest.case.name.startswith("motorbike"):
        announce_geometry(emit, name="motorBike.obj",
                          label="nearest solved case — motorBike")
    script.researcher(
        f"• Nearest neighbour: {nearest.case.name} — weak support, stated precisely. "
        f"• Shared: {', '.join(nearest.shared) or 'little'}. "
        f"• Differing: {'; '.join(nearest.differing) or 'nothing material'}.",
        citations=(nearest.case.source,))

    # ---- What transfers, what does not: stated as claims, not numbers ----
    if target["body_type"] == "streamlined":
        script.researcher(
            "• Transfers: the methodology — converged, envelope-bounded Cd "
            "on 3D external aero. "
            "• Known mesh-quality band (non-ortho 65, skew 8.94). Process confidence.",
            citations=(f"{KNOWLEDGE} #7 (motorBike benchmark)",))
        script.researcher(
            "• Does NOT transfer: the coefficient — memory is all bluff bodies. "
            "• Streamlined drag is friction-dominated; our records are pressure-dominated. "
            "• Interpolating a magnitude would be inventing evidence.",
            citations=(f"{KNOWLEDGE} #1 (cylinder benchmark, bluff)",))
        gap = ("attached-flow drag decomposition — we have never validated a "
               "skin-friction-dominated case")
        cheapest = ("a single 2D airfoil run at one angle of attack, meshed with "
                    "the same chain, checked against published section data")
    else:
        script.researcher(
            "• Transfers: the regime warning — above Re ≈ 47 steady converges "
            "onto an unphysical branch. "
            "• Cd 1.181 where the physical time-average is 1.3–1.4. "
            "• A sphere at Re 200 is the same trap, one dimension up.",
            citations=(f"{KNOWLEDGE} #3, #4 (unstable branch, degradation)",))
        script.researcher(
            "• Does NOT transfer: the 2D magnitudes. "
            "• 3D relief changes separation and shedding — neither measured.",
            citations=(f"{KNOWLEDGE} #1",))
        gap = "3D unsteady wake behaviour — no unsteady solver track exists yet"
        cheapest = ("a pimpleFoam sphere run at Re 200 with time-averaged "
                    "coefficients, compared against the standard drag correlation")

    script.engineer(
        "• Position: high confidence in the process; low in any magnitude today. "
        "• Explicit refusal to interpolate one. "
        f"• Dominant gap: {gap}.")
    script.engineer(
        f"• Cheapest gap-closer: {cheapest}. "
        f"• One solve converts opinion into a citable case-memory record.",
        citations=(f"{LESSONS_FILE} L-001",))
    script.researcher(
        "• Agreed — approve that single run before any sweep. "
        "• A sweep on an unvalidated magnitude multiplies error, not information.")

    script.save(out / "transcript.txt")
    print("\nArtifacts in", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main("sphere" if "--sphere" in sys.argv else "airfoil"))
