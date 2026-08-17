"""`scripts/hand_carry.py` executed against synthetic trees.

WHY THIS FILE EXISTS
====================
`hand_carry` is the only thing standing between the reorganisation and 1.51 GB
that goes missing without a single red line anywhere.  `git mv` will not move a
directory holding no tracked file; the rule set of MOVE_MAP section 2 was built
by classifying TRACKED paths, so such a directory appears in no rule; and the
mechanical prefix rewrite of section 4.3 moves the CONSTANT that names it
regardless.  Constant in the new tree, files in the old one, everything green.

Two properties are load-bearing and both are tested with a must-not-match
control beside them:

  * the DERIVATION separates "git mv will never reach this" from "this rides
    along on an ancestor's rename".  Getting that backwards either buries the
    three trees that matter under nine hundred that do not, or -- far worse --
    calls a stranded tree carried.
  * the VERIFICATION reddens.  A carry whose after-check cannot fail is a
    carry nobody checked, which is the failure mode by name.  So every check
    is exercised by planting the discrepancy it is supposed to catch.

The tests build their own git repositories under `tempfile`.  Nothing here
reads or writes the live tree except the two derivation classes at the end,
which only read.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_TARGET = Path(os.environ.get("HAND_CARRY_PATH",
                              _REPO / "scripts" / "hand_carry.py"))
PASS, FAIL, UNKNOWN = 0, 1, 3
_W = "demo-output/website"


def load(root: Path, name: str):
    """A fresh `hand_carry` bound to `root`."""
    old = os.environ.get("LAB_REPO")
    os.environ["LAB_REPO"] = str(root)
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


def git(root: Path, *args: str):
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True)


def write(root: Path, rel: str, body: str = "x", age: float = 10_000) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)
    t = time.time() - age
    os.utime(p, (t, t))
    return p


class RepoCase(unittest.TestCase):
    """A fresh repository per test."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="hand_carry_")
        self.root = Path(self.tmp)
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.email", "t@t")
        git(self.root, "config", "user.name", "t")
        write(self.root, "README.md", "seed")
        git(self.root, "add", "README.md")
        git(self.root, "commit", "-qm", "seed")
        self.hc = None

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def mod(self, name: str | None = None):
        return load(self.root, name or ("hc_" + self.id().rsplit(".", 1)[-1]))

    def commit(self, *rels: str) -> None:
        git(self.root, "add", "--", *rels)
        git(self.root, "commit", "-qm", "add")

    def plan(self, hc, quiet: int = 0) -> dict:
        p = hc.build_plan(quiet)
        self.manifest = self.root.parent / (self.root.name + ".plan.json")
        self.manifest.write_text(json.dumps(p))
        return p


# ---------------------------------------------------------------------------


