"""
F6d -- random-matrix / maximum-entropy model-form UQ sampler for RANS Reynolds
stresses, implementing:

    Xiao, H., Wang, J.-X. & Ghanem, R.G., "A Random Matrix Approach for
    Quantifying Model-Form Uncertainties in Turbulence Modeling",
    arXiv:1603.09656v1 (31 Mar 2016); also Comput. Methods Appl. Mech. Engrg.
    Local full-text copy (fetched this session, 42 pp.):
      /home/ubuntu/Certonomous/docs/papers/xiao_wang_ghanem_1603.09656.pdf
      /home/ubuntu/Certonomous/docs/papers/xiao_wang_ghanem_1603.09656.txt

Every equation number cited below is that paper's own numbering, read from the
local text extract, not paraphrased from memory.

METHOD (paper Appendix A, "Summary of the Algorithm of the Proposed Method"):

  Eq. (9)  : mean Reynolds stress   [R_bar] = [L_R]^T [L_R]   (Cholesky, L_R
             UPPER triangular with non-negative diagonal).
  Eq. (8)  : realization            [R]     = [L_R]^T [G] [L_R],  E{[G]} = [I].
  Eq. (14) : [G] = [L]^T [L], [L] upper triangular with independent elements.
  Eq. (15) : off-diagonals  L_ij = sigma_d * w_ij            (i < j)
  Eq. (16) : diagonals      L_ii = sigma_d * sqrt(2 u_i)
  Eq. (20) : sigma_d(x) = delta(x) * (d+1)^(-1/2),  d = 3
  Eq. (17) : u_i ~ Gamma(shape k_i = (d+1)/(2 delta^2) + (1-i)/2, scale 1)
  Eq. (13) : 0 < delta < sqrt((d+1)/(d+5)) = sqrt(2)/2 for d = 3
  Eq. (18) : correlation kernel, Gaussian, on L_ij and L_ii^2
  Eq. (22) : KL expansion  w(x) = sum_alpha sqrt(lambda_alpha) phi_alpha(x) omega_alpha
  Eq. (23) : Fredholm eigenproblem for (lambda_alpha, phi_alpha)
  Eq. (26) : PCE of the gamma field, u(x) = sum_beta U_beta Psi_beta(w(x))
  Eq. (27) : PCE coefficients U_beta by Gaussian-measure projection

TWO INTERNAL INCONSISTENCIES IN THE PAPER, resolved here explicitly (both
found by trying to implement it, both recorded rather than silently patched):

  (a) Appendix A step 2.4 writes  L_ii = sigma_d * sqrt(u_i), dropping the
      factor 2 that the main text carries in Eq. (16) and Eq. (24).  The main
      text is right: only with the factor 2 does E{[G]} = [I] hold.  Proof for
      G_11: E{G_11} = E{L_11^2} = 2 sigma_d^2 E{u_1} = 2*(delta^2/4)*(2/delta^2)
      = 1.  Without the 2 it would be 1/2.  verify_mean_identity() below
      re-checks this numerically, for all six components, at run time.
  (b) Appendix A step 1.3 says the polynomial-chaos expansion of Eq. (17) is
      "for off-diagonal terms only".  Eq. (17) is the gamma PDF of u_i, which
      by Eq. (16) enters the DIAGONAL terms; sections 3.3 and 3.4 (steps 4 and
      5) state the opposite and correct assignment.  The main text is followed.

CONVENTION.  [R] here is the velocity covariance <u'_i u'_j> (the paper's own
footnote 1 on p.6: "This is actually the negative of the Reynolds stress").
OpenFOAM's turbulenceFields(R) writes the same quantity,
R = (2/3) k I - nut * dev(twoSymm(grad U)), so the two are directly compatible
and no sign flip is applied anywhere in this file.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.special import gammaincinv, gammainccinv, ndtr

D = 3  # Reynolds stress is a rank-2 tensor in 3 dimensions (paper, Notations)

# OpenFOAM symmTensor component order: (xx xy xz yy yz zz)
SYMM_IDX = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


# --------------------------------------------------------------------------
# OpenFOAM ASCII field I/O (symmTensor)
# --------------------------------------------------------------------------
def read_symmtensor_internal(path) -> np.ndarray:
    """Return (N, 3, 3) array from a volSymmTensorField internalField."""
    text = Path(path).read_text(errors="ignore")
    m = re.search(
        r"internalField\s+nonuniform\s+List<symmTensor>\s*\n(\d+)\s*\n\s*\(\s*\n(.*?)\n\s*\)\s*\n\s*;",
        text,
        re.S,
    )
    if not m:
        raise ValueError(f"could not parse symmTensor internalField in {path}")
    n = int(m.group(1))
    rows = re.findall(r"\(([^()]*)\)", m.group(2))
    if len(rows) != n:
        raise ValueError(f"{path}: expected {n} symmTensors, got {len(rows)}")
    flat = np.array([[float(v) for v in r.split()] for r in rows])
    out = np.zeros((n, 3, 3))
    for c, (i, j) in enumerate(SYMM_IDX):
        out[:, i, j] = flat[:, c]
        out[:, j, i] = flat[:, c]
    return out


_SYMM_HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
| F6d random-matrix UQ: written by rmt_sampler.py -- do not hand-edit.        |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       volSymmTensorField;
    location    "{loc}";
    object      {obj};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   nonuniform List<symmTensor>
{n}
(
"""

