"""TMR flat-plate verification plumbing — every test solver-free.

Covers the geometric-grading mathematics, the ladder/observed-order and
Richardson machinery, wall-shear and coefficient parsing, the reference
tables copied from the TMR convergence data files, and the product-language
rules on everything user-visible.
"""
from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from workflows.tmr_verification import (halves_drift, measure_period,
                                        time_weighted_stats)

from workflows.tmr_verification import (
    BANNED_CARD_WORDS, BUMP_LEVELS, CFL3D_BUMP_SST, CFL3D_NACA_SST,
    CFL3D_SST_V, FUN3D_BUMP_SST, FUN3D_NACA_SST, FUN3D_SST_V, LEVELS,
    NACA_LEVELS, _axis_vector, build_bump_summary, build_proposals,
    build_summary, bump_edge_points, bump_profile, card_entry_text,
    card_update, cf_at, classify_naca_patches, final_coefficient,
    format_bump_summary_lines, format_summary_lines, geometric_first_cell,
    grid_convergence_index, naca_fields_tmr, naca_thickness, observed_order,
    parse_boundary_patches, parse_force_split, parse_wall_shear_raw,
    parse_yplus_dat, ratio_for_first_cell, richardson_extrapolate,
)

from workflows.tmr_verification import (
    BACKSTOP_MIN_ITERATIONS, SETTLE_MIN_ITERATIONS, SETTLE_TOL,
    SETTLE_WINDOW_MAX, SETTLE_WINDOW_MIN, control_dict, iteration_backstop,
    live_coefficient_series, request_solver_stop, rung_shades,
    settle_verdict, settle_window,
)


class GeometricGrading(unittest.TestCase):
    def test_uniform_distribution_is_length_over_count(self):
        self.assertAlmostEqual(geometric_first_cell(2.0, 10, 1.0), 0.2)

    def test_cells_sum_to_the_block_length(self):
        length, n, ratio = 1.0, 24, 4.95e4
        first = geometric_first_cell(length, n, ratio)
        r = ratio ** (1.0 / (n - 1))
        total = sum(first * r ** i for i in range(n))
        self.assertAlmostEqual(total, length, places=9)

    def test_last_over_first_equals_the_requested_ratio(self):
        first = geometric_first_cell(1.0, 48, 100.0)
        r = 100.0 ** (1.0 / 47)
        self.assertAlmostEqual(first * r ** 47 / first, 100.0, places=6)

    def test_ratio_solver_inverts_first_cell(self):
        ratio = ratio_for_first_cell(1.0, 24, 8.0e-6)
        recovered = geometric_first_cell(1.0, 24, ratio)
        self.assertAlmostEqual(recovered, 8.0e-6, delta=1e-9)

    def test_ratio_solver_returns_uniform_when_no_stretching_needed(self):
        self.assertEqual(ratio_for_first_cell(1.0, 10, 0.2), 1.0)


class LadderMathematics(unittest.TestCase):
    def _power_law(self, exact, c, p):
        # f(h) = exact + c h^p sampled at h = 4, 2, 1 (refinement factor 2).
        return [exact + c * h ** p for h in (4.0, 2.0, 1.0)]

    def test_observed_order_recovers_a_pure_power_law(self):
        fc, fm, ff = self._power_law(0.00285, 1e-4, 1.7)
        self.assertAlmostEqual(observed_order(fc, fm, ff), 1.7, places=9)

    def test_observed_order_none_when_not_monotone(self):
        self.assertIsNone(observed_order(1.0, 0.9, 0.95))
        self.assertIsNone(observed_order(1.0, 1.0, 0.9))

    def test_richardson_recovers_the_exact_value(self):
        exact = 0.00285
        fc, fm, ff = self._power_law(exact, -2e-4, 2.0)
        p = observed_order(fc, fm, ff)
        self.assertAlmostEqual(richardson_extrapolate(fm, ff, p), exact,
                               places=12)

    def test_gci_is_positive_and_scales_with_the_gap(self):
        small = grid_convergence_index(1.001, 1.0, 2.0)
        large = grid_convergence_index(1.01, 1.0, 2.0)
        self.assertGreater(small, 0.0)
        self.assertAlmostEqual(large / small, 10.0, places=6)

    def test_gci_refuses_a_zero_fine_value(self):
        with self.assertRaises(ValueError):
            grid_convergence_index(0.1, 0.0, 2.0)


