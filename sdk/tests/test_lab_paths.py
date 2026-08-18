"""`scripts/lab_paths.py` executed, not read.

WHY THIS FILE EXISTS
====================
`lab_paths` is the module MOVE_MAP section 9's batch 3 lands so that batches
4-8 edit ONE file instead of thirteen.  Every later batch trusts it.  A path
shim that is merely plausible is worse than none: it would hand every consumer
a path that is not there, and this repository has already measured what that
costs.  `scripts/check_absolutes.py`'s `audit(paths=)` filtered on suffix
before stat-ing, so a caller-named path that did not exist returned **PASS**;
executed against the pre-repair module, three of four nonexistent paths came
back CLEAN/exit 0, the outcome turning on the filename's suffix.  Repaired at
`b0ab070d`.

So the load-bearing half of this file is not "the table is right".  It is
`FailsClosed` and the must-not-match controls: a name that resolves to nothing
must raise or return UNKNOWN, and -- the control that makes that mean anything
-- a name that DOES resolve must not.  An instrument that always says UNKNOWN
passes the first half and is worthless (L-84).

THE THREE TREE STATES
=====================
`lab_paths` binds against the filesystem at import and reads `LAB_REPO` from
the environment, so the pre-move, mid-move and post-move trees are all
reachable from one test process by loading fresh module instances over
synthetic roots.  That is the property the batch plan needs: the same module
is correct at every batch boundary, with no edit between them.
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_TARGET = Path(os.environ.get("LAB_PATHS_PATH", _REPO / "scripts" / "lab_paths.py"))

_W = "demo-output/website"


def load(root: Path | None = None, name: str = "lab_paths_under_test"):
    """A fresh `lab_paths` bound to `root` (default: this repository)."""
    old = os.environ.get("LAB_REPO")
    if root is not None:
        os.environ["LAB_REPO"] = str(root)
    elif "LAB_REPO" in os.environ:
        del os.environ["LAB_REPO"]
    try:
        spec = importlib.util.spec_from_file_location(name, _TARGET)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        if old is None:
            os.environ.pop("LAB_REPO", None)
        else:
            os.environ["LAB_REPO"] = old


L = load()


def touch(root: Path, rel: str, body: str = "x") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)
    return p


class TreeCase(unittest.TestCase):
    """A synthetic tree per test.  Never the live repository."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="lab_paths_")
        self.root = Path(self.tmp)

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)


# ---------------------------------------------------------------------------


class TheTableIsWellFormed(unittest.TestCase):

    def test_names_are_unique(self):
        names = [m.name for m in L.MOVES]
        self.assertEqual(len(names), len(set(names)))

    def test_a_shorter_prefix_placed_first_is_refused_at_import(self):
        """The must-not-match control for `_check_prefix_order`.

        A longest-prefix table that somebody re-sorts alphabetically routes
        `demo-output/website/dafoam/x` to `web/dafoam/x` -- a wrong answer that
        looks right.  So the ordering is executed, not commented.
        """
        src = _TARGET.read_text()
        # Move the catch-all webroot row to the front of the moving block.
        row = ('    ("WEB", _W, "web", "R13"),\n')
        self.assertIn(row, src, "the WEB row moved; update this test")
        broken = src.replace(row, "")
        anchor = '    ("WEB_CLOSURE_HTML"'
        broken = broken.replace(anchor, row + anchor, 1)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "broken_lab_paths.py"
            p.write_text(broken)
            spec = importlib.util.spec_from_file_location("broken_lp", p)
            mod = importlib.util.module_from_spec(spec)
            with self.assertRaises(RuntimeError) as cm:
                spec.loader.exec_module(mod)
            self.assertIn("mis-ordered", str(cm.exception))

    def test_every_move_rule_of_section_2_2_is_represented(self):
        """R1-R25, and it is asked of `RULES` rather than of `MOVES`.

        R12, R16, R17, R20, R21 and R25 are regex rules in `_special`, not
        table rows, so a test that reads `MOVES` cannot see them -- and it did
        not: R16 and R17 were UNIMPLEMENTED for a whole batch while this test
        was green, and all 40 loose webroot files were being routed to `web/`
        instead of to `research/closure/{md,data}/`.  A coverage claim taken
        over the wrong collection is a coverage claim about the collection.
        """
        for r in ("R1", "R2", "R5", "R6", "R8", "R10", "R11", "R12", "R13",
                  "R14", "R15", "R16", "R17", "R18", "R19", "R20", "R21",
                  "R22", "R23", "R24", "R25"):
            self.assertIn(r, L.RULES, f"{r} is unimplemented in lab_paths")

    def test_the_rules_set_is_not_a_wish_list(self):
        """The must-not-match control for the test above.

        `RULES` is written by hand, so on its own it proves nothing: a name
        added to it without a rule behind it would turn the coverage test
        green.  Every rule id claimed must actually fire on some path.
        """
        witness = {
            "R12": "demo-output/duct.png",
            "R16": _W + "/ACTIVE_RESEARCH.md",
            "R17": _W + "/closure_challenge_round5_qcr.json",
            "R20": _W + "/campaign/F8_runs/log.simpleFoam",
            "R21": _W + "/campaign/RECORD.md",
            "R25": "docs/campaigns/F14-cooling-ladder/K0c_runs/x",
        }
        for rule, path in witness.items():
            with self.subTest(rule=rule):
                self.assertIsNotNone(L.redirect(path),
                                     f"{rule} is in RULES and fires on nothing")
        self.assertNotIn("R99", L.RULES)

    def test_dark_tree_destinations_agree_with_the_table(self):
        by_legacy = {m.legacy: m.target for m in L.MOVES}
        for name, legacy, target in L.DARK_TREES:
            if legacy in by_legacy:
                self.assertEqual(by_legacy[legacy], target,
                                 f"DARK_TREES and _MOVES disagree on {name}")


