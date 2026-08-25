#!/usr/bin/env python3
"""F1 (ONERA M6) nested C-H mesh family -- levels m = 1, 2, 4.

Registered by verification/campaign/F13_ONERA_M6_PREREGISTRATION.md section 5 and
by AMENDMENT 2 at its foot.  The file name is a FROZEN PATH TOKEN (section 9);
the instrument writes constant/polyMesh DIRECTLY rather than a blockMeshDict,
for the measured reason recorded in AMENDMENT 2:

    OpenFOAM v2606 blockMesh ABORTS (rc 134) on a repeated-vertex prism block,
    and the same block written with two distinct-but-coincident vertices yields
    48 ZERO-AREA FACES and "Failed 2 mesh checks" from checkMesh.

    The tip fill registered by AMENDMENT 2 is 47m x 12m x 6m -- a lens whose
    leading- and trailing-edge ends are single lines.  It CANNOT be expressed in
    blockMesh v2606 without those zero-area faces.  Written as polyMesh the
    collapsed ends are ordinary PRISM cells with five real faces and no
    zero-area face exists.

Topology, all counts exactly as frozen:
    wrap   i : 16m wake_lo + 36m S2_lo + 11m S1_lo + 11m S1_up + 36m S2_up + 16m wake_up = 126m
    normal j : 32m, exponential beta = 10.575549 over 20 c_root
    span   k : 20m root->tip + 6m outboard, uniform            = 26m
    C-grid cells   126m * 32m * 26m = 104832 m^3
    tip fill cells  47m * 12m *  6m =   3384 m^3
    TOTAL                            = 108216 m^3
        m=1  108,216   m=2  865,728   m=4  6,925,824      r = 2.000000000 exactly
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m6_section import M6Geometry  # noqa: E402

# ---------------------------------------------------------------- frozen recipe
BETA_N = 10.575549          # wall-normal shape parameter, FIXED across levels
BETA_S1 = np.log(12.5)      # 2.525729, chordwise LE block, FIXED across levels
C_ROOT_REG = 0.8059         # section 1, from cases/dafoam/ladder-a/A3_onera_m6.json
FARFIELD = 20.0 * C_ROOT_REG   # 16.118 m -- section 7 "Far field 20 c_root"
N_WAKE, N_S2, N_S1 = 16, 36, 11
N_NORM, N_SPAN_WING, N_SPAN_OUT = 32, 20, 6
N_FILL_CROSS = 12


def stretch(n, beta):
    """(e^{beta i/n} - 1)/(e^{beta} - 1), i = 0..n.  Nested by construction:
    sampling at i/n and 2i/2n gives the SAME point, exactly."""
    i = np.arange(n + 1)
    return (np.exp(beta * i / n) - 1.0) / (np.exp(beta) - 1.0)


def grading_E(n, beta):
    """last/first cell -- the simpleGrading number section 5 quotes per level."""
    return float(np.exp(beta * (n - 1) / n))


class Mesh:
    def __init__(self, m, geo, verbose=True, nofill=False):
        self.nofill = nofill
        self.m = m
        self.g = geo
        self.NW = 126 * m
        self.NN = N_NORM * m
        self.NS = (N_SPAN_WING + N_SPAN_OUT) * m
        self.NSW = N_SPAN_WING * m           # k index of the wing tip plane
        self.NA = (N_S1 + N_S2) * m          # 47m, chordwise stations LE->TE
        self.NB = N_FILL_CROSS * m           # 12m across the lens
        self.nw, self.n2, self.n1 = N_WAKE * m, N_S2 * m, N_S1 * m
        self.i_te_lo = self.nw               # i of the lower TE
        self.i_le = self.nw + self.n2 + self.n1   # i of the LE  ( = 63m )
        self.i_te_up = self.NW - self.nw     # i of the upper TE ( = 110m )
        self.z_tip = geo.z_tip
        self.verbose = verbose
        self._chordwise()
        self._points()

    # ---------------------------------------------------------------- chordwise
    def _chordwise(self):
        """x/c stations from the LE (index 0) to the TE (index NA)."""
        s1 = stretch(self.n1, BETA_S1) * 0.10                 # 0 -> 0.10, LE-clustered
        s2 = 0.10 + np.arange(1, self.n2 + 1) / self.n2 * 0.90  # 0.10 -> 1.00, uniform
        self.xc = np.concatenate([s1, s2])
        assert len(self.xc) == self.NA + 1
        assert abs(self.xc[0]) < 1e-15 and abs(self.xc[-1] - 1.0) < 1e-12

    # ------------------------------------------------------------------- points
    def _points(self):
        m, NW, NN, NS = self.m, self.NW, self.NN, self.NS
        g = self.g
        R = FARFIELD
        XEXIT = FARFIELD
        dz = self.z_tip / (N_SPAN_WING * m)
        self.z = np.arange(NS + 1) * dz
        self.z_out = float(self.z[-1])

        # --- inner curve (j = 0) and outer curve (j = NN) in the (x,y) plane, per k
        xin = np.zeros((NW + 1, NS + 1)); yin = np.zeros_like(xin)
        xou = np.zeros_like(xin);         you = np.zeros_like(xin)

        xcs = self.xc
        t2 = g.t2(xcs)
        # wake abscissa, uniform in x from TE to the exit
        wf = np.arange(self.nw + 1) / self.nw

        for k, zk in enumerate(self.z):
            c = g.chord(zk); xl = g.xle(zk)
            xs = xl + xcs * c
            ys = t2 * c
            xte = xl + c
            # ---- inner: exit -> TE (wake lo) -> LE (lower) -> TE (upper) -> exit
            xw = XEXIT + (xte - XEXIT) * wf                        # nw+1 pts
            xin[0:self.nw + 1, k] = xw;                 yin[0:self.nw + 1, k] = 0.0
            lo = slice(self.nw, self.i_le + 1)                     # NA+1 pts, TE->LE
            xin[lo, k] = xs[::-1];                      yin[lo, k] = -ys[::-1]
            up = slice(self.i_le, self.i_te_up + 1)                # NA+1 pts, LE->TE
            xin[up, k] = xs;                            yin[up, k] = ys
            xin[self.i_te_up:, k] = xw[::-1]      # upper wake: TE -> exit
            yin[self.i_te_up:, k] = 0.0
            # ---- outer, the SAME parameter fractions (pure transfinite)
            # wake: straight down/up at the same x
            xou[0:self.nw + 1, k] = xw;                 you[0:self.nw + 1, k] = -R
            # lower S2: straight, same x, y = -R
            b = slice(self.nw, self.nw + self.n2 + 1)
            xou[b, k] = xs[::-1][:self.n2 + 1];         you[b, k] = -R
            # lower S1: from (x(0.10c), -R) along y=-R to (0,-R) then the quarter arc to (-R,0)
            xj = xl + 0.10 * c
            L_str, L_arc = xj, 0.5 * np.pi * R
            f = stretch(self.n1, BETA_S1)[::-1]          # 1 -> 0 with LE clustering
            sarc = (1.0 - f) * (L_str + L_arc)
            xa, ya = self._outer_lower(sarc, xj, R)
            xou[self.nw + self.n2:self.i_le + 1, k] = xa
            you[self.nw + self.n2:self.i_le + 1, k] = ya
            # upper mirrors
            xou[self.i_le:self.i_le + self.n1 + 1, k] = xa[::-1]
            you[self.i_le:self.i_le + self.n1 + 1, k] = -ya[::-1]
            e = slice(self.i_le + self.n1, self.i_te_up + 1)
            xou[e, k] = xs[self.n1:];                   you[e, k] = R
            xou[self.i_te_up:, k] = xw[::-1];           you[self.i_te_up:, k] = R

        self.xin, self.yin, self.xou, self.you = xin, yin, xou, you

        # --- radial distribution, exact geometric = the frozen exponential mapping
        fj = stretch(NN, BETA_N)[None, :, None]
        X = xin[:, None, :] + (xou - xin)[:, None, :] * fj
        Y = yin[:, None, :] + (you - yin)[:, None, :] * fj
        Z = np.broadcast_to(self.z[None, None, :], X.shape)
        self.delta0 = float(np.abs(
            np.hypot(X[:, 1, :] - X[:, 0, :], Y[:, 1, :] - Y[:, 0, :])).mean())

        # --- global point ids, with the WAKE CUT identified (i <-> NW-i at j=0)
        pid = -np.ones((NW + 1, NN + 1, NS + 1), dtype=np.int64)
        keep = np.ones((NW + 1, NN + 1, NS + 1), dtype=bool)
        keep[NW - self.nw:, 0, :] = False              # upper cut duplicates lower
        n_c = int(keep.sum())
        pid[keep] = np.arange(n_c)
        for i in range(self.nw + 1):
            pid[NW - i, 0, :] = pid[i, 0, :]
        pts = np.empty((n_c, 3))
        pts[:, 0] = X[keep]; pts[:, 1] = Y[keep]; pts[:, 2] = Z[keep]

        # --- fill points (outboard lens interior), a = 0..NA, b = 0..NB, k = NSW..NS
        NA, NB, NSW = self.NA, self.NB, self.NSW
        nk = NS - NSW + 1
        fpid = -np.ones((NA + 1, NB + 1, nk), dtype=np.int64)
        for a in range(NA + 1):
            fpid[a, 0, :] = pid[self.i_le - a, 0, NSW:]     # lower trace
            fpid[a, NB, :] = pid[self.i_le + a, 0, NSW:]    # upper trace
        fpid[0, :, :] = pid[self.i_le, 0, NSW:][None, :]    # LE line, collapsed
        fpid[NA, :, :] = pid[self.i_te_lo, 0, NSW:][None, :]  # TE line, collapsed
        nint = (NA - 1) * (NB - 1) * nk
        fpid[1:NA, 1:NB, :] = n_c + np.arange(nint).reshape(NA - 1, NB - 1, nk)
        fp = np.empty((nint, 3))
        c_t = self.g.chord(self.z_tip); x_t = self.g.xle(self.z_tip)
        xa = x_t + self.xc * c_t
        ya = self.g.t2(self.xc) * c_t
        # Interior of the lens: straight lower->upper lines at the SURFACE chordwise
        # stations, sampled at the same xi = a/NA and eta = b/NB at every level, so
        # the family is EXACTLY NESTED.  A camber-blended variant was TRIED and
        # MEASURED WORSE (severely non-orthogonal faces 36 -> 1956, max 84.64 ->
        # 84.99 deg) and was rejected for that measured reason.
        bb = (np.arange(1, NB) / NB)[None, :]
        xx = np.broadcast_to(xa[1:NA, None], (NA - 1, NB - 1))
        yy = (-ya[1:NA, None] + 2 * ya[1:NA, None] * bb)
        fp[:, 0] = np.repeat(xx.ravel(), nk)
        fp[:, 1] = np.repeat(yy.ravel(), nk)
        fp[:, 2] = np.tile(self.z[NSW:], (NA - 1) * (NB - 1))

        self.points = np.vstack([pts, fp])
        self.pid, self.fpid = pid, fpid
        self.n_points = len(self.points)

    @staticmethod
    def _outer_lower(s, xj, R):
        """point at arclength s along  (xj,-R) -> (0,-R) -> quarter arc -> (-R,0)"""
        x = np.empty_like(s); y = np.empty_like(s)
        st = s <= xj
        x[st] = xj - s[st]; y[st] = -R
        ar = ~st
        th = (s[ar] - xj) / R                      # 0 .. pi/2
        x[ar] = -R * np.sin(th); y[ar] = -R * np.cos(th)
        return x, y

    # -------------------------------------------------------------------- cells
    def cells(self):
        NW, NN, NS, NSW = self.NW, self.NN, self.NS, self.NSW
        p = self.pid
        i = np.arange(NW)[:, None, None]; j = np.arange(NN)[None, :, None]
        k = np.arange(NS)[None, None, :]
        def P(di, dj, dk):
            return p[i + di, j + dj, k + dk]
        hexC = np.stack([P(0, 0, 0), P(1, 0, 0), P(1, 1, 0), P(0, 1, 0),
                         P(0, 0, 1), P(1, 0, 1), P(1, 1, 1), P(0, 1, 1)], axis=-1)
        hexC = hexC.reshape(-1, 8)
        NA, NB = self.NA, self.NB
        f = self.fpid
        a = np.arange(NA)[:, None, None]; b = np.arange(NB)[None, :, None]
        kk = np.arange(NS - NSW)[None, None, :]
        def Q(da, db, dk):
            return f[a + da, b + db, kk + dk]
        hexF = np.stack([Q(0, 0, 0), Q(1, 0, 0), Q(1, 1, 0), Q(0, 1, 0),
                         Q(0, 0, 1), Q(1, 0, 1), Q(1, 1, 1), Q(0, 1, 1)], axis=-1)
        hexF = hexF.reshape(-1, 8)
        if self.nofill:
            hexF = hexF[:0]
        self.nC = len(hexC); self.nF = len(hexF)
        self._cells_cache = np.vstack([hexC, hexF])
        return self._cells_cache

    # -------------------------------------------------------------------- faces
    def build(self):
        NW, NN, NS, NSW = self.NW, self.NN, self.NS, self.NSW
        NA, NB = self.NA, self.NB
        NK = NS - NSW
        p, f = self.pid, self.fpid
        nC = NW * NN * NS
        cid = lambda i, j, k: (i * NN + j) * NS + k                       # noqa: E731
        fid = lambda a, b, k: nC + (a * NB + b) * NK + k                  # noqa: E731

        I = np.arange(NW); J = np.arange(NN); K = np.arange(NS)
        A = np.arange(NA); B = np.arange(NB); KK = np.arange(NK)
        F, OW, NE, TAG = [], [], [], []

        def add(pts, own, nei, tag):
            F.append(np.stack(pts, axis=-1).reshape(-1, 4))
            OW.append(np.asarray(own).ravel())
            NE.append(np.asarray(nei).ravel() if nei is not None
                      else np.full(np.asarray(own).size, -1, dtype=np.int64))
            TAG.append(tag)

        def g3(ii, jj, kk):
            return np.broadcast_arrays(ii[:, None, None], jj[None, :, None], kk[None, None, :])

        # ---- C-grid i faces (internal, i = 1..NW-1)
        i, j, k = g3(np.arange(1, NW), J, K)
        add((p[i, j, k], p[i, j + 1, k], p[i, j + 1, k + 1], p[i, j, k + 1]),
            cid(i - 1, j, k), cid(i, j, k), "int")
        # ---- C-grid j faces (internal, j = 1..NN-1)
        i, j, k = g3(I, np.arange(1, NN), K)
        add((p[i, j, k], p[i + 1, j, k], p[i + 1, j, k + 1], p[i, j, k + 1]),
            cid(i, j - 1, k), cid(i, j, k), "int")
        # ---- C-grid k faces (internal, k = 1..NS-1)
        i, j, k = g3(I, J, np.arange(1, NS))
        add((p[i, j, k], p[i + 1, j, k], p[i + 1, j + 1, k], p[i, j + 1, k]),
            cid(i, j, k - 1), cid(i, j, k), "int")
        # ---- wake cut, j = 0 : lower cell i  <->  upper cell NW-1-i
        i, j, k = g3(np.arange(self.nw), np.array([0]), K)
        add((p[i, j, k], p[i + 1, j, k], p[i + 1, j, k + 1], p[i, j, k + 1]),
            cid(i, 0, k), cid(NW - 1 - i, 0, k), "int")
        # ---- boundary
        j, k = np.meshgrid(J, K, indexing="ij")
        add((p[0, j, k], p[0, j + 1, k], p[0, j + 1, k + 1], p[0, j, k + 1]),
            cid(0, j, k), None, "outlet")
        add((p[NW, j, k], p[NW, j + 1, k], p[NW, j + 1, k + 1], p[NW, j, k + 1]),
            cid(NW - 1, j, k), None, "outlet")
        i, k = np.meshgrid(I, K, indexing="ij")
        add((p[i, NN, k], p[i + 1, NN, k], p[i + 1, NN, k + 1], p[i, NN, k + 1]),
            cid(i, NN - 1, k), None, "farfield")
        i, j = np.meshgrid(I, J, indexing="ij")
        add((p[i, j, 0], p[i + 1, j, 0], p[i + 1, j + 1, 0], p[i, j + 1, 0]),
            cid(i, j, 0), None, "symmetry")
        add((p[i, j, NS], p[i + 1, j, NS], p[i + 1, j + 1, NS], p[i, j + 1, NS]),
            cid(i, j, NS - 1), None, "spanOuter")
        if not self.nofill:
            a, b = np.meshgrid(A, B, indexing="ij")
            add((f[a, b, NK], f[a + 1, b, NK], f[a + 1, b + 1, NK], f[a, b + 1, NK]),
                fid(a, b, NK - 1), None, "spanOuter")
            add((f[a, b, 0], f[a + 1, b, 0], f[a + 1, b + 1, 0], f[a, b + 1, 0]),
                fid(a, b, 0), None, "wingTip")
        i, k = np.meshgrid(np.arange(self.nw, self.i_te_up), np.arange(NSW), indexing="ij")
        add((p[i, 0, k], p[i + 1, 0, k], p[i + 1, 0, k + 1], p[i, 0, k + 1]),
            cid(i, 0, k), None, "wing")

        if self.nofill:
            i, k = np.meshgrid(np.arange(self.nw, self.i_te_up),
                               np.arange(NSW, NS), indexing="ij")
            add((p[i, 0, k], p[i + 1, 0, k], p[i + 1, 0, k + 1], p[i, 0, k + 1]),
                cid(i, 0, k), None, "wing")
            faces = np.vstack(F).astype(np.int64)
            own = np.concatenate(OW).astype(np.int64)
            nei = np.concatenate(NE).astype(np.int64)
            tags = np.concatenate([np.full(len(a_), t) for a_, t in zip(F, TAG)])
            self._assemble(faces, own, nei, tags)
            return
        # ---- fill <-> C-grid, lower and upper traces
        a, b, kk = g3(A, np.array([0]), KK)
        add((f[a, 0, kk], f[a + 1, 0, kk], f[a + 1, 0, kk + 1], f[a, 0, kk + 1]),
            fid(a, 0, kk), cid(self.i_le - a - 1, 0, NSW + kk), "int")
        add((f[a, NB, kk], f[a + 1, NB, kk], f[a + 1, NB, kk + 1], f[a, NB, kk + 1]),
            fid(a, NB - 1, kk), cid(self.i_le + a, 0, NSW + kk), "int")
        # ---- fill internal a / b / k faces
        a, b, kk = g3(np.arange(1, NA), B, KK)
        add((f[a, b, kk], f[a, b + 1, kk], f[a, b + 1, kk + 1], f[a, b, kk + 1]),
            fid(a - 1, b, kk), fid(a, b, kk), "int")
        a, b, kk = g3(A, np.arange(1, NB), KK)
        add((f[a, b, kk], f[a + 1, b, kk], f[a + 1, b, kk + 1], f[a, b, kk + 1]),
            fid(a, b - 1, kk), fid(a, b, kk), "int")
        a, b, kk = g3(A, B, np.arange(1, NK))
        add((f[a, b, kk], f[a + 1, b, kk], f[a + 1, b + 1, kk], f[a, b + 1, kk]),
            fid(a, b, kk - 1), fid(a, b, kk), "int")

        faces = np.vstack(F).astype(np.int64)
        own = np.concatenate(OW).astype(np.int64)
        nei = np.concatenate(NE).astype(np.int64)
        tags = np.concatenate([np.full(len(a_), t) for a_, t in zip(F, TAG)])
        del F, OW, NE
        self._assemble(faces, own, nei, tags)

    # ----------------------------------------------------------------- assemble
    def _assemble(self, faces, own, nei, tags):
        pts = self.points
        ncell = self.nC + self.nF
        # cell centres (mean of the UNIQUE corner points is not needed: repeated
        # corners only bias a prism centre slightly and this is used ONLY to fix
        # face orientation, which is then re-verified)
        cells = self._cells_cache
        cc = np.add.reduceat(pts[cells.ravel()], np.arange(0, cells.size, 8), axis=0) / 8.0

        # triangles: drop the repeated corner
        tri = (faces[:, 0] == faces[:, 3]) | (faces[:, 1] == faces[:, 2])

        internal = nei >= 0
        # owner < neighbour
        sw = internal & (own > nei)
        own[sw], nei[sw] = nei[sw], own[sw]

        # orientation: normal owner -> neighbour (or outward on a boundary)
        P0, P1, P2, P3 = (pts[faces[:, q]] for q in range(4))
        nrm = np.cross(P2 - P0, P3 - P1)
        ctr = 0.25 * (P0 + P1 + P2 + P3)
        tgt = np.where(internal[:, None], cc[np.where(internal, nei, own)] - cc[own],
                       ctr - cc[own])
        flip = np.einsum("ij,ij->i", nrm, tgt) < 0
        faces[flip] = faces[flip][:, ::-1]
        # re-verify after flipping -- a zero dot is a degenerate face and is fatal
        P0, P1, P2, P3 = (pts[faces[:, q]] for q in range(4))
        nrm = np.cross(P2 - P0, P3 - P1)
        dot = np.einsum("ij,ij->i", nrm, tgt)
        assert (dot > 0).all(), f"ABORT: {int((dot <= 0).sum())} faces cannot be oriented"
        area = 0.5 * np.linalg.norm(nrm, axis=1)
        assert area.min() > 0, "ABORT: zero-area face"
        self.min_face_area = float(area.min())

        order = np.lexsort((nei[internal], own[internal]))
        ii = np.nonzero(internal)[0][order]
        self.n_internal = len(ii)
        bnd_names = ["wing", "wingTip", "symmetry", "farfield", "spanOuter", "outlet"]
        bi, self.patches = [], []
        start = self.n_internal
        for nm in bnd_names:
            sel = np.nonzero((~internal) & (tags == nm))[0]
            sel = sel[np.argsort(own[sel], kind="stable")]
            self.patches.append((nm, start, len(sel)))
            start += len(sel)
            bi.append(sel)
        allidx = np.concatenate([ii] + bi)
        self.faces = faces[allidx]
        self.tri = tri[allidx]
        self.owner = own[allidx]
        self.neighbour = nei[ii]
        cnt = np.bincount(self.owner, minlength=ncell) + \
            np.bincount(self.neighbour, minlength=ncell)
        assert cnt.min() >= 5 and cnt.max() <= 6, f"ABORT: faces/cell {cnt.min()}..{cnt.max()}"
        self.n_prism = int((cnt == 5).sum())

    # -------------------------------------------------------------------- write
    def write(self, case):
        d = os.path.join(case, "constant", "polyMesh")
        os.makedirs(d, exist_ok=True)

        def head(cls, obj):
            return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
                    f"    class       {cls};\n    location    \"constant/polyMesh\";\n"
                    f"    object      {obj};\n}}\n\n")

        with open(os.path.join(d, "points"), "w") as fh:
            fh.write(head("vectorField", "points"))
            fh.write(f"{len(self.points)}\n(\n")
            P = self.points
            CH = 500000
            for s0 in range(0, len(P), CH):
                blk = P[s0:s0 + CH].tolist()
                fh.write("\n".join("(%.17g %.17g %.17g)" % tuple(q) for q in blk) + "\n")
            fh.write(")\n")

        with open(os.path.join(d, "faces"), "w") as fh:
            fh.write(head("faceList", "faces"))
            fh.write(f"{len(self.faces)}\n(\n")
            F, T = self.faces, self.tri
            CH = 500000
            for s in range(0, len(F), CH):
                e = min(s + CH, len(F))
                buf = []
                for q, t in zip(F[s:e], T[s:e]):
                    if t:
                        u = [q[0]] + [q[n] for n in (1, 2, 3) if q[n] != q[n - 1]]
                        if u[-1] == u[0]:
                            u = u[:-1]
                        assert len(u) == 3, f"ABORT: collapsed face {q} -> {u}"
                        buf.append(f"3({u[0]} {u[1]} {u[2]})")
                    else:
                        buf.append(f"4({q[0]} {q[1]} {q[2]} {q[3]})")
                fh.write("\n".join(buf) + "\n")
            fh.write(")\n")

        for nm, arr in (("owner", self.owner), ("neighbour", self.neighbour)):
            with open(os.path.join(d, nm), "w") as fh:
                fh.write(head("labelList", nm))
                fh.write(f"{len(arr)}\n(\n")
                CH = 1000000
                for s in range(0, len(arr), CH):
                    fh.write("\n".join(map(str, arr[s:s + CH].tolist())) + "\n")
                fh.write(")\n")

        types = {"wing": "wall", "wingTip": "wall", "symmetry": "symmetryPlane"}
        with open(os.path.join(d, "boundary"), "w") as fh:
            fh.write(head("polyBoundaryMesh", "boundary"))
            fh.write(f"{len(self.patches)}\n(\n")
            for nm, st, n in self.patches:
                t = types.get(nm, "patch")
                fh.write(f"    {nm}\n    {{\n        type            {t};\n")
                if t == "wall":
                    fh.write("        inGroups        1(wall);\n")
                fh.write(f"        nFaces          {n};\n        startFace       {st};\n    }}\n")
            fh.write(")\n")


def build_level(m, outdir, verbose=True):
    t0 = time.time()
    g = M6Geometry(verbose=verbose)
    g.z_tip = g.z_tip_measured
    mm = Mesh(m, g, verbose)
    mm.cells()
    mm.build()
    mm.write(outdir)
    dt = time.time() - t0
    info = dict(m=m, cells=mm.nC + mm.nF, cells_C=mm.nC, cells_fill=mm.nF,
                points=mm.n_points, faces=len(mm.faces), internal=mm.n_internal,
                prisms=mm.n_prism, delta0_um=mm.delta0 * 1e6, z_tip=mm.z_tip,
                z_out=mm.z_out, min_face_area=mm.min_face_area,
                E_normal=grading_E(mm.NN, BETA_N), E_s1=grading_E(mm.n1, BETA_S1),
                wall_s=dt)
    if verbose:
        print(f"  m={m}: {info['cells']:,} cells ({mm.nC:,} C + {mm.nF:,} fill), "
              f"{info['points']:,} points, {info['faces']:,} faces "
              f"({mm.n_prism:,} prisms), delta0 {info['delta0_um']:.2f} um, "
              f"E_normal {info['E_normal']:.1f}, {dt:.1f} s")
    return info, mm


if __name__ == "__main__":
    build_level(int(sys.argv[1]), sys.argv[2])