class WallShearParsing(unittest.TestCase):
    RAW = (
        "# sampled surface\n"
        "# x y z wallShearStress_x ...\n"
        "1.5 0 0.5 -1.30e-03 1e-9 0\n"
        "0.5 0 0.5 -1.50e-03 0 0\n"
        "not a data line\n"
        "1.0 0 0.5 -1.40e-03 0 0\n"
    )

    def test_profile_is_sorted_and_sign_corrected(self):
        profile = parse_wall_shear_raw(self.RAW)
        self.assertEqual([x for x, _ in profile], [0.5, 1.0, 1.5])
        # Cf = -tau_x / (0.5 U^2) with U = 1: -(-1.5e-3)/0.5 = 3.0e-3.
        self.assertAlmostEqual(profile[0][1], 3.0e-3, places=12)
        self.assertAlmostEqual(profile[2][1], 2.6e-3, places=12)

    def test_station_interpolation_is_linear(self):
        profile = parse_wall_shear_raw(self.RAW)
        self.assertAlmostEqual(cf_at(profile, 0.75), 2.9e-3, places=12)
        self.assertAlmostEqual(cf_at(profile, 1.0), 2.8e-3, places=12)

    def test_station_outside_the_profile_is_none(self):
        profile = parse_wall_shear_raw(self.RAW)
        self.assertIsNone(cf_at(profile, 1.9))
        self.assertIsNone(cf_at(profile, 0.1))
        self.assertIsNone(cf_at([(1.0, 2e-3)], 1.0))


class CoefficientParsing(unittest.TestCase):
    DAT = (
        "# Force coefficients\n"
        "# Time Cd Cs Cl CmRoll CmPitch CmYaw Cd(f) Cd(r)\n"
        + "\n".join(f"{i} {0.0030 - 0.0001 / i:.12f} 0 0 0 0 0 0 0"
                    for i in range(1, 401)) + "\n"
    )

    def test_final_value_is_the_last_iterate(self):
        result = final_coefficient(self.DAT, "Cd", tail=100)
        self.assertAlmostEqual(result["value"], 0.0030 - 0.0001 / 400,
                               places=10)
        self.assertEqual(result["iterations"], 400)

    def test_tail_spread_measures_only_the_window(self):
        result = final_coefficient(self.DAT, "Cd", tail=100)
        expected = (0.0001 / 301) - (0.0001 / 400)
        self.assertAlmostEqual(result["spread"], expected, places=12)

    def test_missing_column_is_none(self):
        self.assertIsNone(final_coefficient(self.DAT, "Cx"))

    def test_yplus_last_row_wins(self):
        text = ("# Time patch min max average\n"
                "100 plate 0.5 2.0 1.0\n"
                "200 plate 0.1 0.8 0.4\n")
        parsed = parse_yplus_dat(text, "plate")
        self.assertEqual(parsed, {"min": 0.1, "max": 0.8, "average": 0.4})
        self.assertIsNone(parse_yplus_dat(text, "hull"))


class GridFamily(unittest.TestCase):
    def test_ladder_matches_the_tmr_cell_counts(self):
        self.assertEqual([lv.cells for lv in LEVELS], [816, 3264, 13056])
        for lv in LEVELS:
            self.assertIn(lv.cells, CFL3D_SST_V)
            self.assertIn(lv.cells, FUN3D_SST_V)

    def test_each_level_doubles_both_directions(self):
        for lo, hi in zip(LEVELS, LEVELS[1:]):
            self.assertEqual(hi.nx_up, 2 * lo.nx_up)
            self.assertEqual(hi.nx_plate, 2 * lo.nx_plate)
            self.assertEqual(hi.ny, 2 * lo.ny)

    def test_reference_finest_values_match_the_tmr_data_files(self):
        self.assertAlmostEqual(CFL3D_SST_V[208896]["cd"], 0.285332397e-2,
                               places=12)
        self.assertAlmostEqual(FUN3D_SST_V[208896]["cf097"],
                               0.269054633489452e-2, places=15)


