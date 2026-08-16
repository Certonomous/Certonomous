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

THE EXIT CODES ARE TYPED OUT IN THIS FILE, AS NUMBERS (V15 round 7 F0, D101)
----------------------------------------------------------------------------
Every whole-runner assertion here used to read `assertEqual(rc, lc.EXIT[lc.FAIL])`
-- the subprocess's exit code compared against the module-under-test's OWN
dictionary. Both sides move together, so mutating

    EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}  ->  EXIT = {PASS: 0, FAIL: 77, UNKNOWN: 99}

left 25 of 25 tests green, while `scripts/installed/pre-push`, which reads the
numbers directly, fell through to its out-of-contract arm on every FAIL. The
literals below are the contract. A test that asks the thing under test what the
right answer is has not tested it.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / "scripts" / "lab_check.py"
HOOK = REPO / "scripts" / "installed" / "pre-push"

#: THE PUBLISHED EXIT-CODE CONTRACT, as numbers, typed here and imported from
#: nowhere. `lab_check.py` and `scripts/installed/pre-push` are the two files
#: that have to agree about them; this is the third place, and it is the only
#: one that is not free to change its mind.
RC_PASS = 0
RC_FAIL = 1
RC_UNKNOWN_REACH = 3
RC_UNKNOWN_OUTPUT = 4

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
        self.assertEqual(rc, RC_FAIL, out)
        self.assertIn("VERDICT: FAIL", out)
        self.assertIn("scripts/gate.py", out)

    def test_a_failing_test_file_turns_the_aggregate_red(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), tests="2")
            rc, out = _run(root)
        self.assertEqual(rc, RC_FAIL, out)
        self.assertIn("test_planted.py", out)


class TheRunnerIsSilentWhereItShouldBe(unittest.TestCase):
    """The half that L-84 says is the one usually missing."""

    def test_the_same_tree_without_the_defect_comes_back_PASS(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), gate_findings="[]")
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_PASS, out)
        self.assertIn("VERDICT: PASS", out)

    def test_a_passing_gate_and_a_passing_suite_together_are_PASS(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), gate_findings="[]", tests="1")
            rc, out = _run(root)
        self.assertEqual(rc, RC_PASS, out)


class AnEmptyCheckSetIsNeverAPass(unittest.TestCase):
    """Defect class B1: the sweep that examined nothing and reported clean.

    Both cases here now assert exit 4 rather than exit 3, and the change is not
    cosmetic: 3 is the code `scripts/installed/pre-push` deliberately does NOT
    block on. A run that admitted no check at all reaching a hook as "warn and
    push" is B1 with a schedule attached, so an empty admitted set is UNKNOWN
    ABOUT WHAT THE CHECKS WOULD HAVE SAID, which blocks.
    """

    def test_no_checks_at_all_is_UNKNOWN_and_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp))
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_UNKNOWN_OUTPUT, out)
        self.assertIn("VERDICT: UNKNOWN", out)
        self.assertIn("no check was admitted", out)

    def test_a_tree_of_printers_is_UNKNOWN_not_PASS(self):
        """D64's own criterion: a main() that returns 0 unconditionally cannot fail."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), printer=True)
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_UNKNOWN_OUTPUT, out)
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
        self.assertEqual(rc, RC_FAIL, out)
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
        self.assertEqual(rc, RC_UNKNOWN_REACH, out)
        self.assertIn("none of them declares a test", out)

    def test_without_the_plant_the_same_tree_is_PASS(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), tests="1")
            rc, out = _run(root)
        self.assertEqual(rc, RC_PASS, out)

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
        self.assertTrue(out.blocking, "a crash the runner cannot read a verdict "
                                      "out of must not be a free pass")

    def test_exit_three_is_the_checks_own_UNKNOWN(self):
        out = self._run_one('import sys\nsys.exit(3)\n')
        self.assertEqual(out.verdict, lc.UNKNOWN)
        self.assertTrue(out.blocking)

    def test_a_PASS_is_the_only_non_blocking_outcome_a_check_can_earn(self):
        """The must-not-match half of `blocking`: it is not on by default."""
        out = self._run_one(
            'import sys\nprint("VERDICT: PASS")\nsys.exit(0)\n')
        self.assertEqual(out.verdict, lc.PASS, out.reason)
        self.assertFalse(out.blocking, out.reason)

    def test_stderr_is_reported_and_never_discarded(self):
        out = self._run_one(
            'import sys\nprint("a problem", file=sys.stderr)\nsys.exit(0)\n')
        self.assertEqual(out.stderr_lines, 1)
        self.assertIn("a problem", out.stderr_tail)


# ---------------------------------------------------------------------------
# V15 round 7, F0 / docket D101. The graded party controlled the predicate that
# decided whether it had been graded.
# ---------------------------------------------------------------------------

#: The demonstration gate from the round document, both halves. The ONLY
#: difference between them is one line written to the check's own stderr; the
#: finding, the stdout report and the exit code are identical.
GATE_REPORTS_AND_FAILS = '''\
#!/usr/bin/env python3
"""A gate whose exit code is a function of its finding."""
import sys


def main():
    print("VERDICT: FAIL -- the corpus is bad")
{extra}    return 1


if __name__ == "__main__":
    sys.exit(main())
'''

#: The other half of the escape: a gate that hides its finding entirely and
#: shows the runner only a traceback line. It gets UNKNOWN -- which is the
#: honest reading -- and it gets a BLOCKING exit code, which is what makes the
#: escape worthless rather than merely narrower.
GATE_HIDES_ITS_FINDING = '''\
#!/usr/bin/env python3
"""A gate that found something and would rather not be counted."""
import sys


def main():
    sys.stderr.write("Traceback (most recent call last)\\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
'''

_TRACEBACK_LINE = ('    sys.stderr.write("Traceback (most recent call last)'
                   '\\n")\n')


class AGradedCheckCannotBuyABetterOutcomeByPrinting(unittest.TestCase):
    """F0, reproduced as a regression pair and then closed.

    Reproduced in a scratch repository before the repair: one gate, the same
    finding, the same exit code 1, run twice.

        plain                    FAIL      runner exit 1    push blocked
        + one stderr line      UNKNOWN     runner exit 3    push ALLOWED

    The finding was still on stdout in the second run; the runner read it,
    printed it, and did not act on it. This is one level worse than docket D78
    (a detector that switches itself off), because the GRADED PARTY controls the
    predicate deciding whether it was graded -- and a check that crashes is
    exactly the check most likely to be hiding something.

    Two locks, one test each, plus the must-not-match half for both.
    """

    def _run_gate(self, source: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            (root / "scripts").mkdir(parents=True)
            (root / "sdk" / "tests").mkdir(parents=True)
            (root / "scripts" / "gate.py").write_text(source)
            (root / "README").write_text("fixture tree\n")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                            "commit", "-qm", "fixture"], cwd=root, check=True)
            return _run(root, "--no-tests")

    def test_LOCK_1_a_traceback_does_not_unsay_a_finding_already_reported(self):
        rc, out = self._run_gate(
            GATE_REPORTS_AND_FAILS.format(extra=_TRACEBACK_LINE))
        self.assertEqual(
            rc, RC_FAIL,
            "one line on the check's OWN stderr erased its own reported FAIL. "
            "This is docket D101 back:\n" + out)
        self.assertIn("VERDICT: FAIL", out)

    def test_LOCK_1_control_the_same_gate_without_the_stderr_line(self):
        """The must-not-match half. If this and the case above did not agree,
        the assertion above would be proving nothing about the stderr line."""
        rc, out = self._run_gate(GATE_REPORTS_AND_FAILS.format(extra=""))
        self.assertEqual(rc, RC_FAIL, out)
        self.assertIn("VERDICT: FAIL", out)

    def test_LOCK_2_hiding_the_finding_behind_a_crash_still_blocks(self):
        """The escape that is still REACHABLE, shown to be worth nothing.

        A check can still reach UNKNOWN -- by suppressing its own finding
        entirely, which is the only way left. What it cannot do is reach a
        non-blocking exit code, and `RC_UNKNOWN_REACH` (3) is the one
        `scripts/installed/pre-push` does not block on. So the whole trade is a
        blocking code for a blocking code, at the price of deleting the
        evidence: no monotone improvement is available.
        """
        rc, out = self._run_gate(GATE_HIDES_ITS_FINDING)
        self.assertEqual(
            rc, RC_UNKNOWN_OUTPUT,
            "a check that crashed instead of reporting reached a code the "
            "pre-push hook waves through:\n" + out)
        self.assertNotEqual(rc, RC_UNKNOWN_REACH, out)
        self.assertNotEqual(rc, RC_PASS, out)
        self.assertIn("VERDICT: UNKNOWN", out)

    def test_LOCK_2_control_a_clean_tree_is_still_a_non_blocking_PASS(self):
        """L-84's other half: the repair must not make everything block.

        A gate that ran, reported and passed comes back 0. If this reddens, the
        two locks above have been implemented as an alarm rather than a gate,
        and an alarm gets switched off inside a day.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), gate_findings="[]")
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_PASS, out)
        self.assertIn("exit 0 -- clean", out)


