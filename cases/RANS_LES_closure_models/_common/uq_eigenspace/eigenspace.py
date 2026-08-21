#!/usr/bin/env python3
"""Eigenspace perturbation machinery (shelf D).

Sources, read from the PDFs on disk, not from memory:

  Emory, Larsson & Iaccarino, "Modeling of structural uncertainties in
  Reynolds-averaged Navier-Stokes closures", Phys. Fluids 25, 110822 (2013).
  `docs/papers/closure/Emory2013_structural_uncertainty_rans.pdf`
    eq. (4)  p.110822-5  R_ij = 2k (d_ij/3 + v_in L_nl v_jl),  l1 >= l2 >= l3
    eq. (5)  p.110822-5  x = x_1c (l1-l2) + x_2c (2l2-2l3) + x_3c (3l3+1) = M l
    eq. (7)  p.110822-6  x* = x + delta_B (x^(t) - x)
    eq. (8a) p.110822-6  l* = M^-1 x*

  Iaccarino, Mishra & Ghili, "Eigenspace perturbations for uncertainty estimation
  of single-point turbulence closures", Phys. Rev. Fluids 2, 024605 (2017).
  `docs/papers/closure/Iaccarino2017_eigenspace_perturbations.pdf` -- ACCEPTED
  MANUSCRIPT via CHORUS, so equation/page numbering may differ from the journal
  of record; numbers below are manuscript numbering.
    eq. (3)  <A,R>_F in [l1 g3 + l2 g2 + l3 g1,  l1 g1 + l2 g2 + l3 g3],
             g1 >= g2 >= g3 the eigenvalues of the mean rate of strain
    after eq. (3)  in the strain-eigenvector frame the bounding alignments are
             v_min = [[0,0,1],[0,1,0],[1,0,0]],  v_max = I
    before sec. III  "we need a set of only 5 RANS simulations": 3
             componentiality limits x 2 alignments, with 3C degenerate under
             rotation (spherical ellipsoid) -> {1C,2C} x {vmin,vmax} plus 3C.

NAMING. The Emory paper writes `B` both for the perturbation magnitude (eq. 7)
and for the linear map matrix (eq. 5). Here the scalar is `delta_B` and the
matrix is `M`; they are never the same object.

Barycentric coordinates are carried as the triple c = (c1, c2, c3) with
  c1 = l1 - l2,   c2 = 2(l2 - l3),   c3 = 3 l3 + 1,   c1 + c2 + c3 = 1,
which is eq. (5) expressed in the corner basis. The realisable set is exactly
{c_i >= 0}, so eq. (7) with delta_B in [0,1] cannot leave it -- a convex move
toward a vertex of a simplex stays in the simplex. `assert_realisable` checks it.

Nothing here is fitted. Reads no data; operates on arrays handed to it.
"""
from __future__ import annotations
import numpy as np

CORNERS = ("1C", "2C", "3C")
ALIGNMENTS = ("vmin", "vmax", "base")
# Iaccarino, paragraph after eq. (3): alignment permutations of the Reynolds
# stress eigenvectors in the coordinate frame of the mean rate of strain.
P_VMAX = np.eye(3)
P_VMIN = np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]])


def eig_sorted(b):
    """Eigenvalues descending and matching eigenvectors as columns. (N,3),(N,3,3)."""
    w, v = np.linalg.eigh(b)
    order = np.argsort(-w, axis=1)
    w = np.take_along_axis(w, order, axis=1)
    v = np.take_along_axis(v, order[:, None, :], axis=2)
    return w, v


def bary_from_lambda(lam):
    """Emory eq. (5) in the corner basis. lam (N,3) descending -> c (N,3)."""
    return np.stack([lam[:, 0] - lam[:, 1],
                     2.0 * (lam[:, 1] - lam[:, 2]),
                     3.0 * lam[:, 2] + 1.0], axis=1)


def lambda_from_bary(c):
    """Emory eq. (8a): invert eq. (5). c (N,3) -> lam (N,3) descending."""
    l3 = (c[:, 2] - 1.0) / 3.0
    l2 = l3 + c[:, 1] / 2.0
    l1 = l2 + c[:, 0]
    return np.stack([l1, l2, l3], axis=1)


def barycentric_coords(b):
    """(N,3,3) anisotropy -> (c, lam, v). c is Emory eq. (5) in the corner basis."""
    lam, v = eig_sorted(b)
    return bary_from_lambda(lam), lam, v


def perturb_eigenvalues(c, target, delta_B):
    """Emory eq. (7): c* = c + delta_B (e_t - c), e_t the target corner."""
    t = CORNERS.index(target)
    e = np.zeros(3)
    e[t] = 1.0
    return c + delta_B * (e[None, :] - c)


