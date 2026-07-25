"""Variance-based global sensitivity — Sobol indices as a lab primitive.

Answers the question the Monte-Carlo envelopes leave open: the lab propagates
stated input spreads through a model and reports one spread out, but never says
WHICH input owns the variance, so uncertainty-reduction effort is untargeted.
Sobol decomposition apportions the output variance across the inputs: the MAIN
(first-order) index is the variance share an input explains alone, the TOTAL
index is its share including every interaction it touches. The gap between the
two is interaction; an input whose total index is small can be frozen at its
nominal value without moving the envelope.

Estimator: the pick-and-freeze (Saltelli) scheme over two independent base
sample matrices A and B of ``n_base`` rows each, plus the M column-swapped
matrices AB_i (A with column i taken from B) — cost ``n_base * (M + 2)`` model
evaluations for M inputs. Index estimators are the standard ones:

* main   S_i = mean( f(B) * (f(AB_i) - f(A)) ) / V       (Saltelli et al. 2010)
* total  T_i = mean( (f(A) - f(AB_i))^2 ) / (2 V)        (Jansen 1999)

with V the variance of the pooled A and B evaluations. Confidence intervals
come from a percentile bootstrap over the base-sample rows. Everything is
deterministic given ``seed``: same seed, same draws, same bootstrap, same
numbers to the last digit.

This module is a PURE primitive: a callable model in, indices out. It touches
no workflow, no surface, no router intent. Its offline evidence (per the
Innovation Standard) runs through ``scripts/run_sobol_evidence.py`` on the
valve screen's loss model, the airliner sizing chain, and the closed-form
Ishigami benchmark whose true indices are known analytically.

Basis: Dakota Theory Manual (Sandia), variance-based decomposition section;
Saltelli et al., "Variance based sensitivity analysis of model output", 2010;
Jansen, "Analysis of variance designs for model output", 1999.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

# A sampler draws one input value from that input's distribution using the
# supplied RNG (the primitive owns the RNG so the whole study is seedable).
Sampler = Callable[[random.Random], float]


# --------------------------------------------------------------------------
# Input distributions (the two the lab's stated spreads actually use)
# --------------------------------------------------------------------------

def normal_input(mean: float, sigma: float) -> Sampler:
    """Gaussian input — the airliner act's stated-spread convention."""
    return lambda rng: rng.gauss(mean, sigma)


def uniform_input(lo: float, hi: float) -> Sampler:
    """Uniform on [lo, hi] — the Ishigami benchmark's convention."""
    return lambda rng: rng.uniform(lo, hi)


def uniform_sigma_input(mean: float, sigma: float) -> Sampler:
    """Bounded uniform with a MATCHING 1-sigma — the valve envelope's
    convention (its low-discrepancy sweep spans mean +- sigma*sqrt(3))."""
    half = sigma * math.sqrt(3.0)
    return lambda rng: rng.uniform(mean - half, mean + half)


