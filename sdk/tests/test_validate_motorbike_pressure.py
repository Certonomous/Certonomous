"""Pure-function coverage for the motorbike / B-52 pressure-field validation.

Everything the verdict rests on that is arithmetic rather than solver output
is exercised here on synthetic data with hand-checkable answers: face-normal
alignment against the flow, area-weighted percentiles, binned profiles and
their delta, shared-edge neighbour correlation (the statistic that separates
a smooth painted field from the pre-fix truncation paint), the display
pipeline's percentile colour window and its legacy stride arithmetic, region
boxes, connected components, the GUI's orphan-island display filter together
with the alignment proof for its survivors, and the stagnation-bound
exceedance report. No solver output, no WSL, no network.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np

SDK = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "validate_motorbike_pressure",
        SDK / "scripts" / "validate_motorbike_pressure.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vmp = _load()


def _grid_mesh(nx: int, ny: int):
    """A flat (nx+1) x (ny+1) vertex grid triangulated into 2*nx*ny faces."""
    verts = [[float(i), float(j), 0.0]
             for j in range(ny + 1) for i in range(nx + 1)]
    faces = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            b = a + 1
            c = a + (nx + 1)
            d = c + 1
            faces.append([a, b, d])
            faces.append([a, d, c])
    return verts, faces


class AlignmentTests(unittest.TestCase):
    def test_face_on_surface_is_fully_forward(self):
        stats = vmp.alignment_stats([[1.0, 0.0, 0.0]] * 4)
        self.assertEqual(stats["frac_forward"], 1.0)
        self.assertAlmostEqual(stats["mean_dot"], 1.0)
        self.assertEqual(stats["count"], 4)

    def test_rear_facing_surface_is_never_forward(self):
        stats = vmp.alignment_stats([[-1.0, 0.0, 0.0], [-0.5, 0.5, 0.7]])
        self.assertEqual(stats["frac_forward"], 0.0)
        self.assertLess(stats["mean_dot"], 0.0)

    def test_flow_axis_is_honoured(self):
        normals = [[0.0, 0.0, 1.0]] * 3
        self.assertEqual(vmp.alignment_stats(normals, 2)["frac_forward"], 1.0)
        self.assertEqual(vmp.alignment_stats(normals, 0)["frac_forward"], 0.0)

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            vmp.alignment_stats(np.zeros((0, 3)))


class AreaWeightedPercentileTests(unittest.TestCase):
    def test_equal_areas_reproduce_the_median(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        median = vmp.area_weighted_percentiles(values, [1.0] * 5, [50])[0]
        self.assertAlmostEqual(median, 3.0)

    def test_a_dominant_area_pulls_the_median_to_its_value(self):
        # One face carries 99% of the surface: the median must be its value,
        # even though four of five faces read something else.
        values = [-10.0, -10.0, 7.0, -10.0, -10.0]
        areas = [0.0025, 0.0025, 0.99, 0.0025, 0.0025]
        median = vmp.area_weighted_percentiles(values, areas, [50])[0]
        # Interpolated on cumulative area, so it lands just inside the big
        # face's value rather than exactly on it.
        self.assertGreater(median, 6.5)
        self.assertLessEqual(median, 7.0)
        # Unweighted, the same data would report -10.
        self.assertAlmostEqual(float(np.median(values)), -10.0)

    def test_mismatched_lengths_rejected(self):
        with self.assertRaises(ValueError):
            vmp.area_weighted_percentiles([1.0, 2.0], [1.0], [50])


class BinnedProfileTests(unittest.TestCase):
    def test_weighted_means_per_bin_and_empty_bins_skipped(self):
        x = np.array([0.1, 0.2, 2.5])
        v = np.array([1.0, 3.0, -4.0])
        w = np.array([3.0, 1.0, 1.0])
        centers, means, counts = vmp.binned_mean_profile(
            x, v, w, [0.0, 1.0, 2.0, 3.0])
        np.testing.assert_allclose(centers, [0.5, 2.5])
        np.testing.assert_allclose(means, [1.5, -4.0])
        np.testing.assert_array_equal(counts, [2, 1])

    def test_identical_profiles_have_zero_delta(self):
        centers = np.linspace(0.0, 1.0, 11)
        means = np.sin(centers)
        delta = vmp.profile_delta(centers, means, centers, means.copy())
        self.assertAlmostEqual(delta["rms"], 0.0)
        self.assertAlmostEqual(delta["max_abs"], 0.0)
        self.assertEqual(delta["bins"], 11)

    def test_delta_reports_the_worst_bin_position(self):
        centers = np.array([0.0, 1.0, 2.0])
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([0.0, 0.0, 0.5])
        delta = vmp.profile_delta(centers, a, centers, b)
        self.assertAlmostEqual(delta["max_abs"], 0.5)
        self.assertAlmostEqual(delta["worst_x"], 2.0)

    def test_disjoint_profiles_report_no_common_bins(self):
        delta = vmp.profile_delta([0.0], [1.0], [9.0], [1.0])
        self.assertEqual(delta["bins"], 0)


class NeighbourCorrelationTests(unittest.TestCase):
    def test_shared_edges_are_found_once_each(self):
        # Two triangles sharing the diagonal 1-2.
        pairs = vmp.face_edge_pairs([[0, 1, 2], [1, 3, 2]])
        self.assertEqual(pairs, [(0, 1)])

    def test_boundary_edges_pair_nothing(self):
        self.assertEqual(vmp.face_edge_pairs([[0, 1, 2]]), [])

    def test_smooth_field_correlates_and_a_shuffle_does_not(self):
        verts, faces = _grid_mesh(14, 14)
        centroid_x = [np.mean([verts[i][0] for i in f]) for f in faces]
        smooth = np.sin(np.asarray(centroid_x) * 0.4)
        r_smooth, pairs = vmp.neighbor_correlation(faces, smooth)
        self.assertGreater(pairs, 100)
        self.assertGreater(r_smooth, 0.9)
        shuffled = np.random.default_rng(0).permutation(smooth)
        r_shuffled, _ = vmp.neighbor_correlation(faces, shuffled)
        self.assertLess(abs(r_shuffled), 0.2)

    def test_constant_field_has_no_defined_correlation(self):
        verts, faces = _grid_mesh(4, 4)
        r, pairs = vmp.neighbor_correlation(faces, np.ones(len(faces)))
        self.assertTrue(np.isnan(r))
        self.assertGreater(pairs, 0)


class DisplayWindowTests(unittest.TestCase):
    def test_percentile_window_trims_the_spike(self):
        values = list(range(100)) + [10_000.0]
        lo, hi = vmp.percentile_window(values)
        self.assertEqual(lo, 2.0)
        self.assertLess(hi, 100.0)

    def test_window_matches_the_pipeline_index_arithmetic(self):
        values = [float(v) for v in range(50)]
        lo, hi = vmp.percentile_window(values)
        ordered = sorted(values)
        self.assertEqual(lo, ordered[int(0.02 * 50)])
        self.assertEqual(hi, ordered[int(0.98 * 50)])

    def test_empty_values_rejected(self):
        with self.assertRaises(ValueError):
            vmp.percentile_window([])

    def test_legacy_paint_truncates_rather_than_maps(self):
        # The pre-fix pipeline had stride 1 and took the first N values, so a
        # 10-face display body wore the first 10 of 100 source values.
        source = [float(v) for v in range(100)]
        values, lo, hi = vmp.legacy_display_values(source, 100, 10)
        self.assertEqual(values, source[:10])
        self.assertEqual(lo, 0.0)
        self.assertEqual(hi, 9.0)

    def test_legacy_window_comes_from_the_truncated_subset(self):
        # Source values span 0..999 but the display window sees only 0..9.
        source = [float(v) for v in range(1000)]
        _, lo, hi = vmp.legacy_display_values(source, 1000, 10)
        self.assertLess(hi, 10.0)


class RegionShareTests(unittest.TestCase):
    def test_first_matching_box_claims_the_face(self):
        regions = (("inner", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
                   ("outer", (-5.0, -5.0, -5.0), (5.0, 5.0, 5.0)))
        shares = vmp.region_shares([[0.5, 0.5, 0.5]], [True], regions)
        self.assertAlmostEqual(shares["inner"], 1.0)
        self.assertAlmostEqual(shares["outer"], 0.0)

    def test_shares_sum_to_one_over_the_selected_faces(self):
        regions = (("box", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),)
        centroids = [[0.5, 0.5, 0.5], [9.0, 9.0, 9.0], [0.2, 0.2, 0.2]]
        shares = vmp.region_shares(centroids, [True, True, False], regions)
        self.assertAlmostEqual(sum(shares.values()), 1.0)
        self.assertAlmostEqual(shares["box"], 0.5)
        self.assertAlmostEqual(shares["elsewhere"], 0.5)


class ComponentAndOrphanTests(unittest.TestCase):
    def _two_islands(self):
        verts, faces = _grid_mesh(10, 10)          # 200 faces
        base = len(verts)
        verts += [[100.0, 0.0, 0.0], [101.0, 0.0, 0.0], [100.0, 1.0, 0.0],
                  [101.0, 1.0, 0.0]]
        faces += [[base, base + 1, base + 3], [base, base + 3, base + 2]]
        return verts, faces

    def test_components_are_counted_largest_first(self):
        verts, faces = self._two_islands()
        sizes, roots = vmp.component_sizes(verts, faces)
        self.assertEqual(sizes, [200, 2])
        self.assertEqual(len(roots), len(faces))

    def test_a_vertex_soup_still_unifies_by_position(self):
        # Two triangles that share an edge geometrically but not by index.
        verts = [[0, 0, 0], [1, 0, 0], [0, 1, 0],
                 [1, 0, 0], [0, 1, 0], [1, 1, 0]]
        faces = [[0, 1, 2], [3, 5, 4]]
        sizes, _ = vmp.component_sizes(verts, faces)
        self.assertEqual(sizes, [2])

    def test_orphan_island_is_dropped_and_values_follow(self):
        verts, faces = self._two_islands()
        values = [float(i) for i in range(len(faces))]
        out = vmp.drop_orphan_islands(verts, faces, values)
        self.assertTrue(out["filtered"])
        self.assertEqual(out["dropped"], 2)
        self.assertEqual(len(out["faces"]), 200)
        self.assertEqual(out["values"], values[:200])
        # The re-pack must not leave the island's vertices behind.
        self.assertEqual(len(out["vertices"]), len(verts) - 4)

    def test_survivor_alignment_proof_passes_on_the_real_filter(self):
        verts, faces = self._two_islands()
        values = [float(i) for i in range(len(faces))]
        out = vmp.drop_orphan_islands(verts, faces, values)
        proof = vmp.orphan_filter_alignment(verts, faces, values, out)
        self.assertTrue(proof["values_aligned"])
        self.assertTrue(proof["corner_positions_preserved"])
        self.assertEqual(proof["worst_corner_error"], 0.0)
        self.assertEqual(proof["faces_out"], 200)

    def test_survivor_alignment_proof_catches_a_shifted_value_list(self):
        verts, faces = self._two_islands()
        values = [float(i) for i in range(len(faces))]
        out = vmp.drop_orphan_islands(verts, faces, values)
        out["values"] = out["values"][1:] + [0.0]      # off-by-one paint
        proof = vmp.orphan_filter_alignment(verts, faces, values, out)
        self.assertFalse(proof["values_aligned"])

    def test_survivor_alignment_proof_catches_a_broken_remap(self):
        verts, faces = self._two_islands()
        out = vmp.drop_orphan_islands(verts, faces, None)
        out["faces"] = [[(i + 1) % len(out["vertices"]) for i in f]
                        for f in out["faces"]]
        proof = vmp.orphan_filter_alignment(verts, faces, None, out)
        self.assertFalse(proof["corner_positions_preserved"])
        self.assertGreater(proof["worst_corner_error"], 0.0)

    def test_single_component_body_is_left_alone(self):
        verts, faces = _grid_mesh(6, 6)
        out = vmp.drop_orphan_islands(verts, faces, None)
        self.assertFalse(out["filtered"])
        self.assertEqual(out["dropped"], 0)
        self.assertEqual(len(out["faces"]), len(faces))

    def test_cap_protects_real_geometry(self):
        # Two halves of comparable size: dropping either would exceed the 3%
        # cap, so nothing is cut even though one is under the 1% threshold.
        verts, faces = _grid_mesh(4, 4)             # 32 faces
        base = len(verts)
        verts += [[50.0, 0.0, 0.0], [51.0, 0.0, 0.0], [50.0, 1.0, 0.0]]
        faces += [[base, base + 1, base + 2]]
        out = vmp.drop_orphan_islands(verts, faces, None)
        self.assertFalse(out["filtered"])
        self.assertEqual(len(out["faces"]), len(faces))

    def test_tiny_payloads_short_circuit_like_the_gui(self):
        verts = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
        out = vmp.drop_orphan_islands(verts, [[0, 1, 2]], [1.0])
        self.assertFalse(out["filtered"])
        self.assertEqual(out["kept"], [0])

    def test_value_length_mismatch_rejected(self):
        verts, faces = _grid_mesh(4, 4)
        with self.assertRaises(ValueError):
            vmp.drop_orphan_islands(verts, faces, [1.0])


class ExceedanceTests(unittest.TestCase):
    def test_no_exceedance_reports_zero_and_the_maximum(self):
        stats = vmp.exceedance_stats([1.0, 2.0], [1.0, 1.0],
                                     [[0, 0, 0], [1, 1, 1]], limit=5.0)
        self.assertEqual(stats["count"], 0)
        self.assertEqual(stats["area_fraction"], 0.0)
        self.assertIsNone(stats["bbox"])
        self.assertEqual(stats["max_p"], 2.0)

    def test_area_fraction_and_bbox_locate_the_breach(self):
        p = [1.0, 9.0, 1.0]
        areas = [1.0, 0.25, 2.75]
        centroids = [[0, 0, 0], [0.5, -0.1, 0.3], [1, 1, 1]]
        stats = vmp.exceedance_stats(p, areas, centroids, limit=5.0)
        self.assertEqual(stats["count"], 1)
        self.assertAlmostEqual(stats["area_m2"], 0.25)
        self.assertAlmostEqual(stats["area_fraction"], 0.0625)
        self.assertEqual(stats["bbox"][0], [0.5, -0.1, 0.3])
        self.assertEqual(stats["bbox"][1], [0.5, -0.1, 0.3])


class CaseConstantTests(unittest.TestCase):
    """The constants the verdicts quote must stay tied to the case files."""

    def test_kinematic_dynamic_heads_match_the_velocities(self):
        self.assertAlmostEqual(vmp.Q_KINEMATIC, 0.5 * vmp.U_INF ** 2)
        self.assertAlmostEqual(vmp.B52_Q, 0.5 * vmp.B52_U_INF ** 2)

    def test_b52_rescale_is_exactly_three_percent(self):
        self.assertAlmostEqual(vmp.B52_LENGTH_NEW / vmp.B52_LENGTH_OLD, 0.97)

    def test_brake_gap_box_is_searched_before_the_front_wheel(self):
        names = [name for name, _, _ in vmp.MOTORBIKE_REGIONS]
        self.assertEqual(names[0], "front_brake_disc_gap")
        self.assertLess(names.index("front_brake_disc_gap"),
                        names.index("front_wheel"))


if __name__ == "__main__":
    unittest.main()
