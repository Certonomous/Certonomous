"""A certificate that could not be read is not a certificate that agreed.

WHY. Docket B2. The rung's defect class is a gate that answers "what did I
find?" without first answering "did I run?", and reports the second question's
silence as a pass.

THE DEFECT THIS PINS is a denominator, not a status. The mesh-certificate
recheck of 2026-08-10 built its population with

    for p in RUNS.rglob('birth_certificate.json'):
        try: d = json.loads(p.read_text())
        except Exception: continue

so any certificate that would not parse left the population without a trace,
and the record it wrote then published `total`, `agree`, `drift` and
`points_hash_mismatch` over what remained. The published record had four
buckets and none of them was "could not be read".

THE INJECTION `test_an_unreadable_certificate_does_not_vanish_from_the_record`
runs: two retrospective certificates on disk, one truncated mid-JSON, checkMesh
stubbed to return a clean log. Before the fix the record read `total: 1,
agree: 1` -- a hundred per cent agreement over a population silently one
smaller than the directory it claimed to sweep -- and the skipped file's name
appeared nowhere in it.

WHAT THIS IS NOT EVIDENCE OF. It is NOT evidence that the committed
`recheck_95_record.json` is wrong. That record was re-checked against the tree
on 2026-08-11: 127 birth certificates on disk, 0 unparseable, 95 retrospective,
which is the number it published. The blind spot did not bite that run. The
finding is that the run could not have told anyone either way, and a figure
whose frame nobody can state is worse than no figure (L-75).

The script already had this exact third verdict for its INNER loop -- a
checkMesh that did not run states no cell count, so `ran` guards `agree` and
`checkMesh_did_not_run` is its own bucket. The fix is that bucket's twin one
level out, which is why `TheInnerThirdVerdictStillHoldsTests` is here too: a
repair that broke the working half would be a poor trade.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SCRIPT = (REPO / "demo-output" / "website" / "campaign"
          / "MESH_CERT_RULINGS_2026-08-10" / "recheck_95.py")

CLEAN_LOG = ("Mesh stats\n    points:           1000\n"
             "    cells:            500\n"
             "Checking geometry...\n"
             "Mesh OK.\n\nEnd\n")
NO_CELLS_LOG = "--> FOAM FATAL ERROR: cannot find file controlDict\nEnd\n"


def _load():
    spec = importlib.util.spec_from_file_location("recheck_95_under_test",
                                                  SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _Harness(unittest.TestCase):
    """A throwaway runs tree and a stubbed checkMesh. No solver is launched."""

    def setUp(self):
        if not SCRIPT.exists():
            self.skipTest(f"{SCRIPT} is the subject of this test; without it "
                          f"nothing here asserts anything")
        self.mod = _load()
        self._dir = tempfile.TemporaryDirectory()
        root = Path(self._dir.name)
        self.runs = root / "runs"
        self.out = root / "out"
        self.tmp = root / "tmp"
        for path in (self.runs, self.out, self.tmp):
            path.mkdir(parents=True)

    def tearDown(self):
        self._dir.cleanup()

    def _case(self, name: str, certificate: str):
        case = self.runs / name
        (case / "constant" / "polyMesh").mkdir(parents=True)
        (case / "system").mkdir(parents=True)
        (case / "system" / "controlDict").write_text("x")
        (case / "constant" / "polyMesh" / "points").write_text("100\n(\n)\n")
        (case / "constant" / "birth_certificate.json").write_text(certificate)
        return case

    def _good(self, cells: int = 500, verdict: str = "clean") -> str:
        return json.dumps({"provenance": "retrospective-from-archived-log",
                           "verdict": verdict, "cells": cells,
                           "points_sha256": None})

    def _run(self, log: str = CLEAN_LOG):
        done = subprocess.CompletedProcess(["checkMesh"], 0, log, "")
        with mock.patch.object(self.mod, "RUNS", self.runs), \
                mock.patch.object(self.mod, "OUT", self.out), \
                mock.patch.object(self.mod, "TMP", self.tmp), \
                mock.patch.object(self.mod.subprocess, "run",
                                  return_value=done):
            code = self.mod.main()
        record = json.loads(
            (self.out / "recheck_95_record.json").read_text())
        return code, record


class TheUnreadableCertificateIsAThirdVerdictTests(_Harness):
    """Evidence FOR: a certificate the sweep could not open reaches the
    record, instead of shrinking the denominator in silence."""

    def test_an_unreadable_certificate_does_not_vanish_from_the_record(self):
        """THE INJECTION. Before the fix: total 1, agree 1, name nowhere."""
        self._case("case_good", self._good())
        self._case("case_unreadable", '{"provenance": "retrospective-from-arch')
        code, record = self._run()
        self.assertEqual(1, record["certificates_unreadable"], record["frame"])
        self.assertEqual(2, record["certificates_found"])
        self.assertIn("case_unreadable",
                      json.dumps(record["unreadable_rows"]),
                      "the skipped certificate is not named in the record")
        self.assertIn("NOT counted as agreeing",
                      json.dumps(record["unreadable_rows"]))
        self.assertNotEqual(0, code,
                            "a run that could not read a certificate exited "
                            "clean, which is the green that means 'I looked at "
                            "nothing'")

    def test_the_record_states_its_own_denominator(self):
        """A number whose frame nobody can state is worse than no number
        (L-75). The frame line has to survive in the record itself."""
        self._case("case_good", self._good())
        _, record = self._run()
        self.assertIn("frame", record)
        for owed in ("birth_certificate.json", "denominator",
                     "AN UNREADABLE CERTIFICATE IS NOT AN AGREEING ONE"):
            self.assertIn(owed, record["frame"])

    def test_a_clean_population_still_exits_zero_and_says_zero(self):
        """The positive control on both negatives above. Without it the fix
        could be 'never exit clean again', which states nothing."""
        self._case("case_good", self._good())
        self._case("case_also_good", self._good())
        code, record = self._run()
        self.assertEqual(0, code)
        self.assertEqual(0, record["certificates_unreadable"])
        self.assertEqual(2, record["certificates_found"])
        self.assertEqual(2, record["total"])
        self.assertEqual(2, record["agree"])
        self.assertEqual([], record["unreadable_rows"])

    def test_a_non_retrospective_certificate_is_excluded_but_not_unreadable(
            self):
        """The two reasons a certificate leaves the population must not be
        confused: out of scope by provenance is not the same as unreadable,
        and only one of them is a blind spot."""
        self._case("case_good", self._good())
        self._case("case_at_creation", json.dumps(
            {"provenance": "at-creation", "verdict": "clean", "cells": 500,
             "points_sha256": None}))
        code, record = self._run()
        self.assertEqual(0, code)
        self.assertEqual(2, record["certificates_found"])
        self.assertEqual(0, record["certificates_unreadable"])
        self.assertEqual(1, record["total"])


class TheInnerThirdVerdictStillHoldsTests(_Harness):
    """Evidence FOR: the repair did not break the third verdict the script
    already had. A checkMesh that did not run states no cell count, and that
    was never allowed to read as agreement."""

    def test_a_checkmesh_that_did_not_run_is_not_an_agreement(self):
        self._case("case_good", self._good())
        code, record = self._run(log=NO_CELLS_LOG)
        self.assertEqual(1, record["checkMesh_did_not_run"])
        self.assertEqual(0, record["agree"])
        self.assertEqual(1, record["total"])

    def test_a_checkmesh_that_did_run_and_matches_is_an_agreement(self):
        """The positive control on the negative above."""
        self._case("case_good", self._good())
        _, record = self._run(log=CLEAN_LOG)
        self.assertEqual(0, record["checkMesh_did_not_run"])
        self.assertEqual(1, record["agree"])


if __name__ == "__main__":
    unittest.main()