class Redirect(unittest.TestCase):

    def test_the_campaign_split_is_on_the_child_segment_not_a_prefix(self):
        """R20 and R21 both live under `campaign/`.  A prefix table cannot
        express the split, and one that silently gets it wrong routes 7,940
        files to the wrong root while looking correct."""
        self.assertEqual(
            L.redirect(_W + "/campaign/F8_runs/phase6_mrf/log.simpleFoam"),
            "verification/runs/F8_runs/phase6_mrf/log.simpleFoam")
        self.assertEqual(
            L.redirect(_W + "/campaign/D5_rsm_work/a/b"),
            "verification/runs/D5_rsm_work/a/b")
        self.assertEqual(
            L.redirect(_W + "/campaign/LADDER_V_TRIPLE_VERIFICATION.md"),
            "verification/campaign/LADDER_V_TRIPLE_VERIFICATION.md")

    def test_r21_preserves_the_campaign_segment(self):
        """MOVE_MAP section 6: 45 ladder records cite each other as
        `campaign/LADDER_V_*.md`.  The segment surviving is what keeps 95 of
        V10's path references from becoming a rewrite."""
        out = L.redirect(_W + "/campaign/LADDER_V_V7_RULING_2026-08-16.md")
        self.assertIn("/campaign/", "/" + out)

    def test_the_served_png_beats_the_campaign_split(self):
        """R13's fifth file sits under `campaign/` and must reach `web/`, with
        its `campaign/` segment kept, because `closure.html:350` reaches it
        relatively and flattening it would edit a live page for no gain."""
        png = _W + "/campaign/duct_secondary_flow_AR_7_validation_qcr.png"
        self.assertEqual(
            L.redirect(png),
            "web/campaign/duct_secondary_flow_AR_7_validation_qcr.png")

    def test_never_touch_trees_get_no_redirect(self):
        """X3.  `latex/` is its owner's and `motorbike-video/` is filming.
        The webroot's own prefix would otherwise sweep both into `web/`."""
        self.assertIsNone(L.redirect(_W + "/latex/paper.tex"))
        self.assertIsNone(L.redirect(_W + "/latex"))
        self.assertIsNone(L.redirect(_W + "/motorbike-video/clip.mp4"))

    def test_r12_loose_pngs_do_not_swallow_r10_and_r11(self):
        self.assertEqual(L.redirect("demo-output/duct.png"), "media/duct.png")
        self.assertEqual(L.redirect("demo-output/plots/a.png"),
                         "media/plots/a.png")
        self.assertEqual(L.redirect("demo-output/acts/act1/x.png"),
                         "media/acts/act1/x.png")

    def test_longest_prefix_wins_over_the_webroot_catch_all(self):
        for legacy, expect in (
                (_W + "/dafoam/f6a/x.json", "cases/dafoam/f6a/x.json"),
                (_W + "/agenda/proposals/p.json",
                 "research/agenda/proposals/p.json"),
                (_W + "/tmr-flatplate-finest-grids/g.json",
                 "cases/tmr/tmr-flatplate-finest-grids/g.json"),
                (_W + "/race-gui/index.png",
                 "research/race/race-gui/index.png"),
                (_W + "/wall/wall.json", "research/closure/data/wall.json"),
                (_W + "/closure.html", "web/closure.html"),
                (_W + "/anything-unclaimed.txt", "web/anything-unclaimed.txt")):
            with self.subTest(legacy=legacy):
                self.assertEqual(L.redirect(legacy), expect)

    def test_tmr_family_merge_does_not_collide(self):
        """Four sources become `cases/tmr`.  `tmr/` itself flattens; the three
        siblings keep their segment, so no two files land on one path."""
        self.assertEqual(L.redirect(_W + "/tmr/a.json"), "cases/tmr/a.json")
        self.assertEqual(L.redirect(_W + "/tmr-naca0012-transient-300cu/a.json"),
                         "cases/tmr/tmr-naca0012-transient-300cu/a.json")

    def test_the_r23_closure_merge_preserves_the_child_segment(self):
        """RATIFIED 2026-08-18, EXECUTING BATCH 5.

        `MOVE_MAP_2026-08-16.md` s2.2's R23 sends four `closure_*` source
        directories to `research/closure` without saying whether each keeps its
        own segment, and `MOVE_MAP_EXECUTION_2026-08-17.md` s4.3's worked
        example reads the OTHER way.  s5 rules that the child segment is
        preserved on every many-to-one merge, and s6 gives R21's reason: a
        preserved segment keeps relative citations alive.

        THE RATIFICATION IS NOT A PREFERENCE, IT IS A MEASUREMENT, and it is
        pinned here rather than asserted in prose.  Measured at `7a98c33d`
        immediately before the batch: the four sources hold 24 + 9 + 9 + 11 =
        53 tracked files over **35 distinct relative paths**, because
        `MANIFEST.json` and eight `test/*.csv` are contributed by three of the
        four submissions apiece.  Flattened into one namespace, 53 files land
        on 35 paths and **18 are silently overwritten** -- including all three
        round-over-round `MANIFEST.json`s, whose whole content is that they
        differ.  The two round-4 and round-1 directories even share a sorted
        path digest (`55e372ce9b626836`) while differing in bytes, so a
        path-set check alone would have called the merge clean.
        """
        for src, dst in (
                ("closure_eval", "research/closure/closure_eval"),
                ("closure_challenge_submission",
                 "research/closure/closure_challenge_submission"),
                ("closure_challenge_submission_round4",
                 "research/closure/closure_challenge_submission_round4"),
                ("closure_challenge_submission_round5",
                 "research/closure/closure_challenge_submission_round5")):
            with self.subTest(src=src):
                self.assertEqual(L.redirect(f"{_W}/{src}/MANIFEST.json"),
                                 f"{dst}/MANIFEST.json")
        # The same rule, the same way, on the other two many-to-one merges.
        self.assertEqual(L.redirect(_W + "/race-gui/app.js"),
                         "research/race/race-gui/app.js")
        self.assertEqual(L.redirect(_W + "/r2-coefficient-uq-flatplate/x.json"),
                         "research/uq/r2-coefficient-uq-flatplate/x.json")
        # MUST-NOT-MATCH CONTROL.  A `redirect` that appended the child segment
        # to everything would satisfy the six assertions above.  The parent of
        # a merge family flattens -- that is what makes it the parent.
        self.assertEqual(L.redirect(_W + "/race/benchmarks.md"),
                         "research/race/benchmarks.md")
        self.assertEqual(L.redirect(_W + "/tmr/a.json"), "cases/tmr/a.json")

    def test_roots_that_do_not_move_return_none(self):
        for p in ("sdk/chief_engineer/agenda.py", "models/curriculum/x.json",
                  "scripts/self_audit.py", "docs/DOCKET.md",
                  "mission-output/geometry-study/x", "dist/certonomous-demo/a",
                  "Stl_files/naca4412_wing.stl"):
            with self.subTest(p=p):
                self.assertIsNone(L.redirect(p))

    def test_docs_aws_moves_but_the_rest_of_docs_does_not(self):
        self.assertEqual(L.redirect("docs/aws/EC2.md"), "ops/aws/EC2.md")
        self.assertIsNone(L.redirect("docs/charters/X.md"))

    def test_scripts_launcher_dirs_move_but_scripts_does_not(self):
        self.assertEqual(L.redirect("scripts/installed/pre-commit"),
                         "ops/installed/pre-commit")
        self.assertIsNone(L.redirect("scripts/check_absolutes.py"))

    def test_redirect_does_not_fire_twice(self):
        """A successor must not itself redirect, or a second pass over the
        corpus would move everything again."""
        for p in (_W + "/dafoam/x", _W + "/campaign/F8_runs/y",
                  _W + "/closure.html", "demo-output/plots/a.png"):
            once = L.redirect(p)
            with self.subTest(p=p):
                self.assertIsNotNone(once)
                self.assertIsNone(L.redirect(once))

    def test_r25_sends_a_docs_campaign_run_tree_to_verification_runs(self):
        """RULING 1 of 2026-08-17: a run tree is classified by WHAT IT IS.

        `docs/campaigns/<campaign>/*_{runs,sensitivity}/**` is an OpenFOAM run
        archive sitting in the documentation tree because of an authoring
        accident, and it follows R20's destination.
        """
        self.assertEqual(
            L.redirect("docs/campaigns/F14-cooling-ladder/K0c_runs/c/0.orig/T"),
            "verification/runs/F14-cooling-ladder/K0c_runs/c/0.orig/T")
        self.assertEqual(
            L.redirect("docs/campaigns/F14-cooling-ladder/K0b_mesh_sensitivity"),
            "verification/runs/F14-cooling-ladder/K0b_mesh_sensitivity")

    def test_r25_preserves_the_campaign_segment(self):
        """The sub-decision the ruling flagged as the owner's.

        `verification/runs/` is flat and already holds 27 `*_runs`/`*_work`
        names; `docs/campaigns/` is per-campaign.  Two campaigns each landing
        a `K0c_runs` collide the moment the second one arrives.
        """
        a = L.redirect("docs/campaigns/F14-cooling-ladder/K0c_runs/x")
        b = L.redirect("docs/campaigns/ANOTHER-CAMPAIGN/K0c_runs/x")
        self.assertNotEqual(a, b, "the campaign segment was flattened away")
        self.assertIn("/F14-cooling-ladder/", "/" + a)

    def test_the_must_not_match_control_for_r25(self):
        """R7 keeps the campaign's DOCUMENTATION, and the ruling says so.

        Without this, an R25 written as "everything under docs/campaigns/"
        would satisfy both tests above and move 31 gate specifications,
        results documents and reference tables out of `docs/`.
        """
        for keep in ("docs/campaigns/F14-cooling-ladder/README.md",
                     "docs/campaigns/F14-cooling-ladder/K0c_RESULTS.md",
                     "docs/campaigns/F14-cooling-ladder/reference-data/M.md",
                     "docs/campaigns/F14-cooling-ladder/compute_reference_metrics.py"):
            with self.subTest(keep=keep):
                self.assertIsNone(L.redirect(keep))

    def test_r25_inverts_without_being_swallowed_by_r20(self):
        """`verification/runs/` holds both, and only the first segment tells
        them apart: R20 puts a `*_runs`/`*_work` TREE name there and R25 puts
        a CAMPAIGN name.  Reading an R25 path back as R20's would rewrite a
        citation to `docs/campaigns/...` as `demo-output/website/campaign/...`
        -- a path that never existed."""
        self.assertEqual(
            L.unredirect("verification/runs/F14-cooling-ladder/K0c_runs/x"),
            "docs/campaigns/F14-cooling-ladder/K0c_runs/x")
        self.assertEqual(
            L.unredirect("verification/runs/F8_runs/phase6_mrf/log.simpleFoam"),
            _W + "/campaign/F8_runs/phase6_mrf/log.simpleFoam")

    def test_r16_and_r17_take_the_loose_webroot_files_out_of_the_webroot(self):
        """MEASURED MISSING 2026-08-17: 19 `*.md` and 21 `*.json` sitting
        loose in the webroot were falling through to the `WEB` catch-all and
        being routed to `web/`, which contradicts R13's own "the webroot is
        five files" and would have pointed every closure generator's output
        at the wrong root."""
        self.assertEqual(L.redirect(_W + "/ACTIVE_RESEARCH.md"),
                         "research/closure/md/ACTIVE_RESEARCH.md")
        self.assertEqual(
            L.redirect(_W + "/closure_challenge_round5_qcr.json"),
            "research/closure/data/closure_challenge_round5_qcr.json")

    def test_the_must_not_match_control_for_r16_r17(self):
        """Three ways the loose-file rule could over-reach, each checked.

        A rule written as "anything directly under the webroot" would take
        the served HTML pages (R13), and one that ignored the table would
        take `benchmarks.json` and `benchmarks.png` away from R14/R15 -- same
        destination for the JSON, WRONG destination for the PNG.
        """
        self.assertEqual(L.redirect(_W + "/closure.html"), "web/closure.html")
        self.assertEqual(L.redirect(_W + "/anything-unclaimed.txt"),
                         "web/anything-unclaimed.txt")
        self.assertEqual(L.redirect(_W + "/benchmarks.png"),
                         "research/closure/plots/benchmarks.png")
        self.assertEqual(L.redirect(_W + "/benchmarks.json"),
                         "research/closure/data/benchmarks.json")
        # not loose: one level down is R18's, and it keeps its own row
        self.assertEqual(L.redirect(_W + "/wall/wall.json"),
                         "research/closure/data/wall.json")

    def test_the_webroot_keeps_exactly_the_five_served_files(self):
        """R13 says the webroot is five files.  Run over the tracked corpus,
        because that is the claim -- not over an example."""
        landing = {p: L.redirect(p) for p in TrackedCorpus.tracked()}
        web = sorted(p for p, out in landing.items()
                     if out is not None and out.split("/")[0] == "web")
        self.assertEqual(len(web), 5, f"web/ would hold {len(web)}: {web}")
        self.assertEqual(set(web), set(L.SERVED_SET))

    def test_unredirect_inverts_redirect(self):
        cases = [m.legacy + "/leaf.txt" for m in L.MOVES
                 if m.moves and m.name not in ("CAMPAIGN", "RUNS")
                 and not m.legacy.endswith((".md", ".html", ".json", ".png"))]
        cases += [_W + "/campaign/F8_runs/a/b",
                  _W + "/campaign/RECORD.md",
                  "demo-output/loose.png",
                  _W + "/closure.html"]
        self.assertGreater(len(cases), 20)
        for p in cases:
            fwd = L.redirect(p)
            with self.subTest(p=p):
                self.assertIsNotNone(fwd, f"no redirect for {p}")
                self.assertEqual(L.unredirect(fwd), p)


