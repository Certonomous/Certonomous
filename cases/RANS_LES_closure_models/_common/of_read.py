"""OpenFOAM ASCII field readers for the Closure Challenge benchmark data.

Two file dialects live side by side in the benchmark release:

  (a) standard OpenFOAM fields with a FoamFile header  -> Ofpp.parse_internal_field
  (b) headerless fields shipped by the challenge authors for the LES/DNS truth on
      the DUCT and NASA_2DWMH cases, whose first line is literally
          U_LES nonuniform List<vector>
      and which Ofpp returns None for.

read_field() dispatches between them and always returns a numpy array with the
per-cell values, shape (N,) / (N,3) / (N,6) / (N,9).

Conventions established by inspection of the data (documented so nothing here
rests on an assumed sign):

  * symmTensor component order is (xx, xy, xz, yy, yz, zz).
  * tauij_LES is the FULL Reynolds stress <u_i' u_j'>; verified because
    0.5*trace(tauij_LES) reproduces k_LES to machine precision on
    alpha_15_13929_4048 (corr = 1 - 4.3e-14, identical min/max).
  * tauij_B (== tauij_B_bouss in every shipped case, checked bitwise) is the
    Boussinesq stress (2/3) k delta_ij - 2 nu_t S_ij built from the RANS fields.
  * gradU[i][j] = d(U_j)/d(x_i)  (OpenFOAM's fvc::grad convention), i.e. the
    velocity-gradient tensor A_ij = dU_i/dx_j is gradU transposed. Verified on
    the near-wall cell of alpha_15_13929_4048 where gradU[1][0] = dU_x/dy = 12.88
    is the large component, and because -2*nu_t*S_xy reproduces tauij_B_xy exactly.
  * bijDelta, kDeficit and sigma ship as `uniform 0` placeholders in every case
    (they are input slots for a corrected solve, NOT truth). Any anisotropy
    discrepancy must be computed from tauij_LES / k_LES here.

No file in the benchmark tree is written by this module.
"""
from __future__ import annotations

import os
import re
import numpy as np

try:
    from Ofpp import parse_internal_field as _ofpp_parse
except ImportError:  # pragma: no cover
    _ofpp_parse = None

_NCOMP = {"scalar": 1, "vector": 3, "symmTensor": 6, "tensor": 9}


def _read_headerless(path):
    """Parse the challenge's headerless '<name> nonuniform List<type>' dialect."""
    with open(path, "r") as fh:
        txt = fh.read()
    m = re.search(r"nonuniform\s+List<(\w+)>", txt)
    if m is None:
        raise ValueError(f"{path}: no 'nonuniform List<...>' marker")
    ncomp = _NCOMP[m.group(1)]
    rest = txt[m.end():]
    m2 = re.search(r"(\d+)\s*\(", rest)
    n = int(m2.group(1))
    body = rest[m2.end():]
    # strip the trailing ')' / ');' and any boundaryField block that follows
    end = body.find("\n)")
    if end >= 0:
        body = body[:end]
    nums = np.fromstring(body.replace("(", " ").replace(")", " "), sep=" ")
    if nums.size != n * ncomp:
        raise ValueError(f"{path}: expected {n}x{ncomp} values, got {nums.size}")
    return nums.reshape(n, ncomp) if ncomp > 1 else nums


