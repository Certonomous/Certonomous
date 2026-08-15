"""Both halves of the control on the attribution checker (L-84).

L-84: a positive control proves an instrument CAN fire; it does not prove it
fires only where it should. So every case here is built in a throwaway git
repository with real commits carrying real trailers, and the cases come in
pairs:

  * A GENUINE NON-AUTHOR verifies -- two sessions, and the checker says
    NON-AUTHOR and exits 0. Without this half every other test is satisfied by
    a checker that says AUTHOR to everything.
  * A SAME-AGENT PAIR IS CAUGHT -- one session on both sides, and the checker
    says AUTHOR and exits 1. Without this half the mechanism certifies
    everything.
  * A COMMIT PREDATING THE MECHANISM returns UNKNOWN, and specifically NOT
    either verdict. This is the half that matters most: a missing attribution
    reading as independence would be strictly worse than the uniform ignorance
    it replaces, because today nobody is fooled.
  * AN EMPTY GRADED SET is UNKNOWN with a reason naming defect class B1, never
    a clean answer. D62's class: a checker that examined nothing and reported
    clean.

THE EXIT CODES ARE TYPED OUT HERE AS NUMBERS, and imported from nowhere. The
reason is `test_lab_check.py`'s: every assertion there once read
`assertEqual(rc, lc.EXIT[lc.FAIL])`, comparing a subprocess's exit code against
the module-under-test's own dictionary, so mutating the dictionary moved both
sides together and left 25 of 25 tests green while the hook that reads the
numbers directly fell through to its out-of-contract arm. A test that asks the
thing under test what the right answer is has not tested it.

Nothing here touches the live repository. Every commit is made in a tempdir.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CHECKER = REPO / "scripts" / "check_rung_attribution.py"

#: THE PUBLISHED EXIT CONTRACT, as numbers.
RC_PASS = 0
RC_FAIL = 1
RC_UNKNOWN = 3

_SPEC = importlib.util.spec_from_file_location("rung_attribution_under_test",
                                               CHECKER)
ra = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = ra
_SPEC.loader.exec_module(ra)

#: Two sessions, shaped exactly as `CLAUDE_CODE_SESSION_ID` is on this box.
SESSION_A = "64b13819-ff95-4d4d-a50f-3720bab19084"
SESSION_B = "982d6244-5800-47f3-a450-80ce0b0a24b7"
HOST = "ip-172-31-43-247"


def trailer(session: str, tag: str = "-", host: str = HOST) -> str:
    return f"Lab-Agent: {host}/{session}/{tag}"


class Repo:
    """A throwaway git repository whose commits carry chosen trailers."""

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._git("init", "-q", "-b", "main")
        self._git("config", "user.email", "ubuntu@ip-172-31-43-247")
        self._git("config", "user.name", "Ubuntu")

    def _git(self, *args: str) -> subprocess.CompletedProcess:
        r = subprocess.run(["git", "-C", str(self.root), *args],
                           capture_output=True, text=True)
        if r.returncode != 0 and args[0] not in ("cherry-pick",):
            raise AssertionError(f"git {' '.join(args)} failed: {r.stderr}")
        return r

    def commit(self, subject: str, body: str = "", *, fname: str = "f.txt"
               ) -> str:
        p = self.root / fname
        prev = p.read_text() if p.exists() else ""
        p.write_text(prev + subject + "\n")
        self._git("add", fname)
        msg = subject if not body else f"{subject}\n\n{body}"
        mp = self.root / ".msg"
        mp.write_text(msg + "\n")
        self._git("commit", "-q", "-F", str(mp), "--", fname)
        return self._git("rev-parse", "HEAD").stdout.strip()


def run(repo: Repo, *args: str, env: dict | None = None
        ) -> subprocess.CompletedProcess:
    e = dict(os.environ)
    if env is not None:
        e.update(env)
    return subprocess.run([sys.executable, str(CHECKER), "--repo", str(repo.root),
                           *args], capture_output=True, text=True, env=e)


def verdict_of(proc: subprocess.CompletedProcess) -> str:
    for line in proc.stdout.splitlines():
        if line.startswith("VERDICT: "):
            return line[len("VERDICT: "):].strip()
    raise AssertionError(f"no VERDICT line in output:\n{proc.stdout}\n{proc.stderr}")


class _Tmp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def repo(self) -> Repo:
        return Repo(self.tmp / "r")


# ---------------------------------------------------------------------------
# THE TWO HALVES, END TO END
# ---------------------------------------------------------------------------

class BothHalvesOfTheControl(_Tmp):

    def test_a_genuine_non_author_verifies(self):
        """POSITIVE HALF: two sessions -> NON-AUTHOR, exit 0."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        g1 = r.commit("the work", trailer(SESSION_A, "builder"))
        g2 = r.commit("more work", trailer(SESSION_A, "builder"))
        closing = r.commit("rung closed", trailer(SESSION_B, "grader"))

        p = run(r, "--anchor", anchor, "--closing", closing,
                "--graded", g1, "--graded", g2)
        self.assertEqual(verdict_of(p), "NON-AUTHOR", p.stdout)
        self.assertEqual(p.returncode, RC_PASS, p.stdout)

    def test_a_same_agent_pair_is_caught(self):
        """NEGATIVE HALF: one session on both sides -> AUTHOR, exit 1."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        g1 = r.commit("the work", trailer(SESSION_A))
        closing = r.commit("rung closed", trailer(SESSION_A))

        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", g1)
        self.assertEqual(verdict_of(p), "AUTHOR", p.stdout)
        self.assertEqual(p.returncode, RC_FAIL, p.stdout)

    def test_the_self_declared_tag_never_upgrades_a_same_session_pair(self):
        """Two DIFFERENT tags, one session, and it is still AUTHOR.

        The tag is the one field an agent types, so it is the one field a
        copied dispatch brief duplicates by accident. Letting it certify
        independence would put the weakest field in the deciding position.
        """
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        g1 = r.commit("the work", trailer(SESSION_A, "builder"))
        closing = r.commit("rung closed", trailer(SESSION_A, "grader"))

        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", g1)
        self.assertEqual(verdict_of(p), "AUTHOR", p.stdout)
        self.assertEqual(p.returncode, RC_FAIL)

    def test_a_commit_predating_the_mechanism_is_unknown_not_either_verdict(self):
        """THE HALF THAT MATTERS MOST: backfill is impossible, so UNKNOWN."""
        r = self.repo()
        old = r.commit("work done before any of this existed")
        anchor = r.commit("anchor", trailer(SESSION_A))
        closing = r.commit("rung closed", trailer(SESSION_B, "grader"))

        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", old)
        v = verdict_of(p)
        self.assertEqual(v, "UNKNOWN", p.stdout)
        self.assertNotEqual(v, "NON-AUTHOR")
        self.assertNotEqual(v, "AUTHOR")
        self.assertEqual(p.returncode, RC_UNKNOWN, p.stdout)
        self.assertIn("predate", p.stdout.lower())

    def test_a_pre_anchor_closing_commit_is_unknown_and_says_why(self):
        r = self.repo()
        old_closing = r.commit("closed before the mechanism existed")
        anchor = r.commit("anchor", trailer(SESSION_A))
        g1 = r.commit("the work", trailer(SESSION_A))

        p = run(r, "--anchor", anchor, "--closing", old_closing, "--graded", g1)
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertIn("Backfill is impossible", p.stdout)

    def test_an_empty_graded_set_is_unknown_naming_b1(self):
        """Defect class B1: zero matches is never a clean answer."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        closing = r.commit("rung closed", trailer(SESSION_B))

        p = run(r, "--anchor", anchor, "--closing", closing)
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertIn("B1", p.stdout)

    def test_an_unattributed_graded_commit_is_unknown_never_independent(self):
        """A missing identity must not read as independence."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        naked = r.commit("work by an agent that did not adopt the mechanism")
        closing = r.commit("rung closed", trailer(SESSION_B, "grader"))

        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", naked)
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertNotIn("VERDICT: NON-AUTHOR", p.stdout)


# ---------------------------------------------------------------------------
# RULE ORDER, AND THE GRAMMAR
# ---------------------------------------------------------------------------

class TheAmbiguousCasesResolveTheSafeWay(_Tmp):

    def test_author_beats_partial_unknown(self):
        """Half the graded set unattributed, half provably the closing agent.

        AUTHOR, not UNKNOWN. AUTHOR can only DENY a closure, so resolving the
        ambiguity that way cannot manufacture an independence claim.
        """
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        naked = r.commit("unattributed work")
        mine = r.commit("work I did", trailer(SESSION_A))
        closing = r.commit("rung closed", trailer(SESSION_A))

        p = run(r, "--anchor", anchor, "--closing", closing,
                "--graded", naked, "--graded", mine)
        self.assertEqual(verdict_of(p), "AUTHOR", p.stdout)
        self.assertEqual(p.returncode, RC_FAIL)

    def test_a_malformed_trailer_is_not_treated_as_absent(self):
        r = self.repo()
        self.assertEqual(ra.parse_trailer("Lab-Agent: nonsense")[0], "malformed")
        self.assertEqual(ra.parse_trailer("Lab-Agent: h/NOT-A-UUID/-")[0],
                         "malformed")
        self.assertIsNone(ra.parse_trailer("Lab-Agent: nonsense")[1])
        anchor = r.commit("anchor", trailer(SESSION_A))
        bad = r.commit("work", "Lab-Agent: nonsense")
        closing = r.commit("closed", trailer(SESSION_B))
        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", bad)
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)

    def test_two_trailers_on_one_commit_do_not_resolve_to_the_first(self):
        """A commit claiming two identities has not said which agent made it."""
        state, ident, _ = ra.parse_trailer(
            trailer(SESSION_A) + "\n" + trailer(SESSION_B))
        self.assertEqual(state, "duplicate")
        self.assertIsNone(ident)

    def test_the_emitter_and_the_grammar_agree(self):
        """What --emit-trailer prints must parse. Otherwise the mechanism emits
        exactly what it rejects, and every adopter reads MALFORMED."""
        line, why = ra.local_identity("some.tag-1")
        self.assertIsNotNone(line, why)
        state, ident, tag = ra.parse_trailer(line)
        self.assertEqual(state, "ok")
        self.assertEqual(tag, "some.tag-1")
        self.assertTrue(ident.endswith(os.environ["CLAUDE_CODE_SESSION_ID"]))

    def test_emit_without_a_session_emits_nothing_and_says_unknown(self):
        r = self.repo()
        p = subprocess.run(
            [sys.executable, str(CHECKER), "--emit-trailer"],
            capture_output=True, text=True,
            env={k: v for k, v in os.environ.items()
                 if k != "CLAUDE_CODE_SESSION_ID"})
        self.assertEqual(p.stdout.strip(), "", "emitted a fabricated identity")
        self.assertEqual(p.returncode, RC_UNKNOWN)
        del r

    def test_a_bare_graded_rev_does_not_walk_its_ancestors(self):
        """`--graded <sha>` means that commit, not everything under it.

        Without `--no-walk`, `git rev-list <sha>` returns the whole ancestry,
        so a dispatcher naming one commit would silently grade the entire
        history and get a guaranteed AUTHOR.
        """
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        mine = r.commit("work by the closer", trailer(SESSION_B))
        theirs = r.commit("work by someone else", trailer(SESSION_A))
        closing = r.commit("closed", trailer(SESSION_B))

        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", theirs,
                "--json")
        frame = json.loads(p.stdout)
        self.assertEqual(frame["graded_count"], 1, frame)
        self.assertEqual(frame["verdict"], "NON-AUTHOR", frame)
        del mine


# ---------------------------------------------------------------------------
# THE INTEGRITY RUN -- what `scripts/lab_check.py` schedules
# ---------------------------------------------------------------------------

class TheUnargumentedRun(_Tmp):

    def test_clean_history_passes_and_reports_adoption_as_a_number(self):
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        r.commit("adopted", trailer(SESSION_B))
        r.commit("did not adopt")

        p = run(r, "--anchor", anchor)
        self.assertEqual(verdict_of(p), "PASS", p.stdout)
        self.assertEqual(p.returncode, RC_PASS)
        # A PASS here is an integrity claim, never a coverage claim, and the
        # output has to make that impossible to misread.
        self.assertIn("ADOPTION", p.stdout)
        self.assertIn("2 of 3", p.stdout)
        self.assertIn("UNKNOWN", p.stdout)

    def test_a_trailer_before_the_anchor_is_a_fail(self):
        """Either history was rewritten or a trailer was fabricated."""
        r = self.repo()
        r.commit("ancient", trailer(SESSION_A))
        anchor = r.commit("anchor", trailer(SESSION_A))
        r.commit("later", trailer(SESSION_B))

        p = run(r, "--anchor", anchor)
        self.assertEqual(verdict_of(p), "FAIL", p.stdout)
        self.assertEqual(p.returncode, RC_FAIL)

    def test_a_broken_emitter_is_a_fail_not_a_gap_in_adoption(self):
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        r.commit("garbage", "Lab-Agent: this is not an identity")

        p = run(r, "--anchor", anchor)
        self.assertEqual(verdict_of(p), "FAIL", p.stdout)
        self.assertEqual(p.returncode, RC_FAIL)

    def test_an_anchor_absent_from_the_clone_is_unknown_not_pass(self):
        """And it must say WHY -- an absent anchor, not a stray branch.

        The verdict alone does not pin this: deleting the presence check leaves
        the ancestry check to catch it, which returns the same UNKNOWN under
        the wrong reason ("HEAD is not a descendant"). A right verdict with a
        wrong reason sends the next reader to the wrong repair, so the reason
        is asserted here and not only the code.
        """
        r = self.repo()
        r.commit("anchor", trailer(SESSION_A))
        p = run(r, "--anchor", "0" * 40)
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertIn("not present in this repository", p.stdout)

    def test_an_unanchored_build_is_unknown_not_pass(self):
        r = self.repo()
        r.commit("anything", trailer(SESSION_A))
        p = run(r)  # no --anchor, and the shipped ANCHOR is what it is
        # Either the shipped anchor is absent from this throwaway repo, or the
        # build is unanchored. Both are UNKNOWN; neither may be PASS.
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)
        self.assertEqual(p.returncode, RC_UNKNOWN)

    def test_an_anchor_with_no_commits_after_it_still_examines_the_anchor(self):
        """B1's shape: the range must never be empty when the anchor exists."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        p = run(r, "--anchor", anchor, "--json")
        frame = json.loads(p.stdout)
        self.assertEqual(frame["stats"]["examined"], 1, frame)
        self.assertEqual(frame["verdict"], "PASS", frame)


