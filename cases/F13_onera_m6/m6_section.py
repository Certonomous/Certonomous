"""ONERA M6 planform + section, MEASURED from the registered STL.

Registered geometry (F13_ONERA_M6_PREREGISTRATION.md section 1):
    sdk/geometry/onera_m6_wing.stl -- 12,480 triangles, header
    "Certonomous patch-extracted STL".

Nothing here is taken from memory or from the open literature.  Every number is
read off that file.  The planform fit and the mean section are both printed with
their residuals so a reader can see how good the fit is rather than trust it.
"""
import struct
import numpy as np

STL = "/home/ubuntu/Certonomous/sdk/geometry/onera_m6_wing.stl"


def read_stl(path=STL):
    with open(path, "rb") as f:
        hdr = f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        raw = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
    tri = np.zeros((n, 3, 3))
    for k in range(3):
        tri[:, k, :] = raw[:, 12 + 12 * k: 24 + 12 * k].copy().view("<f4").reshape(n, 3)
    return hdr, tri


def slice_z(tri, zc):
    d = tri[:, :, 2] - zc
    pts = []
    for a, b in ((0, 1), (1, 2), (2, 0)):
        da, db = d[:, a], d[:, b]
        m = ((da <= 0) & (db >= 0)) | ((db <= 0) & (da >= 0))
        m &= np.abs(db - da) > 1e-14
        if not m.any():
            continue
        s = (-da[m] / (db[m] - da[m]))[:, None]
        pts.append(tri[m][:, a, :] + s * (tri[m][:, b, :] - tri[m][:, a, :]))
    return np.vstack(pts) if pts else np.zeros((0, 3))


class M6Geometry:
    """Planform + normalised symmetric section, all measured."""

    def __init__(self, verbose=True):
        self.hdr, self.tri = read_stl()
        P = self.tri.reshape(-1, 3)
        self.bounds = (P.min(axis=0), P.max(axis=0))
        self.report = {}
        self._fit_planform(verbose)
        self._mean_section(verbose)

    # -- planform: xle(z) = TAN * z + X0 ; c(z) = C0 - CS * z, over the prismatic part
    def _fit_planform(self, verbose):
        zs = np.linspace(0.02, 1.15, 24)
        xle, ch = [], []
        for z in zs:
            S = slice_z(self.tri, z)
            xle.append(S[:, 0].min())
            ch.append(S[:, 0].max() - S[:, 0].min())
        xle = np.array(xle); ch = np.array(ch)
        A = np.vstack([zs, np.ones_like(zs)]).T
        (self.TAN, self.X0), r1, *_ = np.linalg.lstsq(A, xle, rcond=None)
        (mCS, self.C0), r2, *_ = np.linalg.lstsq(A, ch, rcond=None)
        self.CS = -mCS
        self.res_xle = float(np.abs(A @ [self.TAN, self.X0] - xle).max())
        self.res_c = float(np.abs(A @ [mCS, self.C0] - ch).max())
        # tip = last station where the linear planform still holds to 1e-3 c_root
        zt = np.linspace(1.15, 1.2164, 400)
        z_tip = 1.15
        for z in zt:
            S = slice_z(self.tri, z)
            if len(S) < 3:
                break
            c = S[:, 0].max() - S[:, 0].min()
            if abs(c - (self.C0 - self.CS * z)) > 1e-3 * self.C0:
                break
            z_tip = z
        self.z_tip_measured = float(z_tip)
        self.z_stl_max = float(self.bounds[1][2])
        if verbose:
            print(f"  planform  xle(z) = {self.TAN:.7f} z + {self.X0:+.3e}   max resid {self.res_xle:.2e} m"
                  f"   (LE sweep {np.degrees(np.arctan(self.TAN)):.4f} deg)")
            print(f"  planform  c(z)   = {self.C0:.7f} - {self.CS:.7f} z        max resid {self.res_c:.2e} m")
            print(f"  prismatic to z = {self.z_tip_measured:.5f} m; STL closes at z = {self.z_stl_max:.5f} m"
                  f"  -> rounded cap of {self.z_stl_max - self.z_tip_measured:.5f} m"
                  f" = {(self.z_stl_max - self.z_tip_measured)/self.C0*100:.2f} % c_root")

    # -- mean normalised half-thickness t2(x/c), symmetric, sharp TE
    def _mean_section(self, verbose):
        P = self.tri.reshape(-1, 3)
        m = (P[:, 2] > 0.02) & (P[:, 2] < 1.15)
        Q = P[m]
        c = self.C0 - self.CS * Q[:, 2]
        xn = (Q[:, 0] - (self.TAN * Q[:, 2] + self.X0)) / c
        yn = Q[:, 1] / c
        ok = (xn > -1e-6) & (xn < 1 + 1e-6)
        xn, yn = np.clip(xn[ok], 0.0, 1.0), yn[ok]
        # cosine-spaced bins, mean |y| per bin (upper/lower averaged together: the
        # section is symmetric -- the ASYMMETRY IS MEASURED AND REPORTED, not assumed)
        th = np.linspace(0.0, np.pi, 241)
        edges = 0.5 * (1 - np.cos(th))
        idx = np.clip(np.searchsorted(edges, xn) - 1, 0, len(edges) - 2)
        xs, ts, asym = [], [], []
        for b in range(len(edges) - 1):
            s = idx == b
            if s.sum() < 4:
                continue
            up = yn[s][yn[s] > 0]; lo = yn[s][yn[s] < 0]
            if len(up) < 2 or len(lo) < 2:
                continue
            xs.append(xn[s].mean()); ts.append(0.5 * (up.mean() + (-lo).mean()))
            asym.append(abs(up.mean() - (-lo).mean()))
        xs = np.array(xs); ts = np.array(ts)
        # anchor a sharp LE point and a sharp TE
        xs = np.concatenate([[0.0], xs, [1.0]])
        ts = np.concatenate([[0.0], ts, [0.0]])
        o = np.argsort(xs); xs, ts = xs[o], ts[o]
        _, u = np.unique(np.round(xs, 12), return_index=True)
        self.xs, self.ts = xs[u], ts[u]
        self.max_asym = float(np.max(asym))
        self.tc_max = float(2 * self.ts.max())
        self.tc_max_at = float(self.xs[np.argmax(self.ts)])
        if verbose:
            print(f"  section   {len(self.xs)} stations; t/c_max = {self.tc_max:.5f} at x/c = {self.tc_max_at:.4f};"
                  f"  max upper/lower asymmetry {self.max_asym:.2e} c (symmetrised)")

    def t2(self, xc):
        """half-thickness / c at chord fraction xc, sqrt-mapped near the round LE."""
        xc = np.asarray(xc, dtype=float)
        # sqrt stretch so the round nose interpolates without a kink
        return np.interp(np.sqrt(xc), np.sqrt(self.xs), self.ts)

    def chord(self, z):
        return self.C0 - self.CS * np.minimum(z, self.z_tip)

    def xle(self, z):
        return self.TAN * np.minimum(z, self.z_tip) + self.X0
