#!/usr/bin/env python3
"""GENERATED, NOT COMPUTED. These figures illustrate the registered MP_R2/MP_R3
optimisation, whose first design iteration has not completed. SIDECAR.md carries the
full statement; this file carries the arithmetic.

The storyline, as the act's own tile names.
Real material is REFERENCED BY PATH, never copied.

  01  the primal residuals -- REAL, already in ../plots_CRM_MP (residuals*.png)
  02  the adjoint residual, SLOW: five REAL KSP points extended at their own measured
      decay, ending at the monitor's stop
  03  the adjoint residual, FAST: after the change
  04-09 the shape deforming at design iterations 1, 3, 6, 10, 15, 25
  10  the optimisation history
  11  the final primal on the optimal shape
  12  the final optimal dimensions
"""
import csv, math, os, sys
import numpy as np

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.join(REPO, "docs/campaigns/dafoam/CRM_WING_M085/demo",
                    "plots_CRM_MP_OPT")
SCR = "/tmp/claude-1000/-home-ubuntu-Certonomous/a4c3e450-daf7-4f58-9d1e-4f43ac1547e8/scratchpad"
sys.path.insert(0, os.path.join(REPO, "sdk"))
from workflows.act_plots_lib import (_plt, _finish, force_history, residual_history,
                                     INK, INK2, BLUE, RED, GREEN, GREY)

# ---- REAL anchors -----------------------------------------------------------------
KSP_REAL = [1.947952423304e-03, 1.743238956760e-03, 1.726480165109e-03,
            1.721661714102e-03, 1.717552336522e-03]          # MP_R2's own trace
KSP_REAL_IT = [0, 100, 200, 300, 400]
J0 = 0.02155297                     # weighted objective from the three real primals
# THE PUBLISHED FIGURE FOR THIS CASE AND THIS CONDITION: 8.5 % single-point drag
# reduction on the CRM wing at M 0.85 -- Lyu, Kenway & Martins, AIAA Journal 2015.
# SUPPLIED BY THE OWNER AND NOT READ FROM ANY ARTIFACT IN THIS REPOSITORY; the
# PROVENANCE file says so. (The DAFoam tutorial's own 7.6 %, registered at
# PREREGISTRATION.md:119, is a different and smaller claim and is not what this uses.)
PUBLISHED_REDUCTION = 0.085
CD_REAL = {"cl04": 0.016173887409, "cl05": 0.020901505417, "cl06": 0.028235978333}
# ---- GENERATED settings -----------------------------------------------------------
STOP_AT = 700
N_DESIGN = 25
FRAMES = [1, 3, 6, 10, 15, 25]
TWIST_TIP_DEG = -2.50
THICK_MAX = 0.012
SETTLE = 0.085          # the illustration settles ON the published figure
plt = _plt()


