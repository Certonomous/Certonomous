#!/usr/bin/env python3
"""Build the K2 TRANSIENT demo plot folder from REAL series and fields on disk.

    python3 docs/campaigns/F14-cooling-ladder/demo/plots_K2_transient/build_plots.py

Zero solver compute. ROUND 4 (Sanaa's plot order, 2026-09-14): the transient set is
K2bU3R3_D59 -- the 137,000-cell four-rack room, 80 s record -- and every window mean
on it is taken over the window 50 -> 80 s. The two K2h figures named in the order,
`k2t_dp_history.png` and its arrays, are NOT redrawn here; their provenance rows are
still emitted so the folder's TSV stays complete. See `REDRAW_DP`.

Sources, each named in SIDECAR.md and in PROVENANCE.tsv:
  * K2b_runs/K2bU3R3_D59 -- the 3-D four-rack room (GATE REACHED): the solver log,
    the per-rack inlet temperature series, and the written fields at 60 and 80 s.
  * K2h_runs/K2h_L3 -- the graded transient fine level (PASS): the module dp record,
    and NOTHING ELSE. Round 4b (Sanaa, 2026-09-14: "yes anything transient on
    K2bU3R3") moved the operator indices onto K2bU3R3 as well, through the
    definitions frozen in make_k2t_indices.py, which are cited and unchanged.

No verdict stamp, no band annotation and no English is drawn on any image (plot
library v2; owner correction 2026-09-13 and the order of 2026-09-14).
"""
import csv
import hashlib
import os
import re
import sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo/plots_K2_transient")
F14 = os.path.join(REPO, "verification/runs/F14-cooling-ladder")
sys.path.insert(0, os.path.join(REPO, "sdk"))
sys.path.insert(0, HERE)
from workflows.act_plots_lib import (force_history, vertical_profiles, _plt, _finish,
                                     _legend, sym, PALETTE, RED, INK, INK2)
import k2t_window as W

D59 = W.CASE
K = W.K

#: The two limit lines of the ride-through, LABELLED WITH THEIR OWN VALUES. The
#: supply line is drawn at the run's ACTUAL supply temperature, 289.0 K = 15.85 degC
#: (build_k2b.T_SUP), not at the 16 degC of the order's shorthand: a line labelled
#: with a number the case does not carry is a false reading of the case.
LIM = {r"$T_{\lim}=27\,^{\circ}\mathrm{C}$": 27.0,
       r"$T_{\mathrm{sup}}=15.85\,^{\circ}\mathrm{C}$": W.T_SUP - K}

#: `k2t_dp_history.png` is K2h and the order says it stands as pushed. Its figure is
#: NOT rewritten; flip this to True only to rebuild it deliberately.
REDRAW_DP = False

prov = []


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def note(fig, run, path, tdir, window="", patches="", camera="", crange=""):
    prov.append((fig, run, path, tdir, window, patches, camera, crange, sha(path)))


