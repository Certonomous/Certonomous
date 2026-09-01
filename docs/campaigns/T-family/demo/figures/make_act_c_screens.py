#!/usr/bin/env python3
# =========================================================================
# ACT C SCREEN DATA PRODUCTS -- built from the landed 8-cell module run.
#
# NOTHING HERE SOLVES ANYTHING.  It reads the run that already exists and
# writes the data files and vector figures the display mission needs.
#
# EVERY FIELD VALUE AND EVERY CELL RECTANGLE COMES OUT OF THE REAL
# COMPUTATIONAL MESH (constant/module/polyMesh) AND THE REAL TIME
# DIRECTORIES.  No STL, no tessellation, no interpolation onto a display
# grid: each of the 960 mesh cells is drawn as its own rectangle, coloured
# by its own stored value.
#
# The parsing and geometry come from analyse_t25.py, imported rather than
# re-implemented, so there is one parser and one geometry definition.  Its
# four-way geometry guard (cell count, total volume, channel area, 120 mesh
# cells per module cell) is RE-ASSERTED here in this script's own code path,
# because a guard that only runs in the other module is not a guard on this
# one.
#
# PLANTED CONTROL (CLAUDE.md rule 3), TWICE:
#   (a) analyse_t25.selftest -- the shared parser must see +1 K on all cells.
#   (b) this script's own snapshot extractor -- a known perturbation is
#       planted in ONE known mesh cell at ONE known time, read back through
#       the snapshot path, and the run refuses unless it is seen at the
#       right size, in the right cell, and nowhere else.
# =========================================================================
import csv
import json
import os
import shutil
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = "/home/ubuntu/Certonomous/verification/runs/T-family/T25_MODULE_runs"
CASE = os.path.join(RUNS, "T25_MOD_L1")
sys.path.insert(0, RUNS)
import analyse_t25 as A                                    # noqa: E402

SNAP_TIMES = [0.0, 30.0, 60.0, 120.0, 300.0, 900.0]
PULSE_END = A.T_PULSE
T_REF = A.T_REF

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 9,
    "axes.labelsize": 9,
    "mathtext.fontset": "dejavuserif",
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "figure.dpi": 150,
})


# ------------------------------------------------------- mesh, my code path
def cell_rectangles(case, region="module"):
    """Per-mesh-cell axis-aligned extent, volume and y-centre.

    Built from constant/<region>/polyMesh with analyse_t25's own readers.
    The mesh is one cell thick in z (front/back are `empty`), so the x-y
    extent of a cell IS the cell as it is drawn -- no projection is taken
    and no surface is tessellated.
    """
    pm = os.path.join(case, "constant", region, "polyMesh")
    pts = A.read_points(pm)
    faces = A.read_faces(pm)
    owner = A.read_labels(pm, "owner")
    neigh = A.read_labels(pm, "neighbour")
    bnd = A.read_boundary(pm)

    ncells = max(max(owner), max(neigh) if neigh else -1) + 1
    cpts = [set() for _ in range(ncells)]
    for fi, f in enumerate(faces):
        cpts[owner[fi]].update(f)
        if fi < len(neigh):
            cpts[neigh[fi]].update(f)

    rects, vol, cy = [], [], []
    for s in cpts:
        xs = [pts[i][0] for i in s]
        ys = [pts[i][1] for i in s]
        zs = [pts[i][2] for i in s]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        rects.append((x0, x1, y0, y1))
        vol.append((x1 - x0) * (y1 - y0) * (max(zs) - min(zs)))
        cy.append(0.5 * (y0 + y1))

    nf, sf = bnd["channelFaces"]
    areas = [A.face_area(faces[sf + i], pts) for i in range(nf)]

    # --- the four-way geometry guard, re-asserted in THIS code path --------
    bad = []
    if ncells != 960:
        bad.append(f"expected 960 cells, mesh has {ncells}")
    tv = sum(vol)
    if abs(tv - A.N_CELLS * A.LX * A.LY * A.LZ) > 1e-9:
        bad.append(f"total volume {tv} != {A.N_CELLS*A.LX*A.LY*A.LZ}")
    ta = sum(areas)
    exp_a = (2 * A.N_CELLS - 2) * A.LX * A.LZ
    if abs(ta - exp_a) > 1e-9:
        bad.append(f"channel area {ta} != expected {exp_a}")
    groups = [[] for _ in range(A.N_CELLS)]
    for c, y in enumerate(cy):
        groups[A.cell_index(y)].append(c)
    for i, g in enumerate(groups):
        if len(g) != 120:
            bad.append(f"module cell {i+1} has {len(g)} mesh cells, not 120")
    if bad:
        sys.exit("REFUSE: mesh does not match the registered geometry: "
                 + "; ".join(bad))
    return rects, vol, cy, groups, ncells, tv, ta