# --------------------------------------------------------------------------
# Result record
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class SobolIndices:
    """Main and total Sobol indices with bootstrap CIs, one entry per input."""

    names: tuple[str, ...]
    main: tuple[float, ...]            # first-order indices S_i
    total: tuple[float, ...]           # total-effect indices T_i
    main_ci: tuple[tuple[float, float], ...]    # percentile bootstrap CIs
    total_ci: tuple[tuple[float, float], ...]
    mean: float                        # pooled output mean over A and B
    variance: float                    # pooled output variance (the V above)
    n_base: int
    n_evaluations: int                 # n_base * (M + 2), every one performed
    seed: int
    ci_level: float

    def ranking(self) -> list[tuple[str, float, float]]:
        """Inputs ordered by main index, largest variance share first."""
        rows = list(zip(self.names, self.main, self.total))
        return sorted(rows, key=lambda r: r[1], reverse=True)

    def identity_report(self, slack: float | None = None) -> dict[str, bool]:
        """Do the Sobol identities hold, within CI slack?

        Checks, per input: index within [0, 1] and main <= total; globally:
        sum of mains <= 1. ``slack`` widens each check by the half-width of
        the widest relevant bootstrap CI when None (sampling noise must not
        fail an identity the estimator satisfies in expectation).
        """
        def half_width(ci: tuple[float, float]) -> float:
            return (ci[1] - ci[0]) / 2.0

        report: dict[str, bool] = {}
        for i, name in enumerate(self.names):
            eps = slack if slack is not None else max(
                half_width(self.main_ci[i]), half_width(self.total_ci[i]))
            report[f"{name}: main in [0,1]"] = (
                -eps <= self.main[i] <= 1.0 + eps)
            report[f"{name}: total in [0,1]"] = (
                -eps <= self.total[i] <= 1.0 + eps)
            report[f"{name}: main <= total"] = (
                self.main[i] <= self.total[i] + eps)
        eps_sum = slack if slack is not None else sum(
            half_width(ci) for ci in self.main_ci)
        report["sum of mains <= 1"] = sum(self.main) <= 1.0 + eps_sum
        return report


# --------------------------------------------------------------------------
# The estimator
# --------------------------------------------------------------------------

def _as_named_samplers(
        dists: Sequence[Sampler] | Mapping[str, Sampler],
) -> tuple[tuple[str, ...], tuple[Sampler, ...]]:
    if isinstance(dists, Mapping):
        names = tuple(str(k) for k in dists.keys())
        samplers = tuple(dists[k] for k in dists.keys())
    else:
        samplers = tuple(dists)
        names = tuple(f"x{i + 1}" for i in range(len(samplers)))
    if not samplers:
        raise ValueError("sobol_indices needs at least one input distribution")
    return names, samplers


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs)


def _variance(xs: Sequence[float]) -> float:
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)


def _indices_from_rows(f_a: Sequence[float], f_b: Sequence[float],
                       f_ab: Sequence[Sequence[float]],
                       rows: Sequence[int]) -> tuple[list[float], list[float]]:
    """Saltelli mains and Jansen totals over a chosen subset of base rows
    (the full range for the point estimate, resampled rows for bootstrap)."""
    pooled = [f_a[r] for r in rows] + [f_b[r] for r in rows]
    v = _variance(pooled)
    if v <= 0.0:
        raise ValueError(
            "output variance is zero over the base sample; Sobol indices "
            "are undefined for a constant model")
    # Center on the pooled mean before forming the Saltelli product: the
    # estimator is unbiased either way, but with a raw output whose mean
    # dwarfs its spread (a pressure loss in the thousands of Pa varying a
    # few percent) the uncentered product's variance is dominated by the
    # mean and the main indices drown in noise.
    mu = _mean(pooled)
    n = len(rows)
    mains, totals = [], []
    for f_abi in f_ab:
        mains.append(
            sum((f_b[r] - mu) * (f_abi[r] - f_a[r]) for r in rows) / n / v)
        totals.append(
            sum((f_a[r] - f_abi[r]) ** 2 for r in rows) / (2.0 * n) / v)
    return mains, totals