class Derivation(RepoCase):

    def test_a_gitignored_only_tree_under_a_split_parent_is_hand_carry(self):
        """`campaign/` splits under R20/R21, so it is never renamed as a unit
        and nothing beneath it rides anywhere.  This is `THERMAL_K0_runs`."""
        write(self.root, _W + "/campaign/RECORD.md")
        self.commit(_W + "/campaign/RECORD.md")
        write(self.root, _W + "/campaign/K0_runs/a/log.foam")
        write(self.root, _W + "/campaign/K0_runs/b/log.foam")
        hc = self.mod()
        d = hc.derive()
        carry = {r["source"]: r for r in d["carry"]}
        self.assertIn(_W + "/campaign/K0_runs", carry)
        self.assertEqual(carry[_W + "/campaign/K0_runs"]["dest"],
                         "verification/runs/K0_runs")
        self.assertEqual(carry[_W + "/campaign/K0_runs"]["files"], 2)

    def test_the_must_not_match_control_a_tracked_tree_is_not_hand_carry(self):
        """A directory holding a tracked file is moved by `git mv`.  Listing it
        here would have the mover hand-move a tree git is about to rename,
        which lands it twice or not at all."""
        write(self.root, _W + "/campaign/K0_runs/a/case.json")
        self.commit(_W + "/campaign/K0_runs/a/case.json")
        write(self.root, _W + "/campaign/K0_runs/a/log.foam")
        hc = self.mod()
        srcs = {r["source"] for r in hc.derive()["carry"]}
        self.assertNotIn(_W + "/campaign/K0_runs", srcs)

    def test_a_dark_subtree_under_a_clean_directory_move_rides_along(self):
        """`git mv demo-output/website/dafoam cases/dafoam` renames the
        directory, so gitignored content inside it travels.  Hand-carrying it
        as well would move it twice."""
        write(self.root, _W + "/dafoam/case/case.json")
        self.commit(_W + "/dafoam/case/case.json")
        write(self.root, _W + "/dafoam/case/processor0/f")
        hc = self.mod()
        d = hc.derive()
        self.assertNotIn(_W + "/dafoam/case/processor0",
                         {r["source"] for r in d["carry"]})
        rides = {r["source"]: r for r in d["rides_along"]}
        self.assertIn(_W + "/dafoam/case/processor0", rides)
        self.assertEqual(rides[_W + "/dafoam/case/processor0"]["carried_by"],
                         _W + "/dafoam")

    def test_a_regenerated_cache_tree_is_discarded_not_carried(self):
        """A `__pycache__` under `campaign/` goes dark like anything else and
        a rule's prefix claims it.  Carrying it moves a stale `.pyc` whose
        embedded source path no longer exists into the new tree."""
        write(self.root, _W + "/campaign/RECORD.md")
        self.commit(_W + "/campaign/RECORD.md")
        write(self.root, _W + "/campaign/__pycache__/x.cpython-312.pyc")
        hc = self.mod()
        d = hc.derive()
        self.assertNotIn(_W + "/campaign/__pycache__",
                         {r["source"] for r in d["carry"]})
        self.assertIn(_W + "/campaign/__pycache__",
                      {r["source"] for r in d["discard"]})

    def test_a_tree_no_rule_maps_stays_put(self):
        """`mission-output/` holds 8,625 files and appears nowhere in the
        target tree.  It must be reported as staying, not carried anywhere."""
        write(self.root, "mission-output/study/x.dat")
        hc = self.mod()
        d = hc.derive()
        self.assertIn("mission-output", {r["source"] for r in d["stays"]})
        self.assertNotIn("mission-output", {r["source"] for r in d["carry"]})

    def test_batch_2_untracking_creates_a_new_hand_carry(self):
        """A move source whose LAST tracked file batch 2 removes goes dark
        between batch 2 and the batch that was going to move it.  This is
        `MESH_AUDIT_runs`, whose 78 tracked files are all solver logs."""
        # A campaign record, so `campaign/` stays lit after batch 2 and the
        # maximal dark tree is the run archive rather than the whole webroot.
        write(self.root, _W + "/campaign/RECORD.md")
        write(self.root, _W + "/campaign/AUDIT_runs/2026/a.log.checkMesh")
        write(self.root, _W + "/campaign/AUDIT_runs/2026/b.log.checkMesh")
        self.commit(_W + "/campaign/RECORD.md",
                    _W + "/campaign/AUDIT_runs/2026/a.log.checkMesh",
                    _W + "/campaign/AUDIT_runs/2026/b.log.checkMesh")
        hc = self.mod()
        tracked = hc.tracked_paths()
        self.assertEqual({r["source"] for r in hc.derive(tracked)["carry"]}, set())
        proj = hc.project_after_untracking(tracked)
        self.assertEqual([r["source"] for r in proj],
                         [_W + "/campaign/AUDIT_runs"])
        self.assertEqual(proj[0]["tracked_now"], 2)

    def test_the_must_not_match_control_for_the_projection(self):
        """A run tree whose tracked files are case dictionaries survives batch
        2 and must NOT be reported.  A projection that fires on everything is
        the same as none."""
        write(self.root, _W + "/campaign/AUDIT_runs/c/system/controlDict")
        self.commit(_W + "/campaign/AUDIT_runs/c/system/controlDict")
        hc = self.mod()
        self.assertEqual(hc.project_after_untracking(hc.tracked_paths()), [])


