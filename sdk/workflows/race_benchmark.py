"""Speed, certified — the race on the NACA 4412 finite wing, both paths real.

One question — where the wing's lift-to-drag peaks over alpha 0-10 degrees,
and what that peak is worth — answered two ways, every evaluation a real
VSPAERO solve, both wall clocks measured:

* **Full Monte-Carlo path** — an input-uncertainty ensemble over the chord
  Reynolds number; each sample sweeps alpha 0-10 as ELEVEN direct single-alpha
  solves. Nothing is interpolated: the peak is read off solved points only.
* **Reduced-order path** — four real anchor solves across the alpha range, a
  fitted quadratic response surface locating the peak, one real confirmation
  solve at the predicted alpha. Same objective, same tolerance (the peak
  located to half the Monte-Carlo grid step).

The wing is the curriculum body "NACA 4412 finite wing": chord 1 m, span 3 m,
untapered, unswept, chord Reynolds 1e6 (models/curriculum/naca4412_wing).
The two envelopes mean different things — input spread vs surrogate residual —
and every artifact says so. All times are measured on this machine with the
load context recorded, because the box is shared tonight.

    python -m workflows.race_benchmark pass1
"""

from __future__ import annotations

import json
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import OUT_ROOT, safe_print
from chief_engineer.compute_audit import audit
from chief_engineer.vspaero import VspAeroWingApi
from workflows.shape_optimization import _fit_quadratic, _predict

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

# The curriculum wing (models/curriculum/naca4412_wing/reference.yaml).
WING = {"span": 3.0, "area": 3.0, "sweep": 0.0, "taper": 1.0,
        "camber": 0.04, "camber_loc": 0.4, "thick_chord": 0.12}


def wing_section_name(wing: dict | None = None) -> str:
    """The four-digit NACA name this wing's OWN parameters spell.

    The section is set by three numbers the solver is handed — maximum
    camber, where it sits, and thickness — and a four-digit NACA name is
    exactly those three numbers written out. Deriving the name from the
    parameters rather than writing it down beside them is the point: a
    section label can then never drift from the section that was solved,
    which is how a cambered anchor came to be raced under a symmetric
    section's name.
    """
    wing = wing or WING
    camber = int(round(100 * float(wing.get("camber", 0.0))))
    location = int(round(10 * float(wing.get("camber_loc", 0.0))))
    thickness = int(round(100 * float(wing.get("thick_chord", 0.12))))
    if not camber:
        location = 0
    return f"NACA {camber}{location}{thickness:02d}"
RE_NOMINAL = 1.0e6
RE_SIGMA = 0.08 * RE_NOMINAL      # stated freestream/Re input uncertainty (8%)
ALPHAS = [float(a) for a in range(0, 11)]          # 0..10 deg, 1-deg grid
TOLERANCE_DEG = 0.5               # both paths locate the peak to +-0.5 deg
N_SAMPLES = 8                     # MC ensemble size (sample 0 = nominal)
ANCHOR_ALPHAS = [0.0, 3.3, 6.7, 10.0]
VSPAERO_THREADS = 4               # OpenMP threads per solve (measured banner)
MAX_WORKERS = 6

RACE_ROOT = lab_paths.RACE

INK = "#1c2430"
BLUE = "#2563b8"
ORANGE = "#b8562f"
GREEN = "#1c7a3d"


def _load_context() -> dict:
    """Machine conditions at measurement time — the box is shared tonight."""
    panel = audit(1, memory_per_worker_mb=256).panel()
    return {"at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cores": panel.get("cores"), "memory": panel.get("memory"),
            "other_jobs": panel.get("other_jobs"), "load": panel.get("load")}


def _design(alpha: float, re_cref: float, wing: dict | None = None) -> dict:
    """Single-alpha design point. ``wing`` overrides the curriculum wing when
    the race runs on an uploaded surface's measured parametric anchor."""
    return {**(wing or WING), "re_cref": re_cref, "alpha_start": alpha,
            "alpha_end": alpha, "alpha_npts": 1}


