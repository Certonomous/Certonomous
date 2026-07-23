"""Monte-Carlo uncertainty propagation over real solver runs.

Every sample here is an actual OpenFOAM solve: the freestream condition is
drawn from its stated distribution, a case is generated and solved, and the
resulting coefficient enters the ensemble.  Nothing is emulated.

The quantity the chief reports is the **estimate of the mean** and its
standard error, because that is the part of the uncertainty sampling can
reduce: the ensemble spread reflects the physical input uncertainty (it does
not shrink with N), while the standard error of the mean falls as 1/sqrt(N).
Lesson L-001 is exactly this distinction — keep spending samples while the
estimator is still moving, and stop when what remains is the irreducible
input-driven spread.
"""

from __future__ import annotations

import math
import random
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Sequence

from .openfoam import OpenFoamCylinderApi


@dataclass
class Sample:
    index: int
    design: dict[str, float]
    metrics: dict[str, float]
    seconds: float
    error: str | None = None


@dataclass
class EnsembleResult:
    metric: str
    samples: list[Sample]
    values: list[float]
    mean: float
    ensemble_sigma: float          # physical spread — does not shrink with N
    standard_error: float          # estimator uncertainty — shrinks as 1/sqrt(N)
    ci95: tuple[float, float]
    wall_seconds: float
    workers: int

    @property
    def n(self) -> int:
        return len(self.values)

    @property
    def relative_error(self) -> float:
        return abs(2 * self.standard_error / self.mean) if self.mean else float("inf")

    def as_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric, "n": self.n, "mean": self.mean,
            "ensemble_sigma": self.ensemble_sigma,
            "standard_error": self.standard_error,
            "ci95": list(self.ci95), "relative_error": self.relative_error,
            "wall_seconds": self.wall_seconds, "workers": self.workers,
        }

    def headline(self) -> str:
        return (
            f"{self.metric} = {self.mean:.4g} ± {2 * self.standard_error:.2g} "
            f"(95% CI [{self.ci95[0]:.4g}, {self.ci95[1]:.4g}], n={self.n}, "
            f"{self.relative_error * 100:.1f}% of value)"
        )


def running_statistics(values: Sequence[float]) -> dict[str, list[float]]:
    """Running mean and ±2·SEM band — the envelope that tightens with N."""
    means, los, his, sems = [], [], [], []
    total = 0.0
    total_sq = 0.0
    for index, value in enumerate(values, start=1):
        total += value
        total_sq += value * value
        mean = total / index
        if index > 1:
            variance = max(0.0, (total_sq - index * mean * mean) / (index - 1))
            sem = math.sqrt(variance / index)
        else:
            sem = 0.0
        means.append(mean); sems.append(sem)
        los.append(mean - 2 * sem); his.append(mean + 2 * sem)
    return {"n": list(range(1, len(values) + 1)), "mean": means,
            "lo": los, "hi": his, "sem": sems}