class Planning(RepoCase):

    def test_the_inverse_list_exists_before_anything_moves(self):
        """MOVE_MAP section 9: a batch without its inverse list does not
        start.  `git reset --hard` does not undo a move's effect on gitignored
        content, so the inverse must be written down first."""
        write(self.root, _W + "/campaign/RECORD.md")
        self.commit(_W + "/campaign/RECORD.md")
        write(self.root, _W + "/solve_registry/a.log")
        hc = self.mod()
        p = self.plan(hc)
        self.assertEqual([i["inverse"] for i in p["items"]],
                         [f"mv {p['items'][0]['dest']} {_W}/solve_registry"])
        self.assertTrue((self.root / _W / "solve_registry").is_dir(),
                        "plan must not move anything")

    def test_gitignore_patterns_naming_a_carried_tree_are_reported(self):
        """A carried tree whose ignore rule is not re-pointed stops being
        ignored the moment it lands, and the next `git add` sweeps it in."""
        write(self.root, ".gitignore", _W + "/solve_registry/\n**/surfaces/\n")
        write(self.root, _W + "/closure.html")   # keeps the webroot lit
        self.commit(".gitignore", _W + "/closure.html")
        write(self.root, _W + "/solve_registry/a.log")
        hc = self.mod()
        pl = self.plan(hc)
        self.plan_dest = pl["items"][0]["dest"]
        lines = pl["gitignore_repoint"]
        self.assertEqual(len(lines), 1)
        self.assertIn(self.plan_dest + "/", lines[0])
        self.assertNotIn("surfaces", lines[0])  # path-independent, needs nothing


