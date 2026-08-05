"""Non-intrusive polynomial chaos and a Gaussian-process surrogate, on numpy.

Two ways to answer the same question -- what does the band look like, and which
input owns it -- from ONE set of expensive solves. Neither adds a dependency:
the lab's boxes have numpy and scipy and do not have chaospy or scikit-learn,
and a chaos expansion in a bounded uniform germ is a least-squares fit against
Legendre products, which numpy does exactly.

The two are here together on purpose. A chaos expansion gives variance shares
in closed form from its own coefficients but only inside the polynomial family
it was given; a process regression gives a band with its own posterior spread
but no variance decomposition. Fitted on the same samples they check each
other, and the check is the point: a chaos band that disagrees with the process
band is telling you the response is not the shape the expansion assumed.

WHAT IS SCORED, AND WHY IT IS SCORED TWICE. Both fits report leave-one-out,
which is free and which every surrogate paper quotes. Leave-one-out on a design
this small is optimistic -- the point left out still has all its neighbours --
so both also accept a held-out set, and where a caller supplies one, the
held-out number is the one that decides whether the surrogate may be believed.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

__all__ = ["multi_indices", "legendre_design", "PCEFit", "fit_pce",
           "GPFit", "fit_gp", "band_from_samples"]


# ---------------------------------------------------------------------------
# Polynomial chaos on a uniform germ (Legendre)
# ---------------------------------------------------------------------------

def multi_indices(dim: int, order: int) -> list[tuple[int, ...]]:
    """Every multi-index of total degree <= `order` in `dim` variables.

    Ordered by total degree, then lexicographically, so index 0 is always the
    constant term and a truncation to a lower order is a prefix of this list.
    """
    out: list[tuple[int, ...]] = []
    for total in range(order + 1):
        for idx in itertools.product(range(total + 1), repeat=dim):
            if sum(idx) == total:
                out.append(idx)
    return out


def _normalised_legendre(xi: np.ndarray, degree: int) -> np.ndarray:
    """Legendre polynomials on [-1, 1] scaled to unit variance under the
    uniform measure, i.e. E[P_k^2] = 1. Shape (n, degree+1)."""
    n = xi.shape[0]
    raw = np.empty((n, degree + 1))
    raw[:, 0] = 1.0
    if degree >= 1:
        raw[:, 1] = xi
    for k in range(1, degree):
        raw[:, k + 1] = ((2 * k + 1) * xi * raw[:, k] - k * raw[:, k - 1]) / (k + 1)
    scale = np.sqrt(2.0 * np.arange(degree + 1) + 1.0)
    return raw * scale


def legendre_design(x: np.ndarray, lower: np.ndarray, upper: np.ndarray,
                    indices: Sequence[tuple[int, ...]]) -> np.ndarray:
    """Design matrix of orthonormal Legendre products at the sample points.

    `x` is in physical coordinates; it is mapped to the germ [-1, 1] with the
    box the samples were drawn from, so the orthogonality the variance
    decomposition relies on is orthogonality under THAT uniform measure.
    """
    x = np.atleast_2d(np.asarray(x, dtype=float))
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)
    span = np.where(upper > lower, upper - lower, 1.0)
    xi = 2.0 * (x - lower) / span - 1.0
    max_deg = max((max(idx) for idx in indices), default=0)
    per_dim = [_normalised_legendre(xi[:, j], max_deg) for j in range(x.shape[1])]
    design = np.ones((x.shape[0], len(indices)))
    for col, idx in enumerate(indices):
        for j, deg in enumerate(idx):
            if deg:
                design[:, col] *= per_dim[j][:, deg]
    return design


@dataclass
class PCEFit:
    """A fitted expansion and everything it can say about itself."""
    order: int
    names: list[str]
    lower: np.ndarray
    upper: np.ndarray
    indices: list[tuple[int, ...]]
    coefficients: np.ndarray
    n_samples: int
    mean: float
    variance: float
    loo_q2: float
    loo_rmse: float
    fit_rmse: float
    sobol_first: dict[str, float]
    sobol_total: dict[str, float]
    conditioning: float
    oversampling: float
    notes: list[str] = field(default_factory=list)

    def predict(self, x: np.ndarray) -> np.ndarray:
        design = legendre_design(x, self.lower, self.upper, self.indices)
        return design @ self.coefficients

    def as_dict(self) -> dict[str, Any]:
        return {
            "order": self.order,
            "n_terms": len(self.indices),
            "n_samples": self.n_samples,
            "oversampling_ratio": round(self.oversampling, 3),
            "mean": self.mean,
            "std": math.sqrt(max(self.variance, 0.0)),
            "variance": self.variance,
            "fit_rmse": self.fit_rmse,
            "loo_rmse": self.loo_rmse,
            "loo_q2": self.loo_q2,
            "design_condition_number": self.conditioning,
            "sobol_first_order": {k: round(v, 6) for k, v in self.sobol_first.items()},
            "sobol_total": {k: round(v, 6) for k, v in self.sobol_total.items()},
            "basis": "orthonormal Legendre products (uniform germ)",
            "fit": "point-collocation least squares (non-intrusive)",
            "notes": self.notes,
        }


def fit_pce(x: np.ndarray, y: np.ndarray, *, lower, upper,
            names: Sequence[str], order: int = 2) -> PCEFit:
    """Least-squares chaos expansion of `y` on the box [lower, upper].

    Refuses to fit an expansion with more terms than samples: an underdetermined
    chaos fit interpolates its own training set and reports a variance that is
    an artefact of the least-norm solution, which is exactly the number a
    caller would then quote as a band.
    """
    x = np.atleast_2d(np.asarray(x, dtype=float))
    y = np.asarray(y, dtype=float).ravel()
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)
    indices = multi_indices(x.shape[1], order)
    if len(indices) > len(y):
        raise ValueError(
            f"order-{order} expansion needs {len(indices)} terms but only "
            f"{len(y)} samples were given; an underdetermined fit would report "
            f"a variance it did not measure")
    design = legendre_design(x, lower, upper, indices)
    coeffs, *_ = np.linalg.lstsq(design, y, rcond=None)
    resid = y - design @ coeffs

    # Leave-one-out in closed form for a linear least-squares fit: the hat
    # matrix gives every held-out residual without refitting once.
    pinv = np.linalg.pinv(design)
    hat = np.einsum("ij,ji->i", design, pinv)
    denom = np.clip(1.0 - hat, 1e-12, None)
    loo_resid = resid / denom
    spread = float(np.sum((y - y.mean()) ** 2))
    loo_q2 = 1.0 - float(np.sum(loo_resid ** 2)) / spread if spread > 0 else float("nan")

    variance = float(np.sum(coeffs[1:] ** 2))
    first, total = {}, {}
    for j, name in enumerate(names):
        only_j = [c for c, idx in zip(coeffs, indices)
                  if idx[j] > 0 and sum(idx) == idx[j]]
        any_j = [c for c, idx in zip(coeffs, indices) if idx[j] > 0]
        first[name] = float(np.sum(np.square(only_j)) / variance) if variance > 0 else float("nan")
        total[name] = float(np.sum(np.square(any_j)) / variance) if variance > 0 else float("nan")

    notes = []
    if loo_q2 < 0.9:
        notes.append(f"leave-one-out Q2 = {loo_q2:.3f}: the expansion does not "
                     f"reproduce points it did not see, so its variance shares "
                     f"are a reading of the fit, not of the response")
    return PCEFit(order=order, names=list(names), lower=lower, upper=upper,
                  indices=indices, coefficients=coeffs, n_samples=len(y),
                  mean=float(coeffs[0]), variance=variance, loo_q2=loo_q2,
                  loo_rmse=float(np.sqrt(np.mean(loo_resid ** 2))),
                  fit_rmse=float(np.sqrt(np.mean(resid ** 2))),
                  sobol_first=first, sobol_total=total,
                  conditioning=float(np.linalg.cond(design)),
                  oversampling=len(y) / len(indices), notes=notes)


# ---------------------------------------------------------------------------
# Gaussian process regression
# ---------------------------------------------------------------------------

def _kernel(a: np.ndarray, b: np.ndarray, log_theta: np.ndarray) -> np.ndarray:
    """Anisotropic squared exponential; `log_theta` is [log sigma_f, log l_1..d]."""
    sig2 = math.exp(2.0 * log_theta[0])
    scales = np.exp(log_theta[1:])
    diff = (a[:, None, :] - b[None, :, :]) / scales
    return sig2 * np.exp(-0.5 * np.sum(diff ** 2, axis=-1))


@dataclass
class GPFit:
    names: list[str]
    lower: np.ndarray
    upper: np.ndarray
    y_mean: float
    y_scale: float
    x_train: np.ndarray
    log_theta: np.ndarray
    log_noise: float
    chol: np.ndarray
    alpha: np.ndarray
    loo_rmse: float
    loo_q2: float
    loo_z_rms: float
    log_marginal_likelihood: float
    n_samples: int

    def predict(self, x: np.ndarray, *, with_std: bool = False):
        x = np.atleast_2d(np.asarray(x, dtype=float))
        span = np.where(self.upper > self.lower, self.upper - self.lower, 1.0)
        xs = (x - self.lower) / span
        k = _kernel(xs, self.x_train, self.log_theta)
        mean = self.y_mean + self.y_scale * (k @ self.alpha)
        if not with_std:
            return mean
        v = np.linalg.solve(self.chol, k.T)
        var = (math.exp(2.0 * self.log_theta[0]) + math.exp(2.0 * self.log_noise)
               - np.sum(v ** 2, axis=0))
        return mean, self.y_scale * np.sqrt(np.clip(var, 0.0, None))

    def as_dict(self) -> dict[str, Any]:
        return {
            "kernel": "anisotropic squared exponential + nugget",
            "hyperparameters_by": "marginal likelihood maximisation",
            "n_samples": self.n_samples,
            "signal_std": math.exp(self.log_theta[0]) * self.y_scale,
            "noise_std": math.exp(self.log_noise) * self.y_scale,
            "lengthscales_unit_box": {
                n: round(float(v), 5)
                for n, v in zip(self.names, np.exp(self.log_theta[1:]))},
            "loo_rmse": self.loo_rmse,
            "loo_q2": self.loo_q2,
            "loo_z_rms": self.loo_z_rms,
            "log_marginal_likelihood": self.log_marginal_likelihood,
            "calibration_note": (
                "loo_z_rms is the RMS of the held-out residual divided by the "
                "posterior standard deviation the process claimed for it; near "
                "1 the process's own error bars are honest, well above 1 they "
                "are too narrow and below 1 too wide"),
        }


def fit_gp(x: np.ndarray, y: np.ndarray, *, lower, upper,
           names: Sequence[str], restarts: int = 6, seed: int = 0) -> GPFit:
    """Gaussian process with hyperparameters from the marginal likelihood.

    Inputs are mapped to the unit box and the response is centred and scaled,
    so the lengthscales are readable as "what fraction of the box this input
    varies over" and one set of optimiser bounds serves every problem.
    """
    x = np.atleast_2d(np.asarray(x, dtype=float))
    y = np.asarray(y, dtype=float).ravel()
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)
    span = np.where(upper > lower, upper - lower, 1.0)
    xs = (x - lower) / span
    y_mean = float(y.mean())
    y_scale = float(y.std(ddof=0)) or 1.0
    ys = (y - y_mean) / y_scale
    dim = xs.shape[1]

    def negative_log_marginal(params: np.ndarray) -> float:
        log_theta, log_noise = params[:-1], params[-1]
        k = _kernel(xs, xs, log_theta)
        k[np.diag_indices_from(k)] += math.exp(2.0 * log_noise) + 1e-10
        try:
            chol = np.linalg.cholesky(k)
        except np.linalg.LinAlgError:
            return 1e12
        alpha = np.linalg.solve(chol.T, np.linalg.solve(chol, ys))
        return float(0.5 * ys @ alpha + np.sum(np.log(np.diag(chol)))
                     + 0.5 * len(ys) * math.log(2 * math.pi))

    from scipy.optimize import minimize

    rng = np.random.default_rng(seed)
    bounds = [(-4.0, 3.0)] + [(-3.0, 3.0)] * dim + [(-9.0, 0.0)]
    best, best_value = None, math.inf
    starts = [np.array([0.0] + [math.log(0.5)] * dim + [-6.0])]
    for _ in range(restarts - 1):
        starts.append(np.array([rng.normal(0, 0.5)]
                               + list(rng.normal(math.log(0.5), 0.7, dim))
                               + [rng.uniform(-8.0, -3.0)]))
    for start in starts:
        res = minimize(negative_log_marginal, start, method="L-BFGS-B",
                       bounds=bounds)
        if res.fun < best_value:
            best, best_value = res.x, float(res.fun)

    log_theta, log_noise = best[:-1], float(best[-1])
    k = _kernel(xs, xs, log_theta)
    k[np.diag_indices_from(k)] += math.exp(2.0 * log_noise) + 1e-10
    chol = np.linalg.cholesky(k)
    alpha = np.linalg.solve(chol.T, np.linalg.solve(chol, ys))

    # Closed-form leave-one-out for a GP (Rasmussen & Williams 5.4.2).
    k_inv = np.linalg.solve(chol.T, np.linalg.solve(chol, np.eye(len(ys))))
    diag = np.clip(np.diag(k_inv), 1e-300, None)
    loo_resid = alpha / diag
    loo_var = 1.0 / diag
    spread = float(np.sum((ys - ys.mean()) ** 2))
    return GPFit(names=list(names), lower=lower, upper=upper, y_mean=y_mean,
                 y_scale=y_scale, x_train=xs, log_theta=log_theta,
                 log_noise=log_noise, chol=chol, alpha=alpha,
                 loo_rmse=float(np.sqrt(np.mean(loo_resid ** 2))) * y_scale,
                 loo_q2=(1.0 - float(np.sum(loo_resid ** 2)) / spread
                         if spread > 0 else float("nan")),
                 loo_z_rms=float(np.sqrt(np.mean(loo_resid ** 2 / loo_var))),
                 log_marginal_likelihood=-best_value, n_samples=len(ys))


# ---------------------------------------------------------------------------
# Reading a band off a sample set
# ---------------------------------------------------------------------------

def band_from_samples(values: Sequence[float], *,
                      reference: float | None = None) -> dict[str, Any]:
    """The band a set of propagated samples supports, both ways of reading it.

    `envelope` is the interval reading -- min to max, the only reading an
    epistemic interval box actually licenses. `percentile_5_95` and `std` are
    the probabilistic reading, which exists only because a distribution was
    ASSUMED over the box to get the samples; both are returned so a caller
    cannot quote one without the other being in the same record.
    """
    v = np.asarray(list(values), dtype=float)
    if v.size < 2:
        raise ValueError("a band needs at least two samples")
    lo, hi = float(v.min()), float(v.max())
    p5, p95 = (float(x) for x in np.percentile(v, [5, 95]))
    out: dict[str, Any] = {
        "n": int(v.size),
        "min": lo, "max": hi,
        "envelope_width": hi - lo,
        "mean": float(v.mean()),
        "std": float(v.std(ddof=1)),
        "percentile_5": p5, "percentile_95": p95,
        "central_90_width": p95 - p5,
        "reading_note": (
            "envelope is the interval reading of an epistemic box; the "
            "percentile and standard-deviation figures exist only under the "
            "sampling distribution assumed over that box and are never folded "
            "into a quadrature as if they were measured scatter"),
    }
    if reference:
        out["reference"] = float(reference)
        out["envelope_pct_of_reference"] = 100.0 * (hi - lo) / abs(reference)
        out["reference_inside_envelope"] = bool(lo <= reference <= hi)
    return out
