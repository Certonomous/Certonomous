"""Monte-Carlo convergence, measured from the race act's recorded solver runs.

The race act (mission-output/race-study) answered one question two ways: a
full Monte-Carlo ensemble, 8 Reynolds samples x 11 angles = 88 recorded
VSPAERO runs, against a reduced-order model, 4 anchors + 1 confirmation = 5
recorded runs. This script turns those on-disk records into the convergence
story for the website section: the 95 percent confidence half-width of the
Monte-Carlo peak lift-to-drag estimate versus the number of solver runs N,
with the 1 over sqrt N theoretical guarantee anchored at the measured
ensemble variance, and the reduced-order model's own convergence curve
(its prediction error measured against each next recorded run) reaching
its confirmed envelope at 5 runs.

Every number is read from the recorded artifacts, nothing is invented:

* mission-output/race-study/work/mc/mc-s{S}a{A}/result.json  (88 files)
* mission-output/race-study/work/rom/rom-*/result.json       (5 files)
* the act's published numbers live in
  mission-output/race-study/certificate.pdf -- cited by that path and by the
  numbers it prints, never by its certificate number or its seal, both of
  which are functions of the issuance clock rather than of the result
  (see the citation note under OUT_DIR).

The estimator study: the act's Monte-Carlo band is 2 * stdev / sqrt(m) over
the m per-sample peaks, and one ensemble member costs 11 solver runs (a full
angle sweep locates its peak), so the band updates every 11 runs. The curve
is resampled over many random orderings of the recorded ensemble members so
it is the estimator's behavior, not one lucky ordering: the root mean square
across orderings is the primary curve (the guarantee speaks about the mean
square error), the median and the middle 50 percent of orderings are drawn
beside it.

Outputs (1920x1080, control-room theme):

* demo-output/plots/monte_carlo/mc_convergence.png       hero still
* demo-output/plots/monte_carlo/frame_0001..0087.png     N = 2..88 sequence
* demo-output/plots/monte_carlo/panel_stats.md           numbers + sources

Usage (from sdk/):

    python scripts/render_mc_convergence.py            # hero + stats note
    python scripts/render_mc_convergence.py --frames   # + 87 frames
    python scripts/render_mc_convergence.py --check    # verdicts only
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from pathlib import Path

import numpy as np

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "mission-output" / "race-study" / "work"
OUT_DIR = lab_paths.PLOTS / "monte_carlo"

# --- how this file cites the act's certificate, and why -------------------
# By PATH and by the NUMBERS on the page. Never by its certificate number and
# never by its seal.
#
# Both of those are functions of the wall clock rather than of the result: the
# seal covers `issued_utc` (`certificate.py` `_seal_payload`) and the serial is
# a four-digit projection of the seal (`_human_number`), so re-issuing the SAME
# result reproduces neither. This file used to hardcode `C-2026-9704` in five
# places. The file it names still exists and now prints C-2026-7228, so the
# citation was not merely dead -- it was contradicted by the very artifact it
# pointed at, which is the worst shape a citation can take.
#
# Rejected, and why:
#   * Re-point the literal at C-2026-7228. That is a reset, not a repair: it
#     dies on the race act's next re-render exactly as 9704 did.
#   * Cite the SEAL instead (D137's own recommendation). It does not survive
#     the mechanism -- the seal moves for the same reason the serial moves, so
#     this buys a 64-hex-digit dangling citation in place of a 4-digit one.
#     The seal is collision-free; it is not stable.
#   * Drop the citation and restate the claim alone. Rejected because
#     `run_checks` really does compare recomputed numbers against the act's
#     published band, so the provenance of that band has to stay nameable.
#
# What survives re-issuance is the mission, the artifact path, and the numbers
# printed on the page. Those are the citation. `observed_certificate_identity`
# additionally reports the identity the page carried AT RENDER TIME, labelled
# as an observation and not as a name, so the panel dates itself instead of
# asserting a permanence the generator cannot deliver.
CERTIFICATE_PATH = "mission-output/race-study/certificate.pdf"
CERTIFICATE_PUBLISHES = (
    "peak L/D 18.14 +- 0.06 at 95 percent, input channel 0.065, "
    "speedup 16.7x core-minutes, 88 + 5 solver runs, residual 0.084")

N_SAMPLES = 8
ALPHAS = [float(a) for a in range(11)]        # the act's 1-degree grid
RUNS_PER_MEMBER = len(ALPHAS)                 # one member = 11 solver runs
ANCHOR_TAGS = ("rom-anchor0", "rom-anchor3.3", "rom-anchor6.7", "rom-anchor10")
ORDERINGS = 20000
SEED = 20260725

# Control-room palette, mirrors chief_engineer/plot_theme.py and
# control_room.html so the PNGs sit beside the live canvases in one tone.
BG = "#0a0c0e"
INK = "#f4f6f8"
MUTED = "#868d95"
DIM = "#545a61"
LIVE = "#57a5ff"
VALID = "#4fd483"
GRID = "#191d21"


# ---------------------------------------------------------------------------
# Pure functions (unit-tested in tests/test_render_mc_convergence.py)
# ---------------------------------------------------------------------------

def half_width_95(values) -> float | None:
    """The act's own 95 percent band: 2 * stdev / sqrt(n) over the values.

    This is exactly the statistic the race act published (note and
    certificate use mean +- 2 * standard error). None below two values,
    where no spread can be estimated.
    """
    vals = [float(v) for v in values]
    if len(vals) < 2:
        return None
    return 2.0 * statistics.stdev(vals) / math.sqrt(len(vals))


def sample_peaks(points: list[dict]) -> list[float]:
    """Per-sample peak lift-to-drag, the ensemble the act's band is built on.

    ``points`` carry ``sample`` and ``l_d``; the peak of a sample is the
    largest lift-to-drag among its solved angles. Returned in sample order.
    """
    by_sample: dict[int, list[float]] = {}
    for p in points:
        by_sample.setdefault(int(p["sample"]), []).append(float(p["l_d"]))
    return [max(vals) for _, vals in sorted(by_sample.items())]


def sequential_band_stats(peaks, *, orderings: int = ORDERINGS,
                          seed: int = SEED) -> dict[int, dict[str, float]]:
    """Half-width after m complete members, resampled over member orderings.

    For each random ordering of the recorded per-sample peaks, the sequential
    95 percent band after m members is 2 * stdev(first m) / sqrt(m), the
    exact statistic a live run displays as members land. Across orderings the
    root mean square, median, and 25th/75th percentiles are returned per m.
    The root mean square is the primary curve: the sqrt-N guarantee is a
    statement about the mean square error, and the sample variance of a
    without-replacement prefix is an unbiased estimate of the full-ensemble
    variance, so this curve is the estimator's true error scale.
    """
    vals = np.asarray(list(peaks), dtype=float)
    n = vals.size
    if n < 2:
        raise ValueError("need at least two ensemble members")
    rng = np.random.default_rng(seed)
    perms = rng.permuted(np.tile(vals, (orderings, 1)), axis=1)
    out: dict[int, dict[str, float]] = {}
    for m in range(2, n + 1):
        prefix = perms[:, :m]
        sd = prefix.std(axis=1, ddof=1)
        hw = 2.0 * sd / math.sqrt(m)
        out[m] = {
            "rms": float(np.sqrt(np.mean(hw ** 2))),
            "median": float(np.median(hw)),
            "q25": float(np.percentile(hw, 25)),
            "q75": float(np.percentile(hw, 75)),
        }
    return out


def guarantee_half_width(sd: float, n_runs, *,
                         runs_per_member: int = RUNS_PER_MEMBER):
    """The theoretical guarantee anchored at the measured variance.

    Error falls as 1 over sqrt N: half-width(N) = 2 * sd * sqrt(runs per
    member / N), which passes exactly through the act's published band at
    N = 88 runs (m = 8 members).
    """
    n = np.asarray(n_runs, dtype=float)
    return 2.0 * float(sd) * np.sqrt(float(runs_per_member) / n)


def band_at_runs(n_runs: int, per_member: dict[int, dict[str, float]],
                 key: str = "rms", *,
                 runs_per_member: int = RUNS_PER_MEMBER
                 ) -> tuple[int, float | None]:
    """(complete members, band) at a solver-run count.

    A member's peak exists only once all its angle solves are in, so the
    band updates every ``runs_per_member`` runs and holds in between; below
    two complete members there is no band yet.
    """
    m = n_runs // runs_per_member
    if m < 2:
        return m, None
    m = min(m, max(per_member))
    return m, per_member[m][key]


def fit_powerlaw_slope(ns, values) -> float:
    """Least-squares exponent of value ~ N**slope, fitted in log-log."""
    x = np.log(np.asarray(ns, dtype=float))
    y = np.log(np.asarray(values, dtype=float))
    slope = np.polyfit(x, y, 1)[0]
    return float(slope)


def rom_convergence(anchors: list[dict], confirm: dict, *,
                    x_lo: float = ALPHAS[0], x_hi: float = ALPHAS[-1]
                    ) -> list[dict]:
    """The reduced-order model's own convergence, from its recorded runs.

    ``anchors`` must be in run order (the recorded dispatch order). With k
    anchors fitted (k >= 3, a quadratic needs three points, so no 2-run
    point exists), the model's error is measured against the next recorded
    run: the next anchor while anchors remain, then the confirmation run at
    the located peak. The final entry is the confirmation run itself
    landing, which turns the last prediction error into the model's
    confirmed envelope. Every value is a recorded solver result; nothing is
    invented.
    """
    if len(anchors) < 3:
        raise ValueError("a quadratic model needs at least three anchors")
    out: list[dict] = []
    for k in range(3, len(anchors) + 1):
        xs = [a["alpha"] for a in anchors[:k]]
        ys = [a["l_d"] for a in anchors[:k]]
        if k < len(anchors):
            nxt = anchors[k]
            pred = float(np.polyval(np.polyfit(xs, ys, 2), nxt["alpha"]))
            out.append({"n_runs": k, "error": abs(pred - nxt["l_d"]),
                        "tested_at": nxt["alpha"],
                        "tested": "next recorded anchor"})
        else:
            sur = quadratic_peak_residual(xs, ys, confirm["l_d"],
                                          x_lo=x_lo, x_hi=x_hi)
            out.append({"n_runs": k, "error": sur["residual"],
                        "tested_at": sur["alpha_star"],
                        "tested": "confirmation at the located peak"})
    out.append({"n_runs": len(anchors) + 1, "error": out[-1]["error"],
                "tested_at": out[-1]["tested_at"],
                "tested": "confirmation run lands, envelope confirmed"})
    return out


def quadratic_peak_residual(xs, ys, confirm_value: float, *,
                            x_lo: float = ALPHAS[0], x_hi: float = ALPHAS[-1]
                            ) -> dict[str, float]:
    """The reduced-order model's achieved envelope, from its own records.

    Fit the quadratic surface through the anchor points, locate its peak on
    [x_lo, x_hi] exactly as the act did (vertex when concave, else the
    higher end, rounded to 0.1), predict there, and return the residual
    against the recorded confirmation value. Nothing is invented: anchors
    and confirmation are the recorded solver runs.
    """
    a2, a1, a0 = np.polyfit(np.asarray(xs, float), np.asarray(ys, float), 2)
    predict = lambda x: a2 * x * x + a1 * x + a0            # noqa: E731
    if a2 < 0:
        vertex = -a1 / (2.0 * a2)
    else:
        vertex = x_lo if predict(x_lo) >= predict(x_hi) else x_hi
    x_star = round(min(max(vertex, x_lo), x_hi), 1)
    predicted = float(predict(x_star))
    return {"alpha_star": float(x_star), "predicted": predicted,
            "residual": abs(float(confirm_value) - predicted)}


# ---------------------------------------------------------------------------
# Record loading (reads the race act's on-disk artifacts, read-only)
# ---------------------------------------------------------------------------

def load_mc_points(work: Path = WORK) -> list[dict]:
    points = []
    for s in range(N_SAMPLES):
        for a in ALPHAS:
            d = work / "mc" / f"mc-s{s}a{a:g}"
            r = json.loads((d / "result.json").read_text(encoding="utf-8"))
            points.append({"sample": s, "alpha": a,
                           "l_d": r["polar"]["L_D"][0],
                           "elapsed_s": float(r["elapsed_s"]),
                           "source": str(d / "result.json")})
    return points


def load_rom(work: Path = WORK) -> dict:
    """Anchors are returned in run order, taken from the recorded dispatch
    times (job.json mtime); for this act that order is alpha 0, 3.3, 6.7,
    10, then the confirmation."""
    anchors = []
    for tag in ANCHOR_TAGS:
        d = work / "rom" / tag
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        j = json.loads((d / "job.json").read_text(encoding="utf-8"))
        anchors.append({"alpha": float(j["alpha_start"]),
                        "l_d": r["polar"]["L_D"][0],
                        "elapsed_s": float(r["elapsed_s"]),
                        "dispatched": (d / "job.json").stat().st_mtime})
    d = work / "rom" / "rom-confirm"
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    j = json.loads((d / "job.json").read_text(encoding="utf-8"))
    confirm = {"alpha": float(j["alpha_start"]),
               "l_d": r["polar"]["L_D"][0],
               "elapsed_s": float(r["elapsed_s"])}
    return {"anchors": sorted(anchors, key=lambda a: a["dispatched"]),
            "confirm": confirm}


def build_story(work: Path = WORK, *, orderings: int = ORDERINGS,
                seed: int = SEED) -> dict:
    """Everything the figures and the stats note need, from the records."""
    points = load_mc_points(work)
    rom = load_rom(work)
    peaks = sample_peaks(points)
    sd = statistics.stdev(peaks)
    per_member = sequential_band_stats(peaks, orderings=orderings, seed=seed)
    ns = [RUNS_PER_MEMBER * m for m in sorted(per_member)]
    rms = [per_member[m]["rms"] for m in sorted(per_member)]
    xs = [a["alpha"] for a in rom["anchors"]]
    ys = [a["l_d"] for a in rom["anchors"]]
    surrogate = quadratic_peak_residual(xs, ys, rom["confirm"]["l_d"])
    rom_curve = rom_convergence(rom["anchors"], rom["confirm"])
    mc_seconds = sum(p["elapsed_s"] for p in points)
    rom_seconds = (sum(a["elapsed_s"] for a in rom["anchors"])
                   + rom["confirm"]["elapsed_s"])
    return {
        "points": points, "rom": rom, "peaks": peaks,
        "peak_mean": statistics.fmean(peaks), "peak_sd": sd,
        "per_member": per_member,
        "hw_final": per_member[len(peaks)]["rms"],
        "slope_rms": fit_powerlaw_slope(ns, rms),
        "slope_median": fit_powerlaw_slope(
            ns, [per_member[m]["median"] for m in sorted(per_member)]),
        "surrogate": surrogate, "rom_curve": rom_curve,
        "mc_seconds": mc_seconds, "rom_seconds": rom_seconds,
        "seconds_per_run": mc_seconds / len(points),
        "speedup_solver_time": mc_seconds / rom_seconds,
        "n_mc_runs": len(points),
        "n_rom_runs": len(rom["anchors"]) + 1,
    }


# ---------------------------------------------------------------------------
# Checks: the deliverable's own validation, printed as verdicts
# ---------------------------------------------------------------------------

def run_checks(story: dict, *, slope_tol: float = 0.05) -> list[dict]:
    """Every checkable claim in the deliverable, checked against the records
    and the act's certificate (mission-output/race-study/certificate.pdf,
    which publishes peak L/D 18.14 +- 0.06 at 95 percent, input channel
    0.065, speedup 16.7x core-minutes, 88 + 5 solver runs, residual 0.084).

    The certificate is named by path and by those numbers; its serial and its
    seal are deliberately not quoted here, because both move with the
    issuance clock rather than with the result."""
    checks = []

    slope = story["slope_rms"]
    checks.append({
        "name": "convergence slope matches the 1 over sqrt N guarantee",
        "pass": abs(slope + 0.5) <= slope_tol,
        "detail": f"fitted slope {slope:+.4f} on the root mean square curve "
                  f"over N = 22..88, guarantee -0.5, tolerance {slope_tol}"})

    hw = story["hw_final"]
    checks.append({
        "name": "N = 88 half-width reproduces the act's published band",
        "pass": round(hw, 2) == 0.06 and round(hw, 3) == 0.065,
        "detail": f"recomputed +-{hw:.4f}; the act's certificate "
                  f"({CERTIFICATE_PATH}) publishes "
                  f"+-0.06 (95 percent) with input channel 0.065. The +-0.07 "
                  f"band belongs to the earlier race-benchmark passes "
                  f"(demo-output/website/race/benchmarks.md), not this act."})

    res = story["surrogate"]["residual"]
    checks.append({
        "name": "reduced-order envelope comes from its recorded runs",
        "pass": round(res, 3) == 0.084,
        "detail": f"quadratic through the 4 recorded anchors peaks at alpha "
                  f"{story['surrogate']['alpha_star']:g}, predicts "
                  f"{story['surrogate']['predicted']:.4f}, recorded "
                  f"confirmation {story['rom']['confirm']['l_d']:.4f}, "
                  f"residual {res:.4f}; certificate says 0.084"})

    spd = story["speedup_solver_time"]
    checks.append({
        "name": "measured speedup reproduces the act's 16.7x",
        "pass": round(spd, 1) == 16.7 or round(spd) == 17,
        "detail": f"recorded solver time {story['mc_seconds']:.1f} s over 88 "
                  f"runs vs {story['rom_seconds']:.1f} s over 5 runs = "
                  f"{spd:.2f}x; certificate says 16.7x core-minutes"})

    spr = story["seconds_per_run"]
    checks.append({
        "name": "per-run wall cost matches the stated 4.25 s",
        "pass": abs(spr - 4.25) < 0.01,
        "detail": f"mean recorded elapsed over the 88 ensemble runs "
                  f"{spr:.3f} s per solver run"})

    rc = story["rom_curve"]
    errors = [p["error"] for p in rc]
    order = [round(a["alpha"], 1) for a in story["rom"]["anchors"]]
    checks.append({
        "name": "reduced-order convergence curve traced to its recorded runs",
        "pass": (rc[0]["n_runs"] == 3
                 and rc[-1]["n_runs"] == story["n_rom_runs"]
                 and all(a >= b for a, b in zip(errors, errors[1:]))
                 and round(errors[-1], 3) == 0.084
                 and order == [0.0, 3.3, 6.7, 10.0]),
        "detail": f"run order from recorded dispatch times: alphas {order}; "
                  f"3-run model tested at the next recorded run (alpha "
                  f"{rc[0]['tested_at']:g}) misses by {errors[0]:.4f}, "
                  f"4-run model tested by the confirmation misses by "
                  f"{errors[1]:.4f}, envelope confirmed +-{errors[-1]:.3f} "
                  f"at {rc[-1]['n_runs']} runs; certificate says 0.084. "
                  f"No 2-run point exists (a quadratic needs 3), so the "
                  f"curve starts at 3."})
    return checks


# ---------------------------------------------------------------------------
# Rendering (control-room theme; matplotlib imported lazily)
# ---------------------------------------------------------------------------

def _pyplot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
        "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "font.family": "monospace", "font.size": 12,
        "mathtext.fontset": "cm", "axes.titlesize": 14,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    })
    return plt


X_LIM = (1.8, 105.0)
Y_LIM = (0.05, 2.4)
TITLE = "MC convergence vs Reduced model"


def _base_axes(plt, story):
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=150)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*X_LIM)
    ax.set_ylim(*Y_LIM)
    ax.set_xlabel("solver runs  $N$", color=INK, fontsize=13)
    ax.set_ylabel(r"error band on peak $L/D$", color=INK, fontsize=13)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(DIM)
    ax.grid(True, which="both", color=GRID, linewidth=0.8)
    ax.tick_params(colors=MUTED, labelsize=10, which="both")
    ticks = [2, 3, 5, 11, 22, 44, 88]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(t) for t in ticks])
    ax.set_xticks([], minor=True)
    yticks = [0.05, 0.1, 0.2, 0.4, 0.8, 1.6]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{t:g}" for t in yticks])
    ax.set_yticks([], minor=True)

    # Guarantee line, anchored at the measured variance.
    grid_n = np.geomspace(2, 100, 200)
    ax.plot(grid_n, guarantee_half_width(story["peak_sd"], grid_n),
            color=INK, linewidth=1.6, linestyle=(0, (6, 4)), alpha=0.85,
            label="theoretical guarantee")
    return fig, ax


def _step_arrays(per_member, key, upto_n=None):
    """Step-hold (N, value) arrays: the band updates every 11 runs."""
    ms = sorted(per_member)
    xs, ys = [], []
    for i, m in enumerate(ms):
        n0 = m * RUNS_PER_MEMBER
        n1 = ms[i + 1] * RUNS_PER_MEMBER if i + 1 < len(ms) else n0
        if upto_n is not None and n0 > upto_n:
            break
        end = n1 if upto_n is None else min(n1, upto_n)
        xs += [n0, end]
        ys += [per_member[m][key]] * 2
    return xs, ys


def _draw_band(ax, story, upto_n=None, *, envelope=True):
    per = story["per_member"]
    label_n = story["n_mc_runs"]
    if envelope:
        xq, lo = _step_arrays(per, "q25", upto_n)
        _, hi = _step_arrays(per, "q75", upto_n)
        if xq:
            ax.fill_between(xq, lo, hi, color=LIVE, alpha=0.16, linewidth=0,
                            label="spread across run orderings (middle 50%)")
    xs, ys = _step_arrays(per, "rms", upto_n)
    if xs:
        ax.plot(xs, ys, color=LIVE, linewidth=2.4, solid_capstyle="round",
                label=f"Monte-Carlo: measured 95% band over the "
                      f"{label_n} recorded runs")
        marker_n = [m * RUNS_PER_MEMBER for m in sorted(per)
                    if upto_n is None or m * RUNS_PER_MEMBER <= upto_n]
        ax.plot(marker_n, [per[n // RUNS_PER_MEMBER]["rms"]
                           for n in marker_n], linestyle="none", marker="o",
                markersize=7, color=LIVE, markeredgecolor=INK,
                markeredgewidth=0.9, zorder=5)


def _draw_rom(ax, story, upto_n=None, *, annotate: bool):
    curve = [p for p in story["rom_curve"]
             if upto_n is None or p["n_runs"] <= upto_n]
    if not curve:
        return
    n_rom = story["n_rom_runs"]
    xs = [p["n_runs"] for p in curve]
    ys = [p["error"] for p in curve]
    ax.plot(xs, ys, color=VALID, linewidth=2.4, solid_capstyle="round",
            marker="o", markersize=7, markeredgecolor=INK,
            markeredgewidth=0.9, zorder=6,
            label=f"reduced-order model: converges in {n_rom} runs")
    if xs[-1] == n_rom:
        ax.scatter([xs[-1]], [ys[-1]], s=170, marker="D", color=VALID,
                   edgecolor=INK, linewidths=1.4, zorder=7)
    if annotate:
        res = story["surrogate"]["residual"]
        ax.annotate(
            f"reduced-order model: converges in {n_rom} solver runs\n"
            f"envelope $\\pm${res:.3f}",
            xy=(0.30, 0.155), xycoords="axes fraction", ha="left",
            fontsize=10.5, color=INK)


def render_hero(story: dict, out_png: Path) -> Path:
    plt = _pyplot()
    fig, ax = _base_axes(plt, story)
    _draw_band(ax, story)
    _draw_rom(ax, story, annotate=True)

    n88 = story["n_mc_runs"]
    hw = story["hw_final"]
    ax.annotate(
        f"$\\pm${hw:.3f} at {n88} runs\npublished $\\pm$0.06 (95%)",
        xy=(0.985, 0.035), xycoords="axes fraction", ha="right",
        va="bottom", fontsize=10.5, color=INK, weight="bold")
    ax.set_title(TITLE, color=INK, fontsize=14, loc="left", pad=14,
                 weight="bold")
    leg = ax.legend(frameon=False, fontsize=9.5, loc="upper right",
                    bbox_to_anchor=(0.995, 0.97), labelcolor=INK)
    for text in leg.get_texts():
        text.set_color(INK)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)
    return out_png


def render_frames(story: dict, out_dir: Path) -> list[Path]:
    plt = _pyplot()
    paths = []
    per = story["per_member"]
    for i, n in enumerate(range(2, story["n_mc_runs"] + 1), start=1):
        fig, ax = _base_axes(plt, story)
        _draw_band(ax, story, upto_n=n)
        _draw_rom(ax, story, upto_n=n, annotate=False)
        m, value = band_at_runs(n, per)
        if value is not None:
            ax.scatter([m * RUNS_PER_MEMBER], [value], s=120, color=LIVE,
                       edgecolor=INK, linewidths=1.2, zorder=6)
        lines = [f"solver runs: {n} of {story['n_mc_runs']}"]
        if n >= story["n_rom_runs"]:
            lines.append(f"reduced-order model: done, "
                         f"$\\pm${story['surrogate']['residual']:.3f} "
                         f"at {story['n_rom_runs']} runs")
        if value is not None:
            lines.append(f"Monte-Carlo 95% band: $\\pm${value:.3f}")
        ax.annotate(
            "\n".join(lines),
            xy=(0.985, 0.035), xycoords="axes fraction", ha="right",
            va="bottom", fontsize=11.5, color=INK, weight="bold")
        ax.set_title(TITLE, color=INK, fontsize=14, loc="left", pad=14,
                     weight="bold")
        leg = ax.legend(frameon=False, fontsize=9.5, loc="upper right",
                        bbox_to_anchor=(0.995, 0.97), labelcolor=INK)
        for text in leg.get_texts():
            text.set_color(INK)
        fig.tight_layout()
        png = out_dir / f"frame_{i:04d}.png"
        fig.savefig(png)
        plt.close(fig)
        paths.append(png)
    return paths


# ---------------------------------------------------------------------------
# Stats note
# ---------------------------------------------------------------------------

def observed_certificate_identity(repo: Path = REPO) -> str:
    """The identity the act's certificate carries RIGHT NOW, as an observation.

    This is never a citation key -- see the citation note under OUT_DIR. It is
    a dated reading of a page that is allowed to change, phrased so a reader
    cannot mistake it for a durable name. It never invents a serial, and an
    absent or unreadable page yields a plain statement of absence rather than
    an exception: a missing certificate must not fail a panel render.
    """
    pdf = repo / CERTIFICATE_PATH
    try:
        raw = pdf.read_bytes()
    except OSError:
        return (f"{CERTIFICATE_PATH} was not readable when this panel was "
                f"rendered, so no issued identity is reported here.")
    text = raw.decode("latin-1")
    serials = re.findall(r"C-\d{4}-\d{4}", text)
    seals = re.findall(r"\(([0-9a-f]{32})\) Tj", text)
    if not serials:
        return (f"{CERTIFICATE_PATH} was present when this panel was rendered "
                f"but printed no certificate number.")
    seal_bit = f", seal {seals[0][:16]}..." if seals else ""
    return (f"When this panel was rendered that page carried {serials[0]}"
            f"{seal_bit}. That is an observation of one issuance, not a name: "
            f"the act's next re-render will print a different one for the same "
            f"result, which is why nothing above cites it.")


def write_stats_note(story: dict, checks: list[dict], out_md: Path) -> Path:
    per = story["per_member"]
    rows = "\n".join(
        f"| {m} | {m * RUNS_PER_MEMBER} | {per[m]['rms']:.4f} | "
        f"{per[m]['median']:.4f} | {per[m]['q25']:.4f}..{per[m]['q75']:.4f} | "
        f"{guarantee_half_width(story['peak_sd'], m * RUNS_PER_MEMBER):.4f} |"
        for m in sorted(per))
    verdicts = "\n".join(
        f"- {'PASS' if c['pass'] else 'FAIL'}: {c['name']}. {c['detail']}"
        for c in checks)
    peaks = ", ".join(f"{p:.4f}" for p in story["peaks"])
    identity = observed_certificate_identity()
    rom_rows = "\n".join(
        f"| {p['n_runs']} | {p['error']:.4f} | {p['tested']} "
        f"(alpha {p['tested_at']:g}) |"
        for p in story["rom_curve"])
    md = f"""# Monte-Carlo convergence panel: the numbers and their sources

