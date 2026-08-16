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

#: A session UUID that is deliberately NOT one this box has ever run. The
#: probe controls build fake transcripts under it, so a mutant that ignores
#: the --transcripts override searches the real harness state and finds
#: nothing, instead of quietly passing on a real transcript.
SESSION_C = "0f0e0d0c-0b0a-0908-0706-050403020100"


#: Two per-agent handles, shaped exactly as the harness names its own
#: per-subagent transcripts: `agent-<hex>.jsonl` under
#: `~/.claude/projects/<slug>/<session-uuid>/subagents/`.
AGENT_1 = "agent-afa60c3f2045c7ce3"
AGENT_2 = "agent-afc0fa9cd734f6641"

#: THE NEVER-VARIED WORDING, TYPED OUT HERE, and imported from nowhere -- for
#: this file's opening reason. Reading it off the module under test
#: (`ra._NEVER_VARIED`) would move both sides of every assertion together, so a
#: mutant that printed the phrase unconditionally would still be green. D235's
#: defect was that this phrase was appended to the identity reading as a
#: CONSTANT, so the instrument said the discriminating field had never varied
#: while printing `2 per-agent` beside it. The assertions below are on the
#: IDENTITY of the wording emitted for a given reading -- never on how much
#: text came out -- because a probe that asserts a COUNT survives an inverted
#: comparison, which has been caught in this lab three times.
NEVER_VARIED = "has never varied"


def trailer(session: str, tag: str = "-", host: str = HOST,
            agent: str | None = None) -> str:
    line = f"Lab-Agent: {host}/{session}/{tag}"
    return f"{line}/{agent}" if agent else line


def fake_transcripts(root: Path, session: str,
                     contents: dict[str, str]) -> Path:
    """A stand-in for `~/.claude/projects/<slug>/<session>/subagents/`.

    The controls must never read the real harness state of whatever box they
    run on: a box with no transcripts would make the negative half pass for the
    wrong reason, and a box with real ones would make it flaky.
    """
    d = root / "projects" / "-a-project" / session / "subagents"
    d.mkdir(parents=True, exist_ok=True)
    for name, text in contents.items():
        (d / f"{name}.jsonl").write_text(text, encoding="utf-8")
    return root / "projects"


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
        state, ident, _, agent = ra.parse_trailer(
            trailer(SESSION_A) + "\n" + trailer(SESSION_B))
        self.assertEqual(state, "duplicate")
        self.assertIsNone(ident)
        self.assertIsNone(agent)

    def test_the_emitter_and_the_grammar_agree(self):
        """What --emit-trailer prints must parse. Otherwise the mechanism emits
        exactly what it rejects, and every adopter reads MALFORMED."""
        line, why = ra.local_identity("some.tag-1")
        self.assertIsNotNone(line, why)
        state, ident, tag, agent = ra.parse_trailer(line)
        self.assertEqual(state, "ok")
        self.assertEqual(tag, "some.tag-1")
        self.assertIsNone(agent, "an unprobed emit must not claim an agent id")
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


# ---------------------------------------------------------------------------
# THE PER-AGENT IDENTITY -- D173's defect, and the half that decides
# ---------------------------------------------------------------------------