def _fake_grids():
    """Three synthetic-but-plausible grid records shaped like run_level's."""
    grids = []
    for level, cd, cf in zip(LEVELS, (0.002710, 0.002790, 0.002828),
                             (0.002550, 0.002628, 0.002665)):
        grids.append({
            "level": level.name, "tmr_nodes": level.tmr_nodes,
            "cells": level.cells, "nx": level.nx_total,
            "ny": level.ny, "cd": cd, "cd_tail_spread": 1e-9,
            "cf_station": cf, "iterations": 4000, "wall_seconds": 60.0,
            "yplus": {"min": 0.1, "max": 0.9, "average": 0.4},
            "timings": {"simpleFoam": 55.0},
        })
    return grids


class SummaryAndCard(unittest.TestCase):
    def test_summary_carries_order_extrapolate_and_comparison(self):
        summary = build_summary(_fake_grids())
        cd = summary["convergence"]["cd"]
        self.assertIsNotNone(cd["observed_order"])
        self.assertGreater(cd["richardson"], summary["grids"][-1]["cd"])
        comp = summary["comparison"]
        self.assertEqual(len(comp["cfl3d_cd_ladder"]), 3)
        self.assertAlmostEqual(comp["cfl3d_cd_finest"], 0.285332397e-2,
                               places=12)
        self.assertIn("cd_extrapolate_vs_cfl3d_finest_pct", comp)

    def test_summary_lines_obey_product_language_rules(self):
        lines = format_summary_lines(build_summary(_fake_grids()))
        joined = "\n".join(lines)
        self.assertNotIn("—", joined)          # no em dashes
        self.assertNotIn("--", joined)
        for line in lines:
            first = next((ch for ch in line if ch.isalpha()), "X")
            self.assertTrue(first.isupper() or first.isdigit(),
                            msg=f"bullet not capitalized: {line!r}")
        self.assertIn("turbmodels.larc.nasa.gov", joined)

    def test_summary_lines_carry_no_banned_words(self):
        joined = "\n".join(format_summary_lines(build_summary(_fake_grids()))
                           ).lower()
        for word in BANNED_CARD_WORDS:
            self.assertNotIn(word, joined, msg=word)

    def test_card_text_measured_state(self):
        text = card_entry_text(build_summary(_fake_grids()))
        self.assertIsNotNone(text)
        self.assertIn("0.002828", text)      # fine-grid Cd, as measured
        self.assertIn("0.002826", text)      # CFL3D on the same grid size
        self.assertIn("bump-in-channel next", text)
        self.assertNotIn("--", text)
        for word in BANNED_CARD_WORDS:
            self.assertNotIn(word, text.lower(), msg=word)

    def test_card_text_refused_without_a_monotone_ladder(self):
        grids = _fake_grids()
        grids[1]["cd"] = 0.002830            # non-monotone: order undefined
        self.assertIsNone(card_entry_text(build_summary(grids)))

    def test_card_text_refused_with_a_short_ladder(self):
        summary = build_summary(_fake_grids())
        summary["grids"] = summary["grids"][:2]
        self.assertIsNone(card_entry_text(summary))


def _fake_bump_grids():
    """Bump-shaped records: Cd decreasing with refinement, like the case."""
    grids = []
    for level, cd, cdp, cf in zip(
            BUMP_LEVELS, (0.004480, 0.003720, 0.003625),
            (0.001400, 0.000560, 0.000440), (0.005230, 0.005640, 0.005780)):
        grids.append({
            "level": level.name, "tmr_nodes": level.tmr_nodes,
            "cells": level.cells, "nx": level.nx_total, "ny": level.ny,
            "cd": cd, "cd_tail_spread": 1e-9, "cd_pressure": cdp,
            "cd_viscous": cd - cdp, "cf_station": cf, "iterations": 3000,
            "wall_seconds": 300.0,
            "yplus": {"min": 0.1, "max": 0.8, "average": 0.3},
            "timings": {"simpleFoam": 290.0},
        })
    return grids