def run_ensemble(nominal: dict[str, float],
                 uncertain: dict[str, float],
                 *, n: int, workers: int, work_root: str | Path,
                 run_prefix: Sequence[str], metric: str = "Cd",
                 seed: int | None = None,
                 on_sample: Callable[[Sample], None] | None = None,
                 emit: Callable[[str, dict], None] | None = None,
                 label: str = "mc") -> EnsembleResult:
    """Draw ``n`` designs, solve each for real, return the ensemble statistics.

    ``uncertain`` maps a parameter name to the standard deviation of its
    (normal) distribution: the physical input uncertainty being propagated.

    When ``emit`` is given, each completed sample streams a ``trace.point`` with
    the running mean and its ±2·SEM band, so the estimate and its envelope form
    (and tighten) live on screen sample by sample (#7).
    """
    import time

    # A fresh draw each run: a Monte-Carlo estimate that returns identical
    # samples every time is not sampling. Pass an explicit seed to reproduce.
    rng = random.Random(time.time_ns() if seed is None else seed)
    designs = []
    for index in range(n):
        design = dict(nominal)
        for name, sigma in uncertain.items():
            design[name] = rng.gauss(nominal[name], sigma)
        designs.append(design)

    root = Path(work_root)
    started = time.monotonic()
    # Completion-order accumulator for the live running-mean trace. Threads
    # finish out of order; the running estimate is over samples as they land.
    _seen: list[float] = []
    _seen_lock = Lock()

    def solve(job: tuple[int, dict[str, float]]) -> Sample:
        index, design = job
        api = OpenFoamCylinderApi(root / f"{label}-{index:03d}",
                                  run_prefix=list(run_prefix), timeout_s=1200.0)
        began = time.monotonic()
        try:
            metrics = dict(api.evaluate(design, ["aerodynamics"]))
            sample = Sample(index, design, metrics, time.monotonic() - began)
        except Exception as exc:
            sample = Sample(index, design, {}, time.monotonic() - began,
                            error=f"{type(exc).__name__}: {exc}")
        if on_sample:
            on_sample(sample)
        if emit and not sample.error and metric in sample.metrics:
            with _seen_lock:
                _seen.append(sample.metrics[metric])
                k = len(_seen)
                m = sum(_seen) / k
                if k > 1:
                    var = max(0.0, sum((v - m) ** 2 for v in _seen) / (k - 1))
                    sem = math.sqrt(var / k)
                else:
                    sem = 0.0
                emit("trace.point", {
                    "series": f"{metric}_running_mean", "x": k, "y": round(m, 5),
                    "lo": round(m - 2 * sem, 5), "hi": round(m + 2 * sem, 5),
                    "x_label": "samples", "y_label": metric,
                    "title": f"{metric} running mean — envelope tightening with N",
                    "feasible": True})
        return sample

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        samples = list(pool.map(solve, enumerate(designs)))

    wall = time.monotonic() - started
    values = [s.metrics[metric] for s in samples if not s.error and metric in s.metrics]
    if not values:
        raise RuntimeError(f"no successful samples produced {metric!r}")
    mean = sum(values) / len(values)
    if len(values) > 1:
        variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        sigma = math.sqrt(variance)
        sem = sigma / math.sqrt(len(values))
    else:
        sigma = sem = 0.0
    return EnsembleResult(
        metric=metric, samples=samples, values=values, mean=mean,
        ensemble_sigma=sigma, standard_error=sem,
        ci95=(mean - 2 * sem, mean + 2 * sem), wall_seconds=wall, workers=workers,
    )


# --------------------------------------------------------------------------
# Plots — dark GUI theme (G10): every plotted quantity carries its envelope,
# labelled in typeset math ($C_d$, $\pm\sigma$), sized to span the report column.
# --------------------------------------------------------------------------

from . import plot_theme as _theme


def plot_convergence(result: EnsembleResult, out_png: str | Path,
                     *, title: str | None = None) -> str | None:
    """Running estimate with its ±2·SEM envelope, sample by sample."""
    plt = _theme._pyplot()
    if plt is None:
        return None
    label = _theme.metric_label(result.metric)
    stats = running_statistics(result.values)
    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    ax.fill_between(stats["n"], stats["lo"], stats["hi"], color=_theme.LIVE, alpha=0.18,
                    linewidth=0, label=r"$\pm 2\,$SEM — reducible floor, not a bound")
    ax.plot(stats["n"], stats["mean"], color=_theme.LIVE, linewidth=2.4,
            label=f"running mean {label}")
    ax.scatter(stats["n"], result.values, s=16, color=_theme.LIVE, alpha=0.45,
               edgecolor=_theme.INK, linewidth=0.4, zorder=3,
               label="individual solver runs")
    ax.annotate(result.headline(), xy=(stats["n"][-1], stats["mean"][-1]),
                xytext=(-6, 16), textcoords="offset points", ha="right",
                fontsize=10.5, color=_theme.INK, weight="bold")
    _theme.style_axes(ax, "samples (chosen solver: OpenFOAM)", label,
                      title or f"{label} — Monte-Carlo estimate with uncertainty envelope")
    leg = ax.legend(frameon=False, fontsize=9.5, labelcolor=_theme.INK, loc="lower right")
    for text in leg.get_texts():
        text.set_color(_theme.INK)
    fig.tight_layout(); fig.savefig(out_png); plt.close(fig)
    return str(out_png)


