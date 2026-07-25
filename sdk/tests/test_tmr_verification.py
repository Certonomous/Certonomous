"""TMR flat-plate verification plumbing — every test solver-free.

Covers the geometric-grading mathematics, the ladder/observed-order and
Richardson machinery, wall-shear and coefficient parsing, the reference
tables copied from the TMR convergence data files, and the product-language
rules on everything user-visible.
"""
from __future__ import annotations

import math
import unittest

from workflows.tmr_verification import (
    BANNED_CARD_WORDS, CFL3D_SST_V, FUN3D_SST_V, LEVELS, build_summary,
    card_entry_text, cf_at, final_coefficient, format_summary_lines,
    geometric_first_cell, grid_convergence_index, observed_order,
    parse_wall_shear_raw, parse_yplus_dat, ratio_for_first_cell,
    richardson_extrapolate,
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
            "cells": level.cells, "nx": level.nx_up + level.nx_plate,
            "ny": level.ny, "cd": cd, "cd_tail_spread": 1e-9, "cf_097": cf,
            "iterations": 4000, "wall_seconds": 60.0,
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


if __name__ == "__main__":
    unittest.main()
