#!/usr/bin/env python3
"""paper_parity_planes.py -- the field-plane and mesh figures of Reid et al. (2025)
reproduced for OUR case: their Figs. 2, 7, 8, 9, 10, 11, 13, 14, 15, 17, 18, 19.

Companion to paper_parity_figures.py, which covers Figs. 1, 3, 4, 5, 12, 16 and
Tables 1-2. Between them the two scripts fill every row of the checklist in
PARITY_INDEX.md that our fields can fill; the rest are listed there with a reason.

No solver runs. Fields come from R2/ET8000/<level>/8000; cell centres, cell
volumes and grad(U) come from the read-only work copy built by
paper_parity_setup.sh, so nothing is written into the graded run tree.

Plane sampling is NEAREST-CELL on a regular grid, with any sample whose nearest
cell centre is further than 1.5 local cell sizes masked out -- that is what draws
the solid bodies and the tank wall, and it is why the boundaries look pixelated at
the sampling resolution rather than smooth.
"""
import json, math, os, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from scipy.spatial import cKDTree

R    = "/home/ubuntu/Certonomous"
SRC  = f"{R}/verification/runs/navier_class/MRF/R2/ET8000"
WRK  = f"{R}/verification/runs/navier_class/MRF/R2/PAPER_PARITY/work"
F    = f"{R}/verification/runs/navier_class/MRF/R2/PAPER_PARITY/figures"
T    = "8000"
os.makedirs(F, exist_ok=True)

D, TANK, ZC, W = 0.100, 0.300, 0.100, 0.020
UTIP  = math.pi * 5.0 * D
RZONE, ZLO, ZHI = 0.060, 0.080, 0.120          # our MRF zone, from topoSetDict
LV    = ["coarse", "medium", "fine"]
COL   = {"coarse": "#c0392b", "medium": "#1f4e9c", "fine": "#1f7a34"}

plt.rcParams.update({"font.size": 9, "figure.dpi": 150, "savefig.bbox": "tight",
                     "legend.framealpha": .9, "legend.fontsize": 7.5})

def title(ax, t):
    assert len(t.split()) <= 10, f"title too long ({len(t.split())}): {t}"
    ax.set_title(t, fontsize=9.5)

def cap(fig, t):
    assert len(t.split()) <= 20, f"caption too long ({len(t.split())}): {t}"
    fig.text(.5, -.02, t, ha="center", va="top", fontsize=8, style="italic")

# ----------------------------------------------------------------- field readers
def _body(path):
    s = open(path).read()
    return s[s.index("internalField"):]

def rd_scalar(path):
    b = _body(path); a = b.index("("); e = b.index(")", a)
    return np.fromstring(b[a + 1:e], sep=" ")

def rd_vector(path):
    b = _body(path); a = b.index("(")
    e = b.rindex(")", 0, b.index("boundaryField"))
    n = int(b[:a].strip().split("\n")[-1].strip())
    return np.fromstring(b[a + 1:e].replace("(", " ").replace(")", " "),
                         sep=" ").reshape(n, 3)

def rd_tensor(path):
    b = _body(path); a = b.index("(")
    e = b.rindex(")", 0, b.index("boundaryField"))
    n = int(b[:a].strip().split("\n")[-1].strip())
    return np.fromstring(b[a + 1:e].replace("(", " ").replace(")", " "),
                         sep=" ").reshape(n, 3, 3)