class TheExitCodeContractIsPinned(unittest.TestCase):
    """The `{0, 77, 99}` mutation that left 25 of 25 tests green (F0, D101).

    `EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}` was mutated to
    `{PASS: 0, FAIL: 77, UNKNOWN: 99}` in a scratch copy of the runner and its
    suite, `__pycache__` purged before both: control and mutant alike returned
    `25 passed`. Nothing pinned the numbers, and `scripts/installed/pre-push`
    hardcodes them -- so under that mutation every FAIL fell into the hook's
    out-of-contract arm, which at the time printed "Not blocking; nothing was
    checked" and returned 0.

    Two independent pins, so the mutation reddens twice:
      * the numbers, asserted as literals typed in THIS file;
      * the hook, RUN against a stub runner for each code the runner publishes.
        That second one is the anti-drift pin: renumber the runner and the
        hook's own arms stop covering it, whatever the literals say.
    """

    STUB = 'import sys\nprint("stub runner")\nsys.exit({code})\n'

    def _run_hook(self, runner_exit: int | None, *, skip: str = "0"
                  ) -> tuple[int, str]:
        """Run the REAL hook against a stub runner. `None` omits the runner."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            (root / "scripts" / "installed").mkdir(parents=True)
            if runner_exit is not None:
                (root / "scripts" / "lab_check.py").write_text(
                    self.STUB.format(code=runner_exit))
            hook = root / "scripts" / "installed" / "pre-push"
            shutil.copy(HOOK, hook)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            proc = subprocess.run(
                ["bash", str(hook)], cwd=root, capture_output=True, text=True,
                timeout=120, stdin=subprocess.DEVNULL,
                env={**os.environ, "LAB_CHECK_SKIP": skip})
        return proc.returncode, proc.stdout + proc.stderr

    def test_the_published_codes_are_exactly_these_numbers(self):
        self.assertEqual(lc.EXIT_PASS, RC_PASS)
        self.assertEqual(lc.EXIT_FAIL, RC_FAIL)
        self.assertEqual(lc.EXIT_UNKNOWN, RC_UNKNOWN_REACH)
        self.assertEqual(lc.EXIT_UNSOUND, RC_UNKNOWN_OUTPUT)

    def test_exit_code_maps_every_verdict_and_blocking_pair(self):
        self.assertEqual(lc.exit_code(lc.PASS, False), RC_PASS)
        self.assertEqual(lc.exit_code(lc.FAIL, True), RC_FAIL)
        self.assertEqual(lc.exit_code(lc.UNKNOWN, False), RC_UNKNOWN_REACH)
        self.assertEqual(lc.exit_code(lc.UNKNOWN, True), RC_UNKNOWN_OUTPUT)

    def test_the_hook_blocks_on_FAIL(self):
        rc, out = self._run_hook(RC_FAIL)
        self.assertNotEqual(rc, 0, out)

    def test_the_hook_does_not_block_on_PASS(self):
        rc, out = self._run_hook(RC_PASS)
        self.assertEqual(rc, 0, out)

    def test_the_hook_warns_and_does_not_block_on_UNKNOWN_about_reach(self):
        """The must-not-match half at the hook level. A hook that blocks on the
        permanent state of this repository is a hook that gets deleted, and a
        deleted hook checks nothing."""
        rc, out = self._run_hook(RC_UNKNOWN_REACH)
        self.assertEqual(rc, 0, out)
        self.assertIn("REACH", out)

    def test_the_hook_blocks_on_UNKNOWN_about_a_checks_output(self):
        rc, out = self._run_hook(RC_UNKNOWN_OUTPUT)
        self.assertNotEqual(
            rc, 0,
            "a check that could not report reached the hook and was waved "
            "through. That is docket D101's second half:\n" + out)

    def test_the_hook_blocks_on_every_code_outside_the_contract(self):
        """Including 77 and 99 -- the mutation's own codes -- and 2."""
        for code in (2, 5, 77, 99, 127):
            with self.subTest(code=code):
                rc, out = self._run_hook(code)
                self.assertNotEqual(
                    rc, 0,
                    f"the runner exited {code}, nothing was checked, and the "
                    f"hook allowed the push:\n{out}")

    def test_the_hook_blocks_when_the_runner_is_missing_entirely(self):
        rc, out = self._run_hook(None)
        self.assertNotEqual(rc, 0, out)
        self.assertIn("NOTHING WAS CHECKED", out)

    def test_every_code_the_runner_publishes_has_its_own_arm_in_the_hook(self):
        """THE ANTI-DRIFT PIN, and the one that survives a rename.

        Renumber `lab_check.py`'s constants and these codes stop matching the
        hook's `case` arms, so each falls into `*` -- which now blocks, but
        which also names itself in the output. This reddens on any renumbering
        even if someone updates the literals at the top of this file to match.
        """
        for code in (lc.EXIT_PASS, lc.EXIT_FAIL, lc.EXIT_UNKNOWN,
                     lc.EXIT_UNSOUND):
            with self.subTest(code=code):
                rc, out = self._run_hook(code)
                self.assertNotIn(
                    "outside its own contract", out,
                    f"the runner publishes exit code {code} and the hook has "
                    f"no arm for it, so it is being handled as an unknown "
                    f"code:\n{out}")

    def test_the_stated_escape_hatch_still_works(self):
        """LAB_CHECK_SKIP=1 is the answer to every blocked push, and it has to
        keep working or the blocking arms above become a reason to uninstall."""
        rc, out = self._run_hook(RC_FAIL, skip="1")
        self.assertEqual(rc, 0, out)
        self.assertIn("SKIPPED", out)


# ---------------------------------------------------------------------------
# D148 -- an interrupted run keeps what it learned, and says it was interrupted
# ---------------------------------------------------------------------------

#: THE MARKERS, TYPED HERE AS LITERALS, imported from nowhere -- the same
#: discipline as the exit codes above and for the same reason. A test that asks
#: `lc.MARK_END` what the terminator is would stay green under a mutation that
#: renamed it, while every log already on disk and every reader's `grep` broke.
MARK_BEGIN = "LAB-CHECK-BEGIN"
MARK_PLAN = "LAB-CHECK-PLAN"
MARK_END = "LAB-CHECK-END"
END_COMPLETE = "LAB-CHECK-END COMPLETE"
END_INCOMPLETE = "LAB-CHECK-END INCOMPLETE"


def _terminator(text: str) -> str:
    """The terminator LINE, at column 0, or "" if the log carries none.

    Every assertion below goes through this rather than through `assertIn`
    over the whole log, and the reason is a real near-miss in writing these
    tests: the run's own preamble says "COMPLETE only if it ends with a
    `LAB-CHECK-END COMPLETE` line", so a substring search over the log matches
    that sentence. `assertIn(END_COMPLETE, out)` would have been green on a
    runner that emitted no terminator at all, and `assertNotIn(END_COMPLETE,
    partial)` red on a correctly interrupted one. The marker is specified at
    column 0; the test reads it at column 0.
    """
    ends = [l for l in text.splitlines() if l.startswith(MARK_END)]
    return ends[-1] if ends else ""

#: A gate that takes long enough to be killed while it is running. It is a PASS
#: gate: nothing in the mid-flight kill case depends on a finding, so a reader
#: grepping the killed log for faults finds none -- which is the exact state
#: D148 says must be distinguishable from a clean run.
#: It is a real gate -- `return 1 if FINDINGS else 0` -- and not a `return 0`,
#: or the runner's own `cannot-fail` predicate would refuse to admit it and the
#: fixture would silently have one check in it instead of two.
SLOW_GATE = '''\
#!/usr/bin/env python3
"""A gate that is still running when the kill arrives."""
import sys, time

FINDINGS = []


def main():
    time.sleep({seconds})
    print(f"VERDICT: {{'FAIL' if FINDINGS else 'PASS'}}")
    return 1 if FINDINGS else 0


if __name__ == "__main__":
    sys.exit(main())
'''


