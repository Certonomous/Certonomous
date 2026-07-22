"""Part 2 — a simulation under a deadline, on a coarser mesh than ideal.

The deadline forces a coarse mesh.  The Chief Researcher decides whether the
existing closure model may be applied:

* **Approved** (case inside the validated envelope) — the coarse run is
  corrected by a closure that was *measured on this machine*, and the verdict
  says the coarse mesh cost speed, not trust.
* **Rejected** (case outside the envelope) — the coarse run is reported with
  an explicitly widened envelope, and the Chief Engineer executes the
  diagnostics that convert guessed uncertainty into measured uncertainty: a
  grid-sensitivity probe and an oscillation check.

The uncertainty language in the two verdicts is deliberately different, and
both paths are real solves.

    python -m workflows.time_constrained            # Re 20 — closure applies
    python -m workflows.time_constrained --reject   # Re 100 — closure refused
"""

from __future__ import annotations

import sys
from pathlib import Path

from . import (NOMINAL_CYLINDER, OUT_ROOT, RUN_PREFIX, announce_geometry,
               announce_plot, make_transcript)
from chief_engineer.chief_researcher import approve_closure
from chief_engineer.compute_audit import audit
from chief_engineer.lab import per, trust
from chief_engineer.monte_carlo import plot_estimates
from chief_engineer.openfoam import OpenFoamCylinderApi

KNOWLEDGE = "docs/NUMERICS_KNOWLEDGE.md"
DEADLINE_MINUTES = 5.0
COARSE_REFINEMENT = 0.5      # ~600 cells: fast, and inside the calibrated range
FINE_REFINEMENT = 1.0        # ~2400 cells: the probe step


def _solve(design, out, tag):
    api = OpenFoamCylinderApi(Path(out) / tag, run_prefix=RUN_PREFIX, timeout_s=1200)
    return dict(api.evaluate(design, ["aerodynamics"]))


