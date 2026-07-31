"""Tests for the validation-hierarchy tiers and the credibility scorecard.

Two approved agenda items: r1-validation-tier-labels and
r1-credibility-scorecard. The contract these tests defend is that both are
ADDITIONS beside a fidelity chip and neither changes what a chip means.
"""

import json
import sys
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer import credibility as cred
from chief_engineer import lab

RESULTS = SDK.parent / "models" / "curriculum" / "results"


class ValidationTierTests(unittest.TestCase):
    def test_the_four_tiers_are_the_published_hierarchy(self):
        self.assertEqual(
            cred.VALIDATION_TIERS,
            ("UNIT PROBLEM", "BENCHMARK CASE", "SUBSYSTEM CASE",
             "COMPLETE SYSTEM"))

    def test_the_recorded_mapping_is_honoured(self):
        # These five placements are recorded in the lab's own reading of the
        # report and must not drift.
        self.assertEqual(cred.validation_tier("cylinder"), "UNIT PROBLEM")
        self.assertEqual(cred.validation_tier("flat_plate"), "BENCHMARK CASE")
        self.assertEqual(cred.validation_tier("motorbike"), "BENCHMARK CASE")
        self.assertEqual(cred.validation_tier("valve"), "SUBSYSTEM CASE")
        self.assertEqual(cred.validation_tier("airliner"), "COMPLETE SYSTEM")

    def test_every_tier_is_a_known_tier(self):
        for slug, tier in cred.labelled_cases().items():
            self.assertIn(tier, cred.VALIDATION_TIERS, slug)

    def test_every_case_carries_a_basis(self):
        for slug in cred.labelled_cases():
            basis = cred.validation_tier_basis(slug)
            self.assertTrue(basis and basis.strip(), slug)

    def test_aliases_resolve(self):
        for alias, canonical in (("aortic_valve", "valve"),
                                 ("valve-study", "valve"),
                                 ("naca4412", "naca4412_wing"),
                                 ("aircraft_optimization", "airliner")):
            self.assertEqual(cred.validation_tier(alias),
                             cred.validation_tier(canonical), alias)

    def test_an_unregistered_case_gets_no_guess(self):
        # Guessing a tier is exactly the fabrication this module prevents.
        self.assertIsNone(cred.validation_tier("no_such_body"))
        self.assertIsNone(cred.validation_tier(None))
        self.assertIsNone(cred.tier_label("no_such_body"))

    def test_the_two_bodies_the_first_pass_missed_are_placed(self):
        # "Label every case in the lab" is the objective, and these two are
        # named bodies the lab has solved that the first pass left unplaced.
        self.assertEqual(cred.validation_tier("mach_tutorial_wing"),
                         "BENCHMARK CASE")
        self.assertEqual(cred.validation_tier("airliner_wing_span52"),
                         "SUBSYSTEM CASE")

    def test_every_graded_case_on_disk_is_labelled(self):
        # "Label every case in the lab" is the objective; a graded record with
        # no tier is the failure this test exists to catch.
        unlabelled = [path.stem for path in sorted(RESULTS.glob("*.json"))
                      if cred.validation_tier(path.stem) is None]
        self.assertEqual(unlabelled, [])

    def test_the_label_explains_the_ceiling_and_what_unlocks_it(self):
        label = cred.tier_label("airliner")
        self.assertEqual(label["validation_tier"], "COMPLETE SYSTEM")
        self.assertEqual(label["rank"], 4)
        self.assertEqual(label["of"], 4)
        for key in ("basis", "data_available", "ceiling", "unlocked_by",
                    "citation"):
            self.assertTrue(label[key].strip(), key)


