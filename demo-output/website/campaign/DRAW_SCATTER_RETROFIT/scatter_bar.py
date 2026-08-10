#!/usr/bin/env python3
"""The draw-scatter retrofit's SHARED bar calibration (Verification Charter §17).

ONE implementation, used by every retrofit arm, because two implementations of
a calibration are two things that can disagree about what was calibrated --
the same reasoning that put every lever echo behind one predicate.

The bar separating "the scatter is structured around one aberrant draw" from
"the scatter is broad" is calibrated BY SIMULATION AGAINST THE NULL, before any
draw exists, and never chosen afterwards. Every verdict therefore arrives with
its false-positive rate stated.

Statistic (as used on Ahmed 25 c3, the worked precedent):
    R = s(draws excluding the most extreme) / s(all draws)
A single aberrant draw inflates s and collapses it on removal; broad scatter
does not.

Usage:
    from scatter_bar import calibrate, classify
    bar = calibrate(n=4)                    # -> R_bar and its stated FP rate
    v   = classify([cd1, cd2, cd3, cd4], bar)
"""
from __future__ import annotations
import math
from dataclasses import dataclass, asdict

FP_RATE = 0.10          # the convention: bar at the 10th percentile of the null
SEED = 20260810         # fixed so any agent reproduces the same bar exactly


@dataclass
class Bar:
    n: int
    r_bar: float
    false_positive_rate: float
    null_median: float
    samples: int
    seed: int
    convention: str = ("R = s(without most extreme)/s(all); OUTLIER-DOMINATED if "
                       "R <= r_bar. Bar is the FP_RATE-th percentile of the "
                       "pure-normal null at this n, computed before any draw "
                       "exists (Verification Charter section 17).")

    def as_dict(self): return asdict(self)


def _sd(v):
    m = sum(v) / len(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def calibrate(n: int, samples: int = 200_000) -> Bar:
    """The bar for a sample of size n, from the pure-scatter null."""
    if n < 3:
        raise ValueError("R is undefined below n=3: removing one draw from two "
                         "leaves no sample standard deviation to compare against")
    import numpy as np
    rng = np.random.default_rng(SEED)
    x = rng.normal(size=(samples, n))
    s_all = x.std(axis=1, ddof=1)
    ex = np.abs(x - x.mean(axis=1)[:, None]).argmax(axis=1)
    keep = np.ones_like(x, dtype=bool)
    keep[np.arange(samples), ex] = False
    s_wo = x[keep].reshape(samples, n - 1).std(axis=1, ddof=1)
    r = s_wo / s_all
    return Bar(n=n, r_bar=float(np.percentile(r, 100 * FP_RATE)),
               false_positive_rate=FP_RATE, null_median=float(np.median(r)),
               samples=samples, seed=SEED)


def classify(draws: list[float], bar: Bar, published_index: int = 0) -> dict:
    """Classify a rung's draws against a pre-computed bar.

    ``published_index`` is the draw that appears in the published ladder; which
    draw is extreme decides whether the PUBLISHED NUMBER or the RECIPE is at
    fault, and that asymmetry is part of the verdict.
    """
    if len(draws) != bar.n:
        raise ValueError(f"bar calibrated for n={bar.n}, got {len(draws)} draws")
    s_all = _sd(draws)
    m = sum(draws) / len(draws)
    ex = max(range(len(draws)), key=lambda i: abs(draws[i] - m))
    s_wo = _sd([v for i, v in enumerate(draws) if i != ex])
    R = s_wo / s_all
    if R <= bar.r_bar:
        branch = "B1_PUBLISHED_NUMBER" if ex == published_index else "B2_RECIPE"
        reading = ("outlier-dominated, and the extreme draw IS the published one: "
                   "the ladder's entry is an unlucky draw and the PUBLISHED NUMBER "
                   "is at fault") if ex == published_index else \
                  ("outlier-dominated, and the extreme draw is a REDRAW: the "
                   "published value is representative and the recipe occasionally "
                   "lands elsewhere. THE RECIPE is at fault -- not an exoneration")
    else:
        branch, reading = "B3_BROAD", ("broad scatter: no single draw at this rung "
                   "is trustworthy and the increment cannot be read from single "
                   "draws at all. BOTH are implicated")
    pct = None
    try:
        import numpy as np
        rng = np.random.default_rng(SEED)
        x = rng.normal(size=(20_000, bar.n)); sa = x.std(axis=1, ddof=1)
        e = np.abs(x - x.mean(axis=1)[:, None]).argmax(axis=1)
        k = np.ones_like(x, dtype=bool); k[np.arange(20_000), e] = False
        r0 = x[k].reshape(20_000, bar.n - 1).std(axis=1, ddof=1) / sa
        pct = float(100 * (r0 < R).mean())
    except Exception:
        pass
    return {"draws": list(draws), "s_all": s_all, "s_without_extreme": s_wo,
            "R": R, "r_bar": bar.r_bar, "extreme_index": ex,
            "extreme_is_published": ex == published_index,
            "branch": branch, "reading": reading,
            "R_percentile_in_null": pct,
            "near_miss": (pct is not None and abs(R - bar.r_bar) < 0.06),
            "false_positive_rate": bar.false_positive_rate,
            "bar": bar.as_dict()}