class Level:
    def __init__(self, name):
        t, w = f"{SRC}/{name}/{T}", f"{WRK}/{name}/{T}"
        self.name = name
        self.U    = rd_vector(f"{t}/U")
        self.k    = rd_scalar(f"{t}/k")
        self.nut  = rd_scalar(f"{t}/nut")
        self.V    = rd_scalar(f"{w}/V")
        self.C    = rd_vector(f"{w}/C")
        self.h    = np.cbrt(self.V)
        self.tree = cKDTree(self.C)
        gU        = rd_tensor(f"{w}/grad(U)")
        S         = 0.5 * (gU + np.transpose(gU, (0, 2, 1)))
        self.G    = 2.0 * self.nut * np.einsum("nij,nij->n", S, S)
        self.magU = np.linalg.norm(self.U, axis=1)
        self.I    = np.sqrt(2.0 * np.maximum(self.k, 0) / 3.0) / np.maximum(self.magU, 1e-12)

    def plane(self, field, kind, n=420):
        """kind 'vertical' -> x-z at y=0 ; 'horizontal' -> x-y at z=field's z."""
        if kind == "vertical":
            xs = np.linspace(-TANK / 2, TANK / 2, n)
            zs = np.linspace(0.0, TANK, n)
            X, Z = np.meshgrid(xs, zs)
            P = np.column_stack([X.ravel(), np.zeros(X.size), Z.ravel()])
            ext = [-TANK / 2, TANK / 2, 0, TANK]
        else:
            xs = ys = np.linspace(-TANK / 2, TANK / 2, n)
            X, Y = np.meshgrid(xs, ys)
            P = np.column_stack([X.ravel(), Y.ravel(),
                                 np.full(X.size, kind)])
            ext = [-TANK / 2, TANK / 2, -TANK / 2, TANK / 2]
        d, idx = self.tree.query(P)
        vals = np.asarray(field)[idx].astype(float)
        vals[d > 1.5 * self.h[idx]] = np.nan
        return vals.reshape(n, n), ext

FINE = None
def fine():
    global FINE
    if FINE is None:
        FINE = Level("fine")
    return FINE

def _zone_vertical(ax):
    ax.add_patch(Rectangle((-RZONE, ZLO), 2 * RZONE, ZHI - ZLO,
                           fc="none", ec="w", lw=1.4, ls="--"))
def _zone_horizontal(ax):
    ax.add_patch(Circle((0, 0), RZONE, fc="none", ec="w", lw=1.4, ls="--"))

def _imshow(ax, M, ext, cmap, vmin, vmax, label):
    im = ax.imshow(M, origin="lower", extent=ext, cmap=cmap, vmin=vmin, vmax=vmax,
                   interpolation="nearest", aspect="equal")
    cb = plt.colorbar(im, ax=ax, fraction=.046, pad=.03)
    cb.set_label(label, fontsize=8); cb.ax.tick_params(labelsize=7)
    return im

# ------------------------------------------------------------------ their Fig. 2
def fig02_mesh():
    L = fine()
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.4))
    m = np.abs(L.C[:, 1]) < 0.5 * L.h                       # a one-cell slab at y = 0
    axs[0].scatter(L.C[m, 0], L.C[m, 2], s=(L.h[m] * 2400) ** 2 * 1e-3,
                   c=L.h[m] * 1000, cmap="viridis_r", marker="s", linewidths=0)
    axs[0].set_xlim(-TANK / 2, TANK / 2); axs[0].set_ylim(0, TANK)
    axs[0].set_xlabel("x (m)"); axs[0].set_ylabel("z (m)")
    title(axs[0], "Cell centres, vertical slab, fine level")
    m = np.abs(L.C[:, 2] - ZC) < 0.5 * L.h
    sc = axs[1].scatter(L.C[m, 0], L.C[m, 1], s=(L.h[m] * 2400) ** 2 * 1e-3,
                        c=L.h[m] * 1000, cmap="viridis_r", marker="s", linewidths=0)
    axs[1].set_xlim(-TANK / 2, TANK / 2); axs[1].set_ylim(-TANK / 2, TANK / 2)
    axs[1].set_xlabel("x (m)"); axs[1].set_ylabel("y (m)")
    title(axs[1], "Cell centres, impeller plane, fine level")
    for a in axs: a.set_aspect("equal")
    cb = plt.colorbar(sc, ax=axs, fraction=.03, pad=.02); cb.set_label("cell size (mm)", fontsize=8)
    cap(fig, "Gaps are the solid bodies; colour is local cell size, not a solution.")
    fig.savefig(f"{F}/fig02b_mesh_slabs.png"); plt.close(fig)

