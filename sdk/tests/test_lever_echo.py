"""Lever echo (Verification Charter v1.5 section 9, adopted 2026-08-08):
the four lever classes stock OpenFOAM never echoes enter the run log at
launch, fenced and hash-bound, so levers_verified_active is satisfiable at
write time. The dead-lever audit's 16 unverifiable-from-logs conclusions are
the measured cost of not having this."""

import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from chief_engineer import lever_echo
from workflows import tmr_verification as tv


def _fixture_case(root: Path) -> Path:
    case = root / "case"
    (case / "system").mkdir(parents=True)
    (case / "constant").mkdir()
    (case / "0").mkdir()
    (case / "system" / "fvSchemes").write_text(
        "divSchemes { div(phi,U) bounded Gauss linearUpwind grad(U); }\n")
    (case / "system" / "fvSolution").write_text(
        "SIMPLE { consistent yes; }\n")
    (case / "constant" / "turbulenceProperties").write_text(
        "simulationType RAS;\n")
    (case / "0" / "U").write_text(
        "boundaryField { inlet { type freestreamVelocity; } }\n")
    return case


class EchoBlockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lever-echo-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.case = _fixture_case(self.tmp)

    def test_every_present_lever_file_is_echoed_and_hash_bound(self):
        block = lever_echo.echo_block(self.case)
        echoed = lever_echo.parse_echo(block)
        self.assertEqual(
            set(echoed),
            {"system/fvSchemes", "system/fvSolution",
             "constant/turbulenceProperties", "0/U"})
        # The hash binds the echo to the exact bytes that ran: class 2,
        # the SIMPLEC `consistent` flag no solver banner ever states.
        expected = hashlib.sha256(
            (self.case / "system" / "fvSolution").read_bytes()).hexdigest()
        self.assertEqual(echoed["system/fvSolution"], expected)
        self.assertIn("consistent yes", block)

    def test_a_log_without_an_echo_says_so_plainly(self):
        field = lever_echo.levers_verified_active("Time = 100\nEnd\n")
        self.assertEqual(field["verified"], [])
        self.assertIn("unverifiable", field["basis"])

    def test_the_record_field_cites_the_echo_by_hash(self):
        log_text = lever_echo.echo_block(self.case) + "Time = 100\nEnd\n"
        field = lever_echo.levers_verified_active(log_text)
        names = {entry["file"] for entry in field["verified"]}
        self.assertIn("system/fvSchemes", names)
        for entry in field["verified"]:
            self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
            self.assertIn("LEVER-ECHO", entry["evidence"])

    def test_absent_dictionaries_are_simply_absent(self):
        (self.case / "system" / "fvSolution").unlink()
        echoed = lever_echo.parse_echo(lever_echo.echo_block(self.case))
        self.assertNotIn("system/fvSolution", echoed)


class FoamRunnerEchoTests(unittest.TestCase):
    """The workflows' shared solver runner echoes for SOLVER launches only;
    utility logs stay pristine for their parsers."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lever-foam-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.case = _fixture_case(self.tmp)
        patcher = mock.patch.object(tv, "_run_prefix", return_value=["echo"])
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_solver_launch_carries_the_echo(self):
        tv._foam(["simpleFoam"], self.case, "log.simpleFoam")
        text = (self.case / "log.simpleFoam").read_text()
        self.assertTrue(text.startswith(lever_echo.BEGIN))
        self.assertIn("system/fvSchemes", lever_echo.parse_echo(text))

    def test_a_utility_launch_stays_pristine(self):
        tv._foam(["blockMesh"], self.case, "log.blockMesh")
        text = (self.case / "log.blockMesh").read_text()
        self.assertNotIn(lever_echo.BEGIN, text)


if __name__ == "__main__":
    unittest.main()