class AnInterruptedRunSaysSo(unittest.TestCase):
    """Docket D148. Both L-84 halves, and the positive one is the whole point.

    THE ARTIFACT, measured on the live tree before the repair:

        timeout 45 python3 scripts/lab_check.py --no-tests
          -> exit 124, stdout 0 bytes, stderr 0 bytes

    The runner built its whole report in a list and printed it in one write at
    the end, so an interrupted run destroyed everything it had already learned
    AND -- the part that ranks -- produced an artifact indistinguishable from a
    clean one. A nightly cron that hits its window appends nothing to the log,
    and nothing is what a clean run looks like to anyone who greps it for
    faults. Defect class B1, the silent-zero, in the instrument that reports
    every other check's verdict.

    The must-not-match half is `test_a_complete_clean_run_is_not_marked_
    incomplete` and it is not a formality: a runner that marked every run
    INCOMPLETE would pass every positive case here and be worthless.
    """

    #: Long enough that the kill lands inside it on a loaded box, short enough
    #: that the test does not hang if the kill misses.
    SLOW_SECONDS = 45

    def _slow_repo(self, tmp: Path) -> Path:
        """A fast PASS gate, then a slow one. Scripts run in sorted path order,
        so `gate_a` is guaranteed to have finished and `gate_b_slow` to be in
        flight at the moment of the kill."""
        root = tmp / "repo"
        (root / "scripts").mkdir(parents=True)
        (root / "sdk" / "tests").mkdir(parents=True)
        (root / "scripts" / "gate_a.py").write_text(GATE.format(findings="[]"))
        (root / "scripts" / "gate_b_slow.py").write_text(
            SLOW_GATE.format(seconds=self.SLOW_SECONDS))
        (root / "README").write_text("fixture tree\n")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "fixture"], cwd=root, check=True)
        return root

    def _kill_mid_flight(self, root: Path, log: Path, sig: int) -> tuple[int, str]:
        """Start a run, wait until it is demonstrably inside the slow gate, and
        signal it. Returns (exit code, everything the run wrote).

        The wait is on the LOG, not on a sleep: the test asserts the runner had
        streamed the first gate's result before the kill, which is the property
        under test. Polling a clock instead would make this pass on a runner
        that buffered everything and happened to be lucky.
        """
        with log.open("wb") as fh:
            proc = subprocess.Popen(
                [sys.executable, str(RUNNER), "--root", str(root),
                 "--no-tests"], stdout=fh, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                text = log.read_text(errors="replace")
                if "gate_b_slow.py ..." in text and "gate_a.py" in text:
                    break
                if proc.poll() is not None:
                    break
                time.sleep(0.2)
            else:
                proc.kill()
                self.fail("the runner never reached the slow gate")
            proc.send_signal(sig)
            rc = proc.wait(timeout=60)
        return rc, log.read_text(errors="replace")

    # -- the positive half -------------------------------------------------

    def test_a_run_killed_mid_flight_keeps_everything_up_to_the_kill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._slow_repo(Path(tmp))
            log = Path(tmp) / "run.log"
            rc, out = self._kill_mid_flight(root, log, signal.SIGTERM)

        # (a) NON-EMPTY. The whole defect in one assertion.
        self.assertTrue(out.strip(), "a killed run wrote nothing at all")
        # (b) EVERYTHING UP TO THE KILL. The gate that finished is reported
        #     with its verdict, and the frame that names what was looked at is
        #     above it.
        self.assertIn("FRAME", out)
        self.assertIn("SKIPPED, BY REASON", out)
        self.assertIn("scripts/gate_a.py", out)
        self.assertIn("[PASS", out)
        # (c) UNMISTAKABLY INCOMPLETE, said rather than implied.
        self.assertTrue(_terminator(out).startswith(END_INCOMPLETE),
                        f"terminator was {_terminator(out)!r}\n{out}")
        self.assertIn("THIS RUN DID NOT FINISH", out)
        # and it names what it was inside when it died, and how far it got
        # against a denominator fixed before the first check started.
        self.assertIn("scripts/gate_b_slow.py", out)
        self.assertIn("ran=1/2", out)

    def test_the_frame_and_the_plan_are_written_before_any_check_runs(self):
        """Truncation takes the END of a log. Anything that must survive it has
        to be at the START -- which is why the coverage statement and the
        denominator are emitted before the first check is launched."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._slow_repo(Path(tmp))
            log = Path(tmp) / "run.log"
            rc, out = self._kill_mid_flight(root, log, signal.SIGTERM)
        self.assertIn(MARK_BEGIN, out)
        self.assertIn(f"{MARK_PLAN} expected=2", out)
        self.assertIn("candidates", out)
        # the plan names them, so a reader of a truncated log knows which
        # checks this run never reached
        self.assertIn("will run  scripts/gate_b_slow.py", out)

    def test_a_reader_grepping_for_faults_can_tell_partial_from_clean(self):
        """THE REQUIREMENT, stated as the test that decides it.

        Both logs below contain no fault. One is a clean run and one died at
        check 2 of 2. Before D148 the second was zero bytes and the two were
        the same artifact; a reader could not tell them apart, and a nightly
        cron would have shown "no faults" every night it timed out.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = self._slow_repo(Path(tmp))
            log = Path(tmp) / "run.log"
            _, partial = self._kill_mid_flight(root, log, signal.SIGTERM)
            clean_root = _repo(Path(tmp) / "clean", gate_findings="[]")
            _, clean = _run(clean_root, "--no-tests")

        # the premise: neither log reports a fault
        for name, text in (("partial", partial), ("clean", clean)):
            with self.subTest(log=name):
                self.assertNotIn("VERDICT: FAIL", text)
                self.assertNotIn("[FAIL", text)
        # and yet they are distinguishable, by one greppable line each
        self.assertTrue(_terminator(clean).startswith(END_COMPLETE),
                        f"clean run terminator: {_terminator(clean)!r}")
        self.assertTrue(_terminator(partial).startswith(END_INCOMPLETE),
                        f"partial run terminator: {_terminator(partial)!r}")

    def test_sigint_from_a_person_is_reported_the_same_way(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._slow_repo(Path(tmp))
            log = Path(tmp) / "run.log"
            rc, out = self._kill_mid_flight(root, log, signal.SIGINT)
        self.assertTrue(_terminator(out).startswith(END_INCOMPLETE), out)
        self.assertIn("cause=SIGINT", _terminator(out))
        self.assertIn("scripts/gate_a.py", out)
        # and no bare Python traceback in place of a report
        self.assertNotIn("KeyboardInterrupt\n", out)

    def test_a_direct_signal_exits_blocking_and_inside_the_contract(self):
        """What the runner CAN control. `timeout` is the case where it cannot
        -- see the test below -- but a supervisor that signals the runner
        itself gets 4: UNKNOWN about the output of the checks that never ran,
        which is the code `scripts/installed/pre-push` already blocks on. Not a
        new code, not a weakening of the contract, and not 1: an interrupted
        run has NOT found a fault, and reporting it as FAIL would be a claim
        about the lab that this run is in no position to make.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = self._slow_repo(Path(tmp))
            log = Path(tmp) / "run.log"
            rc, out = self._kill_mid_flight(root, log, signal.SIGTERM)
        self.assertEqual(rc, RC_UNKNOWN_OUTPUT, out)

    def test_under_timeout_the_exit_code_is_124_and_the_LOG_carries_the_truth(self):
        """D148's own reproduction, run forward.

        `timeout` reports 124 whenever it had to kill, WHATEVER the child then
        chose -- measured, not assumed. So on the path that produced the
        artifact the exit code is not the runner's to set, and any repair that
        leaned on it would be broken at exactly that point. The log is the
        channel the runner controls all the way through, and this is the test
        that says so.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = self._slow_repo(Path(tmp))
            proc = subprocess.run(
                ["timeout", "8", sys.executable, str(RUNNER), "--root",
                 str(root), "--no-tests"],
                capture_output=True, text=True, timeout=120)
        out = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 124,
                         "expected timeout's own code, not the runner's")
        self.assertTrue(out.strip(),
                        "THE D148 ARTIFACT: exit 124 with a zero-byte report")
        self.assertTrue(_terminator(out).startswith(END_INCOMPLETE), out)
        self.assertIn("the shell sees 124", out)

    def test_an_unhandled_exception_inside_the_runner_is_UNKNOWN_not_FAIL(self):
        """The third interrupt path.

        A crash inside a CHECK is a subprocess and was already handled (it is
        UNKNOWN and blocking; see `test_a_traceback_is_UNKNOWN_not_FAIL`). A
        crash inside the RUNNER was not: Python exits 1 on an unhandled
        exception, 1 is EXIT_FAIL, and the hook printed "a check that ran
        returned a finding" over a runner that had never got that far -- while
        every line it had already produced went with it.

        Patched on the imported module OBJECT, never on the file: the tracked
        worktree is not mutated by this suite.
        """
        def boom(*a, **kw):
            raise RuntimeError("the instrument broke, not the lab")

        buf = io.StringIO()
        original = lc.run_script
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), gate_findings="[]")
            lc.run_script = boom
            try:
                with contextlib.redirect_stdout(buf):
                    rc = lc.main(["--root", str(root), "--no-tests"])
            finally:
                lc.run_script = original
        out = buf.getvalue()
        self.assertEqual(rc, RC_UNKNOWN_OUTPUT, out)
        self.assertNotEqual(rc, RC_FAIL, "a broken runner is not a finding")
        self.assertTrue(_terminator(out).startswith(END_INCOMPLETE), out)
        self.assertIn("RUNNER TRACEBACK", out)
        self.assertIn("the instrument broke, not the lab", out)

    def test_results_are_flushed_as_they_are_produced_not_at_the_end(self):
        """The streaming pin proper, and the one the terminator rests on.

        Read the log WHILE the run is still in flight. `stdout` redirected to a
        file is block buffered, so a report that is merely `print`ed line by
        line still loses its last several KB to a kill; only an explicit flush
        at each line makes the bytes real. This asserts the first gate's
        verdict is on disk while the second gate is still running.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = self._slow_repo(Path(tmp))
            log = Path(tmp) / "run.log"
            with log.open("wb") as fh:
                proc = subprocess.Popen(
                    [sys.executable, str(RUNNER), "--root", str(root),
                     "--no-tests"], stdout=fh, stderr=subprocess.STDOUT)
                mid = ""
                deadline = time.monotonic() + 60
                while time.monotonic() < deadline:
                    mid = log.read_text(errors="replace")
                    if "[PASS" in mid and "gate_a.py" in mid:
                        break
                    if proc.poll() is not None:
                        break
                    time.sleep(0.2)
                still_running = proc.poll() is None
                proc.kill()
                proc.wait(timeout=30)
        self.assertTrue(still_running,
                        "the run finished before the assertion could be made")
        self.assertIn("scripts/gate_a.py", mid)
        self.assertIn("[PASS", mid)
        self.assertEqual(_terminator(mid), "",
                         "the run had already terminated; nothing was proved")

    # -- the must-not-match half -------------------------------------------

    def test_a_complete_clean_run_is_not_marked_incomplete(self):
        """L-84's other half. A runner that marked every run INCOMPLETE would
        pass every positive case above and be worth nothing."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), gate_findings="[]")
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_PASS, out)
        self.assertTrue(_terminator(out).startswith(END_COMPLETE),
                        f"terminator was {_terminator(out)!r}\n{out}")
        self.assertIn("ran=1/1", _terminator(out))
        self.assertNotIn("THIS RUN DID NOT FINISH", out)

    def test_a_complete_run_keeps_the_shape_its_consumers_already_parse(self):
        """The consumers are `scripts/installed/pre-push` (exit code only),
        the cron line (appends the stream to a log), and this file (substrings
        on stdout). Streaming must not have moved any of them."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), gate_findings="['a defect']")
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_FAIL, out)
        for expected in ("LAB CHECK -- one entry point", "FRAME",
                         "SKIPPED, BY REASON", "CHECKS RUN", "VERDICT: FAIL",
                         "check(s) ran", "scripts/gate.py"):
            with self.subTest(expected=expected):
                self.assertIn(expected, out)
        # the verdict block is still the last thing before the terminator, so
        # a reader who tails the log sees the verdict without scrolling
        tail = [l for l in out.splitlines() if l.strip()][-2:]
        self.assertTrue(tail[0].startswith("="), tail)
        self.assertTrue(tail[1].startswith(END_COMPLETE), tail)

    def test_the_terminator_reports_the_verdict_and_the_exit_code(self):
        """A log reader must not have to parse prose to get the verdict. Each
        case is checked in both directions: the code on the terminator is the
        code the process actually returned."""
        cases = [("[]", RC_PASS, "PASS"), ("['x']", RC_FAIL, "FAIL")]
        for findings, want_rc, want_verdict in cases:
            with self.subTest(findings=findings):
                with tempfile.TemporaryDirectory() as tmp:
                    root = _repo(Path(tmp), gate_findings=findings)
                    rc, out = _run(root, "--no-tests")
                self.assertEqual(rc, want_rc, out)
                self.assertTrue(
                    _terminator(out).startswith(
                        f"{END_COMPLETE} verdict={want_verdict} "
                        f"exit={want_rc} "),
                    f"terminator was {_terminator(out)!r}")

    def test_json_mode_still_emits_one_parseable_document_on_stdout(self):
        """`--json` streams its narration to stderr precisely so that stdout
        stays one object. A partial run gets a partial document flagged
        `complete: false` rather than a truncated one."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(Path(tmp), gate_findings="[]")
            proc = subprocess.run(
                [sys.executable, str(RUNNER), "--root", str(root),
                 "--no-tests", "--json"], capture_output=True, text=True,
                timeout=600)
        doc = json.loads(proc.stdout)
        self.assertEqual(doc["verdict"], "PASS")
        self.assertIs(doc["complete"], True)
        self.assertTrue(_terminator(proc.stderr).startswith(END_COMPLETE),
                        proc.stderr)
        self.assertNotIn(MARK_BEGIN, proc.stdout)