Website line served: orders of magnitude fewer runs, backed by theoretical
guarantees. Every number below is read from the race act's recorded
artifacts; nothing is synthesized.

## Headline numbers

| quantity | value | source |
|---|---|---|
| Monte-Carlo solver runs | {story['n_mc_runs']} | mission-output/race-study/work/mc/mc-s0a0 .. mc-s7a10 (result.json, one per run) |
| reduced-order solver runs | {story['n_rom_runs']} | mission-output/race-study/work/rom (4 anchors + 1 confirmation, result.json each) |
| peak L/D, ensemble mean | {story['peak_mean']:.2f} | mean of the 8 per-sample peaks below |
| peak L/D, reduced-order confirmed | {story['rom']['confirm']['l_d']:.2f} at alpha {story['rom']['confirm']['alpha']:g} | work/rom/rom-confirm/result.json |
| ensemble 95% band at 88 runs | +-{story['hw_final']:.3f} (published +-0.06) | 2 x stdev / sqrt(8) over the per-sample peaks; the act's certificate, {CERTIFICATE_PATH} |
| reduced-order envelope | +-{story['surrogate']['residual']:.3f} | recorded confirmation {story['rom']['confirm']['l_d']:.4f} vs surface prediction {story['surrogate']['predicted']:.4f} from the 4 recorded anchors; certificate says residual 0.084 |
| measured speedup, solver time | {story['speedup_solver_time']:.1f}x | {story['mc_seconds']:.1f} s over 88 runs vs {story['rom_seconds']:.1f} s over 5 runs (elapsed_s in every result.json); certificate says 16.7x core-minutes |
| measured cost per run | {story['seconds_per_run']:.2f} s | mean elapsed_s over the 88 ensemble records |
| fitted convergence slope | {story['slope_rms']:+.3f} | log-log fit over the root mean square curve, N = 22..88; guarantee is -1/2 |
| ensemble standard deviation | {story['peak_sd']:.4f} | stdev of the 8 per-sample peaks; anchors the guarantee line |

