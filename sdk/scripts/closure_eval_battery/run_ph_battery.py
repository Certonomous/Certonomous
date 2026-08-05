"""Periodic-hill half of the evaluation battery, on TRAIN/VALIDATION cases.

WHAT THIS PRODUCES (per demo-output/website/CLOSURE_EVALUATION_PROTOCOL.md):
  M1  station velocity profiles in the para-database's own offset form
      `2 Ux/Ub + x/H` vs `y/H` at x/H = 1..8 (Xiao, Wang & Ghanem 2016,
      arXiv:1603.09656, Fig. 10 axis label, verbatim: "x/H; 2Ux /Ub + x/H";
      "eight streamwise locations x/H = 1, . . . , 8"). Truth = black filled
      circles, RANS = blue dashed, corrected = red solid.
  M2  1:1 scatter, one panel per quantity (Ux, Uy, |U|), black 1:1 line.
  M3  pointwise-error maps -- the challenge metric's own integrand
      ||U_pred - U_true||_2 per cell -- RANS vs corrected, shared colour
      scale per case, with the integrated scalar (cell-population scaled
      MAE) in each panel title.
  M4  per-case statistics rows for the master table.

CASES. The 4 PH validation cases (held out from fitting, truth legal) plus
3 PH training cases spanning the alpha family. No test case's ground truth
is opened -- the loader in battery_common.py refuses by whitelist, and the
scoring guard is armed before any work.

Run (2-core cap)::
    OMP_NUM_THREADS=2 taskset -c 0-1 /home/ubuntu/closure-venv/bin/python \
        sdk/scripts/closure_eval_battery/run_ph_battery.py
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import battery_common as bc  # noqa: E402

import train_closure_periodic_hill_correction as ph  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Held-out validation cases first (the honest ones), then 3 training cases
# spanning the alpha family for the in-sample comparison.
VAL_CASES = list(ph._PH_VAL)
TRAIN_SHOWN = ["alpha_10_9000_3036", "alpha_05_7071_3036", "alpha_15_10929_3036"]
STATIONS = [1, 2, 3, 4, 5, 6, 7, 8]   # Xiao et al. 2016, Fig. 10
PROFILE_SCALE = 2.0                    # the "2 Ux/Ub" of that same axis label


def bulk_velocity_at_crest(C, U, h, Ly):
    """U_b, the bulk velocity at the crest -- the periodic-hill normaliser.

    Xiao, Wang & Ghanem 2016 (arXiv:1603.09656) §3: "Re is based on the
    crest height H and bulk velocity Ub at the crest". Computed here as the
    height-average of <Ux> over the crest column, from y = H to the top
    wall, on the field supplied (the truth field, so all three curves in a
    figure share one normaliser -- stated in every caption)."""
    x0 = float(C[:, 0].min())
    col = np.abs(C[:, 0] - x0) < 1e-9
    y = C[col, 1]
    ux = U[col, 0]
    order = np.argsort(y)
    y, ux = y[order], ux[order]
    keep = y >= h - 1e-9
    return float(np.trapezoid(ux[keep], y[keep]) / (y[keep].max() - y[keep].min()))


def figure_profiles(case, geom, C, U_rans, U_corr, U_true, Ub, outpath):
    """M1: the offset station-profile plot, Xiao et al. Fig. 10 convention."""
    h, Ly, Lx = geom["h"], geom["Ly"], geom["Lx"]
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    used = []
    for s in STATIONS:
        x0 = s * h
        if x0 > Lx - 0.02:
            continue
        used.append(s)
        # lower-wall height at this station, from the mesh's own floor curve
        y_lo = float(np.interp(x0, geom["floor_x"], geom["floor_y"]))
        for field, kw in ((U_true, bc.TRUTH_KW), (U_rans, bc.RANS_KW), (U_corr, bc.CORR_KW)):
            y, ux = bc.sample_profile(C, field[:, 0], x0, y_lo, Ly, n=48)
            ax.plot(PROFILE_SCALE * ux / Ub + s, y / h,
                    **{k: v for k, v in kw.items() if k != "label"})
        ax.axvline(s, color="0.85", linewidth=0.6, zorder=0)
    # legend proxies (labels once, not once per station)
    for kw in (bc.TRUTH_KW, bc.RANS_KW, bc.CORR_KW):
        ax.plot([], [], **kw)
    ax.set_xlabel("$x/H$;   $2U_x/U_b + x/H$")
    ax.set_ylabel("$y/H$")
    ax.set_xlim(used[0] - 1.0, used[-1] + 1.6)
    ax.set_ylim(0, Ly / h)
    ax.set_title(
        f"{case}: streamwise velocity at x/H = {used[0]}..{used[-1]}\n"
        f"all cells on the station line, linear interpolation; "
        f"$U_b$ = {Ub:.4f} (crest bulk of the LES field, height-averaged H..{Ly/h:.3f}H)",
        fontsize=9)
    ax.legend(fontsize=8, loc="upper right", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(outpath, dpi=160)
    plt.close(fig)
    return used


def figure_scatter(pool, outpath, population_note):
    """M2: 1:1 scatter, one panel per quantity, black 1:1 line."""
    quantities = [("$U_x$", 0), ("$U_y$", 1), (r"$\|U\|$", None)]
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 5.0))
    rng = np.random.default_rng(0)
    for ax, (label, comp) in zip(axes, quantities):
        def q(field):
            return np.linalg.norm(field, axis=1) if comp is None else field[:, comp]
        t, r, c = q(pool["truth"]), q(pool["rans"]), q(pool["corr"])
        n = t.shape[0]
        idx = rng.choice(n, size=min(6000, n), replace=False)
        ax.scatter(t[idx], r[idx], s=2.5, alpha=0.25, color=bc.C_RANS,
                   linewidths=0, label="RANS baseline (k-ω SST)")
        ax.scatter(t[idx], c[idx], s=2.5, alpha=0.25, color=bc.C_CORR,
                   linewidths=0, label="corrected (entry of record)")
        lo = float(min(t.min(), r.min(), c.min()))
        hi = float(max(t.max(), r.max(), c.max()))
        ax.plot([lo, hi], [lo, hi], color="black", linewidth=1.2, zorder=5,
                label="1:1")
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel(f"truth (LES) {label}")
        ax.set_ylabel(f"model {label}")
        ax.set_title(f"{label}", fontsize=10)
    axes[0].legend(fontsize=7, loc="upper left", markerscale=4, framealpha=0.9)
    fig.suptitle(population_note, fontsize=9)
    fig.tight_layout(rect=(0, 0.01, 1, 0.93))
    fig.savefig(outpath, dpi=160)
    plt.close(fig)


def figure_error_maps(rows, outpath, title):
    """M3: the challenge metric's integrand as a field, RANS vs corrected."""
    n = len(rows)
    fig, axes = plt.subplots(n, 2, figsize=(11.0, 2.55 * n), squeeze=False)
    for i, row in enumerate(rows):
        C = row["C"]
        vmax = float(np.percentile(np.concatenate([row["e_rans"], row["e_corr"]]), 99))
        for j, (key, name, scalar) in enumerate((
                ("e_rans", "RANS baseline", row["mae_rans"]),
                ("e_corr", "corrected", row["mae_corr"]))):
            ax = axes[i][j]
            sc = ax.scatter(C[:, 0] / row["h"], C[:, 1] / row["h"], c=row[key],
                            s=1.6, cmap=bc.CMAP_MAG, vmin=0.0, vmax=vmax,
                            linewidths=0)
            ax.set_aspect("equal", adjustable="box")
            ax.set_xlabel("$x/H$", fontsize=8)
            ax.set_ylabel("$y/H$", fontsize=8)
            ax.set_title(f"{row['case']} — {name}: scaled MAE = {scalar:.4f}\n"
                         f"all {C.shape[0]} cells, no volume weighting",
                         fontsize=8)
            ax.tick_params(labelsize=7)
            cb = fig.colorbar(sc, ax=ax, fraction=0.035, pad=0.02)
            cb.set_label(r"$\|U_{model}-U_{truth}\|_2$", fontsize=7)
            cb.ax.tick_params(labelsize=6)
    fig.suptitle(title, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def main() -> int:
    t0 = time.time()
    bc.arm_scoring_guard()
    from Ofpp import parse_internal_field

    print("[fit] PH model (21 training cases, random_state=0)")
    ph_predict = bc.fit_ph_model(parse_internal_field)

    bc.OUT_DIR.mkdir(parents=True, exist_ok=True)
    figures, stats = [], {}
    pools = {"validation": {"truth": [], "rans": [], "corr": []},
             "train": {"truth": [], "rans": [], "corr": []}}
    map_rows = {"validation": [], "train": []}

    for group, cases in (("validation", VAL_CASES), ("train", TRAIN_SHOWN)):
        for case in cases:
            f = bc.load_ph_case(case, parse_internal_field, with_truth=True)
            X = ph.build_features(f["gradU"], f["k"], f["omega"],
                                  f["walldist"], f["U"], f["nu"])
            U_rans = f["U"]
            U_corr = U_rans + ph_predict(X)
            U_true = f["U_truth"]
            geom = bc.ph_geometry(f["C"])

            # Validity check on the normalisation, from a second and
            # independent source: the domain-height tag in the case name
            # (e.g. ..._3036 -> Ly/h = 3.036) must agree with the measured
            # crest-normalised domain height to 2%. `alpha_075` and
            # `alpha_125` carry no tag; they are checked against Breuer's
            # 3.036 channel height instead.
            tag = case.rsplit("_", 1)[-1]
            expect = float(tag) / 1000.0 if tag.isdigit() and len(tag) == 4 else 3.036
            measured = geom["Ly"] / geom["h"]
            assert abs(measured - expect) / expect < 0.02, (case, measured, expect)

            Ub = bulk_velocity_at_crest(f["C"], U_true, geom["h"], geom["Ly"])
            out = bc.OUT_DIR / f"ph_profiles_{case}.png"
            used = figure_profiles(case, geom, f["C"], U_rans, U_corr, U_true,
                                   Ub, out)
            figures.append(str(out))

            e_r = bc.pointwise_error(U_rans, U_true)
            e_c = bc.pointwise_error(U_corr, U_true)
            stats[case] = {
                "group": group,
                "n_cells": int(U_true.shape[0]),
                "U_b_crest_from_LES": round(Ub, 5),
                "h": round(geom["h"], 4),
                "Lx_over_h": round(geom["Lx"] / geom["h"], 3),
                "stations_plotted_x_over_h": used,
                "scaled_mae_cells_rans": round(bc.scaled_mae_cells(U_rans, U_true), 4),
                "scaled_mae_cells_corrected": round(bc.scaled_mae_cells(U_corr, U_true), 4),
                "max_pointwise_error_rans": round(float(e_r.max()), 4),
                "max_pointwise_error_corrected": round(float(e_c.max()), 4),
            }
            print(f"  {case:24s} [{group:10s}] RANS {stats[case]['scaled_mae_cells_rans']:.4f}"
                  f" -> corrected {stats[case]['scaled_mae_cells_corrected']:.4f}")

            for key, arr in (("truth", U_true), ("rans", U_rans), ("corr", U_corr)):
                pools[group][key].append(arr)
            map_rows[group].append(dict(case=case, C=f["C"], h=geom["h"],
                                        e_rans=e_r, e_corr=e_c,
                                        mae_rans=stats[case]["scaled_mae_cells_rans"],
                                        mae_corr=stats[case]["scaled_mae_cells_corrected"]))

    # Validity anchor: pooled validation scaled MAE must reproduce the
    # recorded round-1 value 0.0876.
    vp = {k: np.concatenate(v) for k, v in pools["validation"].items()}
    pooled_val = bc.scaled_mae_cells(vp["corr"], vp["truth"])
    pooled_val_rans = bc.scaled_mae_cells(vp["rans"], vp["truth"])
    print(f"[anchor] pooled validation scaled MAE = {pooled_val:.4f} "
          f"(recorded round 1: 0.0876)")
    assert abs(pooled_val - 0.0876) < 5e-4, (
        f"pooled validation {pooled_val:.4f} != recorded 0.0876; this is not "
        "the model behind the entry of record")

    for group in ("validation", "train"):
        p = {k: np.concatenate(v) for k, v in pools[group].items()}
        out = bc.OUT_DIR / f"ph_scatter_{group}.png"
        cases = VAL_CASES if group == "validation" else TRAIN_SHOWN
        figure_scatter(
            p, out,
            f"Periodic hills, {group} cases ({len(cases)}): {p['truth'].shape[0]} cells, "
            f"6000 plotted (uniform random, seed 0). No spatial or temporal averaging — "
            f"one point per cell of the case's own solved field.")
        figures.append(str(out))

        out = bc.OUT_DIR / f"ph_error_maps_{group}.png"
        figure_error_maps(
            map_rows[group], out,
            f"Periodic hills, {group} cases: pointwise "
            r"$\|U_{model}-U_{truth}\|_2$ (the challenge metric's integrand). "
            "Colour scale shared within a row, capped at that case's 99th percentile.")
        figures.append(str(out))

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "produced_by": "sdk/scripts/closure_eval_battery/run_ph_battery.py",
        "protocol": "demo-output/website/CLOSURE_EVALUATION_PROTOCOL.md",
        "test_blindness": {
            "scoring_calls": 0,
            "test_ground_truth_reads": 0,
            "how": "raising-stub guard armed and proven before any work; the "
                   "ground-truth loader asserts the case against the "
                   "PH train+validation whitelist before opening a file",
        },
        "model": "round-1 PH HistGradientBoostingRegressor x3, random_state=0, "
                 "21 PH training cases, 7 Pope-invariant features",
        "validity_anchor": {
            "pooled_validation_scaled_mae_this_run": round(pooled_val, 4),
            "recorded_round1_value": 0.0876,
            "pooled_validation_rans_floor_this_run": round(pooled_val_rans, 4),
            "matches": abs(pooled_val - 0.0876) < 5e-4,
        },
        "station_convention": {
            "stations_x_over_h": STATIONS,
            "offset_axis": "2*Ux/Ub + x/H against y/H",
            "citation": "Xiao, Wang & Ghanem, arXiv:1603.09656, Fig. 10 axis "
                        "label 'x/H; 2Ux /Ub + x/H'; 'eight streamwise "
                        "locations x/H = 1, ..., 8'",
            "clipping_note": "stations beyond the case's own Lx/h are omitted "
                             "(the para-database alpha family stretches the "
                             "domain); the plotted range is recorded per case",
        },
        "per_case": stats,
        "figures": figures,
        "compute": {"elapsed_seconds": round(time.time() - t0, 1), "cores_cap": 2},
    }
    bc.write_json(bc.OUT_DIR / "ph_battery.json", payload)
    print(f"elapsed {time.time() - t0:.1f}s; {len(figures)} figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