_TRACKED: list[str] | None = None


def tracked_paths() -> list[str]:
    """HEAD's tree, NEVER the index (docket D274).

    `git ls-files` reads the INDEX, and this lab's own commit protocol builds
    every commit under a private `GIT_INDEX_FILE` and never writes the shared
    one -- so a file another agent landed an hour ago is in HEAD and invisible
    to `ls-files` until somebody runs `git add`.  Measured at `f40f6ef5`:
    13,814 against 13,974.  A corpus-wide assertion taken over the smaller
    frame is an assertion about a stale corpus, and this file's own sweeps are
    exactly the assertions that must not be.
    """
    global _TRACKED
    if _TRACKED is None:
        cp = subprocess.run(
            ["git", "-C", str(_REPO), "ls-tree", "-r", "-z", "--name-only",
             "HEAD"], capture_output=True)
        _TRACKED = [p.decode("utf-8", "surrogateescape")
                    for p in cp.stdout.split(b"\0") if p]
    return _TRACKED


class TrackedCorpus:
    tracked = staticmethod(tracked_paths)


class TheCorpusRoutesSomewhereReal(unittest.TestCase):
    """Run over every tracked path, not over hand-picked examples."""

    @classmethod
    def setUpClass(cls):
        cls.tracked = tracked_paths()

    def test_there_are_tracked_files_to_test_against(self):
        # A sweep over an empty corpus passes every assertion below it.
        self.assertGreater(len(self.tracked), 1000)

    def test_every_redirected_path_lands_under_a_target_tree_root(self):
        """MOVE_MAP section 1 names the target tree.  A table row that routes
        a file outside it is a typo that no example-based test would catch."""
        allowed = {"sdk", "scripts", "ops", "docs", "cases", "research",
                   "verification", "web", "media", "evidence", "models",
                   "dist", "Stl_files", "demo-output"}
        bad = []
        for p in self.tracked:
            out = L.redirect(p)
            if out is not None and out.split("/")[0] not in allowed:
                bad.append((p, out))
        self.assertEqual(bad[:20], [], f"{len(bad)} paths route off-tree")

    def test_no_two_tracked_paths_collide_on_one_successor(self):
        seen: dict[str, str] = {}
        clash = []
        for p in self.tracked:
            out = L.redirect(p)
            if out is None:
                continue
            if out in seen:
                clash.append((seen[out], p, out))
            seen[out] = p
        self.assertEqual(clash[:20], [], f"{len(clash)} successor collisions")

    def test_the_webroot_is_fully_classified(self):
        """Every tracked file under the webroot must reach a rule.  A `None`
        here is a file the reorganisation would leave behind silently."""
        unrouted = [p for p in self.tracked
                    if p.startswith(_W + "/") and L.redirect(p) is None]
        # X3's never-touch trees are the only legitimate `None`.
        stray = [p for p in unrouted
                 if not p.startswith((_W + "/latex/", _W + "/motorbike-video/"))]
        self.assertEqual(stray[:20], [], f"{len(stray)} unrouted webroot files")
        self.assertGreater(len(unrouted), 0, "X3's trees should be unrouted")