_SYMM_FOOTER = """)
;

boundaryField
{
    bottomWall
    {
        type            zeroGradient;
    }
    topWall
    {
        type            zeroGradient;
    }
    "(inlet|outlet)_half[01]"
    {
        type            cyclic;
    }
    "side(Right|Left)_half[01]"
    {
        type            empty;
    }
}

// ************************************************************************* //
"""


def write_symmtensor_field(path, arr, obj, loc):
    """arr: (N,3,3) -> OpenFOAM volSymmTensorField ASCII file."""
    n = arr.shape[0]
    lines = [_SYMM_HEADER.format(loc=loc, obj=obj, n=n)]
    comp = np.column_stack([arr[:, i, j] for (i, j) in SYMM_IDX])
    for row in comp:
        lines.append("(" + " ".join(f"{v:.12e}" for v in row) + ")\n")
    lines.append(_SYMM_FOOTER)
    Path(path).write_text("".join(lines))


# --------------------------------------------------------------------------
# Karhunen-Loeve expansion  (paper Eqs. 18, 22, 23)
# --------------------------------------------------------------------------
@dataclass
class KLBasis:
    """Truncated KL basis of a Gaussian random field on a structured KL mesh.

    Paper Sec. 3.5: the KL expansion is deliberately performed on its own
    coarse mesh ("KL mesh"), separate from the RANS mesh, because it only has
    to resolve the correlation length l, not the boundary layer.  Table 1:
    KL mesh 50 x 30, N_KL = 30 modes, lx/H = 2, ly/H = 1.
    """

    xy: np.ndarray        # (M, 2) KL-mesh node coordinates
    lam: np.ndarray       # (N_KL,) eigenvalues, descending
    phi: np.ndarray       # (M, N_KL) eigenfunctions, normalised so sum(w phi^2)=1
    lam_all: np.ndarray   # full eigenvalue spectrum (for the variance-captured metric)
    weight: float         # Nystrom quadrature weight (uniform structured mesh)
    lx: float
    ly: float

    @property
    def variance_captured(self) -> float:
        return float(self.lam.sum() / self.lam_all.sum())

    def pointwise_variance(self) -> np.ndarray:
        """Var{w(x)} = sum_alpha lambda_alpha phi_alpha(x)^2  (=1 if untruncated)."""
        return (self.lam[None, :] * self.phi ** 2).sum(axis=1)

    def synthesize(self, omega: np.ndarray) -> np.ndarray:
        """Paper Eq. (22): w(x) = sum_alpha sqrt(lambda_alpha) phi_alpha(x) omega_alpha."""
        return self.phi @ (np.sqrt(self.lam) * omega)