# ---------------------------------------------------------------------------
# THE GUARD SURVIVORS, measured rather than guessed (docket D217's census)
# ===========================================================================
# Everything above this line was written from the defect that motivated it.
# Everything below it was written from a MEASUREMENT: 94 single-edit mutants of
# `scripts/lab_check.py`, each run against this file in an isolated `git
# worktree` of HEAD with `__pycache__` purged before every cell, judged by the
# CHANGE IN FAILURE COUNT against a control asserted green at 52 passed / 20
# subtests / rc 0 -- never by a non-zero exit code, which reports every mutant
# killed the moment the control is red (D211/D217).
#
# The mutants that SURVIVED are the guards this runner was carrying without
# cover, and each test below names the one it kills. Three rules were applied
# to writing them, each from a documented near-miss in this lab:
#
#   * DRIVE THE RUNNER, do not read it. Where a guard is reachable through the
#     shipped entry point, the test runs it and asserts on what came out.
#   * ASSERT AN IDENTITY, never a count -- WHICH check, WHICH verdict, WHICH
#     message. A probe that counted survived an inverted comparison here once.
#   * NEVER ASSERT TEXT THE HARNESS COULD HAVE PRODUCED FOR ANOTHER REASON.
#     The run's own preamble quotes its markers, so marker assertions below go
#     through a shape that only the real emission has (`_started_lines`), the
#     same discipline `_terminator` already applies to the END marker.
# ---------------------------------------------------------------------------

#: A check whose argv head is a solver binary. It is NEVER EXECUTED by anything
#: here -- the predicate that skips it is static, read out of this source by
#: `ast`, and the whole point of the test is that the runner refuses to launch
#: it. Compute authorisation is Katie's.
NEEDS_COMPUTE_GATE = '''\
#!/usr/bin/env python3
"""A check that cannot answer without spending core-minutes."""
import subprocess
import sys


def main():
    p = subprocess.run(["simpleFoam", "-case", "."])
    return 1 if p.returncode else 0


if __name__ == "__main__":
    sys.exit(main())
'''

#: Write-CAPABLE when read statically; it writes nothing on the path this
#: runner takes, because the runner passes no arguments. This separates "was it
#: ADMITTED" from "did it WRITE", which are two different guards.
WRITER_THAT_DOES_NOT_WRITE = '''\
#!/usr/bin/env python3
"""Statically write-capable; on this runner's path it writes nothing."""
import sys

FINDINGS = []


def main():
    if len(sys.argv) > 3:                 # never true: the runner passes none
        open("would_have_written.txt", "w").write("x")
    print(f"VERDICT: {'FAIL' if FINDINGS else 'PASS'}")
    return 1 if FINDINGS else 0


if __name__ == "__main__":
    sys.exit(main())
'''

#: `withdrawal_sweep.py`'s honest shape: it plants its own control in the tree
#: it is being graded in. That plant is not a defect, it is the apparatus -- and
#: the runner has to SEE it, because an exit code that grades a write the runner
#: caused is not a finding about the lab.
WRITER_THAT_WRITES = '''\
#!/usr/bin/env python3
"""A check that plants its own L-84 control in the tree."""
import sys

FINDINGS = []


def main():
    open("planted_control.txt", "w").write("L-84 control\\n")
    print(f"VERDICT: {'FAIL' if FINDINGS else 'PASS'}")
    return 1 if FINDINGS else 0


if __name__ == "__main__":
    sys.exit(main())
'''

#: Passes, and says something on stderr on the way. `NO 2>/dev/null, ANYWHERE`
#: is a stated rule of this module; a silent stderr is the claim that there was
#: nothing on it.
GATE_WITH_STDERR = '''\
#!/usr/bin/env python3
"""A gate that passes and still has something to say on stderr."""
import sys

FINDINGS = []


def main():
    print(f"VERDICT: {'FAIL' if FINDINGS else 'PASS'}")
    print("the board referent could not be read, so one guard graded nothing",
          file=sys.stderr)
    return 1 if FINDINGS else 0


if __name__ == "__main__":
    sys.exit(main())
'''

#: More sub-results than the report shows. Silent truncation is the class this
#: module exists to close, so the report has to say it truncated.
NOISY_GATE = '''\
#!/usr/bin/env python3
"""A gate with more sub-results than one block will show."""
import sys


def main():
    for i in range(30):
        print(f"[FAIL] sub-result {i:02d} did not re-derive")
    return 1


if __name__ == "__main__":
    sys.exit(main())
'''

#: A test file that ERRORS rather than FAILS. The two are on opposite sides of
#: this runner's control boundary: a failure is a statement about the lab, an
#: error is a statement about the instrument.
ERRORING_TEST_FILE = '''\
import pytest


@pytest.fixture
def broken_fixture():
    raise RuntimeError("the fixture is broken, not the lab")


def test_it(broken_fixture):
    assert True
'''

#: A helper that happens to be named `test_*`. pytest collects nothing from it
#: and exits 5.
HELPER_DECLARING_NO_TEST = '''\
"""A helper that happens to be named test_something.py. It declares no test."""

CONSTANT = 3
'''

#: Forces pytest to report success while having collected nothing -- the exact
#: state `run_pytest`'s `elif total == 0` arm exists for, and one this
#: repository could reach for real the day anybody adds a `conftest.py` that
#: normalises pytest's exit 5 away.
CONFTEST_FORCES_EXIT_ZERO = '''\
def pytest_sessionfinish(session, exitstatus):
    session.exitstatus = 0
'''


def _tree(tmp: Path, files: dict, *, git: bool = True) -> Path:
    """A throwaway tree holding exactly `files`, optionally a git repository."""
    root = tmp / "repo"
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "sdk" / "tests").mkdir(parents=True, exist_ok=True)
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    (root / "README").write_text("fixture tree\n")
    if git:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "fixture"], cwd=root, check=True)
    return root


def _run_one_script(body: str, **kw):
    """`run_script` over one throwaway check. Returns its `Outcome`."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "scripts").mkdir()
        (root / "scripts" / "c.py").write_text(body)
        cand = lc.Candidate(path="scripts/c.py", frames=("worktree",))
        return lc.run_script(root, cand, timeout=kw.pop("timeout", 60), **kw)


#: The in-flight marker is specified at column 0 (after the block's indent) and
#: FOLLOWED BY A POSITION AND A PATH. The run's own preamble quotes the token in
#: prose -- "a `>>` line is written when a check STARTS" -- so a bare substring
#: search for `>>` is satisfied by the preamble on a runner that emits no
#: in-flight line at all. That is the near-miss `_terminator` was written for,
#: one marker along, so this reads the same way: by shape, not by substring.
_STARTED = re.compile(r"^\s*>> \((\d+)/(\d+)\) (\S+)")


def _started_lines(text: str) -> list:
    """(position, denominator, name) for every check the log says STARTED."""
    return [(int(m.group(1)), int(m.group(2)), m.group(3))
            for m in (_STARTED.match(l) for l in text.splitlines()) if m]


class TheInFlightMarkerNamesTheCheckThatWasRunning(unittest.TestCase):
    """`>>` is the fourth of the four column-0 markers, and the only one that
    was not pinned anywhere.

    MEASURED SURVIVOR: renaming `MARK_RUNNING` from `>>` to anything else left
    the suite at 52 passed. The other three markers each reddened it.

    The `>>` line is what makes "died at check 3 of 17" readable off a truncated
    log rather than inferred from silence: the reader takes the LAST `>>` with
    no verdict block under it. Rename the token and every such reader goes
    quiet, and the log of a run that died inside a check becomes indistinguish-
    able from a log of a run that never started one -- which is D148's own
    defect class, one marker along.
    """

    def test_every_check_is_announced_by_name_before_it_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate_a.py": GATE.format(findings="[]"),
                "scripts/gate_b.py": GATE.format(findings="[]"),
            })
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_PASS, out)
        self.assertEqual(
            _started_lines(out),
            [(1, 2, "scripts/gate_a.py"), (2, 2, "scripts/gate_b.py")],
            "the in-flight marker did not name each check, in order, at its "
            "position against the planned denominator:\n" + out)

    def test_the_in_flight_marker_survives_into_a_truncated_log(self):
        """The property it exists for: the check that was RUNNING when the log
        ends is named in the log, not inferred from the absence of anything."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate_a.py": GATE.format(findings="[]"),
                "scripts/gate_b_slow.py": SLOW_GATE.format(seconds=45),
            })
            log = Path(tmp) / "run.log"
            with log.open("wb") as fh:
                proc = subprocess.Popen(
                    [sys.executable, str(RUNNER), "--root", str(root),
                     "--no-tests"], stdout=fh, stderr=subprocess.STDOUT)
                deadline = time.monotonic() + 60
                while time.monotonic() < deadline:
                    if _started_lines(log.read_text(errors="replace")):
                        break
                    if proc.poll() is not None:
                        break
                    time.sleep(0.2)
                proc.send_signal(signal.SIGTERM)
                proc.wait(timeout=60)
            out = log.read_text(errors="replace")
        started = _started_lines(out)
        self.assertTrue(started, "no check was ever announced:\n" + out)
        self.assertEqual(started[-1][2], "scripts/gate_b_slow.py",
                         "the log does not name what was in flight:\n" + out)


