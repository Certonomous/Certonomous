"""The streamline overlay on the mid-span pressure slice.

Pure-piece coverage for the three new field_render building blocks (in-plane
velocity interpolation onto the slice grid, silhouette masking of the vector
field, upstream seed-line generation), the vector reader on a synthetic
foamToVTK-format volume file, an end-to-end render whose drawn strokes are
checked against the silhouette, and the render script's own pure helpers
(field sampling, integration, penetration measurement, solve-log parsing).
No solver output, no WSL, no network.
"""
from __future__ import annotations

import base64
import importlib.util
import math
import re
import struct
import tempfile
import unittest
from pathlib import Path

import numpy as np

from chief_engineer.field_render import (STREAM_SEEDS, inplane_velocity_grid,
                                         read_volume_vector,
                                         render_pressure_slice,
                                         silhouette_mask, streamline_seeds)
from tests.test_pressure_slice import (_BANNED, _binary_array, _box_mesh,
                                       _hex_grid)

SDK = Path(__file__).resolve().parents[1]


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "render_sail_streamlines",
        SDK / "scripts" / "render_sail_streamlines.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rss = _load_script()


def _write_vtu_with_velocity(path: Path, points, conn, offsets, p_values,
                             velocity) -> None:
    """A synthetic internal.vtu carrying both p and a 3-component U."""
    cells = len(offsets)
    flat_u = [c for vec in velocity for c in vec]
    body = (
        "<?xml version='1.0'?>\n"
        "<VTKFile type='UnstructuredGrid' version='0.1' "
        "byte_order='LittleEndian' header_type='UInt64'>\n"
        "<UnstructuredGrid>\n"
        f"<Piece NumberOfPoints='{len(points) // 3}' NumberOfCells='{cells}'>\n"
        "<Points>\n" + _binary_array("Points", "Float32", points, ncomp=3)
        + "\n</Points>\n<Cells>\n"
        + _binary_array("connectivity", "Int32", conn) + "\n"
        + _binary_array("offsets", "Int32", offsets) + "\n"
        + _binary_array("types", "UInt8", [12] * cells)
        + "\n</Cells>\n<CellData>\n"
        + _binary_array("p", "Float32", p_values) + "\n"
        + _binary_array("U", "Float32", flat_u, ncomp=3)
        + "\n</CellData>\n</Piece>\n</UnstructuredGrid>\n</VTKFile>\n")
    path.write_text(body, encoding="ascii")


# --------------------------------------------------------------------------
# In-plane velocity interpolation onto the slice grid
# --------------------------------------------------------------------------

class InplaneVelocityGridTests(unittest.TestCase):
    def test_linear_field_is_reproduced_exactly_inside_the_hull(self):
        # Linear interpolation on a triangulation is exact for linear data.
        rng = np.random.default_rng(3)
        u = rng.uniform(0.0, 1.0, 220)
        v = rng.uniform(0.0, 1.0, 220)
        vel_u = 2.0 * u - v + 1.0
        vel_v = 0.5 * v + 3.0
        grid_x = np.linspace(0.25, 0.75, 21)
        grid_y = np.linspace(0.25, 0.75, 17)
        uu, vv = inplane_velocity_grid(u, v, vel_u, vel_v, grid_x, grid_y)
        mesh_x, mesh_y = np.meshgrid(grid_x, grid_y)
        np.testing.assert_allclose(uu, 2.0 * mesh_x - mesh_y + 1.0,
                                   atol=1e-12)
        np.testing.assert_allclose(vv, 0.5 * mesh_y + 3.0, atol=1e-12)

    def test_outside_the_data_hull_is_nan(self):
        u = np.array([0.0, 1.0, 0.0, 1.0])
        v = np.array([0.0, 0.0, 1.0, 1.0])
        ones = np.ones(4)
        grid_x = np.linspace(-1.0, 2.0, 7)
        grid_y = np.linspace(0.0, 1.0, 3)
        uu, _ = inplane_velocity_grid(u, v, ones, ones, grid_x, grid_y)
        self.assertTrue(np.isnan(uu[:, 0]).all())   # x = -1, off the hull
        self.assertTrue(np.isfinite(uu[:, 3]).all())  # x = 0.5, inside

    def test_body_mask_blanks_the_vector_field(self):
        rng = np.random.default_rng(5)
        u = rng.uniform(0.0, 1.0, 120)
        v = rng.uniform(0.0, 1.0, 120)
        ones = np.ones(120)
        grid_x = np.linspace(0.3, 0.7, 9)
        grid_y = np.linspace(0.3, 0.7, 9)
        mask = np.zeros((9, 9), dtype=bool)
        mask[3:6, 3:6] = True
        uu, vv = inplane_velocity_grid(u, v, ones, ones, grid_x, grid_y,
                                       body_mask=mask)
        self.assertTrue(np.isnan(uu[mask]).all())
        self.assertTrue(np.isnan(vv[mask]).all())
        self.assertTrue(np.isfinite(uu[~mask]).all())


