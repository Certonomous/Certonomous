"""The auto-stop gate decides whether this box lives, and it lives outside the repo.

Why this file exists
--------------------
`/usr/local/bin/auto-stop.sh` powers the machine off after an idle interval. It
is root-owned, outside the tree, and therefore invisible to every repo-scoped
sweep (L-75). On 2026-07-30 a repaired version was written to
`scripts/auto-stop.sh.proposed` and never installed; `diff` on 2026-08-12 proved
the live script was still byte-identical to the broken one, and it powered the
box off twice that day -- once in the middle of a verification suite.

So the defect class is not "the gate had a bad regex". It is **a fix that lives
only in the repo cannot be assumed to be running, and nothing was checking.**
These tests are that check.

They are deliberately tolerant of absence: on a laptop or CI box there is no
installed gate, and that is not a failure. What they refuse to tolerate is an
installed gate that has silently drifted from the reviewed one.

A GUARD THAT WAS SATISFIED BY A COMMENT DENYING IT (V15 round 7 F7, docket D96)
-------------------------------------------------------------------------------
Until 2026-08-15 the solver-protection clause -- the one that stops this box
powering off in the middle of an OpenFOAM run -- was guarded by

    self.assertIn("pgrep -x", text)         # text = the raw file

and `scripts/auto-stop.sh:80-81` is a COMMENT reading *"Solvers and meshers,
matched on PROCESS NAME. pgrep -x on the name cannot be triggered by a path, a
comment, or a grep that mentions the name."* Measured on a scratch
`git archive HEAD` copy, control run first: deleting the entire
`if pgrep -x '...'; then keep; fi` block, until
`/usr/bin/grep -c simpleFoam scripts/auto-stop.sh` returned 0, left
`12 passed, 1 skipped` -- byte-identical to the control.

That is a detector whose fixture is the documentation of the thing it detects,
and a substring assertion against a heavily commented file is the general trap.
The repair is in two layers, because the cheap layer is worth keeping:

  * the text assertions now run over LIVE CODE ONLY, comments stripped; and
  * each of the three clauses now has a BEHAVIOURAL test that plants the world
    the clause exists for and requires the gate to decide correctly -- with the
    L-84 must-not-match half beside it, because a gate that holds the box on
    everything is a bill rather than a protection.

The behavioural half is the one that matters: the text assertions can be
satisfied by anything, and the only thing that cannot be faked is running the
script.
"""

from __future__ import annotations

import getpass
import os
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TRACKED = REPO / "scripts" / "auto-stop.sh"
INSTALLED = Path("/usr/local/bin/auto-stop.sh")

#: The clause-(1) process name planted by the behavioural tests below. A real
#: solver name, and NOT read out of the script under test: a check that asks
#: its subject what the right answer is has not checked it. If the clause stops
#: covering `simpleFoam`, that is a change worth reddening for.
PLANTED_SOLVER = "simpleFoam"

#: The user clause (2) filters on, hardcoded in the gate as `pgrep -u ubuntu`.
GATE_USER = "ubuntu"


def live_code(text: str) -> str:
    """The lines of a shell script that EXECUTE -- comments dropped.

    Deliberately conservative: it drops whole-line comments and nothing else,
    so a trailing `# ...` on a live line can still satisfy a substring. That
    residual is why the behavioural tests below exist and why these text
    assertions are a tripwire rather than the guard.
    """
    return "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith("#"))


def idle_world(tmp: Path) -> dict:
    """A fabricated world in which the box is 45 minutes idle and unoccupied.

    No worker, no session transcript, and a marker backdated past the
    threshold, so the gate's own decision is SHUTDOWN unless one of the three
    activity clauses fires. Every behavioural test below starts here and plants
    exactly one thing, so what moved the verdict is never in doubt.
    """
    repo, sessions = tmp / "repo", tmp / "sessions"
    repo.mkdir(exist_ok=True)
    sessions.mkdir(exist_ok=True)
    marker = tmp / "marker"
    marker.touch()
    old = time.time() - 45 * 60
    os.utime(marker, (old, old))
    return {**os.environ, "DRY_RUN": "1", "MARKER": str(marker),
            "REPO": str(repo), "SESSIONS": str(sessions)}