class BumpGeometry(unittest.TestCase):
    def test_profile_is_zero_off_the_bump(self):
        for x in (0.0, 0.1, 0.29999, 1.20001, 1.5):
            self.assertEqual(bump_profile(x), 0.0)

    def test_profile_peaks_at_five_percent_at_the_tmr_peak(self):
        self.assertAlmostEqual(bump_profile(0.75), 0.05, places=12)

    def test_profile_is_symmetric_about_the_peak(self):
        for d in (0.05, 0.15, 0.30, 0.44):
            self.assertAlmostEqual(bump_profile(0.75 - d),
                                   bump_profile(0.75 + d), places=12)

    def test_profile_is_continuous_at_the_junctions(self):
        self.assertLess(bump_profile(0.300001), 1e-12)
        self.assertLess(bump_profile(1.199999), 1e-12)

    def test_edge_points_are_interior_dense_and_bounded(self):
        points = bump_edge_points()
        self.assertGreater(len(points), 400)
        self.assertGreater(points[0][0], 0.0)
        self.assertLess(points[-1][0], 1.5)
        self.assertAlmostEqual(max(y for _, y in points), 0.05, places=4)
        self.assertGreaterEqual(min(y for _, y in points), 0.0)


class BumpGridFamily(unittest.TestCase):
    def test_ladder_matches_the_tmr_cell_counts(self):
        self.assertEqual([lv.cells for lv in BUMP_LEVELS],
                         [3520, 14080, 56320])
        for lv in BUMP_LEVELS:
            self.assertIn(lv.cells, CFL3D_BUMP_SST)
            self.assertIn(lv.cells, FUN3D_BUMP_SST)

    def test_each_level_doubles_every_direction(self):
        for lo, hi in zip(BUMP_LEVELS, BUMP_LEVELS[1:]):
            self.assertEqual(hi.nx_up, 2 * lo.nx_up)
            self.assertEqual(hi.nx_wall, 2 * lo.nx_wall)
            self.assertEqual(hi.nx_down, 2 * lo.nx_down)
            self.assertEqual(hi.ny, 2 * lo.ny)

    def test_reference_finest_values_match_the_tmr_data_files(self):
        self.assertAlmostEqual(CFL3D_BUMP_SST[901120]["cd"],
                               0.36045158543e-2, places=13)
        self.assertAlmostEqual(CFL3D_BUMP_SST[901120]["cf075"],
                               0.58482303300e-2, places=13)
        self.assertAlmostEqual(FUN3D_BUMP_SST[901120]["cd"],
                               0.3592588e-2, places=10)


class ForceSplitParsing(unittest.TestCase):
    LOG = (
        "forceCoeffs forceCoeffs1 write:\n"
        "    Cd:\t0.004000\t0.001000\t0.003000\t0\n"
        "    Cl:\t0.024000\t0.023990\t0.000010\t0\n"
        "later iteration...\n"
        "forceCoeffs forceCoeffs1 write:\n"
        "    Cd:\t0.003625\t0.000440\t0.003185\t0\n"
        "    Cl:\t0.024800\t0.024790\t0.000010\t0\n"
    )

    def test_last_block_wins_and_splits(self):
        split = parse_force_split(self.LOG, "Cd")
        self.assertAlmostEqual(split["total"], 0.003625)
        self.assertAlmostEqual(split["pressure"], 0.000440)
        self.assertAlmostEqual(split["viscous"], 0.003185)

    def test_other_names_and_missing(self):
        self.assertAlmostEqual(parse_force_split(self.LOG, "Cl")["total"],
                               0.0248)
        self.assertIsNone(parse_force_split(self.LOG, "Cs"))
        self.assertIsNone(parse_force_split("no coefficients here", "Cd"))


