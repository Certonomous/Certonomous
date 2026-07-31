"""The validation wall shows ONE consistently rebased number (v2-G1).

Every percentage a wall card displays must be reproducible from the numbers
stored in the same record: the rebased coefficient, the reference, and the
reason text all have to agree. These tests run against the actual curriculum
result records, so a regression in the writer or the rebase shows up here.
"""
from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

RESULTS = (Path(__file__).resolve().parents[2]
           / "models" / "curriculum" / "results")

_PCT = re.compile(r"(?:within|is)\s+(\d+)%")


def _records():
    for path in sorted(RESULTS.glob("*.json")):
        yield path.name, json.loads(path.read_text(encoding="utf-8"))


class WallArithmetic(unittest.TestCase):
    def test_results_exist(self):
        self.assertTrue(RESULTS.exists(), "curriculum results directory missing")
        self.assertGreater(len(list(RESULTS.glob("*.json"))), 0)

    def test_records_carry_the_rebased_coefficient(self):
        for name, data in _records():
            with self.subTest(body=name):
                if data.get("reference_cd") is None:
                    continue
                self.assertIsNotNone(
                    data.get("cd_compared"),
                    f"{name}: record lacks cd_compared — writer regression; "
                    f"re-run the curriculum suite")

    def test_reason_percentage_matches_the_stored_numbers(self):
        """The percentage the wall prints is recomputed, not trusted."""
        for name, data in _records():
            with self.subTest(body=name):
                compared = data.get("cd_compared")
                reference = data.get("reference_cd")
                reason = data.get("reason") or ""
                match = _PCT.search(reason)
                if compared is None or not reference or not match:
                    continue
                shown = int(match.group(1))
                actual = abs(float(compared) - float(reference)) / abs(float(reference)) * 100
                self.assertLessEqual(
                    abs(actual - shown), 0.51,
                    f"{name}: reason says {shown}% but stored numbers give "
                    f"{actual:.2f}% — the wall is quoting a different figure "
                    f"than it displays")

    def test_stored_relative_error_is_consistent(self):
        for name, data in _records():
            with self.subTest(body=name):
                compared = data.get("cd_compared")
                reference = data.get("reference_cd")
                stored = data.get("relative_error")
                if compared is None or not reference or stored is None:
                    continue
                actual = abs(float(compared) - float(reference)) / abs(float(reference))
                # compared_cd is stored rounded to 4 decimals; allow exactly
                # that much slack relative to the reference scale.
                tol = 5e-4 + 5e-5 / abs(float(reference))
                self.assertTrue(math.isclose(actual, float(stored), abs_tol=tol),
                                f"{name}: relative_error {stored} vs recomputed {actual:.4f}")

    def test_wall_card_serves_the_compared_value(self):
        """The card's displayed 'measured' is the rebased figure of whichever
        measurement it is surfacing.

        This used to pin the card to the record's own ``cd_compared``, the
        coefficient from the mesh solved the night the file was written. That
        expectation was wrong, and it was load-bearing: a refinement ladder
        that finishes hours later measures the SAME case on a finer mesh, and
        pinning the card to the earlier figure is exactly what kept the
        coarsest rung of a finished ladder on the wall. What this test is for
        is the rebasing rule, so the rule is checked against whatever
        measurement the card surfaces, and the coarse-rung pin is gone.
        """
        import os
        os.environ.setdefault("CERTONOMOUS_CREDENTIALS", str(RESULTS))
        from chief_engineer.server import _credentials

        cards = {card["name"]: card for card in _credentials()}
        for name, data in _records():
            body = data.get("name")
            if body not in cards or data.get("cd_compared") is None:
                continue
            card = cards[body]
            with self.subTest(body=body):
                # The planform-to-frontal ratio is a property of the geometry,
                # so it is the same on every mesh of the same body.
                ratio = 1.0
                if str(data.get("basis_note") or "").startswith("rebased"):
                    ratio = float(data["cd_compared"]) / float(data["cd_measured"])
                self.assertAlmostEqual(float(card["measured"]),
                                       float(card["measured_raw"]) * ratio,
                                       places=3)
                if not card.get("finest_rung"):
                    self.assertEqual(card["measured"], data["cd_compared"])

    def test_displayed_percentage_is_recomputed_from_the_displayed_value(self):
        """ONE consistently rebased number, on the card as much as in the file.

        Surfacing a finer rung is only half the repair. Every figure standing
        beside that number, the percentage in the reason and the tier chip
        itself, has to come from the SAME measurement. A card reading 0.01892
        under a percentage derived from 0.02892 would be worse than the stale
        card it replaced, and a 37 percent deviation may not sit next to a
        VALIDATED chip.
        """
        import os
        os.environ.setdefault("CERTONOMOUS_CREDENTIALS", str(RESULTS))
        from chief_engineer.server import _credentials

        for card in _credentials():
            reference = card.get("reference_cd")
            shown = card.get("measured")
            match = _PCT.search(card.get("reason") or "")
            if shown is None or not reference or not match:
                continue
            with self.subTest(body=card["name"]):
                actual = abs(float(shown) - float(reference)) / abs(float(reference)) * 100
                self.assertLessEqual(
                    abs(actual - int(match.group(1))), 0.51,
                    f"{card['name']}: the card prints {match.group(1)}% beside "
                    f"a Cd that gives {actual:.2f}%")
                if actual > 35.0:
                    self.assertNotEqual(card["tier"], "VALIDATED")

    def test_website_asset_obeys_the_same_arithmetic(self):
        """The static wall asset is built from the same rule as the payload.

        The website builder used to print the raw solver coefficient beside a
        percentage computed on the reference's area basis, so an Ahmed card
        read "Cd 0.08978 vs 0.285" and called it 13 percent apart. Both cards
        now come from the same helper and must agree with themselves.
        """
        import sys
        scripts = str(Path(__file__).resolve().parents[1] / "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        import build_wall

        for card in build_wall._credentials_from_disk():
            reference = card.get("reference_cd")
            match = _PCT.search(card.get("reason") or "")
            if card.get("measured") is None or not reference or not match:
                continue
            with self.subTest(body=card["name"]):
                actual = (abs(float(card["measured"]) - float(reference))
                          / abs(float(reference)) * 100)
                self.assertLessEqual(abs(actual - int(match.group(1))), 0.51)
                if actual > 35.0:
                    self.assertNotEqual(card["tier"], "VALIDATED")

    def test_wall_never_serves_a_coarser_rung_than_the_lab_has_measured(self):
        """The propagation rule: a finished ladder reaches the card.

        The NACA 4412 credential was written on the coarsest rung of its own
        ladder and the finest rung landed about sixteen hours later, so the
        wall kept quoting the coarse mesh. Whenever a ladder is anchored to a
        credential's mesh, the card must carry the finest rung on record.
        """
        import os
        os.environ.setdefault("CERTONOMOUS_CREDENTIALS", str(RESULTS))
        from chief_engineer import uq
        from chief_engineer.server import _credentials

        cards = {card["name"]: card for card in _credentials()}
        checked = 0
        for name, data in _records():
            body = data.get("name")
            if body not in cards:
                continue
            study = uq.load_study(body) or {}
            levels = [lv for lv in study.get("levels", []) if lv.get("cells")]
            cells = cards[body].get("cells")
            if not levels or cells is None:
                continue
            anchored = any(int(lv["cells"]) == int(cells) for lv in levels)
            if not anchored and not cards[body].get("finest_rung"):
                continue
            checked += 1
            self.assertEqual(int(cells),
                             max(int(lv["cells"]) for lv in levels),
                             f"{body}: the card is not on the finest mesh the "
                             f"lab has measured for this case")
        self.assertGreater(checked, 0, "no laddered credential was checked")

    def test_wall_serves_only_mission_bodies(self):
        """Owner curation: the wall response carries the on-screen mission
        bodies alone. The wider graded library stays on disk, ungraded rows and
        all, but never rides the credentials payload.

        The curation list is `_WALL_BODIES` and only `_WALL_BODIES`; the
        subset assertion below is what enforces it. The hard-coded roll call
        that used to sit here was written on 2026-07-24 against the
        three-name list of that day, and 0bd166c2 later widened the list to
        the bodies that actually hold a curriculum record. Naming bodies
        twice is what let the two drift, so the names that stayed out are
        asserted against `_WALL_BODIES` rather than against a second copy of
        it."""
        import os
        os.environ.setdefault("CERTONOMOUS_CREDENTIALS", str(RESULTS))
        from chief_engineer.server import _WALL_BODIES, _credentials

        served = {card["name"] for card in _credentials()}
        self.assertTrue(served, "the wall still serves the mission bodies")
        self.assertLessEqual(served, set(_WALL_BODIES))
        for ungraded in ("ahmed_35", "cylinder", "naca0012_wing", "sphere"):
            self.assertNotIn(ungraded, _WALL_BODIES,
                             f"{ungraded} is not an on-screen mission body")
            self.assertNotIn(ungraded, served)

    def test_wall_payload_obeys_the_style_rules(self):
        """No banned words, no em dashes, and no internal file references in
        anything the wall response serves."""
        import os
        os.environ.setdefault("CERTONOMOUS_CREDENTIALS", str(RESULTS))
        from chief_engineer.server import _credentials

        blob = json.dumps(_credentials())
        self.assertNotIn("—", blob)
        self.assertNotIn("--", blob)
        low = blob.lower()
        for banned in ("demo", "stored", "saved", "cached", "pre-computed",
                       "precomputed", "recorded", "trend"):
            self.assertNotIn(banned, low, f"banned word served: {banned}")
        for internal in (".md", "docs/", "handoff", "sdk/"):
            self.assertNotIn(internal, low, f"internal reference served: {internal}")


if __name__ == "__main__":
    unittest.main()