# --------------------------------------------------------------------------
# Silhouette masking (even-odd over the section loops)
# --------------------------------------------------------------------------

class SilhouetteMaskTests(unittest.TestCase):
    _SQUARE = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])

    def test_inside_and_outside_a_single_loop(self):
        points = np.array([[0.5, 0.5], [1.5, 0.5], [-0.1, 0.2], [0.9, 0.9]])
        inside = silhouette_mask(points, [self._SQUARE])
        np.testing.assert_array_equal(inside, [True, False, False, True])

    def test_nested_loop_carves_fluid_back_out(self):
        hole = np.array([[0.4, 0.4], [0.6, 0.4], [0.6, 0.6], [0.4, 0.6]])
        points = np.array([[0.5, 0.5], [0.2, 0.2]])
        inside = silhouette_mask(points, [self._SQUARE, hole])
        np.testing.assert_array_equal(inside, [False, True])

    def test_empty_and_degenerate_loops_mask_nothing(self):
        points = np.array([[0.5, 0.5]])
        self.assertFalse(silhouette_mask(points, None).any())
        self.assertFalse(silhouette_mask(points, []).any())
        self.assertFalse(
            silhouette_mask(points, [np.array([[0.0, 0.0], [1.0, 1.0]])])
            .any())

    def test_matches_the_render_fill_mask_definition(self):
        # The pressure fill and the streamline mask must share one inside
        # test: the extracted function is what render_slice_figure calls.
        source = (SDK / "chief_engineer" / "field_render.py").read_text(
            encoding="utf-8")
        self.assertIn("silhouette_mask(flat, silhouette)", source)


# --------------------------------------------------------------------------
# Upstream seed lines
# --------------------------------------------------------------------------

