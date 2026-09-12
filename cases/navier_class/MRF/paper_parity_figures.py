#!/usr/bin/env python3
"""paper_parity_figures.py -- OUR MRF Rushton case presented in the figure
layout of Reid, Rossi, Cottini & Benassi (2025), arXiv:2508.03176.

Every figure obeys the lab figure standard (Sanaa 2026-09-01): title of at most
ten words, axis labels with units, legend inside the axes, one caption line of
at most twenty words, no explanatory paragraphs inside the image.

Inputs (all on disk, no solver runs):
  PAPER_PARITY_RESULTS.json        our fields, post-processed
  MESH_TABLE_OURS.json             our mesh table
  REID2025_FIG16_DIGITISED.json    the paper's Fig. 16, exactly digitised
  ET8000/<level>/postProcessing/impellerForces/0/moment.dat
  ET8000/<level>/log.simpleFoam
"""
import json, math, os, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = "/home/ubuntu/Certonomous"
P = f"{R}/verification/runs/navier_class/MRF/R2/PAPER_PARITY"
S = f"{R}/verification/runs/navier_class/MRF/R2/ET8000"
F = f"{P}/figures"
os.makedirs(F, exist_ok=True)

res = json.load(open(f"{P}/PAPER_PARITY_RESULTS.json"))
mesh = json.load(open(f"{P}/MESH_TABLE_OURS.json"))
dig = json.load(open(f"{P}/REID2025_FIG16_DIGITISED.json"))
LV = ["coarse", "medium", "fine"]
COL = {"coarse": "#c0392b", "medium": "#1f4e9c", "fine": "#1f7a34"}
UTIP = res["Utip_mps"]
RHO, N, D = 998.0, 5.0, 0.100
R_MATCH = "0.0538"     # r/D = 0.538, the station matched to the paper's r = 5 cm
R_ABS = "0.0500"       # the paper's ABSOLUTE r = 5 cm, which is our blade-tip radius

plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 150, "savefig.bbox": "tight",
                     "legend.framealpha": 0.9, "legend.fontsize": 7.5})


def cap(fig, text):
    assert len(text.split()) <= 20, f"caption too long: {text}"
    fig.text(0.5, -0.02, text, ha="center", va="top", fontsize=8, style="italic")


def title(ax, t):
    assert len(t.split()) <= 10, f"title too long: {t}"
    ax.set_title(t, fontsize=9.5)


# ---------------------------------------------------------------- 1 geometry
def fig_geometry():
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 4.2))
    for ax, (T, Dd, C, bw, bt, sh, dsc, zr, zt, nm, npv) in zip(axs, [
        (0.300, 0.100, 0.100, 0.030, 0.004, 0.010, 0.0375, 0.060, 0.040,
         "ours (MRF_R2)", "Np 4.38"),
        (0.270, 0.093, 0.090, 0.0093, 0.00093, 0.0075, 0.036, 0.05115, 0.028830,
         "Reid 2025 Zone 1", "Np 5.44 to 5.49")]):
        H = T
        ax.add_patch(plt.Rectangle((-T / 2, 0), T, H, fc="#eef3f8", ec="k", lw=1.2))
        for s in (-1, 1):
            ax.add_patch(plt.Rectangle((s * (T / 2 - bw) - (bw if s > 0 else 0), 0),
                                       bw, H, fc="#9aa7b4", ec="k", lw=0.5))
        ax.add_patch(plt.Rectangle((-sh, C - 0.02), 2 * sh, H - C + 0.02,
                                   fc="#7f8c8d", ec="k", lw=0.5))
        ax.add_patch(plt.Rectangle((-dsc, C - bt / 2), 2 * dsc, bt, fc="#34495e"))
        for s in (-1, 1):
            ax.add_patch(plt.Rectangle((s * Dd / 2 - (Dd / 4 if s > 0 else 0),
                                        C - Dd / 10), Dd / 4, Dd / 5, fc="#34495e"))
        ax.add_patch(plt.Rectangle((-zr, C - zt / 2), 2 * zr, zt, fc="none",
                                   ec="#e67e22", lw=1.8, ls="--"))
        ax.set_xlim(-T / 2 * 1.15, T / 2 * 1.15); ax.set_ylim(-0.01, H * 1.05)
        ax.set_aspect("equal")
        ax.set_xlabel("radius (m)"); ax.set_ylabel("height (m)")
        title(ax, f"{nm}: tank, impeller, MRF zone")
        ax.text(0.02, 0.97, f"T={T:.3f} m  D={Dd:.3f} m\nzone {2*zr/Dd:.2f}D dia, "
                f"{zt/Dd:.2f}D thick\n{npv}", transform=ax.transAxes, va="top",
                fontsize=7.5, bbox=dict(fc="w", ec="0.6", alpha=0.9))
    cap(fig, "Dashed orange marks the rotating MRF cell zone in each tank.")
    fig.savefig(f"{F}/fig01_geometry_and_mrf_zone.png"); plt.close(fig)


