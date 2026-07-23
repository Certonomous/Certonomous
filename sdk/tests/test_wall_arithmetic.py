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
        """The server card's displayed 'measured' is the rebased figure."""
        import os
        os.environ.setdefault("CERTONOMOUS_CREDENTIALS", str(RESULTS))
        from chief_engineer.server import _credentials

        cards = {card["name"]: card for card in _credentials()}
        for name, data in _records():
            body = data.get("name")
            if body not in cards or data.get("cd_compared") is None:
                continue
            with self.subTest(body=body):
                self.assertEqual(cards[body]["measured"], data["cd_compared"])


if __name__ == "__main__":
    unittest.main()
