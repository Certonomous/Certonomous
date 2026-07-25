"""Pure-function coverage for the pressure-field validation script.

The script's extraction and comparison arithmetic (Cp conversion, polygon
geometry, mid-span banding, mirror-symmetry residuals, the section normal
force, and deviation statistics against a reference survey) is exercised on
synthetic data with known answers. No solver output, no WSL, no network.
"""
from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

import numpy as np

SDK = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "validate_pressure_fields",
        SDK / "scripts" / "validate_pressure_fields.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vpf = _load()


class CpConversionTests(unittest.TestCase):
    def test_kinematic_units_no_density_factor(self):
        # p is p over rho: at U = 75, q = 2812.5 m2/s2 exactly.
        cp = vpf.cp_from_kinematic([2812.5, 0.0, -1406.25], 0.0, 75.0)
        np.testing.assert_allclose(cp, [1.0, 0.0, -0.5])

    def test_p_inf_offset_is_subtracted(self):
        cp = vpf.cp_from_kinematic([112.5 + 5.0], 5.0, 15.0)
        np.testing.assert_allclose(cp, [1.0])

    def test_rejects_zero_velocity(self):
        with self.assertRaises(ValueError):
            vpf.cp_from_kinematic([1.0], 0.0, 0.0)


class PolygonGeometryTests(unittest.TestCase):
    def test_unit_square_centroid_normal_area(self):
        verts = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        c, n, a = vpf.polygon_geometry(verts, [[0, 1, 2, 3]])
        np.testing.assert_allclose(c[0], [0.5, 0.5, 0.0])
        np.testing.assert_allclose(n[0], [0.0, 0.0, 1.0], atol=1e-12)
        self.assertAlmostEqual(a[0], 1.0)

    def test_winding_flips_normal(self):
        verts = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        _, n, _ = vpf.polygon_geometry(verts, [[3, 2, 1, 0]])
        np.testing.assert_allclose(n[0], [0.0, 0.0, -1.0], atol=1e-12)


class BandAndBinningTests(unittest.TestCase):
    def test_midspan_band_widens_until_populated(self):
        coords = np.linspace(-1.5, 1.5, 601)  # spacing 0.005
        mask, half = vpf.midspan_band(coords, 0.0, 0.001, min_count=20)
        self.assertGreaterEqual(int(mask.sum()), 20)
        self.assertGreater(half, 0.001)

    def test_cosine_edges_cluster_at_ends(self):
        edges = vpf.cosine_edges(10)
        self.assertAlmostEqual(edges[0], 0.0)
        self.assertAlmostEqual(edges[-1], 1.0)
        self.assertTrue(np.all(np.diff(edges) > 0))
        # End bins are narrower than the middle bin.
        self.assertLess(edges[1] - edges[0], edges[6] - edges[5])

    def test_chord_fraction_normalises(self):
        xc = vpf.chord_fraction([0.2, 0.7, 1.2], 0.2, 1.2)
        np.testing.assert_allclose(xc, [0.0, 0.5, 1.0])

    def test_binned_curve_means_and_skips_empty(self):
        xc = np.array([0.05, 0.06, 0.95])
        cp = np.array([1.0, 3.0, -1.0])
        centers, means, counts = vpf.binned_curve(xc, cp, [0.0, 0.1, 0.9, 1.0])
        np.testing.assert_allclose(centers, [0.05, 0.95])
        np.testing.assert_allclose(means, [2.0, -1.0])
        np.testing.assert_array_equal(counts, [2, 1])


