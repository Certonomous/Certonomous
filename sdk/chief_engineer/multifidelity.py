"""Multifidelity Monte Carlo (MFMC) — control-variate fusion as pure math.

The race act runs the same designs through two lanes — a cheap reduced-order
surrogate and real VSPAERO solves — then keeps only the winner's answer and
discards the pairing. MFMC is the estimator that USES the pairing: the cheap
model becomes a control variate for the expensive one, the measured
correlation ``rho`` between the paired lanes and the measured cost ratio
``w = cost_hi / cost_lo`` decide the optimal sample split analytically, and
the same two numbers decide honestly whether fusion pays at all.

Two-model MFMC (survey notation, high-fidelity model 1, low-fidelity model 2):

* control-variate coefficient  alpha* = rho * sigma_hi / sigma_lo
                                      = cov(hi, lo) / var(lo)
* optimal low/high sample ratio  r* = sqrt( rho^2 / (1 - rho^2) * w )
* estimator  y = mean_n(hi) + alpha * ( mean_N(lo) - mean_n(lo) ),
  n high-fidelity solves, N = r*n cheap evaluations, UNBIASED for E[hi]
  for any alpha (the two low-fidelity means share no systematic offset).
* variance at equal budget, relative to single-fidelity MC on the
  high-fidelity model alone:

      var_MFMC / var_MC = ( sqrt(1 - rho^2) + sqrt(rho^2 / w) )^2

  MFMC pays (ratio < 1) iff  1/w < rho^2 / (1 - rho^2); with a strongly
  correlated surrogate and a large cost ratio the ratio approaches
  1 - rho^2 — the fusion floor.

Everything here is a pure function over measured numbers; nothing touches a
workflow or a surface. Offline evidence (per the Innovation Standard) runs
through ``scripts/run_mfmc_evidence.py`` on the race act's REAL paired
records — matched reduced-order and VSPAERO evaluations with measured costs.

Basis: Peherstorfer, Willcox and Gunzburger, "Survey of multifidelity methods
in uncertainty propagation, inference, and optimization", SIAM Review 2018.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


# --------------------------------------------------------------------------
# Sample statistics (paired records in, moments out)
# --------------------------------------------------------------------------

def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs)


def _variance(xs: Sequence[float]) -> float:
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)


def _covariance(xs: Sequence[float], ys: Sequence[float]) -> float:
    mx, my = _mean(xs), _mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)


def pearson(hi: Sequence[float], lo: Sequence[float]) -> float:
    """Measured correlation between the paired lanes. Raises on degenerate
    input (a constant lane carries no information; rho is undefined, and
    pretending rho = 0 would silently hide a broken pairing)."""
    if len(hi) != len(lo) or len(hi) < 2:
        raise ValueError("pearson needs two equal-length series of >= 2 pairs")
    vh, vl = _variance(hi), _variance(lo)
    if vh <= 0.0 or vl <= 0.0:
        raise ValueError(
            "one lane is constant over the paired records; the correlation "
            "is undefined and MFMC has nothing to work with")
    return _covariance(hi, lo) / math.sqrt(vh * vl)


def control_variate_alpha(hi: Sequence[float], lo: Sequence[float]) -> float:
    """Optimal control-variate coefficient alpha* = cov(hi, lo) / var(lo),
    measured from the paired records (equals rho * sigma_hi / sigma_lo)."""
    vl = _variance(lo)
    if len(hi) != len(lo) or len(hi) < 2 or vl <= 0.0:
        raise ValueError("alpha* needs >= 2 pairs with a non-constant low lane")
    return _covariance(hi, lo) / vl


# --------------------------------------------------------------------------
# The analytic decisions: does fusion pay, and how to split the budget
# --------------------------------------------------------------------------

def variance_ratio(rho: float, cost_hi: float, cost_lo: float) -> float:
    """var_MFMC / var_MC at EQUAL budget (the honesty number: < 1 means
    fusion beats single-fidelity MC on the high-fidelity model, > 1 means
    the cheap model is not worth carrying)."""
    if not (0.0 < cost_lo <= cost_hi):
        raise ValueError("costs must satisfy 0 < cost_lo <= cost_hi")
    rho2 = min(rho * rho, 1.0)
    w = cost_hi / cost_lo
    return (math.sqrt(1.0 - rho2) + math.sqrt(rho2 / w)) ** 2


def mfmc_pays(rho: float, cost_hi: float, cost_lo: float) -> bool:
    """The survey's admissibility condition: cost_lo/cost_hi < rho^2/(1-rho^2)."""
    rho2 = min(rho * rho, 1.0)
    if rho2 >= 1.0:
        return True
    return (cost_lo / cost_hi) < rho2 / (1.0 - rho2)


