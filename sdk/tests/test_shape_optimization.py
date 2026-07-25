"""Shape-optimization act: the gradient-descent presentation layer.

Three contracts pinned here, from the website round (owner order, 2026-07-25):

1. **The descent is real mathematics on the calibrated model.** The fitted
   quadratic is differentiable; ``descend`` walks its analytic gradient with a
   fixed, bounded step and returns the full trajectory. Known coefficients
   produce the known trajectory, interior minima converge, and a bound pins
   the walk exactly at the bound. No interpolation, no padding.

2. **The act never speaks the sampling story.** "Real solve(s)", "design(s)
   evaluated" and every variants-tried-and-picked phrasing are banned from
   every emitted surface: transcript, dispatch, roster, report, verdict,
   agenda, ledger notes, channel notes. The house banned words (stored,
   saved, cached, recorded, demo, trend, live, solver backed prose,
   conceptual model, em dash) ride the same walk.

3. **One frame per computed trajectory point.** The renderer emits exactly as
   many frames as there are ``descent.step`` events, and clears stale frames.
"""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SDK = Path(__file__).resolve().parents[1]

import workflows.shape_optimization as so
from chief_engineer.monte_carlo import EnsembleResult


# --------------------------------------------------------------------------
# 1. The descent, as a pure function
# --------------------------------------------------------------------------

class DescentOnModelTests(unittest.TestCase):
    """descend() is honest gradient descent on the fitted surface."""

    def test_known_quadratic_converges_to_interior_minimum(self):
        # f(x) = (x - 2)^2  ->  coefficients [4, -4, 1], minimum at x = 2.
        c = [4.0, -4.0, 1.0]
        path = so.descend(c, 0.5, 0.0, 3.0)
        self.assertAlmostEqual(path[-1]["x"], 2.0, delta=0.005)
        # Gradient magnitude at the stop is inside the tolerance band.
        scale = max(abs(so._gradient(c, 0.0)), abs(so._gradient(c, 3.0)))
        self.assertLessEqual(abs(path[-1]["gradient"]), 2e-3 * scale)

    def test_bound_pins_the_walk_exactly_at_the_bound(self):
        # Same bowl, but the feasible range ends before the minimum: the
        # projected gradient vanishes at the bound and the walk stops there.
        c = [4.0, -4.0, 1.0]
        path = so.descend(c, 0.2, 0.0, 1.0)
        self.assertEqual(path[-1]["x"], 1.0)
        # The raw gradient still points beyond the bound.
        self.assertLess(path[-1]["gradient"], 0.0)

    def test_explicit_step_reproduces_the_closed_form_trajectory(self):
        # f(x) = x^2, gradient 2x, step 0.1: x_{k+1} = 0.8 x_k exactly.
        c = [0.0, 0.0, 1.0]
        path = so.descend(c, 1.0, -1.0, 1.0, step=0.1)
        for k, point in enumerate(path[:6]):
            self.assertAlmostEqual(point["x"], 0.8 ** k, places=12)

    def test_objective_never_increases_along_the_walk(self):
        c = [4.0, -4.0, 1.0]
        for start, lo, hi in ((0.5, 0.0, 3.0), (0.2, 0.0, 1.0), (3.0, 0.0, 3.0)):
            objs = [p["objective"] for p in so.descend(c, start, lo, hi)]
            for a, b in zip(objs, objs[1:]):
                self.assertLessEqual(b, a + 1e-12)

    def test_every_move_respects_the_step_rule(self):
        c = [4.0, -4.0, 1.0]
        lo, hi = 0.0, 3.0
        path = so.descend(c, 0.1, lo, hi)
        bound = (hi - lo) / so.DESCENT_STEP_DIVISOR + 1e-12
        for a, b in zip(path, path[1:]):
            self.assertLessEqual(abs(b["x"] - a["x"]), bound)

    def test_trajectory_records_carry_the_true_model_values(self):
        c = [5.989, -5.9498, 1.9605]
        for point in so.descend(c, 1.0, 0.7, 1.4):
            self.assertAlmostEqual(point["objective"],
                                   so._predict(c, point["x"]), places=12)
            self.assertAlmostEqual(point["gradient"],
                                   so._gradient(c, point["x"]), places=12)

    def test_step_count_is_honest_and_bounded(self):
        c = [4.0, -4.0, 1.0]
        path = so.descend(c, 0.5, 0.0, 3.0, max_steps=7)
        self.assertLessEqual(len(path) - 1, 7)