class BumpSummaryAndCard(unittest.TestCase):
    def test_bump_summary_convergence_and_split_comparison(self):
        summary = build_bump_summary(_fake_bump_grids())
        self.assertIsNotNone(summary["convergence"]["cd"]["observed_order"])
        comp = summary["comparison"]
        self.assertAlmostEqual(comp["cfl3d_cd_finest"], 0.36045158543e-2,
                               places=13)
        self.assertIn("cd_pressure_fine_vs_cfl3d_same_grid_pct", comp)
        self.assertIn("cd_extrapolate_vs_cfl3d_finest_pct", comp)

    def test_bump_summary_lines_obey_product_rules(self):
        lines = format_bump_summary_lines(build_bump_summary(_fake_bump_grids()))
        joined = "\n".join(lines)
        self.assertNotIn("—", joined)
        self.assertNotIn("--", joined)
        for word in BANNED_CARD_WORDS:
            self.assertNotIn(word, joined.lower(), msg=word)
        for line in lines:
            first = next((ch for ch in line if ch.isalpha()), "X")
            self.assertTrue(first.isupper() or first.isdigit(),
                            msg=f"bullet not capitalized: {line!r}")
        self.assertIn("turbmodels.larc.nasa.gov", joined)

    def test_combined_card_carries_both_results_without_methods(self):
        card = card_update(build_summary(_fake_grids()),
                           build_bump_summary(_fake_bump_grids()))
        self.assertEqual(card["status"], "flat plate and bump measured")
        self.assertIn("0.002828", card["entry"])     # flat fine Cd measured
        self.assertIn("0.003625", card["entry"])     # bump fine Cd measured
        self.assertIn("NACA 0012 airfoil next", card["entry"])
        lowered = card["entry"].lower()
        for banned in (*BANNED_CARD_WORDS, "foam", "sst", "mesh", "solver",
                       "k-omega", "upwind"):
            self.assertNotIn(banned, lowered, msg=banned)
        self.assertNotIn("--", card["entry"])

    def test_card_falls_back_to_flat_only_when_bump_missing(self):
        card = card_update(build_summary(_fake_grids()), None)
        self.assertEqual(card["status"], "flat plate measured")
        self.assertIn("bump-in-channel next", card["entry"])

    def test_card_none_when_even_flat_is_not_defensible(self):
        grids = _fake_grids()
        grids[1]["cd"] = 0.002830
        self.assertIsNone(card_update(build_summary(grids), None))


class Proposals(unittest.TestCase):
    SCHEMA = {"id", "objective", "rationale", "citations", "est_core_min",
              "expected_knowledge_gain", "source_kind", "status",
              "created_at", "launch_prompt"}

    def _proposals(self):
        return build_proposals(build_summary(_fake_grids()),
                               build_bump_summary(_fake_bump_grids()))

    def test_schema_is_exact_and_ids_distinct(self):
        proposals = self._proposals()
        self.assertEqual(len(proposals), 2)
        ids = {p["id"] for p in proposals}
        self.assertEqual(len(ids), 2)
        for p in proposals:
            self.assertEqual(set(p), self.SCHEMA)
            self.assertEqual(p["status"], "proposed")
            self.assertEqual(p["source_kind"], "challenge")
            self.assertIsInstance(p["est_core_min"], int)
            self.assertGreater(p["est_core_min"], 0)
            self.assertTrue(p["citations"])
            self.assertTrue(p["created_at"].startswith("20"))
            self.assertTrue(p["launch_prompt"].strip())

    def test_estimates_are_anchored_to_measured_wall_clocks(self):
        proposals = self._proposals()
        by_id = {p["id"]: p for p in proposals}
        # Bump ladder: 3 x 300 s = 15 core-min; NACA: 3 alphas x 1.5 margin.
        self.assertEqual(by_id["tmr-naca0012-verification"]["est_core_min"],
                         int(round(3 * 15.0 * 1.5)) + 1)
        # Finest grids: (4*2 + 16*4) x measured flat fine-solve seconds / 60.
        expected = int(round(72 * 55.0 / 60.0)) + 1
        self.assertEqual(by_id["tmr-flatplate-finest-grids"]["est_core_min"],
                         expected)

    def test_proposal_text_obeys_product_rules(self):
        for p in self._proposals():
            blob = " ".join([p["objective"], p["rationale"],
                             p["expected_knowledge_gain"]])
            self.assertNotIn("—", blob)
            self.assertNotIn("--", blob)
            for word in BANNED_CARD_WORDS:
                self.assertNotIn(word, blob.lower(), msg=word)