class ThePerAgentIdentity(_Tmp):
    """D173: one identity across one hundred percent of the deployed life.

    Session granularity cannot separate two agents of one chief, and on this box
    a chief runs three to five at once, so every same-chief pair graded AUTHOR
    and no real pair ever returned NON-AUTHOR. These are the cases that decide
    whether the fourth field repaired that or merely renamed it.
    """

    def test_a_same_session_pair_with_different_agents_is_non_author(self):
        """THE POSITIVE HALF OF THE REPAIR, and the case D173 says never fired.

        One chief session, two dispatched agents, and the checker separates
        them. Before the fourth field existed this pairing was AUTHOR.
        """
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A, agent=AGENT_1))
        g1 = r.commit("the work", trailer(SESSION_A, "builder", agent=AGENT_1))
        closing = r.commit("rung closed",
                           trailer(SESSION_A, "grader", agent=AGENT_2))

        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", g1)
        self.assertEqual(verdict_of(p), "NON-AUTHOR", p.stdout)
        self.assertEqual(p.returncode, RC_PASS, p.stdout)
        self.assertIn("GRANULARITY: agent", p.stdout)
        # Name the thing, do not count it: the verdict must be about THESE two
        # handles. A count would survive an inverted comparison.
        self.assertIn(AGENT_2, p.stdout)
        self.assertIn(AGENT_1, p.stdout)

    def test_the_same_agent_on_both_sides_is_still_caught(self):
        """THE MUST-NOT-MATCH HALF. A genuine author must not be cleared.

        This is the sharp one: the repair widens the only path to NON-AUTHOR,
        so if it also cleared an agent grading its own work it would have turned
        the check into a rubber stamp.
        """
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A, agent=AGENT_1))
        g1 = r.commit("the work", trailer(SESSION_A, "me", agent=AGENT_1))
        closing = r.commit("I graded my own work",
                           trailer(SESSION_A, "also-me", agent=AGENT_1))

        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", g1)
        self.assertEqual(verdict_of(p), "AUTHOR", p.stdout)
        self.assertEqual(p.returncode, RC_FAIL, p.stdout)
        self.assertIn("GRANULARITY: agent", p.stdout)
        self.assertIn(g1[:8], p.stdout)

    def test_an_agent_id_on_only_the_closing_side_does_not_upgrade(self):
        """A handle on one side is not evidence of anything about the other."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        g1 = r.commit("the work", trailer(SESSION_A, "builder"))
        closing = r.commit("closed", trailer(SESSION_A, "grader", agent=AGENT_2))

        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", g1)
        self.assertEqual(verdict_of(p), "AUTHOR", p.stdout)
        self.assertEqual(p.returncode, RC_FAIL)
        self.assertIn("GRANULARITY: session", p.stdout)

    def test_an_agent_id_on_only_the_graded_side_does_not_upgrade(self):
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        g1 = r.commit("the work", trailer(SESSION_A, "builder", agent=AGENT_1))
        closing = r.commit("closed", trailer(SESSION_A, "grader"))

        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", g1)
        self.assertEqual(verdict_of(p), "AUTHOR", p.stdout)
        self.assertEqual(p.returncode, RC_FAIL)
        self.assertIn("GRANULARITY: session", p.stdout)

    def test_a_session_only_trailer_still_parses(self):
        """Backward compatibility is not a nicety here.

        The four trailers this mechanism has ever emitted are three-field. If
        the repair made them MALFORMED it would turn the integrity run red on
        history nobody can rewrite, and the check would be deleted.
        """
        state, ident, tag, agent = ra.parse_trailer(
            "Lab-Agent: ip-172-31-43-247/"
            "64b13819-ff95-4d4d-a50f-3720bab19084/-")
        self.assertEqual(state, "ok")
        self.assertEqual(
            ident, "ip-172-31-43-247/64b13819-ff95-4d4d-a50f-3720bab19084")
        self.assertEqual(tag, "-")
        self.assertIsNone(agent)

    def test_a_fourth_field_that_is_not_an_agent_handle_is_malformed(self):
        for bad in ("Lab-Agent: h/" + SESSION_A + "/-/notanagent",
                    "Lab-Agent: h/" + SESSION_A + "/-/agent-ZZZZZZ",
                    "Lab-Agent: h/" + SESSION_A + "/-/agent-ab",
                    "Lab-Agent: h/" + SESSION_A + "/-/agent-ab/agent-cd"):
            self.assertEqual(ra.parse_trailer(bad)[0], "malformed", bad)

    def test_distinct_agents_needs_two_well_formed_and_different_handles(self):
        def c(agent):
            return ra.Commit(sha="x" * 40, when="", subject="", state="ok",
                             identity="h/" + SESSION_A, agent=agent)
        self.assertFalse(ra.distinct_agents(c(None), c(AGENT_1)))
        self.assertFalse(ra.distinct_agents(c(AGENT_1), c(None)))
        self.assertFalse(ra.distinct_agents(c(AGENT_1), c(AGENT_1)))
        self.assertFalse(ra.distinct_agents(c("agent-ZZ"), c(AGENT_1)))
        self.assertTrue(ra.distinct_agents(c(AGENT_1), c(AGENT_2)))


class TheProbeReadsTheIdentityRatherThanTakingIt(_Tmp):
    """The fourth field is only worth having because it is not typed.

    `<tag>` has existed since the mechanism shipped and has never been allowed
    to decide, for the reason D132 gives: a copied dispatch brief duplicates a
    typed field by accident. So the probe is a LOOKUP KEY and the value it finds
    is read off the harness's own per-subagent transcripts.
    """

    def test_a_probe_in_exactly_one_transcript_resolves_to_that_agent(self):
        root = fake_transcripts(self.tmp / "h", SESSION_C, {
            AGENT_1: '{"x":"...PROBE-TOKEN-abc123..."}\n',
            AGENT_2: '{"x":"something else entirely"}\n'})
        got, why = ra.find_own_agent("PROBE-TOKEN-abc123", SESSION_C, root)
        self.assertEqual(got, AGENT_1, why)

    def test_a_probe_in_two_transcripts_is_refused_not_guessed(self):
        """The copied-brief accident, and the one it must not resolve.

        A second agent typing a token a first agent already used produces two
        matches. Picking either would attribute a commit to the wrong agent,
        and picking the first would do it silently.
        """
        root = fake_transcripts(self.tmp / "h", SESSION_C, {
            AGENT_1: "PROBE-TOKEN-abc123\n",
            AGENT_2: "PROBE-TOKEN-abc123\n"})
        got, why = ra.find_own_agent("PROBE-TOKEN-abc123", SESSION_C, root)
        self.assertIsNone(got)
        self.assertIn("2 subagent transcripts", why)

    def test_a_probe_in_no_transcript_is_refused(self):
        root = fake_transcripts(self.tmp / "h", SESSION_C,
                                {AGENT_1: "nothing to see\n"})
        got, why = ra.find_own_agent("PROBE-TOKEN-abc123", SESSION_C, root)
        self.assertIsNone(got)
        self.assertIn("appears in no subagent transcript", why)

    def test_a_short_probe_is_refused_before_it_is_searched(self):
        """A three-character token matches by accident, and an accidental match
        names the wrong agent -- which is worse than naming none."""
        root = fake_transcripts(self.tmp / "h", SESSION_C, {AGENT_1: "abc\n"})
        got, why = ra.find_own_agent("abc", SESSION_C, root)
        self.assertIsNone(got)
        self.assertIn("not usable", why)

    def test_a_transcript_filename_that_is_not_a_handle_is_not_returned(self):
        """The value goes into a commit message and is read back by the grammar
        in this same file. A filename the grammar rejects must never be emitted,
        or the emitter produces exactly what the checker calls MALFORMED."""
        root = fake_transcripts(self.tmp / "h", SESSION_C, {
            "agent-NOTHEX": "PROBE-TOKEN-abc123\n",
            AGENT_1: "PROBE-TOKEN-abc123\n"})
        got, why = ra.find_own_agent("PROBE-TOKEN-abc123", SESSION_C, root)
        self.assertEqual(got, AGENT_1, why)

    def test_a_transcript_of_another_session_is_not_searched(self):
        root = fake_transcripts(self.tmp / "h", SESSION_B,
                                {AGENT_1: "PROBE-TOKEN-abc123\n"})
        got, why = ra.find_own_agent("PROBE-TOKEN-abc123", SESSION_C, root)
        self.assertIsNone(got)
        del why

    def test_emit_with_a_probe_yields_a_four_field_trailer_that_parses(self):
        from unittest import mock
        root = fake_transcripts(self.tmp / "h", SESSION_C,
                                {AGENT_1: "PROBE-TOKEN-abc123\n"})
        with mock.patch.dict(os.environ,
                             {"CLAUDE_CODE_SESSION_ID": SESSION_C}):
            line, why = ra.local_identity("grader", "PROBE-TOKEN-abc123", root)
        self.assertIsNotNone(line, why)
        state, ident, tag, agent = ra.parse_trailer(line)
        self.assertEqual(state, "ok")
        self.assertEqual(agent, AGENT_1)
        self.assertEqual(tag, "grader")
        del ident

    def test_an_unresolvable_probe_emits_nothing_rather_than_the_weaker_line(self):
        """The whole defect in one sentence: a session-granularity identity
        handed to a caller who asked for a per-agent one gets cited as the
        per-agent evidence it is not."""
        from unittest import mock
        root = fake_transcripts(self.tmp / "h", SESSION_C, {AGENT_1: "x\n"})
        with mock.patch.dict(os.environ,
                             {"CLAUDE_CODE_SESSION_ID": SESSION_C}):
            line, why = ra.local_identity("grader", "PROBE-TOKEN-abc123", root)
        self.assertIsNone(line)
        self.assertIn("appears in no subagent transcript", why)
        self.assertIn("Emitting nothing", why)

    def test_the_cli_refuses_an_unresolvable_probe_and_exits_unknown(self):
        r = self.repo()
        root = fake_transcripts(self.tmp / "h", SESSION_C, {AGENT_1: "x\n"})
        p = run(r, "--emit-trailer", "--probe", "PROBE-TOKEN-abc123",
                "--transcripts", str(root),
                env={"CLAUDE_CODE_SESSION_ID": SESSION_C})
        self.assertEqual(p.stdout.strip(), "", "emitted a weaker line anyway")
        self.assertEqual(p.returncode, RC_UNKNOWN)

    def test_a_session_that_is_not_a_uuid_is_refused_before_any_search(self):
        """The session id SCOPES the search, so a field that is not one must
        stop it rather than widen it.

        Built so that removing the guard would SUCCEED rather than merely
        differ: a transcript carrying the probe is planted at exactly the path
        an unguarded search would glob, so the unguarded module resolves a
        handle and this test sees a handle where there must be none.
        """
        root = fake_transcripts(self.tmp / "h", "not-a-uuid-at-all",
                                {AGENT_1: "PROBE-TOKEN-abc123\n"})
        got, why = ra.find_own_agent("PROBE-TOKEN-abc123", "not-a-uuid-at-all",
                                     root)
        self.assertIsNone(got, "searched a session field that is not a UUID")
        self.assertIn("is not a UUID", why)

    def test_a_missing_transcript_root_is_named_not_read_as_no_match(self):
        """An environment that CANNOT answer and an environment that answered
        NO are different states, and only one of them is about the probe.

        Asserted on the IDENTITY of the reason rather than on the refusal
        alone: both the guarded and the unguarded module return None here, and
        the only thing that separates them is which reason they give. A test
        that asserted only `assertIsNone` would pass on both.
        """
        missing = self.tmp / "no-such-transcript-root"
        self.assertFalse(missing.exists())
        got, why = ra.find_own_agent("PROBE-TOKEN-abc123", SESSION_C, missing)
        self.assertIsNone(got)
        self.assertIn("no transcript root", why)
        self.assertNotIn("appears in no subagent transcript", why)

    def test_a_failed_probe_puts_its_refusal_on_stderr_and_no_trailer_anywhere(self):
        """WHICH STREAM, for WHICH probe -- not how many bytes.

        The published adoption line is `--emit-trailer --probe <token> >>
        <msgfile>`, so stdout is spliced into a durable record and stderr is
        not. A refusal that moved to stdout would be appended INTO the commit
        message; a trailer emitted despite the failure would be cited as the
        per-agent evidence it is not. Both are assertions about identity of
        content per stream, and a byte-count assertion would survive either.
        """
        r = self.repo()
        root = fake_transcripts(self.tmp / "h", SESSION_C, {AGENT_1: "x\n"})
        p = run(r, "--emit-trailer", "--probe", "PROBE-TOKEN-unresolvable1",
                "--transcripts", str(root),
                env={"CLAUDE_CODE_SESSION_ID": SESSION_C})
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertNotIn("Lab-Agent:", p.stdout,
                         "a failed probe put a trailer on the appended stream")
        self.assertIn("PROBE-TOKEN-unresolvable1", p.stderr)
        self.assertIn("appears in no subagent transcript", p.stderr)
        self.assertIn("Emitting nothing", p.stderr)

    def test_the_published_append_form_can_never_gain_a_trailer_from_a_failure(self):
        """D245: the published `>> <msgfile>` form appends NOTHING when the
        probe fails, so the commit lands with no identity and reads exactly
        like a healthy one -- the exit code is the only signal the caller gets.

        WHAT IS ASSERTED HERE IS THE SAFETY HALF, and deliberately not the
        defect: a failed probe must never append anything that could parse as a
        trailer, and it must report a non-zero status. That both must hold
        under ANY repair of D245 is the reason they are pinned; that the file
        comes back byte-identical is the DEFECT and is recorded in D245 rather
        than asserted here, so repairing it does not redden this test.
        """
        r = self.repo()
        root = fake_transcripts(self.tmp / "h", SESSION_C, {AGENT_1: "x\n"})
        msg = self.tmp / "commit-message.txt"
        msg.write_text("subject line\n\nbody paragraph\n", encoding="utf-8")
        p = run(r, "--emit-trailer", "--probe", "PROBE-TOKEN-unresolvable2",
                "--transcripts", str(root),
                env={"CLAUDE_CODE_SESSION_ID": SESSION_C})
        with msg.open("a", encoding="utf-8") as fh:   # exactly what `>>` does
            fh.write(p.stdout)
        landed = msg.read_text(encoding="utf-8")
        self.assertEqual(p.returncode, RC_UNKNOWN,
                         "a failed probe reported success to the caller")
        self.assertNotIn("Lab-Agent:", landed,
                         "a failed probe appended a trailer to the message")

    def test_the_cli_emits_the_resolved_handle(self):
        r = self.repo()
        root = fake_transcripts(self.tmp / "h", SESSION_C,
                                {AGENT_1: "PROBE-TOKEN-abc123\n"})
        p = run(r, "--emit-trailer", "--probe", "PROBE-TOKEN-abc123",
                "--transcripts", str(root),
                env={"CLAUDE_CODE_SESSION_ID": SESSION_C})
        self.assertEqual(
            p.stdout.strip(),
            f"Lab-Agent: {ra.local_identity()[0].split(': ')[1].split('/')[0]}"
            f"/{SESSION_C}/-/{AGENT_1}", p.stderr)
        self.assertEqual(p.returncode, RC_PASS)


# ---------------------------------------------------------------------------
# WHAT THE CHECK REFUSES TO CLAIM -- printed, not merely documented
# ---------------------------------------------------------------------------

class TheOutputCarriesItsOwnLimits(_Tmp):

    def test_every_run_prints_the_backfill_statement(self):
        """Backfill is impossible for the 1,849+ commits before the anchor, and
        that has to be where the verdict is, or a green reads as covering
        earlier work."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        for args in (("--anchor", anchor),
                     ("--anchor", anchor, "--closing", anchor,
                      "--graded", anchor)):
            p = run(r, *args)
            self.assertIn("BACKFILL IS IMPOSSIBLE", p.stdout, args)
            self.assertIn("REFUSES TO CLAIM", p.stdout, args)
            self.assertIn("GRANULARITY:", p.stdout, args)

    def test_one_identity_observed_says_it_has_not_been_shown_to_discriminate(self):
        """D173's number, in the frame, in words.

        Four runs of a constant are not four confirmations, and the count is the
        single fact that tells a reader what a green run is worth.
        """
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        r.commit("more of the same", trailer(SESSION_A, "other"))
        p = run(r, "--anchor", anchor)
        self.assertIn("ONE CONSTANT OBSERVED", p.stdout)
        self.assertIn("distinct identities observed", p.stdout)
        self.assertIn("1 session, 0 per-agent", p.stdout)

    def test_per_agent_handles_are_counted_in_the_integrity_frame(self):
        """Sessions and agents are counted separately, because one session with
        two agents in it is a different state from two sessions -- and it is the
        state this box is actually in."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A, agent=AGENT_1))
        r.commit("someone else in the same chief",
                 trailer(SESSION_A, "b", agent=AGENT_2))
        p = run(r, "--anchor", anchor, "--json")
        frame = json.loads(p.stdout)
        self.assertEqual(frame["stats"]["distinct_sessions"], 1, frame)
        self.assertEqual(frame["stats"]["distinct_agents"], 2, frame)
        self.assertNotIn("ONE CONSTANT OBSERVED", frame["discrimination"])

    def test_two_identities_observed_drops_the_never_varied_wording(self):
        """The must-not-match half of the notice: it has to stop saying it once
        the field HAS varied, or it is a slogan and not a measurement."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        r.commit("someone else", trailer(SESSION_B))
        p = run(r, "--anchor", anchor)
        self.assertNotIn("ONE CONSTANT OBSERVED", p.stdout)
        self.assertIn("2 distinct session identities", p.stdout)

    def test_the_identities_gloss_is_derived_from_the_reading_beside_it(self):
        """D235: the gloss must be a function of the two numbers it glosses.

        Driven directly, one reading at a time. A reading where the field has
        NOT varied must carry the never-varied wording; every reading where it
        HAS varied must not. Replacing the branch with a literal -- the defect
        this pins -- fails at least one arm whichever literal is chosen.
        """
        varied = ((1, 1), (1, 2), (2, 0), (2, 2), (3, 5))
        for sessions, agents in varied:
            row = ra._identities_row(sessions, agents)
            self.assertIn(f"{sessions} session, {agents} per-agent", row)
            self.assertNotIn(NEVER_VARIED, row, (sessions, agents, row))
        for sessions, agents in ((0, 0), (1, 0)):
            row = ra._identities_row(sessions, agents)
            self.assertIn(f"{sessions} session, {agents} per-agent", row)
            self.assertIn(NEVER_VARIED, row, (sessions, agents, row))

    def test_the_printed_frame_row_stops_saying_never_varied_once_it_has(self):
        """The same assertion through the real tool, on real commits, because a
        derivation that is never wired into the row it feeds is not a repair.

        Two agents inside ONE chief session: the reading is `1 session,
        2 per-agent`, and the never-varied wording must be absent from the
        WHOLE output -- the frame row included, which is where it used to be
        printed as a constant.
        """
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A, agent=AGENT_1))
        r.commit("a second agent in the same chief",
                 trailer(SESSION_A, "b", agent=AGENT_2))
        p = run(r, "--anchor", anchor)
        self.assertIn("1 session, 2 per-agent", p.stdout)
        self.assertNotIn(NEVER_VARIED, p.stdout)

    def test_the_printed_frame_row_does_say_never_varied_when_it_has_not(self):
        """The must-match half of the pair above. Without it, a repair that
        deleted the wording outright would pass every assertion, and deleting
        the caveat is a worse defect than printing it in the wrong place."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        r.commit("the same one again", trailer(SESSION_A, "other"))
        p = run(r, "--anchor", anchor)
        self.assertIn("1 session, 0 per-agent", p.stdout)
        self.assertIn(NEVER_VARIED, p.stdout)

    def test_the_json_frame_carries_the_granularity_and_the_counts(self):
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A, agent=AGENT_1))
        g1 = r.commit("work", trailer(SESSION_A, "b", agent=AGENT_1))
        closing = r.commit("closed", trailer(SESSION_A, "g", agent=AGENT_2))
        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", g1,
                "--json")
        frame = json.loads(p.stdout)
        self.assertEqual(frame["verdict"], "NON-AUTHOR", frame)
        self.assertEqual(frame["granularity"], "agent", frame)
        self.assertEqual(frame["distinct_agents"], 2, frame)
        self.assertEqual(frame["distinct_sessions"], 1, frame)
        self.assertIn("BACKFILL IS IMPOSSIBLE", frame["refuses_to_claim"])

    def test_a_session_granularity_author_does_not_claim_the_measurer_wrote_it(self):
        """AUTHOR at session granularity means "the same chief session", and a
        chief runs several agents at once. Saying "the measurer is an author"
        there is an overclaim in the other direction."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        g1 = r.commit("work", trailer(SESSION_A, "builder"))
        closing = r.commit("closed", trailer(SESSION_A, "grader"))
        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", g1)
        self.assertEqual(verdict_of(p), "AUTHOR", p.stdout)
        self.assertIn("SESSION identity", p.stdout)
        self.assertIn("does not establish that the measurer personally wrote",
                      p.stdout)