def run_gate(env: dict, timeout: int = 90) -> str:
    return subprocess.run(["bash", str(TRACKED)], env=env,
                          capture_output=True, text=True,
                          timeout=timeout).stdout


# `_read_installed` lived here until 2026-08-14 and was deleted with the
# hand-typed drift comparison it served: reading the installed side is now
# `installed_registry.installed_text`, which also handles the sources a file
# read cannot express (a crontab has no file a normal user can read).


class AutoStopGateTests(unittest.TestCase):
    def test_the_tracked_gate_exists_and_is_the_reviewed_one(self):
        self.assertTrue(
            TRACKED.is_file(),
            f"{TRACKED} is missing. The gate that decides whether this box stays "
            "alive must have a reviewable copy in the tree.",
        )
        # The three activity clauses are the whole point of the 2026-08-12
        # repair. If one is deleted, the gate regresses to the shape that
        # killed two suites, and it should regress loudly.
        #
        # OVER LIVE CODE, NOT OVER THE RAW FILE (D96). Against the raw file,
        # `assertIn("pgrep -x", text)` was satisfied by the COMMENT at
        # `auto-stop.sh:80` -- whose own text says a comment cannot trigger the
        # clause -- and the entire `if pgrep -x ...; then keep; fi` block could
        # be deleted with this suite green. This is a tripwire and not the
        # guard; the guard is `TheClausesAreLiveAndDecideCorrectly` below.
        code = live_code(TRACKED.read_text())
        self.assertIn("pgrep -x", code,
                      "clause 1 (process NAME match) is not in the executable "
                      "text of the gate. A comment about it is not it.")
        self.assertIn("/proc/", code, "clause 2 (CWD match) is not live code")
        self.assertIn(".jsonl", code,
                      "clause 3 (session transcript) is not live code")

    def test_the_string_match_that_caused_the_outage_is_not_back(self):
        """The old gate matched the literal path fragment `Certonomous/sdk`.

        That is what made a relative-path suite invisible AND made a `grep` for
        the pattern count as work. It must not return as an activity predicate.
        """
        text = TRACKED.read_text()
        offenders = [
            line.strip()
            for line in text.splitlines()
            # only executable lines -- the comments explain the bug on purpose
            if "Certonomous/sdk" in line and not line.lstrip().startswith("#")
        ]
        self.assertEqual(
            [],
            offenders,
            "an activity test is matching the literal string `Certonomous/sdk` "
            "again; that predicate misses relative-path work and fires on any "
            "command line that merely mentions it:\n  " + "\n  ".join(offenders),
        )

    def test_installed_gate_has_not_drifted_from_the_tracked_one(self):
        """Delegated to the registry as of 2026-08-14 (D53), on purpose.

        This assertion used to type the two paths in here. That closed the
        incident and not the class: every OTHER artifact with a copy outside
        the tree had the same unguarded gap, and each would have needed its own
        copy of this file. The pairs are now data in
        `scripts/installed_registry.py` and the comparison is one mechanism in
        `sdk/tests/test_installed_matches_tracked.py`.

        What is kept here is the CONNECTION: this gate must still be a
        registered pair. A second comparator typed out beside the first is how
        two checks drift apart and one of them becomes the one nobody reads.
        """
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location(
            "installed_registry_from_autostop_gate",
            REPO / "scripts" / "installed_registry.py")
        reg = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = reg
        spec.loader.exec_module(reg)

        entry = next((d for d in reg.DEPLOYMENTS
                      if d.source == str(INSTALLED)), None)
        self.assertIsNotNone(
            entry,
            f"{INSTALLED} is no longer a registered installed/tracked pair. "
            "The gate that powers this box off must be in "
            "`installed_registry.DEPLOYMENTS`, or nothing is comparing what "
            "runs against what was reviewed -- which is the 2026-07-30 "
            "failure with the tooling removed rather than the file.")
        self.assertEqual(
            str(TRACKED.relative_to(REPO)), entry.tracked,
            "the registered pair for the auto-stop gate does not name the "
            "tracked file this test reviews")

        finding = reg.compare(entry)
        if finding.state == reg.ABSENT:
            self.skipTest(
                f"no readable {INSTALLED} on this host -- nothing is powering "
                f"this box off, so there is nothing to drift ({finding.detail})")
        if finding.state == reg.PENDING:
            # D65, 2026-08-14. A repair to this gate is not the fleet's to
            # install -- docket A4 puts the box's power control with Katie and
            # Sanaa -- so the registry carries a DECLARED divergence with an
            # owner, an expiry and the sha256 of what is expected to still be
            # running. This is not a pass and it is not silence: it prints, and
            # the registry fails the moment the waiver expires or the installed
            # copy becomes anything other than the pinned one. Those
            # fragilities are planted and shown to fire in
            # `test_installed_matches_tracked.py`; duplicating a second waiver
            # register here is exactly the divergence this method was rewritten
            # to stop.
            print(f"\n[auto-stop gate] PENDING INSTALL -- {INSTALLED} is NOT "
                  f"the reviewed copy in the tree, by declaration:\n"
                  f"{finding.detail.strip()}")
            return
        self.assertEqual(
            reg.MATCH, finding.state,
            f"{INSTALLED} differs from {TRACKED}.\n"
            "This is the exact 2026-07-30 failure: a reviewed fix in the tree "
            f"while the machine runs something else.\n{finding.detail}\n"
            f"Reinstall with:\n  {entry.reinstall}",
        )

    def test_the_gate_still_shuts_down_when_genuinely_idle(self):
        """A gate that never fires is not cost control, it is a bill.

        The repair widened what counts as activity, so the failure mode worth
        guarding is the opposite one: that it now keeps the box alive forever.
        Run the real script against a fabricated idle world and require it to
        decide SHUTDOWN.
        """
        if not TRACKED.is_file():
            self.skipTest("no tracked gate")
        import tempfile
        import time

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            repo, sessions = tmp / "repo", tmp / "sessions"
            repo.mkdir()
            sessions.mkdir()
            marker = tmp / "marker"
            marker.touch()
            old = time.time() - 45 * 60
            os.utime(marker, (old, old))

            env = {
                **os.environ,
                "DRY_RUN": "1",
                "MARKER": str(marker),
                "REPO": str(repo),
                "SESSIONS": str(sessions),
            }
            out = subprocess.run(
                ["bash", str(TRACKED)], env=env, capture_output=True, text=True, timeout=60
            ).stdout
            self.assertIn(
                "shutting down",
                out,
                "45 minutes idle, no worker, no session -- the gate must still "
                f"decide to stop. It said:\n{out}",
            )

    def test_a_fresh_session_transcript_keeps_the_box_alive(self):
        """The clause that was missing on 2026-08-12, asserted directly.

        A working session must not read as an idle box. Same fabricated world as
        above, plus one fresh transcript.
        """
        if not TRACKED.is_file():
            self.skipTest("no tracked gate")
        import tempfile
        import time

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            repo, sessions = tmp / "repo", tmp / "sessions"
            repo.mkdir()
            sessions.mkdir()
            (sessions / "live.jsonl").touch()  # written just now
            marker = tmp / "marker"
            marker.touch()
            old = time.time() - 45 * 60
            os.utime(marker, (old, old))

            env = {
                **os.environ,
                "DRY_RUN": "1",
                "MARKER": str(marker),
                "REPO": str(repo),
                "SESSIONS": str(sessions),
            }
            out = subprocess.run(
                ["bash", str(TRACKED)], env=env, capture_output=True, text=True, timeout=60
            ).stdout
            self.assertNotIn(
                "shutting down",
                out,
                "a session transcript written seconds ago was treated as an idle "
                f"box -- this is the outage. Gate said:\n{out}",
            )