class ScorecardTests(unittest.TestCase):
    def test_the_two_factors_the_chips_do_not_encode(self):
        card = cred.scorecard({})
        names = [f["factor"] for f in card["factors"]]
        self.assertEqual(names, ["Input pedigree", "Results robustness"])

    def test_every_level_is_on_the_published_scale(self):
        for record in ({}, {"reference_source": "x"},
                       {"grid_study": {"grid_conclusive": True},
                        "envelope": 0.1},
                       {"sobol_indices": {"a": 0.5}}):
            for factor in cred.scorecard(record)["factors"]:
                self.assertGreaterEqual(factor["level"], 0)
                self.assertLessEqual(factor["level"], cred.MAX_LEVEL)
                self.assertEqual(factor["of"], cred.MAX_LEVEL)
                self.assertTrue(factor["note"].strip())

    def test_untraceable_inputs_score_zero(self):
        self.assertEqual(cred.scorecard({})["factors"][0]["level"], 0)

    def test_a_traced_operating_point_outscores_a_bare_reference(self):
        bare = cred.scorecard({"reference_source": "a published polar"})
        traced = cred.scorecard({
            "reference_source": "a published polar",
            "comparison": {"solved_reynolds": 3e6, "regime": "matched"}})
        self.assertGreater(traced["factors"][0]["level"],
                           bare["factors"][0]["level"])

    def test_a_regime_mismatch_does_not_earn_the_traced_level(self):
        card = cred.scorecard({
            "reference_source": "a published polar",
            "comparison": {"solved_reynolds": 3e6,
                           "regime": "REFERENCE REGIME MISMATCH"}})
        self.assertEqual(card["factors"][0]["level"], 2)

    def test_robustness_rises_with_what_is_actually_known(self):
        levels = [
            cred.scorecard({})["factors"][1]["level"],
            cred.scorecard({"grid_study": {"rungs": [1, 2, 3]}}
                           )["factors"][1]["level"],
            cred.scorecard({"grid_study": {"rungs": [1, 2, 3],
                                           "grid_conclusive": True}}
                           )["factors"][1]["level"],
            cred.scorecard({"grid_study": {"rungs": [1, 2, 3],
                                           "grid_conclusive": True},
                            "envelope": 0.002})["factors"][1]["level"],
            cred.scorecard({"sobol_indices": {"a": 0.6}}
                           )["factors"][1]["level"],
        ]
        self.assertEqual(levels, [0, 1, 2, 3, 4])

    def test_apportioned_variance_is_the_top_level(self):
        # This is the link to the sensitivity mission: apportioning variance
        # is what moves a result to the top of the robustness scale.
        card = cred.scorecard({"sobol_indices": {"flow": 0.39, "cd": 0.61}})
        self.assertEqual(card["factors"][1]["level"], 4)

    def test_a_placard_needs_all_three_parts(self):
        with self.assertRaises(ValueError):
            cred.domain_placard("a screening cap", "", "model form")
        placard = cred.domain_placard(
            "a screening cap", "alpha near 17 against a ceiling of 25",
            "carried as model form")
        self.assertEqual(sorted(placard),
                         ["consequences", "extent", "limit"])

    def test_a_placard_rides_the_scorecard_when_given(self):
        placard = cred.domain_placard("a cap", "an extent", "a consequence")
        self.assertNotIn("placard", cred.scorecard({}))
        self.assertIn("placard", cred.scorecard({}, placard=placard))


class ChipsAreUntouchedTests(unittest.TestCase):
    """The load-bearing guarantee: this module adds, it never redefines."""

    def test_the_four_chips_still_mean_what_they_meant(self):
        self.assertEqual(lab.VALIDATED, "VALIDATED")
        self.assertEqual(lab.SOLVER_BACKED, "SOLVER-BACKED")
        self.assertEqual(lab.CONCEPTUAL, "RESEARCH MODEL")
        self.assertEqual(lab.UNCONVERGED, "UNCONVERGED")

    def test_the_module_defines_no_chip_of_its_own(self):
        source = (SDK / "chief_engineer" / "credibility.py").read_text(
            encoding="utf-8")
        for chip in ("VALIDATED", "SOLVER-BACKED", "UNCONVERGED"):
            self.assertNotIn(f'"{chip}"', source, chip)

    def test_the_tier_field_never_collides_with_the_chip_field(self):
        # "tier" already means the fidelity chip everywhere in this codebase.
        block = cred.credibility_block("airliner", {})
        self.assertIn("validation_tier", block)
        self.assertNotIn("tier", block)

    def test_a_block_is_produced_even_for_an_unregistered_case(self):
        block = cred.credibility_block("no_such_body", {})
        self.assertIn("credibility", block)
        self.assertNotIn("validation_tier", block)