class Binding(TreeCase):

    def test_legacy_only_binds_legacy(self):
        (self.root / _W / "dafoam").mkdir(parents=True)
        m = load(self.root, "lp_legacy")
        self.assertEqual(m.state("DAFOAM"), "legacy")
        self.assertEqual(m.DAFOAM, self.root / _W / "dafoam")

    def test_target_only_binds_target(self):
        (self.root / "cases" / "dafoam").mkdir(parents=True)
        m = load(self.root, "lp_moved")
        self.assertEqual(m.state("DAFOAM"), "moved")
        self.assertEqual(m.DAFOAM, self.root / "cases" / "dafoam")

    def test_both_present_prefers_the_target_and_is_reported(self):
        """Mid-`mv` both exist.  Preferring the target is what makes the batch
        after a move read the new tree; reporting it is what stops a half-moved
        region from looking settled."""
        (self.root / _W / "dafoam").mkdir(parents=True)
        (self.root / "cases" / "dafoam").mkdir(parents=True)
        m = load(self.root, "lp_both")
        self.assertEqual(m.state("DAFOAM"), "both")
        self.assertEqual(m.DAFOAM, self.root / "cases" / "dafoam")
        self.assertIn("DAFOAM", m.AMBIGUOUS)

    def test_neither_present_is_absent_and_unresolved(self):
        m = load(self.root, "lp_absent")
        self.assertEqual(m.state("DAFOAM"), "absent")
        self.assertIn("DAFOAM", m.UNRESOLVED)

    def test_a_partially_moved_tree_reports_each_region_separately(self):
        """Batch 6 lands `cases/`; batch 7 has not run.  Both answers must be
        right in the same process."""
        (self.root / "cases" / "dafoam").mkdir(parents=True)
        (self.root / _W / "campaign").mkdir(parents=True)
        m = load(self.root, "lp_partial")
        self.assertEqual(m.state("DAFOAM"), "moved")
        self.assertEqual(m.state("CAMPAIGN"), "legacy")