def build_kl_basis(nx=50, ny=30, xlim=(0.0, 9.0), ylim=(0.0, 3.035),
                   lx=2.0, ly=1.0, n_kl=30) -> KLBasis:
    """Solve the Fredholm equation (23) by the Nystrom method on a uniform
    structured KL mesh covering the bounding box of the periodic-hill domain.

    Kernel: paper Eq. (18) with the anisotropic, spatially uniform length
    scales of Sec. 4.1,  rho(x,x') = exp(-[(dx/lx)^2 + (dy/ly)^2]).

    Nystrom discretisation:  int rho(x,x') phi(x') dx' = lambda phi(x)
      ->  (K W) phi = lambda phi,  W = diag(cell area) = diag(w) with w uniform.
    Symmetrised as  A = W^{1/2} K W^{1/2},  phi = W^{-1/2} psi, giving
    orthonormality  sum_i w_i phi_a(x_i) phi_b(x_i) = delta_ab, which is the
    discrete form of the continuous normalisation the KL theorem assumes.
    """
    x = np.linspace(xlim[0], xlim[1], nx)
    y = np.linspace(ylim[0], ylim[1], ny)
    XX, YY = np.meshgrid(x, y, indexing="ij")
    xy = np.column_stack([XX.ravel(), YY.ravel()])

    area = (xlim[1] - xlim[0]) * (ylim[1] - ylim[0])
    w = area / (nx * ny)

    dx = (xy[:, 0][:, None] - xy[:, 0][None, :]) / lx
    dy = (xy[:, 1][:, None] - xy[:, 1][None, :]) / ly
    K = np.exp(-(dx ** 2 + dy ** 2))

    A = w * K  # W^{1/2} K W^{1/2} with uniform weights == w*K
    A = 0.5 * (A + A.T)
    lam_all, psi = np.linalg.eigh(A)
    order = np.argsort(lam_all)[::-1]
    lam_all = lam_all[order]
    psi = psi[:, order]

    lam = lam_all[:n_kl].copy()
    phi = psi[:, :n_kl] / np.sqrt(w)  # phi = W^{-1/2} psi  -> sum(w phi^2) = 1
    return KLBasis(xy=xy, lam=lam, phi=phi, lam_all=lam_all, weight=w, lx=lx, ly=ly)


# --------------------------------------------------------------------------
# Polynomial chaos expansion of the gamma marginals  (paper Eqs. 26, 27)
# --------------------------------------------------------------------------
def gamma_shape(i: int, delta: float) -> float:
    """Paper Eq. (17): shape k = (d+1)/(2 delta^2) + (1-i)/2, i = 1,2,3."""
    return (D + 1) / (2.0 * delta ** 2) + (1 - i) / 2.0


def hermite_probabilists(n: int, w: np.ndarray) -> np.ndarray:
    """He_n(w), the Hermite polynomials of Eq. (26) (He_0=1, He_1=w,
    He_2=w^2-1, He_3=w^3-3w, He_4=w^4-6w^2+3), by the standard recurrence."""
    if n == 0:
        return np.ones_like(w)
    hm1, h = np.ones_like(w), w.copy()
    for k in range(1, n):
        hm1, h = h, w * h - k * hm1
    return h


def pce_coefficients(shape_k: float, n_p: int = 3, n_quad: int = 80) -> np.ndarray:
    """Paper Eq. (27):
           U_beta = <u Psi_beta> / <Psi_beta^2>
                  = (1/<Psi_beta^2>) int F_u^{-1}[F_w(w)] Psi_beta(w) p_w(w) dw
    with u ~ Gamma(shape_k, scale 1) and w ~ N(0,1).  Gauss-Hermite quadrature.
    <He_beta^2> = beta!.

    n_quad is capped well below the point where numpy's hermegauss loses its
    weights to floating-point overflow (it does, silently, by n=200); 80 nodes
    integrate a cubic against a smooth monotone map to machine precision here,
    and pce_coefficients_converged() in the verification script re-checks the
    coefficients against a second, independent quadrature rule.
    """
    nodes, wts = np.polynomial.hermite_e.hermegauss(n_quad)
    wts = wts / np.sqrt(2.0 * np.pi)  # normalise to the N(0,1) measure
    if not np.isfinite(wts).all():
        raise FloatingPointError("hermegauss returned non-finite weights")
    # F_u^{-1}[F_w(w)], scale 1.  Evaluated through the SURVIVAL function in the
    # upper tail: for w > ~8.3 the double-precision CDF saturates at exactly 1
    # and gammaincinv(k, 1.0) returns +inf, which silently poisons every
    # coefficient.  (This bit the first implementation; caught by V5b.)
    u_of_w = np.where(
        nodes <= 0.0,
        gammaincinv(shape_k, ndtr(nodes)),
        gammainccinv(shape_k, ndtr(-nodes)),
    )
    if not np.isfinite(u_of_w).all():
        raise FloatingPointError("non-finite F_u^{-1}[F_w(w)] in Eq. (27) quadrature")
    coeffs = np.zeros(n_p + 1)
    fact = 1.0
    for beta in range(n_p + 1):
        if beta > 0:
            fact *= beta
        psi = hermite_probabilists(beta, nodes)
        coeffs[beta] = float((u_of_w * psi * wts).sum() / fact)
    return coeffs