def sobol_indices(model: Callable[..., float],
                  dists: Sequence[Sampler] | Mapping[str, Sampler],
                  n_base: int = 256,
                  seed: int = 0,
                  *,
                  bootstrap: int = 200,
                  ci_level: float = 0.95) -> SobolIndices:
    """Main and total Sobol indices of ``model`` under the input ``dists``.

    ``model`` is called as ``model(x1, ..., xM)`` and must return a float;
    ``dists`` is a sequence of samplers (inputs named x1..xM) or a mapping
    name -> sampler (order preserved, names carried into the result). Cost is
    exactly ``n_base * (M + 2)`` model evaluations. Deterministic given
    ``seed`` — draws and bootstrap both derive from it.
    """
    names, samplers = _as_named_samplers(dists)
    if n_base < 2:
        raise ValueError("n_base must be at least 2")
    m = len(samplers)

    rng = random.Random(seed)
    a = [[s(rng) for s in samplers] for _ in range(n_base)]
    b = [[s(rng) for s in samplers] for _ in range(n_base)]

    f_a = [float(model(*row)) for row in a]
    f_b = [float(model(*row)) for row in b]
    f_ab: list[list[float]] = []
    for i in range(m):
        rows = [a_row[:i] + [b_row[i]] + a_row[i + 1:]
                for a_row, b_row in zip(a, b)]
        f_ab.append([float(model(*row)) for row in rows])

    all_rows = range(n_base)
    mains, totals = _indices_from_rows(f_a, f_b, f_ab, list(all_rows))
    pooled = f_a + f_b

    # Percentile bootstrap over base-sample rows, derived deterministically
    # from the same seed (fixed arithmetic, no string hashing — str hashes
    # are salted per process and would break run-to-run determinism).
    boot_rng = random.Random(seed * 1000003 + 0x5EED)
    boot_mains: list[list[float]] = [[] for _ in range(m)]
    boot_totals: list[list[float]] = [[] for _ in range(m)]
    for _ in range(max(0, bootstrap)):
        rows = [boot_rng.randrange(n_base) for _ in range(n_base)]
        try:
            bm, bt = _indices_from_rows(f_a, f_b, f_ab, rows)
        except ValueError:      # a degenerate resample proves nothing
            continue
        for i in range(m):
            boot_mains[i].append(bm[i])
            boot_totals[i].append(bt[i])

    def percentile_ci(values: list[float], point: float) -> tuple[float, float]:
        if not values:
            return (point, point)
        ordered = sorted(values)
        tail = (1.0 - ci_level) / 2.0
        lo = ordered[min(len(ordered) - 1, int(tail * len(ordered)))]
        hi = ordered[min(len(ordered) - 1, int((1.0 - tail) * len(ordered)))]
        return (lo, hi)

    return SobolIndices(
        names=names,
        main=tuple(mains),
        total=tuple(totals),
        main_ci=tuple(percentile_ci(boot_mains[i], mains[i]) for i in range(m)),
        total_ci=tuple(percentile_ci(boot_totals[i], totals[i]) for i in range(m)),
        mean=_mean(pooled),
        variance=_variance(pooled),
        n_base=n_base,
        n_evaluations=n_base * (m + 2),
        seed=seed,
        ci_level=ci_level,
    )


# --------------------------------------------------------------------------
# Analytic benchmark: the Ishigami function (true indices in closed form)
# --------------------------------------------------------------------------

ISHIGAMI_A = 7.0
ISHIGAMI_B = 0.1


def ishigami_model(x1: float, x2: float, x3: float,
                   a: float = ISHIGAMI_A, b: float = ISHIGAMI_B) -> float:
    """f = sin(x1) + a sin^2(x2) + b x3^4 sin(x1), inputs U(-pi, pi)."""
    return math.sin(x1) + a * math.sin(x2) ** 2 + b * x3 ** 4 * math.sin(x1)


def ishigami_true_indices(a: float = ISHIGAMI_A, b: float = ISHIGAMI_B) -> dict:
    """Closed-form Sobol indices of the Ishigami function (standard result)."""
    pi = math.pi
    v1 = 0.5 * (1.0 + b * pi ** 4 / 5.0) ** 2
    v2 = a ** 2 / 8.0
    v13 = b ** 2 * pi ** 8 * (1.0 / 18.0 - 1.0 / 50.0)
    v = v1 + v2 + v13
    return {
        "variance": v,
        "main": (v1 / v, v2 / v, 0.0),
        "total": ((v1 + v13) / v, v2 / v, v13 / v),
    }


def ishigami_dists() -> dict[str, Sampler]:
    pi = math.pi
    return {"x1": uniform_input(-pi, pi),
            "x2": uniform_input(-pi, pi),
            "x3": uniform_input(-pi, pi)}