class CarryAndItsChecks(RepoCase):

    def stage(self, files: int = 3):
        write(self.root, _W + "/campaign/RECORD.md")
        self.commit(_W + "/campaign/RECORD.md")
        for i in range(files):
            write(self.root, f"{_W}/solve_registry/j{i}.log", "body%d" % i)
        hc = self.mod()
        return hc, self.plan(hc)

    def test_a_clean_carry_moves_the_tree_and_verifies_it(self):
        hc, p = self.stage()
        self.assertEqual(hc.carry(p, [], 0), PASS)
        self.assertFalse((self.root / _W / "solve_registry").exists())
        dst = self.root / p["items"][0]["dest"]
        self.assertEqual(len(list(dst.iterdir())), 3)
        self.assertTrue(p["items"][0]["carried"])
        self.assertEqual(hc.verify(p), PASS)

    def test_the_after_check_reddens_when_the_destination_is_short(self):
        """THE load-bearing test.  A carry whose after-check cannot fail is a
        carry nobody checked.  One file is removed behind the verifier's back
        and it must say so."""
        hc, p = self.stage()
        self.assertEqual(hc.carry(p, [], 0), PASS)
        (self.root / p["items"][0]["dest"] / "j1.log").unlink()
        self.assertEqual(hc.verify(p), FAIL)

    def test_the_after_check_reddens_when_the_bytes_differ(self):
        """A file count alone is not evidence: two trees can share a count and
        differ in every byte."""
        hc, p = self.stage()
        self.assertEqual(hc.carry(p, [], 0), PASS)
        (self.root / p["items"][0]["dest"] / "j1.log").write_text(
            "a much longer body than the original")
        self.assertEqual(hc.verify(p), FAIL)

    def test_the_after_check_reddens_when_the_path_set_differs(self):
        """Count and bytes both preserved, names swapped.  Only the path set
        catches this, which is why it is measured."""
        hc, p = self.stage()
        self.assertEqual(hc.carry(p, [], 0), PASS)
        d = self.root / p["items"][0]["dest"]
        (d / "j1.log").rename(d / "j9.log")
        self.assertEqual(hc.verify(p), FAIL)

    def test_the_after_check_reddens_when_the_source_is_recreated_with_files(self):
        """A live launcher writing to the old path re-creates it.  An empty
        re-creation is a note; files in it mean the carry did not take."""
        hc, p = self.stage()
        self.assertEqual(hc.carry(p, [], 0), PASS)
        write(self.root, _W + "/solve_registry/late.log")
        self.assertEqual(hc.verify(p), FAIL)

    def test_a_tree_that_gained_a_tracked_file_is_refused(self):
        """If `git mv` now works, a hand `mv` leaves the index pointing at the
        old path.  Refusing is the only safe answer.

        A file already on disk is committed rather than a new one added, so
        the file count and byte total are UNCHANGED -- otherwise the drift
        check fires first and masks this one entirely.  It did, until a mutant
        that deleted the tracked-file check went undetected.
        """
        hc, p = self.stage()
        self.commit(_W + "/solve_registry/j1.log")
        after = hc.measure(self.root / _W / "solve_registry")
        self.assertEqual(after["files"], p["items"][0]["files"])
        self.assertEqual(after["bytes"], p["items"][0]["bytes"])
        self.assertEqual(hc.carry(p, [], 0), FAIL)
        self.assertTrue((self.root / _W / "solve_registry").is_dir())

    def test_the_carry_itself_reddens_when_the_move_does_not_land_it_all(self):
        """The check inside `carry`, not the one in `verify`.

        A `shutil.move` that lands short -- a cross-device copy that hits an
        unreadable file, a destination filesystem that runs out -- must be
        caught in the same invocation, not on a later `verify` nobody runs.
        The destination measurement is intercepted rather than simulated,
        because what is under test is whether the comparison is MADE.
        """
        hc, p = self.stage()
        src = str(self.root / _W / "solve_registry")
        real = hc.measure
        calls: list[str] = []

        def short(path):
            m = dict(real(path))
            calls.append(str(path))
            if str(path) != src:               # only the destination reading
                m["files"] -= 1
            return m

        hc.measure = short
        try:
            self.assertEqual(hc.carry(p, [], 0), FAIL)
        finally:
            hc.measure = real
        self.assertTrue(any(s != src for s in calls),
                        "carry never measured the destination")
        self.assertFalse(p["items"][0]["carried"])

    def test_a_tree_that_changed_since_the_plan_is_refused(self):
        """`THERMAL_K0_runs` measured 387 files and, ten minutes later, 362.
        A carry of a tree a solver is writing into has an "after" count that is
        evidence of nothing."""
        hc, p = self.stage()
        write(self.root, _W + "/solve_registry/j99.log")
        self.assertEqual(hc.carry(p, [], 0), FAIL)
        self.assertTrue((self.root / _W / "solve_registry").is_dir())

    def test_a_tree_written_inside_the_quiet_window_is_refused(self):
        hc, p = self.stage()
        os.utime(self.root / _W / "solve_registry" / "j0.log", None)
        p["items"][0].update(hc.measure(self.root / _W / "solve_registry"))
        self.assertEqual(hc.carry(p, [], 300), FAIL)
        self.assertTrue((self.root / _W / "solve_registry").is_dir())

    def test_an_existing_destination_is_refused_rather_than_merged(self):
        hc, p = self.stage()
        (self.root / p["items"][0]["dest"]).mkdir(parents=True)
        self.assertEqual(hc.carry(p, [], 0), FAIL)
        self.assertTrue((self.root / _W / "solve_registry").is_dir())

    def test_the_inverse_list_actually_restores_the_tree(self):
        """The rollback is asserted, not assumed."""
        hc, p = self.stage()
        before = hc.measure(self.root / _W / "solve_registry")
        self.assertEqual(hc.carry(p, [], 0), PASS)
        src, dst = p["items"][0]["inverse"].split()[1:]
        (self.root / dst).parent.mkdir(parents=True, exist_ok=True)
        (self.root / src).rename(self.root / dst)
        self.assertEqual(hc.measure(self.root / _W / "solve_registry"), before)


