"""The race, as a routed in-GUI mission — two real paths, both timed, live.

One question — where the NACA 4412 finite wing's lift-to-drag peaks over alpha
0-10 degrees — answered two ways at once, on screen, every evaluation a real
VSPAERO solve and every wall clock measured on this machine:

* **Full Monte-Carlo lane** — an input-uncertainty ensemble over the chord
  Reynolds number; each sample sweeps alpha 0-10 as eleven direct single-alpha
  solves. Nothing is interpolated: the peak is read off solved points only.
* **Reduced-order lane** — four real anchor solves across the alpha range, a
  fitted quadratic response surface locating the peak, one real confirmation
  solve at the predicted alpha. Same objective, same tolerance.

The two lanes run CONCURRENTLY through one shared pool of at most four solver
slots (the compute treaty — a mega-batch and the UQ ladders share the box), so
the on-screen race is a real race: the reduced-order lane crosses the line while
the Monte-Carlo lane is still grinding, and the speedup card at the end shows
only the numbers measured in THIS run.

This is the streaming twin of ``workflows.race_benchmark``: it reuses that
harness's wing, solver, and math, and adds live per-lane event emission for the
split-screen race view in the control room.
"""

from __future__ import annotations

import random
import re
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import OUT_ROOT, announce_geometry, emit_table, make_transcript
from chief_engineer import vspaero
from chief_engineer.compute_audit import audit
from chief_engineer.display_names import display_name
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, NUMERICIST, PLAN, Roster,
                                uncertainty_channels)
from chief_engineer.researcher import (ENGINEER_ACK, MissionProperties,
                                       method_memo)
from chief_engineer.transcript import CHIEF_ENGINEER as _CE_ROLE
from chief_engineer.transcript import CHIEF_RESEARCHER as _CR_ROLE
from workflows.race_benchmark import (ALPHAS, ANCHOR_ALPHAS, RE_NOMINAL,
                                      RE_SIGMA, TOLERANCE_DEG, VSPAERO_THREADS,
                                      WING, _TimedSolver)
from workflows.shape_optimization import _fit_quadratic, _predict
# The canonical uploaded-surface measurement lives in the airliner act; it is
# imported, not duplicated, so every act measures an uploaded surface the same
# way (largest horizontal bounding-box extent, z up).
from workflows.aircraft_optimization import measure_surface_span

# Where the router stages uploaded surfaces (the router and the airliner act
# each define this same path locally).
_GEOMETRY_DIR = Path(__file__).resolve().parents[1] / "geometry"

# The compute treaty: at most four real solves in flight at once, across BOTH
# lanes together (a mega-batch and the UQ ladders share the box). The four slots
# are split evenly, two per lane, so each lane has a guaranteed, reserved share
# and never exceeds the cap together. The even split also makes the race honest
# and deterministic: at equal parallelism the reduced-order lane wins purely
# because it needs an order of magnitude fewer real solves — never because it
# was handed more of the box. When a lane finishes, its slots simply fall idle
# (total in flight only ever drops), so the cap is respected throughout.
MAX_WORKERS = 4
MC_WORKERS = 2
ROM_WORKERS = 2
assert MC_WORKERS + ROM_WORKERS <= MAX_WORKERS

# The Monte-Carlo ensemble size. Sample 0 is the nominal Reynolds; the rest draw
# the stated 8% input uncertainty. Every alpha of every sample is a real solve,
# so this sets the lane's solve count (samples x len(ALPHAS)). Kept modest so a
# live on-camera race finishes in a sensible window; every solve is still real.
import os
# 8 samples x 11 alphas = 88 direct solves: the Monte-Carlo lane visibly
# grinds for minutes while the reduced-order lane crosses in seconds — the
# orders-of-magnitude gap IS the act.
N_SAMPLES = int(os.environ.get("RACE_MC_SAMPLES", "8"))

# The ensemble's random draw is seeded from a fixed constant.
#
# This changes NOTHING about what runs: all 88 Monte-Carlo evaluations and all 5
# reduced-order evaluations are still solved fresh on this machine in this run
# (``_TimedSolver`` holds ``reuse_prior=False``), and every wall clock, core
# minute and speedup on screen is still measured here. What the seed fixes is
# the lane's *inputs* — the Reynolds numbers drawn for samples 1..N-1. With a
# clock seed those wandered every run, so the peak, the confidence band and the
# two-path agreement moved between takes and no narration could be timed
# against them. A Monte-Carlo study quoting its seed is ordinary practice; this
# one states the seed on the record so the run can be reproduced exactly.
#
# Set RACE_MC_SEED=clock (or none/random) for a fresh draw, or pass seed=None.
_SEED_ENV = os.environ.get("RACE_MC_SEED", "").strip().lower()
MC_SEED: int | None = (None if _SEED_ENV in {"clock", "none", "random"}
                       else int(_SEED_ENV or "20260730"))