class TheClausesAreLiveAndDecideCorrectly(unittest.TestCase):
    """Each activity clause, PLANTED and run, with its must-not-match half.

    This class is docket D96's repair. The substring assertions above can be
    satisfied by prose; these cannot be satisfied by anything except the clause
    executing. Every case starts from the same fabricated 45-minutes-idle world
    (`idle_world`) and plants exactly ONE fact, so the thing that moved the
    verdict is never in doubt -- and each positive is paired with the L-84
    negative, because a gate that holds the box on everything has deleted the
    cost control it exists to provide.

    MUTATION-PROVED 2026-08-15, on a scratch copy, `__pycache__` purged before
    each cell:
      * delete `auto-stop.sh`'s clause-(1) block entirely (the state in which
        the old suite returned `12 passed, 1 skipped`) -> RED here;
      * mutate clause (2)'s CPU threshold to `-gt 999999999`, so no worker can
        ever hold the box -> RED here;
      * unmutated control -> green.
    """

    def setUp(self):
        if not TRACKED.is_file():
            self.fail(f"{TRACKED} is missing -- there is no gate to exercise")
        if getpass.getuser() != GATE_USER:
            self.skipTest(
                f"clause (2) filters on `pgrep -u {GATE_USER}` and this suite "
                f"is running as {getpass.getuser()!r}, so a planted worker "
                f"would be invisible to the gate for a reason that is about "
                f"this host and not about the gate")

    # -- helpers ---------------------------------------------------------

    def _plant(self, argv: list[str], cwd: str) -> subprocess.Popen:
        proc = subprocess.Popen(argv, cwd=cwd,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        self.addCleanup(self._reap, proc)
        time.sleep(0.6)          # let it appear in /proc and start burning CPU
        self.assertIsNone(proc.poll(),
                          f"the planted process {argv} exited immediately; "
                          f"nothing was being measured")
        return proc

    @staticmethod
    def _reap(proc: subprocess.Popen) -> None:
        proc.kill()
        proc.wait(timeout=30)

    @staticmethod
    def _pgrep(*args: str) -> list[str]:
        return subprocess.run(["pgrep", *args], capture_output=True,
                              text=True).stdout.split()

    def _no_real_solver_is_running(self):
        """A live solver on this box would make the negative case unrunnable."""
        live = self._pgrep("-x", PLANTED_SOLVER)
        if live:
            self.skipTest(
                f"a real process named {PLANTED_SOLVER} is running on this box "
                f"(pid {' '.join(live)}), so the must-not-match half cannot be "
                f"measured: the clause would fire for a genuine reason")

    # -- clause (1): solvers and meshers, matched on PROCESS NAME ----------

    def test_clause_1_a_running_solver_holds_the_box(self):
        """The clause that stops this box dying mid-OpenFOAM-run, executed.

        A real process whose PROCESS NAME is `simpleFoam`, in a world that is
        otherwise 45 minutes idle. If the clause is deleted -- which the old
        substring assertion permitted, because the comment above the clause
        contains the string it matched -- this goes red.
        """
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            env = idle_world(tmp)
            fake = tmp / PLANTED_SOLVER
            shutil.copy("/bin/sleep", fake)
            fake.chmod(0o755)
            proc = self._plant([str(fake), "300"], cwd="/")
            # Precondition, asserted rather than assumed: the plant really is
            # visible to a NAME match. Without this the test could pass by
            # planting nothing.
            self.assertIn(
                str(proc.pid), self._pgrep("-x", PLANTED_SOLVER),
                f"the planted process is not visible to `pgrep -x "
                f"{PLANTED_SOLVER}`, so this case is measuring nothing")
            out = run_gate(env)
        self.assertNotIn(
            "shutting down", out,
            "a solver was running and the gate powered the box off. This is "
            f"the 2026-08-12 outage. Gate said:\n{out}")
        self.assertIn(
            "solver or mesher running", out,
            "the box was held, but not by the solver clause -- so this case is "
            f"passing for the wrong reason. Gate said:\n{out}")

    def test_clause_1_a_command_line_that_MENTIONS_a_solver_does_not_hold_it(self):
        """L-84's other half, and the comment's own claim, executed.

        `auto-stop.sh:80-81` claims `pgrep -x` on the name "cannot be triggered
        by a path, a comment, or a grep that mentions the name". The
        pre-2026-08-12 gate matched command-line STRINGS and was silently
        reprieved by a `grep Certonomous/sdk` typed to investigate the bug. So:
        a process whose COMMAND LINE contains `simpleFoam` and whose NAME does
        not must leave the box free to stop.
        """
        self._no_real_solver_is_running()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            env = idle_world(tmp)
            # `sh -c <cmd> <name>` puts the name on the command line as $0.
            proc = self._plant(["/bin/sh", "-c", "sleep 300", PLANTED_SOLVER],
                               cwd="/")
            self.assertIn(
                str(proc.pid), self._pgrep("-f", PLANTED_SOLVER),
                "the decoy's command line does not mention the solver, so this "
                "case is not testing what it says it is")
            self.assertNotIn(
                str(proc.pid), self._pgrep("-x", PLANTED_SOLVER),
                "a NAME match found a process merely MENTIONING the solver -- "
                "the clause is matching strings again, which is the predicate "
                "that both missed real work and fired on a grep about itself")
            out = run_gate(env)
        self.assertIn(
            "shutting down", out,
            "a command line that merely mentions a solver pinned the box. A "
            "gate that holds on a mention is a bill, not cost control. Gate "
            f"said:\n{out}")

    # -- clause (2): a worker in the repo that is actually burning CPU -----

    def test_clause_2_a_worker_burning_cpu_in_the_repo_holds_the_box(self):
        """The clause the relative-path suite needed, executed rather than read.

        Round 7 measured that mutating this clause's CPU threshold to
        `-gt 999999999` -- so that no worker on earth could hold the box --
        left the suite at `12 passed`. This is the case that mutation reddens.
        """
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            env = idle_world(tmp)
            repo = Path(env["REPO"])
            proc = self._plant(["/usr/bin/python3", "-c", "while True: pass"],
                               cwd=str(repo))
            self.assertIn(
                str(proc.pid),
                self._pgrep("-u", GATE_USER, "-x",
                            "python|python3|python3.10|python3.11|python3.12"),
                "the planted worker is not visible to the gate's own process-"
                "name filter, so this case is measuring nothing")
            self.assertEqual(
                str(repo), os.path.realpath(f"/proc/{proc.pid}/cwd"),
                "the planted worker's CWD is not the fabricated repo")
            out = run_gate(env)
        self.assertNotIn(
            "shutting down", out,
            "a worker burning CPU with its CWD inside the repo was read as an "
            f"idle box. Gate said:\n{out}")
        self.assertIn(
            "busy in repo", out,
            "the box was held, but not by the CPU clause -- this case is "
            f"passing for the wrong reason. Gate said:\n{out}")

    def test_clause_2_a_parked_process_in_the_repo_does_NOT_hold_the_box(self):
        """L-84's other half, and the reason the CPU test is not decoration.

        `chief_engineer.server` is a permanent daemon whose CWD is inside the
        repo. Counting mere presence would pin the box forever and silently
        delete the cost control this script exists for.
        """
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            env = idle_world(tmp)
            repo = Path(env["REPO"])
            proc = self._plant(
                ["/usr/bin/python3", "-c", "import time; time.sleep(300)"],
                cwd=str(repo))
            self.assertIn(
                str(proc.pid),
                self._pgrep("-u", GATE_USER, "-x",
                            "python|python3|python3.10|python3.11|python3.12"),
                "the parked worker is invisible to the gate, so its silence "
                "here proves nothing")
            out = run_gate(env)
        self.assertIn(
            "shutting down", out,
            "a parked process with its CWD in the repo pinned the box. That is "
            "the cost control deleted -- a daemon would hold this machine "
            f"forever. Gate said:\n{out}")


if __name__ == "__main__":
    unittest.main()