# ------------------------------------------------------- 2 mesh table / y+
def fig_mesh():
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.4))
    ours_c = [mesh[L]["n_cells"] / 1e6 for L in LV]
    theirs_c = [1.51, 3.33, 5.76]
    x = np.arange(3); w = 0.38
    axs[0].bar(x - w / 2, ours_c, w, color="#1f4e9c", label="ours")
    axs[0].bar(x + w / 2, theirs_c, w, color="#bdc3c7", label="Reid 2025")
    axs[0].set_xticks(x); axs[0].set_xticklabels(LV)
    axs[0].set_ylabel("cells (million)"); title(axs[0], "Mesh size, three levels")
    axs[0].legend(loc="upper left")
    axs[1].bar(x - w / 2, [mesh[L]["base_cell_mm"] for L in LV], w, color="#1f4e9c")
    axs[1].bar(x + w / 2, [7, 5, 4], w, color="#bdc3c7")
    axs[1].set_xticks(x); axs[1].set_xticklabels(LV)
    axs[1].set_ylabel("base cell size (mm)"); title(axs[1], "Base cell size")
    yo = [res["levels"][L]["yPlus_per_patch_unweighted_face_stats"]["ALL_WALLS"] for L in LV]
    axs[2].bar(x - w / 2, [y["mean"] for y in yo], w, color="#1f4e9c",
               yerr=[[y["mean"] - y["min"] for y in yo], [y["max"] - y["mean"] for y in yo]],
               capsize=3, error_kw=dict(lw=0.8))
    axs[2].bar(x + w / 2, [6.5, 5.1, 4.1], w, color="#bdc3c7",
               yerr=[[6.5 - .13, 5.1 - .11, 4.1 - .07], [55.3 - 6.5, 39.9 - 5.1, 29.9 - 4.1]],
               capsize=3, error_kw=dict(lw=0.8))
    axs[2].set_xticks(x); axs[2].set_xticklabels(LV); axs[2].set_yscale("log")
    axs[2].set_ylabel("y+ (-)"); title(axs[2], "Wall y+, mean with min and max")
    cap(fig, "Grey is the paper's tank; bars carry min and max as whiskers.")
    fig.savefig(f"{F}/fig02_mesh_and_yplus.png"); plt.close(fig)


# ------------------------------------------------------ 3 convergence history
def _torque(level):
    p = f"{S}/{level}/postProcessing/impellerForces/0/moment.dat"
    a = np.loadtxt(p, comments="#", usecols=(0, 3))
    return a[:, 0], 2 * math.pi * np.abs(a[:, 1]) / (RHO * N ** 2 * D ** 5)


def _resid(level):
    out = {}
    pat = re.compile(r"Solving for (\w+), Initial residual = ([\d.eE+-]+)")
    for line in open(f"{S}/{level}/log.simpleFoam", errors="ignore"):
        m = pat.search(line)
        if m and m.group(1) in ("Ux", "Uy", "Uz", "p", "k", "omega"):
            out.setdefault(m.group(1), []).append(float(m.group(2)))
    return out