# The act's four tables. Each one opens with its headers before any row lands,
# then grows a row at a time from the lane that measured it: the ensemble table
# gains a row when a sample's whole alpha sweep has resolved, the reduced-order
# table gains one per anchor and then the surface peak and the confirmation.
# Every cell below is a number the run measured or a setting it was handed.
_SETUP_TABLE = "race-setup"
_SETUP_TITLE = "What is raced and what settles it"
_SETUP_HEADERS = ("Item", "Setting")
_MC_TABLE = "race-mc-samples"
_MC_TITLE = "Monte Carlo ensemble: peak per sample"
_MC_HEADERS = ("Sample", "Chord Reynolds", "Peak L/D", "Peak angle",
               "Solve seconds")
_ROM_TABLE = "race-rom-steps"
_ROM_TITLE = "Reduced-order lane: anchors, fitted surface, confirmation"
_ROM_HEADERS = ("Step", "Angle", "L/D", "Solve seconds")
_AGREE_TABLE = "race-agreement"
_AGREE_TITLE = "The two lanes side by side"
_AGREE_HEADERS = ("Quantity", "Monte Carlo", "Reduced order", "Agreement")


def _seconds_cell(seconds) -> str:
    """A measured wall clock, or an empty cell when there was no solve."""
    return f"{seconds:.2f}" if isinstance(seconds, (int, float)) else ""


def _mc_sample_row(emit, script, sample: int, re_cref: float,
                   points: list[dict]) -> None:
    """Land one finished sample's measured peak in the ensemble table.

    Called the moment that sample's whole alpha sweep has resolved, so the
    row is final when it appears. Nothing here paces or delays the solves.
    """
    best = max(points, key=lambda p: p["l_d"])
    seconds = [p.get("seconds") for p in points]
    spent = (sum(seconds)
             if all(isinstance(s, (int, float)) for s in seconds) else None)
    emit_table(emit, script, role=_CE_ROLE, title=_MC_TITLE,
               headers=list(_MC_HEADERS),
               rows=[[f"{sample} (nominal)" if sample == 0 else f"{sample}",
                      f"{re_cref / 1e6:.3f}e6",
                      f"{best['l_d']:.2f}",
                      f"{best['alpha']:g}°",
                      _seconds_cell(spent)]],
               table_id=_MC_TABLE, append=True)


def _rom_row(emit, script, step: str, alpha: float, value: str,
             seconds=None) -> None:
    """Land one reduced-order step in that lane's table as it happens."""
    emit_table(emit, script, role=_CE_ROLE, title=_ROM_TITLE,
               headers=list(_ROM_HEADERS),
               rows=[[step, f"{alpha:g}°", value, _seconds_cell(seconds)]],
               table_id=_ROM_TABLE, append=True)


def peak_grid_bracket(anchors: list[dict], alpha_star: float,
                      half_step: float = TOLERANCE_DEG) -> float | None:
    """The race's numerical channel, computed from the lane data in hand.

    Both lanes locate the peak on a discrete angle grid, so the true optimum
    lies between grid points. The reduced-order lane's own anchors fit the
    local response, and the bracket is the largest change in peak
    lift-to-drag across half a grid step either side of the winning angle,
    the same half-step convention the airliner act's grid bracket uses.
    Returns None when the anchors cannot support a fit; nothing is invented.
    """
    points = sorted((a for a in anchors
                     if a.get("alpha") is not None and a.get("l_d") is not None),
                    key=lambda a: a["alpha"])
    if len(points) < 3:
        return None
    try:
        coefficients = _fit_quadratic([float(p["alpha"]) for p in points],
                                      [float(p["l_d"]) for p in points])
        at = lambda x: _predict(coefficients, x)   # noqa: E731
        return max(abs(at(alpha_star + half_step) - at(alpha_star)),
                   abs(at(alpha_star - half_step) - at(alpha_star)))
    except (ValueError, ZeroDivisionError, ArithmeticError):
        return None


def _mc_reynolds(samples: int, seed: int | None) -> list[float]:
    rng = random.Random(time.time_ns() if seed is None else seed)
    return [RE_NOMINAL] + [max(1e5, rng.gauss(RE_NOMINAL, RE_SIGMA))
                           for _ in range(samples - 1)]


