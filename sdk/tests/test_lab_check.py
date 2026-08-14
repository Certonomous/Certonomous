"""Both halves of the control on the runner itself (L-84).

L-84: a positive control proves an instrument CAN fire; it does not prove it
fires only where it should. A runner that goes FAIL on everything is not a
runner, it is an alarm, and an alarm gets switched off inside a day -- after
which it is worse than nothing, because it looks like coverage.

So every case here is a PAIR built in a throwaway git repository: the same tree
with a defect planted and without it. Nothing here touches the live repo.

The four things being pinned, each of which this lab has been burned by:

  * PLANTED DEFECT -> FAIL. A failing script gate and a failing test file each
    turn the aggregate red on their own.
  * NO DEFECT -> PASS. The same tree, unplanted, comes back clean. Without
    this half the FAIL above proves nothing.
  * NO CHECKS -> UNKNOWN, never PASS. Defect class B1, the silent-zero sweep:
    a checker that examined nothing and reported clean. This is the class this
    lab ranks highest (D62).
  * A PRINTER IS NOT A GATE. A script whose main() returns the constant 0 is
    not admitted, and a tree containing only printers reads UNKNOWN rather than
    PASS -- which is D64's own criterion about `gate_table.py` turned into a
    test.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / "scripts" / "lab_check.py"

_SPEC = importlib.util.spec_from_file_location("lab_check_under_test", RUNNER)
lc = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = lc
_SPEC.loader.exec_module(lc)

GATE = '''\
#!/usr/bin/env python3
"""A gate whose exit code is a function of its finding."""
import sys

FINDINGS = {findings}


def main():
    print(f"VERDICT: {{'FAIL' if FINDINGS else 'PASS'}}")
    return 1 if FINDINGS else 0


if __name__ == "__main__":
    sys.exit(main())
'''

PRINTER = '''\
#!/usr/bin/env python3
"""The gate_table.py shape: it reports, and its exit code is a constant."""
import sys


def main():
    print("[FAIL] something is wrong, and this program will still exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

TEST_FILE = '''\
import unittest


class T(unittest.TestCase):
    def test_it(self):
        self.assertEqual(1, {rhs})
'''


def _repo(tmp: Path, *, gate_findings=None, printer=False, tests=None) -> Path:
    root = tmp / "repo"
    (root / "scripts").mkdir(parents=True)
    (root / "sdk" / "tests").mkdir(parents=True)
    if gate_findings is not None:
        (root / "scripts" / "gate.py").write_text(
            GATE.format(findings=gate_findings))
    if printer:
        (root / "scripts" / "printer.py").write_text(PRINTER)
    if tests is not None:
        (root / "sdk" / "tests" / "test_planted.py").write_text(
            TEST_FILE.format(rhs=tests))
    (root / "README").write_text("fixture tree\n")   # so an empty repo commits
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "fixture"], cwd=root, check=True)
    return root


def _run(root: Path, *extra: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--root", str(root), *extra],
        capture_output=True, text=True, timeout=600)
    return proc.returncode, proc.stdout + proc.stderr


class TheRunnerFiresOnAPlantedDefect(unittest.TestCase):
    def test_a_failing_script_gate_turns_the_aggregate_red(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), gate_findings="['a defect']")
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, lc.EXIT[lc.FAIL], out)
        self.assertIn("VERDICT: FAIL", out)
        self.assertIn("scripts/gate.py", out)

    def test_a_failing_test_file_turns_the_aggregate_red(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), tests="2")
            rc, out = _run(root)
        self.assertEqual(rc, lc.EXIT[lc.FAIL], out)
        self.assertIn("test_planted.py", out)


class TheRunnerIsSilentWhereItShouldBe(unittest.TestCase):
    """The half that L-84 says is the one usually missing."""

    def test_the_same_tree_without_the_defect_comes_back_PASS(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), gate_findings="[]")
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, lc.EXIT[lc.PASS], out)
        self.assertIn("VERDICT: PASS", out)

    def test_a_passing_gate_and_a_passing_suite_together_are_PASS(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), gate_findings="[]", tests="1")
            rc, out = _run(root)
        self.assertEqual(rc, lc.EXIT[lc.PASS], out)


class AnEmptyCheckSetIsNeverAPass(unittest.TestCase):
    """Defect class B1: the sweep that examined nothing and reported clean."""

    def test_no_checks_at_all_is_UNKNOWN(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp))
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, lc.EXIT[lc.UNKNOWN], out)
        self.assertIn("VERDICT: UNKNOWN", out)
        self.assertIn("no check was admitted", out)

    def test_a_tree_of_printers_is_UNKNOWN_not_PASS(self):
        """D64's own criterion: a main() that returns 0 unconditionally cannot fail."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), printer=True)
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, lc.EXIT[lc.UNKNOWN], out)
        self.assertIn("cannot-fail", out)