class AgainstTheLiveTree(unittest.TestCase):
    """Read-only.  These pin the findings the batch plan is built on."""

    @classmethod
    def setUpClass(cls):
        cls.hc = load(_REPO, "hc_live")
        cls.tracked = cls.hc.tracked_paths()

    def test_solve_registry_is_still_dark(self):
        """MOVE_MAP section 4.3's named instance.  If it ever gains a tracked
        file this test fails, which is the correct alarm: `git mv` then works
        and the hand-carry must not run.

        Asked of HEAD, not of `git ls-files`.  The index on this tree is
        missing every file landed by a private-index commit -- 160 of them at
        `f40f6ef5` -- and `THERMAL_K0_runs` was called dark on exactly that
        mistake."""
        cp = subprocess.run(
            ["git", "-C", str(_REPO), "ls-tree", "-r", "--name-only", "HEAD",
             "--", _W + "/solve_registry"],
            capture_output=True, text=True)
        self.assertEqual(cp.stdout.strip(), "",
                         "solve_registry gained tracked files: re-derive the "
                         "carry set before moving anything")

    def test_the_tracked_frame_is_head_and_not_the_index(self):
        """The frame itself, pinned.  A regression to `git ls-files` here is
        silent and puts a git-mv-able tree on the hand-carry list."""
        hc = self.hc
        head = subprocess.run(
            ["git", "-C", str(_REPO), "ls-tree", "-r", "--name-only", "HEAD"],
            capture_output=True, text=True).stdout.split("\n")
        head = [p for p in head if p]
        self.assertEqual(sorted(self.tracked), sorted(head))
        idx = subprocess.run(["git", "-C", str(_REPO), "ls-files"],
                             capture_output=True, text=True).stdout.split("\n")
        idx = [p for p in idx if p]
        # Not an equality assertion: the two frames may coincide at a quiet
        # moment.  What is pinned is that the module took the HEAD one.
        self.assertGreaterEqual(len(self.tracked), len(set(self.tracked) & set(idx)))

    def test_the_carry_set_is_reachable_and_every_member_has_a_destination(self):
        d = self.hc.derive(self.tracked)
        self.assertGreater(len(d["carry"]), 0)
        for r in d["carry"]:
            with self.subTest(src=r["source"]):
                self.assertIsNotNone(r["dest"])
                self.assertGreater(r["files"], 0)

    def test_no_tree_is_in_two_buckets_at_once(self):
        d = self.hc.derive(self.tracked)
        buckets = [{r["source"] for r in d[k]}
                   for k in ("carry", "rides_along", "stays", "discard")]
        for i, a in enumerate(buckets):
            for b in buckets[i + 1:]:
                self.assertEqual(a & b, set())


class TheBatch2GateFiredBothWays(RepoCase):
    """The amendment of 2026-08-17, and the plant that proves it.

    `batch2_survivors` classified `*.log.checkMesh` inside a `*_runs` tree as
    output BY FILE CLASS.  Batch 2's stated verification is *"the
    goes-dark-after-batch-2 section must read 0 afterwards, not 1"*, and under
    a class test that line read 0 under option B -- the tree is already in the
    carry set, so the projection reports only the difference -- and 1 under
    option A, where batch 2 had actually spared the files and nothing was ever
    going to go dark.  **The gate was satisfied by the riskier option and
    failed under the safer one.**

    So the two tests below are one fixture fired in both directions.  Neither
    is evidence alone: a gate that always reads 0 passes the first, and a gate
    that always reads 1 passes the second.
    """

    def fixture(self):
        """A campaign run archive whose every tracked file is a solver log --
        `MESH_AUDIT_runs` in miniature -- beside a record that keeps
        `campaign/` lit, so the maximal dark tree is the archive."""
        write(self.root, _W + "/campaign/RECORD.md")
        rels = [_W + "/campaign/MESH_AUDIT_runs/a/a.log.checkMesh",
                _W + "/campaign/MESH_AUDIT_runs/b/b.log.checkMesh"]
        for r in rels:
            write(self.root, r)
        self.commit(_W + "/campaign/RECORD.md", *rels)
        hc = self.mod()
        hc.BATCH2_EXCLUSIONS = (_W + "/campaign/MESH_AUDIT_runs",)
        return hc, hc.tracked_paths()

    def test_the_gate_passes_when_the_ruled_exclusion_is_honoured(self):
        """Option A: batch 2's list does not name those files, so the tree
        never goes dark and the section reads 0."""
        hc, tracked = self.fixture()
        b2 = hc.batch2_untrack_list(tracked)
        self.assertNotIn(_W + "/campaign/MESH_AUDIT_runs/a/a.log.checkMesh", b2)
        self.assertEqual(hc.project_after_untracking(tracked, b2), [])
        self.assertEqual(hc.project_after_untracking(tracked), [],
                         "the default must BE the ruled option, or the gate "
                         "reads one thing and the batch does another")

    def test_the_gate_fails_when_the_ruled_exclusion_is_dropped(self):
        """The same fixture, exclusion dropped: batch 2 takes the 78, the tree
        goes dark, and the section reads 1.  Without this direction the test
        above is satisfied by a projection that never fires."""
        hc, tracked = self.fixture()
        b2 = hc.batch2_untrack_list(tracked, ())
        self.assertIn(_W + "/campaign/MESH_AUDIT_runs/a/a.log.checkMesh", b2)
        proj = hc.project_after_untracking(tracked, b2)
        self.assertEqual([r["source"] for r in proj],
                         [_W + "/campaign/MESH_AUDIT_runs"])
        self.assertEqual(proj[0]["tracked_now"], 2)

    def test_the_survivors_are_a_membership_test_and_not_a_class_test(self):
        """The load-bearing property in one line: a path survives batch 2 if
        and only if batch 2's LIST does not name it.  Handing the function a
        list that spares a solver log must spare it, whatever its class."""
        hc, tracked = self.fixture()
        log = _W + "/campaign/MESH_AUDIT_runs/a/a.log.checkMesh"
        self.assertIn(log, hc.batch2_survivors(tracked, untrack_list=[]))
        self.assertNotIn(log, hc.batch2_survivors(tracked, untrack_list=[log]))
        # ... and a file no class rule would ever touch still goes if the list
        # names it, which a class test could not express at all.
        rec = _W + "/campaign/RECORD.md"
        self.assertNotIn(rec, hc.batch2_survivors(tracked, untrack_list=[rec]))