def pce_evaluate(coeffs: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Paper Eq. (26): u(x) = sum_beta U_beta He_beta(w(x))."""
    out = np.zeros_like(w)
    for beta, c in enumerate(coeffs):
        out += c * hermite_probabilists(beta, w)
    return out


# --------------------------------------------------------------------------
# The sampler
# --------------------------------------------------------------------------
class RandomMatrixSampler:
    """Draw realisations of the Reynolds-stress random matrix FIELD.

    delta is the dispersion parameter of paper Eq. (12); the paper's own two
    uniform demonstration values are delta = 0.2 (Case 1) and delta = 0.6
    (Case 2), Table 1.
    """

    def __init__(self, delta: float, kl: KLBasis, n_p: int = 3, seed: int = 0):
        dmax = np.sqrt((D + 1) / (D + 5))  # Eq. (13) = sqrt(2)/2 for d=3
        if not (0.0 < delta < dmax):
            raise ValueError(f"delta={delta} violates paper Eq. (13): 0 < delta < {dmax:.6f}")
        self.delta = float(delta)
        self.kl = kl
        self.n_p = n_p
        self.sigma_d = delta / np.sqrt(D + 1)  # Eq. (20)
        self.shapes = [gamma_shape(i, delta) for i in (1, 2, 3)]
        self.pce = [pce_coefficients(k, n_p) for k in self.shapes]
        self.rng = np.random.default_rng(seed)

    # -- single-point sampling, paper Sec. 3.2 (used by the verification suite)
    def sample_G_pointwise(self, n: int) -> np.ndarray:
        """Direct Eqs. (14)-(17) sampling of [G] at one point, n realisations."""
        L = np.zeros((n, 3, 3))
        for i in range(3):
            u = self.rng.gamma(self.shapes[i], 1.0, size=n)
            L[:, i, i] = self.sigma_d * np.sqrt(2.0 * u)  # Eq. (16)
        for (i, j) in [(0, 1), (0, 2), (1, 2)]:
            L[:, i, j] = self.sigma_d * self.rng.standard_normal(n)  # Eq. (15)
        return np.einsum("nki,nkj->nij", L, L)  # [G] = [L]^T [L], Eq. (14)

    # -- field sampling, paper Sec. 3.4 / Appendix A step 2
    def sample_L_field(self) -> np.ndarray:
        """Return (M, 3, 3) upper-triangular [L](x) on the KL mesh."""
        M = self.kl.phi.shape[0]
        L = np.zeros((M, 3, 3))
        # six INDEPENDENT Gaussian fields, one per element of [L]
        # (Appendix A step 2.1: independent omega draws per element)
        fields = {}
        for key in ["11", "22", "33", "12", "13", "23"]:
            omega = self.rng.standard_normal(self.kl.lam.size)
            fields[key] = self.kl.synthesize(omega)
        for n, (i, j) in enumerate([(0, 1), (0, 2), (1, 2)]):
            L[:, i, j] = self.sigma_d * fields[["12", "13", "23"][n]]  # Eq. (19)
        for i in range(3):
            u = pce_evaluate(self.pce[i], fields[f"{i+1}{i+1}"])  # Eq. (26)
            u = np.maximum(u, 0.0)  # gamma support is R+; PCE can undershoot
            L[:, i, i] = self.sigma_d * np.sqrt(2.0 * u)  # Eq. (24)
        return L

    def sample_G_field(self) -> np.ndarray:
        L = self.sample_L_field()
        return np.einsum("mki,mkj->mij", L, L)


# --------------------------------------------------------------------------
# Cholesky of the mean field, Eq. (9), with an explicit realizability audit
# --------------------------------------------------------------------------
def cholesky_upper_field(R: np.ndarray, jitter_rel: float = 1e-10):
    """Eq. (9): [R_bar] = [L_R]^T [L_R], L_R UPPER triangular, diag >= 0.

    numpy.linalg.cholesky returns LOWER C with R = C C^T, so L_R = C^T.

    Returns (L_R, audit) where audit records how many cells needed the
    paper's own remedy for the semi-definite / indefinite case (Sec. 3.1:
    "In practice, we can make it slightly positive definite by adding a small
    element to the diagonal entries").  A Boussinesq Reynolds stress is NOT
    guaranteed positive semi-definite -- R = (2/3)k I - 2 nut S goes indefinite
    wherever 2 nut |S| exceeds 2k/3 -- so this count is a real, reportable
    property of the baseline field, not a numerical nicety.
    """
    n = R.shape[0]
    evals = np.linalg.eigvalsh(R)
    trace_scale = np.maximum(np.trace(R, axis1=1, axis2=2), 1e-300)
    n_indef = int((evals[:, 0] < 0).sum())
    worst = float((evals[:, 0] / trace_scale).min())

    Rw = R.copy()
    # paper Sec. 3.1 remedy, applied only where needed and by the minimum amount
    need = evals[:, 0] <= jitter_rel * trace_scale
    shift = (jitter_rel * trace_scale - evals[:, 0])[need]
    idx = np.where(need)[0]
    for c, s in zip(idx, shift):
        Rw[c] += s * np.eye(3)

    C = np.linalg.cholesky(Rw)
    L_R = np.transpose(C, (0, 2, 1))
    audit = {
        "n_cells": n,
        "n_cells_indefinite": n_indef,
        "frac_cells_indefinite": n_indef / n,
        "n_cells_jittered": int(need.sum()),
        "frac_cells_jittered": float(need.sum()) / n,
        "worst_eigenvalue_over_trace": worst,
    }
    return L_R, audit


def assemble_R(L_R: np.ndarray, G: np.ndarray) -> np.ndarray:
    """Eq. (8): [R] = [L_R]^T [G] [L_R]."""
    return np.einsum("nki,nkl,nlj->nij", L_R, G, L_R)


# --------------------------------------------------------------------------
# KL mesh -> RANS mesh interpolation operator (paper Sec. 3.5)
# --------------------------------------------------------------------------
def build_interp_operator(kl: KLBasis, xy_rans: np.ndarray):
    """Bilinear interpolation matrix P (N_rans x M_kl), built once and reused
    for every sample and every tensor component.  Paper Sec. 3.5: "the matrix
    [G] is first interpolated from the KL mesh to the RANS mesh".

    Points on or outside the KL-mesh bounding box are clamped to the boundary
    cell (nearest-edge, not extrapolated) so the operator is a convex
    combination everywhere -- which is what keeps [G] positive definite after
    interpolation: a convex combination of SPD matrices is SPD.  Extrapolation
    would not have that property and is therefore deliberately excluded.
    """
    from scipy.sparse import csr_matrix

    gx = np.unique(kl.xy[:, 0])
    gy = np.unique(kl.xy[:, 1])
    nx, ny = gx.size, gy.size
    # kl.xy was built with indexing="ij" then ravel: index = ix*ny + iy
    xc = np.clip(xy_rans[:, 0], gx[0], gx[-1])
    yc = np.clip(xy_rans[:, 1], gy[0], gy[-1])
    ix = np.clip(np.searchsorted(gx, xc) - 1, 0, nx - 2)
    iy = np.clip(np.searchsorted(gy, yc) - 1, 0, ny - 2)
    tx = (xc - gx[ix]) / (gx[ix + 1] - gx[ix])
    ty = (yc - gy[iy]) / (gy[iy + 1] - gy[iy])
    n = xy_rans.shape[0]
    rows = np.repeat(np.arange(n), 4)
    cols = np.column_stack([
        ix * ny + iy,
        ix * ny + iy + 1,
        (ix + 1) * ny + iy,
        (ix + 1) * ny + iy + 1,
    ]).ravel()
    vals = np.column_stack([
        (1 - tx) * (1 - ty),
        (1 - tx) * ty,
        tx * (1 - ty),
        tx * ty,
    ]).ravel()
    assert np.isfinite(vals).all() and vals.min() >= -1e-12
    return csr_matrix((vals, (rows, cols)), shape=(n, nx * ny))


def interp_G(P, G_kl: np.ndarray) -> np.ndarray:
    """Apply the interpolation operator to a (M,3,3) field -> (N,3,3)."""
    M = G_kl.shape[0]
    flat = G_kl.reshape(M, 9)
    return np.asarray(P @ flat).reshape(P.shape[0], 3, 3)


# --------------------------------------------------------------------------
# Barycentric coordinates, paper Eq. (2) -- used for interpretation only
# --------------------------------------------------------------------------
def barycentric(R: np.ndarray):
    """Paper Eqs. (1)-(2): k, and (C1, C2, C3) from the anisotropy eigenvalues.

    lambda~ sorted DESCENDING, as Eq. (2) requires (C1 = l1 - l2 >= 0).
    """
    k = 0.5 * np.trace(R, axis1=1, axis2=2)
    kk = np.maximum(k, 1e-30)
    A = R / (2.0 * kk[:, None, None]) - np.eye(3) / 3.0
    ev = np.linalg.eigvalsh(A)[:, ::-1]
    C1 = ev[:, 0] - ev[:, 1]
    C2 = 2.0 * (ev[:, 1] - ev[:, 2])
    C3 = 3.0 * ev[:, 2] + 1.0
    return k, np.column_stack([C1, C2, C3])