def strain_frame(gradU):
    """Eigenvectors of the mean rate of strain, columns ordered g1 >= g2 >= g3."""
    S = 0.5 * (gradU + gradU.transpose(0, 2, 1))
    g, V = eig_sorted(S)
    return g, V


def reconstruct(lam, V):
    """b = V diag(lam) V^T."""
    return np.einsum("nij,nj,nkj->nik", V, lam, V)


def permute_eigenvectors(lam, gradU, which):
    """Iaccarino alignment: build b from `lam` with the Reynolds-stress
    eigenvectors set to the extremal alignment in the STRAIN eigenframe.

    `which` = "vmax" aligns the largest anisotropy eigenvalue with the
    stretching strain direction (maximum production); "vmin" with the
    compressive direction (minimum production); "base" is not an alignment and
    is handled by the caller, which passes the model's own eigenvectors.
    """
    _, V = strain_frame(gradU)
    P = P_VMAX if which == "vmax" else P_VMIN
    # V P diag(lam) P^T V^T ; P a permutation so P diag(l) P^T = diag(P l)
    return reconstruct(lam @ P, V)


def five_states(b, gradU, delta_B):
    """Iaccarino's five extremal states: {1C,2C} x {vmin,vmax} plus 3C.

    Returns (states, labels): states (5,N,3,3). 3C is rotationally degenerate
    (spherical ellipsoid) so it carries no alignment -- the paper's own reason
    for five simulations rather than six.
    """
    c, lam, _ = barycentric_coords(b)
    out, labels = [], []
    for corner in ("1C", "2C"):
        lp = lambda_from_bary(perturb_eigenvalues(c, corner, delta_B))
        for al in ("vmin", "vmax"):
            out.append(permute_eigenvectors(lp, gradU, al))
            labels.append(f"{corner}_{al}")
    lp3 = lambda_from_bary(perturb_eigenvalues(c, "3C", delta_B))
    _, V = strain_frame(gradU)
    out.append(reconstruct(lp3, V))
    labels.append("3C")
    return np.stack(out), labels


def envelope(vals):
    """(S,N,...) over states -> (min, max) per cell."""
    return vals.min(axis=0), vals.max(axis=0)


def production(b, k, gradU):
    """Momentum-forcing proxy P_k = -R_ij dU_i/dx_j with R = 2k(b + I/3).

    The isotropic part contributes -2k/3 tr(gradU) = 0 for incompressible flow,
    so P_k = -2k b_ij dU_i/dx_j. This is the term through which the Reynolds
    stress forces the mean momentum equation, and the quantity Iaccarino eq. (3)
    bounds.
    """
    return -2.0 * k * np.einsum("nij,nij->n", b, gradU)


def inside_hull_c(c_test, c_states):
    """Is c_test inside the triangle spanned by three state points, in c-space?

    All points satisfy sum(c) = 1, so the barycentric weights of c_test with
    respect to the three vertices solve a 2x2 system; inside <=> all weights >= 0.
    """
    v0, v1, v2 = c_states[0], c_states[1], c_states[2]
    a = v1[:, :2] - v0[:, :2]
    bb = v2[:, :2] - v0[:, :2]
    p = c_test[:, :2] - v0[:, :2]
    det = a[:, 0] * bb[:, 1] - a[:, 1] * bb[:, 0]
    ok = np.abs(det) > 1e-14
    w1 = np.where(ok, (p[:, 0] * bb[:, 1] - p[:, 1] * bb[:, 0]) / np.where(ok, det, 1), -1)
    w2 = np.where(ok, (a[:, 0] * p[:, 1] - a[:, 1] * p[:, 0]) / np.where(ok, det, 1), -1)
    return (w1 >= -1e-12) & (w2 >= -1e-12) & (w1 + w2 <= 1 + 1e-12)


def delta_B_required(c_rans, c_truth):
    """Smallest delta_B at which the truth lies in the perturbed triangle.

    T(delta) = {(1-delta) c + delta e : e in simplex} is a homothety of the
    realisable simplex about the model point c with ratio delta. c_truth is in
    T(delta) iff e = c + (c_truth - c)/delta has all components >= 0, i.e.

        delta >= (c_i - c_truth_i) / c_i   for every i with c_truth_i < c_i.

    Returns that maximum (0 where the truth is already at the model point, and
    +inf where a component of c_i is zero while the truth is negative there).
    A value <= 1 is equivalent to the truth being realisable.
    """
    num = c_rans - c_truth
    need = np.where(num > 0, num / np.where(c_rans > 0, c_rans, np.nan), 0.0)
    need = np.where(np.isnan(need), np.inf, need)
    return np.max(need, axis=1)


def assert_realisable(c, tol=1e-9):
    """Eq. (7) with delta_B in [0,1] cannot leave the simplex. Verify it."""
    bad = int((c.min(axis=1) < -tol).sum())
    return bad