def read_field(path):
    """Read one OpenFOAM internal field, any of the three dialects. -> ndarray."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    # third dialect (CBFS only): a stub file whose internalField is an #include
    # of interpolatedFields/<name>_internalField.
    with open(path, "r") as fh:
        head = fh.read(4096)
    m = re.search(r"internalField\s+\$(\w+)_internalField", head)
    if m is not None:
        inc = os.path.join(os.path.dirname(path), "interpolatedFields",
                           m.group(1) + "_internalField")
        if os.path.exists(inc):
            return _read_headerless(inc)
    if _ofpp_parse is not None:
        try:
            v = _ofpp_parse(path)
        except Exception:
            v = None
        if v is not None:
            return np.asarray(v)
    return _read_headerless(path)


def read_field_expand(path, ncells):
    """read_field, but broadcast a `uniform` value to ncells rows."""
    v = read_field(path)
    v = np.asarray(v)
    if v.ndim == 0:
        return np.full(ncells, float(v))
    if v.ndim == 1 and v.shape[0] != ncells:
        # a uniform vector/tensor value
        return np.tile(v[None, :], (ncells, 1))
    return v


def latest_time_dir(case_dir):
    """Highest-numbered non-zero time directory in an OpenFOAM case."""
    times = []
    for name in os.listdir(case_dir):
        if not os.path.isdir(os.path.join(case_dir, name)):
            continue
        try:
            t = float(name)
        except ValueError:
            continue
        if t > 0:
            times.append((t, name))
    if not times:
        raise RuntimeError(f"{case_dir}: no non-zero time directory")
    return max(times)[1]


def sym_to_full(t6):
    """(N,6) symmTensor -> (N,3,3)."""
    n = t6.shape[0]
    out = np.empty((n, 3, 3))
    xx, xy, xz, yy, yz, zz = (t6[:, i] for i in range(6))
    out[:, 0, 0] = xx; out[:, 0, 1] = xy; out[:, 0, 2] = xz
    out[:, 1, 0] = xy; out[:, 1, 1] = yy; out[:, 1, 2] = yz
    out[:, 2, 0] = xz; out[:, 2, 1] = yz; out[:, 2, 2] = zz
    return out


def anisotropy(tau_full, k, k_floor_frac=1e-4, k_ref=None):
    """b_ij = tau_ij / (2k) - delta_ij/3 from a full (N,3,3) stress and k.

    Cells whose k falls below k_floor_frac * k_ref are masked out (returned in
    the boolean `valid` array) rather than silently amplified: the LES
    interpolation onto the RANS mesh produces a handful of cells with k <= 0.
    """
    if k_ref is None:
        k_ref = np.mean(np.abs(k))
    valid = k > k_floor_frac * k_ref
    kk = np.where(valid, k, np.nan)
    b = tau_full / (2.0 * kk[:, None, None]) - np.eye(3)[None] / 3.0
    return b, valid


def barycentric(b):
    """Barycentric coordinates (C1c, C2c, C3c) of the anisotropy tensor.

    Banerjee et al. (2007) mapping, as used by Emory et al. (2013) and
    Iaccarino et al. (2017). Eigenvalues sorted descending l1 >= l2 >= l3:
        C1c = l1 - l2                (one-component)
        C2c = 2 (l2 - l3)            (two-component)
        C3c = 3 l3 + 1               (three-component / isotropic)
    They sum to 1 by construction; all three >= 0 iff the state is realisable.
    """
    lam = np.linalg.eigvalsh(b)              # ascending
    lam = lam[:, ::-1]                       # descending l1 >= l2 >= l3
    c1 = lam[:, 0] - lam[:, 1]
    c2 = 2.0 * (lam[:, 1] - lam[:, 2])
    c3 = 3.0 * lam[:, 2] + 1.0
    return np.stack([c1, c2, c3], axis=1), lam


def realisability_violation(b, tol=0.0):
    """Fraction-wise realisability test on the barycentric coordinates.

    Schumann (1977) realisability of the Reynolds stress is equivalent, for the
    normalised anisotropy tensor, to the eigenvalue state lying inside the
    barycentric triangle, i.e. all three barycentric coordinates >= 0.
    Returns (violating_mask, min_coord) with min_coord the most negative
    barycentric coordinate per cell (0 if realisable).
    """
    c, _ = barycentric(b)
    mn = c.min(axis=1)
    return mn < -tol, mn


# ------------------------------------------------- structured-mesh gradients
# The DUCT, PH_Breuer, CBFS and NASA_2DWMH cases ship no gradU field, so the
# velocity gradient (needed for the Boussinesq stress and for any invariant
# feature set) has to be computed here. Every one of these meshes is a
# structured 2-D body-fitted block with the "fast" logical index i running
# first, so a curvilinear chain-rule gradient in index space is exact to second
# order in the interior. validate_gradient() below checks it against the
# gradU that OpenFOAM itself wrote on the periodic-hill cases.

def plane_axes(C, tol=1e-12):
    """Which two coordinate axes the 2-D mesh lives in, and the thin one."""
    ext = C.max(axis=0) - C.min(axis=0)
    thin = int(np.argmin(ext))
    keep = [a for a in range(3) if a != thin]
    return keep, thin


def structured_shape(C):
    """(n_slow, n_fast) of a structured 2-D mesh written with i fastest.

    Detected geometrically: walking along the fast index moves away from cell 0
    monotonically until the row wraps, at which point the distance from cell 0
    drops back to roughly one cell spacing. The first such index that also
    divides the cell count is n_fast.
    """
    n = C.shape[0]
    d1 = np.linalg.norm(C[1] - C[0])
    dist = np.linalg.norm(C - C[0], axis=1)
    for i in range(3, n // 2 + 1):
        if n % i == 0 and dist[i] < 1.6 * d1:
            return n // i, i
    raise RuntimeError("structured_shape: no fast-index period found")


def structured_gradient(C, f):
    """d f / d x_j on a structured 2-D mesh. f is (N,) or (N,m).

    Returns (N, 3) for scalar f, (N, m, 3) for vector f. The derivative along
    the thin (homogeneous) axis is set to zero, which is exact for these
    statistically 2-D flows.
    """
    keep, thin = plane_axes(C)
    ns, nf = structured_shape(C)
    a = C[:, keep[0]].reshape(ns, nf)
    b = C[:, keep[1]].reshape(ns, nf)
    a_xi = np.gradient(a, axis=1); a_et = np.gradient(a, axis=0)
    b_xi = np.gradient(b, axis=1); b_et = np.gradient(b, axis=0)
    J = a_xi * b_et - a_et * b_xi
    scalar = (f.ndim == 1)
    F = f[:, None] if scalar else f
    m = F.shape[1]
    out = np.zeros((C.shape[0], m, 3))
    for c in range(m):
        g = F[:, c].reshape(ns, nf)
        g_xi = np.gradient(g, axis=1); g_et = np.gradient(g, axis=0)
        out[:, c, keep[0]] = ((g_xi * b_et - g_et * b_xi) / J).ravel()
        out[:, c, keep[1]] = ((g_et * a_xi - g_xi * a_et) / J).ravel()
    return out[:, 0, :] if scalar else out


def validate_gradient(case_dir, time_dir):
    """Compare structured_gradient(U) with the shipped gradU. Returns a dict."""
    C = read_field(os.path.join(case_dir, time_dir, "C"))
    U = read_field(os.path.join(case_dir, time_dir, "U"))
    G = read_field(os.path.join(case_dir, time_dir, "gradU")).reshape(-1, 3, 3)
    A_of = G.transpose(0, 2, 1)                     # dU_i/dx_j
    A_me = structured_gradient(C, U)                # dU_i/dx_j
    keep, thin = plane_axes(C)
    sel = np.ix_(np.arange(C.shape[0]), keep, keep)
    num = np.linalg.norm((A_me - A_of)[sel], axis=(1, 2))
    den = np.linalg.norm(A_of[sel], axis=(1, 2))
    ns, nf = structured_shape(C)
    interior = np.zeros((ns, nf), bool); interior[1:-1, 1:-1] = True
    interior = interior.ravel()
    return {"n_fast": nf, "n_slow": ns,
            "rel_L2_all": float(np.sqrt((num ** 2).sum() / (den ** 2).sum())),
            "rel_L2_interior": float(np.sqrt((num[interior] ** 2).sum()
                                             / (den[interior] ** 2).sum())),
            "median_rel_interior": float(np.median(num[interior]
                                                   / np.maximum(den[interior], 1e-30)))}
