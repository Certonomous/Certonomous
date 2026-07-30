"""A Reynolds-aware reduced-order surrogate for the NACA 4412 race wing.

The race act's reduced-order lane (``workflows.shape_optimization._fit_quadratic``
as reused by ``workflows.race_study``) fits L/D as a quadratic in angle of
attack ALONE: its four anchor solves are all taken at the one nominal chord
Reynolds number (see ``workflows.race_benchmark.RE_NOMINAL``), so the fitted
surface has zero Reynolds dependence by construction. The lab's multifidelity
study (``scripts/run_mfmc_evidence.py``) measured the consequence directly:
over the race's actual estimand — peak L/D under the sampled Reynolds spread
at fixed alpha — the surrogate's lane is CONSTANT, the correlation with the
solver is undefined, and MFMC degenerates to plain Monte Carlo.

This module replaces the alpha-only surface with a quadratic response surface
in BOTH angle of attack and (normalized) chord Reynolds number:

    L/D(alpha, Re) = c0 + c1*a + c2*a^2 + c3*u + c4*u^2 + c5*a*u,
    u = (Re - Re_ref) / Re_ref

``Re_ref`` is the race's own nominal chord Reynolds (1.0e6), so ``u`` stays
O(0.1-0.3) over the sampled range and the normal-equations fit stays well
conditioned without any external numerics dependency (pure Python, matching
``workflows.shape_optimization._fit_quadratic``'s style).

Fit and prediction are pure functions over measured (alpha, Re, L/D) triples;
nothing here runs a solver. Evidence generation (real VSPAERO anchors, a
genuine held-out validation split, and the correlation/MFMC comparison against
the race's recorded pairing) lives in
``scripts/run_reynolds_surrogate_evidence.py``.
"""

from __future__ import annotations

from typing import Sequence

N_TERMS = 6


def _basis(alpha: float, u: float) -> list[float]:
    return [1.0, alpha, alpha * alpha, u, u * u, alpha * u]


def _solve_linear(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    """Gaussian elimination with partial pivoting on a square system.

    Same technique as ``workflows.shape_optimization._fit_quadratic``,
    generalized to N_TERMS unknowns instead of hard-coding 3.
    """
    n = len(rhs)
    matrix = [row[:] for row in matrix]
    rhs = rhs[:]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(matrix[r][col]))
        if abs(matrix[pivot][col]) < 1e-14:
            raise ValueError("normal-equations matrix is singular, the "
                             "training design does not span alpha and Re "
                             "independently enough to fit the surface")
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        rhs[col], rhs[pivot] = rhs[pivot], rhs[col]
        for row in range(col + 1, n):
            factor = matrix[row][col] / matrix[col][col]
            for k in range(col, n):
                matrix[row][k] -= factor * matrix[col][k]
            rhs[row] -= factor * rhs[col]
    out = [0.0] * n
    for row in reversed(range(n)):
        out[row] = (rhs[row] - sum(matrix[row][k] * out[k]
                                   for k in range(row + 1, n))) / matrix[row][row]
    return out


def fit_reynolds_surface(alphas: Sequence[float], res: Sequence[float],
                         l_ds: Sequence[float], re_ref: float) -> list[float]:
    """Least-squares fit of the quadratic-in-(alpha, Re) surface.

    ``re_ref`` is the normalization center (the race's nominal chord
    Reynolds); it must be supplied by the caller, never re-derived here, so
    the fit and every later prediction share the identical normalization.
    Needs at least N_TERMS=6 training points that are not confined to a
    lower-dimensional slice (e.g. not all at one alpha or one Re).
    """
    if len(alphas) != len(res) or len(alphas) != len(l_ds):
        raise ValueError("alphas, res, l_ds must be equal length")
    if len(alphas) < N_TERMS:
        raise ValueError(f"need at least {N_TERMS} training points for the "
                         f"{N_TERMS}-term surface, got {len(alphas)}")
    rows = [_basis(a, (r - re_ref) / re_ref) for a, r in zip(alphas, res)]
    matrix = [[sum(row[i] * row[j] for row in rows) for j in range(N_TERMS)]
              for i in range(N_TERMS)]
    rhs = [sum(row[i] * y for row, y in zip(rows, l_ds)) for i in range(N_TERMS)]
    return _solve_linear(matrix, rhs)


def predict_reynolds_surface(coeff: Sequence[float], alpha: float, re: float,
                             re_ref: float) -> float:
    u = (re - re_ref) / re_ref
    return sum(c * b for c, b in zip(coeff, _basis(alpha, u)))


def fit_quality(alphas: Sequence[float], res: Sequence[float],
                l_ds: Sequence[float], coeff: Sequence[float],
                re_ref: float) -> dict:
    """RMSE and R^2 of the fitted surface against one set of (alpha, Re, L/D)
    triples — call once on the training set and once on a disjoint held-out
    set to report train vs validation accuracy separately."""
    preds = [predict_reynolds_surface(coeff, a, r, re_ref)
             for a, r in zip(alphas, res)]
    errs = [p - y for p, y in zip(preds, l_ds)]
    n = len(l_ds)
    mse = sum(e * e for e in errs) / n
    mean_y = sum(l_ds) / n
    ss_tot = sum((y - mean_y) ** 2 for y in l_ds)
    ss_res = sum(e * e for e in errs)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {"n": n, "rmse": mse ** 0.5,
            "max_abs_error": max(abs(e) for e in errs), "r2": r2}