class RegisterTests(unittest.TestCase):
    """Anything here can reach a camera surface, so it obeys the register."""

    def _strings(self):
        out = []
        for slug in cred.labelled_cases():
            label = cred.tier_label(slug)
            out.extend(str(v) for v in label.values())
        for record in ({}, {"reference_source": "x"},
                       {"sobol_indices": {"a": 1.0}}):
            card = cred.scorecard(record)
            out.append(card["scale"])
            out.append(card["citation"])
            for factor in card["factors"]:
                out.append(factor["factor"])
                out.append(factor["note"])
        return out

    def test_no_dash_reaches_any_of_these_strings(self):
        for text in self._strings():
            self.assertNotIn("—", text, text)
            self.assertNotIn("–", text, text)
            self.assertNotIn("→", text, text)

    def test_no_banned_vocabulary(self):
        for text in self._strings():
            lowered = text.lower()
            self.assertNotIn("conceptual model", lowered, text)
            self.assertNotIn("solver-backed", lowered, text)
            self.assertNotIn("solver backed", lowered, text)
            self.assertNotIn("http", lowered, text)

    def test_no_internal_paths_or_file_references(self):
        import re
        for text in self._strings():
            self.assertIsNone(re.search(r"docs/|\.md\b|\.py\b|\.json\b", text),
                              text)


class RecordArtifactTests(unittest.TestCase):
    """The tier labels are written to the permanent record, not only served."""

    ARTIFACT = (SDK.parent / "demo-output" / "website" / "credibility"
                / "validation_tiers.json")

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(cls.ARTIFACT.read_text(encoding="utf-8")) \
            if cls.ARTIFACT.exists() else None

    def test_the_artifact_exists_and_covers_every_labelled_case(self):
        self.assertTrue(self.ARTIFACT.exists(),
                        "the tier record has not been generated")
        cases = {row["case"]: row for row in self.data["cases"]}
        self.assertEqual(sorted(cases), sorted(cred.labelled_cases()))
        for slug, row in cases.items():
            self.assertEqual(row["validation_tier"],
                             cred.validation_tier(slug))
            self.assertTrue(row["display_name"])

    def test_the_record_matches_what_the_generator_produces_today(self):
        # A record that drifts from the module it was generated from is worse
        # than no record. Everything but the timestamp must still agree.
        sys.path.insert(0, str(SDK / "scripts"))
        from build_credibility_record import build

        fresh = build()
        fresh.pop("generated_at", None)
        stored = dict(self.data)
        stored.pop("generated_at", None)
        self.assertEqual(fresh, stored)

    def test_the_record_carries_no_chip_of_its_own(self):
        # The chip lives on each case's own record and stays the one
        # authority. A second copy here would be a second thing to drift, and
        # some of those records still carry vocabulary that has been retired.
        for row in self.data["cases"]:
            self.assertNotIn("fidelity_chip", row, row["case"])
            self.assertNotIn("tier", row, row["case"])

    def test_every_graded_case_carries_a_scorecard_on_both_factors(self):
        graded = [path.stem for path in sorted(RESULTS.glob("*.json"))]
        self.assertTrue(graded)
        scored = {row["case"]: row for row in self.data["cases"]
                  if "credibility" in row}
        self.assertEqual(sorted(scored), sorted(graded))
        for slug, row in scored.items():
            factors = row["credibility"]["factors"]
            self.assertEqual([f["factor"] for f in factors],
                             ["Input pedigree", "Results robustness"])
            for factor in factors:
                self.assertLessEqual(factor["level"], cred.MAX_LEVEL)
                self.assertTrue(factor["note"].strip())

    def test_an_unplaced_case_gets_a_tier_and_no_invented_scorecard(self):
        # A case the lab has placed but never graded gets its tier and no
        # scorecard, rather than a row of zeros that would read as a measured
        # judgment on evidence nobody gathered.
        graded = {path.stem for path in RESULTS.glob("*.json")}
        ungraded = [row for row in self.data["cases"]
                    if row["case"] not in graded]
        self.assertTrue(ungraded)
        for row in ungraded:
            self.assertNotIn("credibility", row, row["case"])
            self.assertTrue(row["validation_tier"])

    def test_an_unregistered_display_name_is_declared_not_hidden(self):
        # The display-name registry is the one ratified mapping and this
        # record never writes a name of its own. Where the registry has no
        # entry the fallback reads as a slug, so the record says which rows
        # those are and a surface can decline to show them.
        declared = set(self.data["cases_without_a_registered_display_name"])
        flagged = {row["case"] for row in self.data["cases"]
                   if not row["display_name_registered"]}
        self.assertEqual(declared, flagged)


if __name__ == "__main__":
    unittest.main()