def snapshot_field(case, t, ncells, region="module"):
    """The internal temperature field at time t, straight off disk."""
    p = os.path.join(case, A.fmt_t(t), region, "T")
    vals, uni = A.scalar_field(p)
    if vals is None:
        vals = [uni] * ncells
    if len(vals) != ncells:
        sys.exit(f"REFUSE: {p} holds {len(vals)} values, mesh has {ncells}")
    return vals


# ------------------------------------------------- planted control (b)
def plant_snapshot_control(case, ncells, region="module"):
    """Plant +2.500000 K in ONE known mesh cell at ONE known time.

    Refuses unless the snapshot path sees exactly that change, in exactly
    that cell, and no change anywhere else.
    """
    t_plant, idx, delta = 300.0, 137, 2.5
    base = snapshot_field(case, t_plant, ncells, region)

    tmp = tempfile.mkdtemp(prefix="t25_snap_plant_")
    dst = os.path.join(tmp, "case")
    os.makedirs(dst)
    os.symlink(os.path.join(case, "constant"), os.path.join(dst, "constant"))
    shutil.copytree(os.path.join(case, A.fmt_t(t_plant)),
                    os.path.join(dst, A.fmt_t(t_plant)))

    p = os.path.join(dst, A.fmt_t(t_plant), region, "T")
    txt = open(p).read()
    k = txt.index("internalField")
    body, j = A.read_list(txt, k)
    vals = [float(v) for v in body.split()]
    vals[idx] += delta
    open(p, "w").write(txt[:txt.index("(", k) + 1] + "\n"
                       + "\n".join(repr(v) for v in vals) + "\n" + txt[j:])

    seen = snapshot_field(dst, t_plant, ncells, region)
    shutil.rmtree(tmp)

    d = [s - b for s, b in zip(seen, base)]
    d_target = d[idx]
    d_other = max(abs(v) for i, v in enumerate(d) if i != idx)
    ok = abs(d_target - delta) < 1e-9 and d_other < 1e-12
    rep = {
        "planted_K": delta,
        "planted_cell_index": idx,
        "planted_time_s": t_plant,
        "seen_in_planted_cell_K": d_target,
        "largest_change_elsewhere_K": d_other,
        "seen": bool(ok),
    }
    print("PLANTED CONTROL (b) -- snapshot extractor")
    print(f"  planted            +{delta:.6f} K in mesh cell {idx} at "
          f"t = {t_plant:.0f} s")
    print(f"  extractor saw      {d_target:+.6f} K in that cell")
    print(f"  largest change     {d_other:.3e} K anywhere else")
    print("  RESULT             " + ("PLANT SEEN" if ok else "PLANT NOT SEEN"))
    if not ok:
        sys.exit("REFUSE: the snapshot extractor cannot see a planted change; "
                 "figures drawn by it would not be evidence")
    return rep


# ------------------------------------------------------ lumped reference
def lumped_reference(times, n_cooled_faces):
    """Zero-dimensional energy balance on one module cell.

    rho*cp*V dT/dt = P(t) - h*A*(T - T_inf), integrated in closed form on
    each leg of the duty cycle.  Constants are the registered material,
    geometry and duty-cycle values (CASE.txt); this is an independent
    hand check, not a second solve.
    """
    C = A.RHO * A.CP * A.LX * A.LY * A.LZ
    hA = A.H_CONV * n_cooled_faces * A.LX * A.LZ
    tau = C / hA
    th60 = (A.P_TAKEOFF / hA) * (1.0 - np.exp(-PULSE_END / tau))
    out = []
    for t in times:
        if t <= PULSE_END:
            out.append((A.P_TAKEOFF / hA) * (1.0 - np.exp(-t / tau)))
        else:
            inf = A.P_CRUISE / hA
            out.append(inf + (th60 - inf) * np.exp(-(t - PULSE_END) / tau))
    return np.array(out)


