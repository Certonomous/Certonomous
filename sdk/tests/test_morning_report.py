"""The morning-report frame checker, REPORTING_CHARTER section 2.

Every test here is a report a human could plausibly hand in. The point of the
frame is that a report which skipped a section is rejected by a rule rather
than noticed by a reader, so each malformed case asserts WHICH rule fired, not
merely that something did.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from morning_report import check_report  # noqa: E402


HEADER = """CERTONOMOUS MORNING REPORT
Date:       2026-08-01
Assembled:  2026-08-01T06:00:00Z
Sections:   6 of 6
Missing:    none
"""

# Two paths that exist in this repository, used so rule 7 is exercised on real
# resolution rather than on a stub.
REAL = "docs/charters/REPORTING_CHARTER.md"
REAL2 = "demo-output/website/agenda/docket.json"


def body(section: str, text: str) -> str:
    return f"\n{section}\n\n{text}\n"


def good_report(**overrides: str) -> str:
    parts = {
        "## 1. SPEND": f"212.28 core-hours cleaned.\nSource: {REAL2}",
        "## 2. LADDER POSITIONS": f"flat plate at five rungs.\nSource: {REAL}",
        "## 3. GATES": f"nothing\nSource: {REAL}",
        "## 4. FD TABLES": "PENDING: demo-output/website/dafoam/not_here.md",
        "## 5. REFILLED QUEUE": f"40 approved and unstarted.\nSource: {REAL2}",
        "## 6. WAITING LIST": f"nothing\nSource: {REAL2}",
    }
    parts.update(overrides)
    return HEADER + "".join(body(k, v) for k, v in parts.items())


def rules(findings) -> list[str]:
    return [finding.rule for finding in findings]


class AcceptsAWellFormedReport(unittest.TestCase):

    def test_the_frame_holds_and_nothing_is_flagged(self):
        faults, citations = check_report(good_report(), repo=REPO)
        self.assertEqual([str(f) for f in faults], [])
        self.assertEqual([str(f) for f in citations], [])

    def test_pending_needs_no_source_line_and_nothing_does(self):
        # The two reserved words are not symmetric, and the checker says so.
        faults, _ = check_report(good_report(**{
            "## 3. GATES": "nothing"}), repo=REPO)
        self.assertEqual(rules(faults), ["RULE 6"])


class RejectsASkippedSection(unittest.TestCase):
    """The failure the charter exists to prevent: five sections, no comment."""

    def test_a_missing_heading_fails_rule_1_and_the_recount(self):
        report = good_report()
        report = report.replace(body(
            "## 4. FD TABLES",
            "PENDING: demo-output/website/dafoam/not_here.md"), "")
        faults, _ = check_report(report, repo=REPO)
        self.assertIn("RULE 1", rules(faults))
        # And the header still claims six, which rule 3 recounts.
        self.assertIn("RULE 3", rules(faults))
        self.assertTrue(any("4. FD TABLES" in str(f) for f in faults))

    def test_a_report_that_admits_the_gap_still_fails_only_rule_1(self):
        # Honest about the count, still malformed: the section is required.
        report = good_report().replace("Sections:   6 of 6",
                                       "Sections:   5 of 6")
        report = report.replace("Missing:    none", "Missing:    4")
        report = report.replace(body(
            "## 4. FD TABLES",
            "PENDING: demo-output/website/dafoam/not_here.md"), "")
        faults, _ = check_report(report, repo=REPO)
        self.assertEqual(rules(faults), ["RULE 1"])


class RejectsTheOtherSevenWays(unittest.TestCase):

    def test_a_retitled_heading_is_not_the_heading(self):
        faults, _ = check_report(
            good_report().replace("## 3. GATES", "## 3. GATE STATUS"),
            repo=REPO)
        self.assertIn("RULE 1", rules(faults))
        self.assertIn("RULE 2", rules(faults))

    def test_headings_out_of_order(self):
        report = good_report()
        one = body("## 1. SPEND", f"212.28 core-hours cleaned.\nSource: {REAL2}")
        two = body("## 2. LADDER POSITIONS",
                   f"flat plate at five rungs.\nSource: {REAL}")
        report = report.replace(one + two, two + one)
        faults, _ = check_report(report, repo=REPO)
        self.assertIn("RULE 1", rules(faults))
        self.assertTrue(any("out of order" in str(f) for f in faults))

    def test_a_seventh_section_is_a_fault(self):
        faults, _ = check_report(
            good_report() + body("## 7. NOTES", "a thought\nSource: x"),
            repo=REPO)
        self.assertIn("RULE 2", rules(faults))

    def test_a_typed_count_that_disagrees_with_the_headings(self):
        faults, _ = check_report(
            good_report().replace("Sections:   6 of 6", "Sections:   5 of 6"),
            repo=REPO)
        self.assertEqual(rules(faults), ["RULE 3"])

    def test_missing_line_must_name_the_sections(self):
        report = good_report().replace("Sections:   6 of 6", "Sections:   5 of 6")
        report = report.replace(body(
            "## 5. REFILLED QUEUE",
            f"40 approved and unstarted.\nSource: {REAL2}"), "")
        faults, _ = check_report(report, repo=REPO)
        self.assertIn("RULE 3", rules(faults))
        self.assertTrue(any("'5'" in str(f) for f in faults))

    def test_an_empty_section_is_not_the_word_nothing(self):
        faults, _ = check_report(good_report(**{"## 3. GATES": ""}), repo=REPO)
        self.assertIn("RULE 4", rules(faults))

    def test_nothing_beside_content_is_a_contradiction(self):
        faults, _ = check_report(good_report(**{
            "## 3. GATES": f"nothing\nexcept the hump\nSource: {REAL}"}),
            repo=REPO)
        self.assertIn("RULE 4", rules(faults))

    def test_pending_prints_nothing_else(self):
        faults, _ = check_report(good_report(**{
            "## 4. FD TABLES": "PENDING: a/b.md\nand also this"}), repo=REPO)
        self.assertEqual(rules(faults), ["RULE 5"])

    def test_content_without_a_source_line(self):
        faults, _ = check_report(good_report(**{
            "## 1. SPEND": "212.28 core-hours cleaned."}), repo=REPO)
        self.assertEqual(rules(faults), ["RULE 6"])

    def test_a_cited_artifact_that_is_not_on_disk(self):
        faults, citations = check_report(good_report(**{
            "## 1. SPEND": "212.28 core-hours.\nSource: demo-output/nope.json"}),
            repo=REPO)
        self.assertEqual(faults, [])
        self.assertEqual(rules(citations), ["RULE 7"])
        self.assertIn("1. SPEND", str(citations[0]))


class RejectsABrokenHeader(unittest.TestCase):

    def test_the_title_line(self):
        faults, _ = check_report(
            good_report().replace("CERTONOMOUS MORNING REPORT", "Morning notes"),
            repo=REPO)
        self.assertIn("HEADER", rules(faults))

    def test_a_date_that_is_not_a_date(self):
        faults, _ = check_report(
            good_report().replace("Date:       2026-08-01",
                                  "Date:       this morning"), repo=REPO)
        self.assertIn("HEADER", rules(faults))

    def test_an_assembled_stamp_that_is_not_utc(self):
        faults, _ = check_report(
            good_report().replace("Assembled:  2026-08-01T06:00:00Z",
                                  "Assembled:  about six"), repo=REPO)
        self.assertIn("HEADER", rules(faults))


if __name__ == "__main__":
    unittest.main()