class InitialConditionsAreSourceNotSolverOutput(RepoCase):
    """`0.orig/` is CASE INPUT, added 2026-08-17 while executing batch 2.

    `batch2_class_candidates` spared `system/`, `constant/` and `0/` and did
    NOT spare `0.orig/`, which is the OpenFOAM spelling for the initial
    conditions a case is rebuilt from -- the same table row of MOVE_MAP
    section 7.2, ruled source.  On the live tree at `fc1e3bac` the unrepaired
    function reached **122 tracked initial-condition files**, 64 of them
    tracked only because two `.gitignore` negation blocks written that same day
    re-include them.  Batch 2 would have untracked exactly the files those two
    blocks exist to keep.

    Fired in both directions, because a `stays()` that spared everything would
    satisfy the first assertion on its own.
    """

    def fixture(self):
        rels = ["c/K0c_runs/case1/0.orig/T",
                "c/K0c_runs/case1/0.orig/U",
                "c/K0c_runs/case1/0/T",
                "c/K0c_runs/case1/system/controlDict",
                "c/K0c_runs/case1/constant/g",
                "c/K0c_runs/case1/log.blockMesh",
                "c/K0c_runs/case1/500/T"]
        for r in rels:
            write(self.root, r)
        self.commit(*rels)
        hc = self.mod()
        hc.BATCH2_EXCLUSIONS = ()
        return hc, hc.tracked_paths()

    def test_initial_conditions_are_not_in_the_untracking_class(self):
        hc, tracked = self.fixture()
        cand = hc.batch2_class_candidates(tracked)
        for p in ("c/K0c_runs/case1/0.orig/T", "c/K0c_runs/case1/0.orig/U",
                  "c/K0c_runs/case1/0/T", "c/K0c_runs/case1/system/controlDict",
                  "c/K0c_runs/case1/constant/g"):
            self.assertNotIn(p, cand, f"{p} is case INPUT and stays tracked")

    def test_the_control_solver_output_beside_them_still_goes(self):
        """The must-not-match control.  Without it, a `stays()` that returned
        True for everything passes the test above and untracks nothing, which
        is a batch 2 that reports success having done nothing."""
        hc, tracked = self.fixture()
        cand = hc.batch2_class_candidates(tracked)
        self.assertIn("c/K0c_runs/case1/log.blockMesh", cand)
        self.assertIn("c/K0c_runs/case1/500/T", cand)