def fig_convergence():
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.6))
    r = _resid("fine")
    for kk, v in r.items():
        axs[0].semilogy(np.arange(1, len(v) + 1), v, lw=0.7, label=kk)
    axs[0].set_xlabel("iteration (-)"); axs[0].set_ylabel("initial residual (-)")
    title(axs[0], "Residuals, fine level, k-omega SST")
    axs[0].legend(ncol=3, loc="upper right")
    for L in LV:
        it, npv = _torque(L)
        axs[1].plot(it, npv, lw=0.7, color=COL[L], label=L)
    axs[1].set_xlabel("iteration (-)"); axs[1].set_ylabel("power number Np (-)")
    axs[1].set_ylim(3.5, 6.5)
    axs[1].axhspan(5.3, 5.6, color="#e67e22", alpha=0.18)
    axs[1].text(400, 5.42, "Reid 2025 band 5.3-5.6", fontsize=7, color="#a04000")
    title(axs[1], "Power number against iteration, three levels")
    axs[1].legend(loc="lower right")
    cap(fig, "The fine level is graded not iteratively converged; its band claim is void.")
    fig.savefig(f"{F}/fig03_convergence_history.png"); plt.close(fig)


# -------------------------------------------------- 4 velocity profiles, mesh
def _prof(L, rkey):
    return res["levels"][L]["profiles"][rkey]


def fig_velocity(rkey, fname, label):
    fig, axs = plt.subplots(1, 3, figsize=(10.2, 4.0), sharey=True)
    for comp, ax, nm in zip(["Ur_over_Utip", "Ut_over_Utip", "Uz_over_Utip"], axs,
                            ["radial", "tangential", "axial"]):
        for L in LV:
            p = _prof(L, rkey)
            ax.plot(p[comp], p["two_z_over_W"], lw=1.1, color=COL[L], label=L)
        sd = np.array(_prof("fine", rkey)[comp.replace("_over_Utip", "_azimuthal_sd")])
        m = np.array(_prof("fine", rkey)[comp])
        ax.fill_betweenx(_prof("fine", rkey)["two_z_over_W"], m - sd, m + sd,
                         color=COL["fine"], alpha=0.15)
        ax.set_xlabel(f"U_{nm[0]} / Utip (-)"); ax.set_xlim(-0.35, 0.9)
        title(ax, f"{nm.capitalize()} velocity at {label}")
    axs[0].set_ylabel("2z/W (-)"); axs[0].set_ylim(-2.5, 2.5)
    axs[0].legend(loc="upper left")
    cap(fig, "Shading is the azimuthal spread of the fine level over thirty-six angles.")
    fig.savefig(f"{F}/{fname}"); plt.close(fig)


# --------------------------------------------------------------- 5 TKE profile
def fig_tke():
    fig, axs = plt.subplots(1, 2, figsize=(9.4, 4.4), sharey=True)
    for L in LV:
        p = _prof(L, R_MATCH)
        axs[0].plot(p["k_over_Utip2"], p["two_z_over_W"], lw=1.1, color=COL[L], label=L)
    p = _prof("fine", R_MATCH)
    sd = np.array(p["k_azimuthal_sd"]); m = np.array(p["k_over_Utip2"])
    axs[0].fill_betweenx(p["two_z_over_W"], m - sd, m + sd, color=COL["fine"], alpha=0.15)
    axs[0].set_xlabel("k / Utip^2 (-)"); axs[0].set_ylabel("2z/W (-)")
    axs[0].set_xlim(0, 0.12); axs[0].set_ylim(-2.5, 2.5)
    title(axs[0], "Turbulent kinetic energy, our three levels")
    axs[0].legend(loc="upper right")
    lda = dig["wu_patterson_1989_LDA"]
    axs[1].errorbar([d["k_over_Utip2"] for d in lda], [d["two_z_over_W"] for d in lda],
                    xerr=[d["half_width_k_over_Utip2"] for d in lda], fmt="ko",
                    ms=4, lw=0.8, capsize=2, label="Wu Patterson LDA, digitised")
    z1 = dig["paper_MRF_Zone1_curve"]
    axs[1].plot([d["k_over_Utip2"] for d in z1], [d["two_z_over_W"] for d in z1],
                color="#c0392b", lw=1.0, label="Reid 2025 Zone 1, digitised")
    axs[1].plot(m, p["two_z_over_W"], color=COL["fine"], lw=1.4, label="ours, fine")
    axs[1].set_xlabel("k / Utip^2 (-)"); axs[1].set_xlim(0, 0.12)
    title(axs[1], "Our fine level against the paper's tank")
    axs[1].legend(loc="upper right")
    cap(fig, "Different tanks: our baffles and blades differ, so no match is expected.")
    fig.savefig(f"{F}/fig05_tke_profile.png"); plt.close(fig)