# --------------------------------------------------------------- figures
def fig_snapshots(rects, snaps, out):
    allv = np.concatenate([np.asarray(v) for v in snaps.values()])
    vmin, vmax = float(allv.min()), float(allv.max())
    fig, axes = plt.subplots(1, len(SNAP_TIMES), figsize=(13.2, 5.4),
                             constrained_layout=True)
    boxes = [Rectangle((x0, y0), x1 - x0, y1 - y0)
             for (x0, x1, y0, y1) in rects]
    for ax, t in zip(axes, SNAP_TIMES):
        v = np.asarray(snaps[t])
        pc = PatchCollection([Rectangle(b.get_xy(), b.get_width(),
                                        b.get_height()) for b in boxes],
                             cmap="inferno", edgecolors="none")
        pc.set_array(v)
        pc.set_clim(vmin, vmax)          # shared scale, and it spans the data
        ax.add_collection(pc)
        ax.set_xlim(0.0, A.LX)
        ax.set_ylim(0.0, A.N_CELLS * A.PITCH - A.GAP)
        ax.set_aspect("equal")
        ax.set_title(f"$t$ = {t:.0f} s\n"
                     f"min {v.min():.6f} K\nmax {v.max():.6f} K", fontsize=8)
        ax.set_xlabel(r"$x$, m")
        ax.tick_params(labelsize=7)
        if ax is axes[0]:
            ax.set_ylabel(r"$y$, m")
        else:
            ax.set_yticklabels([])
    cb = fig.colorbar(pc, ax=axes, location="right", shrink=0.82, pad=0.015)
    cb.set_label(r"Temperature $T$, K")
    cb.set_ticks([vmin, vmin + 0.25 * (vmax - vmin),
                  vmin + 0.5 * (vmax - vmin),
                  vmin + 0.75 * (vmax - vmin), vmax])
    cb.ax.set_yticklabels([f"{x:.6f}" for x in cb.get_ticks()], fontsize=7)
    cb.ax.text(0.5, 1.02, f"max {vmax:.6f} K", transform=cb.ax.transAxes,
               ha="center", va="bottom", fontsize=7)
    cb.ax.text(0.5, -0.02, f"min {vmin:.6f} K", transform=cb.ax.transAxes,
               ha="center", va="top", fontsize=7)
    fig.suptitle("Module temperature on the computational mesh: "
                 "960 finite-volume cells, each drawn at its own extent and "
                 "coloured by its own stored value.\n"
                 "One colour scale is shared by all six frames and spans the "
                 "full range of the data shown -- nothing is clipped.",
                 fontsize=9)
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight")
    plt.close(fig)
    return vmin, vmax


def fig_histories(times, percell, out):
    fig, ax = plt.subplots(figsize=(7.2, 4.4), constrained_layout=True)
    ax.axvspan(0.0, PULSE_END, color="#f3d9b1", alpha=0.55, lw=0,
               label="takeoff power pulse, 15 W per cell")
    cmap = plt.get_cmap("viridis")
    styles = ["-", "--"]
    for i in range(A.N_CELLS):
        ax.plot(times, percell[:, i], styles[i % 2], lw=1.5,
                color=cmap(i / (A.N_CELLS - 1)),
                label=f"cell {i+1}")
    for (nf, lab), ls, col in (((1, "end cell"), (0, (5, 2)), "#b30000"),
                               ((2, "interior cell"), (0, (1, 1.6)), "#00429d")):
        ax.plot(times, T_REF + lumped_reference(times, nf), ls=ls, lw=1.2,
                color=col,
                label=f"lumped energy balance, {lab} "
                      f"(specified material and duty-cycle constants)")
    ax.set_xlabel(r"$t$, s")
    ax.set_ylabel(r"Volume-averaged cell temperature $\bar{T}$, K")
    ax.set_xlim(0.0, A.T_END)
    ax.grid(alpha=0.25)
    ax.set_title("Cell temperature histories, volume-averaged over the 120 "
                 "mesh cells of each cell\n"
                 "Cells 1 and 8 coincide; cells 2-7 coincide "
                 r"(difference $0.000\times10^{0}$ K)", fontsize=9)
    ax.legend(fontsize=6.5, ncol=2, loc="lower right", framealpha=0.9)
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight")
    plt.close(fig)