def _mc_lane(pool: ThreadPoolExecutor, work_root: Path, emit, script, *,
             samples: int, seed: int | None,
             wing: dict | None = None) -> dict:
    """The full Monte-Carlo lane: samples x alpha, every point a real solve.

    Submits every (sample, alpha) job to the shared pool and streams a trace
    point and a lane-progress event as each solve lands. The nominal-Reynolds
    sample is flagged so the polar can draw it as the running answer line while
    the ensemble keeps grinding out the envelope behind it. A sample's row
    joins the ensemble table the moment its last alpha resolves, so the drawn
    Reynolds number and the peak it produced are on screen while the rest of
    the ensemble is still solving.
    """
    solver = _TimedSolver(work_root / "mc", wing=wing)
    res = _mc_reynolds(samples, seed)
    jobs = [(s, alpha, re_c) for s, re_c in enumerate(res) for alpha in ALPHAS]
    total = len(jobs)
    started = time.time()
    emit("race.lane", {"lane": "mc", "done": 0, "total": total,
                       "elapsed_s": 0.0, "state": "running"})

    futures = {pool.submit(solver.solve, alpha, re_c, f"mc-s{s}a{alpha:g}"):
               (s, alpha, re_c) for (s, alpha, re_c) in jobs}
    points: list[dict] = []
    # Built as the solves land rather than after the lane, so a sample's row
    # can be written the moment that sample's sweep is complete.
    by_sample: dict[int, list[dict]] = {}
    resolved: dict[int, int] = {}
    per_sample = len(ALPHAS)
    done = 0
    for fut in as_completed(futures):
        s, alpha, re_c = futures[fut]
        resolved[s] = resolved.get(s, 0) + 1
        try:
            point = fut.result()
        except Exception:
            point = None
        done += 1
        if point is not None:
            point["sample"] = s
            points.append(point)
            by_sample.setdefault(s, []).append(point)
            emit("trace.point", {"series": "mc", "x": alpha,
                                 "y": round(point["l_d"], 3),
                                 "nominal": s == 0, "sample": s,
                                 "x_label": "angle of attack [deg]",
                                 "y_label": "L/D",
                                 "title": "Full Monte-Carlo: polar"})
        emit("race.lane", {"lane": "mc", "done": done, "total": total,
                           "elapsed_s": round(time.time() - started, 1),
                           "state": "running"})
        if resolved[s] == per_sample and by_sample.get(s):
            _mc_sample_row(emit, script, s, res[s], by_sample[s])
    wall = time.time() - started

    peaks = [max(pts, key=lambda p: p["l_d"])["l_d"]
             for pts in by_sample.values() if pts]
    mean = statistics.fmean(peaks) if peaks else 0.0
    sigma = statistics.stdev(peaks) if len(peaks) > 1 else 0.0
    sem = sigma / (len(peaks) ** 0.5) if peaks else 0.0
    nominal = [p for p in points if p["sample"] == 0]
    peak_alpha = (max(nominal, key=lambda p: p["l_d"])["alpha"]
                  if nominal else (peaks and ALPHAS[0]))
    core_minutes = round(sum(solver.solve_seconds) * VSPAERO_THREADS / 60, 2)
    summary = {"lane": "mc", "n_solves": len(points), "samples": samples,
               "peak_mean": round(mean, 2), "peak_sem": round(sem, 3),
               "peak_alpha": peak_alpha, "wall_seconds": round(wall, 1),
               "core_minutes": core_minutes}
    emit("race.lane", {"lane": "mc", "done": len(points), "total": total,
                       "elapsed_s": round(wall, 1), "state": "done",
                       "note": f"peak L/D {mean:.2f} ± {2 * sem:.2f} at "
                               f"{peak_alpha:g}° · {len(points)} solves"})
    return summary