class TheR25ExclusionIsNotVisibleToTheGoDarkGate(RepoCase):
    """`docs/campaigns/` excluded 2026-08-17, and why a constant was needed.

    R25 sends `docs/campaigns/<c>/*_{runs,sensitivity}/**` to
    `verification/runs/<c>/`.  Batch 2's class rule reaches part of that tree
    but not all of it, so -- unlike `MESH_AUDIT_runs` -- the tree never goes
    dark and `project_after_untracking` reads 0 whether batch 2 spares those
    files or takes every one of them.  The gate is a GO-DARK detector; this
    hazard is not a go-dark, and the two tests below are the pair that says so.
    """

    def fixture(self):
        rels = ["docs/campaigns/F14/K0c_runs/case1/system/controlDict",
                "docs/campaigns/F14/K0c_runs/case1/constant/g",
                "docs/campaigns/F14/K0c_runs/case1/log.blockMesh",
                "docs/campaigns/F14/K0c_runs/case1/log.checkMesh"]
        for r in rels:
            write(self.root, r)
        self.commit(*rels)
        return self.mod()

    def test_the_ruled_exclusion_keeps_r25_files_out_of_batch_2s_list(self):
        """Read the DEFAULT, never a hand-passed tuple.

        The first cut of this test passed `("docs/campaigns",)` explicitly and
        was therefore green against a `BATCH2_EXCLUSIONS` that did not contain
        it -- it pinned the filtering, not the ruling.  That is the failure the
        option-A amendment already records in its own words: *"a gate whose
        default differs from the batch's own choice reads one thing while the
        batch does another."*  Caught by the m3 mutant, which dropped the
        constant's second entry and passed all four tests.
        """
        hc = self.fixture()
        tracked = hc.tracked_paths()
        self.assertIn("docs/campaigns", hc.BATCH2_EXCLUSIONS,
                      "the ruled exclusion must be IN the constant, because "
                      "the constant is what batch 2's list is built from")
        self.assertEqual(hc.batch2_untrack_list(tracked), [],
                         "with no argument at all -- the default must BE the "
                         "ruled option")

    def test_the_go_dark_gate_reads_zero_either_way_so_it_is_not_the_check(self):
        """The load-bearing negative result.  The projection reads 0 with the
        exclusion honoured AND with it dropped, so a green batch-2 gate is not
        evidence that R25 was left alone.  If this test ever reddens, the gate
        has become able to see this hazard and the constant can be revisited."""
        hc = self.fixture()
        tracked = hc.tracked_paths()
        spared = hc.batch2_untrack_list(tracked, ("docs/campaigns",))
        taken = hc.batch2_untrack_list(tracked, ())
        self.assertNotEqual(spared, taken, "the fixture must differ both ways")
        self.assertEqual(hc.project_after_untracking(tracked, spared), [])
        self.assertEqual(hc.project_after_untracking(tracked, taken), [])


class TheBatch2GateOnTheLiveTree(unittest.TestCase):
    """The same plant, against the tree the ruling is about.  Read-only."""

    @classmethod
    def setUpClass(cls):
        cls.hc = load(_REPO, "hc_b2_live")
        cls.tracked = cls.hc.tracked_paths()
        cls.tree = _W + "/campaign/MESH_AUDIT_runs"

    def setUp(self):
        if not any(p.startswith(self.tree + "/") for p in self.tracked):
            self.skipTest(f"{self.tree} holds no tracked file at HEAD: batch 2 "
                          "or batch 7 has since run and this plant is spent")

    def test_the_live_gate_reads_zero_under_the_ruled_option(self):
        proj = self.hc.project_after_untracking(self.tracked)
        self.assertEqual([r["source"] for r in proj], [],
                         "batch 2's stated verification does not pass")

    def test_the_live_gate_reads_one_when_the_exclusion_is_dropped(self):
        proj = self.hc.project_after_untracking(
            self.tracked, self.hc.batch2_untrack_list(self.tracked, ()))
        self.assertEqual([r["source"] for r in proj], [self.tree])


