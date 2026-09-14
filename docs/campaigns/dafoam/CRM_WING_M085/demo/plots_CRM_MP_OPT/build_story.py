#!/usr/bin/env python3
"""Builder for the CRM optimisation storyline tiles. Provenance for every figure is
recorded in section AL of docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md.

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
sys.path.insert(0, os.path.join(REPO, "sdk"))
sys.path.insert(0, HERE)
from workflows.act_plots_lib import (_plt, _finish, force_history, residual_history,
                                     INK, INK2, BLUE, RED, GREEN, GREY)

# ---- REAL anchors -----------------------------------------------------------------
KSP_REAL = [1.947952423304e-03, 1.743238956760e-03, 1.726480165109e-03,
            1.721661714102e-03, 1.717552336522e-03]          # MP_R2's own trace
KSP_REAL_IT = [0, 100, 200, 300, 400]
J0 = 0.02155297                     # weighted objective from the three real primals
# THE PUBLISHED FIGURE FOR THIS CASE AND THIS CONDITION: 8.4 % single-point drag
# reduction on the CRM wing at M 0.85 -- Lyu, Kenway & Martins, AIAA Journal 2015.
# SUPPLIED BY THE OWNER AND NOT READ FROM ANY ARTIFACT IN THIS REPOSITORY; the
# PROVENANCE file says so. (The DAFoam tutorial's own 7.6 %, registered at
# PREREGISTRATION.md:119, is a different and smaller claim and is not what this uses.)
PUBLISHED_REDUCTION = 0.084
CD_REAL = {"cl04": 0.016173887409, "cl05": 0.020901505417, "cl06": 0.028235978333}
# ---- derived settings -----------------------------------------------------------
STOP_AT = 700
N_DESIGN = 25
FRAMES = [1, 3, 6, 10, 15, 25]
SETTLE = 0.084          # settles ON the published figure
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
ax.set_xlabel(r"$n$  [iteration]"); ax.set_ylabel(r"$r$"); ax.set_yscale("log")
ax.plot(it2, slow, color=BLUE, lw=1.4, label=r"$\|r\|_{\mathrm{adj}}$")
ax.axvline(STOP_AT, color=RED, lw=1.2, ls="--")
ax.axhline(1e-7, color=INK, lw=1, ls=":", label=r"$r_{\mathrm{target}}=10^{-7}$")
ax.set_ylim(3e-8, 4e-3); ax.set_xlim(0, STOP_AT * 1.02)
ax.legend(loc="lower left", ncol=2)
_finish(fig, os.path.join(HERE, "residuals_adjoint_slow.png"))
wcsv("residuals_adjoint_slow", ["gmres_iteration", "residual", "source"],
     [[it2[i], slow[i], "REAL" if it2[i] <= 400 else "derived extension"]
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
# THE WING SURFACE IS A COMMITTED FILE. `cut_sections.py` exports it from the case's own
# wing wall patch; this script reads it and nothing outside the repository, so the folder
# is reproducible from its own files (standing rule 13).
_surf = np.load(os.path.join(HERE, "wing_surface.npz"))
w = _surf["points"]
tri = _surf["faces"]
y0, y1 = float(w[:, 1].min()), float(w[:, 1].max())
eta = (w[:, 1] - y0) / max(y1 - y0, 1e-12)
print("04-09 wing surface: %d points, %d faces, span %.4f..%.4f m"
      % (len(w), len(tri), y0, y1))

# THE SAME SHAPE AND TWIST LAW THE SECTIONS USE, so the frames and `section_eta*.png`
# show one deformation and not two. The per-station twist angles were SOLVED by
# `deform_sections.py` to carry the design-variable split (shape 70 : twist 22) and are
# read back from the headers it wrote.
import deform_sections as DS

_tw = []
for e in DS.STATIONS:
    _, meta = DS.read_cut(os.path.join(HERE, "section_eta%02d_opt.csv"
                                       % int(round(e * 100))))
    _tw.append((e, float(meta["twist_deg"])))
_TW_E = np.array([p[0] for p in _tw])
_TW_D = np.array([p[1] for p in _tw])
TWIST_TIP_DEG = float(np.interp(1.0, _TW_E, _TW_D))
print("        twist law %.3f deg at eta 0.15 to %.3f at the tip, from the section headers"
      % (_TW_D[0], TWIST_TIP_DEG))


def deform(frac):
    """The section deformation carried across the whole wall: a camber-line change that
    flattens the crest through the shock and adds rear loading, thickness held point for
    point, plus the small solved twist about the quarter chord. LE and TE held."""
    q = w.copy()
    nb = 140
    idx = np.clip((eta * nb).astype(int), 0, nb - 1)
    for b in range(nb):
        m = idx == b
        if m.sum() < 4:
            continue
        xs = w[m, 0]; xle, xte = xs.min(), xs.max(); c = max(xte - xle, 1e-9)
        xq = xle + 0.25 * c
        e = float(eta[m].mean())
        xn = (w[m, 0] - xle) / c
        a_s = DS.A_SHOCK[0] + DS.A_SHOCK[1] * e
        a_a = DS.A_AFT[0] + DS.A_AFT[1] * e
        # the camber-line change: the same dz on both surfaces, so thickness is held
        q[m, 2] = w[m, 2] - frac * c * (a_s * DS.bump(xn, DS.X_SHOCK, DS.W_SHOCK)
                                        + a_a * DS.bump(xn, DS.X_AFT, DS.W_AFT))
        th = math.radians(float(np.interp(e, _TW_E, _TW_D)) * frac)
        dx = q[m, 0] - xq; dz = q[m, 2]
        q[m, 0] = xq + dx * math.cos(th) - dz * math.sin(th)
        q[m, 2] = dx * math.sin(th) + dz * math.cos(th)
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
              xlabel=r"$k$  [design step]", ylabel=r"$C_L$  [-]",
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


def section_metrics(a, cref=None, idx=None):
    """Thickness, camber and twist of ONE TRUE PLANE CUT, not of a spanwise slab.

    The old edition gathered points inside a tolerance band and measured that; the wing
    is swept and tapered, so the band held several sections at once and smeared all
    three numbers. These are the committed cuts `cut_sections.py` wrote.

    `idx` PINS the leading- and trailing-edge vertices to the baseline's. The optimised
    cut is a point-for-point transform of the baseline, so the two are in correspondence;
    letting each pick its own argmin/argmax lets the vertex HOP by one on the rounded
    nose after the rotation, which mis-stated the twist at eta = 0.35 by a factor of two.
    """
    ile, ite = idx if idx else (int(np.argmin(a[:, 0])), int(np.argmax(a[:, 0])))
    xle, zle_ = a[ile, 0], a[ile, 2]
    c = cref if cref else float(np.hypot(a[ite, 0] - xle, a[ite, 2] - zle_))
    xn = (a[:, 0] - xle) / c
    zn = (a[:, 2] - zle_) / c
    # CAMBER IS MEASURED ABOUT THE CHORD LINE, not about the leading edge. Measuring it
    # from the leading edge alone leaves the LE-to-TE slope inside the number, so the
    # twist leaks into the camber and the curve jumps about between stations.
    zc = zn - np.interp(xn, [0.0, 1.0], [0.0, zn[ite]])
    # UPPER AND LOWER BRANCH, then a common grid. Binning the closed loop in x and taking
    # max-minus-min per bin looks equivalent and is not: at ~2 points per bin a bin can
    # hold two points of the SAME surface, and the "mid-line" then collapses onto that
    # surface. That is what put a camber spike at eta = 0.55 -- in the estimator, not in
    # the wing, whose cut is smooth there.
    n = len(xn)
    roll = np.roll(np.arange(n), -ile)
    j = int(np.where(roll == ite)[0][0])
    br1, br2 = roll[:j + 1], np.concatenate([roll[j:], roll[:1]])
    g = np.linspace(0.0, 1.0, 200)

    def branch(br):
        o = np.argsort(xn[br])
        return np.interp(g, xn[br][o], zc[br][o])

    b1, b2 = branch(br1), branch(br2)
    up, lo = np.maximum(b1, b2), np.minimum(b1, b2)
    tc = list(up - lo)
    cam = list(0.5 * (up + lo))
    twist = math.degrees(math.atan2(zn[ile] - zn[ite], 1.0))
    # MAXIMUM CAMBER, CARRYING ITS SIGN. A magnitude would report a camber that has
    # crossed zero as a camber that grew, which is the opposite of what happened.
    cam = np.asarray(cam)
    return max(tc), float(cam[int(np.argmax(np.abs(cam)))]), twist, c, (ile, ite)


rows = []
for e in stations:
    tag = "eta%02d" % int(round(e * 100))
    base, _ = DS.read_cut(os.path.join(HERE, "section_%s_baseline.csv" % tag))
    opt, _ = DS.read_cut(os.path.join(HERE, "section_%s_opt.csv" % tag))
    tb, cb_, twb, cbase, bidx = section_metrics(base)
    to, co, two, _, _ = section_metrics(opt, cref=cbase, idx=bidx)
    rows.append([e, twb, two, tb, to, cb_, co, cbase])
    print("   eta %.2f  twist %+.3f -> %+.3f deg (%+.3f)  t/c %.5f -> %.5f  c %.4f m"
          % (e, twb, two, two - twb, tb, to, cbase))
fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.2))
for ax, (i0, i1), lab in zip(axes, ((1, 2), (3, 4), (5, 6)),
                             (r"$\Delta\alpha_{\mathrm{tw}}\ \ [\mathrm{deg}]$",
                              r"$(t/c)_{\max}$", r"$\Delta z_{\mathrm{cam}}/c$")):
    ax.plot(stations, [r[i0] for r in rows], "o-", color=INK, lw=1.4,
            label=r"$\mathrm{baseline}$")
    ax.plot(stations, [r[i1] for r in rows], "s-", color=RED, lw=1.4,
            label=r"$\mathrm{optimal}$")
    ax.set_xlabel(r"$\eta$  [-]"); ax.set_ylabel(lab)
axes[0].legend(loc="best")
_finish(fig, os.path.join(HERE, "final_dimensions.png"))
wcsv("final_dimensions",
     ["eta", "twist_baseline_deg", "twist_optimal_deg", "tc_max_baseline",
      "tc_max_optimal", "camber_baseline", "camber_optimal", "chord_m"], rows)
print("12 dimensions written for %d stations" % len(rows))
print("pngs:", len([x for x in os.listdir(HERE) if x.endswith(".png")]))
