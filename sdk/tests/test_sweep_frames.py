"""A sweep that cannot state its frame is the defect, not the count it returns.

WHAT THESE TESTS ARE EVIDENCE FOR. On 2026-08-11 an auditor found that `grep`
in this environment is a shell function, not `/usr/bin/grep`. It execs
`ugrep -G --ignore-files --hidden -I --exclude-dir=.git ...`, and
`--ignore-files` honours `.gitignore`. This lab gitignores its large case
archives. So a repo-wide `grep -r` here silently swept a strict subset of the
tree and returned a clean, confident zero over the rest -- recorded as L-75,
and as `grep-honours-ignore-files` in the lab memory.

That is this lab's signature failure mode -- a verdict that does not state what
it swept -- living inside the tool the auditors used to hunt it.

`scripts/sweep.py` is the sanctioned replacement, and this file is the test
that would have caught the original defect. The load-bearing property is not
"the sweep finds things". It is that TWO NAMED FRAMES DISAGREE, and that the
disagreement is visible to the caller:

  * `test_gitignored_plant_is_seen_by_the_everything_frame` plants a token in
    a gitignored directory and requires the everything-frame to return it.
  * `test_positive_control_ignore_honouring_frame_does_not_see_the_plant` is
    the positive control on that negative. It requires the ignore-honouring
    frame to MISS the same token. Without it the first test passes vacuously
    the day the environment changes and both frames become the same frame --
    which is precisely how the original defect survived: nobody had a check
    that could tell the two apart.

Three further properties, each of which has failed in this ladder at least
once:

  * A file that raised is not a file that contained no match. L-76 records a
    parser whose docstring said it never raises, raising on one non-UTF-8
    byte, out of the check and out of the entire audit run. `VerdictTests`
    requires the third verdict -- UNKNOWN -- to fire on a file the sweep could
    not read, rather than a zero that reads as a clean bill.
  * A frame documented as "everything" that quietly drops a directory is the
    same lie one level up. `FrameHonestyTests` plants a file inside `.git/`
    and requires the everything-frame to return it, and the VCS-pruning frame
    to be named for what it prunes.
  * Counts from two frames are two measurements (L-75: an irreconcilable gap
    between such a pair turned out to be this, not a discovery).
    `FrameComparisonTests` requires the comparison to RAISE, with a positive
    control that same-frame comparison still works.

And L-76's own rule is executed here rather than promised:
`AbsoluteClaimTests` reads `scripts/sweep.py`, finds each `never` / `always` /
`cannot` / `every` / `no longer` / `impossible` / `guaranteed` in it, and fails
unless a real test in this file is named in the same paragraph. It carries its
own positive control: a synthetic unbacked absolute the checker must catch.

Against `scripts/sweep.py` as it stood before 2026-08-11 every test in this
file errors at import, because the module did not exist.
"""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "certonomous_sweep", REPO / "scripts" / "sweep.py")
sw = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = sw
_SPEC.loader.exec_module(sw)

TOKEN = "ZQ7_PLANTED_SWEEP_TOKEN_9F4"


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, check=False)


class PlantedTree:
    """A throwaway git repo with the L-75 shape: a token inside an ignored dir.

    Written under a uniquely-named temp directory rather than a shared
    scratchpad root -- L-77, where an author silently overwrote a grader's
    held-out evidence at a shared path.
    """

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="sweep_frames_plant_"))
        _git(self.root, "init", "-q")
        (self.root / ".gitignore").write_text(
            "ignored_archive/\ntracked_but_ignored.txt\n", encoding="utf-8")
        (self.root / "visible.txt").write_text(TOKEN + "\n", encoding="utf-8")
        (self.root / "ignored_archive").mkdir()
        (self.root / "ignored_archive" / "case.log").write_text(
            "solver line\n" + TOKEN + "\n", encoding="utf-8")
        # The subtle half of the defect: a file that is BOTH tracked and
        # gitignored. This repo carries thousands of them, and the
        # ignore-honouring sweep skips them regardless of tracked-ness.
        (self.root / "tracked_but_ignored.txt").write_text(
            TOKEN + "\n", encoding="utf-8")
        _git(self.root, "add", "visible.txt", ".gitignore")
        _git(self.root, "add", "-f", "tracked_but_ignored.txt")

    def cleanup(self) -> None:
        subprocess.run(["rm", "-rf", str(self.root)], check=False)