class TheTerminatorCountsWhatActuallyCompleted(unittest.TestCase):
    """MEASURED SURVIVOR: `ran={completed}/{expected}` reporting
    `{expected}/{expected}` instead left the suite at 52 passed.

    It survives against the runner because on the COMPLETE path the two numbers
    are equal by construction -- which is exactly why nothing caught it, and
    exactly why the numerator has to be pinned at the point it is chosen. A
    terminator that prints the denominator twice would report `ran=17/17` on the
    day a check unit is added that the loop can skip, and the ratio a reader
    uses to size a log would be a constant.
    """

    def test_the_COMPLETE_terminator_reports_the_completed_count(self):
        buf = io.StringIO()
        lc.Report(buf).end_complete(lc.PASS, RC_PASS,
                                    lc.Progress(expected=3, completed=1), 1.5)
        line = _terminator(buf.getvalue())
        self.assertTrue(line.startswith(END_COMPLETE), line)
        self.assertIn("ran=1/3", line)

    def test_the_INCOMPLETE_terminator_reports_the_completed_count(self):
        buf = io.StringIO()
        lc.Report(buf).end_incomplete(
            "SIGTERM was received", lc.Progress(expected=3, completed=1,
                                                in_flight="scripts/x.py"),
            1.5, RC_UNKNOWN_OUTPUT)
        line = _terminator(buf.getvalue())
        self.assertTrue(line.startswith(END_INCOMPLETE), line)
        self.assertIn("ran=1/3", line)
        self.assertIn("in-flight=scripts/x.py", line)


class NothingRanIsNeverAPass(unittest.TestCase):
    """Defect class B1 reached through the RUNNER's own options rather than
    through an empty tree.

    MEASURED SURVIVORS, both of them: `--list` returning `PASS, EXIT_PASS`, and
    a snapshot that could not be made returning the non-blocking `EXIT_UNKNOWN`.
    Each leaves a run that examined NOTHING wearing a code
    `scripts/installed/pre-push` waves through.
    """

    def test_list_mode_examines_nothing_and_that_is_not_a_pass(self):
        """The tree has a real defect in it. `--list` does not look at it, and
        a runner that answered PASS here would be certifying a tree it never
        opened -- with the finding sitting in the file it just enumerated."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="['a real defect']")})
            rc, out = _run(root, "--list")
        self.assertEqual(rc, RC_UNKNOWN_REACH, out)
        self.assertNotEqual(rc, RC_PASS,
                            "a run that executed no check reported a pass")
        self.assertIn("nothing was run, so there is no verdict", out)
        self.assertIn("verdict=UNKNOWN", _terminator(out))
        self.assertEqual(_started_lines(out), [],
                         "--list announced a check as starting")

    def test_a_snapshot_that_could_not_be_made_blocks(self):
        """Nothing was checked, and `NOTHING WAS CHECKED is a reason to stop`
        -- the hook's own words. Exit 3 would have been waved through."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]")}, git=False)
            rc, out = _run(root, "--tree", "snapshot", "--no-tests")
        self.assertEqual(
            rc, RC_UNKNOWN_OUTPUT,
            "the snapshot could not be made, so no check ran at all, and the "
            "run reached the hook on a non-blocking code:\n" + out)
        self.assertIn("because the snapshot could not be made", out)


class ASkipThatCouldHideAVerdictDowngradesTheRun(unittest.TestCase):
    """MEASURED SURVIVOR: emptying `HIDING_PREFIXES` left the suite at 52
    passed.

    That tuple is the whole difference between "everything I ran passed" and
    "everything I ran passed, and here is what I could not run". Empty it and a
    tree whose compute-bound and write-capable checks were all skipped comes
    back a clean PASS -- the coverage statement still printed above it, and
    nothing acting on it.
    """

    def test_a_compute_bound_check_that_was_skipped_downgrades_PASS_to_UNKNOWN(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]"),
                "scripts/needs_solver.py": NEEDS_COMPUTE_GATE,
            })
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_UNKNOWN_REACH, out)
        self.assertIn(
            "UNKNOWN scripts/needs_solver.py: skipped -- needs-compute", out,
            "the skipped compute check was not named as an unknown:\n" + out)
        self.assertNotIn("exit 0 -- clean", out)

    def test_the_same_tree_without_it_is_a_clean_PASS(self):
        """L-84's other half. Without this, the assertion above is satisfied by
        a runner that never returns PASS at all."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]")})
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_PASS, out)
        self.assertIn("exit 0 -- clean", out)

    def test_a_write_capable_check_skipped_in_live_mode_downgrades_it_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]"),
                "scripts/writer.py": WRITER_THAT_WRITES,
            })
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_UNKNOWN_REACH, out)
        self.assertIn("UNKNOWN scripts/writer.py: skipped -- writes-to-tree",
                      out)


class AFilteredRunMustNotReadAsAFullOne(unittest.TestCase):
    """`7bf55c90`: a "Full suite 115 passed" that was one file run alone.

    MEASURED SURVIVOR: blanking `only_note` left the suite at 52 passed. The
    filter still worked; what disappeared was the sentence saying it had been
    applied -- which is precisely the defect `7bf55c90` was, and it would be
    indefensible in this module of all modules.
    """

    def test_only_says_so_in_the_frame_and_again_under_the_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]"),
                "scripts/other_gate.py": GATE.format(findings="['a defect']"),
            })
            rc, out = _run(root, "--no-tests", "--only", "scripts/gate.py")
        # the defect in the tree was never looked at ...
        self.assertEqual(rc, RC_PASS, out)
        self.assertEqual(_started_lines(out), [(1, 1, "scripts/gate.py")], out)
        # ... and the run says so, twice, in its own words
        self.assertIn("--only 'scripts/gate.py' IN EFFECT: 1 of", out)
        self.assertIn("This run is NOT a full check of this lab", out)
        self.assertEqual(
            out.count("This run is NOT a full check of this lab"), 2,
            "the filter notice has to survive truncation of EITHER end of the "
            "log, so it is printed in the frame and again under the verdict:\n"
            + out)

    def test_an_unfiltered_run_carries_no_such_notice(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]")})
            rc, out = _run(root, "--no-tests")
        self.assertNotIn("IN EFFECT", out)


class AFailedEnumerationIsNotAnEmptyOne(unittest.TestCase):
    """MEASURED SURVIVOR: dropping `tracked_frame`'s `returncode != 0` arm left
    the suite at 52 passed.

    Without it a failed enumeration returns an EMPTY tracked frame and an
    empty note, so the run reports "tracked 0" as though the repository
    genuinely tracked nothing -- the silent-zero, in the half of the enumeration
    that decides what TRAVELS. The whole point of two frames is that the
    difference between them is a finding; a broken frame that reads as an empty
    one turns every tracked file into an untracked one silently.
    """

    def test_the_note_names_the_failure_rather_than_returning_a_clean_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths, note = lc.tracked_frame(Path(tmp))       # not a repository
        self.assertEqual(paths, [])
        self.assertIn("git ls-tree HEAD failed", note)

    def test_the_run_prints_that_note_in_its_frame(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]")}, git=False)
            rc, out = _run(root, "--no-tests")
        self.assertIn("git note", out)
        self.assertIn("git ls-tree HEAD failed", out)

    def test_a_working_repository_carries_no_such_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]")})
            rc, out = _run(root, "--no-tests")
        self.assertNotIn("git ls-tree HEAD failed", out)


class TheTrackedFrameReadsHEADAndNotTheIndex(unittest.TestCase):
    """Docket D274, ruled 2026-08-16: HEAD is the referent, never the index.

    THE PIN IS THE FAILING CASE, NOT AN ORDINARY ONE, and that distinction is
    the whole test. `git ls-files` lists INDEX entries, so a check over a
    NORMALLY-STAGED file passes throughout the broken period -- the index and
    HEAD agree about it. The state that separates them is A COMMITTED FILE WITH
    NO INDEX ENTRY, which on this tree is not exotic: every commit made by the
    private-index docket protocol leaves one, so the defect GROWS rather than
    staying constant. Measured at `452a0764`, 11 files were in that state and
    this runner reported all 11 as `untracked only -- present here, will not
    travel`, `scripts/check_docket_reconciliation.py` among them.

    `git rm --cached` reproduces exactly that state: the file stays on disk,
    stays in HEAD, and loses its index entry.
    """

    def _repo_with_a_deindexed_file(self, tmp: Path) -> Path:
        root = _tree(tmp, {"scripts/gate.py": GATE.format(findings="[]")})
        subprocess.run(["git", "rm", "--cached", "-q", "scripts/gate.py"],
                       cwd=root, check=True)
        # the premise, asserted rather than assumed: in HEAD, absent from the index
        listed = subprocess.run(["git", "ls-files", "--", "scripts/gate.py"],
                                cwd=root, capture_output=True, text=True)
        in_head = subprocess.run(["git", "cat-file", "-e",
                                  "HEAD:scripts/gate.py"], cwd=root)
        self.assertEqual(listed.stdout.strip(), "",
                         "the fixture did not remove the index entry")
        self.assertEqual(in_head.returncode, 0,
                         "the fixture did not leave the file in HEAD")
        return root

    def test_a_committed_file_with_no_index_entry_is_still_TRACKED(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo_with_a_deindexed_file(Path(tmp))
            paths, note = lc.tracked_frame(root)
        self.assertEqual(note, "")
        self.assertIn(
            "scripts/gate.py", paths,
            "a committed file was dropped from the frame that answers 'will "
            "this travel' because somebody's staging area did not mention it")

    def test_the_run_does_not_report_it_as_not_travelling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo_with_a_deindexed_file(Path(tmp))
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_PASS, out)
        self.assertNotIn(
            "will not travel", out,
            "the runner told its reader that a COMMITTED file would not "
            "travel, which is the D274 defect:\n" + out)

    def test_a_genuinely_untracked_file_is_still_reported(self):
        """The must-not-match half. Reading HEAD must not silence the frame:
        a file that really is absent from HEAD does not travel, and saying so
        is the reason the two frames are diffed at all."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {"scripts/gate.py": GATE.format(findings="[]")})
            (root / "scripts" / "never_committed.py").write_text(
                GATE.format(findings="[]"))
            rc, out = _run(root, "--no-tests")
        self.assertIn("will not travel", out)
        self.assertIn("scripts/never_committed.py", out)