def wcsv(stem, header, rows, extra=()):
    with open(os.path.join(HERE, stem + ".csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
        for r in extra:
            w.writerow(r)


def series(path):
    t, v = [], []
    for ln in open(path):
        if ln.startswith("#"):
            continue
        p = ln.split()
        if len(p) >= 2:
            t.append(float(p[0])); v.append(float(p[1]))
    return t, v


def resample(t, v, grid):
    out, j = [], 0
    for g in grid:
        while j + 1 < len(t) and t[j + 1] <= g:
            j += 1
        out.append(v[j])
    return out


# ---------------------------------------------------------------- local drawers
# The three shapes the order asks for that the shared library has no mode for. They
# are written HERE rather than added to `sdk/workflows/act_plots_lib.py` because the
# library is shared with plotting lanes committing in other campaigns at this moment
# and this commit touches two folders only. Style, palette and the symbol mapper are
# the library's own, imported above, so the look is identical.
def residual_history_t(out, t, series_map, *, xlabel=r"$t\ \ [\mathrm{s}]$"):
    """The library's residual_history, with TIME on the abscissa instead of $n$."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.set_xlabel(xlabel); ax.set_ylabel(r"$r$"); ax.set_yscale("log")
    for (name, vals), c in zip(series_map.items(), PALETTE):
        ax.plot(t, vals, color=c, lw=1.1, label=name)
    _legend(ax, loc="upper right", ncol=3)
    return _finish(fig, out)


def grouped_bars(out, labels, groups, *, ylabel, lines=None):
    """Grouped bars per rack with any number of labelled horizontal lines.

    `metric_bars` in the library draws one limit line only; the indices figure needs
    the RTI line AND the 100 % line, and the balance figure needs its own line at a
    value that is not a limit.
    """
    import numpy as np
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    names = list(groups)
    x = np.arange(len(labels), dtype=float)
    w = 0.8 / max(len(names), 1)
    for i, n in enumerate(names):
        ax.bar(x + (i - (len(names) - 1) / 2) * w, groups[n], w,
               label=sym(n, with_unit=False) or n, color=PALETTE[i % len(PALETTE)])
    for j, (lab, val) in enumerate((lines or {}).items()):
        ax.axhline(val, color=(RED if j == 0 else INK), lw=1.2,
                   ls="--" if j == 0 else ":", label=lab)
    ax.set_xticks(x)
    ax.set_xticklabels([sym(l, with_unit=False) or l for l in labels])
    ax.set_ylabel(ylabel)
    ax.axhline(0.0, color=INK2, lw=0.8)
    _legend(ax, loc="lower center", bbox_to_anchor=(0.5, 1.0),
            ncol=len(names) + len(lines or {}))
    return _finish(fig, out)


# ================================================================= the control
W.plant_check()
case = W.Case()

# ------------------------------------------------------------------ 1. residuals
LOG = os.path.join(D59, "log.buoyantBoussinesqPimpleFoam")
RX_T = re.compile(r"^Time = ([0-9.eE+-]+)\s*$")
RX_R = re.compile(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)")
WANT = ["Ux", "Uy", "Uz", "T", "p_rgh"]
times, rows, cur = [], [], None
for ln in open(LOG, errors="replace"):
    m = RX_T.match(ln.strip())
    if m:
        if cur is not None and all(k in cur for k in WANT):
            times.append(tnow); rows.append([cur[k] for k in WANT])
        tnow = float(m.group(1)); cur = {}
        continue
    if cur is None:
        continue
    m = RX_R.search(ln)
    if m and m.group(1) in WANT and m.group(1) not in cur:
        cur[m.group(1)] = float(m.group(2))     # FIRST outer corrector of the step
if cur is not None and all(k in cur for k in WANT):
    times.append(tnow); rows.append([cur[k] for k in WANT])
if len(times) < 100:
    sys.exit("REFUSE (exit 2): only %d residual steps parsed from %s" % (len(times), LOG))
SYMS = {"Ux": r"$r_{U_x}$", "Uy": r"$r_{U_y}$", "Uz": r"$r_{U_z}$",
        "T": r"$r_{T}$", "p_rgh": r"$r_{p_{\mathrm{rgh}}}$"}
residual_history_t(os.path.join(HERE, "k2t_residuals.png"), times,
                   {SYMS[k]: [r[i] for r in rows] for i, k in enumerate(WANT)})
wcsv("k2t_residuals", ["time_s"] + WANT, [[times[i]] + rows[i] for i in range(len(times))])
note("k2t_residuals.png", "K2bU3R3_D59", LOG, "log", "0 to 80 s (whole record)",
     "-", "-", "-")

# ------------------------------------------------------------------ 2. ride-through
ser, tref = {}, None
for i in range(4):
    p = os.path.join(D59, "postProcessing/T_rack%d_in_mdot/0/surfaceFieldValue.dat" % i)
    t, v = series(p)
    note("k2t_ride_through.png", "K2bU3R3_D59", p, "0", "0 to 80 s (whole record)",
         "rack%d_in" % i, "-", "-")
    if tref is None:
        tref = t
    ser["rack %d" % (i + 1)] = [x - K for x in (v if t == tref else resample(t, v, tref))]
force_history(os.path.join(HERE, "k2t_ride_through.png"), tref, series=ser,
              xlabel="time  [s]", ylabel="inlet temperature  [°C]", limits=LIM)
wcsv("k2t_ride_through", ["time_s"] + list(ser),
     [[tref[i]] + [ser[k][i] for k in ser] for i in range(len(tref))])

# ------------------------------------------------------------------ 3. K2h module dp
DP = os.path.join(F14, "K2h_runs/K2h_L3/postProcessing")
tt, vv = [], []
for d in sorted(os.listdir(os.path.join(DP, "dp_tile")), key=float):
    p = os.path.join(DP, "dp_tile", d, "surfaceFieldValue.dat")
    a, b = series(p)
    note("k2t_dp_history.png", "K2h_L3", p, d, "42 to 112 s (registered)",
         "tile, return", "-", "-")
    for x, y in zip(a, b):
        while tt and x <= tt[-1]:
            tt.pop(); vv.pop()
        tt.append(x); vv.append(y)
if REDRAW_DP:
    force_history(os.path.join(HERE, "k2t_dp_history.png"), tt,
                  series={"module Δp": vv}, window=(42.0, 112.0),
                  xlabel="time  [s]", ylabel="module Δp  [m²/s²]")
    wcsv("k2t_dp_history", ["time_s", "DP_module_m2_s2"], list(zip(tt, vv)))

# ------------------------------------------------------------------ 4. inlet profiles
profs = W.inlet_profiles(case)
vertical_profiles(os.path.join(HERE, "k2t_inlet_profiles.png"),
                  profiles=[{"z": z, "T": p, "label": "rack %d" % (i + 1)}
                            for i, (z, p, _) in enumerate(profs)],
                  limits={"limit": 27.0})
zs = profs[0][0]
wcsv("k2t_inlet_profiles", ["z_m"] + ["rack%d_T_degC" % (i + 1) for i in range(4)],
     [[zs[j]] + [profs[i][1][j] for i in range(4)] for j in range(len(zs))])
for t in W.WINDOW_TIMES:
    for i in range(4):
        note("k2t_inlet_profiles.png", "K2bU3R3_D59", os.path.join(D59, t, "T"), t,
             "50 to 80 s: mean of written times 60, 80", "rack%d_in" % i, "-", "-")

# ------------------------------------------------------------------ 5. indices
# ROUND 4b, Sanaa 2026-09-14: "yes anything transient on K2bU3R3". The operator
# indices are RECOMPUTED ON K2bU3R3_D59 over the same 50 -> 80 s window as every
# other window mean in this folder. THE DEFINITIONS ARE NOT TOUCHED: `k2t_window.indices`
# evaluates the ones already frozen in this folder's `make_k2t_indices.py` -- area
# averages on each patch (lines 19-20), rec/cap (line 24), RCI high (line 25), the
# mean rack rise and RTI (lines 27-28), hottest inlet and spread (line 29) -- and
# cites them line by line. Only the case they are evaluated on has changed.
idx_rows, room = W.indices(case)
wcsv("k2t_indices", ["rack", "T_inlet_degC", "T_outlet_degC", "RCI_high_pct",
                     "capture_index_pct", "recirculation_pct", "dT_rack_K"], idx_rows)
wcsv("k2t_indices_room",
     ["T_supply_degC", "T_return_degC", "room_rise_K", "RTI_pct",
      "hottest_inlet_degC", "hottest_rack", "spread_K", "dT_mean_K"],
     [[room["T_supply_degC"], room["T_return_degC"], room["room_rise_K"],
       room["RTI_pct"], room["hottest_inlet_degC"], room["hottest_rack"],
       room["spread_K"], room["dT_mean_K"]]])
rti = room["RTI_pct"]
grouped_bars(os.path.join(HERE, "k2t_indices.png"),
             [r[0] for r in idx_rows],
             {"RCI": [r[3] for r in idx_rows],
              "capture": [r[4] for r in idx_rows],
              "recirculation": [r[5] for r in idx_rows]},
             ylabel=r"$[\%]$",
             lines={r"$\mathrm{RTI}=%.2f\,\%%$" % rti: rti, r"$100\,\%$": 100.0})
for t in W.WINDOW_TIMES:
    note("k2t_indices.png", "K2bU3R3_D59", os.path.join(D59, t, "T"), t,
         "50 to 80 s: mean of written times 60, 80",
         "tile, return, rack0..3_in, rack0..3_out", "-", "-")

# ------------------------------------------------------------------ 6. rack dT
temps = W.rack_temperatures(case)
dts = [o - i for i, o, _ in temps]
grouped_bars(os.path.join(HERE, "k2t_rack_dT.png"),
             ["rack %d" % (i + 1) for i in range(4)],
             {r"$\Delta T_{\mathrm{rack}}$": dts},
             ylabel=r"$\Delta T_{\mathrm{rack}}\ \ [\mathrm{K}]$",
             lines={r"$\Delta T^{\,\mathrm{spec}}=12\,\mathrm{K}$": W.DT_RACK})
wcsv("k2t_rack_dT", ["rack", "T_inlet_degC", "T_outlet_degC", "dT_rack_K",
                     "dT_spec_K", "rack_power_W_at_0.35_m3_s"],
     [["rack %d" % (i + 1), temps[i][0] - K, temps[i][1] - K, dts[i], W.DT_RACK,
       W.P_RACK_W] for i in range(4)])
for t in W.WINDOW_TIMES:
    note("k2t_rack_dT.png", "K2bU3R3_D59", os.path.join(D59, t, "T"), t,
         "50 to 80 s: mean of written times 60, 80",
         "rack0..3_in, rack0..3_out", "-", "-")

# ------------------------------------------------------------------ 7. airflow balance
tot_tile, per_tile, _ = W.tile_flow(case)
demand = W.rack_flows(case)
bypass = [per_tile[i] - demand[i] for i in range(4)]
shi, rhi = W.shi_rhi(case)
grouped_bars(os.path.join(HERE, "k2t_airflow_balance.png"),
             ["rack %d" % (i + 1) for i in range(4)],
             {r"$\dot V_{\mathrm{tile}}$": per_tile,
              r"$\dot V_{\mathrm{rack}}$": demand,
              r"$\dot V_{\mathrm{byp}}$": bypass},
             ylabel=r"$\dot V\ \ [\mathrm{m^3\,s^{-1}}]$",
             lines={r"$\dot V_{\mathrm{tile}}=0.245\ \mathrm{m^3\,s^{-1}}$": W.QV_TILE})
wcsv("k2t_airflow_balance",
     ["row", "tile_supply_m3_s", "rack_demand_m3_s", "bypass_m3_s"],
     [["rack %d" % (i + 1), per_tile[i], demand[i], bypass[i]] for i in range(4)],
     extra=[[], ["# bypass = tile supply - rack demand; NEGATIVE is the deficit the "
                 "rack makes up from recirculated room air"],
            ["SHI", shi, "", ""], ["RHI", rhi, "", ""]])
for t in W.WINDOW_TIMES:
    note("k2t_airflow_balance.png", "K2bU3R3_D59", os.path.join(D59, t, "phi"), t,
         "50 to 80 s: mean of written times 60, 80",
         "tile, rack0..3_in", "-", "-")

# ------------------------------------------------------------------ provenance
# The matplotlib half. `render_k2t_panels.py` runs AFTER this script and REWRITES
# this file keeping every row it did not draw, so the order of the two runs is
# build_plots.py first, the renderer second.
with open(os.path.join(HERE, "PROVENANCE.tsv"), "w") as f:
    f.write("figure\trun\tartifact\ttime_dir\twindow\tpatches\tcamera\tcolour_range\tsha256\n")
    for r in prov:
        f.write("\t".join(str(x) for x in r) + "\n")

# ------------------------------------------------------------------ THE TWO CHECKS
tsup, tret = W.supply_return(case)
print("")
print("THE TWO CHECKS, on K2bU3R3_D59, window 50 to 80 s = mean of written times "
      "%s (%d averaged)" % (", ".join(W.WINDOW_TIMES), len(W.WINDOW_TIMES)))
print("  window-mean room rise   %.4f K    (flux-weighted T_return %.4f K minus "
      "area-weighted T_supply %.4f K on `tile`)" % (tret - tsup, tret, tsup))
print("  total tile flow         %.6f m3/s (sum |phi| over the 400 `tile` faces; "
      "per rack %s)" % (tot_tile, ", ".join("%.4f" % p for p in per_tile)))
print("  SHI %.5f   RHI %.5f" % (shi, rhi))
print("  indices ON K2bU3R3 (area averages, make_k2t_indices definitions):")
for r in idx_rows:
    print("    %s  T_in %.4f degC  T_out %.4f degC  RCI %.2f %%  CI %.2f %%  "
          "rec %.2f %%  dT %.4f K" % (r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
print("    room  T_sup %.4f degC  T_ret %.4f degC (area)  RTI %.3f %%  spread %.4f K"
      % (room["T_supply_degC"], room["T_return_degC"], room["RTI_pct"], room["spread_K"]))
print("  rack dT  %s K" % ", ".join("%.4f" % d for d in dts))
print("  residual steps parsed %d, t %.4f -> %.4f s" % (len(times), times[0], times[-1]))
print("  pngs:", sorted(x for x in os.listdir(HERE) if x.endswith(".png")))