class FailsClosed(TreeCase):
    """The load-bearing half.  A root that is not there must never read PASS."""

    def test_require_raises_rather_than_returning_a_path_that_is_not_there(self):
        m = load(self.root, "lp_fc1")
        with self.assertRaises(FileNotFoundError) as cm:
            m.require("DAFOAM")
        self.assertIn("must not report PASS", str(cm.exception))

    def test_unknown_reason_names_the_missing_roots(self):
        m = load(self.root, "lp_fc2")
        why = m.unknown_reason("DAFOAM", "AGENDA")
        self.assertIsNotNone(why)
        self.assertTrue(why.startswith("UNKNOWN because"))
        self.assertIn("DAFOAM", why)
        self.assertIn("AGENDA", why)

    def test_the_must_not_match_control(self):
        """A shim that always answered UNKNOWN would pass every assertion
        above and be worthless.  A root that IS on disk must come back clean,
        and `require` must return it."""
        (self.root / _W / "dafoam").mkdir(parents=True)
        m = load(self.root, "lp_fc3")
        self.assertIsNone(m.unknown_reason("DAFOAM"))
        self.assertTrue(m.resolved("DAFOAM"))
        self.assertEqual(m.require("DAFOAM"), self.root / _W / "dafoam")

    def test_resolve_returns_none_for_something_that_never_existed(self):
        """MOVE_MAP section 4.2: the redirect resolver keeps the guard honest.
        A citation to a path that never existed must still fail."""
        (self.root / _W / "dafoam").mkdir(parents=True)
        m = load(self.root, "lp_fc4")
        self.assertIsNone(m.resolve("demo-output/website/never_existed/x.md"))
        self.assertIsNone(m.resolve("cases/never_existed/x.md"))

    def test_resolve_finds_a_citation_at_its_successor_after_the_move(self):
        touch(self.root, "cases/dafoam/f6a/RESULT.md")
        m = load(self.root, "lp_fc5")
        got = m.resolve(_W + "/dafoam/f6a/RESULT.md")
        self.assertIsNotNone(got, "a pre-move citation must survive the move")
        self.assertEqual(got, self.root / "cases/dafoam/f6a/RESULT.md")

    def test_resolve_finds_a_citation_at_its_predecessor_before_the_move(self):
        touch(self.root, _W + "/dafoam/f6a/RESULT.md")
        m = load(self.root, "lp_fc6")
        got = m.resolve("cases/dafoam/f6a/RESULT.md")
        self.assertEqual(got, self.root / _W / "dafoam/f6a/RESULT.md")

    def test_an_absent_root_does_not_silently_shrink_a_record_sweep(self):
        """`RECORD_ROOTS()` drops absent roots -- correct mid-move -- so the
        caller that must not be blinded pairs it with `unknown_reason`.  This
        pins that the pairing actually reports."""
        m = load(self.root, "lp_fc7")
        self.assertEqual(m.RECORD_ROOTS(), ())
        self.assertIsNotNone(m.unknown_reason(*m.RECORD_ROOT_NAMES))