class StreamlineSeedsTests(unittest.TestCase):
    VIEW = (-0.5, 2.3, -0.8, 0.8)

    def test_seeds_sit_on_an_upstream_column_inside_the_view(self):
        seeds = streamline_seeds(self.VIEW)
        u_lo, u_hi, v_lo, v_hi = self.VIEW
        self.assertGreater(len(seeds), 0)
        np.testing.assert_allclose(seeds[:, 0],
                                   u_lo + 0.02 * (u_hi - u_lo))
        self.assertTrue((seeds[:, 1] > v_lo).all())
        self.assertTrue((seeds[:, 1] < v_hi).all())

    def test_centreline_is_always_seeded_and_count_is_odd(self):
        # The stagnation streamline needs a seed exactly on the centreline.
        for n in (8, 9, 15):
            seeds = streamline_seeds(self.VIEW, center_v=0.1, n_lines=n)
            self.assertEqual(len(seeds) % 2, 1)
            self.assertTrue(np.isclose(seeds[:, 1], 0.1).any())

    def test_spacing_is_denser_near_the_body_than_at_the_edges(self):
        seeds = streamline_seeds(self.VIEW, center_v=0.0,
                                 n_lines=STREAM_SEEDS)
        ys = np.sort(seeds[:, 1])
        gaps = np.diff(ys)
        centre_gap = gaps[len(gaps) // 2]
        self.assertLess(centre_gap, 0.5 * gaps.max())

    def test_default_centre_is_the_middle_of_the_view(self):
        seeds = streamline_seeds((0.0, 1.0, 2.0, 4.0), n_lines=5)
        self.assertTrue(np.isclose(seeds[:, 1], 3.0).any())


# --------------------------------------------------------------------------
# Vector reader on the synthetic wire format
# --------------------------------------------------------------------------

class ReadVolumeVectorTests(unittest.TestCase):
    def test_u_round_trips_as_c_by_3(self):
        points, conn, offsets, p_values = _hex_grid(3, 2, 2, d=0.5)
        velocity = [(1.0 + i, 2.0, 0.5) for i in range(len(offsets))]
        with tempfile.TemporaryDirectory() as tmp:
            vtu = Path(tmp) / "internal.vtu"
            _write_vtu_with_velocity(vtu, points, conn, offsets, p_values,
                                     velocity)
            got = read_volume_vector(vtu, "U")
        self.assertIsNotNone(got)
        vectors = got[3]
        self.assertEqual(vectors.shape, (len(offsets), 3))
        np.testing.assert_allclose(vectors, velocity, rtol=1e-6)

    def test_missing_field_returns_none(self):
        points, conn, offsets, p_values = _hex_grid(1, 1, 1)
        with tempfile.TemporaryDirectory() as tmp:
            vtu = Path(tmp) / "internal.vtu"
            _write_vtu_with_velocity(vtu, points, conn, offsets, p_values,
                                     [(1.0, 0.0, 0.0)])
            self.assertIsNone(read_volume_vector(vtu, "does_not_exist"))


# --------------------------------------------------------------------------
# End to end: strokes drawn, silhouette respected, register held
# --------------------------------------------------------------------------

class OverlayRenderTests(unittest.TestCase):
    def _render(self, tmp: str):
        # A block in a uniform stream: U = (1, 0, 0) everywhere the volume
        # has cells; the box silhouette must stay stroke-free.
        points, conn, offsets, p_values = _hex_grid(8, 1, 8, d=0.1)
        velocity = [(1.0, 0.0, 0.0)] * len(offsets)
        surface = _box_mesh((0.3, -1.0, 0.3), (0.5, 1.0, 0.5))
        vtu = Path(tmp) / "internal.vtu"
        _write_vtu_with_velocity(vtu, points, conn, offsets, p_values,
                                 velocity)
        out = Path(tmp) / "slice.png"
        meta = render_pressure_slice(
            vtu, out, span_axis=1, plane_axes=(0, 2),
            body_label="synthetic block", surface_mesh=surface,
            overlay_velocity_field="U")
        return meta, out

    def test_streamlines_ride_the_figure_and_avoid_the_silhouette(self):
        from chief_engineer.field_render import surface_cross_section

        with tempfile.TemporaryDirectory() as tmp:
            meta, out = self._render(tmp)
            self.assertIsNotNone(meta)
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 10_000)
        stream = meta["streamlines"]
        self.assertIsNotNone(stream)
        self.assertGreater(stream["n_seeds"], 0)
        self.assertGreater(len(stream["segments"]), 0)
        # No drawn point intrudes into the exact section of the box.
        surface = _box_mesh((0.3, -1.0, 0.3), (0.5, 1.0, 0.5))
        loops = surface_cross_section(surface[0], surface[1], axis=1,
                                      station=0.1, plane_axes=(0, 2))
        drawn = np.concatenate([s.reshape(-1, 2)
                                for s in stream["segments"]])
        self.assertEqual(rss.max_silhouette_penetration(drawn, loops), 0.0)
        # Uniform unit stream: the gridded speed reads 1 everywhere sampled.
        self.assertAlmostEqual(stream["speed_max"], 1.0, places=5)

    def test_no_velocity_keeps_the_pressure_only_figure(self):
        points, conn, offsets, p_values = _hex_grid(6, 1, 6, d=0.1)
        with tempfile.TemporaryDirectory() as tmp:
            vtu = Path(tmp) / "internal.vtu"
            _write_vtu_with_velocity(vtu, points, conn, offsets, p_values,
                                     [(1.0, 0.0, 0.0)] * len(offsets))
            out = Path(tmp) / "slice.png"
            meta = render_pressure_slice(vtu, out, span_axis=1,
                                         plane_axes=(0, 2))
            self.assertIsNotNone(meta)
            self.assertTrue(out.exists())
        self.assertIsNone(meta["streamlines"])
        self.assertNotIn("streamlines of the in-plane velocity",
                         meta["note"])

    def test_overlay_note_and_strings_hold_the_register(self):
        with tempfile.TemporaryDirectory() as tmp:
            meta, _ = self._render(tmp)
        self.assertIn("streamlines of the in-plane velocity", meta["note"])
        for text in (meta["title"], meta["xlabel"], meta["ylabel"],
                     meta["colorbar"], meta["note"], meta["annotation"]):
            hit = _BANNED.search(text)
            self.assertIsNone(hit, f"register break {hit and hit.group(0)!r}"
                                   f" in figure text: {text!r}")


# --------------------------------------------------------------------------
# Script helpers: sampling, integration, penetration, log parsing
# --------------------------------------------------------------------------

class BilinearSampleTests(unittest.TestCase):
    GRID_X = np.linspace(0.0, 1.0, 11)
    GRID_Y = np.linspace(0.0, 2.0, 21)

    def test_exact_on_a_bilinear_field(self):
        mesh_x, mesh_y = np.meshgrid(self.GRID_X, self.GRID_Y)
        field = 3.0 * mesh_x + 2.0 * mesh_y - 1.0
        self.assertAlmostEqual(
            rss.bilinear_sample(self.GRID_X, self.GRID_Y, field, 0.37, 1.13),
            3.0 * 0.37 + 2.0 * 1.13 - 1.0, places=12)

    def test_outside_the_grid_and_nan_corners_read_nan(self):
        field = np.ones((21, 11))
        field[10, 5] = np.nan
        self.assertTrue(math.isnan(rss.bilinear_sample(
            self.GRID_X, self.GRID_Y, field, -0.1, 1.0)))
        self.assertTrue(math.isnan(rss.bilinear_sample(
            self.GRID_X, self.GRID_Y, field, 0.51, 1.01)))