# ---------------------------------------------------------------------------
# THE SELECTORS -- every one of these can SHRINK the graded set, and a graded
# set that lost the author's commit returns a false NON-AUTHOR nobody can see.
# ---------------------------------------------------------------------------

class TheGradedSetIsNeverSilentlySmaller(_Tmp):

    def test_a_range_selector_grades_every_commit_in_the_range(self):
        """`--graded A..B` must not collapse to B.

        Named, not counted: the frame has to list the exact shas, because a
        count is satisfied by any three commits and the defect is about WHICH.
        """
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_B))
        first = r.commit("theirs", trailer(SESSION_B, "a"))
        mine = r.commit("MINE -- the one a collapsed range would drop",
                        trailer(SESSION_A, "b"))
        tip = r.commit("theirs again", trailer(SESSION_B, "c"))
        closing = r.commit("closed", trailer(SESSION_A, "grader"))

        p = run(r, "--anchor", anchor, "--closing", closing,
                "--graded", f"{first}..{tip}", "--json")
        frame = json.loads(p.stdout)
        self.assertEqual(sorted(frame["graded_shas"]), sorted([mine, tip]),
                         frame)
        self.assertEqual(frame["verdict"], "AUTHOR", frame)

    def test_a_selector_matching_nothing_is_named_not_ignored(self):
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        closing = r.commit("closed", trailer(SESSION_B))
        p = run(r, "--anchor", anchor, "--closing", closing,
                "--graded", f"{closing}..{closing}")
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertIn("resolved to zero commits", p.stdout)

    def test_an_unresolvable_graded_spec_is_unknown_never_a_verdict(self):
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        g1 = r.commit("work", trailer(SESSION_A))
        closing = r.commit("closed", trailer(SESSION_B))
        p = run(r, "--anchor", anchor, "--closing", closing,
                "--graded", g1, "--graded", "0" * 40)
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertIn("cannot resolve", p.stdout)

    def test_read_commits_reports_a_bad_rev_rather_than_dropping_it(self):
        """The same defect one layer down, where `resolve` cannot catch it: a
        commit that fails to read must abort the answer, not shrink the set."""
        r = self.repo()
        good = r.commit("work", trailer(SESSION_A))
        commits, err = ra.read_commits(r.root, [good, "0" * 40], None)
        self.assertEqual(commits, [])
        self.assertIn("git log failed", err)

    def test_the_same_commit_named_twice_is_graded_once(self):
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        g1 = r.commit("work", trailer(SESSION_A))
        closing = r.commit("closed", trailer(SESSION_B))
        p = run(r, "--anchor", anchor, "--closing", closing,
                "--graded", g1, "--graded", g1, "--json")
        frame = json.loads(p.stdout)
        self.assertEqual(frame["graded_shas"], [g1], frame)

    def test_a_closing_spec_naming_more_than_one_commit_is_refused(self):
        """`--closing` is the MEASURER. Taking the first of a range picks an
        arbitrary one and drops the rest without saying so."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        a = r.commit("one", trailer(SESSION_B))
        b = r.commit("two", trailer(SESSION_B))
        g1 = r.commit("work", trailer(SESSION_A))
        p = run(r, "--anchor", anchor, "--closing", f"{anchor}..{b}",
                "--graded", g1)
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertIn("must name exactly one", p.stdout)
        del a

    def test_a_closing_commit_inside_its_own_graded_set_is_author(self):
        """A dispatch error, surfaced rather than tidied away. Filtering it out
        would turn "you graded your own closing commit" into a clean answer."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        closing = r.commit("closed", trailer(SESSION_B, "grader"))
        p = run(r, "--anchor", anchor, "--closing", closing, "--graded", closing)
        self.assertEqual(verdict_of(p), "AUTHOR", p.stdout)
        self.assertEqual(p.returncode, RC_FAIL)

    def test_graded_without_closing_exits_unknown_with_a_reason(self):
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        p = run(r, "--anchor", anchor, "--graded", anchor)
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertIn("no attribution question without a measurer", p.stderr)