# ---------------------------------------------------------------------------
# THE DOCUMENTED HAZARDS, PINNED SO THEY ARE PROPERTIES AND NOT SURPRISES
# ---------------------------------------------------------------------------

class TheStatedLimits(_Tmp):

    def test_a_cherry_pick_replays_the_original_agents_trailer(self):
        """A cherry-pick replays under a NEW sha and carries the OLD identity.

        This lab has been bitten by assuming a relation survives a cherry-pick.
        Here it survives in a way that is a hazard rather than a feature: the
        replayed commit attributes itself to whoever wrote it first, not to
        whoever replayed it. Pinned so the docstring's claim is measured.
        """
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        r._git("checkout", "-q", "-b", "side")
        original = r.commit("a repair", trailer(SESSION_A, "builder"),
                            fname="side.txt")
        r._git("checkout", "-q", "main")
        # main must move first, or the replay lands on the same parent with the
        # same tree, message and timestamps and git hands back the SAME object.
        r.commit("meanwhile on main", trailer(SESSION_B), fname="main.txt")
        picked = r._git("cherry-pick", original)
        self.assertEqual(picked.returncode, 0, picked.stderr)
        new_sha = r._git("rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(new_sha, original)

        closing = r.commit("closed by the same session that wrote the original",
                           trailer(SESSION_A, "grader"))
        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", new_sha)
        self.assertEqual(verdict_of(p), "AUTHOR", p.stdout)

    def test_every_run_prints_what_it_does_not_verify(self):
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        for args in (("--anchor", anchor),
                     ("--anchor", anchor, "--closing", anchor,
                      "--graded", anchor)):
            p = run(r, *args)
            self.assertIn("EXECUTE the claim", p.stdout, args)
            self.assertIn("FORGEABILITY", p.stdout, args)

    def test_every_run_prints_its_frame(self):
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        p = run(r, "--anchor", anchor)
        self.assertIn("anchor", p.stdout)
        self.assertIn("frame", p.stdout)
        self.assertIn("examined", p.stdout)


class TheExitContractIsPinned(_Tmp):

    def test_the_three_numbers(self):
        self.assertEqual(ra.EXIT_PASS, 0)
        self.assertEqual(ra.EXIT_FAIL, 1)
        self.assertEqual(ra.EXIT_UNKNOWN, 3)

    def test_lab_check_admits_this_module(self):
        """It has to be enumerable and runnable, or it is a check nobody runs."""
        spec = importlib.util.spec_from_file_location(
            "lab_check_for_attribution", REPO / "scripts" / "lab_check.py")
        lc = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = lc
        spec.loader.exec_module(lc)
        cand = lc.Candidate(path="scripts/check_rung_attribution.py",
                            frames=("tracked", "worktree"))
        cand = lc.classify(REPO, cand, allow_writers=False)
        self.assertTrue(cand.admitted, cand.reason)


if __name__ == "__main__":
    unittest.main()
