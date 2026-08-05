"""Square/rectangular-duct half of the battery, on TRAIN/VALIDATION cases.

THE POINT OF THIS FILE. The duct is where the challenge metric and the
field literature part company hardest. The metric sees one number per
case; the literature's duct metric is the in-plane secondary flow -- the
corner vortices that a linear eddy-viscosity model cannot produce at all.
Ling, Kurzawski & Templeton (JFM 2016 / OSTI 1333570) evaluate exactly
this with in-plane vector plots, verbatim: "Plot of secondary flows in
duct flow case. Reference arrows of length Ub /10 shown at the top of
each plot", and lay the field out as "Only the lower left quadrant of the
duct is shown, and the streamwise flow direction is out of the page" --
which is precisely the domain the benchmark ships. This script reproduces
that panel for RANS / our correction / truth and reports the answer
whatever it is.

FIGURES
  D1  in-plane secondary-flow vectors over |U_inplane|/U_b, three columns
      (RANS, corrected, truth), Ling's U_b/10 reference arrow.
  D2  streamwise velocity Ux/U_b at spanwise stations z/h.
  D3  1:1 scatter, one panel per quantity (Ux, Uy, Uz), black 1:1 line.
  D4  pointwise-error maps (the challenge metric's integrand) + integrated
      scalar per panel title.
  and the secondary-flow intensity scalar per model, per case.

CASES. AR_7_Ret_180 (the benchmark's own suggested duct validation case --
the one variant D was selected on) and AR_1_Ret_180, AR_3_Ret_180
(training). No test duct's ground truth is opened.

Run (2-core cap)::
    OMP_NUM_THREADS=2 taskset -c 0-1 /home/ubuntu/closure-venv/bin/python \
        sdk/scripts/closure_eval_battery/run_duct_battery.py
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import battery_common as bc  # noqa: E402

import closure_mesh_recon as mr  # noqa: E402
import train_closure_extended_correction as ex  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

CASES = ["AR_7_Ret_180", "AR_1_Ret_180", "AR_3_Ret_180"]
MODELS = ["RANS baseline (k-ω SST)", "corrected (entry of record)", "truth (LES/DNS)"]


def duct_bulk(case, C, U):
    """U_b, the bulk streamwise velocity: the cell-volume-weighted mean of
    Ux over the quadrant. Volume weights come from the same validated
    Green-Gauss mesh machinery the divergence audit uses."""
    mesh = mr.Mesh(ex._duct_case_dir(case))
    _, V = mr.reconstruct_cell_centres_vols(mesh)
    assert V.shape[0] == C.shape[0]
    return float(np.sum(V * U[:, 0]) / np.sum(V)), V


def _uniform_grid(C, h, fields, n_y=110):
    """Resample the (stretched, structured) quadrant onto a uniform (z,y)
    grid. Needed because streamplot requires uniform spacing; the raw mesh
    clusters cells at the walls. Linear interpolation, nearest fallback at
    the hull edge -- the same two-step used for the hill profiles."""
    from scipy.interpolate import griddata
    ar = float(C[:, 2].max() / h)
    zg = np.linspace(0.0, ar, int(round(n_y * ar)))
    yg = np.linspace(0.0, 1.0, n_y)
    Z, Y = np.meshgrid(zg, yg)
    pts = np.column_stack([C[:, 2] / h, C[:, 1] / h])
    tgt = np.column_stack([Z.ravel(), Y.ravel()])
    out = []
    for f in fields:
        comps = []
        for c in (2, 1):  # (Uz, Uy) -- the in-plane pair
            v = griddata(pts, f[:, c], tgt, method="linear")
            bad = ~np.isfinite(v)
            if bad.any():
                v[bad] = griddata(pts, f[:, c], tgt[bad], method="nearest")
            comps.append(v.reshape(Z.shape))
        out.append(tuple(comps))
    return zg, yg, Z, Y, out


def figure_secondary_flow(case, C, fields, Ub, h, outpath):
    """D1: in-plane secondary flow. Layout after Ling, Kurzawski & Templeton
    (JFM 2016) Fig. 4/6 -- "Only the lower left quadrant of the duct is
    shown, and the streamwise flow direction is out of the page", reference
    arrow "of length Ub /10". Streamlines over an in-plane-speed contour
    follow Liu, Wang, Zhao & Xiao (arXiv:2509.17189) Fig. S39b, verbatim
    "cross-sectional contours ... overlaid with streamlines illustrate the
    corner-vortex structures and secondary circulations"."""
    ar = float(C[:, 2].max() / h)
    zg, yg, Z, Y, inplane = _uniform_grid(C, h, fields)
    mags = [np.hypot(uz, uy) / Ub for uz, uy in inplane]
    vmax = max(float(max(np.percentile(m, 99.5) for m in mags)), 1e-9)

    panel_h = max(1.35, min(2.9, 11.0 / ar))
    W = float(np.clip(2.9 + panel_h * ar, 9.0, 15.0))
    H = 3 * (panel_h + 0.98) + 1.35
    fig, axes = plt.subplots(3, 1, figsize=(W, H))
    for ax, name, (uz, uy), m, raw in zip(axes, MODELS, inplane, mags, fields):
        pc = ax.pcolormesh(Z, Y, m, cmap=bc.CMAP_MAG, vmin=0.0, vmax=vmax,
                           shading="auto", rasterized=True)
        if m.max() > 1e-8:   # streamplot on an all-zero field draws nothing
            ax.streamplot(zg, yg, uz, uy, color="white", density=(1.1 * ar, 1.1),
                          linewidth=0.55, arrowsize=0.65)
        else:
            ax.text(0.5 * ar, 0.5, "no in-plane flow to stream "
                    "(field is zero to machine precision)",
                    ha="center", va="center", color="white", fontsize=8)
        raw_mag = np.linalg.norm(raw[:, 1:], axis=1) / Ub
        ax.set_title(f"{name}\nmean $|U_{{in-plane}}|/U_b$ = {raw_mag.mean():.2e},"
                     f"   peak = {raw_mag.max():.2e}",
                     fontsize=8, loc="left")
        ax.set_xlabel("$z/h$   (0 = duct centreplane, max = side wall)", fontsize=8)
        ax.set_ylabel("$y/h$\n(1 = wall)", fontsize=8)
        ax.set_xlim(0, ar)
        ax.set_ylim(0, 1.0)
        ax.set_aspect("equal", adjustable="box")
        ax.tick_params(labelsize=7)
        cb = fig.colorbar(pc, ax=ax, fraction=0.02 + 0.025 / ar, pad=0.012)
        cb.set_label("$|U_{in-plane}|/U_b$", fontsize=7)
        cb.ax.tick_params(labelsize=6)
    fig.suptitle(
        f"{case} (AR = {ar:.0f}): in-plane secondary flow, lower-left quadrant, "
        f"streamwise direction out of the page\n"
        f"layout after Ling et al. JFM 2016 Fig. 4/6; contour+streamline form after "
        f"Liu et al. arXiv:2509.17189 Fig. S39b\n"
        f"panel statistics are over all {C.shape[0]} solver cells, no averaging; "
        f"streamlines drawn on a uniform {len(zg)}×{len(yg)} resample.  "
        f"$U_b$ = {Ub:.3f} m/s (volume-weighted mean $U_x$, RANS field)",
        fontsize=8.5)
    fig.tight_layout(rect=(0, 0, 1, 1 - 0.95 / H))
    fig.savefig(outpath, dpi=160)
    plt.close(fig)