class _TimedSolver:
    """Every solve through here is individually wall-clocked."""

    def __init__(self, work_root: Path, wing: dict | None = None):
        # The race is a timing measurement: never reuse a prior result.
        self.api = VspAeroWingApi(work_root, reuse_prior=False)
        self.wing = dict(wing) if wing else None
        self.solve_seconds: list[float] = []

    def solve(self, alpha: float, re_cref: float, tag: str) -> dict:
        started = time.time()
        design = {**_design(alpha, re_cref, self.wing), "tag_hint": tag}
        try:
            result = self.api.evaluate(design)
        except RuntimeError:
            # One retry for transient failures; a second failure is real.
            result = self.api.evaluate({**design, "tag_hint": tag + "-r"})
        seconds = time.time() - started
        self.solve_seconds.append(seconds)
        point = result["polar"]
        return {"alpha": alpha, "re_cref": re_cref,
                "cl": point["CLtot"][0], "cd": point["CDtot"][0],
                "l_d": point["L_D"][0], "seconds": round(seconds, 2)}


def run_mc_path(work_root: Path, *, seed: int | None = None) -> dict:
    """Sample 0 is the nominal Reynolds; samples 1..N-1 draw the stated input
    uncertainty. Every alpha of every sample is a direct solve."""
    context = _load_context()
    rng = random.Random(time.time_ns() if seed is None else seed)
    res = [RE_NOMINAL] + [max(1e5, rng.gauss(RE_NOMINAL, RE_SIGMA))
                          for _ in range(N_SAMPLES - 1)]
    solver = _TimedSolver(work_root / "mc")
    jobs = [(s, alpha, re_c) for s, re_c in enumerate(res)
            for alpha in ALPHAS]
    results: list[dict | None] = [None] * len(jobs)
    started = time.time()

    def _one(index: int) -> None:
        sample, alpha, re_c = jobs[index]
        try:
            point = solver.solve(alpha, re_c, f"s{sample}a{alpha:g}")
            results[index] = {**point, "sample": sample}
        except Exception as exc:
            safe_print(f"[race] MC solve s{sample} a={alpha:g} failed: {exc}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        list(pool.map(_one, range(len(jobs))))
    wall = time.time() - started

    points = [p for p in results if p]
    samples: dict[int, list[dict]] = {}
    for point in points:
        samples.setdefault(point["sample"], []).append(point)
    peaks = []
    for sample, pts in sorted(samples.items()):
        best = max(pts, key=lambda p: p["l_d"])
        peaks.append({"sample": sample, "alpha": best["alpha"],
                      "l_d": best["l_d"], "re_cref": best["re_cref"]})
    peak_values = [p["l_d"] for p in peaks]
    mean = statistics.fmean(peak_values)
    sigma = statistics.stdev(peak_values) if len(peak_values) > 1 else 0.0
    sem = sigma / (len(peak_values) ** 0.5) if peak_values else 0.0
    return {"points": points, "peaks": peaks, "n_solves": len(points),
            "peak_mean": mean, "peak_sigma": sigma, "peak_sem": sem,
            "peak_alpha_mode": statistics.mode(p["alpha"] for p in peaks),
            "wall_seconds": round(wall, 1),
            "solve_seconds": [round(s, 2) for s in solver.solve_seconds],
            "core_minutes": round(sum(solver.solve_seconds)
                                  * VSPAERO_THREADS / 60, 2),
            "context": context}


def run_rom_path(work_root: Path) -> dict:
    """Four real anchors, a quadratic in alpha, one real confirmation solve."""
    context = _load_context()
    solver = _TimedSolver(work_root / "rom")
    started = time.time()
    anchors = [solver.solve(alpha, RE_NOMINAL, f"anchor{alpha:g}")
               for alpha in ANCHOR_ALPHAS]
    xs = [a["alpha"] for a in anchors]
    ys = [a["l_d"] for a in anchors]
    coefficients = _fit_quadratic(xs, ys)
    # Peak of the fitted quadratic over the swept range: the vertex when the
    # fit is concave, otherwise whichever end the fit values higher.
    a2, a1 = coefficients[2], coefficients[1]
    if a2 < 0:
        vertex = -a1 / (2 * a2)
    else:
        vertex = (ALPHAS[0]
                  if _predict(coefficients, ALPHAS[0])
                  >= _predict(coefficients, ALPHAS[-1]) else ALPHAS[-1])
    alpha_star = round(min(max(vertex, ALPHAS[0]), ALPHAS[-1]), 1)
    predicted = _predict(coefficients, alpha_star)
    confirm = solver.solve(alpha_star, RE_NOMINAL, "confirm")
    wall = time.time() - started
    return {"anchors": anchors, "coefficients": list(coefficients),
            "alpha_star": alpha_star, "predicted": predicted,
            "confirmed": confirm["l_d"], "confirm_seconds": confirm["seconds"],
            "surrogate_error": abs(confirm["l_d"] - predicted),
            "n_solves": len(anchors) + 1,
            "wall_seconds": round(wall, 1),
            "solve_seconds": [round(s, 2) for s in solver.solve_seconds],
            "core_minutes": round(sum(solver.solve_seconds)
                                  * VSPAERO_THREADS / 60, 2),
            "context": context}


# ---------------------------------------------------------------------------
# Artifacts — publication-style plots, real data only
# ---------------------------------------------------------------------------

def _style(ax, title: str) -> None:
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.set_xlabel(r"$\alpha$ [$^\circ$]", fontsize=10, color=INK)
    ax.set_ylabel(r"$L/D$", fontsize=10, color=INK)
    ax.grid(True, color="#dfe4ea", linewidth=0.6)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def _plt():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        return None


def polar_plot(mc: dict, out_png: Path) -> str | None:
    plt = _plt()
    if plt is None:
        return None
    nominal = sorted((p for p in mc["points"] if p["sample"] == 0),
                     key=lambda p: p["alpha"])
    fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=140)
    ax.plot([p["alpha"] for p in nominal], [p["l_d"] for p in nominal],
            color=BLUE, linewidth=2, marker="o", markersize=4.5,
            label="direct solves, nominal $Re_c = 10^6$")
    best = max(nominal, key=lambda p: p["l_d"])
    ax.annotate(rf"peak $L/D$ = {best['l_d']:.1f} at "
                rf"$\alpha$ = {best['alpha']:g}$^\circ$",
                (best["alpha"], best["l_d"]), xytext=(14, -16),
                textcoords="offset points", fontsize=10, color=INK)
    ax.scatter([best["alpha"]], [best["l_d"]], s=70, facecolors="none",
               edgecolors=GREEN, linewidths=2, zorder=5)
    _style(ax, "NACA 4412 finite wing: solved lift-to-drag polar")
    ax.legend(frameon=False, fontsize=9, loc="lower center")
    fig.tight_layout(); fig.savefig(out_png); plt.close(fig)
    return str(out_png)