class NacaCase(unittest.TestCase):
    def test_airfoil_closes_sharp_at_both_ends(self):
        self.assertEqual(naca_thickness(0.0), 0.0)
        self.assertLess(abs(naca_thickness(1.0)), 1e-12)
        self.assertAlmostEqual(
            max(naca_thickness(x / 1000) for x in range(1001)), 0.0595,
            places=3)

    def test_ladder_matches_the_tmr_cell_counts(self):
        self.assertEqual([lv.cells for lv in NACA_LEVELS],
                         [3584, 14336, 57344])

    def test_reference_values_match_the_published_files(self):
        self.assertAlmostEqual(CFL3D_NACA_SST[10.0]["cl"], 1.0778080613,
                               places=10)
        self.assertAlmostEqual(CFL3D_NACA_SST[15.0]["cd"], 2.2186245406e-2,
                               places=12)
        self.assertAlmostEqual(FUN3D_NACA_SST[10.0]["cl"], 1.0840, places=8)

    def test_axis_vector_places_lift_on_the_discovered_axis(self):
        self.assertEqual(_axis_vector(1.0, 0.5, 2),
                         "(1.00000000 0.00000000 0.50000000)")
        self.assertEqual(_axis_vector(1.0, 0.5, 1),
                         "(1.00000000 0.50000000 0.00000000)")

    def test_boundary_parse_and_classification(self):
        boundary = """
    auto0 { type patch; nFaces 4; startFace 0; }
    auto1 { type patch; nFaces 4; startFace 4; }
    auto2 { type patch; nFaces 4; startFace 8; }
    empty0 { type patch; nFaces 0; startFace 12; }
"""
        patches = parse_boundary_patches(boundary)
        self.assertEqual(patches["auto1"], (4, 4))
        # Synthetic mesh: chord x, lift z, span y in [0, -1] (the TMR NACA
        # layout). Patch 0 far away, patch 1 on the body, patch 2 a span
        # plane.
        points = [(0.5, 0.0, 0.001), (0.6, 0.0, 0.001),
                  (0.5, -1.0, 0.001), (0.6, -1.0, 0.001),
                  (400.0, 0.0, -300.0), (410.0, 0.0, -300.0),
                  (400.0, -1.0, -300.0), (410.0, -1.0, -300.0),
                  (0.5, 0.0, 0.3), (0.6, 0.0, 0.3),
                  (0.5, 0.0, -0.3), (0.6, 0.0, -0.3)]
        faces = ([[4, 5, 7, 6]] * 4          # patch auto0: farfield
                 + [[0, 1, 3, 2]] * 4        # patch auto1: on the body
                 + [[0, 1, 9, 8]] * 4)       # patch auto2: span plane y=0
        roles, thickness, lift_axis, span_axis = classify_naca_patches(
            points, faces, patches)
        self.assertEqual(span_axis, 1)
        self.assertEqual(lift_axis, 2)
        self.assertAlmostEqual(thickness, 1.0)
        self.assertEqual(roles, {"auto0": "outer", "auto1": "airfoil",
                                 "auto2": "frontAndBack",
                                 "empty0": "unused"})

    def test_fields_carry_the_discovered_patch_names_and_alpha(self):
        roles = {"auto3": "airfoil", "auto4": "outer",
                 "auto1": "frontAndBack", "defaultFaces": "unused"}
        fields = naca_fields_tmr(10.0, roles, lift_axis=2)
        for text in fields.values():
            for name in roles:
                self.assertIn(name, text)
        # Alpha 10 with lift on z: U = (cos10, 0, sin10).
        self.assertIn("(0.98480775 0.00000000 0.17364818)", fields["U"])
        self.assertIn("noSlip", fields["U"])
        self.assertIn("omegaWallFunction", fields["omega"])


