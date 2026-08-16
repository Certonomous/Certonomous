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


if __name__ == "__main__":
    unittest.main()
