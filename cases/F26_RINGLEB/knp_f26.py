#!/usr/bin/env python3
"""
F26 -- THE DISCRETISATION MODEL: a numpy re-implementation of rhoCentralFoam's
inviscid step (OpenFOAM v2606, `fluxScheme Kurganov`, `ddt Euler`,
`reconstruct(rho) vanLeer`, `reconstruct(U) vanLeerV`, `reconstruct(T) vanLeer`,
`Gauss linear` gradients) on a GENERAL 2-D owner/neighbour finite-volume mesh
of unit depth, run on the flow-net lattice exact_f26.lattice() builds -- the
same node coordinates build_f26.py writes into constant/polyMesh/points -- so
the model integrates the scheme on the face geometry the solver sees.

What is reproduced face by face (rhoCentralFoam.C, v2606):
  pos/neg limited interpolation: weights = psi*CDweights + (1 - psi)*pos0(dir),
  psi = vanLeer(r) with r = 2 (d . gradc_upwind)/(phi_N - phi_P) - 1 (NVDTVD;
  1000x clamp) for scalars and the NVDVTVDV projection for vectors; boundary
  faces take the patch value on both sides; Kurganov weights a_pos, aSf;
  phi, phiUp, phiEp exactly as formed there; explicit Euler `diagonal` updates
  of rho, rhoU, rhoE; boundary fields refreshed in the solver's order.
Cell gradients: Gauss linear with OpenFOAM's linear weights
  w = |Sf.(C_N - C_f)| / (|Sf.(C_f - C_P)| + |Sf.(C_N - C_f)|).
Geometry: face centres = edge midpoints, cell centres = exact quad centroids,
volumes = quad areas (what OpenFOAM's pyramid decomposition returns for a
right prism over a planar quad).

Boundary conditions per patch (registered in exact/build): `fixed` = exact
value at the face centre (hodograph inversion), `zeroGradient`, `slip` (U:
tangential projection; scalars: zeroGradient).  rho on the boundary is
psi_b p_b as in the solver.

Refusals are `raise`.  Zero `assert` (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: knp_f26.py must not run under `python3 -O`.\n")
    sys.exit(2)

import math

import numpy as np

import exact_f26 as EX

PATCHES = ("inflow", "outflow", "wallOuter", "wallInner")


class ModelError(Exception):
    pass


# ---------------------------------------------------------------------------
# GEOMETRY from node arrays X[j, i], Y[j, i]
# ---------------------------------------------------------------------------
def geometry(X, Y):
    nc1, na1 = X.shape
    Nc, Na = nc1 - 1, na1 - 1
    ncell = Na * Nc

    def cid(j, i):
        return j * Na + i
    # cell centroids and areas (polygon formula, counter-clockwise quad a b c d)
    ax, ay = X[:-1, :-1], Y[:-1, :-1]
    bx, by = X[:-1, 1:], Y[:-1, 1:]
    cx, cy = X[1:, 1:], Y[1:, 1:]
    dx_, dy_ = X[1:, :-1], Y[1:, :-1]
    px = np.stack([ax, bx, cx, dx_], -1)
    py = np.stack([ay, by, cy, dy_], -1)
    qx, qy = np.roll(px, -1, -1), np.roll(py, -1, -1)
    cross = px * qy - qx * py
    area = 0.5 * np.sum(cross, -1)
    sgn = np.sign(area)
    Cx = np.sum((px + qx) * cross, -1) / (6.0 * area)
    Cy = np.sum((py + qy) * cross, -1) / (6.0 * area)
    if np.any(area * sgn[0, 0] <= 0):
        raise ModelError("non-positive or inconsistent cell areas in the lattice")
    C = np.column_stack([Cx.ravel(), Cy.ravel()])
    Vol = np.abs(area).ravel()

    faces = []            # (own, nei_or_-1, ax, ay, bx, by, patch)
    # internal along-faces between (j,i) and (j,i+1): the edge at node column i+1
    for j in range(Nc):
        for i in range(Na - 1):
            faces.append((cid(j, i), cid(j, i + 1), X[j, i + 1], Y[j, i + 1], X[j + 1, i + 1], Y[j + 1, i + 1], None))
    # internal across-faces between (j,i) and (j+1,i): the edge at node row j+1
    for j in range(Nc - 1):
        for i in range(Na):
            faces.append((cid(j, i), cid(j + 1, i), X[j + 1, i], Y[j + 1, i], X[j + 1, i + 1], Y[j + 1, i + 1], None))
    n_int = len(faces)
    for j in range(Nc):                                           # inflow i = 0
        faces.append((cid(j, 0), -1, X[j, 0], Y[j, 0], X[j + 1, 0], Y[j + 1, 0], "inflow"))
    for j in range(Nc):                                           # outflow i = Na
        faces.append((cid(j, Na - 1), -1, X[j, Na], Y[j, Na], X[j + 1, Na], Y[j + 1, Na], "outflow"))
    for i in range(Na):                                           # inner wall j = 0 (psi = 1/K_MAX)
        faces.append((cid(0, i), -1, X[0, i], Y[0, i], X[0, i + 1], Y[0, i + 1], "wallInner"))
    for i in range(Na):                                           # outer wall j = Nc (psi = 1/K_MIN)
        faces.append((cid(Nc - 1, i), -1, X[Nc, i], Y[Nc, i], X[Nc, i + 1], Y[Nc, i + 1], "wallOuter"))
    own = np.array([f[0] for f in faces])
    nei = np.array([f[1] for f in faces])
    a = np.array([[f[2], f[3]] for f in faces])
    b = np.array([[f[4], f[5]] for f in faces])
    Cf = 0.5 * (a + b)
    e = b - a
    Sf = np.column_stack([e[:, 1], -e[:, 0]])                     # one of the two normals, |Sf| = edge length x depth 1
    target = np.where(nei[:, None] >= 0, C[np.maximum(nei, 0)] - C[own], Cf - C[own])
    flip = np.sum(Sf * target, 1) < 0
    Sf[flip] *= -1.0
    magSf = np.hypot(Sf[:, 0], Sf[:, 1])
    nf = Sf / magSf[:, None]
    patch = np.array([f[6] if f[6] else "" for f in faces])
    # linear (CD) weights on internal faces
    o, n = own[:n_int], nei[:n_int]
    SfdOwn = np.abs(np.sum(Sf[:n_int] * (Cf[:n_int] - C[o]), 1))
    SfdNei = np.abs(np.sum(Sf[:n_int] * (C[n] - Cf[:n_int]), 1))
    w_cd = SfdNei / (SfdOwn + SfdNei)
    d = C[n] - C[o]
    bidx = dict((p, np.where(patch == p)[0]) for p in PATCHES)
    # non-orthogonality (deg) on internal faces, skewness proxy: for MESH_LINE-type diagnostics
    cosang = np.sum(nf[:n_int] * d, 1) / np.hypot(d[:, 0], d[:, 1])
    nonortho = np.degrees(np.arccos(np.clip(cosang, -1, 1)))
    return dict(Na=Na, Nc=Nc, ncell=ncell, C=C, V=Vol, own=own, nei=nei, n_int=n_int, Sf=Sf, magSf=magSf, nf=nf,
                Cf=Cf, w_cd=w_cd, d=d, patch=patch, bidx=bidx, nonortho_max=float(np.max(nonortho)))


# ---------------------------------------------------------------------------
# THE SCHEME
# ---------------------------------------------------------------------------
def _van_leer(r):
    return (r + np.abs(r)) / (1.0 + np.abs(r))


def _r_scalar(gradcf, gradf):
    sg = np.where(gradcf >= 0, 1.0, -1.0) * np.where(gradf >= 0, 1.0, -1.0)
    clamp = np.abs(gradcf) >= 1000.0 * np.abs(gradf)
    safe = np.where(clamp, 1.0, gradf)
    return np.where(clamp, 2.0 * 1000.0 * sg - 1.0, 2.0 * gradcf / safe - 1.0)


class Model:
    def __init__(self, X, Y, bc):
        """bc: dict patch -> dict(U=..., T=..., p=...) with values in ('fixed', 'zeroGradient', 'slip')."""
        self.g = geometry(X, Y)
        g = self.g
        self.bc = bc
        # exact state at boundary face centres (for 'fixed')
        ex = EX.fields_at(g["Cf"][:, 0], g["Cf"][:, 1])
        self.exact_b = dict(rho=ex["rho"], u=ex["u"], v=ex["v"], p=ex["p"], T=ex["T"],
                            dpdn=EX.dp_dn(g["Cf"][:, 0], g["Cf"][:, 1], g["nf"][:, 0], g["nf"][:, 1]))
        # OpenFOAM's boundary deltaCoeffs: 1/|nf . (Cf - C_P)| (patch-normal delta, fvPatch::delta())
        ob = g["own"][g["n_int"]:]
        self.bdelta = np.abs(np.sum(g["nf"][g["n_int"]:] * (g["Cf"][g["n_int"]:] - g["C"][ob]), 1))
        exc = EX.fields_at(g["C"][:, 0], g["C"][:, 1])
        self.exact_c = dict(rho=exc["rho"], u=exc["u"], v=exc["v"], p=exc["p"], T=exc["T"], M=exc["M"])
        self.ex_max_wave = None

    def set_initial(self, exact=True, uniform_V=None):
        e = self.exact_c
        if exact:
            rho, u, v, T = e["rho"], e["u"], e["v"], e["T"]
        else:
            V = uniform_V
            rho = np.full_like(e["rho"], float(EX.rho_of(V)))
            T = np.full_like(e["rho"], float(EX.T_of(V)))
            # uniform speed along the local exact flow direction
            u, v = V * e["u"] / np.hypot(e["u"], e["v"]), V * e["v"] / np.hypot(e["u"], e["v"])
        self.rho = rho.copy()
        self.rhoU = np.column_stack([rho * u, rho * v])
        self.rhoE = rho * (EX.CV * T + 0.5 * (u * u + v * v))
        self._boundary_state()

    # ---- boundary fields, in the solver's order (values as they stand at the end of a step)
    def _boundary_state(self):
        g = self.g
        n_int = g["n_int"]
        nb = len(g["own"]) - n_int
        ob = g["own"][n_int:]
        U = self.rhoU / self.rho[:, None]
        e = self.rhoE / self.rho - 0.5 * np.sum(U * U, 1)
        T = e / EX.CV
        p = self.rho * EX.R_GAS * T
        Ub = U[ob].copy()
        Tb = T[ob].copy()
        pb = p[ob].copy()
        for pn in PATCHES:
            loc = g["bidx"][pn] - n_int
            glo = g["bidx"][pn]
            spec = self.bc[pn]
            if spec["U"] == "fixed":
                Ub[loc, 0] = self.exact_b["u"][glo]
                Ub[loc, 1] = self.exact_b["v"][glo]
            elif spec["U"] == "slip":
                nf = g["nf"][glo]
                un = np.sum(Ub[loc] * nf, 1)
                Ub[loc] -= un[:, None] * nf
            elif spec["U"] != "zeroGradient":
                raise ModelError("unknown U bc %r" % spec["U"])
            if spec["T"] == "fixed":
                Tb[loc] = self.exact_b["T"][glo]
            elif spec["T"] not in ("zeroGradient", "slip"):
                raise ModelError("unknown T bc")
            if spec["p"] == "fixed":
                pb[loc] = self.exact_b["p"][glo]
            elif spec["p"] == "fixedGradient":
                pb[loc] = pb[loc] + self.exact_b["dpdn"][glo] * self.bdelta[loc]
            elif spec["p"] not in ("zeroGradient", "slip"):
                raise ModelError("unknown p bc")
        self.Ub, self.Tb, self.pb = Ub, Tb, pb
        self.rhob = pb / (EX.R_GAS * Tb)

    def _gauss_grad(self, phic, phib):
        """Gauss linear cell gradient of a scalar (phic cells, phib boundary faces)."""
        g = self.g
        n_int = g["n_int"]
        o, n = g["own"][:n_int], g["nei"][:n_int]
        f_int = g["w_cd"] * phic[o] + (1.0 - g["w_cd"]) * phic[n]
        Sx, Sy = g["Sf"][:, 0], g["Sf"][:, 1]
        gx = np.bincount(o, Sx[:n_int] * f_int, g["ncell"]) - np.bincount(n, Sx[:n_int] * f_int, g["ncell"])
        gy = np.bincount(o, Sy[:n_int] * f_int, g["ncell"]) - np.bincount(n, Sy[:n_int] * f_int, g["ncell"])
        ob = g["own"][n_int:]
        gx += np.bincount(ob, Sx[n_int:] * phib, g["ncell"])
        gy += np.bincount(ob, Sy[n_int:] * phib, g["ncell"])
        return gx / g["V"], gy / g["V"]

    def _recon_scalar(self, phic, phib, gx, gy):
        g = self.g
        n_int = g["n_int"]
        o, n = g["own"][:n_int], g["nei"][:n_int]
        d = g["d"]
        gradf = phic[n] - phic[o]
        gcP = d[:, 0] * gx[o] + d[:, 1] * gy[o]
        gcN = d[:, 0] * gx[n] + d[:, 1] * gy[n]
        psi_p = _van_leer(_r_scalar(gcP, gradf))
        psi_n = _van_leer(_r_scalar(gcN, gradf))
        w_p = psi_p * g["w_cd"] + (1.0 - psi_p)          # pos0(+1) = 1
        w_n = psi_n * g["w_cd"]                          # pos0(-1) = 0
        f_pos = np.concatenate([w_p * phic[o] + (1.0 - w_p) * phic[n], phib])
        f_neg = np.concatenate([w_n * phic[o] + (1.0 - w_n) * phic[n], phib])
        return f_pos, f_neg

    def _recon_vector(self, qc, qb):
        """vanLeerV: one limiter for both components (NVDVTVDV), gradient tensor Gauss linear."""
        g = self.g
        n_int = g["n_int"]
        o, n = g["own"][:n_int], g["nei"][:n_int]
        d = g["d"]
        gxx, gyx = self._gauss_grad(qc[:, 0], qb[:, 0])       # d/dx u, d/dy u
        gxy, gyy = self._gauss_grad(qc[:, 1], qb[:, 1])       # d/dx v, d/dy v
        gfx, gfy = qc[n, 0] - qc[o, 0], qc[n, 1] - qc[o, 1]
        gradf = gfx * gfx + gfy * gfy
        # (d & gradcP) = directional derivative vector
        dP = (d[:, 0] * gxx[o] + d[:, 1] * gyx[o], d[:, 0] * gxy[o] + d[:, 1] * gyy[o])
        dN = (d[:, 0] * gxx[n] + d[:, 1] * gyx[n], d[:, 0] * gxy[n] + d[:, 1] * gyy[n])
        gcP = gfx * dP[0] + gfy * dP[1]
        gcN = gfx * dN[0] + gfy * dN[1]
        psi_p = _van_leer(_r_scalar(gcP, gradf))
        psi_n = _van_leer(_r_scalar(gcN, gradf))
        w_p = psi_p * g["w_cd"] + (1.0 - psi_p)
        w_n = psi_n * g["w_cd"]
        pos = np.vstack([w_p[:, None] * qc[o] + (1.0 - w_p)[:, None] * qc[n], qb])
        neg = np.vstack([w_n[:, None] * qc[o] + (1.0 - w_n)[:, None] * qc[n], qb])
        return pos, neg

    def step(self, dt):
        g = self.g
        n_int = g["n_int"]
        rho, rhoU, rhoE = self.rho, self.rhoU, self.rhoE
        U = rhoU / rho[:, None]
        e = rhoE / rho - 0.5 * np.sum(U * U, 1)
        T = e / EX.CV
        rPsi = EX.R_GAS * T
        c = np.sqrt(GAMMA_ * rPsi)
        # boundary fields as they stand
        rhob, Ub, Tb = self.rhob, self.Ub, self.Tb
        rPsib = EX.R_GAS * Tb
        eb = EX.CV * Tb
        cb = np.sqrt(GAMMA_ * rPsib)
        rhoUb = rhob[:, None] * Ub
        # gradients (Gauss linear) for the limiters
        grho = self._gauss_grad(rho, rhob)
        grPsi = self._gauss_grad(rPsi, rPsib)
        ge = self._gauss_grad(e, eb)
        gc = self._gauss_grad(c, cb)
        rho_pos, rho_neg = self._recon_scalar(rho, rhob, *grho)
        rhoU_pos, rhoU_neg = self._recon_vector(rhoU, rhoUb)
        rPsi_pos, rPsi_neg = self._recon_scalar(rPsi, rPsib, *grPsi)
        e_pos, e_neg = self._recon_scalar(e, eb, *ge)
        c_pos, c_neg = self._recon_scalar(c, cb, *gc)
        U_pos = rhoU_pos / rho_pos[:, None]
        U_neg = rhoU_neg / rho_neg[:, None]
        p_pos = rho_pos * rPsi_pos
        p_neg = rho_neg * rPsi_neg
        Sf, magSf = g["Sf"], g["magSf"]
        phiv_pos = np.sum(U_pos * Sf, 1)
        phiv_neg = np.sum(U_neg * Sf, 1)
        cSf_pos = c_pos * magSf
        cSf_neg = c_neg * magSf
        ap = np.maximum(np.maximum(phiv_pos + cSf_pos, phiv_neg + cSf_neg), 0.0)
        am = np.minimum(np.minimum(phiv_pos - cSf_pos, phiv_neg - cSf_neg), 0.0)
        a_pos = ap / (ap - am)
        aSf = am * a_pos
        a_neg = 1.0 - a_pos
        phiv_pos = phiv_pos * a_pos
        phiv_neg = phiv_neg * a_neg
        aphiv_pos = phiv_pos - aSf
        aphiv_neg = phiv_neg + aSf
        amaxSf = np.maximum(np.abs(aphiv_pos), np.abs(aphiv_neg))
        phi = aphiv_pos * rho_pos + aphiv_neg * rho_neg
        pf = a_pos * p_pos + a_neg * p_neg
        phiUp = aphiv_pos[:, None] * rhoU_pos + aphiv_neg[:, None] * rhoU_neg + pf[:, None] * Sf
        phiEp = (aphiv_pos * (rho_pos * (e_pos + 0.5 * np.sum(U_pos * U_pos, 1)) + p_pos)
                 + aphiv_neg * (rho_neg * (e_neg + 0.5 * np.sum(U_neg * U_neg, 1)) + p_neg)
                 + aSf * p_pos - aSf * p_neg)
        o, n = g["own"][:n_int], g["nei"][:n_int]
        ob = g["own"][n_int:]
        nc = g["ncell"]

        def div(F):
            return (np.bincount(o, F[:n_int], nc) - np.bincount(n, F[:n_int], nc) + np.bincount(ob, F[n_int:], nc))
        sumAmax = (np.bincount(o, amaxSf[:n_int], nc) + np.bincount(n, amaxSf[:n_int], nc) + np.bincount(ob, amaxSf[n_int:], nc))
        co = 0.5 * float(np.max(sumAmax / g["V"])) * dt
        self.rho = rho - dt / g["V"] * div(phi)
        self.rhoU = rhoU - dt / g["V"][:, None] * np.column_stack([div(phiUp[:, 0]), div(phiUp[:, 1])])
        self.rhoE = rhoE - dt / g["V"] * div(phiEp)
        self._boundary_state()
        return co

    # ---- diagnostics
    def state(self):
        U = self.rhoU / self.rho[:, None]
        e = self.rhoE / self.rho - 0.5 * np.sum(U * U, 1)
        T = e / EX.CV
        p = self.rho * EX.R_GAS * T
        return dict(rho=self.rho, u=U[:, 0], v=U[:, 1], p=p, T=T)

    def errors(self):
        s = self.state()
        ex = self.exact_c
        V = self.g["V"]
        e2 = math.sqrt(np.sum(V * (s["rho"] - ex["rho"]) ** 2) / np.sum(V))
        ent = EX.entropy_of(s["p"], s["rho"])
        s2 = math.sqrt(np.sum(V * ent ** 2) / np.sum(V))
        return dict(E2_rho=e2, S2_entropy=s2, max_abs_entropy=float(np.max(np.abs(ent))),
                    M_max=float(np.max(np.hypot(s["u"], s["v"]) / np.sqrt(GAMMA_ * EX.R_GAS * s["T"]))))

    def dt_for_co(self, co_target):
        return dt_for_co_geometry(self.g, co_target)


def dt_for_co_geometry(g, co_target):
    """fixed dt giving solver-convention max Courant `co_target` on the EXACT field
    on this mesh: with equal states on both sides of a face the Kurganov weights
    give aphiv_pos = (phiv + cSf)/2 and aphiv_neg = (phiv - cSf)/2, so
    amaxSf = (|phiv| + cSf)/2 and CoNum = 0.5 max(sum_f amaxSf / V) dt."""
    n_int = g["n_int"]
    ex = EX.fields_at(g["Cf"][:, 0], g["Cf"][:, 1])
    un = np.abs(ex["u"] * g["Sf"][:, 0] + ex["v"] * g["Sf"][:, 1])
    cS = np.sqrt(GAMMA_ * EX.R_GAS * ex["T"]) * g["magSf"]
    amax = 0.5 * (un + cS)
    o, n, ob = g["own"][:n_int], g["nei"][:n_int], g["own"][n_int:]
    nc = g["ncell"]
    sumAmax = np.bincount(o, amax[:n_int], nc) + np.bincount(n, amax[:n_int], nc) + np.bincount(ob, amax[n_int:], nc)
    return co_target / (0.5 * float(np.max(sumAmax / g["V"])))


GAMMA_ = EX.GAMMA