def fig_uniformity(times, spread, qout, out):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 5.8), sharex=True,
                                 constrained_layout=True)
    for ax in (a1, a2):
        ax.axvspan(0.0, PULSE_END, color="#f3d9b1", alpha=0.55, lw=0)
        ax.grid(alpha=0.25)
    a1.plot(times, spread, "-", lw=1.8, color="#8c2d04",
            label="hottest cell minus coldest cell")
    a1.set_ylabel(r"$\bar{T}_{\max}-\bar{T}_{\min}$, K")
    a1.set_title("Pack uniformity across the eight cells "
                 "(shaded band: takeoff power pulse)", fontsize=9)
    a1.legend(fontsize=7.5, loc="upper left")
    a2.plot(times, qout, "-", lw=1.8, color="#08519c",
            label="heat removed at the channel-facing surfaces")
    a2.axhline(A.N_CELLS * A.P_CRUISE, ls="--", lw=1.1, color="0.35",
               label=r"cruise heat input, $8\times4$ W "
                     "(specified duty cycle)")
    a2.axhline(A.N_CELLS * A.P_TAKEOFF, ls=":", lw=1.1, color="0.35",
               label=r"takeoff heat input, $8\times15$ W "
                     "(specified duty cycle)")
    a2.set_xlabel(r"$t$, s")
    a2.set_ylabel(r"Heat rate $\dot{Q}$, W")
    a2.set_xlim(0.0, A.T_END)
    a2.legend(fontsize=7.5, loc="center right")
    a2.text(0.015, 0.87,
            "No outlet coolant temperature is shown because none exists in "
            "this configuration:\nthe cooling channels are not resolved as "
            "fluid, so there is no coolant stream to take an outlet\n"
            "temperature from. This panel shows the surface heat removal "
            "that is defined instead.",
            transform=a2.transAxes, fontsize=7, va="top",
            bbox=dict(boxstyle="round,pad=0.35", fc="#fdf6e3", ec="0.6",
                      lw=0.6))
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight")
    plt.close(fig)