class IntegrateStreamlineTests(unittest.TestCase):
    def test_uniform_stream_runs_straight_to_the_edge(self):
        grid_x = np.linspace(0.0, 1.0, 51)
        grid_y = np.linspace(0.0, 1.0, 51)
        uu = np.ones((51, 51))
        vv = np.zeros((51, 51))
        path = rss.integrate_streamline(grid_x, grid_y, uu, vv, (0.02, 0.5))
        self.assertGreater(len(path), 10)
        np.testing.assert_allclose(path[:, 1], 0.5, atol=1e-9)
        self.assertGreater(path[-1, 0], 0.95)

    def test_nan_region_terminates_the_path(self):
        grid_x = np.linspace(0.0, 1.0, 51)
        grid_y = np.linspace(0.0, 1.0, 51)
        uu = np.ones((51, 51))
        vv = np.zeros((51, 51))
        uu[:, 30:] = np.nan
        path = rss.integrate_streamline(grid_x, grid_y, uu, vv, (0.02, 0.5))
        self.assertLess(path[-1, 0], 0.62)


class PenetrationTests(unittest.TestCase):
    SQUARE = [np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])]

    def test_outside_points_have_zero_penetration(self):
        points = np.array([[-0.5, 0.5], [1.5, 1.5], [0.5, -0.2]])
        self.assertEqual(
            rss.max_silhouette_penetration(points, self.SQUARE), 0.0)

    def test_inside_point_reports_distance_to_the_nearest_edge(self):
        points = np.array([[0.1, 0.5], [0.5, 0.98]])
        self.assertAlmostEqual(
            rss.max_silhouette_penetration(points, self.SQUARE), 0.1,
            places=12)


_LOG = """
Time = 137

smoothSolver:  Solving for Ux, Initial residual = 2e-05, Final residual = 1e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4e-05, Final residual = 3e-07, No Iterations 2
smoothSolver:  Solving for omega, Initial residual = 3e-05, Final residual = 2e-06, No Iterations 2
smoothSolver:  Solving for k, Initial residual = 5e-05, Final residual = 4e-06, No Iterations 2

forceCoeffs forceCoeffs1 write:
    Cd:	0.010151
    Cl:	-0.000289

Time = 138

smoothSolver:  Solving for Ux, Initial residual = 1.2284897e-05, Final residual = 6.4878479e-07, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 9.4107642e-05, Final residual = 7.3129074e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.0251612e-05, Final residual = 2.7445689e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.0964533e-06, Final residual = 9.8449964e-08, No Iterations 1
smoothSolver:  Solving for omega, Initial residual = 2.1855443e-05, Final residual = 1.3074385e-06, No Iterations 2
smoothSolver:  Solving for k, Initial residual = 4.3251e-05, Final residual = 3.6966135e-06, No Iterations 2

SIMPLE solution converged in 138 iterations

forceCoeffs forceCoeffs1 write:
    Cd:	0.010150841
    Cl:	-0.0002882335
"""


class LogParsingTests(unittest.TestCase):
    def test_last_iteration_residuals_take_the_final_block(self):
        iteration, residuals = rss.last_iteration_residuals(_LOG)
        self.assertEqual(iteration, 138)
        self.assertAlmostEqual(residuals["Ux"][0], 1.2284897e-05)
        self.assertAlmostEqual(residuals["Ux"][1], 6.4878479e-07)
        # p solved twice: initial from the first solve, final from the last.
        self.assertAlmostEqual(residuals["p"][0], 3.0251612e-05)
        self.assertAlmostEqual(residuals["p"][1], 9.8449964e-08)
        self.assertIn("k", residuals)
        self.assertIn("omega", residuals)

    def test_final_force_coefficients_are_the_last_written(self):
        cd, cl = rss.final_force_coefficients(_LOG)
        self.assertAlmostEqual(cd, 0.010150841)
        self.assertAlmostEqual(cl, -0.0002882335)

    def test_settle_bands_parse_the_report_rows(self):
        report = ("| Cd | **0.01015 ± 4e-06** (95% envelope "
                  "[0.01015, 0.01016], window 27) |\n"
                  "| Cl | **-0.0002874 ± 1.6e-06** (95% envelope "
                  "[-0.000289, -0.0002858], window 27) |\n")
        bands = rss.settle_bands(report)
        self.assertEqual(bands["Cd"]["value"], 0.01015)
        self.assertEqual(bands["Cd"]["half_band"], 4e-06)
        self.assertEqual(bands["Cd"]["envelope"], (0.01015, 0.01016))
        self.assertEqual(bands["Cl"]["window"], 27)


if __name__ == "__main__":
    unittest.main()