class TheTempScopeExemptionIsPerFunctionNotPerModule(unittest.TestCase):
    """Docket D283: one `mkdtemp` anywhere disabled the write predicate for a
    WHOLE FILE, and the direction of that failure is the one that matters.

    `_write_primitive` collected `ast.Module` as a scope, and a scope counts as
    temp-scoped if ANY call inside it makes a temporary directory. The module
    contains every node in the file, so a single `tempfile.mkdtemp()` in some
    unrelated helper marked the module temp-scoped and the containment check
    then forgave EVERY write in it.

    This is a FALSE ADMIT, not a false skip. The module's own comment states the
    asymmetry: a false SKIP is printed and costs coverage, a false ADMIT runs a
    writer against a tree ten agents are working in. Measured at the repair: 8
    of 25 admitted script gates were admitted only by that blanket, and SEVEN
    were mutation harnesses -- programs that hold a tracked file mutated by
    construction -- reachable from `scripts/installed/pre-push`, which runs
    every admitted gate on every push.

    The positive case writes to an ABSOLUTE PATH INSIDE THE REPOSITORY, so
    there is no reading of it under which running the file would be safe.
    """

    def _classify(self, body: str):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "c.py").write_text(body)
            return lc.classify(root, lc.Candidate(path="scripts/c.py",
                                                  frames=("worktree",)),
                               allow_writers=False)

    #: The write and the `mkdtemp` are in DIFFERENT functions and have nothing
    #: to do with each other. Only the module encloses both.
    UNRELATED = (
        'import sys, tempfile\n'
        'from pathlib import Path\n'
        'def scratch():\n'
        '    return tempfile.mkdtemp()\n'
        'def main():\n'
        '    Path("/home/ubuntu/Certonomous/EVIDENCE.txt").write_text("x")\n'
        '    return 1 if True else 0\n'
        'if __name__ == "__main__":\n'
        '    sys.exit(main())\n')

    def test_a_mkdtemp_in_another_function_does_not_exempt_a_repo_write(self):
        c = self._classify(self.UNRELATED)
        self.assertFalse(
            c.admitted,
            "a module writing to an absolute path inside this repository was "
            "admitted against the LIVE tree because an unrelated helper "
            "elsewhere in the file called mkdtemp: " + c.reason)
        self.assertIn("writes-to-tree", c.reason)
        self.assertIn("write_text(...)", c.reason)

    def test_the_control_without_the_mkdtemp_is_skipped_the_same_way(self):
        """The two must agree, or the test above is measuring the write rather
        than the exemption."""
        c = self._classify(self.UNRELATED.replace(
            "    return tempfile.mkdtemp()\n", "    return 1\n"))
        self.assertFalse(c.admitted)
        self.assertIn("writes-to-tree", c.reason)

    def test_a_write_beside_its_own_mkdtemp_is_still_exempt(self):
        """The must-not-match half, and it is the case the exemption exists for:
        `detect_overwrite_signature.py` builds its whole control corpus under
        `mkdtemp` IN THE FUNCTION THAT WRITES. Refusing that would drop a
        working control for nothing."""
        c = self._classify(
            'import sys, tempfile\n'
            'def main():\n'
            '    d = tempfile.mkdtemp()\n'
            '    open(d + "/corpus.txt", "w").write("control")\n'
            '    return 1 if d else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertTrue(c.admitted, c.reason)


class ShellActuatorsAreNamedAsShell(unittest.TestCase):
    """MEASURED SURVIVOR: deleting the `.sh`/`.ps1` arm left the suite at 52
    passed, because the next arm catches the file anyway and it is still not
    admitted.

    What is lost is the REASON, and the reason is the coverage statement. These
    files are actuators -- `auto-stop.sh` powers the box off, `launch_solve.sh`
    spends core-hours -- and the module's stated position is that they are a
    named, permanent coverage gap. Filed under "not an executable module (data,
    prose or fixture)" they stop being a gap anybody can see.
    """

    def _classify_file(self, name: str, body: str):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / name).write_text(body)
            return lc.classify(root, lc.Candidate(path=f"scripts/{name}",
                                                  frames=("worktree",)),
                               allow_writers=False)

    def test_a_shell_actuator_is_classified_shell_and_the_hazard_is_named(self):
        c = self._classify_file("auto-stop.sh", "#!/bin/bash\nexit 1\n")
        self.assertFalse(c.admitted)
        self.assertEqual(c.kind, "shell")
        self.assertIn("no exit contract this runner can read", c.reason)
        self.assertNotIn("data, prose or fixture", c.reason)

    def test_the_coverage_statement_groups_it_under_shell(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]"),
                "scripts/auto-stop.sh": "#!/bin/bash\nexit 1\n",
            })
            rc, out = _run(root, "--no-tests")
        block = out.split("SKIPPED, BY REASON")[1].split("LAB-CHECK-PLAN")[0]
        self.assertIn("shell", block)
        self.assertIn("scripts/auto-stop.sh", block)

    def test_a_data_file_is_still_classified_other(self):
        """The must-not-match half: `shell` must not become the bucket for
        everything that is not Python."""
        c = self._classify_file("board.json", '{"a": 1}\n')
        self.assertEqual(c.kind, "other")
        self.assertIn("not an executable module", c.reason)


class StaleBytecodeIsPurgedBeforeTheSuiteRuns(unittest.TestCase):
    """MEASURED SURVIVOR: neutering `purge_pycache`'s `d == "__pycache__"` test
    left the suite at 52 passed.

    `__pycache__` under this repo has INVERTED mutation results in this lab --
    the clean control failed and the mutated case passed -- and
    `PYTHONDONTWRITEBYTECODE=1` does not fix it, because it stops writing and
    not reading. A purge that quietly stopped purging would be invisible: the
    frame would still print a number, the suite would still run, and the answers
    would be about bytecode that is no longer on disk anywhere.

    The assertion is on a PLANTED FILE and not on the directory: pytest recreates
    `__pycache__` while it runs, so a directory-existence check would be green
    on a runner that never purged anything.
    """

    def test_a_stale_bytecode_file_is_gone_after_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "sdk/tests/test_planted.py": TEST_FILE.format(rhs="1")})
            stale = root / "sdk" / "tests" / "__pycache__" / "stale.pyc"
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.write_bytes(b"bytecode from a tree that has moved on")
            rc, out = _run(root)
            survived = stale.exists()
        self.assertEqual(rc, RC_PASS, out)
        self.assertFalse(survived,
                         "stale bytecode outlived the purge that the frame "
                         "claims removed it")
        self.assertNotIn("__pycache__ purged    0 directories", out)


class AChecksStderrReachesTheReport(unittest.TestCase):
    """`NO 2>/dev/null, ANYWHERE` is a stated rule of this module.

    MEASURED SURVIVOR: deleting the stderr block from `_emit_outcome` left the
    suite at 52 passed -- the existing pin is on the `Outcome` object, and
    nothing asserted the bytes reach the log a person or a cron actually reads.
    A silent stderr is a claim, and the claim is "there was nothing on stderr".
    """

    def test_a_passing_checks_stderr_is_printed_under_its_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {"scripts/gate.py": GATE_WITH_STDERR})
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_PASS, out)
        self.assertIn("stderr (1 lines, NOT discarded)", out)
        self.assertIn("the board referent could not be read", out)

    def test_a_check_that_said_nothing_on_stderr_gets_no_such_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]")})
            rc, out = _run(root, "--no-tests")
        self.assertNotIn("NOT discarded", out)


class TruncationIsAnnounced(unittest.TestCase):
    """MEASURED SURVIVOR: deleting the `len(o.detail) > 25` notice left the
    suite at 52 passed.

    Silent truncation is the class this whole module exists to close. A block
    that shows 25 of 30 sub-results and says nothing is a smaller version of the
    zero-byte log that produced D148.
    """

    def test_a_block_that_shows_part_of_a_finding_says_how_much_it_hid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {"scripts/gate.py": NOISY_GATE})
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_FAIL, out)
        self.assertIn("sub-result 24 did not re-derive", out)
        self.assertNotIn("sub-result 29 did not re-derive", out)
        self.assertIn("and 5 further sub-result line(s), not shown", out)

    def test_a_block_that_shows_everything_says_nothing_about_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="['one defect']")})
            rc, out = _run(root, "--no-tests")
        self.assertNotIn("not shown", out)


class EveryWayACheckFailsToReportBlocks(unittest.TestCase):
    """The class the graded party controls, and therefore the class that must
    not pay. Three MEASURED SURVIVORS in it.

      * a check that TIMED OUT carried `blocking=False`  -> exit 3, waved through
      * a check that WOULD NOT LAUNCH carried `blocking=False` -> same
      * an exit code OUTSIDE the contract read as PASS
    """

    def test_a_check_that_timed_out_blocks_and_names_the_timeout(self):
        out = _run_one_script(
            'import sys, time\ntime.sleep(30)\nsys.exit(1)\n', timeout=1)
        self.assertEqual(out.verdict, lc.UNKNOWN, out.reason)
        self.assertIn("timed out after 1s", out.reason)
        self.assertTrue(
            out.blocking,
            "a check that never came back reached a non-blocking code; the "
            "runner cannot say what it would have found")

    def test_a_timed_out_check_takes_the_whole_run_to_a_blocking_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": SLOW_GATE.format(seconds=30)})
            rc, out = _run(root, "--no-tests", "--timeout", "1")
        self.assertEqual(rc, RC_UNKNOWN_OUTPUT, out)
        self.assertIn("timed out after 1s", out)

    def test_a_check_that_could_not_be_launched_blocks(self):
        real = lc.subprocess.run

        def refuse(argv, *a, **kw):
            if argv and argv[0] == sys.executable:
                raise OSError(13, "Permission denied")
            return real(argv, *a, **kw)

        lc.subprocess.run = refuse
        try:
            out = _run_one_script('import sys\nsys.exit(1)\n')
        finally:
            lc.subprocess.run = real
        self.assertEqual(out.verdict, lc.UNKNOWN, out.reason)
        self.assertIn("could not launch", out.reason)
        self.assertTrue(out.blocking,
                        "a check that never started reached a non-blocking "
                        "code")

    def test_an_exit_code_outside_the_contract_is_UNKNOWN_and_names_the_code(self):
        out = _run_one_script('import sys\nprint("frame")\nsys.exit(7)\n')
        self.assertEqual(out.verdict, lc.UNKNOWN, out.reason)
        self.assertIn("exit 7 (outside the published contract)", out.reason)
        self.assertTrue(out.blocking, out.reason)

    def test_a_run_containing_one_such_check_exits_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py":
                    'import sys\n\n\ndef main():\n    print("frame")\n'
                    '    return 7\n\n\nif __name__ == "__main__":\n'
                    '    sys.exit(main())\n'})
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_UNKNOWN_OUTPUT, out)
        self.assertIn("outside the published contract", out)

    def test_a_check_that_exited_zero_is_a_PASS_whatever_it_put_on_stderr(self):
        """The must-not-fire half of the crash downgrade, and a MEASURED
        SURVIVOR of its own: dropping `and code != 0` from the downgrade left
        the suite at 52 passed.

        A check that mentioned a traceback and still exited 0 has not crashed.
        Reading it as UNKNOWN would make every check that prints a captured
        traceback in its own report unschedulable -- an alarm, not a gate.
        """
        out = _run_one_script(
            'import sys\n'
            'sys.stderr.write("Traceback (most recent call last)\\n")\n'
            'sys.exit(0)\n')
        self.assertEqual(out.verdict, lc.PASS, out.reason)
        self.assertFalse(out.blocking, out.reason)