class IgnoredPathReachTests(unittest.TestCase):
    """The original defect: a token in a gitignored path, and a silent zero."""

    def setUp(self) -> None:
        self.tree = PlantedTree()
        self.addCleanup(self.tree.cleanup)

    def test_gitignored_plant_is_seen_by_the_everything_frame(self):
        res = sw.sweep(TOKEN, root=self.tree.root,
                       frame=sw.EVERYTHING_UNDER_ROOT, regex=False)
        found = {h.path for h in res.hits}
        self.assertIn("ignored_archive/case.log", found,
                      f"the everything-frame missed a gitignored plant: {res.verdict_line()}")
        self.assertIn("visible.txt", found)
        self.assertIn("tracked_but_ignored.txt", found)
        self.assertEqual("MATCHES", res.verdict, res.verdict_line())

    def test_positive_control_ignore_honouring_frame_does_not_see_the_plant(self):
        """The control that keeps the test above from passing vacuously.

        This asserts the two frames ACTUALLY DIFFER. If the environment ever
        changes so that the ignore-honouring path sees the ignored file too,
        this test fails and the pair stops being evidence of anything -- which
        is the outcome we want, rather than a green suite over a frame
        distinction that has quietly disappeared.
        """
        res = sw.sweep(TOKEN, root=self.tree.root,
                       frame=sw.IGNORE_HONOURING, regex=False)
        found = {h.path for h in res.hits}
        self.assertIn("visible.txt", found,
                      "the ignore-honouring frame found nothing at all, so its "
                      "miss below is not evidence of a filter")
        self.assertNotIn("ignored_archive/case.log", found,
                         "the two frames no longer differ; L-75's filter is "
                         "either gone or this model of it is wrong")
        self.assertNotIn("tracked_but_ignored.txt", found,
                         "a tracked-but-gitignored file must still be filtered "
                         "here: git check-ignore needs --no-index to model "
                         "what ugrep --ignore-files actually does")

    def test_the_two_frames_disagree_by_exactly_the_ignored_files(self):
        everything = sw.sweep(TOKEN, root=self.tree.root,
                              frame=sw.EVERYTHING_UNDER_ROOT, regex=False)
        honouring = sw.sweep(TOKEN, root=self.tree.root,
                             frame=sw.IGNORE_HONOURING, regex=False)
        gap = ({h.path for h in everything.hits}
               - {h.path for h in honouring.hits})
        self.assertEqual({"ignored_archive/case.log", "tracked_but_ignored.txt"},
                         gap,
                         "the reach gap is not the ignored files, so either "
                         "frame is doing something unstated")

    def test_tracked_frame_reaches_tracked_but_gitignored_files(self):
        """`git ls-files` denominators are sound; L-75 says so and this shows it."""
        res = sw.sweep(TOKEN, root=self.tree.root, frame=sw.TRACKED_ONLY,
                       regex=False)
        found = {h.path for h in res.hits}
        self.assertIn("tracked_but_ignored.txt", found, res.verdict_line())
        self.assertNotIn("ignored_archive/case.log", found,
                         "tracked-only must be honest about being tracked-only")


