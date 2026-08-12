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
"""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TRACKED = REPO / "scripts" / "auto-stop.sh"
INSTALLED = Path("/usr/local/bin/auto-stop.sh")


def _read_installed() -> str | None:
    """Return the installed gate's text, or None if it is not present/readable."""
    try:
        return INSTALLED.read_text()
    except (FileNotFoundError, PermissionError):
        return None


class AutoStopGateTests(unittest.TestCase):
    def test_the_tracked_gate_exists_and_is_the_reviewed_one(self):
        self.assertTrue(
            TRACKED.is_file(),
            f"{TRACKED} is missing. The gate that decides whether this box stays "
            "alive must have a reviewable copy in the tree.",
        )
        text = TRACKED.read_text()
        # The three activity clauses are the whole point of the 2026-08-12
        # repair. If one is deleted, the gate regresses to the shape that
        # killed two suites, and it should regress loudly.
        self.assertIn("pgrep -x", text, "clause 1 (process NAME match) is gone")
        self.assertIn("/proc/", text, "clause 2 (CWD match) is gone")
        self.assertIn(".jsonl", text, "clause 3 (session transcript) is gone")

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
        installed = _read_installed()
        if installed is None:
            self.skipTest(
                f"no readable {INSTALLED} on this host -- nothing is powering "
                "this box off, so there is nothing to drift"
            )
        self.assertEqual(
            TRACKED.read_text(),
            installed,
            f"{INSTALLED} differs from {TRACKED}.\n"
            "This is the exact 2026-07-30 failure: a reviewed fix in the tree "
            "while the machine runs something else. Reinstall with:\n"
            f"  sudo install -m 755 {TRACKED} {INSTALLED}",
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


if __name__ == "__main__":
    unittest.main()