# --------------------------------------------------------------------------
# 2. Register walk over everything the act emits
# --------------------------------------------------------------------------

class _Capacity:
    def __init__(self, fits, capacity=3):
        self.fits = fits
        self.capacity = capacity

    def headline(self):
        return "Compute audit stub"

    def panel(self):
        return {"verdict": "FITS" if self.fits else "CONSTRAINED"}


def _fake_solve(design, work_root, tag):
    d = design["cylinder_diameter"]
    return {"Cd": round(2.0 / d, 5), "converged": 1.0, "Re": 20.0 * d}


def _fake_ensemble(nominal, uncertain, **kwargs):
    values = [1.51, 1.49, 1.50, 1.52, 1.48, 1.50,
              1.51, 1.49, 1.50, 1.50, 1.51, 1.49]
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    sigma = var ** 0.5
    sem = sigma / len(values) ** 0.5
    return EnsembleResult(
        metric="Cd", samples=[], values=values, mean=mean,
        ensemble_sigma=sigma, standard_error=sem,
        ci95=(mean - 2 * sem, mean + 2 * sem), wall_seconds=1.0, workers=2)


def _collect_strings(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for value in obj.values():
            _collect_strings(value, out)
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            _collect_strings(value, out)


def _run_act(force_scarce, fits):
    events = []
    tmp = Path(tempfile.mkdtemp())
    try:
        with mock.patch.object(so, "_solve", _fake_solve), \
                mock.patch.object(so, "audit",
                                  lambda *a, **k: _Capacity(fits)), \
                mock.patch.object(so, "run_ensemble", _fake_ensemble), \
                mock.patch.object(so, "plot_convergence",
                                  lambda *a, **k: None), \
                mock.patch.object(so, "OUT_ROOT", tmp):
            rc = so.main(request="Minimise drag on the cylinder body",
                         force_scarce=force_scarce,
                         emit=lambda e, p: events.append((e, p)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return rc, events


class ActRegisterTests(unittest.TestCase):
    """Both branches of the act, walked end to end with the solver stubbed,
    every emitted string checked against the hard rules."""

    # The owner's two hard-banned families plus the house banned words.
    _BANNED = (
        ("real solve", re.compile(r"real[ -]solves?", re.IGNORECASE)),
        ("designs evaluated",
         re.compile(r"designs?\s+(?:\w+\s+)?evaluat", re.IGNORECASE)),
        ("evaluated designs",
         re.compile(r"evaluat\w*\s+designs?", re.IGNORECASE)),
        ("design evaluation",
         re.compile(r"design\s+evaluations?", re.IGNORECASE)),
        ("stored", re.compile(r"\bstored\b", re.IGNORECASE)),
        ("saved", re.compile(r"\bsaved\b", re.IGNORECASE)),
        ("cached", re.compile(r"\bcached\b", re.IGNORECASE)),
        ("recorded", re.compile(r"\brecorded\b", re.IGNORECASE)),
        ("demo", re.compile(r"\bdemos?\b", re.IGNORECASE)),
        ("trend", re.compile(r"\btrends?\b", re.IGNORECASE)),
        ("live label", re.compile(r"\blive\b", re.IGNORECASE)),
        ("solver backed prose", re.compile(r"solver[ -]backed")),
        ("conceptual model", re.compile(r"conceptual model", re.IGNORECASE)),
        ("em dash", re.compile("—")),
        ("arrow glyph", re.compile("→")),
    )

    @classmethod
    def setUpClass(cls):
        cls.runs = {}
        rc, events = _run_act(force_scarce=True, fits=False)
        assert rc == 0
        cls.runs["staged"] = events
        rc, events = _run_act(force_scarce=False, fits=True)
        assert rc == 0
        cls.runs["one-wave"] = events

    def _all_strings(self, events):
        out = []
        for _event, payload in events:
            _collect_strings(payload, out)
        return out

    def test_no_banned_phrase_on_any_emitted_surface(self):
        for branch, events in self.runs.items():
            strings = self._all_strings(events)
            self.assertTrue(strings, branch)
            for text in strings:
                for name, pattern in self._BANNED:
                    self.assertFalse(
                        pattern.search(text),
                        f"{branch}: [{name}] in {text!r}")

    def test_staged_branch_tells_the_gradient_story(self):
        messages = [p.get("message", "") for e, p in self.runs["staged"]
                    if e == "transcript.entry"]
        joined = "\n".join(messages)
        self.assertIn("solver runs calibrate the model; the geometry then "
                      "follows the design gradient", joined)
        self.assertIn("The converged shape is confirmed with a solver run",
                      joined)
        self.assertIn("Gradient descent on the model", joined)

    def test_descent_trajectory_is_emitted_and_consistent(self):
        steps = [p for e, p in self.runs["staged"] if e == "descent.step"]
        self.assertGreaterEqual(len(steps), 2)
        self.assertEqual([p["step"] for p in steps], list(range(len(steps))))
        objs = [p["objective"] for p in steps]
        for a, b in zip(objs, objs[1:]):
            self.assertLessEqual(b, a + 1e-12)
        confirm = next(p for e, p in self.runs["staged"]
                       if e == "confirmation.solve")
        self.assertEqual(confirm["D"], steps[-1]["D"])
        self.assertEqual(confirm["steps"], len(steps) - 1)

    def test_calibration_runs_are_on_the_record(self):
        calibration = [p for e, p in self.runs["staged"]
                       if e == "calibration.solve"]
        self.assertGreaterEqual(len(calibration), 3)
        for run in calibration:
            self.assertEqual(run["converged"], 1)


# --------------------------------------------------------------------------
# 3. Frame count equals the computed trajectory, exactly
# --------------------------------------------------------------------------

def _load_renderer():
    spec = importlib.util.spec_from_file_location(
        "render_shape_optimization_frames",
        SDK / "scripts" / "render_shape_optimization_frames.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FrameRenderTests(unittest.TestCase):
    def setUp(self):
        self.renderer = _load_renderer()
        self.out = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def _events(self):
        # A real descent on known coefficients; nothing hand-drawn.
        c = [4.0, -4.0, 1.0]
        path = so.descend(c, 0.5, 0.0, 3.0, step=0.3)
        events = [{"t": 0.0, "event": "descent.step",
                   "payload": {"step": i, "D": p["x"],
                               "objective": p["objective"],
                               "gradient": p["gradient"]}}
                  for i, p in enumerate(path)]
        for i, (d, cd) in enumerate(((0.9, 2.22), (1.0, 2.0), (1.1, 1.82))):
            events.append({"t": 0.0, "event": "calibration.solve",
                           "payload": {"name": f"a{i}", "D": d, "Cd": cd,
                                       "converged": 1}})
        events.append({"t": 0.0, "event": "confirmation.solve",
                       "payload": {"D": path[-1]["x"], "Cd": 0.02,
                                   "model": path[-1]["objective"],
                                   "error": 0.01, "steps": len(path) - 1}})
        events.append({"t": 0.0, "event": "result.verdict",
                       "payload": {"quantity": "Drag coefficient",
                                   "value": "0.02", "ci": "0.004",
                                   "confidence": "95%",
                                   "envelope": "12-sample ensemble"}})
        return events, len(path)

    def test_one_frame_per_descent_step_event(self):
        events, n_points = self._events()
        steps, calibration, confirmation, verdict = \
            self.renderer.trajectory(events)
        self.assertEqual(len(steps), n_points)
        count = self.renderer.render(steps, calibration, confirmation,
                                     verdict, self.out)
        frames = sorted(self.out.glob("frame_*.png"))
        self.assertEqual(count, n_points)
        self.assertEqual(len(frames), n_points)
        self.assertEqual(frames[0].name, "frame_0001.png")
        self.assertEqual(frames[-1].name, f"frame_{n_points:04d}.png")

    def test_stale_frames_are_cleared_before_rendering(self):
        events, n_points = self._events()
        self.out.mkdir(parents=True, exist_ok=True)
        stale = self.out / "frame_9999.png"
        stale.write_bytes(b"stale")
        steps, calibration, confirmation, verdict = \
            self.renderer.trajectory(events)
        self.renderer.render(steps, calibration, confirmation, verdict,
                             self.out)
        self.assertFalse(stale.exists())
        self.assertEqual(len(list(self.out.glob("frame_*.png"))), n_points)

    def test_no_trajectory_means_no_frames_and_a_clean_refusal(self):
        steps, calibration, confirmation, verdict = \
            self.renderer.trajectory([])
        self.assertEqual(steps, [])


if __name__ == "__main__":
    unittest.main()