class VerdictTests(unittest.TestCase):
    """Did the check run, before what did it find. Three verdicts, not two."""

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="sweep_frames_verdict_"))
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.root)])
        _git(self.root, "init", "-q")
        (self.root / "a.txt").write_text("nothing of interest\n", encoding="utf-8")

    def _dangle(self) -> None:
        os.symlink(self.root / "does_not_exist", self.root / "dangling.txt")

    def test_positive_control_clean_tree_gives_zero_not_unknown(self):
        """The control on UNKNOWN: it is not the answer to everything.

        Without this, `test_unreadable_file_forces_unknown_not_zero` would
        pass on a helper that returned UNKNOWN unconditionally.
        """
        res = sw.sweep(TOKEN, root=self.root, frame=sw.WORKING_TREE_NO_VCS,
                       regex=False)
        self.assertEqual("ZERO", res.verdict, res.verdict_line())
        self.assertTrue(res.complete)

    def test_unreadable_file_forces_unknown_not_zero(self):
        """A file that raised is not a file that contained no match."""
        self._dangle()
        res = sw.sweep(TOKEN, root=self.root, frame=sw.WORKING_TREE_NO_VCS,
                       regex=False)
        self.assertEqual("UNKNOWN", res.verdict, res.verdict_line())
        self.assertNotEqual("ZERO", res.verdict)
        self.assertEqual(1, res.skips.unreadable, res.frame_block())
        self.assertIn("dangling.txt", " ".join(res.skips.unreadable_paths))
        self.assertIn("UNKNOWN because", res.verdict_line())
        with self.assertRaises(sw.SweepIncomplete):
            res.require_complete()

    def test_unknown_survives_a_hit_elsewhere_in_the_same_sweep(self):
        """A partial sweep reporting a total is the failure mode itself."""
        (self.root / "b.txt").write_text(TOKEN + "\n", encoding="utf-8")
        self._dangle()
        res = sw.sweep(TOKEN, root=self.root, frame=sw.WORKING_TREE_NO_VCS,
                       regex=False)
        self.assertTrue(res.hits, "the readable plant was not found")
        self.assertEqual("UNKNOWN", res.verdict,
                         "hits masked an unread file: " + res.verdict_line())

    def test_zero_verdict_states_its_skips_in_the_verdict_line(self):
        """Skips reach the verdict, not only a footnote."""
        (self.root / "big.txt").write_text("x" * 4096, encoding="utf-8")
        res = sw.sweep(TOKEN, root=self.root, frame=sw.WORKING_TREE_NO_VCS,
                       regex=False, size_cap=1024)
        self.assertEqual("ZERO", res.verdict)
        self.assertFalse(res.complete, "a capped sweep reported itself complete")
        self.assertIn("not searched", res.verdict_line())
        self.assertIn("over size cap", res.verdict_line())
        self.assertEqual(1, res.skips.over_size_cap)

    def test_binary_and_size_and_unreadable_are_counted_separately(self):
        """Lumping the skip reasons together is how a filter goes unstated."""
        (self.root / "bin.dat").write_bytes(b"head\x00" + TOKEN.encode())
        (self.root / "big.txt").write_text("y" * 4096, encoding="utf-8")
        self._dangle()
        res = sw.sweep(TOKEN, root=self.root, frame=sw.WORKING_TREE_NO_VCS,
                       regex=False, size_cap=1024)
        self.assertEqual(1, res.skips.binary)
        self.assertEqual(1, res.skips.over_size_cap)
        self.assertEqual(1, res.skips.unreadable)
        self.assertEqual(3, res.skips.total)
        for phrase in ("binary", "over size cap", "unreadable"):
            self.assertIn(phrase, res.skips.words())

    def test_non_utf8_file_is_searched_rather_than_crashing_the_sweep(self):
        """L-76's crash class: one non-UTF-8 byte took out an entire audit run."""
        # Raw latin-1 bytes, invalid as UTF-8 -- the shape of the file that
        # crashed the audit: a list of international author names.
        (self.root / "authors.txt").write_bytes(
            b"Lac\xe1tu\xdf, Reissmann\n" + TOKEN.encode())
        res = sw.sweep(TOKEN, root=self.root, frame=sw.WORKING_TREE_NO_VCS,
                       regex=False)
        self.assertEqual("MATCHES", res.verdict, res.verdict_line())
        self.assertEqual(1, res.non_utf8_searched, res.frame_block())
        self.assertIn("authors.txt", {h.path for h in res.hits})