class SymmetryTests(unittest.TestCase):
    def test_perfect_mirror_has_zero_residual(self):
        xc = np.linspace(0.01, 0.99, 50)
        cp = -0.5 * np.sin(math.pi * xc)
        sym = vpf.symmetry_residual(xc, cp, xc, cp.copy(),
                                    vpf.cosine_edges(20))
        self.assertEqual(sym["max_abs"], 0.0)
        self.assertEqual(sym["mean_abs"], 0.0)
        self.assertGreater(sym["bins_compared"], 10)

    def test_known_offset_is_measured(self):
        xc = np.linspace(0.01, 0.99, 50)
        cp = -0.5 * np.sin(math.pi * xc)
        sym = vpf.symmetry_residual(xc, cp, xc, cp + 0.02,
                                    vpf.cosine_edges(20))
        self.assertAlmostEqual(sym["max_abs"], 0.02, places=12)
        self.assertAlmostEqual(sym["mean_abs"], 0.02, places=12)


class NormalForceTests(unittest.TestCase):
    def test_constant_loading_integrates_to_the_constant(self):
        xc = np.linspace(0.0, 1.0, 80)
        cn = vpf.normal_force_from_cp(xc, np.full_like(xc, -0.6),
                                      xc, np.full_like(xc, 0.4))
        self.assertAlmostEqual(cn, 1.0, places=10)

    def test_swapped_surfaces_flip_the_sign(self):
        xc = np.linspace(0.0, 1.0, 80)
        upper = np.full_like(xc, -0.6)
        lower = np.full_like(xc, 0.4)
        cn = vpf.normal_force_from_cp(xc, lower, xc, upper)
        self.assertAlmostEqual(cn, -1.0, places=10)

    def test_disjoint_surveys_are_rejected(self):
        with self.assertRaises(ValueError):
            vpf.normal_force_from_cp([0.0, 0.1], [1, 1], [0.5, 0.9], [1, 1])


class DeviationTests(unittest.TestCase):
    def test_identical_curves_deviate_zero(self):
        x = np.linspace(0.0, 1.0, 30)
        cp = np.cos(x)
        stats = vpf.deviation_stats(x, cp, x, cp.copy())
        self.assertAlmostEqual(stats["rms"], 0.0)
        self.assertAlmostEqual(stats["max_abs"], 0.0)
        self.assertEqual(stats["n_stations"], 30)

    def test_uniform_bias_is_reported_exactly(self):
        x = np.linspace(0.0, 1.0, 30)
        cp = np.cos(x)
        stats = vpf.deviation_stats(x, cp, x, cp + 0.05)
        self.assertAlmostEqual(stats["rms"], 0.05, places=12)
        self.assertAlmostEqual(stats["max_abs"], 0.05, places=12)

    def test_reference_outside_survey_is_excluded(self):
        stats = vpf.deviation_stats([0.0, 0.5, 2.0], [1, 1, 99],
                                    [0.0, 1.0], [1, 1])
        self.assertEqual(stats["n_stations"], 2)
        self.assertAlmostEqual(stats["max_abs"], 0.0)


class PinkertonTableTests(unittest.TestCase):
    def test_surfaces_split_and_cover_the_chord(self):
        upper, lower = vpf.pinkerton_surfaces(3)
        self.assertGreaterEqual(len(upper), 25)
        self.assertGreaterEqual(len(lower), 20)
        for surf in (upper, lower):
            self.assertGreaterEqual(surf[:, 0].min(), 0.0)
            self.assertLessEqual(surf[:, 0].max(), 1.0)
            self.assertTrue(np.all(np.diff(surf[:, 0]) >= 0))

    def test_alpha_zero_column_hits_published_anchor_values(self):
        upper, lower = vpf.pinkerton_surfaces(3)
        # Leading-edge orifice 41 reads P = 1.010 at alpha 0 (Table I).
        self.assertAlmostEqual(float(upper[0, 1]), 1.010)
        # Trailing-edge orifice 28 reads P = 0.200 on the lower path.
        self.assertAlmostEqual(float(lower[-1, 1]), 0.200)

    def test_nearest_alpha_selection(self):
        self.assertEqual(vpf.nearest_pinkerton_alpha(0.317), 0.0)
        self.assertEqual(vpf.nearest_pinkerton_alpha(0.15), -2.0)
        self.assertEqual(vpf.nearest_pinkerton_alpha(0.55), 2.0)


if __name__ == "__main__":
    unittest.main()