class TimeAccurateStatistics(unittest.TestCase):
    def _sine(self, period=1.7, mean=1.0, amp=0.1, dt=0.01, t_end=10.0):
        ts = [i * dt for i in range(int(t_end / dt) + 1)]
        vs = [mean + amp * math.sin(2 * math.pi * t / period) for t in ts]
        return ts, vs

    def test_time_weighted_mean_and_envelope_of_a_sine(self):
        ts, vs = self._sine()
        stats = time_weighted_stats(ts, vs, 3.0)
        self.assertAlmostEqual(stats["mean"], 1.0, places=2)
        self.assertAlmostEqual(stats["band"], 0.2, places=3)
        self.assertAlmostEqual(stats["window_start"], 3.0, places=9)

    def test_mean_is_time_weighted_not_sample_weighted(self):
        # Uneven sampling biased toward the peak must not bias the mean.
        ts = [0.0, 1.0, 1.01, 1.02, 1.03, 2.0]
        vs = [0.0, 2.0, 2.0, 2.0, 2.0, 0.0]
        stats = time_weighted_stats(ts, vs, 0.0)
        self.assertAlmostEqual(stats["mean"], 1.0, delta=0.06)

    def test_period_recovered_from_mean_crossings(self):
        ts, vs = self._sine(period=1.7)
        self.assertAlmostEqual(measure_period(ts, vs, 3.0), 1.7, places=2)

    def test_period_refused_without_enough_crossings(self):
        ts, vs = self._sine(period=50.0, t_end=10.0)
        self.assertIsNone(measure_period(ts, vs, 3.0))
        self.assertIsNone(time_weighted_stats([1.0], [2.0], 0.0))

    def test_halves_drift_is_tiny_on_a_genuine_limit_cycle(self):
        ts, vs = self._sine()
        drift = halves_drift(ts, vs, 3.0, 10.0)
        self.assertLess(drift["relative_drift"], 0.001)

    def test_halves_drift_flags_a_still_developing_ramp(self):
        # A monotonically rising mean (turbulence still ramping up under a
        # cold, low-freestream-turbulence start) with a small sine riding on
        # top, mirroring the measured 300-convective-unit NACA 0012 alpha=0
        # coarse-rung history (Cd rose 0.00032 -> 0.00089, no leveling off).
        ts = [i * 0.01 for i in range(3001)]
        vs = [0.0003 + 0.0006 * (t / 30.0) + 5e-5 * math.sin(2 * math.pi * t / 0.4)
              for t in ts]
        drift = halves_drift(ts, vs, 12.0, 30.0)
        self.assertGreater(drift["relative_drift"], 0.10)

    def test_halves_drift_none_without_enough_samples_each_half(self):
        self.assertIsNone(halves_drift([1.0, 2.0], [1.0, 2.0], 0.0, 2.0))