def plot_ab_comparison(run_a: EnsembleResult, run_b: EnsembleResult,
                       out_png: str | Path) -> str | None:
    """Side-by-side proof that more samples tightened the envelope."""
    plt = _theme._pyplot()
    if plt is None:
        return None
    label = _theme.metric_label(run_a.metric)
    stats_a, stats_b = running_statistics(run_a.values), running_statistics(run_b.values)
    lo = min(min(stats_a["lo"][1:] or [run_a.mean]), min(stats_b["lo"][1:] or [run_b.mean]))
    hi = max(max(stats_a["hi"][1:] or [run_a.mean]), max(stats_b["hi"][1:] or [run_b.mean]))
    pad = 0.12 * (hi - lo or 1.0)

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.7), dpi=150, sharey=True)
    for ax, stats, result, color, name in (
        (axes[0], stats_a, run_a, _theme.LIVE, "Run A"),
        (axes[1], stats_b, run_b, _theme.VALID, "Run B"),
    ):
        ax.fill_between(stats["n"], stats["lo"], stats["hi"], color=color,
                        alpha=0.18, linewidth=0)
        ax.plot(stats["n"], stats["mean"], color=color, linewidth=2.4)
        ax.scatter(stats["n"], result.values, s=14, color=color, alpha=0.45,
                   edgecolor=_theme.INK, linewidth=0.4, zorder=3)
        ax.set_ylim(lo - pad, hi + pad)
        _theme.style_axes(ax, "samples (chosen solver: OpenFOAM)", label,
                          f"{name} — n = {result.n}")
        ax.annotate(rf"$\pm${2 * result.standard_error:.2g}  "
                    f"({result.relative_error * 100:.1f}%)",
                    xy=(0.97, 0.06), xycoords="axes fraction", ha="right",
                    fontsize=11.5, color=_theme.INK, weight="bold")
    shrink = (1 - run_b.relative_error / run_a.relative_error) * 100 if run_a.relative_error else 0
    fig.suptitle(
        f"More samples, tighter estimate — the reducible envelope narrowed "
        f"{shrink:.0f}%  ({run_a.n} → {run_b.n} real solves)",
        color=_theme.INK, fontsize=13, x=0.012, ha="left", weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(out_png); plt.close(fig)
    return str(out_png)


def plot_estimates(entries, out_png, *, title: str, ylabel: str = "Cd"):
    """Compare a handful of point estimates, each with its stated band.

    ``entries`` are dicts: {label, value, band, tier}. Used where a study
    produces a small number of considered values rather than a sample stream —
    a coarse solve, a corrected value, a refinement probe.
    """
    plt = _theme._pyplot()
    if plt is None:
        return None
    if not entries:
        return None
    labels = [e["label"] for e in entries]
    values = [float(e["value"]) for e in entries]
    bands = [float(e.get("band") or 0.0) for e in entries]
    colours = [_theme.VALID if e.get("tier") == "VALIDATED" else _theme.TREND
               for e in entries]

    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    xs = list(range(len(entries)))
    for x, value, band, colour in zip(xs, values, bands, colours):
        if band:
            ax.fill_between([x - 0.28, x + 0.28], [value - band] * 2, [value + band] * 2,
                            color=colour, alpha=0.2, linewidth=0)
        ax.plot([x - 0.28, x + 0.28], [value, value], color=colour, linewidth=2.8)
        ax.annotate(f"{value:.4g}" + (rf" $\pm${band:.2g}" if band else ""),
                    xy=(x, value), xytext=(0, 12), textcoords="offset points",
                    ha="center", fontsize=11, color=_theme.INK, weight="bold")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_xlim(-0.6, len(entries) - 0.4)
    _theme.style_axes(ax, "", _theme.metric_label(ylabel), title)
    fig.tight_layout(); fig.savefig(out_png); plt.close(fig)
    return str(out_png)