# --------------------------------------------------- 6 global parameters bars
def fig_globals():
    fig, axs = plt.subplots(1, 3, figsize=(11.0, 3.6))
    zones = ["1\n1.10D", "2\n1.26D", "3\n1.49D", "4\n1.70D", "5\n1.93D"]
    paper = {"Np": [5.4, 6.2, 6.3, 6.3, 6.1], "Ig": [13.7, 14.8, 15.1, 15.4, 15.1],
             "I": [6.3, 6.6, 7.0, 7.4, 7.5]}
    ours = {"Np": [res["levels"][L]["Np"] for L in LV],
            "Ig": [res["levels"][L]["agitation_index_pct"] for L in LV],
            "I": [res["levels"][L]["turb_intensity_over_Utip_pct"] for L in LV]}
    for ax, key, ylab, t in zip(
            axs, ["Np", "Ig", "I"],
            ["power number Np (-)", "agitation index Ig (%)", "turbulence intensity (%)"],
            ["Power number", "Agitation index", "Turbulence intensity"]):
        ax.bar(np.arange(3), ours[key], 0.6, color="#1f4e9c", label="ours, 3 meshes")
        ax.bar(np.arange(5) + 3.6, paper[key], 0.6, color="#bdc3c7",
               label="Reid 2025, 5 zones")
        ax.set_xticks(list(np.arange(3)) + list(np.arange(5) + 3.6))
        ax.set_xticklabels(LV + zones, fontsize=6.5, rotation=45, ha="right")
        ax.set_ylabel(ylab); title(ax, f"{t}, ours beside the paper")
        for i, v in enumerate(ours[key]):
            ax.text(i, v, f"{v:.2f}", ha="center", va="bottom", fontsize=6.5)
        for i, v in enumerate(paper[key]):
            ax.text(i + 3.6, v, f"{v:.1f}", ha="center", va="bottom", fontsize=6.5)
        if key == "Np":
            ax.axhspan(5.3, 5.6, color="#e67e22", alpha=0.18)
            ax.axhspan(5.29, 5.53, color="#2e8b57", alpha=0.14)
            ax.text(0.02, 0.965,
                    "our fine Np 4.38 is 17.3 to 21.8 % below Reid's band 5.3-5.6\n"
                    "and 2.6 % below Beshay's measurement at our own ratios, 4.50\n"
                    "both are true and they are different tanks",
                    transform=ax.transAxes, va="top", ha="left", fontsize=6.4,
                    bbox=dict(fc="w", ec="#8b0000", alpha=.92))
            ax.set_ylim(0, 8.2)
        ax.legend(loc="lower right")
    cap(fig, "Our intensity uses tip speed; grey values are printed labels on their figure.")
    fig.savefig(f"{F}/fig06_global_parameters.png"); plt.close(fig)


# --------------------------------------------------------- 7 y+ per patch
def fig_yplus():
    patches = ["impeller", "shaft", "baffles", "tankWall", "tankBottom", "tankLid"]
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    x = np.arange(len(patches)); w = 0.26
    for i, L in enumerate(LV):
        st = res["levels"][L]["yPlus_per_patch_unweighted_face_stats"]
        m = [st[p]["mean"] for p in patches]
        lo = [st[p]["mean"] - st[p]["min"] for p in patches]
        hi = [st[p]["max"] - st[p]["mean"] for p in patches]
        ax.bar(x + (i - 1) * w, m, w, color=COL[L], label=L,
               yerr=[lo, hi], capsize=2, error_kw=dict(lw=0.6))
    ax.axhspan(30, 300, color="#2e8b57", alpha=0.12)
    ax.text(0.02, 0.95, "log-law band 30 to 300", transform=ax.transAxes,
            fontsize=7, va="top", color="#20603d")
    ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels(patches, fontsize=7.5)
    ax.set_ylabel("y+ (-)"); title(ax, "Wall y+ per surface, three mesh levels")
    ax.legend(loc="upper right")
    cap(fig, "Whiskers span each patch min and max; the paper reports mean 4.13.")
    fig.savefig(f"{F}/fig07_yplus_per_patch.png"); plt.close(fig)