class AFailingRunSaysItIsBlocking(unittest.TestCase):
    """MEASURED SURVIVOR: `blocking = bool(fails) or any(...)` reduced to
    `any(...)` left the suite at 52 passed.

    The exit code is unmoved -- FAIL is 1 either way -- so nothing that asserts
    on the code can see it. What moves is the SENTENCE, and it moves all the way
    to the wrong end: a run that found a defect prints `exit 1 -- clean.`
    """

    def test_a_run_that_found_a_defect_does_not_call_itself_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="['a real defect']")})
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_FAIL, out)
        self.assertIn("BLOCKING. A check that ran returned a finding.", out)
        self.assertNotIn("exit 1 -- clean", out)


class TheSuiteGroupSeparatesTheLabFromTheInstrument(unittest.TestCase):
    """Three MEASURED SURVIVORS inside `run_pytest`, all on the same boundary.

      * a test that ERRORED read as FAIL rather than UNKNOWN
      * a suite that collected nothing while exiting 0 read as PASS
      * "pytest itself collected nothing (rc=5)" and "we parsed zero cases"
        became the same sentence
    """

    def test_an_errored_test_is_UNKNOWN_about_the_instrument_not_a_FAIL(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "sdk/tests/test_broken.py": ERRORING_TEST_FILE})
            rc, out = _run(root)
        self.assertEqual(
            rc, RC_UNKNOWN_OUTPUT,
            "a broken fixture was reported in the vocabulary of a finding "
            "about the lab:\n" + out)
        self.assertIn("0 failed, 1 errored, out of 1", out)
        self.assertNotIn("VERDICT: FAIL", out)

    def test_a_genuinely_failing_test_is_still_a_FAIL(self):
        """The must-not-match half: the boundary has to cut, not slide."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "sdk/tests/test_planted.py": TEST_FILE.format(rhs="2")})
            rc, out = _run(root)
        self.assertEqual(rc, RC_FAIL, out)
        self.assertIn("VERDICT: FAIL", out)

    def test_a_suite_pytest_refused_to_collect_names_pytests_own_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "sdk/tests/test_helpers_only.py": HELPER_DECLARING_NO_TEST})
            rc, out = _run(root)
        self.assertEqual(rc, RC_UNKNOWN_OUTPUT, out)
        self.assertIn("no tests were collected (rc=5)", out)

    def test_a_suite_that_collected_nothing_and_exited_zero_is_not_a_PASS(self):
        """B1 in the suite group. pytest reports success, the junit document
        holds no case at all, and an empty suite is not a pass."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "sdk/tests/test_helpers_only.py": HELPER_DECLARING_NO_TEST,
                "sdk/tests/conftest.py": CONFTEST_FORCES_EXIT_ZERO})
            rc, out = _run(root)
        self.assertEqual(
            rc, RC_UNKNOWN_OUTPUT,
            "the suite collected nothing, said it was happy, and the runner "
            "agreed:\n" + out)
        self.assertIn("zero tests collected -- an empty suite is not a pass",
                      out)


class WhoMayWriteToTheTreeBeingGraded(unittest.TestCase):
    """Three MEASURED SURVIVORS on the write axis.

      * `--tree snapshot` implying `--admit-writers` was never driven
      * the OBSERVED write -- `TREE CHANGED DURING THIS CHECK` -- was never
        driven, so the static predicate had a test and the measurement did not
      * the snapshot-mode downgrade of a check that wrote was never driven
    """

    def test_snapshot_mode_admits_a_write_capable_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/writer.py": WRITER_THAT_DOES_NOT_WRITE})
            rc, out = _run(root, "--tree", "snapshot", "--no-tests")
        self.assertEqual(rc, RC_PASS, out)
        self.assertEqual(_started_lines(out), [(1, 1, "scripts/writer.py")],
                         "the write-capable check was not run in snapshot "
                         "mode:\n" + out)
        self.assertNotIn("writes-to-tree", out)

    def test_the_same_check_is_skipped_against_the_live_tree(self):
        """The must-not-match half, and the reason the flag exists: ten agents
        write in the live tree."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/writer.py": WRITER_THAT_DOES_NOT_WRITE})
            rc, out = _run(root, "--no-tests")
        self.assertIn("writes-to-tree", out)
        self.assertEqual(_started_lines(out), [], out)

    def test_a_check_that_writes_is_reported_by_name_with_what_it_touched(self):
        """The static predicate PREDICTS; this MEASURES. Against the live tree
        the write is reported and not charged to the check, because other
        agents write here too."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {"scripts/writer.py": WRITER_THAT_WRITES})
            rc, out = _run(root, "--no-tests", "--admit-writers")
        self.assertEqual(rc, RC_PASS, out)
        self.assertIn("TREE CHANGED DURING THIS CHECK", out)
        self.assertIn("planted_control.txt", out)
        self.assertIn("other agents write here too", out)

    def test_in_snapshot_mode_the_same_write_downgrades_its_own_verdict(self):
        """The tree is the runner's there, so the write IS charged: an exit code
        that grades a write the runner caused is not a finding about the lab."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {"scripts/writer.py": WRITER_THAT_WRITES})
            rc, out = _run(root, "--tree", "snapshot", "--no-tests")
        self.assertEqual(rc, RC_UNKNOWN_OUTPUT, out)
        self.assertIn("TREE CHANGED DURING THIS CHECK", out)
        self.assertIn("its exit code is not a clean finding", out)


class MoreAdmissionPredicates(unittest.TestCase):
    """Four MEASURED SURVIVORS among the predicates that decide what runs.

    A false SKIP costs coverage and is printed; a false ADMIT writes into a tree
    ten agents are working in, or spends compute nobody authorised. These are
    the four that had no cover in either direction.
    """

    def _classify(self, body: str, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "c.py").write_text(body)
            return lc.classify(root, lc.Candidate(path="scripts/c.py",
                                                  frames=("worktree",)),
                               allow_writers=kw.get("writers", False))

    def test_open_in_write_mode_is_a_write(self):
        c = self._classify(
            'import sys\n'
            'def main():\n'
            '    open("report.txt", "w").write("x")\n'
            '    return 1 if True else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertFalse(c.admitted)
        self.assertIn("writes-to-tree", c.reason)
        self.assertIn("open(..., 'w')", c.reason)

    def test_open_for_reading_is_not_a_write(self):
        """The must-not-match half: `open(p)` and `open(p, "r")` are how every
        check in this repository reads its evidence."""
        c = self._classify(
            'import sys\n'
            'def main():\n'
            '    body = open("report.txt", "r").read()\n'
            '    return 1 if body else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertTrue(c.admitted, c.reason)

    def test_write_text_is_a_write_whoever_the_receiver_is(self):
        c = self._classify(
            'import sys\n'
            'from pathlib import Path\n'
            'def main():\n'
            '    Path("report.txt").write_text("x")\n'
            '    return 1 if True else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertFalse(c.admitted)
        self.assertIn("write_text(...)", c.reason)

    def test_a_write_scoped_to_a_temporary_directory_is_still_admitted(self):
        """`detect_overwrite_signature.py`'s self-test builds its whole control
        corpus under `mkdtemp`. Refusing to run it on that basis would drop a
        working control for nothing."""
        c = self._classify(
            'import sys, tempfile\n'
            'def main():\n'
            '    d = tempfile.mkdtemp()\n'
            '    open(d + "/corpus.txt", "w").write("control")\n'
            '    return 1 if d else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertTrue(c.admitted, c.reason)

    def test_reading_sys_argv_one_means_it_needs_arguments(self):
        c = self._classify(
            'import sys\n'
            'def main():\n'
            '    return 1 if sys.argv[1] else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertFalse(c.admitted)
        self.assertIn("reads sys.argv[1]", c.reason)

    def test_reading_sys_argv_as_a_whole_does_not(self):
        """The must-not-match half: `len(sys.argv)` is not a required argument."""
        c = self._classify(
            'import sys\n'
            'def main():\n'
            '    return 1 if len(sys.argv) > 9 else 0\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main())\n')
        self.assertTrue(c.admitted, c.reason)

    ARGPARSE = ('import argparse, sys\n'
                'def main():\n'
                '    p = argparse.ArgumentParser()\n'
                '    p.add_argument("case"{nargs})\n'
                '    a = p.parse_args()\n'
                '    return 1 if a.case else 0\n'
                'if __name__ == "__main__":\n'
                '    sys.exit(main())\n')

    def test_an_optional_positional_is_schedulable(self):
        """MEASURED SURVIVOR: narrowing the `nargs` exemption from `("?", "*")`
        to `("*",)` left the suite at 52 passed.

        A positional the parser will happily leave unset is not an argument the
        check REQUIRES, and skipping it costs a check that would have run
        unattended -- the false SKIP that this module says is the cheap error
        but is not the free one.
        """
        for nargs in ('"?"', '"*"'):
            with self.subTest(nargs=nargs):
                c = self._classify(
                    self.ARGPARSE.format(nargs=f", nargs={nargs}"))
                self.assertTrue(c.admitted, c.reason)

    def test_a_positional_that_must_be_given_is_not(self):
        """The must-fire half, in both of its shapes."""
        for nargs in ("", ', nargs="+"'):
            with self.subTest(nargs=nargs or "(none)"):
                c = self._classify(self.ARGPARSE.format(nargs=nargs))
                self.assertFalse(c.admitted, c.reason)
                self.assertIn("argparse positional 'case'", c.reason)

    def test_the_runner_never_admits_itself(self):
        """MEASURED SURVIVOR: deleting the `is this me?` arm left the suite at
        52 passed.

        `lab_check.py` lives in `scripts/`, so it enumerates itself on every
        run. It parses as a gate -- `main()` returns `EXIT_UNSOUND` -- so
        without this arm the runner is a candidate for its own admitted set,
        and under `--admit-writers` or `--tree snapshot` it is ADMITTED and
        launched recursively, each copy enumerating and launching another.
        Asserted with `--admit-writers`' predicate, which is the reachable
        worst case rather than the comfortable one.
        """
        c = lc.classify(REPO, lc.Candidate(path=str(RUNNER),
                                           frames=("tracked",)),
                        allow_writers=True)
        self.assertEqual(c.kind, "runner", c.reason)
        self.assertFalse(c.admitted,
                         "the runner admitted itself as one of its own "
                         "checks: " + c.reason)
        self.assertIn("the runner itself", c.reason)


class AnInterruptedJsonRunIsFlaggedInTheDocument(unittest.TestCase):
    """MEASURED SURVIVOR: flipping the interrupted document's `complete` to
    `True` left the suite at 52 passed.

    `complete` is the one key a consumer of a partial document needs, and the
    complete path was pinned while the partial path -- the only one where the
    key carries information -- was not.
    """

    def test_a_killed_json_run_says_complete_false_and_names_the_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate_a.py": GATE.format(findings="[]"),
                "scripts/gate_b_slow.py": SLOW_GATE.format(seconds=45),
            })
            op, ep = Path(tmp) / "out.json", Path(tmp) / "err.log"
            with op.open("wb") as fo, ep.open("wb") as fe:
                proc = subprocess.Popen(
                    [sys.executable, str(RUNNER), "--root", str(root),
                     "--no-tests", "--json"], stdout=fo, stderr=fe)
                deadline = time.monotonic() + 60
                while time.monotonic() < deadline:
                    if len(_started_lines(
                            ep.read_text(errors="replace"))) >= 2:
                        break
                    if proc.poll() is not None:
                        break
                    time.sleep(0.2)
                else:
                    proc.kill()
                    self.fail("the runner never reached the slow gate")
                proc.send_signal(signal.SIGTERM)
                rc = proc.wait(timeout=60)
            raw = op.read_text()
            err = ep.read_text(errors="replace")
        self.assertTrue(
            raw.strip(),
            "`--json` promises stdout carries a document or nothing, and an "
            "interrupted run emitted nothing -- which is the silent zero the "
            "streaming repair exists to remove:\n" + err)
        doc = json.loads(raw)
        self.assertEqual(rc, RC_UNKNOWN_OUTPUT, err)
        self.assertIs(doc["complete"], False,
                      "a partial document claimed to be a whole one")
        self.assertEqual(doc["verdict"], "UNKNOWN")
        self.assertIn("SIGTERM", doc["interrupted"])
        self.assertEqual(doc["completed"], 1)
        self.assertEqual(doc["in_flight"], "scripts/gate_b_slow.py")


class TheSuiteThatWasNotRunIsStillOnTheRecord(unittest.TestCase):
    """MEASURED SURVIVOR: dropping the `--no-tests` pseudo-candidate from the
    hiding list left the suite at 52 passed.

    `--no-tests` is what `scripts/installed/pre-push` runs on every push. Drop
    that one record and the fast tier returns a clean PASS over a tree whose
    entire test suite was never opened -- a green whose frame does not cover its
    enumeration, which is `7bf55c90` with a hook attached.
    """

    def test_no_tests_leaves_the_run_UNKNOWN_and_names_the_suite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]"),
                "sdk/tests/test_planted.py": TEST_FILE.format(rhs="1"),
            })
            rc, out = _run(root, "--no-tests")
        self.assertEqual(
            rc, RC_UNKNOWN_REACH,
            "the suite was never run and the fast tier called the tree "
            "clean:\n" + out)
        self.assertIn("test file(s) were enumerated and NOT run", out)
        self.assertIn("UNKNOWN sdk/tests (pytest): skipped -- needs-compute: "
                      "--no-tests was passed", out)

    def test_the_same_tree_with_the_suite_run_is_a_PASS(self):
        """L-84's other half: the downgrade is about what was SKIPPED, not a
        standing objection to the tree."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]"),
                "sdk/tests/test_planted.py": TEST_FILE.format(rhs="1"),
            })
            rc, out = _run(root)
        self.assertEqual(rc, RC_PASS, out)