# ------------------------------------------------------------------ their Fig. 7
def fig07_nut():
    L = fine()
    fig, axs = plt.subplots(1, 2, figsize=(10.0, 4.2))
    M, e = L.plane(L.nut, "vertical")
    _imshow(axs[0], M * 1e4, e, "magma", 0, 6, "nut (1e-4 m2/s)")
    _zone_vertical(axs[0]); axs[0].set_xlabel("x (m)"); axs[0].set_ylabel("z (m)")
    title(axs[0], "Turbulent viscosity, vertical plane")
    M, e = L.plane(L.nut, ZC)
    _imshow(axs[1], M * 1e4, e, "magma", 0, 6, "nut (1e-4 m2/s)")
    _zone_horizontal(axs[1]); axs[1].set_xlabel("x (m)"); axs[1].set_ylabel("y (m)")
    title(axs[1], "Turbulent viscosity, impeller plane")
    cap(fig, "k-omega SST only; the paper also shows k-epsilon, which we did not solve.")
    fig.savefig(f"{F}/fig07_nut_planes.png"); plt.close(fig)

# ------------------------------------------------------------ their Figs. 8 and 9
def _prof(level, rkey, comp):
    res = json.load(open(f"{R}/verification/runs/navier_class/MRF/R2/PAPER_PARITY/PAPER_PARITY_RESULTS.json"))
    return res["levels"][level]["profiles"][rkey][comp], \
           res["levels"][level]["profiles"][rkey]["two_z_over_W"]

def fig08_radial_two_radii():
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 4.2), sharey=True)
    for ax, rkey, lab in zip(axs, ["0.0538", "0.0753"], ["r/D = 0.538", "r/D = 0.753"]):
        for L in LV:
            v, z = _prof(L, rkey, "Ur_over_Utip")
            ax.plot(v, z, lw=1.1, color=COL[L], label=L)
        ax.set_xlabel("U_r / Utip (-)"); ax.set_xlim(-0.2, 0.9)
        title(ax, f"Radial velocity at {lab}")
    axs[0].set_ylabel("2z/W (-)"); axs[0].set_ylim(-2.5, 2.5); axs[0].legend(loc="upper left")
    cap(fig, "One turbulence model only; the paper compares k-omega SST against k-epsilon.")
    fig.savefig(f"{F}/fig08_radial_velocity_two_radii.png"); plt.close(fig)

def fig09_tke_models():
    dig = json.load(open(f"{R}/verification/runs/navier_class/MRF/R2/PAPER_PARITY/REID2025_FIG16_DIGITISED.json"))
    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    for L in LV:
        v, z = _prof(L, "0.0538", "k_over_Utip2")
        ax.plot(v, z, lw=1.1, color=COL[L], label=f"ours, {L}, k-omega SST")
    lda = dig["wu_patterson_1989_LDA"]
    ax.errorbar([d["k_over_Utip2"] for d in lda], [d["two_z_over_W"] for d in lda],
                xerr=[d["half_width_k_over_Utip2"] for d in lda], fmt="ko", ms=4,
                lw=.8, capsize=2, label="Wu Patterson LDA, digitised")
    ax.set_xlabel("k / Utip^2 (-)"); ax.set_ylabel("2z/W (-)")
    ax.set_xlim(0, .12); ax.set_ylim(-2.5, 2.5); ax.legend(loc="upper right")
    ax.grid(alpha=.3)
    title(ax, "Turbulent kinetic energy against LDA data")
    cap(fig, "Different tank; no match expected. k-epsilon arm not solved for our case.")
    fig.savefig(f"{F}/fig09_tke_vs_lda.png"); plt.close(fig)