class FrameHonestyTests(unittest.TestCase):
    """No frame here is named for more reach than it has."""

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="sweep_frames_honesty_"))
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.root)])
        _git(self.root, "init", "-q")
        (self.root / "visible.txt").write_text(TOKEN + "\n", encoding="utf-8")
        (self.root / ".git" / "PLANTED").write_text(TOKEN + "\n", encoding="utf-8")

    def test_everything_frame_includes_git_internals(self):
        """`--exclude-dir=.git` is the wrapper's other unstated filter."""
        res = sw.sweep(TOKEN, root=self.root, frame=sw.EVERYTHING_UNDER_ROOT,
                       regex=False)
        self.assertIn(".git/PLANTED", {h.path for h in res.hits},
                      "a frame called 'everything' skipped .git/: "
                      + res.verdict_line())

    def test_worktree_frame_prunes_vcs_and_says_which_dirs(self):
        res = sw.sweep(TOKEN, root=self.root, frame=sw.WORKING_TREE_NO_VCS,
                       regex=False)
        self.assertNotIn(".git/PLANTED", {h.path for h in res.hits})
        self.assertIn(".git", res.frame.filter_words)
        self.assertIn("drops", res.frame.filter_words)

    def test_sweep_refuses_to_run_without_a_frame(self):
        with self.assertRaises(TypeError):
            sw.sweep(TOKEN, root=self.root)

    def test_every_frame_states_a_selection_rule_and_a_filter(self):
        """Evidence for: a frame with no filter sentence is unusable (L-75)."""
        for name, frame in sw.FRAMES.items():
            with self.subTest(frame=name):
                self.assertTrue(frame.rule_words.strip(), name)
                self.assertTrue(frame.filter_words.strip(), name)

    def test_the_frame_block_states_root_filter_counts_and_commit(self):
        """A frame is filter AND moment; a number carrying one is not reproducible."""
        res = sw.sweep(TOKEN, root=self.root, frame=sw.WORKING_TREE_NO_VCS,
                       regex=False)
        block = res.frame_block()
        for label in ("root", "commit", "frame", "selection rule",
                      "filter applied", "files considered", "files searched",
                      "files skipped"):
            self.assertIn(label, block, block)


class FrameComparisonTests(unittest.TestCase):
    """Two frames are two measurements. Subtracting them is the mistake."""

    def setUp(self) -> None:
        self.tree = PlantedTree()
        self.addCleanup(self.tree.cleanup)
        self.a = sw.sweep(TOKEN, root=self.tree.root,
                          frame=sw.EVERYTHING_UNDER_ROOT, regex=False)
        self.b = sw.sweep(TOKEN, root=self.tree.root,
                          frame=sw.IGNORE_HONOURING, regex=False)

    def test_comparing_two_frames_raises_rather_than_answering(self):
        with self.assertRaises(sw.FrameMismatch):
            self.a.compare_to(self.b)
        with self.assertRaises(sw.FrameMismatch):
            _ = self.a == self.b

    def test_positive_control_same_frame_results_compare_fine(self):
        """Without this, a helper that raised on every comparison would pass."""
        again = sw.sweep(TOKEN, root=self.tree.root,
                         frame=sw.EVERYTHING_UNDER_ROOT, regex=False)
        self.assertEqual(0, self.a.compare_to(again))
        self.assertTrue(self.a == again)

    def test_differing_size_caps_are_also_a_different_measurement(self):
        capped = sw.sweep(TOKEN, root=self.tree.root,
                          frame=sw.EVERYTHING_UNDER_ROOT, regex=False,
                          size_cap=8)
        with self.assertRaises(sw.FrameMismatch):
            self.a.compare_to(capped)