class ADeclaredDivergenceStaysLoud(unittest.TestCase):
    """MEASURED SURVIVOR: deleting the bare-status-word scrape left the suite
    at 52 passed.

    This is the documented case and it is not hypothetical: the auto-stop repair
    of D65 sits in `installed_registry.py` as `PENDING`, and the registry exits
    0 on a declared PENDING. A runner that printed only the exit code would show
    `[PASS] installed_registry.py` and hide the fact that the box is running an
    uninstalled power gate -- the check said something, the runner read it, and
    nothing carried it to the reader.
    """

    REGISTRY_SHAPE = '''\
#!/usr/bin/env python3
"""The `installed_registry.py` shape: a declared divergence, and exit 0."""
import sys

UNDECLARED = []


def main():
    print("PENDING  auto-stop gate is declared but not installed")
    return 1 if UNDECLARED else 0


if __name__ == "__main__":
    sys.exit(main())
'''

    def test_a_PENDING_line_under_an_exit_zero_still_reaches_the_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {"scripts/registry.py": self.REGISTRY_SHAPE})
            rc, out = _run(root, "--no-tests")
        self.assertEqual(rc, RC_PASS, out)
        self.assertIn(
            "- PENDING  auto-stop gate is declared but not installed", out,
            "the check declared a divergence, exited 0, and the runner showed "
            "only the exit code:\n" + out)

    def test_a_check_with_nothing_to_declare_gets_no_sub_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]")})
            rc, out = _run(root, "--no-tests")
        self.assertNotIn("PENDING", out)


class TheReaderHangingUpIsNotAPass(unittest.TestCase):
    """`lab_check.py | head` is the ordinary way somebody reads the top of a
    report, and the run really is truncated when it happens.

    THE `except BrokenPipeError` ARM IS NOT REACHED ON THIS PATH, and that is a
    DEFECT filed on the docket rather than repaired here. Measured: the runner
    exits **120**, not the `EXIT_UNSOUND` its own arm returns, because the four
    banner lines and `Report.begin` are written BEFORE `main()` enters the
    `try:` that carries the arm. The first write is the one that raises, so the
    exception leaves `main()` uncovered, the interpreter's shutdown flush raises
    again, and the process ends 120 -- the exact number the arm's own comment
    says it was written to avoid.

    That is why the mutation that made the arm `return EXIT_PASS` survived: the
    arm is dead code on the path it exists for, so nothing a test does to that
    path can see what it returns.

    What IS pinned here is the property the arm was for, at the strength the
    shipped runner actually delivers it, and it holds under the repair as well:
    a truncated report never leaves a passing exit status, and it never leaves a
    terminator claiming the run finished. 120 is outside the published contract,
    so `scripts/installed/pre-push` blocks on it through its `*` arm -- it fails
    safe, by accident rather than by design, which is precisely the distinction
    worth writing down.
    """

    def test_a_hung_up_reader_never_yields_a_passing_exit_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]")})
            proc = subprocess.Popen(
                [sys.executable, str(RUNNER), "--root", str(root),
                 "--no-tests"], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            proc.stdout.close()               # the reader hangs up
            err = proc.stderr.read().decode(errors="replace")
            rc = proc.wait(timeout=120)
        self.assertNotEqual(
            rc, RC_PASS,
            "the report was truncated by its reader and the run still exited "
            "as though it had finished cleanly:\n" + err)
        self.assertNotIn(
            rc, (RC_FAIL, RC_UNKNOWN_REACH),
            "a truncated run took a code that is either a claim about the lab "
            "or a non-blocking one:\n" + err)
        self.assertEqual(_terminator(err), "",
                         "a run nobody could be told about certified itself")


class AKeyboardInterruptBeforeTheHandlersAreInstalled(unittest.TestCase):
    """MEASURED SURVIVOR: the `except KeyboardInterrupt` arm returning
    `EXIT_UNKNOWN` instead of `EXIT_UNSOUND` left the suite at 52 passed.

    It is the narrow arm -- reachable in the window before the handlers are
    installed, or off the main thread -- and it is the arm nothing drove. An
    interrupted run that reached the hook on 3 would have been pushed on top of.

    Patched on the imported module OBJECT, never on the file: the tracked
    worktree is not mutated by this suite.
    """

    def test_it_is_reported_as_an_interrupted_run_and_blocks(self):
        def interrupt(*a, **kw):
            raise KeyboardInterrupt()

        buf = io.StringIO()
        original = lc.run_script
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {
                "scripts/gate.py": GATE.format(findings="[]")})
            lc.run_script = interrupt
            try:
                with contextlib.redirect_stdout(buf):
                    rc = lc.main(["--root", str(root), "--no-tests"])
            finally:
                lc.run_script = original
        out = buf.getvalue()
        self.assertEqual(rc, RC_UNKNOWN_OUTPUT, out)
        self.assertNotEqual(rc, RC_UNKNOWN_REACH,
                            "an interrupted run reached the hook on the code "
                            "it does not block on:\n" + out)
        self.assertTrue(_terminator(out).startswith(END_INCOMPLETE), out)
        self.assertIn("KeyboardInterrupt was received", out)


if __name__ == "__main__":
    unittest.main()