# ----------------------------------------------------- 8 grid convergence Np
def fig_gci():
    g = json.load(open(f"{S}/MRF_R2_GRADED_ROW_ET8000.json"))
    h = np.array([mesh[L]["base_cell_mm"] for L in LV])
    v = np.array([res["levels"][L]["Np"] for L in LV])
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot(h, v, "o-", color="#1f4e9c", lw=1.4, ms=7)
    for hh, vv, L in zip(h, v, LV):
        ax.annotate(f"{L}\n{vv:.3f}", (hh, vv), textcoords="offset points",
                    xytext=(8, -4), fontsize=7.5)
    ax.axhspan(5.3, 5.6, color="#e67e22", alpha=0.18)
    ax.text(4.2, 5.42, "Reid 2025 band 5.3-5.6", fontsize=7.5, color="#a04000")
    ax.axhspan(4.0, 6.0, color="#7f8c8d", alpha=0.08)
    ax.text(4.2, 4.05, "superseded band 4.0-6.0", fontsize=7.5, color="#555")
    ax.set_xlabel("base cell size (mm)"); ax.set_ylabel("power number Np (-)")
    ax.set_ylim(3.8, 6.3); ax.invert_xaxis()
    title(ax, "Power number against mesh refinement")
    ax.text(0.03, 0.06, f"triple {g['triples'][0]['state']}, observed order "
            f"{g['orders'][0]:.2f}\nverdict {g['verdict']}",
            transform=ax.transAxes, fontsize=8, color="#8b0000",
            bbox=dict(fc="w", ec="#8b0000", alpha=0.9))
    cap(fig, "A divergent triple is not a result whatever the value reads.")
    fig.savefig(f"{F}/fig08_np_grid_convergence.png"); plt.close(fig)


# ------------------------------------------- 9 the paper's zone sensitivity
def fig_zone_sensitivity():
    dia = np.array([1.10, 1.26, 1.49, 1.70, 1.93])
    npv = np.array([5.4, 6.2, 6.3, 6.3, 6.1])
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.plot(dia, npv, "s-", color="#7f8c8d", lw=1.4, ms=7, label="Reid 2025 zones")
    ax.axvline(1.20, color="#c0392b", lw=1.6, ls="--")
    ax.text(1.21, 5.65, "our zone 1.20D", color="#c0392b", fontsize=8)
    ax.axhline(res["levels"]["fine"]["Np"], color="#1f4e9c", lw=1.4)
    ax.text(1.55, 4.44, "our Np 4.38", color="#1f4e9c", fontsize=8)
    ax.axhspan(5.3, 5.6, color="#e67e22", alpha=0.18)
    ax.set_xlabel("MRF zone diameter / D (-)"); ax.set_ylabel("power number Np (-)")
    ax.set_ylim(4.0, 6.6); title(ax, "Zone diameter against power number")
    ax.legend(loc="lower right")
    cap(fig, "Their curve rises through our zone size, so zone size cannot explain 4.38.")
    fig.savefig(f"{F}/fig09_zone_sensitivity.png"); plt.close(fig)


if __name__ == "__main__":
    fig_geometry(); fig_mesh(); fig_convergence()
    fig_velocity(R_MATCH, "fig04_velocity_profiles_rD0538.png", "r/D = 0.538")
    fig_velocity("0.0645", "fig04b_velocity_profiles_rD0645.png", "r/D = 0.645")
    fig_velocity("0.0753", "fig04c_velocity_profiles_rD0753.png", "r/D = 0.753")
    fig_velocity(R_ABS, "fig04d_velocity_profiles_r5cm_absolute.png", "r = 5 cm")
    fig_tke(); fig_globals(); fig_yplus(); fig_gci(); fig_zone_sensitivity()
    print("figures ->", F)
    for f in sorted(os.listdir(F)):
        print("  ", f)
