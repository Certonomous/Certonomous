"""Two live ensembles: quantify the envelope, then close what sampling can close.

Run A spends a deliberately small sample budget and produces a wide envelope.
The Chief judges the uncertainty reducible and orders more samples.  Run B spends the larger budget and the envelope
visibly tightens; the verdict then separates what sampling fixed (the
estimator's standard error) from what it cannot (the physical input spread),
and declares the remainder irreducible.

Both runs are real OpenFOAM ensembles executed back to back.

    python -m workflows.uncertainty_reduction       # 5 -> 40 samples (~75 s)
    python -m workflows.uncertainty_reduction 4 24  # custom budgets
"""

from __future__ import annotations

import sys
from pathlib import Path

from . import (NOMINAL_CYLINDER, OUT_ROOT, RUN_PREFIX, announce_geometry,
               announce_plot, make_transcript)
from chief_engineer.compute_audit import audit
from chief_engineer.lessons import chip, express
from chief_engineer.monte_carlo import (
    plot_ab_comparison,
    plot_convergence,
    run_ensemble,
)

LESSON = "L-001"
LESSONS_FILE = "sdk/introspection/recipe/memory/LESSONS.md"
KNOWLEDGE = "docs/NUMERICS_KNOWLEDGE.md"
# The estimator is considered converged when 2·SEM is within this fraction of
# the mean; below it, further sampling buys precision we would not act on.
TARGET_RELATIVE = 0.010
# Physical uncertainty being propagated: 8% (1 sigma) on the freestream speed.
INLET_SIGMA = 0.08


def main(request: str | None = None, params: dict | None = None,
         n_a: int = 5, n_b: int = 40, workers: int = 8, emit=None) -> int:
    params = params or {}
    out = OUT_ROOT / "uncertainty-reduction"
    out.mkdir(parents=True, exist_ok=True)
    script = make_transcript("uncertainty reduction", emit)

    script.system(request or
        f"Request: report drag for the validated cylinder case with a "
        f"freestream uncertainty of {INLET_SIGMA * 100:.0f}% (1σ) on inlet velocity. "
        f"Every sample below is a real OpenFOAM solve.")

    announce_geometry(emit, diameter=NOMINAL_CYLINDER["cylinder_diameter"],
                      label="case geometry")
    capacity = audit(workers, memory_per_worker_mb=256)
    if emit:
        emit("audit.completed", capacity.panel())
    script.engineer(capacity.headline(), panel=capacity.panel())
    workers = max(1, min(workers, capacity.capacity))

    # ---------------- Run A ----------------
    script.engineer(
        f"• Starting small: {n_a} samples across {workers} workers. "
        f"• Cheap to be wrong about — the envelope says if it was enough.")
    run_a = run_ensemble(
        NOMINAL_CYLINDER, {"inlet_velocity": INLET_SIGMA},
        n=n_a, workers=workers, work_root=out / "run-a",
        run_prefix=RUN_PREFIX, metric="Cd", label="a")
    plot_a = plot_convergence(run_a, out / "run_a_envelope.png",
                              title=f"Run A — {run_a.n} samples")
    announce_plot(emit, "uncertainty-reduction", plot_a, f"First pass — {run_a.n} samples")
    script.engineer(
        f"• Run A — {run_a.wall_seconds:.0f} s. • {run_a.headline()}",
        result=run_a.as_dict())

    reducible = run_a.relative_error > TARGET_RELATIVE
    if reducible:
        script.engineer(
            express(LESSON, metric=run_a.metric, relative=run_a.relative_error,
                    threshold=TARGET_RELATIVE, current_n=run_a.n, proposed_n=n_b),
            citations=(f"{LESSONS_FILE} {LESSON}",),
            lesson=chip(LESSON), reducible=True)
    else:
        script.engineer(
            f"• Envelope already inside the {TARGET_RELATIVE * 100:.0f}% threshold. "
            f"• Running the larger ensemble anyway — the scaling stays visible.",
            citations=(f"{LESSONS_FILE} {LESSON}",), lesson=chip(LESSON))

    # ---------------- Run B ----------------
    run_b = run_ensemble(
        NOMINAL_CYLINDER, {"inlet_velocity": INLET_SIGMA},
        n=n_b, workers=workers, work_root=out / "run-b",
        run_prefix=RUN_PREFIX, metric="Cd", label="b")
    plot_b = plot_convergence(run_b, out / "run_b_envelope.png",
                              title=f"Run B — {run_b.n} samples")
    announce_plot(emit, "uncertainty-reduction", plot_b, f"Second pass — {run_b.n} samples")
    script.engineer(
        f"• Run B — {run_b.wall_seconds:.0f} s. • {run_b.headline()}",
        result=run_b.as_dict())

    comparison = plot_ab_comparison(run_a, run_b, out / "uncertainty_ab_panel.png")
    announce_plot(emit, "uncertainty-reduction", comparison, "Before and after additional sampling")
    shrink = (1 - run_b.relative_error / run_a.relative_error) * 100 if run_a.relative_error else 0.0
    verdict = "irreducible" if run_b.relative_error <= TARGET_RELATIVE else "still reducible"
    script.engineer(
        f"• Envelope {run_a.relative_error * 100:.1f}% → {run_b.relative_error * 100:.1f}% "
        f"({shrink:.0f}% tighter) for {run_b.n - run_a.n} extra solves. "
        f"• Estimator error shrank; physical spread ±{run_b.ensemble_sigma:.3g} "
        f"cannot — it is the {INLET_SIGMA * 100:.0f}% input propagating. "
        f"• Remaining estimator uncertainty: {verdict}.",
        citations=(f"{LESSONS_FILE} {LESSON}", f"{KNOWLEDGE} #1 (validated cylinder benchmark)"),
        lesson=chip(LESSON))
    script.engineer(
        f"• Cd = {run_b.mean:.4g} ± {2 * run_b.standard_error:.2g} (95% on the mean). "
        f"• Irreducible physical spread ±{2 * run_b.ensemble_sigma:.2g} at 95%. "
        f"• Both numbers travel with the answer.")

    script.save(out / "transcript.txt")
    for label, path in (("Run A", plot_a), ("Run B", plot_b), ("A/B panel", comparison)):
        if path:
            script.system(f"{label} plot: {Path(path).name}")
    print("\nArtifacts in", out)
    return 0


if __name__ == "__main__":
    args = [int(value) for value in sys.argv[1:3]] or [5, 40]
    raise SystemExit(main(n_a=args[0], n_b=args[1]))