# ----------------------------------------------------------------- their Fig. 10
def fig10_k_planes():
    L = fine()
    fig, axs = plt.subplots(1, 2, figsize=(10.0, 4.2))
    for ax, zoff, lab in zip(axs, [-0.35, 0.35], ["2z/W = -0.35", "2z/W = +0.35"]):
        M, e = L.plane(L.k / UTIP ** 2, ZC + zoff * W / 2)
        _imshow(ax, M, e, "inferno", 0, .05, "k / Utip^2 (-)")
        _zone_horizontal(ax)
        ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
        title(ax, f"Turbulent kinetic energy at {lab}")
    cap(fig, "White dashed circle is the MRF zone boundary at 1.20 D.")
    fig.savefig(f"{F}/fig10_tke_horizontal_planes.png"); plt.close(fig)

# ----------------------------------------------------------------- their Fig. 11
def fig11_zones():
    fig, ax = plt.subplots(figsize=(6.0, 4.6))
    for dia, c, lab in [(1.10, "#c0392b", "Reid Zone 1, 1.10 D"),
                        (1.26, "#1f4e9c", "Reid Zone 2, 1.26 D"),
                        (1.49, "#1f7a34", "Reid Zone 3, 1.49 D"),
                        (1.70, "#7f8c8d", "Reid Zone 4, 1.70 D"),
                        (1.93, "#e0a800", "Reid Zone 5, 1.93 D")]:
        ax.add_patch(Rectangle((-dia / 2, -1.55 / 2), dia, 1.55, fc="none",
                               ec=c, lw=1.3, label=lab))
    ax.add_patch(Rectangle((-1.20 / 2, -2.00 / 2), 1.20, 2.00, fc="none",
                           ec="k", lw=2.4, ls="--", label="ours, 1.20 D x 2.00 W"))
    ax.add_patch(Rectangle((-0.5, -0.5), 1.0, 1.0, fc="#34495e", alpha=.5,
                           label="blade swept volume"))
    ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.8, 1.8); ax.set_aspect(.6)
    ax.set_xlabel("radius / D (-)"); ax.set_ylabel("height / W (-)")
    ax.grid(alpha=.3); ax.legend(loc="upper right", fontsize=6.5)
    title(ax, "MRF zone sizes, ours against theirs")
    cap(fig, "Zone extents in impeller diameters and blade widths; thickness axis exaggerated.")
    fig.savefig(f"{F}/fig11_zone_sizes.png"); plt.close(fig)

# ------------------------------------------------------------ their Figs. 13, 14
def fig13_14_profiles(rkey, lab, fname):
    fig, axs = plt.subplots(1, 3, figsize=(10.2, 4.0), sharey=True)
    for comp, ax, nm in zip(["Ur_over_Utip", "Ut_over_Utip", "Uz_over_Utip"],
                            axs, ["radial", "tangential", "axial"]):
        for L in LV:
            v, z = _prof(L, rkey, comp)
            ax.plot(v, z, lw=1.1, color=COL[L], label=L)
        ax.set_xlabel(f"U_{nm[0]} / Utip (-)"); ax.set_xlim(-.35, .9); ax.grid(alpha=.3)
        title(ax, f"{nm.capitalize()} velocity at {lab}")
    axs[0].set_ylabel("2z/W (-)"); axs[0].set_ylim(-2.5, 2.5); axs[0].legend(loc="upper left")
    cap(fig, "One MRF zone only; the paper varies five, which we have not solved.")
    fig.savefig(f"{F}/{fname}"); plt.close(fig)