class ASuiteThatCoveredLessThanItClaimed(unittest.TestCase):
    """`7bf55c90`: a "Full suite 115 passed" that was one test file run alone.

    The tree it certified had 1,609 tests in 69 files. Nothing was lying: the
    number 115 was real, the tests really passed, and the label was wrong. No
    check catches that, because the defect is in the FRAME of the claim rather
    than in any measurement inside it.

    This is the runner's answer: the suite is run over the DIRECTORY, the test
    files are enumerated INDEPENDENTLY from git and the disk, and the two are
    diffed. A file that was enumerated and produced no collected test is named:
    FAIL if it declares tests and contributed none, UNKNOWN if it declares none.
    A green whose frame does not cover its enumeration is not a green.
    """

    COLLECTS_NOTHING = '''\
import unittest


class NotPickedUpByPytest(unittest.TestCase):     # class name does not match
    def checks_something(self):                    # method name does not match
        self.assertEqual(1, 1)
'''

    HELPER_WITH_NO_TESTS = '''\
"""A helper that happens to be named test_something.py. It declares no test."""

CONSTANT = 3
'''

    def test_a_file_that_declares_tests_and_contributes_none_is_FAIL(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), tests="1")
            (root / "sdk" / "tests" / "test_silent.py").write_text(
                self.COLLECTS_NOTHING)
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            rc, out = _run(root)
        self.assertEqual(rc, lc.EXIT[lc.FAIL], out)
        self.assertIn("enumerated but not collected: sdk/tests/test_silent.py",
                      out)
        self.assertIn("test files enumerated 2", out)
        self.assertIn("test files collected  1", out)

    def test_a_helper_that_declares_no_test_is_only_UNKNOWN(self):
        """The must-not-match half: this is not a defect, and calling it one is
        how a runner earns a permanent false alarm and gets switched off."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), tests="1")
            (root / "sdk" / "tests" / "test_helpers_only.py").write_text(
                self.HELPER_WITH_NO_TESTS)
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            rc, out = _run(root)
        self.assertEqual(rc, lc.EXIT[lc.UNKNOWN], out)
        self.assertIn("none of them declares a test", out)

    def test_without_the_plant_the_same_tree_is_PASS(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), tests="1")
            rc, out = _run(root)
        self.assertEqual(rc, lc.EXIT[lc.PASS], out)

    def test_every_run_prints_what_the_suite_actually_covered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), tests="1")
            rc, out = _run(root)
        self.assertIn("SUITE FRAME", out)
        self.assertIn("tests collected", out)
        self.assertIn("test files enumerated", out)


class TheFrameIsPrinted(unittest.TestCase):
    def test_the_run_states_how_many_it_found_ran_and_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), gate_findings="[]", printer=True)
            rc, out = _run(root, "--no-tests")
        self.assertIn("FRAME", out)
        self.assertIn("candidates", out)
        self.assertIn("SKIPPED, BY REASON", out)
        self.assertIn("check(s) ran", out)


class AdmissionPredicates(unittest.TestCase):
    """The predicates, unit level, because the whole-runner cases are slow."""

    def _classify(self, body: str, name: str = "c.py", **kw):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / name).write_text(body)
            cand = lc.Candidate(path=f"scripts/{name}", frames=("worktree",))
            return lc.classify(root, cand, allow_writers=kw.get("writers", False))

    def test_a_constant_zero_exit_is_not_a_gate(self):
        c = self._classify(PRINTER)
        self.assertFalse(c.admitted)
        self.assertIn("cannot-fail", c.reason)

    def test_a_data_dependent_exit_is_a_gate(self):
        c = self._classify(GATE.format(findings="[]"))
        self.assertTrue(c.admitted, c.reason)

    def test_a_nested_helpers_return_is_not_the_exit_path(self):
        """`ugrid_to_foam.py` reads as a gate if nested returns are counted."""
        c = self._classify(
            'import sys\n'
            'def main():\n'
            '    def helper():\n'
            '        return "some string"\n'
            '    print(helper())\n'
            '    return 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertFalse(c.admitted)
        self.assertIn("cannot-fail", c.reason)

    def test_str_replace_is_not_a_write(self):
        """The first cut skipped self_audit.py on a `line.replace("\\n", ...)`."""
        c = self._classify(
            'import sys\n'
            'def main():\n'
            '    s = "a\\nb".replace("\\n", " ")\n'
            '    return 1 if s else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertTrue(c.admitted, c.reason)

    def test_os_replace_is_a_write(self):
        c = self._classify(
            'import os, sys\n'
            'def main():\n'
            '    os.replace("a", "b")\n'
            '    return 1 if os.path.exists("b") else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertFalse(c.admitted)
        self.assertIn("writes-to-tree", c.reason)

    def test_a_write_capable_check_is_admitted_in_snapshot_mode(self):
        c = self._classify(
            'import os, sys\n'
            'def main():\n'
            '    os.replace("a", "b")\n'
            '    return 1 if os.path.exists("b") else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n', writers=True)
        self.assertTrue(c.admitted, c.reason)

    def test_a_solver_launch_is_never_admitted(self):
        """Compute authorisation is Katie's; a scheduled runner must not spend it."""
        c = self._classify(
            'import subprocess, sys\n'
            'def main():\n'
            '    p = subprocess.run(["simpleFoam", "-case", "x"])\n'
            '    return 1 if p.returncode else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertFalse(c.admitted)
        self.assertIn("needs-compute", c.reason)

    def test_a_required_positional_is_not_schedulable(self):
        c = self._classify(
            'import argparse, sys\n'
            'def main():\n'
            '    p = argparse.ArgumentParser()\n'
            '    p.add_argument("case")\n'
            '    a = p.parse_args()\n'
            '    return 1 if a.case else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertFalse(c.admitted)
        self.assertIn("requires-arguments", c.reason)


class ExitCodeReading(unittest.TestCase):
    def _run_one(self, body: str):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "c.py").write_text(body)
            cand = lc.Candidate(path="scripts/c.py", frames=("worktree",))
            return lc.run_script(root, cand, timeout=60)

    def test_a_usage_error_is_UNKNOWN_not_FAIL(self):
        """`sweep.py` has no default frame on purpose. That is not a finding."""
        out = self._run_one(
            'import argparse, sys\n'
            'p = argparse.ArgumentParser()\n'
            'p.add_argument("pattern")\n'
            'p.parse_args()\n')
        self.assertEqual(out.verdict, lc.UNKNOWN, out.reason)
        self.assertIn("exited 2 on invocation", out.reason)

    def test_a_check_that_printed_nothing_and_exited_2_is_UNKNOWN(self):
        """`sweep.py`'s shape: its own sentence, not argparse's `usage:`."""
        out = self._run_one(
            'import sys\n'
            'print("sweep: both a pattern and --frame are required",\n'
            '      file=sys.stderr)\n'
            'sys.exit(2)\n')
        self.assertEqual(out.verdict, lc.UNKNOWN, out.reason)

    def test_exit_2_WITH_a_report_on_stdout_is_still_a_FAIL(self):
        """The must-not-match half: a check that reported and then failed."""
        out = self._run_one(
            'import sys\n'
            'print("VERDICT: FAIL -- 3 rows do not re-derive")\n'
            'sys.exit(2)\n')
        self.assertEqual(out.verdict, lc.FAIL, out.reason)

    def test_a_traceback_is_UNKNOWN_not_FAIL(self):
        out = self._run_one('raise RuntimeError("the check itself is broken")\n')
        self.assertEqual(out.verdict, lc.UNKNOWN, out.reason)
        self.assertIn("crashed", out.reason)

    def test_exit_three_is_the_checks_own_UNKNOWN(self):
        out = self._run_one('import sys\nsys.exit(3)\n')
        self.assertEqual(out.verdict, lc.UNKNOWN)

    def test_stderr_is_reported_and_never_discarded(self):
        out = self._run_one(
            'import sys\nprint("a problem", file=sys.stderr)\nsys.exit(0)\n')
        self.assertEqual(out.stderr_lines, 1)
        self.assertIn("a problem", out.stderr_tail)


if __name__ == "__main__":
    unittest.main()
