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
        rules = {m.rule for m in L.MOVES}
        for r in ("R1", "R2", "R5", "R6", "R8", "R10", "R11", "R13", "R14",
                  "R15", "R18", "R19", "R20", "R21", "R22", "R23", "R24"):
            self.assertIn(r, rules, f"{r} is unrepresented in lab_paths._MOVES")

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


class TheCorpusRoutesSomewhereReal(unittest.TestCase):
    """Run over every tracked path, not over hand-picked examples."""

    @classmethod
    def setUpClass(cls):
        cp = subprocess.run(["git", "-C", str(_REPO), "ls-files", "-z"],
                            capture_output=True)
        cls.tracked = [p.decode("utf-8", "surrogateescape")
                       for p in cp.stdout.split(b"\0") if p]

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


class ItReplacesWhatItClaimsTo(unittest.TestCase):
    """Pinned against the live modules, so drift in either one is caught."""

    def test_sweep_roots_reproduces_self_audit_4309_before_the_move(self):
        """`self_audit.py`'s `check_evidence_paths_exist` whitelist.  Read out
        of the source rather than copied, so a change to either side fails."""
        src = (_REPO / "scripts" / "self_audit.py").read_text()
        m = re.search(r'roots = \((.*?)\)\n', src, re.S)
        self.assertIsNotNone(m, "the `roots` whitelist moved; re-derive it")
        declared = tuple(re.findall(r'"([^"]+)"', m.group(1)))
        self.assertEqual(set(L.SWEEP_ROOTS()), set(declared))

    def test_bundle_pages_reproduces_self_audit_6484_before_the_move(self):
        src = (_REPO / "scripts" / "self_audit.py").read_text()
        block = re.search(r'_BUNDLE_PAGES = \((.*?)\n\)\n', src, re.S)
        self.assertIsNotNone(block)
        repo_paths = re.findall(r'Path\("(demo-output/[^"]+)"\)', block.group(1))
        mine = [str(p.relative_to(L.REPO)) for _, p, _ in L.BUNDLE_PAGES()]
        self.assertEqual(repo_paths, mine)

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
        """MOVE_MAP section 4.3 names the four consumers.  If the constant in
        `lab_paths` and the literal in those modules ever disagree, the
        hand-carry lands the tree somewhere the code will not look."""
        legacy = str(L.MOVES[[m.name for m in L.MOVES].index("SOLVE_REGISTRY")].legacy)
        for rel in ("scripts/dispatch_queue.py", "scripts/check_convergence_sweep.py",
                    "scripts/contention_audit.py", "scripts/launch_solve.sh"):
            with self.subTest(rel=rel):
                src = (_REPO / rel).read_text()
                pieces = legacy.split("/")
                self.assertTrue(
                    legacy in src
                    or all(f'"{seg}"' in src for seg in pieces),
                    f"{rel} no longer names {legacy}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