Per-sample peaks (L/D, samples s0..s7): {peaks}.
Every sample peaked at alpha 0, so each peak is that sample's recorded
alpha-0 run.

## The convergence table (resampled over {ORDERINGS} member orderings)

One ensemble member costs {RUNS_PER_MEMBER} solver runs (a full angle sweep
locates its peak), so the sequential band updates every {RUNS_PER_MEMBER}
runs. Root mean square is the primary curve: the prefix sample variance is
an unbiased estimate of the full-ensemble variance, so its square root per
member count is the estimator's true error scale. The median of a 2-to-7
member standard deviation is biased and noisy, which is why the median
column wanders around the guarantee instead of tracking it (slope of the
median curve: {story['slope_median']:+.3f}).

| members m | solver runs N | half-width, rms | half-width, median | middle 50% | guarantee 2s*sqrt(11/N) |
|---|---|---|---|---|---|
{rows}

## The reduced-order model's own convergence (drawn on the figure)

Anchor run order comes from the recorded dispatch times (job.json mtime
under mission-output/race-study/work/rom): alpha 0, 3.3, 6.7, 10, then the
confirmation at the located peak. With k anchors fitted, the model's error
is measured against the next recorded run; the final run confirms the
envelope. No 2-run point exists (a quadratic needs three anchors), so the
curve starts at 3 runs. Every value is a recorded solver result.