def race_chart(mc: dict, rom: dict, out_png: Path) -> str | None:
    plt = _plt()
    if plt is None:
        return None
    fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=140)
    ax.scatter([p["alpha"] for p in mc["points"]],
               [p["l_d"] for p in mc["points"]], s=14, color=BLUE, alpha=0.45,
               label=f"Monte-Carlo candidates ({mc['n_solves']} direct solves)")
    grid = [ALPHAS[0] + (ALPHAS[-1] - ALPHAS[0]) * i / 80 for i in range(81)]
    ax.plot(grid, [_predict(rom["coefficients"], x) for x in grid],
            color=ORANGE, linewidth=2, label="fitted response surface")
    ax.scatter([a["alpha"] for a in rom["anchors"]],
               [a["l_d"] for a in rom["anchors"]], s=52, color=ORANGE,
               zorder=4, label=f"anchor solves ({len(rom['anchors'])})")
    ax.scatter([rom["alpha_star"]], [rom["confirmed"]], s=80, color=GREEN,
               zorder=5, label=f"confirmation solve ($L/D$ = "
                               f"{rom['confirmed']:.1f})")
    _style(ax, "Same question, two candidate sets: every point a real solve")
    ax.legend(frameon=False, fontsize=8.5, loc="lower center", ncols=2)
    fig.tight_layout(); fig.savefig(out_png); plt.close(fig)
    return str(out_png)