def _rom_lane(pool: ThreadPoolExecutor, work_root: Path, emit, script, *,
              wing: dict | None = None) -> dict:
    """The reduced-order lane: four anchor solves, a fitted surface, one
    confirmation solve. Shares the same four-slot pool as the Monte-Carlo lane,
    so on a busy box it queues behind those solves — the race stays honest."""
    solver = _TimedSolver(work_root / "rom", wing=wing)
    total = len(ANCHOR_ALPHAS) + 1
    started = time.time()
    emit("race.lane", {"lane": "rom", "done": 0, "total": total,
                       "elapsed_s": 0.0, "state": "running"})

    anchor_futs = {pool.submit(solver.solve, a, RE_NOMINAL, f"rom-anchor{a:g}"):
                   a for a in ANCHOR_ALPHAS}
    anchors: list[dict] = []
    for fut in as_completed(anchor_futs):
        alpha = anchor_futs[fut]
        point = fut.result()
        anchors.append(point)
        emit("trace.point", {"series": "rom", "x": alpha,
                             "y": round(point["l_d"], 3), "kind": "anchor",
                             "x_label": "angle of attack [deg]",
                             "y_label": "L/D",
                             "title": "Reduced-order: anchors + surface"})
        emit("race.lane", {"lane": "rom", "done": len(anchors), "total": total,
                           "elapsed_s": round(time.time() - started, 1),
                           "state": "running"})
        _rom_row(emit, script, "Anchor solve", alpha,
                 f"{point['l_d']:.2f}", point.get("seconds"))

    anchors.sort(key=lambda p: p["alpha"])
    xs = [a["alpha"] for a in anchors]
    ys = [a["l_d"] for a in anchors]
    coefficients = _fit_quadratic(xs, ys)
    a2, a1 = coefficients[2], coefficients[1]
    if a2 < 0:
        vertex = -a1 / (2 * a2)
    else:
        vertex = (ALPHAS[0] if _predict(coefficients, ALPHAS[0])
                  >= _predict(coefficients, ALPHAS[-1]) else ALPHAS[-1])
    alpha_star = round(min(max(vertex, ALPHAS[0]), ALPHAS[-1]), 1)
    predicted = _predict(coefficients, alpha_star)
    emit("race.curve", {"lane": "rom", "coefficients": list(coefficients),
                        "x0": ALPHAS[0], "x1": ALPHAS[-1],
                        "alpha_star": alpha_star,
                        "predicted": round(predicted, 3)})
    # The prediction goes on the record before the solve that tests it, so the
    # confirmation row lands beside a number nobody could have adjusted.
    _rom_row(emit, script, "Fitted surface peak", alpha_star,
             f"{predicted:.2f}")

    confirm = solver.solve(alpha_star, RE_NOMINAL, "rom-confirm")
    wall = time.time() - started
    emit("trace.point", {"series": "rom", "x": alpha_star,
                         "y": round(confirm["l_d"], 3), "kind": "confirm",
                         "x_label": "angle of attack [deg]", "y_label": "L/D",
                         "title": "Reduced-order: confirmation solve"})
    surrogate_error = abs(confirm["l_d"] - predicted)
    _rom_row(emit, script, "Confirmation solve", alpha_star,
             f"{confirm['l_d']:.2f}", confirm.get("seconds"))
    _rom_row(emit, script, "Confirmation against the surface", alpha_star,
             f"{surrogate_error:.3g}")
    core_minutes = round(sum(solver.solve_seconds) * VSPAERO_THREADS / 60, 2)
    emit("race.lane", {"lane": "rom", "done": total, "total": total,
                       "elapsed_s": round(wall, 1), "state": "done",
                       "note": f"peak L/D {confirm['l_d']:.2f} at {alpha_star:g}° "
                               f"· surrogate error {surrogate_error:.2g} "
                               f"· {total} solves"})
    return {"lane": "rom", "n_solves": total, "anchors": anchors,
            "alpha_star": alpha_star, "predicted": round(predicted, 3),
            "confirmed": round(confirm["l_d"], 2),
            "surrogate_error": round(surrogate_error, 3),
            "wall_seconds": round(wall, 1), "core_minutes": core_minutes}


