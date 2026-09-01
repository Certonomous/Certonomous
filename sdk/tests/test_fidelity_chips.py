"""G5: trend language is retired; fidelity chips carry the grade.

Honesty is carried by value ± CI, the chip, and the uncertainty channels —
never by hedging prose. These tests pin the chip contract and scan the
narration/report sources so the retired vocabulary cannot creep back.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from chief_engineer import lab

SDK = Path(__file__).resolve().parents[1]

# Retired vocabulary, banned from headlines, badges, plot annotations, and
# report sentences. Scanned as phrases so physical usages ("drag trend" in an
# agenda scope) don't false-positive.
_BANNED = ("TREND ONLY", "trend only", "indicative",
           "as a trend", "is a trend", "a plain trend")
# Files whose string literals feed camera surfaces.
_SOURCES = [SDK / "workflows" / name for name in (
    "aircraft_optimization.py", "valve_study.py", "shape_optimization.py",
    "geometry_study.py", "time_constrained.py", "uncertainty_reduction.py",
    "unseen_geometry.py")] + [SDK / "chief_engineer" / "researcher.py"]

_ALLOWED_LINE = re.compile(r"LEGACY|legacy|# ")


class ChipContract(unittest.TestCase):
    def test_chip_names(self):
        self.assertEqual(lab.VALIDATED, "VALIDATED")
        self.assertEqual(lab.SOLVER_BACKED, "SOLVER-BACKED")
        self.assertEqual(lab.CONCEPTUAL, "RESEARCH MODEL")
        self.assertEqual(lab.UNCONVERGED, "UNCONVERGED")

    def test_trust_never_emits_retired_labels(self):
        cases = [
            dict(converged=False),
            dict(solver_backed=False),
            dict(in_validated_regime=False),
            dict(calibrated=False),
            dict(relative_error=0.01),
            dict(relative_error=0.5),
            dict(),
        ]
        for kwargs in cases:
            tier = lab.trust(**kwargs)["tier"]
            self.assertIn(tier, {lab.VALIDATED, lab.SOLVER_BACKED,
                                 lab.CONCEPTUAL, lab.UNCONVERGED}, kwargs)

    def test_plain_trust_never_grants_validated(self):
        """VALIDATED is earned only against a published experiment."""
        self.assertNotEqual(lab.trust(relative_error=0.001)["tier"],
                            lab.VALIDATED)

    def test_validation_path_still_grants_validated(self):
        verdict = lab.validate_against_reference(
            measured_cd=1.05,
            reference={"cd": 1.05, "tolerance": 0.15, "area_basis": "planform",
                       "source": "test reference"})
        self.assertEqual(verdict["tier"], lab.VALIDATED)

    def test_legacy_renames_map_to_chips(self):
        """A retired SPELLING resolves onto the current spelling of that grade."""
        self.assertEqual(lab.resolve_tier("NEEDS WORK"), lab.UNCONVERGED)
        self.assertEqual(lab.resolve_tier("CONCEPTUAL MODEL"), lab.CONCEPTUAL)

    def test_weaker_grades_are_never_upgraded_to_solver_backed(self):
        """The regression guard. This assertion used to run the other way.

        `lab.LEGACY_CHIPS["TREND ONLY"] == lab.SOLVER_BACKED` was a passing
        test, and it was the defect written down as a requirement: four display
        surfaces each mapped TREND ONLY and REFERENCE REGIME MISMATCH onto
        SOLVER-BACKED, which is also the tier that renders no badge.
        """
        self.assertEqual(lab.resolve_tier("TREND ONLY"), "TREND ONLY")
        self.assertEqual(lab.resolve_tier("REFERENCE REGIME MISMATCH"),
                         "REFERENCE REGIME MISMATCH")
        self.assertNotIn("TREND ONLY", lab.LEGACY_CHIPS)
        self.assertNotIn("REFERENCE REGIME MISMATCH", lab.LEGACY_CHIPS)

    def test_no_legacy_mapping_may_raise_a_tier(self):
        """The rule is checked against the rank table, not against a name list.

        A future entry cannot reintroduce the upgrade quietly: this is the same
        assertion `lab` runs at import, so the module refuses to load rather
        than serving an inflated wall.
        """
        lab._assert_no_tier_upgrade()
        for source, target in lab.LEGACY_CHIPS.items():
            self.assertLessEqual(lab.TIER_RANK[source], lab.TIER_RANK[target],
                                 f"{source} -> {target}")

    def test_an_unranked_label_does_not_pass_through_as_a_tier(self):
        for junk in ("EXCELLENT", "probably fine", "", None):
            self.assertEqual(lab.resolve_tier(junk), lab.UNESTABLISHED, junk)

    def test_a_tier_without_a_certificate_is_not_a_credential(self):
        self.assertEqual(lab.credential_tier(lab.VALIDATED, "C-2026-0001"),
                         lab.VALIDATED)
        for missing in (None, "", "   "):
            self.assertEqual(lab.credential_tier(lab.VALIDATED, missing),
                             lab.UNESTABLISHED, repr(missing))


class RetiredVocabulary(unittest.TestCase):
    def test_workflow_sources_carry_no_retired_language(self):
        for path in _SOURCES:
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), 1):
                if _ALLOWED_LINE.search(line):
                    continue
                for phrase in _BANNED:
                    self.assertNotIn(
                        phrase, line,
                        f"{path.name}:{lineno} still says {phrase!r}")


if __name__ == "__main__":
    unittest.main()
