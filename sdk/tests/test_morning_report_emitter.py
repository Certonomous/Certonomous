"""The morning-report emitter, P-8.1's larger half.

The checker's tests (test_morning_report.py) hold the frame against reports a
human might write. These hold the emitter against the frame and against its
own hard rule: everything it prints traces to a file it read, its output
passes the landed checker on the real repository, and the same repository
state produces the same bytes.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from morning_report import (  # noqa: E402
    HEADINGS, build_morning_report, check_report)

DATE = "2026-08-04"
STAMP = "2026-08-04T06:00:00Z"

# The charter's frozen heading strings, restated here on purpose: if the
# script's HEADINGS tuple ever drifted, this test names the drift rather than
# inheriting it.
CHARTER_HEADINGS = (
    "## 1. SPEND",
    "## 2. LADDER POSITIONS",
    "## 3. GATES",
    "## 4. FD TABLES",
    "## 5. REFILLED QUEUE",
    "## 6. WAITING LIST",
)


def build(scan=lambda: []) -> str:
    return build_morning_report(REPO, DATE, STAMP, scan=scan)


class TheEmitterHoldsTheFrame(unittest.TestCase):

    def test_the_landed_checker_accepts_the_output(self):
        faults, citations = check_report(build(), repo=REPO)
        self.assertEqual([str(f) for f in faults], [])
        self.assertEqual([str(f) for f in citations], [])

    def test_the_headings_are_the_charters_frozen_strings_in_order(self):
        self.assertEqual(HEADINGS, CHARTER_HEADINGS)
        report = build()
        found = [line for line in report.splitlines()
                 if line.startswith("## ")]
        self.assertEqual(tuple(found), CHARTER_HEADINGS)

    def test_the_header_block_is_computed_not_typed(self):
        lines = build().splitlines()
        self.assertEqual(lines[0], "CERTONOMOUS MORNING REPORT")
        self.assertEqual(lines[1], f"Date:       {DATE}")
        self.assertEqual(lines[2], f"Assembled:  {STAMP}")
        self.assertEqual(lines[3], "Sections:   6 of 6")
        self.assertEqual(lines[4], "Missing:    none")

    def test_every_section_names_its_source_or_prints_pending(self):
        report = build()
        for heading in CHARTER_HEADINGS:
            index = report.index(heading)
            end = min((report.index(h) for h in CHARTER_HEADINGS
                       if report.index(h) > index), default=len(report))
            section = report[index:end]
            self.assertTrue("Source: " in section or "PENDING: " in section,
                            f"{heading} carries neither a Source line nor "
                            "the PENDING token")


class TheEmitterKeepsItsOwnRules(unittest.TestCase):

    def test_deterministic_given_the_same_repository_state(self):
        self.assertEqual(build(), build())

    def test_no_em_or_en_dash_reaches_the_page(self):
        report = build()
        self.assertNotIn("–", report)
        self.assertNotIn("—", report)

    def test_every_spend_figure_declares_its_basis(self):
        """P-6.2, carried out 2026-08-05: every core-minute figure in the
        spend section carries an inline basis, gross or cleaned, per the
        compute budget charter section 2. The dollar line is not a
        core-minute figure and the waiting list explains it."""
        report = build()
        spend = report[report.index("## 1. SPEND"):
                       report.index("## 2. LADDER POSITIONS")]
        figure_labels = ("Last night:", "Of which:", "Cleaned:",
                         "Week to date:")
        seen = []
        for line in spend.splitlines():
            if line.startswith(figure_labels):
                seen.append(line.split(":", 1)[0])
                self.assertIn("(basis: ", line, line)
                self.assertRegex(line, r"\(basis: (gross|cleaned)[;)]", line)
        self.assertEqual(sorted(seen),
                         sorted(label.rstrip(":") for label in figure_labels),
                         "a spend figure line went missing; the basis rule "
                         "covers all four")
        # And the section defines where the terms are defined.
        self.assertIn("compute budget charter section 2", spend)

    def test_a_live_process_scan_lands_on_the_left_running_line(self):
        report = build(scan=lambda: ["mpirun -np 4 simpleFoam -parallel"])
        left = next(line for line in report.splitlines()
                    if line.startswith("Left running:"))
        self.assertIn("simpleFoam", left)
        quiet = next(line for line in build().splitlines()
                     if line.startswith("Left running:"))
        self.assertIn("nothing", quiet)


class TheCommandLineRunsTheCheckerOverItsOwnOutput(unittest.TestCase):

    def test_emit_writes_self_checks_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as scratch:
            done = subprocess.run(
                [sys.executable, str(REPO / "scripts" / "morning_report.py"),
                 "--emit", "--date", DATE, "--assembled", STAMP,
                 "--out", scratch],
                capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("holds the frame", done.stdout)
            written = Path(scratch) / f"MORNING_REPORT_{DATE}.md"
            self.assertTrue(written.exists())
            faults, citations = check_report(
                written.read_text(encoding="utf-8"), repo=REPO)
            self.assertEqual([str(f) for f in faults], [])
            self.assertEqual([str(f) for f in citations], [])

    def test_a_second_emit_refuses_to_overwrite_the_morning(self):
        with tempfile.TemporaryDirectory() as scratch:
            command = [sys.executable,
                       str(REPO / "scripts" / "morning_report.py"),
                       "--emit", "--date", DATE, "--assembled", STAMP,
                       "--out", scratch]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0)
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(second.returncode, 1)
            self.assertIn("never overwritten", second.stdout)


if __name__ == "__main__":
    unittest.main()