class SettleCriterion(unittest.TestCase):
    """A rung stops when the answer stops moving, not when a guess runs out.

    The 2026-07-31 lesson: the 208896-cell flat plate was asked for 15000
    iterations, read Cd 1.05% high there, still falling, and would have
    published the ladder as a divergence at p = -0.745. It took 36000.
    """

    def test_a_flat_history_settles(self):
        series = [0.0028635 + 1e-9 * ((i % 7) - 3) for i in range(4000)]
        out = settle_verdict(series)
        self.assertTrue(out["settled"])
        self.assertLessEqual(out["spread"], SETTLE_TOL)

    def test_a_slow_monotone_drift_does_not_settle(self):
        # The failure the fifty-iteration gate cannot see: 1e-5 per thousand
        # iterations is 5e-7 over fifty, but 2e-5 over the 2000-iteration
        # window, which is what the ladder actually cares about.
        series = [0.0029 - 1e-8 * i for i in range(9000)]
        out = settle_verdict(series)
        self.assertFalse(out["settled"])
        self.assertGreater(out["spread"], SETTLE_TOL)
        self.assertIn("above", out["reason"])

    def test_a_short_history_is_never_called_settled(self):
        # A run that has barely started can look arbitrarily flat.
        out = settle_verdict([0.003] * (SETTLE_MIN_ITERATIONS - 1))
        self.assertFalse(out["settled"])
        self.assertIsNone(out["window"])
        self.assertIn("iterations", out["reason"])

    def test_the_window_grows_with_the_run_and_is_clamped(self):
        self.assertEqual(settle_window(0), SETTLE_WINDOW_MIN)
        self.assertEqual(settle_window(4000), 1000)
        self.assertEqual(settle_window(10 ** 6), SETTLE_WINDOW_MAX)
        # Monotone, so a longer run is never judged on a shorter window.
        widths = [settle_window(n) for n in range(0, 20000, 137)]
        self.assertEqual(widths, sorted(widths))

    def test_the_backstop_is_a_backstop_not_the_commitment(self):
        # The 208896-cell rung settled at iteration 30720; the backstop must
        # leave room beyond that, and must exceed the 15000 that decided the
        # ladder wrongly.
        self.assertGreater(iteration_backstop(208896), 30720)
        self.assertGreater(iteration_backstop(208896), 15000)
        # Floored, monotone in cells, and a whole number of thousands.
        self.assertEqual(iteration_backstop(1), BACKSTOP_MIN_ITERATIONS)
        counts = [816, 3264, 13056, 52224, 208896]
        caps = [iteration_backstop(c) for c in counts]
        self.assertEqual(caps, sorted(caps))
        for cap in caps:
            self.assertEqual(cap % 1000, 0)

    def test_the_control_dict_can_be_stopped_while_it_runs(self):
        # Without runTimeModifiable the only thing that can stop a rung is
        # the cap, which is the defect.
        text = control_dict(12345)
        self.assertIn("runTimeModifiable yes;", text)
        self.assertIn("endTime         12345;", text)

    def test_a_stop_request_rewrites_stop_at_and_nothing_else(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Path(tmp) / "system"
            case.mkdir(parents=True)
            (case / "controlDict").write_text(control_dict(9000))
            self.assertTrue(request_solver_stop(Path(tmp)))
            after = (case / "controlDict").read_text()
            self.assertIn("stopAt          writeNow;", after)
            self.assertNotIn("stopAt          endTime;", after)
            self.assertIn("endTime         9000;", after)

    def test_a_missing_case_does_not_raise(self):
        # A failed stop request must degrade to running on to the backstop.
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(request_solver_stop(Path(tmp)))

    def test_a_continued_run_reads_forward_not_lexicographically(self):
        # A rung continued from latestTime writes its second history under a
        # directory named for the iteration it resumed at. Sorted as strings
        # "15000" comes before "0" and the history reads backwards.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "postProcessing" / "forceCoeffs1"
            header = "# Force coefficients\n# Time Cd Cs Cl\n"
            for start, first in (("0", 1.0), ("15000", 2.0)):
                d = root / start
                d.mkdir(parents=True)
                (d / "coefficient.dat").write_text(
                    header + "\n".join(f"{i} {first + i * 0.0} 0 0"
                                       for i in range(1, 4)) + "\n")
            series = live_coefficient_series(Path(tmp))
            self.assertEqual(series, [1.0, 1.0, 1.0, 2.0, 2.0, 2.0])

    def test_no_history_at_all_is_not_settled(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(live_coefficient_series(Path(tmp)), [])
            self.assertFalse(settle_verdict([])["settled"])


class RungShades(unittest.TestCase):
    """Every rung gets a colour, because two of them used to vanish.

    The Cf-profile figures zipped the ladder against a literal three-colour
    list. With five rungs the 273x193 and 545x385 profiles were dropped in
    silence, and those two are exactly the rungs the flat plate's earned
    discretization band rests on.
    """

    def test_three_rungs_are_unchanged(self):
        from chief_engineer import plot_theme as theme
        self.assertEqual(rung_shades(3), [theme.DIM, theme.MUTED, theme.LIVE])

    def test_every_rung_gets_its_own_colour(self):
        for count in range(1, 12):
            shades = rung_shades(count)
            self.assertEqual(len(shades), count, count)
            self.assertEqual(len(set(shades)), count, count)
            for shade in shades:
                self.assertRegex(shade, r"^#[0-9a-f]{6}$")

    def test_the_ladder_still_reads_coarse_to_fine(self):
        from chief_engineer import plot_theme as theme
        shades = rung_shades(5)
        self.assertEqual(shades[0], theme.DIM)
        self.assertEqual(shades[-1], theme.LIVE)

    def test_no_rungs_is_no_colours(self):
        self.assertEqual(rung_shades(0), [])


if __name__ == "__main__":
    unittest.main()
