"""Planted controls for the tier-inflation repair (2026-09-01).

Rule 3: a check that has not been shown able to FAIL is not evidence. Each
plant below is a record written to disk carrying a known tier, read back
through the surface that renders it, and asserted on. Three plants, because a
fix validated only against the bad case is half a fix:

  1. a TREND ONLY record must render TREND ONLY, not SOLVER-BACKED;
  2. a REFERENCE REGIME MISMATCH record must render itself, not SOLVER-BACKED;
  3. a genuine SOLVER-BACKED record must still render SOLVER-BACKED.

Plant 3 is the control on the control: without it, a repair that mapped every
tier to "TREND ONLY" would pass plants 1 and 2 and be catastrophically wrong.

The plants are derived by hand, one per alternative, and deliberately not from
a shared vocabulary list. The rails this repair removed were a fixed
alternation, and a fixed alternation is blind to every spelling it does not
enumerate -- a plant generated from the same list as the code under test
inherits exactly that blindness. Casing and whitespace variants are planted
explicitly for the same reason.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer import lab  # noqa: E402
from chief_engineer import certificate  # noqa: E402

sys.path.insert(0, str(SDK / "scripts"))
import build_wall  # noqa: E402


# The three plants, by hand. Each is (planted tier, what a surface must show).
PLANT_TREND = "TREND ONLY"
PLANT_REGIME = "REFERENCE REGIME MISMATCH"
PLANT_GENUINE = "SOLVER-BACKED"


class ResolverPlants(unittest.TestCase):
    """Limb 1: the shared authority itself."""

    def test_plant_trend_only_renders_as_trend_only(self):
        self.assertEqual(lab.resolve_tier(PLANT_TREND), PLANT_TREND)
        self.assertNotEqual(lab.resolve_tier(PLANT_TREND), lab.SOLVER_BACKED)

    def test_plant_regime_mismatch_renders_as_itself(self):
        self.assertEqual(lab.resolve_tier(PLANT_REGIME), PLANT_REGIME)
        self.assertNotEqual(lab.resolve_tier(PLANT_REGIME), lab.SOLVER_BACKED)

    def test_plant_genuine_solver_backed_still_renders_solver_backed(self):
        """The control on the control. A repair that broke this is not a repair."""
        self.assertEqual(lab.resolve_tier(PLANT_GENUINE), lab.SOLVER_BACKED)
        self.assertEqual(lab.resolve_tier(lab.VALIDATED), lab.VALIDATED)

    def test_inflections_of_the_plants_are_not_a_way_back_in(self):
        """The trap the removed rails fell into, planted deliberately.

        The old rails were `\\bTREND[ -]ONLY\\b` (IGNORECASE) and `\\bTREND\\b`
        (NOT ignorecase). So "TREND" was rewritten and "trend" was not. Casing
        and spacing must not change the answer now.
        """
        for spelling in ("trend only", "Trend Only", "  TREND ONLY  ",
                         "tReNd OnLy"):
            self.assertEqual(lab.resolve_tier(spelling), PLANT_TREND, spelling)
        for spelling in ("reference regime mismatch", "Reference Regime Mismatch",
                         "  REFERENCE REGIME MISMATCH "):
            self.assertEqual(lab.resolve_tier(spelling), PLANT_REGIME, spelling)


class SealedPagePlants(unittest.TestCase):
    """Limb 1 on the certificate: the badge, through the real text pipeline.

    `certificate._fold` runs the language rails over EVERY string drawn on the
    page, so a tier that survives `resolve_tier` can still be rewritten on its
    way to the canvas. These plants go through `_fold`, which is where the
    laundering actually happened.
    """

    def test_plant_trend_only_survives_the_page_text_rails(self):
        self.assertEqual(certificate._fold(PLANT_TREND), PLANT_TREND)
        self.assertNotIn("SOLVER-BACKED", certificate._fold(PLANT_TREND))

    def test_plant_regime_mismatch_survives_the_page_text_rails(self):
        self.assertEqual(certificate._fold(PLANT_REGIME), PLANT_REGIME)
        self.assertNotIn("SOLVER-BACKED", certificate._fold(PLANT_REGIME))

    def test_plant_genuine_solver_backed_survives_the_page_text_rails(self):
        self.assertEqual(certificate._fold(PLANT_GENUINE), PLANT_GENUINE)

    def test_the_word_trend_in_prose_is_no_longer_rewritten(self):
        """A reason line may legitimately say "trend"; it used to be replaced."""
        prose = "the TREND across the three meshes is monotone"
        self.assertIn("TREND", certificate._fold(prose))
        self.assertNotIn("SOLVER-BACKED", certificate._fold(prose))

    def test_the_badge_draws_for_a_planted_weak_tier(self):
        """SOLVER-BACKED draws no badge, so an upgraded tier drew none either.

        The observable consequence of the defect was not a wrong word on the
        page: it was NO word on the page. A weak tier must now be badge-worthy.
        """
        for plant in (PLANT_TREND, PLANT_REGIME):
            shown = certificate._resolved_tier(plant)
            self.assertNotEqual(shown, lab.SOLVER_BACKED, plant)
            self.assertIn(shown, certificate._TIER_COLOR, plant)
        # And the genuine default still suppresses its badge, as designed.
        self.assertEqual(certificate._resolved_tier(PLANT_GENUINE),
                         lab.SOLVER_BACKED)


class WallPlants(unittest.TestCase):
    """Limb 1 on the curated wall: the chip markup build_wall emits."""

    def test_plant_trend_only_gets_a_visible_chip(self):
        chip = build_wall._chip_html(PLANT_TREND)
        self.assertIn("TREND ONLY", chip)
        self.assertNotIn("SOLVER-BACKED", chip)

    def test_plant_regime_mismatch_gets_a_visible_chip(self):
        chip = build_wall._chip_html(PLANT_REGIME)
        self.assertIn("REFERENCE REGIME MISMATCH", chip)
        self.assertNotIn("SOLVER-BACKED", chip)

    def test_plant_genuine_solver_backed_is_still_the_unlabeled_default(self):
        """Control: SOLVER-BACKED renders no chip, and that is correct."""
        self.assertEqual(build_wall._chip_html(PLANT_GENUINE), "")


class CredentialSealPlants(unittest.TestCase):
    """Limb 2: a tier is asserted against an issued certificate.

    Planted as records on disk and read back through `credential_tier`, so the
    check is against a stored file rather than an in-memory constant.
    """

    def _plant(self, tmp: Path, name: str, tier: str,
               certificate_no: str | None) -> dict:
        record = {"name": name, "tier": tier, "cd_measured": 0.1234}
        if certificate_no is not None:
            record["certificate"] = certificate_no
        path = tmp / f"{name}.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_a_sealed_tier_is_displayed_and_an_unsealed_one_is_not(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            sealed = self._plant(tmp, "sealed", lab.VALIDATED, "C-2026-0001")
            unsealed = self._plant(tmp, "unsealed", lab.VALIDATED, None)

            # Read back from disk, not from the dict we wrote.
            self.assertEqual(
                lab.credential_tier(sealed["tier"], sealed.get("certificate")),
                lab.VALIDATED,
                "a sealed VALIDATED record must still display VALIDATED")
            self.assertEqual(
                lab.credential_tier(unsealed["tier"],
                                    unsealed.get("certificate")),
                lab.UNESTABLISHED,
                "a tier with no certificate behind it is not a credential")

    def test_an_unsealed_weak_tier_is_not_quietly_promoted_either(self):
        self.assertEqual(lab.credential_tier(PLANT_TREND, None),
                         lab.UNESTABLISHED)
        self.assertEqual(lab.credential_tier(PLANT_TREND, "C-2026-0002"),
                         PLANT_TREND)

    def test_unestablished_never_outranks_a_real_tier(self):
        self.assertGreater(lab.TIER_RANK[lab.UNESTABLISHED],
                           lab.TIER_RANK[lab.UNCONVERGED])


class ImportTimeGuard(unittest.TestCase):
    """The guard must be shown able to refuse, not merely to pass."""

    def test_the_guard_rejects_a_reintroduced_upgrade(self):
        original = dict(lab.LEGACY_CHIPS)
        try:
            lab.LEGACY_CHIPS["TREND ONLY"] = lab.SOLVER_BACKED
            with self.assertRaises(AssertionError):
                lab._assert_no_tier_upgrade()
        finally:
            lab.LEGACY_CHIPS.clear()
            lab.LEGACY_CHIPS.update(original)
        # And is passing again once restored -- so the failure above was the
        # planted condition, not a broken module.
        lab._assert_no_tier_upgrade()

    def test_the_guard_rejects_an_unranked_target(self):
        original = dict(lab.LEGACY_CHIPS)
        try:
            lab.LEGACY_CHIPS["NEEDS WORK"] = "SPLENDID"
            with self.assertRaises(AssertionError):
                lab._assert_no_tier_upgrade()
        finally:
            lab.LEGACY_CHIPS.clear()
            lab.LEGACY_CHIPS.update(original)
        lab._assert_no_tier_upgrade()


if __name__ == "__main__":
    unittest.main()
