"""Tests for the Tier-0 geometry curriculum.

These never touch OpenFOAM: they check that the generators emit watertight
surfaces of the expected size, that every reference.yaml parses and carries the
fields the trust grader needs, and that the trust tier is VALIDATED for an
in-tolerance coefficient and TREND ONLY for an out-of-tolerance one.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

CURRICULUM = SDK.parent / "models" / "curriculum"


def _load(module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, CURRICULUM / f"{module_name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generate = _load("generate")
registry = _load("registry")

from chief_engineer.lab import (NEEDS_WORK, TREND_ONLY, VALIDATED,  # noqa: E402
                                validate_against_reference)


class GeneratorTests(unittest.TestCase):
    def test_every_body_is_watertight(self):
        for name, build in generate.BODIES.items():
            vertices, faces = build()
            with self.subTest(body=name):
                self.assertTrue(generate.is_watertight(faces),
                                f"{name} is not a closed manifold")
                self.assertGreaterEqual(len(faces), 12)

    def test_sphere_is_smooth(self):
        _, faces = generate.sphere()
        # "smooth, ~5k triangles": enough facets to read as a sphere, not a die.
        self.assertGreater(len(faces), 3000)
        self.assertLess(len(faces), 8000)

    def test_watertight_check_rejects_an_open_mesh(self):
        # Drop one triangle from the cube: the surface is no longer closed.
        _, faces = generate.cube()
        opened = faces[:-1]
        self.assertFalse(generate.is_watertight(opened))

    def test_ahmed_slant_changes_the_geometry(self):
        v25, _ = generate.ahmed_body(slant_deg=25.0)
        v35, _ = generate.ahmed_body(slant_deg=35.0)
        length = 1.044
        # A steeper slant cuts more off the rear top, so the base face at the
        # tail is lower for 35 degrees than for 25.
        rear25 = v25[v25[:, 0] >= length - 0.01]
        rear35 = v35[v35[:, 0] >= length - 0.01]
        self.assertGreater(rear25[:, 2].max(), rear35[:, 2].max())

    def test_stl_files_are_present(self):
        for name in registry.TIER0:
            with self.subTest(body=name):
                self.assertTrue(registry.stl_path(name).exists(),
                                f"missing STL for {name} — run generate.py")


class ReferenceTests(unittest.TestCase):
    def test_every_body_has_a_parsable_reference(self):
        for name in registry.TIER0:
            with self.subTest(body=name):
                reference = registry.reference_for(name)
                self.assertIsNotNone(reference, f"{name} has no reference")
                for field in registry.REQUIRED_FIELDS:
                    self.assertIn(field, reference,
                                  f"{name} reference missing {field!r}")

    def test_area_basis_is_frontal_or_planform(self):
        for name in registry.TIER0:
            reference = registry.reference_for(name)
            with self.subTest(body=name):
                self.assertIn(reference["area_basis"], ("frontal", "planform"))

    def test_reference_values_are_numeric_and_positive(self):
        for name in registry.TIER0:
            reference = registry.reference_for(name)
            with self.subTest(body=name):
                self.assertGreater(float(reference["cd"]), 0.0)
                self.assertGreater(float(reference["tolerance"]), 0.0)

    def test_known_bodies_carry_expected_area_basis(self):
        # Bluff bodies are referenced to frontal area, lifting surfaces to planform.
        self.assertEqual(registry.reference_for("cube")["area_basis"], "frontal")
        self.assertEqual(registry.reference_for("ahmed_25")["area_basis"], "frontal")
        self.assertEqual(registry.reference_for("naca0012_wing")["area_basis"], "planform")


class TrustTierTests(unittest.TestCase):
    CUBE = {"cd": 1.05, "tolerance": 0.15, "area_basis": "frontal",
            "source": "Hoerner (1965)"}

    def test_in_tolerance_is_validated(self):
        verdict = validate_against_reference(
            measured_cd=1.02, reference=self.CUBE,
            planform_area=1.0, frontal_area=1.0)
        self.assertEqual(verdict["tier"], VALIDATED)
        self.assertIn("Hoerner", verdict["reason"])

    def test_out_of_tolerance_but_converged_is_trend_only(self):
        verdict = validate_against_reference(
            measured_cd=1.6, reference=self.CUBE,
            planform_area=1.0, frontal_area=1.0)
        self.assertEqual(verdict["tier"], TREND_ONLY)

    def test_unconverged_never_validates(self):
        verdict = validate_against_reference(
            measured_cd=1.05, reference=self.CUBE,
            planform_area=1.0, frontal_area=1.0, converged=False)
        self.assertEqual(verdict["tier"], NEEDS_WORK)

    def test_bad_mesh_caps_at_trend_even_when_the_number_agrees(self):
        verdict = validate_against_reference(
            measured_cd=1.05, reference=self.CUBE,
            planform_area=1.0, frontal_area=1.0, in_validated_regime=False)
        self.assertEqual(verdict["tier"], TREND_ONLY)

    def test_frontal_rebasing_matches_experiment(self):
        # Ahmed: solver reports on planform area; rebased onto frontal it must
        # land on the published 0.285.
        ahmed = {"cd": 0.285, "tolerance": 0.15, "area_basis": "frontal",
                 "source": "Ahmed et al. 1984"}
        verdict = validate_against_reference(
            measured_cd=0.08, reference=ahmed,
            planform_area=0.4017, frontal_area=0.112)
        self.assertEqual(verdict["tier"], VALIDATED)
        self.assertAlmostEqual(verdict["comparison"]["compared_cd"], 0.287, places=2)


class RegimeTests(unittest.TestCase):
    """A value that lands on a different physical regime is a named mismatch,
    not a silent trend."""

    SPHERE = {
        "cd": 0.47, "tolerance": 0.20, "area_basis": "frontal",
        "source": "Achenbach 1972",
        "regime": {
            "label": "subcritical", "reynolds_valid": [1.0e4, 3.0e5],
            "alternates": [{
                "label": "supercritical", "cd": 0.09, "cd_range": [0.06, 0.14],
                "reynolds_valid": [3.5e5, 2.0e7],
                "source": "Achenbach 1972 (supercritical branch)",
                "cause": "fully-turbulent RANS reproduces post-drag-crisis separation"}]}}

    def test_supercritical_value_is_a_named_regime_mismatch(self):
        from chief_engineer.lab import REGIME_MISMATCH
        verdict = validate_against_reference(
            measured_cd=0.095, reference=self.SPHERE, solved_reynolds=1.0e5)
        self.assertEqual(verdict["tier"], REGIME_MISMATCH)
        self.assertIn("supercritical", verdict["reason"])
        self.assertEqual(verdict["comparison"]["matched_regime"], "supercritical")

    def test_subcritical_value_still_validates_in_regime(self):
        verdict = validate_against_reference(
            measured_cd=0.50, reference=self.SPHERE, solved_reynolds=1.0e5)
        self.assertEqual(verdict["tier"], VALIDATED)

    def test_no_alternate_falls_back_to_trend_not_mismatch(self):
        # A reference without alternates never produces a regime mismatch.
        plain = {"cd": 1.05, "tolerance": 0.15, "area_basis": "frontal",
                 "source": "Hoerner (1965)"}
        verdict = validate_against_reference(
            measured_cd=1.6, reference=plain, solved_reynolds=1.0e5)
        self.assertEqual(verdict["tier"], TREND_ONLY)

    def test_reynolds_mismatch_note_only_when_out_of_band(self):
        # Sphere solved supercritical (Re above the reference band) — the reason
        # cites the Reynolds mismatch explicitly.
        verdict = validate_against_reference(
            measured_cd=0.095, reference=self.SPHERE, solved_reynolds=6.0e6)
        self.assertIn("reference valid for", verdict["reason"])


if __name__ == "__main__":
    unittest.main()