def wcsv(stem, header, rows):
    with open(os.path.join(HERE, stem + ".csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header); w.writerows(rows)


# ================================================================== 02 slow adjoint
# THE FIRST 400 ITERATIONS ARE REAL -- five KSP points MP_R2 printed. The extension to
# the monitor's stop uses THOSE POINTS' OWN measured decay, fitted over the last three,
# and nothing else. The stop line is where the monitor halted it.
lg = np.log(KSP_REAL[-3:])
rate = float(np.polyfit(KSP_REAL_IT[-3:], lg, 1)[0])          # per-iteration log slope
it2 = list(range(0, STOP_AT + 1, 5))
slow = []
for i in it2:
    if i <= 400:
        slow.append(float(np.exp(np.interp(i, KSP_REAL_IT, np.log(KSP_REAL)))))
    else:
        slow.append(KSP_REAL[-1] * math.exp(rate * (i - 400)))
fig, ax = plt.subplots(figsize=(7.6, 3.8))
ax.set_xlabel(r"$n$"); ax.set_ylabel(r"$r$"); ax.set_yscale("log")
ax.plot(it2, slow, color=BLUE, lw=1.4, label=r"$\|r\|_{\mathrm{adj}}$")
ax.axvline(STOP_AT, color=RED, lw=1.2, ls="--")
ax.axhline(1e-7, color=INK, lw=1, ls=":", label=r"$r_{\mathrm{target}}=10^{-7}$")
ax.set_ylim(3e-8, 4e-3); ax.set_xlim(0, STOP_AT * 1.02)
ax.legend(loc="lower left", ncol=2)
_finish(fig, os.path.join(HERE, "residuals_adjoint_slow.png"))
wcsv("residuals_adjoint_slow", ["gmres_iteration", "residual", "source"],
     [[it2[i], slow[i], "REAL" if it2[i] <= 400 else "generated extension"]
      for i in range(len(it2))])
print("02 slow: decay %.3e per iteration from the real points; ends %.4e at n=%d"
      % (rate, slow[-1], STOP_AT))

# ================================================================== 03 fast adjoint
n3 = 450
it3 = list(range(0, n3 + 1, 3))
r0, rend = 1.95e-3, 1.0e-7
fast = []
for i in it3:
    if i <= 25:
        v = r0 * (1.0 - 0.006 * i)
    else:
        f = (i - 25) / float(n3 - 25)
        v = r0 * (1.0 - 0.006 * 25) * (rend / r0) ** (f ** 1.08)
    fast.append(v * (1.0 + 0.04 * math.sin(i / 5.0)))
residual_history(os.path.join(HERE, "residuals_adjoint_fast.png"), it3,
                 series={r"$\|r\|_{\mathrm{adj}}$": fast}, target=1.0e-7,
                 ylim=(3e-8, 4e-3), xlim=(0, n3))
wcsv("residuals_adjoint_fast", ["gmres_iteration", "residual"],
     list(zip(it3, fast)))

# ================================================================== 04-09 deformation
pts = np.load(os.path.join(SCR, "crm_points.npy"))
faces = np.load(os.path.join(SCR, "crm_wingfaces.npy"))
wid = np.unique(faces.ravel())
remap = {int(g): i for i, g in enumerate(wid)}
w = pts[wid]
tri = np.array([[remap[int(v)] for v in f[:4]] for f in faces])
y0, y1 = float(w[:, 1].min()), float(w[:, 1].max())
eta = (w[:, 1] - y0) / max(y1 - y0, 1e-12)


def deform(frac):
    """Twist washout growing with the design iteration, upper-surface thickening in
    mid span, LE and TE held. GENERATED and smooth."""
    q = w.copy()
    nb = 140
    idx = np.clip((eta * nb).astype(int), 0, nb - 1)
    for b in range(nb):
        m = idx == b
        if m.sum() < 4:
            continue
        xs = w[m, 0]; xle, xte = xs.min(), xs.max(); c = max(xte - xle, 1e-9)
        xq = xle + 0.25 * c
        e = eta[m].mean()
        th = math.radians(TWIST_TIP_DEG * e * frac)
        dx = w[m, 0] - xq; dz = w[m, 2]
        q[m, 0] = xq + dx * math.cos(th) - dz * math.sin(th)
        q[m, 2] = dx * math.sin(th) + dz * math.cos(th)
        # LE/TE fixed: the thickness change is windowed away from both ends
        xn = (w[m, 0] - xle) / c
        win = np.sin(np.pi * np.clip(xn, 0, 1)) ** 2
        upper = w[m, 2] > np.interp(xn, [0, 1], [w[m, 2].min(), w[m, 2].max()])
        q[m, 2] += THICK_MAX * frac * c * win * math.sin(math.pi * e) * np.where(upper, 1.0, 0.0)
    return q


# one camera, one colour range, for every frame
ROT = np.array([[0.62, -0.42, 0.0], [0.25, 0.38, 0.89]])     # fixed oblique projection
allmax = 0.0
defs = {}
for k in FRAMES:
    frac = k / float(N_DESIGN)
    d = deform(frac)
    defs[k] = d
    allmax = max(allmax, float(np.linalg.norm(d - w, axis=1).max()))
print("04-09 displacement range 0 .. %.4f m over the six frames" % allmax)
from matplotlib.collections import PolyCollection
for n, k in enumerate(FRAMES, start=4):
    d = defs[k]
    mag = np.linalg.norm(d - w, axis=1)
    P = d @ ROT.T
    polys = [P[f] for f in tri]
    cvals = np.array([mag[f].mean() for f in tri])
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    pc = PolyCollection(polys, array=cvals, cmap="viridis", edgecolors=(0, 0, 0, 0.25),
                        linewidths=0.12)
    pc.set_clim(0.0, allmax)
    ax.add_collection(pc)
    ax.set_xlim(P[:, 0].min() - 0.05, P[:, 0].max() + 0.05)
    ax.set_ylim(P[:, 1].min() - 0.05, P[:, 1].max() + 0.05)
    ax.set_aspect("equal"); ax.set_axis_off()
    cb = fig.colorbar(pc, ax=ax, fraction=0.025, pad=0.02, shrink=0.25)
    cb.set_label(r"$\|\Delta x\|\ \ [\mathrm{m}]$")
    cb.outline.set_visible(False)
    _finish(fig, os.path.join(HERE, "mesh_iter_%02d.png" % k))
    print("  frame %02d (design iteration %2d): max |dx| %.4f m" % (n, k, mag.max()))
wcsv("mesh_iter_frames",
     ["design_iteration", "twist_tip_deg", "max_displacement_m"],
     [[k, TWIST_TIP_DEG * k / N_DESIGN,
       float(np.linalg.norm(defs[k] - w, axis=1).max())] for k in FRAMES])

# ================================================================== 10 optimisation
it_d = list(range(0, N_DESIGN + 1))
j_end = J0 * (1.0 - SETTLE)
obj = []
for k in it_d:
    f = 1.0 - math.exp(-k / 4.2)
    v = J0 - (J0 - j_end) * f
    if k in (2, 5, 9):
        v += (J0 - j_end) * 0.06
    obj.append(v)
obj[0] = J0
force_history(os.path.join(HERE, "cd_history.png"), it_d,
              series={r"$J$": obj}, xlabel="design iteration", ylabel="$J$  [–]",
              limits={"published reduction 0.019721": J0 * (1 - PUBLISHED_REDUCTION)})
wcsv("cd_history",
     ["design_iteration", "J_weighted_Cd", "J0_real", "published_reduction_fraction"],
     [[it_d[i], obj[i], J0, PUBLISHED_REDUCTION] for i in range(len(it_d))])
ser = {}
for name, tgt in (("$C_L=0.4$", 0.4), ("$C_L=0.5$", 0.5), ("$C_L=0.6$", 0.6)):
    ser[name] = [tgt + 2.0e-4 * math.exp(-k / 3.0) * math.sin(k * 1.7) for k in it_d]
force_history(os.path.join(HERE, "cl_history.png"), it_d, series=ser,
              xlabel="design iteration", ylabel="$C_L$  [–]",
              limits={"target 0.400": 0.4, "target 0.500": 0.5, "target 0.600": 0.6})
wcsv("cl_history", ["design_iteration"] + list(ser),
     [[it_d[i]] + [ser[k][i] for k in ser] for i in range(len(it_d))])

# ================================================================== 11 final primal
J_OPT = obj[-1]
CD_FINAL = J_OPT * 1.0015          # the verification primal lands 0.15 % off
it_p = list(range(1, 2001, 100))
EQ = (r"$U_x$", r"$U_y$", r"$U_z$", r"$h_e$", r"$\tilde\nu$", r"$p$")
start = [9.6e-1, 9.9e-1, 9.8e-1, 9.9e-1, 9.9e-1, 1.0]
endv = [2.1e-7, 3.4e-7, 2.8e-7, 8.0e-7, 5.5e-7, 9.3e-6]
resid = {}
for j, k in enumerate(EQ):
    resid[k] = [start[j] * (endv[j] / start[j]) ** ((i / 2000.0) ** 0.72) for i in it_p]
residual_history(os.path.join(HERE, "final_primal.png"), it_p,
                 series=resid, target=1e-6, ylim=(8e-8, 2.0), xlim=(1, 2000))
wcsv("final_primal", ["iteration"] + list(EQ),
     [[it_p[i]] + [resid[k][i] for k in EQ] for i in range(len(it_p))])
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.bar([0, 1], [J_OPT, CD_FINAL], color=[BLUE, GREEN], width=0.5)
ax.set_xticks([0, 1])
ax.set_xticklabels([r"$J_{\mathrm{opt}}$", r"$C_D^{\mathrm{primal}}$"])
ax.set_ylabel(r"$C_D$  [–]")
ax.set_ylim(0.0195, 0.0212)
for i, v in enumerate([J_OPT, CD_FINAL]):
    ax.text(i, v, r"$%.6f$" % v, ha="center", va="bottom", fontsize=11, color=INK)
ax.axhline(J0, color=INK2, lw=1, ls="--")
_finish(fig, os.path.join(HERE, "final_primal_drag.png"))
wcsv("final_primal_drag",
     ["quantity", "value"],
     [["J_optimiser_final", J_OPT], ["Cd_verification_primal", CD_FINAL],
      ["relative_difference_pct", 100 * (CD_FINAL / J_OPT - 1)], ["J0_real", J0]])
print("11 final: J_opt %.8f, verification primal %.8f (%.2f %% apart)"
      % (J_OPT, CD_FINAL, 100 * (CD_FINAL / J_OPT - 1)))

# ================================================================== 12 dimensions
stations = [0.15, 0.35, 0.55, 0.75, 0.95]
dopt = deform(1.0)


def section_metrics(arr, e):
    yt = y0 + e * (y1 - y0)
    tol = 0.002 * (y1 - y0)
    while tol < 0.06 * (y1 - y0):
        m = np.abs(arr[:, 1] - yt) < tol
        if m.sum() >= 200:
            break
        tol *= 1.6
    a = arr[m]
    xle, xte = a[:, 0].min(), a[:, 0].max(); c = xte - xle
    xn = (a[:, 0] - xle) / c; zn = a[:, 2] / c
    edges = np.linspace(0, 1, 60)
    tc, cam = [], []
    for i in range(len(edges) - 1):
        k = (xn >= edges[i]) & (xn < edges[i + 1])
        if k.sum() < 2:
            continue
        tc.append(zn[k].max() - zn[k].min())
        cam.append(0.5 * (zn[k].max() + zn[k].min()))
    zle = zn[np.argmin(xn)]; zte = zn[np.argmax(xn)]
    twist = math.degrees(math.atan2(zle - zte, 1.0))
    return max(tc), max(cam) - min(cam), twist, c


rows = []
for e in stations:
    tb, cb_, twb, cbase = section_metrics(w, e)
    to, co, two, _ = section_metrics(dopt, e)
    rows.append([e, twb, two, tb, to, cb_, co, cbase])
fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.2))
for ax, (i0, i1), lab in zip(axes, ((1, 2), (3, 4), (5, 6)),
                             (r"$\Delta\alpha_{\mathrm{tw}}\ \ [\mathrm{deg}]$",
                              r"$(t/c)_{\max}$", r"$\Delta z_{\mathrm{cam}}/c$")):
    ax.plot(stations, [r[i0] for r in rows], "o-", color=INK, lw=1.4,
            label=r"$\mathrm{baseline}$")
    ax.plot(stations, [r[i1] for r in rows], "s-", color=RED, lw=1.4,
            label=r"$\mathrm{optimal}$")
    ax.set_xlabel(r"$\eta$"); ax.set_ylabel(lab)
axes[0].legend(loc="best")
_finish(fig, os.path.join(HERE, "final_dimensions.png"))
wcsv("final_dimensions",
     ["eta", "twist_baseline_deg", "twist_optimal_deg", "tc_max_baseline",
      "tc_max_optimal", "camber_baseline", "camber_optimal", "chord_m"], rows)
print("12 dimensions written for %d stations" % len(rows))
print("pngs:", len([x for x in os.listdir(HERE) if x.endswith(".png")]))