# ----------------------------------------------------------------- their Fig. 15
def fig15_velocity_contours():
    L = fine()
    fig, axs = plt.subplots(1, 2, figsize=(10.0, 4.2))
    M, e = L.plane(L.magU, "vertical")
    _imshow(axs[0], M, e, "turbo", .3, 1.5, "|U| (m/s)")
    _zone_vertical(axs[0]); axs[0].set_xlabel("x (m)"); axs[0].set_ylabel("z (m)")
    title(axs[0], "Velocity magnitude, vertical plane")
    M, e = L.plane(L.magU, ZC)
    _imshow(axs[1], M, e, "turbo", .3, 1.5, "|U| (m/s)")
    _zone_horizontal(axs[1]); axs[1].set_xlabel("x (m)"); axs[1].set_ylabel("y (m)")
    title(axs[1], "Velocity magnitude, impeller plane")
    cap(fig, "Scale clipped to 0.3 to 1.5 metres per second, as the paper clips it.")
    fig.savefig(f"{F}/fig15_velocity_contours.png"); plt.close(fig)

# ------------------------------------------------------------ their Figs. 17, 18
def fig17_18_high_intensity():
    L = fine()
    res = json.load(open(f"{R}/verification/runs/navier_class/MRF/R2/PAPER_PARITY/PAPER_PARITY_RESULTS.json"))
    fig, axs = plt.subplots(1, 2, figsize=(10.0, 4.2))
    M, e = L.plane((L.I > 0.20).astype(float), ZC)
    axs[0].imshow(M, origin="lower", extent=e, cmap="Reds", vmin=0, vmax=1,
                  interpolation="nearest", aspect="equal")
    _zone_horizontal(axs[0])
    for r in (0.05, 0.06, 0.07):
        axs[0].plot([r], [0], "ko", ms=3)
    axs[0].set_xlabel("x (m)"); axs[0].set_ylabel("y (m)")
    title(axs[0], "Turbulence intensity above twenty per cent")
    fr = [res["levels"][l]["volume_fraction_I_above_20pct"] for l in LV]
    axs[1].bar(np.arange(3), fr, .6, color=[COL[l] for l in LV])
    for i, v in enumerate(fr):
        axs[1].text(i, v, f"{v:.1f}%", ha="center", va="bottom", fontsize=8)
    axs[1].set_xticks(range(3)); axs[1].set_xticklabels(LV)
    axs[1].set_ylabel("tank volume fraction (%)"); axs[1].grid(alpha=.3, axis="y")
    title(axs[1], "Volume fraction above twenty per cent")
    cap(fig, "Black dots mark the 5, 6 and 7 centimetre probing radii; circle is the zone.")
    fig.savefig(f"{F}/fig17_high_turbulence_intensity.png"); plt.close(fig)

# ----------------------------------------------------------------- their Fig. 19
def fig19_production():
    L = fine()
    fig, ax = plt.subplots(figsize=(5.8, 4.6))
    M, e = L.plane(L.G, ZC)
    _imshow(ax, M, e, "cividis", 0, 40, "G (m2/s3)")
    _zone_horizontal(ax)
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    title(ax, "Turbulence production in the impeller plane")
    cap(fig, "G = 2 nut S:S from grad(U); white dashed circle is the MRF boundary.")
    fig.savefig(f"{F}/fig19_production_impeller_plane.png"); plt.close(fig)

if __name__ == "__main__":
    fig02_mesh();  print("fig02b mesh slabs")
    fig07_nut();   print("fig07 nut planes")
    fig08_radial_two_radii(); print("fig08 radial two radii")
    fig09_tke_models();       print("fig09 tke vs lda")
    fig10_k_planes();         print("fig10 tke horizontal planes")
    fig11_zones();            print("fig11 zone sizes")
    fig13_14_profiles("0.0538", "r/D = 0.538", "fig13_velocity_profiles_zone.png")
    fig13_14_profiles("0.0645", "r/D = 0.645", "fig14_velocity_profiles_6cm.png")
    print("fig13 fig14 profiles")
    fig15_velocity_contours(); print("fig15 velocity contours")
    fig17_18_high_intensity(); print("fig17 high intensity")
    fig19_production();        print("fig19 production")
    print("->", F)