def progress_frames(mc: dict, rom: dict, out_dir: Path) -> dict:
    """Start/mid/finish stills per path for the split-screen staging."""
    plt = _plt()
    if plt is None:
        return {}
    frames: dict[str, list[str]] = {"mc": [], "rom": []}

    for stage, upto in (("start", 2), ("mid", N_SAMPLES // 2),
                        ("finish", N_SAMPLES)):
        pts = [p for p in mc["points"] if p["sample"] < upto]
        peaks = [p for p in mc["peaks"] if p["sample"] < upto]
        fig, ax = plt.subplots(figsize=(6.6, 4.2), dpi=140)
        ax.scatter([p["alpha"] for p in pts], [p["l_d"] for p in pts],
                   s=14, color=BLUE, alpha=0.5)
        if peaks:
            mean = statistics.fmean(p["l_d"] for p in peaks)
            ax.axhline(mean, color=GREEN, linewidth=1.4, linestyle="--")
            ax.annotate(f"running peak estimate {mean:.1f} "
                        f"({len(pts)} solves)", (ALPHAS[0], mean),
                        xytext=(4, 6), textcoords="offset points",
                        fontsize=9, color=INK)
        _style(ax, f"Monte-Carlo path: sample {upto} of {N_SAMPLES}")
        png = out_dir / f"mc_{stage}.png"
        fig.tight_layout(); fig.savefig(png); plt.close(fig)
        frames["mc"].append(str(png))

    stages = [("start", len(rom["anchors"]), False, False),
              ("mid", len(rom["anchors"]), True, False),
              ("finish", len(rom["anchors"]), True, True)]
    grid = [ALPHAS[0] + (ALPHAS[-1] - ALPHAS[0]) * i / 80 for i in range(81)]
    for stage, n_anchor, fitted, confirmed in stages:
        fig, ax = plt.subplots(figsize=(6.6, 4.2), dpi=140)
        anchors = rom["anchors"][:n_anchor]
        ax.scatter([a["alpha"] for a in anchors],
                   [a["l_d"] for a in anchors], s=52, color=ORANGE, zorder=3)
        title = f"Reduced-order path: {n_anchor} real anchors"
        if fitted:
            ax.plot(grid, [_predict(rom["coefficients"], x) for x in grid],
                    color=ORANGE, linewidth=2)
            ax.axvline(rom["alpha_star"], color=INK, linewidth=0.8,
                       linestyle=":")
            title = "Reduced-order path: surface fitted, peak predicted"
        if confirmed:
            ax.scatter([rom["alpha_star"]], [rom["confirmed"]], s=80,
                       color=GREEN, zorder=5)
            ax.annotate(f"confirmed {rom['confirmed']:.1f} "
                        f"(surrogate err {rom['surrogate_error']:.2g})",
                        (rom["alpha_star"], rom["confirmed"]),
                        xytext=(-8, -16), textcoords="offset points",
                        ha="right", fontsize=9, color=INK)
            title = "Reduced-order path: one real solve certifies the peak"
        _style(ax, title)
        png = out_dir / f"rom_{stage}.png"
        fig.tight_layout(); fig.savefig(png); plt.close(fig)
        frames["rom"].append(str(png))
    return frames


def speedup_card(mc: dict, rom: dict, out_png: Path) -> str | None:
    plt = _plt()
    if plt is None:
        return None
    cm_mc, cm_rom = mc["core_minutes"], rom["core_minutes"]
    speedup = cm_mc / cm_rom if cm_rom else float("inf")
    fig, ax = plt.subplots(figsize=(8.2, 3.4), dpi=140)
    bars = ax.barh(
        [f"reduced-order\n({rom['n_solves']} real solves)",
         f"full Monte-Carlo\n({mc['n_solves']} real solves)"],
        [cm_rom, cm_mc], color=[ORANGE, BLUE], height=0.55)
    for bar, minutes, wall in zip(bars, (cm_rom, cm_mc),
                                  (rom["wall_seconds"], mc["wall_seconds"])):
        ax.annotate(f"{minutes:.1f} core-min · wall {wall:.0f} s (measured)",
                    (bar.get_width(), bar.get_y() + bar.get_height() / 2),
                    xytext=(6, 0), textcoords="offset points", va="center",
                    fontsize=9.5, color=INK)
    ax.set_title(f"full MC: {cm_mc:.1f} core-min · reduced: {cm_rom:.1f} "
                 f"core-min · speedup {speedup:.1f}×  (all measured)",
                 loc="left", fontsize=11, color=INK)
    ax.set_xlabel("core-minutes (solve time × 4 solver threads)", fontsize=9,
                  color=INK)
    ax.grid(True, axis="x", color="#dfe4ea", linewidth=0.6)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.set_xlim(0, max(cm_mc, cm_rom) * 1.3)
    fig.tight_layout(); fig.savefig(out_png); plt.close(fig)
    return str(out_png)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_race(tag: str = "pass1", *, seed: int | None = None) -> dict:
    out_dir = RACE_ROOT / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    work_root = OUT_ROOT / "race-benchmark" / tag

    safe_print(f"[race:{tag}] reduced-order path: "
               f"{len(ANCHOR_ALPHAS)} anchors + surface + confirm")
    rom = run_rom_path(work_root)
    safe_print(f"[race:{tag}] ROM: peak L/D {rom['confirmed']:.2f} at "
               f"{rom['alpha_star']:g} deg in {rom['wall_seconds']:.0f}s "
               f"({rom['core_minutes']:.1f} core-min)")
    safe_print(f"[race:{tag}] Monte-Carlo path: {N_SAMPLES} samples x "
               f"{len(ALPHAS)} direct solves")
    mc = run_mc_path(work_root, seed=seed)
    safe_print(f"[race:{tag}] MC: peak L/D {mc['peak_mean']:.2f} ± "
               f"{2 * mc['peak_sem']:.2f} at {mc['peak_alpha_mode']:g} deg in "
               f"{mc['wall_seconds']:.0f}s ({mc['core_minutes']:.1f} core-min)")

    artifacts = {
        "polar": polar_plot(mc, out_dir / "polar_LD.png"),
        "race_chart": race_chart(mc, rom, out_dir / "race_candidates.png"),
        "card": speedup_card(mc, rom, out_dir / "speedup_card.png"),
        "frames": progress_frames(mc, rom, out_dir),
    }
    record = {
        "tag": tag,
        "subject": "NACA 4412 finite wing (chord 1 m, span 3 m, Re_c 1e6)",
        "question": "peak L/D over alpha 0-10 deg, located to "
                    f"±{TOLERANCE_DEG:g} deg, with an envelope",
        "mc": {k: v for k, v in mc.items() if k != "points"},
        "mc_points": mc["points"],
        "rom": rom,
        "speedup_core_minutes": round(mc["core_minutes"] / rom["core_minutes"],
                                      2) if rom["core_minutes"] else None,
        "speedup_wall": round(mc["wall_seconds"] / rom["wall_seconds"], 2)
        if rom["wall_seconds"] else None,
        "artifacts": artifacts,
    }
    (out_dir / "race.json").write_text(json.dumps(record, indent=1),
                                       encoding="utf-8")
    return record


def write_benchmarks(records: list[dict], out_md: Path) -> None:
    first = records[0]
    lines = [
        "# Speed, certified: NACA 4412 finite wing race (measured)",
        "",
        f"Subject: {first['subject']}.",
        f"Question: {first['question']}.",
        "",
        "Every evaluation on both sides is a real VSPAERO solve. The two",
        "envelopes mean different things: the Monte-Carlo envelope is the",
        "stated Reynolds input uncertainty propagated through direct solves;",
        "the reduced-order envelope is the surrogate's error measured against",
        "one real confirmation solve. Core-minutes = solve wall-time × the",
        "solver's 4 OpenMP threads. No choreographed delays anywhere; any",
        "time-compression in the video must be labeled with its factor.",
        "",
        "| pass | path | real solves | wall [s] | core-min | answer | load |",
        "|---|---|---|---|---|---|---|",
    ]
    for record in records:
        mc, rom = record["mc"], record["rom"]
        lines.append(
            f"| {record['tag']} | full Monte-Carlo | {mc['n_solves']} | "
            f"{mc['wall_seconds']:.0f} | {mc['core_minutes']:.1f} | "
            f"peak L/D {mc['peak_mean']:.2f} ± {2 * mc['peak_sem']:.2f} at "
            f"{mc['peak_alpha_mode']:g}° | {mc['context']['cores']}, "
            f"load {mc['context']['load']} |")
        lines.append(
            f"| {record['tag']} | reduced-order | {rom['n_solves']} | "
            f"{rom['wall_seconds']:.0f} | {rom['core_minutes']:.1f} | "
            f"peak L/D {rom['confirmed']:.2f} at {rom['alpha_star']:g}° "
            f"(surrogate err {rom['surrogate_error']:.2g}) | "
            f"{rom['context']['cores']}, load {rom['context']['load']} |")
        lines.append(
            f"| {record['tag']} | **speedup** |  |  | "
            f"**{record['speedup_core_minutes']}×** "
            f"(wall {record['speedup_wall']}×) |  |  |")
    lines += [
        "",
        "For the website speed-benchmark panel (N2), from the headline pass:",
        f"- full MC: {first['mc']['core_minutes']:.1f} core-min",
        f"- reduced: {first['rom']['core_minutes']:.1f} core-min",
        f"- speedup: {first['speedup_core_minutes']}×",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    import sys

    tag = sys.argv[1] if len(sys.argv) > 1 else "pass1"
    record = run_race(tag)
    records = []
    for prior in sorted(RACE_ROOT.glob("pass*/race.json")):
        records.append(json.loads(prior.read_text(encoding="utf-8")))
    write_benchmarks(records or [record], RACE_ROOT / "benchmarks.md")
    safe_print(f"[race:{tag}] speedup {record['speedup_core_minutes']}x "
               f"core-min, artifacts in {RACE_ROOT}")