@dataclass(frozen=True)
class MfmcPlan:
    """The measured inputs and the analytic allocation they imply."""

    rho: float
    cost_hi: float                 # measured seconds per high-fidelity solve
    cost_lo: float                 # measured seconds per cheap evaluation
    cost_ratio: float              # w = cost_hi / cost_lo
    budget: float                  # total seconds to allocate
    r_optimal: float               # cheap evaluations per high-fidelity solve
    n_hi: int                      # high-fidelity solves under the budget
    n_lo: int                      # cheap evaluations under the budget
    variance_ratio: float          # var_MFMC / var_MC at this budget
    speedup_equal_error: float     # budget factor MC needs for equal variance
    pays: bool

    def spent(self) -> float:
        return self.n_hi * self.cost_hi + self.n_lo * self.cost_lo


def optimal_allocation(rho: float, cost_hi: float, cost_lo: float,
                       budget: float) -> MfmcPlan:
    """Split ``budget`` (same units as the costs) optimally across the two
    models. Requires at least one high-fidelity solve under the budget —
    MFMC keeps the expensive model in the loop for the accuracy guarantee;
    a plan with n_hi = 0 would be surrogate-only extrapolation, refused."""
    if not (0.0 < cost_lo <= cost_hi):
        raise ValueError("costs must satisfy 0 < cost_lo <= cost_hi")
    if abs(rho) >= 1.0:
        raise ValueError(
            "|rho| >= 1 over the paired records means the lanes are affinely "
            "identical; use the cheap model directly, no fusion needed")
    rho2 = rho * rho
    r = math.sqrt(rho2 / (1.0 - rho2) * (cost_hi / cost_lo)) if rho2 > 0 else 1.0
    n_hi = int(budget / (cost_hi + r * cost_lo))
    if n_hi < 1:
        raise ValueError(
            f"budget {budget:g} cannot afford one high-fidelity solve plus "
            f"its cheap complement (needs {cost_hi + r * cost_lo:g})")
    n_lo = max(n_hi, int(r * n_hi))
    ratio = variance_ratio(rho, cost_hi, cost_lo)
    return MfmcPlan(
        rho=rho, cost_hi=cost_hi, cost_lo=cost_lo,
        cost_ratio=cost_hi / cost_lo, budget=budget,
        r_optimal=r, n_hi=n_hi, n_lo=n_lo,
        variance_ratio=ratio,
        speedup_equal_error=(1.0 / ratio if ratio > 0 else math.inf),
        pays=mfmc_pays(rho, cost_hi, cost_lo),
    )


# --------------------------------------------------------------------------
# The estimator itself
# --------------------------------------------------------------------------

def mfmc_estimate(hi_paired: Sequence[float], lo_paired: Sequence[float],
                  lo_extra: Sequence[float],
                  alpha: float | None = None) -> dict:
    """The fused mean: high-fidelity mean, shifted by alpha times the gap
    between the cheap model's broad-ensemble mean and its mean over the
    paired subset. ``hi_paired``/``lo_paired`` are the matched records (same
    designs, both lanes); ``lo_extra`` are the additional cheap-only
    evaluations that give the estimator its volume. Unbiased for E[hi] for
    any fixed alpha; alpha defaults to the measured optimum."""
    if len(hi_paired) != len(lo_paired) or len(hi_paired) < 2:
        raise ValueError("mfmc_estimate needs >= 2 matched pairs")
    if alpha is None:
        alpha = control_variate_alpha(hi_paired, lo_paired)
    lo_all = list(lo_paired) + list(lo_extra)
    estimate = _mean(hi_paired) + alpha * (_mean(lo_all) - _mean(lo_paired))
    return {
        "estimate": estimate,
        "alpha": alpha,
        "n_hi": len(hi_paired),
        "n_lo": len(lo_all),
        "hi_mean": _mean(hi_paired),
        "lo_shift": alpha * (_mean(lo_all) - _mean(lo_paired)),
    }
