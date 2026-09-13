#!/usr/bin/env python3
"""Build the SUBOFF drift-sweep demo plot folder from what is on disk NOW.

Zero solver compute. ALL SEVEN SWEEP POINTS WERE STILL RUNNING when this was
written and nothing is written into any run tree.

Normalisation and sign convention are transcribed from
`verification/campaign/SUBOFF_A1h_FULL_DOMAIN_DRIFT_SWEEP_PREREGISTRATION.md` §4.1,
which derives them in full and registers them before compute:

    Y' = - F_z,mesh / 101.500341        (= 1/2 rho U^2 L_BP^2, rho = 1 kinematic)
    N' = - M_y,mesh / 432.478763        (= 1/2 rho U^2 L_BP^3)
    v' = sin(beta)

THE GRADED CHANNEL IS THE HORIZONTAL PLANE, Y' AND N' -- NOT "Z and M". A vertical
plane result is A1g's, on a different body, and §9 of the registration says this act
produces no Z, no M and no neutral point.

The Roddy numbers drawn here are HIS EXPERIMENTAL MEASUREMENTS read out of a printed
table, never anything this lab computed: Y_v' = -0.023008, GATED at +-4 % on
[-0.023928, -0.022088]; N_v' = -0.015534, REPORTED AND NOT GRADED.

No verdict word and no band annotation is drawn on any image.
"""
import csv, hashlib, json, math, os, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.join(REPO, "docs/campaigns/navier_class/SUBOFF/demo/plots_SUBOFF")
SWEEP = os.path.join(REPO, "verification/runs/navier_class/SUBOFF_A1H_DRIFT/L1M_SWEEP")
L2 = os.path.join(REPO, "verification/runs/navier_class/SUBOFF_A1/SOLVE_L2")
sys.path.insert(0, os.path.join(REPO, "sdk"))
from workflows.act_plots_lib import force_history, sweep_curve
from workflows.act_residual_frames import residual_frames

NORM_Y = 101.500341          # prereg s.4, 1/2 rho U^2 L_BP^2
NORM_N = 432.478763          # prereg s.4, 1/2 rho U^2 L_BP^3
YV_RODDY = -0.023008         # prereg s.5, Roddy 1990 Table 4, B.H. + Sail
NV_RODDY = -0.015534         # prereg s.5, REPORTED, NOT GRADED
YV_BAND = (-0.023928, -0.022088)      # prereg s.5, the registered +-4 % gate
NV_BAND = (NV_RODDY * 1.04, NV_RODDY * 0.96)   # the same +-4 %, NOT a gate
ENDTIME = 3000
TAIL = 300                   # the window the preliminary means are taken over
POINTS = [("m12", -12.0), ("m08", -8.0), ("m04", -4.0), ("p00", 0.0),
          ("p04", 4.0), ("p08", 8.0), ("p12", 12.0)]

prov = []


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def note(fig, path, tdir):
    prov.append((fig, path, tdir, sha(path)))


