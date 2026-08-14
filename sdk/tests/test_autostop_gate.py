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


if __name__ == "__main__":
    unittest.main()