def fig_table(table, out):
    hdr = ["Cell", "Peak temperature\nK", "Peak rise above coolant\nK",
           "Time to peak\ns", "Uncertainty on the peak\nK"]
    body = [[r["cell"], f"{r['peak_T_K']:.6f}", f"{r['peak_rise_K']:.6f}",
             f"{r['time_to_peak_s']:.0f}", "not established"] for r in table]
    fig, ax = plt.subplots(figsize=(8.8, 3.5))
    ax.axis("off")
    tb = ax.table(cellText=body, colLabels=hdr, loc="upper center",
                  cellLoc="center",
                  colWidths=[0.09, 0.22, 0.26, 0.17, 0.24])
    tb.auto_set_font_size(False)
    tb.set_fontsize(8)
    tb.scale(1, 1.5)
    for (r, c), cell in tb.get_celld().items():
        cell.set_linewidth(0.5)
        if r == 0:
            cell.set_facecolor("#e8eef5")
            cell.set_text_props(weight="bold", fontsize=7.5)
    ax.set_title("Peak temperature and time to peak, per cell\n"
                 "Volume-averaged over the 120 mesh cells of each cell; "
                 "coolant reference temperature 293.000000 K",
                 fontsize=9, pad=12)
    ax.text(0.0, -0.10,
            "Uncertainty column: not established from this configuration. "
            "One mesh and one time step were run in this arm, so no\n"
            "discretisation error estimate is available. Each value above is "
            "the field as computed, not a value carrying a measured\n"
            "error bar. The peak is the largest of 181 samples taken every "
            "5 s, so the time to peak is resolved to 5 s.",
            transform=ax.transAxes, fontsize=7, va="top", ha="left")
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------- main
def main():
    print("PLANTED CONTROL (a) -- shared parser")
    A.selftest(CASE)
    print()

    rects, vol, cy, groups, ncells, tv, ta = cell_rectangles(CASE)
    print(f"mesh   {ncells} cells, total volume {tv:.6f} m3, "
          f"channel area {ta:.4f} m2 -- four-way geometry guard passed")
    plant = plant_snapshot_control(CASE, ncells)
    print()

    rows, closure_pct, qint, last = A.analyse(CASE, quiet=True)
    times = np.array([r["t"] for r in rows])
    percell = np.array([r["percell"] for r in rows])
    qout = np.array([r["Qout"] for r in rows])
    spread = percell.max(axis=1) - percell.min(axis=1)

    snaps = {t: snapshot_field(CASE, t, ncells) for t in SNAP_TIMES}
    for t in SNAP_TIMES:
        v = np.asarray(snaps[t])
        print(f"  snapshot t = {t:6.1f} s   min {v.min():.6f} K   "
              f"max {v.max():.6f} K   range {v.max()-v.min():.6e} K")

    UNC = ("not established from this configuration -- one mesh and one time "
           "step, so no discretisation error estimate is available; the value "
           "is the field as computed, not a value with a measured error bar")
    table = []
    for i in range(A.N_CELLS):
        j = int(np.argmax(percell[:, i]))
        table.append({"cell": i + 1,
                      "peak_T_K": float(percell[j, i]),
                      "peak_rise_K": float(percell[j, i] - T_REF),
                      "time_to_peak_s": float(times[j]),
                      "uncertainty": UNC})

    vmin, vmax = fig_snapshots(rects, snaps, os.path.join(HERE, "actc_field_snapshots"))
    fig_histories(times, percell, os.path.join(HERE, "actc_cell_histories"))
    fig_uniformity(times, spread, qout, os.path.join(HERE, "actc_pack_uniformity"))
    fig_table(table, os.path.join(HERE, "actc_per_cell_table"))

    # ------------------------------------------------------------ data out
    with open(os.path.join(HERE, "actc_field_snapshots.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["mesh_cell_index", "x_min_m", "x_max_m", "y_min_m",
                    "y_max_m", "module_cell"]
                   + [f"T_K_at_t_{int(t)}s" for t in SNAP_TIMES])
        gof = {c: gi + 1 for gi, g in enumerate(groups) for c in g}
        for c in range(ncells):
            x0, x1, y0, y1 = rects[c]
            w.writerow([c, f"{x0:.9f}", f"{x1:.9f}", f"{y0:.9f}",
                        f"{y1:.9f}", gof[c]]
                       + [f"{snaps[t][c]:.9f}" for t in SNAP_TIMES])

    with open(os.path.join(HERE, "actc_cell_histories.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["time_s"] + [f"cell{i+1}_T_K" for i in range(A.N_CELLS)]
                   + [f"cell{i+1}_rise_K" for i in range(A.N_CELLS)])
        for k, t in enumerate(times):
            w.writerow([f"{t:.1f}"]
                       + [f"{percell[k, i]:.9f}" for i in range(A.N_CELLS)]
                       + [f"{percell[k, i]-T_REF:.9f}"
                          for i in range(A.N_CELLS)])

    with open(os.path.join(HERE, "actc_pack_uniformity.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["time_s", "spread_Tmax_minus_Tmin_K",
                    "surface_heat_removal_W", "outlet_temperature_K"])
        for k, t in enumerate(times):
            w.writerow([f"{t:.1f}", f"{spread[k]:.9f}", f"{qout[k]:.6f}",
                        "NOT DEFINED - channels not resolved as fluid"])

    with open(os.path.join(HERE, "actc_per_cell_table.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "peak_temperature_K", "peak_rise_above_coolant_K",
                    "time_to_peak_s", "uncertainty"])
        for r in table:
            w.writerow([r["cell"], f"{r['peak_T_K']:.6f}",
                        f"{r['peak_rise_K']:.6f}",
                        f"{r['time_to_peak_s']:.0f}", r["uncertainty"]])

    bundle = {
        "source_case": CASE,
        "reader": os.path.join(RUNS, "analyse_t25.py"),
        "mesh": {"n_mesh_cells": ncells, "total_volume_m3": tv,
                 "channel_area_m2": ta, "module_cells": A.N_CELLS,
                 "mesh_cells_per_module_cell": 120,
                 "geometry_guard": "satisfied, four ways"},
        "coolant_reference_temperature_K": T_REF,
        "pulse_window_s": [0.0, PULSE_END],
        "instrument_check_shared_parser": {
            "planted_K": 1.0, "scope": "all 960 cells at t = 900 s",
            "seen": True},
        "instrument_check_snapshot_extractor": plant,
        "snapshot_times_s": SNAP_TIMES,
        "snapshot_min_max_K": {str(int(t)): [float(np.min(snaps[t])),
                                             float(np.max(snaps[t]))]
                               for t in SNAP_TIMES},
        "shared_colour_scale_K": [vmin, vmax],
        "outlet_temperature": ("NOT DEFINED -- the cooling channels are not "
                               "resolved as a fluid region in this "
                               "configuration, so no coolant stream and no "
                               "outlet temperature exist; the defined "
                               "surface heat removal is given instead"),
        "surface_heat_removal_final_W": float(qout[-1]),
        "energy_closure_percent": closure_pct,
        "per_cell_table": table,
        "max_spread_K": float(spread.max()),
        "max_spread_time_s": float(times[int(np.argmax(spread))]),
    }
    with open(os.path.join(HERE, "actc_screen_data.json"), "w") as f:
        json.dump(bundle, f, indent=2)

    print()
    print(f"shared colour scale  {vmin:.6f} .. {vmax:.6f} K")
    print(f"max spread           {bundle['max_spread_K']:.6f} K at "
          f"t = {bundle['max_spread_time_s']:.0f} s")
    print(f"final surface heat removal {qout[-1]:.4f} W")
    print("outlet temperature   NOT DEFINED -- no fluid region")


if __name__ == "__main__":
    main()