class WalkErrorsAreRefusedNotSwallowed(RepoCase):
    """The repair of 2026-08-17 to the instrument guarding 1.51 GB.

    `measure` and `maximal_dark_trees` walked with no `onerror` and swallowed
    per-file `OSError`, so an unreadable directory left the file count, the
    byte total AND the path digest short together, with nothing on stderr.
    The after-check compares two measurements by the same instrument, so all
    three agreed and the carry reported success while data went missing.
    """

    def setUp(self):
        super().setUp()
        if os.geteuid() == 0:
            self.skipTest("root ignores the permission bits these tests plant")

    def tree(self):
        """Three files, one of them behind a directory we will lock."""
        write(self.root, _W + "/campaign/RECORD.md")
        self.commit(_W + "/campaign/RECORD.md")
        for r in ("open/a.dat", "open/b.dat", "locked/c.dat"):
            write(self.root, _W + "/campaign/K0_runs/" + r)
        return self.mod(), self.root / _W / "campaign" / "K0_runs"

    def lock(self, d: Path, mode: int):
        d.chmod(mode)
        self.addCleanup(lambda: d.chmod(0o755))

    def test_the_control_a_readable_tree_measures_clean(self):
        """The must-not-match control.  A `measure` that raised on everything
        would satisfy every test below and be worthless."""
        hc, src = self.tree()
        m = hc.measure(src)
        self.assertEqual(m["files"], 3)
        self.assertEqual(m["walk_errors"], 0)
        self.assertEqual(m["error_paths"], [])

    def test_an_unreadable_directory_is_refused_not_silently_undercounted(self):
        """`os.walk`'s default `onerror` yields nothing for a directory it
        cannot open.  The file under it used to vanish from all three
        figures."""
        hc, src = self.tree()
        self.lock(src / "locked", 0o000)
        with self.assertRaises(hc.MeasurementError) as cm:
            hc.measure(src)
        self.assertTrue(any("locked" in e for e in cm.exception.errors))
        # And this is the number it used to return instead: 2 of 3, quietly.
        loose = hc.measure(src, strict=False)
        self.assertEqual(loose["files"], 2)
        self.assertEqual(loose["walk_errors"], 1)

    def test_an_unstatable_file_is_refused_not_silently_undercounted(self):
        """The other half: the directory lists but its entries do not stat, so
        the walk succeeds and the per-file `except OSError: continue` ate the
        file.  Same three figures short, same silence."""
        hc, src = self.tree()
        self.lock(src / "locked", 0o400)
        loose = hc.measure(src, strict=False)
        if loose["walk_errors"] == 0:  # pragma: no cover - filesystem dependent
            self.skipTest("this filesystem stats entries the directory bits "
                          "should have refused")
        self.assertLess(loose["files"], 3)
        with self.assertRaises(hc.MeasurementError):
            hc.measure(src)

    def test_the_dark_tree_walk_refuses_rather_than_missing_a_tree(self):
        """One level up, where the silent loss is a whole tree rather than a
        file -- and an unreported dark tree is the 1.51 GB left behind."""
        hc, _src = self.tree()
        d = self.root / _W / "campaign" / "K0_runs" / "locked"
        self.lock(d, 0o000)
        with self.assertRaises(hc.MeasurementError):
            hc.maximal_dark_trees(hc.tracked_paths())
        with self.assertRaises(hc.MeasurementError):
            hc.derive()

    def test_the_carry_refuses_rather_than_calling_an_unmeasurable_tree_moved(self):
        """The check the module exists for, at the moment it matters most.

        The REASON is asserted, not just the exit code: a swallowing `measure`
        also reddens here, via the drift check, and a test satisfied by that
        would be masked exactly the way this file's own header warns about."""
        import contextlib, io
        hc, src = self.tree()
        plan = self.plan(hc, quiet=0)
        self.assertEqual([i["source"] for i in plan["items"]],
                         [_W + "/campaign/K0_runs"])
        self.lock(src / "locked", 0o000)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = hc.carry(plan, [], 0)
        self.assertEqual(rc, FAIL)
        self.assertIn("walk/stat error", out.getvalue())
        self.assertNotIn("mv ", out.getvalue(),
                         "it must refuse BEFORE moving anything")

    def test_the_error_reaches_stderr_and_is_not_only_an_exception(self):
        """*"without reaching stderr"* was half the defect.  A caller that
        catches the exception must still be able to see which path failed."""
        import contextlib, io
        hc, src = self.tree()
        self.lock(src / "locked", 0o000)
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            with self.assertRaises(hc.MeasurementError):
                hc.measure(src)
        self.assertIn("WALK ERROR", buf.getvalue())
        self.assertIn("locked", buf.getvalue())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