def wcsv(stem, header, rows):
    with open(os.path.join(HERE, stem + ".csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


def read_total(path, comp):
    """Time and one `total_*` component of an OpenFOAM force/moment file."""
    t, v = [], []
    for ln in open(path):
        if ln.startswith("#"):
            continue
        c = ln.replace("(", " ").replace(")", " ").split()
        if len(c) >= 4:
            t.append(float(c[0])); v.append(float(c[comp]))
    return t, v


# ------------------------------------------------------------------ read the sweep
series_y, series_n, table = {}, {}, []
for tag, beta in POINTS:
    fp = os.path.join(SWEEP, "BETA_%s" % tag, "postProcessing/forces/0/force.dat")
    mp = os.path.join(SWEEP, "BETA_%s" % tag, "postProcessing/forces/0/moment.dat")
    t, fz = read_total(fp, 3)                 # total_z
    tm, my = read_total(mp, 2)                # total_y
    n = min(len(t), len(tm))
    lab = "β = %+.0f°" % beta
    series_y[lab] = [-x / NORM_Y for x in fz[:n]]
    series_n[lab] = [-x / NORM_N for x in my[:n]]
    note("suboff_yprime_history.png", fp, str(int(t[-1])))
    note("suboff_nprime_history.png", mp, str(int(tm[-1])))
    ytail = series_y[lab][-TAIL:]
    ntail = series_n[lab][-TAIL:]
    table.append([tag, beta, math.sin(math.radians(beta)), int(t[n - 1]),
                  sum(ytail) / len(ytail), sum(ntail) / len(ntail), len(ytail)])
    if tag == "p00":
        it_ref = t[:n]

# the seven points have run to slightly different iterations; plot each on its own
its = {}
for tag, beta in POINTS:
    fp = os.path.join(SWEEP, "BETA_%s" % tag, "postProcessing/forces/0/force.dat")
    t, _ = read_total(fp, 3)
    its["β = %+.0f°" % beta] = t

nmin = min(len(v) for v in series_y.values())
common = list(range(1, nmin + 1))
force_history(os.path.join(HERE, "suboff_yprime_history.png"), common,
              series={k: series_y[k][:nmin] for k, _ in
                      ((("β = %+.0f°" % b), None) for _, b in POINTS)},
              xlabel="iteration", ylabel="$Y'$  [–]",
              title="Side-force coefficient, run in progress")
force_history(os.path.join(HERE, "suboff_nprime_history.png"), common,
              series={k: series_n[k][:nmin] for k, _ in
                      ((("β = %+.0f°" % b), None) for _, b in POINTS)},
              xlabel="iteration", ylabel="$N'$  [–]",
              title="Yaw-moment coefficient, run in progress")
wcsv("suboff_histories", ["iteration"] + ["Y'(%+.0f)" % b for _, b in POINTS]
     + ["N'(%+.0f)" % b for _, b in POINTS],
     [[i + 1] + [series_y["β = %+.0f°" % b][i] for _, b in POINTS]
      + [series_n["β = %+.0f°" % b][i] for _, b in POINTS] for i in range(nmin)])

# ------------------------------------------------------------------ Y' and N' vs beta
betas = [b for _, b in POINTS]
ylab = [r[4] for r in table]
nlab = [r[5] for r in table]
roddy_y = [YV_RODDY * math.sin(math.radians(b)) for b in betas]
band_y = [abs((YV_BAND[1] - YV_BAND[0]) / 2.0 * math.sin(math.radians(b))) for b in betas]
roddy_n = [NV_RODDY * math.sin(math.radians(b)) for b in betas]
band_n = [abs((NV_BAND[1] - NV_BAND[0]) / 2.0 * math.sin(math.radians(b))) for b in betas]

sweep_curve(os.path.join(HERE, "suboff_yprime_vs_beta.png"), betas,
            series={"Roddy 1990, gated ±4 %": {"y": roddy_y, "band": band_y},
                    "lab, preliminary": {"y": ylab, "band": None}},
            xlabel="drift angle  β  [deg]", ylabel="$Y'$  [–]",
            title="Side force against drift angle")
sweep_curve(os.path.join(HERE, "suboff_nprime_vs_beta.png"), betas,
            series={"Roddy 1990, reported not graded": {"y": roddy_n, "band": band_n},
                    "lab, preliminary": {"y": nlab, "band": None}},
            xlabel="drift angle  β  [deg]", ylabel="$N'$  [–]",
            title="Yaw moment against drift angle")
wcsv("suboff_vs_beta",
     ["point", "beta_deg", "v_prime", "iterations_so_far", "Y_prime_mean",
      "N_prime_mean", "window_iterations", "Roddy_Y_prime", "Roddy_N_prime"],
     [r + [ry, rn] for r, ry, rn in zip(table, roddy_y, roddy_n)])

# ------------------------------------------------------------------ the L2 corner
lp = os.path.join(L2, "postProcessing/forceCoeffs")
dirs = sorted(os.listdir(lp), key=float)
it, cd = [], []
for d in dirs:
    f = [x for x in os.listdir(os.path.join(lp, d)) if x.endswith(".dat")][0]
    p = os.path.join(lp, d, f)
    hdr = None
    for ln in open(p):
        if ln.startswith("#"):
            if "Time" in ln or "Cd" in ln:
                hdr = ln.lstrip("#").split()
            continue
        c = ln.split()
        if hdr and len(c) == len(hdr) and "Cd" in hdr:
            t = float(c[hdr.index("Time")])
            while it and t <= it[-1]:
                it.pop(); cd.pop()
            it.append(t); cd.append(float(c[hdr.index("Cd")]))
    note("suboff_l2_corner.png", p, d)
force_history(os.path.join(HERE, "suboff_l2_corner.png"), it, series={"$C_D$": cd},
              xlabel="iteration", ylabel="$C_D$  [–]",
              title="L2 zero-incidence corner, drag history")
wcsv("suboff_l2_corner", ["iteration", "Cd"], list(zip(it, cd)))

# ------------------------------------------------------------------ residual frames
# ONE point carries the frame series -- the most advanced -- and every point's final
# frame is written beside it, so the act can step through the evolution and still
# show that all seven are descending together.
def read_residuals(case):
    p = os.path.join(case, "postProcessing/residuals/0/solverInfo.dat")
    hdr, rows = None, []
    for ln in open(p):
        if ln.startswith("#"):
            if "Time" in ln:
                hdr = ln.lstrip("#").split()
            continue
        c = ln.split()
        if hdr and len(c) == len(hdr):
            rows.append(c)
    want = [k for k in ("Ux_initial", "Uy_initial", "Uz_initial", "p_initial",
                        "k_initial", "omega_initial") if k in hdr]
    lab = {"Ux_initial": "$U_x$", "Uy_initial": "$U_y$", "Uz_initial": "$U_z$",
           "p_initial": "$p$", "k_initial": "$k$", "omega_initial": r"$\omega$"}
    it = [float(r[hdr.index("Time")]) for r in rows]
    return p, it, {lab[k]: [float(r[hdr.index(k)]) for r in rows] for k in want}

lead = max(table, key=lambda r: r[3])[0]
rp, rit, rser = read_residuals(os.path.join(SWEEP, "BETA_%s" % lead))
for _f, _pp, _n in residual_frames(HERE, "suboff_residuals", rit, rser, target=1e-5,
                                   final_name="suboff_residuals.png"):
    note(os.path.basename(_pp), rp, str(int(_n)))
print("residual frames from the most advanced point BETA_%s, %d iterations"
      % (lead, int(rit[-1])))

with open(os.path.join(HERE, "PROVENANCE.tsv"), "w") as f:
    f.write("figure\tartifact\ttime_dir\tsha256\n")
    for r in prov:
        f.write("\t".join(str(x) for x in r) + "\n")
print("sweep progress of %d:" % ENDTIME,
      {r[0]: r[3] for r in table})
print("preliminary means over the last %d iterations:" % TAIL)
for r in table:
    print("  beta %+5.1f  v' %+8.5f  Y' %+12.8f  N' %+12.8f" % (r[1], r[2], r[4], r[5]))
print("L2 corner: %d rows, last Cd %.8f" % (len(it), cd[-1]))
print("pngs:", sorted(x for x in os.listdir(HERE) if x.endswith(".png")))