def figure_streamwise_profiles(case, C, fields, Ub, h, outpath):
    """D2: Ux/U_b against y/h at spanwise stations z/h, one panel per
    station. Stations are placed on the mesh's own z-lines nearest to a
    fixed set of fractions of the half-width, so no interpolation in z is
    needed."""
    zvals = np.unique(C[:, 2])
    ar = float(C[:, 2].max() / h)
    fracs = [0.05, 0.25, 0.5, 0.75, 0.95]
    picks = [zvals[np.argmin(np.abs(zvals - fr * C[:, 2].max()))] for fr in fracs]
    fig, axes = plt.subplots(1, len(picks), figsize=(3.0 * len(picks), 3.4),
                             sharey=True)
    for ax, z0 in zip(axes, picks):
        m = np.isclose(C[:, 2], z0)
        o = np.argsort(C[m, 1])
        yy = C[m, 1][o] / h
        for f, kw in zip(fields, (bc.RANS_KW, bc.CORR_KW, bc.TRUTH_KW)):
            ax.plot(f[m, 0][o] / Ub, yy, **kw)
        ax.set_title(f"$z/h$ = {z0 / h:.2f}  ({m.sum()} cells)", fontsize=8)
        ax.set_xlabel("$U_x/U_b$", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.25, linewidth=0.5)
    axes[0].set_ylabel("$y/h$   (0 = duct centreplane, 1 = wall)", fontsize=8)
    axes[-1].legend(fontsize=6.5, loc="lower left", framealpha=0.9)
    fig.suptitle(
        f"{case} (AR = {ar:.0f}): streamwise velocity on the mesh's own "
        f"z-lines, no averaging or interpolation; "
        f"$U_b$ = {Ub:.4f} m/s (volume-weighted mean $U_x$ of the RANS field)",
        fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(outpath, dpi=160)
    plt.close(fig)


def figure_scatter(pool, outpath, note):
    """D3: 1:1 scatter, one panel per velocity component."""
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.2))
    rng = np.random.default_rng(0)
    for ax, (label, comp) in zip(axes, [("$U_x$", 0), ("$U_y$", 1), ("$U_z$", 2)]):
        t = pool["truth"][:, comp]
        r = pool["rans"][:, comp]
        c = pool["corr"][:, comp]
        idx = rng.choice(t.shape[0], size=min(6000, t.shape[0]), replace=False)
        ax.scatter(t[idx], r[idx], s=2.5, alpha=0.3, color=bc.C_RANS, linewidths=0,
                   label="RANS baseline (k-ω SST)")
        ax.scatter(t[idx], c[idx], s=2.5, alpha=0.3, color=bc.C_CORR, linewidths=0,
                   label="corrected (entry of record)")
        lo = float(min(t.min(), r.min(), c.min()))
        hi = float(max(t.max(), r.max(), c.max()))
        ax.plot([lo, hi], [lo, hi], color="black", linewidth=1.2, zorder=5, label="1:1")
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel(f"truth (LES/DNS) {label}")
        ax.set_ylabel(f"model {label}")
        ax.set_title(label, fontsize=10)
    axes[0].legend(fontsize=7, loc="upper left", markerscale=4, framealpha=0.9)
    fig.suptitle(note, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(outpath, dpi=160)
    plt.close(fig)


def figure_error_maps(rows, outpath, title):
    """D4: pointwise ||U_model - U_truth||_2 maps + integrated scalar."""
    n = len(rows)
    fig, axes = plt.subplots(n, 2, figsize=(11.5, 2.6 * n), squeeze=False)
    for i, row in enumerate(rows):
        vmax = float(np.percentile(np.concatenate([row["e_rans"], row["e_corr"]]), 99))
        for j, (key, name, scalar) in enumerate((
                ("e_rans", "RANS baseline", row["mae_rans"]),
                ("e_corr", "corrected", row["mae_corr"]))):
            ax = axes[i][j]
            sc = ax.scatter(row["C"][:, 2] / row["h"], row["C"][:, 1] / row["h"],
                            c=row[key], s=2.0, cmap=bc.CMAP_MAG, vmin=0, vmax=vmax,
                            linewidths=0)
            ax.set_aspect("equal", adjustable="box")
            ax.set_xlabel("$z/h$", fontsize=8)
            ax.set_ylabel("$y/h$", fontsize=8)
            ax.set_title(f"{row['case']} — {name}: scaled MAE = {scalar:.4f}\n"
                         f"all {row['C'].shape[0]} cells, no volume weighting",
                         fontsize=8)
            ax.tick_params(labelsize=7)
            cb = fig.colorbar(sc, ax=ax, fraction=0.03, pad=0.015)
            cb.set_label(r"$\|U_{model}-U_{truth}\|_2$", fontsize=7)
            cb.ax.tick_params(labelsize=6)
    fig.suptitle(title, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.972))
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def main() -> int:
    t0 = time.time()
    bc.arm_scoring_guard()
    from Ofpp import parse_internal_field

    print("[fit] DUCT model, round-4 variant D (4 training cases)")
    duct_predict = bc.fit_duct_model(parse_internal_field)

    bc.OUT_DIR.mkdir(parents=True, exist_ok=True)
    figures, stats = [], {}
    pool = {"truth": [], "rans": [], "corr": []}
    map_rows = []

    for case in CASES:
        f = bc.load_duct_case(case, parse_internal_field, with_truth=True)
        U_rans, U_true = f["U"], f["U_truth"]
        U_corr = U_rans + duct_predict(f)
        C = f["C"]
        h = float(C[:, 1].max())
        Ub, V = duct_bulk(case, C, U_rans)

        out = bc.OUT_DIR / f"duct_secondary_flow_{case}.png"
        figure_secondary_flow(case, C, [U_rans, U_corr, U_true], Ub, h, out)
        figures.append(str(out))

        out = bc.OUT_DIR / f"duct_profiles_{case}.png"
        figure_streamwise_profiles(case, C, [U_rans, U_corr, U_true], Ub, h, out)
        figures.append(str(out))

        e_r = bc.pointwise_error(U_rans, U_true)
        e_c = bc.pointwise_error(U_corr, U_true)

        def sec_intensity(U):
            """Secondary-flow intensity: volume-weighted mean of the
            in-plane speed, normalised by U_b."""
            m = np.linalg.norm(U[:, 1:], axis=1)
            return float(np.sum(V * m) / np.sum(V) / Ub)

        stats[case] = {
            "role": "validation" if case in ex._DUCT_VAL else "train",
            "n_cells": int(C.shape[0]),
            "aspect_ratio": round(float(C[:, 2].max() / h), 2),
            "U_b_volume_weighted_rans": round(Ub, 4),
            "scaled_mae_cells_rans": round(bc.scaled_mae_cells(U_rans, U_true), 4),
            "scaled_mae_cells_corrected": round(bc.scaled_mae_cells(U_corr, U_true), 4),
            "secondary_flow_intensity_rans": sec_intensity(U_rans),
            "secondary_flow_intensity_corrected": sec_intensity(U_corr),
            "secondary_flow_intensity_truth": sec_intensity(U_true),
        }
        s = stats[case]
        s["secondary_flow_recovered_fraction"] = round(
            s["secondary_flow_intensity_corrected"]
            / s["secondary_flow_intensity_truth"], 4)
        print(f"  {case:16s} [{s['role']:10s}] scaled MAE {s['scaled_mae_cells_rans']:.4f}"
              f" -> {s['scaled_mae_cells_corrected']:.4f} | secondary-flow intensity "
              f"RANS {s['secondary_flow_intensity_rans']:.2e} / corr "
              f"{s['secondary_flow_intensity_corrected']:.4f} / truth "
              f"{s['secondary_flow_intensity_truth']:.4f} "
              f"({100 * s['secondary_flow_recovered_fraction']:.1f}% recovered)")

        for key, arr in (("truth", U_true), ("rans", U_rans), ("corr", U_corr)):
            pool[key].append(arr)
        map_rows.append(dict(case=case, C=C, h=h, e_rans=e_r, e_corr=e_c,
                             mae_rans=s["scaled_mae_cells_rans"],
                             mae_corr=s["scaled_mae_cells_corrected"]))

    # Validity anchor: the pre-registered variant-D validation number.
    val = stats["AR_7_Ret_180"]["scaled_mae_cells_corrected"]
    print(f"[anchor] AR_7_Ret_180 corrected scaled MAE = {val:.4f} "
          f"(pre-registered variant D: 0.0135)")
    assert abs(val - 0.0135) < 1e-3, (
        f"AR_7 {val:.4f} != pre-registered 0.01345; this is not variant D")

    p = {k: np.concatenate(v) for k, v in pool.items()}
    out = bc.OUT_DIR / "duct_scatter.png"
    figure_scatter(p, out,
                   f"Ducts, {len(CASES)} train/validation cases: "
                   f"{p['truth'].shape[0]} cells, 6000 plotted (uniform random, "
                   f"seed 0). One point per cell of the case's own solved field, "
                   f"no averaging.")
    figures.append(str(out))

    out = bc.OUT_DIR / "duct_error_maps.png"
    figure_error_maps(map_rows, out,
                      "Ducts, train/validation cases: pointwise "
                      r"$\|U_{model}-U_{truth}\|_2$ (the challenge metric's "
                      "integrand). Colour scale shared within a row, capped at "
                      "that case's 99th percentile.")
    figures.append(str(out))

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "produced_by": "sdk/scripts/closure_eval_battery/run_duct_battery.py",
        "protocol": "demo-output/website/CLOSURE_EVALUATION_PROTOCOL.md",
        "test_blindness": {"scoring_calls": 0, "test_ground_truth_reads": 0},
        "model": "round-4 variant D: 7 Pope invariants + d/d_max, target "
                 "(U_LES-U_RANS)/mean|U_RANS|, HistGradientBoostingRegressor x3, "
                 "random_state=0, 4 DUCT training cases",
        "validity_anchor": {
            "AR_7_Ret_180_corrected_scaled_mae_this_run": val,
            "pre_registered_value": 0.01345,
            "source": "closure_challenge_duct_reynolds_transfer.json",
        },
        "secondary_flow_convention": {
            "quantity": "|U_inplane| = sqrt(Uy^2 + Uz^2), normalised by U_b",
            "layout": "lower-left quadrant, streamwise direction out of the page",
            "reference_arrow": "U_b/10",
            "citation": "Ling, Kurzawski & Templeton, JFM 2016 (OSTI 1333570), "
                        "Fig. 6 'Reference arrows of length Ub /10 shown at the "
                        "top of each plot'; Fig. 4 'Only the lower left quadrant "
                        "of the duct is shown, and the streamwise flow direction "
                        "is out of the page.'",
            "intensity_scalar_is_our_extension": True,
        },
        "per_case": stats,
        "figures": figures,
        "compute": {"elapsed_seconds": round(time.time() - t0, 1), "cores_cap": 2},
    }
    bc.write_json(bc.OUT_DIR / "duct_battery.json", payload)
    print(f"elapsed {time.time() - t0:.1f}s; {len(figures)} figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