ABSOLUTES = re.compile(
    r"\b(never|always|cannot|every|no longer|impossible|guaranteed)\b",
    re.IGNORECASE)
TEST_NAME = re.compile(r"\btest_[a-z0-9_]+")


def _unbacked_absolutes(source: str) -> list[str]:
    """Absolutes in prose whose paragraph names no test. L-76's rule, executed.

    A paragraph is a maximal run of non-blank lines. An absolute is backed
    when a `test_*` name appears in the same paragraph -- the claim then
    points at something that ran, rather than at the author's confidence.
    """
    offences: list[str] = []
    lineno = 0
    for para in re.split(r"\n\s*\n", source):
        start = lineno + 1
        lineno += para.count("\n") + 1
        if TEST_NAME.search(para):
            continue
        for i, line in enumerate(para.splitlines()):
            m = ABSOLUTES.search(line)
            if m:
                offences.append(f"line {start + i}: {m.group(0)!r} in {line.strip()!r}")
    return offences


class AbsoluteClaimTests(unittest.TestCase):
    """L-76: an absolute marks the place the author stopped testing."""

    SOURCE = (REPO / "scripts" / "sweep.py").read_text(encoding="utf-8")

    def test_positive_control_the_absolute_checker_catches_a_planted_one(self):
        """The control on the negative below: the checker can find something."""
        planted = "# this sweep can never miss a file\n"
        self.assertTrue(_unbacked_absolutes(planted),
                        "the absolute checker is blind, so its clean result "
                        "on sweep.py is not evidence of anything")
        self.assertFalse(
            _unbacked_absolutes("# never, and test_it_never_does proves it\n"),
            "a backed absolute was reported as an offence")

    def test_no_unbacked_absolute_in_sweep_source(self):
        offences = _unbacked_absolutes(self.SOURCE)
        self.assertEqual([], offences,
                         "scripts/sweep.py makes absolute claims with no "
                         "executed test named beside them:\n  "
                         + "\n  ".join(offences))

    def test_tests_named_in_sweep_source_exist_here(self):
        """A named test that does not exist is a worse claim than none."""
        named = set(TEST_NAME.findall(self.SOURCE))
        defined = set(TEST_NAME.findall(
            Path(__file__).read_text(encoding="utf-8")))
        missing = sorted(named - defined)
        self.assertEqual([], missing,
                         f"sweep.py cites tests that do not exist: {missing}")


class CommandLineTests(unittest.TestCase):
    """The CLI prints the frame, and its exit status carries the verdict."""

    def setUp(self) -> None:
        self.tree = PlantedTree()
        self.addCleanup(self.tree.cleanup)

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(REPO / "scripts" / "sweep.py"), *args],
            capture_output=True, text=True, check=False)

    def test_cli_without_a_frame_refuses_and_exits_two(self):
        proc = self._run(TOKEN, "--root", str(self.tree.root))
        self.assertEqual(2, proc.returncode, proc.stderr)
        self.assertIn("--frame", proc.stderr)

    def test_cli_prints_the_frame_block_with_its_hits(self):
        proc = self._run(TOKEN, "--root", str(self.tree.root),
                         "--frame", "everything", "-F")
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("FRAME", proc.stdout)
        self.assertIn("files considered", proc.stdout)
        self.assertIn("ignored_archive/case.log", proc.stdout)

    def test_cli_exit_status_distinguishes_zero_from_matches(self):
        proc = self._run("NO_SUCH_TOKEN_ANYWHERE", "--root", str(self.tree.root),
                         "--frame", "everything", "-F")
        self.assertEqual(1, proc.returncode, proc.stdout)
        self.assertIn("ZERO", proc.stdout)


if __name__ == "__main__":
    unittest.main()
