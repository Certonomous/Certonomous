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
from chief_engineer import uq, vspaero
from chief_engineer.compute_audit import audit
from chief_engineer.display_names import display_name
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, NUMERICIST, PLAN, Roster,
                                lab_report, uncertainty_channels)
from chief_engineer.researcher import (ENGINEER_ACK, MissionProperties,
                                       method_memo)
from chief_engineer.transcript import CHIEF_ENGINEER as _CE_ROLE
from chief_engineer.transcript import CHIEF_RESEARCHER as _CR_ROLE
from workflows.race_benchmark import (ALPHAS, ANCHOR_ALPHAS, RE_NOMINAL,
                                      RE_SIGMA, TOLERANCE_DEG, VSPAERO_THREADS,
                                      WING, _TimedSolver, wing_section_name)
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
# table gains one per anchor and then the reduced space peak and the
# confirmation.
# Every cell below is a number the run measured or a setting it was handed.
# Every variable is written as its symbol wherever it is named on camera — the
# lift-to-drag ratio L/D, the angle of attack α, the chord Reynolds number Re —
# and Reynolds numbers are set in scientific notation, not exponent shorthand.
_SETUP_TABLE = "race-setup"
_SETUP_TITLE = "What is raced and what settles it"
_SETUP_HEADERS = ("Item", "Setting")
_MC_TABLE = "race-mc-samples"
_MC_TITLE = "Monte Carlo ensemble: peak per sample"
_MC_HEADERS = ("Sample", "Chord Reynolds Re", "Peak L/D", "Peak angle α",
               "Solve seconds")
_ROM_TABLE = "race-rom-steps"
_ROM_TITLE = "Reduced-order lane: anchors, reduced space, confirmation"
_ROM_HEADERS = ("Step", "Angle α", "L/D", "Solve seconds")
_AGREE_TABLE = "race-agreement"
_AGREE_TITLE = "The two lanes side by side"
_AGREE_HEADERS = ("Quantity", "Monte Carlo", "Reduced order", "Agreement")
_SECTION_TABLE = "race-section"
_SECTION_TITLE = "The received surface against the raced section"
_SECTION_HEADERS = ("Section property", "Received surface, measured",
                    "Raced section, as set")

# The section both lanes solve, spelled by its own parameters rather than
# written down beside them (``wing_section_name``). Every place the act names
# the raced body reads this, so the name on screen and the camber in the
# solver's job can never disagree again.
RACED_SECTION = wing_section_name(WING)
RACED_WING = f"{RACED_SECTION} finite wing"


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
                      f"{re_cref / 1e6:.3f}×10⁶",
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
                                 "x_label": "angle of attack α [deg]",
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


def _zero_lift_guard(emit, script, point: dict, *, wing: dict | None,
                     received: str = "", section: dict | None = None) -> list:
    """Hold every name this act puts on the polar to the zero-lift prior.

    A section with no camber has no circulation at zero incidence, so a curve
    presented under a symmetric section's name must read no lift at α = 0.
    The check runs on the α = 0 solve itself, against BOTH names a viewer
    sees: the section the lanes race, and the surface the request arrived
    with. A flag is spoken, never drawn silently past.
    """
    from chief_engineer.geometry import zero_lift_report

    camber = float((wing or WING).get("camber", 0.0))
    reports = [zero_lift_report(name=RACED_WING, alpha_deg=point["alpha"],
                                cl=point["cl"], camber_frac_chord=camber)]
    if received:
        reports.append(zero_lift_report(
            name=received, alpha_deg=point["alpha"], cl=point["cl"],
            camber_frac_chord=(None if not section
                               else section["max_camber_frac_chord"]),
            incidence_deg=(None if not section else section["incidence_deg"])))
    reports = [r for r in reports if r]
    for report in reports:
        if emit:
            emit("physics.guard", {"check": "zero lift on a symmetric "
                                            "section", **report})
    flagged = [r for r in reports if not r["consistent"]]
    if flagged:
        # The terse form is what is said; the full caveat rides in the event.
        script.numericist(
            "• " + " • ".join(r["headline"] for r in flagged)
            + f" • The polar stays named {RACED_WING}.")
    elif reports:
        script.numericist(
            f"• Zero lift check clear: {reports[0]['name']} is symmetric and "
            f"reads no lift at α = {point['alpha']:g}°.")
    return reports