# ---------------------------------------------------------------------------
# THE INTEGRITY RUN'S OWN FAIL-OPEN SHAPES
# ---------------------------------------------------------------------------

class TheIntegrityRunNeverPassesFromNothing(_Tmp):

    def test_zero_adoption_since_the_anchor_is_unknown_not_pass(self):
        """B1's shape at the top level: no commit carries an identity, so there
        is nothing to check, so the answer is not PASS."""
        r = self.repo()
        anchor = r.commit("anchor with no trailer at all")
        r.commit("nor this one")
        p = run(r, "--anchor", anchor)
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertIn("nothing here to check", p.stdout)

    def test_zero_commits_examined_is_unknown_naming_b1(self):
        verdict, why, stats = ra.integrity([], [])
        self.assertEqual(verdict, "UNKNOWN")
        self.assertIn("B1", why)
        self.assertEqual(stats["examined"], 0)

    def test_a_duplicate_trailer_is_a_broken_emitter_not_an_adoption_gap(self):
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        r.commit("two claims",
                 trailer(SESSION_A, "one") + "\n" + trailer(SESSION_B, "two"))
        p = run(r, "--anchor", anchor)
        self.assertEqual(verdict_of(p), "FAIL", p.stdout)
        self.assertEqual(p.returncode, RC_FAIL)
        self.assertIn("duplicate", p.stdout)

    def test_the_pass_reason_states_the_adoption_ratio_not_the_examined_count(self):
        """The ratio is the number that says what the PASS is worth. Printing
        `4 of 4` where the truth is `2 of 4` is the whole defect D173 filed."""
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        r.commit("adopted", trailer(SESSION_B))
        r.commit("did not")
        r.commit("nor did this")
        p = run(r, "--anchor", anchor)
        self.assertEqual(verdict_of(p), "PASS", p.stdout)
        self.assertIn("(2 of 4 commits carry one)", p.stdout)

    def test_an_anchor_on_another_branch_is_unknown_and_says_so(self):
        """A branch that does not contain the mechanism's starting commit has
        no range to check, and the range it would compute is not the one the
        frame claims."""
        r = self.repo()
        r.commit("base", trailer(SESSION_A))
        r._git("checkout", "-q", "-b", "side")
        side = r.commit("side work", trailer(SESSION_A), fname="side.txt")
        r._git("checkout", "-q", "main")
        r.commit("main work", trailer(SESSION_B), fname="main.txt")
        p = run(r, "--anchor", side)
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertIn("not a descendant of the anchor", p.stdout)

    def test_an_unanchored_build_is_unknown_and_names_the_reason(self):
        """Right verdict, wrong reason sends the next reader to the wrong
        repair: an unanchored BUILD and an absent anchor are different faults."""
        r = self.repo()
        r.commit("anything", trailer(SESSION_A))
        saved = ra.ANCHOR
        try:
            ra.ANCHOR = None
            verdict, frame = ra.run_integrity(r.root, True)
        finally:
            ra.ANCHOR = saved
        self.assertEqual(verdict, "UNKNOWN")
        self.assertIn("not anchored", frame["reason"])

    def test_a_range_that_comes_back_empty_is_an_error_not_a_clean_sheet(self):
        r = self.repo()
        base = r.commit("base", trailer(SESSION_A))
        anchor = r.commit("anchor", trailer(SESSION_A))
        shas, err = ra._since_anchor(r.root, anchor, base)
        self.assertEqual(shas, [])
        self.assertIn("range is empty", err)

    def test_a_pre_anchor_sweep_that_cannot_run_is_unknown_not_clean(self):
        """The instrument's one FAIL condition, switched off by a non-zero exit
        code nobody reads. A sweep that did not run has found nothing in the
        sense that matters, and reporting it as clean is the fail-open shape."""
        r = self.repo()
        r.commit("base carrying no trailer")
        anchor = r.commit("anchor", trailer(SESSION_A))
        claims, err = ra._pre_anchor_claims(r.root, anchor)
        self.assertEqual((claims, err), ([], ""))
        claims, err = ra._pre_anchor_claims(r.root, "0" * 40)
        self.assertIn("is not a commit in this repository", err)
        self.assertEqual(claims, [])
        # And the same shape one level down: an absent rev is not a root commit.
        self.assertEqual(ra._has_parent(r.root, anchor), (True, ""))
        self.assertIsNone(ra._has_parent(r.root, "0" * 40)[0])

    def test_the_integrity_run_reports_a_sweep_that_could_not_run(self):
        """The unit refusing is not enough: the caller has to carry the refusal
        to the verdict. A guard that returns an error nobody reads is a guard
        that does not exist."""
        from unittest import mock
        r = self.repo()
        anchor = r.commit("anchor", trailer(SESSION_A))
        saved = ra.ANCHOR
        try:
            ra.ANCHOR = anchor
            with mock.patch.object(ra, "_pre_anchor_claims",
                                   return_value=([], "the sweep did not run")):
                verdict, frame = ra.run_integrity(r.root, True)
        finally:
            ra.ANCHOR = saved
        self.assertEqual(verdict, "UNKNOWN")
        self.assertIn("the sweep did not run", frame["reason"])

    def test_a_root_anchor_has_no_ancestry_to_sweep(self):
        r = self.repo()
        anchor = r.commit("root anchor", trailer(SESSION_A))
        claims, err = ra._pre_anchor_claims(r.root, anchor)
        self.assertEqual((claims, err), ([], ""))

    def test_the_pre_anchor_sweep_walks_both_parents_of_a_merge(self):
        """`<anchor>~1` walks the first-parent side only and reports a clean
        zero over the half it never opened. A merge anchor has two."""
        r = self.repo()
        r.commit("base", trailer(SESSION_A))
        r._git("checkout", "-q", "-b", "side")
        smuggled = r.commit("a trailer on the second-parent side",
                            trailer(SESSION_B), fname="side.txt")
        r._git("checkout", "-q", "main")
        r.commit("main moves", trailer(SESSION_A), fname="main.txt")
        r._git("merge", "-q", "--no-ff", "-m", "merge anchor", "side")
        anchor = r._git("rev-parse", "HEAD").stdout.strip()
        claims, err = ra._pre_anchor_claims(r.root, anchor)
        self.assertEqual(err, "")
        self.assertIn(smuggled, claims)


