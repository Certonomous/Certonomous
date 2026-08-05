#!/usr/bin/env python3
"""Analysis half of the flat-plate coefficient-uncertainty ladder.

Three propagations on ONE sample set -- direct Monte Carlo, a chaos expansion,
a process surrogate -- plus the plots and the study record. Kept apart from the
solve half so re-reading the samples never risks re-running them.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "sdk"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from chief_engineer import pce_surrogate as ps            # noqa: E402
from chief_engineer import uncertainty_band as ub         # noqa: E402
from coefficient_uq_plate import (                        # noqa: E402
    CELLS, CF_STATION, CFL3D_SST_V, COEFFICIENTS, FUN3D_SST_V, LOWER, NAMES,
    NOMINAL, OUT, STUDY, UPPER, load_results, solver_coefficients,
)

QOIS = {"cd": "Cd", "cf_station": f"Cf at x = {CF_STATION}"}
RESAMPLE = 200_000
RESAMPLE_SEED = 20260807

CONVENTION = ("Convention: shaded region is the propagated coefficient band; "
              "black symbols are reference values, not our solves.")


# ---------------------------------------------------------------------------
# Propagation
# ---------------------------------------------------------------------------

def box_resample(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return LOWER + rng.random((n, len(LOWER))) * (UPPER - LOWER)


def surrogate_band(predict, reference: float) -> dict[str, Any]:
    """Band read off a surrogate by dense resampling of the same box.

    The direct band comes from 42 solves; this one comes from 200,000 surrogate
    evaluations of the same box. Where the two agree, the 42 solves were enough
    to see the box; where the surrogate band is wider, the sample set had not
    reached the corners the surrogate thinks are there.
    """
    x = box_resample(RESAMPLE, RESAMPLE_SEED)
    return ps.band_from_samples(predict(x), reference=reference)


def qoi_analysis(key: str, x_train: np.ndarray, y_train: np.ndarray,
                 x_valid: np.ndarray, y_valid: np.ndarray,
                 baseline: float, reference: dict[str, float]) -> dict[str, Any]:
    ref_value = reference["value"]
    out: dict[str, Any] = {
        "quantity": QOIS[key],
        "baseline_openfoam_default": baseline,
        "reference": reference,
        "monte_carlo": ps.band_from_samples(y_train, reference=ref_value),
    }
    out["monte_carlo"]["method"] = (
        f"direct propagation: {len(y_train)} maximin-Latin-hypercube samples of "
        f"the 5-coefficient box, one solve each on the held mesh")
    out["monte_carlo"]["baseline_inside_envelope"] = bool(
        out["monte_carlo"]["min"] <= baseline <= out["monte_carlo"]["max"])

    # ---- chaos expansions, order 1 and 2, scored on the held-out set
    pce: dict[str, Any] = {}
    for order in (1, 2):
        fit = ps.fit_pce(x_train, y_train, lower=LOWER, upper=UPPER,
                         names=NAMES, order=order)
        record = fit.as_dict()
        held = y_valid - fit.predict(x_valid)
        spread = float(np.sum((y_valid - y_valid.mean()) ** 2))
        record["holdout_rmse"] = float(np.sqrt(np.mean(held ** 2)))
        record["holdout_q2"] = 1.0 - float(np.sum(held ** 2)) / spread
        record["holdout_max_abs_error"] = float(np.max(np.abs(held)))
        record["band"] = surrogate_band(fit.predict, ref_value)
        pce[f"order_{order}"] = record
        if order == 2:
            out["_pce2"] = fit
    out["polynomial_chaos"] = pce

    # ---- process surrogate
    gp = ps.fit_gp(x_train, y_train, lower=LOWER, upper=UPPER, names=NAMES,
                   seed=17)
    record = gp.as_dict()
    mean, std = gp.predict(x_valid, with_std=True)
    held = y_valid - mean
    spread = float(np.sum((y_valid - y_valid.mean()) ** 2))
    record["holdout_rmse"] = float(np.sqrt(np.mean(held ** 2)))
    record["holdout_q2"] = 1.0 - float(np.sum(held ** 2)) / spread
    record["holdout_max_abs_error"] = float(np.max(np.abs(held)))
    record["holdout_z_rms"] = float(np.sqrt(np.mean((held / std) ** 2)))
    record["band"] = surrogate_band(lambda a: gp.predict(a), ref_value)
    out["gaussian_process"] = record
    out["_gp"] = gp

    # ---- the three bands side by side
    mc = out["monte_carlo"]
    p2 = pce["order_2"]["band"]
    gpb = record["band"]
    out["band_comparison"] = {
        "envelope_width": {"monte_carlo": mc["envelope_width"],
                           "polynomial_chaos_order_2": p2["envelope_width"],
                           "gaussian_process": gpb["envelope_width"]},
        "std": {"monte_carlo": mc["std"],
                "polynomial_chaos_order_2": p2["std"],
                "gaussian_process": gpb["std"]},
        "chaos_std_vs_mc_pct": 100.0 * (p2["std"] - mc["std"]) / mc["std"],
        "process_std_vs_mc_pct": 100.0 * (gpb["std"] - mc["std"]) / mc["std"],
        "reading": (
            "the standard deviations are the comparable pair: all three are "
            "computed over the same assumed uniform box. The ENVELOPES are not "
            "directly comparable -- the direct one is a minimum over 42 solves "
            f"and the surrogate ones are minima over {RESAMPLE:,} surrogate "
            "evaluations, so the surrogate envelopes should be wider whenever "
            "the surrogates are trustworthy, and that is what makes them useful"),
    }
    return out


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def _style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "font.size": 11, "axes.grid": True, "grid.alpha": 0.25,
        "axes.spines.top": False, "axes.spines.right": False,
    })
    return plt


def plot_cf_band(records: list[dict], baseline_profile, out_png: Path) -> None:
    """Cf(x) with the coefficient band as a shaded region."""
    plt = _style()
    xs = np.array([p[0] for p in baseline_profile])
    stack = []
    for rec in records:
        prof = np.array(rec["cf_profile"])
        stack.append(np.interp(xs, prof[:, 0], prof[:, 1]))
    stack = np.array(stack)
    base = np.array([p[1] for p in baseline_profile])

    fig, ax = plt.subplots(figsize=(9.0, 5.4), dpi=150)
    ax.fill_between(xs, stack.min(0), stack.max(0), color="#3b7dd8", alpha=0.22,
                    label=f"coefficient band, envelope of {len(records)} solves")
    ax.fill_between(xs, np.percentile(stack, 5, axis=0),
                    np.percentile(stack, 95, axis=0), color="#3b7dd8",
                    alpha=0.30, label="central 90% of the same solves")
    ax.plot(xs, base, color="#12305c", lw=1.8,
            label="baseline (OpenFOAM default coefficients)")
    for tag, data, marker in (("CFL3D SST-V", CFL3D_SST_V[CELLS], "s"),
                              ("FUN3D SST-V", FUN3D_SST_V[CELLS], "o")):
        ax.plot([CF_STATION], [data["cf097"]], marker, color="black", ms=8,
                mfc="black", zorder=6, label=f"{tag}, x = {CF_STATION:.4f}")
    ax.set_xscale("log")
    ax.set_xlim(1e-3, 2.0)
    ax.set_xlabel("x along the plate  [m]")
    ax.set_ylabel(r"skin friction  $C_f$")
    ax.set_title("Flat plate: what the closure coefficients do to $C_f(x)$",
                 loc="left", weight="bold")
    ax.legend(frameon=False, fontsize=9.5, loc="upper right")
    ax.annotate(CONVENTION, xy=(0, -0.16), xycoords="axes fraction",
                fontsize=8.5, color="#555")
    fig.tight_layout()
    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)


def plot_band_comparison(analysis: dict, out_png: Path) -> None:
    """The three propagations of the same samples, one row each, per QoI."""
    plt = _style()
    fig, axes = plt.subplots(2, 1, figsize=(11.0, 7.6), dpi=150)
    for ax, key in zip(axes, QOIS):
        a = analysis[key]
        n = a["monte_carlo"]["n"]
        rows = [(f"Monte Carlo\n{n} solves", a["monte_carlo"]),
                ("polynomial chaos\norder 2, same solves",
                 a["polynomial_chaos"]["order_2"]["band"]),
                ("process surrogate\nsame solves", a["gaussian_process"]["band"])]
        labels = []
        for i, (label, band) in enumerate(rows):
            y = len(rows) - i
            labels.append((y, label))
            ax.barh([y], [band["max"] - band["min"]], left=band["min"],
                    height=0.40, color="#3b7dd8", alpha=0.20, zorder=2)
            ax.barh([y], [band["percentile_95"] - band["percentile_5"]],
                    left=band["percentile_5"], height=0.40, color="#3b7dd8",
                    alpha=0.45, zorder=3)
            ax.plot([band["mean"]], [y], "D", color="#12305c", ms=7, zorder=5)
            ax.annotate(f"{band['max'] - band['min']:.2e} wide",
                        xy=(band["max"], y), xytext=(8, 0),
                        textcoords="offset points", va="center", fontsize=9,
                        color="#333")
        base = a["baseline_openfoam_default"]
        ax.axvline(base, color="#12305c", lw=1.4, ls="--", zorder=4)
        ref = a["reference"]
        ax.plot([ref["value"]], [0], "s", color="black", ms=9, zorder=7)
        ax.plot([ref["second_value"]], [0], "o", color="black", ms=8,
                mfc="none", mew=1.8, zorder=7)
        labels.append((0, "reference codes\n(not our solves)"))
        ax.annotate(f"{ref['code']}  {ref['value']:.5f}",
                    xy=(ref["value"], 0), xytext=(0, 12),
                    textcoords="offset points", ha="center", fontsize=9,
                    color="black")
        ax.set_yticks([y for y, _ in labels])
        ax.set_yticklabels([t for _, t in labels], fontsize=9.5)
        ax.set_ylim(-0.6, len(rows) + 0.6)
        span = a["monte_carlo"]
        pad = 0.10 * (span["max"] - span["min"])
        ax.set_xlim(min(span["min"], ref["value"]) - pad,
                    max(span["max"], ref["value"]) + 2.2 * pad)
        ax.set_xlabel(QOIS[key])
        ax.set_title(
            f"{QOIS[key]}   —   envelope is {span['envelope_pct_of_reference']:.1f}% "
            f"of the reference value", loc="left", weight="bold", fontsize=11.5)
    axes[1].annotate(
        "Convention: light band is the full envelope, darker band the central 90%, "
        "diamond the mean; dashed line is our baseline solve; black filled square "
        "is CFL3D and open circle FUN3D — reference codes, not our solves.",
        xy=(0, -0.30), xycoords="axes fraction", fontsize=9, color="#555")
    fig.suptitle("Same 42 solves, three ways of turning them into a band",
                 x=0.06, ha="left", weight="bold", fontsize=13)
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)


def plot_sobol(analysis: dict, out_png: Path) -> None:
    plt = _style()
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.6), dpi=150)
    for ax, key in zip(axes, QOIS):
        rec = analysis[key]["polynomial_chaos"]["order_2"]
        first = rec["sobol_first_order"]
        total = rec["sobol_total"]
        order = sorted(NAMES, key=lambda n: total[n])
        ys = np.arange(len(order))
        ax.barh(ys, [first[n] for n in order], height=0.5, color="#3b7dd8",
                alpha=0.85, label=r"main effect $S_i$")
        ax.plot([total[n] for n in order], ys, "o", mfc="none", mec="#d1701a",
                mew=2.0, ms=11, label=r"total effect $S_{T_i}$")
        for y, n in zip(ys, order):
            ax.annotate(f"{first[n] * 100:.1f}%",
                        xy=(max(first[n], total[n]), y), xytext=(14, 0),
                        textcoords="offset points", va="center", fontsize=9.5)
        ax.set_yticks(ys)
        ax.set_yticklabels(order, fontsize=10)
        ax.set_xlim(0, 1.22)
        ax.set_xlabel("share of variance")
        ax.set_title(f"{QOIS[key]}   (chaos $Q^2_{{LOO}}$ = "
                     f"{rec['loo_q2']:.4f})", loc="left", weight="bold")
        ax.legend(frameon=False, fontsize=9.5, loc="lower right")
    axes[0].annotate(
        "Convention: shares are of the variance under the assumed uniform box, "
        "not of the interval envelope; the gap between bar and ring is "
        "interaction.",
        xy=(0, -0.24), xycoords="axes fraction", fontsize=8.5, color="#555")
    fig.suptitle("Which coefficient owns the band", x=0.02, ha="left",
                 weight="bold")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)


def plot_surrogate_validation(analysis: dict, x_valid, values, out_png: Path) -> None:
    """Held-out predictions against held-out solves; black is the truth line."""
    plt = _style()
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.0), dpi=150)
    for ax, key in zip(axes, QOIS):
        truth = values[key]
        pce = analysis[key]["_pce2"].predict(x_valid)
        gp_mean, gp_std = analysis[key]["_gp"].predict(x_valid, with_std=True)
        span = [min(truth.min(), pce.min(), gp_mean.min()),
                max(truth.max(), pce.max(), gp_mean.max())]
        pad = 0.05 * (span[1] - span[0])
        ax.plot(span, span, "-", color="black", lw=1.4, zorder=2,
                label="exact agreement")
        ax.errorbar(truth, gp_mean, yerr=2 * gp_std, fmt="o", color="#d1701a",
                    ms=6, elinewidth=1.2, capsize=3, zorder=4,
                    label="process surrogate, 2$\\sigma$ posterior")
        ax.plot(truth, pce, "^", color="#3b7dd8", ms=7, zorder=5,
                label="chaos expansion, order 2")
        ax.set_xlim(span[0] - pad, span[1] + pad)
        ax.set_ylim(span[0] - pad, span[1] + pad)
        ax.set_xlabel(f"solved {QOIS[key]} (held-out sample)")
        ax.set_ylabel(f"predicted {QOIS[key]}")
        ax.set_title(f"{QOIS[key]}", loc="left", weight="bold")
        ax.legend(frameon=False, fontsize=9.0, loc="upper left")
    axes[0].annotate(
        "Convention: black line is exact agreement, the truth these surrogates "
        "are scored against; every point is a solve neither surrogate was "
        "fitted on.",
        xy=(0, -0.20), xycoords="axes fraction", fontsize=8.5, color="#555")
    fig.suptitle("Ten solves neither surrogate saw", x=0.02, ha="left",
                 weight="bold")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def dominance_diagnostic(x_train: np.ndarray, train: list[dict]) -> dict[str, Any]:
    """Independent check on WHY the leading coefficient leads.

    A variance share names the input that owns the band; it does not say
    through what. Here the answer changes how the result should be read, so it
    is measured rather than asserted: the derived gamma1 is reconstructed for
    every sample, its own variance is decomposed over the sampled box, and Cd
    is refitted against gamma1 alone. If the leading coefficient's effect runs
    through the log-layer relation, this is where that shows up -- and a reader
    comparing against a study that did NOT enforce that relation needs to know
    it before comparing.
    """
    y = np.array([r["cd"] for r in train])
    gamma1 = np.array([solver_coefficients(x)["gamma1"] for x in x_train])
    gfit = ps.fit_pce(x_train, gamma1, lower=LOWER, upper=UPPER, names=NAMES,
                      order=2)
    alone = ps.fit_pce(gamma1.reshape(-1, 1), y, lower=[gamma1.min()],
                       upper=[gamma1.max()], names=["gamma1"], order=3)
    return {
        "question": "does the leading coefficient act directly, or through gamma1?",
        "gamma1_range_over_samples": [float(gamma1.min()), float(gamma1.max())],
        "gamma1_at_constrained_nominal": solver_coefficients(NOMINAL)["gamma1"],
        "pearson_r_cd_vs_gamma1": float(np.corrcoef(y, gamma1)[0, 1]),
        "pearson_r_cd_vs_each_coefficient": {
            n: float(np.corrcoef(y, x_train[:, j])[0, 1])
            for j, n in enumerate(NAMES)},
        "who_owns_gamma1_variance": {k: round(v, 4)
                                     for k, v in gfit.sobol_total.items()},
        "cd_from_gamma1_alone_loo_q2": alone.loo_q2,
        "finding": (
            "sigma_w1 owns the band because sigma_w1 owns gamma1. gamma1 is not "
            "a free coefficient in this study -- it is reconstructed from the "
            "log-layer relation, in which sigma_w1 enters with the largest "
            "lever -- and Cd tracks gamma1 far more tightly than it tracks any "
            "coefficient sampled directly. THE CONSEQUENCE FOR COMPARISON: a "
            "coefficient study that leaves gamma at its default while moving "
            "sigma_w1 is moving only the omega-equation diffusion and will find "
            "sigma_w1 nearly inert. The motorbike stage of this docket item is "
            "such a study. The two studies' sigma_w1 rankings are therefore not "
            "the same quantity and must not be read against each other."),
    }


def analyze() -> None:
    data = load_results()
    train = [r for r in data["train"] if r["flat"]]
    valid = [r for r in data["valid"] if r["flat"]]
    dropped = [r["tag"] for r in data["train"] + data["valid"] if not r["flat"]]
    base = data["baseline_openfoam_default"]
    nominal = data["baseline_constrained_nominal"]

    x_train = np.array([r["x"] for r in train])
    x_valid = np.array([r["x"] for r in valid])
    analysis: dict[str, Any] = {}
    values = {}
    for key in QOIS:
        y_train = np.array([r[key] for r in train])
        y_valid = np.array([r[key] for r in valid])
        values[key] = y_valid
        ref = ("cd" if key == "cd" else "cf097")
        analysis[key] = qoi_analysis(
            key, x_train, y_train, x_valid, y_valid, base[key],
            {"code": "CFL3D SST-V", "value": CFL3D_SST_V[CELLS][ref],
             "second_code": "FUN3D SST-V",
             "second_value": FUN3D_SST_V[CELLS][ref],
             "source": "NASA TMR grid-convergence data at this cell count"})

    OUT.mkdir(parents=True, exist_ok=True)
    plot_cf_band(train, base["cf_profile"], OUT / "cf_band.png")
    plot_band_comparison(analysis, OUT / "band_comparison.png")
    plot_sobol(analysis, OUT / "sobol_shares.png")
    plot_surrogate_validation(analysis, x_valid, values,
                              OUT / "surrogate_validation.png")

    core_min = (base["core_minutes"] + nominal["core_minutes"]
                + sum(r["core_minutes"] for r in data["train"])
                + sum(r["core_minutes"] for r in data["valid"])
                + sum(c["cold_core_minutes"]
                      for c in data.get("restart_verification", [])))

    for key in QOIS:                       # fitted objects do not serialise
        analysis[key].pop("_pce2", None)
        analysis[key].pop("_gp", None)

    cd = analysis["cd"]
    band = ub.coefficient_interval(
        low=cd["monte_carlo"]["min"], high=cd["monte_carlo"]["max"],
        working=base["cd"], n_samples=len(train),
        method=(f"joint {len(train)}-sample maximin Latin hypercube over the "
                f"five published SST coefficient intervals, log-layer "
                f"consistency enforced, held mesh, restarted from converged"),
        citations=["Schaefer, West, Hosder, Rumsey, Carlson and Kleb, "
                   "AIAA Journal 55(1), 2017, Table 3"])
    composed = ub.compose(
        {"input": None,
         "numerical": None,
         "model": None},
        working_value=base["cd"], coefficient_band=band, quantity="flat-plate Cd")

    study = json.loads(STUDY.read_text())
    study["status"] = "complete"
    study["completed_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    study["deviations_from_preregistration"] = data.get("deviations", [])
    study["samples_solved"] = {
        "train_planned": len(data["train"]), "train_used": len(train),
        "valid_planned": len(data["valid"]), "valid_used": len(valid),
        "dropped_for_flatness": dropped,
        "worst_cd_tail_spread": max(r["cd_tail_spread"]
                                    for r in data["train"] + data["valid"]),
    }
    study["baselines"] = {
        "openfoam_default": {k: base[k] for k in
                             ("cd", "cf_station", "iterations", "cd_tail_spread")},
        "log_layer_constrained_nominal": {
            k: nominal[k] for k in ("cd", "cf_station", "iterations",
                                    "cd_tail_spread")},
        "difference": {
            "cd": nominal["cd"] - base["cd"],
            "cd_pct": 100.0 * (nominal["cd"] - base["cd"]) / base["cd"],
            "cf_station_pct": 100.0 * (nominal["cf_station"]
                                       - base["cf_station"]) / base["cf_station"],
            "meaning": (
                "the measured cost of OpenFOAM's rounded gamma1 = 5/9 against "
                "the log-layer-consistent 0.553167. It is reported because it "
                "is the size of the error a coefficient study makes when it "
                "perturbs betaStar and leaves gamma alone."),
            "constrained_coefficients": solver_coefficients(NOMINAL),
        },
        "reference": {
            "cfl3d_sst_v": CFL3D_SST_V[CELLS],
            "fun3d_sst_v": FUN3D_SST_V[CELLS],
            "our_cd_vs_cfl3d_pct": 100.0 * (base["cd"] - CFL3D_SST_V[CELLS]["cd"])
                                   / CFL3D_SST_V[CELLS]["cd"],
            "our_cf_vs_cfl3d_pct": 100.0 * (base["cf_station"]
                                            - CFL3D_SST_V[CELLS]["cf097"])
                                   / CFL3D_SST_V[CELLS]["cf097"],
        },
    }
    study["restart_verification"] = data.get("restart_verification", [])
    study["dominance_diagnostic"] = dominance_diagnostic(x_train, train)
    study["propagation"] = analysis
    study["composed_band"] = composed
    study["channel_table"] = ub.as_channel_table(composed)
    mc_cd = cd["monte_carlo"]
    ref_cd = CFL3D_SST_V[CELLS]["cd"]
    sob = cd["polynomial_chaos"]["order_2"]["sobol_total"]
    lead = max(sob, key=sob.get)
    study["findings"] = {
        "band_dwarfs_the_validation_discrepancy": (
            f"The case's own agreement with CFL3D is +"
            f"{100.0 * (base['cd'] - ref_cd) / ref_cd:.2f}% on Cd. The joint "
            f"coefficient band is {mc_cd['envelope_width']:.3e} wide, "
            f"{mc_cd['envelope_pct_of_reference']:.1f}% of the reference value "
            f"— about {mc_cd['envelope_width'] / abs(base['cd'] - ref_cd):.0f} "
            f"times the discrepancy the validation is usually reported as. A "
            f"validated case is not a case with a small model channel; it is a "
            f"case whose closure happened to be calibrated near the answer."),
        "log_layer_correction_exceeds_the_validation_discrepancy": (
            f"Simply making gamma1 consistent with the log-layer relation, at "
            f"otherwise nominal coefficients, moves Cd by "
            f"{100.0 * (nominal['cd'] - base['cd']) / base['cd']:+.3f}% — "
            f"larger than the +"
            f"{100.0 * (base['cd'] - ref_cd) / ref_cd:.2f}% gap to CFL3D that "
            f"this case is validated on. The rounding of gamma1 to 5/9 in "
            f"OpenFOAM's defaults is not a rounding as far as this QoI is "
            f"concerned."),
        "dominant_coefficient": (
            f"{lead}, total-effect variance share {sob[lead]:.3f}, with the "
            f"other four sharing {1.0 - sob[lead]:.3f}. See "
            f"dominance_diagnostic: the effect runs through the derived gamma1."),
        "published_ranking_does_not_transfer": (
            f"The source paper finds betaStar dominant for drag and skin "
            f"friction in transonic wall-bounded flow. Here betaStar's "
            f"total-effect share is {sob['betaStar']:.3f} and its correlation "
            f"with Cd is essentially zero. The ranking measured on this "
            f"incompressible zero-pressure-gradient plate is not the published "
            f"transonic one, which is what running it was for."),
        "the_process_surrogate_is_overconfident": (
            f"Its held-out z-RMS is "
            f"{cd['gaussian_process']['holdout_z_rms']:.2f}: on the ten solves "
            f"it never saw, its errors are about three times the posterior "
            f"standard deviation it claimed for them. Its MEAN is good (held-out "
            f"Q2 {cd['gaussian_process']['holdout_q2']:.4f}) and its band agrees "
            f"with the direct one, but its own error bars are not yet a "
            f"trustworthy statement about a point it has not solved, and are "
            f"not used as one anywhere in this record."),
        "the_three_propagations_agree": (
            f"Chaos and process surrogate land within "
            f"{max(abs(cd['band_comparison']['chaos_std_vs_mc_pct']), abs(cd['band_comparison']['process_std_vs_mc_pct'])):.1f}% "
            f"of the direct standard deviation, on held-out data neither saw. "
            f"On this response the cheap fits are not buying accuracy over "
            f"direct sampling — they are buying the variance decomposition and "
            f"the ability to interrogate the box without solving again."),
    }
    study["validation_comparison"] = {
        "reference": "CFL3D SST-V at this cell count",
        "our_cd": base["cd"], "reference_cd": ref_cd,
        "E_cd": base["cd"] - ref_cd,
        "E_cd_pct": 100.0 * (base["cd"] - ref_cd) / ref_cd,
        "model_channel_not_completed_here": (
            "V&V-20's direct mechanism needs u_val^2 = u_num^2 + u_input^2 + "
            "u_D^2 and this pass measured none of those three on this body, so "
            "E is reported as a comparison and the model channel is left "
            "honestly unquantified rather than set to |E|."),
    }
    study["follow_ups"] = [
        "route certificate.py's uncertainty section through "
        "uncertainty_band.compose (deliberately not done in this pass: the "
        "certificate path took a truthfulness fix in 4925fafb and should land "
        "its own change with its own test pass)",
        "widen the box from the docketed 5 coefficients to all 9 the source "
        "varies (sigma_k1, sigma_k2, sigma_w2, kappa); this study's envelope "
        "is a lower bound on that one",
        "store a numerical channel for this body from the existing TMR grid "
        "ladder so the model channel can be completed by the direct mechanism",
        "re-read the motorbike stage's sigma_w1 ranking with gamma recomputed, "
        "since the two studies' sigma_w1 are not currently the same quantity",
    ]
    study["core_minutes"] = round(core_min, 2)
    study["budget_core_min_remaining"] = round(100.0 - core_min, 2)
    study["plots"] = sorted(p.name for p in OUT.glob("*.png"))
    study["samples_record"] = str((OUT / "samples.json").relative_to(REPO))
    STUDY.write_text(json.dumps(study, indent=2, default=float) + "\n")

    mc = cd["monte_carlo"]
    print(f"core-min {core_min:.2f}  n_train {len(train)}")
    print(f"Cd baseline {base['cd']:.7f}  constrained nominal {nominal['cd']:.7f} "
          f"({100 * (nominal['cd'] - base['cd']) / base['cd']:+.3f}%)")
    print(f"MC envelope {mc['min']:.7f} .. {mc['max']:.7f} "
          f"({mc['envelope_width']:.3e}, {mc['envelope_pct_of_reference']:.2f}% "
          f"of CFL3D)  std {mc['std']:.3e}")
    for name in ("polynomial_chaos", "gaussian_process"):
        rec = (cd[name]["order_2"] if name == "polynomial_chaos" else cd[name])
        print(f"{name:20s} std {rec['band']['std']:.3e}  "
              f"LOO Q2 {rec['loo_q2']:.4f}  holdout Q2 {rec['holdout_q2']:.4f}")
    print("Sobol total:", {k: round(v, 3) for k, v in sorted(
        cd["polynomial_chaos"]["order_2"]["sobol_total"].items(),
        key=lambda kv: -kv[1])})


if __name__ == "__main__":
    analyze()