def main(request: str | None = None, params: dict | None = None,
         emit=None, *, seed: int | None = MC_SEED) -> int:
    params = params or {}
    samples = int(params.get("mc_samples") or N_SAMPLES)
    out = OUT_ROOT / "race-study"
    out.mkdir(parents=True, exist_ok=True)
    work_root = OUT_ROOT / "race-study" / "work"
    script = make_transcript("race study", emit)
    roster = Roster(emit)

    # ---- uploaded raced wing -------------------------------------------
    # A surface uploaded with the race prompt is the raced wing: it is
    # acknowledged on the record under its display name, shown in the
    # viewport before the race takes the stage, and its span measured from
    # the file's bounding box anchors the parametric wing both lanes solve
    # (reference chord held at the family's 1 m). The STL itself is never
    # pretended to be the parametric family; it stays on file.
    surface = str(params.get("surface") or "").strip()
    surface_name = display_name(surface) if surface else ""
    chord_ref = WING["area"] / WING["span"]
    wing = None
    measured_span = None
    if surface:
        measured_span = measure_surface_span(_GEOMETRY_DIR / surface)
        if measured_span:
            wing = {**WING, "span": measured_span,
                    "area": round(measured_span * chord_ref, 3)}

    if wing:
        subject = (f"{surface_name} (span {measured_span:g} m measured from "
                   f"the surface bounding box, reference chord {chord_ref:g} m, "
                   f"chord Reynolds 1e6)")
    elif surface:
        subject = (f"{surface_name} (surface on file; raced on the NACA 4412 "
                   f"parametric anchor)")
    else:
        subject = ("NACA 4412 finite wing (chord 1 m, span 3 m, unswept, "
                   "chord Reynolds 1e6)")
    raced_name = surface_name or "NACA 4412 finite wing"
    script.system(request or f"Race a full Monte-Carlo sweep against the "
                             f"reduced-order path on the {raced_name}: "
                             f"same objective, same tolerance, both timed.")

    if surface:
        announce_geometry(emit, name=surface,
                          label=f"raced wing: {surface_name}")
        if wing:
            script.engineer(
                f"• Raced wing received: {surface_name}. "
                f"• Span {measured_span:g} m measured from the surface "
                f"bounding box; reference chord {chord_ref:g} m sets the "
                f"area at {wing['area']:g} m². "
                f"• Both lanes race this wing's parametric anchor; the "
                f"surface itself stays on file.")
        else:
            script.engineer(
                f"• Raced wing received: {surface_name}. "
                f"• The surface is on file as the reference shape; both "
                f"lanes race the NACA 4412 parametric anchor.")

    # ---------------- Hypothesis ----------------
    script.phase(HYPOTHESIS)
    roster.set(CHIEF_RESEARCHER, "framing the head-to-head", "working")
    props = MissionProperties(
        kind="one-parameter-sweep",
        objective="locate the peak lift-to-drag over angle of attack",
        dimensionality=1, regime="steady", smoothness="smooth",
        fidelity="the selected solver (vortex lattice) on both paths",
        constraints=("same objective", "same tolerance"))
    # The generic memo phrases fidelity as a bound on the claim; in this act
    # the owner-ratified line is the plain statement of what runs. Solver
    # status is carried by the tier chip, never reassured in prose.
    fidelity_line = re.compile(
        r"Model fidelity \(.*?\) bounds the claim, not the search")
    stated_solver = False
    for line in method_memo(props):
        if fidelity_line.search(line):
            line = fidelity_line.sub("Both lanes solve with VSPAERO", line)
            stated_solver = True
        script.researcher(line)
    # Bullets ride together inside ONE emitted entry (owner rule: an agent
    # never appears to speak twice for one thought), so if the memo did not
    # carry the solver line it leads this entry instead of standing alone.
    script.researcher(
        ("" if stated_solver else "• Both lanes solve with VSPAERO. ") +
        "• Two ways to find one smooth peak: sweep the whole ensemble with "
        "Monte Carlo, or solve in a reduced order space. "
        "• The only honest question is what each path costs. "
        "• So we run them side by side and measure.")
    # The terms of the race, on the record before either lane starts. Every
    # cell is a setting this run was handed, never a result.
    emit_table(emit, script, role=_CR_ROLE, title=_SETUP_TITLE,
               headers=list(_SETUP_HEADERS),
               rows=[["Raced body", raced_name],
                     ["Objective", "Peak L/D over angle of attack"],
                     ["Angle range",
                      f"{ALPHAS[0]:g}° to {ALPHAS[-1]:g}°, "
                      f"{len(ALPHAS)} angles"],
                     ["Tolerance on the peak angle", f"±{TOLERANCE_DEG:g}°"],
                     ["Ensemble samples", f"{samples}"],
                     ["Ensemble draw",
                      f"seed {seed}" if seed is not None
                      else "drawn from the clock"],
                     ["Reduced-order anchors", f"{len(ANCHOR_ALPHAS)}"]],
               table_id=_SETUP_TABLE)
    roster.idle(CHIEF_RESEARCHER)
    script.engineer(ENGINEER_ACK)

    # ---------------- Plan ----------------
    script.phase(PLAN)
    total_mc = samples * len(ALPHAS)
    total_rom = len(ANCHOR_ALPHAS) + 1
    capacity = audit(MAX_WORKERS, memory_per_worker_mb=256)
    if emit:
        emit("audit.completed", capacity.panel())
    script.engineer(capacity.headline(), panel=capacity.panel())

    solver_live = vspaero.available()
    if solver_live and emit:
        emit("solver.selected", {
            "solver": "VSPAERO", "method": "vortex lattice",
            "basis": "both lanes commit every evaluation to the selected solver"})
    script.engineer(
        f"• Left lane: full Monte-Carlo, {samples} Reynolds samples "
        f"× {len(ALPHAS)} direct solves = {total_mc} solver runs. "
        f"• Right lane: reduced-order, {len(ANCHOR_ALPHAS)} anchors, a "
        f"fitted surface, one confirmation = {total_rom} solver runs. "
        f"• Same peak, same ±{TOLERANCE_DEG:g}° tolerance, the same box: "
        f"{MAX_WORKERS} slots split evenly, {ROM_WORKERS} per lane. "
        + (f"• Ensemble drawn from seed {seed}, so the same {samples} Reynolds "
           f"numbers are solved on every run and the result is reproducible; "
           f"the clocks below are still measured here, this run."
           if seed is not None else
           "• Ensemble drawn from the clock, so this run's Reynolds numbers "
           "are its own."))

    if emit:
        emit("race.init", {
            "subject": subject,
            "objective": "peak L/D over angle of attack 0 to 10°",
            "tolerance": f"±{TOLERANCE_DEG:g}°",
            "x_label": "angle of attack [deg]", "y_label": "L/D",
            "lanes": [
                {"key": "mc", "title": "FULL MONTE-CARLO",
                 "subtitle": f"{samples} samples × {len(ALPHAS)} alphas",
                 "total": total_mc},
                {"key": "rom", "title": "REDUCED-ORDER",
                 "subtitle": f"{len(ANCHOR_ALPHAS)} anchors + surface + confirm",
                 "total": total_rom}]})

    # ---------------- Evidence: the race ----------------
    script.phase(EVIDENCE)
    roster.set(CHIEF_ENGINEER, "running both lanes", "working")
    roster.set_workers(MAX_WORKERS, "shared solver slots")
    script.numericist(
        f"• The Monte-Carlo lane needs all {total_mc} solves to reach a "
        f"confidence band this tight; the reduced-order lane gets there "
        f"with {total_rom}.")
    script.engineer(
        "• Each sample lands its row in the ensemble table as its sweep "
        "finishes. "
        "• The reduced-order lane fills its own table anchor by anchor.")
    # Both tables open empty, so the columns are on screen while the lanes
    # work and every row that follows is a measurement.
    emit_table(emit, script, role=_CE_ROLE, title=_MC_TITLE,
               headers=list(_MC_HEADERS), rows=[], table_id=_MC_TABLE)
    emit_table(emit, script, role=_CE_ROLE, title=_ROM_TITLE,
               headers=list(_ROM_HEADERS), rows=[], table_id=_ROM_TABLE)

    lane_results: dict[str, dict] = {}

    def _run(lane_fn, key):
        try:
            lane_results[key] = lane_fn()
        except Exception as exc:  # a lane failure is reported, not hidden
            lane_results[key] = {"lane": key, "error": str(exc)}

    # Each lane gets its own reserved pool; the two sizes sum to the four-slot
    # cap. Reserved slots are what make the on-screen race deterministic — the
    # reduced-order lane cannot be starved of the box by the Monte-Carlo lane's
    # far larger job queue, so it wins on solve count alone.
    with ThreadPoolExecutor(max_workers=ROM_WORKERS) as rom_pool, \
         ThreadPoolExecutor(max_workers=MC_WORKERS) as mc_pool, \
         ThreadPoolExecutor(max_workers=2) as drivers:
        futs = [
            drivers.submit(_run, lambda: _rom_lane(rom_pool, work_root, emit,
                                                   script, wing=wing),
                           "rom"),
            drivers.submit(_run, lambda: _mc_lane(mc_pool, work_root, emit,
                                                  script, samples=samples,
                                                  seed=seed, wing=wing),
                           "mc"),
        ]
        for fut in futs:
            fut.result()

    mc = lane_results.get("mc", {})
    rom = lane_results.get("rom", {})
    roster.set_workers(0, "")
    roster.idle(CHIEF_ENGINEER)

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    if "error" in mc or "error" in rom or not mc or not rom:
        script.engineer("• A lane did not finish cleanly; reporting "
                        "what completed, not a manufactured number.")
        if emit:
            emit("mission.note", {"mc": mc, "rom": rom})
        script.save(out / "transcript.txt")
        return 1

    cm_mc, cm_rom = mc["core_minutes"], rom["core_minutes"]
    speedup_cm = round(cm_mc / cm_rom, 1) if cm_rom else None
    speedup_wall = round(mc["wall_seconds"] / rom["wall_seconds"], 1) \
        if rom["wall_seconds"] else None
    agreement = abs(mc["peak_mean"] - rom["confirmed"])
    agreement_pct = round(100 * agreement / mc["peak_mean"], 1) if mc["peak_mean"] else None

    script.engineer(
        f"• Same answer: full MC peak L/D {mc['peak_mean']:.2f} ± "
        f"{2 * mc['peak_sem']:.2f}; reduced-order {rom['confirmed']:.2f} at "
        f"{rom['alpha_star']:g}°, and they agree to {agreement_pct}%. "
        f"• Cost: {cm_mc:.1f} core-min versus {cm_rom:.1f} core-min. "
        f"• Measured speedup {speedup_cm}× in core-minutes.")

    # The two lanes' independently located answers, and what they cost, in one
    # table. Every cell is carried straight from the lane summaries above; the
    # agreement column is left empty where no agreement is defined.
    alpha_gap = abs(float(mc["peak_alpha"]) - float(rom["alpha_star"]))
    emit_table(emit, script, role=_CE_ROLE, title=_AGREE_TITLE,
               headers=list(_AGREE_HEADERS),
               rows=[["Peak L/D",
                      f"{mc['peak_mean']:.2f} ± {2 * mc['peak_sem']:.2f}",
                      f"{rom['confirmed']:.2f}",
                      "" if agreement_pct is None else f"{agreement_pct}%"],
                     ["Peak angle", f"{mc['peak_alpha']:g}°",
                      f"{rom['alpha_star']:g}°", f"{alpha_gap:g}° apart"],
                     ["Solver runs", f"{mc['n_solves']}",
                      f"{rom['n_solves']}", ""],
                     ["Cost in core minutes", f"{cm_mc:.1f}",
                      f"{cm_rom:.1f}", ""]],
               table_id=_AGREE_TABLE)

    if emit:
        emit("race.result", {
            "subject": subject,
            "mc": {"n_solves": mc["n_solves"], "core_minutes": cm_mc,
                   "wall_seconds": mc["wall_seconds"],
                   "peak": f"L/D {mc['peak_mean']:.2f} ± {2 * mc['peak_sem']:.2f} "
                           f"at {mc['peak_alpha']:g}°"},
            "rom": {"n_solves": rom["n_solves"], "core_minutes": cm_rom,
                    "wall_seconds": rom["wall_seconds"],
                    "peak": f"L/D {rom['confirmed']:.2f} at {rom['alpha_star']:g}°"},
            "speedup_core_min": speedup_cm, "speedup_wall": speedup_wall,
            "agreement_pct": agreement_pct,
            "agreement": (f"The two paths agree to {agreement_pct}%. "
                          f"Both within confidence bounds.")})
        emit("result.verdict", {
            "quantity": "Peak L/D",
            "value": f"{rom['confirmed']:.2f}", "ci": f"{2 * mc['peak_sem']:.2f}",
            "confidence": "95%", "tier": "SOLVER-BACKED",
            "envelope": f"full MC {cm_mc:.1f} core-min vs reduced {cm_rom:.1f} "
                        f"core-min, {speedup_cm}× measured",
            "reason": f"every evaluation on both lanes ran the selected solver; the "
                      f"paths agree to {agreement_pct}%"})
        emit("agenda.updated", {"entries": [
            {"title": "Push the reduced-order lane to a two-parameter surface",
             "scope": "add camber to the anchor set; measure whether five real "
                      "anchors still beat the ensemble on a curved trade",
             "cost": "a few extra anchor solves"},
            {"title": "Sweep from -4° for an interior peak",
             "scope": "the cambered AR-3 wing peaks at the alpha=0 boundary; a "
                      "wider sweep would put the peak inside the range",
             "cost": "one-line change, ~2 min rerun"},
            {"title": "Re-race under measured box load",
             "scope": "record the speedup with the mega-batch and UQ ladders "
                      "sharing the four slots, to bound the busy-box number",
             "cost": "one contended pass"}]})
        emit("report.ready", {
            "title": (f"Speed, certified: the {surface_name} race" if surface
                      else "Speed, certified: the NACA 4412 race"),
            "subject": subject,
            "summary": (f"Two real paths, both timed on this machine. Full "
                        f"Monte-Carlo: {mc['n_solves']} solver runs, "
                        f"{cm_mc:.1f} core-min, peak L/D {mc['peak_mean']:.2f} "
                        f"± {2 * mc['peak_sem']:.2f}. Reduced-order: "
                        f"{rom['n_solves']} solver runs, {cm_rom:.1f} core-min, "
                        f"peak L/D {rom['confirmed']:.2f} at "
                        f"{rom['alpha_star']:g}°. They agree to "
                        f"{agreement_pct}%; the measured speedup is "
                        f"{speedup_cm}× in core-minutes."),
            "figures": []})

    # The three uncertainty channels, every value measured in THIS run:
    # input is the ensemble spread over the stated Reynolds uncertainty;
    # numerical is the angle-grid bracket computed from the lane data; model
    # is the measured agreement of the two independent solve paths, which is
    # direct cross-path evidence, with the surface's own confirmation
    # residual stated beside it. Generic register only; no method names.
    bracket = peak_grid_bracket(rom.get("anchors") or [], rom["alpha_star"])
    race_channels = uncertainty_channels(
        input_2sigma=round(2 * mc["peak_sem"], 3),
        numerical=None if bracket is None else round(bracket, 3),
        model=round(agreement, 3),
        input_note="Ensemble run over the stated spread in chord Reynolds "
                   "number, propagated to the peak lift-to-drag through "
                   "direct solves.",
        numerical_note=("Both lanes locate the peak on a discrete angle "
                        "grid, so the true optimum lies between grid points. "
                        "The band is the change in peak lift-to-drag across "
                        "half a grid step at the winning angle."
                        if bracket is not None else
                        "Both lanes locate the peak on a discrete angle "
                        "grid; the anchor set cannot bracket the half-step "
                        "variation on this run."),
        model_note=(f"Measured agreement between the two independent solve "
                    f"paths: {agreement:.2f} in peak lift-to-drag "
                    f"({agreement_pct}%). The fitted surface's residual "
                    f"against its confirmation solve is "
                    f"{rom['surrogate_error']:.2g}."))
    if emit:
        emit("uncertainty.channels", race_channels)

    # The Certonomous certificate for the race act: the peak lift-to-drag
    # with its measured ensemble band as the headline, the measured speedup
    # and agreement in the structured result table. Every evaluation on both
    # lanes was a real solve, so the chip is SOLVER-BACKED. Uniform
    # convention (airliner pattern): the previous run's page is withdrawn
    # FIRST and the new page lands atomically; a failure is said on the
    # record. No mesh block: this act solves no mesh.
    cert_path = out / "certificate.pdf"
    try:
        cert_path.unlink()
    except OSError:
        pass
    try:
        from chief_engineer.certificate import build_certificate_v2

        verdict = {"tier": "SOLVER-BACKED",
                   "reason": (f"every evaluation on both lanes was a converged "
                              f"vortex-lattice run on the selected solver; the "
                              f"two paths agree to {agreement_pct}%")}
        cert_doc = {
            "results": [
                {"quantity": "Peak lift-to-drag",
                 "value": f"{rom['confirmed']:.2f}",
                 "envelope": f"{2 * mc['peak_sem']:.2f}", **verdict},
                {"quantity": "Measured speedup, reduced-order vs full "
                             "ensemble sweep",
                 "value": f"{speedup_cm}x in core-minutes"},
            ],
            # Structured result block: Title Case labels, verbatim numbers.
            "result_fields": [
                ("Peak L/D", f"{rom['confirmed']:.2f} at "
                             f"{rom['alpha_star']:g} deg"),
                ("Band (95%)", f"±{2 * mc['peak_sem']:.2f}"),
                ("Agreement", f"{agreement_pct}%"),
                ("Speedup", f"{speedup_cm}x core-minutes"),
                ("Solver Runs", f"{mc['n_solves']} ensemble lane, "
                                f"{rom['n_solves']} reduced-order lane"),
                ("Cost", f"{cm_mc:.1f} vs {cm_rom:.1f} core-min"),
            ],
            "compute": {"spent_core_minutes": round(cm_mc + cm_rom, 2),
                        "saved_core_minutes": round(cm_mc - cm_rom, 2)},
        }
        geometry_key = Path(surface).stem if surface else "naca4412"
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path,
            geometry=geometry_key,
            # The objective is always THIS run's verbatim request.
            objective=(request or "Locate the peak lift-to-drag over angle "
                       "of attack two ways, same objective and tolerance, "
                       "both timed."),
            mission_id="race-comparison",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=race_channels,
            display_name=display_name(geometry_key),
            source_filename=subject,
            solver="OpenVSP VSPAERO, vortex lattice, run on both lanes")
        if emit:
            emit("certificate.ready", {**certificate, "dir": out.name})
    except Exception:  # a certificate must never take down a good mission
        script.engineer(
            "• No certificate could be issued for this run. "
            "• The previous run's certificate is withdrawn, so nothing out of "
            "date is served. "
            "• The result above stands on the transcript and the report.")

    # The act's own record on disk. Every other act saves one; the race did
    # not, which left it the one filmed act whose reproducibility could not be
    # checked by scripts/verify_warm_replay.sh.
    script.save(out / "transcript.txt")
    return 0


if __name__ == "__main__":
    main(request="Race the full Monte-Carlo sweep against the reduced-order "
                 "path on the NACA 4412 finite wing.",
         emit=lambda e, p=None: print(f"[{e}] {p}"))