class ItReplacesWhatItClaimsTo(TreeCase):
    """Pinned against the live modules, so drift in either one is caught."""

    #: The seven roots `self_audit.py:4309`'s whitelist named at `4d7c195a`,
    #: which is what `check_evidence_paths_exist`'s reach was measured against.
    _SEVEN = ("demo-output/", "sdk/", "scripts/", "models/", "mission-output/",
              "docs/", "dist/")

    def test_sweep_roots_never_loses_one_of_self_audit_4309s_seven(self):
        """`self_audit.py`'s `check_evidence_paths_exist` whitelist.

        Batch 3b made `self_audit.py` CALL this function instead of carrying
        its own copy, so there is no longer a second spelling to read out of
        its source and diff against -- and a test that kept reading for one
        would go green on the absence of what it was checking.

        AMENDED AT BATCH 4, 2026-08-18.  This asserted EQUALITY with the seven
        and was correct only before the first move landed.  Batch 4 creates
        `media/` and `ops/`, and emitting a destination root the moment it
        exists is the whole point of this function -- a citation written after
        the move has to resolve while a citation written before it still does.
        So equality was the wrong pin: it reddens on the function working.

        What is load-bearing is that a root never LEAVES.  A whitelist that
        silently shrinks is `check_evidence_paths_exist` scanning fewer
        documents and passing, which is this corpus's most repeated failure and
        the reason batch 9 exists.  So: the seven are all still there, in
        order, and anything added is a real directory that some rule sends
        files to.
        """
        got = L.SWEEP_ROOTS()
        for root in self._SEVEN:
            with self.subTest(root=root):
                self.assertIn(root, got, f"{root} left the whitelist")
        self.assertEqual(tuple(r for r in got if r in self._SEVEN),
                         self._SEVEN, "the seven changed order")
        targets = {m.target.split("/")[0] + "/" for m in L.MOVES}
        for extra in (r for r in got if r not in self._SEVEN):
            with self.subTest(extra=extra):
                self.assertTrue((L.REPO / extra).is_dir(),
                                f"{extra} is not on disk")
                self.assertIn(extra, targets,
                              f"{extra} is no rule's destination")

    def test_sweep_roots_does_not_emit_a_root_that_is_not_there(self):
        """The must-not-match control for the test above.

        Without it, a `SWEEP_ROOTS` that returned every spelling it knows --
        including `web/`, `cases/`, `research/` and `verification/`, none of
        which exists until batches 5 to 8 -- would satisfy every assertion
        above and hand `check_evidence_paths_exist` four prefixes that match
        nothing.
        """
        got = L.SWEEP_ROOTS()
        for absent in ("web/", "cases/", "research/", "verification/",
                       "evidence/"):
            if (L.REPO / absent).is_dir():
                continue
            with self.subTest(absent=absent):
                self.assertNotIn(absent, got)

    def test_self_audit_actually_calls_the_shared_roots_and_pages(self):
        """The other half: a value that matches proves nothing if nobody
        reads it.  Both call sites are asserted in the module's own source."""
        src = (_REPO / "scripts" / "self_audit.py").read_text()
        self.assertIn("roots = lab_paths.SWEEP_ROOTS()", src)
        self.assertIn("lab_paths.BUNDLE_PAGES()", src)
        self.assertIn("lab_paths.RECORD_ROOTS()", src)
        self.assertNotIn('roots = ("demo-output/"', src)

    def test_bundle_pages_reproduces_self_audit_6484_before_the_move(self):
        """The triple `_BUNDLE_PAGES` held at `4d7c195a`, value for value.

        The member path inside the ZIP is not the repo path, which is the
        whole reason the triple exists, and `build_laptop_bundle.py:53`'s
        deliberate omission of `shoot.html` is preserved.
        """
        self.assertEqual(
            [(label, str(p.relative_to(L.REPO)), member)
             for label, p, member in L.BUNDLE_PAGES()],
            [("closure.html", "demo-output/website/closure.html",
              "site/closure.html"),
             ("benchmarks.html", "demo-output/website/benchmarks.html",
              "site/benchmarks.html"),
             ("wall.html", "demo-output/website/wall/wall.html",
              "site/wall/wall.html")])

    def test_record_documents_never_loses_a_record_the_rglob_reached(self):
        """`self_audit._record_documents()` replaces `WEB.rglob("*.md")`.

        AMENDED 2026-08-18, EXECUTING BATCH 5, AND THE OLD PIN WAS THE WRONG
        ONE.  It asserted EQUALITY with `WEB.rglob("*.md")`, which held only
        while every record root was still under the one webroot.  Batch 5 is
        the first batch that takes records OUT of it -- R16's 19 loose `*.md`
        to `research/closure/md/`, R23's `agenda/`, `race/` and the four
        `closure_*` trees -- so equality now reddens on the function doing
        exactly what it exists to do.  That is batch 4's finding on
        `test_sweep_roots_reproduces_self_audit_4309_before_the_move`,
        recurring one instrument over.

        WHAT IS LOAD-BEARING IS THE DIRECTION.  A sweep that GAINS a root
        walks more documents; a sweep that LOSES one scans fewer and passes,
        which is `check_evidence_paths_exist` reporting a clean bill of health
        on a corpus it no longer reads -- this repository's most repeated
        failure.  So: nothing the rglob still reaches may be missing, every
        record that LEFT the webroot must still be reached, nothing may be
        double-counted, and the must-not-match control asserts the list is not
        merely everything.
        """
        import importlib.util
        import sys as _s
        spec = importlib.util.spec_from_file_location(
            "_self_audit_under_test", _REPO / "scripts" / "self_audit.py")
        mod = importlib.util.module_from_spec(spec)
        _s.modules["_self_audit_under_test"] = mod
        try:
            spec.loader.exec_module(mod)
            got = mod._record_documents()
            web = sorted(mod.WEB.rglob("*.md"))
            self.assertGreater(len(got), 100, "the corpus is empty; nothing "
                                              "below this line means anything")
            # 1. NOTHING IS LOST.  Everything still under the webroot is here.
            self.assertEqual([], [p for p in web if p not in set(got)],
                             "the record sweep no longer reaches a document "
                             "the webroot rglob does")
            # 2. NOTHING IS DOUBLE-COUNTED.  A root inside another root would
            #    report every finding in it twice.
            self.assertEqual(len(got), len(set(got)), "a record is reached "
                                                      "twice; the roots overlap")
            # 3. EVERY EXTRA IS A REAL RECORD UNDER A REAL RULE DESTINATION.
            roots = L.RECORD_ROOTS()
            for p in got:
                if p in set(web):
                    continue
                self.assertTrue(p.is_file() and p.suffix == ".md", p)
                self.assertTrue(any(r == p or r in p.parents for r in roots), p)
            # 4. THE BATCH-5 ARM, and it is the reason this test was amended.
            #    A record that has LEFT the webroot is still swept.  Skipped
            #    before the batch lands, named rather than silently passing.
            moved = [L.resolve("demo-output/website/ACTIVE_RESEARCH.md"),
                     L.resolve("demo-output/website/CLOSURE_CHALLENGE_STATUS.md")]
            for m in moved:
                if m is None or str(m).find("/research/") < 0:
                    self.skipTest("batch 5 has not landed; the R16 records are "
                                  "still under the webroot and arm 1 covers them")
            for m in moved:
                self.assertIn(m, set(got),
                              f"{m} left the webroot and the record sweep no "
                              f"longer reaches it")
            # 5. MUST-NOT-MATCH CONTROL.  A sweep that returned every `*.md`
            #    in the repository would satisfy all four arms above.
            self.assertNotIn(_REPO / "docs" / "LESSONS.md", set(got),
                             "the record sweep has stopped selecting")
        finally:
            _s.modules.pop("_self_audit_under_test", None)

    def test_web_file_answers_where_a_file_that_does_not_exist_yet_goes(self):
        """R16/R17's files are mostly GENERATOR OUTPUT, and a generator names
        its output before the output is there.  `resolve()` returns None for
        that, which is the wrong answer for a write.  Once the destination
        DIRECTORY exists, a not-yet-written file belongs at the successor."""
        touch(self.root, _W + "/keep.md")
        (self.root / "research" / "closure" / "data").mkdir(parents=True)
        m = load(self.root, "lp_webfile")
        self.assertEqual(m.web_file("brand_new_output.json"),
                         self.root / "research/closure/data/brand_new_output.json")

    def test_web_file_prefers_the_side_the_file_is_actually_on(self):
        """The must-not-match control.  A `web_file` that always answered
        with the successor would satisfy the test above and send every
        pre-move reader to a path with nothing in it."""
        touch(self.root, _W + "/closure_challenge_x.json")
        m = load(self.root, "lp_webfile2")
        self.assertEqual(m.web_file("closure_challenge_x.json"),
                         self.root / _W / "closure_challenge_x.json")

    def test_submission_packages_finds_all_three_on_whichever_side_they_are(self):
        """Replaces `self_audit.py`'s `WEB.glob("closure_challenge_submission*")`.

        AMENDED 2026-08-18, EXECUTING BATCH 5.  It asserted EQUALITY with that
        glob whenever the webroot exists, and the whole reason the accessor was
        written is stated in its own docstring: R23 scatters the three into
        `research/closure/`, after which the glob finds nothing.  The webroot
        still exists after batch 5 -- it keeps 4,487 tracked files until
        batch 8 -- so the equality arm fired against an empty glob and reddened
        on the accessor doing its job.  Equality with the thing being replaced
        is only ever a PRE-move pin.

        What is load-bearing is that all three are found wherever they are, and
        that the accessor is still counting rather than reciting -- which is
        `test_submission_packages_is_not_a_hardcoded_three` directly below.
        """
        got = [p.name for p in L.SUBMISSION_PACKAGES()]
        self.assertEqual(3, len(got), got)
        self.assertEqual(sorted(got), got, "the accessor must return sorted")
        for name in ("closure_challenge_submission",
                     "closure_challenge_submission_round4",
                     "closure_challenge_submission_round5"):
            self.assertIn(name, got)
        for p in L.SUBMISSION_PACKAGES():
            self.assertTrue(p.is_dir(), p)
        # PRE-MOVE ARM, kept: while they are still under the webroot the
        # accessor must reproduce the glob it replaces, exactly.
        web = L.REPO / _W
        legacy = sorted(p.name for p in
                        web.glob("closure_challenge_submission*")) \
            if web.is_dir() else []
        if legacy:
            self.assertEqual(got, legacy)

    def test_submission_packages_is_not_a_hardcoded_three(self):
        """The control: an accessor that returned three names unconditionally
        would satisfy the test above and would keep reporting three after the
        packages moved and were not found."""
        m = load(self.root, "lp_pkgs")
        self.assertEqual(m.SUBMISSION_PACKAGES(), ())

    def test_run_archive_finds_an_r25_tree_under_its_campaign(self):
        """R25's trees are one segment deeper than R20's, so the accessor
        that answers "where is run archive X" has to know about the campaign
        namespace or it returns None for 490 files."""
        touch(self.root, "docs/campaigns/F14-cooling-ladder/K0c_runs/c/log.x")
        m = load(self.root, "lp_ra")
        self.assertEqual(m.run_archive("K0c_runs", "F14-cooling-ladder"),
                         self.root / "docs/campaigns/F14-cooling-ladder/K0c_runs")
        self.assertEqual(m.run_archive("K0c_runs"),
                         self.root / "docs/campaigns/F14-cooling-ladder/K0c_runs")
        self.assertIsNone(m.run_archive("NO_SUCH_runs"))

    def test_served_set_is_the_five_files_of_section_3_and_all_exist(self):
        self.assertEqual(len(L.SERVED_SET), 5)
        for rel in L.SERVED_SET:
            with self.subTest(rel=rel):
                self.assertIsNotNone(L.resolve(rel), f"{rel} is not on disk")

    def test_record_roots_covers_every_record_the_rglob_reached(self):
        """`WEB.rglob("*.md")` had no single successor.  Before the move the
        replacement must cover exactly what the rglob did; the dedup must not
        make it walk the webroot twice."""
        roots = L.RECORD_ROOTS()
        self.assertGreater(len(roots), 0)
        for a in roots:
            for b in roots:
                if a is not b:
                    self.assertNotIn(a, b.parents,
                                     f"{a} is inside {b}: double-counted")
        web = L.REPO / _W
        if web.exists():
            self.assertTrue(any(r == web or r in web.parents
                                or web in r.parents for r in roots))

    def test_the_solve_registry_constant_names_the_tree_four_modules_name(self):
        """MOVE_MAP section 4.3 names four consumers of the 1.51 GB tree that
        `git mv` cannot move.  If the constant here and what those modules
        name ever disagree, the hand-carry lands it where nothing looks.

        Batch 3b converted the three Python ones to IMPORT the constant, which
        is strictly stronger than agreeing with it -- they cannot disagree.
        `launch_solve.sh` is shell and cannot import, so it still carries the
        literal and is still checked as one.
        """
        legacy = str(L.MOVES[[m.name for m in L.MOVES].index("SOLVE_REGISTRY")].legacy)
        for rel in ("scripts/dispatch_queue.py", "scripts/check_convergence_sweep.py",
                    "scripts/contention_audit.py"):
            with self.subTest(rel=rel):
                src = (_REPO / rel).read_text()
                self.assertIn("lab_paths.SOLVE_REGISTRY", src,
                              f"{rel} stopped importing the constant")
                # Prose may still narrate the old path -- these are records
                # as much as code.  What must be gone is the CODE-level
                # re-spelling, which is the pattern the module exists to end.
                self.assertNotIn('"solve_registry"', src,
                                 f"{rel} still builds the path from segments "
                                 f"as well as importing the constant")
        shell = (_REPO / "scripts" / "launch_solve.sh").read_text()
        self.assertIn(legacy, shell, "launch_solve.sh no longer names "
                                     + legacy)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
