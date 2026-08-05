"""Tier discipline over citations: P-2.1's remaining half.

The checker reports and never repairs, so what these tests pin is the two
things a review aid has to get right. It fires on the shape of the live
2026-08-05 defect, a quantity asserted beside a tier that licenses no
quantity. And it stays silent on the four shapes that would make it useless:
an availability check reporting a paywall, a bibliography entry whose
neighbour is paywalled, a citation locator, and a block already carrying its
own dated correction.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "citation_tier_audit", REPO / "sdk" / "scripts" / "citation_tier_audit.py")
audit_mod = importlib.util.module_from_spec(_SPEC)
# Registered before execution because the module defines a dataclass, and
# dataclasses resolve their annotations through sys.modules.
sys.modules[_SPEC.name] = audit_mod
_SPEC.loader.exec_module(audit_mod)


def _rules(findings) -> set[str]:
    return {f.rule for f in findings}


class QuantityAtABelowFullTier(unittest.TestCase):
    """Rule 1, the live-defect rule."""

    LIVE = ('the paper reports average adjoint derivative error under 0.1 '
            'percent at up to 1536 cores (tier: SEARCH-EXCERPT, abstract '
            'level only)')

    def test_it_fires_on_the_incident_it_was_written_for(self):
        found = audit_mod.check_block(self.LIVE, "fixture.md", 1)
        self.assertIn("quantity asserted at a below-full tier", _rules(found))
        why = next(f.why for f in found if f.rule.startswith("quantity"))
        self.assertIn("0.1", why)
        self.assertIn("1536 cores", why)

    def test_a_full_tier_in_the_same_block_clears_it(self):
        block = self.LIVE.replace("SEARCH-EXCERPT, abstract level only",
                                  "READ IN FULL")
        self.assertNotIn("quantity asserted at a below-full tier",
                         _rules(audit_mod.check_block(block, "f.md", 1)))

    def test_a_dated_correction_in_the_block_clears_it(self):
        block = self.LIVE + " [CORRECTION 2026-08-05: the abstract joins two "
        block += "disjoint experiments; the paper is since READ IN FULL]"
        self.assertEqual(audit_mod.check_block(block, "f.md", 1), [])

    def test_a_tier_with_no_quantity_is_not_a_finding(self):
        block = ("Cappelli and Mansour, PAYWALLED, abstract-only; nothing "
                 "beyond what the abstract states is asserted from it.")
        self.assertNotIn("quantity asserted at a below-full tier",
                         _rules(audit_mod.check_block(block, "f.md", 1)))

    def test_reporting_a_paywall_is_not_declaring_a_tier(self):
        """The availability discipline is section 2 working, not failing."""
        block = ("Checked via Unpaywall before choosing this case: is_oa "
                 "false, no repository copy, so the paywalled Settles "
                 "reference was replaced and the case reports 7.05 Mach.")
        self.assertEqual(audit_mod.check_block(block, "f.md", 1), [])


class WhatCountsAsAQuantity(unittest.TestCase):
    """A citation's own machinery is digit-shaped and asserts nothing."""

    def test_identifiers_and_locators_are_not_quantities(self):
        for text in ("DOI 10.1016/j.jfluidstructs.2005.02.004",
                     "arXiv 2603.28884v1",
                     "Physics of Fluids 7(8):1841-1865",
                     "section 2.9 and table 3",
                     "NACA 0012 at RAE 2822",
                     "published in 1995, read in 2026"):
            self.assertEqual(audit_mod.quantities(text), [], text)

    def test_real_quantities_are_found(self):
        self.assertTrue(audit_mod.quantities("error under 0.1 percent"))
        self.assertTrue(audit_mod.quantities("at up to 1536 cores"))
        self.assertTrue(audit_mod.quantities("a band of 5.45e-03"))


class ATierTheCharterDoesNotDefine(unittest.TestCase):
    """Rule 2. Section 2: there is no fourth tier."""

    def test_search_excerpt_is_reported(self):
        found = audit_mod.check_block("cited at tier SEARCH-EXCERPT",
                                      "f.md", 1)
        self.assertIn("a tier the charter does not define", _rules(found))

    def test_the_three_charter_tiers_are_not_reported(self):
        for tier in ("READ IN FULL", "PAYWALLED, abstract-only",
                     "INTERNAL, already read"):
            self.assertNotIn("a tier the charter does not define",
                             _rules(audit_mod.check_block(tier, "f.md", 1)),
                             tier)


class BlockGranularity(unittest.TestCase):
    """One tier belongs to one citation, not to its neighbours."""

    BIBLIOGRAPHY = (
        "- Barkley and Henderson, Journal of Fluid Mechanics 322 (1996). "
        "PAYWALLED, not independently read.\n"
        "- Jiang and Cheng, Journal of Fluid Mechanics 812 (2017). Full "
        "text read; Strouhal 0.2105 at Reynolds 3900.\n")

    def test_a_paywalled_entry_does_not_taint_the_next_entry(self):
        blocks = audit_mod._blocks(self.BIBLIOGRAPHY)
        self.assertEqual(len(blocks), 2)
        findings = [f for line, block in blocks
                    for f in audit_mod.check_block(block, "f.md", line)]
        self.assertEqual(findings, [])

    def test_a_table_row_is_its_own_block(self):
        table = ("| Source | Tier | Cd |\n"
                 "| Norberg | READ IN FULL | 0.210 |\n"
                 "| Henderson | PAYWALLED | 1.505 |\n")
        blocks = audit_mod._blocks(table)
        self.assertEqual(len(blocks), 3)
        rules = {f.rule for line, block in blocks
                 for f in audit_mod.check_block(block, "f.md", line)}
        self.assertIn("quantity asserted at a below-full tier", rules)


class OverTheRealRecords(unittest.TestCase):
    """The replay this checker owes under charter 1 disqualifier 10.

    A rule that fires on everything cannot come out more than one way, so the
    adopted rules are held to a fire rate here rather than only in the
    docstring that states one.
    """

    def test_the_adopted_rules_stay_rare_on_the_real_corpus(self):
        files = audit_mod._iter_files(audit_mod.DEFAULT_ROOTS)
        if len(files) < 50:
            self.skipTest("records not present in this tree")
        findings = audit_mod.audit()
        self.assertLess(len(findings), len(files) // 10,
                        "the tier rules fire on over a tenth of the records "
                        "and have stopped discriminating")

    def test_rule_three_is_off_by_default(self):
        """It was replayed, it did not discriminate, and it is not adopted."""
        files = audit_mod._iter_files(audit_mod.DEFAULT_ROOTS)
        if len(files) < 50:
            self.skipTest("records not present in this tree")
        default = audit_mod.audit()
        opted_in = audit_mod.audit(untiered=True)
        self.assertNotIn("a citation carrying no tier, in a file that tiers",
                         _rules(default))
        self.assertGreater(len(opted_in), len(default))


if __name__ == "__main__":
    unittest.main()