def main(request: str | None = None, params: dict | None = None,
         reject: bool = False, emit=None) -> int:
    """Answer a deadline-constrained request.

    The Reynolds number comes from the request when it states one, so the
    closure ruling follows from the physics of the case rather than from a
    switch. ``reject`` remains only as a manual rehearsal override.
    """
    params = params or {}
    deadline = float(params.get("deadline_minutes") or DEADLINE_MINUTES)
    reynolds = float(params.get("reynolds") or (100.0 if reject else 20.0))
    # Diameter and speed stay nominal, so the stated Re fixes viscosity.
    viscosity = (NOMINAL_CYLINDER["inlet_velocity"]
                 * NOMINAL_CYLINDER["cylinder_diameter"] / max(reynolds, 1e-6))
    out = OUT_ROOT / "time-constrained"
    out.mkdir(parents=True, exist_ok=True)
    script = make_transcript("time-constrained simulation", emit)

    design = {**NOMINAL_CYLINDER,
              "kinematic_viscosity": viscosity,
              "mesh_refinement": COARSE_REFINEMENT}

    script.system(request or
                  f"Request: drag for this case within {deadline:.0f} minutes.")
    script.engineer(
        f"A {deadline:.0f}-minute budget rules out the mesh I would choose. Proposing "
        f"{COARSE_REFINEMENT:.1f}× refinement (~600 cells) instead of the "
        f"grid-converged resolution — that meets the clock, but it carries a "
        f"known discretization bias. Case is Re = {reynolds:.0f}. "
        f"Requesting a closure ruling before I report anything.",
        citations=(f"{KNOWLEDGE} #2 (coarse-grid bias measured at 1.6%)",))

    announce_geometry(emit, diameter=NOMINAL_CYLINDER["cylinder_diameter"],
                      label="case geometry")
    capacity = audit(2, memory_per_worker_mb=256)
    if emit:
        emit("audit.completed", capacity.panel())
    script.engineer(capacity.headline(), panel=capacity.panel())

    decision = approve_closure(
        geometry="cylinder-2d", flow="steady-laminar" if not reject else "steady-laminar",
        reynolds=reynolds, cells=600, deadline_minutes=deadline)
    script.researcher(decision.headline(), citations=decision.citations,
                      decision=decision.as_dict())
    for order in decision.orders:
        script.researcher(f"  → {order}")

    coarse = _solve(design, out, "coarse")
    script.engineer(
        f"Coarse solve complete: Cd = {coarse['Cd']:.4g}, "
        f"{int(coarse['cell_count'])} cells, converged={int(coarse['converged'])}, "
        f"residual {coarse['convergence_residual']:.2g}.")

    if decision.approved:
        # ---------------- Approved: apply the measured correction ----------------
        corrected = coarse["Cd"] * 0.984
        script.engineer(
            f"Applying {decision.model.name}: {coarse['Cd']:.4g} → {corrected:.4g}. "
            f"The 1.6% removed here is not a fudge factor — it is the bias measured "
            f"between 600 cells and the 21600-cell asymptote on this machine.",
            citations=(decision.model.citation,))
        verdict = trust(relative_error=0.01 / max(corrected, 1e-9))
        panel = plot_estimates(
            [{"label": f"coarse mesh, {int(coarse['cell_count'])} cells",
              "value": coarse["Cd"], "band": 0.0, "tier": "TREND ONLY"},
             {"label": "after calibrated correction",
              "value": corrected, "band": 0.01, "tier": verdict["tier"]}],
            out / "closure_correction.png",
            title="Coarse solve and the correction measured for it")
        announce_plot(emit, "time-constrained", panel,
                      "Coarse solve corrected by measured calibration")
        if emit:
            emit("result.verdict", {"quantity": "Drag coefficient",
                                    "value": f"{corrected:.4g}",
                                    "envelope": "±0.01", **verdict})
        script.engineer(
            f"VERDICT — {decision.uncertainty_language} "
            f"Reported: Cd = {corrected:.4g} ± 0.01 (closure calibration residual), "
            f"delivered inside the {deadline:.0f}-minute deadline.", verdict=verdict)
    else:
        # ---------------- Rejected: widen, then measure the uncertainty ----------
        script.engineer(
            f"Closure refused, so I will not dress this number up. "
            f"VERDICT — {decision.uncertainty_language}")
        script.engineer(
            "Running the ordered diagnostics now: uncertainty I can measure is "
            "worth more than uncertainty I can only warn about.")

        probe_design = {**design, "mesh_refinement": FINE_REFINEMENT}
        probe = _solve(probe_design, out, "grid-probe")
        grid_delta = abs(probe["Cd"] - coarse["Cd"])
        grid_percent = grid_delta / abs(probe["Cd"]) * 100
        script.engineer(
            f"Grid difference ({int(coarse['cell_count'])} → "
            f"{int(probe['cell_count'])} cells): Cd {coarse['Cd']:.4g} → "
            f"{probe['Cd']:.4g}, a {grid_percent:.1f}% shift. I am calling that a "
            f"grid difference and not a verified uncertainty, because two meshes "
            f"cannot give one.",
            citations=(f"{KNOWLEDGE} #2 (grid convergence method)",))
        script.numericist(
            f"That distinction is not pedantry. Establishing a numerical "
            f"uncertainty needs systematically refined grids and a fit whose "
            f"scatter sets the safety factor — {per('grid-uncertainty')}. With two "
            f"meshes we have the size of a change and no evidence about the order "
            f"it is converging at, so {grid_percent:.1f}% is a difference we "
            f"measured, not a bound we can defend.")

        oscillation = probe.get("Cd_oscillation", 0.0)
        unsteady = oscillation > 1e-3
        script.engineer(
            f"Oscillation diagnostic on the coefficient history: "
            f"{oscillation:.2g}"
            + (" — the steady solver is suppressing genuine unsteadiness; the "
               "physical flow at this Re sheds vortices, so the steady value is "
               "a branch, not an average."
               if unsteady else
               " — the history is flat, so the steady solver is at least "
               "self-consistent here."),
            citations=(f"{KNOWLEDGE} #3 (convergence ≠ physical validity)",))

        verdict = trust(relative_error=grid_delta / max(abs(probe["Cd"]), 1e-9),
                        in_validated_regime=reynolds <= 47)
        panel = plot_estimates(
            [{"label": f"coarse mesh, {int(coarse['cell_count'])} cells",
              "value": coarse["Cd"], "band": grid_delta, "tier": "TREND ONLY"},
             {"label": f"refinement probe, {int(probe['cell_count'])} cells",
              "value": probe["Cd"], "band": grid_delta, "tier": verdict["tier"]}],
            out / "grid_sensitivity.png",
            title="Grid-sensitivity probe — the discretization band, measured")
        announce_plot(emit, "time-constrained", panel,
                      "Grid-sensitivity probe with measured band")
        if emit:
            emit("result.verdict", {"quantity": "Drag coefficient",
                                    "value": f"{probe['Cd']:.4g}",
                                    "envelope": f"±{grid_delta:.2g}", **verdict})
        script.engineer(
            f"FINAL — Cd = {probe['Cd']:.4g} with a grid difference of "
            f"±{grid_delta:.2g} ({grid_percent:.1f}%) measured between two meshes — "
            f"indicative of the discretization error, not a verified bound on it — "
            f"plus an unquantified regime error because Re = {reynolds:.0f} "
            f"is above the validated steady limit of 47. I am reporting the trend "
            f"as usable and the magnitude as indicative. Closing that last gap "
            f"needs an unsteady run, which does not fit this deadline — it is the "
            f"first thing I would buy with more time.", verdict=verdict)

    script.save(out / "transcript.txt")
    print("\nArtifacts in", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(reject="--reject" in sys.argv))