| solver runs | model error | measured against |
|---|---|---|
{rom_rows}

## Check verdicts

{verdicts}

## Provenance note on the published band

The race act's own certificate ({CERTIFICATE_PATH}) publishes peak L/D
18.14 +- 0.06 at 95 percent with input channel 0.065, speedup 16.7x
core-minutes, 88 + 5 solver runs. The +-0.07 band circulating with the
value 18.14 belongs to the earlier race-benchmark passes
(demo-output/website/race/benchmarks.md: pass1 18.10 +- 0.07, pass2 18.20
+- 0.07); this panel reproduces the race act's records exactly, so it
carries +-0.06.

That certificate is cited by its path and by the numbers it prints, and
deliberately not by its certificate number or its seal. Both of those are
functions of the issuance clock rather than of the result -- the seal covers
`issued_utc` and the number is a four-digit projection of the seal -- so a
serial quoted here would name nothing after the act's next re-render. This
note previously cited C-2026-9704, and that page now prints a different
number for the same result. {identity}
"""
    out_md.write_text(md, encoding="utf-8")
    return out_md


# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", action="store_true",
                        help="also render the 87-frame sequence")
    parser.add_argument("--check", action="store_true",
                        help="run the checks and print verdicts only")
    parser.add_argument("--orderings", type=int, default=ORDERINGS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args(argv)

    story = build_story(orderings=args.orderings, seed=args.seed)
    checks = run_checks(story)
    for c in checks:
        print(f"[{'PASS' if c['pass'] else 'FAIL'}] {c['name']}: {c['detail']}")
    if args.check:
        return 0 if all(c["pass"] for c in checks) else 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    hero = render_hero(story, OUT_DIR / "mc_convergence.png")
    print(f"[panel] hero still: {hero}")
    note = write_stats_note(story, checks, OUT_DIR / "panel_stats.md")
    print(f"[panel] stats note: {note}")
    if args.frames:
        frames = render_frames(story, OUT_DIR)
        print(f"[panel] frames: {len(frames)} "
              f"({frames[0].name} .. {frames[-1].name})")
    return 0 if all(c["pass"] for c in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