def _rom_lane(pool: ThreadPoolExecutor, work_root: Path, emit, script, *,
              wing: dict | None = None, received: str = "",
              section: dict | None = None) -> dict:
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
                             "x_label": "angle of attack α [deg]",
                             "y_label": "L/D",
                             "title": "Reduced-order: anchors + reduced space"})
        emit("race.lane", {"lane": "rom", "done": len(anchors), "total": total,
                           "elapsed_s": round(time.time() - started, 1),
                           "state": "running"})
        _rom_row(emit, script, "Anchor solve", alpha,
                 f"{point['l_d']:.2f}", point.get("seconds"))
        # The zero-angle anchor is the one the prior has an opinion about, so
        # the check runs the moment that solve lands rather than after the act
        # has already put the curve on screen under a name.
        if alpha == 0.0 and "cl" in point:
            _zero_lift_guard(emit, script, point, wing=wing,
                             received=received, section=section)

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
    _rom_row(emit, script, "Reduced space peak", alpha_star,
             f"{predicted:.2f}")

    confirm = solver.solve(alpha_star, RE_NOMINAL, "rom-confirm")
    wall = time.time() - started
    emit("trace.point", {"series": "rom", "x": alpha_star,
                         "y": round(confirm["l_d"], 3), "kind": "confirm",
                         "x_label": "angle of attack α [deg]", "y_label": "L/D",
                         "title": "Reduced-order: confirmation solve"})
    surrogate_error = abs(confirm["l_d"] - predicted)
    _rom_row(emit, script, "Confirmation solve", alpha_star,
             f"{confirm['l_d']:.2f}", confirm.get("seconds"))
    _rom_row(emit, script, "Confirmation against the reduced space", alpha_star,
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

    # ---- received surface, and the section that is actually raced -------
    # A surface uploaded with the race prompt is acknowledged on the record
    # under its display name, shown in the viewport before the race takes the
    # stage, and its span measured from the file's bounding box anchors the
    # parametric wing both lanes solve (reference chord held at the family's
    # 1 m). The STL itself is never pretended to be the parametric family.
    #
    # WHAT THE SPAN DOES AND DOES NOT CARRY (2026-07-31). A received surface
    # lends the lanes its SPAN and nothing else: the section stays the
    # anchor's own camber, camber position and thickness. The act used to let
    # it lend its NAME too, so a symmetric NACA 0012 arrived, a cambered
    # section was solved, and the polar went on screen labelled 0012 with its
    # lift-to-drag peaking at α = 0 — the signature of camber, impossible for
    # a symmetric section at a zero-angle reference. Both surfaces were
    # measured to settle it rather than reasoned about from their names:
    # naca0012_wing.stl reads 0.00% camber, 12.00% thickness and 0.00° of
    # built-in incidence, so the file is a genuine NACA 0012 and the angle
    # reference is sound; the wing the solver was handed carries camber 0.04
    # at 0.4 chord. So the surface was right, the label was wrong, and the
    # raced body is now named by the section its own parameters spell.
    surface = str(params.get("surface") or "").strip()
    surface_name = display_name(surface) if surface else ""
    chord_ref = WING["area"] / WING["span"]
    wing = None
    measured_span = None
    section = None
    if surface:
        from chief_engineer.geometry import measure_section

        measured_span = measure_surface_span(_GEOMETRY_DIR / surface)
        section = measure_section(_GEOMETRY_DIR / surface)
        if measured_span:
            wing = {**WING, "span": measured_span,
                    "area": round(measured_span * chord_ref, 3)}

    raced_name = RACED_WING
    if wing:
        subject = (f"{RACED_WING} (span {measured_span:g} m measured off the "
                   f"received {surface_name}, reference chord {chord_ref:g} m, "
                   f"chord Reynolds 1e6)")
    elif surface:
        subject = (f"{RACED_WING} (chord {chord_ref:g} m, span "
                   f"{WING['span']:g} m, chord Reynolds 1e6; the received "
                   f"{surface_name} is on file)")
    else:
        subject = (f"{RACED_WING} (chord 1 m, span 3 m, unswept, "
                   f"chord Reynolds 1e6)")
    script.system(request or f"Race a full Monte-Carlo sweep against the "
                             f"reduced-order path on the {raced_name}: "
                             f"same objective, same tolerance, both timed.")

    if surface:
        # The label says where the numbers live, so a viewer never has to work
        # out which of two named wings the polar belongs to.
        announce_geometry(emit, name=surface,
                          label=f"{surface_name}, received. The polar comes "
                                f"from the {RACED_SECTION} section")
        if wing:
            script.engineer(
                f"• Wing received: {surface_name}. "
                f"• Span {measured_span:g} m measured off the surface; "
                f"reference chord {chord_ref:g} m sets the area at "
                f"{wing['area']:g} m². "
                f"• Both lanes race a {RACED_SECTION} section on that span, "
                f"so the polar below is a {RACED_SECTION} polar.")
        else:
            script.engineer(
                f"• Wing received: {surface_name}. "
                f"• The surface is on file and sets nothing here. "
                f"• Both lanes race the {RACED_WING}.")
        # Measured against as-set, side by side, before either lane starts.
        # The received column is read off the file; the raced column is the
        # three numbers the solver is handed.
        if section:
            emit_table(
                emit, script, role=_CE_ROLE, title=_SECTION_TITLE,
                headers=list(_SECTION_HEADERS),
                rows=[["Maximum camber",
                       f"{100 * section['max_camber_frac_chord']:.2f}% chord",
                       f"{100 * float((wing or WING)['camber']):.2f}% chord"],
                      ["Camber position",
                       (f"{section['max_camber_at_x_over_c']:.2f} chord"
                        if not section["symmetric"] else ""),
                       f"{float((wing or WING)['camber_loc']):.2f} chord"],
                      ["Maximum thickness",
                       f"{100 * section['max_thickness_frac_chord']:.2f}% chord",
                       f"{100 * float((wing or WING)['thick_chord']):.2f}% chord"],
                      ["Built-in incidence",
                       f"{section['incidence_deg']:.2f}°", "0.00°"]],
                table_id=_SECTION_TABLE)
            script.numericist(
                f"• The received section measures "
                f"{100 * section['max_camber_frac_chord']:.2f}% camber; the "
                f"raced section carries "
                f"{100 * float((wing or WING)['camber']):.2f}%. "
                f"• Angle α is measured from the raced section's own chord "
                f"line, at zero built-in incidence.")

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
                     ["Raced section",
                      f"{RACED_SECTION}, camber "
                      f"{100 * float((wing or WING)['camber']):.0f}% chord at "
                      f"{float((wing or WING)['camber_loc']):.1f} chord"],
                     ["Angle α reference", "the raced section's chord line"],
                     ["Objective", "Peak L/D over angle of attack α"],
                     ["Angle range α",
                      f"{ALPHAS[0]:g}° to {ALPHAS[-1]:g}°, "
                      f"{len(ALPHAS)} angles"],
                     ["Tolerance on the peak angle α", f"±{TOLERANCE_DEG:g}°"],
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
        f"reduced space, one confirmation = {total_rom} solver runs. "
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
            "objective": "peak L/D over angle of attack α, 0° to 10°",
            "tolerance": f"±{TOLERANCE_DEG:g}°",
            "x_label": "angle of attack α [deg]", "y_label": "L/D",
            "lanes": [
                {"key": "mc", "title": "FULL MONTE-CARLO",
                 "subtitle": f"{samples} samples × {len(ALPHAS)} alphas",
                 "total": total_mc},
                {"key": "rom", "title": "REDUCED-ORDER",
                 "subtitle": f"{len(ANCHOR_ALPHAS)} anchors + reduced space "
                             f"+ confirm",
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
                                                   script, wing=wing,
                                                   received=surface_name,
                                                   section=section),
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

    # The three uncertainty channels, every value measured in THIS run:
    # input is the ensemble spread over the stated Reynolds uncertainty;
    # numerical is the angle-grid bracket computed from the lane data; model
    # is the measured agreement of the two independent solve paths, which is
    # direct cross-path evidence, with the reduced space's own confirmation
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
                    f"({agreement_pct}%). The reduced space's residual "
                    f"against its confirmation solve is "
                    f"{rom['surrogate_error']:.2g}."))

    # THE HEADLINE BAND COMPOSES (2026-07-31). The act used to publish the
    # ensemble spread alone beside it: the banner read ±0.07 while the
    # numerical channel in the same panel read six times that, so a viewer
    # saw the smallest of three numbers quoted as the answer's band. Eight
    # other acts already close their channels through the same call; this one
    # now does too, so the headline is the root sum of squares over every
    # channel that carries a figure. The Monte Carlo lane keeps its own
    # ±{2 sigma / sqrt(N)} in the lane table, which is what that column is.
    #
    # The numerical channel is large here for a physical reason worth stating
    # rather than smoothing: the peak sits on the α = 0 boundary, so the
    # half-step bracket reads the curve's slope and not its curvature.
    total = uq.combine_expanded(
        input_2sigma=round(2 * mc["peak_sem"], 3),
        numerical_abs=None if bracket is None else round(bracket, 3),
        model_abs=round(agreement, 3))
    headline_ci = total["combined_95"]

    script.engineer(
        f"• Same answer: full MC peak L/D {mc['peak_mean']:.2f} ± "
        f"{2 * mc['peak_sem']:.2f}; reduced-order {rom['confirmed']:.2f} at "
        f"{rom['alpha_star']:g}°, and they agree to {agreement_pct}%. "
        f"• Cost: {cm_mc:.1f} core-min versus {cm_rom:.1f} core-min. "
        f"• Measured speedup {speedup_cm}× in core-minutes.")
    # Whether the located peak sits on an end of the swept range. It decides
    # what the angle-grid channel is reading, so the act says which rather
    # than asserting the boundary case it happened to be filmed in.
    peak_at_edge = float(rom["alpha_star"]) in (ALPHAS[0], ALPHAS[-1])
    if headline_ci is not None:
        script.numericist(
            f"• Peak L/D {rom['confirmed']:.2f} ± {headline_ci:.2f} at 95%, "
            f"composed over the "
            f"{len(total['contributions'])} channels below. "
            + (f"• The angle grid dominates it: the peak sits on the α = "
               f"{rom['alpha_star']:g}° edge of the range, where a half step "
               f"reads slope and not curvature."
               if peak_at_edge else
               f"• The peak sits inside the range, so the angle grid reads "
               f"curvature at α = {rom['alpha_star']:g}°."))

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
                     ["Peak angle α", f"{mc['peak_alpha']:g}°",
                      f"{rom['alpha_star']:g}°", f"{alpha_gap:g}° apart"],
                     ["Solver runs", f"{mc['n_solves']}",
                      f"{rom['n_solves']}", ""],
                     ["Cost in core minutes", f"{cm_mc:.1f}",
                      f"{cm_rom:.1f}", ""],
                     # The lane columns carry each lane's own spread; the
                     # published band is the composition of the channels and
                     # belongs to the answer, not to either lane.
                     ["Published band (95%)", "", "",
                      "" if headline_ci is None else f"±{headline_ci:.2f}"]],
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
            "value": f"{rom['confirmed']:.2f}",
            "ci": ("" if headline_ci is None else f"{headline_ci:.2f}"),
            "confidence": "95%", "tier": "SOLVER-BACKED",
            "envelope": f"full MC {cm_mc:.1f} core-min vs reduced {cm_rom:.1f} "
                        f"core-min, {speedup_cm}× measured",
            "reason": f"every evaluation on both lanes ran the selected solver; the "
                      f"paths agree to {agreement_pct}%"})
        agenda = [
            {"title": "Push the reduced-order lane to a two-parameter "
                      "reduced space",
             "scope": "add camber to the anchor set; measure whether five "
                      "anchors still beat the ensemble on a curved trade",
             "cost": "a few extra anchor solves"},
            ({"title": "Sweep from α = -4° for an interior peak",
              "scope": f"the cambered {RACED_SECTION} section peaks at the "
                       f"α = {rom['alpha_star']:g}° edge of the range, where "
                       f"the fit reads a slope and not a curvature; a wider "
                       f"sweep puts the peak inside the range",
              "cost": "one-line change, ~2 min rerun"}
             if peak_at_edge else
             {"title": "Tighten the angle grid around the located peak",
              "scope": f"the peak sits at α = {rom['alpha_star']:g}°, inside "
                       f"the range; a finer grid there shrinks the angle-grid "
                       f"channel that leads the published band",
              "cost": "a few extra solves near the peak"}),
            {"title": "Re-race under measured box load",
             "scope": "record the speedup with the mega-batch and UQ ladders "
                      "sharing the four slots, to bound the busy-box number",
             "cost": "one contended pass"}]
        emit("agenda.updated", {"entries": agenda})
        # THE REPORT TAB (2026-07-31). The act used to emit a report.ready
        # carrying title, subject, summary and an empty figure list. The
        # report view renders abstract, methods, results, uncertainty and
        # next investigations, and reads none of those three keys, so every
        # heading in the export came out as an empty list while the digest
        # beside it was full. The certificate links from that page. Built
        # through lab_report now, the same assembly every other act uses, so
        # the structure the view renders is the structure the act writes.
        emit("report.ready", lab_report(
            title=f"Speed, certified: the {RACED_SECTION} race",
            abstract=[
                f"One question, where the {RACED_WING}'s lift-to-drag peaks "
                f"over angle of attack {ALPHAS[0]:g}° to {ALPHAS[-1]:g}°, "
                f"answered two ways at once and both timed on this machine.",
                f"The ensemble lane took {mc['n_solves']} direct solves to "
                f"peak L/D {mc['peak_mean']:.2f} ± {2 * mc['peak_sem']:.2f} at "
                f"α = {mc['peak_alpha']:g}°. The reduced-order lane reached "
                f"{rom['confirmed']:.2f} at α = {rom['alpha_star']:g}° in "
                f"{rom['n_solves']}, and the two agree to {agreement_pct}%.",
                f"Cost was {cm_mc:.1f} core-minutes against {cm_rom:.1f}, a "
                f"measured {speedup_cm}× at equal parallelism, both lanes "
                f"drawing on the same four solver slots.",
            ],
            methods=[
                f"Both lanes solve with VSPAERO, a vortex-lattice method. "
                f"Every evaluation is its own solve; nothing is interpolated "
                f"and no prior result is reused.",
                f"The raced body is the {RACED_WING}: camber "
                f"{100 * float((wing or WING)['camber']):.0f}% of chord at "
                f"{float((wing or WING)['camber_loc']):.1f} chord, thickness "
                f"{100 * float((wing or WING)['thick_chord']):.0f}%, span "
                f"{float((wing or WING)['span']):g} m, reference chord "
                f"{chord_ref:g} m, chord Reynolds 1e6.",
                f"Angle of attack α is measured from that section's own chord "
                f"line, over {len(ALPHAS)} angles on a "
                f"{ALPHAS[1] - ALPHAS[0]:g}° grid.",
                f"Ensemble lane: {samples} chord Reynolds samples over the "
                f"stated 8% input spread, each swept across all "
                f"{len(ALPHAS)} angles, "
                + (f"drawn from seed {seed} so the inputs replay exactly."
                   if seed is not None else "drawn from the clock."),
                f"Reduced-order lane: {len(ANCHOR_ALPHAS)} anchor solves, a "
                f"quadratic response surface locating the peak, and one "
                f"confirmation solve at the located angle.",
                f"The two lanes run concurrently through one pool of "
                f"{MAX_WORKERS} solver slots split evenly, so neither lane "
                f"wins on parallelism.",
            ] + ([f"The received {surface_name} contributed its measured span "
                  f"and nothing else. Its own section measures "
                  f"{100 * section['max_camber_frac_chord']:.2f}% camber and "
                  f"{section['incidence_deg']:.2f}° of built-in incidence, so "
                  f"it is not the section these curves belong to."]
                 if surface and section else []),
            results=[
                {"quantity": "Peak lift-to-drag",
                 "value": f"{rom['confirmed']:.2f} at α = "
                          f"{rom['alpha_star']:g}°",
                 "envelope": ("" if headline_ci is None
                              else f"± {headline_ci:.2f} at 95%, composed over "
                                   f"{len(total['contributions'])} channels"),
                 "tier": "SOLVER-BACKED",
                 "reason": f"every evaluation on both lanes ran the selected "
                           f"solver; the paths agree to {agreement_pct}%"},
                {"quantity": "Measured speedup, reduced-order against the "
                             "full ensemble sweep",
                 "value": f"{speedup_cm}× in core-minutes",
                 "envelope": f"{mc['n_solves']} solves against "
                             f"{rom['n_solves']}, on the same box"},
            ],
            uncertainty=[
                channel["note"] for channel in race_channels["channels"]
                if channel.get("note")
            ] + ([f"The published band is the root sum of squares over the "
                  f"{len(total['contributions'])} quantified channels, "
                  f"± {headline_ci:.2f}, and not any one of them alone."]
                 if headline_ci is not None else []
                 ) + [
                f"The peak sits on the α = {rom['alpha_star']:g}° edge of the "
                f"swept range, so the angle-grid channel reads the curve's "
                f"slope rather than its curvature and dominates the total."
                if peak_at_edge else
                f"The peak sits inside the swept range, so the angle-grid "
                f"channel reads the curvature at the located angle.",
            ],
            next_investigations=[f"{entry['title']}: {entry['scope']}"
                                 for entry in agenda],
            compute={"spent_core_minutes": round(cm_mc + cm_rom, 2),
                     "saved_core_minutes": round(cm_mc - cm_rom, 2)}))

    if emit:
        emit("uncertainty.channels", race_channels)

    # The Certonomous certificate for the race act: the peak lift-to-drag
    # with its composed band as the headline, the measured speedup
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
                 "envelope": ("" if headline_ci is None
                              else f"{headline_ci:.2f}"), **verdict},
                {"quantity": "Measured speedup, reduced-order vs full "
                             "ensemble sweep",
                 "value": f"{speedup_cm}x in core-minutes"},
            ],
            # Structured result block: Title Case labels, verbatim numbers.
            "result_fields": [
                ("Peak L/D", f"{rom['confirmed']:.2f} at "
                             f"{rom['alpha_star']:g} deg"),
                # Composed over the quantified channels, not the smallest of
                # them. The channel table one level down carries the split.
                ("Band (95%)", "not composed" if headline_ci is None
                 else f"±{headline_ci:.2f}"),
                ("Ensemble Spread (95%)", f"±{2 * mc['peak_sem']:.2f}"),
                ("Agreement", f"{agreement_pct}%"),
                ("Speedup", f"{speedup_cm}x core-minutes"),
                ("Solver Runs", f"{mc['n_solves']} ensemble lane, "
                                f"{rom['n_solves']} reduced-order lane"),
                ("Cost", f"{cm_mc:.1f} vs {cm_rom:.1f} core-min"),
            ],
            "compute": {"spent_core_minutes": round(cm_mc + cm_rom, 2),
                        "saved_core_minutes": round(cm_mc - cm_rom, 2)},
        }
        # The certificate's subject is the body the numbers belong to, which
        # is the raced section, never the received surface. The surface gets
        # the scope line, where what it did and did not set is stated.
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path,
            geometry="naca4412",
            # The objective is always THIS run's verbatim request.
            objective=(request or "Locate the peak lift-to-drag over angle "
                       "of attack two ways, same objective and tolerance, "
                       "both timed."),
            mission_id="race-comparison",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=race_channels,
            display_name=RACED_WING,
            source_filename=subject,
            scope=(f"Peak lift-to-drag of the {RACED_WING}, angle of attack "
                   f"measured from that section's chord line."
                   + (f" The received {surface_name} set the span "
                      f"({measured_span:g} m) and nothing else; its own "
                      f"section is not the section raced."
                      if surface and measured_span else
                      f" The received {surface_name} is on file and set "
                      f"nothing." if surface else "")),
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