# ---------------------------------------------------------------------------
# THE GRAMMAR AND THE EMITTER, WHICH MUST AGREE IN BOTH DIRECTIONS
# ---------------------------------------------------------------------------

class TheEmitterCannotProduceWhatTheGrammarRejects(_Tmp):

    def test_the_host_distinguishes_two_commits_of_the_same_session_id(self):
        """A session UUID is unique per box, not per world. Dropping the host
        merges two machines' sessions into one identity."""
        a = ra.parse_trailer(trailer(SESSION_A, host="box-one"))[1]
        b = ra.parse_trailer(trailer(SESSION_A, host="box-two"))[1]
        self.assertNotEqual(a, b)
        self.assertEqual(a, f"box-one/{SESSION_A}")

    def test_a_tag_with_a_separator_or_a_space_is_malformed(self):
        for bad in (f"Lab-Agent: h/{SESSION_A}/two words",
                    f"Lab-Agent: h/{SESSION_A}/a/b",
                    f"Lab-Agent: h/{SESSION_A}/"):
            self.assertEqual(ra.parse_trailer(bad)[0], "malformed", bad)

    def test_a_tab_separated_broken_line_is_malformed_not_absent(self):
        """"the emitter is broken" and "this agent did not adopt" are different
        findings, and only one of them is a FAIL."""
        self.assertEqual(ra.parse_trailer("Lab-Agent:\tnonsense")[0],
                         "malformed")

    def test_a_hostile_hostname_is_sanitised_into_something_that_parses(self):
        import types
        from unittest import mock
        fake = types.SimpleNamespace(nodename="ip 172/31:43")
        with mock.patch.object(ra.os, "uname", return_value=fake):
            line, why = ra.local_identity("t")
        self.assertIsNotNone(line, why)
        state, ident, _, _ = ra.parse_trailer(line)
        self.assertEqual(state, "ok")
        self.assertEqual(ident.split("/")[0], "ip-172-31-43")

    def test_a_hostname_with_no_usable_field_emits_nothing(self):
        import types
        from unittest import mock
        fake = types.SimpleNamespace(nodename="!!!")
        with mock.patch.object(ra.os, "uname", return_value=fake):
            line, why = ra.local_identity("t")
        self.assertIsNone(line)
        self.assertIn("no usable host field", why)

    def test_a_hostile_tag_is_sanitised_into_something_that_parses(self):
        line, why = ra.local_identity("grader/v13 round 8")
        self.assertIsNotNone(line, why)
        state, _, tag, _ = ra.parse_trailer(line)
        self.assertEqual(state, "ok")
        self.assertEqual(tag, "grader-v13-round-8")

    def test_an_empty_tag_becomes_the_no_tag_marker(self):
        line, why = ra.local_identity("")
        self.assertIsNotNone(line, why)
        self.assertEqual(ra.parse_trailer(line)[0], "ok")
        self.assertEqual(ra.parse_trailer(line)[2], "-")

    def test_a_non_uuid_session_emits_nothing_and_exits_unknown(self):
        p = subprocess.run(
            [sys.executable, str(CHECKER), "--emit-trailer"],
            capture_output=True, text=True,
            env={**os.environ, "CLAUDE_CODE_SESSION_ID": "not-a-uuid"})
        self.assertEqual(p.stdout.strip(), "")
        self.assertEqual(p.returncode, RC_UNKNOWN)
        self.assertIn("is not a UUID", p.stderr)

    def test_a_body_carrying_the_unit_separator_keeps_its_trailer(self):
        """The record separator is a control character, and a commit body is
        free to contain one. Splitting without a bound truncates the body there
        and turns an identity into an absence."""
        parts, err = ra._split_record(
            "sha\x1fwhen\x1fsubject\x1fline one\x1fLab-Agent: x")
        self.assertEqual(err, "")
        self.assertEqual(parts[3], "line one\x1fLab-Agent: x")
        parts, err = ra._split_record("sha\x1fwhen")
        self.assertEqual(parts, [])
        self.assertIn("not 4", err)

    def test_an_unknown_ancestry_is_not_reported_as_predating_the_anchor(self):
        """`merge-base --is-ancestor` answers 0, 1 or an error, and the error is
        not a No. Reading it as one labels a commit PRE_ANCHOR and tells the
        reader backfill is why it has no identity."""
        r = self.repo()
        naked = r.commit("no trailer here")
        closing = r.commit("closed", trailer(SESSION_B))
        self.assertIsNone(ra._is_after_anchor(r.root, naked, "0" * 40))
        p = run(r, "--anchor", "0" * 40, "--closing", closing, "--graded", naked)
        self.assertEqual(verdict_of(p), "UNKNOWN", p.stdout)
        self.assertNotIn("predate", p.stdout.lower())

    def test_no_anchor_at_all_is_unknown_rather_than_after(self):
        """An unanchored build knows NOTHING about where a commit sits, and
        `True` there would be a claim.

        PINNED AT THE FUNCTION BOUNDARY ON PURPOSE, and the reason is recorded
        because it is the difference between a proof and a decoration: the only
        consumer of this value tests `after is False`, which `None` and `True`
        both fail, and `Commit.after_anchor` is stored and never read again. So
        the distinction is currently INERT downstream and no end-to-end test
        can reach it -- the same shape D231 recorded for three other guards
        here. It is asserted anyway, because the value is what a future reader
        of that field would rely on, and D246 records that the field is
        write-only.
        """
        r = self.repo()
        sha = r.commit("the only commit", trailer(SESSION_A))
        self.assertIsNone(ra._is_after_anchor(r.root, sha, None))
        self.assertIsNone(ra._is_after_anchor(r.root, sha, ""))


if __name__ == "__main__":
    unittest.main()
